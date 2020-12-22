import csv
from datetime import datetime
import logging

from vulnerable_people_form.form_pages.shared.logger_utils import create_log_message, log_event_names

logger = logging.getLogger(__name__)

DEFAULT_NATIONAL_SHIELDING_ADVICE = 'NO'
FIELDNAMES = [
    'ladcode',
    'ladname',
    'shielding_advice',
    'start_datetime_utc'
]


class LocalAuthorityShielding:
    la_shielding_advice_data = {}

    def __init__(self, shielding_advice_csv_file: str):
        self.la_shielding_advice_data = {}
        valid_applicable_records = []

        with open(shielding_advice_csv_file, 'r') as f:
            la_shielding_advice = csv.DictReader(f, delimiter=',')

            # Find all non-future records
            for la in la_shielding_advice:
                now = datetime.utcnow()
                if datetime.strptime(la['start_datetime_utc'], '%Y-%m-%dT%H:%M:%S') < now:
                    valid_applicable_records.append(la)
            # Sort by date for every ladcode in ascending order
            sorted_advice = sorted(
                valid_applicable_records,
                key=lambda k: (k['ladcode'], k['start_datetime_utc']),
                reverse=False)
            # Keep the latest record only.
            for record in sorted_advice:
                ladcode = record['ladcode']
                self.la_shielding_advice_data[ladcode] = record

    def get_shielding_advice_by_ladcode(self, ladcode: str):
        """
        fetches the shielding advice status for supplied LAD Code
        """
        if ladcode not in self.la_shielding_advice_data:
            logger.info(create_log_message(
                log_event_names["LADCODE_NOT_IN_FILE"],
                f"{ladcode} not in shielding advice file. Using default: {DEFAULT_NATIONAL_SHIELDING_ADVICE}"))
            return DEFAULT_NATIONAL_SHIELDING_ADVICE

        shielding_advice = self.la_shielding_advice_data[ladcode]["shielding_advice"]
        logger.info(create_log_message(
            log_event_names["SHIELDING_ADVICE_FOR_LADCODE_SUCCESS"],
            f"{ladcode} has Shielding Advice {shielding_advice}"))
        return shielding_advice
