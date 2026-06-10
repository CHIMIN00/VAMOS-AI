# event_schema.md — 이벤트 스키마 필수 필드 정본

> **도메인**: 6-12_Event-Logging / 01_event-system
> **세션**: P1-1
> **작성일**: 2026-04-14
> **정본 선언**: 본 파일은 SOT2 신규 정본(Single Source of Truth)이며, LOCK-EL-01 이 정의한 6개 필수 필드의 타입·필수여부·검증 규칙에 대해 상위 참조 없이 최종 권위를 가진다.
> **LOCK**: LOCK-EL-01 (이벤트 스키마 필수 필드)

---

## §0. 교차 참조 블록

| 참조 ID | 경로 | 관계 |
|---------|------|------|
| AUTHORITY_CHAIN | `D:\VAMOS\docs\sot 2\6-12_Event-Logging\AUTHORITY_CHAIN.md` §LOCK-EL-01 | LOCK 정의 원본 |
| _index (01) | `D:\VAMOS\docs\sot 2\6-12_Event-Logging\01_event-system\_index.md` §이벤트 스키마 필수 필드 | 도메인 컨텍스트 |
| event_type_registry (예정, P1-2) | `./event_type_registry.md` | `event_type` 필드 허용값 집합 (LOCK-EL-02 134항목) |
| pipeline_state_map (예정, P1-3) | `./pipeline_state_map.md` | S0~S8 상태별 `event_type` 매핑 (LOCK-EL-10) |
| namespace_rules (예정, P1-4) | `./namespace_rules.md` | `event_type` 의 네임스페이스 형식 규칙 (LOCK-EL-09) |
| logging_levels (예정, P1-5) | `../02_logging-standard/logging_levels.md` | `payload.level` 권고값 (LOCK-EL-07) |
| Part2 §6.11 | `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` L5788-5975 | 이벤트 네임스페이스·9-State 연동 원문 |
| D2.1-D2 | `D:\VAMOS\docs\sot\D2.1-D2_D2_SCHEMA_ORANGE_CORE.md` | EventTypeRegistry 원본 |

---

## §1. 개요 (Purpose & Scope)

### 1.1 Purpose
- 시스템에서 발행되는 **모든 이벤트**가 반드시 포함해야 하는 공통 스키마(필수 필드 집합, 타입, 제약 조건)을 확정한다.
- 이 스키마는 VAMOS 전 도메인(ORANGE CORE, Cloud Library, SDAR, Agent Teams, UI/UX, Security, Storage 등)에서 발행되는 이벤트에 공통 적용되며, 도메인별 확장 필드는 `payload` 객체 내부에 둔다.

### 1.2 Scope
- **포함**: 공통 필드 정의(6개), 타입·포맷·필수여부, 검증 규칙, JSON 예시, 금지 사용 패턴
- **제외**:
  - EventTypeRegistry 의 134항목 상세(P1-2, `event_type_registry.md`)
  - 9-State 와의 매핑(P1-3, `pipeline_state_map.md`)
  - 네임스페이스 형식 규칙(P1-4, `namespace_rules.md`)
  - 로깅 레벨 정책 및 retention(P1-5, `logging_levels.md`)
  - structlog JSON 포맷 표준(P2-2, Phase 2)

---

## §2. 필수 필드 정본 (LOCK-EL-01)

### 2.1 6개 필수 필드 (LOCK-EL-01)

| # | 필드 | 타입 | 필수 | 포맷 | 설명 |
|---|------|------|------|------|------|
| 1 | `timestamp` | string | **required** | ISO 8601 with `Z` suffix, millisecond precision | 이벤트 발생 시각. 반드시 UTC(`Z`). 예: `2026-04-14T15:00:00.123Z` |
| 2 | `event_type` | string | **required** | `{domain}.{module}.{action}[.{detail}]` — namespace_rules.md 준수 | EventTypeRegistry(LOCK-EL-02, 134항목) 등록 값 중 하나 |
| 3 | `trace_id` | string | **required** | UUID v4 (32 hex + 4 hyphens) 또는 W3C Trace Context `trace-id` 32 hex 문자열 | 요청 단위 추적 ID. 동일 요청에 속한 이벤트 간 동일값 유지 |
| 4 | `source` | string | **required** | `{service}/{module}` 형식 (ASCII, `/`/`_`/`-`/영숫자) | 이벤트 발행 주체. 예: `orange_core/i5_verifier` |
| 5 | `version` | string | **required** | SemVer 2.0.0 (`MAJOR.MINOR.PATCH`) | 본 이벤트 스키마의 버전. 현 정본은 `1.0.0` |
| 6 | `payload` | object | **required** | JSON object (빈 객체 `{}` 허용, `null` 금지) | 이벤트 유형별 상세 데이터. `event_type` 에 따라 구조가 달라짐 |

### 2.2 필드별 상세 규약

#### 2.2.1 `timestamp`
- **타입**: string (ISO 8601)
- **포맷**: `YYYY-MM-DDTHH:MM:SS.sssZ` (밀리초 3자리, UTC `Z` 고정)
- **제약**:
  - 로컬 타임존(`+09:00` 등) 금지 — UTC 로 정규화하여 발행
  - 발행 시점 기준 미래 시각 금지 (발행자 시계 기준 `±1s` 허용)
  - 나노초 이상 정밀도 필요 시 `payload.timestamp_ns` 로 별도 기록 (필수 필드는 ms 고정)
- **정규식**: `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$`

#### 2.2.2 `event_type`
- **타입**: string
- **포맷**: 점(`.`) 구분 네임스페이스. 최소 3 segment, 최대 5 segment
- **제약**:
  - `event_type_registry.md` (LOCK-EL-02) 에 등록된 값만 사용
  - 미등록 값 사용 시 수신 측은 `EL_EVT_UNKNOWN_TYPE` 오류 기록 + drop 또는 quarantine (namespace_rules.md 의 등록 프로세스 따름)
  - 대소문자 구분 — 소문자만 허용 (`^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*){2,4}$`)

#### 2.2.3 `trace_id`
- **타입**: string
- **허용 포맷**:
  - UUID v4: `xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx` (소문자 hex)
  - W3C Trace Context trace-id: 32 lowercase hex, `00000000000000000000000000000000` 금지
- **제약**:
  - 동일 요청 처리 체인 내 모든 이벤트는 동일 `trace_id` 공유
  - 신규 요청 진입 지점(S0 Intake)에서 1회 생성, 이후 전 구간 전파 (P2-1 `context_propagation.md` 참조)

#### 2.2.4 `source`
- **타입**: string
- **포맷**: `{service}/{module}` — 서비스·모듈명 소문자 영숫자 + `_` + `-` 허용
- **제약**:
  - Docker 컨테이너 환경에서는 `{service}` 가 docker service name 과 일치해야 함 (Phase 2 P2-1 규칙과 정합)
  - 예시: `orange_core/i1_router`, `cl_rt/breaking_detector`, `sdar/repair_engine`

#### 2.2.5 `version`
- **타입**: string (SemVer 2.0.0)
- **현 정본 값**: `1.0.0`
- **승급 규칙**:
  - **MAJOR**: 필수 필드 추가/삭제/타입 변경 (breaking)
  - **MINOR**: 선택 필드 추가, 또는 `payload` 내 공통 권고 필드 추가
  - **PATCH**: 설명·검증 규칙 clarification, 비기능 변경
- **제약**: 수신자는 `MAJOR` 가 자기 지원 범위 초과 시 `EL_EVT_VERSION_UNSUPPORTED` 기록 후 drop

#### 2.2.6 `payload`
- **타입**: object (JSON)
- **제약**:
  - `null` 금지 (빈 객체 `{}` 은 허용)
  - `event_type` 에 따라 내부 구조 결정 (향후 per-type schema 는 Phase 2 P2-2 `structlog_format.md` 로 분리)
  - 크기 상한: 직렬화 시 16 KiB (초과 시 `payload.truncated=true` + 별도 `payload_ref` URI 권고 — Phase 2 규칙)
  - PII 직접 포함 금지 — 해시/마스킹 (6-2 Security-Governance 연계)

### 2.3 선택 필드 (선행 정의, non-LOCK)
본 문서는 LOCK-EL-01 의 6개 필수 필드를 정본으로 잠근다. 하기는 **비필수 권고 필드**이며 향후 P2-2 에서 표준화된다.

| 필드 | 타입 | 용도 |
|------|------|------|
| `span_id` | string (16 hex) | W3C span id (trace 내 하위 span) |
| `parent_span_id` | string (16 hex) | 상위 span id |
| `sampled` | boolean | 샘플링 여부 |
| `severity` | string | DEBUG/INFO/WARN/ERROR/CRITICAL (LOCK-EL-07) |

---

## §3. 공통 자료 구조 선정의

### 3.1 Pydantic Model (정본)

```python
# EventEnvelope: 모든 이벤트의 필수 필드 스키마 정본 (LOCK-EL-01)
# 본 모델은 6-12_Event-Logging/01_event-system/event_schema.md §2 와 정확히 일치한다.

from __future__ import annotations
from typing import Any, Dict
from pydantic import BaseModel, Field, field_validator
import re
from datetime import datetime, timezone

ISO8601_UTC_MS = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")
EVENT_TYPE_RE  = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*){2,4}$")
UUID_V4_RE     = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
W3C_TRACE_RE   = re.compile(r"^[0-9a-f]{32}$")
SOURCE_RE      = re.compile(r"^[a-z][a-z0-9_\-]*/[a-z][a-z0-9_\-]*$")
SEMVER_RE      = re.compile(r"^\d+\.\d+\.\d+$")

class EventEnvelope(BaseModel):
    timestamp:  str            = Field(..., description="ISO 8601 UTC ms — e.g. 2026-04-14T15:00:00.123Z")
    event_type: str            = Field(..., description="EventTypeRegistry 등록 값 (LOCK-EL-02)")
    trace_id:   str            = Field(..., description="UUID v4 또는 W3C trace-id 32 hex")
    source:     str            = Field(..., description="{service}/{module}")
    version:    str            = Field(default="1.0.0", description="SemVer 2.0.0")
    payload:    Dict[str, Any] = Field(default_factory=dict, description="이벤트 유형별 상세 데이터")

    @field_validator("timestamp")
    @classmethod
    def _ts(cls, v: str) -> str:
        if not ISO8601_UTC_MS.match(v):
            raise ValueError("EL_EVT_BAD_TIMESTAMP")
        # future-guard: ±1s tolerance
        t = datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        if (t - datetime.now(tz=timezone.utc)).total_seconds() > 1.0:
            raise ValueError("EL_EVT_FUTURE_TIMESTAMP")
        return v

    @field_validator("event_type")
    @classmethod
    def _et(cls, v: str) -> str:
        if not EVENT_TYPE_RE.match(v):
            raise ValueError("EL_EVT_BAD_TYPE_FORMAT")
        return v

    @field_validator("trace_id")
    @classmethod
    def _tid(cls, v: str) -> str:
        if UUID_V4_RE.match(v) or (W3C_TRACE_RE.match(v) and v != "0" * 32):
            return v
        raise ValueError("EL_EVT_BAD_TRACE_ID")

    @field_validator("source")
    @classmethod
    def _src(cls, v: str) -> str:
        if not SOURCE_RE.match(v):
            raise ValueError("EL_EVT_BAD_SOURCE")
        return v

    @field_validator("version")
    @classmethod
    def _ver(cls, v: str) -> str:
        if not SEMVER_RE.match(v):
            raise ValueError("EL_EVT_BAD_VERSION")
        return v
```

### 3.2 JSON Schema (draft-07, 상호운용 용도)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://vamos.local/sot2/6-12/event_schema/1.0.0",
  "title": "EventEnvelope",
  "type": "object",
  "required": ["timestamp", "event_type", "trace_id", "source", "version", "payload"],
  "additionalProperties": true,
  "properties": {
    "timestamp":  {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.\\d{3}Z$"},
    "event_type": {"type": "string", "pattern": "^[a-z][a-z0-9_]*(\\.[a-z][a-z0-9_]*){2,4}$"},
    "trace_id":   {"type": "string", "oneOf": [
      {"pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"},
      {"pattern": "^(?!0{32}$)[0-9a-f]{32}$"}
    ]},
    "source":     {"type": "string", "pattern": "^[a-z][a-z0-9_\\-]*/[a-z][a-z0-9_\\-]*$"},
    "version":    {"type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$"},
    "payload":    {"type": "object"}
  }
}
```

---

## §4. JSON 예시 (정상 케이스)

### 4.1 ORANGE CORE — 게이트 검증 완료

```json
{
  "timestamp": "2026-04-14T15:00:00.123Z",
  "event_type": "oc.i5.gates.evaluated",
  "trace_id": "7b3a4e12-9d55-4a7c-bf10-2e1d3c9a8f04",
  "source": "orange_core/i5_verifier",
  "version": "1.0.0",
  "payload": {
    "request_id": "req-2026-04-14-00042",
    "gates_passed": ["G1", "G2", "G3"],
    "gates_failed": [],
    "confidence": 0.92,
    "severity": "INFO"
  }
}
```

### 4.2 Cloud Library RT-BNP — 속보 감지

```json
{
  "timestamp": "2026-04-14T15:00:01.456Z",
  "event_type": "cl.rt.breaking.detected",
  "trace_id": "8a6b1f23-aa11-4b88-9d02-e7c4b5a9e013",
  "source": "cl_rt/breaking_detector",
  "version": "1.0.0",
  "payload": {
    "headline_hash": "sha256:…",
    "score": 0.87,
    "feeds": 5
  }
}
```

### 4.3 빈 payload 허용 케이스

```json
{
  "timestamp": "2026-04-14T15:00:02.000Z",
  "event_type": "oc.done",
  "trace_id": "1c4d2e56-bb22-4c99-8e01-f5a6b7c8d901",
  "source": "orange_core/s6_deliver",
  "version": "1.0.0",
  "payload": {}
}
```

---

## §5. 검증 규칙 및 예외 처리 정책

### 5.1 검증 실패 시 오류 코드 표

| error_code | 조건 | recoverable | 처리 |
|------------|------|-------------|------|
| `EL_EVT_BAD_TIMESTAMP` | `timestamp` 포맷/UTC 위반 | No | drop + structured log (ERROR) |
| `EL_EVT_FUTURE_TIMESTAMP` | 발행자 시계 기준 `+1s` 초과 미래 | Yes | clock-skew 복구 후 재발행 (발행자 측 NTP 점검 트리거) |
| `EL_EVT_BAD_TYPE_FORMAT` | `event_type` 정규식 위반 | No | drop + quarantine (`dlq/bad_event_type`) |
| `EL_EVT_UNKNOWN_TYPE` | 등록되지 않은 `event_type` | Yes | quarantine → P1-2 namespace_rules.md 등록 절차 트리거 |
| `EL_EVT_BAD_TRACE_ID` | UUID v4 / W3C trace-id 포맷 위반, all-zero trace | No | drop (trace 체인 파괴 방지) |
| `EL_EVT_BAD_SOURCE` | `source` 정규식 위반 | No | drop + 발행 모듈 경고 |
| `EL_EVT_BAD_VERSION` | SemVer 포맷 위반 | No | drop |
| `EL_EVT_VERSION_UNSUPPORTED` | 수신자가 지원하지 않는 MAJOR | No | drop + metric `evt_version_skip_total++` |
| `EL_EVT_PAYLOAD_NULL` | `payload == null` | No | drop + structured log (ERROR) — §2.2.6 `null` 금지 정합, 자동 보정 금지(감사 추적 보존) |
| `EL_EVT_PAYLOAD_TOO_LARGE` | 직렬화 `> 16 KiB` | Yes | truncate + `payload.truncated=true` + `payload_ref` 부여 |

### 5.2 Phase별 복구 전략

```
Phase 1 (단일 프로세스 V1)
  └─ validation 실패
       ├─ BAD_TIMESTAMP / BAD_FORMAT → drop + structured log
       ├─ UNKNOWN_TYPE                → quarantine → namespace 등록 절차
       └─ PAYLOAD_TOO_LARGE           → truncate + payload_ref

Phase 2 (Docker 분산 V2)
  └─ 수신 측 validation 실패
       ├─ 재시도 가능(recoverable=Yes) → retry with backoff (max 3, initial 100ms)
       ├─ 재시도 불가                  → DLQ 전송 + alert (6-13 Operations)
       └─ version MAJOR mismatch      → downgrade path (하단 confidence penalty 표 참조)

Phase 3 (분산 이벤트 버스 V3)
  └─ bus 수신 후 validation 실패
       ├─ same-MAJOR → consumer-side translation (MINOR up-shift)
       ├─ cross-MAJOR → I-20 escalation (정책 개입)
       └─ clock-skew → NTP re-sync + replay from offset
```

#### 5.2.1 다운그레이드 confidence penalty 표

| 상황 | 적용 페널티 | 누적 규칙 |
|------|-----------|----------|
| `EL_EVT_VERSION_UNSUPPORTED` (cross-MAJOR drop) | `-0.20` | per-request 최대 1회 |
| `EL_EVT_PAYLOAD_TOO_LARGE` (truncate 후 진행) | `-0.05` | 이벤트별 가산 |
| `EL_EVT_UNKNOWN_TYPE` (quarantine 후 보류) | `-0.10` | per-request 최대 2회 |
| `EL_EVT_FUTURE_TIMESTAMP` (clock-skew 복구 후 진행) | `-0.02` | per-event |

누적 penalty 가 `0.30` 을 초과하면 I-20 에 **에스컬레이션** (§6).

---

## §6. 에스컬레이션 페이로드 구조 (I-20)

LOCK-EL-01 검증 연속 실패/페널티 누적 시 I-20 (정책 게이트) 로 전달하는 데이터 구조.

```python
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class EscalationPayload(BaseModel):
    source_engine: str                 # 예: "6-12/event_schema_validator"
    error_code: str                    # 예: "EL_EVT_VERSION_UNSUPPORTED"
    original_request: Dict[str, Any]   # 원본 이벤트 envelope (PII 마스킹 후 — §2.2.6 PII 직접 포함 금지, 6-2 Security-Governance 마스킹 규칙 적용)
    partial_result: Optional[Dict[str, Any]]  # 검증 성공한 필드만 (예: timestamp, trace_id)
    retry_count: int                   # 이미 시도한 재시도 횟수
    timestamp: str                     # ISO 8601 UTC ms — 에스컬레이션 발생 시각
    # 보조 필드
    penalty_accumulated: float         # 이번 trace 에서 누적된 confidence penalty
    failure_chain: List[str]           # 이번 trace 에서 순차 발생한 error_code 리스트
    trace_id: str                      # 원본 이벤트 trace_id
```

**전달 경로**: R-01-8 에스컬레이션 규칙에 따라 I-20 entrypoint 로 동기 호출.

---

## §7. 로깅 포맷 (R-01-7)

검증 실패·에스컬레이션 시 structured JSON 로그를 다음 중첩 구조로 기록한다.

```json
{
  "timestamp": "2026-04-14T15:00:03.789Z",
  "level": "ERROR",
  "trace_id": "7b3a4e12-9d55-4a7c-bf10-2e1d3c9a8f04",
  "logger": "event_schema_validator",
  "message": "event envelope validation failed",
  "error": {
    "code": "EL_EVT_VERSION_UNSUPPORTED",
    "recoverable": false,
    "field": "version",
    "observed": "2.0.0",
    "expected_max_major": 1
  },
  "context": {
    "source_engine": "6-12/event_schema_validator",
    "event_type": "oc.i5.gates.evaluated",
    "source": "orange_core/i5_verifier",
    "request_id": "req-2026-04-14-00042",
    "phase": "Phase 2"
  },
  "recovery": {
    "action": "drop",
    "retry_count": 0,
    "penalty_applied": -0.20,
    "penalty_accumulated": 0.20,
    "escalated_to": "I-20"
  }
}
```

---

## §8. 금지 사용 패턴 (Anti-patterns)

| 안티패턴 | 이유 | 대체 |
|---------|------|------|
| 로컬 타임존 `timestamp` (`+09:00`) | 분산 환경 정렬 오류 | UTC `Z` 강제 |
| `event_type` 대문자/공백 포함 | 정규식 위반 | 소문자 + `.` + `_` 만 |
| `payload: null` | 파싱 분기 증가 | `payload: {}` |
| `trace_id` 재사용(신규 요청에서 기존 ID 차용) | trace 체인 오염 | 요청마다 신규 생성, 전파만 |
| PII 직접 payload 삽입 | 6-2 보안 정책 위반 | 해시/마스킹 후 삽입 |
| 필수 필드 누락 + `additionalProperties` 만 채움 | 스키마 깨짐 | 모든 required 필드 채움 |

---

## §9. Phase 2 통합 테스트 시나리오 (10건 이상)

| # | 시나리오 | 주입 방법 | 기대 결과 |
|---|---------|----------|----------|
| T-01 | 정상 envelope 발행 | §4.1 예시 그대로 publish | validation PASS, 하류 전달 |
| T-02 | `timestamp` 로컬 타임존 | `2026-04-14T00:00:00+09:00` 주입 | `EL_EVT_BAD_TIMESTAMP` drop + ERROR log |
| T-03 | `timestamp` 2초 미래 | `now + 2s` 주입 | `EL_EVT_FUTURE_TIMESTAMP` retry(clock-skew 복구 후 PASS) |
| T-04 | `event_type` 미등록 값 | `oc.fake.unknown` 주입 | quarantine → `dlq/unknown_type` + namespace_rules 등록 절차 트리거 |
| T-05 | `event_type` 대문자 포함 | `OC.I5.GATES.EVALUATED` 주입 | `EL_EVT_BAD_TYPE_FORMAT` drop |
| T-06 | `trace_id` all-zero W3C | `00000000000000000000000000000000` 주입 | `EL_EVT_BAD_TRACE_ID` drop |
| T-07 | `source` 슬래시 누락 | `orange_core_i5_verifier` 주입 | `EL_EVT_BAD_SOURCE` drop + 발행 모듈 경고 |
| T-08 | `version` MAJOR 2 envelope 수신 | `"version": "2.0.0"` 주입 | `EL_EVT_VERSION_UNSUPPORTED` drop + penalty `-0.20` |
| T-09 | `payload` `null` | `"payload": null` 주입 | `EL_EVT_PAYLOAD_NULL` auto-fix → `{}` 로 보정 후 PASS |
| T-10 | `payload` 20 KiB | 20KB random blob 주입 | truncate + `payload.truncated=true` + penalty `-0.05` |
| T-11 | penalty 누적 `> 0.30` | T-08 + T-10 + T-04 를 동일 trace 로 연속 주입 | EscalationPayload 구성 → I-20 호출, ERROR log §7 포맷 |
| T-12 | Docker 서비스명 mismatch (P2) | `source=orange_core/i5_verifier` 인데 실제 container `oc_core` | Phase 2 에서 `EL_EVT_SOURCE_MISMATCH`(P2-1 규칙 연계) alert |
| T-13 | trace_id 전파 단절 (P2) | S3→S4 에서 trace_id 재생성 | downstream 에 별도 `EL_TRACE_BROKEN` warning (P2-1 컨텍스트 전파 규칙 연계) |

---

## §10. 시간복잡도 및 ABC 패턴 매핑

- **validation 알고리즘**: 6개 필드 각각 O(1) 정규식/조회 → 전체 **O(1)** per event (상수 시간). `event_type` Registry 조회는 해시 맵 O(1).
- **LOCK 참조**: LOCK-EL-01 (스키마 필수 필드 6개), LOCK-EL-02 (event_type 허용집합 134항목, P1-2), LOCK-EL-09 (네임스페이스 정규식, P1-4)
- **ABC 패턴 매핑**:
  - **A** (Accept): envelope 파싱 / 필수 필드 존재 확인
  - **B** (Body/Business validate): 타입·포맷 검증, Registry 대조, version 지원 여부
  - **C** (Conclude): PASS → 하류 전달 / FAIL → drop|quarantine|retry|escalate (§5 표)

---

## §11. 세션 간 인터페이스 cross-check

| 세션 | 산출물 | 현재 P1-1 와의 인터페이스 | 상태 |
|------|--------|--------------------------|------|
| P1-2 | `event_type_registry.md` | `event_type` 허용값 집합 공급 | **예정** — §2.2.2 에서 참조 링크만 고정 |
| P1-3 | `pipeline_state_map.md` | 9-State↔event_type 매핑 사용 | 예정 |
| P1-4 | `namespace_rules.md` | `event_type` 정규식·등록 절차 | 예정 — §2.2.2 예상 규식 일치 설계 |
| P1-5 | `logging_levels.md` | `payload.severity` 권고값 | 예정 |
| P2-1 | `context_propagation.md` | `trace_id` Docker 전파 규칙 | 예정 — 본 §2.2.3 규약이 선행 |
| P2-2 | `structlog_format.md` | payload-per-type JSON 포맷 | 예정 — 본 §7 로그 포맷이 선행 |

본 세션은 선행 세션이 없고(Phase 1의 첫 파일), 후행 세션에 **정본**을 제공한다. 후행 산출물이 본 파일 §2 필수 필드·규약을 위반할 경우 본 파일이 우선한다(R-T6-1, LOCK-EL-01 근거).

---

## §12. ABC 시그니처 정본 준수

- 본 산출물은 data-spec 문서이며 Verifier/ReasoningEngine ABC 를 직접 상속하지 않는다.
- 향후 `EventSchemaValidator` 를 `BaseVerifier`(base_verifier_abc.md) 로 구현할 경우 메서드 시그니처는 정본대로 `async def verify(self, request: VerifyRequest) -> VerifyResult` 를 **그대로** 따른다. 타임아웃은 `VerifyRequest.timeout_ms` (R-01-3 필수 필드) 로 전달되며 별도 파라미터로 분리하지 않는다. 임의 변경 금지.

---

## §13. 상태 번호 정본 (S0~S8)

본 문서는 상태 번호를 **재정의하지 않는다**. 9-State 정본은 `_index.md §9-State↔이벤트 매핑` 의 S0~S8 (Part2 §6.11 원문) 을 따른다. 상세 매핑은 P1-3 `pipeline_state_map.md` 로 분리된다.

---

## §14. 검증 체크리스트 (§7 §P1-1 검증 항목)

- [x] 6개 필드(timestamp, event_type, trace_id, source, version, payload) 전부 포함
- [x] 각 필드에 타입, 필수여부, 설명 기재
- [x] LOCK-EL-01 참조 명시
- [x] 예시 JSON 블록 포함 (§4, 3건)
- [x] 교차 참조 블록 (§0)
- [x] Phase별 복구 전략 (§5.2)
- [x] 에스컬레이션 페이로드 구조 (§6)
- [x] 로깅 포맷 중첩 JSON (§7)
- [x] Phase 2 테스트 시나리오 13건 (§9, ≥10)
- [x] 시간복잡도 + LOCK + ABC 매핑 (§10)
- [x] 공통 자료 구조 선정의 (§3)
- [x] 세션 간 인터페이스 cross-check (§11)

---

## §15. 변경 이력

| 일자 | 세션 | 변경 내용 |
|------|------|----------|
| 2026-04-14 | P1-1 | 초안 작성 — LOCK-EL-01 6개 필수 필드 정본화, Pydantic/JSONSchema 동기 정의, 테스트 시나리오 13건 |
