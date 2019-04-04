from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.common.strings import CustomUserAdminText
from users.forms import CustomUserChangeForm
from users.forms import CustomUserCreationForm
from users.models import CustomUser


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            CustomUserAdminText.PERSONAL_INFO,
            {"fields": ("first_name", "last_name", "date_of_birth", "phone_number", "country")},
        ),
        (CustomUserAdminText.STATUS, {"fields": ("user_type",)}),
        (
            CustomUserAdminText.PERMISSIONS,
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        (CustomUserAdminText.IMPORTANT_DATES, {"fields": ("last_login",)}),
    )
    add_fieldsets = ((None, {"classes": ("wide"), "fields": ("email", "password1", "password2")}),)
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ("email", "first_name", "last_name", "last_login", "updated_at", "date_joined")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)


admin.site.register(CustomUser, CustomUserAdmin)
