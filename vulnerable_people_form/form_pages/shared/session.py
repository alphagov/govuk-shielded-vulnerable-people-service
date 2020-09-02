import datetime

from flask import request, session

from .answers_enums import (
    NHSLetterAnswers,
    ApplyingOnOwnBehalfAnswers,
    MedicalConditionsAnswers,
    PrioritySuperMarketDeliveriesAnswers,
    YesNoAnswers,
)
from .constants import PAGE_TITLES

from ...integrations import persistence


def form_answers():
    return session.setdefault("form_answers", {})


def request_form():
    return {k: v for k, v in request.form.items() if k != "csrf_token"}


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
            "form_answers",
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


def should_contact_gp():
    return NHSLetterAnswers(form_answers()["nhs_letter"]) is NHSLetterAnswers.YES


def _slice(keys, _dict):
    return (_dict[key] for key in keys if key in _dict)


def get_summary_rows_from_form_answers():
    summary_rows = []
    answers = form_answers()
    order = [
        "support_address",
        "name",
        "date_of_birth",
        "contact_details",
        "nhs_number",
        "do_you_have_someone_to_go_shopping_for_you",
        "priority_supermarket_deliveries",
        "basic_care_needs",
    ]

    answers_to_key = {
        "priority_supermarket_deliveries": PrioritySuperMarketDeliveriesAnswers,
        "do_you_have_someone_to_go_shopping_for_you": YesNoAnswers,
        "basic_care_needs": YesNoAnswers,
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

        answer = answers[key]
        dashed_key = key.replace("_", "-")
        question = answer_labels[dashed_key]

        value = {}
        row = {
            "key": {
                "text": question,
                "classes": "govuk-!-width-two-thirds",
            },
            "value": {},
            "actions": {
                "items": [
                    {
                        "href": f"/{dashed_key}",
                        "text": "Change",
                        "visuallyHiddenText": question,
                    }
                ]
            },
        }
        if key == "support_address":
            value["html"] = "<br>".join(
                _slice(
                    [
                        "building_and_street_line_1",
                        "building_and_street_line_2",
                        "town_city",
                        "postcode",
                    ],
                    answer,
                )
            )
        elif key == "name":
            value["text"] = " ".join(_slice(["first_name", "middle_name", "last_name"], answer))
        elif key == "contact_details":
            value["html"] = "<br>".join(
                [
                    f"Phone number: {answer.get('phone_number_calls', '')}",
                    f"Text: {answer.get('phone_number_texts', '')}",
                    f"Email: {answer.get('email', '')}",
                ]
            )
        elif key == "date_of_birth":
            value["text"] = "{day:02}/{month:02}/{year}".format(**{k: int(v) for k, v in answer.items()})
        elif key in answers_to_key:
            value["text"] = answers_to_key[key](answer).value_as_text
        else:
            value["text"] = answers[key]

        row["value"] = value
        summary_rows.append(row)

    return summary_rows


def persist_answers_from_session():
    address_postcode = form_answers()["support_address"]["postcode"]
    if len(address_postcode) == 6 and " " not in address_postcode:
        address_postcode = f"{address_postcode[:3]} {address_postcode[3:]}"
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
        form_answers()["basic_care_needs"],
        form_answers().get("do_you_have_someone_to_go_shopping_for_you"),
        form_answers().get("medical_conditions"),
    )

    session["form_uid"] = submission_reference

    return submission_reference


def _strip_keys_with_no_value(_dict):
    return {key: value for key, value in _dict.items() if value is not None}


def load_answers_into_session_if_available():
    print("aaa" * 134)
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
            "basic_care_needs": do_you_need_help_meeting_your_basic_care_needs["longValue"],
            "do_you_have_someone_to_go_shopping_for_you": do_you_have_someone_to_go_shopping_for_you["longValue"],
        }
        priority_supermarket_deliveries = do_you_want_supermarket_deliveries.get("longValue")
        if priority_supermarket_deliveries is not None:
            session["form_answers"]["priority_supermarket_deliveries"] = priority_supermarket_deliveries

        medical_conditions = do_you_have_one_of_the_listed_medical_conditions.get("longValue")
        if medical_conditions is not None:
            session["medical_conditions"] = medical_conditions
        session["accessing_saved_answers"] = True
        return True
    return False
