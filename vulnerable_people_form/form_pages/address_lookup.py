import json

from flask import redirect, session

from ..integrations import postcode_lookup_helper
from .blueprint import form
from .shared.constants import SESSION_KEY_ADDRESS_SELECTED
from .shared.querystring_utils import append_querystring_params
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page
from .shared.session import get_errors_from_session, request_form, form_answers, is_nhs_login_user
from .shared.validation import validate_address_lookup


@form.route("/address-lookup", methods=["GET"])
def get_address_lookup():
    postcode = session.get("postcode")
    if not postcode:
        postcode = form_answers()["support_address"]["postcode"]
    try:
        addresses = postcode_lookup_helper.get_addresses_from_postcode(postcode)
    except postcode_lookup_helper.PostcodeNotFound:
        session["error_items"] = {
            **session.setdefault("error_items", {}),
            "support_address": {"postcode": "Could not find postcode, please enter your address manually"},
        }
        return redirect("/support-address")
    except postcode_lookup_helper.NoAddressesFoundAtPostcode:
        session["error_items"] = {
            **session.setdefault("error_items", {}),
            "support_address": {
                "support_address": f"No addresses found for {postcode}, please enter your address manually",
            },
        }
        return redirect("/support-address")
    except postcode_lookup_helper.ErrorFindingAddress:
        session["error_items"] = {
            **session.setdefault("error_items", {}),
            "support_address": {
                "support_address": "An error has occurred, please enter your address manually",
            },
        }
        return redirect("/support-address")

    prev_path = append_querystring_params("/nhs-letter" if is_nhs_login_user() else "/date-of-birth")

    return render_template_with_title(
        "address-lookup.html",
        previous_path=prev_path,
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
    session[SESSION_KEY_ADDRESS_SELECTED] = True
    return route_to_next_form_page()
