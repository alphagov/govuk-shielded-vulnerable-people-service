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
from .shared.validation import validate_essential_supplies


@form.route("/essential-supplies", methods=["GET"])
def get_essential_supplies():
    return render_template_with_title(
        "essential-supplies.html",
        radio_items=get_radio_options_from_enum(
            YesNoAnswers, form_answers().get("essential_supplies")
        ),
        previous_path="/nhs-number",
        **get_errors_from_session("essential_supplies"),
    )


@form.route("/essential-supplies", methods=["POST"])
def post_essential_supplies():
    update_session_answers_from_form_for_enum()
    if not validate_essential_supplies():
        return redirect("/essential-supplies")
    return route_to_next_form_page()
