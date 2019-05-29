from datetime import date
from datetime import timedelta
from decimal import Decimal
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Coalesce
from markdown import markdown
from markdown_checklists.extension import ChecklistsExtension

from common.convert import timedelta_to_string
from employees.common.constants import ReportModelConstants
from employees.common.constants import TaskActivityTypeConstans
from employees.common.strings import ReportValidationStrings
from managers.models import Project
from users.models import CustomUser


class TaskActivityType(models.Model):
    name = models.CharField(max_length=TaskActivityTypeConstans.TASK_ACTIVITIES_MAX_LENGTH.value, default="Other")

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def get_or_create_default_task_activity_type_pk() -> int:
        default_task_activity_type, _ = TaskActivityType.objects.get_or_create(name="Other")
        default_task_activity_type.full_clean()
        default_task_activity_type.save()
        return default_task_activity_type.pk


class ReportQuerySet(models.QuerySet):
    def get_work_hours_sum_for_all_dates(self) -> dict:
        return dict(
            self.extra({"date_created": "date(date)"})
            .values("date_created")
            .annotate(created_count=models.Sum("work_hours"))
            .values_list("date_created", "created_count")
        )

    def get_report_work_hours_sum_for_date(self, for_date: date, excluded_id: Optional[int] = None) -> Decimal:
        queryset = self.filter(date=for_date)

        # Don't add currently edited report work hours.
        if excluded_id is not None:
            queryset = queryset.exclude(pk=excluded_id)

        return queryset.aggregate(work_hours_sum=Coalesce(models.Sum("work_hours"), timedelta()))["work_hours_sum"]

    def get_work_hours_sum_for_all_authors(self) -> dict:
        return dict(
            self.values("author")
            .annotate(monthly_hours_sum=models.Sum("work_hours"))
            .values_list("author", "monthly_hours_sum")
        )


class Report(models.Model):
    objects = ReportQuerySet.as_manager()

    objects = ReportQuerySet.as_manager()

    date = models.DateField()
    description = models.TextField(max_length=ReportModelConstants.MAX_DESCRIPTION_LENGTH.value)
    task_activities = models.ForeignKey(
        TaskActivityType,
        on_delete=models.SET_DEFAULT,
        default=TaskActivityType.get_or_create_default_task_activity_type_pk,
    )
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    work_hours = models.DurationField()
    editable = models.BooleanField(default=True)

    @property
    def work_hours_str(self) -> str:
        return timedelta_to_string(self.work_hours)

    @property
    def markdown_description(self) -> str:
        return markdown(
            self.description,
            extensions=["extra", "sane_lists", "wikilinks", "nl2br", "legacy_em", ChecklistsExtension()],
        )

    def clean(self) -> None:
        super().clean()

        if hasattr(self, "author"):
            if not isinstance(self.work_hours, timedelta):
                raise ValidationError(message=ReportValidationStrings.WORK_HOURS_FIELD_NOT_TIMEDELTA_INSTANCE.value)
            work_hours_per_day = self.author.report_set.get_report_work_hours_sum_for_date(self.date, self.pk)
            _24_hours = timedelta(hours=24)
            hours_to_compare = work_hours_per_day + self.work_hours
            if hours_to_compare > _24_hours:
                raise ValidationError(
                    message=ReportValidationStrings.WORK_HOURS_SUM_FOR_GIVEN_DATE_FOR_SINGLE_AUTHOR_EXCEEDED.value
                )
            if hours_to_compare < ReportModelConstants.MIN_WORK_HOURS.value:
                raise ValidationError(message=ReportValidationStrings.WORK_HOURS_MIN_VALUE_NOT_EXCEEDED.value)
