import pytest

from vulnerable_people_form.tier_lookup.lacode_tier_loookup import LacodeTierLookup


@pytest.fixture()
def local_tier_lookup():
    return LacodeTierLookup(restrictions_yaml_file='tests/tier_lookup/data/local-restrictions.yaml')
