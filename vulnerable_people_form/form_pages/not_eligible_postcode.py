from vulnerable_people_form.form_pages.shared.location_tier import is_tier_less_than_very_high
from vulnerable_people_form.form_pages.shared.session import get_location_tier, get_is_postcode_in_england
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
    location_tier = get_location_tier()
    is_postcode_in_england = get_is_postcode_in_england()
    if not is_postcode_in_england:
        return "not-eligible-postcode-not-found.html"
    if is_tier_less_than_very_high(location_tier):
        return "not-eligible-postcode-tier.html"

    return "not-eligible-postcode-not-found.html"
