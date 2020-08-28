from flask import abort, current_app, redirect, request, session

from .blueprint import form
from .shared.constants import NHS_USER_INFO_TO_FORM_ANSWERS
from .shared.routing import get_redirect_to_terminal_page
from .shared.session import (
    form_answers,
    get_answer_from_form,
    get_summary_rows_from_form_answers,
    load_answers_into_session_if_available,
    request_form,
    should_contact_gp,
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

    session["nhs_sub"] = nhs_user_info["sub"]

    if load_answers_into_session_if_available():
        return get_redirect_to_terminal_page()

    set_form_answers_from_nhs_userinfo(nhs_user_info)

    return redirect("postcode-eligibility")


@form.route("/start", methods=["GET"])
def get_start():
    session.clear()
    return redirect("/applying-on-own-behalf")


@form.route("/", methods=["GET"])
def get_default_route():
    session.clear()
    return redirect("/applying-on-own-behalf")
