from typing import Type
from typing import Union

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpRequest
from django.http import HttpResponse
from django.http.response import HttpResponseRedirectBase
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from rest_framework import permissions
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from users.common.fields import Action
from users.common.strings import ConfirmationMessages
from users.models import CustomUser
from users.permissions import AuthenticatedAdmin
from users.permissions import AuthenticatedAdminOrOwnerUser
from users.serializers import CustomRegisterSerializer
from users.serializers import UserCreateSerializer
from users.serializers import UserListSerializer
from users.serializers import UserSerializer
from users.serializers import UserUpdateByAdminSerializer
from users.serializers import UserUpdateSerializer


@api_view()
def api_root(request: HttpRequest, _format: str = None) -> Response:
    if request.user.is_authenticated and request.user.user_type == CustomUser.UserType.ADMIN.name:
        return Response(
            {
                "users": reverse("users-list", request=request, format=_format),
                "account": reverse("user-account-detail", args=(request.user.pk,), request=request, format=_format),
            }
        )
    elif request.user.is_authenticated:
        return Response(
            {"account": reverse("user-account-detail", args=(request.user.pk,), request=request, format=_format)}
        )
    else:
        return Response({"registration": reverse("rest_register", request=request, format=_format)})


class UsersViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = (AuthenticatedAdmin,)

    def get_serializer_class(
        self
    ) -> Type[Union[UserListSerializer, UserUpdateByAdminSerializer, UserCreateSerializer, UserSerializer]]:
        if self.action == Action.LIST.value:  # pylint: disable=no-member
            return UserListSerializer
        elif self.action == Action.RETRIEVE.value:  # pylint: disable=no-member
            return UserUpdateByAdminSerializer
        elif self.action in [Action.CREATE.value, Action.UPDATE.value]:  # pylint: disable=no-member
            return UserCreateSerializer
        else:
            return UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = (AuthenticatedAdminOrOwnerUser,)

    def get_serializer_class(self) -> Type[Union[UserUpdateByAdminSerializer, UserUpdateSerializer, UserSerializer]]:
        if self.action == Action.RETRIEVE.value:  # pylint: disable=no-member
            return UserUpdateByAdminSerializer
        elif self.action == Action.UPDATE.value:  # pylint: disable=no-member
            return UserUpdateSerializer
        else:
            return UserSerializer


@login_required
def index(request: HttpRequest) -> HttpResponse:
    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    return render(request, "home.html", context={"num_visits": num_visits})


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, ConfirmationMessages.SUCCESSFUL_USER_PASSWORD_CHANGE_MESSAGE)
            return redirect('change_password')
        else:
            messages.error(request, ConfirmationMessages.FAILED_USER_PASSWORD_CHANGE_MESSAGE)
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {
        'form': form
    })


class SignUp(APIView):
    serializer_class = CustomRegisterSerializer
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = "signup.html"

    @classmethod
    def get(cls, request: HttpRequest) -> Response:
        serializer = CustomRegisterSerializer(context={"request": request})
        return Response({"serializer": serializer})

    @classmethod
    def post(cls, request: HttpRequest) -> Union[Response, HttpResponseRedirectBase]:
        serializer = CustomRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "serializer": serializer,
                    "errors": serializer.errors,
                    "non_field_errors": serializer.errors.get("non_field_errors"),
                }
            )
        else:
            serializer.save(request)
            return redirect("login")


class UserCreate(APIView):
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = "user_create.html"

    @classmethod
    def get(cls, request: HttpRequest) -> Response:
        serializer = UserCreateSerializer(context={"request": request})
        return Response({"serializer": serializer})

    @classmethod
    def post(cls, request: HttpRequest) -> Union[Response, HttpResponseRedirectBase]:
        serializer = UserCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"serializer": serializer, "errors": serializer.errors})
        email = serializer.validated_data.get("email")
        serializer.save()
        user = CustomUser.objects.get(email=email)
        user.set_password("passwduser")
        user.full_clean()
        user.save()
        return redirect("custom-users-list")


class UserUpdate(APIView):
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = "user_update.html"

    @classmethod
    def return_suitable_serializer_for_get_method(
        cls, request: HttpRequest, user: CustomUser
    ) -> Union[UserUpdateByAdminSerializer, UserUpdateSerializer]:
        if request.user.user_type == CustomUser.UserType.ADMIN.name:
            return UserUpdateByAdminSerializer(user, context={"request": request})
        else:
            return UserUpdateSerializer(user, context={"request": request})

    @classmethod
    def return_suitable_serializer_for_post_method(
        cls, request: HttpRequest, user: CustomUser
    ) -> Union[UserUpdateByAdminSerializer, UserUpdateSerializer]:
        if request.user.user_type == CustomUser.UserType.ADMIN.name:
            return UserUpdateByAdminSerializer(user, data=request.data, context={"request": request})
        else:
            return UserUpdateSerializer(user, data=request.data, context={"request": request})

    @classmethod
    def get(cls, request: HttpRequest, pk: int) -> Response:
        user = get_object_or_404(CustomUser, pk=pk)
        serializer = cls.return_suitable_serializer_for_get_method(request, user)
        return Response({"serializer": serializer, "user": user})

    @classmethod
    def post(cls, request: HttpRequest, pk: int) -> Union[Response, HttpResponseRedirectBase]:
        user = get_object_or_404(CustomUser, pk=pk)
        serializer = cls.return_suitable_serializer_for_post_method(request, user)
        if not serializer.is_valid():
            return Response({"serializer": serializer, "user": user, "errors": serializer.errors})
        serializer.save()
        messages.success(request, ConfirmationMessages.SUCCESSFUL_UPDATE_USER_MESSAGE)
        return redirect("custom-user-update", pk=pk)


class UserUpdateByAdmin(APIView):
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = "users_detail.html"

    @classmethod
    def get(cls, request: HttpRequest, pk: int) -> Response:
        user_detail = get_object_or_404(CustomUser, pk=pk)
        serializer = UserUpdateByAdminSerializer(user_detail, context={"request": request})
        return Response({"serializer": serializer, "user_detail": user_detail})

    @classmethod
    def post(cls, request: HttpRequest, pk: int) -> Union[Response, HttpResponseRedirectBase]:
        user_detail = get_object_or_404(CustomUser, pk=pk)
        serializer = UserUpdateByAdminSerializer(user_detail, data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response({"serializer": serializer, "user_detail": user_detail, "errors": serializer.errors})
        serializer.save()
        messages.success(request, ConfirmationMessages.SUCCESSFUL_UPDATE_USER_MESSAGE)
        return redirect("custom-user-update-by-admin", pk=pk)


class UserList(APIView):
    serializer_class = UserListSerializer
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = "users_list.html"
    permission_classes = (permissions.IsAuthenticated,)

    @classmethod
    def get_queryset(cls) -> CustomUser:
        return CustomUser.objects.order_by("id")

    @classmethod
    def get(cls, request: HttpRequest) -> Response:
        users_queryset = cls.get_queryset()
        users_serializer = UserListSerializer(context={"request": request})
        return Response({"serializer": users_serializer, "users_list": users_queryset})
