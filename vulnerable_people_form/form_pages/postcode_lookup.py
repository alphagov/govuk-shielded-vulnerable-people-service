from flask import redirect, session, current_app

from .blueprint import form
from .shared.form_utils import format_postcode
from .shared.location_tier import update_location_status_by_postcode
from .shared.querystring_utils import append_querystring_params
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page
from .shared.session import (
    get_errors_from_session,
    request_form,
    delete_answer_from_form,
    accessing_saved_answers
)
from .shared.location_tier import update_is_postcode_in_england
from .shared.validation import validate_postcode


@form.route("/postcode-lookup", methods=["POST"])
def post_postcode_lookup():
    session["postcode"] = format_postcode(request_form().get("postcode"))
    if not validate_postcode(session["postcode"], "postcode"):
        return redirect("/postcode-lookup")

    update_is_postcode_in_england(session["postcode"], current_app)
    update_location_status_by_postcode(session["postcode"], current_app)

    if not accessing_saved_answers():
        delete_answer_from_form("support_address")

    session["error_items"] = {}
    return route_to_next_form_page()


@form.route("/postcode-lookup", methods=["GET"])
def get_postcode_lookup():
    return render_template_with_title(
        "postcode-lookup.html",
        previous_path=append_querystring_params("/address-lookup"),
        values={"postcode": session.get("postcode", "")},
        **get_errors_from_session("postcode"),
    )
