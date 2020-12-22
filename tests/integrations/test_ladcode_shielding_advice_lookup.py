def test_get_shielding_advice_from_ladcode_returns_correct_value_if_available(local_tier_lookup):
    shielding_list = local_tier_lookup()
    assert shielding_list.get_shielding_advice_by_ladcode("E08000012") == 'YES'


def test_get_shielding_advice_from_ladcode_returns_default_value_if_not_available(local_tier_lookup):
    shielding_list = local_tier_lookup()
    assert shielding_list.get_shielding_advice_by_ladcode("NOTAVAILABLE001") == 'NO'


def test_get_shielding_advice_from_ladcode_returns_latest_value_if_multiple_rows_available(local_tier_lookup):
    shielding_list = local_tier_lookup()
    assert shielding_list.get_shielding_advice_by_ladcode("E06000002") == 'NO'
    assert shielding_list.get_shielding_advice_by_ladcode("E06000003") == 'YES'


def test_get_shielding_advice_from_ladcode_returns_latest_value_and_ignore_future_values(local_tier_lookup):
    shielding_list = local_tier_lookup()
    assert shielding_list.get_shielding_advice_by_ladcode("E06000018") == 'YES'
    assert shielding_list.get_shielding_advice_by_ladcode("E0800021") == 'NO'
