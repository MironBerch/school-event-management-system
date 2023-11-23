from django.contrib import admin

from events.models import Event, Participant, Supervisor, Team


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
    )
    search_fields = (
        'event__name',
        'user',
        'team__name',
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
    )
    search_fields = (
        'event__name',
        'name',
    )
    list_filter = ('event', )


@admin.register(Supervisor)
class SupervisorAdmin(admin.ModelAdmin):
    list_display = (
        'get_event',
        'team',
        'full_name',
        'email',
        'user',
    )
    search_fields = (
        'team',
        'full_name',
        'email',
        'user',
    )
    list_filter = (
        'user',
        'full_name',
    )

    def get_event(self, obj):
        return obj.team.event.name

    def get_queryset(self, request):
        queryset = super().get_queryset(request).select_related('team__event')
        return queryset
