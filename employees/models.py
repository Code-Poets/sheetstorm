from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models
from markdown import markdown
from markdown_checklists.extension import ChecklistsExtension

from employees.common.constants import ReportModelConstants
from employees.common.constants import TaskActivityTypeConstans
from employees.common.strings import MAX_HOURS_VALUE_VALIDATOR_MESSAGE
from employees.common.strings import MIN_HOURS_VALUE_VALIDATOR_MESSAGE
from employees.common.validators import MaxDecimalValueValidator
from managers.models import Project
from users.models import CustomUser


class TaskActivityType(models.Model):
    name = models.CharField(max_length=TaskActivityTypeConstans.TASK_ACTIVITIES_MAX_LENGTH.value, default="Other")

    def __str__(self) -> str:
        return self.name


class ReportQuerySet(models.QuerySet):
    def get_work_hours_sum_for_all_dates(self) -> dict:
        return dict(
            self.extra({"date_created": "date(date)"})
            .values("date_created")
            .annotate(created_count=models.Sum("work_hours"))
            .values_list("date_created", "created_count")
        )


class Report(models.Model):
    objects = ReportQuerySet.as_manager()

    date = models.DateField()
    description = models.TextField(max_length=ReportModelConstants.MAX_DESCRIPTION_LENGTH.value)
    task_activities = models.ForeignKey(TaskActivityType, on_delete=models.SET_DEFAULT, default=1)
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
