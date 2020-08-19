import os

from .persistence import get_rds_data_client, generate_string_parameter, generate_date_parameter, execute_sql


def check_spl(nhs_number, date_of_birth):
    records = execute_sql(
        "CALL cv_base.is_person_on_the_spl(:nhs_number, :date_of_birth)",
        (
            generate_string_parameter("nhs_number", nhs_number),
            generate_date_parameter("date_of_birth", date_of_birth),
        ),
    )["records"]

    if records[0][0]["stringValue"] not in ("YES", "NO"):
        raise ValueError(f"RDS procedure returned unrecognised value {records}")

    return records[0][0]["stringValue"] == "YES"
