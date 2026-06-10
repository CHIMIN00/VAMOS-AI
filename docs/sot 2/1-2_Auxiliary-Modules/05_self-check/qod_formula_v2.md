# S-1 Self-check Engine — QoD 점수 체계 V2 Enhanced (L3 보강, LOCK-AX-03 정본 정합)

> **V단계**: V2-Phase 2
> **Status**: APPROVED (Phase 4 ✅ 완료, 2026-05-23, V2 strict L3 PASS production-ready 정본 승급, Phase 3 V-17 PASS inheritance)
> **Last-reviewed**: 2026-05-23 (Phase 4 production promotion)
> **ReadOnly**: TRUE (production 승급 후 immutable, 변경 시 일시 해제→fix→복원 EXACT 패턴 + audit log)
> **작성일**: 2026-05-10
> **V1 정본**: `qod_formula.md` (32 lines, byte EXACT)
> **모듈**: S-1 Self-check Engine (CORE, Reflection)
> **LOCK 참조**: LOCK-AX-01, **LOCK-AX-03 (PLAN-3.0 5-factor 정본)**, LOCK-AX-04 (QoD 임계), LOCK-AX-05 (Self-check 임계 P0/P1/P2), LOCK-AX-13
> **L3 판정**: PASS (V-17 row content, 9/9 또는 8/9, 2026-05-14)
> **변경 이력 태그**: `V2-Phase 2` (2026-05-10, 세션 2-5, chain s9_36_a_2)
> **종합계획서 §**: §7 Phase 2 L1587~L1652 (2-5 S-1 L3 보강 핵심)
> **계약 cross-ref**: C-10 (I-6 → S-1 output metrics), C-11 (S-1 → I-14 QoD ref), C-13 (S-1 → I-25 SDAR event)
> **F-05 이월**: S-1 ↔ I-15 통합 결정 PENDING (STEP_C)
> **F-06 이월**: CORE → S-1 활성화 호출 경로 OOS (STEP_C 등재)
> **F-07 이월**: ABC 단위 테스트 (C-10/C-11/C-13)
> **D-02 인지**: CONFLICT_LOG D-02 — V1 §1 5 메트릭 (V1-006 이전) vs LOCK-AX-03 정본 5-factor 차이. sot 2/ 내부 선조치 완료 (AUTHORITY/registry), V1 본문 byte EXACT 보존, V2는 LOCK 정본 인용. 외부 (D2.0-06 DEC-014/MASTER_SPEC) 갱신 PENDING.
> **횡단**: 6-2 (응답 sanity 검증 시 PII 누출 종단 점검)

---

## 1. 교차 참조 블록

| 정본 | 역할 |
|------|------|
| `AUXILIARY_MODULES_구조화_종합계획서.md` §7 Phase 2 (2-5) | V2 절차 |
| `AUTHORITY_CHAIN.md` §4 LOCK-AX-01/03/04/05 | LOCK 정본 |
| `qod_formula.md` (V1, 32 lines, byte EXACT) | V1 정본 (V1 §1 5 메트릭 보존) |
| `06_mapping/lock_value_registry.md` LOCK-AX-03 (V1-006 PLAN-3.0 5-factor 정본) | LOCK 레지스트리 |
| `06_mapping/interface_contracts.md` C-10/C-11/C-13 | 계약 |
| `CONFLICT_LOG.md` D-02 | 4-factor → 5-factor SUPERSEDED 인지 |
| `00_common/response_envelope.md` (LOCK-AX-11) | evidence.qod 채널 |
| `6-2/01_ai-code-security/pii_regex_masking.md` | 응답 sanity 검증 |

---

## 2. LOCK 인용 (R9 형식)

> LOCK (D2.0-01 §5.6, LOCK-AX-01): S-1 = CORE, change_lock=false (V1:ON / V2:ON / V3:ON)

> LOCK (D2.0-06 DEC-014 → **PLAN-3.0 §11 S11-6 갱신**, LOCK-AX-03 정본): `qod = Accuracy×0.30 + Relevance×0.25 + Completeness×0.20 + Safety×0.15 + Efficiency×0.10` *(5-factor, 가중치 합=1.0). 기존 4-factor (D2.0-06 DEC-014) 는 SUPERSEDED.*

> LOCK (D2.0-06, LOCK-AX-04): `QoD < 0.4 → L2/L3 forbidden, QoD >= 0.7 → L2 allowed`

> LOCK (D2.0-02 §7.53-1, LOCK-AX-05): `Self-check thresholds P0>=70, P1>=75, P2>=80`

---

## 3. V1 → V2 승급 개요

V1 byte EXACT (32 lines, V1 §1 5 메트릭 표 + QoD 합산 공식). V1 변경 0 (D-02 RESOLVED 외부 PENDING으로 V1 본문 정정 보류, V1 immutability 의무).

| 요소 | 보강 |
|------|------|
| **E1** | QoD formula 목적 (LOCK-AX-03 정본 단일 진입) |
| **E2** | 5-factor 산출 의사코드 (Accuracy/Relevance/Completeness/Safety/Efficiency 각 측정) |
| **E4** | IQoDCalculator ABC |
| **E5** | metric 측정 실패, 가중치 합 ≠ 1.0 |
| **E6** | QoD 계산 P95 50ms |
| **E7** | high/low QoD + LOCK-AX-04 임계 + LOCK-AX-05 P0/P1/P2 |
| **E8** | LOCK-AX-03 + LOCK-AX-04 + LOCK-AX-05 명시 참조 |
| **E9** | numpy, transformers (NLI for hallucination) |

---

## 4. V2 본문 (L3 보강)

### 4.1 E1 — 목적 및 역할

qod_formula는 S-1의 **QoD (Quality of Decision) 단일 산출 정본**. **LOCK-AX-03 PLAN-3.0 5-factor** 가 정본:

```
QoD = Accuracy × 0.30 + Relevance × 0.25 + Completeness × 0.20 + Safety × 0.15 + Efficiency × 0.10
```

- 결과 범위: 0.0 ~ 1.0
- LOCK-AX-04 임계: < 0.4 → L2/L3 사용 금지, ≥ 0.7 → L2 허용
- LOCK-AX-05 임계: P0 ≥ 70 (시작), P1 ≥ 75 (개선), P2 ≥ 80 (운영)

**D-02 인지**: V1 본문 5 메트릭 (accuracy/latency/hallucination_rate/user_satisfaction/cost_efficiency) 은 PLAN-3.0 갱신 이전 (V1-006 이전) 의 4-factor 변형. AUTHORITY_CHAIN.md / lock_value_registry.md 는 LOCK-AX-03 5-factor 로 정정 완료. V1 본문은 byte EXACT 보존 (V1 immutability), V2 산출은 LOCK 정본 5-factor.

### 4.2 E2 + E4 — 5-factor 의사코드 + ABC

```python
class QoDFactors(BaseModel):
    accuracy: float       # 0~1
    relevance: float      # 0~1
    completeness: float   # 0~1
    safety: float         # 0~1
    efficiency: float     # 0~1

class QoDScore(BaseModel):
    score: float          # 0~1, LOCK-AX-03 가중 합
    factors: QoDFactors
    breakdown: dict[str, float]  # {factor_name: weighted_contribution}
    verdict_lock_ax_04: Literal["L2_L3_FORBIDDEN", "STANDARD", "L2_ALLOWED"]
    verdict_lock_ax_05: Literal["P0_PASS", "P0_FAIL", "P1_PASS", "P1_FAIL", "P2_PASS", "P2_FAIL"]
    timestamp: str | None = None  # ISO 8601 평가 시각 (anomaly_detection sustained-window 평가용; calculate() 설정)
    timestamp: str | None = None  # ISO 8601 평가 시각 (anomaly_detection sustained-window 평가용; calculate() 설정)

class IQoDCalculator(ABC):
    @abstractmethod
    async def calculate(
        self,
        response_metrics: ResponseMetrics,  # I-6 → S-1 (C-10) 입력
        sla_phase: Literal["P0", "P1", "P2"] = "P1",
    ) -> QoDScore: ...

class QoDCalculator(IQoDCalculator):
    # LOCK-AX-03 정본 가중치 (불변)
    WEIGHTS = {
        "accuracy": 0.30,
        "relevance": 0.25,
        "completeness": 0.20,
        "safety": 0.15,
        "efficiency": 0.10,
    }

    async def calculate(self, response_metrics, sla_phase="P1") -> QoDScore:
        # 1. 가중치 무결성 검증 (LOCK 변조 차단)
        if abs(sum(self.WEIGHTS.values()) - 1.0) > 1e-6:
            raise AuxError("AUX-E-LOCK-001", "LOCK-AX-03 weight sum != 1.0")
        if self.WEIGHTS != {"accuracy": 0.30, "relevance": 0.25, "completeness": 0.20, "safety": 0.15, "efficiency": 0.10}:
            raise AuxError("AUX-E-LOCK-001", "LOCK-AX-03 weights modified")

        # 2. 5 factor 측정 (각 sub-routine, 0~1 scale)
        accuracy = await self._measure_accuracy(response_metrics)        # NLI / fact-check 통과율
        relevance = await self._measure_relevance(response_metrics)      # query-response cosine sim
        completeness = await self._measure_completeness(response_metrics) # 요구사항 충족 비율
        safety = await self._measure_safety(response_metrics)             # PII / 정책 위반 부재
        efficiency = await self._measure_efficiency(response_metrics)     # token-quality / latency 효율

        factors = QoDFactors(
            accuracy=accuracy, relevance=relevance, completeness=completeness,
            safety=safety, efficiency=efficiency,
        )

        # 3. LOCK-AX-03 정본 가중 합
        score = (
            accuracy * self.WEIGHTS["accuracy"]
            + relevance * self.WEIGHTS["relevance"]
            + completeness * self.WEIGHTS["completeness"]
            + safety * self.WEIGHTS["safety"]
            + efficiency * self.WEIGHTS["efficiency"]
        )
        breakdown = {k: getattr(factors, k) * v for k, v in self.WEIGHTS.items()}

        # 4. LOCK-AX-04 임계 verdict
        if score < 0.4:
            verdict_04 = "L2_L3_FORBIDDEN"
        elif score >= 0.7:
            verdict_04 = "L2_ALLOWED"
        else:
            verdict_04 = "STANDARD"

        # 5. LOCK-AX-05 P0/P1/P2 임계 (점수 → 100 기준)
        score_100 = score * 100
        thresholds = {"P0": 70, "P1": 75, "P2": 80}
        if score_100 < thresholds[sla_phase]:
            verdict_05 = f"{sla_phase}_FAIL"
        else:
            verdict_05 = f"{sla_phase}_PASS"

        return QoDScore(score=score, factors=factors, breakdown=breakdown,
                       verdict_lock_ax_04=verdict_04, verdict_lock_ax_05=verdict_05)

    async def _measure_safety(self, metrics) -> float:
        # 6-2 PII 누출 검사 (1.0 = 완전 안전, 0.0 = 누출)
        pii_leaks = pii_masker.detect_unmask(metrics.response_text)
        if pii_leaks:
            return 0.0  # 즉시 safety=0
        # 정책 위반 (NeMo / Guardrails 결과)
        policy_pass = 1.0 if metrics.policy_passed else 0.5
        return policy_pass
```

### 4.3 E5 — 에러 핸들링

| error_code | 설명 | recoverable | 처리 |
|-----------|------|:-----------:|------|
| `AUX-E-LOCK-001` | LOCK-AX-03 가중치 변조 | NO | 즉시 abort + 무결성 알림 |
| `AUX-E-QOD-001` | factor 측정 실패 (예: NLI 모델 unavailable) | YES | 해당 factor=0.5 default + WARN |
| `AUX-E-QOD-002` | response_metrics 입력 부족 | NO | 거부 + audit |
| `AUX-E-PII-002` | safety factor에서 PII 누출 검출 | YES | safety=0.0 + 6-2 P1 알림 |

### 4.4 E6 — 성능 벤치마크

| 작업 | timeout_policy | P95 |
|------|------------|:---:|
| accuracy (NLI 모델) | LLM 추론 (로컬) | 200 ms |
| relevance (cosine) | (인-프로세스, 임베딩 사전 캐시) | 10 ms |
| completeness (rule) | (인-프로세스) | 5 ms |
| safety (PII + policy) | (인-프로세스) | 30 ms |
| efficiency (token / latency) | (인-프로세스) | 5 ms |
| **전체 P95** | (복합) | **300 ms** |

### 4.5 E7 — 테스트 시나리오

| # | 시나리오 | 입력 | 예상 |
|---|---------|------|------|
| T-01 | 정상: 모든 factor 0.9 | factors all=0.9 | score=0.9, L2_ALLOWED, P2_PASS |
| T-02 | 낮음: factors 0.3 | all=0.3 | score=0.3, L2_L3_FORBIDDEN |
| T-03 | LOCK-AX-04 경계 (0.4) | score=0.4 | STANDARD (≥0.4) |
| T-04 | LOCK-AX-04 경계 (0.7) | score=0.7 | L2_ALLOWED |
| T-05 | LOCK-AX-05 P1 경계 (75) | score=0.75 | P1_PASS |
| T-06 | safety=0 (PII 누출) | (mock PII leak) | safety=0, score 감소 + 6-2 P1 |
| T-07 | LOCK 변조 시도 | weights 변경 | AUX-E-LOCK-001 abort |
| T-08 | F-07 ABC 테스트 (C-10) | I-6 → S-1 metrics | QoDScore 정합 |

### 4.6 E8 — LOCK 명시 참조

본 V2는 다음 LOCK을 본문에 명시 참조:

| LOCK | 위치 | 인용 형식 |
|------|------|----------|
| LOCK-AX-03 (PLAN-3.0 5-factor) | §2 + §4.1 + §4.2 WEIGHTS | "qod = Accuracy×0.30 + ..." 원문 그대로 |
| LOCK-AX-04 (QoD 임계) | §4.2 verdict_04 + §4.5 T-03/T-04 | "<0.4 L2/L3 forbidden, >=0.7 L2 allowed" |
| LOCK-AX-05 (P0/P1/P2 임계) | §4.2 verdict_05 + §4.5 T-05 | "P0>=70, P1>=75, P2>=80" |
| LOCK-AX-13 (S0~S8 state machine, S3 Decision Lock) | §1 + §6 (간접) | composite_output_v2 cross-ref |

### 4.7 E9 — 의존성 명세

| 카테고리 | 의존성 |
|---------|--------|
| 외부 라이브러리 (NLI) | `transformers` (NLI 모델 - DeBERTa-v3-base-mnli 등) |
| 외부 라이브러리 | `sentence-transformers` (cosine sim for relevance), `numpy` |
| 내부 모듈 | `00_common/response_envelope` (evidence.qod 채널), `00_common/error_taxonomy` |
| 내부 모듈 | `anomaly_detection_v2`, `evaluation_window_v2`, `sdar_trigger_v2`, `prometheus_metrics_v2` (자매) |
| 횡단 도메인 | `6-2/01_ai-code-security/pii_regex_masking` (safety factor) |

---

## 5. LOCK 교차 검증

| LOCK | AUTHORITY 값 | 본 V2 | 일치 |
|------|------------|------------|:----:|
| LOCK-AX-01 | S-1 CORE | §2 | ✅ |
| LOCK-AX-03 | PLAN-3.0 5-factor (Accuracy 0.30 / Relevance 0.25 / Completeness 0.20 / Safety 0.15 / Efficiency 0.10) | §2 + §4.2 WEIGHTS + 변조 차단 abort | ✅ |
| LOCK-AX-04 | <0.4 forbidden / ≥0.7 allowed | §4.2 verdict_04 | ✅ |
| LOCK-AX-05 | P0≥70 / P1≥75 / P2≥80 | §4.2 verdict_05 | ✅ |
| 가중치 합 | 0.30+0.25+0.20+0.15+0.10 = 1.0 | §4.2 WEIGHTS sum check | ✅ |
| D-02 인지 | V1 5 메트릭 (V1-006 이전) ≠ LOCK-AX-03 5-factor | §3 + §4.1 명시 (외부 D2.0-06 갱신 PENDING) | ✅ |

---

## 6. V2 종결 marker

★ V2-Phase 2 (2026-05-10, 세션 2-5)
★ V1 byte EXACT (D-02 외부 갱신 PENDING으로 V1 본문 보류)
★ LOCK-AX-01/03/04/05 EXACT 인용
★ E1+E2(5-factor 의사코드)+E4 ABC+E5+E6+E7+**E8 LOCK 명시 참조**+E9 7+1요소
★ C-10/C-11/C-13 baseline
★ F-05/F-06/F-07 이월 (STEP_C)
★ D-02 RESOLVED 인지 (sot 2/ 내부 선조치)
★ 6-2 PII safety factor 명시
★ L3: PENDING
