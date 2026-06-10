# 02_knowledge-graph — 지식그래프 + 조직화

> **도메인**: #6 PKM Knowledge Management
> **범위**: M-011~M-013, M-015~M-020, M-031~M-038 (17항목)
> **정본**: sot 2/3-3_PKM-Knowledge-Management/02_knowledge-graph/

---

## 파일 목록

| # | 파일명 | M-ID | 항목명 | 상태 |
|---|--------|------|--------|------|
| 1 | auto_tagging_classification.md | M-011, M-018 | 자동 태깅/분류 + 멀티계층 카테고리 | EXTEND |
| 2 | knowledge_graph_construction.md | M-012 | 지식그래프 자동 구축 (Neo4j) | EXTEND |
| 3 | folder_notebook_structure.md | M-013 | 폴더/노트북 계층 구조 | NEW |
| 4 | semantic_duplicate_detection.md | M-015 | 시맨틱 중복 감지 (MinHash + 벡터) | EXTEND |
| 5 | time_based_management.md | M-016 | 시간 기반 지식 관리 + Daily Notes | NEW |
| 6 | maturity_tracking.md | M-017 | 지식 성숙도 추적 (Seedling→Evergreen) | EXTEND |
| 7 | bookmark_favorite.md | M-019 | 북마크/즐겨찾기 시스템 | NEW |
| 8 | import_export.md | M-020 | 지식 임포트/익스포트 | EXTEND |
| 9 | ontology_construction.md | M-031 | 자동 온톨로지 구축 | EXTEND |
| 10 | graph_reasoning.md | M-032 | 그래프 추론 (경로/유사/누락) | NEW |
| 11 | graph_query_language.md | M-033 | 그래프 질의 언어 (NL→Cypher) | SKELETON (DEFER) |
| 12 | graph_visualization.md | M-034 | 그래프 시각화 인터랙션 | NEW |
| 13 | graph_vector_hybrid.md | M-035 | 지식그래프 ↔ 벡터DB 하이브리드 | NEW |
| 14 | graph_maintenance.md | M-036 | 그래프 자동 정리 (중복/고립 노드) | NEW |
| 15 | personal_wiki.md | M-037 | 개인 위키 (마크다운 기반) | NEW |
| 16 | graph_recommendation.md | M-038 | 그래프 기반 추천 | NEW |

## LOCK 참조

> LOCK (기존 명세 §4.1): **LOCK-PKM-04 지식그래프 노드 타입** — KnowledgeNote, Tag, Domain, Source, Person

> LOCK (기존 명세 §4.1): **LOCK-PKM-05 지식그래프 엣지 타입** — RELATED_TO, TAGGED_WITH, BELONGS_TO, SOURCED_FROM, CONTRADICTS, SUPERSEDES, SUPPORTS, MENTIONS

> LOCK (기존 명세 §3.3 / 가이드 R-06-1): **LOCK-PKM-06 중복 감지 임계값** — MinHash Jaccard ≥ 0.7 (근사), 벡터 유사도 ≥ 0.85 (의미적)

> LOCK (STEP7-M M-011): **LOCK-PKM-07 태그 분류 체계** — 주제/유형/감정/중요도/프로젝트 5차원

> LOCK (기존 명세 §3.2): **LOCK-PKM-08 지식 카테고리** — concept, fact, procedure, decision, reference, opinion, code_snippet, bookmark

> LOCK (STEP7-M M-017): **LOCK-PKM-12 지식 성숙도 상태** — Seedling → Growing → Evergreen → Archived

## 의존성

- ← 01_knowledge-capture/: 캡처된 지식 → 그래프 삽입
- ← T2-DATA_PIPELINE: 벡터 검색 (Chroma/Qdrant)
- → 03_spaced-repetition/: 그래프 기반 검색/추천
- → 06_zettelkasten/: 양방향 링크 → RELATED_TO 엣지
- → T4-Frontend (#4-1): D3.js/Cytoscape.js 그래프 시각화

---

## Phase 2 V2 상태 sync (2026-04-23 STAGE 7 STEP_B #2b 도메인 마감)

- V2 13/13 = 100.0% 달성 (도메인 전체)
- 본 폴더 V2 기여분:
  * `graph_reasoning.md` §V2 EXTEND (M-032, 237L, 세션 2-2)
  * `graph_visualization.md` §V2 EXTEND (M-034, 229L, 세션 2-2)
  * `graph_maintenance.md` §V2 EXTEND (M-036, 251L, 세션 2-2)
  * `graph_recommendation.md` §V2 EXTEND (M-038, 222L, 세션 2-2)
- V1 body mutation 0 (byte-prefix SHA 4/4 match=True) / LOCK-PKM-04/05/06/09/12 verbatim / FABRICATION 0
- per-file LOCK-PKM grep (R5 실측): graph_reasoning 15 + graph_visualization 28 + graph_maintenance 25 + graph_recommendation 11 = 79

## STEP_C 최종 확정 (2026-04-23)

- Phase F 6-step + Phase G 8-step 전수 PASS
- 심층 재검증 R1~R_N truly_converged_v2 (사용자 2차 재요청 "더이상 수정하지 않을때까지" 반영)
- **[PHASE3_READY v2: 3-3 — 2026-04-23] 최종 확정** 6 지점 동기화 완료
- Phase 7-II 10/21 → **11/21 ✅ 확정**
