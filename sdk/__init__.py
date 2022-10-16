import ast
from typing import Union
from urllib.parse import urljoin

from marketplace.app import MarketPlaceApp
from urllib3.response import HTTPResponse


class HpcGatewayApp(MarketPlaceApp):
    def status(self):
        return super().heartbeat()

    def _request(self, op, path, **kwargs):
        kwargs.setdefault("headers", {}).update(self.default_headers)
        full_url = urljoin(self.marketplace_host_url, path)
        response = op(url=full_url, **kwargs)
        if response.status_code >= 300:
            message = (
                f"Querying MarketPlace for {full_url} returned {response.status_code} "
                f"because: {response.text}."
                "Please check the host, client_id and token validity."
            )
            raise RuntimeError(message)
        return response

    def upload_file(self, resourceid, source_path=str):
        """upload file to remote path `resourceid` from source path"""
        with open(source_path, "rb") as fh:
            print(resourceid)
            print(fh)
            super().put(
                path="updateDataset",
                params={"resourceid": f"{resourceid}"},
                files={"file": fh},
            )

    def download_file(
        self, resourceid, filename, is_binary=False
    ) -> Union[str, HTTPResponse]:
        """download file from `resourceid`
        return str of content"""
        resp = super().get(
            path="getDataset",
            params={"resourceid": f"{resourceid}"},
            json={"filename": filename},
            stream=True,
        )

        if is_binary:
            return resp.raw
        else:
            return resp.txt

    def delete_file(self, resourceid, filename):
        super().delete(
            path="delateDataset",
            params={"resourceid": f"{resourceid}"},
            json={"filename": filename},
        )

    def new_job(self, config=None):
        """Create a new job

        Actually it will create a new folder in specific user path on HPC
        Return the folder name for further opreration."""
        resp = super().new_transformation(config)
        resp = ast.literal_eval(resp)

        return resp["resourceid"]

    def list_job(self):
        """List the jobs"""
        # TODO filter jobs from respond
        return super().get(path="getTransformationList").json()

    def run_job(self, resourceid):
        """submit job in the path `resourceid`
        It actually execute sbatch submit.sh in remote
        Need job script `submit.sh` uploaded to the folder
        TODO, check the job script ready"""
        resp = super().post(
            path="startTransformation", params={"resourceid": f"{resourceid}"}
        )

        return resp.text

    def cancel_job(self, resourceid):
        """cancel a job"""
        resp = super().post(
            path="stopTransformation", params={"resourceid": f"{resourceid}"}
        )

        return resp.text

    def delete_job(self, resourceid):
        """delete job corresponded to path `resourceid`
        It actually drop entity from DB.
        """
        resp = super().delete(
            path="deleteTransformation", params={"resourceid": f"{resourceid}"}
        )

        return resp.text
