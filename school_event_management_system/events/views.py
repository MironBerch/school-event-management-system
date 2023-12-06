from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.shortcuts import redirect
from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin

from accounts.services import get_user_by_fio
from events.forms import (
    ParticipantForm,
    SolutionForm,
    SupervisorForm,
    TeamForm,
    TeamParticipantsForm,
)
from events.models import Event, Participant, Solution
from events.services import (
    create_team,
    get_event_by_slug,
    get_event_participant,
    get_participant_solution,
    get_published_events,
    get_published_not_archived_events,
    get_team_solution,
    get_user_diplomas,
    is_user_participation_of_event,
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
                'events': get_published_not_archived_events(),
            },
        )


class EventArchiveView(
    LoginRequiredMixin,
    TemplateResponseMixin,
    View,
):
    """View list of archived events."""

    template_name = 'events/events_archive.html'

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
        event = get_event_by_slug(slug=slug)
        return self.render_to_response(
            context={
                'event': event,
                'is_user_participation_of_event': is_user_participation_of_event(
                    event=event,
                    user=request.user,
                )
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
    is_user_participation_of_event: bool = False
    event: Event = None

    def dispatch(self, request: HttpRequest, slug, *args, **kwargs):
        self.event = get_event_by_slug(slug=slug)
        self.is_user_participation_of_event = is_user_participation_of_event(
            event=self.event,
            user=request.user,
        )
        if self.is_user_participation_of_event:
            return redirect('edit_participant_event', slug=self.event.slug)
        self.team_participants_form = TeamParticipantsForm(
            data=request.POST or None,
            minimum_number_of_team_members=self.event.minimum_number_of_team_members,
            maximum_number_of_team_members=self.event.maximum_number_of_team_members,
        )
        self.team_form = TeamForm(
            event=self.event,
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
        return self.render_to_response(
            context={
                'event': self.event,
                'is_user_participation_of_event': self.is_user_participation_of_event,
                'supervisor_form': self.supervisor_form,
                'participant_form': self.participant_form,
                'team_form': self.team_form,
                'team_participants_form': self.team_participants_form,
            }
        )

    def post(self, request, slug):
        if self.event.type == 'Индивидуальное':
            if self.supervisor_form.is_valid():
                join_event(
                    user=request.user,
                    supervisor=get_user_by_fio(
                        fio=self.supervisor_form.cleaned_data['fio'],
                    ),
                    event=self.event,
                )
                return redirect('edit_participant_event', slug=self.event.slug)
        else:
            if (
                self.team_participants_form.is_valid() and
                self.team_form.is_valid() and
                self.supervisor_form.is_valid()
            ):
                team = create_team(
                    event=self.event,
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
                                event=self.event,
                                user=user,
                                team=team,
                            )
                        else:
                            pass
                return redirect('edit_participant_event', slug=self.event.slug)

        return self.render_to_response(
            context={
                'event': self.event,
                'is_user_participation_of_event': self.is_user_participation_of_event,
                'supervisor_form': self.supervisor_form,
                'participant_form': self.participant_form,
                'team_form': self.team_form,
                'team_participants_form': self.team_participants_form,
            }
        )


class EditParticipantEventView(
    LoginRequiredMixin,
    TemplateResponseMixin,
    View,
):
    """View for register on event."""

    template_name = 'events/edit_participant_event.html'
    team_form: TeamForm = None
    supervisor_form: SupervisorForm = None
    participant_form: ParticipantForm = None
    team_participants_form: TeamParticipantsForm = None
    is_user_participation_of_event: bool = False
    participant: Participant = None
    event: Event = None

    def dispatch(self, request: HttpRequest, slug, *args, **kwargs):
        self.event = get_event_by_slug(slug=slug)
        self.participant = get_event_participant(event=self.event, user=request.user)
        self.is_user_participation_of_event = is_user_participation_of_event(
            event=self.event,
            user=request.user,
        )
        if not self.is_user_participation_of_event:
            return redirect('register_on_event', slug=self.event.slug)
        self.team_participants_form = TeamParticipantsForm(
            data=request.POST or None,
            minimum_number_of_team_members=self.event.minimum_number_of_team_members,
            maximum_number_of_team_members=self.event.maximum_number_of_team_members,
        )
        if self.event.type != 'Индивидуальное':
            self.team_form = TeamForm(
                event=self.event,
                data=request.POST or None,
                initial={'name': self.participant.team.name},
            )
        self.supervisor_form = SupervisorForm(
            data=request.POST or None,
            initial={'fio': self.participant.supervisor.full_name},
        )
        self.participant_form = ParticipantForm(
            data=request.POST or None,
            user=request.user,
        )
        return super(EditParticipantEventView, self).dispatch(request, slug, *args, **kwargs)

    def get(self, request: HttpRequest, slug):
        return self.render_to_response(
            context={
                'event': self.event,
                'is_user_participation_of_event': self.is_user_participation_of_event,
                'supervisor_form': self.supervisor_form,
                'participant_form': self.participant_form,
                'team_form': self.team_form,
                'team_participants_form': self.team_participants_form,
            }
        )

    def post(self, request, slug):
        if self.event.type == 'Индивидуальное':
            if self.supervisor_form.is_valid():
                join_event(
                    user=request.user,
                    supervisor=get_user_by_fio(
                        fio=self.supervisor_form.cleaned_data['fio'],
                    ),
                    event=self.event,
                )
                return redirect('edit_participant_event', slug=self.event.slug)
        else:
            if (
                self.team_participants_form.is_valid() and
                self.team_form.is_valid() and
                self.supervisor_form.is_valid()
            ):
                team = create_team(
                    event=self.event,
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
                                event=self.event,
                                user=user,
                                team=team,
                            )
                        else:
                            pass
                return redirect('edit_participant_event', slug=self.event.slug)

        return self.render_to_response(
            context={
                'event': self.event,
                'is_user_participation_of_event': self.is_user_participation_of_event,
                'supervisor_form': self.supervisor_form,
                'participant_form': self.participant_form,
                'team_form': self.team_form,
                'team_participants_form': self.team_participants_form,
                'participant': self.participant,
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


class EventSolutionView(
    LoginRequiredMixin,
    TemplateResponseMixin,
    View,
):
    """View for edit team or participant event solution."""

    template_name = 'events/event_solution.html'
    solution_form: SolutionForm = None
    is_user_participation_of_event: bool = False
    participant: Participant = None
    solution: Solution = None
    event: Event = None

    def dispatch(self, request: HttpRequest, slug, *args, **kwargs):
        self.event = get_event_by_slug(slug=slug)
        self.participant = get_event_participant(event=self.event, user=request.user)
        self.is_user_participation_of_event = is_user_participation_of_event(
            event=self.event,
            user=request.user,
        )
        if not self.is_user_participation_of_event:
            return redirect('register_on_event', slug=self.event.slug)
        if self.event.type == 'Индивидуальное':
            self.solution = get_participant_solution(
                event=self.event,
                participant=self.participant,
            )
        else:
            self.solution = get_team_solution(
                event=self.event,
                team=self.participant.team,
            )
        self.solution_form = SolutionForm(
            data=request.POST or None,
            instance=self.solution,
        )
        return super(EventSolutionView, self).dispatch(request, slug, *args, **kwargs)

    def get(self, request: HttpRequest, slug):
        return self.render_to_response(
            context={
                'event': self.event,
                'participant': self.participant,
                'is_user_participation_of_event': self.is_user_participation_of_event,
                'solution_form': self.solution_form,
            }
        )

    def post(self, request, slug):
        if self.solution_form.is_valid():
            solution = self.solution_form.save(commit=False)
            if self.event.type == 'Индивидуальное':
                solution.participant = self.participant
            else:
                solution.team = self.participant.team
            solution.event = self.event
            solution.save()
        return self.render_to_response(
            context={
                'event': self.event,
                'participant': self.participant,
                'is_user_participation_of_event': self.is_user_participation_of_event,
                'solution_form': self.solution_form,
            }
        )
