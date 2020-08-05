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
    "applying-on-own-behalf": "Are you applying on your own behalf?",
    "cookies": "Cookies",
    "address-lookup": "Select your address",
    "basic-care-needs": "Are your basic care needs being met at the moment?",
    "carry-supplies": "Is there someone in the house who’s able to carry a delivery of supplies inside?	",
    "check-contact-details": "Check this is correct",
    "check-your-answers": "Are you ready to send your application?",
    "contact-details": "What are your contact details?",
    "date-of-birth": "What is your date of birth?",
    "dietary-requirements": "Do you have any special dietary requirements?",
    "essential-supplies": "Do you have a way of getting essential supplies delivered at the moment?",
    "live-in-england": "Do you live in England?",
    "medical-conditions": "Do you have one of the listed medical conditions?",
    "name": "What is your name?	",
    "nhs-letter": "Have you had a letter from the NHS or been told by your doctor to ’shield’ because you’re clinically extremely vulnerable to coronavirus?",
    "nhs-login": "Would you like to use an existing NHS login to access this service?",
    "nhs-number": "Do you know your NHS number?",
    "nhs-registration": "Would you like to register an NHS Login to use with an account on this service?",
    "not-eligible-england": "Sorry, this service is only available in England",
    "not-eligible-medical": "Sorry, you’re not eligible for help through this service",
    "postcode-lookup": "What is the postcode where you need support?",
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
