import logging
from typing import Any
from typing import Dict
from typing import Optional  # pylint: disable=unused-import

from allauth.account import app_settings as allauth_settings
from allauth.account.adapter import get_adapter as allauth_get_adapter
from allauth.account.utils import setup_user_email
from allauth.utils import email_address_exists
from django.http import HttpRequest
from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers

from users.common.strings import ValidationErrorText
from users.common.utils import custom_validate_email_function
from users.models import CustomUser

logger = logging.getLogger(__name__)


class UserSerializer(CountryFieldMixin, serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"

    def validate_email(self, email: str) -> str:
        if self.instance is not None:
            instance_old_email = self.instance.email
        email = allauth_get_adapter().clean_email(email)
        custom_validate_email_function(email)
        if self.instance is not None and email != instance_old_email:
            try:
                CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                return email
            raise serializers.ValidationError(ValidationErrorText.VALIDATION_ERROR_EMAIL_MESSAGE_DOMAIN)
        else:
            if self.instance is not None and email != instance_old_email:
                try:
                    CustomUser.objects.get(email=email)
                except CustomUser.DoesNotExist:
                    return email
                raise serializers.ValidationError(ValidationErrorText.VALIDATION_ERROR_SIGNUP_EMAIL_MESSAGE)
        return email


class UserListSerializer(UserSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="users-detail")

    class Meta:
        model = CustomUser
        fields = ("url", "email", "first_name", "last_name")


class UserUpdateByAdminSerializer(UserSerializer):
    email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)

    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name", "date_of_birth", "phone_number", "country", "user_type")


class UserUpdateSerializer(UserSerializer):
    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "date_of_birth", "phone_number", "country")


class UserCreateSerializer(UserSerializer):
    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name", "user_type")


class CustomRegisterSerializer(serializers.Serializer):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.cleaned_data = None  # type: Optional[Dict[str, str]]

    email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)
    first_name = serializers.CharField(required=False, allow_blank=True, write_only=True)
    last_name = serializers.CharField(required=False, allow_blank=True, write_only=True)
    password = serializers.CharField(label="Password", required=True, write_only=True, style={"input_type": "password"})
    password_confirmation = serializers.CharField(
        label="Password confirmation", required=True, write_only=True, style={"input_type": "password"}
    )

    @staticmethod
    def validate_email(email: str) -> str:
        email = allauth_get_adapter().clean_email(email)
        custom_validate_email_function(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                logger.warning(f"Email: {email} already exist")
                raise serializers.ValidationError(ValidationErrorText.VALIDATION_ERROR_SIGNUP_EMAIL_MESSAGE)
        return email

    @staticmethod
    def validate_password(password: str) -> str:
        return allauth_get_adapter().clean_password(password)

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:  # pylint: disable=no-self-use
        if data["password"] != data["password_confirmation"]:
            raise serializers.ValidationError(ValidationErrorText.VALIDATION_ERROR_SIGNUP_PASSWORD_MESSAGE)
        return data

    def get_cleaned_data(self) -> Dict[str, str]:
        logger.debug("Get cleaned data method in CustomRegisterSerializer")
        return {
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
            "password1": self.validated_data.get("password", ""),
            "email": self.validated_data.get("email", ""),
        }

    def save(self, request: HttpRequest) -> "CustomUser":
        logger.debug("Save method for CustomRegisterSerializer")
        adapter = allauth_get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        setup_user_email(request, user, [])
        user.save()
        logger.info(f"New user with id: {user.pk} has been created")
        return user
