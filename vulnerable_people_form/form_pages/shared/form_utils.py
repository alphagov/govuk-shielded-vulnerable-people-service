from stdnum.gb.nhs import clean


def clean_nhs_number(nhs_number):
    if nhs_number:
        return clean(nhs_number, '- ')  # remove spaces & hyphens

    return None
