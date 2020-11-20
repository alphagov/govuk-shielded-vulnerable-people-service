import yaml

from datetime import datetime
import pytz

import logging
logger = logging.getLogger(__name__)


DEFAULT_LOCAL_RESTRICTIONS_FILE = "vulnerable_people_form/tier_lookup/data/local-restrictions.yaml"
DEFAULT_NATIONAL_ALERT_LEVEL = 1


class LacodeTierLookup:
    """
    fetches the tier status for supplied LA Code
    """

    def __init__(self, restrictions_yaml_file: str = DEFAULT_LOCAL_RESTRICTIONS_FILE):
        with open(restrictions_yaml_file, 'r') as f:
            la_restrictions = yaml.load(f, Loader=yaml.BaseLoader)

        for la in la_restrictions:
            for restriction in la_restrictions[la]["restrictions"]:
                restriction["start_datetime"] = self.__get_start_datetime(restriction)

                del restriction["start_date"]
                del restriction["start_time"]

                restriction["alert_level"] = int(restriction["alert_level"])

            sorted_restrictions = sorted(
                    la_restrictions[la]["restrictions"],
                    key=lambda k: k['start_datetime'],
                    reverse=True)

            la_restrictions[la]["restrictions"] = sorted_restrictions

        self.la_restrictions = la_restrictions

    def lacode_to_tier(self, lacode: str):
        if lacode not in self.la_restrictions:
            logger.info(f"{lacode} not in restrictions file. Using default.")
            return DEFAULT_NATIONAL_ALERT_LEVEL

        for restriction in self.la_restrictions[lacode]["restrictions"]:
            now = datetime.utcnow().replace(tzinfo=pytz.utc)
            if now > restriction["start_datetime"]:
                tier = restriction["alert_level"]
                logger.info(f"{lacode} has restriction level {tier}")
                return tier

        logger.info(f"{lacode} has no relevant restriction level. Using default.")
        return DEFAULT_NATIONAL_ALERT_LEVEL

    def __get_start_datetime(self, restriction):
        return pytz.timezone("Europe/London").localize(
                datetime.strptime(
                    f'{restriction["start_date"]} {restriction["start_time"]}',
                    '%Y-%m-%d %H:%M'
                    )
                ).astimezone(pytz.utc)
