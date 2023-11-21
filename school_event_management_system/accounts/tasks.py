from typing import Optional

from celery import shared_task


@shared_task
def send_email_verification_code(
        domain: str,
        scheme: str,
        user_id: int | str,
) -> None:
    from .services import send_verification_email
    send_verification_email(
        domain=domain,
        scheme=scheme,
        user_id=user_id,
    )


@shared_task
def send_password_reset_code(
        subject_template_name: str,
        email_template_name: str,
        context: dict,
        from_email: str,
        to_email: str,
        html_email_template_name: Optional[str] = None,
) -> None:
    from .services import _send_password_reset_email, get_user_by_pk

    context['user'] = get_user_by_pk(pk=context['user'])
    _send_password_reset_email(
        subject_template_name=subject_template_name,
        email_template_name=email_template_name,
        context=context,
        from_email=from_email,
        to_email=to_email,
        html_email_template_name=html_email_template_name,
    )
