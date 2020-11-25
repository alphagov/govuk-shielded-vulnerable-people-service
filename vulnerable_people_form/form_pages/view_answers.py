from flask import session, current_app

from .blueprint import form
from .shared.constants import PostcodeTier
from .shared.render import render_template_with_title
from .shared.session import get_summary_rows_from_form_answers, get_postcode_tier


@form.route("/view-answers", methods=["GET"])
def get_view_answers():
    session["check_answers_page_seen"] = True

    exclude_answers = ["nhs_number", "date_of_birth"]

    if current_app.is_tiering_logic_enabled and get_postcode_tier() == PostcodeTier.VERY_HIGH.value:
        exclude_answers.append('basic_care_needs')

    return render_template_with_title(
        "view-answers.html",
        summary_rows=get_summary_rows_from_form_answers(exclude_answers)
    )
