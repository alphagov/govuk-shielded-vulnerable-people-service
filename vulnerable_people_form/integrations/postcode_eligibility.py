import logging

from vulnerable_people_form.form_pages.shared.logger_utils import init_logger, log_event_names, create_log_message
from .persistence import generate_string_parameter, execute_sql

logger = logging.getLogger(__name__)
init_logger(logger)


def get_postcode_tier(postcode):
    records = execute_sql(
            "CALL cv_base.get_postcode_tier(:postcode)",
            (generate_string_parameter("postcode", postcode),),)["records"]

    if records[0][0]["stringValue"] not in ("MEDIUM", "HIGH", "VERY_HIGH", "VERY_HIGH_PLUS_SHIELDING"):
        raise ValueError(f"get_postcode_tier returned an unrecognised valus {records}")

    tier = records[0][0]["stringValue"]

    log_event_name = log_event_names[f"{tier}_POSTCODE_TIER"]
    logger.info(create_log_message(log_event_name, f"Postcode: {postcode}"))

    return (tier)


def check_postcode(postcode):
    records = execute_sql(
        "CALL cv_base.is_postcode_in_lockdown(:postcode)",
        (generate_string_parameter("postcode", postcode),),
    )["records"]

    if records[0][0]["stringValue"] not in ("YES", "NO"):
        raise ValueError(f"RDS procedure returned unrecognised value {records}")

    postcode_is_eligible = records[0][0]["stringValue"] == "YES"

    log_event_name = log_event_names["POSTCODE_ELIGIBLE"] if postcode_is_eligible \
        else log_event_names["POSTCODE_INELIGIBLE"]
    logger.info(create_log_message(log_event_name, f"Postcode: {postcode}"))

    return postcode_is_eligible
