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

  - `Procfile`: This file contains a gunicorn command, intended for use in
    production by CloudFoundry. It is also possible to run it using a 
    Procfile runner.

  - `runtime.txt`: A file containing the version of python that CloudFoundry 
    will use to run the application with.

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
folder. There are two files in the instance folder. The first at
`instance/config.py.sample.dev` is a sample config file suitable for
development. The second is a file (`instance/env_to_config_shim.py`)
that allows the use of environment variables for app configuration,
which is intended to smooth production deployments.

### Development configuration

To set up the app for local development you need to follow these steps:

1.  Copy the configuration template file to a config file: 
    ```sh
    cp instance/config.py.sample.dev instance/config.py
    ```
2. Start rds-client-api and mysql, and sqs server
    ```docker-compose up -d```

3.  Fill in the missing configuration values as per the **Configuration
    Variables Guide** section, and set the AWS environment variables as
    per the ***Environment Variables Guide***. Otherwise it will default to talking to a local mock ons server and the mock rds-client. 

4.  If you wish to test with NHS functionality place the private key file for your NHS oidc client id into the
    path `instance/private_key.pem`.
 
5. Make sure the database is up to date (following the guide in 
   covid-engineering/database/README.md).
   ```
   cd $PATH_TO_COVID_ENGINEERING\covid-engineering\database
   alembic --config=alembic.local.ini upgrade head

   ```
6. Create a local queue in sqs. You need to have [awslocal](https://github.com/localstack/awscli-local) installed
   ```
   scripts/create-sqs-queue.sh 
   ```

		
### Production configuration & Deployment

In production the app is intended to retrieve its configuration from
environment variables. To do this it uses the file at
`instance/env_to_config.shim` as its path.

1.  Set the Flask environment to production, and let Flask know where
    the app file is stored:
    ```sh
    export FLASK_CONFIG=`env_to_config_shim.py`
    export FLASK_ENV=`production`
    export FLASK_APP=`run.py`
    ```
2.  Set environment variables as per the **Configuration Variables Guide** section.

3.  Set the additional environment variable for gunicorn
    (`$GUNICORN_WORKERS_COUNT`) and `NHS_OIDC_LOGIN_PRIVATE_KEY`.

4.  Run the app via the Procfile, using any procfile runner.

The SVP is deployed to GOV.UK PaaS using Concourse.

The pipeline can be found here:

https://cd.gds-reliability.engineering/teams/covid19/pipelines/svp-form

The deployment pipeline is configured as follows:

- update: updates the pipeline
- test: installs any python dependencies and runs the unit tests using pytest
- deploy-to-staging: deploys the application to staging space in GOV.UK PaaS
- smoke-test-staging: a simple curl command is run to check the website is up and running
- e2e-test-staging: runs the python behave automation tests
- deploy-to-prod: deploys the application to the production space in GOV.UK PaaS
- smoke-test-prod: a simple curl command is run to check the website is up and running

The following environment variables are all stored within Concourse and pulled into the pipeline when it is run.


- AWS_ACCESS_KEY
- AWS_SECRET_ACCESS_KEY
- NHS_OIDC_LOGIN_PRIVATE_KEY
- ORDNANCE_SURVEY_PLACES_API_KEY
- SECRET_KEY


### Environment variables guide

  - `FLASK_ENV` **\[required\]**: This should be set to `development`
    when developing, and `production` when in production.

  - `FLASK_CONFIG` **\[required\]**: The path to the Flask config file
    that the app should use. The path is given relative to the instance
    folder.

  - `FLASK_APP` **\[required\]**: The path to the Flask app's run file.
    This should be set to `run.py`.

  - `OVERRIDE_ONS_URL` : Remove if you wish to test with the real ONS API with an API key

### Configuration variables guide

The following variables can either be set in the config file pointed at
by the `FLASK_CONFIG` environment variable, or if using the
`env_to_config_shim.py` configuration, configured as environment
variables.

  - `SECRET_KEY` **\[required\]**: This is the secret key that Flask
    will use to encrypt the session.

  - `ORDNANCE_SURVEY_PLACES_API_KEY` **\[required\]**: The API key for
    the Ordnance Survey Places API. This is used to retrieve a list of
    candidate addresses from the UPRN.

  - `PERMANENT_SESSION_LIFETIME` **\[defaults to 3600 seconds\]** : This
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
    
  - `NHS_OIDC_LOGIN_PRIVATE_KEY_PATH`: This is used to specify the path 
     to the private key pem file when working within a local development environment.
     
  - `NHS_OIDC_LOGIN_PRIVATE_KEY`: This is used to specify the private key
     contents in the GOV.UK PaaS environment only. 

  - `AWS_RDS_DATABASE_NAME` **\[required\]**: This variable sets the
    database that the app will use to persist form answers.

  - `AWS_REGION` **\[required\]**: This variable sets the AWS region
    that the app will communicate with to persist form answers.

  - `AWS_ACCESS_KEY` **\[required\]**: This variable sets the AWS
    access key that the app needs to communicate with AWS servers.
 
  - `AWS_SECRET_ACCESS_KEY` **\[required\]**: This variable sets the
    AWS secret access key that the app needs to communicate with AWS
    servers. A blank string can be used if no schema is required.

  - `DATABASE_CLUSTER_PREFIX` **\[either this or
    `AWS_RDS_DATABASE_ARN_OVERRIDE` required\]**: This variable is used
    to retrieve the correct AWS database cluster ARN from RDS.

  - `AWS_SQS_QUEUE_URL` **\[required\]**: This variable is used to send
    messages to SQS which sends user communications.

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
    endpoint URL, instead of the AWS (RDS) servers.

  - `LOCAL_SQS_ENDPOINT_URL` **\[not required\]**: The presence of this
    variable will configure the app to communicate with the supplied
    endpoint URL, instead of the AWS (SQS) servers.

  - `AWS_RDS_DATABASE_ARN_OVERRIDE` **\[either this or
    `DATABASE_CLUSTER_PREFIX` required\]**: If this variable is present
    it will be used as the database or 'resource' ARN when communicating
    with AWS.

  - `AWS_RDS_SECRET_ARN_OVERRIDE` **\[either this or
    `DATABASE_SECRET_TAGS` required\]**: If this variable is present it
    will be used as the RDS secret ARN when communicating with AWS. 

  - `DEBUG_METRICS` **\[not required\]**: If this variable is set then
    Prometheus metrics will be available in development mode.

## Unit tests

### Execution
The unit tests can be executed from the root of the project by issuing the following command:
``python -m pytest --disable-warnings``

### Code coverage
The code coverage can be viewed by executing the following commands from the root of the project:
```
coverage run --source vulnerable_people_form/ -m pytest --disable-warnings

coverage report -m
```

## Automated tests

### Running locally
The flask web application should be running locally on port 5000 (http://localhost:5000) as per the above instructions.

In order to get them to pass the following nhs tests you need to add in variables in the docker-compose.yml 
* NHS_EMAIL
* NHS_PASSWORD
* NHS_OTP


The tests can then be executed using the following command from the root of the project:
```
make test_e2e_local
```


## Licence

[MIT License](LICENCE)
