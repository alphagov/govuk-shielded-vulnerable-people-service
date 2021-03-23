from .default import app_default
from .shared.render import render_template_with_title


@app_default.route("/privacy", methods=["GET"])
def get_privacy():
    return render_template_with_title("privacy.html")
