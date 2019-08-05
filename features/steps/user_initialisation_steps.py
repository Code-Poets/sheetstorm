# pylint: disable=E0102, E0611
from behave import given
from behave import then
from behave import when
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait

from features.fixtures import get_chrome_browser
from features.steps.helpers import cautious_click
from features.steps.helpers import cautious_send_keys
from features.steps.helpers import sign_in
from users.factories import AdminUserFactory


@given("an admin exists in database")
def step_impl(context):
    context.admin = AdminUserFactory()


@when("the user signs up")
def step_impl(context):
    context.username = "jan.kowalski@codepoets.it"
    context.browser.get(context.base_url)
    cautious_click(browser=context.browser, xpath="//*[@id='formFooter']/span[1]/a")
    signup_form = WebDriverWait(context.browser, 10).until(
        expected_conditions.visibility_of_element_located((By.CLASS_NAME, "signup"))
    )
    cautious_send_keys(browser=signup_form, xpath=".//*[@id='id_email']", sequence=context.username)
    password = signup_form.find_element_by_xpath(".//*[@id='id_password']")
    password2 = signup_form.find_element_by_xpath(".//*[@id='id_password2']")
    captcha = signup_form.find_element_by_xpath(".//*[@id='id_captcha_1']")
    password.send_keys("userpasswd")
    password2.send_keys("userpasswd")
    captcha.send_keys("PASSED")
    submit_button = signup_form.find_element_by_xpath(".//input[5]")
    submit_button.click()
    context.browser.find_element_by_link_text("Okay!").click()

    sign_in(context)


@when("admin changes user's employee type to '{user_type}'")
def step_impl(context, user_type):
    other_browser = get_chrome_browser()
    sign_in(context=context, login=context.admin.email, browser=other_browser)
    other_browser.find_element_by_link_text("Employees").click()
    table = other_browser.find_element_by_class_name("table")
    table_headers_count = len(table.find_elements_by_tag_name("th"))
    button = table.find_element_by_xpath(
        f".//td[contains(text(),'{context.username}')]/parent::tr/td[{table_headers_count + 1}]/a"
    )
    button.click()
    user_type_selection = Select(other_browser.find_element_by_name("user_type"))
    user_type_selection.select_by_visible_text(user_type)
    update = other_browser.find_element_by_id("opener_user_account_update")
    update.click()
    confirm = WebDriverWait(other_browser, 10).until(
        expected_conditions.visibility_of_element_located((By.ID, "id_confirm_update_button"))
    )
    confirm.click()

    other_browser.quit()


@then("the user should have '{user_type}' status")
def step_impl(context, user_type):
    context.browser.get(context.base_url)
    sidebar = context.browser.find_element_by_id("sidebar")
    sidebar_header = sidebar.find_element_by_xpath(".//div[@class='sidebar-header']")
    assert user_type in sidebar_header.text


@then("the user should have access to '{page_name}' page")
def step_impl(context, page_name):
    context.browser.get(context.base_url)
    sidebar = context.browser.find_element_by_id("sidebar")
    sidebar_components = sidebar.find_element_by_xpath(".//ul[contains(@class, 'components')]")
    assert page_name in sidebar_components.text
