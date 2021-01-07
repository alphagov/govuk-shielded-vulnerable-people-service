import json

from flask import redirect, session, current_app

from ..integrations import postcode_lookup_helper, location_eligibility
from .blueprint import form
from .shared.constants import SESSION_KEY_ADDRESS_SELECTED
from .shared.querystring_utils import append_querystring_params
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page
from .shared.session import get_errors_from_session, request_form, form_answers
from .shared.validation import validate_address_lookup
from .shared.location_tier import update_location_status_by_uprn, update_location_status_by_postcode


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
        if postcode in current_app.postcode_tier_override:
            addresses = _create_test_address(postcode)
        else:
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

    prev_path = append_querystring_params("/postcode-eligibility")

    return render_template_with_title(
        "address-lookup.html",
        previous_path=prev_path,
        postcode=postcode,
        addresses=addresses,
        **get_errors_from_session("postcode"),
    )


def _create_test_address(postcode):
    return [{
        "text": f"{current_app.postcode_tier_override[postcode]}, Test Lane, City, {postcode}",
        "value": json.dumps({"uprn": None,
                             "town_city": "Test",
                             "postcode": postcode,
                             "building_and_street_line_1": f"{current_app.config['POSTCODE_TIER_OVERRIDE'][postcode]} Test Lane", # noqa
                             "building_and_street_line_2": ""})
    }]


@form.route("/address-lookup", methods=["POST"])
def post_address_lookup():
    session["form_answers"] = {
        **session.setdefault("form_answers", {}),
        "support_address": {**json.loads(request_form()["address"])},
    }
    session["error_items"] = {}

    if not validate_address_lookup():
        return redirect("/address-lookup")

    uprn = {**json.loads(request_form()["address"])}.get("uprn", None)

    if uprn and location_eligibility.get_uprn_tier(uprn):
        update_location_status_by_uprn(uprn, current_app)
    else:
        update_location_status_by_postcode(session["postcode"], current_app)

    session[SESSION_KEY_ADDRESS_SELECTED] = True
    return route_to_next_form_page()
