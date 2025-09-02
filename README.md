LangChain Chatbot Backend

📌 프로젝트 목적

이 프로젝트는 LangChain 기반 챗봇 백엔드를 구축하기 위한 템플릿입니다.
FastAPI를 기반으로 계층형 구조(routers, controllers, adapters,
services)를 적용하여 유지보수성과 확장성을 높였습니다.
테스트는 pytest를 활용하여 단위(Unit), 통합(Integration), e2e(E2E)수준으로 관리할
수 있습니다.
---
아직 pytest 최신화 못했습니다 수정 예정
------------------------------------------------------------------------

📂 폴더 구조
```
langchain-chatbot/
├── api/
│   ├── main.py                    # FastAPI 엔트리포인트 (create_app)
│   ├── core/
│   │   ├── graph.py               # LangGraph StateGraph 구성
│   │   └── state/
│   │       └── chatstate.py       # ChatState / Message / ModelOpts (Pydantic v2)
│   ├── core/node/
│   │   ├── load_summary.py        # 세션 요약 로드(Postgres)
│   │   ├── load_history.py        # 히스토리 로드/예산 계산(Redis)
│   │   ├── build_prompt.py        # system+summary+history+user → 패킹
│   │   ├── call_model.py          # 모델 호출(어댑터)
│   │   ├── persist.py             # 메시지 영속화(Postgres/Redis)
│   │   └── normalizer.py          # 최종 상태 정규화(선택)
│   ├── routers/                   # 라우팅 (health, chat)
│   ├── controllers/               # HTTP → 그래프 호출/응답 변환
│   ├── adapters/                  # 외부 연동 (Redis, DB, etc.)
│   ├── providers/                 # 모델 제공자(BaseChatModel, 구현체)
│   ├── db/                        # rdb/redis/models
│   ├── utils/                     # token_count, pack_prompt 등 유틸
│   └── schemas/                   # API 요청/응답 스키마
│
├── tests/
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── test_data/
│
├── docker/
│   ├── config/
│   └── data/
│
├── scripts_autocommit/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt (선택)
├── pytest.ini
└── uv.lock
```

------------------------------------------------------------------------
## 기술

* **FastAPI**, **Uvicorn**
* **LangGraph(LangChain)**: 멀티 노드 대화 파이프라인
* **Pydantic v2**: 타입 안정성 (ChatState/Message)
* **SQLModel + Postgres**: 세션/메시지 영속화
* **redis-py(Async) + Redis**: 최근 대화 히스토리 캐시
* **pytest**: 단위/통합/E2E 테스트

---

## ⚙️ 환경 변수(.env 예시)

```
# Server
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/chatdb
DB_SET=keep                    # keep | recreate (recreate는 부팅 시 테이블 드랍)

# Redis
REDIS_URL=redis://localhost:6379/0

# Model
MODEL_NAME=gpt-4o-mini
MODEL_PROVIDER=openai          # 필요 시 교체

# Prompt budget
PROMPT_BUDGET=8192
REPLY_RESERVE=1024
HISTORY_RATIO=0.7
```

> 설정은 `config.settings`에서 로드합니다. 값이 없으면 기본값을 사용합니다.

---

##  실행 방법

### 1) 의존성 설치(uv)

```bash
# uv 설치 (최초 1회)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 의존성 설치
uv sync
```

### 2) 로컬 개발 서버

```bash
uv run uvicorn api.main:app --reload
```

### 3) 테스트

```bash
uv run pytest
```

### 4) Docker

```bash
docker-compose up -d --build
```

> 설정만 만들어둔 미구현 오픈서치
```bash
docker compose --profile search up -d
```

---

## 엔드포인트

### Health

```
GET /health
```

200 OK를 반환합니다.

### Chat

```
POST /v1/chat
Content-Type: application/json
```

**요청 (ChatRequest)**

```json
{
  "message": "안녕!",
  "session_id": "abc-123",
  "user_id": "user-42",
  "system_prompt": "You are a helpful assistant.",
  "opts": { "temperature": 0.2 }
}
```

**응답 (ChatResponse)**

```json
{
  "reply": "안녕하세요! 무엇을 도와드릴까요?",
  "session_id": "abc-123"
}
```

---

##  대화 그래프 파이프라인

`api/core/graph.py`에 정의된 기본 플로우:

1. **load\_session\_summary** — (Postgres) 세션 요약 로드
2. **load\_history\_turn\_based** — (Redis) 토큰 예산에 맞게 최근 턴 수집 20쌍
3. **build\_prompt** — system + (요약) + history + 현재 user를 토큰 예산에 맞게 패킹
4. **call\_model** — 모델 호출 후 assistant 메시지 추가
5. **postprocess** — 후처리 훅( 미완성 )
6. **persist** — 마지막 user/assistant 쌍을 Postgres/Redis에 저장

---

## 노드 구현 규칙

* 시그니처: `async def node(state: ChatState) -> ChatState`
* **반환은 항상 `state`** (`dict` 반환을 안하는 형태로 진행)
* 상태 접근: `state.xxx` (해당 형태로 통일)
* 메시지 타입: 항상 `Message(role=..., content=...)` (dict 금지)
* 에러는 `state.error = "..."`로 세팅 후 `return state`
* Redis 저장: `Message.model_dump_json()` 사용(직렬화 에러 방지)

---

## 토큰/프롬프트 관리

* `utils/pack_prompt.py`의 `pack_prompt_with_ratio`는

  * **예산** = `PROMPT_BUDGET - REPLY_RESERVE`
  * 예산 내에서 \*\*system(선택) + history(가능한 만큼) + current\_user(필수)\*\*를 배치
  * 필요 시 user 메시지를 안전하게 truncate
* `count_messages`는 \*\*`List[Message]`\*\*를 입력으로 받고 `m.content` 기준으로 토큰을 집계합니다.

---

## 영속화 전략

* **Postgres(SQLModel)**: 세션 존재 보장 후 user/assistant 메시지 저장
* **Redis**: 최근 대화 히스토리 리스트 보존, `model_dump_json()`으로 push, `LTRIM`으로 윈도 관리(예: 최근 20쌍=40개)

---

## 향후 계획

1. RAG 연결 로직 구현 ( 일단은 pdf로만 )
2. chatbot-models 구현 (이제 다른 곳에서 ai 호출)


