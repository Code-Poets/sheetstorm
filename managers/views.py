import logging
from typing import Any
from typing import Type
from typing import Union

from django.contrib.auth.decorators import login_required
from django.db.models import Count
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
from django.views.generic.edit import ModelFormMixin

from managers.forms import ProjectAdminForm
from managers.forms import ProjectManagerForm
from managers.models import Project
from users.models import CustomUser
from utils.decorators import check_permissions

logger = logging.getLogger(__name__)


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by(Lower("name"))
    serializer_class = ProjectSerializer


@method_decorator(login_required, name="dispatch")
@method_decorator(
    check_permissions(allowed_user_types=[CustomUser.UserType.ADMIN.name, CustomUser.UserType.MANAGER.name]),
    name="dispatch",
)
class ProjectsListView(ListView):
    template_name = "managers/projects_list.html"
    allowed_sort_values = [
        "name",
        "-name",
        "start_date",
        "-start_date",
        "stop_date",
        "-stop_date",
        "members_count",
        "-members_count",
    ]
    queryset = Project.objects.all()

    def get_queryset(self) -> QuerySet:
        logger.debug(f"Get project query set for user with id: {self.request.user.pk}")
        if self.request.user.user_type == CustomUser.UserType.ADMIN.name:
            projects_queryset = self.queryset
        elif self.request.user.user_type == CustomUser.UserType.MANAGER.name:
            projects_queryset = self.queryset.filter(managers__id=self.request.user.pk)
        else:
            assert False

        if self.request.GET.get("sort") in self.allowed_sort_values:
            if "members_count" in self.request.GET.get("sort"):
                projects_queryset = projects_queryset.annotate(members_count=Count("members", distinct=True))
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
        logger.info(f"User with id: {self.request.user.pk} is in project create view")
        context_data = super().get_context_data(**kwargs)
        context_data["back_url"] = self.get_success_url()
        return context_data

    def get_success_url(self) -> str:  # pylint: disable=no-self-use
        return reverse("custom-projects-list")

    def form_valid(self, form: ProjectForm) -> HttpRequest:
        project = form.save()
        logger.info(f"New project with id: {project.pk} has been created")
        return super(ModelFormMixin, self).form_valid(form) # pylint: disable=bad-super-call


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
        logger.info(
            f"User with id: {self.request.user.pk} is in ProjectUpdate view for project with id: {self.kwargs['pk']}"
        )
        return reverse("custom-project-detail", kwargs={"pk": self.kwargs["pk"]})

    def get_form_class(self) -> Union[Type[ProjectAdminForm], Type[ProjectManagerForm]]:
        if self.request.user.is_admin:
            return ProjectAdminForm
        return self.form_class

    def form_valid(self, form: ProjectAdminForm) -> HttpRequest:
        project = form.save()
        logger.info(f"Project with id: {project.pk} has been updated by user with id: {self.request.user.pk}")
        return super(ModelFormMixin, self).form_valid(form)  # pylint: disable=bad-super-call


@method_decorator(login_required, name="dispatch")
class ProjectDeleteView(DeleteView):
    model = Project

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_admin:
            return redirect(reverse("home"))

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return reverse("custom-projects-list")
