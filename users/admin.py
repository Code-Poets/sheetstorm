from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from users.models import CustomUser
from users.forms import CustomUserChangeForm
from users.forms import CustomUserCreationForm


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (
            None, {
                'fields': (
                    'email',
                    'password',
                )
            }
        ),
        (
            _('Personal info'), {
                'fields': (
                    'first_name',
                    'last_name',
                    'date_of_birth',
                    'phone_number',
                    'country'
                )
            }
        ),
        (
            _('Status'), {
                'fields': (
                    'user_type',
                )
            }
        ),
        (
            _('Permissions'), {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions'
                )
            }
        ),
        (
            _('Important dates'), {
                'fields': (
                    'last_login',
                )
            }
        ),
    )
    add_fieldsets = (
        (
            None, {
                'classes': (
                    'wide',
                ),
                'fields': (
                    'email',
                    'password1',
                    'password2'
                )
            }
        ),
    )
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = (
        'email',
        'first_name',
        'last_name',
        'last_login',
        'updated_at',
        'date_joined',
    )
    search_fields = (
        'email',
        'first_name',
        'last_name',
    )
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)
