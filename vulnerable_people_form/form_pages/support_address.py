from flask import redirect, session

from vulnerable_people_form.integrations.postcode_lookup_helper import format_postcode
from .blueprint import form
from .postcode_tier_blueprint import postcode_tier_form
from .shared.constants import SESSION_KEY_ADDRESS_SELECTED
from .shared.form_utils import sanitise_support_address
from .shared.querystring_utils import append_querystring_params
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page
from .shared.session import form_answers, get_errors_from_session, request_form
from .shared.validation import validate_support_address


@postcode_tier_form.route("/support-address", methods=["POST"])
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
