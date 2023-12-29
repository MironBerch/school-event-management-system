from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin

from mailings.forms import MailingForm


class MailingCreateView(
    TemplateResponseMixin,
    View,
):
    template_name = 'mailings/mailing_create.html'
    mailing_form: MailingForm = None

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('signin'))
        if not (request.user.is_superuser or request.user.is_staff):
            return redirect(reverse('settings_dashboard'))
        self.mailing_form = MailingForm(
            data=request.POST or None,
        )
        return super(MailingCreateView, self).dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest):
        return self.render_to_response(
            context={
                'mailing_form': self.mailing_form,
            }
        )
