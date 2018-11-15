from rest_framework import permissions
from users.models import CustomUser


class IsAdminUser(permissions.BasePermission):
    message = 'You are not allowed to enter - for admin only.'
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_type == CustomUser.UserType.ADMIN.name


class IsOwnerOrAdmin(permissions.BasePermission):
    message = "It's none of your business."
    def has_permission(self, request, view):
        return (view.get_object() == request.user) or (request.user and request.user.is_authenticated and request.user.user_type == CustomUser.UserType.ADMIN.name)
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return request.user.user_type == CustomUser.UserType.ADMIN.name or obj == request.user
