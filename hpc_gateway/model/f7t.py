import os
import pathlib
from contextlib import nullcontext

import firecrest as f7t
import requests
from flask import current_app


def create_f7t_client():
    if os.environ.get("DEPLOYMENT", "MC") == "IWM":
        hardcode = HardCodeTokenAuth(
            token=current_app.config["F7T_TOKEN"],
        )
        auth_url = current_app.config["F7T_AUTH_URL"]
        client = Firecrest(firecrest_url=auth_url, authorization=hardcode)

        return client

    else:
        client_id = current_app.config["F7T_CLIENT_ID"]
        client_secret = current_app.config["F7T_CLIENT_SECRET"]
        token_url = current_app.config["F7T_TOKEN_URL"]
        auth_url = current_app.config["F7T_AUTH_URL"]

        # Create an authorization object with Client Credentials authorization grant
        keycloak = f7t.ClientCredentialsAuth(
            client_id,
            client_secret,
            token_url,
        )

        # Setup the client for the specific account
        client = Firecrest(firecrest_url=auth_url, authorization=keycloak)

        return client


# Create an authorization object with Client Credentials authorization grant
class HardCodeTokenAuth:
    def __init__(self, token):
        self._token = token

    def get_access_token(self):
        return self._token


class Firecrest(f7t.Firecrest):
    def simple_upload(self, machine, source_path, target_path, filename):
        """Blocking call to upload a small file.
        The file that will be uploaded will have the same name as the source_path.
        The maximum size of file that is allowed can be found from the parameters() call.
        :param source_path: binary stream
        :type source_path: binary stream
        :param target_path: the absolute target path of the directory where the file will be uploaded
        :type target_path: string
        :calls: POST `/utilities/upload`
        :rtype: None
        """
        # This method is implemented to pyfirecrest, but not release yet.
        # THis part can be removed after bump pyfirecrest version to 1.3.0.

        url = f"{self._firecrest_url}/utilities/upload"
        headers = {
            "Authorization": f"Bearer {self._authorization.get_access_token()}",
            "X-Machine-Name": machine,
        }
        context = (
            open(source_path, "rb")
            if isinstance(source_path, str)
            or isinstance(source_path, pathlib.PosixPath)
            else nullcontext(source_path)
        )

        with context as f:
            # Set filename
            if filename is not None:
                f = (filename, f)
            data = {"targetPath": target_path}
            files = {"file": f}
            resp = requests.post(
                url=url, headers=headers, data=data, files=files, verify=self._verify
            )

        self._json_response([resp], 201)
