from marketplace import MarketPlaceClient
from marketplace.app.v0 import MarketPlaceApp
from marketplace.app.v0.utils import _encode_metadata
from marketplace_standard_app_api.models import transformation
from packaging.version import parse

STAGING_URL = "https://staging.materials-marketplace.eu/"
MC_HPC_APP_ID = "13f59545-cb1f-4113-b873-6bb079539788"
IWM_HPC_APP_ID = "c0ee3889-0b97-4083-8a7b-a1a807848437"


def get_app(name, access_token=None, **kwargs):
    """Get an hpc gateway app instance.
    Args:
        app_id (str): client id of the app
        **kwargs: keyword arguments for the app
    Returns:
        MarketPlaceApp: app instance
    """
    client = MarketPlaceClient(
        marketplace_host_url=STAGING_URL, access_token=access_token
    )

    # Getting api version and list of capabilities for the application
    if name == "iwm":
        app_id = IWM_HPC_APP_ID
    elif name == "mc":
        app_id = MC_HPC_APP_ID
    else:
        raise RuntimeError(f"No hpc gateway app named {name} available.")

    app_service_path = f"api/applications/{app_id}"
    resp = client.get(path=app_service_path)
    if resp.status_code == 200:
        app_info = resp.json()
    else:
        raise RuntimeError("request fail, check access token is renewed.")

    app_api_version = parse(app_info["api_version"])
    assert app_api_version == parse("0.3.0")

    return HpcGatewayApp(client, app_id, app_info, **kwargs)


class HpcGatewayApp(MarketPlaceApp):
    """This class simply do mapping of capabilities as alias."""

    # If the API is fully conformed with the standard app API
    # the following alias can be easily implemented. (Tedious for the momnet
    # since the app updated functionality is broken for the moment.
    # have to register the new app again everytime when bug found.)
    #
    # create_job = MarketPlaceApp.new_transformation
    # launch_job = MarketPlaceApp.start_transformation
    # check_job_state = MarketPlaceApp.get_transformation_state
    # cancel_job = MarketPlaceApp.delete_transformation

    # download_file = MarketPlaceApp.get_dataset
    # upload_file = MarketPlaceApp.create_dataset
    # delete_file = MarketPlaceApp.delete_dataset

    def create_user(self, **kwargs):
        return super().create_or_update_collection(metadata={}, **kwargs)

    def create_job(
        self, new_transformation: transformation.NewTransformationModel
    ) -> str:
        response_json = self._client.post(
            self._proxy_path("newTransformation"), json=new_transformation
        ).json()
        return response_json.get("jobid", "")

    def launch_job(
        self,
        jobid: str,
    ):
        response = self._client.patch(
            self._proxy_path("updateTransformation"),
            params={"jobid": jobid},
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise RuntimeError("request fail, check access token is renewed.")

    def check_job_state(
        self,
        jobid: str,
    ) -> dict:
        response_json = self._client.get(
            self._proxy_path("getTransformationState"),
            params={"jobid": jobid},
        ).json()

        return response_json

    def cancel_job(self, jobid: str):
        return self._client.delete(
            self._proxy_path("deleteTransformation"),
            params={"jobid": jobid},
        ).json()

    def download_file(
        self,
        jobid: str,
        filename: str,
    ):
        return self._client.get(
            self._proxy_path("getDataset"),
            params={"jobid": jobid, "filename": filename},
        )

    def delete_file(
        self,
        jobid: str,
        filename: str,
    ):
        resp = self._client.delete(
            self._proxy_path("deleteDataset"),
            params={"jobid": jobid, "filename": filename},
        )

        return resp.json()

    def upload_file(
        self,
        jobid: str,
        filename: str,
        source_path: str,
    ):
        params = {"jobid": jobid}
        if filename:
            params.update({"filename": filename})

        with open(source_path, "rb") as fh:
            files = {"file": (fh.name, fh, "multipart/form-data")}
            return self._client.put(
                self._proxy_path("createDataset"),
                params=params,
                headers=_encode_metadata({}),
                files=files,
            )
