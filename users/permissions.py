from rest_framework import permissions

from users.models import CustomUser


class ReportAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class AuthenticatedAdmin(permissions.BasePermission):
    message = 'You are not allowed to enter - for admin only.'

    def has_permission(self, request, view):
        is_user_authenticated = request.user and request.user.is_authenticated
        is_user_admin = request.user.user_type == CustomUser.UserType.ADMIN.name
        return  is_user_authenticated and is_user_admin

class AuthenticatedAdminOrUser(permissions.BasePermission):
    message = "It's none of your business."

    def has_permission(self, request, view):
        is_user_authenticated = request.user and request.user.is_authenticated
        is_user_admin = request.user.user_type == CustomUser.UserType.ADMIN.name
        is_object_owner = view.get_object() == request.user
        return (is_object_owner) or (is_user_authenticated and is_user_admin)

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return request.user.user_type == CustomUser.UserType.ADMIN.name or obj == request.user


class AuthenticatedManager(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.user_type == CustomUser.UserType.MANAGER.value
        return False
