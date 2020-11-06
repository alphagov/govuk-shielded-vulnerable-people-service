from flask import current_app

from .blueprint import form
from .shared.constants import JourneyProgress
from .shared.render import render_template_with_title


@form.route("/nhs-registration", methods=["GET"])
def get_nhs_registration():
    return render_template_with_title(
        "nhs-registration.html",
        nhs_registration_href=current_app.nhs_oidc_client.get_registration_url(JourneyProgress.NHS_REGISTRATION),
    )
