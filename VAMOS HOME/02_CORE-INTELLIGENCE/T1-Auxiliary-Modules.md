---
tags: [tier/T1, module/I-series, module/S-series, status/CORE, version/V1, type/domain, lock/FREEZE]
aliases: [1-2, 보조 모듈, Auxiliary-Modules]
tier: T1
domain: "1-2 Auxiliary-Modules"
sot_source: "D:\\VAMOS\\docs\\sot 2\\1-2_Auxiliary-Modules\\"
design_doc: "[[D2.0-06-Storage-Memory]]"
quality_gate: "APPROVED — Phase 4 production 승급 + ReadOnly TRUE"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V1: P0~P1 | V2: P2 | V3: P3"
created: 2026-06-11
---

# 1-2 Auxiliary-Modules

## 한줄 요약
멀티모달 해석/렌더링, 요약(I-14), 지식 검색(I-16), Self-check(S-1) 등 ORANGE CORE 보조 모듈(I/S-Series)의 구현 정본을 관리하는 Tier 1 도메인.

## 핵심 정의
- 6개 서브영역: multimodal-interpreter / multimodal-renderer / summarizer / knowledge-search / self-check / mapping
- QoD 5-factor 공식 (PLAN-3.0 정본): Accuracy×0.30 + Relevance×0.25 + Completeness×0.20 + Safety×0.15 + Efficiency×0.10
- RAG 하이브리드 검색: alpha=0.3(BM25) + 0.7(vector), BGE-M3 1024-dim
- Memory 4-layer: L0(session)/L1(project)/L2(long-term)/L3(procedural)

## LOCK 항목 (LOCK-AX-01~15, 15건)
- AX-01 I-Series 모듈 분류 (CORE/COND/EXP+change_lock) / AX-02 의존성 단방향 (D-01 UNCONFIRMED/DEFERRED)
- AX-03 QoD 5-factor 공식 / AX-04 QoD 임계값 (<0.4 L2/L3 forbidden, ≥0.7 L2 allowed)
- AX-05 Self-check P0≥70/P1≥75/P2≥80 / AX-06 RAG alpha=0.3 / AX-07 BGE-M3 1024-dim
- AX-08 VectorStore 4 methods (upsert/search/delete/get_by_id) / AX-09 Memory 4-layer
- AX-10 Semantic cache cosine≥0.95 TTL 24h / AX-11 ResponseEnvelope 최소 스펙
- AX-12 5-stage 파이프라인 / AX-13 S0~S8 상태 머신 / AX-14 PII 마스킹 AES-256
- AX-15 메모리 검색 우선순위 L0→L1→L2→L3 (레이어당 max 5, 최종 top 5)

## 의존성 (Depends On)
- [[T0-Governance]] — R1~R11 / [[T6-Security]] — PII 마스킹·출력 삭제 정책
- [[T6-Memory-RAG]] — 메모리 API (L0~L3, 양방향) / [[T6-SDAR]] — I-25 SDAR 모듈 인터페이스 (양방향)

## 제공 (Provides To)
- [[T3-Health-EmotionAI]] — S-1 VWS score 참조 / [[T6-Memory-RAG]] — I-14 요약기 모듈 (양방향)
- [[T6-SDAR]] — BaseGate(ABC) 인터페이스 (양방향) / [[T6-EXP-Modules]] — I/S-시리즈 정본 참조

## 횡단 개념 연결
- [[Memory-Layers]] — 4-layer 정의 / [[RAG-Pipeline]] — 하이브리드 검색 비율
- [[BGE-M3-Embedding-Pipeline]] — 임베딩 모델 LOCK / [[Self-Check-Loop]] — S-1 임계값
- [[Data-Governance-Pipeline]] — QoD·PII 마스킹

## 관련 모듈 시리즈
- [[MODULE-MAP]] — I-14 Summarizer, I-16 Knowledge Search, S-1 Self-check 등 I/S-Series

## STEP7 매핑
- 출처: Part2 COMPLETE (1-10 완료, 06_mapping/part2_reference_table.md)

## 버전별 범위
- V1: P0~P1 기본 모듈 / V2: P2 (*_v2 산출물 — qod_formula_v2, search_pipeline_v2 등) / V3: P3

## 검증 상태
- Quality Gate: APPROVED (Phase 5 FINAL PASS + Phase 4 production 승급 2026-05-23, ReadOnly TRUE)
- LOCK 검증: 15/15 일치 (AX-02는 D-01 OPEN — 외부 D2.0 원문 명시 전까지 production LOCK 미적용)

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\
- Authority: 1-2_Auxiliary-Modules\AUTHORITY_CHAIN.md
- Design: [[D2.0-01-Overview]] §5.6, [[D2.0-02-Orange-Core]] §7, [[D2.0-06-Storage-Memory]]
