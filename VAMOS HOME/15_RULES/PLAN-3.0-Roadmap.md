---
tags: [type/rule, tier/T0, version/V0, version/V1, version/V2, version/V3]
aliases: [PLAN 3.0, 계획 정본, 로드맵 정본]
created: 2026-06-11
source: "D:\\VAMOS\\docs\\sot\\PLAN-3.0_VAMOS_PLAN_3_0_최종완성본.md (7,049줄, 헤더/목차 실측 2026-06-11)"
---

# PLAN-3.0 Roadmap — 로드맵/비용/버전 정본

> 문서 위계 2순위 (RULE 1.3 바로 아래). [[BASE-1.3-Rules]]를 절대 기준으로 시스템의 목적·범위·우선순위·정책·구조를 100% 확정하는 최상위 계획 문서. "설계·구현하지 않으며, 무엇을 만들 것인가만 확정".

## 문서 구조 (목차 실측)

- §0 서문(목적·BASE 연동·계획 단계 역할) → §1 시스템 목적·범위 → §2 전체 아키텍처 개요
- **§3 버전 구조 (V0~V3)** — 버전 로드맵 정본 (L1323~)
- §10 결정·조건 모듈(Decision Logic) → §11 운영 한계(Limits) → §12 버전/변경 관리
- §14 E-모듈 (기능 목적 / Hologram 연동 / E-모듈↔도메인 매트릭스) → §15 Self-evo (역할·연동·동작 패턴·PLAN 2.0 정합성)
- §17 14개 목표 매핑(A/B/C/D) → §19 계획 단계 최종 완료 선언(FINAL) → §20~§22 아이디어 확장 로드맵(PART 3+5/6/7)
- **STEP7 AI기술보강 R1~R6** — R1 V1+CRITICAL(5건) / R2 V1+HIGH(25건) / R3 V1+MED·LOW(~15건) / R4 V2+CRIT·HIGH(~20건) / R5 V2+MED·LOW(~20건) / R6 V3 엔터프라이즈(~20건)

## DEC 결정 사항

- PLAN-3.0 본문 실측 등장: **DEC-002**(LangChain import 금지·Allowlist) / **DEC-005**(Embedding: BGE-M3 1024dim) / **DEC-004**(GraphRAG 하이브리드 RAG)
- DEC-001~017 전체 레지스트리 정본은 D2.0 계열 — 전수 목록: [[LOCK-DECISION-REGISTRY]] (예: DEC-003 도구 승인 Allowlist, DEC-010 QoD 스케일, DEC-014 QoD 가중치, DEC-017 MCP Streamable HTTP)

## 버전 로드맵 (LOCK)

| 버전 | 성격 | 기간 | 비용 상한 (LOCK) |
|------|------|------|------------------|
| V0 | 구조 기반 | 1~2주 | V1 동일 적용 |
| V1 | MVP | 8~12주 | ₩40,000/월 ($30) |
| V2 | Pro | — | ₩93,000/월 ($70) |
| V3 | Enterprise | — | ₩266,000/월 ($200) |

## 연결

- [[BASE-1.3-Rules]] (상위) · [[Part2-Master-Reference]] (구현 전개) · [[VAMOS-Version-Strategy]] · [[Cost-Limits]] · [[VAMOS-Authority-Chain]]
