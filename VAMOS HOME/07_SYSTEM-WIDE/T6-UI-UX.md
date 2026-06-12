---
tags: [tier/T6, module/I-series, status/CORE, version/V1, type/domain, lock/FREEZE]
aliases: [6-1, UI/UX 시스템, UI-UX-System]
tier: T6
domain: "6-1 UI-UX-System"
sot_source: "D:\\VAMOS\\docs\\sot 2\\6-1_UI-UX-System\\"
design_doc: "[[D2.0-08-UI-UX]]"
quality_gate: "APPROVED (AUTHORITY v2.6, Phase 4 RECOVERY 도메인 종료 2026-06-01)"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V1: V1-P4 (Week 13-14) | V2: 리팩토링+PWA | V3: Mobile/AR"
created: 2026-06-12
---

# 6-1 UI-UX-System

## 한줄 요약
Builder View + Hologram View 2-View, 3-Column 레이아웃, UI 9-State 머신, React 컴포넌트/디자인 시스템의 정본을 소유하는 Tier 6 UI 레이어 도메인.

## 핵심 정의
- 2-View: Builder(만드는 창) + Hologram(쓰는 창), 3-Column: Left 250-300px / Center Flex / Right 350-400px
- UI 9-State: UI_S0_BOOT~UI_S8_ARCHIVED, 상태 전이 지연 최대 500ms
- React 컴포넌트 ~44개(10그룹, V3 통산 57 카탈로그 확장) + Custom Hooks 8 + Zustand Stores 7
- 테마: ORANGE #F97316 / BLUE #00F6FF, 기본 Dark(#1E1E1E), WCAG 2.1 AA

## LOCK 항목 (L1~L20, 20건)
- L1 UI 9-State / L2~L4 3-Column 폭 규격 / L5 ORANGE #F97316 / L6 BLUE #00F6FF / L7 다크모드 기본
- L8 WCAG 2.1 AA / L9 CLI 명령어 6개 고정 / L10 RBAC 4단계 / L11 최소 해상도 1280x720 / L12 Tauri 기본 1440x900
- L13 컴포넌트 ~44개 / L14 Hooks 8 / L15 Stores 7 / L16 i18n ko-KR / L17 전이 지연 500ms
- L18 P2 승인 타임아웃(고위험 5분/일반 10분→auto deny) / L19 이벤트 네이밍 `ui.{layer}.{subject}.{action}` / L20 FailureCode 14+9(V3 확장 18+12)

## 의존성 (Depends On)
- [[T4-Rust-Tauri]] — IPC 백엔드 (72 commands) / [[T6-Memory-RAG]] — Memory API, 저장 확인 UI
- [[T6-Event-Logging]] — UI 이벤트(ui.builder.*) 표준 / [[T6-Hologram]] — Hologram 렌더링/LLM (양방향 B13)

## 제공 (Provides To)
- [[T6-Hologram]] — UI 프레임워크 (양방향 B13, 6-1=AR UI View 구조 / 6-11=렌더링 로직 경계)

## 횡단 개념 연결
- [[Event-Logging-Standard]] — ui.* 네임스페이스 발행 / [[Cost-Limits]] — 비용 경고 색상(DEC-015)
- [[5-Gate-Decision-Framework]] — 승인 대기 UI_S5_AWAIT_APPROVAL

## 관련 모듈 시리즈
- [[MODULE-MAP]] — I-10 UI 오케스트레이션 레이어 (상태/근거/승인/비용을 UI 이벤트로 변환)

## STEP7 매핑
- 출처: STEP7-C (보강 항목 104건 체크리스트)

## 버전별 범위
- V1: V1-P4 Week 13-14 (데스크톱 전용) / V2: 리팩토링+PWA / V3: Mobile + AR 경계 확정(ISS-6 RESOLVED)

## 검증 상태
- Quality Gate: APPROVED (Phase 4 RECOVERY genuine write, 도메인 종료 2026-06-01)
- LOCK 검증: 20/20 일치 (L1~L20, AUTHORITY_CHAIN v2.6 실측, 재정의 0)

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\6-1_UI-UX-System\
- Authority: 6-1_UI-UX-System\AUTHORITY_CHAIN.md
- Design: [[D2.0-08-UI-UX]], [[D2.0-07-Safety-Cost]] (승인 타임아웃)
