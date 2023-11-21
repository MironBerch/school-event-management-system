from typing import Any

from django.core.mail import EmailMultiAlternatives


def send_email_with_attachments(
        subject: str,
        body: str,
        email_to: list[str],
        email_from: str | None = None,
        alternatives: list[Any] | None = None,
) -> None:
    """Send an email with optional alternatives (html files, pdf, etc.)."""
    email = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=email_from,
        to=email_to,
    )

    if alternatives:
        for alternative_content, alternative_type in alternatives:
            email.attach_alternative(alternative_content, alternative_type)

    email.send()
