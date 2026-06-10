# 0-0 Governance-Rules-Meta 규칙서

> **버전**: v1.0
> **작성일**: 2026-03-24
> **Tier**: T0 — Governance (축약 4섹션 템플릿)
> **정본 출처**: Part2 구현단계 §1 Foundation (L1-191), §6.13 (L6127-6141), §7 Validation (L6143-6450)
> **목적**: VAMOS 프로젝트 전체 거버넌스 메타 — 설계 원칙, 공통 규칙 R1~R11, LOCK/FREEZE 레지스트리, K-값, Phase 체크리스트를 단일 정본으로 관리

---

## §1 개요

### 1.1 도메인 정의

본 도메인(0-0)은 VAMOS AI 프로젝트의 **거버넌스 메타 정보**를 관리하는 단일 도메인이다. 모든 다른 도메인(1-1 ~ 6-13)은 본 도메인의 규칙을 **참조 전용**으로 사용하며, 규칙 변경은 본 도메인에서만 가능하다.

### 1.2 설계 원칙 요약 (Part2 §1 Foundation 기반)

| 원칙 | 설명 |
|------|------|
| **버전 진화** | V0(Scaffold) → V1(MVP) → V2(Pro) → V3(Enterprise) 순차 진행. 이전 버전 완료 없이 다음 버전 진입 금지 |
| **모듈 분류** | CORE(핵심) / COND(조건부) / EXP(실험) 3단계. CORE→COND 단방향 의존만 허용 |
| **정본 우선순위** | RULE 1.3 > PLAN 3.0 > DESIGN 2.0 LOCK > DESIGN 본문 > 스키마/TECH_STACK |
| **핵심 규약** | LOCK(절대 변경 불가), FREEZE(구조 고정, 값 변경 가능), SOT(정본 문서 — 충돌 시 SOT 우선) |
| **비용 절대 상한** | V1: ₩40,000/월, V2: ₩93,000/월, V3: ₩266,000/월 (ABSOLUTE LOCK) |
| **자율도 단계** | V0=L0(MANUAL), V1=L2(COPILOT), V2=L3(AUTONOMOUS), V3=L4(SELF_EVOLVING) (정본: GLOSSARY §14 — MANUAL=L0) |

### 1.3 프로젝트 구조 표준 (Part2 §2 STEP-1 기준)

```
vamos/
├── src/                    # React 18 + TypeScript
├── src-tauri/              # Rust Tauri 2.0
├── backend/                # Python 3.11+
│   ├── orange_core/        # I-Series 모듈
│   ├── blue_nodes/         # E-Series 모듈
│   ├── tools/              # MCP 도구
│   └── tests/
├── shared/types/           # 공유 타입 (codegen)
├── config/
│   ├── config.v1.toml      # 메인 설정 (LOCK)
│   └── .env.example
├── data/                   # SQLite DB, Chroma 데이터
├── logs/                   # JSONL 로그 파일
├── scripts/                # 유틸리티 스크립트
├── docs/
├── .github/workflows/
├── CLAUDE.md
└── README.md
```

### 1.4 버전별 활성 모듈 수

| 버전 | I-Series | E-Series | S-Series | A-Series | B-Series | C-Series | D-Series | EVX | 합계 |
|------|---------|---------|---------|---------|---------|---------|---------|-----|------|
| V0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **5** |
| V1 | 17 | 6 | 1 | 2 | 1 | 3 | 2 | 0 | **32** |
| V2 | 22 | 10 | 1 | 3 | 1 | 3 | 2 | 0 | **42** |
| V3 | 25 | 16 | 8 | 7 | 6 | 7 | 6 | 6 | **81** |

### 1.5 버전별 핵심 차이

| 항목 | V0 | V1 | V2 | V3 |
|------|-----|-----|-----|-----|
| **목적** | 실행 가능한 뼈대 | Operational MVP | Scale-Up | Enterprise |
| **기간** | 1-2주 | 14-16주 | 11-13주 | 12-16주 |
| **인프라** | 로컬 (Tauri) | 로컬 (Tauri) | VPS + Docker Compose | Hetzner Lite/K8s |
| **DB** | SQLite + Chroma | SQLite + Chroma | PostgreSQL + Qdrant + Neo4j | 관리형 DB + PVC |
| **LLM** | Ollama 단일 | Ollama + GPT-4o-mini | Claude + Ollama (2-tier) | Claude + vLLM |
| **비용 상한** | ₩0 (로컬) | ₩40,000/월 LOCK | ₩93,000/월 LOCK | ₩266,000/월 ABSOLUTE LOCK |
| **자율도** | L1 (수동) | L2_COPILOT | L3_AUTONOMOUS | L4_SELF_EVOLVING |
| **모듈** | CORE 5개 | CORE 32개 | CORE+COND 42개 | 전체 81개 |
| **SDAR** | OFF | OFF | AR-L2~L3 | AR-L4 + Self-evo |
| **Agent** | 없음 | Lead+2 Sub | Teams 10 | Mesh 50+ |
| **보안** | 기본 (입력 검증) | 2-Layer Guardrails | 3-Layer + HMAC | 4-Layer + LlamaGuard |

### 1.6 의존성 체인 (필수 순서)

```
V0 완료 → V1 진입 → V1 완료 → V2 마이그레이션 → V2 완료 → V3 업그레이드
```

### 1.7 Glossary (주요 약어)

| 약어 | 정식명 | 설명 |
|------|--------|------|
| VAMOS | Virtual AI Mind Operating System | AI 멀티버전 운영 체제 |
| CORE/COND/EXP | Module Category | 핵심/조건부/실험 모듈 |
| S0~S8 | Pipeline State | 9-State 상태 머신 |
| 5-Gate | Policy→Approval→Cost→Evidence→SelfCheck | 의사결정 검증 체계 |
| CL-G0~G4 | Cloud Library Gate | 수집 검증 게이트 |
| P0~P3 | Priority Level | 우선순위 (P0=긴급~P3=낮음) |
| L0~L3 | Memory Layer | Session→Project→Long-term→Procedural |
| AR-L1~L4 | Auto-Repair Level | SDAR 수리 수준 |
| SDAR | Self-Diagnosis and Auto-Repair | 자가진단/자동수리 엔진 |
| RT-BNP | Real-Time Breaking News Pipeline | 실시간 속보 파이프라인 |
| DCL | Domain Context Layer | 도메인 컨텍스트 계층 |
| PARL | Parallel Agent Runtime Layer | 병렬 에이전트 런타임 |
| RBAC | Role-Based Access Control | 4레벨 (OWNER/ADMIN/OPERATOR/VIEWER) |
| MCP | Model Context Protocol | 도구 프로토콜 |

---

## §2 규칙 목록

### 2.1 R1~R11 공통 규칙 레지스트리 (Part2 §1.3 원문)

> **LOCK**: 아래 R1~R11은 모든 V0-STEP 및 V1~V3 Phase AI 프롬프트에 공통 적용되는 규칙이며, 모든 프롬프트의 규칙 섹션에서 강제 참조됩니다.

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
| **R11** | `schema_registry.toml` 단일 참조점 활용 | 스키마 참조 | 중복 정의 방지 |

### 2.2 판단 실패 시 규칙 (SDD 명세 계층) — Part2 §1.3.1 원문

> AI가 구현 중 불확실한 상황에 직면했을 때 따라야 할 절대 규칙:

| # | 상황 | 조치 |
|---|------|------|
| 1 | 필드 수가 SOT(seed JSON / D2.1 스키마)와 다름 | **즉시 중단** + 사용자에게 불일치 보고. 임의 필드 추가/삭제 금지 |
| 2 | LOCK/FREEZE 값 변경 시도 | **거부**. LOCK 값은 runtime 변경 불가 (config.v1.toml frozen) |
| 3 | 참조 SOT 문서에 없는 내용 | **창작 금지**. "해당 스펙 미정의" 보고 후 사용자 판단 대기 |
| 4 | 삭제가 필요한 경우 | **삭제 금지**. `[DEPRECATE] + (대체 경로)` 로만 처리 |
| 5 | 모듈 간 의존성이 불명확 | 상위 문서(RULE 1.3 > PLAN 3.0 > DESIGN LOCK) 순서로 확인 후 판단 |

### 2.3 Claude Code 세션 운영 규칙 — Part2 §1.3.2 원문

| # | 시점 | 명령/행동 | 목적 |
|---|------|----------|------|
| 1 | 각 STEP/Phase 완료 후 | `/compact` 실행 | 컨텍스트 요약 → 토큰 비용 절감 + 맥락 오염 방지 |
| 2 | 코드 생성 완료 후 | `/review` 실행 | AI 자기 검토 → 품질 향상 |
| 3 | 장시간 세션 중 (30분+) | `/cost` 확인 | 비용 모니터링 → V1 ₩40,000/월 상한 준수 |
| 4 | 새 STEP/Phase 시작 시 | `/clear` 또는 새 세션 | 이전 맥락 간섭 방지 |
| 5 | 복수 파일 수정 시 | 순차 실행 (큐 방식) | 파일 간 충돌 방지, 변경 추적 용이 |

### 2.4 컨텍스트 다이어트 원칙 — Part2 §1.3.3 원문

| 구분 | 정의 | AI 세션 적용 |
|------|------|-------------|
| **필수 로드 (MUST)** | 해당 STEP에서 직접 구현하는 기능의 SOT | @file 첨부 또는 직접 붙여넣기 |
| **선택 참조 (MAY)** | 관련되지만 직접 구현 대상이 아닌 문서 | 필요 시에만 부분 참조 |
| **참조 금지 (NEVER)** | 해당 STEP 범위 밖 문서 (다른 버전/다른 Phase) | 첨부 금지 — 토큰 낭비 + 환각 유발 |

> **핵심**: AI 한 세션에 첨부하는 SOT 문서는 **3~5개 이내**로 제한.

### 2.5 LOCK/FREEZE 전체 목록 (Part2 §1 + §2 STEP-1 config.v1.toml 추출)

#### 2.5.1 LOCK 값 (절대 변경 불가)

| # | 항목 | 값 | 출처 |
|---|------|-----|------|
| L1 | `[core] autonomy_level` | `"L1"` (V0) | PHASE_B4 §3.1 |
| L2 | `[core] single_decision_lock` | `true` (always) | PHASE_B4 §3.1 |
| L3 | `[core] pipeline_stages` | `["intake","plan","execute","verify","deliver"]` | PHASE_B4 §3.1 |
| L4 | `[llm] max_tokens` | `2048` | B4 §4.1 (V1 기준) |
| L5 | `[embedding] model` | `"bge-m3"` | PHASE_B4 §3.3 |
| L6 | `[embedding] dimension` | `1024` | PHASE_B4 §3.3 |
| L7 | `[vector_db] backend` | `"chroma"` (V1), V2=qdrant | PHASE_B4 §3.4 |
| L8 | `[graph_db] backend` | `"json_file"` (V1), V2=neo4j | PHASE_B4 §3.5 |
| L9 | `[cost] monthly_limit` | V1=40000, V2=93000, V3=266000 (KRW) | PHASE_B4 §3.7, ABSOLUTE LOCK |
| L10 | `[self_check] threshold_p0` | `70` | PHASE_B4 §3.8a |
| L11 | `[self_check] threshold_p1` | `75` | PHASE_B4 §3.8a |
| L12 | `[self_check] threshold_p2` | `80` | PHASE_B4 §3.8a |
| L13 | `[self_check] soft_loop_max` | `1` (자동 1회만) | PHASE_B4 §3.8a |
| L14 | `[approval] timeout_s` | `600` (10분) | PHASE_B4 §3.8b |
| L15 | `[approval] p2_timeout_s` | `300` (5분) | PHASE_B4 §3.8b |
| L16 | `[mcp] transport` | `"streamable_http"` | PHASE_B4 §3.9 |
| L17 | `[logging] format` | `"json"` (평문 금지) | PHASE_B4 §3.12 |
| L18 | `[logging] trace_id_required` | `true` | PHASE_B4 §3.12 |
| L19 | `[semantic_cache] similarity_threshold` | `0.95` | PHASE_B4 §3.15 |
| L20 | 5-Gate 순서 | Policy→Approval→Cost→Evidence→SelfCheck | pipeline.py |
| L21 | 9-State 전이 순서 | S0→S1→...→S8 (변경 불가) | pipeline.py |
| L22 | B↔L 매핑 | B-1→L1, B-2→L3, B-3→L2, B-4→L0 | memory 모듈 |
| L23 | NEVER_AUTO 정책 | P1+ 자동승인 금지 | ApprovalGate |

#### 2.5.2 FREEZE 값 (구조 고정, 값 변경 가능)

| # | 항목 | 값 | 출처 |
|---|------|-----|------|
| F1 | DecisionSchema 필드 수 | 18 (14필수+4선택) | D2.1-D2 §4.1 |
| F2 | ResponseEnvelope 필드 수 | 5 | CLAUDE.md §12 LOCK |

### 2.6 K-값 레지스트리 (Part2 §1 + config.v1.toml 추출)

| K-ID | 항목 | 값 | 버전 | 성격 |
|------|------|-----|------|------|
| K-1 | V0 활성 모듈 | 5 (I-1,I-2,I-3,I-5,I-19) | V0 | LOCK |
| K-2 | V1 활성 모듈 | 32 | V1 | LOCK |
| K-3 | V2 활성 모듈 | 42 | V2 | LOCK |
| K-4 | V3 활성 모듈 | 81 | V3 | LOCK |
| K-5 | GO/NO-GO 합계 | 64 (V0=16, V1=22, V2=14, V3=12) | 전체 | LOCK |
| K-6 | Stage Gate 합계 | 204 (V0=58, V1=66, V2=43, V3=37) | 전체 | LOCK |
| K-7 | 코딩 작업량 합계 | ~696 | 전체 | FREEZE |
| K-8 | 산출물 파일 수 | 43 | 전체 | LOCK |
| K-9 | SOURCE_CONFLICT 해소 | 15건 전수 해결 | 전체 | LOCK |
| K-10 | RBAC 역할 수 | 4 (OWNER/ADMIN/OPERATOR/VIEWER) | 전체 | LOCK |
| K-11 | Guardrails 계층 | V1=2, V2=3, V3=4 | 버전별 | LOCK |

### 2.7 SLA 목표치 (Part2 §7.5.3 성능 검토)

| 지표 | 목표 |
|------|------|
| Simple response (mini) | start ≤ 2초 |
| Complex response (main+tool) | ≤ 10초 |
| Self-check | ≤ 1초 |
| 동시 처리 | BLUE_NODES=3 / TOOLS=5 concurrent |
| Token counting | ≤ 50ms / 10K tokens |

### 2.8 Tier 0 고유 규칙

| ID | 규칙 |
|----|------|
| R-T0-1 | R1~R11 변경 시 전체 도메인 AUTHORITY_CHAIN 동기화 필수 |
| R-T0-2 | LOCK/FREEZE 값 변경은 본 도메인에서만 가능 (다른 도메인은 참조만) |
| R-T0-3 | Phase 체크리스트 항목 추가/삭제 시 SESSION_PROMPTS Gate 기준 동시 갱신 |

### 2.9 R1~R11 도메인 컴플라이언스 매트릭스

> 아래 20개 도메인(1-1 ~ 6-13)은 본 문서(0-0)의 **global R1~R11 전체 준수** 대상입니다.
> 각 도메인은 자체 §4 거버넌스 규칙 섹션에 "본 도메인은 0-0 global R1~R11 전체 준수" 선언을 포함해야 합니다.

| Tier | 도메인 | R1~R11 적용 | 비고 |
|------|--------|:---:|------|
| T1 | 1-1 Verifier-Reasoning | ✅ | CORE 판단 도메인 — R7 단방향 규칙 핵심 적용 |
| T1 | 1-2 Auxiliary-Modules | ✅ | CORE 보조 도메인 |
| T2 | 2-1 Blue-Node-Architecture | ✅ | 오케스트레이션 인프라 |
| T2 | 2-2 COND-Modules-Detail | ✅ | 조건부 모듈 상세 |
| T3 | 3-2 Multimodal-Processing | ✅ | 멀티모달 |
| T3 | 3-3 PKM-Knowledge-Management | ✅ | PKM |
| T3 | 3-4 Workflow-RPA | ✅ | 워크플로 |
| T3 | 3-5 Education-Learning | ✅ | 교육 |
| T3 | 3-6 Health-Emotion | ✅ | 헬스/감정 |
| T3 | 3-7 Dev-Tools | ✅ | 개발 도구 |
| T3 | 3-8 Conversation-A2A | ✅ | 대화/A2A |
| T3 | 3-9 Business-Model-Strategy | ✅ | 비즈니스 |
| T3 | 3-10 Agent-Protocol | ✅ | 에이전트 프로토콜 |
| T4 | 4-1 Rust-Tauri-Infrastructure | ✅ | Rust/Tauri |
| T4 | 4-2 CICD-Pipeline | ✅ | CI/CD |
| T4 | 4-3 MCP-Server-Client | ✅ | MCP |
| T5 | 5-1 Benchmark-Evaluation | ✅ | 벤치마크 |
| T5 | 5-2 File-Context-Strategy | ✅ | 파일/컨텍스트 |
| T5 | 5-3 Testing-Strategy | ✅ | 테스트 전략 |
| T5 | 5-4 Error-Handling | ✅ | 에러 처리 |

> **R-prefix 충돌 방지 규칙**: 각 도메인의 문서 레벨 규칙(R-XX-N 형식, 예: R-62-1)은 **도메인 접두어를 반드시 포함**하여 global R1~R11과 명확히 구분합니다.
> - Global 규칙: R1, R2, …, R11 (숫자만, 0-0 관할)
> - 도메인 규칙: R-{도메인ID}-N (예: R-62-1, R-611-5 등, 각 도메인 관할)
> - 충돌 시: Global R1~R11이 항상 우선 (R-T0-1 적용)

---

## §3 참조 매핑

### 3.1 전체 코딩 작업량 요약 (Part2 §6.13 원문) → 도메인별 매핑

| 영역 | V0 | V1 | V2 | V3 | 합계 | 주요 매핑 도메인 |
|------|----|----|----|----|------|----------------|
| UI/UX | 0 | ~75 | ~40 | ~20 | **~135** | 6-1_UI-UX-System |
| 인프라 (Rust IPC, Docker) | ~8 | ~80 | ~15 | ~5 | **~108** | 4-1_Rust-Tauri-Infrastructure |
| 테스트 | ~15 | ~70 | ~30 | ~13 | **~128** | 5-1_Benchmark-Evaluation |
| CI/CD | 0 | ~8 | ~4 | ~2 | **~14** | 4-2_CICD-Pipeline |
| 도구 (스키마, Config) | ~10 | ~5 | ~4 | 0 | **~19** | 0-0_Governance (config) |
| 보안 | 0 | ~8 | ~5 | ~2 | **~15** | 6-2_Security-Governance |
| MCP | 0 | ~5 | ~2 | 0 | **~7** | 4-3_MCP-Server-Client |
| 기타 (이벤트, Agent, LangGraph, RT-BNP, DCL, PARL) | ~8 | ~30 | ~17 | ~25 | **~80** | 6-3, 6-5, 6-7, 6-12 |
| **합계** | **~41** | **~284** | **~292** | **~79** | **~696** | |

### 3.2 V0 GO/NO-GO 체크리스트 (16항목) — Part2 §7.1 원문

| # | 항목 | 근거 | 상태 |
|---|------|------|------|
| 1 | 통신 계층: Python 백엔드 확정 | V0-004 | [ ] |
| 2 | IMPLEMENTATION 계층 = PHASE_B 명시 | V0-002 | [ ] |
| 3 | V0 비용 엔진 = V1 한도(₩40,000) 사전 설정 (V0 실제 지출 ₩0 — 로컬 전용, §1.5 정본) | V0-001 | [ ] |
| 4 | 디렉토리 구조: PHASE_B2 정본 명시 + monorepo 생성 | V0-003 | [ ] |
| 5 | config 포맷: config.toml 통일 | V0-005 | [ ] |
| 6 | D2.1 스키마 v3.0.0 통일 승격 | CC-001 | [ ] |
| 7 | PLAN-2.0 "(대체됨)" 표기 | CC-010 | [ ] |
| 8 | BASE-1.3 전 24개 규칙 코드 매핑 | RULE 1.3 | [ ] |
| 9 | 스캐폴딩 + 의존성 설치 (pip/npm/cargo) | PHASE_B2/B3 | [ ] |
| 10 | config.v1.toml LOCK 값 배치 | PHASE_B4 | [ ] |
| 11 | 25개 스키마 코드 생성 (Pydantic v2/Zod/serde) | D2.1-D1~D8 | [ ] |
| 12 | I-1~I-3, I-5, I-19 스켈레톤 생성 (5개, I-4 제외) | READINESS §2.7 | [ ] |
| 13 | L0 세션 메모리 최소 구현 | D2.0-06 §2.1 | [ ] |
| 14 | 비용 엔진 ₩40,000/월 하드코딩 | ABSOLUTE LOCK | [ ] |
| 15 | Guardrails L1+L2 설정 | PHASE_B4 | [ ] |
| 16 | Ollama + Chroma + SQLite 초기화 | PHASE_B4 | [ ] |

### 3.3 V1 GO/NO-GO 체크리스트 (22항목) — Part2 §7.2 원문

| # | 항목 | 근거 | 상태 |
|---|------|------|------|
| 1 | I-Series 25개 모듈 정본 확정 | V1-001, V1-016 | [ ] |
| 2 | E-15, S-5 명칭 겸용 처리 | V1-002, V1-003 | [ ] |
| 3 | 38개 DEFER/TBD V1 차단 0건 확인 | V1-008 | [ ] |
| 4 | datetime.utcnow() 전수 교체 | V1-005 | [ ] |
| 5 | approval_status enum 통일 (D2.1-D7 SOT=2개: approved/denied) | V1-004 | [ ] |
| 6 | QoD 5요소 공식 통일 | V1-006 | [ ] |
| 7 | Front Mini LLM = I-1 내부 명시 | V1-007 | [ ] |
| 8 | Guardrails 4-Layer 명시 (V1=L1+L2 활성, L3+L4=V2+) | V1-010 | [ ] |
| 9 | 비용 상한 ₩40,000 통일 | V1-013 | [ ] |
| 10 | React 18.3 통일 | V1-014 | [ ] |
| 11 | LangChain Allowlist 명시 | V1-009 | [ ] |
| 12 | V1 CRITICAL 보안항목 15개 구현 완료 | READINESS §9, §6.5 | [ ] |
| 13 | 테스트 인프라 구축 (Python 80%+, Rust 80%+, React 80%+) | PHASE_B5 | [ ] |
| 14 | CI/CD 설정 완료 (GitHub Actions 8-stage) | PHASE_B6 | [ ] |
| 15 | 스토리지 스택 구축 (SQLite+Chroma+JSONL+Graph) | D2.0-06 | [ ] |
| 16 | EventTypeRegistry 통합 | CC-006 | [ ] |
| 17 | Python/TS 스키마 동기화 도구 (Pydantic→Zod) | CC-007 | [ ] |
| 18 | BEGINNER_GUIDE 모듈 목록 갱신 | CC-002 | [ ] |
| 19 | B↔L 매핑표 추가 | CC-009 | [ ] |
| 20 | STEP7 항목 수 비고 추가 | CC-011 | [ ] |
| 21 | V0 GO 체크리스트 전수 통과 | §7.1 | [ ] |
| 22 | MCP Bridge/Server/Client 개별 검증 | V1-P6 gate | [ ] |

**V1→V2 전환 조건**: QoD ≥ 0.85 (30일) / RAG 정확도 ≥ 60% / 메모리 오류율 < 1% / P0 테스트 100% / 비용 30일 무초과 / 사용자 승인

### 3.4 V2 GO/NO-GO 체크리스트 (14항목) — Part2 §7.3 원문

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
| 12 | V2 인프라 10개 컴포넌트 구축 | PHASE_B6 §5 | [ ] |
| 13 | V2 비용 모니터링 대시보드 (₩93,000 이내) | ABSOLUTE LOCK | [ ] |
| 14 | QoD 가중치 이중 체계 구분 명시 | CC-003 | [ ] |

**V2→V3 전환 조건**: QoD ≥ 0.90 (60일) / 2-tier LLM 최적화 완료 / P1 고급 테스트 통과 / Self-evo 체계 검증 / V3 비용 재검토 + 승인

### 3.5 V3 GO/NO-GO 체크리스트 (12항목) — Part2 §7.4 원문

| # | 항목 | 근거 | 상태 |
|---|------|------|------|
| 1 | V2→V3 전환 조건 충족 | CLAUDE.md §10 | [ ] |
| 2 | K8s 배포 명세 상세 완성 | V3-001 | [ ] |
| 3 | S-8 Self-evo 거버넌스 상세화 | V3-002 | [ ] |
| 4 | V3 비용 상한 재산정 + 승인 | V3-003 | [ ] |
| 5 | GraphRAG 벤치마크 정의 | V3-004 | [ ] |
| 6 | SDAR V3 ON 조건 충족 | SDAR SPEC | [ ] |
| 7 | STEP7 TITLE_ONLY ~317건 상세 보강 | V2-008 확장 | [ ] |
| 8 | 에이전트 50+ 병렬 인프라 구축 | LOCK-AT-014 | [ ] |
| 9 | A2A 프로토콜 설계 | DEFER-AT-005 | [ ] |
| 10 | Federated Agent 승인 체계 | DEFER-AT-004 | [ ] |
| 11 | Agent Marketplace 기준 확정 | DEFER-AT-003 | [ ] |
| 12 | PARL Agent Swarm 병렬 실행 안정성 | PATCH-B01, D2.0-05 §12.17.1 | [ ] |

### 3.6 크로스컷 검토 항목 (Part2 §7.5 원문)

#### 3.6.1 문서 정합성

| 검증 항목 | 방법 |
|----------|------|
| I-모듈 번호 일관성 | PLAN 3.0 ↔ DESIGN 2.0 ↔ CLAUDE.md 크로스체크 |
| E-모듈 역할 일관성 | D2.0-01/03 정본 ↔ CLAUDE.md ↔ PLAN 3.0 |
| B/C/D-Series 존재 확인 | CLAUDE.md에 81개 모듈 전체 카탈로그 |
| 스키마 버전 통일 | D1~D8 전체 v3.0.0 확인 |
| LOCK 값 코드 반영 | config.v1.toml vs 문서 LOCK 값 대조 |
| RBAC 역할 통일 | OWNER/ADMIN/OPERATOR/VIEWER |
| 비용 임계값 단일화 | config.toml 4단계: warn=70%, caution=85%, danger=95%, block=100% (6-13 LOCK-OP-07 정본, Phase 11 S11-6 갱신) |
| Gate 우회 불가 | 코드에서 Gate bypass 검색 |
| SDAR NEVER_AUTO 완전성 | 10항목 전체 코드 반영 |

#### 3.6.2 보안 검토

| 검증 항목 | 기준 |
|----------|------|
| PII 마스킹 동작 | 주민번호/전화번호/이메일/카드번호 탐지율 99%+ |
| Non-goal 차단 | Non-goal 목록 100% deny 확인 |
| P2 자동 OFF | 세션 종료 시 즉시 비활성 확인 |
| 비용 상한 준수 | 70% 경고 / 85% 주의 / 95% 위험 / 100% 차단 4단계 동작 확인 (6-13 LOCK-OP-07 정본, Phase 11 S11-6 갱신) |
| Docker 샌드박스 | 네트워크 격리, 30초 타임아웃 확인 |

#### 3.6.3 성능 검토

| 지표 | 목표 |
|------|------|
| Simple response (mini) | start ≤ 2초 |
| Complex response (main+tool) | ≤ 10초 |
| Self-check | ≤ 1초 |
| 동시 처리 | BLUE_NODES=3 / TOOLS=5 concurrent |
| Token counting | ≤ 50ms / 10K tokens |

#### 3.6.4 정본 우선순위 준수

```
1. RULE 1.3 — 절대 불변 (Identity, Non-goal, Safety, Cost, Self-evo)
2. PLAN 3.0 — 전략 레벨 결정
3. DESIGN 2.0 LOCK — 설계 레벨 확정
4. DESIGN 본문 — 상세 설계
5. 스키마/TECH_STACK — 구현 레벨
```

#### 3.6.5 LOCK 값 검증 체크리스트

| # | LOCK 항목 | 기대 값 | 검증 위치 | 버전 |
|---|----------|---------|----------|------|
| 1 | cost.monthly_limit | V1=40000, V2=93000, V3=266000 | config.v{N}.toml `[cost]` | V0+ |
| 2 | 5-Gate 순서 | Policy→Approval→Cost→Evidence→SelfCheck | pipeline.py Gate 노드 | V1+ |
| 3 | 9-State 전이 | S0→S1→...→S8 | pipeline.py StateGraph | V0+ |
| 4 | embedding.dimension | 1024 | config `[embedding]` | V1+ |
| 5 | semantic_cache.threshold | cosine ≥ 0.95 | config `[semantic_cache]` | V1+ |
| 6 | approval.timeout_s | 600 (10분) | config `[approval]` | V1+ |
| 7 | circuit_breaker.recovery_time_sec | 60 | config `[circuit_breaker]` | V1+ |
| 8 | self_check 임계값 | P0≥70, P1≥75, P2≥80 | config `[self_check]` | V1+ |
| 9 | B↔L 매핑 | B-1→L1, B-2→L3, B-3→L2, B-4→L0 | memory 모듈 | V1+ |
| 10 | NEVER_AUTO 정책 | P1+ 자동승인 금지 | ApprovalGate | V1+ |

#### 3.6.6 SOURCE_CONFLICT 전수 인덱스 (15건)

| # | 위치 | 충돌 내용 | 채택 | 근거 |
|---|------|----------|------|------|
| SC-01 | §2 V0 모듈 | §2.8=6개 vs §2.7=5개 | 5개 | §2.7 상세 테이블 |
| SC-02 | config L2 TTL | B4="indefinite" vs BASE-1.3="영구" | indefinite | 동일 의미, B4 리터럴 |
| SC-03 | semantic_cache TTL | B4="3600" vs D2.0-06="86400" | 86400 | DESIGN 2.0 > PHASE_B |
| SC-04 | 메모리 계층 | D2.0-06=4계층 vs S7D=5계층 | 4계층 LOCK | L4=V2+ 확장 |
| SC-05 | B-3 명칭 | §5.10="Memory Decay" vs §8.4="Deep Reflection" | §5.10 LOCK | §8.4 DEPRECATE |
| SC-06 | Circuit Breaker | D2.1-D5/D7=300s vs D2.0-05=60s | 60s LOCK | DESIGN 2.0 LOCK > Schema |
| SC-07 | UI 출처 | 기존="D2.0-08" vs 실제=CLAUDE.md §14 | CLAUDE.md §14 | 출처 정정 |
| SC-08 | I-25 명칭 | D2.0-01="Self-Directed" vs SDAR_SPEC="Self-Diagnosis" | SDAR_SPEC | 전문 LOCK |
| SC-09 | 협업 패턴 | §5=5개 vs §7.1=6개(HYBRID) | 6개 | §7.1 enum 기준 |
| SC-10 | IPC 핸들러 | B1=47개 vs CLAUDE.md=72개 | 72개 | CLAUDE.md 정본 |
| SC-11 | approval_status | CLAUDE.md=4개 vs D2.1-D7=2개 | 2개 | D2.1-D7 SOT |
| SC-12 | L0 TTL | 기존 30일 vs CLAUDE.md=7일(최대30일) | 7일(최대30일) | RESOLVED |
| SC-13 | G1 Gate명 | Part2="Trust Score" vs SPEC="Content Quality" | Content Quality | SOT(SPEC) |
| SC-14 | G2 Gate명 | Part2="Relevance" vs SPEC="Consistency" | Consistency | SOT(SPEC) |
| SC-15 | Guardrails Layer | 기존 V2+=4-Layer vs 실제 | V2=3, V3=4 | B4 §3.16 정본 |

### 3.7 최종 산출물 파일 인덱스 (Part2 §7.6 원문, 43개)

| # | 파일명 | 주요 용도 | V0 필수 |
|---|--------|----------|---------|
| 1 | BASE-1.3_VAMOS_RULE_1.3_BASE.md | 절대 규칙 | ✓ |
| 2 | PLAN-3.0_VAMOS_PLAN_3_0_최종완성본.md | 전략/로드맵 | ✓ |
| 3 | D2.0-01 ~ D2.0-08 (8개) | 아키텍처 설계 | ✓/참조 |
| 4 | D2.1-A1_TECH_STACK.md | 기술 스택 | ✓ |
| 5 | D2.1-D1~D8 (8개) | 스키마 정의 | ✓ |
| 6 | D2.1-Q1_AUDIT_REPORT.md | 감사 보고서 | 참조 |
| 7 | PHASE_B1~B7 (7개) | 구현 명세 | ✓ |
| 8 | VAMOS_STEP7_* (5개) | 상세 명세 | 참조 |
| 9 | VAMOS_AGENT_TEAMS_SPEC.md | Agent Teams | V1 |
| 10 | VAMOS_AI_INVESTING_SPEC.md | AI 투자 | V1 |
| 11 | VAMOS_SDAR_DESIGN_SPECIFICATION.md | SDAR | V2 |
| 12 | VAMOS_CLOUD_LIBRARY_SPEC.md | Cloud Library | V2 |
| 13 | VAMOS_MASTER_SPECIFICATION.md | 마스터 스펙 | ✓ |
| 14 | CLAUDE.md | AI 코딩 지침 | ✓ |
| 15 | 기타 (Guide, Review 등, 5개) | 참조 | 참조 |

---

## §4 변경 이력

| 버전 | 날짜 | 변경 내용 | 영향 도메인 |
|------|------|----------|-----------|
| v1.0 | 2026-03-24 | 초기 작성. Part2 §1, §6.13, §7 전수 추출. R1~R11, LOCK/FREEZE 23+2건, K-값 11건, GO/NO-GO 64건, 크로스컷 전체, SOURCE_CONFLICT 15건, 산출물 43건 등록 | 전체 (0-0 ~ 6-13) |
| v1.1 | 2026-03-27 | S10-5 A등급 격상: §2.9 R1~R11 도메인 컴플라이언스 매트릭스 추가 (20개 도메인 전수 선언), R-prefix 충돌 방지 규칙 명문화 (Global R1~R11 vs 도메인 R-XX-N 접두어 분리) | 전체 (0-0 ~ 6-13) |
