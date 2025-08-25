LangChain Chatbot Backend

📌 프로젝트 목적

이 프로젝트는 LangChain 기반 챗봇 백엔드를 구축하기 위한 템플릿입니다.
FastAPI를 기반으로 계층형 구조(routers, controllers, adapters,
services)를 적용하여 유지보수성과 확장성을 높였습니다.
테스트는 pytest를 활용하여 단위(Unit), 통합(Integration) 수준으로 관리할
수 있습니다.

------------------------------------------------------------------------

📂 폴더 구조

    langchain-chatbot/
    ├── api/                     # 애플리케이션 코드
    │   ├── main.py              # FastAPI 앱 엔트리포인트 (create_app)
    │   ├── core/                # 핵심 설정 (환경변수, config)
    │   ├── routers/             # 라우팅 계층 (health, chat 등)
    │   ├── controllers/         # 비즈니스 로직 계층
    │   ├── adapters/            # 외부 연동 계층 (예: Redis, DB)
    │   ├── services/            # 서비스 계층 (추후 구현)
    │   └── schemas/             # Pydantic 모델 정의
    │
    ├── tests/                   # 테스트 코드
    │   ├── conftest.py          # 공용 pytest fixture
    │   ├── unit/                # 단위 테스트
    │   ├── integration/         # 통합 테스트 (추후 확장)
    │   └── test_data/           # 테스트용 데이터
    │
    ├── docker/                  # Docker 관련 설정
    │   ├── config/              # Nginx 등 환경 설정
    │   └── data/                # 볼륨/데이터 디렉토리
    │
    ├── scripts_autocommit/      # Git hook 및 자동화 스크립트
    │
    ├── Dockerfile
    ├── docker-compose.yml
    ├── pyproject.toml           # uv / Poetry 기반 패키지 관리
    ├── requirements.txt         # 호환용 requirements (선택적)
    ├── pytest.ini               # pytest 설정
    ├── README.md
    └── uv.lock

------------------------------------------------------------------------

🚀 사용법

1. 환경 세팅

    # uv 설치 (최초 1회)
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.local/bin/env

    # 의존성 설치
    uv sync

2. 로컬 실행

    uv run uvicorn api.main:app --reload

→ API 서버가 http://localhost:8000 에서 실행됩니다.

3. 테스트 실행

    uv run pytest

4. Docker 실행

    docker-compose up --build

------------------------------------------------------------------------

🧪 현재 제공되는 엔드포인트

-   GET /healthz → 헬스 체크
-   POST /v1/chat → 기본 챗 API (echo 동작)

------------------------------------------------------------------------

📖 향후 확장 포인트

-   api/services/ 계층에 핵심 도메인 로직 추가
-   api/adapters/에 DB, 외부 API 연동 모듈 추가
-   tests/integration/ 디렉토리를 활용해 end-to-end 테스트 구현
-   docker/config/nginx/nginx.conf 채워서 배포 환경 구성

------------------------------------------------------------------------
