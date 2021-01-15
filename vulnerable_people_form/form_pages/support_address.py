from flask import redirect, session, current_app

from .blueprint import form
from .shared.constants import SESSION_KEY_ADDRESS_SELECTED
from .shared.form_utils import sanitise_support_address, format_postcode
from .shared.location_tier import update_location_status_by_postcode,  update_is_postcode_in_england
from .shared.querystring_utils import append_querystring_params
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page
from .shared.session import form_answers, get_errors_from_session, request_form
from .shared.validation import validate_support_address


@form.route("/support-address", methods=["POST"])
def post_support_address():
    support_address_from_form = sanitise_support_address(request_form())
    support_address_from_form["postcode"] = format_postcode(support_address_from_form["postcode"])
    original_address = {k: v for k, v in form_answers().get("support_address", {}).items() if k != "uprn"}
    session["postcode"] = support_address_from_form["postcode"]

    if original_address != support_address_from_form:
        session["form_answers"] = {
            **session.setdefault("form_answers", {}),
            "support_address": {**support_address_from_form, "uprn": None},
        }
    session["error_items"] = {}
    if not validate_support_address():
        return redirect("/support-address")

    update_is_postcode_in_england(session["postcode"], current_app)
    update_location_status_by_postcode(session["postcode"], current_app)

    session[SESSION_KEY_ADDRESS_SELECTED] = False
    return route_to_next_form_page()


@form.route("/support-address", methods=["GET"])
def get_support_address():

    return render_template_with_title(
        "support-address.html",
        previous_path=append_querystring_params("/address-lookup"),
        values=form_answers().get("support_address", {}),
        **get_errors_from_session("support_address"),
    )
