import datetime
import logging
from typing import Any
from typing import Union

from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.db.models.query import Prefetch
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.http.response import HttpResponseRedirectBase
from django.shortcuts import redirect
from django.shortcuts import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import UpdateView
from django.views.generic.base import ContextMixin

from employees.common.constants import MONTH_NAVIGATION_FORM_MAX_MONTH_VALUE
from employees.common.constants import MONTH_NAVIGATION_FORM_MAX_YEAR_VALUE
from employees.common.constants import MONTH_NAVIGATION_FORM_MIN_MONTH_VALUE
from employees.common.constants import MONTH_NAVIGATION_FORM_MIN_YEAR_VALUE
from employees.common.constants import ExcelGeneratorSettingsConstants
from employees.common.exports import generate_xlsx_for_project
from employees.common.exports import generate_xlsx_for_single_user
from employees.common.strings import AuthorReportListStrings
from employees.common.strings import MonthNavigationText
from employees.common.strings import ProjectReportDetailStrings
from employees.common.strings import ProjectReportListStrings
from employees.common.strings import ReportDetailStrings
from employees.common.strings import ReportListStrings
from employees.forms import MonthSwitchForm
from employees.forms import ProjectJoinForm
from employees.forms import ReportForm
from employees.models import Report
from managers.models import Project
from users.models import CustomUser
from utils.decorators import check_permissions
from utils.mixins import ProjectsWorkPercentageMixin
from utils.mixins import UserIsAuthorOfCurrentReportMixin
from utils.mixins import UserIsManagerOfCurrentProjectMixin
from utils.mixins import UserIsManagerOfCurrentReportProjectOrAuthorOfCurrentReportMixin

logger = logging.getLogger(__name__)


class MonthNavigationMixin(ContextMixin):
    url_name = ""
    kwargs = {}  # type: dict

    def _get_url_from_date(self, date: datetime.date, pk: int = None) -> str:
        url_kwargs = {"year": date.year, "month": date.month}
        if pk is not None:
            url_kwargs["pk"] = pk
        return reverse(self.url_name, kwargs=url_kwargs)

    def _get_previous_month_url(self, year: int, month: int, pk: int) -> str:
        date = datetime.date(year=year, month=month, day=1) + relativedelta(months=-1)
        return self._get_url_from_date(date, pk)

    def _get_next_month_url(self, year: int, month: int, pk: int) -> str:
        date = datetime.date(year=year, month=month, day=1) + relativedelta(months=+1)
        return self._get_url_from_date(date, pk)

    def _get_recent_month_url(self, pk: int) -> str:
        date = datetime.datetime.now().date()
        return self._get_url_from_date(date, pk)

    @staticmethod
    def _get_title_date(year: int, month: int) -> str:
        date = datetime.date(year=year, month=month, day=1)
        return date.strftime("%m/%y")

    def _date_out_of_bounds(self) -> bool:
        year_too_old = int(self.kwargs["year"]) < MONTH_NAVIGATION_FORM_MIN_YEAR_VALUE
        date_too_old = (
            int(self.kwargs["month"]) < MONTH_NAVIGATION_FORM_MIN_MONTH_VALUE
            and int(self.kwargs["year"]) == MONTH_NAVIGATION_FORM_MIN_YEAR_VALUE
        )
        year_too_far = int(self.kwargs["year"]) > MONTH_NAVIGATION_FORM_MAX_YEAR_VALUE
        date_too_far = (
            int(self.kwargs["month"]) > MONTH_NAVIGATION_FORM_MAX_MONTH_VALUE
            and int(self.kwargs["year"]) == MONTH_NAVIGATION_FORM_MAX_YEAR_VALUE
        )
        return year_too_old or date_too_old or year_too_far or date_too_far

    def _get_month_navigator_params(self) -> dict:
        disable_next_button = False
        disable_previous_button = False
        year = int(self.kwargs["year"])
        month = int(self.kwargs["month"])
        pk = self.kwargs.get("pk", None)

        if month == MONTH_NAVIGATION_FORM_MAX_MONTH_VALUE and year == MONTH_NAVIGATION_FORM_MAX_YEAR_VALUE:
            disable_next_button = True
        elif month == MONTH_NAVIGATION_FORM_MIN_MONTH_VALUE and year == MONTH_NAVIGATION_FORM_MIN_YEAR_VALUE:
            disable_previous_button = True

        return {
            "path": self.request.path,
            "navigation_text": MonthNavigationText,
            "month_form": MonthSwitchForm(initial_date=datetime.date(year=year, month=month, day=1)),
            "next_month_url": self._get_next_month_url(year, month, pk),
            "recent_month_url": self._get_recent_month_url(pk),
            "previous_month_url": self._get_previous_month_url(year, month, pk),
            "disable_next_button": disable_next_button,
            "disable_previous_button": disable_previous_button,
            "title_date": self._get_title_date(year, month),
        }

    def get_context_data(self, **kwargs: Any) -> dict:
        context_data = super().get_context_data(**kwargs)
        context_data.update(self._get_month_navigator_params())
        return context_data

    def redirect_to_another_month(self, request: HttpRequest) -> HttpResponseRedirectBase:
        post_data = request.POST.copy()
        post_data["date"] = datetime.datetime.strptime(post_data["date"], "%m-%Y")
        form = MonthSwitchForm(data=post_data)
        if form.is_valid():
            redirect_kwargs = {"year": post_data["date"].year, "month": post_data["date"].month}
            if self.kwargs.get("pk", None) is not None:
                redirect_kwargs["pk"] = self.kwargs["pk"]
            return redirect(reverse(self.url_name, kwargs=redirect_kwargs))
        else:
            return redirect(request.path)

    def redirect_to_current_month(self) -> HttpResponseRedirectBase:
        pk = self.kwargs.get("pk", None)
        if pk is not None:
            pk = int(pk)
        return redirect(self._get_recent_month_url(pk))


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
class ReportListCreateProjectJoinView(MonthNavigationMixin, ProjectsWorkPercentageMixin, CreateView):
    template_name = "employees/report_list.html"
    project_join_form = ProjectJoinForm
    model = Report
    form_class = ReportForm
    url_name = "custom-report-list"
    object = None

    def get_initial(self) -> dict:
        initial = super().get_initial()
        initial.update({"date": timezone.now(), "author": self.request.user})
        return initial

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(author=self.request.user, date__year=self.kwargs["year"], date__month=self.kwargs["month"])
            .order_by("-date", "project__name", "-creation_date")
        )

    def get_context_data(self, **kwargs: Any) -> dict:
        context_data = super().get_context_data(**kwargs)
        context_data["UI_text"] = ReportListStrings
        context_data["object_list"] = self.get_queryset()
        context_data["daily_hours_sum"] = context_data["object_list"].order_by().get_work_hours_sum_for_all_dates()
        context_data["monthly_hours_sum"] = context_data["object_list"].order_by().get_work_hours_sum_for_all_authors()
        project_form_queryset = Project.objects.exclude(members__id=self.request.user.id).order_by("name")
        context_data["hide_join"] = not project_form_queryset.exists()
        context_data["project_form"] = ProjectJoinForm(queryset=project_form_queryset)
        return context_data

    def get_success_url(self) -> str:
        return reverse("custom-report-list", kwargs={"year": self.kwargs["year"], "month": self.kwargs["month"]})

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if "join" in request.POST:
            return self._handle_join_request(request)
        elif "month-switch" in request.POST:
            return self.redirect_to_another_month(request)
        return super().post(request, *args, **kwargs)

    def _handle_join_request(self, request: HttpRequest) -> HttpResponse:
        form = ProjectJoinForm(
            queryset=Project.objects.exclude(members__id=self.request.user.id).order_by("name"), data=request.POST
        )
        if form.is_valid():
            project = Project.objects.get(id=int(self.request.POST["projects"]))
            project.members.add(request.user)
            project.full_clean()
            project.save()
            logger.debug(f"User with id: {request.user.pk} join to the project with id: {project.pk}")
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(context={"form": form})


class ReportDetailBase(UpdateView):
    form_class = ReportForm
    model = Report
    template_name = "employees/project_report_detail.html"
    template_post_url = ""
    redirect_url = ""
    url_pk = ""

    def get_initial(self) -> dict:
        initial = super().get_initial()
        initial.update({"author": self.request.user})
        return initial

    def get_context_data(self, **kwargs: Any) -> dict:
        context_data = super().get_context_data(**kwargs)
        context_data["UI_text"] = ProjectReportDetailStrings
        context_data["post_url"] = self.template_post_url
        context_data["discard_url"] = self.redirect_url
        context_data["url_pk"] = getattr(self.object, self.url_pk).pk
        return context_data

    def get_success_url(self) -> str:
        return reverse(
            self.redirect_url,
            kwargs={
                "pk": getattr(self.object, self.url_pk).id,
                "year": self.object.date.year,
                "month": self.object.date.month,
            },
        )

    def form_valid(self, form: ReportForm) -> HttpResponseRedirectBase:
        self.object = form.save(commit=False)  # pylint: disable=attribute-defined-outside-init
        self.object.editable = True
        self.object.save()
        return super().form_valid(form)


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
class ReportDetailView(
    UserIsManagerOfCurrentReportProjectOrAuthorOfCurrentReportMixin, UserIsAuthorOfCurrentReportMixin, UpdateView
):
    template_name = "employees/report_detail.html"
    form_class = ReportForm
    model = Report

    def get_initial(self) -> dict:
        initial = super().get_initial()
        initial.update({"author": self.request.user})
        return initial

    def get_context_data(self, **kwargs: Any) -> dict:
        context_data = super().get_context_data(**kwargs)
        context_data["UI_text"] = ReportDetailStrings
        return context_data

    def get_success_url(self) -> str:
        return reverse("custom-report-list", kwargs={"year": self.object.date.year, "month": self.object.date.month})

    def form_valid(self, form: ReportForm) -> HttpResponseRedirectBase:
        instance = form.save(commit=False)
        instance.editable = True
        instance.save()
        return super().form_valid(form)


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
class ReportDeleteView(
    UserIsAuthorOfCurrentReportMixin, UserIsManagerOfCurrentReportProjectOrAuthorOfCurrentReportMixin, DeleteView
):
    model = Report

    def get_success_url(self) -> str:
        logger.debug(f"Report with id: {self.kwargs['pk']} has been deleted")
        return reverse("custom-report-list", kwargs={"year": self.object.date.year, "month": self.object.date.month})


@method_decorator(login_required, name="dispatch")
@method_decorator(check_permissions(allowed_user_types=[CustomUser.UserType.ADMIN.name]), name="dispatch")
class AuthorReportView(MonthNavigationMixin, ProjectsWorkPercentageMixin, DetailView):
    template_name = "employees/author_report_list.html"
    model = CustomUser
    url_name = "author-report-list"

    def get_queryset(self) -> QuerySet:
        return CustomUser.objects.prefetch_related(
            Prefetch(
                "report_set",
                queryset=Report.objects.filter(date__year=self.kwargs["year"], date__month=self.kwargs["month"]),
            )
        )

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)
        context["UI_text"] = AuthorReportListStrings
        context["daily_hours_sum"] = self.object.report_set.get_work_hours_sum_for_all_dates()
        context["monthly_hours_sum"] = self.object.report_set.get_work_hours_sum_for_all_authors()
        return context

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Union[HttpResponse, HttpResponseRedirectBase]:
        if self._date_out_of_bounds():
            return self.redirect_to_current_month()
        return super().get(request, *args, **kwargs)

    def post(  # pylint: disable=unused-argument
        self, request: HttpRequest, pk: int, year: int, month: int
    ) -> HttpResponseRedirectBase:
        return self.redirect_to_another_month(request)


@method_decorator(login_required, name="dispatch")
@method_decorator(check_permissions(allowed_user_types=[CustomUser.UserType.ADMIN.name]), name="dispatch")
class AdminReportView(ReportDetailBase):
    template_post_url = "admin-report-detail"
    redirect_url = "author-report-list"
    url_pk = "author"


@method_decorator(login_required, name="dispatch")
@method_decorator(
    check_permissions(allowed_user_types=[CustomUser.UserType.MANAGER.name, CustomUser.UserType.ADMIN.name]),
    name="dispatch",
)
class ProjectReportList(UserIsManagerOfCurrentProjectMixin, DetailView, MonthNavigationMixin):
    template_name = "employees/project_report_list.html"
    model = Project
    url_name = "project-report-list"

    def get_queryset(self) -> QuerySet:
        return Project.objects.prefetch_related(
            Prefetch(
                "report_set",
                queryset=Report.objects.filter(date__year=self.kwargs["year"], date__month=self.kwargs["month"]),
            )
        )

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)
        context["UI_text"] = ProjectReportListStrings
        context["monthly_hours_sum"] = self.object.report_set.get_work_hours_sum_for_all_authors()
        return context

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Union[HttpResponse, HttpResponseRedirectBase]:
        if self._date_out_of_bounds():
            return self.redirect_to_current_month()
        return super().get(request, *args, **kwargs)

    def post(  # pylint: disable=unused-argument
        self, request: HttpRequest, pk: int, year: int, month: int
    ) -> HttpResponseRedirectBase:
        return self.redirect_to_another_month(request)


@method_decorator(login_required, name="dispatch")
@method_decorator(
    check_permissions(allowed_user_types=[CustomUser.UserType.MANAGER.name, CustomUser.UserType.ADMIN.name]),
    name="dispatch",
)
class ProjectReportDetail(UserIsManagerOfCurrentReportProjectOrAuthorOfCurrentReportMixin, ReportDetailBase):
    template_post_url = "project-report-detail"
    redirect_url = "project-report-list"
    url_pk = "project"


@method_decorator(login_required, name="dispatch")
@method_decorator(
    check_permissions(
        allowed_user_types=[
            CustomUser.UserType.ADMIN.name,
            CustomUser.UserType.MANAGER.name,
            CustomUser.UserType.EMPLOYEE.name,
        ]
    ),
    name="dispatch",
)
class ExportUserReportView(DetailView):
    model = CustomUser

    def get_queryset(self) -> QuerySet:
        return CustomUser.objects.prefetch_related(
            Prefetch(
                "report_set",
                queryset=Report.objects.filter(date__year=self.kwargs["year"], date__month=self.kwargs["month"]),
            )
        )

    def render_to_response(self, context: dict, **response_kwargs: Any) -> HttpResponse:
        if self.request.user.is_admin:
            author = super().get_object()
        else:
            author = self.get_queryset().get(pk=self.request.user.pk)
        response = HttpResponse(content_type=ExcelGeneratorSettingsConstants.CONTENT_TYPE_FORMAT.value)
        response["Content-Disposition"] = ExcelGeneratorSettingsConstants.EXPORTED_FILE_NAME.value.format(
            author.email, datetime.date.today()
        )
        work_book = generate_xlsx_for_single_user(author)
        work_book.save(response)
        return response


@method_decorator(login_required, name="dispatch")
@method_decorator(
    check_permissions(allowed_user_types=[CustomUser.UserType.ADMIN.name, CustomUser.UserType.MANAGER.name]),
    name="dispatch",
)
class ExportReportsInProjectView(UserIsManagerOfCurrentProjectMixin, DetailView):
    model = Project

    def get_queryset(self) -> QuerySet:
        return Project.objects.prefetch_related(
            Prefetch(
                "report_set",
                queryset=Report.objects.filter(date__year=self.kwargs["year"], date__month=self.kwargs["month"]),
            )
        )

    def render_to_response(self, context: dict, **response_kwargs: Any) -> HttpResponse:
        project = super().get_object()
        response = HttpResponse(content_type=ExcelGeneratorSettingsConstants.CONTENT_TYPE_FORMAT.value)
        response["Content-Disposition"] = ExcelGeneratorSettingsConstants.EXPORTED_FILE_NAME.value.format(
            project.name, datetime.date.today()
        )
        work_book = generate_xlsx_for_project(project)
        work_book.save(response)
        return response
