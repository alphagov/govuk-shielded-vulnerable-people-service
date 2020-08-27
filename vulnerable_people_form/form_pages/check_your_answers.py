from flask import redirect, session

from ..integrations import govuk_notify_client
from .blueprint import form
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page
from .shared.session import (
    form_answers,
    persist_answers_from_session,
    get_answer_from_form,
    get_summary_rows_from_form_answers,
    request_form,
    should_contact_gp,
)


def send_sms_and_email_notifications_if_applicable(reference_number):
    first_name = get_answer_from_form(["name", "first_name"])
    last_name = get_answer_from_form(["name", "last_name"])
    phone_number = get_answer_from_form(["contact_details", "phone_number_texts"])
    email = get_answer_from_form(["contact_details", "email"])
    contact_gp = should_contact_gp()

    if phone_number:
        govuk_notify_client.try_send_confirmation_sms(
            phone_number, first_name, last_name, contact_gp
        )
    if email:
        govuk_notify_client.try_send_confirmation_email(
            phone_number, first_name, last_name, reference_number, contact_gp
        )


@form.route("/check-your-answers", methods=["GET"])
def get_check_your_answers():
    session["check_answers_page_seen"] = True
    return render_template_with_title(
        "check-your-answers.html",
        previous_path="/basic-care-needs",
        summary_rows=get_summary_rows_from_form_answers(),
    )


@form.route("/check-your-answers", methods=["POST"])
def post_check_your_answers():
    registration_number = persist_answers_from_session()
    session["registration_number"] = registration_number
    send_sms_and_email_notifications_if_applicable(registration_number)

    return route_to_next_form_page()
