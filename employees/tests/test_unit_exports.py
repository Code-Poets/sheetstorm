import pytest
from assertpy import assert_that
from markdown import markdown

from employees.common.exports import convert_markdown_html_to_text


@pytest.mark.parametrize(
    "input_, expected_output",
    [
        ("`important_parameter`", "important_parameter"),
        ("**bold**", "bold"),
        ("*italic*", "italic"),
        ("_italic as well_", "italic as well"),
        (
            "This **is** _very important_ `feature`: html_to_text_conversion",
            "This is very important feature: html_to_text_conversion",
        ),
    ],
)
def test_convert_markdown_to_text(input_, expected_output):
    html = markdown(input_)
    output = convert_markdown_html_to_text(html)
    assert_that(output).is_equal_to(expected_output)
