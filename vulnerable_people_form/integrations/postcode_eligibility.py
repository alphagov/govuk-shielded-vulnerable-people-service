import logging

from vulnerable_people_form.form_pages.shared.constants import PostcodeTier
from vulnerable_people_form.form_pages.shared.logger_utils import init_logger, log_event_names, create_log_message
from .persistence import generate_string_parameter, execute_sql
from vulnerable_people_form.integrations import ladcode_tier_lookup

logger = logging.getLogger(__name__)
init_logger(logger)


def get_postcode_tier(postcode):
    ladcode = get_ladcode(postcode)

    if not ladcode:
        return None

    postcode_tier = ladcode_tier_lookup.get_tier_by_ladcode(ladcode)

    if postcode_tier not in [e.value for e in PostcodeTier]:
        raise ValueError(f"Unexpected postcode tier retrieved: {postcode_tier}")

    return postcode_tier


def get_ladcode(postcode):
    records = execute_sql(
            "CALL cv_ref.postcode_to_ladcode(:postcode)",
            (generate_string_parameter("postcode", postcode),),)["records"]

    if not records:
        logger.info(create_log_message(
            log_event_names["LADCODE_NOT_FOUND"],
            f"No ladcode found in the database for postcode: {postcode}"
        ))
        return records

    if len(records) > 1:
        logger.warning(create_log_message(
            log_event_names["TOO_MANY_LADCODES_FOUND"],
            f"More than 1 ladcode found in the database for postcode: {postcode}"
        ))

    ladcode = records[0][0]["stringValue"]

    logger.info(create_log_message(log_event_names["POSTCODE_TO_LADCODE_SUCCESS"],
                                   f"Successfully retrieved ladcode: {ladcode} for postcode: {postcode}"))

    return ladcode


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
