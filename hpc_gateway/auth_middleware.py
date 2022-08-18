from functools import wraps
import os
import json
from flask import request, jsonify
import requests

MP_USERINFO_URL = os.environ.get("MP_USERINFO_URL")

# Need white list to prevent unknown users, we don't have purchase in action at the moment.
# this is inconvinient since have to redeploy to add account, should using another DB collection.
# But since the white list is not required by IWM deployment, it is not urgent to implement that.
WHITE_LIST = os.environ.get("HPCGATEWAY_WHITE_LIST", None)
if WHITE_LIST is not None:
    # read from ENV
    WHITE_LIST = json.loads(WHITE_LIST)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            return jsonify(
                message="Authentication Token is missing!",
                data=None,
                error="Unauthorized",
            ), 401
        try:
            headers = {
                "Accept": "application/json",
                "User-Agent": "HPC-app",
                "Authorization": f"Bearer {token}",
            }

            # Use GET request method
            resp = requests.get(
                MP_USERINFO_URL,
                headers=headers,
                verify=None,
            )

            if resp.status_code == 200:
                current_user = resp.json()
            else:
                current_user = None

            if current_user is None:
                return jsonify(
                    message="Invalid Authentication token!",
                    data=None,
                    error="Unauthorized",
                ), 401
                
            if WHITE_LIST is not None and current_user['email'] not in WHITE_LIST:
                return jsonify(
                    message=f"User {current_user['email']} not allowed to access the API.",
                    data=None,
                    error="Access IM"
                ), 503

        except Exception as e:
            return jsonify(
                message="Something went wrong.",
                data=None,
                error=str(e),
            ), 500

        return f(current_user, *args, **kwargs)

    return decorated