from typing import Any

from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from django.db.models import QuerySet

from employees.models import Report


class ProjectJoinForm(forms.Form):

    projects = forms.ChoiceField(choices=[])

    def __init__(self, queryset: QuerySet, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        assert isinstance(queryset, QuerySet)
        self.fields["projects"].choices = [(project.id, project.name) for project in queryset]


class AdminReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ("date", "description", "task_activities", "author", "project", "work_hours")
        widgets = {"date": DatePickerInput(format="%Y-%m-%d")}
