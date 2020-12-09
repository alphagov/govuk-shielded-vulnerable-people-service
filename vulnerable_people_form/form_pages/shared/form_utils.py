from stdnum.gb.nhs import clean
import re


def clean_nhs_number(nhs_number):
    if nhs_number:
        return clean(nhs_number, '- ')  # remove spaces & hyphens

    return None


def strip_non_digits(value):
    if value:
        return re.sub("[^0-9]", "", value)

    return value


def sanitise_date(date_value):
    if date_value:
        if len(date_value.keys()) != 3 or \
          not all(k in date_value for k in ["day", "month", "year"]):
            raise ValueError(f"Unexpected date_value encountered: {date_value}")

        for k in date_value.keys():
            date_value[k] = strip_non_digits(date_value[k])


def sanitise_name(name_value):
    if name_value:
        if len(name_value.keys()) != 3 or \
          not all(k in name_value for k in ["first_name", "middle_name", "last_name"]):
            raise ValueError(f"Unexpected name value encountered: {name_value}")

        return _strip_whitespace_from_dict_values(name_value)

    return name_value


def sanitise_support_address(support_address):
    if support_address:
        if len(support_address.keys()) != 4 or \
           not all(k in support_address for k in [
               "building_and_street_line_1",
               "building_and_street_line_2",
               "town_city",
               "postcode"]):
            raise ValueError(f"Unexpected support_address value encountered: {support_address}")
        return _strip_whitespace_from_dict_values(support_address)

    return support_address


def format_postcode(postcode):
    if postcode:
        return postcode.replace(" ", "").upper()

    return None


def postcode_with_spaces(postcode):
    if postcode is None or len(postcode) < 3:
        return postcode

    formatted = format_postcode(postcode)
    return f'{formatted[0:-3]} {formatted[-3:]}'


def _strip_whitespace_from_dict_values(input_dict):
    return {k: v.strip() for k, v in input_dict.items()}
