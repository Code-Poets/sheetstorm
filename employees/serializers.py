from collections import OrderedDict
from decimal import Decimal
from typing import Any

from rest_framework import serializers

from employees.common.constants import ReportModelConstants
from employees.common.strings import MAX_HOURS_VALUE_VALIDATOR_MESSAGE
from employees.common.strings import MIN_HOURS_VALUE_VALIDATOR_MESSAGE
from employees.common.strings import ReportValidationStrings
from employees.common.validators import MaxDecimalValueValidator
from employees.models import Report
from employees.models import TaskActivityType
from managers.models import Project


class HoursField(serializers.DecimalField):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            max_value=ReportModelConstants.MAX_WORK_HOURS.value,
            min_value=ReportModelConstants.MIN_WORK_HOURS.value,
            max_digits=ReportModelConstants.MAX_DIGITS.value,
            decimal_places=ReportModelConstants.DECIMAL_PLACES.value,
            validators=[MaxDecimalValueValidator(ReportModelConstants.MAX_WORK_HOURS_DECIMAL_VALUE.value)],
            **kwargs
        )
        self.validators[1].message = MAX_HOURS_VALUE_VALIDATOR_MESSAGE
        self.validators[2].message = MIN_HOURS_VALUE_VALIDATOR_MESSAGE

    def to_internal_value(self, data: str) -> Decimal:
        if isinstance(data, str) and ":" in data:
            converted = data.replace(":", ".")
            return super().to_internal_value(converted)
        else:
            return super().to_internal_value(data)


class ReportSerializer(serializers.HyperlinkedModelSerializer):

    project = serializers.SlugRelatedField(queryset=Project.objects.all(), slug_field="name")
    author = serializers.StringRelatedField()
    task_activities = serializers.SlugRelatedField(queryset=TaskActivityType.objects.all(), slug_field="name")
    description = serializers.CharField(
        style={"base_template": "textarea.html"}, max_length=ReportModelConstants.MAX_DESCRIPTION_LENGTH.value
    )

    work_hours = HoursField()

    class Meta:
        model = Report
        fields = ("url", "date", "project", "author", "task_activities", "description", "work_hours")

    def to_representation(self, instance: Report) -> OrderedDict:
        data = super().to_representation(instance)
        if isinstance(self.instance, Report):
            data["work_hours"] = self.instance.work_hours_str
        return data

    def validate(self, data: OrderedDict) -> OrderedDict:
        data = super().validate(data)
        author = None
        pk = None
        if self.instance is not None:
            author = self.instance.author
            pk = self.instance.pk
        elif "request" in self.context:
            author = self.context["request"].user
        if (
            author is not None
            and author.report_set.get_report_work_hours_sum_for_date(for_date=data["date"], excluded_id=pk)
            + data["work_hours"]
            > 24
        ):
            raise serializers.ValidationError(
                detail=ReportValidationStrings.WORK_HOURS_SUM_FOR_GIVEN_DATE_FOR_SINGLE_AUTHOR_EXCEEDED.value
            )
        return data
