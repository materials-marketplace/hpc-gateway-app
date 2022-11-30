from flask import Blueprint, request, jsonify

from hpc_gateway.model.database import get_db

# For the job manipulate, basically the
# capabilies relate to simulation.
job_api_v1 = Blueprint(
    'job_api_v1', 'job_api_v1', url_prefix='/api/v1/job'
)

@job_api_v1.route('/', methods=['GET'])
def api_get_jobs():
    """list all jobs of user."""
    pass

@job_api_v1.route('/state/<jobid>', methods=['GET'])
def api_get_job_state(jobid):
    """get state of a job through firecrest."""
    pass

@job_api_v1.route('/create', methods=['POST'])
def api_create_job():
    """create a job and return jobid for job modification,
    return repository id for data manipulation.
    This api will create the folder in remote cluster return the 
    folder(repository) name.
    It will also create a slurm script to run the job inside the container
    controlled by singularity.
    """
    pass

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