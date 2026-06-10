# transition_matrix.md — 9-State UI State Machine 전이 매트릭스

> **도메인**: 6-11_Hologram-Main-LLM / 03_ui-state-machine
> **출처**: D2.0-08 §4 (L335-352, LOCK-HM-03 정본), Part2 §6.1.6 (L4622-4642), 계획서 §A.5
> **LOCK**: LOCK-HM-03 (9-State UI State Machine)
> **정본 소유**: 6-11 DEFINED-HERE (상태 이름·번호는 D2.0-08 LOCK; 전이 매트릭스 상세는 DEFINED-HERE)
> **Phase 배정**: Phase 1 T1-5
> **작성일**: 2026-04-14
> **세션**: TASK_ID=6-11_T1-5_step1_2026-04-14T07-05-00
> **쌍방 문서**: `state_definitions.md` (상태 정의 본문)

---

## 0. 메타데이터 / 교차 참조

### 0.1 LOCK 메타데이터

| 필드 | 값 |
|------|----|
| LOCK ID | **LOCK-HM-03** |
| 항목명 | 9-State UI State Machine 전이 매트릭스 |
| 정본 출처 | `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §4.1 ~ §4.6 |
| §4.2 기본 전환 | 6건 (T1~T6) — 원문 그대로 |
| 확장 전이 (DEFINED-HERE) | 본 문서에서 초기화·아카이브·복구 경로 보강 |
| 연관 규칙 | R-611-5 (이벤트 기반), R-T6-3 (레이아웃 정합성) |

### 0.2 교차 참조 블록

| 참조 | 대상 | 역할 |
|------|------|------|
| D2.0-08 §4.1 (L335-344) | 9개 상태 정규명 | LOCK (노드) |
| D2.0-08 §4.2 (L346-352) | 전이 6건 트리거 원문 | LOCK (엣지 정본) |
| D2.0-08 §4.3 | Decision Lock 제약 | 가드 |
| D2.0-08 §4.4 | 런타임 6-State | EngineState 매핑 |
| D2.0-08 §4.5 | 9↔6 매핑 | 일관성 |
| D2.0-08 §4.6 | Pipeline ↔ UI 매핑 | 일관성 (D8-M11) |
| Part2 §6.1.6 (L4622-4642) | 주요 전이 재확인 | 쌍방 대조 |
| `state_definitions.md` | 노드 정의 | 쌍방 문서 |
| `_index.md` | 폴더 인덱스 | 상위 |
| `07_orchestration-layer/` | I-10 오케스트레이션 | EngineState ↔ UIState |
| 6-9 Brain-Adapter-HAL | Core 상태 계약 | 1:1 반영 |
| 6-12 Event-Logging | 전이 이벤트 로깅 | 중첩 JSON |

---

## 1. 공통 자료 구조 (선정의)

> `state_definitions.md` §1과 동일 정의 — 본 문서는 **전이 엣지 스키마**를 추가.

### 1.1 `Transition` 인터페이스

```typescript
export interface Transition {
  id: string;                      // T1~T6(§4.2) 또는 TX-## (DEFINED-HERE)
  from: UIState;
  to: UIState;
  trigger: string;                 // 이벤트 ID (도트 네임)
  guard?: (ctx: StateContext) => boolean;   // 전이 허용 가드
  action?: (ctx: StateContext) => void;     // 전이 시 실행 액션
  engineSideEffect?: "emit" | "sync" | "none";
  lockSource: "D2.0-08 §4.2" | "DEFINED-HERE";
  errorCode?: string;              // 실패 경로 엣지에만
}
```

### 1.2 `TransitionEvent` 로깅 스키마 (중첩 JSON)

```json
{
  "event": "ui.state.transition",
  "correlationId": "<uuid>",
  "transition": {
    "id": "T2",
    "from": "UI_S4_RUNNING",
    "to":   "UI_S5_AWAIT_APPROVAL",
    "trigger": "core.approval_required",
    "duration_ms": 120
  },
  "guards":  { "approvalRequired": true },
  "actions": ["modal.open:approval", "timer.start", "hud.render:cost_panel"],
  "context": {
    "engineState":   "UIS5AWAITAPPROVAL",
    "pipelineStage": "S4_EXECUTING",
    "costEstimateUSD": 2.8
  },
  "lockSource": "D2.0-08 §4.2"
}
```

---

## 2. §4.2 기본 전이 6건 (LOCK, 원문 유지)

| ID | FROM | TO | 트리거 (원문) | 가드 | 액션 | lockSource |
|----|------|----|---------------|------|------|-----------|
| **T1** | UI_S1_IDLE | UI_S4_RUNNING | 전송/실행 | `input.nonEmpty ∧ preflight.pass` | `core.exec.start`, `stream.open`, `hud.render:progress` | §4.2 |
| **T2** | UI_S4_RUNNING | UI_S5_AWAIT_APPROVAL | approval_required=true | `approvalRequired === true` | `modal.open:approval`, `timer.start`, `hud.render:cost_panel` | §4.2 |
| **T3** | UI_S5_AWAIT_APPROVAL | UI_S4_RUNNING | 승인(Approve) | `user.role ∈ approvers` | `core.exec.resume`, `modal.close`, `timer.stop` | §4.2 |
| **T4** | UI_S4_RUNNING | UI_S7_RECOVERY | failure(도구/근거/포맷 등) | `failureCode ≠ null` | `escalation.emit`, `stream.abort`, `hud.render:recovery` | §4.2 |
| **T5** | UI_S7_RECOVERY | UI_S4_RUNNING | 재시도/대안 선택 | `retryAxis ∈ {evidence, execution, format}` (§4.3) | `core.exec.retry(axis)`, `penalty.apply` | §4.2 |
| **T6** | UI_S4_RUNNING | UI_S6_PRESENTING | output_ready | `outputReady === true` | `output.bind:3point`, `hud.render:evidence`, `timeline.commit` | §4.2 |

---

## 3. 확장 전이 (DEFINED-HERE — §4.1 상태 노드는 LOCK 준수)

> 초기화/아카이브/복구 파생/취소/편집 경로는 §4.1 상태 노드를 사용하되 엣지는 본 문서에서 정의.

| ID | FROM | TO | 트리거 | 가드 | 액션 | lockSource |
|----|------|----|--------|------|------|-----------|
| TX-01 | — (init) | UI_S0_BOOT | `app.load` | — | `store.hydrate`, `auth.verify` | DEFINED-HERE |
| TX-02 | UI_S0_BOOT | UI_S1_IDLE | `hydrate.complete` | `auth.valid ∧ hydrate.ok` | `layout.resolveInitial`, `input.focus` | DEFINED-HERE |
| TX-03 | UI_S0_BOOT | UI_S7_RECOVERY | `auth.expired` | `token.expired` | `escalation.emit(ERR-SM-002)` | DEFINED-HERE |
| TX-04 | UI_S1_IDLE | UI_S2_EDITING | `builder.open` | `layout === "builder"` (Hologram 외) | `editor.mount` | DEFINED-HERE |
| TX-05 | UI_S2_EDITING | UI_S3_READY | `preflight.pass` | `validation.ok` | `runButton.enable`, `cost.estimate` | DEFINED-HERE |
| TX-06 | UI_S2_EDITING | UI_S1_IDLE | `builder.cancel` | — | `editor.unmount` | DEFINED-HERE |
| TX-07 | UI_S3_READY | UI_S4_RUNNING | `user.run` | `preflight.pass ∧ cost ≤ budget` | `core.exec.start`, `stream.open` | DEFINED-HERE (§4.2 T1 별칭) |
| TX-08 | UI_S3_READY | UI_S7_RECOVERY | `preflight.recheck.fail` | `revalidation.fail` | `escalation.emit(ERR-SM-003)` | DEFINED-HERE |
| TX-09 | UI_S4_RUNNING | UI_S1_IDLE | `user.cancel` | `decisionLocked === false` | `core.exec.abort`, `stream.close` | DEFINED-HERE |
| TX-10 | UI_S5_AWAIT_APPROVAL | UI_S7_RECOVERY | `user.reject` | — | `escalation.emit(ERR-SM-007)`, `penalty.apply(0.5)` | DEFINED-HERE |
| TX-11 | UI_S5_AWAIT_APPROVAL | UI_S7_RECOVERY | `approval.timeout` | `elapsed > timeoutMs` | `escalation.emit(ERR-SM-008)`, `penalty.apply(0.25)` | DEFINED-HERE |
| TX-12 | UI_S6_PRESENTING | UI_S1_IDLE | `user.newInput` | — | `stream.reset`, `input.focus` | DEFINED-HERE |
| TX-13 | UI_S6_PRESENTING | UI_S8_ARCHIVED | `user.archive` | `session.complete` | `session.freeze`, `timeline.lock` | DEFINED-HERE |
| TX-14 | UI_S7_RECOVERY | UI_S1_IDLE | `user.abort` OR `penalty ≤ 0` | — | `session.soft_reset`, `escalation.emit(ERR-SM-009)` | DEFINED-HERE |
| TX-15 | UI_S8_ARCHIVED | UI_S0_BOOT | `session.restart` | — | `session.new`, `store.reset` | DEFINED-HERE |
| TX-16 | any | `engineState`에 의해 결정 (기본 UI_S7_RECOVERY, `A-SYNC-FORCE`가 엔진 상태로 수렴) | `ui.core.state.mismatch` (persist>500ms) | `mismatch.duration > 500` | `sync.force`, `escalation.emit(ERR-SM-010)` | DEFINED-HERE (§4.4) |

---

## 4. FROM × TO 매트릭스 (9×9)

> 셀 내용: `[id:trigger]` 또는 `—` (금지). 가드/액션 상세는 §2, §3 참조.

| FROM \ TO | UI_S0_BOOT | UI_S1_IDLE | UI_S2_EDITING | UI_S3_READY | UI_S4_RUNNING | UI_S5_AWAIT_APPROVAL | UI_S6_PRESENTING | UI_S7_RECOVERY | UI_S8_ARCHIVED |
|-----------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **UI_S0_BOOT** | — | TX-02:hydrate.complete | — | — | — | — | — | TX-03:auth.expired / TX-03b:hydrate.fail | — |
| **UI_S1_IDLE** | — | — | TX-04:builder.open | — | T1:user.send | — | — | TX-16:mismatch | — |
| **UI_S2_EDITING** | — | TX-06:builder.cancel | — | TX-05:preflight.pass | — | — | — | TX-16:mismatch | — |
| **UI_S3_READY** | — | — | — | — | TX-07:user.run | — | — | TX-08:preflight.recheck.fail | — |
| **UI_S4_RUNNING** | — | TX-09:user.cancel | — | — | — | T2:core.approval_required | T6:core.output_ready | T4:core.failure | — |
| **UI_S5_AWAIT_APPROVAL** | — | — | — | — | T3:user.approve | — | — | TX-10:user.reject / TX-11:approval.timeout | — |
| **UI_S6_PRESENTING** | — | TX-12:user.newInput | — | — | — | — | — | TX-16:mismatch | TX-13:user.archive |
| **UI_S7_RECOVERY** | — | TX-14:user.abort / penalty≤0 | — | — | T5:user.retry(axis) | — | — | — | — |
| **UI_S8_ARCHIVED** | TX-15:session.restart | — | — | — | — | — | — | — | — |

**불변식 검증**:
- 모든 엣지는 `Transition` 스키마를 만족한다.
- 금지 셀(—)은 직접 전이가 없다는 의미이며, 필요 시 **중간 상태를 경유**해야 한다 (예: S8→S1은 S0 경유).
- `UI_S0_BOOT`로의 전이는 오직 `TX-15`(S8→S0) 및 앱 초기화(TX-01)만 허용.
- `UI_S2_EDITING`은 Hologram View에서는 미활성 (layout 가드에 의해 차단).
- **TX-16 (메타 리졸버, from any)**: `ui.core.state.mismatch` (persist>500ms, G-MISMATCH-500) 는 9×9 셀 매트릭스와 **직교**하는 from-any 메타 전이로, **모든 상태(S0~S8)** 에서 발동한다. 도달 상태는 `A-SYNC-FORCE` 가 엔진 상태로 수렴시키며 `ERR-SM-010` 을 발행한다 (§3 TX-16, §4.4, §8.4). 상기 S1/S2/S6 셀의 `TX-16:mismatch` 표기는 예시이며 S3/S4/S5/S7/S8 에도 동일 적용된다.
- **TX-16 (메타 리졸버, from any)**: `ui.core.state.mismatch` (persist>500ms, G-MISMATCH-500) 는 9×9 셀 매트릭스와 **직교**하는 from-any 메타 전이로, **모든 상태(S0~S8)** 에서 발동한다. 도달 상태는 `A-SYNC-FORCE` 가 엔진 상태로 수렴시키며 `ERR-SM-010` 을 발행한다 (§3 TX-16, §4.4, §8.4). 상기 S1/S2/S6 셀의 `TX-16:mismatch` 표기는 예시이며 S3/S4/S5/S7/S8 에도 동일 적용된다.

---

## 5. 가드 정의 (Guard Library)

| 가드 ID | 정의 | 출처 |
|---------|------|------|
| G-INPUT-NE | `ctx.input.length > 0` | DEFINED-HERE |
| G-PREFLIGHT-OK | `ctx.preflight.pass === true` | §4.2 T1 |
| G-APPROVAL-REQ | `ctx.approvalRequired === true` | §4.2 T2 |
| G-OUTPUT-READY | `ctx.outputReady === true` | §4.2 T6 |
| G-FAILURE | `ctx.failureCode !== null` | §4.2 T4 |
| G-RETRY-AXIS | `ctx.retryAxis ∈ {evidence, execution, format}` | §4.3 |
| G-DL-OFF | `ctx.decisionLocked === false` (취소 허용) | §4.3 |
| G-APPROVER | `ctx.user.role ∈ approvers` | §4.2 T3 |
| G-COST-OK | `ctx.costEstimateUSD ≤ ctx.budgetUSD` | DEFINED-HERE |
| G-TIMEOUT | `now - ctx.enteredAt > ctx.timeoutMs` | §4.4 |
| G-MISMATCH-500 | `ctx.mismatchDurationMs > 500` | §4.4 |
| G-PENALTY-DEPLETED | `ctx.penalty ≤ 0` | DEFINED-HERE |

---

## 6. 액션 정의 (Action Library)

| 액션 ID | 정의 | 부수 효과 |
|---------|------|-----------|
| A-CORE-EXEC-START | Core 실행 시작 | SSE/WS open |
| A-CORE-EXEC-RESUME | Core 실행 재개 (승인 후) | stream 재개 |
| A-CORE-EXEC-RETRY | 축 기반 재시도 (evidence/execution/format) | retryCount++, penalty×=0.5 |
| A-CORE-EXEC-ABORT | Core 실행 중단 | stream.close, trace.flush |
| A-STREAM-OPEN | 스트리밍 채널 열기 | 06_streaming-canvas 바인딩 |
| A-STREAM-ABORT | 스트리밍 중단 | 버퍼 플러시 |
| A-MODAL-OPEN-APPROVAL | 승인 모달 표시 | 포커스 이동 |
| A-TIMER-START | 승인 타이머 시작 | timeout 이벤트 예약 |
| A-HUD-RENDER | HUD 패널 렌더 (progress/cost/evidence/recovery) | 05_glass-hud-overlay |
| A-OUTPUT-BIND-3POINT | 3-point 출력 바인딩 (LOCK-HM-06) | user_response/evidence/log_report |
| A-TIMELINE-COMMIT | 타임라인에 EventCard 기록 | TimelinePanel 갱신 |
| A-ESCALATION-EMIT | EscalationPayload 발행 | 6-12 로깅 |
| A-PENALTY-APPLY | penalty 감쇠 적용 | `penalty = max(0, p × 0.5)` |
| A-SYNC-FORCE | Core 상태로 UI 강제 동기화 | `ui.core.state.mismatch` 후속 |
| A-SESSION-FREEZE | 세션 불변화 (아카이브) | 편집 차단 |
| A-SESSION-SOFT-RESET | 세션 소프트 리셋 (소프트루프 폴백, TX-14) | `session.soft_reset`, UI_S1_IDLE, store 부분 초기화 |
| A-SESSION-RESTART | 새 세션 초기화 | store.reset, UI_S0_BOOT |

---

## 7. 일관성 검증 (EngineState ↔ PipelineState ↔ UIState)

### 7.1 엣지별 EngineState 변화 (§4.4/§4.5)

| 엣지 | EngineState 전환 |
|------|-----------------|
| T1 (S1→S4) | UIS1IDLE → UIS2PROCESSING → UIS3LOCKED → UIS4RUNNING |
| T2 (S4→S5) | UIS4RUNNING → UIS5AWAITAPPROVAL |
| T3 (S5→S4) | UIS5AWAITAPPROVAL → UIS4RUNNING |
| T4 (S4→S7) | UIS4RUNNING → UIS4RUNNING (복구 흐름 내 유지) |
| T5 (S7→S4) | UIS4RUNNING → UIS4RUNNING (재시도) |
| T6 (S4→S6) | UIS4RUNNING → UIS6PRESENTING |
| TX-13 (S6→S8) | UIS6PRESENTING → (Core 비활성) |

### 7.2 Pipeline ↔ UIState 엣지 동기 (§4.6)

| Pipeline 엣지 | 유발 UI 엣지 |
|---------------|-------------|
| S0→S1→S2→S3→S4 (Core 진행) | UI는 UI_S4_RUNNING 유지 |
| S4→S5_OUTPUT_READY | T6: UI_S4 → UI_S6 |
| S5→S6→S7 (자기검증·메모리) | UI_S6 유지, HUD 진행률 갱신 |
| S7→S8_DONE | TX-13: UI_S6 → UI_S8 (사용자 archive 필요) |

### 7.3 LOCK 교차 검증

| LOCK | 엣지 검증 사항 |
|------|----------------|
| LOCK-HM-03 §4.1 | 9개 노드 이름·번호 매트릭스에 그대로 유지 |
| LOCK-HM-03 §4.2 | T1~T6 트리거 원문 그대로(`전송/실행`, `approval_required=true` 등) |
| LOCK-HM-03 §4.3 | DL 이후 결론 변경 엣지 없음 (UI_S6 → UI_S6 결론 변경 셀 없음) |
| LOCK-HM-04 | T1/TX-07 엣지 액션에 Main LLM 맥락 5개 전달 포함 (UI_S4_RUNNING 진입 경로) |
| LOCK-HM-06 | T6 액션에 `A-OUTPUT-BIND-3POINT` 포함 |
| LOCK-HM-10 | 모든 엣지 액션에 HUD 렌더 포함 여부 확인 |
| R-611-5 | 모든 엣지는 `trigger` 필수(이벤트 기반), 직접 setState 금지 |
| R-T6-3 | 본 매트릭스 변경 시 01/02 폴더 정합성 재검증 |

---

## 8. 전이 시퀀스 예시 (3건+: 정상 / 에러 / 소프트루프)

### 8.1 [정상 경로] T1 → T6 → TX-13

```
UI_S1_IDLE --[T1:user.send | G:G-INPUT-NE,G-PREFLIGHT-OK | A:A-CORE-EXEC-START,A-STREAM-OPEN]--> UI_S4_RUNNING
UI_S4_RUNNING --[T6:core.output_ready | G:G-OUTPUT-READY | A:A-OUTPUT-BIND-3POINT,A-HUD-RENDER,A-TIMELINE-COMMIT]--> UI_S6_PRESENTING
UI_S6_PRESENTING --[TX-13:user.archive | A:A-SESSION-FREEZE]--> UI_S8_ARCHIVED
```

로그(요약):
```json
[
  {"id":"T1", "from":"UI_S1_IDLE","to":"UI_S4_RUNNING","engineState":"UIS4RUNNING"},
  {"id":"T6", "from":"UI_S4_RUNNING","to":"UI_S6_PRESENTING","engineState":"UIS6PRESENTING","pipelineStage":"S5_OUTPUT_READY"},
  {"id":"TX-13","from":"UI_S6_PRESENTING","to":"UI_S8_ARCHIVED"}
]
```

### 8.2 [에러 경로] T1 → T4 → T5 → T6

```
UI_S1 --[T1]--> UI_S4 --[T4:core.failure | G:G-FAILURE | A:A-ESCALATION-EMIT,A-HUD-RENDER:recovery]--> UI_S7
UI_S7 --[T5:user.retry.evidence | G:G-RETRY-AXIS | A:A-CORE-EXEC-RETRY(evidence),A-PENALTY-APPLY]--> UI_S4
UI_S4 --[T6]--> UI_S6
```

EscalationPayload(T4):
```json
{
  "from":"UI_S4_RUNNING","to":"UI_S7_RECOVERY",
  "trigger":"core.failure","errorCode":"ERR-SM-005",
  "reason":"evidence.insufficient","retryCount":0,
  "correlationId":"corr-a1b2","timestamp":1744611202100
}
```

### 8.3 [소프트루프] T2 → TX-10 → T5 → T2 → TX-10 → TX-14

```
UI_S4 --[T2]--> UI_S5 --[TX-10:user.reject | A:A-ESCALATION-EMIT(ERR-SM-007),A-PENALTY-APPLY(0.5)]--> UI_S7
UI_S7 --[T5:user.retry.format]--> UI_S4 --[T2]--> UI_S5 --[TX-10:user.reject | A:A-PENALTY-APPLY(0.25)]--> UI_S7
UI_S7 --[TX-14:penalty≤0 | G:G-PENALTY-DEPLETED | A:A-SESSION-SOFT-RESET,A-ESCALATION-EMIT(ERR-SM-009)]--> UI_S1
```

### 8.4 [Mismatch 경로] TX-16 (보너스)

```
UI_S4 (core: UIS5AWAITAPPROVAL for 620ms) --[TX-16:ui.core.state.mismatch | G:G-MISMATCH-500 | A:A-SYNC-FORCE,A-ESCALATION-EMIT(ERR-SM-010)]--> UI_S5
```
(※ 엄밀히는 `A-SYNC-FORCE`가 UIState를 엔진과 일치시키므로, 최종 도달 상태는 엔진 상태와 동일 — 여기서는 UI_S5로 수렴)

---

## 9. 에러 표 (엣지별)

| 코드 | 엣지 | 트리거 | penalty | 복구 엣지 |
|------|------|--------|---------|-----------|
| ERR-SM-002 | TX-03 | token.expired | 0.0 | UI_S7 → UI_S1 (재로그인) |
| ERR-SM-003 | TX-08 | preflight.recheck.fail | 0.5 | UI_S7 → UI_S4 (T5) or UI_S1 (TX-14) |
| ERR-SM-004 | T4 | tool.timeout | 0.5^r | UI_S7 → UI_S4 (T5 execution axis) |
| ERR-SM-005 | T4 | evidence.insufficient | 0.5^r | UI_S7 → UI_S4 (T5 evidence axis) |
| ERR-SM-006 | T4 | format.violation | 0.5^r | UI_S7 → UI_S4 (T5 format axis) |
| ERR-SM-007 | TX-10 | user.reject | 0.5 | UI_S7 → UI_S4 or UI_S1 |
| ERR-SM-008 | TX-11 | approval.timeout | 0.25 | UI_S7 → UI_S4 or UI_S1 |
| ERR-SM-009 | TX-14 | penalty depleted (soft loop) | 0.0 (reset) | UI_S1 강제 |
| ERR-SM-010 | TX-16 | mismatch > 500ms | — | 자동 동기화 |
| ERR-SM-011 | (차단) | DL 이후 결론 변경 시도 | — | 상태 유지 + HUD 경고 |
| ERR-SM-012 | (차단) | 직접 setState (이벤트 미경유) | — | R-611-5 위반 로그 |

---

## 10. 복구 흐름 + Penalty (엣지 기준)

```
[T4/TX-08/TX-10/TX-11] --> UI_S7_RECOVERY
   │
   ├── [T5 evidence axis]   --> UI_S4  (retryCount++, penalty *= 0.5)
   ├── [T5 execution axis]  --> UI_S4
   ├── [T5 format axis]     --> UI_S4
   └── [TX-14 abort / penalty≤0] --> UI_S1 (강제 폴백)

penalty_next = max(0, penalty_current * 0.5)
soft_loop_detect: (from,to)=(UI_S4,UI_S7) 카운트 ≥ 3 in 10s  ⇒  강제 TX-14
```

---

## 11. 세션 간 인터페이스

| 세션 | 제공 | 수신 |
|------|------|------|
| T1-3 Hook | `useTransition(id)` 훅 시그니처 | — |
| T1-4 Store | Zustand 액션 네임스페이스 `uiStateStore.dispatch(trigger,payload)` | — |
| T1-6 ChatPage | 상태별 분기 셀렉터 `selectByUIState()` | — |
| T2-1 2-tier 라우팅 | T1 엣지 액션에 맥락 5개 포함 | — |
| T2-4 Glass HUD | 엣지별 `A-HUD-RENDER` 타겟 | — |
| T2-5 스트리밍 캔버스 | T1 `A-STREAM-OPEN`, T6 종료, T4 `A-STREAM-ABORT` | — |
| T2-6 I-10 오케스트레이션 | EngineState 반영 계약 | — |

---

## 12. 의존성

| 유형 | 대상 |
|------|------|
| LOCK | LOCK-HM-03 §4.1~§4.6 |
| Sibling | `state_definitions.md` |
| Downstream | T1-3/T1-4/T1-6 |
| Cross-domain | 6-9 (EngineState), 6-12 (로깅), 6-2 (RBAC approver) |

---

## 13. 통합 지점

- **Event Bus**: 모든 엣지는 도트-네임 이벤트(`user.*`, `core.*`, `approval.*`, `ui.*`)로만 발화
- **Zustand Store**: `dispatch(trigger, payload)` → 매트릭스 조회 → 가드 평가 → 액션 실행 → 상태 커밋
- **Guard/Action 라이브러리**: §5/§6 카탈로그를 단일 소스로 유지
- **Logging**: 엣지 통과 시 §1.2 스키마로 6-12 로깅
- **Big-O (전이 엔진)**: 매트릭스 조회 O(1)(해시), 가드 평가 O(g), 액션 실행 O(Σa)

### 13.1 ABC 시그니처

| 컴포넌트 | A | B | C |
|----------|---|---|---|
| Transition Engine | `dispatch(trigger)` | 매트릭스/가드/액션 파이프 | `{from,to,logged}` |
| Guard Evaluator | `evaluate(guardId, ctx)` | 순수 함수 | `boolean` |
| Action Executor | `execute(actionId, ctx)` | 부수효과 허용 | `Promise<void>` |

---

## 14. Phase 2 테스트 (10건+)

| # | 테스트 ID | 시나리오 | 입력 | 기대 | 검증 |
|---|-----------|----------|------|------|------|
| T01 | SM-TRANS-001 | T1 정상 | UI_S1 + user.send (preflight.pass=true) | UI_S4, A-CORE-EXEC-START 1회 | 매트릭스 §4 / §2 |
| T02 | SM-TRANS-002 | T2 정상 | UI_S4 + approval_required=true | UI_S5, 모달 표시 | §2 T2 |
| T03 | SM-TRANS-003 | T3 승인 | UI_S5 + user.approve | UI_S4 재개, timer.stop | §2 T3 |
| T04 | SM-TRANS-004 | T4 실패 | UI_S4 + failureCode="tool.timeout" | UI_S7, escalation emit(ERR-SM-004) | §2 T4 |
| T05 | SM-TRANS-005 | T5 재시도 | UI_S7 + retryAxis="evidence" | UI_S4, penalty *= 0.5 | §2 T5 |
| T06 | SM-TRANS-006 | T6 출력 | UI_S4 + outputReady=true | UI_S6, 3-point 바인딩 | §2 T6 / LOCK-HM-06 |
| T07 | SM-TRANS-007 | TX-10 거부 | UI_S5 + user.reject | UI_S7, penalty=0.5, ERR-SM-007 | §3 |
| T08 | SM-TRANS-008 | TX-11 승인 타임아웃 | UI_S5 + elapsed>timeout | UI_S7, penalty=0.25, ERR-SM-008 | §3 |
| T09 | SM-TRANS-009 | TX-13 아카이브 | UI_S6 + user.archive | UI_S8, 편집 차단 | §3 |
| T10 | SM-TRANS-010 | TX-14 소프트루프 abort | UI_S7 + penalty=0 | UI_S1, ERR-SM-009 | §3 / §10 |
| T11 | SM-TRANS-011 | TX-15 재시작 | UI_S8 + session.restart | UI_S0, store.reset | §3 |
| T12 | SM-TRANS-012 | TX-16 mismatch | UI_S4, Core=UIS5AWAITAPPROVAL 620ms | UI_S5(sync), ERR-SM-010 | §3 / §4.4 |
| T13 | SM-TRANS-013 | 금지 셀 (UI_S1→UI_S6 직접) | user.send + outputReady=true 동시 | 거부: 중간상태 경유 강제 | §4 매트릭스 |
| T14 | SM-TRANS-014 | R-611-5: 직접 setState | `store.set({current:UI_S6})` | 차단, ERR-SM-012 | R-611-5 |
| T15 | SM-TRANS-015 | §4.3 DL 제약 | UI_S6 + user.changeConclusion | 차단, ERR-SM-011, 상태 유지 | §4.3 |
| T16 | SM-TRANS-016 | T1 guard 미충족 | UI_S1 + user.send (input="") | 엣지 거부, 상태 유지 | G-INPUT-NE |
| T17 | SM-TRANS-017 | T4→T5→T4→T5→T4→TX-14 연쇄 | penalty 감쇠 | (0.5, 0.25, 0.125→0) → UI_S1 | §10 |
| T18 | SM-TRANS-018 | TX-09 취소 (DL 이후) | UI_S4 + user.cancel + decisionLocked=true | 차단, 상태 유지 | G-DL-OFF |

---

## 15. ISS-05 해소 체크리스트

- [x] 9×9 매트릭스 전수 작성 (§4) — 모든 셀 기재 또는 `—` 명시
- [x] §4.2 6건 원문 트리거 보존 (§2 T1~T6)
- [x] 확장 전이 16건 (§3 TX-01~TX-16) — 초기화/아카이브/복구/취소/편집/mismatch 전 경로
- [x] 가드 라이브러리 12종 (§5)
- [x] 액션 라이브러리 17종 (§6)
- [x] EngineState 매핑 (§7.1) — §4.4/§4.5 준수
- [x] Pipeline 매핑 (§7.2) — §4.6 준수
- [x] LOCK 교차 검증 (§7.3) — HM-03/04/06/10, R-611-5, R-T6-3
- [x] 전이 시퀀스 예시 4건 (§8: 정상/에러/소프트루프/mismatch)
- [x] 에러 표 11건 (§9)
- [x] 복구 흐름 + penalty 공식 (§10)
- [x] 세션 간 인터페이스 (§11)
- [x] 의존성 (§12), 통합 (§13), ABC 시그니처 (§13.1)
- [x] Phase 2 테스트 18건 (§14)
- [x] 출처 및 LOCK 메타데이터 상단 기재 (§0)

> **ISS-05 상태**: 본 문서(매트릭스) + `state_definitions.md`(노드 정의) 쌍으로 **해소 완료** (Phase 1 T1-5).

---

## 16. 변경 이력

| 일자 | 세션 | 변경 | 작성자 |
|------|------|------|--------|
| 2026-04-14 | T1-5 step1 | 최초 작성 (9×9 매트릭스, 확장 전이 16건, ISS-05 해소) | subagent |
| 2026-04-14 | T1-5 step2 | 재검증: §7.3 LOCK-HM-04 "T1/T7" → "T1/TX-07" 교정, §6 `A-SESSION-SOFT-RESET` 액션 추가(17종), §15 카운트 동기화, §3 TX-16 대상 상태 정밀화(엔진 상태로 수렴) | subagent |
