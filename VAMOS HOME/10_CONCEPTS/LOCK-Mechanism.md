---
tags: [type/concept, tier/all, lock/ABSOLUTE, lock/FREEZE, lock/DEFINED-HERE]
aliases: [LOCK, 락 메커니즘, FREEZE]
created: 2026-06-11
---

# LOCK Mechanism

## 정의
VAMOS 설계 결정의 변경 불가 보호 체계. 469+개 LOCK 항목이 28개 네임스페이스(LOCK-AT, LOCK-BN, LOCK-MR 등)와 DEC-001~017 아키텍처 결정으로 관리되며, 3단계 강도(ABSOLUTE > FREEZE > DEFINED-HERE)로 분류된다. 문서 위계 `RULE 1.3 > PLAN 3.0 > DESIGN LOCK > DESIGN 본문 > 스키마`가 ABSOLUTE.

## 이 개념이 등장하는 모든 도메인
- [[T0-Governance]] — LOCK 레지스트리·문서 위계 정본 소유
- [[T6-Memory-RAG]] — LOCK-MR(Hybrid Search 등) 네임스페이스
- [[T3-Agent-Protocol]] — Autonomy L0~L4 정본 LOCK
- [[T3-Business-Model]] — LOCK-BM(3-9 전용 — 5-1은 LOCK-BE 사용)
- [[T5-Benchmark]] — LOCK-BE-01~15
- 전수 인덱스: [[LOCK-DECISION-REGISTRY]]

## 값·수치 (LOCK)
- 7개 절대 불변 구역: safety_rules / cost_ceiling / approval_flow / non_goals / audit_format / data_retention / user_consent
- 변경관리: 삭제 금지(DEPRECATE만), 없는 내용 창작 금지, Major 변경은 07 Approval Gate 필수
- 대표 LOCK: DEC-002(LangChain 본체 import 금지, Allowlist 한정), DEC-017(MCP=Streamable HTTP), LangGraph(프레임워크), config.toml(포맷)
- config.v1.toml LOCK 값 20개 (CLAUDE.md §20)

## 버전별 차이
- V1~V3 공통 — LOCK 자체는 버전 무관 불변, 일부 LOCK은 버전 한정(예: vector_db.backend=chroma는 V1 LOCK)

## 원본 참조
- `D:\VAMOS\CLAUDE.md` §3·§7·§20 / `D:\VAMOS\docs\sot\D2.0-01_01. VAMOS_DESIGN_2_0_OVERVIEW.md`
- `D:\VAMOS\docs\sot 2\0-0_Governance-Rules-Meta\`
