from typing import Any
from typing import Type
from typing import Union

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import Lower
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView
from rest_framework import renderers
from rest_framework import viewsets

from managers.forms import ProjectAdminForm
from managers.forms import ProjectManagerForm
from managers.models import Project
from managers.serializers import ProjectSerializer
from users.models import CustomUser


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by(Lower("name"))
    serializer_class = ProjectSerializer


@method_decorator(login_required, name="dispatch")
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


@method_decorator(login_required, name="dispatch")
class ProjectDetailView(DetailView):
    template_name = "managers/project_detail.html"
    model = Project


@method_decorator(login_required, name="dispatch")
class ProjectCreateView(CreateView):
    extra_context = {"button_text": _("Create"), "title": _("Create new project")}
    form_class = ProjectAdminForm
    model = Project
    template_name = "managers/project_form.html"

    def get_context_data(self, **kwargs: Any) -> dict:
        context_data = super().get_context_data(**kwargs)
        context_data["back_url"] = self.get_success_url()
        return context_data

    def get_success_url(self) -> str:  # pylint: disable=no-self-use
        return reverse("custom-projects-list")


@method_decorator(login_required, name="dispatch")
class ProjectUpdateView(UpdateView):
    extra_context = {"button_text": _("Update")}
    form_class = ProjectManagerForm
    model = Project
    template_name = "managers/project_form.html"

    def get_context_data(self, **kwargs: Any) -> dict:
        context_data = super().get_context_data(**kwargs)
        context_data["title"] = self.object.name
        context_data["back_url"] = self.get_success_url()
        return context_data

    def get_success_url(self) -> str:
        return reverse("custom-project-detail", kwargs={"pk": self.kwargs["pk"]})

    def get_form_class(self) -> Union[Type[ProjectAdminForm], Type[ProjectManagerForm]]:
        if self.request.user.is_admin:
            return ProjectAdminForm
        return self.form_class


@method_decorator(login_required, name="dispatch")
class ProjectDeleteView(DeleteView):
    model = Project

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_admin:
            return redirect(reverse("home"))

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return reverse("custom-projects-list")
