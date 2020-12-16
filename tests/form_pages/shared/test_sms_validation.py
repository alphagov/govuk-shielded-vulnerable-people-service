import pytest

from vulnerable_people_form.form_pages.shared.sms_validation import validate_uk_phone_number, InvalidPhoneError

valid_notify_uk_phone_numbers = [
    '7123456789',
    '07123456789',
    '07123 456789',
    '07123-456-789',
    '00447123456789',
    '00 44 7123456789',
    '+447123456789',
    '+44 7123 456 789',
    '+44 (0)7123 456 789',
    '\u200B\t\t+44 (0)7123 \uFEFF 456 789 \r\n',
]

invalid_notify_uk_phone_numbers = [
    '71234567890',  # International numbers
    '1-202-555-0104',
    '+12025550104',
    '0012025550104',
    '+0012025550104',
    '23051234567',
    '+682 12345',
    '+3312345678',
    '003312345678',
    '1-2345-12345-12345',
    '712345678910',  # Too many digits
    '0712345678910',
    '0044712345678910',
    '0044712345678910',
    '+44 ()7123 456 789 10',
    '0712345678',  # Not enough digits
    '004471234567',
    '00447123456',
    '+44 (0)7123 456 78',
    '08081 570364',  # Not a UK mobile number
    '+44 8081 570364',
    '0117 496 0860',
    '+44 117 496 0860',
    '020 7946 0991',
    '+44 20 7946 0991',
    '07890x32109',  # Must not contain letters or symbols
    '07123 456789...',
    '07123 ☟☜⬇⬆☞☝',
    '07123☟☜⬇⬆☞☝',
    '07";DROP TABLE;"',
    '+44 07ab cde fgh',
    'ALPHANUM3R1C',
]


@pytest.mark.parametrize("phone_number", valid_notify_uk_phone_numbers)
def test_phone_number_is_valid_for_notify_returns_true_for_valid_notify_uk_test_cases(phone_number):
    assert validate_uk_phone_number(phone_number)


@pytest.mark.parametrize("phone_number", invalid_notify_uk_phone_numbers)
def test_phone_number_is_valid_for_notify_raises_exception_for_invalid_notify_uk_test_cases(phone_number):
    with pytest.raises(InvalidPhoneError):
        validate_uk_phone_number(phone_number)
