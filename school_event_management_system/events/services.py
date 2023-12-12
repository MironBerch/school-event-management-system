from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from accounts.models import User
from events.models import Event, EventDiplomas, Participant, Solution, Team


def get_published_events() -> QuerySet[Event]:
    """Return all published `Event`'s."""
    return Event.objects.filter(published=True)


def get_published_not_archived_events() -> QuerySet[Event]:
    """Return all published not archived `Event`'s."""
    return Event.objects.filter(
        published=True,
        archived=False,
    )


def get_event_by_slug(slug: int) -> Event:
    """Return `Event` by id."""
    return get_object_or_404(Event, slug=slug)


def create_team(
        name: str,
        event: Event,
        supervisor: User,
        school_class: str = '',
) -> Team:
    return Team.objects.create(
        name=name,
        event=event,
        supervisor=supervisor,
        school_class=school_class,
    )


def join_team(
        user: User,
        team: Team,
        event: Event,
) -> Participant:
    return Participant.objects.create(
        team=team,
        event=event,
        user=user,
    )


def join_event(
        user: User,
        supervisor: User,
        event: Event,
) -> Participant:
    return Participant.objects.create(
        event=event,
        user=user,
        supervisor=supervisor,
    )


def get_user_diplomas(user: User) -> QuerySet[EventDiplomas]:
    return EventDiplomas.objects.filter(
        event_id__in=Participant.objects.filter(
            user=user,
        ).values_list('event_id', flat=True)
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
        event: Event, user: User
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
        participant: Participant,
        supervisor: User,
) -> Participant:
    participant.supervisor = supervisor
    participant.save()
    return participant


def change_team_supervisor(
        team: Team,
        supervisor: User,
) -> Team:
    team.supervisor = supervisor
    team.save()
    return team


def create_initial_data_for_team_participants_form(
        team: Team,
) -> dict[str, str]:
    participants = team.participants.all()
    initial_data = {}
    for i, participant in enumerate(participants, start=1):
        participant_key = f'participant_{i}'
        participant_value = f'{participant.user.full_name}'
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
        participants__user=user
    )


def get_events_where_user_are_supervisor(
        user: User,
) -> QuerySet[Event]:
    return Event.objects.filter(
        participants__supervisor=user
    )
