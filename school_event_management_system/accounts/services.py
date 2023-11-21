from typing import Optional, Union

from django.contrib.auth.models import Group
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.template.loader import get_template, render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from accounts.models import User, UserManager
from accounts.tasks import send_email_verification_code
from accounts.tokens import account_activation_token
from common.services import is_cooldown_ended, set_key_with_timeout
from mailings.services import send_email_with_attachments


def _send_password_reset_email(
        *,
        subject_template_name: str,
        email_template_name: str,
        context: dict,
        from_email: str,
        to_email: str,
        html_email_template_name: Optional[str] = None,
) -> None:
    subject = render_to_string(subject_template_name, context)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    body = render_to_string(email_template_name, context)

    html = get_template(html_email_template_name)
    html_content = html.render(context)

    send_email_with_attachments(
        subject=subject,
        body=body,
        email_to=[to_email],
        email_from=from_email,
        alternatives=[(html_content, 'text/html')],
    )


def send_verification_email(*, domain: str, scheme: str, user_id: Union[int, str]) -> None:
    user = User.objects.get(pk=user_id)
    subject = 'Активируйте вашу учетную запись'
    text_content = render_to_string(
        template_name='registration/account_activation_email.html',
        context={
            'user': user,
            'protocol': scheme,
            'domain': domain,
            'uid': urlsafe_base64_encode(force_bytes(user_id)),
            'token': account_activation_token.make_token(user),
        },
    )
    html = get_template(template_name='registration/account_activation_email.html')
    html_content = html.render(
        context={
            'user': user,
            'protocol': scheme,
            'domain': domain,
            'uid': urlsafe_base64_encode(force_bytes(user_id)),
            'token': account_activation_token.make_token(user),
        },
    )
    send_email_with_attachments(
        subject=subject,
        body=text_content,
        email_to=[user.email],
        alternatives=[(html_content, 'text/html')],
    )


def send_verification_link(domain: str, scheme: str, user: User) -> None:
    """Send email verification link."""
    user_id = user.pk
    email_sent_key = f'accounts:user:{user_id}:email.sent'
    if not is_cooldown_ended(email_sent_key):
        return
    set_key_with_timeout(email_sent_key, 60, 1)

    send_email_verification_code.delay(domain=domain, scheme=scheme, user_id=user_id)


def get_user_by_pk(pk: Union[int, str]) -> Optional[User]:
    return get_object_or_404(User, pk=pk)


def get_user_by_email(email: str) -> QuerySet[User]:
    return User.objects.filter(email=UserManager.normalize_email(email))


def get_user_from_uid(uid: str) -> User:
    uid = force_str(urlsafe_base64_decode(force_str(uid)))
    user: User = User.objects.get(id=uid)
    return user


def add_user_to_group(user: User, group_name: str) -> None:
    group = Group.objects.get_or_create(name=group_name)[0]
    user.groups.add(group)


def update_user_email_confirmation_status(user: User, is_email_confirmed: bool) -> User:
    user.is_email_confirmed = is_email_confirmed
    user.save(update_fields=['is_email_confirmed'])
    return user
