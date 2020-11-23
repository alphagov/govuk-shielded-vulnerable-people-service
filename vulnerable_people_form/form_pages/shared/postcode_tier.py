from vulnerable_people_form.form_pages.shared.session import set_postcode_tier
from vulnerable_people_form.integrations.postcode_eligibility import get_postcode_tier


def update_postcode_tier(postcode, app):
    if is_tiering_logic_enabled(app):
        postcode_tier = get_postcode_tier(postcode)
        set_postcode_tier(postcode_tier)


def is_tiering_logic_enabled(app):
    return "TIERING_LOGIC" in app.config and app.config["TIERING_LOGIC"] == "True"
