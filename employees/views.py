import datetime
from typing import Any
from typing import Dict
from typing import Union

from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.http.response import HttpResponseRedirectBase
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from rest_framework import permissions
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from employees.common.strings import AuthorReportListStrings
from employees.common.strings import ReportDetailStrings
from employees.common.strings import ReportListStrings
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
    project_form = ""
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self) -> QuerySet:
        return Report.objects.filter(author=self.request.user).order_by("-date", "project__name")

    def _add_project(self, serializer: ReportSerializer, project: Project) -> None:
        project.members.add(self.request.user)
        project.full_clean()
        project.save()
        serializer.fields["project"].initial = project

    def _create_serializer(self) -> ReportSerializer:
        reports_serializer = ReportSerializer(context={"request": self.request})
        reports_serializer.fields["project"].queryset = Project.objects.filter(
            members__id=self.request.user.id
        ).order_by("name")
        reports_serializer.fields["task_activities"].queryset = TaskActivityType.objects.order_by("name")
        reports_serializer.fields["date"].initial = str(datetime.datetime.now().date())
        return reports_serializer

    def initial(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        super().initial(request, *args, **kwargs)
        self.reports_dict = query_as_dict(self.get_queryset())
        self.project_form = ProjectJoinForm(
            queryset=Project.objects.exclude(members__id=self.request.user.id).order_by("name")
        )

    def get(self, _request: HttpRequest) -> Response:
        return Response(
            {
                "serializer": self._create_serializer(),
                "reports_dict": self.reports_dict,
                "UI_text": ReportListStrings,
                "project_form": self.project_form,
            }
        )

    def post(self, request: HttpRequest) -> Response:
        reports_serializer = ReportSerializer(data=request.data, context={"request": request})
        if "join" in request.POST:
            project_id = request.POST["projects"]
            project = Project.objects.get(id=int(project_id))
            self._add_project(serializer=reports_serializer, project=project)
            self.project_form = ProjectJoinForm(
                queryset=Project.objects.exclude(members__id=self.request.user.id).order_by("name")
            )
            reports_serializer = self._create_serializer()
            reports_serializer.fields["project"].initial = project
            return Response(
                {
                    "serializer": reports_serializer,
                    "reports_dict": self.reports_dict,
                    "UI_text": ReportListStrings,
                    "project_form": self.project_form,
                }
            )

        elif not reports_serializer.is_valid():
            return Response(
                {
                    "serializer": reports_serializer,
                    "reports_dict": self.reports_dict,
                    "errors": reports_serializer.errors,
                    "UI_text": ReportListStrings,
                    "project_form": self.project_form,
                }
            )
        reports_serializer.save(author=self.request.user)
        return Response(
            {
                "serializer": self._create_serializer(),
                "reports_dict": query_as_dict(self.get_queryset()),
                "UI_text": ReportListStrings,
                "project_form": self.project_form,
            },
            status=201,
        )


class ReportDetail(APIView):
    serializer_class = ReportSerializer
    model_class = Report
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = "employees/report_detail.html"
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


class AuthorReportList(APIView):
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = "employees/author_report_list.html"
    user_interface_text = AuthorReportListStrings
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self, pk):
        return Report.objects.filter(author=pk).order_by("-date", "project__name")

    def get(self, _request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        queryset = self.get_queryset(user.pk)
        reports_dict = query_as_dict(queryset)
        return Response({"user_name": user.email, "reports_dict": reports_dict, "UI_text": self.user_interface_text})
