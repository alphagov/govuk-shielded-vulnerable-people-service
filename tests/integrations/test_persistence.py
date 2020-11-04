import pytest
from flask import Flask
from unittest.mock import patch

from vulnerable_people_form.integrations.persistence import (
    get_client_kwargs,
    generate_string_parameter,
    generate_int_parameter,
    generate_bigint_parameter,
    generate_date_parameter,
    persist_answers,
    persist_answers_with_tier,
    _postcode_tier_map,
    load_answers, init_app)

_current_app = Flask(__name__)
_current_app.secret_key = 'test_secret'

_current_app.config["GOVUK_NOTIFY_SPL_MATCH_EMAIL_TEMPLATE_ID"] = "match_email_template_id"

_AWS_ENDPOINT_URL = "endpoint_url"
_AWS_ACCESS_KEY = "access_key"
_AWS_SECRET_KEY = "secret_key"
_AWS_REGION = "region"

_current_app.config["LOCAL_AWS_ENDPOINT_URL"] = "endpoint_url"
_current_app.config["AWS_ACCESS_KEY"] = "access_key"
_current_app.config["AWS_SECRET_ACCESS_KEY"] = "secret_key"
_current_app.config["AWS_REGION"] = "region"


def test_get_client_kwargs_should_return_args_populated_from_app_config():
    kwargs = get_client_kwargs(_current_app)
    assert kwargs["endpoint_url"] == _AWS_ENDPOINT_URL
    assert kwargs["aws_access_key_id"] == _AWS_ACCESS_KEY
    assert kwargs["aws_secret_access_key"] == _AWS_SECRET_KEY
    assert kwargs["region_name"] == _AWS_REGION


def test_init_app_should_use_overridden_aws_rds_db_arn_and_secret_when_override_config_present():
    arn_override_value = "overridden_arn"
    secret_override_value = "overridden_secret"
    _current_app.config["AWS_RDS_DATABASE_ARN_OVERRIDE"] = arn_override_value
    _current_app.config["AWS_RDS_SECRET_ARN_OVERRIDE"] = secret_override_value
    init_app(_current_app)
    assert _current_app.config["AWS_RDS_DATABASE_ARN"] == arn_override_value
    assert _current_app.config["AWS_RDS_SECRET_ARN"] == secret_override_value
    _current_app.config.pop("AWS_RDS_DATABASE_ARN_OVERRIDE", None)
    _current_app.config.pop("AWS_RDS_SECRET_ARN_OVERRIDE", None)


def test_init_app_should_get_aws_rds_config_from_aws_when_no_override_config_present():
    arn_value = "aws_test_arn"
    secret_value = "aws_secret"

    with patch("vulnerable_people_form.integrations.persistence._find_database_arn",
               return_value=arn_value) as mock_find_db_arn, \
            patch("vulnerable_people_form.integrations.persistence._find_database_secret_arn",
                  return_value=secret_value) as mock_find_db_secret_arn:
        init_app(_current_app)
        mock_find_db_arn.asert_called_once_with(_current_app)
        mock_find_db_secret_arn.assert_called_once_with(_current_app)
        assert _current_app.config["AWS_RDS_DATABASE_ARN"] == arn_value
        assert _current_app.config["AWS_RDS_SECRET_ARN"] == secret_value


@pytest.mark.parametrize("param_name, param_value, expected_value",
                         [("test_name", "test_value", {"stringValue": "test_value"}),
                          ("test_name", None, {"isNull": True})])
def test_generate_string_parameter_should_return_dict_for_valid_arguments(param_name, param_value, expected_value):
    generated_param = generate_string_parameter(param_name, param_value)
    assert generated_param["name"] == param_name
    assert generated_param["value"] == expected_value


@pytest.mark.parametrize("param_name, param_value, expected_value",
                         [("test_name", 123, {"doubleValue": 123}),
                          ("test_name", None, {"isNull": True})])
def test_generate_int_parameter_should_return_dict_for_valid_arguments(param_name, param_value, expected_value):
    generated_param = generate_int_parameter(param_name, param_value)
    assert generated_param["name"] == param_name
    assert generated_param["value"] == expected_value


@pytest.mark.parametrize("param_name, param_value, expected_value",
                         [("test_name", 116433571646301278737566203, {"longValue": 116433571646301278737566203}),
                          ("test_name", None, {"isNull": True})])
def test_generate_bigint_parameter_should_return_dict_for_valid_arguments(param_name, param_value, expected_value):
    generated_param = generate_bigint_parameter(param_name, param_value)
    assert generated_param["name"] == param_name
    assert generated_param["value"] == expected_value


@pytest.mark.parametrize("param_name, param_value, expected_value",
                         [("test_name", {"day": 12, "month": 9, "year": "1967"}, {"stringValue": "1967-09-12"}),
                          ("test_name", None, {"isNull": True})])
def test_generate_date_parameter_should_return_dict_for_valid_arguments(param_name, param_value, expected_value):
    generated_param = generate_date_parameter(param_name, param_value)
    assert generated_param["name"] == param_name
    assert generated_param["value"] == expected_value
    assert generated_param["typeHint"] == "DATE"


def test_persist_answers_should_map_parameters_correctly_with_tier():
    submission_ref = "1234"

    nhs_number = "1116432455"
    first_name = "Tommy"
    middle_name = None
    last_name = "Tester"
    date_of_birth = {"day": 15, "month": 7, "year": 1981}
    address_line1 = "12 Test Avenue"
    address_line2 = None
    address_town_city = "Leeds"
    address_postcode = "LS1 1BA"
    address_uprn = None
    contact_number_calls = "0113 123 4566"
    contact_number_texts = "07404 123 4567"
    contact_email = "test_email@gmail.com"
    uid_nhs_login = None
    are_you_applying_on_behalf_of_someone_else = 0
    have_you_received_an_nhs_letter = 1
    do_you_want_supermarket_deliveries = 1
    do_you_need_help_meeting_your_basic_care_needs = 1
    do_you_have_someone_to_go_shopping_for_you = 1
    do_you_have_one_of_the_listed_medical_conditions = 0
    do_you_live_in_england = 1
    tier_at_submission = "HIGH"

    with patch("vulnerable_people_form.integrations.persistence.execute_sql",
               return_value={"records": [[None, {"stringValue": submission_ref}]]}) as mock_execute_sql:
        submission_reference = persist_answers_with_tier(
            nhs_number,
            first_name,
            middle_name,
            last_name,
            date_of_birth,
            address_line1,
            address_line2,
            address_town_city,
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
            do_you_have_someone_to_go_shopping_for_you,
            do_you_have_one_of_the_listed_medical_conditions,
            do_you_live_in_england,
            tier_at_submission)

        assert submission_reference == submission_ref
        mock_execute_sql.assert_called_once_with(
            sql="CALL cv_staging.create_web_submission_with_tier("
                ":nhs_number,"
                ":first_name,"
                ":middle_name,"
                ":last_name,"
                ":date_of_birth,"
                ":address_line1,"
                ":address_line2,"
                ":address_town_city,"
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
                ":do_you_have_someone_to_go_shopping_for_you,"
                ":do_you_have_one_of_the_listed_medical_conditions,"
                ":do_you_live_in_england,"
                ":tier_at_submission"
                ")",
            parameters=(
                {"name": "nhs_number", "value": {"stringValue": nhs_number}},
                {
                    "name": "have_you_received_an_nhs_letter",
                    "value": {"doubleValue": have_you_received_an_nhs_letter}
                },
                {"name": "first_name", "value": {"stringValue": first_name}},
                {"name": "middle_name", "value": {"isNull": True}},
                {"name": "last_name", "value": {"stringValue": last_name}},
                {"name": "address_line1", "value": {"stringValue": address_line1}},
                {"name": "address_postcode", "value": {"stringValue": address_postcode}},
                {"name": "address_town_city", "value": {"stringValue": address_town_city}},
                {"name": "address_uprn", "value": {"isNull": True}},
                {"name": "contact_number_calls", "value": {"stringValue": contact_number_calls}},
                {"name": "contact_number_texts", "value": {"stringValue": contact_number_texts}},
                {"name": "contact_email", "value": {"stringValue": contact_email}},
                {
                    "name": "do_you_have_one_of_the_listed_medical_conditions",
                    "value": {"doubleValue": do_you_have_one_of_the_listed_medical_conditions}
                },
                {
                    "name": "are_you_applying_on_behalf_of_someone_else",
                    "value": {"doubleValue": are_you_applying_on_behalf_of_someone_else}
                },
                {
                    "name": "do_you_want_supermarket_deliveries",
                    "value": {"doubleValue": do_you_want_supermarket_deliveries}
                },
                {
                    "name": "date_of_birth",
                    "typeHint": "DATE",
                    "value": {"stringValue": "1981-07-15"}
                },
                {
                    "name": "do_you_have_someone_to_go_shopping_for_you",
                    "value": {"doubleValue": do_you_have_someone_to_go_shopping_for_you}
                },
                {"name": "uid_nhs_login", "value": {"isNull": True}},
                {"name": "address_line2", "value": {"isNull": True}},
                {
                    "name": "do_you_need_help_meeting_your_basic_care_needs",
                    "value": {"doubleValue": do_you_need_help_meeting_your_basic_care_needs}
                },
                {
                    "name": "do_you_live_in_england",
                    "value": {"doubleValue": do_you_live_in_england}
                },
                {
                    "name": "tier_at_submission",
                    "value": {"doubleValue":  _postcode_tier_map[tier_at_submission]}
                }
            )
        )


def test_persist_answers_should_map_parameters_correctly():
    submission_ref = "1234"

    nhs_number = "1116432455"
    first_name = "Tommy"
    middle_name = None
    last_name = "Tester"
    date_of_birth = {"day": 15, "month": 7, "year": 1981}
    address_line1 = "12 Test Avenue"
    address_line2 = None
    address_town_city = "Leeds"
    address_postcode = "LS1 1BA"
    address_uprn = None
    contact_number_calls = "0113 123 4566"
    contact_number_texts = "07404 123 4567"
    contact_email = "test_email@gmail.com"
    uid_nhs_login = None
    are_you_applying_on_behalf_of_someone_else = 0
    have_you_received_an_nhs_letter = 1
    do_you_want_supermarket_deliveries = 1
    do_you_need_help_meeting_your_basic_care_needs = 1
    do_you_have_someone_to_go_shopping_for_you = 1
    do_you_have_one_of_the_listed_medical_conditions = 0
    do_you_live_in_england = 1
    tier_at_submission = 1

    with patch("vulnerable_people_form.integrations.persistence.execute_sql",
               return_value={"records": [[None, {"stringValue": submission_ref}]]}) as mock_execute_sql:
        submission_reference = persist_answers(
            nhs_number,
            first_name,
            middle_name,
            last_name,
            date_of_birth,
            address_line1,
            address_line2,
            address_town_city,
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
            do_you_have_someone_to_go_shopping_for_you,
            do_you_have_one_of_the_listed_medical_conditions,
            do_you_live_in_england,
            tier_at_submission)

        assert submission_reference == submission_ref
        mock_execute_sql.assert_called_once_with(
                sql="CALL cv_staging.create_web_submission_with_tier("
                ":nhs_number,"
                ":first_name,"
                ":middle_name,"
                ":last_name,"
                ":date_of_birth,"
                ":address_line1,"
                ":address_line2,"
                ":address_town_city,"
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
                ":do_you_have_someone_to_go_shopping_for_you,"
                ":do_you_have_one_of_the_listed_medical_conditions,"
                ":do_you_live_in_england,"
                ":tier_at_submission"
                ")",
            parameters=(
                {"name": "nhs_number", "value": {"stringValue": nhs_number}},
                {
                    "name": "have_you_received_an_nhs_letter",
                    "value": {"doubleValue": have_you_received_an_nhs_letter}
                },
                {"name": "first_name", "value": {"stringValue": first_name}},
                {"name": "middle_name", "value": {"isNull": True}},
                {"name": "last_name", "value": {"stringValue": last_name}},
                {"name": "address_line1", "value": {"stringValue": address_line1}},
                {"name": "address_postcode", "value": {"stringValue": address_postcode}},
                {"name": "address_town_city", "value": {"stringValue": address_town_city}},
                {"name": "address_uprn", "value": {"isNull": True}},
                {"name": "contact_number_calls", "value": {"stringValue": contact_number_calls}},
                {"name": "contact_number_texts", "value": {"stringValue": contact_number_texts}},
                {"name": "contact_email", "value": {"stringValue": contact_email}},
                {
                    "name": "do_you_have_one_of_the_listed_medical_conditions",
                    "value": {"doubleValue": do_you_have_one_of_the_listed_medical_conditions}
                },
                {
                    "name": "are_you_applying_on_behalf_of_someone_else",
                    "value": {"doubleValue": are_you_applying_on_behalf_of_someone_else}
                },
                {
                    "name": "do_you_want_supermarket_deliveries",
                    "value": {"doubleValue": do_you_want_supermarket_deliveries}
                },
                {
                    "name": "date_of_birth",
                    "typeHint": "DATE",
                    "value": {"stringValue": "1981-07-15"}
                },
                {
                    "name": "do_you_have_someone_to_go_shopping_for_you",
                    "value": {"doubleValue": do_you_have_someone_to_go_shopping_for_you}
                },
                {"name": "uid_nhs_login", "value": {"isNull": True}},
                {"name": "address_line2", "value": {"isNull": True}},
                {
                    "name": "do_you_need_help_meeting_your_basic_care_needs",
                    "value": {"doubleValue": do_you_need_help_meeting_your_basic_care_needs}
                },
                {
                    "name": "do_you_live_in_england",
                    "value": {"doubleValue": do_you_live_in_england}
                },
                {
                    "name": "tier_at_submission",
                    "value": {"doubleValue": tier_at_submission},
                }
            )
        )


@pytest.mark.parametrize("execute_sql_return_value", [None, []])
def test_load_answers_should_return_none_when_no_submission_present(execute_sql_return_value):
    with patch("vulnerable_people_form.integrations.persistence.execute_sql",
               return_value={"records": execute_sql_return_value}):
        result = load_answers("test_nhs_uid")
        assert result is None


def test_load_answers_should_raise_error_when_multiple_submissions_present():
    with patch("vulnerable_people_form.integrations.persistence.execute_sql",
               return_value={"records": [{"test_1": 1}, {"test_2": 2}]}), \
            pytest.raises(ValueError) as exception_info:
        load_answers("test_nhs_uid")
        assert "Answers returned more than one result" == str(exception_info.value)


def test_load_answers_should_return_submission_for_valid_nhs_uid():
    mock_return_value = {"records": [{"first_name": "Tom"}]}
    with patch("vulnerable_people_form.integrations.persistence.execute_sql",
               return_value=mock_return_value):
        result = load_answers("test_nhs_uid")
        assert result == mock_return_value["records"][0]
