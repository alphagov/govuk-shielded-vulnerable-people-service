from flask import session

from .blueprint import form
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page, dynamic_back_url
from .shared.session import persist_answers_from_session, form_answers, get_summary_rows_from_form_answers
from ..integrations import govuk_notify_client, spl_check


@form.route("/check-your-answers", methods=["GET"])
def get_check_your_answers():
    session["check_answers_page_seen"] = True
    return render_template_with_title(
        "check-your-answers.html",
        previous_path=dynamic_back_url(),
        summary_rows=get_summary_rows_from_form_answers(),
    )


@form.route("/check-your-answers", methods=["POST"])
def post_check_your_answers():
    registration_number = persist_answers_from_session()
    session["registration_number"] = registration_number

    return route_to_next_form_page()
