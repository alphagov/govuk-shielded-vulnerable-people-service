from flask import current_app
from notifications_python_client.notifications import NotificationsAPIClient

from vulnerable_people_form.form_pages.shared.session import form_answers
from vulnerable_people_form.integrations.notification_content import create_spl_no_match_email_content, \
    create_spl_match_email_content, create_spl_match_sms_content, create_spl_no_match_sms_content, \
    create_spl_match_letter_content, create_spl_no_match_letter_content
from ..integrations import govuk_notify_client

_COMMS_HEADING_SUBJECT = "Coronavirus shielding support: your registration"


def get_notifications_client():
    return NotificationsAPIClient(current_app.config["NOTIFY_API_KEY"])


def send_sms(phone_number, template_id, message):
    return get_notifications_client().send_sms_notification(
        phone_number=phone_number,
        template_id=template_id,
        personalisation={"message": message},
    )


def send_email(email_address, template_id, email_subject, email_content):
    return get_notifications_client().send_email_notification(
        email_address=email_address,
        template_id=template_id,
        personalisation={"body": email_content, "subject": email_subject}
    )


def send_letter(postal_address, template_id, letter_heading, letter_content):
    return get_notifications_client().send_letter_notification(template_id, {
        "address_line_1": postal_address["address_line_1"],
        "address_line_2": postal_address["address_line_2"],
        "address_line_3": postal_address["town_city"],
        "postcode": postal_address["postcode"],
        "heading": letter_heading,
        "body": letter_content
    })


def send_notification(reference_number, is_spl_match, app=current_app):
    email_address = form_answers()["contact_details"].get("email")
    mobile_number = form_answers()["contact_details"].get("phone_number_texts")

    if email_address:
        if is_spl_match:
            email_content = create_spl_match_email_content(reference_number)
            email_template_id = app.config.get('GOVUK_NOTIFY_SPL_MATCH_EMAIL_TEMPLATE_ID')
        else:
            email_content = create_spl_no_match_email_content(reference_number)
            email_template_id = app.config.get('GOVUK_NOTIFY_NO_SPL_MATCH_EMAIL_TEMPLATE_ID')

        govuk_notify_client.send_email(email_address, email_template_id, _COMMS_HEADING_SUBJECT, email_content)
    elif mobile_number:
        if is_spl_match:
            sms_content = create_spl_match_sms_content(reference_number)
            sms_email_template_id = app.config.get("GOVUK_NOTIFY_SPL_MATCH_SMS_TEMPLATE_ID")
        else:
            sms_content = create_spl_no_match_sms_content(reference_number)
            sms_email_template_id = app.config.get("GOVUK_NOTIFY_NO_SPL_MATCH_SMS_TEMPLATE_ID")

        govuk_notify_client.send_sms(mobile_number, sms_email_template_id, sms_content)
    else:
        if is_spl_match:
            letter_content = create_spl_match_letter_content(reference_number)
            letter_template_id = app.config.get("GOVUK_NOTIFY_SPL_MATCH_LETTER_TEMPLATE_ID")
        else:
            letter_content = create_spl_no_match_letter_content(reference_number)
            letter_template_id = app.config.get("GOVUK_NOTIFY_NO_SPL_MATCH_LETTER_TEMPLATE_ID")

        address_line_1 = form_answers()["support_address"].get("building_and_street_line_1")
        address_line_2 = form_answers()["support_address"].get("building_and_street_line_2")
        address_line_2 = address_line_2 if address_line_2 else " "
        town_city = form_answers()["support_address"].get("town_city")
        town_city = town_city if town_city else " "

        govuk_notify_client.send_letter({"address_line_1": address_line_1,
                                         "address_line_2": address_line_2,
                                         "town_city": town_city,
                                         "postcode": form_answers()["support_address"]["postcode"]},
                                        letter_template_id,
                                        _COMMS_HEADING_SUBJECT,
                                        letter_content)
