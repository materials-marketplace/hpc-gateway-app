import os
import uuid

from flask import Blueprint, current_app, jsonify, request

from hpc_gateway.auth import token_required
from hpc_gateway.model.database import (
    EntityNotFoundError,
    create_job,
    get_job,
    get_jobs,
    get_user,
    update_job,
)
from hpc_gateway.model.f7t import create_f7t_client
from hpc_gateway.model.job import create_job_script

# For the job manipulate, basically the
# capabilies relate to simulation.
job_api_v1 = Blueprint("job_api_v1", "job_api_v1", url_prefix="/api/v1/job")

JOB_SCRIPT_FILENAME = "job.sh"


@job_api_v1.route("/", methods=["GET"])
@token_required
def api_get_jobs(current_user):
    """get jobs from DB of the user."""
    email = current_user.get("email")
    try:
        user = get_user(email)
    except EntityNotFoundError:
        return (jsonify(error="We can not find your are registered."), 500)
    else:
        user_id = user.get("_id")

    jobs = get_jobs(user_id)

    # arrange output where the jobs is
    # as dict of key: value -> _id: details
    output_jobs = {}
    for job in jobs:
        output_jobs[str(job.get("_id"))] = job

    return jsonify(
        jobs=output_jobs,
    )


@job_api_v1.route("/state/<jobid>", methods=["GET"])
def api_get_job_state(jobid):
    """get state (return by files in the folder) of a job through firecrest.
    list files of a job.
    file contain also the folder and the format is list.
    """
    machine = current_app.config["MACHINE"]

    job = get_job(job_id=jobid)
    remote_folder = job.get("remote_folder")

    try:
        f7t_client = create_f7t_client()
        response = f7t_client.list_files(machine=machine, target_path=remote_folder)
    except Exception as e:
        return (
            jsonify(
                error="unable to list files to job folder.",
                except_type=str(type(e)),
            ),
            500,
        )
    else:
        return (
            jsonify(
                files=response,
                message="Files in the job folder.",
            ),
            200,
        )


@job_api_v1.route("/create", methods=["POST"])
@token_required
def api_create_job(current_user):
    """create a job and
    return jobid for job modification and data manipulation

    This api will create the folder in remote cluster return the
    folder(repository) name.
    It will also create a slurm script to run the job inside the container
    controlled by singularity.
    """
    machine = current_app.config["MACHINE"]

    email = current_user.get("email")

    try:
        user = get_user(email)
    except EntityNotFoundError:
        return (jsonify(error="We can not find your are registered."), 500)
    else:
        user_id = user.get("_id")
        user_home = user.get("home")

    fd = str(uuid.uuid4())  # the remote folder name of this job
    remote_folder = os.path.join(user_home, fd)

    request_obj = request.get_json()
    request_obj["email"] = email

    try:
        f7t_client = create_f7t_client()
        f7t_client.mkdir(machine=machine, target_path=remote_folder)
        # create a script file and upload, the content is read from parameters
        job_script = create_job_script(**request_obj)

        f7t_client.simple_upload(
            machine=machine,
            source_path=job_script.encode(),
            target_path=remote_folder,
            filename=JOB_SCRIPT_FILENAME,
        )
    except Exception as e:
        # faild to create job to remote folder
        return (
            jsonify(
                error=f"unable to create job in machine {machine}.",
                except_type=str(type(e)),
            ),
            400,
        )
    else:
        job = create_job(user_id=user_id, remote_folder=remote_folder)
        return (
            jsonify(
                jobid=job["_id"],
            ),
            200,
        )


@job_api_v1.route("/launch/<jobid>", methods=["PATCH"])
@token_required
def api_launch_job(current_user, jobid):
    """launch the job."""
    machine = current_app.config["MACHINE"]

    job = get_job(jobid)
    remote_folder = job.get("remote_folder")

    try:
        f7t_client = create_f7t_client()
        response = f7t_client.submit(
            machine=machine,
            job_script=os.path.join(remote_folder, JOB_SCRIPT_FILENAME),
            local_file=False,
        )
        f7t_job_id = response.get("jobid")
    except Exception as e:
        print(e)
        # faild to create job to remote folder
        return (
            jsonify(
                error=f"unable to submit job in machine {machine}.",
                except_type=str(type(e)),
            ),
            600,
        )
    else:
        job = update_job(job_id=jobid, f7t_job_id=f7t_job_id)
        return (
            jsonify(
                jobid=job["_id"],
            ),
            200,
        )


@job_api_v1.route("/cancel/<jobid>", methods=["DELETE"])
@token_required
def api_cancel_job(current_user, jobid):
    """cancel the job, by call cancel f7t operation.
    Simply send a f7t signal and do nothing to the DB entity.
    """
    machine = current_app.config["MACHINE"]

    job = get_job(jobid)
    if job.get("state") != "ACTIVATED":
        return (
            jsonify(
                error=f"Job {jobid} not launched yet.",
            ),
            505,
        )

    try:
        f7t_client = create_f7t_client()
        f7t_job_id = job.get("f7t_job_id")
        f7t_client.cancel(
            machine=machine,
            job_id=f7t_job_id,
        )
    except Exception as e:
        # faild to create job to remote folder
        return (
            jsonify(
                error=f"unable to cancel job in machine {machine}.",
                except_type=str(type(e)),
            ),
            600,
        )
    else:
        return (
            jsonify(
                message=f"Send cancelling signal to job-{jobid}, of f7t job id={f7t_job_id}",
            ),
            200,
        )


@job_api_v1.route("/delete/<jobid>", methods=["DELETE"])
def api_delete_job(jobid):
    """Delete job entity from database.
    This will also trigger the clean up of its repository corresponded.
    """
    pass
