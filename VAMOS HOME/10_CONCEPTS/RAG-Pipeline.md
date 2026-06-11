---
tags: [type/concept, tier/all, version/V1, lock/ABSOLUTE]
aliases: [RAG 파이프라인, 6-stage RAG, Hybrid Search]
created: 2026-06-11
---

# RAG Pipeline (6-Stage + Hybrid)

## 정의
VAMOS 지식 검색의 6단계 파이프라인(LOCK): **Collect → Chunk(300~500tok) → Embed → Store → Retrieve → Generate**. 검색은 Hybrid Search(BM25+Vector)가 LOCK 정본이다.

## 이 개념이 등장하는 모든 도메인
- [[T6-Memory-RAG]] — 6-stage·Hybrid Search 정본(6-4, LOCK-MR-009)
- [[T1-Auxiliary-Modules]] — I-2 Context Builder, I-15 Evidence/QoD, I-16 Knowledge Search
- [[T1-Verifier-Engines]] — D-6 GraphRAG/Hybrid RAG(EXP, V3)
- [[T5-File-Context]] — Agentic RAG(Self-RAG/CRAG) 정본, alpha 표기 정본(LOCK-AX-06)
- [[T5-v23-Extensions]] — Self-RAG, CRAG, ColBERT v3 등 V2-P2 확장

## 값·수치 (LOCK)
- Hybrid Search(LOCK): **BM25 0.3 + Vector(Dense) 0.7, Top-K 20, Rerank Top 5, threshold 0.75**
- ⚠️ alpha 표기: 정본 alpha=BM25 가중치=0.3(LOCK-AX-06) — 6-4/PART2의 α=0.7은 Dense 관점 동일 값(용어충돌 #15)
- DEC-004 GraphRAG 정확도 목표: V1=Basic 64%+ / V2=Hybrid+Rerank 83%+ / V3=Self-RAG+Graph 90%+
- DEC-005 Embedding: V1=BGE-M3(로컬, 1024dim) / 클라우드=text-embedding-3-small
- DEC-014 QoD 가중치(RAG): relevance 0.30 + accuracy 0.25 + freshness 0.25 + completeness 0.20
- Vector DB: V1=Chroma 로컬, V2+=Qdrant / Semantic Cache cosine ≥ 0.95(LOCK)

## 버전별 차이
- V1: Basic RAG(Chroma+BM25/Vector) / V2: Hybrid+Rerank, Qdrant, Agentic RAG / V3: Self-RAG+GraphRAG(D-6 ON)

## 원본 참조
- `D:\VAMOS\CLAUDE.md` §7.4 / `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md`(S7D-012/S7D-018) / `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\`
