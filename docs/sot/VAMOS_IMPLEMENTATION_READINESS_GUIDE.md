# VAMOS AI 구현단계 진입 종합 준비 가이드

> **작성일**: 2026-02-23
> **범위**: V0 → V1 → V2 → V3 전 버전 구현 착수 전 준비사항 전수
> **대상 산출물**: `STEP6_pipeline/output/updated/` 내 39개 문서
> **목적**: 각 버전 구현 착수 전 **반드시** 해소/준비해야 할 항목을 하나도 빠짐없이 정리

---

## 목차

1. [전체 개요: 39개 산출물 5그룹 분류](#1-전체-개요-39개-산출물-5그룹-분류)
2. [V0 구현 착수 전 준비사항 (구조적 기반)](#2-v0-구현-착수-전-준비사항)
3. [V1 구현 착수 전 준비사항 (MVP)](#3-v1-구현-착수-전-준비사항)
4. [V2 구현 착수 전 준비사항 (Pro Server)](#4-v2-구현-착수-전-준비사항)
5. [V3 구현 착수 전 준비사항 (Enterprise K8s)](#5-v3-구현-착수-전-준비사항)
6. [Cross-cutting: 버전 횡단 해소 항목](#6-cross-cutting-버전-횡단-해소-항목)
7. [45개 검증 이슈 전수 매핑표](#7-45개-검증-이슈-전수-매핑표)
8. [파일별 수정 액션 매트릭스](#8-파일별-수정-액션-매트릭스)
9. [구현 진입 GO/NO-GO 체크리스트](#9-구현-진입-gono-go-체크리스트)
10. [부록: 수정사항 파일 기존 항목 반영 상태](#10-부록-수정사항-파일-기존-항목-반영-상태)

---

## 1. 전체 개요: 39개 산출물 5그룹 분류

### 1.1 그룹별 요약

| 그룹 | 파일 수 | 총 줄수 | 역할 | 구현 시 위치 |
|------|--------|---------|------|-------------|
| **A: 설계 3종** | 21 | ~35,472 | BASE+PLAN+DESIGN+SCHEMA — "무엇을 만들지" 정의 | 구현 전 필독 + 상시 참조 |
| **B: 구현 가이드** | 7 | ~9,618 | PHASE_B1~B7 — "어떻게 코딩하지" 정의 | V0부터 필수 |
| **C: 특화 SPEC** | 5 | ~8,543 | MASTER/INVESTING/CLOUD/TEAMS/SDAR — 도메인별 상세 | 해당 도메인 구현 시 |
| **D: STEP7 상세명세** | 5 | ~9,019 | A-E/F-I/J-M/N-P/보강 — 기술 보강 1,545건 | V2+ 보강 참조 |
| **E: 기타** | 1 | ~1,853 | BEGINNER_GUIDE — 온보딩 가이드 | 참조용 |

### 1.2 핵심 결론

**BASE + PLAN + DESIGN만으로는 구현 불가능.** PHASE_B (구현가이드 7종)가 V0부터 필수이며, 이것이 디렉토리 구조, API 계약, 의존성, 설정, 테스트, CI/CD, 마이그레이션 정보를 제공한다.

### 1.3 파일별 버전 참조 타이밍

| # | 파일명 | 줄수 | V0 | V1 | V2 | V3 |
|---|--------|------|:--:|:--:|:--:|:--:|
| 1 | BASE-1.3_VAMOS_RULE_1.3_BASE.md | 633 | **필수** | 필수 | 필수 | 필수 |
| 2 | PLAN-2.0_VAMOS_PLAN_2.0_.md | 4,350 | ~~무시~~ | ~~무시~~ | ~~무시~~ | ~~무시~~ |
| 3 | PLAN-3.0_VAMOS_PLAN_3_0_최종완성본.md | 6,948 | **필수** | 필수 | 필수 | 필수 |
| 4 | D2.0-01 OVERVIEW | ~1,852 | **필수** | 필수 | 필수 | 필수 |
| 5 | D2.0-02 ORANGE CORE | 4,233 | 통독 | **필수** | 필수 | 필수 |
| 6 | D2.0-03 BLUE NODES | 1,938 | 통독 | **필수** | 필수 | 필수 |
| 7 | D2.0-04 INFRA CORE | 1,591 | **필수** | 필수 | 필수 | 필수 |
| 8 | D2.0-05 AGENT WORKFLOW | 1,974 | 통독 | **필수** | 필수 | 필수 |
| 9 | D2.0-06 STORAGE MEMORY | 2,418 | 통독 | **필수** | 필수 | 필수 |
| 10 | D2.0-07 SAFETY COST | 2,608 | 통독 | **필수** | 필수 | 필수 |
| 11 | D2.0-08 UI/UX | 2,484 | 통독 | **필수** | 필수 | 필수 |
| 12 | D2.1-A1 TECH STACK | 401 | 참조 | 참조 | 참조 | 참조 |
| 13 | D2.1-D1 GLOSSARY | 348 | **필수** | 필수 | 필수 | 필수 |
| 14 | D2.1-D2 ORANGE CORE 스키마 | 420 | **필수** | 필수 | 필수 | 필수 |
| 15 | D2.1-D3 BLUE NODES 스키마 | 751 | **필수** | 필수 | 필수 | 필수 |
| 16 | D2.1-D4 INFRA CORE 스키마 | 511 | **필수** | 필수 | 필수 | 필수 |
| 17 | D2.1-D5 AGENT WORKFLOW 스키마 | 630 | **필수** | 필수 | 필수 | 필수 |
| 18 | D2.1-D6 STORAGE MEMORY 스키마 | 389 | **필수** | 필수 | 필수 | 필수 |
| 19 | D2.1-D7 SAFETY COST 스키마 | 588 | **필수** | 필수 | 필수 | 필수 |
| 20 | D2.1-D8 UI/UX 스키마 | 177 | 참조 | **필수** | 필수 | 필수 |
| 21 | D2.1-Q1 AUDIT REPORT | 1,172 | 참조 | 참조 | - | - |
| 22 | PHASE_B1 API CONTRACT | 2,218 | **필수** | 필수 | 필수 | 필수 |
| 23 | PHASE_B2 PROJECT STRUCTURE | 886 | **필수** | 필수 | 필수 | 필수 |
| 24 | PHASE_B3 DEPENDENCIES | 356 | **필수** | 필수 | 필수 | 필수 |
| 25 | PHASE_B4 CONFIG SPEC | 1,170 | **필수** | 필수 | 필수 | 필수 |
| 26 | PHASE_B5 TEST STRATEGY | 945 | 참조 | **필수** | 필수 | 필수 |
| 27 | PHASE_B6 CI/CD PIPELINE | 1,735 | 참조 | **필수** | 필수 | 필수 |
| 28 | PHASE_B7 MIGRATION | 2,308 | - | 참조 | **필수** | 필수 |
| 29 | VAMOS_MASTER_SPECIFICATION | 1,893 | **필수** | 필수 | 필수 | 필수 |
| 30 | VAMOS_AI_INVESTING_SPEC | 1,372 | - | **필수** | 필수 | 필수 |
| 31 | VAMOS_CLOUD_LIBRARY_SPEC | 1,439 | - | 참조 | **필수** | 필수 |
| 32 | VAMOS_AGENT_TEAMS_SPEC | 2,192 | - | 참조 | **필수** | 필수 |
| 33 | VAMOS_SDAR_DESIGN_SPECIFICATION | 1,647 | - | - | **필수** | 필수 |
| 34 | VAMOS_STEP7_A-E_상세명세서 | 1,000 | - | 참조 | **필수** | 필수 |
| 35 | VAMOS_STEP7_F-I_상세명세서 | 2,867 | - | 참조 | **필수** | 필수 |
| 36 | VAMOS_STEP7_J-M_상세명세서 | 1,822 | - | 참조 | **필수** | 필수 |
| 37 | VAMOS_STEP7_N-P_보강_상세명세서 | 1,807 | - | 참조 | **필수** | 필수 |
| 38 | VAMOS_STEP7_보강_통합명세서 | 1,523 | - | - | 참조 | **필수** |
| 39 | VAMOS_BEGINNER_GUIDE | 1,853 | 참조 | 참조 | 참조 | 참조 |

> **범례**: **필수** = 해당 버전 착수 전 반드시 숙지, 통독 = 전체 한번 읽기, 참조 = 필요 시 찾아보기, - = 미사용

---

## 2. V0 구현 착수 전 준비사항

> **V0 정의**: "돌아가는 코어" — 구조적 기반 + 최소 실행 가능 프레임워크
> **예상 기간**: 1~2주

### 2.1 차단 이슈 해소 (V0 착수 전 반드시)

#### 2.1.1 [HIGH] 통신 계층 확정 (V0-004 + V1-015)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | PLAN-3.0은 Python 백엔드(JSON-RPC over subprocess), STEP7 F-Part 2(S7F-012)는 Node.js sidecar(JSON-RPC over stdio) 제시 | - |
| **정본 판단** | PLAN-3.0 > STEP7 (문서 위계상 PLAN이 상위) | - |
| **확정** | **Python 백엔드** (Rust<→Python subprocess, JSON-RPC over stdin/stdout) | PHASE_B1에 이미 정의된 3-Layer 구조 채택 |
| **수정 대상** | STEP7_F-I 내 Node.js sidecar 참조 | "대안 참조"로 격하, 정본 아님 명시 |
| **수정 파일** | STEP7_F-I_상세명세서 (S7F-012 부근) | 비고란에 "PLAN-3.0 정본: Python 백엔드" 추가 |

**확정 아키텍처:**
```
React UI (TypeScript)
    ↓ Tauri IPC (invoke/event) — Layer 1
Rust Backend (IPC Handler + subprocess manager)
    ↓ JSON-RPC over stdin/stdout — Layer 2
Python AI/ML Backend (LangGraph + LLM)
    ↓ MCP Streamable HTTP — Layer 3 (외부 도구)
```

#### 2.1.2 [HIGH] IMPLEMENTATION 계층 문서 부재 (V0-002)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | BASE > PLAN > DESIGN > IMPLEMENTATION 4계층 중 IMPLEMENTATION 계층 산출물 전무 | - |
| **해소** | PHASE_B1~B7이 사실상 IMPLEMENTATION 계층 역할 수행 | MASTER_SPEC에 "PHASE_B = IMPLEMENTATION 계층" 명시 추가 |
| **수정 파일** | VAMOS_MASTER_SPECIFICATION §0 인덱스 | B그룹 설명에 "(= IMPLEMENTATION 계층)" 추가 |

#### 2.1.3 [MEDIUM] V0 비용 상한 미정의 (V0-001)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | V1/V2/V3 비용 상한은 있으나 V0 단계 비용 상한 별도 정의 없음 | - |
| **해소** | V0는 V1 비용 상한을 그대로 적용 (V0 = V1 시작 전 구조 기반이므로) | - |
| **확정 값** | 일일 ₩1,300 / 월 ₩40,000 (BASE-1.3 §5 ABSOLUTE LOCK) | - |
| **수정 파일** | D2.0-01 OVERVIEW §8.5 V0 체크리스트 | "V0 비용 상한 = V1 동일 적용" 명시 |

#### 2.1.4 [MEDIUM] 디렉토리 구조 불일치 (V0-003)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | PHASE_B2는 모노레포 `src-tauri/`, `src/`, `backend/` 구조, STEP7-F는 Node.js sidecar 구조 | - |
| **확정** | PHASE_B2 모노레포 구조가 정본 (PLAN-3.0 우선) | STEP7-F 내 구조 참조를 "대안"으로 격하 |
| **수정 파일** | STEP7_F-I_상세명세서 | 해당 구조 부분에 비고 추가 |

#### 2.1.5 [LOW] config 파일 포맷 혼재 (V0-005)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | MASTER_SPEC: config.yaml, B4: config.toml, STEP7-F: settings.yaml | - |
| **확정** | **config.toml** (PHASE_B4 정본, Pydantic v2 + tomli 파싱) | - |
| **수정 파일** | MASTER_SPEC §6.9, STEP7-F 해당 부분 | config.toml로 통일 표기 |

### 2.2 규칙 임베딩 (BASE-1.3 전수)

BASE-1.3의 모든 규칙이 코드에 반영되어야 한다. **총 24개 카테고리:**

| # | BASE 섹션 | 규칙 | 구현 위치 | 방법 |
|---|----------|------|----------|------|
| 1 | §1.1 | VAMOS Identity: 개인 AI 비서 목적 | system prompt | 시스템 프롬프트에 삽입 |
| 2 | §1.2 | Core Philosophy: 사용자 중심/정확성/최신성/장기 컨텍스트/모듈성 | config + prompt | 설정 + 프롬프트 |
| 3 | §1.3 | Architecture: Front Mini LLM → ORANGE CORE → BLUE NODE → OTHER BRAINS → Main LLM | 전체 구조 | LangGraph StateGraph |
| 4 | §2.1 | Non-goal: 실거래 금지 | Intent filter | I-1에서 "실거래" 키워드 차단 |
| 5 | §2.2 | Non-goal: 해킹/권한상승 금지 | Guardrails L1 | NeMo에서 차단 |
| 6 | §2.3 | Non-goal: 의료/법률 단정 금지 | Guardrails policy | "전문가 상담 필요" 부착 |
| 7 | §2.4 | Non-goal: PII 장기 저장 금지 | I-3 Memory Masking | 주민번호 등 제거 |
| 8 | §2.5 | Non-goal: 저작권/ToS 준수 | MCP tool check | API ToS 검증 |
| 9 | §2.6 | Non-goal: P2 자동 활성화 금지 | RBAC | P2는 명시적 승인 필요 |
| 10 | §2.7 | Non-goal: 위험 함수 자동 실행 금지 | HITL gate | API 호출 시 승인 |
| 11 | §3.1 | API ToS 4항목 체크리스트 | config | api_checklist.json |
| 12 | §3.3 | P2 2단계 승인 + 세션 재확인 + 자동 OFF | D7 ApprovalSchema | 세션 스코프 |
| 13 | §3.4 | 편향/유해 콘텐츠 생성 방지 | Guardrails L2 | Guardrails AI |
| 14 | §4.1~4.6 | 공식 정의: ORANGE CORE, BLUE NODE, Domain, Project, Model Tiers | schemas | contracts.py enum |
| 15 | §5 | 비용 상한 (V1: 40K, V2: 93K, V3: 266K) | D7 CostBudgetSchema | **ABSOLUTE LOCK** |
| 16 | §6.1 | Self-evo 허용 범위: 템플릿/라우팅/프롬프트/QoD/비용 최적화만 | S-series | 승인 게이트 |
| 17 | §6.2 | Self-evo 금지: 정체성/Non-goal/비용천장/승인/P2 생성 | 코드 하드코딩 | config override 불가 |
| 18 | §6.4 | `.vamosrules` JSON/YAML 구조 | config | .vamosrules.json 템플릿 |
| 19 | §7.1 | 4계층(L0~L3) 메모리: Session(7d)/Project(90d)/Core(영구)/Procedural(영구) | D6 MemoryRecord | L0/L1/L2/L3 |
| 20 | §7.2 | 프로젝트 네임스페이스 격리 | RAG query | project_id 필터 |
| 21 | §8.1~8.3 | RAG 검색 순서: 현재 프로젝트 → 글로벌 → 아카이브 | I-2 Evidence | QoD 필터링 |
| 22 | §9.1~9.2 | 승인 2단계: 계획 승인 + 실행 승인 | D7 Approval FSM | plan/execute stage |
| 23 | §10 | 로깅 3파트: Evidence+Audit+Answer, LogEvent 필수 | D2 LogEvent | trace_id 전역 |
| 24 | §11 | 위계: BASE → PLAN → DESIGN → RUN (불변) | config load order | B4 §1.2 |

### 2.3 환경 구축

#### 2.3.1 필수 소프트웨어

| 소프트웨어 | 버전 | 용도 | 비고 |
|-----------|------|------|------|
| Python | 3.11+ | AI/ML 백엔드 | venv 사용 |
| Node.js | 18+ | React/Tauri 프론트엔드 | LTS |
| Rust | 1.70+ | Tauri 2.0 IPC 계층 | stable |
| Ollama | 0.1+ | 로컬 LLM 서빙 | llama3.2:3b + llama3.1:8b |
| Git | 최신 | 소스 관리 | - |

#### 2.3.2 Python 의존성 (pyproject.toml)

> **전체 의존성 목록은 PHASE_B3_DEPENDENCIES.md를 참조.** 아래는 핵심 패키지만 발췌.

```toml
[tool.poetry.dependencies]
# === Core ===
pydantic = ">=2.10,<3.0"           # V2 validation LOCK
pydantic-settings = ">=2.7,<3.0"   # Config 로딩
langgraph = ">=0.2.60,<1.0"        # StateGraph LOCK
langchain-core = ">=0.3.25,<1.0"
langchain-community = ">=0.3.15,<1.0"
langchain-openai = ">=0.2.14,<1.0"
# === Embedding ===
FlagEmbedding = ">=1.3.0,<2.0"     # BGE-M3 LOCK
sentence-transformers = ">=3.3,<4.0"
torch = ">=2.5,<3.0"               # 로컬 추론
openai = ">=1.58,<2.0"             # API fallback
# === Storage ===
chromadb = ">=0.5.23,<1.0"         # Vector DB V1
sqlalchemy = ">=2.0.36,<3.0"       # DB ORM
aiosqlite = ">=0.20.0,<1.0"        # Async SQLite
alembic = ">=1.14.0,<2.0"          # DB migrations
# === Safety ===
nemoguardrails = ">=0.11.0,<1.0"   # Layer 1
guardrails-ai = ">=0.5.15,<1.0"    # Layer 2
tiktoken = ">=0.8.0,<1.0"          # Token counting LOCK
# === MCP ===
httpx = ">=0.28,<1.0"              # MCP HTTP client
starlette = ">=0.41,<1.0"          # MCP server
uvicorn = ">=0.34,<1.0"            # MCP server 실행
sse-starlette = ">=2.2,<3.0"       # SSE 스트리밍
# === Utils ===
python-dotenv = ">=1.0,<2.0"       # .env 로딩
structlog = ">=24.4,<25.0"         # 구조화 로깅
orjson = ">=3.10,<4.0"             # 고속 JSON
tenacity = ">=9.0,<10.0"           # API 재시도
aiofiles = ">=24.1,<25.0"          # 비동기 파일 I/O

[tool.poetry.group.dev.dependencies]
pytest = ">=8.3"
pytest-asyncio = ">=0.24"
ruff = ">=0.8"
mypy = ">=1.13"
coverage = ">=7.6"
```

#### 2.3.3 Frontend 의존성 (package.json)

> **전체 목록은 PHASE_B3_DEPENDENCIES.md §2 참조.** 아래는 핵심만 발췌.

```json
{
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-router-dom": "^6.28.0",
    "@tauri-apps/api": "^2.2.0",
    "@tauri-apps/plugin-shell": "^2.2.0",
    "zustand": "^5.0.0",
    "@tanstack/react-query": "^5.62.0",
    "@xyflow/react": "^12.4.0",
    "zod": "^3.24.0",
    "recharts": "^2.14.0",
    "date-fns": "^4.1.0",
    "lucide-react": "^0.468.0"
  },
  "devDependencies": {
    "typescript": "^5.7.0",
    "vite": "^6.0.0",
    "vitest": "^2.1.0",
    "tailwindcss": "^3.4.0",
    "eslint": "^9.15.0",
    "prettier": "^3.4.0"
  }
}
```

#### 2.3.4 Rust 의존성 (Cargo.toml)

> **전체 목록은 PHASE_B3_DEPENDENCIES.md §3 참조.** 아래는 핵심만 발췌.

```toml
[dependencies]
tauri = { version = "^2.2", features = ["tray-icon"] }
tauri-plugin-shell = "^2.2"
serde = { version = "^1.0", features = ["derive"] }
serde_json = "^1.0"
tokio = { version = "^1.42", features = ["full"] }
reqwest = { version = "^0.12", features = ["json"] }
chrono = { version = "^0.4", features = ["serde"] }
uuid = { version = "^1.11", features = ["v4"] }
thiserror = "^2.0"
anyhow = "^1.0"
tracing = "^0.1"
tracing-subscriber = "^0.3"
toml = "^0.8"
dirs = "^5.0"

[build-dependencies]
tauri-build = "^2.2"
```

### 2.4 디렉토리 스캐폴딩 (PHASE_B2 기준)

> **완전한 디렉토리 구조는 PHASE_B2_PROJECT_STRUCTURE.md (886줄) 참조.** 아래는 V0 핵심 구조만 발췌.
> 누락된 상세 디렉토리: `shared/` (크로스 언어 타입), `scripts/` (setup/dev/build), `tests/` (루트 통합 테스트), `docs/`, `.vscode/`, `config/` 하위 구조 (llm/, embedding/, storage/, safety/, mcp/).

```
vamos/                              (Monorepo LOCK)
├── .github/workflows/              CI/CD (V0: 최소 설정)
├── src/                            React UI
│   └── components/decision/        DecisionCard 컴포넌트
├── src-tauri/                      Rust 백엔드
│   ├── src/commands/               기본 IPC 스텁
│   ├── src/bridge/                 Python subprocess 관리
│   │   ├── python_manager.rs       subprocess launcher
│   │   └── ipc_protocol.rs         JSON-RPC 프로토콜
│   └── src/models/                 D2~D7 스키마 Rust 구조체
├── backend/                        Python AI/ML 코어
│   ├── vamos_core/
│   │   ├── orange_core/            I-1~I-5 스켈레톤
│   │   ├── blue_nodes/             BaseNode + 도메인 스텁
│   │   ├── infra/                  Brain/Tool/Cache/RateLimit
│   │   ├── agent/                  LangGraph StateGraph
│   │   ├── storage/                L0 메모리 only
│   │   ├── safety/                 Policy/Approval/Cost gates
│   │   └── schemas/                Pydantic v2 contracts.py
│   ├── main.py                     IPC 서버 진입점 (stdin/stdout)
│   └── tests/                      Pytest fixtures
├── config/
│   ├── config.v1.toml              V1 프리셋 (LOCK 값)
│   ├── .vamosrules.json            BASE 규칙 적용
│   └── .env.example                API 키 템플릿
├── data/
│   ├── sqlite/                     vamos.db
│   ├── chroma/                     벡터 DB
│   ├── logs/                       JSONL 로그
│   ├── graph/                      graph.json
│   └── backups/                    백업 스냅샷
└── .env.example                    (git-safe 템플릿)
```

### 2.5 설정 파일 구성 (PHASE_B4 기준)

**config.v1.toml LOCK 값:**

| 설정 키 | V0/V1 값 | LOCK 여부 | 근거 |
|---------|----------|----------|------|
| `core.autonomy_level` | L1 | - | V0: 수동 제어 |
| `core.single_decision_lock` | true | **LOCK** | 불변 원칙 |
| `llm.mini_model` | ollama/llama3.2:3b | - | 비용 최소화 |
| `llm.main_model` | ollama/llama3.1:8b | - | 로컬 메인 |
| `llm.fallback_model` | gpt-4o-mini | - | API 대체 |
| `embedding.model` | bge-m3 | **LOCK** | DEC-005 |
| `embedding.dimension` | 1024 | **LOCK** | BGE-M3 고정 |
| `vector_db.backend` | chroma | **LOCK** | AC-D6-008 |
| `vector_db.mode` | embedded | - | 서버 불필요 |
| `graph_db.backend` | json_file | **LOCK** | AC-D6-009 |
| `storage.backend` | sqlite | - | V1 전용 |
| `cost.daily_limit` | 1300 | **ABSOLUTE LOCK** | BASE §5 |
| `cost.monthly_limit` | 40000 | **ABSOLUTE LOCK** | BASE §5 |
| `cost.warn_threshold` | 80 | **LOCK** | D7 Downshift |
| `cost.block_threshold` | 100 | **LOCK** | D7 Downshift |
| `guardrails.layer1_enabled` | true | - | NeMo |
| `guardrails.layer2_enabled` | true | - | Guardrails AI |
| `guardrails.layer3_enabled` | false | - | V0: GPU 부하 방지 |
| `semantic_cache.similarity_threshold` | 0.95 | **LOCK** | AC-D6-010 |
| `logging.trace_id_required` | true | **LOCK** | D2 LogEvent |
| `mcp.transport` | streamable_http | **LOCK** | DEC-017 |

### 2.6 스키마 코드 생성 (D2.1-D1~D8 → 실제 코드)

D2.1 스키마 문서의 ~40개 JSON Schema를 3개 언어로 변환:

| 대상 | 파일 위치 | 소스 문서 |
|------|----------|----------|
| Python Pydantic v2 모델 | `backend/vamos_core/schemas/` | D2.1-D2~D7 |
| TypeScript Zod 스키마 | `src/types/` | D2.1-D2~D7 |
| Rust serde 구조체 | `src-tauri/src/models/` | D2.1-D2~D7 |

**필수 스키마 목록 (V0에서 생성해야 할 것):**

| 스키마 | 소스 | 우선순위 |
|--------|------|---------|
| DecisionSchema | D2.1-D2 v2.2.1 | CRITICAL |
| LogEventSchema | D2.1-D2 v2.2.1 | CRITICAL |
| EventTypeRegistry | D2.1-D2 | CRITICAL |
| FailureCodeRegistry | D2.1-D2 | CRITICAL |
| FallbackRegistry | D2.1-D2 | CRITICAL |
| NodeRegistrySchema | D2.1-D3 | CRITICAL |
| NodeRequestEnvelope | D2.1-D3 | HIGH |
| NodeResponseEnvelope | D2.1-D3 | HIGH |
| ToolRegistryEntry | D2.1-D4 | HIGH |
| BrainAdapterResponse | D2.1-D4 | HIGH |
| PolicyCheckSchema | D2.1-D7 v2.2.0 | CRITICAL |
| ApprovalSchema | D2.1-D7 v2.2.0 | CRITICAL |
| CostBudgetSchema | D2.1-D7 v2.2.0 | CRITICAL |
| DownshiftSchema | D2.1-D7 v2.2.0 | HIGH |
| GuardrailsCheckSchema | D2.1-D7 v2.3.0 | HIGH |
| RBACRoleSchema | D2.1-D7 v2.3.0 | HIGH |
| AutonomyLevelSchema | D2.1-D7 v2.3.0 | HIGH |
| MemoryRecordSchema | D2.1-D6 | HIGH |
| SourceQoDSchema | D2.1-D6 | HIGH |
| VectorStoreAdapterSchema | D2.1-D6 v2.3.0 | HIGH |
| SemanticCacheSchema | D2.1-D6 v2.3.0 | HIGH |
| WorkflowOutputEnvelope | D2.1-D5 | HIGH |
| CircuitBreakerSchema | D2.1-D5 v2.3.0 | MEDIUM |
| HITLRequestSchema | D2.1-D5 v2.3.0 | MEDIUM |

### 2.7 V0 구현 대상 모듈

| 모듈 | 범위 | 상태 |
|------|------|------|
| I-1 Intent Detector | 기본 의도 파악 + 키워드 필터 | 스켈레톤 |
| I-2 Context Builder | 기본 Evidence/RAG 컨텍스트 | 스켈레톤 |
| I-3 Memory System | L0 세션 메모리만 (L1/L2/L3 미활성) | 최소 구현 |
| I-5 Decision Engine | 단일 결정 잠금 + 기본 Gate(policy/cost/hold) | 스켈레톤 |
| I-19 Approval Manager | HITL 승인 게이트 (P2 = OFF) | 스켈레톤 |
| 비용 엔진 | ₩40,000/월 하드코딩 + 80%/100% 임계값 | 최소 구현 |
| 로깅 | LogEvent JSONL 최소 (1개 파일) | 최소 구현 |
| Guardrails | Layer 1(NeMo) + Layer 2(Guardrails AI) only | 최소 구현 |

### 2.8 V0 GO/NO-GO 체크리스트

```
☐ 통신 계층 확정: Python 백엔드 (V0-004 해소)
☐ BASE-1.3 전 24개 규칙 코드 매핑 완료
☐ PHASE_B2 디렉토리 구조 스캐폴딩 생성
☐ PHASE_B3 의존성 전체 설치 (pip/npm/cargo)
☐ PHASE_B4 config.v1.toml LOCK 값 배치
☐ D2.1 스키마 → Pydantic v2/Zod/serde 코드 생성 (24개)
☐ I-1~I-5 + I-19 스켈레톤 생성
☐ L0 세션 메모리 최소 구현
☐ LogEvent JSONL 최소 구현
☐ 비용 엔진 (₩40,000/월) 하드코딩
☐ Guardrails L1+L2 설정
☐ .env + .vamosrules.json 템플릿 생성
☐ data/ 디렉토리 (sqlite/chroma/logs/graph/backups) 생성
☐ Ollama 로컬 모델 다운로드 (llama3.2:3b, llama3.1:8b)
☐ Chroma 임베디드 DB 초기화
☐ SQLite 스키마 + Alembic 초기 마이그레이션
```

---

## 3. V1 구현 착수 전 준비사항

> **V1 정의**: MVP — Minimum Viable Product (₩40,000/월 로컬)
> **예상 기간**: 8~12주

### 3.1 차단 이슈 해소 (V1 착수 전 반드시)

#### 3.1.1 [HIGH] I-Series 모듈 카운트 통일 (V1-001 + V1-016)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | PLAN-3.0: I-1~I-21, D2.0-02: I-1~I-24, SDAR: I-25 추가, BEGINNER_GUIDE: I-21~I-23 누락 | - |
| **확정** | **I-1~I-25 (25개 모듈)** 이 정본 | PLAN-3.0에는 I-21까지만 있으나, 이후 설계 확장에서 I-22~I-25 추가됨 |
| **수정 파일** | BEGINNER_GUIDE I-Series 표 | I-21~I-23 추가 |
| **수정 파일** | MASTER_SPEC I-Series 인덱스 | I-21~I-25 전수 확인 |
| **수정 파일** | PLAN-3.0 §13.1 | I-22~I-25 참조 추가 (또는 "DESIGN에서 확장됨" 명시) |

**I-21~I-25 정의:**

| ID | 명칭 | 역할 | V1 상태 |
|----|------|------|---------|
| I-21 | Source Evolution | 소스 진화/최적화 | COND |
| I-22 | Task/Project Manager | 태스크/프로젝트 관리 | OFF (V2) |
| I-23 | Doc/Code Structuring | 문서/코드 구조화 | OFF (V2) |
| I-24 | Knowledge Graph Engine | 그래프 RAG | OFF (V3) |
| I-25 | SDAR Engine | 자가진단-수리 | OFF (V2) |

#### 3.1.2 [HIGH] E-15 모듈 명칭 충돌 (V1-002)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | MASTER_SPEC/BEGINNER_GUIDE: E-15 = "File System Access", CLOUD_LIBRARY_SPEC: E-15 = "Cloud Collector" | - |
| **해소** | E-15 = **"File System / Cloud Collector" (겸용)** | D2.0-01에 이미 겸용 처리됨 |
| **수정 파일** | MASTER_SPEC E-Series 표 | E-15 명칭을 "File System / Cloud Collector" 로 변경 |
| **수정 파일** | BEGINNER_GUIDE E-Series 표 | 동일 변경 |

#### 3.1.3 [HIGH] S-5 모듈 명칭 충돌 (V1-003)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | MASTER_SPEC: S-5 = "Router Evolution", CLOUD_LIBRARY_SPEC: S-5 = "Cloud Evolver" | - |
| **해소** | S-5 = **"Router Evolution / Cloud Evolver" (겸용)** | - |
| **수정 파일** | MASTER_SPEC S-Series 표 | S-5 명칭을 겸용으로 변경 |
| **수정 파일** | BEGINNER_GUIDE S-Series 표 | 동일 변경 |

#### 3.1.4 [HIGH] 38개 DEFER/TBD 분류 (V1-008)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | D2.0-01 §7.2에 70개 DEFER/TBD 중 38개 미해소, V1 차단 항목 미분류 | - |
| **해소** | 38개를 V1-MUST / V2-DEFER / V3-DEFER로 분류 | - |
| **수정 파일** | D2.0-01 OVERVIEW §7.2 | 각 항목에 대상 버전 태그 추가 |

**분류 기준:**
- D2.1 스키마 DECISION_NEEDED 16건: **전수 해소 완료** (Q1 Audit 확인)
- DESIGN 2.0 본문 DEFER: 01(1건 V2+), 02(2건 V1.1), 04(1건 V3) → **V1 차단 없음**
- 도메인 SPEC DEFER: AI_INVESTING(2전략 V2+), AGENT_TEAMS(5건 V1.1~V3), SDAR(전체 V2+) → **V1 차단 없음**
- **결론: V1 차단 DEFER/TBD = 0건** (전부 V1.1 이후로 이관됨)

#### 3.1.5 [HIGH] datetime.utcnow() 위반 수정 (V1-005)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | AGENT_TEAMS_SPEC의 AgentMessage 클래스에서 `datetime.utcnow()` 사용 (PEP 594 deprecated) | - |
| **해소** | `datetime.now(timezone.utc)` 로 교체 | - |
| **수정 파일** | VAMOS_AGENT_TEAMS_SPEC 코드 예시 전수 | `datetime.utcnow` → `datetime.now(timezone.utc)` |

### 3.2 모듈 스코프 확정

#### 3.2.1 V1 활성 모듈 (ON)

| 시리즈 | 활성 모듈 | 수 |
|--------|----------|---|
| I-Series | I-1~I-5, I-6, I-8, I-9, I-10, I-11, I-13~I-17, I-19, I-20 | 17 |
| S-Series | S-1 (Self-check Engine) | 1 |
| E-Series | E-1~E-6 (기본 외부 도구) | 6 |
| A-Series | A-1, A-2 (기본 분석) | 2 |
| B-Series | B-1, B-4 (Episodic + Working Memory) | 2 |

#### 3.2.2 V1 비활성 모듈 (OFF / COND)

| 모듈 | 상태 | 활성화 시점 |
|------|------|-----------|
| I-7 | OFF | V2 |
| I-12 Workflow Builder | COND (OFF→COND) | V2 |
| I-18 Self-evo Engine | OFF | V3 |
| I-21 Source Evolution | COND | V1.1 |
| I-22 Task/Project Manager | OFF | V2 |
| I-23 Doc/Code Structuring | OFF | V2 |
| I-24 Knowledge Graph Engine | OFF | V3 |
| I-25 SDAR Engine | OFF | V2 |
| S-6~S-8 | OFF | V2/V3 |
| E-7~E-16 | COND/OFF | V2/V3 |

### 3.3 스키마 정합성 확인

#### 3.3.1 Decision.approval_status enum 통일 (V1-004)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | MASTER_SPEC Decision: "pending" 포함, D2 SOT: "approved\|denied"만, D7: "approved/denied/pending/expired" | - |
| **확정** | D7이 SOT → **approved / denied / pending / expired** 4개 | - |
| **수정 파일** | D2.1-D2 DecisionSchema | approval_status enum에 pending/expired 추가 |
| **수정 파일** | MASTER_SPEC Decision 스키마 | D7 SOT와 일치하도록 수정 |

#### 3.3.2 QoD 가중치 공식 통일 (V1-006)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | MASTER_SPEC: 4요소(relevance 0.30, accuracy 0.25, freshness 0.25, completeness 0.20), PLAN-3.0: 5요소(Accuracy 0.30, Relevance 0.25, Completeness 0.20, Safety 0.15, Efficiency 0.10) | - |
| **확정** | PLAN-3.0이 상위 → **5요소 공식이 정본** | - |
| **수정 파일** | MASTER_SPEC §8.8 QoD 절 | PLAN-3.0 5요소 공식으로 통일 |
| **수정 파일** | BEGINNER_GUIDE QoD 설명 | 동일 5요소로 수정 |
| **수정 파일** | D2.1-D6 SourceQoDSchema | 5개 필드(accuracy, relevance, completeness, safety, efficiency) 반영 |

#### 3.3.3 Front Mini LLM 모듈 ID (V1-007)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | "Front Mini LLM"이 반복 언급되나 I/E/S/A 어떤 시리즈에도 모듈 ID 미부여 | - |
| **확정** | **I-1 Intent Detector의 내부 서브컴포넌트** (별도 모듈 ID 불필요) | - |
| **수정 파일** | D2.0-02 I-1 섹션 | "Front Mini LLM은 I-1의 내부 서브컴포넌트" 명시 |
| **수정 파일** | MASTER_SPEC | 동일 명시 |

#### 3.3.4 Guardrails 계층 수 통일 (V1-010)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | D2.0-07/D2.1-D7: 3-Layer, MASTER_SPEC §7.13: 4-Layer (+L4 Post-delivery Audit) | - |
| **확정** | **4-Layer가 정본** (L4는 V2+에서 활성화) | - |
| **수정 파일** | D2.1-D7 GuardrailsCheckSchema | L4 필드 추가 (V1=null/skipped, V2+=active) |
| **수정 파일** | D2.0-07 | 4-Layer 명시 (L4 = Post-delivery Audit) |

#### 3.3.5 비용 상한 수치 통일 (V1-013)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | BASE-1.3/D7: V1 ₩40,000/월(~$30), STEP7-F: V1 <=$8/mo(~₩10,400) | - |
| **확정** | **BASE-1.3이 정본** → ₩40,000/월 | STEP7-F의 $8은 "최소 운영 목표"로 재해석 |
| **수정 파일** | STEP7_F-I 비용 섹션 | "BASE 상한: ₩40,000/월, 최소 운영 목표: $8/월" 구분 명시 |

#### 3.3.6 React 버전 통일 (V1-014)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | A1/PHASE_B3: React 18, STEP7-F: React 19 | - |
| **확정** | **React 18.3** (PHASE_B3 정본, 안정 버전) | - |
| **수정 파일** | STEP7_F-I React 버전 참조 | "React 18 (PHASE_B3 정본)" 명시 |

#### 3.3.7 LangChain import Allowlist (V1-009)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | DEC-001: "LangChain import 금지" FREEZE, 그러나 PHASE_B3에 langchain-core 의존성 포함 | - |
| **확정** | langchain-core는 adapter exception으로 허용, langchain 전체 패키지는 금지 | - |
| **수정 파일** | D2.0-02 DEC-001 비고 | "허용 범위: langchain-core, langchain-community, langchain-openai (adapter only). langchain 본체 import 금지" |

### 3.4 스토리지 스택 구축

| 컴포넌트 | V1 기술 | 초기화 방법 | 참조 문서 |
|---------|---------|-----------|----------|
| 관계형 DB | SQLite (vamos.db) | Alembic 마이그레이션 | D2.0-06, B4 |
| 벡터 DB | Chroma embedded | 자동 생성 (data/chroma/) | D2.0-06, D2.1-D6 |
| 그래프 DB | JSON file (NetworkX) | 빈 graph.json 생성 | D2.0-06 |
| 로그 | JSONL append-only | data/logs/events.jsonl | D2.0-02, D2.1-D2 |
| 캐시 | SQLite embedding_cache 테이블 | Alembic 포함 | D2.1-D6 |
| 백업 | data/backups/ | 디렉토리 생성 | B4 |
| L0 메모리 | In-memory LRU | 코드 내 | D2.0-06 |
| L1 메모리 | SQLite + Chroma | Session end → L1 전환 | D2.0-06 |

### 3.5 보안 설정 (STEP7 E-Series CRITICAL)

| ID | 항목 | V1 구현 | 우선순위 |
|----|------|---------|---------|
| S7E-001 | STRIDE 위협 모델링 | 문서화 + 기본 대응 | CRITICAL |
| S7E-003 | OWASP Top 10 for LLM | 전 항목 컨트롤 매핑 | CRITICAL |
| S7E-005 | API Key 관리 | .env + dotenv + .gitignore | HIGH |
| S7E-006 | 입력 검증 | Zod + regex 패턴 | HIGH |
| S7E-008 | Rate limiting/Cost | 로컬 카운터 + 일일/월간 하드캡 | HIGH |
| S7E-011 | Instruction hierarchy | System/user/tool 우선순위 | CRITICAL |
| S7E-012 | Input/Output tagging | XML 태그 기반 신뢰 경계 | CRITICAL |
| S7E-013 | Canary token 감지 | 정적 canary (V1) | CRITICAL |
| S7E-015 | Tool call 검증 | Whitelist + 기본 체크 | CRITICAL |
| S7E-017 | Jailbreak 방어 | Guardrail override 차단 | HIGH |
| S7E-021 | 로컬 인증 | PIN/생체 (Windows Hello) | CRITICAL |
| S7E-031 | PII 감지/마스킹 | 정규식 패턴 (한국+글로벌) | CRITICAL |
| S7E-032 | 데이터 암호화 (at-rest) | SQLCipher (AES-256-CBC) | CRITICAL |
| S7E-033 | 데이터 주권 | 전부 로컬, 클라우드 전송 금지 | CRITICAL |

### 3.6 테스트 인프라 (PHASE_B5)

| 카테고리 | 테스트 대상 | 커버리지 목표 |
|---------|-----------|-------------|
| 스키마 테스트 | D2/D7 전체 스키마 Pydantic 검증 | 100% |
| Core 로직 | I-1~I-5 Decision kernel, Intent parser | 80%+ |
| Blue Node | NodeRegistry, Request/Response Envelope | 80%+ |
| Safety/Cost | PolicyCheck, Approval, CostBudget, Downshift | 100% |
| Memory/Storage | MemoryRecord, VectorStore, SemanticCache | 80%+ |
| Workflow | 5-stage pipeline, VerifyChain, CircuitBreaker | 80%+ |
| 통합 | 전체 request→decision→execution 흐름 | 핵심 경로 100% |
| AC 검증 | AC-D2-001~003, AC-D7-001~007, AC-D6-010 등 | 100% |

### 3.7 CI/CD 설정 (PHASE_B6)

```
GitHub Actions (.github/workflows/ci.yml)
├── Stage 1: Dependencies (poetry install / cargo build / npm ci)
├── Stage 2: Linting (ruff / clippy / eslint)
├── Stage 3: Type Check (mypy / cargo check / tsc)
├── Stage 4: Unit Tests (pytest 80%+ / cargo test / vitest 60%+)
├── Stage 5: Integration Tests (pytest + subprocess)
├── Stage 6: Security Scans (npm audit / pip-audit)
├── Stage 7: Build Artifacts (wheel / binary / Tauri app)
└── Stage 8: Coverage Reports (80% Python 강제)
```

### 3.8 V1 구현 순서 (주차별)

| 주차 | 구현 대상 | 참조 파일 |
|------|----------|----------|
| 1~2 | ORANGE CORE 기본 파이프라인 (I-1→I-2→I-5→I-8) | D2.0-02, D2.1-D2, B1 |
| 3~4 | Storage/Memory + RAG (L0/L1, Chroma, BM25+Vector) | D2.0-06, D2.1-D6, B1 |
| 5~6 | Workflow Engine (LangGraph StateGraph, 5-Pipeline, TEE) | D2.0-05, D2.1-D5, B1 |
| 7~9 | UI/UX (Tauri+React, Builder/Hologram View, 3단 패널) | D2.0-08, D2.1-D8, B1 |
| 10~12 | 통합 + AI Investing Paper Trading MVP + E2E 테스트 | AI_INVESTING_SPEC, B5 |

### 3.9 V1 GO/NO-GO 체크리스트

```
☐ I-Series 25개 모듈 정본 확정 (V1-001, V1-016 해소)
☐ E-15, S-5 명칭 겸용 처리 (V1-002, V1-003 해소)
☐ 38개 DEFER/TBD → V1 차단 0건 확인 (V1-008 해소)
☐ datetime.utcnow() 전수 교체 (V1-005 해소)
☐ Decision.approval_status enum 4개 통일 (V1-004 해소)
☐ QoD 5요소 공식 통일 (V1-006 해소)
☐ Front Mini LLM = I-1 내부 서브컴포넌트 명시 (V1-007 해소)
☐ Guardrails 4-Layer 명시 (V1-010 해소)
☐ 비용 상한 ₩40,000/월 통일 (V1-013 해소)
☐ React 18.3 통일 (V1-014 해소)
☐ LangChain Allowlist 명시 (V1-009 해소)
☐ 14개 보안 항목 (S7E) 전수 구현
☐ 테스트 인프라 + CI/CD 설정 완료
☐ V0 GO 체크리스트 전수 통과
☐ Python 백엔드 진입점 정의 (V1-015 → V0에서 해소됨)
```

---

## 4. V2 구현 착수 전 준비사항

> **V2 정의**: Pro Server — 서버 배포 + 멀티에이전트 + 확장 기능 (₩93,000/월)
> **V1→V2 전환 조건**: QoD≥0.85(30일), RAG정확도≥60%, 메모리오류<1%, P0테스트100%, 비용초과0(30일), 사용자승인

### 4.1 차단 이슈 해소 (V2 착수 전 반드시)

#### 4.1.1 [HIGH] Agent Teams vs FREEZE 충돌 (V2-003)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | MASTER_SPEC §7.2: "멀티에이전트 자유 상호 호출/무한 대화 금지" (FREEZE), AGENT_TEAMS_SPEC: Sub-agent 간 MessageBus 직접 통신 설계 | - |
| **확정** | **Lead Agent 통한 단방향 위임만 V1 허용, MessageBus 기반 통신은 V2에서 도입** | - |
| **해석** | FREEZE 규칙 = "자유 상호 호출" 금지 (무제한). MessageBus = "관리된 통신" (Lead Agent 감사). 양립 가능 | - |
| **수정 파일** | MASTER_SPEC §7.2 | FREEZE 해석 명확화: "자유 상호 호출 = 무제한 P2P 호출 금지. Lead Agent 경유 MessageBus 허용" |
| **수정 파일** | AGENT_TEAMS_SPEC | "V1: Lead Agent 위임만, V2: MessageBus (Lead 감사 하에)" 명시 |

#### 4.1.2 [HIGH] STEP7 TITLE_ONLY 44% (V2-008)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | STEP7 1,545건 중 ~675건(44%)이 TITLE_ONLY (제목만 존재) | - |
| **해소** | V2 착수 전 STEP7 중 V2 CRITICAL 항목의 상세 스펙 보강 필수 | - |
| **우선 대상** | F(인프라 66건), K(에이전트 61건), G(벤치마크 63건) | - |
| **작업량** | ~190건 상세 스펙 작성 (V2 전) | - |

#### 4.1.3 [MEDIUM] 10-Layer 명칭 충돌 (V2-001)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | MASTER_SPEC: VAMOS 전체 10계층(UI~Config), CLOUD_LIBRARY: 별도 10-Layer(INPUT~OUTPUT) | - |
| **해소** | Cloud Library 10-Layer를 "CL-Layer" 접두어로 구분 | - |
| **수정 파일** | CLOUD_LIBRARY_SPEC | "CL-Layer 1~10" 표기로 변경 |

### 4.2 데이터 마이그레이션 (PHASE_B7)

#### 4.2.1 SQLite → PostgreSQL

| 항목 | 상세 |
|------|------|
| 소스 | ~/.vamos/vamos.db (SQLite) |
| 타겟 | PostgreSQL 16 (Neon/Supabase) |
| 스크립트 | migrations/versions/002_add_v2_tables.py (Alembic) |
| 검증 | 행 수 일치, 데이터 타입 변환, UUID 생성 |
| **준비 사항** | ☐ SQLite 스키마 완전성 검증 ☐ SQLite→PostgreSQL 타입 매핑 ☐ 전체 DB 백업 ☐ 스테이징 dry-run 테스트 |

#### 4.2.2 Chroma → Qdrant 벡터 마이그레이션 (V2-005)

| 단계 | 시점 | 작업 | 검색 모드 |
|------|------|------|----------|
| Phase 1 | V2 배포일 | V2 Qdrant 컬렉션 생성, 신규 데이터만 V2 | 하이브리드 (V1+V2) |
| Phase 2 | Day 1~7 | V1 벡터 → V2로 재임베딩 (text-embedding-3-small) | 하이브리드 (V1 페널티) |
| Phase 3 | Day 7~14 | 재임베딩 완료 검증, V1 비활성화 | V2 only |
| Phase 4 | Day 30+ | V1 컬렉션 삭제 | V2 프로덕션 |

**CRITICAL**: `needs_reembedding=True` 플래그를 Qdrant 메타데이터에 구현 필수

#### 4.2.3 NetworkX JSON → Neo4j (V2-006)

| 항목 | 상세 |
|------|------|
| 소스 | knowledge_graph.json (NetworkX + JSON) |
| 타겟 | Neo4j Community (50K 노드 제한) |
| 변환 | JSON 그래프 → Cypher 쿼리 매핑 |
| **준비 사항** | ☐ Entity 유일성 제약 ☐ Relationship type 매핑 ☐ Property 검증 |

#### 4.2.4 JSONL → PostgreSQL + Loki (V2-004)

| 항목 | 상세 |
|------|------|
| 소스 | ~/.vamos/logs/*.jsonl |
| 타겟 | PostgreSQL logs 테이블 + Loki (V2+) |
| 전략 | 배치 삽입 + 시계열 인덱싱 |

### 4.3 V2 인프라 구축

| 컴포넌트 | 기술 | 우선순위 |
|---------|------|---------|
| Web App | Next.js 15 PWA | HIGH |
| API Gateway | Nginx/Traefik | HIGH |
| App Server | Node.js + LangGraph | CRITICAL |
| Main DB | PostgreSQL 16 | CRITICAL |
| Vector DB | Qdrant Server | CRITICAL |
| Graph DB | Neo4j Community | HIGH |
| Cache | Redis 7 | HIGH |
| File Storage | MinIO/R2 | HIGH |
| Message Queue | BullMQ | MEDIUM |
| WebSocket | Socket.io | MEDIUM |

### 4.4 V2 비용 목표

| 항목 | 금액 | 비고 |
|------|------|------|
| VPS | ~₩20,000/월 | - |
| DB (PostgreSQL) | ~₩10,000/월 | Neon/Supabase Free tier |
| API 비용 | ~₩10,000/월 | Claude/OpenAI |
| **합계** | ~₩40,000/월 | BASE 상한 ₩93,000 이내 |

### 4.5 V2 SDAR 활성화 조건 (V2-002)

| 조건 | 상세 |
|------|------|
| V2 SDAR 상태 | COND (조건부) |
| 허용 AR 레벨 | AR-L2 → AR-L3 (LOW + MEDIUM 리스크) |
| 필수 전제 | ☐ S-4 Pattern Miner 통합 ☐ 스냅샷 시스템 구현 ☐ 5개 수리 액션 구현 |
| 활성화 트리거 | LOW 리스크 성공률 ≥95% (30일), 오탐률 <5% |

### 4.6 V2 Agent Teams 구축

| 항목 | V1 | V2 | 결정 필요 |
|------|-----|-----|----------|
| 최대 병렬 에이전트 | 3 | 10 | LOCK |
| MessageBus | In-memory | Redis | DEFER-AT-001 (V1.1에서 결정) |
| Debate Mode | OFF | COND | - |
| Delegation Chain | N/A | 최대 3단계 | LOCK-AT-004 |
| GroupChat 순서 | N/A | 알고리즘 필요 | DEFER-AT-002 |

### 4.7 V2 GO/NO-GO 체크리스트

```
☐ V1 전환 조건 충족 (QoD≥0.85, RAG≥60%, 메모리오류<1%, P0 100%, 비용초과0, 사용자승인)
☐ Agent Teams vs FREEZE 해석 확정 (V2-003 해소)
☐ STEP7 V2 CRITICAL 항목 상세 스펙 보강 (~190건)
☐ 10-Layer 명칭 충돌 해소 (V2-001)
☐ SQLite → PostgreSQL 마이그레이션 테스트 완료 (V2-004)
☐ Chroma → Qdrant 재임베딩 전략 구현 (V2-005)
☐ NetworkX → Neo4j 변환 규칙 정의 (V2-006)
☐ SDAR V2 COND 활성화 조건 확정 (V2-002)
☐ MessageBus 구현 방식 결정 (Redis vs In-Memory)
☐ V2 서버 인프라 10개 컴포넌트 구축
☐ V2 비용 모니터링 대시보드 구축
☐ STEP7 비용 vs BASE 비용 괴리 인지 (V2-007)
☐ Cloud Library E-15/S-5 인터페이스 검증
☐ V1 GO 체크리스트 전수 통과
```

---

## 5. V3 구현 착수 전 준비사항

> **V3 정의**: Enterprise K8s — 대규모 배포 + 완전 자율 + 자기진화 (₩266,000/월)
> **V2→V3 전환 조건**: QoD≥0.90(60일), 2-tier LLM 최적화 완료, Self-evo 검증, V3 비용 재검토+승인

### 5.1 차단 이슈 해소

#### 5.1.1 [MEDIUM] K8s 배포 명세 보강 (V3-001)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | STEP7 S7F-031~036에서 K8s 언급하나 각 3~5줄 수준 | - |
| **해소** | V2 운영 기간 중 K8s 상세 명세 작성 (Helm Chart, 멀티리전, GPU 클러스터) | - |
| **작성 대상** | 신규 문서 또는 STEP7 보강 | Helm Chart 상세, ArgoCD 파이프라인, 멀티리전 전략 |

#### 5.1.2 [MEDIUM] Self-evo 거버넌스 상세 (V3-002)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | S-8 Self-evo Governance가 "자기진화의 관리자"로만 정의 | - |
| **해소** | 승인 절차, 롤백 조건, 인간 개입 시점, SDAR I-25 AR-L4 관계 상세화 | - |
| **수정 파일** | D2.0-02 S-8 섹션 + SDAR_SPEC | 거버넌스 프로토콜 상세 추가 |

#### 5.1.3 [LOW] V3 비용 상한 현실성 (V3-003)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | V3 ₩266,000/월 상한, GPU A10G 24/7만 ~$144/월, K8s+DB+모니터링 시 초과 가능 | - |
| **해소** | V2 운영 데이터 기반 V3 비용 재산정, 필요 시 BASE-1.3 비용 상한 조정 승인 | - |

#### 5.1.4 [LOW] GraphRAG 90% 목표 근거 (V3-004)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | MASTER_SPEC V3 GraphRAG 목표 정확도 90%+ 이나 벤치마크 기준/측정 방법 미정의 | - |
| **해소** | V2 운영 중 벤치마크 셋 + 측정 방법 정의 | - |

### 5.2 V3 SDAR 완전 활성화 조건

| 조건 | 상세 |
|------|------|
| V3 SDAR 상태 | ON (완전 자율) |
| 허용 AR 레벨 | AR-L4 (HIGH 리스크 포함) |
| **V2→V3 전이 조건** | ☐ V2 수리 성공률 ≥95% (60일) ☐ 스냅샷 복원 성공 100% ☐ S-4 패턴 매칭 정확도 ≥80% ☐ 수리 후 회귀율 <2% ☐ S-8 거버넌스 감사 통과 ☐ Owner 승인 |

### 5.3 V3 STEP7 TITLE_ONLY 잔여 보강

| 카테고리 | TITLE_ONLY 수 | V3 전 보강 필요 |
|---------|-------------|---------------|
| H (비즈니스 모델) | ~58건 | 전수 |
| I (AI 투자) | ~66건 | 전수 |
| J (멀티모달) | ~73건 | 주요 항목 |
| L (개발 도구) | ~62건 | 전수 |
| M (PKM/지식) | ~58건 | 전수 |
| **합계** | ~317건 | V3 전 보강 필수 |

### 5.4 V3 GO/NO-GO 체크리스트

```
☐ V2 전환 조건 충족 (QoD≥0.90, 2-tier LLM 최적화, Self-evo 검증, V3 비용 재검토)
☐ K8s 배포 명세 상세 완료 (V3-001)
☐ S-8 Self-evo 거버넌스 상세화 (V3-002)
☐ V3 비용 상한 재산정 + 승인 (V3-003)
☐ GraphRAG 벤치마크 정의 (V3-004)
☐ SDAR V3 완전 활성화 조건 충족 (AR-L4)
☐ STEP7 TITLE_ONLY ~317건 상세 보강
☐ 에이전트 50+ 병렬 인프라 구축
☐ A2A 프로토콜 설계 (DEFER-AT-005)
☐ Federated Agent 승인 체계 (DEFER-AT-004)
☐ V2 GO 체크리스트 전수 통과
```

---

## 6. Cross-cutting: 버전 횡단 해소 항목

### 6.1 스키마 버전 통일 (CC-001)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | D1=v2.3.0, D2=v2.2.3, D3=v2.4.0, D4~D8 혼재 | - |
| **해소** | V0 진입 시 전체 v3.0.0 통일 승격 (Q1 Risk R-1-5 계획) | - |
| **시점** | V0 진입 시 |

### 6.2 BEGINNER_GUIDE 갱신 (CC-002)

| 수정 항목 | 현재 | 변경 |
|----------|------|------|
| I-Series 목록 | I-21~I-23 누락 | I-21~I-25 전수 추가 |
| E-15 명칭 | "File System" | "File System / Cloud Collector" |
| S-5 명칭 | "Router Evolution" | "Router Evolution / Cloud Evolver" |

### 6.3 QoD 가중치 이중 체계 (CC-003)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | MASTER_SPEC: 출처별 가중치(공식문서 0.85, 내부KB 0.70, 커뮤니티 0.50, 미분류 0.30), CLOUD_LIBRARY: 소스별 가중치(공식발표 1.0, 논문 0.9 등) | - |
| **해소** | 두 체계는 **다른 목적**: 전자는 "RAG 소스 신뢰도", 후자는 "Cloud Library 수집 품질". 각각의 컨텍스트에서 사용 | - |
| **수정 파일** | MASTER_SPEC | "RAG 소스 신뢰도 가중치 (Cloud Library 가중치와 별개)" 명시 |

### 6.4 Gate G0~G4 이중 사용 (CC-004)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | MASTER_SPEC G0~G4 = Pipeline 5단계, CLOUD_LIBRARY G0~G4 = 품질 5단계 | - |
| **해소** | Cloud Library를 **CL-G0~CL-G4**로 접두어 추가 | - |
| **수정 파일** | CLOUD_LIBRARY_SPEC | Gate 표기를 CL-G0~CL-G4로 변경 |

### 6.5 EventTypeRegistry 미완성 (CC-006)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | D2 EventTypeRegistry에 53개 등록, AGENT_TEAMS 16개 추가, SDAR 이벤트 미등록 | - |
| **해소** | 전체 이벤트를 D2 Registry에 통합 등록 | - |
| **수정 파일** | D2.1-D2 EventTypeRegistry | agent.* + sdar.* 이벤트 추가 |

### 6.6 Python/TypeScript 스키마 동기화 (CC-007)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | D2.1: Python Pydantic v2, B1: TypeScript interface — 자동 동기화 메커니즘 없음 | - |
| **해소** | V0 스키마 코드 생성 시 양방향 생성 (Pydantic → Zod 자동 변환 스크립트) | - |
| **수정 파일** | PHASE_B3 또는 별도 빌드 스크립트 | schema sync 도구 추가 |

### 6.7 HMAC 서명 상세 (CC-012)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | AGENT_TEAMS_SPEC AgentMessage에 HMAC signature 필드 있으나 키 관리/알고리즘/검증 실패 처리 없음 | - |
| **해소** | HMAC-SHA256 + 키 생성/교환/갱신 프로토콜 상세화 | - |
| **수정 파일** | AGENT_TEAMS_SPEC 보안 섹션 | HMAC 프로토콜 상세 추가 |
| **시점** | V2 전 (MessageBus 도입 시) |

### 6.8 STEP7 모듈 연동 추상적 (CC-005)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | STEP7: "VAMOS 연동: I(메모리) + E(API)"처럼 카테고리만 표기, 구체적 ID 미기재 | - |
| **해소** | V2 STEP7 보강 시 구체적 모듈 ID 매핑 추가 (예: I-3 + E-1) | - |
| **시점** | V2 전 |

### 6.9 테스트 케이스 목록 부재 (CC-008)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | PHASE_B5에 전략만 있고 구체적 테스트 시나리오 없음 | - |
| **해소** | V1 구현 시 AC (Acceptance Criteria) 기반 테스트 케이스 자동 도출 | - |
| **시점** | V1 구현 시 |

### 6.10 B-Series/L-Series 교차 매핑 (CC-009)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | B-1(Episodic)=L1, B-2(Procedural)=L3, B-3(Semantic)=L2, B-4(Working)=L0 — 비직관적 교차 | - |
| **해소** | **LOCK (변경 불가)**. 개발자 가이드에 매핑표 명시 | - |
| **수정 파일** | BEGINNER_GUIDE | B↔L 매핑표 추가 |

### 6.11 문서 인덱스 39 vs 실제 38파일 (CC-010)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | MASTER_SPEC 39파일 인덱스, 실제 38파일 (PLAN-2.0 미포함 시) | - |
| **해소** | PLAN-2.0 = SUPERSEDED → 인덱스에서 "(대체됨)" 표기, 실제 38파일 = 정상 | - |

### 6.12 STEP7 항목 수 60건 차이 (CC-011)

| 항목 | 현재 상태 | 해소 방법 |
|------|----------|----------|
| **문제** | 보강통합명세서: 1,545건 선언, 실제 합산: 1,485건 (60건 차이) | - |
| **해소** | 범위 묶음(range bundle) 전개 시 차이 발생 — 개별 문서 참조 기준이 정본 | - |
| **수정 파일** | STEP7 보강통합명세서 | "범위 묶음 전개 후 실제: ~1,485건" 비고 추가 |

---

## 7. 45개 검증 이슈 전수 매핑표

### 7.1 해소 시점별 분류

| 해소 시점 | 이슈 ID | 수 |
|----------|---------|---|
| **V0 착수 전** | V0-001, V0-002, V0-003, V0-004, V0-005 | 5 |
| **V0~V1 착수 전** | V1-001~V1-016 (V1-015는 V0에서 해소) | 16 |
| **V2 착수 전** | V2-001~V2-008 | 8 |
| **V3 착수 전** | V3-001~V3-004 | 4 |
| **버전 횡단** | CC-001~CC-012 | 12 |
| **합계** | | **45** |

### 7.2 심각도별 분류

| 심각도 | 수 | 이슈 ID |
|--------|---|---------|
| **HIGH** | 10 | V0-002, V0-004, V1-001, V1-002, V1-003, V1-008, V1-015, V1-016, V2-003, V2-008 |
| **MEDIUM** | 21 | V0-001, V0-003, V1-004, V1-005, V1-006, V1-007, V1-010, V1-013, V2-001, V2-002, V2-004, V2-005, V2-006, V2-007, V3-001, V3-002, CC-001, CC-003, CC-006, CC-007, CC-012 |
| **LOW** | 9 | V0-005, V1-009, V1-011, V1-014, V3-003, V3-004, CC-002, CC-004, CC-005 |
| **INFO** | 5 | V1-012(정합확인됨), CC-008, CC-009, CC-010, CC-011 |

### 7.3 수정 대상 파일별 매핑

| 수정 파일 | 관련 이슈 ID | 수정 항목 수 |
|----------|-------------|-----------|
| VAMOS_MASTER_SPECIFICATION | V0-002, V1-001, V1-002, V1-003, V1-004, V1-006, V1-007, V1-010, CC-003 | 9 |
| D2.0-01 OVERVIEW | V0-001, V1-008 | 2 |
| D2.0-02 ORANGE CORE | V1-007, V1-009 | 2 |
| D2.0-07 SAFETY COST | V1-010 | 1 |
| D2.1-D2 ORANGE CORE 스키마 | V1-004, CC-006 | 2 |
| D2.1-D6 STORAGE MEMORY 스키마 | V1-006 | 1 |
| D2.1-D7 SAFETY COST 스키마 | V1-010 | 1 |
| VAMOS_AGENT_TEAMS_SPEC | V1-005, V2-003, CC-012 | 3 |
| VAMOS_CLOUD_LIBRARY_SPEC | V2-001, CC-004 | 2 |
| VAMOS_BEGINNER_GUIDE | V1-001, V1-002, V1-003, V1-006, CC-002, CC-009 | 6 |
| STEP7_F-I_상세명세서 | V0-003, V0-004, V0-005, V1-013, V1-014 | 5 |
| STEP7_보강_통합명세서 | CC-011 | 1 |
| PLAN-3.0 | V1-001 | 1 |

---

## 8. 파일별 수정 액션 매트릭스

### 8.1 즉시 수정 (V0 전)

| # | 파일 | 수정 내용 | 이슈 ID | 긴급도 |
|---|------|----------|---------|--------|
| 1 | STEP7_F-I | S7F-012 Node.js sidecar → "대안 참조" 격하, "PLAN-3.0 정본: Python 백엔드" 명시 | V0-004 | HIGH |
| 2 | STEP7_F-I | 디렉토리 구조 → "PHASE_B2 정본" 비고 | V0-003 | MEDIUM |
| 3 | STEP7_F-I | config.yaml → config.toml 통일 | V0-005 | LOW |
| 4 | MASTER_SPEC | §0 인덱스 B그룹에 "(= IMPLEMENTATION 계층)" 추가 | V0-002 | HIGH |
| 5 | D2.0-01 | §8.5 "V0 비용 상한 = V1 동일 적용 (₩40,000/월)" 명시 | V0-001 | MEDIUM |
| 6 | MASTER_SPEC | §6.9 config.yaml → config.toml 통일 | V0-005 | LOW |

### 8.2 V1 전 수정

| # | 파일 | 수정 내용 | 이슈 ID | 긴급도 |
|---|------|----------|---------|--------|
| 7 | BEGINNER_GUIDE | I-Series 표에 I-21~I-25 추가 | V1-001, V1-016 | HIGH |
| 8 | MASTER_SPEC | I-Series 인덱스 I-21~I-25 확인 | V1-001 | HIGH |
| 9 | PLAN-3.0 | §13.1에 I-22~I-25 참조 추가 | V1-001 | HIGH |
| 10 | MASTER_SPEC | E-15 → "File System / Cloud Collector" | V1-002 | HIGH |
| 11 | BEGINNER_GUIDE | E-15 → "File System / Cloud Collector" | V1-002 | HIGH |
| 12 | MASTER_SPEC | S-5 → "Router Evolution / Cloud Evolver" | V1-003 | HIGH |
| 13 | BEGINNER_GUIDE | S-5 → "Router Evolution / Cloud Evolver" | V1-003 | HIGH |
| 14 | D2.0-01 | §7.2 38개 DEFER/TBD에 대상 버전 태그 추가 | V1-008 | HIGH |
| 15 | AGENT_TEAMS_SPEC | datetime.utcnow() → datetime.now(timezone.utc) 전수 교체 | V1-005 | MEDIUM |
| 16 | D2.1-D2 | DecisionSchema approval_status에 pending/expired 추가 | V1-004 | MEDIUM |
| 17 | MASTER_SPEC | Decision 스키마 → D7 SOT와 일치 | V1-004 | MEDIUM |
| 18 | MASTER_SPEC | §8.8 QoD → PLAN-3.0 5요소 공식으로 통일 | V1-006 | MEDIUM |
| 19 | BEGINNER_GUIDE | QoD → 5요소 공식으로 수정 | V1-006 | MEDIUM |
| 20 | D2.1-D6 | SourceQoDSchema → 5개 필드 반영 | V1-006 | MEDIUM |
| 21 | D2.0-02 | I-1 섹션에 "Front Mini LLM = I-1 내부 서브컴포넌트" 명시 | V1-007 | MEDIUM |
| 22 | MASTER_SPEC | Front Mini LLM = I-1 서브컴포넌트 명시 | V1-007 | MEDIUM |
| 23 | D2.1-D7 | GuardrailsCheckSchema L4 필드 추가 | V1-010 | MEDIUM |
| 24 | D2.0-07 | 4-Layer Guardrails 명시 | V1-010 | MEDIUM |
| 25 | STEP7_F-I | 비용: "BASE 상한: ₩40,000/월, 최소 운영 목표: $8/월" 구분 | V1-013 | MEDIUM |
| 26 | STEP7_F-I | React → "React 18 (PHASE_B3 정본)" 명시 | V1-014 | LOW |
| 27 | D2.0-02 | DEC-001 비고에 LangChain Allowlist 명시 | V1-009 | LOW |

### 8.3 V2 전 수정

| # | 파일 | 수정 내용 | 이슈 ID | 긴급도 |
|---|------|----------|---------|--------|
| 28 | MASTER_SPEC | §7.2 FREEZE 해석 명확화 | V2-003 | HIGH |
| 29 | AGENT_TEAMS_SPEC | V1/V2 구분: Lead Agent 위임 vs MessageBus | V2-003 | HIGH |
| 30 | CLOUD_LIBRARY_SPEC | 10-Layer → CL-Layer 접두어 | V2-001 | MEDIUM |
| 31 | CLOUD_LIBRARY_SPEC | Gate → CL-G0~CL-G4 접두어 | CC-004 | LOW |
| 32 | AGENT_TEAMS_SPEC | HMAC 프로토콜 상세 추가 | CC-012 | MEDIUM |
| 33 | D2.1-D2 | EventTypeRegistry에 agent.* + sdar.* 추가 | CC-006 | MEDIUM |
| 34 | MASTER_SPEC | QoD 가중치 = "RAG 소스 신뢰도" 명시 | CC-003 | MEDIUM |

### 8.4 버전 횡단 수정

| # | 파일 | 수정 내용 | 이슈 ID | 시점 |
|---|------|----------|---------|------|
| 35 | D2.1-D1~D8 전체 | 스키마 버전 v3.0.0 통일 승격 | CC-001 | V0 |
| 36 | BEGINNER_GUIDE | B↔L 매핑표 추가 | CC-009 | V1 |
| 37 | STEP7_보강_통합명세서 | "범위 묶음 전개 후 실제: ~1,485건" 비고 | CC-011 | V1 |
| 38 | MASTER_SPEC | PLAN-2.0 → "(대체됨)" 표기 | CC-010 | V0 |

---

## 9. 구현 진입 GO/NO-GO 체크리스트

### 9.1 V0 진입 전 (총 16항목)

| # | 체크 항목 | 관련 이슈 | 상태 |
|---|----------|----------|------|
| 1 | 통신 계층: Python 백엔드 확정 | V0-004 | ☐ |
| 2 | IMPLEMENTATION 계층 = PHASE_B 명시 | V0-002 | ☐ |
| 3 | V0 비용 상한 = V1 동일 명시 | V0-001 | ☐ |
| 4 | 디렉토리 구조: PHASE_B2 정본 명시 | V0-003 | ☐ |
| 5 | config 포맷: config.toml 통일 | V0-005 | ☐ |
| 6 | D2.1 스키마 v3.0.0 통일 승격 | CC-001 | ☐ |
| 7 | PLAN-2.0 "(대체됨)" 표기 | CC-010 | ☐ |
| 8 | BASE-1.3 전 24개 규칙 코드 매핑 | §2.2 | ☐ |
| 9 | 스캐폴딩 + 의존성 설치 | §2.3~2.4 | ☐ |
| 10 | config.v1.toml LOCK 값 배치 | §2.5 | ☐ |
| 11 | 24개 스키마 코드 생성 | §2.6 | ☐ |
| 12 | I-1~I-5 + I-19 스켈레톤 | §2.7 | ☐ |
| 13 | L0 세션 메모리 최소 구현 | §2.7 | ☐ |
| 14 | 비용 엔진 ₩40,000/월 하드코딩 | §2.7 | ☐ |
| 15 | Guardrails L1+L2 설정 | §2.7 | ☐ |
| 16 | Ollama + Chroma + SQLite 초기화 | §2.3 | ☐ |

### 9.2 V1 진입 전 (총 21항목, V0 완료 전제)

| # | 체크 항목 | 관련 이슈 | 상태 |
|---|----------|----------|------|
| 1 | I-Series 25개 모듈 정본 확정 | V1-001, V1-016 | ☐ |
| 2 | E-15 겸용 처리 | V1-002 | ☐ |
| 3 | S-5 겸용 처리 | V1-003 | ☐ |
| 4 | 38개 DEFER/TBD V1 차단 0건 확인 | V1-008 | ☐ |
| 5 | datetime.utcnow() 전수 교체 | V1-005 | ☐ |
| 6 | approval_status enum 4개 통일 | V1-004 | ☐ |
| 7 | QoD 5요소 공식 통일 | V1-006 | ☐ |
| 8 | Front Mini LLM = I-1 내부 명시 | V1-007 | ☐ |
| 9 | Guardrails 4-Layer 명시 | V1-010 | ☐ |
| 10 | 비용 상한 ₩40,000 통일 | V1-013 | ☐ |
| 11 | React 18.3 통일 | V1-014 | ☐ |
| 12 | LangChain Allowlist 명시 | V1-009 | ☐ |
| 13 | 14개 보안 항목 (S7E) 구현 | §3.5 | ☐ |
| 14 | 테스트 인프라 구축 | §3.6 | ☐ |
| 15 | CI/CD 설정 완료 | §3.7 | ☐ |
| 16 | 스토리지 스택 구축 (SQLite+Chroma+JSONL+Graph) | §3.4 | ☐ |
| 17 | EventTypeRegistry 통합 | CC-006 | ☐ |
| 18 | Python/TS 스키마 동기화 도구 | CC-007 | ☐ |
| 19 | BEGINNER_GUIDE 모듈 목록 갱신 | CC-002 | ☐ |
| 20 | B↔L 매핑표 추가 | CC-009 | ☐ |
| 21 | STEP7 항목 수 비고 추가 | CC-011 | ☐ |

### 9.3 V2 진입 전 (총 14항목, V1 완료 전제)

| # | 체크 항목 | 관련 이슈 | 상태 |
|---|----------|----------|------|
| 1 | V1→V2 전환 조건 6개 충족 | - | ☐ |
| 2 | Agent Teams FREEZE 해석 확정 | V2-003 | ☐ |
| 3 | STEP7 V2 CRITICAL ~190건 상세 보강 | V2-008 | ☐ |
| 4 | 10-Layer / Gate 접두어 변경 | V2-001, CC-004 | ☐ |
| 5 | SQLite→PostgreSQL 마이그레이션 완료 | V2-004 | ☐ |
| 6 | Chroma→Qdrant 재임베딩 전략 구현 | V2-005 | ☐ |
| 7 | NetworkX→Neo4j 변환 규칙 정의 | V2-006 | ☐ |
| 8 | SDAR V2 COND 활성화 조건 확정 | V2-002 | ☐ |
| 9 | MessageBus 구현 결정 | DEFER-AT-001 | ☐ |
| 10 | HMAC 프로토콜 상세 완성 | CC-012 | ☐ |
| 11 | STEP7 모듈 연동 구체화 | CC-005 | ☐ |
| 12 | V2 인프라 10개 컴포넌트 구축 | §4.3 | ☐ |
| 13 | V2 비용 모니터링 대시보드 | §4.4 | ☐ |
| 14 | QoD 가중치 이중 체계 구분 명시 | CC-003 | ☐ |

### 9.4 V3 진입 전 (총 11항목, V2 완료 전제)

| # | 체크 항목 | 관련 이슈 | 상태 |
|---|----------|----------|------|
| 1 | V2→V3 전환 조건 4개 충족 | - | ☐ |
| 2 | K8s 배포 명세 상세 완성 | V3-001 | ☐ |
| 3 | S-8 Self-evo 거버넌스 상세화 | V3-002 | ☐ |
| 4 | V3 비용 상한 재산정 + 승인 | V3-003 | ☐ |
| 5 | GraphRAG 벤치마크 정의 | V3-004 | ☐ |
| 6 | SDAR V3 ON 조건 충족 (6개) | §5.2 | ☐ |
| 7 | STEP7 TITLE_ONLY ~317건 보강 | §5.3 | ☐ |
| 8 | 에이전트 50+ 병렬 인프라 | - | ☐ |
| 9 | A2A 프로토콜 설계 | DEFER-AT-005 | ☐ |
| 10 | Federated Agent 승인 체계 | DEFER-AT-004 | ☐ |
| 11 | Agent Marketplace 기준 확정 | DEFER-AT-003 | ☐ |

---

## 10. 부록: 수정사항 파일 기존 항목 반영 상태

> **소스**: `final summary 수정 사항.md`

### 10.1 기존 항목 상태

| # | 항목 | 상태 | 비고 |
|---|------|------|------|
| 01 | A-04 청크 2/8 추출 부족 (98.4%) | **이전 세션에서 확인됨** | 나머지 7청크 정상, 핵심 내용 보존 |
| 02 | base 1.0 언급 확인 | **확인 필요** | STEP7 진행 시 원본 base 1.3만 제공 → base 1.0 언급은 참조용 비교 |
| 03 | 청크 중복 + step 4 진행 여부 | **해소됨** | STEP6에서 청크 합쳐짐 |
| 04 | AI 용어 정리 | **BEGINNER_GUIDE에 반영됨** | 1,853줄 용어 가이드 |
| ir-001 | 완전 자율 vs 승인 필요 구분 | **설계에 반영됨** | AutonomyLevel L0~L3 + P0/P1/P2 구분 |
| ir-002 | v1 뼈대 → v2/v3 구현 | **반영됨** | V1 스켈레톤 → V2/V3 확장 설계 |
| ir-003 | v3 선에서 무조건 구현 | **반영됨** | V3 GO 체크리스트에 포함 |
| ir-004 | 벡터 DB 대기업용 문제점 | **확인됨** | Chroma→Qdrant→Qdrant Cloud 진화 경로 |
| ir-005 | Pinecone 대체 | **반영됨** | Qdrant 채택 (무료 시작 가능) |
| ir-006 | 빈자리 확인 | **확인 필요** | 구현 시 채워질 TBD 항목 vs 현재 누락 |
| ir-007 | 승인 필요/불필요 자율화 구분 | **반영됨** | AutonomyLevel + DEC-003 Allowlist |
| ir-008 | 토크나이저 비용 + 자체 vs tiktoken | **반영됨** | tiktoken LOCK (비용 대비 효율 최선) |
| ir-009 | TSZ 오픈소스 패턴 적합성 | **확인 필요** | 구현 시 패턴 검토 |
| ir-010~011 | MCP 대체 품질 | **반영됨** | MCP Streamable HTTP LOCK |
| ir-011b | 추가 설계 필요 여부 | **반영됨** | 1%라도 필요하면 설계 |
| ir-012~013 | LangChain 패턴만 참조 적합성 | **반영됨** | DEC-002=B (패턴 참조, 직접 사용 안함) |
| ir-014 | 90~100% 달성 방안 | **반영됨** | V3 GraphRAG 90%+ 목표 |
| ir-015~016 | 더 좋은 방법 확인 | **반영됨** | 각 항목별 최선안 채택 |
| ir-017 | 파일 분리 vs 합치기 판단 | **반영됨** | 39개 파일 5그룹 구조 유지 (최적) |
| ir-018~026 | 각종 동의+더 좋은 방법 | **반영됨** | 이슈별 최선안 적용 |

### 10.2 미해소 항목

| 항목 | 상태 | 다음 단계 |
|------|------|----------|
| ir-006 (빈자리) | 확인 필요 | V1 구현 시 TBD 채우기 과정에서 확인 |
| ir-009 (TSZ 패턴) | 확인 필요 | 구현 시 오픈소스 패턴 적합성 재검토 |
| 02 (base 1.0 언급) | 확인 필요 | STEP7 원본 분석에서 비교 참조용으로 사용됨 |

---

## 최종 요약

### 버전별 수정 항목 수

| 버전 | 산출물 수정 | 이슈 해소 | GO 체크항목 |
|------|-----------|----------|-----------|
| **V0 전** | 6건 | 5건 (HIGH:2, MEDIUM:2, LOW:1) | 16 |
| **V1 전** | 21건 | 16건 (HIGH:6, MEDIUM:6, LOW:3, INFO:1) | 21 |
| **V2 전** | 7건 | 8건 (HIGH:2, MEDIUM:6) | 14 |
| **V3 전** | 0건 | 4건 (MEDIUM:2, LOW:2) | 11 |
| **횡단** | 4건 | 12건 (MEDIUM:5, LOW:3, INFO:4) | - |
| **합계** | **38건** | **45건** | **62** |

### 구현 타임라인

```
Week 0 (Day 1~5)  : V0 차단 이슈 해소 (6건 수정) + 스키마 코드 생성
Week 1~2           : V0 스캐폴딩 + 최소 프레임워크
Week 3             : V1 차단 이슈 해소 (21건 수정)
Week 4~15          : V1 MVP 구현 (8~12주)
Week 16~17         : V1→V2 전환 검증
Week 18~19         : V2 차단 이슈 해소 (7건 수정) + 마이그레이션
Week 20~35         : V2 Pro Server 구현
Week 36~           : V3 Enterprise (V2 안정화 후)
```

---

> **이 문서는 VAMOS AI 프로젝트의 39개 산출물을 대상으로, V0~V3 전 버전의 구현 착수 전 준비사항을 빠짐없이 정리한 종합 가이드입니다.**
> **모든 45개 검증 이슈, 38개 파일 수정 사항, 62개 GO/NO-GO 체크 항목이 포함되어 있습니다.**
