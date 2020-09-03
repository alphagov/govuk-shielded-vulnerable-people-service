from flask import current_app

from .blueprint import form
from .shared.answers_enums import YesNoAnswers, get_radio_options_from_enum
from .shared.render import render_template_with_title
from .shared.session import (
    form_answers,
    get_errors_from_session,
)


@form.route("/nhs-registration", methods=["GET"])
def get_nhs_registration():
    return render_template_with_title(
        "nhs-registration.html",
        radio_items=get_radio_options_from_enum(
            YesNoAnswers, form_answers().get("nhs_registration")
        ),
        nhs_registration_href=current_app.nhs_oidc_client.get_registration_url(),
        previous_path="/basic-care-needs",
        **get_errors_from_session("nhs_registration"),
    )
