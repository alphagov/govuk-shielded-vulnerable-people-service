from flask import (
    Blueprint,
    redirect,
    render_template,
    session,
)
from flask_wtf.csrf import CSRFError

form = Blueprint("form", __name__)


@form.before_request
def redirect_to_first_page():
    if not session.get("form_started"):
        session.clear()
        session["form_started"] = True
        return redirect("/applying-on-own-behalf")


@form.after_request
def add_caching_headers(response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return response


@form.errorhandler(CSRFError)
def handle_csrf_error(e):
    if "form_started" not in session:
        return render_template("session-expired.html")
    else:
        return render_template("400.html")
