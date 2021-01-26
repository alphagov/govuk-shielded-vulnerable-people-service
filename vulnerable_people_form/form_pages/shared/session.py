import datetime

from flask import request, session

from .answers_enums import (
    NHSLetterAnswers,
    PrioritySuperMarketDeliveriesAnswers,
    ShoppingAssistanceAnswers,
    BasicCareNeedsAnswers
)
from .constants import (
    PAGE_TITLES,
    NHS_USER_INFO_TO_FORM_ANSWERS,
    SESSION_KEY_LOCATION_TIER,
    SESSION_KEY_SHIELDING_ADVICE,
    SESSION_KEY_IS_POSTCODE_IN_ENGLAND,
    PostcodeTier,
    ShieldingAdvice
)
from .form_utils import clean_nhs_number, postcode_with_spaces
from .querystring_utils import append_querystring_params
from .security import sanitise_input

from ...integrations import persistence


def form_answers():
    return session.setdefault("form_answers", {})


def request_form():
    return {k: sanitise_input(v) for k, v in request.form.items() if k != "csrf_token"}


def delete_answer_from_form(answer_key):
    answers = session["form_answers"]
    if answer_key in answers:
        del answers[answer_key]


def get_errors_from_session(error_group_name):
    error_list = []
    error_messages = {}
    if session.get("error_items") and session["error_items"].get(error_group_name):
        errors = session["error_items"][error_group_name]
        error_messages = {k: {"text": v} for k, v in errors.items()}
        error_list = [{"text": text, "href": f"#{field}"} for field, text in errors.items()]
    answers = session.setdefault("form_answers", {})
    return {
        "error_list": error_list,
        "error_messages": error_messages,
        "answers": answers,
    }


def accessing_saved_answers():
    return session.get("accessing_saved_answers", False)


def update_session_answers_from_form_for_enum():
    session["form_answers"] = {
        **session.setdefault(
            "form_answers", {}
        ),
        **{k: int(v) for k, v in request_form().items()},
    }
    session["error_items"] = {}


def get_answer_from_form(answers_key_list):
    answers = session["form_answers"]
    for key in answers_key_list:
        answers = answers.get(key)
        if answers is None:
            break
    return answers


def is_nhs_login_user():
    return session.get("nhs_sub") is not None


def has_started_form():
    return "form_started" in session


def should_contact_gp():
    return NHSLetterAnswers(form_answers()["nhs_letter"]) is NHSLetterAnswers.YES


def _slice(keys, _dict):
    return (_dict[key] for key in keys if key in _dict)


def get_summary_rows_from_form_answers(excluded_answers=None):
    summary_rows = []
    answers = form_answers()
    order = [
        "nhs_number",
        "name",
        "date_of_birth",
        "support_address",
        "do_you_have_someone_to_go_shopping_for_you",
        "priority_supermarket_deliveries",
        "basic_care_needs",
        "contact_details"
    ]

    if excluded_answers:
        for answer_to_exclude in excluded_answers:
            order.remove(answer_to_exclude)

    answers_to_key = {
        "priority_supermarket_deliveries": PrioritySuperMarketDeliveriesAnswers,
        "do_you_have_someone_to_go_shopping_for_you": ShoppingAssistanceAnswers,
        "basic_care_needs": BasicCareNeedsAnswers,
    }

    for key in order:
        if key not in answers:
            continue

        answer_labels = {
            **PAGE_TITLES,
            "support-address": "The address where support is needed",
            "name": "Name",
            "date-of-birth": "Date of birth",
            "contact-details": "Contact details",
        }

        change_answer_urls = {
            "support_address": "address-lookup"
        }

        answer = answers[key]
        dashed_key = key.replace("_", "-")
        question = answer_labels[dashed_key]

        change_answer_url = (f"/{change_answer_urls[key]}" if key in change_answer_urls else f"/{dashed_key}") + "?ca=1"
        change_answer_url = append_querystring_params(change_answer_url)

        value = {}
        if key == "support_address":
            address_lines = [
                answer['building_and_street_line_1'],
                answer.get('building_and_street_line_2'),
                answer['town_city'],
                postcode_with_spaces(answer['postcode']),
            ]
            value["html"] = "<br>".join([line for line in address_lines if line])
        elif key == "name":
            value["text"] = " ".join(_slice(["first_name", "middle_name", "last_name"], answer))
        elif key == "contact_details":
            value["html"] = "<br>".join(
                [
                    f"Phone number (for calls): {answer.get('phone_number_calls', '')}",
                    f"Phone number (for texts): {answer.get('phone_number_texts', '')}",
                    f"Email: {answer.get('email', '')}",
                ]
            )
        elif key == "date_of_birth":
            value["text"] = "{day:02}/{month:02}/{year}".format(**{k: int(v) for k, v in answer.items()})
        elif key in answers_to_key:
            value["text"] = answers_to_key[key](answer).value_as_text
        else:
            value["text"] = answers[key]

        row = _get_summary_row(change_answer_url, question, value)
        summary_rows.append(row)

    return summary_rows


def _get_summary_row(change_answer_url, question, value):
    row = {
        "key": {
            "text": question,
            "classes": "govuk-!-width-two-thirds",
        },
        "value": value,
        "actions": {
            "items": [
                {
                    "href": change_answer_url,
                    "classes": "change-link",
                    "text": "Change",
                    "visuallyHiddenText": question,
                }
            ]
        },
    }
    return row


def persist_answers_from_session():
    address_postcode = form_answers()["support_address"]["postcode"]
    if len(address_postcode) == 6 and " " not in address_postcode:
        address_postcode = f"{address_postcode[:3]} {address_postcode[3:]}"

    location_tier = get_location_tier()
    if location_tier not in [PostcodeTier.VERY_HIGH_PLUS_SHIELDING.value, PostcodeTier.VERY_HIGH.value]:
        raise ValueError(f"Unexpected value encountered for location tier: {location_tier}")
    if get_shielding_advice() == ShieldingAdvice.NOT_ADVISED_TO_SHIELD.value:
        # it is not possible to have an answer for basic_care_needs when the shielding is not advised
        _set_form_answer(["basic_care_needs"], None)

    submission_reference = persistence.persist_answers(
        form_answers()["nhs_number"],
        form_answers()["name"]["first_name"],
        form_answers()["name"].get("middle_name"),
        form_answers()["name"]["last_name"],
        form_answers()["date_of_birth"],
        form_answers()["support_address"]["building_and_street_line_1"],
        form_answers()["support_address"].get("building_and_street_line_2"),
        form_answers()["support_address"]["town_city"],
        address_postcode,
        form_answers()["support_address"].get("uprn"),
        form_answers()["contact_details"].get("phone_number_calls"),
        form_answers()["contact_details"].get("phone_number_texts"),
        form_answers()["contact_details"].get("email"),
        session.get("nhs_sub"),
        form_answers()["applying_on_own_behalf"],
        form_answers()["nhs_letter"],
        form_answers().get("priority_supermarket_deliveries"),
        form_answers().get("basic_care_needs"),
        form_answers().get("do_you_have_someone_to_go_shopping_for_you"),
        form_answers().get("medical_conditions"),
        None,
        get_location_tier(),
        get_shielding_advice(),
    )
    session["form_uid"] = submission_reference

    return submission_reference


def _strip_keys_with_no_value(_dict):
    return {key: value for key, value in _dict.items() if value is not None}


def load_answers_into_session_if_available():
    nhs_sub = session.get("nhs_sub")
    if nhs_sub is None:
        raise RuntimeError("Could not find nhs_sub in session")

    stored_answers = persistence.load_answers(nhs_sub)
    if stored_answers is not None:
        (
            _,
            nhs_number,
            first_name,
            middle_name,
            last_name,
            date_of_birth,
            address_line1,
            address_line2,
            address_town_city,
            address_postcode,
            address_uprn,
            contact_number_calls,
            contact_number_texts,
            contact_email,
            uid_nhs_login,
            are_you_applying_on_behalf_of_someone_else,
            have_you_received_an_nhs_letter,
            do_you_want_supermarket_deliveries,
            do_you_need_help_meeting_your_basic_care_needs,
            do_you_have_someone_to_go_shopping_for_you,
            do_you_have_one_of_the_listed_medical_conditions,
            do_you_live_in_england,
            tier_at_submission,
            shielding_at_submission,
        ) = stored_answers

        date_of_birth = datetime.date.fromisoformat(date_of_birth["stringValue"])

        session["form_answers"] = {
            "nhs_number": nhs_number["stringValue"],
            "name": _strip_keys_with_no_value(
                {
                    "first_name": first_name["stringValue"],
                    "last_name": last_name["stringValue"],
                    "middle_name": middle_name.get("stringValue"),
                }
            ),
            "date_of_birth": {
                "day": date_of_birth.day,
                "year": date_of_birth.year,
                "month": date_of_birth.month,
            },
            "support_address": _strip_keys_with_no_value(
                {
                    "building_and_street_line_1": address_line1["stringValue"],
                    "building_and_street_line_2": address_line2.get("stringValue"),
                    "town_city": address_town_city["stringValue"],
                    "postcode": address_postcode["stringValue"],
                    "uprn": address_uprn.get("longValue"),
                }
            ),
            "contact_details": _strip_keys_with_no_value(
                {
                    "phone_number_calls": contact_number_calls.get("stringValue"),
                    "phone_number_texts": contact_number_texts.get("stringValue"),
                    "email": contact_email.get("stringValue"),
                }
            ),
            "applying_on_own_behalf": are_you_applying_on_behalf_of_someone_else["longValue"],
            "nhs_letter": have_you_received_an_nhs_letter["longValue"],
            "basic_care_needs": do_you_need_help_meeting_your_basic_care_needs.get("longValue"),
            "do_you_have_someone_to_go_shopping_for_you": do_you_have_someone_to_go_shopping_for_you["longValue"],
            "do_you_live_in_england": do_you_live_in_england.get("longValue"),
            "shielding_at_submission": shielding_at_submission.get("longValue")
        }
        priority_supermarket_deliveries = do_you_want_supermarket_deliveries.get("longValue")
        if priority_supermarket_deliveries is not None:
            session["form_answers"]["priority_supermarket_deliveries"] = priority_supermarket_deliveries

        medical_conditions = do_you_have_one_of_the_listed_medical_conditions.get("longValue")
        if medical_conditions is not None:
            session["medical_conditions"] = medical_conditions
        session["accessing_saved_answers"] = True
        set_location_tier(tier_at_submission.get("longValue"))
        set_shielding_advice(shielding_at_submission.get("longValue"))
        return True
    return False


def _format_nhs_user_info_answer(answers_key, nhs_answer):
    if "nhs_number" in answers_key:
        return clean_nhs_number(nhs_answer)
    return nhs_answer


def set_form_answers_from_nhs_user_info(nhs_user_info):
    for answers_key, maybe_key in NHS_USER_INFO_TO_FORM_ANSWERS.items():
        nhs_answer = maybe_key(nhs_user_info) if callable(maybe_key) else nhs_user_info.get(maybe_key)
        if nhs_answer is None:
            continue

        formatted_answer = _format_nhs_user_info_answer(answers_key, nhs_answer)
        _set_form_answer(answers_key, formatted_answer)


def set_location_tier(location_tier):
    session[SESSION_KEY_LOCATION_TIER] = location_tier


def get_location_tier():
    return session.get(SESSION_KEY_LOCATION_TIER, None)


def set_shielding_advice(shielding_advice):
    session[SESSION_KEY_SHIELDING_ADVICE] = shielding_advice


def get_shielding_advice():
    return session.get(SESSION_KEY_SHIELDING_ADVICE, None)


def set_is_postcode_in_england(is_postcode_in_england):
    session[SESSION_KEY_IS_POSTCODE_IN_ENGLAND] = is_postcode_in_england


def get_is_postcode_in_england():
    return session.get(SESSION_KEY_IS_POSTCODE_IN_ENGLAND, None)


def _set_form_answer(answers_key_list, answer):
    answers = session["form_answers"]
    for key in answers_key_list[:-1]:
        answers = answers.setdefault(key, {})
    answers[answers_key_list[-1]] = answer


def is_returning_nhs_login_user_without_basic_care_needs_answer():
    # Scenario: Where the postcode tier has increased to VERY_HIGH_PLUS_SHIELDING
    # and no answer is present for 'basic_care_needs'
    return is_nhs_login_user() and accessing_saved_answers() and is_shielding_without_basic_care_needs_answer()  # noqa


def is_shielding_without_basic_care_needs_answer():
    # Scenario: Where the location they are in have been advised to shield
    # and no answer is present for 'basic_care_needs'
    return get_shielding_advice() == ShieldingAdvice.ADVISED_TO_SHIELD.value \
           and get_answer_from_form(["basic_care_needs"]) is None
