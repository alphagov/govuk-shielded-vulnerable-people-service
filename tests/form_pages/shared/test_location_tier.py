from unittest.mock import patch, Mock
from flask import Flask
import pytest

from vulnerable_people_form.form_pages.shared.constants import PostcodeTier, PostcodeTierStatus
from vulnerable_people_form.form_pages.shared.answers_enums import YesNoAnswers
from vulnerable_people_form.form_pages.shared.location_tier import (
    update_location_tier_by_postcode,
    update_location_tier_by_uprn,
    is_tier_very_high_or_above,
    is_tier_less_than_very_high,
    get_latest_location_tier
)

_current_app = Flask(__name__)
_current_app.secret_key = 'test_secret'
_current_app.is_tiering_logic_enabled = False
_current_app.config["POSTCODE_TIER_OVERRIDE"] = {"TE22RR": 2, "TE33RR": 3, "TE44RR": 4}


def test_update_location_tier_by_uprn_should_not_update_when_tiering_logic_disabled():
    with patch("vulnerable_people_form.form_pages.shared.location_tier.get_postcode_tier") as mock_get_postcode_tier, \
         patch("vulnerable_people_form.form_pages.shared.location_tier.set_location_tier") as mock_set_location_tier:
        update_location_tier_by_uprn(19999, _current_app)
        mock_get_postcode_tier.assert_not_called()
        mock_set_location_tier.assert_called_once_with(PostcodeTier.VERY_HIGH_PLUS_SHIELDING.value)


def test_update_location_tier_by_uprn_should_update_session_when_tiering_logic_enabled():
    try:
        uprn = 110000
        la = "E06000008"
        location_tier = PostcodeTier.MEDIUM.value
        shielding_advice = YesNoAnswers.YES.value
        _current_app.is_tiering_logic_enabled = True
        _current_app.shielding_advice = Mock()
        _current_app.shielding_advice.is_la_shielding = lambda ladcode: shielding_advice
        with _current_app.app_context(), \
             _current_app.test_request_context("/test?irrelevant=1&la=3") as test_request_context, \
             patch("vulnerable_people_form.form_pages.shared.location_tier.get_uprn_tier",
                   return_value=location_tier) as mock_get_location_tier, \
             patch("vulnerable_people_form.form_pages.shared.location_tier.get_ladcode_from_uprn",
                   return_value=la) as mock_get_ladcode_from_uprn, \
             patch("vulnerable_people_form.form_pages.shared.location_tier.set_location_tier") \
                as mock_set_location_tier,  \
             patch("vulnerable_people_form.form_pages.shared.location_tier.set_shielding_advice") \
                as mock_set_shielding_advice:
            test_request_context.session["form_answers"] = {"support_address": {"postcode": ""}}
            update_location_tier_by_uprn(uprn, _current_app)
            mock_get_ladcode_from_uprn.assert_called_once()
            mock_get_location_tier.assert_called_once_with(uprn)
            mock_set_location_tier.assert_called_once_with(location_tier)
            mock_set_shielding_advice.assert_called_once_with(shielding_advice)
    finally:
        _current_app.is_tiering_logic_enabled = False


def test_update_location_tier_by_postcode_should_not_update_when_tiering_logic_disabled():
    with patch("vulnerable_people_form.form_pages.shared.location_tier.get_postcode_tier") as mock_get_postcode_tier, \
         patch("vulnerable_people_form.form_pages.shared.location_tier.set_location_tier") as mock_set_location_tier:
        update_location_tier_by_postcode("LS11BA", _current_app)
        mock_get_postcode_tier.assert_not_called()
        mock_set_location_tier.assert_called_once_with(PostcodeTier.VERY_HIGH_PLUS_SHIELDING.value)


def test_update_location_tier_by_postcode_should_update_session_when_tiering_logic_enabled():
    try:
        postcode = "LS11BA"
        la = "E06000008"
        location_tier = PostcodeTier.MEDIUM.value
        shielding_advice = YesNoAnswers.YES.value
        _current_app.is_tiering_logic_enabled = True
        _current_app.shielding_advice = Mock()
        _current_app.shielding_advice.is_la_shielding = lambda ladcode: shielding_advice
        with _current_app.app_context(), \
             patch("vulnerable_people_form.form_pages.shared.location_tier.get_postcode_tier",
                   return_value=location_tier) as mock_get_location_tier, \
             patch("vulnerable_people_form.form_pages.shared.location_tier.get_ladcode_from_postcode",
                   return_value=la) as mock_get_ladcode_from_postcode, \
             patch("vulnerable_people_form.form_pages.shared.location_tier.set_location_tier") \
                as mock_set_location_tier, \
             patch("vulnerable_people_form.form_pages.shared.location_tier.set_shielding_advice") \
                as mock_set_shielding_advice:

            update_location_tier_by_postcode(postcode, _current_app)
            mock_get_ladcode_from_postcode.assert_called_once()
            mock_get_location_tier.assert_called_once_with(postcode)
            mock_set_location_tier.assert_called_once_with(location_tier)
            mock_set_shielding_advice.assert_called_once_with(shielding_advice)
    finally:
        _current_app.is_tiering_logic_enabled = False


@pytest.mark.parametrize("location_tier, expected_output",
                         [(None, False),
                          (PostcodeTier.MEDIUM.value, False),
                          (PostcodeTier.HIGH.value, False),
                          (PostcodeTier.VERY_HIGH.value, True),
                          (PostcodeTier.VERY_HIGH_PLUS_SHIELDING.value, True)])
def test_is_tier_very_high_or_above_should_return_expected_value(location_tier, expected_output):
    assert is_tier_very_high_or_above(location_tier) == expected_output


@pytest.mark.parametrize("location_tier, expected_output",
                         [(None, False),
                          (PostcodeTier.MEDIUM.value, True),
                          (PostcodeTier.HIGH.value, True),
                          (PostcodeTier.VERY_HIGH.value, False),
                          (PostcodeTier.VERY_HIGH_PLUS_SHIELDING.value, False)])
def test_is_tier_less_than_very_high_should_return_expected_value(location_tier, expected_output):
    assert is_tier_less_than_very_high(location_tier) == expected_output


@pytest.mark.parametrize("original_location_tier, latest_location_tier, expected_change_status",
                         [(PostcodeTier.VERY_HIGH, PostcodeTier.VERY_HIGH_PLUS_SHIELDING, PostcodeTierStatus.INCREASED),
                          (PostcodeTier.VERY_HIGH, PostcodeTier.VERY_HIGH, PostcodeTierStatus.NO_CHANGE),
                          (PostcodeTier.VERY_HIGH, PostcodeTier.HIGH, PostcodeTierStatus.DECREASED),
                          (PostcodeTier.VERY_HIGH, PostcodeTier.MEDIUM, PostcodeTierStatus.DECREASED),
                          (PostcodeTier.VERY_HIGH_PLUS_SHIELDING,
                           PostcodeTier.VERY_HIGH_PLUS_SHIELDING,
                           PostcodeTierStatus.NO_CHANGE),
                          (PostcodeTier.VERY_HIGH_PLUS_SHIELDING, PostcodeTier.VERY_HIGH, PostcodeTierStatus.DECREASED),
                          (PostcodeTier.VERY_HIGH_PLUS_SHIELDING, PostcodeTier.HIGH, PostcodeTierStatus.DECREASED),
                          (PostcodeTier.VERY_HIGH_PLUS_SHIELDING, PostcodeTier.MEDIUM, PostcodeTierStatus.DECREASED)])
def test_get_latest_location_tier_should_return_correct_change_status(
        original_location_tier, latest_location_tier, expected_change_status):
    try:
        _current_app.is_tiering_logic_enabled = True
        with _current_app.app_context():
            latest_location_tier_info = get_latest_location_tier(latest_location_tier.value,
                                                                 original_location_tier.value)
            assert latest_location_tier_info["change_status"] == expected_change_status.value
            assert latest_location_tier_info["latest_location_tier"] == latest_location_tier.value
    finally:
        _current_app.is_tiering_logic_enabled = False


def test_get_latest_location_tier_should_return_none_when_location_tier_cannot_be_determined():
    try:
        _current_app.is_tiering_logic_enabled = True
        with _current_app.app_context():
            latest_location_tier_info = get_latest_location_tier(None, PostcodeTier.VERY_HIGH.value)
            assert latest_location_tier_info is None
    finally:
        _current_app.is_tiering_logic_enabled = False
