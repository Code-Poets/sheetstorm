from collections import OrderedDict
from datetime import timedelta
from typing import Any

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from common.convert import convert_string_work_hours_field_to_hour_and_minutes
from employees.common.constants import ReportModelConstants
from employees.common.strings import ReportValidationStrings
from employees.models import Report
from employees.models import TaskActivityType
from managers.models import Project


class HoursField(serializers.DurationField):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            max_value=ReportModelConstants.MAX_WORK_HOURS.value,
            min_value=ReportModelConstants.MIN_WORK_HOURS.value,
            **kwargs
        )

    def to_internal_value(self, data: str) -> timedelta:
        (hours, minutes) = convert_string_work_hours_field_to_hour_and_minutes(
            data, ValidationError(detail=ReportValidationStrings.WORK_HOURS_WRONG_FORMAT.value)
        )
        return timedelta(hours=int(hours), minutes=int(minutes))


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
        if author is not None:
            _24_hours = timedelta(hours=24)
            work_hours_per_day = author.report_set.get_report_work_hours_sum_for_date(
                for_date=data["date"], excluded_id=pk
            )
            hours_to_compare = work_hours_per_day + data["work_hours"]
            if hours_to_compare > _24_hours:
                raise serializers.ValidationError(
                    detail=ReportValidationStrings.WORK_HOURS_SUM_FOR_GIVEN_DATE_FOR_SINGLE_AUTHOR_EXCEEDED.value
                )
            if hours_to_compare < ReportModelConstants.MIN_WORK_HOURS.value:
                raise serializers.ValidationError(
                    detail=ReportValidationStrings.WORK_HOURS_MIN_VALUE_NOT_EXCEEDED.value
                )
        return data
