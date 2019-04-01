from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models
from markdown_deux import markdown

from employees.common.constants import ReportModelConstants
from employees.common.strings import MAX_HOURS_VALUE_VALIDATOR_MESSAGE
from employees.common.strings import MIN_HOURS_VALUE_VALIDATOR_MESSAGE
from employees.common.validators import MaxDecimalValueValidator
from managers.models import Project
from users.models import CustomUser


class Report(models.Model):
    date = models.DateField()
    description = models.CharField(
        max_length=ReportModelConstants.MAX_DESCRIPTION_LENGTH.value,
    )
    creation_date = models.DateTimeField(
        auto_now_add=True,
    )
    last_update = models.DateTimeField(
        auto_now=True,
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
    )
    work_hours = models.DecimalField(
        max_digits=ReportModelConstants.MAX_DIGITS.value,
        decimal_places=ReportModelConstants.DECIMAL_PLACES.value,
        validators=[
            MinValueValidator(
                ReportModelConstants.MIN_WORK_HOURS.value,
                message=MIN_HOURS_VALUE_VALIDATOR_MESSAGE,
            ),
            MaxValueValidator(
                ReportModelConstants.MAX_WORK_HOURS.value,
                message=MAX_HOURS_VALUE_VALIDATOR_MESSAGE,
            ),
            MaxDecimalValueValidator(
                ReportModelConstants.MAX_WORK_HOURS_DECIMAL_VALUE.value,
            ),
        ]
    )
    editable = models.BooleanField(
        default=True,
    )

    @property
    def work_hours_str(self):
        return self.work_hours.to_eng_string().replace('.', ':')

    @property
    def markdown_description(self):
        return markdown(self.description)
