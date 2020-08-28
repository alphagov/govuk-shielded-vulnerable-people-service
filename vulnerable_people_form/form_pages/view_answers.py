from flask import session

from .blueprint import form
from .shared.render import render_template_with_title
from .shared.routing import dynamic_back_url
from .shared.session import (
    get_summary_rows_from_form_answers,
    load_answers_into_session_if_available,
)


@form.route("/view-answers", methods=["GET"])
def get_view_answers():
    session["check_answers_page_seen"] = True
    return render_template_with_title(
        "view-answers.html",
        summary_rows=get_summary_rows_from_form_answers(),
        previous_path=dynamic_back_url(),
    )
