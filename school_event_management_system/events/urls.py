from django.contrib.auth.decorators import login_required
from django.urls import path

from events.views import (
    DiplomasListView,
    EditParticipantEventView,
    EventArchiveView,
    EventDetailView,
    EventListView,
    EventQRCodeView,
    EventSolutionView,
    ParticipantEventsView,
    RegisterOnEventView,
    SupervisorEventsView,
)

urlpatterns = [
    path(
        route='events/',
        view=EventListView.as_view(),
        name='events_list',
    ),
    path(
        route='events/participant/',
        view=ParticipantEventsView.as_view(),
        name='participant_events',
    ),
    path(
        route='events/supervisor/',
        view=SupervisorEventsView.as_view(),
        name='supervisor_events',
    ),
    path(
        route='events/archive/',
        view=EventArchiveView.as_view(),
        name='events_archive',
    ),
    path(
        route='event/<slug:slug>/',
        view=EventDetailView.as_view(),
        name='event_detail',
    ),
    path(
        route='event/<slug:slug>/qr_code/',
        view=EventQRCodeView.as_view(),
        name='event_qr_code',
    ),
    path(
        route='event/<slug:slug>/register/',
        view=login_required(
            RegisterOnEventView.as_view(),
        ),
        name='register_on_event',
    ),
    path(
        route='event/<slug:slug>/edit/',
        view=login_required(
            EditParticipantEventView.as_view(),
        ),
        name='edit_participant_event',
    ),
    path(
        route='event/<slug:slug>/solution/',
        view=login_required(
            EventSolutionView.as_view(),
        ),
        name='event_solution',
    ),

    # diplomas
    path(
        route='diplomas/',
        view=DiplomasListView.as_view(),
        name='diplomas_list',
    ),
]
