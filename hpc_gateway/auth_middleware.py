from functools import wraps
import os
from flask import request, jsonify
import requests

MP_USERINFO_URL = os.environ.get("MP_USERINFO_URL")

# Need white list to prevent unknown users, we don't have purchase in action at the moment.
if os.environ.get("F7T_TOKEN") is None:
    WHITE_LIST = [
        'jusong.yu@epfl.ch',
        'andreas.aigner@dcs-computing.com', 
        'simon.adorf@epfl.ch',
    ]

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