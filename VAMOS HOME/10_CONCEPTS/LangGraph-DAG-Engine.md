---
tags: [type/concept, tier/all, version/V1, lock/FREEZE]
aliases: [LangGraph, StateGraph, DAG 엔진, S0~S8 상태머신]
created: 2026-06-12
---

# LangGraph DAG Engine (S0~S8)

## 정의
VAMOS Agent Workflow의 정본 프레임워크 (**LangGraph = LOCK**). StateGraph로 5-Phase 파이프라인과 S0~S8 상태머신을 DAG로 실행한다. LangChain 본체 import는 금지(DEC-002)이며 패턴만 참조한다.

## S0~S8 상태 머신 (타임아웃 포함)
```
S0_RECEIVED → S1_INTENT_PARSED(5s) → S2_EVIDENCE_READY(30s)
→ S3_DECISION_LOCKED(120s) → S4_EXECUTING(10s) → S5_OUTPUT_READY(15s)
→ S6_SELF_CHECKED → S7_MEMORY_COMMITTED → S8_DONE
```

## 이 개념이 등장하는 모든 도메인
- [[T3-Workflow-RPA]] — 워크플로우/자동화 실행 기반(3-4)
- [[T2-Blue-Node]] — 5-Phase Action/Execute 단계 실행
- [[T4-Rust-Tauri]] — Python-Rust JSON-RPC 13개 중 `langgraph.*` 메서드
- [[T6-Agent-Teams]] — 멀티에이전트 위임(Lead+Sub) 워크플로우 기반

## 값·수치 (LOCK)
- **LangGraph = Agent Workflow 프레임워크 (LOCK §7.1)** — V1~V3 동일
- DEC-002 (LOCK): LangChain import 금지 — Allowlist(V1-009): `langchain-core`/`langchain-community`/`langchain-openai` adapter만
- 네이밍 (LOCK §7.4): state=`S#_`(언더스코어) / module=`S-#`(하이픈) — 충돌 원천 분리
- [[Decision-Lock]]: S3_DECISION_LOCKED 이후 변경 불가 (locked=true) / TEE 최대 반복 P0=3, P1=5, P2=10 (LOCK)

## 버전별 차이
- V1~V3 프레임워크 동일 (LOCK) — 코드 위치: `backend/vamos_core/agent/` (LangGraph StateGraph + pipeline)

## 원본 참조
- `D:\VAMOS\CLAUDE.md` §7.1·§12 / `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` / `D:\VAMOS\docs\sot 2\3-4_Workflow-RPA\`
