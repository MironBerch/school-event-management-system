from django.contrib import admin

from events.models import Event, Participant, Team


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('name', ),
    }
    list_display = (
        'name',
        'slug',
        'status',
        'type',
        'date_of_starting_event',
        'published',
    )
    search_fields = (
        'name',
        'slug',
    )
    list_filter = (
        'status',
        'type',
        'published',
    )
    ordering = (
        'status',
        'type',
        'published',
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
        'supervisor',
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
    list_filter = (
        'event',
        'supervisor',
    )
