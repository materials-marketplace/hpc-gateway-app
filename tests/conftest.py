import mongomock
import pymongo
import pytest

from hpc_gateway.factory import create_app


@pytest.fixture(scope="session")
@mongomock.patch(servers=(("server.example.com", 27017),))
def mock_db():
    """This fixture last for whole test session, the db will not destroy
    until the end of pytest"""
    client = pymongo.MongoClient(host="server.example.com")
    db = client._database
    return db


@pytest.fixture()
def app():
    app = create_app()
    app.config.from_object("hpc_gateway.config.TestingConfig")

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
