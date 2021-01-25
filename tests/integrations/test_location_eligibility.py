from unittest.mock import patch

import pytest
from flask import Flask

from vulnerable_people_form.integrations.location_eligibility import (is_postcode_in_england,
                                                                      get_postcode_tier, get_uprn_tier,
                                                                      get_shielding_advice_by_uprn,
                                                                      get_shielding_advice_by_postcode)

from vulnerable_people_form.form_pages.shared.constants import PostcodeTier

_current_app = Flask(__name__)


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


def test_get_shielding_advice_by_postcode_should_raise_error():
    with patch("vulnerable_people_form.integrations.location_eligibility.execute_sql",
               return_value={"records": [[{"longValue": "INVALID_VALUE"}]]}), \
               pytest.raises(ValueError) as exception_info:
        get_shielding_advice_by_postcode("LSas1BA111")
        assert "RDS procedure returned unrecognised value" in str(exception_info.value)


def test_get_shielding_advice_by_uprn_should_raise_error():
    with patch("vulnerable_people_form.integrations.location_eligibility.execute_sql",
               return_value={"records": [[{"longValue": "INVALID_VALUE"}]]}), \
               pytest.raises(ValueError) as exception_info:
        get_shielding_advice_by_uprn("asasas")
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


@pytest.mark.parametrize("stored_proc_return_value, expected_output",
                         [(0, 0), (1, 1)])
def test_get_shielding_advice_by_uprn_should_return_correct_eligibility_value(
        stored_proc_return_value, expected_output):
    with patch("vulnerable_people_form.integrations.location_eligibility.execute_sql",
               return_value={"records": [[{"longValue": stored_proc_return_value}]]}):
        uprn_shielding = get_shielding_advice_by_uprn("10000000")
    assert uprn_shielding == expected_output


@pytest.mark.parametrize("stored_proc_return_value, expected_output",
                         [(0, 0), (1, 1)])
def test_get_shielding_advice_by_postcode_should_return_correct_eligibility_value(
        stored_proc_return_value, expected_output):
    with patch("vulnerable_people_form.integrations.location_eligibility.execute_sql",
               return_value={"records": [[{"longValue": stored_proc_return_value}]]}):
        postcode_shielding = get_shielding_advice_by_postcode("BB1 1TA")
    assert postcode_shielding == expected_output
