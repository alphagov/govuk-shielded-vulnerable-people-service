import pytest

from vulnerable_people_form.form_pages.shared.constants import SESSION_KEY_QUERYSTRING_PARAMS
from vulnerable_people_form.form_pages.shared.querystring_utils import (
    get_querystring_params_to_retain,
    append_querystring_params
)

from flask import Flask

_current_app = Flask(__name__)
_current_app.secret_key = 'test_secret'


def test_get_querystring_params_to_retain_should_return_empty_dict_when_no_relevant_querystring_params_present():
    with _current_app.test_request_context("/"):
        params_to_retain = get_querystring_params_to_retain()
        assert len(params_to_retain) == 0


def test_get_querystring_params_to_retain_should_return_dict_with_la_param():
    with _current_app.test_request_context("/test?irrelevant=1&la=1"):
        params_to_retain = get_querystring_params_to_retain()
        assert len(params_to_retain) == 1
        assert params_to_retain["la"] == "1"


@pytest.mark.parametrize("initial_url, expected_output", [
    ("/next-page", "/next-page?la=3"),
    ("/next-page?another-param=1", "/next-page?another-param=1&la=3")
])
def test_append_querystring_params_should_append_la_param_when_present_in_request_args(
    initial_url, expected_output
):
    with _current_app.test_request_context("/test?irrelevant=1&la=3"):
        url = append_querystring_params(initial_url)
        assert url == expected_output


def test_append_querystring_params_should_not_append_la_param_when_already_present():
    with _current_app.test_request_context("/test?irrelevant=1&la=3"):
        url = append_querystring_params("/next-page?la=4")
        assert url == "/next-page?la=4"


def test_append_querystring_params_should_append_la_param_when_present_in_session():
    with _current_app.test_request_context("/test?irrelevant=1") as test_request_ctx:
        test_request_ctx.session[SESSION_KEY_QUERYSTRING_PARAMS] = {"la": "5"}
        url = append_querystring_params("/next-page")
        assert url == "/next-page?la=5"
