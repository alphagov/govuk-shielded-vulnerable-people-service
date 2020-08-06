from .blueprint import form
from .shared.render import render_template_with_title
from .shared.routing import dynamic_back_url


@form.route("/privacy", methods=["GET"])
def get_privacy():
    return render_template_with_title("privacy.html", back_url=dynamic_back_url)
