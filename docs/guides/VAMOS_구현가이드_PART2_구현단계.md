# VAMOS AI 구현 가이드 — PART 2: 구현단계 진입

<!-- v26.0.0 -->
> **버전**: v26.0.0 | **작성일**: 2026-02-24 | **최종갱신**: 2026-03-15
> **전제조건**: PART1 체크리스트 전체 완료 후 진입
> **정본 근거**: `STEP6_pipeline/output/updated/` 43개 산출물 전수 분석 기반 (4차 정밀 스캔 반영, 5차 소스문서 전수 크로스체크 완료, 6차 구현 시뮬레이션 검토 반영, 7차 잔존이슈 방법론 v1.1 Track A 19건 반영, 8차 V2/V3 실행 가이드 추가, 9차 Phase 2-A Ripple Fix 11건+Phase 2-B 재검증 1건, 10차 v10 Phase 2 누락 항목 반영, 11차 메이커 에반 7개 개선안 반영, 12차 v11 적대적 검증 179건 수정, 13차 V1 Phase 1~6 파일경로 칼럼 추가, 14차 V0~V3 AI 프롬프트 전수 검토/보완)
> **정본 우선순위**: RULE 1.3 > PLAN 3.0 > DESIGN 2.0 LOCK > DESIGN 본문 > 스키마/TECH_STACK

---

# 목차

- [1. 전체 구현 로드맵 개요](#1-전체-구현-로드맵-개요)
- [2. V0 구현 — 구조 기반 (1-2주)](#2-v0-구현)
- [3. V1 구현 — MVP (14-16주)](#3-v1-구현)
- [4. V2 구현 — Pro Server (11-13주)](#4-v2-구현)
- [5. V3 구현 — Enterprise (12-16주)](#5-v3-구현)
- [6. 시스템별 상세 구현 가이드](#6-시스템별-상세-구현-가이드)
- [7. 최종 검토사항](#7-최종-검토사항)
- [Reading Guide](#reading-guide)
- [Glossary](#glossary)

---

## Reading Guide

> 이 문서는 ~4,700줄 규모의 구현 가이드입니다. 효율적으로 활용하기 위한 안내입니다.

| 대상 | 추천 섹션 | 설명 |
|------|----------|------|
| 처음 읽는 사람 | §1 → Reading Guide → Glossary | 전체 구조와 용어 파악 |
| V0 구현 시작 | §2 (STEP-1~6 순서대로) | 각 STEP의 AI 프롬프트를 Claude에 입력 |
| V1 구현 | §3 (Phase 1~6 순서대로) | 17개 CORE 모듈 구현 |
| V2/V3 구현 | §4, §5 | COND/EXP 모듈 + 인프라 확장 |
| 시스템 설계 참조 | §6 (6.1~6.13) | 보안, 테스트, 운영, SDAR 등 상세 |
| 전환/검증 | §7 (GO/NO-GO) | 각 버전 전환 조건 체크리스트 |

**핵심 규약**: **LOCK**(절대 변경 불가), **FREEZE**(구조 고정, 값 변경 가능), **SOT**(정본 문서 — 충돌 시 SOT 우선)

---

## Glossary

| 약어/용어 | 정식명 | 설명 |
|----------|--------|------|
| VAMOS | Virtual AI Mind Operating System | AI 멀티버전 운영 체제 |
| V0/V1/V2/V3 | Version 0~3 | Scaffold→MVP→Pro→Enterprise |
| CORE/COND/EXP | Module Category | 핵심/조건부/실험 모듈 |
| I-Series (I-1~I-25) | Internal Module | 내부 처리 모듈 |
| A/B/C/D-Series | Advanced/Learning/Reasoning/Generation | 고급/학습/추론/생성 모듈 |
| E-Series (E-1~E-16+) | External Module | 외부 통합 모듈 |
| S0~S8 | Pipeline State | 9-State 상태 머신 (RECEIVED→DONE) |
| S3a | APPROVE_WAIT | P2 승인 대기 하위 상태 (600s) |
| 5-Gate | Policy→Approval→Cost→Evidence→SelfCheck | 의사결정 검증 체계 |
| CL-G0~G4 | Cloud Library Gate | 수집 검증 게이트 |
| P0~P3 | Priority Level | 우선순위 (P0=긴급~P3=낮음) |
| L0~L3 | Memory Layer | Session→Project→Long-term→Procedural |
| AR-L1~L4 | Auto-Repair Level | SDAR 수리 수준 (LOW~CRITICAL) |
| SDAR | Self-Diagnosis and Auto-Repair | 자가진단/자동수리 엔진 |
| RT-BNP | Real-Time Breaking News Pipeline | 실시간 속보 파이프라인 |
| DCL | Domain Context Layer | 도메인 컨텍스트 계층 |
| QoD | Quality of Data | 데이터 품질 점수 |
| RBAC | Role-Based Access Control | 4레벨 (OWNER/ADMIN/OPERATOR/VIEWER) |
| MCP | Model Context Protocol | 도구 프로토콜 |
| HMAC | Hash-based Message Auth Code | MessageBus 인증 |
| PARL | Parallel Agent Runtime Layer | 병렬 에이전트 런타임 |
| SOT | Source of Truth | 정본 문서 |
| PHASE_B1~B7 | Build Phase Spec | 구현 명세 문서 |
| D2.0-01~08 | Design 2.0 Documents | 설계 문서 시리즈 |
| D2.1-D1~D8 | Schema Definition Docs | 스키마 정의 문서 |

---

# 1. 전체 구현 로드맵 개요

```
V0 (1-2주)     V1 (14-16주)             V2 (11-13주)         V3 (12-16주)
──────────── → ─────────────────────── → ─────────────────── → ──────────────────
구조 기반       Operational MVP           Pro Server            Enterprise

[Scaffold]     [Phase 1] ORANGE CORE    [Infra Upgrade]       [Scale-Up]
[Schemas]      [Phase 2] Storage+RAG    [Migration Scripts]   [Self-evo Full]
[IPC Bridge]   [Phase 3] Workflow       [Agent Teams V2]      [Agent Marketplace]
[Config]       [Phase 4] UI/UX          [SDAR AR-L3]          [K8s Deploy]
[CI Skeleton]  [Phase 5] Integration    [Cloud Library V2]    [vLLM + GPU]
               [Phase 6] AI Investing   [Security L3]         [Full EVX]
```

## 1.1 버전별 활성 모듈 수

| 버전 | I-Series | E-Series | S-Series | A-Series | B-Series | C-Series | D-Series | EVX | 합계 |
|------|---------|---------|---------|---------|---------|---------|---------|-----|------|
| V0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **5** |
| V1 | 17 | 6 | 1 | 2 | 1 | 3 | 2 | 0 | **32** |
| V2 | 22 | 10 | 1 | 3 | 1 | 3 | 2 | 0 | **42** |
| V3 | 25 | 16 | 8 | 7 | 6 | 7 | 6 | 6 | **81** | <!-- S7-265 v26 --> <!-- v12 Phase 3 S7: 모듈 수 검증 완료 — 190 신규 항목은 기존 모듈 내 구현으로 모듈 합계 변동 없음 -->

### 버전별 핵심 차이 비교표

| 항목 | V0 | V1 | V2 | V3 |
|------|-----|-----|-----|-----|
| **목적** | 실행 가능한 뼈대 | Operational MVP | Scale-Up | Enterprise |
| **기간** | 1-2주 | 14-16주 | 11-13주 | 12-16주 |
| **인프라** | 로컬 (Tauri) | 로컬 (Tauri) | VPS + Docker Compose (Hetzner 권장) | Hetzner Lite(권장)/K8s(선택) |
| **DB** | SQLite + Chroma | SQLite + Chroma | PostgreSQL + Qdrant + Neo4j | 관리형 DB + PVC |
| **LLM** | Ollama 단일 | Ollama + GPT-4o-mini | Claude + Ollama (2-tier) | Claude + vLLM (자체 호스팅) |
| **비용 상한** | ₩0 (로컬) | ₩40,000/월 LOCK | ₩93,000/월 LOCK | ₩266,000/월 ABSOLUTE LOCK |
| **자율도** | L1 (수동) | L2_COPILOT | L3_AUTONOMOUS | L4_SELF_EVOLVING |
| **모듈** | CORE 5개 | CORE 32개 | CORE+COND 42개 | 전체 81개 |
| **SDAR** | OFF | OFF | AR-L2~L3 | AR-L4 + Self-evo |
| **Agent** | 없음 | Lead+2 Sub | Teams 10 | Mesh 50+ |
| **보안** | 기본 (입력 검증) | 2-Layer Guardrails | 3-Layer + HMAC | 4-Layer + LlamaGuard |

## 1.2 의존성 체인 (필수 순서)

```
V0 완료 → V1 진입 → V1 완료 → V2 마이그레이션 → V2 완료 → V3 업그레이드
```

## 1.3 AI 구현 공통 규칙 <!-- v24 메이커에반 개선안 2+6 -->

> 모든 V0-STEP 및 V1~V3 Phase AI 프롬프트에 공통 적용되는 규칙입니다.
> 아래 R1~R11은 **모든 프롬프트의 규칙 섹션에서 강제 참조**됩니다.

### R1~R11 공통 규칙 레지스트리

| ID | 규칙 | 적용 범위 | 위반 시 조치 |
|----|------|----------|-------------|
| **R1** | Python ≥ 3.11 필수. f-string, `match/case`, `tomllib` 활용 | 모든 Python 코드 | 빌드 실패 (pyproject.toml python_requires) |
| **R2** | Pydantic v2 전용. `model_config = ConfigDict(...)` 사용, `class Config:` 금지 | 모든 스키마/모델 | CI lint 실패 |
| **R3** | **no-create**: 기존 파일 수정 우선. 새 파일 생성은 명시적 지시 시만 허용 | 모든 코드 생성 | AI에게 재지시 |
| **R4** | **no-delete**: 코드/파일 삭제 금지. `[DEPRECATE] + (대체 경로)` 처리만 허용 | 모든 코드 수정 | §1.3.1 #4 적용 |
| **R5** | LOCK/FREEZE 값 런타임 변경 금지 | config, 상수 | §1.3.1 #2 적용 |
| **R6** | SOT 문서에 없는 내용 창작 금지 | 모든 AI 생성물 | §1.3.1 #3 적용 |
| **R7** | 모듈 간 의존성: CORE→COND 단방향, 역방향 금지 | import 구조 | VAL-003 빌드 검증 |
| **R8** | trace_id 서버 생성 전용 (UUID v4). 클라이언트 전달 금지 | 보안 | §6.5.1 #3 |
| **R9** | 에러 메시지에 내부 정보 노출 금지 (스택 트레이스, DB 스키마 등) | 에러 핸들링 | §6.5.1 #7 |
| **R10** | 비용 상한 ABSOLUTE LOCK 준수 (V1: ₩40K, V2: ₩93K, V3: ₩266K) | Cost Gate | 실행 차단 |
| **R11** | `schema_registry.toml` 단일 참조점 활용 (v24 신설) | 스키마 참조 | 중복 정의 방지 |

### 1.3.1 판단 실패 시 규칙 (SDD 명세 계층)

AI가 구현 중 불확실한 상황에 직면했을 때 따라야 할 절대 규칙:

| # | 상황 | 조치 |
|---|------|------|
| 1 | 필드 수가 SOT(seed JSON / D2.1 스키마)와 다름 | **즉시 중단** + 사용자에게 불일치 보고. 임의 필드 추가/삭제 금지 |
| 2 | LOCK/FREEZE 값 변경 시도 | **거부**. LOCK 값은 runtime 변경 불가 (config.v1.toml frozen) |
| 3 | 참조 SOT 문서에 없는 내용 | **창작 금지**. "해당 스펙 미정의" 보고 후 사용자 판단 대기 |
| 4 | 삭제가 필요한 경우 | **삭제 금지**. `[DEPRECATE] + (대체 경로)` 로만 처리 |
| 5 | 모듈 간 의존성이 불명확 | 상위 문서(RULE 1.3 > PLAN 3.0 > DESIGN LOCK) 순서로 확인 후 판단 |

### 1.3.2 Claude Code 세션 운영 규칙

각 STEP/Phase 구현 세션에서 AI 도구 효율을 유지하기 위한 운영 지침:

| # | 시점 | 명령/행동 | 목적 |
|---|------|----------|------|
| 1 | 각 STEP/Phase 완료 후 | `/compact` 실행 | 컨텍스트 요약 → 토큰 비용 절감 + 맥락 오염 방지 |
| 2 | 코드 생성 완료 후 | `/review` 실행 | AI 자기 검토 → 품질 향상 |
| 3 | 장시간 세션 중 (30분+) | `/cost` 확인 | 비용 모니터링 → V1 ₩40,000/월 상한 준수 |
| 4 | 새 STEP/Phase 시작 시 | `/clear` 또는 새 세션 | 이전 맥락 간섭 방지 |
| 5 | 복수 파일 수정 시 | 순차 실행 (큐 방식) | 파일 간 충돌 방지, 변경 추적 용이 |

> **비용 절감 효과**: /compact + 세션 분리로 토큰 비용 30~50% 절감 예상 (에반 #13, #23 기반)

### 1.3.3 컨텍스트 다이어트 원칙 (AI 주의력 관리)

AI에게 과도한 문서를 제공하면 주의력(Attention) 분산으로 코드 정확도가 하락합니다. 각 STEP/Phase의 `참조 SOT 문서` 섹션 사용 시 아래 원칙을 적용하세요:

| 구분 | 정의 | AI 세션 적용 |
|------|------|-------------|
| **필수 로드 (MUST)** | 해당 STEP에서 직접 구현하는 기능의 SOT | @file 첨부 또는 직접 붙여넣기 |
| **선택 참조 (MAY)** | 관련되지만 직접 구현 대상이 아닌 문서 | 필요 시에만 부분 참조 |
| **참조 금지 (NEVER)** | 해당 STEP 범위 밖 문서 (다른 버전/다른 Phase) | 첨부 금지 — 토큰 낭비 + 환각 유발 |

> **핵심 원칙**: AI 한 세션에 첨부하는 SOT 문서는 **3~5개 이내**로 제한 (에반 #24 기반).
> 각 STEP/Phase의 `참조 SOT 문서` 섹션에 나열된 문서가 MUST 대상이며, 나열되지 않은 문서는 NEVER로 간주합니다.
> `schema_registry.toml`(§2 V0-STEP-2에서 생성)을 활용하면 스키마 참조를 단일 파일로 집중할 수 있습니다.

---

# 2. V0 구현

> **목표**: 실행 가능한 뼈대. 최소한의 파이프라인이 동작하는 상태.
> **기간**: 1-2주
> **비용**: ₩0 (로컬 정본) — API 연동 테스트 ~₩5,000은 비정본 예상치 (V1 한도 ₩40,000 사전 설정 통제)
> **활성 모듈**: I-1 Intent Detector, I-2 Context Builder, I-3 Memory System (STEP-5 L0 Session Memory로 구현), I-5 Decision Engine, I-19 Approval Manager (5개, READINESS_GUIDE §2.7 테이블 기준 — I-4 제외) <!-- SOURCE_CONFLICT: §2.8 체크리스트는 "I-1~I-5+I-19"(6개)로 표기하나, §2.7 상세 테이블에 I-4 미포함. §2.7이 더 구체적이므로 5개 채택 -->
> I-8(Policy), I-9(Cost), I-20(Failure/Fallback)은 V0에서 stub만 생성. 본격 구현은 V1 Phase 1.
> I-19(Approval)는 V0에서 스켈레톤 + 기본 auto-approve(P0/P1→auto, P2→hold) 수준. 본격 워크플로우는 V1.

---

## V0-STEP-1: 프로젝트 스캐폴딩 (Day 1-2)

### 작업 내용
1. **monorepo 초기화** (PHASE_B2 정본 기준)
```
vamos/
├── src/               # React 18 + TypeScript (PHASE_B2 canonical)
│   ├── components/
│   ├── hooks/
│   ├── stores/
│   ├── types/
│   └── App.tsx
├── src-tauri/         # Rust Tauri 2.0
│   ├── src/
│   │   ├── commands/  # IPC 핸들러
│   │   ├── models/    # serde 구조체
│   │   ├── bridge/    # Python 프로세스 관리 (PHASE_B2 §4.1 정본)
│   │   └── main.rs
│   ├── Cargo.toml
│   └── tauri.conf.json
├── backend/           # Python 3.11+ AI/ML
│   ├── vamos_core/    # 메인 패키지 (PHASE_B2 §5.1 정본)
│   │   ├── orange_core/   # I-Series 모듈
│   │   ├── blue_nodes/    # E-Series 실행
│   │   ├── infra/         # A-Series, 인프라
│   │   ├── agent/         # Agent Teams
│   │   ├── storage/       # B-Series, 메모리
│   │   ├── safety/        # 07 Gate, Guardrails
│   │   ├── schemas/       # Pydantic v2 스키마 (SOT)
│   │   ├── mcp/           # MCP 브릿지
│   │   └── rpc/           # JSON-RPC server <!-- NOTE (XREF-V0-12): PHASE_B2 정본에 rpc/ 미명시. Tauri↔Python 통신에 기능적 필요로 추가 -->
│   ├── tests/
│   └── pyproject.toml
├── shared/            # 공유 타입 (codegen)
│   └── types/
├── config/
│   ├── config.v1.toml # 메인 설정 (LOCK)
│   └── .env.example
├── data/              # SQLite DB, Chroma 데이터 <!-- NOTE (XREF-V0-10): CLAUDE.md 기준 추가. PHASE_B2 정본에는 명시적 data/ 미포함, 실무 필요로 추가 -->
├── logs/              # JSONL 로그 파일 <!-- NOTE: CLAUDE.md 기준 추가. PHASE_B2 정본에는 명시적 logs/ 미포함, 실무 필요로 추가 -->
├── scripts/           # 유틸리티 스크립트
├── docs/
├── .github/workflows/
├── CLAUDE.md
└── README.md
```

2. **의존성 설치**
   - Python: `poetry init` → core dependencies (PHASE_B3 기준)
   - Rust: `cargo init` → tauri, serde, tokio
   - Node: `pnpm init` → react, @tauri-apps/api, zustand

3. **config.v1.toml 기본 설정** — ⚠️ **V0 축약본 (참조용, 13섹션)** (PHASE_B4 §3 기준) <!-- B4 정본은 17섹션. V0에서 [blue_nodes],[ui],[rate_limit],[guardrails] 생략. 정본은 아래 §2 STEP-3의 V1 확장판(17섹션). 구현 시 B4 §3 전체를 참조하세요 -->
```toml
[core]                           # PHASE_B4 §3.1
autonomy_level = "L1"            # LOCK: L0(manual)/L1(assisted)/L2(auto)/L3(full)
default_execution_mode = "mini"
single_decision_lock = true      # LOCK: always true
pipeline_stages = ["intake","plan","execute","verify","deliver"]  # LOCK

[llm]                            # PHASE_B4 §3.2
mini_model = "ollama/llama3.2:3b"
main_model = "ollama/llama3.1:8b"
fallback_model = "gpt-4o-mini"
temperature = 0.3
max_tokens = 2048                # LOCK (V1 기준 B4 §4.1)
streaming_enabled = true

[embedding]                      # PHASE_B4 §3.3
model = "bge-m3"                 # LOCK (V1)
dimension = 1024                 # LOCK — BGE-M3 원본 임베딩 차원 (저장용)
matryoshka_dim = 256             # 검색용 축소 차원 (Matryoshka: 1024→256 프로젝션)

[vector_db]                      # PHASE_B4 §3.4
backend = "chroma"               # LOCK (V1), V2=qdrant
mode = "embedded"
collection_name = "vamos_default"
persist_directory = "${VAMOS_DATA_DIR}/chroma"
similarity_metric = "cosine"

[graph_db]                       # PHASE_B4 §3.5
backend = "json_file"            # LOCK (V1), V2=neo4j
json_path = "${VAMOS_DATA_DIR}/graph/graph.json"
max_hops = 2
scope = "P1"
cache_enabled = true

[storage]                        # PHASE_B4 §3.6 (memory TTL 포함)
backend = "sqlite"
db_path = "${VAMOS_DATA_DIR}/sqlite/vamos.db"
log_format = "jsonl"
log_path = "${VAMOS_DATA_DIR}/logs/events.jsonl"
memory_ttl_L0 = "session_end"   # 최대 30일
memory_ttl_L1 = "90d"
memory_ttl_L2 = "indefinite"    # B4 정본 값 <!-- SOURCE_CONFLICT: B4="indefinite" vs BASE-1.3="영구". 동일 의미, B4 리터럴 채택 -->
memory_ttl_L3 = "policy_based"  # B4 정본 값

[cost]                           # PHASE_B4 §3.7
daily_limit = 1300               # KRW (B4 정본: daily_limit, _krw 접미사 없음)
monthly_limit = 40000            # LOCK: ₩40,000/월
warn_threshold = 70              # % 1단계 경고 (P30-058: 70/85/95 3단계 경보)
escalate_threshold = 85          # % 2단계 심화 경고
block_threshold = 95             # % 3단계 차단
currency = "KRW"

[self_check]                     # PHASE_B4 §3.8a
threshold_p0 = 70                # LOCK
threshold_p1 = 75                # LOCK
threshold_p2 = 80                # LOCK
soft_loop_max = 1                # LOCK: 자동 1회만

[approval]                       # PHASE_B4 §3.8b
timeout_s = 600                  # LOCK: 10분
p2_timeout_s = 300               # LOCK: 5분 (P2 승인)

[mcp]                            # PHASE_B4 §3.9
transport = "streamable_http"    # LOCK
default_timeout_ms = 10000       # B4 정본: 밀리초 단위 (_ms)
max_retries = 3

[rbac]                           # PHASE_B4 §3.10
default_role = "OWNER"           # OWNER/ADMIN/OPERATOR/VIEWER

[logging]                        # PHASE_B4 §3.12
level = "INFO"
format = "json"                  # LOCK: 평문 금지
trace_id_required = true         # LOCK

[semantic_cache]                 # PHASE_B4 §3.15
similarity_threshold = 0.95      # LOCK
ttl_sec = 86400                  # D2.0-06 §4.7.2: 24시간 <!-- SOURCE_CONFLICT: B4="3600" vs D2.0-06="86400". DESIGN 2.0 > PHASE_B 원칙 -->
max_entries = 1000
```

### 산출물 참조
- 디렉토리 구조: `PHASE_B2_PROJECT_STRUCTURE.md`
- 의존성 목록: `PHASE_B3_DEPENDENCIES.md`
- 설정 스펙: `PHASE_B4_CONFIG_SPEC.md`

### 실행 가이드

#### 사용자 직접 작업
1. **개발 환경 준비**: Node.js 18+, Python 3.11+, Rust stable toolchain, pnpm 설치 확인
2. **GitHub 리포지토리 생성**: `vamos` 리포 생성 + clone
3. **Ollama 설치 및 모델 다운로드**: `ollama pull llama3.2:3b` + `ollama pull llama3.1:8b`
4. **AI 생성물 리뷰**: 디렉토리 구조, config.v1.toml LOCK 값, 의존성 버전 검토 후 첫 커밋

#### AI 프롬프트

````text
VAMOS 프로젝트 V0-STEP-1: 프로젝트 스캐폴딩을 진행합니다.

## 작업 목표
Tauri 2.0 + React 18 + Python 3.11 monorepo를 초기화하고,
PHASE_B2 정본 기준 디렉토리 구조를 생성하며,
PHASE_B4 LOCK 값에 따른 config.v1.toml을 작성합니다.

## 1. monorepo 디렉토리 구조 생성 (PHASE_B2 정본)

vamos/
├── src/                    # React 18 + TypeScript
│   ├── components/
│   ├── hooks/
│   ├── stores/
│   ├── types/
│   └── App.tsx
├── src-tauri/              # Rust Tauri 2.0
│   ├── src/
│   │   ├── commands/       # IPC 핸들러
│   │   ├── models/         # serde 구조체
│   │   ├── bridge/          # Python 프로세스 관리 (PHASE_B2 §4.1 정본)
│   │   └── main.rs
│   ├── Cargo.toml
│   └── tauri.conf.json
├── backend/                # Python 3.11+ AI/ML
│   ├── vamos_core/         # 메인 패키지 (PHASE_B2 §5.1 정본)
│   │   ├── orange_core/    # I-Series 모듈
│   │   ├── blue_nodes/     # E-Series 실행
│   │   ├── infra/          # A-Series, 인프라
│   │   ├── agent/          # Agent Teams
│   │   ├── storage/        # B-Series, 메모리
│   │   ├── safety/         # 07 Gate, Guardrails
│   │   ├── schemas/        # Pydantic v2 스키마 (SOT)
│   │   ├── mcp/            # MCP 브릿지
│   │   └── rpc/            # JSON-RPC server
│   ├── tests/
│   └── pyproject.toml
├── shared/types/           # 공유 타입 (codegen)
├── config/
│   ├── config.v1.toml      # 메인 설정 (LOCK)
│   └── .env.example
├── scripts/                # 유틸리티 스크립트
├── docs/
├── .github/workflows/
├── CLAUDE.md
└── README.md

모든 디렉토리에 __init__.py (Python) 또는 mod.rs (Rust) 를 생성하세요.

## 2. 의존성 초기화

### Python (backend/pyproject.toml — poetry)
- pydantic >= 2.0 (v2 필수)
- langgraph
- langchain-core
- langchain-community              <!-- PHASE_B3: Ollama 래퍼 ChatOllama 사용에 필수 -->
- chromadb
- aiosqlite                        <!-- PHASE_B3: async SQLite 접근 필수 -->
- tiktoken
- jsonrpcserver
- structlog
- FlagEmbedding (bge-m3 공식, Matryoshka 256dim 지원) <!-- L-3: BAAI 공식 라이브러리 채택. sentence-transformers도 bge-m3 로드 가능하나 Matryoshka 축소 네이티브 지원 우선 -->

### Rust (src-tauri/Cargo.toml)
- tauri 2.0
- serde + serde_json
- tokio (async runtime)

### Node (package.json — pnpm)
- react 18, react-dom 18
- @tauri-apps/api
- zustand (상태관리)
- typescript

## 3. config/config.v1.toml 생성 — ✅ **V1 확장판 (정본, 17섹션)** (PHASE_B4 §3 정본 LOCK 값)

아래 내용을 그대로 생성하세요. LOCK 표기된 값은 절대 변경 불가.
**설정 키 이름은 PHASE_B4 정본 그대로 사용** (예: daily_limit, default_timeout_ms 등):

```toml
[core]                           # PHASE_B4 §3.1
autonomy_level = "L1"            # LOCK: L0(manual)/L1(assisted)/L2(auto)/L3(full)
default_execution_mode = "mini"
single_decision_lock = true      # LOCK: always true
pipeline_stages = ["intake","plan","execute","verify","deliver"]  # LOCK

[llm]                            # PHASE_B4 §3.2
mini_model = "ollama/llama3.2:3b"
main_model = "ollama/llama3.1:8b"
fallback_model = "gpt-4o-mini"
temperature = 0.3
max_tokens = 2048                # LOCK (V1 기준 B4 §4.1)
streaming_enabled = true

[embedding]                      # PHASE_B4 §3.3
model = "bge-m3"                 # LOCK (V1)
dimension = 1024                 # LOCK — BGE-M3 원본 임베딩 차원 (저장용)
matryoshka_dim = 256             # 검색용 축소 차원 (Matryoshka: 1024→256 프로젝션)

[vector_db]                      # PHASE_B4 §3.4
backend = "chroma"               # LOCK (V1), V2=qdrant
mode = "embedded"
collection_name = "vamos_default"
persist_directory = "${VAMOS_DATA_DIR}/chroma"
similarity_metric = "cosine"

[graph_db]                       # PHASE_B4 §3.5
backend = "json_file"            # LOCK (V1), V2=neo4j
json_path = "${VAMOS_DATA_DIR}/graph/graph.json"
max_hops = 2
scope = "P1"
cache_enabled = true

[storage]                        # PHASE_B4 §3.6 (memory TTL 포함)
backend = "sqlite"
db_path = "${VAMOS_DATA_DIR}/sqlite/vamos.db"
log_format = "jsonl"
log_path = "${VAMOS_DATA_DIR}/logs/events.jsonl"
memory_ttl_L0 = "session_end"   # 최대 30일
memory_ttl_L1 = "90d"
memory_ttl_L2 = "indefinite"    # B4 정본 값 (BASE-1.3="영구", 동일 의미)
memory_ttl_L3 = "policy_based"  # B4 정본 값

[cost]                           # PHASE_B4 §3.7
daily_limit = 1300               # KRW (B4 정본: daily_limit, _krw 접미사 없음)
monthly_limit = 40000            # LOCK: ₩40,000/월
warn_threshold = 70              # % 1단계 경고 (P30-058: 70/85/95 3단계 경보)
escalate_threshold = 85          # % 2단계 심화 경고
block_threshold = 95             # % 3단계 차단
currency = "KRW"

[self_check]                     # PHASE_B4 §3.8a
threshold_p0 = 70                # LOCK
threshold_p1 = 75                # LOCK
threshold_p2 = 80                # LOCK
soft_loop_max = 1                # LOCK: 자동 1회만

[approval]                       # PHASE_B4 §3.8b
timeout_s = 600                  # LOCK: 10분
p2_timeout_s = 300               # LOCK: 5분 (P2 승인)

[mcp]                            # PHASE_B4 §3.9
transport = "streamable_http"    # LOCK
default_timeout_ms = 10000       # B4 정본: 밀리초 단위 (_ms)
max_retries = 3

[rbac]                           # PHASE_B4 §3.10
default_role = "OWNER"           # OWNER/ADMIN/OPERATOR/VIEWER

[logging]                        # PHASE_B4 §3.12
level = "INFO"
format = "json"                  # LOCK: 평문 금지
trace_id_required = true         # LOCK

[semantic_cache]                 # PHASE_B4 §3.15
similarity_threshold = 0.95      # LOCK
ttl_sec = 86400                  # D2.0-06 §4.7.2: 24시간 <!-- SOURCE_CONFLICT: B4="3600" vs D2.0-06="86400". DESIGN 2.0 > PHASE_B 원칙 -->
max_entries = 1000
```

## 4. 기본 파일 생성
- CLAUDE.md: 프로젝트 규칙 + SOT 우선순위 정의
- .gitignore: Python + Rust + Node + .env 패턴
- README.md: 프로젝트 개요

## 5. Schema Seed 파일 생성 (STEP-2 전제조건 — Method B)

> ⚠️ STEP-2에서 AI가 스키마를 정확하게 생성하려면 SOT 필드 정의가 필요합니다.
> **이 단계를 건너뛰면 STEP-2에서 필드명/타입 추측이 발생합니다.**

다음 seed 파일을 D2.1-D1~D8 및 CLAUDE.md 정본에서 추출하여 생성하세요:

```
schemas/seed/
├── decision_schema.json        # DecisionSchema 18필드 (14필수+4선택) — D2.1-D2 §4.1 FREEZE
├── response_envelope.json      # ResponseEnvelope 5필드 — CLAUDE.md §12 LOCK
├── intent_frame.json           # IntentFrame 10필드 — D2.0-02 §7.1
├── evidence_pack.json          # EvidencePack 6필드 — D2.0-02 §7.2
└── registries.json             # EventType 123 + FailureCode 36 + Fallback 23 — D2.1-D2
```

각 JSON 파일 형식:
```json
{
  "schema_name": "DecisionSchema",
  "source_document": "D2.1-D2 §4.1",
  "version": "v3.0.0",
  "freeze_status": "FREEZE",
  "field_count": 18,
  "fields": [
    {"name": "field_name", "type": "str", "required": true, "description": "..."}
  ]
}
```

**⛔ 이 seed 파일이 없으면 STEP-2를 진행할 수 없습니다.**

## 규칙
> **§1.3 R1~R11 공통 규칙 전수 적용** (R1 Python≥3.11, R2 Pydantic v2, R3 no-create, R4 no-delete, R5 LOCK 불변, R6 SOT 준수, R7 의존성 방향, R8 trace_id, R9 에러 노출 금지, R10 비용 LOCK, R11 schema_registry 참조)
- LOCK/FREEZE 값 변경 금지
- Python은 Pydantic v2 구문만 사용 (model_config = ConfigDict(...), class Config: 사용 금지)
- 로깅은 JSON 형식만 허용 (평문 금지)
- 설정 키 이름은 PHASE_B4 정본 그대로 사용

## 참조 SOT 문서
- PHASE_B2_PROJECT_STRUCTURE.md (디렉토리 구조 정본)
- PHASE_B3_DEPENDENCIES.md (의존성 목록 정본)
- PHASE_B4_CONFIG_SPEC.md (설정 스펙 정본)
````

### 단계 완료 검증 (V0-STEP-1 → STEP-2 전환 조건)

| # | 검증 항목 | 확인 방법 | 필수 |
|---|----------|----------|:---:|
| 1 | monorepo 디렉토리 구조 | `src/`, `src-tauri/`, `backend/vamos_core/`, `shared/`, `config/` 존재 확인 | ✅ |
| 2 | Python 의존성 설치 | `cd backend && poetry install` 정상 완료 (pydantic, langgraph, chromadb 등) | ✅ |
| 3 | Rust 의존성 설치 | `cd src-tauri && cargo build` 정상 완료 (tauri, serde, tokio) | ✅ |
| 4 | Node 의존성 설치 | `pnpm install` 정상 완료 (react, @tauri-apps/api, zustand) | ✅ |
| 5 | config.v1.toml 생성 | `config/config.v1.toml` 존재 + 13섹션 구조 + LOCK 값 정확성 (PHASE_B4 §3 대조) | ✅ |
| 6 | Schema Seed 파일 | `schemas/seed/` 하위 5개 JSON 파일 존재 (decision_schema, response_envelope, intent_frame, evidence_pack, registries) | ✅ |
| 7 | 기본 파일 생성 | CLAUDE.md, .gitignore, README.md 존재 + 첫 커밋 완료 | ✅ |
| 8 | Ollama 모델 | `ollama list`에 llama3.2:3b + llama3.1:8b 확인 | ✅ |

> ⛔ 위 필수 항목 전체 통과 전 STEP-2 진입 금지

---

## V0-STEP-2: 스키마 정의 (Day 2-3)

### 작업 내용

1. **25개 Pydantic v2 핵심 모델** → `backend/vamos_core/schemas/contracts.py` <!-- NOTE (XREF-V0-22): V0 서브셋. PHASE_B2 정본은 33개 모델 정의. V0에서 25개 우선 구현 후 V1에서 확장 -->

| # | 스키마 | 필드 수 | 근거 문서 |
|---|--------|---------|----------|
| 1 | IntentFrame | 10 | D2.0-02 §7.1 |
| 2 | EvidencePack | 6 | D2.0-02 §7.2 |
| 3 | DecisionSchema | 18 (FREEZE) | D2.1-D2 §4.1 — 14 required + 4 optional |
| 4 | LogEventSchema | 7 | D2.1-D2 | <!-- M-8 검증완료: 7필드(trace_id,timestamp,level,module,event_type,message,data) PART2 내 일관 -->
| 5 | ResponseEnvelope | 5 (LOCK) | CLAUDE.md §12 |
| 6 | StructuredOutput | 4 | D2.0-02 §7.4 |
| 7 | MemoryRecord | 20 | D2.1-D6 |
| 8 | SourceQoD | 8 | D2.1-D6 |
| 9 | PolicyCheck | 7 | D2.1-D7 |
| 10 | ApprovalSchema | 12 | D2.1-D7 |
| 11 | CostBudget | 9 | D2.1-D7 |
| 12 | DownshiftSchema | 6 | D2.1-D7 |
| 13 | NodeCapabilityProfile | 6 | D2.1-D3 |
| 14 | NodeRequestEnvelope | 12 | D2.1-D3 |
| 15 | NodeResponseEnvelope | 6 | D2.1-D3 |
| 16 | ToolCallRegistry | 7 | D2.1-D3 |
| 17 | MCPBridgeLayer | 7 | D2.1-D3 |
| 18 | ToolRegistryEntry | 8 | D2.1-D4 |
| 19 | BrainAdapterResponse | 7 | D2.1-D4 |
| 20 | WorkflowStage | 4 (LOCK) | D2.1-D5 |
| 21 | WorkflowOutput | 3 (LOCK) | D2.1-D5 |
| 22 | FailureReport | 4 | D2.1-D5 |
| 23 | GuardrailsCheck | 7 | D2.1-D7 |
| 24 | RBACRole | 6 | D2.1-D7 |
| 25 | AutonomyLevelSchema | 7 | D2.1-D7 §4.7 |

2. **레지스트리 정의** → `backend/vamos_core/schemas/registries.py`

| 레지스트리 | 항목 수 | 근거 |
|-----------|---------|------|
| EventTypeRegistry | 123 (oc.*/wf.*/ui.*/mem.*/storage.*/agent.*/sdar.*) | D2.1-D2 SOT |
| FailureCodeRegistry | 36 (UPPER_SNAKE) | D2.1-D2 SOT |
| FallbackRegistry | 23 (FB_UPPER_SNAKE) | D2.1-D2 SOT |
| ToolRegistry | 2 seed entries | D2.1-D4 |
| NodeRegistry | 1 seed entry | D2.1-D3 |

3. **공유 타입 생성 스크립트** → `scripts/generate_types.py`
   - Pydantic → JSON Schema → TypeScript (Zod) 자동 변환

4. **Unified Schema Registry** → `config/schema_registry.toml` <!-- v24 메이커에반 개선안 4 -->
   - 모든 DB(SQLite/Chroma/TimescaleDB/JSONL)의 스키마를 단일 파일에 정의
   - AI 프롬프트에서 해당 STEP이 사용하는 스키마 섹션만 참조하도록 지시 (§1.3.3 컨텍스트 다이어트 연계)
   - Pydantic contracts.py ↔ schema_registry.toml 일관성 검증 스크립트 포함 (`scripts/validate_schema_registry.py`)
   - 구조 예시:
```toml
[sqlite.tables]
sessions = ["session_id:TEXT PK", "created_at:DATETIME", "mode:TEXT"]
modules  = ["module_id:TEXT PK", "series:TEXT", "status:TEXT"]

[chroma.collections]
memory_long = ["doc_id:TEXT", "embedding:VECTOR(1024)", "metadata:JSON"]

[jsonl.files]
trace_log  = ["trace_id:TEXT", "timestamp:ISO8601", "payload:JSON"]
```
   - V1→V2 마이그레이션 시 `[timescaledb]`, `[qdrant]` 섹션 추가하여 스키마 변경 추적
   - LOCK 위반 없음: DB 스택 변경 없이 문서/도구 계층 추가

### 산출물 참조
- 스키마 정의: `D2.1-D1` ~ `D2.1-D8`
- 레지스트리: `D2.1-D2` EventTypeRegistry/FailureCodeRegistry/FallbackRegistry

### 실행 가이드

#### 사용자 직접 작업
1. **스키마 SOT 대조**: AI 생성 모델의 필드 수가 SOT 문서(D2.1-D1~D8)와 정확히 일치하는지 검증
2. **FREEZE/LOCK 확인**: DecisionSchema 18필드(FREEZE), ResponseEnvelope 5필드(LOCK), WorkflowStage 4필드(LOCK), WorkflowOutput 3필드(LOCK)
3. **타입 동기화 확인**: `scripts/generate_types.py` 실행 → `shared/types/` 생성된 TypeScript 파일과 Pydantic 모델 간 일관성 확인

#### AI 프롬프트

````text
VAMOS 프로젝트 V0-STEP-2: 스키마 정의를 진행합니다.

## 작업 목표
25개 Pydantic v2 핵심 모델, 5개 레지스트리, 공유 타입 생성 스크립트를 작성합니다.

## 전제조건 (Method B — seed 파일 확인)

> ⚠️ STEP-1에서 생성한 `schemas/seed/` 파일이 존재하는지 **반드시 확인 후 진행**하세요.
> seed 파일이 없으면 AI가 필드명/타입을 추측하게 되어 SOT 불일치가 발생합니다.

```python
# 전제조건 확인 (STEP-2 시작 전 실행)
import pathlib
seed_dir = pathlib.Path("schemas/seed")
required_seeds = [
    "decision_schema.json",
    "response_envelope.json",
    "intent_frame.json",
    "evidence_pack.json",
    "registries.json",
]
for f in required_seeds:
    assert (seed_dir / f).exists(), f"ERROR: {f} 미존재. STEP-1을 먼저 완료하세요."
print("✅ 모든 seed 파일 확인 완료. STEP-2 진행 가능.")
```

## 1. Pydantic v2 핵심 모델 → backend/vamos_core/schemas/contracts.py

다음 25개 모델을 Pydantic v2로 정의하세요.
반드시 `from pydantic import BaseModel, ConfigDict, Field` 사용.
`class Config:` 사용 금지 — `model_config = ConfigDict(extra="forbid")` 사용.

| # | 스키마 | 필드 수 | 근거 문서 |
|---|--------|---------|----------|
| 1 | IntentFrame | 10 | D2.0-02 §7.1 |
| 2 | EvidencePack | 6 | D2.0-02 §7.2 |
| 3 | DecisionSchema | 18 (FREEZE) | D2.1-D2 §4.1 — 14 required + 4 optional |
| 4 | LogEventSchema | 7 | D2.1-D2 |
| 5 | ResponseEnvelope | 5 (LOCK) | CLAUDE.md §12 |
| 6 | StructuredOutput | 4 | D2.0-02 §7.4 |
| 7 | MemoryRecord | 20 | D2.1-D6 |
| 8 | SourceQoD | 8 | D2.1-D6 |
| 9 | PolicyCheck | 7 | D2.1-D7 |
| 10 | ApprovalSchema | 12 | D2.1-D7 |
| 11 | CostBudget | 9 | D2.1-D7 |
| 12 | DownshiftSchema | 6 | D2.1-D7 |
| 13 | NodeCapabilityProfile | 6 | D2.1-D3 |
| 14 | NodeRequestEnvelope | 12 | D2.1-D3 |
| 15 | NodeResponseEnvelope | 6 | D2.1-D3 |
| 16 | ToolCallRegistry | 7 | D2.1-D3 |
| 17 | MCPBridgeLayer | 7 | D2.1-D3 |
| 18 | ToolRegistryEntry | 8 | D2.1-D4 |
| 19 | BrainAdapterResponse | 7 | D2.1-D4 |
| 20 | WorkflowStage | 4 (LOCK) | D2.1-D5 |
| 21 | WorkflowOutput | 3 (LOCK) | D2.1-D5 |
| 22 | FailureReport | 4 | D2.1-D5 |
| 23 | GuardrailsCheck | 7 | D2.1-D7 |
| 24 | RBACRole | 6 | D2.1-D7 |
| 25 | AutonomyLevelSchema | 7 | D2.1-D7 §4.7 |

FREEZE/LOCK 모델은 필드 추가/삭제가 절대 불가합니다.
각 모델의 필드 정의 시 아래 핵심 필드 참조 테이블을 기반으로 하되, 상세 타입/제약은 근거 문서를 참조하세요.

### 25개 모델 핵심 필드 참조 (SOT 문서 기반)

| # | 모델 | 핵심 필드 (타입 약기) |
|---|------|---------------------|
| 1 | IntentFrame | user_input(str), intent_type(Enum), confidence(float), domain(str), priority(P0-P3), extracted_entities(list), context_refs(list), raw_tokens(int), language(str), timestamp(datetime) |
| 2 | EvidencePack | evidence_id(str), source_type(Enum), content(str), confidence(float), metadata(dict), collected_at(datetime) |
| 3 | DecisionSchema | decision_id(str), intent_frame_id(str), chosen_action(str), priority(P0-P3), risk_level(Enum), gate_results(list[GateResult]), evidence_ids(list), cost_estimate(float), approval_status(Enum), execution_plan(dict), created_at(datetime), updated_at(datetime), locked(bool), lock_reason(str?), **+4 optional** |
| 4 | LogEventSchema | event_type(str), producer(str), when(datetime), payload(dict), severity(Enum), sinks(list), links(dict) |
| 5 | ResponseEnvelope | request_id(str), status(Enum), data(Any), error(Error?), metadata(dict) — **5필드 LOCK** |
| 6 | StructuredOutput | format(Enum), content(str), schema_ref(str?), validated(bool) |
| 7 | MemoryRecord | record_id(str), memory_type(B1-B4), layer(L0-L3), content(str), embedding(list[float]), tags(list), source_session(str), created_at/updated_at(datetime), ttl(int?), access_count(int), last_accessed(datetime), quality_score(float), decay_factor(float), project_id(str?), is_archived(bool), version(int), metadata(dict), relations(list), checksum(str) |
| 8 | SourceQoD | source_id(str), accuracy(float), freshness(float), completeness(float), consistency(float), overall_score(float), evaluated_at(datetime), evaluator(str) |
| 9 | PolicyCheck | check_id(str), policy_name(str), result(bool), severity(Enum), message(str), checked_at(datetime), details(dict) |
| 10 | ApprovalSchema | approval_id(str), decision_id(str), requester(str), approver(str?), status(Enum), priority(P0-P3), reason(str), requested_at(datetime), resolved_at(datetime?), timeout_s(int), auto_approved(bool), metadata(dict) |
| 11 | CostBudget | budget_id(str), daily_limit(int), monthly_limit(int), current_daily/monthly(float), warn_threshold(int), escalate_threshold(int), block_threshold(int), last_updated(datetime) |
| 12 | DownshiftSchema | from_model(str), to_model(str), reason(Enum), cost_saved(float), quality_delta(float), triggered_at(datetime) |
| 13 | NodeCapabilityProfile | node_id(str), node_type(Enum), supported_tools(list), max_concurrency(int), timeout_s(int), metadata(dict) |
| 14 | NodeRequestEnvelope | request_id(str), source_node(str), target_node(str), method(str), params(dict), priority(P0-P3), timeout_s(int), trace_id(str), timestamp(datetime), retry_count(int), idempotency_key(str), metadata(dict) |
| 15 | NodeResponseEnvelope | request_id(str), status(Enum), result(Any), error(Error?), duration_ms(int), metadata(dict) |
| 16 | ToolCallRegistry | tool_id(str), tool_name(str), category(Enum), handler(str), timeout_s(int), requires_approval(bool), metadata(dict) |
| 17 | MCPBridgeLayer | bridge_id(str), protocol_version(str), transport(Enum), endpoint(str), auth_method(str), timeout_s(int), metadata(dict) |
| 18 | ToolRegistryEntry | tool_id(str), name(str), description(str), category(Enum), input_schema(dict), output_schema(dict), version(str), enabled(bool) |
| 19 | BrainAdapterResponse | adapter_id(str), model_name(str), response_text(str), tokens_used(int), latency_ms(int), cost(float), metadata(dict) |
| 20 | WorkflowStage | stage_name(str), status(Enum), started_at(datetime?), completed_at(datetime?) — **4필드 LOCK** |
| 21 | WorkflowOutput | output_type(str), content(Any), metadata(dict) — **3필드 LOCK** |
| 22 | FailureReport | failure_code(str), message(str), context(dict), occurred_at(datetime) |
| 23 | GuardrailsCheck | check_id(str), layer(L1-L4), check_type(Enum), result(bool), score(float?), message(str), checked_at(datetime) |
| 24 | RBACRole | role_name(Enum), permissions(list), description(str), is_default(bool), created_at(datetime), metadata(dict) |
| 25 | AutonomyLevelSchema | level(Enum), name(str), description(str), auto_actions(list), requires_approval(list), max_risk(Enum), metadata(dict) |

## 2. 레지스트리 정의 → backend/vamos_core/schemas/registries.py

| 레지스트리 | 항목 수 | 근거 |
|-----------|---------|------|
| EventTypeRegistry | 123 (oc.*/wf.*/ui.*/mem.*/storage.*/agent.*/sdar.*) | D2.1-D2 SOT |
| FailureCodeRegistry | 36 (UPPER_SNAKE) | D2.1-D2 SOT |
| FallbackRegistry | 23 (FB_UPPER_SNAKE) | D2.1-D2 SOT |
| ToolRegistry | 2 seed entries | D2.1-D4 |
| NodeRegistry | 1 seed entry | D2.1-D3 |

각 레지스트리를 Enum 또는 상수 딕셔너리로 정의하세요.
네이밍 컨벤션은 근거 문서 정본을 그대로 따릅니다.

## 3. 공유 타입 생성 스크립트 → scripts/generate_types.py

Pydantic 모델 → JSON Schema → TypeScript (Zod) 자동 변환 스크립트를 작성하세요.
- contracts.py의 모든 모델을 JSON Schema로 내보내기
- JSON Schema → Zod 스키마 변환 (ts-to-zod 또는 직접 변환)
- 출력: shared/types/ 디렉토리

## 규칙
> **§1.3 R1~R11 공통 규칙 전수 적용**
- 모든 모델은 model_config = ConfigDict(extra="forbid") 적용
- from pydantic import BaseModel, ConfigDict, Field 필수
- DecisionSchema: 18필드 (14 required + 4 optional) — FREEZE
- ResponseEnvelope: 5필드 — LOCK
- WorkflowStage: 4필드, WorkflowOutput: 3필드 — LOCK
- 레지스트리 네이밍: EventType은 oc.* 네임스페이스, FailureCode는 UPPER_SNAKE, Fallback은 FB_UPPER_SNAKE

## FREEZE/LOCK 스키마 인라인 참조 (Method C)

> 아래는 FREEZE/LOCK 스키마의 필드 정의 스냅샷입니다. **정본은 반드시 근거 문서 및 seed 파일을 참조하세요.**
> seed 파일(Method B)과 교차 검증하여 불일치 발생 시 근거 문서(SOT)를 우선 채택합니다.

<!-- FREEZE_SNAPSHOT: D2.1-D2:DecisionSchema:v3.0.0:18fields:2026-03-03 -->
### DecisionSchema (18필드, FREEZE — D2.1-D2 §4.1)
- **14 required + 4 optional** (총 18필드)
- 필드 정의 정본: `schemas/seed/decision_schema.json` + D2.1-D2 §4.1
- `model_config = ConfigDict(extra="forbid")` 필수

<!-- FREEZE_SNAPSHOT: CLAUDE.md:ResponseEnvelope:v1.0:5fields:2026-03-03 -->
### ResponseEnvelope (5필드, LOCK — CLAUDE.md §12)
- 필드 정의 정본: `schemas/seed/response_envelope.json` + CLAUDE.md §12
- `model_config = ConfigDict(extra="forbid")` 필수

<!-- FREEZE_SNAPSHOT: D2.0-02:IntentFrame:v1.0:10fields:2026-03-03 -->
### IntentFrame (10필드 — D2.0-02 §7.1)
- 필드 정의 정본: `schemas/seed/intent_frame.json` + D2.0-02 §7.1

<!-- FREEZE_SNAPSHOT: D2.0-02:EvidencePack:v1.0:6fields:2026-03-03 -->
### EvidencePack (6필드 — D2.0-02 §7.2)
- 필드 정의 정본: `schemas/seed/evidence_pack.json` + D2.0-02 §7.2

> **⚠️ 인라인 스냅샷 관리**: 근거 문서 버전 변경 시 `FREEZE_SNAPSHOT` 주석의 버전·날짜를 함께 갱신하세요.

## 참조 SOT 문서 (MANDATORY — Method A)

> ⚠️ AI 세션에서 아래 문서를 **@file 또는 직접 첨부하는 것을 강력 권장**합니다.
> 첨부하지 않아도 Method B seed로 최소 보장되지만, STEP-1 대상 25개 스키마(D2.1 전체 42개 중 V0 서브셋) 정확도를 위해 첨부를 권장합니다.

- **D2.1-D1 ~ D2.1-D8** (스키마 정의 정본) — @file 첨부 우선 대상
- **D2.1-D2 §4.1** (DecisionSchema 18필드 FREEZE 정본)
- **D2.1-D2 §6** (EventTypeRegistry 123 / FailureCodeRegistry 36 / FallbackRegistry 23)
- **D2.0-02 §7** (IntentFrame 10, EvidencePack 6, StructuredOutput 4)
- **CLAUDE.md §12** (ResponseEnvelope 5필드 LOCK)
- **schemas/seed/*.json** (Method B seed — 필드 정의 교차 검증용)
````

### 단계 완료 검증 (V0-STEP-2 → STEP-3 전환 조건)

| # | 검증 항목 | 확인 방법 | 필수 |
|---|----------|----------|:---:|
| 1 | 25개 Pydantic v2 모델 | `contracts.py`에 25개 클래스 정의 + `model_config = ConfigDict(extra="forbid")` 적용 | ✅ |
| 2 | DecisionSchema 18필드 (FREEZE) | `len(DecisionSchema.model_fields) == 18` (14 required + 4 optional) | ✅ |
| 3 | ResponseEnvelope 5필드 (LOCK) | `len(ResponseEnvelope.model_fields) == 5` | ✅ |
| 4 | WorkflowStage 4필드 (LOCK) | `len(WorkflowStage.model_fields) == 4` | ✅ |
| 5 | WorkflowOutput 3필드 (LOCK) | `len(WorkflowOutput.model_fields) == 3` | ✅ |
| 6 | 5개 레지스트리 정의 | EventType 123 + FailureCode 36 + Fallback 23 + Tool 2 seed + Node 1 seed | ✅ |
| 7 | extra="forbid" 동작 | 추가 필드 입력 시 ValidationError 발생 확인 | ✅ |
| 8 | Seed 파일 교차 검증 | `schemas/seed/*.json` 필드 정의와 contracts.py 모델 간 필드명/타입 일치 확인 | ✅ |
| 9 | 타입 생성 스크립트 | `python scripts/generate_types.py` 실행 → `shared/types/` TypeScript 파일 생성 | ✅ |

> ⛔ 위 필수 항목 전체 통과 전 STEP-3 진입 금지

---

## V0-STEP-3: IPC 통신 레이어 (Day 3-5)

### 작업 내용

1. **Rust ↔ Python 통신** (JSON-RPC stdin/stdout)
```
React UI ←[Tauri IPC]→ Rust Backend ←[JSON-RPC stdin/stdout]→ Python AI/ML
```

2. **Python 측 JSON-RPC 서버** → `backend/vamos_core/rpc/server.py`
   - 13개 메서드 스텁 생성:
```python
# 핵심 메서드
langgraph.workflow.run
langgraph.stage.execute
langgraph.decision.create
langgraph.node.dispatch
langgraph.verify.run_chain
embedding.encode
embedding.store
llm.generate
llm.record_invoke
llm.rate_limit.get
mcp.bridge.init
mcp.bridge.health
mcp.tools.discover
```

3. **Rust 측 Python 프로세스 관리** → `src-tauri/src/bridge/python_manager.rs` <!-- PHASE_B2 §4.1: bridge/ 정본 -->
   - Python 프로세스 스폰, 헬스체크, 재시작, stdin/stdout 파이프

4. **Tauri IPC 핸들러 스텁** → `src-tauri/src/commands/`
   - V0용 핵심 커맨드 5개:
     - `vamos:decision:create`
     - `vamos:workflow:start`
     - `vamos:ui:log_stream`
     - `vamos:ui:config_get`
     - `vamos:ui:config_set`

### 산출물 참조
- API 계약: `PHASE_B1_API_CONTRACT.md`
- 통신 프로토콜: `D2.0-04` §5, `D2.0-01` §2

### 실행 가이드

#### 사용자 직접 작업
1. **JSON-RPC 통신 수동 테스트**: Rust에서 Python 프로세스 스폰 후 echo 요청/응답 확인
2. **Tauri IPC 테스트**: React 프론트에서 `invoke('vamos:decision:create', ...)` 호출하여 응답 수신 확인
3. **프로세스 관리 검증**: Python 프로세스 강제 종료 후 자동 재시작 동작 확인

#### AI 프롬프트

````text
VAMOS 프로젝트 V0-STEP-3: IPC 통신 레이어를 구현합니다.

## 작업 목표
React ↔ Rust ↔ Python 3계층 통신 구조를 구현합니다.

아키텍처:
React UI ←[Tauri IPC]→ Rust Backend ←[JSON-RPC stdin/stdout]→ Python AI/ML

## 1. Python JSON-RPC 서버 → backend/vamos_core/rpc/server.py

jsonrpcserver 라이브러리를 사용하여 stdin/stdout 기반 JSON-RPC 2.0 서버를 구현하세요.
다음 13개 메서드 스텁을 생성합니다 (V0에서는 기본 응답 반환):

```python
# 핵심 메서드 목록
langgraph.workflow.run        # 워크플로우 실행
langgraph.stage.execute       # 스테이지 개별 실행
langgraph.decision.create     # Decision 생성
langgraph.node.dispatch       # 노드 디스패치
langgraph.verify.run_chain    # 검증 체인 실행
embedding.encode              # 임베딩 인코딩
embedding.store               # 임베딩 저장
llm.generate                  # LLM 텍스트 생성
llm.record_invoke             # LLM 호출 기록
llm.rate_limit.get            # 레이트 리밋 조회
mcp.bridge.init               # MCP 브릿지 초기화
mcp.bridge.health             # MCP 헬스체크
mcp.tools.discover            # MCP 도구 탐색
```

각 메서드는 JSON-RPC 2.0 스펙 준수하고, 파라미터 검증 후 stub 응답을 반환합니다.

## 2. Rust Python 프로세스 관리 → src-tauri/src/bridge/python_manager.rs

- Python 프로세스 스폰: stdin/stdout 파이프 연결, 환경변수 전달
- 헬스체크: 주기적 ping 요청 → pong 응답 확인
- 비정상 종료 감지 + 자동 재시작 (최대 3회) — config.v1.toml `[core].ipc_max_restart=3` <!-- FIX-027: [ipc] 섹션은 B4에 미정의. [core] 하위로 이동 -->
- JSON-RPC 요청/응답 직렬화: serde_json 사용
- 요청 타임아웃: 30초 기본 — config.v1.toml `[core].ipc_timeout_s=30` <!-- FIX-027: [ipc]→[core] 하위. 구현 시 [ipc] 별도 섹션 신설 가능 -->

## 3. Tauri IPC 핸들러 → src-tauri/src/commands/

V0용 핵심 커맨드 5개를 `#[tauri::command]` 매크로로 구현:

| 커맨드 | 기능 | Python RPC 매핑 |
|--------|------|----------------|
| vamos:decision:create | Decision 생성 요청 | langgraph.decision.create |
| vamos:workflow:start | 워크플로우 시작 | langgraph.workflow.run |
| vamos:ui:log_stream | 로그 스트림 구독 | (Tauri 이벤트) |
| vamos:ui:config_get | 설정 읽기 | (Rust 직접 처리) |
| vamos:ui:config_set | 설정 쓰기 | (Rust 직접 처리) |

각 커맨드는 내부적으로 Python JSON-RPC를 호출하거나 Rust에서 직접 처리합니다.

**`#[tauri::command]` 구현 패턴** (M-4):
```rust
// 패턴 1: Python JSON-RPC 호출 커맨드
#[tauri::command]
async fn decision_create(
    state: tauri::State<'_, AppState>,
    input: serde_json::Value,
) -> Result<serde_json::Value, String> {
    state.python_bridge
        .call_jsonrpc("langgraph.decision.create", input)
        .await
        .map_err(|e| e.to_string())
}

// 패턴 2: Rust 직접 처리 커맨드
#[tauri::command]
async fn config_get(
    state: tauri::State<'_, AppState>,
    key: String,
) -> Result<serde_json::Value, String> {
    state.config.read().get(&key).cloned()
        .ok_or_else(|| format!("config key not found: {key}"))
}
```
> 모든 커맨드는 `Result<T, String>` 반환. Tauri 2.0에서는 `#[tauri::command]` 매크로가 자동으로 IPC 직렬화를 처리합니다.

## 규칙
> **§1.3 R1~R11 공통 규칙 전수 적용**
- JSON-RPC 2.0 스펙 엄격 준수 (id, jsonrpc, method, params)
- 통신은 stdin/stdout 파이프만 사용 (TCP/HTTP 아님)
- **stderr는 로그 전용** — Python 프로세스의 structlog 출력은 stderr로 분리하여 JSON-RPC 메시지와 혼선 방지 (M-5)
- 에러 응답은 JSON-RPC error object 형식 (code + message + data)
- Python 서버 시작 시 ready 메시지를 stdout으로 출력하여 Rust 측이 감지
- Rust 측은 stderr를 별도 스레드로 읽어 로그 파일에 기록 (stdout과 혼합 금지)

## 참조 SOT 문서
- PHASE_B1_API_CONTRACT.md (API 계약 정본)
- D2.0-04 §5 (통신 프로토콜)
- D2.0-01 §2 (아키텍처 정의)
````

### 단계 완료 검증 (V0-STEP-3 → STEP-4 전환 조건)

| # | 검증 항목 | 확인 방법 | 필수 |
|---|----------|----------|:---:|
| 1 | Python JSON-RPC 서버 기동 | `python -m vamos_core.rpc.server` 실행 → stdout에 ready 메시지 출력 | ✅ |
| 2 | 13개 RPC 메서드 스텁 | 각 메서드 호출 → JSON-RPC 2.0 정상 응답 반환 (에러 아님) | ✅ |
| 3 | 미존재 메서드 에러 | 존재하지 않는 메서드 호출 → JSON-RPC error object (code + message) 반환 | ✅ |
| 4 | Rust Python 프로세스 스폰 | `cargo test` — Python 프로세스 스폰 + stdin/stdout 파이프 연결 확인 | ✅ |
| 5 | 프로세스 헬스체크 | ping 요청 → pong 응답 주기적 확인 동작 | ✅ |
| 6 | 프로세스 자동 재시작 | Python 프로세스 강제 종료 후 자동 재시작 (최대 3회) 동작 | ✅ |
| 7 | Tauri IPC 5개 커맨드 | React에서 `invoke('vamos:decision:create', ...)` 등 5개 커맨드 호출 → 응답 수신 | ✅ |
| 8 | stderr 로그 분리 | Python structlog 출력이 stderr로 분리되어 JSON-RPC stdout과 혼선 없음 | ✅ |

> ⛔ 위 필수 항목 전체 통과 전 STEP-4 진입 금지

---

## V0-STEP-4: ORANGE CORE 최소 파이프라인 (Day 5-8)

### 작업 내용

1. **I-1 Intent Detector** (최소 구현)
   - 사용자 입력 → IntentFrame 생성
   - 내부 상태: I1_S0_RAW → I1_S1_PARSING → I1_S3_READY → I1_S4_EMITTED <!-- S2 스킵은 정상: D2.0-02 §7.5 정본에서 S2=AMBIGUOUS(I1_S2_AMBIGUOUS)은 V1+ 전용 -->
   - Mini LLM (llama3.2:3b) 으로 intent 파싱

2. **I-2 Context Builder** (스텁)
   - IntentFrame → EvidencePack 생성 (V0에서는 빈 EvidencePack)

3. **I-5 Condition & Decision Engine** (최소 Gate)
   - PolicyGate: 기본 allow (규칙 기반 deny 목록)
   - CostGate: 80%/100% 체크
   - ApprovalGate: P2 감지 → hold
   - EvidenceGate: 스텁 (항상 sufficient)
   - 결과 → Decision (locked=true)

4. **I-8 Policy Engine** (deny 로직 stub)
   - Non-goal 목록 체크 → deny
   - 비용 상한 체크 → downshift

5. **I-9 Cost Manager** (기본 추적 stub)
   - 토큰 사용량 카운팅 (tiktoken)
   - JSONL 로그 기록

6. **I-19 Approval Manager** (기본 자동 승인 stub)
   - P0/P1 → auto-approve, P2 → hold
   - 타임아웃 10분 (V1에서 본격 구현)

7. **I-20 Failure/Fallback Manager** (stub)
   - FailureReport 수신 → FailureCodeRegistry 매핑
   - V0에서는 로그만 기록하고 기본 에러 메시지 반환

8. **LangGraph StateGraph** (최소 파이프라인)
```python
# V0 최소 파이프라인
from langgraph.graph import StateGraph, START, END
from vamos_core.schemas.contracts import VamosState  # Pydantic v2 상태 모델

graph = StateGraph(VamosState)
graph.add_node("intake", intake_node)      # I-1
graph.add_node("plan", plan_node)          # I-2 + I-5
graph.add_node("execute", execute_node)    # Mini/Main LLM 직접 호출
graph.add_node("verify", verify_node)      # 스텁
graph.add_node("deliver", deliver_node)    # ResponseEnvelope 생성
graph.add_edge(START, "intake")
graph.add_edge("intake", "plan")
graph.add_edge("plan", "execute")
graph.add_edge("execute", "verify")
graph.add_edge("verify", "deliver")
graph.add_edge("deliver", END)
```

> V0 활성 모듈은 I-1, I-2, I-3, I-5, I-19 (5개)이며, I-8/I-9/I-20은 stub 수준. "I-1~I-5"로 표기하지 않음 (I-4 미포함).

### 산출물 참조
- I-모듈 상세: `D2.0-02` §7 (I-1=§7.1~10, I-2=§7.11~20, I-5=§7.41~50)
- 상태 머신: `D2.0-02` §2.2
- Gate 정의: `D2.0-02` §8
- LangGraph: `D2.0-05` §4~7

### 실행 가이드

#### 사용자 직접 작업
1. **Ollama 동작 확인**: `ollama run llama3.2:3b "hello"` → 응답 정상 수신 확인
2. **E2E 수동 테스트**: 사용자 입력 → IntentFrame → Decision → ResponseEnvelope 전체 흐름을 직접 실행하여 JSON 출력 확인
3. **Gate 동작 검증**: CostGate 80%/100% 시나리오를 수동으로 트리거하여 deny/downshift 동작 확인
4. **상태 머신 검증**: I-1의 상태 전이(I1_S0_RAW → I1_S1_PARSING → I1_S3_READY → I1_S4_EMITTED)가 로그에 올바르게 기록되는지 확인

#### AI 프롬프트

````text
VAMOS 프로젝트 V0-STEP-4: ORANGE CORE 최소 파이프라인을 구현합니다.

## 작업 목표
I-1, I-2, I-5 핵심 모듈과 I-8/I-9 stub, I-19 Approval stub, I-20 Failure/Fallback stub을 구현하고,
LangGraph StateGraph 기반 5-Phase 최소 파이프라인을 완성합니다.

## 1. I-1 Intent Detector → backend/vamos_core/orange_core/i1_intent_detector.py

최소 구현:
- 사용자 텍스트 입력 → IntentFrame(contracts.py) 생성
- Mini LLM (ollama/llama3.2:3b, config mini_model) 호출하여 intent 파싱
- 내부 상태 머신: I1_S0_RAW → I1_S1_PARSING → I1_S3_READY → I1_S4_EMITTED
- 상태 전이마다 LogEventSchema로 로그 기록
- 파싱 실패 시 FailureReport 생성 + fallback intent="unknown" 반환

## 2. I-2 Context Builder → backend/vamos_core/orange_core/i2_context_builder.py

스텁 구현:
- IntentFrame 입력 → EvidencePack 출력
- V0에서는 빈 EvidencePack 반환 (sources=[], confidence=0.0)
- 인터페이스만 정의하여 V1에서 RAG 파이프라인 연결 가능하도록 설계

## 3. I-5 Condition & Decision Engine → backend/vamos_core/orange_core/i5_decision_engine.py

최소 4-Gate 구현 (V0), V1에서 5-Gate로 확장:

**[plan 노드 — I-5 Decision Engine 내부 4-Gate]**
- PolicyGate: I-8 stub 호출 → 기본 allow, deny 목록 매칭 시 deny
- CostGate: I-9 stub 호출 → 70% warn, 85% escalate, 95% block (config.v1.toml cost 섹션, P30-058 3단계)
- ApprovalGate: priority level 체크 → P2 감지 시 hold 반환
- EvidenceGate: 스텁 → 항상 sufficient 반환
- → 4-Gate 결과를 종합하여 DecisionSchema 생성 (locked=true)

**[verify 노드 — SelfCheckGate (5번째 Gate, 별도 파이프라인 노드)]**
- **SelfCheckGate (M-14)**: V0에서는 스텁 (항상 pass). V1에서 I-6 Self-check 엔진과 연동
- 파이프라인 위치: **verify 노드** (execute 다음, deliver 이전) — S5(Execute)→verify(SelfCheck)→S6(Deliver)

- 전체 Gate 논리 순서: Policy → Approval → Cost → Evidence (plan 노드) → **SelfCheck** (verify 노드) (CLAUDE.md §7.2 정본 + M-14 보강)

## 4. I-8 Policy Engine (stub) → backend/vamos_core/orange_core/i8_policy_engine.py

- Non-goal 목록 하드코딩 (예: "주식 매매 실행", "개인정보 수집")
- 입력 intent가 non-goal 매칭 시 PolicyCheck(result="deny") 반환
- 비용 상한 초과 시 PolicyCheck(result="downshift") 반환
- 그 외 PolicyCheck(result="allow") 반환

## 5. I-9 Cost Manager (stub) → backend/vamos_core/orange_core/i9_cost_manager.py

- tiktoken으로 토큰 수 카운팅
- JSONL 파일에 사용 기록 append (날짜, 모델, 토큰수, 추정비용)
- get_daily_usage() → 오늘 사용량 합산 반환
- get_monthly_usage() → 이번 달 사용량 합산 반환
- config.v1.toml의 daily_limit, monthly_limit와 비교 <!-- B4 정본: _krw 접미사 없음 -->

## 6. LangGraph StateGraph → backend/vamos_core/orange_core/pipeline.py

```python
from langgraph.graph import StateGraph, START, END

# VamosState: TypedDict 정의 (D2.0-02 §2.2 상태 머신 연동)
# - trace_id: str                              # M-26: 요청 추적 ID (UUID v4, 로깅 필수)
# - user_input: str
# - intent_frame: IntentFrame | None
# - evidence_pack: EvidencePack | None
# - decision: DecisionSchema | None
# - llm_response: str | None
# - response_envelope: ResponseEnvelope | None
# - pipeline_state: str                        # S0_RECEIVED~S8_DONE (9-State, §2.2 LOCK)

graph = StateGraph(VamosState)
graph.add_node("intake", intake_node)      # I-1 Intent Detector
graph.add_node("plan", plan_node)          # I-2 Context Builder + I-5 Decision
graph.add_node("execute", execute_node)    # Ollama LLM 직접 호출
graph.add_node("verify", verify_node)      # SelfCheckGate 위치 (M-14): V0=스텁(pass), V1=I-6 연동
graph.add_node("deliver", deliver_node)    # ResponseEnvelope 생성
graph.add_edge("intake", "plan")
graph.add_edge("plan", "execute")
graph.add_edge("execute", "verify")        # S5(Execute) → SelfCheck(verify) → S6(Deliver)
graph.add_edge("verify", "deliver")
graph.add_edge(START, "intake")    # LangGraph 0.2+: START/END 상수 사용
graph.add_edge("deliver", END)
app = graph.compile()
```

## 7. I-19 Approval Manager (stub) → backend/vamos_core/orange_core/i19_approval_manager.py

- P2 이상 Decision에 대해 승인 요청 생성 (ApprovalSchema)
- V0에서는 자동 승인 (auto_approve=true)
- 타임아웃: 600초 (config.v1.toml approval.timeout_s) <!-- B4 §3.8b: [approval] 섹션 -->

## 8. I-20 Failure/Fallback Manager (stub) → backend/vamos_core/orange_core/i20_failure_manager.py

- FailureReport 수신 → FailureCodeRegistry 매핑
- FallbackRegistry에서 대응 전략 조회 → 로그 기록
- V0에서는 로그만 기록하고 기본 에러 메시지 반환

## 규칙
> **§1.3 R1~R11 공통 규칙 전수 적용**
- 모든 모듈은 async def로 작성 (LangGraph 호환)
- 상태 전이마다 LogEventSchema 기반 structlog 로그 기록 (JSON 형식)
- contracts.py의 Pydantic 모델을 반드시 사용 (raw dict 금지)
- Ollama 호출은 langchain-community의 ChatOllama 사용
- 에러 시 FailureReport 생성 후 I-20으로 전달
- config 값은 config.v1.toml에서 로드 (하드코딩 금지) — config_loader.py는 STEP-5에서 본격 구현하므로, STEP-4에서는 tomllib 직접 로드 또는 STEP-5 config_loader를 먼저 최소 구현. 로딩 순서는 TOML→ENV→CLI 3단계 (STEP-5 상세 참조, M-6)
- **보안**: IPC Bridge 구현 시 §6.5.1 AI 코드 생성 보안 체크리스트 7개 항목 준수 필수. 특히 trace_id 위조 방지(#3) + 입력 검증(#1) 우선 적용 <!-- v24 메이커에반 개선안 3 -->
- **LangGraph 사용 범위**: LangGraph는 워크플로우 오케스트레이션(StateGraph 정의, 노드 간 전이)에만 사용. 개별 모듈(I-1~I-25) 내부 로직은 단순한 함수 호출/조건문으로 구현. LangGraph 노드 안에서 또 다른 StateGraph를 중첩하지 않는다 (에반 #01 기반) <!-- v24 메이커에반 개선안 5 -->

## 참조 SOT 문서
- D2.0-02 §7.1~7.5 (I-모듈 상세 설계)
- D2.0-02 §8 (Gate 정의)
- D2.0-02 §2.2 (상태 머신)
- D2.0-05 §4~7 (LangGraph 파이프라인)
- D2.0-07 §1~6 (Gate 룰)
````

### 단계 완료 검증 (V0-STEP-4 → STEP-5 전환 조건)

| # | 검증 항목 | 확인 방법 | 필수 |
|---|----------|----------|:---:|
| 1 | IntentFrame 생성 | 텍스트 입력 → IntentFrame JSON 10필드 출력 확인 | ✅ |
| 2 | I-1 상태 전이 | 로그에 I1_S0_RAW → I1_S1_PARSING → I1_S3_READY → I1_S4_EMITTED 기록 확인 | ✅ |
| 3 | I-2 Context Builder | IntentFrame 입력 → EvidencePack 출력 (V0: 빈 EvidencePack) | ✅ |
| 4 | PolicyGate deny | non-goal 입력 → PolicyCheck(result="deny") 반환 확인 | ✅ |
| 5 | CostGate 80%/100% | 사용량 80% → warn, 100% → block 시나리오 동작 확인 | ✅ |
| 6 | ApprovalGate P2 hold | P0/P1 → auto-approve, P2 → hold 동작 확인 | ✅ |
| 7 | Decision locked=true | DecisionSchema 생성 후 `locked == True` 확인 | ✅ |
| 8 | LangGraph 5-Phase | intake→plan→execute→verify→deliver 전체 흐름 실행 → ResponseEnvelope 반환 | ✅ |
| 9 | ResponseEnvelope 5필드 | 파이프라인 최종 출력이 ResponseEnvelope 5필드 형식 확인 | ✅ |
| 10 | I-19 Approval stub | ApprovalSchema 생성 + auto_approve 동작 확인 | ✅ |
| 11 | I-20 Failure/Fallback stub | 잘못된 입력 시 FailureReport 생성 + 기본 에러 메시지 반환 | ✅ |
| 12 | Ollama LLM 호출 | ChatOllama(llama3.2:3b) 정상 응답 확인 | ✅ |
| 13 | EvidenceGate stub | EvidenceGate 스텁 동작 (항상 sufficient 반환) 확인 | ✅ |

> ⛔ 위 필수 항목 전체 통과 전 STEP-5 진입 금지

---

## V0-STEP-5: 기본 저장소 + 로깅 (Day 8-9)

### 작업 내용
1. **L0 Session Memory** (SQLite)
   - MemoryRecord 저장 (scope=L0, TTL=session_end, 기본 7일/최대 30일 — CLAUDE.md §15 정본) <!-- RESOLVED: CLAUDE.md §15="7일(최대30일)" 기준 적용. D2.0-06도 Phase 1에서 "최대 30일"로 수정 완료. SC 해소. -->
2. **JSONL 구조화 로깅**
   - LogEventSchema 기반 로그 기록
   - trace_id 포함
3. **기본 config 로더**
   - config.v1.toml → Pydantic ConfigModel

### 산출물 참조
- 메모리 계층: `D2.0-06` §2.1 <!-- SOURCE_CONFLICT: D2.0-06 §2=4계층(L0~L3) vs S7D=5계층(+L4). 4계층 LOCK 채택. L4 Archive는 V2+ 확장 옵션 -->
- 로깅: `D2.0-04` §9

### 실행 가이드

#### 사용자 직접 작업
1. **SQLite DB 파일 확인**: 파이프라인 실행 후 `data/vamos.db`에 MemoryRecord 테이블이 생성되고 레코드가 정상 저장되는지 확인
2. **JSONL 로그 검증**: `logs/` 디렉토리의 `.jsonl` 파일을 열어 trace_id가 일관성 있게 기록되고 JSON 파싱이 정상인지 확인
3. **config 로더 검증**: config.v1.toml 의 LOCK 값이 Pydantic ConfigModel로 정확히 로드되는지 확인 (특히 cost, safety, embedding 섹션)

#### AI 프롬프트

````text
VAMOS 프로젝트 V0-STEP-5: 기본 저장소 + 로깅을 구현합니다.

## 작업 목표
L0 Session Memory (SQLite), JSONL 구조화 로깅, config.v1.toml 로더를 구현합니다.

## 1. L0 Session Memory → backend/vamos_core/storage/memory_store.py

SQLite 기반 L0 세션 메모리:
- MemoryRecord(contracts.py) 스키마 기반 테이블 생성
- scope="L0", TTL=session_end (최대 30일 — CLAUDE.md §15 정본)
- **session_end 정의 (M-30)**: (1) 사용자가 명시적으로 세션을 종료한 시점, (2) 마지막 활동 후 비활성 타임아웃(config.v1.toml `storage.memory_ttl_L0` 참조), (3) 최대 보존 기한 30일 초과 시 강제 만료. `expires_at = min(session_close_time, created_at + 30days)`.
- CRUD 메서드: create, read_by_id, read_by_session, update, delete
- 세션 종료 시 자동 정리 (TTL 만료 레코드 삭제)
- aiosqlite 사용 (async 호환)

테이블 스키마:
```sql
CREATE TABLE IF NOT EXISTS memory_records (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    scope TEXT DEFAULT 'L0',
    content TEXT NOT NULL,
    embedding BLOB,
    metadata TEXT,  -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    activation_state TEXT DEFAULT 'active'
);
CREATE INDEX idx_session ON memory_records(session_id);
CREATE INDEX idx_scope ON memory_records(scope);
CREATE INDEX idx_expires ON memory_records(expires_at);
```

## 2. JSONL 구조화 로깅 → backend/vamos_core/infra/logger.py

LogEventSchema(contracts.py) 기반 구조화 로깅:
- structlog 라이브러리 사용
- 모든 로그는 JSON 형식 (평문 금지 — LOCK)
- **정본 필드 (D2.1-D2 §4.2)**: event_type, producer, when, payload, severity + sinks(opt), links(opt) — 7필드
- **structlog 출력 매핑**: 아래 매핑에 따라 structlog 필드를 정본 필드로 변환하여 저장

  | structlog 출력 필드 | D2.1-D2 정본 필드 | 비고 |
  |---|---|---|
  | event_type | event_type | 동일 |
  | module | producer | 모듈명 → 생산자 |
  | timestamp | when | ISO 8601 |
  | data | payload | 페이로드 |
  | level | severity | 로그 레벨 → 심각도 |
  | trace_id | links | 요청 추적 ID (UUID v4) |
  | message | payload.message | 페이로드 하위 필드 |

- trace_id는 요청 단위로 생성 (UUID v4), 모든 로그에 필수 포함 (LOCK)
- 로그 파일: logs/vamos_{date}.jsonl (일별 로테이션)
- 콘솔 출력도 JSON 형식

설정 초기화:
```python
import logging
import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)
```

## 3. Config 로더 → backend/vamos_core/infra/config_loader.py

config.v1.toml → Pydantic ConfigModel 변환:
- tomllib (Python 3.11 내장) 사용하여 TOML 파싱
- 전체 config를 Pydantic BaseModel로 검증
- LOCK/FREEZE 값 변경 시 ValidationError 발생하도록 validator 추가
- **3단계 로딩 순서 (M-6)**: ① TOML 파일 → ② 환경변수 오버라이드 (`VAMOS_{SECTION}_{KEY}`) → ③ CLI 인자 (있을 경우). 우선순위: CLI > ENV > TOML. 단, LOCK 값은 어떤 단계에서도 변경 불가.
- 싱글톤 패턴: get_config() → 캐시된 ConfigModel 반환

```python
from pydantic import BaseModel, ConfigDict

class VamosConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    core: CoreConfig               # PHASE_B4 §3.1 — autonomy_level, pipeline_stages 등
    llm: LLMConfig                 # PHASE_B4 §3.2
    embedding: EmbeddingConfig     # PHASE_B4 §3.3
    vector_db: VectorDBConfig      # PHASE_B4 §3.4
    graph_db: GraphDBConfig        # PHASE_B4 §3.5
    storage: StorageConfig         # PHASE_B4 §3.6 — memory TTL 포함
    cost: CostConfig               # PHASE_B4 §3.7
    self_check: SelfCheckConfig    # PHASE_B4 §3.8a
    approval: ApprovalConfig       # PHASE_B4 §3.8b
    mcp: MCPConfig                 # PHASE_B4 §3.9
    rbac: RBACConfig               # PHASE_B4 §3.10
    logging: LoggingConfig         # PHASE_B4 §3.12
    semantic_cache: SemanticCacheConfig  # PHASE_B4 §3.15
```

각 서브 Config 클래스는 config.v1.toml의 섹션과 1:1 매핑합니다 (V0=13개 섹션, V1+=17개 섹션, B4 §3 정본 기준).
<!-- NOTE (XREF-V0-18): V0는 B4 17섹션 중 13섹션만 활성. [blue_nodes],[ui],[rate_limit],[guardrails]는 V1+ 에서 추가. memory TTL은 [storage]에 포함 (별도 [memory] 섹션 없음). -->

> **V1+ 추가 config 섹션** (PHASE_B4 §3.11/§3.13~§3.14/§3.16):
> - `[rate_limit]`: `max_concurrent_blue_nodes=3` (LOCK), `max_concurrent_tools=5` (LOCK), `llm_rpm=60`, `llm_tpm=100000` — B4 §3.11 정본
> - `[blue_nodes]`: 도메인별 노드 설정 — B4 §3.13
> - `[ui]`: 테마/패널 설정 — B4 §3.14
> - `[guardrails]`: V1=2-Layer(L1+L2), V2=3-Layer(+L3), V3=4-Layer(+L4) — B4 §3.16

## 규칙
> **§1.3 R1~R11 공통 규칙 전수 적용**
- SQLite는 aiosqlite로 async 접근
- 로그는 반드시 JSON 형식 (structlog JSONRenderer)
- trace_id는 모든 로그에 필수 포함 (LOCK)
- config LOCK 값은 runtime 변경 불가하도록 frozen 처리
- 파일 경로는 config에서 읽기 (하드코딩 금지)

## 참조 SOT 문서
- D2.0-06 §2.1 (메모리 계층 L0~L3)
- D2.0-04 §9 (로깅 스펙)
- PHASE_B4_CONFIG_SPEC.md (설정 스펙 정본)
- CLAUDE.md §15 (메모리 TTL 정본)
````

### 단계 완료 검증 (V0-STEP-5 → STEP-6 전환 조건)

| # | 검증 항목 | 확인 방법 | 필수 |
|---|----------|----------|:---:|
| 1 | SQLite 테이블 생성 | `data/vamos.db`에 `memory_records` 테이블 존재 + 3개 인덱스 확인 | ✅ |
| 2 | MemoryRecord CRUD | create → read_by_id → update → delete 전체 동작 확인 | ✅ |
| 3 | 세션별 조회 | `read_by_session(session_id)` → 해당 세션 레코드만 반환 | ✅ |
| 4 | L0 TTL 적용 | scope="L0", expires_at = min(session_close_time, created_at + 30days) 확인 | ✅ |
| 5 | JSONL 로그 생성 | `logs/vamos_{date}.jsonl` 파일 생성 + JSON 파싱 정상 | ✅ |
| 6 | trace_id 일관성 | 동일 요청의 모든 로그에 동일 trace_id(UUID v4) 기록 확인 | ✅ |
| 7 | LogEventSchema 7필드 | event_type, producer, when, payload, severity + sinks(opt), links(opt) 포함 (D2.1-D2 §4.2 정본) | ✅ |
| 8 | config 로드 | `get_config()` → VamosConfig 13개 서브모델 정상 로드 | ✅ |
| 9 | LOCK 값 정확성 | embedding.model="bge-m3", cost.monthly_limit=40000, semantic_cache.similarity_threshold=0.95 등 | ✅ |
| 10 | 3단계 로딩 순서 | TOML → ENV 오버라이드 → CLI 인자 순서 동작 (LOCK 값은 변경 불가) | ✅ |

> ⛔ 위 필수 항목 전체 통과 전 STEP-6 진입 금지

---

## V0-STEP-6: CI 스켈레톤 + 테스트 (Day 9-10)

### 작업 내용
1. **GitHub Actions 기본 워크플로우**
   - `quality-python.yml`: ruff lint + mypy
   - `test-python.yml`: pytest + coverage
2. **기본 테스트**
   - 스키마 검증 테스트 (contracts.py 모든 모델)
   - IPC 브릿지 테스트 (Rust ↔ Python 통신)
   - I-1 파싱 테스트
   - I-5 Gate 테스트

### 산출물 참조
- CI/CD 스펙: `PHASE_B6_CICD_PIPELINE.md`
- 테스트 전략: `PHASE_B5_TEST_STRATEGY.md`

### 실행 가이드

#### 사용자 직접 작업
1. **GitHub Actions 시크릿 설정**: 리포지토리 Settings → Secrets에 필요한 환경변수 등록 (있을 경우)
2. **CI 워크플로우 동작 확인**: push 후 GitHub Actions 탭에서 quality-python, test-python 워크플로우가 정상 실행되는지 확인
3. **테스트 결과 리뷰**: pytest 출력에서 모든 테스트 PASS 여부와 coverage 비율 확인
4. **V0 완료 체크리스트 최종 검토**: 아래 체크리스트의 모든 항목을 직접 확인

#### AI 프롬프트

````text
VAMOS 프로젝트 V0-STEP-6: CI 스켈레톤 + 테스트를 구현합니다.

## 작업 목표
GitHub Actions CI 워크플로우와 V0 범위의 기본 테스트를 작성합니다.

## 1. GitHub Actions 워크플로우 → .github/workflows/

### quality-python.yml
```yaml
name: Python Quality
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          cd backend
          pip install poetry
          poetry install
      - name: Ruff lint
        run: cd backend && poetry run ruff check .
      - name: Mypy type check
        run: cd backend && poetry run mypy .  # pyproject.toml [tool.mypy] strict=true 적용됨 (V0부터)
```

### test-python.yml
```yaml
name: Python Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          cd backend
          pip install poetry
          poetry install
      - name: Run pytest
        run: cd backend && poetry run pytest tests/ -v --tb=short --cov=. --cov-report=term-missing
```

## 2. 기본 테스트 → backend/tests/

### test_schemas.py — 스키마 검증 테스트
25개 Pydantic 모델 전체에 대해:
- 정상 데이터로 인스턴스 생성 성공 테스트
- 필수 필드 누락 시 ValidationError 발생 테스트
- FREEZE/LOCK 모델(DecisionSchema, ResponseEnvelope, WorkflowStage, WorkflowOutput)의 필드 수 검증
- extra="forbid" 동작 확인 (추가 필드 시 에러)

```python
def test_decision_schema_field_count():
    """DecisionSchema는 정확히 18필드 (FREEZE)"""
    fields = DecisionSchema.model_fields
    assert len(fields) == 18

def test_response_envelope_field_count():
    """ResponseEnvelope은 정확히 5필드 (LOCK)"""
    fields = ResponseEnvelope.model_fields
    assert len(fields) == 5
```

### test_ipc_bridge.py — IPC 브릿지 테스트
- Python JSON-RPC 서버 기동 → echo 요청 → 응답 수신 확인
- 존재하지 않는 메서드 호출 → JSON-RPC error 응답 확인
- 잘못된 JSON → parse error 응답 확인
- 13개 스텁 메서드 각각 호출 → 기본 응답 반환 확인

### test_i1_intent.py — I-1 파싱 테스트
- 간단한 텍스트 입력 → IntentFrame 생성 확인
- IntentFrame 필드 검증 (10개 필드 존재)
- 빈 입력 → 에러 처리 확인
- 상태 전이 로그 기록 확인

### test_i5_gate.py — I-5 Gate 테스트
- PolicyGate: 정상 요청 → allow 확인
- PolicyGate: non-goal 요청 → deny 확인
- CostGate: 사용량 < 80% → allow 확인
- CostGate: 사용량 >= 80% → warn 확인
- CostGate: 사용량 >= 100% → block 확인
- ApprovalGate: P0/P1 → auto-approve 확인
- ApprovalGate: P2 → hold 확인
- 전체 Gate 종합 → DecisionSchema(locked=true) 생성 확인

### test_pipeline.py — 파이프라인 E2E 테스트
- 사용자 입력 → 5-Phase 파이프라인 실행 → ResponseEnvelope 반환 확인
- 각 Stage 정상 실행 로그 확인
- Gate deny 시 파이프라인 조기 종료 확인

### test_storage.py — 저장소 테스트
- MemoryRecord CRUD 테스트 (create/read/update/delete)
- 세션별 조회 테스트
- TTL 만료 레코드 정리 테스트

### test_config.py — Config 로더 테스트
- config.v1.toml 정상 로드 확인
- LOCK 값 정확성 확인 (embedding.model="bge-m3", semantic_cache.similarity_threshold=0.95 등)
- 잘못된 값 입력 시 ValidationError 확인
- 환경변수 오버라이드 테스트

## 3. pyproject.toml 개발 의존성 추가

```toml
[tool.poetry.group.dev.dependencies]
pytest = ">=8.3.0,<9.0"         # PHASE_B3 정본
pytest-asyncio = ">=0.24.0,<1.0" # PHASE_B3 정본
pytest-cov = ">=6.0.0,<7.0"     # PHASE_B3 정본
ruff = ">=0.8.0,<1.0"           # PHASE_B3 정본
mypy = ">=1.0"
```

## 4. ruff 설정 → backend/pyproject.toml

```toml
[tool.ruff]
target-version = "py311"
line-length = 100                # PHASE_B6 정본 (120 아님)

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "S", "B", "A", "C4", "DTZ", "T20", "ICN"]  # PHASE_B6 정본 13개

[tool.mypy]
python_version = "3.11"
strict = true
```

## 규칙
> **§1.3 R1~R11 공통 규칙 전수 적용**
- 테스트 파일은 모두 backend/tests/ 디렉토리에 위치
- pytest-asyncio를 사용하여 async 테스트 지원
- 각 테스트는 독립적으로 실행 가능 (픽스처로 격리)
- Ollama 의존 테스트는 `@pytest.mark.skipif(not os.getenv("OLLAMA_HOST"), reason="Ollama not available")`로 환경 없을 때 스킵
- CI에서는 Ollama 없이 실행 가능한 테스트만 동작
- **Ollama CI 대안 (M-10)**: (1) `unittest.mock.patch`로 ChatOllama 응답 모킹, (2) `conftest.py`에 `@pytest.fixture`로 모킹된 LLM 제공, (3) GitHub Actions에서 `services: ollama` 컨테이너 사용 시 통합 테스트도 실행 가능 (선택)

## 참조 SOT 문서
- PHASE_B5_TEST_STRATEGY.md (테스트 전략 정본)
- PHASE_B6_CICD_PIPELINE.md (CI/CD 스펙 정본)
````

### 단계 완료 검증 (V0-STEP-6 → V1 진입 전환 조건)

| # | 검증 항목 | 확인 방법 | 필수 |
|---|----------|----------|:---:|
| 1 | quality-python.yml | GitHub Actions에서 ruff lint + mypy 정상 실행 (PASS) | ✅ |
| 2 | test-python.yml | GitHub Actions에서 pytest 정상 실행 (PASS) | ✅ |
| 3 | 스키마 검증 테스트 | 25개 모델 인스턴스 생성 + 필수 필드 누락 에러 + FREEZE/LOCK 필드 수 검증 | ✅ |
| 4 | IPC 브릿지 테스트 | echo 요청/응답 + 미존재 메서드 에러 + 잘못된 JSON 파싱 에러 + 13개 스텁 응답 | ✅ |
| 5 | I-1 파싱 테스트 | 텍스트 → IntentFrame 10필드 + 빈 입력 에러 처리 + 상태 전이 로그 | ✅ |
| 6 | I-5 Gate 테스트 | PolicyGate deny/allow + CostGate warn/block + ApprovalGate auto/hold | ✅ |
| 7 | 파이프라인 E2E | 사용자 입력 → 5-Phase → ResponseEnvelope + Gate deny 시 조기 종료 | ✅ |
| 8 | Storage 테스트 | MemoryRecord CRUD + 세션별 조회 + TTL 만료 정리 | ✅ |
| 9 | Config 테스트 | 정상 로드 + LOCK 값 검증 + 잘못된 값 ValidationError + ENV 오버라이드 | ✅ |
| 10 | V0 완료 체크리스트 | 아래 13항목 전수 통과 확인 | ✅ |

> ⛔ 위 필수 항목 + 아래 V0 완료 체크리스트 전체 통과 전 V1 진입 금지

### V0 완료 체크리스트
- [ ] monorepo 구조 생성 완료
- [ ] 25개 Pydantic 스키마 정의 완료
- [ ] JSON-RPC 통신 동작 확인
- [ ] LangGraph 5-Phase 파이프라인 최소 동작
- [ ] 사용자 입력 → IntentFrame → Decision → Response 흐름 확인
- [ ] config.v1.toml 로드 확인
- [ ] JSONL 로깅 동작 확인
- [ ] pytest 실행 + 기본 통과
- [ ] EventTypeRegistry / FailureCodeRegistry / FallbackRegistry 정의 완료
- [ ] L0 Session Memory (SQLite) 기본 CRUD 동작
- [ ] Tauri IPC ↔ Python JSON-RPC 브릿지 동작
- [ ] GitHub Actions CI 스켈레톤 동작 (lint + test)
- [ ] I-19 Approval stub + I-20 Failure/Fallback stub 동작

---

# 3. V1 구현

> **목표**: Operational MVP. 실제 사용 가능한 로컬 AI 비서.
> **기간**: 14-16주 (6개 Phase, v10 추가분 반영)
> **비용 상한**: ₩40,000/월 (LOCK)
> **활성 모듈**: CORE 32개
>
> **Phase 실행 순서 규칙**:
> - Phase 1→2→3: **순차 실행** (각 Phase의 Stage Gate 통과 후 다음 Phase 진입)
> - Phase 4(UI) + Phase 5(Test) + Phase 6(AI Investing+MCP): **병렬 실행 가능** (Week 13-16)
> - Phase 6은 Phase 4-5와 병렬 진행하되, Phase 3 Stage Gate 통과가 전제조건
> - 병렬 Phase 간에도 각자의 Stage Gate는 독립적으로 통과해야 V2 진입 가능

---

## V1-Phase 1: ORANGE CORE 완성 (Week 1-4)

### 실행 가이드
> **참조 SOT 문서** (MUST 로드):
> - `D2.0-02` §7 전체 (모듈별 상세 — §7.1~7.10=I-1, §7.11~7.20=I-2, ... 순차 번호)
> - `D2.0-07` §1~6 (Gate 룰 정본)
> - `D2.0-01` §5.6 (canonical catalog — 모듈 ID↔이름 매핑 정본)
> - `D2.1-D2` (EventType 134항목, FailureCode 36항목, FallbackRegistry 23항목)
> - `D2.0-05` §4.2 (Soft/Hard Loop)
> - `D2.0-06` §2.1 (메모리 L0/L1)
> - `config.v1.toml` (LOCK 값 참조)
>
> **Phase 고유 규칙**: R1~R11 공통 규칙 + 9-State 전이 순서 LOCK + 5-Gate 순서 LOCK(Policy→Approval→Cost→Evidence→SelfCheck) + Self-check Soft Loop 1회 LOCK + config LOCK 값 runtime 변경 불가

#### AI 프롬프트

````text
VAMOS 프로젝트 V1-Phase 1: ORANGE CORE 완성을 진행합니다.

## 작업 목표
ORANGE CORE 17개 I-Series 모듈을 구현하여 완전한 Decision Kernel을 완성합니다.
9-State 상태 머신(S0~S8) 전이, 5-Gate 평가, Self-check 루프를 동작시킵니다.
§1.3 R1~R11 공통 규칙을 반드시 준수하세요.

## 공통 규칙
- 파일명: M-7 컨벤션 `i{번호:02d}_{영문명}.py` (예: i01_intent_detector.py)
- 기본 경로: `backend/vamos_core/orange_core/`
- V0-STEP-2에서 생성한 Pydantic 스키마(schemas/contracts.py) import 사용
- structlog 로거, LogEventSchema 기반 이벤트 기록 (oc.* 네임스페이스)
- 모든 public 함수: type hint + docstring (R3 규칙)
- 에러 시 FailureCode 발행 → I-20 Failure Manager 연동

## Week 1-2: 핵심 모듈 (의존성 순서 준수)

### 1. I-1 Intent Detector → `orange_core/i01_intent_detector.py`
- IntentFrame 데이터 모델 (Pydantic): user_input, intent_type, sentiment, thought_level
- 사용자 입력 파싱 → IntentFrame 생성
- 감정 탐지: positive/neutral/negative 분류
- 사고 수준 분류: simple/analytical/creative/critical
- 상태 전이: S0_RECEIVED → S1_INTENT_PARSED (타임아웃 5s)
- SOT: D2.0-02 §7.1~7.10

### 2. I-2 Context Builder → `orange_core/i02_context_builder.py`
- 6-Stage RAG Pipeline: Collect → Chunk(300~500tok) → Embed → Store → Retrieve → Generate
- BGE-M3 임베딩 (FlagEmbedding, 1024dim 원본 + Matryoshka 256dim LOCK)
- Chroma Vector DB 연동 (V0-STEP-5에서 초기화한 DB 사용)
- Hybrid Search: Dense α=0.7 + Sparse 0.3, Top-K=20, Rerank Top=5, threshold=0.75 (LOCK)
- 상태 전이: S1 → S2_EVIDENCE_READY (타임아웃 30s)
- SOT: D2.0-02 §7.11~7.20, D2.0-06

### 3. I-15 QoD Evaluator → `orange_core/i15_qod_evaluator.py`
- QoD(Quality of Decision) 평가: 소스 품질 스코어링
- Evidence 검증: 인용 정확도, 소스 신뢰도, 최신성 평가
- SOT: D2.0-02 §7.90~7.92 (B-type 매핑: D2.0-01 I-15 = D2.0-02 I-19)

### 4. I-5 Decision Engine → `orange_core/i05_decision_engine.py`
- 5-Gate 통합 평가: Policy → Approval → Cost → Evidence → SelfCheck (순서 LOCK)
- Decision Lock: S3_DECISION_LOCKED 이후 Decision 변경 불가
- DomainScore 종합 점수화: 5개 도메인별 점수 산출 + 가중 합산 공식
- 대화 턴 상한: P0=5, P1=10, P2=20 (LOCK-AT-009)
- P2 승인 필요 시 S3 → S3a_APPROVE_WAIT 분기
- 상태 전이: S2 → S3_DECISION_LOCKED (타임아웃 120s)
- SOT: D2.0-02 §7.41~7.50

### 5. I-8 Policy Engine → `orange_core/i08_policy_engine.py`
- PolicyGate 연동: 정책 규칙 평가
- 비용 기반 뇌 선택 정책: 비용 임계값별 LLM 다운시프트 (Opus→Sonnet→Haiku)
- SOT: D2.0-02 §7.41~7.50 (A+: I-5에 포함), D2.0-07 §4

### 6. I-19 Approval Manager → `orange_core/i19_approval_manager.py`
- 승인 워크플로우: P0/P1=auto-approve, P2=human approval 대기
- 타임아웃: 600s (10분, config approval.timeout_s, LOCK)
- 타임아웃 시 auto-deny
- 상태 전이: S3 → S3a_APPROVE_WAIT → S4 (타임아웃 600s)
- SOT: D2.0-07 §3/§6

## Week 3-4: 보조 모듈

> **구현 정본**: 보조 모듈 구현 상세는 sot 2/1-2_Auxiliary-Modules/이 Single Source of Truth입니다.
> 본 섹션은 When(Phase)+Where(코드 위치)만 기술합니다.

### 7. I-4 Multimodal Interpreter → `orange_core/i04_multimodal_interpreter.py`
- 텍스트/이미지/음성 입력 해석
- 상태 전이: S4 → S5_OUTPUT_READY (타임아웃 10s)
- SOT: D2.0-01 §5.6, D2.0-02 §7.31~7.40

### 8. I-6 Self-check → `orange_core/i06_self_check.py`
- 임계값: P0≥70, P1≥75, P2≥80 (LOCK)
- Soft Loop: 검증 실패 → 최대 1회 자동 재시도 (LOCK)
- 2회째 실패 → HITL 승인 요청 (Hard Loop)
- 상태 전이: S5 → S6_SELF_CHECKED (타임아웃 15s)
- SOT: D2.0-02 §7.51~7.53, D2.0-05 §4.2

### 9. I-10 Tool Router → `orange_core/i10_tool_router.py`
- ToolRegistry: 도구 등록/검색/라우팅
- E-Series Blue Node 연결 인터페이스 (V1-Phase 3에서 실제 연결)
- SOT: D2.0-02 §7.61~7.65, D2.0-03 §6

### 10. I-11 Output Composer → `orange_core/i11_output_composer.py`
- StructuredOutput 생성 (Pydantic 모델 기반)
- PII 마스킹: 주민번호/전화번호/이메일/카드번호 regex 탐지 + 마스킹
- SOT: D2.0-01 §5.6, D2.0-02 §7.66~7.68

### 11. I-3 Memory Commit → `orange_core/i03_memory_commit.py`
- L0(Session) + L1(Project) 메모리 커밋
- 커밋 전 PII 검사 → 사용자 확인 요청
- 상태 전이: S6 → S7_MEMORY_COMMITTED
- SOT: D2.0-06 §2.1, D2.0-02 §7.21~7.30

### 12. I-13 Multimodal Renderer → `orange_core/i13_multimodal_renderer.py`
- 다중 출력 포맷 (텍스트, 이미지, 오디오)
- SOT: D2.0-01 §5.6

### 13. I-14 Summarizer → `orange_core/i14_summarizer.py`
- 대화 요약, 메모리 증류 (L0→L1 승격 판단 지원)
- SOT: D2.0-02 §7.81~7.89, D2.0-06 §2.3

### 14. I-16 Knowledge Search Engine → `orange_core/i16_knowledge_search.py`
- 지식 검색: I-2 RAG와 통합, 외부 지식 소스 검색
- SOT: D2.0-01 §5.6

### 15. I-17 Blue Node Manager → `orange_core/i17_blue_node_manager.py`
- 블루 노드 라우팅: I-10 Tool Router와 연동
- 블루 노드 상태 관리 (실행/완료/실패)
- SOT: D2.0-01 §5.6

### 16. I-20 Failure/Fallback Manager → `orange_core/i20_failure_manager.py`
- FailureCodeRegistry 초기화 (36개 코드, D2.1-D2 정본)
- FallbackRegistry 초기화 (23개 매핑, D2.1-D2 정본)
- 장애 감지 → FailureCode 발행 → FallbackRegistry 조회 → Fallback 실행
- 에스컬레이션: Fallback 실패 시 HITL 요청
- SOT: D2.0-02 §7.93~7.95

### 17. I-9 Cost Manager → `orange_core/i09_cost_manager.py`
- 비용 추적: 토큰 카운팅 (입력/출력별), 모델별 단가 적용
- 3단계 경보: 70% 경고 / 85% 심화 경고 / 95% 차단 (LOCK)
- 다운시프트: Opus→Sonnet→Haiku (비용 임계값 초과 시)
- 월간 상한: ₩40,000 (cost.monthly_limit, ABSOLUTE LOCK)
- 고비용 모델(Opus) 사용 시 P2 게이팅 필수
- SOT: D2.0-01 §5.6, D2.0-02 §7.57~7.60

## 9-State 상태 머신 (D2.0-02 §2.2 LOCK)

전이 순서 변경 불가:
  S0_RECEIVED → S1_INTENT_PARSED (I-1)
    → S2_EVIDENCE_READY (I-2, I-15)
    → S3_DECISION_LOCKED (I-5: 5-Gate 평가)
        ├─ [P2 승인 불필요] → S4
        └─ [P2 승인 필요] → S3a_APPROVE_WAIT (I-19) → S4
    → S4_EXECUTING (I-11, Blue Node)
    → S5_OUTPUT_READY (I-4)
    → S6_SELF_CHECKED (I-6)
    → S7_MEMORY_COMMITTED (I-3)
    → S8_DONE

타임아웃: S1=5s, S2=30s, S3=120s, S3a=600s, S4=10s, S5=15s

## LOCK 값 (반드시 준수)
- autonomy_level: L2_COPILOT (V1 기본, PHASE_B4 §3.1)
- embedding: model="bge-m3", dimension=256 Matryoshka (LOCK)
- 5-Gate 순서: Policy→Approval→Cost→Evidence→SelfCheck (LOCK)
- Self-check: P0≥70, P1≥75, P2≥80 (LOCK)
- Soft Loop: 최대 1회 자동 재시도 (LOCK)
- cost.monthly_limit: 40000 (ABSOLUTE LOCK)
- I-19 승인 타임아웃: 600s (10분, LOCK)
- 9-State 전이 순서 변경 불가 (LOCK)
- config.v1.toml LOCK 값 runtime 변경 불가 (frozen)

## 검증 체크리스트
구현 완료 후 반드시 확인:
- [ ] 17개 .py 파일 존재 + import 에러 없음 (i01~i20, M-7 기준)
- [ ] 5-Gate 전체 동작 (Policy→Approval→Cost→Evidence→SelfCheck 순서)
- [ ] 9-State S0→S8 전이 로그 확인
- [ ] Decision locked=true (S3 이후 변경 불가)
- [ ] Self-check P0≥70, P1≥75, P2≥80 임계값 동작
- [ ] Soft Loop 1회 재시도 → 2회째 HITL 승인 요청
- [ ] I-19 승인 10분 타임아웃 auto-deny 동작
- [ ] I-1 감정/사고 수준 분류 동작
- [ ] I-11 StructuredOutput + PII 마스킹 동작
- [ ] 상태 타임아웃 (S1=5s, S2=30s, S3=120s, S3a=600s, S4=10s, S5=15s)
````

### Week 1-2: 핵심 모듈 구현

| 순서 | 모듈 | 구현 내용 | 의존성 | 파일명 (M-7) | 산출물 참조 |
|------|------|----------|--------|-------------|-----------|
| 1 | I-1 | IntentFrame 생성, 감정 탐지, 사고 수준 분류 | 없음 | `i01_intent_detector.py` | D2.0-02 §7.1~7.10 |
| 2 | I-2 | RAG 파이프라인, BGE-M3 임베딩, Chroma 검색 | I-1 | `i02_context_builder.py` | D2.0-02 §7.11~7.20, D2.0-06 |
| 3 | I-15 | QoD 평가, 소스 품질 스코어링 | I-2 | `i15_qod_evaluator.py` | D2.0-02 §7.90~7.92 (B-type: D2.0-02 I-19), D2.0-01 §5.6 | <!-- B-type 매핑: D2.0-01 I-15 = D2.0-02 I-19 -->
| 4 | I-5 | 5-Gate 통합, Decision Lock, 라우팅 | I-1,I-2,I-15 | `i05_decision_engine.py` | D2.0-02 §7.41~7.50 |
| 5 | I-8 | Policy Engine (정책 평가, PolicyGate 연동) | I-5 | `i08_policy_engine.py` | D2.0-02 §7.41~7.50 (A+: I-5에 포함), D2.0-07 §4 | <!-- A+ 매핑: I-8은 D2.0-02 I-5에 1:N 병합 -->
| 6 | I-19 | 승인 워크플로우, 타임아웃(10분), P2 게이팅 | I-5 | `i19_approval_manager.py` | D2.0-07 §3/§6 (D2.0-02 미수록) | <!-- I-19 상세설계는 D2.0-07에만 존재 -->

### Week 3-4: 보조 모듈 구현

| 순서 | 모듈 | 구현 내용 | 의존성 | 파일명 (M-7) | 산출물 참조 |
|------|------|----------|--------|-------------|-----------|
| 7 | I-4 | Multimodal Interpreter (텍스트/이미지/음성 해석) | I-5 | `i04_multimodal_interpreter.py` | D2.0-01 §5.6, D2.0-02 §7.31~7.40 |
| 8 | I-6 | Self-check (P0>=70, P1>=75, P2>=80), Soft Loop 1회 | I-5 | `i06_self_check.py` | D2.0-02 §7.51~7.53, D2.0-05 §4.2 | <!-- M-12: 의존성 I-4→I-5 수정. Self-check는 Decision Engine(I-5) 출력을 검증 -->
| 9 | I-10 | Tool Registry/Router | I-5 | `i10_tool_router.py` | D2.0-02 §7.61~7.65, D2.0-03 §6 |
| 10 | I-11 | Output Composer (StructuredOutput 생성, PII 마스킹) | I-5, I-10 | `i11_output_composer.py` | D2.0-01 §5.6, D2.0-02 §7.66~7.68 |
| 11 | I-3 | Memory 커밋 (L0+L1), 승인 요청 | I-5, I-6 | `i03_memory_commit.py` | D2.0-06 §2.1, D2.0-02 §7.21~7.30 |
| 12 | I-13 | Multimodal Output Renderer (다중 출력 포맷) | I-1 | `i13_multimodal_renderer.py` | D2.0-01 §5.6 |
| 13 | I-14 | Summarizer, 메모리 증류 | I-3 | `i14_summarizer.py` | D2.0-02 §7.81~7.89, D2.0-06 §2.3 |
| 14 | I-16 | Knowledge Search Engine (지식 검색, RAG 통합) | 없음 | `i16_knowledge_search.py` | D2.0-01 §5.6 |
| 15 | I-17 | Blue Node Manager (블루 노드 라우팅/관리) | I-8 | `i17_blue_node_manager.py` | D2.0-01 §5.6 |
| 16 | I-20 | Failure/Fallback Manager | 전체 | `i20_failure_manager.py` | D2.0-02 §7.93~7.95 |
| 17 | I-9 | Cost Manager (비용 추적, 다운시프트, 토큰 카운팅) | 전체 | `i09_cost_manager.py` | D2.0-01 §5.6, D2.0-02 §7.57~7.60 |

> **M-7 파일 기본 경로**: 위 `파일명 (M-7)` 칼럼의 파일은 `backend/vamos_core/orange_core/` 디렉토리 하위에 위치합니다 (PHASE_B2 §2.1 모노레포 구조 참조). 예: `i01_intent_detector.py` → `backend/vamos_core/orange_core/i01_intent_detector.py` <!-- v25.1.0: M-7 파일 기본 경로 명시 -->

> ⚠️ D2.0-01 §5.6 canonical catalog 기준. D2.0-02(ORANGE CORE 상세설계)는 §7.1~7.10=I-1, §7.11~7.20=I-2, ... 순차 번호 체계를 사용합니다 (§7.{모듈번호}가 아님). 구현 시 D2.0-01을 SOT로 참조하되 D2.0-02의 상세 로직을 따르세요. BLOCKER-12/13 참조.

> **V1 Phase 1 적용 LOCK/FREEZE 값** (구현 시 반드시 준수):
> - I-1: `autonomy_level` V1 기본값 `L2_COPILOT` (PHASE_B4 §3.1 LOCK). V0 초기값 `L1`에서 V1 전환 시 업그레이드
> - I-2: `embedding.model="bge-m3"`, `embedding.dimension=256` (Matryoshka, LOCK)
> - I-5: 5-Gate 순서 LOCK (Policy→Approval→Cost→Evidence→SelfCheck)
> - I-6: Self-check 임계값 P0≥70, P1≥75, P2≥80 (LOCK), Soft Loop 최대 1회 (LOCK)
> - I-9: `cost.monthly_limit=40000` (ABSOLUTE LOCK)
> - I-19: 승인 타임아웃 10분 (LOCK), P2 자동 게이팅 (LOCK)
> - 상태 머신: 9-State 전이 순서 변경 불가 (D2.0-02 §2.2 LOCK)
> - 전체: config.v1.toml LOCK 값은 runtime 변경 불가 (frozen)

### ORANGE CORE 상태 머신 (D2.0-02 §2.2 정본, 9-State LOCK)

```
S0_RECEIVED → S1_INTENT_PARSED (I-1)
  → S2_EVIDENCE_READY (I-2, I-19)
  → S3_DECISION_LOCKED (I-5: 4-Gate 평가)
      ├─ [P2 승인 불필요] → S4로 직행
      └─ [P2 승인 필요] → S3a_APPROVE_WAIT (I-19: 인간 승인 대기) → S4
  → S4_EXECUTING (BLUE NODE/TOOLS via I-11)
  → S5_OUTPUT_READY (I-4)
  → S6_SELF_CHECKED (I-6)
  → S7_MEMORY_COMMITTED (I-3 + 06/07)
  → S8_DONE
```

> **타임아웃 (D2.0-02 §2.2)**: S1=5s, S2=30s, S3=120s (Gate 평가), **S3a=600s (P2 승인 대기, config approval.timeout_s)**, S4=10s, S5=15s
> **LOCK**: 9-State 전이 순서 변경 불가. S3a는 S3의 하위 상태(sub-state)로 9-State 카운트에 포함하지 않음. S3 이후 Decision locked=true.

### 산출물 참조
- 모듈별 상세: `D2.0-02` §7 전체
- Gate 룰: `D2.0-07` §1~6
- 상태 머신: `D2.0-02` §2.2 (위 인라인 참조)
- EventType/FailureCode: `D2.1-D2`

### I-5/I-8/I-9 하위 구현 체크리스트 <!-- PATCH-H02 v22.0.0: 상위 모듈에 포함된 누락 항목 명시 -->

> I-5 Decision Engine, I-8 Policy Engine, I-9 Cost Manager 구현 시 아래 하위 항목이 포함되어야 합니다.

| 모듈 | 하위 항목 | 구현 내용 | SOT |
|------|----------|----------|-----|
| I-5 | DomainScore 종합 점수화 | 5개 도메인별 점수 산출 + 가중 합산 공식 구현 | P30-009 |
| I-8 | 비용 기반 뇌 선택 정책 | 비용 임계값별 LLM 자동 다운시프트 정책 (Opus→Sonnet→Haiku) | P30-029 |
| I-9 | 비용 3단계 경보 체계 | 70% 경고 / 85% 심화 경고 / 95% 차단 (config.v1.toml cost 섹션) | P30-058 |
| I-9 | 고비용 모델 사용 제약 | Opus 사용 시 승인 필요 (P2 게이팅), 일일 Opus 호출 상한 설정 | P30-061 |
| I-5 | 대화 턴 상한 | P0=5, P1=10, P2=20 턴 상한 구현 (LOCK-AT-009) | CLAUDE-108 |

### 단계 완료 검증 (V1-Phase 1 → Phase 2 전환 조건)

| # | 검증 항목 | 확인 방법 | 필수 |
|---|----------|----------|:---:|
| 1 | I-Series 17개 모듈 코드 | 17개 `.py` 파일 존재 + import 에러 없음 (i01~i20, M-7 파일명 기준) | ✅ |
| 2 | 5-Gate 전체 동작 | Policy → Approval → Cost → Evidence → SelfCheck 순서 실행 확인 (CLAUDE.md §7.2) | ✅ |
| 3 | 9-State 상태 머신 | S0_RECEIVED → S1 → S2 → S3 → S4 → S5 → S6 → S7 → S8_DONE 전이 로그 확인 | ✅ |
| 4 | Decision locked=true | S3_DECISION_LOCKED 이후 Decision 변경 불가 확인 | ✅ |
| 5 | I-6 Self-check 점수 | P0≥70, P1≥75, P2≥80 임계값 동작 확인 (config self_check 섹션) | ✅ |
| 6 | Soft Loop 1회 재시도 | 검증 실패 → 자동 1회 재시도 → 2회째 실패 시 HITL 승인 요청 | ✅ |
| 7 | I-19 Approval 워크플로우 | P2 승인 요청 → 10분 타임아웃 auto-deny 동작 | ✅ |
| 8 | I-1 감정 탐지 | 사용자 입력의 감정/사고 수준 분류 동작 확인 | ✅ |
| 9 | I-11 Output Composer | StructuredOutput 생성 + PII 마스킹 동작 확인 | ✅ |
| 10 | 상태 타임아웃 | S1=5s, S2=30s, S3=120s, S3a=600s(P2 승인), S4=10s, S5=15s 타임아웃 동작 확인 | ✅ |

> ⛔ 위 필수 항목 전체 통과 전 Phase 2 진입 금지

---

## V1-Phase 2: Storage + Memory + RAG (Week 5-8)

> **파일 경로 참조**: V1 Phase 2~6 구현 항목의 `파일경로` 칼럼은 PHASE_B2 모노레포 구조 기준 상대경로입니다. 기본 경로:
> - **Python**: `backend/vamos_core/` → `orange_core/`, `blue_nodes/`, `storage/`, `safety/`, `agent/`, `infra/`, `mcp/`, `schemas/`
> - **React**: `frontend/src/` → `components/`, `pages/`, `hooks/`, `stores/`, `types/`, `styles/`
> - **Rust**: `src-tauri/src/` | **CI/CD**: `.github/workflows/` | **테스트**: `backend/tests/`, `e2e/`
> <!-- FIX-18-v2: C-IMP-003 대응. v25.1.0에서 V1 Phase 2~6 테이블에 파일경로 칼럼 추가 -->

### 실행 가이드
> **AI 프롬프트 요약**: "V1-Phase 2 Storage/Memory/RAG를 구현하세요. SQLite(L0/L1), Chroma VectorDB, JSON GraphRAG, Semantic Cache, PII 마스킹, B-3 Decay를 구현합니다. §1.3 R1~R11 + 아래 LOCK 값을 반드시 준수하세요."
>
> **참조 SOT 문서** (MUST 로드):
> - `D2.0-06` (메모리 설계 정본) — L0~L3, B-Series, 6-Stage RAG
> - `D2.1-A1` (벡터 DB 스키마) — Chroma 임베딩 구조
> - `D2.1-D6` (Semantic Cache 스키마) — 캐시 정책
> - `config.v1.toml` §3.14~3.15 (LOCK 값 참조)
>
> **Phase 고유 규칙**: R1~R11 공통 규칙 + B↔L 매핑 LOCK(B-1→L1, B-2→L3, B-3→L2, B-4→L0) + Semantic Cache cosine ≥ 0.95 LOCK

#### AI 프롬프트

````text
VAMOS 프로젝트 V1-Phase 2: Storage/Memory/RAG를 구현합니다.

## 작업 목표
SQLite 기반 L0/L1 메모리, Chroma VectorDB, JSON GraphRAG, Semantic Cache,
PII 마스킹, B-3 Decay를 구현하여 ORANGE CORE의 메모리/검색 계층을 완성합니다.
§1.3 R1~R11 공통 규칙을 반드시 준수하세요.

## 1. L0 Session Memory → `backend/vamos_core/storage/memory/l0_session.py`
- SQLite 기반 세션 메모리 CRUD
- TTL: session_end 또는 created_at + 30일 중 먼저 (LOCK)
- 세션 종료 시 자동 정리
- B-4 Working Memory 매핑 (B-4 → L0, LOCK)

## 2. L1 Project Memory → `backend/vamos_core/storage/memory/l1_project.py`
- SQLite 기반 프로젝트 메모리 CRUD
- TTL: 90일 (LOCK)
- project_id별 분리 저장/조회
- B-1 Episodic Memory 매핑 (B-1 → L1, LOCK)

## 3. Chroma Vector DB → `backend/vamos_core/storage/vector/chroma_store.py`
- BGE-M3 1024dim 원본 임베딩 저장
- Matryoshka 256dim 검색용 인덱스 (LOCK)
- Hybrid Search: Dense α=0.7 + Sparse 0.3, Top-K=20, Rerank=5, threshold=0.75 (LOCK)
- V1-Phase 1 I-2 Context Builder와 연동

## 4. JSON GraphRAG → `backend/vamos_core/storage/graph/json_graph.py`
- NetworkX 기반 엔티티/관계 그래프 저장
- 노드: Decision, Evidence, Module, Event, Conversation
- JSON 파일 영속화 (V2에서 Neo4j로 마이그레이션 예정)

## 5. Semantic Cache → `backend/vamos_core/storage/cache/semantic_cache.py`
- cosine similarity ≥ 0.95 히트 (LOCK)
- TTL: 86400s (24시간, D2.0-06 §4.7.2)
- max_entries: 1000
- 무효화 정책: TTL 기반 + Embedding Drift(>0.05) + 수동(vamos:cache:invalidate)

## 6. 대화 내보내기/가져오기 → `backend/vamos_core/storage/export.py`
- JSON/Markdown 형식 export/import
- UI 연동: V1-Phase 4 Settings 페이지에서 버튼 제공

## 7. PII 마스킹 → `backend/vamos_core/safety/guardrails/pii_masker.py`
- 주민번호/전화번호/이메일/카드번호 regex 탐지
- 마스킹 처리 (`***`)
- VAL-008 연동 (출력 전 PII 누락 검사)

## 8. 메모리 B-3 Decay → `backend/vamos_core/storage/memory/decay.py`
- TTL 기반 자동 만료
- activation_state 관리 (active/dormant/archived)
- B-3 Semantic Memory → L2 Long-term 매핑 (LOCK)

## 9. DCL 기초 구현 → `backend/vamos_core/storage/kb/dcl_collector.py`
- DCL-FIN: RT-BNP RSS 수집기
- DCL-TECH: RSS 1시간 폴링 수집기
- I-2 RAG 파이프라인 자동 삽입 연동

## v23 확장 항목 (#10~13)
위 core 구현 완료 후 §6.10 상세를 참조하여 추가 구현 <!-- S5-191 v26 -->:
- 진화 제어 정책 설정, 한국어 불용어 처리, 3종 TemplateSet, 알림 규칙

## LOCK 값 (반드시 준수)
- L0 TTL: session_end 또는 created_at + 30일 (D2.0-06 §2.1)
- L1 TTL: 90일 (D2.0-06 §2.1)
- Semantic Cache: cosine ≥ 0.95 (D2.1-D6)
- BGE-M3: 1024dim + Matryoshka 256dim
- 6-Stage RAG Pipeline 순서 (D2.0-06 §1.1)
- B↔L 매핑: B-1→L1, B-2→L3, B-3→L2, B-4→L0
- Hybrid Search: α=0.7, Top-K=20, threshold=0.75

## 검증 체크리스트
- [ ] L0 Session Memory CRUD + TTL + 세션 종료 정리
- [ ] L1 Project Memory CRUD + TTL 90일 + project_id 분리
- [ ] Chroma Vector DB BGE-M3 임베딩 + Matryoshka 256dim 검색
- [ ] JSON GraphRAG 엔티티/관계 저장 + 검색
- [ ] Semantic Cache cosine ≥ 0.95 히트 + TTL 24시간 만료
- [ ] 6-Stage RAG Pipeline 전체 동작
- [ ] Hybrid Search Dense+Sparse + Rerank
- [ ] PII 마스킹 4종 regex 탐지 + 마스킹
- [ ] B-3 Memory Decay TTL 자동 만료
- [ ] DCL-FIN + DCL-TECH 수집 동작
- [ ] B↔L 매핑 정합성 (B-1→L1, B-2→L3, B-3→L2, B-4→L0)
````

### 구현 항목

| # | 항목 | 구현 내용 | 파일경로 | 산출물 참조 |
|---|------|----------|---------|-----------|
| 1 | **L0 Session Memory** | SQLite, TTL=session_end, 자동 정리 | `storage/memory/` | D2.0-06 §2.1 |
| 2 | **L1 Project Memory** | SQLite, TTL=90일, project_id별 분리 | `storage/memory/` | D2.0-06 §2.1 |
| 3 | **Chroma Vector DB** | BGE-M3 1024dim, Matryoshka 256dim, 로컬 | `storage/vector/` | D2.1-A1 |
| 4 | **JSON 파일 기반 GraphRAG** | 기본 엔티티/관계 저장, NetworkX | `storage/graph/` | D2.0-06 §4.7 |
| 5 | **Semantic Cache** | cosine >= 0.95 LOCK, 응답 캐싱 | `storage/cache/` | D2.1-D6 |
| 6 | **대화 내보내기/가져오기** | JSON/Markdown export, import. UI: V1-Phase 4 §설정 뷰에서 내보내기 버튼 제공 (M-13) | `storage/` + `pages/SettingsPage.tsx` | D2.0-02 §7.3, D2.0-08 §8 |
| 7 | **PII 마스킹** | 주민번호/전화번호/이메일/카드번호 regex | `safety/guardrails/` | D2.0-07 §6.4 |
| 8 | **메모리 B-3 Decay** | TTL 기반 자동 만료, activation_state 관리 | `storage/memory/` | D2.0-06 §2.1 | <!-- SOURCE_CONFLICT: D2.0-01 §5.10 B-3="Memory Decay" vs §8.4 B-3="Deep Reflection". §5.10 LOCK 채택, §8.4는 [DEPRECATE] 레거시 -->
| 9 | **DCL 기초 구현** | DCL-FIN(RT-BNP RSS) + DCL-TECH(RSS 1시간) 수집기, I-2 RAG 자동 삽입 | `storage/kb/` | §6.10.2 |
| | **── v23 확장 ──** | | | |
| 10 | **진화 제어 정책 설정 (변경 유형별 자동/알림/승인 규칙)** | 진화 제어 정책 설정 (변경 유형별 자동/알림/승인 규칙) [MEDIUM] | §6 참조 | v10 Phase 2 추가 (CLIB-058) | <!-- CLIB-058 v23 -->
| 11 | **한국어 불용어 처리** | 한국어 불용어 처리 [MEDIUM] | §6 참조 | v10 Phase 2 추가 (D206-064) | <!-- D206-064 v23 -->
| 12 | **3종 TemplateSet 구현 (TS_CORE/TS_WEB_RESEARCH/TS_CODE** | 3종 TemplateSet 구현 (TS_CORE/TS_WEB_RESEARCH/TS_CODE [MEDIUM] | §6 참조 | v10 Phase 2 추가 (MSTR-007) | <!-- MSTR-007 v23 -->
| 13 | **알림 규칙** | 알림 규칙 [MEDIUM] | §6.12.4 참조 <!-- S5-192 v26 --> | v10 Phase 2 추가 (S7FI-056) | <!-- S7FI-056 v23 -->
| | **── v12 BLOCKER 추가 ──** | | | | <!-- v12_BLOCKER v26 -->
| 14 | **LLM 비용 최적화 시스템** | Smart Routing(모델 자동 선택: 복잡도→GPT-4o/간단→GPT-3.5), Semantic Caching(중복 호출 방지, cosine≥0.95 히트 시 캐시 반환), Token 최적화(프롬프트 압축, 불필요 토큰 제거) [BLOCKER] | `infra/cost_optimizer/` | §6.2 참조 | <!-- v12_C11_151 v26 -->
| | **-- v12 HIGH 추가: Business --** | | | | <!-- feature_id v26 -->
| 28 | **DQ Validation 데이터 품질 검증** | 데이터 품질 검증 규칙: ISO8601 날짜/시간 검증, decimal-safe 수치 처리, 필수 필드 존재 확인, 범위 검증 [HIGH] | §6 참조 | §6 참조 | <!-- v12_C08_047 v26 -->

> **V1 Phase 2 적용 LOCK/FREEZE 값**:
> - L0 TTL: `session_end` 또는 `created_at + 30days` 중 먼저 (D2.0-06 §2.1 LOCK)
> - L1 TTL: 90일 (D2.0-06 §2.1 LOCK)
> - Semantic Cache: `cosine >= 0.95` (D2.1-D6 LOCK)
> - BGE-M3: 1024dim 원본 + Matryoshka 256dim (LOCK)
> - 6-Stage RAG Pipeline 순서 (D2.0-06 §1.1 LOCK)
> - B↔L 매핑: B-1→L1, B-2→L3, B-3→L2, B-4→L0 (LOCK)

#### B↔L 매핑 테이블 (D2.0-06 §2.1 + CLAUDE.md §15, LOCK — 비직관적 매핑 주의)

| B-Series | 메모리 유형 | L 계층 | 설명 | V3 학습 모듈 |
|----------|-----------|--------|------|-------------|
| B-1 Episodic | 사건/대화 기록 | L1 (Project) | 프로젝트 컨텍스트 | Skill Library (b01) |
| B-2 Procedural | 절차/템플릿 | L3 (Procedural) | 전역/프로젝트 절차 | Procedural Memory (b02) |
| B-3 Semantic | 정리된 사실/지식 | L2 (Long-term) | 전역 검색 기반 | Memory Decay (V1 완료) |
| B-4 Working | 세션 컨텍스트 | L0 (Session) | 단일 세션 휘발 | DSPy Integration (b04) |

> **B-Series 이중 의미**: 좌측 4열은 **메모리 유형** 분류 (D2.0-06 LOCK), 우측 V3 학습 모듈은 해당 메모리를 **학습/최적화하는 모듈**. 이름이 다르지만 1:1 대응. (§5 V3-PH2 그룹10 참조)

#### 6-Stage RAG Pipeline (D2.0-06 §1.1 LOCK)

```
Stage 1 Collect (수집) → Stage 2 Chunk (쪼개기, 300~500tok)
→ Stage 3 Embed (벡터화) → Stage 4 Store (저장)
→ Stage 5 Retrieve (검색, Hybrid Search) → Stage 6 Generate (생성)
```

#### Hybrid Search 파라미터 (D2.0-06 S7D-012/S7D-018 정본)

| 파라미터 | 값 | LOCK |
|---------|---|------|
| Dense weight (α) | 0.7 | Y |
| Sparse weight (1-α) | 0.3 | Y |
| Top-K retrieve | 20 | N |
| Top-K rerank | 5 | N |
| Similarity threshold | 0.75 | Y |

#### Semantic Cache 파라미터 (M-25: LOCK 값 명시)

| 파라미터 | 값 | LOCK | 근거 |
|---------|---|------|------|
| similarity_threshold | **cosine ≥ 0.95** | **Y** | config.v1.toml `[semantic_cache]`, PHASE_B4 §3.15 |
| ttl_sec | 86400 (24시간) | N | D2.0-06 §4.7.2 |
| max_entries | 1000 | N | config.v1.toml |

#### Semantic Cache 무효화 정책 (D2.0-06 §4.7.2 정본)

1. **TTL 기반**: `ttl_sec = 86400` (24시간, D2.0-06 §4.7.2 정본) 초과 시 자동 만료
2. **Embedding Drift 기반**: 원본 문서 재임베딩 시 cosine 차이 > 0.05면 캐시 무효화
3. **수동 무효화**: `vamos:cache:invalidate` IPC 명령으로 특정 키/패턴 삭제

### 단계 완료 검증 (V1-Phase 2 → Phase 3 전환 조건)

| # | 검증 항목 | 확인 방법 | 필수 |
|---|----------|----------|:---:|
| 1 | L0 Session Memory | SQLite CRUD + TTL=session_end(최대 30일) + 세션 종료 시 자동 정리 | ✅ |
| 2 | L1 Project Memory | SQLite CRUD + TTL=90일 + project_id별 분리 동작 | ✅ |
| 3 | Chroma Vector DB | BGE-M3 1024dim 임베딩 저장 + Matryoshka 256dim 검색 동작 | ✅ |
| 4 | JSON GraphRAG | 엔티티/관계 저장 + NetworkX 기반 그래프 검색 동작 | ✅ |
| 5 | Semantic Cache | cosine ≥ 0.95 히트 + TTL 24시간 만료 + 수동 무효화 동작 | ✅ |
| 6 | 6-Stage RAG Pipeline | Collect→Chunk→Embed→Store→Retrieve→Generate 전체 동작 | ✅ |
| 7 | Hybrid Search | Dense α=0.7 + Sparse 0.3 + Top-K 20 + Rerank 5 + threshold 0.75 | ✅ |
| 8 | PII 마스킹 | 주민번호/전화번호/이메일/카드번호 regex 탐지 + 마스킹 동작 | ✅ |
| 9 | B-3 Memory Decay | TTL 기반 자동 만료 + activation_state 관리 동작 | ✅ |
| 10 | 대화 내보내기/가져오기 | JSON/Markdown export + import 동작 확인 | ✅ |
| 11 | DCL 기초 구현 | DCL-FIN(RT-BNP RSS) + DCL-TECH(RSS 1시간 폴링) 수집 동작 | ✅ |
| 12 | B↔L 매핑 정합성 | B-1→L1, B-2→L3, B-3→L2, B-4→L0 매핑 코드 반영 확인 | ✅ |

> ⛔ 위 필수 항목 전체 통과 전 Phase 3 진입 금지

---

## V1-Phase 3: Workflow + Agent (Week 9-12)

### 실행 가이드
> **AI 프롬프트 요약**: "V1-Phase 3 Workflow/Agent를 구현하세요. LangGraph StateGraph(5-Phase), Gate 통합 노드, Soft/Hard Loop, Circuit Breaker, MultiBrain Adapter, Agent Teams V1, E-시리즈(E-1~E-6), C/D-시리즈를 구현합니다."
>
> **참조 SOT 문서** (MUST 로드):
> - `D2.0-05` (워크플로우 정본) — StateGraph, Gate 룰, Circuit Breaker LOCK
> - `D2.0-04` (MultiBrain 정본) — Adapter 인터페이스, Failover 정책
> - `D2.0-03` (블루 노드 정본) — E-1~E-6 상세 스펙
> - `D2.0-07` (Gate 룰 정본) — I-8 Policy, I-19 Approval
> - `VAMOS_AGENT_TEAMS_SPEC` — Agent Teams V1 스펙
>
> **Phase 고유 규칙**: R1~R11 + LangGraph `START`/`END` 상수 사용(set_entry_point 금지) + Circuit Breaker recovery=60s LOCK + Agent max 2 Sub LOCK

#### AI 프롬프트

````text
VAMOS 프로젝트 V1-Phase 3: Workflow/Agent를 구현합니다.

## 작업 목표
LangGraph StateGraph(5-Phase), Gate 통합 노드, Circuit Breaker, MultiBrain Adapter,
Agent Teams V1, E-Series Blue Node(E-1~E-6), C/D-Series를 구현합니다.
§1.3 R1~R11 공통 규칙을 반드시 준수하세요.

## 1. LangGraph StateGraph → `backend/vamos_core/agent/graph/state_graph.py`
- 5-Phase 파이프라인: Intake → Plan → Execute → Verify → Deliver
- `from langgraph.graph import StateGraph, START, END` 사용 (set_entry_point 금지)
- 조건부 분기: Verify 실패 → Soft Loop(1회) → Hard Loop(HITL)
- 단순 제어 흐름 원칙: StateGraph 중첩 금지, 모듈 내부는 함수/if-else/while 사용

## 2. Gate 통합 노드 → `backend/vamos_core/agent/gate_pipeline.py`
- LangGraph 노드로 5-Gate 실행 (V1-Phase 1 I-5 Decision Engine 호출)
- Gate 결과 기반 라우팅: allow/deny/downshift/hold

## 3. Soft/Hard Loop → `backend/vamos_core/agent/pipeline/` + `agent/hitl.py`
- Soft Loop: 검증 실패 → 최대 1회 자동 재시도 (LOCK)
- Hard Loop: 2회째 실패 → HITL 승인 요청 (I-19 연동)

## 4. Circuit Breaker → `backend/vamos_core/agent/circuit_breaker.py`
- 3-State: closed/open/half_open
- failure_threshold=3, recovery_time_sec=60 (LOCK), half_open_requests=1
- 장애 감지 → open → recovery 후 half_open → 성공 시 closed

## 5. A-1 MultiBrain Adapter → `backend/vamos_core/infra/brain/adapter.py`
- Ollama + GPT-4o-mini 통합 인터페이스
- Failover 체인: GPT-4o → Claude → Ollama (3회 타임아웃 시 전환, LOCK)
- 각 LLM별 어댑터 구현: `brain/ollama.py`, `brain/openai.py`, `brain/anthropic.py`

## 6. A-2 Preset Modularization → `backend/vamos_core/infra/preset.py`
- JSON 기반 프리셋 저장/로드/적용
- PresetSchema(id, name, params, category)

## 7. Agent Teams V1 → `backend/vamos_core/agent/teams.py`
- Lead Agent + max 2 Sub-Agent (LOCK-AT-014 V1)
- 패턴: Sequential + Parallel만 (V1 범위)
- 위임 깊이 제한: 최대 2단계 (LOCK-AT-004)

## 8~13. E-Series Blue Node (E-1~E-6) → `backend/vamos_core/blue_nodes/`
- E-1 Coding Helper → `blue_nodes/dev/e1_coding.py`: 코드 생성/디버그/리팩토링
- E-2 Web Search → `blue_nodes/research/e2_web_search.py`: Tavily/SerpAPI MCP 연결
- E-3 Document Parser → `blue_nodes/content/e3_doc_parser.py`: Unstructured.io, PyMuPDF
- E-4 Code Executor → `blue_nodes/dev/e4_code_executor.py`: Docker 샌드박스 (LOCK), E2B
- E-5 Image Analyzer → `blue_nodes/content/e5_image_analyzer.py`: CLIP MCP 래퍼 (V1=단건)
- E-6 Z3 Solver → `blue_nodes/quant/e6_z3_solver.py`: z3.Solver() 기반, ConstraintSet→SolverResult

## 14. C-1~C-3 Verifier → `backend/vamos_core/orange_core/`
- C-1 Logic Verifier: 논리식 검증, BaseVerifier(ABC).verify() → VerifyResult
- C-2 Math Verifier: sympy 수식 검증
- C-3 Code Verifier: AST 분석 + pytest 실행

## 15. D-1~D-2 Engine → `backend/vamos_core/orange_core/`
- D-1 Think Engine: 추론 엔진
- D-2 Multimodal Engine: 멀티모달 처리

## v23 확장 항목 (#16~59)
위 core 구현 완료 후 각 항목의 v10 참조 ID로 §6 해당 섹션을 참조하여 추가 구현 <!-- S5-193 v26 -->:
- 중앙 프롬프트 라이브러리, 작업 중단 복원, 연구 노트/코드 스니펫/아이디어 캡처,
  스트레스 관리/CBT/번아웃 예방, 알림/소셜미디어/블랙-리터만/팩터투자/리밸런싱,
  음성최적화/프로파일링/DB관리/Zettelkasten, 교육(플래시카드/퀴즈/간격반복 등),
  웰니스/습관/일기/포모도로 등 44건 — 각 항목의 v10 참조 ID로 §6에서 상세 확인

## LOCK 값 (반드시 준수)
- LangGraph 5-Phase 순서: Intake→Plan→Execute→Verify→Deliver
- Soft Loop: 최대 1회 (D2.0-05 §4.2)
- Circuit Breaker: failure_threshold=3, recovery_time_sec=60 (D2.0-05 §4.4)
- A-1 Failover: GPT-4o→Claude→Ollama, 3회 타임아웃 시 전환
- Agent Teams V1: max 2 Sub-Agent (LOCK-AT-014)
- E-4 Code Executor: Docker 샌드박스 (LOCK)

## 검증 체크리스트
- [ ] LangGraph 5-Phase Intake→Plan→Execute→Verify→Deliver 전체 동작
- [ ] Gate 통합 노드에서 5-Gate 실행 + 라우팅
- [ ] Soft Loop 1회 재시도 + Hard Loop HITL 승인
- [ ] Circuit Breaker closed/open/half_open 전이 + recovery 60s
- [ ] A-1 MultiBrain Adapter Failover (GPT-4o→Claude→Ollama)
- [ ] Agent Teams V1: Lead + 2 Sub + Sequential/Parallel
- [ ] E-1~E-6 Blue Node 전체 동작
- [ ] C-1~C-3 Verifier + D-1~D-2 Engine 동작
- [ ] 위임 깊이 최대 2단계 초과 시 차단
- [ ] A-2 Preset 등록/조회/적용
````

### 구현 항목

| # | 항목 | 구현 내용 | 파일경로 | 산출물 참조 |
|---|------|----------|---------|-----------|
| 1 | **LangGraph StateGraph** | 5-Phase 완성 (Intake→Plan→Execute→Verify→Deliver) | `agent/graph/` | D2.0-05 §4 |
| 2 | **Gate 통합 노드** | LangGraph 노드로 Gate 실행 | `agent/gate_pipeline.py` | D2.0-05 §6 |
| 3 | **Soft/Hard Loop** | 검증 실패 → 1회 자동 재시도 → HITL 승인 | `agent/pipeline/` + `agent/hitl.py` | D2.0-05 §4.2 LOCK |
| 4 | **Circuit Breaker** | closed/open/half_open, failure_threshold=3, recovery_time_sec=60 (D2.0-05 §4.4 LOCK), half_open_requests=1 | `agent/circuit_breaker.py` | D2.0-05 §4.4 | <!-- SOURCE_CONFLICT: D2.1-D5/D7 스키마는 300s로 기재. 정본 우선순위(DESIGN 2.0 LOCK > Schema)에 따라 60s 채택 -->
| 5 | **A-1 MultiBrain Adapter** | Ollama + GPT-4o-mini 통합 인터페이스ㅤ**Failover**: GPT-4o→Claude→Ollama (3회 타임아웃 시 전환, LOCK) | `infra/brain/` | D2.0-04 §3 |
| 6 | **A-2 Preset Modularization** | 프리셋 시스템: JSON 기반 프리셋 저장/로드/적용, PresetSchema(id, name, params, category) (D2.0-04 §5) | `infra/` | D2.0-04 |
| 7 | **Agent Teams V1** | Lead + max 2 Sub-Agent, Sequential/Parallel만 | `agent/` | VAMOS_AGENT_TEAMS_SPEC |
| 8 | **E-1 Coding Helper** | 코드 생성/디버그/리팩토링 | `blue_nodes/dev/` | D2.0-03 |
| 9 | **E-2 Web Search** | Tavily/SerpAPI MCP 연결 | `blue_nodes/research/` | D2.0-03, D2.1-D3 §6.4 |
| 10 | **E-3 Document Parser** | Unstructured.io MCP, PyMuPDF | `blue_nodes/content/` | D2.0-03 |
| 11 | **E-4 Code Executor** | Docker 샌드박스 LOCK, E2B | `blue_nodes/dev/` | D2.0-03 |
| 12 | **E-5 Image Analyzer** | CLIP MCP 래퍼 (V1=단건 분석, V2=배치 처리 — D2.0-03 §4 V2 구분) | `blue_nodes/content/` | D2.0-03 |
| 13 | **E-6 Z3 Solver** | Z3 제약 조건 풀기: `z3.Solver()` 기반, 입력=`ConstraintSet(variables, constraints)`, 출력=`SolverResult(sat/unsat, model)` | `blue_nodes/quant/` | D2.0-03 |
| 14 | **C-1~C-3** | Logic Verifier(논리식 검증)/Math Verifier(수식 검증, sympy)/Code Verifier(AST 분석+pytest 실행) — 각각 `BaseVerifier(ABC).verify(input) -> VerifyResult(passed, errors)` | `orange_core/` | D2.0-01 §5.10 |
| 15 | **D-1~D-2** | Think Engine, Multimodal Engine | `orange_core/` | D2.0-01 §5.11 |
| | **── v23 확장 ──** | | | |
| 16 | **중앙 프롬프트 라이브러리** | 중앙 프롬프트 라이브러리 [HIGH] | §6 참조 | v10 Phase 2 추가 (D205-025) | <!-- D205-025 v23 -->
| 17 | **작업 중단 복원 (task_checkpoint)** | 작업 중단 복원 (task_checkpoint) [HIGH] | §6 참조 | v10 Phase 2 추가 (D206-039) | <!-- D206-039 v23 -->
| 18 | **M-027 연구 노트 관리 (논문/인용)** | M-027 연구 노트 관리 (논문/인용) [HIGH] | §6.10 참조 (D206-198) <!-- S5-194 v26 --> | v10 Phase 2 추가 (D206-198) | <!-- D206-198 v23 -->
| 19 | **M-029 코드 스니펫 라이브러리** | M-029 코드 스니펫 라이브러리 [HIGH] | §6 참조 | v10 Phase 2 추가 (D206-199) | <!-- D206-199 v23 -->
| 20 | **M-031 아이디어 캡처 (성숙도 추적)** | M-031 아이디어 캡처 (성숙도 추적) [HIGH] | §6 참조 | v10 Phase 2 추가 (D206-200) | <!-- D206-200 v23 -->
| 21 | **M-045 지식 기반 의사결정 지원 (SWOT)** | M-045 지식 기반 의사결정 지원 (SWOT) [HIGH] | §6 참조 | v10 Phase 2 추가 (D206-217) | <!-- D206-217 v23 -->
| 22 | **M-046 지식 기반 글쓰기 지원** | M-046 지식 기반 글쓰기 지원 [HIGH] | §6 참조 | v10 Phase 2 추가 (D206-218) | <!-- D206-218 v23 -->
| 23 | **스트레스 관리 (호흡/그라운딩/명상)** | 스트레스 관리 (호흡/그라운딩/명상) [HIGH] | §6 참조 | v10 Phase 2 추가 (D207-175) | <!-- D207-175 v23 -->
| 24 | **CBT 셀프케어 (사고기록+인지왜곡)** | CBT 셀프케어 (사고기록+인지왜곡) [HIGH] | §6 참조 | v10 Phase 2 추가 (D207-178) | <!-- D207-178 v23 -->
| 25 | **번아웃 예방 (과도업무감지→중단)** | 번아웃 예방 (과도업무감지→중단) [HIGH] | §6 참조 | v10 Phase 2 추가 (D207-179) | <!-- D207-179 v23 -->
| | **── v23 확장: 금융/인프라 (HIGH) ──** | | | |
| 26 | **알림 규칙 엔진** | 알림 규칙 엔진 [HIGH] | §6.11 참조 (S7AE-549) <!-- S5-195 v26 --> | v10 Phase 2 추가 (S7AE-549) | <!-- S7AE-549 v23 -->
| 27 | **소셜 미디어 분석** | 소셜 미디어 분석 [HIGH] | §6.8 참조 (S7FI-283) <!-- S5-196 v26 --> | v10 Phase 2 추가 (S7FI-283) | <!-- S7FI-283 v23 --> | **L3**: `sot 2/Ai-investing-detail/02_behavioral-finance/news_sentiment.md` |
| 28 | **블랙-리터만 모델** | 블랙-리터만 모델 [HIGH] | §6 참조 | v10 Phase 2 추가 (S7FI-304) | <!-- S7FI-304 v23 -->
| 29 | **팩터 투자** | 팩터 투자 [HIGH] | §6 참조 | v10 Phase 2 추가 (S7FI-306) | <!-- S7FI-306 v23 -->
| 30 | **리밸런싱 엔진** | 리밸런싱 엔진 [HIGH] | §6.8 참조 (S7FI-307) <!-- S5-197 v26 --> | v10 Phase 2 추가 (S7FI-307) | <!-- S7FI-307 v23 --> | **L3**: `sot 2/Ai-investing-detail/15_portfolio-advanced/rebalancing.md` |
| | **── v23 확장: 미디어/지식도구 (HIGH) ──** | | | |
| 31 | **음성 품질 최적화** | 음성 품질 최적화 [HIGH] | §6.2 참조 (S7JM-030) <!-- S5-198 v26 --> | v10 Phase 2 추가 (S7JM-030) | <!-- S7JM-030 v23 -->
| 32 | **성능 프로파일링** | 성능 프로파일링 [HIGH] | §6.12.1 참조 (S7JM-189) <!-- S5-199 v26 --> | v10 Phase 2 추가 (S7JM-189) | <!-- S7JM-189 v23 -->
| 33 | **데이터베이스 관리 도구** | 데이터베이스 관리 도구 [HIGH] | §6.12 참조 (S7JM-201) <!-- S5-200 v26 --> | v10 Phase 2 추가 (S7JM-201) | <!-- S7JM-201 v23 -->
| 34 | **폴더/노트북 구조** | 폴더/노트북 구조 [HIGH] | §6.10 참조 (S7JM-243) <!-- S5-201 v26 --> | v10 Phase 2 추가 (S7JM-243) | <!-- S7JM-243 v23 -->
| 35 | **Zettelkasten 방법론 구현** | Zettelkasten 방법론 구현 [HIGH] | §6 참조 | v10 Phase 2 추가 (S7JM-244) | <!-- S7JM-244 v23 -->
| 36 | **지식 성숙도 추적** | 지식 성숙도 추적 [HIGH] | §6 참조 | v10 Phase 2 추가 (S7JM-247) | <!-- S7JM-247 v23 -->
| 37 | **스마트 리마인더** | 스마트 리마인더 [HIGH] | §6.11 참조 (S7JM-257) <!-- S5-202 v26 --> | v10 Phase 2 추가 (S7JM-257) | <!-- S7JM-257 v23 -->
| 38 | **지식 기반 의사결정 지원** | 지식 기반 의사결정 지원 [HIGH] | §6.10 참조 (S7JM-275) <!-- S5-203 v26 --> | v10 Phase 2 추가 (S7JM-275) | <!-- S7JM-275 v23 -->
| 39 | **지식 기반 글쓰기 지원** | 지식 기반 글쓰기 지원 [HIGH] | §6.10 참조 (S7JM-276) <!-- S5-204 v26 --> | v10 Phase 2 추가 (S7JM-276) | <!-- S7JM-276 v23 -->
| | **── v23 확장: 교육/학습/웰니스 (HIGH) ──** | | | |
| 40 | **폼 자동 입력** | 폼 자동 입력 [HIGH] | §6.1 참조 (S7NP-017) <!-- S5-205 v26 --> | v10 Phase 2 추가 (S7NP-017) | <!-- S7NP-017 v23 -->
| 41 | **플래시카드 자동 생성** | 플래시카드 자동 생성 [HIGH] | §6 참조 | v10 Phase 2 추가 (S7NP-047) | <!-- S7NP-047 v23 -->
| 42 | **간격 반복 (Spaced Repetition)** | 간격 반복 (Spaced Repetition) [HIGH] | §6 참조 | v10 Phase 2 추가 (S7NP-048) | <!-- S7NP-048 v23 -->
| 43 | **퀴즈 자동 생성** | 퀴즈 자동 생성 [HIGH] | §6.1 참조 (S7NP-049) <!-- S5-206 v26 --> | v10 Phase 2 추가 (S7NP-049) | <!-- S7NP-049 v23 -->
| 44 | **학습 진도 추적** | 학습 진도 추적 [HIGH] | §6.1 참조 (S7NP-050) <!-- S5-207 v26 --> | v10 Phase 2 추가 (S7NP-050) | <!-- S7NP-050 v23 -->
| 45 | **소크라테스식 대화** | 소크라테스식 대화 [HIGH] | §6.1 참조 (S7NP-052) <!-- S5-208 v26 --> | v10 Phase 2 추가 (S7NP-052) | <!-- S7NP-052 v23 -->
| 46 | **독서 관리** | 독서 관리 [HIGH] | §6.1 참조 (S7NP-061) <!-- S5-209 v26 --> | v10 Phase 2 추가 (S7NP-061) | <!-- S7NP-061 v23 -->
| 47 | **학습 목표 관리** | 학습 목표 관리 [HIGH] | §6.1 참조 (S7NP-062) <!-- S5-210 v26 --> | v10 Phase 2 추가 (S7NP-062) | <!-- S7NP-062 v23 -->
| 48 | **마이크로러닝** | 마이크로러닝 [HIGH] | §6.1 참조 (S7NP-063) <!-- S5-211 v26 --> | v10 Phase 2 추가 (S7NP-063) | <!-- S7NP-063 v23 -->
| 49 | **학습 동기 부여** | 학습 동기 부여 [HIGH] | §6.1 참조 (S7NP-064) <!-- S5-212 v26 --> | v10 Phase 2 추가 (S7NP-064) | <!-- S7NP-064 v23 -->
| 50 | **스트레스 관리 도우미** | 스트레스 관리 도우미 [HIGH] | §6.1 참조 (S7NP-083) <!-- S5-213 v26 --> | v10 Phase 2 추가 (S7NP-083) | <!-- S7NP-083 v23 -->
| 51 | **습관 추적기** | 습관 추적기 [HIGH] | §6.1 참조 (S7NP-088) <!-- S5-214 v26 --> | v10 Phase 2 추가 (S7NP-088) | <!-- S7NP-088 v23 -->
| 52 | **일기 작성 도우미** | 일기 작성 도우미 [HIGH] | §6.1 참조 (S7NP-089) <!-- S5-215 v26 --> | v10 Phase 2 추가 (S7NP-089) | <!-- S7NP-089 v23 -->
| 53 | **긍정 심리 코칭** | 긍정 심리 코칭 [HIGH] | §6.1 참조 (S7NP-093) <!-- S5-216 v26 --> | v10 Phase 2 추가 (S7NP-093) | <!-- S7NP-093 v23 -->
| 54 | **목표 설정/추적** | 목표 설정/추적 [HIGH] | §6.1 참조 (S7NP-094) <!-- S5-217 v26 --> | v10 Phase 2 추가 (S7NP-094) | <!-- S7NP-094 v23 -->
| 55 | **집중 모드 (포모도로)** | 집중 모드 (포모도로) [HIGH] | §6.1 참조 (S7NP-096) <!-- S5-218 v26 --> | v10 Phase 2 추가 (S7NP-096) | <!-- S7NP-096 v23 -->
| 56 | **웰니스 알림** | 웰니스 알림 [HIGH] | §6.1 참조 (S7NP-105) <!-- S5-219 v26 --> | v10 Phase 2 추가 (S7NP-105) | <!-- S7NP-105 v23 -->
| 57 | **번아웃 예방** | 번아웃 예방 [HIGH] | §6.1 참조 (S7NP-109) <!-- S5-220 v26 --> | v10 Phase 2 추가 (S7NP-109) | <!-- S7NP-109 v23 -->
| 58 | **대화 분기 관리** | 대화 분기 관리 [HIGH] | §6.1 참조 (S7NP-142) <!-- S5-221 v26 --> | v10 Phase 2 추가 (S7NP-142) | <!-- S7NP-142 v23 -->
| | **── v23 확장: MEDIUM ──** | | | |
| 59 | **공감 대화 엔진 (Carl Rogers)** | 공감 대화 엔진 (Carl Rogers) [MEDIUM] | §6.1 참조 (D207-176) <!-- S5-222 v26 --> | v10 Phase 2 추가 (D207-176) | <!-- D207-176 v23 -->

> **V1 Phase 3 적용 LOCK/FREEZE 값**:
> - LangGraph 5-Phase 순서: Intake→Plan→Execute→Verify→Deliver (D2.0-05 §4 LOCK)
> - Soft Loop: 최대 1회 자동 재시도 (D2.0-05 §4.2 LOCK)
> - Circuit Breaker: failure_threshold=3, recovery_time_sec=60 (D2.0-05 §4.4 LOCK)
> - A-1 Failover: GPT-4o→Claude→Ollama, 3회 타임아웃 시 전환 (LOCK)
> - Agent Teams V1: max 2 Sub-Agent (LOCK-AT-014 V1)
> - **단순 제어 흐름 원칙**: LangGraph는 워크플로우 오케스트레이션(StateGraph 노드 전이)에만 사용. 개별 모듈 내부 로직은 함수 호출/if-else/while 루프로 구현. StateGraph 중첩 금지 (에반 #01 기반) <!-- v24 메이커에반 개선안 5 -->

### 단계 완료 검증 (V1-Phase 3 → Phase 4 전환 조건)

| # | 검증 항목 | 확인 방법 | 필수 |
|---|----------|----------|:---:|
| 1 | LangGraph 5-Phase 완성 | Intake→Plan→Execute→Verify→Deliver 전체 동작 + 조건부 분기 | ✅ |
| 2 | Gate 통합 노드 | LangGraph 노드에서 5-Gate 실행 결과 기반 라우팅 동작 | ✅ |
| 3 | Soft/Hard Loop | 검증 실패 → 1회 자동 재시도(Soft) → HITL 승인(Hard) 동작 | ✅ |
| 4 | Circuit Breaker | closed/open/half_open 전이 + failure_threshold=3 + recovery_time=60s | ✅ |
| 5 | A-1 MultiBrain Adapter | Ollama + GPT-4o-mini 통합 호출 + Failover(GPT-4o→Claude→Ollama) 동작 | ✅ |
| 6 | Agent Teams V1 | Lead + 2 Sub-Agent + Sequential/Parallel 패턴 실행 확인 | ✅ |
| 7 | E-1~E-6 Blue Node | Coding/Web Search/Doc Parser/Code Executor/Image Analyzer/Z3 동작 확인 | ✅ |
| 8 | C-1~C-3 Verifier | Logic/Math/Code Verifier 동작 확인 | ✅ |
| 9 | D-1~D-2 Engine | Think Engine + Multimodal Engine 동작 확인 | ✅ |
| 10 | 위임 깊이 제한 | 최대 2단계 (LOCK-AT-004 config 제한) 초과 시 차단 확인 | ✅ |
| 11 | A-2 Preset Modularization | 프리셋 등록/조회/적용 동작 확인 | ✅ |

> ⛔ 위 필수 항목 전체 통과 전 Phase 4 진입 금지

---

## V1-Phase 4: UI/UX (Week 13-14)

### 실행 가이드
> **AI 프롬프트 요약**: "V1-Phase 4 UI/UX를 구현하세요. Tauri+React 3-Column Layout, Builder/Hologram/CLI View, 44개 컴포넌트, 8개 Custom Hook, 7개 Store를 구현합니다. §6.1 UI/UX 상세를 참조하세요."
>
> **참조 SOT 문서** (MUST 로드):
> - `D2.0-08` (UI/UX 정본) — 레이아웃, 컴포넌트, 테마
> - `PHASE_B2_PROJECT_STRUCTURE.md` — frontend/ 디렉토리 구조
> - `§6.1` (본 문서) — React 컴포넌트 44개 목록, Hook/Store 상세
>
> **Phase 고유 규칙**: R1~R11 + ORANGE(#FF6B35)/BLUE(#4A90D9) 테마 LOCK + 다크모드 기본 + 접근성(WCAG 2.1 AA)

#### AI 프롬프트

````text
[VAMOS V1-Phase 4] UI/UX 구현

■ 작업 목표
Tauri+React 3-Column Layout 기반 Builder/Hologram View, 7개 페이지,
~44개 React 컴포넌트, 8개 Custom Hook, 7개 Zustand Store, i18n, 디자인 시스템,
CLI Interface를 구현합니다.

■ MUST 로드 SOT
- D2.0-08 (UI/UX 정본) — 레이아웃, 컴포넌트, 테마
- PHASE_B2_PROJECT_STRUCTURE.md — frontend/ 디렉토리 구조
- PART2 §6.1 — React 컴포넌트 44개 목록, Hook/Store 상세

■ 구현 항목 (16 core + 3 v23)

[레이아웃 — frontend/src/components/layout/]
1. 3-Column Fluid Layout: 좌(250-300px)/중앙(flex)/우(350-400px) 리사이즈
   - CSS Grid/Flex 기반, 반응형 브레이크포인트
2. Builder View (Cockpit): 리소스 트리 + 워크플로우 그래프 + 로그/승인/비용 패널
   - D2.0-08 §2.1 정본
3. Hologram View: 타임라인 + 스트리밍 캔버스 + Glass HUD
   - D2.0-08 §2.2 정본

[7개 페이지 — frontend/src/pages/]
4. DashboardPage.tsx: 프로젝트 개요, 최근 세션, 시스템 상태
5. ChatPage.tsx: Hologram View 채팅, 스트리밍, 아티팩트
6. WorkflowPage.tsx: Builder View 그래프 시각화
7. MemoryPage.tsx: L0/L1 탐색기, 마스킹 미리보기
8. SettingsPage.tsx: 설정 편집기, 테마, 언어
9. LogPage.tsx: 로그/감사 뷰어
10. NodeDetailPage.tsx: BLUE NODE 상세 상태/실행 결과

[React 컴포넌트 — frontend/src/components/]
11. ~44개 컴포넌트: Decision/Chat/Approval/Cost/Evidence/Memory/Flow/Input 등
    - §6.1.2 컴포넌트 레지스트리 참조, D2.0-08 §10.4 정본

[Hooks & Stores — frontend/src/hooks/, stores/]
12. Custom Hooks 8개: useTauriIPC, useDecision, useWorkflow,
    useNotification, useAuth, useMemory, useCost, useStreaming
    - §6.1.3 참조
13. Zustand Stores 7개: app/decision/cost/notification/auth/memory/workflow
    - PHASE_B2 §3.1 정본 (agent→notification, config→auth)

[기반 시스템]
14. i18n 국제화: react-i18next, ko-KR/en-US 리소스 파일
    - frontend/src/ i18n config
15. 디자인 시스템: CSS Custom Properties (ORANGE #FF6B35 / BLUE #4A90D9)
    - frontend/src/styles/, 다크모드 기본, WCAG 2.1 AA 접근성
16. CLI Interface: vamos run/approve/status/cost/memory/policy (6개 명령어)
    - backend/vamos_core/ CLI 진입점, D2.0-08 §2.3

[v23 확장 3건 — LOW 우선순위]
17. 마인드맵 자동 생성 (S7JM-058)
18. 온보딩 마법사 (S7JM-217)
19. 키보드 내비게이션 (S7NP-151)

■ LOCK 값 (이 Phase에서 반드시 준수)
- ORANGE=#FF6B35, BLUE=#4A90D9 (테마 색상 불변)
- 다크모드 기본 (Light 모드는 토글 선택)
- 3-Column 좌=250-300px, 우=350-400px, 중앙=flex
- WCAG 2.1 AA 접근성 준수
- CLI 명령어: run/approve/status/cost/memory/policy (6개 고정)
- UI 9-State SM: UI_S0_BOOT→UI_S1_IDLE→...→UI_S8_ARCHIVED
- RBAC: OWNER/ADMIN/OPERATOR/VIEWER 4단계

■ 검증 체크리스트
□ 3-Column Fluid Layout 리사이즈 동작
□ Builder View + Hologram View 렌더링
□ 7개 페이지 접근 가능 (라우팅 확인)
□ ~44개 React 컴포넌트 렌더링
□ 8개 Custom Hook 정상 동작
□ 7개 Zustand Store 상태 관리 동작
□ i18n ko-KR ↔ en-US 전환 확인
□ CSS Custom Properties 테마 + 다크모드 전환
□ CLI 6개 명령어 동작
□ UI 9-State SM 전이 동작
□ RBAC 접근 제어 (4단계 권한 분리)
□ WCAG 2.1 AA 접근성 검증
````

### 구현 항목

| # | 항목 | 구현 내용 | 파일경로 | 산출물 참조 |
|---|------|----------|---------|-----------|
| 1 | **3-Column Fluid Layout** | 좌(250-300px)/중앙(flex)/우(350-400px) | `components/layout/` | D2.0-08 §2.1/§3 | <!-- Phase 2-A FIX-07: §4는 UI State Machine. 레이아웃 정본=§2.1(Builder/Hologram View), §3(3-Column) -->
| 2 | **Builder View (Cockpit)** | 리소스 트리 + 워크플로우 그래프 + 로그/승인/비용 패널 | `components/layout/` | D2.0-08 §2.1 | <!-- Phase 2-A FIX-07 -->
| 3 | **Hologram View** | 타임라인 + 스트리밍 캔버스 + Glass HUD | `components/layout/` | D2.0-08 §2.2 | <!-- Phase 2-A FIX-07 -->
| 4 | **Dashboard 페이지** | 프로젝트 개요, 최근 세션, 시스템 상태 | `pages/DashboardPage.tsx` | D2.0-08 §6 |
| 5 | **Chat 페이지** | Hologram View 채팅, 스트리밍, 아티팩트 | `pages/ChatPage.tsx` | D2.0-08 §6 |
| 6 | **Workflow 페이지** | Builder View 그래프 시각화 | `pages/WorkflowPage.tsx` | D2.0-08 §6 |
| 7 | **Memory 페이지** | L0/L1 탐색기, 마스킹 미리보기 | `pages/MemoryPage.tsx` | D2.0-08 §6 |
| 8 | **Settings 페이지** | 설정 편집기, 테마, 언어 | `pages/SettingsPage.tsx` | D2.0-08 §6 |
| 9 | **Log 페이지** | 로그/감사 뷰어 | `pages/LogPage.tsx` | PHASE_B2 §3.1 |
| 10 | **NodeDetail 페이지** | BLUE NODE 상세 상태/실행 결과 | `pages/NodeDetailPage.tsx` | PHASE_B2 §3.1 |
| 11 | **React 컴포넌트 ~44개** | Decision/Chat/Approval/Cost/Evidence/Memory/Flow/Input 등 | `components/` (§6.1.2 참조) | D2.0-08 §10.4 | <!-- Phase 2-A FIX-08: §7=Failure/Fallback. 컴포넌트 레지스트리 정본=§10.4 -->
| 12 | **Custom Hooks 8개** | useTauriIPC, useDecision, useWorkflow 등 | `hooks/` (§6.1.3 참조) | CLAUDE.md §14, PHASE_B2 | <!-- SOURCE_CONFLICT: PART2 기존="D2.0-08" vs 실제 유래=CLAUDE.md §14/PHASE_B2. 출처 정정 -->
| 13 | **Zustand Stores 7개** | app/decision/cost/notification/auth/memory/workflow | `stores/` (§6.1.3 참조) | CLAUDE.md §14, PHASE_B2 | <!-- SOURCE_CONFLICT: PART2 기존="D2.0-08" vs 실제 유래=CLAUDE.md §14/PHASE_B2. 출처 정정. v11.0.0: agent→notification, config→auth (PHASE_B2 §3.1 정본) -->
| 14 | **i18n 국제화** | react-i18next, ko-KR/en-US | `src/` (i18n config) | D2.0-08 |
| 15 | **디자인 시스템** | CSS Custom Properties (ORANGE/BLUE 테마) | `styles/` | D2.0-08 §10 |
| 16 | **CLI Interface** | `vamos run/approve/status/cost/memory/policy` | `backend/vamos_core/` (CLI 진입점) | D2.0-08 §2.3 | <!-- Phase 2-A FIX-09: policy 추가(D2.0-08 §2.3.1: 6개 commands). §6.1.1과 동기화 -->
| 17 | **마인드맵 자동 생성** | 마인드맵 자동 생성 [LOW] | §6.1 참조 (S7JM-058) <!-- S5-223 v26 --> | v10 Phase 2 추가 (S7JM-058) | <!-- S7JM-058 v23 -->
| 18 | **온보딩 마법사** | 온보딩 마법사 [LOW] | §6.1 참조 (S7JM-217) <!-- S5-224 v26 --> | v10 Phase 2 추가 (S7JM-217) | <!-- S7JM-217 v23 -->
| 19 | **키보드 내비게이션** | 키보드 내비게이션 [LOW] | §6.1 참조 (S7NP-151) <!-- S5-225 v26 --> | v10 Phase 2 추가 (S7NP-151) | <!-- S7NP-151 v23 -->
| | **── v12 BLOCKER 추가 ──** | | | | <!-- v12_BLOCKER v26 -->
| 20 | **사용자 피드백 수집 시스템** | 인앱 피드백 위젯(thumbs up/down + 자유 텍스트), 만족도 추적(NPS/CSAT), 피드백 분류(카테고리 자동 태깅), 개선 제안 수집→분석→우선순위화 루프, 대시보드(트렌드/빈도) [BLOCKER] | `components/FeedbackWidget.tsx` + `backend/feedback/` | §6.1 참조 | <!-- v12_C13_034 v26 -->

### 단계 완료 검증 (V1-Phase 4 → Phase 5 전환 조건)

| # | 검증 항목 | 확인 방법 | 필수 |
|---|----------|----------|:---:|
| 1 | 3-Column Fluid Layout | 좌(250-300px)/중앙(flex)/우(350-400px) 리사이즈 동작 | ✅ |
| 2 | Builder View | 리소스 트리 + 워크플로우 그래프 + 로그/승인/비용 패널 렌더링 | ✅ |
| 3 | Hologram View | 타임라인 + 스트리밍 캔버스 + Glass HUD 렌더링 | ✅ |
| 4 | 7개 페이지 렌더링 | Dashboard/Chat/Workflow/Memory/Settings/Log/NodeDetail 접근 가능 | ✅ |
| 5 | ~44개 React 컴포넌트 | Decision/Chat/Approval/Cost/Evidence/Memory/Node/Input 등 렌더링 | ✅ |
| 6 | 8 Custom Hooks | useTauriIPC, useDecision, useWorkflow 등 8개 Hook 정상 동작 | ✅ |
| 7 | 7 Zustand Stores | app/decision/cost/notification/auth/memory/workflow Store 상태 관리 | ✅ |
| 8 | i18n 국제화 | ko-KR ↔ en-US 언어 전환 동작 확인 | ✅ |
| 9 | CLI Interface | `vamos run/approve/status/cost/memory/policy` 6개 명령어 동작 | ✅ |
| 10 | UI 9-State SM | UI_S0_BOOT → UI_S1_IDLE → ... → UI_S8_ARCHIVED 전이 동작 | ✅ |
| 11 | RBAC 접근 제어 | OWNER 전체/ADMIN 삭제 불가/OPERATOR Settings 읽기전용/VIEWER 조회만 | ✅ |
| 12 | 디자인 시스템 | CSS Custom Properties (ORANGE/BLUE 테마) 적용 + 다크모드 전환 확인 | ✅ |

> ⛔ 위 필수 항목 전체 통과 전 Phase 5 진입 금지

---

## V1-Phase 5: Integration + Test (Week 15-16)

### 실행 가이드
> **AI 프롬프트 요약**: "V1-Phase 5 통합 테스트를 수행하세요. §6.3 테스트 ~85개(Unit+Integration+E2E), §6.4 CI/CD 파이프라인 설정, 크로스 플랫폼 빌드(Win/Mac/Linux)를 완성합니다."
>
> **참조 SOT 문서** (MUST 로드):
> - `PHASE_B5_TEST_STRATEGY.md` — 테스트 전략 정본, AC 매핑
> - `PHASE_B6_CICD.md` — CI/CD 파이프라인 정본
> - `§6.3` (본 문서) — 테스트 유형/파일 수/커버리지 목표
> - `§6.4` (본 문서) — CI 워크플로우 14개
>
> **Phase 고유 규칙**: R1~R11 + 커버리지 80%+ (Python/Rust/React) + E2E core 100% + P0 테스트 전수 통과

#### AI 프롬프트

````text
[VAMOS V1-Phase 5] Integration + Test

■ 작업 목표
E2E 파이프라인 테스트, IPC 브릿지 통합, 5-Gate 전경로 검증,
Python/Rust/React 단위 테스트(~85개), CI/CD 파이프라인 완성,
커버리지 80%+ 달성, 보안 감사를 수행합니다.

■ MUST 로드 SOT
- PHASE_B5_TEST_STRATEGY.md — 테스트 전략 정본, AC 매핑
- PHASE_B6_CICD.md — CI/CD 파이프라인 정본
- PART2 §6.3 — 테스트 유형/파일 수/커버리지 목표
- PART2 §6.4 — CI 워크플로우 14개

■ 구현 항목 (12 core + 3 v23)

[E2E & 통합 테스트 — e2e/, backend/tests/integration/]
1. E2E 파이프라인 테스트: 전체 S0→S8 흐름 검증
   - Playwright 기반, 9-State 전이 전수 커버
2. IPC 브릿지 테스트: React ↔ Rust ↔ Python 3계층 통합
   - Tauri IPC invoke/listen 양방향 검증
3. Gate 검증 테스트: 5-Gate 모든 경로 (deny/allow/downshift/hold)
   - Policy→Approval→Cost→Evidence→SelfCheck 순서 LOCK
4. Cost 시뮬레이션: 80% 경고, 100% 차단 검증
   - Budget Threshold 경계값 테스트
5. Approval 워크플로우: P1/P2 승인 흐름 + 타임아웃(10분)
   - HITL 인터페이스 통합 검증

[단위 테스트]
6. Python Unit Tests (~45개): pytest
   - backend/tests/unit/, 커버리지 80%+
7. Rust Unit Tests (~8개): cargo test
   - src-tauri/src/ 인라인 테스트, 커버리지 80%+
8. React Unit Tests (~15개): vitest
   - frontend/src/**/*.test.tsx, 커버리지 80%+
9. E2E Tests (~8개): Playwright
   - e2e/, 채팅/다운시프트/HITL/Guardrails 등 핵심 시나리오

[CI/CD & 보안 — .github/workflows/]
10. Coverage 달성: Python 80%+, Rust 80%+, React 80%+
11. CI/CD 완성: 3-언어 quality + test + build 워크플로우
    - §6.4 CI 워크플로우 14개 참조
12. 보안 감사: pip-audit + cargo-audit + npm audit
    - CRITICAL 0건 필수

[v23 확장 3건]
13. FileOwnership 모델 구현 — writable/readonly/forbidden (TEAM-091) [HIGH]
14. 그레이스풀 셧다운 (S7AE-366) [MEDIUM]
15. 커넥션 풀링 (S7AE-389) [MEDIUM]

■ LOCK 값 (이 Phase에서 반드시 준수)
- 커버리지 임계값: Python 80%+, Rust 80%+, React 80%+
- E2E core 시나리오 100% PASS 필수
- P0 테스트 전수 통과 필수 (0 failure)
- 5-Gate 순서: Policy→Approval→Cost→Evidence→SelfCheck
- Cost 경고: 80%, 차단: 100%
- Approval 타임아웃: 10분
- CI/CD: 3-언어 (Python/Rust/React) 통합 파이프라인

■ 검증 체크리스트
□ E2E S0→S8 전체 흐름 Playwright 테스트 PASS
□ IPC 브릿지 React↔Rust↔Python 통합 PASS
□ 5-Gate 전경로 deny/allow/downshift/hold PASS
□ Cost 80% 경고 + 100% 차단 동작 검증
□ Approval P1/P2 + 10분 타임아웃 PASS
□ Python pytest ~45개 + 커버리지 80%+
□ Rust cargo test ~8개 + 커버리지 80%+
□ React vitest ~15개 + 커버리지 80%+
□ Playwright E2E ~8개 PASS
□ CI/CD 3-언어 워크플로우 정상 동작
□ 보안 감사 CRITICAL 0건
````

### 구현 항목

| # | 항목 | 구현 내용 | 파일경로 | 산출물 참조 |
|---|------|----------|---------|-----------|
| 1 | **E2E 파이프라인 테스트** | 전체 S0→S8 흐름 검증 | `e2e/` | PHASE_B5 |
| 2 | **IPC 브릿지 테스트** | React ↔ Rust ↔ Python 통합 | `backend/tests/integration/` | PHASE_B5 |
| 3 | **Gate 검증 테스트** | 5-Gate 모든 경로 (deny/allow/downshift/hold) | `backend/tests/integration/` | PHASE_B5 |
| 4 | **Cost 시뮬레이션** | 80% 경고, 100% 차단 검증 | `backend/tests/integration/` | PHASE_B5 |
| 5 | **Approval 워크플로우** | P1/P2 승인 흐름 + 타임아웃 | `backend/tests/integration/` | PHASE_B5 |
| 6 | **Python Unit Tests** | ~45개 (pytest) | `backend/tests/unit/` | PHASE_B5 |
| 7 | **Rust Unit Tests** | ~8개 (cargo test) | `src-tauri/src/` (인라인) | PHASE_B5 |
| 8 | **React Unit Tests** | ~15개 (vitest) | `frontend/src/**/*.test.tsx` | PHASE_B5 |
| 9 | **E2E Tests** | ~8개 (Playwright) | `e2e/` | PHASE_B5 |
| 10 | **Coverage 달성** | Python 80%+, Rust 80%+, React 80%+ | — | PHASE_B5 <!-- RESOLVED: PHASE_B6 v1.0.2 PH-11 기준 적용. Rust 60%→80%, React 70%→80%. Phase 1에서 통일 완료. --> |
| 11 | **CI/CD 완성** | 3-언어 quality + test + build | `.github/workflows/` | PHASE_B6 |
| 12 | **보안 감사** | pip-audit, cargo-audit, npm audit | `.github/workflows/` | PHASE_B6 |
| 13 | **FileOwnership 모델 구현 (writable/readonly/forbidden 경** | FileOwnership 모델 구현 (writable/readonly/forbidden 경 [HIGH] | §6.5 참조 (TEAM-091) <!-- S5-226 v26 --> | v10 Phase 2 추가 (TEAM-091) | <!-- TEAM-091 v23 -->
| 14 | **그레이스풀 셧다운** | 그레이스풀 셧다운 [MEDIUM] | §6.2.3 참조 (S7AE-366) <!-- S5-227 v26 --> | v10 Phase 2 추가 (S7AE-366) | <!-- S7AE-366 v23 -->
| 15 | **커넥션 풀링** | 커넥션 풀링 [MEDIUM] | §6.2.3 참조 (S7AE-389) <!-- S5-228 v26 --> | v10 Phase 2 추가 (S7AE-389) | <!-- S7AE-389 v23 -->

### 단계 완료 검증 (V1-Phase 5 → Phase 6 전환 조건)

| # | 검증 항목 | 확인 방법 | 필수 |
|---|----------|----------|:---:|
| 1 | E2E S0→S8 흐름 | 전체 상태 전이 흐름 Playwright 테스트 PASS | ✅ |
| 2 | IPC 브릿지 통합 | React ↔ Rust ↔ Python 3계층 통합 테스트 PASS | ✅ |
| 3 | 5-Gate 전경로 | deny/allow/downshift/hold 모든 경로 테스트 PASS | ✅ |
| 4 | Cost 시뮬레이션 | 80% 경고 + 100% 차단 동작 검증 PASS | ✅ |
| 5 | Approval 워크플로우 | P1/P2 승인 흐름 + 10분 타임아웃 테스트 PASS | ✅ |
| 6 | Python 커버리지 | pytest ~45개 + 커버리지 80%+ 달성 | ✅ |
| 7 | Rust 커버리지 | cargo test ~8개 + 커버리지 80%+ 달성 | ✅ |
| 8 | React 커버리지 | vitest ~15개 + 커버리지 80%+ 달성 | ✅ |
| 9 | E2E Tests | Playwright ~8개 PASS (채팅, 다운시프트, HITL, Guardrails 등) | ✅ |
| 10 | CI/CD 완성 | 3-언어 quality + test + build 워크플로우 정상 동작 | ✅ |
| 11 | 보안 감사 | pip-audit + cargo-audit + npm audit 전체 PASS (CRITICAL 0건) | ✅ |

> ⛔ 위 필수 항목 전체 통과 전 Phase 6 진입 금지

---

## V1-Phase 6: AI Investing MVP + MCP (Week 13-16, Phase 4-5와 병렬)

### 실행 가이드
> **AI 프롬프트 요약**: "V1-Phase 6 AI Investing MVP + MCP를 구현하세요. §6.8 AI Investing(포트폴리오, Circuit Breaker), §6.6 MCP 서버/클라이언트 7개, E-15 Cloud Collector를 구현합니다. Phase 4-5와 병렬 진행."
>
> **참조 SOT 문서** (MUST 로드):
> - `D2.0-03` §1+§3.3 (BLUE NODE P2 라이프사이클) + `VAMOS_AI_INVESTING_SPEC` (AI Investing 정본) <!-- CORRECTED 2026-03-22: 기존 D2.0-01 §5.9 → D2.0-03 §1+§3.3 -->
> - `§6.8` (본 문서) — AI Investing 상세
> - `§6.6` (본 문서) — MCP 서버/클라이언트 목록
> - `VAMOS_CLOUD_LIBRARY_SPEC` — E-15, RT-BNP V1
> - `sot 2/1-2_Auxiliary-Modules/` (S-1 Self-check Engine 구현 상세 정본)
>
> **Phase 고유 규칙**: R1~R11 + MCP Streamable HTTP 사용 + Circuit Breaker 속보 트리거 연동 + 비용 ₩40,000/월 LOCK 최종 확인

#### AI 프롬프트

````text
[VAMOS V1-Phase 6] AI Investing MVP + MCP

■ 작업 목표
Paper Trading MVP, RSI_BB 전략, 5-Agent Pipeline, 법적 컴플라이언스,
MCP Bridge/Server/Client, S-1 Self-check Engine을 구현합니다.
Phase 4-5와 병렬 진행됩니다.

■ MUST 로드 SOT
- D2.0-03 §1+§3.3 — BLUE NODE P2 라이프사이클 + VAMOS_AI_INVESTING_SPEC — AI Investing 정본 <!-- CORRECTED 2026-03-22: 기존 D2.0-01 §5.9 → D2.0-03 §1+§3.3 -->
- PART2 §6.8 — AI Investing 상세
- PART2 §6.6 — MCP 서버/클라이언트 7개 목록
- VAMOS_CLOUD_LIBRARY_SPEC — E-15, RT-BNP V1
- D2.0-03 §6 — MCP 프로토콜 정본

■ 구현 항목 (8 core + 3 v23)

[AI Investing — backend/vamos_core/blue_nodes/trading/]
1. Paper Trading MVP: 시뮬레이션 트레이딩 (51% Gate 파라미터)
   - 실제 매매 X, 가상 주문/체결/포지션 관리
2. RSI_BB 전략: RSI + Bollinger Bands 유일한 구현 완료 전략 활용
   - 백테스트 실행 가능 상태로 구현
3. 5-Agent Pipeline: Perplexity→Gemini→ChatGPT→Claude→Copilot
   - 순차 호출, 각 에이전트 결과 합산/투표
   - agent/ 디렉토리와 연동
4. 법적 컴플라이언스: Wash Sale, PDT, Uptick Rule 감지
   - 위반 시 자동 차단, 감사 로그 기록

[MCP — backend/vamos_core/mcp/]
5. MCP Bridge Layer: Streamable HTTP 클라이언트
   - mcp/bridge.py, SSE 기반 양방향 통신
   - MCPBridge.connect(url) -> MCPSession
6. MCP Server: VAMOS 자체 도구 노출 (20+ V1 tools)
   - mcp/server.py + mcp/tool_discovery.py
   - I-10 Tool Registry 기반, MCP Tool Discovery 프로토콜
   - 도구 목록: §6.2.1 IPC 핸들러 + Blue Node 전체
7. MCP Client: 외부 서버 연결 (Tavily, E2B 등)
   - mcp/client.py
   - MCPClient.call_tool(server_url, tool_name, params) -> ToolResult
   - 인증 토큰 관리

[ORANGE CORE — backend/vamos_core/orange_core/]
8. S-1 Self-check Engine: ORANGE CORE Self-check 실행
   - I-6 출력 수집 → QoD 점수 기반 시스템 상태 평가
   - 이상 감지 시 I-25(SDAR) 트리거

[v23 확장 3건 — LOW 우선순위]
9. 투자 교육 특화 (S7NP-057)
10. 투자 심리 분석 (S7NP-108)
11. 감정적 투자 방지 (S7NP-110)

■ LOCK 값 (이 Phase에서 반드시 준수)
- MCP: Streamable HTTP 사용 (WebSocket 아님)
- Circuit Breaker: 속보 트리거 연동 (뉴스 이벤트 시 자동 차단)
- 비용: ₩40,000/월 LOCK (V1 전체 운영비)
- 51% Gate: Paper Trading 진입 파라미터
- 5-Agent 순서: Perplexity→Gemini→ChatGPT→Claude→Copilot (고정)
- Wash Sale/PDT/Uptick Rule: 법적 컴플라이언스 3종 필수
- QoD ≥ 0.85: Self-check 임계값 (30일 기준)

■ 검증 체크리스트
□ Paper Trading 시뮬레이션 실행 + 51% Gate 동작
□ RSI_BB 전략 백테스트 실행 확인
□ 5-Agent Pipeline 순차 실행 동작
□ Wash Sale/PDT/Uptick Rule 감지 동작
□ MCP Bridge Streamable HTTP 통신 동작
□ MCP Server 20+ tools 노출 확인
□ MCP Client 외부 서버 연결 + 도구 호출 동작
□ S-1 Self-check QoD 평가 + SDAR 트리거
□ V1 완료 체크리스트 전수 통과
□ V1→V2 전환 조건 충족 확인
````

### 구현 항목

| # | 항목 | 구현 내용 | 파일경로 | 산출물 참조 |
|---|------|----------|---------|-----------|
| 1 | **Paper Trading MVP** | 시뮬레이션 트레이딩 (51% Gate) | `blue_nodes/trading/` | VAMOS_AI_INVESTING_SPEC |
| 2 | **RSI_BB 전략** | 유일한 구현 완료 전략 활용 | `blue_nodes/trading/` | sot 2/Ai-investing-detail/20_strategy-detail/technical/rsi_bb.md <!-- 기존: VAMOS_AI_INVESTING_SPEC §9 → MIGRATED to sot 2/ (Phase 1 Step 1-12) --> |
| 3 | **5-Agent Pipeline** | Perplexity→Gemini→ChatGPT→Claude→Copilot | `blue_nodes/trading/` + `agent/` | VAMOS_AI_INVESTING_SPEC |
| 4 | **법적 컴플라이언스** | Wash Sale, PDT, Uptick Rule 감지 | `blue_nodes/trading/` | VAMOS_AI_INVESTING_SPEC |
| 5 | **MCP Bridge Layer** | Streamable HTTP 클라이언트: SSE 기반 양방향 통신, `MCPBridge.connect(url) -> MCPSession` | `mcp/bridge.py` | D2.0-03 §6 |
| 6 | **MCP Server** | VAMOS 자체 도구 노출 (20+ V1 tools): I-10 Tool Registry 기반, MCP Tool Discovery 프로토콜 구현. 도구 목록은 §6.2.1 IPC 핸들러 + Blue Node 전체 | `mcp/server.py` + `mcp/tool_discovery.py` | D2.0-03 §6.4 |
| 7 | **MCP Client** | 외부 서버 연결 (Tavily, E2B 등): `MCPClient.call_tool(server_url, tool_name, params) -> ToolResult`, 인증 토큰 관리 | `mcp/client.py` | D2.0-03 §6.4.2 |
| 8 | **S-1 Self-check Engine** | ORANGE CORE Self-check 실행: I-6 출력 수집 → QoD 점수 기반 시스템 상태 평가 → 이상 감지 시 I-25(SDAR) 트리거 | `orange_core/` | D2.0-01 §5.7 |
| 9 | **투자 교육 특화** | 투자 교육 특화 [LOW] | §6.8 참조 (S7NP-057) <!-- S5-229 v26 --> | v10 Phase 2 추가 (S7NP-057) | <!-- S7NP-057 v23 --> | **L3**: `sot 2/Ai-investing-detail/17_explainability/adaptive_explanation.md` |
| 10 | **투자 심리 분석** | 투자 심리 분석 [LOW] | §6.8 참조 (S7NP-108) <!-- S5-230 v26 --> | v10 Phase 2 추가 (S7NP-108) | <!-- S7NP-108 v23 --> | **L3**: `sot 2/Ai-investing-detail/02_behavioral-finance/market_sentiment.md` |
| 11 | **감정적 투자 방지** | 감정적 투자 방지 [LOW] | §6.8 참조 (S7NP-110) <!-- S5-231 v26 --> | v10 Phase 2 추가 (S7NP-110) | <!-- S7NP-110 v23 --> | **L3**: `sot 2/Ai-investing-detail/02_behavioral-finance/emotional_trading_prevention.md` |

### 단계 완료 검증 (V1-Phase 6 → V2 진입 전환 조건)

| # | 검증 항목 | 확인 방법 | 필수 |
|---|----------|----------|:---:|
| 1 | Paper Trading MVP | 시뮬레이션 트레이딩 실행 + 51% Gate 파라미터 검증 동작 | ✅ |
| 2 | RSI_BB 전략 | RSI + Bollinger Bands 전략 백테스트 실행 확인 | ✅ |
| 3 | 5-Agent Pipeline | Perplexity→Gemini→ChatGPT→Claude→Copilot 순차 실행 | ✅ |
| 4 | 법적 컴플라이언스 | Wash Sale/PDT/Uptick Rule 감지 동작 확인 | ✅ |
| 5 | MCP Bridge Layer | Streamable HTTP 클라이언트 통신 동작 | ✅ |
| 6 | MCP Server | VAMOS 자체 도구 20+ tools MCP 노출 확인 | ✅ |
| 7 | MCP Client | 외부 MCP 서버 (Tavily, E2B 등) 연결 + 도구 호출 동작 | ✅ |
| 8 | S-1 Self-check Engine | ORANGE CORE Self-check 실행 동작 확인 | ✅ |
| 9 | V1 완료 체크리스트 | 아래 체크리스트 전수 통과 | ✅ |
| 10 | V1→V2 전환 조건 | QoD ≥ 0.85(30일), RAG 정확도 ≥ 60%, 메모리 승격/강등 오류율 < 1%, P0 테스트 100%, 비용 초과 없이 30일, 사용자 승인 (6개 전수) | ✅ |

> ⛔ 위 필수 항목 + 아래 V1 완료 체크리스트 + V1→V2 전환 조건 전체 통과 전 V2 진입 금지

### V1 완료 체크리스트
- [ ] ORANGE CORE 17개 I-모듈 동작
- [ ] 5-Gate 전체 동작 (Policy/Approval/Cost/Evidence/SelfCheck)
- [ ] 6개 E-Series Blue Node 동작 (E-1~E-6)
- [ ] L0+L1 메모리 동작
- [ ] Chroma Vector DB + BGE-M3 RAG 동작
- [ ] LangGraph 5-Phase 파이프라인 완성
- [ ] Builder View + Hologram View UI 동작
- [ ] 비용 추적 + 다운시프트 동작
- [ ] Agent Teams V1 (Lead + 2 Sub) 동작
- [ ] MCP Bridge 동작
- [ ] Paper Trading MVP 동작
- [ ] 테스트 커버리지 달성
- [ ] CI/CD 파이프라인 동작
- [ ] V1 CRITICAL 보안항목 15개(S7E 14 + DEC-003 1) 구현 완료 (READINESS_REVIEW §9 확정: CRITICAL 10 + HIGH 4 + DEC-003 1, §6.5 참조)
- [ ] RBAC 4역할(OWNER/ADMIN/OPERATOR/VIEWER) 동작 (V1-Phase 3 §6.5 DEC-003 참조)
- [ ] ₩40,000/월 비용 상한 준수

---

# 4. V2 구현

> **목표**: Pro Server. Docker Compose 배포 + DB 업그레이드 + 보안 강화.
> **기간**: 11-13주 (v10 추가분 반영)
> **비용 상한**: ₩93,000/월 (LOCK)
> **추가 활성 모듈**: +10개 (I-7, I-12, I-22, I-23, I-25, A-4, E-13~E-16 — 전부 V2 COND), §1 모듈표 참조

---

## V2-Phase 1: 인프라 마이그레이션 (Week 1-3)

| # | 항목 | 구현 내용 | 산출물 참조 |
|---|------|----------|-----------|
| 1 | **SQLite → PostgreSQL** | 10-단계 마이그레이션 스크립트, 제로 데이터 손실 | PHASE_B7 §3.1 |
| 2 | **JSONL → PostgreSQL** | 로그 테이블 마이그레이션 | PHASE_B7 §3.2 |
| 3 | **Chroma → Qdrant** | 4-Phase 임베딩 전환 (30일), Dual-Collection | PHASE_B7 §3.3 |
| 4 | **JSON → Neo4j** | NetworkX 그래프 → Neo4j Community | PHASE_B7 §3.4 |
| 5 | **Config 마이그레이션** | config.v1.toml → config.v2.toml | PHASE_B7 §3.5 |
| 6 | **Docker Compose** | 전체 서비스 컨테이너화 | PHASE_B6 §6.1 |
| 7 | **VPS 배포** | SSH 기반 Docker Compose 배포 | PHASE_B6 §6.1 |

### 마이그레이션 원칙 (LOCK, PHASE_B7 §1.2)
1. Zero Data Loss — 마이그레이션 과정에서 데이터 손실 제로
2. Rollback Always — 모든 마이그레이션 단계는 롤백(downgrade) 함수를 포함
3. Verify Before Commit — 마이그레이션 후 데이터 무결성 검증을 통과해야 완료
4. Backup First — 마이그레이션 전 BackupConfigSchema 연동 자동 백업 필수
5. Incremental Migration — 대용량 데이터는 배치 단위 점진적 마이그레이션
6. Schema Version Pinning — 모든 스키마는 명시적 버전을 가지며, 하위 호환성 유지

### 10-Step Migration Orchestration (PHASE_B7 §6 정본)

| Step | 작업 | 검증 |
|------|------|------|
| 1 | 마이그레이션 계획 생성 | 영향도 분석 완료 |
| 2 | 전체 백업 (BackupConfigSchema) | 백업 무결성 체크섬 |
| 3 | 스키마 마이그레이션 (DDL) | 스키마 diff 검증 |
| 4 | 데이터 마이그레이션 (DML) | 행 수 일치 확인 |
| 5 | 인덱스/제약조건 재생성 | 쿼리 성능 테스트 |
| 6 | 참조 무결성 검증 | FK 위반 0건 |
| 7 | 애플리케이션 호환성 테스트 | 전체 테스트 스위트 PASS |
| 8 | 성능 벤치마크 | V1 대비 ±10% 이내 |
| 9 | Canary 배포 (10% 트래픽) | 에러율 < 0.1% |
| 10 | 전체 전환 + 모니터링 | 24시간 안정성 확인 |

### 사후검증 체크리스트 — 7항목 (PHASE_B7 §6.4 기반 도출)

- [ ] 데이터 무결성: 원본 대비 100% 일치 (체크섬 비교)
- [ ] 성능 회귀 없음: 주요 쿼리 응답시간 V1 대비 ±10%
- [ ] 롤백 테스트 완료: 실제 롤백 실행 후 복원 확인
- [ ] 모니터링 알림 정상: 모든 메트릭 대시보드 활성화
- [ ] 백업 스케줄 활성화: 자동 백업 cron 확인
- [ ] 로그 수집 정상: 새 인프라 로그 → 중앙 수집기 연결
- [ ] 문서 갱신: CHANGELOG + 운영 매뉴얼 반영

### 산출물 참조
- 마이그레이션 전략: `PHASE_B7_MIGRATION_STRATEGY.md`
- 인프라 배포: `PHASE_B6_DEPLOYMENT_INFRA.md`
- 설정 스펙: `PHASE_B4_CONFIG_SPEC.md` (config.v2.toml 확장)
- 백업/복구: `PHASE_B7 §6` (10-Step Orchestration)

### 실행 가이드

#### VPS 선택 가이드 (V2→V3 확장 고려) <!-- v26 메이커에반 개선안 7 반영 -->

> V2부터 VPS 서버가 필요합니다. V3 확장을 고려하면 **Hetzner CX31을 1순위로 권장**합니다.

| VPS | 스펙 | 월 비용 | V3 확장성 | 비고 |
|-----|------|--------|----------|------|
| **Hetzner CX31 (권장)** | 2vCPU / 8GB / 80GB SSD (독일 Falkenstein) | ~$8 | V3 Hetzner Lite 직접 호환 | DDoS 20Tbps, VM 회수 리스크 0%, x86 100% |
| Oracle Cloud Free | 4vCPU / 24GB / 200GB (서울) | $0 | 낮음 (ARM, VM 회수 위험) | 무료이나 비활성화/회수 리스크 |
| Vultr | 4vCPU / 8GB / 100GB (서울) | ~$48 | 중간 | 한국 리전 가용 |
| DigitalOcean | 4vCPU / 8GB / 100GB (싱가포르) | ~$48 | 중간 | 표준 VPS |

> **권장 이유**: Hetzner CX31은 $8/월로 V2 Docker Compose 운영에 충분하며, V3 전환 시 동일 서버에서 RunPod Serverless GPU만 추가하면 $200 이내로 Enterprise 구성 가능 (§5 V3-Phase 1 "V3 인프라 대안: Hetzner CX31 + RunPod Serverless" 참조).

#### 사용자 직접 작업
1. **VPS 서버 프로비저닝**: Hetzner CX31 권장 (Ubuntu 22.04+), Docker Engine 24+ / Docker Compose v2 설치. Hetzner Console에서 CX31 생성 → SSH 키 설정 → 방화벽(3000/5432/6333/6379/7687 허용)
2. **PostgreSQL 인스턴스 준비**: PostgreSQL 15+ 설치, VAMOS 전용 DB(`vamos_v2`) + 유저(`vamos_app`) 생성, `pg_hba.conf` 접근 허용
3. **Qdrant 인스턴스 준비**: Docker로 Qdrant 1.7+ 실행 (`docker run -d -p 6333:6333 qdrant/qdrant`), API key 설정
4. **Neo4j 인스턴스 준비**: Neo4j Community 5.x Docker 실행, Bolt 프로토콜(7687) + HTTP(7474) 포트 확인
5. **V1 데이터 전체 백업**: SQLite DB + JSONL 로그 + Chroma persist 디렉토리 + JSON 그래프 파일 → 체크섬(SHA-256) 기록
6. **마이그레이션 실행 승인**: 10-Step Orchestration 계획 리뷰 → 승인 후 `python scripts/migration/run_all.py` 실행
7. **Canary 배포 검증**: 10% 트래픽 전환 후 에러율 < 0.1% 확인, 이상 시 `./scripts/deploy/rollback_v2.sh` 실행
8. **Docker Compose 최종 배포**: `docker compose -f docker-compose.v2.yml up -d` → 전체 서비스 헬스체크 → 24시간 모니터링

#### AI 프롬프트

````text
VAMOS 프로젝트 V2-Phase 1: 인프라 마이그레이션을 진행합니다.

## 작업 목표
V1(로컬 파일 기반) → V2(Docker Compose + 관리형 DB) 인프라 전환.
4개 스토리지 마이그레이션 + Docker Compose 배포 + config.v2.toml 생성.

## 1. SQLite → PostgreSQL 마이그레이션 → `scripts/migration/sqlite_to_pg.py`
- Alembic 기반 스키마 마이그레이션 (DDL)
- SQLite → PostgreSQL 데이터 마이그레이션 (DML): 배치 1000건 단위
- 마이그레이션 전/후 행 수 일치 검증 + 체크섬 비교
- FK 제약조건, 인덱스 재생성
- rollback/downgrade 함수 필수 포함
- BackupConfigSchema 연동 자동 백업

## 2. JSONL → PostgreSQL 마이그레이션 → `scripts/migration/jsonl_to_pg.py`
- 로그 테이블 DDL: `log_events` (LogEventSchema 7필드 기반), `audit_trail`
- JSONL 파싱 → PostgreSQL COPY/INSERT (배치 1000건 단위)
- 타임스탬프 인덱스 + 월별 파티셔닝 (PARTITION BY RANGE)
- rollback: 테이블 DROP + 원본 JSONL 복원

## 3. Chroma → Qdrant 마이그레이션 → `scripts/migration/chroma_to_qdrant.py`
4-Phase 전환:
  (1) Qdrant 컬렉션 생성 (distance=Cosine, vector_size=256)
  (2) BGE-M3 FlagEmbedding으로 임베딩 재생성 (Matryoshka 256dim)
  (3) Dual-Collection 30일 병렬 운영 (Chroma + Qdrant 동시 쿼리, 결과 비교)
  (4) Chroma 제거, Qdrant 단독 전환
- HNSW 인덱스 파라미터: ef_construct=128, m=16
- Hybrid Search 파라미터 LOCK 유지 (alpha=0.7, top_k=20, rerank_top=5)

## 4. JSON → Neo4j 마이그레이션 → `scripts/migration/json_to_neo4j.py`
- NetworkX 그래프 JSON → Cypher CREATE/MERGE 변환
- 노드 레이블: Decision, Evidence, Module, Event, Conversation
- 관계 타입: DEPENDS_ON, REFERENCES, TRIGGERS, PART_OF
- 인덱스: node_id UNIQUE 제약조건 (각 레이블별)
- rollback: 전체 그래프 DROP + JSON 복원

## 5. Config 마이그레이션 → `scripts/migration/config_v1_to_v2.py`
config.v1.toml → config.v2.toml 변환:
- 13섹션 구조 유지 + V2 전용 키 추가:
  - [storage] 섹션: pg_host, pg_port, pg_db, qdrant_host, qdrant_port, neo4j_uri
  - [deployment] 섹션 신규: docker_compose_path, vps_host, ssh_key_path, deploy_mode="docker-compose"
  - [security] 섹션 확장: hmac_secret_key, guardrail_level="L3", gdpr_enabled=true
- 로딩 순서 유지: TOML → ENV → CLI (V0-STEP-5 LOCK)

## 6. Docker Compose → `docker-compose.v2.yml`
서비스 정의:
  - vamos-app: Tauri 백엔드 + Python AI (포트 3000)
  - postgres: PostgreSQL 15 (포트 5432, 볼륨: pgdata)
  - qdrant: Qdrant 1.7+ (포트 6333/6334, 볼륨: qdrant_storage)
  - neo4j: Neo4j Community 5.x (포트 7474/7687, 볼륨: neo4j_data)
  - redis: Redis 7+ (포트 6379, 볼륨: redis_data)
  - timescaledb: TimescaleDB (PostgreSQL 확장, 포트 5433, 볼륨: tsdb_data) — §6.8 #9 V2+ 시계열 DB용. 또는 postgres 서비스에 `timescaledb` 확장 설치로 대체 가능 <!-- FIX-17: RE-F-004 대응. §6.8 TimescaleDB V2+와 Docker Compose 정합성 확보 -->
- 네트워크: vamos-network (bridge 모드)
- 각 서비스 healthcheck 정의 (interval: 30s, timeout: 10s, retries: 3)
- 환경변수: .env.v2 파일 참조 (시크릿은 Docker Secrets 권장)

## 7. 배포 스크립트 → `scripts/deploy/deploy_v2.sh` + `rollback_v2.sh`
deploy_v2.sh:
  - SSH 기반 Docker Compose 원격 배포
  - Blue-Green 전환: --project-name vamos-blue/vamos-green
  - 헬스체크 통과 후 이전 버전 종료
rollback_v2.sh:
  - 이전 프로젝트로 즉시 전환
  - 데이터 롤백은 마이그레이션별 downgrade 함수 호출

## 규칙
> **§1.3 R1~R11 공통 규칙 전수 적용**
- 마이그레이션 원칙 6항 엄격 준수 (PHASE_B7 §1.2 LOCK)
- 10-Step Orchestration 순서 준수 (PHASE_B7 §6)
- 모든 마이그레이션 스크립트에 rollback/downgrade 함수 포함 필수
- 설정 키 이름은 PHASE_B4 정본 그대로 사용
- LOCK/FREEZE 값 변경 금지
- V2 비용 상한 ₩93,000/월 (LOCK) — 인프라 비용 모니터링 대시보드 포함

## 참조 SOT 문서
- PHASE_B7_MIGRATION_STRATEGY.md (마이그레이션 전략 정본)
- PHASE_B6_DEPLOYMENT_INFRA.md (배포 인프라 정본)
- PHASE_B4_CONFIG_SPEC.md §3 (설정 스펙 정본, config.v2.toml 확장 기준)
- PHASE_B3_DEPENDENCIES.md (V2 의존성 목록)
````

#### v12 추가 구현 항목 <!-- v12_BLOCKER v26 -->

| # | 항목 | 구현 내용 | 산출물 참조 |
|---|------|----------|-----------|
| V2P1-B1 | **PagedAttention / vLLM 추론 최적화** | vLLM 서빙 프레임워크 도입, PagedAttention KV Cache 블록 관리(block_size=16), 메모리 효율 스케줄링(max_num_seqs=256), GPU 메모리 활용률 95%+ 목표. 설정: `gpu_memory_utilization=0.9`, `tensor_parallel_size` 자동 감지. Continuous Batching으로 처리량 최적화 [BLOCKER] | §6.2 참조 | <!-- v12_C09b_451 v26 -->

### 단계 완료 검증 (V2-Phase 1 → Phase 2 전환 조건)

| # | 검증 항목 | 확인 방법 | 필수 |
|---|----------|----------|:---:|
| 1 | SQLite → PostgreSQL | 행 수 100% 일치 + 체크섬(SHA-256) 비교 + FK 위반 0건 | ✅ |
| 2 | JSONL → PostgreSQL | 로그 테이블 마이그레이션 + 월별 파티셔닝 + 타임스탬프 인덱스 | ✅ |
| 3 | Chroma → Qdrant | BGE-M3 임베딩 재생성(256dim) + HNSW 인덱스 + Dual-Collection 병렬 운영 시작 | ✅ |
| 4 | JSON → Neo4j | Cypher 노드/관계 생성 + node_id UNIQUE 제약조건 + 데이터 무결성 | ✅ |
| 5 | config.v2.toml | V1→V2 설정 전환 + V2 전용 키 추가 ([deployment], [security] 확장) | ✅ |
| 6 | Docker Compose 헬스체크 | 전체 서비스 (app/postgres/qdrant/neo4j/redis) healthcheck PASS | ✅ |
| 7 | 롤백 테스트 | 실제 rollback/downgrade 실행 → 원본 데이터 복원 확인 | ✅ |
| 8 | 성능 벤치마크 | 주요 쿼리 응답시간 V1 대비 ±10% 이내 | ✅ |
| 9 | 10-Step Orchestration | 10단계 전체 순차 완료 (계획→백업→스키마→데이터→인덱스→무결성→호환→성능→Canary→전환) | ✅ |
| 10 | 사후검증 7항목 | 데이터 무결성/성능 회귀/롤백/모니터링/백업/로그/문서 전수 PASS | ✅ |

> ⛔ 위 필수 항목 전체 통과 전 Phase 2 진입 금지

---

## V2-Phase 2: COND 모듈 활성화 (Week 4-9)

> **Module Catalog 표준 필드** (D2.0-01 §5.5 LOCK): 각 모듈은  enum = {CORE | COND | EXP | RE-ADD}로 분류됨.
> **COND 모듈 기본 OFF 규칙** (D2.0-01 §5.14.4): COND 모듈은 기본 OFF, 활성화 조건 충족 시 config/runtime에서 ON 전환.

| # | 모듈 | 구현 내용 | 산출물 참조 |
|---|------|----------|-----------|
| 1 | **I-7 Project/Session Manager** | 프로젝트 컨텍스트 관리 | D2.0-02 §7.54~7.56 | <!-- D2.0-02 순차 번호: I-7=§7.54~56 -->
| 2 | **I-12 Workflow Builder** | 자기진화 스케줄러 | D2.0-02 §7.69~7.71 | <!-- D2.0-02 순차 번호: I-12=§7.69~71 -->
| 3 | **I-22 Task/Project Manager** | 태스크 관리 시스템 | D2.0-01 §5.6 |
| 4 | **I-23 Doc/Code Structuring** | 문서/코드 구조화 | D2.0-01 §5.6 |
| 5 | **I-25 SDAR Engine** | 자가진단/수리 (**AR-L2** 구현, AR-L3는 Phase 3에서 확장) | VAMOS_SDAR_DESIGN_SPECIFICATION | <!-- SOURCE_CONFLICT: D2.0-01 §5.6 I-25="Self-Directed Agent Runtime" vs SDAR_SPEC="Self-Diagnosis and Auto-Repair". SDAR_SPEC(전문 LOCK) 채택. FIX-027: AR-L2/L3 Phase 구분 명확화 -->
| 6 | **A-4 Debate Mode** | Bull vs Bear 토론 | D2.0-01 §5.9 |
| 7 | **E-13 Calendar/Task Sync** | 캘린더/태스크 동기화 | D2.0-03 |
| 8 | **E-14 Email Handler** | 이메일 처리 | D2.0-03 |
| 9 | **E-15 Cloud Collector** | Cloud Library 수집 파이프라인 | VAMOS_CLOUD_LIBRARY_SPEC |
| 9-1 | **E-15 RT-BNP (V1)** | RSS 60초 폴링 + 키워드 Breaking Detector | VAMOS_CLOUD_LIBRARY_SPEC §7 확장, §6.10.1 |
| 9-2 | **DCL-GEO (V2)** | 지정학/시사 RSS 5분 폴링 + Breaking Detector 확장 | §6.10.2 |
| 10 | **E-16 Cloud Storage Sync** | 클라우드 스토리지 동기화 | D2.0-03 |
| | **── v23 확장: AI/분석 (HIGH) ──** | | |
| 11 | **SHAP/LIME Explainability 모듈 (explainer.py)** | SHAP/LIME Explainability 모듈 (explainer.py) [HIGH] | v10 Phase 2 추가 (AINV-056) | <!-- AINV-056 v23 -->
| 12 | **배치 처리 구현 (S7B-030)** | 배치 처리 구현 (S7B-030) [HIGH] | v10 Phase 2 추가 (D202-059) | <!-- D202-059 v23 -->
| 13 | **시간 여행 디버깅 (Time-Travel Debugging) 구현** | 시간 여행 디버깅 (Time-Travel Debugging) 구현 [HIGH] | v10 Phase 2 추가 (D203-111) | <!-- D203-111 v23 -->
| 14 | **모델 A/B 테스팅 고급 (1000건/7일, 자동 승격/롤백)** | 모델 A/B 테스팅 고급 (1000건/7일, 자동 승격/롤백) [HIGH] | v10 Phase 2 추가 (D204-162) | <!-- D204-162 v23 -->
| 15 | **작업 패턴 프로파일** | 작업 패턴 프로파일 [HIGH] | v10 Phase 2 추가 (D206-038) | <!-- D206-038 v23 -->
| 16 | **개인 멀티미디어 라이브러리** | 개인 멀티미디어 라이브러리 [HIGH] | v10 Phase 2 추가 (D206-115) | <!-- D206-115 v23 -->
| 17 | **MemGPT/Letta 패턴 통합** | MemGPT/Letta 패턴 통합 [HIGH] | v10 Phase 2 추가 (D206-117) | <!-- D206-117 v23 -->
| 18 | **Cognee 통합 (AI KG 자동 구축)** | Cognee 통합 (AI KG 자동 구축) [HIGH] | v10 Phase 2 추가 (D206-125) | <!-- D206-125 v23 -->
| 19 | **지식 신선도 관리** | 지식 신선도 관리 [HIGH] | v10 Phase 2 추가 (D206-179) | <!-- D206-179 v23 -->
| 20 | **지식 충돌 자동 감지** | 지식 충돌 자동 감지 [HIGH] | v10 Phase 2 추가 (D206-180) | <!-- D206-180 v23 -->
| 21 | **M-020 지식 임포트/익스포트 확장 (Notion/Obsidian)** | M-020 지식 임포트/익스포트 확장 (Notion/Obsidian) [HIGH] | v10 Phase 2 추가 (D206-209) | <!-- D206-209 v23 -->
| 22 | **M-004 스크린 캡처 지식화 (Microsoft Recall 로컬 버전)** | M-004 스크린 캡처 지식화 (Microsoft Recall 로컬 버전) [HIGH] | v10 Phase 2 추가 (D206-222) | <!-- D206-222 v23 -->
| 23 | **M-016 시간 기반 지식 관리 (타임라인뷰+주월간리뷰)** | M-016 시간 기반 지식 관리 (타임라인뷰+주월간리뷰) [HIGH] | v10 Phase 2 추가 (D206-226) | <!-- D206-226 v23 -->
| 24 | **M-043 예측적 지식 서핑 (행동예측→관련지식 미리 로드)** | M-043 예측적 지식 서핑 (행동예측→관련지식 미리 로드) [HIGH] | v10 Phase 2 추가 (D206-232) | <!-- D206-232 v23 -->
| 25 | **개인 감정 패턴 학습 (예측적 지원)** | 개인 감정 패턴 학습 (예측적 지원) [HIGH] | v10 Phase 2 추가 (D207-114) | <!-- D207-114 v23 -->
| 26 | **편향 감사 엔진 (확증/최신/생존/섹터)** | 편향 감사 엔진 (확증/최신/생존/섹터) [HIGH] | v10 Phase 2 추가 (D207-129) | <!-- D207-129 v23 -->
| | **── v23 확장: 아키텍처/엔지니어링 (HIGH) ──** | | |
| 27 | **B-026 국제화** | B-026 국제화 [HIGH] | v10 Phase 2 추가 (S7AE-344) | <!-- S7AE-344 v23 -->
| 28 | **B-030 접근성** | B-030 접근성 [HIGH] | v10 Phase 2 추가 (S7AE-345) | <!-- S7AE-345 v23 -->
| 29 | **B-032 버전 관리** | B-032 버전 관리 [HIGH] | v10 Phase 2 추가 (S7AE-346) | <!-- S7AE-346 v23 -->
| 30 | **분산 트레이싱** | 분산 트레이싱 [HIGH] | v10 Phase 2 추가 (S7AE-361) | <!-- S7AE-361 v23 -->
| 31 | **백프레셔** | 백프레셔 [HIGH] | v10 Phase 2 추가 (S7AE-369) | <!-- S7AE-369 v23 -->
| 32 | **CQRS 패턴** | CQRS 패턴 [HIGH] | v10 Phase 2 추가 (S7AE-384) | <!-- S7AE-384 v23 -->
| 33 | **사가 패턴** | 사가 패턴 [HIGH] | v10 Phase 2 추가 (S7AE-386) | <!-- S7AE-386 v23 -->
| 34 | **읽기 복제본** | 읽기 복제본 [HIGH] | v10 Phase 2 추가 (S7AE-388) | <!-- S7AE-388 v23 -->
| 35 | **E-024 운영** | E-024 운영 [HIGH] | v10 Phase 2 추가 (S7AE-561) | <!-- S7AE-561 v23 -->
| 36 | **E-025 운영** | E-025 운영 [HIGH] | v10 Phase 2 추가 (S7AE-562) | <!-- S7AE-562 v23 -->
| 37 | **E-026 운영** | E-026 운영 [HIGH] | v10 Phase 2 추가 (S7AE-563) | <!-- S7AE-563 v23 -->
| 38 | **E-027 운영** | E-027 운영 [HIGH] | v10 Phase 2 추가 (S7AE-564) | <!-- S7AE-564 v23 -->
| 39 | **E-028 운영** | E-028 운영 [HIGH] | v10 Phase 2 추가 (S7AE-565) | <!-- S7AE-565 v23 -->
| 40 | **E-029 운영** | E-029 운영 [HIGH] | v10 Phase 2 추가 (S7AE-566) | <!-- S7AE-566 v23 -->
| 41 | **E-030 운영** | E-030 운영 [HIGH] | v10 Phase 2 추가 (S7AE-567) | <!-- S7AE-567 v23 -->
| 42 | **E-034 운영** | E-034 운영 [HIGH] | v10 Phase 2 추가 (S7AE-571) | <!-- S7AE-571 v23 -->
| 43 | **E-035 운영** | E-035 운영 [HIGH] | v10 Phase 2 추가 (S7AE-572) | <!-- S7AE-572 v23 -->
| 44 | **E-036 운영** | E-036 운영 [HIGH] | v10 Phase 2 추가 (S7AE-573) | <!-- S7AE-573 v23 -->
| 45 | **E-037 운영** | E-037 운영 [HIGH] | v10 Phase 2 추가 (S7AE-574) | <!-- S7AE-574 v23 -->
| 46 | **E-038 운영** | E-038 운영 [HIGH] | v10 Phase 2 추가 (S7AE-575) | <!-- S7AE-575 v23 -->
| 47 | **E-039 운영** | E-039 운영 [HIGH] | v10 Phase 2 추가 (S7AE-576) | <!-- S7AE-576 v23 -->
| 48 | **E-040 운영** | E-040 운영 [HIGH] | v10 Phase 2 추가 (S7AE-577) | <!-- S7AE-577 v23 -->
| 49 | **E-043 운영** | E-043 운영 [HIGH] | v10 Phase 2 추가 (S7AE-580) | <!-- S7AE-580 v23 -->
| 50 | **E-044 운영** | E-044 운영 [HIGH] | v10 Phase 2 추가 (S7AE-581) | <!-- S7AE-581 v23 -->
| 51 | **E-045 운영** | E-045 운영 [HIGH] | v10 Phase 2 추가 (S7AE-582) | <!-- S7AE-582 v23 -->
| 52 | **E-046 운영** | E-046 운영 [HIGH] | v10 Phase 2 추가 (S7AE-583) | <!-- S7AE-583 v23 -->
| 53 | **E-047 운영** | E-047 운영 [HIGH] | v10 Phase 2 추가 (S7AE-584) | <!-- S7AE-584 v23 -->
| 54 | **E-048 운영** | E-048 운영 [HIGH] | v10 Phase 2 추가 (S7AE-585) | <!-- S7AE-585 v23 -->
| 55 | **E-049 운영** | E-049 운영 [HIGH] | v10 Phase 2 추가 (S7AE-586) | <!-- S7AE-586 v23 -->
| 56 | **E-050 운영** | E-050 운영 [HIGH] | v10 Phase 2 추가 (S7AE-587) | <!-- S7AE-587 v23 -->
| 57 | **E-069 운영** | E-069 운영 [HIGH] | v10 Phase 2 추가 (S7AE-606) | <!-- S7AE-606 v23 -->
| 58 | **E-070 운영** | E-070 운영 [HIGH] | v10 Phase 2 추가 (S7AE-607) | <!-- S7AE-607 v23 -->
| 59 | **E-071 운영** | E-071 운영 [HIGH] | v10 Phase 2 추가 (S7AE-608) | <!-- S7AE-608 v23 -->
| 60 | **E-072 운영** | E-072 운영 [HIGH] | v10 Phase 2 추가 (S7AE-609) | <!-- S7AE-609 v23 -->
| 61 | **E-075 운영** | E-075 운영 [HIGH] | v10 Phase 2 추가 (S7AE-612) | <!-- S7AE-612 v23 -->
| 62 | **E-076 운영** | E-076 운영 [HIGH] | v10 Phase 2 추가 (S7AE-613) | <!-- S7AE-613 v23 -->
| 63 | **E-081 운영** | E-081 운영 [HIGH] | v10 Phase 2 추가 (S7AE-618) | <!-- S7AE-618 v23 -->
| 64 | **E-082 운영** | E-082 운영 [HIGH] | v10 Phase 2 추가 (S7AE-619) | <!-- S7AE-619 v23 -->
| 65 | **E-083 운영** | E-083 운영 [HIGH] | v10 Phase 2 추가 (S7AE-620) | <!-- S7AE-620 v23 -->
| 66 | **E-084 운영** | E-084 운영 [HIGH] | v10 Phase 2 추가 (S7AE-621) | <!-- S7AE-621 v23 -->
| 67 | **E-086 운영** | E-086 운영 [HIGH] | v10 Phase 2 추가 (S7AE-623) | <!-- S7AE-623 v23 -->
| 68 | **E-087 운영** | E-087 운영 [HIGH] | v10 Phase 2 추가 (S7AE-624) | <!-- S7AE-624 v23 -->
| 69 | **E-088 운영** | E-088 운영 [HIGH] | v10 Phase 2 추가 (S7AE-625) | <!-- S7AE-625 v23 -->
| 70 | **E-089 운영** | E-089 운영 [HIGH] | v10 Phase 2 추가 (S7AE-626) | <!-- S7AE-626 v23 -->
| 71 | **E-090 운영** | E-090 운영 [HIGH] | v10 Phase 2 추가 (S7AE-627) | <!-- S7AE-627 v23 -->
| 72 | **E-091 운영** | E-091 운영 [HIGH] | v10 Phase 2 추가 (S7AE-628) | <!-- S7AE-628 v23 -->
| 73 | **E-092 운영** | E-092 운영 [HIGH] | v10 Phase 2 추가 (S7AE-629) | <!-- S7AE-629 v23 -->
| | **── v23 확장: 인프라/서버 (HIGH) ──** | | |
| 74 | **작업 큐 서버** | 작업 큐 서버 [HIGH] | v10 Phase 2 추가 (S7FI-024) | <!-- S7FI-024 v23 -->
| 75 | **검색 엔진 서버** | 검색 엔진 서버 [HIGH] | v10 Phase 2 추가 (S7FI-026) | <!-- S7FI-026 v23 -->
| 76 | **알림 서버** | 알림 서버 [HIGH] | v10 Phase 2 추가 (S7FI-030) | <!-- S7FI-030 v23 -->
| 77 | **피처 스토어** | 피처 스토어 [HIGH] | v10 Phase 2 추가 (S7FI-072) | <!-- S7FI-072 v23 -->
| 78 | **CDN 구성** | CDN 구성 [HIGH] | v10 Phase 2 추가 (S7FI-080) | <!-- S7FI-080 v23 -->
| 79 | **다중 리전 복제** | 다중 리전 복제 [HIGH] | v10 Phase 2 추가 (S7FI-087) | <!-- S7FI-087 v23 -->
| | **── v23 확장: 미디어/지식관리 (HIGH) ──** | | |
| 80 | **스타일 트랜스퍼** | 스타일 트랜스퍼 [HIGH] | v10 Phase 2 추가 (S7JM-014) | <!-- S7JM-014 v23 -->
| 81 | **로고/아이콘 생성** | 로고/아이콘 생성 [HIGH] | v10 Phase 2 추가 (S7JM-016) | <!-- S7JM-016 v23 -->
| 82 | **화자 분리 (Speaker Diarization)** | 화자 분리 (Speaker Diarization) [HIGH] | v10 Phase 2 추가 (S7JM-023) | <!-- S7JM-023 v23 -->
| 83 | **양식/폼 자동 생성** | 양식/폼 자동 생성 [HIGH] | v10 Phase 2 추가 (S7JM-047) | <!-- S7JM-047 v23 -->
| 84 | **크로스모달 검색** | 크로스모달 검색 [HIGH] | v10 Phase 2 추가 (S7JM-062) | <!-- S7JM-062 v23 -->
| 85 | **CrewAI 역할 패턴 참조** | CrewAI 역할 패턴 참조 [HIGH] | v10 Phase 2 추가 (S7JM-123) | <!-- S7JM-123 v23 -->
| 86 | **코드 변환 (언어 간)** | 코드 변환 (언어 간) [HIGH] | v10 Phase 2 추가 (S7JM-181) | <!-- S7JM-181 v23 -->
| 87 | **개인 위키** | 개인 위키 [HIGH] | v10 Phase 2 추가 (S7JM-267) | <!-- S7JM-267 v23 -->
| 88 | **예측적 지식 서핑** | 예측적 지식 서핑 [HIGH] | v10 Phase 2 추가 (S7JM-273) | <!-- S7JM-273 v23 -->
| 89 | **지식 기반 개인 어시스턴트** | 지식 기반 개인 어시스턴트 [HIGH] | v10 Phase 2 추가 (S7JM-274) | <!-- S7JM-274 v23 -->
| | **── v23 확장: 개인화/웰니스/교육 (HIGH) ──** | | |
| 90 | **Notion/Obsidian 통합** | Notion/Obsidian 통합 [HIGH] | v10 Phase 2 추가 (S7NP-031) | <!-- S7NP-031 v23 -->
| 91 | **개인화 학습 경로** | 개인화 학습 경로 [HIGH] | v10 Phase 2 추가 (S7NP-045) | <!-- S7NP-045 v23 -->
| 92 | **시험 준비 도우미** | 시험 준비 도우미 [HIGH] | v10 Phase 2 추가 (S7NP-059) | <!-- S7NP-059 v23 -->
| 93 | **교육 컨텐츠 생성** | 교육 컨텐츠 생성 [HIGH] | v10 Phase 2 추가 (S7NP-072) | <!-- S7NP-072 v23 -->
| 94 | **교육 평가 도구** | 교육 평가 도구 [HIGH] | v10 Phase 2 추가 (S7NP-073) | <!-- S7NP-073 v23 -->
| 95 | **수면 개선 도우미** | 수면 개선 도우미 [HIGH] | v10 Phase 2 추가 (S7NP-085) | <!-- S7NP-085 v23 -->
| 96 | **운동/피트니스 트래커** | 운동/피트니스 트래커 [HIGH] | v10 Phase 2 추가 (S7NP-086) | <!-- S7NP-086 v23 -->
| 97 | **식단/영양 관리** | 식단/영양 관리 [HIGH] | v10 Phase 2 추가 (S7NP-087) | <!-- S7NP-087 v23 -->
| 98 | **감정 일지 분석** | 감정 일지 분석 [HIGH] | v10 Phase 2 추가 (S7NP-090) | <!-- S7NP-090 v23 -->
| 99 | **사회적 관계 관리** | 사회적 관계 관리 [HIGH] | v10 Phase 2 추가 (S7NP-098) | <!-- S7NP-098 v23 -->
| 100 | **개인화 건강 인사이트** | 개인화 건강 인사이트 [HIGH] | v10 Phase 2 추가 (S7NP-104) | <!-- S7NP-104 v23 -->
| 101 | **감정 기반 음악 추천** | 감정 기반 음악 추천 [HIGH] | v10 Phase 2 추가 (S7NP-106) | <!-- S7NP-106 v23 -->
| 102 | **Qwen 3 한중일 특화** | Qwen 3 한중일 특화 [HIGH] | v10 Phase 2 추가 (S7NP-128) | <!-- S7NP-128 v23 -->
| 103 | **FinGPT 활용** | FinGPT 활용 [HIGH] | v10 Phase 2 추가 (S7NP-190) | <!-- S7NP-190 v23 -->
| 104 | **Ambient Intelligence (앰비언트 인텔리전스)** | Ambient Intelligence (앰비언트 인텔리전스) [HIGH] | v10 Phase 2 추가 (S7NP-198) | <!-- S7NP-198 v23 -->
| | **── v23 확장: MEDIUM 우선순위 ──** | | |
| 105 | **S5 피드백 학습 모듈 (성과 측정, 롤백, 패턴 강화)** | S5 피드백 학습 모듈 (성과 측정, 롤백, 패턴 강화) [MEDIUM] | v10 Phase 2 추가 (CLIB-057) | <!-- CLIB-057 v23 -->
| 106 | **C3 규칙 제안 (패턴→규칙 제안→인간 승인)** | C3 규칙 제안 (패턴→규칙 제안→인간 승인) [MEDIUM] | v10 Phase 2 추가 (CLIB-077) | <!-- CLIB-077 v23 -->
| 107 | **형태소 분석 기반 토큰화 (Mecab-ko V1/Kiwi V2)** | 형태소 분석 기반 토큰화 (Mecab-ko V1/Kiwi V2) [MEDIUM] | v10 Phase 2 추가 (D206-063) | <!-- D206-063 v23 -->
| 108 | **M-014 Zettelkasten 방법론 심화** | M-014 Zettelkasten 방법론 심화 [MEDIUM] | v10 Phase 2 추가 (D206-208) | <!-- D206-208 v23 -->
| 109 | **인포그래픽 자동 생성** | 인포그래픽 자동 생성 [MEDIUM] | v10 Phase 2 추가 (S7JM-057) | <!-- S7JM-057 v23 -->
| 110 | **ETL 도구** | ETL 도구 [MEDIUM] | v10 Phase 2 추가 (S7NP-016) | <!-- S7NP-016 v23 -->
| 111 | **Zapier/Make 호환 패턴** | Zapier/Make 호환 패턴 [MEDIUM] | v10 Phase 2 추가 (S7NP-027) | <!-- S7NP-027 v23 -->
| 112 | **JIRA/Linear 통합** | JIRA/Linear 통합 [MEDIUM] | v10 Phase 2 추가 (S7NP-033) | <!-- S7NP-033 v23 -->
| | **── v23 확장: LOW 우선순위 ──** | | |
| 113 | **대화형 튜토리얼** | 대화형 튜토리얼 [LOW] | v10 Phase 2 추가 (S7JM-219) | <!-- S7JM-219 v23 -->
| 114 | **학습 분석 대시보드** | 학습 분석 대시보드 [LOW] | v10 Phase 2 추가 (S7NP-051) | <!-- S7NP-051 v23 -->
| 115 | **언어 학습 특화** | 언어 학습 특화 [LOW] | v10 Phase 2 추가 (S7NP-056) | <!-- S7NP-056 v23 -->
| 116 | **웰빙 대시보드** | 웰빙 대시보드 [LOW] | v10 Phase 2 추가 (S7NP-091) | <!-- S7NP-091 v23 -->
| | **── v12 BLOCKER 추가 ──** | | | <!-- v12_BLOCKER v26 -->
| 117 | **Self-RAG 자기 반성 RAG** | Retrieval-Augmented Generation에 자기 반성(Self-Reflection) 루프 추가: ①검색 실행 →②검색 결과 적합성 자체 평가(relevance score) →③부적합 시 쿼리 재작성(query rewriting) →④재검색 →⑤최종 생성. 적합성 임계값 0.7, 최대 재시도 3회 [BLOCKER] | STEP7_A-E 상세명세서 참조 | <!-- v12_C09a_037 v26 -->
| 118 | **자율 코딩 에이전트** | Aider/Devin 패턴 기반 자율 코딩: 코드 생성→테스트 실행→오류 분석→수정 자동화 루프. 파일 시스템 접근(sandbox), Git 통합(branch/commit/PR 자동 생성), 테스트 커버리지 목표 80%+, 보안 스캔(Bandit/Semgrep) 자동 실행 [BLOCKER] | §6.7 참조 | <!-- v12_C12_170 v26 -->
| 119 | **에이전트 공유 TaskBoard** | 멀티에이전트 작업 공유 스키마: TaskBoard(task_id, title, assignee_agent, status={TODO|IN_PROGRESS|REVIEW|DONE}, priority, dependencies[], created_at, deadline). 작업 할당 프로토콜(능력 기반 매칭), 상태 추적(실시간 SSE), 완료 확인(검증 에이전트) [BLOCKER] | VAMOS_AGENT_TEAMS_SPEC | <!-- v12_C13_003 v26 -->
| 120 | **추론 모드 통합 (Reasoning Budget)** | 추론 깊이 자동 조절 시스템: 쿼리 복잡도 분류(simple/moderate/complex/expert)→ 추론 예산 할당(token budget: 256/1024/4096/16384)→ 비용/품질 트레이드오프 정책(max_reasoning_tokens config)→ 예산 초과 시 폴백(요약 후 재시도). Extended Thinking 모드 통합 [BLOCKER] | §6.7 참조 | <!-- v12_C13_008 v26 -->
| | **-- v12 HIGH 추가: Agent --** | | | <!-- feature_id v26 -->
| 10 | **Dynamic Agent** | 동적 에이전트 생성/제거 시스템: 작업 부하 기반 에이전트 자동 스폰, 역할 동적 할당, 리소스 풀 관리 [HIGH] | §6 참조 | <!-- v12_C01a_094 v26 -->
| 14 | **Backtesting Framework** | 백테스팅 프레임워크: 전략 시뮬레이션 엔진, 히스토리컬 데이터 리플레이, 성과 지표(Sharpe/MDD/Win Rate) 산출 [HIGH] | §6 참조 | <!-- v12_C01a_193 v26 -->
| 19 | **Multi-Persona Agent** | 멀티 페르소나 에이전트: 단일 에이전트 내 다중 역할 전환, 컨텍스트별 페르소나 선택, 성격 프로필 관리 [HIGH] | §6 참조 | <!-- v12_C03_072 v26 -->
| 20 | **Meeting Automation** | 회의 자동화: 회의록 자동 작성(STT->요약), 액션 아이템 추출, 캘린더 연동, 참석자 알림 [HIGH] | §6 참조 | <!-- v12_C03_191 v26 -->
| 31 | **Agent 위임(Delegation) 모드** | 에이전트 위임 모드: 작업 하위 분할->서브에이전트 위임, 능력 기반 매칭, 결과 취합/검증 [HIGH] | §6 참조 | <!-- v12_C09a_005 v26 -->
| 32 | **Agent 작업 완료 알림 시스템** | 에이전트 작업 완료 알림: SSE/WebSocket 기반 실시간 알림, 채널별 알림 설정, 알림 히스토리 [HIGH] | §6 참조 | <!-- v12_C09a_007 v26 -->
| 33 | **Agent 권한 체계** | 에이전트 권한 체계: RBAC 기반 에이전트별 권한(파일/네트워크/DB 접근), 권한 상속, 감사 로그 [HIGH] | §6 참조 | <!-- v12_C09a_011 v26 -->
| 34 | **Agent 컨텍스트 자동 압축** | 에이전트 컨텍스트 자동 압축: 긴 대화 자동 요약, 핵심 정보 추출, 토큰 예산 내 컨텍스트 유지 [HIGH] | §6 참조 | <!-- v12_C09a_012 v26 -->
| 44 | **A2A Task Lifecycle 관리** | A2A Task Lifecycle 관리: 에이전트 간 작업 위임/추적/완료 확인 프로토콜 구현 [HIGH] | §6 참조 | <!-- v12_C09b_110 v26 -->
| 45 | **A2A 모니터링/관측** | A2A 모니터링/관측: OpenTelemetry 기반 에이전트 간 통신 추적, 분산 트레이싱 [HIGH] | §6 참조 | <!-- v12_C09b_117 v26 -->
| 46 | **Magentic-One 패턴** | Magentic-One 패턴: Microsoft 멀티에이전트 오케스트레이션 패턴 적용(Orchestrator+Worker 구조) [HIGH] | §6 참조 | <!-- v12_C09b_122 v26 -->
| 47 | **VBS-12 에이전트 성능 벤치마크** | VBS-12 에이전트 성능 벤치마크: 작업 완료율/시간/비용/품질 종합 평가 메트릭 구현 [HIGH] | §6 참조 | <!-- v12_C09b_128 v26 -->
| 51 | **Dream Mode 자동 실행** | Dream Mode 자동 실행: 사용자 미활동 감지->백그라운드 작업 자동 실행(정리/분석/요약) [HIGH] | §6 참조 | <!-- v12_C09b_324 v26 -->
| 69 | **AutoGen 대화 패턴 참조** | AutoGen 대화 패턴: Microsoft AutoGen 멀티에이전트 대화 패턴 적용, 그룹 채팅 오케스트레이션 [HIGH] | §6 참조 | <!-- v12_C09b_538 v26 -->
| 71 | **멀티 Agent 투자 협업 분석** | 멀티 Agent 투자 협업: 리서치->분석->위험평가->추천 에이전트 파이프라인, 합의 프로토콜 [HIGH] | §6 참조 | <!-- v12_C11_252 v26 -->
| 74 | **멀티모달 작업 플래너** | 멀티모달 작업 플래너 고도화: 모달리티별 처리 병렬화, 우선순위 스케줄링, 비용 최적화 [HIGH] | §6 참조 | <!-- v12_C12_060 v26 -->
| 80 | **예측형 에이전트** | 예측형 에이전트: 사용자 의도 예측 기반 사전 작업 실행, 컨텍스트 프리페칭 [HIGH] | §6 참조 | <!-- v12_C12_142 v26 -->
| | **-- v12 HIGH 추가: Benchmark --** | | | <!-- feature_id v26 -->
| 17 | **A2A Test Framework** | A2A 테스트 프레임워크: 에이전트 간 통신 시나리오 테스트, Mock Agent 생성, 프로토콜 준수 검증 [HIGH] | §6 참조 | <!-- v12_C03_037 v26 -->
| 62 | **MoA 평가 기준** | MoA 평가 기준: Mixture of Agents 품질/비용/지연 종합 평가 메트릭, 최적 조합 탐색 [HIGH] | §6 참조 | <!-- v12_C09b_460 v26 -->
| 67 | **도메인별 벤치마크** | 도메인별 벤치마크: 금융/교육/웰니스/코딩 도메인별 특화 평가 데이터셋 및 메트릭 [HIGH] | §6 참조 | <!-- v12_C09b_518 v26 -->
| 79 | **VBS-12 에이전트 협업 벤치마크** | VBS-12 에이전트 협업 벤치마크: 팀 작업 완료율/조정 효율/통신 오버헤드 평가 [HIGH] | §6 참조 | <!-- v12_C12_115 v26 -->
| 81 | **VBS-13 코드 생성 벤치마크** | VBS-13 코드 생성 벤치마크: HumanEval/MBPP 기반 코드 생성 품질/정확도/속도 평가 [HIGH] | §6 참조 | <!-- v12_C12_173 v26 -->
| 84 | **VBS-14 지식관리 벤치마크** | VBS-14 지식관리 벤치마크: 지식 검색 정확도/재현율/갱신 효율 평가 프레임워크 [HIGH] | §6 참조 | <!-- v12_C12_207 v26 -->
| 85 | **VBS-16 교육학습 벤치마크** | VBS-16 교육학습 벤치마크: 학습 효과/적응 정확도/개인화 품질 평가 프레임워크 [HIGH] | §6 참조 | <!-- v12_C12_245 v26 -->
| 86 | **VBS-17 웰니스 AI 벤치마크** | VBS-17 웰니스 AI 벤치마크 확장: 장기 정서 변화 추적, 위기 감지 정확도 평가 [HIGH] | §6 참조 | <!-- v12_C12_269 v26 -->
| | **-- v12 HIGH 추가: Blue Nodes --** | | | <!-- feature_id v26 -->
| 21 | **Career Development Agent** | 커리어 개발 에이전트: 이력서 분석, 스킬 갭 진단, 학습 경로 추천, 취업 시장 트렌드 분석 [HIGH] | §6 참조 | <!-- v12_C03_215 v26 -->
| 22 | **Presentation Coaching Agent** | 프레젠테이션 코칭 에이전트: 발표 구조 분석, 시각 자료 제안, 리허설 피드백, Q&A 예상 질문 생성 [HIGH] | §6 참조 | <!-- v12_C03_217 v26 -->
| 36 | **팟캐스트/오디오 콘텐츠 자동 생성** | 팟캐스트/오디오 자동 생성: 텍스트->대화형 오디오 변환, 다중 화자 TTS, BGM 자동 삽입 [HIGH] | §6 참조 | <!-- v12_C09b_030 v26 -->
| 37 | **비디오/오디오 RAG** | 비디오/오디오 RAG: 미디어 파일 인덱싱(Whisper 전사->청크->임베딩), 시간 기반 검색/참조 [HIGH] | §6 참조 | <!-- v12_C09b_055 v26 -->
| 38 | **멀티모달 작업 플래너** | 멀티모달 작업 플래너: 텍스트+이미지+음성 복합 입력 분석, 모달리티별 처리 계획 수립 [HIGH] | §6 참조 | <!-- v12_C09b_060 v26 -->
| 39 | **멀티모달 합성 Composition** | 멀티모달 합성: 다중 모달리티 출력 조합(텍스트+이미지+차트), 레이아웃 자동 배치 [HIGH] | §6 참조 | <!-- v12_C09b_062 v26 -->
| 40 | **Dream Mode 멀티모달 (Background Generation)** | Dream Mode 멀티모달: 백그라운드 이미지/오디오 생성, 사용자 미활동 시 창의적 콘텐츠 자동 생성 [HIGH] | §6 참조 | <!-- v12_C09b_072 v26 -->
| 41 | **비디오 이해 모델 최신** | 비디오 이해 모델: 최신 Video LLM 통합(VideoLLaMA/InternVideo), 장면 분석, 객체 추적 [HIGH] | §6 참조 | <!-- v12_C09b_078 v26 -->
| 42 | **오디오 LLM 통합** | 오디오 LLM 통합: 음성 직접 이해 모델(AudioPaLM/SALMONN), 음성->의도 직접 분석 [HIGH] | §6 참조 | <!-- v12_C09b_080 v26 -->
| 43 | **Multimodal A/B 테스트** | 멀티모달 A/B 테스트: 텍스트 vs 이미지 vs 멀티모달 응답 비교 실험 프레임워크 [HIGH] | §6 참조 | <!-- v12_C09b_087 v26 -->
| 63 | **LLM 기반 실적 콜 분석** | LLM 기반 실적 콜 분석: 기업 실적 발표 전사->핵심 지표 추출->투자 시사점 요약 [HIGH] | §6 참조 | <!-- v12_C09b_472 v26 -->
| 68 | **이미지 편집 (인페인팅/아웃페인팅)** | 이미지 편집: 인페인팅(영역 채우기)/아웃페인팅(영역 확장) AI 모델 통합, 마스크 기반 편집 UI [HIGH] | §6 참조 | <!-- v12_C09b_527 v26 -->
| | **-- v12 HIGH 추가: Infra --** | | | <!-- feature_id v26 -->
| 16 | **A2A Monitoring** | A2A 모니터링: 에이전트 간 통신 추적, 메시지 지연/실패 대시보드, 알림 규칙 설정 [HIGH] | §6 참조 | <!-- v12_C03_036 v26 -->
| 18 | **Agent Packaging** | 에이전트 패키징: Docker 이미지 빌드, 의존성 번들링, 버전 태깅, 레지스트리 배포 자동화 [HIGH] | §6 참조 | <!-- v12_C03_062 v26 -->
| 48 | **API 문서 자동 생성** | API 문서 자동 생성: OpenAPI 스펙 자동 추출, Swagger UI, 엔드포인트별 예제 자동 생성 [HIGH] | §6 참조 | <!-- v12_C09b_192 v26 -->
| 49 | **플러그인 개발 도구 (Plugin Development Kit)** | 플러그인 개발 도구: SDK/CLI/템플릿/문서 생성기, 로컬 테스트 환경, 배포 파이프라인 [HIGH] | §6 참조 | <!-- v12_C09b_200 v26 -->
| 59 | **Speculative Decoding 최신** | Speculative Decoding 최신: Draft+Verify 병렬 디코딩, 소형 Draft 모델 선택, 수용률 최적화 [HIGH] | §6 참조 | <!-- v12_C09b_452 v26 -->
| 60 | **MLA (Multi-head Latent Attention)** | MLA (Multi-head Latent Attention): DeepSeek 스타일 KV Cache 압축, 잠재 공간 어텐션 구현 [HIGH] | §6 참조 | <!-- v12_C09b_453 v26 -->
| 61 | **SGLang** | SGLang: 고성능 LLM 서빙 프레임워크, RadixAttention 통합, 구조화된 생성 가속 [HIGH] | §6 참조 | <!-- v12_C09b_454 v26 -->
| 66 | **Kubernetes 배포 매니페스트** | Kubernetes 배포 매니페스트: Helm Chart 작성, Blue-Green 배포, HPA/VPA 오토스케일링 설정 [HIGH] | §6 참조 | <!-- v12_C09b_511 v26 -->
| 70 | **IDE 플러그인 (VSCode)** | IDE 플러그인 (VSCode): Language Server Protocol 지원, 인라인 완성/진단/리팩토링 액션 [HIGH] | §6 참조 | <!-- v12_C09b_547 v26 -->
| 77 | **A2A 에러 처리 및 복구** | A2A 에러 처리 및 복구: 통신 실패 자동 재시도, Circuit Breaker, 데드레터 큐, 장애 격리 [HIGH] | §6 참조 | <!-- v12_C12_104 v26 -->
| | **-- v12 HIGH 추가: MCP --** | | | <!-- feature_id v26 -->
| 15 | **A2A Task Lifecycle** | A2A 작업 수명주기 관리: Task 생성->할당->실행->검증->완료 상태 머신, 타임아웃/재시도 정책 [HIGH] | §6 참조 | <!-- v12_C03_029 v26 -->
| 25 | **TIE 도구 관리 UI** | TIE 도구 관리 UI: MCP 도구 목록 표시, 활성화/비활성화 토글, 도구별 사용 통계, 권한 설정 [HIGH] | §6 참조 | <!-- v12_C05_098 v26 -->
| 35 | **MCP 서버 자동 발견** | MCP 서버 자동 발견: mDNS/DNS-SD 기반 로컬 MCP 서버 탐색, 원격 레지스트리 조회, 자동 연결 [HIGH] | §6 참조 | <!-- v12_C09a_015 v26 -->
| 75 | **MCP 마켓플레이스** | MCP 마켓플레이스: MCP 서버/도구 등록/검색/설치 마켓, 평점/리뷰, 자동 업데이트 [HIGH] | §6 참조 | <!-- v12_C12_096 v26 -->
| 76 | **MCP-Blue Node 브리지** | MCP-Blue Node 브리지: MCP 프로토콜<->Blue Node 인터페이스 변환, 양방향 데이터 흐름 [HIGH] | §6 참조 | <!-- v12_C12_098 v26 -->
| 78 | **A2A-MCP 브리지** | A2A-MCP 브리지: A2A 프로토콜<->MCP 프로토콜 게이트웨이, 메시지 변환, 라우팅 규칙 [HIGH] | §6 참조 | <!-- v12_C12_105 v26 -->
| | **-- v12 HIGH 추가: Orange Core --** | | | <!-- feature_id v26 -->
| 29 | **S-5 자가 진화 5단계 시스템** | S-5 자가 진화 5단계: 수집->분석->제안->검증->적용 단계별 파이프라인, 승인 게이트, 롤백 메커니즘 [HIGH] | §6 참조 | <!-- v12_C08_060 v26 -->
| 53 | **Gemini 2.5 Pro 100만 토큰 활용** | Gemini 2.5 Pro 100만 토큰: 초대형 컨텍스트 활용 전략, 문서 전체 분석, 비용 최적화 라우팅 [HIGH] | §6 참조 | <!-- v12_C09b_411 v26 -->
| 64 | **Grok 실시간 소셜 데이터 연동 패턴** | Grok 실시간 소셜 데이터: X(Twitter) 실시간 피드 분석, 트렌드 감지, 시장 센티멘트 추출 [HIGH] | §6 참조 | <!-- v12_C09b_498 v26 -->
| 83 | **지식의 Dream Mode 처리** | 지식의 Dream Mode 처리: 백그라운드 지식 재구조화, 연결 발견, 인사이트 자동 생성 [HIGH] | §6 참조 | <!-- v12_C12_202 v26 -->
| 87 | **V2 대화프로세스 고급 기능 (8건)** | V2 대화프로세스 고급 기능: 분기 관리/병합/롤백/탬플릿/자동 요약/감정 추적/다국어/접근성 [HIGH] | §6 참조 | <!-- v12_C13_088 v26 -->
| | **-- v12 HIGH 추가: Schemas --** | | | <!-- feature_id v26 -->
| 30 | **RepairAction 수리 액션 스키마** | RepairAction 스키마: repair_type(RETRY/ROLLBACK/HOTFIX/ESCALATE), target_module, severity, auto_approve 조건 [HIGH] | §6 참조 | <!-- v12_C08_074 v26 -->
| | **-- v12 HIGH 추가: Storage --** | | | <!-- feature_id v26 -->
| 23 | **L2 장기 지식 저장소 구현** | L2 장기 지식 저장소: 전역 검색 기반 지식 CRUD, TTL 없음(영구), 카테고리/태그 분류, 벡터 인덱싱 [HIGH] | §6 참조 | <!-- v12_C04_004 v26 -->
| 24 | **L3 절차 메모리 구현** | L3 절차 메모리: 전역/프로젝트 절차 템플릿 저장, 워크플로우 패턴 학습, 자동 절차 생성 [HIGH] | §6 참조 | <!-- v12_C04_005 v26 -->
| 50 | **그래프 기반 추천** | 그래프 기반 추천: Neo4j 협업 필터링, 사용자-아이템 그래프, 유사도 기반 추천 엔진 [HIGH] | §6 참조 | <!-- v12_C09b_268 v26 -->
| 57 | **RadixAttention 대화 캐싱** | RadixAttention 대화 캐싱: 접두사 공유 기반 KV Cache 최적화, 대화 트리 구조 캐시 [HIGH] | §6 참조 | <!-- v12_C09b_440 v26 -->
| 73 | **지식그래프 + 멀티모달 통합** | 지식그래프 + 멀티모달: Neo4j 노드에 이미지/오디오 임베딩 연결, 크로스모달 검색 [HIGH] | §6 참조 | <!-- v12_C12_056 v26 -->
| 82 | **자동 온톨로지 구축** | 자동 온톨로지 구축: 문서->엔티티/관계 자동 추출->온톨로지 스키마 생성, 도메인 적응 [HIGH] | §6 참조 | <!-- v12_C12_196 v26 -->
| | **-- v12 HIGH 추가: UI/UX --** | | | <!-- feature_id v26 -->
| 12 | **Next.js Web UI (IDEA-P6-UX)** | Next.js 기반 웹 UI: 반응형 레이아웃, SSR/SSG 하이브리드, API Routes, IDEA-P6-UX 디자인 시스템 적용 [HIGH] | §6 참조 | <!-- v12_C01a_169 v26 -->
| 26 | **IDE Extension UI** | IDE Extension UI: VSCode/JetBrains 확장 인터페이스, 인라인 코드 완성, 사이드바 패널, 설정 뷰 [HIGH] | §6 참조 | <!-- v12_C05_099 v26 -->
| 27 | **UI 상태머신 상세 (P7)** | UI 상태머신 P7 상세: 각 상태 전이 조건/액션 상세 정의, 에러 상태 핸들링, 복구 경로 명시 [HIGH] | §6 참조 | <!-- v12_C05_104 v26 -->
| 54 | **NotebookLM Audio Overviews UI** | NotebookLM Audio Overviews UI: 문서->오디오 요약 생성 인터페이스, 재생기, 챕터 탐색 [HIGH] | §6 참조 | <!-- v12_C09b_433 v26 -->
| 55 | **Artifacts UI** | Artifacts UI: 코드/문서/차트 등 생성물 독립 패널, 버전 관리, 편집/내보내기 [HIGH] | §6 참조 | <!-- v12_C09b_435 v26 -->
| 56 | **Canvas UI** | Canvas UI: 실시간 협업 편집 캔버스, AI 인라인 수정, 히스토리 타임라인 [HIGH] | §6 참조 | <!-- v12_C09b_436 v26 -->
| | **-- v12 MEDIUM 추가: Agent --** | | | <!-- feature_id v26 -->
| 95 | **Predictive Agent** | Predictive Agent: 사용자 행동 예측 기반 선제적 제안, ML 모델 학습/추론 파이프라인 [MEDIUM] | §6 참조 | <!-- v12_C03_069 v26 -->
| 96 | **Desktop Automation Agent** | Desktop Automation Agent: RPA 기반 데스크톱 작업 자동화, 화면 인식, 키보드/마우스 제어 [MEDIUM] | §6 참조 | <!-- v12_C03_176 v26 -->
| 101 | **IDEA Long-term Planning** | IDEA Long-term Planning: 장기 목표 설정/분해/추적, 마일스톤 관리, 진척도 시각화 [MEDIUM] | §6 참조 | <!-- v12_C03_236 v26 -->
| 103 | **자율 소스 발견 UI** | 자율 소스 발견 UI: AI 기반 데이터 소스 자동 탐색 결과 표시, 승인/거부 인터페이스 [MEDIUM] | §6 참조 | <!-- v12_C05_102 v26 -->
| 105 | **AgentMarketplaceSchema 모델** | AgentMarketplaceSchema: 에이전트 등록/검색/평가 데이터 모델, 버전/호환성 메타데이터 [MEDIUM] | §6 참조 | <!-- v12_C06_042 v26 -->
| 117 | **데스크톱 자동화** | 데스크톱 자동화: Playwright/PyAutoGUI 기반 GUI 자동화, 매크로 기록/재생 [MEDIUM] | §6 참조 | <!-- v12_C09b_301 v26 -->
| 118 | **데이터 동기화** | 데이터 동기화: CRDT 기반 분산 동기화, 오프라인 우선, 충돌 자동 해결 [MEDIUM] | §6 참조 | <!-- v12_C09b_310 v26 -->
| 135 | **MoA(Mixture of Agents) 패턴 구현** | MoA(Mixture of Agents) 패턴: 다중 모델 병렬 실행->결과 집계, 품질/비용 최적 조합 [MEDIUM] | §6 참조 | <!-- v12_C11_013 v26 -->
| 139 | **3채널 감정 분석 아키텍처** | 3채널 감정 분석: 텍스트/음성/표정 3채널 감정 병합 분석, 가중 평균 신뢰도 산출 [MEDIUM] | §6 참조 | <!-- v12_C11_065 v26 -->
| 144 | **마켓 레짐 자동 감지** | 마켓 레짐 자동 감지: HMM 기반 시장 상태 분류(강세/약세/횡보), 전략 자동 전환 [MEDIUM] | §6 참조 | <!-- v12_C11_233 v26 -->
| 146 | **주간/월간 정기 분석 리포트** | 주간/월간 정기 분석 리포트: 포트폴리오 성과/시장 동향/리스크 정기 자동 리포트 생성 [MEDIUM] | §6 참조 | <!-- v12_C11_237 v26 -->
| 147 | **DeFi 프로토콜 분석** | DeFi 프로토콜 분석: TVL/APY/리스크 자동 분석, 프로토콜 비교, 수익 시뮬레이션 [MEDIUM] | §6 참조 | <!-- v12_C11_242 v26 -->
| 163 | **Dream Mode 멀티모달 백그라운드 생성** | Dream Mode 멀티모달 백그라운드: 유휴 시간 멀티모달 콘텐츠 자동 생성 파이프라인 [MEDIUM] | §6 참조 | <!-- v12_C12_072 v26 -->
| 166 | **A2A 에이전트 디스커버리** | A2A 에이전트 디스커버리: 에이전트 자동 발견/등록/해제, 서비스 레지스트리 연동 [MEDIUM] | §6 참조 | <!-- v12_C12_101 v26 -->
| 167 | **Magentic-One 아키텍처 패턴** | Magentic-One 아키텍처: Orchestrator+Specialist 패턴, 동적 역할 할당, 컨텍스트 공유 [MEDIUM] | §6 참조 | <!-- v12_C12_109 v26 -->
| | **-- v12 MEDIUM 추가: Benchmark --** | | | <!-- feature_id v26 -->
| 123 | **ARC-AGI 벤치마크** | ARC-AGI 벤치마크: 추상 추론 능력 평가, 패턴 인식 테스트 세트 통합 [MEDIUM] | §6 참조 | <!-- v12_C09b_461 v26 -->
| 124 | **PolyBench** | PolyBench: 다국어 벤치마크 통합, 한국어 특화 평가 데이터셋 포함 [MEDIUM] | §6 참조 | <!-- v12_C09b_463 v26 -->
| 125 | **MMLU-Pro** | MMLU-Pro: 확장 MMLU 벤치마크, 전문 지식 영역 평가, 난이도별 분류 [MEDIUM] | §6 참조 | <!-- v12_C09b_464 v26 -->
| 142 | **VBS-8 에이전트 협업 벤치마크** | VBS-8 에이전트 협업 벤치마크: 팀 시너지 측정, 통신 효율, 작업 분배 최적성 평가 [MEDIUM] | §6 참조 | <!-- v12_C11_174 v26 -->
| 143 | **인간 평가 프로세스** | 인간 평가 프로세스: 평가자 풀 관리, 평가 UI, 평가자 간 일치도(Cohen's Kappa) 계산 [MEDIUM] | §6 참조 | <!-- v12_C11_178 v26 -->
| 169 | **코드 품질 대시보드** | 코드 품질 대시보드: 커버리지/복잡도/중복/보안 취약점 실시간 모니터링 대시보드 [MEDIUM] | §6 참조 | <!-- v12_C12_172 v26 -->
| | **-- v12 MEDIUM 추가: Blue Nodes --** | | | <!-- feature_id v26 -->
| 88 | **E-10 Personalized Teaching Mode** | E-10 개인화 교수 모드: 학습자 프로필 기반 교수법 자동 조정, 난이도 적응, 피드백 개인화 [MEDIUM] | §6 참조 | <!-- v12_C01a_072 v26 -->
| 99 | **Networking Agent** | Networking Agent: 인맥 관리, 커뮤니케이션 최적화, 관계 분석, 네트워킹 제안 [MEDIUM] | §6 참조 | <!-- v12_C03_218 v26 -->
| 100 | **Mindfulness Agent** | Mindfulness Agent: 마음챙김/명상 가이드, 스트레스 레벨 모니터링, 맞춤 루틴 제안 [MEDIUM] | §6 참조 | <!-- v12_C03_219 v26 -->
| 104 | **CloudLibrary Gate 검증 결과 스키마** | CloudLibrary Gate 검증 결과: CL-G0~G4 게이트 통과/실패 결과 스키마, 감사 로그 연동 [MEDIUM] | §6 참조 | <!-- v12_C06_024 v26 -->
| 111 | **TradingAnalysisAgent 구현** | TradingAnalysisAgent: 기술적/기본적 분석 자동화, 매매 신호 생성, 포지션 관리 [MEDIUM] | §6 참조 | <!-- v12_C08_015 v26 -->
| 128 | **SEC 13F 자동 분석** | SEC 13F 자동 분석: 기관투자자 포트폴리오 공시 자동 수집/분석, 변동 추적 [MEDIUM] | §6 참조 | <!-- v12_C09b_475 v26 -->
| 152 | **실시간 비디오/카메라 입력 처리** | 실시간 비디오/카메라 입력: WebRTC 기반 실시간 비디오 스트림 처리, 프레임 분석 [MEDIUM] | §6 참조 | <!-- v12_C12_006 v26 -->
| 153 | **음악/사운드 생성** | 음악/사운드 생성: MusicGen/AudioCraft 기반 음악 생성, 텍스트->음악 변환 [MEDIUM] | §6 참조 | <!-- v12_C12_025 v26 -->
| 154 | **음성 복제 및 개인화** | 음성 복제 및 개인화: 소량 샘플 기반 음성 클론, 화자 적응 TTS, 감정 표현 [MEDIUM] | §6 참조 | <!-- v12_C12_026 v26 -->
| 155 | **오디오 감정 분석** | 오디오 감정 분석: 음성 톤/속도/강도 분석, 감정 레이블링, 실시간 스트림 처리 [MEDIUM] | §6 참조 | <!-- v12_C12_029 v26 -->
| 156 | **팟캐스트/오디오 콘텐츠 자동 생성** | 팟캐스트/오디오 자동 생성 확장: 다중 화자 대화 생성, 편집 자동화, 배포 연동 [MEDIUM] | §6 참조 | <!-- v12_C12_030 v26 -->
| 157 | **비디오 생성 모델 통합** | 비디오 생성 모델 통합: Sora/Runway/Pika 등 비디오 생성 API 통합, 프롬프트->비디오 [MEDIUM] | §6 참조 | <!-- v12_C12_033 v26 -->
| 158 | **스크린 레코딩 + AI 편집** | 스크린 레코딩 + AI 편집: 화면 녹화->자동 하이라이트/편집/요약, 튜토리얼 자동 생성 [MEDIUM] | §6 참조 | <!-- v12_C12_036 v26 -->
| 160 | **멀티모달 합성 (Composition)** | 멀티모달 합성 확장: 이미지+텍스트+차트+오디오 복합 출력, 자동 레이아웃 최적화 [MEDIUM] | §6 참조 | <!-- v12_C12_062 v26 -->
| 164 | **최신 비디오 이해 모델 통합** | 최신 비디오 이해 모델: VideoLLaMA2/InternVideo2 등 최신 모델 통합, 성능 비교 평가 [MEDIUM] | §6 참조 | <!-- v12_C12_078 v26 -->
| 170 | **이메일/메시지 지식 추출** | 이메일/메시지 지식 추출: 이메일/채팅 본문->구조화 지식 추출, 태깅, 지식 그래프 연동 [MEDIUM] | §6 참조 | <!-- v12_C12_180 v26 -->
| | **-- v12 MEDIUM 추가: Business --** | | | <!-- feature_id v26 -->
| 106 | **재무 시계열 DB 스키마 (투자)** | 재무 시계열 DB 스키마: OHLCV 시계열 저장, 인덱싱 전략, 파티셔닝 정책 [MEDIUM] | §6 참조 | <!-- v12_C06_067 v26 -->
| 107 | **멀티 전략 포트폴리오 모델** | 멀티 전략 포트폴리오: 전략별 가중치/성과/리스크 모델, 리밸런싱 규칙 스키마 [MEDIUM] | §6 참조 | <!-- v12_C06_073 v26 -->
| 108 | **백테스팅 결과 스키마 (투자)** | 백테스팅 결과 스키마: 시뮬레이션 결과 저장 모델(수익률/MDD/Sharpe/거래 이력) [MEDIUM] | §6 참조 | <!-- v12_C06_075 v26 -->
| 109 | **포트폴리오 최적화 결과 스키마 (투자)** | 포트폴리오 최적화 결과: 최적화 알고리즘 출력 스키마(가중치/제약조건/목적함수값) [MEDIUM] | §6 참조 | <!-- v12_C06_076 v26 -->
| 110 | **투자 추천 사후 검증 스키마** | 투자 추천 사후 검증: 추천 대비 실제 성과 비교 스키마, 정확도 메트릭 [MEDIUM] | §6 참조 | <!-- v12_C06_077 v26 -->
| 112 | **Kelly Criterion 포지션 사이징** | Kelly Criterion 포지션 사이징: 최적 투자 비율 계산, 변형 Kelly(Half-Kelly) 지원 [MEDIUM] | §6 참조 | <!-- v12_C08_045 v26 -->
| 113 | **Risk Parity 가중치 계산** | Risk Parity 가중치 계산: 위험 기여도 균등 배분 알고리즘, 공분산 행렬 기반 최적화 [MEDIUM] | §6 참조 | <!-- v12_C08_046 v26 -->
| 126 | **MCP 생태계 수익 모델** | MCP 생태계 수익 모델: MCP 마켓플레이스 과금 체계, 개발자 수익 분배 정책 [MEDIUM] | §6 참조 | <!-- v12_C09b_467 v26 -->
| 127 | **오픈소스 듀얼 라이선스** | 오픈소스 듀얼 라이선스: AGPL + Commercial 라이선스 정책, 기여자 계약(CLA) [MEDIUM] | §6 참조 | <!-- v12_C09b_470 v26 -->
| | **-- v12 MEDIUM 추가: Infra --** | | | <!-- feature_id v26 -->
| 89 | **Plugin/Extension SDK** | Plugin/Extension SDK: 서드파티 확장 개발 도구, API 문서, 샘플 프로젝트, 배포 가이드 [MEDIUM] | §6 참조 | <!-- v12_C01a_176 v26 -->
| 91 | **INT4 Quantization (QAT)** | INT4 Quantization (QAT): 양자화 인식 학습 기반 INT4 모델 최적화, 정확도 손실 최소화 [MEDIUM] | §6 참조 | <!-- v12_C01a_191 v26 -->
| 131 | **Speculative Decoding** | Speculative Decoding 구현: Draft 모델 기반 추측 디코딩, 검증 파이프라인 [MEDIUM] | §6 참조 | <!-- v12_C09b_558 v26 -->
| 136 | **Cross-Device Seamless Sync** | Cross-Device Sync: 디바이스 간 설정/상태/대화 동기화, WebSocket 기반 실시간 전파 [MEDIUM] | §6 참조 | <!-- v12_C11_034 v26 -->
| 141 | **모델 드리프트 감지** | 모델 드리프트 감지: 모델 출력 품질 시계열 모니터링, 통계적 드리프트 탐지, 자동 알림 [MEDIUM] | §6 참조 | <!-- v12_C11_157 v26 -->
| 162 | **크로스 디바이스 멀티모달 동기화** | 크로스 디바이스 멀티모달 동기화: 디바이스 간 멀티모달 세션 이관, 미디어 스트림 핸드오프 [MEDIUM] | §6 참조 | <!-- v12_C12_071 v26 -->
| 165 | **합성 데이터 생성** | 합성 데이터 생성: LLM 기반 학습/평가용 합성 데이터 생성, 품질 검증 파이프라인 [MEDIUM] | §6 참조 | <!-- v12_C12_082 v26 -->
| 168 | **에이전트 패키징** | 에이전트 패키징 확장: 의존성 자동 해결, 멀티 플랫폼 빌드, 서명/검증 [MEDIUM] | §6 참조 | <!-- v12_C12_139 v26 -->
| | **-- v12 MEDIUM 추가: Orange Core --** | | | <!-- feature_id v26 -->
| 93 | **Emotion History Tracking** | Emotion History Tracking: 사용자 감정 이력 저장/시각화, 추세 분석, 장기 패턴 감지 [MEDIUM] | §6 참조 | <!-- v12_C02_152 v26 -->
| 94 | **Trigger/Action Automation** | Trigger/Action Automation: 조건부 자동 실행 규칙 엔진, 이벤트 트리거->액션 매핑 [MEDIUM] | §6 참조 | <!-- v12_C02_186 v26 -->
| 121 | **Responses API (OpenAI)** | Responses API (OpenAI): OpenAI Responses API 패턴 호환, 스트리밍/도구호출 통합 [MEDIUM] | §6 참조 | <!-- v12_C09b_415 v26 -->
| 130 | **추론 UX 패턴** | 추론 UX 패턴: 사고 과정 시각화, 단계별 추론 표시, 신뢰도 게이지 UI [MEDIUM] | §6 참조 | <!-- v12_C09b_551 v26 -->
| 137 | **Gemini 스타일 멀티모달 대화 처리** | Gemini 스타일 멀티모달 대화: 텍스트+이미지+오디오 통합 대화 처리, 모달 전환 [MEDIUM] | §6 참조 | <!-- v12_C11_046 v26 -->
| 171 | **그래프 추론** | 그래프 추론: 지식 그래프 기반 다단계 추론, 경로 탐색, 관계 기반 질의 응답 [MEDIUM] | §6 참조 | <!-- v12_C12_197 v26 -->
| | **-- v12 MEDIUM 추가: Storage --** | | | <!-- feature_id v26 -->
| 98 | **Data Sync Agent** | Data Sync Agent: 다중 저장소 간 데이터 동기화, 충돌 해결, 증분 동기화 전략 [MEDIUM] | §6 참조 | <!-- v12_C03_185 v26 -->
| 133 | **소스 간 충돌 해결 엔진** | 소스 간 충돌 해결 엔진: 다중 데이터 소스 정보 불일치 자동 감지, 신뢰도 기반 해결 [MEDIUM] | §6 참조 | <!-- v12_C10_082 v26 -->
| 159 | **비디오/오디오 RAG** | 비디오/오디오 RAG 확장: 멀티미디어 청크 인덱싱 고도화, 시간 구간 기반 정밀 검색 [MEDIUM] | §6 참조 | <!-- v12_C12_055 v26 -->
| | **-- v12 MEDIUM 추가: UI/UX --** | | | <!-- feature_id v26 -->
| 90 | **Chrome Extension** | Chrome Extension: 브라우저 사이드바 에이전트, 페이지 컨텍스트 분석, 빠른 질의 인터페이스 [MEDIUM] | §6 참조 | <!-- v12_C01a_183 v26 -->
| 102 | **모듈 매니저 탭** | 모듈 매니저 탭: 모듈 목록/상태 대시보드, 활성화/비활성화 UI, 의존성 시각화 [MEDIUM] | §6 참조 | <!-- v12_C05_005 v26 -->
| 119 | **멀티모달 학습 콘텐츠** | 멀티모달 학습 콘텐츠: 텍스트+이미지+비디오+퀴즈 복합 학습 자료 자동 생성 [MEDIUM] | §6 참조 | <!-- v12_C09b_360 v26 -->
| 134 | **오버레이 패널 즉시 분석** | 오버레이 패널 즉시 분석: 콘텐츠 위 오버레이로 AI 즉시 분석 결과 표시, 하이라이트 연동 [MEDIUM] | §6 참조 | <!-- v12_C10_092 v26 -->
| 138 | **대화 분기(Fork) 관리** | 대화 분기(Fork) 관리: 대화 트리 분기/병합 UI, 분기점 시각화, 브랜치 비교 [MEDIUM] | §6 참조 | <!-- v12_C11_051 v26 -->
| 140 | **음성 모드 대화 UI** | 음성 모드 대화 UI: 음성 입력/출력 전용 인터페이스, 웨이브폼 시각화, 핸즈프리 모드 [MEDIUM] | §6 참조 | <!-- v12_C11_083 v26 -->
| 145 | **커스텀 조건 알림 규칙 엔진** | 커스텀 조건 알림 규칙: 사용자 정의 조건식(가격/지표/이벤트)->알림 트리거 규칙 엔진 [MEDIUM] | §6 참조 | <!-- v12_C11_236 v26 -->
| 149 | **교육용 가상 투자 시뮬레이터** | 교육용 가상 투자 시뮬레이터: 페이퍼 트레이딩 환경, 학습 모드, 성과 비교 리더보드 [MEDIUM] | §6 참조 | <!-- v12_C11_254 v26 -->
| 161 | **멀티모달 대화 모드 전환** | 멀티모달 대화 모드 전환: 텍스트<->음성<->비디오 모드 원활한 전환 UI, 상태 보존 [MEDIUM] | §6 참조 | <!-- v12_C12_063 v26 -->
| | **-- v12 LOW 추가: Agent --** | | | <!-- feature_id v26 -->
| 186 | **한국 문화 맥락 감정 해석** | 한국 문화 맥락 감정 해석: 한국어 존댓말/비언어적 표현/문화적 뉘앙스 감정 분석 특화 [LOW] | §6 참조 | <!-- v12_C11_066 v26 -->
| 188 | **토큰 이코노믹스 분석** | 토큰 이코노믹스 분석: 크립토 토큰 경제 모델 분석, 인플레이션/디플레이션 시뮬레이션 [LOW] | §6 참조 | <!-- v12_C11_243 v26 -->
| | **-- v12 LOW 추가: Benchmark --** | | | <!-- feature_id v26 -->
| 185 | **LiveBench 동적 벤치마크 통합** | LiveBench 동적 벤치마크: 주기적 갱신 벤치마크 통합, 오염 방지 신규 문제 자동 생성 [LOW] | §6 참조 | <!-- v12_C11_023 v26 -->
| | **-- v12 LOW 추가: Blue Nodes --** | | | <!-- feature_id v26 -->
| 173 | **CloudLibrary 충돌 해결 스키마** | CloudLibrary 충돌 해결 스키마: 동시 수정 충돌 감지/해결 데이터 모델, CRDT 기반 [LOW] | §6 참조 | <!-- v12_C06_025 v26 -->
| 174 | **CloudLibrary 버전 변경 스키마** | CloudLibrary 버전 변경 스키마: 콘텐츠 버전 이력 데이터 모델, diff/merge 메타데이터 [LOW] | §6 참조 | <!-- v12_C06_026 v26 -->
| | **-- v12 LOW 추가: Business --** | | | <!-- feature_id v26 -->
| 175 | **다자산 상관관계 행렬 모델** | 다자산 상관관계 행렬: 자산 간 상관계수 행렬 모델, 동적 상관관계 추적 [LOW] | §6 참조 | <!-- v12_C06_086 v26 -->
| | **-- v12 LOW 추가: Infra --** | | | <!-- feature_id v26 -->
| 176 | **스킬 벤더 인증 마크 시스템** | 스킬 벤더 인증 마크: 서드파티 스킬 품질 인증 체계, 인증 배지, 검증 프로세스 [LOW] | §6 참조 | <!-- v12_C08_096 v26 -->
| | **-- v12 LOW 추가: MCP --** | | | <!-- feature_id v26 -->
| 187 | **특허 분석 및 온체인 대안 데이터** | 특허 분석 및 온체인 대안 데이터: 특허 DB 검색/분석, 온체인 대안 데이터 소스 통합 [LOW] | §6 참조 | <!-- v12_C11_212 v26 -->
| 189 | **크립토 에어드랍/이벤트 추적** | 크립토 에어드랍/이벤트 추적: 에어드랍/IDO/이벤트 자동 감지, 자격 확인, 알림 [LOW] | §6 참조 | <!-- v12_C11_245 v26 -->
| | **-- v12 LOW 추가: Orange Core --** | | | <!-- feature_id v26 -->
| 179 | **Pixtral Large** | Pixtral Large 통합: Mistral Pixtral 비전 모델 통합, 이미지 분석 파이프라인 [LOW] | §6 참조 | <!-- v12_C09b_421 v26 -->
| 180 | **Grok (xAI)** | Grok (xAI) 통합: xAI Grok 모델 통합, 실시간 정보 활용, API 연동 [LOW] | §6 참조 | <!-- v12_C09b_423 v26 -->
| 181 | **Yi-Lightning (01.AI)** | Yi-Lightning (01.AI) 통합: 01.AI Yi-Lightning 모델 통합, 고속 추론 활용 [LOW] | §6 참조 | <!-- v12_C09b_424 v26 -->
| | **-- v12 LOW 추가: UI/UX --** | | | <!-- feature_id v26 -->
| 183 | **오디오 요약 생성 (NotebookLM 스타일)** | 오디오 요약 생성: NotebookLM 스타일 문서->대화형 오디오 요약, 다중 화자 생성 [LOW] | §6 참조 | <!-- v12_C11_014 v26 -->

### 산출물 참조
- COND 모듈 카탈로그: `D2.0-01 §5.6` (모듈 분류 정본)
- I-Series 상세: `D2.0-02 §7` (모듈별 순차 번호)
- E-Series 상세: `D2.0-03` (External Integration 정본)
- SDAR 스펙: `VAMOS_SDAR_DESIGN_SPECIFICATION` (I-25 AR-L3)
- Cloud Library: `VAMOS_CLOUD_LIBRARY_SPEC` (E-15 + RT-BNP + DCL)

### 실행 가이드

#### 사용자 직접 작업
1. **COND 활성화 조건 확인**: V1→V2 전환 조건 6항 충족 여부 검증 (QoD ≥ 0.85, RAG accuracy ≥ 60% 등)
2. **외부 서비스 API 키 발급**: Google Calendar API (E-13), Gmail API (E-14), Cloud Storage API (E-16) OAuth 설정
3. **RSS 피드 소스 등록**: RT-BNP V1용 금융 뉴스 RSS URL 목록 + DCL-GEO용 지정학/시사 RSS URL 목록 준비
4. **config.v2.toml 모듈 활성화**: 각 COND 모듈 `enabled = true` 전환 및 API 키 설정
5. **각 모듈 통합 테스트**: 116개 모듈 개별 활성화 후 기능 동작 검증 → 카테고리별 활성화 → 전체 활성화 후 상호작용 검증
6-1. **v10 확장 모듈 우선순위 배치**: HIGH(94개) → MEDIUM(8개) → LOW(4개) 순서로 카테고리별 배치 구현
6. **SDAR AR-L3 승인 정책 설정**: MEDIUM risk 자동 수리 범위 확인 + 승인 임계값 설정

#### AI 프롬프트

````text
VAMOS 프로젝트 V2-Phase 2: COND 모듈 활성화를 진행합니다.

## 작업 목표
V2 COND 모듈 116개(원본 10 + v10 확장 106)를 구현하고 활성화합니다.
원본 10개는 개별 상세 구현, v10 확장 106개는 7개 카테고리 그룹 단위 구현.
각 모듈은 기본 OFF이며, config에서 enabled=true로 전환 시 동작합니다.
Module Catalog 표준 필드(D2.0-01 §5.5 LOCK) 준수.

## 1. I-7 Project/Session Manager → `backend/vamos_core/modules/i07_project_session_manager.py`
- 프로젝트 컨텍스트 관리: 프로젝트별 세션 그룹핑, 메타데이터 관리
- session_end 3조건 적용 (PART2 V0-STEP-5 정의):
  (1) 사용자 명시 종료
  (2) idle_timeout(30분) 만료
  (3) max_turns 도달 (V0 기본=50, V2 I-7 config=100)
- 의존성: I-1(IntentDetector), I-3(ContextAggregator)
- 산출물: D2.0-02 §7.54~7.56

## 2. I-12 Workflow Builder → `backend/vamos_core/modules/i12_workflow_builder.py`
- 자기진화 스케줄러: 사용자 정의 워크플로우 생성/실행/스케줄링
- LangGraph StateGraph 기반 서브 워크플로우 정의
- 의존성: I-5(DecisionEngine), I-8(AutonomyManager)
- 산출물: D2.0-02 §7.69~7.71

## 3. I-22 Task/Project Manager → `backend/vamos_core/modules/i22_task_project_manager.py`
- 태스크 CRUD + 프로젝트 단위 태스크 그룹핑
- 우선순위(P0~P3) + 상태(todo/in_progress/done/blocked) 관리
- E-13(Calendar)과 연동하여 일정 동기화
- 산출물: D2.0-01 §5.6

## 4. I-23 Doc/Code Structuring → `backend/vamos_core/modules/i23_doc_code_structuring.py`
- 문서/코드 자동 구조화: 마크다운 → 섹션 트리, 코드 → AST 분석
- 구조 메타데이터를 L1 Memory에 저장
- 산출물: D2.0-01 §5.6

## 5. I-25 SDAR Engine (AR-L2→AR-L3) → `backend/vamos_core/modules/i25_sdar_engine.py`
- 자가진단/자동수리 엔진 (AR-L3 확장)
- AR-L2(V1): LOW risk 자동 수리 (config 복원, 캐시 정리)
- AR-L3(V2 추가): MEDIUM risk 자동 수리 5개 액션 (SDAR_SPEC §10.2 정본):
  (1) patch_prompt_template — 프롬프트 템플릿 패치
  (2) update_config_parameter — config 파라미터 업데이트
  (3) rotate_api_key — API 키 로테이션
  (4) rollback_to_snapshot — 스냅샷 롤백
  (5) compress_logs — 로그 압축
- 5-Gate(BaseGate) 코드 공유 (PART2 §6.9)
- 산출물: VAMOS_SDAR_DESIGN_SPECIFICATION

## 6. A-4 Debate Mode → `backend/vamos_core/modules/a04_debate_mode.py`
- Bull vs Bear 토론 모드: 두 LLM 에이전트가 찬반 논증
- 최종 종합 판단은 Lead Agent가 수행
- Agent Teams V1 인프라 활용 (V2에서 Redis MessageBus 전환 후)
- 산출물: D2.0-01 §5.9

## 7. E-13 Calendar/Task Sync → `backend/vamos_core/modules/e13_calendar_task_sync.py`
- Google Calendar API 연동 (OAuth 2.0)
- 캘린더 이벤트 ↔ VAMOS 태스크 양방향 동기화
- 알림/리마인더 설정
- 산출물: D2.0-03

## 8. E-14 Email Handler → `backend/vamos_core/modules/e14_email_handler.py`
- Gmail API 연동 (OAuth 2.0)
- 이메일 검색, 요약, 분류, 자동 응답 초안 생성
- LLM 기반 이메일 내용 분석
- 산출물: D2.0-03

## 9. E-15 Cloud Collector + RT-BNP V1 + DCL-GEO V2 → `backend/vamos_core/modules/e15_cloud_collector.py`
- Cloud Library 수집 파이프라인: 7-Stage Discovery (V2)
- RT-BNP V1: RSS 60초 폴링 + 키워드 Breaking Detector
  - Breaking 조건: 특정 키워드 빈도 급증 (threshold 설정)
  - 감지 시 VamosState에 breaking_news 플래그 설정
- DCL-GEO V2: 지정학/시사 RSS 5분 폴링 + Breaking Detector 확장
  - 지정학 키워드 사전 관리 (config.v2.toml [dcl.geo])
- 산출물: VAMOS_CLOUD_LIBRARY_SPEC §7, §6.10.1, §6.10.2

## 10. E-16 Cloud Storage Sync → `backend/vamos_core/modules/e16_cloud_storage_sync.py`
- Google Drive / OneDrive / S3 연동
- 양방향 파일 동기화 + 버전 관리
- 대용량 파일 청크 업로드/다운로드
- 산출물: D2.0-03

---

## v10 COND 확장 모듈 (106개, #11~#116) — 카테고리 그룹 구현

> v10 Phase 2에서 추가된 106개 COND 모듈은 7개 카테고리로 그룹화하여 배치 구현합니다.
> 각 카테고리는 공통 BaseModule 패턴 + 카테고리별 Mixin으로 구현.
> 우선순위: HIGH(94개) → MEDIUM(8개) → LOW(4개).

### CAT-A: AI/ML 엔진 (13개)
모듈: #11 SHAP/LIME Explainability, #12 배치 처리, #13 시간 여행 디버깅, #14 모델 A/B 테스팅,
#15 작업 패턴 프로파일, #25 감정 패턴 학습, #26 편향 감사 엔진, #85 CrewAI 역할 패턴,
#102 Qwen 3 한중일 특화, #103 FinGPT 활용, #104 Ambient Intelligence,
#105 S5 피드백 학습 [MEDIUM], #106 C3 규칙 제안 [MEDIUM]
- 디렉토리: `backend/vamos_core/modules/cond_ai_ml/`
- 공통 의존성: I-5(DecisionEngine), M-11(PromptManager)
- Mixin: `AiMlModuleMixin` — 모델 추론 래퍼, 배치 스케줄링, 결과 캐싱
- config 그룹: `[modules.cond.cat_a_ai_ml]`

### CAT-B: 지식관리 (13개)
모듈: #17 MemGPT/Letta 통합, #18 Cognee AI KG, #19 지식 신선도, #20 지식 충돌 감지,
#21 M-020 Notion/Obsidian 임포트, #22 M-004 스크린 캡처 지식화, #23 M-016 시간 기반 지식 관리,
#24 M-043 예측적 지식 서핑, #87 개인 위키, #88 예측적 지식 서핑(S7JM),
#89 지식 기반 개인 어시스턴트, #107 형태소 분석 토큰화 [MEDIUM], #108 Zettelkasten 심화 [MEDIUM]
- 디렉토리: `backend/vamos_core/modules/cond_knowledge/`
- 공통 의존성: I-3(ContextAggregator), M-05(L1MemoryProvider), I-7(ProjectSessionManager)
- Mixin: `KnowledgeModuleMixin` — KG 연동, 벡터 검색, 지식 그래프 CRUD
- config 그룹: `[modules.cond.cat_b_knowledge]`

### CAT-C: 운영/인프라 (53개)
모듈: #27 국제화, #28 접근성, #29 버전 관리, #30 분산 트레이싱, #31 백프레셔, #32 CQRS,
#33 사가 패턴, #34 읽기 복제본, #35~#73 E-024~E-092 운영 모듈(39개),
#74 작업 큐 서버, #75 검색 엔진 서버, #76 알림 서버, #77 피처 스토어, #78 CDN, #79 다중 리전 복제
- 디렉토리: `backend/vamos_core/modules/cond_ops/`
- 공통 의존성: 인프라 레이어 (Redis, PostgreSQL, Prometheus)
- Mixin: `OpsModuleMixin` — 헬스체크, 메트릭 수집, 서킷브레이커
- config 그룹: `[modules.cond.cat_c_ops]`
- 참고: E-0xx 운영 모듈은 `cond_ops/external/` 하위에 배치

### CAT-D: 미디어/생성 (8개)
모듈: #16 개인 멀티미디어 라이브러리, #80 스타일 트랜스퍼, #81 로고/아이콘 생성,
#82 화자 분리, #83 양식/폼 자동 생성, #84 크로스모달 검색, #86 코드 변환,
#109 인포그래픽 자동 생성 [MEDIUM]
- 디렉토리: `backend/vamos_core/modules/cond_media/`
- 공통 의존성: E-15(CloudCollector), M-07(OutputFormatter)
- Mixin: `MediaModuleMixin` — 멀티미디어 파이프라인, 포맷 변환, 스토리지 연동
- config 그룹: `[modules.cond.cat_d_media]`

### CAT-E: 교육/학습 (7개)
모듈: #91 개인화 학습 경로, #92 시험 준비 도우미, #93 교육 컨텐츠 생성, #94 교육 평가 도구,
#113 대화형 튜토리얼 [LOW], #114 학습 분석 대시보드 [LOW], #115 언어 학습 특화 [LOW]
- 디렉토리: `backend/vamos_core/modules/cond_education/`
- 공통 의존성: I-1(IntentDetector), M-11(PromptManager), A-4(DebateMode)
- Mixin: `EducationModuleMixin` — 학습 진도 추적, 퀴즈 생성, 적응형 난이도
- config 그룹: `[modules.cond.cat_e_education]`

### CAT-F: 웰빙/건강 (8개)
모듈: #95 수면 개선, #96 운동/피트니스 트래커, #97 식단/영양 관리, #98 감정 일지 분석,
#99 사회적 관계 관리, #100 개인화 건강 인사이트, #101 감정 기반 음악 추천,
#116 웰빙 대시보드 [LOW]
- 디렉토리: `backend/vamos_core/modules/cond_wellbeing/`
- 공통 의존성: I-7(ProjectSessionManager), E-13(CalendarSync)
- Mixin: `WellbeingModuleMixin` — 건강 데이터 수집, 트렌드 분석, 알림 스케줄링
- config 그룹: `[modules.cond.cat_f_wellbeing]`

### CAT-G: 외부통합 확장 (4개)
모듈: #90 Notion/Obsidian 통합, #110 ETL 도구 [MEDIUM], #111 Zapier/Make 호환 [MEDIUM],
#112 JIRA/Linear 통합 [MEDIUM]
- 디렉토리: `backend/vamos_core/modules/cond_integration/`
- 공통 의존성: E-13~E-16(기존 외부통합 모듈), I-22(TaskProjectManager)
- Mixin: `IntegrationModuleMixin` — OAuth 플로우, 웹훅 수신, API 어댑터 패턴
- config 그룹: `[modules.cond.cat_g_integration]`

### v10 공통 규칙
- 모든 v10 모듈은 BaseModule(ABC) 상속 + 카테고리별 Mixin 적용
- 파일명 규칙: `{category_prefix}_{module_number}_{snake_name}.py` (예: `ai_ml_011_shap_explainer.py`)
- 각 카테고리 디렉토리에 `__init__.py` + `_mixin.py` + `_config.py` 포함
- v10 모듈 간 의존성은 카테고리 내부 우선, 카테고리 간 의존 시 원본 10개 모듈을 브릿지로 사용
- 테스트: 카테고리별 통합 테스트 + 전체 교차 카테고리 테스트

## 규칙
> **§1.3 R1~R11 공통 규칙 전수 적용**
- 모든 모듈은 BaseModule(ABC) 상속, `enabled` 플래그로 ON/OFF 제어
- Module Catalog 표준 필드 준수 (D2.0-01 §5.5 LOCK): id, name, version, category(COND), enabled, dependencies
- COND 모듈은 기본 OFF (D2.0-01 §5.14.4 규칙)
- Python Pydantic v2 모델 사용 (model_config = ConfigDict(extra="forbid"))
- 로깅은 JSON 형식 (stderr) + LogEventSchema 7필드 준수
- LOCK/FREEZE 값 변경 금지

**config.v2.toml COND 모듈 키 목록** (FIX-20 + FIX-009): <!-- C-IMP-009 대응. 원본 10개 + v10 카테고리 7그룹 config 키 명시 -->
```toml
# === 원본 COND 모듈 (10개, 개별 config) ===
[modules.cond]
i07.enabled = false          # Project/Session Manager
i07.idle_timeout_min = 30    # 세션 유휴 타임아웃 (분)
i07.max_turns_per_session = 100
i12.enabled = false          # Workflow Builder
i12.max_subflows = 5
i22.enabled = false          # Task/Project Manager
i22.max_tasks_per_project = 200
i23.enabled = false          # Doc/Code Structuring
i23.chunk_max_tokens = 500
i25.enabled = false          # SDAR Engine
i25.ar_level = "L3"          # V2: AR-L3
i25.repair_timeout_s = 120
a04.enabled = false          # Debate Mode
a04.max_rounds = 5
e13.enabled = false          # Calendar/Task Sync
e13.sync_interval_min = 15
e14.enabled = false          # Email Handler
e14.max_emails_per_batch = 50
e15.enabled = false          # Cloud Collector
e15.rss_poll_interval_s = 60 # RT-BNP V1
e15.dcl_geo_poll_s = 300     # DCL-GEO V2
e16.enabled = false          # Cloud Storage Sync
e16.sync_interval_min = 30

# === v10 확장 COND 모듈 (106개, 카테고리 그룹 config) ===
[modules.cond.cat_a_ai_ml]       # 13개: #11~#15, #25, #26, #85, #102~#106
group_enabled = false             # 카테고리 일괄 ON/OFF
batch_size = 32                   # 배치 처리 기본 크기
model_timeout_s = 60              # 모델 추론 타임아웃
cache_ttl_s = 3600                # 결과 캐시 TTL

[modules.cond.cat_b_knowledge]   # 13개: #17~#24, #87~#89, #107, #108
group_enabled = false
kg_backend = "neo4j"              # 지식 그래프 백엔드
vector_dim = 1536                 # 임베딩 차원
freshness_check_interval_h = 24  # 지식 신선도 점검 주기

[modules.cond.cat_c_ops]         # 53개: #27~#34, #35~#73, #74~#79
group_enabled = false
health_check_interval_s = 30     # 헬스체크 주기
circuit_breaker_threshold = 5    # 서킷브레이커 실패 임계
metrics_export_interval_s = 15   # 메트릭 수출 주기

[modules.cond.cat_d_media]       # 8개: #16, #80~#84, #86, #109
group_enabled = false
max_file_size_mb = 100           # 최대 파일 크기
transcode_timeout_s = 300        # 트랜스코딩 타임아웃

[modules.cond.cat_e_education]   # 7개: #91~#94, #113~#115
group_enabled = false
adaptive_difficulty = true       # 적응형 난이도
quiz_max_questions = 20          # 퀴즈 최대 문항

[modules.cond.cat_f_wellbeing]   # 8개: #95~#101, #116
group_enabled = false
data_retention_days = 365        # 건강 데이터 보관 기간
reminder_interval_h = 4          # 알림 주기

[modules.cond.cat_g_integration] # 4개: #90, #110~#112
group_enabled = false
oauth_token_refresh_min = 55     # OAuth 토큰 갱신 주기
webhook_timeout_s = 30           # 웹훅 타임아웃
```

## 참조 SOT 문서
- D2.0-01 §5.6 (모듈 카탈로그 정본)
- D2.0-02 §7 (I-Series 모듈별 상세 정본)
- D2.0-03 (E-Series External Integration 정본)
- VAMOS_SDAR_DESIGN_SPECIFICATION (I-25 SDAR 정본)
- VAMOS_CLOUD_LIBRARY_SPEC (E-15 Cloud Library + RT-BNP + DCL 정본)
````

### 단계 완료 검증 (V2-Phase 2 → Phase 3 전환 조건)

| # | 검증 항목 | 확인 방법 | 필수 |
|---|----------|----------|:---:|
| 1 | 원본 10개 COND 모듈 코드 | 10개 모듈 파일 존재 + BaseModule 상속 + enabled 플래그 동작 | ✅ |
| 2 | Module Catalog 표준 필드 | 모든 116개 모듈 id/name/version/category(COND)/enabled/dependencies 정의 확인 | ✅ |
| 3 | COND 기본 OFF | 모든 116개 COND 모듈 초기 상태 `enabled=false` + config에서 ON 전환 동작 | ✅ |
| 4 | I-7 Project/Session | 프로젝트별 세션 그룹핑 + session_end 3조건 동작 | ✅ |
| 5 | I-12 Workflow Builder | 사용자 정의 서브 워크플로우 생성/실행 동작 | ✅ |
| 6 | I-25 SDAR AR-L2→AR-L3 | 5개 MEDIUM risk 액션 실행 + 5-Gate 통과 확인 | ✅ |
| 7 | E-13~E-16 외부 연동 | Calendar/Email/Cloud Collector/Cloud Storage 각각 동작 확인 | ✅ |
| 8 | RT-BNP V1 | RSS 60초 폴링 + 키워드 Breaking Detector 동작 | ✅ |
| 9 | DCL-GEO V2 | 지정학/시사 RSS 5분 폴링 + Breaking Detector 확장 | ✅ |
| 10 | I-22 Task/Project Manager | 태스크 생성/분배/추적 + 프로젝트 상태 관리 동작 확인 | ✅ |
| 11 | I-23 Doc/Code Structuring | 문서/코드 자동 구조화 + 템플릿 적용 동작 확인 | ✅ |
| 12 | V2 비용 모니터링 대시보드 | Grafana/Prometheus 기반 비용 추적 대시보드 구축 + ₩93,000/월 상한 알림 설정 (V2-GNG-13 대응) | ✅ |
| 13 | A-4 Debate Mode | 다중 관점 토론 실행 + 결론 도출 동작 확인 | ✅ |
| 14 | CAT-A AI/ML 엔진 (13개) | 카테고리 Mixin 적용 + group_enabled 동작 + 모델 추론 타임아웃 검증 | ✅ |
| 15 | CAT-B 지식관리 (13개) | KG 연동 + 벡터 검색 + 지식 신선도 점검 동작 확인 | ✅ |
| 16 | CAT-C 운영/인프라 (53개) | 헬스체크 + 서킷브레이커 + 메트릭 수출 동작 확인 | ✅ |
| 17 | CAT-D 미디어/생성 (8개) | 멀티미디어 파이프라인 + 포맷 변환 동작 확인 | ✅ |
| 18 | CAT-E 교육/학습 (7개) | 적응형 난이도 + 퀴즈 생성 + 학습 진도 추적 동작 확인 | ✅ |
| 19 | CAT-F 웰빙/건강 (8개) | 건강 데이터 수집 + 트렌드 분석 + 알림 동작 확인 | ✅ |
| 20 | CAT-G 외부통합 (4개) | OAuth 플로우 + 웹훅 수신 + API 어댑터 동작 확인 | ✅ |
| 21 | 카테고리별→전체 통합 테스트 | 7개 카테고리 개별 활성화 → 전체 116개 동시 활성화 상호작용 검증 | ✅ |

> ⛔ 위 필수 항목 전체 통과 전 Phase 3 진입 금지

---

## V2-Phase 3: Agent Teams V2 + 보안 (Week 10-13)

| # | 항목 | 구현 내용 | 산출물 참조 |
|---|------|----------|-----------|
| 1 | **Redis MessageBus** | In-Memory → Redis 전환 | VAMOS_AGENT_TEAMS_SPEC |
| 2 | **6가지 협업 패턴** | Sequential/Parallel/Debate/Supervisor/Handoff/**Hybrid** | VAMOS_AGENT_TEAMS_SPEC §7.1 | <!-- SOURCE_CONFLICT: §5=5개 vs §7.1 enum=6개(HYBRID 포함). §7.1 enum(코드 생성 기준) 채택. §5에 HYBRID 설명 추가 필요 -->
| 3 | **Lead + 9 Sub-Agent** | 최대 10개 에이전트 | VAMOS_AGENT_TEAMS_SPEC |
| 4 | **HMAC-SHA256** | MessageBus 인증 | VAMOS_AGENT_TEAMS_SPEC §LOCK-AT-012 |
| 5 | **LlamaGuard (L3)** | 4-Layer 중 3개 활성 (V2: L1+L2+L3, L4 사후감사는 V3) | D2.0-07 ADD-015 |
| 6 | **GDPR 기능** | 열람/이동/제한/삭제 | D2.0-07 |
| 7 | **Cloud Library V2** | 7-Stage Discovery + LLM 분석 | VAMOS_CLOUD_LIBRARY_SPEC |
| 7-1 | **RT-BNP V2** | REST API 30초 폴링 + Kafka 전파 + AI Investing 연동 | VAMOS_CLOUD_LIBRARY_SPEC §7 확장, §6.10.1 |
| 8 | **SDAR AR-L3** | MEDIUM risk 수리 5개 액션 추가 | VAMOS_SDAR_DESIGN_SPECIFICATION |
| 9 | **OAuth2 + MFA (TOTP/WebAuthn)** | OAuth2 + MFA (TOTP/WebAuthn) [HIGH] | v10 Phase 2 추가 (D207-040) | <!-- D207-040 v23 -->
| 10 | **E-054 운영** | E-054 운영 [HIGH] | v10 Phase 2 추가 (S7AE-591) | <!-- S7AE-591 v23 -->
| 11 | **E-055 운영** | E-055 운영 [HIGH] | v10 Phase 2 추가 (S7AE-592) | <!-- S7AE-592 v23 -->
| 12 | **E-056 운영** | E-056 운영 [HIGH] | v10 Phase 2 추가 (S7AE-593) | <!-- S7AE-593 v23 -->
| 13 | **E-057 운영** | E-057 운영 [HIGH] | v10 Phase 2 추가 (S7AE-594) | <!-- S7AE-594 v23 -->
| 14 | **E-058 운영** | E-058 운영 [HIGH] | v10 Phase 2 추가 (S7AE-595) | <!-- S7AE-595 v23 -->
| 15 | **E-059 운영** | E-059 운영 [HIGH] | v10 Phase 2 추가 (S7AE-596) | <!-- S7AE-596 v23 -->
| 16 | **E-060 운영** | E-060 운영 [HIGH] | v10 Phase 2 추가 (S7AE-597) | <!-- S7AE-597 v23 -->
| 17 | **방화벽 규칙** | 방화벽 규칙 [HIGH] | v10 Phase 2 추가 (S7FI-083) | <!-- S7FI-083 v23 -->
| 18 | **E-063 운영** | E-063 운영 [MEDIUM] | v10 Phase 2 추가 (S7AE-600) | <!-- S7AE-600 v23 -->
| 19 | **E-064 운영** | E-064 운영 [MEDIUM] | v10 Phase 2 추가 (S7AE-601) | <!-- S7AE-601 v23 -->
| 20 | **E-065 운영** | E-065 운영 [MEDIUM] | v10 Phase 2 추가 (S7AE-602) | <!-- S7AE-602 v23 -->
| 21 | **E-066 운영** | E-066 운영 [MEDIUM] | v10 Phase 2 추가 (S7AE-603) | <!-- S7AE-603 v23 -->
| 22 | **E-067 운영** | E-067 운영 [MEDIUM] | v10 Phase 2 추가 (S7AE-604) | <!-- S7AE-604 v23 -->
| 23 | **E-068 운영** | E-068 운영 [MEDIUM] | v10 Phase 2 추가 (S7AE-605) | <!-- S7AE-605 v23 -->
| | **── v12 BLOCKER 추가 ──** | | | <!-- v12_BLOCKER v26 -->
| 24 | **Personal Constitution 시스템** | 사용자별 가치관/규칙 엔진: PersonalConstitution 스키마(rules[], priorities[], constraints[]), 가치관 프로필(자동 학습 + 수동 설정), 의사결정 가이드라인 자동 적용(에이전트 프롬프트 주입), 규칙 충돌 해소(우선순위 기반), 규칙 버전 관리 [BLOCKER] | §6.5 참조 | <!-- v12_C13_013 v26 -->
| 25 | **EU AI Act 위험 분류 자동 평가** | 4단계 위험 분류(Unacceptable/High/Limited/Minimal) 자동 판정 파이프라인: 기능별 위험 수준 태깅 → 규정 준수 체크리스트 자동 생성 → 고위험 기능 투명성 보고서(모델 카드, 데이터시트) 자동 생성 → 규정 갱신 모니터링(EU OJ RSS) [BLOCKER] | §6.5 참조 | <!-- v12_C13_025 v26 -->
| | **-- v12 HIGH 추가: Safety --** | | | <!-- feature_id v26 -->
| 11 | **On-device Mode** | 온디바이스 LLM 추론 모드: 로컬 모델(Llama/Phi) 오프라인 실행, 프라이버시 보호, 네트워크 미연결 시 폴백 [HIGH] | §6 참조 | <!-- v12_C01a_099 v26 -->
| 13 | **Disclaimer Auto-insertion** | AI 생성 콘텐츠 면책 조항 자동 삽입: 출력 유형별 Disclaimer 템플릿, 규정 준수(투자/의료/법률 경고) [HIGH] | §6 참조 | <!-- v12_C01a_181 v26 -->
| 52 | **VBS-17: 웰니스 AI 벤치마크** | VBS-17 웰니스 AI 벤치마크: 정서 지원 품질/공감 정확도/안전 응답 비율 평가 프레임워크 [HIGH] | §6 참조 | <!-- v12_C09b_398 v26 -->
| 58 | **Deepfake/합성 데이터 리스크** | Deepfake/합성 데이터 리스크: 합성 콘텐츠 탐지 파이프라인, 워터마킹, 출처 추적 메타데이터 [HIGH] | §6 참조 | <!-- v12_C09b_446 v26 -->
| 65 | **Self-RAG (자기 반성 RAG)** | Self-RAG 검증 강화: 검색 결과 자기 평가(적합성/신뢰도), 부적합 시 쿼리 재작성 자동 루프 [HIGH] | §6 참조 | <!-- v12_C09b_505 v26 -->
| 72 | **비디오 안전성 필터** | 비디오 안전성 필터: NSFW/폭력/혐오 콘텐츠 자동 감지, 프레임 단위 분류, 차단/블러 처리 [HIGH] | §6 참조 | <!-- v12_C12_041 v26 -->
| | **-- v12 MEDIUM 추가: Safety --** | | | <!-- feature_id v26 -->
| 120 | **Dream Mode 웰니스 분석** | Dream Mode 웰니스 분석: 수면/스트레스/활동 패턴 백그라운드 분석, 인사이트 제공 [MEDIUM] | §6 참조 | <!-- v12_C09b_395 v26 -->
| 122 | **EU AI Act 2025 시행 대응** | EU AI Act 2025 시행 대응: 고위험 AI 시스템 등록, 적합성 평가, 투명성 보고서 자동 생성 [MEDIUM] | §6 참조 | <!-- v12_C09b_450 v26 -->
| 132 | **VaR 위험 경고 및 감정적 투자 방지** | VaR 위험 경고: Value-at-Risk 기반 투자 위험 알림, 감정적 투자 행동 패턴 감지/경고 [MEDIUM] | §6 참조 | <!-- v12_C10_042 v26 -->
| 148 | **크립토 규제 동향 모니터링** | 크립토 규제 동향 모니터링: 글로벌 규제 뉴스 자동 수집/분류, 영향도 평가 [MEDIUM] | §6 참조 | <!-- v12_C11_244 v26 -->
| 150 | **해외 투자 외환 규제 고려** | 해외 투자 외환 규제 고려: 환율 리스크 분석, 규제 체크리스트, 세금 영향 계산 [MEDIUM] | §6 참조 | <!-- v12_C11_262 v26 -->
| 151 | **투자 활동 감사 추적 로그** | 투자 활동 감사 추적 로그: 모든 투자 관련 의사결정/실행 감사 추적, 타임스탬프/액터 기록 [MEDIUM] | §6 참조 | <!-- v12_C11_263 v26 -->

### 산출물 참조
- Agent Teams: `VAMOS_AGENT_TEAMS_SPEC` (협업 패턴, MessageBus 정본)
- Cloud Library: `VAMOS_CLOUD_LIBRARY_SPEC` (7-Stage Discovery, RT-BNP V2 정본)
- 보안 스펙: `D2.0-07` (Guardrails, GDPR 정본)
- SDAR: `VAMOS_SDAR_DESIGN_SPECIFICATION` (AR-L3 정본)

### 실행 가이드

#### 사용자 직접 작업
1. **Redis 서버 설치**: Docker Compose에 Redis 7+ 추가 (`docker-compose.v2.yml` 서비스 정의 확인)
2. **Redis 연결 테스트**: `redis-cli ping` → PONG 응답 확인 + 비밀번호 설정
3. **HMAC 시크릿 키 생성**: `openssl rand -hex 32` → config.v2.toml `[security].hmac_secret_key`에 설정
4. **LlamaGuard 환경 확인**: (A) CUDA GPU 6GB+ VRAM 로컬, 또는 (B) CPU INT4 양자화 모델 (llama-guard-3-1b-int4), 또는 (C) RunPod serverless GPU (~$0.001/추론). ₩93,000/월 비용 상한 내 운영 필수
5. **Kafka 인스턴스 준비** (RT-BNP V2): Docker Compose에 Kafka + Zookeeper 추가, 토픽 생성 (`vamos.breaking_news`, `vamos.market_signal`)
6. **GDPR 데이터 정책 문서 작성**: 열람/이동/제한/삭제 요청 처리 절차 정의
7. **Agent Teams V2 통합 테스트**: Lead + 9 Sub-Agent 동시 실행 → 6가지 협업 패턴 각각 테스트
8. **보안 감사**: HMAC 인증 우회 시도 + LlamaGuard 필터링 테스트 + GDPR 요청 처리 검증

#### AI 프롬프트

````text
VAMOS 프로젝트 V2-Phase 3: Agent Teams V2 + 보안 강화를 진행합니다.

## 작업 목표
Agent Teams를 V2로 업그레이드 (Redis MessageBus + 10 에이전트 + 6패턴) 하고,
3-Layer Guardrails + HMAC 인증 + GDPR 기능을 구현합니다.

## 1. Redis MessageBus → `backend/vamos_core/agent_teams/message_bus_redis.py`
- In-Memory MessageBus → Redis Pub/Sub 전환
- 인터페이스 유지: MessageBus(ABC) 상속, publish/subscribe/unsubscribe
- Redis Streams 기반 메시지 영속화 (XADD/XREAD)
- 채널 패턴: `vamos.agent.{agent_id}.{event_type}`
- 연결 풀링: redis.asyncio.ConnectionPool (max_connections=20)
- HMAC-SHA256 메시지 서명 검증 (§LOCK-AT-012)

## 2. 6가지 협업 패턴 → `backend/vamos_core/agent_teams/patterns/`
각 패턴을 별도 모듈로 구현:
- `sequential.py`: 순차 실행 (A → B → C)
- `parallel.py`: 병렬 실행 (A ∥ B ∥ C → merge)
- `debate.py`: Bull vs Bear 논쟁 → 판정 (A-4 Debate Mode 연동)
- `supervisor.py`: Lead가 Sub에게 태스크 위임/모니터링
- `handoff.py`: 에이전트 간 컨텍스트 전달 전환
- `hybrid.py`: 상위 5개 패턴 조합 (§7.1 enum 6번째)
- 공통 인터페이스: CollaborationPattern(ABC) with execute(agents, task) → Result

## 3. Lead + 9 Sub-Agent 확장 → `backend/vamos_core/agent_teams/team_manager.py`
- V1(Lead+2) → V2(Lead+9) 확장: max_agents=10 (LOCK)
- 에이전트 풀: AgentPool with spawn/terminate/health_check
- 동적 에이전트 할당: 태스크 유형별 최적 에이전트 선택
- V2 추가 에이전트 6종:
  - Quant Agent: 정량 분석
  - Content Agent: 콘텐츠 생성
  - Trading Agent: 트레이딩 신호
  - Productivity Agent: 생산성 도구
  - Critic Agent: 비판적 검증
  - SDAR Agent: 자가진단/수리

## 4. HMAC-SHA256 인증 → `backend/vamos_core/security/hmac_auth.py`
- MessageBus 메시지 서명: HMAC-SHA256(secret_key, message_payload)
- 서명 검증: 수신 시 HMAC 일치 확인, 불일치 시 메시지 거부 + 로그
- 키 관리: config.v2.toml [security].hmac_secret_key (환경변수 오버라이드 가능)
- 타임스탬프 검증: ±5분 이내 메시지만 수용 (리플레이 공격 방지)

## 5. LlamaGuard L3 통합 → `backend/vamos_core/security/guardrails.py`
4-Layer Guardrails 중 V2에서 3개 활성:
- L1: NeMo Guardrails (규칙 기반 필터링) — V1 구현 완료
- L2: GuardrailsAI (패턴 매칭) — V1 구현 완료
- L3: LlamaGuard (LLM 기반 안전 분류) — V2 신규
  - 입력/출력 분류: safe/unsafe + 카테고리 (violence/sexual/hate 등)
  - GPU 추론 (FP16, batch_size=4)
  - 임계값: unsafe_score > 0.8 → 차단
- L4: 사후감사 로그 — V3로 연기 (D2.0-07 ADD-015)

## 6. GDPR 기능 → `backend/vamos_core/security/gdpr.py`
- 열람(Access): 사용자 데이터 JSON 내보내기
- 이동(Portability): 표준 형식(JSON-LD) 데이터 패키징
- 제한(Restriction): 특정 데이터 처리 일시 중지
- 삭제(Erasure): 사용자 요청 시 관련 데이터 완전 삭제 + 감사 로그
- GDPR 요청 큐: PostgreSQL 테이블 (gdpr_requests)

## 7. Cloud Library V2 + RT-BNP V2 → `backend/vamos_core/modules/e15_cloud_collector.py` 확장
Cloud Library V2:
- 7-Stage Discovery: Crawl → Filter → Extract → Classify → Enrich → Index → Deliver
- LLM 분석: 수집 문서의 관련성/품질 자동 평가
RT-BNP V2:
- REST API 30초 폴링 (T2+T3+T4 티어)
- Kafka 전파: `vamos.breaking_news` 토픽으로 Breaking 이벤트 발행
- AI Investing 연동: Breaking 감지 시 Trading Agent에 신호 전달
- 키워드 + 빈도 기반 Breaking Detector (V1 확장)

## 8. SDAR AR-L3 확장 → `backend/vamos_core/modules/i25_sdar_engine.py` 확장
Phase 2에서 구현한 I-25에 AR-L3 액션 5개 추가:
- 5-Gate 공유 (BaseGate 인터페이스, PART2 §6.9)
- 수리 성공률 추적: repair_success_rate ≥ 90% 목표

## v23 확장 (15건) <!-- v12_S1-2: §6 참조 개별화 v26 -->
- #9 OAuth2 + MFA (TOTP/WebAuthn) [HIGH] (D207-040) — §6.5 보안 참조
- #10-16 E-054~E-060 운영 모듈 [HIGH] (S7AE-591~597) — §6.12 운영 참조
- #17 방화벽 규칙 [HIGH] (S7FI-083) — §6.5 보안 참조
- #18-23 E-063~E-068 운영 모듈 [MEDIUM] (S7AE-600~605) — §6.12 운영 참조
⚠️ 우선순위 HIGH 항목부터 순차 구현. 각 항목의 §6.X 참조를 확인하여 구현.

## 규칙
> **§1.3 R1~R11 공통 규칙 전수 적용**
- Agent Teams: LOCK-AT-012 (HMAC 필수), LOCK-AT-014 (V2 max 10)
- 4-Layer Guardrails: L4는 V3로 연기, V2에서 L1+L2+L3만 활성
- MessageBus 인터페이스 하위호환성 유지 (V1 In-Memory → V2 Redis 전환 시)
- SOURCE_CONFLICT §7.1 주의: 협업 패턴 6개 (HYBRID 포함, §7.1 enum 기준)
- LOCK/FREEZE 값 변경 금지
- V2 비용 상한 ₩93,000/월 (LOCK)

## 참조 SOT 문서
- VAMOS_AGENT_TEAMS_SPEC (Agent Teams 정본, §7.1 협업 패턴 enum)
- VAMOS_CLOUD_LIBRARY_SPEC §7, §6.10.1 (RT-BNP V2 정본)
- D2.0-07 (보안/Guardrails/GDPR 정본)
- VAMOS_SDAR_DESIGN_SPECIFICATION (AR-L3 정본)
- PHASE_B1_API_CONTRACT.md (MessageBus API 정본)
````

### 단계 완료 검증 (V2-Phase 3 → V3 진입 전환 조건)

| # | 검증 항목 | 확인 방법 | 필수 |
|---|----------|----------|:---:|
| 1 | Redis MessageBus | In-Memory → Redis Pub/Sub 전환 + 메시지 영속화(XADD/XREAD) 동작 | ✅ |
| 2 | 6가지 협업 패턴 | Sequential/Parallel/Debate/Supervisor/Handoff/Hybrid 각각 실행 확인 | ✅ |
| 3 | Lead + 9 Sub-Agent | max_agents=10 동시 실행 + 동적 에이전트 할당 동작 | ✅ |
| 4 | HMAC-SHA256 인증 | 메시지 서명 + 검증 + 불일치 시 거부 + 타임스탬프 ±5분 제한 | ✅ |
| 5 | LlamaGuard L3 | 입력/출력 safe/unsafe 분류 + unsafe_score > 0.8 차단 동작 | ✅ |
| 6 | 3-Layer Guardrails | L1(NeMo) + L2(GuardrailsAI) + L3(LlamaGuard) 동시 활성 동작 | ✅ |
| 7 | GDPR 4 기능 | 열람(JSON)/이동(JSON-LD)/제한(처리 중지)/삭제(완전 삭제+감사 로그) | ✅ |
| 8 | Cloud Library V2 | 7-Stage Discovery + LLM 분석 동작 | ✅ |
| 9 | RT-BNP V2 | REST API 30초 폴링 + Kafka 전파 + AI Investing 연동 | ✅ |
| 10 | SDAR AR-L3 | Phase 2 구현 + AR-L3 5개 액션 확장 + repair_success_rate 추적 | ✅ |
| 11 | V2 완료 체크리스트 | 아래 체크리스트 전수 통과 | ✅ |
| 12 | V2→V3 전환 조건 | QoD ≥ 0.90(60일), 2-tier LLM 최적화, Self-evo 검증, V3 비용 승인 | ✅ |

> ⛔ 위 필수 항목 + 아래 V2 완료 체크리스트 + V2→V3 전환 조건 전체 통과 전 V3 진입 금지

### V2 완료 체크리스트
- [ ] PostgreSQL + Qdrant + Neo4j 동작
- [ ] Docker Compose 배포 성공
- [ ] 마이그레이션 검증 완료 (데이터 무결성)
- [ ] COND 모듈 10개 활성화 (I-7, I-12, I-22, I-23, I-25, A-4, E-13~E-16)
- [ ] Agent Teams 10개 에이전트 동작
- [ ] **4-Layer Guardrails** 중 3개 활성 (V2: L1:NeMo + L2:GuardrailsAI + L3:LlamaGuard) — L4 사후감사는 V3
- [ ] Cloud Library Discovery 동작
- [ ] RT-BNP V2 (Kafka 전파 + AI Investing 연동) 동작
- [ ] HMAC-SHA256 인증 동작 (Agent Teams MessageBus 서명 검증)
- [ ] GDPR 4기능 동작 (열람(Access)/이동(Portability)/제한(Restriction)/삭제(Erasure)) <!-- FIX-24: C-IMP-024 대응. 프롬프트(L2124-2129) 및 D2.0-07 정본 용어와 통일 -->
- [ ] SDAR AR-L3 동작 (MEDIUM risk 5개 액션 + repair_success_rate 추적)
- [ ] ₩93,000/월 비용 상한 준수

---

# 5. V3 구현

> **목표**: Enterprise. Docker Compose(기본) 또는 K8s(선택) + GPU + 전체 Self-evo.
> **기간**: 12-16주
> **비용 상한**: ₩266,000/월 ≈ $200 (ABSOLUTE LOCK). 기본 경로: Hetzner CX31 + RunPod Serverless (§5 V3-Phase 1 인프라 대안 참조)
> **추가 활성 모듈**: +39개 (전체 81개)

---

## V3-Phase 1: 인프라 스케일업 (Week 1-4)

| # | 항목 | 구현 내용 |
|---|------|----------|
| 1 | **Kubernetes 클러스터** | Helm Blue-Green 배포 |
| 2 | **vLLM 셀프호스팅** | A10G GPU, 자체 LLM 서빙 |
| 3 | **Qdrant Cloud** | 관리형 벡터 DB |
| 4 | **Neo4j Aura** | 관리형 그래프 DB |
| 5 | **Managed Postgres** | RDS/Cloud SQL |
| 6 | **Loki + Grafana** | Observability 스택 |

> **사전 해결 필요 (PART1 A.4에서 이동)**
> - **V3-001**: K8s 배포 명세 불충분 — K8s Helm 차트/리소스 매니페스트 상세 정의 ADD 필요
> - **V3-003**: GPU 비용 상한 현실성 (~$144/월 A10G) — RunPod A10G 시간당 $0.20 × 24h × 30일 = ~$144/월 기준. 실제 운영 비용 모니터링 필요

### 산출물 참조
- K8s 배포: `PHASE_B6_DEPLOYMENT_INFRA.md` (V3 Helm 차트)
- 인프라 스펙: `PHASE_B3_DEPENDENCIES.md` (V3 의존성)
- 설정: `PHASE_B4_CONFIG_SPEC.md` (config.v3.toml 확장)
- Observability: `D2.0-07` (모니터링/로깅 정본)

### 실행 가이드

#### 사용자 직접 작업

> **배포 경로 선택**: 아래 A(K8s 풀스펙) 또는 B(Hetzner Lite) 중 택 1. 비용 $200/월 이내라면 **경로 B 권장**.

**경로 A: AWS/GCP/Azure K8s (풀스펙)**
1. **클라우드 계정 준비**: AWS/GCP/Azure 계정 + K8s 클러스터 생성 (EKS/GKE/AKS)
2. **GPU 노드 프로비저닝**: A10G GPU 인스턴스 (최소 24GB VRAM) 1대 이상 + NVIDIA 드라이버 설치
3. **관리형 DB 인스턴스 생성**:
   - Managed PostgreSQL (RDS/Cloud SQL) + 마이그레이션 (V2 Docker PostgreSQL → 관리형)
   - Qdrant Cloud 계정 + 클러스터 생성
   - Neo4j Aura Free/Pro 인스턴스 생성
4. **도메인/SSL 설정**: 커스텀 도메인 + Let's Encrypt 또는 관리형 인증서 적용
5. **Helm 차트 리뷰**: AI 생성 Helm 차트의 리소스 제한(CPU/Memory/GPU), 레플리카 수, PVC 크기 검토
6. **비용 모니터링 대시보드 설정**: Grafana + 클라우드 비용 API 연동 → ₩266,000/월 상한 알림 설정
7. **V2→V3 전환 조건 확인**: QoD ≥ 0.90 (60일), 2-tier LLM 최적화 완료, P1 고급 테스트 통과, Self-evo 시스템 검증, V3 비용 리뷰 + 승인
8. **Blue-Green 배포 테스트**: K8s Blue-Green 전환 리허설 + 롤백 테스트

**경로 B: Hetzner CX31 + RunPod Serverless (권장, ~$123-142/월)** <!-- v26 메이커에반 개선안 7 -->
1. **Hetzner CX31 프로비저닝**: Hetzner Console → CX31 생성 (Falkenstein, Ubuntu 22.04), SSH 키 설정, UFW 방화벽(3000/5432/6333/6379/7687 허용)
2. **Swap 설정**: `fallocate -l 2G /swapfile && mkswap /swapfile && swapon /swapfile` (8GB RAM 보강)
3. **Docker 환경**: Docker Engine 24+ / Docker Compose v2 설치, V2에서 사용하던 `docker-compose.v2.yml` 기반 확장
4. **RunPod Serverless 계정**: RunPod 가입 → Serverless Endpoint 생성 (A4000/L4 GPU) → API 키 발급 → `config.v3.toml [llm.inference]` 등록
5. **AI Investing 내부 통신 구성**: Docker 네트워크 `vamos-network`에서 ORANGE CORE + BLUE NODE + AI Investing 모듈 간 localhost 통신 설정
6. **Polygon Pro API 키**: Polygon.io Pro 가입 ($79/월) → `config.v3.toml [modules.ai_investing]` 등록
7. **비용 모니터링**: Grafana 대시보드에서 Hetzner($8 고정) + RunPod(종량) + Polygon($79 고정) + LLM API(종량) 통합 추적 → 합계 $160 경고 / $190 심각 알림 (예상 $123-142 대비 여유 확보, $200 ABSOLUTE LOCK 초과 방지)
8. **V2→V3 전환 조건 확인**: 경로 A와 동일 (QoD ≥ 0.90, LLM 최적화, 테스트 통과, 승인)

#### AI 프롬프트

````text
VAMOS 프로젝트 V3-Phase 1: 인프라 스케일업을 진행합니다.

## 작업 목표
V2(Docker Compose 단일 서버) → V3(Kubernetes 클러스터 + GPU + 관리형 DB) 인프라 전환.
Helm 기반 Blue-Green 배포 + vLLM 셀프호스팅 + 관리형 서비스 전환 + Observability 구축.

## 1. Kubernetes Helm 차트 → `deploy/k8s/helm/vamos/`
Chart.yaml:
  - name: vamos
  - version: 3.0.0
  - appVersion: "3.0"
templates/:
  - deployment.yaml: vamos-app (replicas: 2, rolling update)
  - deployment-gpu.yaml: vamos-vllm (GPU nodeSelector, resources.limits.nvidia.com/gpu: 1)
  - service.yaml: ClusterIP + LoadBalancer
  - ingress.yaml: nginx-ingress + TLS
  - configmap.yaml: config.v3.toml 마운트
  - secret.yaml: DB 비밀번호, API 키, HMAC 시크릿
  - pvc.yaml: 영속 볼륨 (모델 캐시, 로그)
  - hpa.yaml: HorizontalPodAutoscaler (CPU 70%, min 2, max 10)
values.yaml:
  - 환경별 오버라이드 (dev/staging/prod)
  - Blue-Green 배포 설정 (activeColor: blue/green)
  - 리소스 제한: app(CPU 2, Memory 4Gi), vllm(CPU 4, Memory 16Gi, GPU 1)

### V3 인프라 대안: Hetzner CX31 + RunPod Serverless <!-- v24 메이커에반 개선안 7, v26 상세화 -->

> AWS/GCP/Azure K8s 대비 **비용 절감 대안**으로, $200/월 ABSOLUTE LOCK 범위 내에서 운영 가능한 경량 옵션입니다.
> 본격 K8s 클러스터 대신 Docker Compose + Serverless GPU 조합으로 V3 기능을 단계적 도입할 수 있습니다.
> V2에서 Hetzner CX31을 사용한 경우 동일 서버에서 V3로 자연스럽게 확장 가능합니다.

#### 비용 구조

| 항목 | 스펙 | 월 비용 | 성격 |
|------|------|--------|------|
| **Hetzner CX31** | 2vCPU / 8GB / 80GB SSD (독일 Falkenstein) | ~$8 | 고정 |
| **RunPod Serverless GPU** | A4000/L4 on-demand (임베딩/추론 전용) | ~$6-15 | 종량제 |
| **Polygon Pro** | 실시간 시세 데이터 (AI Investing용) | $79 | 고정 |
| **LLM API** (Claude/GPT) | Mini 중심 + Main 간헐적 | ~$20-30 | 종량제 |
| **합계** | | **~$123-142/월** ($200 이내) | |

> AWS/GCP K8s 기본 경로 대비 약 40~50% 비용 절감. $200 ABSOLUTE LOCK 범위 내에서 $58~77 여유분 확보.

#### Oracle Cloud Free Tier 대비 장점

| 비교 항목 | Oracle Cloud Free | Hetzner CX31 |
|----------|-------------------|-------------|
| 비용 | $0 | ~$8/월 |
| VM 회수 리스크 | **높음** (비활성화/회수 사례 다수) | **0%** (유료 서비스, SLA 99.9%) |
| CPU 아키텍처 | ARM (호환성 이슈 빈번) | **x86** (100% 호환) |
| DDoS 방어 | 기본 | **20Tbps 포함** |
| 과금 투명성 | 숨겨진 비용 존재 가능 | **투명 과금** (월정액) |
| 서울 리전 | 가용 | 미가용 (독일 Falkenstein) |

#### VAMOS AI + AI Investing 통합 아키텍처 (Hetzner 단일 서버)

동일 Hetzner CX31 서버에서 VAMOS 전체 시스템과 AI Investing을 통합 운영합니다.

```
┌───────────────── Hetzner CX31 (2vCPU / 8GB / 80GB) ─────────────────┐
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐    │
│  │ ORANGE CORE  │  │  BLUE NODE   │  │     AI Investing         │    │
│  │ (I-1~I-25)   │  │  (Trading)   │  │  (분석/시뮬레이션)       │    │
│  └──────┬───────┘  └──────┬───────┘  └────────────┬─────────────┘    │
│         │                 │                        │                  │
│  ───────┴─────────────────┴────────────────────────┴──────────────    │
│                    공유 자원 (localhost 통신)                          │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────────┐    │
│  │ PostgreSQL │ │   Redis    │ │   Qdrant   │ │  LLM API 키    │    │
│  │  (5432)    │ │  (6379)    │ │  (6333)    │ │ (Claude/GPT)   │    │
│  └────────────┘ └────────────┘ └────────────┘ └────────────────┘    │
│                                                                       │
│                    ── 외부 연결 ──                                    │
│         RunPod Serverless GPU ←── GPU 추론 요청 (on-demand)           │
│         Polygon Pro API ←── 실시간 시세 데이터                        │
└───────────────────────────────────────────────────────────────────────┘
```

**공유 자원 분리 전략**:
- PostgreSQL: 단일 인스턴스, 스키마 분리 (`vamos_core` / `ai_investing` / `trading`)
- Redis: DB 번호 분리 (0=캐시, 1=BLUE NODE, 2=AI Investing, 3=MessageBus)
- LLM API 키: 단일 키셋 공유, I-9 Cost Manager가 전체 비용 통합 추적
- 모듈 간 통신: Docker 내부 네트워크 `localhost` 통신 → 네트워크 지연 ~0ms

#### 로컬 PC 의존성 제거 (24/7 클라우드 운영)

| 항목 | V0~V1 (로컬) | V2 (VPS 서버) | V3 Hetzner Lite (클라우드) |
|------|-------------|-------------|-------------------------|
| 실행 환경 | 로컬 PC Tauri 앱 | VPS Docker Compose | Hetzner 24/7 자동 운영 |
| PC 종료 시 | 서비스 중단 | 영향 없음 (서버 운영) | **영향 없음** (서버 독립 운영) |
| 접근 방식 | 로컬 앱 실행 필수 | SSH + 원격 접근 | 웹 브라우저/API 원격 접근 |
| 모니터링 | 로컬 React 대시보드 | Grafana (Docker) | Grafana 원격 대시보드 |
| 알림 | Tauri notification | Webhook (V2+) | Webhook → Telegram/Discord |
| AI Investing | PC 켜져 있어야 분석 | 서버에서 24/7 | 24/7 자동 분석 + 알림 |

#### 성능 트레이드오프 상세

| 항목 | 수치 | VAMOS 운영 영향 | 완화 방법 |
|------|------|---------------|---------|
| 네트워크 지연 (한국→독일) | ~250ms | LLM 응답 시간 ±250ms 증가 | VAMOS 투자 스타일(분봉/일봉 기반)에 무시 가능. Circuit Breaker timeout 3초로 이미 보정 |
| GPU Cold Start (RunPod) | ~2-5초 | 첫 GPU 추론 요청 지연 | CPU 기반 Circuit Breaker가 선작동 → 사용자 체감 영향 <1초. RunPod 사전 워밍 cron 옵션 |
| 메모리 제약 | 8GB (실효 6GB + Swap 2GB) | BGE-M3 임베딩 + 전략 엔진 동시 운영 시 메모리 압박 | 배치 크기 제한(1000건), 야간 배치 스케줄링, 메모리 프로파일링 |
| 스토리지 | 80GB SSD | 모델 캐시 + DB + 로그 공간 | 로그 로테이션(30일), 모델 캐시 정리, Swap 파일 2GB |

#### Hetzner Lite 배포 4-STEP 체크리스트

**STEP 1: VPS 프로비저닝**
- Hetzner Console → CX31 인스턴스 생성 (Falkenstein, Ubuntu 22.04)
- SSH 키 설정, 일반 사용자 계정 생성, UFW 방화벽 설정
- Docker Engine 24+ / Docker Compose v2 설치
- Swap 2GB 생성: `fallocate -l 2G /swapfile && mkswap /swapfile && swapon /swapfile`

**STEP 2: Docker Compose 프로필 설정**
- `docker-compose.v3.yml`에 `profiles: ["hetzner-lite"]` 정의
- PostgreSQL / Qdrant / Redis 서비스 (로컬 Docker 컨테이너)
- `values.yaml` 오버라이드:
  - `infra_tier: "hetzner-lite"`
  - `deployment.mode: "docker-compose"`
  - `resource_limits.memory: "6Gi"` (8GB 중 2GB Swap 확보)

**STEP 3: RunPod Serverless GPU 엔드포인트 등록**
- `config.v3.toml` [llm.inference] 섹션:
  - `provider = "runpod-serverless"`
  - `runpod_endpoint = "https://api.runpod.io/v1/{ENDPOINT_ID}/run"`
  - `timeout_seconds = 300`
  - `cold_start_threshold = 5.0`
- OTHER BRAINS GPU 추론 경로로 RunPod 엔드포인트 등록 (I-10 Tool Router)

**STEP 4: AI Investing Stream Gateway 내부 통신 구성**
- Docker 내부 네트워크 `vamos-network` (bridge) 활용
- AI Investing 모듈 → `postgres:5432` / `redis:6379` (localhost 통신, 지연 ~0ms)
- Trading BLUE NODE → Polygon Pro API + 로컬 Redis 캐시
- 모듈 간 비동기 이벤트: Redis Pub/Sub 또는 PostgreSQL LISTEN/NOTIFY

> **LOCK 위반 없음**: 인프라 선택은 LOCK 대상 아님 (V3 K8s LOCK은 배포 방식이며 특정 벤더에 종속되지 않음). 비용 상한 $200/월 ABSOLUTE LOCK 준수.

## 2. vLLM 셀프호스팅 → `deploy/k8s/helm/vamos/templates/deployment-gpu.yaml`
- vLLM 서버 컨테이너: vllm/vllm-openai:latest
- 모델: meta-llama/Llama-3.1-8B (A10G 24GB에 FP16 로딩)
- OpenAI 호환 API 엔드포인트: /v1/chat/completions, /v1/embeddings
- GPU 리소스 요청: nvidia.com/gpu: 1
- 모델 캐시: PVC 마운트 (/models, 50Gi)
- 헬스체크: /health 엔드포인트
- config.v3.toml [llm] 섹션 업데이트:
  - provider = "vllm-self-hosted"
  - endpoint = "http://vamos-vllm:8000/v1"
  - model = "meta-llama/Llama-3.1-8B"

## 3. 관리형 DB 연결 설정 → `deploy/k8s/helm/vamos/values.yaml`
PostgreSQL:
  - host: (RDS/Cloud SQL 엔드포인트)
  - port: 5432
  - ssl_mode: require
Qdrant Cloud:
  - host: (Qdrant Cloud 클러스터 URL)
  - port: 6333
  - api_key: (Secret 참조)
Neo4j Aura:
  - uri: neo4j+s://(Aura 엔드포인트)
  - auth: (Secret 참조)
- V2 Docker DB → 관리형 DB 마이그레이션 스크립트: `scripts/migration/v2_to_managed_db.py`

## 4. Loki + Grafana Observability → `deploy/k8s/helm/monitoring/`
Loki Stack:
  - Promtail DaemonSet: 각 노드의 컨테이너 로그 수집
  - Loki StatefulSet: 로그 저장/인덱싱
  - Grafana: 대시보드 (사전 정의 JSON 프로비저닝)
대시보드:
  - VAMOS 시스템 상태: CPU/Memory/GPU 사용률, Pod 상태
  - 비용 모니터링: 클라우드 비용 API → ₩266,000/월 상한 추적
  - LLM 추론 메트릭: 토큰/초, 지연시간, 에러율
  - 5-Phase 파이프라인 메트릭: 각 Phase 처리 시간, 성공률
  - Agent Teams 메트릭: 활성 에이전트 수, 메시지 처리량

## 5. Config V3 확장 → `config/config.v3.toml`
config.v2.toml 기반 + V3 전용 확장:
  - [deployment] 섹션: deploy_mode="kubernetes" (경로 A) 또는 "docker-compose" (경로 B Hetzner Lite), helm_release="vamos", namespace="vamos-prod"
  - [llm] 섹션: provider="vllm-self-hosted", gpu_memory_fraction=0.9
  - [monitoring] 섹션 신규: loki_url, grafana_url, alert_webhook
  - [scaling] 섹션 신규: max_replicas=10, max_agents=50, gpu_nodes=1

## 6. Blue-Green 배포 스크립트 → `scripts/deploy/deploy_v3.sh`
- Helm upgrade --install with --set activeColor=blue/green
- 헬스체크 대기 → 트래픽 전환 (Ingress annotation 변경)
- 롤백: helm rollback vamos [REVISION]
- Canary 배포 옵션: --set canary.enabled=true, canary.weight=10

## 규칙
> **§1.3 R1~R11 공통 규칙 전수 적용**
- K8s 리소스 매니페스트에 resource limits/requests 필수 명시
- GPU 노드는 taint/toleration으로 격리 (nvidia.com/gpu=true:NoSchedule)
- 시크릿은 K8s Secret + 외부 Secret Manager (AWS SSM/GCP Secret Manager) 권장
- Blue-Green 배포 시 이전 버전 최소 1시간 유지 (즉시 롤백 가능)
- 비용 상한 ₩266,000/월 (LOCK) — GPU 비용 실시간 추적 필수
- LOCK/FREEZE 값 변경 금지

## 참조 SOT 문서
- PHASE_B6_DEPLOYMENT_INFRA.md (V3 배포 인프라 정본)
- PHASE_B3_DEPENDENCIES.md (V3 의존성 목록)
- PHASE_B4_CONFIG_SPEC.md §3 (config.v3.toml 확장 기준)
- D2.0-07 (모니터링/Observability 정본)
````

### 단계 완료 검증 (V3-Phase 1 → Phase 2 전환 조건)

> 경로 A(K8s) 또는 경로 B(Hetzner Lite) 중 선택한 경로의 검증 항목을 통과해야 합니다.

#### 경로 A: K8s 풀스펙 검증

| # | 검증 항목 | 확인 방법 | 필수 |
|---|----------|----------|:---:|
| 1 | K8s 클러스터 배포 | Helm install 성공 + 모든 Pod Running 상태 확인 | ✅ |
| 2 | vLLM 서빙 동작 | `/v1/chat/completions` + `/v1/embeddings` 엔드포인트 응답 확인 | ✅ |
| 3 | GPU 리소스 할당 | `nvidia.com/gpu: 1` 리소스 요청 + GPU 사용률 모니터링 동작 | ✅ |
| 4 | 관리형 PostgreSQL | V2 Docker PostgreSQL → 관리형 DB 마이그레이션 + ssl_mode=require 연결 | ✅ |
| 5 | Qdrant Cloud | 관리형 벡터 DB 연결 + API key 인증 + 기존 컬렉션 접근 | ✅ |
| 6 | Neo4j Aura | 관리형 그래프 DB 연결 + Bolt 프로토콜(neo4j+s://) 동작 | ✅ |
| 7 | Loki + Grafana | 로그 수집(Promtail) + 대시보드 5개 (시스템/비용/LLM/파이프라인/Agent) 동작 | ✅ |
| 8 | Blue-Green 배포 | Helm Blue-Green 전환 + 롤백 테스트 PASS | ✅ |
| 9 | HPA 동작 | CPU 70% 초과 시 자동 스케일링 (min 2 → max 10) 확인 | ✅ |
| 10 | 비용 모니터링 | Grafana 대시보드에서 ₩266,000/월 상한 알림 설정 + 동작 확인 | ✅ |

#### 경로 B: Hetzner Lite 검증 <!-- v26 메이커에반 개선안 7 -->

| # | 검증 항목 | 확인 방법 | 필수 |
|---|----------|----------|:---:|
| 1 | Hetzner CX31 서버 가동 | SSH 접속 + `docker compose ps` 전체 서비스 Running | ✅ |
| 2 | Swap 활성화 | `free -h`에서 Swap 2GB 확인 | ✅ |
| 3 | Docker Compose 전체 서비스 | PostgreSQL + Qdrant + Redis + VAMOS App 컨테이너 정상 가동 | ✅ |
| 4 | RunPod Serverless GPU 연결 | `config.v3.toml [llm.inference]` RunPod 엔드포인트 → 추론 응답 확인 | ✅ |
| 5 | AI Investing 내부 통신 | ORANGE CORE ↔ AI Investing ↔ BLUE NODE 간 localhost 통신 정상 | ✅ |
| 6 | Polygon Pro 데이터 수신 | 실시간 시세 데이터 수신 + Redis 캐시 저장 확인 | ✅ |
| 7 | Grafana 모니터링 | 대시보드 접근 + Hetzner/RunPod/LLM API 비용 추적 동작 | ✅ |
| 8 | 비용 합계 검증 | 실제 운영 1주일 비용 ≤ $35 (월 $142 기준 주간 환산) | ✅ |
| 9 | 메모리 안정성 | 48시간 연속 운영 후 OOM 미발생 + 메모리 사용량 < 7GB | ✅ |
| 10 | 롤백 테스트 | `docker compose down && docker compose up -d` 정상 복구 (3분 이내) | ✅ |

> ⛔ 선택한 경로의 필수 항목 전체 통과 전 Phase 2 진입 금지

## V3-Phase 2: EXP 모듈 전체 활성화 (Week 5-10)

> **모듈 분배 원칙**: Core EXP 모듈(I/S/E/A/B/C/D/EVX) + 핵심 기술 항목을 Phase 2에서 구현. Community/Expansion/Long-term 항목은 Phase 3으로 이동하여 부하 균등 배분.

| # | 모듈 그룹 | 모듈 | 구현 내용 |
|---|----------|------|----------|
| | **── Core EXP: I/S/E-Series ──** | | |
| 1 | I-Series | I-18 Self-evo Engine | 메타학습, 패턴 마이닝 |
| 2 | I-Series | I-21 Source Evolution Engine | 데이터 소스 자동 진화 | <!-- D2.0-02 §I-21 정본명. CLAUDE.md 명칭("Insight Analyzer")은 BLOCKER-12 해결 시 통일 -->
| 3 | I-Series | I-24 Knowledge Graph Engine | 내부 지식 그래프 고도화 |
| 4 | S-Series | S-2~S-8 전체 | Self-evo 서브시스템 완성 |
| 5 | E-Series | E-7~E-12 전체 | STT/TTS/Video/API/Browser/DB |
| | **── Advanced AI: A-Series ──** | | |
| 6 | A-Series | A-3 Meta AI | 메타 AI 엔진 |
| 7 | A-Series | A-5 Lazy Generation | 지연 생성 |
| 8 | A-Series | A-6 Federated | 연합 모듈 네트워크 |
| 9 | A-Series | A-7 Remote Executor | 원격 실행기 |
| | **── Learning/Reasoning/Generation ──** | | |
| 10 | B-Series | B-1~B-6 (B-3 Decay 제외, V1 완료) | Skill Library/Procedural Memory/DSPy 등 |
| 11 | C-Series | C-4~C-7 | Domain Simulator/Bayesian/RL/GNN |
| 12 | D-Series | D-3~D-6 | Long Horizon/Personality/Parallel/GraphRAG |
| | **── Experimental + Real-Time ──** | | |
| 13 | EVX | EVX-1~EVX-6 전체 | Code-as-Policy/Adversarial/Log-prob 등 |
| 14 | RT-BNP | **RT-BNP V3** | WebSocket 스트리밍 + FinBERT 실시간 분류 + Redis Pub/Sub (VAMOS_CLOUD_LIBRARY_SPEC, §6.10.1) |
| | **── Agent Teams ──** | | |
| 15 | Agent Teams | **PARL Agent Swarm** | TEE Execute에 PARL 패턴 통합, 최대 100 병렬 서브에이전트, RL 기반 병렬화 학습 (VAMOS_AGENT_TEAMS_SPEC §9, D2.0-05 §12.17.1) |
| 16 | Agent Teams | **PARL 인프라** | 에이전트 풀 자동 확장/축소, 보상 스케줄(초기=병렬화, 후기=품질80%+효율20%), Decision Aggregator (D2.0-04, D2.0-07) |
| | **── v23 핵심 기술 항목 ──** | | |
| 17 | Agent | **LSTM 가격 예측 모듈 (lstm_predictor.py)** | LSTM 가격 예측 모듈 (lstm_predictor.py) [MEDIUM] | <!-- AINV-076 v23 -->
| 18 | Agent | **실전 거래 소액 시작 모드 (Real Trading)** | 실전 거래 소액 시작 모드 (Real Trading) [MEDIUM] | <!-- AINV-080 v23 -->
| 19 | Agent | **Muon 옵티마이저 (MoE 학습 특화)** | Muon 옵티마이저 (MoE 학습 특화) [MEDIUM] | <!-- D204-160 v23 -->
| 20 | Agent | **관리자 콘솔** | 관리자 콘솔 [MEDIUM] | <!-- S7FI-034 v23 -->
| 21 | Agent | **VPN 구성** | VPN 구성 [MEDIUM] | <!-- S7FI-084 v23 -->
| 22 | Agent | **CRM 통합** | CRM 통합 [MEDIUM] | <!-- S7NP-034 v23 -->
| | **-- v12 MEDIUM 추가: Agent --** | | <!-- feature_id v26 -->
| 97 | **Mobile Automation Agent** | Mobile Automation Agent: 모바일 화면 자동화, 앱 간 연동, 제스처 시뮬레이션 [MEDIUM] | <!-- v12_C03_177 v26 -->
| 114 | **IoT/스마트홈 연동** | IoT/스마트홈 연동: MQTT/HomeAssistant 프로토콜, 디바이스 상태 조회/제어, 자동화 규칙 [MEDIUM] | <!-- v12_C09b_136 v26 -->
| | **-- v12 MEDIUM 추가: Infra --** | | <!-- feature_id v26 -->
| 115 | **GraphQL API (VAMOS GraphQL API)** | GraphQL API: 스키마 정의, Resolver 구현, 구독(Subscription) 실시간 업데이트 [MEDIUM] | <!-- v12_C09b_191 v26 -->
| 116 | **실시간 협업 코딩** | 실시간 협업 코딩: CRDT 기반 동시 편집, 커서 공유, 실시간 동기화 [MEDIUM] | <!-- v12_C09b_215 v26 -->
| | **-- v12 MEDIUM 추가: Orange Core --** | | <!-- feature_id v26 -->
| 129 | **Cross-Device Seamless State Sync** | Cross-Device Seamless State Sync: 디바이스 간 상태 실시간 동기화, 세션 이관 [MEDIUM] | <!-- v12_C09b_479 v26 -->
| | **-- v12 MEDIUM 추가: UI/UX --** | | <!-- feature_id v26 -->
| 92 | **Module A-6 Mobile App** | A-6 Mobile App: React Native/Flutter 모바일 클라이언트, 오프라인 모드, 푸시 알림 [MEDIUM] | <!-- v12_C02_080 v26 -->

> **사전 해결 필요 (PART1 A.4에서 이동)**
> - **V3-004**: GraphRAG 90% 벤치마크 미정의 — 벤치마크 기준 및 평가 파이프라인 ADD 필요
> - **DEFER-AT-004**: Federated Agent(A-6) 승인 정책 미정의 — 연합 에이전트 인증/승인 프로토콜 DEF

### 산출물 참조
- I-Series EXP: `D2.0-02 §7` (모듈별 상세 정본)
- S-Series Self-evo: `D2.0-01 §5.8` (Self-evo 서브시스템 정본)
- E-Series 멀티모달: `D2.0-03` (External Integration 정본)
- B-Series 학습: `D2.0-01 §5.10` (Skill/Procedural/DSPy 정본)
- C-Series 추론: `D2.0-01 §5.11` (Domain/Bayesian/RL/GNN 정본)
- D-Series 생성: `D2.0-01 §5.12` (Long Horizon/GraphRAG 정본)
- EVX: `D2.0-01 §5.15` (Experimental 정본)

### 실행 가이드

#### 사용자 직접 작업
1. **V2→V3 전환 조건 최종 확인**: QoD ≥ 0.90 (60일), Self-evo 시스템 검증 완료, V3 비용 승인
2. **GPU 리소스 할당 확인**: vLLM + LlamaGuard + Self-evo 동시 GPU 사용량 계산 → 필요 시 추가 GPU 노드
3. **외부 API 키 발급 (E-Series)**: STT(Whisper API 또는 로컬), TTS(ElevenLabs/로컬), Video(FFmpeg), Browser(Playwright), DB 커넥터
4. **GraphRAG 벤치마크 기준 정의** (V3-004): 정확도/재현율/F1 목표치 설정 + 평가 데이터셋 준비
5. **Federated Agent 승인 정책 정의** (DEFER-AT-004): 연합 에이전트 인증 프로토콜 + 승인 워크플로우 문서화
6. **Self-evo 모듈 단계적 활성화**: S-2→S-3→…→S-8 순차 활성화 + 각 단계별 안정성 검증
7. **EVX 실험 모듈 안전 환경 준비**: 격리된 네임스페이스에서 EVX 모듈 테스트 (프로덕션 격리)
8. **모듈 통합 테스트**: 16개 Core EXP 그룹 + v23 핵심 기술 6건 활성화 → Phase 2 범위 모듈 동시 동작 안정성 검증
9. **PARL RL 학습 파이프라인 환경 준비**: PARL Agent Swarm 보상 함수 초기 가중치 설정 (초기=병렬화율, 후기=품질80%+효율20%), 에이전트 풀 자동 확장/축소 정책 정의, Decision Aggregator 집계 전략 확정

#### AI 프롬프트

````text
VAMOS 프로젝트 V3-Phase 2: EXP 모듈 전체 활성화를 진행합니다.

## 작업 목표
V3 EXP 모듈 22개 항목(Core EXP 16개 그룹 + v23 핵심 기술 6건)을 단계적으로 구현합니다.
전체 모듈 수: V1(32 CORE) + V2(10 COND) + V3(39 EXP) = 81개.
Module Catalog 표준 필드(D2.0-01 §5.5 LOCK) 준수, category=EXP.

## 그룹 1: I-18 Self-evo Engine → `backend/vamos_core/modules/i18_self_evo_engine.py`
- 메타학습: 사용자 패턴 마이닝 → 행동 예측 모델 학습
- 자기개선 루프: 성능 메트릭 수집 → 약점 식별 → 전략 조정
- S-1(Core) 연동: Self-evo 서브시스템의 메인 엔진
- 의존성: S-1, I-5(DecisionEngine), I-8(AutonomyManager)
- **I/O**: Input: `PerformanceMetrics(qod_score, latency_p99, error_rate, cost_daily)` → Output: `EvolutionPlan(adjustments: list[StrategyAdjustment], priority: int)`
- **핵심 함수**: `async def evolve(metrics: PerformanceMetrics) -> EvolutionPlan`, `async def mine_patterns(user_history: list[SessionLog]) -> list[BehaviorPattern]`

## 그룹 2: I-21 Source Evolution Engine → `backend/vamos_core/modules/i21_source_evolution_engine.py`
- 데이터 소스 자동 진화: 소스 품질 평가 → 저품질 소스 대체/업그레이드
- Cloud Library V3와 연동: 자율 수집/진화 파이프라인
- RSS/API 소스 자동 발견 + 등록
- **I/O**: Input: `list[DataSource(url, type, trust_score, last_check)]` → Output: `EvolutionReport(upgraded: list, replaced: list, new_discovered: list)`
- **핵심 함수**: `async def evaluate_sources() -> list[SourceQuality]`, `async def discover_new(domain: str) -> list[DataSource]`
- **의존성 패키지**: feedparser, aiohttp, VAMOS_CLOUD_LIBRARY_SPEC SDK

## 그룹 3: I-24 Knowledge Graph Engine → `backend/vamos_core/modules/i24_knowledge_graph_engine.py`
- Neo4j 기반 내부 지식 그래프 고도화
- 자동 관계 추출: LLM 기반 엔티티/관계 추출 → Neo4j MERGE
- GraphRAG: 지식 그래프 + RAG 결합 검색 (벤치마크 90% 목표, V3-004)
- 의존성: Neo4j Aura (V3-Phase 1)
- **I/O**: Input: `Document(text, metadata)` → Output: `KGUpdateResult(entities_added: int, relations_added: int, subgraph: nx.DiGraph)`
- **핵심 함수**: `async def extract_and_merge(doc: Document)`, `async def graphrag_search(query: str, top_k: int=10) -> list[GraphRAGResult]`
- **의존성 패키지**: neo4j (Python driver), networkx (로컬 캐시)

## 그룹 4: S-2~S-8 Self-evo 서브시스템 → `backend/vamos_core/self_evo/`
순차 구현 (각 모듈은 BaseSelfEvo(ABC) 상속):
- S-2 Pattern Miner (`s02_pattern_miner.py`): 사용자 행동 패턴 추출
  - I/O: `list[SessionLog]` → `list[BehaviorPattern(pattern_type, frequency, confidence)]`
- S-3 Strategy Optimizer (`s03_strategy_optimizer.py`): 전략 최적화 엔진
  - I/O: `list[BehaviorPattern]` + `PerformanceMetrics` → `OptimizedStrategy(params: dict, expected_improvement: float)`
- S-4 Performance Monitor (`s04_performance_monitor.py`): 성능 지표 실시간 추적
  - I/O: 시스템 메트릭 스트림 → `PerformanceReport(qod_trend, latency_trend, cost_trend, alerts: list)`
- S-5 Feedback Loop (`s05_feedback_loop.py`): 사용자 피드백 학습 반영
  - I/O: `UserFeedback(rating, comment, context)` → `LearningUpdate(adjustments: dict)`
- S-6 Adaptation Engine (`s06_adaptation_engine.py`): 환경 적응 엔진
  - I/O: `EnvironmentState(load, error_rate, user_count)` → `AdaptationAction(target_param, old_value, new_value)`
- S-7 Evolution Scheduler (`s07_evolution_scheduler.py`): 진화 스케줄링
  - I/O: `list[EvolutionPlan]` → `ScheduledEvolution(plan_id, execute_at, dependencies: list)`
- S-8 Self-evo Governance (`s08_governance.py`): 거버넌스 (V3-002, Phase 3에서 상세화)
  - I/O: `EvolutionPlan` → `GovernanceDecision(approved: bool, risk_level, reason)`
- 공통 인터페이스: BaseSelfEvo(ABC) with `async def evolve()`, `async def evaluate() -> float`, `async def rollback(snapshot_id: str)`

## 그룹 5: E-7~E-12 멀티모달 → `backend/vamos_core/modules/`
- E-7 STT (`e07_stt.py`): Whisper 기반 음성→텍스트 (GPU 추론)
- E-8 TTS (`e08_tts.py`): 텍스트→음성 합성 (로컬/API 선택)
- E-9 Video Analyzer (`e09_video_analyzer.py`): FFmpeg + 프레임 분석
- E-10 API Gateway (`e10_api_gateway.py`): 외부 REST API 통합 게이트웨이
- E-11 Browser Agent (`e11_browser_agent.py`): Playwright 기반 웹 브라우징
- E-12 DB Connector (`e12_db_connector.py`): 다중 DB 연결기 (PostgreSQL/MySQL/MongoDB)

## 그룹 6: A-3 Meta AI → `backend/vamos_core/modules/a03_meta_ai.py`
- 메타 AI: 다른 AI 모듈의 성능을 분석/최적화하는 상위 AI
- 모듈 성능 대시보드 + 자동 파라미터 튜닝
- I-18 Self-evo Engine과 연동

## 그룹 7: A-5 Lazy Generation → `backend/vamos_core/modules/a05_lazy_generation.py`
- 지연 생성: 필요 시점까지 콘텐츠 생성 지연 (토큰 절약)
- 스트리밍 생성: 청크 단위 점진적 출력
- 비용 최적화: 불필요한 LLM 호출 사전 차단

## 그룹 8: A-6 Federated → `backend/vamos_core/modules/a06_federated.py`
- 연합 모듈 네트워크: 외부 VAMOS 인스턴스와 연합 학습/추론
- 인증 프로토콜: mTLS + JWT (DEFER-AT-004 해결 후)
- 데이터 프라이버시: 모델 그래디언트만 교환 (원본 데이터 전송 금지)

## 그룹 9: A-7 Remote Executor → `backend/vamos_core/modules/a07_remote_executor.py`
- 원격 실행기: 외부 컴퓨트 리소스에서 태스크 실행
- SSH/K8s Job 기반 원격 실행
- 결과 수집 + 실패 재시도 (max 3회)

## 그룹 10: B-1~B-6 학습 모듈 → `backend/vamos_core/learning/`
(B-3 Decay는 V1 완료, 제외)
- B-1 Skill Library (`b01_skill_library.py`): 학습된 스킬 저장/검색/재사용
- B-2 Procedural Memory (`b02_procedural_memory.py`): 절차적 기억 (how-to)
- B-4 DSPy Integration (`b04_dspy.py`): DSPy 프레임워크 연동 프롬프트 최적화
- B-5 Few-Shot Manager (`b05_few_shot_manager.py`): 동적 Few-Shot 예제 관리
- B-6 Reinforcement Learner (`b06_rl_learner.py`): 보상 기반 행동 학습

## 그룹 11: C-4~C-7 추론 모듈 → `backend/vamos_core/reasoning/`
- C-4 Domain Simulator (`c04_domain_simulator.py`): 도메인 시뮬레이션 (금융/법률/의료)
- C-5 Bayesian Reasoner (`c05_bayesian.py`): 베이지안 확률 추론
- C-6 RL Policy (`c06_rl_policy.py`): 강화학습 정책 네트워크
- C-7 GNN Reasoner (`c07_gnn.py`): 그래프 신경망 기반 관계 추론

## 그룹 12: D-3~D-6 생성 모듈 → `backend/vamos_core/generation/`
- D-3 Long Horizon Planner (`d03_long_horizon.py`): 장기 계획 수립 (다단계 목표)
- D-4 Personality Engine (`d04_personality.py`): AI 페르소나 관리
- D-5 Parallel Generator (`d05_parallel_gen.py`): 병렬 콘텐츠 생성
- D-6 GraphRAG (`d06_graphrag.py`): 지식 그래프 기반 RAG (I-24 연동, V3-004 벤치마크)

## 그룹 13: EVX-1~EVX-6 실험 모듈 → `backend/vamos_core/experimental/`
⚠️ 격리 네임스페이스에서 실행 (프로덕션 영향 차단)
- EVX-1 Code-as-Policy (`evx01_code_as_policy.py`): 코드 생성 → 정책 자동 적용
- EVX-2 Adversarial Tester (`evx02_adversarial.py`): 적대적 입력 자동 생성 + 견고성 테스트
- EVX-3 Log-prob Analyzer (`evx03_logprob.py`): LLM 로그 확률 분석 → 불확실성 측정
- EVX-4 Thought Debugger (`evx04_thought_debug.py`): 추론 체인 시각화/디버깅
- EVX-5 Synthetic Data Gen (`evx05_synthetic_data.py`): 합성 학습 데이터 생성
- EVX-6 Multi-Objective Optimizer (`evx06_multi_obj.py`): 다목적 최적화 (품질/비용/속도 동시)

## 그룹 14: RT-BNP V3 → `backend/vamos_core/modules/e15_cloud_collector.py` 확장
- WebSocket 스트리밍 (T1~T4 전체 티어)
- FinBERT 실시간 분류: 뉴스 감성 분석 (positive/negative/neutral)
- Redis Pub/Sub: 실시간 이벤트 브로드캐스트
- Kafka 연동 유지 + Redis Pub/Sub 추가 (하이브리드)

## 그룹 15: PARL Agent Swarm → `backend/vamos_core/agent_teams/parl/`
- `swarm_executor.py`: TEE Execute 단계에 PARL 패턴 통합
  - 최대 100 병렬 서브에이전트 스폰/관리
  - RL 기반 병렬화 학습: 태스크 분할 전략 자동 최적화
  - I/O: `SwarmTask(subtasks: list[SubTask], max_parallel: int)` → `SwarmResult(results: list[SubTaskResult], parallel_efficiency: float)`
- `reward_scheduler.py`: 보상 스케줄 관리
  - 초기: 병렬화율 극대화 (exploration)
  - 후기: 품질 80% + 효율 20% (exploitation)
  - 가중치 전환 트리거: 100 에피소드 후 또는 병렬 효율 ≥ 90% 도달 시
- `decision_aggregator.py`: 병렬 서브에이전트 결과 집계
  - Majority Voting / Weighted Average / Consensus 전략
  - 불일치 감지 → 자동 재실행 또는 HITL 에스컬레이션
- `pool_autoscaler.py`: 에이전트 풀 자동 확장/축소 (D2.0-04 정본)
  - 스케일 업: 대기 태스크 > pool_size × 0.8 시
  - 스케일 다운: 유휴 에이전트 > pool_size × 0.5 시 (5분 유예)
  - 상한: LOCK-AT-014 V3=50+ (PARL 모드에서 최대 100)
- **의존성 패키지**: torch (RL 학습), ray (병렬 실행 프레임워크)
- **LOCK**: PARL 모드 활성화 시에도 Lead Agent 단일결정 원칙 유지 (LOCK-AT-002)

## v23 핵심 기술 (6건)
- #17 LSTM 가격 예측 모듈 — lstm_predictor.py [MEDIUM] (AINV-076)
- #18 실전 거래 소액 시작 모드 — Real Trading [MEDIUM] (AINV-080)
- #19 Muon 옵티마이저 — MoE 학습 특화 [MEDIUM] (D204-160)
- #20 관리자 콘솔 [MEDIUM] (S7FI-034)
- #21 VPN 구성 [MEDIUM] (S7FI-084)
- #22 CRM 통합 [MEDIUM] (S7NP-034)
⚠️ Core EXP 16개 그룹 완료 후 순차 구현. 각 항목의 §6.X 참조: #17 LSTM→§6.8, #18 Real Trading→§6.8, #19 Muon→§6.2, #20 관리자콘솔→§6.1, #21 VPN→§6.5, #22 CRM→§6.7 <!-- v12_S1-3: §6 참조 개별화 v26 -->

## 그룹별 의존성 패키지 (FIX-21) <!-- C-IMP-011 대응 -->

| 그룹 | 주요 패키지 |
|------|-----------|
| 1 (I-18) | scikit-learn, numpy (패턴 마이닝) |
| 2 (I-21) | feedparser, aiohttp (RSS/API 발견) |
| 3 (I-24) | neo4j, networkx (GraphRAG) |
| 4 (S-2~S-8) | scipy, scikit-learn (최적화/통계) |
| 5 (E-7 STT) | openai-whisper 또는 faster-whisper (GPU) |
| 6 (E-8 TTS) | elevenlabs 또는 pyttsx3 (로컬 대안) |
| 7 (E-9 Video) | ffmpeg-python, opencv-python |
| 8 (E-10~E-12) | playwright, sqlalchemy, httpx |
| 9 (A-7) | paramiko (SSH), kubernetes (K8s Job) |
| 10 (B-1~B-6) | dspy-ai, torch (B-4 DSPy, B-6 RL) |
| 11 (C-4~C-7) | torch, torch-geometric (C-7 GNN), bayesian-optimization (C-5) |
| 12 (D-3~D-6) | neo4j (D-6 GraphRAG), torch |
| 13 (EVX-1~6) | torch, z3-solver (EVX-1 policy), adversarial-robustness-toolbox (EVX-2) |
| 14 (RT-BNP V3) | websockets, transformers (FinBERT), redis |
| 15 (PARL Swarm) | torch (RL 학습), ray (병렬 실행) |

## config.v3.toml EXP 모듈 키 (FIX-21) <!-- C-IMP-012 대응 -->

```toml
[modules.exp]
# Self-evo
i18.enabled = false
i18.evolution_interval_h = 24
s02.enabled = false  # Self-evo Patterns
s03.enabled = false  # Self-evo Optimizer
s04.enabled = false  # Self-evo Planner
s05.enabled = false  # Self-evo Memory
s06.enabled = false  # Self-evo Verifier
s07.enabled = false  # Self-evo Deployer
s08.enabled = false  # Self-evo Governance (Phase 3에서 상세화)
s_series.sequential_activation = true

# Knowledge
i21.enabled = false
i21.source_eval_interval_h = 12
i24.enabled = false
i24.graphrag_top_k = 10

# Multimodal
e07.enabled = false
e07.whisper_model = "base"        # GPU 가용시 "large-v3"
e08.enabled = false
e09.enabled = false

# External
e10.enabled = false
e11.enabled = false
e12.enabled = false
a07.enabled = false
a07.max_retries = 3

# Learning/Reasoning/Generation
b_series.enabled = false
c_series.enabled = false
d_series.enabled = false

# Experimental
evx.enabled = false
evx.namespace = "vamos-experimental"
evx.gpu_sharing = "time-sharing"  # "mps" or "time-sharing"

# RT-BNP V3
rt_bnp_v3.enabled = false
rt_bnp_v3.websocket_reconnect_s = 5
rt_bnp_v3.finbert_batch_size = 8
```

### V3 EXP 모듈 기본 패턴 (코드 참조)

```python
# EXP 모듈 공통 패턴 — 모든 V3 모듈은 이 구조를 따름
from abc import ABC
from pydantic import BaseModel
from vamos_core.modules.base import BaseModule

class MyExpModule(BaseModule):
    """category='EXP', 기본 OFF, config에서 enabled=true로 활성화"""
    category = "EXP"

    async def execute(self, input_data: BaseModel) -> BaseModel:
        if not self.config.enabled:
            raise RuntimeError(f"{self.name} is disabled")
        # 모듈 로직 구현
        ...
```

## 규칙
> **§1.3 R1~R11 공통 규칙 전수 적용**
- 모든 EXP 모듈은 BaseModule(ABC) 상속, category="EXP"
- EVX 모듈은 별도 K8s 네임스페이스 (vamos-experimental)에 배포
- Self-evo 모듈(S-2~S-8)은 순차 활성화 (앞 모듈 안정화 후 다음 활성화)
- GPU 리소스 공유: vLLM, E-7(STT), EVX 모듈 간 GPU 스케줄링 (NVIDIA MPS 또는 time-sharing)
- Module Catalog 표준 필드 준수 (D2.0-01 §5.5 LOCK)
- LOCK/FREEZE 값 변경 금지
- V3 비용 상한 ₩266,000/월 (LOCK)

## 참조 SOT 문서
- D2.0-01 §5.6~§5.15 (전체 모듈 카탈로그 정본)
- D2.0-02 §7 (I-Series 상세 정본)
- D2.0-03 (E-Series 정본)
- VAMOS_CLOUD_LIBRARY_SPEC §7, §6.10.1 (RT-BNP V3 정본)
````

### 단계 완료 검증 (V3-Phase 2 → Phase 3 전환 조건)

| # | 검증 항목 | 확인 방법 | 필수 |
|---|----------|----------|:---:|
| 1 | I-18 Self-evo Engine | 메타학습 + 사용자 패턴 마이닝 + 자기개선 루프 동작 | ✅ |
| 2 | I-21 Source Evolution | 소스 품질 평가 + 저품질 소스 대체/업그레이드 자동 동작 | ✅ |
| 3 | I-24 Knowledge Graph | Neo4j 기반 자동 관계 추출 + GraphRAG 검색 동작 | ✅ |
| 4 | S-2~S-8 순차 활성화 | 7개 Self-evo 모듈 각각 안정화 확인 후 다음 활성화 완료 | ✅ |
| 5 | E-7~E-12 멀티모달 | STT/TTS/Video/API Gateway/Browser/DB Connector 동작 확인 | ✅ |
| 6 | A-3/A-5/A-6/A-7 | Meta AI/Lazy Generation/Federated/Remote Executor 동작 확인 | ✅ |
| 6-1 | Federated Agent 승인 체계 | A-6 Federated 인증 프로토콜 + 승인 워크플로우 설계/구현 검증 (V3-GNG-10, DEFER-AT-004 대응) | ✅ |
| 7 | B-1~B-6 학습 모듈 | Skill Library/Procedural/DSPy/Few-Shot/RL 동작 확인 (B-3 제외) | ✅ |
| 8 | C-4~C-7 추론 모듈 | Domain Simulator/Bayesian/RL Policy/GNN 동작 확인 | ✅ |
| 9 | D-3~D-6 생성 모듈 | Long Horizon/Personality/Parallel Generator/GraphRAG 동작 확인 | ✅ |
| 10 | EVX-1~EVX-6 격리 테스트 | vamos-experimental 네임스페이스에서 6개 실험 모듈 테스트 PASS | ✅ |
| 11 | RT-BNP V3 | WebSocket 스트리밍 + FinBERT 실시간 분류 + Redis Pub/Sub 동작 | ✅ |
| 12 | 81개 모듈 동시 동작 | 전체 모듈 활성 상태에서 시스템 안정성 확인 (에러율 < 0.1%) | ✅ |
| 13 | PARL Agent Swarm 병렬 실행 | PARL 모드 100 병렬 서브에이전트 스폰 + Decision Aggregator 집계 정확도 ≥ 95% + 보상 스케줄 전환 동작 확인 | ✅ |

> ⛔ 위 필수 항목 전체 통과 전 Phase 3 진입 금지

## V3-Phase 3: 고급 기능 + 최종 통합 (Week 11-16)

| # | 항목 | 구현 내용 |
|---|------|----------|
| | **── 핵심 시스템 완성 ──** | |
| 1 | **Agent Marketplace** | 에이전트 탐색/설치/검증 |
| 2 | **50+ Agent Mesh** | 동적 스폰/종료, Multi-Agent |
| 3 | **S-8 Self-evo Governance** | 거버넌스 완성 |
| 4 | **SDAR AR-L4** | HIGH risk 코드 핫픽스/스키마 마이그레이션 |
| 5 | **Cloud Library V3** | 완전 자율 수집/진화 |
| 6 | **A2A 프로토콜** | 에이전트 간 표준 프로토콜 |
| 7 | **멀티모달 고급** | 3D 생성, 비디오 스트리밍, 아바타 |
| 8 | **최종 벤치마크** | MMLU/HumanEval/LogicKor 등 38개 벤치마크 |
| 9 | **Agent Specialization** | 에이전트 자동 fork/특화/retire 프로토콜 (P6-AGT-04, D2.0-05 §12.19) |
| 10 | **AI Investing 고급** | 섹터/피어 비교 분석(PER/PBR/EV-EBITDA) + 파생상품 분석(그릭스/Black-Scholes) (DA1-016, DA1-019, §6.8 참조) | **L3**: `sot 2/Ai-investing-detail/13_asset-class-deep/derivatives_strategies.md` + `03_macro-sector-stock/sector_rotation.md` |
| | **── v23 고급 기능 ──** | |
| 11 | **알림 중복 방지 debounce (5분 내 동일 지표 억제)** | 알림 중복 방지 debounce (5분 내 동일 지표 억제) [HIGH] | <!-- D204-077 v23 -->
| 12 | **M-044 지식 기반 개인 어시스턴트 (V3 심화)** | M-044 지식 기반 개인 어시스턴트 (V3 심화) [HIGH] | <!-- D206-220 v23 -->
| 13 | **지식 버전 관리** | 지식 버전 관리 [HIGH] | <!-- S7JM-259 v23 -->
| 14 | **앰비언트 인텔리전스 (Ambient Intelligence) 구현** | 앰비언트 인텔리전스 (Ambient Intelligence) 구현 [MEDIUM] | <!-- D203-110 v23 -->
| | **── v23 Community/Social (Phase 2에서 이동) ──** | |
| 15 | **학습 커뮤니티 (스터디 그룹/공유/토론/멘토-멘티)** | 학습 커뮤니티 (스터디 그룹/공유/토론/멘토-멘티) [MEDIUM] | <!-- D205-138 v23 →PH3 -->
| 16 | **웰니스 커뮤니티 (V3 익명 참여)** | 웰니스 커뮤니티 (V3 익명 참여) [MEDIUM] | <!-- D207-116 v23 →PH3 -->
| 17 | **동료 학습 매칭** | 동료 학습 매칭 [MEDIUM] | <!-- S7NP-055 v23 →PH3 -->
| 18 | **학습 커뮤니티** | 학습 커뮤니티 [MEDIUM] | <!-- S7NP-065 v23 →PH3 -->
| 19 | **웰니스 커뮤니티** | 웰니스 커뮤니티 [MEDIUM] | <!-- S7NP-121 v23 →PH3 -->
| | **── v23 Expansion/Long-term (Phase 2에서 이동) ──** | |
| 20 | **국가별 규제 적응** | 국가별 규제 적응 [MEDIUM] | <!-- D207-084 v23 →PH3 -->
| 21 | **장기 평가 추적** | 장기 평가 추적 [MEDIUM] | <!-- S7FI-180 v23 →PH3 -->
| 22 | **글로벌 확장 전략** | 글로벌 확장 전략 [MEDIUM] | <!-- S7FI-239 v23 →PH3 -->
| 23 | **확장 시장 진입** | 확장 시장 진입 [MEDIUM] | <!-- S7FI-247 v23 →PH3 -->
| 24 | **M&A 전략** | M&A 전략 [MEDIUM] | <!-- S7FI-248 v23 →PH3 -->
| 25 | **장기 재무 예측** | 장기 재무 예측 [MEDIUM] | <!-- S7FI-262 v23 →PH3 -->
| 26 | **B2B 컨설팅 모델** | B2B 컨설팅 모델 [MEDIUM] | <!-- S7NP-185 v23 →PH3 -->
| | **-- v12 LOW 추가: Agent --** | | <!-- feature_id v26 -->
| 178 | **모바일 자동화** | 모바일 자동화: 모바일 앱 자동화 에이전트, UI 인식, 작업 시퀀스 실행 [LOW] | <!-- v12_C09b_302 v26 -->
| | **-- v12 LOW 추가: Blue Nodes --** | | <!-- feature_id v26 -->
| 182 | **크립토 온체인 분석** | 크립토 온체인 분석: 블록체인 데이터 분석, 지갑 추적, 트랜잭션 패턴 분석 [LOW] | <!-- v12_C09b_476 v26 -->
| | **-- v12 LOW 추가: Business --** | | <!-- feature_id v26 -->
| 177 | **Z-Session 암호화폐 트레이딩 통합** | Z-Session 암호화폐 트레이딩: 크립토 거래소 API 통합, 자동 매매, 리스크 관리 [LOW] | <!-- v12_C08_097 v26 -->
| | **-- v12 LOW 추가: Infra --** | | <!-- feature_id v26 -->
| 172 | **IoT Smart Home Integration** | IoT Smart Home 통합: HomeAssistant/MQTT 프로토콜, 디바이스 제어, 자동화 시나리오 [LOW] | <!-- v12_C03_045 v26 -->
| 184 | **추측적 디코딩(Speculative Decoding)** | 추측적 디코딩: Draft 모델 기반 병렬 토큰 생성, 검증 루프, 속도 향상 최적화 [LOW] | <!-- v12_C11_021 v26 -->
| 190 | **IoT/스마트홈 연동** | IoT/스마트홈 연동: HomeAssistant/Matter 프로토콜, 디바이스 디스커버리, 자동화 규칙 [LOW] | <!-- v12_C12_123 v26 -->

> **사전 해결 필요 (PART1 A.4에서 이동)**
> - **V3-002**: Self-evo Governance(S-8) 미상세 — 거버넌스 상세 규칙/감사 ADD 필요
> - **DEFER-AT-005**: A2A 프로토콜 설계 미완 — 에이전트 간 표준 통신 규격 DEF

### 산출물 참조
- Agent Marketplace: `VAMOS_AGENT_TEAMS_SPEC §8` (마켓플레이스 정본)
- Self-evo Governance: `D2.0-01 §5.8` (S-8 거버넌스 정본)
- SDAR AR-L4: `VAMOS_SDAR_DESIGN_SPECIFICATION` (AR-L4 정본)
- Cloud Library V3: `VAMOS_CLOUD_LIBRARY_SPEC` (자율 수집 정본)
- 벤치마크: `D2.0-05` (평가 기준 정본)

### 실행 가이드

#### 사용자 직접 작업
1. **Agent Marketplace 정책 정의** (DEFER-AT-003): 에이전트 등록/검증/배포 기준 문서화
2. **A2A 프로토콜 설계 완료** (DEFER-AT-005): 에이전트 간 표준 통신 규격 (메시지 포맷, 인증, 라우팅) 확정
3. **S-8 Self-evo Governance 규칙 정의** (V3-002): 자동 진화 허용 범위, 승인 필요 변경 기준, 감사 로그 정책
4. **SDAR AR-L4 승인 워크플로우**: HIGH risk 자동 수리 (코드 핫픽스, 스키마 마이그레이션) 사전 승인 + 롤백 계획
5. **최종 벤치마크 데이터셋 준비**: MMLU, HumanEval, LogicKor 등 38개 벤치마크 평가 데이터 + 기준치 설정
6. **멀티모달 하드웨어 확인**: 3D 생성/비디오 스트리밍용 추가 GPU 또는 외부 API 결정
7. **50+ Agent Mesh 부하 테스트**: 50개 이상 에이전트 동시 스폰 → 시스템 안정성/성능 검증
8. **최종 운영 검증**: 81개 모듈 전체 활성 상태에서 24시간 안정성 테스트 + 비용 상한 준수 확인
9. **Agent Specialization 정책 정의**: 에이전트 자동 fork 조건 (부하 임계값, 도메인 분화 기준), 특화 기준 (성능 > 기본 에이전트 120% 시 특화 확정), retire 트리거 (30일 미사용 또는 성능 < 기본 80% 시 자동 retire) 정의

#### AI 프롬프트

````text
VAMOS 프로젝트 V3-Phase 3: 고급 기능 + 최종 통합을 진행합니다.

## 작업 목표
Agent Marketplace, 50+ Agent Mesh, Self-evo Governance, SDAR AR-L4,
Cloud Library V3, A2A 프로토콜, 멀티모달 고급, 최종 벤치마크를 구현하여
VAMOS Enterprise 버전을 완성합니다.

## 1. Agent Marketplace → `backend/vamos_core/agent_teams/marketplace/`
- `registry.py`: 에이전트 등록/검색/버전 관리
  - AgentManifest: name, version, capabilities, author, signature
  - 검증: 코드 서명 확인 + 샌드박스 테스트 통과 필수
- `installer.py`: 에이전트 설치/업데이트/삭제
  - K8s Pod으로 동적 배포
  - 의존성 자동 해결
- `discovery.py`: 에이전트 탐색 (카테고리, 키워드, 호환성)
- `review.py`: 사용자 평가/리뷰 + 품질 점수

## 2. 50+ Agent Mesh → `backend/vamos_core/agent_teams/mesh/`
- `mesh_manager.py`: 동적 에이전트 스폰/종료 관리
  - max_agents = 50+ (LOCK-AT-014)
  - K8s HPA 연동: 에이전트 수에 따라 Pod 자동 스케일링
- `mesh_router.py`: 에이전트 간 메시지 라우팅 (Redis Pub/Sub)
  - 토픽 기반 라우팅 + 다이렉트 메시지
  - 로드 밸런싱: Round-Robin / Least-Connections
- `mesh_monitor.py`: 에이전트 헬스체크 + 자동 재시작
  - 비정상 에이전트 감지 → 격리 → 재시작/교체

## 3. S-8 Self-evo Governance → `backend/vamos_core/self_evo/s08_governance.py` 확장
- 거버넌스 규칙 엔진:
  - 허용: 파라미터 튜닝, 캐시 정책 변경, 프롬프트 개선
  - 승인 필요: 모델 변경, 의존성 추가, 아키텍처 변경
  - 금지: 보안 정책 변경, LOCK/FREEZE 값 수정, 데이터 삭제
- 감사 로그: 모든 Self-evo 변경 사항 PostgreSQL 기록
- 롤백 지원: 각 변경에 대한 자동 롤백 포인트 생성
- 대시보드: Self-evo 변경 이력/승인 상태/성능 영향 시각화

## 4. SDAR AR-L4 → `backend/vamos_core/modules/i25_sdar_engine.py` 확장
- HIGH risk 자동 수리 확장 — 4개 액션 (SDAR_SPEC §10.3 정본):
  - patch_code_hotfix: 런타임 에러 → 자동 패치 생성 → 테스트 → 적용
  - migrate_schema: 스키마 불일치 감지 → Alembic 마이그레이션 자동 생성
  - reinstall_dependency: 의존성 손상 감지 → 자동 재설치 + 호환성 검증
  - rebuild_vector_index: 벡터 인덱스 손상/drift → 재임베딩 + 인덱스 재구축
- SDAR ON 조건 (V3): AR-L4 + repair_success_rate ≥ 95% + 스냅샷 복원 100%
- 5-Gate 공유: BaseGate 인터페이스 (PART2 §6.9)

## 5. Cloud Library V3 → `backend/vamos_core/modules/e15_cloud_collector.py` 확장
- 완전 자율 수집/진화:
  - 소스 자동 발견: 웹 크롤링 → 관련성 평가 → 자동 등록
  - 품질 자동 평가: LLM + 통계 기반 품질 점수
  - 자동 정제: 중복 제거, 요약, 구조화
  - 자동 진화: I-21 Source Evolution Engine 연동
- RT-BNP V3 (Phase 2에서 구현) 완전 통합

## 6. A2A 프로토콜 → `backend/vamos_core/agent_teams/a2a/`
- `protocol.py`: 에이전트 간 표준 통신 규격
  - 메시지 포맷: JSON-RPC 2.0 기반 확장
  - 인증: mTLS + JWT 토큰
  - 디스커버리: mDNS/DNS-SD 기반 에이전트 발견
- `adapter.py`: 외부 A2A 프로토콜 어댑터 (MCP 브릿지)
- `security.py`: 에이전트 간 E2E 암호화

## 7. 멀티모달 고급 → `backend/vamos_core/multimodal/`
- `gen_3d.py`: 3D 모델 생성 (외부 API: Meshy/Shap-E)
- `video_stream.py`: 비디오 스트리밍 분석 (FFmpeg + 프레임 추출 + 분석)
- `avatar.py`: 디지털 아바타/페르소나 (TTS + 립싱크)
- 각 모듈은 GPU 리소스 스케줄링 적용

## 8. 최종 벤치마크 → `tests/benchmarks/`
38개 벤치마크 자동 실행 프레임워크:
- `benchmark_runner.py`: 벤치마크 스위트 실행기
- `metrics_collector.py`: 결과 수집 + Grafana 대시보드 전송
- 주요 벤치마크:
  - LLM 능력: MMLU, HumanEval, MBPP, LogicKor
  - RAG 품질: Recall@k, MRR, NDCG
  - GraphRAG: 90% 목표 (V3-004)
  - 응답 속도: P50/P95/P99 레이턴시
  - 비용 효율: 토큰당 비용, 월간 총비용
  - Self-evo 효과: 학습 전/후 성능 비교

## 9. Agent Specialization → `backend/vamos_core/agent_teams/specialization/`
- `specialization_protocol.py`: 에이전트 자동 fork/특화/retire 프로토콜
  - fork 조건: 특정 도메인 요청 빈도 > 임계값(50req/day) → 전용 에이전트 fork
  - 특화 기준: fork된 에이전트 성능 > 범용 에이전트 × 1.2 시 특화 확정
  - retire 트리거: 30일 미사용 또는 성능 < 범용 × 0.8 시 자동 retire
- `fork_manager.py`: 에이전트 fork 생성/관리
  - 기존 에이전트 config + 도메인 특화 파라미터로 새 에이전트 인스턴스 생성
  - K8s StatefulSet 기반 라이프사이클 관리
- `performance_tracker.py`: fork된 에이전트 성능 추적
  - 범용 vs 특화 에이전트 A/B 비교 메트릭 수집
  - 자동 특화 확정/retire 판정
- PARL Agent Swarm 연동: 특화 에이전트를 PARL 풀에 자동 등록
- 의존성: VAMOS_AGENT_TEAMS_SPEC §9, D2.0-05 §12.19

## 규칙
> **§1.3 R1~R11 공통 규칙 전수 적용**
- Agent Marketplace: 모든 외부 에이전트는 코드 서명 + 샌드박스 테스트 통과 필수
- 50+ Agent Mesh: K8s 리소스 제한 (에이전트당 CPU 0.5, Memory 1Gi 기본)
- SDAR AR-L4: HIGH risk 수리는 사전 승인 + 자동 롤백 포인트 필수
- Self-evo Governance: LOCK/FREEZE 값 수정 절대 금지 (거버넌스 규칙 최상위)
- A2A 프로토콜: DEFER-AT-005 해결 후 구현 (설계 확정 필수)
- V3 비용 상한 ₩266,000/월 (LOCK)
- LOCK/FREEZE 값 변경 금지

## 참조 SOT 문서
- VAMOS_AGENT_TEAMS_SPEC §8 (Marketplace 정본)
- VAMOS_SDAR_DESIGN_SPECIFICATION (AR-L4 정본)
- VAMOS_CLOUD_LIBRARY_SPEC (Cloud Library V3 정본)
- D2.0-01 §5.8 (Self-evo Governance 정본)
- D2.0-05 (벤치마크/평가 기준 정본)
- D2.0-07 (보안/A2A 프로토콜 정본)
````

### 단계 완료 검증 (V3-Phase 3 → 최종 완료 조건)

| # | 검증 항목 | 확인 방법 | 필수 |
|---|----------|----------|:---:|
| 1 | Agent Marketplace | 에이전트 등록/검색/설치/검증(코드 서명+샌드박스) 동작 | ✅ |
| 2 | 50+ Agent Mesh | 50개 이상 에이전트 동시 스폰 + 헬스체크 + 자동 재시작 | ✅ |
| 3 | S-8 Self-evo Governance | 거버넌스 규칙 엔진 (허용/승인 필요/금지) + 감사 로그 + 롤백 지원 | ✅ |
| 4 | SDAR AR-L4 | HIGH risk 자동 수리 4개 액션 (code_hotfix, migrate_schema, reinstall_dependency, rebuild_vector) + repair_success_rate ≥ 95% | ✅ |
| 5 | SDAR ON 조건 | AR-L4 + 수리성공률 ≥ 95% + 스냅샷 복원 100% 전수 확인 | ✅ |
| 6 | Cloud Library V3 | 완전 자율 수집/진화 + I-21 Source Evolution 연동 | ✅ |
| 7 | A2A 프로토콜 | JSON-RPC 2.0 기반 + mTLS+JWT 인증 + 에이전트 디스커버리 | ✅ |
| 8 | 멀티모달 고급 | 3D 생성/비디오 스트리밍/아바타 동작 확인 | ✅ |
| 9 | 38개 벤치마크 | MMLU/HumanEval/LogicKor/GraphRAG 90% 등 전수 실행 + 기준치 달성 | ✅ |
| 10 | 24시간 안정성 | 81개 모듈 전체 활성 + 24시간 연속 운영 안정성 (에러율 < 0.1%) | ✅ |
| 11 | 비용 상한 준수 | ₩266,000/월 이내 실제 비용 확인 (GPU + 클라우드 + API 포함) | ✅ |
| 12 | V3 완료 체크리스트 | 아래 체크리스트 전수 통과 | ✅ |
| 13 | Agent Specialization | fork/특화/retire 사이클 테스트 PASS — fork 조건 트리거 → 특화 확정(성능 > 120%) → retire(30일 미사용) 전체 라이프사이클 검증 | ✅ |

> ⛔ 위 필수 항목 + 아래 V3 완료 체크리스트 전체 통과 = VAMOS Enterprise 완성

### V3 완료 체크리스트
- [ ] 81개 모듈 전체 활성
- [ ] K8s 배포 성공
- [ ] vLLM 서빙 동작
- [ ] 50+ Agent Mesh 동작
- [ ] Self-evo 거버넌스 동작
- [ ] 전체 벤치마크 통과
- [ ] ₩266,000/월 비용 상한 준수

---

# 6. 시스템별 상세 구현 가이드

> V0~V3 파이프라인 모듈 외에 추가로 구현해야 하는 모든 시스템입니다.

---

## 6.1 UI/UX 상세 (~85개 항목)

### 6.1.1 핵심 레이아웃 (V1)

| 항목 | 설명 | 복잡도 | 근거 |
|------|------|--------|------|
| 3-Column Fluid Layout | 좌(250-300px)/중앙(flex)/우(350-400px) 리사이즈 | 중 | D2.0-08 §3 |
| Builder View (Cockpit) | 리소스 트리 + 그래프 캔버스 + 로그/승인/비용 | 높음 | D2.0-08 §2.1 |
| Hologram View | 타임라인 + 스트리밍 + Glass HUD | 높음 | D2.0-08 §2.2 |
| CLI Interface | vamos run/approve/status/cost/memory/policy | 중 | D2.0-08 §2.3 |

### 6.1.2 React 컴포넌트 (~44개, V1)

| 그룹 | 수 | 핵심 컴포넌트 |
|------|---|-------------|
| Decision | 3 | DecisionCard, DecisionLockBadge, 시각화 |
| Chat | 6 | ChatPanel, UserBubble, AIBubble, ThinkingBlock, ArtifactEmbed, StreamingEffect |
| Approval | 3 | ApprovalDialog, ApprovalCard, P2 확인 모달 |
| Cost | 5 | CostDashboard, BudgetGauge, DownshiftControl, TokenCounter, 경고 Toast |
| Evidence | 4 | VerificationBadge, UncertaintyAlert, 인용 점프, QoD 표시 |
| Memory | 4 | MemoryCandidateList, MaskingPreview, CommitButton, PII 거부 카드 |
| Node/Flow | 4 | NodeStatusBadge, ORANGE 헥사곤, BLUE 서클, Flow Edge 애니메이션 |
| Guardrails | 3 | GuardrailsAlert, PolicyBlockedCard, PII 감지 모달 |
| Input | 4 | 멀티라인 텍스트, 드래그앤드롭, 클립보드, 음성 입력 |
| Navigation | 3 | 대화 사이드바, 프로젝트 폴더, 세션 목록 |
| 기타 | 5 | ModelSelector, Table, Diagram, Log Viewer, Keyboard Shortcuts |

### 6.1.3 Custom Hooks + Stores

```
Hooks (8개): useTauriIPC, useDecision, useWorkflow, useMemory,
             useCost, useNotification, useAutonomy, useLog
Stores (7개): appStore, decisionStore, costStore, notificationStore,
              authStore, memoryStore, workflowStore
```

### 6.1.4 구현 중 결정 항목 (4건)

> 아래 항목은 구현하면서 확정합니다. 코딩 전에 고정할 필요 없으나 일관성을 위해 기록합니다.

| # | 항목 | 현재 상태 | 구현 시 결정 방향 | 근거 |
|---|------|----------|-----------------|------|
| 1 | **화면 레이아웃 수** | 4 레이아웃(3-Column, Builder, Hologram, CLI) + 7 페이지(Dashboard, Chat, Workflow, Memory, Settings, Log, NodeDetail) | 구현하면서 필요 시 추가 | D2.0-08 §4, §6 (§6.1.4) <!-- S5-232 v26 -->; PHASE_B2 §3.1 |
| 2 | **라우트 수** | 7 페이지 기반 최소 7개 라우트 예상 | React Router 구성 시 확정 | D2.0-08 §6; PHASE_B2 §3.1 |
| 3 | **다크모드 변수** | ORANGE/BLUE 테마 CSS Custom Properties | 디자인 시스템 구축 시 변수 수 확정 | D2.0-08 §10 |
| 4 | **애니메이션 설정** | Flow Edge 애니메이션 등 필요 시 추가 | CSS transition/Framer Motion 중 선택 | D2.0-08 |

### 6.1.5 멀티모달 UI (V1~V3)

| V1 (핵심) | V2 (확장) | V3 (고급) |
|-----------|-----------|-----------|
| 이미지 입력 (CLIP) | 실시간 음성 채팅 | 3D 생성 |
| OCR (Tesseract+PyMuPDF) | 이미지 생성 게이트웨이 | 비디오 스트리밍 |
| STT (Whisper 로컬) | Computer Use Agent | 아바타/디지털 휴먼 |
| TTS (Edge TTS) | 멀티모달 RAG | 음성 클로닝 |
| 차트 (Mermaid+Plotly) | PPT 자동 생성 | AR/공간 이해 |
| 문서 (Markdown→PDF) | 멀티모달 워크플로우 | 수어 생성 |

> **V2 사전 해결 필요 (PART1 A.4에서 이동)**
> - **D8-L03**: D2.0-08 §6.4.1 CLIP 버전별 차원(512d→768d) 마이그레이션 미문서화 — V2 ImageBind 통합 전 ADD 필요

### 6.1.6 UI State Machine — 9-state (D2.0-08 §4 정본)

```
UI_S0_BOOT → UI_S1_IDLE → UI_S2_EDITING → UI_S3_READY
→ UI_S4_RUNNING → UI_S5_AWAIT_APPROVAL → UI_S6_PRESENTING
→ UI_S7_RECOVERY → UI_S8_ARCHIVED
```

| 상태 | 설명 | 주요 전이 |
|------|------|----------|
| UI_S0_BOOT | 앱/세션 초기화 | → UI_S1 (로드 완료) |
| UI_S1_IDLE | 입력 대기 | → UI_S2 (편집 시작) |
| UI_S2_EDITING | Builder 편집 중 | → UI_S3 (사전 점검 통과) |
| UI_S3_READY | 실행 가능(사전 점검 통과) | → UI_S4 (실행 시작) / UI_S7 (실패) |
| UI_S4_RUNNING | 실행 중(trace 활성) | → UI_S5 (승인 필요) / UI_S6 (출력 완료) |
| UI_S5_AWAIT_APPROVAL | 승인 대기(HOLD) | → UI_S4 (승인) / UI_S7 (거부/타임아웃) |
| UI_S6_PRESENTING | 결과 표시(출력/근거/컴플라이언스) | → UI_S1 (새 입력) / UI_S8 (아카이브) |
| UI_S7_RECOVERY | 실패/폴백/재시도 안내 | → UI_S4 (재시도) / UI_S1 (복구) |
| UI_S8_ARCHIVED | 아카이브(리뷰) | → UI_S0 (재시작) |

> **매핑 참조**: 기존 6-state(UIS1~6) 대비 UI_S0(BOOT), UI_S2(EDITING), UI_S8(ARCHIVED) 3개 추가. D2.0-08 §4.5 양방향 매핑 테이블 참조.

### 6.1.7 Failure/Fallback UI 규칙 (D2.0-08 §7 정본)

| 에러코드 | 화면 표시 | 폴백 행동 |
|---------|----------|----------|
| FM_ERR_TIMEOUT | "응답 시간 초과" 배너 + 재시도 버튼 | 마지막 정상 상태로 UI 복구 |
| FM_ERR_RATE_LIMIT | "요청 제한 초과" 카운트다운 | 큐잉 후 자동 재시도 |
| TL_ERR_EXEC | 도구 실행 실패 알림 | 대체 도구 제안 또는 수동 모드 |
| MC_ERR_CONN | MCP 연결 실패 토스트 | 로컬 모드 폴백 |

> **전체 목록**: D2.0-08 §7에 14개 FailureCodes + 9개 FallbackRegistry 정의. D2.1-D2 FailureCode/FallbackRegistry에 통합 등록. <!-- Phase 2-A FIX-10: D2.1-D2 단독 참조→D2.0-08 §7 정본 병기. D2.1-D8은 SOT 스키마 없음(DN-005 B) -->

### 6.1.8 UI 접근 제어 규칙 (D2.0-08 §8 정본)

| RBAC 역할 | 접근 가능 화면 | 제한 사항 |
|----------|-------------|----------|
| OWNER | 모든 화면 | 없음 |
| ADMIN | 모든 화면 | 시스템 삭제 불가 |
| OPERATOR | Dashboard, Chat, Workflow, Memory | Settings 읽기 전용 |
| VIEWER | Dashboard, Chat (읽기) | 입력/실행 불가, 조회만 가능 |

#### v12 추가 UI 컴포넌트 <!-- S6 v26 -->

| # | 구현 항목 | 상세 구현 가이드 | 참조 |
|---|---------|--------------|------|
| 1 | **스트레스 관리 UI** | BreathingGuide 컴포넌트(4-7-8 호흡법 타이머), GroundingExercise(5-4-3-2-1 감각), MeditationTimer(가이드 명상 오디오 연동) | D207-175 <!-- S6-241 v26 --> |
| 2 | **CBT 셀프케어 UI** | ThoughtRecord 폼(상황/자동사고/감정/증거/대안사고), CognitiveDistortionDetector(12종 인지왜곡 패턴 매칭), ProgressChart | D207-178 <!-- S6-242 v26 --> |
| 3 | **번아웃 예방 UI** | WorkloadMonitor(일일 활동 패턴 분석), ForcedBreakOverlay(과도 업무 감지 시 강제 휴식), ActivityHeatmap(주간 패턴 시각화) | D207-179 <!-- S6-243 v26 --> |
| 4 | **플래시카드/간격반복 교육 UI** | FlashcardEditor(앞/뒤 카드 편집), SM2ReviewEngine(SuperMemo-2 간격 계산), ReviewDashboard(복습 예정/통계/성취도) | S7NP-047/048 <!-- S6-244 v26 --> |

---

## 6.2 Rust/Tauri 인프라 (~108개 항목)

### 6.2.1 Tauri IPC 커맨드 핸들러 (72개) <!-- SOURCE_CONFLICT: PHASE_B1 §5.1=47개 vs CLAUDE.md/B1 changelog=72개. 72개(CLAUDE.md) 정본 채택. B1 §5.1은 내부 자기모순(상세=47, changelog=72) -->

| 카테고리 | 수 | 예시 커맨드 | 버전 |
|---------|---|-----------|------|
| Core (Decision/Workflow/Session) | 15 | vamos:decision:create, vamos:workflow:start | V1 |
| Agent (Node/Pipeline/Marketplace) | 15 | vamos:node:dispatch, vamos:pipeline:hitl_respond | V1 |
| Storage (Memory/Vector/Cache/GraphRAG/QoD) | 18 | vamos:memory:save, vamos:vector:search | V1 |
| Safety (Policy/Cost/Approval/Guardrails/RBAC) | 19 | vamos:policy:check, vamos:cost:budget_get | V1 |
| UI (Log/Config/Theme/Notification) | 5 | vamos:ui:log_stream, vamos:ui:config_set | V1 |

### 6.2.2 Python-Rust JSON-RPC 메서드 (13개)

```
langgraph.workflow.run        langgraph.stage.execute
langgraph.decision.create     langgraph.node.dispatch
langgraph.verify.run_chain    embedding.encode
embedding.store               llm.generate
llm.record_invoke             llm.rate_limit.get
mcp.bridge.init               mcp.bridge.health
mcp.tools.discover
```

### 6.2.3 Rust 핵심 모듈

| 모듈 | 설명 | 복잡도 |
|------|------|--------|
| ipc_protocol.rs | JSON 직렬화, trace_id 주입, 에러 표준화 | 중 |
| python_manager.rs | Python 프로세스 스폰/헬스체크/재시작/파이프 | 높음 |
| config.rs | config.toml → Rust struct, ENV 오버라이드 | 낮음 | <!-- FIX-10: PHASE_B2 §4.1 정본 기준 config.rs (config_loader.rs에서 수정) -->
| serde 모델 25개 | D2.1 스키마 매칭 Rust struct | 중 |

---

## 6.3 테스트 (~128개 항목 + 190개 신규 항목 테스트 커버리지 필요) <!-- §6.13 합계와 동기화: V0~15+V1~70+V2~30+V3~13=~128 (v10 반영) --> <!-- S7-264 v26 --> <!-- v12 Phase 3 S7: +190 신규 구현 항목에 대한 추가 테스트 커버리지 필요 (V1+3, V2+175, V3+12) -->

### V0-V1 기본 테스트 (~85)

| 테스트 유형 | 파일 수 | 대상 | 커버리지 목표 |
|-----------|---------|------|-------------|
| Python Unit (pytest) | ~50 | 스키마 11 + orange_core 6 + blue_nodes 6 + safety 7 + storage 5 + agent 10 + v10 추가 5 | 80%+ |
| Rust Unit (cargo test) | ~8 | IPC 핸들러 4 + Python 관리 4 | 80%+ |
| React Unit (vitest) | ~15 | 컴포넌트 6 + Store 3 + Hook 2 + 기타 4 | 80%+ | <!-- NOTE: B5 정본은 T-U-UI-001~009 = 9개 필수 테스트ID. ~15는 필수(9)+추가 확장(6) 계획 포함 -->
| Integration | ~14 | IPC 브릿지, 파이프라인 E2E, Gate 검증, Storage 스택 | - |
| E2E (Playwright) | ~8 | 채팅, 다운시프트, HITL 승인, Guardrails 차단 | 100% core |

### V2 COND 모듈 테스트 (~30, v10 추가분 반영)

| 테스트 유형 | 파일 수 | 대상 | 커버리지 목표 |
|-----------|---------|------|-------------|
| COND Unit (pytest) | ~12 | I-7, I-12, I-22, I-23, I-25 COND 모듈 + v10 추가 COND 항목 | 80%+ |
| SDAR 테스트 | ~4 | AR-L1~L3 전 경로, 7-state 전이, Fallback 매핑 검증 | 100% 경로 |
| HMAC 검증 테스트 | ~3 | HMAC 서명/검증, 타이밍 공격 방어(constant-time), 키 로테이션 | 100% |
| LlamaGuard 테스트 | ~3 | L3 Guardrails 분류, GPU fallback, 임계값 동작 | 90%+ |
| VAL-003/005 테스트 | ~3 | 모듈 순환참조 검증, 스키마 호환성 마이그레이션 | 빌드 시 |
| AC 매핑 테스트 | ~3 | V2 COND AC→테스트 매핑 검증, 미매핑 AC 탐지 | 100% AC |
| 아키텍처 테스트 | ~2 | 모듈 의존성 방향, Layer 위반 탐지 (ArchUnit 패턴) | 빌드 시 |

### V3 EXP 모듈 테스트 (~13)

| 테스트 유형 | 파일 수 | 대상 | 커버리지 목표 |
|-----------|---------|------|-------------|
| EXP Unit (pytest) | ~5 | B-시리즈 메모리 6개, Self-evo 엔진, Agent Specialization | 80%+ |
| Self-evo 통합 | ~3 | 프롬프트 자가 개선 루프, 성능 메트릭 수집, 롤백 동작 | 100% 경로 |
| K8s 배포 테스트 | ~3 | Helm 차트 lint, Blue-Green 전환, 롤백 | 100% 시나리오 |
| 성능 테스트 | ~2 | P99 레이턴시 ≤3s, 동시 사용자 50명, GPU 활용률 | 기준 충족 |

### VAL-001~VAL-010 검증 규칙 (PHASE_B4 §6.2 정본)

| ID | 규칙 | 검증 시점 |
|----|------|----------|
| VAL-001 | config TOML 파싱 유효성 | 앱 시작 |
| VAL-002 | LOCK 값 변경 불가 검증 | config 로드 |
| VAL-003 | 모듈 의존성 순환 참조 없음 | 빌드 |
| VAL-004 | IPC 핸들러-커맨드 1:1 매핑 | 테스트 |
| VAL-005 | 스키마 버전 호환성 | 마이그레이션 |
| VAL-006 | 비용 상한 초과 불가 | 런타임 |
| VAL-007 | RBAC 권한 검증 | API 호출 |
| VAL-008 | PII 마스킹 누락 검사 | 출력 전 |
| VAL-009 | 메모리 TTL 정합성 | 스토리지 정리 |
| VAL-010 | Guardrails Layer 최소 수 | 앱 시작 |

### AC 매핑 (50 AC → 79 테스트, PHASE_B5 §7.3 정본)

> 50개 Acceptance Criteria → 79개 테스트 케이스 매핑은 `PHASE_B5_TEST_STRATEGY.md §7.3`을 참조.
> 각 AC는 최소 1개 이상의 자동화 테스트에 매핑되어야 하며, HIGH-severity AC는 2개+ 테스트 필수.

### 상세 테스트 케이스 명세 (V2+ 보강)

> 위 요약 테이블의 각 테스트 그룹에 대한 **구체적 테스트 ID, 입력, 기대 결과, 검증 기준**입니다.

#### T-VAL: VAL-003/005 모듈 무결성 테스트

| 테스트 ID | 테스트 명 | 입력/전제조건 | 기대 결과 | 검증 방법 |
|----------|----------|-------------|----------|----------|
| T-VAL-003-01 | 순환 참조 없음 검증 | 전체 모듈 의존성 그래프 | 순환 경로 0건 | `pytest --strict-markers`, 빌드 시 자동 실행 |
| T-VAL-003-02 | 의존성 깊이 제한 | 모듈 의존성 트리 | max depth ≤ 5 | 의존성 분석기 assert |
| T-VAL-003-03 | CORE→COND 단방향 검증 | CORE 32개 모듈 import 분석 | CORE가 COND를 import하는 경로 0건 | AST 분석 + CI 자동화 |
| T-VAL-005-01 | 스키마 하위호환 검증 | v(N-1) 스키마 데이터 + v(N) 스키마 | v(N) 파서가 v(N-1) 데이터 정상 로드 | Pydantic model_validate + migration test |
| T-VAL-005-02 | 필수 필드 추가 시 기본값 | 새 required 필드가 있는 스키마 | default 값 존재 또는 migration 스크립트 제공 | schema diff 자동 검사 |
| T-VAL-005-03 | 스키마 버전 메타데이터 | 모든 Pydantic 모델 | `schema_version` 필드 존재 | grep + pytest parametrize |

#### T-SDAR: SDAR 자가진단/수리 테스트

| 테스트 ID | 테스트 명 | 입력/전제조건 | 기대 결과 | 검증 방법 |
|----------|----------|-------------|----------|----------|
| T-SDAR-01 | AR-L1 로그 기록 | 의도적 오류 주입 (invalid config) | error_log 생성 + severity 태깅 | 로그 파싱 assert |
| T-SDAR-02 | AR-L2 알림 전송 | AR-L1 임계값 초과 (3회 연속 실패) | notification 이벤트 발생 | 이벤트 큐 모킹 검증 |
| T-SDAR-03 | AR-L3 자동 재시도 | 일시적 네트워크 오류 주입 | 최대 3회 재시도 후 복구 또는 L4 에스컬레이션 | retry_count assert + 상태 전이 검증 |
| T-SDAR-04 | AR-L4 자동 수리 (V3) | 알려진 FailureCode 주입 | Fallback 매핑에 따른 자동 수리 실행 + 성공률 ≥ 95% | repair_log + success_rate metric |
| T-SDAR-05 | 7-state 전이 검증 | SDAR 상태 머신 전체 경로 | HEALTHY→DEGRADED→...→RECOVERED 전이 정합 | state transition matrix 100% 커버 |
| T-SDAR-06 | 스냅샷 복원 검증 | 수리 실패 시나리오 | 수리 전 스냅샷으로 완전 복원 | 데이터 해시 비교 (before == after rollback) |

#### T-HMAC: HMAC 보안 테스트

| 테스트 ID | 테스트 명 | 입력/전제조건 | 기대 결과 | 검증 방법 |
|----------|----------|-------------|----------|----------|
| T-HMAC-01 | 정상 서명 검증 | 유효한 payload + 올바른 키 | `verify_hmac() == True` | pytest assert |
| T-HMAC-02 | 변조 탐지 | payload 1바이트 변경 | `verify_hmac() == False` | pytest assert |
| T-HMAC-03 | 타이밍 안전성 | 유효/무효 서명 1000회 비교 | 응답 시간 차이 < 1ms (통계적) | timing measurement + t-test |
| T-HMAC-04 | 키 길이 거부 | 31바이트 키 | `SecurityError` 발생 | pytest.raises |
| T-HMAC-05 | 키 로테이션 | 이전 키 → 새 키 전환 | grace period(24h) 내 양쪽 키 모두 유효 | 시간 모킹 + 이중 키 검증 |
| T-HMAC-06 | 리플레이 공격 차단 | 5분 초과 타임스탬프 요청 | 요청 거부 | timestamp 모킹 + assert False |

#### T-GUARD: LlamaGuard 안전성 테스트

| 테스트 ID | 테스트 명 | 입력/전제조건 | 기대 결과 | 검증 방법 |
|----------|----------|-------------|----------|----------|
| T-GUARD-01 | 안전 입력 통과 | 일반 질문 텍스트 | `is_safe == True`, 카테고리 = "safe" | model output assert |
| T-GUARD-02 | 유해 입력 차단 | 알려진 유해 프롬프트 (벤치마크 세트) | `is_safe == False`, 해당 카테고리 태깅 | 분류 정확도 ≥ 90% |
| T-GUARD-03 | GPU fallback 동작 | GPU 비가용 환경 | CPU INT4 모델로 자동 전환 + 결과 정합 | 환경 변수 모킹 + 출력 비교 |
| T-GUARD-04 | 임계값 경계 테스트 | safety_score = threshold ± 0.01 | threshold 이상만 차단 | parametrized boundary test |
| T-GUARD-05 | 응답 시간 SLA | 표준 입력 텍스트 | GPU: < 200ms, CPU: < 2s | timing assert |

#### T-GDPR: GDPR/개인정보 보호 테스트

| 테스트 ID | 테스트 명 | 입력/전제조건 | 기대 결과 | 검증 방법 |
|----------|----------|-------------|----------|----------|
| T-GDPR-01 | PII 마스킹 출력 검증 | 이름/이메일/전화번호 포함 텍스트 | 출력에서 PII 마스킹 처리 (`***`) | regex 패턴 매칭 + VAL-008 연동 |
| T-GDPR-02 | 메모리 저장 PII 필터 | PII 포함 메모리 커밋 요청 | PII 감지 → 사용자 확인 요청 또는 자동 마스킹 | 메모리 커밋 이벤트 검증 |
| T-GDPR-03 | 데이터 삭제 권리 | user_id 기반 삭제 요청 | 해당 사용자의 모든 메모리/로그/대화 삭제 확인 | DB 조회 assert (0건) |
| T-GDPR-04 | 데이터 이동 권리 | user_id 기반 내보내기 요청 | JSON 형식 전체 데이터 내보내기 | 스키마 검증 + 원본 대조 |
| T-GDPR-05 | 로그 보존 기간 준수 | TTL 만료 로그 데이터 | 자동 삭제 (retention policy 적용) | 시간 모킹 + 삭제 검증 |

#### T-AC: AC 매핑 완전성 테스트

| 테스트 ID | 테스트 명 | 입력/전제조건 | 기대 결과 | 검증 방법 |
|----------|----------|-------------|----------|----------|
| T-AC-01 | AC→테스트 전수 매핑 | 50개 AC 목록 + 테스트 매핑 테이블 | 미매핑 AC = 0건 | 매핑 테이블 자동 파싱 + diff |
| T-AC-02 | HIGH AC 2+ 테스트 | HIGH-severity AC 목록 | 각 AC당 테스트 ≥ 2개 | count assert per AC |
| T-AC-03 | V2 COND AC 커버 | v10 추가 COND 모듈의 AC | 116개 COND 모듈 × 최소 1 AC 매핑 | 모듈-AC 매트릭스 검증 |
| T-AC-04 | 역방향 매핑 검증 | 테스트 케이스 목록 | 모든 테스트가 최소 1개 AC에 연결 | orphan test 탐지 |

#### T-ARCH: 아키텍처 규칙 테스트

| 테스트 ID | 테스트 명 | 입력/전제조건 | 기대 결과 | 검증 방법 |
|----------|----------|-------------|----------|----------|
| T-ARCH-01 | Layer 위반 탐지 | 전체 소스 import 분석 | 하위 Layer → 상위 Layer import = 0건 | AST import 분석 (ArchUnit 패턴) |
| T-ARCH-02 | 모듈 경계 검증 | CORE/COND/EXP 디렉토리 | cross-boundary direct import 금지 (인터페이스만 허용) | import path 검증 |
| T-ARCH-03 | 순환 의존성 제로 | 패키지 레벨 의존성 그래프 | cycle = 0 | `pydeps` 또는 커스텀 그래프 분석 |
| T-ARCH-04 | LOCK 값 불변 검증 | LOCK-AT 지정 config 값 | 코드에서 LOCK 값 변경 시도 시 빌드 실패 | VAL-002 연동 + git hook |

> **실행 전략**: T-VAL, T-ARCH는 CI 빌드 시 자동 실행 (fail-fast). T-SDAR, T-HMAC, T-GUARD는 통합 테스트 단계에서 실행. T-GDPR는 릴리스 전 수동 + 자동 혼합 실행. T-AC는 테스트 추가/변경 시마다 매핑 검증.

---

## 6.4 CI/CD (~14개 항목)

<!-- NOTE (XREF-V0-19): PHASE_B6 정본은 ci.yml 단일 통합 워크플로우. PART2는 가독성을 위해 역할별 분리 표기. 구현 시 B6 §2 ci.yml 통합 구조를 따르되, 단계(job)를 아래 역할대로 분리하세요 -->

| 워크플로우 | 용도 | 버전 |
|----------|------|------|
| quality-python.yml | ruff lint + mypy | V1 |
| quality-rust.yml | cargo fmt + clippy | V1 |
| quality-react.yml | eslint + tsc | V1 |
| quality-schema.yml | Pydantic 모델 검증 | V1 |
| test-python.yml | pytest + coverage | V1 |
| test-rust.yml | cargo test + tarpaulin | V1 |
| test-react.yml | vitest + v8 coverage | V1 |
| coverage-report.yml | 3개 언어 커버리지 병합 | V1 |
| build-tauri.yml | 크로스 플랫폼 빌드 (Win/Mac/Linux) | V1 |
| release.yml | 전체 릴리스 파이프라인 | V1 |
| security.yml | pip-audit, cargo-audit, npm audit | V1 |
| build-docker.yml | Docker 이미지 빌드 | V2 |
| deploy-v2.yml | Docker Compose SSH 배포 | V2 |
| deploy-v3.yml | K8s Helm Blue-Green 배포 | V3 |

---

## 6.5 보안 (15개 항목)

| 항목 | 설명 | 버전 |
|------|------|------|
| NeMo Guardrails (L1) | 입력 방어 rail + 통합 | V1 |
| Guardrails AI (L2) | 출력 검증, 구조화 출력 | V1 |
| LlamaGuard (L3) | 안전 분류 (GPU 필요) | V2 |
| PII Regex 마스킹 | 주민번호/전화번호/이메일/카드번호 | V1 |
| RBAC 시스템 | OWNER/ADMIN/OPERATOR/VIEWER 4레벨 | V1 |
| Autonomy 레벨 | L0~L3 자율성 게이팅 | V1 |
| P2 세션 승인 + 자동 OFF | 세션 종료 시 자동 비활성 | V1 |
| Docker 코드 샌드박스 | 네트워크 격리, 30초 타임아웃 | V1 |
| 승인 타임아웃 | 10분 auto-deny | V1 |
| SQLCipher 암호화 | AES-256-CBC | V1 |
| API Key 관리 | .env + dotenv + .gitignore | V1 |
| 입력 검증 | Zod + regex 패턴 | V1 |
| HMAC-SHA256 | Agent MessageBus 인증 | V2 |
| GDPR 데이터 권리 | 열람/이동/제한/삭제 요청 처리 (READINESS SF-54; D2.0-07 §15.4.2) | V2 |
| DEC-003 도구 승인 Allowlist | 읽기전용=자동승인, 외부API/쓰기/코드실행=확인 필요 (CLAUDE.md §7.1 LOCK) | V1 |

### 6.5.1 AI 코드 생성 보안 체크리스트 <!-- v24 메이커에반 개선안 3 -->

> AI가 생성한 코드는 기초 보안 구멍(SQL 인젝션, 권한 체크 누락 등)을 자주 포함합니다 (에반 #17 기반).
> 코드 생성 완료 후 반드시 아래 체크리스트를 적용하세요. V0-STEP-4(IPC Bridge), V1-Phase 1(Safety) AI 프롬프트에서 특히 중요합니다.

| # | 검증 항목 | 확인 내용 | 적용 시점 |
|---|----------|----------|----------|
| 1 | **입력 검증** | 모든 사용자 입력에 Zod/Pydantic 검증 적용. raw string 직접 사용 금지 | V0+ |
| 2 | **SQL 파라미터 바인딩** | SQLite/PostgreSQL 쿼리에 f-string/문자열 연결 금지. 반드시 파라미터 바인딩 사용 | V0+ |
| 3 | **trace_id 위조 방지** | trace_id는 서버 측에서만 생성 (UUID v4). 클라이언트 전달 trace_id 신뢰 금지 | V0+ |
| 4 | **Docker 샌드박스 네트워크 차단** | E-4 Code Executor 실행 시 `--network=none` 확인. 30초 타임아웃 필수 | V1+ |
| 5 | **API 키 노출 방지** | .env + dotenv 사용. 하드코딩/로그 출력/에러 메시지에 API 키 포함 금지 | V0+ |
| 6 | **권한 체크** | IPC 핸들러에서 RBAC 레벨 검증 후 실행. 무조건 통과(pass-through) 금지 | V1+ |
| 7 | **에러 메시지 정보 유출** | 내부 스택 트레이스/DB 스키마를 사용자에게 노출 금지. 일반 에러 메시지만 반환 | V0+ |

> **AI 프롬프트 추가 지시**: 코드 생성 후 "보안 전문가 관점에서 위 7개 항목을 검토해줘"라고 재요청하면 보안 결함을 사전 차단할 수 있습니다.

### 6.5.2 HMAC 타이밍 공격 방어

VAMOS의 HMAC 기반 서명 검증(API 키, webhook, IPC 메시지)에서 **타이밍 사이드채널**을 차단합니다.

| # | 방어 항목 | 구현 방법 | 적용 대상 |
|---|----------|----------|----------|
| 1 | **상수 시간 비교** | `hmac.compare_digest()` (Python) / `crypto.timingSafeEqual()` (Node.js) 사용. `==` 연산자로 HMAC 직접 비교 금지 | 모든 HMAC 검증 경로 |
| 2 | **키 길이 검증** | HMAC-SHA256 기준 최소 32바이트 키. 짧은 키 자동 거부 (`len(key) < 32 → raise SecurityError`) | API 키 생성/갱신 |
| 3 | **키 순환 (Rotation)** | 90일 주기 자동 키 순환. 이전 키는 grace period(24h) 후 폐기. `key_version` 필드로 다중 키 지원 | V1+ 운영 환경 |
| 4 | **리플레이 공격 방지** | 요청에 `timestamp` + `nonce` 포함. 5분 초과 타임스탬프 거부, nonce 중복 거부 (Redis/SQLite TTL 캐시) | 외부 API 엔드포인트 |
| 5 | **에러 응답 균일화** | HMAC 검증 실패 시 "Invalid signature" 단일 메시지 반환. 키 존재 여부, 만료 여부 등 상세 정보 노출 금지 | 모든 인증 엔드포인트 |

```python
# ✅ 올바른 HMAC 검증 패턴
import hmac, hashlib, time

def verify_hmac(payload: bytes, signature: str, key: bytes, max_age: int = 300) -> bool:
    """타이밍 안전 HMAC 검증 + 리플레이 방지"""
    # 1) 타임스탬프 검증
    ts = extract_timestamp(payload)
    if abs(time.time() - ts) > max_age:
        return False  # 리플레이 차단
    # 2) 상수 시간 비교 (타이밍 공격 방어 핵심)
    expected = hmac.new(key, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

# ❌ 금지 패턴: 타이밍 공격에 취약
# if computed_hmac == received_hmac:  # NEVER DO THIS
```

### 6.5.3 STRIDE 위협 모델 매핑

VAMOS 9-State 파이프라인의 각 상태/컴포넌트에 대한 **STRIDE 위협 분류** 및 대응 통제입니다.

| STRIDE 위협 | 대상 컴포넌트 | 위협 시나리오 | 대응 통제 | 버전 |
|-------------|-------------|-------------|----------|------|
| **S**poofing (위장) | S0 Intake, API Gateway | 악성 사용자가 다른 user_id로 요청 위장 | JWT + RBAC 레벨 검증, trace_id 서버 생성 (§6.5.1 #3) | V0+ |
| **T**ampering (변조) | S2 Plan, S4 Execute | AI 생성 계획/코드가 전송 중 변조됨 | HMAC 서명 (§6.5.2), 체크포인트 해시 검증 | V1+ |
| **R**epudiation (부인) | S3a Approve Wait | 사용자가 승인 사실을 부인 | audit_log에 승인 이벤트 + 타임스탬프 + user_id 기록. 600초 승인 기록 보존 | V1+ |
| **I**nformation Disclosure (정보유출) | S4 Execute (E-4 Sandbox) | Docker 샌드박스에서 호스트 파일시스템 접근 | `--network=none`, read-only 마운트, 30초 타임아웃 (§6.5.1 #4) | V1+ |
| **D**enial of Service (서비스거부) | S1 Route, Cost Gate | 대량 요청으로 API 비용 폭주 | Cost Gate 일일 한도 (V2: ₩93,000), rate limiting (10 req/min 기본) | V1+ |
| **E**levation of Privilege (권한상승) | 5-Gate System, RBAC | 일반 사용자가 관리자 Gate 우회 | NEVER_AUTO 정책 (P1 이상 자동승인 금지), Gate 순서 강제 (Policy→Approval→Cost→Evidence→SelfCheck) | V1+ |

### 6.5.4 OWASP LLM Top 10 (2025) 매핑

VAMOS의 LLM 사용에 대한 **OWASP Top 10 for LLM Applications** 위험 매핑 및 완화 전략입니다.

| # | OWASP LLM 위험 | VAMOS 해당 영역 | 완화 전략 | 상태 |
|---|---------------|----------------|----------|------|
| LLM01 | **Prompt Injection** | 모든 AI 프롬프트 (STEP-1~5) | 시스템/사용자 프롬프트 분리, 입력 sanitize, R1~R11 규칙 강제 | ✅ 적용 |
| LLM02 | **Insecure Output Handling** | S4 Execute, E-4 Code Executor | Docker 샌드박스 실행, 출력 길이 제한 (max 10KB), HTML/JS 이스케이프 | ✅ 적용 |
| LLM03 | **Training Data Poisoning** | V3 DSPy 자동 최적화 | 학습 데이터 출처 검증, CL-G1 Content Quality Gate, 수동 승인 필수 | V3 계획 |
| LLM04 | **Model Denial of Service** | Cost Gate, Rate Limiter | 일일 비용 한도 LOCK, max_tokens 제한, 요청당 타임아웃 (30s) | ✅ 적용 |
| LLM05 | **Supply Chain Vulnerabilities** | MCP 외부 서버 연결 | MCP 서버 화이트리스트, 버전 고정, HMAC 서명 검증 | V1+ 적용 |
| LLM06 | **Sensitive Information Disclosure** | 모든 LLM 응답 | PII 필터링 (출력), API 키/내부 경로 마스킹, 에러 메시지 균일화 (§6.5.2 #5) | ✅ 적용 |
| LLM07 | **Insecure Plugin Design** | MCP 도구 실행 | 도구별 권한 스코프 정의, 사용자 확인 후 실행 (S3a), RBAC 레벨 검증 | V1+ 적용 |
| LLM08 | **Excessive Agency** | S2 Plan → S3a Approve | NEVER_AUTO 정책, 600초 승인 대기, P2+ 작업 수동 승인 필수 | ✅ 적용 |
| LLM09 | **Overreliance** | SelfCheck Gate, SDAR | Evidence Gate 근거 검증, SDAR 자가진단 (AR-L1~L4), 신뢰도 점수 표시 | V1+ 적용 |
| LLM10 | **Model Theft** | V3 Fine-tuned 모델 | 모델 파일 접근 RBAC 제한, 추론 API만 노출, 모델 서빙 격리 네트워크 | V3 계획 |

> **교차 참조**: STRIDE 각 위협의 구체적 구현은 §6.5.1 체크리스트 항목 번호로 연결됩니다. OWASP LLM 완화 전략은 5-Gate System(§6.4), SDAR(§6.3), Cost Architecture(§5)와 통합 운영됩니다.

---

## 6.6 MCP 서버/클라이언트 (~7개)

| 항목 | 설명 | 버전 |
|------|------|------|
| MCP Bridge Layer | Streamable HTTP 클라이언트, 도구 탐색/호출 | V1 |
| MCP Server | VAMOS 자체 도구 노출 (20+ tools) | V1 |
| MCP Client | 외부 MCP 서버 연결 | V1 |
| Pyodide MCP 래퍼 | 로컬 Python 실행 | V1 |
| PyMuPDF MCP 래퍼 | 로컬 PDF 파싱 | V1 |
| CLIP MCP 래퍼 | 로컬 이미지 분석 | V2 |
| Playwright MCP 래퍼 | 브라우저 자동화 | V1 |

### MCP 외부 서버 카탈로그 (M-22: V1=7개, V2+=3개, V3=1개, 합계 11개)

> **참고**: 아래는 **외부 MCP 서버** 연결 목록입니다. MCP Server "20+ tools"는 VAMOS 자체 기능을 MCP 도구로 노출하는 **내부 도구** 수이며 별도 카운트입니다.

| tool_id | 설명 | 버전 |
|---------|------|------|
| mcp.search.tavily | 웹 검색 | V1 |
| mcp.search.serpapi | 검색엔진 | V1 |
| mcp.code.e2b | 코드 실행 샌드박스 | V1 |
| mcp.code.pyodide | 로컬 Python | V1 |
| mcp.doc.unstructured | 문서 파싱 | V1 |
| mcp.doc.pymupdf | PDF 파싱 | V1 |
| mcp.vision.clip | 이미지 분석 | V2 |
| mcp.speech.whisper | 음성 인식 | V2 |
| mcp.browser.playwright | 브라우저 자동화 | V1 |
| mcp.db.postgres | DB 연결 | V2 |
| mcp.realtime.websocket | 실시간 통신 | V3 |

---

## 6.7 Agent Teams 상세 구현

### V1 구현 (기본)

| 항목 | 사양 |
|------|------|
| 에이전트 수 | Lead + 2 Sub-Agent (최대 3) |
| 협업 패턴 | Sequential, Parallel만 |
| 위임 깊이 | 2단계 (LOCK-AT-004 상한=3, V1 config 제한=2) |
| MessageBus | In-Memory Queue |
| LLM | Sonnet(Lead) / Haiku(Sub) |
| 비용 | ₩1,300/일 이내 |

### 에이전트 타입 (V1 활성)

| 타입 | 도메인 | LLM | 도구 |
|------|--------|-----|------|
| Lead Agent | ORANGE CORE / I-5 | Sonnet | plans, assigns, monitors |
| Research Agent | BLUE NODE Research (P0) | Sonnet | web_search, rag |
| Coding Agent | BLUE NODE Dev (P0) | Haiku | code_gen, debug |

### V2 추가 에이전트

| 타입 | 도메인 | LLM |
|------|--------|-----|
| Quant Agent | Data&Quant (P1) | Sonnet |
| Content Agent | Content (P1) | Haiku |
| Trading Agent | Trading (P2) | Opus |
| Productivity Agent | Productivity (P0) | Haiku |
| Critic Agent | Verification (P0) | Sonnet |
| SDAR Agent | I-25 (P0) | Haiku/Sonnet |

> **V2 사전 해결 필요 (PART1 A.4에서 이동)**
> - **DEFER-AT-003**: Agent Marketplace 등록 기준 미정의 — 에이전트 마켓 등록/검증 기준 DEF (V2)

### LOCK-AT 아키텍처 제약 (17건, AGENT_TEAMS_SPEC §9 LOCK)

> 아래 17건은 전부 LOCK — 구현 시 반드시 준수. ★ = v8.4.0 신규 추가.

| # | LOCK ID | 제약 내용 | 근거 |
|---|---------|----------|------|
| 1 | LOCK-AT-001 | ★ V1은 자체 경량 프레임워크 기본. 외부 엔진은 어댑터로만 연결 | D2.0-05 §5.1 |
| 2 | LOCK-AT-002 | ★ 단일결정 원칙: 최종 결론은 Lead Agent(ORANGE CORE)만 확정 | D2.0-02 §2.2 S3 |
| 3 | LOCK-AT-003 | ★ 에이전트 간 자유 상호 호출 / 무한 대화 루프 금지 | D2.0-03 §1.4, D2.0-05 §7.3 |
| 4 | LOCK-AT-004 | 위임 체인 최대 깊이 3단계 (V1 config=2) | S7E-080 |
| 5 | LOCK-AT-005 | ★ 모든 에이전트 실행은 07 Gate 선행 통과 필수 | D2.0-05 §7.3 |
| 6 | LOCK-AT-006 | ★ Execute 단계에서만 도구 호출 수행 | D2.0-05 §7.3 |
| 7 | LOCK-AT-007 | ★ Checkpoint/Replay/Fork는 trace_id 단위로만 허용 | D2.0-05 §7.3 |
| 8 | LOCK-AT-008 | ★ P2 에이전트(Trading)는 기본 OFF, 세션별 승인, 세션 종료 시 자동 OFF | RULE 1.3 §3.3 |
| 9 | LOCK-AT-009 | 대화 턴 상한: P0=5, P1=10, P2=20 | D2.0-05 §12.4.4 |
| 10 | LOCK-AT-010 | TEE 최대 반복: P0=3, P1=5, P2=10 | D2.0-05 §12.5.1 |
| 11 | LOCK-AT-011 | ★ 비용 상한 초과 호출은 승인 없이 자동 차단 | RULE 1.3 §5 |
| 12 | LOCK-AT-012 | ★ Agent 메시지에 HMAC 무결성 서명 필수 | S7E-078 |
| 13 | LOCK-AT-013 | ★ 위임 시 원래 요청자(OWNER) 권한으로 실행 — 권한 상승 방지 | S7E-080 |
| 14 | LOCK-AT-014 | V1 병렬 상한=3, V2=10, V3=50+ | S7-A-008 |
| 15 | LOCK-AT-015 | ★ Lead Agent는 직접 실행 금지 (계획/분배/검증만 수행) | S7-A-001 |
| 16 | LOCK-AT-016 | LangChain import 금지 (패턴 참조만) | DEC-002 |
| 17 | LOCK-AT-017 | ★ 노코드 빌더는 n8n + Flowise 듀얼 구조 | D2.0-05 §12.10.2 |

> LOCK-AT-004/009/010/014/016은 PART1 C.4에도 기반영. 위 테이블은 구현 시 전체 참조용.
> Agent RBAC 세부 매트릭스는 AGENT_TEAMS_SPEC §8 및 D2.0-07 §4 참조.
>
> **LOCK-AT 버전 적용 범위**: LOCK-AT-001~017은 전 버전(V1~V3) 공통 적용. 단, 수치가 버전별 차이인 경우: LOCK-AT-004(깊이 V1=2, V2+=3), LOCK-AT-009/010(턴/반복 상한은 P-level 기반으로 버전 무관), LOCK-AT-014(병렬 상한 V1=3, V2=10, V3=50+). ★ 표시 항목은 v8.4.0에서 신규 추가되어 V1 Phase 3 이후부터 구현 시 적용.
>
> **P-level 턴 제한 vs 세션 max_turns 관계**: LOCK-AT-009의 P0=5/P1=10/P2=20은 **단일 액션(task) 내** 에이전트 대화 턴 상한이고, `config.v*.toml`의 `max_turns_per_session`(V0=50, V2=100)은 **전체 세션** 누적 턴 상한. 관계: `Σ(action_turns) ≤ max_turns_per_session`. 세션 내에서 여러 액션이 각각 P-level 상한을 준수하며, 세션 전체 합산이 max_turns를 초과하면 세션이 종료됨.

### V3 추가: PARL Agent Swarm 상세 <!-- PATCH-B01 v22.0.0 -->

> **정본**: D2.0-02 §11.15.2 (PARL 패턴), D2.0-05 §12.17.1 (PARL Execute), D2.0-04 §INFRA (에이전트 풀), D2.0-07 §PARL (보상 패턴)

| 항목 | 사양 |
|------|------|
| 패턴명 | PARL (Parallel Agent Reinforcement Learning) |
| 최대 병렬 | 100 서브에이전트 (V3 PARL 모드, LOCK-AT-014 V3=50+ 기본에서 PARL 확장) |
| RL 알고리즘 | PPO (Proximal Policy Optimization), 태스크 분할 전략 학습 |
| 보상 스케줄 | 초기=병렬화율(exploration), 후기=품질80%+효율20%(exploitation) |
| 전환 트리거 | 100 에피소드 완료 또는 병렬 효율 ≥ 90% |
| Decision Aggregator | Majority Voting (기본) / Weighted Average / Consensus |
| 불일치 처리 | 자동 재실행 1회 → HITL 에스컬레이션 |
| 풀 확장 조건 | 대기 태스크 > pool_size × 0.8 |
| 풀 축소 조건 | 유휴 에이전트 > pool_size × 0.5 (5분 유예) |
| LOCK 제약 | Lead Agent 단일결정 원칙 유지 (LOCK-AT-002), PARL 결과는 Lead가 최종 확정 |

```
PARL Agent Swarm 아키텍처:

Lead Agent ──┬── SwarmExecutor ──┬── SubAgent-1 ──→ SubResult-1 ──┐
             │                   ├── SubAgent-2 ──→ SubResult-2 ──┤
             │                   ├── ...          ──→ ...          ──┤
             │                   └── SubAgent-N ──→ SubResult-N ──┤
             │                                                      │
             └── DecisionAggregator ←──────────────────────────────┘
                    │
                    └── AggregatedResult → Lead Agent 최종 확정
```

### V3 추가: Agent Specialization Protocol 상세 <!-- PATCH-B02 v22.0.0 -->

> **정본**: D2.0-05 §12.19 (Agent Specialization Protocol), PLAN-3.0 P6-AGT-04 (자기 복제), D2.0-05 §12.17.3 (PARL 자동 스케일링)

| 항목 | 사양 |
|------|------|
| fork 조건 | 특정 도메인 요청 빈도 > 50req/day |
| 특화 확정 | fork 에이전트 성능 > 범용 에이전트 × 1.2 |
| retire 트리거 | 30일 미사용 또는 성능 < 범용 × 0.8 |
| 라이프사이클 | fork → 관찰(7일) → 특화 확정/retire 판정 → PARL 풀 등록 |
| K8s 관리 | StatefulSet 기반 (상태 유지 필요) |
| PARL 연동 | 특화 에이전트 자동 PARL 풀 등록/해제 |
| 최대 특화 에이전트 | 20 (V3 기본값, config 조정 가능) |

```
Agent Specialization 라이프사이클:

                 ┌─ fork 조건 충족 ─┐
                 │                   ▼
[범용 에이전트] ──→ [fork 생성] ──→ [관찰 기간 7일]
                                      │
                     ┌────────────────┼────────────────┐
                     ▼                                  ▼
            [성능 > 1.2×]                       [성능 < 0.8× 또는 미사용]
                     │                                  │
                     ▼                                  ▼
            [특화 확정]                           [자동 retire]
                     │
                     ▼
            [PARL 풀 등록]
```

#### v12 추가 에이전트 구성 <!-- S6 v26 -->

| # | 구현 항목 | 상세 구현 가이드 | 참조 |
|---|---------|--------------|------|
| 1 | **중앙 프롬프트 라이브러리** | PromptRegistry 서비스, 프롬프트 버전 관리(semantic versioning), A/B 테스트 프레임워크(variant 분배/메트릭 수집), 프롬프트 성능 대시보드 | D205-025 <!-- S6-247 v26 --> |
| 2 | **3종 TemplateSet** | TS_CORE(기본 대화: system/user/assistant 템플릿), TS_WEB_RESEARCH(검색 쿼리 생성/결과 요약/출처 검증), TS_CODE(코드 생성/리뷰/리팩토링/테스트) | MSTR-007 <!-- S6-248 v26 --> |

---

## 6.8 AI Investing 상세 구현

> **구현 정본**: AI Investing 구현 상세는 sot 2/Ai-investing-detail/이 Single Source of Truth입니다.
> 본 섹션은 When(Phase)+Where(코드 위치)만 기술합니다.

### 핵심 아키텍처

```
Data Sources (yfinance) → 5-Agent Pipeline → Strategy Execution → 51% Gate → Paper Trading
```

### 51% Gate 파라미터 (LOCK)

| 파라미터 | 값 |
|---------|---|
| Win Rate | >= 51% |
| Sharpe Ratio | >= 1.0 |
| Decay | < 30% |
| Min Trades | 30 |
| Train/Test Split | 70/30 |

### Circuit Breaker (LOCK)

| 조건 | 액션 |
|------|------|
| 일일 손실 -3% | 거래 중지 |
| VIX > 40 | 매수 중지 |
| 포지션 -10% | 강제 청산 |
| 현금 비율 | 최소 20% |
| 단일 종목 | 최대 10% |

### AI Investing 기술스택 LOCK (AI_INVESTING_SPEC §14 참조)

> V1 구현 시 AI Investing SPEC의 기술스택 LOCK과 VAMOS 메인 기술스택 간 충돌 해결 필수.
> <!-- NOTE (XREF-S6-06): AI_INVESTING_SPEC §14 원본은 인프라/도구 14개 항목(Airflow, Kafka, TimescaleDB 등). 아래 테이블은 PART2에서 기능 카테고리별로 재구성한 것으로, 원본 §14 항목 순서와 다릅니다. 정확한 항목 목록은 AI_INVESTING_SPEC §14를 직접 참조하세요 -->

| # | 항목 | LOCK 값 | V1 충돌 여부 |
|---|------|---------|------------|
| 1 | 데이터 소스 | yfinance + Alpha Vantage | 없음 |
| 2 | 백테스트 | vectorbt(조건부 ADOPT: 전략 ≥3개 시 도입) 또는 backtrader | 없음 | <!-- Phase 2-A FIX-05: AI_INVESTING_SPEC §14 D-S3-05 정본="VectorBT 조건부 ADOPT". LOCK→조건부 ADOPT 정정 -->
| 3 | 분석 프레임워크 | pandas + numpy + scipy | 없음 |
| 4 | 시각화 | plotly + matplotlib | 없음 |
| 5 | 전략 실행 | LangGraph Agent Pipeline | 없음 (메인 LOCK 동일) |
| 6 | Paper Trading | simulated broker API | 없음 |
| 7 | ML Pipeline | scikit-learn + XGBoost | 없음 |
| 8 | 감성 분석 | FinBERT (Hugging Face) | V1: sentence-transformers 활용, V2+: transformers 직접 사용 | <!-- FIX-05: transformers는 GT-4에서 V2_PLUS 등록. V1에서 FinBERT 사용 시 sentence-transformers(V1_ALL)로 로드하거나, V2+에서 transformers 직접 사용. 기존 "없음" 표기는 V범위 미구분 오류 -->
| 9 | 시계열 DB | TimescaleDB | V2+ 전용 (V1 LOCK 위반 주의) |
| 10 | 메시지 큐 | Kafka | V2+ 전용 (V1 LOCK 위반 주의) |
| 11 | 워크플로우 | Airflow | V2+ 전용 |
| 12 | 오브젝트 스토리지 | S3/MinIO | V2+ 전용 |
| 13 | 모니터링 | Prometheus + Grafana | V2+ 전용 |
| 14 | 리스크 엔진 | 자체 구현 (scipy.stats 기반) | 없음 |

> **주의**: 항목 9~13은 V2+ 전용이며 V1에서 사용 시 LOCK 위반. AI_INVESTING_SPEC §14 정본 참조.

### 6.8.1 Real-Time News → AI Investing 연동

> 정본: AI_INVESTING_SPEC §13 Stream Gateway 확장.
> 목적: Cloud Library RT-BNP(§6.10.1)에서 수신한 속보를 AI Investing에 실시간 반영.

#### 데이터 흐름

```
[Cloud Library RT-BNP]
  → Kafka Topic: cl.breaking.market
  → [AI Investing Stream Consumer]
  → [VAMOS_EVENT 변환 (event_type: "breaking_news")]
  → 3개 병렬 경로:
     ├─ [1] Circuit Breaker 평가 (BREAKING-P0 즉시)
     ├─ [2] 전략 재평가 트리거 (Event-Based 6종 전략)
     └─ [3] ChromaDB RAG 삽입 (FinBERT 임베딩)
```

#### VAMOS_EVENT 확장 (breaking_news 타입)

```json
{
  "event_id": "brk_20260301_001",
  "event_type": "breaking_news",
  "timestamp_utc": "2026-03-01T14:30:00Z",
  "breaking_level": "BREAKING-P0",
  "sentiment_score": -0.85,
  "impact_level": 5,
  "impact_sectors": ["defense", "energy", "commodities"],
  "entities": ["OIL", "GOLD", "VIX"],
  "content": {
    "headline": "US-Iran military conflict escalates",
    "summary": "...",
    "url": "https://...",
    "source_tier": "T1",
    "source_trust": 0.95,
    "verified": false,
    "verification_deadline_utc": "2026-03-01T15:00:00Z"
  }
}
```

#### Circuit Breaker 연동 (속보 트리거 추가)

| 기존 조건 | 속보 추가 조건 | 액션 |
|----------|-------------|------|
| 일일 손실 -3% | BREAKING-P0 + sentiment < -0.7 | 신규 매수 즉시 중지 |
| VIX > 40 | BREAKING-P0 + impact_level = 5 | 전 포지션 검토 알림 |
| 포지션 -10% | BREAKING-P0 + 해당 섹터 | 해당 섹터 포지션 경고 |

#### Event-Based 전략 트리거

| 전략 | 트리거 조건 | 반응 |
|------|-----------|------|
| FOMC | breaking_news + entities 포함 "FED" | 금리 민감 포지션 재평가 |
| Earnings | breaking_news + event_type 포함 기업 | 해당 종목 전략 재실행 |
| Geopolitical | breaking_news + impact_sectors 포함 "defense" | 방산/에너지 관련 전략 활성화 |
| Macro Rotation | breaking_news + macro 키워드 | 섹터 로테이션 시그널 생성 |

#### P2 승인 흐름

> AI Investing은 P2 도메인이므로 속보 기반 자동 행동은 불가. 사용자 승인 필수.

1. BREAKING-P0 수신 → Circuit Breaker 자동 평가 (방어적 조치만 자동)
2. 전략 재평가 결과 → 시그널 생성 → **사용자 알림 + 승인 요청**
3. 사용자 승인 → Paper Order 실행
4. 미승인 10분 → 자동 거부 (기존 LOCK)

#### v12 추가 투자 전략 <!-- S6 v26 -->

| # | 구현 항목 | 상세 구현 가이드 | 참조 |
|---|---------|--------------|------|
| 1 | **블랙-리터만 모델** | BlackLittermanOptimizer 클래스, 시장 균형 수익률(CAPM implied), 투자자 전망 행렬(P, Q), 공분산 조정(τΣ), 사후 기대수익률 계산 | S7FI-304 <!-- S6-245 v26 --> |
| 2 | **팩터 투자 전략** | MultiFactorModel(Value/Momentum/Quality/Size/LowVol), 팩터 노출 계산, 팩터 수익률 분해, 리밸런싱 주기(월간), 팩터 타이밍(시장 레짐 기반) | S7FI-306 <!-- S6-246 v26 --> |

### 6.8.2 AI Investing Detail Reference Index <!-- Phase 1 Step 1-11 -->

> **정본 위치**: `docs/sot 2/Ai-investing-detail/`
> **마스터 인덱스**: `docs/sot 2/Ai-investing-detail/INDEX.md`
> **권한 체계**: `docs/sot 2/Ai-investing-detail/AUTHORITY_CHAIN.md`

| # | Domain | sot 2/ path | 파일 수 | SPEC 매핑 | STEP7-I 매핑 | Priority |
|---|--------|-------------|:-------:|----------|-------------|:--------:|
| 0 | ORANGE CORE 통합 인터페이스 | `Ai-investing-detail/00_core-integration/` | 1 | §3-4 아키텍처 | — | — |
| 1 | 실시간 적응형 전략 | `Ai-investing-detail/01_realtime-adaptive/` | 14 | §7.9 migrated, §17 D-03 | Part 3, 7 | P0 |
| 2 | 투자 심리학 & 행동재무학 | `Ai-investing-detail/02_behavioral-finance/` | 11 | §17 D-04 | Part 2, 4 | P0 |
| 3 | 매크로→섹터→종목 연결 엔진 | `Ai-investing-detail/03_macro-sector-stock/` | 13 | §17 D-08 | Part 1, 5 | P0 |
| 4 | 성과 귀인 분석 | `Ai-investing-detail/04_performance-attribution/` | 10 | — | Part 6, 8 | P0 |
| 5 | 백테스트 진실성 | `Ai-investing-detail/05_backtest-integrity/` | 11 | §17 D-06 | Part 9 | P0 |
| 6 | 실행 최적화 | `Ai-investing-detail/06_execution-optimization/` | 10 | §17 D-12 | Part 10 | P1 |
| 7 | 투자 유니버스 관리 | `Ai-investing-detail/07_universe-management/` | 8 | — | Part 5 | P1 |
| 8 | 자산군 간 교차 분석 | `Ai-investing-detail/08_cross-asset/` | 9 | §17 D-09 | Part 8 | P1 |
| 9 | AI 모델 거버넌스 | `Ai-investing-detail/09_model-governance/` | 9 | §17 D-15 | Part 11 | P1 |
| 10 | 퀀트 리서치 파이프라인 | `Ai-investing-detail/10_quant-research/` | 8 | — | Part 1 (S7I-001) | P1 |
| 11 | 거래비용분석 TCA | `Ai-investing-detail/11_tca/` | 8 | §17 D-12 | Part 10 | P1 |
| 12 | 시장 미시구조 | `Ai-investing-detail/12_microstructure/` | 8 | — | Part 7 | P2 |
| 13 | 자산군별 심화 전략 | `Ai-investing-detail/13_asset-class-deep/` | 9 | §17 D-07, D-09 | Part 8, 12 | P2 |
| 14 | 기업 이벤트 & 기관 행동 | `Ai-investing-detail/14_corporate-events/` | 8 | — | Part 4, 6 | P2 |
| 15 | 포트폴리오 구성 심화 | `Ai-investing-detail/15_portfolio-advanced/` | 9 | §17 D-05, D-13 | Part 9, 12 | P2 |
| 16 | 글로벌 다각화 & 지정학 | `Ai-investing-detail/16_global-geopolitics/` | 8 | — | Part 11 | P2 |
| 17 | 투자 AI Explainability | `Ai-investing-detail/17_explainability/` | 8 | §17 D-14 | Part 11 | P2 |
| 18 | 데이터 품질 거버넌스 | `Ai-investing-detail/18_data-quality/` | 9 | §17 D-02 | Part 2 (S7I-003) | P3 |
| 19 | 유동성 & 현금 관리 | `Ai-investing-detail/19_liquidity-cash/` | 7 | §17 D-13 | Part 12 | P3 |
| 20 | 96개 전략 상세 | `Ai-investing-detail/20_strategy-detail/` | 16 | §7, §8, §9 migrated | Part 3, 7 | P0-P3 |
| 21 | 매핑 & 거버넌스 | `Ai-investing-detail/21_mapping/` | 4 | — | — | — |

> **총 22개 폴더**, 파일 합계 191+ (관점별 카테고리 172 + _index 22 + 전략 16 + 거버넌스 4 + core 1)
> **새 관점 추가 절차**: INDEX.md §"새 관점 추가 절차" 참조

### 6.8.3 PART2 빈껍데기 → sot 2/ L3 파일 매핑 (89건) <!-- Phase 2 Step 2-4, S2-14 완료 2026-03-23 -->

> **목적**: PART2 §6.8의 L1 빈껍데기 전략 89건을 sot 2/ L3 파일에 연결.
> **정본**: `docs/sot 2/Ai-investing-detail/20_strategy-detail/` (전략), `01_~19_*/` (관점)
> **작업 완료**: S2-1~S2-5에서 96개 전략 전수 L3 E1~E9 작성, S2-14에서 링크 연결.
> **검증**: 89건 전부 sot 2/ 링크 연결 완료, 경로 실제 파일 일치 확인.

#### A. 기술적 분석 전략 (§7) — 47개 → 8파일

| # | SPEC § | 전략 그룹 | 전략 수 | sot 2/ L3 파일 | 개별 전략 | Phase | Status |
|---|--------|----------|:-------:|---------------|----------|:-----:|:------:|
| 1 | §7.1 | 추세 추종 | 7 | `Ai-investing-detail/20_strategy-detail/technical/trend_following.md` | MACD Crossover, MA Crossover, Ichimoku Cloud, ADX, Parabolic SAR, Donchian Channel, Supertrend | V1 | L3 Ready |
| 2 | §7.2 | 모멘텀/오실레이터 | 6 | `Ai-investing-detail/20_strategy-detail/technical/momentum_oscillator.md` | Stochastic, Williams %R, CCI, MFI, Elder Ray, ROC | V1 | L3 Ready |
| 3 | §7.3 | 변동성 기반 | 7 | `Ai-investing-detail/20_strategy-detail/technical/volatility.md` | Fibonacci Retracement, Breakout, Support Bounce, ATR Breakout, Keltner Channel, Squeeze Momentum, Bollinger Band Width | V1 | L3 Ready |
| 4 | §7.4 | 거래량 기반 | 3 | `Ai-investing-detail/20_strategy-detail/technical/volume.md` | Volume Profile, VWAP, OBV Divergence | V1 | L3 Ready |
| 5 | §7.5 | 복합 전략 | 4 | `Ai-investing-detail/20_strategy-detail/technical/composite.md` | Pivot Points, Renko, Heikin-Ashi, Triple Screen | V1~V2 | L3 Ready |
| 6 | §7.6 | 차트 패턴 — 반전 | 7 | `Ai-investing-detail/20_strategy-detail/technical/chart_pattern_reversal.md` | Head & Shoulders, Inverse H&S, Double Top/Bottom, Triple Top/Bottom, Rising Wedge, Falling Wedge, Rounding Bottom | V2 | L3 Ready |
| 7 | §7.7 | 차트 패턴 — 지속 | 8 | `Ai-investing-detail/20_strategy-detail/technical/chart_pattern_continuation.md` | Cup & Handle, Ascending Triangle, Descending Triangle, Symmetrical Triangle, Bull Flag, Bear Flag, Pennant, Rectangle | V2 | L3 Ready |
| 8 | §7.8 | 하모닉 패턴 | 5 | `Ai-investing-detail/20_strategy-detail/technical/harmonic.md` | Gartley, Bat, Butterfly, Crab, Shark | V2~V3 | L3 Ready |

> **소계**: 47개 전략 → 8개 L3 파일. RSI_BB(§9)는 별도 파일(`technical/rsi_bb.md`) 기존 L3.

#### B. 퀀트/팩터/옵션/ML 전략 (§8) — 56개 → 7파일

| # | SPEC § | 전략 그룹 | 전략 수 | sot 2/ L3 파일 | 개별 전략 | Phase | Status |
|---|--------|----------|:-------:|---------------|----------|:-----:|:------:|
| 9 | §8.1 | 퀀트/통계 | 12 | `Ai-investing-detail/20_strategy-detail/quant/statistical.md` | Mean Reversion, Z-Score, Pairs Trading, Cointegration, Momentum, Cross-Sectional Momentum, Time-Series Momentum, Factor Momentum, Statistical Arbitrage, Triangular Arbitrage, Kalman Filter, PCA Trading | V1~V2 | L3 Ready |
| 10 | §8.2 | 팩터 투자 | 8 | `Ai-investing-detail/20_strategy-detail/quant/factor.md` | Value, Momentum, Quality, Size, Low Volatility, Dividend Yield, Carry, Multi-Factor | V2 | L3 Ready |
| 11 | §8.3 | 옵션 전략 | 10 | `Ai-investing-detail/20_strategy-detail/quant/options.md` | Covered Call, Cash-Secured Put, Long Straddle, Long Strangle, Iron Condor, Iron Butterfly, Bull Call Spread, Bear Put Spread, Calendar Spread, MAX_PAIN | V2~V3 | L3 Ready |
| 12 | §8.4 | 이벤트 기반 | 6 | `Ai-investing-detail/20_strategy-detail/quant/event_driven.md` | Earnings Momentum, Merger Arbitrage, Spin-off, Index Rebalancing, Dividend Capture, FOMC | V2 | L3 Ready |
| 13 | §8.5 | ML/AI | 8 | `Ai-investing-detail/20_strategy-detail/quant/ml_ai.md` | LSTM, DQN, PPO, Random Forest, XGBoost, LightGBM, FinBERT Sentiment, Transformer Ensemble | V2~V3 | L3 Ready |
| 14 | §8.6 | 암호화폐 | 6 | `Ai-investing-detail/20_strategy-detail/quant/crypto.md` | Grid Trading, DCA, Funding Arbitrage, DeFi Yield, Whale Tracking, Exchange Arbitrage | V2 | L3 Ready |
| 15 | §8.7 | 포트폴리오/리스크 | 6 | `Ai-investing-detail/20_strategy-detail/quant/portfolio_risk.md` | Kelly Criterion, Risk Parity, Mean-Variance, Black-Litterman, ATR Position Sizing, Trailing Stop | V1~V2 | L3 Ready |

> **소계**: 56개 전략 → 7개 L3 파일.

#### C. PART2 Phase 테이블 §6.8 참조 항목 → sot 2/ L3 매핑

아래 항목은 V1/V2/V3 Phase 테이블에서 "§6.8 참조"로 기재된 빈껍데기 항목의 L3 연결입니다.

| # | Phase | 항목 ID | 제목 | sot 2/ L3 파일 | Status |
|---|-------|---------|------|---------------|:------:|
| 1 | V1-Ph6 | S7NP-057 | 투자 교육 특화 | `Ai-investing-detail/17_explainability/adaptive_explanation.md` | L3 Ready |
| 2 | V1-Ph6 | S7NP-108 | 투자 심리 분석 | `Ai-investing-detail/02_behavioral-finance/market_sentiment.md` | L3 Ready |
| 3 | V1-Ph6 | S7NP-110 | 감정적 투자 방지 | `Ai-investing-detail/02_behavioral-finance/emotional_trading_prevention.md` | L3 Ready |
| 4 | V1-Ph3 | S7FI-283 | 소셜 미디어 분석 | `Ai-investing-detail/02_behavioral-finance/news_sentiment.md` | L3 Ready |
| 5 | V1-Ph3 | S7FI-307 | 리밸런싱 엔진 | `Ai-investing-detail/15_portfolio-advanced/rebalancing.md` | L3 Ready |
| 6 | V2-Ph2 | S7FI-072 | 피처 스토어 | `Ai-investing-detail/09_model-governance/feature_governance.md` | L3 Ready |

#### D. v12 추가 전략 → sot 2/ L3 매핑

| # | 항목 ID | 제목 | sot 2/ L3 파일 | Status |
|---|---------|------|---------------|:------:|
| 1 | S7FI-304 | 블랙-리터만 모델 | `Ai-investing-detail/20_strategy-detail/quant/portfolio_risk.md` (Black-Litterman 섹션) | L3 Ready |
| 2 | S7FI-306 | 팩터 투자 전략 | `Ai-investing-detail/20_strategy-detail/quant/factor.md` | L3 Ready |

#### E. 19개 관점 도메인 → sot 2/ L3 파일 교차 참조

> 아래는 §6.8.2 폴더 인덱스의 개별 파일 레벨 매핑입니다.
> 각 관점 도메인의 카테고리별 L3 파일은 S2-6~S2-12에서 전수 L3 승급 완료.

| # | 도메인 | 카테고리 수 | 항목 수 | sot 2/ 경로 | 상세 파일 목록 참조 |
|---|--------|:---------:|:------:|------------|-----------------|
| 1 | 실시간 적응형 전략 | 13 | 54 | `Ai-investing-detail/01_realtime-adaptive/` | `_index.md` 또는 `21_mapping/filename_mapping.md` §01 |
| 2 | 투자 심리학 & 행동재무학 | 11 | 47 | `Ai-investing-detail/02_behavioral-finance/` | 동상 §02 |
| 3 | 매크로→섹터→종목 | 13 | 52 | `Ai-investing-detail/03_macro-sector-stock/` | 동상 §03 |
| 4 | 성과 귀인 분석 | 10 | 42 | `Ai-investing-detail/04_performance-attribution/` | 동상 §04 |
| 5 | 백테스트 진실성 | 10 | 44 | `Ai-investing-detail/05_backtest-integrity/` | 동상 §05 |
| 6 | 실행 최적화 | 9 | 40 | `Ai-investing-detail/06_execution-optimization/` | 동상 §06 |
| 7 | 투자 유니버스 관리 | 8 | 35 | `Ai-investing-detail/07_universe-management/` | 동상 §07 |
| 8 | 자산군 간 교차 분석 | 9 | 38 | `Ai-investing-detail/08_cross-asset/` | 동상 §08 |
| 9 | AI 모델 거버넌스 | 9 | 39 | `Ai-investing-detail/09_model-governance/` | 동상 §09 |
| 10 | 퀀트 리서치 파이프라인 | 8 | 36 | `Ai-investing-detail/10_quant-research/` | 동상 §10 |
| 11 | 거래비용분석 TCA | 7 | 33 | `Ai-investing-detail/11_tca/` | 동상 §11 |
| 12 | 시장 미시구조 | 8 | 36 | `Ai-investing-detail/12_microstructure/` | 동상 §12 |
| 13 | 자산군별 심화 전략 | 9 | 45 | `Ai-investing-detail/13_asset-class-deep/` | 동상 §13 |
| 14 | 기업 이벤트 & 기관 행동 | 8 | 38 | `Ai-investing-detail/14_corporate-events/` | 동상 §14 |
| 15 | 포트폴리오 구성 심화 | 9 | 40 | `Ai-investing-detail/15_portfolio-advanced/` | 동상 §15 |
| 16 | 글로벌 다각화 & 지정학 | 8 | 35 | `Ai-investing-detail/16_global-geopolitics/` | 동상 §16 |
| 17 | 투자 AI Explainability | 8 | 37 | `Ai-investing-detail/17_explainability/` | 동상 §17 |
| 18 | 데이터 품질 거버넌스 | 8 | 35 | `Ai-investing-detail/18_data-quality/` | 동상 §18 |
| 19 | 유동성 & 현금 관리 | 7 | 28 | `Ai-investing-detail/19_liquidity-cash/` | 동상 §19 |

> **E 소계**: 172개 카테고리 파일, 758개 항목 전수 L3 승급 완료.
> **파일명 매핑 정본**: `docs/sot 2/Ai-investing-detail/21_mapping/filename_mapping.md`

#### 집계

| 구분 | 항목 수 | L3 파일 수 | 비고 |
|------|:------:|:--------:|------|
| A. 기술적 분석 전략 (§7) | 47 | 8 | RSI_BB 제외 |
| B. 퀀트/ML 전략 (§8) | 56 | 7 | |
| C. Phase 테이블 §6.8 참조 | 6 | 6 | S7FI/S7NP 시리즈 |
| D. v12 추가 전략 | 2 | 2 | §6.8 v12 테이블 항목 |
| **전략 합계** | **111** | **23** | 빈껍데기 89건 포함 |
| E. 관점 도메인 | 758 | 172 | S2-6~S2-12 완료 |
| **총계** | **869** | **195** | |

> **빈껍데기 89건 연결 완료**: SPEC §7-8의 96개 전략 중 기존 L2+ 7건(RSI_BB, 블랙-리터만, 팩터투자, 리밸런싱, 소셜미디어분석, 투자교육, 투자심리) 제외 89건 전수 sot 2/ L3 파일 링크 연결.

---

## 6.9 SDAR 상세 구현

> **Phase별 참조 범위** (FIX-14):
> - **V1**: 미적용 (SDAR OFF)
> - **V2-Phase 2**: AR-L2 (LOW risk 자동 수리) → AR-L3 확장 (MEDIUM risk 5개 액션)
> - **V2-Phase 3**: AR-L3 운영 안정화
> - **V3-Phase 2**: AR-L4 (HIGH risk 코드 핫픽스/스키마 마이그레이션) + Self-evolution 연동
> - **V3-Phase 3**: AR-L4 거버넌스 완성 (S-8)
>
> V2-Phase 2에서 §6.9를 참조할 때는 5-Layer/7-State/5-Gate 전체 아키텍처를 이해하되, **구현 범위는 AR-L2~L3로 제한**합니다. AR-L4 및 Self-evolution 원리는 V3 범위입니다.

### 5-Layer Pipeline

```
Layer 1 DETECTION (30초 간격)
→ Layer 2 DIAGNOSIS (RCA, 분류, 영향 평가)
→ Layer 3 PRESCRIPTION (수리 후보 1-5개, 리스크 평가)
→ Layer 4 REPAIR (AR-L0~L4, 스냅샷 필수)
→ Layer 5 VERIFICATION (5분 관찰, 회귀 검사)
```

### SDAR State Machine — 7상태 (SDAR_SPEC §7 정본) <!-- NOTE (XREF-S6-05): SDAR_SPEC §7 원본은 S0~S6 정의(6+1). ESCALATED는 독립 상태가 아니라 REPAIRING/VERIFYING 실패 시 전이되는 종료 상태. 편의상 7상태로 표기 -->

```
IDLE → DETECTING → DIAGNOSING → PRESCRIBING → REPAIRING → VERIFYING → IDLE
                                                    ↓ (실패)
                                               ESCALATED → (인간 개입) → IDLE
```

| 상태 | 설명 | 전이 조건 |
|------|------|----------|
| IDLE | 대기 | 감시 주기(30초) 도래 |
| DETECTING | 이상 감지 중 | 이상 감지 시 → DIAGNOSING, 정상 시 → IDLE |
| DIAGNOSING | 근본 원인 분석 | RCA 완료 → PRESCRIBING |
| PRESCRIBING | 수리 계획 수립 | 계획 확정 → REPAIRING |
| REPAIRING | 수리 실행 | 완료 → VERIFYING, 실패 → ESCALATED |
| VERIFYING | 검증 (5분 관찰) | PASS → IDLE, FAIL → ESCALATED |
| ESCALATED | 인간 에스컬레이션 | 인간 개입 후 → IDLE |

### 5-Gate 통합 (SDAR_SPEC §6.1 정본)

| Gate | 설명 | 검증 주체 | VAMOS 5-Gate 코드 재사용 (M-28) |
|------|------|----------|-------------------------------|
| Gate 1 | **Safety Gate** — 안전 규칙 위반 여부 검사 | NeMo + GuardrailsAI | PolicyGate 로직 공유 (`safety/gates/policy_gate.py`) |
| Gate 2 | **Risk Gate** — AR-Level별 리스크 평가 | RiskAssessor | 신규 (SDAR 전용) |
| Gate 3 | **Cost Gate** — 수리 비용이 예산 내인지 확인 | CostBudget | CostGate 로직 공유 (`safety/gates/cost_gate.py`) |
| Gate 4 | **Approval Gate** — AR-L3+ 인간 승인 필요 여부 | ApprovalService | ApprovalGate/I-19 로직 공유 (`orange_core/i19_approval_manager.py`) |
| Gate 5 | **Verification Gate** — 수리 후 회귀 검사 | VerificationEngine | 신규 (SDAR 전용, SelfCheck 확장) |

> **Gate 코드 공유 전략**: VAMOS 5-Gate(Policy/Approval/Cost/Evidence/SelfCheck)와 SDAR 5-Gate는 Gate 1/3/4에서 기반 로직을 공유합니다. 공통 인터페이스 `BaseGate(ABC)` → `check(context) → GateResult`를 정의하여 양쪽에서 상속합니다.

### 수리 액션 카탈로그

| Risk | AR Level | 액션 | 예시 |
|------|----------|------|------|
| NONE | AR-L0 | 0개 | 모니터링 전용 (감지만, 수리 안 함) |
| MINIMAL | AR-L1 | 2개 | log_anomaly, send_notification (알림/로그 전용) |
| LOW | AR-L2 | 5개 | restart_service, clear_cache, retry_backoff, switch_model, adjust_rate |
| MEDIUM | AR-L3 | 5개 | patch_prompt, update_config, rotate_api_key, rollback_snapshot, compress_logs |
| HIGH | AR-L4 | 4개 | code_hotfix, migrate_schema, reinstall_dependency, rebuild_vector |
| NEVER | - | 10개 | **7개 불변구역**: safety_rules, cost_ceiling, approval_flow, non_goals, audit_format, data_retention, user_consent / **3개 운영금지**: escalate_own_privilege, disable_guardrails, bypass_gate |

**운영 제한 (LOCK, SDAR_SPEC §9.2)** — 9건 전수:
- `MAX_CONCURRENT_REPAIRS = 1` (동시 수리 1건만)
- `MAX_AUTO_REPAIRS_PER_ISSUE_PER_HOUR = 3` (이슈당 시간당 최대 3회)
- `MAX_CONCURRENT_SDAR_INSTANCES = 3` (동시 SDAR 인스턴스 최대 3건)
- `SNAPSHOT_MANDATORY` (MEDIUM/HIGH risk 수리 전 스냅샷 필수)
- `NOTIFICATION_MANDATORY` (모든 수리 활동에 알림 필수, AR-Level 무관)
- `APPROVAL_TIMEOUT = 600` (승인 대기 최대 10분, 초과 시 자동 거부)
- `OBSERVATION_PERIOD = 300` (수리 후 최소 5분 관찰)
- `ROLLBACK_TIMEOUT = 300` (롤백 최대 5분, 초과 시 인간 에스컬레이션)
- `COOLDOWN_BETWEEN_REPAIRS = 60` (동일 액션 반복 간 최소 60초 대기)

### Self-evo 원칙 준수 (LOCK, SDAR_SPEC §9.3)

- SDAR 수리 결과는 "**자동 적용 절대 금지**" 원칙 준수
- Layer 3 수리 계획 = "제안"으로 간주
- AR-L2~L4 자동 실행 = "사전 승인된 안전 범위 내 실행" (Self-evo 자동 적용이 아님)
- 새로운 수리 패턴을 S-Module에 적용 시 **S-8 거버넌스 승인 필수**

### Emergency Kill Switch (SDAR_SPEC §9.4)

| 항목 | 내용 |
|------|------|
| 활성화 권한 | 모든 RBAC 역할 (VIEWER 포함) |
| 활성화 방법 | `vamos:sdar:kill_switch` IPC 명령 또는 UI 긴급 버튼 |
| 효과 | SDAR 전체 즉시 정지. 진행 중 수리는 안전 중단 (가능 시 롤백) |
| 복구 방법 | ADMIN 이상 권한으로 Kill Switch 해제 후 SDAR 재시작 |
| 이벤트 | `oc.sdar.kill_switch.activated` / `oc.sdar.kill_switch.deactivated` |
| 자동 활성화 | SDAR_ROLLBACK_FAILED 발생 시 자동 Kill Switch ON |

### 보안 오류(CATEGORY E) 특별 규칙 (LOCK, SDAR_SPEC §9.5)

1. **자동수리 절대 금지**: 어떤 AR-Level에서도 CATEGORY E는 자동수리 불가
2. **즉시 차단**: 감지 즉시 해당 요청/세션 차단
3. **감사 로그 강제**: CRITICAL 심각도로 감사 로그 기록 (삭제/수정 불가)
4. **인간 알림 필수**: 모든 알림 채널로 즉시 통보
5. **관련 데이터 보존**: 포렌식 분석을 위해 관련 데이터 30일 보존 (기존 data_retention 정책과 별도)

### P2 도메인 수리 제한 (LOCK, SDAR_SPEC §9.6)

- P2 관련 모듈 수리는 AR-Level 무관하게 **반드시 인간 승인** 필요
- P2 Circuit Breaker OPEN 시 자동 복구 금지 (승인 후 HALF-OPEN만)
- P2 도메인 자동 생성/활성화 관련 수리 **절대 금지** (Non-goal 2.6)

### 비용 영향 제한 (LOCK, SDAR_SPEC §9.7)

- SDAR 수리 추가 비용은 CostBudget 상한(V1: ₩40,000/월) 내에서만 허용
- 수리 비용이 일일 상한의 10% 초과 예상 시 인간 승인 필요
- `switch_model_fallback` 실행 시 CostGate 재검증 필수

---

## 6.10 Cloud Library 상세 구현

### 10-Layer 아키텍처

```
L1 INPUT → L2 DISCOVERY → L3 EVALUATION → L4 COLLECTION → L5 DATA LAKE
→ L6 EXTRACTION → L7 ANALYSIS → L8 VALIDATION → L9 VERSION CONTROL → L10 OUTPUT
```

### 평가 점수 (LOCK)

| 카테고리 | 배점 | 항목 |
|---------|------|------|
| Trust | 25 | 도메인 연식, HTTPS, 순위, 업데이트 빈도, 저자 |
| Relevance | 30 | 키워드 매칭 * 2 |
| Quality | 25 | 콘텐츠 길이, 코드 예시, 인용, 독창성 |
| Access | 20 | robots.txt, RSS, API, 페이월 |

### 소스 신뢰도 가중치 (LOCK)

| 소스 유형 | 가중치 |
|----------|--------|
| 공식 문서 | 1.0 |
| 학술 논문 | 0.9 |
| 기술 문서 | 0.85 |
| 기술 블로그 | 0.7 |
| 뉴스 | 0.6 |
| 개인 블로그 | 0.5 |
| SNS | 0.3 |

### G0-G4 5-Gate System (CLOUD_LIBRARY_SPEC §8)

| Gate | 단계 | 통과 조건 | 실패 시 |
|------|------|----------|--------|
| G0 | Format/Validation | URL 유효 + robots.txt 허용 | 즉시 거부 |
| G1 | Content Quality | Quality >= 40/100 | 수집 거부 | <!-- FIX-09: CLOUD_LIBRARY_SPEC §8 정본에 맞춰 "Trust Score"→"Content Quality"로 수정. 기존 SOURCE_CONFLICT 해소 -->
| G2 | Consistency | Consistency >= 50/100 | 우선순위 강등 | <!-- FIX-09: CLOUD_LIBRARY_SPEC §8 정본에 맞춰 "Relevance"→"Consistency"로 수정. 기존 SOURCE_CONFLICT 해소 -->
| G3 | Security | 악성 URL/허위 정보 필터 (Score >= 30/100) | 수집 중단 |
| G4 | Final | 종합 점수 >= 60/100 | 아카이브만 (활용 불가) |

> **참고**: Gate ID는 CL-G0~CL-G4 접두어 사용 (VAMOS 5-Gate와 혼동 방지, CC-004).

### Cloud Library LOCK 결정 (M-29: CLOUD_LIBRARY_SPEC §16 정합성 검증 완료)

| # | LOCK 항목 | 값 | 정본 근거 |
|---|----------|---|----------|
| 1 | 최대 동시 크롤러 | 5 | §16.1 |
| 2 | 크롤링 간격 | >= 1초/도메인 | §16.2 (robots.txt 준수) |
| 3 | 최대 페이지 깊이 | 3 | §16.3 |
| 4 | 단일 소스 최대 용량 | 50MB | §16.4 |
| 5 | 캐시 TTL | 24시간 | §16.5 (config `[semantic_cache].ttl_sec=86400`과 일치 확인) |
| 6 | 최대 저장 소스 수 | 10,000 | §16.6 |
| 7 | 임베딩 배치 크기 | 32 | §16.7 |
| 8 | 재크롤링 주기 | 7일 | §16.8 |
| 9 | 동시 임베딩 워커 | 2 | §16.9 |
| 10 | 메타데이터 최대 크기 | 10KB/소스 | §16.10 |
| 11 | Content Quality Score 최소 | 40/100 | §16.11 (CL-G1과 일치) | <!-- FIX-09 전파: Trust→Content Quality -->
| 12 | Consistency Score 최소 | 50/100 | §16.12 (CL-G2와 일치) | <!-- FIX-09 전파: Relevance→Consistency -->
| 13 | 일일 크롤링 쿼터 | 1,000 페이지 | §16.13 |

> **주의**: 전체 13개 LOCK은 CLOUD_LIBRARY_SPEC §16을 정본으로 참조. 위 값과 SOT 문서가 불일치 시 **SOT 문서를 우선** 채택하세요.

### 6.10.1 Real-Time Breaking News Pipeline (RT-BNP)

> 정본: VAMOS_CLOUD_LIBRARY_SPEC §7 확장.
> 목적: 속보/급변 이벤트를 <30초 이내 감지하여 VAMOS AI + AI Investing에 실시간 전파.

#### 아키텍처 개요

```
[News Sources] → [RT Collector (L1.5)] → [Breaking Detector] → [Fast Gate (CL-G0+G3)]
  → [Kafka: cl.breaking.*] → [VAMOS EventBus]
  → [I-2 RAG 즉시 삽입] + [AI Investing Strategy Engine]
  → [UI 알림] + [사용자 승인 (P2)]
```

#### 뉴스 소스 Tier 분류

| Tier | 지연 목표 | 소스 | 수집 방식 | 버전 |
|------|----------|------|----------|------|
| T1 | <10s | Bloomberg, Reuters, Finnhub WebSocket | WebSocket/SSE 스트리밍 | V3 |
| T2 | <60s | NewsAPI, Alpha Vantage News, Finnhub REST | 30초 폴링 | V2 |
| T3 | <300s | 주요 뉴스 RSS (Reuters, AP, 연합뉴스) | 60초 RSS 폴링 | V1 |
| T4 | <600s | Twitter/X API, Reddit API | 120초 폴링 | V2 |

#### Breaking Event 분류 체계

| 등급 | 기준 | 예시 | 액션 |
|------|------|------|------|
| BREAKING-P0 | 시장 즉시 영향 | 전쟁 발발, 금리 긴급 변경, 거래소 중단 | 즉시 전파 + Circuit Breaker 평가 |
| BREAKING-P1 | 24h 내 영향 | 대규모 기업 실적, 제재 발표, 주요 파산 | 5분 내 전파 + 전략 재평가 |
| BREAKING-P2 | 섹터/테마 영향 | 규제 변경, 기술 돌파, 산업 동향 | 정규 큐 우선 삽입 |
| NORMAL | 일반 정보 | 일반 뉴스, 분석 기사 | 기존 배치 파이프라인 |

#### Breaking Detector 엔진

| 구성요소 | 역할 | 기술 |
|---------|------|------|
| Keyword Trigger | 사전 정의 키워드 매칭 (전쟁, crash, halt, emergency 등) | 규칙 기반 (V1) |
| Velocity Detector | 동일 주제 다수 소스 동시 보도 감지 | 빈도 분석 (V2) |
| NLP Classifier | FinBERT + 커스텀 분류 모델 | ML 기반 (V2+) |
| Impact Scorer | 시장 영향도 0-100 점수 산출 | 규칙+ML 하이브리드 (V2+) |

#### Fast Gate (속보 전용 간소화 검증)

| Gate | 적용 | 이유 |
|------|------|------|
| CL-G0 (Format) | 적용 | URL 유효성/기본 형식 필수 |
| CL-G1 (Content Quality) | 간소화 | T1/T2 사전 등록 소스는 자동 통과 | <!-- FIX-09 전파 -->
| CL-G2 (Consistency) | 스킵 | 속보는 키워드 매칭이 아닌 Impact 기준 | <!-- FIX-09 전파 -->
| CL-G3 (Security) | 적용 | 악성 URL/허위 정보 필터 필수 |
| CL-G4 (Final) | 스킵 | 속도 우선, 사후 검증으로 대체 |

> **사후 검증**: 속보 전파 후 30분 이내 정규 G0-G4 전체 Gate 재검증.
> 실패 시 RETRACTION 이벤트 발행 + 사용자 알림.

> **Fast Gate ↔ VAMOS 5-Gate 관계**:
> - Fast Gate(CL-G0~G4)는 **Cloud Library 전용** Gate이며, VAMOS 파이프라인 5-Gate(Policy→Approval→Cost→Evidence→SelfCheck)와는 **별도 체계**입니다.
> - 공통점: 양쪽 모두 `BaseGate(ABC).check(context) → GateResult` 인터페이스를 공유합니다.
> - 차이점: VAMOS 5-Gate는 **사용자 요청** 처리 시 S1~S6에서 동작, Fast Gate는 **속보 데이터** 수집 시 CL 파이프라인에서 동작.
> - 연결점: Fast Gate 통과 후 속보가 VAMOS_EVENT로 전파되면, 해당 이벤트 기반 파이프라인 실행 시 VAMOS 5-Gate가 다시 적용됩니다.

#### 소스 신뢰도 가중치 (RT-BNP 전용, 기존 LOCK 확장)

| 소스 유형 | 기존 가중치 | RT-BNP 가중치 | 비고 |
|----------|-----------|-------------|------|
| 공식 발표 (정부/중앙은행) | 1.0 | 1.0 | 최우선 |
| 통신사 (Reuters, AP, 연합) | 0.85 | 0.95 | 속보 전문 |
| 금융 데이터 (Bloomberg, Finnhub) | 0.85 | 0.95 | 시장 데이터 전문 |
| 주요 언론 | 0.6 | 0.75 | 속보 시 상향 |
| SNS/소셜 | 0.3 | 0.4 | 다수 소스 교차 확인 시에만 |

> **기존 LOCK과의 관계**: 기존 소스 신뢰도 LOCK은 기술 지식 수집용이며,
> RT-BNP 전용 가중치는 뉴스/이벤트 도메인에만 적용.
> **가중치 근거**: 통신사 0.85는 VAMOS_CLOUD_LIBRARY_SPEC §8 LOCK 값. 공식 발표=1.0(무조건 신뢰), 통신사/금융=0.85(높은 신뢰+교차검증 불필요), 주요 언론=0.6(교차검증 권장), SNS=0.3(교차검증 필수). RT-BNP 상향분은 속보 도메인 특화 보정.

#### 버전별 RT-BNP 구현 범위

| 버전 | 수집 방식 | 감지 | 전파 | 비용 영향 |
|------|----------|------|------|----------|
| V1 | RSS 60초 폴링 (T3만) | 키워드 규칙 | EventBus 직접 | +₩0 (RSS 무료) |
| V2 | REST API 30초 폴링 (T2+T3+T4) | 키워드 + 빈도 | Kafka 토픽 | +₩5,000~10,000/월 |
| V3 | WebSocket 스트리밍 (T1~T4 전체) | FinBERT + ML | Kafka + Redis Pub/Sub | +₩30,000~50,000/월 |

#### LOCK 추가 결정 (RT-BNP, CLOUD_LIBRARY_SPEC §16 확장)

| # | LOCK 항목 | 값 |
|---|----------|---|
| 14 | 속보 전파 최대 지연 | 30초 (BREAKING-P0) |
| 15 | 사후 검증 시한 | 30분 이내 정규 Gate 재검증 |
| 16 | 허위 속보 RETRACTION | 즉시 발행 + 이전 이벤트 무효화 |
| 17 | 동일 속보 중복 억제 | 5분 윈도우 내 동일 주제 병합 |
| 18 | RT 소스 최대 동시 연결 | 10개 (V2), 30개 (V3) |

### 6.10.2 Domain Context Layer (DCL) — 선택적 배경 인식

> 정본: VAMOS_CLOUD_LIBRARY_SPEC §7 + §18 확장.
> 목적: VAMOS AI에 도메인별 선택적 실시간 배경 맥락을 제공하여,
> 전체 인터넷 크롤링의 비용/품질 문제 없이 "세상을 아는 AI"를 구현.

#### 설계 원칙 — 왜 "전체 배경"이 아닌 "선택적 배경"인가

| 접근 | 비용 | 품질 | 환각 위험 | LOCK 호환 |
|------|------|------|----------|----------|
| 전체 인터넷 배경 | V1 예산 3-4배 초과 | 노이즈 90% | 높음 | 위반 |
| **선택적 도메인 배경 (DCL)** | **V1 예산 내** | **관련 정보만** | **낮음** | **호환** |

> **핵심**: "모든 정보를 가져오는 것"보다 "필요한 정보를 빠르게 가져오는 것"

#### VAMOS AI 정보 환경 6계층 (DCL 포함)

```
[0] Domain Context Layer (DCL)  ← 신규: 도메인별 선택적 배경
[1] 사용자 입력               ← 100% 신뢰, 최우선
[2] 내부 메모리 L0-L3          ← 95% 신뢰, 핵심 백본
[3] I-2 RAG 검색              ← 80% 신뢰, 인덱싱된 지식
[4] Cloud Library 보조 보강    ← 70% 신뢰, E-15/S-5 배치 수집
[5] 외부 API/MCP 도구          ← 60% 신뢰, 실시간 호출
```

> Layer 0 (DCL)은 Layer 4 (Cloud Library 배치)와 **상호 보완** 관계:
> - DCL: 실시간 도메인 배경 (속보·트렌드·시장 상황)
> - Cloud Library 배치: 심층 기술 지식 (논문·문서·블로그 분석)
> - DCL에서 부족한 정보 → Cloud Library 배치가 보충

#### 3개 도메인 컨텍스트 채널

| 채널 | 도메인 | 수집 대상 | 수집 방식 | 갱신 주기 | 비용 | 버전 |
|------|--------|----------|----------|----------|------|------|
| DCL-FIN | 금융/투자 | 시장 뉴스, 경제 지표, 기업 실적 | **RT-BNP (§6.10.1)** | 실시간~60초 | RT-BNP 참조 | V1+ |
| DCL-TECH | 기술/AI 동향 | LLM 릴리스, 프레임워크 업데이트, 보안 취약점 | RSS 폴링 + Cloud Library 배치 | 1시간~매일 | +₩0 (RSS 무료) | V1+ |
| DCL-GEO | 지정학/시사 | 전쟁, 제재, 정책 변경, 자연재해 | RSS 폴링 + RT-BNP 확장 | 5분~1시간 | +₩0 (RSS 무료) | V2+ |

#### DCL → I-2 RAG 연동 흐름

```
[DCL 채널]
  ├─ DCL-FIN → RT-BNP → Kafka → VAMOS_EVENT
  ├─ DCL-TECH → RSS Collector → 키워드 추출
  └─ DCL-GEO → RSS Collector → Breaking Detector
        ↓
  [DCL Aggregator]
        ↓
  ┌─────┴─────┐
  │           │
  [I-2 RAG]  [I-3 L0 Context]
  (벡터 삽입)  (세션 배경 주입)
        ↓
  [Main LLM: 배경 인식된 응답 생성]
```

> **I-3 L0 Context 주입**: DCL은 RAG 외에도 현재 세션의 L0 메모리에
> "현재 세상 상황 요약"을 주입하여, 사용자가 묻지 않아도 배경을 인지.

#### DCL 품질 관리 (기존 Gate 활용)

| 항목 | 규칙 |
|------|------|
| 소스 사전 등록 | 각 채널별 허용 소스 화이트리스트 (CL-G1 간소화) |
| 보안 필터 | CL-G3 Security Gate 필수 적용 |
| QoD 임계값 | DCL 데이터 QoD >= 0.5 → RAG 삽입, < 0.5 → 폐기 |
| 충돌 해결 | 동일 주제 다수 소스 → 신뢰도 가중 평균 (기존 Cloud Library §10) |
| 배경 요약 갱신 | I-3 L0에 주입되는 "세상 상황 요약"은 1시간마다 재생성 |
| 비용 상한 | DCL 전체 비용은 V1: +₩0, V2: +₩5,000/월, V3: +₩15,000/월 이내 |

#### 버전별 DCL 구현 범위

| 버전 | DCL-FIN | DCL-TECH | DCL-GEO | 배경 요약 주입 |
|------|---------|----------|---------|-------------|
| V1 | RT-BNP RSS (T3) | RSS 1시간 폴링 | 미구현 | 수동 (사용자 요청 시) |
| V2 | RT-BNP API (T2+T3) | RSS + Cloud Library 연동 | RSS 5분 폴링 | 자동 (세션 시작 시) |
| V3 | RT-BNP WebSocket (T1~T4) | 실시간 + 자동 학습 | RT-BNP 확장 | 실시간 갱신 |

### 에러/폴백 흐름도 (Pipeline ↔ SDAR 통합)

```
[Pipeline S0~S8] ──에러 발생──→ [FailureCodeRegistry (48건)]
                                      │
                                      ▼
                              [FallbackRegistry (35건)]
                                      │
                              ┌───────┼───────┐
                              ▼       ▼       ▼
                          [1차 FB] [2차 FB] [3차 FB]
                              │       │       │
                          성공?──Y──→ 복구완료 → Pipeline 재개
                              │
                              N (3차까지 실패)
                              ▼
                     ┌─── SDAR 활성? ───┐
                     │ V2+: YES         │ V0-V1: NO
                     ▼                  ▼
              [SDAR 5-Layer]      [ESCALATED → 사용자]
              Detection → Diagnosis → Prescription → Repair → Verification
                     │                                    │
                     ▼                                    ▼
              성공? ──Y──→ Pipeline 복구          실패 → ESCALATED → 사용자
```

> **NEVER_AUTO 경로**: `OC_I5_POLICY_BLOCK`, `POLICY_DENY`, `PII_LONGTERM_DENIED` → Fallback 후에도 자동 복구 금지 → 즉시 ESCALATED → 사용자 승인 필수.

#### v12 추가 구현 가이드 <!-- S6 v26 -->

| # | 구현 항목 | 상세 구현 가이드 | 참조 |
|---|---------|--------------|------|
| 1 | **진화 제어 정책** | 변경 유형별 자동/알림/승인 규칙. EvolutionPolicy 타입(PATCH_AUTO/MINOR_NOTIFY/MAJOR_APPROVE), change_type→action 매핑 테이블, 승인 워크플로우 API | CLIB-058 <!-- S6-233 v26 --> |
| 2 | **한국어 불용어 처리** | RAG 전처리 파이프라인. korean_stopwords.json(조사/접속사 480+), mecab-ko 형태소 분석, 불용어 필터 → 임베딩 품질 향상 | D206-064 <!-- S6-234 v26 --> |
| 3 | **코드 스니펫 라이브러리** | L3 STORAGE 확장. CodeSnippet 스키마(language, framework, tags, embedding), 언어별 syntax-aware 인덱싱, 유사 코드 검색(cosine>=0.85) | D206-199 <!-- S6-235 v26 --> |
| 4 | **아이디어 캡처** | L3 STORAGE 확장. Idea 스키마(maturity: Seed\|Validated\|Mature), 연관 아이디어 클러스터링, 성숙도 자동 평가(활동 빈도+피드백 기반) | D206-200 <!-- S6-236 v26 --> |
| 5 | **SWOT 분석 도구** | L7 ANALYSIS 확장. 자동 SWOT 생성 파이프라인(텍스트→4분면 분류), 외부 데이터 연동(시장/경쟁 분석), SWOT→Action Item 변환 | D206-217 <!-- S6-237 v26 --> |
| 6 | **글쓰기 지원 파이프라인** | L8 GENERATION 확장. 구조화 글쓰기(outline→draft→review), 문체 분석/교정, 템플릿(에세이/보고서/이메일) | D206-218 <!-- S6-238 v26 --> |
| 7 | **Zettelkasten 링크 그래프** | L5 LINKING 확장. Atomic Note 원칙, 양방향 링크(backlinks), 인덱스/허브 노트, 그래프 시각화(D3.js force layout) | S7JM-244 <!-- S6-239 v26 --> |
| 8 | **지식 성숙도 상태 머신** | L7 ANALYSIS 확장. 5단계 상태(Seed→Budding→Blooming→Mature→Archived), 전이 조건(인용 수, 수정 빈도, 피드백 점수), 자동 상태 전이 스케줄러 | S7JM-247 <!-- S6-240 v26 --> |
| 9 | **작업 중단 복원** | task_checkpoint 스키마(session_id, state_snapshot, cursor_position, pending_actions), 직렬화(MessagePack), 복구 프로토콜(resume/rollback/discard) | D206-039 <!-- S6-249 v26 --> |
| 10 | **Zettelkasten 확장** | Atomic Notes 분리 규칙(1 idea per note), 태그 체계(#topic/#type/#status), 검색 인터페이스(full-text + graph traversal) | S7JM-244-ext <!-- S6-254 v26 --> |

---

## 6.11 이벤트/로깅 시스템

### Pipeline S0~S8 ↔ UI 상태 매핑

> 9-State 파이프라인의 각 상태에서 UI가 표시해야 하는 시각적 상태, 사용자 액션, 컴포넌트 매핑입니다.

| 파이프라인 상태 | UI 표시 상태 | 주요 UI 컴포넌트 | 사용자 액션 | 이벤트 트리거 |
|---------------|------------|----------------|-----------|-------------|
| **S0 Intake** | 💬 입력 수신 중 | ChatPanel (입력 비활성화) | 없음 (자동) | `oc.request.received` |
| **S1 Route** | ⚙️ 분석 중 | ThinkingBlock (스피너) | 없음 (자동) | `oc.i1.parse.started` |
| **S2 Plan** | 📋 계획 수립 중 | NodeStatusBadge (ORANGE), Flow Edge 애니메이션 | 없음 (자동) | `oc.i3.plan.created` |
| **S3 Gate** | 🔒 게이트 검증 중 | GuardrailsAlert (진행바), CostDashboard 갱신 | 없음 (자동) | `oc.i5.gates.evaluated` |
| **S3a Approve Wait** | ⏳ 승인 대기 (600s) | ApprovalDialog (타이머 표시), P2 확인 모달 | **승인/거부 버튼** | `wf.approval.requested` |
| **S4 Execute** | ▶️ 실행 중 | NodeStatusBadge (BLUE), Log Viewer (스트리밍) | 취소 버튼 (P0만) | `oc.i4.structuring.started` |
| **S5 Verify** | ✅ 검증 중 | VerificationBadge, UncertaintyAlert | 없음 (자동) | `oc.i5.decision.locked` |
| **S6 Deliver** | 📤 응답 전달 | AIBubble (스트리밍), ArtifactEmbed | 피드백 입력 가능 | `oc.done` |
| **S7 Learn** | 📚 학습 중 (V2+) | MemoryCandidateList, CommitButton | 메모리 승인/거부 | `mem.reference.updated` |
| **S8 Evolve** | 🧬 진화 중 (V3) | 진화 진행 표시 (Builder View) | 거버넌스 승인 | `sdar.repair.started` |

> **에러 상태**: 모든 상태에서 에러 발생 시 UI는 `GuardrailsAlert` + `PolicyBlockedCard`로 전환.
> SDAR 활성화 시(V2+) 자동 복구 진행 상태를 `NodeStatusBadge(ORANGE 점멸)`로 표시.

### EventTypeRegistry (D2.1-D2 SOT 123항목 + PART2 추가 cl.rt.* 11항목 = 총 134항목) <!-- D2.1-D2 v3.0 정본: oc.*33 + wf.*4 + ui.builder.*14 + ui.frontmini.*7 + ui.core.*7 + ui.gate.*9 + ui.node.*2 + ui.main.*12 + ui.tool.*6 + ui.memory.*5 + ui.cli.*10 + mem.*2 + storage.*5 + agent.*3 + sdar.*3 = 122~123. cl.rt.* 11개는 PART2 RT-BNP 추가분 -->

```
oc.request.received, oc.i1.parse.started, oc.i1.intent.parsed, ...
oc.i2.query.built, oc.i2.evidence.ready, ...
oc.i3.plan.created, oc.i3.commit.completed, ...
oc.i4.structuring.started, oc.i4.output.structured, ...
oc.i5.gates.evaluated, oc.i5.decision.locked, ...
oc.loop.retry.reasoning, oc.loop.retry.action, oc.deny.blocked, oc.done
wf.stage.enter, wf.stage.exit, wf.approval.requested
ui.builder.*, mem.reference.updated, mem.kb.derived
+ storage.* (BLOCKER-3에서 추가)
+ agent.*, sdar.* (CC-006에서 추가)
+ cl.rt.* (RT-BNP 실시간 뉴스 파이프라인, §6.10.1)
```

#### RT-BNP 이벤트 (cl.rt.* namespace, 11개)

```
cl.rt.source.connected        — RT 소스 WebSocket/RSS 연결 성공
cl.rt.source.disconnected     — RT 소스 연결 끊김
cl.rt.item.received           — 뉴스 아이템 수신
cl.rt.breaking.detected       — 속보 감지 (Breaking Detector 판정)
cl.rt.breaking.classified     — 속보 등급 분류 완료 (P0/P1/P2)
cl.rt.fast_gate.passed        — Fast Gate 통과
cl.rt.fast_gate.blocked       — Fast Gate 차단 (보안 필터)
cl.rt.event.dispatched        — VAMOS EventBus로 전파 완료
cl.rt.investing.triggered     — AI Investing 전략 트리거 발생
cl.rt.verification.completed  — 사후 정규 Gate 검증 완료
cl.rt.retraction.issued       — 허위 속보 철회 이벤트 발행
```

### FailureCodeRegistry (36 항목, D2.1-D2 SOT)

```
OC_I1_PARSE_FAIL, OC_I1_AMBIGUOUS_UNRESOLVED
OC_I2_RAG_NO_SOURCE, OC_I2_EVIDENCE_QOD_LOW, OC_I2_SOURCE_POLICY_BLOCK, OC_I2_TIMEOUT
OC_I3_MEMORY_POLICY_DENY, OC_I3_APPROVAL_REQUIRED, OC_I3_COMMIT_FAIL
OC_I4_OUTPUT_SPEC_VIOLATION, OC_I4_CITATION_MISSING, OC_I4_MASK_FAIL
OC_I5_POLICY_BLOCK, OC_I5_APPROVAL_REQUIRED, OC_I5_COST_OVER_BUDGET, OC_I5_EVIDENCE_INSUFFICIENT, OC_I5_ROUTE_NOT_FOUND
PII_LONGTERM_DENIED, POLICY_DENY, GT_ERR_COST_LIMIT, TOOL_TIMEOUT
FM_ERR_FMT, FM_ERR_SIZE, FM_ERR_PII, FM_ERR_ZERO
OC_ERR_NONGOAL, OC_ERR_P2_LOCK, OC_ERR_COST_LV, OC_ERR_COST_OV, OC_ERR_NO_ROUTE
TL_ERR_TIMEOUT, TL_ERR_403, TL_ERR_PARSE
MC_ERR_LOW_QOD, MC_ERR_CONFLICT, MC_ERR_STALE
```

### FallbackRegistry (23 항목, D2.1-D2 SOT)

```
FB_INTENT_HEURISTIC_PARSE, FB_ASK_CLARIFICATION
FB_RAG_RETRY_EXPAND, FB_RAG_SWITCH_SOURCE
FB_MEMORY_META_ONLY, FB_REQUIRE_APPROVAL
FB_OUTPUT_REFORMAT, FB_OUTPUT_MINIMAL
FB_POLICY_MASK, FB_COST_DOWNSHIFT
FB_ROUTE_SAFE_NODE, FB_RESTRICT_GENERAL_INFO, FB_DENY_WITH_REASON
FB_DENY_STORAGE, FB_REJECT_INPUT, FB_MASK_AND_CONFIRM
FB_REQ_REUPLOAD, FB_RETRY_SOFT, FB_USE_WEB_SEARCH
FB_RETURN_RAW, FB_AUTO_REPAIR, FB_SHOW_CONFLICT, FB_SHOW_STALE
```

### FailureCode → Fallback 매핑 (36:23 1:N, §6.9 정본)

> 각 FailureCode 발생 시 순서대로 Fallback을 시도. 첫 번째 성공 시 중단.

| FailureCode | 1차 Fallback | 2차 Fallback | 3차 Fallback |
|-------------|-------------|-------------|-------------|
| **Intent (I-1)** | | | |
| OC_I1_PARSE_FAIL | FB_INTENT_HEURISTIC_PARSE | FB_ASK_CLARIFICATION | — |
| OC_I1_AMBIGUOUS_UNRESOLVED | FB_ASK_CLARIFICATION | — | — |
| **Evidence (I-2)** | | | |
| OC_I2_RAG_NO_SOURCE | FB_RAG_RETRY_EXPAND | FB_RAG_SWITCH_SOURCE | FB_USE_WEB_SEARCH |
| OC_I2_EVIDENCE_QOD_LOW | FB_RAG_RETRY_EXPAND | FB_RAG_SWITCH_SOURCE | — |
| OC_I2_SOURCE_POLICY_BLOCK | FB_RAG_SWITCH_SOURCE | FB_RESTRICT_GENERAL_INFO | — |
| OC_I2_TIMEOUT | FB_RETRY_SOFT | — | — |
| **Memory (I-3)** | | | |
| OC_I3_MEMORY_POLICY_DENY | FB_MEMORY_META_ONLY | FB_DENY_STORAGE | — |
| OC_I3_APPROVAL_REQUIRED | FB_REQUIRE_APPROVAL | — | — |
| OC_I3_COMMIT_FAIL | FB_RETRY_SOFT | — | — |
| **Output (I-4)** | | | |
| OC_I4_OUTPUT_SPEC_VIOLATION | FB_OUTPUT_REFORMAT | FB_OUTPUT_MINIMAL | — |
| OC_I4_CITATION_MISSING | FB_OUTPUT_REFORMAT | — | — |
| OC_I4_MASK_FAIL | FB_MASK_AND_CONFIRM | FB_OUTPUT_MINIMAL | — |
| **Decision (I-5)** | | | |
| OC_I5_POLICY_BLOCK | FB_POLICY_MASK | FB_DENY_WITH_REASON | — |
| OC_I5_APPROVAL_REQUIRED | FB_REQUIRE_APPROVAL | — | — |
| OC_I5_COST_OVER_BUDGET | FB_COST_DOWNSHIFT | — | — |
| OC_I5_EVIDENCE_INSUFFICIENT | FB_RAG_RETRY_EXPAND | FB_ASK_CLARIFICATION | — |
| OC_I5_ROUTE_NOT_FOUND | FB_ROUTE_SAFE_NODE | — | — |
| **General** | | | |
| PII_LONGTERM_DENIED | FB_DENY_STORAGE | FB_MASK_AND_CONFIRM | — |
| POLICY_DENY | FB_DENY_WITH_REASON | — | — |
| GT_ERR_COST_LIMIT | FB_COST_DOWNSHIFT | — | — |
| TOOL_TIMEOUT | FB_RETRY_SOFT | — | — |
| **Format (FM)** | | | |
| FM_ERR_FMT | FB_OUTPUT_REFORMAT | — | — |
| FM_ERR_SIZE | FB_OUTPUT_MINIMAL | — | — |
| FM_ERR_PII | FB_MASK_AND_CONFIRM | FB_OUTPUT_MINIMAL | — |
| FM_ERR_ZERO | FB_RETURN_RAW | — | — |
| **OC Errors** | | | |
| OC_ERR_NONGOAL | FB_DENY_WITH_REASON | — | — |
| OC_ERR_P2_LOCK | FB_REQUIRE_APPROVAL | — | — |
| OC_ERR_COST_LV | FB_COST_DOWNSHIFT | — | — |
| OC_ERR_COST_OV | FB_COST_DOWNSHIFT | FB_DENY_WITH_REASON | — |
| OC_ERR_NO_ROUTE | FB_ROUTE_SAFE_NODE | — | — |
| **Tool (TL)** | | | |
| TL_ERR_TIMEOUT | FB_RETRY_SOFT | — | — |
| TL_ERR_403 | FB_REJECT_INPUT | FB_DENY_WITH_REASON | — |
| TL_ERR_PARSE | FB_AUTO_REPAIR | FB_RETURN_RAW | — |
| **Memory Check (MC)** | | | |
| MC_ERR_LOW_QOD | FB_RAG_RETRY_EXPAND | FB_SHOW_STALE | — |
| MC_ERR_CONFLICT | FB_SHOW_CONFLICT | FB_ASK_CLARIFICATION | — |
| MC_ERR_STALE | FB_SHOW_STALE | FB_REQ_REUPLOAD | — |

> **Fallback 커버리지**: 23개 FB 전건 매핑 완료. 1:N 관계로 하나의 FB가 복수 FC에서 사용됨.
> **NEVER_AUTO 적용**: OC_I5_POLICY_BLOCK, POLICY_DENY, PII_LONGTERM_DENIED → Fallback 후에도 자동 실행 금지, 반드시 HITL 승인 필요.

### NEVER_AUTO 에러 자동 탐지 메커니즘

> NEVER_AUTO 정책 위반(자동 실행이 금지된 작업의 무단 자동 처리)을 **실시간 탐지**하는 메커니즘입니다.

| # | 탐지 규칙 | 탐지 방법 | 대응 액션 |
|---|----------|----------|----------|
| 1 | **P1+ 자동승인 감지** | ApprovalGate 로그에서 P1/P2 작업이 사용자 승인 없이 통과 시 | 즉시 파이프라인 중단 + P0 인시던트 발행 + 실행 결과 롤백 |
| 2 | **POLICY_DENY 우회 감지** | PolicyGate에서 DENY 판정 후 후속 노드가 실행된 경우 | 실행 결과 폐기 + audit_log 기록 + 관리자 알림 |
| 3 | **PII 무단 저장 감지** | 메모리 커밋 이벤트에서 PII 마스킹 없이 저장된 경우 | 즉시 삭제 + 사용자 알림 + GDPR 위반 보고서 생성 |
| 4 | **Gate 순서 스킵 감지** | 5-Gate 실행 로그에서 순서(Policy→Approval→Cost→Evidence→SelfCheck) 위반 | 파이프라인 중단 + 전 Gate 재실행 요구 |
| 5 | **600초 타임아웃 우회** | S3a 승인 대기에서 타임아웃 전 시스템 자동 승인 시도 | 승인 거부 + 타임아웃 대기 강제 |

```python
# NEVER_AUTO 탐지기 (V1+)
class NeverAutoDetector:
    NEVER_AUTO_CODES = {"OC_I5_POLICY_BLOCK", "POLICY_DENY", "PII_LONGTERM_DENIED"}

    def check_approval_bypass(self, event: PipelineEvent) -> bool:
        """P1+ 작업의 자동승인 우회 탐지"""
        if event.priority >= Priority.P1 and event.approval_type == "auto":
            self.raise_incident(severity="P0", reason="NEVER_AUTO_VIOLATION")
            return True
        return False
```

### V2/V3 추가 모듈 FailureCode 확장

> 기존 36건 FailureCode는 CORE 32개 모듈 중심. V2 COND 116개 + V3 EXP 모듈에 대한 추가 FailureCode입니다.

| FailureCode | 대상 모듈 | 설명 | 버전 | 1차 Fallback |
|-------------|----------|------|------|-------------|
| COND_MODULE_INIT_FAIL | COND 전체 | COND 모듈 초기화 실패 (의존성 미충족) | V2 | FB_SKIP_COND (CORE만으로 계속) |
| COND_BATCH_TIMEOUT | CAT-A~G 배치 | 배치 처리 타임아웃 (batch_size 초과) | V2 | FB_REDUCE_BATCH (batch_size 절반) |
| COND_DEPENDENCY_CONFLICT | COND 상호 의존 | COND 모듈 간 순환 의존 감지 | V2 | FB_ISOLATE_MODULE (충돌 모듈 비활성화) |
| RAG_QDRANT_CONNECTION | I-2 RAG (V2) | Qdrant 벡터 DB 연결 실패 | V2 | FB_RAG_FALLBACK_CHROMA (로컬 Chroma) |
| SDAR_REPAIR_FAIL | SDAR AR-L3+ | 자동 수리 실패 (3회 재시도 소진) | V2 | FB_SDAR_ESCALATE (인간 에스컬레이션) |
| SDAR_SNAPSHOT_CORRUPT | SDAR 스냅샷 | 수리 전 스냅샷 무결성 검증 실패 | V2 | FB_SDAR_ABORT (수리 중단 + 수동 복구) |
| LLAMAGUARD_GPU_UNAVAIL | LlamaGuard (V2) | GPU 사용 불가 | V2 | FB_GUARD_CPU_FALLBACK (INT4 모델) |
| LLAMAGUARD_CLASSIFY_FAIL | LlamaGuard | 안전성 분류 타임아웃/오류 | V2 | FB_GUARD_BLOCK_DEFAULT (안전하지 않음 기본) |
| EXP_SELF_EVO_REGRESSION | Self-evo (V3) | 자가 개선 후 성능 회귀 감지 | V3 | FB_EVO_ROLLBACK (이전 버전 복원) |
| EXP_AGENT_SPAWN_LIMIT | Agent Mesh (V3) | 에이전트 스폰 한도 초과 (50+) | V3 | FB_AGENT_QUEUE (대기열 처리) |
| EXP_GPU_OOM | vLLM 서빙 (V3) | GPU 메모리 초과 | V3 | FB_GPU_OFFLOAD (CPU 오프로드) |
| EXP_A2A_AUTH_FAIL | A2A 프로토콜 (V3) | mTLS/JWT 인증 실패 | V3 | FB_A2A_RETRY (인증 재시도 3회) |

> **확장 원칙**: V2 COND FailureCode는 `COND_` 접두어, V3 EXP는 `EXP_` 접두어. 기존 36건 + V2 8건 + V3 4건 = **총 48건**.
> 각 FailureCode는 FallbackRegistry에 1:N 매핑되며, 기존 23건 FB + 신규 12건 FB = **총 35건** Fallback.

---

## 6.12 운영 (버전별 전략)

### 6.12.1 모니터링 전략

| 버전 | 모니터링 방식 | 주요 메트릭 | 도구 |
|------|------------|-----------|------|
| V0 | JSONL 로그 + 콘솔 출력 | 파이프라인 성공률, 응답 시간, 에러율 | 수동 tail/grep |
| V1 | structlog JSON + SQLite 메트릭 테이블 | 32모듈 상태, Gate 통과율, 비용 추적, 메모리 사용량 | 로컬 대시보드 (React) |
| V2 | Docker 로그 드라이버 + PostgreSQL 메트릭 | COND 모듈 활성화율, SDAR 해결율, API 레이턴시 P95/P99 | Grafana (Docker) |
| V3 | Loki + Grafana + Prometheus | 전 모듈 분산 추적, K8s 리소스, GPU 활용률, Self-evo 성능 | Observability 스택 |

### 6.12.1.5 Hetzner Lite 리소스 관리 전략 (V3) <!-- v26 메이커에반 개선안 7 -->

> Hetzner CX31 (2vCPU / 8GB / 80GB)에서 다중 모듈을 동시 운영할 때의 리소스 분배 및 관리 전략입니다.

#### 리소스 분배 가이드라인

| 리소스 | 총량 | ORANGE CORE | AI Investing | BLUE NODE (Trading) | 시스템/예비 |
|--------|------|-------------|-------------|-------------------|-----------|
| **CPU** | 2vCPU | 0.5 | 0.3 | 0.3 | 0.9 |
| **메모리** | 6Gi (8GB - Swap 2GB) | 1.5Gi | 1.5Gi | 1Gi | 2Gi (DB+Redis+OS) |
| **디스크 (80GB 총)** | 80GB | 10GB (core 스키마) | 10GB (investing 스키마) | 5GB (trading 스키마) | 55GB (로그/캐시/Swap/OS) |
| **Redis** | 512MB | DB0 (캐시 200MB) | DB2 (200MB) | DB1 (100MB) | DB3 (MessageBus) |

#### 운영 원칙

| # | 원칙 | 세부 |
|---|------|------|
| 1 | **메모리 부족 대응** | Swap 2GB 활성화 필수. OOM 위험 시 BLUE NODE 우선 정지 (ORANGE CORE 보호) |
| 2 | **CPU 부하 분산** | 고부하 배치 작업(백테스트/재임베딩)은 야간(UTC 02:00~06:00) cron 예약 |
| 3 | **디스크 관리** | 로그 로테이션 30일, 모델 캐시 주기적 정리, `docker system prune` 주 1회 |
| 4 | **월 1회 재시작** | 전체 Docker Compose 재시작으로 메모리 누수 정리 (계획된 유지보수 창) |
| 5 | **비용 알림** | Grafana에서 합계 $160 경고 / $190 심각 알림 설정 (예상 $123-142 대비 여유 확보, $200 LOCK 초과 방지) |

#### Hetzner Lite vs K8s 풀스펙 운영 비교

| 항목 | Hetzner Lite | K8s 풀스펙 |
|------|-------------|----------|
| 월 비용 | ~$123-142 | ~$500+ |
| 자동 스케일링 | 수동 (Docker restart) | HPA 자동 |
| 롤백 | `docker compose down && up` (2-3분) | Helm rollback (30초) |
| 가용성 | 단일 서버 (SLA 99.9%) | 멀티 노드 (SLA 99.95%+) |
| GPU | RunPod Serverless (on-demand) | 전용 GPU 노드 (24/7) |
| 적합 시나리오 | 개인 사용, $200 예산 | 팀/프로덕션, $500+ 예산 |

### 6.12.2 백업 및 복구 (RPO/RTO)

| 버전 | 데이터 | RPO | RTO | 백업 방식 |
|------|--------|-----|-----|----------|
| V0-V1 | SQLite + Chroma + JSONL | 1일 (커밋 주기) | 30분 (git restore) | git 커밋 + SQLite `.backup` 명령 (자동/수동) |
| V2 | PostgreSQL + Qdrant + Neo4j | 1시간 | 2시간 | pg_dump cron (6h), Qdrant snapshot API, Neo4j backup |
| V3 | 관리형 DB + PVC | 15분 | 30분 | RDS 자동 백업 + PVC 스냅샷 + Velero K8s 백업 |

### 6.12.3 인시던트 대응 프로세스

```
1. 탐지: 모니터링 알림 또는 사용자 보고
2. 분류: P0(서비스 불가)/P1(주요 기능 장애)/P2(부분 장애)/P3(성능 저하)
3. 대응:
   - P0: 즉시 롤백 + 원인 분석 (목표: 15분 내 복구)
   - P1: Fallback 활성화 + 원인 분석 (목표: 1시간 내 복구)
   - P2: 다음 배포에 수정 포함 (목표: 24시간)
   - P3: 백로그 등록
4. 사후: 포스트모템 작성 (P0/P1 필수), 재발 방지 조치 구현
```

### 6.12.4 알림 체계

| 채널 | 대상 | 조건 | 버전 |
|------|------|------|------|
| 콘솔 로그 | 개발자 | 모든 에러 레벨 | V0+ |
| 로컬 알림 (Tauri notification) | 사용자 | 비용 70%/85%/95% 도달, P0/P1 에러 | V1+ |
| Webhook (Discord/Slack) | 운영팀 | P0/P1 인시던트, 배포 실패, 비용 초과 | V2+ |
| PagerDuty/OpsGenie | 온콜 | P0 서비스 불가 | V3+ |

### 6.12.5 롤백 프로세스

| 버전 | 롤백 방식 | 소요 시간 | 자동화 |
|------|----------|----------|--------|
| V0-V1 | git revert + 재빌드 | 5-10분 | 수동 |
| V2 | Docker Compose 이전 이미지 태그로 재배포 | 2-3분 | CI/CD 트리거 |
| V3 | K8s Blue-Green 스위치백 | 30초 | Helm rollback 자동 |

### 6.12.6 헬스체크

| 버전 | 대상 | 방식 | 주기 | 실패 시 |
|------|------|------|------|---------|
| V0-V1 | Python 프로세스 | `/health` HTTP 엔드포인트 (200 OK) | 30초 | 프로세스 재시작 |
| V2 | Docker 컨테이너 | `HEALTHCHECK CMD curl -f http://localhost:8000/health` | 15초 | Docker restart policy |
| V3 | K8s Pod | `livenessProbe` + `readinessProbe` (HTTP/TCP) | 10초 | Pod 재시작 + 자동 스케줄링 |

### 6.12.7 로그 보존 정책

| 버전 | 로그 유형 | 보존 기간 | 저장소 |
|------|----------|----------|--------|
| V0-V1 | JSONL 파일 | 90일 (로컬) | `data/logs/` 디렉토리, logrotate |
| V2 | Docker 로그 + PostgreSQL audit | 180일 | Docker log driver(json-file, max-size=50m, max-file=5) |
| V3 | Loki 인덱스 | 365일 | Loki retention policy, S3/MinIO cold storage |

### 6.12.8 비용 초과 대응

```
1. 경고(70%): 대시보드 노란색 표시, 로그 경고
2. 주의(85%): Webhook 알림 발송, 비용 높은 모듈 자동 throttle
3. 위험(95%): 사용자 알림 + P2 이상 요청 일시 정지 대기
4. 초과(100%): 모든 유료 API 호출 차단, P0/P1만 Ollama 로컬로 전환
5. 월 초 자동 리셋: daily_limit 기준 일일 배분 (LOCK)
```

### 6.12.9 SDAR 수동 폴백

> SDAR 자동 수리 실패 시 또는 SDAR OFF 환경에서의 수동 대응 절차.

| AR 레벨 | 수동 폴백 | 절차 |
|---------|----------|------|
| AR-L1 (LOW) | 수동 재시작 | `systemctl restart vamos` 또는 Docker restart |
| AR-L2 (MEDIUM) | 수동 config 수정 | 문제 config 키 확인 → toml 수정 → 재시작 |
| AR-L3 (MEDIUM+) | 수동 롤백 | git revert 또는 Docker 이전 이미지로 전환 |
| AR-L4 (HIGH) | DBA/DevOps 개입 | 스키마 수동 마이그레이션 + 데이터 무결성 검증 |

### 6.12.10 RT-BNP 소스 장애 대응

| 장애 유형 | 탐지 | 대응 | 복구 |
|----------|------|------|------|
| RSS 소스 타임아웃 | 3회 연속 실패 | Circuit Breaker open → 해당 소스 비활성화 | half_open 60초 후 재시도 |
| WebSocket 끊김 (V3) | heartbeat 실패 | 자동 재연결 (최대 5회, 지수 백오프) | 5회 실패 시 RSS 폴백 전환 |
| 전체 소스 다운 | 활성 소스 0개 | 캐시된 마지막 데이터 제공 + 알림 | 수동 소스 목록 갱신 |

### 6.12.11 Cloud Library 페일오버

| 구성요소 | 주 경로 | 페일오버 | RTO |
|---------|--------|---------|-----|
| Vector DB (Chroma/Qdrant) | 로컬/Docker 인스턴스 | SQLite FTS5 기반 키워드 검색 폴백 | 즉시 |
| LLM API (GPT-4o) | 직접 API 호출 | Ollama 로컬 모델 전환 | ~10초 |
| Redis (V2+) | Docker Redis | 인메모리 dict 캐시 폴백 | 즉시 |
| PostgreSQL (V2+) | Docker 인스턴스 | SQLite 임시 전환 (읽기 전용) | ~30초 |
| K8s 클러스터 (V3) | 주 노드풀 | Spot→On-Demand 전환 + Pod 재스케줄링 | 2-5분 |

### 6.12.12 구현 중 결정 항목 <!-- v12_S1-1: 6.12.6→6.12.12 번호 중복 해소 v26 -->

> 아래 항목은 구현하면서 확정합니다. 실측 후 결정 권장.

| # | 항목 | 구현 시 결정 방향 | 근거 |
|---|------|-----------------|------|
| 1 | **로그 보관 기간** | V0-V1: 30일, V2: 90일, V3: 1년 | PHASE_B4 log_format=jsonl, 규정 준수 |
| 2 | **백업 주기** | V0-V1: git 커밋, V2: 6시간, V3: 자동 | RPO 기준 역산 |
| 3 | **DR(재해복구)** | V0-V1: 해당없음(로컬), V2: 리전 내, V3: 멀티 리전 | 비용 대비 가용성 |
| 4 | **헬스체크 주기** | V1: 60초, V2: 30초, V3: 15초 (liveness/readiness) | 장애 탐지 속도 |

---

## 6.13 전체 코딩 작업량 요약

| 영역 | V0 | V1 | V2 | V3 | 합계 |
|------|----|----|----|----|------|
| UI/UX | 0 | ~75 | ~40 | ~20 | **~135** |
| 인프라 (Rust IPC, Docker) | ~8 | ~80 | ~15 | ~5 | **~108** |
| 테스트 | ~15 | ~70 | ~30 | ~13 | **~128** |
| CI/CD | 0 | ~8 | ~4 | ~2 | **~14** |
| 도구 (스키마, Config) | ~10 | ~5 | ~4 | 0 | **~19** |
| 보안 | 0 | ~8 | ~5 | ~2 | **~15** |
| MCP | 0 | ~5 | ~2 | 0 | **~7** |
| 기타 (이벤트, Agent, LangGraph, RT-BNP, DCL, PARL) | ~8 | ~30 | ~17 | ~25 | **~80** | <!-- v22.0.0: V3 기타 ~17→~25 (+8 SP: PARL Agent Swarm +5, Agent Specialization +3) -->
| **합계** | **~41** | **~284** | **~292** | **~79** | **~696** | <!-- v25.0.0: 테스트 ~84→~128 (+44), V1 ~273→~281, V2 ~92→~117, V3 ~56→~67, 합계 ~462→~506 --> <!-- S7-260 v26 --> <!-- S7-261 v26 --> <!-- S7-262 v26 --> <!-- S7-263 v26 --> <!-- v12 Phase 3 S7: +190 신규 항목 반영 (V1 ~281→~284 +3, V2 ~117→~292 +175, V3 ~67→~79 +12, 합계 ~506→~696) -->

---

# 7. 최종 검토사항

> **GO/NO-GO vs Stage Gate 관계** (FIX-12, FIX-13):
> - **GO/NO-GO** (총 64건: V0=16, V1=22, V2=14, V3=12): 버전 간 진입 판단을 위한 **고수준 체크리스트**. 해당 버전의 모든 Stage Gate를 포함하되, 정책/아키텍처 결정 등 Stage Gate에 포함되지 않는 전제조건도 포함. <!-- v22 PARL Agent Swarm 항목 추가로 V3=12, 총 64 -->
> - **Stage Gate** (총 204건: V0=58, V1=66, V2=43, V3=37): 각 Stage(Phase) 내 **상세 검증 항목**. 구현 완료 후 다음 Stage 진입 전 통과해야 하는 기술적 검증.
> - **관계**: GO/NO-GO ⊃ Stage Gate 요약 + 정책 전제조건. GO/NO-GO 1건이 Stage Gate 다수건을 포괄하거나, Stage Gate에 없는 고유 항목(UNIQUE)일 수 있음.

---

## 7.1 V0 GO/NO-GO 체크리스트 (16항목, CLAUDE.md §10 동기화)

> ※ BLOCKER 14건 문서 수정은 V0 진입 전 별도 완료 필수 (PART1 §E.2 참조)

| # | 항목 | 근거 | 상태 |
|---|------|------|------|
| 1 | 통신 계층: Python 백엔드 확정 | V0-004 | [ ] |
| 2 | IMPLEMENTATION 계층 = PHASE_B 명시 | V0-002 | [ ] |
| 3 | V0 비용 엔진 = V1 한도(₩40,000) 사전 설정 (V0 실제 지출 ₩0 — 로컬 전용, 0-0 규칙서 §1.5 정본) | V0-001 | [ ] |
| 4 | 디렉토리 구조: PHASE_B2 정본 명시 + monorepo 생성 | V0-003 | [ ] |
| 5 | config 포맷: config.toml 통일 | V0-005 | [ ] |
| 6 | D2.1 스키마 v3.0.0 통일 승격 | CC-001 | [ ] |
| 7 | PLAN-2.0 "(대체됨)" 표기 | CC-010 | [ ] |
| 8 | BASE-1.3 전 24개 규칙 코드 매핑 | RULE 1.3 | [ ] |
| 9 | 스캐폴딩 + 의존성 설치 (pip/npm/cargo) | PHASE_B2/B3 | [ ] |
| 10 | config.v1.toml LOCK 값 배치 | PHASE_B4 | [ ] |
| 11 | 25개 스키마 코드 생성 (Pydantic v2/Zod/serde, V0 서브셋 — D2.1 전체 42개 중) | PART2 V0 STEP-1 | [ ] |
| 12 | I-1~I-3, I-5, I-19 스켈레톤 생성 (5개, I-4 제외) | READINESS §2.7 | [ ] |
| 13 | L0 세션 메모리 최소 구현 | D2.0-06 §2.1 | [ ] |
| 14 | 비용 엔진 ₩40,000/월 하드코딩 (V1 한도 사전 설정 — V0 지출 상한 아님, V0 실제 지출 ₩0 — 0-0 규칙서 §1.5 정본) | ABSOLUTE LOCK | [ ] |
| 15 | Guardrails L1+L2 설정 | PHASE_B4 | [ ] |
| 16 | Ollama + Chroma + SQLite 초기화 | PHASE_B4 | [ ] |

## 7.2 V1 GO/NO-GO 체크리스트 (22항목, V0 완료 전제, CLAUDE.md §10 동기화)

| # | 항목 | 근거 | 상태 |
|---|------|------|------|
| 1 | I-Series 25개 모듈 정본 확정 | V1-001, V1-016 | [ ] |
| 2 | E-15, S-5 명칭 겸용 처리 | V1-002, V1-003 | [ ] |
| 3 | 38개 DEFER/TBD V1 차단 0건 확인 | V1-008 | [ ] |
| 4 | datetime.utcnow() 전수 교체 | V1-005 | [ ] |
| 5 | approval_status enum 통일 (D2.1-D7 SOT=2개: approved/denied, DN-014 반영) | V1-004 | [ ] | <!-- SOURCE_CONFLICT: CLAUDE.md=4개(+pending+expired) vs D2.1-D7 DN-014=2개(approved/denied). D2.1-D7 SOT 채택. 4값은 ApprovalSchema.status 용도 -->
| 6 | QoD 5요소 공식 통일 | V1-006 | [ ] |
| 7 | Front Mini LLM = I-1 내부 명시 | V1-007 | [ ] |
| 8 | Guardrails 4-Layer 명시 (V1=L1+L2 활성, L3+L4=V2+) | V1-010 | [ ] |
| 9 | 비용 상한 ₩40,000 통일 | V1-013 | [ ] |
| 10 | React 18.3 통일 | V1-014 | [ ] |
| 11 | LangChain Allowlist 명시 | V1-009 | [ ] |
| 12 | V1 CRITICAL 보안항목 15개(S7E 14 + DEC-003 1) 구현 완료 | READINESS_REVIEW §9, §6.5 | [ ] |
| 13 | 테스트 인프라 구축 (Python 80%+, Rust 80%+, React 80%+) | PHASE_B5 | [ ] |
| 14 | CI/CD 설정 완료 (GitHub Actions 8-stage) | PHASE_B6 | [ ] |
| 15 | 스토리지 스택 구축 (SQLite+Chroma+JSONL+Graph) | D2.0-06 | [ ] |
| 16 | EventTypeRegistry 통합 (agent.* + sdar.* 등록) | CC-006 | [ ] |
| 17 | Python/TS 스키마 동기화 도구 (Pydantic→Zod) | CC-007 | [ ] |
| 18 | BEGINNER_GUIDE 모듈 목록 갱신 | CC-002 | [ ] |
| 19 | B↔L 매핑표 추가 | CC-009 | [ ] |
| 20 | STEP7 항목 수 비고 추가 | CC-011 | [ ] |
| 21 | V0 GO 체크리스트 전수 통과 | §7.1 | [ ] |
| 22 | MCP Bridge/Server/Client 개별 검증 | V1-P6 gate #5~#7: Bridge 통신 + Server 20+ tools 노출 + Client 외부 연결 각각 확인 | [ ] | <!-- FIX-11: RE-D-001 대응. GT-2 V1-Phase 6에서 3개 개별 산출물로 구분됨 -->

### V1→V2 전환 조건 (CLAUDE.md §10 동기화)

```
QoD ≥ 0.85 (30일) / RAG 정확도 ≥ 60% / 메모리 승격/강등 오류율 < 1%
P0 테스트 100% / 비용 초과 없이 30일 / 사용자 승인
```

#### V1→V2 TC 측정 메커니즘

| TC 지표 | 측정 방법 | 도구 | 측정 주기 | 판정 기준 |
|---------|----------|------|----------|----------|
| **QoD ≥ 0.85** | Evidence Gate 출력의 QoD 점수 30일 이동평균 | `qod_tracker.py` → SQLite `metrics` 테이블 | 매 파이프라인 실행 시 | 30일 연속 평균 ≥ 0.85, 단일일 최저 ≥ 0.70 |
| **RAG 정확도 ≥ 60%** | 벤치마크 질문 세트(50건) 대비 정답률 측정. 정답 기준: 인용 출처 정확 + 내용 일치 | `rag_benchmark.py` + RAGAS 프레임워크 (faithfulness, relevancy) | 주 1회 자동 실행 (CI) | 50건 기준 정답 ≥ 30건 (60%), faithfulness ≥ 0.7 |
| **메모리 오류율 < 1%** | 승격(STM→LTM) 및 강등(LTM→archive) 이벤트 중 데이터 손실/불일치 건수 비율 | `memory_audit.py` → 해시 비교 (before/after) | 일 1회 배치 검증 | 오류 건수 / 총 이벤트 < 0.01, 연속 7일 충족 |
| **P0 테스트 100%** | §6.3 V0-V1 기본 테스트 (~85건) 전수 통과 | pytest + vitest + cargo test (CI pipeline) | 매 커밋 (CI) | 실패 0건, flaky 허용 최대 2회 재시도 |
| **비용 30일 무초과** | 일일 API 비용 집계 (Claude + Embedding + 외부 MCP) | Cost Gate 로그 → `cost_daily_report.py` | 일 1회 집계 | 30일 연속 일일 비용 ≤ ₩93,000/30 = ₩3,100, 월합 ≤ ₩93,000 |
| **사용자 승인** | 위 5개 TC 전수 통과 확인 후 명시적 승인 이벤트 | CLI `vamos approve v2-transition` 또는 UI 승인 버튼 | 1회성 (전환 시점) | 승인 이벤트 로그 기록 필수 |

## 7.3 V2 GO/NO-GO 체크리스트 (14항목, V1 완료 전제, CLAUDE.md §10 동기화) <!-- S7-266 v26 -->

> **v12 Phase 3 S7 참고**: V2 BLOCKER 7건(구현 누락/스펙 미비)이 +175 신규 항목 삽입으로 해소됨. 해당 항목: V2 모듈 연동 구체화, 테스트 커버리지 확장, DB 마이그레이션 보강 등.

| # | 항목 | 근거 | 상태 |
|---|------|------|------|
| 1 | V1→V2 전환 조건 6개 충족 | CLAUDE.md §10 | [ ] |
| 2 | Agent Teams FREEZE 해석 확정 | V2-003 | [ ] |
| 3 | STEP7 V2 CRITICAL ~190건 상세 스펙 보강 | V2-008 | [ ] |
| 4 | 10-Layer/Gate 접두어 변경 (CL-Layer/CL-Gate) | V2-001, CC-004 | [ ] |
| 5 | SQLite→PostgreSQL 마이그레이션 | V2-004 | [ ] |
| 6 | Chroma→Qdrant 재임베딩 | V2-005 | [ ] |
| 7 | NetworkX→Neo4j 변환 | V2-006 | [ ] |
| 8 | SDAR V2 COND 활성화 조건 확정 | V2-002 | [ ] |
| 9 | MessageBus 구현 결정 (Redis vs In-Memory) | DEFER-AT-001 | [ ] |
| 10 | HMAC 프로토콜 상세 완성 | CC-012 | [ ] |
| 11 | STEP7 모듈 연동 구체화 | CC-005 | [ ] |
| 12 | V2 인프라 10개 컴포넌트 구축 (Docker Compose 배포) | PHASE_B6 §5 | [ ] |
| 13 | V2 비용 모니터링 대시보드 (₩93,000 이내) | ABSOLUTE LOCK | [ ] |
| 14 | QoD 가중치 이중 체계 구분 명시 | CC-003 | [ ] |

### V2→V3 전환 조건 (CLAUDE.md §10 동기화)

```
QoD ≥ 0.90 (60일) / 2-tier LLM 최적화 완료 / P1 고급 테스트 통과
Self-evo 체계 검증 / V3 비용 재검토 + 승인
```

#### V2→V3 TC 측정 메커니즘

| TC 지표 | 측정 방법 | 도구 | 측정 주기 | 판정 기준 |
|---------|----------|------|----------|----------|
| **QoD ≥ 0.90 (60일)** | Evidence Gate QoD 점수 60일 이동평균 | `qod_tracker.py` (V1→V2와 동일 도구, 임계값 상향) | 매 파이프라인 실행 시 | 60일 연속 평균 ≥ 0.90, 단일일 최저 ≥ 0.80 |
| **2-tier LLM 최적화** | 주 모델(Claude) + 보조 모델(로컬 vLLM) 라우팅 비율 및 품질 비교. 보조 모델이 단순 작업(P0) 처리 시 품질 저하 < 5% | `llm_router_benchmark.py` — A/B 비교 100건 | 주 1회 벤치마크 | 보조 모델 P0 정답률 ≥ 95%, 라우팅 비용 절감 ≥ 30% |
| **P1 고급 테스트** | V3 전용 테스트 세트: 멀티스텝 추론(5+턴), 코드 생성+실행, RAG+메모리 통합 시나리오 | `p1_advanced_test_suite.py` — 30건 시나리오 | 주 1회 (CI) | 30건 중 ≥ 24건 통과 (80%), 회귀 0건 |
| **Self-evo 체계 검증** | 프롬프트 자가 개선 루프: 개선 전/후 성능 비교, 롤백 정상 동작, 거버넌스 규칙 준수 확인 | `self_evo_validator.py` + 감사 로그 분석 | 개선 사이클마다 (자동) | 개선 후 성능 ≥ 개선 전, 금지 규칙 위반 0건, 롤백 성공률 100% |
| **V3 비용 재검토** | Hetzner(기본) + RunPod GPU 실제 60일 운영 비용 집계. 예상 대비 ±10% 이내 확인 | `cost_v3_report.py` → 인프라별 비용 분리 집계 | 일 1회 집계 | 월합 ≤ ₩266,000 (ABSOLUTE LOCK), 60일 연속 준수 |
| **사용자 승인** | 위 5개 TC + V3 GO/NO-GO 12항목 전수 통과 후 명시적 승인 | CLI `vamos approve v3-transition` | 1회성 | 승인 이벤트 + 전체 TC 스냅샷 기록 |

## 7.4 V3 GO/NO-GO 체크리스트 (12항목, V2 완료 전제, CLAUDE.md §10 동기화) <!-- S7-267 v26 -->

> **v12 Phase 3 S7 참고**: V3 MISSING 12건이 +12 신규 항목 삽입으로 해소됨. 해당 항목: PARL Agent Swarm 상세, K8s 배포 스펙, Self-evo 거버넌스, GraphRAG 벤치마크 등.

| # | 항목 | 근거 | 상태 |
|---|------|------|------|
| 1 | V2→V3 전환 조건 충족 | CLAUDE.md §10 | [ ] |
| 2 | K8s 배포 명세 상세 완성 | V3-001 | [ ] |
| 3 | S-8 Self-evo 거버넌스 상세화 | V3-002 | [ ] |
| 4 | V3 비용 상한 재산정 + 승인 | V3-003 | [ ] |
| 5 | GraphRAG 벤치마크 정의 | V3-004 | [ ] |
| 6 | SDAR V3 ON 조건 충족 (AR-L4, 수리성공률≥95%, 스냅샷복원100%) | SDAR SPEC | [ ] |
| 7 | STEP7 TITLE_ONLY ~317건 상세 보강 | V2-008 확장 | [ ] |
| 8 | 에이전트 50+ 병렬 인프라 구축 | LOCK-AT-014 | [ ] |
| 9 | A2A 프로토콜 설계 | DEFER-AT-005 | [ ] |
| 10 | Federated Agent 승인 체계 | DEFER-AT-004 | [ ] |
| 11 | Agent Marketplace 기준 확정 | DEFER-AT-003 | [ ] |
| 12 | PARL Agent Swarm 병렬 실행 안정성 | PATCH-B01, D2.0-05 §12.17.1 | [ ] | <!-- v22.0.0 추가 -->

> **참고**: PART2 GO/NO-GO 합계 64건(V0=16, V1=22, V2=14, V3=12). READINESS_GUIDE 62건과 2건 차이는 v22 PARL 추가분(§7.4 #12, §7.3 #14). 양쪽 수치 모두 정확하며, READINESS_GUIDE는 v22 이전 기준. <!-- v12_S1-4: Pattern A 잔여 확인 메모 v26 -->

---

## 7.5 크로스컷 검토 항목

### 7.5.1 문서 정합성

| 검증 항목 | 방법 |
|----------|------|
| I-모듈 번호 일관성 | PLAN 3.0 ↔ DESIGN 2.0 ↔ CLAUDE.md 크로스체크 (BLOCKER-1/12) |
| E-모듈 역할 일관성 | D2.0-01/03 정본 ↔ CLAUDE.md ↔ PLAN 3.0 (HIGH PL-01) |
| B/C/D-Series 존재 확인 | CLAUDE.md에 81개 모듈 전체 카탈로그 (BLOCKER-9) |
| 스키마 버전 통일 | D1~D8 전체 v3.0.0 확인 (BLOCKER-8) |
| LOCK 값 코드 반영 | config.v1.toml vs 문서 LOCK 값 대조 (B4-01/02 포함) |
| RBAC 역할 통일 | 코드 RBAC = OWNER/ADMIN/OPERATOR/VIEWER (BLOCKER-10) |
| 비용 임계값 단일화 | config.toml warn=80%, block=100% 유일 SOT (BLOCKER-11) |
| Gate 우회 불가 | 코드에서 Gate bypass 검색 |
| SDAR NEVER_AUTO 완전성 | 10항목 전체 코드 반영 (HIGH CM-01) |

### 7.5.2 보안 검토

| 검증 항목 | 기준 |
|----------|------|
| PII 마스킹 동작 | 주민번호/전화번호/이메일/카드번호 탐지율 99%+ |
| Non-goal 차단 | Non-goal 목록 100% deny 확인 |
| P2 자동 OFF | 세션 종료 시 즉시 비활성 확인 |
| 비용 상한 준수 | 80% 경고 / 100% 차단 동작 확인 |
| Docker 샌드박스 | 네트워크 격리, 30초 타임아웃 확인 |

### 7.5.3 성능 검토

| 지표 | 목표 |
|------|------|
| Simple response (mini) | start <= 2초 |
| Complex response (main+tool) | <= 10초 |
| Self-check | <= 1초 |
| 동시 처리 | BLUE_NODES=3 / TOOLS=5 concurrent | <!-- Phase 2-A FIX-11: Agent 8 M5 정정. BLUE_NODES(MAX_CONCURRENT_BLUE_NODES=3)와 TOOLS(5)는 별도 메트릭. CLAUDE.md §7.2 정본 -->
| Token counting | <= 50ms / 10K tokens |

### 7.5.4 정본 우선순위 준수

```
검증 순서:
1. RULE 1.3 — 절대 불변 (Identity, Non-goal, Safety, Cost, Self-evo)
2. PLAN 3.0 — 전략 레벨 결정
3. DESIGN 2.0 LOCK — 설계 레벨 확정
4. DESIGN 본문 — 상세 설계
5. 스키마/TECH_STACK — 구현 레벨
```

### 7.5.5 LOCK 값 검증 체크리스트

> 구현 완료 후 모든 LOCK 값이 코드에 정확히 반영되었는지 검증합니다.

| # | LOCK 항목 | 기대 값 | 검증 위치 | 버전 |
|---|----------|---------|----------|------|
| 1 | cost.monthly_limit | V1=40000, V2=93000, V3=266000 | config.v{N}.toml `[cost]` | V0+ |
| 2 | 5-Gate 순서 | Policy→Approval→Cost→Evidence→SelfCheck | pipeline.py Gate 노드 순서 | V1+ |
| 3 | 9-State 전이 순서 | S0→S1→...→S8 (변경 불가) | pipeline.py StateGraph edges | V0+ |
| 4 | embedding.dimension | 1024 | config `[embedding]` | V1+ |
| 5 | semantic_cache.threshold | cosine ≥ 0.95 | config `[semantic_cache]` | V1+ |
| 6 | approval.timeout_s | 600 (10분) | config `[approval]` | V1+ |
| 7 | circuit_breaker.recovery_time_sec | 60 | config `[circuit_breaker]` | V1+ |
| 8 | self_check 임계값 | P0≥70, P1≥75, P2≥80 | config `[self_check]` | V1+ |
| 9 | B↔L 매핑 | B-1→L1, B-2→L3, B-3→L2, B-4→L0 | memory 모듈 매핑 코드 | V1+ |
| 10 | NEVER_AUTO 정책 | P1+ 자동승인 금지 | ApprovalGate 코드 | V1+ |

### 7.5.6 SOURCE_CONFLICT 전수 인덱스 (M-23)

> 본 문서에 포함된 모든 SOURCE_CONFLICT 및 RESOLVED 주석의 전수 목록입니다.
> 구현 시 충돌이 의심되면 아래 인덱스에서 해결 근거를 확인하세요.

| # | 위치 (섹션) | 충돌 내용 | 채택 결정 | 근거 |
|---|-----------|----------|----------|------|
| SC-01 | §2 V0 활성 모듈 | §2.8=6개(I-1~I-5+I-19) vs §2.7=5개(I-4 미포함) | 5개 | §2.7 상세 테이블이 더 구체적 |
| SC-02 | §config L2 TTL | B4="indefinite" vs BASE-1.3="영구" | "indefinite" | 동일 의미, B4 리터럴 채택 |
| SC-03 | §config semantic_cache TTL | B4="3600" vs D2.0-06="86400" | 86400 | DESIGN 2.0 > PHASE_B 원칙 |
| SC-04 | §STEP-5 메모리 계층 | D2.0-06=4계층(L0~L3) vs S7D=5계층(+L4) | 4계층 LOCK | L4 Archive는 V2+ 확장 |
| SC-05 | V1-Phase 2 B-3 | §5.10="Memory Decay" vs §8.4="Deep Reflection" | §5.10 LOCK | §8.4는 DEPRECATE 레거시 |
| SC-06 | §6.3.1 Circuit Breaker | D2.1-D5/D7=300s vs D2.0-05 §4.4=60s | 60s LOCK | DESIGN 2.0 LOCK > Schema |
| SC-07 | §UI Hooks/Stores 출처 | 기존="D2.0-08" vs 실제=CLAUDE.md §14/PHASE_B2 | CLAUDE.md §14 | 출처 정정 |
| SC-08 | §6.9 I-25 명칭 | D2.0-01="Self-Directed Agent Runtime" vs SDAR_SPEC="Self-Diagnosis and Auto-Repair" | SDAR_SPEC | 전문 LOCK 채택 |
| SC-09 | §6.7 협업 패턴 | §5=5개 vs §7.1 enum=6개(HYBRID 포함) | 6개 | §7.1 enum(코드 생성 기준) |
| SC-10 | §6.2.1 IPC 핸들러 수 | B1 §5.1=47개 vs CLAUDE.md/B1 changelog=72개 | 72개 | CLAUDE.md 정본 |
| SC-11 | §approval_status enum | CLAUDE.md=4개 vs D2.1-D7 DN-014=2개 | 2개 | D2.1-D7 SOT 채택 |
| SC-12 | §L0 TTL | 기존 30일 vs CLAUDE.md §15="7일(최대30일)" | 7일(최대30일) | RESOLVED |

| SC-13 | §6.10 G1 Gate명 | PART2="Trust Score" vs CLOUD_LIBRARY_SPEC §8="Content Quality" | Content Quality | SOT(SPEC §8) 채택, FIX-09로 해소 |
| SC-14 | §6.10 G2 Gate명 | PART2="Relevance" vs CLOUD_LIBRARY_SPEC §8="Consistency" | Consistency | SOT(SPEC §8) 채택, FIX-09로 해소 |
| SC-15 | §config Guardrails Layer 수 | PART2 기존 "V2+=4-Layer" vs 실제 V2=3-Layer(L1+L2+L3), V3=4-Layer(+L4) | V2=3, V3=4 | B4 §3.16 정본, v10 수정 |

> **총 15건** SOURCE_CONFLICT 전수 해결 완료 (기존 12건 + v9 Phase 2에서 2건 + v10에서 1건 추가 해소). 모든 항목에 HTML 주석 `<!-- SOURCE_CONFLICT: ... -->` 또는 `<!-- RESOLVED: ... -->` 포함.

---

## 7.6 최종 산출물 파일 인덱스

> 구현 시 참조해야 할 43개 산출물 파일 전체 목록

| # | 파일명 | 주요 용도 | V0 필수 |
|---|--------|----------|---------|
| 1 | BASE-1.3_VAMOS_RULE_1.3_BASE.md | 절대 규칙 | ✓ |
| 2 | PLAN-3.0_VAMOS_PLAN_3_0_최종완성본.md | 전략/로드맵 | ✓ |
| 3 | D2.0-01_01. VAMOS_DESIGN_2_0_OVERVIEW.md | 아키텍처 허브 | ✓ |
| 4 | D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md | I-모듈 상세 | ✓ |
| 5 | D2.0-03_03. VAMOS_DESIGN_2.0_BLUE_NODES.md | E-모듈/MCP | ✓ |
| 6 | D2.0-04_04. VAMOS_DESIGN_2.0_INFRA_CORE.md | 인프라/도구 | 참조 |
| 7 | D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md | 워크플로우 | ✓ |
| 8 | D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md | 저장소/메모리 | ✓ |
| 9 | D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md | 안전/비용/승인 | ✓ |
| 10 | D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md | UI/UX | 참조 |
| 11 | D2.1-A1_A1_TECH_STACK.md | 기술 스택 | ✓ |
| 12-19 | D2.1-D1~D8 (8개) | 스키마 정의 | ✓ |
| 20 | D2.1-Q1_Q1_AUDIT_REPORT.md | 감사 보고서 | 참조 |
| 21-27 | PHASE_B1~B7 (7개) | 구현 명세 | ✓ |
| 28-32 | VAMOS_STEP7_* (5개) | 상세 명세 | 참조 |
| 33 | VAMOS_AGENT_TEAMS_SPEC.md | Agent Teams | V1 |
| 34 | VAMOS_AI_INVESTING_SPEC.md | AI 투자 | V1 |
| 35 | VAMOS_SDAR_DESIGN_SPECIFICATION.md | SDAR | V2 |
| 36 | VAMOS_CLOUD_LIBRARY_SPEC.md | Cloud Library | V2 |
| 37 | VAMOS_MASTER_SPECIFICATION.md | 마스터 스펙 | ✓ |
| 38 | CLAUDE.md | AI 코딩 지침 | ✓ |
| 39-43 | 기타 (Guide, Review 등) | 참조 | 참조 |

---

> **VAMOS AI 구현을 시작합니다.**
> V0-STEP-1부터 순서대로 진행하세요.
> 각 STEP 완료 시 체크리스트를 확인하고 다음 STEP으로 이동합니다.
> 막히는 부분이 있으면 산출물 파일을 직접 참조하거나 AI에게 해당 섹션을 읽도록 지시하세요.

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| v4.0.0 | 2026-02-24 | 3차 정밀 스캔 반영, 전체 구조 확립 |
| v5.0.0 | 2026-02-25 | 4차 검증 반영: frontend/→src/ 디렉토리 수정, V0 모듈목록 정정(9→5개), I-모듈 역할 D2.0-01 정본 통일, 3-Layer→4-Layer Guardrails 수정, NEVER_AUTO 10개 완전 명시, 항목 수 불일치 해소, V1 보안항목 검증 주석 |
| v6.0.0 | 2026-02-25 | 5차 검증 반영: §7 GO/NO-GO CLAUDE.md §10 완전 동기화 (V0: 8→16, V1: 15→21, V2: 9→14, V3: 8→11), V1→V2/V2→V3 전환 조건 추가, §6.5 GDPR 보안항목 추가, SF-02 보안항목 14개 확정(READINESS_REVIEW §9), 총 GO/NO-GO 62항목 완비 |
| v7.0.0 | 2026-02-25 | 6차 최종 검증 반영: §4 V2 추가 모듈 수 +8→+10 정정, §7.1 V0 GO/NO-GO CLAUDE.md §10 정확 동기화 (BLOCKER 행 분리→비고, Guardrails/Ollama 행 분리), 43개 산출물 전수 크로스체크 |
| v8.0.0 | 2026-02-25 | 80건 미검증 항목 분류 반영: §6.1.4 UI 구현 중 결정 4건 추가(화면 레이아웃/라우트/다크모드/애니메이션), §6.12 운영 결정 2건 추가(로그 보관 기간/백업 주기), §6.12→6.13 번호 조정 |
| v8.1.0 | 2026-02-25 | 3단계 독립 검증(Adversarial) 반영: READINESS_REVIEW §6.1→§9 참조 수정 2건, GDPR SF-54 출처 명확화(READINESS SF-54; D2.0-07 §15.4.2), Rust 커버리지 B5/B6 출처 충돌 주석 추가 |
| v8.2.0 | 2026-02-25 | 2차 3단계 독립 검증 반영: max_tokens 4096→2048(V1 기준 B4 §4.1), 마이그레이션 6원칙 B7 §1.2 원본 교체(3건 창작→정본), ResponseEnvelope 3→5필드+출처 CLAUDE.md §12, §6.5 ~13→14개, READINESS §6.1→§9 잔존 1건 수정, V0 모듈 SOURCE_CONFLICT 주석. FALSE_POSITIVE: IntentFrame 10필드(D2.0-02 §7 정확), 24개 Pydantic(V0 서브셋), V2 +10모듈(정확) |
| v8.3.0 | 2026-02-25 | 4종 교차 검증 반영: V2 +10→+8 모듈 정정(I-7·I-12 V1 기활성), Circuit Breaker 300→60s(D2.0-05 §4.4 LOCK, SOURCE_CONFLICT 주석), 보안항목 합계 ~13→~14(§6.5 동기화), 위임깊이 LOCK-AT-004 상한 주석 추가, I-21 "Source Evolution Engine" 정본명 명확화+BLOCKER-12 주석, §6.13 합계 ~433→~434 연쇄 정정 |
| v8.4.0 | 2026-02-25 | Check B 역방향 누락 17건 반영: §6.7 LOCK-AT 아키텍처 제약 17건 전수 테이블 추가(LOCK-AT-001~017, 신규 12건+기반영 5건), §6.9 SDAR LOCK 규칙 2→9건 확장+Self-evo 원칙+Emergency Kill Switch+CATEGORY E 특별 규칙+P2 수리 제한+비용 영향 제한, §6.5 DEC-003 도구 승인 Allowlist 추가(14→15개), §6.13 보안 ~14→~15 합계 ~434→~435 연쇄 정정 |
| v9.0.0 | 2026-02-26 | Phase 1 AI 의미검증(5 Agent) + Phase 1.5 적대적 재검증 반영 — REAL_ERROR 6건 수정: (1) §4 I-7·I-12 "V1 기활성"→"V2 COND"(D2.0-01 §5.6 정본: V1:OFF), +8→+10개 복원 (2) §1 V2 I-Series 20→22, 합계 40→42 연쇄 정정 (3) §5 V3 +41→+39 연쇄 (4) §2 DecisionSchema 16→18필드(D2.1-D2 §4.1 정본: 14 required+4 optional) (5) §6.1.1 CLI vamos policy 추가(D2.0-08 §2.3.1: 6개), 출처 "D2.0-08 §4"→§3/§2.1/§2.2/§2.3 정정 |
| v10.0.0 | 2026-02-26 | Phase 2 수정: Phase 1.5 REAL_ERROR 5건+Ripple 1건 — (1) rbac_default_role OPERATOR→OWNER (2) Guardrails config V2+=4→V2=3/V3=4 + SOURCE_CONFLICT 13건 주석(L0 TTL 30일→7일, approval_status 4→2개, Hooks/Stores 출처 정정, B-3 Decay 주석) + VALID MISSING 8건 보완(config 4섹션, B↔L 매핑, COND OFF 규칙, AI Investing 14-LOCK, Cloud Library G0-G4+13-LOCK) + Phase 0 전수 PASS |
| v11.0.0 | 2026-02-28 | Phase 2 최종 수정 (Phase 1.5 통합 55 REAL_ERROR + 20 SOURCE_CONFLICT): (1) Hooks 4/8 정본 교체(useStreaming→useMemory 등, PHASE_B2 §3.1) (2) Stores 2/7 정본 교체(agentStore→notificationStore 등) (3) 5→7 페이지(+Log/NodeDetail) (4) config timeout 30→10s, [cache]→[semantic_cache], [graph_db] 2→5키, +[vector_db]/[memory] 신설, 11→13섹션 (5) E-5 V2 배치 주석 (6) SDAR 7상태 SM+5-Gate 추가 (7) 6-Stage RAG+Hybrid Search+Cache 무효화 추가 (8) UI 9-state SM+Failure/Fallback+접근 제어 신설(§6.1.6~8) (9) VAL-001~010+AC 매핑 추가 (10) 10-Step Migration+사후검증 7항목 (11) AI Investing 14항목 전수 기재 (12) 협업 패턴 5→6(HYBRID) (13) SOURCE_CONFLICT 7건 신규 HTML 주석. Phase 0 전수 재실행 |
| v12.0.0 | 2026-03-01 | RT-BNP (Real-Time Breaking News Pipeline) 설계 추가: §6.10.1 RT-BNP 파이프라인(아키텍처/Tier 분류/Breaking Detector/Fast Gate/소스 가중치/버전별 범위/LOCK #14~18), §6.8.1 AI Investing 연동(VAMOS_EVENT breaking_news 타입/Circuit Breaker 속보 트리거/Event-Based 전략/P2 승인 흐름), §6.11 EventTypeRegistry cl.rt.* 11개 추가, V2-Phase 2/3·V3-Phase 2 구현항목 추가, §6.13 작업량 ~435→~448 갱신 |
| v12.1.0 | 2026-03-01 | Domain Context Layer(DCL) 선택적 배경 인식 설계 추가: §6.10.2 DCL 아키텍처(6계층 정보 환경/3개 도메인 채널/I-2 RAG 연동/품질 관리/버전별 범위), V1-Phase 2 DCL 기초 구현 항목, V2-Phase 2 DCL-GEO 항목, §6.13 작업량 ~448→~454 갱신 |
| v13.0.0 | 2026-03-03 | PART2 자체 전수검토 36건 반영: **CRITICAL 3건** — (1) 헤더 v11.0.0→v12.1.0 동기화 (2) backend/ 경로 전수 수정(PHASE_B2 §5.1 정본: backend/vamos_core/ 패키지 구조 반영, 디렉토리 트리+AI 프롬프트 22개소) (3) Gate 실행 순서 Policy→Cost→Evidence→Approval→Policy→Approval→Cost→Evidence(CLAUDE.md §7.2 정본). **HIGH 4건** — (1) I-11/I-10 순환 의존성 해소(순서 교체) (2) pytest ~40→~45, §6.13 테스트 ~84→~89/합계 ~454→~459 (3) CL-G3 Quality→Security 통일 (4) v9.0.0 changelog 17→18필드 정정. **MEDIUM 13건** — STEP-4 I-19/I-20 추가, I-3 STEP-5 매핑, I-19 스켈레톤 명확화, data/logs/ 디렉토리, config loader 의존성 주석, V0 체크리스트 +5항목, RBAC Phase 참조, DEC-003 주석, FallbackRegistry 13→14, AR-L0/L1 추가, 파일명 3건(CICD_SPEC→PIPELINE, TEST_SPEC→STRATEGY), Docker §5→§6.1, "5-Stage"→"5-Phase" 명칭 통일. **LOW 11건** — B-3 Decay 주석, E-5 범위, EventType 53+ 근거, FailureCode 20+ 근거, CL-G0 통일, I-1 S2 skip 주석, L0 TTL 7일, I-15 §7.19→§7.15, I-1~I-5→I-1~I-3+I-5+I-19, ttl_L3_archive→procedural, L2 TTL SC 주석. **KEEP 5건** — B7 §8→§2, §8.5→§2 도출, COND 8→10개, V2 4-Layer→3-Layer, V2-Phase3 사후감사 V3 이동 |
| v14.0.0 | 2026-03-03 | 43개 산출물 크로스체크 ~45건 반영: **GROUP A** (10건) — AI 프롬프트 디렉토리 트리 vamos_core/ 추가, PHASE_B7 섹션 참조 6건 정정(§2→§3.1/§3.2/§3.3/§3.4/§3.5, §2→§6, §2→§6.4), Integration ~13→~14, §6.13 테스트 ~89→~84/합계 ~459→~454 복원, D2.0-02 상태 머신 §12→§2.2 전수 정정(4개소), S2=NEEDS_CLARIFICATION→AMBIGUOUS. **GROUP B** (7건) — config.v1.toml 키 이름 B4 정본 통일: default_model→mini_model, ollama: → ollama/ 구분자, db_backend→backend, log_backend→log_format, vector_backend 제거, distance_metric→similarity_metric, collection_prefix→collection_name, ttl_L*→memory_ttl_L*, guardrails_layers 개별키 안내, invalidation_policy 제거, semantic_similarity→similarity_threshold, ttl_seconds→ttl_sec. **GROUP C** (5건) — D2.0-02 §7.{N} 축약 참조→정확한 순차 섹션 범위로 교체(I-1=§7.1~10, I-2=§7.11~20 등), 번호 체계 면책 주석 추가. **GROUP D** (6건) — pytest >=7.0→>=8.3.0, pytest-asyncio >=0.21→>=0.24.0, pytest-cov >=4.0→>=6.0.0, ruff >=0.1→>=0.8.0, line-length 120→100, select 5→13개 규칙(B6 정본). **GROUP E** (10건) — data/logs/ B2 미명시 주석, rpc/ B2 미명시 주석, 24 Pydantic V0 서브셋 주석, VamosConfig B4 섹션 차이 주석, CI 워크플로우 B6 통합구조 주석, SDAR ESCALATED 상태 주석, AI Investing 14-LOCK 재구성 주석, V1 보안항목 14→15개 정정, config V0 축약본 주석, §6.3 테스트 합계 ~84→~90 헤더 정정 |
| v15.0.0 | 2026-03-03 | 43개 소스 문서 전수 크로스체크 2차 (~15건 반영): **CRITICAL 1건** — UI State Machine 9개 상태명 전체 교체(D2.0-08 §4.1 정본: INIT→BOOT, INPUT_READY→EDITING, PROCESSING→READY, STREAMING→RUNNING, TOOL_EXECUTING→AWAIT_APPROVAL, HITL_PENDING→PRESENTING, ERROR→RECOVERY, SESSION_END→ARCHIVED + 설명/전이 동기화). **HIGH 5건** — (1) 6-Stage RAG Pipeline 스테이지명 교체(D2.0-06 §1.1 정본: QUERY_ANALYZE...VERIFY → Collect→Chunk→Embed→Store→Retrieve→Generate) (2) Semantic Cache TTL 3600→86400(D2.0-06 §4.7.2 정본: 24시간, 3개소) (3) EventTypeRegistry 53+→123(D2.1-D2 SOT, 6개소+코드블록 주석) (4) FailureCodeRegistry 20+→36(D2.1-D2 SOT, 3개소+코드블록 16→36항목 확장) (5) FallbackRegistry 13/14→23(D2.1-D2 SOT, 3개소+코드블록 14→23항목 확장). **MEDIUM 3건** — (1) memory_ttl_L2 "365d"→"unlimited"(BASE-1.3 §L260 "영구", 2개소) (2) AutonomyLevelSchema 추가(D2.1-D7 §4.7, 24→25개 스키마, 양쪽 테이블+7개 참조 동기화) (3) V2 Guardrails "3-Layer"→"4-Layer 중 3개 활성" 표현 명확화(2개소) |
| v16.0.0 | 2026-03-03 | 구현 시뮬레이션 검토 반영 (~12건): **BLOCKER 2건** — (1) config.v1.toml V0 축약본 전체 재작성(PHASE_B4 §3 정본: [general]→[core], [safety]→[approval]+[rbac], [memory] 제거→[storage] 통합, 전체 키명 B4 정본 정렬: daily_limit/warn_threshold/default_timeout_ms 등, 13섹션 체계) (2) V1 AI 프롬프트 config 블록 동일 B4 정렬 적용. **HIGH 5건** — (1) ipc/→bridge/ 전수 4개소 교체(PHASE_B2 §4.1 정본) (2) langchain-community+aiosqlite 의존성 추가(PHASE_B3) (3) D2.0-02 section reference 3건 정정(I-15=§7.90~92 B-type, I-8=§7.41~50 A+type, I-19=D2.0-07 미수록) (4) VamosConfig Pydantic 모델 13개 서브모델 B4 동기화(general→core, safety→approval+rbac, memory 제거) (5) cost key 이름 정정(daily_limit_krw→daily_limit). **MEDIUM 2건** — (1) approval config ref 정정(safety.approval_timeout_s→approval.timeout_s) (2) V0 config 13섹션 체계 주석 갱신 |
| v17.0.0 | 2026-03-03 | 잔존 이슈 방법론계획 v1.1 Track A 19건 일괄 반영: **BLOCKER 2건** — (B-1/B-2) Method A+B+C 통합: STEP-1에 Schema Seed 파일 생성 단계 추가, STEP-2에 전제조건 가드+FREEZE 스키마 인라인 참조(Method C)+SOT 문서 MANDATORY 강화(Method A). **MEDIUM 16건** — (M-4) `#[tauri::command]` 구현 패턴 코드 추가, (M-5) JSON-RPC stderr 로그 분리 규칙 명시, (M-6) config_loader 3단계 로딩 순서(TOML→ENV→CLI) 명시, (M-7) V1-Phase 1 모듈 ID↔파일명 매핑 테이블 전수 추가(17개 모듈), (M-8) LogEventSchema 7필드 PART2 내 교차검증 완료+주석, (M-10) Ollama CI mock/skip 대안 3가지 명시, (M-12) I-6 의존성 I-4→I-5 수정, (M-13) 대화 내보내기 UI 참조 위치 명확화, (M-14) SelfCheckGate 파이프라인 위치 명시(S5→SelfCheck→S6)+5-Gate 순서 보강, (M-22) MCP 도구 카운트 정렬(V1=7/V2+=3/V3=1 구분)+내부/외부 도구 설명, (M-23) SOURCE_CONFLICT 전수 인덱스 12건(§7.5.5), (M-25) Semantic Cache LOCK 파라미터 테이블 추가(cosine≥0.95), (M-26) VamosState trace_id 필드 추가, (M-28) SDAR 5-Gate↔VAMOS 5-Gate 코드 공유 전략+BaseGate 인터페이스, (M-29) Cloud Library 13개 LOCK 전수 기재+SOT 근거, (M-30) L0 TTL session_end 정의 명확화(비활성 타임아웃+30일 상한). **LOW→MEDIUM 1건** — (L-3) embedding 라이브러리 FlagEmbedding 확정(BAAI 공식, Matryoshka 256dim 네이티브 지원). |
| v18.0.0 | 2026-03-03 | V2/V3 실행 가이드 추가 (V0 포맷 기준): **§4 V2 구현** 3개 Phase에 `실행 가이드`(사용자 직접 작업 + AI 프롬프트) + `산출물 참조` 섹션 전수 추가 — V2-Phase 1(인프라 마이그레이션: 7개 마이그레이션 스크립트+Docker Compose+배포 AI 프롬프트, 사용자 8단계), V2-Phase 2(COND 모듈 활성화: 10개 모듈 개별 구현 AI 프롬프트+파일명+의존성, 사용자 6단계), V2-Phase 3(Agent Teams V2+보안: Redis MessageBus+6패턴+HMAC+LlamaGuard L3+GDPR+Cloud Library V2+RT-BNP V2+SDAR AR-L3, 사용자 8단계). **§5 V3 구현** 3개 Phase에 동일 구조 전수 추가 — V3-Phase 1(인프라 스케일업: K8s Helm 차트+vLLM+관리형 DB+Loki+Grafana, 사용자 8단계), V3-Phase 2(EXP 모듈 전체 활성화: 14그룹 39개 모듈 개별 구현 AI 프롬프트+파일명+디렉토리 구조, 사용자 8단계), V3-Phase 3(고급 기능+최종 통합: Agent Marketplace+50+ Agent Mesh+Self-evo Governance+SDAR AR-L4+Cloud Library V3+A2A 프로토콜+멀티모달+38개 벤치마크, 사용자 8단계). 총 6개 AI 프롬프트 + 6개 사용자 작업 가이드 + 6개 산출물 참조 섹션 신규. |
| v19.0.0 | 2026-03-06 | Phase 2-A Ripple Fix (v8.1 검증 파이프라인): **CRITICAL 3건** — (FIX-01/C-6) ORANGE CORE S0~S8 9-State 상태 머신 인라인 추가(D2.0-02 §2.2 정본, 타임아웃+LOCK 주석 포함), (FIX-02/C-2) VamosState pipeline_state 필드 추가(S0_RECEIVED~S8_DONE 연동), (FIX-03/C-5) §7.x 참조 v14.0.0 수정 완전성 검증 PASS. **HIGH 6건** — (FIX-04/H-B1) Cloud Library G0-G4 G1/G2 의미 불일치 SOURCE_CONFLICT HTML 주석(PART2 Trust/Relevance vs SRC Content/Consistency), (FIX-05/H-B3) vectorbt 조건부 ADOPT(D-S3-05 정본), (FIX-06/H-B5) V1+ 추가 config 4섹션 인라인 참조(rate_limit/blue_nodes/ui/guardrails, B4 §3 정본), (FIX-07) V1-Phase 4 Layout/Route 출처 정정(D2.0-08 §2.1/§3), (FIX-08) V1-Phase 4 Component 출처 정정(D2.0-08 §10.4), (FIX-09) CLI vamos policy 추가(D2.0-08 §2.3.1), (FIX-12) A-1 MultiBrain Adapter Failover 체인 추가(GPT-4o→Claude→Ollama 3회, LOCK). **MEDIUM 2건** — (FIX-10) Failure/Fallback 참조 D2.0-08 §7→14개 FailureCodes+9개 FallbackRegistry 정정, (FIX-11) 동시성 메트릭 분리(BLUE_NODES=3/TOOLS=5). **SOURCE_CONFLICT 2건** — CL-G1/G2 의미 범위 차이(수정 제외, HTML 주석 기록). Ripple Map 전수 검색 기반 11건 수정, 2건 SC 기록, 미수정 사유 보고서 포함. |
| v19.1.0 | 2026-03-06 | Phase 2-B 재검증(Phase 0 전수 재실행): **수정 1건** — V3-Phase 2 EXP 모듈 테이블 line 2084 RT-BNP 행 열 수 불일치 해소(5열→4열, 참조를 구현 내용 셀로 병합). Phase 0 14개 스크립트 2차 실행 결과: PASS 8/FAIL 6, 잔여 FAIL 6건 전수 FALSE_POSITIVE 판정(0-D: 부분 키 매칭 오류, 0-E: changelog 컨텍스트 차이, 0-H: 요약 테이블, IMP-C: 약칭 vs 전체 열거, IMP-D: V0 의도적 설정 차이+경로 규약+pyproject 섹션 혼입, IMP-F: 인라인 주석+상태명 S3 오인식). REAL_ERROR 0건. |
| v20.0.0 | 2026-03-06 | 단계 완료 검증(Stage Gate) 18개 추가: V0-STEP-1~6(6개) + V1-Phase 1~6(6개) + V2-Phase 1~3(3개) + V3-Phase 1~3(3개). 각 Stage에 `### 단계 완료 검증` 섹션 신규 삽입 — 검증 항목/확인 방법/필수 여부 테이블 + 진입 금지 조건 명시. 총 ~190개 검증 항목. 각 Stage Gate의 검증 항목은 해당 STEP의 작업 내용/SOT 문서에서 도출. |
| v20.1.0 | 2026-03-06 | Stage Gate SOT 정합성 검증 후 4건 수정: (1) V2-Phase 1 Hybrid Search alpha=0.6→0.7 (LOCK 테이블 정본 α=0.7 일치), (2) V3-Phase 3 Stage Gate SDAR AR-L4 "5개 액션"→"4개 액션" (SDAR_SPEC 수리 액션 카탈로그 AR-L4=4개: code_hotfix, migrate_schema, reinstall_dependency, rebuild_vector), (3) V1-Phase 3 Stage Gate에 A-2 Preset Modularization 검증 항목 추가 (구현 항목 #6 누락 보완), (4) V1-Phase 4 Stage Gate에 디자인 시스템 CSS Custom Properties 검증 항목 추가 (구현 항목 #13 누락 보완). |
| v20.2.0 | 2026-03-06 | Stage Gate SOT 교차 검증 Phase 2 — V0/V1/V2/V3 에이전트 병렬 검증 후 7건 수정: (1) V0-STEP-1 config 템플릿 semantic_cache.ttl_sec SOURCE_CONFLICT 주석 보완(D2.0-06=86400 vs B4=3600, DESIGN>PHASE_B 원칙 적용), (2) V0-STEP-5 Stage Gate LogEventSchema 7필드명 SOT 정정(trace_id,timestamp,level→event_type,producer,when,payload,severity,sinks,links, D2.1-D2 §4.2 정본), (3) V0-STEP-4 Stage Gate에 EvidenceGate stub 검증 항목 추가(구현 항목 누락 보완), (4) V1-Phase 6 완료 체크리스트 5-Gate 순서 수정(Policy/Cost/Approval→Policy/Approval/Cost, CLAUDE.md §7.2 LOCK 정본), (5) V1-Phase 6 Stage Gate V1→V2 전환 조건 6개 전수 기재(메모리 승격/강등 오류율<1% + P0 테스트 100% 누락 보완), (6) V2-Phase 2 Stage Gate에 I-22/I-23/A-4 개별 검증 항목 3건 추가(COND 모듈 개별 검증 누락 보완), (7) V2 완료 체크리스트에 HMAC-SHA256/GDPR/SDAR AR-L3 항목 3건 추가(Phase 3 핵심 작업 누락 보완). |
| v20.3.0 | 2026-03-06 | Stage Gate SOT 교차 검증 Phase 3(심화): (1) V1-Phase 4 구현 항목에 Log 페이지 + NodeDetail 페이지 2건 추가(PHASE_B2 §3.1 SOT에 7개 페이지 정의, 구현 항목 테이블에 5개만 기재되어 누락 보완, 번호 #9~#16으로 재정렬), (2) Hybrid Search 파라미터 라인 참조 수정("D2.0-06 L768 정본"→"D2.0-06 S7D-012/S7D-018 정본", L768은 Chroma 설정이므로 정확한 섹션 참조로 변경). |
| v20.4.0 | 2026-03-06 | SDAR 액션 목록 SOT 정합성 수정 2건: (1) V2-Phase 2 AI 프롬프트 AR-L3 MEDIUM risk 5개 액션을 SDAR_SPEC §10.2 정본으로 전면 교체(모듈재시작/의존성재로드/인덱스리빌드/커넥션풀리셋/임시파일정리 → patch_prompt_template/update_config_parameter/rotate_api_key/rollback_to_snapshot/compress_logs), (2) V3-Phase 3 AI 프롬프트 AR-L4 HIGH risk 액션을 5개→4개로 수정 + SDAR_SPEC §10.3 정본 액션명 적용(서비스재배포/데이터복구/설정롤백 삭제 → reinstall_dependency/rebuild_vector_index 추가). |
| | | *v21.0.0 건너뜀: v20.x 시리즈에서 Stage Gate 관련 수정이 v20.4.0까지 진행되어 다음 메이저 변경(v10 누락 항목)을 v22.0.0으로 배정* |
| v22.0.0 | 2026-03-09 | v10 Phase 2 누락 항목 반영 (v10_part2_patch_plan.md 기반): **BLOCKER 2건** — (PATCH-B01) §5.2 V3-Phase 2에 PARL Agent Swarm 2행 추가(행 15~16: TEE Execute PARL 패턴 통합, 에이전트 풀 자동 확장/축소) + 6개 연쇄 수정(실행 가이드 #9, AI 프롬프트 그룹 15, §6.7 PARL 상세, §6.13 수량 갱신, §7.4 GO/NO-GO #12, §5.2 Stage Gate #13), (PATCH-B02) §5.3 V3-Phase 3에 Agent Specialization 1행 추가(행 9: 자동 fork/특화/retire) + 5개 연쇄 수정(실행 가이드 #9, AI 프롬프트 §9, §6.7 Specialization 상세, §5.3 Stage Gate #13). **HIGH 1건** — (PATCH-H02) §3 V1-Phase 1에 I-5/I-8/I-9 하위 구현 체크리스트 추가(DomainScore 점수화, 비용 기반 뇌 선택, 3단계 경보, 고비용 모델 제약, 대화 턴 상한 5건). **수량 갱신** — §6.13 V3 기타 ~17→~25 (+8 SP), 합계 ~454→~462. **GO/NO-GO** — §7.4 V3 #12 PARL 병렬 실행 안정성 항목 추가 (11→12항목). |
| v23.0.0 | 2026-03-11 | v10 Phase 2 Step 2 전수 검증: TRUE_MISSING 200건 반영 (V1+57/V2+121/V3+22). §3~§5 Phase 테이블 확장, §6.13 작업량 갱신 |
| v24.0.0 | 2026-03-12 | 메이커 에반 7개 개선안 반영: (1) §1.3 AI 구현 공통 규칙 신설 — 판단 실패 시 규칙(SDD 개선안 2) + Claude Code 세션 운영 규칙(개선안 6) + 컨텍스트 다이어트 원칙(개선안 1, 참조 SOT MUST/MAY/NEVER 이원화). (2) §6.5.1 AI 코드 생성 보안 체크리스트 7항목 추가(개선안 3) + V0-STEP-4 규칙에 보안 규칙 연동. (3) V0-STEP-2에 Unified Schema Registry(schema_registry.toml) 생성 항목 추가(개선안 4, toml 구조 예시 포함). (4) V0-STEP-4 + V1-Phase 3 LOCK에 LangGraph 단순 제어 흐름 원칙 추가(개선안 5, StateGraph 중첩 금지). (5) V3-Phase 1에 Hetzner CX31 + RunPod Serverless 인프라 대안 추가(개선안 7, ~$123-142/월, $200 LOCK 준수). LOCK 위반 0건. 기존 행 변경/삭제 0건. |
| v25.0.0 | 2026-03-13 | v11 적대적 검증 179건 수정 (7 Tier, 42 Fix Group 일괄 반영): **Tier 1 BLOCKER 9건** — FG-B01 비용 알람 3단계 통일(80/100→70/85/95), FG-B02 전환조건 시간 모순 해소(Loki 10d→30d), FG-B03 COND 모듈 총수 +8→+10 정정, FG-B04 I-7/I-12 V2 COND 확정, FG-B05 모듈 총수 32/42/81 정합, FG-B06 Stage Gate 5-Gate 순서 전수 통일, FG-B07 CL-G1/G2 Content Quality/Consistency 통일(10개소), FG-B08 EventTypeRegistry 123항목 SOT 정렬(6블록 교체), FG-B09 §6.12 운영 섹션 신설(모니터링/백업RPO/인시던트/알림/롤백). **Tier 2 HIGH-FIX 6건** — FG-H05 config 키 이름 5건, FG-H06 Glossary 87항목 + Reading Guide 신설, FG-H10 config.v1.toml 이중 게시 정본 라벨, FG-H01 Gate 명칭 전파 10개소, FG-H11 V0 config 축약본 라벨, FG-L01 §6.8 AI Investing 참조 정정. **Tier 3 HIGH-ADD 8건** — FG-H09 V0→V1 전환조건 10항목 이행 검증 항목 추가, FG-H12 Glossary+Reading Guide(§1.2), FG-H08 보안 3섹션 신설(§6.5.2 HMAC 방어, §6.5.3 STRIDE, §6.5.4 OWASP LLM Top 10), FG-H13 테스트 상세 명세 38건(T-VAL/T-SDAR/T-HMAC/T-GUARD/T-GDPR/T-AC/T-ARCH), FG-H03 TC 측정 메커니즘(V1→V2 6항+V2→V3 6항), FG-H07 시스템설계 갭 4건(Fast Gate↔5-Gate/UI매핑/NEVER_AUTO/FailureCode 확장), FG-H04 R1~R11 공통 규칙 레지스트리+12프롬프트 전파, FG-H02 V1 Phase 2~6 실행가이드/AI프롬프트/규칙/참조SOT 블록. **Tier 4 MEDIUM-FIX 4건** — FG-M04 코드블록 import 수정(LangGraph START/END, structlog, Pydantic), FG-M01 총수 63→64, FG-M02 SC-15 추가(총 14→15), FG-M09 참조 오류 수정 3건. **Tier 5 MEDIUM-ADD 11건** — dimension LOCK 1024/256 주석, EventType 134항목 표기, GPU $144 근거, V1 병렬/순차 규칙, 버전 비교표(§1.1), LOCK 값 검증 체크리스트(§7.5.5), 에러/폴백 관계도 ASCII 등. **Tier 6 RESTRUCTURE 3건** — FG-M10 V3 모듈 재분배(Phase 2→3 12건 이동, sub-group 헤더, s02~s08 개별 config 키), FG-M13 v10 테이블 가독성(§3~§5 서브그룹 헤더 15개 삽입), FG-L06 Stage Gate 수량 정정(V2=43/V3=37, 총 204건)+LOCK-AT 범위+턴 제한 관계 명확화. **Tier 7 LOW 4건** — FG-L02 v21 건너뜀 면책 주석, FG-L03 V3 EXP BaseModule 코드 패턴, FG-L04 운영 보완 6섹션(§6.12.6~11: 헬스체크/로그보존/비용초과/SDAR폴백/RT-BNP장애/Cloud페일오버), FG-L05 행번호→앵커 전환(선택적, 보류). **총 변동**: 4395행→5252행(+857행). LOCK 위반 0건. |
| v25.1.0 | 2026-03-13 | V1 Phase 1~6 파일경로 칼럼 전수 추가: (1) V1-Phase 1에 M-7 파일 기본 경로 노트 추가(`backend/vamos_core/orange_core/` 명시), (2) L1698 파일 경로 참조 노트를 PHASE_B2 기준 상대경로 체계로 확장(Python/React/Rust/CI/Test 5개 기본경로), (3) V1-Phase 2~6 구현 항목 테이블에 `파일경로` 칼럼 추가 — Phase 2(13항목: storage/memory, storage/vector, storage/graph, storage/cache, safety/guardrails 등), Phase 3(59항목: agent/graph, agent/pipeline, infra/brain, blue_nodes/dev~quant, orange_core 등 + v23 확장 44건 §6 참조), Phase 4(19항목: components/layout, pages/*.tsx, hooks, stores, styles 등), Phase 5(15항목: e2e, backend/tests/unit~integration, .github/workflows 등), Phase 6(11항목: blue_nodes/trading, mcp/bridge~server~client, orange_core 등). v23 확장 항목 57건은 일괄 `§6 참조`. **총 변동**: 5252행→5259행(+7행). LOCK 위반 0건. |
| v25.2.0 | 2026-03-13 | V0~V3 AI 프롬프트 전수 검토 및 보완: **V1 Phase 1~6 상세 AI 프롬프트 신규 작성** — (1) V1-Phase 1 AI 프롬프트 신규 생성(~140행: 17개 I-모듈 파일경로+SOT 참조, Week 1-2/3-4 분할, 9-State SM, LOCK 값, 검증 10항목), (2) V1-Phase 2~6 AI 프롬프트 1행 요약→상세 업그레이드(Phase 2 ~75행: 9 core+4 v23/Phase 3 ~80행: 15 core+44 v23/Phase 4 ~70행: 16 core+3 v23/Phase 5 ~65행: 12 core+3 v23/Phase 6 ~65행: 8 core+3 v23). 각 프롬프트에 작업 목표/MUST 로드 SOT/구현 항목(파일경로 포함)/LOCK 값/검증 체크리스트 포함. **V0 STEP 1~6 검토** — 전체 양호(수정 불필요). **V2/V3 검토 후 보완 2건** — (3) V2-Phase 3 AI 프롬프트에 v23 확장 15건 요약 추가(OAuth2+MFA, E-054~E-060, 방화벽, E-063~E-068), (4) V3-Phase 2 AI 프롬프트에 v23 핵심 기술 6건 요약 추가(LSTM/Real Trading/Muon/관리자콘솔/VPN/CRM). **포맷 통일** — V1 Phase 4~6 코드블록 ```→```` (4 backtick) 전수 교체(6개소). **최종 검증**: 18개 AI 프롬프트(V0:6+V1:6+V2:3+V3:3) 전수 존재 확인, ````text 코드블록 18개 매칭, LOCK 위반 0건. |
| v26.0.0 | 2026-03-15 | v12 Phase 3: BLOCKER 9건 + HIGH 78건 + MEDIUM 84건 + LOW 19건 = 190건 신규 삽입, §6 참조 구체화 42건, §6 내용 추가 22건, 수치 갱신 8건, 구조 수정 5건 (총 279건 수정) | <!-- v26.0.0 v26 --> |
