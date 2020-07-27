import jwt
import os
import uuid

from oic import rndstr
from oic.oic import Client
from oic.utils.authn.client import CLIENT_AUTHN_METHOD

from oic.utils.time_util import utc_time_sans_frac

from oic.oauth2 import AuthorizationResponse

from flask import Blueprint
from flask import current_app


class NHSOIDCDetails:
    def init_app(self, app):
        try:
            self.client_id = app.config["NHS_OIDC_CLIENT_ID"]
            self.callback_url = app.config["NHS_OIDC_CALLBACK_URL"]
            self.scopes = app.config["NHS_OIDC_SCOPES"]
            self.vtr = app.config["NHS_OIDC_VTR"]
            self.authority_url = app.config["NHS_OIDC_AUTHORITY_URL"]
        except ValueError as e:
            raise ValueError(f"Missing NHS OIDC configuration: {e!r}")

        self.client = Client(
            client_id=self.client_id, client_authn_method=CLIENT_AUTHN_METHOD
        )
        self.client.provider_config(self.authority_url)

        self.private_key_path = os.path.join(app.instance_path, "private_key.pem")
        if not os.stat(self.private_key_path):
            raise ValueError(
                f"Missing private key file. Expected private key file at {self.private_key_path!r}"
            )

    def get_authorization_url(self):
        self.client.provider_config(self.authority_url)  # update
        return self.client.construct_AuthorizationRequest(
            request_args={
                "client_id": self.client.client_id,
                "response_type": "code",
                "scope": self.scopes,
                "nonce": rndstr(),
                "redirect_uri": self.callback_url,
                "state": rndstr(),
                "vtr": self.vtr,
            }
        ).request(self.client.authorization_endpoint)

    def get_nhs_user_info(self, callback_args):
        auth_response = self.client.parse_response(
            AuthorizationResponse, info=callback_args, sformat="dict"
        )

        access_token_result = self.client.do_access_token_request(
            algorithm="RS512",
            authn_endpoint="token",
            authn_method="private_key_jwt",
            client_assertion=self._get_client_assertion(),
            request_args={
                "code": auth_response["code"],
                "client_id": self.client.client_id,
                "redirect_uri": self.callback_url,
            },
            scope=self.scopes,
            state=auth_response.get("state", ""),
        )
        if "access_token" not in access_token_result:
            raise RuntimeError(
                f"Could not retrieve access token from NHS oidc endpoint. Recieved {access_token_result}"
            )

        return self.client.do_user_info_request(
            token=access_token_result["access_token"], method="GET"
        ).to_dict()

    def _get_client_assertion(self):
        with open(self.private_key_path) as key_file:
            return jwt.encode(
                {
                    "iss": self.client.client_id,
                    "sub": self.client.client_id,
                    "aud": self.client.token_endpoint,
                    "jti": str(uuid.uuid4()),
                    "exp": utc_time_sans_frac() + 120,
                },
                key=key_file.read(),
                algorithm="RS512",
            ).decode("utf-8")
