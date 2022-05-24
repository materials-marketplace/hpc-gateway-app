import jwt, os
import io
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask import Response, stream_with_context
from flask import send_file
from firecrest_sdk import Firecrest
import requests
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import uuid

load_dotenv()

WHITE_LIST = ['jusong.yu@epfl.ch', 'andreas.aigner@dcs-computing.com', 'simon.adorf@epfl.ch']
# Setup the client for the specific account
client = Firecrest(firecrest_url="https://firecrest.cscs.ch/")
ROOT_FOLDER = '/scratch/snx3000/jyu/firecrest/'

ALLOWED_EXTENSIONS = {'txt', 'sh', 'in', 'sif', 'stl', 'asx', 'lic'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
SECRET_KEY = os.environ.get('SECRET_KEY') or 'this is a secret'
print(SECRET_KEY)

app.config['SECRET_KEY'] = SECRET_KEY
app.config['ROOT_FOLDER'] = ROOT_FOLDER

from models import Jobs, User
from auth_middleware import token_required

def helper_get_db_userid(mp_user):
    pass

def email2repo(email):
    """Since the username allowed space character contained it is not proper to be 
    directly used as repo (folder) name
    this helper function will convert space to underscore"""
    username = email.split('@')[0] # get username of email
    repo = username.replace('.', '_')
    
    return repo
    
@app.route("/")
@token_required
def heartbeat(current_user):
    user = User().get_by_email(current_user['email'])
    if not user:
        resp = {
            'message': 'user not create yet, please register for DB first time.'
        }
        return resp, 401
    else: 
        resp = {
            'message': 'user is available.'
        }
        try:
            fresp = client.heartbeat()
            resp.update(fresp)
        except Exception as e:
            raise e
    
    return resp, 200

@app.route("/login/")
def frontend():
    return render_template('index.html')

@app.route("/resource-request/", methods=["POST"])
def resource_request():
    return 'request sent', 200

@app.route("/userinfo/", methods=["GET"])
@token_required
def get_userinfo(current_user):
    user = User().get_by_email(current_user['email'])
    if user:
        resp = {
            'db_user': user,
            'marketplace_user': current_user,
        }
    else:
        resp = {
            'db_user': 'NOT AVAILABLE',
            'marketplace_user': current_user,
        }
    
    return resp, 200

@app.route('/doregister', methods=['POST'])
def doregister():
    access_token = request.form['access_token']
    headers = {
        "Accept": "application/json",
        "User-Agent": "HPC-app",
        "Authorization": f"Bearer {access_token}",
    }
    resp = requests.get(
        f'{request.url_root}/register/',
        headers=headers,
        verify=None,
    )
    resp, status_code = resp.json(), resp.status_code
    if status_code < 300:
        return resp['message'], status_code
    else:
        return resp['error'], status_code


@app.route("/register/", methods=["GET"])
@token_required
def register(current_user):
    try:
        email = current_user['email']
        name = current_user['name']
        if email in WHITE_LIST:
            try:
                # user name and email validate
                user = User().create(name=name, email=email)
            except Exception as e:
                return {
                    'error': 'failed to create user in DB.'
                }, 500
        else:
            return {
                'error': f'User <{name}> is not allowed to access database.'
            }, 406
            
        # user are created or aready exist (None return from create method)
        if user:
            # create the repository for user to store file
            repo = email2repo(email)
            client.mkdir(target_path=os.path.join(app.config['ROOT_FOLDER'], repo))
            
            # New db user created
            resp = {
                'message': 'New database and repository are created.',
                'data': {
                    'name': name,
                    'email': email,
                    '_id': user['_id']
                }
            } 
            return resp, 200
        else:
             # Already exist in DB
            return {
                'message': 'Already registered in database.'
            }, 200
    except Exception as e:    
        return {
            "error": "Something went wrong",
            "message": str(e)
        }, 500
        

@app.route("/jobs/new", methods=["POST"])
@token_required
def create_job(current_user):
    """This will essentially create a workdir in user repo
    and return the folder name as resourceId"""
    repo = email2repo(current_user['email'])
    
    # the folder name (resource) is a 
    resource = str(uuid.uuid4())
    
    try:
        target_path = os.path.join(app.config['ROOT_FOLDER'], repo, resource)
        client.mkdir(target_path=target_path)
    except Exception as e:
        return {
            "function": 'create_job',
            "error": f"unable to mkdir {target_path}",
            "message": str(e)
        }, 500
    else:
        return {
            'resourceId': resource,
        }, 200

@app.route("/jobs/run/<resource>", methods=["POST"])
@token_required
def run_job(current_user, resource):
    """Submit job from the folder and return jobid"""
    repo = email2repo(current_user['email'])
    
    workdir = os.path.join(ROOT_FOLDER, repo, resource)
    
    script_path = os.path.join(workdir, 'submit.sh')
    # TODO: check (error return code) the job script exist
    try:
        resp = client.submit(job_script=script_path)
        user = User().get_by_email(current_user['email'])
        userid = user['_id']
        jobid = resp.get('jobid')
        job = Jobs().create(userid=userid, jobid=jobid)
        
        resp['userid'] = job['userid']
        
    except Exception as e:
        return {
            "function": 'submit',
            "error": "Something went wrong",
            "message": str(e)
        }, 500
        
    return resp, 200
        
@app.route("/jobs/", methods=["GET"])
@token_required
def list_jobs(current_user):
    user = User().get_by_email(current_user['email'])
    userid = user['_id']
    
    jobs = Jobs().get_by_userid(userid)
    app.logger.debug(userid)
    app.logger.debug(jobs)
    if not jobs:
        return f"no jobs in list of user {user['name']}", 400
        
    try:
        fresp = client.poll(jobs=jobs)
    except Exception as e:
        raise e
    
    return fresp, 200

@app.route("/download/<resource>", methods=["GET"])
@token_required
def download_remote(current_user, resource):
    """
    Downloads the remote files from the cluster.
    :param path: path string relative to the parent ROOT_PATH=`/scratch/snx3000/jyu/firecrest/`
    :return: file.
    """
    repo = email2repo(current_user['email'])
    
    data = request.json
    filename = data.get('filename')
    source_path = os.path.join(ROOT_FOLDER, repo, resource, filename)
    app.logger.debug(source_path)
    binary_stream = io.BytesIO()
    
    client.simple_download(source_path=source_path, target_path=binary_stream)

    download_name = os.path.basename(filename)
    binary_stream.seek(0) # buffer position from start
    resp = send_file(path_or_file=binary_stream, download_name=download_name)
    
    return resp, 200

@app.route("/upload/<resource>", methods=["PUT"])
@token_required
def upload_remote(current_user, resource):
    """
    Upload the file to the cluster. to folder ROOT_PATH=`/scratch/snx3000/jyu/firecrest/`
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
    target_path = os.path.join(app.config['ROOT_FOLDER'], repo, resource)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        binary_stream = io.BytesIO(file.read())
        
        resp = client.simple_upload(binary_stream, target_path, filename)
    
        return resp, 200
    
@app.route("/delete/<resource>", methods=["DELETE"])
@token_required
def delete_remote(current_user, resource):
    """
    Downloads the remote files from the cluster.
    :param path: path string relative to the parent ROOT_PATH=`/scratch/snx3000/jyu/firecrest/`
    :return: file.
    """
    repo = email2repo(current_user['email'])
    
    data = request.json
    filename = data.get('filename')
    target_path = os.path.join(ROOT_FOLDER, repo, resource, filename)
    
    client.simple_delete(target_path=target_path)
    
    return '', 204


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


if __name__ == "__main__":
    app.run(
        debug=True, 
        port=5005, 
        # ssl_context='adhoc',
    )
