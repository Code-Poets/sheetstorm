import datetime

import pytest
from assertpy import assertpy
from django.http import HttpRequest
from django.template import Context
from django.template import Template
from django.test import TestCase

from employees.common.strings import MonthNavigationText
from employees.forms import MonthSwitchForm
from employees.views import MonthNavigationMixin


class MonthNavigationMixinCustomMethodsTests(TestCase):
    def setUp(self):
        self.mixin = MonthNavigationMixin()

    def test_get_url_from_date_should_return_url_with_no_pk_if_none_is_provided(self):
        current_date = datetime.datetime.now().date()
        self.mixin.url_name = "custom-report-list"
        self.assertEqual(
            self.mixin._get_url_from_date(current_date, None), f"/reports/{current_date.year}/{current_date.month}/"
        )

    def test_get_title_date_should_return_five_character_string_containing_month_number_separator_and_two_last_digits_of_year_number(
        self
    ):
        self.assertEqual(self.mixin._get_title_date(year=2019, month=4), "04/19")

    def test_get_next_month_url_should_generate_url_for_next_month_for_given_path(self):
        self.mixin.url_name = "project-report-list"
        self.assertEqual(self.mixin._get_next_month_url(2018, 12, 1), "/reports/project/1/2019/1/")

    def test_get_previous_month_url_should_generate_url_for_previous_month_for_given_path(self):
        self.mixin.url_name = "project-report-list"
        self.assertEqual(self.mixin._get_previous_month_url(2019, 1, 1), "/reports/project/1/2018/12/")

    def test_get_recent_month_url_should_generate_url_for_current_month_for_given_path(self):
        current_date = datetime.datetime.now()
        self.mixin.url_name = "project-report-list"
        self.assertEqual(
            self.mixin._get_recent_month_url(1), f"/reports/project/1/{current_date.year}/{current_date.month}/"
        )


class TestDateOutOfBoundsMethod:
    def _test_date_out_of_bounds_method(self, year, month):  # pylint: disable=no-self-use
        mixin = MonthNavigationMixin()
        mixin.kwargs = {"year": year, "month": month}
        return mixin._date_out_of_bounds()

    @pytest.mark.parametrize(("year", "month"), [("2019", "5"), ("2020", "4"), ("2099", "12")])
    def test_date_out_of_bounds_should_return_true_if_selected_date_is_inside_the_defined_scope(self, year, month):
        assertpy.assert_that(self._test_date_out_of_bounds_method(year, month)).is_false()

    @pytest.mark.parametrize(("year", "month"), [("2019", "4"), ("2018", "9"), ("2100", "1")])
    def test_date_out_of_bounds_should_return_false_if_selected_date_is_outside_of_defined_scope(self, year, month):
        assertpy.assert_that(self._test_date_out_of_bounds_method(year, month)).is_true()


class MonthNavigationMixinContextDataTests(TestCase):
    def setUp(self):
        self.mixin = MonthNavigationMixin()
        self.mixin.url_name = "project-report-list"

    def _get_month_navigation_context_data(self, year, month, pk):
        request = HttpRequest()
        request.path = f"/reports/project/{pk}/{year}/{month}/"
        self.mixin.request = request
        self.mixin.kwargs["year"] = year
        self.mixin.kwargs["month"] = month
        self.mixin.kwargs["pk"] = pk
        return Context(self.mixin._get_month_navigator_params())

    def _render_month_navigation_bar(self, year, month, pk):
        context = self._get_month_navigation_context_data(year, month, pk)
        template_to_render = Template("{% include 'employees/month_navigation_bar.html' %}")
        return template_to_render.render(context)

    def test_month_navigator_get_context_data_method_should_return_all_data_necessary_for_month_navigator_template(
        self
    ):
        context = self._get_month_navigation_context_data(2019, 3, 1)
        current_date = datetime.datetime.now()
        expected_output = {
            "path": self.mixin.request.path,
            "navigation_text": MonthNavigationText,
            "month_form": MonthSwitchForm(initial_date=datetime.date(year=2019, month=3, day=1)),
            "next_month_url": "/reports/project/1/2019/4/",
            "recent_month_url": f"/reports/project/1/{current_date.year}/{current_date.month}/",
            "previous_month_url": "/reports/project/1/2019/2/",
            "disable_next_button": False,
            "disable_previous_button": False,
            "title_date": "03/19",
        }
        self.assertEqual(expected_output, context.dicts[1])

    def test_month_navigator_should_render_html_with_links_to_other_months_for_given_url(self):
        rendered_template = self._render_month_navigation_bar(2019, 1, 1)
        current_date = datetime.datetime.now()
        self.assertTrue('<a href="/reports/project/1/2018/12/" class="btn btn-info">' in rendered_template)
        self.assertTrue(
            f'<a href="/reports/project/1/{current_date.year}/{current_date.month}/" class="btn btn-info">'
            in rendered_template
        )
        self.assertTrue('<a href="/reports/project/1/2019/2/" class="btn btn-info">' in rendered_template)

    def test_month_navigator_should_not_render_html_with_link_to_next_month_if_upper_limit_is_met(self):
        rendered_template = self._render_month_navigation_bar(2099, 12, 1)
        current_date = datetime.datetime.now()
        self.assertTrue('<a href="/reports/project/1/2099/11/" class="btn btn-info">' in rendered_template)
        self.assertTrue(
            f'<a href="/reports/project/1/{current_date.year}/{current_date.month}/" class="btn btn-info">'
            in rendered_template
        )
        self.assertFalse('<a href="/reports/project/1/2100/1/" class="btn btn-info">' in rendered_template)

    def test_month_navigator_should_not_render_html_with_link_to_previous_month_if_lower_limit_is_met(self):
        rendered_template = self._render_month_navigation_bar(2019, 5, 1)
        current_date = datetime.datetime.now()
        self.assertTrue('<a href="/reports/project/1/2019/6/" class="btn btn-info">' in rendered_template)
        self.assertTrue(
            f'<a href="/reports/project/1/{current_date.year}/{current_date.month}/" class="btn btn-info">'
            in rendered_template
        )
        self.assertFalse('<a href="/reports/project/1/2000/4/" class="btn btn-info">' in rendered_template)

    def test_month_navigator_should_render_html_with_month_navigation_form_related_to_post_method_under_request_path(
        self
    ):
        rendered_template = self._render_month_navigation_bar(2019, 3, 1)
        self.assertTrue('<form action="/reports/project/1/2019/3/" method="POST">' in rendered_template)

    def test_redirect_to_another_month_method_should_redirect_to_link_with_provided_date(self):
        self.mixin.kwargs["pk"] = 1
        request = HttpRequest()
        request.POST["date"] = "05-2020"
        response = self.mixin.redirect_to_another_month(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/reports/project/1/2020/5/")

    def test_redirect_to_another_month_method_should_redirect_to_request_path_if_provided_date_is_out_of_bonds(self):
        self.mixin.kwargs["pk"] = 1
        request = HttpRequest()
        request.path = "/reports/project/1/2019/3/"
        request.POST["date"] = "04-2019"
        response = self.mixin.redirect_to_another_month(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/reports/project/1/2019/3/")

    def test_redirect_to_current_month_method_should_redirect_to_current_month_section(self):
        current_date = datetime.datetime.now()
        self.mixin.kwargs["pk"] = 1
        response = self.mixin.redirect_to_current_month()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"/reports/project/1/{current_date.year}/{current_date.month}/")
