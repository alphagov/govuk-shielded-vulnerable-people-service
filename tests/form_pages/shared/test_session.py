from unittest.mock import patch, MagicMock

import pytest

from flask import Flask

from vulnerable_people_form.form_pages.shared import session
from vulnerable_people_form.form_pages.shared.answers_enums import \
    NHSLetterAnswers, \
    YesNoAnswers, \
    ApplyingOnOwnBehalfAnswers, MedicalConditionsAnswers, PrioritySuperMarketDeliveriesAnswers, BasicCareNeedsAnswers, \
    ShoppingAssistanceAnswers, \
    LiveInEnglandAnswers
from vulnerable_people_form.form_pages.shared.constants import PAGE_TITLES, PostcodeTier, SESSION_KEY_POSTCODE_TIER
from vulnerable_people_form.form_pages.shared.session import \
    is_returning_nhs_login_user_without_basic_care_needs_answer, \
    is_very_high_plus_shielding_without_basic_care_needs_answer, \
    set_form_answers_from_nhs_user_info

_current_app = Flask(__name__)
_current_app.secret_key = 'test_secret'
_current_app.is_tiering_logic_enabled = False


def test_form_answers_should_return_answers_when_present_in_session():
    with _current_app.test_request_context() as test_request_ctx:
        test_request_ctx.session["form_answers"] = {"nhs_letter": NHSLetterAnswers.YES.value}
        form_answers = session.form_answers()

        assert form_answers is not None
        assert form_answers["nhs_letter"] == NHSLetterAnswers.YES.value
        assert len(test_request_ctx.session) == 1


def test_form_answers_should_return_empty_dict_when_answers_present_in_session():
    with _current_app.test_request_context() as test_request_ctx:
        assert len(test_request_ctx.session) == 0
        form_answers = session.form_answers()

        assert form_answers == {}
        assert len(test_request_ctx.session) == 1


def test_accessing_saved_answers_should_return_false_when_no_value_present_in_session():
    with _current_app.test_request_context() as test_request_ctx:
        accessing_saved_answers = session.accessing_saved_answers()

        assert accessing_saved_answers is False
        assert len(test_request_ctx.session) == 0


def test_accessing_saved_answers_should_return_true_when_true_entry_present_in_session():
    with _current_app.test_request_context() as test_request_ctx:
        test_request_ctx.session["accessing_saved_answers"] = True
        accessing_saved_answers = session.accessing_saved_answers()

        assert accessing_saved_answers is True
        assert len(test_request_ctx.session) == 1


def test_is_nhs_login_user_should_return_false_when_no_value_present_in_session():
    with _current_app.test_request_context() as test_request_ctx:
        is_nhs_login_user = session.is_nhs_login_user()

        assert is_nhs_login_user is False
        assert len(test_request_ctx.session) == 0


def test_is_nhs_login_user_should_return_true_when_value_present_in_session():
    with _current_app.test_request_context() as test_request_ctx:
        test_request_ctx.session["nhs_sub"] = "some-value"
        is_nhs_login_user = session.is_nhs_login_user()

        assert is_nhs_login_user is True
        assert len(test_request_ctx.session) == 1


def test_should_contact_gp_should_return_true_when_yes_value_present_in_session():
    with _current_app.test_request_context() as test_request_ctx:
        test_request_ctx.session["form_answers"] = {"nhs_letter": NHSLetterAnswers.YES.value}
        should_contact_gp = session.should_contact_gp()

        assert should_contact_gp is True
        assert len(test_request_ctx.session) == 1


@pytest.mark.parametrize("nhs_letter_form_field_value", [NHSLetterAnswers.NO.value, NHSLetterAnswers.NOT_SURE.value])
def test_should_contact_gp_should_return_false_when_no_or_not_sure_value_present_in_session(
        nhs_letter_form_field_value):
    with _current_app.test_request_context() as test_request_ctx:
        test_request_ctx.session["form_answers"] = {"nhs_letter": nhs_letter_form_field_value}
        should_contact_gp = session.should_contact_gp()

        assert should_contact_gp is False
        assert len(test_request_ctx.session) == 1


@pytest.mark.parametrize("answer_key, expected_answer",
                         [(("live_in_england",), "Yes"), (("name", "first_name"), "Tom")])
def test_get_answer_from_form_should_return_answers_when_correct_answer_key_supplied(answer_key, expected_answer):
    with _current_app.test_request_context() as test_request_ctx:
        test_request_ctx.session["form_answers"] = {
            "live_in_england": "Yes",
            "nhs_login": "No",
            "name": {"first_name": "Tom", "last_name": "Smith"}
        }
        answer = session.get_answer_from_form(answer_key)
        assert answer == expected_answer


def test_get_answer_from_form_should_return_none_when_supplied_key_is_not_present_in_session():
    with _current_app.test_request_context() as test_request_ctx:
        test_request_ctx.session["form_answers"] = {
            "live_in_england": YesNoAnswers.YES.value,
            "nhs_login": "No"
        }
        answer = session.get_answer_from_form(("name", "first_name"))
        assert answer is None


def test_update_session_answers_from_form_for_enum_should_populate_session_when_request_form_data_present():
    with _current_app.test_request_context(
            "any-url",
            data=dict(nhs_letter=NHSLetterAnswers.YES.value)) as test_request_ctx:
        session.update_session_answers_from_form_for_enum()
        assert test_request_ctx.session["form_answers"] is not None
        assert test_request_ctx.session["form_answers"]["nhs_letter"] == NHSLetterAnswers.YES.value


def test_get_errors_from_session_should_return_errors_when_error_items_present_in_session():
    with _current_app.test_request_context() as test_request_ctx:
        test_request_ctx.session["error_items"] = {
            "view_or_setup": {
                "view_or_setup":
                    "You must select if you would like to set up an account, or access an account via your NHS Login."
            }
        }
        error_detail = session.get_errors_from_session("view_or_setup")
        assert error_detail is not None
        assert len(error_detail["error_list"]) > 0
        assert error_detail["answers"] == {}
        assert error_detail["error_messages"]["view_or_setup"]["text"] \
               == "You must select if you would like to set up an account, or access an account via your NHS Login."


def test_get_errors_from_session_should_return_empty_error_object_when_no_error_items_present_in_session():
    with _current_app.test_request_context() as test_request_ctx:
        test_request_ctx.session["error_items"] = {}
        error_detail = session.get_errors_from_session("view_or_setup")
        assert error_detail is not None
        assert error_detail["error_list"] == []
        assert error_detail["answers"] == {}
        assert error_detail["error_messages"] == {}


def test_get_summary_rows_from_form_answers_should_return_ordered_summary_rows_for_form_answers_present_in_session():
    with _current_app.test_request_context() as test_request_ctx:
        test_request_ctx.session["form_answers"] = {
            "basic_care_needs": BasicCareNeedsAnswers.YES.value,
            "do_you_have_someone_to_go_shopping_for_you": ShoppingAssistanceAnswers.NO.value,
            "priority_supermarket_deliveries": PrioritySuperMarketDeliveriesAnswers.YES.value,
            "applying_on_own_behalf": ApplyingOnOwnBehalfAnswers.YES.value,
            "nhs_number": "1234567891",
            "contact_details": {"email": "tst_email@gmail.com", "phone_number_calls": "0113 123 4567",
                                "phone_number_texts": "07976 152456"},
            "date_of_birth": {"day": "12", "month": "12", "year": "1980"},
            "name": {"first_name": "Joe", "last_name": "Smith", "middle_name": ""},
            "support_address": {
                "building_and_street_line_1": "1 Test Street",
                "building_and_street_line_2": "address line 2",
                "town_city": "Leeds",
                "postcode": "LS1 1BA"
            }

        }

        summary_rows = session.get_summary_rows_from_form_answers()

        assert len(summary_rows) > 0

        _make_summary_row_assertions(summary_rows[0],
                                     "nhs-number",
                                     "1234567891")

        _make_summary_row_assertions(summary_rows[1],
                                     "name",
                                     "Joe  Smith",
                                     False,
                                     "Name")

        _make_summary_row_assertions(summary_rows[2],
                                     "date-of-birth",
                                     "12/12/1980",
                                     False,
                                     "Date of birth")

        _make_summary_row_assertions(summary_rows[3],
                                     "support-address",
                                     "1 Test Street<br>address line 2<br>Leeds<br>LS1 1BA",
                                     True,
                                     "Address where support is needed",
                                     expected_change_url="/address-lookup")

        _make_summary_row_assertions(summary_rows[4],
                                     "do-you-have-someone-to-go-shopping-for-you",
                                     ShoppingAssistanceAnswers.NO.value_as_text)

        _make_summary_row_assertions(summary_rows[5],
                                     "priority-supermarket-deliveries",
                                     PrioritySuperMarketDeliveriesAnswers.YES.value_as_text)

        _make_summary_row_assertions(summary_rows[6],
                                     "basic-care-needs",
                                     BasicCareNeedsAnswers.YES.value_as_text)

        _make_summary_row_assertions(summary_rows[7],
                                     "contact-details",
                                     "Phone number: 0113 123 4567<br>Text: 07976 152456<br>Email: tst_email@gmail.com",
                                     True,
                                     "Contact details")


def test_persist_answers_from_session():
    with _current_app.app_context(), \
         patch("vulnerable_people_form.form_pages.shared.session.persistence") as mock_persistence, \
         _current_app.test_request_context() as test_request_ctx:
        submission_ref = "submission-reference"
        nhs_sub_value = "nhs-sub-value"
        test_request_ctx.session["postcode_tier"] = PostcodeTier.VERY_HIGH.value
        data_to_persist = {
            "nhs_number": "1234567891",
            "name": {"first_name": "Jon", "middle_name": "", "last_name": "Smith"},
            "date_of_birth": {"day": "10", "month": "11", "year": "1981"},
            "support_address": {
                "building_and_street_line_1": "address line 1",
                "building_and_street_line_2": "address line 2",
                "town_city": "town city",
                "county": "county",
                "postcode": "LS1 1BA",
                "uprn": "uprn"
            },
            "contact_details": {
                "phone_number_calls": "01131234567",
                "phone_number_texts": "07976123456",
                "email": "test-email@gov.uk"
            },
            "applying_on_own_behalf": ApplyingOnOwnBehalfAnswers.YES.value,
            "priority_supermarket_deliveries": PrioritySuperMarketDeliveriesAnswers.NO.value,
            "do_you_have_someone_to_go_shopping_for_you": YesNoAnswers.NO.value,
            "nhs_letter": NHSLetterAnswers.YES.value,
            "basic_care_needs": YesNoAnswers.NO.value,
            "medical_conditions": MedicalConditionsAnswers.YES.value,
            "do_you_live_in_england": LiveInEnglandAnswers.YES.value,
            "tier_at_submission": PostcodeTier.VERY_HIGH.value,
        }

        test_request_ctx.session["nhs_sub"] = nhs_sub_value
        test_request_ctx.session["form_answers"] = data_to_persist

        mock_persistence.persist_answers = MagicMock(return_value=submission_ref)

        returned_submission_ref = session.persist_answers_from_session()

        mock_persistence.persist_answers.assert_called_with(
            data_to_persist["nhs_number"],
            data_to_persist["name"]["first_name"],
            data_to_persist["name"]["middle_name"],
            data_to_persist["name"]["last_name"],
            data_to_persist["date_of_birth"],
            data_to_persist["support_address"]["building_and_street_line_1"],
            data_to_persist["support_address"]["building_and_street_line_2"],
            data_to_persist["support_address"]["town_city"],
            data_to_persist["support_address"]["postcode"],
            data_to_persist["support_address"]["uprn"],
            data_to_persist["contact_details"]["phone_number_calls"],
            data_to_persist["contact_details"]["phone_number_texts"],
            data_to_persist["contact_details"]["email"],
            nhs_sub_value,
            data_to_persist["applying_on_own_behalf"],
            data_to_persist["nhs_letter"],
            data_to_persist["priority_supermarket_deliveries"],
            data_to_persist["basic_care_needs"],
            data_to_persist["do_you_have_someone_to_go_shopping_for_you"],
            data_to_persist["medical_conditions"],
            data_to_persist["do_you_live_in_england"],
            data_to_persist["tier_at_submission"],
        )

        assert test_request_ctx.session["form_uid"] == submission_ref
        assert returned_submission_ref == submission_ref


@pytest.mark.parametrize("is_nhs_login_user, accessing_saved_answers, basic_care_needs_answer, expected_return_value",
                         [(True, True, None, True),
                          (False, True, 1, False),
                          (True, False, 1, False),
                          (True, True, 1, False)])
def test_is_returning_nhs_login_user_without_basic_care_needs_answer_should_return_correct_value(
        is_nhs_login_user, accessing_saved_answers, basic_care_needs_answer, expected_return_value
):
    with _current_app.app_context(), \
         _current_app.test_request_context() as test_request_ctx:
        test_request_ctx.session["accessing_saved_answers"] = accessing_saved_answers
        test_request_ctx.session["nhs_sub"] = "nhs_sub_value" if is_nhs_login_user else None
        test_request_ctx.session["form_answers"] = {"basic_care_needs": basic_care_needs_answer}
        test_request_ctx.session[SESSION_KEY_POSTCODE_TIER] = PostcodeTier.VERY_HIGH_PLUS_SHIELDING.value
        output = is_returning_nhs_login_user_without_basic_care_needs_answer()
        assert output == expected_return_value


@pytest.mark.parametrize("postcode_tier, basic_care_needs_answer, expected_return_value",
                         [(PostcodeTier.VERY_HIGH_PLUS_SHIELDING, None, True),
                          (PostcodeTier.VERY_HIGH_PLUS_SHIELDING, 1, False),
                          (PostcodeTier.VERY_HIGH, None, False)])
def test_is_very_high_plus_shielding_without_basic_care_needs_answer_should_return_correct_value(
        postcode_tier, basic_care_needs_answer, expected_return_value
):
    with _current_app.app_context(), \
         _current_app.test_request_context() as test_request_ctx:
        test_request_ctx.session["form_answers"] = {"basic_care_needs": basic_care_needs_answer}
        test_request_ctx.session[SESSION_KEY_POSTCODE_TIER] = postcode_tier.value
        output = is_very_high_plus_shielding_without_basic_care_needs_answer()
        assert output == expected_return_value


@pytest.mark.parametrize("nhs_number, expected_return_value",
                         [("123-123-1234", "1231231234"),
                          ("123 123 1234", "1231231234"), (" 123456 1234 ", "1234561234")])
def test_set_form_answers_from_nhs_user_info_should_only_format_nhs_number(nhs_number, expected_return_value):
    with _current_app.test_request_context() as test_request_ctx:
        test_request_ctx.session["form_answers"] = {}
        set_form_answers_from_nhs_user_info({"nhs_number": nhs_number})
        assert test_request_ctx.session["form_answers"]["nhs_number"] == expected_return_value


def test_set_form_answers_from_nhs_user_info_should_not_format_other_values():
    user_info = {
        "sub": "00c4a4c1-6b20-4864-826a-e048f706670d",
        "family_name": 'CARTHY',
        "email": "test@nhs.net",
        "phone_number": "+447839395989",
        "nhs_number": "1234567899"
    }
    with _current_app.test_request_context() as test_request_ctx:
        test_request_ctx.session["form_answers"] = {}
        set_form_answers_from_nhs_user_info(user_info)
        assert test_request_ctx.session["form_answers"]["contact_details"]["email"] == user_info["email"]
        assert test_request_ctx.session["form_answers"]["name"]["last_name"] == user_info["family_name"]
        assert test_request_ctx.session["form_answers"]["contact_details"]["phone_number_calls"] == user_info["phone_number"] # noqa


def _make_summary_row_assertions(summary_row,
                                 key,
                                 expected_value,
                                 is_html=False,
                                 expected_text=None,
                                 expected_change_url=None):
    assert summary_row["key"]["text"] == (PAGE_TITLES[key] if expected_text is None else expected_text)
    assert summary_row["value"]["html" if is_html else "text"] == expected_value
    assert summary_row["actions"]["items"][0]["href"] == f"{expected_change_url}?ca=1" if expected_change_url \
        else f"/{key}?ca=1"
