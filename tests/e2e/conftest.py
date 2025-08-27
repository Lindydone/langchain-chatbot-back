import os, pytest, httpx

@pytest.fixture(scope="session")
def base_url(load_env):
    base = os.path.dirname(os.path.dirname(__file__)) 
    env_path = os.path.join(base, "envs", "e2e.env")
    load_env(env_path, override=False)

    url = os.getenv("E2E_BASE_URL")
    if not url:
        pytest.skip("E2E_BASE_URL not set; skipping e2e tests")
    return url.rstrip("/")

@pytest.fixture()
def http(base_url):
    with httpx.Client(base_url=base_url, timeout=15) as c:
        yield c
