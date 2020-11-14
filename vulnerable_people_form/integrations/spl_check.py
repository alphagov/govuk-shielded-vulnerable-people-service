import logging

from vulnerable_people_form.form_pages.shared.logger_utils import create_log_message, log_event_names, init_logger
from .persistence import generate_string_parameter, generate_date_parameter, execute_sql

logger = logging.getLogger(__name__)
init_logger(logger)


def check_spl(nhs_number, date_of_birth):
    test_mode = 'NO'
    records = execute_sql(
        "CALL cv_base.is_person_currently_on_the_spl_new(:nhs_number, :date_of_birth, :test_mode)",
        (
            generate_string_parameter("nhs_number", nhs_number),
            generate_date_parameter("date_of_birth", date_of_birth),
            generate_string_parameter("test_mode", test_mode),
        ),
    )["records"]

    if records[0][0]["stringValue"] not in ("YES", "NO"):
        raise ValueError(f"RDS procedure returned unrecognised value {records}")

    is_person_on_spl = records[0][0]["stringValue"] == "YES"

    logger.info(create_log_message(log_event_names["SPL_CHECK"], f"is on the SPL: {is_person_on_spl}"))

    return is_person_on_spl
