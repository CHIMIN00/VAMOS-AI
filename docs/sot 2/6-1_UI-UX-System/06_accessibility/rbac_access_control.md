# RBAC 접근 제어 — L3 상세 명세

> **도메인**: 6-1_UI-UX-System / 06_accessibility
> **버전**: v1.0
> **작성일**: 2026-04-12
> **세션**: P1-12 — #10 RBAC 접근 제어
> **정본 출처**: D2.0-08 §8 (Approval Gate/Masking), Part2 §6.1.8 (RBAC 4단계), D2.0-07 §3.6/§4.3 (승인 타임아웃)
> **상태**: Phase 1 L3 완료
> **권한**: sot 2/6-1 = What + How (구현 상세). LOCK 값 재정의 불가 (AUTHORITY_CHAIN §3.4)

---

## 목차

1. [정본 참조 테이블](#1-정본-참조-테이블)
2. [LOCK 참조](#2-lock-참조)
3. [RBAC 4단계 역할 정의](#3-rbac-4단계-역할-정의)
4. [페이지별 RBAC 접근 매트릭스](#4-페이지별-rbac-접근-매트릭스)
5. [컴포넌트별 가시성/활성화 규칙](#5-컴포넌트별-가시성활성화-규칙)
6. [Approval Gate HOLD 전환 UI](#6-approval-gate-hold-전환-ui)
7. [RBAC 미들웨어/가드 설계](#7-rbac-미들웨어가드-설계)
8. [6-1 ↔ 6-2 동기화 (W-3)](#8-6-1--6-2-동기화-w-3)
9. [STEP7-C 매핑](#9-step7-c-매핑)
10. [검증 체크리스트](#10-검증-체크리스트)

---

## 1. 정본 참조 테이블

| 문서 | 섹션 | 참조 내용 | 용도 |
|------|------|----------|------|
| **D2.0-08** | §8 | 승인 게이트 UI 패턴, 민감정보 마스킹 패턴, PII 장기 저장 차단 UI | 접근 제어 UI 패턴 정본 |
| **Part2** | §6.1.8 | RBAC 4역할별 접근 가능 화면 + 제한 사항 | RBAC 역할 정의 정본 |
| **D2.0-07** | §3.6 | OWNER/ADMIN/OPERATOR/VIEWER 역할별 허용 범위 + 승인 요구 수준 | 역할 권한 상세 |
| **D2.0-07** | §4.3/§4.3.2 | 일반 승인 10분 / HITL 고위험 5분 타임아웃 → 자동 deny | 승인 타임아웃 정본 |
| **D2.0-08** | §10.4 | React 컴포넌트 44개 레지스트리 | 컴포넌트별 RBAC 규칙 대상 |
| **01_builder-view/seven_pages.md** | §2 | 7개 페이지 목록 + 라우트 | 페이지별 접근 매트릭스 대상 |

---

## 2. LOCK 참조

> **규칙**: LOCK 값은 재정의 불가. 참조 시 `> LOCK (출처): [원문 그대로]` 형식 준수 (AUTHORITY_CHAIN §3.4)

> LOCK (Part2 §6.1.8): **RBAC 4단계** — OWNER / ADMIN / OPERATOR / VIEWER (L10)

> LOCK (D2.0-07 §4.3): **승인 타임아웃** — HITL 고위험 5분 / 일반 승인 10분 → 미응답 시 자동 deny (L18)

---

## 3. RBAC 4단계 역할 정의

> **출처**: Part2 §6.1.8 + D2.0-07 §3.6 교차 확인

### 3.1 역할 개요

| 역할 | 설명 | 허용 범위 | 승인 요구 수준 |
|------|------|----------|--------------|
| **OWNER** | 시스템 소유자(사용자 본인) | 모든 정책 변경, 비용 상한 변경, P2 도메인 승인 포함 전체 권한 | 계획 승인 + 실행 승인 모두 직접 부여 가능 |
| **ADMIN** | 위임된 관리자(멀티유저 V2+) | 정책 조회, 일반 설정 변경, 비용 상한 변경, Agent 실행 전체 허용. Constitution 편집/P2 승인은 OWNER만 가능 | 계획 승인 + 일반 실행 승인 가능. 고위험 실행 승인(P2, 비용 상한 변경)은 OWNER만 |
| **OPERATOR** | 일반 운영자 | 일반 Task 실행, 허용목록 내 Tool 호출, 비P2 도메인 작업, 개인 설정만 변경 가능 | 계획 승인까지만 가능. 실행 승인(고위험)은 OWNER/ADMIN만 |
| **VIEWER** | 읽기 전용 열람자(감사/로그 열람 포함) | 읽기 전용(로그/이벤트 조회, 대시보드 열람), 실행/승인 불가 | 승인 행위 불가 |

> **출처**: D2.0-07 §3.6.1 (역할 정의) + §3.6.2 (역할별 승인 요구 수준) 원문 그대로

### 3.2 TypeScript 역할 열거형

```typescript
/**
 * RBAC 역할 — LOCK L10 (Part2 §6.1.8)
 * 절대 변경 금지. 순서는 권한 수준 내림차순.
 */
export enum RBACRole {
  OWNER    = 'OWNER',
  ADMIN    = 'ADMIN',
  OPERATOR = 'OPERATOR',
  VIEWER   = 'VIEWER',
}

/** 역할 권한 레벨 (숫자가 클수록 높은 권한) */
export const RBAC_LEVEL: Record<RBACRole, number> = {
  [RBACRole.VIEWER]:   0,
  [RBACRole.OPERATOR]: 1,
  [RBACRole.ADMIN]:    2,
  [RBACRole.OWNER]:    3,
};
```

### 3.3 권한 범위 초과 시 처리

> **출처**: D2.0-07 §3.6.3

- 역할 권한 초과 요청은 즉시 **deny** + `failure_code: RBAC_PERMISSION_DENIED` 기록
- AGENT가 자신의 허용 범위 밖 실행을 시도할 경우, 자동으로 OWNER에게 승인 요청을 상신

---

## 4. 페이지별 RBAC 접근 매트릭스

> **출처**: Part2 §6.1.8 원문 (L10) + seven_pages.md §2 (7개 페이지)
> **규칙**: 접근 가능(`FULL`), 읽기 전용(`READ`), 접근 불가(`DENY`)

### 4.1 매트릭스

| # | 페이지 | 라우트 | OWNER | ADMIN | OPERATOR | VIEWER |
|---|--------|--------|-------|-------|----------|--------|
| 1 | **DashboardPage** | `/dashboard` | FULL | FULL | FULL | READ |
| 2 | **ChatPage** | `/chat` | FULL | FULL | FULL | READ (입력/실행 불가) |
| 3 | **WorkflowPage** | `/workflow` | FULL | FULL | FULL | DENY |
| 4 | **MemoryPage** | `/memory` | FULL | FULL | FULL | DENY |
| 5 | **SettingsPage** | `/settings` | FULL | FULL (시스템 삭제 불가) | READ | DENY |
| 6 | **LogPage** | `/log` | FULL | FULL | DENY | DENY |
| 7 | **NodeDetailPage** | `/node-detail/:nodeId` | FULL | FULL | FULL | DENY |

### 4.2 매트릭스 도출 근거

| 역할 | Part2 §6.1.8 원문 | 매트릭스 적용 |
|------|-------------------|-------------|
| **OWNER** | 모든 화면 / 제한 없음 | 7개 전체 FULL |
| **ADMIN** | 모든 화면 / 시스템 삭제 불가 | 7개 전체 FULL (SettingsPage 내 시스템 삭제 버튼만 disabled) |
| **OPERATOR** | Dashboard, Chat, Workflow, Memory / Settings 읽기 전용 | Dashboard/Chat/Workflow/Memory/NodeDetail = FULL, Settings = READ, Log = DENY |
| **VIEWER** | Dashboard, Chat (읽기) / 입력/실행 불가, 조회만 가능 | Dashboard = READ, Chat = READ (입력 비활성), 나머지 = DENY |

> **OPERATOR + LogPage**: Part2 §6.1.8에 Log가 접근 가능 화면에 명시되지 않으므로 DENY 처리. LogPage 접근이 필요한 경우 ADMIN 이상 권한 필요.
> **OPERATOR + NodeDetailPage**: NodeDetailPage는 Workflow 작업의 연장선으로 판단하여 FULL 접근 허용 (Workflow 범위 내).

### 4.3 조건부 접근 규칙

| 조건 | 적용 대상 | 규칙 |
|------|----------|------|
| **P2 도메인 작업** | WorkflowPage, NodeDetailPage | OWNER만 P2 도메인 활성화/승인 가능 (D2.0-07 §2.1) |
| **Constitution 편집** | SettingsPage | OWNER만 가능 — ADMIN 포함 불가 (D2.0-07 §3.6.1) |
| **비용 상한 변경** | SettingsPage | OWNER/ADMIN만 가능 (D2.0-07 §3.6.2) |
| **Agent 자율 운영 수준 변경** | SettingsPage | OWNER만 명시적 승인 필요 (D2.0-07 §3.2) |

---

## 5. 컴포넌트별 가시성/활성화 규칙

> **출처**: D2.0-08 §10.4 (44개 컴포넌트) + Part2 §6.1.8 (RBAC 접근 규칙)
> **표기**: `V` = visible+enabled, `D` = visible+disabled, `H` = hidden, `R` = visible+read-only

### 5.1 RBAC 영향 컴포넌트 (26건)

아래 컴포넌트만 RBAC 역할에 따라 가시성/활성화 상태가 변경된다. 나머지 18개 컴포넌트(BV-PIPE-01, BV-PIPE-02, HV-CHAT-02, HV-CHAT-03, HV-EVID-01, HV-EVID-02, HV-EVID-03, HV-STATE-01, HV-STATE-02, HV-MEM-01, HV-MEM-02, CM-ALERT-01, CM-ALERT-02, CM-ALERT-03, CM-I18N-01, CM-THEME-01, LOG-DASH-02, P2-DASH-01)는 RBAC 역할과 무관하게 해당 페이지 접근 권한이 있으면 동일하게 표시된다.

#### 5.1.1 Builder View 컴포넌트

| # | Component ID | 컴포넌트명 | OWNER | ADMIN | OPERATOR | VIEWER |
|---|---|---|---|---|---|---|
| 1 | BV-LAYOUT-01 | BuilderShell | V | V | V | H (Workflow 페이지 DENY 시) |
| 2 | BV-NAV-01 | SideNav | V | V | V | R (접근 불가 메뉴 hidden) |
| 3 | BV-REG-01 | PolicyRegistryPanel | V | V | H | H |
| 4 | BV-REG-02 | TemplateRegistryPanel | V | V | V | H |
| 5 | BV-REG-03 | EventTypeRegistryView | V | V | V | H |
| 6 | BV-REG-04 | FailureCodeRegistryView | V | V | V | H |
| 7 | BV-REG-05 | NodeRegistryPanel | V | V | V | H |
| 8 | BV-DEBUG-01 | TraceLogPanel | V | V | H | H |
| 9 | BV-DEBUG-02 | CostMeterWidget | V | V | R | H |
| 10 | BV-CONFIG-01 | ConfigEditorPanel | V | V (삭제 버튼 D) | R | H |

#### 5.1.2 Hologram View 컴포넌트

| # | Component ID | 컴포넌트명 | OWNER | ADMIN | OPERATOR | VIEWER |
|---|---|---|---|---|---|---|
| 11 | HV-LAYOUT-01 | HologramShell | V | V | V | V (READ 모드) |
| 12 | HV-CHAT-01 | ConversationPanel | V | V | V | R (메시지만 조회) |
| 13 | HV-INPUT-01 | ComposerBar | V | V | V | H (입력 불가) |
| 14 | HV-INPUT-02 | FileUploadDropzone | V | V | V | H |
| 15 | HV-INPUT-03 | MultimodalPreview | V | V | V | H |
| 16 | HV-APPR-01 | ApprovalCard | V | V (P2 승인 D) | D (승인 버튼 D) | H |
| 17 | HV-APPR-02 | ApprovalHistoryList | V | V | R | R |
| 18 | HV-COST-01 | CostWarningBanner | V | V | V | H |
| 19 | HV-COST-02 | CostBreakdownPopover | V | V | R | H |

#### 5.1.3 공통/CLI/대시보드 컴포넌트

| # | Component ID | 컴포넌트명 | OWNER | ADMIN | OPERATOR | VIEWER |
|---|---|---|---|---|---|---|
| 20 | CM-NAV-01 | ViewSwitcher | V | V | V (접근 불가 뷰 D) | D (Builder DENY) |
| 21 | CM-NAV-02 | SettingsPanel | V | V (시스템 삭제 D) | R | H |
| 22 | CLI-CMD-01 | CLIPrompt | V | V | V | H |
| 23 | CLI-CMD-02 | CLIOutput | V | V | V | R |
| 24 | CLI-CMD-03 | CLIProgressBar | V | V | V | H |
| 25 | CLI-CMD-04 | CLIApprovalPrompt | V | V (P2 D) | D | H |
| 26 | LOG-DASH-01 | LogDashboard | V | V | H | H |

### 5.2 RBAC 가시성 규칙 요약

```typescript
/**
 * 컴포넌트 RBAC 가시성 상태
 */
export type RBACVisibility = 'visible' | 'disabled' | 'readonly' | 'hidden';

/**
 * 컴포넌트별 RBAC 규칙 정의
 */
export interface ComponentRBACRule {
  componentId: string;
  rules: Record<RBACRole, RBACVisibility>;
  /** 조건부 규칙 (예: P2 도메인일 때 추가 제한) */
  conditionalRules?: {
    condition: string;
    overrides: Partial<Record<RBACRole, RBACVisibility>>;
  }[];
}
```

### 5.3 조건부 가시성 규칙 (Conditional)

| 컴포넌트 | 조건 | ADMIN 오버라이드 | OPERATOR 오버라이드 |
|---------|------|----------------|-------------------|
| HV-APPR-01 (ApprovalCard) | P2 도메인 승인 요청 | 승인 버튼 `disabled` | 전체 `disabled` |
| BV-CONFIG-01 (ConfigEditorPanel) | Constitution 편집 모드 | `hidden` (OWNER만) | `hidden` |
| CM-NAV-02 (SettingsPanel) | 비용 상한 변경 탭 | `visible` | `hidden` |
| CLI-CMD-04 (CLIApprovalPrompt) | 고위험 실행 승인 | `disabled` | `disabled` |

---

## 6. Approval Gate HOLD 전환 UI

> **출처**: D2.0-08 §8 (승인 게이트), D2.0-07 §4.3 (타임아웃), R-61-8 (명시적 승인/거절 필수)
> **LOCK (D2.0-07 §4.3): 일반 승인 10분 / HITL 고위험 5분 → 미응답 시 자동 deny** (L18)

### 6.1 Approval Gate 진입 조건

상태 머신 `UI_S5_AWAIT_APPROVAL` 전이가 발생하는 경우:

| # | 트리거 | 설명 | 타임아웃 |
|---|--------|------|---------|
| 1 | P2 도메인 활성화 | P2 도메인 작업 진입 시 OWNER 승인 필수 | HITL 5분 |
| 2 | 정책 변경 | Constitution/Policy 변경 요청 | 일반 10분 |
| 3 | 비용 임계 초과 | 월/일 비용 상한 80%+ 도달 시 경고 → 100% 초과 시 차단 | 일반 10분 |
| 4 | 고위험 실행 | 파괴적/영구적 변경(파일 삭제, 외부 송신 등) | HITL 5분 |
| 5 | Agent 권한 초과 | AGENT가 허용 범위 밖 실행 시도 → OWNER 상신 | HITL 5분 |
| 6 | 자율 운영 수준 변경 | L0~L2 수준 변경 요청 | 일반 10분 |

### 6.2 Approval Card UI 명세 (HV-APPR-01)

> **R-61-8 준수**: 승인/거절이 명시적 UI 액션으로만 가능. **자동 승인 절대 금지**.

```
┌─────────────────────────────────────────────┐
│  🛡️ 승인 요청                    [HOLD]     │
├─────────────────────────────────────────────┤
│  사유: {approval_reason}                     │
│  범위: {approval_scope}                      │
│  대안: {alternative_action}                  │
│  요청자: {requester} ({role})                │
│  대상: {target_resource}                     │
├─────────────────────────────────────────────┤
│  ⏱️ 남은 시간: {mm:ss}                      │
│  ████████████░░░░ {progress}%               │
├─────────────────────────────────────────────┤
│  [ ✅ 승인 ]        [ ❌ 거절 ]              │
│                     [ 📋 상세 보기 ]          │
└─────────────────────────────────────────────┘
```

**카드 구성 요소**:

| 영역 | 설명 | 필수 |
|------|------|------|
| **사유 (Reason)** | 승인이 필요한 이유 텍스트 | 필수 |
| **범위 (Scope)** | 영향을 받는 리소스/도메인 범위 | 필수 |
| **대안 (Alternative)** | 승인 거부 시 대안 행동 안내 | 필수 |
| **타이머** | 남은 시간 프로그레스 바 (L18 기반) | 필수 |
| **승인 버튼** | 명시적 클릭으로만 승인 (R-61-8) | 필수 |
| **거절 버튼** | 명시적 클릭으로만 거절 (R-61-8) | 필수 |
| **상세 보기** | 상세 정보 모달 링크 | 선택 |

### 6.3 타이머 동작 명세 (L18)

```typescript
interface ApprovalTimerConfig {
  /** HITL 고위험 타임아웃 (밀리초) — LOCK L18 */
  HITL_TIMEOUT_MS: 300_000;   // 5분
  /** 일반 승인 타임아웃 (밀리초) — LOCK L18 */
  NORMAL_TIMEOUT_MS: 600_000; // 10분
  /** 경고 표시 임계값 (남은 시간 비율) */
  WARNING_THRESHOLD: 0.2;     // 20% — 1분/2분 남았을 때 경고색 전환
}
```

**타이머 UI 전이**:

| 단계 | 남은 시간 | UI 변화 |
|------|----------|---------|
| 정상 | > 20% | 프로그레스 바 기본색 (`#F59E0B` 노란색) |
| 경고 | ≤ 20% | 프로그레스 바 위험색 (`#EF4444` 빨간색) + 펄스 애니메이션 |
| 만료 | 0 | 자동 deny → 카드 상태 `TIMEOUT_DENIED` → 붉은 배경 + "시간 초과로 자동 거절" 메시지 |

### 6.4 승인/거절 후 상태 전이

| 액션 | 현재 상태 | 다음 상태 | UI 변화 |
|------|----------|----------|---------|
| **승인 클릭** | UI_S5_AWAIT_APPROVAL | UI_S4_RUNNING (이전 상태 복원) | 카드 배경 → 녹색 (`#10B981`), "승인 완료" 토스트 |
| **거절 클릭** | UI_S5_AWAIT_APPROVAL | UI_S1_IDLE | 카드 배경 → 회색, "거절됨" 토스트 + 대안 행동 안내 |
| **타임아웃** | UI_S5_AWAIT_APPROVAL | UI_S7_RECOVERY (T-11) | 카드 배경 → 빨간 (`#EF4444`), "시간 초과 자동 거절" 토스트 |

### 6.5 RBAC 역할별 승인 버튼 상태

| 승인 유형 | OWNER | ADMIN | OPERATOR | VIEWER |
|----------|-------|-------|----------|--------|
| 일반 실행 승인 | 활성 | 활성 | 비활성 | 숨김 |
| P2 도메인 승인 | 활성 | 비활성 | 비활성 | 숨김 |
| 비용 상한 변경 | 활성 | 활성 | 비활성 | 숨김 |
| Constitution 편집 | 활성 | 비활성 | 비활성 | 숨김 |
| 고위험 실행 승인 | 활성 | 활성 | 비활성 | 숨김 |

---

## 7. RBAC 미들웨어/가드 설계

### 7.1 아키텍처 개요

```
┌────────────────────────────────────────────────────┐
│                   App Router                        │
│  ┌──────────────────────────────────────────────┐  │
│  │         RBACRouteGuard (라우트 가드)           │  │
│  │  ┌────────────────────────────────────────┐  │  │
│  │  │     Page Component                      │  │  │
│  │  │  ┌──────────────────────────────────┐  │  │  │
│  │  │  │  useRBAC Hook (컴포넌트 가드)     │  │  │  │
│  │  │  │  - checkAccess(componentId)       │  │  │  │
│  │  │  │  - getVisibility(componentId)     │  │  │  │
│  │  │  └──────────────────────────────────┘  │  │  │
│  │  └────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────┘  │
│                       ↑                             │
│              useAuthStore (Zustand)                  │
│              - currentRole: RBACRole                │
│              - permissions: Permission[]            │
│                       ↑                             │
│              6-2 Security Policy API                │
└────────────────────────────────────────────────────┘
```

### 7.2 RBACRouteGuard — React Router 라우트 가드

```typescript
import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '@/stores/useAuthStore';
import { RBACRole, RBAC_LEVEL } from '@/types/rbac';

interface RBACRouteGuardProps {
  /** 접근에 필요한 최소 역할 */
  minimumRole: RBACRole;
  /** 접근 거부 시 리다이렉트 경로 */
  fallbackPath?: string;
  /** 읽기 전용 모드 허용 역할 */
  readOnlyRoles?: RBACRole[];
}

/**
 * 라우트 레벨 RBAC 가드
 * - §4 매트릭스 기반 페이지 접근 제어
 * - DENY → fallbackPath로 리다이렉트 + failure_code: RBAC_PERMISSION_DENIED
 */
export function RBACRouteGuard({
  minimumRole,
  fallbackPath = '/dashboard',
  readOnlyRoles = [],
}: RBACRouteGuardProps) {
  const { currentRole } = useAuthStore();
  const userLevel = RBAC_LEVEL[currentRole];
  const requiredLevel = RBAC_LEVEL[minimumRole];

  if (!currentRole || userLevel === undefined || userLevel < requiredLevel) {
    // 접근 거부 — failure_code 기록
    logRBACDenied(currentRole, minimumRole);
    return <Navigate to={fallbackPath} replace />;
  }

  const isReadOnly = readOnlyRoles.includes(currentRole);
  return <Outlet context={{ isReadOnly }} />;
}
```

### 7.3 라우트 정의 + 가드 적용

```typescript
/**
 * 라우트별 RBAC 가드 매핑 — §4 매트릭스 기반
 */
const routes = [
  {
    path: '/dashboard',
    element: <RBACRouteGuard minimumRole={RBACRole.VIEWER} readOnlyRoles={[RBACRole.VIEWER]} />,
    children: [{ index: true, element: <DashboardPage /> }],
  },
  {
    path: '/chat',
    element: <RBACRouteGuard minimumRole={RBACRole.VIEWER} readOnlyRoles={[RBACRole.VIEWER]} />,
    children: [{ index: true, element: <ChatPage /> }],
  },
  {
    path: '/workflow',
    element: <RBACRouteGuard minimumRole={RBACRole.OPERATOR} />,
    children: [{ index: true, element: <WorkflowPage /> }],
  },
  {
    path: '/memory',
    element: <RBACRouteGuard minimumRole={RBACRole.OPERATOR} />,
    children: [{ index: true, element: <MemoryPage /> }],
  },
  {
    path: '/settings',
    element: <RBACRouteGuard minimumRole={RBACRole.OPERATOR} readOnlyRoles={[RBACRole.OPERATOR]} />,
    children: [{ index: true, element: <SettingsPage /> }],
  },
  {
    path: '/log',
    element: <RBACRouteGuard minimumRole={RBACRole.ADMIN} />,
    children: [{ index: true, element: <LogPage /> }],
  },
  {
    path: '/node-detail/:nodeId',
    element: <RBACRouteGuard minimumRole={RBACRole.OPERATOR} />,
    children: [{ index: true, element: <NodeDetailPage /> }],
  },
];
```

### 7.4 useRBAC Hook — 컴포넌트 레벨 가드

```typescript
import { useMemo } from 'react';
import { useAuthStore } from '@/stores/useAuthStore';
import { RBACRole, RBACVisibility, ComponentRBACRule } from '@/types/rbac';
import { COMPONENT_RBAC_RULES } from '@/config/rbacRules';

interface UseRBACReturn {
  /** 현재 사용자 역할 */
  role: RBACRole;
  /** 컴포넌트 가시성 확인 */
  getVisibility: (componentId: string) => RBACVisibility;
  /** 접근 가능 여부 (visible 또는 readonly) */
  canAccess: (componentId: string) => boolean;
  /** 활성화 여부 (visible만 true) */
  isEnabled: (componentId: string) => boolean;
  /** 최소 역할 요구 충족 여부 */
  hasMinRole: (minRole: RBACRole) => boolean;
  /** 승인 가능 여부 (승인 유형별) */
  canApprove: (approvalType: ApprovalType) => boolean;
}

/**
 * RBAC 컴포넌트 가드 Hook
 * - §5 매트릭스 기반 컴포넌트 가시성 제어
 * - 조건부 규칙(§5.3) 지원
 */
export function useRBAC(): UseRBACReturn {
  const { currentRole } = useAuthStore();

  const getVisibility = useMemo(() => {
    return (componentId: string): RBACVisibility => {
      const rule = COMPONENT_RBAC_RULES[componentId];
      if (!rule) return 'hidden'; // 규칙 미정의 컴포넌트는 fail-closed 기본 hidden (명시적 예외만 규칙 등록)
      return rule.rules[currentRole] ?? 'hidden';
    };
  }, [currentRole]);

  const canAccess = (componentId: string) => {
    const vis = getVisibility(componentId);
    return vis === 'visible' || vis === 'readonly';
  };

  const isEnabled = (componentId: string) => {
    return getVisibility(componentId) === 'visible';
  };

  const hasMinRole = (minRole: RBACRole) => {
    return RBAC_LEVEL[currentRole] >= RBAC_LEVEL[minRole];
  };

  const canApprove = (approvalType: ApprovalType) => {
    // §6.5 역할별 승인 버튼 상태 기반
    return APPROVAL_PERMISSION[approvalType].includes(currentRole);
  };

  return { role: currentRole, getVisibility, canAccess, isEnabled, hasMinRole, canApprove };
}
```

### 7.5 RBACGuard 래퍼 컴포넌트

```typescript
interface RBACGuardProps {
  componentId: string;
  children: React.ReactNode;
  /** hidden 대신 대체 UI 표시 */
  fallback?: React.ReactNode;
}

/**
 * 선언적 컴포넌트 RBAC 래퍼
 * 사용: <RBACGuard componentId="BV-CONFIG-01"><ConfigEditorPanel /></RBACGuard>
 */
export function RBACGuard({ componentId, children, fallback = null }: RBACGuardProps) {
  const { getVisibility } = useRBAC();
  const visibility = getVisibility(componentId);

  switch (visibility) {
    case 'hidden':
      return <>{fallback}</>;
    case 'disabled':
      return <div className="rbac-disabled" aria-disabled="true" inert>{children}</div>;
    case 'readonly':
      return <div className="rbac-readonly" data-readonly="true">{children}</div>;
    case 'visible':
    default:
      return <>{children}</>;
  }
}
```

### 7.6 RBAC CSS 클래스

```css
/* RBAC 비활성화 스타일 */
.rbac-disabled {
  pointer-events: none;
  opacity: 0.5;
  filter: grayscale(30%);
  cursor: not-allowed;
}

/* RBAC 읽기 전용 스타일 */
.rbac-readonly {
  pointer-events: none; /* 클릭 차단 */
  opacity: 0.85;
}
.rbac-readonly input,
.rbac-readonly textarea,
.rbac-readonly select,
.rbac-readonly button {
  pointer-events: none;
  background-color: var(--color-surface-disabled, #2a2a2a);
}
```

---

## 8. 6-1 ↔ 6-2 동기화 (W-3)

> **출처**: 종합계획서 §5.2 (W-3), CONFLICT_LOG W-3 RESOLVED
> **상태**: RESOLVED (S7-4: 6-1 RBAC UI 표시, 6-2 RBAC 정책 정의)

### 8.1 역할 분담

| 도메인 | 역할 | 소유 데이터 |
|--------|------|-----------|
| **6-1 (UI/UX System)** | RBAC **UI 표시** — 화면 접근 제한, 버튼 비활성화 | `COMPONENT_RBAC_RULES`, 페이지 접근 매트릭스, Approval Card UI |
| **6-2 (Security)** | RBAC **정책 정의** — 인증/인가 규칙, 보안 체크리스트 | `RBACPolicy`, 역할별 Permission, 토큰 발급/검증 |

### 8.2 데이터 흐름

```
6-2 (Security)                        6-1 (UI/UX System)
┌─────────────────┐                   ┌─────────────────┐
│ RBACPolicy      │──── IPC ────────→ │ useAuthStore    │
│ - roles[]       │   vamos:rbac:get  │ - currentRole   │
│ - permissions[] │                   │ - permissions[] │
│ - tokenPayload  │                   │                 │
└─────────────────┘                   │       ↓         │
                                      │ useRBAC Hook    │
       정책 변경 시                    │ - getVisibility │
┌─────────────────┐                   │ - canApprove    │
│ PolicyUpdate    │── IPC Event ────→ │                 │
│ - updatedRoles  │ vamos:rbac:update │ → UI 즉시 반영  │
└─────────────────┘                   └─────────────────┘
```

### 8.3 IPC 인터페이스 정의

```typescript
/** 6-2 → 6-1: RBAC 정책 조회 응답 */
interface RBACPolicyResponse {
  role: RBACRole;
  permissions: Permission[];
  /** 세션 만료 시각 (ISO 8601) */
  sessionExpiresAt: string;
  /** 역할 변경 시각 (캐시 무효화용) */
  roleUpdatedAt: string;
}

/** 6-2 → 6-1: RBAC 정책 변경 이벤트 */
interface RBACPolicyUpdateEvent {
  type: 'vamos:rbac:update';
  payload: {
    updatedRole: RBACRole;
    updatedPermissions: Permission[];
    reason: string;
  };
}
```

### 8.4 동기화 규칙

| 규칙 | 설명 |
|------|------|
| **정책 우선** | 6-2 보안 규칙이 6-1 UI 규칙보다 우선 (AUTHORITY_CHAIN §5.3) |
| **즉시 반영** | 6-2에서 역할/권한 변경 시 6-1 UI 즉시 업데이트 (Zustand subscribe) |
| **캐시 무효화** | `roleUpdatedAt` 변경 감지 시 `COMPONENT_RBAC_RULES` 캐시 폐기 + 재계산 |
| **세션 만료** | `sessionExpiresAt` 도달 시 자동 잠금 화면 표시 (D2.0-07 §3.7: 30분 미사용 자동 잠금) |
| **충돌 기록** | 6-2 정책과 6-1 UI 규칙 불일치 발견 시 CONFLICT_LOG에 등재 |

---

## 9. STEP7-C 매핑

> **출처**: 06_accessibility/_index.md §9 (STEP7-C 매핑 현황)

### 9.1 RBAC 관련 STEP7-C 항목

| # | 항목 ID | Part | 설명 | Phase | 본 문서 매핑 |
|---|---------|------|------|-------|------------|
| 1 | **S7C-077** | Part 8 | MCP 도구 관리 UI — RBAC 연동 권한 설정 | Phase 2 | §5.1 컴포넌트 규칙 (V2 범위) |
| 2 | **S7C-081** | Part 9 | 3-Gate 상태 표시기 — Policy/Cost/Evidence 색상+형태 구분 | Phase 1 | §6 Approval Gate (Gate 상태와 RBAC 역할별 가시성 연동) |

### 9.2 RBAC 간접 연관 항목

| # | 항목 ID | 설명 | 본 문서 관련 |
|---|---------|------|------------|
| 3 | S7C-071 | 프로필/계정 설정 — 선호 언어, 시간대, 응답 스타일 | §4 SettingsPage RBAC (OPERATOR=READ) |
| 4 | S7C-072 | 메모리 관리 UI — 저장 메모리 목록/편집/삭제/검색 | §4 MemoryPage RBAC (VIEWER=DENY) |
| 5 | S7C-097 | 다크모드/라이트모드 | §5 CM-THEME-01 (RBAC 무관) |

---

## 10. 검증 체크리스트

| # | 검증 항목 | 상태 | 근거 |
|---|----------|------|------|
| 1 | RBAC 4단계가 Part2 §6.1.8 정본과 일치 (LOCK L10) | PASS | §3.1 역할 테이블이 Part2 §6.1.8 원문 그대로 |
| 2 | 페이지별 접근 매트릭스(7페이지 x 4역할) 완성 | PASS | §4.1 매트릭스 28셀 전체 정의 |
| 3 | Approval Gate 타임아웃이 L18(HITL 5분/일반 10분) 준수 | PASS | §6.3 타이머 명세에 HITL_TIMEOUT_MS=300000, NORMAL_TIMEOUT_MS=600000 |
| 4 | R-61-8 준수: 승인/거절이 명시적 UI 액션으로만 가능(자동 승인 금지) | PASS | §6.2 Approval Card 구조에 명시적 승인/거절 버튼만 존재, 자동 승인 경로 없음 |
| 5 | W-3(6-1 ↔ 6-2 RBAC 동기화) 인터페이스 정의 | PASS | §8 IPC 인터페이스 + 동기화 규칙 정의 |
| 6 | STEP7-C RBAC 관련 항목 매핑 | PASS | §9 S7C-077/081 + 간접 3건 매핑 |
| 7 | LOCK 변경 없음 | PASS | L10, L18 참조만, 재정의 없음 |

---

## 부록 A. CONFLICT/LOCK 보고

### LOCK 참조 현황

| LOCK ID | 항목 | 본 문서 참조 위치 | 변경 여부 |
|---------|------|-----------------|----------|
| L10 | RBAC 4단계 | §2, §3, §4, §5 전체 | 변경 없음 (참조만) |
| L18 | 승인 타임아웃 | §6.1, §6.3 | 변경 없음 (참조만) |
| L1 | UI 9-State | §6.4 (UI_S5_AWAIT_APPROVAL) | 변경 없음 (참조만) |

### CONFLICT 발견 현황

- 발견 0건 / 해소 0건 / OPEN 0건

---

*End of Document*
