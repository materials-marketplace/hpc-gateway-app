import os
from datetime import datetime

from bson import ObjectId, json_util
from flask import Flask, jsonify, render_template
from flask.json import JSONEncoder

from hpc_gateway.api.file import file_api_v1
from hpc_gateway.api.image import image_api_v1
from hpc_gateway.api.job import job_api_v1
from hpc_gateway.api.user import user_api_v1


class MongoJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(obj, ObjectId):
            return str(obj)
        return json_util.default(obj, json_util.CANONICAL_JSON_OPTIONS)


def create_app():
    APP_DIR = os.path.abspath(os.path.dirname(__file__))
    STATIC_FOLDER = os.path.join(APP_DIR, "build/static")
    TEMPLATE_FOLDER = os.path.join(APP_DIR, "build")

    app = Flask(
        __name__,
        static_folder=STATIC_FOLDER,
        template_folder=TEMPLATE_FOLDER,
    )
    app.json_encoder = MongoJsonEncoder
    app.register_blueprint(file_api_v1)
    app.register_blueprint(job_api_v1)
    app.register_blueprint(user_api_v1)
    app.register_blueprint(image_api_v1)

    @app.route("/")
    def serve():
        return render_template("index.html")

    @app.route("/heartbeat")
    def heartbeat():
        return (
            jsonify(
                message="HPC-gateway-App : application running.",
            ),
            200,
        )

    return app
