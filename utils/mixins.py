from typing import Any
from typing import Dict
from typing import Tuple
from typing import Union

from django.db.models import Q
from django.db.models import QuerySet
from django.db.models import Sum
from django.utils import timezone
from django.views.generic.base import ContextMixin


class NotCallableMixin:
    do_not_call_in_templates = True


class UserIsManagerOfCurrentProjectMixin:
    def get_queryset(self) -> QuerySet:
        if self.request.user.is_manager:  # type: ignore
            return super().get_queryset().filter(managers=self.request.user.pk)  # type: ignore
        else:
            return super().get_queryset()  # type: ignore


class UserIsManagerOfCurrentReportProjectOrAuthorOfCurrentReportMixin:
    def get_queryset(self) -> QuerySet:
        if self.request.user.is_manager:  # type: ignore
            return (
                super()  # type: ignore
                .get_queryset()
                .filter(Q(project__managers=self.request.user.pk) | Q(author=self.request.user.pk))  # type: ignore
                .distinct()
            )
        else:
            return super().get_queryset()  # type: ignore


class UserIsAuthorOfCurrentReportMixin:
    def get_queryset(self) -> QuerySet:
        if self.request.user.is_employee:  # type: ignore
            return super().get_queryset().filter(author=self.request.user.pk)  # type: ignore
        else:
            return super().get_queryset()  # type: ignore


class ProjectsWorkPercentageMixin(ContextMixin):
    def get_context_data(self, **kwargs: Any) -> dict:
        from users.models import CustomUser  # pylint: disable=import-outside-toplevel

        context_data = super().get_context_data(**kwargs)

        report_set = self.object.report_set.all() if self.model is CustomUser else self.get_queryset()

        context_data["projects_work_percentage"] = self._get_projects_work_hours_and_percentage(report_set)
        return context_data

    def _get_projects_work_hours_and_percentage(self, report_set: QuerySet) -> Dict[str, Any]:
        """
        Returns dict where keys are Project names and values are lists containing total sum of work hours
        and percentage amount of work by this user.
        """
        work_hours_per_project = self._generate_hours_per_project_queryset_from_reports_queryset(report_set)
        work_hours_sum = self._get_sum_total_of_work_hours_sum_from_hours_per_project_queryset(work_hours_per_project)
        return self._get_dict_of_total_work_hours_per_project_statistics(work_hours_per_project, work_hours_sum)

    @staticmethod
    def _generate_hours_per_project_queryset_from_reports_queryset(reports_queryset: QuerySet) -> QuerySet:
        return reports_queryset.values("project__name").annotate(project_hours=Sum("work_hours"))

    @staticmethod
    def _get_sum_total_of_work_hours_sum_from_hours_per_project_queryset(
        hours_per_project_queryset: QuerySet
    ) -> timezone.timedelta:
        return hours_per_project_queryset.aggregate(Sum("project_hours"))["project_hours__sum"]

    def _get_dict_of_total_work_hours_per_project_statistics(
        self, queryset: QuerySet, work_hours_sum: timezone.timedelta
    ) -> Dict[str, Any]:
        return {
            annotation["project__name"]: (
                self._get_project_hours_sum_and_percentage(annotation["project_hours"], work_hours_sum)
            )
            for annotation in queryset
        }

    @staticmethod
    def _get_project_hours_sum_and_percentage(
        project_hours: timezone.timedelta, all_hours: timezone.timedelta
    ) -> Union[Tuple[timezone.timedelta, float], int]:
        return (project_hours, (project_hours / all_hours) * 100) if all_hours.total_seconds() > 0 else 0
