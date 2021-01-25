from flask import session, current_app, redirect

from .blueprint import form
from .shared.constants import ShieldingAdvice
from .shared.render import render_template_with_title
from .shared.session import (
    get_summary_rows_from_form_answers,
    get_shielding_advice,
    is_returning_nhs_login_user_without_basic_care_needs_answer)


@form.route("/view-answers", methods=["GET"])
def get_view_answers():
    session["check_answers_page_seen"] = True
    exclude_answers = ["nhs_number", "date_of_birth"]

    if current_app.is_tiering_logic_enabled:
        if is_returning_nhs_login_user_without_basic_care_needs_answer():
            return redirect("/basic-care-needs?ca=1")
        if get_shielding_advice() == ShieldingAdvice.NOT_ADVISED_TO_SHIELD.value:
            exclude_answers.append('basic_care_needs')

    return render_template_with_title(
        "view-answers.html",
        summary_rows=get_summary_rows_from_form_answers(exclude_answers)
    )
