# A-2. Conversation IPC Commands

> **그룹**: A-2 Conversation (8개 커맨드, LOCK-RT-01)
> **카테고리 소속**: Part2 Safety(19) 일부 — Conversation(8) (LOCK-RT-02 매핑표)
> **작성일**: 2026-04-11
> **이름 정본**: PHASE_B1 §5.1 / Part2 §6.2.1 (LOCK-RT-01)
> **메시지 프레이밍 정본**: `./message_framing.md` §3~§5 (FR-3 DEFINED-HERE); 에러 매트릭스는 본 파일 §2 정본

---

## 교차 참조

| 대상 | 경로 |
|-----|-----|
| LOCK-RT-01 이름 | `sot/PHASE_B1_API_CONTRACT.md` §5.1 |
| LOCK-RT-02 카테고리 | Part2 §6.2.1 Safety 그룹 |
| LOCK-RT-14 에러 | `RUST_TAURI_INFRASTRUCTURE_상세명세.md` §A 공통 에러 |
| LOCK-RT-06 이벤트 | D2.1-D2 §5.1 EventTypeRegistry `conversation.*` |
| Python bridge | `03_python-bridge/method_catalog.md` (T1-3) — `process_message` 위임 |
| Serde 모델 | `02_serde-models/core_models.md` (T1-2) — `ConversationTurn` |

---

## 1. 전수 시그니처 (8/8)

| # | invoke_name | 함수 시그니처 | 입력 | 출력 | TauriError | 타임아웃 | RBAC |
|---|---|---|---|---|---|---|---|
| 9 | `vamos:conversation:send` | `conversation_send(msg: UserMessage) -> Result<AssistantResponse, TauriError>` | `UserMessage` | `AssistantResponse` | PythonBridgeError, Timeout, ValidationError, InternalError | 120 s (LLM) | `conversation:write` |
| 10 | `vamos:conversation:stream` | `conversation_stream(msg: UserMessage) -> Result<StreamHandle, TauriError>` | `UserMessage` | `StreamHandle` | PythonBridgeError, Timeout, InternalError | 120 s | `conversation:write` |
| 11 | `vamos:conversation:retry` | `conversation_retry(turn_id: TurnId) -> Result<AssistantResponse, TauriError>` | `TurnId` | `AssistantResponse` | NotFound, PythonBridgeError, Timeout | 120 s | `conversation:write` |
| 12 | `vamos:conversation:edit` | `conversation_edit(turn_id: TurnId, new_content: String) -> Result<(), TauriError>` | `(TurnId, String)` | `()` | NotFound, ValidationError, IoError | 800 ms | `conversation:write` |
| 13 | `vamos:conversation:branch` | `conversation_branch(turn_id: TurnId) -> Result<BranchId, TauriError>` | `TurnId` | `BranchId` | NotFound, IoError, InternalError | 800 ms | `conversation:write` |
| 14 | `vamos:conversation:get_history` | `conversation_get_history(session_id: SessionId, range: Range) -> Result<Vec<Turn>, TauriError>` | `(SessionId, Range)` | `Vec<Turn>` | NotFound, IoError, Timeout | 1500 ms | `conversation:read` |
| 15 | `vamos:conversation:clear` | `conversation_clear(session_id: SessionId) -> Result<(), TauriError>` | `SessionId` | `()` | NotFound, PermissionDenied, IoError | 800 ms | `conversation:delete` |
| 16 | `vamos:conversation:summarize` | `conversation_summarize(session_id: SessionId) -> Result<String, TauriError>` | `SessionId` | `String` | NotFound, PythonBridgeError, Timeout | 30 s | `conversation:read` |

**합계 검증**: 8/8 커맨드 (LOCK-RT-01 ID 9~16).

## 2. 에러 매트릭스 (8 × 7)

| 커맨드 \ Err | NotFound | ValidationError | PythonBridgeError | IoError | Timeout | PermissionDenied | InternalError |
|---|---|---|---|---|---|---|---|
| conversation_send | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| conversation_stream | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| conversation_retry | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ |
| conversation_edit | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ |
| conversation_branch | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ |
| conversation_get_history | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ |
| conversation_clear | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ |
| conversation_summarize | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ |

**커버리지**: 7/7 TauriError variant.

## 3. LOCK-RT-06 이벤트 교차 참조

| 커맨드 | 이벤트 후보 |
|-------|-----------|
| send/stream/retry | `conversation.turn.added`, `conversation.llm.failed` |
| edit | `conversation.turn.edited` |
| branch | `conversation.branch.created` |
| clear | `conversation.cleared` |
| summarize | `conversation.summary.generated` |

> 실제 enum 값은 D2.1-D2 §5.1 EventTypeRegistry **134건** LOCK 내에서 채택한다(LOCK-RT-06, Phase 11 S11-6 SC-13 갱신 — D2.1-D2 baseline 123 → 6-12 정본 134).

## 4. Python 위임 요약 (03_python-bridge 연계)

| 커맨드 | JSON-RPC 메서드 (LOCK-RT-03) |
|-------|-----------------------------|
| conversation_send | `process_message` |
| conversation_stream | `process_message` (streaming) |
| conversation_retry | `process_message` |
| conversation_summarize | `process_message` (summary prompt) |
| 나머지 (edit/branch/clear/get_history) | Rust 단독 (DB 조작) |

## 5. 복구 전략

| 에러 | 1차 | 2차 | Confidence Penalty |
|-----|----|----|--------------------|
| PythonBridgeError | 프로세스 재시작 후 1회 재시도 | 회로차단기 OPEN | -0.3 |
| Timeout (LLM 120s) | 사용자 재시도 제안 | 모델 다운그레이드 제안 | -0.2 |
| NotFound | turn_id 검증 UI | 세션 리로드 | N/A |

## 6. 구조화 로그 예시

```json
{
  "ts": "...", "level": "ERROR", "trace_id": "...",
  "source": "rust_tauri.ipc.conversation",
  "invoke_name": "vamos:conversation:send",
  "error": { "type": "TauriError::PythonBridgeError", "code": -32001, "message": "..." },
  "context": { "session_id": "...", "turn_index": 42, "model": "gpt-4o" },
  "recovery": { "attempt": 2, "strategy": "python_restart", "fallback": "degrade_model" }
}
```

## 7. Phase 2 테스트 시나리오 (10건)

1. TS-C1 — 정상 send → 응답 수신
2. TS-C2 — 긴 프롬프트(10k 토큰) stream 성공 유지
3. TS-C3 — Python 브릿지 죽음 → 재시작 후 재시도 성공
4. TS-C4 — 타임아웃 경계(119s) → 성공 / 121s → `Timeout`
5. TS-C5 — 존재하지 않는 turn_id retry → `NotFound`
6. TS-C6 — edit + get_history → 수정본 반영 확인
7. TS-C7 — branch 후 독립 히스토리 분기 확인
8. TS-C8 — clear 권한 박탈 → `PermissionDenied`
9. TS-C9 — 손상된 Serde 역직렬화 → `ValidationError`
10. TS-C10 — summarize 짧은 세션(1턴) → `String` 반환

---

<!-- END OF DOCUMENT -->

---

# §V2. IPC 보안 강화 — T2-2 (ISS-07 해소)

> **Phase 2 T2-2 산출물** (ISS-07 해소, plan §7 T2-2 L977~L1008 + §A.4 L1266~L1276 정본 verbatim)
> **작성일**: 2026-04-24
> **대상 V1 커맨드**: A-2 Conversation 8개 (ID 9-16, Part2 카테고리: Safety)
> **LOCK 근거**: LOCK-RT-01 (IPC 72 커맨드 이름) / LOCK-RT-02 (5분류) / LOCK-RT-14 (TauriError 7 variant)
> **V1 본문**: 불변 (§1~§N 위 모든 내용 append-only 엄수, byte-prefix SHA 검증 대상)
> **baseline**: `577ee055690f9e35` / bytes=6115 / lines=112

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
| SEC-1 | 입력 검증 (Serde + validator) | ✅ 적용 | 전수 8/8 | ValidationError |
| SEC-2 | trace_id UUID v7 위조 탐지 | ✅ 적용 | 전수 8/8 | ValidationError |
| SEC-3 | RBAC Permission Level 사전 체크 | ✅ 적용 | 전수 8/8 | PermissionDenied |
| SEC-4 | 경로 탐색 방지 (canonicalize + whitelist) | — (N/A) | 해당 없음 | ValidationError / PermissionDenied |
| SEC-5 | 주입 방지 (이스케이프 + 파라미터화) | — (N/A) | 해당 없음 | ValidationError |
| SEC-6 | 레이트 리밋 (D4 RateLimitConfig) | ✅ 적용 | 전수 8/8 | InternalError (rate_limit) |
| SEC-7 | HMAC-SHA256 서명 (constant-time) | — (N/A) | 해당 없음 | ValidationError (signature) |

### 적용 설명
- **SEC-1 입력 검증**: Serde `#[derive(Deserialize)]` + custom validator (예: `session_id: validate_uuid_v7`) 72 커맨드 공통 1순위
- **SEC-2 trace_id 검증**: UUID v7 형식 강제 (`00000000-0000-7xxx-yyyy-xxxxxxxxxxxx`, variant bits `10`) + 시간 역전/미래 1h 초과 거부
- **SEC-3 RBAC Permission Level**: V1 §1 표의 `RBAC` 열 정본 사용, session_open 시점 확정된 level 과 대조
- **SEC-6 레이트 리밋**: Safety 1000 req/s (LLM 스트리밍 경로 포함) (message_framing §V2 카테고리 정본 표 — Core 100/Agent 50/Storage 200/Safety 1000/UI 100, D4 RateLimitConfig 연동, 초과 시 `InternalError { message: "rate_limit_exceeded" }`)

## §V2.3 LOCK 5필드 매핑

| LOCK ID | 항목 | 정본 출처 | 값 | 재정의 |
|---------|------|-----------|-----|--------|
| LOCK-RT-01 | IPC 커맨드 이름 | PHASE_B1 §5.1 / Part2 §6.2.1 (공동) | `vamos:conversation:*` 8개 (ID 9-16) | ❌ |
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
    file_scope: Literal["A-2 Conversation"] = "A-2 Conversation"
```

## §V2.8 구조화 로그 3-block (LOCK-RT-15 stderr 분리)

### block-1: SEC-1 Validation 실패
```json
{
  "source": "rust_tauri.ipc.cnv.sec",
  "sec_id": "SEC-1",
  "invoke_name": "vamos:conversation:example",
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
  "source": "rust_tauri.ipc.cnv.sec",
  "sec_id": "SEC-3",
  "invoke_name": "vamos:conversation:example",
  "tauri_error": "PermissionDenied",
  "required_level": "conversation:admin",
  "actual_level": "user",
  "severity": "Error"
}
```

### block-3: SEC-6 Rate limit trip
```json
{
  "source": "rust_tauri.ipc.cnv.sec",
  "sec_id": "SEC-6",
  "invoke_name": "vamos:conversation:example",
  "tauri_error": "InternalError",
  "message": "rate_limit_exceeded",
  "window_s": 1,
  "limit": "Safety 50 req/s (LLM 스트리밍)",
  "severity": "Info"
}
```

> **LOCK-RT-15 준수**: 위 3 블록은 **stderr** 로그 전용, stdout 은 JSON-RPC 응답 전용 (혼선 절대 금지).

## §V2.9 Phase 3 테스트 시나리오 (CNV, ≥ 10건)

1. TS-SEC-CNV-1 — UserMessage.content 1MB 초과 → `ValidationError { field: content, too_large }`
2. TS-SEC-CNV-2 — conversation_stream 50 req/s 초과 (LLM 스트리밍) → `InternalError rate_limit`
3. TS-SEC-CNV-3 — turn_id UUID 위조 → `ValidationError { field: turn_id, format }`
4. TS-SEC-CNV-4 — 타 세션 conversation_edit 시도 → `PermissionDenied`
5. TS-SEC-CNV-5 — trace_id SEC-2 통과 + RBAC ✅ → 첫 토큰 ≤ 200ms (SLA P99)
6. TS-SEC-CNV-6 — conversation_branch 부모 turn 없음 → `NotFound`
7. TS-SEC-CNV-7 — conversation_summarize 빈 session → `ValidationError`
8. TS-SEC-CNV-8 — Serde UserMessage 필드 누락 → `ValidationError { field: role }`
9. TS-SEC-CNV-9 — retry turn_id mismatch session → `NotFound`
10. TS-SEC-CNV-10 — conversation_clear admin only → `PermissionDenied` for user role

## §V2.10 자가 체크리스트 (품질 필수 구조 #1~#8 적용)

- [x] §1 교차 참조 블록 (§V2.1): peer V2 + plan §A.4 + 상세명세 §A + upstream SoT 전수
- [x] §2 공통 자료 구조 참조 (§V2.3): LOCK-RT-01/02/14 5필드 분리 인용 (ID × 항목 × 정본 출처 × 값 × 재정의)
- [x] §3 SEC-1~7 규칙 매트릭스 (§V2.2): 본 파일 적용 여부 + 범위 + TauriError 매핑 전수 표
- [x] §4 카테고리 특화 (§V2.4/§V2.5/§V2.7): SEC-4/5/7 중 본 파일 해당 섹션만 상세화
- [x] §N LOCK panel (§V2.3) + §N.1 에스컬레이션 Pydantic (§V2.6) + §N.2 구조화 로그 3-block (§V2.8)
- [x] §N Phase 3 테스트 시나리오 ≥ 10건 (§V2.9): TS-SEC-CNV-1~10 실체화
- [x] §N 세션 간 cross-check: peer T2-1 V2 (build/signing) + T2-3 plan §A.3 SLA + T2-4 V2 (메트릭) 실체 참조
- [x] 자가 체크리스트 (§V2.10): 본 항목, §3.1~§3.5 anti-fabrication 가이드 준수

---

<!-- END OF §V2 (T2-2) -->
