import logging

import phonenumbers
from flask import redirect, session

from .blueprint import form
from .shared.logger_utils import init_logger
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page, get_back_url_for_contact_details
from .shared.session import form_answers, get_errors_from_session, request_form
from .shared.validation import validate_contact_details


logger = logging.getLogger(__name__)
init_logger(logger)


def format_phone_number_if_valid(phone_number):
    try:
        return phonenumbers.format_number(
            phonenumbers.parse(phone_number, region="GB"),
            phonenumbers.PhoneNumberFormat.NATIONAL,
        )
    except phonenumbers.NumberParseException:
        return phone_number


@form.route("/contact-details", methods=["GET"])
def get_contact_details():
    return render_template_with_title(
        "contact-details.html",
        previous_path=get_back_url_for_contact_details(),
        values=form_answers().get("contact_details", {}),
        **get_errors_from_session("contact_details"),
    )


@form.route("/contact-details", methods=["POST"])
def post_contact_details():
    email = request_form().get("email")
    phone_number_calls = request_form().get("phone_number_calls")
    phone_number_texts = request_form().get("phone_number_texts")

    session["form_answers"] = {
        **session.setdefault("form_answers", {}),
        "contact_details": {
            **request_form(),
            "phone_number_calls": format_phone_number_if_valid(phone_number_calls) if phone_number_calls else '',
            "phone_number_texts": format_phone_number_if_valid(phone_number_texts) if phone_number_texts else '',
            "email": email.strip() if email else ""
        },
    }
    session["error_items"] = {}
    if not validate_contact_details("contact_details"):
        return redirect("/contact-details")
    return route_to_next_form_page()
