from django.apps import AppConfig


class EventsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'events'
    verbose_name = 'Мероприятия'

    def ready(self):
        from events import signals  # noqa: F401, F403
