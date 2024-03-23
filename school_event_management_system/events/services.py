from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404
from django.template.loader import get_template, render_to_string

from accounts.models import User
from events.models import Event, EventDiplomas, Participant, Solution, Task, Team
from events.tasks import send_notify_about_diplomas_appearance_email
from mailings.services import send_email_with_attachments


def get_published_events() -> QuerySet[Event]:
    """Вернуть все опубликованные `Event`."""
    return Event.objects.filter(published=True)


def get_published_not_archived_events() -> QuerySet[Event]:
    """Вернуть все опубликованные не заархивированные `Event`."""
    return Event.objects.filter(
        published=True,
        archived=False,
    )


def get_event_by_slug(slug: int) -> Event:
    """Вернуть `Event` по `slug`."""
    return get_object_or_404(Event, slug=slug)


def create_team(
        supervisor: User | None,
        supervisor_fio: str | None,
        supervisor_email: str | None,
        supervisor_phone_number: str | None,
        name: str,
        event: Event,
        school_class: str = '',
) -> Team:
    if supervisor:
        return Team.objects.create(
            name=name,
            event=event,
            supervisor=supervisor,
            school_class=school_class,
            supervisor_fio=supervisor.full_name,
            supervisor_email=supervisor.email,
            supervisor_phone_number=supervisor.profile.phone_number,
        )
    else:
        return Team.objects.create(
            name=name,
            event=event,
            supervisor_fio=supervisor_fio,
            supervisor_email=supervisor_email,
            supervisor_phone_number=supervisor_phone_number,
            school_class=school_class,
        )


def join_team(
        user: User,
        team: Team,
        event: Event,
        fio: str,
) -> Participant:
    if not user and not fio:
        return None
    return Participant.objects.create(
        team=team,
        fio=fio,
        event=event,
        user=user,
    )


def join_event(
        supervisor_fio: str | None,
        supervisor_email: str | None,
        supervisor_phone_number: str | None,
        supervisor: User | None,
        user: User,
        event: Event,
) -> Participant:
    if supervisor:
        return Participant.objects.create(
            event=event,
            user=user,
            fio=user.full_name,
            supervisor=supervisor,
            supervisor_fio=supervisor.full_name,
            supervisor_email=supervisor.email,
            supervisor_phone_number=supervisor.profile.phone_number,
        )
    else:
        return Participant.objects.create(
            event=event,
            user=user,
            fio=user.full_name,
            supervisor=None,
            supervisor_fio=supervisor_fio,
            supervisor_email=supervisor_email,
            supervisor_phone_number=supervisor_phone_number,
        )


def get_user_diplomas(user: User) -> QuerySet[EventDiplomas]:
    return EventDiplomas.objects.filter(
        Q(
            event_id__in=Participant.objects.filter(
                user=user,
            ).values_list('event_id', flat=True),
        ) |
        Q(
            event_id__in=Team.objects.filter(
                supervisor=user,
            ).values_list('event_id', flat=True),
        ) |
        Q(
            event_id__in=Participant.objects.filter(
                supervisor=user,
            ).values_list('event_id', flat=True),
        ),
    )


def team_with_name_exist_in_event(
        team_name: str,
        event: Event,
) -> bool:
    return Team.objects.filter(
        event=event,
        name=team_name,
    ).exists()


def is_user_participation_of_event(
        event: Event,
        user: User,
) -> bool:
    return Participant.objects.filter(
        user=user,
        event=event,
    ).exists()


def get_event_participant(
        event: Event,
        user: User,
) -> Participant:
    try:
        return Participant.objects.get(
            event=event,
            user=user,
        )
    except Participant.DoesNotExist:
        return None


def get_team_solution(
        event: Event,
        team: Team,
) -> Solution:
    try:
        return Solution.objects.get(
            event=event,
            team=team,
        )
    except Solution.DoesNotExist:
        return None


def get_participant_solution(
        event: Event,
        participant: Participant,
) -> Solution:
    try:
        return Solution.objects.get(
            event=event,
            participant=participant,
        )
    except Solution.DoesNotExist:
        return None


def change_participant_supervisor(
        supervisor_fio: str | None,
        supervisor_email: str | None,
        supervisor_phone_number: str | None,
        supervisor: User | None,
        participant: Participant,
) -> Participant:
    if supervisor:
        participant.supervisor = supervisor
        participant.supervisor_fio = supervisor.full_name
        participant.supervisor_email = supervisor.email
        participant.supervisor_phone_number = supervisor.profile.phone_number
    else:
        participant.supervisor = None
        participant.supervisor_fio = supervisor_fio
        participant.supervisor_email = supervisor_email
        participant.supervisor_phone_number = supervisor_phone_number
    participant.save()
    return participant


def change_team_supervisor(
        supervisor_fio: str | None,
        supervisor_email: str | None,
        supervisor_phone_number: str | None,
        supervisor: User | None,
        team: Team,
) -> Team:
    if supervisor:
        team.supervisor = supervisor
        team.supervisor_fio = supervisor.full_name
        team.supervisor_email = supervisor.email
        team.supervisor_phone_number = supervisor.profile.phone_number
    else:
        team.supervisor = None
        team.supervisor_fio = supervisor_fio
        team.supervisor_email = supervisor_email
        team.supervisor_phone_number = supervisor_phone_number
    team.save()
    return team


def create_initial_data_for_team_participants_form(
        team: Team,
) -> dict[str, str]:
    participants = team.participants.all()
    initial_data = {}
    for i, participant in enumerate(participants, start=1):
        participant_key = f'participant_{i}'
        participant_value = f'{participant.fio}'
        initial_data[participant_key] = participant_value
    return initial_data


def change_team_name(
        team: Team,
        name: str,
) -> Team:
    team.name = name
    team.save()
    return team


def get_or_join_team(
        user: User,
        team: Team,
        event: Event,
) -> Participant:
    participant, _ = Participant.objects.get_or_create(
        team=team,
        event=event,
        user=user,
    )
    return participant


def change_team_school_class(
        team: Team,
        school_class: str,
) -> Team:
    team.school_class = school_class
    team.save()
    return team


def disband_team_participants(team: Team) -> None:
    for participant in team.participants.all():
        participant.delete()


def get_events_where_user_are_participant(
        user: User,
) -> QuerySet[Event]:
    return Event.objects.filter(
        participants__user=user,
    )


def get_events_where_user_are_supervisor(user: User) -> QuerySet[Event]:
    return Event.objects.filter(
        Q(participants__supervisor=user) | Q(teams__supervisor=user),
    ).distinct()


def get_event_task(event: Event) -> Task:
    try:
        return Task.objects.get(event=event)
    except Task.DoesNotExist:
        return None


def get_teams_with_supervisor(
        event: Event,
        supervisor: User,
) -> QuerySet[Team]:
    teams = Team.objects.filter(
        event=event,
        supervisor=supervisor,
    )
    return teams


def get_participants_with_supervisor(
        event: Event,
        supervisor: User,
) -> QuerySet[Participant]:
    participants = Participant.objects.filter(
        event=event,
        supervisor=supervisor,
    )
    return participants


def get_team_by_id(id: int) -> Team:
    try:
        return Team.objects.get(id=id)
    except Team.DoesNotExist:
        return None


def get_participant_by_id(id: int) -> Participant:
    try:
        return Participant.objects.get(id=id)
    except Participant.DoesNotExist:
        return None


def get_event_participants(event):
    return Participant.objects.filter(event=event)


def get_event_teams(event):
    return Team.objects.filter(event=event)


def get_team_participants_fio_string(team):
    participants = team.participants.all()
    participant_names = [f'{participant.fio}' for participant in participants]
    participants_string = ', '.join(participant_names)
    return participants_string


def get_team_participants_email_string(team):
    participants = team.participants.all()
    if not team.event.need_account:
        return ''
    participant_names = [f'{participant.user.email}' for participant in participants]
    participants_string = ' '.join(participant_names)
    return participants_string


def get_team_participants_phone_number_string(team):
    participants = team.participants.all()
    if not team.event.need_account:
        return ''
    participant_names = [f'{participant.user.profile.phone_number}' for participant in participants]
    participants_string = ' '.join(participant_names)
    return participants_string


def get_team_participants(team):
    return team.participants.all()


def get_all_participants_with_supervisor(
        supervisor: User,
) -> QuerySet[Participant]:
    participants = Participant.objects.filter(
        supervisor=supervisor,
    )
    return participants


def get_all_teams_with_supervisor(
        supervisor: User,
) -> QuerySet[Team]:
    teams = Team.objects.filter(
        supervisor=supervisor,
    )
    return teams


def get_emails_of_event_participants_and_supervisors(event: Event) -> list[str]:
    emails: set = set()
    participants = Participant.objects.filter(event=event)
    for participant in participants:
        if participant.user:
            emails.add(participant.user.email)
        emails.add(participant.supervisor_email)
    return list(emails)


def get_event_diplomas_url(event: Event) -> str | None:
    try:
        diplomas = EventDiplomas.objects.get(event=event)
        return diplomas.url
    except Exception:
        return None


def _send_diplomas_notification_email(
        *,
        domain: str,
        from_email: str,
        to_email: str,
        diplomas_url: str,
        event: str,
) -> None:
    """
    Функция для отправки электронного письма с уведомлением о появлении диплома.
    """
    subject = 'Появились дипломы за участие в мероприятии'
    text_content = render_to_string(
        template_name='diplomas/notify_about_diplomas_appearance_email.html',
        context={
            'diplomas_url': diplomas_url,
            'event': event,
            'domain': domain,
        },
    )
    html = get_template(template_name='diplomas/notify_about_diplomas_appearance_email.html')
    html_content = html.render(
        context={
            'diplomas_url': diplomas_url,
            'event': event,
            'domain': domain,
        },
    )
    send_email_with_attachments(
        subject=subject,
        body=text_content,
        email_to=[to_email],
        email_from=from_email,
        alternatives=[(html_content, 'text/html')],
    )


def notify_about_diplomas_appearance(
        from_email: str,
        domain: str,
        event: str,
        diplomas_url: str,
        emails: list[str],
) -> None:
    for email in emails:
        send_notify_about_diplomas_appearance_email.delay(
            domain=domain,
            from_email=from_email,
            to_email=email,
            diplomas_url=diplomas_url,
            event=event,
        )
