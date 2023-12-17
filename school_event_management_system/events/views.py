import base64
from io import BytesIO

import qrcode

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
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
    TeamOrParticipantForm,
    TeamParticipantsForm,
)
from events.models import Event, Participant, Solution, Team
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
    get_participant_by_id,
    get_participant_solution,
    get_participants_with_supervisor,
    get_published_events,
    get_published_not_archived_events,
    get_team_by_id,
    get_team_solution,
    get_teams_with_supervisor,
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
        teams = get_teams_with_supervisor(
            event=event,
            supervisor=request.user,
        )
        participants = get_participants_with_supervisor(
            event=event,
            supervisor=request.user,
        )
        return self.render_to_response(
            context={
                'event': event,
                'is_user_participation_of_event': is_user_participation_of_event(
                    event=event,
                    user=request.user,
                ),
                'teams': teams,
                'participants': participants,
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
        teams = get_teams_with_supervisor(
            event=event,
            supervisor=request.user,
        )
        participants = get_participants_with_supervisor(
            event=event,
            supervisor=request.user,
        )
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
                'teams': teams,
                'participants': participants,
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
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'Участник успешно зарегистрирован на мероприятии',
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
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    f'Комманда \'{team.name}\' успешно зарегистрирована на мероприятии',
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
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    f'Комманда \'{team.name}\' успешно зарегистрирована на мероприятии',
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
    teams: QuerySet[Team] = None
    participants: QuerySet[Participant] = None
    team_or_participant_form: TeamOrParticipantForm = None
    team_id: int = None
    participant_id: int = None
    team: Team = None

    def dispatch(self, request: HttpRequest, slug, *args, **kwargs):
        self.event = get_event_by_slug(slug=slug)
        if request.user.role != 'ученик':
            if self.event.type == 'Индивидуальное':
                self.participants = get_participants_with_supervisor(
                    event=self.event,
                    supervisor=request.user,
                )
            else:
                self.teams = get_teams_with_supervisor(
                    event=self.event,
                    supervisor=request.user,
                )
        if request.user.role == 'ученик':
            self.participant = get_event_participant(event=self.event, user=request.user)
        else:
            if self.event.type == 'Индивидуальное':
                self.participant = get_participant_by_id(request.GET.get('participant_id'))
                self.participant_id = request.GET.get('participant_id')
            else:
                self.team = get_team_by_id(request.GET.get('team_id'))
                self.team_id = request.GET.get('team_id')
        self.is_user_participation_of_event = is_user_participation_of_event(
            event=self.event,
            user=request.user,
        )
        if not self.is_user_participation_of_event and not self.teams and not self.participants:
            return redirect('register_on_event', slug=self.event.slug)
        if self.teams:
            self.team_or_participant_form = TeamOrParticipantForm(teams=self.teams)
        if self.participants:
            self.team_or_participant_form = TeamOrParticipantForm(
                participants=self.participants,
            )
        if self.is_user_participation_of_event:
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
        else:
            if self.team_id or self.participant_id:
                if self.event.type != 'Индивидуальное':
                    self.team_form = TeamForm(
                        event=self.event,
                        team=self.team,
                        data=request.POST or None,
                        initial={
                            'name': self.team.name,
                            'school_class': self.team.school_class,
                        },
                    )
                    self.team_participants_form = TeamParticipantsForm(
                        data=request.POST or None,
                        minimum_number_of_team_members=self.event.minimum_number_of_team_members,
                        maximum_number_of_team_members=self.event.maximum_number_of_team_members,
                        initial=create_initial_data_for_team_participants_form(self.team),
                    )
                    self.supervisor_form = SupervisorForm(
                        data=request.POST or None,
                        initial={'fio': self.team.supervisor.full_name},
                    )
                else:
                    self.supervisor_form = SupervisorForm(
                        data=request.POST or None,
                        initial={'fio': self.participant.supervisor.full_name},
                    )
        if is_user_participation_of_event:
            self.participant_form = ParticipantForm(
                data=request.POST or None,
                user=request.user,
            )
        if self.participant:
            self.participant_form = ParticipantForm(
                data=request.POST or None,
                user=self.participant.user,
            )
        return super(EditParticipantEventView, self).dispatch(request, slug, *args, **kwargs)

    def get(self, request: HttpRequest, slug, *args, **kwargs):
        return self.render_to_response(
            context={
                'event': self.event,
                'is_user_participation_of_event': self.is_user_participation_of_event,
                'supervisor_form': self.supervisor_form,
                'participant_form': self.participant_form,
                'team_form': self.team_form,
                'team_participants_form': self.team_participants_form,
                'team_or_participant_form': self.team_or_participant_form,
                'participant': self.participant,
                'teams': self.teams,
                'participants': self.participants,
                'team_id': self.team_id,
                'participant_id': self.participant_id,
            }
        )

    def post(self, request, slug, *args, **kwargs):
        if self.is_user_participation_of_event:
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
        else:
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
                            team=self.team,
                            supervisor=get_user_by_fio(
                                fio=self.supervisor_form.cleaned_data['fio'],
                            ),
                        )
                    if (
                        self.team_form.cleaned_data['name'] !=
                        self.team_form.initial.get('name')
                    ):
                        change_team_name(
                            team=self.team,
                            name=self.team_form.cleaned_data['name'],
                        )
                    disband_team_participants(team=self.team)
                    for field_name, field in self.team_participants_form.fields.items():
                        if field_name.startswith('participant_'):
                            user = get_user_by_fio(
                                fio=self.team_participants_form.cleaned_data[field_name],
                            )
                            if user:
                                join_team(
                                    user=user,
                                    team=self.team,
                                    event=self.event,
                                )
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
                            team=self.team,
                            supervisor=get_user_by_fio(
                                fio=self.supervisor_form.cleaned_data['fio'],
                            ),
                        )
                    if (
                        self.team_form.cleaned_data['school_class'] !=
                        self.team_form.initial.get('school_class')
                    ):
                        change_team_school_class(
                            team=self.team,
                            school_class=self.team_form.cleaned_data['school_class'],
                        )
                    if (
                        self.team_form.cleaned_data['name'] !=
                        self.team_form.initial.get('name')
                    ):
                        change_team_name(
                            team=self.team,
                            name=self.team_form.cleaned_data['name'],
                        )
                    disband_team_participants(team=self.team)
                    for field_name, field in self.team_participants_form.fields.items():
                        if field_name.startswith('participant_'):
                            user = get_user_by_fio(
                                fio=self.team_participants_form.cleaned_data[field_name],
                            )
                            if user:
                                join_team(
                                    user=user,
                                    team=self.team,
                                    event=self.event,
                                )

        return self.render_to_response(
            context={
                'event': self.event,
                'is_user_participation_of_event': self.is_user_participation_of_event,
                'supervisor_form': self.supervisor_form,
                'participant_form': self.participant_form,
                'team_form': self.team_form,
                'team_participants_form': self.team_participants_form,
                'team_or_participant_form': self.team_or_participant_form,
                'participant': self.participant,
                'teams': self.teams,
                'participants': self.participants,
                'team_id': self.team_id,
                'participant_id': self.participant_id,
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
    teams: QuerySet[Team] = None
    participants: QuerySet[Participant] = None
    team_or_participant_form: TeamOrParticipantForm = None
    team_id: int = None
    participant_id: int = None
    team: Team = None

    def dispatch(self, request: HttpRequest, slug, *args, **kwargs):
        self.event = get_event_by_slug(slug=slug)
        if request.user.role != 'ученик':
            if self.event.type == 'Индивидуальное':
                self.participants = get_participants_with_supervisor(
                    event=self.event,
                    supervisor=request.user,
                )
            else:
                self.teams = get_teams_with_supervisor(
                    event=self.event,
                    supervisor=request.user,
                )

        if request.user.role == 'ученик':
            self.participant = get_event_participant(event=self.event, user=request.user)
        else:
            if self.event.type == 'Индивидуальное':
                self.participant = get_participant_by_id(request.GET.get('participant_id'))
                self.participant_id = request.GET.get('participant_id')
            else:
                self.team = get_team_by_id(request.GET.get('team_id'))
                self.team_id = request.GET.get('team_id')

        self.is_user_participation_of_event = is_user_participation_of_event(
            event=self.event,
            user=request.user,
        )
        if not self.is_user_participation_of_event and not self.teams and not self.participants:
            return redirect('register_on_event', slug=self.event.slug)

        if self.event.type == 'Индивидуальное':
            self.solution = get_participant_solution(
                event=self.event,
                participant=self.participant,
            )
        else:
            if self.is_user_participation_of_event:
                self.solution = get_team_solution(
                    event=self.event,
                    team=self.participant.team,
                )
            else:
                self.solution = get_team_solution(
                    event=self.event,
                    team=self.team,
                )
        if self.teams:
            self.team_or_participant_form = TeamOrParticipantForm(teams=self.teams)
        if self.participants:
            self.team_or_participant_form = TeamOrParticipantForm(
                participants=self.participants,
            )
        self.solution_form = SolutionForm(
            data=request.POST or None,
            instance=self.solution,
        )
        return super(EventSolutionView, self).dispatch(request, slug, *args, **kwargs)

    def get(self, request: HttpRequest, slug, *args, **kwargs):
        return self.render_to_response(
            context={
                'team_or_participant_form': self.team_or_participant_form,
                'task': get_event_task(event=self.event),
                'event': self.event,
                'participant': self.participant,
                'is_user_participation_of_event': self.is_user_participation_of_event,
                'solution_form': self.solution_form,
                'teams': self.teams,
                'participants': self.participants,
                'team_id': self.team_id,
                'participant_id': self.participant_id,
            }
        )

    def post(self, request, slug, *args, **kwargs):
        if self.solution_form.is_valid():
            solution = self.solution_form.save(commit=False)
            if self.event.type == 'Индивидуальное':
                solution.participant = self.participant
            else:
                if self.is_user_participation_of_event:
                    solution.team = self.participant.team
                else:
                    solution.team = self.team
            solution.event = self.event
            solution.save()
        return self.render_to_response(
            context={
                'team_or_participant_form': self.team_or_participant_form,
                'task': get_event_task(event=self.event),
                'event': self.event,
                'participant': self.participant,
                'is_user_participation_of_event': self.is_user_participation_of_event,
                'solution_form': self.solution_form,
                'teams': self.teams,
                'participants': self.participants,
                'team_id': self.team_id,
                'participant_id': self.participant_id,
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
