import os
import uuid

from flask import Blueprint, jsonify, current_app

from hpc_gateway.model.database import get_user, EntityNotFoundError, create_job, get_jobs
from hpc_gateway.auth import token_required
from hpc_gateway.model.f7t import create_f7t_client

# For the job manipulate, basically the
# capabilies relate to simulation.
job_api_v1 = Blueprint(
    'job_api_v1', 'job_api_v1', url_prefix='/api/v1/job'
)

@job_api_v1.route('/', methods=['GET'])
@token_required
def api_get_jobs(current_user):
    """get jobs from DB of the user."""
    machine = current_app.config['MACHINE']
        
    email = current_user.get("email")
    try:
        user = get_user(email)
    except EntityNotFoundError:
        return (
            jsonify(
                error=f"We can not find your are registered."
            ), 500
        )
    else:
        user_id = user.get('_id')
        
    jobs = get_jobs(user_id)
    
    return (
        jsonify(
            jobs=jobs
        )
    )
        
    

@job_api_v1.route('/state/<jobid>', methods=['GET'])
def api_get_job_state(jobid):
    """get state of a job through firecrest."""
    pass

@job_api_v1.route('/create', methods=['POST'])
@token_required
def api_create_job(current_user):
    """create a job and 
    return jobid for job modification and data manipulation
    
    This api will create the folder in remote cluster return the 
    folder(repository) name.
    It will also create a slurm script to run the job inside the container
    controlled by singularity.
    """
    machine = current_app.config['MACHINE']
        
    email = current_user.get("email")

    try:
        user = get_user(email)
    except EntityNotFoundError:
        return (
            jsonify(
                error=f"We can not find your are registered."
            ), 500
        )
    else:
        user_id = user.get('_id')
        user_home = user.get('home')
    
    fd = str(uuid.uuid4())  # the remote folder name of this job
    remote_folder = os.path.join(user_home, fd)
    
    try:
        f7t_client = create_f7t_client()
        f7t_client.mkdir(machine=machine, target_path=remote_folder)
        # create a script file and upload, the content is read from parameters
    except Exception as e:
        # faild to create job to remote folder
        return (
            jsonify(
                error=f"unable to create job in machine {machine}.",
            ), 500
        )
    else:
        job = create_job(user_id=user_id, remote_folder=remote_folder)
        return (
            jsonify(
                jobid=job['_id'],
            ), 200
        )
    

@job_api_v1.route('/launch/<jobid>', methods=['POST'])
def api_launch_job(jobid):
    """launch the job."""
    pass

@job_api_v1.route('/cancel/<jobid>', methods=['POST'])
def api_cancel_job(jobid):
    """cancel the job."""
    pass

@job_api_v1.route('/delete/<jobid>', methods=['DELETE'])
def api_delete_job(jobid):
    """Delete job entity from database.
    This will also trigger the clean up of its repository corresponded.
    """
    pass