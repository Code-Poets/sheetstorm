from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models
from markdown import markdown
from markdown_checklists.extension import ChecklistsExtension

from employees.common.constants import ReportModelConstants
from employees.common.strings import MAX_HOURS_VALUE_VALIDATOR_MESSAGE
from employees.common.strings import MIN_HOURS_VALUE_VALIDATOR_MESSAGE
from employees.common.strings import TaskActivitiesStrings
from employees.common.validators import MaxDecimalValueValidator
from managers.models import Project
from users.common.fields import ChoiceEnum
from users.models import CustomUser


class Report(models.Model):
    class TaskType(ChoiceEnum):
        PROJECT_MANAGEMENT = TaskActivitiesStrings.PROJECT_MANAGEMENT.value
        MEETING = TaskActivitiesStrings.MEETING.value
        SPEC_AND_DOCS = TaskActivitiesStrings.SPEC_AND_DOCS.value
        DESING_AND_RESEARCH = TaskActivitiesStrings.DESING_AND_RESEARCH.value
        FRONTED_DEVELOPMENT = TaskActivitiesStrings.FRONTED_DEVELOPMENT.value
        BACKEND_DEVELOPMENT = TaskActivitiesStrings.BACKEND_DEVELOPMENT.value
        QUALITY_ASSURANCE_TESTING = TaskActivitiesStrings.QUALITY_ASSURANCE_TESTING.value
        TRAVEL = TaskActivitiesStrings.TRAVEL.value
        DEVOPS = TaskActivitiesStrings.DEVOPS.value
        REVIEW = TaskActivitiesStrings.REVIEW.value
        CONFERENCE = TaskActivitiesStrings.CONFERENCE.value
        OTHER = TaskActivitiesStrings.OTHER.value
        ADMINISTRATIVE = TaskActivitiesStrings.ADMINISTRATIVE.value
        MARKETING = TaskActivitiesStrings.MARKETING.value
        TRAINING = TaskActivitiesStrings.TRAINING.value
        MENTORSHIP = TaskActivitiesStrings.MENTORSHIP.value
        GRAPHIC_DESIGN = TaskActivitiesStrings.GRAPHIC_DESIGN.value

    date = models.DateField()
    description = models.CharField(max_length=ReportModelConstants.MAX_DESCRIPTION_LENGTH.value)
    task_activities = models.CharField(
        max_length=ReportModelConstants.TASK_ACTIVITIES_MAX_LENGTH.value,
        choices=TaskType.choices(),
        default=TaskType.OTHER.name,
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
