import json
import sentry_sdk

from flask import abort, current_app, redirect, request, session

from ..integrations import google_analytics
from .blueprint import form
from .shared.constants import NHS_USER_INFO_TO_FORM_ANSWERS
from .shared.session import (
    form_answers,
    get_answer_from_form,
    get_summary_rows_from_form_answers,
    request_form,
    should_contact_gp,
    persist_answers_from_session,
)


def log_form_and_nhs_answers_differences(nhs_user_info):
    different_answers = []
    for answers_key, nhs_user_info_key in NHS_USER_INFO_TO_FORM_ANSWERS.items():
        form_value = get_answer_from_form(answers_key)
        nhs_value = (
            nhs_user_info_key(nhs_user_info)
            if callable(nhs_user_info_key)
            else nhs_user_info.get(nhs_user_info_key)
        )
        if form_value != nhs_value:
            if answers_key == ("nhs_number",):
                google_analytics.track_nhs_number_and_form_value_differs()
            else:
                different_answers.append(
                    {
                        "key": "/".join(answers_key),
                        "nhs_value": nhs_value,
                        "form_value": form_value,
                    }
                )
    if len(different_answers) > 0:
        google_analytics.track_nhs_userinfo_and_form_answers_differs()


@form.route("/nhs-registration-callback", methods=["GET"])
def get_nhs_registration_callback():
    if "error" in request.args:
        abort(500)
    nhs_user_info = current_app.nhs_oidc_client.get_nhs_user_info_from_registration_callback(
        request.args
    )
    log_form_and_nhs_answers_differences(nhs_user_info)
    session["nhs_sub"] = nhs_user_info["sub"]
    session["form_answers"]["nhs_number"] = nhs_user_info["nhs_number"]
    persist_answers_from_session()
    return redirect("/confirmation")
