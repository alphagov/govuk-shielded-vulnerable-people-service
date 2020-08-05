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
from .validation import validate_live_in_england


@form.route("/live-in-england", methods=["GET"])
def get_live_in_england():
    return render_template_with_title(
        "live-in-england.html",
        radio_items=get_radio_options_from_enum(
            YesNoAnswers, form_answers().get("live_in_england")
        ),
        previous_path="/applying-on-own-behalf",
        **get_errors_from_session("live_in_england"),
    )


@form.route("/live-in-england", methods=["POST"])
def post_live_in_england():
    update_session_answers_from_form()
    if not validate_live_in_england():
        return redirect("/live-in-england")
    return route_to_next_form_page()
