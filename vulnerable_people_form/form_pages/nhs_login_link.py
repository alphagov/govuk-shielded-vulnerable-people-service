from flask import current_app, render_template

from .blueprint import form


@form.route("/nhs-login-link", methods=["GET"])
def get_nhs_login_link():
    return render_template(
        "nhs-login-link.html",
        previous_path="/nhs-login",
        nhs_login_href=current_app.nhs_oidc_client.get_authorization_url(),
    )
