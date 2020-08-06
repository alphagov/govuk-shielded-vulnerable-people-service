from flask import redirect, session

from .blueprint import form
from .render_utils import render_template_with_title
from .routing_utils import route_to_next_form_page
from .session_utils import form_answers, get_errors_from_session, request_form
from .validation import validate_postcode


@form.route("/postcode-eligibility", methods=["GET"])
def get_postcode_eligibility():
    return render_template_with_title(
        "postcode-eligibility.html",
        previous_path="/date-of-birth",
        values={"postcode": session.get("postcode", "")},
        **get_errors_from_session("postcode"),
    )

@form.route("/postcode-eligibility", methods=["POST"])
def post_postcode_verification():
    session["postcode"] = request_form().get("postcode")
    if not validate_postcode("postcode"):
        return redirect("/postcode-eligibility")

    session["error_items"] = {}
    return route_to_next_form_page()


