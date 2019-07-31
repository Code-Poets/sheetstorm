import datetime
from typing import Any
from typing import Optional

from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db.models import QuerySet
from django.forms import HiddenInput
from django.forms import TextInput
from django.utils.dateparse import parse_duration
from django.utils.duration import duration_string

from common.convert import convert_string_work_hours_field_to_hour_and_minutes
from common.convert import timedelta_to_string
from employees.common.constants import MonthNavigationConstants
from employees.models import Report
from employees.models import TaskActivityType
from managers.models import Project
from users.models import CustomUser


class ProjectJoinForm(forms.Form):

    projects = forms.ChoiceField(choices=[])

    def __init__(self, queryset: QuerySet, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        assert isinstance(queryset, QuerySet)
        self.fields["projects"].choices = [(project.id, project.name) for project in queryset]


class DurationInput(TextInput):
    def format_value(self, value: Optional[str]) -> str:
        if value is not None and value != ":":
            return timedelta_to_string(parse_duration(value))
        return ""


class DurationFieldForm(forms.DurationField):
    widget = DurationInput(attrs={"data-mask": "09:99", "placeholder": "H:MM"})

    def clean(self, value: str) -> str:
        if value is None:
            return ""
        (hours, minutes) = convert_string_work_hours_field_to_hour_and_minutes(value)
        return f"{hours}:{minutes}:00"

    def prepare_value(self, value: str) -> str:
        if isinstance(value, datetime.timedelta):
            return duration_string(value)
        else:
            return f"{value}:00"


class ReportForm(forms.ModelForm):
    work_hours = DurationFieldForm()
    project = forms.ModelChoiceField(queryset=Project.objects, empty_label=None)

    class Meta:
        model = Report
        fields = ("date", "author", "description", "project", "task_activities", "work_hours")
        widgets = {"date": DatePickerInput(format="%Y-%m-%d"), "author": HiddenInput}

    def __init__(self, *args: Any, **kwargs: Any):
        super(ReportForm, self).__init__(*args, **kwargs)
        author = kwargs["initial"]["author"]
        self.fields["project"].queryset = author.get_project_ordered_by_last_report_creation_date()

        self._filter_task_activities_per_project(author)
        self._set_last_choices_in_report_form(author)

    def _filter_task_activities_per_project(self, author: CustomUser) -> None:
        if 'project' in self.data:
            project_id = int(self.data.get('project'))
            self.fields['task_activities'].queryset = TaskActivityType.objects.filter(projects=project_id).order_by('name')
        elif self.instance.pk:
            self.fields['task_activities'].queryset = self.instance.project.project_activities.order_by('name')

    def _set_last_choices_in_report_form(self, author):
        if self.instance.pk is None:
            if self.fields["project"].queryset.exists():
                self.initial["project"] = self.fields["project"].queryset.first()
            report_set = author.report_set.order_by("-creation_date")
            if report_set:
                self.fields['task_activities'].queryset = report_set.first().project.project_activities.all()
                self.initial["task_activities"] = report_set.first().task_activities


class MonthSwitchForm(forms.Form):

    date = forms.DateField(
        widget=DatePickerInput(format="%m-%Y"),
        label=False,
        validators=[
            MaxValueValidator(
                datetime.date(
                    year=MonthNavigationConstants.MAX_YEAR_VALUE.value,
                    month=MonthNavigationConstants.MAX_MONTH_VALUE.value,
                    day=1,
                )
            ),
            MinValueValidator(
                datetime.date(
                    year=MonthNavigationConstants.MIN_YEAR_VALUE.value,
                    month=MonthNavigationConstants.MIN_MONTH_VALUE.value,
                    day=1,
                )
            ),
        ],
    )

    def __init__(  # pylint: disable=keyword-arg-before-vararg
        self, initial_date: Optional[datetime.date] = None, *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        if initial_date is not None:
            self.fields["date"].initial = initial_date

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MonthSwitchForm):
            return NotImplemented
        self_dict = self.fields["date"].__dict__
        other_dict = other.fields["date"].__dict__
        for key in self_dict.keys():
            if key == "widget":
                if self_dict[key].__dict__ != other_dict[key].__dict__:
                    return False
            elif self_dict[key] != other_dict[key]:
                return False
        return True


class TaskActivityForm(forms.ModelForm):
    class Meta:
        model = TaskActivityType
        fields = ["name"]
