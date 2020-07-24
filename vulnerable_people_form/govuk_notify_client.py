from flask import current_app
from notifications_python_client.notifications import NotificationsAPIClient


def get_notifications_client():
    return NotificationsAPIClient(current_app.config["NOTIFY_API_KEY"])


SMS_GREETING_PARAGRAPHS = [
    "Hello {first_name} {last_name} - we’ve received your registration as someone who’s extremely vulnerable to coronavirus.",
]

SMS_CLOSING_PARAGRAPHS = [
    "This can take up to a week. Contact your local authority if you need urgent support and cannot rely on friends or neighbours: https://www.gov.uk/coronavirus-local-help",
    "If you want priority supermarket deliveries and do not already have an account with a supermarket, set one up now. You can set up accounts with more than one supermarket.",
    "If your support needs change, go to https://www.gov.uk/coronavirus-extremely-vulnerable and answer the questions again.",
]

SMS_CONTACT_GP_PARAGRAPHS = [
    "Contact your doctor as soon as possible so they can confirm to us you’re classed as clinically extremely vulnerable. You may not get the support you need if you do not contact them.",
    "After that we’ll check that you’re eligible, and you’ll start getting support if you asked for it.",
]

SMS_NO_CONTACT_GP_PARAGRAPHS = [
    "Contact your doctor as soon as possible so they can confirm to us you’re classed as clinically extremely vulnerable. You may not get the support you need if you do not contact them.",
    "After that we’ll check that you’re eligible, and you’ll start getting support if you asked for it.",
]

NO_GP_CONTACT_SMS_MESSAGE = "\n\n".join(
    SMS_GREETING_PARAGRAPHS + SMS_NO_CONTACT_GP_PARAGRAPHS + SMS_CLOSING_PARAGRAPHS
)
GP_CONTACT_SMS_MESSAGE = "\n\n".join(
    SMS_GREETING_PARAGRAPHS + SMS_CONTACT_GP_PARAGRAPHS + SMS_CLOSING_PARAGRAPHS
)


def send_confirmation_sms(phone_number, first_name, last_name, need_to_contact_gp):
    message = (
        GP_CONTACT_SMS_MESSAGE if need_to_contact_gp else NO_GP_CONTACT_SMS_MESSAGE
    ).format(first_name=first_name, last_name=last_name)
    get_notifications_client().send_sms_notification(
        phone_number=phone_number,
        template_id=current_app.config["GOVUK_NOTIFY_SMS_TEMPLATE_ID"],
        personalisation={"message": message},
    )


