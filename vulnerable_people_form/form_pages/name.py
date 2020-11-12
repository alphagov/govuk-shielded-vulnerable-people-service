from flask import redirect, session

from .blueprint import form
from .shared.form_utils import sanitise_name
from .shared.querystring_utils import append_querystring_params
from .shared.render import render_template_with_title
from .shared.routing import route_to_next_form_page
from .shared.session import form_answers, get_errors_from_session, request_form
from .shared.validation import validate_name


@form.route("/name", methods=["GET"])
def get_name():
    return render_template_with_title(
        "name.html",
        values=form_answers().get("name", {}),
        previous_path=append_querystring_params("/nhs-number"),
        **get_errors_from_session("name"),
    )


@form.route("/name", methods=["POST"])
def post_name():
    posted_name = sanitise_name(request_form())

    session["form_answers"] = {
        **session.setdefault("form_answers", {}),
        "name": {**posted_name},
    }
    if not validate_name():
        return redirect("/name")

    session["error_items"] = {}
    return route_to_next_form_page()
