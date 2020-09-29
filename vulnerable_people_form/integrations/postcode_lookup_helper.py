import json
import logging
from http import HTTPStatus

import requests
import sentry_sdk
from flask import current_app

from vulnerable_people_form.form_pages.shared.logger_utils import init_logger, create_log_message, log_event_names

logger = logging.getLogger(__name__)
init_logger(logger)


class NoAddressesFoundAtPostcode(RuntimeError):
    pass


class PostcodeNotFound(RuntimeError):
    pass


class ErrorFindingAddress(RuntimeError):
    pass


def address_line_builder(lpi_info, slice):
    return ", ".join({k: v for k, v in lpi_info.items() if k in slice}.values())


def address_builder(lpi_info):
    sao = address_line_builder(
        lpi_info,
        [
            "ORGANISATION",
            "SAO_START_NUMBER",
            "SAO_START_SUFFIX",
            "SAO_END_NUMBER",
            "SAO_END_SUFFIX",
            "SAO_TEXT",
        ],
    )
    pao = address_line_builder(
        lpi_info,
        [
            "PAO_START_NUMBER",
            "PAO_START_SUFFIX",
            "PAO_END_NUMBER",
            "PAO_END_SUFFIX",
            "PAO_TEXT",
        ],
    )

    building_and_street_line_1 = ""
    building_and_street_line_2 = ""
    street = lpi_info.get("STREET_DESCRIPTION", "")

    if sao != "":
        building_and_street_line_1 = sao
        building_and_street_line_2 = pao + " " + street
    elif lpi_info.get("PAO_TEXT"):
        building_and_street_line_1 = pao
        building_and_street_line_2 = street
    else:
        building_and_street_line_1 = pao + " " + street

    return {
        "uprn": int(lpi_info.get("UPRN")),
        "town_city": address_line_builder(lpi_info, ["LOCALITY_NAME", "TOWN_NAME"]).title(),
        "postcode": lpi_info.get("POSTCODE_LOCATOR"),
        "building_and_street_line_1": building_and_street_line_1.title(),
        "building_and_street_line_2": building_and_street_line_2.title(),
    }


def entry_is_a_postal_address(result):
    """
    The LPI dataset includes entries for address assets that cannot receive post
    such as car parks and streets. These should not appear in the address
    picker. Such entries have a POSTAL_ADDRESS_CODE of 'N'. Return boolean true
    if an entry is a "real" postable address.
    """
    return result['LPI']['POSTAL_ADDRESS_CODE'] != 'N'


def get_addresses_from_postcode(postcode):
    url = "https://api.ordnancesurvey.co.uk/places/v1/addresses/postcode"
    params = {
        "postcode": postcode,
        "key": current_app.config.get("ORDNANCE_SURVEY_PLACES_API_KEY"),
        "dataset": "LPI",
    }
    response = requests.get(url, params=params)
    if response.status_code == HTTPStatus.OK.value:
        response_json = response.json()
        if response_json["header"]["totalresults"] == 0:
            raise NoAddressesFoundAtPostcode()
        else:
            logger.info(create_log_message(log_event_names["ORDNANCE_SURVEY_LOOKUP_SUCCESS"], f"Postcode: {postcode}"))
            values = []
            for result in response_json["results"]:
                if entry_is_a_postal_address(result):
                    values.append(
                        {
                            "text": result["LPI"]["ADDRESS"],
                            "value": json.dumps(address_builder(result["LPI"])),
                        }
                    )
            return values
    elif response.status_code == HTTPStatus.UNAUTHORIZED.value:
        _log_postcode_lookup_failure("Unauthorised request submitted to API", postcode)
        sentry_sdk.capture_message("Invalid ORDNANCE_SURVEY_PLACES_API_KEY", "error")
        raise ErrorFindingAddress()
    elif response.status_code == HTTPStatus.BAD_REQUEST.value:
        _log_postcode_lookup_failure("Invalid request submitted to API", postcode)
        sentry_sdk.capture_message("Invalid OS postcode request:" + response.text, "error")
        raise PostcodeNotFound()
    else:
        _log_postcode_lookup_failure("Error finding address", postcode)
        raise ErrorFindingAddress()


def _log_postcode_lookup_failure(failure_reason, postcode):
    logger.error(create_log_message(log_event_names["ORDNANCE_SURVEY_LOOKUP_FAILURE"],
                                    f"Failure reason: {failure_reason}, Postcode: {postcode}"))
