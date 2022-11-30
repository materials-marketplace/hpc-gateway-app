"""The repository is created by job api, so it is also
destroyed from job API instead of here.
"""

from flask import Blueprint, request, jsonify

from hpc_gateway.model.database import get_db

# For the direct DB data manipulate, basically the
# capabilies of DataSink and DataSource.
file_api_v1 = Blueprint(
    'file_api_v1', 'file_api_v1', url_prefix='/api/v1/file'
)

@file_api_v1.route('/', methods=['GET'])
def api_get_repositories():
    """get/list all remote project repositories.
    """
    pass

@file_api_v1.route('/download/<repository>', methods=['GET'])
def api_fetch_file_from_repo(repository):
    """fetch (download) file from a repository."""
    pass

@file_api_v1.route('/list/<repository>', methods=['GET'])
def api_list_repo(repository):
    """list files in a repository."""
    pass

@file_api_v1.route('/upload/<repository>', methods=['POST'])
def api_push_file_to_repo(repository):
    """push (upload) the file to a repository"""
    pass

@file_api_v1.route('/delete/<repository>', methods=['DELETE'])
def api_delete_file_from_repo(repository):
    """delete the file from a repository."""
    pass