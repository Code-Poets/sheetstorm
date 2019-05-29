import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from employees.common.constants import ReportModelConstants
from employees.common.strings import ReportValidationStrings
from employees.factories import ReportFactory
from employees.models import Report
from employees.models import TaskActivityType
from managers.models import Project
from users.factories import UserFactory
from users.models import CustomUser
from utils.base_tests import BaseModelTestCase


class DataSetUpToTests(BaseModelTestCase):
    model_class = Report
    required_input = {
        "date": datetime.datetime.now().date(),
        "description": "Some description",
        "author": None,
        "project": None,
        "work_hours": datetime.timedelta(hours=8),
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
        self.field_should_accept_input("work_hours", datetime.timedelta(hours=8))

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
    def test_report_model_work_hours_field_should_not_accept_value_exceeding_set_maximum(self):
        self.field_should_not_accept_input(
            "work_hours", ReportModelConstants.MAX_WORK_HOURS.value + datetime.timedelta(hours=25)
        )

    # PARAM
    def test_report_model_work_hours_field_should_not_accept_value_exceeding_set_minimum(self):
        self.field_should_not_accept_input(
            "work_hours", ReportModelConstants.MIN_WORK_HOURS.value - datetime.timedelta(seconds=1)
        )


class TestReportQuerySetWorkHoursSumForAllDates(TestCase):
    def setUp(self):
        super().setUp()
        self.date_1 = datetime.datetime.now().date()
        self.date_2 = self.date_1 - datetime.timedelta(days=1)
        ReportFactory(work_hours=datetime.timedelta(hours=6), date=self.date_1)
        ReportFactory(work_hours=datetime.timedelta(hours=7), date=self.date_1)
        ReportFactory(work_hours=datetime.timedelta(hours=5), date=self.date_2)

    def test_get_work_hours_sum_for_all_dates_should_return_dict_with_sum_total_of_work_hours_for_each_day(self):
        result = Report.objects.get_work_hours_sum_for_all_dates()
        self.assertEqual(result[self.date_1], datetime.timedelta(hours=13))
        self.assertEqual(result[self.date_2], datetime.timedelta(hours=5))


class TestReportWorkHoursSumForGivenDayForSingleUser(TestCase):
    def test_that_work_hours_sum_for_given_day_for_single_user_can_be_24(self):
        user = UserFactory()
        today = timezone.now().date()
        report = ReportFactory(work_hours=datetime.timedelta(hours=23), date=today, author=user)

        new_report = Report(
            work_hours=datetime.timedelta(hours=1), date=today, author=user, project=report.project, description="test"
        )
        new_report.full_clean()
        new_report.save()

        self.assertEqual(user.report_set.get_report_work_hours_sum_for_date(today), datetime.timedelta(hours=24))

    def test_that_work_hours_sum_for_given_day_for_single_user_should_not_exceed_24(self):
        user = UserFactory()
        today = timezone.now().date()
        report = ReportFactory(work_hours=datetime.timedelta(hours=23), date=today, author=user)

        with self.assertRaises(ValidationError) as exception:
            new_report = Report(
                work_hours=datetime.timedelta(hours=2),
                date=today,
                author=user,
                project=report.project,
                description="test",
            )
            new_report.full_clean()

        self.assertEqual(
            exception.exception.messages[0],
            ReportValidationStrings.WORK_HOURS_SUM_FOR_GIVEN_DATE_FOR_SINGLE_AUTHOR_EXCEEDED.value,
        )

    def test_that_editing_report_work_hours_sum_for_given_day_for_single_user_should_not_exceed_24(self):
        user = UserFactory()
        today = timezone.now().date()
        ReportFactory(work_hours=datetime.timedelta(hours=23), date=today, author=user)
        edited_report = ReportFactory(work_hours=datetime.timedelta(hours=1), date=today, author=user)

        with self.assertRaises(ValidationError) as exception:
            edited_report.work_hours = datetime.timedelta(hours=2)
            edited_report.full_clean()

        self.assertEqual(
            exception.exception.messages[0],
            ReportValidationStrings.WORK_HOURS_SUM_FOR_GIVEN_DATE_FOR_SINGLE_AUTHOR_EXCEEDED.value,
        )

    def test_that_edited_report_would_not_be_summed_twice_for_work_hours_sum(self):
        user = UserFactory()
        today = timezone.now().date()
        work_hours = datetime.timedelta(hours=20)
        ReportFactory(work_hours=work_hours, date=today, author=user)
        edited_report = ReportFactory(work_hours=datetime.timedelta(hours=3), date=today, author=user)
        edited_report.work_hours = datetime.timedelta(hours=4)
        edited_report.full_clean()
        edited_report.save()

        self.assertEqual(user.report_set.get_report_work_hours_sum_for_date(today), datetime.timedelta(hours=24))


class TestReportQuerySetWorkHoursSumForAllAuthors(TestCase):
    def setUp(self):
        super().setUp()
        self.author_1 = UserFactory()
        self.author_2 = UserFactory()
        ReportFactory(work_hours=datetime.timedelta(hours=6), author=self.author_1)
        ReportFactory(work_hours=datetime.timedelta(hours=7), author=self.author_2)
        ReportFactory(work_hours=datetime.timedelta(hours=5), author=self.author_2)

    def test_monthly_hours_sum_should_return_dict_with_sum_total_of_all_work_hours_for_each_author(self):
        result = Report.objects.get_work_hours_sum_for_all_authors()
        self.assertEqual(result[self.author_1.pk], datetime.timedelta(hours=6))
        self.assertEqual(result[self.author_2.pk], datetime.timedelta(hours=12))


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
