import os
import pytest
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi.testclient import TestClient
from dotenv import dotenv_values

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

# ── lifespan 컨텍스트 ──
@asynccontextmanager
async def lifespan_fake(app):
    app.state.chat_model = FakeModel()
    app.state.chat_graph = create_graph(app.state.chat_model)
    yield

@asynccontextmanager
async def lifespan_real(app):
    # 통합테스트 때 사용(실 모델/환경)
    from api.providers.factory import build_chat_model
    model = build_chat_model()
    app.state.chat_model = model
    app.state.chat_graph = create_graph(model)
    yield

# ── 하위 conftest가 선택하는 픽스처 ──
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


# ── 테스트용 env 로딩 ──
def _load_env_file_early(path: str, override: bool = False):
    p = Path(path)
    if not p.exists():
        return
    data = dotenv_values(p) or {}
    for k, v in data.items():
        if v is None:
            continue
        if override or k not in os.environ:
            os.environ[k] = v

def pytest_sessionstart(session):
    """세션 시작 직후, 전역 스킵 훅보다 먼저 테스트용 env를 주입."""
    base = Path(__file__).parent / "envs"
    # 통합 테스트용 env 우선 로드
    _load_env_file_early(str(base / "integration.env"), override=False)
    # E2E도 함께 로드
    _load_env_file_early(str(base / "e2e.env"), override=False)

# ── 외부 의존 테스트 자동 skip ──
def pytest_runtest_setup(item):
    has_provider = os.getenv("OPENAI_API_KEY") or os.getenv("AI_MODELS_BASE_URL")
    if "external" in item.keywords and not has_provider:
        pytest.skip("OPENAI_API_KEY (or AI_MODELS_BASE_URL) not set; skipping external test")

# ── env 파일 로더 ──
@pytest.fixture(scope="session")
def load_env():
    """env 파일을 읽어 os.environ에 주입하는 함수 픽스처 반환"""
    def _load_env_file(path: str, override: bool = False) -> None:
        if not os.path.exists(path):
            return
        data = dotenv_values(path) or {}
        for k, v in data.items():
            if v is None:
                continue
            if override or k not in os.environ:
                os.environ[k] = v
    return _load_env_file