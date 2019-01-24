import datetime
from typing import Any
from typing import Dict
from typing import Union

from django.contrib.auth.decorators import login_required
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.http.response import HttpResponseRedirectBase
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import reverse
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from django.views.generic import UpdateView
from rest_framework import permissions
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from employees.common.strings import AdminReportDetailStrings
from employees.common.strings import AuthorReportListStrings
from employees.common.strings import ProjectReportListStrings
from employees.common.strings import ReportDetailStrings
from employees.common.strings import ReportListStrings
from employees.forms import AdminReportForm
from employees.forms import ProjectJoinForm
from employees.models import Report
from employees.models import TaskActivityType
from employees.serializers import ReportSerializer
from managers.models import Project
from users.models import CustomUser


class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self) -> QuerySet:
        return Report.objects.filter(author=self.request.user).order_by("-date")

    def perform_create(self, serializer: ReportSerializer) -> None:
        serializer.save(author=self.request.user)


def query_as_dict(query_set: QuerySet) -> Dict[str, Any]:
    dictionary = {}  # type: Dict[str, Any]
    for record in query_set:
        key = record.date
        dictionary.setdefault(key, [])
        dictionary[key].append(record)
    return dictionary


class ReportList(APIView):
    serializer_class = ReportSerializer
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = "employees/report_list.html"
    reports_dict = {}  # type: Dict[str, Any]
    permission_classes = (permissions.IsAuthenticated,)
    hide_join = False

    def get_queryset(self) -> QuerySet:
        return Report.objects.filter(author=self.request.user).order_by("-date", "project__name")

    def _add_project(self, project: Project) -> None:
        project.members.add(self.request.user)
        project.full_clean()
        project.save()

    def _create_serializer(self) -> ReportSerializer:
        reports_serializer = ReportSerializer(context={"request": self.request})
        reports_serializer.fields["project"].queryset = Project.objects.filter(
            members__id=self.request.user.id
        ).order_by("name")
        reports_serializer.fields["task_activities"].queryset = TaskActivityType.objects.order_by("name")
        reports_serializer.fields["date"].initial = str(datetime.datetime.now().date())
        return reports_serializer

    def _create_project_join_form(self) -> ProjectJoinForm:
        project_form_queryset = Project.objects.exclude(members__id=self.request.user.id).order_by("name")
        self.hide_join = not project_form_queryset.exists()
        return ProjectJoinForm(queryset=project_form_queryset)

    def initial(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        super().initial(request, *args, **kwargs)
        self.reports_dict = query_as_dict(self.get_queryset())

    def get(self, _request: HttpRequest) -> Response:
        return Response(
            {
                "serializer": self._create_serializer(),
                "reports_dict": self.reports_dict,
                "UI_text": ReportListStrings,
                "project_form": self._create_project_join_form(),
                "hide_join": self.hide_join,
            }
        )

    def post(self, request: HttpRequest) -> Response:
        reports_serializer = ReportSerializer(data=request.data, context={"request": request})
        if "join" in request.POST:
            if "projects" in request.POST.keys():
                project_id = request.POST["projects"]
                project = Project.objects.get(id=int(project_id))
                self._add_project(project=project)
                reports_serializer = self._create_serializer()
                reports_serializer.fields["project"].initial = project
            else:
                reports_serializer = self._create_serializer()
            return Response(
                {
                    "serializer": reports_serializer,
                    "reports_dict": self.reports_dict,
                    "UI_text": ReportListStrings,
                    "project_form": self._create_project_join_form(),
                    "hide_join": self.hide_join,
                }
            )

        elif not reports_serializer.is_valid():
            return Response(
                {
                    "serializer": reports_serializer,
                    "reports_dict": self.reports_dict,
                    "errors": reports_serializer.errors,
                    "UI_text": ReportListStrings,
                    "project_form": self._create_project_join_form(),
                    "hide_join": self.hide_join,
                }
            )
        reports_serializer.save(author=self.request.user)
        return Response(
            {
                "serializer": self._create_serializer(),
                "reports_dict": query_as_dict(self.get_queryset()),
                "UI_text": ReportListStrings,
                "project_form": self._create_project_join_form(),
                "hide_join": self.hide_join,
            },
            status=201,
        )


class ReportDetail(APIView):
    serializer_class = ReportSerializer
    model_class = Report
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = "employees/report_detail.html"
    user_interface_text = ReportDetailStrings
    permission_classes = (permissions.IsAuthenticated,)

    def _create_serializer(self, report: Report, data: Any = None) -> ReportSerializer:
        if data is None:
            reports_serializer = self.serializer_class(report, context={"request": self.request})
        else:
            reports_serializer = self.serializer_class(report, data=data, context={"request": self.request})
        reports_serializer.fields["project"].queryset = Project.objects.filter(members__id=report.author.pk).order_by(
            "name"
        )
        return reports_serializer

    def get(self, _request: HttpRequest, pk: int) -> Response:
        report = get_object_or_404(self.model_class, pk=pk)
        serializer = self._create_serializer(report)
        return Response({"serializer": serializer, "report": report, "UI_text": ReportDetailStrings})

    def post(self, request: HttpRequest, pk: int) -> Union[Response, HttpResponseRedirectBase]:
        if "discard" not in request.POST:
            report = get_object_or_404(self.model_class, pk=pk)
            serializer = self._create_serializer(report, request.data)
            if not serializer.is_valid():
                return Response(
                    {
                        "serializer": serializer,
                        "report": report,
                        "errors": serializer.errors,
                        "UI_text": ReportDetailStrings,
                    }
                )
            serializer.save()
        return redirect("custom-report-list")


def delete_report(_request: HttpRequest, pk: int) -> HttpResponseRedirectBase:
    report = get_object_or_404(Report, pk=pk)
    report.delete()

    return redirect("custom-report-list")


@method_decorator(login_required, name="dispatch")
class AuthorReportView(DetailView):
    template_name = "employees/author_report_list.html"
    model = CustomUser
    queryset = CustomUser.objects.prefetch_related("report_set")

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)
        context["UI_text"] = AuthorReportListStrings
        return context


@method_decorator(login_required, name="dispatch")
class AdminReportView(UpdateView):
    template_name = "employees/admin_report_detail.html"
    form_class = AdminReportForm
    model = Report

    def get_context_data(self, **kwargs: Any) -> dict:
        context_data = super().get_context_data(**kwargs)
        context_data["UI_text"] = AdminReportDetailStrings
        return context_data

    def get_success_url(self) -> str:
        return reverse("author-report-list", kwargs={"pk": self.object.author.id})

    def form_valid(self, form: AdminReportForm) -> HttpResponseRedirectBase:
        self.object = form.save(commit=False)  # pylint: disable=attribute-defined-outside-init
        self.object.editable = True
        self.object.save()
        return super().form_valid(form)


class ProjectReportList(APIView):
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = "employees/project_report_list.html"
    user_interface_text = ProjectReportListStrings
    permission_classes = (permissions.IsAuthenticated,)

    @classmethod
    def get_queryset(cls, pk: int) -> QuerySet:
        return Report.objects.filter(project=pk).order_by("-date")

    def get(self, _request: HttpRequest, pk: int) -> Response:
        project = get_object_or_404(Project, pk=pk)
        queryset = self.get_queryset(project.pk)
        reports_dict = query_as_dict(queryset)
        return Response(
            {"project_name": project.name, "reports_dict": reports_dict, "UI_text": self.user_interface_text}
        )
