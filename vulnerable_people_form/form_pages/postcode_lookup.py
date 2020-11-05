from flask import redirect, session

from vulnerable_people_form.integrations.postcode_lookup_helper import format_postcode
from .blueprint import form
from .shared.querystring_utils import append_querystring_params
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page
from .shared.session import get_errors_from_session, request_form, delete_answer_from_form
from .shared.validation import validate_postcode


@form.route("/postcode-lookup", methods=["POST"])
def post_postcode_lookup():
    session["postcode"] = format_postcode(request_form().get("postcode"))
    if not validate_postcode(session["postcode"], "postcode"):
        return redirect("/postcode-lookup")

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
