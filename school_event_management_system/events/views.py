from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin

from events.forms import ParticipantForm, SupervisorForm, TeamForm, TeamParticipantsForm
from events.services import get_event_by_slug, get_published_events


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
            user=request.user,
            minimum_number_of_team_members=event.minimum_number_of_team_members,
            maximum_number_of_team_members=event.maximum_number_of_team_members,
        )
        self.team_form = TeamForm()
        self.supervisor_form = SupervisorForm()
        self.participant_form = ParticipantForm(user=request.user)
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
        pass
