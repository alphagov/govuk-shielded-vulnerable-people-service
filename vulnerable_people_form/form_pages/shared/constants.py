import enum
from functools import partial


def get_partial_date_from_userinfo(partial_date_key, nhs_user_info):
    return get_answers_formatted_date_from_userinfo(nhs_user_info).get(partial_date_key)


def get_answers_formatted_date_from_userinfo(nhs_user_info):
    if "birthdate" in nhs_user_info and len(nhs_user_info["birthdate"]) > 0:
        year, month, day = nhs_user_info["birthdate"].split("-")

        return {
            "year": year,
            "month": month,
            "day": day,
        }
    return {}


PAGE_TITLES = {
    "privacy": "Privacy",
    "accessibility": "Accessibility statement",
    "applying-on-own-behalf": "Are you using this service for yourself or for someone else?",
    "cookies": "Cookies",
    "address-lookup": "What is the address where you need support?",
    "basic-care-needs": "Do you need someone to contact you about local support that might be available?",
    "check-contact-details": "Check this is correct",
    "check-your-answers": "Check your answers before submitting",
    "contact-details": "What are your contact details?",
    "date-of-birth": "What is your date of birth?",
    "do-you-have-someone-to-go-shopping-for-you": "Is there someone you can rely on to go shopping for you if you need them to?",  # noqa: E501
    "do-you-live-in-england": "Do you live in England?",  # noqa: E501
    "priority-supermarket-deliveries": "Do you want access to priority supermarket deliveries?",
    "medical-conditions": "Do you have one of the listed medical conditions?",
    "name": "What is your name?	",
    "nhs-letter": "Has the NHS or your doctor told you that you’re classed as clinically extremely vulnerable to coronavirus?",  # noqa: E501
    "nhs-login": "Do you have an NHS login?",
    "nhs-login-link": "If you've previously registered with NHS login for this service you can sign in",
    "nhs-number": "What is your NHS number?",
    "nhs-registration": "Would you like to create an NHS Login you can use to retrieve your answers in the future?",
    "nhs-registration-link": "Set up an NHS login account to confirm who you are",
    "not-eligible-postcode": "Sorry, this service is only available in England",
    "not-eligible-postcode-tier": "Sorry, this service is not available in your area",
    "not-eligible-postcode-not-found": "Sorry, we could not find your postcode in our system",
    "not-eligible-medical": "Sorry, you’re not eligible for help through this service",
    "postcode-lookup": "What is the postcode where you need support?",
    "postcode-eligibility": "What is the postcode where you need support?",
    "confirmation": "Registration complete",
    "support-address": "What is the address where you need support?",
    "view-or-setup": "Do you want to set up this service, or access an existing account?",
    "view-answers": "Your saved details",
    "nhs-login-landing": "Sign in to update your details or change the support you need",
    "nhs-login-no-consent": "You have decided not to share your NHS login information",
}

NHS_USER_INFO_TO_FORM_ANSWERS = {
    ("name", "first_name"): "given_name",
    ("name", "last_name"): "family_name",
    ("contact_details", "phone_number_calls"): "phone_number",
    ("contact_details", "email"): "email",
    ("nhs_number",): "nhs_number",
    ("date_of_birth", "day"): partial(get_partial_date_from_userinfo, "day"),
    ("date_of_birth", "month"): partial(get_partial_date_from_userinfo, "month"),
    ("date_of_birth", "year"): partial(get_partial_date_from_userinfo, "year"),
}

SESSION_KEY_ADDRESS_SELECTED = "auto_populated_address_selected"
SESSION_KEY_QUERYSTRING_PARAMS = "querystring_params_to_retain"
SESSION_KEY_LIVES_IN_ENGLAND_REFERRER = "lives_in_england_referrer"
SESSION_KEY_POSTCODE_TIER = "postcode_tier"

GOVUK_JOURNEY_START_PAGE_URL = "https://gov.uk/coronavirus-shielding-support"


@enum.unique
class JourneyProgress(enum.Enum):
    NHS_NUMBER = 0
    NHS_REGISTRATION = 1


@enum.unique
class PostcodeTier(enum.Enum):
    MEDIUM = 1
    HIGH = 2
    VERY_HIGH = 3
    VERY_HIGH_PLUS_SHIELDING = 4
