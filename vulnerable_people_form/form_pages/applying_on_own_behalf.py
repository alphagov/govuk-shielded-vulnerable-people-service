from flask import redirect

from .shared.answers_enums import ApplyingOnOwnBehalfAnswers, get_radio_options_from_enum
from .blueprint import form
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page
from .shared.session import (
    form_answers,
    get_errors_from_session,
    request_form,
    update_session_answers_from_form,
)
from .shared.validation import validate_applying_on_own_behalf


@form.route("/applying-on-own-behalf", methods=["GET"])
def get_apply_on_own_behalf():
    return render_template_with_title(
        "applying-on-own-behalf.html",
        radio_items=get_radio_options_from_enum(
            ApplyingOnOwnBehalfAnswers, form_answers().get("applying_on_own_behalf")
        ),
        previous_path="/",
        **get_errors_from_session("applying_on_own_behalf"),
    )


@form.route("/applying-on-own-behalf", methods=["POST"])
def post_applying_on_own_behalf():
    update_session_answers_from_form()
    if not validate_applying_on_own_behalf():
        return redirect("/applying-on-own-behalf")
    return route_to_next_form_page()
