from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from accounts.models import User
from events.models import Event, Participant, Team


def get_published_events() -> QuerySet[Event]:
    """Return all published `Event`'s."""
    return Event.objects.filter(published=True)


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
