import logging
from typing import Any
from typing import Type
from typing import Union

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models import Q
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import RedirectView
from django.views.generic import UpdateView
from django.views.generic.edit import FormView
from django.views.generic.edit import ModelFormMixin

from employees.forms import TaskActivityForm
from employees.models import TaskActivityType
from managers.forms import ProjectAdminForm
from managers.forms import ProjectManagerForm
from managers.models import Project
from users.models import CustomUser
from utils.decorators import check_permissions
from utils.mixins import UserIsManagerOfCurrentProjectMixin

logger = logging.getLogger(__name__)


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
    model = Project

    def get_queryset(self) -> QuerySet:
        logger.debug(f"Get project query set for user with id: {self.request.user.pk}")
        if self.request.user.user_type == CustomUser.UserType.ADMIN.name:
            projects_queryset = super().get_queryset()
        elif self.request.user.user_type == CustomUser.UserType.MANAGER.name:
            projects_queryset = super().get_queryset().filter(managers__id=self.request.user.pk)
        else:
            assert False

        if self.request.GET.get("sort") in self.allowed_sort_values:
            if "members_count" in self.request.GET.get("sort"):
                projects_queryset = projects_queryset.annotate(members_count=Count("members", distinct=True))
            projects_queryset = projects_queryset.order_by(self.request.GET.get("sort"))

        return projects_queryset


@method_decorator(login_required, name="dispatch")
@method_decorator(
    check_permissions(allowed_user_types=[CustomUser.UserType.ADMIN.name, CustomUser.UserType.MANAGER.name]),
    name="dispatch",
)
class ProjectDetailView(UserIsManagerOfCurrentProjectMixin, DetailView):
    template_name = "managers/project_detail.html"
    model = Project

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)
        context["year"] = timezone.now().year
        context["month"] = timezone.now().month
        return context


@method_decorator(login_required, name="dispatch")
@method_decorator(check_permissions(allowed_user_types=[CustomUser.UserType.ADMIN.name]), name="dispatch")
class ProjectCreateView(CreateView):
    extra_context = {"button_text": _("Create"), "title": _("New project")}
    form_class = ProjectAdminForm
    model = Project
    template_name = "managers/project_form.html"

    def get_form_kwargs(self) -> dict:
        kwargs = super().get_form_kwargs()
        kwargs["user_pk"] = self.request.user.pk
        return kwargs

    def get_context_data(self, **kwargs: Any) -> dict:
        logger.info(f"User with id: {self.request.user.pk} is in project create view")
        context_data = super().get_context_data(**kwargs)
        context_data["back_url"] = self.get_success_url()
        return context_data

    def get_success_url(self) -> str:  # pylint: disable=no-self-use
        return reverse("custom-projects-list")

    def form_valid(self, form: ProjectAdminForm) -> HttpRequest:
        if self.request.user not in form.cleaned_data["managers"]:
            assert not self.request.user.is_employee
            managers_pk_list = [manager.pk for manager in form.cleaned_data["managers"]]
            managers_pk_list.append(self.request.user.pk)
            managers_queryset = CustomUser.objects.active().filter(pk__in=managers_pk_list)
            form.cleaned_data["managers"] = managers_queryset
        project = form.save()
        logger.info(f"New project with id: {project.pk} has been created")
        return super(ModelFormMixin, self).form_valid(form)  # pylint: disable=bad-super-call


@method_decorator(login_required, name="dispatch")
@method_decorator(
    check_permissions(allowed_user_types=[CustomUser.UserType.ADMIN.name, CustomUser.UserType.MANAGER.name]),
    name="dispatch",
)
class ProjectUpdateView(UserIsManagerOfCurrentProjectMixin, UpdateView):
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
@method_decorator(check_permissions(allowed_user_types=[CustomUser.UserType.ADMIN.name]), name="dispatch")
class ProjectDeleteView(DeleteView):
    model = Project

    def get_success_url(self) -> str:
        return reverse("custom-projects-list")

    def delete(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        response = super().delete(request, args, kwargs)
        logger.info(f"Project with id: {kwargs['pk']} has been deleted by user with id: {self.request.user.pk}")
        return response


@method_decorator(login_required, name="dispatch")
@method_decorator(
    check_permissions(allowed_user_types=[CustomUser.UserType.ADMIN.name, CustomUser.UserType.MANAGER.name]),
    name="dispatch",
)
class ManageTaskActivitiesInProjectView(FormView, UserIsManagerOfCurrentProjectMixin, DetailView):
    model = Project
    template_name = "managers/project_task_activities.html"
    form_class = TaskActivityForm

    def _add_task_activities_to_relation(self, list_of_task_activities: list) -> None:
        self.object.project_activities.set(
            TaskActivityType.objects.filter(Q(pk__in=list_of_task_activities) | Q(projects=self.object.pk))
        )

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data()
        context["project"] = self.object
        context["activities_not_connected"] = TaskActivityType.objects.exclude(projects=self.kwargs["pk"])
        context["task_activities"] = self.object.project_activities.all().order_by("name")
        return context

    def form_valid(self, form: TaskActivityForm) -> HttpRequest:
        task_activity = form.save()
        self.object.project_activities.add(task_activity)
        return super().form_valid(form)

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.object = self.get_object()  # pylint: disable=attribute-defined-outside-init
        if "task_activities" in request.POST:
            self._add_task_activities_to_relation(request.POST.getlist("task_activities"))
            return HttpResponseRedirect(self.get_success_url())
        return super().post(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return reverse("project-task-activities", kwargs={"pk": self.kwargs["pk"]})


@method_decorator(login_required, name="dispatch")
@method_decorator(
    check_permissions(allowed_user_types=[CustomUser.UserType.ADMIN.name, CustomUser.UserType.MANAGER.name]),
    name="dispatch",
)
class RemoveTaskActivityFromProjectView(RedirectView, UserIsManagerOfCurrentProjectMixin, DetailView):
    http_method_names = ["post"]
    model = Project

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        task_activity = get_object_or_404(TaskActivityType, pk=self.kwargs["task_activity_pk"])
        self.get_object().project_activities.remove(task_activity)
        return HttpResponseRedirect(reverse("project-task-activities", kwargs={"pk": self.kwargs["pk"]}))
