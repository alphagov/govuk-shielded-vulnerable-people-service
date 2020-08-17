import sentry_sdk
from flask import Flask, render_template, request
from flask_wtf.csrf import CSRFProtect
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader
from prometheus_flask_exporter import PrometheusMetrics
from sentry_sdk.integrations.flask import FlaskIntegration

from . import form_pages
from .integrations import nhs_openconnect_id, persistence

sentry_sdk.init(
    dsn="https://examplePublicKey@o0.ingest.sentry.io/0",
    integrations=[FlaskIntegration()],
)


def generate_error_handler(code):
    def handle_error(_):
        return render_template(f"{code}.html"), code

    return handle_error


def verify_config(app):
    required_keys = {
        "SECRET_KEY",
        "ORDNANCE_SURVEY_PLACES_API_KEY",
        "AWS_DYNAMODB_SUBMISSIONS_TABLE_NAME",
        "PERMANENT_SESSION_LIFETIME",
        "GA_TRACKING_ID",
        # SENTRY CONFIG
        "SENTRY_DSN",
        # NHS OIDC config
        "NHS_OIDC_AUTHORITY_URL",
        "NHS_OIDC_CLIENT_ID",
        "NHS_OIDC_REGISTRATION_CALLBACK_URL",
        "NHS_OIDC_REGISTRATION_CALLBACK_URL",
        "NHS_OIDC_LOGIN_CALLBACK_URL",
    }
    present_keys = set(k for k in app.config.keys() if app.config[k] is not None)
    if not present_keys.issuperset(required_keys):
        raise ValueError(
            f"The following config keys are missing: {', '.join(required_keys - present_keys)}"
        )


def create_app(scriptinfo):
    app = Flask(__name__, static_url_path="/assets", instance_relative_config=True)
    app.config.from_envvar("FLASK_CONFIG_FILE")
    verify_config(app)
    app.jinja_loader = ChoiceLoader(
        [
            PackageLoader("vulnerable_people_form"),
            PrefixLoader(
                {"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")}
            ),
        ]
    )

    app.register_blueprint(form_pages.blueprint.form)
    CSRFProtect(app)

    app.nhs_oidc_client = nhs_openconnect_id.NHSOIDCDetails()
    app.nhs_oidc_client.init_app(app)

    persistence.init_app(app)

    app.register_error_handler(404, generate_error_handler(404))
    app.register_error_handler(500, generate_error_handler(500))

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
            labels={"status": lambda r: r.status_code, "path": lambda: request.path,},
        ),
    )

    sentry_sdk.init(
        dsn=app.config["SENTRY_DSN"], integrations=[FlaskIntegration()],
    )

    return app
