from typing import Any

from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from django_select2.forms import Select2MultipleWidget

from common.constants import CORRECT_DATE_FORMAT
from managers.models import Project
from users.models import CustomUser


class ProjectAdminForm(forms.ModelForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        user_pk = kwargs.pop("user_pk", None)
        super().__init__(*args, **kwargs)

        managers_to_choose = CustomUser.objects.active().exclude(user_type=CustomUser.UserType.EMPLOYEE.name)
        if self.instance.pk:
            self.fields["managers"].queryset = managers_to_choose
        else:
            self.fields["managers"].queryset = managers_to_choose.exclude(pk=user_pk)
            self.fields["managers"].required = False
        self.fields["members"].queryset = CustomUser.objects.active()

    class Meta:
        model = Project
        fields = "__all__"
        widgets = {
            "start_date": DatePickerInput(options={"format": CORRECT_DATE_FORMAT}),
            "stop_date": DatePickerInput(options={"format": CORRECT_DATE_FORMAT}),
            "managers": Select2MultipleWidget(),
            "members": Select2MultipleWidget(),
        }


class ProjectManagerForm(forms.ModelForm):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.fields["members"].queryset = CustomUser.objects.active()

    class Meta:
        model = Project
        exclude = ("managers",)
        widgets = ProjectAdminForm.Meta.widgets
