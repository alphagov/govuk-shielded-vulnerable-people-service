from .blueprint import form
from .render_utils import render_template_with_title
from .routing_utils import dynamic_back_url


@form.route("/accessibility-statement", methods=["GET"])
def get_accessibility_statement():
    return render_template_with_title("accessibility.html", back_url=dynamic_back_url)
