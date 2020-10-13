from flask import redirect

from .blueprint import form
from .shared.answers_enums import (
    PrioritySuperMarketDeliveriesAnswers,
    get_radio_options_from_enum,
)
from .shared.querystring_utils import append_querystring_params
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page
from .shared.session import (
    form_answers,
    get_errors_from_session,
    update_session_answers_from_form_for_enum,
)
from .shared.validation import validate_priority_supermarket_deliveries


@form.route("/priority-supermarket-deliveries", methods=["GET"])
def get_priority_supermarket_deliveries():
    return render_template_with_title(
        "priority-supermarket-deliveries.html",
        radio_items=get_radio_options_from_enum(
            PrioritySuperMarketDeliveriesAnswers,
            form_answers().get("priority_supermarket_deliveries"),
        ),
        previous_path=append_querystring_params("/do-you-have-someone-to-go-shopping-for-you"),
        **get_errors_from_session("priority_supermarket_deliveries"),
    )


@form.route("/priority-supermarket-deliveries", methods=["POST"])
def post_priority_supermarket_deliveries():
    update_session_answers_from_form_for_enum()
    if not validate_priority_supermarket_deliveries():
        return redirect("/priority-supermarket-deliveries")
    return route_to_next_form_page()
