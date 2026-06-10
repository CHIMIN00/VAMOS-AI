# VBS-12+ 상호운용성 테스트 자동화 — K-068 (V3 신규 L3, Phase 4 production-ready 정본)

> **STEP7-K**: K-068 VBS-12+ 상호운용성 테스트 (L1304~L1318 원문 / `150720a3496f557d359a421dcbf0922ebe5b1e4fbaa06611eff40e0865177539`)
> **레벨**: L3 (V3-Phase 3 SPEC 완료 → Phase 4 production 승급)
> **정본 소유**: #13 Agent-Protocol-Interoperability / 05_self-evolution (VAMOS 독자 혁신 영역)
> **V 스코프**: V3-Phase 3 (5-1 Benchmark 표준 정합 + chaos 시나리오 + VBS-12 정합)
> **Phase 4 태그**: V3-Phase 4 production-ready 정본 승급 (RECOVERY genuine write, P4-1)
> **Status**: APPROVED (DRAFT → APPROVED, 2026-06-03 Phase 4 production promotion)
> **Last-reviewed**: 2026-06-03
> **upstream baseline**: STEP7-K sha256 `150720a3496f557d359a421dcbf0922ebe5b1e4fbaa06611eff40e0865177539`

---

## §1. 교차 참조 블록

| 정본 문서 | 섹션 | 참조 내용 |
|----------|------|----------|
| STEP7-K (Level 2) | L1304~L1318 | K-068 원문 (상호운용성 테스트/카오스/회귀 자동화) |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-01 | VamosMessage 6필드 — 테스트 케이스 메시지 검증 |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-03 | A2A Task 상태 머신 — 상태 전이 테스트 |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-07 | A2A + MCP 양방향 — 인터롭 테스트 핵심 |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-10 | Confidence < 50% HITL (06_autonomy-safety 정본, 본 문서 참조자) |
| 구조화_종합계획서.md | §7.5 P3-1 L1451 | Phase 3 V3 K-068 테스트 자동화 |
| **5-1 Benchmark-Evaluation** | VBS 표준 | 벤치마크 측정 표준 정본 (cross-ref) |
| 05_self-evolution/agent_marketplace.md | §5 | K-067 — 마켓 등록 전 테스트 게이트 |
| 06_autonomy-safety/guardrail_rules.md (V2) | §V2.8 SE-09 | A/B 테스트 트래픽 상한 정합 |
| 4-4 MLOps-LLMOps | CI/CD 테스트 인프라 | 테스트 실행 환경 정본 |

> **R6 준수**: What+How 전용. 벤치마크 측정 표준 정본은 5-1 Benchmark-Evaluation, 본 문서는 상호운용성 테스트 자동화 구조만.

---

## §2. Purpose & Scope (E1 목표 / E2 범위)

### 2.1 테스트 자동화 5대 요건 (STEP7-K L1304~L1318 원문)

| 요건 | 원문 | 본 문서 섹션 |
|------|------|-------------|
| 인터롭 테스트 (A2A + MCP 양방향) | L1305 | §4 인터롭 테스트 |
| 상태 머신 전이 테스트 (LOCK-AP-03) | L1307 | §5 상태 전이 테스트 |
| 카오스 시나리오 (장애 주입) | L1309 | §6 카오스 |
| 회귀 테스트 (VBS-12 정합) | L1311 | §7 회귀 |
| CI 통합 + 자동 게이트 | L1313 | §8 CI 게이트 |

### 2.2 범위 경계 (E2)

| 영역 | 본 문서 | 정본 소유 |
|------|--------|----------|
| 상호운용성 테스트 스위트·카오스·회귀 | ✅ | — |
| 벤치마크 측정 표준 (VBS) | 참조 | 5-1 Benchmark-Evaluation |
| CI/CD 실행 인프라 | 참조 | 4-4 MLOps-LLMOps |
| 마켓 등록 심사 | ❌ | agent_marketplace.md (K-067) |

### 2.3 VAMOS 독자 혁신 포지셔닝

| 비교 대상 | 기존 AI | VAMOS 인터롭 테스트 |
|----------|---------|--------------------|
| 일반 LLM 평가 (정확도 벤치) | 단일 모델 정확도 위주 | A2A+MCP 양방향 인터롭 + 상태 머신 + 카오스 + 회귀 자동화 + 마켓 등록 게이트 |

---

## §3. 공통 자료 구조 Import (E3)

```python
from sot2_domain.agent_protocol_interoperability.types import (
    VamosMessage,        # LOCK-AP-01 6필드
    A2ATaskState,        # LOCK-AP-03 상태 머신
)
from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, List
from datetime import datetime
```

---

## §4. 인터롭 테스트 스위트 (D1 / E4 — LOCK-AP-07)

```python
class InteropTestCase(BaseModel):
    case_id: str
    direction: Literal["a2a_to_mcp", "mcp_to_a2a", "bidirectional"]
    input_message: VamosMessage           # LOCK-AP-01 6필드 검증
    expected_schema: str
    expected_state: Optional[str]         # LOCK-AP-03
    timeout_ms: int = 5000
```

- A2A↔MCP 양방향 변환 무손실 검증 (LOCK-AP-07).
- VamosMessage 6필드 (id/type/source/target/content/metadata) 스키마 정합 (LOCK-AP-01).

---

## §5. 상태 머신 전이 테스트 (E5 — LOCK-AP-03)

### 5.1 A2A Task 상태 전이 검증 (LOCK-AP-03 정본)

> **LOCK-AP-03**: A2A Task 상태 머신 = `submitted → working → input-required → completed/failed/canceled` — 변경 금지.

| 전이 | 유효 | 테스트 |
|------|:----:|-------|
| submitted → working | ✅ | AT-01 |
| working → input-required | ✅ | AT-02 |
| input-required → working | ✅ | AT-03 |
| working → completed | ✅ | AT-04 |
| working → failed | ✅ | AT-05 |
| * → canceled | ✅ | AT-06 |
| completed → working (역행) | ❌ | AT-07 (거부 검증) |

---

## §6. 카오스 시나리오 (E6 — 장애 주입)

| 카오스 | 주입 | 기대 복원 |
|--------|------|----------|
| 네트워크 지연 (+2s) | latency injection | 타임아웃 + 재시도 |
| 메시지 손실 (10%) | drop | 재전송 + idempotency |
| Circuit Breaker 트립 | 연속 실패 3회 | LOCK-AP-06 failure_threshold=3 / 60s recovery |
| 권한 거부 폭주 | L3+ 자동 시도 | HITL + abort (LOCK-AP-02) |
| confidence 급락 | drift 주입 | LOCK-AP-10 HITL |
| 외부 에이전트 무응답 | hang | 타임아웃 + escalation |

> Circuit Breaker recovery 60s 는 LOCK-AP-06 정본 (D2.0-05 §4.4) verbatim.

---

## §7. 회귀 테스트 (E7 — VBS-12 정합)

```python
class RegressionResult(BaseModel):
    suite_id: str
    vbs_version: str                       # "VBS-12+" (5-1 표준)
    pass_count: int
    fail_count: int
    regression_delta: float                # vs. baseline (음수 = 회귀)
    confidence: float                      # 측정 신뢰도
```

- VBS-12+ 벤치마크 표준은 5-1 Benchmark-Evaluation 정본 정합.
- `regression_delta < -0.05` → 회귀 알람 + 배포 차단 (자동 RESOLVE 금지, HITL 보고).

---

## §8. CI 게이트 + Confidence Penalty (E8)

| 이벤트 | Confidence Penalty | HITL (< 0.50) |
|--------|:-----------------:|:-------------:|
| 인터롭 테스트 실패 (A2A↔MCP 손실) | -0.30 | ✅ |
| 상태 전이 위반 (역행 허용) | -0.40 | ✅ (LOCK-AP-03) |
| 회귀 delta < -0.05 | -0.25 | ✅ (배포 차단) |
| 카오스 복원 실패 | -0.20 | 누적 기준 |
| 측정 신뢰도 < 95% | -0.15 | 누적 기준 |

> LOCK-AP-10 재정의 없음 — 06_autonomy-safety/guardrail_rules.md (P2-6 정본) cumulative 기준. CI 게이트: 전 스위트 PASS + 회귀 0 + 신뢰도 ≥ 95% → 통과.

---

## §9. 에스컬레이션 + LOCK 매핑 5필드 표 (E9 / E10)

```python
class TestingEscalation(BaseModel):
    trace_id: str
    event_class: Literal[
        "interop_loss",
        "state_transition_violation",
        "regression_detected",
        "chaos_recovery_failure",
        "low_measurement_confidence",
    ]
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    confidence_delta: float = Field(..., le=0.0, ge=-1.0)
    suite_id: str
    recommended_action: Literal["block_deploy", "escalate_hitl_L3", "rerun_suite", "report"]
    occurred_at: datetime
```

| LOCK ID | 항목 | 원본 문서 | 값 | 재정의 | 본 문서 적용 지점 |
|---------|------|----------|-----|--------|------------------|
| LOCK-AP-01 | 프로토콜 메시지 포맷 | STEP7-K, D2.0-05 | VamosMessage 6필드 | 금지 | §4 input_message 6필드 검증 |
| LOCK-AP-03 | A2A Task 상태 머신 | D2.0-05, K-012 | submitted→working→input-required→completed/failed/canceled | 금지 | §5.1 상태 전이 검증 verbatim |
| LOCK-AP-07 | 인터롭 규격 | STEP7-K | A2A + MCP 양방향 지원 필수 | 금지 | §4 인터롭 양방향 무손실 테스트 |
| LOCK-AP-10 | Confidence 임계값 | DEFINED-HERE (06_autonomy-safety 정본) | HITL 트리거 < 50% | 금지 | §8 CI penalty (참조자, 재정의 없음) |

---

## §10. Phase 3 테스트 시나리오 (≥ 10건)

| # | ID | 설명 | 기대 결과 |
|---|----|------|----------|
| 1 | AG-01 | A2A→MCP 변환 무손실 검증 | ✅ LOCK-AP-07 |
| 2 | AG-02 | VamosMessage 6필드 스키마 정합 | ✅ LOCK-AP-01 |
| 3 | AG-03 | 상태 전이 submitted→working→completed | ✅ LOCK-AP-03 |
| 4 | AG-04 | completed→working 역행 거부 | ✅ §5.1 AT-07 |
| 5 | AG-05 | 네트워크 지연 +2s 카오스 → 재시도 복원 | ✅ §6 |
| 6 | AG-06 | Circuit Breaker 트립 → 60s recovery | ✅ LOCK-AP-06 |
| 7 | AG-07 | 회귀 delta -0.07 → 배포 차단 + HITL | ✅ §7/§8 |
| 8 | AG-08 | 측정 신뢰도 92% → confidence -0.15 | ✅ §8 |
| 9 | AG-09 | VBS-12+ 5-1 표준 정합 | ✅ 5-1 cross-ref |
| 10 | AG-10 | 마켓 등록 전 테스트 게이트 (K-067) | ✅ agent_marketplace.md §5 |
| 11 | AG-11 | L3+ 권한 자동 시도 카오스 → abort | ✅ LOCK-AP-02 |
| 12 | AG-12 | Langfuse trace `test.interop.*` span 기록 | ✅ logging_spec.md §5.1 |

---

## §11. 세션 간 인터페이스 Cross-check 표

| 인터페이스 | 대상 파일 | 검증 기준 |
|-----------|----------|----------|
| 마켓 등록 게이트 | `agent_marketplace.md §5` | chaos + interop 게이트 |
| VBS 측정 표준 | `5-1 Benchmark-Evaluation` | VBS-12+ 정본 정합 |
| A/B 테스트 상한 | `06_autonomy-safety/guardrail_rules.md §V2.8 SE-09` | 트래픽 상한 정합 |
| CI/CD 실행 인프라 | `4-4 MLOps-LLMOps` | 테스트 실행 환경 |

---

## §12. 검증 자가 체크리스트 (L3 D1~D8 + E1~E10)

- [x] STEP7-K L1304~L1318 K-068 5대 요건 전수 구현 (인터롭/상태/카오스/회귀/CI)
- [x] LOCK-AP-03 상태 머신 전이 verbatim 검증 (§5.1)
- [x] LOCK-AP-07 A2A+MCP 양방향 무손실 인터롭 (§4)
- [x] LOCK-AP-01/03/07/10 5필드 분리 인용 (§9)
- [x] LOCK-AP-06 Circuit Breaker 60s recovery 카오스 (§6)
- [x] LOCK-AP-10 재정의 없음 (§8 참조자)
- [x] VBS-12+ 5-1 Benchmark 표준 정합 (§7/§11)
- [x] agent_marketplace (K-067) 등록 게이트 cross-ref (§11)
- [x] 회귀 delta < -0.05 자동 RESOLVE 금지 + HITL 보고 (§7)
- [x] Phase 3 테스트 12건 (≥ 10 요건 충족, §10)
- [x] Status DRAFT → APPROVED 전환 (Phase 4 production 승급)

---

*정본 소유: #13 Agent-Protocol-Interoperability (자기진화 전략 — 상호운용성 테스트 자동화)*
*VBS-12+ 벤치마크 측정 표준 정본은 5-1 Benchmark-Evaluation*
*LOCK-AP-10 HITL<50% 는 06_autonomy-safety/guardrail_rules.md (P2-6 정본) 에서 정의, 본 문서는 참조자*
