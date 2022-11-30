import mongomock
import pymongo
import pytest

from hpc_gateway.model import database

@pytest.fixture(scope="function")
@mongomock.patch(servers=(('server.example.com', 27017),))
def mock_db():
    client = pymongo.MongoClient('server.example.com')
    db = client._database
    
    return db

@mongomock.patch(servers=(('server.example.com', 27017),))
def test_create_user(monkeypatch, mock_db):
    monkeypatch.setattr('hpc_gateway.model.database.db', mock_db)
    
    name = "test"
    email = "test@test.com"
    user = database.create_user(email, name)
    
    find_user = mock_db.users.find_one({"email": email})
    
    assert user.inserted_id == find_user['_id']
    assert find_user['name'] == name
    
