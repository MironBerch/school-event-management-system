from django.urls import path

from mailings.views import MailingCreateView

urlpatterns = [
    path(
        route='mailings/create/',
        view=MailingCreateView.as_view(),
        name='mailing_create',
    ),
]
