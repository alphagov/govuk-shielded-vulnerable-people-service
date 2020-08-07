import boto3
import contextlib
import datetime
import decimal
import secrets
import time

from flask import current_app


def get_rds_data_client():
    return boto3.client("rds-data")


def _form_response_database_name():
    return current_app.config.get("AWS_RDS_DATABASE", "coronavirus-vulnerable-people")


def generate_uid_form():
    return f'{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")}-{secrets.token_hex(3)}'


def generate_string_parameter(name, value):
    return ({"name": name, "value": {"stringValue": value,},},)


def generate_date_parameter(name, value):
    return ({"name": name, "typeHint": "DATE", "value": {"stringValue": value,},},)


def execute_sql(sql, parameters):
    return get_rds_data_client().execute_sql(
        sql=sql,
        parameters=parameters,
        database=current_app.config["AWS_RDS_DATABASE"],
        resourceArn=current_app.config["AWS_RDS_RESOURCE_ARN"],
        secretArn=current_app.config["AWS_RDS_SECRET_ARN"],
        schema=current_app.config.get("AWS_RDS_DATABASE_SCHEMA"),
    )


def update_answers(
    uid_form,
    nhs_number,
    nhs_letter,
    first_name,
    middle_name,
    last_name,
    address_line1,
    address_town_city,
    address_postcode,
    address_county,
    address_uprn,
    contact_number_calls,
    contact_number_texts,
    contact_email,
    medical_conditions,
    applying_on_own_behalf,
    do_you_want_supermarket_deliveries,
    date_of_birth,
    carry_supplies=None,
    uid_nhs_login=None,
    address_line2=None,
    dietary_requirements=None,
):
    get_rds_data_client().execute_sql(
        continueAfterTimeout=True,
        sql="CALL submit_web_form("
        "    nhs_number := :nhs_number,"
        "    nhs_letter := :nhs_letter,"
        "    first_name := :first_name,"
        "    middle_name := :middle_name,"
        "    last_name := :last_name,"
        "    address_line1 := :address_line1,"
        "    address_town_city := :address_town_city,"
        "    address_postcode := :address_postcode,"
        "    address_county := :address_county,"
        "    address_uprn := :address_uprn,"
        "    contact_number_calls := :contact_number_calls,"
        "    contact_number_texts := :contact_number_texts,"
        "    contact_email := :contact_email,"
        "    medical_conditions := :medical_conditions,"
        "    applying_on_own_behalf := :applying_on_own_behalf,"
        "    do_you_want_supermarket_deliveries := :do_you_want_supermarket_deliveries,"
        "    date_of_birth := :date_of_birth,"
        "    carry_supplies := :carry_supplies,"
        "    uid_nhs_login := :uid_nhs_login,"
        "    address_line2 := :address_line2,"
        "    uid_form := :uid_form,"
        "    dietary_requirements := :dietary_requirements,"
        ")",
        parameters=(
            generate_string_parameter("nhs_number", nhs_number),
            generate_string_parameter("nhs_letter", nhs_letter),
            generate_string_parameter("first_name", first_name),
            generate_string_parameter("middle_name", middle_name),
            generate_string_parameter("last_name", last_name),
            generate_string_parameter("address_line1", address_line1),
            generate_string_parameter("address_town_city", address_town_city),
            generate_string_parameter("address_postcode", address_postcode),
            generate_string_parameter("address_county", address_county),
            generate_string_parameter("address_uprn", address_uprn),
            generate_string_parameter("contact_number_calls", contact_number_calls),
            generate_string_parameter("contact_number_texts", contact_number_texts),
            generate_string_parameter("contact_email", contact_email),
            generate_string_parameter("medical_conditions", medical_conditions),
            generate_string_parameter("applying_on_own_behalf", applying_on_own_behalf),
            generate_string_parameter(
                "do_you_want_supermarket_deliveries", do_you_want_supermarket_deliveries
            ),
            generate_string_parameter("date_of_birth", date_of_birth),
            generate_string_parameter("carry_supplies", carry_supplies),
            generate_string_parameter("uid_nhs_login", uid_nhs_login),
            generate_string_parameter("address_line2", address_line2),
            generate_string_parameter("uid_form", uid_form),
            dietary_requirements,
        ),
    )
    return uid_form


def load_answers(nhs_uid):
    records = get_rds_data_client().execute_sql(
        "CALL retrieve_answers(:nhs_uid)", (nhs_uid,)
    )["records"]
    if len(records) > 0:
        raise ValueError("Answers returned more than one result")
    return None if not records else records[0]
