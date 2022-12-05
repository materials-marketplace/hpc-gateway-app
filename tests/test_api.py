import pathlib
from contextlib import nullcontext
from types import MethodType

import pytest
from bson.objectid import ObjectId
from firecrest import Firecrest


def test_index(client):
    response = client.get("/")
    assert "HPC gateway app for MarketPlace" in str(response.data)


@pytest.fixture()
def auth_header():
    token = "valid_token"
    header = {
        "Accept": "application/json",
        "User-Agent": "HPC-app",
        "Authorization": f"Bearer {token}",
    }
    return header


@pytest.fixture()
def userinfo():
    """userinfo is a dict return for query userinfo from marketplace"""
    info = {
        "sub": "222-333",
        "email_verified": False,
        "roles": ["admin", "user"],
        "name": "Jusong Yu",
        "preferred_username": "jusongyu",
        "given_name": "Jusong",
        "family_name": "Yu",
        "email": "jusong.yu@epfl.ch",
    }

    return info


# test of user API
def test_create_user(app, requests_mock, monkeypatch, mock_db, auth_header, userinfo):
    """Mock the f7t mkdir operation and create a db, we don't want
    the test have outside effect on the server."""
    client = app.test_client()
    userinfo_url = app.config["MP_USERINFO_URL"]

    def mock_mkdir(cls, machine, target_path, p=None):
        return "mkdir!"

    # monkeypatch the mkdir operation of f7t
    monkeypatch.setattr("firecrest.Firecrest.mkdir", MethodType(mock_mkdir, Firecrest))

    # moketpach the db
    monkeypatch.setattr("hpc_gateway.model.database.db", mock_db)

    requests_mock.get(userinfo_url, json=userinfo, status_code=200)
    response = client.post("/api/v1/user/create", headers=auth_header)

    rjson = response.json
    assert rjson["home"] == "/scratch/f7t/jusong_yu"
    assert rjson["message"] == "Success: Create user in database."


# test job APIs
def test_create_job(app, auth_header, userinfo, mock_db, monkeypatch, requests_mock):
    client = app.test_client()
    userinfo_url = app.config["MP_USERINFO_URL"]

    def mock_mkdir(cls, machine, target_path, p=None):
        return "mkdir!"

    # monkeypatch the mkdir operation of f7t
    monkeypatch.setattr("firecrest.Firecrest.mkdir", MethodType(mock_mkdir, Firecrest))

    # moketpach the db
    monkeypatch.setattr("hpc_gateway.model.database.db", mock_db)

    requests_mock.get(userinfo_url, json=userinfo, status_code=200)

    # create user
    client.post("/api/v1/user/create", headers=auth_header)

    # create jobs
    response = client.post("/api/v1/job/create", headers=auth_header)
    job_id = response.json["jobid"]

    assert response.status_code == 200

    job = mock_db.jobs.find_one({"_id": ObjectId(job_id)})
    assert job.get("state") == "CREATED"

    # create another job
    client.post("/api/v1/job/create", headers=auth_header)

    # get jobs
    response = client.get("/api/v1/job/", headers=auth_header)
    assert job_id in response.json["jobs"]


def test_launch_job(app, auth_header, userinfo, mock_db, monkeypatch, requests_mock):
    """This test launch job to cluster and get job list by f7t."""
    client = app.test_client()
    userinfo_url = app.config["MP_USERINFO_URL"]
    expected_f7t_job_id = "00001"

    def mock_mkdir(cls, machine, target_path, p=None):
        return "mkdir!"

    def mock_submit(cls, machine, job_script, local_file=False):
        return {"jobid": expected_f7t_job_id}

    # monkeypatch the mkdir/submit operation of f7t
    monkeypatch.setattr("firecrest.Firecrest.mkdir", MethodType(mock_mkdir, Firecrest))
    monkeypatch.setattr(
        "firecrest.Firecrest.submit", MethodType(mock_submit, Firecrest)
    )

    # moketpach the db
    monkeypatch.setattr("hpc_gateway.model.database.db", mock_db)

    requests_mock.get(userinfo_url, json=userinfo, status_code=200)

    # create user
    client.post("/api/v1/user/create", headers=auth_header)

    # create jobs
    response = client.post("/api/v1/job/create", headers=auth_header)
    job_id = response.json["jobid"]

    assert response.status_code == 200

    # launch the job
    response = client.post(f"/api/v1/job/launch/{job_id}", headers=auth_header)

    assert response.status_code == 200

    job = mock_db.jobs.find_one({"_id": ObjectId(job_id)})
    assert job.get("state") == "ACTIVATED"
    assert job.get("f7t_job_id") == expected_f7t_job_id


def test_cancel_job(app, auth_header, userinfo, mock_db, monkeypatch, requests_mock):
    """This test launch job to cluster and get job list by f7t."""
    client = app.test_client()
    userinfo_url = app.config["MP_USERINFO_URL"]
    expected_f7t_job_id = "00001"

    def mock_mkdir(cls, machine, target_path, p=None):
        return "mkdir!"

    def mock_submit(cls, machine, job_script, local_file=False):
        return {"jobid": expected_f7t_job_id}

    def mock_cancel(cls, machine, job_id):
        return "cancel!"

    # monkeypatch the mkdir/submit/cancel operation of f7t
    monkeypatch.setattr("firecrest.Firecrest.mkdir", MethodType(mock_mkdir, Firecrest))
    monkeypatch.setattr(
        "firecrest.Firecrest.submit", MethodType(mock_submit, Firecrest)
    )
    monkeypatch.setattr(
        "firecrest.Firecrest.cancel", MethodType(mock_cancel, Firecrest)
    )

    # moketpach the db
    monkeypatch.setattr("hpc_gateway.model.database.db", mock_db)

    requests_mock.get(userinfo_url, json=userinfo, status_code=200)

    # create user
    client.post("/api/v1/user/create", headers=auth_header)

    # create jobs
    response = client.post("/api/v1/job/create", headers=auth_header)
    job_id = response.json["jobid"]

    assert response.status_code == 200

    # test cancel but failed
    response = client.delete(f"/api/v1/job/cancel/{job_id}", headers=auth_header)

    assert response.status_code == 505

    # launch the job
    response = client.post(f"/api/v1/job/launch/{job_id}", headers=auth_header)

    assert response.status_code == 200

    job = mock_db.jobs.find_one({"_id": ObjectId(job_id)})
    assert job.get("state") == "ACTIVATED"
    assert job.get("f7t_job_id") == expected_f7t_job_id

    # cancel again and it works
    response = client.delete(f"/api/v1/job/cancel/{job_id}", headers=auth_header)

    assert response.status_code == 200


def test_list_job_repo(app, auth_header, userinfo, mock_db, monkeypatch, requests_mock):
    """This test launch job to cluster and get job list by f7t."""
    from hpc_gateway.api.job import JOB_SCRIPT_FILENAME

    client = app.test_client()
    userinfo_url = app.config["MP_USERINFO_URL"]

    def mock_mkdir(cls, machine, target_path, p=None):
        return "mkdir!"

    def mock_submit(cls, machine, job_script, local_file=False):
        return {"jobid": "00001"}

    def mock_list_files(cls, machine, target_path):
        return [
            {
                "group": "root",
                "last_modified": "2022-12-02T09:17:51",
                "link_target": "",
                "name": "e1000",
                "permissions": "rwxr-xr-x",
                "size": "20480",
                "type": "d",
                "user": "root",
            },
            {
                "group": "root",
                "last_modified": "2022-12-02T16:00:40",
                "link_target": "",
                "name": "snx3000",
                "permissions": "rwxr-xr-x",
                "size": "262144",
                "type": "d",
                "user": "root",
            },
            {
                "group": "user",
                "last_modified": "2022-12-03T09:17:51",
                "link_target": "",
                "name": "_job.sh",
                "permissions": "rwxr-xr-x",
                "size": "20480",
                "type": "f",
                "user": "userA",
            },
        ]

    # monkeypatch the mkdir/submit/cancel operation of f7t
    monkeypatch.setattr("firecrest.Firecrest.mkdir", MethodType(mock_mkdir, Firecrest))
    monkeypatch.setattr(
        "firecrest.Firecrest.submit", MethodType(mock_submit, Firecrest)
    )
    monkeypatch.setattr(
        "firecrest.Firecrest.list_files", MethodType(mock_list_files, Firecrest)
    )

    # moketpach the db
    monkeypatch.setattr("hpc_gateway.model.database.db", mock_db)

    requests_mock.get(userinfo_url, json=userinfo, status_code=200)

    # create user
    client.post("/api/v1/user/create", headers=auth_header)

    # create jobs
    response = client.post("/api/v1/job/create", headers=auth_header)
    job_id = response.json["jobid"]

    assert response.status_code == 200

    # test that the script is there.
    response = client.get(f"/api/v1/file/list/{job_id}", headers=auth_header)

    assert response.status_code == 200
    assert JOB_SCRIPT_FILENAME in [i["name"] for i in response.json["files"]]


def test_file_operations_repo(
    app, auth_header, userinfo, mock_db, monkeypatch, requests_mock
):
    """This test launch job to cluster and get job list by f7t."""
    _dummy_filename = "dummy.in"
    expected_download = b"download!!"

    client = app.test_client()
    userinfo_url = app.config["MP_USERINFO_URL"]

    def mock_mkdir(cls, machine, target_path, p=None):
        return "mkdir!"

    def mock_submit(cls, machine, job_script, local_file=False):
        return {"jobid": "00001"}

    def mock_simple_upload(cls, machine, source_path, target_path, filename):
        context = (
            open(source_path, "rb")
            if isinstance(source_path, str)
            or isinstance(source_path, pathlib.PosixPath)
            else nullcontext(source_path)
        )
        with context as f:
            _ = {"targetPath": target_path}
            _ = {"file": f}

        assert isinstance(f, bytes)

    def mock_simple_download(cls, machine, source_path, target_path):
        # mock that content is read from source_path
        content = expected_download
        context = (
            open(target_path, "wb")
            if isinstance(target_path, str)
            or isinstance(target_path, pathlib.PosixPath)
            else nullcontext(target_path)
        )
        with context as f:
            f.write(content)

    def mock_simple_delete(cls, machine, target_path):
        assert _dummy_filename in target_path
        return None

    # monkeypatch the mkdir/submit/cancel operation of f7t
    monkeypatch.setattr("firecrest.Firecrest.mkdir", MethodType(mock_mkdir, Firecrest))
    monkeypatch.setattr(
        "firecrest.Firecrest.submit", MethodType(mock_submit, Firecrest)
    )
    monkeypatch.setattr(
        "hpc_gateway.model.f7t.Firecrest.simple_upload",
        MethodType(mock_simple_upload, Firecrest),
    )
    monkeypatch.setattr(
        "firecrest.Firecrest.simple_delete", MethodType(mock_simple_delete, Firecrest)
    )
    monkeypatch.setattr(
        "firecrest.Firecrest.simple_download",
        MethodType(mock_simple_download, Firecrest),
    )

    # moketpach the db
    monkeypatch.setattr("hpc_gateway.model.database.db", mock_db)

    requests_mock.get(userinfo_url, json=userinfo, status_code=200)

    # create user
    client.post("/api/v1/user/create", headers=auth_header)

    # create jobs
    response = client.post("/api/v1/job/create", headers=auth_header)
    job_id = response.json["jobid"]

    assert response.status_code == 200

    # upload the dummy file
    dummy_file = f"tests/static/{_dummy_filename}"
    with open(dummy_file, "rb") as fh:
        data = {"file": (fh, f"{_dummy_filename}")}
        response = client.post(
            f"/api/v1/file/upload/{job_id}",
            buffered=True,
            data=data,
            content_type="multipart/form-data",
            headers=auth_header,
        )

    assert response.status_code == 200

    # download the dummy file
    response = client.get(
        f"/api/v1/file/download/{job_id}/{_dummy_filename}", headers=auth_header
    )

    assert response.status_code == 200
    assert response.data == expected_download

    # delete file
    response = client.delete(
        f"/api/v1/file/delete/{job_id}/{_dummy_filename}",
        headers=auth_header,
    )

    assert response.status_code == 200
