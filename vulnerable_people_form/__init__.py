from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader
from flask import Flask, render_template
from . import views


def create_app(config_filename):
    app = Flask(__name__, static_url_path="/assets", instance_relative_config=True)
    app.config.from_pyfile(config_filename)

    app.jinja_loader = ChoiceLoader(
        [
            PackageLoader("vulnerable_people_form"),
            PrefixLoader(
                {"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")}
            ),
        ]
    )

    app.register_blueprint(views.form)
    return app
