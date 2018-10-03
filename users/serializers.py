from allauth.account import app_settings as allauth_settings
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from allauth.utils import email_address_exists

from django_countries.serializers import CountryFieldMixin
from django_countries.serializer_fields import CountryField
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from users.common.strings import CustomValidationErrorText
from users.models import CustomUser


class UserSerializer(CountryFieldMixin, serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'


class UserListSerializer(UserSerializer):
    url = serializers.HyperlinkedIdentityField(
            view_name="users-detail",
    )
    class Meta:
        model = CustomUser
        fields = (
            'url',
            'email',
            'first_name',
            'last_name',
        )


class UserDetailSerializer(UserSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'email',
            'first_name',
            'last_name',
            'date_of_birth',
            'phone_number',
            'country',
            'user_type',
        )


class UserUpdateSerializer(UserSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'first_name',
            'last_name',
            'date_of_birth',
            'phone_number',
            'country',
        )


class UserCreateSerializer(UserSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'email',
            'first_name',
            'last_name',
            'date_of_birth',
            'phone_number',
            'country',
            'user_type',
            'is_staff',
            'is_superuser',
            'is_active',
        )


class CustomRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)
    first_name = serializers.CharField(required=False, write_only=True)
    last_name = serializers.CharField(required=False, write_only=True)
    password = serializers.CharField(required=True, write_only=True)
    password_confirmation = serializers.CharField(required=True, write_only=True)

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    CustomValidationErrorText.VALIDATION_ERROR_SIGNUP_EMAIL_MESSAGE)
        return email

    def validate_password(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError(
                CustomValidationErrorText.VALIDATION_ERROR_SIGNUP_PASSWORD_MESSAGE)
        return data

    def get_cleaned_data(self):
        return {
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'password': self.validated_data.get('password', ''),
            'email': self.validated_data.get('email', ''),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        setup_user_email(request, user, [])
        user.save()
        return user
