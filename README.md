#	Deployment (development)

##	Prerequisites

  - Python 3.8.5
  - Pip
  - Docker
  - Google Analytics API key
  - Sentry DSN
  - NHS oidc client id + private key

#	Developers' guide

##	Folder structure

This repository uses Flask (with the registry pattern). The app is
structured like this:

  - `instance`: This folder contains files relating to a specific
    running instance of an app, as well as template files for the
    configuration of the app.

  - `vulnerable_people_form`: A package containing the app itself.

  - `vulnerable_people_form/form_pages`: Each Python module/file in
    this folder relates to a specific route in the app. All methods
    for the route are contained in the same module. The convention is
    to give the file the same name as the route, only with dashes
    (`-`) replaced with underscores (`_`).

  - `vulnerable_people_form/form_pages/shared/`: Some functionality
    provided by each route is shared across multiple routes. This
    package provides a central location to store the shared
    functionality. Examples of shared functionality include session
    management, validation and routing.

  - `vulnerable_people_form/templates`: This is a collection of jinja2
    templates used to render each route. Shared functionality is broken
    out into templates with the suffix/prefix `base`, otherwise the
    convention is to name the template after the route.

  - `vulnerable_people_form/static`: This folder is created by
    `build.sh` and serves static content in development.

##	Root level executables and files of interest

  - `run.py`: This file is responsible for running the app in
    development mode. It can be run in standalone mode (`python run.py`)
    but is best run as described in the **Development Configuration**
    section to get auto-reloading.

  - `build.sh`: This file retrieves static dependencies (only the
    government design system js files currently) and places them in
    `vulnerable_people_form/static`.

## AWS integration

This app persists and retrieves form responses from an Amazon Aurora RDS
MySQL database backend created by the `covid-engineering` repository.
That repository produces an endpoint, which we communicate with over an
RDS Data HTTP connection. We call the following procedures:

  - `cv_base.retrieve_latest_web_submission_for_nhs_login`
  - `cv_staging.create_web_submission`

In addition we use an `rds` client to retrieve database resource ARNs,
and the `secretsmanager` API to retrieve the database secret ARN.

The `AWS_ACCESS_KEY` and `AWS_SECRET_ACCESS_KEY` variables in this
application need to be configured with credentials that have sufficient
privileges to perform those operations.

## Setup

Instance-level configuration and keys are stored in the instance
folder. When deploying this folder will need to be created manually.

### Development setup

To set up the app for local development you need to follow these steps:

1.  Create a new instance directory:
    ```sh
    mkdir instance
    ```

2.  Create a new file at `instance/config.py` and place this
    configuration into it: 
    ```python
    SECRET_KEY = "Something super secret"
    TEMPLATES_AUTO_RELOAD = True
    ORDNANCE_SURVEY_PLACES_API_KEY = 
    PERMANENT_SESSION_LIFETIME = 30 * 60
    GA_TRACKING_ID =

    # SENTRY CONFIG
    SENTRY_DSN =

    # NHS OIDC config
    NHS_OIDC_AUTHORITY_URL = "https://auth.sandpit.signin.nhs.uk"
    NHS_OIDC_CLIENT_ID =
    NHS_OIDC_REGISTRATION_CALLBACK_URL = "http://localhost:5000/nhs-registration-callback"
    NHS_OIDC_LOGIN_CALLBACK_URL = "http://localhost:5000/nhs-login-callback"
    NHS_OIDC_SCOPES=["openid", "profile", "email", "phone", "profile_extended"]
    NHS_OIDC_VTR=["P0.Cp.Cd", "P0.Cp.Ck", "P0.Cm"]

    # AWS CONFIG
    AWS_RDS_DATABASE_NAME = "coronavirus"
    AWS_RDS_DATABASE_SCHEMA = ""
    ```
    Obviously, change the example hostnames as appropriate for your
    setup.

3.  Fill in the missing configuration values as per the **Configuration
    Variables Guide** section, and set the AWS environment variables as
    per the ***Environment Variables Guide***.

4.  Place the private key file for your NHS oidc client id into the
    path `instance/private_key.pem`.

5.  Set the `FLASK_CONFIG_FILE` environment variable so that it points at
    the new file. (Note: the root path for Flask config is the `instance`
    folder.) I.e.:
    ```sh
    export FLASK_CONFIG_FILE='config.py'
    ```
    
6.  Set the Flask environment to development, and let Flask know where
    the app file is stored:
    ```sh
    export FLASK_ENV='development'
    export FLASK_APP='run.py'
    ```

7.  Run the build script that downloads the government dependencies:
    ```sh
    bash build.sh
    ```

8.  Set up the Python environment:
    ```sh
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
	
9.  Run the app:
    ```sh
    flask run
    ```

10. Navigate to: http://localhost:5000/start in a web browser.

### Environment variables guide

  - `FLASK_ENV` **\[required\]**: This should be set to `development`
    when developing, and `production` when in production.

  - `FLASK_CONFIG` **\[required\]**: The path to the Flask config file
    that the app should use. The path is given relative to the instance
    folder.

  - `FLASK_APP` **\[required\]**: The path to the Flask app's run file.
    This should be set to `run.py`.

  - `AWS_DEFAULT_REGION` **\[required\]**: This variable sets the AWS
    region that the app will communicate with to persist form answers.

  - `AWS_ACCESS_KEY_ID` **\[required\]**: This variable sets the AWS
    access key that the app needs to communicate with AWS servers.
 
  - `AWS_SECRET_ACCESS_KEY` **\[required\]**: This variable sets the
    AWS secret access key that the app needs to communicate with AWS
    servers.

### Configuration variables guide

The following variables are set in the config file pointed at
by the `FLASK_CONFIG` environment variable.

  - `SECRET_KEY` **\[required\]**: This is the secret key that Flask
    will use to encrypt the session.

  - `ORDNANCE_SURVEY_PLACES_API_KEY` **\[required\]**: The API key for
    the Ordnance Survey Places API. This is used to retrieve a list of
    candidate addresses from the UPRN.

  - `PERMANENT_SESSION_LIFETIME` **\[defaults to 1800 seconds\]** : This
    is the lifetime of a session, provided in seconds.

  - `GA_TRACKING_ID` **\[required\]**: The Google Analytics tracking id
    the app uses to record certain events.

  - `SENTRY_DSN` **\[required\]**: This is the DSN to which Sentry will
    submit its stack traces.

  - `NHS_OIDC_AUTHORITY_URL` **\[required\]**: The authority URL at
    which OIDC logins will take place.

  - `NHS_OIDC_CLIENT_ID` **\[required\]**: The client id that the app
    will use to authenticate with the client.

  - `NHS_OIDC_REGISTRATION_CALLBACK_URL` **\[required\]**: This is the
    callback URL passed to NHS OIDC when the user is attempting
    registration. It should have the form
    `http(s)://<externally_reachable_app_url>/nhs-registration-callback`.

  - `NHS_OIDC_LOGIN_CALLBACK_URL` **\[required\]**: This is the callback
    URL passed to NHS OIDC when the user is in the login flow. It should
    have the form
    `http(s)://<externally_reachable_app_url>/nhs-login-callback`.

  - `AWS_RDS_DATABASE_NAME` **\[required\]**: This variable sets the
    database that the app will use to persist form answers.

  - `AWS_RDS_DATABASE_SCHEMA` **\[optional\]**: this variable sets the
    schema of the database that the app will use to persist form
    answers.

  - `DATABASE_CLUSTER_PREFIX` **\[either this or
    `AWS_RDS_DATABASE_ARN_OVERRIDE` required\]**: This variable is used
    to retrieve the correct AWS database cluster ARN from RDS.

  - `DATABASE_SECRET_TAGS` **\[either this or
    `AWS_RDS_DATABASE_SECRET_OVERRIDE` required\]**: This variable
    should be a list of tags that the app uses to retrieve the correct
    values from the database. If set as an environment variable this
    should be a comma-separated list of tags. If set in the `config.py`
    file, it should be a list of Python strings.

#### Useful config variables for development

  - `TEMPLATES_AUTO_RELOAD` **\[not required\]**: This should be set to
    `True` in development, as it will tell Flask to automatically reload
    templates as they change. It defaults to false.

  - `LOCAL_AWS_ENDPOINT_URL` **\[not required\]**: The presence of this
    variable will configure the app to communicate with the supplied
    endpoint URL, instead of the AWS servers.

  - `AWS_RDS_DATABASE_ARN_OVERRIDE` **\[either this or
    `DATABASE_CLUSTER_PREFIX` required\]**: If this variable is present
    it will be used as the database or 'resource' ARN when communicating
    with AWS.

  - `AWS_RDS_SECRET_ARN_OVERRIDE` **\[either this or
    `DATABASE_SECRET_TAGS` required\]**: If this variable is present it
    will be used as the RDS secret ARN when communicating with AWS. 

