def test_index(client):
    response = client.get("/")
    assert "HPC gateway app for MarketPlace" in str(response.data)

def test_request_no_auth_fail(client):
    response = client.post("/api/v1/user/create")
    assert response.json['message'] == 'Authentication Token is missing!'
    
def test_request_invalid_token(client):
    token = "invalid_token"
    headers = {
        "Accept": "application/json",
        "User-Agent": "HPC-app",
        "Authorization": f"Bearer {token}",
    }
    response = client.post("/api/v1/user/create", headers=headers)
    assert response.json['message'] == 'Invalid Authentication token!'
    
def test_request_invalid_userinfo_url(app):
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
    
    