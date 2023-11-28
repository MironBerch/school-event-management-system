from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.shortcuts import redirect
from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin

from accounts.services import get_user_by_fio
from events.forms import ParticipantForm, SupervisorForm, TeamForm, TeamParticipantsForm
from events.services import (
    create_team,
    get_event_by_slug,
    get_published_events,
    get_user_diplomas,
    join_event,
    join_team,
)


class EventListView(
    LoginRequiredMixin,
    TemplateResponseMixin,
    View,
):
    """View list of events."""

    template_name = 'events/events_list.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        return self.render_to_response(
            context={
                'events': get_published_events(),
            },
        )


class EventDetailView(
    LoginRequiredMixin,
    TemplateResponseMixin,
    View,
):
    """Detail event view."""

    template_name = 'events/event_detail.html'

    def get(self, request, slug):
        return self.render_to_response(
            context={
                'event': get_event_by_slug(slug=slug),
            },
        )


class RegisterOnEventView(
    LoginRequiredMixin,
    TemplateResponseMixin,
    View,
):
    """View for register on event."""

    template_name = 'events/register_on_event.html'
    team_form: TeamForm = None
    supervisor_form: SupervisorForm = None
    participant_form: ParticipantForm = None
    team_participants_form: TeamParticipantsForm = None

    def dispatch(self, request: HttpRequest, slug, *args, **kwargs):
        event = get_event_by_slug(slug=slug)
        self.team_participants_form = TeamParticipantsForm(
            data=request.POST or None,
            user=request.user,
            minimum_number_of_team_members=event.minimum_number_of_team_members,
            maximum_number_of_team_members=event.maximum_number_of_team_members,
        )
        self.team_form = TeamForm(
            data=request.POST or None,
        )
        self.supervisor_form = SupervisorForm(
            data=request.POST or None,
        )
        self.participant_form = ParticipantForm(
            data=request.POST or None,
            user=request.user,
        )
        return super(RegisterOnEventView, self).dispatch(request, slug, *args, **kwargs)

    def get(self, request: HttpRequest, slug):
        event = get_event_by_slug(slug=slug)
        return self.render_to_response(
            context={
                'event': event,
                'supervisor_form': self.supervisor_form,
                'participant_form': self.participant_form,
                'team_form': self.team_form,
                'team_participants_form': self.team_participants_form,
            }
        )

    def post(self, request, slug):
        event = get_event_by_slug(slug=slug)
        if event.type == 'Индивидуальное':
            if self.supervisor_form.is_valid():
                join_event(
                    user=request.user,
                    supervisor=get_user_by_fio(
                        fio=self.supervisor_form.cleaned_data['fio'],
                    ),
                    event=event,
                )
                return redirect('/')
        else:
            if (
                self.team_participants_form.is_valid() and
                self.team_form.is_valid() and
                self.supervisor_form.is_valid()
            ):
                team = create_team(
                    event=event,
                    name=self.team_form.cleaned_data['name'],
                    supervisor=get_user_by_fio(
                        fio=self.supervisor_form.cleaned_data['fio'],
                    ),
                )
                for field_name, field in self.team_participants_form.fields.items():
                    if field_name.startswith('participant_'):
                        user = get_user_by_fio(
                            fio=self.team_participants_form.cleaned_data[field_name],
                        )
                        if user:
                            join_team(
                                event=event,
                                user=user,
                                team=team,
                            )
                        else:
                            pass
                return redirect('/')

        return self.render_to_response(
            context={
                'event': event,
                'supervisor_form': self.supervisor_form,
                'participant_form': self.participant_form,
                'team_form': self.team_form,
                'team_participants_form': self.team_participants_form,
            }
        )


class DiplomasListView(
    LoginRequiredMixin,
    TemplateResponseMixin,
    View,
):
    """List view of diplomas that the user received for participating in events."""

    template_name = 'diplomas/diploma_list.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        return self.render_to_response(
            context={
                'diplomas': get_user_diplomas(user=request.user),
            },
        )
