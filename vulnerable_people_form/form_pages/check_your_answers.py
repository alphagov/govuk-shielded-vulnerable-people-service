from flask import session, redirect

from .blueprint import form
from .shared.constants import ShieldingAdvice
from .shared.querystring_utils import append_querystring_params
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page
from .shared.session import persist_answers_from_session, get_summary_rows_from_form_answers, \
     is_shielding_without_basic_care_needs_answer, get_shielding_advice
from ..integrations import notifications


@form.route("/check-your-answers", methods=["GET"])
def get_check_your_answers():
    session["check_answers_page_seen"] = True
    exclude_answers = None

    if is_shielding_without_basic_care_needs_answer():
        return redirect(append_querystring_params("/basic-care-needs"))
    if get_shielding_advice() == ShieldingAdvice.NOT_ADVISED_TO_SHIELD.value:
        exclude_answers = ['basic_care_needs']

    return render_template_with_title(
        "check-your-answers.html",
        summary_rows=get_summary_rows_from_form_answers(exclude_answers)
    )


@form.route("/check-your-answers", methods=["POST"])
def post_check_your_answers():
    registration_number = persist_answers_from_session()
    session["registration_number"] = registration_number

    notifications.send_message(registration_number)

    return route_to_next_form_page()
