from http import HTTPStatus

from flask import (
    Blueprint,
    redirect,
    render_template
)
from flask_wtf.csrf import CSRFError

from vulnerable_people_form.form_pages.shared.querystring_utils import append_querystring_params
from vulnerable_people_form.form_pages.shared.session import has_started_form

form = Blueprint("form", __name__)


@form.before_request
def redirect_to_first_page():
    if not has_started_form():
        return _redirect_to_session_expired()


@form.after_request
def add_caching_headers(response):
    if response.status_code == HTTPStatus.FOUND:
        redirect_location = append_querystring_params(response.headers['Location'])
        response = redirect(redirect_location)

    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return response


@form.errorhandler(CSRFError)
def handle_csrf_error(e):
    if not has_started_form():
        return _redirect_to_session_expired()
    else:
        return render_template("400.html")


def _redirect_to_session_expired():
    redirect_location = append_querystring_params("/session-expired")
    return redirect(redirect_location)
