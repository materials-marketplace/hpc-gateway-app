"""This module serve as the model of the HPC gateway to interafcing for the
users and jobs collection of the DB."""

import bson

from flask import current_app, g
from werkzeug.local import LocalProxy
from flask_pymongo import PyMongo
from pymongo.errors import DuplicateKeyError, OperationFailure
from bson.objectid import ObjectId
from bson.errors import InvalidId

def get_db():
    """Configuration method to return db instance.
    """
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = PyMongo(current_app).db
        
    return db

# Use LocalProxy to read the global db instance with just `db`
db = LocalProxy(get_db)

"""
User: Create User

- create_user
"""

def create_user(email, name, home):
    """Insert a user into the users collection, with the following fields:
    
    - "name": will be used as the folder name, any special charater will convert to `_`.
    - "email": email of user.
    
    email is the exclusive key, can not have two users with the same email.
    If user already in the DB return it.
    """
    user = db.users.find_one({'email': email})
    if user:
        return user
    else:
        user_info = {'name': name, 'email': email, 'home': home}
        _id = db.users.insert_one(user_info).inserted_id
        user = db.users.find_one({'_id': _id})
        return user

"""
Job: Create/Update/Delete/Get simulation jobs

- create_job
- delete_job
- update_job: only for update the state of the job
    State can be:
    - CREATED: the job created but not launched
    - ATTACHED: the job has been trigger to run, there is no real state stored since
        the real state is read from remote on the fly by f7t.
"""

def create_job(user_id, remote_folder, repository):
    """Create job to DB.

    Args:
        user_id (str): attached user
        remote_folder (str): the remote folder name a uuid in user's repository folder
        repository (str): user's repository folder
    """
    state = "CREATED"
    job_info = {'user_id': user_id, 'remote_folder': remote_folder, 'repository': repository, 'state': state}
    _id = db.jobs.insert_one(job_info).inserted_id
    job = db.jobs.find_one({'_id': _id})
    
    return job

def update_job(job_id, state):
    """Update job state.
    """
    
    response = db.jobs.update_one(
        { "_id": job_id },
        { "$set": { "state": state } }
    )
    return response

def delete_job(job_id):
    """
    Given a job ID, deletes a job from the jobs collection
    """

    response = db.jobs.delete_one( { "_id": ObjectId(job_id) } )
    return response