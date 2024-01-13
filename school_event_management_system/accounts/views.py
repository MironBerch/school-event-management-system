from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View
from django.views.generic.base import TemplateResponseMixin

from accounts.constants import (
    EMAIL_CONFIRMATION_FAILURE_RESPONSE_MESSAGE,
    EMAIL_CONFIRMATION_SUCCESS_RESPONSE_MESSAGE,
    EMAIL_SENT_SUCCESSFULLY_RESPONSE_MESSAGE,
    PROFILE_INFO_EDIT_SUCCESS_RESPONSE_MESSAGE,
)
from accounts.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    ProfileForm,
    SetPasswordForm,
    SignUpForm,
    UserInfoForm,
)
from accounts.mixins import AnonymousUserRequiredMixin, UnconfirmedEmailRequiredMixin
from accounts.models import User
from accounts.services import (
    get_user_from_uid,
    send_verification_link,
    set_profile_values_after_user_registration,
    update_user_email_confirmation_status,
    update_user_profile_year_of_study,
)
from accounts.tokens import account_activation_token


class SignUpView(
    AnonymousUserRequiredMixin,
    TemplateResponseMixin,
    View,
):
    """Просмотр для создания новой учетной записи."""

    form_class = SignUpForm
    template_name = 'registration/signup.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        return self.render_to_response(
            context={
                'form': self.form_class(),
            },
        )

    def post(self, request: HttpRequest, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            send_verification_link(
                get_current_site(request).domain,
                request.scheme,
                user,
            )
            set_profile_values_after_user_registration(
                profile=user.profile,
                phone_number=form.cleaned_data['phone_number'],
                school=form.cleaned_data['school'],
                year_of_study=form.cleaned_data['year_of_study'],
            )
            messages.add_message(
                request,
                messages.SUCCESS,
                EMAIL_SENT_SUCCESSFULLY_RESPONSE_MESSAGE,
            )
            return redirect('events_list')
        return self.render_to_response(
            context={
                'form': form,
            },
        )


class SignInView(
    AnonymousUserRequiredMixin,
    LoginView,
):
    """Просмотр для входа в систему."""

    form_class = AuthenticationForm
    template_name = 'registration/signin.html'


class SignOutView(
    LoginRequiredMixin,
    LogoutView,
):
    """Просмотр для выхода из системы."""

    template_name = 'registration/signout.html'
    next_page = None


class AccountActivationView(
    LoginRequiredMixin,
    View,
):
    """Просмотр для подтверждения адреса электронной почты пользователя."""

    def get(self, request: HttpRequest, uidb64, token, *args, **kwargs):
        try:
            user = get_user_from_uid(uidb64)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user = update_user_email_confirmation_status(user=user, is_email_confirmed=True)
            messages.add_message(
                request,
                messages.SUCCESS,
                EMAIL_CONFIRMATION_SUCCESS_RESPONSE_MESSAGE,
            )
            return redirect('security_dashboard')

        messages.add_message(
            request,
            messages.ERROR,
            EMAIL_CONFIRMATION_FAILURE_RESPONSE_MESSAGE,
        )
        return redirect('security_dashboard')


class PasswordResetView(PasswordResetView):
    """Просмотр для сброса пароля."""

    template_name = 'registration/password_reset.html'
    success_url = reverse_lazy('password_reset_done')
    html_email_template_name = 'registration/password_reset_email.html'
    email_template_name = 'registration/password_reset_email.html'
    form_class = PasswordResetForm


class PasswordResetDoneView(PasswordResetDoneView):
    """Просмотр для показа, что сброс пароля выполнен."""

    template_name = 'registration/password_reset_done.html'


class PasswordResetConfirmView(PasswordResetConfirmView):
    """Просмотр для подтверждения сброса пароля."""

    form_class = SetPasswordForm
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class PasswordResetCompleteView(PasswordResetCompleteView):
    """Просмотр для показа, что сброс пароля завершен."""

    template_name = 'registration/password_reset_complete.html'


class PasswordChangeView(PasswordChangeView):
    """Просмотр для смены пароля."""

    form_class = PasswordChangeForm
    template_name = 'registration/password_change.html'
    success_url = reverse_lazy('password_change_done')


class PasswordChangeDoneView(PasswordChangeDoneView):
    """Просмотр для показа, что смена пароля завершена."""

    template_name = 'registration/password_change_done.html'


class ActivationRequiredView(
    LoginRequiredMixin,
    TemplateView,
):
    """
    Отображение страницы ошибки: для страницы требуется подтвержденный адрес электронной почты.
    """

    template_name = 'registration/account_activation_required.html'


class SendConfirmationEmailView(
    UnconfirmedEmailRequiredMixin,
    LoginRequiredMixin,
    View,
):
    """Просмотр отправки электронного письма с подтверждением пользователю."""

    def get(self, request: HttpRequest, *args, **kwargs):
        send_verification_link(get_current_site(request).domain, request.scheme, request.user)
        messages.add_message(request, messages.SUCCESS, EMAIL_SENT_SUCCESSFULLY_RESPONSE_MESSAGE)
        return redirect('security_dashboard')


class AccountSettingsDashboardView(
    LoginRequiredMixin,
    TemplateView,
):
    """Представление для отображения панели управления учетной записью."""

    template_name = 'settings/settings_dashboard.html'


class PersonalInfoEditView(
    LoginRequiredMixin,
    TemplateResponseMixin,
    View,
):
    """Просмотр для редактирования личной информации пользователя."""

    template_name = 'settings/user_form.html'
    profile_form: ProfileForm = None
    user_info_form: UserInfoForm = None

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        self.profile_form = ProfileForm(
            user_role=request.user.role,
            data=request.POST or None,
            instance=request.user.profile,
        )
        self.user_info_form = UserInfoForm(
            data=request.POST or None,
            instance=request.user,
        )
        return super(PersonalInfoEditView, self).dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args, **kwargs):
        return self.render_to_response(
            context={
                'user_info_form': self.user_info_form,
                'profile_form': self.profile_form,
            },
        )

    def post(self, request: HttpRequest, *args, **kwargs):
        if self.user_info_form.is_valid() and self.profile_form.is_valid():
            self.user_info_form.save()
            self.profile_form.save()

            # if email has been changed
            if 'email' in self.user_info_form.changed_data:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    EMAIL_SENT_SUCCESSFULLY_RESPONSE_MESSAGE,
                )
                update_user_email_confirmation_status(request.user, is_email_confirmed=False)
                send_verification_link(
                    get_current_site(request).domain,
                    request.scheme,
                    request.user,
                )

            if (
                'role' in self.user_info_form.changed_data and
                self.user_info_form.cleaned_data['role'] != 'ученик'
            ):
                update_user_profile_year_of_study(profile=request.user.profile)

            if self.profile_form.changed_data or self.user_info_form.changed_data:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    PROFILE_INFO_EDIT_SUCCESS_RESPONSE_MESSAGE,
                )

            return redirect('user_info_edit')

        return self.render_to_response(
            context={
                'user_info_form': self.user_info_form,
                'profile_form': self.profile_form,
            },
        )


class SecurityDashboardView(
    LoginRequiredMixin,
    TemplateView,
):
    """Представление для отображения панели управления `Login & Security`."""

    template_name = 'settings/security_dashboard.html'
