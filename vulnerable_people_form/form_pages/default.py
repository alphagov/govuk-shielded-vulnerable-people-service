from vulnerable_people_form.form_pages.shared.constants import (
    SESSION_KEY_QUERYSTRING_PARAMS,
    GOVUK_JOURNEY_START_PAGE_URL
)
from vulnerable_people_form.form_pages.shared.querystring_utils import (
    get_querystring_params_to_retain,
    append_querystring_params
)
from flask import session, redirect, Blueprint, render_template

app_default = Blueprint("app_default", __name__)


@app_default.route("/", methods=["GET"])
def get_default_route():
    return redirect(GOVUK_JOURNEY_START_PAGE_URL)


@app_default.route("/start", methods=["GET"])
def get_start():
    session.clear()
    session["form_started"] = True
    _populate_session_with_querystring_params_to_retain()
    return redirect(append_querystring_params("/applying-on-own-behalf"))


@app_default.route("/session-expired", methods=["GET"])
def get_session_expired():
    session.clear()
    return render_template("session-expired.html",
                           govuk_start_page_url=GOVUK_JOURNEY_START_PAGE_URL)


def _populate_session_with_querystring_params_to_retain():
    querystring_params = get_querystring_params_to_retain()
    if querystring_params:
        session[SESSION_KEY_QUERYSTRING_PARAMS] = querystring_params
