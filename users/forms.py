from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import UserCreationForm
from django_countries.widgets import CountrySelectWidget

from users.common import constants
from users.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """
    A form that creates a user, without privileges,
    from given email and password.
    """

    class Meta:
        model = CustomUser
        fields = ("email",)


class CustomUserChangeForm(UserChangeForm):
    """
    A form for updating users. Includes all fields from user model,
    but replaces the password field with admin's
    password hash display field.
    """

    class Meta:
        model = CustomUser
        fields = "__all__"
        widgets = {"country": CountrySelectWidget()}


class CustomUserSignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=constants.EMAIL_MAX_LENGTH, required=True, label="id_email")

    class Meta:
        model = CustomUser
        fields = ("email", "password1", "password2")
