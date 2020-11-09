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
            raise ValueError("Unexpected date_value encountered: " + str(date_value))

        date_value["day"] = strip_non_digits(date_value["day"])
        date_value["month"] = strip_non_digits(date_value["month"])
        date_value["year"] = strip_non_digits(date_value["year"])


def sanitise_name(name_value):
    if name_value:
        if len(name_value.keys()) != 3 or \
          not all(k in name_value for k in ["first_name", "middle_name", "last_name"]):
            raise ValueError("Unexpected name value encountered: " + str(name_value))

        name_value["first_name"] = name_value["first_name"].strip()
        name_value["middle_name"] = name_value["middle_name"].strip()
        name_value["last_name"] = name_value["last_name"].strip()
