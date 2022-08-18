import firecrest as f7t
import requests
import os
from contextlib import nullcontext
import pathlib

# # For CSCS daint only
# # Configuration parameters for the Authorization Object
# client_id = os.environ.get('FIRECREST_CLIENT_ID')
# client_secret = os.environ.get('FIRECREST_CLIENT_SECRET')
# token_uri = "https://auth.cscs.ch/auth/realms/cscs/protocol/openid-connect/token"

# # Create an authorization account object with Client Credentials authorization grant
# keycloak = f7t.ClientCredentialsAuth(
#     client_id, client_secret, token_uri
# )

# Create an authorization object with Client Credentials authorization grant
class HardCodeTokenAuth:
    
    def __init__(self, token):
        self._token = token
        
    def get_access_token(self):
        return self._token
    
class Firecrest(f7t.Firecrest):
    
    
    # def simple_download(self, source_path, target_path):
    #     """Blocking call to download a small file.
    #     The maximun size of file that is allowed can be found from the parameters() call.
    #     :param source_path: the absolute source path
    #     :type source_path: string
    #     :param target_path: binary stream
    #     :type target_path: binary stream
    #     :calls: GET `/utilities/download`
    #     :rtype: None
    #     """
        
    #     url = f"{self._firecrest_url}/utilities/download"
    #     headers = {
    #         "Authorization": f"Bearer {self._authorization.get_access_token()}",
    #         "X-Machine-Name": self._MACHINE,
    #     }
    #     params = {"sourcePath": source_path}
    #     resp = requests.get(
    #         url=url, headers=headers, params=params, verify=self._verify
    #     )
    #     # print(resp.content)
    #     self._json_response([resp], 200)
    #     context = nullcontext(target_path)

    #     with context as f:
    #         f.write(resp.content)
            
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
    
    # def simple_delete(self, target_path):
    #     """Blocking call to delete a small file.
    #     :param target_path: the absolute target path
    #     :type target_path: string
    #     :calls: DELETE `/utilities/rm`
    #     :rtype: None
    #     """

    #     url = f"{self._firecrest_url}/utilities/rm"
    #     headers = {
    #         "Authorization": f"Bearer {self._authorization.get_access_token()}",
    #         "X-Machine-Name": self._MACHINE,
    #     }
    #     data = {"targetPath": target_path}
    #     resp = requests.delete(url=url, headers=headers, data=data, verify=self._verify)
        
    #     return self._json_response([resp], 204)
        