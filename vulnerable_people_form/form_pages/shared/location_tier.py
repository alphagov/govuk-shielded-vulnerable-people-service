from vulnerable_people_form.form_pages.shared.constants import PostcodeTier, PostcodeTierStatus, ShieldingAdvice
from vulnerable_people_form.form_pages.shared.session import (
        set_location_tier,
        set_is_postcode_in_england,
        set_shielding_advice,
        form_answers
        )
from vulnerable_people_form.integrations.location_eligibility import (
        get_uprn_tier,
        get_postcode_tier,
        is_postcode_in_england,
        get_ladcode_from_postcode,
        get_ladcode_from_uprn
        )


def update_is_postcode_in_england(postcode, app):
    postcode_in_england = is_postcode_in_england(postcode)

    if postcode in app.config["POSTCODE_TIER_OVERRIDE"]:
        postcode_in_england = True

    set_is_postcode_in_england(postcode_in_england)


def update_location_tier_by_uprn(uprn, app):
    if app.is_tiering_logic_enabled:
        location_tier = get_uprn_tier(uprn)
        set_location_tier(location_tier)

        lad_code = get_ladcode_from_uprn(uprn)
        if app.shielding_advice.is_la_shielding(lad_code):
            set_shielding_advice(ShieldingAdvice.ADVISED_TO_SHIELD.value)
        else:
            set_shielding_advice(ShieldingAdvice.NOT_ADVISED_TO_SHIELD.value)

        if form_answers()["support_address"]["postcode"] in app.config["POSTCODE_TIER_OVERRIDE"]:
            postcode = form_answers()["support_address"]["postcode"]
            set_location_tier(app.config["POSTCODE_TIER_OVERRIDE"][postcode]["tier"])
            set_shielding_advice(app.config["POSTCODE_TIER_OVERRIDE"][postcode]["shielding"])

    else:
        set_location_tier(PostcodeTier.VERY_HIGH_PLUS_SHIELDING.value)


def update_location_tier_by_postcode(postcode, app):
    if app.is_tiering_logic_enabled:
        location_tier = get_postcode_tier(postcode)
        set_location_tier(location_tier)

        lad_code = get_ladcode_from_postcode(postcode)
        if app.shielding_advice.is_la_shielding(lad_code):
            set_shielding_advice(ShieldingAdvice.ADVISED_TO_SHIELD.value)
        else:
            set_shielding_advice(ShieldingAdvice.NOT_ADVISED_TO_SHIELD.value)

        if postcode in app.config["POSTCODE_TIER_OVERRIDE"]:
            set_location_tier(app.config["POSTCODE_TIER_OVERRIDE"][postcode]["tier"])
            set_shielding_advice(app.config["POSTCODE_TIER_OVERRIDE"][postcode]["shielding"])

    else:
        set_location_tier(PostcodeTier.VERY_HIGH_PLUS_SHIELDING.value)


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
