---
tags: [type/concept, tier/T6, version/V1, lock/ABSOLUTE]
aliases: [BGE-M3, 임베딩 파이프라인, DEC-005]
created: 2026-06-12
---

# BGE-M3 Embedding Pipeline (1024dim · DEC-005)

## 정의
VAMOS 임베딩 정본(DEC-005): **V1 = BGE-M3(로컬, 1024dim)**, 클라우드 보조 = text-embedding-3-small. RAG 6단계 중 Embed→Store 단계를 담당하며 Hybrid Search의 Dense 축을 공급한다.

## 이 개념이 등장하는 모든 도메인
- [[T6-Memory-RAG]] — 6-4 정본(벡터 저장·Hybrid Search·재임베딩)
- [[T1-Auxiliary-Modules]] — I-2 Context Builder, I-16 Knowledge Search가 소비
- [[T4-MLOps]] — 모델 운영·임베딩 모델 교체 관리
- [[RAG-Pipeline]] — 6-stage 중 Embed/Store 단계

## 값·수치 (LOCK)
- DEC-005: V1=BGE-M3(로컬, **1024dim**) / 클라우드=text-embedding-3-small / V3=+text-embedding-3-large
- config LOCK: `embedding.model = bge-m3`, `embedding.dimension = 1024`
- 입력 청크: 300~500 tokens (RAG Pipeline LOCK)
- Vector DB: V1=Chroma 로컬(`vector_db.backend=chroma` LOCK V1) → V2+=Qdrant
- V2 전환 시 재임베딩: 4-Phase + needs_reembedding 플래그 (V2-005)
- Hybrid Search: BM25 0.3 + Vector(Dense) 0.7, Top-K 20, Rerank Top 5, threshold 0.75

## 버전별 차이
- V1: BGE-M3+Chroma 로컬 / V2: Qdrant 서버 재임베딩 + small 병행 / V3: Qdrant Cloud + large

## 원본 참조
- `D:\VAMOS\CLAUDE.md` §7.4/§11/§20 / `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` / `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\`
