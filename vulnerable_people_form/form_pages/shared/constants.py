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
    "address-lookup": "Select your address",
    "basic-care-needs": "Do you need help meeting your basic care needs?",
    "check-contact-details": "Check this is correct",
    "check-your-answers": "Check your answers before submitting",
    "contact-details": "What are your contact details?",
    "date-of-birth": "What is your date of birth?",
    "do-you-have-someone-to-go-shopping-for-you": "While you're shielding is there someone you can rely on to go shopping for you?",
    "priority-supermarket-deliveries": "Do you want access to priority supermarket deliveries?",
    "medical-conditions": "Do you have one of the listed medical conditions?",
    "name": "What is your name?	",
    "nhs-letter": "Are you 'shielding' because you’ve been told you're clinically extremely vulnerable to coronavirus?",
    "nhs-login": "Do you have an NHS login?",
    "nhs-number": "Do you know your NHS number?",
    "nhs-registration": "Would you like to create an NHS Login you can use to retrieve your answers in the future?",
    "not-eligible-postcode": "Sorry, this service is not available in your area",
    "not-eligible-medical": "Sorry, you’re not eligible for help through this service",
    "postcode-lookup": "What is the postcode where you need support?",
    "postcode-eligibility": "What is the postcode where you need support?",
    "confirmation": "Registration complete",
    "support-address": "What is the address where you need support?",
    "view-or-setup": "Do you want to set up this service, or access an existing account?",
    "view-answers": "Your saved details",
}

NHS_USER_INFO_TO_FORM_ANSWERS = {
    ("name", "first_name"): "given_name",
    ("name", "last_name"): "family_name",
    ("contact_details", "phone_number_calls"): "phone_number",
    ("contact_details", "phone_number_texts"): "phone_number",
    ("contact_details", "email"): "email",
    ("nhs_number",): "nhs_number",
    ("date_of_birth", "day"): partial(get_partial_date_from_userinfo, "day"),
    ("date_of_birth", "month"): partial(get_partial_date_from_userinfo, "month"),
    ("date_of_birth", "year"): partial(get_partial_date_from_userinfo, "year"),
}
