from http import HTTPStatus

import sentry_sdk
from flask import Flask, render_template, request, session
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader
from prometheus_flask_exporter import PrometheusMetrics
from sentry_sdk.integrations.flask import FlaskIntegration

from . import form_pages
from .integrations import nhs_openconnect_id, persistence

_ENV_DEVELOPMENT = "DEVELOPMENT"


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
        "NOTIFY_API_KEY",
        "SENTRY_DSN",
        "GOVUK_NOTIFY_SPL_MATCH_EMAIL_TEMPLATE_ID",
        "GOVUK_NOTIFY_SPL_MATCH_SMS_TEMPLATE_ID",
        "GOVUK_NOTIFY_SPL_MATCH_LETTER_TEMPLATE_ID",
        "GOVUK_NOTIFY_NO_SPL_MATCH_EMAIL_TEMPLATE_ID",
        "GOVUK_NOTIFY_NO_SPL_MATCH_SMS_TEMPLATE_ID",
        "GOVUK_NOTIFY_NO_SPL_MATCH_LETTER_TEMPLATE_ID",
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
        "ENVIRONMENT"
    }
    present_keys = set(k for k in app.config.keys() if app.config[k] is not None)
    if not present_keys.issuperset(required_keys):
        raise ValueError(f"The following config keys are missing: {', '.join(required_keys - present_keys)}")


def create_app(scriptinfo):
    app = Flask(__name__, static_url_path="/assets", instance_relative_config=True)
    app.config.from_envvar("FLASK_CONFIG_FILE")
    verify_config(app)
    app.jinja_loader = ChoiceLoader(
        [
            PackageLoader("vulnerable_people_form"),
            PrefixLoader({"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")}),
        ]
    )

    sentry_sdk.init(
        dsn=app.config["SENTRY_DSN"], integrations=[FlaskIntegration()],
    )

    app.register_blueprint(form_pages.blueprint.form)

    _init_security(app)

    app.nhs_oidc_client = nhs_openconnect_id.NHSOIDCDetails()
    app.nhs_oidc_client.init_app(app)

    persistence.init_app(app)

    app.register_error_handler(HTTPStatus.NOT_FOUND.value, _handle_error)
    app.register_error_handler(HTTPStatus.INTERNAL_SERVER_ERROR.value, _handle_error)

    metrics = PrometheusMetrics(app)
    metrics.register_default(
        metrics.counter(
            "by_path_counter",
            "Request count by request paths",
            labels={"path": lambda: request.path},
        ),
        metrics.histogram(
            "requests_by_status_and_path",
            "Request latencies by status and path",
            labels={
                "status": lambda r: r.status_code,
                "path": lambda: request.path,
            },
        ),
    )

    return app


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
