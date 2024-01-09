from bootstrap_datepicker_plus.widgets import DateTimePickerInput

from django import forms

from events.models import Event
from mailings.models import Mailing


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = (
            'header',
            'content',
            'dispatch_time',
        )
        widgets = {
            'dispatch_time': DateTimePickerInput(
                options={
                    'format': 'DD-MM-YYYY HH:mm',
                },
            ),
        }


class RecipientsForm(forms.Form):
    event = forms.ModelChoiceField(
        queryset=Event.objects.all(),
        label='Мероприятие',
    )
    to_participants = forms.BooleanField(
        required=False,
        label='Отправить участникам',
    )
    to_supervisors = forms.BooleanField(
        required=False,
        label='Отправить руководителям',
    )
