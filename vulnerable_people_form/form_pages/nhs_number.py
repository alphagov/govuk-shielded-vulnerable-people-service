from flask import redirect, session

from .blueprint import form
from .shared.querystring_utils import append_querystring_params
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page
from .shared.session import (
    form_answers,
    get_errors_from_session,
    request_form,
    get_answer_from_form,
)
from .shared.validation import validate_nhs_number


@form.route("/nhs-number", methods=["GET"])
def get_nhs_number():
    previous_path = "/nhs-letter"
    if get_answer_from_form(("medical_conditions",)) is not None:
        previous_path = "/medical-conditions"

    previous_path = append_querystring_params(previous_path)
    return render_template_with_title(
        "nhs-number.html",
        previous_path=previous_path,
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
        "nhs_number": request_form().get("nhs_number").replace(" ", ""),
        "know_nhs_number": "Yes, I know my NHS number",
    }

    session["error_items"] = {}
    if not validate_nhs_number():
        return redirect("/nhs-number")

    return route_to_next_form_page()
