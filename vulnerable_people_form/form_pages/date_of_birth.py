from flask import redirect, session

from .blueprint import form
from .shared.form_utils import sanitise_date
from .shared.querystring_utils import append_querystring_params
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page
from .shared.session import form_answers, get_errors_from_session, request_form
from .shared.validation import validate_date_of_birth


@form.route("/date-of-birth", methods=["GET"])
def get_date_of_birth():
    return render_template_with_title(
        "date-of-birth.html",
        previous_path=append_querystring_params("/name"),
        values=form_answers().get("date_of_birth", {}),
        **get_errors_from_session("date_of_birth"),
    )


@form.route("/date-of-birth", methods=["POST"])
def post_date_of_birth():
    posted_date_of_birth = request_form()
    sanitise_date(posted_date_of_birth)

    session["form_answers"] = {
        **session.setdefault("form_answers", {}),
        "date_of_birth": {**posted_date_of_birth},
    }
    if not validate_date_of_birth():
        return redirect("/date-of-birth")

    session["error_items"] = {}
    return route_to_next_form_page()
