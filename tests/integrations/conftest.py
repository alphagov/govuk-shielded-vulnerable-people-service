import pytest

from lib.fake_os_places_api_entry import fake_os_places_api_entry as _fake_os_places_api_entry
from lib.fake_os_places_api_response import FakeOSPlacesAPIResponse

from vulnerable_people_form.integrations import ladcode_tier_lookup


@pytest.fixture()
def fake_os_places_api_entry(faker):
    return _fake_os_places_api_entry(faker)


@pytest.fixture()
def fake_os_places_api_response(faker):
    def func(
            postcode=None,
            entries=None,
    ):
        return FakeOSPlacesAPIResponse(
            postcode=postcode or faker.postcode(),
            address_entries=entries,
        )

    return func


@pytest.fixture(scope='session', autouse=True)
def local_tier_lookup():
    ladcode_tier_lookup.init(restrictions_yaml_file='tests/integrations/data/local-restrictions.yaml')
