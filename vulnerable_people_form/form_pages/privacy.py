from .default import app_default
from .shared.render import render_template_with_title
from .shared.routing import dynamic_back_url


@app_default.route("/privacy", methods=["GET"])
def get_privacy():
    return render_template_with_title("privacy.html", previous_path=dynamic_back_url())
