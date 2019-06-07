from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six

from users.models import CustomUser


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user: CustomUser, timestamp: int) -> str:
        return (six.text_type(user.pk) + six.text_type(timestamp)) + six.text_type(user.is_active)


account_activation_token = AccountActivationTokenGenerator()
