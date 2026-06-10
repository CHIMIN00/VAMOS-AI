# D-1 Think Engine — Monitoring Metrics

> **Status**: APPROVED
> **버전**: v1.1
> **작성일**: 2026-04-18
> **Last-reviewed**: 2026-06-02 (Phase 4 production promotion RECOVERY Sub-B P4-6 — DRAFT → APPROVED 정식 승급 + ReadOnly TRUE 진입)
> **Phase**: Phase 2 (P2-7, V2-Phase 2)
> **Owner**: 1-1_Verifier-Reasoning-Engines
> **Level**: L3 (메트릭 정의 + 알림 임계값 + 대시보드 가이드)

---

## 1. 교차 참조 (Cross-References)

| 항목 | 참조 | 용도 |
|------|------|------|
| 종합계획서 §7 | P2-7 | 대조 기준 5건 |
| LOCK 정본 | `AUTHORITY_CHAIN.md` §4 LOCK-VR-01, VR-04, VR-05, VR-07, VR-08, VR-12 | 임계값/상태머신/판정/failover/토큰/SLA |
| Spec | `04_think-engine/spec.md` | D-1 인터페이스 |
| Reasoning strategies | `04_think-engine/reasoning_strategies.md` | CoT/ToT/GoT/Auto 전략 |
| State machine | `04_think-engine/state_machine.md` | S0~S8 (LOCK-VR-04) |
| Error handling | `04_think-engine/error_handling.md` | 에러 코드 15종 |
| ABC 정본 | `00_common/base_reasoning_engine_abc.md` | think() 시그니처 |
| OC 통합 | `06_dependency-graph/orange_core_integration.md` §5.4 | `think_reasoning_check` + `reasoning_trace_id` |
| 교차 도메인 | **6-12 Event-Logging** (READ-only) | oc.i1~i5 / BRAIN_FAILOVER |
| PART2 | V1-Phase 3 (L2140~2147) | 구현 가이드 |

### 1.1 상위 SoT 정책

- **UPSTREAM_SOT=null** → 상위 SoT 직접 Read = **SKIP**.

### 1.2 cross-check 결과

- §4.1: LOCK-VR-01/04/05/07/08/12 Read 확인 (VR-07 Failover: GPT-4o→Claude Sonnet→Ollama, VR-08 Token: tiktoken 표준).
- §4.2: `04_think-engine/_index.md` priority 일관 처리.
- §4.3: D-1 ↔ `think_reasoning_check` + `reasoning_trace_id` refs 매핑 확인.

---

## 2. LOCK 정본 참조

> LOCK (D2.0-02 §7.53-1 — LOCK-VR-01): Self-check 임계값 P0≥70, P1≥75, P2≥80
> LOCK (D2.0-02 §2.2 — LOCK-VR-04): 상태 머신 S0~S8 (S3 Decision Lock immutable)
> LOCK (상세명세 C-1 §4 — LOCK-VR-05): ≥0.8 PASS, 0.5~0.8 REVIEW, <0.5 FAIL
> LOCK (D2.0-02 §11.1.2 — LOCK-VR-07): Failover Chain GPT-4o → Claude Sonnet → Ollama
> LOCK (D2.0-02 §2.3-A — LOCK-VR-08): Token 계측 tiktoken 표준
> LOCK (D2.0-02 §2.3-B — LOCK-VR-12): 단일응답 ≤2s, 복합응답 ≤10s, Self-check ≤1s

---

## 3. 공통 메트릭 5종

### 3.1 M-COM-01 — Latency

- ID: `vre.d1.think.latency_ms` (p50/p95/p99)
- 태그: `engine=D-1`, `strategy={cot,tot,got,auto}`, `mode={single,composite}`

> **주의**: D-1 추론은 구조상 대부분 **복합응답**(≤10s) 분류. CoT는 단일응답 가능, ToT/GoT는 복합응답.

**임계값 (LOCK-VR-12)**:
| 구간 | p95 | WARNING | CRITICAL |
|------|-----|---------|----------|
| 단일 (CoT) | ≤2,000 ms | > 1,600 ms | > 2,000 ms |
| 복합 (ToT/GoT) | ≤10,000 ms | > 8,000 ms | > 10,000 ms |
| Self-check | ≤1,000 ms | > 800 ms | > 1,000 ms |

### 3.2 M-COM-02 — Throughput

- ID: `vre.d1.think.requests_per_sec`
- WARNING: 5분 연속 용량 80%
- CRITICAL: 5분 연속 용량 100%

### 3.3 M-COM-03 — Error Rate

- ID: `vre.d1.think.error_rate` (태그 `error_code` 15종)
- WARNING: ≥ 20% / CRITICAL: = 100%

### 3.4 M-COM-04 — Confidence 분포 (LOCK-VR-05)

- ID: `vre.d1.think.confidence_histogram`
- 파생: pass_rate / review_rate / fail_rate
- WARNING: fail_rate > 15% 또는 review_rate > 40%
- CRITICAL: fail_rate > 30%

### 3.5 M-COM-05 — Resource Usage

- ID: `vre.d1.think.cpu_pct` / `vre.d1.think.mem_mb` / `vre.d1.think.gpu_pct`
- WARNING: 70% (5분) / CRITICAL: 90% (2분)

---

## 4. D-1 고유 메트릭

### 4.1 M-D1-06 — 전략별 사용 빈도

| 항목 | 값 |
|------|---|
| 메트릭 ID | `vre.d1.think.strategy_usage_count` |
| 태그 | `strategy={cot,tot,got,auto}` |
| 단위 | count (시간당/일별) |
| 파생 | `strategy_mix_ratio` (각 전략 비율) |
| WARNING | auto 비율 > 70% (Auto 과다 의존) |
| CRITICAL | 단일 전략 비율 100% (Auto 선택기 고장 의심) |

### 4.2 M-D1-07 — 추론 깊이 분포

| 항목 | 값 |
|------|---|
| 메트릭 ID | `vre.d1.think.reasoning_depth` |
| 정의 | CoT/ToT/GoT 추론 단계 수 (히스토그램) |
| 태그 | `strategy` |
| WARNING | p95 > 12 (추론 비대) |
| CRITICAL | p95 > 20 또는 max > 30 |

### 4.3 M-D1-08 — 토큰 효율 (LOCK-VR-08 연동)

| 항목 | 값 |
|------|---|
| 메트릭 ID | `vre.d1.think.tokens_per_decision` |
| 하위 | `prompt_tokens`, `completion_tokens`, `total_tokens` |
| 단위 | tokens (tiktoken 표준 — LOCK-VR-08) |
| 파생 | `tokens_per_confidence_point` (총 토큰 / confidence 증가분) |
| WARNING | total_tokens > 4,000 (단일 호출) |
| CRITICAL | total_tokens > 8,000 또는 tokens_per_confidence_point > 임계 비용 |

### 4.4 M-D1-09 — 상태머신 전이 분포 (LOCK-VR-04 연동)

| 항목 | 값 |
|------|---|
| 메트릭 ID | `vre.d1.think.state_transition_count` |
| 태그 | `from_state`, `to_state` (S0~S8 + S_TIMEOUT/S_FAILED/S_ESCALATING) |
| 파생 | `s3_lock_violation_count` (S3 이후 결정 수정 시도) |
| WARNING | `S_TIMEOUT` 전이 비율 > 5% |
| CRITICAL | `s3_lock_violation_count` > 0 (LOCK-VR-04 위반) |

### 4.5 M-D1-10 — chain_length (chain_used 재사용)

> **[CONFLICT_CANDIDATE]**: `think_reasoning_check` 명칭은 ORANGE CORE 컨펌 대상 (P2-6 보고).

| 항목 | 값 |
|------|---|
| 메트릭 ID | `vre.d1.think.chain_length` |
| 정의 | Decision.verify.chain_used 배열 길이 |
| WARNING | > 7 |
| CRITICAL | > 10 |

---

## 5. 6-12 Event-Logging 연동

### 5.1 oc.i1~i5 매핑 (6-12 정본 READ-only)

| 이벤트 | D-1 연동 |
|--------|----------|
| `oc.i1` | latency 측정 시작 + reasoning_trace_id 발급 |
| `oc.i2` | think() 호출, 전략 선택 카운트 ++ |
| `oc.i3` | 추론 단계별 중간 결과 (ToT 노드 확장 등) |
| `oc.i4` | Self-check latency 종료, confidence 히스토그램 적재 |
| `oc.i5` | 전체 latency 집계 + 토큰 사용량 기록 |

### 5.2 BRAIN_FAILOVER 연동 (LOCK-VR-07)

| 메트릭 | 설명 |
|--------|------|
| `vre.d1.think.brain_failover_count` | Layer 1 전환 횟수 |
| `vre.d1.think.brain_active` | `gpt-4o` → `claude-sonnet` → `ollama` |
| `vre.d1.think.fallback_exhausted_count` | Chain 소진 (`OC_I20_BRAIN_EXHAUSTED`) |

> D-1은 Layer 1 (LLM Brain) + Layer 2 (엔진 에스컬레이션)이 **교차**하는 유일한 엔진 (`failover_policy.md` §2.3). 두 레이어 별도 카운팅 필수.

WARNING: brain_failover_count ≥ 3/hr / CRITICAL: fallback_exhausted_count ≥ 1 (30분 윈도우).

### 5.3 OC_I20_* 참조 정책

> **INFRA 이관**: `OC_I20_BRAIN_TIMEOUT/5XX/EXHAUSTED/ESCALATION_FAIL` 정식 등록은 6-12 Phase 2 INFRA 확정 대상. 본 문서는 참조 방식만 정의.

---

## 6. 로깅 포맷 (R-01-7 중첩 JSON)

```json
{
  "timestamp": "2026-04-18T10:30:00.123Z",
  "trace_id": "tr_abc123",
  "decision_id": "dec_xyz789",
  "reasoning_trace_id": "rt_d1_456",
  "engine": "D-1",
  "engine_name": "think-engine",
  "event": "think.completed",
  "metrics": {
    "latency_ms": 7200,
    "confidence": 0.84,
    "chain_length": 4,
    "strategy": "tot",
    "reasoning_depth": 8,
    "prompt_tokens": 1200,
    "completion_tokens": 2400,
    "total_tokens": 3600,
    "state_path": ["S0","S1","S2","S3","S6","S7"]
  },
  "error": {
    "code": "THINK_REASONING_TIMEOUT",
    "severity": "WARNING",
    "recoverable": true
  },
  "context": {
    "mode": "composite",
    "brain_active": "claude-sonnet",
    "phase": "P2"
  },
  "recovery": {
    "strategy": "failover_to_ollama",
    "attempt": 2,
    "max_attempts": 3,
    "escalated_to": "HITL"
  }
}
```

---

## 7. 대시보드 구성 가이드

### 7.1 패널 배치 (5x3)

| 위치 | 패널 | 메트릭 | 갱신 주기 |
|------|------|--------|----------|
| 1,1 | Latency Trend (by strategy) | M-COM-01 | 10초 |
| 1,2 | Throughput | M-COM-02 | 10초 |
| 1,3 | Error Rate by Code | M-COM-03 | 30초 |
| 2,1 | Confidence Histogram | M-COM-04 | 1분 |
| 2,2 | PASS/REVIEW/FAIL % | 파생 | 1분 |
| 2,3 | Resource | M-COM-05 | 30초 |
| 3,1 | Strategy Mix (CoT/ToT/GoT/Auto) | M-D1-06 | 5분 |
| 3,2 | Reasoning Depth Distribution | M-D1-07 | 5분 |
| 3,3 | Tokens per Decision | M-D1-08 | 1분 |
| 4,1 | State Machine Transition | M-D1-09 | 30초 |
| 4,2 | S3 Lock Violations (must be 0) | M-D1-09 파생 | 실시간 |
| 4,3 | Chain Length Distribution | M-D1-10 | 1분 |
| 5,1 | BRAIN_FAILOVER (Layer 1) | §5.2 | 실시간 |
| 5,2 | Fallback Exhausted | §5.2 | 실시간 |
| 5,3 | SLA Compliance (LOCK-VR-12) | 파생 | 1분 |

### 7.2 갱신 주기 / 7.3 보존 기간

- 실시간 (≤10초): latency, S3 lock, failover
- 단기 (30초~1분): error, confidence, token, resource, chain_length
- 중기 (5분): strategy mix, reasoning depth
- 보존: 메트릭 30일/1년, 구조화 로그 14일/90일, SLA/LOCK 위반 90일/3년

---

## 8. Phase 3 테스트 시나리오 (10건+)

| # | 시나리오 | 조건 | 기대 알림 | 근거 |
|---|---------|------|----------|------|
| TS-01 | CoT 단일응답 p95 초과 | 1,700ms | WARNING | LOCK-VR-12 |
| TS-02 | ToT 복합 SLA 위반 | 10,500ms | CRITICAL | LOCK-VR-12 |
| TS-03 | Self-check SLA | 1,100ms | CRITICAL | LOCK-VR-12 |
| TS-04 | Error rate 급등 | 25% (5분) | WARNING | LOCK-VR-01 |
| TS-05 | FAIL 급증 | fail_rate=32% | CRITICAL | LOCK-VR-05 |
| TS-06 | Auto 과다 의존 | auto 비율=75% | WARNING | M-D1-06 |
| TS-07 | 추론 깊이 비대 | p95=22 | CRITICAL | M-D1-07 |
| TS-08 | 토큰 폭증 | total_tokens=9000 | CRITICAL | M-D1-08, LOCK-VR-08 |
| TS-09 | **S3 Lock 위반** | s3_lock_violation_count ≥ 1 | CRITICAL | LOCK-VR-04, M-D1-09 |
| TS-10 | S_TIMEOUT 빈발 | 전이 비율=7% | WARNING | M-D1-09 |
| TS-11 | BRAIN_FAILOVER 연쇄 | 1시간 4회 | WARNING | LOCK-VR-07, §5.2 |
| TS-12 | Fallback 소진 | `OC_I20_BRAIN_EXHAUSTED` | CRITICAL | §5.2 |
| TS-13 | chain_length 비대 | = 12 | CRITICAL | M-D1-10 |

---

## 9. ABC 시그니처 정합 (LOCK-VR-11)

> LOCK (상세명세 C-1 §3 — LOCK-VR-11): 시그니처 변경 불가.

D-1은 `BaseReasoningEngine` ABC 준수. `reason(ThinkRequest) → ThinkResult` 시그니처 보존.

```python
@metrics.observe(engine="D-1", metric_set="vre.d1.think")
async def reason(self, request: ThinkRequest) -> ThinkResult:
    ...
```

---

## 10. 검증 체크리스트 (§7 P2-7 대조 기준 5건)

- [x] G2-3 기여: `04_think-engine/monitoring_metrics.md` 완성
- [x] 메트릭 5종 이상: 공통 5 + 고유 5 = **10종**
- [x] WARNING/CRITICAL 전부 정의
- [x] 6-12 oc.i1~i5 연동 §5.1
- [x] P1 이연 "모니터링 메트릭" 해소
- [x] P1 이연 "OC_I20_*" INFRA 이관 명시 §5.3

---

## 11. 변경 이력

| 버전 | 일자 | 요약 |
|------|------|------|
| v1.0 | 2026-04-18 | Phase 2 P2-7 신규 (V2-Phase 2) |

---

**End of D-1 Think Engine monitoring_metrics.md (v1.0)**
