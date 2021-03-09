from .default import app_default
from .shared.render import render_template_with_title


@app_default.route("/cookies", methods=["GET"])
def get_cookies():
    return render_template_with_title("cookies.html")
