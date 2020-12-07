from unittest.mock import patch

import pytest

from vulnerable_people_form.integrations.location_eligibility import (is_postcode_in_england,
                                                                      get_postcode_tier, get_uprn_tier)

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
