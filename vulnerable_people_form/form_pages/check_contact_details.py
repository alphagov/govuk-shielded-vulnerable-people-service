from flask import redirect, session

from .blueprint import form
from .shared.querystring_utils import append_querystring_params
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page
from .shared.session import form_answers, get_errors_from_session, request_form
from .shared.validation import validate_contact_details


@form.route("/check-contact-details", methods=["GET"])
def get_check_contact_details():
    return render_template_with_title(
        "check-contact-details.html",
        previous_path=append_querystring_params("/contact-details"),
        values=form_answers().get("contact_details", {}),
        button_text="This is correct",
        **get_errors_from_session("check_contact_details"),
    )


@form.route("/check-contact-details", methods=["POST"])
def post_check_contact_details():
    existing_answers = form_answers().get("contact_details", {})
    session["form_answers"] = {
        **session.setdefault("form_answers", {}),
        "contact_details": {
            **existing_answers,
            **request_form(),
        },
    }
    session["error_items"] = {}
    if not validate_contact_details("check_contact_details"):
        return redirect("/check-contact-details")

    return route_to_next_form_page()
