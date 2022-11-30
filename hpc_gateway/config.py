#!/usr/bin/env python

import os
from dotenv import load_dotenv
from urllib.parse import urljoin

load_dotenv

# Find the absolute file path to the top level project directory
basedir = os.path.abspath(os.path.dirname(__file__))

USERINFO_ENDPOINT = "auth/realms/marketplace/protocol/openid-connect/userinfo"

class Config:
    """Base configuration class. 
    Contains default configuration settings."""
    # Default settings
    FLASK_ENV = 'development'
    DEBUG = False
    TESTING = False
    USE_SSL = True
    
    PORT = 5000
    
class StagingConfig(Config):
    """Staging server registries
    """
    DEBUG = True
    MP_URL = "http://staging.materials-marketplace.eu"
    MP_USERINFO_URL = urljoin(MP_URL, USERINFO_ENDPOINT)
    
class TestingConfig(Config):
    TESTING = True
    MP_URL = "http://staging.materials-marketplace.eu"
    MP_USERINFO_URL = urljoin(MP_URL, USERINFO_ENDPOINT)
    