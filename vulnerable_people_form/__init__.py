from http import HTTPStatus

import sentry_sdk
from flask import Flask, render_template, session
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from gds_metrics import GDSMetrics
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader
from sentry_sdk.integrations.flask import FlaskIntegration

from vulnerable_people_form.form_pages.shared.querystring_utils import append_querystring_params
from . import form_pages
from .form_pages.shared.form_utils import postcode_with_spaces
from .integrations import nhs_openconnect_id, persistence
from vulnerable_people_form.integrations import ladcode_tier_lookup

_ENV_DEVELOPMENT = "DEVELOPMENT"
_DEFAULT_LOCAL_RESTRICTIONS_FILE_PREFIX = "vulnerable_people_form/integrations/data/local-restrictions-"


def _handle_error(e):
    if e.code == HTTPStatus.INTERNAL_SERVER_ERROR.value:
        session.clear()
    return render_template(f"{e.code}.html"), e.code


def verify_config(app):
    required_keys = {
        "SECRET_KEY",
        "ORDNANCE_SURVEY_PLACES_API_KEY",
        "PERMANENT_SESSION_LIFETIME",
        "GA_TRACKING_ID",
        "GA_CROSS_DOMAIN_TRACKING_ID",
        "SENTRY_DSN",
        # NHS OIDC config
        "NHS_OIDC_AUTHORITY_URL",
        "NHS_OIDC_CLIENT_ID",
        "NHS_OIDC_REGISTRATION_CALLBACK_URL",
        "NHS_OIDC_REGISTRATION_CALLBACK_URL",
        "NHS_OIDC_LOGIN_CALLBACK_URL",
        # AWS CONFIG
        "AWS_REGION",
        "AWS_ACCESS_KEY",
        "AWS_SECRET_ACCESS_KEY",
        "ENVIRONMENT",
        "AWS_SQS_QUEUE_URL"
    }
    present_keys = set(k for k in app.config.keys() if app.config[k] is not None)
    if not present_keys.issuperset(required_keys):
        raise ValueError(f"The following config keys are missing: {', '.join(required_keys - present_keys)}")


def create_app(scriptinfo):
    app = Flask(__name__, static_url_path="/assets", instance_relative_config=True)
    app.config.from_envvar("FLASK_CONFIG_FILE")
    verify_config(app)
    metrics = GDSMetrics()
    metrics.init_app(app)
    app.jinja_loader = ChoiceLoader(
        [
            PackageLoader("vulnerable_people_form"),
            PrefixLoader({"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")}),
        ]
    )

    sentry_sdk.init(
        dsn=app.config["SENTRY_DSN"],
        integrations=[FlaskIntegration()],
        with_locals=False,
        request_bodies='never',
    )

    app.register_blueprint(form_pages.default.app_default)
    app.register_blueprint(form_pages.blueprint.form)

    _init_security(app)

    app.nhs_oidc_client = nhs_openconnect_id.NHSOIDCDetails()
    app.nhs_oidc_client.init_app(app)

    persistence.init_app(app)

    app.is_tiering_logic_enabled = "TIERING_LOGIC" in app.config and app.config["TIERING_LOGIC"] == "True"
    if app.is_tiering_logic_enabled:
        ladcode_tier_lookup.init(_get_ladcode_tier_data_path(app.config['ENVIRONMENT']))

    app.register_error_handler(HTTPStatus.NOT_FOUND.value, _handle_error)
    app.register_error_handler(HTTPStatus.INTERNAL_SERVER_ERROR.value, _handle_error)
    app.context_processor(utility_processor)

    app.add_template_filter(postcode_with_spaces)

    return app


def _get_ladcode_tier_data_path(env: str):
    return _DEFAULT_LOCAL_RESTRICTIONS_FILE_PREFIX + env.lower() + ".yaml"


def _init_security(app):
    CSRFProtect(app)

    app.config.update(SESSION_COOKIE_SAMESITE='Lax')

    google_analytics_base_url = "https://www.google-analytics.com"
    csp = {
        "default-src": "'self'",
        "img-src": [
            "'self'",
            google_analytics_base_url
        ],
        "script-src": [
            "'self'",
            google_analytics_base_url
        ],
        "connect-src": [
            "'self'",
            google_analytics_base_url
        ],
        "style-src": "'self'",
    }
    secure_system = app.config['ENVIRONMENT'] != _ENV_DEVELOPMENT

    return Talisman(
        app,
        force_https=secure_system,
        strict_transport_security=secure_system,
        session_cookie_secure=secure_system,
        content_security_policy=csp,
        content_security_policy_nonce_in=['script-src']
    )


def utility_processor():
    return dict(append_querystring_params=append_querystring_params)
