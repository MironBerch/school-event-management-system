from ckeditor.fields import RichTextFormField

from django import forms


class MailingForm(forms.Form):
    content = RichTextFormField()
