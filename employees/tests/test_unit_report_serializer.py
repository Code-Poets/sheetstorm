import datetime
from decimal import Decimal

from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory

from employees.common.constants import ReportModelConstants
from employees.common.strings import MAX_DECIMAL_VALUE_VALIDATOR_MESSAGE
from employees.common.strings import MAX_HOURS_VALUE_VALIDATOR_MESSAGE
from employees.common.strings import MIN_HOURS_VALUE_VALIDATOR_MESSAGE
from employees.models import Report
from employees.models import TaskActivityType
from employees.serializers import HoursField
from employees.serializers import ReportSerializer
from managers.models import Project
from users.models import CustomUser
from utils.base_tests import BaseSerializerTestCase
from utils.sample_data_generators import generate_decimal_with_decimal_places
from utils.sample_data_generators import generate_decimal_with_digits


class DataSetUpToTests(BaseSerializerTestCase):
    serializer_class = ReportSerializer
    required_input = {
        "date": datetime.datetime.now().date(),
        "description": "Some description",
        "author": None,
        "project": None,
        "work_hours": Decimal("8.00"),
    }

    def setUp(self):

        self.sample_string_for_type_validation_tests = "This is a string"
        author = CustomUser(
            email="testuser@codepoets.it", password="newuserpasswd", first_name="John", last_name="Doe", country="PL"
        )
        author.full_clean()
        author.save()

        project = Project(name="Test Project", start_date=datetime.datetime.now())
        project.full_clean()
        project.save()

        self.required_input["author"] = author
        self.required_input["project"] = project
        self.required_input["task_activities"] = TaskActivityType.objects.get(name="Other")


class ReportSerializerTests(DataSetUpToTests):
    def test_report_serializer_date_field_should_accept_correct_value(self):
        self.field_should_accept_input(field="date", value="2018-11-07")

    def test_report_serializer_description_field_should_accept_correct_value(self):
        self.field_should_accept_input(field="description", value="Example description")

    def test_report_serializer_work_hours_field_should_accept_correct_value(self):
        self.field_should_accept_input(field="work_hours", value=Decimal("8.00"))


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
    def test_report_serializer_work_hours_field_should_not_accept_value_exceeding_set_digits_number(self):
        self.field_should_not_accept_input(
            field="work_hours", value=generate_decimal_with_digits(digits=ReportModelConstants.MAX_DIGITS.value + 1)
        )

    def test_report_serializer_work_hours_field_should_not_accept_value_exceeding_set_decimal_places_number(self):
        self.field_should_not_accept_input(
            field="work_hours",
            value=generate_decimal_with_decimal_places(decimal_places=ReportModelConstants.DECIMAL_PLACES.value + 1),
        )

    def test_report_serializer_work_hours_field_should_not_accept_value_exceeding_set_maximum(self):
        self.field_should_not_accept_input(
            field="work_hours",
            value=ReportModelConstants.MAX_WORK_HOURS.value + Decimal("0.01"),
            error_message=MAX_HOURS_VALUE_VALIDATOR_MESSAGE,
        )

    def test_report_serializer_work_hours_field_should_not_accept_value_exceeding_set_minimum(self):
        self.field_should_not_accept_input(
            field="work_hours",
            value=ReportModelConstants.MIN_WORK_HOURS.value - Decimal("0.01"),
            error_message=MIN_HOURS_VALUE_VALIDATOR_MESSAGE,
        )

    def test_report_serializer_work_hours_field_should_not_accept_decimal_value_exceeding_set_maximum(self):
        self.field_should_not_accept_input(
            field="work_hours",
            value=ReportModelConstants.MAX_WORK_HOURS_DECIMAL_VALUE.value + Decimal("0.01"),
            error_message=MAX_DECIMAL_VALUE_VALIDATOR_MESSAGE,
        )

    def test_report_serializer_work_hours_should_not_accept_non_numeric_value(self):
        self.field_should_not_accept_input(field="work_hours", value=self.sample_string_for_type_validation_tests)

    def test_report_serializer_work_hours_field_should_not_be_empty(self):
        self.field_should_not_accept_null(field="work_hours")

    def test_report_serializer_to_representation_method_should_replace_work_hours_with_string_containing_colon_instead_of_dot(
        self
    ):
        report = Report(
            date=datetime.datetime.now().date(),
            description=self.required_input["description"],
            author=self.required_input["author"],
            project=self.required_input["project"],
            work_hours=Decimal("8.00"),
        )
        report.full_clean()
        report.save()
        request = APIRequestFactory().get(path=reverse("custom-report-detail", args=(report.pk,)))
        serializer = ReportSerializer(report, context={"request": request})
        data = serializer.to_representation(report)
        self.assertEqual(data["work_hours"], "8:00")


class AdminReportSerializerTests(DataSetUpToTests):
    serializer_class = AdminReportSerializer

    def test_report_serializer_creation_date_field_should_ignore_input_on_model_update(self):
        timestamp = datetime.datetime(2001, 1, 1, 0, 0, 0, 0)
        report = Report(
            date=datetime.datetime.now().date(),
            description=self.required_input["description"],
            author=self.required_input["author"],
            project=self.required_input["project"],
            work_hours=Decimal("8.00"),
        )
        report.full_clean()
        report.save()
        request = APIRequestFactory().get(path=reverse("admin-report-detail", args=(report.pk,)))
        serializer = AdminReportSerializer(
            instance=report,
            context={"request": request},
            data={
                "date": self.required_input["date"],
                "description": self.required_input["description"],
                "author": self.required_input["author"],
                "project": self.required_input["project"],
                "work_hours": self.required_input["work_hours"],
                "creation_date": timestamp,
            },
        )
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertFalse(serializer.instance.creation_date is timestamp)

    def test_report_serializer_last_update_field_should_ignore_input_on_model_update(self):
        timestamp = datetime.datetime(2001, 1, 1, 0, 0, 0, 0)
        report = Report(
            date=datetime.datetime.now().date(),
            description=self.required_input["description"],
            author=self.required_input["author"],
            project=self.required_input["project"],
            work_hours=Decimal("8.00"),
        )
        report.full_clean()
        report.save()
        request = APIRequestFactory().get(path=reverse("admin-report-detail", args=(report.pk,)))
        serializer = AdminReportSerializer(
            instance=report,
            context={"request": request},
            data={
                "date": self.required_input["date"],
                "description": self.required_input["description"],
                "author": self.required_input["author"],
                "project": self.required_input["project"],
                "work_hours": self.required_input["work_hours"],
                "last_update": timestamp,
            },
        )
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertFalse(serializer.instance.last_update is timestamp)

    def test_report_serializer_editable_field_should_ignore_input_on_model_update(self):
        report = Report(
            date=datetime.datetime.now().date(),
            description=self.required_input["description"],
            author=self.required_input["author"],
            project=self.required_input["project"],
            work_hours=Decimal("8.00"),
        )
        report.full_clean()
        report.save()
        request = APIRequestFactory().get(path=reverse("admin-report-detail", args=(report.pk,)))
        serializer = AdminReportSerializer(
            instance=report,
            context={"request": request},
            data={
                "date": self.required_input["date"],
                "description": self.required_input["description"],
                "author": self.required_input["author"],
                "project": self.required_input["project"],
                "work_hours": self.required_input["work_hours"],
                "editable": False,
            },
        )
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertTrue(serializer.instance.editable)


class HoursFieldTests(TestCase):
    def test_to_internal_value_should_change_string_with_colon_representing_hour_to_numeric_value_with_dot_separator(
        self
    ):
        hours_field = HoursField()
        data = hours_field.to_internal_value("8:00")
        self.assertEqual(data, Decimal("8.00"))
