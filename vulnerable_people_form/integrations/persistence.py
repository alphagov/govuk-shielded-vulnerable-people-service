import contextlib
import datetime
import decimal
import secrets
import time


import psycopg2
from psycopg2.extensions import cursor
from psycopg2.extras import DictCursor
from flask import current_app


def get_postgres_client():
    return psycopg2.connect(
        host=current_app.config.get("POSTGRES_HOST"),
        database=current_app.config.get("POSTGRES_DB_NAME"),
        user=current_app.config.get("POSTGRES_USER"),
        password=current_app.config.get("POSTGRES_PASSWORD"),
        cursor_factory=DictCursor,
    )


postgres_connection = None


@contextlib.contextmanager
def postgres_cursor():
    if postgres_connection is None or postgres_connection.closed != 0:
        postgres_connection = psycopg2.connect()
    yield postgres_connection.cursor()


def _form_response_database_name():
    return current_app.config.get("AWS_RDS_DATABASE", "coronavirus-vulnerable-people")


def generate_uid_form():
    return f'{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")}-{secrets.token_hex(3)}'


def generate_string_parameter(name, value):
    return ({"name": name, "value": {"stringValue": value,},},)


def save_answers(*args, **kwargs):
    uid_form = generate_uid_form()
    update_answers(uid_form, *args, **kwargs)
    return uid_form


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
    with postgres_cursor() as _cursor:
        _cursor.execute(
            "CALL submit_web_form("
            "    nhs_number := %s,"
            "    nhs_letter := %s,"
            "    first_name := %s,"
            "    middle_name := %s,"
            "    last_name := %s,"
            "    address_line1 := %s,"
            "    address_town_city := %s,"
            "    address_postcode := %s,"
            "    address_county := %s,"
            "    address_uprn := %s,"
            "    contact_number_calls := %s,"
            "    contact_number_texts := %s,"
            "    contact_email := %s,"
            "    medical_conditions := %s,"
            "    applying_on_own_behalf := %s,"
            "    do_you_want_supermarket_deliveries := %s,"
            "    date_of_birth := %s,"
            "    carry_supplies := %s,"
            "    uid_nhs_login := %s,"
            "    address_line2 := %s,"
            "    uid_form := %s,"
            "    dietary_requirements := %s,"
            ")",
            (
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
                carry_supplies,
                uid_nhs_login,
                address_line2,
                uid_form,
                dietary_requirements,
            ),
        )
    return uid_form


def load_answers(nhs_uid):
    with postgres_cursor() as _cursor:
        rec = _cursor.execute("CALL retrieve_answers(%s)", (nhs_uid,))
        return rec.fetchone()  # there will only be one result
