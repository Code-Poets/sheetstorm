from typing import Any

from django import forms
from django.db.models import QuerySet


class ProjectJoinForm(forms.Form):

    projects = forms.ChoiceField(choices=[])

    def __init__(self, queryset: QuerySet, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        assert isinstance(queryset, QuerySet)
        self.fields["projects"].choices = [(project.id, project.name) for project in queryset]
