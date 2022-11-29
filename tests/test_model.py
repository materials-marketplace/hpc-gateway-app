import mongomock
import pytest

from hpc_gateway import model

def test_create_user():
    client = mongomock.MongoClient()
    db = client.test_database
    
    name = "test"
    email = "test@test.com"
    user = model.User().create(name=name, email=email)
    
    print(user)
    
    print(model.User.get_all())
    