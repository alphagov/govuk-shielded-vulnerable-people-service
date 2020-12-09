"""
The mailchecker takes it's original code from https://github.com/dbarlett/pymailcheck/ (MIT License)
These test cases are adapted from it's original unittest versions
"""

import pytest

from vulnerable_people_form.form_pages.shared import mailchecker

DOMAINS = (
    "google.com",
    "gmail.com",
    "emaildomain.com",
    "comcast.net",
    "facebook.com",
    "msn.com",
    "gmx.de",
)

SECOND_LEVEL_DOMAINS = (
    "yahoo",
    "hotmail",
    "mail",
    "live",
    "outlook",
    "gmx",
)

TOP_LEVEL_DOMAINS = (
    "co.uk",
    "com",
    "org",
    "info",
    "fr",
)


def test_sift3_distance():
    assert mailchecker.sift3_distance("boat", "boot") == 1
    assert mailchecker.sift3_distance("boat", "bat") == 1.5
    assert mailchecker.sift3_distance("ifno", "info") == 2
    assert mailchecker.sift3_distance("hotmial", "hotmail") == 2


def test_one_level_domain():
    parts = mailchecker.split_email("postbox@com")
    expected = {
        "address": "postbox",
        "domain": "com",
        "top_level_domain": "com",
        "second_level_domain": "",
    }
    assert parts == expected


def test_two_level_domain():
    parts = mailchecker.split_email("test@example.com")
    expected = {
        "address": "test",
        "domain": "example.com",
        "top_level_domain": "com",
        "second_level_domain": "example",
    }
    assert parts == expected


def test_three_level_domain():
    parts = mailchecker.split_email("test@example.co.uk")
    expected = {
        "address": "test",
        "domain": "example.co.uk",
        "top_level_domain": "co.uk",
        "second_level_domain": "example",
    }
    assert parts == expected


def test_four_level_domain():
    parts = mailchecker.split_email("test@mail.randomsmallcompany.co.uk")
    expected = {
        "address": "test",
        "domain": "mail.randomsmallcompany.co.uk",
        "top_level_domain": "randomsmallcompany.co.uk",
        "second_level_domain": "mail",
    }
    assert parts == expected


def test_rfc_compliant():
    parts = mailchecker.split_email('"foo@bar"@example.com')
    expected = {
        "address": '"foo@bar"',
        "domain": "example.com",
        "top_level_domain": "com",
        "second_level_domain": "example",
    }
    assert parts == expected


def test_contains_numbers():
    parts = mailchecker.split_email("containsnumbers1234567890@example.com")
    expected = {
        "address": "containsnumbers1234567890",
        "domain": "example.com",
        "top_level_domain": "com",
        "second_level_domain": "example",
    }
    assert parts == expected


def test_contains_plus():
    parts = mailchecker.split_email("contains+symbol@example.com")
    expected = {
        "address": "contains+symbol",
        "domain": "example.com",
        "top_level_domain": "com",
        "second_level_domain": "example",
    }
    assert parts == expected


def test_contains_hyphen():
    parts = mailchecker.split_email("contains-symbol@example.com")
    expected = {
        "address": "contains-symbol",
        "domain": "example.com",
        "top_level_domain": "com",
        "second_level_domain": "example",
    }
    assert parts == expected


def test_contains_periods():
    parts = mailchecker.split_email("contains.symbol@domain.contains.symbol")
    expected = {
        "address": "contains.symbol",
        "domain": "domain.contains.symbol",
        "top_level_domain": "contains.symbol",
        "second_level_domain": "domain",
    }
    assert parts == expected


def test_contains_period_backslash():
    parts = mailchecker.split_email('"contains.and\ symbols"@example.com')
    expected = {
        "address": '"contains.and\ symbols"',
        "domain": "example.com",
        "top_level_domain": "com",
        "second_level_domain": "example",
    }

    assert parts == expected


def test_contains_period_at_sign():
    parts = mailchecker.split_email('"contains.and.@.symbols.com"@example.com')
    expected = {
        "address": '"contains.and.@.symbols.com"',
        "domain": "example.com",
        "top_level_domain": "com",
        "second_level_domain": "example",
    }

    assert parts == expected


def test_contains_all_symbols():
    parts = mailchecker.split_email(
        '"()<>[]:;@,\\\"!#$%&\'*+-/=?^_`{}|\ \ \ \ \ ~\ \ \ \ \ \ \ ?\ \ \ \ \ \ \ \ \ \ \ \ ^_`{}|~.a"@allthesymbols.com')
    expected = {
        "address": '"()<>[]:;@,\\\"!#$%&\'*+-/=?^_`{}|\ \ \ \ \ ~\ \ \ \ \ \ \ ?\ \ \ \ \ \ \ \ \ \ \ \ ^_`{}|~.a"',
        "domain": "allthesymbols.com",
        "top_level_domain": "com",
        "second_level_domain": "allthesymbols",
    }

    assert parts == expected


def test_not_rfc_compliant():
    assert mailchecker.split_email("example.com") is False
    assert mailchecker.split_email("abc.example.com") is False
    assert mailchecker.split_email("@example.com") is False
    assert mailchecker.split_email("test@") is False


def test_trim_spaces():
    parts = mailchecker.split_email(" postbox@com")
    expected = {
        "address": "postbox",
        "domain": "com",
        "top_level_domain": "com",
        "second_level_domain": "",
    }

    assert parts == expected
    parts = mailchecker.split_email("postbox@com ")

    assert parts == expected


def test_most_similar_domain():
    assert mailchecker.find_closest_domain("google.com", DOMAINS) == "google.com"
    assert mailchecker.find_closest_domain("gmail.com", DOMAINS) == "gmail.com"
    assert mailchecker.find_closest_domain("emaildomain.com", DOMAINS) == "emaildomain.com"
    assert mailchecker.find_closest_domain("gmsn.com", DOMAINS) == "msn.com"
    assert mailchecker.find_closest_domain("gmaik.com", DOMAINS) == "gmail.com"


def test_most_similar_second_level_domain():
    assert mailchecker.find_closest_domain("hotmial", SECOND_LEVEL_DOMAINS) == "hotmail"
    assert mailchecker.find_closest_domain("tahoo", SECOND_LEVEL_DOMAINS) == "yahoo"
    assert mailchecker.find_closest_domain("livr", SECOND_LEVEL_DOMAINS) == "live"
    assert mailchecker.find_closest_domain("outllok", SECOND_LEVEL_DOMAINS) == "outlook"


def test_most_similar_top_level_domain():
    assert mailchecker.find_closest_domain("cmo", TOP_LEVEL_DOMAINS) == "com"
    assert mailchecker.find_closest_domain("ogr", TOP_LEVEL_DOMAINS) == "org"
    assert mailchecker.find_closest_domain("ifno", TOP_LEVEL_DOMAINS) == "info"
    assert mailchecker.find_closest_domain("com.uk", TOP_LEVEL_DOMAINS) == "co.uk"


def test_returns_array():
    expected = {
        "address": "test",
        "domain": "gmail.com",
        "full": "test@gmail.com",
    }
    assert mailchecker.suggest("test@gmail.co", DOMAINS) == expected


def test_no_suggestion_returns_false():
        assert mailchecker.suggest("contact@kicksend.com", DOMAINS) is False


def test_incomplete_email_returns_false():
        assert mailchecker.suggest("", DOMAINS) is False
        assert mailchecker.suggest("test@", DOMAINS) is False
        assert mailchecker.suggest("test", DOMAINS) is False


def test_returns_valid_suggestions():
    assert mailchecker.suggest("test@gmailc.om", DOMAINS)["domain"] == "gmail.com"
    assert mailchecker.suggest("test@emaildomain.co", DOMAINS)["domain"] == "emaildomain.com"
    assert mailchecker.suggest("test@gmail.con", DOMAINS)["domain"] == "gmail.com"
    assert mailchecker.suggest("test@gnail.con", DOMAINS)["domain"] == "gmail.com"
    assert mailchecker.suggest("test@GNAIL.con", DOMAINS)["domain"] == "gmail.com"
    assert mailchecker.suggest("test@#gmail.com", DOMAINS)["domain"] == "gmail.com"
    assert mailchecker.suggest("test@comcast.nry", DOMAINS)["domain"] == "comcast.net"
    assert mailchecker.suggest(
            "test@homail.con",
            DOMAINS,
            SECOND_LEVEL_DOMAINS,
            TOP_LEVEL_DOMAINS
        )["domain"] == "hotmail.com"
    assert mailchecker.suggest(
            "test@hotmail.co",
            DOMAINS,
            SECOND_LEVEL_DOMAINS,
            TOP_LEVEL_DOMAINS
        )["domain"] == "hotmail.com"
    assert mailchecker.suggest(
            "test@yajoo.com",
            DOMAINS,
            SECOND_LEVEL_DOMAINS,
            TOP_LEVEL_DOMAINS
        )["domain"] == "yahoo.com"
    assert mailchecker.suggest(
            "test@randomsmallcompany.cmo",
            DOMAINS,
            SECOND_LEVEL_DOMAINS,
            TOP_LEVEL_DOMAINS
        )["domain"] == "randomsmallcompany.com"


def test_idempotent_suggestions():
    assert mailchecker.suggest(
            "test@yahooo.cmo",
            DOMAINS,
            SECOND_LEVEL_DOMAINS,
            TOP_LEVEL_DOMAINS
        )["domain"] == "yahoo.com"


def test_no_suggestions_valid_2ld_tld():
    assert mailchecker.suggest(
            "test@yahoo.co.uk",
            DOMAINS,
            SECOND_LEVEL_DOMAINS,
            TOP_LEVEL_DOMAINS
        ) is False


def test_no_suggestions_valid_2ld_tld_close_domain():
    assert mailchecker.suggest(
            "test@gmx.fr",
            DOMAINS,
            SECOND_LEVEL_DOMAINS,
            TOP_LEVEL_DOMAINS
        ) is False
