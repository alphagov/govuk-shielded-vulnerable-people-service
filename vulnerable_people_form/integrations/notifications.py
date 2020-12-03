import logging
import json

import boto3
from botocore.config import Config
from flask import current_app

from vulnerable_people_form.form_pages.shared.form_utils import postcode_with_spaces
from vulnerable_people_form.form_pages.shared.session import form_answers
from vulnerable_people_form.form_pages.shared.logger_utils import init_logger

logger = logging.getLogger(__name__)
init_logger(logger)

boto3_config = Config(
    retries={
        "max_attempts": 5,
        "mode": "standard",
    }
)


def get_client_kwargs(app=current_app):
    return {
        "endpoint_url": app.config.get("LOCAL_SQS_ENDPOINT_URL"),
        "aws_access_key_id": app.config.get("AWS_ACCESS_KEY"),
        "aws_secret_access_key": app.config.get("AWS_SECRET_ACCESS_KEY"),
        "region_name": app.config.get("AWS_REGION"),
    }


def get_sqs_client(app=current_app):
    return boto3.client("sqs", **get_client_kwargs(app))


def send_message(registration_number, app=current_app):
    client = get_sqs_client()

    spaced_postcode = postcode_with_spaces(form_answers()["support_address"]["postcode"])
    date_of_birth = form_answers()["date_of_birth"]

    message = {
        "submission_id": registration_number,
        "nhs_number": form_answers()["nhs_number"],
        "date_of_birth": f"{date_of_birth['year']}/{date_of_birth['month']}/{date_of_birth['day']}",
        "first_name": form_answers()["name"]["first_name"],
        "last_name": form_answers()["name"]["last_name"],
        "email": form_answers()["contact_details"].get("email"),
        "phone_number_texts": form_answers()["contact_details"].get("phone_number_texts"),
        "address_line_1": form_answers()["support_address"]["building_and_street_line_1"],
        "address_line_2": form_answers()["support_address"].get("building_and_street_line_2"),
        "address_town_city": form_answers()["support_address"]["town_city"],
        "postcode": spaced_postcode,
        "has_someone_to_shop": form_answers().get("do_you_have_someone_to_go_shopping_for_you"),
        "wants_supermarket_deliveries": form_answers().get("priority_supermarket_deliveries"),
        "wants_social_care": form_answers().get("basic_care_needs"),
        "has_set_up_account": form_answers().get("nhs_sub"),
        "told_to_shield": form_answers()["nhs_letter"]
    }

    return client.send_message(
        QueueUrl=app.config.get("AWS_SQS_QUEUE_URL"),
        MessageBody=json.dumps(message)
    )
