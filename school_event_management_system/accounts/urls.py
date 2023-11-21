from django.contrib.auth.decorators import login_required
from django.urls import path

from accounts.views import (
    AccountActivationView,
    AccountSettingsDashboardView,
    ActivationRequiredView,
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
    PersonalInfoEditView,
    SecurityDashboardView,
    SendConfirmationEmailView,
    SignInView,
    SignOutView,
    SignUpView,
)

urlpatterns = [
    # authentication urls
    path(
        route='signup/',
        view=SignUpView.as_view(),
        name='signup',
    ),
    path(
        route='signin/',
        view=SignInView.as_view(),
        name='signin',
    ),
    path(
        route='signout/',
        view=SignOutView.as_view(),
        name='signout',
    ),

    # password change urls
    path(
        route='password_change/',
        view=PasswordChangeView.as_view(),
        name='password_change',
    ),
    path(
        route='password_change/done/',
        view=PasswordChangeDoneView.as_view(),
        name='password_change_done',
    ),

    # password reset urls
    path(
        'password_reset/',
        PasswordResetView.as_view(),
        name='password_reset',
    ),
    path(
        route='password_reset/done/',
        view=PasswordResetDoneView.as_view(),
        name='password_reset_done',
    ),
    path(
        route='reset/<uidb64>/<token>/',
        view=PasswordResetConfirmView.as_view(),
        name='password_reset_confirm',
    ),
    path(
        route='reset/done/',
        view=PasswordResetCompleteView.as_view(),
        name='password_reset_complete',
    ),

    # settings urls
    path(
        route='settings/',
        view=AccountSettingsDashboardView.as_view(),
        name='settings_dashboard',
    ),
    path(
        route='settings/personal-info/',
        view=login_required(
            PersonalInfoEditView.as_view(),
        ),
        name='user_info_edit',
    ),
    path(
        route='settings/login-and-security/',
        view=SecurityDashboardView.as_view(),
        name='security_dashboard',
    ),
    path(
        route='settings/login-and-security/confirm-email/',
        view=SendConfirmationEmailView.as_view(),
        name='confirm_email',
    ),

    # email verification urls
    path(
        route='activate/<uidb64>/<token>/',
        view=AccountActivationView.as_view(),
        name='activate',
    ),
    path(
        route='activation-required/',
        view=ActivationRequiredView.as_view(),
        name='activation_required',
    ),
]
