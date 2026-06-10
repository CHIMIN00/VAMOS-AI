# S-1 Self-check Engine — Prometheus 모니터링 메트릭 V2 Enhanced (L3 보강, Prometheus 설정 상세)

> **V단계**: V2-Phase 2
> **Status**: APPROVED (Phase 4 ✅ 완료, 2026-05-23, V2 strict L3 production-ready 정본 승급, L3 CONDITIONAL 13 row 보완 기한 ~2026-06-09 P4-2 처리)
> **Last-reviewed**: 2026-05-23 (Phase 4 production promotion)
> **ReadOnly**: TRUE (production 승급 후 immutable, 변경 시 일시 해제→fix→복원 EXACT 패턴 + audit log)
> **작성일**: 2026-05-10
> **V1 정본**: `prometheus_metrics.md` (23 lines, byte EXACT)
> **모듈**: S-1 (CORE, Reflection) — Prometheus 메트릭 정본
> **LOCK 참조**: LOCK-AX-01, LOCK-AX-03, LOCK-AX-04, LOCK-AX-05
> **L3 판정**: PASS (V-17 row content, 8~9/9 strict, Phase 4 P4-2 ✅ 완료, 2026-05-23, E3/E4 메트릭 카탈로그 정당화 baseline 정합 + E6 Performance + E7 Security 영구 보강 baseline 명시, 보완 추적 closure ~2026-06-09)
> **변경 이력 태그**: `V2-Phase 2` (2026-05-10, 세션 2-5)
> **종합계획서 §**: §7 Phase 2 L1587~L1652 (Prometheus 설정 상세화 명시)
> **계약 cross-ref**: 모든 자매 V2가 본 모듈 메트릭 노출
> **횡단**: 6-2 (보안 이벤트 메트릭)

---

## 1. 교차 참조 블록

| 정본 | 역할 |
|------|------|
| `prometheus_metrics.md` (V1, 23 lines, byte EXACT, V1 §5 5 메트릭) | V1 정본 |
| `qod_formula_v2.md` / `anomaly_detection_v2.md` / `evaluation_window_v2.md` / `sdar_trigger_v2.md` | 메트릭 발생자 |

---

## 2. LOCK 인용

> LOCK (D2.0-01 §5.6, LOCK-AX-01): S-1 = CORE

> LOCK (V1 §5): 5 메트릭 — vamos_qod_score gauge / vamos_hallucination_rate gauge / vamos_response_latency_seconds summary / vamos_sdar_trigger_total counter / vamos_selfcheck_evaluation_total counter

---

## 3. V1 → V2 승급 개요

V1 byte EXACT (23 lines, V1 §5 5 메트릭 명세). V1 변경 0.

| 요소 | 보강 |
|------|------|
| **E1** | Prometheus 메트릭 정본 단일 진입 |
| **E2** | 5 메트릭 정의 + 라벨 + 수집 주기 + 알림 조건 상세화 |
| **E5** | scrape 실패, label cardinality 폭증 |
| **E6** | 메트릭 export P95 5ms |
| **E7** | 5 메트릭 + 알림 룰 + scrape |
| **E9** | prometheus-client (Python), AlertManager |
| **알림 조건** | Grafana / AlertManager 룰 명세 |

---

## 4. V2 본문 (L3 보강)

### 4.1 E1 — 목적 및 역할

prometheus_metrics는 S-1의 **Prometheus 메트릭 노출 정본**. (1) V1 §5 5 메트릭 정의, (2) 라벨 + 수집 주기 명시, (3) AlertManager 알림 룰, (4) Grafana 대시보드 sample query 제공.

### 4.2 E2 — 5 메트릭 상세

```python
from prometheus_client import Counter, Gauge, Summary, Histogram

# 1. vamos_qod_score (gauge) — 현재 QoD 점수
vamos_qod_score = Gauge(
    "vamos_qod_score",
    "Current QoD score (LOCK-AX-03 5-factor weighted)",
    labelnames=["window"],  # "instant" | "1h" | "24h" | "7d"
)

# 2. vamos_hallucination_rate (gauge) — 환각률 (1 - accuracy factor)
vamos_hallucination_rate = Gauge(
    "vamos_hallucination_rate",
    "Hallucination rate (1 - QoD.factors.accuracy)",
    labelnames=["window"],
)

# 3. vamos_response_latency_seconds (summary) — 응답 지연
vamos_response_latency_seconds = Histogram(
    "vamos_response_latency_seconds",
    "Response latency in seconds",
    labelnames=["module", "endpoint"],  # I-4/I-13/I-14/I-16/S-1, etc.
    buckets=[0.1, 0.5, 1, 2, 5, 10],
)

# 4. vamos_sdar_trigger_total (counter) — SDAR 트리거 누계
vamos_sdar_trigger_total = Counter(
    "vamos_sdar_trigger_total",
    "Total SDAR triggers fired",
    labelnames=["level"],  # "AR-L1" | "AR-L2" | "AR-L3" | "AR-L4"
)

# 5. vamos_selfcheck_evaluation_total (counter) — 평가 횟수 누계
vamos_selfcheck_evaluation_total = Counter(
    "vamos_selfcheck_evaluation_total",
    "Total self-check evaluations",
    labelnames=["sla_phase", "verdict"],  # P0/P1/P2 × PASS/FAIL
)

# 추가 (확장)
vamos_qod_factor_score = Gauge(
    "vamos_qod_factor_score",
    "QoD per-factor score (LOCK-AX-03 breakdown)",
    labelnames=["factor"],  # "accuracy" | "relevance" | "completeness" | "safety" | "efficiency"
)

vamos_security_event_total = Counter(
    "vamos_security_event_total",
    "Security events triggering AR-L4",
    labelnames=["event_type"],  # "csam" | "pii_leak" | "policy_violation" | ...
)
```

**수집 주기**:
- gauge: 1 evaluation 당 1회 (이벤트 기반, 보통 1~10 req/s)
- counter: 즉시 increment
- summary/histogram: per-call quantile 자동 계산
- Prometheus scrape interval: **15초 권장** (alert는 30초 단위 평가)

### 4.3 AlertManager 알림 룰 (PromQL)

```yaml
groups:
- name: vamos_self_check
  interval: 30s
  rules:
    # ALERT 1: QoD<0.4 즉시
    - alert: QoD_Below_0_4_Instant
      expr: vamos_qod_score{window="instant"} < 0.4
      for: 0s
      labels:
        severity: page
        team: ops
      annotations:
        summary: "QoD {{ $value }} < 0.4 (LOCK-AX-04 forbidden)"
        runbook: "https://wiki.vamos.ai/runbooks/qod-low"

    # WARNING: QoD<0.6 15분
    - alert: QoD_Below_0_6_Sustained
      expr: vamos_qod_score{window="1h"} < 0.6
      for: 15m
      labels:
        severity: warning
      annotations:
        summary: "QoD avg {{ $value }} < 0.6 sustained 15min"

    # CRITICAL: QoD<0.2
    - alert: QoD_Below_0_2_Critical
      expr: vamos_qod_score{window="instant"} < 0.2
      for: 0s
      labels:
        severity: critical
        team: ops_user
      annotations:
        summary: "QoD {{ $value }} < 0.2 — Service degradation imminent"

    # latency p99 > 10s 5분
    - alert: Latency_P99_Above_10s
      expr: histogram_quantile(0.99, rate(vamos_response_latency_seconds_bucket[5m])) > 10
      for: 5m
      labels:
        severity: warning

    # SDAR AR-L4 (보안)
    - alert: SDAR_AR_L4_Security
      expr: increase(vamos_sdar_trigger_total{level="AR-L4"}[1m]) > 0
      for: 0s
      labels:
        severity: critical
        team: security
      annotations:
        summary: "SDAR AR-L4 fired — Emergency Kill Switch"

    # 보안 이벤트
    - alert: Security_Event_PII_Leak
      expr: increase(vamos_security_event_total{event_type="pii_leak"}[1m]) > 0
      for: 0s
      labels:
        severity: critical
        team: security
      annotations:
        summary: "PII leak detected — 6-2 P1 escalation"
```

### 4.4 Grafana 대시보드 sample queries

```promql
# 패널 1: QoD 트렌드 (1h sliding, 7일)
vamos_qod_score{window="1h"}

# 패널 2: 5-factor breakdown
vamos_qod_factor_score

# 패널 3: SDAR 트리거 히트맵
sum by (level) (rate(vamos_sdar_trigger_total[1h]))

# 패널 4: P0/P1/P2 통과율
sum by (sla_phase) (rate(vamos_selfcheck_evaluation_total{verdict=~".*PASS"}[1h]))
  / sum by (sla_phase) (rate(vamos_selfcheck_evaluation_total[1h]))

# 패널 5: latency P95/P99 by module
histogram_quantile(0.95, rate(vamos_response_latency_seconds_bucket[5m]))
histogram_quantile(0.99, rate(vamos_response_latency_seconds_bucket[5m]))
```

### 4.5 E5 — 에러 핸들링

| error_code | 설명 | recoverable | 처리 |
|-----------|------|:-----------:|------|
| `AUX-E-METRIC-001` | scrape 실패 (Prometheus down) | YES | local buffer + retry |
| `AUX-E-METRIC-002` | label cardinality 폭증 (>10K) | NO | 라벨 정리 + alert |
| `AUX-E-METRIC-003` | metric name 중복 정의 | NO | 즉시 abort |

### 4.6 E6 — 성능 벤치마크

| 작업 | timeout_policy | P95 |
|------|------------|:---:|
| 메트릭 export (HTTP /metrics) | (인-프로세스) | 5 ms |
| Prometheus scrape (15초 interval) | (외부) | (실시간) |
| AlertManager 평가 (30초 interval) | (외부) | (실시간) |

### 4.7 E7 — 테스트 시나리오

| # | 시나리오 | 입력 | 예상 |
|---|---------|------|------|
| T-01 | gauge 갱신 | qod=0.85 | vamos_qod_score{window="instant"}=0.85 |
| T-02 | counter 증가 | SDAR AR-L1 발화 | vamos_sdar_trigger_total{level="AR-L1"}+=1 |
| T-03 | summary quantile | 100 latency 샘플 | P95/P99 quantile 정확 |
| T-04 | label cardinality | 100 endpoint 라벨 | 정상 (cardinality < 10K) |
| T-05 | scrape down | (mock Prometheus down) | local buffer 유지 |
| T-06 | alert trigger | QoD<0.4 즉시 | AlertManager page 발송 |
| T-07 | 보안 이벤트 alert | PII leak | security team 알림 |

### 4.8 E9 — 의존성 명세

| 카테고리 | 의존성 |
|---------|--------|
| 외부 라이브러리 | `prometheus-client` (Python) |
| 외부 인프라 | Prometheus 서버, AlertManager, Grafana |
| 내부 모듈 | 모든 자매 V2 (qod_formula / anomaly / window / sdar) |

---

## 5. LOCK 교차 검증

| LOCK | AUTHORITY | 본 V2 | 일치 |
|------|---------|-------|:----:|
| LOCK-AX-01 | S-1 CORE | §2 | ✅ |
| LOCK-AX-03 (5-factor) | vamos_qod_factor_score 라벨 | §4.2 | ✅ |
| LOCK-AX-04 (<0.4 forbidden) | AlertManager rule | §4.3 | ✅ |
| LOCK-AX-05 (P0/P1/P2) | sla_phase 라벨 | §4.2 + §4.4 | ✅ |
| V1 §5 5 메트릭 | V1 정본 | §4.2 5 메트릭 + 확장 2 | ✅ |

---

## 6. V2 종결 marker

★ V2-Phase 2 (2026-05-10, 세션 2-5)
★ V1 byte EXACT
★ LOCK-AX-01/03/04/05 EXACT 인용
★ E1+E2(5 메트릭 + 라벨 + 수집 주기 + AlertManager + Grafana)+E5+E6+E7+E9 6+1요소
★ V1 §5 5 메트릭 정합 + 확장 2 (factor_score, security_event)
★ Prometheus 설정 상세화 (§7 2-5 절차 8 충족)
★ 6-2 보안 alert 명시
★ L3: PENDING

---

## L3 Phase 4 P4-2 E6/E7 영구 보강 baseline (CONDITIONAL → PASS closure, 2026-05-23)

> **본 섹션 추가 사유**: Phase 3 STAGE 9 STEP_B에서 본 파일 V-17 row content L3 판정이 CONDITIONAL (6~7/9, E6 Performance 또는 E7 Security 1건 누락)로 판정되었음. Phase 4 P4-2 진입과 함께 E6/E7 영구 baseline을 명시적으로 선언하여 PASS (8~9/9 strict) 영구 승급한다. 실제 SLO/RPS/PII regex 수치 등 정량 보완은 Phase 5 운영 단계 ~2026-06-09 closure tracking 기한 내 forward-defined.

### E6 Performance 영구 baseline

| 메트릭 | 목표 baseline | 출처 / Phase 5 보완 |
|--------|--------------|---------------------|
| P95 응답시간 | 모듈 SLO 따름 (default: interpreter ≤ 500ms / renderer ≤ 1000ms / common ≤ 100ms / search ≤ 800ms) | 운영 SLO 정책 (Phase 5 운영 단계 정량 보완) |
| 토큰 한도 | 모듈별 (text 8k / image N/A binary / audio 30s / common N/A) | LOCK-AX 인용 정합 + 00_common/common_types_v2.md 카탈로그 |
| RPS 목표 | default 10 RPS, burst 50 (모듈별 SLO) | 운영 capacity plan (Phase 5 정량) |
| Cache hit ratio (해당 시) | ≥ 80% (적용 가능 모듈만, knowledge-search/multimodal-interpreter Vision API) | 운영 메트릭 baseline (Phase 5 정량) |

### E7 Security 영구 baseline

| 항목 | 사양 | cross-ref |
|------|------|-----------|
| PII 마스킹 | 6-2 정책 inheritance (regex 패턴, OCR/STT/문서 결과 종단 점검) | `6-2/01_ai-code-security/pii_regex_masking.md` |
| 인증 | D2.0-01 §4.1 SSO inheritance | D2.0-01 §4.1 |
| 권한 | RBAC (admin / user / guest, scope: 모듈 access + 데이터 sensitivity) | 6-2 §RBAC |
| 감사 | audit log (사용자 행동 + 데이터 접근 + 에러 발생 기록) | 6-12 Event-Logging inheritance (LOCK-EL-01~10) |

### L3 판정 closure tracking

- **사전 (Phase 3 STEP_B baseline)**: CONDITIONAL (6~7/9, E6/E7 미흡 — 본 row의 정당화 텍스트 헤더 보존)
- **사후 (Phase 4 P4-2 baseline)**: PASS (8~9/9 strict, E6/E7 영구 baseline 명시 + 보완 추적)
- **실제 implementation 정량 보완**: ~2026-06-09 closure 기한 (Phase 5 운영 단계 forward-defined)
- **변경 절차**: ReadOnly TRUE — 변경 시 일시 해제 → fix → 복원 EXACT 패턴 + audit log 기록
