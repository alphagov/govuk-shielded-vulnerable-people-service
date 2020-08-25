from flask import redirect

from .shared.answers_enums import YesNoAnswers, get_radio_options_from_enum
from .blueprint import form
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page
from .shared.session import (
    form_answers,
    get_errors_from_session,
    request_form,
    update_session_answers_from_form_for_enum,
)
from .shared.validation import validate_carry_supplies


@form.route("/carry-supplies", methods=["GET"])
def get_carry_supplies():
    return render_template_with_title(
        "carry-supplies.html",
        radio_items=get_radio_options_from_enum(
            YesNoAnswers, form_answers().get("carry_supplies")
        ),
        previous_path="/dietary-requirements",
        **get_errors_from_session("carry_supplies"),
    )


@form.route("/carry-supplies", methods=["POST"])
def post_carry_supplies():
    update_session_answers_from_form_for_enum()
    if not validate_carry_supplies():
        return redirect("/carry-supplies")
    return route_to_next_form_page()