import logging

from flask import abort, current_app, redirect, request, session

from .blueprint import form
from .shared.logger_utils import init_logger, create_log_message, log_event_names
from .shared.routing import get_redirect_to_terminal_page, get_redirect_for_returning_user_based_on_tier
from .shared.session import (
    load_answers_into_session_if_available,
    set_form_answers_from_nhs_user_info
)

logger = logging.getLogger(__name__)
init_logger(logger)


@form.route("/nhs-login-callback", methods=["GET"])
def get_nhs_login_callback():
    session.permanent = True

    if "error" in request.args:
        error_description = request.args.get("error_description", "")
        error = request.args['error']

        if error_description == "ConsentNotGiven":
            logger.warning(create_log_message(log_event_names["NHS_LOGIN_USER_CONSENT_NOT_GIVEN"],
                                              f"NHS login warning: {error}, error description: {error_description}"))
            return redirect("/no-consent")
        else:
            logger.error(create_log_message(
                log_event_names["NHS_LOGIN_FAIL"],
                f"NHS login error: {error}, error description: {error_description}"))
            abort(500)

    nhs_user_info = current_app.nhs_oidc_client.get_nhs_user_info_from_authorization_callback(request.args)

    session["nhs_sub"] = nhs_user_info["sub"]

    if load_answers_into_session_if_available():
        if current_app.is_tiering_logic_enabled:
            return get_redirect_for_returning_user_based_on_tier()

        return get_redirect_to_terminal_page()

    set_form_answers_from_nhs_user_info(nhs_user_info)

    return redirect("postcode-eligibility")
