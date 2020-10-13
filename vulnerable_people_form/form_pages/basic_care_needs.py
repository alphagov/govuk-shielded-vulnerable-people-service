from flask import redirect

from .blueprint import form
from .shared.answers_enums import get_radio_options_from_enum, BasicCareNeedsAnswers
from .shared.querystring_utils import append_querystring_params
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page
from .shared.session import (
    form_answers,
    get_errors_from_session,
    update_session_answers_from_form_for_enum,
)
from .shared.validation import validate_basic_care_needs


@form.route("/basic-care-needs", methods=["GET"])
def get_basic_care_needs():
    prev_path = "/priority-supermarket-deliveries" \
        if form_answers().get("priority_supermarket_deliveries") is not None \
        else "/do-you-have-someone-to-go-shopping-for-you"
    prev_path = append_querystring_params(prev_path)
    return render_template_with_title(
        "basic-care-needs.html",
        previous_path=prev_path,
        radio_items=get_radio_options_from_enum(BasicCareNeedsAnswers, form_answers().get("basic_care_needs")),
        **get_errors_from_session("basic_care_needs"),
    )


@form.route("/basic-care-needs", methods=["POST"])
def post_basic_care_needs():
    update_session_answers_from_form_for_enum()
    if not validate_basic_care_needs():
        return redirect("/basic-care-needs")
    return route_to_next_form_page()
