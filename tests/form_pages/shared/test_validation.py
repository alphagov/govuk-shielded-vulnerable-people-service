import pytest
from unittest.mock import patch

from vulnerable_people_form.form_pages.shared import validation
from flask import Flask
from vulnerable_people_form.form_pages.shared.answers_enums import (
    ApplyingOnOwnBehalfAnswers,
    MedicalConditionsAnswers,
    NHSLetterAnswers,
    ViewOrSetupAnswers,
    YesNoAnswers,
    PrioritySuperMarketDeliveriesAnswers)
from vulnerable_people_form.form_pages.shared.form_utils import sanitise_name, format_postcode

_FORM_ANSWERS_FUNCTION_FULLY_QUALIFIED_NAME = \
    "vulnerable_people_form.form_pages.shared.validation.form_answers"

_current_app = Flask(__name__)
_current_app.secret_key = 'test_secret'

_radio_button_negative_test_data = ["148", 99, "test_invalid_enum_value"]
_yes_no_radio_button_positive_test_data = [e.value for e in YesNoAnswers]


def test_validate_name_should_return_true_when_first_name_and_surname_entered():
    def create_form_answers_with_first_name_and_surname():
        return {
            "name": {"first_name": "jon", "middle_name": "", "last_name": "smith"}
        }

    with patch(
            _FORM_ANSWERS_FUNCTION_FULLY_QUALIFIED_NAME,
            create_form_answers_with_first_name_and_surname), \
            _current_app.test_request_context() as test_request_ctx:
        test_request_ctx.session["form_answers"] = create_form_answers_with_first_name_and_surname()
        is_valid = validation.validate_name()
        assert len(test_request_ctx.session) == 1
        assert is_valid is True


@pytest.mark.parametrize("first_name", ["", " ", "    "])
def test_validate_name_should_return_false_when_only_first_name_entered(first_name):
    def create_form_answers_with_first_name_only():
        return {'name': {'first_name': first_name, 'middle_name': '', 'last_name': ''}}

    with patch(
            _FORM_ANSWERS_FUNCTION_FULLY_QUALIFIED_NAME,
            create_form_answers_with_first_name_only), \
            _current_app.test_request_context() as test_request_ctx:
        test_request_ctx.session["form_answers"] = create_form_answers_with_first_name_only()
        sanitise_name(test_request_ctx.session["form_answers"]["name"])
        is_valid = validation.validate_name()

        assert is_valid is False
        assert len(test_request_ctx.session["error_items"]) == 1
        assert test_request_ctx.session["error_items"]["name"]["last_name"] == "Enter your last name"


def test_validate_name_should_return_false_when_only_last_name_entered():
    def create_form_answers_with_last_name_only():
        return {'name': {'first_name': '', 'middle_name': '', 'last_name': 'Smith'}}

    with patch(
            _FORM_ANSWERS_FUNCTION_FULLY_QUALIFIED_NAME,
            create_form_answers_with_last_name_only), \
            _current_app.test_request_context() as test_request_ctx:
        test_request_ctx.session["form_answers"] = create_form_answers_with_last_name_only()
        is_valid = validation.validate_name()

        assert is_valid is False
        assert len(test_request_ctx.session["error_items"]) == 1
        assert test_request_ctx.session["error_items"]["name"]["first_name"] == "Enter your first name"


@pytest.mark.parametrize("form_field_value", _radio_button_negative_test_data)
def test_validate_applying_on_own_behalf_should_return_false_when_invalid_answer_selected(form_field_value):
    _execute_input_validation_test_and_assert_validation_failed(
        validation.validate_applying_on_own_behalf,
        form_field_value,
        "applying_on_own_behalf",
        "Select if you are using this service for yourself or someone else"
    )


@pytest.mark.parametrize("form_field_value", [e.value for e in ApplyingOnOwnBehalfAnswers])
def test_validate_applying_on_own_behalf_should_return_true_when_valid_answer_selected(form_field_value):
    _execute_input_validation_test_and_assert_validation_passed(
        validation.validate_applying_on_own_behalf,
        form_field_value,
        "applying_on_own_behalf"
    )


@pytest.mark.parametrize("form_field_value", _radio_button_negative_test_data)
def test_validate_nhs_letter_should_return_false_when_invalid_answer_selected(form_field_value):
    _execute_input_validation_test_and_assert_validation_failed(
        validation.validate_nhs_letter,
        form_field_value,
        "nhs_letter",
        "Select if you received the letter from the NHS"
    )


@pytest.mark.parametrize("form_field_value", [e.value for e in NHSLetterAnswers])
def test_validate_nhs_letter_should_return_true_when_valid_answer_selected(form_field_value):
    _execute_input_validation_test_and_assert_validation_passed(
        validation.validate_nhs_letter,
        form_field_value,
        "nhs_letter"
    )


@pytest.mark.parametrize("form_field_value", _radio_button_negative_test_data)
def test_validate_nhs_login_should_return_false_when_invalid_answer_selected(form_field_value):
    _execute_input_validation_test_and_assert_validation_failed(
        validation.validate_nhs_login,
        form_field_value,
        "nhs_login",
        "Select yes if you want log in with you NHS details"
    )


@pytest.mark.parametrize("form_field_value", _yes_no_radio_button_positive_test_data)
def test_validate_nhs_login_should_return_true_when_valid_answer_selected(form_field_value):
    _execute_input_validation_test_and_assert_validation_passed(
        validation.validate_nhs_login,
        form_field_value,
        "nhs_login"
    )


@pytest.mark.parametrize("form_field_value", _radio_button_negative_test_data)
def test_validate_register_with_nhs_should_return_false_when_invalid_answer_selected(form_field_value):
    _populate_request_form_and_execute_input_validation_test_and_assert_validation_failed(
        validation.validate_register_with_nhs,
        form_field_value,
        "nhs_registration",
        "You need to select if you want to register an account with the NHS"
        + " in order to retrieve your answers at a alater point."
    )


@pytest.mark.parametrize("form_field_value", _yes_no_radio_button_positive_test_data)
def test_validate_register_with_nhs_should_return_true_when_valid_answer_selected(form_field_value):
    _populate_request_form_and_execute_input_validation_test_and_assert_validation_passed(
        validation.validate_register_with_nhs,
        form_field_value,
        "nhs_registration"
    )


@pytest.mark.parametrize("form_field_value", [e.value for e in ViewOrSetupAnswers])
def test_validate_view_or_setup_should_return_true_when_valid_answer_selected(form_field_value):
    _populate_request_form_and_execute_input_validation_test_and_assert_validation_passed(
        validation.validate_view_or_setup,
        form_field_value,
        "view_or_setup"
    )


@pytest.mark.parametrize("form_field_value", _radio_button_negative_test_data)
def test_validate_view_or_setup_should_return_false_when_invalid_answer_selected(form_field_value):
    _populate_request_form_and_execute_input_validation_test_and_assert_validation_failed(
        validation.validate_view_or_setup,
        form_field_value,
        "view_or_setup",
        "You must select if you would like to set up an account, or access an account via your NHS Login."
    )


@pytest.mark.parametrize("form_field_value", _radio_button_negative_test_data)
def test_validate_medical_conditions_should_return_false_when_invalid_answer_selected(form_field_value):
    _execute_input_validation_test_and_assert_validation_failed(
        validation.validate_medical_conditions,
        form_field_value,
        "medical_conditions",
        "Select yes if you have one of the medical conditions on the list"
    )


@pytest.mark.parametrize("form_field_value", [e.value for e in MedicalConditionsAnswers])
def test_validate_medical_conditions_should_return_true_when_valid_answer_selected(form_field_value):
    _execute_input_validation_test_and_assert_validation_passed(
        validation.validate_medical_conditions,
        form_field_value,
        "medical_conditions"
    )


@pytest.mark.parametrize("form_field_value", [e.value for e in PrioritySuperMarketDeliveriesAnswers])
def test_validate_priority_supermarket_deliveries_should_return_true_when_valid_answer_selected(form_field_value):
    _execute_input_validation_test_and_assert_validation_passed(
        validation.validate_priority_supermarket_deliveries,
        form_field_value,
        "priority_supermarket_deliveries"
    )


@pytest.mark.parametrize("form_field_value", _radio_button_negative_test_data)
def test_validate_priority_supermarket_deliveries_should_return_false_when_invalid_answer_selected(
        form_field_value):
    _execute_input_validation_test_and_assert_validation_failed(
        validation.validate_priority_supermarket_deliveries,
        form_field_value,
        "priority_supermarket_deliveries",
        "Select if you want priority supermarket deliveries"
    )


@pytest.mark.parametrize("form_field_value", _yes_no_radio_button_positive_test_data)
def test_validate_do_you_have_someone_to_go_shopping_for_you_should_return_true_when_valid_answer_selected(
        form_field_value):
    _execute_input_validation_test_and_assert_validation_passed(
        validation.validate_do_you_have_someone_to_go_shopping_for_you,
        form_field_value,
        "do_you_have_someone_to_go_shopping_for_you"
    )


@pytest.mark.parametrize("form_field_value", _radio_button_negative_test_data)
def test_validate_do_you_have_someone_to_go_shopping_for_you_should_return_false_when_invalid_answer_selected(
        form_field_value):
    _execute_input_validation_test_and_assert_validation_failed(
        validation.validate_do_you_have_someone_to_go_shopping_for_you,
        form_field_value,
        "do_you_have_someone_to_go_shopping_for_you",
        "Select yes if you have someone who can go shopping for you"
    )


@pytest.mark.parametrize("form_field_value", ["", None])
def test_validate_address_lookup_should_return_false_when_no_address_present(form_field_value):
    _populate_request_form_and_execute_input_validation_test_and_assert_validation_failed(
        validation.validate_address_lookup,
        form_field_value,
        "address",
        "You must select an address",
        "address_lookup"
    )


def test_validate_address_lookup_should_return_true_when_address_present():
    _populate_request_form_and_execute_input_validation_test_and_assert_validation_passed(
        validation.validate_address_lookup,
        "{&quot;uprn&quot;: 72277644, &quot;town_city&quot;: &quot;Pudsey&quot;, " +
        "&quot;postcode&quot;: &quot;LS28 8JR&quot;, &quot;building_and_street_line_1&quot;: " +
        "&quot;2 Galloway Lane&quot;, &quot;building_and_street_line_2&quot;: &quot;&quot;}",
        "address"
    )


@pytest.mark.parametrize("postcode", ["LS1 6AE", "EC4A 1EN", "L3 5AB", "NW1W 8XG"])
def test_validate_postcode_should_return_true_when_valid_postcode_present(postcode):
    with _current_app.test_request_context() as test_request_ctx:
        is_valid = validation.validate_postcode(format_postcode(postcode), "postcode")
        assert is_valid is True
        assert len(test_request_ctx.session) == 0


@pytest.mark.parametrize("postcode", ["", " "])
def test_validate_postcode_should_return_false_when_no_postcode_present(postcode):
    with _current_app.test_request_context() as test_request_ctx:
        is_valid = validation.validate_postcode(format_postcode(postcode), "postcode")
        assert is_valid is False
        assert len(test_request_ctx.session) == 1
        assert test_request_ctx.session["error_items"]["postcode"]["postcode"] \
            == "What is the postcode where you need support?"


@pytest.mark.parametrize("postcode", ["invalid_post_code", "ssss 12345", "LS1 1AB ABC", "NE11", "NE11 1LBC"])
def test_validate_postcode_should_return_false_when_invalid_postcode_present(postcode):
    with _current_app.test_request_context() as test_request_ctx:
        is_valid = validation.validate_postcode(format_postcode(postcode), "postcode")
        assert is_valid is False
        assert len(test_request_ctx.session) == 1
        assert test_request_ctx.session["error_items"]["postcode"]["postcode"] == "Enter a real postcode"


@pytest.mark.parametrize("form_field_value", _radio_button_negative_test_data)
def test_validate_basic_care_needs_should_return_false_when_invalid_answer_selected(form_field_value):
    _execute_input_validation_test_and_assert_validation_failed(
        validation.validate_basic_care_needs,
        form_field_value,
        "basic_care_needs",
        "Select yes if your basic care needs are being met at the moment"
    )


@pytest.mark.parametrize("form_field_value", _yes_no_radio_button_positive_test_data)
def test_validate_basic_care_needs_should_return_true_when_valid_answer_selected(form_field_value):
    _execute_input_validation_test_and_assert_validation_passed(
        validation.validate_basic_care_needs,
        form_field_value,
        "basic_care_needs"
    )


@pytest.mark.parametrize("form_field_value", ["", None, "123", "11164324557"])
def test_validate_nhs_number_should_return_false_when_empty_or_invalid_length_nhs_number_entered(
        form_field_value):
    _execute_input_validation_test_and_assert_validation_failed(
        validation.validate_nhs_number,
        form_field_value,
        "nhs_number",
        "Enter your 10-digit NHS number"
    )


@pytest.mark.parametrize("form_field_value", ["1234567891", "abcd123456", "111~643245#5", "123 643245-5"])
def test_validate_nhs_number_should_return_false_when_invalid_nhs_number_entered(form_field_value):
    _execute_input_validation_test_and_assert_validation_failed(
        validation.validate_nhs_number,
        form_field_value,
        "nhs_number",
        "Enter a real NHS number"
    )


def test_validate_nhs_number_should_return_true_when_valid_nhs_number_entered():
    _execute_input_validation_test_and_assert_validation_passed(
        validation.validate_nhs_number,
        "9686368604",
        "nhs_number"
    )


@pytest.mark.parametrize("form_field_value, expected_error_msg", [
    ("sfsdf-sfdsfsd", "Enter an email address in the correct format, like name@example.com"),
    ("invalid@email", "Enter an email address in the correct format, like name@example.com")])
def test_validate_email_if_present_should_return_false_when_invalid_email_entered(form_field_value, expected_error_msg):
    def create_form_answers():
        return {"contact_details": {"email": form_field_value}}

    with patch(
            _FORM_ANSWERS_FUNCTION_FULLY_QUALIFIED_NAME,
            create_form_answers), \
            _current_app.test_request_context() as test_request_ctx:
        is_valid = validation.validate_email_if_present("contact_details", "email")

        _make_validation_failure_assertions(
            is_valid,
            test_request_ctx.session,
            "email",
            expected_error_msg,
            "contact_details")


def test_validate_email_if_present_should_return_true_when_valid_email_entered():
    def create_form_answers():
        return {"contact_details": {"email": "my-valid.email@gmail.com"}}

    with patch(
            _FORM_ANSWERS_FUNCTION_FULLY_QUALIFIED_NAME,
            create_form_answers), \
            _current_app.test_request_context() as test_request_ctx:
        is_valid = validation.validate_email_if_present("contact_details", "email")

        assert is_valid is True
        assert len(test_request_ctx.session) == 0


def test_validate_email_if_present_should_return_true_when_no_email_entered():
    def create_form_answers():
        return {"contact_details": {"email": ""}}

    with patch(
            _FORM_ANSWERS_FUNCTION_FULLY_QUALIFIED_NAME,
            create_form_answers), \
            _current_app.test_request_context() as test_request_ctx:
        is_valid = validation.validate_email_if_present("contact_details", "email")

        assert is_valid is True
        assert len(test_request_ctx.session) == 0


@pytest.mark.parametrize("form_field", [None, ""])
def test_validate_phone_number_if_present_should_return_true_when_no_email_entered(form_field):
    def create_form_answers():
        return {"contact_details": {"phone_number_calls": ""}}

    with patch(
            _FORM_ANSWERS_FUNCTION_FULLY_QUALIFIED_NAME,
            create_form_answers), \
            _current_app.test_request_context() as test_request_ctx:
        is_valid = validation.validate_phone_number_if_present("contact_details", "phone_number_calls")

        assert is_valid is True
        assert len(test_request_ctx.session) == 0


@pytest.mark.parametrize("form_field_value", _yes_no_radio_button_positive_test_data)
def test_validate_do_you_live_in_england_return_true_when_valid_answer_selected(
        form_field_value):
    _execute_input_validation_test_and_assert_validation_passed(
        validation.validate_do_you_live_in_england,
        form_field_value,
        "do_you_live_in_england"
    )


@pytest.mark.parametrize("form_field_value", _radio_button_negative_test_data)
def test_validate_do_you_live_in_england_should_return_false_when_invalid_answer_selected(
        form_field_value):
    _execute_input_validation_test_and_assert_validation_failed(
        validation.validate_do_you_live_in_england,
        form_field_value,
        "do_you_live_in_england",
        "Select yes if you live in England"
    )


@pytest.mark.parametrize("form_field_value, expected_error_msg", [
    ({"day": "12", "month": "12", "year": "12"}, "Enter a real date of birth"),
    ({"day": "", "month": "", "year": ""}, "Enter your date of birth"),
    ({"day": "", "month": "", "year": "1978"}, "Enter your date of birth and include a day, month and a year"),
    ({"day": "df", "month": "sb", "year": "1971"}, "Enter month as a number"),
    ({"day": "df", "month": "10", "year": "1971"}, "Enter day as a number"),
    ({"day": "-1", "month": "09", "year": "1974"}, "Enter a real day"),
    ({"day": "15", "month": "0", "year": "1981"}, "Enter a real month"),
    ({"day": "156", "month": "03", "year": "1981"}, "Enter a day with the correct amount of digits"),
    ({"day": "12", "month": "010", "year": "1982"}, "Enter a month with the correct amount of digits"),
])
def test_validate_date_of_birth_should_return_false_when_an_invalid_date_of_birth_is_entered(
        form_field_value, expected_error_msg):
    _execute_input_validation_test_and_assert_validation_failed(
        validation.validate_date_of_birth,
        form_field_value,
        "date_of_birth",
        expected_error_msg
    )


@pytest.mark.parametrize("form_field_value",
                         [{"day": "12", "month": "12", "year": "1987"}, {"day": 8, "month": 5, "year": 2006}])
def test_validate_date_of_birth_should_return_true_when_a_valid_date_of_birth_is_provided(
        form_field_value):
    _execute_input_validation_test_and_assert_validation_passed(
        validation.validate_date_of_birth,
        form_field_value,
        "date_of_birth"
    )


def test_validate_support_address_should_return_true_when_a_valid_address_is_provided():
    with _current_app.test_request_context() as test_request_ctx:
        test_request_ctx.session["form_answers"] = {
            "support_address": {
                "building_and_street_line_1": "123 Test Avenue",
                "building_and_street_line_2": "",
                "town_city": "Leeds",
                "postcode": "LS11BA"
            }
        }
        is_valid = validation.validate_support_address()

        assert is_valid is True
        assert "error_items" not in test_request_ctx.session


@pytest.mark.parametrize("test_case_support_address, field_error_messages", [
    ({
        "building_and_street_line_1": "",
        "building_and_street_line_2": "",
        "town_city": "",
        "postcode": ""
     },
     [{"form_field": "building_and_street_line_1", "expected_error_msg": "Enter a building and street"},
      {"form_field": "town_city", "expected_error_msg": "Enter a town or city"},
      {"form_field": "postcode", "expected_error_msg": "What is the postcode where you need support?"}]),
    ({
        "building_and_street_line_1": "address line one too long address line one too long  address line one too long address line one too long address line one too long, address line one too long address line one too long  address line one too long address line one too long address line one too long,addr ",  # noqa
        "building_and_street_line_2": "address line two too long address line two too long address line two too long address line two too long address line two too long address line one too long address line one too long  address line one too long address line one too long address line one too long ad",  # noqa
        "town_city": "town / city too long town / city too long town / city too long town / city too long town / city too long ",  # noqa
        "postcode": "LS11BA"
     },
     [{
         "form_field": "building_and_street_line_1",
         "expected_error_msg": "'Address line 1' cannot be longer than 110 characters"
      },
      {
         "form_field": "building_and_street_line_2",
         "expected_error_msg": "'Address line 2' cannot be longer than 210 characters"
      },
      {"form_field": "town_city", "expected_error_msg": "'Town or city' cannot be longer than 50 characters"}])
])
def test_validate_support_address_should_return_false_when_an_invalid_address_is_provided(
 test_case_support_address, field_error_messages
):
    with _current_app.test_request_context() as test_request_ctx:
        test_request_ctx.session["form_answers"] = {
            "support_address": test_case_support_address
        }
        is_valid = validation.validate_support_address()

        assert is_valid is False
        assert "error_items" in test_request_ctx.session
        for field_error_message in field_error_messages:
            assert test_request_ctx.session["error_items"]["support_address"][field_error_message["form_field"]] \
                   == field_error_message["expected_error_msg"]


def _populate_request_form_and_execute_input_validation_test_and_assert_validation_failed(
        validation_function, form_field_value, form_field, validation_error_msg, session_error_items_key=None):
    with _current_app.test_request_context(
            "any-test-url",
            data={form_field: form_field_value}) as test_request_ctx:
        is_valid = validation_function()
        _make_validation_failure_assertions(is_valid, test_request_ctx.session,
                                            form_field, validation_error_msg, session_error_items_key)


def _populate_request_form_and_execute_input_validation_test_and_assert_validation_passed(
        validation_function, form_field_value, form_field):
    with _current_app.test_request_context(
            "any-test-url",
            data={form_field: form_field_value}) as test_request_ctx:
        is_valid = validation_function()

        assert is_valid is True
        assert len(test_request_ctx.session) == 0


def _execute_input_validation_test_and_assert_validation_passed(validation_function, form_field_value, form_field):
    def create_form_answers():
        return {form_field: form_field_value}

    with patch(
            _FORM_ANSWERS_FUNCTION_FULLY_QUALIFIED_NAME,
            create_form_answers), \
            _current_app.test_request_context() as test_request_ctx:
        is_valid = validation_function()

        assert is_valid is True
        assert len(test_request_ctx.session) == 0


def _execute_input_validation_test_and_assert_validation_failed(validation_function, form_field_value, form_field,
                                                                validation_error_msg, session_error_items_key=None):
    def create_form_answers():
        return {} if form_field_value is None else {form_field: form_field_value}

    with patch(
            _FORM_ANSWERS_FUNCTION_FULLY_QUALIFIED_NAME,
            create_form_answers), \
            _current_app.test_request_context() as test_request_ctx:
        is_valid = validation_function()

        _make_validation_failure_assertions(is_valid, test_request_ctx.session,
                                            form_field, validation_error_msg, session_error_items_key)


def _make_validation_failure_assertions(is_valid, session, form_field,
                                        validation_error_msg, session_error_items_key=None):
    assert is_valid is False
    assert len(session["error_items"]) == 1
    error_items_key = session_error_items_key if session_error_items_key else form_field
    assert session["error_items"][error_items_key][form_field] == validation_error_msg
