import logging

from flask import abort, current_app, redirect, request, session

from vulnerable_people_form.form_pages.shared.logger_utils import create_log_message, log_event_names, init_logger
from vulnerable_people_form.form_pages.shared.routing import (
    get_next_form_url_after_nhs_number,
    get_redirect_to_terminal_page,
    get_redirect_for_returning_user_based_on_tier
)
from .blueprint import form
from .shared.constants import NHS_USER_INFO_TO_FORM_ANSWERS, JourneyProgress
from .shared.session import (
    get_answer_from_form,
    persist_answers_from_session,
    set_form_answers_from_nhs_user_info,
    load_answers_into_session_if_available
)
from ..integrations import google_analytics

_CONFIRMATION_URL = "/confirmation"
logger = logging.getLogger(__name__)
init_logger(logger)


def _log_form_and_nhs_answers_differences(nhs_user_info):
    different_answers = []
    for answers_key, nhs_user_info_key in NHS_USER_INFO_TO_FORM_ANSWERS.items():
        form_value = get_answer_from_form(answers_key)
        nhs_value = (
            nhs_user_info_key(nhs_user_info) if callable(nhs_user_info_key) else nhs_user_info.get(nhs_user_info_key)
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
        error_description = request.args.get('error_description')
        error = request.args['error']

        if error_description == "ConsentNotGiven" and session.get('registration_number'):
            _log_no_consent(error, error_description)
            return redirect(_CONFIRMATION_URL)
        elif error_description == "ConsentNotGiven":
            _log_no_consent(error, error_description)
            return redirect("/no-consent-registration")
        else:
            logger.error(create_log_message(
                log_event_names["NHS_LOGIN_FAIL"],
                f"NHS login error: {error} , error description: {error_description}"))
            abort(500)

    state_from_query_string = request.args.get('state')
    if state_from_query_string:
        last_char_of_state = state_from_query_string[len(state_from_query_string) - 1]
        journey_progress = JourneyProgress(int(last_char_of_state))
    else:
        return abort(500)

    nhs_user_info = current_app.nhs_oidc_client.get_nhs_user_info_from_registration_callback(request.args)
    _log_form_and_nhs_answers_differences(nhs_user_info)
    session["nhs_sub"] = nhs_user_info["sub"]
    session["form_answers"]["nhs_number"] = nhs_user_info["nhs_number"]

    if load_answers_into_session_if_available():
        if current_app.is_tiering_logic_enabled and journey_progress is JourneyProgress.NHS_NUMBER:
            return get_redirect_for_returning_user_based_on_tier()
        return get_redirect_to_terminal_page()

    if journey_progress is JourneyProgress.NHS_NUMBER:
        set_form_answers_from_nhs_user_info(nhs_user_info)
        redirect_url = get_next_form_url_after_nhs_number()
    elif journey_progress is JourneyProgress.NHS_REGISTRATION:
        persist_answers_from_session()
        redirect_url = _CONFIRMATION_URL
    else:
        raise ValueError("Unexpected JourneyProgress value extracted from state: " + last_char_of_state)

    return redirect(redirect_url)


def _log_no_consent(error, error_description):
    logger.warning(create_log_message(log_event_names["NHS_LOGIN_USER_CONSENT_NOT_GIVEN"],
                                      f"NHS login warning: {error}, error description: {error_description}"))
