from time import sleep

from django.conf import settings
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

CAUTIOUS_ACTION_TIMEOUT = settings.DEFAULT_TIMEOUT_FOR_FAILED_INTERACTION
CAUTIOUS_ACTION_ITERATIONS = settings.DEFAULT_ITERATIONS_FOR_FAILED_INTERACTION


def sign_in(context, login=None, browser=None):
    if login is None:
        login = context.username
    if browser is None:
        browser = context.browser
    browser.get(context.base_url)
    login_form = WebDriverWait(browser, 10).until(
        expected_conditions.visibility_of_element_located((By.CLASS_NAME, "login"))
    )
    cautious_send_keys(browser=login_form, xpath=".//input[@id='username']", sequence=login)
    password = login_form.find_element_by_xpath(".//input[@id='password']")
    password.send_keys("userpasswd")
    submit_button = login_form.find_element_by_xpath(".//input[@type='submit']")
    submit_button.click()


def cautious_click(browser, xpath, iterations=CAUTIOUS_ACTION_ITERATIONS, timeout=CAUTIOUS_ACTION_TIMEOUT):
    cautious_action(browser, xpath, "click", ElementClickInterceptedException, iterations=iterations, timeout=timeout)


def cautious_send_keys(
    browser, xpath, sequence, iterations=CAUTIOUS_ACTION_ITERATIONS, timeout=CAUTIOUS_ACTION_TIMEOUT
):
    cautious_action(
        browser, xpath, "send_keys", ElementNotInteractableException, sequence, iterations=iterations, timeout=timeout
    )


def cautious_action(
    browser,
    xpath,
    action,
    expected_exception,
    *args,
    iterations=CAUTIOUS_ACTION_ITERATIONS,
    timeout=CAUTIOUS_ACTION_TIMEOUT,
    **kwargs
):
    received_exception = None
    while iterations > 0:
        try:
            element = browser.find_element_by_xpath(xpath)
            sleep(timeout)
            getattr(element, action)(*args, **kwargs)
            break
        except expected_exception as error:
            received_exception = error
            iterations -= 1
    else:
        raise received_exception
