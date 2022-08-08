from email import message
import os
import io
import sys
import threading
import uuid
import logging
from logging.handlers import TimedRotatingFileHandler
import requests

from flask import Flask, request, jsonify, g
from flask import send_file
from flask import Flask, flash, request, render_template
from werkzeug.utils import secure_filename
import firecrest as f7t

from hpc_gateway.f7t import HardCodeTokenAuth
from hpc_gateway.models import Jobs, User
from hpc_gateway.auth_middleware import token_required

from dotenv import load_dotenv

# # Only test need load_dotenv
# load_dotenv("./deploy/common.env")

# Checks if an environment variable injected to F7T is a valid True value
# var <- object
# returns -> boolean
def get_boolean_var(var):
    # ensure variable to be a string
    var = str(var)
    # True, true or TRUE
    # Yes, yes or YES
    # 1

    return var.upper() == "TRUE" or var.upper() == "YES" or var == "1"

debug = get_boolean_var(os.environ.get("HPCGATEWAY_DEBUG_MODE", False))
USE_SSL = get_boolean_var(os.environ.get("HPCGATEWAY_USE_SSL", False))

# WHITE_LIST = ['jusong.yu@epfl.ch', 'andreas.aigner@dcs-computing.com', 'simon.adorf@epfl.ch']
# Setup the client for the specific account
# Create an authorization object with Client Credentials authorization grant
    
hardcode = HardCodeTokenAuth(
    token=os.environ.get("F7T_TOKEN"),
)

# Setup the client for the specific account
f7t_client = f7t.Firecrest(
    firecrest_url=os.environ.get("F7T_URL"), 
    authorization=hardcode,
)

MACHINE = os.environ.get("HPC_MACHINE_NAME")
EXEC_HOME_FOLDER = os.environ.get("EXEC_HOME_FOLDER")

def allowed_file(filename):
    # TODO check file size < 10 MB
    return '.' in filename and True

app = Flask(__name__)

def email2repo(email):
    """Since the username allowed space character contained it is not proper to be 
    directly used as repo (folder) name
    this helper function will convert space to underscore"""
    username = email.split('@')[0] # get username of email
    repo = username.replace('.', '_')
    
    return repo

###################### 
# ONLY FOR TEST
# PLEASE REMOVE US WHEN RELEASE
@app.route("/broker")
def broker():
    resp = {'test': 'DONE!'}
    
    return resp, 200

@app.route("/f7ttest", methods=["GET"])
def f7ttest():
    parameters = f7t_client.parameters()
    
    return jsonify(parameters=parameters), 200

@app.route("/dbtest")
def dbtest():
    name = "jason"
    email = "j.y@ca.h"
    try:
        # user name and email validate
        user = User().create(name=name, email=email)
    except Exception as e:
        return {
            'error': 'failed to create user in DB.'
        }, 500
        
    user_get = User().get_by_email(email=email)
    return jsonify(user_get=user_get, user=user), 200
## TEST ONLY
#######################
    
@app.route("/")
@token_required
def heartbeat(current_user):
    user = User().get_by_email(current_user['email'])
    if not user:
        return jsonify(
            message='user not create yet, please register for DB first time.',
        ), 401
    else: 
        repo = email2repo(current_user['email'])
        target_path = os.path.join(EXEC_HOME_FOLDER, repo)
        
        try:
            resp = f7t_client.list_files(machine=MACHINE, target_path=target_path)
        except Exception as exc:
            return jsonify(
                message='User is available in DB but cluster not available.',
                error=str(exc),
            ), 401
        else:
            return jsonify(
                output=resp,
                message='system is ready for you, HAPPY COMPUTING!',
            ), 200
            


@app.route("/user", methods=["GET"])
@token_required
def get_user(current_user):
    user = User().get_by_email(current_user['email'])
    if user:
        return jsonify(
            user=user,
            message=f"DB user {user} with repo {email2repo(current_user['email'])}",
            mp_user=current_user,
        ), 200
    else:
        return jsonify(
            error=f'User {current_user} not registered.',
        ), 401

@app.route("/user", methods=["POST"])
@token_required
def create_user(current_user):
    try:
        email = current_user['email']
        name = current_user['name']
        
        try:
            # user name and email validate
            user = User().create(name=name, email=email)
        except Exception as e:
            return jsonify(
                error='failed to create user in DB.'
            ), 500
            
        # user are created or aready exist (None return from create method)
        if user:
            # create the repository for user to store file
            repo = email2repo(email)
            repo_path = os.path.join(EXEC_HOME_FOLDER, repo)
            app.logger.debug(f"Will create repo at {repo_path}")
            app.logger.debug(f"machine={MACHINE}, path={repo_path}")
            f7t_client.mkdir(machine=MACHINE, target_path=repo_path)
            
            # New db user created
            return jsonify(
                message='New database and repository are created.',
                name=name,
                email=email,
                id=user['_id'],
            ), 200

        else:
             # Already exist in DB
            user = User().get_by_email(email=email)
            return jsonify(
                message=f'User {user} already registered in database.',
            ), 200
    except Exception as e:    
        return {
            "error": "Something went wrong",
            "message": str(e)
        }, 500
        

@app.route("/jobs/new", methods=["POST"])
@token_required
def create_job(current_user):
    """This will essentially create a workdir in user repo
    and return the folder name as resourceid"""
    repo = email2repo(current_user['email'])
    
    # the folder name (resource) is a 
    resourceid = str(uuid.uuid4())
    
    try:
        target_path = os.path.join(EXEC_HOME_FOLDER, repo, resourceid)
        f7t_client.mkdir(machine=MACHINE, target_path=target_path)
    except Exception as e:
        return jsonify(
            entry_point="create_job",
            error=f"unable to mkdir {target_path}",
            error_message=str(e),
        ), 500
    else:
        return jsonify(
            resourceid=resourceid,
        ), 200

@app.route("/jobs/run/<resourceid>", methods=["POST"])
@token_required
def run_job(current_user, resourceid):
    """Submit job from the folder and return jobid"""
    repo = email2repo(current_user['email'])
    
    workdir = os.path.join(EXEC_HOME_FOLDER, repo, resourceid)
    
    script_path = os.path.join(workdir, 'submit.sh')
    if 'submit.sh' not in f7t_client.list_files(machine=MACHINE, target_path=workdir):
        return jsonify(
            error="job script 'submit.sh' not uploaded yet."
        )
        
    try:
        resp = f7t_client.submit(machine=MACHINE, job_script=script_path, local_file=False)
        user = User().get_by_email(current_user['email'])
        userid = user['_id']
        jobid = resp.get('jobid')
        job = Jobs().create(userid=userid, jobid=jobid, resourceid=resourceid)
        
        resp['userid'] = job['userid']
        resp['jobid'] = job['jobid']
        resp['resourceid'] = job['resourceid']
        
        return resp, 200
        
    except Exception as e:
        return {
            "function": 'submit',
            "error": "Something went wrong",
            "message": str(e)
        }, 500

# still use resourceid for job manipulation it will map to the jobid internally
@app.route("/jobs/cancel/<resourceid>", methods=["POST"])
@token_required
def cancel_job(current_user, resourceid):
    """Submit job from the folder and return jobid"""
    try:
        user = User().get_by_email(current_user['email'])
        userid = user['_id']
        jobid = Jobs().get_by_userid_and_resourceid(userid=userid, resourceid=resourceid).get('jobid')
        
        app.logger.debug(userid)
        app.logger.debug(jobid)
        
        resp = f7t_client.cancel(machine=MACHINE, jobid=jobid)
        
        # update the state of job entity in db, state to cancel.
        Jobs.update(jobid=jobid, state='cancel')
        
    except Exception as e:
        return {
            "function": 'cancel',
            "error": "Something went wrong",
            "message": str(e)
        }, 500
    else:    
        return resp, 200

@app.route("/jobs/delete/<resourceid>", methods=["DELETE"])
@token_required
def delete_job(current_user, resourceid):
    """Delete job from list jobid DB. This will not actually delete the
    remote folder but simply remove the entity from DB list to unlink. 
    The remote folder in the /scratch should be cleanup in period by setting in HPC.
    """
    try:
        user = User().get_by_email(current_user['email'])
        userid = user['_id']
        jobid = Jobs().get_by_userid_and_resourceid(userid=userid, resourceid=resourceid).get('jobid')
        
        app.logger.debug(userid)
        app.logger.debug(jobid)
        
        # simply delete DB entity from the list, no matter how is the job state.
        # Need to added in future that job must not in running states first. TODO.
        r = Jobs().delete(jobid=jobid)
        
    except Exception as e:
        return {
            "function": 'delete_job',
            "error": "Something went wrong",
            "message": str(e)
        }, 500
    else:
        return {
            "function": 'delete_job',
            "message": f"job {jobid} of {resourceid} detached from DB."    
        }, 200
        
@app.route("/jobs/", methods=["GET"])
@token_required
def list_jobs(current_user):
    user = User().get_by_email(current_user['email'])
    userid = user['_id']
    
    jobs = Jobs().get_joblist_by_userid(userid)
    app.logger.debug(userid)
    app.logger.debug(jobs)
    if not jobs:
        return f"no jobs in list of user {user['name']}", 400
        
    try:
        fresp = f7t_client.poll(machine=MACHINE, jobs=jobs)
    except Exception as e:
        raise e
    
    return fresp, 200

@app.route("/download/<resourceid>", methods=["GET"])
@token_required
def download_remote(current_user, resourceid):
    """
    Downloads the remote files from the cluster.
    :param path: path string relative to the parent ROOT_PATH=`/scratch/snx3000/jyu/firecrest/`
    :return: file.
    """
    repo = email2repo(current_user['email'])
    
    data = request.json
    filename = data.get('filename')
    source_path = os.path.join(EXEC_HOME_FOLDER, repo, resourceid, filename)
    app.logger.debug(source_path)
    binary_stream = io.BytesIO()
    
    try:
        f7t_client.simple_download(machine=MACHINE, source_path=source_path, target_path=binary_stream)

        download_name = os.path.basename(filename)
        binary_stream.seek(0) # buffer position from start
        resp = send_file(path_or_file=binary_stream, download_name=download_name)
    except Exception as exc:
        return {"message": f"Failed with {exc}"}, 402
    else:
        return resp, 200

@app.route("/list/<resourceid>", methods=["GET"])
@token_required
def list_remote(current_user, resourceid):
    """
    list the remote files of resourceid folder from the cluster.
    :param path: path string relative to the parent EXEC_HOME_FOLDER
    :return: list of files.
    """
    repo = email2repo(current_user['email'])
    
    data = request.json or {}
    filename = data.get('filename', '.')
    target_path = os.path.join(EXEC_HOME_FOLDER, repo, resourceid, filename)
    
    try:
        resp = f7t_client.list_files(machine=MACHINE, target_path=target_path)
    except Exception as exc:
        return {"message": f"Failed with {exc}"}, 402
    else:
        return jsonify(
            output=resp,
        ), 200

@app.route("/upload/<resourceid>", methods=["PUT"])
@token_required
def upload_remote(current_user, resourceid):
    """
    Upload the file to the cluster. to folder EXEC_HOME_FOLDER
    """
    repo = email2repo(current_user['email'])
    
    if 'file' not in request.files:
        flash('No file part')
        return jsonify({
            "message": "No file part",
            "error": str('error'),
            "data": None
        }), 403
        
    file = request.files['file']
    target_path = os.path.join(EXEC_HOME_FOLDER, repo, resourceid)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        binary_stream = io.BytesIO(file.read())
        
        resp = f7t_client.simple_upload(
            machine=MACHINE, 
            binary_stream=binary_stream, 
            target_path=target_path, 
            # filename=filename,    problem with F7T API for this.
        )
    
        return resp, 200
        
@app.route("/delete/<resourceid>", methods=["DELETE"])
@token_required
def delete_remote(current_user, resourceid):
    """
    Will be map to deleteDataset Downloads the remote files from the cluster.
    This is for delete a singlefile in the resource.
    
    :param path: path string relative to the parent ROOT_PATH=`/scratch/snx3000/jyu/firecrest/`
    :return: file.
    """
    repo = email2repo(current_user['email'])
    
    data = request.json
    filename = data.get('filename')
    target_path = os.path.join(ROOT_FOLDER, repo, resourceid, filename)
    
    try:
        f7t_client.simple_delete(target_path=target_path)
    except Exception as exc:
        return {"message": f"Failed with {exc}"}, 402
    else:
        return {"message": f"Delete the file {filename} from {resourceid}"}, 200


@app.errorhandler(403)
def forbidden(e):
    return jsonify({
        "message": "Forbidden",
        "error": str(e),
        "data": None
    }), 403

@app.errorhandler(404)
def forbidden(e):
    return jsonify({
        "message": "Endpoint Not Found",
        "error": str(e),
        "data": None
    }), 404
    
# formatter is executed for every log
class LogRequestFormatter(logging.Formatter):
    def format(self, record):
        try:
            # try to get TID from Flask g object, it's set on @app.before_request on each microservice
            record.TID = g.TID
        except:
            try:
                record.TID = threading.current_thread().name
            except:
                record.TID = 'notid'

        return super().format(record)


if __name__ == "__main__":
    LOG_PATH = os.environ.get("HPCGATEWAY_LOG_PATH", "./deploy/logs/hpc-gateway")
    # timed rotation: 1 (interval) rotation per day (when="D")
    logHandler = TimedRotatingFileHandler(f'{LOG_PATH}/gw.log', when='D', interval=1)

    logFormatter = LogRequestFormatter('%(asctime)s,%(msecs)d %(thread)s [%(TID)s] %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                                    '%Y-%m-%dT%H:%M:%S')
    logHandler.setFormatter(logFormatter)

    # get app log (Flask+werkzeug+python)
    logger = logging.getLogger()

    # set handler to logger
    logger.addHandler(logHandler)
    logging.getLogger().setLevel(logging.DEBUG)

    # disable Flask internal logging to avoid full url exposure
    logging.getLogger('werkzeug').propagate = False
        
    if USE_SSL:
        app.run(debug=debug, host='0.0.0.0', port=5253, ssl_context='adhoc')
    else:
        app.run(debug=debug, host='0.0.0.0', port=5253)
