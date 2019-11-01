from typing import Any

from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from django_select2.forms import Select2MultipleWidget

from common.constants import CORRECT_DATE_FORMAT
from employees.models import TaskActivityType
from managers.models import Project
from users.models import CustomUser


class ActivityWidget(forms.ModelMultipleChoiceField):
    widget = Select2MultipleWidget()

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            queryset=TaskActivityType.objects.all(),
            required=False,
            initial=TaskActivityType.objects.filter(is_default=True),
            **kwargs
        )


class ProjectAdminForm(forms.ModelForm):
    activities = ActivityWidget()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        user_pk = kwargs.pop("user_pk", None)
        super().__init__(*args, **kwargs)

        managers_to_choose = CustomUser.objects.active().exclude(user_type=CustomUser.UserType.EMPLOYEE.name)
        if self.instance.pk:
            self.fields["managers"].queryset = managers_to_choose
            self.initial["activities"] = list(TaskActivityType.objects.filter(projects=self.instance.pk))
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

    def save(self, commit: bool = True) -> Project:
        project = super().save()
        project.project_activities.set(self.cleaned_data["activities"])
        return project


class ProjectManagerForm(forms.ModelForm):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.fields["members"].queryset = CustomUser.objects.active()

    activities = ActivityWidget()

    class Meta:
        model = Project
        exclude = ("managers",)
        widgets = ProjectAdminForm.Meta.widgets

    def save(self, commit: bool = True) -> Project:
        project = super().save()
        project.project_activities.set(self.cleaned_data["activities"])
        return project
