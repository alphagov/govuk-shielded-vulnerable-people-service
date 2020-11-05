import pytest

from unittest.mock import patch, MagicMock
from flask import Flask

from vulnerable_people_form.form_pages.shared.answers_enums import ApplyingOnOwnBehalfAnswers, YesNoAnswers, \
    MedicalConditionsAnswers, NHSLetterAnswers
from vulnerable_people_form.form_pages.shared.routing import route_to_next_form_page

_ROUTING_FORM_ANSWERS_FUNCTION_FULLY_QUALIFIED_NAME = \
    "vulnerable_people_form.form_pages.shared.routing.form_answers"
_VALIDATION_FORM_ANSWERS_FUNCTION_FULLY_QUALIFIED_NAME = \
    "vulnerable_people_form.form_pages.shared.validation.form_answers"
_POSTCODE_ELIGIBILITY_FUNCTION_FULLY_QUALIFIED_NAME = \
    "vulnerable_people_form.form_pages.shared.routing.postcode_eligibility"
_NHS_AUTH_URL = "nhs-auth-url"

_current_app = Flask(__name__)
_current_app.secret_key = 'test_secret'
_current_app.nhs_oidc_client = MagicMock()
_current_app.nhs_oidc_client.get_authorization_url = MagicMock(return_value=_NHS_AUTH_URL)


@pytest.mark.parametrize("current_form_url, expected_redirect_location, form_answers",
                         [("/address-lookup", "/do-you-have-someone-to-go-shopping-for-you", None),
                          ("/applying-on-own-behalf", "/nhs-login",
                           {"applying_on_own_behalf": ApplyingOnOwnBehalfAnswers.YES.value}),
                          ("/applying-on-own-behalf", "/postcode-eligibility",
                           {"applying_on_own_behalf": ApplyingOnOwnBehalfAnswers.NO.value}),
                          ("/nhs-login", "/nhs-login-link", {"nhs_login": YesNoAnswers.YES.value}),
                          ("/nhs-login", "/postcode-eligibility", {"nhs_login": YesNoAnswers.NO.value}),
                          ("/basic-care-needs", "/contact-details", None),
                          ("/check-your-answers", "/confirmation",
                           {"applying_on_own_behalf": 0,
                            "contact_details": {
                               "phone_number_texts": "",
                               "email": "e@mail.com"}
                            }),
                          ("/check-your-answers", "/confirmation",
                           {"applying_on_own_behalf": 0,
                            "contact_details": {
                                "email": "",
                                "phone_number_texts": "07976123456"}
                            }),
                          ("/check-your-answers", "/nhs-registration",
                           {"applying_on_own_behalf": 0,
                            "contact_details": {
                                "email": "test@email.com",
                                "phone_number_texts": "07976123456"}
                            }),
                          ("check-contact-details", "/check-your-answers", None),
                          ("/do-you-have-someone-to-go-shopping-for-you", "/basic-care-needs",
                           {"do_you_have_someone_to_go_shopping_for_you": YesNoAnswers.YES.value}),
                          ("/do-you-have-someone-to-go-shopping-for-you", "/priority-supermarket-deliveries",
                           {"do_you_have_someone_to_go_shopping_for_you": YesNoAnswers.NO.value}),
                          ("/priority-supermarket-deliveries", "/basic-care-needs", None),
                          ("/medical-conditions",
                           "/nhs-number",
                           {"medical_conditions": MedicalConditionsAnswers.YES.value}),
                          ("/medical-conditions",
                           "/not-eligible-medical",
                           {"medical_conditions": MedicalConditionsAnswers.NO.value}),
                          ("name", "/date-of-birth", None),
                          ("/nhs-letter", "/medical-conditions", {"nhs_letter": NHSLetterAnswers.NO.value}),
                          ("/nhs-letter", "/nhs-number", {"nhs_letter": NHSLetterAnswers.YES.value}),
                          ("nhs-number", "/name", None)])
def test_route_to_next_form_page_redirects_to_expected_page(
        current_form_url, expected_redirect_location, form_answers):
    _execute_routing_test_and_assert_redirect_location_is_correct(
        current_form_url,
        expected_redirect_location,
        {} if form_answers is None else form_answers
    )


@pytest.mark.parametrize("current_form_url, expected_redirect_location, form_answers, session_variables",
                         [("/check-your-answers", "/confirmation", None, {"nhs_sub": "value"}),
                          ("/check-contact-details", "/view-answers", None, {"accessing_saved_answers": True}),
                          ("/basic-care-needs", "/contact-details", None, {"accessing_saved_answers": True}),
                          ("/medical-conditions",
                           "/nhs-number",
                           {"medical_conditions": MedicalConditionsAnswers.YES.value,
                            "name": {"first_name": "Jon", "middle_name": "", "last_name": "Snow"}},
                           {"nhs_sub": "value"}),
                          ("/name",
                           "/address-lookup",
                           {"date_of_birth": {"day": "10", "month": "11", "year": "1981"},
                            "contact_details": {"email": "invalid_email"}},
                           {"nhs_sub": "value"}),
                          ("/name",
                           "/address-lookup",
                           {"date_of_birth": {"day": "10", "month": "11", "year": "1981"},
                            "contact_details": {}},
                           {"nhs_sub": "value"}),
                          ("/nhs-letter",
                           "/nhs-number",
                           {"nhs_letter": NHSLetterAnswers.YES.value,
                            "name": {"first_name": "Jon", "middle_name": "", "last_name": "Snow"},
                            "date_of_birth": {"day": "", "month": "", "year": ""}},
                           {"nhs_sub": "value"})])
def test_route_to_next_form_page_redirects_to_expected_page_with_session_variables_assigned(
        current_form_url, expected_redirect_location, form_answers, session_variables):
    _execute_routing_test_and_assert_redirect_location_is_correct(
        current_form_url,
        expected_redirect_location,
        {} if form_answers is None else form_answers,
        session_variables
    )


@pytest.mark.parametrize("current_form_url, expected_redirect_location, check_postcode_return_value",
                         [("/postcode-eligibility", "/nhs-letter", True),
                          ("/postcode-eligibility", "/do-you-live-in-england", False),
                          ("/postcode-lookup", "/address-lookup", True),
                          ("/postcode-lookup", "/do-you-live-in-england", False),
                          ("/support-address", "/do-you-have-someone-to-go-shopping-for-you", True),
                          ("/support-address", "/do-you-live-in-england", False)])
def test_route_to_next_form_page_redirects_to_expected_page_with_postcode_eligibility_check(
        current_form_url, expected_redirect_location, check_postcode_return_value):
    def create_form_answers():
        return {}

    postcode = "LS1 1AB"

    with patch(_ROUTING_FORM_ANSWERS_FUNCTION_FULLY_QUALIFIED_NAME, create_form_answers), \
            patch(_POSTCODE_ELIGIBILITY_FUNCTION_FULLY_QUALIFIED_NAME) as postcode_eligibility, \
            _current_app.test_request_context() as test_request_ctx:
        test_request_ctx.session["postcode"] = postcode
        test_request_ctx.request.url_rule = _create_mock_url_rule(current_form_url)
        postcode_eligibility.check_postcode = MagicMock(return_value=check_postcode_return_value)

        routing_result = route_to_next_form_page()

        assert routing_result is not None
        assert routing_result.headers["location"] == expected_redirect_location
        postcode_eligibility.check_postcode.assert_called_once_with(postcode)


def _create_mock_url_rule(current_form_url):
    url_rule = MagicMock()
    url_rule.rule = current_form_url
    url_rule.endpoint = "form.any_endpoint"
    return url_rule


def _execute_routing_test_and_assert_redirect_location_is_correct(current_form_url,
                                                                  expected_redirect_location,
                                                                  form_answers=None,
                                                                  session_variables=None):
    def create_form_answers():
        return form_answers

    with patch(_ROUTING_FORM_ANSWERS_FUNCTION_FULLY_QUALIFIED_NAME, create_form_answers), \
            patch(_VALIDATION_FORM_ANSWERS_FUNCTION_FULLY_QUALIFIED_NAME, create_form_answers), \
            patch("vulnerable_people_form.form_pages.shared.routing.persist_answers_from_session"), \
            _current_app.test_request_context() as test_request_ctx:
        test_request_ctx.request.url_rule = _create_mock_url_rule(current_form_url)

        if session_variables:
            for k, v in session_variables.items():
                test_request_ctx.session[k] = v

        routing_result = route_to_next_form_page()

        assert routing_result is not None
        assert routing_result.headers["location"] == expected_redirect_location
