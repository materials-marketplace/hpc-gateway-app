def test_index(client):
    response = client.get("/")
    assert "HPC gateway app for MarketPlace" in str(response.data)

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
    
def test_create_user(app, requests_mock, monkeypatch, mock_db):
    """Mock the f7t mkdir operation and create a db, we don't want
    the test have outside effect on the server."""
    from firecrest import Firecrest
    from types import MethodType
    
    token = 'valid_token'
    client = app.test_client()
    
    headers = {
        "Accept": "application/json",
        "User-Agent": "HPC-app",
        "Authorization": f"Bearer {token}",
    }
    userinfo_url = app.config['MP_USERINFO_URL']
    mock_user = {
        'sub': '222-333', 
        'email_verified': False, 
        'roles': ['admin', 'user'], 
        'name': 'Jusong Yu', 
        'preferred_username': 'jusongyu', 
        'given_name': 'Jusong', 
        'family_name': 'Yu', 
        'email': 'jusong.yu@epfl.ch'
    }
    
    def mock_mkdir(cls, machine, target_path, p=None):
        return "mkdir!"
    
    # monkeypatch the mkdir operation of f7t
    monkeypatch.setattr('firecrest.Firecrest.mkdir', MethodType(mock_mkdir, Firecrest))
    
    # moketpach the db
    monkeypatch.setattr('hpc_gateway.model.database.db', mock_db)
    
    requests_mock.get(userinfo_url, json=mock_user, status_code=200)
    response = client.post("/api/v1/user/create", headers=headers)
    
    rjson = response.json
    assert rjson['home'] == '/scratch/f7t/jusong_yu'
    assert rjson['message'] == 'Success: Create user in database.'