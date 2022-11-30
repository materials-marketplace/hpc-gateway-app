import mongomock
import pymongo
import pytest

from hpc_gateway.model import database

@mongomock.patch(servers=(('server.example.com', 27017),))
def test_create_user(monkeypatch):
    client = pymongo.MongoClient('server.example.com')
    fake_db = client._database
    
    monkeypatch.setattr('hpc_gateway.model.database.db', fake_db)
    
    name = "test"
    email = "test@test.com"
    user = database.create_user(email, name)
    
    find_user = fake_db.users.find_one({"email": email})
    
    assert user.inserted_id == find_user['_id']
    assert find_user['name'] == name
    