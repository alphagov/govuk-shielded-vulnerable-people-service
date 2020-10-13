from vulnerable_people_form.form_pages.shared.constants import SESSION_KEY_QUERYSTRING_PARAMS
from vulnerable_people_form.form_pages.shared.querystring_utils import get_querystring_params_to_retain
from .blueprint import form
from flask import session, redirect


@form.route("/", methods=["GET"])
def get_default_route():
    return _clear_session_and_create_redirect_response()


@form.route("/start", methods=["GET"])
def get_start():
    return _clear_session_and_create_redirect_response()


def _clear_session_and_create_redirect_response():
    session.clear()
    _populate_session_with_querystring_params_to_retain()
    return redirect("/applying-on-own-behalf")


def _populate_session_with_querystring_params_to_retain():
    querystring_params = get_querystring_params_to_retain()
    if querystring_params:
        session[SESSION_KEY_QUERYSTRING_PARAMS] = querystring_params
