from vulnerable_people_form.form_pages.shared.render import render_template_with_title
from vulnerable_people_form.form_pages.shared.querystring_utils import append_querystring_params
from .blueprint import form


@form.route("/no-consent", methods=["GET"])
def get_nhs_login_no_consent():
    return render_template_with_title(
        "nhs-login-no-consent.html",
        continue_url=append_querystring_params("/postcode-eligibility"),
        hint_text="You can still register, then decide to share your NHS login information later."
    )


@form.route("/no-consent-registration", methods=["GET"])
def get_nhs_login_no_consent_registration():
    return render_template_with_title(
        "nhs-login-no-consent.html",
        continue_url=append_querystring_params("/nhs-number"),
        hint_text="This means you will need to enter an NHS number."
    )
