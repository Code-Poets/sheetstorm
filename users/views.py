import logging
from typing import Type
from typing import Union

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.views import PasswordResetCompleteView
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetDoneView
from django.contrib.auth.views import PasswordResetView
from django.http import HttpRequest
from django.http import HttpResponse
from django.http.response import HttpResponseRedirectBase
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy
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

logger = logging.getLogger(__name__)


@api_view()
def api_root(request: HttpRequest, _format: str = None) -> Response:
    logger.debug(f"User with id: {request.user.pk} entered to api_root view")
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
    logger.info(f"User with id: {request.user.pk} is on home page")
    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    return render(request, "home.html", context={"num_visits": num_visits})


class SignUp(APIView):
    serializer_class = CustomRegisterSerializer
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = "signup.html"

    @classmethod
    def get(cls, request: HttpRequest) -> Response:
        logger.info(f"User get to the SignUp view with id: {request.user.pk}")
        serializer = CustomRegisterSerializer(context={"request": request})
        return Response({"serializer": serializer})

    @classmethod
    def post(cls, request: HttpRequest) -> Union[Response, HttpResponseRedirectBase]:
        logger.info(f"User with id: {request.user.pk} sent post to the SignUp view")
        serializer = CustomRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            logger.debug(f"Sent form is invalid due to those errors: {serializer.errors}")
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
        logger.info(f"User with id: {request.user.pk} entered UserCreate View")
        serializer = UserCreateSerializer(context={"request": request})
        return Response({"serializer": serializer})

    @classmethod
    def post(cls, request: HttpRequest) -> Union[Response, HttpResponseRedirectBase]:
        logger.debug(f"User with id: {request.user.pk} sent post on UserCreate View")
        serializer = UserCreateSerializer(data=request.data)
        if not serializer.is_valid():
            logger.debug(f"Sent form is invalid due to those errors: {serializer.errors}")
            return Response({"serializer": serializer, "errors": serializer.errors})
        email = serializer.validated_data.get("email")
        serializer.save()
        user = CustomUser.objects.get(email=email)
        user.set_password("passwduser")
        user.full_clean()
        user.save()
        logger.info(f"New user with id {user.pk} has been created")
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
        logger.info(f"User with id: {request.user.pk} get to the UserUpdateView")
        user = get_object_or_404(CustomUser, pk=pk)
        serializer = cls.return_suitable_serializer_for_get_method(request, user)
        return Response({"serializer": serializer, "user": user})

    @classmethod
    def post(cls, request: HttpRequest, pk: int) -> Union[Response, HttpResponseRedirectBase]:
        logger.info(f"User with id: {request.user.pk} sent post to the UserUpdateView")
        user = get_object_or_404(CustomUser, pk=pk)
        serializer = cls.return_suitable_serializer_for_post_method(request, user)
        if not serializer.is_valid():
            logger.debug(f"Sent form is invalid due to those errors: {serializer.errors}")
            return Response({"serializer": serializer, "user": user, "errors": serializer.errors})
        user = serializer.save()
        logger.info(f"User with id: {user.pk} has been updated")
        messages.success(request, ConfirmationMessages.SUCCESSFUL_UPDATE_USER_MESSAGE)
        return redirect("custom-user-update", pk=pk)


class UserUpdateByAdmin(APIView):
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = "users_detail.html"

    @classmethod
    def get(cls, request: HttpRequest, pk: int) -> Response:
        logger.info(
            f"Admin with id: {request.user.pk} get to the UserUpdateByAdmin view with data from user with id: {pk}"
        )
        user_detail = get_object_or_404(CustomUser, pk=pk)
        serializer = UserUpdateByAdminSerializer(user_detail, context={"request": request})
        return Response({"serializer": serializer, "user_detail": user_detail})

    @classmethod
    def post(cls, request: HttpRequest, pk: int) -> Union[Response, HttpResponseRedirectBase]:
        logger.info(f"Admin with id: {request.user.pk} get to the UserUpdateByAdmin view to update user with id: {pk}")
        user_detail = get_object_or_404(CustomUser, pk=pk)
        serializer = UserUpdateByAdminSerializer(user_detail, data=request.data, context={"request": request})
        if not serializer.is_valid():
            logger.debug(f"Serializer is not valid with those errors: {serializer.errors}")
            return Response({"serializer": serializer, "user_detail": user_detail, "errors": serializer.errors})
        user = serializer.save()
        logger.info(f"User with id: {user.pk} has been updated by admin with id {request.user.pk}")
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


class CustomPasswordChangeView(PasswordChangeView):

    template_name = "accounts/change_password.html"
    success_url = reverse_lazy("password_change")

    def form_valid(self, form: PasswordChangeView.form_class) -> HttpRequest:
        messages.success(self.request, ConfirmationMessages.SUCCESSFUL_USER_PASSWORD_CHANGE_MESSAGE)
        return super().form_valid(form)

    def form_invalid(self, form: PasswordChangeView.form_class) -> str:
        messages.error(self.request, ConfirmationMessages.FAILED_USER_PASSWORD_CHANGE_MESSAGE)
        return super().form_invalid(form)


class CustomPasswordResetView(PasswordResetView):

    email_template_name = "emails/password_reset_email.html"
    subject_template_name = "emails/password_reset_subject.txt"
    template_name = "accounts/password_reset_form.html"


class CustomPasswordResetDoneView(PasswordResetDoneView):

    template_name = "accounts/password_reset_done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):

    template_name = "accounts/password_reset_confirm.html"


class CustomPasswordResetCompleteView(PasswordResetCompleteView):

    template_name = "accounts/password_reset_complete.html"
