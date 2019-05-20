import datetime
from decimal import Decimal

from django.test import TestCase

from employees.common.constants import ReportModelConstants
from employees.factories import ReportFactory
from employees.models import Report
from employees.models import TaskActivityType
from managers.models import Project
from users.models import CustomUser
from utils.base_tests import BaseModelTestCase
from utils.sample_data_generators import generate_decimal_with_decimal_places
from utils.sample_data_generators import generate_decimal_with_digits


class DataSetUpToTests(BaseModelTestCase):
    model_class = Report
    required_input = {
        "date": datetime.datetime.now().date(),
        "description": "Some description",
        "author": None,
        "project": None,
        "work_hours": Decimal("8.00"),
    }

    def setUp(self):

        self.SAMPLE_STRING_FOR_TYPE_VALIDATION_TESTS = "This is a string"
        self.author = CustomUser(
            email="testuser@codepoets.it", password="newuserpasswd", first_name="John", last_name="Doe", country="PL"
        )
        self.author.full_clean()
        self.author.save()

        self.project = Project(name="Test Project", start_date=datetime.datetime.now())
        self.project.full_clean()
        self.project.save()

        self.required_input["author"] = self.author
        self.required_input["project"] = self.project

        self.REPORT_MODEL_DATA = self.required_input.copy()


class TestReportModel(DataSetUpToTests):

    # PARAM
    def test_report_model_save_date_field_should_accept_correct_input(self):
        self.field_should_accept_input("date", datetime.datetime.now().date())

    # PARAM
    def test_report_model_description_field_should_accept_correct_input(self):
        self.field_should_accept_input("description", "Example")

    # PARAM
    def test_report_model_creation_date_field_should_be_filled_on_save(self):
        self.field_should_have_non_null_default("creation_date")

    # PARAM
    def test_report_model_last_update_field_should_be_filled_on_save(self):
        self.field_should_have_non_null_default("last_update")

    # PARAM
    def test_report_model_author_field_should_accept_correct_input(self):
        self.field_should_accept_input("author", self.author)

    # PARAM
    def test_report_model_project_field_should_accept_correct_input(self):
        self.field_should_accept_input("project", self.project)

    # PARAM
    def test_report_model_work_hours_field_should_accept_correct_input(self):
        self.field_should_accept_input("work_hours", Decimal("8.00"))

    def test_report_model_editable_field_should_have_default_value(self):
        self.field_should_have_non_null_default(field="editable", value=True)

    def test_report_model_last_update_field_should_be_changed_on_update(self):
        self.field_auto_now_test("last_update", "description", "Updated")


class TestReportDataParameterFails(DataSetUpToTests):
    def test_report_model_date_field_should_not_be_empty(self):
        self.field_should_not_accept_null("date")

    # PARAM
    def test_report_model_date_field_should_not_accept_non_date_value(self):
        self.field_should_not_accept_input("date", self.SAMPLE_STRING_FOR_TYPE_VALIDATION_TESTS)


class TestReportDescriptionParameterFails(DataSetUpToTests):
    def test_report_model_description_field_should_not_be_empty(self):
        self.field_should_not_accept_null("description")


class TestReportProjectParameterFails(DataSetUpToTests):

    # PARAM
    def test_report_model_project_field_should_not_accept_non_model_value(self):
        self.key_should_not_accept_incorrect_input("project", self.SAMPLE_STRING_FOR_TYPE_VALIDATION_TESTS)

    def test_report_model_work_project_field_should_not_be_empty(self):
        self.field_should_not_accept_null("project")


class TestReportAuthorParameterFails(DataSetUpToTests):

    # PARAM
    def test_report_model_author_field_should_not_accept_non_model_value(self):
        self.key_should_not_accept_incorrect_input("author", self.SAMPLE_STRING_FOR_TYPE_VALIDATION_TESTS)

    def test_report_model_author_field_should_not_be_empty(self):
        self.field_should_not_accept_null("author")


class TestReportWorkHoursParameterFails(DataSetUpToTests):

    # PARAM
    def test_report_model_work_hours_field_should_not_accept_non_numeric_value(self):
        self.field_should_not_accept_input("work_hours", self.SAMPLE_STRING_FOR_TYPE_VALIDATION_TESTS)

    def test_report_model_work_hours_field_should_not_be_empty(self):
        self.field_should_not_accept_null("work_hours")

    # PARAM
    def test_report_model_work_hours_field_should_not_accept_value_exceeding_set_digits_number(self):
        self.field_should_not_accept_input(
            "work_hours", generate_decimal_with_digits(digits=ReportModelConstants.MAX_DIGITS.value + 1)
        )

    # PARAM
    def test_report_model_work_hours_field_should_not_accept_value_exceeding_set_decimal_places_number(self):
        self.field_should_not_accept_input(
            "work_hours",
            generate_decimal_with_decimal_places(decimal_places=ReportModelConstants.DECIMAL_PLACES.value + 1),
        )

    # PARAM
    def test_report_model_work_hours_field_should_not_accept_value_exceeding_set_maximum(self):
        self.field_should_not_accept_input("work_hours", ReportModelConstants.MAX_WORK_HOURS.value + Decimal("0.01"))

    # PARAM
    def test_report_model_work_hours_field_should_not_accept_value_exceeding_set_minimum(self):
        self.field_should_not_accept_input("work_hours", ReportModelConstants.MIN_WORK_HOURS.value - Decimal("0.01"))

    # PARAM
    def test_report_model_work_hours_field_should_not_accept_decimal_value_exceeding_set_maximum(self):
        self.field_should_not_accept_input(
            "work_hours", ReportModelConstants.MAX_WORK_HOURS_DECIMAL_VALUE.value + Decimal("0.01")
        )

    # PARAM
    def test_report_model_work_hours_str_property_should_return_work_hours_field_value_as_string_with_colon_instead_of_dot(
        self
    ):
        report = self.initiate_model("work_hours", Decimal("8.00"))
        self.assertEqual(report.work_hours_str, "8:00")


class TestReportQuerySet(TestCase):
    def setUp(self):
        super().setUp()
        self.date_1 = datetime.datetime.now().date()
        self.date_2 = self.date_1 - datetime.timedelta(days=1)
        ReportFactory(work_hours=Decimal("6.00"), date=self.date_1)
        ReportFactory(work_hours=Decimal("7.00"), date=self.date_1)
        ReportFactory(work_hours=Decimal("5.00"), date=self.date_2)

    def test_get_work_hours_sum_for_all_dates_should_return_dict_with_sum_total_of_work_hours_for_each_day(self):
        result = Report.objects.get_work_hours_sum_for_all_dates()
        self.assertEqual(result[self.date_1], Decimal("13.00"))
        self.assertEqual(result[self.date_2], Decimal("5.00"))


class TestReportTaskActivitiesParameter(DataSetUpToTests):
    def test_report_model_should_accept_correct_input(self):
        self.field_should_accept_input("task_activities", TaskActivityType.objects.get(name="Other"))

    def test_report_model_should_not_accept_incorrect_input(self):
        with self.assertRaises(ValueError):
            self.field_should_not_accept_input("task_activities", self.SAMPLE_STRING_FOR_TYPE_VALIDATION_TESTS)

    def test_report_model_should_be_create_with_default_value(self):
        report = Report()
        self.assertEqual(TaskActivityType.objects.get(name="Other").name, report.task_activities.name)

    def test_that_added_task_activity_must_be_accepted_as_correct_input(self):
        test_activity_type = TaskActivityType(name="test")
        test_activity_type.full_clean()
        test_activity_type.save()
        self.field_should_accept_input("task_activities", TaskActivityType.objects.get(name="test"))
