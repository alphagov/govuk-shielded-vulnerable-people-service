from flask import redirect

from .shared.answers_enums import MedicalConditionsAnswers, get_radio_options_from_enum
from .blueprint import form
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page
from .shared.session import (
    form_answers,
    get_errors_from_session,
    update_session_answers_from_form_for_enum,
)
from .shared.validation import validate_medical_conditions


@form.route("/medical-conditions", methods=["POST"])
def post_medical_conditions():
    update_session_answers_from_form_for_enum()
    if not validate_medical_conditions():
        return redirect("/medical-conditions")
    return route_to_next_form_page()


@form.route("/medical-conditions", methods=["GET"])
def get_medical_conditions():
    return render_template_with_title(
        "medical-conditions.html",
        radio_items=get_radio_options_from_enum(MedicalConditionsAnswers, form_answers().get("medical_conditions")),
        previous_path="/nhs-letter",
        **get_errors_from_session("medical_conditions"),
    )
