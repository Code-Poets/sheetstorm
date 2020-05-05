import datetime
import logging
from typing import Any
from typing import Optional
from typing import Type

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.views import PasswordResetCompleteView
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetDoneView
from django.contrib.auth.views import PasswordResetView
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import F
from django.db.models import Max
from django.db.models import QuerySet
from django.db.models.functions import Coalesce
from django.forms import ModelForm
from django.http import HttpRequest
from django.http import HttpResponse
from django.http.response import HttpResponseRedirectBase
from django.shortcuts import redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views.generic import CreateView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView

from common.utils import render_confirmation_email
from common.utils import send_email
from users.common.strings import AccountConfirmationText
from users.common.strings import ConfirmationMessages
from users.common.strings import SuccessInfoAfterRegistrationText
from users.common.strings import UserNotificationsText
from users.common.utils import count_workdays
from users.forms import AdminUserChangeForm
from users.forms import CustomUserCreationForm
from users.forms import CustomUserSignUpForm
from users.forms import SimpleUserChangeForm
from users.models import CustomUser
from users.tokens import account_activation_token
from utils.decorators import check_permissions

logger = logging.getLogger(__name__)


class SignUp(FormView):
    form_class = CustomUserSignUpForm
    template_name = "signup.html"

    def _send_activation_email(self, user: CustomUser) -> None:
        current_site = get_current_site(self.request)
        message = render_confirmation_email(user, current_site.domain)
        send_email(mail_subject="Activate your Sheet Storm account.", message=message, addressee=user.email)

    def form_valid(self, form: CustomUserSignUpForm) -> HttpResponseRedirectBase:
        user = form.save()
        if settings.EMAIL_SIGNUP_VERIFICATION:
            self._send_activation_email(user)
        else:
            user.is_active = True
            user.full_clean()
            user.save()
        logger.info(f"New user with id: {user.pk} has been created")
        return redirect("success-signup")


class UserSignUpSuccess(TemplateView):
    template_name = "accounts/success-registration.html"
    extra_context = {"MESSAGES": SuccessInfoAfterRegistrationText}


@method_decorator(login_required, name="dispatch")
@method_decorator(check_permissions(allowed_user_types=[CustomUser.UserType.ADMIN.name]), name="dispatch")
class UserCreate(CreateView):
    template_name = "user_create.html"
    form_class = CustomUserCreationForm

    def get_success_url(self) -> str:
        return reverse("custom-users-list")


@method_decorator(login_required, name="dispatch")
@method_decorator(
    check_permissions(
        allowed_user_types=[
            CustomUser.UserType.EMPLOYEE.name,
            CustomUser.UserType.MANAGER.name,
            CustomUser.UserType.ADMIN.name,
        ]
    ),
    name="dispatch",
)
class UserUpdate(UpdateView):
    template_name = "user_update.html"
    form_class = SimpleUserChangeForm
    admins_form_class = AdminUserChangeForm
    model = CustomUser

    def get_object(self, queryset: Optional[QuerySet] = None) -> CustomUser:
        return self.request.user

    def get_form_class(self) -> Type[ModelForm]:
        if self.request.user.user_type == CustomUser.UserType.ADMIN.name:
            return self.admins_form_class
        return self.form_class

    def get_success_url(self) -> str:
        return reverse("custom-user-update")

    def form_valid(self, form: SimpleUserChangeForm) -> HttpResponse:
        super().form_valid(form)
        messages.success(self.request, ConfirmationMessages.SUCCESSFUL_UPDATE_USER_MESSAGE)
        return redirect(self.get_success_url())


@method_decorator(login_required, name="dispatch")
@method_decorator(check_permissions(allowed_user_types=[CustomUser.UserType.ADMIN.name]), name="dispatch")
class UserUpdateByAdmin(UpdateView):
    template_name = "users_detail.html"
    form_class = AdminUserChangeForm
    context_object_name = "user_detail"
    model = CustomUser

    def get_success_url(self) -> str:
        return reverse("custom-user-update-by-admin", kwargs={"pk": self.object.pk})

    def form_valid(self, form: SimpleUserChangeForm) -> HttpResponse:
        super().form_valid(form)
        logger.info(f"User with id: {self.object.pk} has been updated by admin with id {self.request.user.pk}")
        messages.success(self.request, ConfirmationMessages.SUCCESSFUL_UPDATE_USER_MESSAGE)
        return redirect(self.get_success_url())


@method_decorator(login_required, name="dispatch")
@method_decorator(check_permissions(allowed_user_types=[CustomUser.UserType.ADMIN.name]), name="dispatch")
class UserList(ListView):
    template_name = "users_list.html"
    model = CustomUser
    queryset = CustomUser.objects.prefetch_related("projects")

    def get_context_data(self, *, _object_list: Any = None, **kwargs: Any) -> dict:
        context_data = super().get_context_data(**kwargs)
        context_data["year"] = datetime.datetime.now().year
        context_data["month"] = datetime.datetime.now().month
        return context_data


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


class ActivateAccountView(TemplateView):
    extra_context = {"MESSAGES": AccountConfirmationText}
    template_name = "account_confirmation/confirmation.html"

    def activate(self) -> bool:
        try:
            user_id = force_str(urlsafe_base64_decode(self.kwargs["encoded_user_id"]))
            user = CustomUser.objects.get(pk=user_id)
            is_token_correct = account_activation_token.check_token(user, self.kwargs["token"])
            if is_token_correct:
                user.is_active = True
                user.full_clean()
                user.save()
                return True
            else:
                return False
        except CustomUser.DoesNotExist:
            return False

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)
        context["is_activated"] = self.activate()
        return context


@method_decorator(login_required, name="dispatch")
@method_decorator(
    check_permissions(allowed_user_types=[CustomUser.UserType.ADMIN.name, CustomUser.UserType.MANAGER.name]),
    name="dispatch",
)
class NotificationUserListView(ListView):
    template_name = "user_notifications_list.html"
    model = CustomUser

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(
                is_active=True,
                projects__suspended=False,
                projects__stop_date__isnull=True,
                projects__managers__pk=self.request.user.pk,
                projects__is_notification_enabled=True,
            )
            .annotate(last_report_date=Coalesce(Max("report__date"), datetime.date.today()))
            .annotate(days_without_report=datetime.date.today() - F("last_report_date"))
            .order_by("-last_report_date")
            .distinct()
        )

    def get_context_data(self, *, _object_list: Any = None, **kwargs: Any) -> dict:
        context_data = super().get_context_data(**kwargs)
        users_days_without_report_dict = {}
        for user in context_data["object_list"]:
            no_report_days = count_workdays(user.last_report_date, user.days_without_report)
            if no_report_days > 0:
                users_days_without_report_dict[user.email] = no_report_days

        context_data["users_days_without_report"] = users_days_without_report_dict
        context_data["UI_text"] = UserNotificationsText
        return context_data
