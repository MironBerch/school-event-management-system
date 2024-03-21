from os import environ

from django.contrib.auth.models import Group
from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404
from django.template.loader import get_template, render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from accounts.models import Profile, User, UserManager
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
        html_email_template_name: str | None = None,
) -> None:
    """
    Функция для отправки электронного письма с инструкцией по сбросу пароля.

    Аргументы:
    - subject_template_name (строка): Имя шаблона заголовка электронной почты.
    - email_template_name (строка): Имя шаблона текста электронной почты.
    - context (словарь): Контекстные данные для заполнения шаблонов.
    - from_email (строка): Адрес электронной почты отправителя.
    - to_email (строка): Адрес электронной почты получателя.
    - html_email_template_name (строка, необязательно): Имя шаблона HTML-электронной почты.
    """

    subject = render_to_string(subject_template_name, context)
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


def send_verification_email(*, domain: str, scheme: str, user_id: int | str) -> None:
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
    """Отправить ссылку для подтверждения электронной почты."""
    user_id = user.pk
    email_sent_key = f'accounts:user:{user_id}:email.sent'
    if not is_cooldown_ended(email_sent_key):
        return
    set_key_with_timeout(email_sent_key, 60, 1)

    send_email_verification_code.delay(domain=domain, scheme=scheme, user_id=user_id)


def get_user_by_pk(pk: int | str) -> User | None:
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


def get_user_by_fio(fio: str) -> User | None:
    try:
        fio_list = ' '.join(fio.strip().split()).split(' ')
    except AttributeError:
        return None
    if len(fio_list) < 2:
        return None
    try:
        if len(fio_list) == 3:
            return User.objects.filter(
                Q(surname=fio_list[0]) &
                Q(name=fio_list[1]) &
                Q(patronymic=fio_list[2]),
            ).first()
        else:
            return User.objects.filter(
                Q(surname=fio_list[0]) &
                Q(name=fio_list[1]),
            ).first()
    except User.DoesNotExist:
        return None


def is_user_with_fio_exist(fio: str) -> bool:
    fio_list = ' '.join(fio.strip().split()).split(' ')
    if len(fio_list) < 2:
        return False
    try:
        if len(fio_list) == 3:
            return User.objects.filter(
                Q(surname=fio_list[0]) &
                Q(name=fio_list[1]) &
                Q(patronymic=fio_list[2]),
            ).exists()
        else:
            return User.objects.filter(
                Q(surname=fio_list[0]) &
                Q(name=fio_list[1]),
            ).exists()
    except User.DoesNotExist:
        return False


def update_user_profile_year_of_study(profile: Profile) -> None:
    profile.year_of_study = None
    profile.save()


def get_user_by_id(id: int) -> User:
    try:
        User.objects.get(id=id)
    except User.DoesNotExist:
        return None


def set_profile_values_after_user_registration(
        profile: Profile,
        phone_number,
        school,
        year_of_study,
):
    profile.phone_number = phone_number
    if school != environ.get('SCHOOL_NAME'):
        profile.from_current_school = False
    profile.school = school
    profile.year_of_study = year_of_study
    profile.save()
