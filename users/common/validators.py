from django.core.validators import RegexValidator
from users.common.strings import CustomUserModelText


PhoneRegexValidator = RegexValidator(
    regex=r'^\d{9,15}$',
    message=CustomUserModelText.PHONE_REGEX_MESSAGE,
)
