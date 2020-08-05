from flask import redirect, session

from .blueprint import form
from .render_utils import render_template_with_title
from .routing_utils import route_to_next_form_page
from .session_utils import form_answers, get_errors_from_session, request_form
from .validation import validate_nhs_number


@form.route("/nhs-number", methods=["GET"])
def get_nhs_number():
    return render_template_with_title(
        "nhs-number.html",
        previous_path="/contact-details",
        values={"nhs_number": form_answers().get("nhs_number", "")},
        **get_errors_from_session("nhs_number"),
    )


@form.route("/nhs-number", methods=["POST"])
def post_nhs_number():
    session["form_answers"] = {
        **session.setdefault("form_answers", {}),
        **request_form(),
        "know_nhs_number": "Yes, I know my NHS number",
    }
    session["error_items"] = {}
    if not validate_nhs_number():
        return redirect("/nhs-number")

    return route_to_next_form_page()
