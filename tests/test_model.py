import mongomock
import pymongo
import pytest
import uuid
from bson.binary import UuidRepresentation

from hpc_gateway.model import database

@pytest.fixture(scope="session")
@mongomock.patch(servers=(('server.example.com', 27017),))
def mock_db():
    """This fixture last for whole test session, the db will not destroy 
    until the end of pytest"""
    client = pymongo.MongoClient(host='server.example.com')
    db = client._database
    return db
    
    

def test_create_user(monkeypatch, mock_db):
    monkeypatch.setattr('hpc_gateway.model.database.db', mock_db)
    
    name = "test"
    email = "test@test.com"
    user = database.create_user(email, name)
    
    find_user = mock_db.users.find_one({"email": email})
    
    assert user.inserted_id == find_user['_id']
    assert find_user['name'] == name
    
def test_create_job(monkeypatch, mock_db):
    monkeypatch.setattr('hpc_gateway.model.database.db', mock_db)
    
    user_id = 'an_id_for_test'
    
    remote_folder = str(uuid.uuid4())
    repository = 'tmp_user'
    
    job = database.create_job(user_id, remote_folder, repository)
    find_job = mock_db.jobs.find_one({"remote_folder": remote_folder})
    
    assert job.inserted_id == find_job['_id']
    assert find_job['state'] == 'CREATED'
    assert find_job['remote_folder'] == remote_folder
    assert find_job['repository'] == repository
    
def test_update_job(monkeypatch, mock_db):
    monkeypatch.setattr('hpc_gateway.model.database.db', mock_db)
    
    user_id = 'an_id_for_test'
    
    remote_folder = str(uuid.uuid4())
    repository = 'tmp_user'
    
    job = database.create_job(user_id, remote_folder, repository)
    job_id = job.inserted_id
    
    updated_state = "ATTACHED"
    database.update_job(job_id, state=updated_state)
    
    find_job = mock_db.jobs.find_one({"remote_folder": remote_folder})
    assert find_job['state'] == updated_state
    assert find_job['repository'] == repository


def test_delete_job(monkeypatch, mock_db):
    monkeypatch.setattr('hpc_gateway.model.database.db', mock_db)
    
    user_id = 'an_id_for_test'
    
    remote_folder = str(uuid.uuid4())
    repository = 'tmp_user'
    
    job = database.create_job(user_id, remote_folder, repository)
    job_id = job.inserted_id
    
    count_before_delete = mock_db.jobs.count_documents({})
    database.delete_job(job_id)
    count_after_delete = mock_db.jobs.count_documents({})
    
    assert count_before_delete - count_after_delete == 1