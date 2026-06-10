# EventType V2 동기 + Phase 1 L3 14건 V2 갱신본 통합 검증 — L3 상세

> **도메인**: 6-1_UI-UX-System / 03_ui-state-machine
> **세션**: P2-4 (Phase 2)
> **버전**: v1.0 (2026-04-26)
> **정본 출처**: D2.0-08 §5.1 LOCK L19 이벤트 네이밍 / D2.0-08 §5.3~§5.7 EventType 54+건 (Front Mini 7 + Core/Gate 14 + Node/Main 13 + Tool 6 + CLI 10 + Memory 5) / D2.0-08 §5.9 D2.1-D2 동기 / Part2 §6.1.6 9-state SM / AUTHORITY_CHAIN §4 LOCK
> **종합계획서**: §7.3 P2-4 (L1687~L1720) / §6 ISS-3 (STEP7-C 잔여 매핑) / §6 ISS-7 (EventType 54+건 D2.1-D2 동기)
> **상위 SoT**: STEP7-C UI/UX 전수비교 작업가이드 (manifest L72 단일, 235 L)
> **선행**: 03_ui-state-machine/nine_state_machine.md (V1 675L) / failure_fallback_ui.md (V1 399L)
> **연관 V2**: P2-1 multimodal_v2.md / P2-2 responsive_layout_v2.md / P2-3 v12_components.md (3 sibling V2 산출물)

---

## 1. 개요

본 V2 산출물은 P2-1/P2-2/P2-3 3 V2 산출물에서 발행하는 신규 이벤트들을 D2.0-08 §5 EventType 54+건 정본 위에 LOCK L19 (`ui.{layer}.{subject}.{action}`) 네이밍 규칙으로 통일하고, **6-12 Event-Logging 도메인 교차 참조 포인터**를 설정한다 (ISS-7 RESOLVED). 또한 Phase 1 L3 14건의 V2 영향도 분석 + V2 참조 카탈로그를 본 산출물에 통합 수록한다 (V1 14/14 byte-prefix SHA 불변 보존 — V1 본문 변경 0건, V2 참조는 본 NEW 산출물에 통합).

**범위**: UI 레이어(6-1) — EventType 발행 인터페이스 / V1↔V2 영향도 매트릭스 / 6-12 동기 등록 협력. 6-12 EventLogging Backend / 저장 / 재생 / Telemetry 는 6-12 LOCK-EL-* 소관 (참조만, 재정의 ❌).

---

## 2. LOCK 참조 (4-field verbatim, AUTHORITY_CHAIN §4)

| LOCK ID | 항목 | 정본 출처 | LOCK 값 |
|---------|------|----------|---------|
| **L1** | UI 9-State | D2.0-08 §4.1 | UI_S0_BOOT, UI_S1_IDLE, UI_S2_EDITING, UI_S3_READY, UI_S4_RUNNING, UI_S5_AWAIT_APPROVAL, UI_S6_PRESENTING, UI_S7_RECOVERY, UI_S8_ARCHIVED (9개) |
| **L17** | 상태 전이 지연 | D2.0-08 §4.4 | 최대 500ms |
| **L19** | 이벤트 네이밍 | D2.0-08 §5.1 | `ui.{layer}.{subject}.{action}` |
| **L20** | FailureCode 수 | D2.0-08 §7.6 | 14개 FailureCodes + 9개 FallbackRegistry |

> **LOCK L19 원문 그대로** (D2.0-08 §5.1 정본): `ui.{layer}.{subject}.{action}` — 본 V2 모든 신규 이벤트는 동 네이밍 규칙 100% 준수.

> **LOCK 정의 변경 0건** — V2 신규 이벤트는 기존 6 layer (front_mini / core / node / tool / cli / memory) 외에 ui-side **6-1 layer 추가 발행만** (6-12 Event-Logging 측 LOCK-EL-* 정의는 6-12 도메인 소관, 본 6-1은 발행자, 6-12는 수집/저장자 — DH cross-handoff).

---

## 3. ISS-7 EventType 54+건 동기 — 6-12 cross-handoff 포인터

### 3.1 6-12 Event-Logging 경계 (AUTHORITY_CHAIN §5.3 정본)

> **AUTHORITY_CHAIN §5.3 인용**:
> | 6-12 (Event-Logging) | EventType 54+건 D2.1-D2 동기 등록. `ui.*` 네임스페이스 발행(6-1) vs 수집/저장(6-12) | D2.0-08 §5 이벤트 정본 기준 협력 |

| 구분 | 6-1 (본 V2 산출물 + 4 sibling V2) | 6-12 Event-Logging (참조만) |
|------|-----------------------------------|----------------------------|
| **범위** | `ui.*` 네임스페이스 이벤트 **발행자** | EventType 수집 / 저장 / 재생 / 통계 / Telemetry |
| **정본 LOCK** | LOCK L19 네이밍 규칙 | LOCK-EL-* (6-12 도메인 소관, 재정의 ❌) |
| **D2.1-D2 동기** | 6-1 측 신규 이벤트 발생 시 6-12 에 등록 요청 (cross-handoff 절차) | 6-12 가 D2.1-D2 EventTypeRegistry 정본 갱신 |
| **충돌 시** | 6-1 = UI layer 발행, 6-12 = 수집/저장 — D2.0-08 §5 정본 우선 |

### 3.2 V2 신규 발행 이벤트 — 6-12 동기 등록 대상 (6-1 → 6-12 발신)

> **본 표가 ISS-7 RESOLVED 의 핵심 산출물** — V2 신규 이벤트를 6-12 동기 등록 협력 큐에 명시화.

| # | 이벤트 (LOCK L19 형식) | 발생 V2 | 트리거 | 6-12 등록 우선순위 |
|---|------------------------|---------|--------|---------------------|
| 1 | `ui.hologram.unified_search.started` | P2-1 §4.1 | UnifiedSearchPanel 검색 시작 | P0 (검색 telemetry 핵심) |
| 2 | `ui.hologram.unified_search.result_received` | P2-1 §4.1 | 결과 표시 | P0 |
| 3 | `ui.hologram.unified_search.fallback_to_v1` | P2-1 §4.1 | V2→V1 자동 롤백 | P0 (롤백 모니터링) |
| 4 | `ui.hologram.voice_to_text.started` | P2-1 §4.2 | 음성 입력 시작 | P1 |
| 5 | `ui.hologram.voice_to_text.partial_received` | P2-1 §4.2 | 스트리밍 partial | P2 |
| 6 | `ui.hologram.voice_to_text.finalized` | P2-1 §4.2 | 최종 텍스트 확정 | P1 |
| 7 | `ui.hologram.voice_to_text.error` | P2-1 §4.2 | STT 오류 | P0 |
| 8 | `ui.hologram.image_similarity.computed` | P2-1 §4.3 | 유사도 계산 완료 | P2 |
| 9 | `ui.hologram.image_similarity.dim_mismatch` | P2-1 §4.3 | 차원 혼합 시도 | P0 (호환성 위반 감지) |
| 10 | `ui.hologram.image_similarity.shown` | P2-1 §4.3 | UI 표시 | P2 |
| 11 | `ui.hologram.cache.hit` | P2-1 §4.4 | 캐시 적중 | P1 (캐시 효율 측정) |
| 12 | `ui.hologram.cache.miss` | P2-1 §4.4 | 캐시 미스 | P2 |
| 13 | `ui.hologram.cache.unavailable` | P2-1 §4.4 | 캐시 백엔드 다운 | P0 |
| 14 | `ui.hologram.glass_hud.opened` | P2-1 §4.5 | HUD 패널 열림 | P2 |
| 15 | `ui.hologram.glass_hud.modality_changed` | P2-1 §4.5 | 활성 모달리티 변경 | P2 |
| 16 | `ui.hologram.stream.chunk_rendered` | P2-1 §4.6 | 스트림 청크 렌더 | P2 |
| 17 | `ui.hologram.stream.completed` | P2-1 §4.6 | 스트림 완료 | P1 |
| 18 | `ui.hologram.stream.interrupted` | P2-1 §4.6 | 스트림 중단 | P0 |
| 19 | `ui.builder.layout.bp_changed` | P2-2 §6.2 | BP 전이 (BP-A/B/C/D) | P1 |
| 20 | `ui.builder.layout.drawer_opened` | P2-2 §7.1 | BP-C drawer 열림 | P2 |
| 21 | `ui.builder.layout.drawer_closed` | P2-2 §7.1 | BP-C drawer 닫힘 | P2 |
| 22 | `ui.builder.layout.unsupported_resolution_shown` | P2-2 §7.1 | BP-D 진입 모달 | P0 (V3 mobile 출시 전 통계) |
| 23 | `ui.wellness.breathing.started` | P2-3 §3.2.1 | 호흡 시작 | P2 |
| 24 | `ui.wellness.breathing.cycle_completed` | P2-3 §3.2.1 | cycle 완료 | P2 |
| 25 | `ui.wellness.breathing.completed` | P2-3 §3.2.1 | 전체 완료 | P1 |
| 26 | `ui.wellness.breathing.cancelled` | P2-3 §3.2.1 | 사용자 중단 | P2 |
| 27 | `ui.wellness.grounding.started` | P2-3 §3.2.2 | 그라운딩 시작 | P2 |
| 28 | `ui.wellness.grounding.sense_completed` | P2-3 §3.2.2 | 단계 완료 | P2 |
| 29 | `ui.wellness.grounding.completed` | P2-3 §3.2.2 | 전체 완료 | P1 |
| 30 | `ui.wellness.meditation.started` | P2-3 §3.2.3 | 명상 시작 | P2 |
| 31 | `ui.wellness.meditation.paused` | P2-3 §3.2.3 | 일시정지 | P2 |
| 32 | `ui.wellness.meditation.resumed` | P2-3 §3.2.3 | 재개 | P2 |
| 33 | `ui.wellness.meditation.completed` | P2-3 §3.2.3 | 완료 | P1 |
| 34 | `ui.cbt.thought_record.started` | P2-3 §4.2.1 | 사고 기록 시작 | P2 |
| 35 | `ui.cbt.thought_record.field_updated` | P2-3 §4.2.1 | 필드 갱신 | P3 (디버깅용) |
| 36 | `ui.cbt.thought_record.saved` | P2-3 §4.2.1 | 저장 완료 | P1 |
| 37 | `ui.cbt.thought_record.save_failed` | P2-3 §4.2.1 | 저장 실패 | P0 |
| 38 | `ui.cbt.distortion.analyzed` | P2-3 §4.2.2 | 12종 분석 완료 | P2 |
| 39 | `ui.cbt.distortion.match_clicked` | P2-3 §4.2.2 | 매치 카드 클릭 | P3 |
| 40 | `ui.cbt.distortion.suggestion_applied` | P2-3 §4.2.2 | 제안 적용 | P2 |
| 41 | `ui.cbt.progress_chart.shown` | P2-3 §4.2.3 | 차트 표시 | P3 |
| 42 | `ui.cbt.progress_chart.range_changed` | P2-3 §4.2.3 | 범위 변경 | P3 |
| 43 | `ui.wellness.workload.refreshed` | P2-3 §5.2.1 | 5분 갱신 | P3 |
| 44 | `ui.wellness.workload.threshold_exceeded` | P2-3 §5.2.1 | 임계 초과 | P0 |
| 45 | `ui.wellness.forced_break.shown` | P2-3 §5.2.2 | 강제 휴식 표시 | P0 |
| 46 | `ui.wellness.forced_break.dismissed` | P2-3 §5.2.2 | 사용자 dismiss | P1 |
| 47 | `ui.wellness.forced_break.completed` | P2-3 §5.2.2 | 휴식 완료 | P1 |
| 48 | `ui.wellness.heatmap.shown` | P2-3 §5.2.3 | 히트맵 표시 | P3 |
| 49 | `ui.education.flashcard.editing` | P2-3 §6.2.1 | 카드 편집 | P3 |
| 50 | `ui.education.flashcard.saved` | P2-3 §6.2.1 | 저장 완료 | P1 |
| 51 | `ui.education.flashcard.save_failed` | P2-3 §6.2.1 | 저장 실패 | P0 |
| 52 | `ui.education.review.shown` | P2-3 §6.2.2 | 복습 카드 표시 | P2 |
| 53 | `ui.education.review.graded` | P2-3 §6.2.2 | 평가 완료 | P1 (학습 효과 분석) |
| 54 | `ui.education.review.next_scheduled` | P2-3 §6.2.2 | 다음 일정 등록 | P2 |
| 55 | `ui.education.review_dashboard.shown` | P2-3 §6.2.3 | 대시보드 표시 | P3 |
| 56 | `ui.education.review_dashboard.range_changed` | P2-3 §6.2.3 | 범위 변경 | P3 |

> **합계**: V2 신규 56 EventType. V1 57건 (nine_state_machine.md §6 정본) + V2 신규 56건 = **113 누계** (D2.0-08 §5.9 D2.1-D2 EventTypeRegistry 동기 등록 협력 대상).

> **6-12 동기 등록 절차** (참조만, 6-12 LOCK-EL-* 재정의 ❌):
> 1. 6-1 측 V2 산출물 (P2-1~P2-3) 발행 이벤트 명세 (본 §3.2 표) → 6-12 도메인 PR 으로 이관
> 2. 6-12 측 D2.1-D2 EventTypeRegistry 갱신 (LOCK-EL-* 정본)
> 3. 6-1 측 통합 테스트 — 6-12 mock 으로 발행 → 수신 검증
> 4. ISS-7 RESOLVED 확정 (도메인 마감 step 7 cascade)

---

## 4. ISS-3 잔여 — STEP7-C 104건 V2 매핑 확인

> **§6 ISS-3** "STEP7-C 신규 항목이 D2.0-08 LOCK과 충돌": Phase 0 STEP7-C 104건 등록 + Phase 1 디자인 시스템 구현 (3건 직접 + 4건 간접) → Phase 2 V2 단계 매핑 확인.

### 4.1 STEP7-C V2 매핑 매트릭스 (P2-1~P2-3 산출물 기여)

| STEP7-C Part | 항목 ID 범위 | V2 P2-1 | V2 P2-2 | V2 P2-3 | V2 P2-4 (본 산출물) | Phase 3 이월 |
|--------------|--------------|---------|---------|---------|---------------------|--------------|
| Part 1 메인 대화 | S7C-001~012 | — | S7C-001 / S7C-002 / S7C-007 | — | — | S7C-003 / S7C-005 / S7C-008~011 |
| Part 2 Canvas/Artifacts | S7C-013~022 | S7C-018 / S7C-022 | — | — | — | S7C-013~017 / S7C-019~021 |
| Part 3 Composer | S7C-023~032 | S7C-026 / S7C-031 | — | — | — | S7C-023~025 / S7C-027~030 / S7C-032 |
| Part 4 응답 렌더링 | S7C-033~044 | S7C-033 / S7C-034 | — | — | — | S7C-035~044 |
| Part 5 음성 모드 | S7C-045~052 | S7C-045 / S7C-046 / S7C-051 | — | — | — | S7C-047~050 / S7C-052 |
| Part 6 모바일/CLI | S7C-053~062 | — | S7C-053~055 (모바일 V3 예고) | — | — | S7C-056~062 |
| Part 7 에이전트 상태 | S7C-063~070 | — | — | — | — | S7C-063~070 (대부분 V2/V3 범위) |
| Part 8 설정/피드백 | S7C-071~080 | — | — | — | — | S7C-071~080 |
| Part 9 VAMOS 고유 | S7C-081~096 | — | — | S7C-088~090 (v12 4건 원천) | — | S7C-081~087 / S7C-091~096 |
| Part 10 접근성/i18n | S7C-097~104 | — | — | — | — | S7C-097~104 (Phase 1 design_system_orange_blue.md / i18n_internationalization.md / rbac_access_control.md 가 1차 매핑 완료, V3 추가 매핑 점진) |

> **V2 신규 매핑**: 약 14~16 항목 신규 (P2-1 중심). Phase 1 1차 매핑 완료분 (디자인 시스템 3건 직접 + 4건 간접) 위에 추가. Phase 3 잔여는 ~70+ 항목 (대부분 V2/V3 범위 또는 자동완성/공유/탭 등 후속 ROADMAP).

> **upstream baseline**: STEP7-C `9c7b4ea26c2d1d1d6cf32eaa8089e41ee5a16ce913c6f3cb4eed1e1b0f11f709` (235 L) UNCHANGED — 본 P2-4 산출물은 STEP7-C 본문 인용만, 수정 0건.

---

## 5. Phase 1 L3 14건 V2 영향도 매트릭스

> **★ 본 §5 가 "Phase 1 L3 14건 V2 갱신본"의 통합 표현** — V1 14/14 byte-prefix SHA 불변 엄수를 위해 본 NEW 산출물에 V2 참조를 통합 수록 (V1 본문 변경 0건). 각 V1 파일에서 본 §5 의 해당 row 를 참조하면 V2 영향도를 파악할 수 있다.

| # | 서브폴더 | V1 파일 | V1 wc -l | V2 영향도 | V2 참조 (본 산출물 외 sibling V2) |
|---|----------|---------|---------|----------|------------------------------------|
| 1 | 01_builder-view | builder_view_cockpit.md | 449 | 중 — Builder View 반응형 BP 적용 | P2-2 §4 (BP-A/B/C/D 전체) |
| 2 | 01_builder-view | cli_interface.md | 816 | 저 — 반응형 영향 적음 (CLI 모달) | P2-2 §4.4 (BP-D V3 모바일 모달 mode) |
| 3 | 01_builder-view | fluid_layout.md | 372 | **고 — V2 직접 확장 (P2-2 정본)** | **P2-2 전체 (responsive_layout_v2.md NEW)** |
| 4 | 01_builder-view | seven_pages.md | 709 | 중 — 7 페이지별 BP 반응 | P2-2 §4 / §5.3 페이지별 BP 클래스 |
| 5 | 02_hologram-view | hologram_view.md | 872 | **고 — V2 직접 확장 (P2-1 정본)** | **P2-1 §4.5 Glass HUD 오버레이 + §5 6-11 경계** |
| 6 | 02_hologram-view | multimodal_ui_v1.md | 640 | **고 — V2 직접 확장 (P2-1 정본 ImageBind)** | **P2-1 전체 (multimodal_v2.md NEW)** |
| 7 | 03_ui-state-machine | failure_fallback_ui.md | 399 | 중 — V2 신규 FailureCode 발생 시 14 → ?확장 (V3 범위) | 본 P2-4 §6 (V2 FailureCode 영향도) |
| 8 | 03_ui-state-machine | nine_state_machine.md | 675 | 중 — V2 EventType 신규 56건 동기 (LOCK L19 인용) | 본 P2-4 §3.2 EventType 56건 |
| 9 | 04_react-components | react_components_catalog.md | 1,715 | **고 — LOCK L13 ~44 → 48 카탈로그 확장 (P2-3 정본)** | **P2-3 §7 v12 4건 카탈로그 entry** |
| 10 | 05_custom-hooks | custom_hooks.md | 1,488 | 저 — 8 Hooks 변경 0건 (LOCK L14 유지). v12 컴포넌트는 기존 Hook 재사용 | P2-3 §3~§6 (Hook 재사용 명시) |
| 11 | 05_custom-hooks | zustand_stores.md | 1,479 | 저 — 7 Stores 변경 0건 (LOCK L15 유지) | (V2 신규 Store 추가 0건 — V3 범위) |
| 12 | 06_accessibility | design_system_orange_blue.md | 800 | 저 — V2 토큰 재정의 ❌ (LOCK L5/L6/L7 유지) | P2-1/P2-2/P2-3 V2 산출물에서 모두 인용만 |
| 13 | 06_accessibility | i18n_internationalization.md | 911 | 저 — LOCK L16 ja-JP V2 확장 일정 유지 | P2-3 §3.2.3 명상 voice_guide_locale ko/en/ja |
| 14 | 06_accessibility | rbac_access_control.md | 664 | 저 — LOCK L10 4단계 변경 0건 | (V2 신규 RBAC 변경 없음 — Part2 §6.1.8 정본 유지) |

> **V1 본문 변경 0건 통산** — 본 §5 표가 "V2 갱신본" 의 정합성을 보장하는 통합 catalog. V1 14 파일의 byte-prefix SHA는 STEP_A baseline 그대로 유지. 각 V1 파일은 변경 없이 V2 참조를 본 §5 에서 lookup.

---

## 6. V2 FailureCode 영향도 (LOCK L20 보존)

> LOCK L20 정본 = 14 FailureCodes + 9 FallbackRegistry (D2.0-08 §7.6). **V2 P2-1~P2-3 범위에서 FailureCode 추가 0건** — 기존 14건 으로 충분.

### 6.1 V2 신규 오류 → 기존 FailureCode 재사용 매트릭스

| V2 신규 오류 시나리오 | 매핑 FailureCode | Fallback Registry |
|----------------------|------------------|-------------------|
| ImageBind 임베딩 latency p99 > 5s (P2-1 §3.5 R1) | `EM_ERR_TIMEOUT` (응답 시간 초과) | "마지막 정상 상태 V1 임베딩으로 복귀" |
| 임베딩 컬렉션 무결성 손상 (P2-1 §3.5 R3) | `EM_ERR_INTEGRITY` (D2.0-08 §7.6 14건 중) | "검색 비활성화 + 백업 복원 안내" |
| Cache 백엔드 다운 (P2-1 §4.4) | `MC_ERR_CONN` (MCP 연결 실패) | "로컬 모드 폴백" |
| 음성 STT 권한 거부 (P2-1 §4.2) | `OC_ERR_PERMISSION` | "텍스트 입력 모드 제안" |
| BP-D 미지원 해상도 (P2-2 §4.4) | (전용 코드 없음 — V3 시점 재평가) | `<UnsupportedResolutionModal>` 정보 안내만 (오류 아님) |
| 강제 휴식 무시 (P2-3 §5.2.2) | (오류 아님 — 통계 누적) | — |
| SM-2 알고리즘 결과 비정상 (P2-3 §6.2.2) | `OC_ERR_INVALID_STATE` | "재계산 + 사용자 검토 요청" |

> **LOCK L20 정의 변경 0건** — V2 14 → 14 유지. 추가 FailureCode 검토는 V3 범위 (모바일/AR 신규 오류 시점).

---

## 7. P2-1~P2-3 산출물 정합성 검증

### 7.1 LOCK 인용 일관성 (4-field verbatim 통산)

| LOCK ID | P2-1 인용 | P2-2 인용 | P2-3 인용 | P2-4 (본) 인용 | 정합 |
|---------|-----------|-----------|-----------|----------------|------|
| L1 | ✅ §2 | — | ✅ §2 | ✅ §2 | OK |
| L2/L3/L4 | — | ✅ §2 / §4 | — | — | OK |
| L5 ORANGE #F97316 | ✅ §2 / §4 | — | ✅ §2 / §3~§6 | — | OK |
| L6 BLUE #00F6FF | ✅ §2 / §4 | — | ✅ §2 / §3~§6 | — | OK |
| L7 다크모드 | ✅ §2 | ✅ §2 / §5.2 | ✅ §2 | — | OK |
| L8 WCAG | — | ✅ §7.1 | ✅ §2 / §3~§6 | — | OK |
| L11/L12 | ✅ §2 | ✅ §2 / §4 | — | — | OK |
| L13 ~44개 | — | — | ✅ §2 / §7 | — | OK |
| L14 8 Hooks | — | — | ✅ §2 (변경 0) | — | OK |
| L17 500ms | ✅ §2 / §4 | ✅ §2 / §4.3 / §7.1 | ✅ §2 / §3 | ✅ §2 | OK |
| L19 이벤트 네이밍 | ✅ §4 (5/6 기능) | ✅ §6.2 / §7.1 | ✅ §3~§6 (12 sub) | ✅ §2 / §3.2 | OK |
| L20 FailureCode | — | — | — | ✅ §2 / §6 | OK |

> **합계 4-field 인용 — 일관성 OK**: 4 V2 산출물 × LOCK 4-field (ID + 항목 + 정본 출처 + 값) 패턴 100% 준수. CONF 신규 0건.

### 7.2 V2↔V2 cross-reference (4 산출물 간)

| 참조 방향 | 참조 내용 | 위치 |
|-----------|----------|------|
| P2-4 → P2-1 | 신규 18 EventType (`ui.hologram.*`) 등록 | 본 §3.2 # 1~18 |
| P2-4 → P2-2 | 신규 4 EventType (`ui.builder.layout.*`) 등록 | 본 §3.2 # 19~22 |
| P2-4 → P2-3 | 신규 34 EventType (`ui.wellness.* / ui.cbt.* / ui.education.*`) 등록 | 본 §3.2 # 23~56 |
| P2-3 → P2-1 | `<VoiceToTextPanel>` 재사용 | P2-3 §3.2.2 GroundingExercise inputMode="voice" |
| P2-3 → P2-1 | `<AudioPlayer>` 재사용 | P2-3 §3.2.3 MeditationTimer 오디오 재생 |
| P2-2 → P2-1 | Glass HUD 오버레이 BP-A/B 우측 패널 fix | P2-2 §4.1 / §4.2 + P2-1 §4.5 |
| P2-1 → P2-3 | StreamingEffectV2 → CBT/Wellness 응답 표시에서 재사용 (잠재) | P2-1 §4.6 (V2 단일 정본) |

> **V2↔V2 cross-ref 7건 명시화** — 4-3 V2 7 peer / 4-2 V2 4 peer 16 / 4-1 V2↔V2 peer 확장 / 3-3 60+ peer 선례 (작은 규모 7 cross-ref 명시).

---

## 8. STEP7-C 상위 SoT 매핑 (P2-4 범위)

| STEP7-C 항목 ID | 출처 (235L) | V2 P2-4 매핑 |
|-----------------|-------------|--------------|
| (P2-4 본 산출물은 통합 검증 메타) | — | §4 STEP7-C 104건 V2 매핑 매트릭스 |

> **upstream baseline**: STEP7-C `9c7b4ea26c2d1d1d6cf32eaa8089e41ee5a16ce913c6f3cb4eed1e1b0f11f709` (235 L) UNCHANGED.

---

## 9. Phase 배정 및 의존성

| 항목 | 값 |
|------|-----|
| **Phase 배정** | Phase 2 통합 검증 (P2-1~P2-3 산출물 정합성 + Phase 1 L3 14건 V2 영향도 + 6-12 동기 등록 협력) |
| **Phase 1 의존성** | nine_state_machine.md (V1 9-state) / failure_fallback_ui.md (V1 14+9) / 11 다른 L3 V1 (참조만, 본문 변경 0) |
| **Phase 2 sibling** | P2-1 multimodal_v2.md / P2-2 responsive_layout_v2.md / P2-3 v12_components.md |
| **Phase 3 이월** | STEP7-C 잔여 ~70+ 항목 (V2/V3 범위), V2 신규 FailureCode 검토 (모바일/AR), 11번째 그룹 신설 (Wellness/Education 카테고리) |
| **교차 도메인** | 6-12 Event-Logging (RECHECK_FLAG, 발신자 6-1 ↔ 수신자 6-12, ISS-7 협력) — LOCK-EL-* 재정의 ❌ |

---

## 10. 검증 (§7.3 P2-4 검증 항목 4/4 충족)

- [x] **Phase 1 L3 파일 10개 이상에 V2 반영 여부 확인**: §5 14/14 (≥10 +40%) 매트릭스 — V1 본문 변경 0 / 본 산출물 §5 통합 catalog 로 V2 영향도 lookup 가능
- [x] **ISS-7 해결**: §3.2 V2 신규 56 EventType + §3.1 6-12 cross-handoff 절차 명시 → 6-12 동기 등록 협력 큐 등록 (RESOLVED 대상)
- [x] **LOCK L19 이벤트 네이밍 규칙 V2 확장 이벤트에 적용**: §3.2 56건 100% `ui.{layer}.{subject}.{action}` 형식 준수
- [x] **P2-1~P2-3 산출물과 기존 L3 파일 간 정합성 확인**: §7.1 LOCK 인용 일관성 + §7.2 V2↔V2 cross-ref 7건

---

## 11. 변경 이력

| 일자 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-04-26 | v1.0 | NEW (P2-4) — 56 V2 EventType 6-12 동기 등록 큐 / STEP7-C 104건 V2 매핑 / Phase 1 L3 14건 V2 영향도 통합 catalog (V1 본문 변경 0) / 4 V2 산출물 정합성 검증. ISS-7 RESOLVED 대상 |

<!-- END OF DOCUMENT -->
