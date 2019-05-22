from datetime import date
from decimal import Decimal
from typing import Optional

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.functions import Coalesce
from markdown import markdown
from markdown_checklists.extension import ChecklistsExtension

from employees.common.constants import ReportModelConstants
from employees.common.constants import TaskActivityTypeConstans
from employees.common.strings import MAX_HOURS_VALUE_VALIDATOR_MESSAGE
from employees.common.strings import MIN_HOURS_VALUE_VALIDATOR_MESSAGE
from employees.common.strings import ReportValidationStrings
from employees.common.validators import MaxDecimalValueValidator
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

        return queryset.aggregate(work_hours_sum=Coalesce(models.Sum("work_hours"), 0))["work_hours_sum"]


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
    work_hours = models.DecimalField(
        max_digits=ReportModelConstants.MAX_DIGITS.value,
        decimal_places=ReportModelConstants.DECIMAL_PLACES.value,
        validators=[
            MinValueValidator(ReportModelConstants.MIN_WORK_HOURS.value, message=MIN_HOURS_VALUE_VALIDATOR_MESSAGE),
            MaxValueValidator(ReportModelConstants.MAX_WORK_HOURS.value, message=MAX_HOURS_VALUE_VALIDATOR_MESSAGE),
            MaxDecimalValueValidator(ReportModelConstants.MAX_WORK_HOURS_DECIMAL_VALUE.value),
        ],
    )
    editable = models.BooleanField(default=True)

    @property
    def work_hours_str(self) -> str:
        return self.work_hours.to_eng_string().replace(".", ":")

    @property
    def markdown_description(self) -> str:
        return markdown(
            self.description,
            extensions=["extra", "sane_lists", "wikilinks", "nl2br", "legacy_em", ChecklistsExtension()],
        )

    def clean(self) -> None:
        super().clean()

        if (
            hasattr(self, "author")
            and isinstance(self.work_hours, Decimal)
            and self.author.report_set.get_report_work_hours_sum_for_date(self.date, self.pk) + self.work_hours > 24
        ):
            raise ValidationError(
                message=ReportValidationStrings.WORK_HOURS_SUM_FOR_GIVEN_DATE_FOR_SINGLE_AUTHOR_EXCEEDED.value
            )
