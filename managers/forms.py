from bootstrap_datepicker_plus import DatePickerInput
from django import forms

from managers.commons.constants import CORRECT_DATE_FORMAT
from managers.models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = "__all__"
        widgets = {
            "start_date": DatePickerInput(options={"format": CORRECT_DATE_FORMAT}),
            "stop_date": DatePickerInput(options={"format": CORRECT_DATE_FORMAT}),
        }
