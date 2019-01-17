import datetime
from decimal import Decimal

from employees.common.constants import ReportModelConstants
from employees.serializers import ReportSerializer
from managers.models import Project
from users.models import CustomUser
from utils.base_tests import BaseSerializerTestCase
from utils.sample_data_generators import generate_decimal_with_decimal_places
from utils.sample_data_generators import generate_decimal_with_digits


class ReportSerializerTests(BaseSerializerTestCase):

    serializer_class = ReportSerializer

    required_input = {
        'date': datetime.datetime.now().date(),
        'description': 'Some description',
        'author': None,
        'project': None,
        'work_hours': Decimal('8.00'),
    }

    SAMPLE_STRING_FOR_TYPE_VALIDATION_TESTS = 'This is a string'

    def setUp(self):
        author = CustomUser(
            email="testuser@codepoets.it",
            password='newuserpasswd',
            first_name='John',
            last_name='Doe',
            country='PL',
        )
        author.full_clean()
        author.save()

        project = Project(
            name="Test Project",
            start_date=datetime.datetime.now(),
        )
        project.full_clean()
        project.save()

        self.required_input['author'] = author
        self.required_input['project'] = project

    def test_report_serializer_date_field_should_accept_correct_value(self):
        self.field_should_accept_input(field='date', value='2018-11-07')

    def test_report_serializer_description_field_should_accept_correct_value(self):
        self.field_should_accept_input(field='description', value='Example description')

    def test_report_serializer_work_hours_field_should_accept_correct_value(self):
        self.field_should_accept_input(field='work_hours', value=Decimal('8.00'))

    """
    ---------------
    DATE FAIL TESTS
    ---------------
    """
    def test_report_serializer_date_field_should_not_be_empty(self):
        self.field_should_not_accept_null(field='date')

    def test_report_serializer_date_field_should_not_accept_non_date_time_value(self):
        self.field_should_not_accept_input(field='date', value=self.SAMPLE_STRING_FOR_TYPE_VALIDATION_TESTS)

    """
    ----------------------
    DESCRIPTION FAIL TESTS
    ----------------------
    """
    def test_report_serializer_description_field_should_not_accept_string_longer_than_set_limit(self):
        self.field_should_not_accept_input(field='description', value='a' * (ReportModelConstants.MAX_DESCRIPTION_LENGTH.value + 1))

    def test_report_serializer_description_field_should_not_be_empty(self):
        self.field_should_not_accept_null(field='description')

    """
    ---------------------
    WORK HOURS FAIL TESTS
    ---------------------
    """
    def test_report_serializer_work_hours_field_should_not_accept_value_exceeding_set_digits_number(self):
        self.field_should_not_accept_input(field='work_hours', value=generate_decimal_with_digits(digits=ReportModelConstants.MAX_DIGITS.value + 1))

    def test_report_serializer_work_hours_field_should_not_accept_value_exceeding_set_decimal_places_number(self):
        self.field_should_not_accept_input(field='work_hours', value=generate_decimal_with_decimal_places(decimal_places=ReportModelConstants.DECIMAL_PLACES.value + 1))

    def test_report_serializer_work_hours_field_should_not_accept_value_exceeding_set_maximum(self):
        self.field_should_not_accept_input(field='work_hours', value=ReportModelConstants.MAX_WORK_HOURS.value + Decimal('0.01'))

    def test_report_serializer_work_hours_field_should_not_accept_value_exceeding_set_minimum(self):
        self.field_should_not_accept_input(field='work_hours', value=ReportModelConstants.MIN_WORK_HOURS.value - Decimal('0.01'))

    def test_report_serializer_work_hours_field_should_not_accept_decimal_value_exceeding_set_maximum(self):
        self.field_should_not_accept_input(field='work_hours', value=ReportModelConstants.MAX_WORK_HOURS_DECIMAL_VALUE.value + Decimal('0.01'))

    def test_report_serializer_work_hours_should_not_accept_non_numeric_value(self):
        self.field_should_not_accept_input(field='work_hours', value=self.SAMPLE_STRING_FOR_TYPE_VALIDATION_TESTS)

    def test_report_serializer_work_hours_field_should_not_be_empty(self):
        self.field_should_not_accept_null(field='work_hours')
