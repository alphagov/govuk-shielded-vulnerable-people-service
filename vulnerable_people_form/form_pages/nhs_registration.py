from flask import current_app, redirect

from .shared.answers_enums import YesNoAnswers, get_radio_options_from_enum
from .blueprint import form
from .shared.render import render_template_with_title
from .shared.session import (
    form_answers,
    get_errors_from_session,
    request_form,
    update_session_answers_from_form,
)
from .shared.validation import validate_register_with_nhs


@form.route("/nhs-registration", methods=["GET"])
def get_nhs_registration():
    return render_template_with_title(
        "nhs-registration.html",
        radio_items=get_radio_options_from_enum(
            YesNoAnswers, form_answers().get("nhs_registration")
        ),
        previous_path="/basic-care-needs",
        **get_errors_from_session("nhs_registration"),
    )


@form.route("/nhs-registration", methods=["POST"])
def post_nhs_registration():
    if not validate_register_with_nhs():
        return redirect("/nhs-registration")
    answer = YesNoAnswers(request_form()["nhs_registration"])
    if answer is YesNoAnswers.YES:
        return redirect(current_app.nhs_oidc_client.get_registration_url())
    else:
        return redirect("/confirmation")
