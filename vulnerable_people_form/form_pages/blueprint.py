from flask import (
    Blueprint,
    abort,
    current_app,
    redirect,
    render_template,
    request,
    session,
)
from flask_wtf.csrf import CSRFError

form = Blueprint("form", __name__)


@form.before_request
def redirect_to_first_page():
    if not session.get("form_started"):
        session.clear()
        session["form_started"] = True
        return redirect("/view-or-setup")


@form.errorhandler(CSRFError)
def handle_csrf_error(e):
    if "form_started" not in session:
        return render_template("session-expired.html")
    else:
        return render_template("400.html")
