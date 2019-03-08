import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase
from managers.commons.constants import MAX_NAME_LENGTH
from managers.models import Project


class TestProjectModel(TestCase):
    def test_that_project_should_have_start_date(self):
        project = Project(
            name='X',
        )
        with self.assertRaises(ValidationError) as exception:
            project.full_clean()
        self.assertTrue("This field cannot be null." in str(exception.exception))

    def test_that_project_name_should_not_be_blank(self):
        project = Project(
            start_date=datetime.datetime.now().date(),
        )
        with self.assertRaises(ValidationError) as exception:
            project.full_clean()
        self.assertTrue("This field cannot be blank." in str(exception.exception))

    def test_that_project_name_should_not_be_longer_than_set_max_length(self):
        project = Project(
            start_date=datetime.datetime.now().date(),
            name='X' * (MAX_NAME_LENGTH + 1),
        )
        with self.assertRaises(ValidationError) as exception:
            project.full_clean()
        self.assertTrue("Ensure this value has at most " + str(MAX_NAME_LENGTH) + " characters" in str(exception.exception))  # pylint: disable=line-too-long # noqa E501

    def test_that_project_name_should_be_shorter_than_or_equal_set_max_length(self):
        project = Project(
            start_date=datetime.datetime.now().date(),
            name='X' * MAX_NAME_LENGTH,
        )
        try:
            project.full_clean()
        except ValidationError:
            self.fail("Ensure this value has at most " + str(MAX_NAME_LENGTH) + " characters")
