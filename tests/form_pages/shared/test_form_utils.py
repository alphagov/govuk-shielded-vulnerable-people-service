import pytest

from vulnerable_people_form.form_pages.shared.form_utils import clean_nhs_number


@pytest.mark.parametrize("nhs_num", ["", None])
def test_clean_nhs_number_should_return_empty_string_when_non_truthy_input_provided(nhs_num):
    cleaned_nhs_number = clean_nhs_number(nhs_num)
    assert cleaned_nhs_number is None


@pytest.mark.parametrize("nhs_num, expected_output", [("123-123-1234-", "1231231234"), ("-123456-1234", "1234561234")])
def test_clean_nhs_number_should_strip_hyphens_from_input(nhs_num, expected_output):
    cleaned_nhs_number = clean_nhs_number(nhs_num)
    assert cleaned_nhs_number == expected_output


@pytest.mark.parametrize("nhs_num, expected_output", [("123 123 1234", "1231231234"), (" 123456 1234 ", "1234561234")])
def test_clean_nhs_number_should_strip_whitespace_from_input(nhs_num, expected_output):
    cleaned_nhs_number = clean_nhs_number(nhs_num)
    assert cleaned_nhs_number == expected_output


@pytest.mark.parametrize("nhs_num, expected_output",
                         [("-123-123 1234 ", "1231231234"), ("-123456 123-4 ", "1234561234")])
def test_clean_nhs_number_should_strip_whitespace_and_hyphens_from_input(nhs_num, expected_output):
    cleaned_nhs_number = clean_nhs_number(nhs_num)
    assert cleaned_nhs_number == expected_output
