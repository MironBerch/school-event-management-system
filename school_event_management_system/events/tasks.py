from celery import shared_task


@shared_task(
    bind=True,
    max_retries=1,
    default_retry_delay=60 * 60 * 24,  # Один день в секундах
)
def send_notify_about_diplomas_appearance_email(
        from_email: str,
        to_email: str,
        domain: str,
        diplomas_url: str,
        event: str,
) -> None:
    from .services import _send_diplomas_notification_email

    _send_diplomas_notification_email(
        from_email=from_email,
        to_email=to_email,
        domain=domain,
        diplomas_url=diplomas_url,
        event=event,
    )
