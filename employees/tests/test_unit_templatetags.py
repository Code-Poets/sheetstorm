from datetime import timedelta

import pytest
from assertpy import assert_that
from django.db.models.functions import datetime
from django.test import TestCase

from employees.templatetags.data_display_filters import duration_field_to_string
from employees.templatetags.data_display_filters import extract_year_and_month_from_url
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
        self.assertEqual(duration_field_to_string(timedelta(hours=8)), "08:00")


class TestExtractionTag:
    @pytest.mark.parametrize(
        ("url", "date"),
        [
            ("/felicita/felicita/felicita/felicita/2019/4", ["2019", "4"]),
            ("/mamma/mia/mamma/mia/2018/9", ["2018", "9"]),
            ("/kazde/pokolenie/ma/wlasny/2100/1", ["2100", "1"]),
        ],
    )  # pylint: disable=no-self-use
    def test_that_extract_year_and_month_from_url_function_should_correct_extract_year_and_month(self, url, date):
        assert_that(extract_year_and_month_from_url(url)).is_equal_to(date)

    @pytest.mark.parametrize(
        "url",
        [
            "/felicita/felicita/felicita/2019/4/felicita",
            "/mamma/mia/mamma/2018/9/mia",
            "/kazde/pokolenie/ma/2100/1/wlasny",
        ],
    )  # pylint: disable=no-self-use
    def test_that_if_function_get_incorrect_url_should_return_current_year_and_month(self, url):
        assert_that(extract_year_and_month_from_url(url)).is_equal_to(
            [datetime.datetime.now().year, datetime.datetime.now().month]
        )
