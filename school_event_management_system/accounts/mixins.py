from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse


class AnonymousUserRequiredMixin:
    """Убедитесь, что текущий пользователь не вошел в систему."""

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('signout'))
        return super(AnonymousUserRequiredMixin, self).dispatch(request, *args, **kwargs)


class UnconfirmedEmailRequiredMixin:
    """Убедитесь, что текущий пользователь еще не подтвердил адрес электронной почты."""

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('signin'))

        if request.user.is_email_confirmed:
            return redirect(reverse('settings_dashboard'))

        return super(UnconfirmedEmailRequiredMixin, self).dispatch(request, *args, **kwargs)


class SuperOrStaffUserRequiredMixin:
    """Убедитесь, что текущий пользователь явлиется `is_superuser` или `is_staff`."""

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('signin'))

        if not (request.user.is_superuser or request.user.is_staff):
            return redirect(reverse('settings_dashboard'))

        return super(SuperOrStaffUserRequiredMixin, self).dispatch(request, *args, **kwargs)
