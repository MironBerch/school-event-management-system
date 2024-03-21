from django.db.models.signals import post_save
from django.dispatch import receiver

from events.models import EventDiplomas


@receiver(post_save, sender=EventDiplomas)
def notify_about_diplomas_appearance(sender, instance: EventDiplomas, created, **kwargs):
    if created:
        pass
