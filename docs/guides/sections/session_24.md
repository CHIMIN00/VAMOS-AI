---
session: 24
sections: [30]
status: complete
---

# §30. UI/UX — 사용자 인터페이스

> VAMOS AI 시스템에서 사용자가 실제로 보고, 누르고, 상호작용하는 "화면"에 대한 모든 것을 다룹니다.
> [근거: D2.0-08 전체]

---

## 일상 비유로 이해하기

UI/UX는 **자동차의 계기판과 핸들**과 같습니다.

- 엔진(ORANGE CORE)이 아무리 좋아도, 계기판(UI)이 엉망이면 운전자(사용자)는 속도도 모르고, 연료도 모릅니다
- VAMOS의 UI는 **"AI가 지금 무엇을 하고 있는지, 왜 그렇게 했는지, 얼마나 비용이 드는지"**를 항상 보여주는 투명한 계기판입니다
- 만드는 사람(개발자)에게는 **정비소 진단기**(Builder View)를, 쓰는 사람(일반 사용자)에게는 **깔끔한 내비게이션**(Hologram View)을 제공합니다

---

## §30.1 설계 철학 7원칙

> VAMOS UI/UX를 설계할 때 반드시 지켜야 하는 7가지 핵심 원칙입니다.
> [근거: D2.0-08 §1]

### 비유: 좋은 병원의 7가지 약속

| 원칙 | 비유 | 설명 |
|------|------|------|
| ① 구조 가시성 | 병원 전광판에 대기순번/진료실 표시 | 사용자가 "결과"뿐 아니라 "왜 그런 결과가 나왔는지"를 항상 확인 가능 |
| ② 이중 모드 | 의사용 차트 vs 환자용 안내문 | Builder View(만드는 사람)와 Hologram View(쓰는 사람) 분리 |
| ③ 근거 투명성 | 처방전에 약 이유 기재 | AI 답변에 인용/출처/근거(QoD 포함) 항상 접근 가능 |
| ④ 오케스트레이션 고정 | 처방 확정 후 임의 변경 불가 | Decision Lock(결정 잠금) 이후 결론 변경 UI 제공 금지 |
| ⑤ 승인/비용/정책 UI 반영 | 고가 시술 전 동의서 | 승인 필요 시 HOLD 전환, 비용 초과 시 경고/차단 |
| ⑥ 프레임워크 무관 UI 고정 | 어떤 엔진이든 같은 계기판 | LangGraph든 다른 엔진이든 Trace/Approval/Cost UI 동일 유지 |
| ⑦ P2/Hard loop/Template 표시 | 위험 약물은 별도 표시 | P2 활성 상태, 재시도 루프, 템플릿 ID를 UI에 명시 |

### 7원칙 상세

**① 구조 가시성 (Observability First)** — Builder는 전체 시스템 관측(Trace/Graph/Logs)을 최우선으로, Hologram은 관측 정보를 "필요할 때만" 노출합니다. [근거: D2.0-08 §1.1]

**② 이중 모드 (Two Views, One System)** — 두 뷰는 동일한 run/trace/decision을 공유하고, **표현 방식만 다릅니다**. [근거: D2.0-08 §1.2]

**③ 근거 투명성 (Evidence Transparency)** — 출처 리스트 + 인용 점프 + QoD(상/중/하)를 기본 제공합니다. [근거: D2.0-08 §1.3]

**④ 오케스트레이션 고정 (Decision Lock 제약)** — 재시도/재생성은 "근거/실행/포맷" 축 수정에 한정되며, 결론 변경 버튼은 제공하지 않습니다. **변경 불가** [근거: D2.0-08 §1.4]

**⑤ 승인/비용/정책 UI 반영** — 승인 필요(P2/정책 변경/비용 임계)는 실행을 HOLD로 전환하고, 명시적 승인/거절을 받습니다. [근거: D2.0-08 §1.5]

**⑥ 프레임워크 무관 UI 고정** — 어떤 실행 엔진을 쓰더라도 3가지는 동일 유지: (1) Trace 타임라인, (2) Approval 카드, (3) 비용 경고/차단 토스트. **LOCK** [근거: D2.0-08 §1.6]

**⑦ P2/Hard loop/Template 표시** — P2 기본 OFF, 활성 시 승인 카드에 명시. Hard loop는 승인 없이 UI에서 선택 불가(비활성). [근거: D2.0-08 §1.7]

### 핵심 요약 (3줄)
1. VAMOS UI는 "투명성 + 이중 모드 + 결정 잠금"을 3대 축으로 설계됩니다
2. 결론이 확정(Decision Lock)되면 UI에서 결론 변경이 불가합니다 (변경 불가)
3. 어떤 실행 엔진을 쓰더라도 Trace/Approval/Cost UI는 동일하게 유지됩니다

---

## §30.2 Builder View (만드는 사람용)

> 시스템을 만들고, 설정하고, 디버깅하는 사람을 위한 "정비소 진단기" 화면입니다.
> [근거: D2.0-08 §2.1]

### 비유: 자동차 정비소의 진단 장비

일반 운전자는 속도계만 보면 되지만, 정비사는 엔진 회전수, 배기가스 수치, 센서 데이터를 모두 봐야 합니다. Builder View는 바로 이 **정비사의 진단 장비**입니다.

### 목적과 대상

| 항목 | 내용 |
|------|------|
| 목적 | ORANGE CORE ↔ BLUE NODE 내부 흐름 시각화, 실행 제어, 디버깅/감사 |
| 대상 | 시스템 관리자, 고급 사용자, Debug Mode 사용자 |
| 별칭 | The Cockpit (조종석) |

### Builder View 주요 구성

| 패널 | 역할 | 구성 요소 |
|------|------|----------|
| 좌측 (Navigation) | 리소스 탐색 + 작업 컨텍스트 | Projects > Sessions > Runs, Registry, Storage, Policy 스냅샷 |
| 중앙 (Main Canvas) | 실행 흐름 시각화 + 편집 | Graph(ORANGE=⬢, BLUE=●), 툴바(실행/중지/스텝), Node Inspector |
| 우측 (Control) | 이벤트/승인/비용/메모리 제어 | Logs, Approval, Cost, Memory 탭 |

### Builder View 사용자 행동 예시 (10+건)

| # | 사용자 행동 | 시스템 반응 | 이벤트 |
|---|-----------|-----------|--------|
| 1 | [Run] 클릭 | Graph 경로 활성화 | `ui.builder.run.started` |
| 2 | ORANGE CORE 노드 클릭 | 내부 상태 + Decision 표시 | `ui.builder.node.inspected` |
| 3 | Approval Approve | 잠금 해제, 실행 재개 | `ui.builder.approval.granted` |
| 4 | Approval Deny | 실행 중단, Red 표시 | `ui.builder.approval.denied` |
| 5 | Cost Force Downshift | 모델/범위 축소 | `ui.builder.cost.mode_changed` |
| 6 | Memory 후보 제외 | 저장 대상 제외 | `ui.builder.memory.candidate_excluded` |
| 7 | Logs Error 필터 | 에러 구간 하이라이트 | `ui.builder.log.filtered` |
| 8 | Graph Step Over | 다음 노드 실행 후 일시정지 | `ui.builder.debug.step_over` |
| 9 | 정책 편집 시도 | 승인 필요 시 편집 잠금 | `ui.builder.policy.edit.attempted` |
| 10 | Simulate 실행 | Gate/Decision 프리뷰 | `ui.builder.simulate.started` |

[근거: D2.0-08 §2.1.3]

### 핵심 요약 (3줄)
1. Builder View는 VAMOS의 내부 동작을 모두 볼 수 있는 "조종석"입니다
2. 좌측(탐색) + 중앙(그래프/편집) + 우측(로그/승인/비용/메모리) 3단 구조입니다
3. 실행, 디버깅, 정책 편집, 시뮬레이션 등 관리자 기능을 제공합니다

---

## §30.3 Hologram View (사용하는 사람용)

> 일반 사용자가 AI와 대화하고 결과물을 받는 "깔끔한 내비게이션" 화면입니다.
> [근거: D2.0-08 §2.2]

### 비유: 자동차 내비게이션

내비게이션은 복잡한 GPS 위성 데이터를 숨기고, 사용자에게 **"다음 교차로에서 좌회전"**만 알려줍니다. Hologram View도 마찬가지로 복잡한 내부 구조를 숨기되, **필요할 때** 근거/비용/승인을 보여줍니다.

### 목적과 대상

| 항목 | 내용 |
|------|------|
| 목적 | 대화/멀티모달 입력/산출물 소비를 몰입형으로 제공 |
| 대상 | 일반 사용자, 집중 모드 사용자 |
| 별칭 | The Experience (경험) |

### Hologram View 주요 구성

| 패널 | 역할 | 구성 요소 |
|------|------|----------|
| 좌측 (Timeline) | 세션 기록 + 도메인 표시 | 세션 리스트, 활성 BLUE NODE, Pipeline 타임라인 |
| 중앙 (Stream Canvas) | 대화 + 산출물 렌더링 | User/AI 대화, Artifact, 입력창(텍스트+📎+🎤+📷) |
| 우측 (Glass HUD) | Evidence/Cost/Approval | 필요 시만 노출되는 카드 |

### 우측 HUD의 3가지 카드

| 카드 | 내용 | 표시 조건 |
|------|------|----------|
| **Evidence (근거)** | Verification Badge — VERIFIED(초록, ≥0.8) / PARTIAL(노랑, 0.5~0.8) / UNVERIFIED(회색, <0.5) | 항상 접근 가능 |
| **Cost (비용)** | 임계치 근접 시 게이지 표시 (V1/V2/V3) | 임계치 근접 시만 |
| **Approval (승인)** | 승인 필요 시 우측 슬라이드 인 | 승인 필요 시만 |

[근거: D2.0-08 §2.2.2]

### 핵심 요약 (3줄)
1. Hologram View는 일반 사용자를 위한 깔끔한 대화형 인터페이스입니다
2. 복잡한 내부 구조를 숨기되, 근거/비용/승인은 필요할 때 즉시 확인 가능합니다
3. 중앙 대화 영역이 가장 넓고, 좌측은 타임라인, 우측은 HUD 카드입니다

---

## §30.4 3-Panel Layout (좌/중/우 패널)

> Builder View와 Hologram View 모두 적용되는 **3단 패널 공통 규칙**입니다.
> [근거: D2.0-08 §3]

### 비유: 신문의 3단 구성

신문이 "사이드바(목차) + 본문(기사) + 보조란(광고/참조)"로 나뉘듯, VAMOS도 화면을 3개로 나눕니다.

### 3단 패널 구조

```
┌──────────────┬────────────────────────┬──────────────────┐
│  좌 (Left)   │     중 (Center)        │   우 (Right)     │
│  250~300px   │     유동(Flex)          │  350~400px       │
│              │                        │  접기 가능       │
├──────────────┼────────────────────────┼──────────────────┤
│ Builder:     │ Builder:               │ Builder:         │
│ Resource/    │ Graph/Editor/          │ Logs/Approval/   │
│ Registry/    │ Simulate               │ Cost/Memory 탭   │
│ Policy       │                        │                  │
├──────────────┼────────────────────────┼──────────────────┤
│ Hologram:    │ Hologram:              │ Hologram:        │
│ Pipeline     │ 대화 + 인라인          │ Evidence/Cost/   │
│ Timeline +   │ 산출물                 │ Approval HUD     │
│ Self-check   │                        │ 카드             │
└──────────────┴────────────────────────┴──────────────────┘
```

### 버전별 레이아웃 제약

| 버전 | 레이아웃 | 비고 |
|------|---------|------|
| V0 | CLI 기반 텍스트 UI | 화면 레이아웃 없음 |
| V1 | 데스크톱 전용 (min-width: 1280px) **LOCK** | 반응형 미지원 |
| V2 | 768px breakpoint 추가 | 사이드바 오버레이 전환 |
| V3 | 반응형 레이아웃 / 모바일 대응 | D8-V3-SLOT-02 |

- Tauri 윈도우 기본 크기: `1440 × 900`, 최소 크기: `1280 × 720` **LOCK**

[근거: D2.0-08 §3.1]

### UI 고정 규칙 (FREEZE)

- **옵션 A (고정 Dock 중심)** — ✅ DEFAULT / FREEZE
  - Builder: 우측 패널을 **고정 탭** 구조로 운영
  - Hologram: 우측 HUD를 **기본 노출(고정/반고정)**
  - Approval/Cost/Evidence는 접근 경로가 항상 **1-click 이내** **변경 불가**
- **옵션 B (오버레이/접기 중심)** — 🧷 KEEP (대안, 기본값 아님)
  - 차기 실험/전환 후보로 보존

[근거: D2.0-08 §9]

### 핵심 요약 (3줄)
1. 좌(탐색) + 중(핵심작업) + 우(제어/관측)의 3단 고정 구조입니다
2. V1은 데스크톱 전용(1280px 이상), V2부터 반응형을 지원합니다
3. 우측 패널은 고정 Dock 방식이 기본값(FREEZE)입니다

---

## §30.5 UI 9-State 상태 머신 (S0_BOOT ~ S8_ARCHIVED)

> UI 화면이 어떤 상태에 있을 수 있는지를 정의한 "상태 머신(State Machine)"입니다.
> [근거: D2.0-08 §4.1, §4.2]

### 비유: 식당 주문 상태

음식 주문도 상태가 있습니다: 입장 → 메뉴 고르기 → 주문 → 조리중 → 서빙 대기 → 식사 → 계산 → 퇴장. VAMOS UI도 비슷한 "상태 흐름"을 가집니다.

### 9가지 UI 상태

| 상태 | 이름 | 비유 | 설명 |
|------|------|------|------|
| **UI_S0_BOOT** | 앱 초기화 | 식당 문 열기 | 앱/세션이 시작되는 단계 |
| **UI_S1_IDLE** | 입력 대기 | 메뉴판 보기 | 사용자의 입력을 기다리는 상태 |
| **UI_S2_EDITING** | 편집 중 | 메뉴 고르는 중 | Builder에서 설정/정책 편집 중 |
| **UI_S3_READY** | 실행 가능 | 주문 준비 완료 | 사전 점검 통과, 실행 가능 |
| **UI_S4_RUNNING** | 실행 중 | 주방에서 조리 중 | AI가 작업을 처리하는 중 (trace 활성) |
| **UI_S5_AWAIT_APPROVAL** | 승인 대기 | "이 요리 괜찮으세요?" | 사용자 승인이 필요한 상태 (HOLD) |
| **UI_S6_PRESENTING** | 결과 표시 | 음식 서빙됨 | 출력/근거/컴플라이언스 표시 |
| **UI_S7_RECOVERY** | 복구 중 | "죄송합니다, 다시 만들겠습니다" | 실패/폴백/재시도 안내 |
| **UI_S8_ARCHIVED** | 아카이브 | 영수증 보관 | 리뷰용 아카이브 상태 |

### 주요 상태 전이 (흐름)

```
UI_S0_BOOT → UI_S1_IDLE (초기화 완료)
UI_S1_IDLE → UI_S4_RUNNING (전송/실행)
UI_S4_RUNNING → UI_S5_AWAIT_APPROVAL (승인 필요 시)
UI_S5_AWAIT_APPROVAL → UI_S4_RUNNING (승인 완료)
UI_S4_RUNNING → UI_S7_RECOVERY (실패 발생)
UI_S7_RECOVERY → UI_S4_RUNNING (재시도/대안 선택)
UI_S4_RUNNING → UI_S6_PRESENTING (출력 준비됨)
UI_S6_PRESENTING → UI_S8_ARCHIVED (완료)
```

### Decision Lock UI 제약 **변경 불가**

- Decision Lock 이후 "결론 변경" UI 제공 금지
- 재시도는 "근거/실행/포맷" 축에서만 허용 (동일 의도/동일 결론 유지)

[근거: D2.0-08 §4.3]

### I-10 UI 오케스트레이션 (DEC-016 확정)

Core 상태와 UI 상태를 동기화하여 사용자가 항상 시스템 현황을 알 수 있도록 보장합니다.

| UI 상태 | 표시 조건 | 허용 액션 |
|---------|----------|----------|
| UIS1IDLE | 입력 대기 중 | 입력 가능 |
| UIS2PROCESSING | Core 처리 중 | 취소 가능 |
| UIS3LOCKED | Decision Lock 중 | 취소 가능, 수정 불가 |
| UIS4RUNNING | 실행 단계 | 실행 취소 가능 |
| UIS5AWAITAPPROVAL | 승인 대기 | 승인/거절 가능 |
| UIS6PRESENTING | 결과 표시 | 재생성/저장/피드백 가능 |

- 상태 업데이트: **이벤트 기반** (폴링 금지) **LOCK**
- 전이 지연 허용 최대값: **500ms** (이상 시 로딩 스피너)
- Core↔UI 불일치 감지 시: `ui.core.state.mismatch` 이벤트 + 자동 동기화

[근거: D2.0-08 §4.4, DEC-016]

### 핵심 요약 (3줄)
1. UI는 S0_BOOT(시작)부터 S8_ARCHIVED(완료)까지 9가지 상태를 순환합니다
2. Decision Lock 이후에는 결론 변경 UI가 제공되지 않습니다 (변경 불가)
3. Core↔UI 상태 동기화는 이벤트 기반(폴링 금지)이며 500ms 이내 반영됩니다

---

## §30.6 Pipeline ↔ UI 상태 매핑

> 백엔드 파이프라인의 9단계(S0~S8)와 UI 상태가 어떻게 연결되는지 보여줍니다.
> [근거: D2.0-08 §4.6, D8-M11]

### 비유: 택배 배송 추적

택배 앱에서 "출고 → 이동 중 → 배달 중 → 배달 완료"를 보여주듯, VAMOS UI는 백엔드 파이프라인의 진행 상태를 사용자에게 보여줍니다.

### 매핑 테이블

| Pipeline (02 정본) | 단계명 | UI 상태 | 사용자에게 보이는 표시 |
|-------------------|--------|---------|---------------------|
| S0_RECEIVED | 인식/접수 | UI_S4_RUNNING | "요청 수신됨" |
| S1_INTENT_PARSED | 인식/접수 | UI_S4_RUNNING | "의도 분석 완료" |
| S2_EVIDENCE_READY | 추론/계획 | UI_S4_RUNNING | "근거 수집 완료" |
| S3_DECISION_LOCKED | 추론/계획 | UI_S4_RUNNING | "결정 잠금" |
| S4_EXECUTING | 실행 | UI_S4_RUNNING | "실행 중" |
| S5_OUTPUT_READY | 실행 완료 | UI_S6_PRESENTING | "출력 준비됨" |
| S6_SELF_CHECKED | 검증 | UI_S6_PRESENTING | "자기검증 완료" |
| S7_MEMORY_COMMITTED | 저장 | UI_S6_PRESENTING | "메모리 저장됨" |
| S8_DONE | 완료 | UI_S8_ARCHIVED | "완료" |

### 정본 우선순위

- §4.1(9-state)이 **UI 설계 정본**
- §4.4(6-state)는 Core 연동 런타임 뷰
- Pipeline S0~S8은 백엔드 정본 (02 문서)

[근거: D2.0-08 §4.5, §4.6]

### 핵심 요약 (3줄)
1. 백엔드 S0~S4까지는 UI에서 "실행 중(RUNNING)"으로 표시됩니다
2. S5~S7은 "결과 표시(PRESENTING)", S8은 "완료(ARCHIVED)"입니다
3. UI는 사용자 친화적 메시지("의도 분석 완료" 등)로 변환하여 보여줍니다

---

## §30.7 React 컴포넌트 목록 (~44개)

> VAMOS UI를 구성하는 React 컴포넌트 44개의 전체 목록입니다.
> [근거: D2.0-08 §10.4]

### 비유: 레고 블록 세트

44개의 컴포넌트는 **레고 블록**과 같습니다. 각각 고유한 역할(버튼, 패널, 카드 등)이 있고, 이 블록들을 조합하면 Builder View, Hologram View, CLI 등의 완성된 화면이 만들어집니다.

### 컴포넌트 ID 규칙

`{View}-{Category}-{번호}` 형식:
- **BV** = Builder View, **HV** = Hologram View, **CM** = 공통
- **CLI** = CLI, **LOG** = 로그 대시보드, **P2** = P2 도메인

### 카테고리별 컴포넌트 요약

| 카테고리 | 컴포넌트 수 | V1 필수(★) | 대표 컴포넌트 |
|---------|-----------|-----------|-------------|
| Builder View (BV) | 12개 | 12개 | BuilderShell, SideNav, PolicyRegistryPanel, PipelineStatusBar, TraceLogPanel |
| Hologram View (HV) | 18개 | 15개 | HologramShell, ConversationPanel, MessageBubble, ComposerBar, EvidencePanel, ApprovalCard |
| 공통 (CM) | 7개 | 6개 | AlertModal, ToastNotification, ViewSwitcher, SettingsPanel, LanguageSelector |
| CLI (CLI) | 4개 | 4개 | CLIPrompt, CLIOutput, CLIProgressBar, CLIApprovalPrompt |
| 대시보드 (LOG/P2) | 3개 | 2개 | LogDashboard, TraceTimeline, DomainDashboard |
| **합계** | **44개** | **39개(★)** | — |

### V1 필수 컴포넌트 주요 목록 (39개)

**Builder View (12개):**
BuilderShell, SideNav, PolicyRegistryPanel, TemplateRegistryPanel, EventTypeRegistryView, FailureCodeRegistryView, NodeRegistryPanel, PipelineStatusBar, DecisionLockBanner, TraceLogPanel, CostMeterWidget, ConfigEditorPanel

**Hologram View (15개):**
HologramShell, ConversationPanel, MessageBubble, StreamingIndicator, ComposerBar, FileUploadDropzone, EvidencePanel, EvidenceBadge, WatermarkBadge, ApprovalCard, ApprovalHistoryList, CostWarningBanner, AgentStatusIndicator, ProgressTracker, MemoryCandidatePanel

**공통 (6개):**
AlertModal, ApprovalSlidePanel, ToastNotification, ViewSwitcher, SettingsPanel, LanguageSelector

**CLI (4개):**
CLIPrompt, CLIOutput, CLIProgressBar, CLIApprovalPrompt

**대시보드 (2개):**
LogDashboard, TraceTimeline

[근거: D2.0-08 §10.4, ADD D8-01]

### 핵심 요약 (3줄)
1. VAMOS UI는 총 44개 React 컴포넌트로 구성되며, V1에서 39개가 필수입니다
2. 컴포넌트 ID는 `{View}-{Category}-{번호}` 규칙을 따릅니다
3. Builder 12개 + Hologram 18개 + 공통 7개 + CLI 4개 + 대시보드 3개입니다

---

## §30.8 Custom Hooks & Zustand Stores

> React에서 사용하는 커스텀 훅(Hook)과 상태 관리 저장소(Store)의 주요 목록입니다.
> [근거: D2.0-08 §11-A, §4.4, P7-UIS]

### 비유: 주방의 도구와 냉장고

- **Custom Hook** = 주방 도구 (반복해서 쓰는 특수 기능을 모아둔 것)
- **Zustand Store** = 냉장고 (여러 사람이 공유하는 데이터를 보관하는 곳)

### 주요 Custom Hooks

| Hook 이름 | 용도 | 관련 컴포넌트 |
|----------|------|-------------|
| `useAutoResize` | textarea 자동 확장 (1줄→10줄) | ComposerBar (S7C-023) |
| `useTokenCount` | 실시간 토큰 수 계산 | 토큰 카운터 (S7C-029) |
| `useCostPreview` | 비용 미리보기 계산 | 비용 표시 (S7C-030) |
| `useKeyboardShortcut` | 키보드 단축키 관리 | 전역 (S7C-006) |
| `useStreamingResponse` | Streamable HTTP 스트리밍 처리 | StreamingIndicator (S7C-038) |
| `useApprovalState` | 승인 상태 관리 | ApprovalCard |
| `usePipelineStatus` | 파이프라인 S0~S8 상태 추적 | PipelineStatusBar |

### 주요 Zustand Stores

| Store 이름 | 관리 데이터 | 관련 섹션 |
|-----------|-----------|----------|
| `useCoreStateStore` | Core↔UI 상태 동기화 (UIS1~6) | §4.4 |
| `useCostStore` | 비용 데이터 (현재/상한/모드) | §23.1 |
| `useApprovalStore` | 승인 대기 큐, 승인/거절 이력 | §8 |
| `useMemoryStore` | 메모리 후보, L0/L1/L2 상태 | §5.7 |
| `useEvidenceStore` | 근거/QoD 데이터, 출처 목록 | §2.2 |
| `useSessionStore` | 세션 정보, trace_id, 히스토리 | §2.2 |
| `useThemeStore` | 다크/라이트 모드, 테마 설정 | §10.1 |
| `useI18nStore` | 언어 설정 (ko-KR/en-US/ja-JP) | MOD-022 |

### 상태 관리 원칙

- Core → UI 상태 업데이트: **이벤트 기반** (LogEvent 스트림 구독, 폴링 금지) **LOCK**
- 위젯별 독립 상태 + Core 데이터 바인딩 (P7-UIS)
- Builder/Hologram WebSocket 실시간 동기화 (Latency < 100ms)

[근거: D2.0-08 §4.4, §11-A, P7-UIS]

### 핵심 요약 (3줄)
1. Custom Hook은 자동 확장, 토큰 계산, 스트리밍 등 반복 로직을 재사용합니다
2. Zustand Store는 Core 상태, 비용, 승인, 메모리 등 공유 데이터를 관리합니다
3. 모든 상태 업데이트는 이벤트 기반(폴링 금지)으로 동작합니다

---

## §30.9 멀티모달 입출력 UI

> 텍스트뿐 아니라 이미지, 음성, 영상, 코드, 차트 등 다양한 형태의 입출력을 처리하는 UI 패턴입니다.
> [근거: D2.0-08 §6, §6.4]

### 비유: 다국어 통역사

일반 채팅은 텍스트만 주고받지만, VAMOS는 **다국어 통역사**처럼 텍스트, 이미지, 음성, 영상, 문서 등 모든 "언어"를 이해하고 변환합니다.

### 입력 UI 패턴

| 입력 유형 | UI 요소 | 이벤트 |
|----------|---------|--------|
| 텍스트 | 텍스트 입력창 (멀티라인, 자동 확장) | `ui.hologram.input.sent` |
| 파일 (이미지/PDF) | 📎 드래그앤드롭 + Ctrl+V 붙여넣기 | `ui.hologram.file.uploaded` |
| 음성 | 🎤 마이크 버튼 → 실시간 STT | `ui.hologram.audio.recording` |
| 화면 캡처 | 📷 캡처 버튼 | `ui.frontmini.input.received` |

### 출력 UI 패턴

| 출력 유형 | UI 요소 | 기술 스택 |
|----------|---------|----------|
| 텍스트 (Markdown) | 헤더/리스트/볼드/링크/이미지/테이블 | react-markdown + remark-gfm |
| 코드 | 구문 강조(200+언어) + 복사 버튼 | highlight.js / Prism.js |
| 수식 | LaTeX/KaTeX 인라인/블록 렌더링 | KaTeX + rehype-katex |
| 차트/다이어그램 | Mermaid, Plotly, D3.js | mermaid.js |
| 이미지 (생성) | 인라인 표시 + 확대/다운로드 | SD/Flux/DALL-E 결과 |
| 음성 (TTS) | 재생 버튼 + 파형 애니메이션 + 속도 조절 | Edge TTS(V1) |

### 멀티모달 파이프라인 흐름

```
사용자 입력 → Front Mini(전처리/PII/요약) → ORANGE CORE(의도/게이트/라우팅)
→ BLUE NODE(도메인 컨텍스트) → Main+Tool(실행/검증) → 결과 표시
```

### 대용량 입력 경고 UI

| 토큰 범위 | UI 표시 | 행동 |
|----------|---------|------|
| < 10K | 없음 | 직접 처리 |
| 10K~50K | [INFO] | "전처리 요약 추천" 배너 |
| 50K~200K | [WARNING] | "정확도 저하 가능" 경고 + 비용 예측 |
| > 200K | [ALERT] | "분할 처리 필수" 모달 + 자동 분할 제안 |

[근거: D2.0-08 §6.1, 대용량 입력 경고 UI]

### STEP7-J 멀티모달 카테고리 요약 (98건)

| 카테고리 | 항목 수 | 대표 항목 | 버전 |
|---------|---------|----------|------|
| 비전-언어 모델 | 10건 (J-001~010) | 이미지 입력, OCR, 차트 분석 | V1~V3 |
| 이미지 생성 | 10건 (J-011~020) | 이미지 생성 게이트웨이, 인페인팅 | V1~V3 |
| 오디오/음성 | 12건 (J-021~032) | STT(Whisper), TTS, 음성 대화 | V1~V3 |
| 비디오 | 10건 (J-033~042) | 비디오 생성, 편집, 분석 | V2~V3 |
| 문서/구조화 데이터 | 8건 (J-043~050) | 마크다운, 스프레드시트, 코드 문서 | V1~V2 |
| 멀티모달 RAG | 8건 (J-051~058) | 청킹, 크로스 검색, 코드 RAG | V1~V2 |
| 멀티모달 에이전트 | 8건 (J-059~066) | Computer Use, 플래너, 비용 관리 | V2~V3 |
| 차별화 전략 | 8건 (J-067~074) | 프라이버시 우선, Dream Mode | V1~V3 |
| 최신 기술 트렌드 | 8건 (J-075~082) | Native Multimodal, DiT, MoE | V1~V3 |
| 통합 아키텍처 | 6건 (J-083~088) | Router, Pipeline Manager, 캐싱 | V1~V2 |
| 참고/로드맵 | 10건 (J-089~098) | 논문, 구현 로드맵, KPI | — |
| **합계** | **98건** | — | — |

[근거: D2.0-08 §6.4]

### 핵심 요약 (3줄)
1. 텍스트/이미지/음성/영상/문서 등 다양한 입출력을 지원하는 멀티모달 UI입니다
2. 대용량 입력(10K 토큰 이상)에 대해 단계별 경고/분할 처리 UI를 제공합니다
3. STEP7-J에서 98건의 멀티모달 기술 항목이 정의되어 V1~V3로 단계 구현됩니다

---

## §30.10 Failure/Fallback UI 규칙

> 오류가 발생했을 때 사용자에게 어떻게 안내하는지에 대한 규칙입니다.
> [근거: D2.0-08 §7]

### 비유: 음식점에서 주문 실패 시

"죄송합니다, 재료가 떨어졌습니다. 비슷한 A 메뉴로 대체하거나, 환불해 드릴까요?" — 좋은 식당은 실패 시에도 **대안과 안내**를 제공합니다. VAMOS UI도 마찬가지입니다.

### 3대 UI 원칙

1. 중앙 흐름은 가능한 유지 (몰입 방해 최소화)
2. 우측 패널/HUD/토스트로 명확히 안내
3. 재시도/대안 버튼 제공

### 단계별 실패 코드 및 UI 안내

**입력 단계 (Front Mini)**

| 실패 코드 | 상황 | UI 안내 |
|----------|------|---------|
| FM_ERR_FMT | 지원 안 되는 형식 | "지원하지 않는 파일 형식입니다 (PDF, JPG, MP3 등만 가능)" |
| FM_ERR_SIZE | 용량 초과 | "파일 크기가 제한을 초과했습니다 (최대 25MB)" |
| FM_ERR_PII | 민감정보 감지 | "문서에 민감한 정보가 포함되어 있습니다. 마스킹 후 진행할까요?" |
| FM_ERR_ZERO | 빈 파일 | "파일 내용이 비어 있습니다. 다시 확인해 주세요." |

**판단 단계 (ORANGE CORE)**

| 실패 코드 | 상황 | UI 안내 |
|----------|------|---------|
| OC_ERR_NONGOAL | 안전 정책 위반 | "해당 요청은 VAMOS 안전 정책상 수행할 수 없습니다" |
| OC_ERR_P2_LOCK | P2 미승인 접근 | "이 작업은 '{도메인}' 활성화 승인이 필요합니다" |
| OC_ERR_COST_LV | 예산 초과 | "비용 효율을 위해 '절약 모드'로 전환합니다" |
| OC_ERR_NO_ROUTE | 라우팅 실패 | "이 요청을 처리할 적절한 도구를 찾지 못했습니다" |

**실행 단계 (Tool/Main)**

| 실패 코드 | 상황 | 폴백 처리 | UI 안내 |
|----------|------|----------|---------|
| TL_ERR_TIMEOUT | 시간 초과 | 소프트 재시도 | "잠시 후 다시 시도합니다" |
| TL_ERR_403 | 접근 차단 | 웹 검색 우회 | "검색 엔진을 통해 정보를 찾습니다" |
| TL_ERR_PARSE | 파싱 실패 | 원본 제공 | "원본 텍스트로 결과를 보여드립니다" |
| MC_ERR_LOW_QOD | 품질 낮음 | 자동 보완 | "근거를 재검색하고 있습니다" |
| MC_ERR_CONFLICT | 정보 충돌 | 충돌 표시 | "서로 다른 출처의 정보가 충돌합니다" |
| MC_ERR_STALE | 데이터 만료 | 만료 표시 | "참조 데이터가 오래되었습니다" |

### 네이밍 규칙

| 유형 | 패턴 | 예시 |
|------|------|------|
| Failure Code | `{LAYER}_ERR_{REASON}` | FM_ERR_PII, OC_ERR_COST_OV |
| Fallback ID | `FB_{ACTION}_{DETAIL}` | FB_MASK_AND_CONFIRM, FB_RETRY_SOFT |
| Event Type | `ui.{layer}.{subject}.{action}` | ui.frontmini.pii.detected |

- 총 등록: **FailureCode 14건 + FallbackRegistry 9건**

[근거: D2.0-08 §7, §7.6]

### 핵심 요약 (3줄)
1. 모든 실패는 failure_code로 식별되고, fallback 또는 deny로 반드시 수렴합니다
2. 입력(4건)/판단(4건)/실행(6건) 단계별로 사용자 친화적 안내 메시지를 제공합니다
3. FailureCode 14건 + FallbackRegistry 9건이 D2.1-D2에 동기 등록됩니다

---

## §30.11 색상 팔레트 & 아이콘 시스템

> VAMOS UI의 시각적 정체성을 결정하는 색상, 아이콘, 타이포그래피 규칙입니다.
> [근거: D2.0-08 §10]

### 비유: 브랜드 CI 가이드

모든 기업이 로고 색상/폰트/아이콘 규칙을 정하듯, VAMOS도 일관된 시각 경험을 위한 **디자인 시스템 표준**을 가지고 있습니다.

### 색상 팔레트

| 용도 | 색상 코드 | 설명 |
|------|----------|------|
| **ORANGE CORE (Main)** | `#F97316` | 판단/제어/경고 — 주황색 |
| **BLUE NODE (Sub)** | `#00F6FF` | 실행/도구 — 시안색 |
| **Approval 대기** | `#F59E0B` | 승인 대기 — 노란색 |
| **Approval 완료** | `#10B981` | 승인 완료 — 초록색 |
| **거절/차단** | `#EF4444` | 거절/차단/에러 — 빨간색 |
| **Evidence (Trust)** | `#00DDB3` | 출처/근거 — 민트색 |
| **Background** | `#1E1E1E` | 다크 IDE 스타일 배경 |
| **비용 80% 경고** | `#FBBF24` | 비용 80% 도달 (DEC-015) |
| **비용 100% 차단** | `#EF4444` | 비용 100% 도달, 빨간색 점멸 (DEC-015) |

### 아이콘 시스템

| 용도 | 아이콘 | 설명 |
|------|--------|------|
| ORANGE CORE | ⬢ (Hexagon) | 육각형, Pulsing 애니메이션 |
| BLUE NODE | ● (Circle) | 원형, 상태별 테두리 색상 변화 |
| Approval | 🛡️ | 승인/보안 |
| Cost | 💲 | 비용 |
| Memory | 💾 | 메모리/저장 |
| Tool | 🔧 | 도구/실행 |

- **아이콘 라이브러리**: `lucide-react` (^0.468.0) — **LOCK** (트리 쉐이킹 지원, 1,400+ 아이콘)

### 타이포그래피

| 용도 | 크기 | 폰트 |
|------|------|------|
| 본문 | 14px | system-ui, "맑은 고딕", sans-serif |
| 소제목 | 16px | 동일 |
| 제목 | 20px | 동일 |
| 코드 | 14px | "Cascadia Code", "D2Coding", monospace |

- V1: 시스템 폰트 전용 (웹폰트 번들링 없음) **LOCK**

### 알림 우선순위 (Alert Priority)

| 우선순위 | 표시 방식 | 효과 |
|---------|----------|------|
| **Alert-P0 (Critical)** | 화면 중앙 모달 or 붉은색 테두리 점멸 | 작업 차단 |
| **Alert-P1 (Approval)** | 우측 패널 슬라이드 인 + 노란색 글로우 | 작업 일시정지 |
| **Alert-P2 (Info)** | 상단 토스트 메시지 or 로그 라인 | 비침해적 |

> **주의**: Alert-P0/P1/P2는 도메인 우선순위(Domain P0/P1/P2)와 **별개**입니다. 코드에서는 `alert_priority` 필드를 사용합니다.

[근거: D2.0-08 §10.1, §10.2, §10.2a, §10.3]

### 핵심 요약 (3줄)
1. 주황(CORE) + 시안(NODE) + 초록/노랑/빨강(상태)이 핵심 색상 팔레트입니다
2. 아이콘은 lucide-react 라이브러리를 사용하며 1,400+ 아이콘을 지원합니다
3. 알림은 P0(차단)/P1(일시정지)/P2(정보) 3단계로 구분됩니다

---

## §30.12 CLI 인터페이스

> 터미널(명령줄)에서 VAMOS를 사용하는 방법입니다.
> [근거: D2.0-08 §2.3]

### 비유: 음성 주문 vs 터치스크린 주문

- Hologram View = 터치스크린 키오스크 (버튼 누르기)
- CLI = 음성 주문 (텍스트 명령어 입력)
- 같은 주문(기능)이지만 방법만 다릅니다

### 주요 CLI 명령어

```bash
vamos run --session <session_id> --input "<query>"    # 실행
vamos approve --decision_id <id> --action approve|deny # 승인/거절
vamos status --trace_id <trace_id>                     # 상태 확인
vamos cost --mode <V0|V1|V2|V3>                        # 비용 모드
vamos memory --list | --commit <id> | --discard <id>    # 메모리 관리
vamos policy --show | --edit <policy_id>                # 정책 조회/편집
```

### CLI 출력 형식

| 플래그 | 출력 형식 | 용도 |
|--------|----------|------|
| (기본) | 사람이 읽기 쉬운 텍스트 | 일반 사용 |
| `--json` | JSON 구조화 출력 | 파이프라인 연동 |
| `--quiet` | 결과값만 출력 | 스크립트 자동화 |

### CLI ↔ UI 동기화

- CLI 실행 시 동일한 `ui.cli.*` 네임스페이스 이벤트 발행
- trace_id 기반으로 Builder View와 동일한 실행 컨텍스트 공유
- CLI 승인/거절도 Approval 탭에 즉시 반영
- i18n: `locales/{locale}/cli.json` — CLI 전용 다국어 키 관리

### CLI 컴포넌트 (V1 필수 4개)

| 컴포넌트 | 역할 |
|---------|------|
| CLIPrompt (CLI-CMD-01) | 명령 입력 |
| CLIOutput (CLI-CMD-02) | 결과 출력 |
| CLIProgressBar (CLI-CMD-03) | 진행률 표시 (spinner/bar) |
| CLIApprovalPrompt (CLI-CMD-04) | 승인 Y/N 프롬프트 |

[근거: D2.0-08 §2.3, §5.6-A]

### 핵심 요약 (3줄)
1. CLI에서 `vamos run/approve/status/cost/memory/policy` 6가지 핵심 명령을 제공합니다
2. `--json`/`--quiet` 플래그로 파이프라인 연동과 스크립트 자동화를 지원합니다
3. CLI 이벤트는 `ui.cli.*` 네임스페이스로 Builder View와 동기화됩니다

---

## §30.13 접근성 (WCAG 2.1 AA) & 다국어 (i18n)

> 장애를 가진 사용자도 불편 없이 사용할 수 있고, 여러 언어를 지원하는 규칙입니다.
> [근거: D2.0-08 §0, §11-A.10, MOD-022]

### 비유: 공공건물의 장애인 편의시설 + 다국어 안내판

좋은 공공건물은 **경사로, 점자 안내판, 다국어 표지판**을 모두 갖추고 있습니다. VAMOS UI도 마찬가지입니다.

### 접근성 (WCAG 2.1 AA) 항목

| 항목 | 구현 내용 | 버전 |
|------|----------|------|
| 키보드 탐색 (S7C-098) | Tab 키로 모든 UI 접근, 포커스 링, Skip to Content | V1 |
| 폰트 크기 조절 (S7C-100) | rem 기반 반응형, 사용자 설정 가능 | V1 |
| 다크/라이트 모드 (S7C-097) | 시스템 설정 연동 + 수동 토글 | V1 |
| 애니메이션 감소 (S7C-104) | `prefers-reduced-motion` 미디어 쿼리 지원 | V1 |
| 스크린 리더 (S7C-099) | ARIA 라벨, role 속성, alt 텍스트 | V3 |
| RTL 지원 (S7C-102) | 아랍어/히브리어 우-좌 레이아웃 | V3 |
| 고대비 모드 (S7C-103) | `prefers-contrast` 미디어 쿼리 | V2 |

### 다국어 (i18n) 규칙

| 항목 | 내용 |
|------|------|
| 기본 로케일 | `ko-KR` (한국어) |
| 보조 로케일 | `en-US` (영어) |
| 확장 로케일 (V2) | `ja-JP` (일본어) |
| 번역 파일 구조 | `locales/{locale}/{namespace}.json` |
| 네임스페이스 | `ui.json` (Builder), `hologram.json` (Hologram), `cli.json` (CLI) |
| i18n 키 패턴 | `ui.{component}.{key}` |
| 기술 스택 | next-intl 또는 react-i18next |

### i18n 핵심 규칙 **변경 불가**

- 모든 사용자 대면 UI 문구는 **i18n 키**로 관리 (하드코딩 금지) **LOCK**
- LogEvent payload의 `message` 필드는 **영어 고정** (로케일 무관 감사 추적 보장) **LOCK**
- 승인 카드/비용 경고/정책 차단 메시지는 사용자 로케일에 따라 렌더링
- UI 언어 변경: 설정 → 언어 → 즉시 적용 (페이지 새로고침 없음)

[근거: D2.0-08 §0, MOD-022, S7C-097~104]

### 핵심 요약 (3줄)
1. V1에서 키보드 탐색, 폰트 조절, 다크 모드, 애니메이션 감소를 지원합니다
2. 한국어(기본)/영어/일본어 3개 언어를 지원하며, 모든 UI 문구는 i18n 키로 관리합니다
3. LogEvent 메시지는 영어 고정이며, 사용자 UI는 로케일에 따라 렌더링됩니다

---

## §30.14 STEP7 UI 강화 항목 (104개)

> VAMOS UI/UX를 시중 AI(ChatGPT/Claude/Gemini/Perplexity 등) 수준으로 끌어올리기 위한 104개 강화 항목입니다.
> [근거: D2.0-08 §11-A]

### 비유: 신차 옵션 목록

기본 차량에 네비게이션, 열선 시트, 후방 카메라 등 다양한 옵션을 추가하듯, VAMOS UI에도 시중 AI에서 검증된 104개 기능을 추가합니다.

### 카테고리별 항목 수 요약

| Part | 카테고리 | 항목 수 | V1 필수 | 대표 항목 |
|------|---------|---------|---------|----------|
| 1 | 메인 대화 인터페이스 | 12건 | 5건 | 3-Column, 모델 선택, ORANGE/BLUE 상태 |
| 2 | Canvas/Artifacts/편집 | 10건 | 3건 | Artifacts 패널, Decision 시각화, Split View |
| 3 | 입력 영역(Composer) | 10건 | 6건 | 멀티라인, 드래그앤드롭, 비용 미리보기 |
| 4 | 응답 렌더링 | 12건 | 8건 | Markdown, 코드 강조, 3-Part 출력, 신뢰도 바 |
| 5 | 음성 모드 | 8건 | 0건 | 음성 대화, 파형, 자막 (V2~) |
| 6 | 모바일/데스크톱/CLI | 10건 | 6건 | Tauri 데스크톱, CLI, 글로벌 검색 |
| 7 | 에이전트 실행 상태 | 8건 | 4건 | 진행률, 5-Gate 통과, 파이프라인 스텝 |
| 8 | 설정/커스터마이징 | 10건 | 5건 | 메모리 관리, 비용 대시보드, 데이터 내보내기 |
| 9 | VAMOS 고유 위젯 | 16건 | 6건 | 5-Gate 표시기, 비용 게이지, QoD 바, NODE 카드 |
| 10 | 접근성/다크모드/i18n | 8건 | 5건 | 다크모드, 키보드, 다국어, 애니메이션 감소 |
| **합계** | — | **104건** | **48건** | — |

### V1+CRITICAL 핵심 21건 (R1 라운드)

| 영역 | 건수 | 항목 |
|------|------|------|
| 핵심 레이아웃 | 3건 | S7C-001(3-Column), S7C-002(사이드바), S7C-004(모델 선택) |
| VAMOS 고유 UI | 9건 | S7C-012(ORANGE/BLUE), S7C-022(Decision), S7C-040(3-Part 출력), S7C-041(신뢰도), S7C-042(비용), S7C-069(5-Gate), S7C-081(Gate 위젯), S7C-082(비용 게이지), S7C-083(QoD 바) |
| 입출력 기본 | 6건 | S7C-023(멀티라인), S7C-024(드래그앤드롭), S7C-030(비용 미리보기), S7C-033(Markdown), S7C-034(코드 강조), S7C-038(스트리밍) |
| 플랫폼/에이전트 | 3건 | S7C-053(Tauri), S7C-063(진행률), S7C-074(비용 대시보드) |

[근거: D2.0-08 §11-A, STEP7 R1 V1+CRITICAL]

### 핵심 요약 (3줄)
1. STEP7-C에서 시중 AI 전수 비교를 통해 104개 UI 강화 항목을 식별했습니다
2. V1에서 48건이 필수이며, 특히 V1+CRITICAL 21건이 최우선 구현 대상입니다
3. 10개 카테고리(대화/Canvas/입력/렌더링/음성/플랫폼/에이전트/설정/위젯/접근성)로 분류됩니다

---

## §30.15 ★대시보드 상세 (Log/P2/Document/Innovation) — GAP-11

> VAMOS에서 제공하는 4가지 주요 대시보드의 상세 설명입니다.
> [근거: D2.0-08 §12, §14, §17]

### 비유: 관제센터의 4개 모니터

관제센터에서 각 모니터가 CCTV, 온도, 전력, 보안을 각각 보여주듯, VAMOS도 **로그, P2 도메인, 문서 처리, 혁신 사이클**을 각각의 대시보드로 보여줍니다.

---

### ① Log Dashboard (로그 대시보드)

> 시스템에서 발생하는 모든 이벤트를 추적하는 대시보드입니다.
> [근거: D2.0-08 §12, IR-023]

**버전별 기술 스택**

| 버전 | 기술 스택 | 핵심 기능 |
|------|----------|----------|
| V1 | **Streamlit** | 로그 필터링, trace_id 검색, 비용 요약 |
| V2 | **Loki-lite** | 레이블 기반 필터, 스트리밍 로그, 알림 |
| V3 | **Loki + Grafana** | 메트릭 시각화, 알림 룰, 대시보드 템플릿 4종 |

**V1 Streamlit 대시보드 화면 구성**

```
┌─────────────────────────────────────────────────┐
│ [상단] trace_id / 날짜 범위 / event_type 필터   │
├─────────────────────────────────────────────────┤
│ [중간] LogEvent 타임라인 (트리 구조)            │
│  trace_id │ event_type          │ 시각    │ 상태 │
│  abc123   │ oc.request.received │ 14:22  │ INFO │
│  abc123   │ oc.i1.parse.started │ 14:22  │ INFO │
│  abc123   │ oc.gate.cost.check  │ 14:22  │ WARN │
├─────────────────────────────────────────────────┤
│ [하단] 비용 요약 (V1/V2/V3별 breakdown)         │
└─────────────────────────────────────────────────┘
```

**V3 Grafana 대시보드 템플릿 4종**

| 템플릿 | 내용 |
|--------|------|
| System Overview | 요청수/에러율/비용/p99 레이턴시 |
| Cost Drill-down | 도메인별·모드별 비용 breakdown |
| Safety Events | CRITICAL 이벤트 타임라인 + 알림 히스토리 |
| Agent Performance | 도메인별 성공률·응답시간·메모리 사용 |

- V1 컴포넌트: LOG-DASH-01 (LogDashboard ★), LOG-DASH-02 (TraceTimeline ★)

[근거: D2.0-08 §12]

---

### ② P2 Domain Dashboard (P2 도메인 대시보드)

> P2(승인 기반) 도메인의 활성화 상태를 전용으로 모니터링하는 대시보드입니다.
> [근거: D2.0-08 §14.1]

**구성 위젯**

| 위젯 | 설명 |
|------|------|
| P2 활성 도메인 목록 | 현재 세션에서 활성화된 P2 도메인 리스트 + 활성화 시각 |
| 세션 만료 카운트다운 | 세션 종료까지 남은 시간 (진행 바) |
| P2 도메인 비용 | 해당 세션에서 P2 도메인이 소비한 비용 |
| 비활성화 버튼 | 클릭 시 즉시 P2 도메인 비활성화 (07 Gate 경유) |

**이벤트 연동**

| 이벤트 | 트리거 |
|--------|--------|
| `ui.p2.domain.activated` | P2 도메인 행 추가 |
| `ui.p2.domain.deactivated` | 도메인 행 제거 + 세션 로그 |
| `ui.p2.session.expiring` | 세션 5분 전 경고 토스트 |

**EVX Chain Status Widget (EVX 검증 체인 위젯)**

EVX 단계별 통과/실패 상태를 실시간 시각화합니다:

```
[EVX-1 입력검증 ✅] → [EVX-2 정책검사 ✅] → [EVX-3 비용확인 ✅] → [EVX-4 실행 🔄]
```

- `ui.evx.step.passed` → ✅, `ui.evx.step.failed` → ❌, `ui.evx.step.started` → 🔄

- V1.1 컴포넌트: P2-DASH-01 (DomainDashboard)

[근거: D2.0-08 §14.1, §14.2]

---

### ③ Document Dashboard (문서 처리 대시보드)

> 문서 처리(A1 후보군, Cloud Library 수집)의 상태를 관리하는 대시보드입니다.
> [근거: D2.0-08 §19, §20, §21, §22]

**구성 요소**

| 탭 | 내용 | 관련 섹션 |
|----|------|----------|
| **E-17 CLib (Cloud Library)** | 수집된 라이브러리 목록, 수집 상태, 수동 수집 트리거, 승인 카드 | §19 |
| **A1 Appendix** | A1 후보군 문서 아카이브, 확정 시 D2.0 병합 | §20 |
| **N1 능동 수집** | 수집 스케줄, 소스 목록, 실행 로그, 승인 큐 | §21 |
| **Autonomous Discovery** | 자동 소스 발견 제안 카드, 승인 → N1 등록 | §22 |

**N1 수집 파이프라인 흐름**

```
N1 스케줄러 → 소스 요청 → 콘텐츠 추출 → 품질 필터 → 승인 큐 → 사용자 확인 → RAG 인덱스 삽입
```

**주요 이벤트**

| 이벤트 | 설명 |
|--------|------|
| `ui.clib.item.discovered` | 신규 라이브러리 발견 → 승인 카드 생성 |
| `ui.n1.item.pending` | 수집 항목 승인 큐 추가 → 알림 배지 |
| `ui.discovery.source.suggested` | 신규 소스 발견 → 제안 카드 표시 |
| `ui.discovery.source.accepted` | 사용자 승인 → N1 소스 등록 |

[근거: D2.0-08 §19, §20, §21, §22]

---

### ④ Innovation Dashboard (혁신 사이클 대시보드)

> VAMOS의 자기 개선(Self-evo) 사이클을 모니터링하는 대시보드입니다.
> [근거: D2.0-08 §17]

**혁신 사이클 6단계 (Builder View > Innovation 탭)**

| 단계 | 이름 | 트리거 | UI 이벤트 |
|------|------|--------|----------|
| 1 | 성능 수집 | 일일 배치 | `ui.innovation.metrics.collected` |
| 2 | 개선 후보 선정 | 임계값 초과 | `ui.innovation.candidate.identified` |
| 3 | Self-evo 제안 | Self-evo 엔진 | `ui.innovation.proposal.generated` |
| 4 | 검토/승인 | 사용자 승인 카드 | `ui.innovation.proposal.approved` |
| 5 | 적용 & 롤아웃 | 07 Gate 승인 후 | `ui.innovation.change.applied` |
| 6 | 효과 검증 | 7일 후 | `ui.innovation.effect.verified` |

**혁신 경로 매핑 (Innovation Path Map)**

- 시각화: 노드-엣지 그래프 (Builder View > Innovation > Path Map)
- 노드: 각 개선 항목 (이름, 상태, 적용 날짜)
- 엣지: 의존 관계 (A 개선이 B를 활성화)
- 필터: 상태별(pending/applied/failed), 도메인별

- 관련 위젯: S7C-088 (자기진화 타임라인, V2)

[근거: D2.0-08 §17]

---

### 4개 대시보드 비교표

| 대시보드 | 위치 | V1 지원 | 주요 용도 |
|---------|------|---------|----------|
| Log Dashboard | Builder View > Logs | ★ V1 (Streamlit) | 이벤트 추적/필터/비용 요약 |
| P2 Domain Dashboard | Builder View > P2 | V1.1 | P2 도메인 활성/비용 모니터링 |
| Document Dashboard | Builder View > Library/Collector | V1 (부분) | 문서 수집/승인 관리 |
| Innovation Dashboard | Builder View > Innovation | V2 | 자기 개선 사이클 모니터링 |

### 핵심 요약 (3줄)
1. Log Dashboard는 V1(Streamlit)→V2(Loki)→V3(Grafana)로 단계 발전합니다
2. P2 Dashboard는 승인 기반 도메인의 활성/비용/만료를 전용 관제합니다
3. Innovation Dashboard는 AI 자기 개선 6단계(수집→선정→제안→승인→적용→검증)를 시각화합니다

---

## 전체 검증 체크리스트

- [x] 7원칙? — §30.1에서 7가지 원칙 각각 설명 완료
- [x] Builder/Hologram View? — §30.2, §30.3에서 상세 설명 완료
- [x] 3-Panel Layout? — §30.4에서 좌/중/우 구조 + ASCII 다이어그램 포함
- [x] UI 9-State? — §30.5에서 9가지 상태 + 전이 조건 + I-10 오케스트레이션 설명
- [x] React 컴포넌트 ~44개? — §30.7에서 44개 전체 목록 카테고리별 정리
- [x] 색상 팔레트? — §30.11에서 색상 코드 + 아이콘 + 타이포그래피 + 알림 우선순위
- [x] 접근성 WCAG? — §30.13에서 WCAG 2.1 AA 항목 + i18n 규칙 설명
- [x] ★대시보드 상세 GAP-11? — §30.15에서 Log/P2/Document/Innovation 각각 상세 설명
- [x] 비유 설명 포함? — 모든 섹션에 일상 비유 포함
- [x] 근거 SOT 참조 표기? — 모든 섹션에 [근거: D2.0-08 §X] 표기
