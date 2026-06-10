# C-3 Code Verifier — Monitoring Metrics

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
| LOCK 정본 | `AUTHORITY_CHAIN.md` §4 LOCK-VR-01, VR-05, VR-12, **VR-15** | 임계값 / 판정 / SLA / 샌드박스 |
| Spec | `03_code-verifier/spec.md` | C-3 인터페이스 |
| Security rules | `03_code-verifier/security_rules.md` | OWASP Top 10 매핑 (G1-4) |
| Error handling | `03_code-verifier/error_handling.md` | 에러 코드 15종 |
| ABC 정본 | `00_common/base_verifier_abc.md` | verify() 시그니처 |
| OC 통합 | `06_dependency-graph/orange_core_integration.md` §5.4 | `code_verify_check` + `sandbox_run_id` |
| 교차 도메인 | **6-12 Event-Logging** (READ-only), **6-2 Security-Governance** 연동 | oc.i1~i5, BRAIN_FAILOVER, OWASP |
| PART2 | V1-Phase 3 (L2140~2147) | 구현 가이드 |

### 1.1 상위 SoT 정책

- **UPSTREAM_SOT=null** → 상위 SoT 직접 Read = **SKIP**.

### 1.2 cross-check 결과

- §4.1: LOCK-VR-01/05/12/**15** Read 확인 (VR-15: Docker sandbox, timeout 30s, CPU/RAM 상한은 설정 파일).
- §4.2: `03_code-verifier/_index.md` priority 일관 처리.
- §4.3: C-3 ↔ `code_verify_check` + `sandbox_run_id` refs 매핑 확인.

---

## 2. LOCK 정본 참조

> LOCK (D2.0-02 §7.53-1 — LOCK-VR-01): Self-check 임계값 P0≥70, P1≥75, P2≥80
> LOCK (상세명세 C-1 §4 — LOCK-VR-05): ≥0.8 PASS, 0.5~0.8 REVIEW, <0.5 FAIL
> LOCK (D2.0-02 §2.3-B — LOCK-VR-12): 단일응답 ≤2s, 복합응답 ≤10s, Self-check ≤1s
> LOCK (D2.0-02 §1.3-A — LOCK-VR-15): Docker sandbox, timeout 30s, CPU/RAM 상한은 설정 파일로 관리 (C-3 전용)

---

## 3. 공통 메트릭 5종

### 3.1 M-COM-01 — Latency

- ID: `vre.c3.code.latency_ms` (p50/p95/p99)
- 태그: `engine=C-3`, `mode={static,sandbox,hybrid}`, `language={py,js,go,rust,...}`

> **주의**: C-3는 샌드박스 실행 시 p95가 단일응답 LOCK-VR-12(≤2s) 범위를 구조적으로 초과할 수 있다. **mode=sandbox** 는 복합응답(≤10s) 구간으로 분류한다. Sandbox 자체 timeout은 LOCK-VR-15(30s)와 별도 (코드 실행 상한 vs SLA 응답 시간 구분).

**임계값 (LOCK-VR-12 인용)**:
| 구간 | p95 | WARNING | CRITICAL |
|------|-----|---------|----------|
| 단일응답 (static) | ≤2,000 ms | p95 > 1,600 ms | p95 > 2,000 ms |
| 복합응답 (sandbox) | ≤10,000 ms | p95 > 8,000 ms | p95 > 10,000 ms |
| Self-check | ≤1,000 ms | p95 > 800 ms | p95 > 1,000 ms |
| Sandbox 실행 (LOCK-VR-15) | ≤30,000 ms hard | > 25,000 ms | = 30,000 ms (timeout) |

### 3.2 M-COM-02 — Throughput

- ID: `vre.c3.code.requests_per_sec`
- WARNING: 5분 연속 용량 80%
- CRITICAL: 5분 연속 용량 100% 또는 샌드박스 동시 실행 한도 초과

### 3.3 M-COM-03 — Error Rate

- ID: `vre.c3.code.error_rate`
- 태그: `error_code` (15종)
- WARNING: ≥ 20% (5분)
- CRITICAL: = 100% (10분)

### 3.4 M-COM-04 — Confidence 분포 (LOCK-VR-05)

- ID: `vre.c3.code.confidence_histogram`
- 파생: pass_rate / review_rate / fail_rate
- WARNING: fail_rate > 15% 또는 review_rate > 40%
- CRITICAL: fail_rate > 30%

### 3.5 M-COM-05 — Resource Usage

- ID: `vre.c3.code.cpu_pct` / `vre.c3.code.mem_mb` / `vre.c3.code.gpu_pct` / `vre.c3.code.sandbox_container_count`
- WARNING: 70% (5분 연속) / 샌드박스 컨테이너 ≥ 운영 상한의 80%
- CRITICAL: 90% (2분 연속) / 샌드박스 컨테이너 운영 상한 도달

---

## 4. C-3 고유 메트릭

### 4.1 M-C3-06 — 보안 취약점 탐지율

| 항목 | 값 |
|------|---|
| 메트릭 ID | `vre.c3.code.vuln_detection_rate` |
| 정의 | GT 주입 취약점(OWASP Top 10) 중 탐지 성공 비율 (recall) |
| 태그 | `owasp_category` (A01~A10) |
| WARNING | recall < 85% |
| CRITICAL | recall < 70% |

### 4.2 M-C3-07 — False Positive 비율

| 항목 | 값 |
|------|---|
| 메트릭 ID | `vre.c3.code.false_positive_rate` |
| 정의 | 안전한 코드 샘플 중 FAIL 판정된 비율 |
| WARNING | > 10% |
| CRITICAL | > 20% |

### 4.3 M-C3-08 — Sandbox 활용률 (LOCK-VR-15 연동)

| 항목 | 값 |
|------|---|
| 메트릭 ID | `vre.c3.code.sandbox_utilization_rate` |
| 정의 | 전체 verify 요청 중 sandbox 모드로 실행된 비율 |
| 보조 | `vre.c3.code.sandbox_timeout_rate` (30s hard timeout 도달 비율) |
| WARNING | sandbox_timeout_rate > 5% |
| CRITICAL | sandbox_timeout_rate > 15% 또는 sandbox escape 의심 신호 |

### 4.4 M-C3-09 — chain_length (chain_used 재사용)

> **[CONFLICT_CANDIDATE]**: `code_verify_check` + `sandbox_run_id` refs 명칭 ORANGE CORE 컨펌 대상 (P2-6 보고).

| 항목 | 값 |
|------|---|
| 메트릭 ID | `vre.c3.code.chain_length` |
| 정의 | Decision.verify.chain_used 배열 길이 |
| WARNING | > 7 |
| CRITICAL | > 10 |

---

## 5. 6-12 Event-Logging 연동

### 5.1 oc.i1~i5 매핑 (6-12 정본 READ-only)

| 이벤트 | C-3 연동 |
|--------|----------|
| `oc.i1` | latency 측정 시작 |
| `oc.i2` | verify() 호출, sandbox_run_id 발급 |
| `oc.i3` | OWASP 카테고리별 탐지 결과 적재 |
| `oc.i4` | Self-check latency 종료 |
| `oc.i5` | 전체 latency 집계 + sandbox 컨테이너 해제 |

### 5.2 BRAIN_FAILOVER 연동

| 메트릭 | 설명 |
|--------|------|
| `vre.c3.code.brain_failover_count` | Layer 1 전환 횟수 |
| `vre.c3.code.brain_active` | 활성 Brain (LOCK-VR-07) |

WARNING: ≥3/hr / CRITICAL: Fallback 소진 `OC_I20_BRAIN_EXHAUSTED`.

### 5.3 OC_I20_* 참조 정책

> **INFRA 이관**: `OC_I20_*` 코드 정식 등록은 6-12 Phase 2 INFRA 확정 대상. 본 문서는 참조 방식만 정의.

---

## 6. 로깅 포맷 (R-01-7 중첩 JSON)

```json
{
  "timestamp": "2026-04-18T10:30:00.123Z",
  "trace_id": "tr_abc123",
  "decision_id": "dec_xyz789",
  "engine": "C-3",
  "engine_name": "code-verifier",
  "event": "verify.completed",
  "metrics": {
    "latency_ms": 4500,
    "confidence": 0.85,
    "chain_length": 3,
    "sandbox_run_ms": 3800,
    "sandbox_exit_code": 0,
    "vuln_findings_count": 2,
    "owasp_categories_hit": ["A03", "A07"]
  },
  "error": {
    "code": "SANDBOX_TIMEOUT",
    "severity": "WARNING",
    "recoverable": true
  },
  "context": {
    "mode": "sandbox",
    "language": "python",
    "code_size_bytes": 8192,
    "sandbox_image": "python:3.12-slim"
  },
  "recovery": {
    "strategy": "retry_with_reduced_scope",
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
| 1,1 | Latency Trend (by mode) | M-COM-01 | 10초 |
| 1,2 | Throughput | M-COM-02 | 10초 |
| 1,3 | Error Rate by Code | M-COM-03 | 30초 |
| 2,1 | Confidence Histogram | M-COM-04 | 1분 |
| 2,2 | PASS/REVIEW/FAIL % | 파생 | 1분 |
| 2,3 | Sandbox Containers / Resource | M-COM-05 | 30초 |
| 3,1 | Vuln Detection Rate by OWASP | M-C3-06 | 5분 |
| 3,2 | False Positive Rate | M-C3-07 | 5분 |
| 3,3 | Sandbox Utilization / Timeout | M-C3-08 | 1분 |
| 4,1 | BRAIN_FAILOVER | §5.2 | 실시간 |
| 4,2 | SLA (LOCK-VR-12, VR-15) | 파생 | 1분 |
| 4,3 | QoD vs P2≥80 (LOCK-VR-01) | 파생 | 5분 |

### 7.2 갱신 주기 / 7.3 보존 기간

- 실시간 (≤10초): latency, throughput, sandbox 이벤트
- 단기 (30초~1분): error, confidence, sandbox util, resource
- 중기 (5분): vuln detection, false positive
- 보존: 일반 30일/1년, SLA/보안 위반 90일/3년

---

## 8. Phase 3 테스트 시나리오 (10건+)

| # | 시나리오 | 조건 | 기대 알림 | 근거 |
|---|---------|------|----------|------|
| TS-01 | static p95 임계 | p95=1,700ms | WARNING | LOCK-VR-12 |
| TS-02 | static SLA 위반 | p95=2,100ms | CRITICAL | LOCK-VR-12 |
| TS-03 | sandbox 복합 SLA 위반 | p95=10,500ms | CRITICAL | LOCK-VR-12 |
| TS-04 | Self-check SLA | p95=1,100ms | CRITICAL | LOCK-VR-12 |
| TS-05 | Sandbox timeout 급증 | sandbox_timeout_rate=18% | CRITICAL | LOCK-VR-15 / M-C3-08 |
| TS-06 | Sandbox 컨테이너 한도 도달 | container_count = 운영 상한 | CRITICAL | M-COM-05 |
| TS-07 | OWASP 탐지율 저하 | recall=65% | CRITICAL | M-C3-06 |
| TS-08 | False positive 폭증 | > 22% | CRITICAL | M-C3-07 |
| TS-09 | Error rate 급등 | 25% (5분) | WARNING | LOCK-VR-01 |
| TS-10 | Fail_rate 급증 | 32% | CRITICAL | LOCK-VR-05 |
| TS-11 | BRAIN_FAILOVER 연쇄 | 1시간 4회 | WARNING | §5.2 |
| TS-12 | Fallback 소진 | `OC_I20_BRAIN_EXHAUSTED` | CRITICAL | §5.2 |
| TS-13 | Sandbox escape 신호 | 보안 시그니처 탐지 | CRITICAL | 6-2 연동 |

---

## 9. ABC 시그니처 정합 (LOCK-VR-11)

> LOCK (상세명세 C-1 §3 — LOCK-VR-11): 시그니처 변경 불가.

```python
@metrics.observe(engine="C-3", metric_set="vre.c3.code")
async def verify(self, request: VerifyRequest) -> VerifyResult:
    ...
```

계측은 데코레이터/훅으로만 삽입.

---

## 10. 검증 체크리스트 (§7 P2-7 대조 기준 5건)

- [x] G2-3 기여: `03_code-verifier/monitoring_metrics.md` 완성
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

**End of C-3 Code Verifier monitoring_metrics.md (v1.0)**
