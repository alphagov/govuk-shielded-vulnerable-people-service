from flask import current_app

from vulnerable_people_form.form_pages.shared.postcode_tier import is_tier_less_than_very_high
from vulnerable_people_form.form_pages.shared.session import get_postcode_tier
from .blueprint import form
from .shared.render import render_template_with_title
from .shared.routing import dynamic_back_url


@form.route("/not-eligible-postcode", methods=["GET"])
def get_not_eligible_postcode():
    template_name = _get_template_name()
    return render_template_with_title(template_name, previous_path=dynamic_back_url())


@form.route("/not-eligible-postcode-returning-user", methods=["GET"])
def get_not_eligible_postcode_returning_user():
    return render_template_with_title("not-eligible-postcode-returning-user.html")


@form.route("/not-eligible-postcode-returning-user-tier-not-found", methods=["GET"])
def get_not_eligible_postcode_returning_user_tier_not_found():
    return render_template_with_title("not-eligible-postcode-returning-user-tier-not-found.html")


def _get_template_name():
    if current_app.is_tiering_logic_enabled:
        postcode_tier = get_postcode_tier()
        if is_tier_less_than_very_high(postcode_tier):
            return "not-eligible-postcode-tier.html"
        return "not-eligible-postcode-tier.html" if postcode_tier else "not-eligible-postcode-not-found.html"

    return "not-eligible-postcode.html"
