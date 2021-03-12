from flask import session
from .blueprint import form
from .shared.render import render_template_with_title


@form.route("/confirmation", methods=["GET"])
def get_confirmation():
    rendered_template = render_template_with_title(
        "confirmation.html")
    session.clear()
    return rendered_template
