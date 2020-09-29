import pytest

from lib.fake_os_places_api_entry import fake_os_places_api_entry as _fake_os_places_api_entry
from lib.fake_os_places_api_response import FakeOSPlacesAPIResponse


@pytest.fixture(scope='session', autouse=True)
def faker_session_locale():
    return ['en_GB']


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
