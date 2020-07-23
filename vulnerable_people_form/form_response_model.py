import boto3
import datetime
import decimal
import secrets
import time

from flask import current_app


def get_dynamodb_client():
    return boto3.resource(
        "dynamodb", endpoint_url=current_app.config.get("AWS_ENDPOINT_URL")
    )


def _form_response_tablename():
    return current_app.config.get(
        "AWS_DYNAMODB_SUBMISSIONS_TABLE_NAME", "coronavirus-vulnerable-people"
    )


def generate_reference_number():
    return f'{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")}-{secrets.token_hex(3)}'


def write_answers_to_table(answers):
    get_dynamodb_client().Table(_form_response_tablename()).put_item(
        Item={
            "ReferenceId": generate_reference_number(),
            "UnixTimestamp": decimal.Decimal(time.time()),
            "FormResponse": answers,
        }
    )


def create_tables_if_not_exist():
    # get_dynamodb_client().delete_table(TableName="coronavirus-vulnerable-people")
    client = get_dynamodb_client()
    try:
        client.create_table(
            TableName=_form_response_tablename(),
            KeySchema=[
                {"AttributeName": "ReferenceId", "KeyType": "HASH"},
                {"AttributeName": "UnixTimestamp", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "ReferenceId", "AttributeType": "S"},
                {"AttributeName": "UnixTimestamp", "AttributeType": "N"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 120, "WriteCapacityUnits": 20},
        )
    except client.meta.client.exceptions.ResourceInUseException:
        return False
    return True

