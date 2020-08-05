from flask import redirect, session

from .. import form_response_model, govuk_notify_client
from .blueprint import form
from .render_utils import render_template_with_title
from .session_utils import (
    form_answers,
    get_answer_from_form,
    get_summary_rows_from_form_answers,
    request_form,
    should_contact_gp,
    update_session_answers_from_form,
)
from .validation import try_validating_answers_against_json_schema


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
    try_validating_answers_against_json_schema()
    # We use a slightly strange value here for non-nhs login users. DynamoDB
    # does not allow us to not set a value for the key schema, so we set it to
    # an invalid oidc subject identifier (one that is > 255 chars)
    reference_number = form_response_model.write_answers_to_table(
        session.get("nhs_sub", f"non_nhs_login_dummy_sub{' ' * 255}"), form_answers()
    )
    send_sms_and_email_notifications_if_applicable(reference_number)

    return redirect("/confirmation",)
