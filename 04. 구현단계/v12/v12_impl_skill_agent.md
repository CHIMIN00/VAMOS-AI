# v12 — 구현 스킬 에이전트 설계서

> v26.0.0 동기화 완료 (2026-03-15) <!-- v12_3D v26 -->

> **작성일**: 2026-03-13
> **목표**: PART2 구현 시 "어떤 대화를 해도 구조적으로 같은 결과물"을 보장
> **핵심**: 1개 구현 스킬 에이전트 + 1개 상태 파일 (impl_status.json)
> **성격**: 설계 문서 (코드 구현 없음). V0-STEP-1 착수 시 실제 생성.

---

## 핵심 문제

v11에서 **검증**은 스킬 에이전트 2개로 "누가 해도 같은 결과"를 달성했습니다.
하지만 **구현**에는 그 장치가 없습니다.

PART2에 좋은 규칙과 프롬프트가 있지만, 세션이 바뀌면 이전 세션의 결과를 모릅니다.

```
지금 (세션마다 독립):
  세션 1: STEP-1 → config 생성 → 세션 끝 → 사라짐
  세션 2: STEP-2 → config 구조 모름 → 다르게 만듦 ← 문제

만들어야 할 것:
  ┌──────────────────────┐    ┌──────────────────┐
  │ 구현 스킬 에이전트     │    │ impl_status.json │
  │ (매 세션 시작 시 로드) │◄──►│ (세션 간 기억)    │
  └──────────────────────┘    └──────────────────┘
         │
         ▼
  세션 1: STEP-1 → config 생성 → 산출물 기록 → 상태 저장
  세션 2: 상태 로드 → STEP-1 완료 확인 → STEP-2 시작 → 일관된 결과
```

---

## §1 세션 프로토콜 (시작 / 실행 / 종료 3단계)

### 1.1 세션 시작 시 — Pre-check

```
① impl_status.json 읽기 → 현재 어느 단계인지 확인
② 이전 단계 Stage Gate PASS 여부 확인 → 미통과면 중단
③ 이전 단계 산출물(파일 목록) 존재 확인
④ 해당 단계의 LOCK 값 + naming 규칙 로드
```

**Pre-check 출력 예시**:
```
[Pre-check] 현재 단계: V0-STEP-2 (스키마 정의)
[Pre-check] 선행 완료: V0-STEP-1 ✓ (2026-03-14, Stage Gate PASS)
[Pre-check] 선행 산출물 확인:
  ✓ config/config.v1.toml 존재
  ✓ backend/vamos_core/__init__.py 존재
  ✓ pyproject.toml 존재
[Pre-check] LOCK 값 로드: 17개 (§2 LOCK 빠른 참조 테이블 참조)
[Pre-check] Naming 규칙 로드: R1 적용 (§3 참조)
[Pre-check] → V0-STEP-2 진행 가능
```

**Pre-check 실패 시**:
```
[Pre-check] ✗ V0-STEP-1 Stage Gate: FAIL (항목 3/16 미통과)
[Pre-check] → V0-STEP-2 진입 차단. V0-STEP-1 미통과 항목부터 해결하세요.
```

### 1.2 세션 실행 중 — Guard

```
① PART2 해당 섹션의 AI 프롬프트 그대로 사용
② LOCK 값 위반 감지 → 즉시 수정
③ 파일명/클래스명 naming convention 강제
④ 이전 단계에서 만든 파일 참조 시 정확한 경로/이름 사용
```

**Guard 작동 예시**:
```
[Guard] ✗ LOCK 위반 감지: autonomy_level = "L3" → LOCK 값은 "L2_COPILOT"
[Guard] → 자동 수정: L3 → L2_COPILOT (FG-H05 Canonical Decision)

[Guard] ✗ Naming 위반: IntentDetector.py → R1 규칙: snake_case
[Guard] → 정확한 파일명: i01_intent_detector.py (M-7 매핑 테이블)

[Guard] ✗ Import 위반: from langgraph import StateGraph
[Guard] → 정확한 import: from langgraph.graph import StateGraph, START, END (FG-M04)
```

### 1.3 세션 종료 시 — Post-check

```
① Stage Gate 체크리스트 실행 → PASS/FAIL
② 생성한 파일 목록 + 핵심 값 기록 → impl_status.json 갱신
③ 다음 단계에 필요한 정보 요약 저장
```

**Post-check 출력 예시**:
```
[Post-check] V0-STEP-2 Stage Gate: 10/10 PASS
[Post-check] 생성 파일:
  - backend/vamos_core/schemas/decision_schema.py (18필드 FREEZE)
  - backend/vamos_core/schemas/response_envelope.py (5필드 LOCK)
  - backend/vamos_core/schemas/workflow_stage.py (4필드 LOCK)
  - backend/vamos_core/schemas/workflow_output.py (3필드 LOCK)
  - scripts/generate_types.py
[Post-check] impl_status.json 갱신 완료
[Post-check] 다음: V0-STEP-3 (IPC 통신 레이어)
[Post-check] 다음 단계 선행조건: 위 스키마 파일 4개 + generate_types.py 존재
```

---

## §2 LOCK 값 빠른 참조 테이블

> v26.0.0 동기화 확인 — LOCK 값 40개 변경 없음 (2026-03-15)

### 2.1 전 단계 공통 LOCK

| # | LOCK 키 | 값 | 근거 | PART2 위치 |
|---|---------|-----|------|-----------|
| 1 | python_version | 3.11+ | PHASE_B3 | §2 STEP-1 |
| 2 | langgraph_import | `from langgraph.graph import StateGraph, START, END` | FG-M04 | 코드블록 전체 |
| 3 | structlog_import | `import logging` (structlog 호환) | FG-M04 | 코드블록 전체 |
| 4 | basemodel_import | `from pydantic import BaseModel, ConfigDict` | FG-M04 | 코드블록 전체 |
| 5 | set_entry_point | **금지** — START/END 상수 사용 | FG-H06 | §전체 |
| 6 | rust_ok_or | `ok_or` (not `ok_or_else`) | FG-H06 | §전체 |
| 7 | log_format | `json` (평문 금지) | PHASE_B4 §3.12 | L318 |
| 8 | trace_id_required | `true` | PHASE_B4 §3.12 | L319 |
| 9 | single_decision_lock | `true` | PHASE_B4 §3.1 | L250 |
| 10 | mcp_transport | `streamable_http` | PHASE_B4 §3.9 | L309 |

### 2.2 V0 LOCK

| # | LOCK 키 | 값 | 근거 |
|---|---------|-----|------|
| 11 | autonomy_level_v0 | `L1` (V0 초기) | PHASE_B4 §3.1 |
| 12 | config_load_order | TOML → ENV → CLI | V0-STEP-5 |

### 2.3 V1 LOCK

| # | LOCK 키 | 값 | 근거 |
|---|---------|-----|------|
| 13 | autonomy_level_v1 | `L2_COPILOT` | FG-H05 Canonical Decision B |
| 14 | max_turns | 50 | FG-H05 Canonical Decision A |
| 15 | cost_monthly_v1 | ₩40,000 (ABSOLUTE) | PHASE_B4 §3.7 |
| 16 | cost_alarm_stages | 3단계 (70/85/95%) | FG-B01 Canonical Decision B |
| 17 | approval_state | S3a_APPROVE (분리) | FG-B04 Canonical Decision B |
| 18 | approval_timeout | 600s (10분) | PHASE_B4 §3.8b |
| 19 | self_check_p0/p1/p2 | 70/75/80 | PHASE_B4 §3.8a |
| 20 | soft_loop_max | 1 | PHASE_B4 §3.8a |
| 21 | 5gate_order | Policy→Approval→Cost→Evidence→SelfCheck | D2.0-02 |
| 22 | 9state_order | S0→S1→S2→S3→(S3a)→S4→S5→S6→S7→S8 | D2.0-02 §2.2 |
| 23 | embedding_model | bge-m3 (1024dim, Matryoshka 256) | PHASE_B4 §3.3 |
| 24 | semantic_cache | cosine ≥ 0.95 | D2.1-D6 |
| 25 | bl_mapping | B-1→L1, B-2→L3, B-3→L2, B-4→L0 | D2.0-06 §2.1 |
| 26 | rag_stages | 6-Stage (Collect→Chunk→Embed→Store→Retrieve→Generate) | D2.0-06 §1.1 |
| 27 | hybrid_search_alpha | 0.7 dense / 0.3 sparse | D2.0-06 S7D-012 |
| 28 | circuit_breaker | failure=3, recovery=60s | D2.0-05 §4.4 |
| 29 | agent_teams_v1 | max 2 Sub-Agent | LOCK-AT-014 |
| 30 | failover_order | GPT-4o→Claude→Ollama | D2.0-04 §3 |

### 2.4 V2 LOCK

| # | LOCK 키 | 값 | 근거 |
|---|---------|-----|------|
| 31 | cost_monthly_v2 | ₩93,000 | §4 헤더 |
| 32 | migration_principles | 6항 (Zero Loss/Rollback/Verify/Backup/Incremental/Version Pin) | PHASE_B7 §1.2 |
| 33 | agent_teams_v2 | max 10 에이전트 | LOCK-AT-014 |
| 34 | hmac_auth | HMAC-SHA256 필수 | LOCK-AT-012 |
| 35 | guardrails_v2 | L1+L2+L3 (L4는 V3) | D2.0-07 ADD-015 |
| 36 | collab_patterns | 6개 (Sequential/Parallel/Debate/Supervisor/Handoff/Hybrid) | AGENT_TEAMS_SPEC §5 + §7(enum) |

### 2.5 V3 LOCK

| # | LOCK 키 | 값 | 근거 |
|---|---------|-----|------|
| 37 | cost_monthly_v3 | ₩266,000 ≈ $200 (ABSOLUTE) | §5 헤더 |
| 38 | agent_teams_v3 | max 50+ (PARL 모드 최대 100) | LOCK-AT-014 |
| 39 | lead_agent_principle | Lead Agent 단일결정 원칙 유지 | LOCK-AT-002 |
| 40 | guardrails_v3 | L1+L2+L3+L4 (전체) | D2.0-07 |

---

## §3 Naming Convention

### 3.1 파일명 규칙

| 유형 | 패턴 | 예시 | 근거 |
|------|------|------|------|
| I-Series 모듈 | `i{번호:02d}_{영문명}.py` | `i01_intent_detector.py` | M-7 매핑 테이블 (V1-PH1) |
| E-Series 모듈 | `e{번호:02d}_{영문명}.py` | `e07_stt.py` | V3-PH2 AI 프롬프트 |
| S-Series 모듈 | `s{번호:02d}_{영문명}.py` | `s02_pattern_miner.py` | V3-PH2 AI 프롬프트 |
| A-Series 모듈 | `a{번호:02d}_{영문명}.py` | `a03_meta_ai.py` | V3-PH2 AI 프롬프트 |
| B-Series 모듈 | `b{번호:02d}_{영문명}.py` | `b01_skill_library.py` | V3-PH2 AI 프롬프트 |
| C-Series 모듈 | `c{번호:02d}_{영문명}.py` | `c05_bayesian.py` | V3-PH2 AI 프롬프트 |
| D-Series 모듈 | `d{번호:02d}_{영문명}.py` | `d06_graphrag.py` | V3-PH2 AI 프롬프트 |
| EVX-Series | `evx{번호:02d}_{영문명}.py` | `evx01_code_as_policy.py` | V3-PH2 AI 프롬프트 |
| 스키마 | `{도메인}_schema.py` | `decision_schema.py` | D2.1-D1~D8 |
| 마이그레이션 | `{소스}_to_{타겟}.py` | `sqlite_to_pg.py` | V2-PH1 AI 프롬프트 |
| 테스트 | `test_{module}.py` | `test_i01_intent_detector.py` | PHASE_B5 |
| Config | `config.v{버전}.toml` | `config.v1.toml` | PHASE_B4 |

### 3.2 코드 네이밍 (R1 기반)

| 유형 | 패턴 | 예시 |
|------|------|------|
| 변수 | snake_case | `event_count`, `max_retries` |
| 함수 | snake_case | `async def process_event()` |
| 클래스 | PascalCase | `IntentDetector`, `DecisionEngine` |
| 상수 | UPPER_SNAKE | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| Pydantic 모델 | PascalCase + Schema | `DecisionSchema`, `ResponseEnvelope` |
| Enum | PascalCase | `WorkflowStage`, `GateResult` |
| 이벤트 타입 | DOMAIN.ACTION | `config.updated`, `gate.denied` |
| 상태값 | S{번호}_{설명} | `S0_RECEIVED`, `S3a_APPROVE_WAIT` |

### 3.3 디렉터리 구조 (PHASE_B2 정본 + PART2 §2 인라인)

```
vamos/
├── src/                    # React 18 + TypeScript
├── src-tauri/              # Rust Tauri 2.0
├── backend/
│   ├── vamos_core/
│   │   ├── orange_core/    # I-Series (i01~i24)
│   │   ├── blue_nodes/     # E-Series (e01~e16)
│   │   ├── infra/          # A-Series (a01~a07)
│   │   ├── agent/          # Agent Teams
│   │   ├── storage/        # 메모리/저장소
│   │   ├── safety/         # Gate, Guardrails
│   │   ├── schemas/        # Pydantic v2 스키마
│   │   ├── mcp/            # MCP 브릿지
│   │   ├── rpc/            # JSON-RPC server
│   │   ├── self_evo/       # S-Series (s01~s08, V3)
│   │   ├── learning/       # B-Series (b01~b06, V3)
│   │   ├── reasoning/      # C-Series (c01~c07, V3)
│   │   ├── generation/     # D-Series (d01~d06, V3)
│   │   └── experimental/   # EVX-Series (V3)
│   └── tests/
├── config/
├── data/
├── logs/
├── scripts/
├── deploy/                 # V2+ K8s/Docker
├── CLAUDE.md               # 구현 스킬 에이전트
└── impl_status.json        # 상태 추적
```

---

## §4 impl_status.json 스키마 정의

```json
{
  "project": "VAMOS",
  "part2_version": "v26.0.0",
  "current_step": "V0-STEP-2",
  "completed": {
    "V0-STEP-1": {
      "stage_gate_result": "PASS",
      "stage_gate_detail": "16/16",
      "files_created": [
        "config/config.v1.toml",
        "backend/vamos_core/__init__.py",
        "pyproject.toml",
        "src-tauri/Cargo.toml",
        "src-tauri/tauri.conf.json",
        "scripts/generate_types.py",
        "CLAUDE.md"
      ],
      "lock_values_verified": 17,
      "key_decisions": [
        "monorepo 구조: PHASE_B2 정본 기준",
        "config 로딩: TOML → ENV → CLI"
      ],
      "completed_at": "2026-03-14"
    }
  },
  "next_prerequisites": [
    "config/config.v1.toml 존재",
    "backend/vamos_core/__init__.py 존재",
    "schemas/seed/ 디렉터리에 D2.1 기반 초기 스키마 존재"
  ],
  "lock_values": {
    "autonomy_level": "L1",
    "cost_monthly": 40000,
    "cost_alarm_thresholds": [70, 85, 95],
    "max_turns": 50,
    "approval_state": "S3a_APPROVE",
    "approval_timeout_s": 600,
    "self_check_thresholds": { "P0": 70, "P1": 75, "P2": 80 },
    "soft_loop_max": 1,
    "embedding_model": "bge-m3",
    "embedding_dim": 1024,
    "matryoshka_dim": 256,
    "semantic_cache_threshold": 0.95,
    "circuit_breaker_failure": 3,
    "circuit_breaker_recovery_s": 60,
    "agent_max_sub": 2,
    "failover_order": ["GPT-4o", "Claude", "Ollama"],
    "mcp_transport": "streamable_http"
  },
  "module_status": {
    "I-1": { "status": "completed", "file": "i01_intent_detector.py", "stage": "V1-PH1" },
    "I-2": { "status": "pending", "file": "i02_context_builder.py", "stage": "V1-PH1" }
  },
  "decisions_log": [
    {
      "id": "FG-B01",
      "decision": "3단계 비용 알람 (70/85/95%)",
      "date": "2026-03-12"
    },
    {
      "id": "FG-H05",
      "decision": "L2_COPILOT + max_turns=50",
      "date": "2026-03-12"
    }
  ],
  "last_updated": "2026-03-14"
}
```

**자동 갱신 규칙**:
- 세션 시작 시: `current_step` 읽기
- 세션 종료 시: `completed`에 해당 단계 추가, `current_step` 다음 단계로 갱신
- 파일 생성 시: `files_created`에 경로 추가
- 결정 발생 시: `decisions_log`에 추가

---

## §5 단계별 입출력 요약 (PART2 §2~§5 크로스레퍼런스)

### 5.1 V0 (§2, L182~L1584)

| STEP | 입력 SOT | 주요 출력 | AI 프롬프트 | 파일경로 명시 |
|------|---------|----------|:----------:|:------------:|
| **STEP-1** (스캐폴딩) | PHASE_B2, B3, B4 | monorepo 구조, config.v1.toml, 의존성 | ✅ 상세 (L342~551) | ✅ 인라인 |
| **STEP-2** (스키마) | D2.1-D1~D8 | Pydantic 모델, TypeScript 타입, 레지스트리 | ✅ 상세 (L649~809) | ✅ 인라인 |
| **STEP-3** (IPC) | PHASE_B1, D2.0-04, D2.0-01 | JSON-RPC, Tauri IPC, 프로세스 관리 | ✅ 상세 (L881~975) | ✅ 인라인 |
| **STEP-4** (CORE 파이프라인) | D2.0-02, D2.0-05 | I-1~I-5 stub, LangGraph 5-Phase, Gate | ✅ 상세 (L1067~1181) | ✅ 인라인 |
| **STEP-5** (저장소+로깅) | D2.0-06, D2.0-04 | SQLite L0/L1, Chroma, JSONL 로깅 | ✅ 상세 (L1229~1353) | ✅ 인라인 |
| **STEP-6** (CI+테스트) | PHASE_B5, B6 | pytest, cargo test, CI 워크플로우 | ✅ 상세 (L1400~1549) | ✅ 인라인 |

**V0 평가**: 6개 STEP 모두 **상세 AI 프롬프트 + 인라인 파일경로** 포함. 커버리지 최고.

### 5.2 V1 (§3, L1585~L2676)

| Phase | 입력 SOT | 주요 출력 | AI 프롬프트 | 파일경로 명시 |
|-------|---------|----------|:----------:|:------------:|
| **Phase 1** (CORE 17모듈) | D2.0-02 §7, D2.0-07, D2.1-D2 | 17개 I-모듈 .py 파일 | ✅ 상세 (L1616~1777) | ✅ M-7 테이블 |
| **Phase 2** (Storage+RAG) | D2.0-06, D2.1-A1, D2.1-D6 | L0/L1 메모리, Chroma, GraphRAG, Cache | ✅ 상세 (v26.0.0 동기화) | ✅ 인라인 |
| **Phase 3** (Workflow+Agent) | D2.0-05, D2.0-04, D2.0-03, D2.0-07 | LangGraph, E-1~E-6, Agent Teams V1 | ✅ 상세 (v26.0.0 동기화) | ✅ 인라인 |
| **Phase 4** (UI/UX) | D2.0-08, PHASE_B2 | 44개 컴포넌트, 8 Hook, 7 Store | ✅ 상세 (v26.0.0 동기화) | ✅ 인라인 |
| **Phase 5** (Integration+Test) | PHASE_B5, B6 | ~85개 테스트, CI/CD, 커버리지 80%+ | ✅ 상세 (v26.0.0 동기화) | ✅ 인라인 |
| **Phase 6** (AI Investing+MCP) | D2.0-01 §5.9, D2.0-03, §6.8, §6.6 | Paper Trading, MCP, S-1 Engine | ✅ 상세 (v26.0.0 동기화) | ✅ 인라인 |

> **참고**: v25.2.0에서 V1 전체 Phase(1~6)에 대한 상세 구현 가이드가 완성되었고, v26.0.0에서 추가 보강되었습니다. V1에서 3건(BLOCKER 2건: §3.P2, §3.P4 / HIGH 1건: §3.P2) 반영 완료.

**V1 평가**:
- Phase 1: v25.2.0에서 ~161줄 상세 AI 프롬프트 추가 (L1616~1777) + M-7 파일명 테이블 (17개 모듈 파일명+의존성+SOT 전부 명시)
- Phase 2: v26.0.0에서 BLOCKER 1건(§3.P2) 해소 → ✅ 완비
- Phase 4: v26.0.0에서 BLOCKER 1건(§3.P4) 해소 → ✅ 완비
- Phase 2~6 전체: v26.0.0 동기화로 **상세 프롬프트 + 인라인 파일경로** 완비 → 커버리지 최고

### 5.3 V2 (§4, L2677~L3461)

| Phase | 입력 SOT | 주요 출력 | AI 프롬프트 | 파일경로 명시 |
|-------|---------|----------|:----------:|:------------:|
| **Phase 1** (인프라 마이그레이션) | PHASE_B7, B6, B4 | 마이그레이션 스크립트 4개, Docker Compose, 배포 | ✅ 상세 (L2751~2831) | ✅ 인라인 |
| **Phase 2** (COND 모듈 116개) | D2.0-01 §5.6, D2.0-02, D2.0-03 | COND 모듈 10개+v10 106개, config.v2.toml COND 섹션 | ✅ 상세 (L3005~3247) | ✅ 인라인 |
| **Phase 3** (Agent Teams V2+보안) | AGENT_TEAMS_SPEC, D2.0-07, SDAR_SPEC, CLOUD_LIBRARY_SPEC | Redis MessageBus, HMAC, LlamaGuard, GDPR | ✅ 상세 (L3328~3425) | ✅ 인라인 |

**V2 평가**: 3개 Phase 모두 **상세 AI 프롬프트 + 인라인 파일경로**. v26.0.0에서 175건(BLOCKER 7건 + 다수 HIGH/MEDIUM/LOW) 반영 → 커버리지 최고.

### 5.4 V3 (§5, L3462~L4174)

| Phase | 입력 SOT | 주요 출력 | AI 프롬프트 | 파일경로 명시 |
|-------|---------|----------|:----------:|:------------:|
| **Phase 1** (인프라 스케일업) | PHASE_B6, B3, B4, D2.0-07 | K8s Helm, vLLM, 관리형 DB, Loki+Grafana | ✅ 상세 (L3509~3618) | ✅ 인라인 |
| **Phase 2** (EXP 모듈 39개) | D2.0-01~03, D2.0-06 | 22개 그룹(I/S/E/A/B/C/D/EVX), PARL Swarm | ✅ 매우 상세 (L3700~3947) | ✅ I/O 타입까지 |
| **Phase 3** (고급 기능+최종통합) | AGENT_TEAMS_SPEC §8, SDAR_SPEC, D2.0-01 §5.8 | Marketplace, 50+ Mesh, Governance, SDAR L4 | ✅ 상세 (L4031~4142) | ✅ 인라인 |

**V3 평가**: 3개 Phase 모두 **매우 상세한 AI 프롬프트** (특히 Phase 2는 I/O 타입, 핵심 함수 시그니처까지 명시). v26.0.0에서 12건 추가 반영 → 커버리지 최고.

---

## 왜 이 구조가 "같은 결과"를 보장하는가

| 불일치 원인 | 스킬 에이전트의 방어 |
|------------|-------------------|
| 세션이 이전 결과를 모름 | impl_status.json에서 파일 목록/경로 로드 |
| LOCK 값을 다르게 사용 | §2 LOCK 빠른 참조 테이블로 즉시 대조 |
| 파일명이 달라짐 | §3 naming convention 강제 (예: `i01_intent_detector.py`) |
| 클래스명이 달라짐 | D2.1 스키마 + Pydantic 모델명 고정 |
| 단계를 건너뜀 | Pre-check에서 이전 Stage Gate 미통과 시 차단 |
| AI가 다른 구조로 코드 생성 | PART2 프롬프트 + 규칙을 스킬이 강제 주입 |
| import 경로 오류 | Guard에서 LOCK된 import 패턴 강제 |

### 100% 동일은 불가능 — 하지만 "구조적 동일"은 가능

**100% 동일 불가능한 것** (AI 특성):
- 함수 내부의 정확한 코드 라인 순서
- 변수 이름의 미세한 차이 (result vs res)
- 주석 내용

**구조적 동일 가능한 것** (스킬 에이전트로 강제):
- ✅ 디렉터리 구조 — PHASE_B2에 고정
- ✅ 파일 이름 — M-7 매핑 테이블 + naming convention에 고정
- ✅ 클래스/스키마 이름 — D2.1 스키마에 고정
- ✅ config 값 — LOCK으로 고정
- ✅ API 시그니처 — SOT 문서에 고정
- ✅ 테스트 구조 — Stage Gate에 고정
- ✅ 의존성 버전 — pyproject.toml에 고정
- ✅ Gate 순서 — LOCK으로 고정
- ✅ 상태 머신 전이 — 9-State LOCK으로 고정

---

## 추천 진행 순서

```
1단계: 본 문서 (v12_impl_skill_agent.md) 리뷰 → 보완 사항 확인
2단계: V0-STEP-1 시작 시:
       → CLAUDE.md 생성 (§1~§3 내용 기반)
       → impl_status.json 초기 생성 (§4 스키마 기반)
3단계: V0-STEP-1 실행 (스킬 에이전트 로드 상태에서)
4단계: Post-check → impl_status.json 갱신 → V0-STEP-2로 진행
```

---

## 구현 시 만들어야 할 파일 2개

### 파일 1: `CLAUDE.md` (프로젝트 루트)
- 역할: Claude Code가 매 세션 자동 로드하는 영구 지시사항
- 내용: §1 프로토콜 + §2 LOCK 테이블 + §3 Naming 규칙 (핵심만, ~200줄)
- 생성 시점: V0-STEP-1

### 파일 2: `impl_status.json` (프로젝트 루트)
- 역할: 세션 간 상태 추적
- 내용: §4 스키마 기반 초기 상태
- 생성 시점: V0-STEP-1
- 갱신 시점: 매 세션 Post-check

---

*파일: D:\VAMOS\04. 구현단계\v12\v12_impl_skill_agent.md*
