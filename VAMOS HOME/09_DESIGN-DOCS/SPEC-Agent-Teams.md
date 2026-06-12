---
tags: [tier/T6, module/I-series, status/CORE, version/V1, type/design, lock/FREEZE]
aliases: [Agent Teams SPEC, S7-A-001-FULL, 에이전트 팀 명세]
sot_source: "D:\\VAMOS\\docs\\sot\\VAMOS_AGENT_TEAMS_SPEC.md"
created: 2026-06-12
---

# SPEC Agent-Teams

## 역할
**Claude Agent Teams 패턴(Lead + Sub-agents 위임)을 VAMOS 3계층(ORANGE CORE→BLUE NODES→OTHER BRAINS)에 통합**하는 명세 (문서 ID S7-A-001-FULL, v1.0.0, 2026-02-23). D2.0-02 §12 TITLE_ONLY를 95~100% 상세 확장한 정본.

## 핵심 섹션
- §1 설계 철학 4원칙: 단일결정(최종 결론은 ORANGE CORE/Lead만 확정) / 위임 기반 실행(Lead는 계획만) / Gate 선행(모든 에이전트 실행은 07 Gate 선행 통과) / 격리된 컨텍스트(자유 상호 호출·무한 대화 금지)
- §1.2 매핑: Lead Agent=ORANGE CORE(I-5), Sub-Agent=BLUE NODE, Tool Use=OTHER BRAINS+MCP, Shared Context=Context Variables(trace_id), Handoff=AgentHandoff Protocol
- §2~5 아키텍처: Task Decomposer + Delegation Engine(plan→decompose→assign→monitor→merge), MessageBus/TaskBoard/EventBus, Agent 유형별 상세(Research/Coding/Quant/Content), 협업 패턴
- §7~8 Pydantic v2 스키마 + API 엔드포인트 / §9 V1/V2/V3 로드맵

## LOCK 하이라이트
- §10 LOCK 결정사항 + §11 안전/비용 제약 전용 장
- **5-Gate(G0~G4) 전 파이프라인 내장** — Claude Teams에 없는 정책/비용/승인 제어가 VAMOS 차별점
- P0/P1/P2 도메인 분류의 에이전트 수준 계층적 접근 제어
- 비용 추적 에이전트 단위 분리: Lead=Opus급, 팀원=Sonnet/Haiku급 차등 모델 허용
- LOCK 기준: RULE 1.3 BASE, PLAN-3.0, DESIGN 2.0 전 문서

## 연결
- [[T6-Agent-Teams]] — 6-3 도메인 구현
- [[D2.0-02-Orange-Core]] / [[D2.0-03-Blue-Nodes]] — Lead/Sub 정본 소스
- [[D2.0-05-Agent-Workflow]] / [[D2.0-07-Safety-Cost]] — 워크플로우·Gate 연동
- [[5-Gate-Decision-Framework]] / [[T3-Agent-Protocol]] — STEP7-K 프로토콜
- [[T4-MCP]] — MCP Servers 연동

## 원본 문서
- `D:\VAMOS\docs\sot\VAMOS_AGENT_TEAMS_SPEC.md`
