"""The repository is created by job api, so it is also
destroyed from job API instead of here.
These apis allow user to upload/download the files for calculation.
"""
import io
import os

from flask import Blueprint, current_app, jsonify, request, send_file

from hpc_gateway.auth import token_required
from hpc_gateway.model.database import get_job
from hpc_gateway.model.f7t import create_f7t_client

# For the direct DB data manipulate, basically the
# capabilies of DataSink and DataSource.
file_api_v1 = Blueprint("file_api_v1", "file_api_v1", url_prefix="/api/v1/file")


@file_api_v1.route("/", methods=["GET"])
@token_required
def api_get_repositories(current_user):
    """get/list all remote project repositories of user."""
    # useless for the moment, duplicate with get_jobs.


@file_api_v1.route("/download/<jobid>", methods=["GET"])
@token_required
def api_fetch_file_from_repo(current_user, jobid):
    """fetch (download) file from a repository."""
    machine = current_app.config["MACHINE"]

    job = get_job(job_id=jobid)
    remote_folder = job.get("remote_folder")

    filename = request.args.get("filename", None)
    if not filename:
        return (
            jsonify(
                error="Please provide the filename to download.",
            ),
            500,
        )

    remote_file_path = os.path.join(remote_folder, filename)
    binary_stream = io.BytesIO()

    try:
        # import ipdb; ipdb.set_trace()
        f7t_client = create_f7t_client()
        f7t_client.simple_download(
            machine=machine,
            source_path=remote_file_path,
            target_path=binary_stream,
        )
        binary_stream.seek(0)  # buffer position from start
        response = send_file(path_or_file=binary_stream, download_name=filename)
    except Exception as e:
        return (
            jsonify(
                error="unable to download file.",
                except_type=str(type(e)),
                debug=f"filename: {filename}",
            ),
            500,
        )
    else:
        return (response, 200)


@file_api_v1.route("/list/<jobid>", methods=["GET"])
@token_required
def api_list_repo(current_user, jobid):
    """list files of a job.
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


@file_api_v1.route("/upload/<jobid>", methods=["PUT"])
@token_required
def api_push_file_to_repo(current_user, jobid):
    """push (upload) file to job repository."""
    machine = current_app.config["MACHINE"]

    job = get_job(job_id=jobid)
    remote_folder = job.get("remote_folder")

    uploaded_file = request.files["file"]

    filename = request.args.get("filename", None)
    if filename:
        upload_filename = filename
    else:
        upload_filename = uploaded_file.filename

    try:
        f7t_client = create_f7t_client()
        f7t_client.simple_upload(
            machine=machine,
            source_path=uploaded_file.read(),
            target_path=remote_folder,
            filename=upload_filename,
        )
    except Exception as e:
        return (
            jsonify(
                error="unable to upload file to job folder.",
                except_type=str(type(e)),
            ),
            500,
        )
    else:
        return (
            jsonify(
                message="File uploaded.",
            ),
            200,
        )


@file_api_v1.route("/delete/<jobid>", methods=["DELETE"])
@token_required
def api_delete_file_from_repo(current_user, jobid):
    """delete the file from the job repository."""
    machine = current_app.config["MACHINE"]

    job = get_job(job_id=jobid)
    remote_folder = job.get("remote_folder")

    filename = request.args.get("filename", None)
    if not filename:
        return (
            jsonify(
                error="Please provide the filename to delete.",
            ),
            500,
        )

    file_path = os.path.join(remote_folder, filename)

    try:
        f7t_client = create_f7t_client()
        f7t_client.simple_delete(
            machine=machine,
            target_path=file_path,
        )
    except Exception as e:
        return (
            jsonify(
                error="unable to delete file.",
                except_type=str(type(e)),
            ),
            500,
        )
    else:
        return (
            jsonify(
                message="File deleted.",
            ),
            200,
        )
