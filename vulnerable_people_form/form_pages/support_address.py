from flask import redirect, session

from .blueprint import form
from .shared.constants import SESSION_KEY_ADDRESS_SELECTED
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page
from .shared.session import form_answers, get_errors_from_session, request_form
from .shared.validation import validate_support_address


@form.route("/support-address", methods=["POST"])
def post_support_address():
    original_address = {k: v for k, v in form_answers().get("support_address", {}).items() if k != "uprn"}
    session["postcode"] = request_form().get("postcode")

    if original_address != request_form():
        session["form_answers"] = {
            **session.setdefault("form_answers", {}),
            "support_address": {**request_form(), "uprn": None},
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
        previous_path="/address-lookup",
        values=form_answers().get("support_address", {}),
        **get_errors_from_session("support_address"),
    )
