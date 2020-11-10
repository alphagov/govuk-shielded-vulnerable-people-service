from flask import redirect, request, session

from ...integrations import postcode_eligibility
from .answers_enums import (
    ApplyingOnOwnBehalfAnswers,
    MedicalConditionsAnswers,
    NHSLetterAnswers,
    LiveInEnglandAnswers,
    YesNoAnswers,
)
from .constants import SESSION_KEY_ADDRESS_SELECTED, SESSION_KEY_LIVES_IN_ENGLAND_REFERRER
from .querystring_utils import append_querystring_params
from .session import (
    accessing_saved_answers,
    form_answers,
    get_answer_from_form,
    is_nhs_login_user,
    persist_answers_from_session,
)
from .validation import (
    validate_date_of_birth,
    validate_nhs_number,
    validate_name,
)

FORM_PAGE_TO_DATA_CHECK_SECTION_NAME = {
    "address-lookup": "support_address",
    "applying-on-own-behalf": "applying_on_own_behalf",
    "basic-care-needs": "basic_care_needs",
    "check-contact-details": "check_contact_details",
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


def get_redirect_to_terminal_page():
    if accessing_saved_answers():
        return redirect("/view-answers")
    return redirect("/check-your-answers")


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
        return "/address-lookup"
    else:
        return "/date-of-birth"


@clear_errors_after
def get_next_form_url_after_check_contact_details():
    if is_nhs_login_user():
        return "/address-lookup"
    else:
        return "/nhs-number"


def return_redirect_if_postcode_valid(_redirect):
    if postcode_eligibility.check_postcode(session["postcode"]):
        return _redirect
    else:
        return redirect("/do-you-live-in-england")


def get_next_form_url_after_lives_in_england(referrer):
    return _LIVES_IN_ENGLAND_REFERRER_TO_NEXT_FORM_URL.get(referrer, referrer)


def update_lives_in_england_referrer(referrer):
    if referrer in _LIVES_IN_ENGLAND_REFERRER_TO_NEXT_FORM_URL.keys():
        session[SESSION_KEY_LIVES_IN_ENGLAND_REFERRER] = referrer


def route_to_next_form_page():
    current_form = request.url_rule.rule.strip("/")
    answer = form_answers().get(current_form.replace("-", "_"))

    if current_form == "address-lookup":
        return redirect_to_next_form_page("/do-you-have-someone-to-go-shopping-for-you")
    elif current_form == "applying-on-own-behalf":
        if ApplyingOnOwnBehalfAnswers(answer) is ApplyingOnOwnBehalfAnswers.YES:
            return redirect_to_next_form_page("/nhs-login")
        return redirect_to_next_form_page("/postcode-eligibility")
    elif current_form == "postcode-eligibility":
        return return_redirect_if_postcode_valid(redirect("/nhs-letter"))
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
    elif current_form == "check-contact-details":
        return get_redirect_to_terminal_page()
    elif current_form == "contact-details":
        if get_answer_from_form(("contact_details", "email")):
            return redirect_to_next_form_page("/check-contact-details")
        return get_redirect_to_terminal_page()
    elif current_form == "date-of-birth":
        return redirect_to_next_form_page("/address-lookup")
    elif current_form == "do-you-have-someone-to-go-shopping-for-you":
        if YesNoAnswers(answer) is YesNoAnswers.YES:
            blank_form_sections("priority_supermarket_deliveries")
            return redirect_to_next_form_page("/basic-care-needs")
        return redirect_to_next_form_page("/priority-supermarket-deliveries")
    elif current_form == "priority-supermarket-deliveries":
        return redirect_to_next_form_page("/basic-care-needs")
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
        return return_redirect_if_postcode_valid(redirect("/address-lookup"))
    elif current_form == "support-address":
        return return_redirect_if_postcode_valid(
            redirect_to_next_form_page("/do-you-have-someone-to-go-shopping-for-you")
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
    back_url = "/address-lookup" if session.get(SESSION_KEY_ADDRESS_SELECTED) else "/support-address"
    return append_querystring_params(back_url)
