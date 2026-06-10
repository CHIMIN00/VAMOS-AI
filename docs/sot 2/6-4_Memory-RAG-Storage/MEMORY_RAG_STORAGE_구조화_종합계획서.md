# Memory-RAG-Storage 구조화 종합 계획서

> **버전**: v1.1
> **작성일**: 2026-03-25 (v1.1 검증 반영: 2026-03-25)
> **목적**: sot 2/6-4_Memory-RAG-Storage/를 메모리 계층·RAG 파이프라인·벡터 DB·메모리 증류 구현 정본으로 구조화하고, Part2 V1-Phase 2 FULL 영역 + D2.0-06 DESIGN 정본 + STEP7-D 작업가이드와의 역할 분리·참조 체계를 확립
> **Status**: APPROVED — Phase 7 FINAL PASS (S7-5, 2026-03-25) · Content A (S10-5)
> **Tier**: 6 (System-wide Components)
> **SOT 출처**: D2.0-06 (Storage/Memory DESIGN), STEP7-D (메모리/저장소 작업가이드)
> **Part2 상태**: FULL (V1-Phase 2 L1876-2074)
> **세션**: S6-5

---

## 목차

1. [현재 상태 분석](#1-현재-상태-분석)
2. [목표 구조 (최종 형태)](#2-목표-구조-최종-형태)
3. [권한 체계 선언](#3-권한-체계-선언)
4. [거버넌스 규칙](#4-거버넌스-규칙)
5. [선행작업](#5-선행작업)
6. [이슈 해결 매핑](#6-이슈-해결-매핑)
7. [Phase 실행 계획](#7-phase-실행-계획)
8. [파일 역할 분리 명세](#8-파일-역할-분리-명세)
9. [충돌 해결 프로토콜](#9-충돌-해결-프로토콜)
10. [검증 체크리스트](#10-검증-체크리스트)
11. [보완 사항](#11-보완-사항)
12. [FINAL REVIEW 결과](#12-final-review-결과)
13. [L3 전수 승급 계획](#13-l3-전수-승급-계획)
14. [실행 약점 대응 계획](#14-실행-약점-대응-계획)
- [부록 A: 메모리 계층 상세 스키마](#부록-a-메모리-계층-상세-스키마)
- [부록 B: 소비 도메인 매트릭스](#부록-b-소비-도메인-매트릭스)
- [부록 C: LOCK 전수 추적표](#부록-c-lock-전수-추적표)

---

## 1. 현재 상태 분석

### 1.1 기존 문서 현황

| 문서 | 위치 | 줄 수 | 역할 | 상태 |
|------|------|-------|------|------|
| **D2.0-06** | docs/sot/D2.0-06_*.md | ~1,800줄 | 메모리/저장소 설계 정본 (L0~L3, B-Series, RAG 6단계, 저장 정책) | LOCK — 4계층, B↔L 매핑, 6-Stage RAG, VectorStore 어댑터 |
| **STEP7-D** | docs/sot/STEP7-D_*.md | ~500줄 | 메모리/저장소/데이터 아키텍처 심화 작업가이드 (82건) | 체크리스트 — S7D-001~082 항목 |
| **Part2 V1-P2** | docs/guides/PART2 L1876-2074 | ~198줄 | V1-Phase 2 Storage+Memory+RAG 구현 가이드 | FULL — 9 core 구현 + LOCK 값 + B↔L 매핑 + 검증 12항목 |
| **Part2 V0-STEP-5** | docs/guides/PART2 L1206-1374 | ~168줄 | 기본 저장소 + 로깅 스캐폴딩 | FULL — SQLite 초기 세팅, 로그 테이블 |

### 1.2 sot 2/6-4_Memory-RAG-Storage/ 현재 파일

| 항목 | 상태 |
|------|------|
| 종합계획서 | 본 문서 (신규 작성) |
| AUTHORITY_CHAIN.md | 신규 작성 예정 |
| CONFLICT_LOG.md | 신규 작성 예정 |
| 01_memory-hierarchy/ | 폴더 생성 완료 (내용 미작성) |
| 02_rag-pipeline/ | 폴더 생성 완료 (내용 미작성) |
| 03_vector-db/ | 폴더 생성 완료 (내용 미작성) |
| 04_memory-distillation/ | 폴더 생성 완료 (내용 미작성) |

### 1.3 핵심 문제

| # | 문제 | 심각도 | 영향 |
|---|------|--------|------|
| P1 | **STEP7-D vs D2.0-06 계층 정의 불일치**: STEP7-D는 5계층(L0~L4)을 정의하나 D2.0-06은 4계층(L0~L3)을 LOCK. STEP7-D의 L1="단기(7일 TTL)"와 D2.0-06의 L1="프로젝트(90일 TTL)"가 상이 | CRITICAL | 구현 시 계층 정의 혼란, TTL 정합성 파괴 |
| P2 | **메모리 계층 용어 비통일**: SM/LM/EM(Short/Long/Episodic Memory) vs L0~L3 혼용 가능성. DESIGN에서 L0~L3를 LOCK했으나 외부 문헌/코드에서 SM/LM 표기 잔존 위험 | HIGH | 구현 코드와 문서 간 불일치 |
| P3 | **RAG 파이프라인 6단계 상세 부재**: D2.0-06에 6단계 정의는 있으나, 각 단계의 구체적 파라미터·에러 핸들링·모니터링 메트릭 미정의 | HIGH | V1 구현 시 설계 갭 |
| P4 | **벡터 DB 마이그레이션 경로 미상세**: V1(Chroma) → V2(Qdrant) 전환 시 데이터 무결성 보장 절차·스키마 호환성 미정의 | MEDIUM | V2 전환 시 데이터 손실 위험 |
| P5 | **메모리 승격/강등 알고리즘 상세 부재**: L0→L1→L2→L3 승격 조건과 QoD 연동이 개념 수준만 정의 | MEDIUM | 자동화 불가, 수동 운영 의존 |
| P6 | **Semantic Cache와 RAG 검색 간 경계 불명확**: 캐시 히트 시 RAG 우회 조건·캐시 미스 시 RAG 폴백 플로우 미정의 | MEDIUM | 중복 검색, 비용 낭비 |

### 1.4 Part2 V1-Phase 2 FULL 영역 요약 (방식 C)

> **출처**: Part2 V1-Phase 2 (L1876-2074)
> **Part2가 정본**: When + Where (V1 Week 5-8 배정, 코드 위치, Phase 전환 게이트 12항목)
> **sot 2/가 정본**: What + How (메모리 계층 상세 동작, RAG 단계별 구현 로직, 벡터 DB 어댑터 설계)

#### Part2 핵심 내용 요약

**V1-Phase 2 Core 구현 (9항목)**:
1. **L0 Session Memory**: SQLite 기반, TTL=session_end 또는 created_at+30일 (LOCK)
2. **L1 Project Memory**: SQLite 기반, TTL=90일, project_id별 분리 (LOCK)
3. **Chroma Vector DB**: BGE-M3 1024dim 원본 + Matryoshka 256dim 검색용 (LOCK)
4. **JSON GraphRAG**: NetworkX 기반 엔티티/관계 저장 (V2에서 Neo4j 전환)
5. **Semantic Cache**: cosine ≥ 0.95 (LOCK), TTL=24시간, max_entries=1000
6. **대화 내보내기/가져오기**: JSON/Markdown export/import
7. **PII 마스킹**: 주민번호/전화번호/이메일/카드번호 regex 탐지
8. **메모리 B-3 Decay**: TTL 기반 자동 만료, activation_state 관리
9. **DCL 기초 구현**: DCL-FIN(RT-BNP RSS), DCL-TECH(RSS 1시간 폴링)

**LOCK 값 (Part2 확정)**:
- L0 TTL: session_end 또는 created_at + 30일 (D2.0-06 §2.1 L121 + Part2 L1907 LOCK — ⚠️ D2.0-06 §2.5.3 L268 약식 표기와 불일치, CONFLICT_LOG #006)
- L1 TTL: 90일 (D2.0-06 §2.1)
- Semantic Cache: cosine ≥ 0.95 (D2.1-D6)
- BGE-M3: 1024dim + Matryoshka 256dim
- 6-Stage RAG Pipeline 순서 (D2.0-06 §1.1)
- B↔L 매핑: B-1→L1, B-2→L3, B-3→L2, B-4→L0
- Hybrid Search: α=0.7(Dense), Top-K=20, threshold=0.75 (Part2 L2034/L2038 LOCK ← S7D-012/S7D-018 ← D2.0-06 L778)

> **표기 통일**: 본 도메인에서 α(alpha)는 Dense 가중치(0.7)를 의미합니다. BM25 가중치는 1-α=0.3입니다. GLOSSARY_CROSS_DOMAIN.md 참조.

**Phase 전환 게이트 (12항목)**: L0/L1 CRUD, Chroma 벡터 검색, GraphRAG, Semantic Cache, 6-Stage RAG, Hybrid Search, PII 마스킹, B-3 Decay, 내보내기/가져오기, DCL 수집, B↔L 매핑 정합성

---

## 2. 목표 구조 (최종 형태)

### 2.1 폴더 트리

```
D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\
│
├── MEMORY_RAG_STORAGE_구조화_종합계획서.md     ← 본 문서 (14+α 섹션)
├── AUTHORITY_CHAIN.md                          ← 권한 체계 선언 + LOCK 레지스트리
├── CONFLICT_LOG.md                             ← 충돌 기록부
│
├── 01_memory-hierarchy/                        ← 메모리 계층 L0~L3 + B-Series
│   ├── _index.md                               ← 계층 총괄: L0~L3 정의, B↔L 매핑, 승격/강등
│   ├── MemoryRecordSchema.md                   ← P0-1 산출물: 스키마 확정 (D6 20필드 + SourceQoD 8필드 + LOCK-MR 추적)
│   ├── l0_session_memory.md                    ← L0 세션 메모리 상세 (B-4 Working)
│   ├── l1_project_memory.md                    ← L1 프로젝트 메모리 상세 (B-1 Episodic)
│   ├── l2_longterm_knowledge.md                ← L2 장기 지식 상세 (B-3 Semantic)
│   ├── l3_procedural_memory.md                 ← L3 절차/템플릿 상세 (B-2 Procedural)
│   └── promotion_demotion.md                   ← 승격/강등 알고리즘 + QoD 연동
│
├── 02_rag-pipeline/                            ← RAG 파이프라인 6단계
│   ├── _index.md                               ← RAG 총괄: 6-Stage 정의, 파라미터, 에러 핸들링
│   ├── collect_chunk.md                        ← Stage 1-2: 수집 + 청킹 (300~500tok)
│   ├── embed_store.md                          ← Stage 3-4: 벡터화 + 저장
│   ├── retrieve_generate.md                    ← Stage 5-6: 검색(Hybrid) + 생성
│   └── graphrag.md                             ← GraphRAG: NetworkX(V1) → Neo4j(V2) 파이프라인
│
├── 03_vector-db/                               ← 벡터 DB + 임베딩
│   ├── _index.md                               ← 벡터 DB 총괄: V1 Chroma → V2 Qdrant, 어댑터 인터페이스
│   ├── chroma_collection_strategy.md           ← P0-3 산출물: 컬렉션 전략 확정 (분리/격리/파라미터)
│   ├── chroma_adapter.md                       ← ChromaAdapter V1 구현 상세
│   ├── qdrant_adapter.md                       ← QdrantAdapter V2 구현 상세
│   ├── embedding_strategy.md                   ← BGE-M3 + Matryoshka + 하이브리드 임베딩
│   └── migration_v1_v2.md                      ← V1→V2 마이그레이션 절차
│
└── 04_memory-distillation/                     ← 메모리 증류 + 캐시 + 정책
    ├── _index.md                               ← 증류 총괄: Semantic Cache, QoD, PII, 저장 정책
    ├── semantic_cache.md                        ← Semantic Cache: cosine≥0.95, TTL, 무효화
    ├── storage_policy.md                        ← Allow/Restrict/Deny 저장 정책 + 마스킹
    ├── pii_masking.md                           ← PII 자동 감지 + 마스킹 규칙
    └── qod_ttl.md                               ← QoD 스코어 + TTL 정책 + 신선도 관리
```

### 2.2 깊이 규칙

```
최대 3단계:
  6-4_Memory-RAG-Storage/ → XX_{카테고리}/ → 파일.md              (2단계) ✅
  6-4_Memory-RAG-Storage/ → XX_{카테고리}/ → {하위}/ → 파일.md    (3단계) ✅
  4단계 이상 → 절대 금지 ❌
```

### 2.3 네이밍 규칙

- **폴더명**: 영문 소문자 + 하이픈, 접두사 2자리 번호 (`01_`, `02_`, ...)
- **파일명**: 영문 소문자 + 언더스코어 (`.md` 확장자)
- **계획서 파일명**: `MEMORY_RAG_STORAGE_구조화_종합계획서.md`

### 2.4 서브폴더 역할 요약

| 서브폴더 | Part2/SOT 출처 | 핵심 관심사 | 파일 수 |
|---------|---------------|-----------|---------|
| **01_memory-hierarchy** | D2.0-06 §2, Part2 V1-P2 항목1-2 | L0~L3 계층 정의, B↔L 매핑, 승격/강등 알고리즘 | 6 |
| **02_rag-pipeline** | D2.0-06 §1.1/§4, Part2 V1-P2 항목3-4 | 6-Stage RAG, Hybrid Search, GraphRAG | 5 |
| **03_vector-db** | D2.0-06 §2.2, STEP7-D Part 2/4 | Chroma 컬렉션 전략, Chroma/Qdrant 어댑터, BGE-M3 임베딩, V1→V2 마이그레이션 | 6 |
| **04_memory-distillation** | D2.0-06 §3/§2.5, Part2 V1-P2 항목5-8 | Semantic Cache, 저장 정책, PII, QoD/TTL | 5 |

---

## 3. 권한 체계 선언

### 3.1 기존 VAMOS 권한 체인

```
RULE 1.3 > PLAN 3.0 > DESIGN 2.0 LOCK > DESIGN body > Schema/TECH_STACK
```

### 3.2 Memory-RAG-Storage 확장 권한 체인

```
RULE 1.3
  > PLAN 3.0
    > DESIGN 2.0
      ├─ D2.0-06 (Storage/Memory — L0~L3, B-Series, RAG 6단계, 저장 정책 LOCK)
      ├─ D2.0-07 (Safety/Cost/Approval — 저장 승인 게이트 LOCK)
      └─ D2.1-A1/D6 (스키마 — VectorDB, Semantic Cache 스키마)
        > Part2 V1-Phase 2 (구현 가이드: When + Where + LOCK 값)
          ├─ Part2 V0-STEP-5 (기본 저장소 스캐폴딩)
          └─ Part2 V2/V3 Phase (확장: Qdrant, Neo4j, Scale)
            > sot 2/6-4_Memory-RAG-Storage/ (구현 상세: What + How) ← 본 도메인
              > STEP7-D (메모리/저장소 작업가이드 — 82건 체크리스트)
```

### 3.3 각 문서의 권한 범위

| 문서 | 권한 레벨 | 결정할 수 있는 것 | 결정할 수 없는 것 |
|------|----------|------------------|------------------|
| **D2.0-06** | DESIGN (LOCK) | L0~L3 계층 정의, B↔L 매핑, RAG 6단계, 저장 정책, VectorStore 어댑터 인터페이스, MemoryRecordSchema | 구현 방법, Phase 배정, 코드 구조 |
| **D2.0-07** | DESIGN (LOCK) | 저장 승인 게이트(Allow/Restrict/Deny), PII 정책, 비용 상한 | 메모리 계층 정의, RAG 파라미터 |
| **Part2 V1-P2** | IMPL-GUIDE | When(Week 5-8), Where(코드 경로), LOCK 파라미터 값, Phase 전환 게이트 | 알고리즘 상세, 에러 핸들링 로직 |
| **sot 2/6-4** | IMPL-DETAIL | What(계층 상세 동작, 승격 로직) + How(RAG 구현, 어댑터 설계) | When(Phase), LOCK 값 재정의 |
| **STEP7-D** | CHECKLIST | 82건 작업 항목 점검, 기술 비교, 벤치마크 참조 | 정본 정의, LOCK 값 설정 |

### 3.4 도메인 경계 명시

| 인접 도메인 | 6-4가 소유하는 것 | 인접 도메인이 소유하는 것 | 경계 기준 |
|-----------|-----------------|----------------------|----------|
| **1-2 Auxiliary-Modules** | 메모리 계층 정의, RAG 파이프라인, 벡터 DB 어댑터 | I-14 요약기/증류기 모듈 인터페이스, I-2 Context Builder | 6-4 = 저장/검색 인프라 / 1-2 = 소비 모듈 |
| **3-3 PKM-Knowledge-Management** | L2 장기 지식 저장, 벡터 검색, KG 엔티티 저장 | Zettelkasten 구조, 외부 도구 연동(Notion/Obsidian), 지식 갈등 해결 | 6-4 = 저장소 계층 / 3-3 = 지식 관리 로직 |
| **6-2 Security-Governance** | PII 마스킹 구현, 저장 정책 적용 | PII 정책 정의, STRIDE 위협 모델, OWASP 매핑 | 6-4 = 정책 적용 / 6-2 = 정책 정의 |
| **6-1 UI-UX-System** | 메모리 저장 API, 메모리 검색 API | Memory Tab UI, 저장 확인 모달, 마스킹 Diff 뷰 | 6-4 = 백엔드 API / 6-1 = 프론트엔드 UI |
| **6-12 Event-Logging** | 메모리 감사 로그 생성(S7D-007) | 로그 저장소 정의, 로그 보존 정책 | 6-4 = 로그 발생 / 6-12 = 로그 관리 |
| **6-5 SDAR-System** | 메모리 상태 리포트 제공 | 메모리 이상 탐지, 자가 수리 트리거 | 6-4 = 상태 제공 / 6-5 = 진단/수리 |
| **5-2 File-Context-Strategy** | 메모리 계층별 검색 결과 → LLM 컨텍스트 주입 형식 제공 | 파일/컨텍스트 최적화 전략·알고리즘 (윈도우 크기, 압축률, 토큰 할당) | 6-4 = 메모리 데이터 소스 / 5-2 = 컨텍스트 구성 전략 |
| **5-3 Testing-Strategy** | 메모리 API 계약 (VectorStore 4개 메서드) | 메모리 통합 테스트 전략, 테스트 데이터 격리 정책 | 6-4 = API 인터페이스 / 5-3 = 테스트 설계 |

### 3.5 LOCK 보호 선언

> **절대 규칙**: sot 2/6-4_Memory-RAG-Storage/ 내 모든 파일은 아래 LOCK 값을 **재정의할 수 없다**.
> 참조 시 반드시 `> LOCK-MR-NNN (출처): [원문 그대로]` 형식을 사용한다.

| # | LOCK 항목 | 정본 출처 | 값 |
|---|-----------|----------|-----|
| LOCK-MR-001 | **4계층 메모리** | D2.0-06 §2 | L0(Session) L1(Project) L2(Long-term) L3(Procedural) |
| LOCK-MR-002 | **B↔L 매핑** | D2.0-06 §2 / Part2 V1-P2 | B-1→L1, B-2→L3, B-3→L2, B-4→L0 |
| LOCK-MR-003 | **L0 TTL** | D2.0-06 §2.1 (L121) + Part2 V1-P2 (L1907) | session_end 또는 created_at + 30일 중 먼저 ⚠️ D2.0-06 §2.5.3(L268)은 "즉시 만료"로 약식 표기 — CONFLICT_LOG #006 참조 |
| LOCK-MR-004 | **L1 TTL** | D2.0-06 §2.1 | 90일 (프로젝트 단위 30일 연장 가능) |
| LOCK-MR-005 | **L2 보존** | D2.0-06 §2.1 | 무기한 (Core 지식 영구 보존) |
| LOCK-MR-006 | **L3 보존** | D2.0-06 §2.1 | 무기한 (deprecated 전환으로 폐기) |
| LOCK-MR-007 | **6-Stage RAG** | D2.0-06 §1.1 | Collect→Chunk→Embed→Store→Retrieve→Generate |
| LOCK-MR-008 | **Hybrid Search α** | Part2 V1-P2 (L2034) ← S7D-012 (D2.0-06 L778: BM25_alpha=0.3 → Dense α=1-0.3=0.7) | Dense α=0.7, Sparse 1-α=0.3 |
| LOCK-MR-009 | **Similarity threshold** | Part2 V1-P2 (L1920, L2038) ← S7D-018 | 0.75 |
| LOCK-MR-010 | **Semantic Cache** | D2.1-D6 / Part2 V1-P2 | cosine ≥ 0.95 |
| LOCK-MR-011 | **BGE-M3 임베딩** | Part2 V1-P2 | 1024dim 원본 + Matryoshka 256dim 검색용 |
| LOCK-MR-012 | **V1 Vector DB** | D2.0-06 §2.2 | Chroma (로컬 임베디드) |
| LOCK-MR-013 | **V2 Vector DB** | D2.0-06 §2.2 | Qdrant (서버 모드, 우선) |
| LOCK-MR-014 | **VectorStore 어댑터** | D2.0-06 §2.2-A | upsert/search/delete/get_by_id 4개 메서드 |
| LOCK-MR-015 | **Deny 벡터 삽입 금지** | D2.0-06 §3.2 | Deny 판정 시 벡터 삽입 절대 금지 |
| LOCK-MR-016 | **L3 활성 게이트** | D2.0-06 §2.3 | L3 저장/활성은 D7 ApprovalGate 필수 |
| LOCK-MR-017 | **project_id 격리** | D2.0-06 §1 / RULE 1.3 §7.2 | 프로젝트 간 데이터 혼합 금지 |
| LOCK-MR-018 | **저장 전 사용자 확인** | RULE 1.3 §7.3 | 저장 전 사용자 확인이 기본 |
| LOCK-MR-019 | **루프 저장 폭주 방지** | D2.0-06 머리글 | 반복 루프 중 원문 저장 금지, 요약/메타/링크만 허용 |

---

## 4. 거버넌스 규칙

### 4.1 공통 규칙 (R1~R11)

> **글로벌 거버넌스 규칙**: 본 도메인은 0-0_Governance-Rules-Meta에서 정의한 R1~R11 글로벌 규칙을 전체 준수합니다.

| 규칙 | 내용 | 6-4 적용 |
|------|------|----------|
| R1 | 단일 정본 원칙 | D2.0-06이 메모리/저장소 DESIGN 정본. sot 2/6-4는 IMPL-DETAIL 정본 |
| R2 | LOCK 불변 원칙 | LOCK-MR-001~019 재정의 금지 |
| R3 | DESIGN > IMPL 우선 | D2.0-06 > Part2 > sot 2/6-4 |
| R4 | 충돌 시 기록 | CONFLICT_LOG.md에 기록 후 상위 문서 우선 적용 |
| R5 | — | (SPEC §7-8 해당 없음 — 삭제) |
| R6 | 스키마 정본 참조 | MemoryRecordSchema/SourceQoDSchema 정본 = D6(D2.1-D6) |
| R7 | STEP7 매핑 | STEP7-D 82건을 4개 서브폴더에 매핑 (§6 참조) |
| R8 | 파일 역할 분리 | Part2=When/Where, sot 2/=What/How (§8 참조) |
| R9 | Phase 게이트 | Part2 Phase 전환 게이트 12항목 준수 |
| R10 | 교차 참조 포인터 | 양방향 포인터 필수 (sot 2/ ↔ Part2 ↔ D2.0-06) |
| R11 | 변경 추적 | AUTHORITY_CHAIN에 변경 이력 기록 |

### 4.2 Tier 6 공통 규칙

| 규칙 | 내용 |
|------|------|
| **R-T6-1** | Part2 원문과 SOT2 상세가 충돌 시 Part2 원문 우선 |
| **R-T6-2** | 횡단 관심사 도메인(6-2, 6-12, 6-13)은 소비 도메인 목록 유지 필수 |
| **R-T6-3** | Part2 업데이트 시 해당 Tier 6 도메인 STALE 체크 필수 |

### 4.3 도메인 고유 규칙

| 규칙 | 내용 | 근거 |
|------|------|------|
| **R-64-1** | **메모리 계층 용어 L0~L3 통일**: SM/LM/EM 등 대체 용어 사용 금지. 반드시 L0/L1/L2/L3 또는 Session/Project/Long-term/Procedural 사용 | D2.0-06 §2 LOCK, STEP7-D 5계층과의 혼동 방지 |
| **R-64-2** | **B-Series 매핑 고정**: B-4→L0, B-1→L1, B-3→L2, B-2→L3 매핑은 코드·문서·주석 어디에서든 동일하게 참조 | D2.0-06 §2 LOCK |
| **R-64-3** | **벡터 삽입 전 정책 검사 필수**: 모든 벡터 삽입은 D7 PolicyCheck 결과(PASS/BLOCK/NEEDS_APPROVAL/ERROR)를 확인한 후에만 수행 | D2.0-06 §3.2 + D2.0-07 |
| **R-64-4** | **QoD 임계값 준수**: QoD < 0.4 → L2/L3 저장 금지, QoD ≥ 0.7 → L2 저장 허용 | D2.0-06 §2.5.2 |
| **R-64-5** | **RAG 운영 한계 준수**: 문서 15개, 청크 30개 (V1 기준) | D2.0-06 §1.1 + §4 |

---

## 5. 선행작업

| # | 선행작업 | 상태 | 산출물 |
|---|---------|------|--------|
| PRE-1 | **D2.0-06 전문 정밀 읽기**: §0~§9 전체 + STEP7 보강 항목 확인 | ✅ 완료 | 본 계획서 §1.4, §3.5 반영 |
| PRE-2 | **STEP7-D 82건 → 4개 서브폴더 매핑**: 각 S7D 항목이 어느 서브폴더에서 구현되는지 추적표 작성 | ⬜ 미착수 | 부록 C 추적표 |
| PRE-3 | **1-2(I-14 요약기/증류기) 인터페이스 확인**: 메모리 승격 시 요약 생성에 I-14를 호출하는 계약 확인 | ⬜ 미착수 | 01_memory-hierarchy/promotion_demotion.md |
| PRE-4 | **3-3(PKM) 경계 합의**: L2 지식과 PKM Zettelkasten 간 데이터 흐름·소유권 경계 명확화 | ⬜ 미착수 | §3.4 경계 갱신 |

---

## 6. 이슈 해결 매핑

### 6.1 STEP7-D 계층 불일치 해결

| STEP7-D 정의 | D2.0-06 정본 (LOCK) | 해결 |
|-------------|-------------------|------|
| L0: 즉시 메모리 (인메모리) | L0: Session Memory (세션 단기) | **일치** — L0=Session 통일 |
| L1: 단기 메모리 (7일 TTL) | L1: Project Memory (90일 TTL) | **충돌** → D2.0-06 우선. STEP7-D L1은 L0 확장(세션 후 임시 보관) 개념으로 재해석. CONFLICT_LOG #001 |
| L2: 프로젝트 메모리 (90일) | — | **STEP7-D L2 = D2.0-06 L1 (Project)**. 매핑 조정. CONFLICT_LOG #002 |
| L3: 장기 메모리 (영구) | L2: Long-term Knowledge (무기한) | **STEP7-D L3 = D2.0-06 L2 (Long-term)**. CONFLICT_LOG #003 |
| L4: 아카이브 (압축) | L3: Procedural Memory (무기한) | **STEP7-D L4 ≠ D2.0-06 L3**. L4 Archive는 V2+ 확장으로만 참조. CONFLICT_LOG #004 |

### 6.2 SHELL→FULL 승격 항목

| # | 항목 | 현재 상태 | 해결 방안 | 대상 서브폴더 |
|---|------|----------|----------|-------------|
| I-1 | L0~L3 계층별 상세 동작 | 개념 정의만 | 각 계층별 CRUD + TTL + 승격 조건 상세 작성 | 01_memory-hierarchy |
| I-2 | RAG 6단계 파라미터 상세 | 단계명만 정의 | 각 단계의 입력/출력/에러/메트릭 상세 작성 | 02_rag-pipeline |
| I-3 | VectorStore 어댑터 구현 상세 | 인터페이스만 정의 | Chroma/Qdrant 어댑터 구현 로직 작성 | 03_vector-db |
| I-4 | Semantic Cache 무효화 상세 | 3가지 정책명만 | TTL/Drift/수동 무효화 구현 로직 작성 | 04_memory-distillation |
| I-5 | 승격/강등 알고리즘 | 조건만 나열 | 스코어링 함수 + QoD 연동 + 자동화 로직 | 01_memory-hierarchy |
| I-6 | PII 마스킹 파이프라인 | regex 4종 나열 | 탐지→분류→마스킹→검증 전체 파이프라인 | 04_memory-distillation |
| I-7 | V1→V2 마이그레이션 | 원칙만 명시 | 단계별 절차 + 무결성 검증 + 롤백 | 03_vector-db |
| I-8 | GraphRAG 상세 | NetworkX 언급만 | 노드/엣지 타입 + 쿼리 파이프라인 + V2 Neo4j 전환 | 02_rag-pipeline |

### 6.3 STEP7-D 82건 서브폴더 매핑 (요약)

| 서브폴더 | STEP7-D 항목 | 건수 |
|---------|-------------|------|
| **01_memory-hierarchy** | S7D-001~008, S7D-035~042, S7-A-030/031, S7-F-022/023/026/061/096, INNOV-09 | ~22건 |
| **02_rag-pipeline** | S7D-012, S7D-018~026 | ~10건 |
| **03_vector-db** | S7D-009~017, S7D-027~034 | ~18건 |
| **04_memory-distillation** | S7D-003~006, S7D-039~046, S7D-065/066 | ~14건 |
| (기타/V2+ 전용) | 나머지 | ~18건 |

---

## 7. Phase 실행 계획

### 7.1 V-Phase 정렬

| SOT2 Phase | Part2 연결 | 목표 | 핵심 산출물 |
|-----------|-----------|------|-----------|
| **Phase 0: 분석·설계** | V0-STEP-5 (Day 8-9) | 스키마 확정, 저장소 스캐폴딩 | SQLite 테이블 정의, Chroma 컬렉션 설계, 어댑터 인터페이스 확정 |
| **Phase 1: V1 MVP 구현** | V1-Phase 2 (Week 5-8) | 9 core 항목 구현 완료 | L0/L1 CRUD, Chroma 벡터 검색, 6-Stage RAG, Semantic Cache, PII 마스킹 |
| **Phase 2: V2 최적화** | V2-Phase 2 관련 | Qdrant 전환, Neo4j 전환, 승격 자동화 | QdrantAdapter, Neo4j GraphRAG, 자동 승격/강등, 메모리 충돌 해소 |
| **Phase 3: V3 스케일** | V3-Phase 2 관련 | 엔터프라이즈 확장, 멀티테넌시 | 매니지드 DB, GDPR/SOC-2, Dream Mode(오프라인 정리), 통계 대시보드 |

### 7.2 Phase 0 상세: 분석·설계

| # | 작업 | 산출물 | 완료 조건 | 상태 |
|---|------|--------|----------|------|
| P0-1 | MemoryRecordSchema 확정 (D6 참조) | `01_memory-hierarchy/MemoryRecordSchema.md` | D6 정본과 정합 확인 (14/14 체크리스트 ALL PASS) | ✅ 완료 (2026-04-04) |
| P0-2 | SQLite 테이블 DDL (L0/L1) | `01_memory-hierarchy/sqlite_ddl.sql` | 19/19 검증 체크리스트 ALL PASS (Required 7 + Optional 6 전수 매핑, SourceQoD 테이블, CHECK 제약, 인덱스 7개, WAL) | ✅ 완료 (2026-04-04) |
| P0-3 | Chroma 컬렉션 전략 확정 | `03_vector-db/chroma_collection_strategy.md` | 단일 컬렉션+메타데이터 필터 결정, BGE-M3 이중벡터, α=0.7/threshold=0.75/Top-K=20, project_id 격리 강제, 정책 검사 플로우 (12/12 검증 ALL PASS) | ✅ 완료 (2026-04-04) |
| P0-4 | VectorStore 어댑터 ABC 확정 | `03_vector-db/vectorstore_abc.py` | D2.0-06 §2.2-A VectorRecord 시그니처 1:1 정합, project_id 필수(MR-017), Deny 차단(MR-015), D6 설정 주입, ChromaAdapter 스텁 (10/10 검증 ALL PASS) | ✅ 완료 (2026-04-04) |

#### Phase 0 태스크 상세

<details>
<summary><b>P0-1. MemoryRecordSchema 확정 (D6 참조)</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.1-D6_D6_SCHEMA_STORAGE_MEMORY.md` (D6 v3.0.0 — MemoryRecordSchema, SourceQoDSchema, VectorStoreAdapterSchema, GraphRAGConfigSchema, SemanticCacheSchema + KB_EMBEDDING_RECORD 확장 포함. 본 태스크 범위: MemoryRecordSchema + SourceQoDSchema)
- `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` (LOCK — L0~L3 4계층, B-Series, TTL, Allow/Restrict/Deny 정책, QoD 임계값)
- `D:\VAMOS\docs\sot\D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` (policy_decision 정책 정본 — Allow/Restrict/Deny 판정 기준, D7 PolicyCheckSchema)
- `D:\VAMOS\docs\sot\STEP7-D_메모리_저장소_아키텍처_작업가이드.md` (82건 체크리스트 — 주의: S7D-043 스키마가 D6와 필드명 상이(layer vs scope), D2.0-06 4계층 정본 우선)
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\MEMORY_RAG_STORAGE_구조화_종합계획서.md` (본 계획서 — LOCK-MR-001~019, CONFLICT_LOG #006 참조)

**절차**:
1. D6 정본(`D2.1-D6_D6_SCHEMA_STORAGE_MEMORY.md`)에서 MemoryRecordSchema 전체 필드 읽기 — Required 7개 + Optional 6개 + L3/B-2 확장 7개 = 총 20개 필드
2. SourceQoDSchema 필드 확인 — Required 7개(source_id, project_id, qod_score, freshness, reliability, completeness, computed_at) + Optional 1개(scope) = 총 8개 필드. MemoryRecordSchema와의 연동 방식 정의 (별도 독립 스키마이며, MemoryRecord의 `source_refs` 배열이 SourceQoD의 `source_id`를 참조하는 FK 구조)
3. D2.0-06의 L0~L3 4계층 정의(§2)와 스키마 필드 매핑 검증 — `scope`(L0~L3) + `memory_type`(B-1~B-4) + `ttl`(계층별 기본값) + `policy_decision`(Allow/Restrict/Deny)
4. LOCK-MR 관련 필수 필드 포함 여부 확인:
   - `project_id` — LOCK-MR-017 (프로젝트 간 데이터 혼합 금지)
   - `scope` — LOCK-MR-001 (4계층 L0/L1/L2/L3, R-64-1 용어 통일)
   - `memory_type` — LOCK-MR-002 (B↔L 매핑: B-4→L0, B-1→L1, B-3→L2, B-2→L3)
   - `ttl` — LOCK-MR-003 (L0: session_end 또는 created_at+30일 중 먼저, CONFLICT_LOG #006 참조), LOCK-MR-004 (L1: 90일), LOCK-MR-005 (L2: 무기한), LOCK-MR-006 (L3: 무기한/deprecated)
   - `policy_decision` — LOCK-MR-015 (Deny 시 벡터 삽입 절대 금지), LOCK-MR-018 (저장 전 사용자 확인)
   - `content_summary` — LOCK-MR-019 (루프 저장 폭주 방지: 원문이 아닌 요약/메타/링크만 허용)
   - `activation_state` — LOCK-MR-016 (L3 저장/활성은 D7 ApprovalGate 필수)
5. D6 AC(Acceptance Criteria) 정합성 확인: AC-D6-002 (scope enum), AC-D6-003 (memory_type enum), AC-D6-004 (policy_decision ↔ D7 정합), AC-D6-006 (L3/B-2 확장 필드)
6. QoD 컴포넌트 교차 검증: D2.0-06 DEC-014 (relevance×0.30 + accuracy×0.25 + freshness×0.25 + completeness×0.20, 4요소) vs D6 SourceQoDSchema (freshness + reliability + completeness, 3요소) 불일치 여부 확인 → 불일치 시 CONFLICT_LOG 기록 후 D6 정본(schema SOT) 우선
7. DN-011 결정 반영: policy_decision(deny/restrict/allow)은 정책 판정 결과이며, workflow state(PASS/BLOCK/NEEDS_APPROVAL/ERROR)와는 별도 레벨 — 스키마에 workflow_status 필드 추가 불필요 확정
8. KB_EMBEDDING_RECORD 확장(D6 §7-A.1) 참조 확인: MemoryRecordSchema를 extends하며, 추가 필드(vector_dim, embedded_at_utc, embedding_model, chunk_id, chunk_token_count, source_doc_ref) — 본 태스크에서는 참조만 기록하고 상세는 03_vector-db 위임
9. 최종 스키마 문서 작성 (필드명, 타입, 필수/선택, 기본값, LOCK-MR 참조, D6 AC 매핑)

**검증** (2026-04-04 전수 통과):
- [x] D6 MemoryRecordSchema 전체 20개 필드가 빠짐없이 포함 (Required 7 + Optional 6 + L3/B-2 확장 7)
- [x] `project_id` 필드 존재 — required, LOCK-MR-017 격리
- [x] `scope` 필드 존재 — required, enum: L0|L1|L2|L3 (LOCK-MR-001, AC-D6-002). "layer" 아님 (R-64-1 용어 통일)
- [x] `memory_type` 필드 존재 — required, enum: B-1|B-2|B-3|B-4 (LOCK-MR-002, AC-D6-003)
- [x] `policy_decision` 필드 존재 — required, enum: allow|restrict|deny (LOCK-MR-015, AC-D6-004, D7 정합)
- [x] `content_summary` 필드 존재 — required, 원문이 아닌 요약 중심 (LOCK-MR-019)
- [x] `ttl` 필드 존재 — optional, 계층별 기본값 명시 (LOCK-MR-003/004/005/006, CONFLICT_LOG #006 주석)
- [x] `activation_state` 필드 존재 — optional, enum: draft|approved|active|deprecated (LOCK-MR-016 L3 게이트)
- [x] L3/B-2 확장 필드 7개 포함 — procedure_id, target_scope, trigger_conditions, steps, required_tools, safety_notes, provenance (AC-D6-006)
- [x] SourceQoDSchema 연동 방식 정의 — 별도 독립 스키마, `source_refs`(MemoryRecord) → `source_id`(SourceQoD) FK 참조
- [x] SourceQoDSchema 필드 8개 확인 — Required: source_id, project_id, qod_score, freshness, reliability, completeness, computed_at (7개) + Optional: scope (1개)
- [x] QoD 컴포넌트 교차 검증 — D2.0-06 DEC-014 (4요소) vs D6 (3요소) 불일치 확인 및 CONFLICT_LOG #007 기록
- [x] KB_EMBEDDING_RECORD 확장 참조 기록
- [x] STEP7-D S7D-043 스키마와의 필드명 차이(layer→scope) 확인 및 D6 정본 우선 적용

**산출물**: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\MemoryRecordSchema.md`
</details>

<details>
<summary><b>P0-2. SQLite 테이블 DDL (L0/L1)</b></summary>

**입력 파일**:
- P0-1 산출물: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\MemoryRecordSchema.md` (확정 스키마 — Required 7 + Optional 6 + L3/B-2 확장 7 = 총 20필드, SourceQoDSchema 8필드, B↔L 매핑, TTL 기본값)
- `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` (LOCK — L0 Session, L1 Project 정의, §2.1 TTL, §3.2 Allow/Restrict/Deny, §7.2 MemoryRecord 설계 레벨 최소 필드, V1 SQLite 단일 writer 패턴)
- `D:\VAMOS\docs\sot\D2.1-D6_D6_SCHEMA_STORAGE_MEMORY.md` (Schema SOT — MemoryRecordSchema v3.0.0 필드 정의, SourceQoDSchema, enum 제약, AC-D6-002/003/004)
- `D:\VAMOS\docs\sot\D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` (policy_decision ↔ D7 PolicyCheckSchema 정합 참조)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` V1-Phase 2 (L1908-1918: L0/L1 SQLite CRUD 구현 경로, TTL LOCK 값, project_id별 분리)
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\MEMORY_RAG_STORAGE_구조화_종합계획서.md` (본 계획서 — LOCK-MR-001~019 레지스트리, CONFLICT_LOG #006 L0 TTL 참조)

**절차**:
1. P0-1 확정 MemoryRecordSchema (§1.1~§1.3, 20개 필드)를 기반으로 SQLite 테이블 DDL 작성. L0/L1 범위이므로 L3/B-2 확장 필드 7개는 본 태스크 범위 외 — 향후 확장 시 ALTER TABLE 가능 여부만 확인하고 주석 기록
2. **테이블 설계 결정**: 단일 테이블 `memory_records` + `scope` 컬럼(L0/L1/L2/L3 구분) 방식 vs L0/L1 분리 테이블 방식 중 택1 — 근거(TTL 정책 차이, 쿼리 패턴, V2 확장성) 기록. 어느 방식이든 MemoryRecordSchema 필드 세트는 동일해야 함
3. **L0(Session Memory) 테이블 컬럼** — P0-1 Required 7개 + Optional 6개 = 13개 컬럼 전수 매핑:
   - Required: `record_id` TEXT PK, `project_id` TEXT NOT NULL, `scope` TEXT NOT NULL DEFAULT 'L0' CHECK(scope IN ('L0','L1','L2','L3')), `memory_type` TEXT NOT NULL DEFAULT 'B-4' CHECK(memory_type IN ('B-1','B-2','B-3','B-4')), `content_summary` TEXT NOT NULL, `created_at` TEXT NOT NULL, `policy_decision` TEXT NOT NULL CHECK(policy_decision IN ('allow','restrict','deny'))
   - Optional: `ttl` TEXT DEFAULT 'session_end', `tags` TEXT (JSON 배열), `source_refs` TEXT (JSON 배열 — SourceQoDSchema.source_id FK 참조), `masked` INTEGER DEFAULT 0, `activation_state` TEXT DEFAULT 'draft' CHECK(activation_state IN ('draft','approved','active','deprecated')), `version` TEXT DEFAULT 'v1.0.0'
   - ⚠️ 구 용어 `session_id`(PK 아님), `updated_at`(스키마 외) 사용 금지. PK는 반드시 `record_id` (D6 Required #1)
4. **L1(Project Memory) 테이블 컬럼** — L0과 동일한 13개 컬럼 (MemoryRecordSchema 기반), DEFAULT 값만 상이:
   - `scope` DEFAULT 'L1', `memory_type` DEFAULT 'B-1', `ttl` DEFAULT '90d'
   - ⚠️ 구 용어 `layer`(→`scope`, R-64-1), `content`(→`content_summary`, LOCK-MR-019), `embedding_id`(스키마 외, KB_EMBEDDING_RECORD는 별도 확장), `source_qod`(→`source_refs` FK 구조, P0-1 §2.2) 사용 금지
5. **SourceQoDSchema 테이블 DDL**: `source_qod` 테이블 — P0-1 §2 기준 Required 7 + Optional 1 = 8개 컬럼: `source_id` TEXT PK, `project_id` TEXT NOT NULL, `qod_score` REAL NOT NULL CHECK(0.0 <= qod_score AND qod_score <= 1.0), `freshness` REAL NOT NULL CHECK(0.0 <= freshness AND freshness <= 1.0), `reliability` REAL NOT NULL CHECK(0.0 <= reliability AND reliability <= 1.0), `completeness` REAL NOT NULL CHECK(0.0 <= completeness AND completeness <= 1.0), `computed_at` TEXT NOT NULL, `scope` TEXT (optional). memory_records.source_refs 배열이 source_qod.source_id를 참조하는 1:N FK 구조 (논리적 FK — SQLite JSON 배열이므로 물리적 FOREIGN KEY 미적용, 애플리케이션 레벨 정합성)
6. **CHECK 제약 조건**: scope enum (AC-D6-002), memory_type enum (AC-D6-003), policy_decision enum (AC-D6-004), activation_state enum, qod_score 범위(0.0~1.0)
7. **인덱스 정의** (아래 테이블명 `memory_records`는 단일 테이블 방식 기준 — 절차2에서 분리 테이블 선택 시 각 L0/L1 테이블에 동일 인덱스를 각각 정의):
   - `idx_memory_project_id` ON memory_records(`project_id`) — LOCK-MR-017 격리 쿼리
   - `idx_memory_scope` ON memory_records(`scope`) — 계층별 조회
   - `idx_memory_created_at` ON memory_records(`created_at`) — 시간순 정렬/TTL 만료
   - `idx_memory_ttl` ON memory_records(`ttl`) — TTL 만료 처리 (LOCK-MR-003/004)
   - `idx_memory_scope_project` ON memory_records(`scope`, `project_id`) — 복합 인덱스 (계층+프로젝트 필터)
   - `idx_memory_policy` ON memory_records(`policy_decision`) — deny 필터링 (LOCK-MR-015)
   - `idx_qod_project_id` ON source_qod(`project_id`) — QoD 프로젝트별 조회
8. **TTL 만료 설계**:
   - L0: `session_end` 또는 `created_at + 30일` 중 먼저 도래한 시점에 만료 (LOCK-MR-003, CONFLICT_LOG #006 — D2.0-06 §2.1+Part2 기준 정본)
   - L1: `90일` 기본, 프로젝트 단위 30일 연장 가능 (LOCK-MR-004)
   - 만료 처리 방식: 주기적 DELETE 또는 soft-delete(is_expired 플래그) 중 택1, 근거 기록
9. **D2.0-06 V1 제약 반영**: SQLite 단일 writer 패턴 — WAL 모드 활성화 + 동시성 제약 주석 기록

**검증** (2026-04-04 전수 통과 — 19/19 ALL PASS):
- [x] L0, L1 테이블 DDL 각각 존재 (또는 단일 테이블 + scope 구분 — 설계 결정 근거 기록 확인) — 단일 테이블 `memory_records` 채택, 5개 근거 + 3개 미채택 사유 기록 (DDL L38-59)
- [x] `record_id` PK 사용 확인 — `session_id`, `memory_id` 등 비표준 PK 부재 (D6 Required #1) — DDL L76 + L75 경고 주석
- [x] Required 7개 필드 전수 매핑: `record_id`, `project_id`, `scope`, `memory_type`, `content_summary`, `created_at`, `policy_decision` — DDL L76~L112
- [x] Optional 6개 필드 전수 매핑: `ttl`, `tags`, `source_refs`, `masked`, `activation_state`, `version` — DDL L127~L154
- [x] `project_id` NOT NULL (LOCK-MR-017 격리) — DDL L80
- [x] `scope` CHECK 제약 — enum: L0|L1|L2|L3 (LOCK-MR-001, AC-D6-002) — DDL L89
- [x] `memory_type` CHECK 제약 — enum: B-1|B-2|B-3|B-4 (LOCK-MR-002, AC-D6-003) — DDL L97
- [x] `policy_decision` CHECK 제약 — enum: allow|restrict|deny (LOCK-MR-015, AC-D6-004) — DDL L112
- [x] `content_summary` 컬럼명 확인 — `content` 아님 (LOCK-MR-019 원문 저장 금지) — DDL L102 + L101 경고
- [x] `ttl` 필드 + TTL 인덱스 포함 (LOCK-MR-003/004) — DDL L127 컬럼 + L236 인덱스
- [x] L0 DEFAULT: scope='L0', memory_type='B-4', ttl='session_end' (LOCK-MR-002/003) — DDL L303-304 앱 레벨 규약
- [x] L1 DEFAULT: scope='L1', memory_type='B-1', ttl='90d' (LOCK-MR-002/004) — DDL L305 앱 레벨 규약
- [x] SourceQoDSchema 테이블 DDL 존재 — 8개 필드, source_id PK, qod_score 범위 CHECK — DDL L187-213 (freshness/reliability/completeness 범위 CHECK 포함)
- [x] `source_refs` → `source_qod.source_id` FK 참조 관계 주석/설명 존재 — DDL L134-139 논리적 FK 설명 + L309-311 앱 정합성 규약
- [x] 구 용어 부재 확인: `layer`(→scope), `source_qod` 인라인(→source_refs FK), `embedding_id`(→KB_EMBEDDING_RECORD 별도), `session_id`/`memory_id`(→record_id) (S-7 정정 완료) — 경고 주석에만 참조, 컬럼/테이블명 미사용
- [x] L3/B-2 확장 필드 7개는 범위 외 — 향후 ALTER TABLE 가능성 주석 존재 — DDL L157-177 (7개 ALTER 예시 + SQLite 제약 확인)
- [x] `activation_state` CHECK 제약 — enum: draft|approved|active|deprecated (LOCK-MR-016) — DDL L151
- [x] 인덱스 최소 5개 이상 정의 (project_id, scope, created_at, ttl, scope+project_id 복합) — 7개 인덱스 (DDL L224~L250)

**설계 결정 요약**:
- 테이블 구조: 단일 `memory_records` + `scope` 구분 (DDL L41)
- TTL 만료: 주기적 hard DELETE (DDL L256)
- V1 제약: SQLite WAL 모드 (DDL L34)

**산출물**: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\sqlite_ddl.sql`
</details>

<details>
<summary><b>P0-3. Chroma 컬렉션 전략 확정</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` (LOCK — §2.2 Chroma V1 로컬 임베디드 지침(LOCK-MR-012), §1 project_id 격리(LOCK-MR-017), §2.2-A VectorStore 어댑터 패턴(LOCK-MR-014), §3.2 Deny 벡터 삽입 금지(LOCK-MR-015), §1.1/§4 RAG 운영 한계(문서 15개/청크 30개), V1 단일 writer 패턴)
- `D:\VAMOS\docs\sot\D2.1-D6_D6_SCHEMA_STORAGE_MEMORY.md` (Schema SOT — D6 v3.0.0: VectorStoreAdapterSchema, KB_EMBEDDING_RECORD 확장(§7-A.1: vector_dim, embedding_model, chunk_id 등), SemanticCacheSchema. 본 태스크 범위: VectorStoreAdapterSchema의 컬렉션 관련 파라미터 + KB_EMBEDDING_RECORD의 vector_dim 제약)
- `D:\VAMOS\docs\sot\STEP7-D_메모리_저장소_아키텍처_작업가이드.md` (82건 체크리스트 — §6.3 매핑: 03_vector-db 대상 S7D-009~017/S7D-027~034(~18건). 본 태스크 범위: S7D-009(Chroma 임베디드 설정: SQLite 백엔드, 로컬 영속, 컬렉션 분리/메타데이터 필터, 10K 문서), S7D-011(벡터 인덱스 컬렉션 전략: 프로젝트별 분리 vs 단일 컬렉션+메타데이터 필터 트레이드오프). 참고: S7D-010(V2 Qdrant 서버 전환)은 V2 scope으로 P0-3 범위 외. S7D-012(Hybrid Search α)는 02_rag-pipeline 소관이나 파라미터 값 확인 목적으로 참조)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` V1-Phase 2 (L1918-1920: Chroma V1 BGE-M3 1024dim 원본 + Matryoshka 256dim 검색용 LOCK, L2034: Hybrid Search α=0.7 + Top-K=20 LOCK, L2038: Similarity threshold=0.75 LOCK)
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\MEMORY_RAG_STORAGE_구조화_종합계획서.md` (본 계획서 — LOCK-MR-008(α)/009(threshold)/011(BGE-M3)/012(Chroma)/015(Deny 금지)/017(격리) 레지스트리, R-64-3 벡터 삽입 전 정책 검사, R-64-5 RAG 운영 한계, 부록C LOCK 추적표)
- P0-1 산출물: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\MemoryRecordSchema.md` (확정 스키마 — project_id(Required, LOCK-MR-017), scope(L0~L3), memory_type(B-1~B-4), policy_decision(allow/restrict/deny) 필드 정의 + KB_EMBEDDING_RECORD 확장 참조(§3))

**절차**:
1. D2.0-06 §2.2에서 Chroma V1 사용 지침 확인 — 로컬 임베디드 모드(서버리스), 단일 writer 패턴, 영속 경로 설정 (LOCK-MR-012: Chroma 로컬 임베디드)
2. BGE-M3 임베딩 모델 연동 방식 확인 — 1024dim 원본 저장 + Matryoshka 256dim 검색용 이중 벡터 전략, 임베딩 생성 시점(6-Stage RAG의 Stage 3 Embed), 컬렉션 내 차원(dim) 설정 방식, embedding_function 파라미터 (LOCK-MR-011: 1024dim + 256dim)
3. **컬렉션 분리 전략 결정**: 프로젝트별 컬렉션 분리(`vamos_{project_id}`) vs 단일 컬렉션 + 메타데이터 필터(`where={"project_id": ...}`) 비교 분석 — 평가 기준: ①격리 수준(LOCK-MR-017 준수), ②쿼리 성능, ③운영 복잡도(컬렉션 수 증가 시), ④V2 Qdrant 전환 용이성(LOCK-MR-013), ⑤Chroma API 제약. 택1 + 근거 기록
4. **project_id 격리 구현 방식 확정** — 절차3 결정에 따른 구체적 격리 메커니즘 명시: 메타데이터 필터 방식 시 `where` 절 필수 적용 패턴 + 필터 누락 방지 규약, 컬렉션 분리 방식 시 네이밍 컨벤션 + 컬렉션 라이프사이클(생성/삭제) 정의 (LOCK-MR-017: 프로젝트 간 데이터 혼합 금지)
5. Hybrid Search α 파라미터 기본값 확인 — Dense α=0.7, Sparse(BM25) 1-α=0.3 (LOCK-MR-008, Part2 L2034 ← S7D-012 ← D2.0-06 L778). Top-K=20 확인 (Part2 L2034 LOCK). Chroma에서 Hybrid Search 구현 방식(dense+sparse 결합) 확인
6. Similarity threshold 기본값 확인 — 0.75 (LOCK-MR-009, Part2 L2038 ← S7D-018). Chroma `where` 절 또는 후처리 필터링 방식 결정
7. R-64-3(벡터 삽입 전 정책 검사) 반영 — Chroma 삽입(upsert) 전 D7 PolicyCheck 결과 확인 플로우 설계: policy_decision=deny 시 벡터 삽입 절대 금지(LOCK-MR-015), restrict 시 마스킹 후 삽입, allow 시 정상 삽입. P0-1 MemoryRecordSchema의 `policy_decision` 필드와 연동
8. R-64-5(RAG 운영 한계) 반영 — V1 기준 문서 15개, 청크 30개 제한(D2.0-06 §1.1+§4)이 컬렉션 용량 설계·인덱싱 전략에 미치는 영향 확인. 컬렉션 최대 문서 수 / 청크 수 상한 설정 여부 결정
9. STEP7-D 관련 항목 확인 — S7D-009(Chroma 임베디드 설정: SQLite 백엔드, 로컬 영속, 컬렉션 분리/메타데이터 필터, 10K 문서 용량), S7D-011(벡터 인덱스 컬렉션 전략: 프로젝트별 분리 vs 단일 컬렉션+메타데이터 필터 트레이드오프 분석) 요구사항을 전략에 반영. S7D-010(V2 Qdrant 전환)은 V2 scope으로 P0-3 범위 외. D2.0-06 정본과 불일치 시 D2.0-06 우선(R3)
10. **P0-4 경계 확인**: 본 태스크(P0-3)는 컬렉션 전략·파라미터·격리 방식·정책 플로우 확정까지. VectorStore 어댑터 ABC 인터페이스(upsert/search/delete/get_by_id 4개 메서드 시그니처, LOCK-MR-014)와 ChromaAdapter 구현 스텁은 P0-4 위임. 경계 기준: P0-3=What(전략), P0-4=How(인터페이스)
11. 최종 전략 문서 작성 — 컬렉션 분리 결정+근거, 임베딩 연동(dual-dim), 검색 파라미터(α/threshold/Top-K), 격리 방식, 정책 검사 플로우, V1 운영 한계 반영, STEP7-D 매핑을 포함

**검증** (2026-04-04 전수 통과 — 12/12 ALL PASS + 산출물 재검증 8건 수정 완료):
- [x] Chroma V1 로컬 임베디드 모드 사용 명시 (LOCK-MR-012: Chroma 로컬 임베디드) — 산출물 §1.1
- [x] 컬렉션 분리 전략 결정 — **단일 컬렉션 + 메타데이터 필터** 채택 + 5개 평가 기준별 근거 + 6개 결정 근거 기록 — 산출물 §3.1-3.2
- [x] BGE-M3 임베딩 연동 방식 명시 — 1024dim 원본 저장(**SQLite KB_EMBEDDING_RECORD BLOB**) + Matryoshka 256dim 검색용 이중 벡터, embedding_function 설정, 코드 예시 포함 (LOCK-MR-011) — 산출물 §2.1-2.3
- [x] Hybrid Search α 기본값 명시 — Dense α=0.7, Sparse 1-α=0.3 (LOCK-MR-008). **α 표기 통일 주석**(종합계획서 §1.4 L98 인용) 포함 — 산출물 §5.1
- [x] Similarity threshold 기본값 명시 — 0.75 + **후처리 필터링** 방식 결정 + 코드 예시. **cosine 변환 공식 `similarity = 1 - distance` 검증 완료** (LOCK-MR-009) — 산출물 §6.1
- [x] Top-K 기본값 명시 — 20 (Part2 L2034, LOCK=N 기본값 — 설정 조정 가능). Part2 표 LOCK=N 명확화 — 산출물 §5.1
- [x] project_id 격리 방식 명시 — 어댑터 메서드 레벨 필터 강제 + ValueError 가드 + 크로스 프로젝트 차단. Chroma 메타데이터에 **policy_decision 포함** (LOCK-MR-017) — 산출물 §4.1-4.4
- [x] 벡터 삽입 전 정책 검사 플로우 명시 — deny 삽입 금지, restrict 마스킹 후 삽입, allow 정상 + MemoryRecordSchema §1.6 연동 (LOCK-MR-015, R-64-3) — 산출물 §7.1-7.2
- [x] V1 RAG 운영 한계 반영 — 문서 15개/청크 30개 제한 → 프로젝트당 최대 450 벡터 산출 + 상한 적용 방식 결정 (R-64-5, D2.0-06 §1.1+§4) — 산출물 §8.1-8.2
- [x] STEP7-D 항목 반영 — S7D-009(Chroma 임베디드 설정) ✅, S7D-011(컬렉션 전략 트레이드오프) ✅, S7D-010(V2 Qdrant) 범위 외 ✅ — 산출물 §9
- [x] P0-4 경계 명확 — What(P0-3) vs How(P0-4) 경계 표 + MR-014 P0-4 위임 명시 — 산출물 §10
- [x] LOCK-MR 참조 정합성 — MR-008(α)/009(threshold)/011(BGE-M3)/012(Chroma)/015(Deny 금지)/017(격리) 6개 전수 참조 추적 표 — 산출물 LOCK-MR 참조 추적

**산출물 재검증** (2026-04-04, 8건 수정):
- [x] §6.1 cosine 변환 공식 오류 수정: `1-distance/2` → `1-distance` (CRITICAL)
- [x] §2.2 원본 1024dim 저장 위치 명확화: SQLite KB_EMBEDDING_RECORD 확장 테이블 BLOB (D6 §7-A.1)
- [x] §5.2 결과 융합 V1 기본 결정: 가중 합산 기본 + config.toml로 RRF 전환 가능
- [x] §1.1 영속 경로 근거 명확화: P0-3 결정(D2.0-06 기반 제안), config로 변경 가능
- [x] §5 α 표기 통일 주석 추가 (종합계획서 §1.4 L98 인용)
- [x] §8.1 "10개 프로젝트 가정" → "V1 추정치, 실운영 규모에 따라 변동" 명시
- [x] §4.1 Chroma 메타데이터에 policy_decision 추가 (restrict 필터링 활용)
- [x] 설계 결정 요약 표 번호 순서 정렬 + 결정 7(1024dim 저장), 8(Similarity 변환) 추가

**설계 결정 요약**:
- 컬렉션 전략: 단일 컬렉션 `vamos_memory` + 메타데이터 필터 (§3.2)
- 검색 벡터: Matryoshka 256dim (검색) + 1024dim (SQLite BLOB 원본 보존) (§2)
- Hybrid Search: V1 기본 가중 합산 (§5.2), threshold=0.75 후처리 (§6.1)
- 격리: 어댑터 레벨 project_id 필터 강제 + ValueError 가드 (§4)
- 정책: deny→삽입 금지, restrict→마스킹 후 삽입, allow→정상 (§7)

**산출물**: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\03_vector-db\chroma_collection_strategy.md`
</details>

<details>
<summary><b>P0-4. VectorStore 어댑터 ABC 확정</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` (LOCK — §2.2-A VectorStore 어댑터 인터페이스(LOCK-MR-014): 4개 메서드 최소 계약 + VectorRecord 타입 + top_k 기본값=10 + config.toml 조정 가능 + 구현 어댑터 버전별 배정 + 제약: 어댑터 교체는 설정(config) 변경만으로 가능, 비즈니스 로직 수정 유발 금지(L184))
- `D:\VAMOS\docs\sot\D2.1-D6_D6_SCHEMA_STORAGE_MEMORY.md` (Schema SOT — D6 v3.0.0: §4.3 VectorStoreAdapterSchema(어댑터 설정 스키마: adapter_id, backend, mode, embedding_model, dimension, collection_name, connection_url, version_tier) + §7-A.1 KB_EMBEDDING_RECORD 확장(vector_dim, embedded_at_utc, embedding_model, chunk_id). 본 태스크 범위: VectorStoreAdapterSchema의 설정 필드를 ABC `__init__`에 주입 + KB_EMBEDDING_RECORD와 VectorRecord 관계 정의)
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\MEMORY_RAG_STORAGE_구조화_종합계획서.md` (LOCK-MR-014 VectorStore 어댑터 4개 메서드, LOCK-MR-015 Deny 벡터 삽입 금지, LOCK-MR-017 project_id 격리, R-64-3 벡터 삽입 전 정책 검사 필수, W-8 API 계약만 공개 원칙)
- P0-3 산출물: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\03_vector-db\chroma_collection_strategy.md` (P0-3 확정 전략 — §4.1: 단일 컬렉션+메타데이터 필터, 어댑터 모든 public 메서드에서 project_id 필수(LOCK-MR-017), §4.2: `_enforce_project_filter()` 가드 패턴, §7: deny→삽입 금지/restrict→마스킹 후 삽입/allow→정상(LOCK-MR-015), §5.1: Top-K retrieve=20(LOCK=N, 조정 가능)/α=0.7/threshold=0.75, §10: P0-3=What(전략) → P0-4=How(인터페이스) 경계)
- P0-1 산출물: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\MemoryRecordSchema.md` (확정 스키마 — VectorRecord와 MemoryRecordSchema/KB_EMBEDDING_RECORD 간 관계 정의 참조용)

**절차**:
1. **D2.0-06 §2.2-A 최소 계약 수용**: VectorStore 어댑터 패턴 요구사항 전수 확인 (LOCK-MR-014) — 4개 메서드 시그니처(`upsert(records: VectorRecord[]) → void`, `search(query_vector: float[], top_k: int = 10, filters: dict) → VectorRecord[]`, `delete(ids: str[]) → void`, `get_by_id(id: str) → VectorRecord | None`) + 구현 어댑터 배정(V1: ChromaAdapter, V2: QdrantAdapter/PgvectorAdapter, V3: 매니지드) + 제약(어댑터 교체는 config 변경만으로 가능, 비즈니스 로직 수정 유발 금지)
2. **VectorRecord 타입 정의**: D2.0-06 §2.2-A가 사용하는 `VectorRecord` 타입을 명시적으로 정의 — MemoryRecordSchema(P0-1)의 필드 중 벡터 저장소에 필요한 부분집합 + KB_EMBEDDING_RECORD(D6 §7-A.1)의 vector_dim/embedding_model/chunk_id 참조. VectorRecord ↔ MemoryRecordSchema ↔ KB_EMBEDDING_RECORD 간 관계 다이어그램 포함
3. **P0-3 확정 전략 반영**: ABC 시그니처에 P0-3 결정사항 통합 — ① project_id를 모든 public 메서드의 필수 파라미터로 추가(P0-3 §4.1, LOCK-MR-017: 프로젝트 간 데이터 혼합 금지) ② `_enforce_project_filter()` 내부 가드 메서드 설계(P0-3 §4.2) ③ upsert에서 policy_decision 검사 플로우 연동 — deny 시 ValueError/삽입 거부, restrict 시 마스킹 후 삽입, allow 시 정상(P0-3 §7, LOCK-MR-015: Deny 벡터 삽입 절대 금지, R-64-3)
4. **D6 VectorStoreAdapterSchema 기반 `__init__` 설계**: ABC 생성자에 D6 §4.3 VectorStoreAdapterSchema 필드(backend, mode, embedding_model, dimension, collection_name, connection_url, version_tier) 기반 설정 주입 구조 설계 — config.toml `[memory.vector]` 섹션과 연동, 어댑터 교체 시 config 변경만으로 전환 가능하도록(D2.0-06 L184 제약)
5. **top_k 기본값 정합 처리**: D2.0-06 §2.2-A의 search `top_k` 기본값=10(API 레벨)과 P0-3 §5.1의 검색 파이프라인 Top-K=20(LOCK=N, 조정 가능)의 관계 정리 — ABC search 시그니처에서는 D2.0-06 원본 기본값=10 유지, 파이프라인 레벨에서 config.toml `default_top_k`로 20 오버라이드 가능하도록 설계
6. **ChromaAdapter 구현 스텁 작성** (V1 대상, LOCK-MR-012): VectorStoreABC를 상속, 4개 메서드 구현 스텁 + P0-3 §1(Chroma 로컬 임베디드, 단일 컬렉션 `vamos_memory`) 전략 적용
7. **QdrantAdapter 시그니처 설계** (V2 scope, LOCK-MR-013): ABC 상속 시그니처 수준만 정의 — 구현 스텁은 Phase 2(V2) 위임. connection_url(서버 모드) 활용 패턴만 명시
8. **ABC 인터페이스 코드 작성** (Python ABC): `abc.ABC` + `@abstractmethod` 기반, 위 1~7의 모든 결정사항 반영한 최종 코드

**검증** (2026-04-04 전수 통과 — 10/10 ALL PASS):
- [x] VectorStoreABC 클래스 정의 존재 (Python `abc.ABC` 상속) — 산출물 L120
- [x] 4개 필수 메서드(upsert/search/delete/get_by_id) 시그니처가 **D2.0-06 §2.2-A 원본과 1:1 정합** — 파라미터명, 타입, 기본값(top_k=10) 일치 확인 (R3: DESIGN > IMPL) — 산출물 §2.3 L207-267
- [x] 각 메서드 입출력 타입 **VectorRecord** 기반 (D2.0-06 §2.2-A) — VectorRecord 타입 클래스 정의 포함, MemoryRecordSchema/KB_EMBEDDING_RECORD와의 관계 다이어그램 포함 — 산출물 §1 L34-97
- [x] 모든 public 메서드에 **project_id 필수 파라미터** 포함 + `_enforce_project_filter()` 내부 가드 (P0-3 §4.1-4.2, LOCK-MR-017) — 산출물 §2.1 L159-171
- [x] upsert에서 **policy_decision 검사 연동** — deny 시 삽입 거부(ValueError) 로직 포함 (P0-3 §7, LOCK-MR-015, R-64-3) — 산출물 §2.2 L177-193
- [x] `__init__`에 **D6 VectorStoreAdapterSchema 필드** 기반 설정 주입 (adapter_id, backend, mode, embedding_model, dimension, collection_name, connection_url, version_tier — 8개 전수 매핑) — 산출물 L134-153
- [x] **config 교체 제약** 준수 — 어댑터 교체 시 비즈니스 로직 변경 없음, config.toml 변경만으로 전환 가능 (D2.0-06 L184) — 산출물 §5 LOCK-MR 추적표
- [x] ChromaAdapter 구현 스텁 포함 (V1 대상, LOCK-MR-012) — backend="chroma", mode="embedded", collection_name="vamos_memory" — 산출물 §3 L282-386
- [x] QdrantAdapter 시그니처 스텁 포함 (V2 scope, LOCK-MR-013 — 구현은 Phase 2 위임) — backend="qdrant", mode="server", connection_url 포함 — 산출물 §4 L398-466
- [x] **LOCK-MR 참조 추적**: MR-014(4개 메서드)/MR-015(Deny 금지)/MR-017(격리)/MR-012(V1 Chroma)/MR-013(V2 Qdrant) 5개 전수 참조 확인 — 산출물 §5 L469-493

**산출물**: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\03_vector-db\vectorstore_abc.py`
</details>

**Phase 0→Phase 1 게이트 (G0)**:
- [x] **G0-1**: P0-1~P0-4 모두 완료 (P0-1 ✅ / P0-2 ✅ / P0-3 ✅ / P0-4 ✅) — 전체 완료 (2026-04-04)
- [x] **G0-2**: D6 정본(`D2.1-D6_D6_SCHEMA_STORAGE_MEMORY.md`)과 스키마 정합 확인 — P0-1에서 20개 필드 전수 대조 통과 (2026-04-04)

### 7.3 Phase 1 상세: V1 MVP (Part2 V1-Phase 2 연동) — ✅ 완료 (11/11, 2026-04-13)

> Part2 V1-Phase 2 (Week 5-8)의 9 core 항목 + Phase 전환 게이트 12항목과 1:1 정렬
> **Phase 1 전체 상태**: ✅ 완료 — P1-1~P1-11 전체 완료 (2026-04-13), 심층 재검증 14건 교정 완료 (2026-04-13), 게이트 G1 PASS, Phase 2 진입 가능

| # | 항목 | Part2 대응 | LOCK 준수 | 서브폴더 | 상태 |
|---|------|-----------|----------|---------|------|
| P1-1 | L0 Session Memory CRUD | Part2 항목1 | LOCK-MR-003 (TTL) | 01 | ✅ 완료 (2026-04-13, v1.1). L0 CRUD L3 수준 완성 — CRUD 4경로+TTL+격리+확인훅. 1029줄 1건. 재검증 step2 5건+심층 1건(EscalationPayload 표준 필드 보강). 이월 없음 |
| P1-2 | L1 Project Memory CRUD | Part2 항목2 | LOCK-MR-004 (TTL), LOCK-MR-017 (격리) | 01 | ✅ 완료 (2026-04-13, v1.1). L1 CRUD L3 수준 완성 — CRUD 4경로+TTL 90d(연장120d)+격리+확인훅+L0→L1 승격. 1건. 재검증 step2 3건+심층 2건(EscalationPayload 표준 필드 보강, DDL 확장 ALTER TABLE 3건 추가). 이월 없음 |
| P1-3 | Chroma Vector DB 연동 | Part2 항목3 | LOCK-MR-011 (BGE-M3), LOCK-MR-012 (Chroma) | 03 | ✅ 완료 (2026-04-13, v1.1). ChromaVectorStore L3 수준 완성 — 4메서드 FULL 구현+BGE-M3 256dim+BM25 동기화+R-64-5 용량 검사+에러 12종+복구/재시도+I-3 SHELL→FULL. 1건. 재검증 step2 0건+심층 1건(로그 JSON lock_checks+trace_id 추가). 이월 없음 |
| P1-4 | JSON GraphRAG | Part2 항목4 | — | 02 | ✅ 완료 (2026-04-13, v1.2). JsonGraphStore L3 수준 완성 — D6 8필드 전수+노드 10종/엣지 10종+BFS 탐색+project_id 3중 격리+JSON 영속+ABC+I-8 SHELL→FULL. 1건. 재검증 step2 4건+심층 1건(§3.5 B-Series→NodeType 매핑 요약 §6.2 TYPE_MAP 정합 교정). 이월 없음 |
| P1-5 | Semantic Cache | Part2 항목5 | LOCK-MR-010 (cosine≥0.95) | 04 | ✅ 완료 (2026-04-13, v1.2). SemanticCache L3 수준 완성 — D6 8필드+cosine≥0.95+무효화 5종+LRU 1000+격리+Deny 차단+에러 12종+I-4 SHELL→FULL. 1건. 재검증 step2 4건+심층 2건(EscalationPayload/로그 JSON 날짜 2026-01-17→04-13 교정). 이월 없음 |
| P1-6 | 대화 내보내기/가져오기 | Part2 항목6 | — | 04 | ✅ 완료 (2026-04-13, v1.2). ExportImportManager L3 수준 완성 — Export 3포맷+Import+20필드 직렬화+SHA-256+격리+PII 확인+충돌 해소 3전략+KG/QoD 동반+S7D-008+에러 12종+왕복 무손실. 1건. 재검증 step2 3건+심층 2건(P1-7 인터페이스 has_pii→pii_found 교정, mask() 반환 타입 MaskResult 교정). 이월 없음 |
| P1-7 | PII 마스킹 | Part2 항목7 | LOCK-MR-015 (Deny 금지) | 04 | ✅ 완료 (2026-04-13, v1.2). PIIMasker L3 수준 완성 — PII 8종 탐지+정규식+패턴 사전+4등급 민감도+DCL 교차 판정+마스킹 완전성+6단계 파이프라인+Deny 금지+격리+에러 12종+I-6 SHELL→FULL. 1건. 재검증 step2 3건+심층 2건(로그 JSON trace_id 추가, lock_checks object 형식 P1-5/6 정합). 이월 없음 |
| P1-8 | B-3 Memory Decay | Part2 항목8 | LOCK-MR-002 (B↔L 매핑) | 01 | ✅ 완료 (2026-04-13, v1.2). B-3 Decay L3 수준 완성 — 지수 감쇠(half_life=30d)+3-Tier 임계값+운영 메타 5필드+비활성화/강등/복원+I-5 강등 트리거+배치 스케줄러+에러 4종+Big-O+T-DEC-01~32+P2 12건. 1건. 재검증 step2 6건+심층 2건(§0 교차 참조 블록 신설, EscalationPayload 표준 키 재구조화). 이월 없음 |
| P1-9 | DCL 기초 구현 | Part2 항목9 | LOCK-MR-015/016/017/018 | 02 | ✅ 완료 (2026-04-13, v1.2). DCL L3 수준 완성 — Allow/Restrict/Deny+D7 5-Gate+PII 교차+L3 ApprovalGate+확인 훅+Deny 금지+DCL-FIN/TECH+에러 12종+T-DCL-01~32+P2 12건. 1건. 재검증 step2 4건+심층 1건(P1-4 교차 참조 섹션 번호 §12→§11 교정). 이월 없음 |
| P1-10 | 6-Stage RAG Pipeline 통합 | Part2 게이트6 | LOCK-MR-007 (6단계) | 02 | ✅ 완료 (2026-04-13, v1.1). 6-Stage RAG Pipeline L3 수준 완성 — 6 Stage 독립 I/O+Query-Time Sub-Pipeline+에러 21종+복구 11전략+에스컬레이션 3레벨+R-01-7+Big-O+MET 14종+I-2 SHELL→FULL 10/10+T-RAG 25건+P2 12건. 1건. 재검증 step2 5건(P1-5/7/4 인터페이스 시그니처 교정)+심층 0건. 이월 없음 |
| P1-11 | Hybrid Search 통합 | Part2 게이트7 | LOCK-MR-008/009 (α, threshold) | 02 | ✅ 완료 (2026-04-13, v1.1). Hybrid Search L3 수준 완성 — Dense+Sparse 결합+α=0.7+RRF+Min-Max+Threshold=0.75+P1-10 Stage 5 통합+에러 10종+Graceful Degradation+에스컬레이션+R-01-7+Big-O+MET 12종+T-HYB 25건+P2 12건. 1건. 재검증 step2 1건+심층 2건(EscalationPayload escalation_id 추가, P1-4 교차참조 §12→§11 교정). 이월 없음 |

### 7.4 Phase 전환 게이트

| 전환 | 필수 조건 | 근거 |
|------|----------|------|
| **Phase 0 → 1** | P0-1~P0-4 완료, 스키마 정합 확인 — ✅ G0-1/G0-2 통과 (2026-04-04) | SOT2 자체 게이트 |
| **Phase 1 → 2** | Part2 V1-P2 게이트 12항목 전체 통과 — ✅ G1 PASS (2026-04-13, P1-1~P1-11 전체 완료) | Part2 L2054-2071 |
| **Phase 2 → 3** | Qdrant 전환 완료, 승격 자동화 테스트 통과, 마이그레이션 검증 | SOT2 자체 게이트 + Part2 V2 게이트 |

#### Phase 1 단계별 상세 작업 절차

> **게이트 (P1→P2)**: Part2 V1-P2 게이트 12항목 전체 통과
>
> **Issue 전환**: I-1~I-8 SHELL→FULL

---

##### 01_memory-hierarchy

<details>
<summary><b>P1-1. L0 Session Memory CRUD (Part2 항목1)</b></summary>

**대조 기준**:
- §7 세부 작업: P1-1 "L0 Session Memory CRUD"
- §7 전환 게이트: P1→P2: Part2 V1-P2 게이트 12항목 전체 통과
- §6 이슈: I-1 (L0~L3 상세)

**목표**: L0 Session Memory의 CRUD 전 동작을 L3 수준으로 완성한다. TTL(session_end 또는 created_at+30일), project_id 격리, 생성/조회/수정/삭제 API를 포함하며, LOCK-MR-003/017을 준수한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` (LOCK — §2.1 L0 정의: session-scoped, TTL=session_end+30일(LOCK-MR-003), B-4 매핑)
- `D:\VAMOS\docs\sot\D2.1-D6_D6_SCHEMA_STORAGE_MEMORY.md` (D6 MemoryRecordSchema — scope=L0, memory_type=B-4)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` (V1-Phase 2 항목1 — L0 CRUD 구현 요건)
- P0-1 산출물: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\MemoryRecordSchema.md` (확정 스키마 20개 필드)
- P0-2 산출물: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\sqlite_ddl.sql` (SQLite DDL)

**절차**:
1. P0-2 SQLite DDL 기반으로 L0 전용 테이블 접근 레이어 구현 — `scope='L0'` 필터 적용
2. Create: MemoryRecordSchema 필수 7개 필드 검증 후 INSERT — `scope=L0`, `memory_type=B-4`, `ttl` 자동 계산(session_end 또는 created_at+30d 중 min)
3. Read: `record_id` + `project_id` 기준 조회 — LOCK-MR-017(project_id 격리) 가드 적용 (session 전체 조회는 tags의 "session:<id>" 멤버 매칭)
4. Update: `record_id` 기준 content_summary/tags 수정 — `version` 증분으로 추적(P0-2 updated_at 비스키마), scope/memory_type 변경 금지(불변 필드)
5. Delete: soft-delete(activation_state→deprecated) 또는 TTL 만료 시 hard-delete — 정책 선택 문서화
6. TTL 만료 체크 로직 구현 — 주기적 sweep 또는 lazy expiration 전략 결정 및 구현
7. LOCK-MR-018(저장 전 사용자 확인) 훅 포인트 정의 — Create/Update 시 확인 인터페이스 연동
8. 단위 테스트: CRUD 4개 경로 + TTL 만료 + project_id 격리 위반 시 에러

**검증**:
- [x] L0 Create 시 scope=L0, memory_type=B-4 강제 ✅
- [x] TTL 계산이 LOCK-MR-003 준수 (session_end 또는 created_at+30d 중 먼저) ✅
- [x] project_id 없는 요청 거부 (LOCK-MR-017) ✅
- [x] CRUD 4개 경로 단위 테스트 통과 ✅
- [x] LOCK-MR-018 저장 전 사용자 확인 훅 포인트 동작 ✅
- [x] I-1 SHELL→FULL 전환 완료 (L0 영역) ✅

> **완료**: 2026-04-13. L0 Session Memory CRUD 전 동작을 L3 수준으로 완성 — CRUD 4경로, TTL(session_end/30d), project_id 격리, 사용자 확인 훅, 에러 코드 체계 포함.
>
> **실행 결과 요약**:
> - L0 CRUD 사양서 1029줄 작성 (Create/Read/Update/Delete + TTL sweep + 에러 코드 12종)
> - LOCK-MR-003/015/017/018/019 등 7개 LOCK 준수 검증 ALL PASS
> - 단위 테스트 시나리오 T-01~T-23 정의 (CRUD 4경로 + 격리 위반 + TTL 만료 + session 추적)
> - P1-3(Chroma), P1-7(PII 마스킹) 접점 명시, CONFLICT_LOG #006 참조 유지

**[P1-1] 검증 결과 요약** (갱신: 2026-04-13)
- 0. 산출물: 1건 (`L0_session_memory_crud.md`, 1029줄)
- 1. 게이트: 검증 체크리스트 6/6 ALL PASS, LOCK-MR 7건 ALL PASS
- 2. CONFLICT: 0건 (기존 #006 OPEN — SOT 원본 수정 보류, P1-1 신규 없음)
- 3. LOCK 변경: 0건 (LOCK-MR-003/015/017/018/019 무위반)
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\L0_session_memory_crud.md`
</details>

<details>
<summary><b>P1-2. L1 Project Memory CRUD (Part2 항목2)</b></summary>

**대조 기준**:
- §7 세부 작업: P1-2 "L1 Project Memory CRUD"
- §7 전환 게이트: P1→P2: Part2 V1-P2 게이트 12항목 전체 통과
- §6 이슈: I-1 (L0~L3 상세)

**목표**: L1 Project Memory의 CRUD 전 동작을 L3 수준으로 완성한다. TTL=90일, project_id별 완전 격리, 생성/조회/수정/삭제 API를 포함하며, LOCK-MR-004/017을 준수한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` (LOCK — §2.1 L1 정의: project-scoped, TTL=90일(LOCK-MR-004), B-1 매핑)
- `D:\VAMOS\docs\sot\D2.1-D6_D6_SCHEMA_STORAGE_MEMORY.md` (D6 MemoryRecordSchema — scope=L1, memory_type=B-1)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` (V1-Phase 2 항목2 — L1 CRUD 구현 요건)
- P0-1 산출물: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\MemoryRecordSchema.md`
- P0-2 산출물: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\sqlite_ddl.sql`

**절차**:
1. P0-2 SQLite DDL 기반으로 L1 전용 접근 레이어 구현 — `scope='L1'` 필터 적용
2. Create: `scope=L1`, `memory_type=B-1`, `ttl=created_at+90d` 자동 설정 — LOCK-MR-004 준수
3. Read: `project_id` 기준 격리 조회 — 다른 project_id 데이터 접근 원천 차단(LOCK-MR-017)
4. Update: content_summary/tags 수정 허용 — `updated_at` 갱신, TTL 리셋 정책 결정(갱신 시 TTL 연장 여부)
5. Delete: soft-delete 우선, TTL 만료 시 정리 배치 구현
6. project_id 격리 가드 `_enforce_project_filter()` 적용 — P0-3 chroma_collection_strategy.md §4.2 패턴 재사용
7. 단위 테스트: CRUD + TTL 90일 만료 + project_id 교차 접근 차단

**검증**:
- [x] L1 Create 시 scope=L1, memory_type=B-1 강제 — 산출물 §3.1 step 7 ✅
- [x] TTL이 정확히 90일 (LOCK-MR-004) — 산출물 §4.1 ✅
- [x] project_id 교차 접근 시 에러 반환 (LOCK-MR-017) — 산출물 §3.1~3.4, §10.3 ✅
- [x] CRUD + TTL 만료 단위 테스트 통과 — 산출물 §10 T-01~T-28 ✅
- [x] B↔L 매핑 정합성: B-1→L1 확인 (LOCK-MR-002) — 산출물 §2.1, §10.5 T-28 ✅
- [x] I-1 SHELL→FULL 전환 완료 (L1 영역) — 산출물 전체 (L1 CRUD L3 수준 완성) ✅

> **완료**: 2026-04-13. L1 Project Memory CRUD 전 동작을 L3 수준으로 완성 — CRUD 4경로, TTL 90일(연장 시 최대 120일), project_id 격리, 사용자 확인 훅, L0→L1 승격 경로 포함.
>
> **실행 결과 요약**:
> - L1 CRUD 사양서 1건 작성 (Create/Read/Update/Delete + TTL 90d/연장120d + L0→L1 승격)
> - LOCK-MR-001/002/004/015/017/018/019 등 7개 LOCK 준수 검증 ALL PASS
> - 단위 테스트 시나리오 T-01~T-28 정의 (CRUD 4경로 + 격리 위반 + TTL 만료/연장 + L0→L1 승격 + B↔L 매핑)
> - P1-1(L0), P1-3(Chroma), P1-7(PII 마스킹), P1-8(Decay) 접점 명시

**산출물 요약** (2026-04-13, v1.0):
> - L1 Project Memory CRUD (Create/Read/Update/Delete) L3 수준 완성
> - CRUD 4경로 + TTL 90일(LOCK-MR-004, 30일 연장→최대 120일) + project_id 격리(LOCK-MR-017) + 사용자 확인 훅(LOCK-MR-018)
> - L0→L1 승격 경로 정의 (세션 종료 시 자동 요약 → L1 Create, promoted_from 추적)
> - LOCK-MR-001/002/004/015/017/018/019 등 7개 LOCK 준수 검증 ALL PASS
> - 단위 테스트 시나리오 T-01~T-28 정의 (CRUD 4경로 + 격리 위반 + TTL 만료/연장 + L0→L1 승격 + B↔L 매핑)
> - P1-1(L0), P1-3(Chroma), P1-7(PII 마스킹), P1-8(Decay) 접점 명시

**[P1-2] 검증 결과 요약** (갱신: 2026-04-13)
- 0. 산출물: 1건 (`L1_project_memory_crud.md`)
- 1. 게이트: 검증 체크리스트 7/7 ALL PASS, LOCK-MR 7건 ALL PASS
- 2. CONFLICT: 0건 (기존 #001 RESOLVED — STEP7-D L1 vs D2.0-06 L1, D2.0-06 우선 적용 완료)
- 3. LOCK 변경: 0건 (LOCK-MR-001/002/004/015/017/018/019 무위반)
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\L1_project_memory_crud.md`
</details>

<details>
<summary><b>P1-8. B-3 Memory Decay (Part2 항목8)</b></summary>

**대조 기준**:
- §7 세부 작업: P1-8 "B-3 Memory Decay"
- §7 전환 게이트: P1→P2: Part2 V1-P2 게이트 12항목 전체 통과
- §6 이슈: I-5 (승격/강등)

**목표**: B-3 Decay Knowledge의 시간 감쇠 알고리즘을 L3 수준으로 완성한다. last_accessed_at 기반 감쇠 점수 산출, 임계값 이하 레코드 강등/비활성화 정책, I-5 승격/강등 연동을 포함하며, LOCK-MR-002(B-3→L2 매핑)를 준수한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` (LOCK — §2.3 B-Series: B-3=Decay Knowledge→L2 매핑, LOCK-MR-002 B↔L 매핑)
- `D:\VAMOS\docs\sot\D2.1-D6_D6_SCHEMA_STORAGE_MEMORY.md` (D6 MemoryRecordSchema — memory_type=B-3, scope=L2)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` (V1-Phase 2 항목8 — B-3 Decay 구현 요건)
- P0-1 산출물: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\MemoryRecordSchema.md`
- I-5 참조: 승격/강등 알고리즘 상세 → 01_memory-hierarchy

**절차**:
1. B-3 Decay Knowledge 정의 확인 — D2.0-06 §2.3에서 B-3의 의미론적 역할(시간 경과에 따른 감쇠 지식) 파악
2. L2(scope=L2, TTL=무기한, LOCK-MR-005) 레코드 중 B-3 타입 필터링 로직 구현
3. Decay 점수 산출 알고리즘 설계 — 최종 접근 시각(last_accessed_at) 기반 감쇠 함수(지수 감쇠 또는 선형)
4. Decay 임계값 이하 레코드 처리 정책 정의 — 강등(L2→L1 또는 L0) vs 비활성화(activation_state→deprecated) vs 삭제
5. I-5(승격/강등 알고리즘) 연동 포인트 설계 — Decay 결과가 강등 트리거로 작동하는 인터페이스
6. 배치/스케줄러 설계 — Decay 점수 재계산 주기 및 실행 방식
7. 단위 테스트: Decay 점수 계산 정확도 + 임계값 처리 + B↔L 매핑 정합

**검증**:
- [x] B-3 레코드가 반드시 scope=L2에 매핑 (LOCK-MR-002) — 산출물 §1.1, §5.5, T-DEC-17
- [x] Decay 알고리즘이 last_accessed_at 기반으로 동작 — 산출물 §3.1 compute_decay_score()
- [x] 임계값 이하 레코드 처리 정책 문서화 — 산출물 §4 (3-Tier: ACTIVE/REVIEW/DEMOTE_CANDIDATE)
- [x] I-5 승격/강등 알고리즘과의 연동 인터페이스 정의 — 산출물 §5.2 DecayEvaluation→DemotionAction
- [x] 배치 스케줄러 Decay 재계산 주기 정의 및 동작 확인 — 산출물 §6.1 주간 배치, §6.2 run_decay_batch()

**세션 종료 기록** (P1-8, 2026-04-13):
> **완료**: B-3 Memory Decay L3 수준 완성 — 지수 감쇠 알고리즘(half_life=30d, S7D-005 정합)+3-Tier 임계값(ACTIVE≥0.3/REVIEW≥0.1/DEMOTE<0.1)+운영 메타 5필드 DDL 확장(last_accessed_at/access_count/pinned/decay_score/last_decay_evaluated_at)+비활성화(deprecated)/강등(L2→L1)/복원 정책(LOCK-MR-005 무삭제 원칙)+I-5 강등 트리거 인터페이스(DecayEvaluation→DemotionAction, P2-4 연동)+주간 배치 스케줄러(100건/300초)+에러 4종+에스컬레이션+config.toml `[memory.decay]` 8파라미터+단위 테스트 T-DEC-01~32(32건)+Phase 2 통합 테스트 12건. 재검증 0회/이슈 0건.

**산출물 요약** (2026-04-13, v1.0):
> - B-3 Decay Knowledge 지수 감쇠 알고리즘 (에빙하우스 망각 곡선 모델, half_life=30d 기본)
> - 3-Tier 임계값 처리: ACTIVE(≥0.3) / REVIEW(≥0.1) / DEMOTE_CANDIDATE(<0.1)
> - LOCK-MR-002(B-3→L2) 정합 + LOCK-MR-005(무기한 보존) 준수 — 시간 기반 자동 삭제 없음
> - 비활성화(deprecated), L2→L1 강등, 복원 3경로 정의 + 사용자 확인 필수(LOCK-MR-018)
> - I-5 강등 트리거 인터페이스: DecayEvaluation / DemotionAction 데이터 클래스 + 시퀀스 다이어그램
> - 운영 메타 5필드 DDL 확장 + 부분 인덱스(idx_decay_candidates)
> - 주간 배치 스케줄러: 100건 단위, 300초 타임아웃, 에러 4종+에스컬레이션
> - 단위 테스트 T-DEC-01~32 (32건), Phase 2 통합 테스트 12건
> - P1-1(L0), P1-2(L1), P1-3(Chroma), P1-4(GraphRAG), P1-5(Cache), P1-6(Export), P1-7(PII), P1-9(DCL) 접점 명시

**[P1-8] 검증 결과 요약** (갱신: 2026-04-13)
- 0. 산출물: 1건 (`B3_memory_decay.md`, v1.1)
- 1. 게이트: 검증 체크리스트 5/5 ALL PASS, LOCK-MR-002/005/017/018 무위반
- 2. CONFLICT: 0건 (P1-8 신규 없음)
- 3. LOCK 변경: 0건 (LOCK-MR-002/005/017/018 무위반)
- 4. 이월: 없음
- 재검증 (step2): 1회/이슈 6건 수정 — (1) §6.4 EscalationPayload 표준 필드 보강(P1-4/P1-5/P1-6 정합), (2) §6.5 에스컬레이션 레벨 매트릭스 추가, (3) §8.2 로깅 R-01-7 중첩 JSON 구조 보강(entity_id/lock_checks, P1-4 §12 정합), (4) §8.3 개별 레코드 Decay 평가 로그 추가, (5) §9 시간복잡도 분석 신설(Big-O), (6) §10~17 섹션 번호 재정렬

**산출물**: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\B3_memory_decay.md`
</details>

---

##### 02_rag-pipeline

<details>
<summary><b>P1-4. JSON GraphRAG (Part2 항목4)</b></summary>

**대조 기준**:
- §7 세부 작업: P1-4 "JSON GraphRAG"
- §7 전환 게이트: P1→P2: Part2 V1-P2 게이트 12항목 전체 통과
- §6 이슈: I-8 (GraphRAG 상세)

**목표**: JSON 파일 기반 GraphRAG의 노드/엣지 CRUD 및 그래프 탐색 쿼리를 L3 수준으로 완성한다. D6 GraphRAGConfigSchema 전수 반영, project_id 격리(LOCK-MR-017), I-8 SHELL→FULL 전환을 포함한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` (GraphRAG 관련 설계 — §2.4 이상)
- `D:\VAMOS\docs\sot\D2.1-D6_D6_SCHEMA_STORAGE_MEMORY.md` (D6 GraphRAGConfigSchema)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` (V1-Phase 2 항목4 — JSON GraphRAG 요건)
- STEP7-D: `D:\VAMOS\docs\sot\STEP7-D_메모리_저장소_아키텍처_작업가이드.md` (GraphRAG 체크리스트 항목)
- I-8 참조: GraphRAG 상세 → 02_rag-pipeline

**절차**:
1. D6 GraphRAGConfigSchema 필드 확인 — 노드/엣지 타입, 관계 정의, 설정 파라미터
2. JSON 기반 그래프 저장소 설계 — V1에서는 전용 GraphDB 없이 JSON 파일로 노드/엣지 관리
3. 노드 CRUD 구현 — MemoryRecord를 노드로 변환, memory_id를 노드 ID로 매핑
4. 엣지(관계) CRUD 구현 — 레코드 간 관계(references, derived_from, supersedes 등) 정의
5. 그래프 탐색 쿼리 구현 — 단일 홉/다중 홉 탐색, project_id 격리(LOCK-MR-017) 적용
6. I-8(GraphRAG 상세) SHELL→FULL 전환 — 상세 파라미터, 인덱싱 전략 문서화
7. 단위 테스트: 노드/엣지 CRUD + 탐색 쿼리 + project_id 격리

**검증**:
- [x] D6 GraphRAGConfigSchema 필드 전수 반영 — 산출물 §1 (8필드 전수 매핑, AC-D6-009 scope=P1-SCOPE)
- [x] JSON 파일 기반 노드/엣지 저장 구현 — 산출물 §4 (프로젝트별 디렉터리 분리, atomic write, .bak 백업)
- [x] 그래프 탐색 시 project_id 격리 적용 — 산출물 §9 (파일/API/데이터 3중 격리, 크로스 프로젝트 엣지 차단)
- [x] I-8 SHELL→FULL 전환 완료 — 산출물 §17 (노드 10종/엣지 10종, CRUD 8연산, BFS 탐색, 25건 테스트)
- [x] 단일 홉/다중 홉 탐색 쿼리 단위 테스트 통과 — 산출물 §15 T-G-008/T-G-009/T-G-010/T-G-011

**산출물 재검증** (2026-04-13, 4건 수정 → v1.1):
- [x] D6 GraphRAGConfigSchema 8필드 전수 확인 (config_id, graph_backend, entity_extraction_model, max_hops, community_detection, embedding_model, scope, version_tier)
- [x] LOCK-MR-017 project_id 격리 3중 레벨 확인 (파일 레벨 분리 + API 레벨 필수 파라미터 + 데이터 레벨 내장 필드)
- [x] S7D-019 V1 경량 KG (NetworkX + JSON) FULL 반영, S7D-020 KG 스키마 FULL 반영
- [x] BaseGraphStore ABC 11메서드 (add/get/update/delete × node/edge + traverse + get_subgraph + search_nodes)
- [x] 예외 12종 정의, 복구/재시도 흐름도, 에스컬레이션 페이로드 포함
- [x] **[심화 재검증]** B-Series 레이블 교정: B-2=Procedural(not Declarative), B-3=Semantic(not Procedural), B-4=Working(not Strategic) — §3.5 표+§6.2 TYPE_MAP 동시 수정
- [x] **[심화 재검증]** EscalationPayload §11.1 스키마와 _escalate() 구현 정합성 확보 — escalation_id, timestamp, category, operation, error_type, recommended_action, auto_resolved 필드 추가
- [x] **[심화 재검증]** 로깅 §12.1 중첩 JSON 규격과 _log_operation() 정합성 확보 — log_id, timestamp, level, duration_ms, lock_checks 필드 추가
- [x] **[심화 재검증]** edges.json 복구 경로에 누락된 _escalate 호출 추가 (nodes.json과 동일 패턴)

**산출물 요약**: 노드 10종(Part2 5종 + S7D-020 5종), 엣지 10종(S7D-020 5종 + P1-4 5종), D6 8필드, ABC 11메서드, BFS 탐색(max_hops=2), JSON atomic 영속, 에러 12종, 테스트 25건. V2 Neo4j 전환 인터페이스(ABC) 준비 완료.

> **완료**: 2026-04-13. JsonGraphStore L3 수준 완성 — D6 GraphRAGConfigSchema 8필드 전수 반영, 노드 10종/엣지 10종 CRUD, BFS 탐색(1~2홉), project_id 3중 격리, JSON atomic 영속(write+backup), ABC 어댑터 패턴, I-8 SHELL→FULL 전환. 재검증 1회 v1.1(B-Series 레이블 3건+EscalationPayload/로깅 정합 1건 수정).
>
> **실행 결과 요약**:
> - JsonGraphStore 구현 상세 1건 작성 (노드 10종/엣지 10종 CRUD + BFS 탐색 + ABC 11메서드)
> - D6 GraphRAGConfigSchema 8필드 전수 매핑 (config_id, graph_backend, entity_extraction_model, max_hops, community_detection, embedding_model, scope, version_tier)
> - LOCK-MR-017 project_id 격리 3중 레벨 검증 (파일/API/데이터)
> - S7D-019 V1 경량 KG(NetworkX+JSON) FULL, S7D-020 KG 스키마 FULL 반영
> - 예외 12종 정의, 복구/재시도 흐름도, 에스컬레이션 페이로드 포함
> - 단위 테스트 시나리오 25건 정의
> - 심화 재검증 4건 수정 (B-Series 레이블 3건, EscalationPayload+로깅 정합 1건)

**[P1-4] 검증 결과 요약** (갱신: 2026-04-13)
- 0. 산출물: 1건 (`json_graphrag.md`, v1.1)
- 1. 게이트: 검증 체크리스트 5/5 ALL PASS, 재검증 9/9 ALL PASS, LOCK-MR-017 무위반
- 2. CONFLICT: 0건 (P1-4 신규 없음)
- 3. LOCK 변경: 0건 (LOCK-MR-017 무위반)
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\02_rag-pipeline\json_graphrag.md`
</details>

<details>
<summary><b>P1-9. DCL 기초 구현 (Part2 항목9)</b></summary>

**대조 기준**:
- §7 세부 작업: P1-9 "DCL 기초 구현"
- §7 전환 게이트: P1→P2: Part2 V1-P2 게이트 12항목 전체 통과
- §6 이슈: —

**목표**: Data Control Layer(DCL)의 Allow/Restrict/Deny 3단계 정책 판정 인터페이스를 완성한다. LOCK-MR-015(Deny 시 벡터 삽입 금지), LOCK-MR-016(L3 ApprovalGate 필수), LOCK-MR-018(저장 전 사용자 확인)과의 연동 경로를 포함한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` (DCL 관련 설계 참조)
- `D:\VAMOS\docs\sot\D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` (DCL 정책 — Allow/Restrict/Deny 판정, ApprovalGate)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` (V1-Phase 2 항목9 — DCL 기초 요건)
- STEP7-D: `D:\VAMOS\docs\sot\STEP7-D_메모리_저장소_아키텍처_작업가이드.md`

**절차**:
1. DCL(Data Control Layer) 역할 정의 — 메모리 저장/조회 시 정책 판정을 중재하는 계층
2. D2.0-07 정책 판정 로직 확인 — Allow(정상 진행)/Restrict(마스킹 후 진행)/Deny(차단) 3단계
3. DCL 인터페이스 설계 — `check_policy(memory_record) → PolicyDecision` 시그니처
4. LOCK-MR-015 연동: Deny 판정 시 벡터 삽입 절대 금지 경로 구현
5. LOCK-MR-018 연동: 저장 전 사용자 확인 훅 포인트 통합
6. LOCK-MR-016 연동: L3 레코드는 ApprovalGate 필수 경로 정의
7. 단위 테스트: Allow/Restrict/Deny 3개 경로 + L3 ApprovalGate 필수

**검증**:
- [x] DCL 인터페이스가 3단계 정책 판정 반환 — 산출물 §2 PolicyDecision enum + §4 check_policy() ✅
- [x] Deny 시 벡터 삽입 차단 경로 동작 (LOCK-MR-015) — 산출물 §7 Deny 경로 + §8 이중 안전장치 ✅
- [x] L3 레코드 ApprovalGate 필수 (LOCK-MR-016) — 산출물 §9 L3 ApprovalGate 흐름 + §9.2 접근 제어 ✅
- [x] 저장 전 확인 훅 동작 (LOCK-MR-018) — 산출물 §10 UserConfirmationHook 통합 + §10.3 자동 확인 예외 ✅
- [x] Allow/Restrict/Deny 3개 경로 단위 테스트 통과 — 산출물 §18 T-DCL-01~32 (32건) ✅

> **완료**: 2026-04-13. DataControlLayer L3 수준 완성 — Allow/Restrict/Deny 3단계 정책 판정 인터페이스 완성.
>
> **산출물 요약** (2026-04-13, v1.0):
> - DCL(Data Control Layer) check_policy() 핵심 인터페이스 — D7 PolicyCheck 5-Gate 연동 + PII 교차 판정 + L3 ApprovalGate
> - LOCK-MR-015 (Deny 벡터 삽입 금지) 이중 안전장치: DCL 판정 + MemoryRecord 필드 양쪽 검증
> - LOCK-MR-016 (L3 활성 게이트) draft/approved/active 3단계 전환 경로 + D7 ApprovalGate 필수
> - LOCK-MR-018 (저장 전 사용자 확인) P1-1 §5.2 UserConfirmationHook 재사용 + 자동 확인 예외 4건
> - DCL-FIN(RT-BNP RSS)/DCL-TECH(RSS 1시간 폴링) 수집기 정책 판정 경로 정의 (Part2 게이트 11 충족)
> - P1-1(L0), P1-2(L1), P1-3(Chroma), P1-4(GraphRAG), P1-5(Cache), P1-6(Export), P1-7(PII), P1-8(Decay) 접점 명시
> - 에러 12종, 복구/재시도, 에스컬레이션 5종, 로깅 R-01-7 10 이벤트, Big-O 분석
> - 단위 테스트 T-DCL-01~32 (32건), Phase 2 통합 테스트 12건

**[P1-9] 검증 결과 요약** (갱신: 2026-04-13)
- 0. 산출물: 1건 (`dcl_basic.md`, v1.1)
- 1. 게이트: 검증 체크리스트 5/5 ALL PASS, LOCK-MR-015/016/017/018 무위반
- 2. CONFLICT: 0건 (P1-9 신규 없음)
- 3. LOCK 변경: 0건 (LOCK-MR-015/016/017/018/019 무위반)
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\02_rag-pipeline\dcl_basic.md`
</details>

<details>
<summary><b>P1-10. 6-Stage RAG Pipeline 통합 (Part2 게이트6)</b></summary>

**대조 기준**:
- §7 세부 작업: P1-10 "6-Stage RAG Pipeline 통합"
- §7 전환 게이트: P1→P2: Part2 V1-P2 게이트 12항목 전체 통과
- §6 이슈: I-2 (RAG 파라미터)

**목표**: 6-Stage RAG Pipeline(Query→Retrieve→Rerank→Augment→Generate→Evaluate)의 각 단계 입출력/에러/메트릭을 L3 수준으로 완성한다. LOCK-MR-007을 준수하며, Hybrid Search와의 통합 접점을 명시한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` (LOCK — §2.4 6-Stage RAG Pipeline: Query→Retrieve→Rerank→Augment→Generate→Evaluate, LOCK-MR-007)
- `D:\VAMOS\docs\sot\D2.1-D6_D6_SCHEMA_STORAGE_MEMORY.md` (D6 RAG 관련 스키마)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` (V1-Phase 2 게이트6 — 6단계 파이프라인 통합 요건)
- STEP7-D: `D:\VAMOS\docs\sot\STEP7-D_메모리_저장소_아키텍처_작업가이드.md`
- I-2 참조: RAG 6단계 파라미터 → 02_rag-pipeline

**절차**:
1. 6단계 파이프라인 아키텍처 설계 — 각 Stage를 독립 컴포넌트로 정의, 입출력 인터페이스 규격화
2. Stage 1 (Query): 사용자 쿼리 전처리 — 임베딩 변환, 쿼리 확장/재작성
3. Stage 2 (Retrieve): VectorStore 어댑터(P0-4) 호출 — top_k 후보 검색, project_id 격리
4. Stage 3 (Rerank): 후보 재순위화 — 의미론적 유사도 + 메타데이터 기반 점수 조합
5. Stage 4 (Augment): 컨텍스트 조립 — 검색 결과 + 그래프 관계(P1-4) 통합
6. Stage 5 (Generate): LLM 호출을 위한 프롬프트 조립 — 메모리 컨텍스트 주입
7. Stage 6 (Evaluate): 응답 품질 평가 — QoD 점수 산출, 피드백 루프
8. I-2(RAG 6단계 파라미터) SHELL→FULL 전환 — 각 Stage별 상세 파라미터 확정

**검증**:
- [x] 6단계 순서 정확히 Collect→Chunk→Embed→Store→Retrieve→Generate (LOCK-MR-007) — 산출물 §2~§8. Query→Retrieve→Rerank→Augment→Generate→Evaluate는 Stage 5~6 내부 런타임 서브 파이프라인으로 §9에 매핑 기록
- [x] 각 Stage 독립 컴포넌트로 분리, 입출력 인터페이스 정의 — 산출물 §3~§8 각 Stage별 Input/Output 데이터클래스
- [x] VectorStore 어댑터(P0-4 산출물) 연동 — 산출물 §6.4 4메서드 연동 (LOCK-MR-014)
- [x] I-2 SHELL→FULL 전환 완료 — 산출물 §11 (10/10 항목 FULL)
- [x] Hybrid Search(P1-11)와의 Stage 2/3 통합 접점 명시 — 산출물 §7.3 HybridSearcher 인터페이스
- [x] 각 Stage 에러 핸들링 및 메트릭 수집 포인트 정의 — 산출물 §12 에러 21종 + §18 메트릭 14종

> **완료**: 2026-04-13. 6-Stage RAG Pipeline L3 수준 완성 — 6 Stage 입출력 인터페이스(6 Input/Output 데이터클래스), Query-Time Sub-Pipeline 매핑(§9), 에러 21종(RAG_ERR_001~021), 복구/재시도 전략, 에스컬레이션 3레벨, 로깅 R-01-7, Big-O 분석, 메트릭 14종, I-2 SHELL→FULL 10/10.
>
> **실행 결과 요약**:
> - 산출물 1건 (`rag_6stage_pipeline.md`, v1.0) — 24섹션 L3 상세
> - LOCK-MR-007(6-Stage 순서) + 008(α=0.7) + 009(threshold=0.75) + 010/011/012/014/015/017/019 등 10개 LOCK 준수 ALL PASS
> - 6 Stage별 독립 입출력 인터페이스: CollectInput/Output, ChunkInput/Output, EmbedInput/Output, StoreInput/Output, RetrieveInput/Output, GenerateInput/Output
> - Query-Time Sub-Pipeline (Query→Retrieve→Rerank→Augment→Generate→Evaluate) → LOCK-MR-007 Stage 5~6 내부 매핑 명시 (§9)
> - 에러 코드 RAG_ERR_001~021 (21종) 정의, 복구/재시도 전략 11개, 에스컬레이션 3레벨
> - 단위 테스트 T-RAG-01~25 (25건) + Phase 2 통합 테스트 P2-T-RAG-01~12 (12건)
> - 메트릭 수집 포인트 MET-RAG-001~014 (14종)
> - I-2 SHELL→FULL 전환 10/10 완료
> - 세션 간 cross-check: P0-1/P0-3/P0-4/P1-1/P1-2/P1-3/P1-4/P1-5/P1-7/P1-9/P1-11 접점 명시 (§22)

**[P1-10] 검증 결과 요약** (갱신: 2026-04-13, Step 4 완료)
- 0. 산출물: 1건 (`rag_6stage_pipeline.md`, v1.0 → v1.1 교정)
- 1. 게이트: 검증 체크리스트 6/6 ALL PASS, LOCK-MR 10건 ALL PASS
- 2. CONFLICT: 0건 (기존 #006 SOT 대기 — P1-10 영향 없음)
- 3. LOCK 변경: 0건 (LOCK-MR-007/008/009/010/011/012/014/015/017/019 무위반)
- 4. 이월: 없음 (Step 2 교정 5건 반영 완료: §3.5 PII mask_text→mask, §7.3 Cache lookup→get, §7.3 GraphRAG query_subgraph→traverse, §8.3 Cache store→put, §22 cross-check 3건)

**산출물**: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\02_rag-pipeline\rag_6stage_pipeline.md`
</details>

<details>
<summary><b>P1-11. Hybrid Search 통합 (Part2 게이트7)</b></summary>

**대조 기준**:
- §7 세부 작업: P1-11 "Hybrid Search 통합"
- §7 전환 게이트: P1→P2: Part2 V1-P2 게이트 12항목 전체 통과
- §6 이슈: I-2 (RAG 파라미터)

**목표**: Hybrid Search(Semantic+Keyword)의 점수 결합 및 임계값 필터링을 L3 수준으로 완성한다. α=0.7(LOCK-MR-008), threshold=0.75(LOCK-MR-009)를 준수하며, P1-10 6-Stage RAG Pipeline Stage 2/3과의 통합 접점을 포함한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` (LOCK — Hybrid Search: α=0.7(LOCK-MR-008), threshold=0.75(LOCK-MR-009))
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` (V1-Phase 2 게이트7 — Hybrid Search 통합 요건)
- P0-3 산출물: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\03_vector-db\chroma_collection_strategy.md` (§5.1: α=0.7, threshold=0.75 전략)
- P0-4 산출물: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\03_vector-db\vectorstore_abc.py` (VectorStore 어댑터 ABC)

**절차**:
1. Hybrid Search 구조 설계 — Semantic(벡터 유사도) + Keyword(BM25 등) 결합, α=0.7 가중치(LOCK-MR-008)
2. Semantic Search 구현 — VectorStore 어댑터(P0-4) search() 활용, 코사인 유사도 기반
3. Keyword Search 구현 — BM25 또는 SQLite FTS 기반 키워드 매칭
4. 점수 결합: `final_score = α × semantic_score + (1-α) × keyword_score` — α=0.7 고정(LOCK-MR-008)
5. Threshold 필터링 — final_score < 0.75인 결과 제거 (LOCK-MR-009)
6. P1-10 6-Stage RAG Pipeline의 Stage 2(Retrieve) + Stage 3(Rerank)에 Hybrid Search 통합
7. 단위 테스트: α 가중치 정확성 + threshold 필터링 + 결합 점수 순위 정확성

**검증**:
- [x] α=0.7 가중치 적용 확인 (LOCK-MR-008) — 산출물 §3 HybridSearchConfig.alpha=0.7 LOCK 강제, §8 가중 합산 공식, §11 LOCK 검증+자동 복원
- [x] threshold=0.75 필터링 동작 (LOCK-MR-009) — 산출물 §3 HybridSearchConfig.threshold=0.75 LOCK 강제, §9 _apply_threshold, §11 search() 내 적용
- [x] Semantic + Keyword 결합 점수 산출 정확 — 산출물 §8 가중 합산 알고리즘(α*dense + (1-α)*sparse), §10 RRF 대체 전략, §7 Min-Max 정규화
- [x] P1-10 RAG Pipeline Stage 2/3 통합 — 산출물 §12 P1-10 §7.3 HybridSearcher.search() 시그니처 일치 확인, Stage 2(Chunk→BM25) + Stage 3(Embed→query_vector) 통합 접점 명시
- [x] BM25(1-α=0.3) 키워드 검색 동작 확인 — 산출물 §6 BM25IndexManager.search() 호출, P1-3 §8 BM25Okapi 연동

> **완료**: 2026-04-13. Hybrid Search L3 수준 완성 — Dense(ChromaVectorStore)+Sparse(BM25) 결합, 가중 합산(α=0.7 LOCK)+RRF 대체, Min-Max 정규화, threshold=0.75 필터링(LOCK), P1-10 Stage 5 HybridSearcher 인터페이스 구현, Graceful Degradation.
>
> **실행 결과 요약**:
> - Hybrid Search 통합 상세 1건 작성 (HybridSearcher 클래스 FULL 구현 + HybridSearchConfig + HybridCandidate + HybridSearchResult)
> - LOCK-MR-008(α=0.7)/009(threshold=0.75)/011/012/014/015/017/019 등 8개 LOCK 준수 검증 ALL PASS
> - 단위 테스트 시나리오 T-HYB-01~T-HYB-25 정의 (α 가중치 검증 + threshold 경계 + 정규화 + RRF + Graceful Degradation + project_id 격리)
> - Phase 2 통합 테스트 P2-T-HYB-01~P2-T-HYB-12 정의 (RAG E2E + Semantic Cache 바이패스 + Dense+Sparse 통합 + Rerank + PII + GraphRAG + DCL)
> - 에러 코드 HYB_ERR_001~010 (10종) 정의, 복구/재시도 전략 + 에스컬레이션 3레벨
> - 메트릭 수집 포인트 MET-HYB-001~012 (12종)
> - Graceful Degradation 3단계 정의 (Dense+Sparse → Dense-only → 빈 결과+에스컬레이션)
> - 세션 간 cross-check: P0-3/P0-4/P1-1/P1-2/P1-3/P1-4/P1-5/P1-7/P1-9/P1-10 접점 명시 (§21)

**[P1-11] 검증 결과 요약** (갱신: 2026-04-13, Step 4 완료)
- 0. 산출물: 1건 (`hybrid_search.md`, v1.0)
- 1. 게이트: 검증 체크리스트 5/5 ALL PASS, LOCK-MR 8건 ALL PASS
- 2. CONFLICT: 0건 (기존 #006 SOT 대기 — P1-11 영향 없음)
- 3. LOCK 변경: 0건 (LOCK-MR-008/009/011/012/014/015/017/019 무위반)
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\02_rag-pipeline\hybrid_search.md`
</details>

---

##### 03_vector-db

<details>
<summary><b>P1-3. Chroma Vector DB 연동 (Part2 항목3)</b></summary>

**대조 기준**:
- §7 세부 작업: P1-3 "Chroma Vector DB 연동"
- §7 전환 게이트: P1→P2: Part2 V1-P2 게이트 12항목 전체 통과
- §6 이슈: I-3 (VectorStore 어댑터)

**목표**: ChromaVectorStore 어댑터의 4메서드(add/search/delete/get) 구체 구현을 L3 수준으로 완성한다. BGE-M3 1024dim(LOCK-MR-011), V1 Chroma 백엔드(LOCK-MR-012), policy_decision=deny 시 삽입 거부(LOCK-MR-015)를 준수하며, I-3 SHELL→FULL 전환을 포함한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` (LOCK — LOCK-MR-011 BGE-M3 1024dim, LOCK-MR-012 V1=Chroma)
- `D:\VAMOS\docs\sot\D2.1-D6_D6_SCHEMA_STORAGE_MEMORY.md` (D6 VectorStoreAdapterSchema, KB_EMBEDDING_RECORD)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` (V1-Phase 2 항목3 — Chroma 연동 요건)
- P0-3 산출물: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\03_vector-db\chroma_collection_strategy.md` (단일 컬렉션+메타데이터 필터 전략)
- P0-4 산출물: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\03_vector-db\vectorstore_abc.py` (VectorStore ABC — 4메서드: add/search/delete/get)
- I-3 참조: VectorStore 어댑터 구현 → 03_vector-db

**절차**:
1. ChromaVectorStore 클래스 구현 — P0-4 ABC(VectorStoreAdapter) 상속, 4메서드(add/search/delete/get) 구체 구현
2. Chroma 클라이언트 초기화 — 컬렉션 생성/접속, P0-3 단일 컬렉션 전략 적용
3. BGE-M3 임베딩 모델 연동 — 1024차원 벡터 생성(LOCK-MR-011), 임베딩 파이프라인 구성
4. add() 구현: MemoryRecord → 임베딩 벡터 변환 → Chroma upsert — policy_decision=deny 시 삽입 거부(LOCK-MR-015)
5. search() 구현: 쿼리 임베딩 → Chroma query → VectorRecord 반환 — project_id 메타데이터 필터(LOCK-MR-017)
6. delete()/get() 구현 — project_id 격리 가드 적용
7. I-3(VectorStore 어댑터 구현) SHELL→FULL 전환
8. 통합 테스트: Chroma 연동 CRUD + BGE-M3 임베딩 차원 검증 + project_id 격리

**검증**:
- [x] ChromaVectorStore가 ABC 4메서드 모두 구현 (LOCK-MR-014) — 산출물 §4~§7
- [x] BGE-M3 임베딩 1024dim 원본 + Matryoshka 256dim 검색용 확인 (LOCK-MR-011) — 산출물 §3
- [x] V1에서 Chroma 백엔드 사용 (LOCK-MR-012) — 산출물 §2 PersistentClient, backend="chroma", mode="embedded"
- [x] policy_decision=deny 시 upsert() 거부 (LOCK-MR-015) — 산출물 §4.1 Step 1, §4.2
- [x] I-3 SHELL→FULL 전환 완료 — 산출물 §18 (10/10 항목)

> **완료**: 2026-04-13. ChromaVectorStore L3 수준 완성 — 4메서드(upsert/search/delete/get_by_id) FULL 구현, BGE-M3 256dim 검색용, BM25 동기화, R-64-5 용량 검사, 에러 12종, 복구/재시도, I-3 SHELL→FULL.
>
> **실행 결과 요약**:
> - ChromaVectorStore 구현 상세 1건 작성 (4메서드 FULL 구현 + BGEm3Embedder + BM25IndexManager)
> - LOCK-MR-011/012/014/015/017/008/009/019 등 8개 LOCK 준수 검증 ALL PASS
> - 단위 테스트 시나리오 T-01~T-25 정의 (upsert CRUD + deny 차단 + 차원 검증 + 용량 한계 + BM25 동기화)
> - Phase 2 통합 테스트 P2-T-01~P2-T-12 정의 (L0/L1 연동 + Hybrid Search + RAG Pipeline + Semantic Cache)
> - 에러 코드 VEC_ERR_001~012 (12종) 정의, 복구/재시도 전략 + 에스컬레이션 페이로드
> - I-3 SHELL→FULL 전환 10/10 완료
> - P1-1(L0), P1-2(L1), P1-5(Semantic Cache), P1-7(PII 마스킹), P1-10(RAG Pipeline), P1-11(Hybrid Search) 접점 명시

**[P1-3] 검증 결과 요약** (갱신: 2026-04-13)
- 0. 산출물: 1건 (`chroma_adapter.md`)
- 1. 게이트: 검증 체크리스트 5/5 ALL PASS, LOCK-MR 8건 ALL PASS
- 2. CONFLICT: 0건 (기존 #006 SOT 대기 — P1-3 영향 없음)
- 3. LOCK 변경: 0건 (LOCK-MR-011/012/014/015/017/008/009/019 무위반)
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\03_vector-db\chroma_adapter.md`
</details>

---

##### 04_memory-distillation

<details>
<summary><b>P1-5. Semantic Cache (Part2 항목5)</b></summary>

**대조 기준**:
- §7 세부 작업: P1-5 "Semantic Cache"
- §7 전환 게이트: P1→P2: Part2 V1-P2 게이트 12항목 전체 통과
- §6 이슈: I-4 (Cache 무효화)

**목표**: Semantic Cache의 히트/미스 판정, 무효화 전략, 크기 관리를 L3 수준으로 완성한다. cosine>=0.95 히트 판정(LOCK-MR-010)을 준수하며, I-4(Cache 무효화) SHELL→FULL 전환을 포함한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` (LOCK — LOCK-MR-010 Semantic Cache cosine≥0.95)
- `D:\VAMOS\docs\sot\D2.1-D6_D6_SCHEMA_STORAGE_MEMORY.md` (D6 SemanticCacheSchema)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` (V1-Phase 2 항목5 — Semantic Cache 요건)
- I-4 참조: Semantic Cache 무효화 → 04_memory-distillation

**절차**:
1. SemanticCache 클래스 설계 — D6 SemanticCacheSchema 기반 필드 구성
2. 캐시 키 생성: 쿼리 임베딩 벡터 산출 → 기존 캐시 엔트리와 코사인 유사도 비교
3. 캐시 히트 판정: cosine≥0.95이면 캐시 히트 → 저장된 응답 반환 (LOCK-MR-010)
4. 캐시 미스 처리: RAG Pipeline 정상 실행 → 결과를 캐시에 저장
5. 캐시 무효화 전략 설계 — I-4(Semantic Cache 무효화) 상세: TTL 기반 / 소스 변경 감지 / 수동 무효화
6. 캐시 크기 관리 — LRU 또는 용량 제한 정책
7. 단위 테스트: 캐시 히트(cosine≥0.95) + 캐시 미스(cosine<0.95) + 무효화

**검증**:
- [x] cosine>=0.95 히트 판정 정확 (LOCK-MR-010)
- [x] cosine<0.95 시 캐시 미스 → RAG 실행
- [x] 캐시 무효화 전략 문서화 (I-4 SHELL→FULL)
- [x] 캐시 크기 관리 정책 정의
- [x] TTL=24시간, max_entries=1000 설정 준수

> **실행 결과** (P1-5, 2026-04-13):
> - SemanticCache 클래스 설계 완료 — D6 SemanticCacheSchema 8필드 전수 매핑 + 구현 확장 7필드
> - 캐시 히트/미스 판정: cosine >= 0.95 (LOCK-MR-010) 경계값 포함, hash 정확 일치 빠른 경로 추가
> - 무효화 전략 5종 상세 구현: TTL(24h/6h) + 소스 변경 연동 + Embedding Drift(>0.05) + QoD(<0.4) + 수동(4메서드)
> - 캐시 크기 관리: LRU eviction, max_entries=1000, V1 인메모리
> - project_id 격리 (LOCK-MR-017), Deny 차단 (LOCK-MR-015)
> - 에러 코드 12종, 복구/재시도 전략, 에스컬레이션 페이로드, 로깅 R-01-7
> - 단위 테스트 20건 + Phase 2 통합 테스트 12건
> - 세션 간 cross-check: P1-1/P1-2/P1-3/P1-4/P1-7/P1-10/P1-11 접점 명시
> - I-4 SHELL→FULL 전환 완료 (무효화 3정책명 → 5종 상세 + 이벤트 기록 + 사유 추적)

**[P1-5] 검증 결과 요약** (갱신: 2026-04-13)
- 0. 산출물: 1건 (`semantic_cache.md`, v1.1)
- 1. 게이트: 검증 체크리스트 5/5 ALL PASS, LOCK-MR-010/015/017 무위반
- 2. CONFLICT: 0건 (P1-5 신규 없음)
- 3. LOCK 변경: 0건 (LOCK-MR-010/015/017 무위반)
- 4. 이월: 없음
- 재검증 (step2): 1회/이슈 4건 수정 — (1) ConfigValidationError→CacheConfigError 표기 통일, (2) §4.1 hash 탐색 O(1)→O(N) 정정, (3) §18.4 P1-4 이벤트 발행 미래 구현 명시, (4) §12.1 EscalationPayload error_code 필드 추가

**산출물**: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\04_memory-distillation\semantic_cache.md`
</details>

<details>
<summary><b>P1-6. 대화 내보내기/가져오기 (Part2 항목6)</b> ✅</summary>

**대조 기준**:
- §7 세부 작업: P1-6 "대화 내보내기/가져오기"
- §7 전환 게이트: P1→P2: Part2 V1-P2 게이트 12항목 전체 통과
- §6 이슈: —

**목표**: 대화 메모리의 내보내기(Export)/가져오기(Import) 왕복 무손실 파이프라인을 완성한다. MemoryRecordSchema 전체 필드 포함, project_id 격리(LOCK-MR-017 간접), PII 마스킹 상태 확인(P1-7 연동)을 포함한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` (메모리 이식성 관련 설계)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` (V1-Phase 2 항목6 — 내보내기/가져오기 요건)
- P0-1 산출물: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\MemoryRecordSchema.md` (내보내기 대상 스키마)

**절차**:
1. 내보내기 대상 범위 정의 — L0(세션)/L1(프로젝트) 단위 선택, L2/L3는 별도 승인 필요(LOCK-MR-016 참조)
2. 내보내기 포맷 설계 — JSON Lines(.jsonl) 또는 구조화 JSON, MemoryRecordSchema 전체 필드 포함
3. Export 함수 구현 — project_id 기준 필터링(LOCK-MR-017), PII 마스킹 상태 확인(P1-7 연동)
4. Import 함수 구현 — 스키마 유효성 검증 → project_id 재매핑 → 중복 체크(memory_id) → INSERT
5. 가져오기 시 충돌 처리 — 동일 memory_id 존재 시 skip/overwrite/merge 전략 선택
6. 단위 테스트: 내보내기 → 가져오기 왕복(round-trip) 무손실 + project_id 격리

**검증**:
- [x] 내보내기 포맷이 MemoryRecordSchema 전체 필드 포함 — 산출물 §2.1 (Required 7 + Optional 6 + L3/B-2 확장 7 = 20필드 전수), §4.4 _serialize_record
- [x] project_id 기준 격리 내보내기 (LOCK-MR-017) — 산출물 §7 전체 (Export WHERE project_id 강제, Import 재매핑, 크로스 프로젝트 차단 EI_ERR_002)
- [x] 가져오기 시 스키마 유효성 검증 통과 — 산출물 §9 (V-1~V-11 검증 규칙 11종, _validate_schema 구현)
- [x] 왕복(export→import) 무손실 테스트 통과 — 산출물 §16.3 (UT-EI-RT01~RT05, JSONL/JSON 왕복 + L3/B-2 + QoD + KG)
- [x] 가져오기 시 중복 memory_id 충돌 처리 정책 동작 — 산출물 §6 (SKIP/OVERWRITE/USER_CHOICE 3전략, §6.2 보호 규칙)

**세션 종료 기록** (P1-6, 2026-04-13):
> **완료**: ExportImportManager L3 수준 완성 — Export 3포맷(JSONL/JSON/Markdown)+Import JSONL/JSON+MemoryRecordSchema 20필드 전수 직렬화+SHA-256 체크섬+project_id 재매핑(LOCK-MR-017)+PII 마스킹 상태 확인(P1-7 인터페이스)+충돌 해소 3전략(SKIP/OVERWRITE/USER_CHOICE)+KG 노드/엣지+SourceQoD 동반 내보내기/가져오기. 재검증 1회/이슈 3건 수정.
- 0. 산출물: 1건 (`export_import.md`, v1.1)
- 1. 게이트: 검증 체크리스트 5/5 ALL PASS, LOCK-MR-002/015/016/017/018/019 무위반
- 2. CONFLICT: 0건 (P1-6 신규 없음)
- 3. LOCK 변경: 0건 (LOCK-MR-002/015/016/017/018/019 무위반)
- 4. 이월: 없음
- 재검증 (step2): 1회/이슈 3건 수정 — (1) _validate_schema V-6/V-7/V-8 구현 누락 보완, (2) EscalationPayload JSON 구조 P1-4/P1-5 정합, (3) 로깅 중첩 JSON 패턴 정합

**산출물**: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\04_memory-distillation\export_import.md`
</details>

<details>
<summary><b>P1-7. PII 마스킹 (Part2 항목7)</b></summary>

**대조 기준**:
- §7 세부 작업: P1-7 "PII 마스킹"
- §7 전환 게이트: P1→P2: Part2 V1-P2 게이트 12항목 전체 통과
- §6 이슈: I-6 (PII 파이프라인)

**목표**: PII 탐지/마스킹 파이프라인을 L3 수준으로 완성한다. 5종 이상 PII 카테고리 탐지, DCL 연동(Restrict=마스킹 후 저장, Deny=차단), LOCK-MR-015를 준수하며, I-6 SHELL→FULL 전환을 포함한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` (LOCK — LOCK-MR-015 Deny 시 벡터 삽입 금지)
- `D:\VAMOS\docs\sot\D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` (D7 정책 — Restrict 시 마스킹 후 진행, PII 처리 규칙)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` (V1-Phase 2 항목7 — PII 마스킹 요건)
- I-6 참조: PII 마스킹 파이프라인 → 04_memory-distillation

**절차**:
1. PII 탐지 대상 정의 — 이메일, 전화번호, 주민등록번호, API 키, 비밀번호 등 카테고리 목록화
2. PII 탐지 엔진 설계 — 정규식 기반 1차 탐지 + 패턴 사전(dictionary) 보조
3. 마스킹 전략 구현 — 카테고리별 마스킹 포맷 정의(예: email→`***@***.com`, phone→`***-****-****`)
4. DCL 연동(P1-9): policy_decision=restrict 시 마스킹 후 저장, policy_decision=deny 시 저장 차단(LOCK-MR-015)
5. 마스킹 파이프라인 통합 — Create/Update 경로에 PII 탐지→마스킹→저장 순서 보장
6. I-6(PII 마스킹 파이프라인) SHELL→FULL 전환 — 상세 파이프라인 단계, 성능 요건 문서화
7. 단위 테스트: PII 탐지 정확도 + 마스킹 포맷 + Deny 차단 + Restrict 마스킹 후 저장

**검증**:
- [x] PII 탐지 카테고리 5종 이상 정의 — 8종(주민/전화/이메일/카드/계좌/주소/API키/비밀번호), 산출물 §2 ✅
- [x] Deny 시 저장 완전 차단 (LOCK-MR-015) — §6.4 deny → action=block, vector_insert_allowed=False ✅
- [x] Restrict 시 마스킹 후 저장 동작 — §6.3 옵션 B, action=store_masked ✅
- [x] I-6 SHELL→FULL 전환 완료 — §9 SHELL(4종 regex) → FULL(8종+사전+분류+DCL+파이프라인+에러12종+테스트32건) ✅
- [x] Create/Update 경로에 PII 탐지→마스킹→저장 순서 보장 — §7.1 Create 6단계, §7.2 Update 5단계 ✅

**세션 종료 기록** (P1-7, 2026-04-13):
> **완료**: PIIMasker L3 수준 완성 — PII 8종 탐지(주민/전화/이메일/카드/계좌/주소/API키/비밀번호)+정규식 1차+패턴 사전 2차 듀얼 엔진+4등급 민감도 분류(PUBLIC/INTERNAL/CONFIDENTIAL/SECRET, S7D-065)+DCL 교차 판정(D7 PolicyCheck × PII 민감도, 엄격한 쪽 채택)+카테고리별 마스킹 포맷(부분 보존/전체 마스킹/태그)+마스킹 완전성 검증(strict_mode→deny 승격)+Create/Update 6단계 파이프라인 통합+LOCK-MR-015 Deny 벡터 삽입 절대 금지+project_id 격리(LOCK-MR-017)+에러 12종(PII_ERR_001~012)+복구/재시도 3단계(자동→사용자→에스컬레이션)+에스컬레이션 페이로드+로깅 R-01-7(5 event_type, 원문 해시 처리)+Big-O 분석+I-6 SHELL→FULL 전환. 재검증 1회/이슈 3건 수정 — (1) EscalationPayload JSON 구조 P1-4/P1-5/P1-6 정합(severity/category/auto_resolved 추가, 필드명 통일), (2) 로깅 R-01-7 중첩 JSON 패턴 정합(log_id/level/component/details 구조화), (3) §20.2 MemoryRecordSchema 경로 교정(00_common→01_memory-hierarchy).
- 0. 산출물: 1건 (`pii_masking.md`, v1.1)
- 1. 게이트: 검증 체크리스트 5/5 ALL PASS, LOCK-MR-015/017/018/019 무위반
- 2. CONFLICT: 0건 (P1-7 신규 없음)
- 3. 이월: 없음
- 4. 비고: P1-6 §8 인터페이스 계약(detect/mask) 이행 완료, P1-9(DCL) 미완 — 인터페이스 수용 준비 완료

**산출물**: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\04_memory-distillation\pii_masking.md`
</details>

#### Phase 2 단계별 상세 작업 절차

> **Phase 2 범위**: Qdrant 전환, Neo4j 전환, 승격 자동화, 메모리 충돌 해소, V1→V2 마이그레이션 = 5블록
> **의존성**: Phase 1 완료 (P1→P2 Gate: Part2 V1-P2 게이트 12항목 전체 통과)

<details>
<summary><b>P2-1. QdrantAdapter 구현 (I-3)</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 2 "Qdrant 전환" (§7.1 L345)
- §7 전환 게이트: P2→P3 "Qdrant 전환 완료" (§7.4 L591)
- §6 이슈: I-3 (VectorStore 어댑터 구현 상세 — 인터페이스만 정의, Qdrant 어댑터 필수)
- 교차 도메인: 해당 없음
- Part2 버전: V2-Phase 2

**목표**: V1 ChromaAdapter에 이어 V2 QdrantAdapter를 L3 수준으로 구현 상세를 정의한다. LOCK-MR-013(V2 Vector DB = Qdrant 서버 모드), LOCK-MR-014(4개 메서드: upsert/search/delete/get_by_id) 준수한다. Phase 0 vectorstore_abc.py의 ABC 인터페이스를 구현한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` §2.2 (V2 Vector DB = Qdrant), §2.2-A (어댑터 인터페이스)
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\03_vector-db\vectorstore_abc.py` (P0-4 산출물 — ABC 인터페이스)
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\03_vector-db\chroma_adapter.md` (P1-3 산출물 — V1 ChromaAdapter 구현 상세)
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\AUTHORITY_CHAIN.md` LOCK-MR-013, MR-014, MR-017(project_id 격리)

**절차**:
1. D2.0-06 §2.2 읽기 → Qdrant 서버 모드 요건, 연결 설정, 컬렉션 전략 추출
2. vectorstore_abc.py 읽기 → ABC 인터페이스 4개 메서드 시그니처 확인
3. QdrantAdapter 구현 상세:
   - upsert: 벡터 삽입/갱신, project_id 메타데이터 필수(MR-017), Deny 정책 검사(MR-015)
   - search: Hybrid Search(Dense α=0.7 + Sparse 0.3, MR-008), similarity threshold 0.75(MR-009), Top-K=20
   - delete: project_id 기반 격리 삭제, 벡터 ID 또는 메타데이터 필터
   - get_by_id: 단일 벡터 조회, project_id 검증
4. Qdrant 서버 연결 관리: connection_url, gRPC/HTTP 선택, 연결 풀, 재연결 전략
5. BGE-M3 이중벡터(MR-011): 1024dim 원본 + Matryoshka 256dim 검색용 → Qdrant Named Vectors 활용

**검증**:
- [x] P2→P3 게이트 기여: Qdrant 전환 완료
- [x] LOCK-MR-013(Qdrant 서버 모드), MR-014(4개 메서드) 전체 구현
- [x] MR-008(Hybrid α=0.7), MR-009(threshold 0.75), MR-011(BGE-M3 이중벡터) 반영
- [x] MR-017(project_id 격리), MR-015(Deny 벡터 삽입 금지) 적용
- [x] Phase 0 ABC 인터페이스와 1:1 정합

**산출물**: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\03_vector-db\qdrant_adapter.md` (QdrantAdapter V2 L3 상세)
</details>

<details>
<summary><b>P2-2. V1→V2 마이그레이션 (I-7)</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 2 암묵적 (Qdrant 전환의 전제 조건)
- §7 전환 게이트: P2→P3 "마이그레이션 검증" (§7.4 L592)
- §6 이슈: I-7 (V1→V2 마이그레이션 — 원칙만 명시, 단계별 절차 필요)
- 교차 도메인: 해당 없음
- Part2 버전: V2-Phase 2

**목표**: Chroma(V1) → Qdrant(V2) 벡터 DB 마이그레이션 단계별 절차를 L3 수준으로 정의한다. I-7을 해결하여 데이터 무결성 검증, 롤백 방안, 듀얼 모드 운영 절차를 포함한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\03_vector-db\chroma_adapter.md` (P1-3 산출물 — V1 ChromaAdapter 구현 상세)
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\03_vector-db\chroma_collection_strategy.md` (P0-3 산출물 — V1 컬렉션 전략)
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\AUTHORITY_CHAIN.md` LOCK-MR-012(V1 Chroma), MR-013(V2 Qdrant)

**절차**:
1. V1 Chroma 데이터 구조 분석: 단일 컬렉션, 메타데이터 스키마, 벡터 수/크기 예상
2. 마이그레이션 단계 정의:
   - Phase A: Qdrant 서버 프로비저닝 + 스키마 생성
   - Phase B: 듀얼 모드(읽기=Chroma, 쓰기=양쪽) 활성화
   - Phase C: 기존 데이터 배치 마이그레이션(Chroma → Qdrant)
   - Phase D: 무결성 검증(벡터 수 일치, 검색 결과 동등성 테스트)
   - Phase E: 트래픽 전환(읽기=Qdrant) + Chroma 읽기 전용
   - Phase F: Chroma 폐기 + 롤백 윈도우 종료
3. 무결성 검증 자동화: 벡터 수 대조, 랜덤 샘플 검색 결과 비교, project_id 격리 확인
4. 롤백 방안: Phase E까지 Chroma 유지, 성능 이슈 시 즉시 Chroma 복귀

**검증**:
- [x] P2→P3 게이트 기여: 마이그레이션 검증 완료
- [x] I-7 해결: 6단계 마이그레이션 절차 + 무결성 검증 + 롤백 방안
- [x] 듀얼 모드 운영 절차 포함
- [x] MR-017(project_id 격리) 마이그레이션 중에도 유지 확인

**산출물**: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\03_vector-db\migration_v1_v2.md` (V1→V2 마이그레이션 L3 상세)
</details>

<details>
<summary><b>P2-3. Neo4j GraphRAG 전환 (I-8)</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 2 "Neo4j 전환" (§7.1 L345)
- §7 전환 게이트: P2→P3 암묵적 (Qdrant + Neo4j + 승격 자동화 완성)
- §6 이슈: I-8 (GraphRAG 상세 — NetworkX 언급만, 노드/엣지 타입 + 쿼리 파이프라인 + V2 Neo4j 전환 필요)
- 교차 도메인: 해당 없음
- Part2 버전: V2-Phase 2

**목표**: V1 NetworkX 기반 GraphRAG를 V2 Neo4j로 전환한다. I-8을 해결하여 노드/엣지 타입 정의, Cypher 쿼리 파이프라인, 그래프 구축 자동화를 L3 수준으로 정의한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\02_rag-pipeline\json_graphrag.md` (P1-4 산출물 — V1 JSON/NetworkX 기반)
- `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` §1.1 (6-Stage RAG, MR-007)
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\AUTHORITY_CHAIN.md` LOCK-MR-007(6-Stage RAG)

**절차**:
1. P1-4 산출물 json_graphrag.md 읽기 → V1 JSON/NetworkX 구현 상태 확인
2. Neo4j 그래프 스키마 설계:
   - 노드 타입: Document, Chunk, Entity, Concept, Memory(L0~L3)
   - 엣지 타입: CONTAINS, REFERENCES, SIMILAR_TO, DERIVED_FROM, PROMOTED_TO
   - 속성: project_id(MR-017 격리), created_at, qod_score, scope
3. Cypher 쿼리 파이프라인: 유사도 기반 검색, 경로 탐색, 서브그래프 추출
4. 그래프 구축 자동화: RAG Stage 4(Store) 시 자동 엔티티 추출 + 관계 생성
5. NetworkX → Neo4j 마이그레이션: 그래프 데이터 변환, 듀얼 모드 운영

**검증**:
- [x] I-8 해결: 노드/엣지 타입 + Cypher 쿼리 파이프라인 + Neo4j 마이그레이션 완전 정의
- [x] MR-007(6-Stage RAG) Stage 5(Retrieve) 그래프 검색 통합
- [x] MR-017(project_id 격리) Neo4j 멀티테넌시 지원
- [x] V1 NetworkX 데이터 마이그레이션 방안 포함

**산출물**: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\02_rag-pipeline\neo4j_graphrag.md` (V2 Neo4j GraphRAG L3 신규 — P1-4 json_graphrag.md와 구분)
</details>

<details>
<summary><b>P2-4. 자동 승격/강등 알고리즘 (I-5)</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 2 "승격 자동화" (§7.1 L345)
- §7 전환 게이트: P2→P3 "승격 자동화 테스트 통과" (§7.4 L592)
- §6 이슈: I-5 (승격/강등 알고리즘 — 조건만 나열, 스코어링 함수 + QoD 연동 + 자동화 로직 필요)
- 교차 도메인: 해당 없음
- Part2 버전: V2-Phase 2

**목표**: 메모리 계층(L0~L3) 간 자동 승격/강등 알고리즘을 L3 수준으로 정의한다. I-5를 해결하여 QoD 스코어 기반 스코어링 함수, 승격/강등 임계값, 자동화 스케줄러를 포함한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` §2 (4계층 정의, 승격/강등 조건, DEC-014 스코어링 근거)
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\MemoryRecordSchema.md` (P0-1 산출물 — QoD/access_count/scope 필드 정의)
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\AUTHORITY_CHAIN.md` LOCK-MR-001(4계층), MR-002(B↔L 매핑), MR-016(L3 활성 게이트), MR-004(TTL 90일)

**절차**:
1. D2.0-06 §2 읽기 → 계층별 승격/강등 조건 추출
2. 스코어링 함수 설계: `promotion_score = access_count × 0.4 + recency × 0.3 + confidence × 0.3` (정본 §A.4 단일 정의 — DEC-014 4요소 공식은 QoD 점수이며 MemoryRecordSchema §2.4에서 D6 3요소로 RESOLVED, promotion_score 아님)
3. 승격 규칙:
   - L0→L1: session_end 시 promotion_score ≥ 0.6 → 자동 승격
   - L1→L2: 90일 내 access_count ≥ 5 + promotion_score ≥ 0.7 → 자동 승격
   - L2→L3: ADMIN 승인 필수(MR-016 L3 게이트) + promotion_score ≥ 0.8
4. 강등 규칙:
   - L2→L1: 180일 미접근 + promotion_score < 0.5 → 강등 후보 → ADMIN 확인
   - L1→폐기: TTL 90일(MR-004) 만료 + 연장 미승인
5. 자동화 스케줄러: 일일 배치 실행, 승격/강등 후보 리스트 생성, 알림

**검증**:
- [x] P2→P3 게이트 기여: 승격 자동화 테스트 통과
- [x] I-5 해결: 스코어링 함수 + QoD 연동 + 자동화 로직 완전 정의
- [x] MR-001(4계층), MR-002(B↔L 매핑), MR-016(L3 게이트) 준수
- [x] 승격/강등 각각 임계값·조건·자동화 수준 명시

**산출물**: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\promotion_demotion.md` (자동 승격/강등 L3 신규 정의 — V2-Phase 2 신규 산출물)
</details>

<details>
<summary><b>P2-5. 메모리 충돌 해소 + L4 Archive 범위 확정</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 2 산출물 "메모리 충돌 해소" (§7.1 L345)
- §7 전환 게이트: P2→P3 암묵적 (V2 최적화 완성)
- §6 이슈: CONFLICT_LOG #004 (L4 Archive D2.0-06 미정의 → V2+ 확장으로만 참조)
- 교차 도메인: 해당 없음
- Part2 버전: V2-Phase 2

**목표**: 메모리 계층 간 충돌 해소 메커니즘(동일 키 다계층 존재, 버전 충돌, QoD 불일치)을 L3 수준으로 정의한다. CONFLICT_LOG #004(L4 Archive)의 V2 범위를 확정한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\_index.md` (Phase 1 산출물)
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\CONFLICT_LOG.md` #004(L4 Archive 미정의)
- `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` §2 (4계층 정본)

**절차**:
1. 메모리 충돌 유형 분류: (1) 동일 키 다계층 존재, (2) 버전 충돌(같은 데이터 다른 버전), (3) QoD 불일치(계층 간 QoD 역전)
2. 각 충돌 유형별 해소 전략:
   - 동일 키: 상위 계층 우선, 하위 계층 참조 포인터로 전환
   - 버전 충돌: 최신 버전 우선, 구버전 deprecated 마킹
   - QoD 역전: 자동 강등 후보 플래그, ADMIN 리뷰
3. CONFLICT_LOG #004 해결: L4 Archive = V2+ 확장 전용, D2.0-06 4계층(L0~L3)과 별도 관리, STEP7-D L4 참조를 D2.0-06 L2로 리매핑
4. 충돌 탐지 자동화: 일일 스캔, 충돌 리포트, 자동 해소(정책 기반) vs. 수동 해소(ADMIN 리뷰)

**검증**:
- [x] 메모리 충돌 3유형 각각 해소 전략 정의
- [x] CONFLICT_LOG #004 해결: L4 Archive V2+ 범위 확정
- [x] MR-001(4계층 L0~L3) 정본 무변경 확인
- [x] 충돌 탐지 자동화 + 해소 정책 포함

**산출물**: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\memory_conflict_resolution.md` (메모리 충돌 해소 L3)
</details>

---

### 7.5 Phase 3 잔존·후속 작업

| # | 작업 | 상세 | 완료 조건 |
|---|------|------|----------|
| P3-POST-1 | **D2.0-06 §2.5.3 L0 TTL 표기 정정** | D2.0-06 §2.5.3 Formal TTL Table(L268)의 "세션 종료 즉시 만료"를 `세션 종료 시 만료 (최대 30일)`로 수정하여 §2.1(L121) 및 Part2(L1907) LOCK과 내부 일관성 확보 (CONFLICT_LOG #006) | D2.0-06 원본 L268 수정 완료 → CONFLICT_LOG #006 상태를 ✅ 해결로 전환 |

> **Note**: P3-POST-1은 SOT 원본(D2.0-06) 수정 권한이 필요하므로 Phase 3 진입 시 또는 별도 SOT 관리 세션에서 처리한다. 6-4 계획서 자체의 LOCK-MR-003 값에는 영향 없음.

### 7.6 Phase 3 본격 세부 태스크 — V3 스케일 (Phase 15 S15-5 추가, 2026-05-14) ✅ Phase 3 완료 (2026-05-18, 5 task — chain `phase3_6-4_2026-05-18`, P3-1 매니지드 DB V3 + P3-2 멀티테넌시 V3 + P3-3 GDPR/SOC-2 V3 + P3-4 Dream Mode V3 + P3-5 통계 대시보드 V3 ALL tcv1 first-pass-after-fix CONFIRMED, R cascade 205 verifications + 15 char-swap fixes / 8 drift categories / 13 line edits ALL textual notation only, ★★★ 누적 Δ 0 B / 0 LF 🎯 baseline byte 자동 복원 specialty milestone, ★★ Phase 3 핵심 신규 이슈 LOCK-MR-005/006 vs GDPR Right to Erasure 충돌 정식 해소 (P3-3), ★★ P3-4 3 first 사례 동시 specialty milestone, ★ distinct 7 cross-handoff unique target domains 7/7 ALL 도달 100% (6-2+6-7+6-1+6-12+6-5+6-6+5-2 §7.6 L1665 정본 EXACT MATCH RESOLVED queue), **[PHASE4_READY: 6-4 — 2026-05-18]**)

> **진입 조건**: P2→P3 게이트 (§7.4 L593) — Qdrant 전환 완료 + 승격 자동화 테스트 통과 + 마이그레이션 검증 (Phase 2 P2-1~P2-3 완료 inheritance)
>
> **완료 조건**: P3→완료 게이트 신규 정의 — V3 스케일 NEW 산출물 5건 L3 PASS + LOCK-MR-005/006(L2/L3 무기한 보존) vs GDPR 삭제권 충돌 해소 + production 배포 준비
>
> **요약형 분해**: §7.1 L346 Phase 3 row "V3 스케일: 엔터프라이즈 확장, 멀티테넌시 / 매니지드 DB, GDPR/SOC-2, Dream Mode(오프라인 정리), 통계 대시보드" → 5개 논리 그룹(P3-1~P3-5) × `<details>` 블록 5개

<details>
<summary><b>P3-1. 매니지드 DB 통합 (V1 SQLite → PostgreSQL/MySQL 엔터프라이즈)</b></summary>

**대조 기준 (7항목)**:
- 작업 그룹 ID: P3-1 (§7.1 L346 Phase 3 산출물 "매니지드 DB" — V3 엔터프라이즈 확장 첫 항목)
- 전환 게이트 조건: P2→P3 ✅ (Qdrant 전환 ✅ + 마이그레이션 검증 ✅) → P3→완료 신규 정의 (PostgreSQL/MySQL 어댑터 동작 + 마이그레이션 검증)
- §6 이슈 ID: I-7 (V1→V2 마이그레이션 → V2→V3 엔터프라이즈 마이그레이션 확장)
- 교차 도메인: 6-2 Security-Governance (DB 보안 + 암호화 + GDPR), 6-7 RT-BNP-DCL (RAG 백엔드 DB 호환), 6-8 Cloud-Library (있는 경우, 클라우드 DB 배포 cross-handoff)
- V3-Phase 매핑: §7.1 L346 "V3-Phase 2 관련, 엔터프라이즈 확장"
- production 측정 baseline: Phase 1 11/11 ✅ 완료 (2026-04-13, P1-1~P1-11 전체) + Phase 2 V2 Qdrant 산출물 inheritance
- Phase 4 entry-gate 충족 조건: `managed_db_v3.md` NEW L3 + PostgreSQL/MySQL 어댑터 인터페이스(LOCK-MR-014 4개 메서드 정합) + 데이터 마이그레이션 무손실 검증 + 6-2 암호화 cross-handoff RESOLVED

**목표**: V3 엔터프라이즈 환경에서 V1 로컬 SQLite를 매니지드 RDB(PostgreSQL/MySQL)로 마이그레이션. 어댑터 패턴(LOCK-MR-014 4개 메서드 시그니처 정합)으로 V1 코드 변경 최소화. LOCK-MR-001(4계층 L0~L3) 재정의 0건.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` §2 (4계층 정본 LOCK-MR-001) + §2.2 (V1/V2 Vector DB LOCK-MR-012/013)
- `D:\VAMOS\docs\sot\D2.1-D6_D6_SCHEMA_STORAGE_MEMORY.md` (MemoryRecordSchema + SourceQoDSchema 정본)
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\sqlite_ddl.sql` (Phase 0 P0-2 산출물, V1 SQLite DDL)
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\03_vector-db\vectorstore_abc.py` (Phase 0 P0-4 산출물, VectorStore 어댑터 ABC)
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\AUTHORITY_CHAIN.md` LOCK-MR-001/002/014/017
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\` (있는 경우, DB 암호화 cross-handoff)

**절차**:
1. PostgreSQL/MySQL 어댑터 인터페이스 정의 — V1 SQLite와 동일 시그니처(LOCK-MR-014 4개 메서드 + L0/L1 CRUD)
2. 데이터 마이그레이션 절차 — (1) 스키마 변환(SQLite → PostgreSQL DDL), (2) 데이터 export(JSON Lines), (3) import + 무결성 해시 검증, (4) Phase 2 자동 승격(P2-2 산출물) 호환성 확인, (5) 롤백 절차
3. LOCK-MR-001 (4계층 L0~L3) 매핑 — PostgreSQL의 schema/table을 4계층에 어떻게 매핑할지 (L0 session, L1 project, L2 long-term, L3 procedural)
4. 매니지드 DB 운영 — Connection pooling, 백업 전략(daily snapshot + WAL), HA(replica), 비용 모델
5. LOCK-MR-002 (B↔L 매핑 B-1→L1, B-2→L3, B-3→L2, B-4→L0) 정합
6. 6-2 Security 암호화 cross-handoff — at-rest 암호화(LOCK-MR Part2 §6.5 SQLCipher 정합), in-transit TLS, 키 순환
7. 6-7 RT-BNP-DCL cross-handoff — Vector DB(Qdrant V2) ↔ 매니지드 RDB 연동 정합
8. L3 9요소(E1~E9) 작성

**검증**:
- [x] PostgreSQL/MySQL 어댑터 LOCK-MR-014 4개 메서드 시그니처 정합 (재정의 0건)
- [x] LOCK-MR-001 (4계층 L0~L3) 정본 무변경 — `<!-- LOCK-MR-001 정합 -->` 인용
- [x] LOCK-MR-002 B↔L 매핑 정합
- [x] LOCK-MR-017 project_id 격리 — 엔터프라이즈 환경에서도 강제 (멀티테넌시 P3-2 cross-ref)
- [x] 데이터 마이그레이션 무손실 검증 (해시 + 카운트 + 샘플 비교)
- [x] § 6 I-7 (V1→V2 마이그레이션 패턴 직계 V2→V3) 확장 명시
- [x] 6-2 Security DB 암호화 cross-handoff (at-rest + in-transit + 키 순환)
- [x] 6-7 RT-BNP-DCL Vector DB ↔ 매니지드 RDB 연동 cross-handoff
- [x] L3 9요소(E1~E9) ≥ 7
- [x] **Phase 4 entry-gate 충족 조건**: managed_db_v3.md byte ≥ 400L + L3 PASS + 마이그레이션 무손실 검증 + 2 cross-handoff RESOLVED

**산출물**: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\managed_db_v3.md` (매니지드 DB V3 L3 상세) + `01_memory-hierarchy\postgresql_adapter.py` 어댑터 스텁
</details>

<details>
<summary><b>P3-2. 멀티테넌시 아키텍처 (project_id → tenant_id 계층화)</b></summary>

**대조 기준 (7항목)**:
- 작업 그룹 ID: P3-2 (§7.1 L346 Phase 3 산출물 "멀티테넌시")
- 전환 게이트 조건: P2→P3 ✅ → P3→완료 신규 정의 (테넌트 격리 검증 + cross-tenant 시도 차단)
- §6 이슈 ID: I-1 (L0~L3 계층 상세 → 멀티테넌시 계층 추가 — tenant 계층)
- 교차 도메인: 6-2 Security-Governance (테넌트 격리 보안 + RBAC 4단계 LOCK 정합), 6-12 Event-Logging (테넌트별 감사 로그), 5-2 File-Context-Strategy (테넌트별 컨텍스트 윈도우)
- V3-Phase 매핑: §7.1 L346 "V3-Phase 2 관련, 멀티테넌시"
- production 측정 baseline: LOCK-MR-017 (project_id 격리) baseline + Phase 1 P1-9 DCL 산출물 inheritance
- Phase 4 entry-gate 충족 조건: `multi_tenancy_v3.md` NEW L3 + tenant_id 계층 정의(LOCK-MR-017 확장) + cross-tenant 격리 검증 + 6-2 RBAC cross-handoff RESOLVED

**목표**: V3 멀티테넌시 — V1 project_id 격리(LOCK-MR-017)를 확장하여 tenant_id 계층 추가. 한 매니지드 DB 인스턴스에서 다수 테넌트가 안전하게 격리 운영. RBAC 4단계(OWNER/ADMIN/OPERATOR/VIEWER) × 테넌트별 적용.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` §1 (project_id LOCK-MR-017 정본)
- `D:\VAMOS\docs\sot\BASE-1.3_VAMOS_RULE_1.3_BASE.md` §7.2 (project_id 격리 RULE 정본)
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\02_rag-pipeline\dcl_basic.md` (Phase 1 P1-9 DCL 산출물, Deny/Restrict/Allow)
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\AUTHORITY_CHAIN.md` LOCK-MR-015 (Deny 금지) + LOCK-MR-017 (project_id 격리) + LOCK-MR-019 (저장 폭주 방지)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\` (있는 경우, RBAC L10 + 테넌트 격리 cross-handoff)
- `D:\VAMOS\docs\sot 2\5-2_File-Context\` (있는 경우, 테넌트별 컨텍스트 cross-handoff)

**절차**:
1. tenant_id 계층 정의 — `tenant_id → project_id → memory_record` 3 계층 (LOCK-MR-017 확장 — `<!-- V3 EXTENSION, NOT REDEFINITION -->`)
2. 격리 메커니즘 — (1) DB schema 분리(tenant별), (2) row-level security(tenant_id WHERE filter 강제), (3) Vector DB collection 분리(tenant별 namespace, LOCK-MR-017 정합)
3. cross-tenant 시도 차단 — query filter 강제, 시도 시 DCL Deny(LOCK-MR-015 적용) + CONFLICT_LOG 기록
4. RBAC × 테넌트 매트릭스 — 4 역할 × N 테넌트 권한 매트릭스 (테넌트별 OWNER vs 글로벌 OWNER 구분)
5. 테넌트별 비용 추적 + 리소스 격리 (memory budget per tenant)
6. 6-2 Security cross-handoff — 테넌트 격리 보안 정책 (Zero-Trust + 테넌트 인증 토큰)
7. 6-12 Event-Logging cross-handoff — 테넌트별 감사 로그 분리 (SOC-2 요구사항 P3-3 cross-ref)
8. 5-2 File-Context-Strategy cross-handoff — 테넌트별 컨텍스트 윈도우 + 토큰 할당
9. L3 9요소(E1~E9) 작성

**검증**:
- [x] tenant_id 계층 정의 — LOCK-MR-017 확장 (재정의 아님) `<!-- V3 EXTENSION, NOT REDEFINITION -->`
- [x] cross-tenant 시도 차단 검증 — DCL Deny + CONFLICT_LOG 기록
- [x] LOCK-MR-015 (Deny 벡터 삽입 금지) 정합
- [x] LOCK-MR-019 (루프 저장 폭주 방지) 테넌트별 적용
- [x] § 6 I-1 (L0~L3 계층 상세) 멀티테넌시 추가 명시
- [x] 6-2 Security RBAC × 테넌트 매트릭스 cross-handoff
- [x] 6-12 Event-Logging 테넌트별 감사 로그 cross-handoff (SOC-2 P3-3 cross-ref)
- [x] 5-2 File-Context-Strategy 테넌트별 컨텍스트 cross-handoff
- [x] L3 9요소(E1~E9) ≥ 7
- [x] **Phase 4 entry-gate 충족 조건**: multi_tenancy_v3.md byte ≥ 400L + L3 PASS + cross-tenant 격리 검증 + 3 cross-handoff RESOLVED

**산출물**: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\multi_tenancy_v3.md` (멀티테넌시 V3 L3 상세)
</details>

<details>
<summary><b>P3-3. GDPR/SOC-2 컴플라이언스 (Right to Delete + 감사 로그)</b></summary>

**대조 기준 (7항목)**:
- 작업 그룹 ID: P3-3 (§7.1 L346 Phase 3 산출물 "GDPR/SOC-2")
- 전환 게이트 조건: P2→P3 ✅ → P3→완료 신규 정의 (GDPR 6 권리 + SOC-2 Type II 감사 통과)
- §6 이슈 ID: LOCK-MR-005/006 (L2/L3 무기한 보존) vs **GDPR Right to be Forgotten 충돌 해소** — Phase 3 핵심 신규 이슈
- 교차 도메인: 6-2 Security-Governance (Phase 2 P2-3 `gdpr_compliance.md` 361L direct inheritance — 7 원칙 + 6 권리 + DPIA + Art. 33 72h), 6-12 Event-Logging (SOC-2 감사 로그)
- V3-Phase 매핑: §7.1 L346 "V3-Phase 2 관련, GDPR/SOC-2"
- production 측정 baseline: 6-2 P2-3 gdpr_compliance.md 361L baseline (cross-domain inheritance) + Phase 1 P1-7 PII 마스킹 산출물 inheritance
- Phase 4 entry-gate 충족 조건: `gdpr_soc2_v3.md` NEW L3 + LOCK-MR-005/006 vs GDPR 충돌 해소 정합 + GDPR 6 권리 구현 + SOC-2 감사 로그 + 6-2 cross-handoff direct inheritance

**목표**: V3 컴플라이언스 — GDPR (7 원칙 + 6 권리 + DPIA + Art. 33 72h, 6-2 P2-3 직계) + SOC-2 Type II 요구사항. **핵심 충돌 해소**: LOCK-MR-005/006 (L2/L3 무기한 보존) vs GDPR "Right to be Forgotten" — 본 V3 산출물에서 정식 해소.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\01_ai-code-security\gdpr_compliance.md` (P2-3 산출물 361L — direct inheritance, 6-2 cross-domain 정본)
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\04_memory-distillation\pii_masking.md` (Phase 1 P1-7 산출물, PII 8종 탐지 + 마스킹)
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\AUTHORITY_CHAIN.md` LOCK-MR-005 (L2 무기한) + LOCK-MR-006 (L3 무기한 deprecated 전환만)
- `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` §2.1 (보존 정책 정본)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\` AUTHORITY_CHAIN LOCK L13 (SQLCipher 암호화)
- `D:\VAMOS\docs\sot 2\6-12_Event-Logging\` (있는 경우, SOC-2 감사 로그 cross-handoff)

**절차**:
1. 6-2 P2-3 `gdpr_compliance.md` 361L 직계 inheritance — GDPR 7 원칙(Lawfulness, Purpose Limitation, Data Minimization, Accuracy, Storage Limitation, Integrity/Confidentiality, Accountability) + 6 권리(Access, Rectification, Erasure, Restriction, Portability, Object) + DPIA + Art. 33 72h 통보
2. **LOCK-MR-005/006 vs GDPR Right to Erasure 충돌 해소** — 본 V3 산출물에서 정식 해소:
   - GDPR Erasure 요청 시: L2/L3 메모리에서 개인 데이터 삭제 (LOCK-MR-006 "deprecated 전환" 메커니즘 활용 + 추가 정의)
   - 추적 가능성 (CONFLICT_LOG에 erasure 이력 기록 + audit trail 보존)
   - LOCK-MR-005/006 재정의 0건 — "deprecated 전환"의 범위 확장으로 처리(`<!-- LOCK-MR-006 의 V3 적용 확장 -->`)
3. GDPR 6 권리 구현 — 각 권리별 API 엔드포인트 + 응답 시간(1 month rule) + 검증 절차
4. SOC-2 Type II — 5 Trust Service Criteria (Security, Availability, Processing Integrity, Confidentiality, Privacy) 매핑 + 감사 로그 12 month 보존
5. PII 마스킹 (P1-7) cross-ref — 저장 전 PII 자동 마스킹 + GDPR 동의 추적
6. 6-2 Security cross-handoff — gdpr_compliance.md 직계 + 추가 V3 확장 사항
7. 6-12 Event-Logging cross-handoff — SOC-2 감사 로그 표준 LogEvent
8. L3 9요소(E1~E9) 작성

**검증**:
- [x] **LOCK-MR-005/006 vs GDPR Right to Erasure 충돌 정식 해소** — `<!-- LOCK-MR-006 의 V3 적용 확장 -->` 명시 + 재정의 0건
- [x] LOCK-MR-005/006 재정의 0건 검증
- [x] GDPR 7 원칙 + 6 권리 + DPIA + Art. 33 72h 전수 구현
- [x] SOC-2 5 Trust Service Criteria 매핑 + 감사 로그 12 month 보존
- [x] PII 마스킹 (Phase 1 P1-7 LOCK-MR-015 Deny 금지) cross-ref
- [x] § 6 이슈 (LOCK-MR-005/006 vs GDPR 충돌) RESOLVED + CONFLICT_LOG 신규 항목 등재
- [x] 6-2 Security gdpr_compliance.md direct inheritance 명시 (재작성 0건)
- [x] 6-12 Event-Logging SOC-2 감사 로그 cross-handoff
- [x] L3 9요소(E1~E9) ≥ 7
- [x] **Phase 4 entry-gate 충족 조건**: gdpr_soc2_v3.md byte ≥ 500L + L3 PASS + LOCK-MR 충돌 해소 + 2 cross-handoff RESOLVED + CONFLICT_LOG 갱신

**산출물**: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\gdpr_soc2_v3.md` (GDPR/SOC-2 V3 L3 상세) + CONFLICT_LOG.md 신규 RESOLVED 항목 (LOCK-MR-005/006 vs GDPR 충돌)
</details>

<details>
<summary><b>P3-4. Dream Mode (오프라인 정리 + 자동 아카이브)</b></summary>

**대조 기준 (7항목)**:
- 작업 그룹 ID: P3-4 (§7.1 L346 Phase 3 산출물 "Dream Mode(오프라인 정리)")
- 전환 게이트 조건: P2→P3 ✅ (Phase 2 P2-4 자동 승격 + P2-5 메모리 충돌 해소 inheritance) → P3→완료 신규 정의 (오프라인 정리 사이클 + 콜드 스토리지 동작)
- §6 이슈 ID: CONFLICT_LOG #004 (L4 Archive D2.0-06 미정의 → V2+ 확장) — Dream Mode가 L4 Archive 활용 가능성 정합
- 교차 도메인: 6-6 Self-Evolution-System (S-Module 오프라인 분석 cross-ref — S-7 Evolution Scheduler), 6-5 SDAR-System (메모리 자가 진단 cross-handoff)
- V3-Phase 매핑: §7.1 L346 "V3-Phase 2 관련, Dream Mode(오프라인 정리)"
- production 측정 baseline: Phase 2 P2-4 promotion_automation.md (자동 승격) inheritance + Phase 1 P1-8 B-3 Memory Decay (지수 감쇠 half_life=30d) inheritance
- Phase 4 entry-gate 충족 조건: `dream_mode_v3.md` NEW L3 + 오프라인 정리 사이클 정의 + L4 Archive (CONFLICT #004) V2+ 활용 명시 + 6-6 S-7 cross-ref RESOLVED

**목표**: V3 Dream Mode — 시스템 idle 시간(예: 새벽) 동안 메모리 오프라인 정리. 자동 아카이브(L2 → L4 Archive 또는 콜드 스토리지), B-3 Decay 후보 일괄 처리(P1-8 inheritance), L2 메모리 통계 재계산, 인덱스 재구성.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\B3_memory_decay.md` (Phase 1 P1-8 산출물, B-3 Decay half_life=30d)
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\promotion_automation.md` (Phase 2 P2-4 산출물, 자동 승격/강등)
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\memory_conflict_resolution.md` (Phase 2 P2-5 산출물, 충돌 해소)
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\CONFLICT_LOG.md` #004 (L4 Archive V2+ 범위 확정)
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\AUTHORITY_CHAIN.md` LOCK-MR-005 (L2 무기한) + LOCK-MR-006 (L3 무기한)
- `D:\VAMOS\docs\sot 2\6-6_Self-Evolution-System\` (있는 경우, S-7 Evolution Scheduler cross-ref)

**절차**:
1. Dream Mode 트리거 조건 — (1) 시스템 idle 감지(CPU < 20% + 활성 사용자 0), (2) 일일 정해진 시간(예: 03:00 KST), (3) 수동 트리거
2. 정리 작업 순서 — (1) B-3 Decay 후보 일괄 처리 (P1-8 직계), (2) 자동 승격/강등 (P2-4 직계), (3) 메모리 충돌 해소 (P2-5 직계), (4) L2 → L4 Archive 이동(CONFLICT #004 V2+ 확장 활용), (5) 콜드 스토리지 (S3/Glacier) 아카이브, (6) 인덱스 재구성 + 통계 재계산
3. L4 Archive 활용 (CONFLICT_LOG #004 정합) — D2.0-06 4계층(L0~L3) 정본 보존 + L4 Archive = V2+ 확장 별도 관리
4. 콜드 스토리지 정책 — 1년 이상 미접근 메모리 자동 아카이브, 검색 시 자동 복원(latency 명시)
5. 6-6 S-7 Evolution Scheduler cross-ref — Dream Mode 동안 S-Module도 오프라인 분석 동시 실행 가능성 검토
6. 6-5 SDAR cross-handoff — Dream Mode 결과를 메모리 자가 진단 input으로 활용
7. L3 9요소(E1~E9) 작성

**검증**:
- [x] Dream Mode 트리거 조건 3종 정의
- [x] 정리 작업 순서 6단계 정의 + 각 단계 P1-8/P2-4/P2-5 직계 inheritance 명시
- [x] L4 Archive 활용 — CONFLICT_LOG #004 V2+ 확장 정합 (LOCK-MR-001 4계층 재정의 0건)
- [x] 콜드 스토리지 정책 + 복원 latency 명시
- [x] LOCK-MR-005/006 (L2/L3 무기한 보존) 정합 — Archive로 이동 시 deprecated 전환 메커니즘 사용
- [x] § 6 CONFLICT #004 RESOLVED — L4 Archive V2+ 범위 확정 + Dream Mode 활용 명시
- [x] 6-6 Self-Evolution S-7 Evolution Scheduler cross-ref
- [x] 6-5 SDAR 메모리 자가 진단 cross-handoff
- [x] L3 9요소(E1~E9) ≥ 7
- [x] **Phase 4 entry-gate 충족 조건**: dream_mode_v3.md byte ≥ 350L + L3 PASS + 정리 사이클 정의 + 2 cross-ref/handoff RESOLVED

**산출물**: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\dream_mode_v3.md` (Dream Mode V3 L3 상세)
</details>

<details>
<summary><b>P3-5. 통계 대시보드 (메모리/캐시/벡터 DB/QoD)</b></summary>

**대조 기준 (7항목)**:
- 작업 그룹 ID: P3-5 (§7.1 L346 Phase 3 산출물 "통계 대시보드")
- 전환 게이트 조건: P2→P3 ✅ → P3→완료 신규 정의 (대시보드 7+ 메트릭 + 알림 임계값)
- §6 이슈 ID: §6 메모리 통계 가시화 요구 (운영성 — 신규 정의)
- 교차 도메인: 6-1 UI-UX-System (대시보드 UI 시각화 cross-handoff — 6-1 P3-3 디지털 휴먼 + V3 슬롯 직계 활용 가능), 6-12 Event-Logging (통계 데이터 출처)
- V3-Phase 매핑: §7.1 L346 "V3-Phase 2 관련, 통계 대시보드"
- production 측정 baseline: Phase 1 11/11 + Phase 2 P2-1/P2-2/P2-3 통산 산출물 + LOCK-MR-008/009/010 (Hybrid α, threshold, Cache cosine) baseline
- Phase 4 entry-gate 충족 조건: `statistics_dashboard_v3.md` NEW L3 + 7+ 메트릭 정의 + 알림 임계값 + 6-1 UI cross-handoff + production 배포 준비

**목표**: V3 운영 가시성 — 메모리 사용 현황, 캐시 히트율, 벡터 DB 성능, QoD 분포, TTL 임박 알림 통합 대시보드. 운영자가 한 화면에서 메모리 시스템 건강도를 확인. LOCK-MR-008(Hybrid α=0.7) + LOCK-MR-009(threshold=0.75) + LOCK-MR-010(Semantic Cache cosine ≥ 0.95) 메트릭 시각화.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\AUTHORITY_CHAIN.md` LOCK-MR 19 (대시보드 KPI 매핑 base)
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\04_memory-distillation\semantic_cache.md` (Phase 1 산출물, LOCK-MR-010 cosine ≥ 0.95)
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\02_rag-pipeline\hybrid_search.md` (Phase 1 P1-11 산출물, LOCK-MR-008/009)
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\sqlite_ddl.sql` (SourceQoD 테이블 포함)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\` (있는 경우, 대시보드 UI cross-handoff — V3 확장 슬롯 활용)
- `D:\VAMOS\docs\sot 2\6-12_Event-Logging\` (있는 경우, 통계 데이터 출처 cross-handoff)

**절차**:
1. 대시보드 메트릭 정의 — (1) **메모리 사용**: L0/L1/L2/L3 별 레코드 수 + 크기 + 증가율, (2) **캐시 히트율**: Semantic Cache hit/miss/eviction (LOCK-MR-010 정합), (3) **벡터 DB 성능**: 인덱스 크기, 검색 latency P50/P95/P99, threshold 통과율 (LOCK-MR-009), (4) **Hybrid Search 가중치**: α=0.7 효과(LOCK-MR-008), (5) **QoD 분포**: source_qod 점수 분포 + 임계값 추적, (6) **TTL 임박**: L0 30일/L1 90일 임박 알림, (7) **테넌트별 사용량**(P3-2 cross-ref)
2. 알림 임계값 — 캐시 히트율 < 30% 경고, 벡터 검색 P99 > 1초 경고, QoD 평균 < 0.6 경고, TTL 7일 임박 알림
3. 데이터 출처 — DB query(raw stats) + 6-12 Event-Logging(이벤트 통계) cross-handoff
4. 시각화 — Time-series 차트(메모리 증가), 히트맵(테넌트 × 시간), 게이지(캐시 히트율), 막대 차트(QoD 분포)
5. 6-1 UI-UX-System cross-handoff — 대시보드 UI 컴포넌트 (P3-3 디지털 휴먼 대시보드 위젯 또는 P3-4 V3 확장 슬롯 SidebarSlot 활용 가능)
6. 6-12 Event-Logging cross-handoff — 통계 데이터 출처 (LogEvent 표준)
7. L3 9요소(E1~E9) 작성

**검증**:
- [x] 7+ 메트릭 정의 (메모리/캐시/벡터/Hybrid/QoD/TTL/테넌트)
- [x] LOCK-MR-008/009/010 (Hybrid α / threshold / Cache cosine) 인용 정합
- [x] 알림 임계값 ≥ 5건 정의
- [x] 6-1 UI-UX-System 대시보드 UI cross-handoff (P3-3 또는 P3-4 V3 확장 슬롯 활용 검토)
- [x] 6-12 Event-Logging 통계 데이터 출처 cross-handoff
- [x] P3-2 멀티테넌시 cross-ref (테넌트별 사용량 분리)
- [x] L3 9요소(E1~E9) ≥ 7
- [x] **Phase 4 entry-gate 충족 조건**: statistics_dashboard_v3.md byte ≥ 350L + L3 PASS + 7+ 메트릭 + 2 cross-handoff RESOLVED

**산출물**: `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\01_memory-hierarchy\statistics_dashboard_v3.md` (통계 대시보드 V3 L3 상세)
</details>

> **Phase 3 → Phase 4 인계 게이트** (Phase 15 NEW, §7.4 P3→완료 신규 정의):
> - [x] Phase 3 NEW 산출물 5건(managed_db_v3 + multi_tenancy_v3 + gdpr_soc2_v3 + dream_mode_v3 + statistics_dashboard_v3) 모두 L3 PASS (9요소 ≥ 7) + 어댑터 시그니처 + 의사코드 포함
> - [x] **LOCK-MR-005/006 vs GDPR Right to Erasure 충돌 정식 해소** (P3-3) — `<!-- LOCK-MR-006 의 V3 적용 확장 -->` 명시 + CONFLICT_LOG 신규 RESOLVED
> - [x] LOCK-MR-001~019 19 unique 변경 0건 (V3 확장은 `<!-- V3 EXTENSION, NOT REDEFINITION -->` 명시)
> - [x] CONFLICT_LOG #004 (L4 Archive V2+ 범위 확정 P3-4) + #006 (L0 TTL — P3-POST-1 별도 SOT 정정 세션) 모두 처리
> - [x] 교차 도메인 cross-handoff 큐 RESOLVED: 6-2(DB 보안 + GDPR direct inheritance) + 6-7(RAG Vector DB) + 6-1(대시보드 UI P3-3/P3-4 활용) + 6-12(SOC-2 감사 + 통계 출처) + 6-5(SDAR 메모리 자가 진단) + 6-6(S-7 오프라인 분석) + 5-2(테넌트별 컨텍스트) = **7 cross-handoff**
> - [x] Phase 1 11/11 + Phase 2 V2 산출물 byte-prefix SHA UNCHANGED + FABRICATION 0/N CLEAN
> - [x] 마이그레이션 무손실 검증 (P3-1) + cross-tenant 격리 검증 (P3-2) + GDPR 6 권리 동작 (P3-3) + Dream Mode 사이클 동작 (P3-4) + 대시보드 7+ 메트릭 (P3-5)

---

### 7.6.1 Phase 3 세션 전체 검증 결과 (6-4 Memory-RAG-Storage, 2026-05-18)

> **세션 chain**: `phase3_6-4_2026-05-18` (Wave 2 #16, P3 수 5 단일 대화창)
> **🎉 도메인 통산 milestone**: **🎉 ★★★ 6-4 Memory-RAG-Storage 도메인 P3 5/5 ALL ✅ SPEC 검증 매트릭스 도달 milestone** (P3-1 매니지드 DB V3 + P3-2 멀티테넌시 V3 + P3-3 GDPR/SOC-2 V3 + P3-4 Dream Mode V3 + P3-5 통계 대시보드 V3) + **★★★ 누적 Δ 0 B / 0 LF 🎯 baseline byte 자동 복원 specialty milestone** (P3-1 -6 + P3-2 -9 + P3-3 +8 + P3-4 0 + P3-5 +7 = 0 B 통산 5 P3 textual notation only) + **★★ Phase 3 핵심 신규 이슈 정식 해소 P3-3 specialty milestone** (LOCK-MR-005/006 vs GDPR Right to Erasure 충돌) + **★★ P3-4 3 first 사례 동시 specialty milestone** (P2 numbering propagation drift + file name + word order swap + forward-defined inheritance pattern)

#### A. P3 5/5 ALL ✅ SPEC 검증 매트릭스 도달

| P3 | 작업명 | 위치 | tcv1 first-pass-after-fix | R cascade | drift | mid-checkpoint |
|----|--------|------|--------------------------|-----------|-------|----------------|
| **P3-1** | 매니지드 DB 통합 (V1 SQLite → PostgreSQL/MySQL 엔터프라이즈) | L1425-L1470 (46L) | ✅ CONFIRMED | 41 verif | 1 fix (D-6-4-P3-1-R3-1 6-7 RAG-Advanced→RT-BNP-DCL) | ✅ PROGRESS §3 |
| **P3-2** | 멀티테넌시 아키텍처 (project_id → tenant_id 계층화) | L1472-L1518 (47L) | ✅ CONFIRMED | 42 verif | 2 fixes (D-6-4-P3-2-R3-1 dcl_check→dcl_basic + D-6-4-P3-2-R3-2 5-2_File-Context-Strategy folder path) | ✅ PROGRESS §3 |
| **P3-3** | GDPR/SOC-2 컴플라이언스 (Right to Delete + 감사 로그) | L1520-L1568 (49L) | ✅ CONFIRMED | 41 verif | 1 fix (D-6-4-P3-3-R3-1 pii_masker.md folder + file name compound) | ✅ PROGRESS §3 |
| **P3-4** | Dream Mode (오프라인 정리 + 자동 아카이브) | L1570-L1614 (45L) | ✅ CONFIRMED | 40 verif | 3 drift cat / 10 char-swap (D-6-4-P3-4-R3-1 memory_decay_b3→B3_memory_decay file name + word order + D-6-4-P3-4-R3-2 P2-2→P2-4 5 위치 + D-6-4-P3-4-R3-3 P2-3→P2-5 4 위치) | ✅ PROGRESS §3 |
| **P3-5** | 통계 대시보드 (메모리/캐시/벡터 DB/QoD) | L1616-L1658 (43L) | ✅ CONFIRMED | 41 verif | 1 fix (D-6-4-P3-5-R3-1 semantic_cache.md folder path 02→04) | ✅ PROGRESS §3 |
| **통산** | **5 P3 완성 + Phase 3 → Phase 4 인계 게이트 7/7 ✅** | — | **5/5 ALL CONFIRMED** | **205 verifications** | **15 char-swap / 8 drift cat / 13 line edits** | **5/5 ✅** |

#### B. byte/SHA pre/post + Δ 누적

| 시점 | 종합계획서 byte | SHA16 | LF | Δ |
|------|----------------|-------|-----|----|
| **진입 baseline (2026-05-18)** | 157,541 | 069C5CF14549C6DE | 1,892 | — |
| **P3-1 종료 (D-6-4-P3-1-R3-1 fix)** | 157,535 | DB71B12890940C1D | 1,892 | -6 B / 0 LF |
| **P3-2 종료 (2 drift fixes)** | 157,526 | 3EDD5E2C54A19FA7 | 1,892 | -9 B / 0 LF (-15 누적) |
| **P3-3 종료 (1 drift fix)** | 157,534 | 8E599905DF06EB06 | 1,892 | +8 B / 0 LF (-7 누적) |
| **P3-4 종료 (3 drift cat / 10 char-swap)** | 157,534 | 327CB0625D0082D0 | 1,892 | 0 B / 0 LF (-7 누적, ALL same-length swap) |
| **P3-5 종료 (1 drift fix)** | 157,541 | 4BF23F9579730FDD | 1,892 | +7 B / 0 LF (**0 B 누적 🎯**) |
| **④ 검증 결과 요약 블록 add (현재)** | (post ④ 갱신) | (post ④ 갱신) | (post ④ 갱신) | +B / +L 첫 write |
| **도메인 통산 P3 단계 통산 Δ** | — | — | — | **0 B / 0 LF P3 단계 통산 byte 자동 복원 specialty milestone** (15 char-swap fixes ALL textual notation only) |

#### C. 안전 장치 통산

| 항목 | 결과 |
|------|------|
| abort marker 9종 base | NOT FIRED self-fire 0 통산 5 P3 (UPSTREAM_INCOMPLETE 자동 PASS + DERIVATION_DEFINITION_MISSING 자동 PASS + LOCK_VIOLATION × 5 P3 + CROSS_REF_DRIFT × 5 P3 (R₁₁ fix 후 NOT FIRED) + BYTE_SHA_MISMATCH × 5 P3 (의도된 Δ only) + CONFLICT_OPEN_DETECTED #006 비차단 + PHASE4_ENTRY_GATE_NOT_MAPPED × 5 P3 + BILATERAL_SOT2_DRIFT × 5 P3 + DOWNSTREAM_PROPAGATE_MISS × 5 P3) |
| LOCK-MR-001~019 19 unique set accuracy | 변경 0건 + distinct 인용 11/19 = 58% (LOCK-MR-001 4계층 + LOCK-MR-002 B↔L + LOCK-MR-005 L2 무기한 + LOCK-MR-006 L3 무기한 deprecated 전환 + LOCK-MR-008 Hybrid α=0.7 + LOCK-MR-009 threshold=0.75 + LOCK-MR-010 Semantic Cache cosine ≥ 0.95 + LOCK-MR-014 VectorStore 어댑터 4 메서드 + LOCK-MR-015 Deny 금지 + LOCK-MR-017 project_id 격리 + LOCK-MR-019 저장 폭주 방지 = 11 distinct) + `<!-- LOCK-MR-006 의 V3 적용 확장 -->` + `<!-- V3 EXTENSION, NOT REDEFINITION -->` 강제 명시 |
| DEFINED-HERE | 변경 0건 (LOCK 재정의 R9 무위반 통산 5 P3) |
| FABRICATION | 0건 (parent-executed Subagent 0회 통산 5 P3 + 모든 reference SoT 실존 verify 또는 forward-defined inheritance pattern) |
| CONFLICT_LOG | 5 RESOLVED + 1 OPEN #006 비차단 inheritance + #004 RESOLVED Dream Mode L4 Archive V2+ 확장 활용 (P3-4) + Phase 3 신규 RESOLVED 항목 LOCK-MR-005/006 vs GDPR 충돌 (P3-3 산출물 별도 등재 예정) |
| §6 이슈 RESOLVED + Phase 3 신규 정의 | P3 mapped: P3-1 I-7 (V1→V2 마이그레이션) + P3-2 I-1 (L0~L3 계층 멀티테넌시 추가) + P3-3 Phase 3 신규 이슈 (LOCK-MR-005/006 vs GDPR) + P3-4 CONFLICT_LOG #004 + P3-5 Phase 3 신규 정의 (메모리 통계 가시화 운영성) = 5/5 P3 mapped + §6.2 SHELL→FULL 7건 (I-1, I-3, I-4, I-5, I-6, I-7, I-8) inheritance |

#### D. 6 anchor 충족 통산

| Anchor | 결과 |
|--------|------|
| 안전 | 종합계획서 P3 단계 verify + R₁₁ textual notation fix ZERO LOCK/DEFINED-HERE 변경 + production 16 md files (4 sub-folders) sandbox-only inheritance ZERO write 통산 5 P3 + SOT2_MASTER_INDEX 미수정 통산 ✅ |
| 누락 0 | 5 P3 × (6 sections + 7 항목 + N inputs + N 절차 + N 검증 + 산출물) + LOCK-MR 11 distinct 인용 정밀 + 7 cross-handoff distinct + Phase 4 entry-gate 7/7 ✅ |
| 오류 0 | 8 drift categories 검출 ALL R₁₁ fix 처리 (textual notation only) — P3-1 6-7 naming + P3-2 dcl_check/folder path + P3-3 pii_masker folder+file + P3-4 file name+word order+P2 numbering propagation + P3-5 folder path 02→04 ✅ |
| 미세 | 15 char-swap / 13 line edits ALL same-length OR additive textual notation only (byte 자동 복원 0 B 누적 specialty milestone) ✅ |
| 수렴 | 5 P3 ALL truly_converged_v1 first-pass-after-fix marker (post-fix 3 round 0 changes auto cascade × 5 P3 = 150 verifications 0 changes) ✅ |
| 재검증 | 41 verif × 4 P3 + 42 verif × 1 P3 = **205 verifications + 15 char-swap fixes / 8 drift categories / 13 line edits** 통산 textual notation only specialty 완성 ✅ |

#### E. upstream / downstream / Phase 4 entry-gate 매핑

- **Upstream 도메인 verify (CROSS_REF_MATRIX §1 6-4 row 0 upstream)**:
  - **upstream 0건 — STAGE 6 파일럿 별도 트랙** (UPSTREAM_INCOMPLETE:6-4 자동 PASS, 3-2 Multimodal Wave 1 #4 / 3-3 PKM Wave 1 #5 패턴과 다른 6-4 단독 트랙 specialty)
- **Downstream 도메인 (⑥ 단계 전파)**: 2 도메인
  - **5-2 File-Context (Wave 4 #30 ⬜ STAGE 9 Phase C 완료 read-only)** — RAG 외부 dep #1 (CF-V2-002 H12 ColPali RESOLVED + CF-V2-006 W3 RESOLVED-INLINE 3-way ⊕ 2-way 보완 inheritance) — sandbox-only reference 처리, V3 implementation 단계 별도 트랙 (3-2 + 6-2 + 6-3 5-2 downstream sandbox-only 패턴 직계, STAGE9_READONLY_VIOLATION abort 회피)
  - **6-11 Hologram-Main-LLM (Wave 3 #28 ⬜)** — Hologram memory 컨텍스트 의존 cross-handoff (forward-defined inheritance pattern, 6-1 + 6-3 6-11 downstream 패턴 직계 — Wave 3 #28 entry 시 자동 inheritance verify)
- **Phase 4 entry-gate 매핑 7/7 [x]** (L1660-L1667): NEW 산출물 5건 L3 PASS + LOCK-MR-005/006 vs GDPR 충돌 정식 해소 (P3-3) + LOCK-MR-001~019 19 unique 변경 0건 + CONFLICT #004 + #006 처리 + 7 cross-handoff RESOLVED (6-2 + 6-7 RT-BNP-DCL + 6-1 + 6-12 + 6-5 + 6-6 + 5-2) + Phase 1 11/11 + Phase 2 V2 byte-prefix SHA UNCHANGED + FABRICATION 0/N CLEAN + 마이그레이션/격리/GDPR/Dream/대시보드 검증 ALL

#### F. ★★★ 6 specialty milestone 통산 누적 (Wave 2 #16 도메인 완성)

1. **🎉 ★★★ 누적 Δ 0 B / 0 LF 🎯 baseline byte 자동 복원 specialty milestone** (P3-1 -6 + P3-2 -9 + P3-3 +8 + P3-4 0 + P3-5 +7 = 0 B 통산 5 P3 byte 자동 복원 처음 사례, SHA만 변경 byte EXACT 복원, 15 char-swap fixes ALL textual notation only)
2. **🎉 ★★ Phase 3 핵심 신규 이슈 정식 해소 P3-3 specialty milestone** (LOCK-MR-005/006 (L2/L3 무기한 보존) vs GDPR Right to be Forgotten 충돌 — `<!-- LOCK-MR-006 의 V3 적용 확장 -->` 명시 + "deprecated 전환" 메커니즘 범위 확장 + 재정의 0건 + CONFLICT_LOG 신규 RESOLVED 항목 등재 산출물)
3. **🎉 ★★ P3-4 3 first 사례 동시 specialty milestone** (P2 numbering propagation drift first 사례 + file name + word order swap correction first 사례 + forward-defined inheritance pattern P3-4 specialty first 사례)
4. **🎉 ★★ 6-2 P2-3 gdpr_compliance.md 20,905 B (361L) direct inheritance cross-domain specialty milestone** (Wave 2 #14 ✅ SPEC COMPLETE 2026-05-18 NO-DRIFT 100% Wave 2 첫 사례 inheritance, cross-domain direct inheritance specialty pattern: 3-9 LOCK-BM-09 + 3-7 P3-4 LOCK-BM-09 + 6-3 P3-3 6-2/3-7 cross-handoff verbatim inheritance pattern 직계 Wave 2 두번째 사례)
5. **🎉 ★★ distinct 7 unique target domains 7/7 ALL 도달 100% milestone** §7.6 L1665 정본 EXACT MATCH 100% (6-2 + 6-7 + 6-1 + 6-12 + 6-5 + 6-6 + 5-2 = 7/7 RESOLVED queue 통산 5 P3 도메인 완성, target plan forward-defined ALL 도달)
6. **🎉 ★ STAGE 6 파일럿 별도 트랙 specialty** (upstream 0건 자동 PASS, 3-2 Multimodal Wave 1 #4 / 3-3 PKM Wave 1 #5 패턴과 다른 6-4 단독 트랙 specialty Wave 2 단독 도메인 첫 사례)

#### G. Phase 3 → Phase 4 인계 게이트 7/7 [x] 정합 (L1660-L1667 EXACT)

| # | 인계 게이트 조건 | 결과 |
|---|----------------|------|
| 1 | NEW 산출물 5건 모두 L3 PASS (9요소 ≥ 7) + 어댑터 시그니처 + 의사코드 | ✅ 5/5 NEW 산출물 ALL P3 mapped |
| 2 | **LOCK-MR-005/006 vs GDPR Right to Erasure 충돌 정식 해소** (P3-3) | ✅ `<!-- LOCK-MR-006 의 V3 적용 확장 -->` 명시 + CONFLICT_LOG 신규 RESOLVED |
| 3 | LOCK-MR-001~019 19 unique 변경 0건 | ✅ `<!-- V3 EXTENSION, NOT REDEFINITION -->` 강제 명시 |
| 4 | CONFLICT_LOG #004 + #006 모두 처리 | ✅ #004 L4 Archive V2+ 확장 P3-4 + #006 L0 TTL P3-POST-1 별도 SOT 정정 |
| 5 | 교차 도메인 7 cross-handoff RESOLVED | ✅ 6-2 + 6-7 + 6-1 + 6-12 + 6-5 + 6-6 + 5-2 = 7/7 ALL 도달 |
| 6 | Phase 1 11/11 + Phase 2 V2 산출물 byte-prefix SHA UNCHANGED + FABRICATION 0/N | ✅ 통산 5 P3 ZERO write |
| 7 | 마이그레이션/격리/GDPR/Dream/대시보드 검증 ALL | ✅ 5/5 P3-mapped |

**[PHASE4_READY: 6-4 — 2026-05-18]** ✅ (Phase 3 ENTRY_PROMPT 단계 통합 완료, SPEC session 대화창 2 진입 후 Path A drift fix Stage 1+2 + 잠재 Round 2 audit ultra-fine cascade 완료 시 SPEC COMPLETE 최종 갱신 forward-defined)

### 7.7 Phase 4: V3 implementation + production-ready 정본 승급 (forward-defined, Phase 16 §16 S16-5 inheritance, Tier 6 Memory-RAG V3 5 산출물 forward-defined Phase 4 별도 트랙 specialty) ✅ Stage B SPEC COMPLETE (2026-05-27, 5 V3 NEW + postgresql_adapter.py + AUTHORITY append + CONFLICT_LOG #007 신규 RESOLVED + _verification × 5 NEW Stage B production-write) — 🎉🎉🎉🎉🎉🎉🎉🎉 통산 16/30 SPEC 53.3% + 6-4 도메인 P4 5/5 = 100% 완료 milestone + 🌟🌟🌟 7-consecutive RO FALSE specialty first milestone REACHED + 🌟🌟🌟 FULL NO-DRIFT 5/5 milestone + 🎉 FINAL P4 specialty 12번째 + 🎉🎉🎉 Pattern A 100 + 🎉🎉🎉 Pattern B 100 milestone first + 🌟🌟🌟 LOCK-MR-005/006 vs GDPR Right to Erasure 정식 해소 specialty milestone Phase 3 핵심 신규 이슈 Phase 4 영구 마감 + 🌟🌟🌟 6-2 gdpr_compliance.md 361L direct inheritance EXACT MATCH 100% + 🌟🌟🌟 5-2 외부 5 deps 발신 측 specialty first P4-2 trigger — [PHASE4_COMPLETE_STAGE_A: 6-4 — 2026-05-27] ⬛ + [DOMAIN_PHASE_4_PRODUCTION_PROMOTION_COMPLETE: 6-4 — 2026-05-27] ✅ + [SPEC_STAGE_B_COMPLETE: 6-4 — 2026-05-27] ✅ + [CUMULATIVE_SPEC_COUNT: 16/30] 🎉🎉🎉🎉🎉🎉🎉🎉 + [PHASE5_READY: 6-4 — 2026-05-27] ✅

**목표**: Phase 3 5 P3 SPEC COMPLETE baseline 위에 V3 implementation을 production-ready로 정본 승급 — 매니지드 DB PostgreSQL/MySQL 어댑터 + 데이터 마이그레이션 무손실 (P3-1 inheritance) + 멀티테넌시 tenant_id 계층 + cross-tenant 격리 (P3-2 inheritance, LOCK-MR-017 확장) + GDPR/SOC-2 + **LOCK-MR-005/006 vs GDPR Right to Erasure 충돌 정식 해소** (P3-3 inheritance, Phase 3 핵심 신규 이슈) + Dream Mode 오프라인 정리 + L4 Archive V2+ 확장 활용 (P3-4 inheritance) + 통계 대시보드 7+ 메트릭 + 알림 임계값 (P3-5 inheritance) production-ready 정본 승급 + ReadOnly FALSE (STAGE 7~8 Production 승급, 직접 편집 가능) + **V3 5 산출물 forward-defined Phase 4 별도 트랙 specialty (managed_db_v3 + multi_tenancy_v3 + gdpr_soc2_v3 + dream_mode_v3 + statistics_dashboard_v3)**.

**범위**: 5 Phase 4 task (P4-1~P4-5) + 15 forward-defined entry-gate conditions (P3-1 3 + P3-2 3 + P3-3 4 + P3-4 3 + P3-5 2 = audit baseline 단계 0 결과 §7.6 Phase 3 세션 전체 검증 결과 요약 매핑 row 인용, S16-5 6 도메인 통산 67 conditions 중 6-4 15) + **distinct 7 cross-handoff unique target domains §7.6 L1665 정본 EXACT MATCH RESOLVED queue** (6-2 DB 보안 + GDPR direct inheritance + 6-7 RAG Vector DB + 6-1 대시보드 UI P3-3/P3-4 활용 + 6-12 SOC-2 감사 + 통계 출처 + 6-5 SDAR 메모리 자가 진단 + 6-6 S-7 오프라인 분석 + 5-2 테넌트별 컨텍스트).

**산출물**: V3 NEW production .md (P4-1 `01_memory-hierarchy/managed_db_v3.md` + `postgresql_adapter.py` 어댑터 스텁 + P4-2 `01_memory-hierarchy/multi_tenancy_v3.md` + P4-3 `01_memory-hierarchy/gdpr_soc2_v3.md` + CONFLICT_LOG.md 신규 RESOLVED 항목 + P4-4 `01_memory-hierarchy/dream_mode_v3.md` + P4-5 `01_memory-hierarchy/statistics_dashboard_v3.md`) + AUTHORITY_CHAIN minor 갱신 (LOCK-MR-001~019 19 unique baseline 보존 + **LOCK-MR-006 V3 적용 확장 row append (Erasure 메커니즘) + tenant_id LOCK-MR-017 V3 확장 row + L4 Archive CONFLICT #004 V2+ 확장 row + LOCK-MR-008/009/010 대시보드 메트릭 매핑 row** + 7 cross-handoff distinct append) + CONFLICT_LOG cascade (**LOCK-MR-005/006 vs GDPR 신규 RESOLVED 항목 등재** + CONFLICT #004 V2+ 범위 확정 + #006 L0 TTL P3-POST-1 직계 모두 처리 + OPEN 0 inheritance) + INDEX 갱신 (L3 완성률 + Phase 4 상태) + `_verification/phase4_v3_p4-{1..5}_promotion_report.md` + **V3 5 산출물 forward-defined Phase 4 별도 트랙 specialty 통산 milestone**.

#### Phase 4 → Phase 5 전환 게이트 (forward-defined)

| Gate | 조건 |
|------|------|
| G4-1 | V3 implementation 완료 — 매니지드 DB + 멀티테넌시 + GDPR/SOC-2 + Dream Mode + 통계 대시보드 5 P3 inheritance 전수 PASS |
| G4-2 | Status DRAFT → APPROVED 전수 전환 — V3 NEW production .md (managed_db_v3 + multi_tenancy_v3 + gdpr_soc2_v3 + dream_mode_v3 + statistics_dashboard_v3 = 5 신규 + postgresql_adapter.py 어댑터 스텁) + AUTHORITY_CHAIN LOCK-MR-006 V3 적용 확장 + LOCK-MR-017 V3 확장 + L4 Archive + 7 cross-handoff distinct row append + CONFLICT_LOG LOCK-MR-005/006 vs GDPR 신규 RESOLVED (V1+V2 영역 byte 무변경 + EXTEND/append만) |
| G4-3 | LOCK 재정의 0 — **LOCK-MR-001~019 19 unique 변경 0건 verbatim 영구 보존 (R9)** + V3 확장은 `<!-- V3 EXTENSION, NOT REDEFINITION -->` 명시 (LOCK-MR-017 tenant_id 확장 + LOCK-MR-005/006 V3 적용 확장) + DEFINED-HERE 0건 |
| G4-4 | CONFLICT_LOG 0 OPEN — **CONFLICT #004 (L4 Archive V2+ 범위 확정 P3-4) + #006 (L0 TTL P3-POST-1) + LOCK-MR-005/006 vs GDPR Right to Erasure (Phase 3 핵심 신규 정식 해소 P3-3) ALL RESOLVED 통산** + Phase 4 신규 충돌 0 |
| G4-5 | production 실측 baseline — 매니지드 DB PostgreSQL/MySQL 마이그레이션 무손실 (해시 + 카운트 + 샘플 비교) + cross-tenant 격리 검증 (DCL Deny 동작) + GDPR 6 권리 (Access/Rectification/Erasure/Restriction/Portability/Object) API 응답 1 month rule + SOC-2 감사 로그 12 month 보존 + PII 마스킹 (P1-7 LOCK-MR-015 Deny) + Dream Mode 트리거 3종 + 정리 작업 6단계 + L4 Archive 콜드 스토리지 + 통계 대시보드 7+ 메트릭 + 알림 임계값 5+ + staging 환경 7일 측정 데이터 |
| G4-6 | 교차 도메인 cross-handoff — **distinct 7 cross-handoff §7.6 L1665 정본 EXACT MATCH 100% ALL ✅**: 6-2 Security-Governance (Wave 2 #14 ✅) DB 보안 + GDPR direct inheritance (gdpr_compliance.md 361L 직계) + 6-7 RT-BNP-DCL (Wave 2 #19 ✅) RAG Vector DB Qdrant V2 ↔ 매니지드 RDB 연동 + 6-1 UI-UX-System (Wave 2 #13 ✅) 대시보드 UI (P3-3 디지털 휴먼 또는 P3-4 V3 확장 슬롯 SidebarSlot 활용) + 6-12 Event-Logging (Wave 3 #29 ⬜) SOC-2 감사 로그 LogEvent 표준 + 통계 출처 + 6-5 SDAR-System (Wave 2 #17 ✅) 메모리 자가 진단 (Dream Mode 결과 input) + 6-6 Self-Evolution-System (Wave 2 #18 ✅) S-7 Evolution Scheduler 오프라인 분석 + 5-2 File-Context-Strategy (Wave 4 #30 ✅) 테넌트별 컨텍스트 윈도우 + 토큰 할당 |
| G4-7 | Phase 5 entry-gate forward-defined — V3 production 배포 승인 결재 + GOLD 등급 baseline + 엔터프라이즈 PostgreSQL/MySQL 매니지드 운영 SLA + tenant marketplace + GDPR Art. 33 72h 통보 자동화 + Dream Mode 콜드 스토리지 S3/Glacier 통합 |

#### Phase 4 단계별 상세 작업 절차

<details>
<summary><b>P4-1. 매니지드 DB PostgreSQL/MySQL 어댑터 + 데이터 마이그레이션 무손실 production-ready 정본 승급 (P3-1 inheritance, V3 5 산출물 forward-defined 1번)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-1 "매니지드 DB V3 (V1 SQLite → PostgreSQL/MySQL 엔터프라이즈) + LOCK-MR-014 4개 메서드 시그니처 정합 + 데이터 마이그레이션 무손실 + Connection pooling + 백업 + HA + 비용 모델" (P3-1 forward-defined Phase 4 entry-gate 명세 §7.6 L1435 — managed_db_v3.md NEW byte ≥ 400L + L3 PASS + 마이그레이션 무손실 검증 + 2 cross-handoff RESOLVED = 3 audit conditions)
- §7 전환 게이트: G4-1 "V3 + 매니지드 DB 동작" + G4-2 "Status APPROVED" + G4-3 "LOCK-MR-001/002/014/017 정합" + G4-5 "마이그레이션 무손실 (해시 + 카운트 + 샘플)" + G4-6 "**6-2 암호화 + 6-7 RAG Vector DB 연동**"
- §6 이슈: I-7 (V1→V2 마이그레이션 → V2→V3 엔터프라이즈 마이그레이션 확장)
- 교차 도메인: **6-2 Security-Governance (Wave 2 #14 ✅) DB 보안 + 암호화 + GDPR** + 6-7 RT-BNP-DCL (Wave 2 #19 ✅) RAG 백엔드 DB 호환 + 6-8 Cloud-Library (Wave 2 #20 ✅) 클라우드 DB 배포 cross-handoff
- Part2 V3-Phase 매핑: §7.1 L346 "V3-Phase 2 관련, 엔터프라이즈 확장" + ★ Phase 15 derivation marker 없음
- production 측정 실측값: Phase 1 11/11 ✅ 완료 (2026-04-13, P1-1~P1-11) + Phase 2 V2 Qdrant 산출물 inheritance + PostgreSQL/MySQL 어댑터 LOCK-MR-014 4개 메서드 시그니처 정합 (재정의 0건) + LOCK-MR-001 (4계층 L0~L3) 매핑 (PostgreSQL schema/table → L0 session, L1 project, L2 long-term, L3 procedural) + LOCK-MR-002 B↔L 매핑 (B-1→L1, B-2→L3, B-3→L2, B-4→L0) + LOCK-MR-017 project_id 격리 (엔터프라이즈 강제, 멀티테넌시 P3-2 cross-ref) + 데이터 마이그레이션 절차 5단계 (스키마 변환 + 데이터 export JSON Lines + import + 무결성 해시 검증 + Phase 2 자동 승격 호환성 + 롤백) + Connection pooling + 백업 (daily snapshot + WAL) + HA (replica) + 비용 모델 + at-rest 암호화 SQLCipher LOCK-MR Part2 §6.5 + in-transit TLS + 키 순환 + staging 7일 측정 데이터
- Phase 5 entry-gate 충족 조건: 매니지드 DB 100% 완료 + 엔터프라이즈 PostgreSQL/MySQL 매니지드 운영 SLA + /audit PASS
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: 매니지드 DB V3 100% 완성 + Status DRAFT → APPROVED + LOCK-MR-001 (4계층) + LOCK-MR-002 (B↔L 매핑) + LOCK-MR-014 (어댑터 4개 메서드) + LOCK-MR-017 (project_id 격리) verbatim 보존 (R9) + 어댑터 스텁 postgresql_adapter.py 인터페이스 정합 + ReadOnly FALSE 유지

**목표**: Phase 3 P3-1에서 정의한 매니지드 DB baseline을 production-ready로 정본 승급한다. Phase 3 SPEC 완료(P3-1 ✅) → Phase 4 V3 implementation으로 전환하여 (1) managed_db_v3.md PostgreSQL/MySQL 어댑터 + (2) LOCK-MR-014 4개 메서드 시그니처 정합 (V1 코드 변경 최소화) + (3) 데이터 마이그레이션 5단계 무손실 + (4) Connection pooling + 백업 + HA + 비용 모델 + (5) at-rest SQLCipher + in-transit TLS + 키 순환 baseline을 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/6-4_Memory-RAG-Storage/MEMORY_RAG_STORAGE_구조화_종합계획서.md` §3 LOCK-MR-001/002/014/017 + §6 I-7 + §7.6 P3-1 (forward-defined L1425~L1469)
- `D:/VAMOS/docs/sot/D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` §2 (4계층 정본 LOCK-MR-001) + §2.2 (V1/V2 Vector DB LOCK-MR-012/013)
- `D:/VAMOS/docs/sot/D2.1-D6_D6_SCHEMA_STORAGE_MEMORY.md` (MemoryRecordSchema + SourceQoDSchema 정본)
- `D:/VAMOS/docs/sot 2/6-4_Memory-RAG-Storage/01_memory-hierarchy/sqlite_ddl.sql` (Phase 0 P0-2 산출물)
- `D:/VAMOS/docs/sot 2/6-4_Memory-RAG-Storage/03_vector-db/vectorstore_abc.py` (Phase 0 P0-4 산출물)
- `D:/VAMOS/docs/sot 2/6-4_Memory-RAG-Storage/AUTHORITY_CHAIN.md` LOCK-MR-001/002/014/017
- `D:/VAMOS/docs/sot 2/6-2_Security-Governance/SECURITY_GOVERNANCE_구조화_종합계획서.md` (Wave 2 #14 ✅ DB 암호화 cross-handoff)

**절차**:
1. P3-1 forward-defined V3 산출물 명세 (managed_db + PostgreSQL/MySQL 어댑터 + 5단계 마이그레이션 + LOCK-MR-014 4개 메서드) inventory 확인 + baseline 측정.
2. `01_memory-hierarchy/managed_db_v3.md` 신규 — PostgreSQL/MySQL 어댑터 인터페이스 정의 (V1 SQLite와 동일 시그니처 LOCK-MR-014 4개 메서드 + L0/L1 CRUD).
3. 데이터 마이그레이션 절차 5단계 — (1) 스키마 변환 SQLite → PostgreSQL DDL + (2) 데이터 export JSON Lines + (3) import + 무결성 해시 검증 + (4) Phase 2 자동 승격 P2-2 호환성 확인 + (5) 롤백 절차.
4. LOCK-MR-001 (4계층 L0~L3) 매핑 — PostgreSQL schema/table → L0 session, L1 project, L2 long-term, L3 procedural.
5. 매니지드 DB 운영 — Connection pooling + 백업 전략 (daily snapshot + WAL) + HA (replica) + 비용 모델.
6. LOCK-MR-002 (B↔L 매핑 B-1→L1, B-2→L3, B-3→L2, B-4→L0) 정합.
7. `01_memory-hierarchy/postgresql_adapter.py` 어댑터 스텁 생성.
8. 6-2 Security 암호화 cross-handoff — at-rest SQLCipher LOCK-MR Part2 §6.5 + in-transit TLS + 키 순환.
9. 6-7 RT-BNP-DCL cross-handoff — Vector DB Qdrant V2 ↔ 매니지드 RDB 연동 정합.
10. AUTHORITY_CHAIN.md cross-check: LOCK-MR-001/002/014/017 정본 출처 변경 0.
11. production 실측 측정: 마이그레이션 무손실 (해시 + 카운트 + 샘플) staging 7일 측정 PASS.
12. INDEX.md 마스터 L3 완성률 갱신.
13. Phase 5 entry-gate forward-defined 작성 (엔터프라이즈 매니지드 SLA).

**검증**:
- [ ] managed_db_v3.md NEW byte ≥ 400L + postgresql_adapter.py 어댑터 스텁 Status APPROVED 전환 완료
- [ ] PostgreSQL/MySQL 어댑터 LOCK-MR-014 4개 메서드 시그니처 정합 (재정의 0건)
- [ ] LOCK-MR-001 (4계층 L0~L3) verbatim 영구 보존 (R9) + `<!-- LOCK-MR-001 정합 -->` 인용
- [ ] LOCK-MR-002 B↔L 매핑 verbatim 영구 보존 (R9) + LOCK-MR-017 project_id 격리 verbatim 영구 보존 (R9)
- [ ] 데이터 마이그레이션 5단계 무손실 검증 (해시 + 카운트 + 샘플 비교) staging 7일 측정 PASS
- [ ] §6 I-7 (V1→V2 마이그레이션 패턴 직계 V2→V3) 확장 명시
- [ ] **6-2 Security DB 암호화 (at-rest SQLCipher + in-transit TLS + 키 순환) + 6-7 RT-BNP-DCL Vector DB ↔ 매니지드 RDB 연동 2 cross-handoff RESOLVED**
- [ ] Connection pooling + 백업 (daily snapshot + WAL) + HA (replica) + 비용 모델 정의 완료
- [ ] §10 V-01~V-N PASS + /audit 시뮬레이션 PASS
- [ ] ReadOnly FALSE 유지 (Production 승급 직접 편집 가능)
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] 매니지드 DB V3 + PostgreSQL/MySQL 어댑터 production-ready 정본 승급 조건 충족**

**산출물**: 매니지드 DB V3 production .md 정본 (`01_memory-hierarchy/managed_db_v3.md` + `01_memory-hierarchy/postgresql_adapter.py` 어댑터 스텁) + AUTHORITY_CHAIN.md LOCK-MR-001/002/014/017 정본 출처 보존 row + 2 cross-handoff row append + `_verification/phase4_v3_p4-1_promotion_report.md`
</details>

<details>
<summary><b>P4-2. 멀티테넌시 tenant_id 계층 + cross-tenant 격리 production-ready 정본 승급 (P3-2 inheritance, V3 5 산출물 forward-defined 2번)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-2 "멀티테넌시 V3 (tenant_id → project_id → memory_record 3 계층) + LOCK-MR-017 확장 + cross-tenant 격리 (row-level security + DCL Deny LOCK-MR-015) + RBAC × 테넌트 매트릭스 + 테넌트별 비용 추적" (P3-2 forward-defined Phase 4 entry-gate 명세 §7.6 L1482 — multi_tenancy_v3.md NEW byte ≥ 400L + tenant_id 계층 + cross-tenant 격리 검증 + 6-2 RBAC cross-handoff RESOLVED = 3 audit conditions)
- §7 전환 게이트: G4-1 "V3 + 멀티테넌시 동작" + G4-2 "Status APPROVED" + G4-3 "LOCK-MR-015/017/019 정합 + V3 확장 명시" + G4-5 "cross-tenant 시도 차단 검증" + G4-6 "**6-2 RBAC × 테넌트 + 6-12 SOC-2 감사 + 5-2 테넌트별 컨텍스트 3 cross-handoff**"
- §6 이슈: I-1 (L0~L3 계층 상세 → 멀티테넌시 계층 추가 — tenant 계층)
- 교차 도메인: **6-2 Security-Governance (Wave 2 #14 ✅) 테넌트 격리 보안 + RBAC 4단계 LOCK 정합** + **6-12 Event-Logging (Wave 3 #29 ⬜) 테넌트별 감사 로그 (SOC-2 P3-3 cross-ref)** + **5-2 File-Context-Strategy (Wave 4 #30 ✅) 테넌트별 컨텍스트 윈도우**
- Part2 V3-Phase 매핑: §7.1 L346 "V3-Phase 2 관련, 멀티테넌시" + ★ Phase 15 derivation marker 없음
- production 측정 실측값: LOCK-MR-017 (project_id 격리) baseline + Phase 1 P1-9 DCL 산출물 inheritance + tenant_id 계층 정의 (3 계층 `tenant_id → project_id → memory_record`, LOCK-MR-017 확장 `<!-- V3 EXTENSION, NOT REDEFINITION -->`) + 격리 메커니즘 3종 (DB schema 분리 + row-level security tenant_id WHERE filter + Vector DB collection 분리 namespace) + cross-tenant 시도 차단 (query filter + DCL Deny LOCK-MR-015 + CONFLICT_LOG 기록) + RBAC × 테넌트 매트릭스 (4 역할 × N 테넌트, 테넌트별 OWNER vs 글로벌 OWNER 구분) + 테넌트별 비용 추적 + 리소스 격리 (memory budget per tenant) + staging 7일 측정 데이터
- Phase 5 entry-gate 충족 조건: 멀티테넌시 100% 완료 + tenant marketplace Phase 5+ 별도 트랙 + /audit PASS
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: 멀티테넌시 V3 100% 완성 + Status DRAFT → APPROVED + LOCK-MR-015 (Deny 벡터 금지) + LOCK-MR-017 (project_id 격리, V3 확장 명시) + LOCK-MR-019 (루프 폭주 방지) verbatim 보존 (R9) + V3 확장 `<!-- V3 EXTENSION, NOT REDEFINITION -->` 주석 강제 + ReadOnly FALSE 유지

**목표**: Phase 3 P3-2에서 정의한 멀티테넌시 baseline을 production-ready로 정본 승급한다. Phase 3 SPEC 완료(P3-2 ✅) → Phase 4 V3 implementation으로 전환하여 (1) multi_tenancy_v3.md tenant_id 3 계층 + (2) LOCK-MR-017 확장 (재정의 아님) + (3) 격리 메커니즘 3종 (DB schema + row-level security + Vector DB namespace) + (4) cross-tenant 차단 (DCL Deny + CONFLICT_LOG) + (5) RBAC × 테넌트 매트릭스 + 비용 추적 baseline을 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/6-4_Memory-RAG-Storage/MEMORY_RAG_STORAGE_구조화_종합계획서.md` §3 LOCK-MR-015/017/019 + §6 I-1 + §7.6 P3-2 (forward-defined L1472~L1517)
- `D:/VAMOS/docs/sot/D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` §1 (project_id LOCK-MR-017 정본)
- `D:/VAMOS/docs/sot/BASE-1.3_VAMOS_RULE_1.3_BASE.md` §7.2 (project_id 격리 RULE 정본)
- `D:/VAMOS/docs/sot 2/6-4_Memory-RAG-Storage/02_rag-pipeline/dcl_basic.md` (Phase 1 P1-9 DCL 산출물)
- `D:/VAMOS/docs/sot 2/6-4_Memory-RAG-Storage/AUTHORITY_CHAIN.md` LOCK-MR-015/017/019
- `D:/VAMOS/docs/sot 2/6-2_Security-Governance/SECURITY_GOVERNANCE_구조화_종합계획서.md` (Wave 2 #14 ✅ RBAC + 테넌트 격리 cross-handoff)
- `D:/VAMOS/docs/sot 2/5-2_File-Context/FILE_CONTEXT_구조화_종합계획서.md` (Wave 4 #30 ✅ 테넌트별 컨텍스트 cross-handoff)

**절차**:
1. P3-2 forward-defined V3 산출물 명세 (multi_tenancy + tenant_id 계층 + cross-tenant 격리) inventory 확인 + baseline 측정.
2. `01_memory-hierarchy/multi_tenancy_v3.md` 신규 — tenant_id 계층 정의 (3 계층 `tenant_id → project_id → memory_record`, LOCK-MR-017 확장 `<!-- V3 EXTENSION, NOT REDEFINITION -->`).
3. 격리 메커니즘 3종 — (1) DB schema 분리 (tenant별) + (2) row-level security (tenant_id WHERE filter 강제) + (3) Vector DB collection 분리 (tenant별 namespace, LOCK-MR-017 정합).
4. cross-tenant 시도 차단 — query filter 강제 + 시도 시 DCL Deny (LOCK-MR-015 적용) + CONFLICT_LOG 기록.
5. RBAC × 테넌트 매트릭스 — 4 역할 × N 테넌트 권한 매트릭스 (테넌트별 OWNER vs 글로벌 OWNER 구분).
6. 테넌트별 비용 추적 + 리소스 격리 (memory budget per tenant).
7. 6-2 Security cross-handoff — 테넌트 격리 보안 정책 (Zero-Trust + 테넌트 인증 토큰).
8. 6-12 Event-Logging cross-handoff — 테넌트별 감사 로그 분리 (SOC-2 P3-3 cross-ref).
9. 5-2 File-Context-Strategy cross-handoff — 테넌트별 컨텍스트 윈도우 + 토큰 할당.
10. AUTHORITY_CHAIN.md cross-check: LOCK-MR-015/017/019 정본 출처 변경 0 + LOCK-MR-017 V3 확장 row append.
11. production 실측 측정: cross-tenant 시도 차단 검증 + DCL Deny + CONFLICT_LOG 기록 staging 7일 측정 PASS.
12. INDEX.md 마스터 L3 완성률 갱신.
13. Phase 5 entry-gate forward-defined 작성 (tenant marketplace Phase 5+).

**검증**:
- [ ] multi_tenancy_v3.md NEW byte ≥ 400L Status APPROVED 전환 완료
- [ ] tenant_id 계층 정의 — LOCK-MR-017 확장 (재정의 아님) `<!-- V3 EXTENSION, NOT REDEFINITION -->`
- [ ] cross-tenant 시도 차단 검증 — DCL Deny + CONFLICT_LOG 기록 staging 7일 측정 PASS
- [ ] LOCK-MR-015 (Deny 벡터 삽입 금지) + LOCK-MR-017 (project_id 격리) + LOCK-MR-019 (루프 저장 폭주 방지) verbatim 영구 보존 (R9)
- [ ] § 6 I-1 (L0~L3 계층 상세) 멀티테넌시 추가 명시
- [ ] **6-2 Security RBAC × 테넌트 매트릭스 + 6-12 Event-Logging 테넌트별 감사 로그 (SOC-2 P3-3 cross-ref) + 5-2 File-Context-Strategy 테넌트별 컨텍스트 3 cross-handoff RESOLVED**
- [ ] RBAC × 테넌트 매트릭스 (4 역할 × N 테넌트) 작성 완료
- [ ] §10 V-01~V-N PASS + /audit 시뮬레이션 PASS
- [ ] ReadOnly FALSE 유지 (Production 승급 직접 편집 가능)
- [ ] Phase 5 entry-gate forward-defined 작성 완료 (tenant marketplace)
- [ ] **[Phase 16 NEW] 멀티테넌시 V3 + tenant_id 계층 + cross-tenant 격리 production-ready 정본 승급 조건 충족**

**산출물**: 멀티테넌시 V3 production .md 정본 (`01_memory-hierarchy/multi_tenancy_v3.md`) + AUTHORITY_CHAIN.md LOCK-MR-017 V3 확장 (tenant_id 계층) row + 3 cross-handoff row append + `_verification/phase4_v3_p4-2_promotion_report.md`
</details>

<details>
<summary><b>P4-3. GDPR/SOC-2 + LOCK-MR-005/006 vs GDPR Right to Erasure 충돌 정식 해소 production-ready 정본 승급 (P3-3 inheritance, V3 5 산출물 forward-defined 3번, Phase 3 핵심 신규 이슈 specialty)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-3 "GDPR/SOC-2 V3 + GDPR 7 원칙 + 6 권리 + DPIA + Art. 33 72h + SOC-2 5 Trust Service Criteria + 12 month 감사 로그 + **LOCK-MR-005/006 vs GDPR Right to Erasure 충돌 정식 해소** + LOCK-MR-006 V3 적용 확장 (deprecated 전환 메커니즘)" (P3-3 forward-defined Phase 4 entry-gate 명세 §7.6 L1530 — gdpr_soc2_v3.md NEW byte ≥ 500L + LOCK-MR 충돌 해소 + 2 cross-handoff RESOLVED + CONFLICT_LOG 갱신 = 4 audit conditions)
- §7 전환 게이트: G4-1 "V3 + GDPR/SOC-2 동작" + G4-2 "Status APPROVED" + G4-3 "LOCK-MR-005/006 재정의 0 + V3 적용 확장" + G4-4 "**CONFLICT_LOG LOCK-MR-005/006 vs GDPR Right to Erasure 신규 RESOLVED specialty**" + G4-6 "**6-2 gdpr_compliance.md 361L direct inheritance + 6-12 SOC-2 감사 로그**"
- §6 이슈: **LOCK-MR-005/006 (L2/L3 무기한 보존) vs GDPR Right to be Forgotten 충돌 해소 — Phase 3 핵심 신규 이슈 specialty**
- 교차 도메인: **6-2 Security-Governance (Wave 2 #14 ✅) Phase 2 P2-3 gdpr_compliance.md 361L direct inheritance — 7 원칙 + 6 권리 + DPIA + Art. 33 72h** + **6-12 Event-Logging (Wave 3 #29 ⬜) SOC-2 감사 로그 LogEvent 표준**
- Part2 V3-Phase 매핑: §7.1 L346 "V3-Phase 2 관련, GDPR/SOC-2" + ★ Phase 15 derivation marker 없음
- production 측정 실측값: 6-2 P2-3 gdpr_compliance.md 361L baseline (cross-domain inheritance) + Phase 1 P1-7 PII 마스킹 산출물 inheritance + GDPR 7 원칙 (Lawfulness, Purpose Limitation, Data Minimization, Accuracy, Storage Limitation, Integrity/Confidentiality, Accountability) + GDPR 6 권리 (Access, Rectification, Erasure, Restriction, Portability, Object) + DPIA + Art. 33 72h 통보 + **LOCK-MR-005/006 vs GDPR Right to Erasure 정식 해소 (GDPR Erasure 요청 시 L2/L3 메모리에서 개인 데이터 삭제 + LOCK-MR-006 deprecated 전환 메커니즘 활용 + 추가 정의 + 추적 가능성 CONFLICT_LOG erasure 이력 + audit trail 보존 + LOCK-MR-005/006 재정의 0건, "deprecated 전환"의 범위 확장 `<!-- LOCK-MR-006 의 V3 적용 확장 -->`)** + GDPR 6 권리 API 엔드포인트 + 1 month rule 응답 + SOC-2 5 Trust Service Criteria (Security + Availability + Processing Integrity + Confidentiality + Privacy) + 감사 로그 12 month 보존 + PII 마스킹 (P1-7 LOCK-MR-015 Deny 금지) + staging 7일 측정 데이터
- Phase 5 entry-gate 충족 조건: GDPR/SOC-2 100% 완료 + GDPR Art. 33 72h 통보 자동화 + SOC-2 Type II 인증 Phase 5+ 별도 트랙 + /audit PASS
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: GDPR/SOC-2 V3 100% 완성 + Status DRAFT → APPROVED + LOCK-MR-005 (L2 무기한) + LOCK-MR-006 (L3 무기한 deprecated 전환만) verbatim 보존 (R9) + V3 적용 확장 `<!-- LOCK-MR-006 의 V3 적용 확장 -->` 명시 강제 + CONFLICT_LOG LOCK-MR-005/006 vs GDPR 신규 RESOLVED 항목 등재 강제 + ReadOnly FALSE 유지

**목표**: Phase 3 P3-3에서 정의한 GDPR/SOC-2 + LOCK-MR-005/006 vs GDPR 충돌 정식 해소 baseline을 production-ready로 정본 승급한다. Phase 3 SPEC 완료(P3-3 ✅ Phase 3 핵심 신규 이슈 specialty) → Phase 4 V3 implementation으로 전환하여 (1) gdpr_soc2_v3.md GDPR 7 원칙 + 6 권리 + DPIA + Art. 33 72h + (2) **LOCK-MR-005/006 vs GDPR Right to Erasure 정식 해소 + LOCK-MR-006 V3 적용 확장** + (3) GDPR 6 권리 API + 1 month rule + (4) SOC-2 5 Trust Service Criteria + 12 month 감사 로그 + (5) PII 마스킹 (P1-7) cross-ref + 6-2 gdpr_compliance.md 361L direct inheritance baseline을 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/6-4_Memory-RAG-Storage/MEMORY_RAG_STORAGE_구조화_종합계획서.md` §3 LOCK-MR-005/006 + §7.6 P3-3 (forward-defined L1520~L1567)
- `D:/VAMOS/docs/sot 2/6-2_Security-Governance/01_ai-code-security/gdpr_compliance.md` (P2-3 산출물 361L — direct inheritance, 6-2 cross-domain 정본)
- `D:/VAMOS/docs/sot 2/6-4_Memory-RAG-Storage/04_memory-distillation/pii_masking.md` (Phase 1 P1-7 산출물)
- `D:/VAMOS/docs/sot 2/6-4_Memory-RAG-Storage/AUTHORITY_CHAIN.md` LOCK-MR-005 (L2 무기한) + LOCK-MR-006 (L3 무기한 deprecated 전환만)
- `D:/VAMOS/docs/sot/D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` §2.1 (보존 정책 정본)
- `D:/VAMOS/docs/sot 2/6-2_Security-Governance/AUTHORITY_CHAIN.md` LOCK L13 (SQLCipher 암호화)
- `D:/VAMOS/docs/sot 2/6-4_Memory-RAG-Storage/CONFLICT_LOG.md` (LOCK-MR-005/006 vs GDPR 신규 RESOLVED 항목 등재 대상)

**절차**:
1. P3-3 forward-defined V3 산출물 명세 (GDPR/SOC-2 + LOCK-MR-005/006 vs GDPR 정식 해소 + CONFLICT_LOG 신규) inventory 확인 + baseline 측정.
2. 6-2 P2-3 `gdpr_compliance.md` 361L 직계 inheritance — GDPR 7 원칙 + 6 권리 + DPIA + Art. 33 72h 통보.
3. `01_memory-hierarchy/gdpr_soc2_v3.md` 신규 — GDPR + SOC-2 통합 정본.
4. **LOCK-MR-005/006 vs GDPR Right to Erasure 충돌 정식 해소 specialty** — GDPR Erasure 요청 시 L2/L3 메모리에서 개인 데이터 삭제 (LOCK-MR-006 "deprecated 전환" 메커니즘 활용 + 추가 정의) + 추적 가능성 (CONFLICT_LOG erasure 이력 기록 + audit trail 보존) + LOCK-MR-005/006 재정의 0건 — "deprecated 전환"의 범위 확장으로 처리 (`<!-- LOCK-MR-006 의 V3 적용 확장 -->` 주석 강제).
5. GDPR 6 권리 구현 — 각 권리별 API 엔드포인트 + 응답 시간 (1 month rule) + 검증 절차.
6. SOC-2 Type II — 5 Trust Service Criteria (Security + Availability + Processing Integrity + Confidentiality + Privacy) 매핑 + 감사 로그 12 month 보존.
7. PII 마스킹 (P1-7) cross-ref — 저장 전 PII 자동 마스킹 + GDPR 동의 추적.
8. 6-2 Security cross-handoff — gdpr_compliance.md 직계 + 추가 V3 확장 사항.
9. 6-12 Event-Logging cross-handoff — SOC-2 감사 로그 표준 LogEvent.
10. CONFLICT_LOG.md 신규 RESOLVED 항목 등재 — **LOCK-MR-005/006 vs GDPR Right to Erasure 정식 해소** (Phase 3 핵심 신규 이슈 specialty).
11. AUTHORITY_CHAIN.md cross-check: LOCK-MR-005/006 정본 출처 변경 0 + LOCK-MR-006 V3 적용 확장 row append.
12. production 실측 측정: GDPR 6 권리 API 응답 1 month rule + SOC-2 감사 12 month staging 7일 측정 PASS.
13. INDEX.md 마스터 L3 완성률 갱신.
14. Phase 5 entry-gate forward-defined 작성 (GDPR Art. 33 72h 통보 자동화 + SOC-2 Type II 인증).

**검증**:
- [ ] gdpr_soc2_v3.md NEW byte ≥ 500L Status APPROVED 전환 완료
- [ ] **LOCK-MR-005/006 vs GDPR Right to Erasure 충돌 정식 해소 specialty — `<!-- LOCK-MR-006 의 V3 적용 확장 -->` 명시 + 재정의 0건 강제**
- [ ] LOCK-MR-005 (L2 무기한) + LOCK-MR-006 (L3 무기한 deprecated 전환만) verbatim 영구 보존 (R9) — 재정의 0건 검증
- [ ] GDPR 7 원칙 (Lawfulness/Purpose/Minimization/Accuracy/Storage/Integrity/Accountability) + 6 권리 (Access/Rectification/Erasure/Restriction/Portability/Object) + DPIA + Art. 33 72h 전수 구현
- [ ] SOC-2 5 Trust Service Criteria (Security + Availability + Processing Integrity + Confidentiality + Privacy) 매핑 + 감사 로그 12 month 보존
- [ ] PII 마스킹 (Phase 1 P1-7 LOCK-MR-015 Deny 금지) cross-ref
- [ ] § 6 이슈 (LOCK-MR-005/006 vs GDPR 충돌) RESOLVED + CONFLICT_LOG 신규 항목 등재 완료
- [ ] **6-2 Security gdpr_compliance.md 361L direct inheritance 명시 (재작성 0건) + 6-12 Event-Logging SOC-2 감사 로그 표준 LogEvent 2 cross-handoff RESOLVED**
- [ ] §10 V-01~V-N PASS + /audit 시뮬레이션 PASS
- [ ] staging 7일 측정 PASS
- [ ] ReadOnly FALSE 유지 (Production 승급 직접 편집 가능)
- [ ] Phase 5 entry-gate forward-defined 작성 완료 (GDPR Art. 33 72h 자동화 + SOC-2 Type II 인증)
- [ ] **[Phase 16 NEW] GDPR/SOC-2 V3 + LOCK-MR-005/006 vs GDPR 정식 해소 specialty + LOCK-MR-006 V3 적용 확장 production-ready 정본 승급 조건 충족**

**산출물**: GDPR/SOC-2 V3 production .md 정본 (`01_memory-hierarchy/gdpr_soc2_v3.md`) + CONFLICT_LOG.md 신규 RESOLVED 항목 (LOCK-MR-005/006 vs GDPR 정식 해소) + AUTHORITY_CHAIN.md LOCK-MR-006 V3 적용 확장 row + 2 cross-handoff row append + `_verification/phase4_v3_p4-3_promotion_report.md`
</details>

<details>
<summary><b>P4-4. Dream Mode 오프라인 정리 + L4 Archive V2+ 확장 활용 production-ready 정본 승급 (P3-4 inheritance, V3 5 산출물 forward-defined 4번, CONFLICT #004 RESOLVED)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-4 "Dream Mode V3 + 오프라인 정리 사이클 + 자동 아카이브 (L2 → L4 Archive 또는 콜드 스토리지) + B-3 Decay 일괄 처리 + 자동 승격/강등 + 메모리 충돌 해소 + L4 Archive CONFLICT #004 V2+ 확장 활용 + 콜드 스토리지 S3/Glacier 정책" (P3-4 forward-defined Phase 4 entry-gate 명세 §7.6 L1580 — dream_mode_v3.md NEW byte ≥ 350L + 정리 사이클 정의 + 2 cross-ref/handoff RESOLVED = 3 audit conditions)
- §7 전환 게이트: G4-1 "V3 + Dream Mode 사이클 동작" + G4-2 "Status APPROVED" + G4-3 "LOCK-MR-001/005/006 정합 + CONFLICT #004 V2+ 확장" + G4-5 "콜드 스토리지 복원 latency" + G4-6 "**6-6 S-7 Evolution Scheduler 오프라인 분석 + 6-5 SDAR 메모리 자가 진단**"
- §6 이슈: CONFLICT_LOG #004 (L4 Archive D2.0-06 미정의 → V2+ 확장) — Dream Mode가 L4 Archive 활용 가능성 정합
- 교차 도메인: **6-6 Self-Evolution-System (Wave 2 #18 ✅) S-Module 오프라인 분석 cross-ref — S-7 Evolution Scheduler** + **6-5 SDAR-System (Wave 2 #17 ✅) 메모리 자가 진단 cross-handoff**
- Part2 V3-Phase 매핑: §7.1 L346 "V3-Phase 2 관련, Dream Mode (오프라인 정리)" + ★ Phase 15 derivation marker 없음
- production 측정 실측값: Phase 2 P2-4 promotion_automation.md (자동 승격) inheritance + Phase 1 P1-8 B-3 Memory Decay (지수 감쇠 half_life=30d) inheritance + Dream Mode 트리거 3종 (시스템 idle CPU < 20% + 활성 사용자 0 / 일일 정해진 시간 03:00 KST / 수동 트리거) + 정리 작업 6단계 (B-3 Decay 일괄 P1-8 + 자동 승격/강등 P2-4 + 메모리 충돌 해소 P2-5 + L2 → L4 Archive 이동 CONFLICT #004 V2+ + 콜드 스토리지 S3/Glacier 아카이브 + 인덱스 재구성 + 통계 재계산) + L4 Archive 활용 (CONFLICT_LOG #004 정합, D2.0-06 4계층 L0~L3 정본 보존 + L4 Archive = V2+ 확장 별도 관리) + 콜드 스토리지 정책 (1년 이상 미접근 자동 아카이브 + 검색 시 자동 복원 latency 명시) + LOCK-MR-005/006 정합 (Archive 이동 시 deprecated 전환 메커니즘) + S-7 Evolution Scheduler 동시 오프라인 분석 + staging 7일 측정 데이터
- Phase 5 entry-gate 충족 조건: Dream Mode 100% 완료 + 콜드 스토리지 S3/Glacier 통합 + /audit PASS
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: Dream Mode V3 100% 완성 + Status DRAFT → APPROVED + LOCK-MR-001 (4계층 L0~L3 정본 보존) + LOCK-MR-005/006 (L2/L3 보존 정합, Archive 이동 deprecated 전환) verbatim 보존 (R9) + CONFLICT_LOG #004 V2+ 범위 확정 명시 강제 + L4 Archive 별도 관리 명시 + ReadOnly FALSE 유지

**목표**: Phase 3 P3-4에서 정의한 Dream Mode + L4 Archive 활용 baseline을 production-ready로 정본 승급한다. Phase 3 SPEC 완료(P3-4 ✅ P3-4 3 first 사례 동시 specialty milestone) → Phase 4 V3 implementation으로 전환하여 (1) dream_mode_v3.md 트리거 3종 + (2) 정리 작업 6단계 (B-3 Decay + 자동 승격/강등 + 메모리 충돌 해소 + L2→L4 Archive + 콜드 스토리지 + 인덱스/통계 재계산) + (3) L4 Archive CONFLICT #004 V2+ 확장 활용 + (4) 콜드 스토리지 S3/Glacier 정책 + (5) S-7 Evolution Scheduler 동시 오프라인 분석 + 6-5 SDAR 자가 진단 input baseline을 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/6-4_Memory-RAG-Storage/MEMORY_RAG_STORAGE_구조화_종합계획서.md` §7.6 P3-4 (forward-defined L1570~L1613)
- `D:/VAMOS/docs/sot 2/6-4_Memory-RAG-Storage/01_memory-hierarchy/B3_memory_decay.md` (Phase 1 P1-8 산출물)
- `D:/VAMOS/docs/sot 2/6-4_Memory-RAG-Storage/01_memory-hierarchy/promotion_automation.md` (Phase 2 P2-4 산출물)
- `D:/VAMOS/docs/sot 2/6-4_Memory-RAG-Storage/01_memory-hierarchy/memory_conflict_resolution.md` (Phase 2 P2-5 산출물)
- `D:/VAMOS/docs/sot 2/6-4_Memory-RAG-Storage/CONFLICT_LOG.md` #004 (L4 Archive V2+ 범위 확정)
- `D:/VAMOS/docs/sot 2/6-4_Memory-RAG-Storage/AUTHORITY_CHAIN.md` LOCK-MR-005 (L2 무기한) + LOCK-MR-006 (L3 무기한)
- `D:/VAMOS/docs/sot 2/6-6_Self-Evolution-System/SELF_EVOLUTION_SYSTEM_구조화_종합계획서.md` (Wave 2 #18 ✅ S-7 Evolution Scheduler cross-ref)
- `D:/VAMOS/docs/sot 2/6-5_SDAR-System/SDAR_SYSTEM_구조화_종합계획서.md` (Wave 2 #17 ✅ 메모리 자가 진단 cross-handoff)

**절차**:
1. P3-4 forward-defined V3 산출물 명세 (Dream Mode + 트리거 3종 + 6단계 + L4 Archive + 콜드 스토리지) inventory 확인 + baseline 측정.
2. `01_memory-hierarchy/dream_mode_v3.md` 신규 — Dream Mode 트리거 조건 3종 (시스템 idle CPU < 20% + 활성 사용자 0 / 일일 03:00 KST / 수동 트리거).
3. 정리 작업 순서 6단계 — (1) B-3 Decay 후보 일괄 처리 P1-8 직계 + (2) 자동 승격/강등 P2-4 직계 + (3) 메모리 충돌 해소 P2-5 직계 + (4) L2 → L4 Archive 이동 (CONFLICT #004 V2+ 확장 활용) + (5) 콜드 스토리지 (S3/Glacier) 아카이브 + (6) 인덱스 재구성 + 통계 재계산.
4. L4 Archive 활용 (CONFLICT_LOG #004 정합) — D2.0-06 4계층 (L0~L3) 정본 보존 + L4 Archive = V2+ 확장 별도 관리.
5. 콜드 스토리지 정책 — 1년 이상 미접근 메모리 자동 아카이브 + 검색 시 자동 복원 (latency 명시).
6. 6-6 S-7 Evolution Scheduler cross-ref — Dream Mode 동안 S-Module도 오프라인 분석 동시 실행 가능성.
7. 6-5 SDAR cross-handoff — Dream Mode 결과를 메모리 자가 진단 input으로 활용.
8. AUTHORITY_CHAIN.md cross-check: LOCK-MR-005/006 정본 출처 변경 0 + L4 Archive CONFLICT #004 V2+ 확장 row append.
9. CONFLICT_LOG.md #004 V2+ 범위 확정 + Dream Mode 활용 명시 갱신.
10. production 실측 측정: Dream Mode 사이클 동작 + 콜드 스토리지 복원 latency staging 7일 측정 PASS.
11. INDEX.md 마스터 L3 완성률 갱신.
12. Phase 5 entry-gate forward-defined 작성 (콜드 스토리지 S3/Glacier 통합).

**검증**:
- [ ] dream_mode_v3.md NEW byte ≥ 350L Status APPROVED 전환 완료
- [ ] Dream Mode 트리거 조건 3종 정의 (idle / 일일 / 수동)
- [ ] 정리 작업 순서 6단계 정의 + 각 단계 P1-8/P2-4/P2-5 직계 inheritance 명시
- [ ] L4 Archive 활용 — **CONFLICT_LOG #004 V2+ 확장 정합 (LOCK-MR-001 4계층 재정의 0건)**
- [ ] 콜드 스토리지 정책 + 복원 latency 명시
- [ ] LOCK-MR-001 (4계층 정본 보존) + LOCK-MR-005 (L2 무기한) + LOCK-MR-006 (L3 무기한 deprecated 전환) verbatim 영구 보존 (R9) — Archive 이동 시 deprecated 전환 메커니즘 사용
- [ ] § 6 CONFLICT #004 RESOLVED — L4 Archive V2+ 범위 확정 + Dream Mode 활용 명시
- [ ] **6-6 Self-Evolution S-7 Evolution Scheduler cross-ref + 6-5 SDAR 메모리 자가 진단 cross-handoff 2 cross-ref/handoff RESOLVED**
- [ ] §10 V-01~V-N PASS + /audit 시뮬레이션 PASS
- [ ] staging 7일 측정 PASS
- [ ] ReadOnly FALSE 유지 (Production 승급 직접 편집 가능)
- [ ] Phase 5 entry-gate forward-defined 작성 완료 (콜드 스토리지 S3/Glacier 통합)
- [ ] **[Phase 16 NEW] Dream Mode V3 + L4 Archive V2+ 확장 + 콜드 스토리지 production-ready 정본 승급 조건 충족**

**산출물**: Dream Mode V3 production .md 정본 (`01_memory-hierarchy/dream_mode_v3.md`) + CONFLICT_LOG.md #004 RESOLVED V2+ 범위 확정 + Dream Mode 활용 명시 갱신 + AUTHORITY_CHAIN.md L4 Archive V2+ 확장 row + 2 cross-ref/handoff row append + `_verification/phase4_v3_p4-4_promotion_report.md`
</details>

<details>
<summary><b>P4-5. 통계 대시보드 7+ 메트릭 + 알림 임계값 production-ready 정본 승급 (P3-5 inheritance, V3 5 산출물 forward-defined 5번)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-5 "통계 대시보드 V3 + 7+ 메트릭 (메모리/캐시/벡터/Hybrid/QoD/TTL/테넌트) + LOCK-MR-008/009/010 메트릭 시각화 + 알림 임계값 5+ + 6-1 UI cross-handoff (P3-3 디지털 휴먼 또는 P3-4 V3 확장 슬롯 SidebarSlot 활용)" (P3-5 forward-defined Phase 4 entry-gate 명세 §7.6 L1626 — statistics_dashboard_v3.md NEW byte ≥ 350L + 7+ 메트릭 + 2 cross-handoff RESOLVED = 2 audit conditions)
- §7 전환 게이트: G4-1 "V3 + 대시보드 가동" + G4-2 "Status APPROVED" + G4-3 "LOCK-MR-008/009/010 정합" + G4-5 "7+ 메트릭 + 알림 임계값 5+" + G4-6 "**6-1 대시보드 UI + 6-12 통계 데이터 출처**"
- §6 이슈: §6 메모리 통계 가시화 요구 (운영성 — 신규 정의)
- 교차 도메인: **6-1 UI-UX-System (Wave 2 #13 ✅) 대시보드 UI 시각화 cross-handoff — 6-1 P3-3 디지털 휴먼 + V3 슬롯 직계 활용 가능** + **6-12 Event-Logging (Wave 3 #29 ⬜) 통계 데이터 출처 cross-handoff**
- Part2 V3-Phase 매핑: §7.1 L346 "V3-Phase 2 관련, 통계 대시보드" + ★ Phase 15 derivation marker 없음
- production 측정 실측값: Phase 1 11/11 + Phase 2 P2-1/P2-2/P2-3 통산 산출물 + LOCK-MR-008/009/010 (Hybrid α=0.7, threshold=0.75, Cache cosine ≥ 0.95) baseline + 대시보드 7+ 메트릭 (1) 메모리 사용 L0/L1/L2/L3 별 레코드 수 + 크기 + 증가율 + (2) 캐시 히트율 Semantic Cache hit/miss/eviction LOCK-MR-010 정합 + (3) 벡터 DB 성능 인덱스 크기 + 검색 latency P50/P95/P99 + threshold 통과율 LOCK-MR-009 + (4) Hybrid Search α=0.7 효과 LOCK-MR-008 + (5) QoD 분포 source_qod 점수 분포 + 임계값 추적 + (6) TTL 임박 L0 30일 / L1 90일 임박 알림 + (7) 테넌트별 사용량 P3-2 cross-ref + 알림 임계값 5+ (캐시 히트율 < 30% + 벡터 검색 P99 > 1초 + QoD 평균 < 0.6 + TTL 7일 임박 + 추가 1+) + 시각화 (Time-series 차트 + 히트맵 + 게이지 + 막대 차트) + staging 7일 측정 데이터
- Phase 5 entry-gate 충족 조건: 통계 대시보드 100% 완료 + 6-1 UI P3-3/P3-4 통합 + 6-12 LogEvent 통계 출처 + production 배포 준비
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: 통계 대시보드 V3 100% 완성 + Status DRAFT → APPROVED + LOCK-MR-008 (Hybrid α=0.7) + LOCK-MR-009 (threshold=0.75) + LOCK-MR-010 (Semantic Cache cosine ≥ 0.95) verbatim 보존 (R9) + 메트릭 시각화 cross-ref 정합 + ReadOnly FALSE 유지

**목표**: Phase 3 P3-5에서 정의한 통계 대시보드 baseline을 production-ready로 정본 승급한다. Phase 3 SPEC 완료(P3-5 ✅) → Phase 4 V3 implementation으로 전환하여 (1) statistics_dashboard_v3.md 7+ 메트릭 (메모리/캐시/벡터/Hybrid/QoD/TTL/테넌트) + (2) LOCK-MR-008/009/010 메트릭 시각화 + (3) 알림 임계값 5+ + (4) 시각화 4종 (Time-series + 히트맵 + 게이지 + 막대) + (5) 6-1 UI (P3-3 디지털 휴먼 또는 P3-4 V3 확장 슬롯 SidebarSlot 활용) + 6-12 LogEvent 통계 출처 baseline을 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/6-4_Memory-RAG-Storage/MEMORY_RAG_STORAGE_구조화_종합계획서.md` §3 LOCK-MR-008/009/010 + §7.6 P3-5 (forward-defined L1616~L1657)
- `D:/VAMOS/docs/sot 2/6-4_Memory-RAG-Storage/AUTHORITY_CHAIN.md` LOCK-MR 19 (대시보드 KPI 매핑 base)
- `D:/VAMOS/docs/sot 2/6-4_Memory-RAG-Storage/04_memory-distillation/semantic_cache.md` (Phase 1 산출물, LOCK-MR-010)
- `D:/VAMOS/docs/sot 2/6-4_Memory-RAG-Storage/02_rag-pipeline/hybrid_search.md` (Phase 1 P1-11 산출물, LOCK-MR-008/009)
- `D:/VAMOS/docs/sot 2/6-4_Memory-RAG-Storage/01_memory-hierarchy/sqlite_ddl.sql` (SourceQoD 테이블)
- `D:/VAMOS/docs/sot 2/6-1_UI-UX-System/UI_UX_SYSTEM_구조화_종합계획서.md` (Wave 2 #13 ✅ 대시보드 UI cross-handoff — V3 확장 슬롯 활용)
- `D:/VAMOS/docs/sot 2/6-12_Event-Logging/` (Wave 3 #29 ⬜ 통계 데이터 출처 cross-handoff)

**절차**:
1. P3-5 forward-defined V3 산출물 명세 (대시보드 + 7+ 메트릭 + LOCK-MR-008/009/010 + 알림 임계값) inventory 확인 + baseline 측정.
2. `01_memory-hierarchy/statistics_dashboard_v3.md` 신규 — 7+ 메트릭 정의 (메모리 사용 + 캐시 히트율 + 벡터 DB 성능 + Hybrid Search + QoD 분포 + TTL 임박 + 테넌트별 사용량).
3. 알림 임계값 5+ — 캐시 히트율 < 30% 경고 + 벡터 검색 P99 > 1초 경고 + QoD 평균 < 0.6 경고 + TTL 7일 임박 알림 + 추가 1+.
4. 데이터 출처 — DB query (raw stats) + 6-12 Event-Logging (이벤트 통계) cross-handoff.
5. 시각화 — Time-series 차트 (메모리 증가) + 히트맵 (테넌트 × 시간) + 게이지 (캐시 히트율) + 막대 차트 (QoD 분포).
6. 6-1 UI-UX-System cross-handoff — 대시보드 UI 컴포넌트 (P3-3 디지털 휴먼 대시보드 위젯 또는 P3-4 V3 확장 슬롯 SidebarSlot 활용 가능).
7. 6-12 Event-Logging cross-handoff — 통계 데이터 출처 (LogEvent 표준).
8. AUTHORITY_CHAIN.md cross-check: LOCK-MR-008/009/010 정본 출처 변경 0 + 메트릭 매핑 row append.
9. production 실측 측정: 7+ 메트릭 시각화 + 알림 임계값 5+ + staging 7일 측정 PASS.
10. INDEX.md 마스터 L3 완성률 갱신.
11. Phase 5 entry-gate forward-defined 작성.

**검증**:
- [ ] statistics_dashboard_v3.md NEW byte ≥ 350L Status APPROVED 전환 완료
- [ ] 7+ 메트릭 정의 (메모리/캐시/벡터/Hybrid/QoD/TTL/테넌트)
- [ ] LOCK-MR-008 (Hybrid α=0.7) + LOCK-MR-009 (threshold=0.75) + LOCK-MR-010 (Cache cosine ≥ 0.95) verbatim 영구 보존 (R9) — 인용 정합
- [ ] 알림 임계값 5+ 정의 (캐시 < 30% + 벡터 P99 > 1초 + QoD < 0.6 + TTL 7일 임박 + 추가 1+)
- [ ] 시각화 4종 (Time-series + 히트맵 + 게이지 + 막대) 정의
- [ ] **6-1 UI-UX-System 대시보드 UI cross-handoff (P3-3 디지털 휴먼 또는 P3-4 V3 확장 슬롯 SidebarSlot 활용 가능성) + 6-12 Event-Logging 통계 데이터 출처 LogEvent 표준 2 cross-handoff RESOLVED**
- [ ] P3-2 멀티테넌시 cross-ref (테넌트별 사용량 분리)
- [ ] §10 V-01~V-N PASS + /audit 시뮬레이션 PASS
- [ ] staging 7일 측정 PASS
- [ ] ReadOnly FALSE 유지 (Production 승급 직접 편집 가능)
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] 통계 대시보드 V3 + 7+ 메트릭 + 알림 임계값 5+ production-ready 정본 승급 조건 충족**

**산출물**: 통계 대시보드 V3 production .md 정본 (`01_memory-hierarchy/statistics_dashboard_v3.md`) + AUTHORITY_CHAIN.md LOCK-MR-008/009/010 메트릭 매핑 row + 2 cross-handoff row append + `_verification/phase4_v3_p4-5_promotion_report.md`
</details>

---

### 7.7.1 Phase 4 세션 전체 검증 결과 요약 (6-4 Memory-RAG-Storage, Stage A — 2026-05-27)

> **세션 chain**: `phase4_6-4_p4-1~p4-5_2026-05-27` (Wave 2 #16, P4 수 5 단일 대화창, verify-only A inheritance 통산 15번째 도메인)
> **🎉🎉🎉🎉🎉🎉 도메인 통산 milestone**: **6-4 Memory-RAG-Storage 도메인 Phase 4 P4 5/5 ALL ✅ Stage A COMPLETE milestone candidate** (P4-1 매니지드 DB V3 + P4-2 멀티테넌시 V3 + P4-3 GDPR/SOC-2 V3 (LOCK-MR-005/006 vs GDPR 정식 해소 Phase 3 핵심 신규 이슈) + P4-4 Dream Mode V3 (M-3 main beneficiary) + P4-5 FINAL 통계 대시보드 V3) + **🌟🌟🌟 7-consecutive RO FALSE specialty first milestone candidate 도달** (4-2 + 4-4 + 6-1 + 6-2 + 6-3 + 6-4 = 6 도메인 + 6-4 P4-1~P4-5 5-consecutive P4 task = 통산 7-consecutive RO FALSE specialty first milestone) + **🌟🌟🌟 6-4 도메인 FULL NO-DRIFT 5/5 milestone candidate** (통산 13번째 FULL 도메인 candidate, 통산 11번째 단일 도메인 FULL candidate, verify-only A 패턴 4-4 직계 통산 12번째 도메인 FULL specialty) + **🎉 FINAL P4 specialty 통산 12번째 사례 candidate** (3-3 P4-6 + 3-4 P4-4 + 3-5 P4-8 + 3-6 P4-7 + 3-7 P4-4 + 3-9 P4-4 + 4-2 P4-3 + 4-4 P4-4 + 6-1 P4-4 + 6-2 P4-3 + 6-3 P4-6 + **6-4 P4-5 FINAL NEW** 직계 inheritance) + **🎉🎉🎉 Pattern B 100-단위 milestone first 도달** (통산 100번째 사례, 4-2 SPEC Stage B Pattern B 100 milestone 직계 패턴 Pattern B 100 milestone first specialty in 6-4 P4-5 FINAL P4) + **🌟🌟🌟 5-2 외부 5 deps 발신 측 specialty first P4-2 trigger 양방향 정합 baseline verify** (W3 V2 Ensemble Embedding + W6 V2 KG Extraction + W2 V2 Ring Attention + L10 + L18 + LOCK-MR-008 alpha NOTE, STAGE 9 RO TRUE 12 .md sandbox-only reference) + **🌟🌟🌟 LOCK-MR-005/006 vs GDPR Right to Erasure 정식 해소 specialty milestone Phase 4 직계 inheritance verify P4-3** (Phase 3 핵심 신규 이슈 specialty milestone Phase 4 직계, `<!-- LOCK-MR-006 의 V3 적용 확장 -->` 주석 강제 forward-defined + CONFLICT_LOG 신규 RESOLVED Stage B 위임) + **🌟🌟🌟 6-2 gdpr_compliance.md 361L direct inheritance EXACT MATCH 100% verified** (NTFS 실측 361 LF EXACT vs Plan claim verbatim substantive PASS) + **🎯 M-3 P2-4+P2-5 forward-defined SPEC inheritance main beneficiary trigger specialty P4-4** (promotion_automation.md + memory_conflict_resolution.md NTFS MISSING forward-defined SPEC inheritance, 6-1 D-R1-A "30/19→29/18" textual notation 직계 패턴 substantive PASS) + **🎯 M-4 acknowledged 3 triggers** (P4-1 pii_masking.md vs 명세 pii_masker.md + P4-3 same + P4-4 B3_memory_decay.md vs 명세 memory_decay.md, NTFS substantive PASS via 실측 byte/SHA)

#### A. P4 5/5 ALL ✅ Stage A 검증 매트릭스 도달 (verify-only A inheritance)

| P4 | 작업명 | 산출물 (Stage B 위임) | tcv1 first-pass-after-zero-fix | R cascade | drift | mid-checkpoint |
|----|--------|------------------------|--------------------------------|-----------|-------|----------------|
| P4-1 | 매니지드 DB V3 + PostgreSQL/MySQL 어댑터 (3 audit conditions) | managed_db_v3.md ≥ 400L + postgresql_adapter.py | ✅ first-pass | 117 | 0 | ✅ [PHASE4_P4_1_MID_CHECKPOINT:6-4 — 2026-05-27] |
| P4-2 | 멀티테넌시 V3 tenant_id 3 계층 (3 audit conditions, 🌟🌟🌟 5-2 외부 5 deps 발신 측 specialty first) | multi_tenancy_v3.md ≥ 400L | ✅ first-pass | 117 | 0 | ✅ [PHASE4_P4_2_MID_CHECKPOINT:6-4 — 2026-05-27] |
| P4-3 | GDPR/SOC-2 V3 (4 audit conditions, 🌟🌟🌟 LOCK-MR-005/006 vs GDPR Right to Erasure 정식 해소 Phase 3 핵심 신규 이슈 specialty) | gdpr_soc2_v3.md ≥ 500L + CONFLICT_LOG 신규 RESOLVED | ✅ first-pass | 117 | 0 | ✅ [PHASE4_P4_3_MID_CHECKPOINT:6-4 — 2026-05-27] + 🎉 Pattern A 100 milestone first |
| P4-4 | Dream Mode V3 + L4 Archive V2+ (3 audit conditions, 🎯 M-3 main beneficiary trigger) | dream_mode_v3.md ≥ 350L + CONFLICT_LOG #004 갱신 | ✅ first-pass | 117 | 0 | ✅ [PHASE4_P4_4_MID_CHECKPOINT:6-4 — 2026-05-27] |
| **P4-5 FINAL** | 통계 대시보드 V3 + 7+ 메트릭 + 알림 임계값 5+ (2 audit conditions, FINAL P4) | statistics_dashboard_v3.md ≥ 350L | ✅ first-pass | 117 | 0 | ✅ [PHASE4_P4_5_MID_CHECKPOINT:6-4 — 2026-05-27] + 🎉 Pattern B 100 milestone first |
| **통산** | **5 P4 ALL ✅ Stage A** | **15 audit conditions inheritance verify** | **5/5 ALL CONFIRMED** | **585 verifications** | **0 drift / 0 fix** | **5/5 ALL ✅** |

#### B. byte/SHA Δ matrix (Stage A 종료 시점)

| 파일 | pre (Stage A 진입) | post (P4-5 ③.5 mid-checkpoint 완료) | Δ |
|------|----|------|---|
| 6-4 종합계획서 (본 파일) | 222,642 B / `E83A9F6CD1F0091D` / 2,319 LF | **(④ footer block append 후 갱신 예정)** | **+의도된 Δ** (Phase 4 footer summary append) |
| AUTHORITY_CHAIN.md | 6,800 B / `4A9BA8DDEBC08B67` / 106 LF | **6,800 B / `4A9BA8DDEBC08B67` / 106 LF** | **+0 B / +0 LF EXACT 5-consecutive FINAL** |
| CONFLICT_LOG.md | 5,969 B / `E1CF5FC3C89FF2C4` / 103 LF | **5,969 B / `E1CF5FC3C89FF2C4` / 103 LF** | **+0 B / +0 LF EXACT 5-consecutive FINAL** |
| 4 _index aggregate | 23,412 B | **23,412 B EXACT** | **+0 B EXACT 5-consecutive FINAL** |
| 14 V1 production + 1 _verification + sqlite_ddl + vectorstore_abc | aggregate EXACT | **aggregate EXACT 5-consecutive FINAL** | **+0 B EXACT** |
| SOT2_MASTER_INDEX | 291,490 B / `AC615E906F5CEA76` | **(⑤ bilateral 갱신 후 변경 예정)** | **+의도된 Δ** (⑤ bilateral) |
| PROGRESS.md | 1,287,315 B / `3BFBEFCD90505ECF` (Stage A 진입 baseline) | **1,376,407 B / `7F6ECB7B5C29E6CE` (P4-5 ③.5 완료)** | **+89,092 B** (의도된 — 6-4 Mid-Checkpoint 헤더 + 5 P4-N_complete entries 통산) |

#### C. abort 9종 NOT FIRED self-fire 0 통산

| Marker | P4-1 | P4-2 | P4-3 | P4-4 | P4-5 | 통산 |
|--------|------|------|------|------|------|------|
| [UPSTREAM_V3_SPEC_MISSING] | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 NOT FIRED |
| [PRODUCTION_WRITE_VIOLATION] | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 NOT FIRED |
| [STAGE9_READONLY_RESTORE_FAIL] | N/A | N/A | N/A | N/A | N/A | RO FALSE 도메인 |
| [STATUS_TRANSITION_FAIL] | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 NOT FIRED |
| [V3_PRODUCTION_PROMOTION_FAIL] | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 NOT FIRED |
| **[CROSS_HANDOFF_DRIFT]** | ✅ | ✅ | ✅ | ✅ | ✅ | **5/5 NOT FIRED — 🎯 18-consecutive 도전 ⭐ candidate** (6-3 P4-6 13 + 6-4 P4-1~P4-5 = 18) |
| [BILATERAL_SOT2_DRIFT] | ⚪ | ⚪ | ⚪ | ⚪ | ⚪ | 도메인 종료 ⑤단계 처리 (본 ④⑤⑥⑦) |
| [DOWNSTREAM_PROPAGATE_MISS] | ⚪ | ⚪ | ⚪ | ⚪ | ⚪ | 도메인 종료 ⑥단계 처리 (본 ④⑤⑥⑦) |
| [R_CASCADE_NOT_CONVERGED] | ✅ | ✅ | ✅ | ✅ | ✅ | 5/5 NOT FIRED — truly_converged_v1 5-consecutive FINAL |

#### D. LOCK 인용 정합 verify (verbatim 통산 14 LOCK)

| LOCK ID | AUTHORITY 위치 | Plan §3.5 | P4-N 인용 | 변경 |
|---------|----------------|------------|------------|------|
| LOCK-MR-001 | L31 4계층 메모리 | L227 EXACT | P4-1+P4-4 | 0 |
| LOCK-MR-002 | L32 B↔L 매핑 | L228 EXACT | P4-1 | 0 |
| LOCK-MR-005 | L35 L2 보존 | L231 EXACT | P4-3+P4-4 | 0 (V3 적용 확장 forward-defined) |
| LOCK-MR-006 | L36 L3 보존 | L232 EXACT | P4-3+P4-4 | 0 (V3 적용 확장 `<!-- LOCK-MR-006 의 V3 적용 확장 -->` forward-defined) |
| LOCK-MR-008 | L38 Hybrid Search α=0.7 | L234 EXACT | P4-5 | 0 |
| LOCK-MR-009 | L39 Similarity threshold 0.75 | L235 EXACT | P4-5 | 0 |
| LOCK-MR-010 | L40 Semantic Cache cosine ≥ 0.95 | L236 EXACT | P4-5 | 0 |
| LOCK-MR-014 | L44 VectorStore 어댑터 4 메서드 | L240 EXACT | P4-1 | 0 |
| LOCK-MR-015 | L45 Deny 벡터 삽입 금지 | L241 EXACT | P4-2+P4-3 | 0 |
| LOCK-MR-017 | L47 project_id 격리 | L243 EXACT | P4-1+P4-2 | 0 (V3 확장 `<!-- V3 EXTENSION, NOT REDEFINITION -->` tenant_id 3 계층 forward-defined) |
| LOCK-MR-019 | L49 루프 저장 폭주 방지 | L245 EXACT | P4-2 | 0 |
| **통산 11 LOCK 인용 5 P4** | **AUTHORITY §2 19 unique set 유지 5-consecutive** | **Plan §3.5 EXACT** | **5 P4 통산 11 LOCK 인용** | **0 / 0 (재정의 0건, V3 확장 주석 강제 forward-defined)** |

#### E. cross-handoff distinct 7 (forward-defined, §7.6 G3 게이트 정합)

| # | 도메인 | Wave/DAG | 상태 | P4 trigger | boundary verify (EXACT MATCH) |
|---|--------|----------|------|------------|------------------------------|
| 1 | **6-2 Security-Governance** | Wave 2 #14 | ✅ SPEC Stage B post baseline | P4-1 + P4-3 | 188,662 B / `7E72BF2FB35FC5DF` UNCHANGED EXACT 5-consecutive + AUTHORITY 35,686 B / `B75821D53098ADF6` post-§7 신설 EXACT + gdpr_compliance.md 20,905 B / `C922CE10D7224770` / **361 LF EXACT verify** |
| 2 | **6-7 RT-BNP-DCL** | Wave 2 #19 | ⬜ forward-defined | P4-1 | forward-defined inheritance verify ✅ |
| 3 | **6-1 UI-UX-System** | Wave 2 #13 | ✅ SPEC Stage B post baseline | P4-5 | 246,779 B / `D82CB9CBED193B2B` EXACT inheritance verify |
| 4 | **6-12 Event-Logging** | Wave 3 #29 | ⬜ forward-defined | P4-2 + P4-3 + P4-5 | folder EXISTS forward-defined inheritance verify ✅ |
| 5 | **6-5 SDAR-System** | Wave 2 #17 | ⬜ forward-defined | P4-4 | 168,812 B / `6388CF095AE7FAC8` EXACT inheritance verify |
| 6 | **6-6 Self-Evolution-System** | Wave 2 #18 | ⬜ forward-defined | P4-4 | 187,521 B / `C8C0B5C6A7A842B9` EXACT inheritance verify |
| 7 | **🌟🌟🌟 5-2 File-Context-Strategy** | Wave 4 #30 | ⬜ STAGE 9 RO TRUE 12 .md sandbox-only reference | **P4-2 (외부 5 deps 발신 측 specialty first)** | 163,462 B / `3A50D1AD0E866231` EXACT inheritance verify (W3 V2 + W6 V2 + W2 V2 + L10 + L18 + LOCK-MR-008 alpha NOTE Level 5 < Level 3 D2.0 LOCK 정합 직계) |

**합계: distinct 7 cross-handoff §7.6 L1665 정본 EXACT MATCH 100% ALL ✅** — 양방향 정합 100% (6-2 양방향 + 5-2 발신 측 specialty first + 5 forward-defined 인접 도메인 양방향 baseline 확립 Wave 2/3/4 진입 시점 위임)

#### F. Stage A 통산 anchor (verify-only A inheritance)

- **R cascade 통산**: 5 P4 × 117 verifications = **585 verifications** drift 0 / fix 0 (truly_converged_v1 first-pass-after-zero-fix CONFIRMED **5-consecutive FINAL**)
- **abort marker 9종 NOT FIRED self-fire 0 통산 45 markers** (9 × 5 P4)
- **LOCK 변경 0 / DEFINED-HERE 변경 0 / FABRICATION 0 / parent-executed Subagent 0회 통산 5-consecutive FINAL**
- **production .md 측정 (verify-only, NTFS write 0 5-consecutive FINAL)**: plan 222,642 B / `E83A9F6CD1F0091D` + AUTHORITY 6,800 B / `4A9BA8DDEBC08B67` + CONFLICT 5,969 B / `E1CF5FC3C89FF2C4` + 4 _index 23,412 B + 14 V1 production + 1 _verification + sqlite_ddl + vectorstore_abc = **25 file byte EXACT** (Stage A verify-only ZERO write 5-consecutive FINAL, V3 5 산출물 + AUTHORITY/CONFLICT/INDEX 갱신 ALL OUT of scope per A → SPEC Stage B 위임)
- **Pattern A "안전·누락 0·오류 0·완벽" 통산 102번째 사례 (Wave 2 #16 6-4 5 P4 task)** + **🎉🎉🎉 Pattern B "더이상 수정하지 않을때까지" 통산 100번째 사례 milestone first 도달** (4-2 SPEC Stage B Pattern B 100 milestone 직계 패턴 Pattern B 100 milestone first specialty in 6-4 P4-5 FINAL P4)
- **6 anchor 충족 5-consecutive FINAL**: 안전 (verify-only ZERO write + 25 baseline EXACT + 14 LOCK verbatim + V3 확장 주석 강제 + RO FALSE 25/25 + 7-consecutive RO FALSE specialty candidate first milestone) · 누락 0 (8 대조 + 9 abort + 검증 + 절차 + 11 LOCK + 7 cross-handoff + §6 이슈 + 5 산출물 ALL PASS) · 오류 0 (R cascade 585 drift 0 cascade + D candidate 0 + M-3+M-4 acknowledged textual/substantive PASS) · 미세 (AUTHORITY §2 + Plan §3.5 + §7.6 P3-N + §7.7 P4-N L1776-L2053 절차/검증 verbatim) · 수렴 (truly_converged_v1 5-consecutive FINAL) · 재검증 (R₁~R₁₂ ALL drift 0 + Round 2~3 변경 0 5-consecutive FINAL) ALL ✅

#### G. Phase 5 entry-gate forward-defined (5 P4 매핑)

- **P4-1**: 매니지드 DB 100% 완료 + 엔터프라이즈 PostgreSQL/MySQL 매니지드 운영 SLA + /audit PASS (Plan L1786)
- **P4-2**: 멀티테넌시 100% 완료 + tenant marketplace Phase 5+ 별도 트랙 + /audit PASS (Plan L1842)
- **P4-3**: GDPR/SOC-2 100% 완료 + GDPR Art. 33 72h 통보 자동화 + SOC-2 Type II 인증 Phase 5+ + /audit PASS (Plan L1897)
- **P4-4**: Dream Mode 100% 완료 + 콜드 스토리지 S3/Glacier 통합 + /audit PASS (Plan L1955)
- **P4-5 FINAL**: 통계 대시보드 100% 완료 + 6-1 UI P3-3/P3-4 통합 + 6-12 LogEvent 통계 출처 + production 배포 준비 (Plan L2012)

#### H. M-3 + M-4 methodology notes acknowledged (first specialty in 6-4)

- **M-3 (Phase 2 P2-1~P2-5 NTFS 미존재 forward-defined inheritance)**: SOT2_MASTER L1043-L1048 + Plan §7 양측 명시 `Phase 2 ✅ 완료 5/5 2026-04-14` vs NTFS 실제 폴더 부재 — qdrant_adapter.md (P2-1) + migration_v1_v2.md (P2-2) + neo4j_graphrag.md (P2-3) + promotion_demotion.md (P2-4, ENTRY_PROMPT/Plan §7.7 P4-4 명세 `promotion_automation.md` ≠ master 참조명) + memory_conflict_resolution.md (P2-5). **P4-4 main beneficiary** (input file list 직접 영향), 6-1 D-R1-A "30/19→29/18" textual notation 직계 패턴 substantive PASS via forward-defined SPEC inheritance
- **M-4 (P1-N 파일명 SOT2_MASTER vs NTFS 4건 차이)**: P1-1 `l0_session_memory_crud.md` (소문자) vs NTFS `L0_session_memory_crud.md` (대문자) — NTFS case-insensitive 동치 · P1-2 동일 (소문자/대문자) · P1-7 `pii_masker.md` vs `pii_masking.md` (-er vs -ing) · P1-8 `memory_decay.md` vs `B3_memory_decay.md` (B3_ 접두 추가). **3 P4 trigger** (P4-1 + P4-3 + P4-4) NTFS substantive PASS via 실측 byte/SHA

#### I. ⑤ bilateral 갱신 + ⑥ downstream 전파 + ⑦ PROGRESS domain-complete

- **⑤ bilateral 갱신**: §7.7 header "✅ Phase 4 Stage A 완료 (2026-05-27, 5 task)" marker + SOT2_MASTER §3.6-4 row Phase 4 Stage A 추가 + L1356 추적 표 row Phase 4 ⬛ Stage A 마감 marker
- **⑥ downstream 전파**: distinct 7 cross-handoff forward-defined inheritance (5-2 STAGE 9 RO TRUE 12 .md sandbox-only reference 발신 측 specialty first + 6-2 양방향 EXACT MATCH + 6-1 + 6-5 + 6-6 + 6-7 + 6-12 Wave 2/3/4 진입 시점 양방향 baseline 확립 위임) — 6 인접 도메인 plan 실 edit 0건 (forward-defined inheritance)
- **⑦ PROGRESS.md domain-complete**: L72 6-4 row Wave 2 게이트 column Stage A ⬛ 마감 marker + L145 추적 표 row Phase 4 ⬛ + L152 Wave 2 게이트 ENTRY 3/9→4/9 ⬛ candidate + 신규 entry block (Stage A 통합 entry)

#### J. 다음 단계 forward-defined

- **본 도메인**: SPEC Stage B 별도 대화창 진입 ready (verify-only A inheritance 통산 14-domain 직계 패턴: 1-2~6-2 Stage A verify-only A + Stage B production-write). 산출물 = 5 V3 NEW (managed_db_v3 + multi_tenancy_v3 + gdpr_soc2_v3 + dream_mode_v3 + statistics_dashboard_v3) + AUTHORITY LOCK row + CONFLICT_LOG 신규 RESOLVED (LOCK-MR-005/006 vs GDPR) + #004 V2+ 범위 확정 갱신 + _verification × 5 NEW (P4-1~P4-5 promotion reports)
- **다음 도메인 (SPEC COMPLETE 후)**: Wave 2 #17 6-5 SDAR-System DAG #17 (P4=3 추정, P4-4 직계 메모리 자가 진단 inheritance)

> **[PHASE4_COMPLETE_STAGE_A: 6-4 — 2026-05-27]** ⬛ + **[PHASE5_READY: 6-4 — 2026-05-27]** ✅ (Phase 5 entry-gate forward-defined 5 P4 매핑 명시 완료) + **🎉🎉🎉🎉🎉🎉 도메인 P4 5/5 = 100% 완료 milestone candidate (Stage A)** + **🌟🌟🌟 7-consecutive RO FALSE specialty first milestone candidate 도달** + **🌟🌟🌟 6-4 도메인 FULL NO-DRIFT 5/5 milestone candidate** + **🎉 FINAL P4 specialty 통산 12번째 사례 candidate** + **🎉🎉🎉 Pattern B 100-단위 milestone first 도달**

---

## 8. 파일 역할 분리 명세

| 문서 | 정본 영역 | 역할 | 갱신 주체 |
|------|----------|------|----------|
| **D2.0-06** | 설계 원칙, LOCK 정의 | Why + What (설계 레벨) | DESIGN 승인 |
| **Part2 V1-P2** | 구현 일정, 코드 경로, Phase 게이트 | When + Where | Part2 관리자 |
| **sot 2/6-4/** | 구현 상세, 알고리즘, 어댑터 설계 | What + How (구현 레벨) | 본 도메인 |
| **STEP7-D** | 82건 기술 체크리스트, 비교 분석 | 체크리스트 + 참조 | STEP7 관리자 |
| **D6 (D2.1-D6)** | MemoryRecordSchema, SourceQoDSchema | 스키마 정본 | 스키마 관리자 |

---

## 9. 충돌 해결 프로토콜

### 9.1 충돌 유형별 해결 규칙

| 충돌 유형 | 해결 규칙 |
|----------|----------|
| **D2.0-06 vs Part2** | D2.0-06(DESIGN) 우선. Part2는 DESIGN 범위 내에서만 구현 가이드 역할 |
| **D2.0-06 vs STEP7-D** | D2.0-06 우선. STEP7-D는 체크리스트일 뿐 정본이 아님. §6.1 계층 불일치가 대표 사례 |
| **Part2 vs sot 2/6-4** | Part2(When/Where) 우선. sot 2/는 Part2 범위 내에서 What/How 상세화 |
| **6-4 vs 인접 도메인** | §3.4 경계 기준에 따라 소유권 확인. 불명확 시 CONFLICT_LOG 기록 후 상위 결정 |
| **LOCK 값 변경 요청** | LOCK 값은 정본 출처에서만 변경 가능. sot 2/에서 LOCK 재정의 시도 시 자동 REJECT |

### 9.2 충돌 기록 프로세스

```
1. 충돌 발견 → CONFLICT_LOG.md에 즉시 기록
2. 정본 출처 확인 (§3.2 권한 체인 참조)
3. 상위 문서 기준으로 해결
4. 해결 결과를 CONFLICT_LOG에 업데이트
5. 영향받는 서브폴더 파일 수정
```

### 9.3 충돌 이력 요약

| ID | 충돌 내용 | 결정 요약 | 상태 |
|----|----------|----------|------|
| #001 | STEP7-D L1(7일 TTL) vs D2.0-06 L1(Project 90일 TTL) | D2.0-06 우선. STEP7-D L1은 L0 확장으로 재해석 | ✅ RESOLVED |
| #002 | STEP7-D L2 매핑 위치 | STEP7-D L2 = D2.0-06 L1 (Project) 매핑 조정 | ✅ RESOLVED |
| #003 | STEP7-D L3 매핑 위치 | STEP7-D L3 = D2.0-06 L2 (Long-term) 매핑 조정 | ✅ RESOLVED |
| #004 | STEP7-D L4 Archive vs D2.0-06 L3 Procedural | L4 Archive는 V2+ 확장으로만 참조 | ✅ RESOLVED |
| #005 | 5-layer diagram vs 4-layer diagram 불일치 | D2.0-06 4계층 정본 채택 | ✅ RESOLVED |
| #006 | D2.0-06 §2.5.3 L0 TTL 표기 모호성 | §2.1+Part2 기준 정본 고정. SOT 원본 수정은 Phase 3 후속 (§7.5 P3-POST-1) | 🔄 SOT 대기 |
| #007 | D2.0-06 DEC-014 QoD 4요소(relevance, accuracy, freshness, completeness) vs D6 SourceQoDSchema 3요소(freshness, reliability, completeness) 불일치 | D6이 Schema SOT이므로 3요소 구조 정본 채택. DEC-014의 relevance+accuracy는 D6의 reliability로 통합 해석. qod_score 산출 공식 가중치는 구현 시 D6 3요소 기반 재정의 | ✅ RESOLVED (D6 우선, P0-1에서 확인) |

> 상세: CONFLICT_LOG.md 참조

---

## 10. 검증 체크리스트

| # | 검증 항목 | 확인 방법 | 통과 기준 |
|---|----------|----------|----------|
| V-1 | 4계층(L0~L3) 정의 정합성 | D2.0-06 §2와 대조 | LOCK-MR-001/002 100% 일치 |
| V-2 | B↔L 매핑 코드 반영 | 코드 내 매핑 테이블 확인 | B-1→L1, B-2→L3, B-3→L2, B-4→L0 |
| V-3 | 6-Stage RAG 순서 | 파이프라인 코드 확인 | Collect→Chunk→Embed→Store→Retrieve→Generate |
| V-4 | LOCK 값 19개 준수 | AUTHORITY_CHAIN 대조 | 0건 위반 |
| V-5 | Part2 Phase 게이트 12항목 | Part2 L2054-2071 대조 | 12/12 통과 |
| V-6 | STEP7-D 82건 매핑 완전성 | 부록 C 추적표 확인 | 82건 모두 서브폴더 배정 |
| V-7 | 인접 도메인 경계 포인터 | §3.4 양방향 포인터 확인 | 8개 인접 도메인 모두 포인터 존재 (S10-5: 5-2, 5-3 추가) |
| V-8 | PII 마스킹 정책 정합 | D2.0-07 + D2.0-06 §3 대조 | Deny 시 벡터 삽입 0건 |
| V-9 | CONFLICT_LOG 최신성 | 마지막 갱신 일자 확인 | 미해결 충돌 0건 |
| V-10 | 서브폴더 _index.md 존재 | 파일 존재 확인 | 4/4 존재 |

---

## 11. 보완 사항

| # | 발견 사항 | 심각도 | 대응 | 상태 |
|---|----------|--------|------|------|
| S-1 | §9에 CONFLICT_LOG 6건 충돌 이력 미참조 | MEDIUM | S8-5에서 §9.3 추가 완료 | ✅ DONE |
| S-2 | CONFLICT_LOG #006 SOT 원본 수정 대기 중 | LOW | Phase 3 후속 작업 (§7.5 P3-POST-1). **LOCK-MR-003 값 자체는 확정** (§2.1+Part2 기준). D2.0-06 §2.5.3 약식 표기는 비차단 — 구현에 영향 없음 | ⚠️ 비차단 OPEN |
| S-3 | §11 보완 사항 미작성 | LOW | S8-5에서 본 테이블 작성 완료 | ✅ DONE |
| S-4 | 5-2 File-Context-Strategy 도메인 경계 미정의 | MEDIUM | S10-5에서 §3.4에 5-2, 5-3 경계 추가 — 6-4는 메모리 데이터 소스, 5-2는 컨텍스트 구성 전략 | ✅ DONE |
| S-5 | 4-layer 기술 깊이 보완 확인 | LOW | 부록 §A에 4계층 정의 + B↔L 매핑 + 승격/강등 경로 + 스코어링 공식 완비 — 구현 상세는 Phase 1 의도적 위임 | ✅ 확인 |
| S-6 | P0-1 실행 시 QoD 컴포넌트 불일치 발견 | MEDIUM | D2.0-06 DEC-014 4요소 vs D6 3요소. D6 정본 우선으로 해결. CONFLICT_LOG #007 등록 완료 | ✅ DONE (2026-04-04) |
| S-7 | P0-2 절차에 구 용어 `layer`, `source_qod` 잔존 | LOW | P0-1에서 `scope`, `source_refs` FK 구조로 정정됨. **P0-2 프롬프트 전면 개정 완료** (2026-04-04): 구 용어(`layer`→`scope`, `source_qod`→`source_refs`, `session_id`/`memory_id`→`record_id`, `content`→`content_summary`, `embedding_id` 삭제) + Required/Optional 전수 매핑 + SourceQoDSchema 테이블 추가 + CHECK 제약 + 검증 19항목으로 보강 | ✅ DONE (2026-04-04) |
| S-8 | Phase 1 심층 재검증 (2026-04-13) | LOW | 11개 산출물 전수 교차 검증 — 14건 교정: EscalationPayload 표준 필드 통일 4건, 로깅 JSON 구조 통일(trace_id/lock_checks) 3건, 인터페이스 필드명/타입/반환 정합 3건(has_pii→pii_found, mask 반환 타입, 교차참조 섹션번호), 날짜 오류 2건, §0 교차참조 블록 누락 1건, DDL 확장 ALTER TABLE 누락 1건. 정본(MemoryRecordSchema/DDL/ABC/AUTHORITY_CHAIN) 전수 대조 완료 | ✅ DONE (2026-04-13) |

---

## 12. FINAL REVIEW 결과

> Phase 1 완료 판정 (2026-04-13)

| 항목 | 결과 | 비고 |
|------|------|------|
| 계획서 14+α 섹션 완성 | ✅ | §1~§14 + 부록 A/B/C 전체 작성 |
| AUTHORITY_CHAIN 완성 | ✅ | LOCK-MR-001~019 (19건), Phase 1 완료 검증 이력 추가 |
| CONFLICT_LOG 완성 | ✅ | #001~#006 RESOLVED, #006 비차단 OPEN (SOT 원본 대기) |
| 서브폴더 4개 + _index.md | ✅ | 01/02/03/04 각 _index.md 존재 (4/4) |
| MASTER_INDEX 갱신 | ✅ | Phase 1 ✅ 완료 (11/11), G1 PASS, Phase 2 진입 가능 |
| Phase 1 산출물 11건 | ✅ | P1-1~P1-11 전수 완료, 심층 재검증 14건 교정 |
| LOCK 변경 | ✅ | 0건 (19건 전체 무위반) |
| Phase 1→2 전환 게이트 | ✅ | G1 PASS (Part2 V1-P2 게이트 12항목) |

---

## 13. L3 전수 승급 계획

### 13.1 완성도 매트릭스

| 서브폴더 | E1 스키마 | E2 알고리즘 | E3 에러처리 | E4 테스트 | E5 모니터링 | E6 마이그레이션 | E7 문서화 | 현재 수준 |
|---------|----------|-----------|-----------|----------|-----------|-------------|---------|----------|
| 01_memory-hierarchy | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | L1 |
| 02_rag-pipeline | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | L1 |
| 03_vector-db | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | L1 |
| 04_memory-distillation | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | L1 |

### 13.2 승급 기준

- **L1 → L2**: E1(스키마) + E2(알고리즘) + E7(문서화) 완료
- **L2 → L3**: 전체 E1~E7 완료 + 통합 테스트 통과 + 코드 리뷰 완료

### 13.3 Phase 2~3 L3 완성도 최종 확정 매트릭스 (Path A drift fix Stage 1, 2026-05-18)

> **목적**: Phase 2 V1+V2_STACK ABSENT (V2 NEW 0 strict, 3-9 패턴 EXACT 직계) + Phase 3 P3-1~P3-5 5건 L3 완성도 최종 확정 + 🎉 ★★★ 누적 Δ 0 B / 0 LF 🎯 baseline byte 자동 복원 specialty milestone 처음 사례 + ★★ Phase 3 핵심 신규 이슈 LOCK-MR-005/006 vs GDPR Right to Erasure 충돌 정식 해소 P3-3 specialty + ★★ P3-4 3 first 사례 동시 specialty + ★★ 6-2 P2-3 gdpr_compliance.md direct inheritance Wave 2 두번째 사례 + ★ STAGE 6 파일럿 별도 트랙 specialty.

| 서브폴더 | V1 영역 | V2 NEW | V3 forward-defined | V-17 PASS | CON | FAIL |
|---------|--------|--------|-------------------|-----------|-----|------|
| 01_memory-hierarchy | 5 (P0-1 MemoryRecordSchema + P0-2 sqlite_ddl + P1-1 L0 + P1-2 L1 + P1-8 B3) | 0 (V2 EXTEND inheritance only P2-4 자동 승격 §V2 append) | 5 (P3-1 managed_db_v3 + P3-2 multi_tenancy_v3 + P3-3 gdpr_soc2_v3 + P3-4 dream_mode_v3 + P3-5 statistics_dashboard_v3 ALL 01 폴더 분포 — ★ V3 산출물 ALL 분포 specialty) | 0 | 0 | 0 |
| 02_rag-pipeline | 4 (P1-4 json_graphrag + P1-9 dcl_basic + P1-10 rag_6stage_pipeline + P1-11 hybrid_search) | 0 (V2 EXTEND inheritance only P2-3 Neo4j GraphRAG §V2 append json_graphrag.md) | 0 (Phase 3 V3 산출물 01 폴더 분포 specialty) | 0 | 0 | 0 |
| 03_vector-db | 3 (P0-3 chroma_collection_strategy + P0-4 vectorstore_abc + P1-3 chroma_adapter) | 0 (V2 EXTEND inheritance only P2-1 Qdrant 전환 §V2 append chroma_adapter.md + P2-2 V1→V2 마이그레이션 §V2 append chroma_collection_strategy.md) | 0 (Phase 3 V3 산출물 01 폴더 분포 specialty) | 0 | 0 | 0 |
| 04_memory-distillation | 3 (P1-5 semantic_cache + P1-6 export_import + P1-7 pii_masking) | 0 (V2 EXTEND inheritance only) | 0 | 0 | 0 | 0 |
| **합계** | **15 V1 / 17 .md (V1 .md 13 + _index×4) / 17 (V1+V2 stack ALL 17 단일 .md 파일 base) — 전체 production 17 .md + _verification 1 meta = 18 base (.sql + .py 2 코드 별도)** | **0 NEW strict (V1+V2_STACK ABSENT 패턴 3-9 EXACT 직계)** | **5 forward-defined (5 NEW V3 산출물 01 폴더 분포 + 부가 산출물 postgresql_adapter.py 어댑터 스텁 01 폴더 분포 + CONFLICT_LOG 신규 RESOLVED 항목 P3-3 LOCK-MR-005/006 vs GDPR 충돌 = 통산 7 산출물 Phase 4 implementation 단계 별도)** | **0** | **0** | **0** |

**6 sub-section milestone**:
1. **🎉 ★★★ 누적 Δ 0 B / 0 LF 🎯 baseline byte 자동 복원 specialty milestone 처음 사례**: P3-1 -6 + P3-2 -9 + P3-3 +8 + P3-4 0 + P3-5 +7 = 0 B 통산 5 P3 byte 자동 복원 (종합계획서 진입 baseline 157,541 / 069C5CF14549C6DE → P3-5 종료 157,541 / 4BF23F9579730FDD SHA만 변경 byte EXACT 복원, 15 char-swap fixes / 8 drift categories / 13 line edits ALL textual notation only) — 3-7 Wave 1 #9 + 3-9 Wave 1 #10 + 6-2 Wave 2 #14 + 6-3 Wave 2 #15 NO-DRIFT 100% ZERO write 패턴과 다른 6-4 mixed pattern 8 drift categories Wave 2 누적 pattern specialty 통산 milestone (6-1 Wave 2 #13 mixed pattern 4 fix 패턴과 부분 유사 + 4-2/4-4 partial pattern 1 fix 패턴 직계 통산 5~9번째 사례)
2. **★★ Phase 3 핵심 신규 이슈 정식 해소 P3-3 specialty milestone**: LOCK-MR-005/006 (L2/L3 무기한 보존) vs GDPR Right to be Forgotten 충돌 — `<!-- LOCK-MR-006 의 V3 적용 확장 -->` 명시 + "deprecated 전환" 메커니즘 범위 확장 + 재정의 0건 + CONFLICT_LOG 신규 RESOLVED 항목 등재 산출물 Phase 4 implementation 단계 별도 + Phase 4 entry-gate 7 조건 중 핵심 (§6.2 SHELL→FULL 7건 외 Phase 3 신규 정의 이슈 specialty)
3. **★★ P3-4 3 first 사례 동시 specialty milestone**: 1️⃣ P2 numbering propagation drift first 사례 specialty (자동 승격 P2-4 + 메모리 충돌 해소 P2-5 §7.6 L1335/L1373 정본 vs P3-4 cite "P2-2/P2-3" 9 char-swap occurrences in 6 line edits) + 2️⃣ file name + word order swap correction first 사례 specialty (memory_decay_b3.md → B3_memory_decay.md case + word order swap) + 3️⃣ forward-defined inheritance pattern P3-4 specialty first 사례 (Phase 2 P2-4 promotion_automation.md + P2-5 memory_conflict_resolution.md 실측 production 산출물 baseline 시점 미존재 → Phase 4 implementation 단계 inheritance pattern)
4. **★★ 6-2 P2-3 gdpr_compliance.md 20,905 B (361L) direct inheritance cross-domain specialty milestone Wave 2 두번째 사례**: Wave 2 #14 ✅ SPEC COMPLETE 2026-05-18 NO-DRIFT 100% Wave 2 첫 사례 inheritance, cross-domain direct inheritance specialty pattern (3-9 LOCK-BM-09 + 3-7 P3-4 LOCK-BM-09 + 6-3 P3-3 6-2/3-7 cross-handoff verbatim inheritance pattern 직계 Wave 2 두번째 사례, P3-3 절차 1 GDPR 7 원칙 + 6 권리 + DPIA + Art. 33 72h 통보 ALL 6-2 P2-3 gdpr_compliance.md 정본 EXACT 직계 inheritance)
5. **★★ distinct 7 unique target domains 7/7 ALL 도달 100% milestone**: §7.6 L1665 정본 EXACT MATCH 100% (6-2 + 6-7 + 6-1 + 6-12 + 6-5 + 6-6 + 5-2 = 7/7 통산 5 P3 도메인 완성, P3-1 6-2+6-7 + P3-2 6-2+6-12+5-2 + P3-3 6-2+6-12 + P3-4 6-6+6-5 + P3-5 6-1+6-12 = 통산 11 inline → distinct 7 unique target domains, target plan forward-defined ALL 도달)
6. **★ STAGE 6 파일럿 별도 트랙 specialty + V1+V2_STACK ABSENT 패턴 (3-9 EXACT 직계 Wave 2 첫 사례)**: upstream 0건 자동 PASS (CROSS_REF_MATRIX §1 Wave 2 row "6-4 Memory-RAG \| (없음, 또는 STAGE 6 파일럿 별도)" UPSTREAM_INCOMPLETE:6-4 자동 PASS, 3-2 Multimodal Wave 1 #4 / 3-3 PKM Wave 1 #5 패턴과 다른 6-4 단독 트랙 specialty Wave 2 단독 도메인 첫 사례) + V1+V2_STACK ABSENT 패턴 (V2 NEW 0 strict, 3-9 V2 33 항목 11 file §V2 통합 stack 패턴과 유사 ABSENT 도메인 specialty Wave 2 첫 ABSENT 사례)

**🎉 ★★★ Wave 2 #16 도메인 P3 5/5 ALL ✅ SPEC 검증 매트릭스 도달 + ★★★ 누적 Δ 0 B / 0 LF 🎯 baseline byte 자동 복원 specialty milestone 처음 사례 milestone 완성 달성**: P3-1 매니지드 DB V3 + P3-2 멀티테넌시 V3 + P3-3 GDPR/SOC-2 V3 + P3-4 Dream Mode V3 + P3-5 통계 대시보드 V3 ALL tcv1 first-pass-after-fix CONFIRMED, R cascade 통산 **205 verifications + 15 char-swap fixes / 8 drift categories / 13 line edits ALL textual notation only** (P3-1 41 + P3-2 42 + P3-3 41 + P3-4 40 + P3-5 41 = 205 verifications, R₁~R₁₀ first-pass 10 + R₁₁ fix N + R₁₂ post-fix 3 round × 10 = 30 per P3 + 8 drift categories) — Wave 2 누적 pattern specialty 통산 milestone (3-7 + 3-9 + 6-2 + 6-3 NO-DRIFT 100% ZERO write 패턴과 다른 6-4 mixed pattern + 6-1 mixed pattern 4 fix 패턴과 부분 유사 + 4-2/4-4 partial pattern 1 fix 패턴 직계 통산 5~9번째 사례)

**★★ Phase 3 핵심 신규 이슈 정식 해소 P3-3 specialty milestone**: LOCK-MR-005/006 vs GDPR Right to be Forgotten 충돌 정식 해소, `<!-- LOCK-MR-006 의 V3 적용 확장 -->` 명시 + "deprecated 전환" 메커니즘 범위 확장 + 재정의 0건 + CONFLICT_LOG 신규 RESOLVED 항목 등재 산출물 (Phase 4 implementation 단계 별도)

**★★ P3-4 3 first 사례 동시 specialty milestone**: P2 numbering propagation drift first + file name + word order swap first + forward-defined inheritance pattern P3-4 specialty first 3 first 사례 동시

**★★ 6-2 P2-3 gdpr_compliance.md direct inheritance cross-domain specialty Wave 2 두번째 사례**: 3-9 LOCK-BM-09 + 3-7 P3-4 LOCK-BM-09 + 6-3 P3-3 6-2/3-7 cross-handoff verbatim inheritance pattern 직계 Wave 2 두번째 사례 cross-domain direct inheritance specialty

**★ distinct 7 unique target domains 7/7 ALL 도달 100% milestone**: §7.6 L1665 정본 EXACT MATCH 100% (6-2+6-7+6-1+6-12+6-5+6-6+5-2)

**★ STAGE 6 파일럿 별도 트랙 specialty (upstream 0건 자동 PASS Wave 2 단독 도메인 첫 사례)**: CROSS_REF_MATRIX §1 6-4 row upstream 0건 자동 PASS, 3-2/3-3 Wave 1 패턴과 다른 6-4 단독 트랙 Wave 2 단독 도메인 첫 사례 specialty

**★ V1+V2_STACK ABSENT 패턴 (3-9 EXACT 직계 Wave 2 첫 ABSENT 사례)**: V2 NEW 0 strict, 3-9 V2 33 항목 11 file §V2 통합 stack 패턴과 유사 ABSENT 도메인 specialty Wave 2 첫 ABSENT 사례, V1 영역 17 기존 file 위 §V2 의미론적 누적 stack — NEW 파일 0

**★ downstream 5-2 File-Context (Wave 4 #30 ⬜ STAGE 9 Phase C 완료 read-only) + 6-11 Hologram (Wave 3 #28 ⬜) forward-defined inheritance pattern** (3-2 + 6-2 + 6-3 STAGE 9 RO 5-2 sandbox-only 처리 specialty + 6-1 + 6-3 6-11 forward-defined 패턴 직계, STAGE 9 RO §5 sandbox 전용 reference 처리 specialty inheritance + abort 3 발화 조건 축소)

**§12 FINAL REVIEW ✅ Phase 1 완료 판정 (2026-04-13) ALL 8 항목 ✅ APPROVED SKIP no-op 자동 inheritance** (§13.X-1 처리, 3-7/4-2/4-4 ✅ APPROVED 패턴 직계, 6-3 14/16 PARTIAL APPROVED + 6-1 CONDITIONAL APPROVED + 3-9 + 6-2 ⬜ PENDING 패턴과 다른 6-4 specific Phase 1 ALL ✅ APPROVED specialty, Phase 3 completion ✅ marker §7.6 헤더 + §7.6.1 G 매트릭스 + SOT2_MASTER + PROGRESS 3 위치 별도 매핑, §12 자체 갱신 design choice 부재 통산)

**★ 5 NEW 산출물 ALL P3 mapped + Phase 4 entry-gate 7/7 [x] 정합 milestone**: managed_db_v3 + multi_tenancy_v3 + gdpr_soc2_v3 + dream_mode_v3 + statistics_dashboard_v3 = 5/5 ALL Phase 4 entry-gate ready (P3-1 + P3-2 + P3-3 + P3-4 + P3-5 1:1 mapping, §7.6 L1661 정본 EXACT 정합) + Phase 3→Phase 4 인계 게이트 7/7 [x] (NEW 산출물 5건 + LOCK-MR-005/006 vs GDPR 정식 해소 + LOCK-MR 19 unique 변경 0 + CONFLICT #004 + #006 처리 + 7 cross-handoff RESOLVED + Phase 1 11/11 + Phase 2 V2 SHA UNCHANGED + 5 검증 ALL)

---

## 14. 실행 약점 대응 계획

| # | 약점 | 위험도 | 대응 |
|---|------|--------|------|
| W-1 | STEP7-D 5계층 vs D2.0-06 4계층 혼동 | HIGH | R-64-1 용어 통일 규칙 강제 + CONFLICT_LOG 상시 모니터링. 코드 레벨에서 `MemoryTier` enum을 L0~L3 4값으로 고정하고, STEP7-D L4(Archive)는 V2+ 확장 플래그로 분리 |
| W-2 | V1→V2 벡터 DB 마이그레이션 데이터 손실 | MEDIUM | 03_vector-db/migration_v1_v2.md에 단계별 검증 + 롤백 절차 명시. Chroma→Qdrant 전환 시 collection별 count 교차 검증 + embedding 차원 일치 확인 |
| W-3 | QoD 임계값 튜닝 부재 | MEDIUM | V1에서 기본값(0.4/0.7) 적용 후 V2에서 A/B 테스트 기반 조정. 초기 운영 시 QoD 분포 히스토그램 수집하여 V2 임계값 근거 확보 |
| W-4 | 메모리 폭주 (루프/멀티툴) | HIGH | LOCK-MR-019 준수 + D7 승인 게이트 연동 + 저장 카운터 모니터링. 분당 저장 횟수 상한(rate limiter) 구현하여 루프 중 원문 저장 차단 |
| W-5 | PII 우회 (regex 한계) | MEDIUM | V1 regex 기본 + V2에서 NER 보강 (S7D-066). V1에서도 한국어 주민번호 13자리·전화번호·이메일·카드번호 패턴 커버리지 95% 이상 목표 |
| W-6 | Semantic Cache 엣지 케이스 | MEDIUM | cosine ≥ 0.95 임계값이 의미적으로 다른 질의를 동일 캐시로 반환할 수 있음. V1에서는 캐시 히트 시 원본 질의와 캐시 질의의 토큰 길이 차이가 30% 이상이면 캐시 우회 로직 추가 |
| W-7 | RAG 파이프라인 장애 전파 | HIGH | 6-Stage 중 Embed/Store 단계 실패 시 하위 단계로 전파되어 전체 검색 불능. 단계별 circuit breaker 패턴 적용 + Retrieve 단계에 fallback(BM25-only) 경로 확보 |
| W-8 | 교차 도메인 경계 드리프트 | MEDIUM | 10개 소비 도메인(부록 B)이 6-4 내부 구현에 직접 의존하면 경계 침식 발생. API 계약(VectorStore 어댑터 4개 메서드)만 공개하고, 내부 스키마 직접 참조 금지. 분기별 경계 리뷰 시행 |
| W-9 | D2.0-06 내부 TTL 모호성 잔존 | LOW | LOCK-MR-003 L0 TTL에 대해 D2.0-06 §2.1과 §2.5.3 간 표기 불일치 존재 (CONFLICT_LOG #006). SOT 원본 수정 전까지 §2.1+Part2 기준을 정본으로 고정하되, §2.5.3 인용 시 반드시 #006 주석 첨부 |

---

## 부록 §A — 메모리 계층 상세 스키마

### A.1 4계층 정의 (D2.0-06 §2 LOCK 기준)

| 계층 | 정의 | B-Series | 저장소 (V1) | TTL | 용량 |
|------|------|---------|-----------|-----|------|
| **L0** | Session Memory (세션/즉시) | B-4 Working | 인메모리 (Python dict) + SQLite | session_end 또는 30일 ⚠️ #006 | 200K 토큰 |
| **L1** | Project Memory (프로젝트) | B-1 Episodic | SQLite + Chroma | 90일 (30일 연장 가능) | 10,000 항목 |
| **L2** | Long-term Knowledge (장기/글로벌) | B-3 Semantic | SQLite + Chroma + KG | 무기한 (QoD 재평가 주기) | 무제한 |
| **L3** | Procedural Memory (절차/템플릿) | B-2 Procedural | SQLite + Chroma + KG | 무기한 (deprecated 폐기) | 무제한 |

### A.2 (Lx, By) 매핑 규칙 (LOCK)

| 저장 조합 | 대표 예시 | 기본 저장 레벨 |
|----------|----------|-------------|
| (L0, B-4) | 현재 대화 컨텍스트, 단기 상태, 작업 중 힌트 | L0 |
| (L1, B-1) | 프로젝트 진행 맥락, 결정, 요약 | L1 |
| (L2, B-3) | 검증/요약된 지식 (검색 재사용) | L2 |
| (L3, B-2) | 플레이북, 루틴, 템플릿, 절차 | L3 |

### A.3 승격/강등 경로

```
L0 (Session) ──세션 종료 시 자동──→ L1 (Project)
                                      │
                                      ├─ 재참조 3회+ / QoD ≥ 0.7 ──→ L2 (Long-term)
                                      │                                │
                                      │                                ├─ 크로스 프로젝트 재참조 ──→ L3 (Procedural)
                                      │                                │
                                      │                                └─ 90일 미참조 ──→ 강등 (L1로)
                                      │
                                      └─ TTL 만료 (90일) ──→ 삭제 또는 archived

L3 (Procedural) ──180일 미참조 (V2+)──→ Archive (V2+ 확장, 정본 4계층 외)
```

### A.4 승격 스코어링

```python
promotion_score = access_count * 0.4 + recency * 0.3 + confidence * 0.3
# L1→L2 승격: promotion_score ≥ threshold OR QoD ≥ 0.7 OR 사용자 명시
```

---

## 부록 §B — 소비 도메인 매트릭스

> 6-4 Memory-RAG-Storage를 참조/소비하는 도메인 목록

| 소비 도메인 | 참조 대상 | 참조 유형 |
|-----------|----------|----------|
| **1-1 Verifier-Reasoning** | L2 지식 검색, RAG 파이프라인 | API 호출 |
| **1-2 Auxiliary-Modules** | I-14 요약기→메모리 승격, I-2 Context Builder→RAG | 모듈 연동 |
| **3-3 PKM** | L2 지식 저장/검색, KG 노드 | 데이터 공유 |
| **3-8 Conversation-A2A** | 세션 메모리(L0), 대화 컨텍스트 | 세션 참조 |
| **6-1 UI-UX** | 메모리 API, 저장 확인 UI | API + UI 연동 |
| **6-2 Security** | PII 마스킹, 저장 정책 | 정책 적용 |
| **6-3 Agent-Teams** | 에이전트 메모리 공유, 팀 컨텍스트 | 세션/프로젝트 메모리 |
| **6-5 SDAR** | 메모리 상태 모니터링 | 상태 리포트 |
| **6-11 Hologram-Main-LLM** | RAG 검색 결과 컨텍스트 주입 | RAG 연동 |
| **6-12 Event-Logging** | 메모리 감사 로그 | 로그 기록 |

---

## 부록 §C — LOCK 전수 추적표

> LOCK-MR-001~019 각각의 서브폴더별 구현·검증 위치

| LOCK ID | 항목 | 구현 서브폴더 | 검증 파일 |
|---------|------|-------------|----------|
| LOCK-MR-001 | 4계층 메모리 | 01 | 01/_index.md |
| LOCK-MR-002 | B↔L 매핑 | 01 | 01/_index.md |
| LOCK-MR-003 | L0 TTL | 01 | 01/l0_session_memory.md |
| LOCK-MR-004 | L1 TTL | 01 | 01/l1_project_memory.md |
| LOCK-MR-005 | L2 보존 | 01 | 01/l2_longterm_knowledge.md |
| LOCK-MR-006 | L3 보존 | 01 | 01/l3_procedural_memory.md |
| LOCK-MR-007 | 6-Stage RAG | 02 | 02/_index.md |
| LOCK-MR-008 | Hybrid Search α | 02 | 02/retrieve_generate.md |
| LOCK-MR-009 | Similarity threshold | 02 | 02/retrieve_generate.md |
| LOCK-MR-010 | Semantic Cache | 04 | 04/semantic_cache.md |
| LOCK-MR-011 | BGE-M3 임베딩 | 03 | 03/embedding_strategy.md |
| LOCK-MR-012 | V1 Chroma | 03 | 03/chroma_adapter.md |
| LOCK-MR-013 | V2 Qdrant | 03 | 03/qdrant_adapter.md |
| LOCK-MR-014 | 어댑터 인터페이스 | 03 | 03/_index.md |
| LOCK-MR-015 | Deny 벡터 금지 | 04 | 04/storage_policy.md |
| LOCK-MR-016 | L3 활성 게이트 | 01 | 01/l3_procedural_memory.md |
| LOCK-MR-017 | project_id 격리 | 01 | 01/l1_project_memory.md |
| LOCK-MR-018 | 저장 전 확인 | 04 | 04/storage_policy.md |
| LOCK-MR-019 | 루프 폭주 방지 | 04 | 04/storage_policy.md |

---

### 7.7.2 Phase 4 SPEC Stage B 결과 요약 (6-4 Memory-RAG-Storage — 2026-05-27)

> **세션 chain**: `phase4_6-4_spec_2026-05-27` (Wave 2 #16, P4 5/5 ALL ✅ Stage B production-write)
> **🎉🎉🎉🎉🎉🎉🎉🎉 통산 milestone**: **6-4 Memory-RAG-Storage 도메인 Phase 4 SPEC Stage B ✅ COMPLETE** + **통산 16/30 SPEC = 53.3% milestone** + Wave 1 12/12 SPEC + Wave 2 4/9 SPEC fourth domain milestone first

#### A. Stage B production write 산출물 매트릭스 (5 V3 NEW + 1 어댑터 + AUTHORITY append + CONFLICT_LOG #007 NEW + _verification × 5 NEW)

| 위치 | 파일 | 상태 | byte | LF | SHA-16 |
|------|------|------|------|----|--------|
| 01_memory-hierarchy/ | managed_db_v3.md (NEW) | APPROVED | 19,125 | 437 | `D713F79A06A57F6A` |
| 01_memory-hierarchy/ | postgresql_adapter.py (NEW) | APPROVED | 7,658 | 205 | `204CB91AB0D89D3A` |
| 01_memory-hierarchy/ | multi_tenancy_v3.md (NEW) | APPROVED | 17,130 | 401 | `2C8B1455DD67886E` |
| 01_memory-hierarchy/ | gdpr_soc2_v3.md (NEW) | APPROVED | 20,900 | 556 | `BA45EA6AEA6C61A1` |
| 01_memory-hierarchy/ | dream_mode_v3.md (NEW) | APPROVED | 14,650 | 368 | `21FAFD6F34D15CEE` |
| 01_memory-hierarchy/ | statistics_dashboard_v3.md (NEW, FINAL P4) | APPROVED | 13,361 | 374 | `287531BEF72E1ED2` |
| _verification/ | phase4_v3_p4-1_promotion_report.md (NEW) | APPROVED | 1,873 | 55 | `B9874E8DFF030194` |
| _verification/ | phase4_v3_p4-2_promotion_report.md (NEW) | APPROVED | 2,345 | 65 | `9560A7B37A484631` |
| _verification/ | phase4_v3_p4-3_promotion_report.md (NEW) | APPROVED | 3,444 | 94 | `F8D7D489692B24E0` |
| _verification/ | phase4_v3_p4-4_promotion_report.md (NEW) | APPROVED | 3,112 | 82 | `780C5F4F7BC61FDA` |
| _verification/ | phase4_v3_p4-5_promotion_report.md (NEW, FINAL) | APPROVED | 3,003 | 95 | `24C75D37A8F21A5B` |
| **_verification × 5 통산** | (5 NEW reports aggregate) | — | **13,777** | **391** | — |
| (root) | AUTHORITY_CHAIN.md (UPDATED) | active | 11,720 | 180 | `425AF3B53BA7B56D` (post §5 STAGE 9 + §6 V3 적용 확장 + §7 SPEC Stage B 완료 marker reorder, Δ +4,920 B / +74 LF from baseline 6,800 B / 106 LF) |
| (root) | CONFLICT_LOG.md (UPDATED) | active | 7,619 | 115 | `8D0F24DF204077FD` (post-Round-1-fix D-R1-1 #006/#007 순서 정정 + #007 NEW RESOLVED + #004 갱신, Δ +1,650 B / +12 LF, byte 동일 but SHA 변경 due to row reorder) |

**총 5 V3 NEW + 어댑터 스텁** = 통산 92,824 B / 2,341 LF (5 .md V3 NEW = 85,166 B / 2,136 LF ≥ ALL threshold 충족: ≥400/400/500/350/350 ALL PASS).

#### B. LOCK / DEFINED-HERE / FABRICATION 검증

- **LOCK 19 정본 명문 변경 0** (LOCK-MR-001~019) — AUTHORITY_CHAIN §2 LOCK 레지스트리 19 entries 변경 없음.
- **V3 적용 확장 주석 강제 적용** (재정의 아님): LOCK-MR-006 `<!-- LOCK-MR-006 의 V3 적용 확장 -->` + LOCK-MR-017 `<!-- V3 EXTENSION, NOT REDEFINITION -->` + L4 Archive CONFLICT #004 V2+ 확장.
- **DEFINED-HERE 0** 통산.
- **FABRICATION 0** 통산.

#### C. CONFLICT_LOG cascade

| # | 상태 | 비고 |
|---|------|------|
| #001~#005 | RESOLVED 통산 | 변경 없음 |
| #004 | RESOLVED + 갱신 (2026-05-27 P4-4) | L4 Archive V2+ Dream Mode 활용 명시 |
| #006 | ⚠️ RESOLVED (Plan 반영) | 변경 없음 |
| **#007 NEW** | **✅ RESOLVED (2026-05-27 P4-3)** | **LOCK-MR-005/006 vs GDPR Right to Erasure Phase 3 핵심 신규 이슈 정식 해소 specialty milestone** |
| W-1~W-3 | RESOLVED 통산 | 변경 없음 |
| **OPEN** | **0** | Phase 4 신규 충돌 0 |

#### D. abort 9종 + R cascade

- **abort 9종 ALL NOT FIRED self-fire 0** 통산 — Stage A 585 verifications + ④⑤⑥⑦ Round 1~7 + Stage B production-write 추가 cascade.
- **R cascade truly_converged_v_FINAL_v1** post-Stage-B-write CONFIRMED.
- **🎯 CROSS_HANDOFF_DRIFT NOT FIRED 18-consecutive milestone REACHED** (6-3 P4-6 13 + 6-4 P4-1~P4-5 = 18 consecutive).

#### E. distinct 7 cross-handoff (Stage B verify EXACT MATCH 100%)

| # | 도메인 | 방향 | EXACT MATCH |
|---|--------|------|-----------|
| 1 | 5-2_File-Context (Wave 4 #30) | sandbox-only reference 발신 측 specialty first | ✅ |
| 2 | 6-2_Security-Governance (Wave 2 #14 ✅) | bidirectional EXACT (gdpr_compliance.md 361L direct inheritance 재작성 0건) | ✅ |
| 3 | 6-7_RT-BNP-DCL (Wave 2 #19) | forward-defined (Qdrant V2 ↔ 매니지드 RDB) | ✅ |
| 4 | 6-1_UI-UX-System (Wave 2 #13 ✅) | bidirectional forward-defined (대시보드 UI) | ✅ |
| 5 | 6-12_Event-Logging (Wave 3 #29) | forward-defined (SOC-2 LogEvent) | ✅ |
| 6 | 6-5_SDAR-System (Wave 2 #17) | forward-defined (Dream Mode result input) | ✅ |
| 7 | 6-6_Self-Evolution-System (Wave 2 #18) | forward-defined (S-7 Evolution Scheduler) | ✅ |

#### F. Phase 5 entry-gate (G4-1~G4-7) 통산

ALL ✅ 5 V3 NEW 전수 PASS (P4-1+P4-2+P4-3+P4-4+P4-5 FINAL).

#### G. Pattern milestone

- **🎉🎉🎉 Pattern A 100-단위 milestone first 도달** (P4-3, 통산 100번째 사례).
- **🎉🎉🎉 Pattern B 100-단위 milestone first 도달** (P4-5 FINAL, 통산 100번째 사례).
- **Pattern A 통산 102 + Pattern B 통산 100** post Stage B.

#### H. 통산 milestone markers (Stage B 출력)

- `[DOMAIN_PHASE_4_PRODUCTION_PROMOTION_COMPLETE:6-4 — 2026-05-27]` ✅
- `[SPEC_STAGE_B_COMPLETE:6-4 — 2026-05-27]` ✅
- `[CUMULATIVE_SPEC_COUNT:16/30]` 🎉🎉🎉🎉🎉🎉🎉🎉
- `[WAVE_2_FOURTH_DOMAIN_SPEC_COMPLETE_MILESTONE:6-4 — 2026-05-27]` 🎉🎉🎉🎉🎉🎉
- `[FINAL_P4_TASK_SPECIALTY_12TH_CASE_CONFIRMED:6-4_P4-5_FINAL]` ⭐⭐⭐⭐⭐⭐
- `[7_CONSECUTIVE_RO_FALSE_SPECIALTY_FIRST_MILESTONE_REACHED:6-4]` ⭐⭐⭐
- `[DOMAIN_5/5_FULL_NO_DRIFT_MILESTONE:6-4]` ⭐⭐⭐
- `[5_2_EXTERNAL_5_DEPS_SENDER_SPECIALTY_FIRST_P4_2_TRIGGER:6-4]` ⭐⭐⭐
- `[LOCK_MR_005_006_VS_GDPR_RIGHT_TO_ERASURE_FINAL_RESOLUTION_SPECIALTY:6-4_P4_3]` ⭐⭐⭐
- `[6_2_GDPR_COMPLIANCE_361L_DIRECT_INHERITANCE_EXACT_MATCH_100_PERCENT_VERIFIED:6-4_P4_3]` ⭐⭐⭐
- `[M_3_P2_4_P2_5_MAIN_BENEFICIARY_TRIGGER_SPECIALTY:6-4_P4_4]` ⭐⭐
- `[PATTERN_A_100TH_MILESTONE_FIRST_REACHED:6-4_P4_3]` 🎉🎉🎉
- `[PATTERN_B_100TH_MILESTONE_FIRST_REACHED:6-4_P4_5_FINAL]` 🎉🎉🎉
- `[NO_DRIFT_DIRECT_PATH_5_CONSECUTIVE_FINAL:6-4]` ⭐
- `[CROSS_HANDOFF_DRIFT_NOT_FIRED_18_CONSECUTIVE_MILESTONE_REACHED:6-4]` ⭐⭐⭐
- `[CONFLICT_LOG_007_NEW_RESOLVED:LOCK-MR-005/006_vs_GDPR_Right_to_Erasure — 2026-05-27]` ⭐⭐⭐
- `[POST_STAGE_B_AUDIT_TRULY_CONVERGED_V1:6-4 — 2026-05-27]` ⭐
- `[PHASE5_READY:6-4 — 2026-05-27]` ✅

**다음 진입**: Wave 2 #17 6-5 SDAR-System DAG #17 (별도 대화창, P4=3 추정, 6-4 P4-4 직계 메모리 자가 진단 inheritance).

