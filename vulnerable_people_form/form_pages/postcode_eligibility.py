from flask import redirect, session

from .blueprint import form
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page
from .shared.session import form_answers, get_errors_from_session, request_form
from .shared.validation import validate_postcode


@form.route("/postcode-eligibility", methods=["GET"])
def get_postcode_eligibility():
    return render_template_with_title(
        "postcode-eligibility.html",
        previous_path="/nhs-login",
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


