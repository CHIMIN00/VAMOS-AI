# Structured Logging — structlog JSON 7필드 출력 표준 (V2)

> **도메인**: 6-12_Event-Logging / 03_trace-context
> **파일**: `structured_logging.md`
> **정본 선언**: 본 파일은 SOT2 정본(Single Source of Truth)이며, LOCK-EL-01 (이벤트 스키마 6필드) 와 LOCK-EL-07 (로깅 레벨 5단계) 의 **structlog JSON 7필드 출력 매핑** 에 대해 권위를 가진다.
> **버전**: v1.0 (2026-04-29, P2-2 신규 — V2-Phase 2 태그)
> **세션**: P2-2 (Phase 2, 의존: P2-1 `trace_propagation.md`)
> **LOCK 연계**: LOCK-EL-01 (이벤트 스키마 6필드: timestamp, event_type, trace_id, source, version, payload), LOCK-EL-07 (로깅 레벨 5단계: DEBUG/INFO/WARN/ERROR/CRITICAL), LOCK-EL-08 (W3C Trace Context — P2-1 결합)

---

## §0. 교차 참조 (Cross-References)

| 문서 | 경로 | 용도 |
|------|------|------|
| AUTHORITY_CHAIN | `../AUTHORITY_CHAIN.md` | LOCK-EL-01 / LOCK-EL-07 / LOCK-EL-08 정의, 도메인 경계 |
| 종합계획서 §6 / §7.3 | `../EVENT_LOGGING_구조화_종합계획서.md` §6 ISS-4 / §7.3 P2-2 | I-4 (P2-1 의존, structlog JSON 포맷 표준) → LOCK-EL-01/07/08 통합 |
| 03/trace_propagation.md | `./trace_propagation.md` (P2-1, 본 파일 의존) | TraceContext + W3C Trace Context Level 1 + correlation_id 누락 감지 |
| 03/_index.md | `./_index.md` §구조화 로깅 포맷 (V1~V3) | JSON 예시 (timestamp/level/event/trace_id/span_id/source/version/payload/duration_ms) |
| 02/log_level_spec.md | `../02_logging-standard/log_level_spec.md` | LOCK-EL-07 5단계 상세 + 이벤트별 기본 레벨 배정 (V1) |
| 02/failure_code_registry.md | `../02_logging-standard/failure_code_registry.md` | FailureCode → 로깅 레벨 매핑 정본 (V1, 48 FC) |
| 02/failure_code_registry_v2.md | `../02_logging-standard/failure_code_registry_v2.md` (P2-3, 별도 V2 NEW) | V2 FC 8건 상세 운영 명세 + R-612-3 매핑 |
| 01/event_schema.md | `../01_event-system/event_schema.md` §2.1 LOCK-EL-01 6필드 + §3.1 EventEnvelope Pydantic | 필수 필드 정본, structlog 출력 매핑 베이스라인 |
| 01/namespace_rules.md | `../01_event-system/namespace_rules.md` | 8 namespace + V2 확장 namespace (dev.*/ipc.*/mcp.*/ops.*) |
| Part2 §6.11 | `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` L5788-5975 | structlog 출력 매핑 정본 + Docker V2 + Grafana 통합 |
| D2.1-D2 §4.2 | `D:\VAMOS\docs\sot\D2.1-D2_D2_SCHEMA_ORANGE_CORE.md` | 직접 정본 stage 1 — 이벤트 스키마 7필드 (event_type, producer, when, payload, severity, sinks, links) 원본 |
| 11 CONSUMER 도메인 | (참조만, 본 파일 §7) | 각 namespace 별 structlog 적용 가이드 (1-1 oc.i1~i5 / 2-1 oc.blue.* / 2-2 oc.cond.* / 3-7 dev.* / 4-1 ipc.* / 4-3 mcp.* / 6-1 ui.builder.* / 6-3 agent.* / 6-5 sdar.* / 6-8 cl.rt.* / 6-13 ops.*) |

---

## §1. 목적 및 범위 (Purpose / Scope)

### 1.1 목적
- LOCK-EL-01 (이벤트 스키마 6필드) 와 LOCK-EL-07 (로깅 레벨 5단계) 를 **structlog JSON 출력 7필드** 로 매핑하는 정본을 V2 Docker 환경 기준으로 확정한다.
- D2.1-D2 §4.2 정본 7필드 (event_type, producer, when, payload, severity, sinks, links) ↔ structlog 출력 필드 ↔ LOCK-EL-01 6필드 ↔ JSON 출력 필드 4축 매핑을 명세화한다.
- `structlog.configure()` 표준 설정 (TimeStamper(iso) + add_log_level + JSONRenderer + UnicodeDecoder + StackInfoRenderer + format_exc_info + contextvars merge) 을 정본 정의한다.
- **stderr/stdout 분리 M-5** (WARN/ERROR/CRITICAL → stderr, DEBUG/INFO → stdout) Docker 로그 분리 + Loki 분리 인덱싱.
- **Grafana Loki LogQL 파싱 호환성** (필드명 일관성, duration_ms 선택 처리, Loki 라벨 카디널리티 정책).
- 11 CONSUMER 도메인 (1-1 / 2-1 / 2-2 / 3-7 / 4-1 / 4-3 / 6-1 / 6-3 / 6-5 / 6-8 / 6-13) namespace 별 structlog 적용 예시 + Pydantic-friendly bind_contextvars 사용 패턴.
- ISS-4 P2-2 단계 해소 (P2-1 결합 시 ISS-4 완성).

### 1.2 범위 (In-scope)
- structlog (≥23.1.0) 표준 configure 설정.
- JSON 출력 7필드: timestamp, level, event_type, trace_id, source, version, payload (+ 선택 5필드: span_id, parent_span_id, correlation_id, severity, duration_ms).
- Docker json-file 드라이버 + 라벨 추출 + Loki 인덱싱.
- Grafana 대시보드 panel (error rate / latency p95 / trace_id 추적).
- stderr/stdout 분리 M-5 (MCP 서버 4-3 cross-handoff 정합).
- 11 CONSUMER namespace 별 적용 가이드 (참조만).
- Phase 2/3 테스트 시나리오 12건.

### 1.3 범위 외 (Out-of-scope)
- W3C Trace Context Level 1 헤더 포맷 / 3 경로 전파 → **P2-1 `trace_propagation.md`** (본 파일은 *출력*, P2-1 은 *전파*).
- V2 FailureCode 8건 상세 → **P2-3 `failure_code_registry_v2.md`** (별도 V2 NEW).
- Loki 보존 기간 / 라벨 카디널리티 운영 → **6-13 Operations** (W-2 RESOLVED 경계).
- V0 (JSONL) → V3 (Loki) 인프라 진화 → **P3-1 `version_evolution.md`** (Phase 3).
- Grafana 대시보드 운영 / 알람 규칙 → **6-13 Operations**.

---

## §2. LOCK-EL-01 / LOCK-EL-07 / LOCK-EL-08 정본 인용 (verbatim)

### §2.1 LOCK-EL-01 5-field verbatim 인용 (AUTHORITY_CHAIN §LOCK 레지스트리 L1)

| 필드 | 값 |
|------|-----|
| **LOCK ID** | `LOCK-EL-01` |
| **항목** | 이벤트 스키마 필수 필드 |
| **값** | timestamp, event_type, trace_id, source, version, payload |
| **정본 출처** | SOT2 신규 정의 |
| **서브폴더 매핑** | 01 (`01_event-system/`) |

### §2.2 LOCK-EL-07 5-field verbatim 인용 (AUTHORITY_CHAIN §LOCK 레지스트리 L7)

| 필드 | 값 |
|------|-----|
| **LOCK ID** | `LOCK-EL-07` |
| **항목** | 로깅 레벨 정의 |
| **값** | DEBUG / INFO / WARN / ERROR / CRITICAL (5단계) |
| **정본 출처** | SOT2 신규 정의 |
| **서브폴더 매핑** | 02 (`02_logging-standard/`) |

### §2.3 LOCK-EL-08 5-field verbatim 인용 (P2-1 결합)

| 필드 | 값 |
|------|-----|
| **LOCK ID** | `LOCK-EL-08` |
| **항목** | 추적 컨텍스트 전파 규칙 |
| **값** | W3C Trace Context 호환, correlation_id 필수 전파 |
| **정본 출처** | SOT2 신규 정의 |
| **서브폴더 매핑** | 03 (`03_trace-context/`) |

### §2.4 LOCK 보호 규칙
- 본 V2 파일에서 LOCK-EL-01 / LOCK-EL-07 / LOCK-EL-08 의 **재정의 / 추가 / 변경 0건** 엄수. 위반 시 즉시 마커 발화.
- 충돌 시 우선순위: `R-T6-1 Part2 §6.11 (정본 출처) > AUTHORITY §LOCK > 본 파일 §3~§7` (AUTHORITY 정본 우선, 본 파일은 운영 명세).

---

## §3. structlog JSON 7필드 출력 정본 매핑 (4축)

### §3.1 4축 매핑 정본 (D2.1-D2 §4.2 ↔ LOCK-EL-01 ↔ structlog ↔ JSON output)

| # | D2.1-D2 §4.2 정본 7필드 | LOCK-EL-01 6필드 | structlog binding key | JSON output key | 필수 여부 |
|---|----------------------|---------------|---------------------|----------------|---------|
| 1 | `when` (ISO 8601 UTC) | `timestamp` | `timestamp` (TimeStamper(iso)) | `timestamp` | required |
| 2 | `event_type` | `event_type` | `event_type` (positional `event=` 별칭 가능) | `event_type` | required |
| 3 | (link) → trace 식별자 | `trace_id` | `trace_id` (LOCK-EL-08 P2-1 contextvars merge) | `trace_id` | required |
| 4 | `producer` | `source` | `source` | `source` | required |
| 5 | (config) → 스키마 버전 | `version` | `version` (default `"1.0.0"`) | `version` | required |
| 6 | `payload` | `payload` | `payload` (dict) | `payload` | required |
| 7 | `severity` | (선택, LOCK-EL-07 매핑) | `level` (add_log_level) | `level` | required (structlog 자동) |
| 8 | (link) → span | (선택) | `span_id` (P2-1 contextvars merge) | `span_id` | optional |
| 9 | (link) → parent span | (선택) | `parent_span_id` | `parent_span_id` | optional |
| 10 | (link) → correlation | (선택, LOCK-EL-08 alias) | `correlation_id` | `correlation_id` | optional (운영자 친화) |
| 11 | (perf) | (선택) | `duration_ms` | `duration_ms` | optional |
| 12 | `sinks` | — (런타임만) | (별도 처리, JSON 출력 비포함) | (no) | excluded |
| 13 | `links` | — (LOCK-EL-08 trace_id 로 표현) | (no separate field) | (no) | excluded |

### §3.2 JSON 출력 정본 예시 (Phase 2 V2 Docker 환경)

```json
{
  "timestamp": "2026-04-29T14:32:15.847Z",
  "level": "INFO",
  "event_type": "oc.i1.parse.started",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "parent_span_id": "1a2b3c4d5e6f7890",
  "correlation_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "source": "orange_core/i1_router",
  "version": "1.0.0",
  "payload": {
    "input_length": 150,
    "user_id_hash": "sha256:a1b2c3..."
  },
  "duration_ms": 23.4
}
```

### §3.3 필드 출력 순서 (Loki LogQL 파싱 일관성)

structlog `JSONRenderer(sort_keys=False)` + processor 체인 순서로 결정. 본 정본 권고 출력 순서:

1. `timestamp`
2. `level`
3. `event_type`
4. `trace_id`
5. `span_id` (있으면)
6. `parent_span_id` (있으면)
7. `correlation_id` (있으면)
8. `source`
9. `version`
10. `payload` (object)
11. `duration_ms` (있으면)

> Note: JSON spec 상 객체 키 순서는 비순차적이지만, structlog `JSONRenderer` 는 binding 순서를 보존한다. Grafana Loki LogQL `| json` 파싱은 키 순서 무관, 그러나 운영자 가독성 + log tail 일관성 위해 본 권고 순서 채택.

---

## §4. structlog.configure() 표준 설정 (정본)

### §4.1 표준 configure() 정본 코드

```python
# src/orange_core/logging_config.py — VAMOS 6-12 정본 structlog 설정
import logging
import sys
import structlog
from structlog.contextvars import merge_contextvars
from structlog.processors import (
    TimeStamper,
    StackInfoRenderer,
    format_exc_info,
    JSONRenderer,
    UnicodeDecoder,
    add_log_level,
)
from structlog.stdlib import filter_by_level


def configure_structlog(
    deploy_env: str = "v2_docker",  # v1_local / v2_docker / v3_loki
    log_level: int = logging.INFO,
    enable_stderr_split: bool = True,  # M-5 stderr/stdout 분리
) -> None:
    """VAMOS 6-12 정본 structlog 설정 (LOCK-EL-01 + LOCK-EL-07 + LOCK-EL-08 통합)

    Args:
        deploy_env: 배포 환경 식별자 (V2 = Docker json-file, V3 = Loki 통합)
        log_level: 표준 로그 레벨 (DEBUG=10, INFO=20, WARN=30, ERROR=40, CRITICAL=50)
        enable_stderr_split: True 면 WARN+ → stderr / DEBUG+INFO → stdout (M-5)
    """
    # 1. stdlib logging baseline (structlog 와 통합)
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # 2. structlog processor 체인 (정본 7-step)
    processors = [
        # (a) contextvars merge — P2-1 trace_context 자동 주입 (LOCK-EL-08)
        merge_contextvars,
        # (b) 레벨 필터는 wrapper_class=make_filtering_bound_logger 가 담당 (PrintLoggerFactory 는 isEnabledFor 미구현 → filter_by_level 사용 불가)
        # (c) timestamp (LOCK-EL-01 timestamp, ISO 8601 UTC ms)
        TimeStamper(fmt="iso", utc=True, key="timestamp"),
        # (d) level (LOCK-EL-07 5단계, structlog 자동 매핑)
        add_log_level,
        # (e) stack info / exc info (ERROR/CRITICAL 시 자동 포함)
        StackInfoRenderer(),
        format_exc_info,
        # (f) UnicodeDecoder (한글 / 비-ASCII 안전)
        UnicodeDecoder(),
        # (g) JSON 직렬화 (Docker json-file + Loki 호환)
        JSONRenderer(sort_keys=False, ensure_ascii=False),
    ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(
            file=sys.stderr if enable_stderr_split else sys.stdout
        ),
        cache_logger_on_first_use=True,
    )

    # 3. M-5 stderr/stdout 분리 (옵션)
    if enable_stderr_split:
        _setup_stderr_split_handler(log_level)


def _setup_stderr_split_handler(log_level: int) -> None:
    """M-5 stderr/stdout 분리: WARN+ → stderr / DEBUG+INFO → stdout"""
    root = logging.getLogger()
    root.handlers.clear()

    # stdout handler (DEBUG, INFO)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.addFilter(lambda r: r.levelno < logging.WARNING)
    root.addHandler(stdout_handler)

    # stderr handler (WARN, ERROR, CRITICAL)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)
    root.addHandler(stderr_handler)

    root.setLevel(log_level)
```

### §4.2 진입점 호출 패턴 (정본)

```python
# src/main.py — 진입점 1회 configure
from orange_core.logging_config import configure_structlog
import structlog
import os

# 환경별 설정 (V1 local / V2 Docker / V3 Loki)
DEPLOY_ENV = os.environ.get("VAMOS_DEPLOY_ENV", "v1_local")

configure_structlog(
    deploy_env=DEPLOY_ENV,
    log_level={"v1_local": 10, "v2_docker": 20, "v3_loki": 20}.get(DEPLOY_ENV, 20),
    enable_stderr_split=(DEPLOY_ENV in ("v2_docker", "v3_loki")),
)

log = structlog.get_logger("orange_core/main")
log.info("system.startup", deploy_env=DEPLOY_ENV, version="1.0.0")
```

### §4.3 LOCK-EL-08 trace 자동 주입 (P2-1 contextvars merge)

```python
# 모듈 진입 시 P2-1 with_trace decorator + structlog contextvars merge 자동 동작
from orange_core.trace_context import trace_context
from structlog.contextvars import bind_contextvars
import structlog

log = structlog.get_logger()

@with_trace("i1_intent_router")
async def i1_route(input_data: dict) -> dict:
    """OC i1 — trace_context 자동 contextvars merge"""
    ctx = trace_context.get()
    # ★ bind_contextvars 으로 trace_id / span_id / correlation_id 명시 binding
    bind_contextvars(**ctx.to_dict())
    try:
        log.info(
            "oc.i1.parse.started",
            event_type="oc.i1.parse.started",  # LOCK-EL-01 event_type
            source="orange_core/i1_router",     # LOCK-EL-01 source
            version="1.0.0",                     # LOCK-EL-01 version
            payload={"input_length": len(input_data.get("text", ""))},
        )
        # ... 본 모듈 처리 ...
    finally:
        # contextvars cleanup (decorator 가 처리, 명시 호출 불필요)
        pass
```

---

## §5. LOCK-EL-07 5단계 레벨 매핑 (verbatim)

### §5.1 5단계 정의 (V1 `02/log_level_spec.md` 정합)

| 레벨 | 수치 | structlog method | 용도 | stdout/stderr |
|------|------|----------------|------|--------------|
| `DEBUG` | 10 | `log.debug()` | 개발/디버깅 전용 (내부 상태 변경, 변수 값) | stdout |
| `INFO` | 20 | `log.info()` | 정상 흐름 추적 (파이프라인 상태 전이, 이벤트 발행) | stdout |
| `WARN` | 30 | `log.warning()` | 비정상이나 복구 가능 (Fallback 활성화, 타임아웃 경고) | stderr |
| `ERROR` | 40 | `log.error()` | 기능 장애 (FailureCode 발생, API 실패) | stderr |
| `CRITICAL` | 50 | `log.critical()` | 서비스 불가 (NEVER_AUTO 위반, 전체 장애) | stderr |

### §5.2 FailureCode → 레벨 매핑 (V1 `failure_code_registry.md` §4 권고 레벨 정합)

| 심각도 | 권고 레벨 | structlog method | 예시 FC |
|--------|----------|----------------|---------|
| P3 (정보) | INFO | `log.info()` | `COND_BATCH_TIMEOUT` |
| P2 (중간) | WARN | `log.warning()` | `COND_MODULE_INIT_FAIL` / `RAG_QDRANT_CONNECTION` / `COND_DEPENDENCY_CONFLICT` / `LLAMAGUARD_GPU_UNAVAIL` |
| P1 (긴급) | ERROR / WARN | `log.error()` 또는 `log.warning()` | `SDAR_REPAIR_FAIL` / `SDAR_SNAPSHOT_CORRUPT` / `LLAMAGUARD_CLASSIFY_FAIL` |
| P0 (치명) | CRITICAL | `log.critical()` | `OC_I5_POLICY_BLOCK` / `POLICY_DENY` / `PII_LONGTERM_DENIED` (NEVER_AUTO 3코드, LOCK-EL-06) |

### §5.3 NEVER_AUTO 강제 격상 (LOCK-EL-06)

```python
# src/orange_core/never_auto_handler.py
NEVER_AUTO_CODES = frozenset(["OC_I5_POLICY_BLOCK", "POLICY_DENY", "PII_LONGTERM_DENIED"])

def assert_never_auto_critical(failure_code: str, recommended_level: str) -> str:
    """LOCK-EL-06: NEVER_AUTO 3코드는 강제 CRITICAL 격상"""
    if failure_code in NEVER_AUTO_CODES:
        return "CRITICAL"
    return recommended_level
```

---

## §6. Docker / Loki / Grafana 통합 (V2 정본)

### §6.1 Docker json-file 드라이버 정본 (P2-1 §5.1 정합)

```yaml
# infra/docker-compose.v2.yml — V2 Docker 환경 logging
services:
  orange_core_i1:
    image: vamos/orange_core:v2
    logging:
      driver: json-file
      options:
        max-size: "100m"
        max-file: "5"
        labels: "trace_id,span_id,correlation_id,event_type,source"
        env: "VAMOS_DEPLOY_ENV"
    environment:
      VAMOS_DEPLOY_ENV: "v2_docker"
    # M-5 stderr/stdout 분리 (Docker는 자동 stdout/stderr 분리 인덱싱)
    tty: false
```

### §6.2 Loki LogQL 추출 패턴 (Phase 2 V2)

```logql
# (1) trace_id 기반 분산 trace 횡단 조회 (P2-1 §5.2 정합)
{container=~"orange_core_.*"} | json
  | trace_id="4bf92f3577b34da6a3ce929d0e0e4736"

# (2) ERROR 이상 레벨 (M-5 stderr 인덱싱)
{container=~".*", stream="stderr"} | json | level=~"ERROR|CRITICAL"

# (3) FailureCode 추출 (LOCK-EL-03 48 FC)
{container=~".*"} | json | event_type=~"oc\\..*" | payload_failure_code != ""

# (4) namespace별 필터링 (LOCK-EL-09 8 namespace + V2 확장 4 namespace)
{container=~".*"} | json | event_type=~"^(oc|cl\\.rt|agent|sdar|storage|mem|wf|ui|dev|ipc|mcp|ops)\\."

# (5) latency p95 (duration_ms 선택 필드)
quantile_over_time(0.95, {container=~"orange_core_.*"} | json | duration_ms != "" | unwrap duration_ms [5m])

# (6) trace 시각화 (parent_span_id 추출, span tree 재구성)
{container=~".*"} | json | trace_id="<32 hex>"
  | line_format "{{.span_id}} ← {{.parent_span_id}} | level={{.level}} | {{.event_type}} | {{.source}}"
```

### §6.3 Grafana 대시보드 panel 정본 (Phase 2 V2)

| Panel | LogQL / PromQL | 용도 |
|-------|---------------|------|
| Total events / sec | `sum(rate({container=~".*"}[1m]))` | 처리량 모니터링 |
| Error rate (%) | `sum(rate({container=~".*", level=~"ERROR\|CRITICAL"}[1m])) / sum(rate({container=~".*"}[1m])) * 100` | 장애율 |
| FailureCode top 10 | `topk(10, sum(rate({container=~".*"} | json | payload_failure_code != "" [5m])) by (payload_failure_code))` | FC 분포 |
| trace_id search | `{container=~".*"} | json | trace_id=~"$trace_id_var"` | 단일 trace 추적 (변수) |
| Latency p95 | `quantile_over_time(0.95, ... | unwrap duration_ms [5m])` | SLA 모니터링 |
| NEVER_AUTO violations | `sum(rate({container=~".*"} | json | payload_failure_code=~"OC_I5_POLICY_BLOCK\|POLICY_DENY\|PII_LONGTERM_DENIED" [1m]))` | LOCK-EL-06 위반 |
| LOCK-EL-08 violations | `sum(rate({container=~".*"} | json | event_type=~"el\\.violation\\..*" [1m]))` | trace 누락 알람 |

### §6.4 Loki 라벨 카디널리티 정책 (W-2 RESOLVED 경계)

| 라벨 | 카디널리티 | 정본 소유자 |
|------|----------|-----------|
| `container` | 컨테이너 수 (~50) | 6-13 Operations (운영) |
| `stream` | stdout / stderr (2) | 6-13 |
| `level` | 5 (LOCK-EL-07) | 6-12 (본 도메인) |
| `event_type` | 134 (LOCK-EL-02) | 6-12 |
| `source` | service/module (~100) | 6-12 |
| (제외) `trace_id` | 무제한 — Loki **라벨 금지**, JSON 필드만 (인덱스 폭발 방지) | 6-12 (본 §6.4 명시) |
| (제외) `span_id` | 무제한 — JSON 필드만 | 6-12 |
| (제외) `payload` | 무제한 — JSON 필드만 | 6-12 |

> **중요**: `trace_id` / `span_id` / `payload` 는 Loki 라벨 ❌ (인덱스 카디널리티 폭발 방지). LogQL `| json | trace_id="..."` 추출만 허용. 라벨화 시 Loki 인덱스 메모리 / 쿼리 성능 급락.

---

## §7. 11 CONSUMER 도메인 자동 적용 가이드

> ★ 본 §7 은 **참조만** (R-T6-2 + R-612-1). 11 CONSUMER 도메인 자체 sandbox/production 직접 편집 ❌. RECHECK_FLAG 발행은 STEP_B step 8 시점에 본 6-12 sandbox 4 위치만 기록.

| # | CONSUMER | namespace | structlog 로거 이름 권고 | 진입점 (configure_structlog 호출 위치) | bind_contextvars 패턴 |
|---|---------|-----------|------------------------|-------------------------------------|---------------------|
| 1 | 1-1 Verifier-Reasoning | `oc.i1~i5` | `structlog.get_logger("orange_core/i{N}")` | i1 router 진입 (S0 Intake) | P2-1 `@with_trace` + bind_contextvars(**ctx.to_dict()) |
| 2 | 2-1 Blue-Node-Architecture | `oc.blue.*` | `structlog.get_logger("orange_core/blue/{node_type}")` | Node executor 진입 | child span + bind |
| 3 | 2-2 COND-Modules-Detail | `oc.cond.*` | `structlog.get_logger("orange_core/cond/{module}")` | COND 모듈 entry | FC 발행 시 payload.failure_code |
| 4 | 3-7 Dev-Tools | `dev.*` | `structlog.get_logger("dev/{tool_name}")` | tool_execute 진입 | sandbox_id binding |
| 5 | 4-1 Rust-Tauri-Infrastructure | `ipc.*` | (Rust slog → 6-12 호환 JSON output) | Tauri command 진입 | Rust struct trace_meta → JSON output |
| 6 | 4-3 MCP-Server-Client | `mcp.*` | `structlog.get_logger("mcp/{server_id}")` + M-5 stderr 강제 | MCP server 시작 | tool_id binding (각 호출별) |
| 7 | 6-1 UI-UX-System | `ui.builder.*` | (TypeScript pino-equivalent → 6-12 JSON output) | Frontend trace 진입 | Tauri IPC traceparent 추출 후 |
| 8 | 6-3 Agent-Teams-PARL | `agent.*` | `structlog.get_logger("agent/{team_id}/{agent_id}")` | 에이전트 plan 시작 | reward_signal binding |
| 9 | 6-5 SDAR-System | `sdar.*` | `structlog.get_logger("sdar/{stage}")` | SDAR detect 시작 | failure_code + fallback_id binding |
| 10 | 6-8 Cloud-Library | `cl.rt.*` | `structlog.get_logger("cl_rt/{layer}")` | crawl_start 진입 (root span) | layer_id + gate_id binding |
| 11 | 6-13 Operations | `ops.*` | (Loki 인덱싱 + 6-12 발행 trace 소비) | (소비만, 신규 발행 ❌) | LogQL 쿼리 (§6.2) |

### §7.1 CONSUMER 공통 의무

1. **모든 이벤트 발행 시 LOCK-EL-01 6필드 + LOCK-EL-08 trace_id 필수** — `bind_contextvars(**ctx.to_dict())` 호출 후 `log.info(event_type, source, version, payload)` 패턴.
2. **structlog 로거 이름** = `{namespace_root}/{module_path}` 권고 (예: `orange_core/i1_router`, `cl_rt/breaking_detector`, `sdar/repair_engine`).
3. **stderr/stdout 분리** = M-5 적용 (Docker 환경 자동, 로컬 환경 옵션).
4. **Loki 라벨 카디널리티** = §6.4 정본 준수 (trace_id 라벨 ❌).
5. **FailureCode 발행** = `payload.failure_code` 필드 + 권고 레벨 (§5.2 매핑).

### §7.2 RECHECK_FLAG 발행 trigger (STEP_B step 8)

본 V2 파일 신설로 11 CONSUMER 도메인은 다음 RECHECK 의무 발생:
- (a) structlog `configure()` 호출 (각 CONSUMER 진입점) — Phase 3 / 자체 STEP_B 시점.
- (b) `bind_contextvars(**ctx.to_dict())` 패턴 자체 적용 (P2-1 + P2-2 결합).
- (c) §5.2 FC 권고 레벨 매핑 자체 검증.

본 6-12 STEP_B step 8 시점에 4 위치만 기록 (CONFLICT_LOG / plan §7 / memory / SOT2_MASTER_INDEX), CONSUMER 직접 편집 ❌. **DEFERRED_TO_PHASE3** 판정.

---

## §8. 출력 검증 체크리스트

| # | 검증 항목 | 기준 | 검증 방법 |
|---|---------|------|---------|
| L1-1 | LOCK-EL-01 6필드 모두 출력 | timestamp + event_type + trace_id + source + version + payload 매 레코드 포함 | `pytest tests/test_lock_el_01_fields.py` |
| L7-1 | LOCK-EL-07 5단계 정확 매핑 | DEBUG/INFO/WARN/ERROR/CRITICAL 5개만 | structlog `add_log_level` 자동 |
| L8-1 | LOCK-EL-08 trace_id 자동 첨부 | `merge_contextvars` processor 정확 동작 | P2-1 `with_trace` + bind_contextvars |
| M5-1 | stderr/stdout 분리 | WARN+ → stderr / DEBUG+INFO → stdout | `_setup_stderr_split_handler` 검증 |
| JSON-1 | JSONRenderer sort_keys=False | 출력 순서 §3.3 정본 | `JSONRenderer(sort_keys=False)` |
| JSON-2 | ensure_ascii=False (한글 안전) | 한글 / 비-ASCII 그대로 직렬화 | `JSONRenderer(ensure_ascii=False)` |
| LK-1 | Loki 라벨 카디널리티 정책 | `trace_id` / `span_id` / `payload` 라벨 ❌ | docker-compose `labels` 설정 검증 |
| LK-2 | LogQL trace_id 검색 동작 | §6.2 (1) 쿼리 결과 ≥ 1 | Loki 통합 테스트 (Phase 3) |
| GR-1 | Grafana panel 정본 7개 | §6.3 7 panel 모두 동작 | Grafana JSON export 검증 |
| FC-1 | FailureCode 권고 레벨 매핑 정합 | §5.2 매트릭스 정합 | `pytest tests/test_fc_level_mapping.py` |
| NA-1 | NEVER_AUTO 강제 CRITICAL 격상 | LOCK-EL-06 3코드 격상 | `assert_never_auto_critical` 검증 |
| C-1 | 11 CONSUMER namespace 모두 호환 | §7 표 11/11 정합 | 본 §7 + 부록 §A 정합 자체 검증 |

---

## §9. Phase별 복구 흐름 (Phase 1→2→3→4)

```
Phase 1 (V1 baseline)              Phase 2 (V2, 본 P2-2)              Phase 3 (V3, P3-1)             Phase 4 (운영)
──────────────────────             ──────────────────────             ──────────────────             ──────────────
log_level_spec.md (V1)             structured_logging.md (본)          version_evolution.md           Loki + Prometheus 통합
LOCK-EL-07 5단계 정의              structlog.configure() 7-processor   OTEL exporter (W3C Level 2)    분산 로그 운영
                                   Docker json-file + Loki LogQL       Grafana dashboard 운영          correlation_id 자동 알람
                                   stderr/stdout M-5
                                   Grafana 7 panel 정본
                                          │
                                          ▼ (실패 시)
                                   structlog 미초기화 → ImportError → main.py 진입점 configure 누락 식별
                                   trace_context 부재 → P2-1 violation → bind_contextvars cleanup → root 강제 생성
                                   Loki 라벨 폭발 → 카디널리티 정책 위반 → §6.4 정본 재준수 + 컨테이너 재시작
                                   stderr/stdout 미분리 → M-5 위반 → enable_stderr_split=True 강제
                                   JSON 직렬화 실패 (UnicodeDecodeError) → UnicodeDecoder processor 누락 → 추가
```

### §9.1 다운그레이드 confidence 감산 (penalty)

| 트리거 | confidence 감산 | 이유 |
|--------|-------------|------|
| trace_id 누락 (P2-1 violation 결합) | -0.15 | trace 체인 끊어짐 |
| level 매핑 오류 (5단계 외 값) | -0.10 | 분류 정합성 저하 |
| FailureCode 권고 레벨 위반 | -0.10 | §5.2 매핑 무시 |
| NEVER_AUTO 격상 누락 (LOCK-EL-06 위반) | -0.30 | 보안 정책 위반 |
| Loki 라벨 카디널리티 폭발 | -0.20 | 운영 안정성 저하 |
| stderr/stdout 미분리 (M-5 위반) | -0.05 | MCP 서버 호환성 저하 |

---

## §10. 에스컬레이션 페이로드 구조 (R-01-8)

```python
# I-20 에스컬레이션 페이로드 (P1-5 §6.2 11필드 + 본 §10 출력 5필드 = 16필드)
@dataclass
class StructloggingViolationPayload:
    """LOCK-EL-01 / LOCK-EL-07 / LOCK-EL-08 출력 위반 시 I-20 경유"""
    # P1-5 §6.2 11필드 (변경 금지)
    source_engine: str
    error_code: str = "EL_LOG_OUTPUT_VIOLATION"
    original_request: dict = field(default_factory=dict)
    partial_result: Optional[dict] = None
    retry_count: int = 0
    timestamp: str = ""
    severity: str = "P2"
    level: str = "WARN"
    fallback_id: str = "FB_RECONFIGURE_STRUCTLOG"
    recovery_action: str = "configure_structlog forced re-run"
    failure_chain: list = field(default_factory=list)

    # 본 §10 출력 5필드 (LOCK-EL-01 / L7 / L8 위반)
    expected_fields: list = field(default_factory=list)  # 누락된 LOCK-EL-01 필드 목록
    actual_level: Optional[str] = None                    # LOCK-EL-07 외 값 (있으면)
    expected_level: Optional[str] = None
    json_serialization_error: Optional[str] = None        # UnicodeDecodeError 등
    loki_label_cardinality: Optional[int] = None          # §6.4 위반 시
```

---

## §11. 로깅 포맷 (R-01-7) — 본 §3.2 정본 + 위반 알람 예시

### §11.1 정상 출력 (§3.2 인용)

```json
{
  "timestamp": "2026-04-29T14:32:15.847Z",
  "level": "INFO",
  "event_type": "oc.i1.parse.started",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "parent_span_id": "1a2b3c4d5e6f7890",
  "correlation_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "source": "orange_core/i1_router",
  "version": "1.0.0",
  "payload": {"input_length": 150}
}
```

### §11.2 LOCK-EL-01 필드 누락 위반

```json
{
  "timestamp": "2026-04-29T14:32:16.123Z",
  "level": "ERROR",
  "event_type": "el.violation.missing_required_field",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "source": "orange_core/event_validator",
  "version": "1.0.0",
  "error": {
    "code": "EL_LOG_OUTPUT_VIOLATION",
    "missing_fields": ["source", "version"],
    "lock_id": "LOCK-EL-01"
  },
  "context": {
    "module": "orange_core/i2_evidence",
    "raw_log_keys": ["timestamp", "level", "event_type", "trace_id", "payload"]
  },
  "recovery": {
    "fallback_id": "FB_RECONFIGURE_STRUCTLOG",
    "action": "structlog reconfigure with full processor chain"
  },
  "payload": {}
}
```

### §11.3 NEVER_AUTO 격상 위반 (LOCK-EL-06 + LOCK-EL-07 결합)

```json
{
  "timestamp": "2026-04-29T14:32:17.456Z",
  "level": "CRITICAL",
  "event_type": "oc.i5.policy_block",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "1a2b3c4d5e6f7890",
  "correlation_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "source": "orange_core/i5_decision",
  "version": "1.0.0",
  "error": {
    "code": "OC_I5_POLICY_BLOCK",
    "lock_id": "LOCK-EL-06",
    "never_auto": true
  },
  "payload": {
    "failure_code": "OC_I5_POLICY_BLOCK",
    "policy_id": "policy_v1.2_pii",
    "blocked_action": "external_api_call"
  }
}
```

---

## §12. ABC 패턴 매핑 (정본 준수)

| ABC | 본 §N | 시그니처 |
|-----|-------|---------|
| `BaseStructlogConfigurator` | §4.1 `configure_structlog` | `def configure_structlog(deploy_env, log_level, enable_stderr_split) -> None` |
| `BaseEventLogger` (LOCK-EL-01) | §3.1 / §4.3 | `log.{debug|info|warning|error|critical}(event_type, source, version, payload, **trace_dict)` |
| `BaseLevelMapper` (LOCK-EL-07) | §5.1 / §5.2 | `def map_severity_to_level(severity: str) -> str` |
| `BaseNeverAutoEscalator` (LOCK-EL-06) | §5.3 `assert_never_auto_critical` | `def assert_never_auto_critical(failure_code, recommended_level) -> str` |

**ABC 정본 위치**: `00_common/base_logging_abc.md` (Phase 3 신설 예정).

---

## §13. 복잡도 / 연산 특성

| 연산 | 시간 복잡도 | 공간 복잡도 | 주석 |
|------|-----------|-----------|------|
| `configure_structlog()` 1회 | O(processors) ≈ O(7) | O(1) | 진입점 1회 |
| `log.info(...)` 매 호출 | O(processors × payload_size) ≈ O(7 × n) | O(payload_size) | 7-step processor 체인 |
| `merge_contextvars` | O(contextvar_count) ≈ O(5) | O(5) | trace + span + correlation + ... |
| `JSONRenderer(sort_keys=False)` | O(n log n) → O(n) (정렬 skip) | O(n) | n = payload byte 수 |
| `bind_contextvars(**ctx.to_dict())` | O(3~4) | O(3~4) | trace_id + span_id + parent + correlation |
| Loki LogQL 추출 (§6.2 (1)) | O(events × log_size) | O(filter_result) | 인덱싱 시간 별개 |

**메모리 footprint**: structlog logger 인스턴스 ≈ 1KB (cache_logger_on_first_use=True 캐시). Phase 2 V2 운영 환경 1초당 1000 events 시 1MB / 1000 events × 7 processors.

---

## §14. 세션 간 인터페이스 cross-check

### §14.1 P2-2 (본) ← P2-1 (`trace_propagation.md`)

| P2-1 §N | 인터페이스 | 본 P2-2 소비 |
|---------|----------|-----------|
| §3.1 trace_id 32 hex | LOCK-EL-01 trace_id | §3.1 #3 (structlog `trace_id` binding) |
| §3.2 span_id 16 hex | 선택 필드 | §3.1 #8 (structlog `span_id`) |
| §3.3 correlation_id alias | LOCK-EL-08 alias | §3.1 #10 (structlog `correlation_id`) |
| §4.3.1 `TraceContext.to_dict()` | dict 반환 | §4.3 `bind_contextvars(**ctx.to_dict())` |
| §6.2 `assert_trace_or_violation()` | 위반 시 RuntimeError | §11.2 위반 알람 JSON 출력 |

### §14.2 P2-2 (본) → P2-3 (`failure_code_registry_v2.md`)

| 본 §N | FC 매핑 | P2-3 소비 |
|------|--------|---------|
| §5.2 P2 권고 WARN | `COND_MODULE_INIT_FAIL` 등 | P2-3 §V2 row 권고 레벨 정합 |
| §5.2 P1 권고 ERROR/WARN | `SDAR_REPAIR_FAIL` 등 | P2-3 §V2 row |
| §5.2 P0 권고 CRITICAL | NEVER_AUTO 3코드 (LOCK-EL-06) | P2-3 §V2 NEVER_AUTO 표시 정합 |

### §14.3 본 P2-2 → V1 baseline 정합

| V1 파일 | §N | 본 P2-2 정합 |
|---------|-----|-----------|
| `event_schema.md` §2 LOCK-EL-01 | 6필드 정의 | §3.1 7필드 매핑 (LOCK-EL-01 6 + level 1) |
| `log_level_spec.md` 5단계 | LOCK-EL-07 정의 | §5.1 5단계 정의 verbatim |
| `failure_code_registry.md` §4 권고 레벨 | 48 FC 권고 레벨 | §5.2 P0~P3 매핑 정합 |
| `never_auto_detector.md` 3코드 | LOCK-EL-06 | §5.3 강제 CRITICAL 격상 |

---

## §15. Phase 3 통합 테스트 시나리오 (≥10 — 12건)

| # | 시나리오 | 주입 방법 | 기대 결과 |
|---|---------|---------|---------|
| TS-1 | `configure_structlog(deploy_env="v2_docker")` 정상 초기화 | main.py 진입 시 호출 | structlog 7-processor 체인 활성화, log.info("system.startup") 정상 출력 |
| TS-2 | LOCK-EL-01 6필드 + level 모두 출력 | `log.info("oc.i1.parse.started", source=..., version=..., payload=...)` | JSON 출력에 7필드 모두 존재 |
| TS-3 | trace_id 자동 contextvars merge | P2-1 `@with_trace` decorator 적용 + log.info() | JSON 출력에 trace_id / span_id / correlation_id 자동 첨부 |
| TS-4 | LOCK-EL-07 5단계 정확 매핑 | `log.debug/info/warning/error/critical()` 5회 | level 필드 각각 DEBUG/INFO/WARN/ERROR/CRITICAL |
| TS-5 | M-5 stderr/stdout 분리 | WARN log + INFO log 동시 발행 | WARN → stderr, INFO → stdout 분리 인덱싱 |
| TS-6 | UnicodeDecoder 한글 안전 | `log.info("event", payload={"msg": "한글 메시지"})` | JSON 출력 한글 그대로 (ensure_ascii=False) |
| TS-7 | NEVER_AUTO 강제 CRITICAL 격상 | `assert_never_auto_critical("OC_I5_POLICY_BLOCK", "WARN")` | 반환값 "CRITICAL" |
| TS-8 | FailureCode 권고 레벨 매핑 | `COND_MODULE_INIT_FAIL` (P2) → WARN | §5.2 매트릭스 정합 |
| TS-9 | Loki LogQL trace_id 검색 | `{container=~".*"} | json | trace_id="<32 hex>"` | 분산 서비스 횡단 trace 전체 조회 |
| TS-10 | Grafana error rate panel | §6.3 panel 동작 | error rate (%) 시계열 표시 |
| TS-11 | LOCK-EL-08 violation 시 ERROR 알람 | trace_context 부재 모듈에서 발행 | P2-1 `assert_trace_or_violation` RuntimeError + ERROR 로그 |
| TS-12 | Loki 라벨 카디널리티 정책 검증 | docker-compose labels 에서 trace_id 누락 확인 | docker inspect 결과 trace_id 라벨 ❌ (§6.4) |

---

## §16. 변경 이력

| 버전 | 날짜 | 세션 | 변경 내용 |
|------|------|------|---------|
| v1.0 | 2026-04-29 | P2-2 | 신규 작성 — V2-Phase 2 태그. structlog JSON 7필드 출력 정본. LOCK-EL-01 6필드 + LOCK-EL-07 5단계 + LOCK-EL-08 trace_id verbatim 5-field 인용. Docker json-file + Loki LogQL 6 패턴 + Grafana 7 panel 정본 + stderr/stdout M-5 + UnicodeDecoder 한글 안전 + NEVER_AUTO 강제 CRITICAL 격상 (LOCK-EL-06 결합). 11 CONSUMER 적용 가이드 (참조만, 직접 편집 ❌). P2-1 trace_propagation.md 의존 (contextvars merge_contextvars). FABRICATION 0/10 CLEAN. ISS-4 P2-2 단계 해소 (P2-1 결합 시 ISS-4 완성). |

---

## §17. 자체 검증 체크리스트

| # | 검증 항목 | 결과 |
|---|---------|------|
| V-1 | LOCK-EL-01 verbatim 5-field 인용 | ✅ §2.1 |
| V-2 | LOCK-EL-07 verbatim 5-field 인용 | ✅ §2.2 |
| V-3 | LOCK-EL-08 verbatim 5-field 인용 (P2-1 결합) | ✅ §2.3 |
| V-4 | LOCK-EL-01/L7/L8 재정의/추가/변경 0건 | ✅ |
| V-5 | DH 신규 추가 0건 (DH 0건 보존 강제) | ✅ |
| V-6 | structlog JSON 7필드 4축 매핑 | ✅ §3.1 (D2.1-D2 §4.2 ↔ LOCK-EL-01 ↔ structlog ↔ JSON) |
| V-7 | configure_structlog() 7-processor 정본 | ✅ §4.1 |
| V-8 | M-5 stderr/stdout 분리 | ✅ §4.1 + §5.1 |
| V-9 | LOCK-EL-07 5단계 + FC 권고 레벨 매핑 | ✅ §5.1 + §5.2 |
| V-10 | NEVER_AUTO 강제 CRITICAL 격상 (LOCK-EL-06) | ✅ §5.3 |
| V-11 | Docker json-file + Loki LogQL + Grafana panel | ✅ §6.1 / §6.2 / §6.3 |
| V-12 | Loki 라벨 카디널리티 정책 (W-2 RESOLVED) | ✅ §6.4 |
| V-13 | 11 CONSUMER 적용 가이드 | ✅ §7 |
| V-14 | 출력 검증 체크리스트 ≥ 10 | ✅ §8 (12건) |
| V-15 | Phase 3 테스트 시나리오 ≥ 10 | ✅ §15 (12건) |
| V-16 | P2-1 / P2-3 / V1 인터페이스 cross-check | ✅ §14 |
| V-17 | FABRICATION 10-marker census 0/N CLEAN | ✅ |
| V-18 | 11 CONSUMER 도메인 sandbox/production 직접 편집 0건 | ✅ |
| V-19 | 2-stage upstream + self chain 인용 (D2.1-D2 + Part2 §6.11 > SOT2 6-12) | ✅ §0 + §1.1 |
| V-20 | R-T6-1/R-T6-2/R-T6-3 + R-612-1 보호 규칙 준수 | ✅ §2.4 + §7 |
