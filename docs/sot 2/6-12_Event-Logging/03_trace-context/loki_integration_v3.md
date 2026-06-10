# Loki 통합 V3 — Grafana 7 panel + Alertmanager + V3 FailureCode 4건 알림 — V3 production 정본

> **도메인**: 6-12_Event-Logging / 03_trace-context
> **파일**: `loki_integration_v3.md`
> **정본 선언**: 본 파일은 SOT2 정본(Single Source of Truth)이며, V2 Loki LogQL 6 패턴(structured_logging.md, P2-2) 을 base 로 한 **V3 Loki 통합 완성** — Grafana 7 panel 대시보드 + Alertmanager 룰 + V3 FailureCode 4건(EXP_*) 알림 통합 + 분산 추적 자동화 에 대해 권위를 가진다.
> **버전**: v3.0.0 (2026-06-03, Phase 4 production promotion)
> **세션**: P4-2 (Phase 4 RECOVERY Stage A+B 통합, Wave 3 #25 = DAG #29 마지막 derivation ★ 도메인)
> **Status**: **APPROVED ✅** (Phase 4 production promotion — DRAFT → APPROVED)
> **LOCK 연계**: LOCK-EL-08 (W3C Trace Context V3 Loki buildout), LOCK-EL-03 (V3 FC 4건 EXP_*), LOCK-EL-04 (V3 FB 4건), LOCK-EL-05 (FC→FB 매핑 정본 Part2 §6.9, 변경 0), LOCK-EL-07 (V3 알림 권고 레벨)

---

## §0. 교차 참조 (Cross-References)

| 문서 | 경로 | 용도 |
|------|------|------|
| structured_logging.md (P2-2) | `./structured_logging.md` | V2 Loki LogQL 6 패턴 base (716L) |
| trace_propagation.md (P2-1) | `./trace_propagation.md` | W3C Trace Context Level 1 (895L) |
| version_evolution.md (P4-1) | `./version_evolution.md` | V0→V3 진화 로드맵 + V3 FC 4건 §3 |
| failure_code_registry_v2.md (P4-2 v3) | `../02_logging-standard/failure_code_registry_v2.md` | V3 FC 4건 EXP_* §V3 |
| 6-5 SDAR AUTHORITY | `../../6-5_SDAR-System/AUTHORITY_CHAIN.md` | DH-4 repair_result + SDAR FC cross-ref (read-only) |
| 6-9 BAH AUTHORITY | `../../6-9_Brain-Adapter-HAL/AUTHORITY_CHAIN.md` | LOCK-69-8 폴백 체인 cross-ref (read-only) |
| Part2 §6.11 | `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` L5788-5975 | When/Where 정본 |

---

## §1. V2 → V3 Loki 통합 확장 개요

V2 단계의 Loki LogQL 6 패턴 (structured_logging.md §6) 을 base 로, V3 단계는 **운영 자동화** 를 완성한다. LOCK-EL-08 (W3C Trace Context 호환 + correlation_id 필수 전파) 의 buildout 이며 LOCK 정의 변경이 아니다.

| 구성 요소 | V2 (base) | V3 (본 파일) |
|----------|-----------|-------------|
| 로그 수집 | Docker json-file driver → Promtail → Loki | + 분산 추적 자동 라벨링 (trace_id/correlation_id) |
| 쿼리 | LogQL 6 패턴 (structured_logging §6) | + Grafana 7 panel 대시보드 |
| 알림 | (미구성) | Alertmanager 룰 + V3 FC 4건 알림 |
| 라벨 카디널리티 | 정책 base (W-2 RESOLVED) | V3 정책 (cl.rt.* / sdar.* 고카디널리티 제어) |

---

## §2. Grafana 7 panel 대시보드 정본

V3 Grafana 대시보드는 7개 panel 로 구성된다. 각 panel 은 LogQL 쿼리 또는 메트릭 쿼리를 사용한다.

| # | Panel | 유형 | 쿼리 (LogQL/메트릭) | 용도 |
|---|-------|------|---------------------|------|
| 1 | Event Volume by Namespace | Time series | `sum by (namespace) (rate({job="vamos"} | json | __error__="" [5m]))` | 8 네임스페이스별 이벤트율 |
| 2 | FailureCode Rate | Time series | `sum by (failure_code) (rate({job="vamos"} | json | failure_code=~".+" [5m]))` | 48 FC 발생률 |
| 3 | Trace Latency p95 | Heatmap | `quantile_over_time(0.95, {job="vamos"} | json | unwrap latency_ms [5m])` | 추적 지연 분포 |
| 4 | NEVER_AUTO Events | Logs | `{job="vamos"} | json | failure_code=~"OC_I5_POLICY_BLOCK|POLICY_DENY|PII_LONGTERM_DENIED"` | LOCK-EL-06 강제 CRITICAL |
| 5 | V3 EXP_* FailureCodes | Logs | `{job="vamos"} | json | failure_code=~"EXP_.+"` | V3 FC 4건 추적 |
| 6 | Fallback Trigger Map | Table | `sum by (failure_code, fallback_id) (count_over_time({job="vamos"} | json | fallback_triggered="true" [1h]))` | FC→FB 매핑 실행 |
| 7 | correlation_id Missing Rate | Stat | `count_over_time({job="vamos"} | json | correlation_id="" [5m]) / count_over_time({job="vamos"} [5m])` | LOCK-EL-08 누락률 (목표 0%) |

> **라벨 카디널리티 정책 (W-2 RESOLVED 정합)**: `namespace` / `failure_code` / `level` 만 Loki 인덱스 라벨로 승격. `trace_id` / `correlation_id` / `node_id` 등 고카디널리티 필드는 **structured payload(json)** 내부로 유지 (인덱스 라벨 금지). 6-13 Operations 보존/모니터링 경계 보존.

---

## §3. Alertmanager 룰 정본 (V3 FailureCode 4건 알림)

V3 FailureCode 4건(EXP_*) + NEVER_AUTO 3코드는 Alertmanager 룰로 자동 알림된다. LOCK-EL-07 권고 레벨 매핑 준수.

| # | 알림 룰 | 트리거 (LogQL) | 레벨 (LOCK-EL-07 권고) | 라우팅 |
|---|--------|----------------|------|--------|
| 1 | `EXP_SELF_EVO_REGRESSION` | `count_over_time({failure_code="EXP_SELF_EVO_REGRESSION"} [5m]) > 0` | WARN | 6-6 Self-Evolution (FB_EVO_ROLLBACK + 거버넌스 로그) |
| 2 | `EXP_AGENT_SPAWN_LIMIT` | `count_over_time({failure_code="EXP_AGENT_SPAWN_LIMIT"} [5m]) > 3` | WARN | 6-3 Agent-Teams (FB_AGENT_QUEUE) |
| 3 | `EXP_GPU_OOM` | `count_over_time({failure_code="EXP_GPU_OOM"} [1m]) > 0` | ERROR | 인프라 on-call (FB_GPU_OFFLOAD CPU 오프로드) |
| 4 | `EXP_A2A_AUTH_FAIL` | `count_over_time({failure_code="EXP_A2A_AUTH_FAIL"} [5m]) > 5` | ERROR | 보안 (FB_A2A_RETRY mTLS 재시도 3회) |
| 5 | `NEVER_AUTO_BLOCK` | `count_over_time({failure_code=~"OC_I5_POLICY_BLOCK|POLICY_DENY|PII_LONGTERM_DENIED"} [1m]) > 0` | CRITICAL | LOCK-EL-06 강제 격상 (자동 폴백 금지) |
| 6 | `correlation_id_missing` | panel 7 누락률 > 1% | WARN | 6-12 추적 표준 위반 |
| 7 | `trace_latency_p95_high` | panel 3 p95 > 10ms (E6 목표) | WARN | 성능 경고 |

> **NEVER_AUTO 강제 (LOCK-EL-06)**: 알림 룰 5번은 자동 Fallback 실행을 **금지** 하고 CRITICAL 격상 + 인간 결재만 허용 (OC_I5_POLICY_BLOCK / POLICY_DENY / PII_LONGTERM_DENIED 3코드). 자동 RESOLVE 금지 원칙 준수.

---

## §4. V3 FailureCode 4건 Loki 알림 연계 (EXP_*)

| V3 FC | Loki 라벨 | 알림 레벨 (LOCK-EL-07) | Fallback (V3, canonical) | cross-ref |
|-------|----------|----------|---------------|-----------|
| `EXP_SELF_EVO_REGRESSION` | `failure_code="EXP_SELF_EVO_REGRESSION"` | WARN | `FB_EVO_ROLLBACK` (AUTO) | 6-6 Self-Evolution V3 |
| `EXP_AGENT_SPAWN_LIMIT` | `failure_code="EXP_AGENT_SPAWN_LIMIT"` | WARN | `FB_AGENT_QUEUE` (AUTO) | 6-3 Agent Mesh V3 |
| `EXP_GPU_OOM` | `failure_code="EXP_GPU_OOM"` | ERROR | `FB_GPU_OFFLOAD` (AUTO, CPU 오프로드) | vLLM 인프라 V3 |
| `EXP_A2A_AUTH_FAIL` | `failure_code="EXP_A2A_AUTH_FAIL"` | ERROR | `FB_A2A_RETRY` (AUTO, mTLS 재시도 3회) | A2A 프로토콜 V3 |

- LOCK-EL-03 48 = 44+4 (EXP_* 4건) — 합계 보존 EXACT (재정의 0).
- LOCK-EL-04 V3 Fallback 4건 (FB_EVO_ROLLBACK/FB_AGENT_QUEUE/FB_GPU_OFFLOAD/FB_A2A_RETRY) — fallback_registry §4 items 32~35 canonical 정본 (재정의 0).
- LOCK-EL-05 FC→FB 매핑 정본 = Part2 §6.9 (변경 0) — fc_fb_mapping §3.12 rows 45~48 canonical.

> **D-P4-2-1 reconcile**: 본 V3 4건은 **EXP_\*** 이며, 6-5 SDAR cross-ref 의 SDAR_REPAIR_FAIL/SDAR_SNAPSHOT_CORRUPT(V2 FC) 와 별개이다 (명명 conflation reconcile, version_evolution.md §3 정합).

---

## §5. cross-ref 실존 (read-only, 외부 source 0 touch)

| 대상 | 내용 | 처리 |
|------|------|------|
| 6-5 SDAR (DH-4 repair_result) | SDAR 자가진단 repair_result 이벤트 → Loki 추적 (W-1 RESOLVED 정합: 6-12 레지스트리, 6-5 실행) | read-only (source 0 touch) |
| 6-9 BAH (LOCK-69-8 폴백 체인) | Brain-Adapter-HAL 폴백 체인 → V3 FC 알림 라우팅 연계 | read-only (source 0 touch) |
| 6-13 Operations (W-2 RESOLVED) | Loki 보존 정책 + Grafana 모니터링 대시보드 운영 (경계: 6-12 발행 표준, 6-13 보존/모니터링) | Wave 4 forward-defined |

---

## §6. LOCK-EL 재정의 0 + 자체 검증 체크리스트

| # | 검증 항목 | 결과 |
|---|---------|------|
| V-1 | LOCK-EL-08 V3 Loki buildout (재정의 0) | ✅ §1 |
| V-2 | Grafana 7 panel 정본 | ✅ §2 (7/7) |
| V-3 | Alertmanager 룰 7건 (V3 FC 4 + NEVER_AUTO + 추적 2) | ✅ §3 (7/7) |
| V-4 | V3 FC 4건 EXP_* Loki 알림 연계 | ✅ §4 |
| V-5 | LOCK-EL-03 48=44+4 합계 보존 | ✅ §4 |
| V-6 | LOCK-EL-04 V3 FB 4건 | ✅ §4 |
| V-7 | LOCK-EL-05 매핑 정본 Part2 §6.9 변경 0 | ✅ §4 |
| V-8 | LOCK-EL-06 NEVER_AUTO 강제 (자동 폴백 금지) | ✅ §3 |
| V-9 | LOCK-EL-07 권고 레벨 매핑 | ✅ §3 |
| V-10 | 라벨 카디널리티 정책 (W-2 RESOLVED 정합) | ✅ §2 |
| V-11 | 6-5/6-9 cross-ref read-only (source 0 touch) | ✅ §5 |
| V-12 | D-P4-2-1 reconcile (EXP_* vs SDAR FC 명명) | ✅ §4 |
| V-13 | DH 0건 보존 (AUTHORITY §4 미존재) | ✅ |
| V-14 | Status DRAFT → APPROVED (Phase 4 production promotion) | ✅ 헤더 |

---

## §7. 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| v3.0.0 | 2026-06-03 | **Phase 4 RECOVERY Stage A+B P4-2 — loki_integration_v3.md NEW production 정본 승급**. V2 Loki LogQL 6 패턴 base → V3 통합 완성: Grafana 7 panel (§2) + Alertmanager 룰 7건 (§3) + V3 FC 4건 EXP_* 알림 연계 (§4) + 라벨 카디널리티 V3 정책 (W-2 RESOLVED 정합) + 6-5/6-9 cross-ref read-only (§5) + LOCK-EL-08 V3 buildout 재정의 0 + D-P4-2-1 reconcile. Status DRAFT → APPROVED. Wave 3 #25 = DAG #29 마지막 derivation ★ 도메인. chain `phase4_6-12_recovery_AB_2026-06-03`. |

---

**[END OF loki_integration_v3.md v3.0.0 — APPROVED ✅ Phase 4 production promotion]**
