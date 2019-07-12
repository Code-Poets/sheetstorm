from behave import fixture
from django.conf import settings
from selenium import webdriver


@fixture
def selenium_browser(context):
    context.browser = get_chrome_browser()
    yield context.browser
    context.browser.quit()


def get_chrome_browser():
    options = webdriver.ChromeOptions()
    if settings.HEADLESS_BROWSER_RUN:
        options.add_argument("headless")
    return webdriver.Chrome(chrome_options=options)
