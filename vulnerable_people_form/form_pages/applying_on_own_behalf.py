from flask import redirect

from .blueprint import form
from .shared.answers_enums import (
    ApplyingOnOwnBehalfAnswers,
    get_radio_options_from_enum,
)
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page, dynamic_back_url
from .shared.session import (
    form_answers,
    get_errors_from_session,
    update_session_answers_from_form_for_enum,
)
from .shared.validation import validate_applying_on_own_behalf


@form.route("/applying-on-own-behalf", methods=["GET"])
def get_apply_on_own_behalf():
    return render_template_with_title(
        "applying-on-own-behalf.html",
        radio_items=get_radio_options_from_enum(
            ApplyingOnOwnBehalfAnswers, form_answers().get("applying_on_own_behalf")
        ),
        previous_path=dynamic_back_url(),
        **get_errors_from_session("applying_on_own_behalf"),
    )


@form.route("/applying-on-own-behalf", methods=["POST"])
def post_applying_on_own_behalf():
    update_session_answers_from_form_for_enum()
    if not validate_applying_on_own_behalf():
        return redirect("/applying-on-own-behalf")
    return route_to_next_form_page()
