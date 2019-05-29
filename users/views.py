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
from django.forms import ModelForm
from django.http import HttpRequest
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.http.response import HttpResponseRedirectBase
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from users.common.fields import Action
from users.common.strings import ConfirmationMessages
from users.common.strings import SuccessInfoAfterRegistrationText
from users.forms import AdminUserChangeForm
from users.forms import CustomUserCreationForm
from users.forms import CustomUserSignUpForm
from users.forms import SimpleUserChangeForm
from users.models import CustomUser
from users.permissions import AuthenticatedAdmin
from users.permissions import AuthenticatedAdminOrOwnerUser
from users.serializers import UserCreateSerializer
from users.serializers import UserListSerializer
from users.serializers import UserSerializer
from users.serializers import UserUpdateByAdminSerializer
from users.serializers import UserUpdateSerializer
from utils.decorators import check_permissions

logger = logging.getLogger(__name__)


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
    return render(request, "home.html")


class SignUp(FormView):
    form_class = CustomUserSignUpForm
    template_name = "signup.html"

    def form_valid(self, form: CustomUserSignUpForm) -> Union[Response, HttpResponseRedirectBase]:
        user = form.save()
        logger.info(f"New user with id: {user.pk} has been created")
        return redirect("success-signup")


class UserSignUpSuccess(TemplateView):
    template_name = "accounts/success-registration.html"
    extra_context = {"MESSAGES": SuccessInfoAfterRegistrationText}


@method_decorator(login_required, name="dispatch")
class UserCreate(CreateView):
    template_name = "user_create.html"
    form_class = CustomUserCreationForm

    def get_success_url(self) -> str:
        return reverse("custom-users-list")

    def from_valid(self, form: CustomUserCreationForm) -> HttpResponseRedirect:
        super().form_valid(form)
        return redirect(self.get_success_url())


@method_decorator(login_required, name="dispatch")
class UserUpdate(UpdateView):
    template_name = "user_update.html"
    form_class = SimpleUserChangeForm
    admins_form_class = AdminUserChangeForm
    model = CustomUser

    def get_form_class(self) -> Type[ModelForm]:
        if self.request.user.user_type == CustomUser.UserType.ADMIN.name:
            return self.admins_form_class
        return self.form_class

    def get_success_url(self) -> str:
        return reverse("custom-user-update", kwargs={"pk": self.object.pk})

    def form_valid(self, form: SimpleUserChangeForm) -> HttpResponse:
        super().form_valid(form)
        messages.success(self.request, ConfirmationMessages.SUCCESSFUL_UPDATE_USER_MESSAGE)
        return redirect(self.get_success_url())


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


@method_decorator(login_required, name="dispatch")
@method_decorator(check_permissions(allowed_user_types=[CustomUser.UserType.ADMIN.name]), name="dispatch")
class UserList(ListView):
    template_name = "users_list.html"
    model = CustomUser
    queryset = CustomUser.objects.prefetch_related("projects")


class CustomPasswordChangeView(PasswordChangeView):

    template_name = "accounts/change_password.html"
    success_url = reverse_lazy("password_change")

    def form_valid(self, form: PasswordChangeView.form_class) -> HttpRequest:
        messages.success(self.request, ConfirmationMessages.SUCCESSFUL_USER_PASSWORD_CHANGE_MESSAGE)
        logger.info(f"User with id: {self.request.user.pk} has changed his password")
        return super().form_valid(form)

    def form_invalid(self, form: PasswordChangeView.form_class) -> str:
        logger.info(f"User with id: {self.request.user.pk} sent invalid form to CustomPasswordChange view")
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
