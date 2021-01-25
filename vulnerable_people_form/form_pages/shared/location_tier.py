from vulnerable_people_form.form_pages.shared.constants import PostcodeTier, PostcodeTierStatus,\
                                                               ShieldingAdviceStatus
from vulnerable_people_form.form_pages.shared.session import (
        set_location_tier,
        set_is_postcode_in_england,
        set_shielding_advice,
        form_answers
        )
from vulnerable_people_form.integrations.location_eligibility import (
        is_postcode_in_england,
        get_shielding_advice_by_postcode,
        get_shielding_advice_by_uprn,
        get_uprn_tier,
        get_postcode_tier
        )


def update_is_postcode_in_england(postcode, app):
    postcode_in_england = is_postcode_in_england(postcode)

    if postcode in app.postcode_tier_override:
        postcode_in_england = True

    set_is_postcode_in_england(postcode_in_england)


def override_location_status_if_test_postcode(postcode, app):
    if postcode in app.postcode_tier_override:
        set_location_tier(app.postcode_tier_override[postcode]["tier"])
        set_shielding_advice(app.postcode_tier_override[postcode]["shielding"])


def update_location_status_by_uprn(uprn, app):
    location_tier = get_uprn_tier(uprn)
    set_location_tier(location_tier)
    shielding_advice = get_shielding_advice_by_uprn(uprn)
    set_shielding_advice(shielding_advice)
    override_location_status_if_test_postcode(form_answers()["support_address"]["postcode"], app)


def update_location_status_by_postcode(postcode, app):
    location_tier = get_postcode_tier(postcode)
    set_location_tier(location_tier)
    shielding_advice = get_shielding_advice_by_postcode(postcode)
    set_shielding_advice(shielding_advice)
    override_location_status_if_test_postcode(postcode, app)


def is_tier_very_high_or_above(location_tier):
    return location_tier is not None \
           and (location_tier in [PostcodeTier.VERY_HIGH.value, PostcodeTier.VERY_HIGH_PLUS_SHIELDING.value])


def is_tier_less_than_very_high(location_tier):
    return location_tier is not None and (location_tier in [PostcodeTier.MEDIUM.value, PostcodeTier.HIGH.value])


def get_latest_location_tier(latest_location_tier, original_location_tier):
    if latest_location_tier is None:
        return latest_location_tier

    if latest_location_tier == original_location_tier:
        change_status = PostcodeTierStatus.NO_CHANGE
    elif latest_location_tier < original_location_tier:
        change_status = PostcodeTierStatus.DECREASED
    elif latest_location_tier > original_location_tier:
        change_status = PostcodeTierStatus.INCREASED

    return {
        "latest_location_tier": latest_location_tier,
        "change_status": change_status.value
    }


def get_latest_shielding_advice(latest_shielding_advice, original_shielding_advice):
    if latest_shielding_advice is None:
        return latest_shielding_advice

    if latest_shielding_advice == original_shielding_advice:
        change_status = ShieldingAdviceStatus.NO_CHANGE
    elif latest_shielding_advice < original_shielding_advice:
        change_status = ShieldingAdviceStatus.DECREASED
    elif latest_shielding_advice > original_shielding_advice:
        change_status = ShieldingAdviceStatus.INCREASED

    return {
        "latest_shielding_advice": latest_shielding_advice,
        "change_status": change_status.value
    }
