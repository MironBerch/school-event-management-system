from django.contrib import admin
from django.db.models import QuerySet

from events.models import Event, EventDiplomas, Participant, Solution, Team


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('name', ),
    }
    list_display = (
        'name',
        'status',
        'type',
        'date_of_starting_event',
        'published',
        'archived',
    )
    search_fields = (
        'name',
        'slug',
    )
    list_filter = (
        'status',
        'type',
        'published',
        'archived',
    )
    ordering = (
        'status',
        'type',
        'published',
    )
    actions = (
        'set_published',
        'set_archived',
    )

    fieldsets = (
        (
            None,
            {
                'fields': (
                    'name',
                    'slug',
                    'image',
                    'description',
                    'regulations',
                    'results',
                    'type',
                    'status',
                    'stage',
                ),
            },
        ),
        (
            'Количество участников в команде', {
                'fields': (
                    'maximum_number_of_team_members',
                    'minimum_number_of_team_members',
                ),
            },
        ),
        (
            'Настройки видимости конкурса', {
                'fields': (
                    'published',
                    'archived',
                ),
            },
        ),
        (
            'Даты',
            {
                'fields': (
                    'date_of_starting_registration',
                    'date_of_ending_registration',
                    'date_of_starting_event',
                ),
            },
        ),
    )

    @admin.action(description='Опубликовать мероприятия')
    def set_published(self, request, queryset: QuerySet):
        count = queryset.count()
        queryset.update(published=True)
        events_word = 'мероприятия'
        if count == 1:
            events_word = 'мероприятие'
        self.message_user(
            request,
            f'Опубликовано {count} {events_word}',
        )

    @admin.action(description='Отправить мероприятия в архив')
    def set_archived(self, request, queryset: QuerySet):
        count = queryset.count()
        queryset.update(archived=True)
        events_word = 'мероприятия'
        if count == 1:
            events_word = 'мероприятие'
        self.message_user(
            request,
            f'В архив отправлено {count} {events_word}',
        )


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = (
        'event',
        'user',
        'team',
        'supervisor',
    )
    search_fields = (
        'event__name',
        'user',
        'team__name',
        'supervisor',
    )
    list_filter = (
        'event',
        'team',
    )


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = (
        'event',
        'name',
        'supervisor',
    )
    search_fields = (
        'event__name',
        'name',
    )
    list_filter = ('event', )


@admin.register(EventDiplomas)
class EventDiplomasAdmin(admin.ModelAdmin):
    list_display = (
        'event',
        'url',
    )
    search_fields = ('event__name', )


@admin.register(Solution)
class SolutionAdmin(admin.ModelAdmin):
    list_display = (
        'event',
        'participant',
        'team',
        'url',
    )
    search_fields = (
        'event__name',
        'participant',
        'team',
    )
    list_filter = ('event', )
