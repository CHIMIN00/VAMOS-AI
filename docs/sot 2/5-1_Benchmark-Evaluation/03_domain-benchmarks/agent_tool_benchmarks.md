# Agent/Tool Benchmarks — 도메인 벤치마크 채점 규칙 및 실행 파라미터

> **Phase**: 1-B (P1-2)
> **범위**: S7G-027 (BFCL v3), S7G-028 (τ-bench)
> **작성일**: 2026-04-12
> **상태**: V1 정의 완료

---

## 교차 참조 블록

| 정본 문서 | 참조 내용 |
|-----------|----------|
| STEP7-G S7G-027~028 | Part 4 Agent/Tool 벤치마크 목표값/평가 방식/우선순위 |
| BENCHMARK_EVALUATION_상세명세.md §C | VBS-12 Agent Benchmark 메트릭 정의 |
| AUTHORITY_CHAIN.md | LOCK-BE-08 (seed=42), LOCK-BE-06 (Bootstrap 95% CI) |
| CONFLICT_LOG | 해당 항목 충돌 없음 |
| Phase 0 F-01 | benchmark_runner.py — 러너 프레임워크 |
| Phase 0 F-02 | schemas/benchmark_result.schema.json — 결과 스키마 |
| Phase 0 F-07 | benchmark_store/ — 결과 저장소 |
| 03_domain-benchmarks/_index.md | S7G-027 MCP Tool 정확도 ≥ 88%, S7G-028 대화형 Agent 완수율 |
| **R-T5-1 횡단 정본 원칙** | **Agent 도메인(3-10_Agent-Protocol)** — 정본 소유자. Task completion, Tool selection 정의권 |
| R-18-5 공동 관리 | VBS-12 Agent는 3-10_Agent-Protocol(정본) + 5-1_Benchmark(실행 인프라) 공동 관리 |

---

## S7G-027: BFCL v3 (Berkeley Function Calling Leaderboard)

### 개요

| 항목 | 값 |
|------|-----|
| **ID** | S7G-027 |
| **우선순위** | CRITICAL |
| **버전** | V1 |
| **LOCK** | — (LOCK-BE 미등록; 종합계획서 목표 ≥ 80%, _index.md 목표 MCP Tool 정확도 ≥ 88%) |
| **정본 소유자** | 3-10_Agent-Protocol (R-T5-1) |

> **[CONFLICT_CANDIDATE: S7G-027 목표값 불일치 — 종합계획서 Phase 1-B에서 "≥ 80%", _index.md에서 "MCP Tool 정확도 ≥ 88%". 8%p 차이. STEP7-G 정본 확인 필요]**

### 입력 포맷

```
System: You are an AI assistant with access to the following tools:
{tool_definitions}  # JSON Schema function descriptions

User: {user_query}

Available tools:
- {tool_1}: {description_1}
- {tool_2}: {description_2}
...

Please call the appropriate tool(s) to fulfill the user's request.
```

- **데이터셋**: BFCL v3 공개 테스트셋 (2,000+ 호출 시나리오)
  - Simple Function Call: 단일 함수 호출 (800건)
  - Multiple Function Call: 다중 함수 호출 (500건)
  - Parallel Function Call: 병렬 함수 호출 (400건)
  - Relevance Detection: 무관 요청 거부 (300건)
- **V1 골든셋**: 100건 (카테고리별 층화 추출 seed=42)
- **MCP 확장**: VAMOS MCP 프로토콜 도구 정의를 BFCL 포맷으로 변환하여 평가

### 채점 방식

1. **함수명 일치**: 호출된 함수명 exact match
2. **파라미터 일치**: JSON Schema 기반 파라미터 값 비교
   - 필수 파라미터: 전수 일치 필수
   - 선택 파라미터: 제공 시 값 일치 확인
   - 타입 검증: JSON Schema type 기반 strict validation
3. **카테고리별 점수**:
   - Simple: exact match (함수명 + 파라미터)
   - Multiple: 순서 무관 set match
   - Parallel: 순서 무관 set match + 독립 실행 가능 여부
   - Relevance: 도구 미호출 시 정답 (거부 정확도)
4. **전체 점수**: 카테고리별 가중 평균 (Simple 30%, Multiple 25%, Parallel 25%, Relevance 20%)
5. **신뢰구간**: Bootstrap 95% CI (LOCK-BE-06: B=5000, n>1000)

### 실행 파라미터

```yaml
benchmark_id: S7G-027
name: BFCL_v3
type: function_calling
model: ${MODEL_ID}
temperature: 0       # R-18-1
seed: 42             # LOCK-BE-08
max_tokens: 1024     # 함수 호출 JSON 응답
dataset_size: 2000
golden_set_size: 100
scoring: weighted_accuracy
aggregation: weighted_average
weights:
  simple: 0.30
  multiple: 0.25
  parallel: 0.25
  relevance: 0.20
ci_method: bootstrap
ci_level: 0.95
ci_bootstrap_b: 5000  # n=2000 > 1000 → B=5000
timeout_seconds: 15    # per call scenario
```

### PASS/FAIL 판정

| 구간 | 판정 | 조건 |
|------|------|------|
| score ≥ 88% | **PASS** | _index.md 정본 충족 (CONFLICT_LOG C-14 RESOLVED) |
| 77% ≤ score < 80% | **BORDERLINE** | CI 상한이 80% 이상이면 조건부 PASS |
| score < 77% | **FAIL** | 목표 미충족 |

> 참고: _index.md의 ≥ 88%와 차이 있음. STEP7-G 정본 확인 후 최종 임계값 결정 필요.

### 로깅 포맷 (R-01-7)

```json
{
  "trace_id": "bench-bfcl-{run_id}",
  "benchmark": "S7G-027",
  "timestamp": "{ISO-8601}",
  "error": {
    "code": null,
    "message": null,
    "parse_failures": 0,
    "schema_validation_errors": 0
  },
  "context": {
    "model_id": "{model_version}",
    "seed": 42,
    "dataset_size": 2000,
    "environment": "{os/python/gpu}",
    "mcp_tools_version": "{mcp_schema_hash}"
  },
  "recovery": {
    "retry_count": 0,
    "fallback_used": false,
    "json_repair_applied": false
  }
}
```

### 에스컬레이션 (I-20 경유, R-01-8)

```json
{
  "escalation_type": "BENCHMARK_THRESHOLD_BREACH",
  "benchmark_id": "S7G-027",
  "lock_id": "N/A",
  "threshold": 0.80,
  "actual": "{score}",
  "ci_lower": "{ci_low}",
  "ci_upper": "{ci_high}",
  "severity": "CRITICAL",
  "route": "I-20 → QA-GATE → AGENT-DOMAIN-REVIEW",
  "cross_domain_notify": ["3-10_Agent-Protocol"]
}
```

### benchmark_runner 등록 (F-01 인터페이스)

```python
runner.register(
    benchmark_id="S7G-027",
    name="BFCL_v3",
    runner_fn=run_bfcl_v3,
    scorer_fn=score_bfcl_weighted,
    dataset_path="datasets/domain/bfcl_v3/",
    result_schema="BenchmarkResult",  # F-02
    store_target="benchmark_store",    # F-07
)
```

### BenchmarkResult 스키마 매핑 (F-02)

```json
{
  "benchmark_name": "BFCL_v3",
  "model_id": "{model_version}",
  "run_date": "{ISO-8601}",
  "score": 0.0,
  "confidence_interval": {
    "lower": 0.0,
    "upper": 0.0,
    "confidence_level": 0.95,
    "n": 2000,
    "B": 5000,
    "type": "bootstrap"
  },
  "metadata": {
    "seed": 42,
    "system_prompt_hash": "sha256:{hex64}",
    "dataset_version": "bfcl_v3_2026q1",
    "golden_set_used": true,
    "category_scores": {
      "simple": 0.0,
      "multiple": 0.0,
      "parallel": 0.0,
      "relevance": 0.0
    }
  }
}
```

---

## S7G-028: τ-bench (Tau-bench)

### 개요

| 항목 | 값 |
|------|-----|
| **ID** | S7G-028 |
| **우선순위** | CRITICAL |
| **버전** | V1 |
| **LOCK** | — (LOCK-BE 미등록; 종합계획서 목표 ≥ 70%) |
| **정본 소유자** | 3-10_Agent-Protocol (R-T5-1), 3-8_Conversation-A2A (참조) |

### 입력 포맷

```
Environment: {environment_description}
  - Database state: {db_snapshot}
  - Available actions: {action_list}

User conversation history:
  Turn 1: {user_message_1}
  Agent 1: {agent_response_1}
  ...
  Turn N: {user_message_n}

Task: Complete the user's request using the available actions.
Expected final state: {expected_db_state}
```

- **데이터셋**: τ-bench 공개 환경 2종
  - Airline (항공 예약/변경/취소): 100 시나리오
  - Retail (온라인 쇼핑 주문/반품): 100 시나리오
- **V1 골든셋**: 50건 (환경별 25건씩 seed=42)
- **대화 턴 수**: 평균 5~12턴 (복합 시나리오)

### 채점 방식

1. **작업 완료 판정**: 최종 DB 상태와 기대 상태 비교
   - 필수 상태 변경: 전수 일치 필수
   - 부수 효과(side effect): 비허용 변경 없음 확인
2. **부분 점수**: 없음 (pass or fail per scenario)
3. **재시도 허용**: 최대 3회 (pass@3)
4. **환경별 점수**: pass rate per environment
5. **전체 점수**: 환경 가중 평균 (Airline 50%, Retail 50%)
6. **신뢰구간**: Bootstrap 95% CI (LOCK-BE-06: B=10000, n<100)

### 실행 파라미터

```yaml
benchmark_id: S7G-028
name: tau_bench
type: agent_interaction
model: ${MODEL_ID}
temperature: 0       # R-18-1
seed: 42             # LOCK-BE-08
max_tokens: 2048     # 다중 턴 응답
max_turns: 20        # 대화 턴 제한
dataset_size: 200
golden_set_size: 50
scoring: pass_fail
aggregation: weighted_average
weights:
  airline: 0.50
  retail: 0.50
ci_method: bootstrap
ci_level: 0.95
ci_bootstrap_b: 10000  # n=50 < 100 → B=10000
timeout_seconds: 120    # per scenario (다중 턴)
```

### PASS/FAIL 판정

| 구간 | 판정 | 조건 |
|------|------|------|
| score ≥ 70% | **PASS** | 종합계획서 목표 충족 |
| 65% ≤ score < 70% | **BORDERLINE** | CI 상한이 70% 이상이면 조건부 PASS |
| score < 65% | **FAIL** | 목표 미충족 |

### 로깅 포맷 (R-01-7)

```json
{
  "trace_id": "bench-tau-{run_id}",
  "benchmark": "S7G-028",
  "timestamp": "{ISO-8601}",
  "error": {
    "code": null,
    "message": null,
    "environment_setup_failures": 0,
    "db_state_mismatch_count": 0
  },
  "context": {
    "model_id": "{model_version}",
    "seed": 42,
    "environment": "{airline|retail}",
    "avg_turns": 0,
    "max_turns_hit": 0,
    "dataset_size": 50
  },
  "recovery": {
    "retry_count": 0,
    "fallback_used": false,
    "db_rollback_count": 0
  }
}
```

### 에스컬레이션 (I-20 경유, R-01-8)

```json
{
  "escalation_type": "BENCHMARK_THRESHOLD_BREACH",
  "benchmark_id": "S7G-028",
  "lock_id": "N/A",
  "threshold": 0.70,
  "actual": "{score}",
  "ci_lower": "{ci_low}",
  "ci_upper": "{ci_high}",
  "severity": "CRITICAL",
  "route": "I-20 → QA-GATE → AGENT-DOMAIN-REVIEW",
  "cross_domain_notify": ["3-10_Agent-Protocol", "3-8_Conversation-A2A"]
}
```

### benchmark_runner 등록 (F-01 인터페이스)

```python
runner.register(
    benchmark_id="S7G-028",
    name="tau_bench",
    runner_fn=run_tau_bench,
    scorer_fn=score_tau_db_state,
    dataset_path="datasets/domain/tau_bench/",
    result_schema="BenchmarkResult",
    store_target="benchmark_store",
)
```

### BenchmarkResult 스키마 매핑 (F-02)

```json
{
  "benchmark_name": "tau_bench",
  "model_id": "{model_version}",
  "run_date": "{ISO-8601}",
  "score": 0.0,
  "confidence_interval": {
    "lower": 0.0,
    "upper": 0.0,
    "confidence_level": 0.95,
    "n": 200,
    "B": 10000,
    "type": "bootstrap"
  },
  "metadata": {
    "seed": 42,
    "system_prompt_hash": "sha256:{hex64}",
    "dataset_version": "tau_bench_v1_2026q1",
    "golden_set_used": true,
    "environment_scores": {
      "airline": 0.0,
      "retail": 0.0
    },
    "avg_turns": 0
  }
}
```

---

## 예외 처리 정책 표

| 예외 상황 | 처리 정책 | 심각도 | 복구 방법 |
|-----------|----------|--------|----------|
| 함수 호출 JSON 파싱 실패 (S7G-027) | 해당 시나리오 FAIL 처리 | WARN | JSON repair 1회 시도 후 재파싱, 실패 시 FAIL |
| 도구 정의 스키마 로드 실패 | 벤치마크 전체 ABORT | CRITICAL | 스키마 파일 경로 검증 + 재로드 |
| τ-bench 환경 초기화 실패 (S7G-028) | 해당 환경 SKIP + 알림 | HIGH | DB 스냅샷 복원 후 재시도 (최대 2회) |
| max_turns 초과 (S7G-028) | 해당 시나리오 FAIL | WARN | 로그에 턴 수 기록, 임계값 조정 검토 |
| API 타임아웃 | 해당 항목 재시도 (최대 3회) | WARN | 지수 백오프 (2s, 4s, 8s) |
| 모델 Rate Limit | 배치 실행 일시 중단 | WARN | 60s 대기 후 재개, 동시 요청 수 감소 |

---

## Phase 2 테스트 시나리오

| # | 시나리오 | 검증 대상 | 기대 결과 |
|---|---------|----------|----------|
| 1 | BFCL v3 전수 실행 (2000건) | E2E 실행 완료 + 결과 저장 | score ≥ 80%, benchmark_store 적재 |
| 2 | BFCL 카테고리별 점수 검증 | 가중 평균 정확성 | 4개 카테고리 개별 점수 + 가중합 일치 |
| 3 | BFCL MCP 도구 정의 호환성 | VAMOS MCP 스키마 → BFCL 포맷 변환 | 변환 오류 0건, 도구 커버리지 100% |
| 4 | τ-bench Airline 환경 E2E | 항공 예약 시나리오 자동 완료 | pass rate ≥ 70%, DB 상태 일치 |
| 5 | τ-bench Retail 환경 E2E | 쇼핑 주문 시나리오 자동 완료 | pass rate ≥ 70%, DB 상태 일치 |
| 6 | τ-bench 다중 턴 안정성 | 12+ 턴 시나리오 | max_turns 미초과, 정상 완료 |
| 7 | BFCL Relevance Detection | 무관 요청 거부 정확도 | 거부율 ≥ 90% |
| 8 | 회귀 테스트 연동 | 이전 실행 대비 3% 이상 하락 감지 | LOCK-BE-14 알림 발송 |
| 9 | CI 파이프라인 통합 | PR 트리거 시 골든셋 50건 자동 실행 | 5분 이내 완료, PASS/FAIL 판정 |
| 10 | benchmark_store 적재 검증 | 결과 JSON → SQLite/Parquet 저장 | F-07 CRUD 라운드트립 성공 |
| 11 | 교차 도메인 알림 | FAIL 시 3-10 Agent-Protocol 알림 | 에스컬레이션 페이로드 전송 확인 |
| 12 | Bootstrap CI 정확성 | 50건 골든셋 CI 계산 | B=10000, 95% CI 범위 합리성 검증 |

---

## Phase 4 §확장 (V3-Phase 4 production-ready, RECOVERY genuine write 2026-06-03)

> **Status**: **APPROVED** | **scope**: P4-6 그룹 3 (에이전트). V1/V2 본문(상기) byte 무변경 prefix EXACT.

### S7G-032 WebArena / VisualWebArena — 웹 자동화 평가
- **내용**: 웹 브라우저 통한 작업 수행 능력 (Computer Use / GUI Agent 품질). V3 웹 기반 작업 자동화 핵심 벤치마크.

### S7G-033 OSWorld — OS 조작 Agent 평가
- **내용**: OS 수준 작업(파일/앱/설정) 수행 능력. V3 데스크톱 자동화 기능 평가.

### S7G-034 MLE-bench — ML 엔지니어링 Agent 평가
- **내용**: Kaggle 대회 수준 ML 파이프라인 구축 능력. Quant Node ML 모델 구축 기준.

- **3-10 Agent-Protocol cross-domain 측정 위임 (R-T5-1)**: S7G-032~034 V3 측정 위임, source 0 touch. **LOCK 재정의 0**. S7G-032/033/034 = DONE.
