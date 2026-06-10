# Upgrade Safety — LLM 모델 교체 안전 조건 + 4-4 MLOps 연동 인터페이스 (ISS-5)

> **수정 정책**: 정본 — Phase 변경 시 갱신 (§8.2)
> **도메인**: 6-6_Self-Evolution-System / 03_model-upgrade-strategy
> **Tier**: 6 (System-wide Components)
> **정본 출처**:
> - Part2 V3-Phase 2 L3675 (V2→V3 전환 조건 verbatim) + L4058 (LOCK L10 정본 — QoD ≥ 0.90 60일 + Self-evo 검증 + V3 비용 승인) + L6248~L6260 (TC 측정 메커니즘 — qod_tracker.py / self_evo_validator.py / cost_v3_report.py)
> - 03_model-upgrade-strategy/_index.md §2 (LOCK L10 3가지 전제 조건), §7 (ISS-5 model_upgrade_request 스키마 개요), §11 (4-4 MLOps 교차 참조)
> - 종합계획서 §6.2 ISS-5 (4-4 MLOps 연동 인터페이스 정의 위임), §7.2 Phase 2 (P2-2 산출물), 부록 B (4-4 MLOps 소비 도메인)
> - **CROSS_DOMAIN_RECHECK.md §3.4 권장조치 1** (3층 매트릭스 명시 의무: L10 0.90 / ML-05 0.85 / ML-07 0.60)
> - **4-4 LOCK 인용 정본 (read-only, 재정의 ❌)**:
>   - `D:\VAMOS\docs\sot 2\4-4_MLOps-LLMOps\04_canary-deployment\_index.md` §D-1/§D-3 (LOCK-ML-08 5단계 + LOCK-ML-09 자동 롤백 조건)
>   - `D:\VAMOS\docs\sot 2\4-4_MLOps-LLMOps\MLOPS_LLMOPS_상세명세.md` §B-5 품질 게이트 (LOCK-ML-05 QoD ≥ 0.85), L487 (LOCK-ML-07 QoD CRITICAL < 0.60)
> **LOCK 매핑**: L3 (S-8 거버넌스 승인 필수 — 모델 업그레이드도 대상), L4 (자동 적용 절대 금지 — kill switch), L8 (S-2 회귀 테스트 — Full 단계 후 회귀), **L10 (모델 업그레이드 안전 조건 — QoD ≥ 0.90 60일, Self-evo 검증, V3 비용 승인)**
> **DH 매핑**: **DH-1 (안정화 4메트릭 — Self-evo 시스템 검증 완료 조건)**, DH-2 (S-8 timeout=600s — 업그레이드 승인도 동일), DH-3 (Policy-based 승인 엔진 — risk 평가)
> **Phase**: P2-2 (ISS-5 해결)
> **생성일**: 2026-04-27
> **ISS 해결**: **ISS-5 (4-4 MLOps 연동 인터페이스)** + CROSS_DOMAIN_RECHECK §3.4 권장조치 1 충족 (3층 매트릭스 명시)
> **선행 의존**: P2-1 s08_governance.md (S-8 평가 주체) / 03/_index.md (R-66-5 카나리 5단계 추상 정의) / 4-4 MLOps Phase 2 완료 baseline

---

## 교차 참조 블록 (Rule a)

| 참조 대상 | 관계 |
|----------|------|
| **Part2 V3-Phase 2 L4058 verbatim** | "QoD ≥ 0.90 (60일), Self-evo 시스템 검증 완료, V3 비용 승인" — LOCK L10 정본 출처 |
| **Part2 V3-Phase 2 L3675 verbatim** | "QoD ≥ 0.90(60일), 2-tier LLM 최적화, Self-evo 검증, V3 비용 승인" — V2→V3 전환 조건 정본 |
| **Part2 V3-Phase 2 L6248~L6260** | TC 측정 메커니즘: `qod_tracker.py` (60일 이동평균) / `self_evo_validator.py` (Self-evo 검증) / `cost_v3_report.py` (V3 비용 집계, 월합 ≤ ₩266,000) |
| **AUTHORITY_CHAIN.md §4 L10** | LOCK L10 정본 등재 (Part2 L4058 매핑) |
| **AUTHORITY_CHAIN.md §5 DH-1** | 안정화 4메트릭 verbatim (에러율<1% 7일 / 스키마 검증 100% 7일 / I-Module 경유 성공률 ≥99% / 리소스 80% 미만) |
| **03_model-upgrade-strategy/_index.md §2** | LOCK L10 3가지 전제 조건 추상 정의 — 본 문서 §2~§4 상세화 |
| **03_model-upgrade-strategy/_index.md §7** | ISS-5 model_upgrade_request 스키마 개요 — 본 §3 정본 정의로 위임 수용 |
| **03_model-upgrade-strategy/_index.md §11** | 4-4 MLOps 교차 참조 항목 (model_upgrade_request 스키마 연동, 카나리 배포 인프라, 드리프트 감지) |
| **종합계획서 §6.2 ISS-5** | "model_upgrade_request = {model_id, version, qod_baseline, safety_checks}" 추상 정의 → 본 §3 6-필드 정본 정의로 확장 |
| **종합계획서 §7.4 6-5 SDAR 연동** | 모델 교체 실패 시 SDAR Detection → Diagnosis 경로 (참조만) |
| **CROSS_DOMAIN_RECHECK.md §3.4 권장조치 1** | "4-4 LOCK-ML-05/07/09 절대경로 출처 인용 + 3층 매트릭스 명시" 의무 → 본 §5 충족 |
| **CROSS_DOMAIN_RECHECK.md §3.3 CFL-SE-XREF-4-4-01** | 잠정 ID — 본 P2-2 ISS-5 해결 후 SEVO-C005 정식 채번 (도메인 마감 step 7) |
| **s08_governance.md (P2-1)** | 모델 업그레이드 EvolutionPlan은 S-8 평가 대상 (`routing_reason="model_upgrade"`) — admin_required 분기 강제 (§3.3) |
| **canary_rollback.md (P2-3)** | 카나리 5단계 + 자동 롤백 메커니즘 — 본 문서 §6은 진입 전제만, 실제 단계별 게이트 임계값은 P2-3 위임 |
| **4-4 04_canary-deployment/_index.md §D-1 (LOCK-ML-08)** | "Shadow(0%)→Canary(5%)→Partial(25%)→Majority(75%)→Full(100%)" verbatim — 6-6 R-66-5와 단계 수·비율 완전 일치 |
| **4-4 04_canary-deployment/_index.md §D-3 (LOCK-ML-09)** | "QoD 차이>0.2 자동 롤백, 에러율>Current×2 자동 롤백" verbatim — 6-6 ISS-6 자동 롤백 트리거 정합 |
| **4-4 MLOPS_LLMOPS_상세명세.md §B-5 (LOCK-ML-05)** | "품질 (QoD score 0.0~1.0) >= 0.85" verbatim — 운영 품질 게이트 |
| **4-4 MLOPS_LLMOPS_상세명세.md L487 (LOCK-ML-07)** | "QoD CRITICAL (24h 평균 < 0.60) EMERGENCY — 즉시 이전 프롬프트 롤백" verbatim |
| **4-4 CONFLICT C-04 (RESOLVED)** | QoD 스케일 0.0~1.0 통일 (S11-6 DEC-010) — 본 문서 모든 수치는 0.0~1.0 스케일 사용 |
| **6-12 Event-Logging** | `oc.self_evo.upgrade.*` 이벤트 발행 (요청·승인·롤백 단계별) |
| **5-1 Benchmark-Evaluation** | 모델 교체 전·후 벤치마크 비교 (S-2 회귀 테스트 데이터 소스) |
| **6-4 Memory-RAG-Storage** | I-15 스냅샷 저장 (롤백용) |

---

## 1. 개요

본 문서는 LLM 모델 교체·업그레이드 시 **3가지 안전 조건 충족 검증** + **6-6 ↔ 4-4 MLOps 인터페이스 정본 정의** + **A/B 테스트 절차** + **3층 QoD 매트릭스 명시**를 다룬다. ISS-5(4-4 MLOps 연동 인터페이스)를 해결하며, 모델 업그레이드 진입 전제 조건은 Part2 V3-P2 L4058 LOCK L10에 의거 — QoD ≥ 0.90 (60일), Self-evo 시스템 검증 완료, V3 비용 승인 3건 모두 충족 시에만 카나리 배포(P2-3) 진입 가능. 본 문서는 진입 게이트만 다루며, 실제 5단계 카나리 배포·자동 롤백은 [canary_rollback.md](canary_rollback.md)에 위임한다.

### 1.1 책임 요약

- **3가지 전제 조건 검증** (§2): LOCK L10 — QoD ≥ 0.90 (60일), Self-evo 시스템 검증, V3 비용 승인 3건 AND 결합
- **`model_upgrade_request` 정본 6-필드 스키마 정의** (§3): 6-6 → 4-4 MLOps 인터페이스 단방향 발행 스키마
- **A/B 테스트 절차** (§4): Mann-Whitney U 검정 (p ≥ 0.05) + Effect size (Cohen's d) + 최소 샘플 1,000건
- **3층 QoD 매트릭스** (§5): L10(0.90) 진입 / ML-05(0.85) 운영 / ML-07(0.60) CRITICAL 즉시 롤백 — CROSS_DOMAIN_RECHECK §3.4 권장조치 1 충족
- **Self-evo 시스템 검증 절차** (§6): DH-1 안정화 4메트릭 + 60일 관찰 누적
- **V3 비용 승인 흐름** (§7): CostBudget 인터페이스 + 일일 10% 초과 시 인간 승인 + 월합 ≤ ₩266,000 ABSOLUTE LOCK
- **S-8 거버넌스 통합** (§8): 모든 model_upgrade_request은 S-8 admin_required 분기 강제 (P2-1 §3.3)
- **자동 적용 금지(L4)**: 본 문서는 검증·인터페이스 정의만, 실제 모델 교체 코드 경로는 4-4 MLOps + 6-13 Operations

### 1.2 진입 흐름

```
[모델 교체 제안 (S-3 또는 S-6)]
        │
        ▼
   §2 LOCK L10 3가지 전제 조건 검증
        │
        ├── 1건 이상 미충족 ──▶ 거부 + 사유 기록 (I-9)
        │
        ▼
   §3 model_upgrade_request 발행 (6-필드)
        │
        ▼
   §4 A/B 테스트 (Mann-Whitney p≥0.05 + Cohen's d ≥ 0.2)
        │
        ▼
   §6 Self-evo 시스템 검증 (DH-1 4메트릭 + 60일 관찰)
        │
        ▼
   §7 V3 비용 승인 (CostBudget + 월합 검증)
        │
        ▼
   §8 S-8 거버넌스 admin_required 분기 (P2-1 §3.3)
        │
        ▼
   [canary_rollback.md (P2-3) 카나리 5단계 진입]
```

---

## 2. LOCK L10 3가지 전제 조건 (Part2 L4058 verbatim 인용)

> **Part2 V3-Phase 2 L4058 verbatim**: "QoD ≥ 0.90 (60일), Self-evo 시스템 검증 완료, V3 비용 승인"
>
> **Part2 V3-Phase 2 L3675 verbatim** (V2→V3 전환 조건): "QoD ≥ 0.90(60일), 2-tier LLM 최적화, Self-evo 검증, V3 비용 승인"
>
> ※ L10은 V2→V3 전환 조건 5건 중 Self-evo 도메인 직접 해당 3건 추출. "2-tier LLM 최적화"는 별도 인프라 전제 조건 (4-1 Rust-Tauri 또는 1-1 Verifier 도메인 소관).

### 2.1 조건 1 — QoD ≥ 0.90 (60일 연속 이동평균)

| 항목 | 값 | 측정 방법 | TC 도구 |
|------|-----|----------|--------|
| **임계값** | QoD ≥ 0.90 | 60일 연속 이동평균 | `qod_tracker.py` (Part2 L6256) |
| **단일일 최저** | QoD ≥ 0.80 | 단일일 일평균 (60일 중 어느 날도 0.80 미만 ❌) | 동일 |
| **측정 주기** | 매 파이프라인 실행 시 | 누적 후 일 1회 집계 | 동일 |
| **기준선** | qod_baseline = 측정 시작 시점 60일 평균 | model_upgrade_request 동봉 (§3) | — |

**준수 검증**:
- ✅ PASS: 60일 연속 이동평균 ≥ 0.90 AND 단일일 최저 ≥ 0.80
- ❌ FAIL: 60일 평균 < 0.90 OR 단일일 최저 < 0.80 (1건이라도)

### 2.2 조건 2 — Self-evo 시스템 검증 완료

DH-1 안정화 4메트릭 (AUTHORITY §5) 전수 충족 + 60일 관찰 누적:

```
1. 모듈 에러율 < 1% (7일 관찰) ← 60일 환산: 60일 중 어느 7일 윈도우도 1% 초과 ❌
2. 출력 스키마 검증 100% 통과 (7일) ← 60일 환산: 60일 누계 100% 통과
3. I-Module 경유 호출 성공률 ≥ 99% ← 60일 누계 ≥ 99%
4. 메모리/CPU 사용량이 할당 리소스의 80% 미만 ← 60일 어느 7일 윈도우도 80% 초과 ❌
```

**TC 도구**: `self_evo_validator.py` (Part2 L6259) — "개선 전/후 성능 비교 + 롤백 정상 동작 + 거버넌스 규칙 준수 확인"

**검증 산출물**: `EvolutionValidationReport` (§3.5 6-필드 스키마)

### 2.3 조건 3 — V3 비용 승인

| 항목 | 값 | 측정 방법 | TC 도구 |
|------|-----|----------|--------|
| **월합 상한** | ≤ ₩266,000 (ABSOLUTE LOCK) | 60일 운영 비용 월합 | `cost_v3_report.py` (Part2 L6260) |
| **60일 연속 준수** | 매월 ≤ ₩266,000 | 60일 누계 일 1회 집계 | 동일 |
| **승인 채널** | 사용자 명시적 승인 | CLI `vamos approve v3-transition` | Part2 §7.4 #14 |
| **일일 10% 초과 알림** | 임계 초과 시 즉시 ADMIN+ 알림 | I-20 EscalationManager | 본 §7 |

**준수 검증**:
- ✅ PASS: 60일 연속 월합 ≤ ₩266,000 AND CLI 승인 이벤트 기록 존재
- ❌ FAIL: 1건이라도 월합 초과 OR 승인 이벤트 부재

### 2.4 3건 AND 결합 — 모두 충족 시에만 §3 발행

```python
def is_upgrade_eligible(qod_60d: float, self_evo_validated: bool,
                       cost_approved: bool, qod_min_day: float,
                       cost_60d_compliant: bool) -> bool:
    """LOCK L10 3건 AND 결합 검증."""
    return (
        qod_60d >= 0.90                  # 조건 1
        and qod_min_day >= 0.80          # 단일일 최저
        and self_evo_validated           # 조건 2
        and cost_approved                # 조건 3 (사용자 승인)
        and cost_60d_compliant           # 조건 3 (60일 ≤ ₩266,000)
    )
```

> **L4 준수**: `is_upgrade_eligible() == False` 시 자동 적용 절대 금지. 거부 사유 I-9 로깅 + S-3/S-6 제안자 피드백.

---

## 3. `model_upgrade_request` 정본 6-필드 스키마 (ISS-5 해결)

### 3.1 스키마 정의 (Pydantic, Rule k)

> **ISS-5 정의 위임 수용**: 종합계획서 §6.2 ISS-5 추상 정의 (`{model_id, version, qod_baseline, safety_checks}`) → 본 §3 **6-필드 정본 확장**.

```python
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal, Optional, Dict
from datetime import datetime

# ── ISS-5 정본 (6-6 → 4-4 MLOps 단방향 발행 스키마) ──────────
class ModelUpgradeRequest(BaseModel):
    """6-6 Self-Evolution → 4-4 MLOps-LLMOps 단방향 발행.

    LOCK L10 (Part2 L4058) 3건 전제 조건 충족 후 발행 가능.
    LOCK L4 준수: 4-4 측은 본 요청을 수신하고 카나리 배포 인프라 실행만 담당.
    """
    # 핵심 식별자 (3 필드)
    model_id: str                          # 대상 모델 식별자 (예: "claude-opus-4-7")
    version: str                           # 신규 모델 버전 (semver 또는 commit SHA)
    qod_baseline: float = Field(ge=0.0, le=1.0)
                                           # 현재 QoD 60일 평균 (기준선, 0.0~1.0 스케일)

    # 안전 검증 체크리스트 (1 중첩 필드 = 3 sub-필드)
    safety_checks: "SafetyChecks"          # 3 sub-필드 (§3.2)

    # 메타 (2 필드)
    request_id: str                        # UUID v4 (S-8 ApprovalRequest.request_id 대응)
    requested_at: datetime                 # ISO8601 UTC

    model_config = ConfigDict(extra="forbid")

# ── safety_checks 내부 스키마 ─────────────────────────────────
class SafetyChecks(BaseModel):
    """LOCK L10 3건 전제 조건 검증 결과 (PASS/FAIL).

    이 객체가 dispatch 직전 모든 필드 True 여야만 §3.4 발행 가능.
    """
    qod_60day_avg: bool                    # 조건 1 충족 (60일 평균 ≥ 0.90 AND 단일일 ≥ 0.80)
    self_evo_verified: bool                # 조건 2 충족 (DH-1 4메트릭 + 60일 관찰)
    v3_cost_approved: bool                 # 조건 3 충족 (월합 ≤ ₩266,000 + CLI 승인)

    model_config = ConfigDict(extra="forbid")
```

### 3.2 6-필드 매핑 (외부 ISS-5 추상 vs 본 정본 확장)

| ISS-5 추상 필드 | 본 정본 필드 | 비고 |
|----------------|-------------|------|
| `model_id: str` | `model_id: str` | 그대로 |
| `version: str` | `version: str` | 그대로 |
| `qod_baseline: float` | `qod_baseline: float` (제약: 0.0~1.0) | Pydantic Field 검증 추가 |
| `safety_checks: list` | `safety_checks: SafetyChecks` (3 sub-필드 정본 분해) | list → 명시적 BaseModel + extra="forbid" |
| (추상에 부재) | `request_id: str` (UUID v4) | S-8 ApprovalRequest.request_id 대응 추가 |
| (추상에 부재) | `requested_at: datetime` | 감사 추적 + timeout 600s 기점 |

> **결정**: ISS-5 추상 정의의 `safety_checks: list` 를 6-6 본 정본에서 `SafetyChecks` BaseModel로 명시 분해. 4-4 측 소비 시 dict-deserialize 가능 (Pydantic v2 호환).

### 3.3 발행 흐름

```
[S-3 또는 S-6 모델 교체 제안 EvolutionPlan]
        │
        ▼
   §2 LOCK L10 3건 전제 조건 검증
        │
        ▼
   §4 A/B 테스트 (Mann-Whitney p≥0.05)
        │
        ▼
   ModelUpgradeRequest 인스턴스 생성
        │
        ├── safety_checks.qod_60day_avg = True (§2.1 PASS)
        ├── safety_checks.self_evo_verified = True (§2.2 PASS)
        └── safety_checks.v3_cost_approved = True (§2.3 PASS)
        │
        ▼
   S-8 ApprovalRequest 발행 (routing_reason="model_upgrade")
        │  (P2-1 §3.3 admin_required 분기 강제)
        ▼
   S-8 admin_manual 승인 (timeout 600s)
        │
        ▼
   [4-4 MLOps 카나리 배포 실행 (canary_rollback.md P2-3 위임)]
```

### 3.4 4-4 측 소비 인터페이스 (read-only 인용)

> **4-4 측 수신 명세 부재 인지**: CROSS_DOMAIN_RECHECK §3.2 D항 "4-4 전체 파일에서 model_upgrade_request / 6-6 / Self-evo 키워드 매치 없음" — 본 P2-2 ISS-5 해결 후 4-4 측에 [RECHECK_FLAG: 4-4] 재발행 (도메인 마감 step 7).

**임시 소비 경로** (4-4 ISS-5 수신 명세 작성 전): `oc.self_evo.upgrade.requested` 이벤트로 4-4 측이 구독. 4-4 차기 Phase에서 `MLOpsUpgradeReceiver` 인터페이스 정의 시 본 스키마 직수신.

### 3.5 Self-evo 검증 보고서 (§2.2 산출물)

```python
class EvolutionValidationReport(BaseModel):
    """§2.2 Self-evo 시스템 검증 결과 (DH-1 4메트릭 60일 관찰 결과)."""
    report_id: str                         # UUID v4
    observation_window_days: int = 60
    error_rate_max_7day: float             # 60일 중 어느 7일 윈도우 최대 에러율
    schema_pass_rate: float                # 60일 누계 스키마 검증 통과율 (0.0~1.0)
    i_module_success_rate: float           # 60일 누계 I-Module 경유 성공률
    resource_usage_max_7day: float         # 60일 중 어느 7일 윈도우 최대 리소스 사용률
    rollback_test_success_rate: float      # 60일 내 롤백 테스트 성공률 (목표 100%)
    governance_violation_count: int        # 60일 내 거버넌스 위반 0건 목표

    model_config = ConfigDict(extra="forbid")
```

---

## 4. A/B 테스트 절차

### 4.1 통계 검정 방법

| 항목 | 값 | 비고 |
|------|-----|------|
| **검정 방법** | Mann-Whitney U test | 비모수 검정 (QoD 분포 정규성 가정 ❌) |
| **유의수준** | p ≥ 0.05 (귀무가설 기각 ❌, 즉 "차이 없음" 또는 "신규 ≥ 기존") | 신규 모델이 기존보다 유의하게 낮지 않음 검증 |
| **Effect size** | Cohen's d — 실용적 차이 분류 임계 (\|d\| < 0.2 ⇒ 동등 PASS, \|d\| ≥ 0.2 AND mean(candidate)>baseline ⇒ 우수 PASS) | §4.2 결정 흐름 정합 — 단독 PASS 게이트가 아닌 동등/우수 분기 분류용 (권장: TOST 비열등 마진 검정 보강) |
| **최소 샘플** | 신규 모델 ≥ 1,000건, 기존 모델 ≥ 1,000건 | A/B 분리 7일 운영 |
| **메트릭** | QoD score (0.0~1.0 스케일, 4-4 CONFLICT C-04 RESOLVED 정합) | LLM-as-judge + 인간 샘플링 |

### 4.2 A/B 테스트 흐름

```
[기존 모델 (Baseline)]                  [신규 모델 (Candidate)]
   1,000건 QoD 측정                          1,000건 QoD 측정
        │                                          │
        └─────────────┬────────────────────────────┘
                      ▼
            Mann-Whitney U test
                      │
                      ├── p < 0.05 AND median(candidate) < median(baseline)
                      │       └─▶ 신규 모델 유의하게 낮음 ──▶ FAIL (거부)
                      │
                      ├── p ≥ 0.05 (차이 없음)
                      │       │
                      │       └──▶ Cohen's d 검사
                      │              │
                      │              ├── |d| < 0.2 ──▶ PASS (통계적·실용적 동등)
                      │              │
                      │              └── |d| ≥ 0.2 AND mean(candidate) > mean(baseline)
                      │                     └─▶ PASS (실용적 우수)
                      │
                      └── p < 0.05 AND median(candidate) > median(baseline)
                              └─▶ PASS (신규 모델 유의하게 우수)
```

### 4.3 회귀 검증 (LOCK L8)

> **LOCK L8 (D2.0-02 §10.6 L3856 verbatim)**: "적용 이후 S-2가 '개선 전/후 성능 비교' 회귀 테스트를 수행한다."

A/B 테스트 PASS 후, Full 단계 안정화 7일 경과 시 S-2 Pattern Miner가 회귀 테스트 수행:
- 비교 대상: 모델 교체 전 60일 평균 QoD/latency/cost vs 교체 후 7일 평균
- 판정 기준: 교체 후 ≥ 교체 전 (LOCK L8 충족)
- 실패 시: 즉시 롤백 + S-8 사후 보고 + 실패 패턴 S-2 학습 (P2-3 §5)

---

## 5. 3층 QoD 매트릭스 (CROSS_DOMAIN_RECHECK §3.4 권장조치 1 충족)

> **본 §5는 CROSS_DOMAIN_RECHECK.md §3.4 권장조치 1 의무 이행** — "L10(0.90) 이 '업그레이드 진입 전제', ML-05(0.85) 가 '운영 최소 품질', ML-07(0.60) 이 'CRITICAL 즉시 롤백' 임을 3층 매트릭스로 명시".

### 5.1 3층 운영 계층 구조

| 계층 | LOCK | 임계값 | 운영 계층 | 정본 출처 |
|------|------|--------|----------|----------|
| **1층 (배포 진입)** | **L10** (6-6) | QoD ≥ **0.90** (60일 평균) | 모델 업그레이드 진입 전제 — 미충족 시 ModelUpgradeRequest 발행 ❌ | `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` V3-P2 L4058 |
| **2층 (일상 운영)** | **ML-05** (4-4) | QoD ≥ **0.85** (운영 품질 게이트) | 카나리 배포 후 일상 운영 최소 품질 — 미충족 시 ML-09 자동 롤백 검토 | `D:\VAMOS\docs\sot 2\4-4_MLOps-LLMOps\MLOPS_LLMOPS_상세명세.md` §B-5 |
| **3층 (긴급 롤백)** | **ML-07** (4-4) | QoD < **0.60** (24h 평균) | EMERGENCY — 즉시 이전 모델 롤백 + 긴급 대응팀 소집 | `D:\VAMOS\docs\sot 2\4-4_MLOps-LLMOps\MLOPS_LLMOPS_상세명세.md` L487 |

### 5.2 매트릭스 운영 시나리오

```
[모델 교체 진행]
   │
   ▼
[1층 진입 게이트 — L10 QoD ≥ 0.90]
   │
   ├── 미충족 ──▶ ModelUpgradeRequest 발행 ❌ (§2 거부)
   │
   └── 충족 ──▶ 카나리 5단계 (canary_rollback.md P2-3)
        │
        ▼
   [2층 운영 게이트 — ML-05 QoD ≥ 0.85]
        │
        ├── 미충족 (≤ 0.85) AND ≥ 0.60 ──▶ ML-09 자동 롤백 검토 (QoD 차이>0.2 또는 에러율>Current×2)
        │       │
        │       └── ML-09 트리거 ──▶ canary_rollback.md ISS-6 자동 롤백
        │
        └── 충족 ──▶ 운영 지속
              │
              ▼
   [3층 CRITICAL — ML-07 QoD < 0.60]
        │
        └── 발화 ──▶ EMERGENCY: 즉시 이전 모델 100% 롤백 + 긴급 대응팀 소집 + S-8 사후 보고
```

### 5.3 4-4 LOCK 인용 (read-only, 재정의 ❌)

본 §5는 4-4 LOCK-ML-05/07/09를 **참조만** 한다. 4-4 정본 자체 수정 ❌ (CROSS_DOMAIN_RECHECK 작성 제약 준수). 6-6 측 LOCK은 AUTHORITY §4 L10 만 사용.

| 4-4 LOCK | verbatim 인용 | 본 §5 위치 |
|----------|--------------|-----------|
| **LOCK-ML-05** | "품질 (QoD score 0.0~1.0) >= 0.85" (§B-5) | §5.1 2층 |
| **LOCK-ML-07** | "QoD CRITICAL (24h 평균 < 0.60) EMERGENCY — 즉시 이전 프롬프트 롤백" (L487) | §5.1 3층 |
| **LOCK-ML-08** | "Shadow(0%)→Canary(5%)→Partial(25%)→Majority(75%)→Full(100%)" (§D-1) | (canary_rollback.md P2-3 위임) |
| **LOCK-ML-09** | "QoD 차이>0.2 자동 롤백, 에러율>Current×2 자동 롤백" (§D-3) | §5.2 (ML-09 자동 롤백 검토 분기) |

> **CFL-SE-XREF-4-4-01 정식 채번 큐**: 본 §5 3층 매트릭스 명시로 CROSS_DOMAIN_RECHECK §3.3 잠정 ID는 ISS-5 해결 시점에 SEVO-C005로 정식 채번 (도메인 마감 step 7).

---

## 6. Self-evo 시스템 검증 절차 (DH-1 + 60일 관찰)

### 6.1 DH-1 4메트릭 60일 환산

| 메트릭 (DH-1) | 7일 기준 (DH-1 원본) | 60일 환산 |
|--------------|---------------------|----------|
| 모듈 에러율 | < 1% (7일 관찰) | 60일 중 어느 7일 슬라이딩 윈도우도 1% 초과 ❌ |
| 출력 스키마 검증 | 100% 통과 (7일) | 60일 누계 스키마 검증 통과율 = 100% (단 1건도 실패 ❌) |
| I-Module 경유 호출 성공률 | ≥ 99% | 60일 누계 ≥ 99% (호출 100만건 기준 실패 ≤ 10,000건) |
| 메모리/CPU 사용량 | ≤ 80% | 60일 중 어느 7일 슬라이딩 윈도우도 80% 초과 ❌ |

### 6.2 추가 검증 (TC 도구 self_evo_validator.py 정합)

> **Part2 V3-P2 L6259 verbatim**: "프롬프트 자가 개선 루프: 개선 전/후 성능 비교, 롤백 정상 동작, 거버넌스 규칙 준수 확인 → `self_evo_validator.py` + 감사 로그 분석 → 개선 사이클마다 (자동) → 개선 후 성능 ≥ 개선 전, 금지 규칙 위반 0건, 롤백 성공률 100%"

**EvolutionValidationReport** (§3.5) 작성 시 추가 필드:
- `rollback_test_success_rate`: 60일 내 롤백 테스트 성공률 (목표 100%)
- `governance_violation_count`: 60일 내 거버넌스 위반 (LOCK L4 자동 적용 위반) 건수 (목표 0)

### 6.3 검증 PASS 조건

```python
def is_self_evo_verified(report: EvolutionValidationReport) -> bool:
    """§2.2 Self-evo 시스템 검증 PASS 조건."""
    return (
        report.error_rate_max_7day < 0.01           # 1%
        and report.schema_pass_rate == 1.0          # 100%
        and report.i_module_success_rate >= 0.99    # 99%
        and report.resource_usage_max_7day < 0.80   # 80%
        and report.rollback_test_success_rate == 1.0  # 100%
        and report.governance_violation_count == 0    # 0건
    )
```

---

## 7. V3 비용 승인 흐름 (CostBudget 인터페이스)

### 7.1 60일 비용 누적 검증

> **Part2 V3-P2 L6260 verbatim**: "Hetzner(기본) + RunPod GPU 실제 60일 운영 비용 집계. 예상 대비 ±10% 이내 확인 → `cost_v3_report.py` → 인프라별 비용 분리 집계 → 일 1회 집계 → 월합 ≤ ₩266,000 (ABSOLUTE LOCK), 60일 연속 준수"

| 항목 | 값 | 비고 |
|------|-----|------|
| **월합 상한** | ≤ ₩266,000 | ABSOLUTE LOCK (Part2 V3-P2 L6260) |
| **±10% 이내** | 예상 대비 90% ~ 110% | 예측 정확도 검증 |
| **인프라 분리** | Hetzner + RunPod GPU | 각 인프라별 별도 집계 |
| **집계 주기** | 일 1회 (KST 03:00) | cron job |

### 7.2 일일 10% 초과 알림

본 도메인 6-6 추가 거버넌스 규칙:
- **일일 비용 ≥ ₩266,000 / 30 × 1.10 = ₩9,753 초과 시** I-20 EscalationManager 알림 (severity=WARN)
- **일일 비용 ≥ ₩266,000 / 30 × 1.50 = ₩13,300 초과 시** S-8 admin_required 분기 자동 트리거 (severity=ERROR)

### 7.3 사용자 명시적 승인

> **Part2 V3-P2 §7.4 #14 verbatim**: "사용자 승인 — 위 5개 TC + V3 GO/NO-GO 12항목 전수 통과 후 명시적 승인 → CLI `vamos approve v3-transition` → 1회성 → 승인 이벤트 + 전체 TC 스냅샷 기록"

승인 이벤트 발행 후에만 `safety_checks.v3_cost_approved = True` 처리 가능.

---

## 8. S-8 거버넌스 통합 (P2-1 정합)

### 8.1 ApprovalRequest 라우팅

모든 ModelUpgradeRequest은 S-8 ApprovalRequest로 변환되어 평가:

```python
def to_approval_request(req: ModelUpgradeRequest, plan_id: str,
                        cost_impact_krw_day: float) -> ApprovalRequest:
    """ModelUpgradeRequest → S-8 ApprovalRequest 변환 (P2-1 §2 정합)."""
    return ApprovalRequest(
        request_id        = req.request_id,
        plan_id           = plan_id,
        source_module     = "S-3",                # 또는 "S-6" (제안자)
        routing_reason    = "model_upgrade",      # P2-1 §3.3 admin_required 강제 트리거
        received_at       = req.requested_at,
        eval_deadline     = req.requested_at + timedelta(seconds=600),  # DH-2
        cost_impact       = cost_impact_krw_day,
        repair_result     = None,                  # 모델 업그레이드는 SDAR 경로 X
        proposed_pattern  = None,                  # 모델 업그레이드는 패턴 학습 경로 X
        trace_id          = generate_trace_id(),
    )
```

### 8.2 admin_required 분기 강제

P2-1 §3.3 결정 트리에 따라 `routing_reason="model_upgrade"`는 무조건 `admin_required` 분기 진입 — composite_score와 무관하게 ADMIN+ 수동 승인 필수 (LOCK L10 모델 업그레이드 안전 조건의 위중성 반영).

### 8.3 timeout=600s (DH-2) + 보수적 거부 (L4)

P2-1 §4.3 정합: 600s 내 ADMIN+ 응답 없을 시 `auto_timeout_reject` (자동 적용 절대 금지 — L4).

---

## 9. LOCK 참조 매핑

| LOCK | 항목 | 정본 출처 | 본 문서 반영 위치 |
|------|------|----------|-----------------|
| **L3** | S-8 거버넌스 승인 필수 | D2.0-02 §10.6, SDAR_SPEC §9.3 | §8 (admin_required 분기 강제) |
| **L4** | 자동 적용 절대 금지 | SDAR_SPEC §9.3 | §1.1, §2.4 거부 강제, §8.3 보수적 거부 |
| **L8** | S-2 회귀 테스트 | D2.0-02 §10.6 L3856 | §4.3 (Full 단계 후 회귀) |
| **L10** | **모델 업그레이드 안전 조건** | Part2 V3-P2 L4058 | **§2 3가지 전제 조건 (본 문서 핵심)** |

### 도메인 규칙 참조

| 규칙 | 반영 위치 |
|------|----------|
| **R-66-1** 자동 적용 절대 금지 | §1.1, §8.3 |
| **R-66-3** 회귀 테스트 필수 | §4.3 |
| **R-66-5** 모델 업그레이드 시 카나리 배포 | (canary_rollback.md P2-3 위임) |

---

## 10. DH 매핑

| DH | 항목 | 본 문서 반영 위치 | 비고 |
|----|------|------------------|------|
| **DH-1** | 안정화 4메트릭 | §6.1 60일 환산 + §6.2 추가 검증 | 변경 없음 |
| **DH-2** | S-8 timeout=600s | §8.3 (Part2 ApprovalRequest.eval_deadline) | P2-1 정식 확정 인용 |
| **DH-3** | Policy-based 승인 엔진 | §8.2 admin_required 분기 강제 | P2-1 §3 정합 |

---

## 11. ISS 해결 매트릭스

| ISS | 본 문서 해결 위치 | 검증 |
|-----|------------------|------|
| **ISS-5 (4-4 MLOps 연동 인터페이스)** | §3 model_upgrade_request 6-필드 정본 정의 | exit_gate 핵심 ✅ |
| **CROSS_DOMAIN_RECHECK §3.4 권장조치 1** | §5 3층 QoD 매트릭스 명시 (L10/ML-05/ML-07) | ✅ |
| **CFL-SE-XREF-4-4-01** (잠정) | §5.3 4-4 LOCK 인용 + 도메인 마감 step 7 SEVO-C005 정식 채번 큐 | RESOLVED 예정 |
| §1.3 P4 (모델 업그레이드 안전 조건 미정의) | §2 LOCK L10 3가지 전제 조건 + §3 6-필드 스키마 | ✅ |
| §6.2 ISS-5 추상 정의 위임 수용 | §3.2 6-필드 매핑 표 | ✅ |

---

## 12. 향후 확장 (Phase 3 이월)

- **C-1** (HIGH): 4-4 측 `MLOpsUpgradeReceiver` 인터페이스 작성 후 직수신 채널 확립 ([RECHECK_FLAG: 4-4] 발행)
- **C-2** (MEDIUM): A/B 테스트 메트릭 확장 — latency p99, cost per token, hallucination rate 추가
- **C-3** (LOW): 다중 모델 동시 카나리 (2-tier LLM 최적화 연동) — 현재 단일 모델 가정
- **C-4** (LOW): 자동 회귀 학습 — 회귀 실패 케이스를 S-2 패턴으로 자동 등재

---

## 13. 변경 이력

| 일자 | 변경 | 비고 |
|------|------|------|
| 2026-04-27 | P2-2 V2 NEW 작성 (ISS-5 해결) | model_upgrade_request 6-필드 정본 + 3층 QoD 매트릭스 + CROSS_DOMAIN_RECHECK §3.4 권장조치 1 충족 |
