# tests/e2e/conftest.py
import os
import pytest
import httpx

@pytest.fixture(scope="session")
def base_url():
    url = os.getenv("E2E_BASE_URL")
    if not url:
        pytest.skip("E2E_BASE_URL not set; skipping e2e tests")
    return url.rstrip("/")

@pytest.fixture(scope="session")
def http(base_url: str):
    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        # 서버가 진짜 떠있는지 확인하고 안 뜨면 스킵
        try:
            client.get("/health", timeout=3.0)
        except Exception as e:
            pytest.skip(f"Cannot reach server at {base_url}: {e}")
        yield client
