---
tags: [tier/T6, module/B-series, status/CORE, version/V1, type/domain, lock/FREEZE]
aliases: [6-4, 메모리 RAG 저장소, Memory-RAG-Storage]
tier: T6
domain: "6-4 Memory-RAG-Storage"
sot_source: "D:\\VAMOS\\docs\\sot 2\\6-4_Memory-RAG-Storage\\"
design_doc: "[[D2.0-06-Storage-Memory]]"
quality_gate: "APPROVED — Phase 7 FINAL PASS · Content A (S10-5)"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V1: V1-P2 Chroma | V2: Qdrant | V3: Enterprise(tenant_id)"
created: 2026-06-12
---

# 6-4 Memory-RAG-Storage

## 한줄 요약
4계층 메모리(L0~L3), 6-Stage RAG 파이프라인, 벡터 DB·임베딩·Semantic Cache 저장 인프라의 정본을 소유하는 Tier 6 도메인.

## 핵심 정의
- 4계층 메모리: L0(Session) / L1(Project) / L2(Long-term) / L3(Procedural), B↔L 매핑: B-1→L1, B-2→L3, B-3→L2, B-4→L0
- 6-Stage RAG: Collect→Chunk→Embed→Store→Retrieve→Generate
- BGE-M3 1024dim 원본 + Matryoshka 256dim 검색용, Hybrid Search α=0.7(Dense)/0.3(Sparse), threshold 0.75
- Vector DB: V1=Chroma(로컬), V2=Qdrant(서버) / Semantic Cache cosine ≥ 0.95

## LOCK 항목 (LOCK-MR-001~019, 19건)
- MR-001 4계층 메모리 / MR-002 B↔L 매핑 / MR-003 L0 TTL(session_end 또는 30일) / MR-004 L1 TTL 90일
- MR-005 L2 무기한 / MR-006 L3 무기한(deprecated 폐기) / MR-007 6-Stage RAG / MR-008 Hybrid α=0.7
- MR-009 Similarity 0.75 / MR-010 Semantic Cache cosine≥0.95 / MR-011 BGE-M3 1024dim+256dim
- MR-012 V1 Chroma / MR-013 V2 Qdrant / MR-014 VectorStore 어댑터 4메서드 / MR-015 Deny 벡터 삽입 금지
- MR-016 L3 활성=D7 ApprovalGate 필수 / MR-017 project_id 격리(V3 tenant_id 확장) / MR-018 저장 전 사용자 확인 / MR-019 루프 저장 폭주 방지

## 의존성 (Depends On)
- [[T5-File-Context]] — 청킹/검색 전략·알고리즘 설계 (전략=5-2, 인프라=6-4) / [[T6-Cloud-Library]] — L10 OUTPUT → VectorStore 인덱싱
- [[T1-Auxiliary-Modules]] — I-14 요약기 모듈 (양방향 B24) / [[T3-PKM]] — Zettelkasten 지식 구조 (양방향 B25)

## 제공 (Provides To)
- [[T1-Verifier-Engines]] — L2 지식 검색·RAG 파이프라인 / [[T1-Auxiliary-Modules]] — I-14 메모리 프로모션, I-2 RAG
- [[T3-PKM]] — L2 저장/검색·KG 노드 / [[T3-A2A-Protocol]] — 세션 메모리(L0) / [[T6-UI-UX]] — Memory API·저장 확인 UI
- [[T6-Security]] — PII 마스킹·저장 정책 / [[T6-Agent-Teams]] — Agent 메모리 공유 / [[T6-SDAR]] — 메모리 상태 모니터링 (양방향 B18)
- [[T6-Hologram]] — RAG 검색 결과 컨텍스트 주입 / [[T6-Event-Logging]] — 메모리 감사 로그

## 횡단 개념 연결
- [[Memory-Layers]] — L0~L3 정본 / [[RAG-Pipeline]] — 6단계 정본 / [[BGE-M3-Embedding-Pipeline]] — 임베딩 정본
- [[B-Series-Memory-Assets]] — B↔L 매핑

## 관련 모듈 시리즈
- [[MODULE-MAP]] — B-Series (메모리 자산) 저장 계층 호스트

## STEP7 매핑
- 출처: STEP7-D (메모리/저장소 작업가이드 82건 체크리스트)

## 버전별 범위
- V1: V1-P2 Chroma+BGE-M3 / V2: Qdrant 전환 / V3: Enterprise (tenant_id 3계층, GDPR Erasure, Dream Mode)

## 검증 상태
- Quality Gate: APPROVED — Phase 7 FINAL PASS · Content A / Phase 4 SPEC Stage B COMPLETE (2026-05-27)
- LOCK 검증: 19/19 일치 (AUTHORITY_CHAIN §2 실측, V3 확장 주석만 append, 정본 변경 0)

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\
- Authority: 6-4_Memory-RAG-Storage\AUTHORITY_CHAIN.md
- Design: [[D2.0-06-Storage-Memory]], [[D2.1-Schema-Index]] (A1/D6 스키마)
