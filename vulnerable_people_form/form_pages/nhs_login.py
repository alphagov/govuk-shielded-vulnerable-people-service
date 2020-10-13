from flask import redirect

from .blueprint import form
from .shared.answers_enums import YesNoAnswers, get_radio_options_from_enum
from .shared.querystring_utils import append_querystring_params
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page
from .shared.session import (
    form_answers,
    get_errors_from_session,
    update_session_answers_from_form_for_enum,
)
from .shared.validation import validate_nhs_login


@form.route("/nhs-login", methods=["GET"])
def get_nhs_login():
    return render_template_with_title(
        "nhs-login.html",
        radio_items=get_radio_options_from_enum(YesNoAnswers, form_answers().get("nhs_login")),
        previous_path=append_querystring_params("/applying-on-own-behalf"),
        **get_errors_from_session("nhs_login"),
    )


@form.route("/nhs-login", methods=["POST"])
def post_nhs_login():
    update_session_answers_from_form_for_enum()
    if not validate_nhs_login():
        return redirect("/nhs-login")
    return route_to_next_form_page()
