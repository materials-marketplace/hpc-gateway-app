"""Application Models"""
import os

import bson
from pymongo import MongoClient

# The CSCS HPC-GW test deploymet DB server is held on https://cloud.mongodb.com/v2
DATABASE_URL = os.environ.get("HPCGATEWAY_MONGO_URL")
client = MongoClient(DATABASE_URL)

if os.environ.get("F7T_TOKEN", None) is not None:
    # The IWM deploy
    db = client.iwm_hpc
else:
    # The CSCS deploy
    db = client.cscs_hpc


class Jobs:
    """Jobs Model

    jobid is unique and the _id of entity is the objectId of jobid
    resourceid is generate in hpc-app. Should be unique, but for assurance,
    find it with userid.
    """

    def __init__(self):
        return

    def get_by_jobid(self, jobid):
        """Get a job given its jobid"""
        job = db.jobs.find_one({"jobid": jobid})
        if not job:
            return None

        return job

    def create(self, userid: str, jobid: str, resourceid: str):
        """Create a new job in DB"""
        job = self.get_by_jobid(jobid)
        if job:
            # the job exist return None do nothing
            return None
        new_job = db.jobs.insert_one(
            {
                "jobid": jobid,
                "userid": userid,
                "resourceid": resourceid,
                # TODO: more metadata (ctime, mtime ..)
            }
        )
        job = db.jobs.find_one({"_id": new_job.inserted_id})

        return self.get_by_jobid(job["jobid"])

    def get_by_userid_and_resourceid(self, userid, resourceid):
        """with resourceid I can retrace back to find jobid"""
        job = db.jobs.find_one({"userid": userid, "resourceid": resourceid})
        if not job:
            return None

        return job

    def update(self, jobid, state):
        data = {"state": state}
        job = db.jobs.update_one({"_id": bson.ObjectId(jobid)}, {"$set": data})
        job = self.get_by_id(jobid)
        return job

    def get_joblist_by_userid(self, userid):
        """Get all jobs created by a user return a list of jobid belong to this user"""
        jobs = db.jobs.find({"userid": userid})
        return [job.get("jobid") for job in jobs]

    def delete(self, jobid):
        """Remove the entity from the list."""
        db.jobs.delete_one({"jobid": jobid})

        return jobid


class User:
    """User Model"""

    def __init__(self):
        self.db = db
        return

    def create(self, name="", email=""):
        """Create a new user"""
        user = self.get_by_email(email)
        if user:
            return
        new_user = db.users.insert_one(
            {
                "name": name,
                "email": email,
                "active": True,
            }
        )
        return self.get_by_id(new_user.inserted_id)

    def get_all(self):
        """Get all users"""
        users = db.users.find({"active": True})
        return [{**user, "_id": str(user["_id"])} for user in users]

    def get_by_id(self, userid):
        """Get a user by id"""
        user = db.users.find_one({"_id": bson.ObjectId(userid), "active": True})
        if not user:
            return
        user["_id"] = str(user["_id"])
        return user

    def get_by_email(self, email):
        """Get a user by email"""
        user = db.users.find_one({"email": email, "active": True})
        if not user:
            return
        user["_id"] = str(user["_id"])
        return user

    def update(self, userid, name=""):
        """Update a user"""
        data = {}
        if name:
            data["name"] = name
        user = db.users.update_one({"_id": bson.ObjectId(userid)}, {"$set": data})
        user = self.get_by_id(userid)
        return user

    def disable_account(self, userid):
        """Disable a user account"""
        user = db.users.update_one(
            {"_id": bson.ObjectId(userid)}, {"$set": {"active": False}}
        )
        user = self.get_by_id(userid)
        return user
