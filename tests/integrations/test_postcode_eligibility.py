from unittest.mock import patch

import pytest

from vulnerable_people_form.form_pages.shared.constants import PostcodeTier
from vulnerable_people_form.integrations.postcode_eligibility import check_postcode, get_ladcode, get_postcode_tier


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


def test_get_postcode_tier_should_return_none_when_ladcode_not_found():
    postcode = "LS11BA"
    with patch("vulnerable_people_form.integrations.postcode_eligibility.get_ladcode",
               return_value=None) as mock_get_ladcode:
        postcode_tier = get_postcode_tier(postcode)
        assert mock_get_ladcode.called_once_with(postcode)
        assert postcode_tier is None


def test_get_postcode_tier_should_invoke_get_tier_by_ladcode_when_ladcode_retrieved():
    postcode = "LS11BA"
    ladcode = "E08000014"
    postcode_tier = PostcodeTier.VERY_HIGH.value

    with patch("vulnerable_people_form.integrations.postcode_eligibility.get_ladcode",
               return_value=ladcode) as mock_get_ladcode, \
        patch("vulnerable_people_form.integrations.postcode_eligibility.get_tier_by_ladcode",
              return_value=postcode_tier) as mock_get_tier_by_ladcode:
        postcode_tier = get_postcode_tier(postcode)
        assert mock_get_ladcode.called_once_with(postcode)
        assert mock_get_tier_by_ladcode.called_once_with(ladcode)
        assert postcode_tier == postcode_tier


def test_get_postcode_tier_should_raise_a_value_error_when_an_unexpected_postcode_tier_is_retrieved():
    postcode = "LS11BA"
    ladcode = "E08000014"
    postcode_tier = 8

    with patch("vulnerable_people_form.integrations.postcode_eligibility.get_ladcode",
               return_value=ladcode) as mock_get_ladcode, \
        patch("vulnerable_people_form.integrations.postcode_eligibility.get_tier_by_ladcode",
              return_value=postcode_tier) as mock_get_tier_by_ladcode, \
            pytest.raises(ValueError) as err_info:
        get_postcode_tier(postcode)
        assert mock_get_ladcode.called_once_with(postcode)
        assert mock_get_tier_by_ladcode.called_once_with(ladcode)
    assert str(err_info.value) == f"Unexpected postcode tier retrieved: {postcode_tier}"
