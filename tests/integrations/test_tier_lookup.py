from freezegun import freeze_time

from vulnerable_people_form.integrations.ladcode_tier_lookup import DEFAULT_NATIONAL_ALERT_LEVEL, get_tier_by_ladcode


def test_return_tier_when_there_is_only_one_historical_restriction():
    assert get_tier_by_ladcode("E08000011") == 3


def test_return_latest_tier_when_there_are_many_historical_restriction():
    assert get_tier_by_ladcode("E08000001") == 3


def test_return_current_tier_when_in_gmt():
    with freeze_time('2020-10-30 00:01:00'):
        assert get_tier_by_ladcode("E06000018") == 1

    with freeze_time('2020-10-30 00:01:01'):
        assert get_tier_by_ladcode("E06000018") == 2


def test_return_current_tier_when_in_bst():
    with freeze_time('2020-05-29 23:01:00'):
        assert get_tier_by_ladcode("E06000018") == DEFAULT_NATIONAL_ALERT_LEVEL

    with freeze_time('2020-05-29 23:01:01'):
        assert get_tier_by_ladcode("E06000018") == 1


def test_return_current_tier_when_the_clocks_change():
    with freeze_time('2020-03-29 00:01:00'):
        assert get_tier_by_ladcode("E08000015") == DEFAULT_NATIONAL_ALERT_LEVEL

    with freeze_time('2020-03-29 00:01:01'):
        assert get_tier_by_ladcode("E08000015") == 1

    with freeze_time('2020-10-24 23:01:00'):
        assert get_tier_by_ladcode("E08000015") == 1

    with freeze_time('2020-10-24 23:01:01'):
        assert get_tier_by_ladcode("E08000015") == 2


@freeze_time('2020-10-13')
def test_return_current_tier_when_there_are_future_restrictions():
    assert get_tier_by_ladcode("E08000018") == 2


def test_return_default_national_tier_when_there_are_no_specific_restrictions():
    assert get_tier_by_ladcode("E99999999") == DEFAULT_NATIONAL_ALERT_LEVEL


def test_return_current_tier_when_yaml_restrictions_are_unordered():
    with freeze_time('2020-06-21'):
        assert get_tier_by_ladcode("E08000012") == DEFAULT_NATIONAL_ALERT_LEVEL
    with freeze_time('2020-07-21'):
        assert get_tier_by_ladcode("E08000012") == 1
    with freeze_time('2020-08-25'):
        assert get_tier_by_ladcode("E08000012") == 2
    with freeze_time('2020-09-25'):
        assert get_tier_by_ladcode("E08000012") == 3
    with freeze_time('2020-10-25'):
        assert get_tier_by_ladcode("E08000012") == 4
    with freeze_time('2020-11-25'):
        assert get_tier_by_ladcode("E08000012") == 4
