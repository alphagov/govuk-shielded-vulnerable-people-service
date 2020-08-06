from .blueprint import form
from .shared.render import render_template_with_title
from .shared.routing import dynamic_back_url


@form.route("/not-eligible-medical", methods=["GET"])
def get_not_eligible_medical():
    return render_template_with_title(
        "not-eligible-medical.html", back_url=dynamic_back_url()
    )
