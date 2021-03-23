from flask import redirect, session, current_app

from .blueprint import form
from .shared.form_utils import format_postcode
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page
from .shared.session import get_errors_from_session, request_form
from .shared.location_tier import update_is_postcode_in_england
from .shared.validation import validate_postcode


@form.route("/postcode-eligibility", methods=["GET"])
def get_postcode_eligibility():
    return render_template_with_title(
        "postcode-eligibility.html",
        values={"postcode": session.get("postcode", "")},
        **get_errors_from_session("postcode"),
    )


@form.route("/postcode-eligibility", methods=["POST"])
def post_postcode_verification():
    session["postcode"] = format_postcode(request_form().get("postcode"))
    if not validate_postcode(session["postcode"], "postcode"):
        return redirect("/postcode-eligibility")

    update_is_postcode_in_england(session["postcode"], current_app)

    session["error_items"] = {}
    return route_to_next_form_page()
