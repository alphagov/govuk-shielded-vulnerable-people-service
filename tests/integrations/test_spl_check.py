from unittest.mock import patch

import pytest

from vulnerable_people_form.integrations.spl_check import check_spl


@pytest.mark.parametrize("stored_proc_return_value, expected_output",
                         [("YES", True), ("NO", False)])
def test_spl_check_should_return_correct_is_on_spl_value(
        stored_proc_return_value, expected_output):
    with patch("vulnerable_people_form.integrations.spl_check.execute_sql",
               return_value={"records": [[{"stringValue": stored_proc_return_value}]]}):
        user_is_on_spl = check_spl("1116432455", {"day": 19, "month": 11, "year": 1987})
        assert user_is_on_spl == expected_output


def test_spl_check_should_raise_error_when_db_returns_unexpected_value():
    with patch("vulnerable_people_form.integrations.spl_check.execute_sql",
               return_value={"records": [[{"stringValue": "INVALID_VALUE"}]]}), \
         pytest.raises(ValueError) as exception_info:
        check_spl("1116432455", {"day": 19, "month": 11, "year": 1987})
        assert "RDS procedure returned unrecognised value" in str(exception_info.value)
