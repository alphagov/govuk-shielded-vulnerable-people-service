from .default import app_default
from .shared.render import render_template_with_title


@app_default.route("/accessibility-statement", methods=["GET"])
def get_accessibility_statement():
    return render_template_with_title("accessibility.html")
