from flask import session, current_app, redirect

from .blueprint import form
from .shared.constants import PostcodeTier
from .shared.querystring_utils import append_querystring_params
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page, dynamic_back_url
from .shared.session import persist_answers_from_session, get_summary_rows_from_form_answers, \
        get_location_tier, is_shielding_without_basic_care_needs_answer
from ..integrations import notifications


@form.route("/check-your-answers", methods=["GET"])
def get_check_your_answers():
    session["check_answers_page_seen"] = True
    exclude_answers = None

    if current_app.is_tiering_logic_enabled:
        if is_shielding_without_basic_care_needs_answer():
            return redirect(append_querystring_params("/basic-care-needs"))
        if get_location_tier() == PostcodeTier.VERY_HIGH.value:
            exclude_answers = ['basic_care_needs']

    return render_template_with_title(
        "check-your-answers.html",
        previous_path=dynamic_back_url(),
        summary_rows=get_summary_rows_from_form_answers(exclude_answers)
    )


@form.route("/check-your-answers", methods=["POST"])
def post_check_your_answers():
    registration_number = persist_answers_from_session()
    session["registration_number"] = registration_number

    notifications.send_message(registration_number)

    return route_to_next_form_page()
