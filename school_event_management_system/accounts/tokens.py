import six

from django.contrib.auth.tokens import PasswordResetTokenGenerator

from accounts.models import User


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user: User, timestamp: str):
        return (
            six.text_type(user.pk) +
            six.text_type(timestamp) +
            six.text_type(user.is_email_confirmed)
        )


account_activation_token = AccountActivationTokenGenerator()
