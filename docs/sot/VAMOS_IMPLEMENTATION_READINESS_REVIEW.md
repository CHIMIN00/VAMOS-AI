# VAMOS AI 구현 착수 준비 상태 종합 검토 보고서

> **버전**: v1.0.0 | **검토일**: 2026-02-24
> **검토 대상**: 산출물 39개 전체 파일 (RULE/PLAN/DESIGN/SCHEMA/PHASE/SPEC/STEP7/GUIDE)
> **목적**: V0 구현 착수 가능 여부 판정 + 전 버전(V0~V3) 사전 준비사항 빠짐없이 정리

---

## 목차

1. [최종 판정 (GO/NO-GO)](#1-최종-판정-gono-go)
2. [BLOCKER 목록 (V0 진입 전 반드시 해결)](#2-blocker-목록-v0-진입-전-반드시-해결)
3. [미결정 항목 전수 조사](#3-미결정-항목-전수-조사)
4. [구현 전 필수 준비사항 체크리스트](#4-구현-전-필수-준비사항-체크리스트)
5. [구현 단계 순서 및 의존성](#5-구현-단계-순서-및-의존성)
6. [문서 간 충돌/불일치 사항](#6-문서-간-충돌불일치-사항)
7. [버전별 외부 서비스/API Key/계정 총정리](#7-버전별-외부-서비스api-key계정-총정리)
8. [버전별 소프트웨어/인프라 설치 총정리](#8-버전별-소프트웨어인프라-설치-총정리)
9. [보안 필수 항목 (V1 CRITICAL)](#9-보안-필수-항목-v1-critical)
10. [문서 수정 필요 목록](#10-문서-수정-필요-목록)
11. [위험 요소 및 대응 방안](#11-위험-요소-및-대응-방안)

---

# 1. 최종 판정 (GO/NO-GO)

## 판정: ⚠️ 조건부 GO (Conditional GO)

| 항목 | 판정 | 근거 |
|------|------|------|
| **V0 착수 가능 여부** | **조건부 GO** | BLOCKER 8건 해결 시 즉시 착수 가능 (모두 문서 수정 수준, 코드/인프라 불필요) |
| **V1 착수 가능 여부** | **준비 중** | V0 완료 후 + HIGH 26건 해결 시 착수 가능 |
| **미결정(DECISION_NEEDED)** | **실질 0건** | 55개 이슈 모두 해결안 제시 완료. 진정한 "열린 결정"은 V2/V3에만 2~3건 |
| **외부 의존성** | **최소** | V0는 OpenAI API Key 1개만 필수. 나머지는 로컬 설치 |
| **아키텍처 완성도** | **95%+** | 4계층/5Phase/9State/5Gate/81모듈 전체 확정 |
| **스키마 완성도** | **90%+** | 24개 스키마 정의 완료, DN-001~DN-016 전부 해결 |

### 조건부 GO의 조건

V0 착수 전 반드시 해결해야 할 **BLOCKER 8건**:

| # | ID | 내용 | 해결 방법 | 소요 시간 |
|---|-----|------|----------|----------|
| 1 | X-01 | PLAN 3.0의 I-모듈 번호가 DESIGN 2.0과 불일치 | PLAN 3.0에 매핑표 추가 또는 DEPRECATE 표기 | 30분 |
| 2 | BN-13 | P0 활성 도메인 리스트 미확정 (Blue Node) | PLAN 3.0 근거로 Dev/Research/Productivity 확정 | 15분 |
| 3 | ST-35 | Storage event_type/failure_code 미등록 | D2 중앙 레지스트리에 5개 코드 등록 | 30분 |
| 4 | DS-66 | 다운시프트 임계값 (80%/100%) 문서 간 충돌 | D2.0-07 §4의 "LOCK: 80%/100%"를 정본으로 통일 | 15분 |
| 5 | V0-004 | Python backend vs Node.js sidecar 충돌 | STEP7 F-I에 "PLAN-3.0: Python 정본" 주석 추가 | 10분 |
| 6 | V0-003 | 디렉토리 구조 충돌 (B2 vs STEP7-F) | PHASE_B2를 정본으로 선언 | 10분 |
| 7 | V0-005 | Config 파일 포맷 혼용 (yaml vs toml) | config.toml로 통일 (PHASE_B4 정본) | 10분 |
| 8 | CC-001 | 스키마 버전 불일치 (v2.2.0~v2.4.0) | V0 진입 시 전체 v3.0.0 통일 | 1시간 |

**총 예상 소요: 약 3시간** (모두 문서 수정 작업)

> **결론**: BLOCKER 8건은 모두 "문서 수정"으로 해결 가능하며, 코드 작성이나 인프라 구축이 필요 없습니다.
> 따라서 **문서 수정 → 즉시 V0 착수 가능**합니다.

---

# 2. BLOCKER 목록 (V0 진입 전 반드시 해결)

## 2.1 BLOCKER 상세

### BLK-1: I-모듈 번호 불일치 (PLAN vs DESIGN)
- **소스**: PLAN-3.0 §2.3 (line 460-475) vs DESIGN 2.0 전체
- **문제**: PLAN 3.0은 구 번호 체계 사용 (I-7=안전, I-8=비용, I-9=로그...)
  - DESIGN 2.0은 신 번호 체계 사용 (I-7=Project/Session Manager, I-8=Policy Engine, I-9=Cost Manager...)
- **위험**: 구현자가 PLAN을 읽으면 완전히 다른 모듈을 구현할 위험
- **해결**: PLAN 3.0 §2.3에 "⚠️ 본 섹션의 I-모듈 번호는 PLAN 2.0 기준. DESIGN 2.0 §5.6~5.13이 정본" 경고 추가
- **정본 규칙**: DESIGN 2.0 > PLAN 3.0 본문 (§0.3 정본 우선순위)

### BLK-2: P0 활성 도메인 리스트 미확정
- **소스**: D2.0-03 §1514 ("구체 도메인 리스트는 PLAN 3.0 근거로만 확정")
- **문제**: Blue Node NodeRegistry에 어떤 domain_name 값을 넣을지 결정 안 됨
- **위험**: V0 스캐폴딩 시 어떤 Blue Node를 생성할지 모름
- **해결**: P0 = Dev/System, Research, Productivity (3개) 확정. PLAN 3.0 §3.1 근거

### BLK-3: Storage 이벤트/실패 코드 미등록
- **소스**: D2.0-06 §1390-1407
- **문제**: `storage.policy.checked`, `storage.memory.write.completed`, `PII_LONGTERM_DENIED` 등이 D2 중앙 레지스트리에 미등록
- **위험**: Storage 모듈의 LogEvent 기록 불가
- **해결**: D2.1-D2 EventTypeRegistry에 5개 event_type, 1개 failure_code, 1개 fallback_id 추가

### BLK-4: 다운시프트 임계값 문서 간 충돌
- **소스**: D2.0-02(80%/100% 명시) vs D2.0-04("근거 확보 후만 잠금") vs D2.0-07(§4=LOCK, §9=운영설정)
- **문제**: 같은 값(80% 경고, 100% 차단)에 대해 3개 문서가 다른 권위 수준 부여
- **위험**: 구현자가 80% Mini-force를 구현해도 되는지 판단 불가
- **해결**: D2.0-07 §4를 정본으로 선언: `warn_threshold=80 LOCK`, `block_threshold=100 LOCK`. §9에 일관성 주석 추가

### BLK-5: Python Backend vs Node.js Sidecar 충돌
- **소스**: STEP7 F-I에서 Node.js sidecar 언급 vs PLAN-3.0 Python backend 확정
- **문제**: 두 문서가 다른 통신 계층 아키텍처 제시
- **위험**: 잘못된 기술 스택으로 V0 시작할 수 있음
- **해결**: STEP7 F-I에 "본 섹션은 대안 참조. PLAN-3.0 정본: Python backend + JSON-RPC stdin/stdout" 추가

### BLK-6: 디렉토리 구조 충돌
- **소스**: PHASE_B2 (monorepo) vs STEP7-F (다른 구조)
- **해결**: PHASE_B2 monorepo를 정본으로 선언

### BLK-7: Config 포맷 혼용
- **소스**: STEP7 일부 yaml 참조 vs PHASE_B4 toml 확정
- **해결**: config.toml로 통일 (Pydantic v2 + tomli LOCK)

### BLK-8: 스키마 버전 불일치
- **소스**: D1=v2.3.0, D2=v2.2.3, D3=v2.4.0, D6=v2.3.1 등 불일치
- **해결**: V0 진입 시 전체 D1~D8을 v3.0.0으로 일괄 승격

---

# 3. 미결정 항목 전수 조사

## 3.1 요약 통계

| 심각도 | V0 | V1 | V2 | V3 | 횡단 | 합계 |
|--------|----|----|----|----|------|------|
| **BLOCKER** | 8 | 0 | 0 | 0 | 0 | **8** |
| **HIGH** | 0 | 12 | 2 | 0 | 6 | **20** |
| **MEDIUM** | 0 | 4 | 8 | 2 | 6 | **20** |
| **LOW** | 0 | 3 | 2 | 2 | 0 | **7** |
| **합계** | **8** | **19** | **12** | **4** | **12** | **55** |

> **핵심**: 모든 55건에 대해 해결안이 제시되어 있음. 진정한 "열린 결정"은 없음.
> V2에서만 MessageBus(Redis vs In-Memory), GroupChat 알고리즘 2건이 실질 미결정.

## 3.2 V0 BLOCKER (8건) → §2에서 상세 기술

## 3.3 V1 HIGH 이슈 (12건)

| # | ID | 내용 | 해결안 |
|---|-----|------|--------|
| 1 | V1-001 | I-Series 모듈 수 불일치 (21 vs 24 vs 25) | I-1~I-25 (25개) 정본 |
| 2 | V1-016 | I-21~I-25 정의 누락 | Source Evolution, Task/Project Mgr, Doc/Code Structuring, KG Engine, SDAR 추가 |
| 3 | V1-002 | E-15 명칭 충돌 | "File System / Cloud Collector" 이중명 |
| 4 | V1-003 | S-5 명칭 충돌 | "Router Evolution / Cloud Evolver" 이중명 |
| 5 | V1-008 | 38개 DEFER/TBD 미분류 | 전수 태깅 완료: V1 blocking = 0건 |
| 6 | V1-015 | Python backend 진입점 미정 | `backend/main.py` (stdin/stdout IPC 서버) |
| 7 | OC-2 | QoD Evidence Gate 임계값 수치 미잠금 | D2.0-02에서 "발명 금지"지만, 운영 기본값 0.4/0.7 채택 |
| 8 | OC-5/6 | 한국어 로컬 LLM 미확정 | DEFER V1.1. 임시: GPT-4o API / SOLAR 10.7B 우선 테스트 |
| 9 | BN-12 | 이벤트 네이밍 최종 잠금 미완 | STEP 1.1 표준을 V1 정본으로 채택 |
| 10 | IF-21/22 | 강등 규칙(use_mini_only) 07/PLAN 근거 미확보 | D2.0-07 §4 LOCK을 근거로 채택 |
| 11 | ST-36 | 메모리 TTL 수치 미잠금 | L0=7일, L1=90일을 운영 기본값으로 채택 |
| 12 | SF-46/47 | 80% warn 임계값 문서 내부 모순 | §4 LOCK이 정본, §9는 "운영 설정 가능 범위" 명시 |

## 3.4 V1 MEDIUM/LOW 이슈 (7건)

| # | ID | 내용 | 해결안 |
|---|-----|------|--------|
| 1 | V1-004 | approval_status enum 2값 vs 4값 | D7 SOT: 4값 (approved/denied/pending/expired) |
| 2 | V1-005 | datetime.utcnow() deprecated | datetime.now(timezone.utc) 전환 |
| 3 | V1-006 | QoD 가중치 4요소 vs 5요소 | PLAN-3.0 5요소 정본 |
| 4 | V1-007 | Front Mini LLM 모듈 ID 없음 | I-1 내부 서브컴포넌트 (별도 ID 불필요) |
| 5 | V1-010 | Guardrails 3Layer vs 4Layer | 4Layer 정본 (L4=V2+ 사후감사) |
| 6 | V1-009 | LangChain 임포트 금지 vs 의존성 | langchain-core/community/openai 어댑터만 허용 |
| 7 | V1-014 | React 18 vs 19 | React 18.3 (PHASE_B3 정본) |

## 3.5 V2 이슈 (12건)

| # | ID | 내용 | 상태 |
|---|-----|------|------|
| 1 | V2-003 | Agent Teams vs "무제한 P2P 금지" FREEZE | Lead Agent 위임 허용 |
| 2 | V2-008 | STEP7 TITLE_ONLY 44% 상세화 필요 | V2 CRITICAL ~190건 |
| 3 | V2-001 | 10-Layer 명칭 충돌 | "CL-Layer" 접두사 |
| 4 | V2-002 | SDAR 활성화 조건 미정 | AR-L2→L3, 성공률 ≥95% |
| 5 | V2-004~006 | 3대 마이그레이션 (DB/Vector/Graph) | 마이그레이션 스크립트 필요 |
| 6 | CC-003 | QoD 이중 가중치 체계 | 별도 목적 시스템으로 문서화 |
| 7 | CC-004 | Gate G0-G4 이중 사용 | "CL-G" 접두사 |
| 8 | CC-012 | HMAC 서명 키 관리 프로토콜 미정 | V2 전 설계 |
| 9 | DEFER-AT-001 | MessageBus: Redis vs In-Memory | **실질 미결정** (V2 결정) |
| 10 | DEFER-AT-002 | GroupChat 순서 알고리즘 | **실질 미결정** (V2 결정) |
| 11 | SF-54 | GDPR 기능 (열람/이동/제한) | V2+ 구현 |
| 12 | IF-27 | V1→V2 마이그레이션 경로 | 마이그레이션 스크립트 필요 |

## 3.6 V3 이슈 (4건)

| # | ID | 내용 |
|---|-----|------|
| 1 | V3-001 | K8s 배포 명세 불충분 (3-5줄) |
| 2 | V3-002 | S-8 Self-evo Governance 미상세 |
| 3 | V3-003 | V3 비용 상한 현실성 (GPU A10G만 ~$144/월) |
| 4 | V3-004 | GraphRAG 90% 벤치마크 정의 없음 |

---

# 4. 구현 전 필수 준비사항 체크리스트

## 4.1 V0 착수 전 체크리스트 ✅

### A. 외부 서비스 (API Key / 계정)

| # | 항목 | 필수/선택 | 용도 | 확인 |
|---|------|----------|------|------|
| 1 | **OpenAI API Key** | **필수** | gpt-4o-mini 폴백 모델, text-embedding-3-small | ☐ |
| 2 | .env.example 파일 생성 | 필수 | API Key 템플릿 | ☐ |

### B. 소프트웨어 설치

| # | 소프트웨어 | 버전 | 용도 | 확인 |
|---|-----------|------|------|------|
| 1 | **Python** | 3.11+ | AI/ML 백엔드 | ☐ |
| 2 | **Node.js** | 18+ LTS | React/Tauri 프론트엔드 | ☐ |
| 3 | **Rust** | 1.70+ stable | Tauri 2.0 IPC 레이어 | ☐ |
| 4 | **Ollama** | 0.1+ | 로컬 LLM 서빙 | ☐ |
| 5 | **Git** | Latest | 소스 관리 | ☐ |
| 6 | `ollama pull llama3.2:3b` | - | Mini LLM 모델 | ☐ |
| 7 | `ollama pull llama3.1:8b` | - | Main LLM 모델 | ☐ |

### C. Python 핵심 패키지 (V0 필수 ~33개)

```
# Core
pydantic>=2.10  pydantic-settings>=2.7  langgraph>=0.2.60
langchain-core>=0.3.25  langchain-community>=0.3.15  langchain-openai>=0.2.14
FlagEmbedding>=1.3.0  sentence-transformers>=3.3  torch>=2.5
openai>=1.58  chromadb>=0.5.23  aiosqlite>=0.20  sqlalchemy>=2.0.36
alembic>=1.14  nemoguardrails>=0.11  guardrails-ai>=0.5.15
httpx>=0.28  starlette>=0.41  uvicorn>=0.34  sse-starlette>=2.2
tiktoken>=0.8  python-dotenv>=1.0  structlog>=24.4  orjson>=3.10
tenacity>=9.0  aiofiles>=24.1  rich>=13.9

# Dev
pytest>=8.3  pytest-asyncio>=0.24  ruff>=0.8  mypy>=1.13  pytest-cov>=6.0
```

### D. Frontend 패키지 (V0 필수 ~28개)

```
# Dependencies (14)
react  react-dom  react-router-dom  @tauri-apps/api  @tauri-apps/plugin-shell
zustand  @tanstack/react-query  recharts  @xyflow/react  date-fns
clsx  lucide-react  sonner  zod

# DevDependencies (14)
typescript  vite  @vitejs/plugin-react  vitest  @testing-library/react
@testing-library/jest-dom  jsdom  @tauri-apps/cli  tailwindcss
postcss  autoprefixer  eslint  prettier  @typescript-eslint/parser
```

### E. Rust 패키지 (V0 필수 ~15개)

```
tauri ^2.2  tauri-plugin-shell ^2.2  serde ^1.0  serde_json ^1.0
tokio ^1.42  reqwest ^0.12  chrono ^0.4  uuid ^1.11
thiserror ^2.0  anyhow ^1.0  tracing ^0.1  tracing-subscriber ^0.3
toml ^0.8  dirs ^5.0
```

### F. 설정 파일 (V0 필수)

| # | 파일 | 핵심 LOCK 값 | 확인 |
|---|------|-------------|------|
| 1 | `config/config.v1.toml` | 20개 LOCK 값 (§4.1.G 참조) | ☐ |
| 2 | `.env.example` | OPENAI_API_KEY 외 9개 키 플레이스홀더 | ☐ |
| 3 | `.vamosrules.json` | BASE 1.3 규칙 구조화 | ☐ |

### G. config.v1.toml 핵심 LOCK 값 (20개)

```toml
[core]
single_decision_lock = true                    # LOCK

[llm]
mini_model = "ollama/llama3.2:3b"
main_model = "ollama/llama3.1:8b"
fallback_model = "gpt-4o-mini"

[embedding]
model = "bge-m3"                               # LOCK (DEC-005)
dimension = 1024                               # LOCK

[vector_db]
backend = "chroma"                             # LOCK (V1)
mode = "embedded"

[graph_db]
backend = "json_file"                          # LOCK (V1)

[cost]
daily_limit = 1300                             # ABSOLUTE LOCK (BASE §5)
monthly_limit = 40000                          # ABSOLUTE LOCK
warn_threshold = 80                            # LOCK (D7 §4)
block_threshold = 100                          # LOCK

[guardrails]
layer1_enabled = true
layer2_enabled = true
layer3_enabled = false                         # V0: GPU 부하 방지

[semantic_cache]
similarity_threshold = 0.95                    # LOCK (AC-D6-010)

[logging]
trace_id_required = true                       # LOCK

[mcp]
transport = "streamable_http"                  # LOCK (DEC-017)

[self_check]
threshold_p0 = 70                              # LOCK
threshold_p1 = 75                              # LOCK
threshold_p2 = 80                              # LOCK
soft_loop_max = 1                              # LOCK

[approval]
timeout_s = 600                                # LOCK
p2_timeout_s = 300                             # LOCK

[blue_nodes]
active_node_cap = 3                            # LOCK (V1, D2.0-03 §4.3-B)

[ui]
min_width = 1280                               # LOCK (V1, D8 §3.1)
```

### H. 디렉토리 구조 (V0 스캐폴딩)

```
vamos/
├── src/                    # React Frontend
├── src-tauri/              # Rust/Tauri IPC
├── backend/                # Python AI/ML
│   ├── vamos_core/
│   │   ├── schemas/        # D2.1 스키마 Pydantic 코드
│   │   ├── orange_core/    # I-1~I-5 + Gates
│   │   ├── blue_nodes/     # P0 노드
│   │   ├── infra/          # Brain Adapter, Tool Runtime
│   │   ├── storage/        # SQLite + Chroma
│   │   ├── safety/         # Guardrails
│   │   └── workflow/       # LangGraph 파이프라인
│   └── main.py             # stdin/stdout IPC 서버
├── shared/types/           # 공유 TypeScript 타입
├── config/                 # config.v1.toml + .env
├── data/                   # SQLite/Chroma/logs/graph
└── tests/                  # 테스트
```

### I. 문서 수정 (V0 전 필수 8건)

| # | 대상 파일 | 수정 내용 | 소요 |
|---|----------|----------|------|
| 1 | PLAN-3.0 §2.3 | I-모듈 번호 경고 + DESIGN 정본 링크 | 30분 |
| 2 | D2.0-03 | P0 도메인 리스트 확정 (Dev/Research/Productivity) | 15분 |
| 3 | D2.1-D2 | Storage event_type 5개 등록 | 30분 |
| 4 | D2.0-07 §9 | 다운시프트 임계값 정본 명시 (§4 LOCK) | 15분 |
| 5 | STEP7 F-I | Python backend 정본 주석 | 10분 |
| 6 | STEP7 F-I | 디렉토리 구조 PHASE_B2 정본 주석 | 10분 |
| 7 | STEP7 F-I | config.toml 통일 주석 | 10분 |
| 8 | D2.1-D1~D8 | 버전 v3.0.0 일괄 승격 | 1시간 |

---

## 4.2 V1 착수 전 추가 체크리스트

### A. 추가 API Key (4개)

| # | API Key | 용도 | 필수 시점 |
|---|---------|------|----------|
| 1 | **Tavily API Key** | 웹 검색 MCP (E-2) | V1 Week 5+ |
| 2 | **SerpAPI Key** | 검색엔진 MCP | V1 Week 5+ |
| 3 | **E2B API Key** | 코드 샌드박스 실행 (E-4) | V1 Week 5+ |
| 4 | **Unstructured.io API Key** | 문서 파싱 (E-3) | V1 Week 5+ |

### B. 추가 소프트웨어

| # | 소프트웨어 | 용도 |
|---|-----------|------|
| 1 | **Docker** | 코드 실행 샌드박스 (네트워크 비활성, 30초 타임아웃) |
| 2 | **SQLCipher** | AES-256-CBC 데이터 암호화 (S7E-032 CRITICAL) |
| 3 | **Playwright** | E2E 테스트 |
| 4 | **tauri-driver** | WebDriver E2E 통합 |
| 5 | **Tauri Signing Key** | 앱 코드 서명 (릴리스 빌드) |

### C. 추가 문서 수정 (21건)

V1-001~V1-016, CC-002~CC-009 해결을 위한 파일 수정 (상세: §10.2 참조)

### D. CI/CD 설정

- GitHub Actions 8단계 파이프라인 구성
- 필수 Secrets: `TAURI_SIGNING_PRIVATE_KEY`, `TAURI_SIGNING_PRIVATE_KEY_PASSWORD`

---

## 4.3 V2 착수 전 추가 체크리스트

### A. 추가 API Key / 계정

| # | 항목 | 용도 | 월 비용 |
|---|------|------|---------|
| 1 | Anthropic API Key | Claude Sonnet LLM | 종량제 |
| 2 | Qdrant API Key | 벡터 DB | Free~유료 |
| 3 | Slack Webhook URL | 배포 알림 | 무료 |
| 4 | VPS 호스팅 | Docker Compose 서버 | ~₩20,000 |
| 5 | PostgreSQL 16 계정 | 메인 DB | ~₩10,000 |
| 6 | Neo4j Community | 그래프 DB (GPL 주의) | 무료 |
| 7 | Redis 7 | 캐시/메시지 | 무료(로컬) |

### B. 추가 소프트웨어

Docker Compose, PostgreSQL 16, Qdrant, Neo4j Community, Redis 7, Nginx/Traefik, Loki

### C. 마이그레이션 스크립트 (3건)

1. SQLite → PostgreSQL (데이터 마이그레이션)
2. Chroma → Qdrant (벡터 재임베딩, needs_reembedding 플래그)
3. NetworkX JSON → Neo4j (Cypher 쿼리 매핑)

---

## 4.4 V3 착수 전 추가 체크리스트

| # | 항목 | 용도 | 월 비용 |
|---|------|------|---------|
| 1 | Kubernetes 클러스터 | K8s 배포 | 변동 |
| 2 | GPU 서버 (A10G) | vLLM 추론 | ~$144 |
| 3 | Helm Charts / ArgoCD | 배포 자동화 | - |
| 4 | KUBECONFIG | K8s 접근 설정 | - |
| 5 | Qdrant Cloud | 관리형 벡터 DB | 유료 |
| 6 | Neo4j Aura | 관리형 그래프 DB | 유료 |

---

# 5. 구현 단계 순서 및 의존성

## 5.1 V0 (1-2주): 구조 골격

```
Week 0 (사전):
  ├─ BLOCKER 8건 문서 수정
  ├─ 소프트웨어 설치 (Python/Node/Rust/Ollama/Git)
  └─ OpenAI API Key 확보

Week 1:
  ├─ [V0-S1] Monorepo 스캐폴딩 (PHASE_B2 기반)
  ├─ [V0-S2] Tauri 2.0 + React 프로젝트 초기화
  ├─ [V0-S3] Rust IPC 브릿지 셸 구현
  ├─ [V0-S4] Python backend stdin/stdout 서버 셸 구현
  └─ [V0-S5] config.v1.toml 생성 (20개 LOCK 값)

Week 2:
  ├─ [V0-S6] D2.1 스키마 → Pydantic v2 코드 생성 (24개)
  ├─ [V0-S7] D2.1 스키마 → Zod 코드 생성 (TypeScript)
  ├─ [V0-S8] SQLite 초기 마이그레이션 (Alembic)
  ├─ [V0-S9] Chroma embedded 초기화
  ├─ [V0-S10] 최소 LogEvent 기록 (JSONL)
  └─ [V0-S11] CLI 기본 입출력 (echo 수준)
```

**V0 의존성 그래프**:
```
V0-S1 → V0-S2 → V0-S3 → V0-S4 (순차)
V0-S1 → V0-S5 (병렬)
V0-S6, V0-S7 (V0-S1 이후 병렬)
V0-S8, V0-S9 (V0-S4 이후 병렬)
V0-S10 → V0-S11 (순차)
```

## 5.2 V1 (8-12주): MVP

```
Phase 1 (Week 1-4): ORANGE CORE
  ├─ I-1 Intent Detector (의도 분석)
  ├─ I-2 Context Builder (RAG/증거 수집)
  ├─ I-5 Routing & Decision Kernel (결정 잠금)
  ├─ I-8 Policy Engine (정책 게이트)
  ├─ I-9 Cost Manager (비용 게이트)
  ├─ I-19 Approval Manager (승인 게이트)
  └─ I-20 Failure/Fallback Manager (실패 처리)

Phase 2 (Week 3-6): Storage + Memory + Safety
  ├─ I-3 Memory System (L0/L1)
  ├─ I-14 Summarizer & Memory Distiller
  ├─ I-6 Self-check Engine
  ├─ I-15 Evidence & QoD Manager
  ├─ Storage Layer (SQLite + Chroma + JSONL)
  ├─ Guardrails Layer 1 (NeMo) + Layer 2 (Guardrails AI)
  └─ PII 감지/마스킹 (S7E-031)

Phase 3 (Week 5-8): Blue Nodes + External Tools
  ├─ I-17 Blue Node Manager
  ├─ I-10 Tool Registry/Router
  ├─ P0 Blue Nodes (Dev, Research, Productivity)
  ├─ E-1 Coding Helper
  ├─ E-2 Web Search (Tavily/SerpAPI MCP)
  ├─ E-3 Document Parser (Unstructured MCP)
  ├─ E-4 Code Executor (E2B MCP + Docker 샌드박스)
  ├─ E-5 Image Analyzer
  └─ E-6 Z3 Solver

Phase 4 (Week 7-10): UI/UX + Workflow
  ├─ I-11 Output Composer
  ├─ I-13 Multimodal Output Renderer
  ├─ I-4 Multimodal Interpreter
  ├─ I-16 Knowledge Search Engine
  ├─ A-1 MultiBrain Adapter
  ├─ A-2 Preset Modularization
  ├─ Builder UI (3패널)
  └─ Hologram View (기본)

Phase 5 (Week 9-12): Integration + Test + Release
  ├─ 9-State 머신 통합 테스트
  ├─ 5-Gate 통과 E2E 테스트
  ├─ ResponseEnvelope 3단 출력 검증
  ├─ 보안 14개 CRITICAL 항목 검증 (§9)
  ├─ CI/CD 파이프라인 구축
  ├─ 단위 테스트 80%+ 커버리지
  └─ V1 릴리스 빌드
```

**V1 의존성 핵심**:
- Phase 1(ORANGE CORE)이 완료되어야 Phase 2(Storage), Phase 3(Blue Nodes) 시작 가능
- Phase 2, Phase 3은 부분적으로 병렬 가능
- Phase 4(UI)는 Phase 1 API 정의 이후 시작 가능
- Phase 5(Integration)는 Phase 1-4 모두 필요

---

# 6. 문서 간 충돌/불일치 사항

## 6.1 BLOCKER 수준 충돌 (4건)

| # | 충돌 문서 | 내용 | 정본 결정 |
|---|----------|------|----------|
| 1 | PLAN-3.0 vs DESIGN 2.0 | I-모듈 번호/명칭 전면 불일치 | **DESIGN 2.0 정본** |
| 2 | D2.0-02 vs D2.0-04 vs D2.0-07 | 다운시프트 임계값 80%/100% 권위 수준 | **D2.0-07 §4 LOCK 정본** |
| 3 | STEP7 F-I vs PLAN-3.0 | Python backend vs Node.js sidecar | **PLAN-3.0 정본** |
| 4 | D2.0-06 vs D2 레지스트리 | Storage event_type 미등록 | D2 레지스트리에 추가 |

## 6.2 HIGH 수준 충돌 (6건)

| # | 충돌 문서 | 내용 | 정본 결정 |
|---|----------|------|----------|
| 1 | BASE/PLAN/DESIGN | QoD 가중치 4요소 vs 5요소 | PLAN-3.0 5요소 |
| 2 | D2.0-02 | QoD 수치 "발명 금지" vs CLAUDE.md 0.4/0.7 | 운영 기본값으로 채택 |
| 3 | BASE vs DESIGN | Front Mini LLM 독립 계층 vs I-1 서브컴포넌트 | I-1 서브컴포넌트 |
| 4 | PLAN vs DESIGN | 2-Tier LLM 시작 시점 (V2 vs V1) | DESIGN (V1부터) |
| 5 | D7 vs D2 | ApprovalSchema status 2값 vs 4값 | D7 SOT: 4값 |
| 6 | D7 vs MASTER_SPEC | Guardrails 3Layer vs 4Layer | 4Layer 정본 |

## 6.3 MEDIUM 수준 충돌 (5건)

| # | 충돌 문서 | 내용 |
|---|----------|------|
| 1 | STEP7 vs BASE | 비용 상한 $8 vs ₩40,000 (단위/기준 차이) |
| 2 | PHASE_B2 vs STEP7-F | 디렉토리 구조 차이 |
| 3 | PHASE_B4 vs STEP7 | Config 파일 포맷 (toml vs yaml) |
| 4 | PHASE_B7 | `streamable-http` vs `streamable_http` (하이픈 vs 언더스코어) |
| 5 | PHASE_B7 | `datetime.utcnow()` (deprecated) 사용 |

---

# 7. 버전별 외부 서비스/API Key/계정 총정리

## 7.1 V0 (1건)

| 서비스 | 키/계정 | 환경변수 | 용도 | 비용 |
|--------|--------|---------|------|------|
| OpenAI | API Key | `OPENAI_API_KEY` | 폴백 LLM (gpt-4o-mini) | 종량제 (V1 ₩40K/월 이내) |

## 7.2 V1 (4건 추가)

| 서비스 | 키/계정 | 환경변수 | 용도 | 비용 |
|--------|--------|---------|------|------|
| Tavily | API Key | `TAVILY_API_KEY` | 웹 검색 MCP | Free tier 가능 |
| SerpAPI | API Key | `SERPAPI_KEY` | 검색엔진 MCP | Free tier 가능 |
| E2B | API Key | `E2B_API_KEY` | 코드 샌드박스 | Free tier 가능 |
| Unstructured.io | API Key | `UNSTRUCTURED_API_KEY` | 문서 파싱 | Free tier 가능 |

## 7.3 V2 (7건 추가)

| 서비스 | 키/계정 | 비용 |
|--------|--------|------|
| Anthropic (Claude) | `ANTHROPIC_API_KEY` | 종량제 |
| Qdrant | `QDRANT_API_KEY` + `QDRANT_URL` | Free~유료 |
| PostgreSQL 16 | `POSTGRES_DSN` + User/PW | ~₩10K/월 |
| Neo4j Community | `NEO4J_URI` + User/PW | 무료 (GPL 주의) |
| Redis 7 | 로컬 설치 | 무료 |
| VPS 서버 | SSH Key + Host | ~₩20K/월 |
| Slack Webhook | `SLACK_WEBHOOK_URL` | 무료 |

## 7.4 V3 (3건 추가)

| 서비스 | 키/계정 | 비용 |
|--------|--------|------|
| K8s 클러스터 | `KUBECONFIG` | 변동 |
| GPU 서버 (vLLM) | - | ~$144/월 |
| Qdrant Cloud / Neo4j Aura | 관리형 | 유료 |

## 7.5 GitHub Secrets 전체 목록 (11개)

| # | Secret | 필요 시점 |
|---|--------|----------|
| 1 | `TAURI_SIGNING_PRIVATE_KEY` | V1+ |
| 2 | `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` | V1+ |
| 3 | `DEPLOY_SSH_KEY` | V2+ |
| 4 | `DEPLOY_HOST` | V2+ |
| 5 | `POSTGRES_USER` | V2+ |
| 6 | `POSTGRES_PASSWORD` | V2+ |
| 7 | `QDRANT_API_KEY` | V2+ |
| 8 | `NEO4J_AUTH` | V2+ |
| 9 | `OPENAI_API_KEY` | V2+ (CI/CD) |
| 10 | `KUBECONFIG` | V3 |
| 11 | `SLACK_WEBHOOK_URL` | V2+ |

---

# 8. 버전별 소프트웨어/인프라 설치 총정리

## 8.1 V0 필수 설치

| 카테고리 | 항목 | 수량 |
|---------|------|------|
| 런타임 | Python 3.11+, Node.js 18+, Rust 1.70+ | 3 |
| 서버 | Ollama (로컬 LLM) | 1 |
| 모델 | llama3.2:3b, llama3.1:8b | 2 |
| Python 패키지 | 코어 27 + 개발 5 | 32 |
| npm 패키지 | deps 14 + devDeps 14 | 28 |
| Cargo 크레이트 | 14 | 14 |
| **합계** | | **80** |

## 8.2 V1 추가 설치

| 항목 | 수량 |
|------|------|
| Docker (코드 샌드박스) | 1 |
| SQLCipher (암호화) | 1 |
| Playwright + tauri-driver (E2E) | 2 |
| Tauri Signing Key (생성) | 1 |

## 8.3 V2 추가 설치

| 항목 | 수량 |
|------|------|
| Docker Compose | 1 |
| PostgreSQL 16 | 1 |
| Qdrant Server | 1 |
| Neo4j Community | 1 |
| Redis 7 | 1 |
| Nginx/Traefik | 1 |
| Loki | 1 |
| Python 추가 패키지 (7+) | 7 |

## 8.4 V3 추가 설치

| 항목 | 수량 |
|------|------|
| Kubernetes 클러스터 | 1 |
| Helm + ArgoCD | 2 |
| vLLM | 1 |
| Prometheus + OpenTelemetry | 2 |
| GPU 드라이버 (CUDA) | 1 |

---

# 9. 보안 필수 항목 (V1 CRITICAL)

V1 릴리스 전 반드시 구현해야 할 보안 항목 **15건** *(14 S7E 항목 + 1 DEC-003 Allowlist, Phase 11 S11-6 SC-3 갱신)*:

| # | ID | 항목 | 우선순위 | V1 구현 방법 |
|---|-----|------|---------|-------------|
| 1 | S7E-001 | STRIDE 위협 모델링 | CRITICAL | 문서화 + 기본 대응 |
| 2 | S7E-003 | OWASP Top 10 for LLM | CRITICAL | 모든 항목 제어 매핑 |
| 3 | S7E-011 | 지시 계층구조 (system/user/tool 우선순위) | CRITICAL | XML 태그 기반 신뢰 경계 |
| 4 | S7E-012 | 입출력 태깅 | CRITICAL | `<system>/<user>/<tool>` 태그 |
| 5 | S7E-013 | 카나리 토큰 감지 | CRITICAL | 정적 카나리 (V1) |
| 6 | S7E-015 | Tool 호출 검증 | CRITICAL | 화이트리스트 + 기본 검증 |
| 7 | S7E-021 | 로컬 인증 | CRITICAL | Windows Hello / PIN |
| 8 | S7E-031 | PII 감지/마스킹 | CRITICAL | Regex 패턴 (한국어 + 글로벌) |
| 9 | S7E-032 | 데이터 암호화 (at-rest) | CRITICAL | SQLCipher (AES-256-CBC) |
| 10 | S7E-033 | 데이터 주권 | CRITICAL | 전부 로컬, 클라우드 전송 금지 |
| 11 | S7E-005 | API Key 관리 | HIGH | .env + dotenv + .gitignore |
| 12 | S7E-006 | 입력 검증 | HIGH | Zod + regex 패턴 |
| 13 | S7E-008 | Rate limiting/비용 | HIGH | 로컬 카운터 + 일/월 hard cap |
| 14 | S7E-017 | Jailbreak 방어 | HIGH | Guardrail override 차단 |
| 15 | DEC-003 | 도구 승인 Allowlist | HIGH | 읽기전용=자동허용, 외부API/쓰기/코드실행=확인 필요 *(Phase 11 S11-6 SC-3 추가)* |

---

# 10. 문서 수정 필요 목록

## 10.1 V0 전 필수 수정 (8건)

| # | 대상 파일 | 수정 내용 | 이슈 ID |
|---|----------|----------|---------|
| 1 | PLAN-3.0 §2.3 | I-모듈 DEPRECATE 경고 + DESIGN 정본 링크 | X-01 |
| 2 | D2.0-03 | P0 도메인 리스트: Dev/Research/Productivity | BN-13 |
| 3 | D2.1-D2 EventTypeRegistry | storage.* 5개 + failure 1개 + fallback 1개 등록 | ST-35 |
| 4 | D2.0-07 §9 | "§4의 80%/100%는 LOCK. 본 섹션은 운영 조정 범위 명시" | DS-66 |
| 5 | STEP7 F-I | "PLAN-3.0 정본: Python backend" 주석 | V0-004 |
| 6 | STEP7 F-I | "PHASE_B2 monorepo 정본" 주석 | V0-003 |
| 7 | STEP7 F-I / MASTER_SPEC | config.yaml → config.toml 통일 | V0-005 |
| 8 | D2.1-D1~D8 | 전체 v3.0.0 승격 | CC-001 |

## 10.2 V1 전 수정 (21건)

| # | 대상 파일 | 수정 내용 | 이슈 ID |
|---|----------|----------|---------|
| 1 | MASTER_SPEC §0 | B-group에 "(= IMPLEMENTATION 계층)" 추가 | V0-002 |
| 2 | D2.0-01 §8.5 | V0 비용 상한 = V1 동일 (₩40,000) 명시 | V0-001 |
| 3 | BEGINNER_GUIDE | I-21~I-25 추가, E-15/S-5 명칭 수정 | V1-001/002/003 |
| 4 | MASTER_SPEC | I-21~I-25 모듈 정의 추가 | V1-016 |
| 5 | D2.1-D2 | DecisionSchema approval_status 4값으로 통일 | V1-004 |
| 6 | AGENT_TEAMS_SPEC | datetime.utcnow() → datetime.now(timezone.utc) | V1-005 |
| 7 | MASTER_SPEC / D6 | QoD 5요소 공식 통일 | V1-006 |
| 8 | D2.0-02 / MASTER_SPEC | Front Mini LLM = I-1 서브컴포넌트 명시 | V1-007 |
| 9 | D2.0-02 §DEC-002 | LangChain 허용 어댑터 명시적 목록 | V1-009 |
| 10 | D2.0-07 / D2.1-D7 | 4-Layer Guardrails + L4 필드 추가 | V1-010 |
| 11 | STEP7 / BASE | 비용 $8 = "최소 운영 목표", BASE ₩40K = 정본 | V1-013 |
| 12 | PHASE_B3 | React 18.3 확정 | V1-014 |
| 13 | MASTER_SPEC | Python backend 진입점: backend/main.py | V1-015 |
| 14 | D2.1-D2 EventTypeRegistry | agent.* / sdar.* 이벤트 등록 | CC-006 |
| 15 | BEGINNER_GUIDE | 모듈 목록 전체 업데이트 | CC-002 |
| 16 | D2.1-D6 | QoD SourceQoDSchema 5필드 추가 | V1-006 |
| 17 | D2.0-03 | Blue Node failure_code 정식 등록 | BN-18 |
| 18 | PHASE_B7 | `streamable-http` → `streamable_http` 수정 | IC-002 |
| 19 | PHASE_B7 | `datetime.utcnow()` → `datetime.now(timezone.utc)` 수정 | IC-001 |
| 20 | PHASE_B7 | 플레이스홀더 패스워드 제거/환경변수화 | CF-003/004 |
| 21 | BEGINNER_GUIDE | B-Series ↔ L-Series 매핑표 추가 | CC-009 |

## 10.3 V2 전 수정 (7건)

| # | 대상 파일 | 수정 내용 | 이슈 ID |
|---|----------|----------|---------|
| 1 | CLOUD_LIBRARY_SPEC | 10-Layer → "CL-Layer" 접두사 | V2-001 |
| 2 | SDAR_SPEC | 활성화 조건 정의 | V2-002 |
| 3 | AGENT_TEAMS_SPEC | Lead Agent 위임 vs FREEZE 구분 명시 | V2-003 |
| 4 | STEP7 보강 | TITLE_ONLY ~190건 상세화 | V2-008 |
| 5 | STEP7 | 모듈 링크 I(memory) → I-3 구체화 | CC-005 |
| 6 | AGENT_TEAMS_SPEC | HMAC 키 관리 프로토콜 설계 | CC-012 |
| 7 | D2.0-01/MASTER_SPEC | Gate G0-G4 → CL-G 접두사 | CC-004 |

---

# 11. 위험 요소 및 대응 방안

## 11.1 V0/V1 위험 요소

| # | 위험 | 영향 | 가능성 | 대응 |
|---|------|------|--------|------|
| 1 | V1 비용 ₩40K/월 매우 빡빡함 | API 호출 제한 | 높음 | Mini 90%+ 전략, 80% 경고 시 Mini 전용 강제 |
| 2 | DecisionSchema 17필드 복잡도 | 구현 오류 | 중간 | 단계적 구현 (필수 8필드 → 전체 17필드) |
| 3 | 53+ event_type 개발자 부담 | 누락 위험 | 중간 | V0에서 핵심 10개만 → V1에서 전체 확장 |
| 4 | PyTorch + BGE-M3 로컬 추론 성능 | 느린 임베딩 | 중간 | CPU 모드 fallback + 배치 처리 |
| 5 | Python-Rust JSON-RPC 통신 안정성 | IPC 실패 | 낮음 | tenacity 재시도 + 헬스체크 |
| 6 | GPL-3.0 Neo4j Community 라이선스 | V2 법적 위험 | 낮음 | 독립 서버 실행으로 격리 |

## 11.2 미확인(ir-series) 항목

| 항목 | 상태 | 조치 |
|------|------|------|
| ir-006 (빈자리 TBD 슬롯) | V1 구현 시 확인 | TBD 남은 곳 채우기 |
| ir-009 (TSZ 오픈소스 패턴) | 검토 필요 | 구현 시 적합성 평가 |
| 02 (BASE 1.0 참조) | STEP7 확인 | BASE 1.3이 정본 확인 |

---

# 부록: V0 GO/NO-GO 최종 체크리스트

| # | 항목 | 상태 | 비고 |
|---|------|------|------|
| 1 | 4계층 아키텍처 확정 | ✅ GO | Front Mini→ORANGE→BLUE→OTHER |
| 2 | 5-Phase 파이프라인 확정 | ✅ GO | Perception→Reasoning→Action→Memory→Reflection |
| 3 | 9-State 머신 확정 | ✅ GO | S0~S8 전체 정의 |
| 4 | 5-Gate 시스템 확정 | ✅ GO | Policy/Cost/Approval/Evidence/SelfCheck |
| 5 | 81모듈 카탈로그 확정 | ✅ GO | I/E/S/A/B/EVX 전체 |
| 6 | 24개 JSON Schema 확정 | ✅ GO | DN-001~016 전부 해결 |
| 7 | Tech Stack 확정 | ✅ GO | Tauri+React+Rust+Python LOCK |
| 8 | 비용 상한 확정 | ✅ GO | V1=₩40K/월 ABSOLUTE LOCK |
| 9 | 문서 우선순위 확정 | ✅ GO | RULE > PLAN > DESIGN LOCK > 본문 > 스키마 |
| 10 | BLOCKER 해결 가능 | ✅ GO | 8건 모두 문서 수정 (코드 불필요) |
| 11 | 외부 의존성 최소 | ✅ GO | V0는 OpenAI Key 1개만 필수 |
| 12 | 진정한 미결정 사항 | ✅ GO | V0/V1에 0건 (V2에만 2건) |
| 13 | PLAN 3.0 vs DESIGN 2.0 I-모듈 매핑 | ⚠️ 수정 필요 | BLOCKER #1 |
| 14 | P0 도메인 리스트 | ⚠️ 수정 필요 | BLOCKER #2 |
| 15 | Storage 이벤트 코드 등록 | ⚠️ 수정 필요 | BLOCKER #3 |
| 16 | 다운시프트 임계값 정본 통일 | ⚠️ 수정 필요 | BLOCKER #4 |

**최종 판정: ⚠️ 조건부 GO — BLOCKER 8건 문서 수정 (~3시간) 후 즉시 V0 착수 가능**

---

> 본 문서는 VAMOS AI 39개 산출물 전체를 빠짐없이 스캔하여 작성되었습니다.
> 검토 범위: RULE(1) + PLAN(2) + DESIGN(8) + SCHEMA(9) + PHASE(7) + SPEC(5) + STEP7(5) + GUIDE(1) + 검증보고서(1) = **39개 파일**
