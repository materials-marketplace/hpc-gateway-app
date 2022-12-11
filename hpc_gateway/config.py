#!/usr/bin/env python

import os
from urllib.parse import urljoin

from dotenv import load_dotenv

load_dotenv

# Find the absolute file path to the top level project directory
basedir = os.path.abspath(os.path.dirname(__file__))

USERINFO_ENDPOINT = "auth/realms/marketplace/protocol/openid-connect/userinfo"


class Config:
    """Base configuration class.
    Contains default configuration settings."""

    # Default settings
    FLASK_ENV = "development"
    DEBUG = False
    TESTING = False
    USE_SSL = True

    PORT = 5000


class StagingConfig(Config):
    """Staging server registries"""

    DEBUG = True
    FLASK_ENV = "production"
    TESTING = False
    MP_URL = "http://staging.materials-marketplace.eu"
    MP_USERINFO_URL = urljoin(MP_URL, USERINFO_ENDPOINT)


class StagingMCConfig(StagingConfig):
    """Materials Cloud dokku deployment,
    registered in staging server."""

    MONGODB_PASSWORD = os.environ.get("MONGODB_PASSWORD")
    MONGO_URI = f"mongodb+srv://mphpc:{MONGODB_PASSWORD}@mongodb-heroku-mp-hpc-a.dzddt.mongodb.net/hpcdb?retryWrites=true&w=majority"

    MACHINE = "daint"
    CLUSTER_HOME = "/scratch/snx3000/jyu/firecrest/"
    F7T_CLIENT_ID = os.environ.get("F7T_CLIENT_ID")
    F7T_CLIENT_SECRET = os.environ.get("F7T_SECRET")
    F7T_AUTH_URL = "https://firecrest.cscs.ch"
    F7T_TOKEN_URL = (
        "https://auth.cscs.ch/auth/realms/cscs/protocol/openid-connect/token"
    )


class StagingIWMConfig(StagingConfig):
    """IWM self-hosted firecrest deployment,
    registered in staging server communicate via broker."""

    MONGODB_PASSWORD = os.environ.get("MONGODB_PASSWORD")
    MONGO_URI = f"mongodb://flaskuser:{MONGODB_PASSWORD}@mongo:27017/flaskdb"

    MACHINE = "cluster"
    CLUSTER_HOME = "/home/jyu/firecrest"
    F7T_AUTH_URL = "http://192.168.220.21:8000"
    F7T_TOKEN = os.environ.get("F7T_TOKEN")


class TestingConfig(Config):
    TESTING = True
    MONGO_URI = "mongodb://"
    MP_URL = "http://staging.materials-marketplace.eu"
    MP_USERINFO_URL = urljoin(MP_URL, USERINFO_ENDPOINT)


class TestingMCConfig(TestingConfig):
    MACHINE = "daint"
    CLUSTER_HOME = "/scratch/snx3000/jyu/firecrest/"
    F7T_CLIENT_ID = os.environ.get("F7T_CLIENT_ID")
    F7T_CLIENT_SECRET = os.environ.get("F7T_SECRET")
    F7T_AUTH_URL = "https://firecrest.cscs.ch"
    F7T_TOKEN_URL = (
        "https://auth.cscs.ch/auth/realms/cscs/protocol/openid-connect/token"
    )


class TestingIWMConfig(TestingConfig):
    MACHINE = "cluster"
    CLUSTER_HOME = "/home/jyu/firecrest"
    F7T_AUTH_URL = "http://192.168.220.21:8000"
    F7T_TOKEN = os.environ.get("F7T_TOKEN")
