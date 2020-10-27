from unittest.mock import patch, MagicMock

import pytest
from flask import Flask

from vulnerable_people_form.integrations.govuk_notify_client import send_notification

_current_app = Flask(__name__)
_current_app.secret_key = 'test_secret'

_current_app.config["GOVUK_NOTIFY_SPL_MATCH_EMAIL_TEMPLATE_ID"] = "match_email_template_id"
_current_app.config["GOVUK_NOTIFY_NO_SPL_MATCH_EMAIL_TEMPLATE_ID"] = "no_match_email_template_id"

_current_app.config["GOVUK_NOTIFY_SPL_MATCH_SMS_TEMPLATE_ID"] = "match_sms_template_id"
_current_app.config["GOVUK_NOTIFY_NO_SPL_MATCH_SMS_TEMPLATE_ID"] = "no_match_sms_template_id"

_current_app.config["GOVUK_NOTIFY_SPL_MATCH_LETTER_TEMPLATE_ID"] = "match_letter_template_id"
_current_app.config["GOVUK_NOTIFY_NO_SPL_MATCH_LETTER_TEMPLATE_ID"] = "no_match_letter_template_id"

_COMMS_HEADING_SUBJECT = "Coronavirus shielding support: your registration"
_NOTIFY_CLIENT_FULL_NAME = "vulnerable_people_form.integrations.govuk_notify_client"
_TEST_REF_NUM = "test_ref_num"
_MATCH_CONTENT = "match"
_NO_MATCH_CONTENT = "no match"


@pytest.fixture
def mock_notifications_api_client():
    from notifications_python_client import NotificationsAPIClient
    return MagicMock(spec=NotificationsAPIClient)


@pytest.mark.parametrize("is_spl_match, expected_template_id", [
    (True, _current_app.config["GOVUK_NOTIFY_SPL_MATCH_EMAIL_TEMPLATE_ID"]),
    (False, _current_app.config["GOVUK_NOTIFY_NO_SPL_MATCH_EMAIL_TEMPLATE_ID"])
])
def test_send_notification_should_send_email_when_email_address_present(
        is_spl_match, expected_template_id, mock_notifications_api_client):
    test_email_address = "testemail@gmail.com"

    with patch(f"{_NOTIFY_CLIENT_FULL_NAME}._get_notifications_client", return_value=mock_notifications_api_client), \
            patch(f"{_NOTIFY_CLIENT_FULL_NAME}.create_spl_no_match_email_content",
                  return_value=_NO_MATCH_CONTENT) as create_spl_no_match_email_content, \
            patch(f"{_NOTIFY_CLIENT_FULL_NAME}.create_spl_match_email_content",
                  return_value=_MATCH_CONTENT) as create_spl_match_email_content, \
            _current_app.test_request_context() as test_request_ctx:

        test_request_ctx.session["form_answers"] = {"contact_details": {"email": test_email_address}}
        send_notification(_TEST_REF_NUM, is_spl_match, _current_app)

        if is_spl_match:
            create_spl_match_email_content.assert_called_once_with(_TEST_REF_NUM)
            create_spl_no_match_email_content.assert_not_called()
            email_content = _MATCH_CONTENT
        else:
            create_spl_match_email_content.assert_not_called()
            create_spl_no_match_email_content.assert_called_with(_TEST_REF_NUM)
            email_content = _NO_MATCH_CONTENT

        mock_notifications_api_client.send_email_notification.assert_called_once_with(
            email_address=test_email_address,
            template_id=expected_template_id,
            personalisation={"body": email_content, "subject": _COMMS_HEADING_SUBJECT})


@pytest.mark.parametrize("is_spl_match, expected_template_id", [
    (True, _current_app.config["GOVUK_NOTIFY_SPL_MATCH_SMS_TEMPLATE_ID"]),
    (False, _current_app.config["GOVUK_NOTIFY_NO_SPL_MATCH_SMS_TEMPLATE_ID"])
])
def test_send_notification_should_send_sms_when_phone_num_for_texts_present(
        is_spl_match, expected_template_id, mock_notifications_api_client):
    test_mobile_number = "07412123456"

    with patch(f"{_NOTIFY_CLIENT_FULL_NAME}._get_notifications_client", return_value=mock_notifications_api_client), \
            patch(f"{_NOTIFY_CLIENT_FULL_NAME}.create_spl_no_match_sms_content",
                  return_value=_NO_MATCH_CONTENT) as create_spl_no_match_sms_content, \
            patch(f"{_NOTIFY_CLIENT_FULL_NAME}.create_spl_match_sms_content",
                  return_value=_MATCH_CONTENT) as create_spl_match_sms_content, \
            _current_app.test_request_context() as test_request_ctx:

        test_request_ctx.session["form_answers"] = {"contact_details": {"phone_number_texts": test_mobile_number}}
        send_notification(_TEST_REF_NUM, is_spl_match, _current_app)

        if is_spl_match:
            create_spl_match_sms_content.assert_called_once_with(_TEST_REF_NUM)
            create_spl_no_match_sms_content.assert_not_called()
            sms_content = _MATCH_CONTENT
        else:
            create_spl_match_sms_content.assert_not_called()
            create_spl_no_match_sms_content.assert_called_with(_TEST_REF_NUM)
            sms_content = _NO_MATCH_CONTENT

        mock_notifications_api_client.send_sms_notification.assert_called_once_with(
            phone_number=test_mobile_number,
            template_id=expected_template_id,
            personalisation={"message": sms_content})


@pytest.mark.parametrize("is_spl_match, expected_template_id, address_line_two, address_town_city, expected_address_line_two, expected_address_line_three",  # noqa
                         [
                            (True,
                             _current_app.config["GOVUK_NOTIFY_SPL_MATCH_LETTER_TEMPLATE_ID"],
                             "address line 2",
                             "Leeds",
                             "address line 2",
                             "Leeds"),
                            (False,
                             _current_app.config["GOVUK_NOTIFY_NO_SPL_MATCH_LETTER_TEMPLATE_ID"],
                             "address line 2",
                             "Leeds",
                             "address line 2",
                             "Leeds"),
                            (True,
                             _current_app.config["GOVUK_NOTIFY_SPL_MATCH_LETTER_TEMPLATE_ID"],
                             "1 test avenue",
                             "",
                             "1 test avenue",
                             " "),
                            (False,
                             _current_app.config["GOVUK_NOTIFY_NO_SPL_MATCH_LETTER_TEMPLATE_ID"],
                             "",
                             "Leeds",
                             " ",
                             "Leeds")
                         ])
def test_send_notification_should_send_letter_when_no_email_or_phone_number_present(is_spl_match,
                                                                                    expected_template_id,
                                                                                    address_line_two,
                                                                                    address_town_city,
                                                                                    expected_address_line_two,
                                                                                    expected_address_line_three,
                                                                                    mock_notifications_api_client):
    address_line_one = "1 Test Street"
    address_postcode = "LS1 1AB"

    with patch(f"{_NOTIFY_CLIENT_FULL_NAME}._get_notifications_client", return_value=mock_notifications_api_client), \
            patch(f"{_NOTIFY_CLIENT_FULL_NAME}.create_spl_no_match_letter_content",
                  return_value=_NO_MATCH_CONTENT) as create_spl_no_match_letter_content, \
            patch(f"{_NOTIFY_CLIENT_FULL_NAME}.create_spl_match_letter_content",
                  return_value=_MATCH_CONTENT) as create_spl_match_letter_content, \
            _current_app.test_request_context() as test_request_ctx:

        test_request_ctx.session["form_answers"] = {
            "contact_details": {},
            "support_address": {
                "building_and_street_line_1": address_line_one,
                "building_and_street_line_2": address_line_two,
                "town_city": address_town_city,
                "postcode": address_postcode
            }
        }

        send_notification(_TEST_REF_NUM, is_spl_match, _current_app)

        if is_spl_match:
            create_spl_match_letter_content.assert_called_once_with(_TEST_REF_NUM)
            create_spl_no_match_letter_content.assert_not_called()
            letter_content = _MATCH_CONTENT
        else:
            create_spl_match_letter_content.assert_not_called()
            create_spl_no_match_letter_content.assert_called_with(_TEST_REF_NUM)
            letter_content = _NO_MATCH_CONTENT

        mock_notifications_api_client.send_letter_notification.assert_called_once_with(
            expected_template_id,
            {
                "address_line_1": address_line_one,
                "address_line_2": expected_address_line_two,
                "address_line_3": expected_address_line_three,
                "postcode": address_postcode,
                "heading": _COMMS_HEADING_SUBJECT,
                "body": letter_content
             })
