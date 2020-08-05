from flask import redirect

from .answers_enums import NHSLetterAnswers, get_radio_options_from_enum
from .blueprint import form
from .render_utils import render_template_with_title
from .routing_utils import route_to_next_form_page
from .session_utils import (
    form_answers,
    get_errors_from_session,
    update_session_answers_from_form,
)
from .validation import validate_nhs_letter


@form.route("/nhs-letter", methods=["GET"])
def get_nhs_letter():
    return render_template_with_title(
        "nhs-letter.html",
        radio_items=get_radio_options_from_enum(
            NHSLetterAnswers, form_answers().get("nhs_letter")
        ),
        previous_path="/live-in-england",
        **get_errors_from_session("nhs_letter"),
    )


@form.route("/nhs-letter", methods=["POST"])
def post_nhs_letter():
    update_session_answers_from_form()
    if not validate_nhs_letter():
        return redirect("/nhs-letter")
    return route_to_next_form_page()
