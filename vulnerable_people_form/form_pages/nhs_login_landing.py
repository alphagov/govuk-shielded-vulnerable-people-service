from flask import current_app, session

from .blueprint import form
from .shared.render import render_template_with_title
from .shared.querystring_utils import append_querystring_params


@form.route("/nhs-login-landing", methods=["GET"])
def get_nhs_login_landing():
    session.clear()
    return render_template_with_title(
        "nhs-login-landing.html",
        nhs_login_href=current_app.nhs_oidc_client.get_authorization_url(),
        continue_url=append_querystring_params("/applying-on-own-behalf")
    )
