import os

SECRET_KEY = os.environ.get("SECRET_KEY")
ORDNANCE_SURVEY_PLACES_API_KEY = os.environ.get("ORDNANCE_SURVEY_PLACES_API_KEY")
PERMANENT_SESSION_LIFETIME = int(os.environ.get("PERMANENT_SESSION_LIFETIME"))
GA_TRACKING_ID = os.environ.get("GA_TRACKING_ID")

# NHS OIDC config
NHS_OIDC_AUTHORITY_URL = os.environ.get("NHS_OIDC_AUTHORITY_URL")
NHS_OIDC_CLIENT_ID = os.environ.get("NHS_OIDC_CLIENT_ID")
NHS_OIDC_REGISTRATION_CALLBACK_URL = os.environ.get(
    "NHS_OIDC_REGISTRATION_CALLBACK_URL"
)
NHS_OIDC_LOGIN_CALLBACK_URL = os.environ.get("NHS_OIDC_LOGIN_CALLBACK_URL")
NHS_OIDC_LOGIN_PRIVATE_KEY = os.environ.get("NHS_OIDC_LOGIN_PRIVATE_KEY")


# AWS CONFIG
LOCAL_AWS_ENDPOINT_URL = os.environ.get("LOCAL_AWS_ENDPOINT_URL")
AWS_REGION = os.environ.get("AWS_REGION")
AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

DATABASE_SECRET_TAGS = [
    s.strip() for s in os.environ.get("DATABASE_SECRET_TAGS", "").split(",")
]

DATABASE_CLUSTER_PREFIX = os.environ.get("DATABASE_CLUSTER_PREFIX")

AWS_RDS_DATABASE_ARN_OVERRIDE = os.environ.get("AWS_RDS_DATABASE_ARN_OVERRIDE")
AWS_RDS_SECRET_ARN_OVERRIDE = os.environ.get("AWS_RDS_SECRET_ARN_OVERRIDE")
