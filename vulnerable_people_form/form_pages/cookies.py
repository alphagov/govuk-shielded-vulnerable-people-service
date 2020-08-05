from .blueprint import form
from .render_utils import render_template_with_title
from .routing_utils import dynamic_back_url


@form.route("/cookies", methods=["GET"])
def get_cookies():
    return render_template_with_title("cookies.html", back_url=dynamic_back_url())
