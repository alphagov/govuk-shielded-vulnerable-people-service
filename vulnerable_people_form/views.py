import datetime
import enum
import email
import json
import phonenumbers

import stdnum
import stdnum.gb.nhs

import re

from flask import current_app, Blueprint, render_template, redirect, request, session


from . import postcode_lookup_helper

form = Blueprint("form", __name__)


def update_session_answers_from_form():
    session["form_answers"] = {**session.setdefault("form_answers", {}), **request.form}
    session["error_items"] = {}


def form_answers():
    return session.setdefault("form_answers", {})


def get_radio_options_from_enum(target_enum, selected_value):
    return [
        {
            "value": value.value,
            "text": value.value,
            "checked": selected_value == value.value,
        }
        for value in target_enum
    ]


@enum.unique
class YesNoAnswers(enum.Enum):
    YES = "Yes"
    NO = "No"


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


def validate_radio_button(EnumClass, value_key, error_message):
    value = request.form.get(value_key)
    try:
        EnumClass(value)
    except ValueError:
        session["error_items"] = {
            **session.setdefault("error_items", {}),
            value_key: {value_key: error_message},
        }
        return False
    if session.get("error_items"):
        session["error_items"].pop(value_key)
    return True


def validate_live_in_england():
    return validate_radio_button(
        YesNoAnswers, "live_in_england", "Select yes if you live in England"
    )


@form.route("/start", methods=["GET"])
def get_start():
    return redirect("/live-in-england")


@form.route("/live-in-england", methods=["GET"])
def get_live_in_england():
    return render_template(
        "live-in-england.html",
        radio_items=get_radio_options_from_enum(
            YesNoAnswers, form_answers().get("live_in_england")
        ),
        previous_path="/",
        **get_errors_from_session("live_in_england"),
    )


@form.route("/live-in-england", methods=["POST"])
def post_live_in_england():
    if not validate_live_in_england():
        return redirect("/live-in-england")
    update_session_answers_from_form()

    live_in_england = request.form["live_in_england"]
    if YesNoAnswers(live_in_england) is YesNoAnswers.YES:
        return redirect("/nhs-letter")
    return redirect("/not-eligible-england")


@enum.unique
class NHSLetterAnswers(enum.Enum):
    YES = "Yes, I’ve been told to shield"
    NO = "No, I haven’t been told to shield"
    NOT_SURE = "Not sure"


def validate_nhs_letter():
    return validate_radio_button(
        NHSLetterAnswers, "nhs_letter", "Select if you received the letter from the NHS"
    )


@form.route("/nhs-letter", methods=["POST"])
def post_nhs_letter():
    if not validate_nhs_letter():
        return redirect("/nhs-letter")

    update_session_answers_from_form()
    nhs_letter = request.form.get("nhs_letter")
    if NHSLetterAnswers(nhs_letter) is NHSLetterAnswers.YES:
        return redirect("/name")
    return redirect("/medical-conditions")


@form.route("/nhs-letter", methods=["GET"])
def get_nhs_letter():
    return render_template(
        "nhs-letter.html",
        radio_items=get_radio_options_from_enum(
            NHSLetterAnswers, form_answers().get("nhs_letter")
        ),
        previous_path="/live-in-england",
        **get_errors_from_session("nhs_letter"),
    )


@enum.unique
class MedicalConditionsAnswers(enum.Enum):
    YES = "Yes, I have one of the listed medical conditions"
    NO = "No, I do not have one of the listed medical conditions"


def validate_medical_conditions():
    return validate_radio_button(
        MedicalConditionsAnswers,
        "medical_conditions",
        "Select yes if you have one of the medical conditions on the list",
    )


@form.route("/medical-conditions", methods=["POST"])
def post_medical_conditions():
    if not validate_medical_conditions():
        return redirect("/medical-conditions")

    update_session_answers_from_form()
    nhs_letter = request.form.get("medical_conditions")
    if MedicalConditionsAnswers(nhs_letter) is MedicalConditionsAnswers.YES:
        return redirect("/name")
    return redirect("/not-eligible-medical")


@form.route("/medical-conditions", methods=["GET"])
def get_medical_conditions():
    return render_template(
        "medical-conditions.html",
        radio_items=get_radio_options_from_enum(
            MedicalConditionsAnswers, form_answers().get("medical_conditions")
        ),
        previous_path="/nhs-letter",
        **get_errors_from_session("medical_conditions"),
    )


def validate_mandatory_form_field(section_key, value_key, error_message):
    if not request.form.get(value_key):
        existing_section = session.setdefault("error_items", {}).setdefault(
            section_key, {}
        )
        session["error_items"] = {
            **session.setdefault("error_items", {}),
            section_key: {**existing_section, value_key: error_message},
        }
        return False
    return True


def validate_name():
    return all(
        [
            validate_mandatory_form_field(
                "name", "first_name", "Enter your first name"
            ),
            validate_mandatory_form_field("name", "last_name", "Enter your last name"),
        ]
    )


@form.route("/name", methods=["POST"])
def post_name():
    session["form_answers"] = {
        **session.setdefault("form_answers", {}),
        "name": {**request.form},
    }
    if not validate_name():
        return redirect("/name")

    session["error_items"] = {}
    return redirect("/date-of-birth")


@form.route("/name", methods=["GET"])
def get_name():
    return render_template(
        "name.html",
        values=form_answers().get("name", {}),
        previous_path="/medical-conditions"
        if session.get("medical_conditions")
        else "/nhs-letter",
        **get_errors_from_session("name"),
    )


def isNumber(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


def isPositiveInt(string):
    try:
        value = int(string)
    except ValueError:
        return False
    return value == float(string) and value > 0


def failing_field(field_bools, field_names):
    return field_names[field_bools.index(True)]


def validate_date_of_birth():
    day = request.form.get("day", "")
    month = request.form.get("month", "")
    year = request.form.get("year", "")

    fields = [month, day, year]
    fieldsEmpty = [period == "" for period in fields]
    fieldsNotNumbers = [not isNumber(period) for period in fields]
    fieldsNotPositiveInt = [not isPositiveInt(period) for period in fields]
    fieldNames = ("month", "day", "year")

    error = None
    if all(fieldsEmpty):
        error = "Enter your date of birth"
    elif any(fieldsEmpty):
        error = "Enter your date of birth and include a day month and a year"
    elif any(fieldsNotNumbers):
        error = f"Enter {failing_field(fieldsNotNumbers, fieldNames)} as a number"
    elif any(fieldsNotPositiveInt):
        error = f"Enter a real {failing_field(fieldsNotPositiveInt, fieldNames)}"

    invalid_date_message = "Enter a real date of birth"
    if error is None:
        try:
            date = datetime.date(int(year), int(day), int(month))
        except ValueError:
            error = invalid_date_message
    if error is None:
        if (date - datetime.date.today()).days > 0:
            error = "Date of birth must be in the past"
        elif (datetime.date.today() - date).days / 365.25 > 150:
            error = invalid_date_message

    session["error_items"] = {
        **session.setdefault("error_items", {}),
        "date_of_birth": {"date_of_birth": error},
    }

    return error is None


@form.route("/date-of-birth", methods=["POST"])
def post_date_of_birth():
    session["form_answers"] = {
        **session.setdefault("form_answers", {}),
        "date_of_birth": {**request.form},
    }
    if not validate_date_of_birth():
        return redirect("/date-of-birth")

    session["error_items"] = {}
    return redirect("/postcode-lookup")


@form.route("/date-of-birth", methods=["GET"])
def get_date_of_birth():
    return render_template(
        "date-of-birth.html",
        previous_path="/name",
        values=form_answers().get("date_of_birth", {}),
        **get_errors_from_session("date_of_birth"),
    )


def validate_postcode(section):
    postcode = request.form.get("postcode")

    postcode.replace(" ", "")
    postcode_regex = "(([A-Z]{1,2}[0-9][A-Z0-9]?|ASCN|STHL|TDCU|BBND|[BFS]IQQ|PCRN|TKCA) ?[0-9][A-Z]{2}|BFPO ?[0-9]{1,4}|(KY[0-9]|MSR|VG|AI)[ -]?[0-9]{4}|[A-Z]{2} ?[0-9]{2}|GE ?CX|GIR ?0A{2}|SAN ?TA1)"
    error = None
    if not postcode:
        error = "What is the postcode where you need support?"
    elif re.match(postcode_regex, postcode.upper()) is None:
        error = "Enter a real postcode"

    if error:
        error_section = session.setdefault("error_items", {}).get(section, {})
        session["error_items"] = {
            **session.setdefault("error_items", {}),
            section: {**error_section, "postcode": error},
        }

    return error is None


@form.route("/address-lookup", methods=["POST"])
def post_address_lookup():
    if not validate_mandatory_form_field(
        "address_lookup", "address", "An address must be selected"
    ):
        return redirect("/address-lookup")
    session["form_answers"] = {
        **session.setdefault("form_answers", {}),
        "support_address": {**json.loads(request.form["address"])},
    }

    session["error_items"] = {}
    return redirect("/support-address")


@form.route("/address-lookup", methods=["GET"])
def get_address_lookup():
    postcode = form_answers()["postcode"]["postcode"]
    try:
        addresses = postcode_lookup_helper.get_addresses_from_postcode(postcode)
    except postcode_lookup_helper.PostcodeNotFound:
        session["error_items"] = {
            **session.setdefault("error_items", {}),
            "support_address": {"postcode", "Could not find postcode"},
        }
        redirect("/postcode-lookup")
    except postcode_lookup_helper.NoAddressesFoundAtPostcode:
        session["error_items"] = {
            **session.setdefault("error_items", {}),
            "support_address": {
                "support_address",
                f"No addresses found for {postcode}",
            },
        }
        redirect("/support-address")
    except postcode_lookup_helper.ErrorFindingAddress:
        session["error_items"] = {
            **session.setdefault("error_items", {}),
            "support_address": {
                "support_address",
                "An error has occurred, please enter your address manually",
            },
        }
        redirect("/support-address")

    return render_template(
        "address-lookup.html",
        previous_path="/postcode-lookup",
        postcode=postcode,
        addresses=addresses,
        **get_errors_from_session("postcode"),
    )


@form.route("/postcode-lookup", methods=["POST"])
def post_postcode_lookup():
    session["form_answers"] = {
        **session.setdefault("form_answers", {}),
        "postcode": {**request.form},
    }
    if not validate_postcode("postcode"):
        return redirect("/postcode-lookup")

    session["error_items"] = {}
    return redirect("/address-lookup")


@form.route("/postcode-lookup", methods=["GET"])
def get_postcode_lookup():
    return render_template(
        "postcode-lookup.html",
        previous_path="/date-of-birth",
        values=form_answers().get("postcode", {}),
        **get_errors_from_session("postcode"),
    )


def validate_length(form_answer_key_list, max_length, error_string):
    import pprint

    pprint.pprint(get_answer_from_form(form_answer_key_list))
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
                75,
                length_fstring.format("Address line 1", 75),
            ),
            validate_length(
                ("support_address", "building_and_street_line_2"),
                75,
                length_fstring.format("Address line 2", 75),
            ),
            validate_length(
                ("support_address", "town_city"),
                50,
                length_fstring.format("Town or City", 50),
            ),
            validate_length(
                ("support_address", "county"), 50, length_fstring.format("County", 50)
            ),
            validate_mandatory_form_field(
                "support_address",
                "building_and_street_line_1",
                "Enter a building and street",
            ),
            validate_mandatory_form_field(
                "support_address", "town_city", "Enter a town or city"
            ),
            validate_postcode("support_address"),
        ]
    )
    return value


@form.route("/support-address", methods=["POST"])
def post_support_address():
    session["form_answers"] = {
        **session.setdefault("form_answers", {}),
        "support_address": {**request.form},
    }
    session["error_items"] = {}
    if not validate_support_address():
        return redirect("/support-address")

    return redirect("/contact-details")


@form.route("/support-address", methods=["GET"])
def get_support_address():
    return render_template(
        "support-address.html",
        previous_path="/address-lookup",
        values=form_answers().get("support_address", {}),
        **get_errors_from_session("support_address"),
    )


def format_phone_number_if_valid(phone_number):
    try:
        return phonenumbers.format_number(
            phonenumbers.parse(phone_number, region="GB"),
            phonenumbers.PhoneNumberFormat.NATIONAL,
        )
    except phonenumbers.NumberParseException:
        return phone_number


def validate_phone_number_if_present(section_key, phone_number_key):
    try:
        phone_number = request.form.get(phone_number_key, "")
        if phone_number:
            phonenumbers.parse(phone_number, region="GB")
    except phonenumbers.NumberParseException:
        error_message = (
            "Enter a telephone number, like 020 7946 0000, 07700900000 or +44 0808 157 0192",
        )
        error_section = session.setdefault("error_items", {}).get(section_key, {})
        session["error_items"] = {
            **session.setdefault("error_items", {}),
            section_key: {**error_section, phone_number_key: error_message},
        }
        return False
    return True


def validate_email_if_present(section_key, email_key):
    email_address = request.form.get(email_key)
    email_regex = r"([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})"
    if email_address and re.match(email_regex, email_address) is None:
        error_message = (
            "Enter email address in the correct format, like name@example.com"
        )
        error_section = session.setdefault("error_items", {}).get(section_key, {})
        session["error_items"] = {
            **session.setdefault("error_items", {}),
            section_key: {**error_section, email_key: error_message},
        }
        return False
    return True


def validate_contact_details(section_key):
    value = all(
        [
            validate_email_if_present(section_key, "email"),
            validate_phone_number_if_present(section_key, "phone_number_calls"),
            validate_phone_number_if_present(section_key, "phone_number_texts"),
        ]
    )
    return value


@form.route("/contact-details", methods=["POST"])
def post_contact_details():
    session["form_answers"] = {
        **session.setdefault("form_answers", {}),
        "contact_details": {
            **request.form,
            **{
                phone_key: format_phone_number_if_valid(request.form.get(phone_key))
                for phone_key in ("phone_number_calls", "phone_number_texts")
            },
        },
    }
    session["error_items"] = {}
    if not validate_contact_details("contact_details"):
        return redirect("/contact-details")

    return redirect("/check-contact-details")


@form.route("/contact-details", methods=["GET"])
def get_contact_details():
    return render_template(
        "contact-details.html",
        previous_path="/name",
        values=form_answers().get("contact_details", {}),
        **get_errors_from_session("contact_details"),
    )


@form.route("/check-contact-details", methods=["POST"])
def post_check_contact_details():
    existing_answers = form_answers().get("contact_details", {})
    session["form_answers"] = {
        **session.setdefault("form_answers", {}),
        "contact_details": {**existing_answers, **request.form,},
    }
    session["error_items"] = {}
    if not validate_contact_details("check_contact_details"):
        return redirect("/check-contact-details")

    return redirect("/nhs-number")


@form.route("/check-contact-details", methods=["GET"])
def get_check_contact_details():
    return render_template(
        "check-contact-details.html",
        previous_path="/contact-details",
        values=form_answers().get("contact_details", {}),
        button_text="These details are correct",
        **get_errors_from_session("check_contact_details"),
    )


def validate_nhs_number():
    error = None
    nhs_number = request.form.get("nhs_number")
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


@form.route("/nhs-number", methods=["POST"])
def post_nhs_number():
    session["form_answers"] = {
        **session.setdefault("form_answers", {}),
        "nhs_number": {**request.form,},
    }
    session["error_items"] = {}
    if not validate_nhs_number():
        return redirect("/nhs-number")

    return redirect("/essential-supplies")


@form.route("/nhs-number", methods=["GET"])
def get_nhs_number():
    return render_template(
        "nhs-number.html",
        previous_path="/contact-details",
        values=form_answers().get("nhs_number", {}),
        **get_errors_from_session("nhs_number"),
    )


def validate_essential_supplies():
    return validate_radio_button(
        YesNoAnswers,
        "essential_supplies",
        "Select yes if you have a way of getting essential supplies delivered at the moment",
    )


@form.route("/essential-supplies", methods=["GET"])
def get_essential_supplies():
    return render_template(
        "essential-supplies.html",
        radio_items=get_radio_options_from_enum(
            YesNoAnswers, form_answers().get("essential_supplies")
        ),
        previous_path="/nhs-number",
        **get_errors_from_session("essential_supplies"),
    )


@form.route("/essential-supplies", methods=["POST"])
def post_essential_supplies():
    if not validate_essential_supplies():
        return redirect("/essential-supplies")
    update_session_answers_from_form()

    essential_supplies = request.form["essential_supplies"]
    if YesNoAnswers(essential_supplies) is YesNoAnswers.YES:
        return redirect("/basic-care-needs")
    return redirect("/dietary-requirements")


def validate_basic_care_needs():
    return validate_radio_button(
        YesNoAnswers,
        "basic_care_needs",
        "Select yes if your basic care needs are being met at the moment",
    )


@form.route("/basic-care-needs", methods=["GET"])
def get_basic_care_needs():
    did_supplies_questions = (
        YesNoAnswers(form_answers().get("essential_supplies")) is YesNoAnswers.NO
    )
    previous_path = (
        "/carry-supplies" if did_supplies_questions else "/essential-supplies"
    )
    return render_template(
        "basic-care-needs.html",
        previous_path=previous_path,
        radio_items=get_radio_options_from_enum(
            YesNoAnswers, form_answers().get("basic_care_needs")
        ),
        **get_errors_from_session("basic_care_needs"),
    )


@form.route("/basic-care-needs", methods=["POST"])
def post_basic_care_needs():
    if not validate_basic_care_needs():
        return redirect("/basic-care-needs")
    update_session_answers_from_form()

    return redirect("/check-your-answers")


def validate_dietary_requirements():
    return validate_radio_button(
        YesNoAnswers,
        "dietary_requirements",
        "Select yes if you have special dietary requirements",
    )


@form.route("/dietary-requirements", methods=["GET"])
def get_dietary_requirements():
    return render_template(
        "dietary-requirements.html",
        radio_items=get_radio_options_from_enum(
            YesNoAnswers, form_answers().get("dietary_requirements")
        ),
        previous_path="/essential-supplies",
        **get_errors_from_session("dietary_requirements"),
    )


@form.route("/dietary-requirements", methods=["POST"])
def post_dietary_requirements():
    if not validate_dietary_requirements():
        return redirect("/dietary-requirements")
    update_session_answers_from_form()

    return redirect("/carry-supplies")


def validate_carry_supplies():
    return validate_radio_button(
        YesNoAnswers,
        "carry_supplies",
        "Select yes if there’s someone in the house who’s able to carry a delivery of supplies inside",
    )


@form.route("/carry-supplies", methods=["GET"])
def get_carry_supplies():
    return render_template(
        "carry-supplies.html",
        radio_items=get_radio_options_from_enum(
            YesNoAnswers, form_answers().get("carry_supplies")
        ),
        previous_path="/dietary-requirements",
        **get_errors_from_session("carry_supplies"),
    )


@form.route("/carry-supplies", methods=["POST"])
def post_carry_supplies():
    if not validate_carry_supplies():
        return redirect("/carry-supplies")
    update_session_answers_from_form()

    return redirect("/basic-care-needs")
