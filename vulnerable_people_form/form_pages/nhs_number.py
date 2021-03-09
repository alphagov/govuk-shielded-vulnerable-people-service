from flask import redirect, session

from .blueprint import form
from .shared.form_utils import clean_nhs_number
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page
from .shared.session import (
    form_answers,
    get_errors_from_session,
    request_form
)
from .shared.validation import validate_nhs_number


@form.route("/nhs-number", methods=["GET"])
def get_nhs_number():

    return render_template_with_title(
        "nhs-number.html",
        values={
            "nhs_number": form_answers().get("nhs_number", ""),
            "applying_on_own_behalf": form_answers().get("applying_on_own_behalf")
        },
        **get_errors_from_session("nhs_number"),
    )


@form.route("/nhs-number", methods=["POST"])
def post_nhs_number():
    session["form_answers"] = {
        **session.setdefault("form_answers", {}),
        "nhs_number": clean_nhs_number(request_form().get("nhs_number")),
        "know_nhs_number": "Yes, I know my NHS number",
    }

    session["error_items"] = {}
    if not validate_nhs_number():
        return redirect("/nhs-number")

    return route_to_next_form_page()
