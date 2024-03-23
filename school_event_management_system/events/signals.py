from os import environ

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from events.models import EventDiplomas
from events.services import (
    get_emails_of_event_participants_and_supervisors,
    get_event_diplomas_url,
    notify_about_diplomas_appearance,
)


@receiver(post_save, sender=EventDiplomas)
def notify_about_diplomas_appearance_receiver(sender, instance: EventDiplomas, created, **kwargs):
    if created:
        notify_about_diplomas_appearance(
            domain=environ.get('DOMAIN'),
            from_email=settings.DEFAULT_FROM_EMAIL,
            event=instance.event.name,
            diplomas_url=get_event_diplomas_url(event=instance.event),
            emails=get_emails_of_event_participants_and_supervisors(
                event=instance.event,
            ),
        )
