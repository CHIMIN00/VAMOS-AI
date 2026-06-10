# cost_evidence_log.md — I-10 Cost / Evidence / Approval / Log 분배 변환 규칙

| 항목 | 값 |
|------|----|
| **도메인** | 6-11_Hologram-Main-LLM / 07_orchestration-layer |
| **세션 (TASK_ID)** | Phase 2 T2-6 (6-11_T2-6_02) |
| **산출물 경로 (sandbox)** | `D:\VAMOS\docs\test_iso_p2\sot 2\6-11_Hologram-Main-LLM\07_orchestration-layer\cost_evidence_log.md` |
| **정본 산출물 경로 (production)** | `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\07_orchestration-layer\cost_evidence_log.md` |
| **LOCK** | **LOCK-HM-05** (I-10 UI 오케스트레이션 — D2.0-02 §7.63), **LOCK-HM-10** (Glass HUD Evidence/Cost/Approval/Alert — D2.0-08 §2.2.2 L255-265), 보조: **LOCK-HM-06** (3-point `evidence_summary`/`log_report`), **LOCK-HM-03** (9-State 전이 `Cost-Alert` 참고) |
| **정본 소유** | 6-11 DEFINED-HERE — I-10 수신 데이터 `UiStatePayload` 를 Glass HUD / Timeline / LogDetail 에 분배하는 **변환 파이프라인** + **store 쓰기 순서 규약** + **단일 프레임 flush 정합** + **S7B-027 멀티 대화 V2 확장 포인트 주석**. `GlassHUDData` 스키마 본체는 T2-4 `overlay_schema.md` 정본 (본 문서는 변환 규칙만). |
| **해소 이슈** | **ISS-07** (I-10 오케스트레이션 데이터 분배 변환 규칙 — 본 문서 해소) |
| **Phase 배정** | Phase 2 T2-6 |
| **Part2 버전 태그** | V2-Phase 2 (Enhanced Hologram) |
| **작성일** | 2026-04-19 |
| **Version** | v1.0 (초안) |
| **TEST_MODE** | false — Phase 4 production promotion 2026-06-03 (sandbox → production 전환 완료) |

---

## §0. 목적 & Scope

### §0.1 목적

I-10 UI·오케스트레이션 레이어가 `emit_ui_state(trace_id, ui_state) -> ok` 를 통해 집계한 **5축 데이터**
(cost / evidence / approval / alerts / log) 를 Builder/Hologram UI 의 세부 컨테이너(Glass HUD /
Timeline / LogDetail) 로 **분배하는 변환 파이프라인** 을 확정한다.

- **입력**: `ui_state_mapping.md` §3 `UiStatePayload` (본 폴더 중앙 정의에서 import, 재정의 금지).
- **출력**: T2-4 `overlay_schema.md` §3 정의 `GlassHUDData` 하위 타입 4종
  (`CostSnapshot` / `EvidenceHudSnapshot` / `ApprovalRequest` / `UncertaintyAlertList`) + Timeline·LogDetail
  레코드.
- **store 쓰기 순서**: `evidenceStore → costStore → approvalStore → notificationStore` verbatim (T2-4
  overlay_schema §3 L298-L300, `HudMeta.store_write_order` 정본).
- **RAF 16ms 창 단일 프레임 flush**: HUD(T2-4 realtime_update §4.6) + 토큰(T2-5 token_rendering §7.1) +
  ArtifactZone(T2-5 artifact_rendering §3.3) 3축 동시 트리거 시 프레임 누락 방지 — `ui_state_mapping.md`
  §5.4 `scheduleUnifiedFlush()` 호출 경로 공유.
- **Cost-Alert (alert item)** — `cost.ratio_to_budget >= 0.8` 은 **CostGauge 게이지/색상 표시 임계** (§4.5: 0.8~1.0 노랑 / >=1.0 빨강, `hud.cost.update` 발행 §4.4). **alert 항목**은 `>= 0.95` (임박) / `>= 1.0` (초과) 에서만 `UiStatePayload.alerts[]` 에 `UncertaintyAlertItem(kind="LOW_QOD", message="Cost ...")` 로 추가 (§4.3, LOCK-HM-10 3종 verbatim — Cost 전용 kind 신설 금지).
- **S7B-027 멀티 대화 V2 확장 포인트**: `parent_session_id` 별 HUD·Timeline 병렬 집계 (V1 구현 외, 본
  문서 §9 주석 처리).

### §0.2 Scope 표

| 구분 | 범위 |
|------|------|
| **In** (본 문서에서 확정) | (a) I-10 `UiStatePayload` → Glass HUD `GlassHUDData` 하위 타입 4종 변환 파이프라인(§3~§6), (b) `cost` → `CostSnapshot` + Cost-Alert 임계 판정 + `hud.cost.update` SSE 트리거(§4), (c) `evidence` + `alerts` → `EvidenceHudSnapshot` + `UncertaintyAlertList` + `hud.evidence.update` / `hud.alert.raise` / `hud.alert.dismiss` SSE 트리거(§3·§6), (d) `approval` → `ApprovalRequest` + 슬라이드 인 트리거 + `hud.approval.update` SSE(§5), (e) `log` → Timeline + LogDetail 이중 기록 분기(§7), (f) `store_write_order` evidenceStore → costStore → approvalStore → notificationStore verbatim 준수 규약(§8.1), (g) RAF 16ms 창 단일 프레임 flush 정합(§8.2), (h) R-01-7 구조화 로깅(§10), (i) S7B-027 멀티 대화 V2 확장 포인트 주석(§9), (j) Phase 3 시나리오 12건 TS-CEL-01~12(§11). |
| **Out** (타 세션/문서 위임) | (a) `UiStatePayload` / `ArtifactRef` / `OrchestrationEvent` 공통 자료 구조 중앙 정의 → **`ui_state_mapping.md` §3 (본 폴더 유일)**, (b) 9-State × 3-point 바인딩 매트릭스 → **`ui_state_mapping.md` §4**, (c) Layout 전환 프로토콜(ISS-13) → **`ui_state_mapping.md` §7**, (d) 7페이지 라우팅(ISS-15) → **`page_routing.md` (본 세션 peer)**, (e) `GlassHUDData` / `CostSnapshot` / `EvidenceHudSnapshot` / `ApprovalRequest` / `UncertaintyAlertList` / `HudMeta` Pydantic + TypeScript 스키마 본체 → **T2-4 `overlay_schema.md` §3 (유일 정본)**, (f) SSE 6 이벤트 프로토콜·라인 포맷·재연결 → **T2-4 `realtime_update.md`**, (g) `scheduleHudFlush()` / `scheduleTokenFlush()` 개별 구현 → **T2-4 §4.6 / T2-5 §7.1 (유일 정본)**, (h) `qod_score` 산출 알고리즘 → **1-1 Verifier-Reasoning-Engines**, (i) `evidenceStore`/`costStore`/`approvalStore`/`notificationStore` 내부 구조 → **Phase 1 V1 `store_catalog.md`**. |
| **관련 이슈** | **ISS-07** (I-10 오케스트레이션 변환 규칙 본 문서 해소) |

### §0.3 도메인 경계 선언 (R-T6-2 / R-T6-4)

- **6-11 소유** (본 문서): I-10 → 하위 UI 컨테이너 **분배 규칙 · 변환 함수 · 쓰기 순서 규약 · RAF 정합**.
- **T2-4 `overlay_schema.md` 소유**: `GlassHUDData` 스키마 본체 + `qod_score` → VerificationBadge
  매핑 테이블 + `store_write_order` 정본 (본 문서는 verbatim 준수 소비).
- **1-1 Verifier-Reasoning-Engines 소유**: `qod_score` 산출 알고리즘 (본 문서는 표시 대상 값만 수신).
- **6-12 Event-Logging 소유**: Timeline / LogDetail 저장 인프라 (본 문서는 이벤트 발행 규약만 정의).
- **6-2 Security-Governance 소유**: 승인 권한 조건(Admin/Member 등, `page_routing.md` 참조).

---

## §1. 교차 참조 블록

### §1.1 상위 정본 (LOCK 근거 표)

| 참조 문서 | 섹션 / 라인 | 역할 |
|-----------|-------------|------|
| `../../../sot/D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md` | §7.63 (L2091-2119) | **LOCK-HM-05 정본** — I-10 `emit_ui_state` payload 5축 verbatim. STEP7 S7B-027 멀티 대화 V2 확장 근거(§9) |
| `../../../sot/D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` | §2.2.2 (L255-265) | **LOCK-HM-10 정본** — Evidence/Cost/Approval/Uncertainty Alert 4 구성 요소 + qod_score 3등급 |
| `../../../sot/D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` | §7.2 (L359-368) | **LOCK-HM-06** — 3-point `evidence_summary` / `log_report` 변환 원천 |
| `../../../sot/D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` | §4.1 (L335-344) | **LOCK-HM-03** — 9-State 전이 시점 근거 |

### §1.2 AUTHORITY_CHAIN / CONFLICT_LOG

| 참조 문서 | 섹션 | 확인 사항 |
|-----------|------|-----------|
| `../AUTHORITY_CHAIN.md` | L104-L110 | **LOCK-HM-05 verbatim** (ui_state_mapping §2.1 과 공통 근거) |
| `../AUTHORITY_CHAIN.md` | L131-L140 | **LOCK-HM-10 verbatim** — Evidence 3등급 + Cost 임계 + Approval 슬라이드 인 + Alert 3종 |
| `../CONFLICT_LOG.md` | — | CFL-HM-001~007 + C-1~C-3 RESOLVED, OPEN 0. 본 세션 신규 CONFLICT_CANDIDATE 0 (9-State 네이밍 drift 는 `ui_state_mapping.md` §11 에 등재, 본 문서 중복 등재 안 함) |

### §1.3 로컬 Phase 1 산출물 (입력 근거)

| 파일 | 역할 |
|------|------|
| `../02_component-architecture/store_catalog.md` §3 | `evidenceStore` / `costStore` / `approvalStore` / `notificationStore` / `timelineStore` / `logStore` Zustand store — 본 문서 §5~§7 쓰기 대상 |
| `../02_component-architecture/hook_catalog.md` | `useEvidence` / `useCost` / `useApproval` / `useLog` / `useTimeline` 훅 — 본 문서 §3~§7 변환 파이프라인 진입점 |
| `../02_component-architecture/component_catalog.md` | HV-EVID-01/02 EvidencePanel/Badge + Glass HUD CostGauge/ApprovalCard + LOG-DASH-02 TraceTimeline + BV-DEBUG-01 TraceLogPanel — 본 문서 §5~§7 UI 타겟 |
| `../03_ui-state-machine/state_definitions.md` | 9-State 전이 이벤트 매트릭스 — `Cost-Alert` 파생 전이 근거 |

### §1.4 Peer V2 세션 이음매 (V2↔V2 cross-reference ≥13 목표)

| peer V2 | 경로 | 섹션·라인 근거 | 본 문서 접점 |
|---------|------|----------------|-------------|
| **`ui_state_mapping.md`** (sibling, T2-6 #2b-3 본 세션) | `./ui_state_mapping.md` | §3 `UiStatePayload` 중앙 정의 + §5 축별 바인딩 훅 표 | 본 문서 §3~§7 import 소비, 재정의 0. §3.4 JSON 예시와 field 이름 1:1 |
| **`ui_state_mapping.md`** (sibling) | `./ui_state_mapping.md` | §5.4 `scheduleUnifiedFlush()` RAF 정합 의사코드 | 본 문서 §8.2 동일 RAF 창에서 HUD·토큰·ArtifactZone 3축 flush 규약 공유 |
| **T2-1 `two_tier_routing.md`** (857줄) | `../04_main-llm-integration/two_tier_routing.md` | **§4 L448** `FM->>EL: emit(oc.i10.ui.state.emitted, trace_id, ui_state)` verbatim + **L729** `oc.i10.ui.state.emitted` INFO | 본 문서 §2.1 발행 시점 + §10 로깅 레벨 일치 |
| **T2-1 `two_tier_routing.md`** (857줄) | `../04_main-llm-integration/two_tier_routing.md` | **§3.1 L140** `TraceId = str  # ULID` | 본 문서 §3 `trace_id` 타입 공유 (ui_state_mapping §3 경유 import) |
| **T2-4 `overlay_schema.md`** (898줄) | `../05_glass-hud-overlay/overlay_schema.md` | **§3** `GlassHUDData` 5 필드 고정 + 하위 타입 5종 (`CostSnapshot` / `EvidenceHudSnapshot` / `ApprovalRequest` / `UncertaintyAlertList` / `HudMeta`) | 본 문서 §3~§6 **import 소비만**, 재정의 0 |
| **T2-4 `overlay_schema.md`** (898줄) | `../05_glass-hud-overlay/overlay_schema.md` | **§3 L298-L300** `HudMeta.store_write_order = ["evidenceStore","costStore","approvalStore","notificationStore"]` verbatim | 본 문서 §8.1 쓰기 순서 verbatim 준수 |
| **T2-4 `overlay_schema.md`** (898줄) | `../05_glass-hud-overlay/overlay_schema.md` | **§3.4** qod_score → verification 매핑 테이블 (LOCK-HM-10 verbatim) | 본 문서 §3.3 import — 매핑 재정의 금지 |
| **T2-4 `realtime_update.md`** (591줄) | `../05_glass-hud-overlay/realtime_update.md` | **§3.1** SSE 6 이벤트 (`hud.cost.update` / `hud.evidence.update` / `hud.approval.update` / `hud.alert.raise` / `hud.alert.dismiss` / `hud.meta.update`) | 본 문서 §4~§7 각 변환 후 해당 SSE 이벤트 트리거 (ui_state_mapping §5.3 분기 매트릭스 동일) |
| **T2-4 `realtime_update.md`** (591줄) | `../05_glass-hud-overlay/realtime_update.md` | **§4.6** `scheduleHudFlush()` RAF 16ms/60fps | 본 문서 §8.2 단일 프레임 flush 정합 보장 |
| **T2-4 `rendering_rules.md`** (490줄) | `../05_glass-hud-overlay/rendering_rules.md` | **§3 z-index 계층** (HUD 150 / Alert 200 / Modal 300) | 본 문서 §5.3 Cost-Alert 토스트 z-index 200 (정합) |
| **T2-5 `stream_protocol.md`** (1,083줄) | `../06_streaming-canvas/stream_protocol.md` | **§3.1 L178** `ChannelId = Literal["stream","hud"]` | 본 문서 §7.2 `hud.*` SSE 이벤트 채널 = `ChannelId="hud"` 계열 |
| **T2-5 `stream_protocol.md`** (1,083줄) | `../06_streaming-canvas/stream_protocol.md` | **§8.1** 별도 채널 default `/api/hologram/hud/stream` | 본 문서 §7.2 채널 정책 (`page_routing.md` §4 해소 결과 소비) |
| **T2-5 `token_rendering.md`** (772줄) | `../06_streaming-canvas/token_rendering.md` | **§7.1** `scheduleTokenFlush()` RAF 16ms | 본 문서 §8.2 단일 프레임 flush 정합 (ui_state_mapping §5.4 와 공통 패턴 공유) |
| **T2-2 `response_formatting.md`** (911줄) | `../04_main-llm-integration/response_formatting.md` | **§3.1** `UserResponse` / `EvidenceSummary` / `LogReport` 3-point 필드 | 본 문서 §3.2 / §6.1 / §7.1 각각의 변환 입력 소스 |
| **T2-3 `dcl_context.md`** (865줄) | `../04_main-llm-integration/dcl_context.md` | **§3.2 L206-L216** `ActiveWorkflow.qod_hint` | 본 문서 §3.3 `EvidenceHudSnapshot.qod_hint_initial` 초기 힌트 경유 규칙 |

> **합계 15 cross-ref** (ui_state_mapping 2 + T2-1 2 + T2-4 overlay 3 + T2-4 realtime 2 + T2-4 rendering 1 + T2-5 stream 2 + T2-5 token 1 + T2-2 1 + T2-3 1). 실측 섹션·라인 verbatim 대조 완료. 목표 ≥13 달성.

### §1.5 Cross-domain Read-only 소비

| 도메인 | 범위 | 본 문서 관계 |
|--------|------|-------------|
| **6-12 Event-Logging** | R-01-7 구조화 JSON + Timeline / LogDetail 저장 인프라 | 본 문서 §7 + §10 로깅 포맷 |
| **1-1 Verifier-Reasoning-Engines** | `qod_score` 산출 알고리즘 | 본 문서 §3 표시 대상 값 수신만 |
| **6-9 Brain-Adapter-HAL** | `emit_ui_state` 호출 주체 | 본 문서 §2.1 호출 시점 주석 |

> CROSS_DOMAIN_DEPS=none (envelope L30-31). 단방향 Read-only 소비만 존재.

---

## §2. I-10 수신 데이터 진입점 (ui_state_mapping §3 `UiStatePayload` import)

### §2.1 발행 시점 (T2-1 §4 L448 verbatim + ui_state_mapping §5.1 공유)

```
FM->>EL: emit(oc.i10.ui.state.emitted, trace_id, ui_state)
```

본 문서의 모든 변환은 위 이벤트 수신 시점 이후 트리거.

### §2.2 진입 스키마

`ui_state_mapping.md` §3.1 `UiStatePayload` **import 소비** — 재정의 금지.

```python
from ..orchestration.models import (
    UiStatePayload,
    CostSlice,
    EvidenceSlice,
    ApprovalSlice,
    AlertItem,
    LogSlice,
    TraceId,
)
# overlay_schema.md §3 import — 스키마 본체 재정의 금지
from ...glass_hud.overlay.models import (
    GlassHUDData,
    CostSnapshot,
    EvidenceHudSnapshot,
    ApprovalRequest,
    UncertaintyAlertList,
    UncertaintyAlertItem,
    HudMeta,
)
```

### §2.3 변환 진입점 함수

```python
def distribute_ui_state(payload: UiStatePayload) -> tuple[GlassHUDData, TimelineRecord, LogRecord]:
    """
    I-10 payload 1건 → Glass HUD 1건 + Timeline 1건 + LogDetail 1건 동시 생성.

    호출 순서 (LOCK-HM-05 §7.63 + HudMeta.store_write_order):
    1. evidence + alerts → EvidenceHudSnapshot + UncertaintyAlertList (§3, §6)
    2. cost → CostSnapshot + Cost-Alert 판정 (§4)
    3. approval → ApprovalRequest (§5)
    4. log → Timeline + LogDetail 이중 기록 (§7)
    """
    ...
```

---

## §3. Evidence 분배 변환 (`evidence` + `qod_hint_initial`)

### §3.1 원천 → 타겟 매트릭스

| 원천 (`UiStatePayload`) | 타겟 (`GlassHUDData`) | UI 컴포넌트 | Store |
|-------------------------|----------------------|-------------|-------|
| `evidence.qod_score` | `evidence.qod_score` | HV-EVID-02 EvidenceBadge (`VERIFIED`/`PARTIAL`/`UNVERIFIED`) + Glass HUD Verification Badge | `evidenceStore` |
| `evidence.source_count` | `evidence.source_count` | HV-EVID-01 EvidencePanel source list | `evidenceStore` |
| `evidence.qod_hint_initial` (T2-3 경유) | `evidence.qod_hint_initial` | 초기 Evidence HUD 힌트 표시 (hint 모드) | `evidenceStore` |

### §3.2 T2-2 `EvidenceSummary` → `EvidenceSlice` 브리지

T2-2 response_formatting.md §3.1 L192-* `EvidenceSummary` 필드를 `EvidenceSlice` 로 축약:

```python
def bridge_evidence(es_t2_2: "EvidenceSummary") -> EvidenceSlice:
    """T2-2 EvidenceSummary → I-10 EvidenceSlice 축약 변환."""
    return EvidenceSlice(
        qod_score=es_t2_2.qod_score,
        source_count=len(es_t2_2.sources),
        qod_hint_initial=None,  # T2-3 경유 시에만 값 (§3.3)
    )
```

### §3.3 T2-3 `ActiveWorkflow.qod_hint` 경유 (초기 힌트 경로)

T2-3 dcl_context.md §3.2 L206-L216 `ActiveWorkflow.qod_hint: Optional[float]` → `EvidenceSlice.qod_hint_initial`:

```python
def apply_qod_hint(slice_: EvidenceSlice, active_workflow_qod_hint: Optional[float]) -> EvidenceSlice:
    """T2-3 DCL 힌트 주입 — UI_S3_READY 진입 시 1회 적용."""
    if active_workflow_qod_hint is not None:
        return slice_.model_copy(update={"qod_hint_initial": active_workflow_qod_hint})
    return slice_
```

### §3.4 qod_score → VerificationBadge 등급 매핑 (T2-4 overlay_schema §3.4 verbatim import)

```
qod_score >= 0.8   → "VERIFIED"  (Green)
0.5 <= qod_score < 0.8 → "PARTIAL"  (Yellow)
qod_score < 0.5    → "UNVERIFIED" (Gray)
```

> **LOCK-HM-10 verbatim**. 본 문서는 테이블 재정의 금지, overlay_schema §3.4 참조만 허용.

### §3.5 분배 함수

```python
def distribute_evidence(
    evidence_slice: EvidenceSlice,
    trace_id: TraceId,
    state_name: str,
) -> EvidenceHudSnapshot:
    """EvidenceSlice → EvidenceHudSnapshot 변환."""
    # overlay_schema.md §3.6 build_evidence_hud_snapshot() 로 위임
    from ...glass_hud.overlay.builders import build_evidence_hud_snapshot
    return build_evidence_hud_snapshot(
        qod_score=evidence_slice.qod_score,
        source_count=evidence_slice.source_count,
        qod_hint_initial=evidence_slice.qod_hint_initial,
        hint_mode=(state_name == "UI_S3_READY" and evidence_slice.qod_hint_initial is not None),
    )
```

### §3.6 SSE 트리거

- 대상 이벤트: `hud.evidence.update` (T2-4 realtime_update §3.1).
- 트리거 조건: `state_name in {"UI_S6_PRESENTING"}` OR `qod_hint_initial` 값 변경.
- payload: `EvidenceHudSnapshot` 전체.

### §3.7 EvidencePanel 바인딩 (Right Panel — HV-EVID-01)

- `useEvidence().bind(EvidenceHudSnapshot)` → `evidenceStore.set(snapshot)`.
- UI 리렌더: `React.memo` + selector 기반 (T2-4 rendering_rules §6.1 패턴 계승).

---

## §4. Cost 분배 변환 (`cost` + Cost-Alert 판정)

### §4.1 원천 → 타겟 매트릭스

| 원천 (`UiStatePayload`) | 타겟 (`GlassHUDData`) | UI 컴포넌트 | Store |
|-------------------------|----------------------|-------------|-------|
| `cost.currency` | `cost.currency` | Glass HUD CostGauge 통화 표기 | `costStore` |
| `cost.amount` | `cost.amount` | Glass HUD CostGauge 수치 | `costStore` |
| `cost.threshold` | `cost.threshold` | Glass HUD CostGauge 임계선 | `costStore` |
| `cost.ratio_to_budget` | `cost.ratio_to_budget` | Glass HUD CostGauge % + 색상 변화 (≥0.8 노랑, ≥1.0 빨강) | `costStore` |

### §4.2 변환 함수 (`CostSlice` → `CostSnapshot`)

```python
def distribute_cost(cost_slice: CostSlice) -> CostSnapshot:
    """CostSlice → CostSnapshot 변환 (필드 1:1)."""
    return CostSnapshot(
        displayed=(cost_slice.ratio_to_budget >= 0.8),  # LOCK-HM-10 "임계치 근접 시만"
        currency=cost_slice.currency,
        amount=cost_slice.amount,
        threshold=cost_slice.threshold,
        ratio_to_budget=cost_slice.ratio_to_budget,
    )
```

> **LOCK-HM-10 verbatim** (AUTHORITY_CHAIN L139): "Cost: 임계치 근접 시만 게이지 노출". 본 함수의
> `displayed=(ratio_to_budget >= 0.8)` 조건이 이 규칙 구현.

### §4.3 Cost-Alert 상태 판정

`ratio_to_budget >= 1.0` (예산 초과) 또는 `>= 0.95` (임박) 시 `UiStatePayload.alerts[]` 에 Cost-Alert
항목 추가:

```python
def cost_alert_item(cost_slice: CostSlice) -> Optional[UncertaintyAlertItem]:
    """Cost 초과 시 Alert item 생성 — 'Cost-Alert' 는 별도 state 가 아닌 alert item 으로 표현."""
    if cost_slice.ratio_to_budget >= 1.0:
        return UncertaintyAlertItem(kind="LOW_QOD",  # Alert kind 3종 한정 — LOCK-HM-10 verbatim
                                     message=f"Cost exceeded: ratio={cost_slice.ratio_to_budget:.2f}",
                                     raised_at_ms=int(time.time() * 1000))
    if cost_slice.ratio_to_budget >= 0.95:
        return UncertaintyAlertItem(kind="LOW_QOD",
                                     message=f"Cost approaching: ratio={cost_slice.ratio_to_budget:.2f}",
                                     raised_at_ms=int(time.time() * 1000))
    return None
```

> **주의**: Alert `kind` 는 **LOCK-HM-10 3종** (`LOW_QOD`/`CONFLICTING_SOURCES`/`STALE_DATA`) verbatim.
> Cost-Alert 는 별도 kind 값 **신설 금지** — `LOW_QOD` + message prefix `Cost exceeded/approaching` 로 구현.
> `ui_state_mapping.md` §4.3 CONFLICT_CANDIDATE 주: "Cost-Alert 는 state 가 아닌 alert item" 재확인.

### §4.4 SSE 트리거

- 대상 이벤트: `hud.cost.update` (T2-4 realtime_update §3.1) — 5초 periodic 또는 `ratio_to_budget >= 0.8`
  최초 돌파 시 즉시.
- payload: `CostSnapshot` 전체 + 임계 돌파 시 `hud.alert.raise` 동시 발송 (Cost-Alert).

### §4.5 CostGauge 바인딩 (Right Panel — Glass HUD)

- `useCost().bind(CostSnapshot)` → `costStore.set(snapshot)`.
- 색상 변화: `ratio_to_budget < 0.8` 투명 / `0.8~1.0` 노랑 / `>= 1.0` 빨강 — 세부는 6-1 UI-UX-System
  정본 (본 문서 범위 외).

---

## §5. Approval 분배 변환 (`approval` → 슬라이드 인)

### §5.1 원천 → 타겟 매트릭스

| 원천 (`UiStatePayload`) | 타겟 (`GlassHUDData`) | UI 컴포넌트 | Store |
|-------------------------|----------------------|-------------|-------|
| `approval.request_id` | `approval.request_id` | HV-APPROVAL-01 ApprovalCard 요청 ID 표기 | `approvalStore` |
| `approval.status` | — (조건 판정) | ApprovalCard 슬라이드 인 활성화 조건 | `approvalStore` |

### §5.2 변환 함수

```python
def distribute_approval(approval_slice: ApprovalSlice, trace_id: TraceId) -> Optional[ApprovalRequest]:
    """ApprovalSlice → ApprovalRequest 변환. status != "REQUESTED" 면 null."""
    if approval_slice.status != "REQUESTED" or approval_slice.request_id is None:
        return None
    return ApprovalRequest(
        request_id=approval_slice.request_id,
        slide_in_active=True,
        reason="Main LLM 결과 승인 요청",
        requested_at_ms=int(time.time() * 1000),
        trace_id=trace_id,
    )
```

### §5.3 상태 전이 — `UI_S5_AWAIT_APPROVAL` 전이 트리거

- 본 함수 결과가 `ApprovalRequest` non-null 이면 `ui_state_mapping.md` §4.4 `APPROVAL_REQUESTED` 이벤트
  발행 → `UI_S4_RUNNING` → `UI_S5_AWAIT_APPROVAL` 전이 (R-611-5 이벤트 기반 전이).

### §5.4 SSE 트리거

- 대상 이벤트: `hud.approval.update` (T2-4 realtime_update §3.1).
- payload: `ApprovalRequest` 전체 (`status="REQUESTED"` 시).
- status 후속 전환 (`GRANTED` / `REJECTED`) 시 `slide_in_active=false` + `hud.approval.update` 재발행.

### §5.5 중앙 과점유 금지 규약 (LOCK-HM-10 verbatim)

> **AUTHORITY_CHAIN L140**: "Approval: 승인 필요 시 우측 슬라이드 인 (중앙 화면 과점유 금지)".
>
> 본 문서 변환 결과 ApprovalCard 는 **Right Panel 내부 슬라이드 인** 만 허용. Modal overlay 금지
> (rendering_rules §4.5 애니메이션 스펙 소비). 본 규약 위반 시 `[VIOLATION: LOCK-HM-10 Approval]`.

---

## §6. Alert 분배 변환 (`alerts[]` → UncertaintyAlertList)

### §6.1 원천 → 타겟 매트릭스

| 원천 (`UiStatePayload.alerts[]`) | 타겟 (`GlassHUDData.uncertainty_alert`) | UI 컴포넌트 | Store |
|----------------------------------|----------------------------------------|-------------|-------|
| `alerts[].kind` | `items[].kind` | Uncertainty Alert Toast (3종 색상 구분) | `notificationStore` |
| `alerts[].message` | `items[].message` | Toast body 문자열 | `notificationStore` |

### §6.2 변환 함수

```python
def distribute_alerts(alerts: list[AlertItem]) -> UncertaintyAlertList:
    """AlertItem[] → UncertaintyAlertList 변환. kind 3종 verbatim 검증."""
    allowed_kinds = {"LOW_QOD", "CONFLICTING_SOURCES", "STALE_DATA"}
    items: list[UncertaintyAlertItem] = []
    for a in alerts:
        if a.kind not in allowed_kinds:
            # LOCK-HM-10 위반 — 드롭 + ERROR 로그
            logError("hologram.orchestration.alert_kind_invalid",
                     {"received": a.kind, "allowed": list(allowed_kinds)})
            continue
        items.append(UncertaintyAlertItem(
            kind=a.kind,
            message=a.message,
            raised_at_ms=int(time.time() * 1000),
        ))
    return UncertaintyAlertList(items=items)
```

### §6.3 SSE 트리거

- `hud.alert.raise` (신규 추가) / `hud.alert.dismiss` (자동/수동 해제).
- 신규 추가 시 payload = 새 item(1건). dismiss 시 payload = `{kind, id}` 조합.

### §6.4 Alert 3종 자동 dismiss 조건

| kind | 자동 dismiss 조건 |
|------|------------------|
| `LOW_QOD` | 다음 `UI_S6_PRESENTING` 에서 `qod_score >= 0.8` 확인 **AND** 활성 cost 초과 없음 (`cost.ratio_to_budget < 0.95`) — cost 기원 LOW_QOD 는 예산 초과 해소 전까지 dismiss 금지 |
| `CONFLICTING_SOURCES` | 다음 evidence 재집계에서 소스 일치 확인 |
| `STALE_DATA` | fresh 데이터 수신 시 즉시 |

---

## §7. Log 분배 변환 (`log` → Timeline + LogDetail 이중 기록)

### §7.1 원천 → 타겟 매트릭스

| 원천 (`UiStatePayload.log`) | 타겟 | UI 컴포넌트 | Store |
|-----------------------------|------|-------------|-------|
| `log.trace_id` | Timeline row 키 + LogDetail 필터 | LOG-DASH-02 TraceTimeline (Left) + BV-DEBUG-01 TraceLogPanel (Bottom) | `timelineStore` + `logStore` |
| `log.stage` | Timeline 단계명 | TraceTimeline 단계 텍스트 | `timelineStore` |
| `log.event_count` | LogDetail 카운터 | TraceLogPanel 이벤트 수 | `logStore` |

### §7.2 변환 함수

```python
def distribute_log(log_slice: LogSlice, ts_ms: int) -> tuple[TimelineRecord, LogRecord]:
    """LogSlice → Timeline + LogDetail 이중 기록."""
    timeline = TimelineRecord(
        trace_id=log_slice.trace_id,
        stage=log_slice.stage,
        ts_ms=ts_ms,
    )
    log_rec = LogRecord(
        trace_id=log_slice.trace_id,
        stage=log_slice.stage,
        event_count=log_slice.event_count,
        ts_ms=ts_ms,
    )
    return timeline, log_rec
```

### §7.3 로컬 타입 정의 (6-11 DEFINED-HERE, Timeline/LogDetail 전용)

```python
class TimelineRecord(BaseModel):
    """LOG-DASH-02 TraceTimeline 1 row — Left Panel."""
    model_config = ConfigDict(extra="forbid")
    trace_id: TraceId
    stage: str
    ts_ms: int = Field(..., ge=0)

class LogRecord(BaseModel):
    """BV-DEBUG-01 TraceLogPanel 1 row — Bottom / Modal."""
    model_config = ConfigDict(extra="forbid")
    trace_id: TraceId
    stage: str
    event_count: int = Field(..., ge=0)
    ts_ms: int = Field(..., ge=0)
```

```typescript
export interface TimelineRecord {
  trace_id: TraceId;
  stage: string;
  ts_ms: number;
}

export interface LogRecord {
  trace_id: TraceId;
  stage: string;
  event_count: number;
  ts_ms: number;
}
```

### §7.4 쓰기 순서 — Timeline 먼저, LogDetail 이어서

1. `timelineStore.append(TimelineRecord)` — Left Panel 즉시 리렌더 (사용자 시각 피드백 최우선).
2. `logStore.append(LogRecord)` — Bottom Panel 또는 Modal, 지연 허용 (RAF 다음 프레임 가능).

### §7.5 6-12 Event-Logging 중복 방지

`oc.i10.ui.state.emitted` 자체는 6-12 Event-Logging 이 별도로 저장(LOCK-HM-05 §7.65 INFO). 본 문서
§7 Timeline/LogDetail 은 **UI 표시용 미러링** — 중복 저장 아님, 6-12 의 파생 뷰. 원본 보존 근거는 6-12
정본.

---

## §8. store 쓰기 순서 규약 + RAF 단일 프레임 flush 정합

### §8.1 `HudMeta.store_write_order` verbatim 준수 (T2-4 overlay_schema §3 L298-L300)

> **정본**: `["evidenceStore", "costStore", "approvalStore", "notificationStore"]` verbatim 순서.

```python
def write_all_stores(hud_data: GlassHUDData, timeline: TimelineRecord, log_rec: LogRecord) -> None:
    """
    store_write_order verbatim 준수.
    timelineStore / logStore 는 HUD 4-store 이후 별도 순서 (§7.4).
    """
    # 1. evidenceStore (HudMeta.store_write_order[0])
    evidenceStore.set(hud_data.evidence)
    # 2. costStore
    costStore.set(hud_data.cost)
    # 3. approvalStore
    if hud_data.approval is not None:
        approvalStore.set(hud_data.approval)
    # 4. notificationStore (alerts)
    notificationStore.setAlerts(hud_data.uncertainty_alert)
    # 5. timelineStore (UI 즉시 피드백)
    timelineStore.append(timeline)
    # 6. logStore (RAF 다음 프레임 허용)
    logStore.append(log_rec)
    # 7. HudMeta (마지막)
    hudMetaStore.set(hud_data.meta)
```

> **위반 시**: `[VIOLATION: HudMeta.store_write_order]` 마커 + ERROR 로그 + 상태 롤백.

### §8.2 RAF 16ms 창 단일 프레임 flush 정합

`ui_state_mapping.md` §5.4 `scheduleUnifiedFlush()` 호출 경로 공유 — HUD·토큰·ArtifactZone 3축이 동일
RAF 창에 수렴:

```typescript
// 본 문서 관점: I-10 distribute_* 모두 완료 후 단일 RAF 창에서 flush
import { scheduleUnifiedFlush } from "../orchestration/scheduleUnifiedFlush";

async function onOrchestrationEvent(payload: UiStatePayload): Promise<void> {
  // §3~§7 변환 실행
  const { glassHud, timeline, log } = distributeUiState(payload);

  // store 쓰기 (§8.1 순서)
  writeAllStores(glassHud, timeline, log);

  // 단일 프레임 flush 예약 (ui_state_mapping §5.4)
  scheduleUnifiedFlush("hud");
  // 토큰·ArtifactZone 이 동일 프레임 안에 trigger 되면 rafId 공유 → merge
}
```

**불변식 (I-8.2-A)**: 동일 `trace_id` 의 `oc.i10.ui.state.emitted` 1회 → HUD·Timeline·LogDetail 6개
store 쓰기 + 1회 RAF flush. 프레임 누락 0 (TS-CEL-07 시나리오 검증 대상).

### §8.3 scheduleHudFlush / scheduleTokenFlush 독립성

T2-4 realtime_update §4.6 `scheduleHudFlush()` 와 T2-5 token_rendering §7.1 `scheduleTokenFlush()` 는
각 파일 **유일 정본** — 본 문서는 `scheduleUnifiedFlush()`(ui_state_mapping §5.4 신규) 를 통해 단일
프레임 정합 보장. 두 scheduler 내부 단일화는 Phase 3 이월 포인트.

---

## §9. S7B-027 멀티 대화 병렬 V2 확장 포인트 (LOCK-HM-05 §7.65 STEP7)

### §9.1 확장 개요

D2.0-02 §7.65 STEP7 AI기술보강 **S7B-027 "멀티 대화 병렬"** (R4, V2):
"여러 대화 동시 실행+결과 비교. 세션 멀티플렉싱으로 동일 사용자가 복수 대화를 병렬 실행. I-10에서 각
세션의 상태를 UI에 병렬 표시. 결과 비교 뷰 제공(A/B 테스트 용도). 리소스 관리: 동시 세션 수 상한(I-8
Cost Gate 연동)."

### §9.2 V2 확장 포인트 주석 (본 문서 내 구현은 Phase 3 이월)

```python
# [S7B-027 V2 확장 포인트 — Phase 3 실 구현]
# parent_session_id 별 HUD/Timeline 병렬 집계:
# - UiStatePayload.parent_session_id != null 인 경우 별도 세션 트리 구성
# - evidenceStore/costStore/approvalStore/notificationStore 내부 Map<session_id, snapshot>
# - UI 비교 뷰: 2~N개 세션의 HUD 를 수직 분할하여 동시 표기
# - I-8 Cost Gate: 동시 세션 수 상한 = 3 (V2 초기값), 초과 시 UiStatePayload alerts 에 CONFLICTING_SOURCES 대신
#   별도 Literal 신설(향후 LOCK 검토 필요)
# 본 Phase 2 범위: parent_session_id 필드만 정의, 실제 병렬 집계 미구현. V1 에서는 항상 null.
```

### §9.3 V1 가드 (본 Phase 2 구현)

```python
def guard_v1_single_session(payload: UiStatePayload) -> None:
    """V1: parent_session_id 항상 null 확인. 위반 시 WARN 로그 (실패 아님, Phase 3 진입 알림)."""
    if payload.parent_session_id is not None:
        logWarn("hologram.orchestration.v2_feature_attempted",
                {"feature": "S7B-027", "parent_session_id": payload.parent_session_id})
```

### §9.4 S7B-015 TTS(V2) / S7B-017 실시간 화면공유(V3) 확장

- **S7B-015 TTS** (R5, V2): `UiStatePayload.audio_output_ready: bool` 예비 필드만 본 Phase 2 정의.
  실 구현 Phase 3. 본 문서 범위 외.
- **S7B-017 실시간 화면공유** (R6, V3): 본 Phase 2 범위 외. `ui_state_mapping.md` §10 TS-UI-12 시나리오
  레퍼런스만.

---

## §10. 로깅 포맷 (R-01-7 구조화 JSON)

### §10.1 이벤트 네임스페이스

| 이벤트 | 트리거 | 레벨 | 필수 필드 |
|-------|-------|------|-----------|
| `hologram.orchestration.distributed` | `distribute_ui_state()` 완료 | INFO | `trace_id`, `i10{}`, `binding{}` |
| `hologram.orchestration.write_order_violation` | `write_all_stores` 순서 위반 | ERROR | `trace_id`, `i10{}`, `error{}`, `recovery{}` |
| `hologram.orchestration.alert_kind_invalid` | Alert kind LOCK-HM-10 3종 외 | ERROR | `trace_id`, `received`, `allowed` |
| `hologram.orchestration.v2_feature_attempted` | V2 확장 포인트 트리거 (V1 에서) | WARN | `trace_id`, `feature` |
| `hologram.orchestration.frame_flushed` | RAF 단일 flush 완료 | DEBUG (1/60 샘플링) | `trace_id`, `axes[]` |

### §10.2 구조화 로그 스키마 — 성공 경로

```json
{
  "ts": "2026-04-19T12:34:56.789Z",
  "level": "INFO",
  "event": "hologram.orchestration.distributed",
  "trace_id": "01HV8M3J7K9P2Q4R6S8T",
  "session_id": "sess_01HV9W",
  "i10": {
    "interface": "emit_ui_state",
    "schema_version": "v1.0"
  },
  "binding": {
    "evidence_store": "bound",
    "cost_store": "bound",
    "approval_store": "bound",
    "notification_store": "bound",
    "timeline_store": "bound",
    "log_store": "bound",
    "hud_meta_store": "bound",
    "write_order_verified": true
  }
}
```

### §10.3 구조화 로그 스키마 — 쓰기 순서 위반

```json
{
  "ts": "2026-04-19T12:34:56.789Z",
  "level": "ERROR",
  "event": "hologram.orchestration.write_order_violation",
  "trace_id": "01HV8M3J7K9P2Q4R6S8T",
  "i10": {
    "interface": "emit_ui_state",
    "schema_version": "v1.0"
  },
  "error": {
    "expected_order": ["evidenceStore", "costStore", "approvalStore", "notificationStore"],
    "actual_order": ["costStore", "evidenceStore", "approvalStore", "notificationStore"],
    "failure_code": "OC_I10_UI_EMIT_FAIL"
  },
  "recovery": {
    "action": "rollback_stores",
    "next_retry_ms": 100,
    "user_facing": false
  }
}
```

### §10.4 샘플링 규칙

- INFO / ERROR = 100%.
- `frame_flushed` DEBUG = 1/60 샘플링 (ui_state_mapping §8.4 와 동일 규약).

---

## §11. Phase 3 테스트 시나리오 (12건, ≥10 요건 초과)

| ID | 시나리오 | 입력 | 기대 결과 | 참조 |
|----|---------|------|-----------|------|
| **TS-CEL-01** | `UiStatePayload` → `GlassHUDData` 5 축 전수 변환 | payload(5 축 전수 값) | `GlassHUDData` 5 필드 모두 non-null + 타입 검증 PASS | §3~§6 |
| **TS-CEL-02** | `store_write_order` verbatim 준수 | payload 분배 → `write_all_stores` | 쓰기 순서 `evidenceStore → costStore → approvalStore → notificationStore` 확인 (ORDER_LOG) | §8.1 |
| **TS-CEL-03** | `ratio_to_budget >= 0.8` Cost-Alert 트리거 | `cost.ratio_to_budget=0.85` | `hud.cost.update` 즉시 발송 + `CostSnapshot.displayed=true` | §4.2, §4.4 |
| **TS-CEL-04** | `ratio_to_budget >= 1.0` 초과 Alert 발송 | `cost.ratio_to_budget=1.05` | `UncertaintyAlertList` 에 `LOW_QOD` kind + `Cost exceeded` prefix 메시지 | §4.3 |
| **TS-CEL-05** | qod_score → VerificationBadge 매핑 (3등급) | 0.95/0.65/0.30 | VERIFIED/PARTIAL/UNVERIFIED 3등급 변환 | §3.4 |
| **TS-CEL-06** | T2-3 qod_hint 경유 Evidence 힌트 | `UI_S3_READY` + `qod_hint_initial=0.75` | `EvidenceHudSnapshot.qod_hint_initial=0.75` + hint_mode | §3.3 |
| **TS-CEL-07** | RAF 단일 프레임 flush 정합 | HUD + 토큰 + ArtifactZone 3축 동시 trigger | `requestAnimationFrame` 1회 호출, 3축 flush (프레임 누락 0) | §8.2 |
| **TS-CEL-08** | `approval.status="REQUESTED"` 슬라이드 인 | payload `approval.status=REQUESTED` | `ApprovalRequest.slide_in_active=true` + `hud.approval.update` SSE | §5.2, §5.4 |
| **TS-CEL-09** | Alert kind LOCK-HM-10 3종 외 값 드롭 | `alerts=[{"kind":"UNKNOWN", ...}]` | 드롭 + ERROR 로그 `hologram.orchestration.alert_kind_invalid` | §6.2 |
| **TS-CEL-10** | Log 이중 기록 (Timeline + LogDetail) | payload `log.stage="present"` | `timelineStore` + `logStore` 모두 append (2 rows) | §7 |
| **TS-CEL-11** | S7B-027 V2 parent_session_id 가드 | payload `parent_session_id="parent_sess_01"` (V1) | WARN `hologram.orchestration.v2_feature_attempted` | §9.3 |
| **TS-CEL-12** | `store_write_order` 위반 시 롤백 | mock 으로 순서 위반 주입 | `OC_I10_UI_EMIT_FAIL` + rollback 완료 + user_facing=false | §8.1, §10.3 |

---

## §12. 산출물 요약

- **정의 대상**: I-10 `UiStatePayload` 5축 분배 변환 규칙.
- **핵심 정의**:
  - §2 진입점 함수 `distribute_ui_state()` + ui_state_mapping §3 `UiStatePayload` import (재정의 금지).
  - §3 Evidence + qod_hint 경유 + T2-4 §3.4 qod_score → VerificationBadge 매핑 import.
  - §4 Cost + Cost-Alert 판정 (LOCK-HM-10 "임계치 근접 시만" verbatim) + alert item (3종 kind 준수).
  - §5 Approval 슬라이드 인 + LOCK-HM-10 "중앙 과점유 금지" verbatim.
  - §6 Alert 3종 verbatim + 자동 dismiss 규칙.
  - §7 Log Timeline + LogDetail 이중 기록 + 6-12 중복 방지.
  - §8 `store_write_order` verbatim 준수 + RAF 단일 프레임 flush 정합 (ui_state_mapping §5.4 `scheduleUnifiedFlush()` 공유).
  - §9 S7B-027 V2 확장 포인트 주석 + V1 가드 + S7B-015/017 레퍼런스.
  - §10 R-01-7 구조화 JSON (`i10{}` / `binding{}` / `error{}` / `recovery{}`).
  - §11 Phase 3 시나리오 12건.
- **V2↔V2 cross-ref**: 15건 PASS (ui_state_mapping 2 + T2-1 2 + T2-4 overlay 3 + T2-4 realtime 2 + T2-4 rendering 1 + T2-5 stream 2 + T2-5 token 1 + T2-2 1 + T2-3 1).
- **CONFLICT_CANDIDATE**: 0건 신규 (9-State 네이밍 drift 는 ui_state_mapping §11.1 에 등재됨, 본 문서 중복 등재 금지).
- **LOCK 준수**: LOCK-HM-05 (§7.63 5축 verbatim + §7.65 STEP7 3종) + LOCK-HM-10 (Cost "임계치 근접 시만" / Approval "중앙 과점유 금지" / Alert 3종 verbatim) + `HudMeta.store_write_order` verbatim.
- **ISS 해소**: ISS-07 (I-10 분배 변환 규칙 축 해소 — 매핑 테이블은 ui_state_mapping §4 과 공동 해소).
- **파일 위치**:
  - sandbox: `D:\VAMOS\docs\test_iso_p2\sot 2\6-11_Hologram-Main-LLM\07_orchestration-layer\cost_evidence_log.md`
  - production: `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\07_orchestration-layer\cost_evidence_log.md` (production-promoted 2026-06-03 Phase 4)

---

**[END OF cost_evidence_log.md — V2-Phase 2 v1.0]**
