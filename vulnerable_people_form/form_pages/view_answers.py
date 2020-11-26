from flask import session, current_app, redirect

from .blueprint import form
from .shared.constants import PostcodeTier
from .shared.render import render_template_with_title
from .shared.session import (
    get_summary_rows_from_form_answers,
    get_postcode_tier,
    is_nhs_login_user,
    get_answer_from_form,
    accessing_saved_answers
)


@form.route("/view-answers", methods=["GET"])
def get_view_answers():
    session["check_answers_page_seen"] = True
    exclude_answers = ["nhs_number", "date_of_birth"]

    if current_app.is_tiering_logic_enabled:
        if is_returning_nhs_login_user_without_basic_care_needs_answer():
            return redirect("/basic-care-needs")
        if get_postcode_tier() == PostcodeTier.VERY_HIGH.value:
            exclude_answers.append('basic_care_needs')

    return render_template_with_title(
        "view-answers.html",
        summary_rows=get_summary_rows_from_form_answers(exclude_answers)
    )


def is_returning_nhs_login_user_without_basic_care_needs_answer():
    # Scenario: Where the postcode tier has increased to VERY_HIGH_PLUS_SHIELDING
    # and no answer is present for 'basic_care_needs'
    return is_nhs_login_user() \
           and accessing_saved_answers() \
           and get_postcode_tier() == PostcodeTier.VERY_HIGH_PLUS_SHIELDING.value \
           and get_answer_from_form(["basic_care_needs"]) is None
