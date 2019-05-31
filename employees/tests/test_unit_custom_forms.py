import datetime

import assertpy
import pytest
from django.core.exceptions import ValidationError
from django.test import TestCase

from employees.common.strings import ReportValidationStrings
from employees.forms import DurationFieldForm
from employees.forms import ProjectJoinForm
from managers.models import Project


class ProjectJoinFormTests(TestCase):
    def test_project_join_form_should_create_choice_field_with_project_name_and_id_based_on_queryset_provided_in_constructor(
        self
    ):
        queryset_length = 10
        for i in range(queryset_length):
            project = Project(name=f"Test Project {i}", start_date=datetime.datetime.now())
            project.full_clean()
            project.save()
        queryset = Project.objects.all()
        form = ProjectJoinForm(queryset)
        choices = form.fields["projects"].choices
        self.assertIsNotNone(choices)
        self.assertEqual(len(choices), queryset_length)
        for i in range(queryset_length):
            self.assertEqual(choices[i][0], queryset[i].id)
            self.assertEqual(choices[i][1], queryset[i].name)


class TestDurationFieldForm:
    def _test_duration_field_form(self, initial_value: str, input_value: str) -> str:  # pylint: disable=no-self-use
        duration_field_form = DurationFieldForm(initial=initial_value)
        return duration_field_form.clean(input_value)

    @pytest.mark.parametrize(
        ("initial_value", "input_value", "expected_value"), [("08:00", "8:00", "8:00:00"), ("08:00", "8:0", "8:0:00")]
    )
    def test_that_correct_work_hours_is_same_as_assumpted(self, initial_value, input_value, expected_value):
        assertpy.assert_that(self._test_duration_field_form(initial_value, input_value)).is_equal_to(expected_value)

    @pytest.mark.parametrize(
        ("initial_value", "input_value"),
        [("08:00", ":00"), ("08:00", "8:"), ("08:00", ":"), ("08:00", ""), ("08:00", "four:zero"), ("08:00", "8:zero")],
    )
    def test_that_incorrect_work_hours_will_raise_exception(self, initial_value, input_value):
        with pytest.raises(ValidationError) as exception:
            self._test_duration_field_form(initial_value, input_value)
        assertpy.assert_that(exception.value.message).is_equal_to(ReportValidationStrings.WORK_HOURS_WRONG_FORMAT.value)
