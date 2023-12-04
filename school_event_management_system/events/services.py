from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from accounts.models import User
from events.models import Event, EventDiplomas, Participant, Team


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
) -> Team:
    return Team.objects.create(
        name=name,
        event=event,
        supervisor=supervisor,
    )


def join_team(
        user: User,
        team: Team,
        event: Event,
) -> None:
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
