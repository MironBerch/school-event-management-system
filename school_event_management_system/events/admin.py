from django.contrib import admin
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.safestring import mark_safe

from events.models import Event, EventDiplomas, Participant, Solution, Task, Team


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
        'get_event_participants_link',
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
    readonly_fields = ('get_event_participants_link', )

    fieldsets = (
        (
            None,
            {
                'fields': (
                    'name',
                    'slug',
                    'image',
                    'description',
                    'need_presentation',
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
            'Настройки регистрации конкурса', {
                'fields': (
                    'need_account',
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
        (
            'Списки участников',
            {
                'fields': (
                    'get_event_participants_link',
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

    def get_event_participants_link(self, obj: Event):
        if obj.slug:
            return mark_safe(
                f"""<a href="{
                    reverse('export_event_participants', args=(obj.slug, ))
                }">Скачать списки участников</a>""",
            )
        return ""
    get_event_participants_link.short_description = 'Ссылка на скачивание списков участников'


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = (
        'event',
        'fio',
        'team',
        'supervisor_fio',
    )
    search_fields = (
        'event__name',
        'fio',
        'team__name',
        'supervisor_fio',
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
        'school_class',
        'supervisor_fio',
    )
    search_fields = (
        'event__name',
        'school_class',
        'name',
        'supervisor_fio',
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
        'topic',
        'url',
    )
    search_fields = (
        'event__name',
        'participant__fio',
        'team__name',
        'topic',
    )
    list_filter = ('event', )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('event', )
    search_fields = ('event__name', )
