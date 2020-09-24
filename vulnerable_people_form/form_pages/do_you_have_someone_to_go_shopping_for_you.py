from flask import redirect

from .shared.answers_enums import get_radio_options_from_enum, ShoppingAssistanceAnswers
from .blueprint import form
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page, get_back_url_for_shopping_assistance
from .shared.session import (
    form_answers,
    get_errors_from_session,
    update_session_answers_from_form_for_enum,
)
from .shared.validation import validate_do_you_have_someone_to_go_shopping_for_you


@form.route("/do-you-have-someone-to-go-shopping-for-you", methods=["GET"])
def get_do_you_have_someone_to_go_shopping_for_you():
    back_url = get_back_url_for_shopping_assistance()
    return render_template_with_title(
        "do-you-have-someone-to-go-shopping-for-you.html",
        radio_items=get_radio_options_from_enum(
            ShoppingAssistanceAnswers,
            form_answers().get("do_you_have_someone_to_go_shopping_for_you"),
        ),
        previous_path=back_url,
        **get_errors_from_session("do_you_have_someone_to_go_shopping_for_you"),
    )


@form.route("/do-you-have-someone-to-go-shopping-for-you", methods=["POST"])
def post_do_you_have_someone_to_go_shopping_for_you():
    update_session_answers_from_form_for_enum()
    if not validate_do_you_have_someone_to_go_shopping_for_you():
        return redirect("/do-you-have-someone-to-go-shopping-for-you")
    return route_to_next_form_page()
