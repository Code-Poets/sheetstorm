from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from django_select2.forms import Select2MultipleWidget

from common.constants import CORRECT_DATE_FORMAT
from managers.models import Project
from users.models import CustomUser


class ManagerSelectMultiple(Select2MultipleWidget):
    def optgroups(self, name: str, value: List, attrs: Optional[Dict] = None) -> List:
        self.choices.queryset = CustomUser.objects.exclude(user_type=CustomUser.UserType.EMPLOYEE.name).exclude(
            pk=self.user_pk if hasattr(self, "user_pk") else None
        )
        return super().optgroups(name, value, attrs)


class ProjectAdminForm(forms.ModelForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if hasattr(self, "user_pk"):
            ManagerSelectMultiple.user_pk = self.user_pk

    class Meta:
        model = Project
        fields = "__all__"
        widgets = {
            "start_date": DatePickerInput(options={"format": CORRECT_DATE_FORMAT}),
            "stop_date": DatePickerInput(options={"format": CORRECT_DATE_FORMAT}),
            "managers": ManagerSelectMultiple(),
            "members": Select2MultipleWidget(),
        }


class ProjectManagerForm(ProjectAdminForm):
    class Meta:
        model = ProjectAdminForm.Meta.model
        fields = ProjectAdminForm.Meta.fields
        exclude = ("managers",)
        widgets = ProjectAdminForm.Meta.widgets
