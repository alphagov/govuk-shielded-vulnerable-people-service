from vulnerable_people_form.form_pages.shared.constants import PostcodeTier
from vulnerable_people_form.form_pages.shared.session import set_postcode_tier
from vulnerable_people_form.integrations.postcode_eligibility import get_postcode_tier


def update_postcode_tier(postcode, app):
    if app.is_tiering_logic_enabled:
        postcode_tier = get_postcode_tier(postcode)
        set_postcode_tier(postcode_tier)


def is_tier_very_high_or_above(postcode_tier):
    return postcode_tier is not None and (postcode_tier == PostcodeTier.VERY_HIGH.value
                                          or postcode_tier == PostcodeTier.VERY_HIGH_PLUS_SHIELDING.value)
