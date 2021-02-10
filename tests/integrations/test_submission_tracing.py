import json
from flask import Flask

from vulnerable_people_form.integrations import submission_tracing

_current_app = Flask(__name__)
_current_app.secret_key = 'test_secret'
_current_app.config["SUBMISSION_TRACING_PEPPER"] = "100fb56c689993f9f05b281491fd2883"


def test_anonymised_submission_log_returns_full_log_with_valid_details():
    # GIVEN some submission details
    test_ip = "111.111.1.1"
    test_ua_string = """Mozilla/5.0 (Apple-iPhone7C2/1202.466; U; CPU like Mac OS X; en)
        AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543 Safari/419.3"""
    test_ua_platform = "iphone"
    test_ua_browser = "safari"
    test_ua_version = "3.0"
    test_submission_reference = "11111111"
    test_submission_details = ["01234567890", "07777777777", "test@test.com", "1 Test Street", "TE12ST"]
    test_nhs_sub = "22222222"

    # WHEN we call the anonymised_submission_log function
    with _current_app.test_request_context(environ_base={"REMOTE_ADDR": test_ip,
                                                         "HTTP_USER_AGENT": test_ua_string}):
        log = submission_tracing.anonymised_submission_log(submission_reference=test_submission_reference,
                                                           submission_details=test_submission_details,
                                                           nhs_sub=test_nhs_sub)
        log_dict = json.loads(log)
        # THEN the log contains the correct details
        assert log_dict["user_agent"]["platform"] == test_ua_platform
        assert log_dict["user_agent"]["browser"] == test_ua_browser
        assert log_dict["user_agent"]["version"] == test_ua_version
        assert log_dict["user_agent"]["string"] == test_ua_string
        assert log_dict["submission_reference"] is not None
        assert log_dict["submission_reference"] != test_submission_reference
        assert log_dict['event'] == "persist_answers"
        assert _are_submission_details_anonymised(test_submission_details, log_dict["submission_details"])


def test_anonymised_submission_log_returns_partial_log_when_full_details_not_provided():
    # GIVEN some request info, but no submission details
    test_ip = "111.111.1.1"
    test_ua_string = """Mozilla/5.0 (Apple-iPhone7C2/1202.466; U; CPU like Mac OS X; en)
        AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543 Safari/419.3"""
    test_ua_platform = "iphone"
    test_ua_browser = "safari"
    test_ua_version = "3.0"

    # WHEN we call the anonymised_submission_log function
    with _current_app.test_request_context(environ_base={"REMOTE_ADDR": test_ip,
                                                         "HTTP_USER_AGENT": test_ua_string}):
        log = submission_tracing.anonymised_submission_log()
        log_dict = json.loads(log)
        # THEN the log contains the correct details
        assert log_dict["user_agent"]["platform"] == test_ua_platform
        assert log_dict["user_agent"]["browser"] == test_ua_browser
        assert log_dict["user_agent"]["version"] == test_ua_version
        assert log_dict["user_agent"]["string"] == test_ua_string
        assert log_dict['event'] == "persist_answers"


def _are_submission_details_anonymised(details, anon_details):
    """Check that details and anon_details do not contain the same values"""
    return (len(details) == len(anon_details) and not set.intersection(set(details), set(anon_details)))
