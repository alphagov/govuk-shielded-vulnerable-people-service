import time
import os

from behave import then, when, given

_BASE_URL = os.environ["WEB_APP_BASE_URL"]


@then('wait "{seconds}" seconds')
def wait_step(context, seconds):
    time.sleep(int(seconds))


@when('you navigate to "{path}"')
def user_path_step(context, path):
    context.browser.get(_BASE_URL + path)


@then('the content of element with selector "{selector}" equals "{title}"')
def content_equals_step(context, selector, title):
    element_content = context.browser.find_element_by_css_selector(selector).text
    assert element_content == title


@given('I am on the "{current_page}" page')
def navigate_to_specified_page_if_necessary(context, current_page):
    current_page_full_url = f"{_BASE_URL}/{current_page}"
    if context.browser.current_url != current_page_full_url:
        context.browser.get(current_page_full_url)


@when('I click the "{css_selector}" element')
def click_element(context, css_selector):
    html_element = context.browser.find_element_by_css_selector(css_selector)
    html_element.click()


@when('I give the "{css_selector}" field the value "{element_value}"')
def set_element_value(context, css_selector, element_value):
    html_element = context.browser.find_element_by_css_selector(css_selector)
    html_element.send_keys(element_value)


@when('I submit the form')
def submit_the_form(context):
    click_element(context, "button[type='Submit']")


@then('I am redirected to the "{expected_page}" page')
def verify_the_current_url_matches_the_expected_url(context, expected_page):
    assert context.browser.current_url == f"{_BASE_URL}/{expected_page}"


@when('I enter the value "{value}" in the field with name "{field_name}"')
def set_field_value_step(context, field_name, value):
    elem = context.browser.find_element_by_name(field_name)
    elem.send_keys(value)
    elem.submit()
    time.sleep(5)


def _get_element_by_css_selector(context, css_selector):
    return context.browser.find_element_by_css_selector(css_selector)
