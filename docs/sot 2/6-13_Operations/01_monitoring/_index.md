# 01_monitoring — 모니터링 전략

> **도메인**: 6-13_Operations / 01_monitoring
> **Part2 출처**: §6.12.1 (L5978-5986)
> **LOCK**: (해당 없음 — 버전별 도구 선택은 구현 결정)

---

## Part2 원문 (When/Where)

| 버전 | 모니터링 방식 | 주요 메트릭 | 도구 |
|------|------------|-----------|------|
| V0 | JSONL 로그 + 콘솔 출력 | 파이프라인 성공률, 응답 시간, 에러율 | 수동 tail/grep |
| V1 | structlog JSON + SQLite 메트릭 테이블 | 32모듈 상태, Gate 통과율, 비용 추적, 메모리 사용량 | 로컬 대시보드 (React) |
| V2 | Docker 로그 드라이버 + PostgreSQL 메트릭 | COND 모듈 활성화율, SDAR 해결율, API 레이턴시 P95/P99 | Grafana (Docker) |
| V3 | Loki + Grafana + Prometheus | 전 모듈 분산 추적, K8s 리소스, GPU 활용률, Self-evo 성능 | Observability 스택 |

## SOT2 상세 (What/How)

### 핵심 메트릭 계산식

| 메트릭 | 계산식 | 알림 임계값 |
|--------|--------|-----------|
| 파이프라인 성공률 | `(oc.done 이벤트 수) / (oc.request.received 수) × 100` | < 95% → WARN, < 90% → ERROR |
| 평균 응답 시간 (p95) | `percentile(response_times, 0.95)` (단위 ms) | > 3000ms → WARN, > 5000ms → CRITICAL (정본: OPERATIONS §5.2) |
| Gate 통과율 | `(oc.i5.gates.evaluated PASS 수) / (total) × 100` | < 80% → WARN |
| 비용 소진율 | `(당월 누적 비용) / ($200 LOCK) × 100` | 70%/85%/95%/100% (LOCK-OP-07) |

### 구현 시 결정 (§6.12.12 관련)

- 대시보드 레이아웃: V1 React 대시보드 → V2 Grafana 전환 시 패널 매핑
- 메트릭 수집 주기: V1은 이벤트 기반, V2+는 pull/push 혼합

## 하위 파일 (Phase 예정)

| 파일 | 내용 | 상태 |
|------|------|------|
| `metric_definitions.md` | 전체 메트릭 정의 + 계산식 + 임계값 | 예정 |
| `dashboard_spec.md` | V1~V3 대시보드 스펙 | 예정 |
