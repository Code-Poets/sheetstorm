from captcha.fields import CaptchaField
from captcha.fields import CaptchaTextInput
from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from users.common.constants import CaptchaConstants
from users.common.constants import UserConstants
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
        fields = ("first_name", "last_name")


class AdminUserChangeForm(ModelForm):
    """
    A form for updating users by ADMIN users. Includes more fields than `SimpleUserChangeForm`.
    """

    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name", "user_type")


class CustomUserChangeForm(UserChangeForm):
    """
    A form for updating users. Includes all fields from user model,
    but replaces the password field with admin's
    password hash display field.
    """

    class Meta:
        model = CustomUser
        fields = "__all__"


class CustomUserSignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=UserConstants.EMAIL_MAX_LENGTH.value, required=True, label="id_email")
    captcha = CaptchaField(widget=CaptchaTextInput(attrs={"placeholder": CaptchaConstants.PLACE_HOLDER_CAPTCHA.value}))

    class Meta:
        model = CustomUser
        fields = ("email", "password1", "password2", "captcha")
