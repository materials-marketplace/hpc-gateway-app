"""The user is create and add to DB, the user parent repository in
remote cluster will be created.
"""

from flask import Blueprint, request, jsonify

from hpc_gateway.model.db import get_db

user_api_v1 = Blueprint(
    'user_api_v1', 'user_api_v1', url_prefix='/api/v1/user'
)

@user_api_v1.route('/create', methods=['POST'])
def api_create_user():
    """create user in DB and create a folder in remote cluster if
    it is not exist yet.
    """
    
