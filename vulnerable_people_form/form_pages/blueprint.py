from http import HTTPStatus

from flask import (
    Blueprint,
    redirect,
    render_template,
    session,
)
from flask_wtf.csrf import CSRFError

from vulnerable_people_form.form_pages.shared.constants import SESSION_KEY_QUERYSTRING_PARAMS
from vulnerable_people_form.form_pages.shared.querystring_utils import (
    append_querystring_params,
    get_querystring_params_to_retain
)

form = Blueprint("form", __name__)


@form.before_request
def redirect_to_first_page():
    if not session.get("form_started"):
        session.clear()
        session["form_started"] = True

        querystring_params = get_querystring_params_to_retain()
        if querystring_params:
            session[SESSION_KEY_QUERYSTRING_PARAMS] = querystring_params

        return redirect("/applying-on-own-behalf")


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
    if "form_started" not in session:
        return render_template("session-expired.html")
    else:
        return render_template("400.html")
