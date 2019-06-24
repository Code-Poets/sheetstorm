import assertpy
import pytest

from users.templatetags.url_filter_tags import startswith


class TestUrlFilterTag:

    simply_string = "Simply string"

    @pytest.mark.parametrize(
        ("whole_string", "test_value"),
        [(simply_string, simply_string[:4]), (simply_string, simply_string[:8]), (simply_string, simply_string)],
    )  # pylint: disable=no-self-use
    def test_correct_value_always_return_true(self, whole_string, test_value):
        assertpy.assert_that(startswith(whole_string, test_value)).is_equal_to(True)

    @pytest.mark.parametrize(
        ("whole_string", "test_value"),
        [(simply_string, simply_string[4:]), (simply_string, simply_string[8:]), (simply_string, "")],
    )  # pylint: disable=no-self-use
    def test_incorrect_value_always_return_false(self, whole_string, test_value):
        assertpy.assert_that(startswith(whole_string, test_value)).is_equal_to(False)
