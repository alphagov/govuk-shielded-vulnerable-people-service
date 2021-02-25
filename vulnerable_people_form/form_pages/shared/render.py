from flask import render_template, current_app, request

from .constants import PAGE_TITLES
from .session import accessing_saved_answers, is_nhs_login_user


def render_template_with_title(template_name, *args, **kwargs):
    if not template_name.endswith(".html"):
        raise ValueError("Template names must end with '.html' for a title to be assigned")

    cookie_prefs_value = request.cookies.get("cookies_preferences_set")
    cookies_preferences_set = cookie_prefs_value is not None and cookie_prefs_value.lower() == "true"
    cross_domain_tracking_id = current_app.config.get("GA_CROSS_DOMAIN_TRACKING_ID")
    is_changing_form_answer = request.args.get("ca") and request.args["ca"] == "1"
    return render_template(
        template_name,
        *args,
        title_text=PAGE_TITLES[template_name[:-5]],
        page_has_validation_error='error_list' in kwargs and kwargs["error_list"],
        ga_tracking_id=current_app.config.get("GA_TRACKING_ID"),
        ga_cross_domain_tracking_id=cross_domain_tracking_id if cross_domain_tracking_id is not None else "",
        cookie_preferences_set=cookies_preferences_set,
        form_base_template="base.html" if is_changing_form_answer else "base-with-back-link.html",
        **{
            "nhs_user": is_nhs_login_user(),
            "button_text": "Save and continue" if accessing_saved_answers() else "Continue",
            **kwargs,
        },
    )
