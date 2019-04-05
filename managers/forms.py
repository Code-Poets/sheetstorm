from bootstrap_datepicker_plus import DatePickerInput
from django import forms

from managers.models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = "__all__"
        widgets = {"start_date": DatePickerInput(format="%Y-%m-%d"), "stop_date": DatePickerInput(format="%Y-%m-%d")}
