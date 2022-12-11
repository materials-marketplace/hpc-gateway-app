from functools import wraps

import requests
from flask import current_app, jsonify, request
from requests.exceptions import ConnectionError


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        userinfo_url = current_app.config["MP_USERINFO_URL"]
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            return (
                jsonify(
                    message="Authentication Token is missing!",
                    data=None,
                    error="Unauthorized",
                ),
                401,
            )
        try:
            headers = {
                "Accept": "application/json",
                "User-Agent": "HPC-app",
                "Authorization": f"Bearer {token}",
            }

            # Use GET request method

            resp = requests.get(
                userinfo_url,
                headers=headers,
                verify=None,
            )

            if resp.status_code == 200:
                current_user = resp.json()
            else:
                current_user = None

            if current_user is None:
                return (
                    jsonify(
                        message="Invalid Authentication token!",
                        data=None,
                        error="Unauthorized",
                    ),
                    401,
                )

        except ConnectionError as e:
            return (
                jsonify(
                    message=f"Connection error to {userinfo_url} failed.",
                    data=None,
                    error=str(e),
                ),
                401,
            )
        except Exception as e:
            return (
                jsonify(
                    message="Something went wrong.",
                    data=None,
                    error=str(e),
                ),
                500,
            )

        return f(current_user, *args, **kwargs)

    return decorated
