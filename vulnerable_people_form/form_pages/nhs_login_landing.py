from flask import current_app, session

from .blueprint import form
from .shared.constants import GOVUK_JOURNEY_START_PAGE_URL
from .shared.render import render_template_with_title


@form.route("/nhs-login-landing", methods=["GET"])
def get_nhs_login_landing():
    session.clear()
    return render_template_with_title(
        "nhs-login-landing.html",
        nhs_login_href=current_app.nhs_oidc_client.get_authorization_url(),
        continue_url=GOVUK_JOURNEY_START_PAGE_URL
    )
