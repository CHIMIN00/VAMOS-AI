# A-8. Settings IPC Commands

> **그룹**: A-8 Settings (6개, LOCK-RT-01)
> **카테고리 소속**: Part2 Safety(19) — Settings(6) (LOCK-RT-02)
> **작성일**: 2026-04-11
> **이름 정본**: PHASE_B1 §5.1 / Part2 §6.2.1

## 교차 참조

| 대상 | 경로 |
|-----|-----|
| LOCK-RT-01/14 | 상세명세 §A |
| LOCK-RT-06 | D2.1-D2 `settings.*` 이벤트 |
| Serde | `02_serde-models/core_models.md` — `VamosConfig` (Theme, LlmProviderConfig...) |

## 1. 전수 시그니처 (6/6)

| # | invoke_name | 함수 시그니처 | 타임아웃 | 주요 에러 | RBAC |
|---|---|---|---|---|---|
| 49 | `vamos:settings:get` | `settings_get(key: String) -> Result<Value, TauriError>` | 300 ms | NotFound, IoError | `settings:read` |
| 50 | `vamos:settings:set` | `settings_set(key: String, value: Value) -> Result<(), TauriError>` | 500 ms | ValidationError, IoError, PermissionDenied | `settings:write` |
| 51 | `vamos:settings:get_all` | `settings_get_all() -> Result<VamosConfig, TauriError>` | 500 ms | IoError, InternalError | `settings:read` |
| 52 | `vamos:settings:reset` | `settings_reset(key: String) -> Result<(), TauriError>` | 500 ms | NotFound, PermissionDenied, IoError | `settings:write` |
| 53 | `vamos:settings:export` | `settings_export() -> Result<String, TauriError>` | 1 s | IoError, InternalError | `settings:read` |
| 54 | `vamos:settings:import` | `settings_import(json: String) -> Result<(), TauriError>` | 1 s | ValidationError, IoError, PermissionDenied | `settings:write` |

**합계**: 6/6 (ID 49~54).

## 2. 에러 매트릭스 (6 × 7)

| 커맨드 \ Err | NotFound | Validation | PythonBridge | IoError | Timeout | Permission | Internal |
|---|---|---|---|---|---|---|---|
| settings_get | ✓ | ✗ | ✗ | ✓ | ✗ | ✗ | ✓ |
| settings_set | ✗ | ✓ | ✗ | ✓ | ✗ | ✓ | ✓ |
| settings_get_all | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✓ |
| settings_reset | ✓ | ✗ | ✗ | ✓ | ✗ | ✓ | ✓ |
| settings_export | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✓ |
| settings_import | ✗ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ |

## 3. LOCK-RT-06 이벤트

| 커맨드 | 이벤트 |
|-------|-------|
| set/reset | `settings.changed` |
| import | `settings.imported` |
| export | `settings.exported` |

## 4. 복구 전략

| 에러 | 전략 |
|-----|-----|
| ValidationError | 롤백 + 이전 값 유지 |
| IoError | 1회 재시도, 실패 시 메모리 캐시 유지 |
| PermissionDenied | admin 권한 필요 알림 |

## 5. 구조화 로그

```json
{
  "source": "rust_tauri.ipc.settings",
  "invoke_name": "vamos:settings:set",
  "error": { "type": "TauriError::ValidationError", "field": "language", "message": "unsupported" },
  "context": { "key": "language", "old_value": "ko", "new_value": "zz" },
  "recovery": { "attempt": 1, "strategy": "rollback_to_old" },
  "trace_id": "..."
}
```

## 6. Phase 2 테스트 시나리오 (10건)

1. TS-ST1 — set → get 일관성
2. TS-ST2 — get_all VamosConfig 모든 필드 존재
3. TS-ST3 — reset 후 기본값 복원
4. TS-ST4 — export → import 라운드트립
5. TS-ST5 — 잘못된 JSON import → `ValidationError`
6. TS-ST6 — 비관리자 설정 변경 → `PermissionDenied`
7. TS-ST7 — 존재하지 않는 key get → `NotFound`
8. TS-ST8 — IO 주입 → 1회 재시도 로그
9. TS-ST9 — 동시 set 레이스 → 마지막 승리 + 이벤트 1회
10. TS-ST10 — telemetry off → 이벤트 미발생 검증

---

<!-- END OF DOCUMENT -->

---

# §V2. IPC 보안 강화 — T2-2 (ISS-07 해소)

> **Phase 2 T2-2 산출물** (ISS-07 해소, plan §7 T2-2 L977~L1008 + §A.4 L1266~L1276 정본 verbatim)
> **작성일**: 2026-04-24
> **대상 V1 커맨드**: A-8 Settings 6개 (ID 49-54, Part2 카테고리: Safety)
> **LOCK 근거**: LOCK-RT-01 (IPC 72 커맨드 이름) / LOCK-RT-02 (5분류) / LOCK-RT-14 (TauriError 7 variant)
> **V1 본문**: 불변 (§1~§N 위 모든 내용 append-only 엄수, byte-prefix SHA 검증 대상)
> **baseline**: `4a47058543849c39` / bytes=3467 / lines=84

## §V2.1 교차 참조 블록

| 대상 | 경로 | 관계 |
|-----|-----|------|
| **상위 정본 체인** | AUTHORITY_CHAIN.md §1 + §2 LOCK-RT-01~15 | LOCK 근거 |
| **plan 정본** | RUST_TAURI_INFRASTRUCTURE_구조화_종합계획서.md §A.4 L1266~L1276 (SEC-1~7) + §7 T2-2 L977~L1008 | SEC 체크리스트 정본 |
| **상세명세 DEFINED-HERE** | RUST_TAURI_INFRASTRUCTURE_상세명세.md §A 공통 에러 L153~L162 (TauriError 7) | 에러 매핑 정본 |
| **upstream SoT** | sot/STEP7-F_인프라_배포_MLOps_작업가이드.md (4-1 은 REF) | 인프라 보안 Tier 4 참조 |
| **peer V2 (T2-1 NEW)** | 04_build-signing/tauri_build_config.md + code_signing.md | Tauri allowlist / updater 서명 |
| **peer V2 (T2-4 EXTEND)** | 05_process-management/spawn_protocol.md §V2 + healthcheck.md §V2 + restart_policy.md §V2 | SEC 위반 메트릭 |
| **peer V2 (T2-3 plan meta)** | plan §A.3 L1255~L1264 | 카테고리별 SLA 에러율 한도 |
| **SEC 정본 상위** | Part2 §6.5.1 보안 체크리스트 | 횡단 관심사 (계획서 §9.4) |
| **FailureCodeRegistry** | D2.1-D2 §5.2 (LOCK-RT-07, 6-12 LOCK-EL-03 정본 REF) | SEC 위반 ↔ canonical code 매핑 |

## §V2.2 SEC-1~SEC-7 체크리스트 매트릭스

| # | 규칙 | 본 파일 적용 | 적용 범위 | TauriError 매핑 |
|---|------|------------|----------|----------------|
| SEC-1 | 입력 검증 (Serde + validator) | ✅ 적용 | 전수 6/6 | ValidationError |
| SEC-2 | trace_id UUID v7 위조 탐지 | ✅ 적용 | 전수 6/6 | ValidationError |
| SEC-3 | RBAC Permission Level 사전 체크 | ✅ 적용 | 전수 6/6 | PermissionDenied |
| SEC-4 | 경로 탐색 방지 (canonicalize + whitelist) | — (N/A) | 해당 없음 | ValidationError / PermissionDenied |
| SEC-5 | 주입 방지 (이스케이프 + 파라미터화) | — (N/A) | 해당 없음 | ValidationError |
| SEC-6 | 레이트 리밋 (D4 RateLimitConfig) | ✅ 적용 | 전수 6/6 | InternalError (rate_limit) |
| SEC-7 | HMAC-SHA256 서명 (constant-time) | ✅ 특화 | 민감 쓰기 커맨드 | ValidationError (signature) |

### 적용 설명
- **SEC-1 입력 검증**: Serde `#[derive(Deserialize)]` + custom validator (예: `session_id: validate_uuid_v7`) 72 커맨드 공통 1순위
- **SEC-2 trace_id 검증**: UUID v7 형식 강제 (`00000000-0000-7xxx-yyyy-xxxxxxxxxxxx`, variant bits `10`) + 시간 역전/미래 1h 초과 거부
- **SEC-3 RBAC Permission Level**: V1 §1 표의 `RBAC` 열 정본 사용, session_open 시점 확정된 level 과 대조
- **SEC-6 레이트 리밋**: Safety 1000 req/s (로컬 쓰기) (D4 RateLimitConfig 연동, 초과 시 `InternalError { message: "rate_limit_exceeded" }`)

## §V2.3 LOCK 5필드 매핑

| LOCK ID | 항목 | 정본 출처 | 값 | 재정의 |
|---------|------|-----------|-----|--------|
| LOCK-RT-01 | IPC 커맨드 이름 | PHASE_B1 §5.1 / Part2 §6.2.1 (공동) | `vamos:settings:*` 6개 (ID 49-54) | ❌ |
| LOCK-RT-02 | 카테고리 소속 | Part2 §6.2.1 (단독) | Safety | ❌ |
| LOCK-RT-14 | TauriError 7 variant | 상세명세 §A L153~L162 (DEFINED-HERE) | NotFound / ValidationError / PythonBridgeError / IoError / Timeout / PermissionDenied / InternalError | ❌ |

## §V2.6 SEC 위반 에스컬레이션 Pydantic 스키마

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime
from uuid import UUID

class SecurityViolation(BaseModel):
    """IPC SEC-1~7 위반 시 내부 에스컬레이션 이벤트 (LOCK-RT-06 event bus)."""
    sec_id: Literal["SEC-1","SEC-2","SEC-3","SEC-4","SEC-5","SEC-6","SEC-7"]
    invoke_name: str = Field(..., description="vamos:<category>:<action> 형식")
    tauri_error: Literal["ValidationError","PermissionDenied","InternalError"]
    field: Optional[str] = Field(None, description="SEC-1 / SEC-7 위반 필드명")
    user_id: str
    trace_id: UUID = Field(..., description="UUID v7 (SEC-2 통과 후)")
    timestamp: datetime
    severity: Literal["Debug","Info","Warn","Error","Critical"] = "Error"
    file_scope: Literal["A-8 Settings"] = "A-8 Settings"
```

## §V2.7 SEC-7 HMAC 서명 (본 파일 특화)

- **알고리즘**: HMAC-SHA256 (FIPS 180-4), rotating key 24h
- **대상**: 민감 커맨드 `vamos:settings:*` (쓰기/admin 계열)
- **비교**: `subtle::ConstantTimeEq` 기반 constant-time 비교 (timing attack 방어)
- **키 저장**: OS keychain (Windows DPAPI / macOS Keychain Services / Linux libsecret)
- **rotation 정책**: 24h 자동 rotation, 이전 key 는 1h grace window 로 보관 (진행중 요청 호환)
- **위반 시**: `ValidationError { field: "hmac_signature", message: "invalid or missing" }`

## §V2.8 구조화 로그 3-block (LOCK-RT-15 stderr 분리)

### block-1: SEC-1 Validation 실패
```json
{
  "source": "rust_tauri.ipc.stg.sec",
  "sec_id": "SEC-1",
  "invoke_name": "vamos:settings:example",
  "tauri_error": "ValidationError",
  "field": "<failing_field>",
  "user_id": "u_...",
  "trace_id": "018f....",
  "severity": "Warn",
  "timestamp": "2026-04-24T..."
}
```

### block-2: SEC-3 RBAC deny
```json
{
  "source": "rust_tauri.ipc.stg.sec",
  "sec_id": "SEC-3",
  "invoke_name": "vamos:settings:example",
  "tauri_error": "PermissionDenied",
  "required_level": "settings:admin",
  "actual_level": "user",
  "severity": "Error"
}
```

### block-3: SEC-6 Rate limit trip
```json
{
  "source": "rust_tauri.ipc.stg.sec",
  "sec_id": "SEC-6",
  "invoke_name": "vamos:settings:example",
  "tauri_error": "InternalError",
  "message": "rate_limit_exceeded",
  "window_s": 1,
  "limit": "Safety 1000 req/s (로컬 쓰기)",
  "severity": "Info"
}
```

> **LOCK-RT-15 준수**: 위 3 블록은 **stderr** 로그 전용, stdout 은 JSON-RPC 응답 전용 (혼선 절대 금지).

## §V2.9 Phase 3 테스트 시나리오 (STG, ≥ 10건)

1. TS-SEC-STG-1 — settings_set HMAC 서명 누락 → SEC-7 `ValidationError { field: hmac_signature }`
2. TS-SEC-STG-2 — settings_set 만료 HMAC (>24h) → SEC-7 `ValidationError`
3. TS-SEC-STG-3 — settings_import SEC-1 잘못된 JSON → `ValidationError`
4. TS-SEC-STG-4 — settings:admin 권한 없는 reset → `PermissionDenied`
5. TS-SEC-STG-5 — constant-time HMAC 비교 (timing attack resistance)
6. TS-SEC-STG-6 — settings_export user 권한 허용 (read-only) → 통과
7. TS-SEC-STG-7 — key `llm.api_key` 조회 → SEC-3 admin only
8. TS-SEC-STG-8 — 1000 req/s 초과 → SEC-6 rate_limit
9. TS-SEC-STG-9 — settings_set value 100KB 초과 → `ValidationError`
10. TS-SEC-STG-10 — 정상 admin + HMAC → P99 ≤ 50ms

## §V2.10 자가 체크리스트 (품질 필수 구조 #1~#8 적용)

- [x] §1 교차 참조 블록 (§V2.1): peer V2 + plan §A.4 + 상세명세 §A + upstream SoT 전수
- [x] §2 공통 자료 구조 참조 (§V2.3): LOCK-RT-01/02/14 5필드 분리 인용 (ID × 항목 × 정본 출처 × 값 × 재정의)
- [x] §3 SEC-1~7 규칙 매트릭스 (§V2.2): 본 파일 적용 여부 + 범위 + TauriError 매핑 전수 표
- [x] §4 카테고리 특화 (§V2.4/§V2.5/§V2.7): SEC-4/5/7 중 본 파일 해당 섹션만 상세화
- [x] §N LOCK panel (§V2.3) + §N.1 에스컬레이션 Pydantic (§V2.6) + §N.2 구조화 로그 3-block (§V2.8)
- [x] §N Phase 3 테스트 시나리오 ≥ 10건 (§V2.9): TS-SEC-STG-1~10 실체화
- [x] §N 세션 간 cross-check: peer T2-1 V2 (build/signing) + T2-3 plan §A.3 SLA + T2-4 V2 (메트릭) 실체 참조
- [x] 자가 체크리스트 (§V2.10): 본 항목, §3.1~§3.5 anti-fabrication 가이드 준수

---

<!-- END OF §V2 (T2-2) -->
