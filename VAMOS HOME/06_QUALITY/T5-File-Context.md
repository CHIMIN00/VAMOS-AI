---
tags: [tier/T5, status/CORE, version/V1, type/domain, lock/DEFINED-HERE]
aliases: [5-2, 파일 컨텍스트, File-Context, 대용량 컨텍스트 이해]
tier: T5
domain: "5-2 File-Context"
sot_source: "D:\\VAMOS\\docs\\sot 2\\5-2_File-Context\\"
design_doc: "[[D2.0-06-Storage-Memory]]"
quality_gate: "APPROVED — Phase 4 SPEC Stage B V3 production promotion (15 산출물, 2026-05-31)"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V1: 청킹+압축 기본 | V2: Self-RAG/CRAG/RAPTOR·Late Chunking·ColBERT v3 | V3: KG Engine I-24 ON·Sparse Attention"
created: 2026-06-12
---

# 5-2 File-Context

## 한줄 요약
대용량 컨텍스트 이해(청킹·하이브리드 검색·압축·구간별 정확도)의 전략/알고리즘 정본 도메인 — Phase 9에서 36번째 도메인으로 승격.

## 핵심 정의
- 3-way Ensemble 검색: BGE-M3 0.40 + KoSimCSE 0.35 + BM25 0.25 (L2 2-way alpha=0.3의 독립 확장, S11-6 SC-10)
- 한국어 청킹 300~500 토큰/오버랩 50~100 (L7), Mecab-ko(V1)→Kiwi(V2) (L6)
- 구간별 정확도(G2): 10~50K 85~95% / 50~130K 70~85% / 130~200K 60~75%
- 압축: trigger 0.8·target 0.5·information_loss ≤0.15 정상(G3 LOCK)
- ⚠️ 폴더명 주의: 정본은 `sot 2\5-2_File-Context\`. 레거시 원본 `sot 2\FILE CONTEXT\` 폴더(1,618줄, 2026-03-18)가 별도 존재 — 정본 아님(참조용)

## LOCK 항목 (SOT 소유 18건 + DEFINED-HERE 37건)
- SOT LOCK L1~L18: Contextual Retrieval(L1)·Hybrid Search(L2)·Reranking(L3)·압축(L4)·슬라이딩 윈도우(L5)·청킹(L6/L7)·Dynamic Chunking(L8)·QoD(L9)·메모리 4계층(L10)·4-Index Fusion(L11)·Self-RAG/CRAG/RAPTOR(L12)·Late Chunking(L13)·ColBERT v3(L14)·NLI 환각 감지(L15)·Prompt Caching(L16)·Batch API(L17)·KG Engine I-24 V3:ON(L18)
- DEFINED-HERE 37건: G-series 8(Gap) + W-series 12(약점) 등 — G3/G6/G8 LOCK 부여

## 의존성 (Depends On)
- [[T1-Verifier-Engines]] — LLM 모델 윈도우·능력 → 전략 설계 기반 / [[T0-Governance]] — R-52-1

## 제공 (Provides To)
- [[T6-Memory-RAG]] — 청킹/검색 전략·알고리즘 → 인프라 구현 / [[T5-Benchmark]] — 구간별 정확도 목표 → 측정(S7G-040/041, 측정 권한은 5-1)
- [[T6-Hologram]] — 컨텍스트 최적화 전략 → UI 렌더링 소비

## 횡단 개념 연결
- [[RAG-Pipeline]] — 청킹·검색 단계 전략 정본 / [[Memory-Layers]] — L0~L3 4계층 인용 / [[BGE-M3-Embedding-Pipeline]] — 3-way Ensemble 1축

## STEP7 매핑
- 출처: STEP7-G(4-Index Fusion, S7G-040/041) + STEP7-D(Dynamic Chunking) — Part2 ABSENT/NOT COVERED

## 버전별 범위
- V1: 형태소 청킹 + 압축 + 환각 자동 검증 / V2: Self-RAG/CRAG/RAPTOR + Late Chunking + ColBERT v3 + NLI / V3: KG Engine ON + Sparse Attention (V3 15 산출물 승급)

## 검증 상태
- Quality Gate: APPROVED — STAGE 9 truly_converged_v3 + Phase 4 SPEC Stage B (2026-05-31)
- LOCK 검증: 18/18 SOT 전사 일치 + DEFINED-HERE 37 (AUTHORITY_CHAIN v1.3)

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\5-2_File-Context\
- Authority: 5-2_File-Context\AUTHORITY_CHAIN.md (v1.3)
- Design: [[D2.0-06-Storage-Memory]] + D2.0-02/-01/-05/-07 + STEP7-G/D
