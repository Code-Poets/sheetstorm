from django import template

from users.models import CustomUser

register = template.Library()


@register.simple_tag
def get_manager_user_type():
    return CustomUser.UserType.MANAGER.name


@register.simple_tag
def get_admin_user_type():
    return CustomUser.UserType.ADMIN.name
