from flask import current_app, redirect, session

from .answers_enums import ViewOrSetupAnswers, get_radio_options_from_enum
from .blueprint import form
from .render_utils import render_template_with_title
from .session_utils import form_answers, get_errors_from_session, request_form
from .validation import validate_view_or_setup


@form.route("/view-or-setup", methods=["GET"])
def get_view_or_setup():
    session.clear()
    session["form_started"] = True
    return render_template_with_title(
        "view-or-setup.html",
        radio_items=get_radio_options_from_enum(
            ViewOrSetupAnswers, form_answers().get("live_in_england")
        ),
        previous_path="/applying-on-own-behalf",
        **get_errors_from_session("view_or_setup"),
    )


@form.route("/view-or-setup", methods=["POST"])
def post_view_or_setup():
    if not validate_view_or_setup():
        return redirect("/view-or-setup")
    answer = ViewOrSetupAnswers(request_form().get("view_or_setup"))
    if answer is ViewOrSetupAnswers.VIEW:
        return redirect(current_app.nhs_oidc_client.get_authorization_url())
    return redirect("/applying-on-own-behalf")
