# C-2 Math Verifier — Monitoring Metrics

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
| 종합계획서 §7 | `VERIFIER_REASONING_ENGINES_구조화_종합계획서.md` P2-7 | 대조 기준 5건 정의 |
| LOCK 정본 | `AUTHORITY_CHAIN.md` §4 LOCK-VR-01, VR-05, VR-12 | 임계값 / 판정 / SLA |
| Spec | `02_math-verifier/spec.md` | C-2 인터페이스 및 알고리즘 |
| Error handling | `02_math-verifier/error_handling.md` | 에러 코드 14종 |
| ABC 정본 | `00_common/base_verifier_abc.md` | verify() 시그니처 |
| Confidence | `00_common/confidence_thresholds.md` | LOCK-VR-05 임계값 |
| OC 통합 | `06_dependency-graph/orange_core_integration.md` §5.4 | `math_verify_check` chain_used 제안 |
| 교차 도메인 | **6-12 Event-Logging** (READ-only) | oc.i1~i5 / BRAIN_FAILOVER 정본 |
| PART2 | V1-Phase 3 (L2140~2147) | 구현 가이드 |

### 1.1 상위 SoT 정책 (v2.2)

- **UPSTREAM_SOT=null** → 상위 SoT 직접 Read = **SKIP** (1-1 횡단 도메인).

### 1.2 cross-check 결과 (v2.1 §4.1~§4.3)

- §4.1: `AUTHORITY_CHAIN.md` LOCK-VR-01/05/12 원문 Read 확인.
- §4.2: `02_math-verifier/_index.md` priority 컬럼 일관 처리.
- §4.3: C-2 Math Verifier ↔ `math_verify_check` chain_used 매핑 확인 (ORANGE CORE 컨펌 필요 — [CONFLICT_CANDIDATE]).

---

## 2. LOCK 정본 참조

> LOCK (D2.0-02 §7.53-1 — LOCK-VR-01): Self-check 임계값 P0≥70, P1≥75, P2≥80
> LOCK (상세명세 C-1 §4 — LOCK-VR-05): ≥0.8 PASS, 0.5~0.8 REVIEW, <0.5 FAIL
> LOCK (D2.0-02 §2.3-B — LOCK-VR-12): 단일응답 ≤2s, 복합응답 ≤10s, Self-check ≤1s

---

## 3. 공통 메트릭 5종

### 3.1 M-COM-01 — Latency

| 항목 | 값 |
|------|---|
| 메트릭 ID | `vre.c2.math.latency_ms` (p50/p95/p99) |
| 태그 | `engine=C-2`, `mode={symbolic,numeric,hybrid}`, `trace_id` |
| 보존 | 30일 원시 / 1년 집계 |

**임계값 (LOCK-VR-12)**:
| 구간 | p95 | WARNING | CRITICAL |
|------|-----|---------|----------|
| 단일응답 | ≤2,000 ms | p95 > 1,600 ms | p95 > 2,000 ms |
| 복합응답 | ≤10,000 ms | p95 > 8,000 ms | p95 > 10,000 ms |
| Self-check | ≤1,000 ms | p95 > 800 ms | p95 > 1,000 ms |

> **주의**: SymPy 수학 처리 특성상 단일응답이라도 기호 단순화가 깊어지면 p95가 쉽게 상승. mode 태그로 세분화 권장.

### 3.2 M-COM-02 — Throughput

- ID: `vre.c2.math.requests_per_sec`
- WARNING: 5분 연속 용량 80% 초과
- CRITICAL: 5분 연속 용량 100% 초과 또는 queue backlog > 50

### 3.3 M-COM-03 — Error Rate

- ID: `vre.c2.math.error_rate`
- 태그: `error_code` (error_handling.md 14종)
- WARNING: ≥ 20% (5분 윈도우, LOCK-VR-01 P2≥80 기반)
- CRITICAL: = 100% (10분 윈도우)

### 3.4 M-COM-04 — Confidence 분포 (LOCK-VR-05)

- ID: `vre.c2.math.confidence_histogram` (bin=0.05)
- 파생: pass_rate, review_rate, fail_rate
- WARNING: fail_rate > 15% 또는 review_rate > 40%
- CRITICAL: fail_rate > 30%

### 3.5 M-COM-05 — Resource Usage

- ID: `vre.c2.math.cpu_pct` / `vre.c2.math.mem_mb` / `vre.c2.math.gpu_pct`
- WARNING: 70% (5분 연속)
- CRITICAL: 90% (2분 연속)

---

## 4. C-2 고유 메트릭

### 4.1 M-C2-06 — 검증 정확도

| 항목 | 값 |
|------|---|
| 메트릭 ID | `vre.c2.math.verification_accuracy` |
| 정의 | 검증 결과(PASS/FAIL)가 정답 라벨(GT)과 일치한 비율 |
| 단위 | % |
| 집계 | 시간당 1회 |
| WARNING | < 90% |
| CRITICAL | < 80% |

### 4.2 M-C2-07 — 수치 vs 기호 일치율

| 항목 | 값 |
|------|---|
| 메트릭 ID | `vre.c2.math.numeric_symbolic_agreement` |
| 정의 | 동일 입력에 대한 수치 검증과 기호 검증 결과 일치 비율 |
| 단위 | % |
| 집계 | 요청당 기록, 10분 윈도우 집계 |
| WARNING | < 95% |
| CRITICAL | < 85% |

### 4.3 M-C2-08 — 오차 범위 내 비율

| 항목 | 값 |
|------|---|
| 메트릭 ID | `vre.c2.math.within_tolerance_ratio` |
| 정의 | 수치 검증에서 허용 오차(ε=1e-6 기본) 내 결과 비율 |
| 단위 | % |
| 태그 | `tolerance_level` (strict / normal / loose) |
| WARNING | < 98% (normal) |
| CRITICAL | < 90% (normal) |

### 4.4 M-C2-09 — chain_length (chain_used 재사용)

> **[CONFLICT_CANDIDATE]**: `math_verify_check` 명칭은 ORANGE CORE 컨펌 대상 (P1 이연, P2-6에서 보고됨).

| 항목 | 값 |
|------|---|
| 메트릭 ID | `vre.c2.math.chain_length` |
| 정의 | Decision.verify.chain_used 배열 길이 (P2-6 동일 구조 재사용) |
| WARNING | > 7 |
| CRITICAL | > 10 |

---

## 5. 6-12 Event-Logging 연동

### 5.1 oc.i1~i5 매핑 (6-12 정본 READ-only)

| 이벤트 | C-2 연동 |
|--------|----------|
| `oc.i1` | latency 측정 시작 |
| `oc.i2` | verify() 호출 카운트 ++ |
| `oc.i3` | confidence 히스토그램 적재 + accuracy GT 비교 |
| `oc.i4` | Self-check latency 종료 |
| `oc.i5` | 전체 latency 집계 |

### 5.2 BRAIN_FAILOVER 연동

| 메트릭 | 설명 |
|--------|------|
| `vre.c2.math.brain_failover_count` | Layer 1 Brain 전환 카운트 |
| `vre.c2.math.brain_active` | `gpt-4o` / `claude-sonnet` / `ollama` (LOCK-VR-07) |

WARNING: ≥ 3/hr / CRITICAL: Fallback Chain 소진 (`OC_I20_BRAIN_EXHAUSTED`).

### 5.3 OC_I20_* 참조 정책

> **INFRA 이관**: `OC_I20_*` 코드는 6-12 Event-Logging Phase 2 INFRA 확정 대상. 본 문서는 레이블 스키마와 알림 연결 가이드만 제공 (정식 등록 금지).

---

## 6. 로깅 포맷 (R-01-7 중첩 JSON)

```json
{
  "timestamp": "2026-04-18T10:30:00.123Z",
  "trace_id": "tr_abc123",
  "decision_id": "dec_xyz789",
  "engine": "C-2",
  "engine_name": "math-verifier",
  "event": "verify.completed",
  "metrics": {
    "latency_ms": 1850,
    "confidence": 0.92,
    "chain_length": 2,
    "numeric_symbolic_agree": true,
    "tolerance_used": 1e-6,
    "within_tolerance": true
  },
  "error": {
    "code": "C2_INFINITE_LOOP",
    "severity": "WARNING",
    "recoverable": true
  },
  "context": {
    "mode": "hybrid",
    "expression_depth": 12,
    "phase": "P2"
  },
  "recovery": {
    "strategy": "fallback_to_numeric_only",
    "attempt": 1,
    "max_attempts": 1,
    "escalated_to": null
  }
}
```

---

## 7. 대시보드 구성 가이드

### 7.1 패널 배치 (4x3)

| 위치 | 패널 | 메트릭 | 갱신 주기 |
|------|------|--------|----------|
| 1,1 | Latency Trend | M-COM-01 | 10초 |
| 1,2 | Throughput | M-COM-02 | 10초 |
| 1,3 | Error Rate by Code | M-COM-03 | 30초 |
| 2,1 | Confidence Histogram | M-COM-04 | 1분 |
| 2,2 | PASS/REVIEW/FAIL % | 파생 | 1분 |
| 2,3 | Resource | M-COM-05 | 30초 |
| 3,1 | Verification Accuracy | M-C2-06 | 5분 |
| 3,2 | Numeric vs Symbolic Agreement | M-C2-07 | 1분 |
| 3,3 | Within Tolerance % | M-C2-08 | 1분 |
| 4,1 | BRAIN_FAILOVER | §5.2 | 실시간 |
| 4,2 | SLA (LOCK-VR-12) | 파생 | 1분 |
| 4,3 | QoD vs P2≥80 (LOCK-VR-01) | 파생 | 5분 |

### 7.2 갱신 주기 / 7.3 보존 기간

- 실시간 (≤10초): latency, throughput
- 단기 (30초~1분): error, confidence, agreement, tolerance
- 중기 (5분): accuracy
- 보존: 메트릭 30일 원시 / 1년 집계, 구조화 로그 14일 / 90일 샘플링, SLA 위반 90일 / 3년 감사

---

## 8. Phase 3 테스트 시나리오 (10건+)

| # | 시나리오 | 조건 | 기대 알림 | 근거 |
|---|---------|------|----------|------|
| TS-01 | 단일응답 p95 임계 초과 | p95=1,700ms (10분) | WARNING | LOCK-VR-12 |
| TS-02 | 단일응답 SLA 위반 | p95=2,100ms (5분) | CRITICAL | LOCK-VR-12 |
| TS-03 | 복합응답 SLA 위반 | 복합 p95=10,500ms | CRITICAL | LOCK-VR-12 |
| TS-04 | Self-check SLA 위반 | p95=1,100ms | CRITICAL | LOCK-VR-12 |
| TS-05 | Error rate 급등 | 25% (5분) | WARNING | LOCK-VR-01 |
| TS-06 | FAIL 급등 | fail_rate=32% | CRITICAL | LOCK-VR-05 |
| TS-07 | 검증 정확도 저하 | accuracy=78% (일별) | CRITICAL | M-C2-06 |
| TS-08 | 수치/기호 불일치 | agreement=82% (10분) | CRITICAL | M-C2-07 |
| TS-09 | 허용 오차 위반 | within_tolerance=85% | CRITICAL | M-C2-08 |
| TS-10 | SymPy 타임아웃 폭증 | `C2_INFINITE_LOOP` 5분 내 50회 | WARNING | error_handling.md |
| TS-11 | BRAIN_FAILOVER 연쇄 | 1시간 4회 | WARNING | §5.2 |
| TS-12 | Fallback 소진 | `OC_I20_BRAIN_EXHAUSTED` | CRITICAL | §5.2 |
| TS-13 | chain_length 비대 | = 12 | CRITICAL | M-C2-09 |

---

## 9. ABC 시그니처 정합 (LOCK-VR-11)

> LOCK (상세명세 C-1 §3 — LOCK-VR-11): ABC Ask→Bridge→Confirm, 시그니처 변경 불가.

모니터링은 계측 훅으로만 삽입. `verify(VerifyRequest) → VerifyResult` 시그니처 보존.

```python
@metrics.observe(engine="C-2", metric_set="vre.c2.math")
async def verify(self, request: VerifyRequest) -> VerifyResult:
    ...
```

---

## 10. 검증 체크리스트 (§7 P2-7 대조 기준 5건)

- [x] G2-3 기여: `02_math-verifier/monitoring_metrics.md` 완성
- [x] 메트릭 5종 이상: 공통 5 + 고유 4 = **9종**
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

**End of C-2 Math Verifier monitoring_metrics.md (v1.0)**
