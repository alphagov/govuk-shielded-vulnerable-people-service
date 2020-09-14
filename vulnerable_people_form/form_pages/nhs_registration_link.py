from flask import current_app, render_template

from vulnerable_people_form.form_pages.shared.constants import JourneyProgress
from .blueprint import form


@form.route("/nhs-registration-link", methods=["GET"])
def get_nhs_registration_link():
    return render_template(
        "nhs-registration-link.html",
        previous_path="/nhs-number",
        nhs_registration_href=current_app.nhs_oidc_client.get_registration_url(JourneyProgress.NHS_NUMBER),
    )
