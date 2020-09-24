from flask import session
from .blueprint import form
from .shared.render import render_template_with_title


@form.route("/confirmation", methods=["GET"])
def get_confirmation():
    rendered_template = render_template_with_title(
        "confirmation.html",
        registration_number=session["registration_number"])
    session.clear()
    return rendered_template
