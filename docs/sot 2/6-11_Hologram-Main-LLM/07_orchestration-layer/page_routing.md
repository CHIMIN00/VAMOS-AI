# page_routing.md — 7 페이지 라우팅 규칙 + Hologram View Chat 전용 제약

| 항목 | 값 |
|------|----|
| **도메인** | 6-11_Hologram-Main-LLM / 07_orchestration-layer |
| **세션 (TASK_ID)** | Phase 2 T2-6 (6-11_T2-6_03) |
| **산출물 경로 (sandbox)** | `D:\VAMOS\docs\test_iso_p2\sot 2\6-11_Hologram-Main-LLM\07_orchestration-layer\page_routing.md` |
| **정본 산출물 경로 (production)** | `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\07_orchestration-layer\page_routing.md` |
| **LOCK** | **LOCK-HM-02** (4 Layout 구조 — D2.0-08 §2.1/§3), **LOCK-HM-05** (I-10 UI 오케스트레이션 — `current_layout` 전파), 보조: **LOCK-HM-01** (3-Pane Right Panel Hologram View 한정), **LOCK-HM-07** (44 컴포넌트 — ChatPage.tsx 진입점) |
| **정본 소유** | 6-11 DEFINED-HERE — 7 페이지 (`Dashboard`/`Chat`/`Workflow`/`Memory`/`Settings`/`Log`/`NodeDetail`) 라우팅 규칙 · Hologram View Chat 페이지 전용 제약 · 페이지 전환 시 Hologram View 상태 보존·초기화 정책 · T2-5 stream_protocol §8.4 `[T2-6 확정 시 재검토]` 주석 해소 경로 (§4 택1 결정) |
| **해소 이슈** | **ISS-15** (7 페이지 라우팅 규칙 — 본 문서 주축 해소) |
| **Phase 배정** | Phase 2 T2-6 |
| **Part2 버전 태그** | V2-Phase 2 (Enhanced Hologram) |
| **작성일** | 2026-04-19 |
| **Version** | v1.0 (초안) |
| **TEST_MODE** | false — Phase 4 production promotion 2026-06-03 (sandbox → production 전환 완료) |

---

## §0. 목적 & Scope

### §0.1 목적

7 페이지(Dashboard / Chat / Workflow / Memory / Settings / Log / NodeDetail) 라우팅 규칙을 확정한다.
핵심 제약:

- **Hologram View = Chat 페이지 전용** — 다른 페이지에서 Hologram View 진입 **금지** (LOCK-HM-07
  `ChatPage.tsx` 가 Hologram View 진입점 verbatim).
- 페이지 전환 시 Hologram View **상태 보존·초기화 정책** 명시.
- **T2-5 stream_protocol §8.4 `[T2-6 확정 시 재검토]` 주석 해소** — 별도 채널 default 확정
  (해소 경로 **A: 해소** 택1, §4).
- 페이지별 경로·권한·진입점 명세 (ISS-15 해소).

### §0.2 Scope 표

| 구분 | 범위 |
|------|------|
| **In** (본 문서에서 확정) | (a) 7 페이지 라우팅 경로 정본 테이블(§3), (b) Hologram View = Chat 페이지 전용 제약(§3.8 + §6), (c) 페이지 전환 × Hologram View 상태 보존·초기화 정책(§5), (d) T2-5 stream_protocol §8.4 `[T2-6 확정 시 재검토]` 주석 해소 — **경로 A (해소: multiplex 불요)** 택1 + 근거(§4), (e) 페이지별 권한 조건(§3.10) + 6-2 Security-Governance 경계 선언, (f) 페이지 전환 trigger 이벤트 매트릭스(§5.2), (g) R-01-7 로깅(§7), (h) Phase 3 시나리오 12건(§8). |
| **Out** (타 세션/문서 위임) | (a) `UiStatePayload` / `ArtifactRef` / `OrchestrationEvent` 공통 자료 구조 → **`ui_state_mapping.md` §3**, (b) 9-State × 3-point 바인딩 → **`ui_state_mapping.md` §4**, (c) Layout × State 허용 매트릭스 + Layout 전환 trigger 매트릭스 → **`ui_state_mapping.md` §7.2/§7.3**, (d) I-10 분배 파이프라인 → **`cost_evidence_log.md`**, (e) SSE 채널 프로토콜·재연결·청크 포맷 → **T2-5 `stream_protocol.md` / T2-4 `realtime_update.md`**, (f) 페이지별 UI 렌더 구현 → **6-1 UI-UX-System + Phase 1 V1**, (g) 권한 검증 로직·세션 토큰 스키마 → **6-2 Security-Governance**. |
| **관련 이슈** | **ISS-15** (본 문서 주축 해소) |

### §0.3 도메인 경계 선언

- **6-11 소유** (본 문서): 7 페이지 라우팅 **경로 테이블** · Hologram View 페이지 전용 **제약** · 페이지
  전환 시 **HUD·스트림 채널 정책** · 상태 보존·초기화 **규약**.
- **6-1 UI-UX-System 소유**: 각 페이지 UI 렌더 구현 + 페이지 전환 애니메이션. 본 문서는 **라우팅 경로와
  진입점 컴포넌트 이름만** 규정.
- **6-2 Security-Governance 소유**: 권한 조건 실 검증 로직 + 세션 토큰 발급·갱신. 본 문서는 **페이지별
  필요 권한만** 선언.
- **4-1 Rust-Tauri-Infrastructure 소유**: 라우터 자체 (React Router or Tauri Navigation) 구현. 본 문서는
  **경로 문자열 정본만** 제공.

---

## §1. 교차 참조 블록

### §1.1 상위 정본 (LOCK 근거 표)

| 참조 문서 | 섹션 / 라인 | 역할 |
|-----------|-------------|------|
| `../../../sot/D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` | §2.1/§3 (L151, L311) | **LOCK-HM-02** — 4 Layout (3-Column Fluid / Builder / Hologram / CLI) |
| `../../../sot/D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` | §2.2 (L223-282) | **LOCK-HM-01** — Hologram View 3-Pane 구조, Right Panel HUD 위치 |
| `../../../sot/D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md` | §7.63 (L2091-2119) | **LOCK-HM-05** — I-10 `emit_ui_state` payload `current_layout` 필드 전파 |
| Part2 V1-P4 (L2277-2414) | — | **LOCK-HM-07** — `ChatPage.tsx` 가 Hologram View 진입점 verbatim |

### §1.2 AUTHORITY_CHAIN / CONFLICT_LOG

| 참조 문서 | 섹션 | 확인 사항 |
|-----------|------|-----------|
| `../AUTHORITY_CHAIN.md` | L43 (L2 LOCK-HM-02) | 4 Layout verbatim |
| `../AUTHORITY_CHAIN.md` | L54 (L8 LOCK-HM-07) | ChatPage.tsx 진입점 verbatim |
| `../AUTHORITY_CHAIN.md` | L104-L110 | LOCK-HM-05 `current_layout` 전파 근거 |
| `../CONFLICT_LOG.md` | — | CFL-HM-001~007 + C-1~C-3 RESOLVED, OPEN 0. 본 세션 신규 CONFLICT_CANDIDATE 0 (9-State 네이밍 drift 는 ui_state_mapping §11 등재) |

### §1.3 로컬 Phase 1 산출물 (입력 근거)

| 파일 | 역할 |
|------|------|
| `../01_hologram-view-layout/layout_structure.md` | 3-Pane 구조 정본 (Hologram View 배치) |
| `../02_component-architecture/component_catalog.md` | HV-*/BV-*/LOG-*/BOARD-*/MEMORY-* 44 컴포넌트 — 본 문서 §3 진입점 참조 |

### §1.4 Peer V2 세션 이음매 (V2↔V2 cross-reference ≥13 목표)

| peer V2 | 경로 | 섹션·라인 근거 | 본 문서 접점 |
|---------|------|----------------|-------------|
| **`ui_state_mapping.md`** (sibling, T2-6 본 세션) | `./ui_state_mapping.md` | §3 `UiStatePayload.current_layout: UiLayout` | 본 문서 §3 각 페이지 → `current_layout` 매핑 테이블 (재정의 금지) |
| **`ui_state_mapping.md`** (sibling) | `./ui_state_mapping.md` | §7.3 Layout 전환 trigger 매트릭스 + §7.4 HOLOGRAM 진입·이탈 채널 정책 | 본 문서 §5 페이지 전환 × Layout 전환 교차 표 |
| **`cost_evidence_log.md`** (sibling) | `./cost_evidence_log.md` | §1.4 peer 표 + §7.5 6-12 중복 방지 | 본 문서 §3 Log 페이지에서 Timeline/LogDetail 소비 규약 교차 참조 |
| **T2-4 `rendering_rules.md`** (490줄) | `../05_glass-hud-overlay/rendering_rules.md` | **§2** Right Panel Fixed HUD 위치 고정 + Hologram View Chat 페이지 전용 근거(Chat 진입 시에만 HUD mount) | 본 문서 §6 Chat 페이지 전용 제약 backup 근거 (6-1 02_hologram-view 정본 우선, 부재 시 본 근거 채택) |
| **T2-4 `realtime_update.md`** (591줄) | `../05_glass-hud-overlay/realtime_update.md` | **§3.1** SSE 6 이벤트 + `/api/hologram/hud/stream` 채널 | 본 문서 §4 채널 정책 (별도 채널 default 확정) |
| **T2-5 `stream_protocol.md`** (1,083줄) | `../06_streaming-canvas/stream_protocol.md` | **§8.1** 별도 채널 default `/api/hologram/stream` vs `/api/hologram/hud/stream` | 본 문서 §4 Chat 페이지 진입·이탈 시 2 채널 개시·정리 규약 |
| **T2-5 `stream_protocol.md`** (1,083줄) | `../06_streaming-canvas/stream_protocol.md` | **§8.2** 별도 채널 vs 공용 multiplex 장단점 표 | 본 문서 §4.2 해소 근거 |
| **T2-5 `stream_protocol.md`** (1,083줄) | `../06_streaming-canvas/stream_protocol.md` | **§8.3** 공용 multiplex 조건 5개 | 본 문서 §4.3 조건 미충족 근거 (V1 Phase 2 범위 외) |
| **T2-5 `stream_protocol.md`** (1,083줄) | `../06_streaming-canvas/stream_protocol.md` | **§8.4** `[T2-6 확정 시 재검토]` 주석 | 본 문서 §4 해소 경로 A (해소: multiplex 불요) 택1 결정 |
| **T2-1 `two_tier_routing.md`** (857줄) | `../04_main-llm-integration/two_tier_routing.md` | **§4 L448** `emit(oc.i10.ui.state.emitted, trace_id, ui_state)` | 본 문서 §5.2 페이지 전환 → I-10 이벤트 재발행 규약 |
| **T2-1 `two_tier_routing.md`** (857줄) | `../04_main-llm-integration/two_tier_routing.md` | **§3.1 L140** `TraceId = str  # ULID` | 본 문서 §5.3 보존 정책에서 `trace_id` 타입 공유 |
| **T2-2 `response_formatting.md`** (911줄) | `../04_main-llm-integration/response_formatting.md` | **§3.1** `UserResponse.is_streaming` | 본 문서 §5.3 Chat 이탈 시 스트림 중단 판정 |
| **T2-5 `token_rendering.md`** (772줄) | `../06_streaming-canvas/token_rendering.md` | **§7.1** `scheduleTokenFlush` + Stream Canvas unmount 시 버퍼 비우기 | 본 문서 §5.3 이탈 시 Stream Canvas 언마운트 규약 |
| **T2-5 `artifact_rendering.md`** (611줄) | `../06_streaming-canvas/artifact_rendering.md` | **§3.3** ArtifactZone CREATED → INTERACTIVE 라이프사이클 | 본 문서 §5.3 이탈 시 ArtifactZone `FINALIZED` 보존 규약 |
| **T2-4 `overlay_schema.md`** (898줄) | `../05_glass-hud-overlay/overlay_schema.md` | **§3** `HudMeta.mode = "FIXED"` 상수 | 본 문서 §6 Chat 페이지 안에서만 HUD mount (mode 유지) |

> **합계 15 cross-ref** (ui_state_mapping 2 + cost_evidence_log 1 + T2-4 rendering 1 + T2-4 realtime 1 + T2-4 overlay 1 + T2-5 stream 4 + T2-5 token 1 + T2-5 artifact 1 + T2-1 2 + T2-2 1). 실측 섹션·라인 verbatim 대조 완료. 목표 ≥13 달성.

### §1.5 Cross-domain Read-only 소비

| 도메인 | 범위 | 본 문서 관계 |
|--------|------|-------------|
| **6-1 UI-UX-System** | `02_hologram-view/hologram_view.md` + `_index.md` — Hologram View Layout 전환 정본 | 본 문서 §6 Chat 페이지 전용 제약 **주 근거** |
| **6-2 Security-Governance** | 페이지별 권한 조건 (`admin`/`member`/`viewer`) | 본 문서 §3.10 참조 |
| **4-1 Rust-Tauri-Infrastructure** | 라우터 구현 (React Router) | 본 문서 §3.1 경로 문자열 제공 |

> CROSS_DOMAIN_DEPS=none (envelope L30-31). 단방향 Read-only 소비만 존재.

---

## §2. 7 페이지 목록 및 역할

### §2.1 7 페이지 개요

종합계획서 `HOLOGRAM_MAIN_LLM_구조화_종합계획서.md` §7 T2-6 절차 3번 (L1226-L1230) 에 명시된 7 페이지:

| # | 페이지 | 역할 요약 | Layout 매핑 (LOCK-HM-02) |
|---|--------|-----------|--------------------------|
| 1 | **Dashboard** | 진입 허브, 시스템 개요 | `THREE_COLUMN` |
| 2 | **Chat** | Hologram View 진입점 — 대화/스트림/HUD | `HOLOGRAM` |
| 3 | **Workflow** | 파이프라인 편집·실행 — Builder View | `BUILDER` |
| 4 | **Memory** | 저장 기억/문서 관리 | `THREE_COLUMN` |
| 5 | **Settings** | 사용자/시스템 설정 | `THREE_COLUMN` |
| 6 | **Log** | 실행 로그·Timeline 뷰 | `THREE_COLUMN` |
| 7 | **NodeDetail** | 노드 상세 (파이프라인 노드 인스턴스) | `BUILDER` (Node Inspector) 또는 `THREE_COLUMN` |

### §2.2 Layout × 페이지 매핑 규칙

- **Hologram View Layout** = Chat 페이지 **유일** (LOCK-HM-07 `ChatPage.tsx` 진입점 verbatim).
- **Builder Layout** = Workflow / NodeDetail (편집 중심).
- **3-Column Fluid** = Dashboard / Memory / Settings / Log (표준 3단 공통).
- **CLI Layout** = 7 페이지와 **독립 Layout** (사용자 명시 토글, `USER_SELECT_CLI` 이벤트로 진입 —
  ui_state_mapping §7.3 전환 trigger 매트릭스 참조).

---

## §3. 페이지 라우팅 테이블 (경로·진입점·컴포넌트·권한)

### §3.1 경로 정본 테이블

| 페이지 | 경로 (path) | 진입점 컴포넌트 | Layout | 권한 | 파라미터 |
|--------|-------------|-----------------|--------|------|----------|
| Dashboard | `/` | `DashboardPage.tsx` | `THREE_COLUMN` | 로그인 | — |
| **Chat** | `/chat/:session_id?` | **`ChatPage.tsx`** (LOCK-HM-07) | `HOLOGRAM` | 로그인 | `session_id` (optional, 기본값 = 신규 세션) |
| Workflow | `/workflow/:workflow_id?` | `WorkflowPage.tsx` | `BUILDER` | 로그인 + `member` 이상 | `workflow_id` |
| Memory | `/memory/:filter?` | `MemoryPage.tsx` | `THREE_COLUMN` | 로그인 | `filter` (optional: `all`/`notes`/`files`/`rag`) |
| Settings | `/settings/:section?` | `SettingsPage.tsx` | `THREE_COLUMN` | 로그인 | `section` (optional: `profile`/`system`/`billing`/`security`) |
| Log | `/log/:trace_id?` | `LogPage.tsx` | `THREE_COLUMN` | 로그인 | `trace_id` (optional, 단일 trace 포커스) |
| NodeDetail | `/node/:node_id` | `NodeDetailPage.tsx` | `BUILDER` | 로그인 + `member` 이상 | `node_id` (required) |

### §3.2 Chat 페이지 (Hologram View 유일 Layout) 상세

| 항목 | 값 |
|------|----|
| 경로 | `/chat/:session_id?` |
| Layout | `HOLOGRAM` (LOCK-HM-02 verbatim) |
| 진입점 | `ChatPage.tsx` (LOCK-HM-07 Part2 V1-P4 L2277-2414 verbatim) |
| 3-Pane | Left Timeline ~250px / Center Stream Canvas / Right Glass HUD ~300px (LOCK-HM-01) |
| Layout 전환 허용 | `BUILDER` / `THREE_COLUMN` / `CLI` 모두 허용 (ui_state_mapping §7.3 전환 trigger 매트릭스) |
| Hologram View 진입 이벤트 | `USER_SELECT_CHAT` / `WORKFLOW_START` (ui_state_mapping §7.3) |
| 채널 개시 | 진입 시 `/api/hologram/stream?trace_id=...` + `/api/hologram/hud/stream?trace_id=...` 2 연결 (T2-5 stream_protocol §8.1 별도 채널 default) |
| 9-State 진입 | `UI_S1_IDLE` → (입력 시) `UI_S4_RUNNING` → `UI_S6_PRESENTING` 주 흐름 |

### §3.3 Dashboard 페이지

| 항목 | 값 |
|------|----|
| 경로 | `/` |
| Layout | `THREE_COLUMN` |
| 진입점 | `DashboardPage.tsx` |
| 역할 | 진입 허브, 시스템 상태 카드(비용/활성 trace 수/최근 Session). **Hologram View 미활성** — HUD mount 금지. |
| 진입 이벤트 | `USER_NAVIGATE_DASHBOARD` / 앱 부팅 후 기본 |

### §3.4 Workflow 페이지

| 항목 | 값 |
|------|----|
| 경로 | `/workflow/:workflow_id?` |
| Layout | `BUILDER` |
| 진입점 | `WorkflowPage.tsx` |
| 역할 | 파이프라인 편집·저장·실행. Chat 페이지와 분리. 실행 시 `WORKFLOW_START` 이벤트 → Chat 으로 자동 이동(Layout `HOLOGRAM` 전환, ui_state_mapping §7.3). |
| 진입 이벤트 | `USER_SELECT_BUILDER` / `USER_CREATE_WORKFLOW` |

### §3.5 Memory 페이지

| 항목 | 값 |
|------|----|
| 경로 | `/memory/:filter?` |
| Layout | `THREE_COLUMN` |
| 진입점 | `MemoryPage.tsx` |
| 역할 | 저장 기억·문서 관리. 필터 `all`/`notes`/`files`/`rag`. |
| 진입 이벤트 | `USER_NAVIGATE_MEMORY` |

### §3.6 Settings 페이지

| 항목 | 값 |
|------|----|
| 경로 | `/settings/:section?` |
| Layout | `THREE_COLUMN` |
| 진입점 | `SettingsPage.tsx` |
| 역할 | 사용자 프로파일 / 시스템 / 빌링 / 보안 설정. |
| 진입 이벤트 | `USER_NAVIGATE_SETTINGS` |

### §3.7 Log 페이지

| 항목 | 값 |
|------|----|
| 경로 | `/log/:trace_id?` |
| Layout | `THREE_COLUMN` |
| 진입점 | `LogPage.tsx` |
| 역할 | 실행 로그·Timeline 뷰. `trace_id` 지정 시 단일 trace 포커스 (LOG-DASH-02 TraceTimeline + BV-DEBUG-01 TraceLogPanel 동시 표시). `cost_evidence_log.md` §7 Timeline/LogDetail 이중 기록 결과 소비. |
| 진입 이벤트 | `USER_NAVIGATE_LOG` / Timeline row 클릭 시 `USER_FOCUS_TRACE(trace_id)` |

### §3.8 NodeDetail 페이지

| 항목 | 값 |
|------|----|
| 경로 | `/node/:node_id` |
| Layout | `BUILDER` |
| 진입점 | `NodeDetailPage.tsx` |
| 역할 | 파이프라인 노드 상세 인스펙터. Workflow 에서 노드 클릭 시 진입. |
| 진입 이벤트 | `USER_SELECT_NODE(node_id)` |

### §3.9 Hologram View Chat 전용 제약 (핵심 규약)

**제약 정본 근거**:
1. **LOCK-HM-07** (AUTHORITY_CHAIN L54, Part2 V1-P4 verbatim): "ChatPage.tsx가 **Hologram View 진입점**".
2. **6-1 UI-UX-System** `02_hologram-view/hologram_view.md` §1 "Hologram View 는 Chat Experience" (3-Pane
   Focus Layout 정본).
3. **T2-4 `rendering_rules.md`** §2 Right Panel Fixed HUD 위치 — Chat 페이지 전용 활성 (backup 근거).

**제약 본문**:

- Hologram View(Right Panel Glass HUD + Left Timeline + Center Stream Canvas) 는 **Chat 페이지에서만** 활성.
- 다른 6 페이지(Dashboard / Workflow / Memory / Settings / Log / NodeDetail)에서는 Hologram View
  **진입 금지** — HUD mount 0, Stream Canvas mount 0, Timeline Hologram 전용 컴포넌트 mount 0.
- Timeline 자체는 Log 페이지에서 단독 표시 가능 (`LOG-DASH-02 TraceTimeline` 독립 컴포넌트, Hologram
  View 와 분리된 렌더 경로).

**위반 시**: `[VIOLATION: HologramView-Chat-only]` 마커 + 해당 페이지 HUD·Stream Canvas 강제 언마운트.

### §3.10 권한 조건 (6-2 Security-Governance 경계)

| 페이지 | 필요 권한 | 검증 위치 |
|--------|-----------|----------|
| Dashboard | 로그인 | 라우터 guard |
| Chat | 로그인 | 라우터 guard |
| Workflow | 로그인 + `member` 이상 | 라우터 guard + Workflow API 이중 검증 (6-2 정본) |
| Memory | 로그인 | 라우터 guard |
| Settings (section=`security`) | 로그인 + 본인 확인 (MFA) | 6-2 MFA 챌린지 |
| Settings (section=`billing`) | 로그인 + `admin` | 라우터 guard + Billing API 이중 검증 |
| Log (trace_id=타인) | 로그인 + `admin` | 라우터 guard + Log API 이중 검증 |
| Log (trace_id=본인) | 로그인 | 라우터 guard |
| NodeDetail | 로그인 + `member` 이상 | 라우터 guard + Node API 이중 검증 |

> **경계**: 권한 실 검증 로직·토큰 스키마·MFA 챌린지 구현은 **6-2 Security-Governance 정본**. 본 문서는
> 필요 권한만 선언.
>
> **Role 별칭 매핑 (정본 Role enum = `OWNER`|`OPERATOR`|`VIEWER`, authStore / hook_catalog §3)**: `viewer` = `VIEWER`, `member` = `OPERATOR` 이상 (`OPERATOR` 또는 `OWNER`), `admin` = `OWNER`. 라우팅 권한 조건의 `member`/`admin` 표기는 본 매핑으로 해석한다 (신규 Role 신설 금지).
>
> **Role 별칭 매핑 (정본 Role enum = `OWNER`|`OPERATOR`|`VIEWER`, authStore / hook_catalog §3)**: `viewer` = `VIEWER`, `member` = `OPERATOR` 이상 (`OPERATOR` 또는 `OWNER`), `admin` = `OWNER`. 라우팅 권한 조건의 `member`/`admin` 표기는 본 매핑으로 해석한다 (신규 Role 신설 금지).

---

## §4. T2-5 stream_protocol §8.4 `[T2-6 확정 시 재검토]` 주석 해소

### §4.1 해소 경로 택1 — **경로 A: 해소 (multiplex 불요, 별도 채널 default 확정)**

T2-5 stream_protocol.md **§8.4 현 시점 결론** (L802-L806):

> **별도 채널 유지** — `../05_glass-hud-overlay/realtime_update.md` §4.5 default 결정과 **일치**.
>
> > `[T2-6 확정 시 재검토]` — T2-6 07_orchestration-layer 세션에서 I-10 이벤트 오케스트레이션 규약
> > 확정 후, 공용 multiplex 이득이 실패 격리 손실을 초과하면 본 §8 결정을 갱신한다. 그 시점까지
> > `ChannelId` 필드는 envelope 예비로 정의만 유지.

**본 세션 (T2-6) 판정**: **경로 A — 해소: 별도 채널 default 확정, multiplex 불요, `[T2-6 확정 시 재검토]`
주석 [SKIP] 로 전환 가능.**

### §4.2 해소 근거

T2-5 §8.2 장단점 표 및 §8.3 공용 multiplex 조건을 I-10 오케스트레이션 관점에서 재검토:

| 조건 (T2-5 §8.3) | I-10 관점 검토 (본 세션) | 충족 여부 |
|-------------------|--------------------------|-----------|
| envelope `channel: ChannelId` 의무 필드 | `OrchestrationEvent` (ui_state_mapping §3.1) 는 `channel` 필드 없음 (I-10 은 `event_type` 1종 `oc.i10.ui.state.emitted` 로 충분) | ❌ 미충족 — 추가 필드 불필요 |
| 채널 내부 독립 seq | I-10 은 `emitted_at_ms` timestamp 만 필요, seq 규약 없음 | ❌ 불필요 |
| heartbeat 공유 | stream 은 loss-sensitive(R-611-4), HUD 는 eventual consistency — 재연결 정책 상이, 공유 heartbeat 은 손실 | ❌ 손실 |
| 라우팅 테이블 | 별도 채널에서 라우팅 단순 (EventSource 2개 독립) | ❌ 불필요 |
| 부하 테스트 1000 세션 | V1 범위 미증명, Phase 3 성능 벤치마크 대기 | ❌ 미검증 |

→ **공용 multiplex 5 조건 전수 미충족**. 별도 채널 default 유지가 I-10 관점에서도 최적.

### §4.3 추가 근거: I-10 이벤트 vs 스트림 이벤트 성격 차이

| 성격 | I-10 이벤트 (`oc.i10.ui.state.emitted`) | 스트림 이벤트 (`StreamChunk`) |
|------|----------------------------------------|-----------------------------|
| 빈도 | 상태 전이 시 1회 (trace 당 1~10회) | 토큰당 1회 (trace 당 수백~수천회) |
| 크기 | ~1~3 KB (5축 필드) | ~10~200 B (토큰 1개) |
| loss-sensitivity | eventual consistency 허용 (재전송 가능, diff 적용) | loss-sensitive (R-611-4 토큰 순서 보장 필수) |
| 전송 채널 | T2-4 realtime_update SSE 6 이벤트 (hud.*) | T2-5 stream_protocol SSE (`/api/hologram/stream`) |

→ **실패 격리 손실 > multiplex 이득**. `ChannelId` 예비 필드는 유지(T2-5 §3.1 L178), 실 활성화 Phase 3
성능 벤치마크 대기.

### §4.4 본 세션 결정 — T2-5 §8.4 주석 전환 제안

> **T2-5 `stream_protocol.md` §8.4 주석 변경 제안**:
>
> ```
> [T2-6 확정 시 재검토] → [T2-6 RESOLVED 2026-04-19 — 경로 A: multiplex 불요, 별도 채널 default 확정]
> ```

> **주의**: 본 세션 (T2-6 #2b-3) 은 sandbox-only, production UNCHANGED. 실 주석 교체는 **#2b-4 도메인
> 마감** 또는 **Phase 3 진입 시점** 에서 처리 (본 세션은 결정만 기록).

### §4.5 채널 정책 (별도 채널 default 확정)

| 채널 | 엔드포인트 | 생산 주체 | 소비 주체 | 수명 |
|------|----------|----------|----------|------|
| **Stream Canvas** | `/api/hologram/stream?trace_id=...` | Main LLM proxy (6-9 Brain-Adapter-HAL) | Center Panel StreamingArea | Chat 페이지 안에서만 |
| **HUD Events** | `/api/hologram/hud/stream?trace_id=...` | Front Mini (aggregator) | Right Panel Glass HUD | Chat 페이지 안에서만 |

두 채널 모두 **Chat 페이지 진입 시 개시, 이탈 시 close()** (§5.3 이탈 정책).

---

## §5. 페이지 전환 × Hologram View 상태 보존·초기화 정책

### §5.1 전환 유형 3가지

| 유형 | 예 | Hologram View 처리 |
|------|---|-------------------|
| **A. Chat → Chat** | `/chat/:a` → `/chat/:b` (세션 변경) | 기존 세션 **보존** (최근 3 세션 스냅샷 유지), 새 세션 UI 초기화 |
| **B. Chat → 비-Chat** | `/chat/:a` → `/log/:x` | 진행 중 trace 있으면 **confirm** ("스트림 중단 후 이동?"), 확인 시 Stream Canvas 언마운트 + HUD unmount |
| **C. 비-Chat → Chat** | `/dashboard` → `/chat/:new` | 신규 HUD mount + 2 채널 개시 (§4.5) |

### §5.2 전환 trigger 이벤트 매트릭스 (ui_state_mapping §7.3 + 본 문서 Mapping)

| 이벤트 | 출발 페이지 | 도착 페이지 | Layout 전환 | HUD 처리 |
|-------|-------------|-------------|-------------|----------|
| `USER_SELECT_CHAT` | Dashboard / Workflow / Memory / Settings / Log / NodeDetail | Chat | `* → HOLOGRAM` | 신규 mount |
| `USER_NAVIGATE_DASHBOARD` | * | Dashboard | `* → THREE_COLUMN` | unmount (if Chat) |
| `USER_SELECT_BUILDER` | * | Workflow | `* → BUILDER` | unmount (if Chat) |
| `USER_NAVIGATE_MEMORY` | * | Memory | `* → THREE_COLUMN` | unmount (if Chat) |
| `USER_NAVIGATE_SETTINGS` | * | Settings | `* → THREE_COLUMN` | unmount (if Chat) |
| `USER_NAVIGATE_LOG` | * | Log | `* → THREE_COLUMN` | unmount (if Chat) |
| `USER_SELECT_NODE(node_id)` | Workflow | NodeDetail | `BUILDER → BUILDER` | unmount (if Chat) |
| `USER_SELECT_CLI` | * | (CLI overlay) | `* → CLI` | unmount (if Chat) |
| `WORKFLOW_START` | Workflow | Chat | `BUILDER → HOLOGRAM` | 신규 mount + 2 채널 개시 |

### §5.3 Chat → 비-Chat 이탈 시 초기화·보존 규약

**UI 처리**:
1. **진행 중 trace 확인** — `UserResponse.is_streaming == true` (T2-2 §3.1 L170-171) 시 confirm dialog.
2. **confirm 통과 시**:
   - Stream Canvas 언마운트 → `scheduleTokenFlush` 취소 (T2-5 token_rendering §7.1) + 버퍼 비우기.
   - ArtifactZone 상태 `STREAMING` 이면 강제 `FINALIZED` 전이 (T2-5 artifact_rendering §3.3) — 부분 렌더
     결과 보존, 이후 재진입 시 `INTERACTIVE` 에서 복원.
   - HUD unmount → `scheduleHudFlush` 취소 (T2-4 realtime_update §4.6).
   - 2 채널 close() — `/api/hologram/stream` + `/api/hologram/hud/stream`.
3. **보존 대상 store**:
   - `chatStore` 최근 3 세션 (메시지 히스토리) — persist.
   - `evidenceStore` / `costStore` / `approvalStore` / `notificationStore` 현재 trace 스냅샷 — persist.
   - `timelineStore` / `logStore` 전수 persist (Log 페이지에서 조회).
4. **초기화 대상**:
   - `scheduleTokenFlush` / `scheduleHudFlush` 내부 버퍼 — clear.
   - ArtifactZone 인스턴스 DOM ref — clear (재진입 시 재mount).

**이벤트 발행**: `oc.i10.ui.state.emitted` 재발행 (`current_layout` 필드 갱신, ui_state_mapping §7.3).

### §5.4 비-Chat → Chat 진입 시 mount 규약

1. Chat 페이지 mount → `ChatPage.tsx` 진입점 실행.
2. 세션 복원: `chatStore` 에서 최근 세션 조회, 없으면 신규 세션 생성.
3. HUD mount (Right Panel, T2-4 rendering_rules §2.1 Option A Fixed HUD).
4. 2 채널 개시 — `/api/hologram/stream` + `/api/hologram/hud/stream` (T2-5 stream_protocol §8.1).
5. `oc.i10.ui.state.emitted` 최초 발행 — `current_layout="HOLOGRAM"` + `state_name="UI_S1_IDLE"`.

### §5.5 Chat → Chat (세션 변경) 규약

1. 기존 세션 스냅샷 → `chatStore` persist (최근 3 세션 상한, LRU).
2. Stream Canvas 내부 메시지 버퍼 → 신규 세션 인스턴스 교체.
3. HUD 재초기화 → `evidenceStore` / `costStore` / `approvalStore` 신규 세션 값으로 reset.
4. 기존 trace 진행 중이면 background 유지 옵션 (Phase 3 이월, V1 은 일괄 중단).
5. `oc.i10.ui.state.emitted` 재발행 — `session_id` 갱신.

---

## §6. Hologram View Chat 전용 제약 — 구현 체크리스트

### §6.1 라우터 guard

```typescript
// router/guards/hologramView.ts
export function hologramViewGuard(to: Route): boolean {
  if (isHologramComponent(to.matchedComponents)) {
    // Hologram View 컴포넌트 (HUD/StreamCanvas/HologramTimeline) 는 Chat 페이지에서만 허용
    return to.path.startsWith("/chat/");
  }
  return true;
}
```

### §6.2 런타임 체크

```typescript
// components/glass-hud/GlassHUDContainer.tsx 의 mount 시
export function GlassHUDContainer(): JSX.Element | null {
  const currentPath = useLocation().pathname;
  if (!currentPath.startsWith("/chat/")) {
    console.warn("[VIOLATION: HologramView-Chat-only]", { path: currentPath });
    return null;  // 강제 미렌더
  }
  // ... 정상 렌더
}
```

### §6.3 제약 위반 탐지

- **정적 탐지**: lint 규칙 — `GlassHUDContainer` / `StreamingArea` / `HologramTimeline` 을 import 하는
  페이지 컴포넌트가 `ChatPage.tsx` 외면 경고.
- **런타임 탐지**: §6.2 체크 + WARN 로그 `hologram.orchestration.chat_only_violation`.

### §6.4 예외 처리

**허용 예외 0건** (Chat 페이지 외 Hologram View 절대 불가). 제약 완화 요청 시 LOCK 개정 필요
(LOCK-HM-07 + 6-1 정본 양측 갱신 수반).

---

## §7. 로깅 포맷 (R-01-7 구조화 JSON)

### §7.1 이벤트 네임스페이스

| 이벤트 | 트리거 | 레벨 | 필수 필드 |
|-------|-------|------|-----------|
| `hologram.orchestration.page_navigated` | 페이지 전환 (라우터 listen) | INFO | `trace_id`, `i10{}`, `from_page`, `to_page`, `layout_transition` |
| `hologram.orchestration.hologram_mounted` | Chat 페이지 mount + HUD + 2 채널 개시 | INFO | `trace_id`, `i10{}`, `channels_opened[]` |
| `hologram.orchestration.hologram_unmounted` | Chat 이탈 시 HUD + 2 채널 close | INFO | `trace_id`, `i10{}`, `preserved_stores[]`, `cleared_buffers[]` |
| `hologram.orchestration.chat_only_violation` | 비-Chat 페이지에서 Hologram 컴포넌트 mount 시도 | WARN | `path`, `component` |
| `hologram.orchestration.permission_denied` | 페이지 권한 검증 실패 | ERROR | `trace_id`, `page`, `required_role`, `user_role` |

### §7.2 구조화 로그 예시 — 페이지 전환

```json
{
  "ts": "2026-04-19T12:34:56.789Z",
  "level": "INFO",
  "event": "hologram.orchestration.page_navigated",
  "trace_id": "01HV8M3J7K9P2Q4R6S8T",
  "i10": {
    "interface": "emit_ui_state",
    "event_source": "page_routing"
  },
  "from_page": "workflow",
  "to_page": "chat",
  "layout_transition": "BUILDER→HOLOGRAM",
  "event_name": "WORKFLOW_START"
}
```

### §7.3 구조화 로그 예시 — Hologram mount

```json
{
  "ts": "2026-04-19T12:34:56.789Z",
  "level": "INFO",
  "event": "hologram.orchestration.hologram_mounted",
  "trace_id": "01HV8M3J7K9P2Q4R6S8T",
  "i10": {
    "interface": "emit_ui_state"
  },
  "channels_opened": ["/api/hologram/stream", "/api/hologram/hud/stream"]
}
```

### §7.4 구조화 로그 예시 — Chat 이탈

```json
{
  "ts": "2026-04-19T12:34:56.789Z",
  "level": "INFO",
  "event": "hologram.orchestration.hologram_unmounted",
  "trace_id": "01HV8M3J7K9P2Q4R6S8T",
  "i10": {
    "interface": "emit_ui_state"
  },
  "preserved_stores": ["chatStore", "evidenceStore", "costStore", "approvalStore", "notificationStore", "timelineStore", "logStore"],
  "cleared_buffers": ["scheduleTokenFlush", "scheduleHudFlush", "ArtifactZone.domRef"]
}
```

---

## §8. Phase 3 테스트 시나리오 (12건, ≥10 요건 초과)

| ID | 시나리오 | 입력 | 기대 결과 | 참조 |
|----|---------|------|-----------|------|
| **TS-PR-01** | 7 페이지 경로 전수 매핑 | Dashboard/Chat/Workflow/Memory/Settings/Log/NodeDetail 7 경로 | 7 진입점 mount + Layout 매핑 일치 | §3.1 |
| **TS-PR-02** | Hologram View = Chat 전용 제약 | 비-Chat 페이지에서 `<GlassHUDContainer/>` mount 시도 | 렌더 차단 + WARN 로그 `chat_only_violation` | §6.2, §7.1 |
| **TS-PR-03** | Chat → Log 이탈 시 Stream Canvas 언마운트 | `/chat/:a` (is_streaming=true) → `/log/:x` (confirm 통과) | Stream Canvas 언마운트 + 2 채널 close + `hologram_unmounted` INFO | §5.3, §7.4 |
| **TS-PR-04** | Dashboard → Chat 진입 시 HUD mount | `/` → `/chat/:new` | HUD mount + 2 채널 개시 + `hologram_mounted` INFO | §5.4, §7.3 |
| **TS-PR-05** | Chat → Chat (세션 변경) persist | `/chat/:a` → `/chat/:b` | `chatStore` LRU 3 세션 유지 + HUD 재초기화 | §5.5 |
| **TS-PR-06** | Workflow → Chat (WORKFLOW_START) | `/workflow/:x` → `/chat/:auto` | Layout `BUILDER→HOLOGRAM` + 2 채널 개시 | §5.2, §4.5 |
| **TS-PR-07** | 권한 미충족 페이지 접근 차단 | `member` 역할로 `/settings/billing` 접근 | `permission_denied` ERROR + 라우터 리다이렉트 | §3.10, §7.1 |
| **TS-PR-08** | CLI Layout 전환 | `/chat/:a` + `USER_SELECT_CLI` | Layout `HOLOGRAM→CLI` + HUD unmount | §2.2, §5.2 |
| **TS-PR-09** | Log 페이지 trace_id 포커스 | `/log/:trace_id=01HV...` | TraceTimeline 포커스 + TraceLogPanel 필터 | §3.7 |
| **TS-PR-10** | NodeDetail → Workflow 복귀 | `/node/:n` → `/workflow/:w` | Layout `BUILDER` 유지, 편집 상태 복원 | §3.8 |
| **TS-PR-11** | T2-5 §8.4 해소 경로 A 검증 | I-10 이벤트 + 스트림 이벤트 동시 발행 | 별도 채널 default, multiplex 불요 | §4.1, §4.4 |
| **TS-PR-12** | Chat 이탈 시 ArtifactZone FINALIZED 강제 전이 | `/chat/:a` (ArtifactZone STREAMING) → `/memory` | 강제 FINALIZED + 부분 렌더 스냅샷 persist | §5.3 |

---

## §9. 신규 CONFLICT_CANDIDATE — 없음

본 세션 추가 발견 0건. `ui_state_mapping.md` §11.1 의 **CONF-HM-008 9-State 네이밍 drift** 는 그곳
1회 등재, 본 문서 중복 등재 금지 (V1 immutability 원칙).

---

## §10. 산출물 요약

- **정의 대상**: 7 페이지 라우팅 + Hologram View Chat 전용 제약 + T2-5 §8.4 주석 해소.
- **핵심 정의**:
  - §2 7 페이지 개요 + Layout × 페이지 매핑.
  - §3 경로·진입점·컴포넌트·권한 테이블 (`/` / `/chat/:session_id?` / `/workflow/:workflow_id?` / `/memory/:filter?` / `/settings/:section?` / `/log/:trace_id?` / `/node/:node_id`).
  - §3.9 Hologram View Chat 전용 제약 정본 근거 3종 (LOCK-HM-07 + 6-1 02_hologram-view + T2-4 rendering_rules).
  - §3.10 권한 조건 매트릭스 + 6-2 Security-Governance 경계.
  - §4 T2-5 stream_protocol §8.4 `[T2-6 확정 시 재검토]` 주석 해소 — **경로 A: 해소 (multiplex 불요, 별도 채널 default 확정)** 택1, 근거 5 조건 전수 미충족.
  - §5 페이지 전환 × Hologram View 상태 보존·초기화 정책 (Chat↔Chat / Chat↔비-Chat / 비-Chat↔Chat 3 유형).
  - §6 Chat 전용 제약 구현 체크리스트 (라우터 guard + 런타임 체크 + 탐지 + 예외 0).
  - §7 R-01-7 구조화 JSON 로깅 (`hologram.orchestration.page_navigated` / `hologram_mounted` / `hologram_unmounted` / `chat_only_violation` / `permission_denied`).
  - §8 Phase 3 시나리오 12건.
- **V2↔V2 cross-ref**: 15건 PASS (ui_state_mapping 2 + cost_evidence_log 1 + T2-4 overlay 1 + T2-4 realtime 1 + T2-4 rendering 1 + T2-5 stream 4 + T2-5 token 1 + T2-5 artifact 1 + T2-1 2 + T2-2 1).
- **CONFLICT_CANDIDATE**: 0건 신규 (ui_state_mapping §11.1 CONF-HM-008 중복 등재 금지).
- **LOCK 준수**: LOCK-HM-02 4 Layout verbatim / LOCK-HM-07 ChatPage.tsx 진입점 verbatim / LOCK-HM-05 `current_layout` 전파 / LOCK-HM-01 3-Pane Chat 페이지 안에서만 활성.
- **ISS 해소**: ISS-15 (7 페이지 라우팅 주축 해소).
- **T2-5 §8.4 해소 기록**: 경로 A (해소, multiplex 불요) 택1 — 본 세션 판정. 실 주석 교체는 #2b-4 또는 Phase 3 이월.
- **파일 위치**:
  - sandbox: `D:\VAMOS\docs\test_iso_p2\sot 2\6-11_Hologram-Main-LLM\07_orchestration-layer\page_routing.md`
  - production: `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\07_orchestration-layer\page_routing.md` (production-promoted 2026-06-03 Phase 4)

---

**[END OF page_routing.md — V2-Phase 2 v1.0]**
