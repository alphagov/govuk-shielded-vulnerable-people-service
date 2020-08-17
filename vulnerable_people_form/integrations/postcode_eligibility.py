import os

from .persistence import get_rds_data_client, generate_string_parameter, execute_sql


def check_postcode(postcode):
    records = execute_sql(
        "CALL cv_base.is_postcode_in_lockdown(:postcode)",
        (generate_string_parameter("postcode", postcode),),
    )["records"]

    if records[0][0]["stringValue"] not in ("YES", "NO"):
        raise ValueError(f"RDS procedure returned unrecognised value {records}")

    return records[0][0]["stringValue"] == "YES"
