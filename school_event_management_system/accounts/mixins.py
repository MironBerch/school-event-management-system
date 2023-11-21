from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse


class AnonymousUserRequiredMixin:
    """Verify that current user is not logged in."""

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('signout'))
        return super(AnonymousUserRequiredMixin, self).dispatch(request, *args, **kwargs)


class UnconfirmedEmailRequiredMixin:
    """Verify that current user has not confirmed an email address yet."""

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('signin'))

        if request.user.is_email_confirmed:
            return redirect(reverse('settings_dashboard'))

        return super(UnconfirmedEmailRequiredMixin, self).dispatch(request, *args, **kwargs)
