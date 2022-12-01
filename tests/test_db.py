import uuid
import pytest
import os
from hpc_gateway.model import database

@pytest.fixture()
def remote_folder():
    fd = os.path.join('/tmp', str(uuid.uuid4()))

    return fd

def test_create_and_get_user(monkeypatch, mock_db):
    monkeypatch.setattr('hpc_gateway.model.database.db', mock_db)
    
    name = "test"
    email = "test@test.com"
    user = database.create_user(email, name, '/home')
    
    find_user = mock_db.users.find_one({"email": email})
    
    assert user == find_user
    assert find_user['name'] == name
    
    assert database.get_user(email=email) == find_user

def test_create_user_exist(monkeypatch, mock_db):
    monkeypatch.setattr('hpc_gateway.model.database.db', mock_db)
    
    home = '/home'
    name = "test"
    name2 = "name2"
    email = "test@test.com"
    user1 = database.create_user(email, name, home)
    user2 = database.create_user(email, name2, home)
    
    assert user1 == user2
    
    # even though the name2 is used but since the data exist 
    # the original user returned.
    assert user2['name'] == name
    
def test_create_job(monkeypatch, mock_db, remote_folder):
    monkeypatch.setattr('hpc_gateway.model.database.db', mock_db)
    
    user_id = 'an_id_for_test'
    
    job = database.create_job(user_id, remote_folder)
    find_job = mock_db.jobs.find_one({"remote_folder": remote_folder})
    
    assert job == find_job
    assert find_job['state'] == 'CREATED'
    assert find_job['remote_folder'] == remote_folder
    
def test_update_job(monkeypatch, mock_db, remote_folder):
    monkeypatch.setattr('hpc_gateway.model.database.db', mock_db)
    
    user_id = 'an_id_for_test'

    job = database.create_job(user_id, remote_folder)
    job_id = job.get('_id')
    
    f7t_job_id = '00'
    database.update_job(job_id, f7t_job_id=f7t_job_id)
    
    find_job = mock_db.jobs.find_one({"remote_folder": remote_folder})
    assert find_job['state'] == "ACTIVATED"
    assert find_job['remote_folder'] == remote_folder
    assert find_job['f7t_job_id'] == f7t_job_id


def test_delete_job(monkeypatch, mock_db, remote_folder):
    monkeypatch.setattr('hpc_gateway.model.database.db', mock_db)
    
    user_id = 'an_id_for_test'
    
    job = database.create_job(user_id, remote_folder)
    job_id = job.get('_id')
    
    count_before_delete = mock_db.jobs.count_documents({})
    database.delete_job(job_id)
    count_after_delete = mock_db.jobs.count_documents({})
    
    assert count_before_delete - count_after_delete == 1
    
def test_get_jobs(monkeypatch, mock_db, remote_folder):
    monkeypatch.setattr('hpc_gateway.model.database.db', mock_db)
    
    user_id = 'an_id_for_test'
    
    database.create_job(user_id, remote_folder)
    database.create_job(user_id, remote_folder)
    
    database.get_jobs(user_id)