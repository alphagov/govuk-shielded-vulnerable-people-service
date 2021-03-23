import os
import json

from datetime import datetime
from behave import then, when, given
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
from datetime import date

import re

_BASE_URL = os.environ["WEB_APP_BASE_URL"]
_DEFAULT_TIMEOUT = 30  # in seconds
_POSTCODE_TIER_OVERRIDE = json.loads(os.environ["POSTCODE_TIER_OVERRIDE"])


_NHS_BASE_URL = os.environ["NHS_BASE_URL"]
_NHS_EMAIL = os.environ["NHS_EMAIL"]
_NHS_PASSWORD = os.environ["NHS_PASSWORD"]
_NHS_OTP = os.environ["NHS_OTP"]


def get_url_match(url_pattern):
    def url_match(c):
        return re.match(url_pattern, c.current_url)

    return url_match


@then('I am redirected to the "{next_page_url}" page')
def wait_until_url_present(context, next_page_url):
    WebDriverWait(context.browser, _DEFAULT_TIMEOUT).until(
        expected_conditions.url_to_be(f"{_BASE_URL}/{next_page_url}"))


@then('I am redirected to a page that matches "{next_page_url}"')
def wait_until_url_match(context, next_page_url):
    WebDriverWait(context.browser, _DEFAULT_TIMEOUT).until(get_url_match(
        f".*/{next_page_url}.*"))


@then('I am redirected to the "{next_page_url}" nhs page')
def wait_until_nhs_url_present(context, next_page_url):
    WebDriverWait(context.browser, _DEFAULT_TIMEOUT).until(
        expected_conditions.url_to_be(f"{_NHS_BASE_URL}/{next_page_url}"))


@then('I am redirected to the external page with URL "{next_page_url}"')
def wait_until_external_url_present(context, next_page_url):
    WebDriverWait(context.browser, _DEFAULT_TIMEOUT).until(
        expected_conditions.url_to_be(next_page_url))


@then('wait up to "{timeout_seconds}" seconds until element with selector "{element_css_selector}" is present')
def wait_until_element_present(context, timeout_seconds, element_css_selector):
    WebDriverWait(context.browser, int(timeout_seconds)).until(
        expected_conditions.presence_of_element_located((By.CSS_SELECTOR, element_css_selector)))


@when('I navigate to "{path}"')
def user_path_step(context, path):
    context.browser.get(_BASE_URL + path)


@then('the content of element with selector "{element_css_selector}" equals "{expected_element_content}"')
def assert_element_content_matches(context, element_css_selector, expected_element_content):
    element = WebDriverWait(context.browser, _DEFAULT_TIMEOUT).until(
        expected_conditions.presence_of_element_located((By.CSS_SELECTOR, element_css_selector)))
    assert element.text == expected_element_content


@given('I am on the "{expected_page}" page')
def assert_on_specified_page(context, expected_page):
    assert context.browser.current_url == f"{_BASE_URL}/{expected_page}"


@given('I am on the "{expected_page}" nhs page')
def assert_on_specified_nhs_page(context, expected_page):
    assert context.browser.current_url == f"{_NHS_BASE_URL}/{expected_page}"


@when('I click the "{css_selector}" element')
def click_element(context, css_selector):
    html_element = context.browser.find_element_by_css_selector(css_selector)
    html_element.click()


@when('I give the "{css_selector}" field the value "{element_value}"')
def set_element_value(context, css_selector, element_value):
    html_element = context.browser.find_element_by_css_selector(css_selector)
    html_element.clear()
    html_element.send_keys(element_value)


@when('I give the "{css_selector}" field the nhs email value')
def set_nhs_email_value(context, css_selector):
    html_element = context.browser.find_element_by_css_selector(css_selector)
    html_element.clear()
    html_element.send_keys(_NHS_EMAIL)


@when('I give the "{css_selector}" field the nhs otp value')
def set_nhs_otp_value(context, css_selector):
    html_element = context.browser.find_element_by_css_selector(css_selector)
    html_element.clear()
    html_element.send_keys(_NHS_OTP)


@when('I give the "{css_selector}" field the nhs password value')
def set_nhs_password_value(context, css_selector):
    html_element = context.browser.find_element_by_css_selector(css_selector)
    html_element.clear()
    html_element.send_keys(_NHS_PASSWORD)


@when('I submit the form')
def submit_the_form(context):
    click_element(context, "button[type='Submit']")


@when('I enter the value "{value}" in the field with name "{field_name}"')
def set_field_value_step(context, field_name, value):
    elem = context.browser.find_element_by_name(field_name)
    elem.send_keys(value)
    elem.submit()


@when('I give the "{css_selector}" field the value "{element_value}" appended with todays date')
def set_element_value_appended_with_today_date(context, css_selector, element_value):
    date_stamp = date.today().strftime('%Y-%m-%d')
    element_value_appended = element_value+'_'+date_stamp
    set_element_value(context, css_selector, element_value_appended)


@when('I give the postcode field a tier {tier} postcode')
def set_postcode_value(context, tier):
    postcode = ""
    for key, value in _POSTCODE_TIER_OVERRIDE.items():
        if value["tier"] == int(tier) and value["shielding"] == 0:
            postcode = key

    html_element = context.browser.find_element_by_css_selector("#postcode")
    html_element.clear()
    html_element.send_keys(postcode)


@when('I select the first address')
def select_first_address(context):
    address_select = Select(context.browser.find_element_by_id('address'))
    address_select.select_by_index(1)


@when('I give the postcode field a tier {tier} postcode with shielding')
def set_postcode_value_for_shielding(context, tier):
    postcode = ""
    for key, value in _POSTCODE_TIER_OVERRIDE.items():
        if value["tier"] == int(tier) and value["shielding"] == 1:
            postcode = key

    html_element = context.browser.find_element_by_css_selector("#postcode")
    html_element.clear()
    html_element.send_keys(postcode)


@when('I answer the care needs question differently to last submission')
def click_basic_care_needs_element(context):
    # change the care needs response each day
    new_care_answer = '0' if datetime.now().toordinal() % 2 else '1'
    html_element = context.browser.find_element_by_css_selector(f".govuk-radios__item input[value='{new_care_answer}']")
    html_element.click()
