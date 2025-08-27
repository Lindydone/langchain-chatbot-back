import os
import pytest
from fastapi.testclient import TestClient

@pytest.fixture(scope="session", autouse=True)
def _inject_integration_env(load_env):
    base = os.path.dirname(os.path.dirname(__file__))  # tests/
    env_path = os.path.join(base, "envs", "integration.env")
    load_env(env_path, override=False)

@pytest.fixture(scope="session")
def app(app_base, real_lifespan_ctx):
    app = app_base
    app.router.lifespan_context = real_lifespan_ctx
    return app

@pytest.fixture()
def client(app):
    with TestClient(app) as c:
        yield c