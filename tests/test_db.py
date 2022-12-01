import uuid

from hpc_gateway.model import database

def test_create_user(monkeypatch, mock_db):
    monkeypatch.setattr('hpc_gateway.model.database.db', mock_db)
    
    name = "test"
    email = "test@test.com"
    user = database.create_user(email, name, '/home')
    
    find_user = mock_db.users.find_one({"email": email})
    
    assert user == find_user
    assert find_user['name'] == name
    
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
    
def test_create_job(monkeypatch, mock_db):
    monkeypatch.setattr('hpc_gateway.model.database.db', mock_db)
    
    user_id = 'an_id_for_test'
    
    remote_folder = str(uuid.uuid4())
    repository = 'tmp_user'
    
    job = database.create_job(user_id, remote_folder, repository)
    find_job = mock_db.jobs.find_one({"remote_folder": remote_folder})
    
    assert job == find_job
    assert find_job['state'] == 'CREATED'
    assert find_job['remote_folder'] == remote_folder
    assert find_job['repository'] == repository
    
def test_update_job(monkeypatch, mock_db):
    monkeypatch.setattr('hpc_gateway.model.database.db', mock_db)
    
    user_id = 'an_id_for_test'
    
    remote_folder = str(uuid.uuid4())
    repository = 'tmp_user'
    
    job = database.create_job(user_id, remote_folder, repository)
    job_id = job.get('_id')
    
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
    job_id = job.get('_id')
    
    count_before_delete = mock_db.jobs.count_documents({})
    database.delete_job(job_id)
    count_after_delete = mock_db.jobs.count_documents({})
    
    assert count_before_delete - count_after_delete == 1