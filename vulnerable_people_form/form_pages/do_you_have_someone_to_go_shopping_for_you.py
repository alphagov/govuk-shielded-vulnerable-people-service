from flask import redirect, session

from .shared.answers_enums import YesNoAnswers, get_radio_options_from_enum
from .blueprint import form
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page
from .shared.session import (
    form_answers,
    get_errors_from_session,
    update_session_answers_from_form_for_enum,
)
from .shared.validation import validate_do_you_have_someone_to_go_shopping_for_you


@form.route("/do-you-have-someone-to-go-shopping-for-you", methods=["GET"])
def get_do_you_have_someone_to_go_shopping_for_you():
    prev_path = "/address-lookup" if session["auto_populated_address_selected"] else "/support-address"
    return render_template_with_title(
        "do-you-have-someone-to-go-shopping-for-you.html",
        radio_items=get_radio_options_from_enum(
            YesNoAnswers,
            form_answers().get("do_you_have_someone_to_go_shopping_for_you"),
        ),
        previous_path=prev_path,
        **get_errors_from_session("do_you_have_someone_to_go_shopping_for_you"),
    )


@form.route("/do-you-have-someone-to-go-shopping-for-you", methods=["POST"])
def post_do_you_have_someone_to_go_shopping_for_you():
    update_session_answers_from_form_for_enum()
    if not validate_do_you_have_someone_to_go_shopping_for_you():
        return redirect("/do-you-have-someone-to-go-shopping-for-you")
    return route_to_next_form_page()
