from typing import Any

from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.forms import TextInput
from django.utils.dateparse import parse_duration

from common.convert import timedelta_to_string
from employees.common.strings import ReportValidationStrings
from employees.models import Report


class ProjectJoinForm(forms.Form):

    projects = forms.ChoiceField(choices=[])

    def __init__(self, queryset: QuerySet, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        assert isinstance(queryset, QuerySet)
        self.fields["projects"].choices = [(project.id, project.name) for project in queryset]


class DurationInput(TextInput):
    def format_value(self, value: str) -> str:
        return timedelta_to_string(parse_duration(value))


class DurationFieldForm(forms.DurationField):
    widget = DurationInput

    def clean(self, value: str) -> str:
        if value.count(":") != 1:
            raise ValidationError(message=ReportValidationStrings.WORK_HOURS_WRONG_FORMAT.value)
        hours, minutes = value.split(":")
        if not hours.isdigit() or not minutes.isdigit():
            raise ValidationError(message=ReportValidationStrings.WORK_HOURS_WRONG_FORMAT.value)
        return f"{hours}:{minutes}:00"


class AdminReportForm(forms.ModelForm):

    work_hours = DurationFieldForm()

    class Meta:
        model = Report
        fields = ("date", "description", "task_activities", "project", "work_hours")
        widgets = {"date": DatePickerInput(format="%Y-%m-%d")}
