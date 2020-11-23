from unittest.mock import patch

from vulnerable_people_form.form_pages.shared.constants import PostcodeTier
from vulnerable_people_form.form_pages.shared.postcode_tier import (
    update_postcode_tier,
    is_tiering_logic_enabled
)

from flask import Flask

_current_app = Flask(__name__)
_current_app.secret_key = 'test_secret'
_current_app.config["TIERING_LOGIC"] = False


def test_update_postcode_tier_should_not_update_when_tiering_logic_disabled():
    with patch("vulnerable_people_form.form_pages.shared.postcode_tier.get_postcode_tier") as mock_get_postcode_tier, \
         patch("vulnerable_people_form.form_pages.shared.postcode_tier.set_postcode_tier") as mock_set_postcode_tier:
        update_postcode_tier("LS11BA", _current_app)
        mock_get_postcode_tier.assert_not_called()
        mock_set_postcode_tier.assert_not_called()


def test_update_postcode_tier_should_update_session_when_tiering_logic_enabled():
    try:
        postcode = "LS11BA"
        postcode_tier = PostcodeTier.MEDIUM.value
        _current_app.config["TIERING_LOGIC"] = "True"
        with patch("vulnerable_people_form.form_pages.shared.postcode_tier.get_postcode_tier",
                   return_value=postcode_tier) as mock_get_postcode_tier, \
            patch("vulnerable_people_form.form_pages.shared.postcode_tier.set_postcode_tier") \
                as mock_set_postcode_tier:
            update_postcode_tier(postcode, _current_app)
            mock_get_postcode_tier.assert_called_once_with(postcode)
            mock_set_postcode_tier.assert_called_once_with(postcode_tier)
    finally:
        _current_app.config["TIERING_LOGIC"] = "False"


def test_is_tiering_logic_enabled_should_return_false_when_disabled():
    assert is_tiering_logic_enabled(_current_app) is False


def test_is_tiering_logic_enabled_should_return_true_when_enabled():
    try:
        _current_app.config["TIERING_LOGIC"] = "True"
        assert is_tiering_logic_enabled(_current_app) is True
    finally:
        _current_app.config["TIERING_LOGIC"] = "False"
