import json

from flask import redirect, session

from ..integrations import postcode_lookup_helper
from .blueprint import form
from .render_utils import render_template_with_title
from .routing_utils import route_to_next_form_page
from .session_utils import form_answers, get_errors_from_session, request_form
from .validation import validate_address_lookup


@form.route("/address-lookup", methods=["GET"])
def get_address_lookup():
    postcode = session["postcode"]
    try:
        addresses = postcode_lookup_helper.get_addresses_from_postcode(postcode)
    except postcode_lookup_helper.PostcodeNotFound:
        session["error_items"] = {
            **session.setdefault("error_items", {}),
            "support_address": {"postcode", "Could not find postcode"},
        }
        redirect("/postcode-lookup")
    except postcode_lookup_helper.NoAddressesFoundAtPostcode:
        session["error_items"] = {
            **session.setdefault("error_items", {}),
            "support_address": {
                "support_address",
                f"No addresses found for {postcode}",
            },
        }
        redirect("/support-address")
    except postcode_lookup_helper.ErrorFindingAddress:
        session["error_items"] = {
            **session.setdefault("error_items", {}),
            "support_address": {
                "support_address",
                "An error has occurred, please enter your address manually",
            },
        }
        redirect("/support-address")

    return render_template_with_title(
        "address-lookup.html",
        previous_path="/postcode-lookup",
        postcode=postcode,
        addresses=addresses,
        **get_errors_from_session("postcode"),
    )


@form.route("/address-lookup", methods=["POST"])
def post_address_lookup():
    session["form_answers"] = {
        **session.setdefault("form_answers", {}),
        "support_address": {**json.loads(request_form()["address"])},
    }
    session["error_items"] = {}
    if not validate_address_lookup():
        return redirect("/address-lookup")
    return route_to_next_form_page()
