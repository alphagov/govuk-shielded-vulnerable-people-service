
import json
from flask import Flask
from unittest.mock import patch

from vulnerable_people_form.integrations.notifications import send_message
from vulnerable_people_form.form_pages.shared.session import form_answers

_current_app = Flask(__name__)
_current_app.secret_key = "test_secret"
_current_app.is_tiering_logic_enabled = False

_current_app.config["AWS_SQS_QUEUE_URL"] = "test_url"


def test_send_message():
    with _current_app.test_request_context() as test_request_ctx, \
         patch("vulnerable_people_form.integrations.notifications.boto3") as boto3:
        test_request_ctx.session["form_answers"] = {
            "nhs_number": "1234567890",
            "nhs_sub": "test",
            "date_of_birth": {
                "day": "01",
                "month": "03",
                "year": "1994"
            },
            "name": {
                "first_name": "FirstName",
                "last_name": "LastName",
            },
            "contact_details": {
                "email": "email@test.com",
                "phone_number_texts": "07912345678"
            },
            "support_address": {
                "building_and_street_line_1": "101 Test Block",
                "building_and_street_line_2": "Test Lane",
                "town_city": "London",
                "postcode": "SW1A 9AJ"
            },
            "do_you_have_someone_to_go_shopping_for_you": 0,
            "priority_supermarket_deliveries": 1,
            "basic_care_needs": 1,
            "nhs_letter": 1
        }
        submission_id = "test-registration-number"

        send_message(submission_id)
        message = json.loads(boto3.mock_calls[1][2]["MessageBody"])

        date_of_birth = form_answers()["date_of_birth"]
        assert message["submission_id"] == submission_id
        assert message["nhs_number"] == form_answers()["nhs_number"]
        assert message["date_of_birth"] == f"{date_of_birth['year']}/{date_of_birth['month']}/{date_of_birth['day']}"
        assert message["first_name"] == form_answers()["name"]["first_name"]
        assert message["last_name"] == form_answers()["name"]["last_name"]
        assert message["email"] == form_answers()["contact_details"]["email"]
        assert message["phone_number_texts"] == form_answers()["contact_details"]["phone_number_texts"]
        assert message["address_line_1"] == form_answers()["support_address"]["building_and_street_line_1"]
        assert message["address_line_2"] == form_answers()["support_address"]["building_and_street_line_2"]
        assert message["address_town_city"] == form_answers()["support_address"]["town_city"]
        assert message["postcode"] == form_answers()["support_address"]["postcode"]
        assert message["has_someone_to_shop"] == form_answers()["do_you_have_someone_to_go_shopping_for_you"]
        assert message["wants_supermarket_deliveries"] == form_answers()["priority_supermarket_deliveries"]
        assert message["wants_social_care"] == form_answers()["basic_care_needs"]
        assert message["has_set_up_account"] == form_answers().get("nhs_sub")
        assert message["told_to_shield"] == form_answers()["nhs_letter"]


def test_send_message_with_postcode_has_no_space():
    with _current_app.test_request_context() as test_request_ctx, \
         patch("vulnerable_people_form.integrations.notifications.boto3") as boto3:
        test_request_ctx.session["form_answers"] = {
            "nhs_number": "1234567890",
            "date_of_birth": {
                "day": "01",
                "month": "03",
                "year": "1994"
            },
            "name": {
                "first_name": "FirstName",
                "last_name": "LastName",
            },
            "contact_details": {
                "email": "email@test.com",
            },
            "support_address": {
                "building_and_street_line_1": "101 Test Block",
                "building_and_street_line_2": "Test Lane",
                "town_city": "London",
                "postcode": "N11AA"
            },
            "nhs_letter": 1
        }
        submission_id = "test-registration-number"

        send_message(submission_id)
        message = json.loads(boto3.mock_calls[1][2]["MessageBody"])

        assert message["postcode"] == "N1 1AA"


def test_send_message_where_optional_values_are_none():
    with _current_app.test_request_context() as test_request_ctx, \
         patch("vulnerable_people_form.integrations.notifications.boto3") as boto3:
        test_request_ctx.session["form_answers"] = {
            "nhs_number": "1234567890",
            "date_of_birth": {
                "day": "01",
                "month": "03",
                "year": "1994"
            },
            "name": {
                "first_name": "FirstName",
                "last_name": "LastName",
            },
            "contact_details": {},
            "support_address": {
                "building_and_street_line_1": "101 Test Block",
                "town_city": "London",
                "postcode": "N11AA"
            },
            "nhs_letter": 1
        }
        submission_id = "test-registration-number"

        send_message(submission_id)
        message = json.loads(boto3.mock_calls[1][2]["MessageBody"])

        assert message["email"] is None
        assert message["phone_number_texts"] is None
        assert message["has_someone_to_shop"] is None
        assert message["wants_supermarket_deliveries"] is None
        assert message["wants_social_care"] is None
        assert message["has_set_up_account"] is None


def test_send_message_fill_leading_zero_on_date_of_birth():
    with _current_app.test_request_context() as test_request_ctx, \
         patch("vulnerable_people_form.integrations.notifications.boto3") as boto3:
        test_request_ctx.session["form_answers"] = {
            "nhs_number": "1234567890",
            "date_of_birth": {
                "day": "1",
                "month": "3",
                "year": "1994"
            },
            "name": {
                "first_name": "FirstName",
                "last_name": "LastName",
            },
            "contact_details": {},
            "support_address": {
                "building_and_street_line_1": "101 Test Block",
                "town_city": "London",
                "postcode": "N11AA"
            },
            "nhs_letter": 1
        }
        submission_id = "test-registration-number"

        send_message(submission_id)
        message = json.loads(boto3.mock_calls[1][2]["MessageBody"])

        assert message["date_of_birth"] == "1994/03/01"
