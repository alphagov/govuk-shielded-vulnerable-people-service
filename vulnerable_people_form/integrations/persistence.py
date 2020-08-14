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


def generate_string_parameter(name, value):
    return {
        "name": name,
        "value": {"isNull": True} if value is None or value == '' else {"stringValue": value,},
    }


def generate_int_parameter(name, value):
    return {
        "name": name,
        "value": {"isNull": True} if value is None else {"doubleValue": value,},
    }


def generate_bigint_parameter(name, value):
    return {
        "name": name,
        "value": {"isNull": True} if value is None else {"longValue": value,},
    }


def generate_date_parameter(name, value):
    return {
        "name": name,
        "typeHint": "DATE",
        "value": {"isNull": True}
        if value is None
        else {"stringValue": "{year}-{month:0>2}-{day:0>2}".format(**value),},
    }


def execute_sql(sql, parameters):
    return get_rds_data_client().execute_sql(
        sql=sql,
        parameters=parameters,
        database=current_app.config["AWS_RDS_DATABASE"],
        resourceArn=current_app.config["AWS_RDS_RESOURCE_ARN"],
        secretArn=current_app.config["AWS_RDS_SECRET_ARN"],
        schema=current_app.config.get("AWS_RDS_DATABASE_SCHEMA"),
    )


def persist_answers(
    nhs_number,
    first_name,
    middle_name,
    last_name,
    date_of_birth,
    address_line1,
    address_line2,
    address_town_city,
    address_county,
    address_postcode,
    address_uprn,
    contact_number_calls,
    contact_number_texts,
    contact_email,
    uid_nhs_login,
    are_you_applying_on_behalf_of_someone_else,
    have_you_received_an_nhs_letter,
    do_you_want_supermarket_deliveries,
    do_you_need_help_meeting_your_basic_care_needs,
    do_you_have_any_special_dietary_requirements,
    do_you_have_someone_in_the_house_to_carry_deliveries,
    do_you_have_one_of_the_listed_medical_conditions,
):
    result = execute_sql(
        sql="CALL cv_staging.create_web_submission("
        ":nhs_number,"
        ":first_name,"
        ":middle_name,"
        ":last_name,"
        ":date_of_birth,"
        ":address_line1,"
        ":address_line2,"
        ":address_town_city,"
        ":address_county,"
        ":address_postcode,"
        ":address_uprn,"
        ":contact_number_calls,"
        ":contact_number_texts,"
        ":contact_email,"
        ":uid_nhs_login,"
        ":are_you_applying_on_behalf_of_someone_else,"
        ":have_you_received_an_nhs_letter,"
        ":do_you_want_supermarket_deliveries,"
        ":do_you_need_help_meeting_your_basic_care_needs,"
        ":do_you_have_any_special_dietary_requirements,"
        ":do_you_have_someone_in_the_house_to_carry_deliveries,"
        ":do_you_have_one_of_the_listed_medical_conditions"
        ")",
        parameters=(
            generate_string_parameter("nhs_number", nhs_number),
            generate_int_parameter(
                "have_you_received_an_nhs_letter", have_you_received_an_nhs_letter
            ),
            generate_string_parameter("first_name", first_name),
            generate_string_parameter("middle_name", middle_name),
            generate_string_parameter("last_name", last_name),
            generate_string_parameter("address_line1", address_line1),
            generate_string_parameter("address_town_city", address_town_city),
            generate_string_parameter("address_postcode", address_postcode),
            generate_string_parameter("address_county", address_county),
            generate_bigint_parameter("address_uprn", address_uprn),
            generate_string_parameter("contact_number_calls", contact_number_calls),
            generate_string_parameter("contact_number_texts", contact_number_texts),
            generate_string_parameter("contact_email", contact_email),
            generate_int_parameter(
                "do_you_have_one_of_the_listed_medical_conditions",
                do_you_have_one_of_the_listed_medical_conditions,
            ),
            generate_int_parameter(
                "are_you_applying_on_behalf_of_someone_else",
                are_you_applying_on_behalf_of_someone_else,
            ),
            generate_int_parameter(
                "do_you_want_supermarket_deliveries", do_you_want_supermarket_deliveries
            ),
            generate_date_parameter("date_of_birth", date_of_birth),
            generate_int_parameter(
                "do_you_have_someone_in_the_house_to_carry_deliveries",
                do_you_have_someone_in_the_house_to_carry_deliveries,
            ),
            generate_string_parameter("uid_nhs_login", uid_nhs_login),
            generate_string_parameter("address_line2", address_line2),
            generate_int_parameter(
                "do_you_have_any_special_dietary_requirements",
                do_you_have_any_special_dietary_requirements,
            ),
            generate_int_parameter(
                "do_you_need_help_meeting_your_basic_care_needs",
                do_you_need_help_meeting_your_basic_care_needs,
            ),
        ),
    )
    submission_reference = result["records"][0][1]["stringValue"]
    return submission_reference


def load_answers(nhs_uid):
    records = execute_sql(
        "CALL cv_base.retrieve_latest_web_submission_for_nhs_login("
        "    :uid_nhs_login"
        ")",
        (generate_string_parameter("uid_nhs_login", nhs_uid),),
    )["records"]

    if len(records) > 1:
        raise ValueError("Answers returned more than one result")
    return None if not records else records[0]
