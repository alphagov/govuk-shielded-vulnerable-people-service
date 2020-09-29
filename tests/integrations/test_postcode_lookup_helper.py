import pytest
import requests
import json
from unittest import mock
from flask import Flask

from vulnerable_people_form.integrations.postcode_lookup_helper import \
        entry_is_a_postal_address, \
        get_addresses_from_postcode, \
        PostcodeNotFound, ErrorFindingAddress

_current_app = Flask(__name__)


def test_entry_is_a_postal_address_function(fake_os_places_api_entry):
    postable_entry = fake_os_places_api_entry(postal_address_code='D')
    non_postable_entry = fake_os_places_api_entry(postal_address_code='N')

    assert entry_is_a_postal_address(postable_entry.to_json()) is True
    assert entry_is_a_postal_address(non_postable_entry.to_json()) is False


@mock.patch('requests.get')
def test_get_addresses_from_postcode(mock_get, faker, fake_os_places_api_entry, fake_os_places_api_response):
    postcode = faker.postcode()

    entries = []
    # GIVEN 5 postable address entries for a postcode
    for _ in range(0, 5):
        entries.append(fake_os_places_api_entry(postcode=postcode, postal_address_code='D'))
    # and one non-postable entry.
    non_postable_entry = fake_os_places_api_entry(postcode=postcode, postal_address_code='N')

    fake_api_response = fake_os_places_api_response(
        postcode=postcode,
        entries=[*entries, non_postable_entry],
    )
    mock_get.return_value = create_response_object(200, fake_api_response.to_json())

    # WHEN we call the get_addresses_from_postcode function
    with _current_app.test_request_context():
        addresses = get_addresses_from_postcode(fake_api_response.postcode)

        # THEN we get 5 postable address entries back with the details we expect.
        assert len(addresses) == 5
        api_response_and_function_result_should_match(entries, addresses)


@mock.patch('requests.get')
def test_get_addresses_from_postcode_handles_400_status_code(mock_get, faker):
    postcode = faker.postcode()
    mock_get.return_value = create_response_object(400, '')
    with pytest.raises(PostcodeNotFound):
        with _current_app.test_request_context():
            get_addresses_from_postcode(postcode)


@mock.patch('requests.get')
def test_get_addresses_from_postcode_handles_401_status_code(mock_get, faker):
    postcode = faker.postcode()
    mock_get.return_value = create_response_object(401, '')
    with pytest.raises(ErrorFindingAddress):
        with _current_app.test_request_context():
            get_addresses_from_postcode(postcode)


@mock.patch('requests.get')
def test_get_addresses_from_postcode_handles_500_status_code(mock_get, faker):
    postcode = faker.postcode()
    mock_get.return_value = create_response_object(500, '')
    with pytest.raises(ErrorFindingAddress):
        with _current_app.test_request_context():
            get_addresses_from_postcode(postcode)


def api_response_and_function_result_should_match(expected_entries, addresses):
    assert len(expected_entries) == len(addresses)
    for i in range(0, len(expected_entries)):
        api_response_entry_json = json.loads(json.dumps(expected_entries[i].to_json()))
        assert addresses[i]['text'] == api_response_entry_json['LPI']['ADDRESS']
        values = json.loads(addresses[i]['value'])
        assert values['uprn'] == expected_entries[i].uprn
        assert values['town_city'] == expected_entries[i].city.title()
        assert values['postcode'] == expected_entries[i].postcode
        assert values['building_and_street_line_1'] == '{door_number} {street}'.format(
            door_number=expected_entries[i].door_number,
            street=expected_entries[i].street,
        ).title()
        assert values['building_and_street_line_2'] == ''


def create_response_object(status_code, json_body):
    r = requests.Response()
    r.status_code = status_code

    def json_func():
        return json_body

    r.json = json_func
    return r
