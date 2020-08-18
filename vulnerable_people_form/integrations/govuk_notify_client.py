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


EMAIL_SUBJECT = "Coronavirus support service: your registration"

GREETER = "Dear {first_name} {last_name}"

EMAIL_CONTACT_GP_GREETER = "Contact your GP or hospital clinician as soon as possible so they can confirm to us you’re classed as clinically extremely vulnerable. You may not get the support you need if you do not contact them."
EMAIL_NO_CONTACT_GP_GREETER = "Your registration number is %{reference_number}."

EMAIL_BODY_PARAGRAPHS = [
    # What happens next
    "We’ll check your details to make sure you’re eligible for support. You’ll only get support if you asked for it.",
    "If we need to confirm any details, you’ll get a call from the National Shielding Service. The number that will show on your phone is 0333 3050466.",
    # Getting support
    "If you’re eligible and you said that you do not have a way of getting basic supplies at the moment we will start sending you a weekly box of basic supplies.",
    "If you do not already have an account with a supermarket delivery service, set one up now. If you’re concerned about not being able to get a delivery slot, you can set up accounts with more than one supermarket.",
    "This can take up to a week. Contact your local authority if you need supplies urgently and cannot rely on family, friends or neighbours: https://www.gov.uk/coronavirus-local-help",
    # If your support needs change
    "You can tell the delivery driver if you want to stop getting the weekly box of supplies.",
    "If your support needs change, go through the questions in the service again: https://www.gov.uk/coronavirus-extremely-vulnerable.",
    "There’s guidance on things you should do if you’re extremely vulnerable to coronavirus: https://www.gov.uk/coronavirus-extremely-vulnerable-guidance.",
    "Thanks,",
    "Coronavirus support team",
    "-----",
    "Do not reply to this email - it’s an automatic message from an unmonitored account.",
]


NO_GP_CONTACT_EMAIL_MESSAGE = "\n\n".join(
    (GREETER, EMAIL_NO_CONTACT_GP_GREETER, *EMAIL_BODY_PARAGRAPHS)
)
GP_CONTACT_EMAIL_MESSAGE = "\n\n".join(
    (GREETER, EMAIL_CONTACT_GP_GREETER, *EMAIL_BODY_PARAGRAPHS)
)


def send_confirmation_email(
    email_address, first_name, last_name, reference_number, need_to_contact_gp
):
    message = (
        GP_CONTACT_SMS_MESSAGE if need_to_contact_gp else NO_GP_CONTACT_SMS_MESSAGE
    ).format(
        first_name=first_name, last_name=last_name, reference_number=reference_number
    )
    get_notifications_client().send_email_notification(
        email_address=email_address,
        template_id=current_app.config["GOVUK_NOTIFY_EMAIL_TEMPLATE_ID"],
        personalisation={"message": message},
    )


def _try_and_report_exception_to_sentry(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except Exception as e:
        print('method _try_and_report_exception_to_sentry exception thrown:' +e)


def try_send_confirmation_email(*args, **kwargs):
    _try_and_report_exception_to_sentry(send_confirmation_email, *args, **kwargs)


def try_send_confirmation_sms(*args, **kwargs):
    _try_and_report_exception_to_sentry(send_confirmation_sms, *args, **kwargs)
