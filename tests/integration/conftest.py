import pytest

@pytest.fixture(scope="session")
def app(app_base, fake_lifespan_ctx):
    app = app_base
    app.router.lifespan_context = fake_lifespan_ctx
    return app