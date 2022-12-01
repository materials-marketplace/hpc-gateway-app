import pytest
from firecrest import Firecrest
from types import MethodType

def test_index(client):
    response = client.get("/")
    assert "HPC gateway app for MarketPlace" in str(response.data)

# Tests of @token_required decorator
def test_auth_no_auth_fail(client):
    response = client.post("/api/v1/user/create")
    assert response.json['message'] == 'Authentication Token is missing!'
    
def test_auth_invalid_token(client):
    token = "invalid_token"
    headers = {
        "Accept": "application/json",
        "User-Agent": "HPC-app",
        "Authorization": f"Bearer {token}",
    }
    response = client.post("/api/v1/user/create", headers=headers)
    assert response.json['message'] == 'Invalid Authentication token!'
    
def test_auth_invalid_userinfo_url(app):
    token = 'invalid_token'
    mp_userinfo_url = "http://dummy.invalid"
    
    app.config.update({'MP_USERINFO_URL': mp_userinfo_url})
    client = app.test_client()
    
    headers = {
        "Accept": "application/json",
        "User-Agent": "HPC-app",
        "Authorization": f"Bearer {token}",
    }
    response = client.post("/api/v1/user/create", headers=headers)
    assert "Connection error" in response.json['message']
    
    
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
        'sub': '222-333', 
        'email_verified': False, 
        'roles': ['admin', 'user'], 
        'name': 'Jusong Yu', 
        'preferred_username': 'jusongyu', 
        'given_name': 'Jusong', 
        'family_name': 'Yu', 
        'email': 'jusong.yu@epfl.ch'
    }
    
    return info
    
# test of user API
def test_create_user(app, requests_mock, monkeypatch, mock_db, auth_header, userinfo):
    """Mock the f7t mkdir operation and create a db, we don't want
    the test have outside effect on the server."""
    client = app.test_client()
    userinfo_url = app.config['MP_USERINFO_URL']
    
    def mock_mkdir(cls, machine, target_path, p=None):
        return "mkdir!"
    
    # monkeypatch the mkdir operation of f7t
    monkeypatch.setattr('firecrest.Firecrest.mkdir', MethodType(mock_mkdir, Firecrest))
    
    # moketpach the db
    monkeypatch.setattr('hpc_gateway.model.database.db', mock_db)
    
    requests_mock.get(userinfo_url, json=userinfo, status_code=200)
    response = client.post("/api/v1/user/create", headers=auth_header)
    
    rjson = response.json
    assert rjson['home'] == '/scratch/f7t/jusong_yu'
    assert rjson['message'] == 'Success: Create user in database.'
    
# test job APIs
def test_create_job(app, auth_header, userinfo, mock_db, monkeypatch, requests_mock):
    client = app.test_client()
    userinfo_url = app.config['MP_USERINFO_URL']
    
    def mock_mkdir(cls, machine, target_path, p=None):
        return "mkdir!"
    
    # monkeypatch the mkdir operation of f7t
    monkeypatch.setattr('firecrest.Firecrest.mkdir', MethodType(mock_mkdir, Firecrest))
    
    # moketpach the db
    monkeypatch.setattr('hpc_gateway.model.database.db', mock_db)
    
    requests_mock.get(userinfo_url, json=userinfo, status_code=200)
    
    # create user
    client.post("/api/v1/user/create", headers=auth_header)
    
    # create jobs
    response = client.post("/api/v1/job/create", headers=auth_header)
    job_id = response.json['jobid']

    assert response.status_code == 200

    # create another job
    client.post("/api/v1/job/create", headers=auth_header)
    
    # get jobs
    response = client.get("/api/v1/job/", headers=auth_header)
    assert job_id in response.json
    
def test_launch_get_job():
    """This test launch job to cluster and get job list by f7t."""
    # # create another job
    # client.post("/api/v1/job/create", header=auth_header)
    
    # # get jobs
    # response = client.get("/api/v1/job/", header=auth_header)
    # assert job_id in response.json