from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from events.models import Event


def get_published_events() -> QuerySet[Event]:
    """Return all published `Event`'s."""
    return Event.objects.filter(published=True)


def get_event_by_slug(slug: int) -> Event:
    """Return `Event` by id."""
    return get_object_or_404(Event, slug=slug)
