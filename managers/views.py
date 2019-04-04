from django.db.models import Count
from django.db.models.functions import Lower
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from managers.models import Project
from managers.serializers import ProjectSerializer
from users.models import CustomUser


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by(Lower("name"))
    serializer_class = ProjectSerializer


class ProjectsList(ListView):
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = "managers/projects_list.html"

    def get_queryset(self) -> QuerySet:
        if self.request.user.user_type == CustomUser.UserType.ADMIN.name:
            projects_queryset = Project.objects.all().order_by("id")
        elif self.request.user.user_type == CustomUser.UserType.MANAGER.name:
            projects_queryset = Project.objects.filter(managers__id=self.request.user.pk)
        else:
            projects_queryset = Project.objects.none()
        if self.request.GET.get("sort"):
            if "members" in self.request.GET.get("sort"):
                projects_queryset = Project.objects.annotate(members_count=Count("members")).order_by(
                    self.request.GET.get("sort")
                )
            else:
                projects_queryset = projects_queryset.order_by(self.request.GET.get("sort"))

        return projects_queryset


class ProjectDetail(APIView):
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = "managers/project_detail.html"

    @staticmethod
    def get(_request: HttpRequest, pk: int) -> Response:
        project = get_object_or_404(Project, pk=pk)
        return Response({"project": project})
