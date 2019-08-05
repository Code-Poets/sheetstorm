# pylint: disable=W0601, W0613
from behave import use_fixture

from features.fixtures import selenium_browser


def before_scenario(context, _scenario):
    use_fixture(selenium_browser, context)
