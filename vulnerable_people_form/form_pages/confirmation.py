from .blueprint import form
from .render_utils import render_template_with_title
from .session_utils import should_contact_gp


@form.route("/confirmation", methods=["GET"])
def get_confirmation():
    return render_template_with_title(
        "confirmation.html", contact_gp=should_contact_gp()
    )
