from flask import current_app

from vulnerable_people_form.form_pages.shared.render import render_template_with_title
from vulnerable_people_form.form_pages.shared.routing import dynamic_back_url
from .blueprint import form


@form.route("/nhs-login-link", methods=["GET"])
def get_nhs_login_link():
    return render_template_with_title(
        "nhs-login-link.html",
        previous_path=dynamic_back_url(),
        nhs_login_href=current_app.nhs_oidc_client.get_authorization_url(),
    )
