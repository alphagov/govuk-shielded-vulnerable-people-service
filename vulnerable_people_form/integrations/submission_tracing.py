import json
import time
import hashlib
import random

from flask import request, current_app


def _client_ip():
    if request:
        if request.environ.get("HTTP_X_FORWARDED_FOR") is None:
            return request.environ["REMOTE_ADDR"]
        else:
            # if behind a proxy
            return request.environ["HTTP_X_FORWARDED_FOR"]
    return None


def _user_agent():
    result = {"platform": None, "browser": None, "version": None, "string": None}
    if request:
        ua_obj = request.user_agent
        result["platform"] = ua_obj.platform
        result["browser"] = ua_obj.browser
        result["version"] = ua_obj.version
        result["string"] = ua_obj.string
    return result


def _peppering(obj, pepper):
    m = hashlib.sha256()
    # convert to string and lower case
    objstr = str(obj).lower()
    # get only the alphanumeric characters
    objstr = "".join(e for e in objstr if e.isalnum())
    # generate hash
    m.update(f"{pepper}:{objstr}".encode())
    # return first 32 characters of the 64 character hash hex
    return m.hexdigest()[:32]


def _hash_without_peppering(obj):
    """Hashes obj without a pepper for easier cross-referencing
    with other log data. Use _peppering instead where this is
    not required."""
    m = hashlib.sha256()
    # convert to string and lower case
    objstr = str(obj).lower()
    # get only the alphanumeric characters
    objstr = "".join(e for e in objstr if e.isalnum())
    # generate hash
    m.update(f"{objstr}".encode())
    # return first 32 characters of the 64 character hash hex
    return m.hexdigest()[:32]


def anonymised_submission_log(
    submission_reference=None, submission_details=[], nhs_sub=None
):
    log_output = {}
    try:
        pepper = current_app.config.get("SUBMISSION_TRACING_PEPPER")
        if not current_app or pepper is None:
            raise Exception("current_app not available or SUBMISSION_TRACING_PEPPER not set")

        if submission_details:
            random.shuffle(submission_details)

        log_output = {
            "time": time.time(),
            "event": "persist_answers",
            "client_ip": _client_ip(),
            "user_agent": _user_agent(),
            "submission_reference": _hash_without_peppering(submission_reference),
            "submission_details": [
                _peppering(sd, pepper) for sd in submission_details if sd is not None
            ],
            "nhs_sub": _peppering(nhs_sub, pepper),
        }
    except Exception as e:
        log_output = {"time": time.time(), "event": "persist_answers", "error": str(e)}

    return json.dumps(log_output)
