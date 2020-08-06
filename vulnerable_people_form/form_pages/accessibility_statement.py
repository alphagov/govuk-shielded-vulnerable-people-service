from .blueprint import form
from .shared.render import render_template_with_title
from .shared.routing import dynamic_back_url


@form.route("/accessibility-statement", methods=["GET"])
def get_accessibility_statement():
    return render_template_with_title("accessibility.html", back_url=dynamic_back_url)
