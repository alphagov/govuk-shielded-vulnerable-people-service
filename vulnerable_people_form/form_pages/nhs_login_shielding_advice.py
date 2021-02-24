from vulnerable_people_form.form_pages.shared.render import render_template_with_title
from vulnerable_people_form.form_pages.shared.querystring_utils import append_querystring_params
from .blueprint import form


@form.route("/shielding-advice", methods=["GET"])
def get_nhs_login_shielding_advice():
    return render_template_with_title(
        "nhs-login-shielding-advice.html",
        continue_url=append_querystring_params("/basic-care-needs")
    )
