import csv
from datetime import datetime
import logging

from vulnerable_people_form.form_pages.shared.logger_utils import create_log_message, log_event_names

logger = logging.getLogger(__name__)

DEFAULT_NATIONAL_SHIELDING_ADVICE = False
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

        with open(shielding_advice_csv_file, 'r') as f:
            la_shielding_advice = csv.DictReader(f, delimiter=',')

            # Sort by date for every ladcode in ascending order
            self.la_shielding_advice_data = sorted(la_shielding_advice,
                                                   key=lambda k: (k['ladcode'], k['start_datetime_utc']),
                                                   reverse=False)

    def is_la_shielding(self, ladcode: str):
        """
        fetches the shielding advice status for supplied LAD Code
        """
        all_ladcode_records = self.get_all_records_for_ladcode(ladcode)
        if not all_ladcode_records:
            logger.info(create_log_message(
                log_event_names["LADCODE_NOT_IN_FILE"],
                f"{ladcode} not in shielding advice file. Using default: {DEFAULT_NATIONAL_SHIELDING_ADVICE}"))
            return DEFAULT_NATIONAL_SHIELDING_ADVICE

        shielding_advice = self.get_latest_valid_advice_for_ladcode(all_ladcode_records)
        logger.info(create_log_message(
            log_event_names["SHIELDING_ADVICE_FOR_LADCODE_SUCCESS"],
            f"{ladcode} has Shielding Advice {shielding_advice}"))
        return shielding_advice == 'YES'

    def get_all_records_for_ladcode(self, ladcode):
        """
        fetches the all shielding advice status for supplied LAD Code
        """
        all_records = []
        for record in self.la_shielding_advice_data:
            if record['ladcode'] == ladcode:
                all_records.append(record)
        return all_records

    def get_latest_valid_advice_for_ladcode(self, all_ladcode_records):
        """
        fetches the all shielding advice status for supplied LAD Code
        """
        latest_advice_for_ladcode = ''
        now = datetime.utcnow()
        for record in all_ladcode_records:
            record_start_datetime = datetime.strptime(record['start_datetime_utc'], '%Y-%m-%dT%H:%M:%S')
            if record_start_datetime < now:
                latest_advice_for_ladcode = record['shielding_advice']
            if record_start_datetime >= now:
                break
        return latest_advice_for_ladcode
