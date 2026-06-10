# UI 9-State Machine — L3 상세 명세

> **도메인**: 6-1_UI-UX-System / 03_ui-state-machine
> **산출물 ID**: P1-7
> **버전**: v1.0
> **작성일**: 2026-04-12
> **정본 출처**: D2.0-08 §4.1~§4.6, §5.3~§5.7 / Part2 §6.1.6
> **LOCK 참조**: L1(9-State), L17(전이 지연 500ms), L19(이벤트 네이밍)
> **이슈 해결**: ISS-1(9↔6 양방향 매핑), ISS-7(EventType 57건 → 상태 전이 매핑)
> **거버넌스**: R-61-1(전이 규칙 변경 금지), R-61-5(Decision Lock 후 결론 변경 UI 금지), R-61-6(이벤트 네이밍 L19 준수)

---

## 1. 9-State 정의 (D2.0-08 §4.1 정본)

> LOCK (D2.0-08 §4.1): UI_S0_BOOT, UI_S1_IDLE, UI_S2_EDITING, UI_S3_READY, UI_S4_RUNNING, UI_S5_AWAIT_APPROVAL, UI_S6_PRESENTING, UI_S7_RECOVERY, UI_S8_ARCHIVED (9개)

| 상태 ID | 상태명 | 설명 | 진입 조건 | 사용자 액션 허용 | UI 표시 |
|---------|--------|------|----------|----------------|--------|
| **UI_S0_BOOT** | 앱/세션 초기화 | 앱 시작 또는 세션 복원 진행 | 앱 실행, 세션 복원 트리거 | 대기만 (입력 불가) | 스플래시 화면 + 로딩 스피너 |
| **UI_S1_IDLE** | 입력 대기 | 초기화 완료, 새 입력 가능 | S0 로드 완료, S6 새 입력, S7 복구 | 입력 가능, 히스토리 탐색 | 입력 필드 활성, 커서 깜빡임 |
| **UI_S2_EDITING** | Builder 편집 중 | Builder View에서 편집 진행 | S1에서 Builder 편집 시작 | 편집, 저장, 취소 | Builder 편집 모드 활성, 저장/취소 버튼 |
| **UI_S3_READY** | 실행 가능 | 사전 점검(Policy/Cost) 통과 | S2에서 사전 점검 통과 | 실행, 편집 복귀 | "실행 가능" 배지, 실행 버튼 활성 |
| **UI_S4_RUNNING** | 실행 중 | Core 처리 진행, trace 활성 | S1 전송/실행, S3 실행 시작, S5 승인, S7 재시도 | 취소(Cancel) 가능 | Thinking Block, 진행률 바, 파이프라인 스텝 표시 |
| **UI_S5_AWAIT_APPROVAL** | 승인 대기(HOLD) | `approval_required=true` 수신 | S4에서 승인 필요 이벤트 | 승인(Approve) / 거절(Deny) | 승인 패널 오픈, 진행바 일시정지, 타임아웃 카운트다운 (L18) |
| **UI_S6_PRESENTING** | 결과 표시 | `output_ready` 수신, 3-Part 출력 | S4에서 출력 완료 | 재생성, 저장, 피드백, 새 입력 | 3-Part 출력 렌더링(user_response + evidence_summary + log_report), Self-check 배지 |
| **UI_S7_RECOVERY** | 실패/폴백/재시도 | failure_code 수신 | S3 실패, S4 failure, S5 거부/타임아웃 | 재시도/대안 선택/복구 | 에러 배너 + failure_code 안내 + 재시도/대안 버튼 |
| **UI_S8_ARCHIVED** | 아카이브(리뷰) | 세션 종료 또는 아카이브 요청 | S6에서 아카이브 | 읽기 전용 리뷰 | 읽기 전용 모드, 아카이브 배지 |

---

## 2. 9x9 전이 매트릭스 (D2.0-08 §4.2 정본)

> R-61-1: UI 상태 머신 9-state 전이 규칙 변경 금지 (D2.0-08 §4.1 LOCK)

### 2.1 허용 전이 요약

| # | Source | Target | 트리거 | 가드 조건 | 부수효과 |
|---|--------|--------|--------|----------|---------|
| T-01 | UI_S0_BOOT | UI_S1_IDLE | 로드 완료 | 초기화 성공(config/auth 유효) | 스플래시 닫힘, 입력 필드 활성화 |
| T-02 | UI_S1_IDLE | UI_S2_EDITING | 편집 시작 | Builder View 활성 상태 | Builder 편집 모드 진입, 편집 도구 활성 |
| T-03 | UI_S1_IDLE | UI_S4_RUNNING | 전송/실행 | Hologram View에서 입력 전송 | Thinking Block 표시, trace_id 할당, 진행률 바 시작 |
| T-04 | UI_S2_EDITING | UI_S3_READY | 사전 점검 통과 | Policy/Cost 사전 점검 PASS | "실행 가능" 배지 표시, 실행 버튼 활성 |
| T-05 | UI_S3_READY | UI_S4_RUNNING | 실행 시작 | 사용자 실행 확인 | Thinking Block 표시, trace_id 할당, 진행률 바 시작 |
| T-06 | UI_S3_READY | UI_S7_RECOVERY | 실패 | 사전 점검 후 초기화 실패 | 에러 배너 표시, failure_code 안내 |
| T-07 | UI_S4_RUNNING | UI_S5_AWAIT_APPROVAL | 승인 필요 | `approval_required=true` 수신 | 승인 패널 오픈, 진행바 HOLD, 타임아웃 카운트다운 시작 (L18) |
| T-08 | UI_S4_RUNNING | UI_S6_PRESENTING | 출력 완료 | `output_ready` 수신 | 스트리밍 완료, 3-Part 출력 렌더링, Self-check 배지 |
| T-09 | UI_S4_RUNNING | UI_S7_RECOVERY | failure | `failure_code` 수신 (도구/근거/포맷 등) | 에러 배너 표시, 재시도/대안 버튼, failure_code + fallback_id 표시 |
| T-10 | UI_S5_AWAIT_APPROVAL | UI_S4_RUNNING | 승인(Approve) | 사용자 승인 클릭 | 잠금 해제, 실행 재개, 승인 패널 닫힘 |
| T-11 | UI_S5_AWAIT_APPROVAL | UI_S7_RECOVERY | 거부/타임아웃 | 사용자 거부 또는 L18 타임아웃 경과 | 에러 배너, 거부/타임아웃 사유 표시, 재시도/대안 버튼 |
| T-12 | UI_S6_PRESENTING | UI_S1_IDLE | 새 입력 | 사용자 새 입력 시작 | 출력 영역 축소/정리, 입력 필드 활성화 |
| T-13 | UI_S6_PRESENTING | UI_S8_ARCHIVED | 아카이브 | 사용자 아카이브 요청 또는 세션 종료 | 읽기 전용 모드 진입, 아카이브 배지 |
| T-14 | UI_S7_RECOVERY | UI_S4_RUNNING | 재시도/대안 선택 | 재시도 횟수 < max_retry | 에러 배너 닫힘, 새 trace 시작 또는 retry_count 증가 |
| T-15 | UI_S7_RECOVERY | UI_S1_IDLE | 복구 포기 | 사용자 복구 포기 또는 새 입력 | 에러 상태 초기화, 입력 필드 활성화 |
| T-16 | UI_S8_ARCHIVED | UI_S0_BOOT | 재시작 | 사용자 새 세션 시작 | 새 세션 초기화, 이전 세션 아카이브 완료 |

### 2.2 9x9 전이 매트릭스

> `O` = 허용 (전이 ID), `X` = 금지, `-` = 자기 전이 (N/A)

| Source \ Target | S0_BOOT | S1_IDLE | S2_EDITING | S3_READY | S4_RUNNING | S5_AWAIT | S6_PRESENT | S7_RECOVERY | S8_ARCHIVED |
|-----------------|---------|---------|------------|----------|------------|----------|------------|-------------|-------------|
| **S0_BOOT** | - | O (T-01) | X | X | X | X | X | X | X |
| **S1_IDLE** | X | - | O (T-02) | X | O (T-03) | X | X | X | X |
| **S2_EDITING** | X | X | - | O (T-04) | X | X | X | X | X |
| **S3_READY** | X | X | X | - | O (T-05) | X | X | O (T-06) | X |
| **S4_RUNNING** | X | X | X | X | - | O (T-07) | O (T-08) | O (T-09) | X |
| **S5_AWAIT** | X | X | X | X | O (T-10) | - | X | O (T-11) | X |
| **S6_PRESENT** | X | O (T-12) | X | X | X | X | - | X | O (T-13) |
| **S7_RECOVERY** | X | O (T-15) | X | X | O (T-14) | X | X | - | X |
| **S8_ARCHIVED** | O (T-16) | X | X | X | X | X | X | X | - |

### 2.3 금지 전이 근거

| 금지 경로 | 근거 |
|-----------|------|
| S0 → S2~S8 | 부팅 완료 전 어떤 사용자 상호작용도 불가 |
| S1 → S0 | 재부팅은 S8 경유 필수 (세션 정리 보장) |
| S1 → S3 | S3 진입은 S2(Builder 편집) 경유 필수 (사전 점검 전제) |
| S1 → S5~S8 | S4(실행) 경유 없이 승인/결과/복구/아카이브 진입 불가 |
| S2 → S0/S1/S4~S8 | 편집 중 직접 실행/승인/결과/복구/아카이브 불가 — S3(사전 점검) 경유 필수 |
| S3 → S0~S2/S5/S6/S8 | 실행 가능 상태에서 부팅/편집 복귀/승인/결과/아카이브 직접 전이 불가 |
| S4 → S0~S3/S8 | 실행 중 부팅/입력 대기/편집/사전 점검/아카이브 직접 전이 불가 |
| S5 → S0~S3/S6/S8 | 승인 대기 중 출력 불가 — 승인 후 S4 경유 필수 |
| S6 → S0/S2~S5/S7 | 결과 표시에서 직접 편집/실행/승인/복구 불가 — S1 또는 S8만 가능 |
| S7 → S0/S2/S3/S5~S8 | 복구에서 가능한 경로는 S4(재시도) 또는 S1(포기)만 |
| S8 → S1~S7 | 아카이브에서 복귀는 S0(새 세션) 경유 필수 |

---

## 3. Decision Lock UI 제약 (D2.0-08 §4.3)

> R-61-5: Decision Lock 이후 "결론 변경" UI 제공 금지

| 제약 ID | 규칙 | 적용 시점 |
|---------|------|----------|
| DL-1 | Decision Lock 이후 **"결론 변경" UI 제공 금지** | `ui.core.decision.locked` 이벤트 수신 후 |
| DL-2 | 재시도는 **"근거/실행/포맷" 축에서만 허용** (동일 의도/동일 결론 유지 원칙) | S7_RECOVERY에서 재시도 시 |
| DL-3 | Decision Lock 이후 UI 갱신은 **"결론 재계산 없이" 포맷/레이아웃만 갱신** | S6_PRESENTING에서 UI 업데이트 시 |

**구현 영향**:
- S4_RUNNING에서 `ui.core.decision.locked` 수신 후 → 입력 필드 비활성, 의도 수정 불가
- S7_RECOVERY 재시도 시 → `retry_scope: "execution" | "evidence" | "format"` 파라미터 필수
- S6_PRESENTING 재생성 시 → 동일 decision_id 유지, 결론 변경 UI 요소 숨김

---

## 4. 전이 지연 500ms 명세 (LOCK L17)

> LOCK (D2.0-08 §4.4): 상태 전이 지연 허용 최대값: 500ms (이상 시 로딩 스피너 표시)

### 4.1 L17 적용 대상 전이

| 전이 ID | 전이 경로 | L17 적용 | 근거 |
|---------|----------|---------|------|
| T-01 | S0 → S1 | **적용** | 초기화 완료 확인 필요, 네트워크/설정 로딩 |
| T-02 | S1 → S2 | 미적용 | 로컬 UI 전환, 즉시 응답 |
| T-03 | S1 → S4 | **적용** | Core 연결 + trace_id 할당 대기 |
| T-04 | S2 → S3 | **적용** | 사전 점검(Policy/Cost) 결과 대기 |
| T-05 | S3 → S4 | **적용** | Core 실행 시작 확인 대기 |
| T-06 | S3 → S7 | 미적용 | 실패 즉시 표시 |
| T-07 | S4 → S5 | **적용** | 승인 패널 오픈 + HOLD 상태 전환 |
| T-08 | S4 → S6 | **적용** | 출력 렌더링 준비 대기 |
| T-09 | S4 → S7 | 미적용 | failure 즉시 표시 |
| T-10 | S5 → S4 | **적용** | 승인 처리 + 실행 재개 확인 |
| T-11 | S5 → S7 | 미적용 | 거부/타임아웃 즉시 표시 |
| T-12 | S6 → S1 | 미적용 | 로컬 UI 전환 |
| T-13 | S6 → S8 | 미적용 | 로컬 상태 변경 |
| T-14 | S7 → S4 | **적용** | 재시도 Core 연결 대기 |
| T-15 | S7 → S1 | 미적용 | 로컬 UI 초기화 |
| T-16 | S8 → S0 | **적용** | 새 세션 초기화 대기 |

### 4.2 지연 중 UI 표시

```typescript
interface TransitionDelay {
  /** 전이 시작 후 경과 시간 */
  elapsedMs: number;
  /** L17 임계값 */
  thresholdMs: 500;
  /** 임계값 초과 시 표시 */
  display: {
    /** 로딩 스피너 활성 */
    showSpinner: boolean;         // elapsedMs >= thresholdMs
    /** 전이 대상 상태 힌트 */
    targetHint: string;           // 예: "실행 준비 중..."
    /** 프로그레스 인디케이터 */
    showProgress: boolean;        // 네트워크 관련 전이만
  };
}
```

**지연 중 UI 규칙**:
- 500ms 미만: 즉시 전이, 로딩 표시 없음
- 500ms 이상: 로딩 스피너 표시 + 대상 상태 힌트 텍스트
- 타임아웃(10초): 전이 실패로 간주 → S7_RECOVERY 진입

### 4.3 지연 취소 조건

| 조건 | 동작 |
|------|------|
| 사용자 취소 클릭 | 전이 중단 → 원래 상태 유지 |
| 네트워크 연결 끊김 | 전이 중단 → S7_RECOVERY (failure_code: `MC_ERR_CONN`) |
| Core 응답 타임아웃 (10s) | 전이 중단 → S7_RECOVERY (failure_code: `TL_ERR_TIMEOUT`) |

---

## 5. 9-State ↔ 6-State 양방향 매핑 (ISS-1 해결, D2.0-08 §4.5)

> ISS-1 해결: D2.0-08 §4.5 양방향 매핑 정본. §4.1(9-state)이 UI 설계 정본, §4.4(6-state)는 Core 연동 런타임 뷰.

### 5.1 매핑 테이블

| §4.1 (9-state) | §4.4 (6-state) | 매핑 유형 | 비고 |
|-----------------|----------------|----------|------|
| UI_S0_BOOT | — | N/A | Core 미연결 (부팅 전) |
| UI_S1_IDLE | UIS1IDLE | 1:1 | 입력 대기 |
| UI_S2_EDITING | UIS1IDLE 또는 UIS2PROCESSING | 1:N (조건부) | Core 미호출 시 UIS1, 사전 점검 시작 시 UIS2 |
| UI_S3_READY | UIS2PROCESSING | 1:1 | 사전 점검 = Core 처리 시작 |
| UI_S4_RUNNING | UIS3LOCKED 또는 UIS4RUNNING | 1:N (시점 분기) | Decision Lock 전 = UIS3, Lock 후 = UIS4 |
| UI_S5_AWAIT_APPROVAL | UIS5AWAITAPPROVAL | 1:1 | 승인 대기 |
| UI_S6_PRESENTING | UIS6PRESENTING | 1:1 | 결과 표시 |
| UI_S7_RECOVERY | UIS4RUNNING | 1:1 | 재시도/폴백은 실행 흐름 내 분기 |
| UI_S8_ARCHIVED | — | N/A | 세션 종료 (Core 비활성) |

### 5.2 `mapToSixState()` — 9-State → 6-State 매핑 함수

```typescript
/**
 * 9-State → 6-State 축소 매핑 (D2.0-08 §4.5 정본)
 * 1:N 모호 매핑 해결 규칙 포함
 */
function mapToSixState(
  nineState: NineState,
  context: { isDecisionLocked: boolean; isCoreConnected: boolean }
): SixState | null {
  switch (nineState) {
    case 'UI_S0_BOOT':
      return null; // Core 미연결 — 6-state 대응 없음

    case 'UI_S1_IDLE':
      return 'UIS1IDLE';

    case 'UI_S2_EDITING':
      // 모호 매핑 해결: Core 호출 여부로 분기
      return context.isCoreConnected ? 'UIS2PROCESSING' : 'UIS1IDLE';

    case 'UI_S3_READY':
      return 'UIS2PROCESSING'; // 사전 점검 = Core 처리 시작

    case 'UI_S4_RUNNING':
      // 모호 매핑 해결: Decision Lock 전후로 분기
      return context.isDecisionLocked ? 'UIS4RUNNING' : 'UIS3LOCKED';

    case 'UI_S5_AWAIT_APPROVAL':
      return 'UIS5AWAITAPPROVAL';

    case 'UI_S6_PRESENTING':
      return 'UIS6PRESENTING';

    case 'UI_S7_RECOVERY':
      return 'UIS4RUNNING'; // Recovery는 실행 흐름 내 분기

    case 'UI_S8_ARCHIVED':
      return null; // 세션 종료 — 6-state 대응 없음
  }
}
```

### 5.3 `mapToNineState()` — 6-State → 9-State 역매핑 함수

```typescript
/**
 * 6-State → 9-State 확장 역매핑 (D2.0-08 §4.5 정본)
 * 1:N 역매핑 해결 규칙: 추가 컨텍스트 필수
 */
function mapToNineState(
  sixState: SixState,
  context: {
    isBootPhase: boolean;
    isEditing: boolean;
    isPreCheckPassed: boolean;
    isDecisionLocked: boolean;
    hasFailure: boolean;
    isArchived: boolean;
  }
): NineState {
  // Boot/Archive는 6-state에서 null로 매핑되므로 컨텍스트로 판별
  if (context.isBootPhase) return 'UI_S0_BOOT';
  if (context.isArchived) return 'UI_S8_ARCHIVED';

  switch (sixState) {
    case 'UIS1IDLE':
      // UIS1IDLE → S1 또는 S2(편집 중 Core 미호출)
      return context.isEditing ? 'UI_S2_EDITING' : 'UI_S1_IDLE';

    case 'UIS2PROCESSING':
      // UIS2PROCESSING → S2(편집 중 Core 호출) 또는 S3(사전 점검 통과)
      return context.isPreCheckPassed ? 'UI_S3_READY' : 'UI_S2_EDITING';

    case 'UIS3LOCKED':
      return 'UI_S4_RUNNING'; // Decision Lock 진행 중

    case 'UIS4RUNNING':
      // UIS4RUNNING → S4(실행 중) 또는 S7(재시도/폴백 중)
      return context.hasFailure ? 'UI_S7_RECOVERY' : 'UI_S4_RUNNING';

    case 'UIS5AWAITAPPROVAL':
      return 'UI_S5_AWAIT_APPROVAL';

    case 'UIS6PRESENTING':
      return 'UI_S6_PRESENTING';
  }
}
```

### 5.4 1:N 모호 매핑 해결 규칙

| 모호 매핑 | 해결 기준 | 결정 컨텍스트 |
|-----------|----------|-------------|
| S2_EDITING → UIS1 or UIS2 | Core 연결 여부 | `isCoreConnected: boolean` |
| S4_RUNNING → UIS3 or UIS4 | Decision Lock 여부 | `isDecisionLocked: boolean` |
| UIS1IDLE → S1 or S2 | 편집 모드 여부 | `isEditing: boolean` |
| UIS2PROCESSING → S2 or S3 | 사전 점검 통과 여부 | `isPreCheckPassed: boolean` |
| UIS4RUNNING → S4 or S7 | failure 발생 여부 | `hasFailure: boolean` |

---

## 6. EventType 57건 → 상태 전이 매핑 (ISS-7 해결, D2.0-08 §5.3~§5.7)

> ISS-7 해결: D2.0-08 §5.3~§5.7 EventType 57건 → 상태 전이 매핑 정본화
> LOCK L19: `ui.{layer}.{subject}.{action}` (소문자, 점 구분)

### 6.1 ui.frontmini.* (7건) — S1_IDLE 유지 / S4_RUNNING 진입

| # | Event Type | 상태 전이 영향 | 전이 ID |
|---|-----------|--------------|--------|
| 1 | `ui.frontmini.input.received` | S1_IDLE 유지 (입력 수신, 아직 실행 아님) | — |
| 2 | `ui.frontmini.scan.started` | S1_IDLE 유지 (Front Mini 내부 처리) | — |
| 3 | `ui.frontmini.pii.detected` | S1_IDLE 유지 → 마스킹/승인 모달 | — |
| 4 | `ui.frontmini.malware.found` | S1_IDLE 유지 → 업로드 취소 | — |
| 5 | `ui.frontmini.summary.ready` | S1_IDLE 유지 (프리뷰 표시) | — |
| 6 | `ui.frontmini.package.ready` | S1_IDLE 유지 (전송 준비 완료) | — |
| 7 | `ui.frontmini.package.sent` | S1_IDLE → **S4_RUNNING** (분석 시작 = 실행 시작) | T-03 |

### 6.2 ui.core.* + ui.gate.* (16건) — S4_RUNNING 내부 / S5_AWAIT 진입

| # | Event Type | 상태 전이 영향 | 전이 ID |
|---|-----------|--------------|--------|
| 1 | `ui.core.received` | S4_RUNNING 유지 (Thinking Block 표시) | — |
| 2 | `ui.core.intent.analyzed` | S4_RUNNING 유지 (의도 분석 완료) | — |
| 3 | `ui.gate.policy.checked` | S4_RUNNING 유지 (디버그 기록) | — |
| 4 | `ui.gate.policy.violated` | S4_RUNNING → **S7_RECOVERY** (정책 위반 = failure) | T-09 |
| 5 | `ui.gate.cost.calculated` | S4_RUNNING 유지 (Cost HUD 갱신) | — |
| 6 | `ui.gate.cost.warning` | S4_RUNNING 유지 (경고 표시) | — |
| 7 | `ui.gate.approval.required` | S4_RUNNING → **S5_AWAIT_APPROVAL** | T-07 |
| 8 | `ui.gate.approval.waiting` | S5_AWAIT_APPROVAL 유지 (Hold 표시) | — |
| 9 | `ui.policy.blocked` | S4_RUNNING → **S7_RECOVERY** (정책 차단 = failure) | T-09 |
| 10 | `ui.core.decision.locked` | S4_RUNNING 유지 (Decision Lock — R-61-5 적용 시작) | — |
| 11 | `ui.core.p2.locked` | S4_RUNNING 유지 (P2 배지 활성) | — |
| 12 | `ui.gate.cost.warning_80` | S4_RUNNING 유지 (DEC-015 게이지 노란색) | — |
| 13 | `ui.gate.cost.ceiling_100` | S4_RUNNING → **S7_RECOVERY** (DEC-015 비용 차단) | T-09 |
| 14 | `ui.core.p2.modal.shown` | S4_RUNNING 유지 (DEC-011 모달 표시) | — |
| 15 | `ui.core.p2.modal.confirmed` | S4_RUNNING 유지 (P2 활성화 확인) | — |
| 16 | `ui.core.p2.modal.cancelled` | S4_RUNNING 유지 (P2 활성화 중단) | — |

### 6.3 ui.node.* + ui.main.* (13건) — S4_RUNNING 내부 / S6_PRESENTING 진입

| # | Event Type | 상태 전이 영향 | 전이 ID |
|---|-----------|--------------|--------|
| 1 | `ui.node.selected` | S4_RUNNING 유지 (노드 선택 표시) | — |
| 2 | `ui.node.context.loaded` | S4_RUNNING 유지 (컨텍스트 로드) | — |
| 3 | `ui.main.job.queued` | S4_RUNNING 유지 (대기 중 표시) | — |
| 4 | `ui.main.execution.started` | S4_RUNNING 유지 (진행률 바 시작) | — |
| 5 | `ui.main.step.started` | S4_RUNNING 유지 (스텝 갱신) | — |
| 6 | `ui.main.stream.chunk` | S4_RUNNING → **S6_PRESENTING** 진행 중 (스트리밍 출력) | T-08 (점진적) |
| 7 | `ui.main.artifact.created` | S6_PRESENTING 유지 (아티팩트 렌더링) | — |
| 8 | `ui.main.evidence.linked` | S6_PRESENTING 유지 (인용 생성) | — |
| 9 | `ui.main.selfcheck.started` | S6_PRESENTING 유지 (검증 중) | — |
| 10 | `ui.main.selfcheck.passed` | S6_PRESENTING 유지 (PASS 배지) | — |
| 11 | `ui.main.selfcheck.failed` | S6_PRESENTING 유지 또는 → **S7_RECOVERY** (자동 보완) | T-09 (조건부) |
| 12 | `ui.main.qod.updated` | S6_PRESENTING 유지 (Evidence 갱신) | — |
| 13 | `ui.main.alert.shown` | S6_PRESENTING 유지 (불확실성 배너) | — |

### 6.4 ui.tool.* (6건) — S4_RUNNING 내부 / S7_RECOVERY 진입

| # | Event Type | 상태 전이 영향 | 전이 ID |
|---|-----------|--------------|--------|
| 1 | `ui.tool.call.started` | S4_RUNNING 유지 (도구 실행 중 토스트) | — |
| 2 | `ui.tool.call.finished` | S4_RUNNING 유지 (완료 체크) | — |
| 3 | `ui.tool.error.timeout` | S4_RUNNING → **S7_RECOVERY** (TL_ERR_TIMEOUT) | T-09 |
| 4 | `ui.tool.error.ratelimit` | S4_RUNNING → **S7_RECOVERY** (대기 안내) | T-09 |
| 5 | `ui.tool.error.parse` | S4_RUNNING 유지 (WARN — 원본 제공 옵션) | — |
| 6 | `ui.tool.file.converted` | S4_RUNNING 유지 (파일 변환 완료) | — |

### 6.5 ui.cli.* (10건) — CLI 모드 전이 매핑

| # | Event Type | 상태 전이 영향 | 전이 ID |
|---|-----------|--------------|--------|
| 1 | `ui.cli.command.received` | S1_IDLE → **S4_RUNNING** (CLI 실행 시작) | T-03 |
| 2 | `ui.cli.command.completed` | S4_RUNNING → **S6_PRESENTING** (결과 출력) | T-08 |
| 3 | `ui.cli.command.failed` | S4_RUNNING → **S7_RECOVERY** (에러 출력) | T-09 |
| 4 | `ui.cli.auth.prompted` | S4_RUNNING → **S5_AWAIT_APPROVAL** (승인 대기) | T-07 |
| 5 | `ui.cli.auth.resolved` | S5_AWAIT_APPROVAL → **S4_RUNNING** (승인 결과) | T-10 |
| 6 | `ui.cli.progress.updated` | S4_RUNNING 유지 (진행률 갱신) | — |
| 7 | `ui.cli.output.streamed` | S4_RUNNING → **S6_PRESENTING** (점진적) | T-08 |
| 8 | `ui.cli.config.changed` | S1_IDLE 유지 (설정 변경) | — |
| 9 | `ui.cli.session.started` | S0_BOOT → **S1_IDLE** (CLI 세션 시작) | T-01 |
| 10 | `ui.cli.session.ended` | S6_PRESENTING → **S8_ARCHIVED** (세션 종료) | T-13 |

### 6.6 ui.memory.* (5건) — S6_PRESENTING 내부

| # | Event Type | 상태 전이 영향 | 전이 ID |
|---|-----------|--------------|--------|
| 1 | `ui.memory.candidate.found` | S6_PRESENTING 유지 (저장 후보 패널) | — |
| 2 | `ui.memory.masking.applied` | S6_PRESENTING 유지 (마스킹 비교) | — |
| 3 | `ui.memory.commit.success` | S6_PRESENTING 유지 (저장 완료 토스트) | — |
| 4 | `ui.memory.commit.denied` | S6_PRESENTING 유지 (저장 취소) | — |
| 5 | `ui.memory.source.trust_updated` | S6_PRESENTING 유지 (신뢰도 갱신) | — |

### 6.7 전이 트리거 이벤트 요약

| 전이 ID | 트리거 이벤트 |
|---------|-------------|
| T-01 | `ui.cli.session.started` (CLI) / 내부 boot_complete (GUI) |
| T-03 | `ui.frontmini.package.sent`, `ui.cli.command.received` |
| T-07 | `ui.gate.approval.required`, `ui.cli.auth.prompted` |
| T-08 | `ui.main.stream.chunk` (is_final=true), `ui.cli.command.completed`, `ui.cli.output.streamed` (is_final=true) |
| T-09 | `ui.gate.policy.violated`, `ui.policy.blocked`, `ui.gate.cost.ceiling_100`, `ui.tool.error.timeout`, `ui.tool.error.ratelimit`, `ui.cli.command.failed` |
| T-10 | `ui.cli.auth.resolved` (approved) |
| T-11 | `ui.cli.auth.resolved` (denied) / L18 타임아웃 |
| T-13 | `ui.cli.session.ended` / 사용자 아카이브 요청 |

### 6.8 D2.1-D2 EventTypeRegistry 동기 등록 형식

```typescript
/**
 * D2.1-D2 §5.1 EventTypeRegistry 동기 등록 형식
 * ISS-7 해결: D2.0-08 §5.9 연동 규칙 준수
 */
interface EventTypeRegistryEntry {
  /** L19 준수: ui.{layer}.{subject}.{action} */
  event_type: string;
  /** 소유 정본 */
  source_doc: 'D2.0-08';
  /** 소유 섹션 */
  source_section: string;  // 예: '§5.3', '§5.4'
  /** 심각도 */
  severity: 'INFO' | 'WARN' | 'ERROR' | 'CRITICAL';
  /** 상태 전이 트리거 여부 */
  triggers_transition: boolean;
  /** 트리거 시 대상 전이 ID */
  transition_id?: string;  // 예: 'T-07', 'T-09'
  /** 공통 Payload 키 (§5.8) */
  payload_keys: string[];
  /** D2.1-D2 등록 상태 */
  registry_status: 'REGISTERED' | 'PENDING';
}
```

**동기화 규칙**: D2.0-08에서 event_type 추가/변경 시, D2.1-D2 §5.1 EventTypeRegistry에도 반드시 반영. 6-12(Event-Logging) 도메인과 협력.

---

## 7. Pipeline S0~S8 ↔ UI 상태 크로스 매핑 (D2.0-08 §4.6 D8-M11)

| Pipeline (02 정본) | 단계명 | UI 상태 (§4.1) | 6-State (§4.4) | UI 표시 |
|---|---|---|---|---|
| S0_RECEIVED | Perception/Intake | UI_S4_RUNNING | UIS3LOCKED | "요청 수신됨" |
| S1_INTENT_PARSED | Perception/Intake | UI_S4_RUNNING | UIS3LOCKED | "의도 분석 완료" |
| S2_EVIDENCE_READY | Reasoning/Plan | UI_S4_RUNNING | UIS3LOCKED | "근거 수집 완료" |
| S3_DECISION_LOCKED | Reasoning/Plan | UI_S4_RUNNING | UIS4RUNNING | "결정 잠금" |
| S4_EXECUTING | Action/Execute | UI_S4_RUNNING | UIS4RUNNING | "실행 중" |
| S5_OUTPUT_READY | Action/Execute | UI_S6_PRESENTING | UIS6PRESENTING | "출력 준비됨" |
| S6_SELF_CHECKED | Reflection/Verify | UI_S6_PRESENTING | UIS6PRESENTING | "자기검증 완료" |
| S7_MEMORY_COMMITTED | Memory/Store | UI_S6_PRESENTING | UIS6PRESENTING | "메모리 저장됨" |
| S8_DONE | — | UI_S8_ARCHIVED | — | "완료" |

---

## 8. Zustand uiStateStore 연동 인터페이스

> Part2 §6.1.3: Zustand Stores 7개 중 `uiStateStore` 정의

### 8.1 Store 인터페이스

```typescript
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

/** 9-State 타입 (LOCK L1) */
type NineState =
  | 'UI_S0_BOOT'
  | 'UI_S1_IDLE'
  | 'UI_S2_EDITING'
  | 'UI_S3_READY'
  | 'UI_S4_RUNNING'
  | 'UI_S5_AWAIT_APPROVAL'
  | 'UI_S6_PRESENTING'
  | 'UI_S7_RECOVERY'
  | 'UI_S8_ARCHIVED';

/** 6-State 타입 (D2.0-08 §4.4) */
type SixState =
  | 'UIS1IDLE'
  | 'UIS2PROCESSING'
  | 'UIS3LOCKED'
  | 'UIS4RUNNING'
  | 'UIS5AWAITAPPROVAL'
  | 'UIS6PRESENTING';

/** 전이 이력 엔트리 */
interface TransitionEntry {
  from: NineState;
  to: NineState;
  trigger: string;         // event_type or user action
  timestamp: number;       // Unix ms
  transitionId: string;    // T-01 ~ T-16
  delayMs: number;         // 실제 전이 소요 시간
  traceId: string;
}

/** uiStateStore 인터페이스 */
interface UIStateStore {
  // --- State ---
  /** 현재 9-state */
  currentState: NineState;
  /** 이전 9-state */
  previousState: NineState | null;
  /** 현재 6-state (자동 동기) */
  currentSixState: SixState | null;
  /** 전이 이력 (최근 50건) */
  transitionHistory: TransitionEntry[];
  /** Decision Lock 여부 */
  isDecisionLocked: boolean;
  /** Core 연결 여부 */
  isCoreConnected: boolean;
  /** 편집 모드 여부 */
  isEditing: boolean;
  /** failure 상태 여부 */
  hasFailure: boolean;
  /** 현재 failure_code (S7 시) */
  currentFailureCode: string | null;
  /** 현재 fallback_id (S7 시) */
  currentFallbackId: string | null;
  /** 재시도 카운트 */
  retryCount: number;
  /** 전이 지연 진행 중 */
  isTransitioning: boolean;

  // --- Actions ---
  /**
   * 상태 전이 실행
   * @param targetState 대상 9-state
   * @param event 트리거 이벤트
   * @returns 전이 성공 여부
   */
  transition: (targetState: NineState, event: string) => boolean;

  /**
   * 전이 유효성 검증 (전이 매트릭스 기반)
   * @param from 현재 상태
   * @param to 대상 상태
   * @returns 허용 여부
   */
  canTransition: (from: NineState, to: NineState) => boolean;

  /**
   * 9-state → 6-state 동기화
   * mapToSixState() 자동 호출
   */
  syncSixState: () => void;

  /**
   * Decision Lock 설정
   * R-61-5 적용 시작
   */
  setDecisionLocked: (locked: boolean) => void;

  /**
   * failure 설정
   * S7_RECOVERY 관련 데이터 갱신
   */
  setFailure: (code: string | null, fallbackId: string | null) => void;

  /** 전이 이력 초기화 */
  clearHistory: () => void;
}
```

### 8.2 전이 매트릭스 검증 로직

```typescript
/** 허용 전이 맵 (§2.2 기반) */
const ALLOWED_TRANSITIONS: Record<NineState, NineState[]> = {
  'UI_S0_BOOT': ['UI_S1_IDLE'],
  'UI_S1_IDLE': ['UI_S2_EDITING', 'UI_S4_RUNNING'],
  'UI_S2_EDITING': ['UI_S3_READY'],
  'UI_S3_READY': ['UI_S4_RUNNING', 'UI_S7_RECOVERY'],
  'UI_S4_RUNNING': ['UI_S5_AWAIT_APPROVAL', 'UI_S6_PRESENTING', 'UI_S7_RECOVERY'],
  'UI_S5_AWAIT_APPROVAL': ['UI_S4_RUNNING', 'UI_S7_RECOVERY'],
  'UI_S6_PRESENTING': ['UI_S1_IDLE', 'UI_S8_ARCHIVED'],
  'UI_S7_RECOVERY': ['UI_S4_RUNNING', 'UI_S1_IDLE'],
  'UI_S8_ARCHIVED': ['UI_S0_BOOT'],
};

function canTransition(from: NineState, to: NineState): boolean {
  return ALLOWED_TRANSITIONS[from]?.includes(to) ?? false;
}
```

### 8.3 Core ↔ UI 상태 불일치 감지

```typescript
/**
 * Core 상태와 UI 상태 불일치 감지 (D2.0-08 §4.4)
 * 불일치 시 ui.core.state.mismatch 이벤트 발행 + 자동 동기화
 */
function detectMismatch(
  uiState: NineState,
  coreState: SixState
): boolean {
  const expectedSixState = mapToSixState(uiState, getContext());
  if (expectedSixState !== null && expectedSixState !== coreState) {
    // ui.core.state.mismatch 이벤트 발행
    emitEvent({
      event_type: 'ui.core.state.mismatch',
      severity: 'WARN',
      payload: {
        ui_state: uiState,
        expected_six_state: expectedSixState,
        actual_core_state: coreState,
      },
    });
    // 자동 동기화: Core 상태를 기준으로 UI 업데이트
    return true;
  }
  return false;
}
```

---

## 9. STEP7-C 상태 머신 관련 항목 매핑 (15건)

> 종합계획서 §6.2 배분: 03_ui-state-machine ~15건

| # | 항목 ID | 설명 | 상태 전이 연관 | 매핑 상세 |
|---|---------|------|-------------|---------|
| 1 | **S7C-012** | ORANGE/BLUE 상태 표시 | S4_RUNNING 중 하단 상태바 | 활성 모듈/NODE 상태를 9-state별로 표시: S4→ORANGE 활성(실행 중), S6→BLUE 활성(결과) |
| 2 | **S7C-030** | 비용 미리보기 | S1_IDLE → S4_RUNNING 전이 전 | "이 메시지를 보내면 ~₩50 예상" — S1에서 입력 시 Cost Gate 연동으로 예상 비용 표시 |
| 3 | **S7C-038** | 스트리밍 타이핑 효과 | S4_RUNNING → S6_PRESENTING 전이 중 | `ui.main.stream.chunk` 이벤트에 의한 토큰 단위 실시간 표시, 커서 깜빡임, "중지" 버튼(S4 취소) |
| 4 | **S7C-041** | 신뢰도 표시바 | S6_PRESENTING 내부 | `ui.main.qod.updated` 이벤트에 의한 QoD 기반 신뢰도 바 렌더링 |
| 5 | **S7C-042** | 비용 표시 | S6_PRESENTING 내부 | `ui.gate.cost.calculated` 기반 "이 응답 비용: ₩35 (모델: Sonnet, 토큰: 2,340)" 표시 |
| 6 | **S7C-060** | 오프라인 UI 상태 | 모든 상태 → 오프라인 감지 시 | 네트워크 끊김 시 `MC_ERR_CONN` → S7_RECOVERY 진입, 온라인 복귀 시 동기화 바 + 이전 상태 복원 |
| 7 | **S7C-063** | 에이전트 실행 진행률 | S4_RUNNING 내부 | `ui.main.step.started` 이벤트에 의한 멀티스텝 "검색 중... (3/7)", Pipeline S0~S4 단계 매핑 |
| 8 | **S7C-067** | 에이전트 취소/일시정지 | S4_RUNNING 내부 | "중지" → S4 유지(일시정지), "재개" → S4 유지(실행 재개), "취소" → S7_RECOVERY |
| 9 | **S7C-069** | 3-Gate 통과 표시 | S4_RUNNING 내부 | `ui.gate.policy.checked` + `ui.gate.cost.calculated` + `ui.main.evidence.linked` → 3원형 시각 표시 |
| 10 | **S7C-070** | 파이프라인 스텝 표시 | S4_RUNNING 내부 | Pipeline S0~S8 → UI_S4_RUNNING 매핑 기반 7단계 시각화 (§7 크로스 매핑 참조) |
| 11 | **S7C-081** | 3-Gate 상태 표시기 | S4_RUNNING / S6_PRESENTING | Policy/Cost/Evidence 3원형 색상 표시기 |
| 12 | **S7C-083** | QoD 신뢰도 바 | S6_PRESENTING 내부 | `ui.main.qod.updated` 기반 색상 바 렌더링 |
| 13 | **S7C-084** | 파이프라인 스텝 인디케이터 | S4_RUNNING 내부 | 7단계 스텝 바, 현재 Pipeline 단계 강조 |
| 14 | **S7C-085** | Decision Object 카드 | S6_PRESENTING 내부 | `ui.core.decision.locked` 후 결정 근거/모델/비용/증거 카드 (V2 배정) |
| 15 | **S7C-040** | 3-Part 출력 UI | S4_RUNNING → S6_PRESENTING | `output_ready` 시 user_response + evidence_summary + log_report 3파트 렌더링 |

**매핑 요약**: Critical 10건 전체 L3 매핑 완료, High 5건 전체 L3 매핑 완료 (V2 1건: S7C-085)

---

## 10. Phase 2 테스트 시나리오

> Gate #10: UI 9-State SM 전이 동작 검증

| # | 테스트 ID | 시나리오 | 예상 전이 경로 | 검증 포인트 |
|---|----------|---------|-------------|-----------|
| 1 | TST-SM-01 | 정상 흐름 (Hologram) | S0→S1→S4→S6→S1 | 전체 전이 순서 + L17 500ms 준수 |
| 2 | TST-SM-02 | 정상 흐름 (Builder) | S0→S1→S2→S3→S4→S6→S8 | Builder 편집 경유 전이 |
| 3 | TST-SM-03 | 승인 흐름 | S4→S5→S4→S6 | 승인 패널 오픈/닫힘, L18 타임아웃 |
| 4 | TST-SM-04 | 승인 거부 | S4→S5→S7→S1 | 거부 시 Recovery → Idle |
| 5 | TST-SM-05 | 실행 실패 + 재시도 | S4→S7→S4→S6 | failure_code 표시, 재시도 카운트 증가 |
| 6 | TST-SM-06 | 실행 실패 + 포기 | S4→S7→S1 | 복구 포기 후 Idle 복귀 |
| 7 | TST-SM-07 | Decision Lock 후 재생성 | S4(lock)→S6→재생성 | R-61-5: 결론 변경 UI 숨김 확인 |
| 8 | TST-SM-08 | 금지 전이 시도 | S1→S6 시도 | canTransition() = false, 전이 거부 |
| 9 | TST-SM-09 | 전이 지연 500ms | T-03 실행 | 500ms 미만 즉시 전이, 500ms 이상 스피너 |
| 10 | TST-SM-10 | 9↔6 매핑 정합성 | 모든 9-state 순회 | mapToSixState() + mapToNineState() 왕복 일관성 |
| 11 | TST-SM-11 | Core 불일치 감지 | UI=S4, Core=UIS1 | `ui.core.state.mismatch` 이벤트 발행 + 자동 동기화 |
| 12 | TST-SM-12 | 오프라인 전환 | 임의 상태 → 네트워크 끊김 | S7_RECOVERY 진입 (MC_ERR_CONN) + 온라인 복귀 시 복원 |
| 13 | TST-SM-13 | CLI 세션 전이 | S0→S1(CLI)→S4→S5→S4→S6→S8 | CLI 모드 전이 경로 전체 |
| 14 | TST-SM-14 | Pipeline 크로스 매핑 | Pipeline S0~S8 → UI 상태 | §7 매핑 테이블 전수 검증 |

---

## 11. LOCK/CONFLICT 보고

### 11.1 참조 LOCK (변경 없음)

| LOCK | 항목 | 값 | 본 문서 준수 |
|------|------|---|------------|
| L1 | UI 9-State | 9개 (S0~S8) | 준수 — §1 9-state 정의 정본 일치 |
| L17 | 상태 전이 지연 | 최대 500ms | 준수 — §4 전이 지연 명세 |
| L18 | P2 승인 타임아웃 | HITL 5분 / 일반 10분 | 준수 — §2.1 T-07/T-11 가드 조건 |
| L19 | 이벤트 네이밍 | `ui.{layer}.{subject}.{action}` | 준수 — §6 전체 57건 L19 형식 |
| L20 | FailureCode 수 | 14 + 9 | 참조만 — §4.3 failure_code 기반 전이 |

### 11.2 CONFLICT

- 발견 0건, OPEN 0건

---

## 변경 이력

| 일자 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-04-12 | v1.0 | P1-7 초기 작성. 9-State 정의, 9x9 전이 매트릭스, ISS-1 해결(양방향 매핑), L17 전이 지연 명세, ISS-7 해결(57건 EventType 전이 매핑), Zustand uiStateStore 인터페이스, STEP7-C 15건 매핑, Phase 2 테스트 14건 |
