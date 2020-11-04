from flask import redirect, session

from .postcode_tier_blueprint import postcode_tier_form
from .blueprint import form
from .shared.answers_enums import ApplyingOnOwnBehalfAnswers
from .shared.querystring_utils import append_querystring_params
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page
from .shared.session import get_errors_from_session, request_form, get_answer_from_form
from .shared.validation import validate_postcode
from vulnerable_people_form.integrations.postcode_lookup_helper import format_postcode


@form.route("/postcode-eligibility", methods=["GET"])
def get_postcode_eligibility():
    applying_on_own_behalf_answer = get_answer_from_form(["applying_on_own_behalf"])
    if applying_on_own_behalf_answer == ApplyingOnOwnBehalfAnswers.YES.value:
        prev_path = "/nhs-login"
    elif applying_on_own_behalf_answer == ApplyingOnOwnBehalfAnswers.NO.value:
        prev_path = "/applying-on-own-behalf"
    else:
        raise ValueError("Unexpected ApplyingOnOwnBehalfAnswers value encountered: " + applying_on_own_behalf_answer)
    prev_path = append_querystring_params(prev_path)
    return render_template_with_title(
        "postcode-eligibility.html",
        previous_path=prev_path,
        values={"postcode": session.get("postcode", "")},
        **get_errors_from_session("postcode"),
    )


@postcode_tier_form.route("/postcode-eligibility", methods=["POST"])
def post_postcode_verification():
    session["postcode"] = format_postcode(request_form().get("postcode"))
    if not validate_postcode(session["postcode"], "postcode"):
        return redirect("/postcode-eligibility")

    session["error_items"] = {}
    return route_to_next_form_page()
