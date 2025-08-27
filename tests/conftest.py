import os
import pytest
from contextlib import asynccontextmanager
from fastapi.testclient import TestClient

import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from main import create_app

from api.core.graph import create_graph

# ── 빠른 유닛 테스트용 Fake 모델 ──
class FakeModel:
    async def generate(self, messages, **opts):
        last = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        return f"echo:{last.strip()}"

# ── lifespan 컨텍스트(선택지) ──
@asynccontextmanager
async def lifespan_fake(app):
    app.state.chat_model = FakeModel()
    app.state.chat_graph = create_graph(app.state.chat_model)
    yield

@asynccontextmanager
async def lifespan_real(app):
    # 통합테스트 때 쓸 예정 (실 모델/환경)
    from api.providers.factory import build_chat_model
    model = build_chat_model()
    app.state.chat_model = model
    app.state.chat_graph = create_graph(model)
    yield

# ── 하위 conftest가 고르도록 내리는 픽스처 ──
@pytest.fixture(scope="session")
def fake_lifespan_ctx():
    return lifespan_fake

@pytest.fixture(scope="session")
def real_lifespan_ctx():
    return lifespan_real

# ── 앱 베이스(수명주기 미설정) ──
@pytest.fixture(scope="session")
def app_base():
    return create_app()

# ── 공통 HTTP 클라이언트 ──
@pytest.fixture()
def client(app):
    with TestClient(app) as c:
        yield c
# 외부 의존 테스트 자동 skip (선택)
def pytest_runtest_setup(item):
    if "external" in item.keywords and not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set; skipping external test")
