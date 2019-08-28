from datetime import datetime
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase

from managers.commons.constants import ProjectConstants
from managers.models import Project
from users.common.model_helpers import create_user_using_full_clean_and_save
from users.common.utils import generate_random_string_from_letters_and_digits
from utils.base_tests import BaseModelTestCase


class TestProjectModel(TestCase):
    def test_project_should_have_start_date(self):
        project = Project(name="X")
        with self.assertRaises(ValidationError) as exception:
            project.full_clean()
        self.assertTrue("This field cannot be null." in str(exception.exception))

    def test_project_name_should_not_be_blank(self):
        project = Project(start_date=datetime.now().date())
        with self.assertRaises(ValidationError) as exception:
            project.full_clean()
        self.assertTrue("This field cannot be blank." in str(exception.exception))

    def test_project_name_should_not_be_longer_than_set_max_length(self):
        project = Project(start_date=datetime.now().date(), name="X" * (ProjectConstants.MAX_NAME_LENGTH.value + 1))
        with self.assertRaises(ValidationError) as exception:
            project.full_clean()
        self.assertTrue(
            "Ensure this value has at most " + str(ProjectConstants.MAX_NAME_LENGTH.value) + " characters"
            in str(exception.exception)
        )  # pylint: disable=line-too-long # noqa E501

    def test_project_name_should_be_shorter_than_or_equal_set_max_length(self):
        project = Project(start_date=datetime.now().date(), name="X" * ProjectConstants.MAX_NAME_LENGTH.value)
        try:
            project.full_clean()
        except ValidationError:
            self.fail("Ensure this value has at most " + str(ProjectConstants.MAX_NAME_LENGTH.value) + " characters")


class TestProjectModelField(BaseModelTestCase):
    model_class = Project
    required_input = {"name": "Example Project", "start_date": datetime.now().date()}

    def setUp(self):
        super().setUp()
        self.manager = create_user_using_full_clean_and_save("manager@codepoets.it", "", "", "managerpassword")
        self.member = create_user_using_full_clean_and_save("projectmember@codepoets.it", "", "", "memberpassword")

    def test_project_model_name_field_should_accept_correct_input(self):
        self.field_should_accept_input("name", "First Project")

    def test_project_model_name_field_may_not_be_empty(self):
        self.field_should_not_accept_null("name")

    def test_project_model_name_field_should_not_accept_string_longer_than_set_limit(self):
        self.field_should_not_accept_input("name", "a" * (ProjectConstants.MAX_NAME_LENGTH.value + 1))

    def test_project_model_start_date_field_should_accept_correct_input(self):
        self.field_should_accept_input("start_date", datetime.now().date())

    def test_project_model_start_date_field_may_not_be_empty(self):
        self.field_should_not_accept_null("start_date")

    def test_project_model_start_date_field_should_not_accept_non_date_or_datetime_value(self):
        self.field_should_not_accept_input("start_date", "123456789")
        self.field_should_not_accept_input(
            "start_date", generate_random_string_from_letters_and_digits(ProjectConstants.MAX_NAME_LENGTH.value)
        )  # pylint: disable=line-too-long # noqa E501

    def test_project_model_stop_date_field_should_accept_correct_input(self):
        self.field_should_accept_input("stop_date", datetime.now().date())

    def test_project_model_stop_date_field_may_be_empty(self):
        self.field_should_accept_null("stop_date")

    def test_project_model_suspended_field_should_accept_correct_input(self):
        self.field_should_accept_input("suspended", True)

    def test_project_model_suspended_field_should_have_default_value(self):
        self.field_should_have_non_null_default("suspended", value=False)

    def test_project_model_managers_field_should_accept_correct_input(self):
        project = self.default_model()
        project.full_clean()
        project.save()
        project.managers.add(self.manager)
        self.assertTrue(project.managers.all().filter(email=self.manager.email).exists())

    def test_project_model_members_field_should_accept_correct_input(self):
        project = self.default_model()
        project.full_clean()
        project.save()
        project.members.add(self.member)
        self.assertTrue(project.members.all().filter(email=self.member.email).exists())

    def test_project_model_end_date_should_not_be_before_start_day(self):
        project = self.default_model()
        project.stop_date = project.start_date - timedelta(1)
        with self.assertRaises(ValidationError) as exception:
            project.full_clean()
            project.save()
        self.assertEqual(ProjectConstants.STOP_DATE_VALIDATION_ERROR_MESSAGE.value, exception.exception.messages.pop())
        self.assertFalse(Project.objects.all().exists())
