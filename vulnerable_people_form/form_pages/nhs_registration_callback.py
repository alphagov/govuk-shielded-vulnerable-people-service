import json

from flask import abort, current_app, redirect, request, session

from .. import form_response_model
from .blueprint import form
from .constants import NHS_USER_INFO_TO_FORM_ANSWERS
from .session_utils import (
    form_answers,
    get_answer_from_form,
    get_summary_rows_from_form_answers,
    request_form,
    should_contact_gp,
    update_session_answers_from_form,
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
            different_answers.append(
                {
                    "key": "/".join(answers_key),
                    "nhs_value": nhs_value,
                    "form_value": form_value,
                }
            )
    if len(different_answers) > 0:
        current_app.logger.warn(
            "Differences were encountered between the results collected from "
            "the NHS oidc procedure at registration, and the values entered into "
            f"the form. {json.dumps({'differences': different_answers})}"
        )


@form.route("/nhs-registration-callback", methods=["GET"])
def get_nhs_registration_callback():
    if "error" in request.args:
        abort(500)
    nhs_user_info = current_app.nhs_oidc_client.get_nhs_user_info_from_registration_callback(
        request.args
    )
    log_form_and_nhs_answers_differences(nhs_user_info)
    nhs_sub = session["nhs_sub"] = nhs_user_info["sub"]
    session["form_answers"]["nhs_number"] = nhs_user_info["nhs_number"]
    form_response_model.write_answers_to_table(nhs_sub, form_answers())
    return redirect("/registration-complete")
