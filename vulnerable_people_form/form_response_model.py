import time
import os

from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, JSONAttribute
from flask import current_app


class FormResponse(Model):
    class Meta:
        table_name = os.environ.get(
            "AWS_DYNAMODB_SUBMISSIONS_TABLE_NAME", "coronavirus-vulnerable-people"
        )
        host = os.environ.get("USE_LOCALHOST_FOR_DYNAMODB", "http://localhost:8000")

        # The following lines are required for table creation
        write_capacity_units = 20
        read_capacity_units = 100

    reference_id = UnicodeAttribute(hash_key=True, attr_name="ReferenceId")
    unix_timestamp = NumberAttribute(
        range_key=True, attr_name="UnixTimestamp", default=time.time()
    )
    form_response = JSONAttribute(attr_name="FormResponse")


def create_tables_if_not_exist():
    if not FormResponse.exists():
        FormResponse.create_table()
