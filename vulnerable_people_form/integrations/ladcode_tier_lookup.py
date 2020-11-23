import yaml

from datetime import datetime
import pytz

import logging

from vulnerable_people_form.form_pages.shared.constants import PostcodeTier
from vulnerable_people_form.form_pages.shared.logger_utils import create_log_message, log_event_names

logger = logging.getLogger(__name__)

DEFAULT_LOCAL_RESTRICTIONS_FILE = "vulnerable_people_form/integrations/data/local-restrictions.yaml"
DEFAULT_NATIONAL_ALERT_LEVEL = PostcodeTier.MEDIUM.value

la_restrictions_data = {}


def init(restrictions_yaml_file: str = DEFAULT_LOCAL_RESTRICTIONS_FILE):
    global la_restrictions_data

    with open(restrictions_yaml_file, 'r') as f:
        la_restrictions = yaml.load(f, Loader=yaml.BaseLoader)

    for la in la_restrictions:
        for restriction in la_restrictions[la]["restrictions"]:
            restriction["start_datetime"] = _get_start_datetime(restriction)

            del restriction["start_date"]
            del restriction["start_time"]

            restriction["alert_level"] = int(restriction["alert_level"])

        sorted_restrictions = sorted(
            la_restrictions[la]["restrictions"],
            key=lambda k: k['start_datetime'],
            reverse=True)

        la_restrictions[la]["restrictions"] = sorted_restrictions

    la_restrictions_data = la_restrictions


def get_tier_by_ladcode(ladcode: str):
    """
    fetches the tier status for supplied LAD Code
    """
    if ladcode not in la_restrictions_data:
        logger.info(create_log_message(
            log_event_names["LADCODE_NOT_IN_FILE"],
            f"{ladcode} not in restrictions file. Using default: {DEFAULT_NATIONAL_ALERT_LEVEL}"))
        return DEFAULT_NATIONAL_ALERT_LEVEL

    for restriction in la_restrictions_data[ladcode]["restrictions"]:
        now = datetime.utcnow().replace(tzinfo=pytz.utc)
        if now > restriction["start_datetime"]:
            tier = restriction["alert_level"]
            logger.info(create_log_message(
                log_event_names["LADCODE_SUCCESSFULLY_MAPPED_TO_TIER"],
                f"{ladcode} has restriction level {tier}"))
            return tier

    logger.info(create_log_message(log_event_names["LADCODE_HAS_NO_RELEVANT_RESTRICTION"],
                                   f"{ladcode} has no relevant restriction level. Using default: {DEFAULT_NATIONAL_ALERT_LEVEL}"))  # noqa
    return DEFAULT_NATIONAL_ALERT_LEVEL


def _get_start_datetime(restriction):
    return pytz.timezone("Europe/London").localize(
        datetime.strptime(
            f'{restriction["start_date"]} {restriction["start_time"]}',
            '%Y-%m-%d %H:%M'
        )
    ).astimezone(pytz.utc)
