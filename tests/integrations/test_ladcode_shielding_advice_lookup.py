from vulnerable_people_form.form_pages.shared.constants import ShieldingAdvice


def test_get_shielding_advice_from_ladcode_returns_correct_value_if_available(local_tier_lookup):
    shielding_list = local_tier_lookup()
    assert shielding_list.advice_from_la_shielding("E08000012") is ShieldingAdvice.ADVISED_TO_SHIELD.value


def test_get_shielding_advice_from_ladcode_returns_default_value_if_not_available(local_tier_lookup):
    shielding_list = local_tier_lookup()
    assert shielding_list.advice_from_la_shielding("NOTAVAILABLE001") is ShieldingAdvice.NOT_ADVISED_TO_SHIELD.value


def test_get_shielding_advice_from_ladcode_returns_latest_value_if_multiple_rows_available(local_tier_lookup):
    shielding_list = local_tier_lookup()
    assert shielding_list.advice_from_la_shielding("E06000002") is ShieldingAdvice.NOT_ADVISED_TO_SHIELD.value
    assert shielding_list.advice_from_la_shielding("E06000003") is ShieldingAdvice.ADVISED_TO_SHIELD.value


def test_get_shielding_advice_from_ladcode_returns_latest_value_and_ignore_future_values(local_tier_lookup):
    shielding_list = local_tier_lookup()
    assert shielding_list.advice_from_la_shielding("E06000018") is ShieldingAdvice.ADVISED_TO_SHIELD.value
    assert shielding_list.advice_from_la_shielding("E0800021") is ShieldingAdvice.NOT_ADVISED_TO_SHIELD.value
