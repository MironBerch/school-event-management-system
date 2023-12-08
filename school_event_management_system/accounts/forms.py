from os import environ

from bootstrap_datepicker_plus.widgets import DatePickerInput

from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserChangeForm,
    UserCreationForm,
)
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts.models import Profile, User
from accounts.tasks import send_password_reset_code


class SignUpForm(UserCreationForm):
    """Form for signing up/creating new account."""

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'name@example.com',
                'autocomplete': 'username',
            },
        ),
    )

    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Имя',
                'autocomplete': 'off',
            },
        ),
    )

    surname = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Фамилия',
                'autocomplete': 'off',
            },
        ),
    )

    patronymic = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Отчество',
                'autocomplete': 'off',
            },
        ),
        required=False,
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Пароль',
            },
        ),
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Подтверждение пароля',
            },
        ),
    )

    class Meta:
        model = User
        fields = (
            'email',
            'surname',
            'name',
            'patronymic',
            'password1',
            'password2',
        )

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['email'].label = '*Почта'
        self.fields['name'].label = '*Имя'
        self.fields['surname'].label = '*Фамилия'
        self.fields['patronymic'].label = 'Отчество'
        self.fields['password1'].label = '*Пароль'
        self.fields['password2'].label = '*Подтверждение пароля'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                _('Пользователь с такой почтой уже существует.'),
            )
        return email


class AuthenticationForm(AuthenticationForm):
    """Custom Authentication form."""

    username = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'name@example.com',
                'autocomplete': 'username',
            },
        ),
    )

    def __init__(self, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'Почта'
        self.fields['password'].label = 'Пароль'


class AdminUserChangeForm(UserChangeForm):
    """Form for editing `User` (used on the admin panel)."""

    class Meta:
        model = User
        fields = (
            'email',
            'name',
            'surname',
            'patronymic',
        )


class PasswordResetForm(PasswordResetForm):
    """
    Custom password reset form.

    Send emails using Celery.
    """

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'id': 'floatingField',
                'placeholder': 'name@example.com',
            },
        ),
    )

    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)
        self.fields['email'].label = 'Почта'

    def send_mail(
            self,
            subject_template_name,
            email_template_name,
            context,
            from_email,
            to_email,
            html_email_template_name=None,
    ):
        context['user'] = context['user'].pk
        send_password_reset_code.delay(
            subject_template_name=subject_template_name,
            email_template_name=email_template_name,
            context=context,
            from_email=from_email,
            to_email=to_email,
            html_email_template_name=html_email_template_name,
        )


class SetPasswordForm(SetPasswordForm):
    """Custom set password form."""

    def __init__(self, *args, **kwargs):
        super(SetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].label = 'Новый пароль'
        self.fields['new_password2'].label = 'Подтверждение нового пароля'


class PasswordChangeForm(PasswordChangeForm):
    """Password change form."""

    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].label = 'Старый пароль'
        self.fields['new_password1'].label = 'Новый пароль'
        self.fields['new_password2'].label = 'Подтверждение нового пароля'


class UserInfoForm(forms.ModelForm):
    """Form for editing user info."""

    patronymic = forms.CharField(
        required=False,
    )

    class Meta:
        model = User
        fields = (
            'email',
            'surname',
            'name',
            'patronymic',
            'role',
        )

    def __init__(self, *args, **kwargs):
        super(UserInfoForm, self).__init__(*args, **kwargs)
        self.fields['email'].label = 'Почта'
        self.fields['name'].label = 'Имя'
        self.fields['surname'].label = 'Фамилия'
        self.fields['patronymic'].label = 'Отчество'
        self.fields['role'].label = 'Роль'


class ProfileForm(forms.ModelForm):
    """Form for editing profile info."""

    class Meta:
        model = Profile
        fields = (
            'date_of_birth',
            'year_of_study',
            'phone_number',
            'from_current_school',
            'school',
        )
        widgets = {
            'date_of_birth': DatePickerInput(
                options={
                    'format': 'DD-MM-YYYY',
                },
            ),
        }

    def __init__(self, *args, **kwargs):
        user_role = kwargs.pop('user_role', None)
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['date_of_birth'].label = 'Дата рождения'
        self.fields['school'].label = 'Школа'
        self.fields['from_current_school'].label = f"из {environ.get('SCHOOL_NAME')}"
        self.fields['year_of_study'].label = 'Год обучения'
        self.fields['phone_number'].label = 'Номер телефона'

        if self.instance and self.instance.from_current_school:
            self.fields['school'].widget = forms.HiddenInput()
            self.fields['school'].required = False

        if user_role and user_role != 'ученик':
            self.fields['year_of_study'].required = False
            self.fields['year_of_study'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        from_current_school = cleaned_data.get('from_current_school')
        if not from_current_school:
            cleaned_data['school'] = ''
        if from_current_school:
            cleaned_data['school'] = environ.get('SCHOOL_NAME')
        return cleaned_data

    def clean_date_of_birth(self):
        """Handles input of date_of_birth field.

        date of birth can't be in the future, must be at least 5 years old
        """
        date_of_birth = self.cleaned_data['date_of_birth']
        if date_of_birth:
            date_now = timezone.now().date()
            year_diff = (date_now.month, date_now.day) < (date_of_birth.month, date_of_birth.day)
            host_age = date_now.year - date_of_birth.year - year_diff
            if date_of_birth > date_now:
                raise ValidationError(
                    'Неверная дата: дата рождения в будущем.',
                    code='invalid',
                )
            elif host_age < 5:
                raise ValidationError(
                    'Неверная дата: вам должно быть не менее 5 лет.',
                    code='underage',
                )
        return date_of_birth
