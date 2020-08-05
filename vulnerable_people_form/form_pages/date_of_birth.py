from flask import redirect, session

from .blueprint import form
from .render_utils import render_template_with_title
from .routing_utils import route_to_next_form_page
from .session_utils import form_answers, get_errors_from_session, request_form
from .validation import validate_date_of_birth


@form.route("/date-of-birth", methods=["GET"])
def get_date_of_birth():
    return render_template_with_title(
        "date-of-birth.html",
        previous_path="/name",
        values=form_answers().get("date_of_birth", {}),
        **get_errors_from_session("date_of_birth"),
    )


@form.route("/date-of-birth", methods=["POST"])
def post_date_of_birth():
    session["form_answers"] = {
        **session.setdefault("form_answers", {}),
        "date_of_birth": {**request_form()},
    }
    if not validate_date_of_birth():
        return redirect("/date-of-birth")

    session["error_items"] = {}
    return route_to_next_form_page()
