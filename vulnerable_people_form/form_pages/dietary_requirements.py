from flask import redirect

from .answers_enums import YesNoAnswers, get_radio_options_from_enum
from .blueprint import form
from .render_utils import render_template_with_title
from .routing_utils import route_to_next_form_page
from .session_utils import (
    form_answers,
    get_errors_from_session,
    request_form,
    update_session_answers_from_form,
)
from .validation import validate_dietary_requirements


@form.route("/dietary-requirements", methods=["GET"])
def get_dietary_requirements():
    return render_template_with_title(
        "dietary-requirements.html",
        radio_items=get_radio_options_from_enum(
            YesNoAnswers, form_answers().get("dietary_requirements")
        ),
        previous_path="/essential-supplies",
        **get_errors_from_session("dietary_requirements"),
    )


@form.route("/dietary-requirements", methods=["POST"])
def post_dietary_requirements():
    update_session_answers_from_form()
    if not validate_dietary_requirements():
        return redirect("/dietary-requirements")
    return route_to_next_form_page()
