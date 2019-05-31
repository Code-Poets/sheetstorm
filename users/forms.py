from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
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


class SimpleUserChangeForm(ModelForm):
    """
    A form for updating users by EMPLOYEE users.
    """

    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "date_of_birth", "phone_number", "country")
        widgets = {"country": CountrySelectWidget(), "date_of_birth": DatePickerInput(options={"format": "YYYY-MM-DD"})}


class AdminUserChangeForm(ModelForm):
    """
    A form for updating users by ADMIN users. Includes more fields than `SimpleUserChangeForm`.
    """

    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name", "date_of_birth", "phone_number", "country", "user_type")
        widgets = {"country": CountrySelectWidget(), "date_of_birth": DatePickerInput(options={"format": "YYYY-MM-DD"})}


class CustomUserChangeForm(UserChangeForm):
    """
    A form for updating users. Includes all fields from user model,
    but replaces the password field with admin's
    password hash display field.
    """

    class Meta:
        model = CustomUser
        fields = "__all__"
        widgets = {"country": CountrySelectWidget(), "date_of_birth": DatePickerInput(options={"format": "YYYY-MM-DD"})}


class CustomUserSignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=constants.EMAIL_MAX_LENGTH, required=True, label="id_email")

    class Meta:
        model = CustomUser
        fields = ("email", "password1", "password2")
