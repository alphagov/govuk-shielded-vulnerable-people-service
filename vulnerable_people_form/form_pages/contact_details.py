import phonenumbers
from flask import redirect, session

from .blueprint import form
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page, get_back_url_for_contact_details
from .shared.session import form_answers, get_errors_from_session, request_form
from .shared.validation import validate_contact_details


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
    session["form_answers"] = {
        **session.setdefault("form_answers", {}),
        "contact_details": {
            **request_form(),
            **{
                phone_key: format_phone_number_if_valid(request_form().get(phone_key))
                for phone_key in ("phone_number_calls", "phone_number_texts")
            },
            "email": request_form().get("email").strip() if request_form().get("email") else ""
        },
    }
    session["error_items"] = {}
    if not validate_contact_details("contact_details"):
        return redirect("/contact-details")
    return route_to_next_form_page()
