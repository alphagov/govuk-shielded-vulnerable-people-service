from flask import render_template, session, current_app, request

from .constants import PAGE_TITLES
from .session import accessing_saved_answers


def render_template_with_title(template_name, *args, **kwargs):
    if not template_name.endswith(".html"):
        raise ValueError("Template names must end with '.html' for a title to be assigned")

    cookie_prefs_value = request.cookies.get("cookies_preferences_set")
    cookies_preferences_set = cookie_prefs_value is not None and cookie_prefs_value.lower() == "true"
    cross_domain_tracking_id = current_app.config.get("GA_CROSS_DOMAIN_TRACKING_ID")
    return render_template(
        template_name,
        *args,
        title_text=PAGE_TITLES[template_name[:-5]],
        ga_tracking_id=current_app.config.get("GA_TRACKING_ID"),
        ga_cross_domain_tracking_id=cross_domain_tracking_id if cross_domain_tracking_id is not None else "",
        cookie_preferences_set=cookies_preferences_set,
        **{
            "nhs_user": session.get("nhs_sub") is not None,
            "button_text": "Save and continue" if accessing_saved_answers() else "Continue",
            **kwargs,
        },
    )
