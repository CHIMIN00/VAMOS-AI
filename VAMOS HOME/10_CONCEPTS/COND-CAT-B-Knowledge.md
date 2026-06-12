---
tags: [type/concept, module/COND, status/COND, tier/T2, version/V2]
aliases: [CAT-B, Knowledge COND, KnowledgeMixin]
created: 2026-06-12
---

# COND CAT-B: Knowledge (13개)

## 정의
COND 106개 중 지식 관리 카테고리 13개. `KnowledgeMixin`으로 Blue Node에 지식 저장/검색/그래프 능력을 제공한다. 모듈 ID 범위 **#17-#24, #87-#89, #107-#108**. 주요 의존성: ChromaDB, Neo4j, LangChain(패턴 참조 — DEC-002 Allowlist 한정).

## 등장 도메인
- [[T2-COND-Modules]] — 정본 소유 (2-2 COND 카테고리 체계)
- [[T3-PKM]] — 지식관리(SM-2, Zettelkasten) 기능 도메인 연계
- [[T6-Memory-RAG]] — VectorStore(Chroma→Qdrant)·GraphDB(NetworkX→Neo4j) 저장 계층 공유
- [[T2-Blue-Node]] — Research/Content Node가 주요 소비

## 값·수치 (LOCK 여부)
- DEC-002 (LOCK): LangChain 본체 import 금지 — Allowlist(V1-009): `langchain-core`, `langchain-community`, `langchain-openai` adapter만 허용
- 실행 모델: COND는 CORE 소비만 가능 — CORE→COND 역방향 import 금지 (R7, vamos_lint VL-003)
- COND 합산 (CLAUDE.md §6 정본): CAT-B 13 / 전체 106

## 버전별 차이
- 조건부 실행, 버전 게이트 Mixed — Vector/Graph 백엔드는 V1 Chroma·JSON → V2+ Qdrant·Neo4j 전환을 따름

## 원본 경로
- `D:\VAMOS\docs\sot 2\2-2_COND-Modules-Detail\COND_MODULES_DETAIL_구조화_종합계획서.md` (L67~76)
- `D:\VAMOS\docs\sot 2\2-2_COND-Modules-Detail\COND_MODULES_종합명세.md` / CAT-B 하위
