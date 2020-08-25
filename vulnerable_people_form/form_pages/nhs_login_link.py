from flask import session, current_app, render_template

from ..integrations import govuk_notify_client
from .blueprint import form
from .shared.routing import route_to_next_form_page
from .shared.session import (
    form_answers,
    persist_answers_from_session,
    get_answer_from_form,
    get_summary_rows_from_form_answers,
    request_form,
    should_contact_gp,
)


@form.route("/nhs-login-link", methods=["GET"])
def get_nhs_login_link():
    return render_template(
        "nhs-login-link.html",
        previous_path="/nhs-login",
        nhs_login_href=current_app.nhs_oidc_client.get_authorization_url(),
    )
