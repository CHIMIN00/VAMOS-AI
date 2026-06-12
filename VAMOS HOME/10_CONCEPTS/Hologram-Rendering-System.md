---
tags: [type/concept, tier/T6, version/V1, lock/FREEZE]
aliases: [Hologram View, 홀로그램 렌더링, 6-11 Main LLM 출력]
created: 2026-06-12
---

# Hologram Rendering System (6-11 Main LLM 출력)

## 정의
VAMOS 최종 출력 계층. Main/Hologram LLM이 4계층 아키텍처의 종단에서 최종 출력/시각화/보고서를 생성하고, Hologram View(사용자 대화 화면)가 이를 렌더링한다. 2-View(Builder+Hologram) 중 사용자 대면 뷰의 정본.

## 이 개념이 등장하는 모든 도메인
- [[T6-Hologram]] — 6-11 정본(LOCK-HM-01~10, Main LLM 출력·MoE)
- [[T6-UI-UX]] — 6-1 Tauri 2.0+React 18, 2-View/3-Panel 프레임워크 LOCK
- [[T6-Brain-Adapter]] — 6-9 HAL Multi-LLM 라우팅(6-9↔6-11 양방향 교차)
- [[T1-Auxiliary-Modules]] — I-10(UI 오케스트레이션, LOCK-HM-05), I-11 Output Composer, I-13 Renderer

## 값·수치 (LOCK)
- LOCK-HM-01: Hologram View 3요소 = 타임라인(Left, ~250px) + 스트리밍 캔버스(Center) + Glass HUD(Right, ~300px)
- LOCK-HM-02: 4 Layout 고정 — 3-Column Fluid / Builder / Hologram / CLI
- LOCK-HM-03: 9-State UI 상태머신 — UI_S0_BOOT ~ UI_S8_ARCHIVED (이름 변경 금지)
- LOCK-HM-04: 2-tier 라우팅 — Orange Core → Front Mini → Main LLM (V1 2~3모델, V3 MoE multi-expert pool)
- LOCK-HM-06: 3-point 출력 — user_response / evidence_summary(근거·QoD) / log_report(trace_id)
- 색상: ORANGE #F97316, BLUE NODE #00F6FF / 비용 경고 80%=#FBBF24, 100%=#EF4444 (DEC-015)

## 버전별 차이
- V1: 2~3개 모델 단순 라우팅, 44 React 컴포넌트(LOCK-HM-07) / V2: +PWA / V3: MoE multi-expert + Expert 기여도 UI

## 원본 참조
- `D:\VAMOS\CLAUDE.md` §5/§7.6/§21 / `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` / `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\AUTHORITY_CHAIN.md`
