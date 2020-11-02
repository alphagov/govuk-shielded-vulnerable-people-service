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
