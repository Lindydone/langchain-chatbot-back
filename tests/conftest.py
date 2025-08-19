import pytest
from fastapi.testclient import TestClient
from api.main import create_app

@pytest.fixture(scope="session")
def app():
    return create_app()

@pytest.fixture()
def client(app):
    return TestClient(app)
