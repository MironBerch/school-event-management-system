from ckeditor.fields import RichTextFormField

from django import forms

from events.models import Event


class MailingForm(forms.Form):
    content = RichTextFormField(
        label='содержание письма',
    )


class RecipientsForm(forms.Form):
    event = forms.ModelChoiceField(
        queryset=Event.objects.all(),
        label='мероприятие',
    )
