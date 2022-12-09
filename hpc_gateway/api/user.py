"""The user is create and add to DB, the user parent repository in
remote cluster will be created.
"""
from pathlib import Path

from flask import Blueprint, current_app, jsonify

from hpc_gateway.auth import token_required
from hpc_gateway.model.database import create_user
from hpc_gateway.model.f7t import create_f7t_client

user_api_v1 = Blueprint("user_api_v1", "user_api_v1", url_prefix="/api/v1/user")


def email_to_repo(email):
    """Since the username allowed space character contained it
    is not proper to bedirectly used as repo (folder) name
    this helper function will convert space to underscore"""
    username = email.split("@")[0]  # get username
    repo = username.replace(".", "_")

    return repo


@user_api_v1.route("/create", methods=["PUT"])
@token_required
def api_create_user(current_user):
    """create user in DB and create a folder in remote cluster if
    it is not exist yet.
    """
    cluster_home = Path(current_app.config["CLUSTER_HOME"])
    machine = current_app.config["MACHINE"]

    email = current_user.get("email")
    name = current_user.get("name")
    repository = email_to_repo(email)
    user_home = cluster_home / repository

    # f7t operation
    try:
        f7t_client = create_f7t_client()
        f7t_client.mkdir(machine=machine, target_path=user_home, p=True)
    except Exception as e:
        return (
            jsonify(
                error=f"mkdir {user_home} on {machine} fail.",
                except_type=str(type(e)),
            ),
            501,
        )
    else:
        # DB operation
        user = create_user(email, name, str(user_home))

        return (
            jsonify(
                message="Success: Create user in database.",
                **user,
            ),
            200,
        )
