from .blueprint import form
from .shared.render import render_template_with_title
from .shared.routing import dynamic_back_url


@form.route("/not-eligible-england", methods=["GET"])
def get_not_eligible_england():
    return render_template_with_title(
        "not-eligible-england.html", back_url=dynamic_back_url()
    )
