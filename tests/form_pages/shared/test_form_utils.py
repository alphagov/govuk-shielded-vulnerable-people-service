import pytest

from vulnerable_people_form.form_pages.shared.form_utils import (
    clean_nhs_number,
    sanitise_date,
    strip_non_digits,
    sanitise_name,
    sanitise_support_address,
    format_postcode,
    postcode_with_spaces)


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
    assert "Unexpected date_value encountered" in str(exception_info.value)


def test_sanitise_date_of_birth_should_raise_error_when_invalid_dict_supplied():
    test_date = {"day": "13", "month": "7", "invalid_field": "test"}
    with pytest.raises(ValueError) as exception_info:
        sanitise_date(test_date)
    assert "Unexpected date_value encountered" in str(exception_info.value)


def test_sanitise_name_should_strip_leading_and_trailing_whitespace():
    test_name = {"first_name": "    ", "middle_name": " middle name  ", "last_name": "    Smith"}
    sanitised_name = sanitise_name(test_name)
    assert sanitised_name["first_name"] == ""
    assert sanitised_name["middle_name"] == "middle name"
    assert sanitised_name["last_name"] == "Smith"


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


def test_sanitise_support_address_should_strip_leading_and_trailing_whitespace():
    test_case_support_address = {
        "building_and_street_line_1": " address line one   ",
        "building_and_street_line_2": "  address line  two     ",
        "town_city": "  test town city",
        "postcode": "LS1 1BA  "
    }
    sanitised_support_address = sanitise_support_address(test_case_support_address)
    assert sanitised_support_address["building_and_street_line_1"] == "address line one"
    assert sanitised_support_address["building_and_street_line_2"] == "address line  two"
    assert sanitised_support_address["town_city"] == "test town city"
    assert sanitised_support_address["postcode"] == "LS1 1BA"


def test_sanitise_support_address_should_raise_error_when_invalid_length_dict_supplied():
    test_support_address = {
        "building_and_street_line_1": "test",
        "building_and_street_line_2": "",
        "invalid_field": "test"
    }
    with pytest.raises(ValueError) as exception_info:
        sanitise_support_address(test_support_address)
    assert "Unexpected support_address value encountered" in str(exception_info.value)


def test_sanitise_support_address_should_raise_error_when_invalid_dict_supplied():
    test_support_address = {"building_and_street_line_1": "test",
                            "building_and_street_line_2": "test",
                            "town_city": "test",
                            "invalid_field": "test"}
    with pytest.raises(ValueError) as exception_info:
        sanitise_support_address(test_support_address)
    assert "Unexpected support_address value encountered" in str(exception_info.value)


@pytest.mark.parametrize("postcode", ["", None])
def test_format_postcode_should_return_none_for_none_truthy_intput_values(postcode):
    formatted_postcode = format_postcode(postcode)
    assert formatted_postcode is None


@pytest.mark.parametrize("postcode, expected_output", [("LS1  1BA  ", "LS11BA"), ("  SW1A 2NP  ", "SW1A2NP")])
def test_format_postcode_should_remove_whitespace_characters(postcode, expected_output):
    formatted_postcode = format_postcode(postcode)
    assert formatted_postcode == expected_output


@pytest.mark.parametrize("postcode, expected_output", [("ls11bA", "LS11BA"), ("sw1A2np", "SW1A2NP")])
def test_format_postcode_should_convert_to_uppercase(postcode, expected_output):
    formatted_postcode = format_postcode(postcode)
    assert formatted_postcode == expected_output


@pytest.mark.parametrize("input_postcode, expected_output",
                         [("A20EB", "A2 0EB"),
                          ("A300EB", "A30 0EB"),
                          ("NW120EB", "NW12 0EB")])
def test_postcode_with_spaces_does_add_space(input_postcode, expected_output):
    output = postcode_with_spaces(input_postcode)
    assert output == expected_output


@pytest.mark.parametrize("input_postcode, expected_output",
                         [("aa1 1AA", "AA1 1AA"),
                          ("aa11AA ", "AA1 1AA")])
def test_postcode_with_spaces_does_format_as_uppercase(input_postcode, expected_output):
    output = postcode_with_spaces(input_postcode)
    assert output == expected_output


@pytest.mark.parametrize("input_postcode, expected_output",
                         [(" AA11AA", "AA1 1AA"),
                          ("AA11AA ", "AA1 1AA"),
                          ("AA1  1AA", "AA1 1AA")])
def test_postcode_with_spaces_does_ignore_spaces(input_postcode, expected_output):
    output = postcode_with_spaces(input_postcode)
    assert output == expected_output


def test_postcode_with_spaces_handles_short_postcodes():
    output = postcode_with_spaces('A')
    assert output == ''

    output = postcode_with_spaces('AB')
    assert output == ''


def test_postcode_with_spaces_handles_none():
    output = postcode_with_spaces(None)
    assert output == ''
