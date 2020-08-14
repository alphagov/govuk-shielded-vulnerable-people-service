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
        form_answers()["support_address"]["county"],
        address_postcode,
        form_answers()["support_address"]["uprn"],
        form_answers()["contact_details"]["phone_number_calls"],
        form_answers()["contact_details"]["phone_number_texts"],
        form_answers()["contact_details"]["email"],
        session.get("nhs_sub"),
        form_answers()["applying_on_own_behalf"],
        form_answers()["nhs_letter"],
        form_answers()["essential_supplies"],
        form_answers()["basic_care_needs"],
        form_answers().get("dietary_requirements"),
        form_answers().get("carry_supplies"),
        form_answers().get("medical_conditions"),
    )

    session["form_uid"] = submission_reference

    return submission_reference


def load_answers_into_session_if_available():
    nhs_sub = session.get("nhs_sub")
    if nhs_sub is None:
        raise RuntimeError("Could not find nhs_sub in session")

    stored_answers = persistence.load_answers(nhs_sub)
    if stored_answers is not None:
        (_, nhs_number, first_name, middle_name, last_name,) = persistence.load_answers(
            nhs_sub
        )
        session["form_answers"] = {
            "nhs_number": nhs_number["stringValue"],
            "name": {
                k: v
                for k, v in {
                    "first_name": first_name["stringValue"],
                    "last_name": last_name["stringValue"],
                    "middle_name": middle_name.get("stringValue"),
                }.items()
                if v is not None
            },
        }
        session["accessing_saved_answers"] = True
        return True
    return False

