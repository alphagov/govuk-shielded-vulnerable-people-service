# NOTIFY CODE

OBSCURE_WHITESPACE = (
    '\u180E'  # Mongolian vowel separator
    '\u200B'  # zero width space
    '\u200C'  # zero width non-joiner
    '\u200D'  # zero width joiner
    '\u2060'  # word joiner
    '\u00A0'  # non breaking space
    '\uFEFF'  # zero width non-breaking space
)

uk_prefix = '44'


class InvalidPhoneError(Exception):

    def __init__(self, message=None):
        super().__init__(message or 'Not a valid phone number')


def validate_uk_phone_number(number):
    number = normalise_phone_number(number).lstrip(uk_prefix).lstrip('0')

    if not number.startswith('7'):
        raise InvalidPhoneError('Not a UK mobile number')

    if len(number) > 10:
        raise InvalidPhoneError('Too many digits')

    if len(number) < 10:
        raise InvalidPhoneError('Not enough digits')

    return '{}{}'.format(uk_prefix, number)


def normalise_phone_number(number):
    import string

    for character in string.whitespace + OBSCURE_WHITESPACE + '()-+':
        number = number.replace(character, '')

    try:
        list(map(int, number))
    except ValueError:
        raise InvalidPhoneError('Must not contain letters or symbols')

    return number.lstrip('0')
