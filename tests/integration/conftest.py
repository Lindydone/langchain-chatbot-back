import pytest
from fastapi.testclient import TestClient

@pytest.fixture(scope="session")
def app(app_base, real_lifespan_ctx):
    app = app_base
    app.router.lifespan_context = real_lifespan_ctx
    return app

@pytest.fixture()
def client(app):
    # lifespan 보장
    with TestClient(app) as c:
        yield c