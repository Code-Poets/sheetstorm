from datetime import date
from typing import Any

from django.db.models import Q
from django.db.models import QuerySet
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
        from users.models import CustomUser

        context_data = super().get_context_data(**kwargs)

        from_date = None
        to_date = None

        if "year" in self.kwargs and "month" in self.kwargs:
            year = int(self.kwargs["year"])
            month = int(self.kwargs["month"])
            current_date = timezone.now().date()
            if current_date.year == year and current_date.month == month:
                from_date = current_date - timezone.timedelta(days=30)
                to_date = current_date
            else:
                from_date = timezone.now().date().replace(year=year, month=month, day=1)
                to_date = self._set_last_day_of_month_on_date(year=year, month=month)

        if self.model == CustomUser:
            user = self.object
        else:
            user = self.request.user

        context_data["projects_work_percentage"] = user.get_projects_work_percentage(from_date, to_date)
        return context_data

    @staticmethod
    def _set_last_day_of_month_on_date(year: int, month: int) -> date:
        if month == 12:
            return date(year=year, month=month, day=31)
        return date(year=year, month=month + 1, day=1) - timezone.timedelta(days=1)
