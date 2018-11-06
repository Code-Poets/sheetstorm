import datetime
from decimal import Decimal

from employees.common.constants import ReportModelConstants
from employees.models import Report
from managers.models import Project
from users.models import CustomUser
from utils.base_tests import BaseModelTestCase
from utils.base_tests import generate_too_many_decimal_places
from utils.base_tests import generate_too_many_digits


class TestReportModel(BaseModelTestCase):

    model_class = Report
    required_input = {
        'date': datetime.datetime.now().date(),
        'description': 'Some description',
        'author': None,
        'project': None,
        'work_hours': Decimal('8.00'),
    }

    WORK_HOURS_ERROR_MARGIN = Decimal(10 ** -ReportModelConstants.DECIMAL_PLACES.value)
    SAMPLE_STRING_FOR_TYPE_VALIDATION_TESTS = 'This is a string'
    DESCRIPTION_DATA_EXCEEDING_LIMIT = 'a' * (ReportModelConstants.MAX_DESCRIPTION_LENGTH.value + 1)
    WORK_HOURS_DATA_EXCEEDING_MAX_VALUE = ReportModelConstants.MAX_WORK_HOURS.value + WORK_HOURS_ERROR_MARGIN
    WORK_HOURS_DATA_EXCEEDING_MIN_VALUE = ReportModelConstants.MIN_WORK_HOURS.value - WORK_HOURS_ERROR_MARGIN

    WORK_HOURS_DATA_EXCEEDING_DECIMAL_MAX_VALUE = ReportModelConstants.MAX_WORK_HOURS.value - 1 + \
                                                    ReportModelConstants.MAX_WORK_HOURS_DECIMAL_VALUE.value + \
                                                    WORK_HOURS_ERROR_MARGIN
    WORK_HOURS_DATA_EXCEEDING_DIGITS_NUMBER = generate_too_many_digits(ReportModelConstants.MAX_DIGITS.value)
    WORK_HOURS_DATA_EXCEEDING_DECIMAL_PLACES = generate_too_many_decimal_places(
                                                    ReportModelConstants.DECIMAL_PLACES.value)

    def setUp(self):
        self.author = CustomUser(
            email="testuser@example.com",
            password='newuserpasswd',
            first_name='John',
            last_name='Doe',
            country='PL',
        )
        self.author.full_clean()
        self.author.save()

        self.project = Project(
            name="Test Project",
            start_date=datetime.datetime.now(),
        )
        self.project.full_clean()
        self.project.save()

        self.required_input['author'] = self.author
        self.required_input['project'] = self.project

        self.REPORT_MODEL_DATA = self.required_input.copy()

    """
    @pytest.mark.parametrize(('test_date_input'), [
    '2018-10-31',
    '2018-10-01',
    '2018-11-01',
    '2018-11-30',
    ])
    """
    # PARAM
    def test_report_model_save_date_field_should_accept_correct_input(self):
        self.field_should_accept_input('date', datetime.datetime.now().date())

    # PARAM
    def test_report_model_description_field_should_accept_correct_input(self):
        self.field_should_accept_input('description', 'Example')

    # PARAM
    def test_report_model_creation_date_field_should_be_filled_on_save(self):
        self.field_should_have_non_null_default('creation_date')

    # PARAM
    def test_report_model_last_update_field_should_be_filled_on_save(self):
        self.field_should_have_non_null_default('last_update')

    # PARAM
    def test_report_model_author_field_should_accept_correct_input(self):
        self.field_should_accept_input('author', self.author)

    # PARAM
    def test_report_model_project_field_should_accept_correct_input(self):
        self.field_should_accept_input('project', self.project)

    # PARAM
    def test_report_model_work_hours_field_should_accept_correct_input(self):
        self.field_should_accept_input('work_hours', Decimal('8.00'))

    def test_report_model_editable_field_should_have_default_value(self):
        self.field_should_have_non_null_default(field='editable', value=True)

    def test_report_model_last_update_field_should_be_changed_on_update(self):
        self.field_auto_now_test('last_update', 'description', 'Updated')

    """
    ---------------
    DATE FAIL TESTS
    ---------------
    """

    def test_report_model_date_field_should_not_be_empty(self):
        self.field_should_not_accept_null('date')

    # PARAM
    def test_report_model_date_field_should_not_accept_non_date_value(self):
        self.field_should_not_accept_input('date', self.SAMPLE_STRING_FOR_TYPE_VALIDATION_TESTS)

    """
    ----------------------
    DESCRIPTION FAIL TESTS
    ----------------------
    """

    # PARAM
    def test_report_model_description_field_should_not_accept_string_longer_than_set_limit(self):
        self.field_should_not_accept_input('description', self.DESCRIPTION_DATA_EXCEEDING_LIMIT)

    def test_report_model_description_field_should_not_be_empty(self):
        self.field_should_not_accept_null('description')

    """
    ------------------
    PROJECT FAIL TESTS
    ------------------
    """
    # PARAM
    def test_report_model_project_field_should_not_accept_non_model_value(self):
        self.key_should_not_accept_incorrect_input('project', self.SAMPLE_STRING_FOR_TYPE_VALIDATION_TESTS)

    def test_report_model_work_project_field_should_not_be_empty(self):
        self.field_should_not_accept_null('project')

    """
    -----------------
    AUTHOR FAIL TESTS
    -----------------
    """

    # PARAM
    def test_report_model_author_field_should_not_accept_non_model_value(self):
        self.key_should_not_accept_incorrect_input('author', self.SAMPLE_STRING_FOR_TYPE_VALIDATION_TESTS)

    def test_report_model_author_field_should_not_be_empty(self):
        self.field_should_not_accept_null('author')
    """
    ---------------------
    WORK_HOURS FAIL TESTS
    ---------------------
    """

    # PARAM
    def test_report_model_work_hours_field_should_not_accept_non_numeric_value(self):
        self.field_should_not_accept_input('work_hours', self.SAMPLE_STRING_FOR_TYPE_VALIDATION_TESTS)

    def test_report_model_work_hours_field_should_not_be_empty(self):
        self.field_should_not_accept_null('work_hours')

    # PARAM
    def test_report_model_work_hours_field_should_not_accept_value_exceeding_set_digits_number(self):
        self.field_should_not_accept_input('work_hours', self.WORK_HOURS_DATA_EXCEEDING_DIGITS_NUMBER)

    # PARAM
    def test_report_model_work_hours_field_should_not_accept_value_exceeding_set_decimal_places_number(self):
        self.field_should_not_accept_input('work_hours', self.WORK_HOURS_DATA_EXCEEDING_DECIMAL_PLACES)

    # PARAM
    def test_report_model_work_hours_field_should_not_accept_value_exceeding_set_maximum(self):
        self.field_should_not_accept_input('work_hours', self.WORK_HOURS_DATA_EXCEEDING_MAX_VALUE)

    # PARAM
    def test_report_model_work_hours_field_should_not_accept_value_exceeding_set_minimum(self):
        self.field_should_not_accept_input('work_hours', self.WORK_HOURS_DATA_EXCEEDING_MIN_VALUE)

    # PARAM
    def test_report_model_work_hours_field_should_not_accept_decimal_value_exceeding_set_maximum(self):
        self.field_should_not_accept_input('work_hours', self.WORK_HOURS_DATA_EXCEEDING_DECIMAL_MAX_VALUE)
