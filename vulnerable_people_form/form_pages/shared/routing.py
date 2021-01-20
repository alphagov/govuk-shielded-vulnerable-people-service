from flask import redirect, request, session, current_app

from ...integrations import location_eligibility
from .answers_enums import (
    ApplyingOnOwnBehalfAnswers,
    MedicalConditionsAnswers,
    NHSLetterAnswers,
    LiveInEnglandAnswers,
    YesNoAnswers,
    ShoppingAssistanceAnswers)
from .constants import (
    SESSION_KEY_ADDRESS_SELECTED,
    SESSION_KEY_LIVES_IN_ENGLAND_REFERRER,
    PostcodeTier,
    ShieldingAdvice,
    PostcodeTierStatus,
    ShieldingAdviceStatus
)
from .location_tier import is_tier_very_high_or_above, get_latest_location_tier, get_latest_shielding_advice
from .querystring_utils import append_querystring_params
from .session import (
    accessing_saved_answers,
    form_answers,
    is_nhs_login_user,
    persist_answers_from_session,
    get_is_postcode_in_england,
    get_location_tier, set_location_tier,
    set_shielding_advice,
    get_shielding_advice)
from .validation import (
    validate_date_of_birth,
    validate_nhs_number,
    validate_name
)

FORM_PAGE_TO_DATA_CHECK_SECTION_NAME = {
    "address-lookup": "support_address",
    "applying-on-own-behalf": "applying_on_own_behalf",
    "basic-care-needs": "basic_care_needs",
    "check-your-answers": "basic_care_needs",
    "contact-details": "contact_details",
    "date-of-birth": "date_of_birth",
    "do-you-have-someone-to-go-shopping-for-you": "do_you_have_someone_to_go_shopping_for_you",
    "priority-supermarket-deliveries": "priority_supermarket_deliveries",
    "medical-conditions": "medical_conditions",
    "name": "name",
    "nhs-letter": "nhs_letter",
    "nhs-login": "nhs_login",
    "nhs-number": "nhs_number",
    "postcode-eligibility": "postcode",
    "postcode-lookup": "support_address",
    "support-address": "support_address",
}

# mapping to indicate where the user should be
# directed to when navigating forward from the
# /do-you-live-england page
_LIVES_IN_ENGLAND_REFERRER_TO_NEXT_FORM_URL = {
    "/postcode-eligibility": "/nhs-letter",
    "/postcode-lookup": "/address-lookup",
    "/support-address": "/do-you-have-someone-to-go-shopping-for-you"
}


def blank_form_sections(*sections_to_blank):
    session["form_answers"] = {
        section: {**answers} if isinstance(answers, dict) else answers
        for section, answers in session.get("form_answers", {}).items()
        if section not in sections_to_blank
    }


def get_redirect_to_terminal_page_url():
    if accessing_saved_answers():
        return ("/view-answers")
    return ("/check-your-answers")


def get_redirect_to_terminal_page():
    return redirect(get_redirect_to_terminal_page_url())


def get_redirect_to_terminal_page_if_applicable():
    if accessing_saved_answers() or session.get("check_answers_page_seen"):
        return get_redirect_to_terminal_page()


def redirect_to_next_form_page(redirect_target):
    next_page_name = redirect_target.strip("/")
    next_page_does_not_need_answer = (
        form_answers().get(FORM_PAGE_TO_DATA_CHECK_SECTION_NAME[next_page_name]) is not None
    )

    if accessing_saved_answers():
        persist_answers_from_session()

    maybe_redirect_to_terminal_page = None
    if next_page_does_not_need_answer:
        maybe_redirect_to_terminal_page = get_redirect_to_terminal_page_if_applicable()

    return maybe_redirect_to_terminal_page or redirect(redirect_target)


def clear_errors_after(fn):
    def wrapper(*args, **kwargs):
        result = fn(*args, **kwargs)
        session["error_items"] = {}
        return result

    return wrapper


@clear_errors_after
def get_next_form_url_after_nhs_number():
    if is_nhs_login_user() and validate_name():
        return get_next_form_url_after_name()
    else:
        return "/name"


@clear_errors_after
def get_next_form_url_after_eligibility_check():
    if is_nhs_login_user() and validate_nhs_number():
        return get_next_form_url_after_nhs_number()
    else:
        return "/nhs-number"


@clear_errors_after
def get_next_form_url_after_name():
    if is_nhs_login_user() and validate_date_of_birth():
        return "/do-you-have-someone-to-go-shopping-for-you"

    else:
        return "/date-of-birth"


def return_redirect_if_postcode_valid(_redirect):
    if get_is_postcode_in_england():
        return _redirect
    else:
        return redirect("/do-you-live-in-england")


def get_next_form_url_after_lives_in_england(referrer):
    return _LIVES_IN_ENGLAND_REFERRER_TO_NEXT_FORM_URL.get(referrer, referrer)


def update_lives_in_england_referrer(referrer):
    if referrer in _LIVES_IN_ENGLAND_REFERRER_TO_NEXT_FORM_URL.keys():
        session[SESSION_KEY_LIVES_IN_ENGLAND_REFERRER] = referrer


def _get_next_form_url_based_on_location_tier(redirect_url, should_redirect_to_next_form_page=False):
    location_tier = get_location_tier()
    if is_tier_very_high_or_above(location_tier):
        return redirect_to_next_form_page(redirect_url) if should_redirect_to_next_form_page else redirect(redirect_url)

    return redirect("/not-eligible-postcode")


def _get_next_form_url_after_shopping_and_priority_supermarket():
    if _is_tiering_logic_enabled():
        location_tier = get_location_tier()
        shielding_advice = get_shielding_advice()

        _validate_location_tier_is_at_least_very_high(location_tier)

        if shielding_advice == ShieldingAdvice.ADVISED_TO_SHIELD.value:
            return "/basic-care-needs"
        elif location_tier == PostcodeTier.VERY_HIGH.value:
            return "/contact-details"

    return "/basic-care-needs"


def route_to_next_form_page():
    current_form = request.url_rule.rule.strip("/")
    answer = form_answers().get(current_form.replace("-", "_"))

    if current_form == "address-lookup":
        if _is_tiering_logic_enabled():
            return _get_next_form_url_based_on_location_tier("/nhs-letter", True)
        return return_redirect_if_postcode_valid(redirect("/nhs-letter"))
    elif current_form == "applying-on-own-behalf":
        if ApplyingOnOwnBehalfAnswers(answer) is ApplyingOnOwnBehalfAnswers.YES:
            return redirect_to_next_form_page("/nhs-login")
        return redirect_to_next_form_page("/postcode-eligibility")
    elif current_form == "postcode-eligibility":
        if get_is_postcode_in_england():
            return redirect_to_next_form_page("/address-lookup")
        else:
            return redirect("/not-eligible-postcode")
    elif current_form == "nhs-login":
        if YesNoAnswers(answer) is YesNoAnswers.YES:
            return redirect("/nhs-login-link")
        return redirect_to_next_form_page("/postcode-eligibility")
    elif current_form == "basic-care-needs":
        return redirect_to_next_form_page("/contact-details")
    elif current_form == "check-your-answers":
        contact_details = form_answers().get("contact_details", {})
        if (
            session.get("nhs_sub")
            or not contact_details.get("phone_number_texts")
            or not contact_details.get("email")
            or ApplyingOnOwnBehalfAnswers(form_answers().get("applying_on_own_behalf")) is ApplyingOnOwnBehalfAnswers.NO
        ):
            return redirect("/confirmation")
        else:
            return redirect("/nhs-registration")
    elif current_form == "contact-details":
        return get_redirect_to_terminal_page()
    elif current_form == "date-of-birth":
        return redirect_to_next_form_page("/do-you-have-someone-to-go-shopping-for-you")
    elif current_form == "do-you-have-someone-to-go-shopping-for-you":
        if ShoppingAssistanceAnswers(answer) is ShoppingAssistanceAnswers.YES:
            blank_form_sections("priority_supermarket_deliveries")
            return redirect_to_next_form_page(_get_next_form_url_after_shopping_and_priority_supermarket())
        return redirect_to_next_form_page("/priority-supermarket-deliveries")
    elif current_form == "priority-supermarket-deliveries":
        return redirect_to_next_form_page(_get_next_form_url_after_shopping_and_priority_supermarket())
    elif current_form == "medical-conditions":
        if MedicalConditionsAnswers(answer) is MedicalConditionsAnswers.YES:
            return redirect_to_next_form_page(get_next_form_url_after_eligibility_check())
        return redirect("/not-eligible-medical")
    elif current_form == "name":
        return redirect_to_next_form_page(get_next_form_url_after_name())
    elif current_form == "nhs-letter":
        if NHSLetterAnswers(answer) is NHSLetterAnswers.YES:
            blank_form_sections("medical_conditions")
            return redirect_to_next_form_page(get_next_form_url_after_eligibility_check())
        return redirect_to_next_form_page("/medical-conditions")
    elif current_form == "nhs-number":
        return redirect_to_next_form_page(get_next_form_url_after_nhs_number())
    elif current_form == "postcode-lookup":
        if _is_tiering_logic_enabled():
            return _get_next_form_url_based_on_location_tier("/address-lookup")
        return return_redirect_if_postcode_valid(redirect("/address-lookup"))
    elif current_form == "support-address":
        if _is_tiering_logic_enabled():
            return _get_next_form_url_based_on_location_tier("/nhs-letter", True)
        return return_redirect_if_postcode_valid(
            redirect_to_next_form_page("/nhs-letter")
        )
    elif current_form == "do-you-live-in-england":
        if LiveInEnglandAnswers(answer) is LiveInEnglandAnswers.NO:
            return redirect("/not-eligible-postcode")

        lives_in_england_referrer = session.get(SESSION_KEY_LIVES_IN_ENGLAND_REFERRER)
        next_form_url = get_next_form_url_after_lives_in_england(lives_in_england_referrer)

        if accessing_saved_answers() and lives_in_england_referrer == "/postcode-lookup":
            return redirect(next_form_url)

        return redirect_to_next_form_page(next_form_url)
    else:
        raise RuntimeError("An unexpected error occurred")


def dynamic_back_url(default="/"):
    return request.args.get("next") or request.referrer or default


def get_back_url_for_shopping_assistance():
    back_url = "/date-of-birth" if session.get(SESSION_KEY_ADDRESS_SELECTED) else "/support-address"
    return append_querystring_params(back_url)


def get_back_url_for_contact_details():
    back_url = "/basic-care-needs"

    if _is_tiering_logic_enabled():
        location_tier = get_location_tier()
        shielding_advise = get_shielding_advice()

        _validate_location_tier_is_at_least_very_high(location_tier)

        if location_tier >= PostcodeTier.VERY_HIGH.value and shielding_advise == ShieldingAdvice.NOT_ADVISED_TO_SHIELD:
            if form_answers().get("do_you_have_someone_to_go_shopping_for_you") == ShoppingAssistanceAnswers.NO.value:
                back_url = "/priority-supermarket-deliveries"
            else:
                back_url = "/do-you-have-someone-to-go-shopping-for-you"
        elif location_tier >= PostcodeTier.VERY_HIGH.value and shielding_advise == ShieldingAdvice.ADVISED_TO_SHIELD :
            back_url = "/basic-care-needs"

    return append_querystring_params(back_url)


def get_redirect_for_returning_user_based_on_tier():
    original_postcode = form_answers()["support_address"]["postcode"]
    original_uprn = form_answers()["support_address"].get("address_uprn", None)
    original_location_tier = get_location_tier()
    original_shielding_advice = get_shielding_advice()

    latest_location_tier = None
    latest_shielding_advice = None
    if original_uprn:
        latest_location_tier = location_eligibility.get_uprn_tier(original_uprn)
        latest_shielding_advice = location_eligibility.get_shielding_advice_by_uprn(original_uprn, current_app)
    else:
        latest_location_tier = location_eligibility.get_postcode_tier(original_postcode)
        latest_shielding_advice = location_eligibility.get_shielding_advice_by_postcode(original_postcode, current_app)

    latest_location_tier_info = get_latest_location_tier(latest_location_tier, original_location_tier)
    latest_shielding_advice_info = get_latest_shielding_advice(latest_shielding_advice, original_shielding_advice)

    if latest_location_tier_info is None:
        return redirect("/not-eligible-postcode-returning-user-tier-not-found")

    latest_location_tier = PostcodeTier(latest_location_tier_info["latest_location_tier"])
    latest_shielding_advice = ShieldingAdvice(latest_shielding_advice_info["latest_shielding_advice"])
    set_location_tier(latest_location_tier)
    set_shielding_advice(latest_shielding_advice)

    location_tier_change_status = PostcodeTierStatus(latest_location_tier_info["change_status"])
    shielding_advice_change_status = ShieldingAdviceStatus(latest_shielding_advice_info["change_status"])

    if location_tier_change_status == PostcodeTierStatus.NO_CHANGE \
       and shielding_advice_change_status == ShieldingAdviceStatus.NO_CHANGE :
        return get_redirect_to_terminal_page()
    elif shielding_advice_change_status == ShieldingAdviceStatus.INCREASED:
        if latest_shielding_advice == ShieldingAdvice.ADVISED_TO_SHIELD:
            return redirect("/basic-care-needs?ca=1")
        _raise_returning_user_redirect_error(location_tier_change_status,
                                             original_location_tier,
                                             latest_location_tier,
                                             shielding_advice_change_status,
                                             original_shielding_advice,
                                             latest_shielding_advice)
    elif location_tier_change_status == PostcodeTierStatus.DECREASED:
        if latest_location_tier == PostcodeTier.VERY_HIGH:
            return get_redirect_to_terminal_page()
        elif not is_tier_very_high_or_above(latest_location_tier):
            return redirect("/not-eligible-postcode-returning-user")
        _raise_returning_user_redirect_error(location_tier_change_status,
                                             original_location_tier,
                                             latest_location_tier,
                                             shielding_advice_change_status,
                                             original_shielding_advice,
                                             latest_shielding_advice)

    _raise_returning_user_redirect_error(location_tier_change_status, original_location_tier, latest_location_tier)


def _raise_returning_user_redirect_error(location_tier_change_status,
                                         original_location_tier,
                                         latest_location_tier,
                                         shielding_advice_change_status,
                                         original_shielding_advice,
                                         latest_shielding_advice):
    raise RuntimeError("Unable to determine redirect location for nhs login returning user, "
                       + f"tier change status: {location_tier_change_status}, "
                       + f"original postcode tier: {original_location_tier}, "
                       + f"latest postcode tier: {latest_location_tier.value},"
                       + f"shielding advice change status: {shielding_advice_change_status}, "
                       + f"original shielding advice: {original_shielding_advice}, "
                       + f"latest shielding advice: {latest_shielding_advice.value}"
                       )


def _is_tiering_logic_enabled():
    return current_app.is_tiering_logic_enabled


def _validate_location_tier_is_at_least_very_high(location_tier):
    if not is_tier_very_high_or_above(location_tier):
        raise ValueError(f"Unexpected location tier value encountered: {location_tier}")
