from urllib.parse import urlparse

from flask import redirect, request

from .blueprint import form
from .shared.answers_enums import get_radio_options_from_enum, LiveInEnglandAnswers
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page, dynamic_back_url, update_lives_in_england_referrer
from .shared.session import (
    form_answers,
    get_errors_from_session,
    update_session_answers_from_form_for_enum,
)
from .shared.validation import validate_do_you_live_in_england


@form.route("/do-you-live-in-england", methods=["GET"])
def get_do_you_live_in_england():
    referrer = urlparse(request.referrer).path
    update_lives_in_england_referrer(referrer)

    return render_template_with_title(
        "do-you-live-in-england.html",
        radio_items=get_radio_options_from_enum(
            LiveInEnglandAnswers,
            form_answers().get("do_you_live_in_england"),
        ),
        previous_path=dynamic_back_url(),
        **get_errors_from_session("do_you_live_in_england"),
    )


@form.route("/do-you-live-in-england", methods=["POST"])
def post_do_you_live_in_england():
    update_session_answers_from_form_for_enum()
    if not validate_do_you_live_in_england():
        return redirect("/do-you-live-in-england")
    return route_to_next_form_page()
