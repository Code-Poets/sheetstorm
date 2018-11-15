from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from users.common.fields import Action
from users.models import CustomUser
from users.permissions import IsAdminUser
from users.permissions import IsOwnerOrAdmin
from users.serializers import UserCreateSerializer
from users.serializers import UserDetailSerializer
from users.serializers import UserListSerializer
from users.serializers import UserSerializer
from users.serializers import UserUpdateSerializer


@api_view()
def api_root(request, format=None):
    if request.user.is_authenticated and request.user.user_type == CustomUser.UserType.ADMIN.name:
        return Response({
                'users': reverse(
                    'users-list',
                    request=request,
                    format=format,
                ),
                'account': reverse(
                    'user-account-detail',
                    args=(request.user.pk,),
                    request=request,
                    format=format,
                ),
            })
    elif request.user.is_authenticated:
        return Response({
                'account': reverse(
                    'user-account-detail',
                    args=(request.user.pk,),
                    request=request,
                    format=format,
                ),
            })
    else:
        return Response({
                'registration': reverse(
                    'rest_register',
                    request=request,
                    format=format,
                ),
            })


class UsersViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = (IsAdminUser,)

    def get_serializer_class(self):
        if self.action == Action.LIST.value:
            return UserListSerializer
        if self.action == Action.RETRIEVE.value:
            return UserDetailSerializer
        if self.action == Action.CREATE.value:
            return UserCreateSerializer
        if self.action == Action.UPDATE.value:
            return UserCreateSerializer
        return UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = (IsOwnerOrAdmin,)

    def get_serializer_class(self):
        if self.action == Action.RETRIEVE.value:
            return UserDetailSerializer
        if self.action == Action.UPDATE.value:
            return UserUpdateSerializer
        return UserSerializer
