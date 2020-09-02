from flask import render_template, session

from .constants import PAGE_TITLES
from .session import accessing_saved_answers


def render_template_with_title(template_name, *args, **kwargs):
    if not template_name.endswith(".html"):
        raise ValueError("Template names must end with '.html' for a title to be assigned")
    return render_template(
        template_name,
        *args,
        title_text=PAGE_TITLES[template_name[:-5]],
        **{
            "nhs_user": session.get("nhs_sub") is not None,
            "button_text": "Save and continue" if accessing_saved_answers() else "Continue",
            **kwargs,
        },
    )
