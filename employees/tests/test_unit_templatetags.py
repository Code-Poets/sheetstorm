import datetime

from django.test import TestCase

from employees.templatetags.data_display_filters import duration_field_to_string
from employees.templatetags.data_structure_element_selectors import get_key_value


class GetKeyValueTests(TestCase):
    def setUp(self):
        self.dictionary = {"one": 1, "two": 2, "three": 3}

    def test_get_key_value_function_should_return_an_element_of_given_dict_at_given_key(self):
        result = get_key_value(self.dictionary, "two")
        self.assertEqual(result, 2)

    def test_get_key_value_function_should_return_empty_string_on_incorrect_key(self):
        result = get_key_value(self.dictionary, 2)
        self.assertEqual(result, "")


class DurationHoursTests(TestCase):
    def test_that_duration_field_to_string_should_parse_duration_to_string(self):
        self.assertEqual(duration_field_to_string(datetime.timedelta(hours=8)), "08:00")
