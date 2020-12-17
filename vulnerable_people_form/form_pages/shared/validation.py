import datetime
import email_validator
import re

import phonenumbers
import stdnum.gb.nhs
from flask import session

from .answers_enums import (
    ApplyingOnOwnBehalfAnswers,
    MedicalConditionsAnswers,
    NHSLetterAnswers,
    ViewOrSetupAnswers,
    YesNoAnswers,
    PrioritySuperMarketDeliveriesAnswers,
    ShoppingAssistanceAnswers,
    BasicCareNeedsAnswers,
    LiveInEnglandAnswers)
from .logger_utils import create_log_message, log_event_names
from .session import form_answers, get_answer_from_form, request_form
from .sms_validation import validate_notify_compatible_uk_mobile_number, InvalidPhoneError


def validate_mandatory_form_field(section_key, value_key, error_message):
    if not form_answers().get(section_key, {}).get(value_key):
        existing_section = session.setdefault("error_items", {}).setdefault(section_key, {})
        session["error_items"] = {
            **session.setdefault("error_items", {}),
            section_key: {**existing_section, value_key: error_message},
        }
        return False
    return True


def validate_name():
    length_fstring = "'{}' cannot be longer than {} characters"
    return all(
        [
            validate_mandatory_form_field("name", "first_name", "Enter your first name"),
            validate_mandatory_form_field("name", "last_name", "Enter your last name"),
            validate_length(
                ("name", "first_name"),
                50,
                length_fstring.format("First name", 50),
            ),
            validate_length(
                ("name", "middle_name"),
                50,
                length_fstring.format("Middle name", 50),
            ),
            validate_length(
                ("name", "last_name"),
                50,
                length_fstring.format("Last name", 50),
            ),
        ]
    )


def validate_view_or_setup():
    value = request_form().get("view_or_setup")
    try:
        ViewOrSetupAnswers(int(value))
    except ValueError:
        session["error_items"] = {
            **session.setdefault("error_items", {}),
            "view_or_setup": {
                "view_or_setup": "You must select if you would like to set up an account, or access an account via your NHS Login."  # noqa: E501
            },
        }
        return False
    if session.get("error_items"):
        session["error_items"].pop("view_or_setup")
    return True


def validate_applying_on_own_behalf():
    return validate_radio_button(
        ApplyingOnOwnBehalfAnswers,
        "applying_on_own_behalf",
        "Select if you are using this service for yourself or someone else",
    )


def validate_radio_button(EnumClass, value_key, error_message):
    value = form_answers().get(value_key)
    try:
        EnumClass(int(value))
    except (ValueError, TypeError):
        session["error_items"] = {
            **session.setdefault("error_items", {}),
            value_key: {value_key: error_message},
        }
        return False
    if session.get("error_items"):
        session["error_items"].pop(value_key)
    return True


def validate_nhs_letter():
    return validate_radio_button(NHSLetterAnswers, "nhs_letter", "Select if you received the letter from the NHS")


def validate_nhs_login():
    return validate_radio_button(
        YesNoAnswers,
        "nhs_login",
        "Select yes if you want log in with you NHS details",
    )


def validate_register_with_nhs():
    value = request_form().get("nhs_registration")
    try:
        YesNoAnswers(int(value))
    except ValueError:
        session["error_items"] = {
            **session.setdefault("error_items", {}),
            "nhs_registration": {
                "nhs_registration": "You need to select if you want to register an account with the NHS in order to retrieve your answers at a alater point."  # noqa: E501
            },
        }
        return False
    if session.get("error_items"):
        session["error_items"].pop("nhs_registration")
    return True


def validate_medical_conditions():
    return validate_radio_button(
        MedicalConditionsAnswers,
        "medical_conditions",
        "Select yes if you have one of the medical conditions on the list",
    )


def validate_address_lookup():
    if not request_form().get("address"):
        session["error_items"] = {
            **session.setdefault("error_items", {}),
            "address_lookup": {
                "address": "You must select an address",
            },
        }
        return False
    return True


def _is_number(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


def _is_positive_int(string):
    try:
        value = int(string)
    except ValueError:
        return False
    return value == float(string) and value > 0


def _failing_field(field_bools, field_names):
    return field_names[field_bools.index(True)]


def _date_field_exceeds_max_permitted_length(value, field_name):
    permitted_max_field_lengths = {"day": 2, "month": 2, "year": 4}
    return value and type(value) is str and len(value) > permitted_max_field_lengths[field_name]


def validate_date_of_birth():
    dob = form_answers().get("date_of_birth", {})
    day = dob.get("day", "")
    month = dob.get("month", "")
    year = dob.get("year", "")

    fields = [month, day, year]
    field_names = ("month", "day", "year")
    fields_empty = [period == "" for period in fields]
    fields_not_numbers = [not _is_number(period) for period in fields]
    fields_not_positive_int = [not _is_positive_int(period) for period in fields]
    fields_invalid_length = [_date_field_exceeds_max_permitted_length(period, field_names[idx])
                             for (idx, period) in enumerate(fields)]

    error = None
    if all(fields_empty):
        error = "Enter your date of birth"
    elif any(fields_empty):
        error = "Enter your date of birth and include a day, month and a year"
    elif any(fields_not_numbers):
        error = f"Enter {_failing_field(fields_not_numbers, field_names)} as a number"
    elif any(fields_not_positive_int):
        error = f"Enter a real {_failing_field(fields_not_positive_int, field_names)}"
    elif any(fields_invalid_length):
        error = f"Enter a {_failing_field(fields_invalid_length, field_names)} with the correct amount of digits"

    invalid_date_message = "Enter a real date of birth"
    if error is None:
        try:
            date = datetime.date(int(year), int(month), int(day))
        except ValueError:
            error = invalid_date_message
    if error is None:
        if (date - datetime.date.today()).days > 0:
            error = "Date of birth must be in the past"
        elif (datetime.date.today() - date).days / 365.25 > 150:
            error = invalid_date_message

    if error:
        session["error_items"] = {
            **session.setdefault("error_items", {}),
            "date_of_birth": {"date_of_birth": error},
        }

    return error is None


def validate_postcode(postcode, error_section_name):
    character_limiting_regex = "^[A-Z0-9]{5,7}$"
    postcode_regex = r"^([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|(([A-Za-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9][A-Za-z]?))))\s?[0-9][A-Za-z]{2})$"  # noqa: E501
    error = None
    if not postcode:
        error = "What is the postcode where you need support?"
    elif re.match(character_limiting_regex, postcode) is None or \
            re.match(postcode_regex, postcode.upper()) is None:
        error = "Enter a real postcode"
    if error:
        error_section = session.setdefault("error_items", {}).get(error_section_name, {})
        session["error_items"] = {
            **session.setdefault("error_items", {}),
            error_section_name: {**error_section, "postcode": error},
        }

    return error is None


def validate_length(form_answer_key_list, max_length, error_string):
    if len(get_answer_from_form(form_answer_key_list) or "") > max_length:
        session["error_items"] = {
            **session.setdefault("error_items", {}),
            form_answer_key_list[0]: {
                **session["error_items"].get(form_answer_key_list[0], {}),
                form_answer_key_list[-1]: error_string,
            },
        }
        return False
    return True


def validate_support_address():
    length_fstring = "'{}' cannot be longer than {} characters"
    value = all(
        [
            validate_length(
                ("support_address", "building_and_street_line_1"),
                110,
                length_fstring.format("Address line 1", 110),
            ),
            validate_length(
                ("support_address", "building_and_street_line_2"),
                210,
                length_fstring.format("Address line 2", 210),
            ),
            validate_mandatory_form_field(
                "support_address",
                "town_city",
                "Enter a town or city",
            ),
            validate_length(("support_address", "town_city"), 50, length_fstring.format("Town or city", 50)),
            validate_mandatory_form_field(
                "support_address",
                "building_and_street_line_1",
                "Enter a building and street",
            ),
            validate_postcode(get_answer_from_form(("support_address", "postcode")), "support_address"),
        ]
    )
    return value


def validate_phone_number_if_present(section_key, phone_number_key):
    try:
        phone_number = form_answers()["contact_details"].get(phone_number_key, "")
        if phone_number:
            phonenumbers.parse(phone_number, region="GB")
    except phonenumbers.NumberParseException:
        error_message = "Enter a telephone number, like 020 7946 0000, 07700900000 or +44 0808 157 0192"
        error_section = session.setdefault("error_items", {}).get(section_key, {})
        session["error_items"] = {
            **session.setdefault("error_items", {}),
            section_key: {**error_section, phone_number_key: error_message},
        }
        return False
    return True


def validate_sms_phone_number_if_present(section_key, phone_number_key, logger=None):
    phone_number = form_answers()["contact_details"].get(phone_number_key, "")
    if phone_number and phone_number_is_valid_for_notify(phone_number, logger=logger):
        return True
    else:
        error_message = "Enter a UK mobile number, like 07700 900000 or +44 7700 900000"
        error_section = session.setdefault("error_items", {}).get(section_key, {})
        session["error_items"] = {
            **session.setdefault("error_items", {}),
            section_key: {**error_section, phone_number_key: error_message},
        }
        return False


def phone_number_is_valid_for_notify(phone_number, logger=None):
    try:
        validate_notify_compatible_uk_mobile_number(phone_number)
        return True
    except InvalidPhoneError as e:
        if logger:
            logger.warning(create_log_message(log_event_names["NHS_LOGIN_USER_CONSENT_NOT_GIVEN"],
                                              f"Invalid phone for receiving Notify SMS entered: {e.message}"))
        return False


def validate_email_if_present(section_key, email_key):
    email_address = form_answers()["contact_details"].get(email_key)
    if email_address:
        try:
            email_validator.validate_email(email_address)
        except email_validator.EmailNotValidError:
            error_message = "Enter an email address in the correct format, like name@example.com"
            error_section = session.setdefault("error_items", {}).get(section_key, {})
            session["error_items"] = {
                **session.setdefault("error_items", {}),
                section_key: {**error_section, email_key: error_message},
            }
            return False
    return True


def validate_contact_details(section_key, logger=None):
    value = all(
        [
            validate_email_if_present(section_key, "email"),
            validate_phone_number_if_present(section_key, "phone_number_calls"),
            validate_sms_phone_number_if_present(section_key, "phone_number_texts", logger=logger),
        ]
    )
    return value


def validate_nhs_number():
    error = None
    nhs_number = form_answers().get("nhs_number")
    if nhs_number:
        try:
            stdnum.gb.nhs.validate(nhs_number)
        except stdnum.exceptions.InvalidLength:
            error = "Enter your 10-digit NHS number"
        except (
            stdnum.exceptions.InvalidChecksum,
            stdnum.exceptions.InvalidComponent,
            stdnum.exceptions.InvalidFormat,
        ):
            error = "Enter a real NHS number"
    else:
        error = "Enter your 10-digit NHS number"

    if error is not None:
        session["error_items"] = {
            **session.setdefault("error_items", {}),
            "nhs_number": {"nhs_number": error},
        }
    return error is None


def validate_priority_supermarket_deliveries():

    return validate_radio_button(
        PrioritySuperMarketDeliveriesAnswers,
        "priority_supermarket_deliveries",
        "Select if you want priority supermarket deliveries",
    )


def validate_basic_care_needs():
    return validate_radio_button(
        BasicCareNeedsAnswers,
        "basic_care_needs",
        "Select yes if your basic care needs are being met at the moment",
    )


def validate_do_you_have_someone_to_go_shopping_for_you():
    return validate_radio_button(
        ShoppingAssistanceAnswers,
        "do_you_have_someone_to_go_shopping_for_you",
        "Select yes if you have someone who can go shopping for you",
    )


def validate_do_you_live_in_england():
    return validate_radio_button(
        LiveInEnglandAnswers,
        "do_you_live_in_england",
        "Select yes if you live in England",
    )
