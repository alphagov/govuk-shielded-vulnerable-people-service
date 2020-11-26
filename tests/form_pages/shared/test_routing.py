import pytest

from unittest.mock import patch, MagicMock
from flask import Flask

from vulnerable_people_form.form_pages.shared.answers_enums import ApplyingOnOwnBehalfAnswers, YesNoAnswers, \
    MedicalConditionsAnswers, NHSLetterAnswers, ShoppingAssistanceAnswers
from vulnerable_people_form.form_pages.shared.constants import SESSION_KEY_POSTCODE_TIER, PostcodeTier, \
    PostcodeTierStatus
from vulnerable_people_form.form_pages.shared.routing import route_to_next_form_page, get_back_url_for_contact_details,\
    get_redirect_for_returning_user_based_on_tier

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
_current_app.is_tiering_logic_enabled = False


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


@pytest.mark.parametrize("current_form_url, expected_redirect_location, get_postcode_tier_return_value, form_answers",
                         [("/postcode-eligibility", "/nhs-letter", PostcodeTier.VERY_HIGH_PLUS_SHIELDING.value, {}),
                          ("/postcode-eligibility", "/nhs-letter", PostcodeTier.VERY_HIGH.value, {}),
                          ("/postcode-eligibility", "/not-eligible-postcode", PostcodeTier.HIGH.value, {}),
                          ("/postcode-eligibility", "/not-eligible-postcode", None, {}),
                          ("/priority-supermarket-deliveries",
                           "/basic-care-needs",
                           PostcodeTier.VERY_HIGH_PLUS_SHIELDING.value,
                           {}),
                          ("/priority-supermarket-deliveries",
                           "/contact-details",
                           PostcodeTier.VERY_HIGH.value,
                           {}),
                          ("/do-you-have-someone-to-go-shopping-for-you",
                           "/priority-supermarket-deliveries",
                           PostcodeTier.VERY_HIGH_PLUS_SHIELDING.value,
                           {"do_you_have_someone_to_go_shopping_for_you": ShoppingAssistanceAnswers.NO.value}),
                          ("/do-you-have-someone-to-go-shopping-for-you",
                           "/basic-care-needs",
                           PostcodeTier.VERY_HIGH_PLUS_SHIELDING.value,
                           {"do_you_have_someone_to_go_shopping_for_you": ShoppingAssistanceAnswers.YES.value}),
                          ("/do-you-have-someone-to-go-shopping-for-you",
                           "/contact-details",
                           PostcodeTier.VERY_HIGH.value,
                           {"do_you_have_someone_to_go_shopping_for_you": ShoppingAssistanceAnswers.YES.value})])
def test_route_to_next_form_page_redirects_to_expected_page_with_tiering_logic(
        current_form_url, expected_redirect_location, get_postcode_tier_return_value, form_answers):
    with _current_app.app_context(), \
         _current_app.test_request_context() as test_request_ctx, \
         patch(_ROUTING_FORM_ANSWERS_FUNCTION_FULLY_QUALIFIED_NAME, return_value=form_answers):
        try:
            _current_app.is_tiering_logic_enabled = True
            test_request_ctx.session[SESSION_KEY_POSTCODE_TIER] = get_postcode_tier_return_value
            test_request_ctx.request.url_rule = _create_mock_url_rule(current_form_url)
            routing_result = route_to_next_form_page()
            assert routing_result is not None
            assert routing_result.headers["location"] == expected_redirect_location
        finally:
            _current_app.is_tiering_logic_enabled = False


@pytest.mark.parametrize("current_form_url, expected_redirect_location, get_postcode_tier_return_value, form_answers",
                         [("/priority-supermarket-deliveries",
                           "/basic-care-needs",
                           PostcodeTier.MEDIUM.value,
                           {}),
                          ("/priority-supermarket-deliveries",
                           "/basic-care-needs",
                           PostcodeTier.HIGH.value,
                           {}),
                          ("/do-you-have-someone-to-go-shopping-for-you",
                           "/basic-care-needs",
                           PostcodeTier.MEDIUM.value,
                           {"do_you_have_someone_to_go_shopping_for_you": ShoppingAssistanceAnswers.YES.value}),
                          ("/do-you-have-someone-to-go-shopping-for-you",
                           "/basic-care-needs",
                           PostcodeTier.HIGH.value,
                           {"do_you_have_someone_to_go_shopping_for_you": ShoppingAssistanceAnswers.YES.value})
                          ])
def test_route_to_next_form_page_raises_a_value_error_when_tiering_logic_enabled_and_invalid_postcode_tier_present(
      current_form_url, expected_redirect_location, get_postcode_tier_return_value, form_answers):
    with _current_app.app_context(), \
         _current_app.test_request_context() as test_request_ctx, \
         patch(_ROUTING_FORM_ANSWERS_FUNCTION_FULLY_QUALIFIED_NAME, return_value=form_answers):
        try:
            _current_app.is_tiering_logic_enabled = True
            test_request_ctx.session[SESSION_KEY_POSTCODE_TIER] = get_postcode_tier_return_value
            test_request_ctx.request.url_rule = _create_mock_url_rule(current_form_url)
            with pytest.raises(ValueError) as err_info:
                route_to_next_form_page()
            assert str(err_info.value) == f"Unexpected postcode tier value encountered: {get_postcode_tier_return_value}"  # noqa
        finally:
            _current_app.is_tiering_logic_enabled = False


def test_get_back_url_for_contact_details_should_return_basic_care_needs_when_tiering_logic_disabled():
    with _current_app.app_context(), \
         _current_app.test_request_context():
        back_url = get_back_url_for_contact_details()
        assert back_url == "/basic-care-needs"


def test_get_back_url_for_contact_details_should_raise_value_error_when_tiering_logic_enabled_with_invalid_postcode_tier():  # noqa
    with _current_app.app_context(), \
         _current_app.test_request_context() as test_request_ctx:
        try:
            _current_app.is_tiering_logic_enabled = True
            test_request_ctx.session[SESSION_KEY_POSTCODE_TIER] = PostcodeTier.HIGH.value
            with pytest.raises(ValueError) as err_info:
                get_back_url_for_contact_details()
            assert f"Unexpected postcode tier value encountered: {PostcodeTier.HIGH.value}" == str(err_info.value)
        finally:
            _current_app.is_tiering_logic_enabled = False


def test_get_back_url_for_contact_details_should_return_basic_care_needs_when_tiering_logic_enabled_with_v_high_plus_shielding_tier():  # noqa
    with _current_app.app_context(), \
         _current_app.test_request_context() as test_request_ctx:
        try:
            _current_app.is_tiering_logic_enabled = True
            test_request_ctx.session[SESSION_KEY_POSTCODE_TIER] = PostcodeTier.VERY_HIGH_PLUS_SHIELDING.value
            back_url = get_back_url_for_contact_details()
            assert back_url == "/basic-care-needs"
        finally:
            _current_app.is_tiering_logic_enabled = False


@pytest.mark.parametrize("shopping_question_answer, expected_back_url",
                         [(ShoppingAssistanceAnswers.NO.value, "/priority-supermarket-deliveries"),
                          (ShoppingAssistanceAnswers.YES.value, "/do-you-have-someone-to-go-shopping-for-you")])
def test_get_back_url_for_contact_details_should_return_correct_url_when_tiering_logic_enabled_with_v_high_tier(
        shopping_question_answer, expected_back_url):
    with _current_app.app_context(),\
         _current_app.test_request_context() as test_request_ctx, \
         patch(_ROUTING_FORM_ANSWERS_FUNCTION_FULLY_QUALIFIED_NAME,
               return_value={"do_you_have_someone_to_go_shopping_for_you": shopping_question_answer}):
        try:
            _current_app.is_tiering_logic_enabled = True
            test_request_ctx.session[SESSION_KEY_POSTCODE_TIER] = PostcodeTier.VERY_HIGH.value
            back_url = get_back_url_for_contact_details()
            assert back_url == expected_back_url
        finally:
            _current_app.is_tiering_logic_enabled = False


@pytest.mark.parametrize("original_postcode_tier, get_latest_postcode_tier_return_value, expected_redirect_url",
                         [(PostcodeTier.VERY_HIGH, None, "/not-eligible-postcode-returning-user-tier-not-found"),
                          (PostcodeTier.VERY_HIGH,
                           {
                               "latest_postcode_tier": PostcodeTier.VERY_HIGH_PLUS_SHIELDING.value,
                               "change_status": PostcodeTierStatus.INCREASED.value
                           },
                          "/basic-care-needs"),
                          (PostcodeTier.VERY_HIGH,
                           {
                               "latest_postcode_tier": PostcodeTier.VERY_HIGH.value,
                               "change_status": PostcodeTierStatus.NO_CHANGE.value
                           },
                           "/view-answers"),
                          (PostcodeTier.VERY_HIGH,
                           {
                               "latest_postcode_tier": PostcodeTier.HIGH.value,
                               "change_status": PostcodeTierStatus.DECREASED.value
                           },
                           "/not-eligible-postcode-returning-user"),
                          (PostcodeTier.VERY_HIGH,
                           {
                               "latest_postcode_tier": PostcodeTier.MEDIUM.value,
                               "change_status": PostcodeTierStatus.DECREASED.value
                           },
                           "/not-eligible-postcode-returning-user"),
                          (PostcodeTier.VERY_HIGH_PLUS_SHIELDING,
                           {
                               "latest_postcode_tier": PostcodeTier.VERY_HIGH_PLUS_SHIELDING.value,
                               "change_status": PostcodeTierStatus.NO_CHANGE.value
                           },
                           "/view-answers"),
                          (PostcodeTier.VERY_HIGH_PLUS_SHIELDING,
                           {
                               "latest_postcode_tier": PostcodeTier.VERY_HIGH.value,
                               "change_status": PostcodeTierStatus.DECREASED.value
                           },
                           "/view-answers"),
                          (PostcodeTier.VERY_HIGH_PLUS_SHIELDING,
                           {
                               "latest_postcode_tier": PostcodeTier.HIGH.value,
                               "change_status": PostcodeTierStatus.DECREASED.value
                           },
                           "/not-eligible-postcode-returning-user"),
                          (PostcodeTier.VERY_HIGH_PLUS_SHIELDING,
                           {
                               "latest_postcode_tier": PostcodeTier.MEDIUM.value,
                               "change_status": PostcodeTierStatus.DECREASED.value
                           },
                           "/not-eligible-postcode-returning-user")])
def test_get_redirect_for_returning_user_based_on_tier(
        original_postcode_tier, get_latest_postcode_tier_return_value, expected_redirect_url):
    with patch(_ROUTING_FORM_ANSWERS_FUNCTION_FULLY_QUALIFIED_NAME,
               return_value={"support_address": {"postcode": "original_postcode"}}), \
         patch("vulnerable_people_form.form_pages.shared.routing.get_latest_postcode_tier",
               return_value=get_latest_postcode_tier_return_value), \
         _current_app.test_request_context() as test_request_ctx:
        test_request_ctx.session["accessing_saved_answers"] = True
        test_request_ctx.session[SESSION_KEY_POSTCODE_TIER] = original_postcode_tier.value
        response = get_redirect_for_returning_user_based_on_tier()
        assert response.headers["Location"] == expected_redirect_url


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

    with _current_app.app_context(), \
            patch(_ROUTING_FORM_ANSWERS_FUNCTION_FULLY_QUALIFIED_NAME, create_form_answers), \
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
