from unittest.mock import patch

import pytest

from vulnerable_people_form.integrations.postcode_eligibility import check_postcode, get_ladcode


@pytest.mark.parametrize("stored_proc_return_value, expected_output",
                         [("YES", True), ("NO", False)])
def test_check_postcode_should_return_correct_eligibility_value(
        stored_proc_return_value, expected_output):
    with patch("vulnerable_people_form.integrations.postcode_eligibility.execute_sql",
               return_value={"records": [[{"stringValue": stored_proc_return_value}]]}):
        postcode_is_eligible_for_support = check_postcode("LS1 1BA")
        assert postcode_is_eligible_for_support == expected_output


def test_check_postcode_should_raise_error_when_db_returns_unexpected_value():
    with patch("vulnerable_people_form.integrations.postcode_eligibility.execute_sql",
               return_value={"records": [[{"stringValue": "INVALID_VALUE"}]]}), \
         pytest.raises(ValueError) as exception_info:
        check_postcode("LS1 1BA")
        assert "RDS procedure returned unrecognised value" in str(exception_info.value)


def test_get_ladcode_should_return_empty_result_set_if_postcode_not_found():
    with patch("vulnerable_people_form.integrations.postcode_eligibility.execute_sql",
               return_value={"records": []}):
        lacode = get_ladcode("BD3 1BA")
        assert not lacode


@pytest.mark.parametrize("stored_proc_return_value, expected_output", [("E08000014", "E08000014")])
def test_get_ladcode_should_return_valid_ladcode_if_postcode_found(
        stored_proc_return_value, expected_output):
    with patch("vulnerable_people_form.integrations.postcode_eligibility.execute_sql",
               return_value={"records": [[{"stringValue": stored_proc_return_value}]]}):
        ladcode = get_ladcode("B21 1BA")
        assert ladcode == expected_output
