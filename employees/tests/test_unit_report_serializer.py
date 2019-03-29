import datetime

from django.test import TestCase
from parameterized import parameterized
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory

from employees.common.constants import ReportModelConstants
from employees.models import Report
from employees.models import TaskActivityType
from employees.serializers import HoursField
from employees.serializers import ReportSerializer
from managers.models import Project
from users.models import CustomUser
from utils.base_tests import BaseSerializerTestCase


class DataSetUpToTests(BaseSerializerTestCase):
    serializer_class = ReportSerializer

    def setUp(self):
        super().setUp()
        task_type = TaskActivityType(pk=1, name="Other")
        task_type.full_clean()
        task_type.save()
        self.sample_string_for_type_validation_tests = "This is a string"
        author = CustomUser(
            email="testuser@codepoets.it", password="newuserpasswd", first_name="John", last_name="Doe", country="PL"
        )
        author.full_clean()
        author.save()

        project = Project(name="Test Project", start_date=datetime.datetime.now())
        project.full_clean()
        project.save()

        self.required_input = {
            "date": datetime.datetime.now().date(),
            "description": "Some description",
            "author": author,
            "project": project,
            "work_hours": "08:00",
            "task_activities": TaskActivityType.objects.get(name="Other"),
        }


class ReportSerializerTests(DataSetUpToTests):
    def test_report_serializer_date_field_should_accept_correct_value(self):
        self.field_should_accept_input(field="date", value="2018-11-07")

    def test_report_serializer_description_field_should_accept_correct_value(self):
        self.field_should_accept_input(field="description", value="Example description")

    def test_report_serializer_work_hours_field_should_accept_correct_value(self):
        self.field_should_accept_input(field="work_hours", value="8:00")

    def test_report_serializer_should_be_valid_total_sum_of_hours_from_single_day_for_single_author_is_24(self):
        report = Report(
            date=datetime.datetime.now().date(),
            description=self.required_input["description"],
            author=self.required_input["author"],
            project=self.required_input["project"],
            work_hours=datetime.timedelta(hours=12),
        )
        report.full_clean()
        report.save()
        request = APIRequestFactory().get(path=reverse("custom-report-list", kwargs={"year": 2019, "month": 5}))
        data = self.required_input.copy()
        data["work_hours"] = "12:00"
        request.user = data["author"]
        serializer = ReportSerializer(data=data, context={"request": request})
        self.assertTrue(serializer.is_valid())

    def test_report_serializer_should_raise_error_if_total_sum_of_hours_from_single_day_for_single_author_exceeds_24(
        self
    ):
        report = Report(
            date=datetime.datetime.now().date(),
            description=self.required_input["description"],
            author=self.required_input["author"],
            project=self.required_input["project"],
            work_hours=datetime.timedelta(hours=12),
        )
        report.full_clean()
        report.save()
        request = APIRequestFactory().get(path=reverse("custom-report-list", kwargs={"year": 2019, "month": 5}))
        data = self.required_input.copy()
        data["work_hours"] = "12.01"
        request.user = data["author"]
        serializer = ReportSerializer(data=data, context={"request": request})
        self.assertFalse(serializer.is_valid())

    def test_report_serializer_based_on_instance_should_be_valid_total_sum_of_hours_from_single_day_for_single_author_is_24(
        self
    ):
        report = Report(
            date=datetime.datetime.now().date(),
            description=self.required_input["description"],
            author=self.required_input["author"],
            project=self.required_input["project"],
            work_hours=datetime.timedelta(hours=10),
        )
        report.full_clean()
        report.save()
        other_report = Report(
            date=datetime.datetime.now().date(),
            description=self.required_input["description"],
            author=self.required_input["author"],
            project=self.required_input["project"],
            work_hours=datetime.timedelta(hours=12),
        )
        other_report.full_clean()
        other_report.save()
        request = APIRequestFactory().get(path=reverse("custom-report-detail", args=(report.pk,)))
        data = self.required_input.copy()
        data["work_hours"] = "12:00"
        request.user = data["author"]
        serializer = ReportSerializer(instance=report, data=data, context={"request": request})
        self.assertTrue(serializer.is_valid())

    def test_report_serializer_based_on_instance_should_raise_error_if_total_sum_of_hours_from_single_day_for_single_author_exceeds_24(
        self
    ):
        report = Report(
            date=datetime.datetime.now().date(),
            description=self.required_input["description"],
            author=self.required_input["author"],
            project=self.required_input["project"],
            work_hours=datetime.timedelta(hours=10),
        )
        report.full_clean()
        report.save()
        other_report = Report(
            date=datetime.datetime.now().date(),
            description=self.required_input["description"],
            author=self.required_input["author"],
            project=self.required_input["project"],
            work_hours=datetime.timedelta(hours=12),
        )
        other_report.full_clean()
        other_report.save()
        request = APIRequestFactory().get(path=reverse("custom-report-detail", args=(report.pk,)))
        data = self.required_input.copy()
        data["work_hours"] = "12:01"
        request.user = data["author"]
        serializer = ReportSerializer(instance=report, data=data, context={"request": request})
        self.assertFalse(serializer.is_valid())


class ReportSerializerDateFailTests(DataSetUpToTests):
    def test_report_serializer_date_field_should_not_be_empty(self):
        self.field_should_not_accept_null(field="date")

    def test_report_serializer_date_field_should_not_accept_non_date_time_value(self):
        self.field_should_not_accept_input(field="date", value=self.sample_string_for_type_validation_tests)


class ReportSerializerDescriptionFailTests(DataSetUpToTests):
    def test_report_serializer_description_field_should_not_accept_string_longer_than_set_limit(self):
        self.field_should_not_accept_input(
            field="description", value="a" * (ReportModelConstants.MAX_DESCRIPTION_LENGTH.value + 1)
        )

    def test_report_serializer_description_field_should_not_be_empty(self):
        self.field_should_not_accept_null(field="description")


class ReportSerializerWorkHoursFailTests(DataSetUpToTests):
    def test_report_serializer_work_hours_should_not_accept_non_numeric_value(self):
        self.field_should_not_accept_input(field="work_hours", value=self.sample_string_for_type_validation_tests)

    @parameterized.expand(["08.00", ":", ".", "08:", ":60"])
    def test_report_serializer_work_hours_field_should_not_accept_invalid_value(self, value):
        self.field_should_not_accept_input(field="work_hours", value=value)

    def test_report_serializer_work_hours_field_should_not_be_empty(self):
        self.field_should_not_accept_null(field="work_hours")


class HoursFieldTests(TestCase):
    def test_to_internal_value_should_change_string_with_colon_representing_hour_to_numeric_value_with_dot_separator(
        self
    ):
        hours_field = HoursField()
        data = hours_field.to_internal_value("8:00")
        self.assertEqual(data, datetime.timedelta(hours=8))
