import json
import logging
from http import HTTPStatus

import requests
from flask import current_app

from vulnerable_people_form.form_pages.shared.form_utils import postcode_with_spaces
from vulnerable_people_form.form_pages.shared.logger_utils import init_logger, create_log_message, log_event_names

logger = logging.getLogger(__name__)
init_logger(logger)
_ONS_URL_PATH = "/places/v1/addresses/postcode"


class NoAddressesFoundAtPostcode(RuntimeError):
    pass


class PostcodeNotFound(RuntimeError):
    pass


class ErrorFindingAddress(RuntimeError):
    pass


def address_builder(lpi_info):
    primary_property_identifier = property_identifier(start_number=lpi_info.get('PAO_START_NUMBER'),
                                                      start_suffix=lpi_info.get('PAO_START_SUFFIX'),
                                                      end_number=lpi_info.get('PAO_END_NUMBER'),
                                                      end_suffix=lpi_info.get('PAO_END_SUFFIX'),
                                                      text_value=lpi_info.get('PAO_TEXT'))
    primary_property_identifier_is_a_building = True if lpi_info.get('PAO_TEXT') else False

    secondary_property_identifier = property_identifier(start_number=lpi_info.get('SAO_START_NUMBER'),
                                                        start_suffix=lpi_info.get('SAO_START_SUFFIX'),
                                                        end_number=lpi_info.get('SAO_END_NUMBER'),
                                                        end_suffix=lpi_info.get('SAO_END_SUFFIX'),
                                                        text_value=lpi_info.get('SAO_TEXT'))

    street = lpi_info.get("STREET_DESCRIPTION", "")
    organisation = lpi_info.get("ORGANISATION", "")

    building_and_street_line_1, building_and_street_line_2 = build_building_and_street_lines(
        primary_property_identifier, primary_property_identifier_is_a_building, secondary_property_identifier, street)

    if organisation:
        building_and_street_line_1, building_and_street_line_2 = include_organisation_name(building_and_street_line_1,
                                                                                           building_and_street_line_2,
                                                                                           organisation)

    return {
        "uprn": int(lpi_info.get("UPRN")) if lpi_info.get("UPRN") else None,
        "town_city": town_city_builder(lpi_info).title(),
        "postcode": lpi_info.get("POSTCODE_LOCATOR"),
        "building_and_street_line_1": building_and_street_line_1.title(),
        "building_and_street_line_2": building_and_street_line_2.title(),
    }


def town_city_builder(lpi_info):
    locality = lpi_info.get('LOCALITY_NAME')
    town = lpi_info.get('TOWN_NAME')
    administrative_area = lpi_info.get('ADMINISTRATIVE_AREA')

    non_null_sections = [item for item in [locality, town, administrative_area] if item]

    unique_sections = unique_values_preserving_order(non_null_sections)

    return ', '.join(unique_sections)


def unique_values_preserving_order(sections):
    unique_sections = []
    for section in sections:
        if section not in unique_sections:
            unique_sections.append(section)
    return unique_sections


def property_identifier(start_number, start_suffix, end_number, end_suffix, text_value):
    def number_suffix(a, b):
        return f'{a}{b}' if b else f'{a}'

    if text_value:
        number_identifier = property_identifier(start_number, start_suffix, end_number, end_suffix, None)
        return f'{text_value}, {number_identifier}' if number_identifier else text_value
    elif end_number:
        return f'{number_suffix(start_number, start_suffix)}-{number_suffix(end_number, end_suffix)}'
    elif start_number:
        return number_suffix(start_number, start_suffix)
    else:
        return None


def build_building_and_street_lines(primary_property_identifier, primary_property_identifier_is_a_building,
                                    secondary_property_identifier, street):
    if secondary_property_identifier:
        building_and_street_line_1 = secondary_property_identifier + ', ' + primary_property_identifier
        building_and_street_line_2 = street
    elif primary_property_identifier_is_a_building:
        building_and_street_line_1 = primary_property_identifier
        building_and_street_line_2 = street
    else:
        building_and_street_line_1 = primary_property_identifier + " " + street
        building_and_street_line_2 = ''
    return building_and_street_line_1, building_and_street_line_2


def include_organisation_name(building_and_street_line_1, building_and_street_line_2, organisation):
    if building_and_street_line_2 == '':
        building_and_street_line_2 = building_and_street_line_1
        building_and_street_line_1 = organisation
    else:
        option_1 = organisation + ', ' + building_and_street_line_1
        option_2 = building_and_street_line_1 + ', ' + building_and_street_line_2
        if len(option_1) <= len(option_2):
            building_and_street_line_1 = option_1
        else:
            building_and_street_line_1 = organisation
            building_and_street_line_2 = option_2
    return building_and_street_line_1, building_and_street_line_2


def entry_is_a_postal_address(result):
    """
    The LPI dataset includes entries for address assets that cannot receive post
    such as car parks and streets. These should not appear in the address
    picker. Such entries have a POSTAL_ADDRESS_CODE of 'N'. Return boolean true
    if an entry is a "real" postable address.
    """
    return result['LPI']['POSTAL_ADDRESS_CODE'] != 'N'


def get_addresses_from_postcode(postcode):
    url = "https://api.ordnancesurvey.co.uk" + _ONS_URL_PATH
    if "OVERRIDE_ONS_URL" in current_app.config:
        url = current_app.config["OVERRIDE_ONS_URL"] + _ONS_URL_PATH
    params = {
        "postcode": postcode,
        "key": current_app.config.get("ORDNANCE_SURVEY_PLACES_API_KEY"),
        "dataset": "LPI",
    }
    response = requests.get(url, params=params)
    if response.status_code == HTTPStatus.OK.value:
        response_json = response.json()
        if response_json["header"]["totalresults"] == 0:
            logger.info(create_log_message(log_event_names["ORDNANCE_SURVEY_LOOKUP_NO_ADDRESSES_RETURNED"],
                                           f"Postcode: {postcode}"))
            raise NoAddressesFoundAtPostcode()
        else:
            logger.info(create_log_message(log_event_names["ORDNANCE_SURVEY_LOOKUP_SUCCESS"], f"Postcode: {postcode}"))
            values = []
            for result in response_json["results"]:
                if entry_is_a_postal_address(result):
                    values.append(
                        {
                            "text": _address_with_spaces_in_postcode(result["LPI"]["ADDRESS"], postcode),
                            "value": json.dumps(address_builder(result["LPI"])),
                        }
                    )
            return values
    elif response.status_code == HTTPStatus.UNAUTHORIZED.value:
        logger.error(_create_postcode_lookup_failure_log_message(
            "Unauthorised request submitted to API - Invalid ORDNANCE_SURVEY_PLACES_API_KEY", postcode,
            response.status_code, response.text))
        raise ErrorFindingAddress()
    elif response.status_code == HTTPStatus.BAD_REQUEST.value:
        logger.warning(_create_postcode_lookup_failure_log_message("Invalid request submitted to API", postcode,
                                                                   response.status_code, response.text))
        raise PostcodeNotFound()
    else:
        logger.error(_create_postcode_lookup_failure_log_message("Error finding address", postcode,
                                                                 response.status_code, response.text))
        raise ErrorFindingAddress()


def _address_with_spaces_in_postcode(address, postcode):
    spaced_postcode = postcode_with_spaces(postcode)
    return address.replace(postcode, spaced_postcode)


def _create_postcode_lookup_failure_log_message(failure_reason, postcode, response_code, response_body):
    response_body_to_log = response_body if response_body else "response body empty"
    return create_log_message(log_event_names["ORDNANCE_SURVEY_LOOKUP_FAILURE"],
                              f"Failure reason: {failure_reason}, Postcode: {postcode}, API response - {response_code}: {response_body_to_log}")  # noqa
