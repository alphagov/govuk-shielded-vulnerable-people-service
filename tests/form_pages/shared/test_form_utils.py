import pytest

from vulnerable_people_form.form_pages.shared.form_utils import (
    clean_nhs_number,
    sanitise_date,
    strip_non_digits,
    sanitise_name)


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


def test_strip_non_digits_should_remove_characters_that_are_not_digits():
    stripped_value = strip_non_digits("123sdfsd4 !~)%|*-")
    assert stripped_value == "1234"


def test_strip_non_digits_should_not_remove_digit_characters():
    stripped_value = strip_non_digits("12345")
    assert stripped_value == "12345"


def test_sanitise_date_of_birth_should_remove_non_digit_characters_from_date():
    test_date = {"day": "12  ", "month": "^05!", "year": "1987xdvxv^&*"}
    sanitise_date(test_date)
    assert test_date["day"] == "12"
    assert test_date["month"] == "05"
    assert test_date["year"] == "1987"


def test_sanitise_date_of_birth_should_not_remove_digit_characters_from_date():
    test_date = {"day": "13", "month": "7", "year": "1991"}
    sanitise_date(test_date)
    assert test_date["day"] == "13"
    assert test_date["month"] == "7"
    assert test_date["year"] == "1991"


def test_sanitise_date_of_birth_should_raise_error_when_invalid_length_dict_supplied():
    test_date = {"day": "13", "month": "7", "year": "1991", "random_field": "test"}
    with pytest.raises(ValueError) as exception_info:
        sanitise_date(test_date)
        assert "Unexpected date_of_birth encountered" in str(exception_info.value)


def test_sanitise_date_of_birth_should_raise_error_when_invalid_dict_supplied():
    test_date = {"day": "13", "month": "7", "invalid_field": "test"}
    with pytest.raises(ValueError) as exception_info:
        sanitise_date(test_date)
        assert "Unexpected date_of_birth encountered" in str(exception_info.value)


def test_sanitise_name_should_strip_leading_and_trailing_whitespace():
    test_name = {"first_name": "    ", "middle_name": " middle name  ", "last_name": "    Smith"}
    sanitise_name(test_name)
    assert test_name["first_name"] == ""
    assert test_name["middle_name"] == "middle name"
    assert test_name["last_name"] == "Smith"


def test_sanitise_name_should_raise_error_when_invalid_length_dict_supplied():
    test_name = {"first_name": "Tom", "middle_name": "", "last_name": "Smith", "invalid_field": "test"}
    with pytest.raises(ValueError) as exception_info:
        sanitise_name(test_name)
        assert "Unexpected name value encountered" in str(exception_info.value)


def test_sanitise_name_should_raise_error_when_invalid_dict_supplied():
    test_name = {"first_name": "Tom", "middle_name": "", "invalid_field": "test"}
    with pytest.raises(ValueError) as exception_info:
        sanitise_name(test_name)
        assert "Unexpected name value encountered" in str(exception_info.value)
