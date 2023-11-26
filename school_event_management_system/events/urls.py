from django.urls import path

from events.views import EventDetailView, EventListView, RegisterOnEventView

urlpatterns = [
    path(
        route='events/',
        view=EventListView.as_view(),
        name='events_list',
    ),
    path(
        route='event/<slug:slug>/',
        view=EventDetailView.as_view(),
        name='event_detail',
    ),
    path(
        route='event/<slug:slug>/register/',
        view=RegisterOnEventView.as_view(),
        name='register_on_event',
    ),
]
