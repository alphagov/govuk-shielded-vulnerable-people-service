import os
import uuid

import jwt
from oic import rndstr
from oic.oauth2 import AuthorizationResponse
from oic.oic import Client
from oic.utils.authn.client import CLIENT_AUTHN_METHOD
from oic.utils.time_util import utc_time_sans_frac


class NHSOIDCDetails:
    def init_app(self, app):
        try:
            self.client_id = app.config["NHS_OIDC_CLIENT_ID"]
            self.authorization_callback_url = app.config["NHS_OIDC_LOGIN_CALLBACK_URL"]
            self.registration_callback_url = app.config[
                "NHS_OIDC_REGISTRATION_CALLBACK_URL"
            ]
            self.scopes = ["openid", "profile", "email", "phone", "profile_extended"]
            self.vtr = '["P5.Cp.Cd", "P5.Cp.Ck", "P5.Cm"]'
            self.authority_url = app.config["NHS_OIDC_AUTHORITY_URL"]
        except ValueError as e:
            raise ValueError(f"Missing NHS OIDC configuration: {e!r}")

        self.client = Client(
            client_id=self.client_id, client_authn_method=CLIENT_AUTHN_METHOD
        )
        self.client.provider_config(self.authority_url)

        self.private_key = app.config["NHS_OIDC_LOGIN_PRIVATE_KEY"]
        if not self.private_key:
            private_key_path = app.config["NHS_OIDC_LOGIN_PRIVATE_KEY_PATH"]
            if not os.stat(private_key_path):
                raise ValueError(
                    f"Missing private key file. Expected private key file at {self.private_key_path!r}"
                )

            with open(private_key_path) as key_file:
                self.private_key = key_file.read()


    def get_authorization_url(self):
        return self._get_authorization_url(self.authorization_callback_url, False)

    def get_registration_url(self):
        return self._get_authorization_url(self.registration_callback_url, True)

    def _get_authorization_url(self, callback_url, allow_registration):
        self.client.provider_config(self.authority_url)  # update
        return self.client.construct_AuthorizationRequest(
            request_args={
                "client_id": self.client.client_id,
                "response_type": "code",
                "scope": self.scopes,
                "nonce": rndstr(),
                "redirect_uri": callback_url,
                "state": rndstr(),
                "vtr": self.vtr,
                "allow_registration": allow_registration,
            }
        ).request(self.client.authorization_endpoint)

    def get_nhs_user_info_from_authorization_callback(self, callback_args):
        return self._get_nhs_user_info(callback_args, self.authorization_callback_url)

    def get_nhs_user_info_from_registration_callback(self, callback_args):
        return self._get_nhs_user_info(callback_args, self.registration_callback_url)

    def _get_nhs_user_info(self, callback_args, callback_url):
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
                "redirect_uri": callback_url,
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
        return jwt.encode(
            {
                "iss": self.client.client_id,
                "sub": self.client.client_id,
                "aud": self.client.token_endpoint,
                "jti": str(uuid.uuid4()),
                "exp": utc_time_sans_frac() + 120,
            },
            key=self.private_key,
            algorithm="RS512",
        ).decode("utf-8")
