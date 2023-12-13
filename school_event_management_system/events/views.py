import base64
from io import BytesIO

import qrcode

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
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
    change_participant_supervisor,
    change_team_name,
    change_team_school_class,
    change_team_supervisor,
    create_initial_data_for_team_participants_form,
    create_team,
    disband_team_participants,
    get_event_by_slug,
    get_event_participant,
    get_event_task,
    get_events_where_user_are_participant,
    get_events_where_user_are_supervisor,
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
                ),
            },
        )


class EventQRCodeView(
    LoginRequiredMixin,
    TemplateResponseMixin,
    View,
):
    """Detail event QR code view."""

    template_name = 'events/event_qr_code.html'

    def get(self, request, slug):
        event = get_event_by_slug(slug=slug)
        qr = qrcode.QRCode(
            version=2,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=31,
            border=1,
        )
        qr.add_data(reverse('event_detail', kwargs={'slug': event.slug}))
        qr.make(fit=True)
        qr_code = qr.make_image(fill_color='black', back_color='white')
        buffered = BytesIO()
        qr_code.save(buffered, format='PNG')
        qr_code = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return self.render_to_response(
            context={
                'event': event,
                'is_user_participation_of_event': is_user_participation_of_event(
                    event=event,
                    user=request.user,
                ),
                'qr_code': qr_code,
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
        if self.event.type == 'Командное от классов':
            self.team_form = TeamForm(
                event=self.event,
                event_for_classes=True,
                data=request.POST or None,
            )
        else:
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
        elif self.event.type == 'Командное':
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
                    school_class=self.team_form.cleaned_data['school_class'],
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
        if self.event.type != 'Индивидуальное':
            self.team_form = TeamForm(
                event=self.event,
                team=self.participant.team,
                data=request.POST or None,
                initial={
                    'name': self.participant.team.name,
                    'school_class': self.participant.team.school_class,
                },
            )
            self.team_participants_form = TeamParticipantsForm(
                data=request.POST or None,
                minimum_number_of_team_members=self.event.minimum_number_of_team_members,
                maximum_number_of_team_members=self.event.maximum_number_of_team_members,
                initial=create_initial_data_for_team_participants_form(self.participant.team),
            )
            self.supervisor_form = SupervisorForm(
                data=request.POST or None,
                initial={'fio': self.participant.team.supervisor.full_name},
            )
        else:
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
                if (
                    self.supervisor_form.cleaned_data['fio'] !=
                    self.supervisor_form.initial.get('fio')
                ):
                    change_participant_supervisor(
                        participant=self.participant,
                        supervisor=get_user_by_fio(
                            fio=self.supervisor_form.cleaned_data['fio'],
                        ),
                    )
                return redirect('edit_participant_event', slug=self.event.slug)
        elif self.event.type == 'Командное':
            if (
                self.team_participants_form.is_valid() and
                self.team_form.is_valid() and
                self.supervisor_form.is_valid()
            ):
                if (
                    self.supervisor_form.cleaned_data['fio'] !=
                    self.supervisor_form.initial.get('fio')
                ):
                    change_team_supervisor(
                        team=self.participant.team,
                        supervisor=get_user_by_fio(
                            fio=self.supervisor_form.cleaned_data['fio'],
                        ),
                    )
                if (
                    self.team_form.cleaned_data['name'] !=
                    self.team_form.initial.get('name')
                ):
                    change_team_name(
                        team=self.participant.team,
                        name=self.team_form.cleaned_data['name'],
                    )
                disband_team_participants(team=self.participant.team)
                for field_name, field in self.team_participants_form.fields.items():
                    if field_name.startswith('participant_'):
                        user = get_user_by_fio(
                            fio=self.team_participants_form.cleaned_data[field_name],
                        )
                        if user:
                            join_team(
                                user=user,
                                team=self.participant.team,
                                event=self.event,
                            )
                return redirect('edit_participant_event', slug=self.event.slug)
        else:
            if (
                self.team_participants_form.is_valid() and
                self.team_form.is_valid() and
                self.supervisor_form.is_valid()
            ):
                if (
                    self.supervisor_form.cleaned_data['fio'] !=
                    self.supervisor_form.initial.get('fio')
                ):
                    change_team_supervisor(
                        team=self.participant.team,
                        supervisor=get_user_by_fio(
                            fio=self.supervisor_form.cleaned_data['fio'],
                        ),
                    )
                if (
                    self.team_form.cleaned_data['school_class'] !=
                    self.team_form.initial.get('school_class')
                ):
                    change_team_school_class(
                        team=self.participant.team,
                        school_class=self.team_form.cleaned_data['school_class'],
                    )
                if (
                    self.team_form.cleaned_data['name'] !=
                    self.team_form.initial.get('name')
                ):
                    change_team_name(
                        team=self.participant.team,
                        name=self.team_form.cleaned_data['name'],
                    )
                disband_team_participants(team=self.participant.team)
                for field_name, field in self.team_participants_form.fields.items():
                    if field_name.startswith('participant_'):
                        user = get_user_by_fio(
                            fio=self.team_participants_form.cleaned_data[field_name],
                        )
                        if user:
                            join_team(
                                user=user,
                                team=self.participant.team,
                                event=self.event,
                            )
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
                'task': get_event_task(event=self.event),
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
                'task': get_event_task(event=self.event),
                'event': self.event,
                'participant': self.participant,
                'is_user_participation_of_event': self.is_user_participation_of_event,
                'solution_form': self.solution_form,
            }
        )


class ParticipantEventsView(
    LoginRequiredMixin,
    TemplateResponseMixin,
    View,
):
    """View for display all events where user are participant."""

    template_name = 'events/participant_events.html'

    def get(self, request: HttpRequest):
        return self.render_to_response(
            context={
                'events': get_events_where_user_are_participant(user=request.user),
            }
        )


class SupervisorEventsView(
    LoginRequiredMixin,
    TemplateResponseMixin,
    View,
):
    """View for display all events where user are supervisor."""

    template_name = 'events/supervisor_events.html'

    def get(self, request: HttpRequest):
        return self.render_to_response(
            context={
                'events': get_events_where_user_are_supervisor(user=request.user),
            }
        )
