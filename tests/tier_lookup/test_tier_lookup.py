from freezegun import freeze_time

from vulnerable_people_form.tier_lookup.lacode_tier_loookup import DEFAULT_NATIONAL_ALERT_LEVEL


def test_return_tier_when_there_is_only_one_historical_restriction(local_tier_lookup):
    assert local_tier_lookup.lacode_to_tier("E08000011") == 3


def test_return_latest_tier_when_there_are_many_historical_restriction(local_tier_lookup):
    assert local_tier_lookup.lacode_to_tier("E08000001") == 3


def test_return_current_tier_when_in_gmt(local_tier_lookup):
    with freeze_time('2020-10-30 00:01:00'):
        assert local_tier_lookup.lacode_to_tier("E06000018") == 1

    with freeze_time('2020-10-30 00:01:01'):
        assert local_tier_lookup.lacode_to_tier("E06000018") == 2


def test_return_current_tier_when_in_bst(local_tier_lookup):
    with freeze_time('2020-05-29 23:01:00'):
        assert local_tier_lookup.lacode_to_tier("E06000018") == DEFAULT_NATIONAL_ALERT_LEVEL

    with freeze_time('2020-05-29 23:01:01'):
        assert local_tier_lookup.lacode_to_tier("E06000018") == 1


def test_return_current_tier_when_the_clocks_change(local_tier_lookup):
    with freeze_time('2020-03-29 00:01:00'):
        assert local_tier_lookup.lacode_to_tier("E08000015") == DEFAULT_NATIONAL_ALERT_LEVEL

    with freeze_time('2020-03-29 00:01:01'):
        assert local_tier_lookup.lacode_to_tier("E08000015") == 1

    with freeze_time('2020-10-24 23:01:00'):
        assert local_tier_lookup.lacode_to_tier("E08000015") == 1

    with freeze_time('2020-10-24 23:01:01'):
        assert local_tier_lookup.lacode_to_tier("E08000015") == 2


@freeze_time('2020-10-13')
def test_return_current_tier_when_there_are_future_restrictions(local_tier_lookup):
    assert local_tier_lookup.lacode_to_tier("E08000018") == 2


def test_return_default_national_tier_when_there_are_no_specific_restrictions(local_tier_lookup):
    assert local_tier_lookup.lacode_to_tier("E99999999") == DEFAULT_NATIONAL_ALERT_LEVEL


def test_return_current_tier_when_yaml_restrictions_are_unordered(local_tier_lookup):
    with freeze_time('2020-06-21'):
        assert local_tier_lookup.lacode_to_tier("E08000012") == DEFAULT_NATIONAL_ALERT_LEVEL
    with freeze_time('2020-07-21'):
        assert local_tier_lookup.lacode_to_tier("E08000012") == 1
    with freeze_time('2020-08-25'):
        assert local_tier_lookup.lacode_to_tier("E08000012") == 2
    with freeze_time('2020-09-25'):
        assert local_tier_lookup.lacode_to_tier("E08000012") == 3
    with freeze_time('2020-10-25'):
        assert local_tier_lookup.lacode_to_tier("E08000012") == 4
    with freeze_time('2020-11-25'):
        assert local_tier_lookup.lacode_to_tier("E08000012") == 4
