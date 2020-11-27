from vulnerable_people_form.form_pages.shared.constants import PostcodeTier, PostcodeTierStatus
from vulnerable_people_form.form_pages.shared.session import set_postcode_tier
from vulnerable_people_form.integrations.postcode_eligibility import get_postcode_tier


def update_postcode_tier(postcode, app):
    if app.is_tiering_logic_enabled:
        postcode_tier = get_postcode_tier(postcode)
        set_postcode_tier(postcode_tier)
    else:
        set_postcode_tier(PostcodeTier.VERY_HIGH_PLUS_SHIELDING.value)


def is_tier_very_high_or_above(postcode_tier):
    return postcode_tier is not None \
           and (postcode_tier in [PostcodeTier.VERY_HIGH.value, PostcodeTier.VERY_HIGH_PLUS_SHIELDING.value])


def is_tier_less_than_very_high(postcode_tier):
    return postcode_tier is not None and (postcode_tier in [PostcodeTier.MEDIUM.value, PostcodeTier.HIGH.value])


def get_latest_postcode_tier(original_postcode, original_postcode_tier):
    latest_postcode_tier = get_postcode_tier(original_postcode)

    if latest_postcode_tier is None:
        return latest_postcode_tier

    if latest_postcode_tier == original_postcode_tier:
        change_status = PostcodeTierStatus.NO_CHANGE
    elif latest_postcode_tier < original_postcode_tier:
        change_status = PostcodeTierStatus.DECREASED
    elif latest_postcode_tier > original_postcode_tier:
        change_status = PostcodeTierStatus.INCREASED

    return {
        "latest_postcode_tier": latest_postcode_tier,
        "change_status": change_status.value
    }
