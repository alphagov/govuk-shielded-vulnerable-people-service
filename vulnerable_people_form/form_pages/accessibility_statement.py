from .default import app_default
from .shared.render import render_template_with_title
from .shared.routing import dynamic_back_url


@app_default.route("/accessibility-statement", methods=["GET"])
def get_accessibility_statement():
    return render_template_with_title("accessibility.html", previous_path=dynamic_back_url())
