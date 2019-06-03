import datetime
import logging
from typing import Any

from django.contrib.auth.decorators import login_required
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.http import QueryDict
from django.http.response import HttpResponse
from django.http.response import HttpResponseRedirectBase
from django.shortcuts import redirect
from django.shortcuts import reverse
from django.utils.decorators import method_decorator
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import UpdateView
from rest_framework import permissions
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from employees.common.constants import ExcelGeneratorSettingsConstants
from employees.common.exports import generate_xlsx_for_project
from employees.common.exports import generate_xlsx_for_single_user
from employees.common.strings import AdminReportDetailStrings
from employees.common.strings import AuthorReportListStrings
from employees.common.strings import ProjectReportDetailStrings
from employees.common.strings import ProjectReportListStrings
from employees.common.strings import ReportDetailStrings
from employees.common.strings import ReportListStrings
from employees.forms import ProjectJoinForm
from employees.forms import ReportForm
from employees.models import Report
from employees.models import TaskActivityType
from employees.serializers import ReportSerializer
from managers.models import Project
from users.models import CustomUser
from utils.decorators import check_permissions
from utils.mixins import UserIsAuthorOfCurrentReportMixin
from utils.mixins import UserIsManagerOfCurrentProjectMixin
from utils.mixins import UserIsManagerOfCurrentReportProjectMixin

logger = logging.getLogger(__name__)


class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self) -> QuerySet:
        return Report.objects.filter(author=self.request.user).order_by("-date")

    def perform_create(self, serializer: ReportSerializer) -> None:
        logger.info(f"Perform create method for user: {self.request.user}")
        serializer.save(author=self.request.user)


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
class ReportList(UserIsManagerOfCurrentReportProjectMixin, UserIsAuthorOfCurrentReportMixin, APIView):
    serializer_class = ReportSerializer
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = "employees/report_list.html"
    reports = None  # type: QuerySet
    permission_classes = (permissions.IsAuthenticated,)
    hide_join = False
    daily_hours_sum = None  # type: QuerySet
    monthly_hours_sum = None  # type: QuerySet

    def get_queryset(self) -> QuerySet:
        logger.info(f"User with id: {self.request.user.pk} get reports queryset")
        return Report.objects.filter(author=self.request.user).order_by("-date", "project__name", "-creation_date")

    def _add_project(self, project: Project) -> None:
        logger.info(f"Add project method for user with id: {self.request.user.pk} to project with id {project.pk}")
        project.members.add(self.request.user)
        project.full_clean()
        project.save()

    def _create_serializer(self, data: QueryDict = None) -> ReportSerializer:
        logger.info(f"Create serializer for user with id: {self.request.user.pk}")
        if data is not None:
            reports_serializer = ReportSerializer(data=data, context={"request": self.request})
            reports_serializer.is_valid()
        else:
            reports_serializer = ReportSerializer(context={"request": self.request})
            reports_serializer.fields["date"].initial = str(datetime.datetime.now().date())
        reports_serializer.fields["project"].queryset = Project.objects.filter(
            members__id=self.request.user.id
        ).order_by("name")
        reports_serializer.fields["task_activities"].queryset = TaskActivityType.objects.order_by("name")
        return reports_serializer

    def _create_project_join_form(self) -> ProjectJoinForm:
        project_form_queryset = Project.objects.exclude(members__id=self.request.user.id).order_by("name")
        self.hide_join = not project_form_queryset.exists()
        return ProjectJoinForm(queryset=project_form_queryset)

    def initial(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        logger.info(f"Initial method for user with id: {self.request.user.pk} in ReportList view")
        super().initial(request, *args, **kwargs)
        self.reports = self.get_queryset()
        self.daily_hours_sum = self.reports.order_by().get_work_hours_sum_for_all_dates()
        self.monthly_hours_sum = self.reports.order_by().get_work_hours_sum_for_all_authors()

    def get(self, _request: HttpRequest) -> Response:
        logger.info(f"User with id: {self.request.user.pk} get to the ReportList view")
        return Response(
            {
                "serializer": self._create_serializer(),
                "object_list": self.reports,
                "daily_hours_sum": self.daily_hours_sum,
                "monthly_hours_sum": self.monthly_hours_sum,
                "UI_text": ReportListStrings,
                "project_form": self._create_project_join_form(),
                "hide_join": self.hide_join,
            }
        )

    def post(self, request: HttpRequest) -> Response:
        logger.info(f"User with id: {request.user.pk} sent post to the ReportList view")
        reports_serializer = self._create_serializer(data=request.data)
        if "join" in request.POST:
            if "projects" in request.POST.keys():
                project_id = request.POST["projects"]
                project = Project.objects.get(id=int(project_id))
                logger.debug(f"User with id: {request.user.pk} join to the project with id: {project.pk}")
                self._add_project(project=project)
                reports_serializer = self._create_serializer()
                reports_serializer.fields["project"].initial = project
            return Response(
                {
                    "serializer": reports_serializer,
                    "object_list": self.reports,
                    "daily_hours_sum": self.daily_hours_sum,
                    "monthly_hours_sum": self.monthly_hours_sum,
                    "UI_text": ReportListStrings,
                    "project_form": self._create_project_join_form(),
                    "hide_join": self.hide_join,
                }
            )

        elif not reports_serializer.is_valid():
            logger.warning(
                f"Serializer sent by user with id: {self.request.user.pk} is not valid with those errors: {reports_serializer.errors}"
            )
            return Response(
                {
                    "serializer": reports_serializer,
                    "object_list": self.reports,
                    "errors": reports_serializer.errors,
                    "daily_hours_sum": self.daily_hours_sum,
                    "monthly_hours_sum": self.monthly_hours_sum,
                    "UI_text": ReportListStrings,
                    "project_form": self._create_project_join_form(),
                    "hide_join": self.hide_join,
                }
            )
        report = reports_serializer.save(author=self.request.user)
        logger.info(f"User with id: {self.request.user.pk} created new report with id: {report.pk}")
        return redirect("custom-report-list")


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
class ReportDetailView(UserIsManagerOfCurrentReportProjectMixin, UserIsAuthorOfCurrentReportMixin, UpdateView):
    template_name = "employees/report_detail.html"
    form_class = ReportForm
    model = Report

    def get_context_data(self, **kwargs: Any) -> dict:
        context_data = super().get_context_data(**kwargs)
        context_data["UI_text"] = ReportDetailStrings
        return context_data

    def get_success_url(self) -> str:
        return reverse("custom-report-list")

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
class ReportDeleteView(UserIsAuthorOfCurrentReportMixin, DeleteView):
    model = Report

    def get_success_url(self) -> str:
        logger.debug(f"Report with id: {self.kwargs['pk']} has been deleted")
        return reverse("custom-report-list")


@method_decorator(login_required, name="dispatch")
@method_decorator(check_permissions(allowed_user_types=[CustomUser.UserType.ADMIN.name]), name="dispatch")
class AuthorReportView(DetailView):
    template_name = "employees/author_report_list.html"
    model = CustomUser
    queryset = CustomUser.objects.prefetch_related("report_set")

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)
        context["UI_text"] = AuthorReportListStrings
        context["daily_hours_sum"] = self.object.report_set.get_work_hours_sum_for_all_dates()
        context["monthly_hours_sum"] = self.object.report_set.get_work_hours_sum_for_all_authors()
        return context


@method_decorator(login_required, name="dispatch")
@method_decorator(check_permissions(allowed_user_types=[CustomUser.UserType.ADMIN.name]), name="dispatch")
class AdminReportView(UpdateView):
    template_name = "employees/admin_report_detail.html"
    form_class = ReportForm
    model = Report

    def get_context_data(self, **kwargs: Any) -> dict:
        context_data = super().get_context_data(**kwargs)
        context_data["UI_text"] = AdminReportDetailStrings
        return context_data

    def get_success_url(self) -> str:
        return reverse("author-report-list", kwargs={"pk": self.object.author.id})

    def form_valid(self, form: ReportForm) -> HttpResponseRedirectBase:
        self.object = form.save(commit=False)  # pylint: disable=attribute-defined-outside-init
        self.object.editable = True
        self.object.save()
        return super().form_valid(form)


@method_decorator(login_required, name="dispatch")
@method_decorator(
    check_permissions(allowed_user_types=[CustomUser.UserType.MANAGER.name, CustomUser.UserType.ADMIN.name]),
    name="dispatch",
)
class ProjectReportList(UserIsManagerOfCurrentProjectMixin, DetailView):
    template_name = "employees/project_report_list.html"
    model = Project
    queryset = Project.objects.prefetch_related("report_set")

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)
        context["UI_text"] = ProjectReportListStrings
        context["monthly_hours_sum"] = self.object.report_set.get_work_hours_sum_for_all_authors()
        return context


@method_decorator(login_required, name="dispatch")
@method_decorator(
    check_permissions(allowed_user_types=[CustomUser.UserType.MANAGER.name, CustomUser.UserType.ADMIN.name]),
    name="dispatch",
)
class ProjectReportDetail(UserIsManagerOfCurrentReportProjectMixin, UpdateView):
    template_name = "employees/project_report_detail.html"
    form_class = ReportForm
    model = Report

    def get_context_data(self, **kwargs: Any) -> dict:
        context_data = super().get_context_data(**kwargs)
        context_data["UI_text"] = ProjectReportDetailStrings
        return context_data

    def get_success_url(self) -> str:
        return reverse("project-report-list", kwargs={"pk": self.object.project.id})

    def form_valid(self, form: ReportForm) -> HttpResponseRedirectBase:
        self.object = form.save(commit=False)  # pylint: disable=attribute-defined-outside-init
        self.object.editable = True
        self.object.save()
        return super().form_valid(form)


@method_decorator(login_required, name="dispatch")
@method_decorator(check_permissions(allowed_user_types=[CustomUser.UserType.ADMIN.name]), name="dispatch")
class ExportUserReportView(DetailView):
    model = CustomUser

    def render_to_response(self, context: dict, **response_kwargs: Any) -> HttpResponse:
        author = super().get_object()
        response = HttpResponse(content_type=ExcelGeneratorSettingsConstants.CONTENT_TYPE_FORMAT.value)
        response["Content-Disposition"] = ExcelGeneratorSettingsConstants.EXPORTED_FILE_NAME.value.format(
            author.email, datetime.date.today()
        )
        work_book = generate_xlsx_for_single_user(author)
        work_book.save(response)
        return response


@method_decorator(login_required, name="dispatch")
@method_decorator(check_permissions(allowed_user_types=[CustomUser.UserType.ADMIN.name]), name="dispatch")
class ExportReportsInProjectView(DetailView):
    model = Project

    def render_to_response(self, context: dict, **response_kwargs: Any) -> HttpResponse:
        project = super().get_object()
        response = HttpResponse(content_type=ExcelGeneratorSettingsConstants.CONTENT_TYPE_FORMAT.value)
        response["Content-Disposition"] = ExcelGeneratorSettingsConstants.EXPORTED_FILE_NAME.value.format(
            project.name, datetime.date.today()
        )
        work_book = generate_xlsx_for_project(project)
        work_book.save(response)
        return response
