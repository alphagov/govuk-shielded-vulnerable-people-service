import logging
from vulnerable_people_form.form_pages.shared.logger_utils import init_logger, log_event_names, create_log_message
from .persistence import generate_string_parameter, generate_int_parameter, execute_sql

from vulnerable_people_form.form_pages.shared.constants import PostcodeTier, ShieldingAdvice

logger = logging.getLogger(__name__)
init_logger(logger)
_DEFAULT_TIER = 1


def get_shielding_advice_by_uprn(uprn):
    records = execute_sql(
            "CALL cv_ref.is_uprn_advised_to_shield(:uprn)",
            (generate_int_parameter("uprn", uprn),),)["records"]

    if not records:
        logger.info(create_log_message(
            log_event_names["SHIELDING_ADVICE_NOT_FOUND"],
            f"No shielding_advice found in the database for uprn: {uprn}"
        ))
        return records

    if records[0][0]["longValue"] not in list(ShieldingAdvice):
        raise ValueError(f"RDS procedure returned unrecognised value {records}")

    shielding_advice = records[0][0]["longValue"]

    logger.info(create_log_message(log_event_names["UPRN_TO_SHIELDING_ADVICE_SUCCESS"],
                                   f"Successfully retrieved shielding advice: {shielding_advice} for uprn: {uprn}"))
    return shielding_advice


def get_shielding_advice_by_postcode(postcode):
    records = execute_sql(
            "CALL cv_ref.is_postcode_advised_to_shield(:postcode)",
            (generate_string_parameter("postcode", postcode),),)["records"]

    if not records:
        logger.info(create_log_message(
            log_event_names["SHIELDING_ADVICE_NOT_FOUND"],
            f"No shielding_advice found in the database for postcode: {postcode}"
        ))
        return records

    if records[0][0]["longValue"] not in list(ShieldingAdvice):
        raise ValueError(f"RDS procedure returned unrecognised value {records}")

    shielding_advice = records[0][0]["longValue"]

    logger.info(create_log_message(log_event_names["POSTCODE_TO_SHIELDING_ADVICE_SUCCESS"],
                                   f"""Successfully retrieved shielding advice: {shielding_advice}
                                        for postcode: {postcode}"""))
    return shielding_advice


def get_postcode_tier(postcode):
    records = execute_sql(
            "CALL cv_ref.postcode_to_tier(:postcode)",
            (generate_string_parameter("postcode", postcode),),)["records"]

    if not records:
        logger.info(create_log_message(
            log_event_names["POSTCODE_TIER_NOT_FOUND"],
            f"No tier found in the database for postcode: {postcode}"
        ))
        return records

    tier = records[0][0]["longValue"]

    if records[0][0]["longValue"] not in list(PostcodeTier):
        raise ValueError(f"RDS procedure returned unrecognised value {records}")

    logger.info(create_log_message(log_event_names["POSTCODE_TO_TIER_SUCCESS"],
                                   f"Successfully retrieved tier: {tier} for postcode: {postcode}"))

    return tier


def get_uprn_tier(uprn):
    records = execute_sql(
            "CALL cv_ref.uprn_to_tier(:uprn)",
            (generate_int_parameter("uprn", uprn),),)["records"]

    if not records:
        logger.info(create_log_message(
            log_event_names["UPRN_TIER_NOT_FOUND"],
            "No tier found in the database for uprn: <redacted>"
        ))
        return records

    tier = records[0][0]["longValue"]

    if records[0][0]["longValue"] not in list(PostcodeTier):
        raise ValueError(f"RDS procedure returned unrecognised value {records}")

    logger.info(create_log_message(log_event_names["UPRN_TO_TIER_SUCCESS"],
                                   f"Successfully retrieved tier: {tier} for uprn: <redacted>"))

    return tier


def is_postcode_in_england(postcode):
    records = execute_sql(
            "CALL cv_ref.is_postcode_in_england(:postcode)",
            (generate_string_parameter("postcode", postcode),),)["records"]

    if records[0][0]["stringValue"] not in ("YES", "NO"):
        raise ValueError(f"RDS procedure returned unrecognised value {records}")

    is_postcode_in_england = records[0][0]["stringValue"] == "YES"

    log_event_name = log_event_names["POSTCODE_IN_ENGLAND"] if is_postcode_in_england \
        else log_event_names["POSTCODE_NOT_IN_ENGLAND"]

    logger.info(create_log_message(log_event_name,
                                   f"Postcode: {postcode} "))

    return is_postcode_in_england
