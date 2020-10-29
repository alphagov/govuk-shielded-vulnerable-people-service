from http import HTTPStatus
from unittest.mock import patch

from flask import Flask

from vulnerable_people_form.form_pages.shared.constants import SESSION_KEY_ADDRESS_SELECTED
from vulnerable_people_form.form_pages.support_address import post_support_address

_current_app = Flask(__name__)
_current_app.secret_key = "test_secret"


def test_post_support_address_should_redirect_to_support_address_when_form_invalid():
    user_entered_postcode = "LS1 1ba"
    with patch("vulnerable_people_form.form_pages.support_address.form_answers", return_value={}),\
            patch("vulnerable_people_form.form_pages.support_address.format_postcode", return_value="LS11BA") \
            as mock_format_postcode,\
            patch("vulnerable_people_form.form_pages.support_address.request_form",
                  return_value={
                      "building_and_street_line_1": "",
                      "building_and_street_line_2": "",
                      "town_city": "Leeds",
                      "postcode": user_entered_postcode}),\
            _current_app.test_request_context("/support-address"):
        response = post_support_address()
        mock_format_postcode.assert_called_once_with(user_entered_postcode)
        assert response.status_code == HTTPStatus.FOUND
        assert response.headers["Location"] == "/support-address"


def test_post_support_address_should_redirect_to_next_form_page_when_form_valid():
    with patch("vulnerable_people_form.form_pages.support_address.form_answers", return_value={}), \
         patch("vulnerable_people_form.form_pages.support_address.route_to_next_form_page") \
            as mock_route_to_next_form_page, \
            patch("vulnerable_people_form.form_pages.support_address.request_form",
                  return_value={
                      "building_and_street_line_1": "12 Test Street",
                      "building_and_street_line_2": "",
                      "town_city": "Leeds",
                      "postcode": "LS1 1BA"}), \
            _current_app.test_request_context("/support-address") as request_context:
        post_support_address()

        assert request_context.session["postcode"] == "LS11BA"
        assert request_context.session["error_items"] == {}
        assert request_context.session["form_answers"]["support_address"]["postcode"] == "LS11BA"
        assert request_context.session[SESSION_KEY_ADDRESS_SELECTED] is False
        mock_route_to_next_form_page.assert_called_once()
