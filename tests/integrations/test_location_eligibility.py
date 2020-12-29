from unittest.mock import patch

import pytest

from vulnerable_people_form.integrations.location_eligibility import (is_postcode_in_england,
                                                                      get_postcode_tier, get_uprn_tier,
                                                                      get_ladcode_from_postcode,
                                                                      get_ladcode_from_uprn)

from vulnerable_people_form.form_pages.shared.constants import PostcodeTier


def test_get_uprn_tier_should_raise_err():
    with patch("vulnerable_people_form.integrations.location_eligibility.execute_sql",
               return_value={"records": [[{"longValue": "INVALID_VALUE"}]]}), \
               pytest.raises(ValueError) as exception_info:
        get_uprn_tier("asasas")
    assert "RDS procedure returned unrecognised value" in str(exception_info.value)


def test_get_postcode_tier_should_raise_err():
    with patch("vulnerable_people_form.integrations.location_eligibility.execute_sql",
               return_value={"records": [[{"longValue": "INVALID_VALUE"}]]}), \
               pytest.raises(ValueError) as exception_info:
        get_postcode_tier("asasas")
    assert "RDS procedure returned unrecognised value" in str(exception_info.value)


def test_is_postcode_in_england_should_raise_error():
    with patch("vulnerable_people_form.integrations.location_eligibility.execute_sql",
               return_value={"records": [[{"stringValue": "INVALID_VALUE"}]]}), \
               pytest.raises(ValueError) as exception_info:
        is_postcode_in_england("LSas1BA111")
        assert "RDS procedure returned unrecognised value" in str(exception_info.value)


@pytest.mark.parametrize("stored_proc_return_value, expected_output",
                         [(1, PostcodeTier.MEDIUM), (2, PostcodeTier.HIGH)])
def test_get_postcode_tier_should_return_correct_tier(
        stored_proc_return_value, expected_output):
    with patch("vulnerable_people_form.integrations.location_eligibility.execute_sql",
               return_value={"records": [[{"longValue": stored_proc_return_value}]]}):
        postcode_tier = get_postcode_tier("LS1 1BA")
    assert postcode_tier == expected_output


@pytest.mark.parametrize("stored_proc_return_value, expected_output",
                         [("YES", True), ("NO", False)])
def test_is_postcode_in_england_should_return_correct_eligibility_value(
        stored_proc_return_value, expected_output):
    with patch("vulnerable_people_form.integrations.location_eligibility.execute_sql",
               return_value={"records": [[{"stringValue": stored_proc_return_value}]]}):
        postcode_in_england = is_postcode_in_england("LS1 1BA")
    assert postcode_in_england == expected_output


def test_get_ladcode_should_return_empty_result_set_if_postcode_not_found():
    with patch("vulnerable_people_form.integrations.location_eligibility.execute_sql",
               return_value={"records": []}):
        lad_code = get_ladcode_from_postcode("BD3 1BA")
        assert not lad_code


@pytest.mark.parametrize("stored_proc_return_value, expected_output", [("E08000014", "E08000014")])
def test_get_ladcode_should_return_valid_ladcode_if_postcode_found(
        stored_proc_return_value, expected_output):
    with patch("vulnerable_people_form.integrations.location_eligibility.execute_sql",
               return_value={"records": [[{"stringValue": stored_proc_return_value}]]}):
        ladcode = get_ladcode_from_postcode("B21 1BA")
        assert ladcode == expected_output


def test_get_ladcode_should_return_empty_result_set_if_uprn_not_found():
    with patch("vulnerable_people_form.integrations.location_eligibility.execute_sql",
               return_value={"records": []}):
        lacode = get_ladcode_from_uprn("123456789")
        assert not lacode


@pytest.mark.parametrize("stored_proc_return_value, expected_output", [("E08000014", "E08000014")])
def test_get_ladcode_should_return_valid_ladcode_if_uprn_found(
        stored_proc_return_value, expected_output):
    with patch("vulnerable_people_form.integrations.location_eligibility.execute_sql",
               return_value={"records": [[{"stringValue": stored_proc_return_value}]]}):
        ladcode = get_ladcode_from_uprn("123456789")
        assert ladcode == expected_output
