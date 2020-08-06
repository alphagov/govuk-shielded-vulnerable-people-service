from flask import abort, current_app, redirect, request, session

from ..integrations import form_response_model
from .blueprint import form
from .shared.constants import NHS_USER_INFO_TO_FORM_ANSWERS
from .shared.routing import get_redirect_to_terminal_page
from .shared.session import (
    form_answers,
    get_answer_from_form,
    get_summary_rows_from_form_answers,
    request_form,
    should_contact_gp,
    update_session_answers_from_form,
)


def set_form_answers_from_nhs_userinfo(nhs_user_info):
    for answers_key, maybe_key in NHS_USER_INFO_TO_FORM_ANSWERS.items():
        nhs_answer = (
            maybe_key(nhs_user_info)
            if callable(maybe_key)
            else nhs_user_info.get(maybe_key)
        )
        if nhs_answer is None:
            continue
        set_form_answer(answers_key, nhs_answer)


def set_form_answer(answers_key_list, answer):
    answers = session["form_answers"]
    for key in answers_key_list[:-1]:
        answers = answers.setdefault(key, {})
    answers[answers_key_list[-1]] = answer


@form.route("/nhs-login-callback", methods=["GET"])
def get_nhs_login_callback():
    session.permanent = True
    if "error" in request.args:
        abort(500)
    nhs_user_info = current_app.nhs_oidc_client.get_nhs_user_info_from_authorization_callback(
        request.args
    )

    nhs_sub = session["nhs_sub"] = nhs_user_info["sub"]

    existing_record = form_response_model.get_record_using_nhs_sub(nhs_sub)
    if existing_record:
        session["form_answers"] = {**existing_record["FormResponse"], **form_answers()}
        session["accessing_saved_answers"] = True
        return get_redirect_to_terminal_page()

    set_form_answers_from_nhs_userinfo(nhs_user_info)
    session["form_answers"]["know_nhs_number"] = True  # required for validation

    return redirect("postcode-eligibility")


@form.route("/start", methods=["GET"])
def get_start():
    return redirect("/view-or-setup")
