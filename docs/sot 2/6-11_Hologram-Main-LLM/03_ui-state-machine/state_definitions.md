# state_definitions.md — 9-State UI State Machine 정의

> **도메인**: 6-11_Hologram-Main-LLM / 03_ui-state-machine
> **출처**: D2.0-08 §4 (L335-352, LOCK-HM-03 정본), Part2 §6.1.6 (L4622-4642), 계획서 §A.5
> **LOCK**: LOCK-HM-03 (9-State UI State Machine)
> **정본 소유**: 6-11 DEFINED-HERE (상태 이름·번호는 D2.0-08 LOCK)
> **Phase 배정**: Phase 1 T1-5
> **작성일**: 2026-04-14
> **세션**: TASK_ID=6-11_T1-5_step1_2026-04-14T07-05-00

---

## 0. 메타데이터 / 교차 참조

### 0.1 LOCK 메타데이터

| 필드 | 값 |
|------|----|
| LOCK ID | **LOCK-HM-03** |
| 항목명 | 9-State UI State Machine |
| 정본 출처 | `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §4.1 (L335-344) |
| 상태 수량 | 9개 (S0~S8, 추가/축소 금지) |
| 정규명 | UI_S0_BOOT, UI_S1_IDLE, UI_S2_EDITING, UI_S3_READY, UI_S4_RUNNING, UI_S5_AWAIT_APPROVAL, UI_S6_PRESENTING, UI_S7_RECOVERY, UI_S8_ARCHIVED |
| 연관 규칙 | R-611-5 (이벤트 기반 전이만 허용), R-T6-3 (변경 시 레이아웃 정합성 검증) |

### 0.2 교차 참조 블록

| 참조 | 대상 | 역할 |
|------|------|------|
| D2.0-08 §4.1 (L335-344) | 9개 상태 정규명·설명 | LOCK 정본 |
| D2.0-08 §4.2 (L346-352) | 기본 전환 규칙 6건 | LOCK (transition_matrix.md 근거) |
| D2.0-08 §4.3 | Decision Lock UI 제약 | 가드 조건 |
| D2.0-08 §4.4 | 런타임 6-State (I-10) | 양방향 매핑 |
| D2.0-08 §4.5 | 9-State ↔ 6-State 매핑 | 일관성 검증 |
| D2.0-08 §4.6 | Pipeline S0~S8 ↔ UI 상태 매핑 | EngineState ↔ UIState 검증 |
| Part2 §6.1.6 (L4622-4642) | 9-state 주요 전이 | 글자 대조 일치 |
| `03_ui-state-machine/_index.md` | 폴더 인덱스·범위 | 상위 인덱스 |
| `03_ui-state-machine/transition_matrix.md` | 전이 매트릭스 | 쌍방 문서 |
| `01_hologram-view-layout/` | Hologram 3-Pane (LOCK-HM-01) | UI 렌더링 계층 |
| `02_component-architecture/` | 44 컴포넌트 / 8 Hook / 7 Store | 상태 바인딩 대상 |
| `07_orchestration-layer/` | I-10 UI↔Core 오케스트레이션 | 6-State 연동 |
| 6-9 Brain-Adapter-HAL | Core State (EngineState) | 1:1 반영 계약 |
| 6-12 Event-Logging | `ui.core.state.mismatch` 이벤트 | 불일치 탐지 |

---

## 1. 공통 자료 구조 선정의 (Common Data Structures)

> 본 문서와 `transition_matrix.md`가 공통으로 참조하는 구조. TypeScript 기준.

### 1.1 `UIState` Enum (정본)

```typescript
// 정본: D2.0-08 §4.1 — LOCK-HM-03
export enum UIState {
  UI_S0_BOOT            = "UI_S0_BOOT",
  UI_S1_IDLE            = "UI_S1_IDLE",
  UI_S2_EDITING         = "UI_S2_EDITING",
  UI_S3_READY           = "UI_S3_READY",
  UI_S4_RUNNING         = "UI_S4_RUNNING",
  UI_S5_AWAIT_APPROVAL  = "UI_S5_AWAIT_APPROVAL",
  UI_S6_PRESENTING      = "UI_S6_PRESENTING",
  UI_S7_RECOVERY        = "UI_S7_RECOVERY",
  UI_S8_ARCHIVED        = "UI_S8_ARCHIVED",
}
```

### 1.2 `StateContext` 인터페이스

```typescript
export interface StateContext {
  current: UIState;                    // 현재 상태
  previous: UIState | null;            // 직전 상태 (복구용)
  enteredAt: number;                   // Unix ms (엔트리 시각)
  tickCount: number;                   // 상태 내 tick 수 (소프트루프 탐지)
  sessionId: string;                   // 세션 식별자
  approvalRequired?: boolean;          // §4.2 T2 가드
  outputReady?: boolean;               // §4.2 T6 가드
  failureCode?: string | null;         // §4.2 T4 페이로드
  costEstimateUSD?: number;            // §4.3 비용 알림 가드
  decisionLocked?: boolean;            // §4.3 DL 제약
  engineState?: EngineState | null;    // 6-9 Core 상태 (1:1 반영)
  pipelineStage?: PipelineStage | null;// §4.6 Pipeline S0~S8
}
```

### 1.3 `EngineState` / `PipelineStage` (외부 참조)

```typescript
// 6-9 정본: Core Engine 6-State
export type EngineState =
  | "UIS1IDLE" | "UIS2PROCESSING" | "UIS3LOCKED"
  | "UIS4RUNNING" | "UIS5AWAITAPPROVAL" | "UIS6PRESENTING";

// §4.6 정본: Pipeline Stage
export type PipelineStage =
  | "S0_RECEIVED" | "S1_INTENT_PARSED" | "S2_EVIDENCE_READY"
  | "S3_DECISION_LOCKED" | "S4_EXECUTING" | "S5_OUTPUT_READY"
  | "S6_SELF_CHECKED" | "S7_MEMORY_COMMITTED" | "S8_DONE";
```

### 1.4 `EscalationPayload` (에러·복구 공통)

```typescript
export interface EscalationPayload {
  from: UIState;
  to: UIState;
  trigger: string;                 // 이벤트 ID
  reason: string;                  // 실패·거부·타임아웃 상세
  errorCode?: string;              // ERR-SM-xxx
  penalty?: number;                // 소프트루프 penalty (0~1)
  retryCount?: number;
  correlationId: string;           // 6-12 로깅 correlation
  timestamp: number;
}
```

---

## 2. 9개 상태 정의 (진입/활성/종료 조건)

> **정본 준수**: 상태 번호·정규명은 D2.0-08 §4.1 원문 그대로. 재정의 금지.

### 2.1 UI_S0_BOOT — 앱/세션 초기화

| 항목 | 내용 |
|------|------|
| **정본 설명** | 앱/세션 초기화 (D2.0-08 §4.1 원문) |
| **진입 조건** | 앱 최초 로드 / 세션 재시작 / UI_S8_ARCHIVED → 재시작 요청 |
| **활성 조건** | Zustand Store 하이드레이션 미완료 OR 토큰 검증 미완료 OR 초기 라우팅 미결정 |
| **활성 액션** | `store.hydrate()`, `auth.verifyToken()`, `layout.resolveInitial()`, Glass HUD 비활성 |
| **종료 조건 (→ UI_S1_IDLE)** | 하이드레이션 완료 ∧ 토큰 유효 ∧ Layout 확정 |
| **종료 조건 (실패)** | 토큰 만료 → UI_S7_RECOVERY (재로그인 안내) |
| **허용 사용자 액션** | 없음 (로딩 스피너만) |
| **EngineState 매핑** | — (Core 미연결) |
| **PipelineStage 매핑** | — |
| **Big-O** | O(1) 진입, O(k) 하이드레이션 (k = 저장 키 수) |
| **ABC 시그니처** | `A`=init, `B`=boot, `C`=UI_S0_BOOT |

### 2.2 UI_S1_IDLE — 입력 대기

| 항목 | 내용 |
|------|------|
| **정본 설명** | 입력 대기 (D2.0-08 §4.1 원문) |
| **진입 조건** | UI_S0 로드 완료 / UI_S6 응답 완료 후 복귀 / UI_S7 복구 후 복귀 |
| **활성 조건** | 사용자 입력 대기 상태, StreamCanvas idle |
| **활성 액션** | 입력창 포커스, HUD 최소화, 타임라인 최신 이벤트 표시 |
| **종료 조건 (→ UI_S2_EDITING)** | Builder 편집 시작 (Hologram 외 경로) |
| **종료 조건 (→ UI_S4_RUNNING)** | 메시지 전송/실행 (§4.2 T1) |
| **허용 사용자 액션** | 입력, 히스토리 탐색, 설정 |
| **EngineState 매핑** | UIS1IDLE |
| **PipelineStage 매핑** | — |
| **Big-O** | O(1) |
| **ABC 시그니처** | `A`=idle, `B`=user_wait, `C`=UI_S1_IDLE |

### 2.3 UI_S2_EDITING — Builder 편집 중

| 항목 | 내용 |
|------|------|
| **정본 설명** | Builder 편집 중 (D2.0-08 §4.1 원문) |
| **진입 조건** | Builder 편집 시작 (Hologram View에서는 일반적으로 비활성, 1-Layout 전환 시 활성) |
| **활성 조건** | Builder 편집 모드 활성, Core 미호출 |
| **활성 액션** | 편집 UI 렌더링, 자동 저장(debounce 500ms), 사전 점검 미수행 |
| **종료 조건 (→ UI_S3_READY)** | 사전 점검 통과 (`preflight.pass = true`) |
| **종료 조건 (→ UI_S1_IDLE)** | 편집 취소 |
| **허용 사용자 액션** | 편집, 취소, 저장 |
| **EngineState 매핑** | UIS2PROCESSING (편집 중 Core 미호출 시 UIS1 유지) |
| **PipelineStage 매핑** | — |
| **Big-O** | O(n) 편집 (n = 입력 길이) |
| **ABC 시그니처** | `A`=edit, `B`=builder, `C`=UI_S2_EDITING |

### 2.4 UI_S3_READY — 실행 가능 (사전 점검 통과)

| 항목 | 내용 |
|------|------|
| **정본 설명** | 실행 가능(사전 점검 통과) (D2.0-08 §4.1 원문) |
| **진입 조건** | UI_S2 사전 점검 통과 / 직접 전송 경로에서 preflight 통과 |
| **활성 조건** | 실행 버튼 활성화, 미실행 상태 |
| **활성 액션** | 실행 버튼 하이라이트, 비용 추정치 표시, HUD에 preflight 요약 |
| **종료 조건 (→ UI_S4_RUNNING)** | 실행 시작 (§4.2 T1) |
| **종료 조건 (→ UI_S7_RECOVERY)** | preflight 재검증 실패 |
| **허용 사용자 액션** | 실행, 취소, 편집 복귀 |
| **EngineState 매핑** | UIS2PROCESSING (사전 점검 = Core 처리 시작) |
| **PipelineStage 매핑** | S0_RECEIVED ~ S2_EVIDENCE_READY 진입 직전 |
| **Big-O** | O(1) |
| **ABC 시그니처** | `A`=ready, `B`=preflight_ok, `C`=UI_S3_READY |

### 2.5 UI_S4_RUNNING — 실행 중 (trace 활성)

| 항목 | 내용 |
|------|------|
| **정본 설명** | 실행 중(trace 활성) (D2.0-08 §4.1 원문) |
| **진입 조건** | UI_S1/UI_S3 실행 시작 (T1) / UI_S5 승인 (T3) / UI_S7 재시도 (T5) |
| **활성 조건** | Core 실행 중, SSE/WS 스트림 수신, Decision Lock 전후 분기 |
| **활성 액션** | trace 패널 활성, StreamCanvas 토큰 렌더링, HUD 진행률·비용 갱신, 취소 버튼 노출 |
| **종료 조건 (→ UI_S5_AWAIT_APPROVAL)** | `approval_required = true` (§4.2 T2) |
| **종료 조건 (→ UI_S6_PRESENTING)** | `output_ready = true` (§4.2 T6) |
| **종료 조건 (→ UI_S7_RECOVERY)** | failure(도구/근거/포맷) (§4.2 T4) |
| **허용 사용자 액션** | 취소(Cancel), DL 이후 수정 불가 |
| **EngineState 매핑** | UIS3LOCKED → UIS4RUNNING (DL 전후) |
| **PipelineStage 매핑** | S0_RECEIVED, S1_INTENT_PARSED, S2_EVIDENCE_READY, S3_DECISION_LOCKED, S4_EXECUTING |
| **Big-O** | O(t) 스트리밍 (t = 토큰 수) |
| **ABC 시그니처** | `A`=run, `B`=core_exec, `C`=UI_S4_RUNNING |

### 2.6 UI_S5_AWAIT_APPROVAL — 승인 대기 (HOLD)

| 항목 | 내용 |
|------|------|
| **정본 설명** | 승인 대기(HOLD) (D2.0-08 §4.1 원문) |
| **진입 조건** | UI_S4에서 `approval_required=true` (비용 초과·위험 작업·RBAC 상향) |
| **활성 조건** | Core HOLD, 세션 복원 시 반드시 UIS5 복원 |
| **활성 액션** | 승인 모달 표시, HUD에 사유·비용·영향 범위 표시, 타이머 시작 |
| **종료 조건 (→ UI_S4_RUNNING)** | 승인(Approve) (§4.2 T3) |
| **종료 조건 (→ UI_S7_RECOVERY)** | 거부 / 타임아웃 |
| **허용 사용자 액션** | Approve / Reject |
| **EngineState 매핑** | UIS5AWAITAPPROVAL (1:1) |
| **PipelineStage 매핑** | S4_EXECUTING 내 HOLD |
| **Big-O** | O(1) 대기, 타이머 경과 시 O(1) |
| **ABC 시그니처** | `A`=hold, `B`=approval, `C`=UI_S5_AWAIT_APPROVAL |

### 2.7 UI_S6_PRESENTING — 결과 표시

| 항목 | 내용 |
|------|------|
| **정본 설명** | 결과 표시(출력/근거/컴플라이언스) (D2.0-08 §4.1 원문) |
| **진입 조건** | UI_S4에서 `output_ready=true` (§4.2 T6) |
| **활성 조건** | 3-point 출력 바인딩 완료 (user_response / evidence_summary / log_report) |
| **활성 액션** | StreamCanvas 최종 렌더, HUD EvidencePanel·LogDetail, TimelinePanel EventCard, DL 이후 포맷·레이아웃만 갱신 |
| **종료 조건 (→ UI_S1_IDLE)** | 새 입력 시작 |
| **종료 조건 (→ UI_S8_ARCHIVED)** | 세션 아카이브 |
| **허용 사용자 액션** | 재생성, 저장, 피드백, 공유 ("결론 변경" UI 금지 — §4.3) |
| **EngineState 매핑** | UIS6PRESENTING (1:1) |
| **PipelineStage 매핑** | S5_OUTPUT_READY, S6_SELF_CHECKED, S7_MEMORY_COMMITTED |
| **Big-O** | O(n) 렌더 (n = 최종 토큰 수) |
| **ABC 시그니처** | `A`=present, `B`=output_bind, `C`=UI_S6_PRESENTING |

### 2.8 UI_S7_RECOVERY — 실패/폴백/재시도 안내

| 항목 | 내용 |
|------|------|
| **정본 설명** | 실패/폴백/재시도 안내 (D2.0-08 §4.1 원문) |
| **진입 조건** | UI_S3 preflight 실패 / UI_S4 failure (T4) / UI_S5 거부·타임아웃 |
| **활성 조건** | 실패 이유·대안 제시, 재시도 축 "근거/실행/포맷"만 허용 (§4.3) |
| **활성 액션** | RecoveryPanel 렌더, EscalationPayload 로깅(6-12), penalty 계산 (소프트루프) |
| **종료 조건 (→ UI_S4_RUNNING)** | 재시도/대안 선택 (§4.2 T5) |
| **종료 조건 (→ UI_S1_IDLE)** | 복구 포기 / 사용자 취소 |
| **허용 사용자 액션** | 재시도(근거/실행/포맷), 포기, 로그 보기 |
| **EngineState 매핑** | UIS4RUNNING (재시도/폴백 진행 중) |
| **PipelineStage 매핑** | 실패 시점의 Stage 유지 |
| **Big-O** | O(r) 재시도 (r = 재시도 수, penalty ≥ 2^r 감쇠) |
| **ABC 시그니처** | `A`=recover, `B`=fallback, `C`=UI_S7_RECOVERY |

### 2.9 UI_S8_ARCHIVED — 아카이브 (리뷰)

| 항목 | 내용 |
|------|------|
| **정본 설명** | 아카이브(리뷰) (D2.0-08 §4.1 원문) |
| **진입 조건** | UI_S6에서 세션 아카이브 선택 |
| **활성 조건** | Core 비활성, 읽기 전용 리뷰 모드 |
| **활성 액션** | 아카이브 뷰 렌더, 편집 UI 차단, 타임라인 고정 |
| **종료 조건 (→ UI_S0_BOOT)** | 세션 재시작 요청 |
| **허용 사용자 액션** | 리뷰, 내보내기, 재시작 |
| **EngineState 매핑** | — (Core 비활성) |
| **PipelineStage 매핑** | S8_DONE |
| **Big-O** | O(1) |
| **ABC 시그니처** | `A`=archive, `B`=review, `C`=UI_S8_ARCHIVED |

---

## 3. 일관성 검증 (EngineState ↔ PipelineState ↔ UIState)

### 3.1 9-State ↔ 6-State 매핑 (§4.5 LOCK)

| UI_S# | EngineState | 비고 |
|-------|------------|------|
| UI_S0_BOOT | — | Core 미연결 |
| UI_S1_IDLE | UIS1IDLE | 1:1 |
| UI_S2_EDITING | UIS2PROCESSING (또는 UIS1) | Builder 전용 |
| UI_S3_READY | UIS2PROCESSING | 사전 점검 = Core 처리 시작 |
| UI_S4_RUNNING | UIS3LOCKED → UIS4RUNNING | DL 전후 분기 |
| UI_S5_AWAIT_APPROVAL | UIS5AWAITAPPROVAL | 1:1 |
| UI_S6_PRESENTING | UIS6PRESENTING | 1:1 |
| UI_S7_RECOVERY | UIS4RUNNING | 재시도/폴백 흐름 내 |
| UI_S8_ARCHIVED | — | Core 비활성 |

### 3.2 Pipeline S0~S8 ↔ UI 상태 (§4.6 LOCK, D8-M11)

| Pipeline | UI 상태 | 검증 불변식 |
|----------|---------|-------------|
| S0_RECEIVED ~ S4_EXECUTING | UI_S4_RUNNING | Pipeline ≤ S4 → UI는 S4 고정 (HOLD·실패 제외) |
| S5_OUTPUT_READY ~ S7_MEMORY_COMMITTED | UI_S6_PRESENTING | output_ready 이후 UI_S6 |
| S8_DONE | UI_S8_ARCHIVED | DONE = 아카이브 |

### 3.3 불일치 감지

- 지연 허용 최대 500ms (§4.4)
- 500ms 초과 시 `ui.core.state.mismatch` 이벤트 발행 (6-12 Event-Logging 계약)
- 자동 동기화: Core 상태를 정본으로 UI 강제 동기화

### 3.4 LOCK 교차 검증

| LOCK | 본 문서 준수 사항 |
|------|-------------------|
| LOCK-HM-03 | 상태 9개·정규명 원문 유지, 번호 재정의 금지 |
| LOCK-HM-04 (2-tier 라우팅) | UI_S4_RUNNING 진입 시 Main LLM 맥락 5개 전달 |
| LOCK-HM-06 (3-point 출력) | UI_S6_PRESENTING 바인딩 시 user_response/evidence_summary/log_report |
| LOCK-HM-10 (Glass HUD) | 상태별 HUD 가시성 규칙 (S0/S8 최소, S4/S5 최대) |
| R-611-5 | 모든 전이는 이벤트 기반, 직접 setState 금지 |
| R-T6-3 | 본 문서 변경 시 01_hologram-view-layout 정합성 재검증 필요 |

---

## 4. 전이 시퀀스 예시 (3건+: 정상 / 에러 / 소프트루프)

### 4.1 [정상 경로] BOOT → IDLE → RUNNING → PRESENTING → ARCHIVED

```json
[
  {"t":0,   "from":null,             "to":"UI_S0_BOOT",           "trigger":"app.load"},
  {"t":220, "from":"UI_S0_BOOT",     "to":"UI_S1_IDLE",           "trigger":"hydrate.complete"},
  {"t":1800,"from":"UI_S1_IDLE",     "to":"UI_S4_RUNNING",        "trigger":"user.send",        "ctx":{"approvalRequired":false}},
  {"t":4200,"from":"UI_S4_RUNNING",  "to":"UI_S6_PRESENTING",     "trigger":"core.output_ready","ctx":{"outputReady":true}},
  {"t":9800,"from":"UI_S6_PRESENTING","to":"UI_S8_ARCHIVED",      "trigger":"user.archive"}
]
```

### 4.2 [에러 경로] RUNNING → RECOVERY → RUNNING → PRESENTING

```json
[
  {"t":0,   "from":"UI_S1_IDLE",     "to":"UI_S4_RUNNING",        "trigger":"user.send"},
  {"t":2100,"from":"UI_S4_RUNNING",  "to":"UI_S7_RECOVERY",
   "trigger":"core.failure",
   "escalation":{
     "from":"UI_S4_RUNNING","to":"UI_S7_RECOVERY",
     "trigger":"core.failure","reason":"tool.timeout",
     "errorCode":"ERR-SM-004","retryCount":0,
     "correlationId":"corr-7a3f","timestamp":1744611202100
   }},
  {"t":4500,"from":"UI_S7_RECOVERY", "to":"UI_S4_RUNNING",        "trigger":"user.retry.evidence","ctx":{"retryAxis":"evidence"}},
  {"t":7300,"from":"UI_S4_RUNNING",  "to":"UI_S6_PRESENTING",     "trigger":"core.output_ready"}
]
```

### 4.3 [소프트루프] RUNNING → AWAIT_APPROVAL → (거부) → RECOVERY → (반복 2회) → IDLE

```json
[
  {"t":0,   "from":"UI_S1_IDLE",     "to":"UI_S4_RUNNING",        "trigger":"user.send"},
  {"t":1500,"from":"UI_S4_RUNNING",  "to":"UI_S5_AWAIT_APPROVAL", "trigger":"core.approval_required","ctx":{"costEstimateUSD":2.8}},
  {"t":8500,"from":"UI_S5_AWAIT_APPROVAL","to":"UI_S7_RECOVERY",  "trigger":"user.reject",
   "escalation":{"errorCode":"ERR-SM-007","reason":"user.reject","penalty":0.5,"retryCount":1,"correlationId":"corr-9b1c"}},
  {"t":12000,"from":"UI_S7_RECOVERY","to":"UI_S4_RUNNING",        "trigger":"user.retry.format"},
  {"t":13500,"from":"UI_S4_RUNNING", "to":"UI_S5_AWAIT_APPROVAL", "trigger":"core.approval_required"},
  {"t":20000,"from":"UI_S5_AWAIT_APPROVAL","to":"UI_S7_RECOVERY", "trigger":"user.reject",
   "escalation":{"errorCode":"ERR-SM-007","penalty":0.25,"retryCount":2,"correlationId":"corr-9b1c"}},
  {"t":23000,"from":"UI_S7_RECOVERY","to":"UI_S1_IDLE",           "trigger":"user.abort",
   "escalation":{"errorCode":"ERR-SM-009","reason":"soft_loop.abort","penalty":0.0,"retryCount":2}}
]
```

**소프트루프 탐지·penalty 규칙**:
- 동일 `(from→to)` 쌍이 10초 내 3회 이상 → soft loop 탐지
- `penalty = 0.5^retryCount` (정본 — 에러표 ERR-SM-004/005/006 및 §6 흐름과 일치), 임계 이하에서 강제 UI_S1_IDLE 폴백 (§6 게이트)

---

## 5. 에러 표 (Error Codes)

| 코드 | 상태 | 의미 | 복구 흐름 | penalty |
|------|------|------|-----------|---------|
| ERR-SM-001 | UI_S0_BOOT | 하이드레이션 실패 | → UI_S7 (재로그인 안내) | 0.0 (초기) |
| ERR-SM-002 | UI_S0_BOOT | 토큰 만료 | → UI_S7 | 0.0 |
| ERR-SM-003 | UI_S3_READY | preflight 실패 | → UI_S7 | 0.5 |
| ERR-SM-004 | UI_S4_RUNNING | 도구 타임아웃 | → UI_S7 (재시도 실행 축) | 0.5^r |
| ERR-SM-005 | UI_S4_RUNNING | 근거 부족 | → UI_S7 (재시도 근거 축) | 0.5^r |
| ERR-SM-006 | UI_S4_RUNNING | 포맷 위반 | → UI_S7 (재시도 포맷 축) | 0.5^r |
| ERR-SM-007 | UI_S5_AWAIT_APPROVAL | 승인 거부 | → UI_S7 | 0.5 |
| ERR-SM-008 | UI_S5_AWAIT_APPROVAL | 승인 타임아웃 | → UI_S7 | 0.25 |
| ERR-SM-009 | UI_S7_RECOVERY | 소프트루프 임계 초과 | → UI_S1 강제 폴백 | 0.0 |
| ERR-SM-010 | any | Core ↔ UI 상태 불일치 500ms+ | 자동 동기화 + `ui.core.state.mismatch` | — |
| ERR-SM-011 | UI_S4/S6 | Decision Lock 이후 결론 변경 시도 | 차단 + 경고 HUD | — |
| ERR-SM-012 | any | 직접 상태 변경 시도 (R-611-5 위반) | 차단 + 에러 로그 | — |

---

## 6. 복구 흐름 + Penalty

```
UI_S3 preflight 실패 ──► UI_S7 (penalty=0.5) ──► 재시도 축 선택
                                                    ├── evidence 재수집 ──► UI_S4
                                                    ├── execution 재실행 ──► UI_S4
                                                    └── format 재포맷 ──► UI_S4
                                                    └── abort ──► UI_S1

UI_S4 failure ──► UI_S7 (penalty=0.5^retryCount)
                    └── retryCount ≥ 3 AND penalty ≤ 0.125 ──► UI_S1 강제 폴백 (ERR-SM-009)

UI_S5 reject/timeout ──► UI_S7 ──► 재시도 or UI_S1

Decision Lock 이후 결론 변경 요청 ──► 차단 (ERR-SM-011) ──► HUD 경고 표시, 상태 유지
```

---

## 7. 세션 간 인터페이스 (T1-5 ↔ 타 세션)

| 타 세션 | 인터페이스 | 방향 |
|---------|-----------|------|
| T1-2 컴포넌트 카탈로그 | 각 상태별 허용 컴포넌트 가시성 규칙 | T1-5 → T1-2 참조 |
| T1-3 Hook | `useUIState`, `useStateTransition` Hook 시그니처 | T1-5 → T1-3 |
| T1-4 Store | Zustand `uiStateStore` 스키마 (StateContext) | T1-5 → T1-4 |
| T1-6 ChatPage 통합 | 상태별 ChatPage 렌더 분기 | T1-5 → T1-6 |
| T2-1 2-tier 라우팅 | UI_S4 진입 시 맥락 전달 hook | T1-5 ← T2-1 |
| T2-6 I-10 오케스트레이션 | EngineState ↔ UIState 매핑 계약 | T1-5 ↔ T2-6 |

---

## 8. 의존성

| 유형 | 대상 | 내용 |
|------|------|------|
| Upstream LOCK | LOCK-HM-03 (D2.0-08 §4.1) | 상태 이름·수량 LOCK |
| Upstream LOCK | LOCK-HM-03 (D2.0-08 §4.2) | 6건 기본 전환 |
| Sibling | `transition_matrix.md` | 전이 매트릭스 (쌍방 참조) |
| Downstream | T1-3 Hook / T1-4 Store | `StateContext` 구조 |
| Cross-domain | 6-9 Brain-Adapter-HAL | EngineState 1:1 반영 |
| Cross-domain | 6-12 Event-Logging | `ui.core.state.mismatch`, escalation 로깅 |

---

## 9. 통합 지점 (Integration)

- **Zustand Store**: `uiStateStore.current`은 본 문서의 `UIState` enum만 허용
- **Hook**: `useUIState()` 반환값은 `StateContext` 인터페이스 준수
- **Event Bus**: 상태 전이는 반드시 이벤트 발행 (R-611-5)
- **Logging**: 전이마다 중첩 JSON 구조 로그 (correlationId, from, to, trigger, duration_ms, engineState, pipelineStage)
- **HUD**: 상태 변경 시 `GlassHUDData.stateIndicator` 갱신

### 9.1 중첩 JSON 로깅 스키마

```json
{
  "event": "ui.state.transition",
  "correlationId": "corr-7a3f",
  "transition": {
    "from": "UI_S4_RUNNING",
    "to":   "UI_S6_PRESENTING",
    "trigger": "core.output_ready",
    "duration_ms": 2400
  },
  "context": {
    "engineState":   "UIS6PRESENTING",
    "pipelineStage": "S5_OUTPUT_READY",
    "decisionLocked": true,
    "costEstimateUSD": 0.42
  },
  "guards": { "outputReady": true, "approvalRequired": false }
}
```

---

## 10. Phase 2 테스트 (10건+)

| # | 테스트 ID | 시나리오 | 기대 | 검증 LOCK/규칙 |
|---|-----------|----------|------|---------------|
| T01 | SM-STATE-001 | UI_S0_BOOT 하이드레이션 완료 후 UI_S1_IDLE 전이 | 전이 성공 | LOCK-HM-03 |
| T02 | SM-STATE-002 | UI_S1_IDLE에서 user.send 시 UI_S4_RUNNING 전이 (T1) | 전이 성공, 맥락 5개 전달 | LOCK-HM-04 |
| T03 | SM-STATE-003 | UI_S4에서 approval_required=true → UI_S5 전이 (T2) | 승인 모달 표시, EngineState=UIS5AWAITAPPROVAL | §4.5 |
| T04 | SM-STATE-004 | UI_S5 Approve → UI_S4 전이 (T3), 재개 | 실행 재개, trace 유지 | LOCK-HM-03 |
| T05 | SM-STATE-005 | UI_S4 failure → UI_S7 전이 (T4), EscalationPayload 발행 | errorCode=ERR-SM-004, 6-12 로그 | LOCK-HM-03 §4.2 |
| T06 | SM-STATE-006 | UI_S7에서 재시도 축 "evidence" 선택 → UI_S4 (T5) | retryCount=1, penalty=0.5 | §4.3 |
| T07 | SM-STATE-007 | UI_S6 완료 후 user.archive → UI_S8_ARCHIVED | Core 비활성, 편집 차단 | §4.5 |
| T08 | SM-STATE-008 | UI_S6 에서 "결론 변경" 시도 | 차단 (ERR-SM-011), 상태 유지 | §4.3 |
| T09 | SM-STATE-009 | 직접 setState(UI_S6) 호출 (이벤트 없음) | 차단 (ERR-SM-012) | R-611-5 |
| T10 | SM-STATE-010 | Core=UIS5AWAITAPPROVAL, UI=UIS4RUNNING 500ms+ 지속 | `ui.core.state.mismatch` 이벤트, 자동 동기화 | §4.4 |
| T11 | SM-STATE-011 | UI_S5 승인 대기 중 세션 종료 → 복원 시 UI_S5 복원 | I-10 복원 보장 | §4.4 |
| T12 | SM-STATE-012 | 소프트루프: 10초 내 UI_S4→UI_S7 3회 | penalty=0.125, UI_S1 강제 폴백 (ERR-SM-009) | 본 문서 §6 |
| T13 | SM-STATE-013 | UI_S4 진입 시 Pipeline S3_DECISION_LOCKED → decisionLocked=true | HUD에 DL 표시 | §4.6 |
| T14 | SM-STATE-014 | Pipeline S5_OUTPUT_READY 도달 시 UI_S6 전이 | 3-point 바인딩 완료 | LOCK-HM-06 |
| T15 | SM-STATE-015 | UI_S8에서 restart → UI_S0_BOOT | 새 세션 초기화 | §4.1 |

---

## 11. ISS-05 해소 체크리스트

- [x] 9개 상태 정의 (진입/활성/종료 조건) 전수 기재 — §2.1~§2.9
- [x] D2.0-08 §4.1 원문 상태명 글자 일치 확인 — §2 헤더
- [x] 전이 규칙 6건 (§4.2) `transition_matrix.md`에 전수 반영 (쌍방 문서)
- [x] 가드 조건(approvalRequired/outputReady/decisionLocked 등) 명시 — §1.2 StateContext
- [x] 액션(진입/활성) 명시 — §2 각 상태
- [x] 9-State ↔ 6-State 매핑 (§4.5) — §3.1
- [x] Pipeline ↔ UI 매핑 (§4.6) — §3.2
- [x] 상태 불일치 탐지 및 동기화 (§4.4, 500ms) — §3.3
- [x] Decision Lock UI 제약 (§4.3) — §2.7, §5 ERR-SM-011
- [x] EscalationPayload 정의 — §1.4
- [x] 에러 표 12건 — §5
- [x] Phase 2 테스트 15건 — §10
- [x] LOCK 교차 검증 (HM-03/04/06/10, R-611-5, R-T6-3) — §3.4
- [x] 출처 및 LOCK 메타데이터 상단 기재 — §0

> **ISS-05 상태**: 본 문서 + `transition_matrix.md` 쌍으로 **해소 완료** (Phase 1 T1-5).

---

## 12. 변경 이력

| 일자 | 세션 | 변경 | 작성자 |
|------|------|------|--------|
| 2026-04-14 | T1-5 step1 | 최초 작성 (9개 상태 전수 정의, ISS-05 해소) | subagent |
