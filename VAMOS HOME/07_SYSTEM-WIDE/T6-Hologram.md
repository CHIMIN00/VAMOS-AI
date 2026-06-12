---
tags: [tier/T6, module/I-series, status/CORE, version/V1, type/domain, lock/FREEZE]
aliases: [6-11, 홀로그램 메인 LLM, Hologram-Main-LLM]
tier: T6
domain: "6-11 Hologram-Main-LLM"
sot_source: "D:\\VAMOS\\docs\\sot 2\\6-11_Hologram-Main-LLM\\"
design_doc: "[[D2.0-08-UI-UX]]"
quality_gate: "APPROVED (Phase 4 RECOVERY 도메인 종료 2026-06-03, CONF-HM-008 RESOLVED)"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V1: V1-P4 | V2: Enhanced | V3: 3D/Avatar + MoE"
created: 2026-06-12
---

# 6-11 Hologram-Main-LLM

## 한줄 요약
Hologram View 렌더링 파이프라인과 Main LLM 2-tier 라우팅·3-point 출력 포맷·Glass HUD 통합의 정본을 소유하는 Tier 6 도메인.

## 핵심 정의
- Hologram View 3요소: 타임라인(Left ~250px) + 스트리밍 캔버스(Center) + Glass HUD(Right ~300px)
- Main LLM 2-tier 라우팅: Orange Core → Front Mini → Main LLM (V1 2~3 모델, V3 MoE multi-expert pool)
- 3-point 출력: user_response / evidence_summary / log_report — 워크플로우 종료 시 3필드 필수
- Glass HUD: Evidence(VERIFIED/PARTIAL/UNVERIFIED) + Cost 게이지 + Approval 카드 + Uncertainty Alert 3종

## LOCK 항목 (LOCK-HM-01~10, 10건)
- HM-01 Hologram View 3요소 구조 / HM-02 4 Layout 고정(3-Column Fluid/Builder/Hologram/CLI)
- HM-03 9-State UI State Machine (UI_S0_BOOT~UI_S8_ARCHIVED) / HM-04 Main LLM 2-tier 라우팅
- HM-05 I-10 UI 오케스트레이션 레이어 역할 / HM-06 3-point 출력 포맷
- HM-07 React 컴포넌트 44개 / HM-08 Custom Hook 8개 / HM-09 Zustand Store 7개 / HM-10 Glass HUD 오버레이

## 의존성 (Depends On)
- [[T4-Rust-Tauri]] — IPC/Tauri 인프라 / [[T6-Memory-RAG]] — RAG 검색 결과 컨텍스트 주입
- [[T5-File-Context]] — 컨텍스트 최적화 전략 / [[T6-UI-UX]] — UI 프레임워크 (양방향 B13)
- [[T6-Brain-Adapter]] — 2-tier 라우팅 (양방향 B27)

## 제공 (Provides To)
- [[T6-UI-UX]] — Hologram 렌더링/LLM 통합 (양방향 B13, 6-1=UI View 구조 / 6-11=렌더링·생성 계층)
- [[T6-Brain-Adapter]] — Main LLM 라우팅 요청 (양방향 B27)

## 횡단 개념 연결
- [[Hologram-Rendering-System]] — 렌더링 파이프라인 정본 / [[SLA-Performance-Targets]] — V3 60fps 보장(AR)

## 관련 모듈 시리즈
- [[MODULE-MAP]] — I-10 UI 오케스트레이션 (emit_ui_state, render_artifact_preview)

## STEP7 매핑
- 출처: D2.0-08 + D2.0-02 §7.63/§11.15.1 + D2.0-05 §7.2 + Part2 §6.1/V1-P4 (PARTIAL — 렌더링 내부 흐름은 SOT2 상세)

## 버전별 범위
- V1: V1-P4 (44 컴포넌트/8 Hook/7 Store) / V2: Enhanced / V3: 3D/Avatar + MoE expert pool

## 검증 상태
- Quality Gate: APPROVED — Phase 4 RECOVERY 도메인 종료 (2026-06-03, 5 V3 ALL NEW, CONF-HM-008 RESOLVED)
- LOCK 검증: 10/10 일치 (AUTHORITY_CHAIN 실측, LOCK-HM-01~10 변경 0건, 6-9↔6-11 cycle EXACT)

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\
- Authority: 6-11_Hologram-Main-LLM\AUTHORITY_CHAIN.md
- Design: [[D2.0-08-UI-UX]], [[D2.0-02-Orange-Core]] (§7.63/§11.15.1), [[D2.0-05-Agent-Workflow]] (§7.2)
