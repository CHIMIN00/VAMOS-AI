---
tags: [tier/T3, module/I-series, module/COND, status/COND, version/V1, type/domain, lock/FREEZE]
aliases: [3-3, 개인 지식 관리, PKM-Knowledge-Management]
tier: T3
domain: "3-3 PKM-Knowledge-Management"
sot_source: "D:\\VAMOS\\docs\\sot 2\\3-3_PKM-Knowledge-Management\\"
design_doc: "[[D2.0-01-Overview]]"
quality_gate: "APPROVED — Phase 5 FINAL PASS / PHASE3_READY v2 (2026-04-23)"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V1: P1 기본+SM-2 | V2: P2 고급+Dream | V3: P3 팀+3D"
created: 2026-06-12
---

# 3-3 PKM-Knowledge-Management

## 한줄 요약
지식그래프·SM-2 간격반복·Zettelkasten 구조를 구현 정본으로 관리하는 Tier 3 개인 지식 관리(PKM) 도메인.

## 핵심 정의
- 핵심 모듈: I-16 Knowledge Search Engine / I-24 Knowledge Graph Engine + CAT-B 지식관리 모듈(#17~#24, #87~#89, #107~#108)
- SM-2 알고리즘 파라미터 정본 소유자 (#8 Education은 참조만, R-06-2 동시 LOCK AMENDMENT 의무)
- 지식그래프: 노드 5타입·엣지 8타입 — 기존 타입 보호, 확장(추가)만 가능
- Phase 2 V2 = 13 M-ID 등재(5,293L), SM-2 대칭 10/10 verbatim match

## LOCK 항목 (LOCK-PKM-01~12, 12건)
- PKM-01 MIN_EASINESS=1.3 / PKM-02 DEFAULT_EASINESS=2.5 / PKM-03 초기 간격 n=1:1일·n=2:6일·n≥3:I(n-1)×EF
- PKM-04 노드 타입 KnowledgeNote·Tag·Domain·Source·Person / PKM-05 엣지 타입 8종(RELATED_TO~MENTIONS)
- PKM-06 중복 감지 MinHash Jaccard≥0.7·벡터 유사도≥0.85 / PKM-07 태그 5차원(주제/유형/감정/중요도/프로젝트)
- PKM-08 지식 카테고리 8종(concept~bookmark) / PKM-09 신선도 지수 감쇠 freshness=exp(-λ×age_days) 공식만 LOCK
- PKM-10 Zettelkasten 5타입(permanent/literature/fleeting/index/structure) / PKM-11 VBS-14 V1 항목 75점·평균 80점
- PKM-12 지식 성숙도 Seedling→Growing→Evergreen→Archived

## 의존성 (Depends On)
- [[T0-Governance]] — R1~R11 / [[T2-Blue-Node]] — BN 런타임 (#5)
- [[T2-COND-Modules]] — COND-017/018 (#7) / [[T6-Memory-RAG]] — L2 지식 저장/검색·KG 노드 (#45, B25 양방향)

## 제공 (Provides To)
- [[T3-Workflow-RPA]] — 지식 기반 워크플로우 템플릿 (#12) / [[T3-Business-Model]] — 투자 지식 분석 데이터 (#13)
- [[T3-Education]] — SM-2 파라미터 정본 (B4) / [[T3-Multimodal]] — cross-modal 지식 캡처 (B2) / [[T6-Memory-RAG]] — Zettelkasten 구조 (B25)

## 횡단 개념 연결
- [[COND-CAT-B-Knowledge]] — CAT-B 모듈 카탈로그 / [[Memory-Layers]] — L2 지식 계층 연동
- [[RAG-Pipeline]] — 지식 검색 파이프라인 / [[BGE-M3-Embedding-Pipeline]] — 임베딩 기반 의미 검색

## 관련 모듈 시리즈
- [[MODULE-MAP]] — I-16/I-24 (I-series), CAT-B 지식관리 (COND)

## STEP7 매핑
- 출처: STEP7-M (78항목, M-001~M-054)

## 버전별 범위
- V1: P1 기본+SM-2 / V2: P2 고급+Dream (Notion/Obsidian sync, VBS-14) / V3: P3 팀+3D

## 검증 상태
- Quality Gate: APPROVED (AUTHORITY v1.3, [PHASE3_READY v2: 3-3 — 2026-04-23] 최종 확정, exit gate 3/3)
- LOCK 검증: 12/12 일치 (재정의 0, SM-2 3 LOCK 정본 소유 유지)

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\3-3_PKM-Knowledge-Management\
- Authority: 3-3_PKM-Knowledge-Management\AUTHORITY_CHAIN.md (v1.3)
- Design: [[D2.0-01-Overview]] §5.6 (I-16/I-24)
