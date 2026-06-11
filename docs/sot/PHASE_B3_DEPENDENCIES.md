# PHASE_B3_DEPENDENCIES (v1.0.1)

## 0. 문서 메타

| 항목 | 내용 |
|------|------|
| 문서 ID | B3 |
| 문서명 | PHASE_B3_DEPENDENCIES |
| 버전 | 1.0.1 |
| 작성일 | 2026-02-22 |
| 역할 | VAMOS AI 에이전트 플랫폼 의존성 목록 (Frontend / Rust / Python) |
| 상위 참조 | A1_TECH_STACK (COMBO-V1/V2/V3 LOCK), B2_PROJECT_STRUCTURE |
| 대상 버전 | V1 (로컬 MVP) 기준, V2/V3 확장 패키지 포함 |

### 연결 참조
- A1 Tech Stack: COMBO-V1/V2/V3 LOCK 결정
- B2 Project Structure: 디렉토리/모듈 구조 → 의존성 매핑
- D1~D8 Schema: Pydantic v2 스키마 → 패키지 연결

---

## 1. 개요 (의존성 관리 원칙)

### 1.1 관리 원칙

| 원칙 | 내용 |
|------|------|
| 최소 의존 | V1에 필요한 패키지만 포함, V2+ 패키지는 `[V2+]` 표시 |
| 버전 고정 | 메이저 버전 호환 범위 지정 (`>=`, `<` 사용) |
| LOCK 준수 | A1 Tech Stack LOCK 결정에 부합하는 패키지만 선정 |
| 라이선스 검토 | 상용/오픈소스 라이선스 충돌 방지 (섹션 6) |
| 보안 감사 | `npm audit`, `cargo audit`, `pip-audit` 정기 실행 |

### 1.2 의존성 관리 도구

| 영역 | 도구 | 잠금 파일 |
|------|------|----------|
| Frontend (React) | npm / pnpm | `package-lock.json` / `pnpm-lock.yaml` |
| Rust (Tauri) | Cargo | `Cargo.lock` |
| Python (AI/ML) | Poetry (또는 pip + pip-tools) | `poetry.lock` (또는 `requirements.lock`) |

---

## 2. Frontend -- package.json

### 2.1 dependencies

| 패키지 | 버전 범위 | 용도 | VAMOS 모듈 연결 |
|--------|----------|------|----------------|
| `react` | `^18.3.0` | React UI 라이브러리 | 전체 프론트엔드 (D8 UI/UX) |
| `react-dom` | `^18.3.0` | React DOM 렌더링 | 전체 프론트엔드 |
| `react-router-dom` | `^6.28.0` | 클라이언트 라우팅 | `pages/` 라우트 관리 |
| `@tauri-apps/api` | `^2.2.0` | Tauri IPC/이벤트 API | `hooks/useTauriIPC.ts` — Rust 백엔드 통신 |
| `@tauri-apps/plugin-shell` | `^2.2.0` | Tauri Shell 플러그인 (subprocess) | Python 프로세스 관리 보조 |
| `zustand` | `^5.0.0` | 경량 상태 관리 (Flux 패턴) | `stores/*.ts` — 앱 상태 관리 |
| `@tanstack/react-query` | `^5.62.0` | 서버 상태/비동기 데이터 관리 | Decision/Memory/Log 비동기 조회 |
| `recharts` | `^2.14.0` | 차트/시각화 라이브러리 | `components/cost/` — 비용 차트, 워크플로우 통계 |
| `@xyflow/react` | `^12.4.0` | 노드 기반 플로우 에디터 | `components/canvas/` — LangGraph 시각화 (D8 §4) |
| `date-fns` | `^4.1.0` | 날짜/시간 유틸리티 | `utils/dateUtils.ts` — ISO8601 포맷 |
| `clsx` | `^2.1.0` | 조건부 className 결합 | 컴포넌트 스타일링 유틸 |
| `lucide-react` | `^0.468.0` | 아이콘 라이브러리 | 전체 UI 아이콘 |
| `sonner` | `^1.7.0` | 토스트 알림 라이브러리 | `components/notifications/` — 알림 UI (D8 §7) |
| `zod` | `^3.24.0` | 스키마 검증 (프론트 타입 안전) | `types/*.ts` — D2~D7 스키마 프론트 검증 |

### 2.2 devDependencies

| 패키지 | 버전 범위 | 용도 | 비고 |
|--------|----------|------|------|
| `typescript` | `^5.7.0` | TypeScript 컴파일러 | 타입 안전 |
| `vite` | `^6.0.0` | 번들러/개발 서버 | Tauri 권장 번들러 |
| `@vitejs/plugin-react` | `^4.3.0` | Vite React 플러그인 | JSX/TSX 지원 |
| `vitest` | `^2.1.0` | 테스트 프레임워크 | React 컴포넌트/훅 테스트 |
| `@testing-library/react` | `^16.1.0` | React 테스트 유틸리티 | DOM 테스트 헬퍼 |
| `@testing-library/jest-dom` | `^6.6.0` | Jest DOM 매처 | DOM assertion 확장 |
| `jsdom` | `^25.0.0` | DOM 시뮬레이션 | vitest 브라우저 환경 |
| `@tauri-apps/cli` | `^2.2.0` | Tauri CLI (빌드/개발) | `tauri dev`, `tauri build` |
| `tailwindcss` | `^3.4.0` | 유틸리티 CSS 프레임워크 | `styles/globals.css` |
| `postcss` | `^8.4.0` | CSS 후처리기 | TailwindCSS 전처리 |
| `autoprefixer` | `^10.4.0` | CSS 벤더 프리픽스 자동 추가 | 브라우저 호환성 |
| `eslint` | `^9.16.0` | JavaScript/TypeScript 린터 | 코드 품질 |
| `@typescript-eslint/parser` | `^8.18.0` | ESLint TypeScript 파서 | TS 린팅 |
| `@typescript-eslint/eslint-plugin` | `^8.18.0` | ESLint TypeScript 규칙 | TS 린팅 규칙 |
| `prettier` | `^3.4.0` | 코드 포매터 | 일관된 코드 스타일 |

---

## 3. Rust -- Cargo.toml

### 3.1 [dependencies]

| 크레이트 | 버전 범위 | 용도 | VAMOS 모듈 연결 |
|----------|----------|------|----------------|
| `tauri` | `^2.2` | Tauri 2.0 코어 프레임워크 | 전체 Rust 백엔드 (A1 UI LOCK) |
| `tauri-plugin-shell` | `^2.2` | 외부 프로세스 실행 (Python subprocess) | `bridge/python_manager.rs` |
| `serde` | `^1.0` | 직렬화/역직렬화 프레임워크 | `models/*.rs` — D2~D7 스키마 Rust 구조체 |
| `serde_json` | `^1.0` | JSON 직렬화/역직렬화 | Rust-Python IPC JSON 통신 |
| `tokio` | `^1.42` | 비동기 런타임 | 비동기 IPC, subprocess 관리 |
| `reqwest` | `^0.12` | HTTP 클라이언트 | MCP Streamable HTTP 통신 (DEC-017) |
| `chrono` | `^0.4` | 날짜/시간 라이브러리 | ISO8601 타임스탬프 처리 |
| `uuid` | `^1.11` | UUID 생성 | `decision_id`, `trace_id` 등 고유 ID 생성 |
| `thiserror` | `^2.0` | 에러 타입 정의 | `utils/error.rs` — VamosError Rust 구현 |
| `anyhow` | `^1.0` | 에러 핸들링 (Result 래퍼) | 에러 전파 유틸 |
| `tracing` | `^0.1` | 구조화 로깅/트레이싱 | Rust 레벨 로그 (Trace 연계) |
| `tracing-subscriber` | `^0.3` | tracing 구독자 (포맷/필터) | 로그 출력 설정 |
| `toml` | `^0.8` | TOML 설정 파일 파싱 | `config/*.toml` 설정 로드 |
| `dirs` | `^5.0` | 플랫폼별 디렉토리 경로 | 데이터/설정 디렉토리 감지 |

### 3.2 [build-dependencies]

| 크레이트 | 버전 범위 | 용도 | 비고 |
|----------|----------|------|------|
| `tauri-build` | `^2.2` | Tauri 빌드 스크립트 | `build.rs`에서 사용 |

### 3.3 [dev-dependencies]

| 크레이트 | 버전 범위 | 용도 | 비고 |
|----------|----------|------|------|
| `tokio-test` | `^0.4` | Tokio 비동기 테스트 유틸 | `cargo test` 비동기 테스트 |
| `tempfile` | `^3.14` | 임시 파일/디렉토리 테스트 | 파일 기반 테스트 격리 |

### 3.4 features

```toml
[dependencies.tauri]
version = "^2.2"
features = ["tray-icon"]          # 시스템 트레이 아이콘

[dependencies.reqwest]
version = "^0.12"
features = ["json", "rustls-tls"] # JSON 지원, TLS

[dependencies.uuid]
version = "^1.11"
features = ["v4"]                 # UUID v4 랜덤 생성

[dependencies.tokio]
version = "^1.42"
features = ["full"]               # 전체 기능 (rt, macros, io 등)
```

---

## 4. Python -- pyproject.toml

### 4.0 프로젝트 메타데이터

```toml
[project]
name = "vamos-core"
requires-python = ">=3.11"
```

> **NOTE**: `requires-python = ">=3.11"`은 필수. BGE-M3(`FlagEmbedding`), Pydantic v2, LangGraph 등 핵심 패키지가 Python 3.11+ 전용 기능(`tomllib` 표준 라이브러리, 타입 힌트 개선 등)에 의존하며, 3.10 이하 환경에서는 설치 실패 가능.

### 4.1 core (핵심 의존성)

| 패키지 | 버전 범위 | 용도 | VAMOS 모듈 연결 |
|--------|----------|------|----------------|
| `pydantic` | `>=2.10,<3.0` | Pydantic v2 스키마 검증 (LOCK) | `schemas/contracts.py` — 전수 검증 의무 (ADD-036b) |
| `pydantic-settings` | `>=2.7,<3.0` | 환경변수/설정 관리 | `config.py` — .env 로딩 |
| `langgraph` | `>=0.2.60,<1.0` | LangGraph StateGraph 프레임워크 (LOCK) | `agent/graph/` — StateGraph 기반 파이프라인 |
| `langchain-core` | `>=0.3.25,<1.0` | LangChain 코어 (Runnable 인터페이스) | `orange_core/`, `blue_nodes/base_node.py` — Runnable 프로토콜 |
| `langchain-openai` | `>=0.2.14,<1.0` | LangChain OpenAI 통합 | `infra/brain/openai_adapter.py` — GPT-4o mini/GPT-4o |
| `langchain-community` | `>=0.3.15,<1.0` | LangChain 커뮤니티 통합 (Ollama 등) | `infra/brain/ollama_adapter.py` — Ollama 로컬 LLM |
| `langchain-anthropic` | `>=0.3.0,<1.0` | LangChain Anthropic 통합 [V2+] | `infra/brain/anthropic_adapter.py` — Claude [V2+] |

### 4.2 embedding (임베딩 모델)

| 패키지 | 버전 범위 | 용도 | VAMOS 모듈 연결 | 버전 |
|--------|----------|------|----------------|------|
| `FlagEmbedding` | `>=1.3.0,<2.0` | BGE-M3 임베딩 모델 (1024차원, 무료) | `storage/vector/embedder.py` — V1 기본 임베딩 (DEC-005) | V1 |
| `sentence-transformers` | `>=3.3.0,<4.0` | Sentence Transformers (BGE-M3 백엔드) | `storage/vector/embedder.py` — 임베딩 생성 보조 | V1 |
| `torch` | `>=2.5.0,<3.0` | PyTorch (BGE-M3 추론 백엔드) | `storage/vector/embedder.py` — 로컬 모델 추론 | V1 |
| `openai` | `>=1.58.0,<2.0` | OpenAI API SDK (임베딩 + LLM) | `storage/vector/embedder.py` — text-embedding-3-small [V2+] | V1/V2+ |

> **NOTE**: `torch`는 BGE-M3 로컬 임베딩에 필수. CPU 환경에서는 `torch` (CPU 전용) 설치 권장. GPU 환경에서는 CUDA 버전에 맞춰 설치.

### 4.3 vector (벡터 데이터베이스)

| 패키지 | 버전 범위 | 용도 | VAMOS 모듈 연결 | 버전 |
|--------|----------|------|----------------|------|
| `chromadb` | `>=0.5.23,<1.0` | Chroma 벡터 DB (로컬 임베디드) | `storage/vector/chroma_store.py` — V1 벡터 저장 (A1 LOCK) | V1 |
| `qdrant-client` | `>=1.12.0,<2.0` | Qdrant 벡터 DB 클라이언트 [V2+] | `storage/vector/qdrant_store.py` — V2+ 벡터 저장 (A1 LOCK) | [V2+] |

### 4.4 storage (저장소)

| 패키지 | 버전 범위 | 용도 | VAMOS 모듈 연결 | 버전 |
|--------|----------|------|----------------|------|
| `aiosqlite` | `>=0.20.0,<1.0` | 비동기 SQLite 드라이버 | `storage/db/sqlite_manager.py` — V1 메타/인덱스 | V1 |
| `sqlalchemy` | `>=2.0.36,<3.0` | SQL ORM / 쿼리 빌더 | `storage/db/` — DB 접근 계층 (SQLite/Postgres 통합) | V1/V2+ |
| `alembic` | `>=1.14.0,<2.0` | DB 마이그레이션 관리 | `storage/db/migrations/` — 스키마 마이그레이션 | V1/V2+ |
| `asyncpg` | `>=0.30.0,<1.0` | 비동기 PostgreSQL 드라이버 [V2+] | `storage/db/postgres_manager.py` — V2+ 중앙 DB | [V2+] |

### 4.5 guardrails (가드레일 / 안전)

| 패키지 | 버전 범위 | 용도 | VAMOS 모듈 연결 | 버전 |
|--------|----------|------|----------------|------|
| `nemoguardrails` | `>=0.11.0,<1.0` | NeMo Guardrails — Layer 1 입력 레일 | `safety/guardrails/nemo_rail.py` — L1 입력 검사 (ADD-013) | V1 |
| `guardrails-ai` | `>=0.5.15,<1.0` | Guardrails AI — Layer 2 출력 검증 | `safety/guardrails/guardrails_ai.py` — L2 출력 검증 (ADD-014) | V1 |
| `transformers` | `>=4.47.0,<5.0` | Hugging Face Transformers (LlamaGuard 기반) | `safety/guardrails/llamaguard.py` — L3 안전 분류 (ADD-015) [V2+ 옵션] | [V2+] |

> **NOTE**: LlamaGuard(Layer 3)는 로컬 GPU가 필요하므로 V1에서는 선택 사항이며, GPU 여건에 따라 V2+에서 도입한다 (A1-6B 결정).

### 4.6 mcp (Model Context Protocol)

| 패키지 | 버전 범위 | 용도 | VAMOS 모듈 연결 | 버전 |
|--------|----------|------|----------------|------|
| `httpx` | `>=0.28.0,<1.0` | 비동기 HTTP 클라이언트 (MCP Streamable HTTP) | `mcp/client.py` — MCP 도구 호출 (DEC-017 LOCK) | V1 |
| `sse-starlette` | `>=2.2.0,<3.0` | SSE(Server-Sent Events) 서버 | `mcp/server.py` — MCP 서버 SSE 스트리밍 | V1 |
| `starlette` | `>=0.41.0,<1.0` | ASGI 프레임워크 (MCP 서버) | `mcp/server.py` — MCP 서버 HTTP 엔드포인트 | V1 |
| `uvicorn` | `>=0.34.0,<1.0` | ASGI 서버 | `mcp/server.py` — MCP 서버 실행 | V1 |

### 4.7 utils (유틸리티)

| 패키지 | 버전 범위 | 용도 | VAMOS 모듈 연결 | 버전 |
|--------|----------|------|----------------|------|
| `tiktoken` | `>=0.8.0,<1.0` | 토큰 카운팅 (cl100k_base LOCK) | `infra/brain/token_counter.py` — 토큰 수 산출 (02 §2.3-A LOCK) | V1 |
| `python-dotenv` | `>=1.0.0,<2.0` | .env 환경변수 로딩 | `config.py` — 환경 설정 | V1 |
| `structlog` | `>=24.4.0,<25.0` | 구조화 로깅 라이브러리 | `storage/logging/` — 구조화 JSON 로그 출력 | V1 |
| `rich` | `>=13.9.0,<14.0` | 리치 터미널 출력 (개발/디버깅) | 개발 시 로그/디버그 출력 | V1 |
| `orjson` | `>=3.10.0,<4.0` | 고속 JSON 직렬화 (Pydantic v2 호환) | `schemas/contracts.py` — 고속 JSON 처리 | V1 |
| `tenacity` | `>=9.0.0,<10.0` | 재시도 라이브러리 | `infra/brain/`, `mcp/client.py` — API 호출 재시도 | V1 |
| `aiofiles` | `>=24.1.0,<25.0` | 비동기 파일 I/O | `storage/logging/jsonl_logger.py` — JSONL 비동기 쓰기 | V1 |

### 4.8 dev (개발 의존성)

| 패키지 | 버전 범위 | 용도 | 비고 |
|--------|----------|------|------|
| `pytest` | `>=8.3.0,<9.0` | Python 테스트 프레임워크 | 단위/통합 테스트 |
| `pytest-asyncio` | `>=0.24.0,<1.0` | pytest 비동기 테스트 지원 | async/await 테스트 |
| `pytest-cov` | `>=6.0.0,<7.0` | 테스트 커버리지 측정 | 코드 커버리지 리포트 |
| `pytest-mock` | `>=3.14.0,<4.0` | pytest 모킹 유틸리티 | LLM/DB 모킹 |
| `ruff` | `>=0.8.0,<1.0` | Python 린터/포매터 (Rust 기반, 고속) | 코드 품질 |
| `mypy` | `>=1.13.0,<2.0` | Python 정적 타입 검사 | Pydantic v2 타입 검증 |
| `pre-commit` | `>=4.0.0,<5.0` | Git pre-commit 훅 관리 | 커밋 전 자동 검사 (lint/type/format) |
| `pip-audit` | `>=2.7.0,<3.0` | Python 패키지 보안 감사 | 취약점 스캔 |
| `ipython` | `>=8.30.0,<9.0` | 대화형 Python 셸 (개발용) | 디버깅/탐색 |

---

## 5. 버전별 의존성 차이 (V1/V2/V3)

### 5.1 V1 (로컬 MVP, <=40K/mo)

**포함 패키지** (기본 설치):

| 영역 | 핵심 패키지 |
|------|------------|
| LLM | `langchain-community` (Ollama), `langchain-openai` (GPT-4o mini), `tiktoken` |
| Embedding | `FlagEmbedding` (BGE-M3), `sentence-transformers`, `torch` |
| Vector | `chromadb` |
| Graph | JSON 파일 기반 (별도 패키지 불필요) |
| Storage | `aiosqlite`, `sqlalchemy`, `alembic` |
| Logging | `structlog`, `aiofiles` (JSONL) |
| UI | `@tauri-apps/api`, `react`, `zustand`, `@xyflow/react` |
| Guardrails | `nemoguardrails`, `guardrails-ai` (2-Layer) |
| Agent | `langgraph`, `langchain-core` |
| MCP | `httpx`, `starlette`, `uvicorn` |

**제외/선택 패키지** (`[V2+]` 표시):

| 패키지 | 사유 |
|--------|------|
| `langchain-anthropic` | Claude API는 V2+에서 도입 |
| `qdrant-client` | V1은 Chroma 사용 |
| `asyncpg` | V1은 SQLite, Postgres는 V2+ |
| `transformers` (LlamaGuard) | Layer 3는 GPU 필요, V2+ 옵션 |

### 5.2 V2 (서버, Docker Compose, <=93K/mo)

**V1 대비 추가 패키지**:

| 패키지 | 용도 |
|--------|------|
| `langchain-anthropic` | Claude API 통합 |
| `qdrant-client` | Qdrant 벡터 DB 서버 모드 |
| `asyncpg` | PostgreSQL 비동기 드라이버 |
| `neo4j` (`>=5.27,<6.0`) | Neo4j Community GraphRAG |
| `transformers` | LlamaGuard (Layer 3) 안전 분류 |
| `openai` 임베딩 활성화 | text-embedding-3-small (클라우드 임베딩) |
| `celery` (`>=5.4,<6.0`) [선택] | 비동기 작업 큐 (장시간 태스크) |
| `redis` (`>=5.2,<6.0`) [선택] | 세션/캐시 (Celery 브로커) |

### 5.3 V3 (엔터프라이즈, K8s, <=266K/mo)

**V2 대비 추가 패키지**:

| 패키지 | 용도 |
|--------|------|
| `vllm` | 자체 호스팅 LLM 추론 서버 |
| `prometheus-client` (`>=0.21,<1.0`) | 메트릭 수집 (K8s 모니터링) |
| `opentelemetry-sdk` (`>=1.29,<2.0`) | 분산 트레이싱 (K8s 환경) |
| `opentelemetry-exporter-otlp` (`>=1.29,<2.0`) | OTLP 트레이스 내보내기 |
| `kubernetes` (`>=31.0,<32.0`) [선택] | K8s API 클라이언트 |

### 5.4 버전별 요약 비교표

| 구성 요소 | V1 패키지 | V2 패키지 | V3 패키지 |
|----------|----------|----------|----------|
| **LLM** | langchain-community(Ollama) + langchain-openai | + langchain-anthropic | + vllm |
| **Embedding** | FlagEmbedding(BGE-M3) + torch | + openai(text-embedding-3-small) | + openai(text-embedding-3-large) |
| **Vector DB** | chromadb | qdrant-client | qdrant-client(Cloud) |
| **Graph DB** | (JSON 파일) | neo4j | neo4j(Aura) |
| **Storage** | aiosqlite + sqlalchemy | + asyncpg(Postgres) | + 매니지드 Postgres |
| **Logging** | structlog + aiofiles(JSONL) | + Postgres 로그 | + opentelemetry + prometheus |
| **UI** | @tauri-apps/api + react | + PWA | + PWA |
| **Guardrails** | nemoguardrails + guardrails-ai | + transformers(LlamaGuard) | = V2 |
| **Agent** | langgraph + langchain-core | = V1 | = V1 |
| **MCP** | httpx + starlette | = V1 | = V1 |
| **비용 상한** | 40K KRW/mo ($30) | 93K KRW/mo ($70) | 266K KRW/mo ($200) |

---

## 6. 보안 / 라이선스 검토

### 6.1 라이선스 호환성 매트릭스

| 패키지 | 라이선스 | VAMOS 호환 | 비고 |
|--------|---------|-----------|------|
| React | MIT | 호환 | 자유로운 상용 사용 |
| Tauri | MIT/Apache-2.0 | 호환 | 이중 라이선스 |
| Zustand | MIT | 호환 | |
| LangGraph | MIT | 호환 | LangChain 생태계 |
| langchain-core | MIT | 호환 | |
| Pydantic v2 | MIT | 호환 | |
| ChromaDB | Apache-2.0 | 호환 | |
| Qdrant (OSS) | Apache-2.0 | 호환 | [V2+] |
| Neo4j Community | GPL-3.0 | **주의** | Community 에디션은 GPL, 서버 독립 실행으로 호환 가능 [V2+] |
| NeMo Guardrails | Apache-2.0 | 호환 | |
| Guardrails AI | Apache-2.0 | 호환 | |
| BGE-M3 (BAAI) | MIT | 호환 | 모델 가중치 |
| PyTorch | BSD-3-Clause | 호환 | |
| SQLAlchemy | MIT | 호환 | |
| tiktoken | MIT | 호환 | |
| Recharts | MIT | 호환 | |
| @xyflow/react | MIT | 호환 | |

### 6.2 보안 감사 도구

| 영역 | 도구 | 실행 명령어 | 주기 |
|------|------|-----------|------|
| Frontend | `npm audit` | `npm audit --production` | 매 빌드 |
| Rust | `cargo audit` | `cargo audit` | 매 빌드 |
| Python | `pip-audit` | `pip-audit --strict` | 매 빌드 |
| 전체 | GitHub Dependabot | `.github/dependabot.yml` | 자동 (주간) |

### 6.3 보안 정책

| 정책 | 내용 |
|------|------|
| API 키 보호 | `.env` 파일은 `.gitignore`에 포함, 커밋 금지 |
| 의존성 업데이트 | Dependabot 자동 PR, 보안 패치는 48시간 내 적용 |
| 취약점 대응 | Critical/High 취약점 → 즉시 패치, Medium → 1주 내 |
| 최소 권한 | Tauri 2.0 capabilities로 앱 권한 최소화 |

---

## 7. 문서 이력

| 버전 | 일자 | 변경 내용 |
|------|------|----------|
| 1.0.0 | 2026-02-22 | Phase B3 초기 생성 — Frontend(package.json)/Rust(Cargo.toml)/Python(pyproject.toml) 의존성 목록. A1 COMBO-V1/V2/V3 LOCK 기반. V1/V2/V3 버전별 차이 명시. 보안/라이선스 검토 포함. |
| 1.0.1 | 2026-03-01 | B3-01: pyproject.toml `requires-python = ">=3.11"` 추가 (§4.0). BGE-M3/Pydantic v2 설치 실패 방지. |

---

<\!-- END OF DOCUMENT -->
