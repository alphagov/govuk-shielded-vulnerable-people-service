from flask import request, session

from .answers_enums import (
    NHSLetterAnswers,
    ApplyingOnOwnBehalfAnswers,
    MedicalConditionsAnswers,
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
        error_list = [
            {"text": text, "href": f"#{field}"} for field, text in errors.items()
        ]
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
        **session.setdefault("form_answers",),
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
    return (_dict[key] for key in keys if _dict[key])


def get_summary_rows_from_form_answers():
    summary_rows = []
    answers = form_answers()
    order = [
        "applying_on_own_behalf",
        "live_in_england",
        "nhs_letter",
        "medical_conditions",
        "name",
        "date_of_birth",
        "support_address",
        "contact_details",
        "nhs_number",
        "essential_supplies",
        "dietary_requirements",
        "carry_supplies",
        "basic_care_needs",
    ]

    answers_to_key = {
        "applying_on_own_behalf": ApplyingOnOwnBehalfAnswers,
        "live_in_england": YesNoAnswers,
        "nhs_letter": NHSLetterAnswers,
        "medical_conditions": MedicalConditionsAnswers,
        "essential_supplies": YesNoAnswers,
        "dietary_requirements": YesNoAnswers,
        "carry_supplies": YesNoAnswers,
        "basic_care_needs": YesNoAnswers,
    }

    for key in order:
        if key not in answers:
            continue

        answer = answers[key]
        dashed_key = key.replace("_", "-")
        question = PAGE_TITLES[dashed_key]

        value = {}
        row = {
            "key": {"text": question, "classes": "govuk-!-width-two-thirds",},
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
                        "county",
                        "postcode",
                    ],
                    answer,
                )
            )
        elif key == "name":
            value["text"] = " ".join(
                _slice(["first_name", "middle_name", "last_name"], answer)
            )
        elif key == "contact_details":
            value["html"] = "<br>".join(
                [
                    f"Phone number: {answer['phone_number_calls']}",
                    f"Text: {answer['phone_number_texts']}",
                    f"Email: {answer['email']}",
                ]
            )
        elif key == "date_of_birth":
            value["text"] = "{day:02}/{month:02}/{year}".format(
                **{k: int(v) for k, v in answer.items()}
            )
        elif key in answers_to_key:
            value["text"] = answers_to_key[key](answer).value_as_text
        else:
            value["text"] = answers[key]

        row["value"] = value
        summary_rows.append(row)

    return summary_rows


def persist_answers_from_session():
    args = [
        form_answers()["nhs_number"],
        form_answers()["nhs_letter"],
        form_answers()["name"]["first_name"],
        form_answers()["name"]["middle_name"],
        form_answers()["name"]["last_name"],
        form_answers()["address"]["address_line1"],
        form_answers()["address"]["address_town_city"],
        form_answers()["address"]["address_postcode"],
        form_answers()["address"]["address_county"],
        form_answers()["address"]["address_uprn"],
        form_answers()["contact_details"]["phone_number_calls"],
        form_answers()["contact_details"]["phone_number_texts"],
        form_answers()["contact_details"]["email"],
        form_answers()["essential_supplies"],
        form_answers()["medical_conditions"],
        form_answers()["applying_on_own_behalf"],
        form_answers()["date_of_birth"],
    ]
    kwargs = {
        "carry_supplies": form_answers().get("carry_supplies"),
        "uid_nhs_login": session.get("nhs_sub"),
        "address_line2": form_answers().get("address_line2"),
        "dietary_requirements": form_answers().get("dietary_requirements"),
    }
    form_uid = session.get("form_uid")
    if form_uid is None:
        session["form_uid"] = persistence.save_answers(*args, **kwargs)
    else:
        persistence.update_answers(form_uid, *args, **kwargs)
    return session["form_uid"]


def load_answers_into_session_if_available():
    nhs_sub = session.get("nhs_sub")
    if nhs_sub is None:
        raise RuntimeError("Could not find nhs_sub in session")
    stored_answers = persistence.load_answers(nhs_sub)
    if stored_answers:
        session["form_answers"] = {
            "nhs_number": stored_answers["nhs_number"],
            "nhs_letter": stored_answers["nhs_letter"],
            "name": {
                "first_name": stored_answers["first_name"],
                "middle_name": stored_answers["middle_name"],
                "last_name": stored_answers["last_name"],
            },
            "postcode": stored_answers["address_postcode"],
            "address": {
                "address_line1": stored_answers["address_line1"],
                "address_line2": stored_answers["address_line2"],
                "town_city": stored_answers["town_city"],
                "county": stored_answers["county"],
                "uprn": stored_answers["uprn"],
            },
            "contact_details": {
                "phone_number_calls": stored_answers["contact_number_calls"],
                "phone_number_texts": stored_answers["contact_number_texts"],
                "email": stored_answers["contact_email"],
            },
            "essential_supplies": stored_answers["essential_supplies"],
            "medical_conditions": stored_answers["medical_conditions"],
            "applying_on_own_behalf": stored_answers["applying_on_own_behalf"],
            "date_of_birth": stored_answers["date_of_birth"],
            "carry_supplies": stored_answers["carry_supplies"],
            "dietary_requirements": stored_answers["dietary_requirements"],
            "basic_care_needs": stored_answers["basic_care_needs"],
        }
        session["nhs_sub"] = (stored_answers["nhs_uid"],)
        session["accessing_saved_answers"] = True
        return True
    return False

