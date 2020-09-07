from flask import current_app, render_template

from .blueprint import form


@form.route("/nhs-registration-link", methods=["GET"])
def get_nhs_registration_link():
    return render_template(
        "nhs-registration-link.html",
        previous_path="/nhs-number",
        nhs_registration_href=current_app.nhs_oidc_client.get_registration_url(),
    )
