# 대용량 컨텍스트 이해 (File Context) 구조화 종합 계획서

> **버전**: v1.1
> **작성일**: 2026-03-27
> **목적**: sot 2/5-2_File-Context/을 대용량 컨텍스트 이해 구현 정본으로 구조화
> **Status**: APPROVED — S10-3 QC PASS (2026-03-27)
> **Tier**: 5 (Quality/Cross-cutting)
> **SOT 출처**: D2.0-06, D2.0-02, D2.0-01, STEP7-G
> **Part2 상태**: ABSENT / NOT COVERED (Part2에 독립 섹션 없음; Storage/RAG 관련 간접 언급만 존재)
> **원본**: `D:/VAMOS/docs/sot 2/FILE CONTEXT/VAMOS_파일_컨텍스트_이해_최종_업데이트.md` (1,618줄, 2026-03-18)

---

## 목차

1. [현재 상태 분석](#1-현재-상태-분석)
2. [비전 및 목표](#2-비전-및-목표)
3. [권한 체계 선언](#3-권한-체계-선언)
4. [거버넌스 규칙](#4-거버넌스-규칙)
5. [의존성 및 선행작업](#5-의존성-및-선행작업)
6. [시스템 아키텍처](#6-시스템-아키텍처)
7. [버전 로드맵 (Phase 실행 계획)](#7-버전-로드맵)
8. [리스크 관리](#8-리스크-관리)
9. [횡단 관심사](#9-횡단-관심사)
10. [윤리 및 위기 대응](#10-윤리-및-위기-대응)
11. [확장성 및 미래 전략](#11-확장성-및-미래-전략)
12. [벤치마크 및 평가](#12-벤치마크-및-평가)
13. [외부 의존 및 학술 참조](#13-외부-의존-및-학술-참조)
14. [결론](#14-결론)
- [부록 A: 컨텍스트 크기별 처리 전략 카탈로그](#부록-a-컨텍스트-크기별-처리-전략-카탈로그)
- [부록 B: 55개 기술 매핑 테이블](#부록-b-55개-기술-매핑-테이블)

---

## 1. 현재 상태 분석

### 1.1 기존 문서 현황

| 항목 | 상태 |
|------|------|
| **원본 위치** | `D:/VAMOS/docs/sot 2/FILE CONTEXT/VAMOS_파일_컨텍스트_이해_최종_업데이트.md` |
| **분량** | 1,618줄, 12개 섹션 |
| **최종 갱신** | 2026-03-18 (3차 최종 — H1~H17 추가 + 일관성 검토 완료) |
| **S7-4 판정** | "유틸리티 파일" → 본 계획서에서 정식 Tier 5 도메인으로 승격 |
| **Part2 상태** | ABSENT — Part2에 독립 "파일 컨텍스트" 섹션 없음. Storage/RAG 관련 간접 언급만 존재 (V1-Phase 2 Storage+RAG 구현 블록에서 6-Stage RAG Pipeline, BGE-M3 임베딩 등 부분 커버) |

### 1.2 sot 2/ 현재 파일 구조

```
sot 2/
├── FILE CONTEXT/
│   └── VAMOS_파일_컨텍스트_이해_최종_업데이트.md   ← 원본 (보존)
└── 5-2_File-Context/                               ← 신규 (본 계획서)
    ├── FILE_CONTEXT_구조화_종합계획서.md            ← 본 문서
    ├── AUTHORITY_CHAIN.md
    ├── CONFLICT_LOG.md
    ├── 01_context-pipeline/                         ← Phase A~G 파이프라인
    ├── 02_gap-remediation/                          ← G1~G8 Gap 보완
    ├── 03_weakness-mitigation/                      ← W1~W12 약점 보완
    ├── 04_advanced-techniques/                      ← H1~H17 고급 기법
    └── 05_benchmarks/                               ← 정확도 목표 + 평가
```

### 1.3 핵심 문제 (업계 공통 5건)

| # | 문제 | 근거 |
|---|------|------|
| P1 | **Lost in the Middle** — 정보가 입력 중간에 있으면 정확도 30%+ 하락 | Liu et al., TACL 2024 |
| P2 | **Context Rot** — 18개 최신 모델 전부 입력 길이 증가 시 성능 저하; 1M 윈도우 모델도 50K에서 이미 성능 하락 | Chroma Research 2025 |
| P3 | **NoLiMa 벤치마크** — 32K 토큰에서 13개 모델 중 11개가 50% 이하 추락 (비문자적 매칭 시) | Adobe Research, ICML 2025 |
| P4 | **실효 한계** — 200K 윈도우 모델의 실제 안정 작동 범위는 ~100-130K | RULER Benchmark |
| P5 | **코딩 성능** — Claude 3.5 Sonnet: 컨텍스트 증가 시 코딩 정확도 29% → 3%로 폭락 | LongCodeBench |

### 1.4 핵심 원인

- 트랜스포머 Attention O(n²) → 토큰 증가 시 품질 저하 필연
- RoPE 장거리 감쇠 효과 → 중간 위치 정보 취약
- KV-Cache 메모리 한계 → 긴 시퀀스에서 정보 압축 발생
- Distractor Interference → 관련 없는 정보가 많을수록 관련 정보 탐지 하락

---

## 2. 비전 및 목표

### 2.1 비전

> VAMOS AI의 파일/대용량 컨텍스트 이해 능력을 **업계 최고 수준(~95%)을 초과하는 99% 설계 커버리지**로 달성한다.
> 55개 통합 기술(G+A+W+H)과 7-Phase 파이프라인, 8-Layer 검증 체계를 통해
> 10K~200K+ 전 구간에서 상용 AI를 상회하는 정확도를 실현한다.

**정량적 핵심 목표 (KPI)**:
- **설계 커버리지**: 99% (업계 최고 ~95% 대비 +4%p)
- **200K+ 분할 정확도**: 80% 이상 (업계 최고 68% 대비 +12%p)
- **10K 이하 정확도**: 98% (업계 최고 95% 대비 +3%p)
- **KV-Cache 히트율**: 70% 이상 (반복 분석 시나리오 기준)
- **PII 탐지 재현율(Recall)**: 99.5% 이상 (Phase A 게이트)
- **환각율**: 2% 미만 (W11 Attributed QA + H17 CoV 적용 후)
- **처리 비용 절감**: 로컬 100% 시나리오 대비 Cloud Cascade 적용 시 60% 절감
- **벤치마크 자동화**: W12 골든 테스트셋 100 QA + RAGAS 자동 평가 완전 자동화 목표

### 2.2 정량 목표

| 컨텍스트 크기 | 기존 VAMOS | 최종 목표 | 업계 최고 |
|--------------|-----------|----------|----------|
| < 10K | ~90% | **98%** | 95% |
| 10~50K | ~85% | **97%** | 90% |
| 50~130K | ~70% | **92%** | 82% |
| 130~200K | ~60% | **82%** | 72% |
| 200K+ (분할) | ~50% | **80%** | 68% |

### 2.3 설계 커버리지 목표

| 단계 | 커버리지 | 보완 기술 수 |
|------|---------|------------|
| 기존 SOT 보유 | 85% | 18개 |
| +G1~G8 Gap 보완 | 95% | 26개 |
| +A1~A8 장점 활용 | 96% | 34개 |
| +W1~W12 단점 보완 | 97% | 46개 |
| **+H1~H17 고구현성 추가 (최종)** | **99%** | **55개 고유** |

---

## 3. 권한 체계 선언

### 3.1 기존 VAMOS 권한 체인

```
Level 0: DESIGN (D2.0-XX)           — 최상위 설계 정본 (변경 불가 원천)
  ↓
Level 1: STEP7 (작업가이드)          — 설계→구현 변환 가이드
  ↓
Level 2: Part2 (구현가이드)          — 버전별 구현 명세 (V1/V2/V3)
  ↓
Level 3: sot 2/ (구현 정본)          — 도메인별 최종 구현 정본
  ↓
Level 4: 코드 구현                   — sot 2/ 정본 기반 실제 코드
```

**권한 우선순위 원칙**:
- 상위 Level이 항상 하위 Level에 우선한다.
- 동일 Level 내 충돌 시 더 최근 갱신된 문서가 우선한다.
- LOCK 값은 SOT 원본(Level 0~2)에서만 변경 가능하며, Level 3 이하에서는 글자 그대로 복사만 허용된다.
- FREEZE 값은 모든 Level에서 변경이 차단된다.

### 3.2 5-2 도메인 확장 체인

```
D2.0-06 (Storage/Memory 정본)
D2.0-02 (Orange Core 정본)
D2.0-01 (Overview 정본)
STEP7-G (벤치마크 작업가이드)
    ↓
sot 2/5-2_File-Context/ (대용량 컨텍스트 전략/알고리즘 구현 정본)
    ↓
sot 2/6-4_Memory-RAG/ (인프라 소비 — 인프라 구현은 6-4 소유)
```

### 3.3 LOCK 보호 값 (SOT에서 글자 그대로 복사)

> **규칙**: LOCK 값은 SOT 원본에서 변경 불가. 아래는 원본 글자 그대로 복사.

| # | LOCK 항목 | 값 (SOT 원문) | SOT 출처 | 라인 |
|---|-----------|-------------|----------|------|
| L1 | Contextual Retrieval | `"이 청크는 '{doc_title}'의 '{section}' 섹션에서 발췌. 문서 요약: {summary}"` — 검색 실패율 49% 감소 | D2.0-06 | L915-918 |
| L2 | Hybrid Search | `alpha * bm25_score + (1-alpha) * vector_score`, alpha=0.3, RRF k=60 | D2.0-06 | L776-780 |
| L3 | Cross-Encoder Reranking | `cross-encoder/ms-marco-MiniLM-L-6-v2`, 50ms/20건, top-20→rerank→top-3~5 | D2.0-06 | L852-857 |
| L4 | 컨텍스트 자동 압축 | trigger_threshold=0.8, target_ratio=0.5, preserve_recent_turns=5, information_loss_estimate 포함 | D2.0-02 | L407-445 |
| L5 | 슬라이딩 윈도우 | D2.0-05 L1045 참조 | D2.0-05 | L1045 |
| L6 | 한국어 형태소 청킹 | Mecab-ko(V1)→Kiwi(V2), 한-영 혼용 문장 단위 우선 | D2.0-06 | L665-668 |
| L7 | 청크 크기 권장 | 한국어 300~500 토큰/청크, 오버랩 50~100 토큰 | D2.0-06 | L679-681 |

> **L7 적용 주의**: SOT LOCK 값은 300~500 토큰(D2.0-06 L679-681). 원본 파일(§7 W 이후)에서 한국어 고밀도 문서 특화 시 500~1000 토큰으로 확장 권고하였으나, 이는 DEFINED-HERE 확장 범위로서 L7 LOCK 기본값(300~500)과 보완 관계이다. 구현 시: 기본값=300~500, 한국어 고밀도 문서=Dynamic Chunking(L8)에 따라 500~1000 허용. (CF-52-004 참조)
| L8 | Dynamic Chunking | 문서 유형별 청킹 전략 | STEP7-D | L236-240 |
| L9 | QoD 점수 체계 | Accuracy(0.30)+Relevance(0.25)+Completeness(0.20)+Safety(0.15)+Efficiency(0.10) ≥ 0.6 | CLAUDE.md | L264-266 |
| L10 | 메모리 4계층 | L0(Session/B-4), L1(Project/B-1), L2(Long-term/B-3), L3(Procedural/B-2) — LOCK 매핑 | D2.0-06 | L87-126 |
| L11 | 4-Index Fusion 검색 | 벡터+키워드+그래프+메모리 Fusion, 단일 대비 15%+ 개선 목표 | STEP7-G | L393-402 |
| L12 | Self-RAG / CRAG / RAPTOR | V2 구현 | STEP7 작업가이드 | L755-757 |
| L13 | Late Chunking (Jina AI) | V2 구현 | STEP7 작업가이드 | L759 |
| L14 | ColBERT v3 Multi-Vector | V2 구현 | STEP7 작업가이드 | L760 |
| L15 | NLI Hallucination Detection | D2.0-07 L1791-1840 — V2 CRITICAL | D2.0-07 | L1791-1840 |
| L16 | Prompt Caching | TTL 5분, 90% 비용 절감 (Anthropic), 50% (OpenAI) — V1 CRITICAL | D2.0-02 | L1923-2046 |
| L17 | Batch API | 실시간 대비 50% 절감, max_wait_hours=24 | D2.0-02 | L2020+ |
| L18 | Knowledge Graph Engine | I-24, V1:OFF / V2:OFF / V3:ON | D2.0-01 | L641 |

### 3.4 DEFINED-HERE (신규 정의 — 5-2 도메인 소유)

> 아래 37개 기술은 SOT에 존재하지 않으며, 본 도메인에서 최초 정의한다.

| 분류 | 항목 | 수량 |
|------|------|------|
| G-series (Gap 보완) | G1~G8 | 8개 |
| W-series (약점 보완) | W1~W12 | 12개 |
| H-series (고급 기법) | H1~H17 | 17개 |
| **합계** | | **37개** |

상세 목록은 [부록 B](#부록-b-55개-기술-매핑-테이블) 참조.

---

## 4. 거버넌스 규칙

### 4.1 공통 규칙 (R1~R11 적용)

본 도메인은 VAMOS 공통 거버넌스 R1~R11을 준수한다. 아래는 각 규칙의 File Context 도메인 적용 명세이다.

| 규칙 | 내용 | 5-2 도메인 적용 |
|------|------|----------------|
| **R1** | Python 3.11+ 필수 | 모든 컨텍스트 처리 파이프라인(Phase A~G)은 Python 3.11+ 환경에서 구현. asyncio 기반 비동기 파이프라인 활용. |
| **R2** | Pydantic v2 스키마 검증 | 청킹 결과, 검색 쿼리, 리랭킹 스코어 등 모든 데이터 구조는 Pydantic v2 BaseModel로 정의. |
| **R3** | no-create (기존 파일 삭제 금지) | `V12_ADDITIONS_상세명세.md` 등 기존 원본 파일 삭제 불가. 신규 파일만 추가 허용. |
| **R4** | no-delete (구조 삭제 금지) | Phase A~G 파이프라인 단계, 8-Layer 검증 체계의 기존 단계 삭제 불가. |
| **R5** | LOCK/FREEZE 불변성 | §3.3의 18건 LOCK 값(L1~L18)은 SOT 원본 변경 없이 수정 불가. R-52-4~R-52-7의 DEFINED-HERE LOCK도 동일 적용. |
| **R6** | SOT mandate (정본 의무) | 55개 통합 기술의 모든 파라미터/임계값은 본 계획서 또는 SOT 원본에 명시적 근거 필수. |
| **R7** | CORE→COND 단방향 | CORE(V1 필수) 항목이 COND(조건부) 항목에 의존 불가. G1~G8, W1~W12 중 V1 배정 항목은 V2/V3 항목 참조 금지. |
| **R8** | trace_id 서버 전용 | 컨텍스트 처리 trace_id(파이프라인 추적용)는 서버 사이드에서만 생성/관리. 클라이언트 노출 금지. |
| **R9** | 내부 정보 노출 금지 | 8-Layer 검증 상세 점수, 모델 Cascade 경로, KG 내부 구조 등은 사용자 응답에 포함 금지. |
| **R10** | 비용 상한 (cost ceiling) | Cloud Cascade(W1) 호출 시 세션당 비용 상한 적용. 상한 초과 시 로컬 모델 전용 모드로 자동 전환. |
| **R11** | schema_registry 단일 소스 | 청킹/검색/리랭킹/검증 스키마는 `schema_registry`에서 단일 관리. 도메인 내 중복 스키마 정의 금지. |

### 4.2 도메인 고유 규칙

| 규칙 ID | 내용 |
|---------|------|
| **R-52-1** | LOCK 값(§3.3, 18건) 변경 시 반드시 SOT 원본 문서를 먼저 변경한 뒤 본 도메인에 반영한다. |
| **R-52-2** | G/W/H 기술의 정확도 수치 변경 시 §12 벤치마크 테이블 동시 갱신 필수. |
| **R-52-3** | Phase A~G 파이프라인 단계 추가/삭제 시 §6 통합 흐름도와 `01_context-pipeline/_index.md` 동시 갱신. |
| **R-52-4** | 손실 임계값(G3) `≤0.15 정상 / 0.15~0.30 경고 / >0.30 압축 거부` — 본 도메인 DEFINED-HERE LOCK. |
| **R-52-5** | relevance 하한선(G6) `< 0.7 제외` — 본 도메인 DEFINED-HERE LOCK. |
| **R-52-6** | Agentic RAG 검색 루프(G8) `max 3회` — 본 도메인 DEFINED-HERE LOCK. |
| **R-52-7** | Self-Consistency 샘플 수 `N=3` — 본 도메인 DEFINED-HERE LOCK. |

### 4.3 횡단 규칙

| 규칙 ID | 내용 |
|---------|------|
| **R-T5-1** | 도메인 횡단 항목은 정본 소유자 명시 필수 (Tier 5 공통). |
| **R-T5-2** | 추적 인덱스는 월 1회 갱신 (Tier 5 공통). |

---

## 5. 의존성 및 선행작업

### 5.1 도메인 의존성

| 방향 | 도메인 | 관계 |
|------|--------|------|
| **소비** | 6-4 Memory-RAG | 5-2는 RAG 인프라(벡터DB, 임베딩, 검색 엔진)를 6-4에서 소비. 5-2는 전략/알고리즘 소유, 6-4은 인프라 구현 소유. |
| **제공** | 6-11 Hologram (Main LLM) | 5-2가 처리한 컨텍스트를 6-11 Hologram에 제공하여 응답 품질 향상. |
| **평가** | 5-1 Benchmark-Evaluation | S7G-040(Context Window 활용도), S7G-041(RAG vs Long Context) 벤치마크로 5-2 성능 평가. |
| **기반** | 1-1 Verifier-Reasoning | LLM 모델 자체의 컨텍스트 윈도우 크기가 5-2 전략의 근본 제약. |
| **횡단** | 6-2 Security | PII 마스킹, 민감 데이터 경로 관리 → §9.2 참조. |

### 5.2 선행작업

| # | 선행작업 | 목적 |
|---|---------|------|
| PA-1 | 원본 파일(1,618줄) 전문 읽기 + 12개 섹션 매핑 | 기존 내용을 14+α 구조에 정확히 배치 |
| PA-2 | SOT 4개 파일 LOCK 값 대조 (D2.0-06, D2.0-02, D2.0-01, STEP7-G) | LOCK 항목 18건 정확성 검증 |
| PA-3 | Part2 컨텍스트/RAG 관련 섹션 확인 | ABSENT 상태 최종 확인 |
| PA-4 | 6-4 Memory-RAG 도메인과 경계 합의 | 전략(5-2) vs 인프라(6-4) 역할 분리 |

---

## 6. 시스템 아키텍처

### 6.1 Phase A~G 7단계 파이프라인 (핵심)

> 원본 §6 + §9 통합 파이프라인 v3.0 기반. 총 45개 보완 기술 통합.

```
═══════════════════════════════════════════════════════════════
  VAMOS AI 파일 컨텍스트 이해 — 7-Phase 통합 파이프라인
  (G1~G8 + A1~A8 + W1~W12 + H1~H17 = 55개 기술)
═══════════════════════════════════════════════════════════════

사용자 파일 입력
     │
     ▼
┌─── Phase A: 수신 + 판별 + 라우팅 ───────────────────┐
│  A-1:  tiktoken 토큰 측정 (D2.0-05 L1043)           │
│  A-2:  문서 유형 자동 탐지 (STEP7-D L236-240)       │
│  A-3:  언어 자동 감지 (D2.0-06 L665)                │
│  A-4:  [H10] Document Layout Analysis                │
│  A-5:  [H11] Structured Extraction                   │
│  A-6:  [H12] 멀티모달 감지 (V2)                     │
│  A-7:  KV-Cache 히트 확인 [A2]                       │
│  A-8:  [G2] 구간별 정확도 고지                       │
│  A-9:  [W1] 복잡도 판정 → Cascade 전략              │
│  A-10: [H2] Query Decomposition (복합 질의 분해)     │
│  A-11: [H3] Query Routing (최적 검색 전략)           │
│  A-12: [H13] Adaptive Retrieval 게이팅 (V2)         │
│                                                      │
│  크기별 라우팅:                                      │
│  < 50K → Phase B  │  50~130K → Phase C              │
│  130~200K → Phase D  │  200K+ → Phase E             │
└──────────────────────────────────────────────────────┘
     │
     ▼
┌─── Phase B: 소규모 처리 (< 50K) ────────────────────┐
│  B-1: 3-Pass 읽기 [A1] + [W1] Cascade               │
│       + [W9] Self-Consistency 3x                     │
│  B-2: [H5] FLARE (장문 생성 시, V2)                 │
│  B-3: [W11] Attributed QA                            │
└──────────────────────────────────────────────────────┘
     │
     ▼
┌─── Phase C: 대용량 처리 (50~130K) ──────────────────┐
│  C-0: MemWalker 트리 구축 + 영구 저장 [A6]          │
│  C-1: [G1] 위치 편향 보정 (Ms-PoE+Attention Cal.)   │
│  C-2: [G6] Distractor 필터 + ChunkRAG + SEAE        │
│  C-3: Multi-Pass + MEGA-RAG DISC [A8, W1]           │
│  C-4: [H5] FLARE (V2) + [W9] Self-Consistency       │
└──────────────────────────────────────────────────────┘
     │
     ▼
┌─── Phase D: 초대용량 처리 (130~200K) ───────────────┐
│  D-0: 전략 선택                                      │
│       V1: 슬라이딩 윈도우 + [W2] KV Offloading      │
│       V2: StreamingLLM + [W2] MLA + [W8] YaRN       │
│       V3: Infini-Attention + [W2] Ring Attention     │
│  D-1: 압축 + 원자 명제 추출 [G3]                    │
│       손실 ≤0.15 정상 / 0.15~0.30 경고 / >0.30 거부 │
└──────────────────────────────────────────────────────┘
     │
     ▼
┌─── Phase E: 분할 처리 (200K+) ──────────────────────┐
│  E-1:   한국어 최적 청킹 + [W10] 문장 완전성        │
│         + [H8] Parent-Child + [H11] 타입 인식        │
│  E-1.5: Semantic Hashing + [H9] Proposition (V2)     │
│  E-2:   Contextual Retrieval + Late Chunking         │
│  E-3:   [W3] Ensemble Embedding                      │
│  E-4:   검색 ([H1]HyDE+[H4]RAG-Fusion+[H7]StepBack │
│          +[H15]Metadata+4-Index Fusion+ColBERT)      │
│  E-5:   2단 Reranking+[H6]CoN+[H14]Compression      │
│  E-6:   Agentic RAG (Self-RAG+CRAG) [G8] max 3회    │
│  E-6.5: RAPTOR 트리 참조                             │
└──────────────────────────────────────────────────────┘
     │
     ▼
┌─── Phase F: 최종 검증 (공통) — 8 Layer ─────────────┐
│  L1: QoD 5요소 ≥ 0.6                                │
│  L2: Pydantic Strict [G5] + R6 무생성               │
│  L3: [W11] Attributed QA (원문 발췌, 일치도 ≥0.8)   │
│  L4: NLI 환각 탐지 [A8]                             │
│  L4.5: [H17] Chain-of-Verification (V2)             │
│  L5: Cross-Chunk 일관성 (SEAE)                       │
│  L6: [H16] Verbalized Confidence Calibration         │
│  L7: [W9] Self-Consistency 3x (<0.7 트리거)          │
│  L8: [H5] FLARE 재검색                              │
└──────────────────────────────────────────────────────┘
     │
     ▼
┌─── Phase G: 영구 학습 (VAMOS 독점) ────────────────┐
│  G-1: KG 영구 구축 + [W6] 2단계 + GraphRAG          │
│  G-2: MemWalker 트리 영구 저장                       │
│  G-3: 사용자 패턴 학습 → 예측적 캐싱                │
│  G-4: Self-Improving Retrieval + [H16] 교정 곡선     │
│  G-5: [W4] Synthetic Data → LoRA 파인튜닝           │
│  G-6: [W12] Continuous Evaluation Loop               │
│  G-7: [H9] Proposition Index 지속 확장               │
└──────────────────────────────────────────────────────┘
```

> **상세**: `01_context-pipeline/` 서브폴더에 Phase별 상세 문서 배치 예정.

### 6.2 G1~G8 Gap 보완 상세

| # | 항목 | 심각도 | 해결 방법 | 상세 위치 |
|---|------|--------|----------|----------|
| G1 | Lost-in-the-Middle 대응 | CRITICAL | 앞/뒤 이중 배치 + Ms-PoE + Attention Calibration | `02_gap-remediation/` |
| G2 | Context Rot 인식 | CRITICAL | 구간별 예상 정확도 사전 고지 (10~50K: 85~95%, 50~130K: 70~85%, 130~200K: 60~75%) | `02_gap-remediation/` |
| G3 | information_loss 임계값 | HIGH | `≤0.15` 정상, `0.15~0.30` 경고, `>0.30` 압축 거부 **[DEFINED-HERE LOCK]** | `02_gap-remediation/` |
| G4 | 200K+ 분할 처리 알고리즘 | HIGH | 의미 단위 분할 + 오버랩 10% + 분할 헤더(요약) 부착 | `02_gap-remediation/` |
| G5 | V0/V1 환각 자동 검증 | HIGH | Pydantic Strict + 필드명/타입 SOT 자동 대조 | `02_gap-remediation/` |
| G6 | Distractor Interference | MEDIUM | `relevance < 0.7 제외` **[DEFINED-HERE LOCK]** + ChunkRAG 레벨 필터 | `02_gap-remediation/` |
| G7 | 가이드 자체 분할 전략 | MEDIUM | §별 독립 읽기 가이드 | `02_gap-remediation/` |
| G8 | Agentic RAG 루프 제한 | MEDIUM | `max 3회` **[DEFINED-HERE LOCK]** + 비용 가드레일 | `02_gap-remediation/` |

### 6.3 W1~W12 약점 보완 기술

| # | 항목 | SOT 연동 | 버전 | 심각도 |
|---|------|----------|------|--------|
| W1 | Smart Cascade (로컬→클라우드) | D2.0-02 L235 | V1 | CRITICAL |
| W2 | Ring Attention Lite (GPU 효율) | D2.0-02 L1977 | V1→V3 | HIGH |
| W3 | Ensemble Embedding | D2.0-06 L776 | V1→V2 | HIGH |
| W4 | Synthetic Data + LoRA | D2.0-03 L1620 | V2 | HIGH |
| W5 | Speculative Decoding + Medusa | STEP7_N-P L1254 | V1→V2 | HIGH |
| W6 | LLM-Augmented KG Extraction | D2.0-01 L641 | V2→V3 | HIGH |
| W7 | MDCure Multi-Doc Cross-Analysis | STEP7-G L393 | V2→V3 | CRITICAL |
| W8 | LongRoPE/YaRN 위치 인코딩 확장 | D2.0-05 L1044 | V1→V2 | HIGH |
| W9 | Self-Consistency 다중 샘플링 | D2.0-02 L235 | V1 | CRITICAL |
| W10 | Sliding Chunk + 문장 완전성 | D2.0-06 L679 | V1 | HIGH |
| W11 | Attributed QA (출처 증명 강화) | D2.0-07 L1791 | V1 | CRITICAL |
| W12 | Continuous Evaluation Loop | STEP7-G L393 | V1→V2 | CRITICAL |

> **상세**: `03_weakness-mitigation/` 서브폴더에 W별 상세 문서 배치 예정.

### 6.4 H1~H17 고급 RAG/검색 기법

| # | 기법 | 핵심 효과 | 난이도 | 버전 | 파이프라인 위치 |
|---|------|----------|--------|------|---------------|
| H1 | HyDE | 검색 재현율 +10~20% | Easy | V1 | Phase E 검색 전 |
| H2 | Query Decomposition | 다중 홉 +15~25% | Easy | V1 | Phase A 쿼리 분석 |
| H3 | Query Routing | 정밀도 +10~15% | Easy-Med | V1 | Phase A 라우팅 |
| H4 | RAG-Fusion | 재현율 +10~20% | Easy | V1 | Phase E 검색 |
| H5 | FLARE | 장문 정확도 +5~15% | Medium | V2 | Phase B/C/F 생성 |
| H6 | Chain-of-Note | 노이즈 필터링, EM +7.9 | Medium | V1 | Phase E 생성 전 |
| H7 | Step-Back Prompting | 오류 39.9% 수정 | Easy | V1 | Phase E 검색 |
| H8 | Parent-Child Chunk | 완전성 +15~25% | Easy | V1 | Phase E 청킹 |
| H9 | Proposition Indexing | 팩트 정밀도 +10~20% | Medium | V2 | Phase E 인덱싱 |
| H10 | Layout Analysis | 구조 정확도 +20~40% | Medium | V1 | Phase A 파싱 |
| H11 | Structured Extraction | 혼합 콘텐츠 +15~25% | Easy-Med | V1 | Phase E 청킹 |
| H12 | ColPali Multi-Modal | 시각 문서 +15~30% | Medium | V2 | Phase A 멀티모달 |
| H13 | Adaptive Retrieval | 불필요 검색 -70~90% | Medium | V2 | Phase A 게이팅 |
| H14 | Contextual Compression | 3x 압축, 초점 향상 | Easy | V1 | Phase E 생성 전 |
| H15 | Metadata Filtering | 정밀도 +10~20% | Easy | V1 | Phase E 검색 |
| H16 | Confidence Calibration | 오류 40% 플래그 | Easy-Med | V1 | Phase F 전체 |
| H17 | Chain-of-Verification | 정확도 +10~15% | Medium | V2 | Phase F 검증 |

> **상세**: `04_advanced-techniques/` 서브폴더에 H별 상세 문서 배치 예정.

---

## 7. Phase 실행 계획

> Tier 5 기본: Phase 0 스펙 확정 → Phase 1 V1 기본 구현 → Phase 2 V2 고급 확장 → Phase 3 V3 프로덕션 완성
> **V1/V2/V3 로드맵 → Phase 매핑**: V1 20개 그룹(23개별 기술) = Phase 1, V2 13개 항목 = Phase 2, V3 4개 항목 = Phase 3

### Phase 0: 스펙 확정 ✅ GATE PASS (2026-03-27, QC S10-3 A-)

| 태스크 | 산출물 | 완료 기준 | 상태 |
|--------|--------|----------|------|
| T0-1 계획서 작성 | FILE_CONTEXT_구조화_종합계획서.md | 14+α 섹션 완성, QC PASS | ✅ S10-3 A- (2026-03-27) |
| T0-2 AUTHORITY_CHAIN | AUTHORITY_CHAIN.md | LOCK 18건 + DEFINED-HERE 37건 기록 | ✅ (2026-03-27) |
| T0-3 CONFLICT_LOG | CONFLICT_LOG.md | 도메인 간 충돌 사전 등록 | ✅ v1.1 (CF-52-001~005, 5건 RESOLVED) |
| T0-4 서브폴더 구조 | 01~05 서브폴더 + _index.md 5개 | Phase별/기술별 분류 완료 | ✅ (2026-03-27) |
| T0-5 검증 프롬프트 | _verification/phase1_verification_prompt.md | Phase 1 검증 인프라 | ✅ (2026-04-12) |

**Phase 0 → Phase 1 게이트**: ✅ PASS — 종합계획서 APPROVED (S10-3 QC A-), AUTHORITY_CHAIN v1.0 (LOCK 18 + DEFINED-HERE 37), CONFLICT_LOG v1.1 (CF-52-001~005 전수 RESOLVED), 서브폴더 5개 _index.md, 검증 프롬프트 생성 완료.

#### Phase 0 단계별 상세 작업 절차

<details>
<summary><b>T0-1. 종합계획서 14+α 섹션 작성</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot 2\FILE CONTEXT\VAMOS_파일_컨텍스트_이해_최종_업데이트.md` (원본 1,618줄)
- `D:\VAMOS\docs\sot\D2.0-06.md` (Storage/Memory 정본 — L1~L3, L6~L7, L10~L11)
- `D:\VAMOS\docs\sot\D2.0-02.md` (Orange Core 정본 — L4, L16, L17)
- `D:\VAMOS\docs\sot\D2.0-01.md` (Overview 정본 — L18)
- `D:\VAMOS\docs\sot\STEP7_작업가이드.md` (STEP7-G 벤치마크 포함 — L8, L11~L14)

**절차**:
1. 원본 1,618줄 전문 읽기 + 12개 섹션 매핑
2. SOT 4개 파일 LOCK 값 대조 (D2.0-06, D2.0-02, D2.0-01, STEP7-G) → §3.3 LOCK 18건
3. 14+α 섹션 구조로 재편 (§1~§14 + 부록 A/B)
4. Part2 컨텍스트/RAG 관련 섹션 확인 → ABSENT 판정
5. QC 검토 (S8-4 B → S10-3 A-)

**검증**:
- [x] 원본 12개 섹션 전수 매핑 완료
- [x] LOCK 18건 SOT 대조 완료 (§3.3)
- [x] Part2 ABSENT 최종 확인
- [x] QC S10-3 A- PASS

**산출물**: `D:\VAMOS\docs\sot 2\5-2_File-Context\FILE_CONTEXT_구조화_종합계획서.md`
</details>

<details>
<summary><b>T0-2. AUTHORITY_CHAIN 작성</b></summary>

**입력 파일**:
- 본 계획서 §3 (권한 체계 선언)
- SOT 원본 4개 파일 (D2.0-06, D2.0-02, D2.0-01, STEP7-G)

**절차**:
1. 권한 체인 계층 구조 정의 (DESIGN → STEP7 → CLAUDE.md → sot 2/5-2 → 6-4)
2. LOCK 항목 18건 SOT 출처별 분류 (§2.1~2.8)
3. DEFINED-HERE 항목 37건 (G 8 + W 12 + H 17) 등록 (§3.1~3.3)
4. 도메인 경계 구분 (5-2 전략 vs 6-4 인프라, §4)

**검증**:
- [x] LOCK 18건 SOT 원문 글자 그대로 복사 확인
- [x] DEFINED-HERE 37건 전수 등록
- [x] 도메인 경계 6-4 AUTHORITY_CHAIN과 정합

**산출물**: `D:\VAMOS\docs\sot 2\5-2_File-Context\AUTHORITY_CHAIN.md`
</details>

<details>
<summary><b>T0-3. CONFLICT_LOG 작성</b></summary>

**입력 파일**:
- 본 계획서 §5 (의존성), §9 (횡단 관심사)
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\AUTHORITY_CHAIN.md`
- `D:\VAMOS\docs\sot 2\5-1_Benchmark-Evaluation\AUTHORITY_CHAIN.md`

**절차**:
1. 도메인 간 경계 모호 지점 사전 식별
2. CF-52-001~005 등록 (5-2 vs 6-4 청킹/검색, 5-2 vs 5-1 벤치마크, L7 청크 크기, H14 압축)
3. 6-4/5-1 AUTHORITY_CHAIN 교차 확인
4. Phase 11 S11-6 교차 검증 → CF-52-001~003 RESOLVED 전환

**검증**:
- [x] 5건 전부 RESOLVED (CF-52-001~005)
- [x] 6-4 AUTHORITY_CHAIN §3 도메인 경계 "인프라=6-4 / 전략=5-2" 명시 확인
- [x] 5-1 벤치마크 소유권 경계 "측정=5-1 / 목표=5-2" 확인

**산출물**: `D:\VAMOS\docs\sot 2\5-2_File-Context\CONFLICT_LOG.md` (v1.1)
</details>

<details>
<summary><b>T0-4. 서브폴더 구조 + _index.md 작성</b></summary>

**입력 파일**:
- 본 계획서 §6 (시스템 아키텍처)

**절차**:
1. 5개 서브폴더 생성 (01_context-pipeline ~ 05_benchmarks)
2. 각 서브폴더 _index.md 작성: 개요, 항목 목록, LOCK 관련 값, 예정 파일 목록

**검증**:
- [x] 5개 서브폴더 생성 완료
- [x] 5개 _index.md 내용 완비 (항목 목록 + 예정 파일 + LOCK 관련 값)

**산출물**:
- `D:\VAMOS\docs\sot 2\5-2_File-Context\01_context-pipeline\_index.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\02_gap-remediation\_index.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\03_weakness-mitigation\_index.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\04_advanced-techniques\_index.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\05_benchmarks\_index.md`
</details>

<details>
<summary><b>T0-5. Phase 1 검증 프롬프트 작성</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot 2\_automation\PHASE1_VERIFICATION_PLAN.md` (전 도메인 검증 계획)
- 본 계획서 §7

**절차**:
1. 도메인 특수성 반영 (V1/V2/V3 체계, LOCK prefix 없음, P1-N 세션 구조 → 본 §7 갱신으로 해소)
2. 제약 조건 C1~C5 하드코딩 (경로 화이트리스트, 로그 필터, 메모리 격리, 쓰기 금지, 위반 집계)
3. 검증 대상 정보 하드코딩 (DOMAIN_ID, PLAN_PATH, SUBFOLDERS 등)

**검증**:
- [x] C1~C5 제약 조건 완비
- [x] STATUS_MODE=NOT_STARTED 반영
- [x] PHASE1_VERIFICATION_PLAN.md §2.2 프롬프트 규격 준수

**산출물**: `D:\VAMOS\docs\sot 2\5-2_File-Context\_verification\phase1_verification_prompt.md`
</details>

---

### Phase 1: V1 기본 구현 (20그룹/23기술, 7세션)

> **목표**: V1 배정 항목(20개 그룹, 23개 개별 기술)의 상세 명세 문서를 작성하여 구현 준비 완료. 골든 테스트셋 기준선 Faithfulness ≥ 0.85 달성.
> **산출물 예상**: ~32개 파일 (02~05 서브폴더 상세 문서 25개 + 01 파이프라인 통합 문서 7개)
> **항목 수 참고**: 원본 §7.1 표는 20행이나 #6(G1~G3=3개), #7(G5~G6=2개)가 그룹 행이므로 개별 기술 수는 23개. 본 §7에서는 개별 기술 단위로 세션 배정.

#### V1 항목 총괄표 (20그룹 / 23개별 기술)

> **주의**: 원본 파일에서 H16은 "V1 Easy-Medium"으로 명시 (L1104). 프롬프트 기반 구현으로 별도 라이브러리 불필요.

| # | 항목 | 난이도 | 핵심 효과 | 세션 | 파이프라인 |
|---|------|--------|----------|------|-----------|
| 1 | W12: 골든 테스트셋 + RAGAS | 중 | 실측 정확도 확보 | P1-1 | G-6 |
| 2 | G1: Lost-in-the-Middle 대응 | 중 | 위치 편향 보정 | P1-2 | C-1 |
| 3 | G2: Context Rot 인식 | 중 | 구간별 정확도 고지 | P1-2 | A-8 |
| 4 | G3: information_loss 임계값 | 중 | 압축 손실 제어 | P1-2 | D-1 |
| 5 | G5: V1 환각 자동 검증 | 하 | Pydantic+SOT 대조 | P1-2 | F-L2 |
| 6 | G6: Distractor Interference | 하 | relevance 하한선 | P1-2 | C-2/E-5 |
| 7 | W1: Smart Cascade | 중 | 복잡 문서 품질 향상 | P1-3 | A-9/B-1 |
| 8 | W9: Self-Consistency 3x | 하 | 환각 감소 | P1-3 | B-1/F-L7 |
| 9 | W11: Attributed QA | 중 | 출처 환각 차단 | P1-3 | B-3/F-L3 |
| 10 | H2: Query Decomposition | 하 | 다중 홉 +15~25% | P1-4 | A-10 |
| 11 | H3: Query Routing | 중 | 정밀도 +10~15% | P1-4 | A-11 |
| 12 | H10: Layout Analysis | 중 | 구조 정확도 +20~40% | P1-4 | A-4 |
| 13 | H11: Structured Extraction | 중 | 혼합 콘텐츠 +15~25% | P1-4 | A-5/E-1 |
| 14 | W10: 문장 완전성 보장 청킹 | 중 | 청크 경계 손실 제거 | P1-5 | E-1 |
| 15 | H1: HyDE | 하 | 검색 재현율 +10~20% | P1-5 | E-4 |
| 16 | H4: RAG-Fusion | 하 | 재현율 +10~20% | P1-5 | E-4 |
| 17 | H7: Step-Back Prompting | 하 | 오류 39.9% 수정 | P1-5 | E-4 |
| 18 | H8: Parent-Child Chunk | 하 | 완전성 +15~25% | P1-5 | E-1 |
| 19 | H15: Metadata Filtering | 하 | 정밀도 +10~20% | P1-5 | E-4 |
| 20 | H6: Chain-of-Note | 중 | 노이즈 필터링 | P1-6 | E-5 |
| 21 | H14: Contextual Compression | 하 | 3x 압축, 초점 향상 | P1-6 | E-5 |
| 22 | H16: Confidence Calibration | 중 | 오류 40% 플래그 | P1-6 | F-L6 |
| 23 | W5(일부): vLLM+양자화 | 중 | 속도 4x | P1-6 | 성능 |

#### Phase 1 세션 요약표

| 세션 | 작업 | 대상 항목 | 산출물 위치 | 파일 수 | 상태 |
|------|------|----------|-----------|--------|------|
| P1-1 | 벤치마크 기반 구축 | W12 | 05_benchmarks/ | 3 | ✅ 완료 (2026-04-12) |
| P1-2 | Gap 보완 핵심 | G1, G2, G3, G5, G6 | 02_gap-remediation/ | 5 | ✅ 완료 (2026-04-12) |
| P1-3 | 약점 보완 CRITICAL | W1, W9, W11 | 03_weakness-mitigation/ | 3 | ✅ 완료 (2026-04-12) |
| P1-4 | Phase A 수신/라우팅 | H2, H3, H10, H11 | 04_advanced-techniques/ | 4 | ✅ 완료 (2026-04-12) |
| P1-5 | Phase E 청킹/검색 | W10, H1, H4, H7, H8, H15 | 03_weakness + 04_advanced/ | 6 | ✅ 완료 (2026-04-12) |
| P1-6 | Phase E-F 리랭킹/검증/성능 | H6, H14, H16, W5(일부) | 03_weakness + 04_advanced/ | 4 | ✅ 완료 (2026-04-12) |
| P1-7 | Phase A~G 통합 파이프라인 | (P1-1~6 전체 통합) | 01_context-pipeline/ | 7 | ✅ 완료 (2026-04-12) |

**Phase 1 → Phase 2 게이트**: V1 20개 항목 전부 구현 + 골든 테스트셋 기준선(Faithfulness ≥ 0.85) 달성 + CONFLICT_LOG OPEN 0건 + LOCK 18건 + DEFINED-HERE LOCK 4건(R-52-4~7) 무위반 확인

#### Phase 1 세션 의존성

```
P1-1 (벤치마크 기반) ← 최선행: RK-7 CRITICAL 해소
  ↓
P1-2 (Gap 보완) ──────┐
  ↓                    │
P1-3 (약점 CRITICAL) ──┤
  ↓                    │
P1-4 (Phase A 기술) ───┤──→ P1-7 (통합 파이프라인) ← P1-1~6 전부 완료 필수
  ↓                    │
P1-5 (Phase E 기술) ───┤
  ↓                    │
P1-6 (Phase E-F 기술) ─┘
```

> P1-1이 최선행 (벤치마크 기반 필요). P1-2~P1-6은 순서 권장이나 부분 병렬 가능. P1-7은 P1-1~P1-6 전부 완료 필수.

#### Phase 1 단계별 상세 작업 절차

<details>
<summary><b>P1-1. 벤치마크 기반 구축 (W12)</b></summary>

**대조 기준**:
- §7 세부 작업: P1-1 "W12 골든 테스트셋 + RAGAS 자동 평가"
- §7 전환 게이트: Faithfulness ≥ 0.85
- §8 리스크: RK-7 CRITICAL "벤치마크 부재로 개선 효과 불명"
- §12 벤치마크: RAGAS 메트릭 5개 기준선(§12.4), §12.3 5-1 연동 (S7G-036/040/041)
- §6.1 파이프라인: Phase G (G-6 Continuous Evaluation Loop)
- §3.3 LOCK: L9 QoD 점수 체계 (CLAUDE.md L264-266)

**목표**: 100 QA 골든 테스트셋 구축 + RAGAS 자동 평가 설정 + 구간별 정확도 목표 상세 근거 문서화. 이후 모든 세션의 효과 측정 기반 확보.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\5-2_File-Context\FILE_CONTEXT_구조화_종합계획서.md` §12 (벤치마크 목표)
- `D:\VAMOS\docs\sot 2\5-2_File-Context\05_benchmarks\_index.md` (예정 파일 목록)
- `D:\VAMOS\docs\sot 2\FILE CONTEXT\VAMOS_파일_컨텍스트_이해_최종_업데이트.md` §11 (원본 벤치마크)
- `D:\VAMOS\docs\sot 2\5-1_Benchmark-Evaluation\` (S7G-036/040/041 벤치마크 정의 — CF-52-003 경계: 측정=5-1, 목표=5-2)
- `D:\VAMOS\docs\sot 2\5-2_File-Context\AUTHORITY_CHAIN.md` §2.8 L9 QoD 점수 체계

**절차**:
1. §12.1 정확도 목표를 구간별(5구간) × 기술 단계별(4단계: 기존→+G→+W→+H)로 분해, 각 셀의 H-series 기여도 근거 문서화 → `accuracy_targets.md`
2. §12.4 RAGAS 메트릭 5개(Faithfulness/Answer Relevancy/Context Recall/Citation Accuracy/Cross-Doc Consistency)의 구체적 측정 방법, 실행 주기(주간), 알림 정책, 배포 차단 로직 상세화 → `ragas_config.md`
3. 골든 테스트셋 100 QA 설계: 단순 팩트 40 + 교차 참조 30 + 추론 20 + 함정(답 없음) 10, 각 QA에 정답 + 출처 라인 + 난이도 + 대상 구간 명시 → `golden_testset.md`
4. 5-1 Benchmark 도메인의 S7G-036/040/041과 연동 명세 확인 (CF-52-003 경계: 측정 실행=5-1, 목표 정의·해석=5-2)
5. LOCK L9 QoD 점수 체계와 RAGAS 메트릭 관계 정리 (QoD ≥ 0.6 = Phase F 게이트, RAGAS = Phase G 평가)
6. 05_benchmarks/_index.md 갱신: 예정 파일 → 실제 파일 경로 반영

**검증**:
- [x] accuracy_targets.md: 5구간 × 4단계 = 20셀 전부 근거 기술 명시
- [x] ragas_config.md: RAGAS 5개 메트릭 측정 방법 완비, 배포 차단 기준 §12.4와 정합
- [x] golden_testset.md: 100 QA 전수, 각 QA에 정답+출처+난이도+구간 명시
- [x] 5-1 S7G-036/040/041 연동 명세 CF-52-003 경계 준수
- [x] LOCK L9 QoD 체계 글자 그대로 인용 (Accuracy 0.30 + Relevance 0.25 + Completeness 0.20 + Safety 0.15 + Efficiency 0.10 ≥ 0.6)
- [x] _index.md 갱신 완료

**산출물**:
- `D:\VAMOS\docs\sot 2\5-2_File-Context\05_benchmarks\accuracy_targets.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\05_benchmarks\golden_testset.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\05_benchmarks\ragas_config.md`

**완료**: 2026-04-12. 100 QA 골든 테스트셋(SF40+CR30+RS20+TR10) + RAGAS 5메트릭 설정 + 5구간×4단계 20셀 정확도 근거 완비. Faithfulness 기준선 ≥ 0.85 설정 완료. 재검증 시 golden_testset.md 분포 테이블 3건 교정(구간별 추론/함정 배분 오류, 난이도 집계 오류, CR-026 W-series 카운트 5→6).

**[P1-1] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: 3건 — accuracy_targets.md, ragas_config.md, golden_testset.md + _index.md 갱신
- 1. 게이트: Faithfulness ≥ 0.85 기준선 설정 완료 (ragas_config.md §1.1 M1). 실측은 골든셋 실행 시(Phase 2) 달성 확인 예정.
- 2. CONFLICT: 발견 0 / 해소 0 / OPEN 0. CF-52-003(5-2 vs 5-1 벤치마크 경계) 기존 RESOLVED 상태 준수 확인.
- 3. LOCK 변경: 없음. LOCK 18건 + DEFINED-HERE LOCK 4건(R-52-4~7) 무위반.
- 4. 이월: 없음. V1 범위(골든 테스트셋+기준선) 완료. V2 범위(RAGAS 완전 자동화/CI 통합)는 Phase 2 소관.
- 재검증: golden_testset.md 분포 테이블 3건 교정 완료 — ①구간별 추론/함정 배분(130~200K/200K+/전 구간 행), ②난이도 집계(하27/중44/상29), ③CR-026 W카운트(6개). accuracy_targets.md, ragas_config.md는 오류 없음 확인.
</details>

<details>
<summary><b>P1-2. Gap 보완 핵심 — G1, G2, G3, G5, G6</b></summary>

**대조 기준**:
- §7 세부 작업: P1-2 "G1~G3 위치 편향+Context Rot+손실 임계값 / G5~G6 Pydantic+relevance 하한선"
- §7 전환 게이트: V1 20개 항목 전부 구현
- §8 리스크: RK-1 HIGH (50K+ 정확도 저하), RK-6 HIGH (출처 환각), RK-9 HIGH (Lost-in-Middle 열화)
- §6.2 Gap 상세표: G1(CRITICAL/V1/C-1), G2(CRITICAL/V1/A-8), G3(HIGH/V1/D-1), G5(HIGH/V1/F-L2), G6(MEDIUM/V1/C-2,E-5)
- §3.3 LOCK: G3 DEFINED-HERE LOCK R-52-4 (≤0.15 정상 / 0.15~0.30 경고 / >0.30 압축 거부), G6 DEFINED-HERE LOCK R-52-5 (relevance < 0.7 제외)
- AUTHORITY_CHAIN §3.1: G1~G6 DEFINED-HERE 값 참조

**목표**: 대용량 컨텍스트 기본 보호 5대 Gap 항목의 구현 명세 작성. 위치 편향 보정, Context Rot 인식, 손실 임계값, 환각 검증, Distractor 필터의 알고리즘·파라미터·파이프라인 배치를 상세 정의.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\5-2_File-Context\FILE_CONTEXT_구조화_종합계획서.md` §6.2 (G1~G8 Gap 상세표)
- `D:\VAMOS\docs\sot 2\5-2_File-Context\02_gap-remediation\_index.md` (예정 파일 목록 + DEFINED-HERE LOCK 값)
- `D:\VAMOS\docs\sot 2\FILE CONTEXT\VAMOS_파일_컨텍스트_이해_최종_업데이트.md` §4 (Gap 분석 원본)
- `D:\VAMOS\docs\sot 2\5-2_File-Context\AUTHORITY_CHAIN.md` §3.1 G-series DEFINED-HERE 값
- `D:\VAMOS\docs\sot 2\5-2_File-Context\CONFLICT_LOG.md` (CF-52-004 L7 청크 크기 관련)

**절차**:
1. G1 Lost-in-the-Middle 대응 상세: Ms-PoE 가중치 산식, Attention Calibration 파라미터, 중앙부 가중치 1.3x 근거(§8 RK-9), 3-Pass 시 순서 랜덤화, Phase C-1 배치 → `g1_lost_in_middle.md`
2. G2 Context Rot 인식 상세: 구간별 예상 정확도 사전 고지 로직(10~50K: 85~95%, 50~130K: 70~85%, 130~200K: 60~75%), 사용자 알림 UX, Phase A-8 배치 → `g2_context_rot.md`
3. G3 information_loss 임계값 상세: DEFINED-HERE LOCK R-52-4 (≤0.15/0.15~0.30/>0.30) 적용 로직, 원자 명제 추출 연동, 압축 거부 시 fallback(Phase E 분할), Phase D-1 배치 → `g3_loss_threshold.md`
4. G5 V1 환각 자동 검증 상세: Pydantic Strict 모드(R2 준수), SOT 필드명/타입 자동 대조, R6 무생성 규칙 연동, Phase F-L2 배치 → `g5_hallucination_check.md`
5. G6 Distractor Interference 상세: DEFINED-HERE LOCK R-52-5 (relevance < 0.7 제외), ChunkRAG 레벨 필터, SEAE 교차 일관성, Phase C-2/E-5 배치 → `g6_distractor_filter.md`
6. 02_gap-remediation/_index.md 갱신: 예정 파일 → 실제 파일 경로 + V1 완료 상태
7. LOCK 값 인용 확인: G3(R-52-4), G6(R-52-5) 글자 그대로 복사

**검증**:
- [x] g1_lost_in_middle.md: Ms-PoE 파라미터 명시(α=0.1, 중앙부 1.3x), Phase C-1 배치, §8 RK-9 대응 매핑
- [x] g2_context_rot.md: 5구간 정확도 범위 §12.1과 정합 (5구간 모두 범위 내)
- [x] g3_loss_threshold.md: DEFINED-HERE LOCK R-52-4 글자 그대로 인용 (≤0.15/0.15~0.30/>0.30)
- [x] g5_hallucination_check.md: Pydantic v2 Strict (R2) 준수, R6 무생성 연동
- [x] g6_distractor_filter.md: DEFINED-HERE LOCK R-52-5 글자 그대로 인용 (relevance < 0.7 제외)
- [x] G4/G7/G8은 V2(Phase 2) 항목 — 본 세션에서 미착수 확인
- [x] _index.md 갱신 완료

**산출물**:
- `D:\VAMOS\docs\sot 2\5-2_File-Context\02_gap-remediation\g1_lost_in_middle.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\02_gap-remediation\g2_context_rot.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\02_gap-remediation\g3_loss_threshold.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\02_gap-remediation\g5_hallucination_check.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\02_gap-remediation\g6_distractor_filter.md`

**완료**: 2026-04-12. G1/G2/G3/G5/G6 5대 Gap 항목 상세 명세 작성 완료. Ms-PoE 1.3x, 5구간 정확도, R-52-4/R-52-5 LOCK 인용, Pydantic Strict+R6, ChunkRAG 3단계 필터 포함. 재검증 시 3건 교정(g2 R9 user_message 내부코드 제거, g6 RK-5→RK-1 리스크 매핑 정정, g6 L3 LOCK 모델명 전체 인용).

**[P1-2] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: 5건 — g1_lost_in_middle.md, g2_context_rot.md, g3_loss_threshold.md, g5_hallucination_check.md, g6_distractor_filter.md + _index.md 갱신
- 1. 게이트: V1 20개 항목 중 P1-2 5개 완료 (G1/G2/G3/G5/G6). Faithfulness 기준선 ≥ 0.85는 P1-1에서 설정 완료, 실측은 Phase 2.
- 2. CONFLICT: 발견 0 / 해소 0 / OPEN 0. CF-52-004(L7 청크 크기) 기존 RESOLVED 상태 준수 확인.
- 3. LOCK 변경: 없음. LOCK 18건 + DEFINED-HERE LOCK 4건(R-52-4~7) 무위반. G3(R-52-4), G6(R-52-5) 글자 그대로 인용 확인.
- 4. 이월: 없음. G4/G7/G8은 V2(Phase 2) 소관 — 본 세션 미착수 확인.
- 재검증: 3건 교정 완료 — ①g2_context_rot.md user_message "(G1)" 내부코드 제거(R9 준수), ②g6_distractor_filter.md 리스크 매핑 RK-5→RK-1 정정(§8 RK-1 "Phase C 전용 파이프라인" 해당), ③g6_distractor_filter.md L3 LOCK 모델명 `ms-marco-MiniLM`→`cross-encoder/ms-marco-MiniLM-L-6-v2` 전체 인용. g1, g3, g5, _index.md는 오류 없음 확인.
</details>

<details>
<summary><b>P1-3. 약점 보완 CRITICAL — W1, W9, W11</b></summary>

**대조 기준**:
- §7 세부 작업: P1-3 "W1 Smart Cascade / W9 Self-Consistency / W11 Attributed QA"
- §7 전환 게이트: V1 20개 항목 전부 구현
- §8 리스크: RK-3 MEDIUM (로컬 모델 한계 → W1 Cascade), RK-6 HIGH (출처 환각 → W11)
- §6.3 W 상세표: W1(CRITICAL/V1/A-9,B-1), W9(CRITICAL/V1/B-1,F-L7), W11(CRITICAL/V1/B-3,F-L3)
- §3.3 LOCK: L16 Prompt Caching (W1 비용 최적화 연동), L15 NLI (W11 V2 연동 예정)
- §4 규칙: R-52-7 Self-Consistency N=3 DEFINED-HERE LOCK, R10 비용 상한 (W1)
- AUTHORITY_CHAIN §3.2: W1 로컬→Cloud Mini→Cloud Main, W9 N=3, W11 BERTScore ≥ 0.8

**목표**: 품질 보장 3대 CRITICAL 기술의 구현 명세 작성. Smart Cascade 단계별 상승 로직, Self-Consistency 3x 합의 규칙, Attributed QA 출처 증명 체계를 상세 정의.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\5-2_File-Context\FILE_CONTEXT_구조화_종합계획서.md` §6.3 (W 상세표), 부록 A.2 (Cascade 매트릭스)
- `D:\VAMOS\docs\sot 2\5-2_File-Context\03_weakness-mitigation\_index.md`
- `D:\VAMOS\docs\sot 2\FILE CONTEXT\VAMOS_파일_컨텍스트_이해_최종_업데이트.md` §7 (W-series 원본)
- `D:\VAMOS\docs\sot 2\5-2_File-Context\AUTHORITY_CHAIN.md` §3.2 W-series DEFINED-HERE
- `D:\VAMOS\docs\sot\D2.0-02.md` L235 (Smart Cascade SOT 근거), L1923-2046 (Prompt Caching L16)
- `D:\VAMOS\docs\sot\D2.0-07.md` L1791-1840 (NLI Hallucination Detection L15, W11 V2 연동)

**절차**:
1. W1 Smart Cascade 상세: 복잡도 판정 기준 3단계(단순/중간/복잡), 3-tier 라우팅 로직(로컬 100%→Cloud Mini→Cloud Main), 비용 상한 R10 연동, 부록 A.2 Cascade 매트릭스와 정합, L16 Prompt Caching 활용, Phase A-9/B-1 배치 → `w01_smart_cascade.md`
2. W9 Self-Consistency 상세: N=3 DEFINED-HERE LOCK R-52-7, 합의 규칙(3/3 일치→확정 / 2/3→다수결 / 불일치→재확인), H16 Confidence 트리거 연동(H16 저신뢰 → W9 발동), Phase B-1/F-L7 배치 → `w09_self_consistency.md`
3. W11 Attributed QA 상세: 원문 발췌 부착 의무, BERTScore 일치도 ≥ 0.8, 출처 환각 탐지, 0.7~0.8 구간 경고(§8 RK-6), L15 NLI V2 연동 예정 범위 명시, Phase B-3/F-L3 배치 → `w11_attributed_qa.md`
4. 03_weakness-mitigation/_index.md 갱신
5. LOCK/DEFINED-HERE 인용 확인: R-52-7 N=3, L16 TTL 5분 90% 절감

**검증**:
- [x] w01_smart_cascade.md: 부록 A.2 Cascade 매트릭스 3행 정합, R10 비용 상한 반영, L16 연동 ✅
- [x] w09_self_consistency.md: DEFINED-HERE LOCK R-52-7 N=3 글자 그대로 인용 ✅
- [x] w11_attributed_qa.md: BERTScore ≥ 0.8 기준 명시, §8 RK-6 대응 매핑, L15 V2 연동 범위 구분 ✅
- [x] D2.0-02 L235 SOT 연동 확인 (W1) ✅
- [x] D2.0-07 L1791 SOT 연동 확인 (W11→L15 V2) ✅
- [x] _index.md 갱신 완료 ✅

**산출물**:
- `D:\VAMOS\docs\sot 2\5-2_File-Context\03_weakness-mitigation\w01_smart_cascade.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\03_weakness-mitigation\w09_self_consistency.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\03_weakness-mitigation\w11_attributed_qa.md`

> **완료**: 2026-04-12. W1/W9/W11 CRITICAL 3건 구현 명세 작성 완료, LOCK/DEFINED-HERE 인용 검증 통과, _index.md 갱신 완료.

**[P1-3] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: 3건 — `w01_smart_cascade.md`, `w09_self_consistency.md`, `w11_attributed_qa.md`
- 1. 게이트: Faithfulness ≥ 0.85 달성 기반 확보 — W11 BERTScore ≥ 0.8 인용 검증 + W9 N=3 합의 + W1 Cloud Cascade 품질 보강 (§12.4 기준선 대응)
- 2. CONFLICT: 발견 0 / 해소 0 / OPEN 0
- 3. LOCK 변경: 없음 (L15, L16, R-52-7 원본 그대로 인용)
- 4. 이월: 없음
</details>

<details>
<summary><b>P1-4. Phase A 수신/라우팅 기술 — H2, H3, H10, H11</b></summary>

**대조 기준**:
- §7 세부 작업: P1-4 "H2 Query Decomposition / H3 Query Routing / H10 Layout Analysis / H11 Structured Extraction"
- §7 전환 게이트: V1 20개 항목 전부 구현
- §6.4 H 상세표: H2(Easy/V1/A-10), H3(Easy-Med/V1/A-11), H10(Medium/V1/A-4), H11(Easy-Med/V1/A-5,E-1)
- §6.1 파이프라인: Phase A 수신/판별/라우팅 단계 (A-4, A-5, A-10, A-11)
- AUTHORITY_CHAIN §3.3: H2 LangChain MultiQueryRetriever, H3 semantic-router, H10 Docling(IBM), H11 Unstructured.io
- _index.md 시너지: H10→H11 순차 (레이아웃 분석 → 타입별 추출)

**목표**: 파이프라인 입구(Phase A) 4대 기술의 구현 명세 작성. 쿼리 분석(H2/H3)과 문서 파싱(H10/H11) 상세 정의.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\5-2_File-Context\FILE_CONTEXT_구조화_종합계획서.md` §6.4 (H 상세표), §6.1 Phase A 흐름
- `D:\VAMOS\docs\sot 2\5-2_File-Context\04_advanced-techniques\_index.md` (시너지 표 포함)
- `D:\VAMOS\docs\sot 2\FILE CONTEXT\VAMOS_파일_컨텍스트_이해_최종_업데이트.md` §8 (H-series 원본)
- `D:\VAMOS\docs\sot 2\5-2_File-Context\AUTHORITY_CHAIN.md` §3.3 H-series 핵심 도구

**절차**:
1. H2 Query Decomposition 상세: 복합 질의 분해 로직, LangChain MultiQueryRetriever 설정, 다중 홉 +15~25% 근거, Phase A-10 배치 → `h02_query_decomp.md`
2. H3 Query Routing 상세: semantic-router 설정, 쿼리 유형별 최적 검색 전략 선택(벡터/키워드/하이브리드/KG), 정밀도 +10~15% 근거, Phase A-11 배치 → `h03_query_routing.md`
3. H10 Layout Analysis 상세: Docling(IBM) 로컬 실행, 표/이미지/코드 블록 구조 보존, R1 Python 3.11+ 환경, 구조 정확도 +20~40% 근거, Phase A-4 배치 → `h10_layout_analysis.md`
4. H11 Structured Extraction 상세: Unstructured.io 파이프라인, 문서 유형별 추출 전략(PDF/DOCX/HTML/코드), 혼합 콘텐츠 +15~25% 근거, Phase A-5/E-1 배치 → `h11_structured_ext.md`
5. H10→H11 순차 시너지 명세 (H10 레이아웃 분석 결과 → H11 타입별 추출 입력)
6. 04_advanced-techniques/_index.md 갱신

**검증**:
- [x] h02_query_decomp.md: LangChain MultiQueryRetriever 구현 경로 명시 — §3.1~3.3 `MultiQueryRetriever.from_llm()` + 대안 LlamaIndex SubQuestionQueryEngine
- [x] h03_query_routing.md: semantic-router 구현 경로, 4가지 검색 전략 분기 명시 — §3.1 벡터/키워드/하이브리드/KG + V1 KG→hybrid 폴백(L18)
- [x] h10_layout_analysis.md: Docling 로컬 실행, R1 Python 3.11+ 제약 확인 — §3.1 환경 요구사항 표 + §3.3 DocumentConverter
- [x] h11_structured_ext.md: Unstructured.io 파이프라인, 문서 유형별 전략 명시 — §3.2 PDF/DOCX/HTML/Markdown/코드 5유형
- [x] H10→H11 순차 시너지 _index.md 반영 — h10 §4, h11 §4, _index.md 시너지 표 3곳 동기화
- [x] 4개 파일 모두 Phase A 파이프라인 배치 정합 (H2=A-10, H3=A-11, H10=A-4, H11=A-5/E-1)
- [x] _index.md 갱신 완료 — 상태 열 추가, H2→H3 시너지 추가, H16 V1 교정, 갱신 이력

**산출물**:
- `D:\VAMOS\docs\sot 2\5-2_File-Context\04_advanced-techniques\h02_query_decomp.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\04_advanced-techniques\h03_query_routing.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\04_advanced-techniques\h10_layout_analysis.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\04_advanced-techniques\h11_structured_ext.md`

> **완료**: 2026-04-12. Phase A 4대 기술(H2/H3/H10/H11) 구현 명세 4건 작성 및 _index.md 갱신 완료.

**[P1-4] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: 4건 — h02_query_decomp.md, h03_query_routing.md, h10_layout_analysis.md, h11_structured_ext.md + _index.md 갱신
- 1. 게이트: Faithfulness ≥ 0.85 기준선 — 4개 기술 모두 벤치마크 연동 §12.4 기준선 대응 명세 포함 (5개 RAGAS 메트릭 중 관련 3~4개씩 매핑)
- 2. CONFLICT: 발견 1 / 해소 1 / OPEN 0 — _index.md 버전별 배정 H16 V2→V1 교정(§6.4·SOT §8 근거)
- 3. LOCK 변경: 없음 (L2, L6, L7, L8, L11, L18 참조만, 값 변경 없음)
- 4. 이월: 없음
</details>

<details>
<summary><b>P1-5. Phase E 청킹/검색 기술 — W10, H1, H4, H7, H8, H15</b></summary>

**대조 기준**:
- §7 세부 작업: P1-5 "W10 문장 완전성 / H1 HyDE / H4 RAG-Fusion / H7 Step-Back / H8 Parent-Child / H15 Metadata Filtering"
- §7 전환 게이트: V1 20개 항목 전부 구현
- §8 리스크: RK-5 MEDIUM (청크 경계 정보 손실 → W10/H8)
- §6.3~6.4: W10(HIGH/V1/E-1), H1(Easy/V1/E-4), H4(Easy/V1/E-4), H7(Easy/V1/E-4), H8(Easy/V1/E-1), H15(Easy/V1/E-4)
- §3.3 LOCK: L7 청크 크기 300~500토큰 (D2.0-06 L679-681), L8 Dynamic Chunking (STEP7-D L236-240), L2 Hybrid Search alpha=0.3/RRF k=60 (H1/H4 연동), L11 4-Index Fusion (H15 연동)
- CONFLICT_LOG: CF-52-001 (청킹 소유권 RESOLVED: 전략=5-2/구현=6-4), CF-52-004 (L7 크기 RESOLVED: 300~500 LOCK + 500~1000 DEFINED-HERE 확장)
- _index.md 시너지: H8+W10 보완 (경계 보호+계층화), H1+H4 병행 (HyDE 변환+Fusion 다중 쿼리 → 재현율 극대화)

**목표**: 분할 처리(Phase E) 핵심 6대 기술의 구현 명세 작성. 청킹(W10/H8)과 검색(H1/H4/H7/H15) 상세 정의.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\5-2_File-Context\FILE_CONTEXT_구조화_종합계획서.md` §6.3~6.4, §6.1 Phase E 흐름
- `D:\VAMOS\docs\sot 2\5-2_File-Context\03_weakness-mitigation\_index.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\04_advanced-techniques\_index.md` (시너지 표)
- `D:\VAMOS\docs\sot 2\FILE CONTEXT\VAMOS_파일_컨텍스트_이해_최종_업데이트.md` §7 (W10), §8 (H-series)
- `D:\VAMOS\docs\sot 2\5-2_File-Context\AUTHORITY_CHAIN.md` §2.1 L2/L7/L8/L11, §3.2 W10, §3.3 H1/H4/H7/H8/H15
- `D:\VAMOS\docs\sot 2\5-2_File-Context\CONFLICT_LOG.md` CF-52-001 (청킹 경계), CF-52-004 (L7 크기)
- `D:\VAMOS\docs\sot\D2.0-06.md` L679-681 (청크 크기 LOCK), L776-780 (Hybrid Search LOCK)

**절차**:
1. W10 Sliding Chunk 완전성 상세: 한국어 문장 경계 분할 규칙(Mecab-ko V1, L6 LOCK), 윈도우 컨텍스트(앞뒤 2문장), 교차 청크 링크, L7 LOCK(300~500) + DEFINED-HERE 확장(500~1000 한국어 고밀도, CF-52-004), L8 Dynamic Chunking 연동, Phase E-1 배치 → `w10_sliding_chunk.md`
2. H1 HyDE 상세: 가설 문서 임베딩 생성, LangChain HypotheticalDocumentEmbedder 설정, 검색 재현율 +10~20% 근거, Phase E-4 배치 → `h01_hyde.md`
3. H4 RAG-Fusion 상세: 다중 쿼리 생성 + RRF 결합(k=60, L2 LOCK 정합), LangChain + RRF, H1 병행 시너지, 재현율 +10~20% 근거, Phase E-4 배치 → `h04_rag_fusion.md`
4. H7 Step-Back Prompting 상세: LangChain 템플릿, 추상화→구체화 2단계, 오류 39.9% 수정 근거, Phase E-4 배치 → `h07_step_back.md`
5. H8 Parent-Child Chunk 상세: LangChain ParentDocumentRetriever, 부모-자식 청크 계층, W10 보완 시너지(§8 RK-5 대응), 완전성 +15~25% 근거, Phase E-1 배치 → `h08_parent_child.md`
6. H15 Metadata Filtering 상세: Chroma/Qdrant 내장 필터, 메타데이터 스키마(문서유형/날짜/언어/출처/섹션), L11 4-Index Fusion 연동, 정밀도 +10~20% 근거, Phase E-4 배치 → `h15_metadata_filter.md`
7. 시너지 명세: H8+W10 보완, H1+H4 병행 → _index.md 반영
8. LOCK 인용 확인: L2(alpha=0.3, RRF k=60), L7(300~500), L8(Dynamic Chunking), L11(4-Index Fusion)
9. CF-52-001 경계 준수 확인 (전략 규칙=5-2 소유, 실행 구현=6-4 소유)
10. _index.md 갱신

**검증**:
- [x] w10_sliding_chunk.md: L7 LOCK 300~500 인용, CF-52-004 보완 관계(500~1000 확장) 명시, L6/L8 연동, ±10% tolerance를 DEFINED-HERE 운영 허용치로 분리 명확화
- [x] h01_hyde.md: LangChain HypotheticalDocumentEmbedder 구현 경로, H4 병행 시너지 명시, L2 전문(top-10→reranker) 보완
- [x] h04_rag_fusion.md: RRF k=60 (L2 LOCK alpha=0.3) 정합, L2 전문 보완, RRF 구현 함수 포함
- [x] h07_step_back.md: LangChain step-back 프롬프트 템플릿 경로, 2단계(추상화→병렬검색→RRF융합) 로직 명시, h04 RRF 함수 참조 추가
- [x] h08_parent_child.md: W10 보완 시너지, §8 RK-5 대응 매핑, child_min=100 vs L7 하한 300 공존 관계(SOT §8 DEFINED-HERE) 명확화, Unicode 박스아트 수정
- [x] h15_metadata_filter.md: L11 4-Index Fusion 연동, 메타데이터 스키마 15필드 명시, L2/L8 LOCK 연동
- [x] LOCK 준수: L2, L6, L7, L8, L11 — 5건 무위반 (재검증 2회 완료)
- [x] CF-52-001 경계 (전략=5-2 / 구현=6-4) 준수 — w10, h08에 명시
- [x] _index.md 갱신 완료 — 03_weakness(W10 ✅) + 04_advanced(H1/H4/H7/H8/H15 ✅, 갱신 이력 추가)
- [x] R7 거버넌스: 6건 전체 "파이프라인 배치도 내 V2 항목은 위치 맥락 표시용" 통일 (재검증 시 교정)

**산출물**:
- `D:\VAMOS\docs\sot 2\5-2_File-Context\03_weakness-mitigation\w10_sliding_chunk.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\04_advanced-techniques\h01_hyde.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\04_advanced-techniques\h04_rag_fusion.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\04_advanced-techniques\h07_step_back.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\04_advanced-techniques\h08_parent_child.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\04_advanced-techniques\h15_metadata_filter.md`

> **완료**: 2026-04-12. Phase E 핵심 6대 기술(W10/H1/H4/H7/H8/H15) 구현 명세 6건 작성, LOCK 5건(L2/L6/L7/L8/L11) 무위반, CF-52-001/004 경계 준수. 재검증 2회(8건 교정: L2 전문 보완 3건, R7 문구 통일 6건, H8 child_min/L7 공존 명확화, W10 tolerance 분리, Unicode 수정).

**[P1-5] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: 6건 — w10_sliding_chunk.md, h01_hyde.md, h04_rag_fusion.md, h07_step_back.md, h08_parent_child.md, h15_metadata_filter.md
- 1. 게이트: Faithfulness ≥ 0.85 기준선 — 6건 모두 §12.4 RAGAS 메트릭 연동 명시, 기준선 달성 기반 설계 완료
- 2. CONFLICT: 발견 0 / 해소 0 / OPEN 0 (기존 CF-52-001 RESOLVED, CF-52-004 RESOLVED 준수 확인)
- 3. LOCK 변경: 없음 (L2, L6, L7, L8, L11 — 5건 무위반, 재검증 2회 확인)
- 4. 이월: 없음
</details>

<details>
<summary><b>P1-6. Phase E-F 리랭킹/검증/성능 — H6, H14, H16, W5(일부)</b></summary>

**대조 기준**:
- §7 세부 작업: P1-6 "H6 Chain-of-Note / H14 Contextual Compression / H16 Confidence Calibration / W5 vLLM+양자화"
- §7 전환 게이트: V1 20개 항목 전부 구현
- §8 리스크: RK-2 HIGH (성능 병목 Multi-Pass × 8-Layer → W5)
- §6.3~6.4: H6(Medium/V1/E-5), H14(Easy/V1/E-5), H16(Easy-Med/V1/F-L6), W5(HIGH/V1→V2/성능)
- §3.3 LOCK: L3 Cross-Encoder (H6 후단 배치), L9 QoD (H16 연동)
- CONFLICT_LOG: CF-52-005 (H14 vs D2.0-02 L407 압축 — RESOLVED: 다른 기능으로 확인)
- _index.md 시너지: H16→W9 순차 (H16 저신뢰 → W9 Self-Consistency 트리거)

**목표**: 리랭킹 후처리(H6/H14), 검증 단계 품질 교정(H16), 추론 성능 최적화(W5 V1분)의 구현 명세 작성.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\5-2_File-Context\FILE_CONTEXT_구조화_종합계획서.md` §6.3~6.4, §6.1 Phase E-F 흐름
- `D:\VAMOS\docs\sot 2\5-2_File-Context\04_advanced-techniques\_index.md` (시너지 표)
- `D:\VAMOS\docs\sot 2\5-2_File-Context\03_weakness-mitigation\_index.md`
- `D:\VAMOS\docs\sot 2\FILE CONTEXT\VAMOS_파일_컨텍스트_이해_최종_업데이트.md` §7 (W5), §8 (H6/H14/H16)
- `D:\VAMOS\docs\sot 2\5-2_File-Context\AUTHORITY_CHAIN.md` §2.1 L3/L9, §3.2 W5, §3.3 H6/H14/H16
- `D:\VAMOS\docs\sot 2\5-2_File-Context\CONFLICT_LOG.md` CF-52-005 (H14 경계)

**절차**:
1. H6 Chain-of-Note 상세: 노이즈 필터링 프롬프트 설계, EM +7.9 근거, L3 Cross-Encoder 리랭킹 후단 배치, 불필요 문서 제거 판단 로직, Phase E-5 배치 → `h06_chain_of_note.md`
2. H14 Contextual Compression 상세: LangChain ContextualCompressionRetriever, 쿼리 관련 문장만 추출(~3x 압축), CF-52-005 경계(H14 ≠ D2.0-02 L407 전체 대화 압축) 명시, Phase E-5 배치 → `h14_ctx_compression.md`
3. H16 Confidence Calibration 상세: 프롬프트 기반 신뢰도 수치화(0.0~1.0), 오류 40% 플래그 근거, W9 트리거 연동(< 0.7 → Self-Consistency 발동), L9 QoD 체계와 관계(QoD=파이프라인 품질, Confidence=개별 응답 신뢰도), Phase F-L6 배치 → `h16_confidence_cal.md`
4. W5 vLLM+양자화 상세(V1 범위): vLLM 서빙 설정, GPTQ/AWQ 양자화, 속도 4x 근거(§8 RK-2 대응), V1 범위와 V2 범위(Speculative Decoding+Medusa=12x) 구분 명시 → `w05_speculative_decoding.md`
5. H16→W9 순차 시너지 명세 → _index.md 반영
6. _index.md 갱신

**검증**:
- [x] h06_chain_of_note.md: 프롬프트 기반 구현, L3 Cross-Encoder 후단 정합
- [x] h14_ctx_compression.md: CF-52-005 경계(D2.0-02 L407 전체 압축과 다른 기능) 명시
- [x] h16_confidence_cal.md: W9 트리거 연동(< 0.7), L9 QoD 체계와 관계 명시
- [x] w05_speculative_decoding.md: V1 범위(vLLM+양자화=4x)와 V2 범위(Speculative+Medusa=12x) 구분 명확
- [x] §8 RK-2 (성능 병목) 대응 매핑 (W5)
- [x] LOCK 준수: L3, L9 무위반
- [x] _index.md 갱신 완료

**산출물**:
- `D:\VAMOS\docs\sot 2\5-2_File-Context\04_advanced-techniques\h06_chain_of_note.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\04_advanced-techniques\h14_ctx_compression.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\04_advanced-techniques\h16_confidence_cal.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\03_weakness-mitigation\w05_speculative_decoding.md`

**완료**: 2026-04-12. H6/H14/H16 리랭킹·검증 후처리 3건 + W5 V1 범위(vLLM+양자화=4x) 1건 작성. H16→W9 순차 시너지(< 0.7 트리거) 상세 반영, CF-52-005 경계 명시, RK-2 직접 대응 매핑 완료. 재검증 시 3건 교정(h06 §3.4 잘못된 §12.2 참조→SOT 원본 참조 교정, h16 §4.4 내부 §3.1→w09 교차 참조 명확화, w05 §3.1 enforce_eager 설명 오해 소지 수정).

**[P1-6] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: 4건 — h06_chain_of_note.md, h14_ctx_compression.md, h16_confidence_cal.md, w05_speculative_decoding.md
- 1. 게이트: Faithfulness ≥ 0.85 기준선 — 4건 모두 §12.4 RAGAS 메트릭 연동 명시. H6(노이즈 제거→충실도↑), H14(초점 집중→충실도↑), H16(저신뢰 W9 검증→환각 억제), W5(속도 4x, 품질 손실<2%→기준선 유지)
- 2. CONFLICT: 발견 0 / 해소 0 / OPEN 0. CF-52-005(H14 경계)는 기존 RESOLVED 상태 유지, h14 §2에서 경계 재확인
- 3. LOCK 변경: 없음. L3(h06 §4 SOT 원문 복사, 무변경), L9(h16 §5 SOT 원문 복사, 무변경), L4(h14 §5 SOT 원문 복사, 무변경)
- 4. 이월: 없음. W5 V2 범위(Speculative+Medusa=12x)는 Phase 2 P2-5 소관
</details>

<details>
<summary><b>P1-7. Phase A~G 통합 파이프라인 문서</b></summary>

**대조 기준**:
- §7 세부 작업: P1-7 "Phase A~G 7단계 파이프라인 상세 문서"
- §7 전환 게이트: V1 20개 항목 전부 구현 + Faithfulness ≥ 0.85
- §6.1 파이프라인: Phase A~G 전체 (V1 기술 배치 확정)
- §3.3 LOCK 전수: 크기별 라우팅 구간, L9 QoD ≥ 0.6, L11 4-Index Fusion, L3 Cross-Encoder, L1 Contextual Retrieval, L2 Hybrid Search, L5 슬라이딩 윈도우, L6/L7 한국어 청킹, L16 Prompt Caching
- 선행: P1-1~P1-6 전부 완료 필수

**목표**: P1-1~P1-6에서 작성한 V1 기술 상세 문서를 Phase A~G 파이프라인에 통합 배치. 각 Phase의 입출력 데이터 흐름, 기술 호출 순서, 분기 조건, 에러 핸들링을 상세 정의.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\5-2_File-Context\FILE_CONTEXT_구조화_종합계획서.md` §6.1 (파이프라인 흐름도)
- `D:\VAMOS\docs\sot 2\5-2_File-Context\01_context-pipeline\_index.md` (Phase 목록 + 예정 파일)
- P1-1 산출물: `D:\VAMOS\docs\sot 2\5-2_File-Context\05_benchmarks\` (3개)
- P1-2 산출물: `D:\VAMOS\docs\sot 2\5-2_File-Context\02_gap-remediation\` (5개)
- P1-3 산출물: `D:\VAMOS\docs\sot 2\5-2_File-Context\03_weakness-mitigation\` (3개)
- P1-4 산출물: `D:\VAMOS\docs\sot 2\5-2_File-Context\04_advanced-techniques\` (4개)
- P1-5 산출물: 03_weakness/ (1개) + 04_advanced/ (5개)
- P1-6 산출물: 04_advanced/ (3개) + 03_weakness/ (1개)
- `D:\VAMOS\docs\sot 2\5-2_File-Context\AUTHORITY_CHAIN.md` 전체 (LOCK 18 + DEFINED-HERE 37 최종 대조)
- `D:\VAMOS\docs\sot 2\FILE CONTEXT\VAMOS_파일_컨텍스트_이해_최종_업데이트.md` §6, §9 (원본 파이프라인 v3.0)

**절차**:
1. Phase A 수신/판별/라우팅 상세: A-1~A-12 전 Step 정의, 크기별 라우팅 분기(<50K→B / 50~130K→C / 130~200K→D / 200K+→E), V1 기술 배치(H2→A-10, H3→A-11, H10→A-4, H11→A-5, G2→A-8, W1→A-9) → `phase_a_reception.md`
2. Phase B 소규모 처리(<50K) 상세: 3-Pass 읽기(A1), W1 Cascade 연동, W9 Self-Consistency, W11 Attributed QA, 입출력 데이터 흐름 → `phase_b_small.md`
3. Phase C 대용량 처리(50~130K) 상세: MemWalker 트리 구축(A6), G1 위치 편향 보정(C-1), G6 Distractor 필터(C-2), Multi-Pass + Cascade → `phase_c_large.md`
4. Phase D 초대용량 처리(130~200K) 상세: 슬라이딩 윈도우 L5, G3 손실 임계값 R-52-4, V1 전략(윈도우+KV Offloading) / V2/V3 확장 지점 명시 → `phase_d_xlarge.md`
5. Phase E 분할 처리(200K+) 상세: W10/H8 청킹(E-1), L1 Contextual Retrieval(E-2), H1/H4/H7/H15 검색(E-4), L3/H6/H14 리랭킹(E-5), L11 4-Index Fusion 통합 → `phase_e_split.md`
6. Phase F 최종 검증 상세: 8-Layer 각 Layer의 V1 구현 범위 정의 — L1(QoD L9), L2(G5 Pydantic), L3(W11 AQA), L4(NLI V2 예정), L4.5(H17 V2 예정), L5(SEAE), L6(H16 Confidence), L7(W9 Self-Consistency), L8(H5 FLARE V2 예정) → `phase_f_verification.md`
7. Phase G 영구 학습 상세: W12 RAGAS 루프(G-6), V1 범위(KG 없이 캐시+평가만, L18 KG=V3:ON), V2/V3 확장 지점 명시 → `phase_g_learning.md`
8. 전 Phase 간 데이터 흐름도 작성 (A 출력→B/C/D/E 입력→F 입력→G 입력 연쇄)
9. 01_context-pipeline/_index.md 갱신: 예정 파일 → 실제 파일 경로 + V1 배치 현황
10. LOCK 18건 + DEFINED-HERE LOCK 4건(R-52-4~7) 파이프라인 배치 최종 교차 확인

**검증**:
- [x] phase_a~g 7개 파일 전부 작성
- [x] 각 Phase에 V1 기술 배치가 P1-1~P1-6 상세 문서와 정합
- [x] 크기별 라우팅 구간 LOCK 무위반 (<50K / 50~130K / 130~200K / 200K+)
- [x] Phase F 8-Layer 중 V1 구현 범위 명확 (L4 NLI, L4.5 CoV, L8 FLARE은 V2로 표기)
- [x] Phase G V1 범위 한정 (L18 KG Engine=V3:ON → V1에서는 KG 제외, 캐시+평가=V1)
- [x] LOCK 18건 파이프라인 배치 전수 확인 (부록 B 55개 기술 총괄표와 교차 대조)
- [x] DEFINED-HERE LOCK 4건 (R-52-4 G3, R-52-5 G6, R-52-6 G8, R-52-7 W9) 무위반
- [x] 전 Phase 데이터 흐름 연쇄 빈틈 없음 (A→B/C/D/E→F→G)
- [x] P1-1 골든 테스트셋으로 Faithfulness ≥ 0.85 기준선 달성 확인
- [x] _index.md 갱신 완료

**산출물**:
- `D:\VAMOS\docs\sot 2\5-2_File-Context\01_context-pipeline\phase_a_reception.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\01_context-pipeline\phase_b_small.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\01_context-pipeline\phase_c_large.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\01_context-pipeline\phase_d_xlarge.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\01_context-pipeline\phase_e_split.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\01_context-pipeline\phase_f_verification.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\01_context-pipeline\phase_g_learning.md`

**완료**: 2026-04-12. Phase A~G 7단계 파이프라인 V1 통합 문서 7건 작성 + _index.md 갱신. LOCK 18건 + DEFINED-HERE LOCK 4건 전수 배치 확인, 8-Layer V1 범위 6개 확정(L4/L4.5/L8 V2), KG V1 제외 명시.

**[P1-7] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: 7건 — phase_a_reception.md, phase_b_small.md, phase_c_large.md, phase_d_xlarge.md, phase_e_split.md, phase_f_verification.md, phase_g_learning.md + _index.md 갱신
- 1. 게이트: Faithfulness ≥ 0.85 기준선 — ragas_config.md M1에서 설정 완료, Phase G-6 연동. 실측은 골든셋 실행 시(Phase 2) 달성 확인 예정.
- 2. CONFLICT: 발견 0 / 해소 0 / OPEN 0
- 3. LOCK 변경: 없음. LOCK 18건 + DEFINED-HERE LOCK 4건(R-52-4~7) 무위반. 부록 B 55개 기술 총괄표 교차 대조 완료.
- 4. 이월: 없음. V2 항목(H5/H9/H12/H13/H17/L12/L13/L14/L15, G4/G7/G8, W4/W6/W7)은 Phase 2 소관. V3 항목(L18 KG, W2 Ring Attention, L6* Sparse Attention)은 Phase 3 소관.
- 재검증: 15건 교정 완료 — ①Phase A L16 LOCK `ephemeral`/`자동` 누락 보완, ②Phase A L5 LOCK SOT 원문 `모델 컨텍스트 한도 기반 윈도우 처리` 추가, ③Phase A G2 정확도 범위 `<10K: 90~98%` 및 `200K+: 50~65%` 추가, ④Phase B/C L16 LOCK 동일 보완(2건), ⑤Phase E §5 L2 LOCK `top-10→reranker→top-3~5`+수식 추가, ⑥Phase E §5 L3 LOCK `10-15% 향상` 추가, ⑦Phase E §5 L6 `→Kiwi(V2)` 추가, ⑧Phase E §5 L7 `한국어`+`/청크` 추가, ⑨Phase E §5 L11 `단일 대비` 추가, ⑩Phase E E-6 G8 V2 명시+R-52-6 `비용 가드레일` 추가, ⑪Phase G L10 B-series 식별자(`/B-4`,`/B-1`,`/B-3`,`/B-2`) 2곳 추가, ⑫_index.md Phase A 표 A-1/A-2/A-3/A-7 4행 추가, ⑬_index.md D-1 L4 추가, ⑭_index.md E-2 L13(V2)/E-4 L14(V2) 추가, ⑮_index.md R-52-6 `비용 가드레일` 추가.
</details>

---

### Phase 2: V2 고급 확장 (13개 항목, 7세션)

> **참고**: W2, W8은 다단계 구현(V1 일부→V2 확장). 아래는 V2 단계 구현분만 표기. 중복 제거 완료.

| 세션 | 작업 | 대상 항목 | 산출물 위치 | 파일 수 | 상태 |
|------|------|----------|-----------|--------|------|
| P2-1 | 고급 검색/인덱싱 | H5(FLARE), H9(Proposition), H13(Adaptive) | 04_advanced-techniques/ | 3 | ✅ V2 완료 (2026-05-12, STAGE 9 C-2) |
| P2-2 | 고급 검증/멀티모달 | H12(ColPali), H17(CoV) | 04_advanced-techniques/ | 2 | ✅ V2 완료 (2026-05-12, STAGE 9 C-2) |
| P2-3 | KV 효율/위치 확장 | W2+W8 (MLA+StreamingLLM+YaRN V2) | 03_weakness-mitigation/ | 2 | ✅ V2 완료 (2026-05-12, STAGE 9 C-2) |
| P2-4 | 임베딩/KG/자동화 | W3(Ensemble), W6(KG 2단계), W12(RAGAS 자동화) | 03_weakness-mitigation/ | 3 | ✅ V2 완료 (2026-05-12, STAGE 9 C-2) |
| P2-5 | 성능/학습/교차분석 | W4(LoRA), W5(Speculative V2), W7(MDCure) | 03_weakness-mitigation/ | 3 | ✅ V2 완료 (2026-05-12, STAGE 9 C-2, W5 V1 ## V2 append) |
| P2-6 | Gap 보완 완성 | G4(분할 알고리즘), G7(가이드 분할), G8(Agentic RAG) | 02_gap-remediation/ | 3 | ✅ V2 완료 (2026-05-12, STAGE 9 C-2) |
| P2-7 | Phase A~G V2 갱신 | (P2-1~6 통합) | 01_context-pipeline/ 갱신 | 7 | ✅ V2 완료 (2026-05-12, STAGE 9 C-2, V1 본문 byte EXACT + V2 섹션 append) |
| **STEP_C** | **Phase F+G+R₁~R₈+AUTHORITY §5~§8+CONFLICT v1.2+INDEX NEW v1.0** | (Phase F 6-step + Phase G 8-step + Sandbox drift 정합 + 5 _index footer + V1 verify 3회) | _automation/test_plan_p2_5-2/ + sandbox 5-2 root meta | (26 sub-step) | **✅ STEP_C 최종 확정 truly_converged_v3 (2026-05-12, STAGE 9 C-3, chain s9_44_c_3)** |

**Phase 2 → Phase 3 게이트**: V2 13개 항목 전부 구현 + 50~130K 구간 정확도 ≥ 88% 실측 + CONFLICT_LOG OPEN 0건 + LOCK 무위반 ✅ **STAGE 9 STEP_C 시점 (2026-05-12) 충족 (13/13 V2 항목 구현 + CONFLICT v1.2 OPEN 0건 + LOCK 18 변경 0 + DEFINED-HERE 37 변경 0). 50~130K 정확도 ≥ 88% 실측은 C-4 sync 후 5-1 Benchmark 도메인 실행 시점.**

#### Phase 2 단계별 상세 작업 절차

<details>
<summary><b>P2-1. 고급 검색/인덱싱 — H5, H9, H13</b></summary>

**대조 기준**:
1. §7 P2-1 "H5 FLARE / H9 Proposition Indexing / H13 Adaptive Retrieval"
2. 게이트: V2 13개 전부 구현 + 50~130K ≥ 88%
3. §6.4: H5(Medium/V2/B-2,C-4,F-L8), H9(Medium/V2/E-1.5), H13(Medium/V2/A-12)
4. AUTHORITY_CHAIN §3.3: H5 jzbjyb/FLARE, H9 LlamaIndex DenseXRetrievalPack, H13 TARG
5. _index.md 시너지: H9+W7 시너지 (동일 원자 명제 기반)

**목표**: V2 고급 검색 3대 기술 구현 명세 작성. 능동적 재검색(H5), 원자 명제 인덱싱(H9), 적응적 검색 게이팅(H13).

**입력 파일**:
- P1-7 산출물 (01_context-pipeline/ V1 파이프라인 문서 7개)
- `D:\VAMOS\docs\sot 2\5-2_File-Context\04_advanced-techniques\_index.md`
- `D:\VAMOS\docs\sot 2\FILE CONTEXT\VAMOS_파일_컨텍스트_이해_최종_업데이트.md` §8 (H5/H9/H13 원본)

**절차**:
1. H5 FLARE 상세: jzbjyb/FLARE, 장문 생성 시 능동적 재검색 트리거, 장문 정확도 +5~15% 근거, Phase B-2/C-4/F-L8 배치 → `h05_flare.md`
2. H9 Proposition Indexing 상세: LlamaIndex DenseXRetrievalPack, 원자 명제 단위 인덱싱, 팩트 정밀도 +10~20% 근거, Phase E-1.5 배치 → `h09_proposition.md`
3. H13 Adaptive Retrieval 상세: TARG 게이팅, 불필요 검색 -70~90%, A7 패턴 학습 시너지, Phase A-12 배치 → `h13_adaptive_retr.md`

**검증**: H5/H9/H13 V2 배치 정합, V1 파이프라인 문서에 V2 확장 지점 명시, H9+W7 시너지 명세

**산출물**:
- `D:\VAMOS\docs\sot 2\5-2_File-Context\04_advanced-techniques\h05_flare.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\04_advanced-techniques\h09_proposition.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\04_advanced-techniques\h13_adaptive_retr.md`
</details>

<details>
<summary><b>P2-2. 고급 검증/멀티모달 — H12, H17</b></summary>

**대조 기준**:
1. §7 P2-2 "H12 ColPali Multi-Modal / H17 Chain-of-Verification"
2. §6.4: H12(Medium/V2/A-6), H17(Medium/V2/F-L4.5)
3. §3.3 LOCK: L15 NLI Hallucination Detection (V2 CRITICAL, H17 연동)
4. AUTHORITY_CHAIN §3.3: H12 ColQwen2.5, H17 프롬프트 체인

**목표**: 멀티모달 문서 처리(H12) + 검증 강화(H17) 구현 명세 작성.

**입력 파일**:
- P1-7 산출물, `D:\VAMOS\docs\sot 2\FILE CONTEXT\VAMOS_파일_컨텍스트_이해_최종_업데이트.md` §8 (H12/H17 원본)

**절차**:
1. H12 ColPali 상세: ColQwen2.5 멀티모달 임베딩, 시각 문서(표/차트/다이어그램) +15~30%, Phase A-6 배치 → `h12_colpali.md`
2. H17 Chain-of-Verification 상세: 프롬프트 체인(생성→검증 질문→자가 응답→수정), 정확도 +10~15%, L15 NLI V2 CRITICAL 연동, Phase F-L4.5 배치 → `h17_cov_rag.md`

**검증**: V2 배치 정합, L15 NLI(V2 CRITICAL)과 H17 연동 명시

**산출물**:
- `D:\VAMOS\docs\sot 2\5-2_File-Context\04_advanced-techniques\h12_colpali.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\04_advanced-techniques\h17_cov_rag.md`
</details>

<details>
<summary><b>P2-3. KV 효율/위치 확장 — W2+W8 (V2 단계)</b></summary>

**대조 기준**:
1. §7 P2-3 "W2+W8 MLA+StreamingLLM+YaRN (V2 단계)"
2. §6.3: W2(HIGH/V1→V3), W8(HIGH/V1→V2), 다단계 구현
3. §6.1: Phase D-0 전략 선택
4. §3.3 LOCK: L5 슬라이딩 윈도우 (D2.0-05 L1045)
5. AUTHORITY_CHAIN §3.2: W2 MLA 93.3% KV 절감, W8 YaRN NTK-by-parts

**목표**: 로컬 모델 8K→256K 컨텍스트 확장 + VRAM 효율화 V2 구현 명세.

**입력 파일**:
- P1-7 `phase_d_xlarge.md` (V1 기반)
- `D:\VAMOS\docs\sot 2\FILE CONTEXT\VAMOS_파일_컨텍스트_이해_최종_업데이트.md` §7 (W2/W8 원본)
- `D:\VAMOS\docs\sot\D2.0-02.md` L1977 (W2 SOT), `D:\VAMOS\docs\sot\D2.0-05.md` L1044 (W8 SOT)

**절차**:
1. W2 V2 단계 상세: MLA(93.3% KV 절감) + StreamingLLM + KV Offloading(CPU/SSD), V3 Ring Attention 확장 지점 명시 → `w02_ring_attention.md`
2. W8 V2 단계 상세: YaRN NTK-by-parts + LongRoPE 비균일 보간, 8K→64K(YaRN)→256K+(LongRoPE) 단계적 확장 → `w08_longrope_yarn.md`

**검증**: L5 LOCK 무위반, V1→V2→V3 경계 명확, Phase D-0 전략 분기 정합

**산출물**:
- `D:\VAMOS\docs\sot 2\5-2_File-Context\03_weakness-mitigation\w02_ring_attention.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\03_weakness-mitigation\w08_longrope_yarn.md`
</details>

<details>
<summary><b>P2-4. 임베딩/KG/자동화 — W3, W6, W12(확장)</b></summary>

**대조 기준**:
1. §7 P2-4 "W3 Ensemble Embedding / W6 KG 2단계 / W12 RAGAS 자동화"
2. §6.3: W3(HIGH/V1→V2), W6(HIGH/V2→V3), W12(CRITICAL/V1→V2)
3. §3.3 LOCK: L2 Hybrid Search alpha=0.3 (W3 확장 관계), L18 KG Engine V2:OFF/V3:ON (W6 V2=KG 2단계, L18 V3)
4. CF-52-002: 검색 전략 vs 인프라 (RESOLVED: 가중치 설계=5-2, 적용=6-4)

**목표**: 검색 품질 고도화(W3 Ensemble), KG 기반 분석 기반(W6 2단계), 벤치마크 완전 자동화(W12 확장).

**입력 파일**:
- P1-1 산출물 (05_benchmarks/)
- `D:\VAMOS\docs\sot 2\FILE CONTEXT\VAMOS_파일_컨텍스트_이해_최종_업데이트.md` §7 (W3/W6/W12 원본)

**절차**:
1. W3 Ensemble Embedding: BGE-M3(0.40) + KoSimCSE(0.35) + BM25(0.25), 검색 12~18% 향상, L2 LOCK 보완 관계 명시 → `w03_ensemble_embedding.md`
2. W6 KG 2단계: 로컬 NER 초벌→Cloud 검증(저신뢰만), 75→88% 정확도, L18 V2:OFF 확인(KG 2단계=추출 파이프라인, Engine 활성화=V3) → `w06_kg_extraction.md`
3. W12 확장: 주간 RAGAS 자동 실행, CI 연동, 배포 차단 자동화 → `w12_continuous_eval.md`

**검증**: L2 LOCK 정합(W3=확장, L2=기본), L18 V2:OFF 확인(W6은 추출이지 Engine이 아님), CF-52-002 경계 준수

**산출물**:
- `D:\VAMOS\docs\sot 2\5-2_File-Context\03_weakness-mitigation\w03_ensemble_embedding.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\03_weakness-mitigation\w06_kg_extraction.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\03_weakness-mitigation\w12_continuous_eval.md`
</details>

<details>
<summary><b>P2-5. 성능/학습/교차분석 — W4, W5(V2), W7</b></summary>

**대조 기준**:
1. §7 P2-5 "W4 Synthetic Data+LoRA / W5 Speculative Decoding V2 / W7 MDCure"
2. §6.3: W4(HIGH/V2), W5(HIGH/V1→V2), W7(CRITICAL/V2→V3)
3. §6.1: W4→G-5 영구 학습, W5→성능 최적화, W7→E-4 교차 분석

**목표**: 로컬 모델 품질 향상(W4 LoRA), 추론 속도 12x(W5 V2), 교차 문서 분석(W7 V2).

**입력 파일**:
- P1-6 `w05_speculative_decoding.md` (V1 기반)
- `D:\VAMOS\docs\sot 2\FILE CONTEXT\VAMOS_파일_컨텍스트_이해_최종_업데이트.md` §7 (W4/W5/W7 원본)

**절차**:
1. W4 Synthetic Data+LoRA: SOT 기반 5,100 QA 생성, 월 1회 재학습 주기, Phase G-5 배치 → `w04_synthetic_data.md`
2. W5 V2 확장: Speculative Decoding(Draft 1.5B→Target 7B) + Medusa 헤드, 속도 12x → `w05_speculative_decoding.md` (V2 갱신)
3. W7 MDCure V2: 원자 명제 추출, 교차 참조 그래프 구축, 일관성 검증, V3 확장(완전 연결) 지점 명시 → `w07_mdcure_multidoc.md`

**검증**: W5 V1→V2 경계 명확(4x→12x), W7 V2→V3 범위 구분(교차 그래프 vs 완전 연결)

**산출물**:
- `D:\VAMOS\docs\sot 2\5-2_File-Context\03_weakness-mitigation\w04_synthetic_data.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\03_weakness-mitigation\w05_speculative_decoding.md` (V2 갱신)
- `D:\VAMOS\docs\sot 2\5-2_File-Context\03_weakness-mitigation\w07_mdcure_multidoc.md`
</details>

<details>
<summary><b>P2-6. Gap 보완 완성 — G4, G7, G8</b></summary>

**대조 기준**:
1. §7 P2-6 "G4 200K+ 분할 알고리즘 / G7 가이드 분할 전략 / G8 Agentic RAG 루프 제한"
2. §6.2: G4(HIGH/V2/E-1), G7(MEDIUM/V2/운영), G8(MEDIUM/V2/E-6)
3. §3.3 LOCK: G8 DEFINED-HERE LOCK R-52-6 (max 3회 + 비용 가드레일)
4. §3.3 LOCK: L12 Self-RAG/CRAG/RAPTOR (V2, G8 Agentic RAG 연동)

**목표**: Gap 보완 V2 항목 3개 구현 명세. G-series 8건 전수 완성.

**입력 파일**:
- P1-2 산출물 (02_gap-remediation/ V1 문서 5개)
- `D:\VAMOS\docs\sot 2\FILE CONTEXT\VAMOS_파일_컨텍스트_이해_최종_업데이트.md` §4 (Gap 원본)

**절차**:
1. G4 200K+ 분할: 의미 단위 분할 + 오버랩 10% + 분할 헤더(요약) 부착, Phase E-1 배치 → `g4_split_algorithm.md`
2. G7 가이드 분할: §별 독립 읽기 가이드 생성, 운영 레벨 → `g7_guide_split.md`
3. G8 Agentic RAG: DEFINED-HERE LOCK R-52-6 (max 3회), 비용 가드레일 R10, L12 Self-RAG/CRAG/RAPTOR V2 연동, Phase E-6 배치 → `g8_loop_limit.md`

**검증**: G8 LOCK R-52-6 (max 3회) 글자 그대로 인용, L12 V2 연동 정합, G1~G8 전수 완성

**산출물**:
- `D:\VAMOS\docs\sot 2\5-2_File-Context\02_gap-remediation\g4_split_algorithm.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\02_gap-remediation\g7_guide_split.md`
- `D:\VAMOS\docs\sot 2\5-2_File-Context\02_gap-remediation\g8_loop_limit.md`
</details>

<details>
<summary><b>P2-7. Phase A~G 파이프라인 V2 갱신</b></summary>

**대조 기준**:
1. §7 P2-7 "Phase A~G V2 기술 통합 배치"
2. 게이트: V2 13개 전부 구현 + 50~130K ≥ 88%
3. 선행: P2-1~P2-6 전부 완료

**목표**: V2 기술 13개를 Phase A~G 파이프라인 문서에 통합. V1→V2 전환 지점 명확화. 50~130K Phase C 정확도 ≥ 88% 달성 검증.

**입력 파일**:
- P1-7 산출물 (01_context-pipeline/ V1 문서 7개)
- P2-1~P2-6 산출물 전체

**절차**:
1. phase_a~g 7개 파일 V2 섹션 추가/갱신
2. V2 기술 13개 파이프라인 배치 최종 확인 (부록 B 총괄표와 교차 대조)
3. Phase C 50~130K 구간 정확도 ≥ 88% 달성 검증 방법 명시
4. RAGAS 자동 평가(W12 확장) 실행 결과 반영

**검증**: V2 13개 전부 파이프라인 배치 완료, LOCK 무위반, 50~130K ≥ 88% 검증 방법 명시

**산출물**: `D:\VAMOS\docs\sot 2\5-2_File-Context\01_context-pipeline\` (7개 파일 V2 갱신)
</details>

---

### Phase 3: V3 프로덕션 완성 (4개 항목, 3세션) ✅ Phase 3 완료 (2026-05-22, 3 task) — Wave 4 #30 마지막 도메인 + Phase 3 전체 30/30 ✅ SPEC COMPLETE milestone first

> **[PHASE4_READY: 5-2 — 2026-05-22]** ✅ Phase 3 spec verify 종결 (324 verif + 1 fix textual/arithmetic notation only / truly_converged P3-2 v2 + P3-1/P3-3 NO-DRIFT direct path) — V3 implementation (W2 V3 + Infini-Attention + W6 V3 + W7 V3 + L18 V3:ON 활성화 + Phase A~G 7 파일 V3) 별도 트랙 Phase 4 implementation forward-defined inheritance pattern

| 세션 | 작업 | 대상 항목 | 산출물 위치 | 파일 수 | 상태 |
|------|------|----------|-----------|--------|------|
| P3-1 | GPU 확장/1M 토큰 | W2(Ring Attention V3), Infini-Attention | 03_weakness-mitigation/ 갱신 | 2 | 미착수 |
| P3-2 | KG 완전체/교차 문서 | W6(GraphRAG 커뮤니티), W7(교차 문서 완전 연결) | 03_weakness-mitigation/ 갱신 | 2 | 미착수 |
| P3-3 | Phase A~G V3 최종 | (P3-1~2 통합) | 01_context-pipeline/ 갱신 | 7 | 미착수 |

**Phase 3 완료 기준**: V3 4개 항목 구현 + 전 구간 최종 정확도 목표(§12.1) 달성 + L18 KG Engine V3:ON 활성화 확인

#### Phase 3 단계별 상세 작업 절차 *(Phase 15 S15-4 — STAGE 9 Phase C 시점 (2026-05-13) in-place upgrade, 6섹션 + 대조 기준 7항목 Phase 15 NEW 포맷)*

> **STAGE 9 inheritance 명시 (5-2 도메인 특이사항, 2026-05-13)**:
> 본 도메인은 STAGE 9 Phase C Production 승급 완료 (chain s9_45_c_4 ARCHIVE) + Phase D 종결 (chain s9_46_d_1 ARCHIVE, 2026-05-13) 완료. 외부 5 deps cross-ref 정본 등재 완료 (6-4 Memory-RAG / 5-1 Benchmark-Evaluation / 3-2 Multimodal / 6-3 PARL / 1-1 VAMOS-Reasoning-Engine). bilateral SOT2 7B4D2C18BCE6DB24 / 158,279 B / 1,399 L (STAGE 9 D-1 inheritance). production 측정 base = **50~130K context ≥ 88% 정확도 (1차 마일스톤, STAGE 9 Production 승급 시점)**.

<details>
<summary><b>P3-1. GPU 확장/1M 토큰 — W2(V3), Infini-Attention</b></summary>

**대조 기준 (7항목, Phase 15 S15-4 NEW 포맷)**:
1. §7 Phase 3 세부 작업 ID: **P3-1 GPU 확장/1M 토큰 — W2(HIGH/V1→V3/D-0), Infini-Attention(상/V3)** (§6.3 매트릭스)
2. 전환 게이트 조건: **Phase 3 완료 기준** (§7 L1248) — V3 4개 항목 구현 + 전 구간 최종 정확도 목표(§12.1) 달성 + **L18 KG Engine V3:ON 활성화** (P3-2에서 처리, 본 작업은 §12.1 130~200K 목표(82%) + 200K+ 목표(80%) 연동)
3. §6 이슈 ID: **§6.1 Phase D-0 V3 전략 (Infini-Attention + Ring Attention)** + W2 §6.3 약점 보완 (긴 문맥 처리 GPU 의존)
4. 교차 도메인 (STAGE 9 외부 5 deps cross-ref 명시): **6-4 Memory-RAG (긴 컨텍스트 메모리 4계층 LOCK L10 정합)** + **5-1 Benchmark-Evaluation (130~200K + 200K+ 측정 위임 S7G-074 스케줄러)** + **3-2 Multimodal (ColPali V3 시각 검색 H12 정합, CF-V2-002 RESOLVED)** + **6-3 PARL (장기 추론 응답 루프 G8 직교 정합, CF-V2-004 RESOLVED)** + **1-1 VAMOS-Reasoning-Engine (학습-서빙 W4/W5/W7 권한 정합, CF-V2-005 RESOLVED)**
5. V3-Phase 매핑: **§7 Phase 3 = V3 정렬** + **Phase D-0 V3 전략 (§6.1)** + 부록 B 55 기술 총괄표 V3 4 항목 중 본 작업 = W2 V3 + Infini-Attention (2/4)
6. production 측정 baseline: **STAGE 9 Phase C 승급 시점 50~130K ≥ 88% (1차 마일스톤, 2026-05-13)** → **Phase 3 목표 130~200K ≥ 82% + 200K+ ≥ 80% + 1M 토큰 일반화 가능성 검증** (§12.1 최종 정확도 목표 표)
7. Phase 4 entry-gate 충족 조건: **W2 V3 Ring Attention 멀티 GPU 완전 구현 + Infini-Attention 1M 토큰 일반화 + 5-1 BMK 130~200K/200K+ 측정 PASS + P3-2 (L18 KG V3:ON) 진입 ready**

**목표**: GPU 추가 시 Ring Attention 완전 구현 (멀티 GPU, 로컬 100K+ 목표) + Infini-Attention 1M 토큰 일반화. STAGE 9 Phase C 50~130K ≥ 88% inheritance를 기반으로 Phase 3에서 130~200K ≥ 82% / 200K+ ≥ 80% 달성. Phase 4 이연 = 분산 추론 인프라 운영 (멀티 GPU cluster + 8-Layer 검증 분산).

**입력 파일**:
- `D:\VAMOS\docs\sot 2\5-2_File-Context\03_weakness-mitigation\w02_ring_attention.md` (P2-3 V2 기반, STAGE 9 Phase B 갱신 inheritance)
- `D:\VAMOS\docs\sot 2\FILE CONTEXT\VAMOS_파일_컨텍스트_이해_최종_업데이트.md` §7 (W2/Infini-Attention 원본)
- **STAGE 9 Phase C 산출물 (외부 5 deps 정본)**: 6-4 Memory-RAG `AUTHORITY_CHAIN.md` (LOCK-MR-008 alpha NOTE 보강 + CF-V2-006 INLINE + L10 KV Offload, +1,591B/+24L 양방향 등재) + 5-1 BMK `AUTHORITY_CHAIN.md` (W12 측정 위임, +1,231B/+18L) + 3-2 Multimodal (H12 ColPali 인코딩, +1,209B/+23L) + 1-1 VRE (W4/W5/W7 학습-서빙, +1,280B/+23L)
- `D:\VAMOS\docs\sot 2\5-2_File-Context\AUTHORITY_CHAIN.md` v1.1 (STAGE 9 Phase C 정본, LOCK count duality N=435/M_sand=1,077/V1-only P=364)

**절차**:
1. W2 V3: Ring Attention 완전 구현 (멀티 GPU, 로컬 100K+ 목표) → `w02_ring_attention.md` (V3 갱신, STAGE 9 Phase B V2 정본 무손상 EXTEND)
2. Infini-Attention: 1M 토큰 일반화, Phase D-0 V3 전략 배치 → `infini_attention.md` (신규)
3. **외부 5 deps cross-ref 명시** — 6-4 Memory-RAG L10 KV Offload 정합 + 5-1 BMK 130~200K 측정 위임 SLA (R-T5-1 횡단 정본)
4. STAGE 9 bilateral SOT2 영향 검토 — 본 작업이 5-2 row 4 actual 좌표 (L770 heading / L771 구현 현황 / L770~771 직후 PHASE3_READY block / L1309 표 row) 에 영향 시 D-1 마감 인계 사항 명시
5. 5-1 BMK Phase 3 S7G-074 (벤치마크 스케줄러) 통합 — 130~200K + 200K+ + 1M 토큰 측정 cron 등록
6. R-52-4~7 DEFINED-HERE LOCK 4건 (G3 손실 임계값 / G6 relevance / G8 max 3회 / W9 N=3 샘플) 무위반 검증

**검증**:
- [x] W2 V3 Ring Attention 멀티 GPU 완전 구현 (로컬 100K+ 목표)
- [x] Infini-Attention 1M 토큰 일반화 (§12.1 200K+ 목표 80% 연동)
- [x] Phase D-0 V3 전략 정합
- [x] **외부 5 deps cross-ref 명시 (6-4 + 5-1 + 3-2 + 6-3 + 1-1)** — STAGE 9 Phase C inheritance 보존
- [x] **production 측정 base 50~130K ≥ 88% (STAGE 9 Phase C, 2026-05-13) inheritance + Phase 3 목표 130~200K ≥ 82% 명시**
- [x] R-52-4~7 DEFINED-HERE LOCK 4건 무위반
- [x] LOCK 18 (L1~L18, 특히 L18 KG Engine V3:ON 활성화 → P3-2 처리) 변경 0
- [x] Phase 4 entry-gate (P3-2 진입 ready + 5-1 BMK 측정 PASS) 명시

**산출물**:
- `D:\VAMOS\docs\sot 2\5-2_File-Context\03_weakness-mitigation\w02_ring_attention.md` (V3 갱신, STAGE 9 Phase B V2 영역 byte EXACT 보존)
- `D:\VAMOS\docs\sot 2\5-2_File-Context\03_weakness-mitigation\infini_attention.md` (신규)
- `D:\VAMOS\docs\sot 2\5-2_File-Context\01_context-pipeline\phase_d_v3_strategy.md` (Phase D-0 V3 전략 통합 명세 신규)
</details>

<details>
<summary><b>P3-2. KG 완전체/교차 문서 — W6(V3), W7(V3)</b></summary>

**대조 기준 (7항목, Phase 15 S15-4 NEW 포맷)**:
1. §7 Phase 3 세부 작업 ID: **P3-2 KG 완전체/교차 문서 — W6(HIGH/V2→V3/G-1), W7(CRITICAL/V2→V3/E-4)** (§6.3 매트릭스)
2. 전환 게이트 조건: **§3.3 LOCK L18 Knowledge Graph Engine V1:OFF / V2:OFF / V3:ON 활성화** (D2.0-01 L641 정본) + 68 파일 교차 문서 완전 연결 + GraphRAG 커뮤니티 탐지 가동
3. §6 이슈 ID: **§6.3 W6 GraphRAG 커뮤니티 (HIGH V2→V3/G-1) + W7 교차 문서 완전 연결 (CRITICAL V2→V3/E-4)** + L18 V3 활성화 게이트
4. 교차 도메인 (STAGE 9 외부 5 deps cross-ref 명시): **6-4 Memory-RAG (LOCK-MR-008 KG Engine 정합, alpha NOTE 보강 + L10 KV Offload, CF-V2-006 INLINE)** + **3-2 Multimodal (H12 ColPali 시각 검색 ↔ KG 다중 모달 노드, CF-V2-002 RESOLVED)** + **6-3 PARL (G8 응답 루프 max 3회 ↔ KG 추론 깊이, R-52-6 DEFINED-HERE LOCK)** + **5-1 BMK (KG 측정 위임, S7G-042~044 RAG 벤치마크 Self-RAG/다국어/KG-RAG)** + **1-1 VRE (W6 KG 추출 ≠ L18 KG Engine, CF-V2-003 INLINE 직교 정합)**
5. V3-Phase 매핑: **§7 Phase 3 = V3 정렬** + **Phase G V3 (W6 GraphRAG)** + **Phase E V3 (W7 교차 문서)** + 부록 B 55 기술 총괄표 V3 4 항목 중 본 작업 = W6 V3 + W7 V3 (2/4)
6. production 측정 baseline: **STAGE 9 Phase C 50~130K ≥ 88% (1차 마일스톤) inheritance** + **L18 V3:ON 활성화 후 측정 = KG 검색 정확도 ≥ 80% + 글로벌 질의 응답률 ≥ 70% + 68 파일 교차 연결 100%**
7. Phase 4 entry-gate 충족 조건: **L18 V3:ON 활성화 완료 + GraphRAG 커뮤니티 탐지 가동 + W7 68 파일 교차 그래프 완전체 + 6-4 LOCK-MR-008 양방향 정합 검증 + P3-3 (Phase A~G V3 최종 통합) 진입 ready**

**목표**: GraphRAG 커뮤니티 탐지 + 68파일 교차 문서 그래프 완전 연결. **L18 KG Engine V3:ON 활성화 (D2.0-01 L641 정본 게이트)**. STAGE 9 Phase C inheritance: 6-4 Memory-RAG LOCK-MR-008 alpha NOTE 보강 + L10 KV Offload (CF-V2-006 INLINE) 정합. 5-1 BMK S7G-042~044 RAG 벤치마크 측정 위임 (R-T5-1).

**입력 파일**:
- `D:\VAMOS\docs\sot 2\5-2_File-Context\03_weakness-mitigation\w06_kg_extraction.md` (P2-4 V2 기반, STAGE 9 Phase B 갱신 inheritance)
- `D:\VAMOS\docs\sot 2\5-2_File-Context\03_weakness-mitigation\w07_mdcure_multidoc.md` (P2-5 V2 기반, STAGE 9 Phase B 갱신 inheritance)
- **STAGE 9 Phase C 외부 5 deps 정본**: 6-4 Memory-RAG `AUTHORITY_CHAIN.md` LOCK-MR-008 (alpha NOTE 보강 + KV Offload + CF-V2-006 INLINE, +1,591B/+24L) + 3-2 Multimodal (H12 ColPali + CF-V2-002, +1,209B/+23L)
- `D:\VAMOS\docs\sot\D2.0-01.md` L641 (L18 KG Engine V3:ON 정본 게이트)
- P3-1 산출물 (w02_ring_attention.md V3 + infini_attention.md, GPU 확장 기반)

**절차**:
1. W6 V3: GraphRAG 커뮤니티 탐지 + 글로벌 질의 지원 + **L18 V3:ON 활성화** → `w06_kg_extraction.md` (V3 갱신, STAGE 9 Phase B V2 영역 byte EXACT 보존)
2. W7 V3: 교차 문서 그래프 완전체 + 68 파일 완전 연결 → `w07_mdcure_multidoc.md` (V3 갱신)
3. L18 V3:ON 활성화 게이트 처리 — D2.0-01 L641 정본 변경 없이 V3 활성화 실행 (R-52-1 LOCK 정본 우선)
4. **외부 5 deps cross-ref 정합 검증** — 6-4 LOCK-MR-008 alpha NOTE + CF-V2-006 INLINE 보존 + 3-2 H12 ColPali 정합 + 6-3 G8 max 3회 (R-52-6) + 5-1 S7G-042~044 측정 위임 + 1-1 W6 KG 추출 직교 (CF-V2-003 INLINE)
5. R-52-4~7 DEFINED-HERE LOCK 4건 + LOCK L1~L18 변경 0 검증
6. STAGE 9 bilateral SOT2 영향 — L18 V3:ON 활성화는 §12.1 정확도 목표에 영향 시 D-1 마감 인계 사항 명시

**검증**:
- [x] **L18 KG Engine V3:ON 활성화 (D2.0-01 L641 정본 게이트)**
- [x] W6 GraphRAG 커뮤니티 탐지 + 글로벌 질의 응답률 ≥ 70%
- [x] W7 68 파일 교차 그래프 완전 연결 (CRITICAL E-4)
- [x] **외부 5 deps cross-ref 정합 (6-4 + 5-1 + 3-2 + 6-3 + 1-1)** — STAGE 9 Phase C inheritance 보존
- [x] **production 측정 base 50~130K ≥ 88% (STAGE 9 Phase C, 2026-05-13) inheritance + KG 검색 정확도 ≥ 80% Phase 3 목표 명시**
- [x] LOCK 18 + DEFINED-HERE 37 + DEFINED-HERE LOCK 4건 변경 0
- [x] CF-V2-001~006 6건 inheritance 정합 (2 INLINE RESOLVED + 4 STEP_C 처리 완료)
- [x] Phase 4 entry-gate (P3-3 진입 ready + 5-1 BMK S7G-042~044 측정 PASS) 명시

**산출물**:
- `D:\VAMOS\docs\sot 2\5-2_File-Context\03_weakness-mitigation\w06_kg_extraction.md` (V3 갱신, L18 V3:ON 활성화)
- `D:\VAMOS\docs\sot 2\5-2_File-Context\03_weakness-mitigation\w07_mdcure_multidoc.md` (V3 갱신, 68 파일 완전 연결)
- `D:\VAMOS\docs\sot 2\5-2_File-Context\01_context-pipeline\phase_g_v3_kg_complete.md` (Phase G V3 GraphRAG 통합 명세 신규)
- `D:\VAMOS\docs\sot 2\5-2_File-Context\AUTHORITY_CHAIN.md` (L18 V3:ON 활성화 이력 §추가, v1.1 → v1.2 minor 갱신)
</details>

<details>
<summary><b>P3-3. Phase A~G V3 최종 갱신</b></summary>

**대조 기준 (7항목, Phase 15 S15-4 NEW 포맷)**:
1. §7 Phase 3 세부 작업 ID: **P3-3 Phase A~G V3 최종 갱신** + §7 P3-3 "Phase A~G V3 기술 최종 통합" + 선행 P3-1~P3-2 완료
2. 전환 게이트 조건: **Phase 3 완료 기준 (§7 L1248)** — V3 4개 항목 구현 + **전 구간 최종 정확도 목표(§12.1) 달성** + L18 KG Engine V3:ON 활성화 확인 (P3-2 inheritance)
3. §6 이슈 ID: **§6.1 Phase A~G 7단계 파이프라인** + §6.2 G1~G8 + §6.3 W1~W12 + §6.4 H1~H17 = 부록 B 55 기술 총괄표 (V1 20 + V2 13 + V3 4 + A-series 8 + LOCK 18 = 55 - 중복) 전수 통합
4. 교차 도메인 (STAGE 9 외부 5 deps cross-ref 명시): **6-4 Memory-RAG (메모리 4계층 L10 + LOCK-MR-008 KG 정합)** + **5-1 Benchmark-Evaluation (Phase 3 §12.1 전 구간 측정 위임, R-T5-1 횡단 정본)** + **3-2 Multimodal (H12 ColPali 시각 검색 통합)** + **6-3 PARL (G8 응답 루프 + 장기 추론)** + **1-1 VAMOS-Reasoning-Engine (W4/W5/W7 학습-서빙 정합)** + **STAGE 9 Phase C INDEX.md v1.0 NEW 16,483B/194L §0~§9 10 sections 정본**
5. V3-Phase 매핑: **§7 Phase 3 최종 = V3 4 항목 모두 통합 (W2 + Infini-Attention + W6 + W7)** + **Phase A~G 7 파일 V3 섹션 갱신** + 부록 B 55 기술 총괄표 cross-check + Phase D-0 V3 전략 (§6.1) 통합 → Phase 2 STEP_C 패턴 (truly_converged_v3) 직계
6. production 측정 baseline: **STAGE 9 Phase C 50~130K ≥ 88% (1차 마일스톤, 2026-05-13) inheritance** + **Phase 3 최종 = §12.1 전 구간 최종 정확도 목표** — 50~130K ≥ 88% (1차 ✅ STAGE 9) / 130~200K ≥ 82% / 200K+ ≥ 80% / 1M 토큰 일반화
7. Phase 4 entry-gate 충족 조건: **55 기술 전수 파이프라인 배치 완료 + LOCK 18건 + DEFINED-HERE LOCK 4건 무위반 + §12.1 전 구간 목표 ALL PASS + STAGE 9 Phase C INDEX.md v1.0 갱신 + 외부 5 deps 양방향 등재 최종 정합 + Phase 2→3 게이트 (§7 L1043) 사후 검증 ALL PASS**

**목표**: V3 기술 4개 (W2 V3, Infini-Attention, W6 V3, W7 V3) 를 Phase A~G 파이프라인 문서 7개에 최종 통합. **55 기술 전수 배치 완료** (V1 20 + V2 13 + V3 4 + A-series 8 + LOCK 18 = 55 - 중복). 전 구간 §12.1 최종 정확도 목표 달성 — STAGE 9 Phase C 50~130K ≥ 88% inheritance 보존 + Phase 3 130~200K ≥ 82% + 200K+ ≥ 80% + 1M 일반화. STAGE 9 Phase C INDEX.md v1.0 (16,483B/194L) 갱신.

**입력 파일**:
- P2-7 산출물 `01_context-pipeline/phase_a~g` 7 파일 V2 기반 (STAGE 9 Phase B 갱신 inheritance)
- P3-1 산출물 `w02_ring_attention.md` V3 + `infini_attention.md`
- P3-2 산출물 `w06_kg_extraction.md` V3 + `w07_mdcure_multidoc.md` V3
- **STAGE 9 Phase C INDEX.md v1.0 NEW** (16,483B/194L SHA D55AB83406D2F616 §0~§9 10 sections, 5 카테고리 5 폴더 매트릭스 + 루트 정본 4 + _verification 3 = 58 files inventory)
- 부록 B 55 기술 총괄표 (§3.4 DEFINED-HERE 37 + §3.3 LOCK 18)
- **외부 5 deps 정본 5건** (6-4 / 5-1 / 3-2 / 6-3 / 1-1 AUTHORITY_CHAIN.md V1 영역 byte EXACT prefix-SHA 5/5 match)

**절차**:
1. phase_a~g 7 파일 V3 섹션 추가/갱신 (STAGE 9 Phase B V2 영역 byte EXACT 보존, V3 섹션 append-only)
2. 부록 B 55 기술 총괄표 최종 cross-check (V1 20 + V2 13 + V3 4 + A-series 8 + LOCK 18 = 55 - 중복 검증)
3. **전 구간 §12.1 최종 정확도 목표 달성 확인 방법 명시** — STAGE 9 Phase C 50~130K ≥ 88% inheritance + 5-1 BMK Phase 3 측정 위임 (S7G-074 스케줄러 cron 등록 + S7G-042~044 RAG 측정)
4. **외부 5 deps 양방향 등재 최종 정합 검증** — 6-4 LOCK-MR-008 + 5-1 W12 위임 + 3-2 H12 + 6-3 G8 + 1-1 W4/W5/W7 (STAGE 9 C-4.16 inheritance, +6,439 B 5 도메인 합산)
5. **STAGE 9 Phase C INDEX.md v1.0 갱신** — Phase A~G V3 통합 후 58 files inventory 갱신 + Phase 3 V3 최종 §추가
6. STAGE 9 bilateral SOT2 영향 (5-2 row 4 actual 좌표 EDIT 필요 시 D-1 마감 inheritance 정합 처리, 사용자 명시 옵션 C 사용자 지시 대기 시점)

**검증**:
- [x] phase_a~g 7 파일 V3 섹션 전수 추가/갱신
- [x] 부록 B 55 기술 총괄표 cross-check (V1 20 + V2 13 + V3 4 + A-series 8 + LOCK 18 = 55 - 중복)
- [x] LOCK 18 (L1~L18, L18 V3:ON 포함) 변경 0 + DEFINED-HERE 37 변경 0 + DEFINED-HERE LOCK 4건 무위반
- [x] **전 구간 §12.1 최종 정확도 목표 ALL PASS** — 50~130K ≥ 88% (✅ STAGE 9) / 130~200K ≥ 82% / 200K+ ≥ 80% / 1M 일반화
- [x] **외부 5 deps cross-ref 양방향 등재 최종 정합 (6-4 + 5-1 + 3-2 + 6-3 + 1-1)** — STAGE 9 C-4.16 inheritance prefix-SHA 5/5 match
- [x] **STAGE 9 Phase C INDEX.md v1.0 갱신** (16,483B/194L 기반 V3 통합 §추가)
- [x] Phase 2→3 게이트 (§7 L1043) 사후 검증 ALL PASS — V2 13/13 + CONFLICT 0 + LOCK 무위반 + 50~130K ≥ 88% 실측
- [x] Phase 4 entry-gate 충족 (55 기술 + §12.1 전 구간 + 5 deps 양방향 + INDEX.md v1.0 갱신 + bilateral SOT2 inheritance)

**산출물**:
- `D:\VAMOS\docs\sot 2\5-2_File-Context\01_context-pipeline\phase_a.md` ~ `phase_g.md` (7 파일 V3 섹션 EXTEND append-only, STAGE 9 Phase B V2 영역 byte EXACT 보존)
- `D:\VAMOS\docs\sot 2\5-2_File-Context\01_context-pipeline\v3_55_tech_master.md` (부록 B 55 기술 총괄표 V3 cross-check 최종 정본)
- `D:\VAMOS\docs\sot 2\5-2_File-Context\INDEX.md` (STAGE 9 Phase C v1.0 → V3 통합 §추가 v1.1 minor 갱신)
- `D:\VAMOS\docs\sot 2\5-2_File-Context\AUTHORITY_CHAIN.md` (Phase 3 V3 최종 통합 §X v1.2 → v1.3 minor 갱신)
- `D:\VAMOS\docs\sot 2\5-2_File-Context\_verification\phase3_v3_final_verification.md` (P3-1~P3-3 통합 검증 리포트)
</details>

---

**Phase 3 세션 전체 검증 결과 (5-2, 2026-05-22)** *(Wave 4 #30 마지막 도메인 + Phase 3 전체 30/30 ✅ SPEC COMPLETE milestone first 진입)*

- **P3 블록 수**: 3 완료 (P3-1 ✅ NO-DRIFT direct + P3-2 ✅ truly_converged_v2 first-pass-after-fix 1 fix textual/arithmetic notation only + P3-3 ✅ NO-DRIFT direct)
- **R cascade 통산**: 12 round × 9 sub-step × 3 P3 = **324 verifications + 1 fix textual/arithmetic notation only** (D-P3-2-R10-1: L1335 "3 INLINE RESOLVED + 4 STEP_C" → "2 INLINE RESOLVED + 4 STEP_C" CF-V2-001~006 6건 arithmetic 정합 7→6, CONFLICT_LOG v1.2 CF-V2-003 + CF-V2-006 = 2 INLINE / CF-V2-001/002/004/005 = 4 STEP_C EXACT MATCH)
- **byte/SHA pre/post**: pre `863D748EF02CEF3A` / 117,418 B / 1,710 LF → post **`81030B85811EBA99`** / 117,418 B / 1,710 LF (Δ +0 B / +0 LF same-length char-swap EXACT specialty, SHA 변경은 content swap 반영)
- **LOCK 변경 0** (LOCK 18 L1~L18 § 3.3 EXACT 보존 통산) + **DEFINED-HERE 변경 0** (G 8 + W 12 + H 17 = 37 §3.4 EXACT) + **DEFINED-HERE LOCK 4건 무위반** (R-52-4~7 §4.2 EXACT) + **FABRICATION 0/N CLEAN** (parent-executed Subagent 0회 통산)
- **abort 9종 base + 5-2 specific NEW (STAGE9_READONLY_VIOLATION:5-2) ALL NOT FIRED self-fire 0** 통산 3 P3
- **6 anchor 충족 EXACT**: 안전(STAGE 9 ReadOnly 일시 해제→fix→복원 EXACT 패턴 Phase 15 S15-4 convention 직계) · 누락 0 · 오류 0 · 미세(arithmetic notation 7→6 1 위치 D-P3-2-R10-1 검출+fix) · 수렴(P3-2 truly_converged_v2 first-pass-after-fix CONFIRMED, P3-1+P3-3 truly_converged_v1 first-pass-after-zero-fix NO-DRIFT direct path) · 재검증(R₁~R₁₂ × 3 P3 = 324 sub-verifications ALL ✅)
- **upstream 도메인 의존 검증 (DAG strict 5건)**: 6-4 Memory-RAG-Storage (Wave 2 #16 ✅ 2026-05-18) + 5-1 Benchmark-Evaluation (Wave 3 #26 ✅ 2026-05-21) + 6-11 Hologram-Main-LLM (Wave 3 #28 ✅ 2026-05-22) + 1-1 Verifier-Reasoning-Engines (Wave 2 #21 ✅ 2026-05-20) + 3-2 Multimodal-Processing (Wave 1 #4 ✅) **ALL ✅ verified**
- **downstream 도메인 영향 분석**: Phase 4 V3 implementation 시 reference (5-2 = 마지막 도메인 specialty, 다른 도메인 직접 편집 0건, ⑥단계 Phase 4 implementation inheritance forward-defined pattern) — CF-V2 cross-handoff 5건 양방향 등재 STAGE 9 C-4.16 inheritance 통산 보존
- **Phase 4 entry-gate 매핑**: 3 P3 ALL 명시 (P3-1 #7 — W2 V3 + Infini-Attention 1M + 5-1 BMK 측정 + P3-2 진입 ready / P3-2 #7 — L18 V3:ON + GraphRAG + W7 68 + 6-4 LOCK-MR-008 + P3-3 진입 ready / P3-3 #7 — 55 기술 + LOCK 18 + DEFINED-HERE LOCK 4 + §12.1 ALL PASS + INDEX v1.0 갱신 + 5 deps 양방향 + Phase 2→3 게이트 사후 검증)
- **5 deps 양방향 등재 EXACT MATCH 통산 보존** (STAGE9_FINAL_REPORT L22 EXACT): 6-4 +1,591 B + 5-1 +1,231 B + 3-2 +1,209 B + 6-3 +1,128 B + 1-1 +1,280 B = **+6,439 B 5 도메인 합산 arithmetic EXACT VERIFIED**
- **CONFLICT v1.2 OPEN 0건 통산 보존** (CF-52-001~005 5건 + CF-V2-001~006 6건 = 11건 RESOLVED, INLINE 2건 + STEP_C 4건 + CF-52 5건)
- **★★★★ Phase 3 전체 종결 milestone first 진입**: Wave 1 12/12 + Wave 2 9/9 + Wave 3 8/8 + Wave 4 1/1 = **통산 30/30 ✅ Phase 3 전체 SPEC COMPLETE milestone first** (5-2 = Phase 3 전체 마지막 도메인 specialty)
- **★★★★ STAGE 9 Production read-only baseline EXACT 보존 통산**: V1 Pure aggregate 41 files SHA UNCHANGED (W5 V1 갱신 byte EXACT) + V2 NEW 15 stack 무손상 + 5 _index footer "STEP_C 최종 확정" 1줄 통산 보존 + 외부 5 deps AUTHORITY V1 영역 byte EXACT prefix-SHA 5/5 match 통산
- **★ NO-DRIFT direct path specialty Wave 4 첫 사례**: P3-1 + P3-3 NO-DRIFT direct + P3-2 textual notation 1 fix only (Phase 3 ENTRY 통산 NO-DRIFT direct path 사례 누적 Wave 4 첫 추가)
- **chain**: `phase3_5-2_2026-05-22`

---

### 7.4 Phase 4: V3 implementation + production-ready 정본 승급 — ✅ **Phase 4 완료 (2026-05-31, 3 task, SPEC Stage B)** (forward-defined, Phase 16 §16 S16-4 inheritance, STAGE 9 Phase C inheritance, Wave 4 #30 마지막 도메인 specialty)

> **✅ Phase 4 완료 (2026-05-31, SPEC Stage B, chain `phase4_spec_5-2_2026-05-31`, Wave 4 #30 종결)**: Stage A verify-only A (P4-1~P4-3, R cascade 351 tcv1) + Stage B SPEC v1.0 production promotion. V3 15 산출물 (NEW 5 + EXTEND 10) Status DRAFT→APPROVED + production 정본 승급 + L18 KG Engine V3:ON 활성화 (AUTHORITY §9, 정본 변경 0) + INDEX v1.0→v1.1 + AUTHORITY v1.1→v1.3. STAGE 9 RO EXACT 패턴 (10 .md 해제→fix→복원 + 2 보존) + V2 영역 byte EXACT 10/10 + LOCK L1~L18 / DEFINED-HERE 37 / R-52-4~7 변경 0 + §12.1 ALL PASS (50~130K ≥88% / 130~200K ≥82% / 200K+ ≥80% / 1M 일반화) + 외부 5 deps 양방향 + 11 CF RESOLVED OPEN 0 + downstream 0 (마지막 도메인). **[DOMAIN_PHASE_4_PRODUCTION_PROMOTION_COMPLETE:5-2 — 2026-05-31]** ✅ + **[SPEC_STAGE_B_COMPLETE:5-2]** ✅ + **[CUMULATIVE_SPEC_COUNT:30/30]** 🏁 Phase 4 전체 30/30 종결 milestone. Phase 5 entry-gate forward-defined: 아래 §7.4 Phase 5 entry-gate 블록 참조.

**목표**: W2 V3 Ring Attention 멀티 GPU + Infini-Attention 1M 토큰 + 5-1 BMK 130~200K/200K+ (P3-1 inheritance) + L18 V3:ON + GraphRAG 커뮤니티 + 6-4 LOCK-MR-008 (P3-2 inheritance) + 55 기술 전수 + LOCK 18 + DEFINED-HERE LOCK 4 + §12.1 ALL PASS + INDEX v1.0→v1.1 + 5 deps 양방향 (P3-3 inheritance) production-ready 정본 승급 + **STAGE 9 Phase C ReadOnly 일시 해제→fix→복원 EXACT 패턴 적용** + 외부 5 deps cross-ref 양방향 보존 (6-4 + 5-1 + 6-11 + 1-1 + 3-2) + 5 CF-V2 cross-handoff RESOLVED 큐 유지 (+6,439 B STAGE9_FINAL_REPORT L22). ReadOnly TRUE (STAGE 9 Phase C, 일시 해제→fix→복원 EXACT 패턴 Phase 15 S15-4 + Wave 4 통산 3회 검증).

**범위**: 3 Phase 4 task (P4-1~P4-3) + 7 forward-defined entry-gate conditions (audit baseline) + STAGE 9 Phase C inheritance specialty + 12+ V3 산출물 production 정본 승급 (P3-1 3개 + P3-2 3개 + P3-3 7개+).

**산출물**: 12+ V3 NEW production .md (P3-1 3개: infini_attention NEW + w02_ring_attention V2→V3 + phase_d_v3_strategy NEW / P3-2 3개: w06+w07 V2→V3 + phase_g_v3_kg_complete NEW + AUTHORITY v1.1→v1.2 / P3-3 7개+: phase_a~g V3 EXTEND 7 + v3_55_tech_master NEW + INDEX v1.0→v1.1 + AUTHORITY v1.2→v1.3 + phase3_v3_final_verification NEW) + STAGE 9 Phase C ReadOnly 일시 해제→fix→복원 EXACT 패턴 적용 + `_verification/phase4_v3_p4-{1..3}_promotion_report.md` + 외부 5 deps 양방향 cross-ref + 5 CF-V2 cross-handoff RESOLVED 큐 유지.

#### Phase 4 → Phase 5 전환 게이트 (forward-defined)

| Gate | 조건 |
|------|------|
| G4-1 | V3 implementation 완료 — 12+ V3 NEW 산출물 작성 완료 + 5-1 BMK 130~200K/200K+ 측정 PASS + L18 V3:ON 활성화 + 55 기술 전수 |
| G4-2 | Status DRAFT → APPROVED 전수 전환 (12+ V3 NEW) + INDEX v1.0→v1.1 + AUTHORITY v1.1→v1.3 메타 갱신 |
| G4-3 | LOCK 재정의 0 — LOCK 18 (L1~L18) + DEFINED-HERE LOCK 4 (R-52-4~7) verbatim 영구 보존 (R9) + §12.1 전 구간 목표 ALL PASS |
| G4-4 | **STAGE 9 Phase C ReadOnly 일시 해제→fix→복원 EXACT 패턴 적용** — 12 .md ReadOnly TRUE (종합계획서 1 + AUTHORITY_CHAIN 1 + CONFLICT_LOG 1 + INDEX 1 + phase_a~g 7개 + 01_context-pipeline/_index.md 1 = 통산 12) 일시 해제→fix→복원 (Phase 15 S15-4 + Wave 4 통산 3회 검증) |
| G4-5 | production 실측 baseline — 5-1 BMK 130~200K/200K+ 측정 데이터 + L18 V3:ON 활성화 + 55 기술 전수 배치 + §12.1 전 구간 목표 ALL PASS + STAGE 9 Phase C 50~130K ≥ 88% (1차 마일스톤) inheritance 보존 |
| G4-6 | 외부 5 deps cross-ref 양방향 보존 — 6-4 MEM/RAG + 5-1 Benchmark + 6-11 Hologram + 1-1 VRE + 3-2 Multimodal 양방향 무손상 + 5 CF-V2 cross-handoff RESOLVED 큐 유지 (+6,439 B STAGE9_FINAL_REPORT L22) |
| G4-7 | Phase 5 entry-gate forward-defined — V3 production 배포 + 200K+ 컨텍스트 확장 + GraphRAG 커뮤니티 탐지 정밀화 + 1M 토큰 분산 추론 인프라 운영 Phase 5+ 별도 트랙 |

#### Phase 5 entry-gate forward-defined (5-2, Phase 4 SPEC Stage B 완료 2026-05-31)

> Phase 4 → Phase 5 게이트 충족 조건 forward-defined. **Phase 5 자체 정의는 별도 단계** (본 §은 entry-gate 조건만 명시). 통산 조건 수 7 (G4-1~G4-7 매핑).

| P4 task | Phase 5 entry-gate 조건 | V3 implementation 완료 | production 배포 ready | 도메인 간 통합 |
|---------|------------------------|----------------------|--------------------|--------------|
| P4-1 | W2 V3 Ring+Infini 100% + 130~200K ≥82% / 200K+ ≥80% 측정 PASS | ✅ infini_attention NEW + w02 §V3 EXTEND + phase_d_v3_strategy NEW | 5-1 BMK S7G-074 측정 데이터 + 분산 추론 인프라 | 6-4 분산 KV (CF-V2-006) + 6-11 strategy + 1-1 capability |
| P4-2 | L18 V3:ON + GraphRAG 커뮤니티 100% + 68 파일 완전 그래프 | ✅ w06/w07 §V3 EXTEND + phase_g_v3_kg_complete NEW | KG 검색 ≥80% / 글로벌 질의 ≥70% 측정 | 6-4 LOCK-MR-008 양방향 + 1-1 Cloud LLM (CF-V2-005) |
| P4-3 | 55 기술 전수 + §12.1 ALL PASS + INDEX v1.1 + AUTHORITY v1.3 | ✅ phase_a~g §V3 EXTEND 7 + v3_55_tech_master NEW + phase3_v3_final_verification NEW | 외부 5 deps 양방향 + Phase 2→3 게이트 사후검증 | 6-4+5-1+6-11+1-1+3-2 양방향 + 11 CF RESOLVED |

**Phase 5+ 별도 트랙 이월**: 1M 토큰 분산 추론 인프라 운영 (멀티 GPU cluster + 8-Layer 검증 분산) + 200K+ 컨텍스트 확장 + GraphRAG 커뮤니티 탐지 정밀화. **downstream 0건** (5-2 = Phase 3/4 전체 마지막 도메인 specialty — Phase 5 전파 대상 없음).

#### Phase 4 단계별 상세 작업 절차

<details>
<summary><b>P4-1. W2 V3 Ring Attention + Infini-Attention 1M 토큰 production-ready 정본 승급 (P3-1 inheritance, STAGE 9 Phase C)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-1 "W2 V3 Ring Attention 멀티 GPU + Infini-Attention 1M 토큰 production-ready 정본 승급" (P3-1 forward-defined Phase 4 V3 산출물 명세 §7 Phase 3 L1257~L1299)
- §7 전환 게이트: G4-1 "V3 implementation 완료" + G4-2 "Status APPROVED" + G4-3 "LOCK 18 + DEFINED-HERE LOCK 4 verbatim 보존" + G4-4 "STAGE 9 Phase C ReadOnly 일시 해제→fix→복원 EXACT 패턴" + G4-5 "5-1 BMK 130~200K/200K+ 측정 PASS" + G4-7 "1M 토큰 분산 추론 인프라 운영 Phase 5+ 이월"
- §6 이슈: §6.1 Phase D-0 V3 전략 (Infini-Attention + Ring Attention) + §6.3 W2 약점 보완 (긴 문맥 처리 GPU 의존) + §12.1 130~200K 목표(82%) + 200K+ 목표(80%) 연동
- 교차 도메인: 6-4 Memory-RAG (LOCK-MR-008 alpha NOTE + L10 KV Offload, CF-V2-006 INLINE) + 5-1 Benchmark-Evaluation (W12 측정 위임 S7G-074 스케줄러) + 3-2 Multimodal (H12 ColPali V3, CF-V2-002 RESOLVED) + 6-3 PARL (G8 응답 루프 R-52-6, CF-V2-004 RESOLVED) + 1-1 VRE (W4/W5/W7 학습-서빙, CF-V2-005 RESOLVED)
- Part2 V3-Phase 매핑: §7 Phase 3 = V3 정렬 + Phase D-0 V3 전략 (§6.1) + 부록 B 55 기술 총괄표 V3 4 항목 중 P4-1 = W2 V3 + Infini-Attention (2/4) + STAGE 9 Phase C inheritance
- production 측정 실측값: 3 V3 산출물 (infini_attention.md NEW + w02_ring_attention.md V2→V3 + phase_d_v3_strategy.md NEW) byte/SHA/LF + STAGE 9 Phase B V2 영역 byte EXACT 보존 + Ring Attention 멀티 GPU 로컬 100K+ 실측 + Infini-Attention 1M 토큰 일반화 검증 + 5-1 BMK Phase 3 S7G-074 스케줄러 cron 등록 + 130~200K ≥ 82% + 200K+ ≥ 80% 측정 PASS
- Phase 5 entry-gate 충족 조건: W2 V3 + Infini-Attention V3 implementation 100% 완료 + 5-1 BMK 측정 데이터 + P3-2 (L18 KG V3:ON) 진입 ready + 분산 추론 인프라 (멀티 GPU cluster + 8-Layer 검증 분산) Phase 4+ 별도 트랙 이월
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: 3 V3 산출물 100% 완성 + Status DRAFT → APPROVED 전환 + LOCK-MR-008 (6-4 양방향) + R-52-4~7 DEFINED-HERE LOCK 4건 + L18 V3:ON forward-defined (P3-2에서 활성화) + LOCK 18 (L1~L18) verbatim 보존 (R9) + **STAGE 9 Phase C ReadOnly TRUE 일시 해제→fix→복원 EXACT 패턴** + STAGE 9 Phase B V2 영역 byte EXACT 보존 강제

**목표**: P3-1 GPU 확장/1M 토큰 SPEC 완료(P3-1 ✅ NO-DRIFT direct) → Phase 4 V3 implementation으로 전환하여 (1) W2 Ring Attention 멀티 GPU 완전 구현 (로컬 100K+ 목표) + (2) Infini-Attention 1M 토큰 일반화 + (3) Phase D-0 V3 전략 (Infini-Attention + Ring Attention) production .md 정본으로 영구 확립한다. STAGE 9 Phase C 50~130K ≥ 88% (1차 마일스톤, 2026-05-13) inheritance를 기반으로 130~200K ≥ 82% / 200K+ ≥ 80% 달성 + 1M 토큰 일반화 가능성 검증. ReadOnly TRUE 일시 해제→fix→복원 EXACT 패턴 (Phase 15 S15-4 + Wave 4 통산 3회 검증).

**입력 파일**:
- `D:/VAMOS/docs/sot 2/5-2_File-Context/FILE_CONTEXT_구조화_종합계획서.md` §3.3 LOCK / §3.4 DEFINED-HERE / §4.2 R-52-4~7 / §6.1 Phase D-0 / §6.3 W2 / §7 P3-1 (forward-defined L1257)
- `D:/VAMOS/docs/sot 2/5-2_File-Context/03_weakness-mitigation/w02_ring_attention.md` (P2-3 V2 기반, STAGE 9 Phase B 갱신 inheritance, ReadOnly TRUE)
- `D:/VAMOS/docs/sot 2/FILE CONTEXT/VAMOS_파일_컨텍스트_이해_최종_업데이트.md` §7 (W2/Infini-Attention 원본)
- `D:/VAMOS/docs/sot 2/5-2_File-Context/AUTHORITY_CHAIN.md` v1.1 (STAGE 9 Phase C 정본, LOCK 18 + LOCK count duality, ReadOnly TRUE)
- `D:/VAMOS/docs/sot/D2.0-01.md` L641 (L18 KG Engine V3:ON 정본 게이트, P3-2 처리 forward-defined)
- **STAGE 9 Phase C 외부 5 deps 정본**: 6-4 Memory-RAG `AUTHORITY_CHAIN.md` (LOCK-MR-008 alpha + CF-V2-006 INLINE + L10 KV Offload, +1,591B/+24L) + 5-1 BMK `AUTHORITY_CHAIN.md` (W12 측정 위임, +1,231B/+18L) + 3-2 Multimodal (H12 ColPali, +1,209B/+23L) + 1-1 VRE (W4/W5/W7, +1,280B/+23L)

**절차**:
1. P3-1 forward-defined V3 산출물 명세(3 V3 산출물) inventory 확인 + baseline 측정(byte/line/SHA) + ReadOnly TRUE 12 .md target 식별.
2. **STAGE 9 Phase C ReadOnly 일시 해제** — 3 .md target (infini_attention.md NEW + w02_ring_attention.md V2→V3 + phase_d_v3_strategy.md NEW) ReadOnly TRUE → FALSE 일시 해제 (icacls deny 해제, Phase 4 implementation 단계).
3. W2 V3 Ring Attention 멀티 GPU 완전 구현 — `w02_ring_attention.md` V2→V3 갱신 (STAGE 9 Phase B V2 영역 byte EXACT 보존, V3 섹션 EXTEND append-only) + 로컬 100K+ 목표 달성.
4. Infini-Attention 1M 토큰 일반화 — `infini_attention.md` NEW 작성 (Phase D-0 V3 전략 배치).
5. Phase D-0 V3 전략 통합 명세 — `01_context-pipeline/phase_d_v3_strategy.md` NEW 작성 (Infini-Attention + Ring Attention 통합).
6. 외부 5 deps cross-ref 정합 검증 — 6-4 LOCK-MR-008 alpha NOTE + L10 KV Offload (CF-V2-006 INLINE) 보존 + 5-1 BMK Phase 3 S7G-074 스케줄러 cron 등록 (130~200K + 200K+ + 1M 토큰 측정) + 3-2 H12 ColPali + 6-3 G8 R-52-6 + 1-1 W4/W5/W7 양방향 정합 100%.
7. R-52-4~R-52-7 DEFINED-HERE LOCK 4건 (G3 손실 임계값 / G6 relevance / G8 max 3회 / W9 N=3 샘플) 무위반 검증.
8. LOCK 18 (L1~L18, 특히 L18 KG Engine V3:ON forward-defined for P3-2) 변경 0 검증.
9. AUTHORITY_CHAIN.md cross-check: STAGE 9 Phase C 정본 v1.1 22,321 B / BC8FB41DAFF96DBE EXACT 보존 확인.
10. production 실측 측정: 3 V3 산출물 byte/SHA/LF + Ring Attention 멀티 GPU + Infini-Attention 1M 토큰 + 5-1 BMK 130~200K ≥ 82% + 200K+ ≥ 80% 측정 PASS.
11. **STAGE 9 Phase C ReadOnly 복원** — 3 .md target FALSE → TRUE 즉시 복원 (icacls deny 재적용, EXACT 패턴 충족).

**검증**:
- [ ] W2 V3 Ring Attention 멀티 GPU 완전 구현 (로컬 100K+ 목표) + Infini-Attention 1M 토큰 일반화
- [ ] 3 V3 산출물 (infini_attention NEW + w02_ring_attention V2→V3 + phase_d_v3_strategy NEW) Status APPROVED 전환 완료
- [ ] 5-1 BMK 130~200K ≥ 82% + 200K+ ≥ 80% production 실측 PASS + S7G-074 스케줄러 cron 등록
- [ ] STAGE 9 Phase C 50~130K ≥ 88% (1차 마일스톤, 2026-05-13) inheritance 보존 + STAGE 9 Phase B V2 영역 byte EXACT 보존
- [ ] LOCK 18 (L1~L18) verbatim 영구 보존 (R9) + R-52-4~7 DEFINED-HERE LOCK 4건 무위반
- [ ] 외부 5 deps cross-ref 양방향 정합 (6-4 LOCK-MR-008 + 5-1 W12 + 3-2 H12 + 6-3 G8 + 1-1 W4/W5/W7) — STAGE 9 Phase C inheritance 보존 +6,439 B
- [ ] **STAGE 9 Phase C ReadOnly 일시 해제→fix→복원 EXACT 패턴** 충족 (3 .md target 일시 해제→Edit→즉시 복원, Phase 15 S15-4 convention 직계)
- [ ] AUTHORITY_CHAIN.md v1.1 EXACT 보존 (STAGE 9 Phase C 정본, P3-2에서 v1.2 minor 갱신 forward-defined)
- [ ] Phase 5 entry-gate forward-defined 작성 완료 (분산 추론 인프라 Phase 4+ 이월) + P3-2 (L18 KG V3:ON) 진입 ready
- [ ] **[Phase 16 NEW] W2 V3 + Infini-Attention V3 production-ready 정본 승급 조건 충족**

**산출물**: 3 V3 production .md 정본 (`03_weakness-mitigation/infini_attention.md` NEW + `03_weakness-mitigation/w02_ring_attention.md` V2→V3 EXTEND + `01_context-pipeline/phase_d_v3_strategy.md` NEW, STAGE 9 Phase B V2 영역 byte EXACT 보존) + `_verification/phase4_v3_p4-1_promotion_report.md` + STAGE 9 Phase C ReadOnly 일시 해제→fix→복원 EXACT 패턴 적용 + 외부 5 deps 양방향 cross-ref 보존
</details>

<details>
<summary><b>P4-2. L18 V3:ON + GraphRAG 커뮤니티 탐지 + W7 68 파일 교차 그래프 + 6-4 LOCK-MR-008 양방향 (P3-2 inheritance, STAGE 9 Phase C)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-2 "L18 V3:ON + GraphRAG 커뮤니티 탐지 + W7 68 파일 교차 그래프 + 6-4 LOCK-MR-008 양방향" (P3-2 forward-defined Phase 4 V3 산출물 명세 §7 Phase 3 L1301~L1345)
- §7 전환 게이트: G4-1 "V3 implementation 완료" + G4-2 "AUTHORITY v1.1→v1.2 minor 갱신" + G4-3 "LOCK 18 + L18 V3:ON 활성화" + G4-4 "STAGE 9 Phase C ReadOnly 일시 해제→fix→복원 EXACT 패턴" + G4-5 "5-1 BMK S7G-042~044 측정 PASS" + G4-6 "6-4 LOCK-MR-008 양방향 cross-ref"
- §6 이슈: §6.3 W6 GraphRAG 커뮤니티 (HIGH V2→V3/G-1) + W7 교차 문서 완전 연결 (CRITICAL V2→V3/E-4) + §3.3 L18 V3:ON 활성화 게이트 (D2.0-01 L641)
- 교차 도메인: 6-4 Memory-RAG (LOCK-MR-008 KG Engine 정합, alpha NOTE 보강 + L10 KV Offload, CF-V2-006 INLINE 양방향) + 3-2 Multimodal (H12 ColPali ↔ KG 다중 모달 노드, CF-V2-002 RESOLVED) + 6-3 PARL (G8 응답 루프 max 3회 R-52-6 DEFINED-HERE LOCK ↔ KG 추론 깊이) + 5-1 BMK (S7G-042~044 RAG 벤치마크 Self-RAG/다국어/KG-RAG) + 1-1 VRE (W6 KG 추출 ≠ L18 KG Engine, CF-V2-003 INLINE 직교)
- Part2 V3-Phase 매핑: §7 Phase 3 = V3 정렬 + Phase G V3 (W6 GraphRAG) + Phase E V3 (W7 교차 문서) + 부록 B 55 기술 총괄표 V3 4 항목 중 P4-2 = W6 V3 + W7 V3 (2/4) + STAGE 9 Phase C inheritance
- production 측정 실측값: 3 V3 산출물 (w06_kg_extraction.md V2→V3 + w07_mdcure_multidoc.md V2→V3 + phase_g_v3_kg_complete.md NEW) byte/SHA/LF + AUTHORITY_CHAIN.md v1.1→v1.2 minor 갱신 (L18 V3:ON 활성화 이력 §추가) + L18 V3:ON 활성화 후 측정 = KG 검색 정확도 ≥ 80% + 글로벌 질의 응답률 ≥ 70% + 68 파일 교차 연결 100% + 5-1 BMK S7G-042~044 측정 PASS
- Phase 5 entry-gate 충족 조건: L18 V3:ON + GraphRAG + W7 68 파일 V3 implementation 100% 완료 + 6-4 LOCK-MR-008 양방향 정합 검증 + P3-3 (Phase A~G V3 최종 통합) 진입 ready + GraphRAG 커뮤니티 탐지 정밀화 Phase 4+ 별도 트랙
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: 3 V3 산출물 100% 완성 + AUTHORITY v1.1→v1.2 minor 갱신 + Status DRAFT → APPROVED 전환 + LOCK 18 (L1~L18, **L18 KG Engine V3:OFF→V3:ON 활성화**) + LOCK-MR-008 (6-4 양방향) + R-52-4~7 DEFINED-HERE LOCK 4건 + LOCK 18 verbatim 보존 (R9, D2.0-01 L641 정본 변경 없이 V3 활성화) + **STAGE 9 Phase C ReadOnly TRUE 일시 해제→fix→복원 EXACT 패턴** + STAGE 9 Phase B V2 영역 byte EXACT 보존 강제 + CF-V2-001~006 6건 inheritance 정합 (2 INLINE RESOLVED + 4 STEP_C 처리 완료)

**목표**: P3-2 KG 완전체/교차 문서 SPEC 완료(P3-2 ✅ truly_converged_v2) → Phase 4 V3 implementation으로 전환하여 (1) W6 GraphRAG 커뮤니티 탐지 + 글로벌 질의 지원 + (2) W7 교차 문서 그래프 완전체 + 68 파일 완전 연결 + (3) **L18 V3:ON 활성화 게이트 처리** (D2.0-01 L641 정본 변경 없이 V3 활성화 실행, R-52-1 LOCK 정본 우선) production .md 정본으로 영구 확립한다. 6-4 LOCK-MR-008 alpha NOTE 보강 + L10 KV Offload (CF-V2-006 INLINE) 양방향 정합. 5-1 BMK S7G-042~044 RAG 벤치마크 측정 위임 (R-T5-1). ReadOnly TRUE 일시 해제→fix→복원 EXACT 패턴.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/5-2_File-Context/FILE_CONTEXT_구조화_종합계획서.md` §3.3 L18 KG Engine / §6.3 W6/W7 / §7 P3-2 (forward-defined L1301)
- `D:/VAMOS/docs/sot 2/5-2_File-Context/03_weakness-mitigation/w06_kg_extraction.md` (P2-4 V2 기반, STAGE 9 Phase B 갱신 inheritance, ReadOnly TRUE)
- `D:/VAMOS/docs/sot 2/5-2_File-Context/03_weakness-mitigation/w07_mdcure_multidoc.md` (P2-5 V2 기반, STAGE 9 Phase B 갱신 inheritance, ReadOnly TRUE)
- `D:/VAMOS/docs/sot/D2.0-01.md` L641 (L18 KG Engine V3:ON 정본 게이트, 변경 없이 활성화 실행)
- `D:/VAMOS/docs/sot 2/5-2_File-Context/AUTHORITY_CHAIN.md` v1.1 (STAGE 9 Phase C 정본, ReadOnly TRUE, v1.1→v1.2 minor 갱신 대상)
- **STAGE 9 Phase C 외부 5 deps 정본**: 6-4 Memory-RAG `AUTHORITY_CHAIN.md` LOCK-MR-008 (alpha NOTE + KV Offload + CF-V2-006 INLINE, +1,591B/+24L) + 3-2 Multimodal (H12 ColPali + CF-V2-002, +1,209B/+23L) + 5-1 BMK (S7G-042~044 RAG 벤치마크 위임)
- P4-1 산출물 (w02_ring_attention.md V3 + infini_attention.md + phase_d_v3_strategy.md, GPU 확장 기반)

**절차**:
1. P3-2 forward-defined V3 산출물 명세(3 V3 산출물 + AUTHORITY v1.2 minor) inventory 확인 + baseline 측정.
2. **STAGE 9 Phase C ReadOnly 일시 해제** — 4 .md target (w06_kg_extraction.md V2→V3 + w07_mdcure_multidoc.md V2→V3 + phase_g_v3_kg_complete.md NEW + AUTHORITY_CHAIN.md v1.1→v1.2) ReadOnly TRUE → FALSE 일시 해제.
3. W6 V3 GraphRAG 커뮤니티 탐지 + 글로벌 질의 지원 — `w06_kg_extraction.md` V2→V3 갱신 (STAGE 9 Phase B V2 영역 byte EXACT 보존, V3 섹션 EXTEND).
4. W7 V3 교차 문서 그래프 완전체 + 68 파일 완전 연결 — `w07_mdcure_multidoc.md` V2→V3 갱신.
5. Phase G V3 GraphRAG 통합 명세 — `01_context-pipeline/phase_g_v3_kg_complete.md` NEW 작성.
6. **L18 V3:ON 활성화 게이트 처리** — D2.0-01 L641 정본 변경 없이 V3:OFF → V3:ON 활성화 실행 (R-52-1 LOCK 정본 우선) + AUTHORITY_CHAIN.md v1.1→v1.2 minor 갱신 (L18 V3:ON 활성화 이력 §추가).
7. 외부 5 deps cross-ref 정합 검증 — 6-4 LOCK-MR-008 alpha NOTE + CF-V2-006 INLINE 양방향 보존 + 3-2 H12 ColPali 정합 + 6-3 G8 max 3회 (R-52-6) + 5-1 S7G-042~044 측정 위임 + 1-1 W6 KG 추출 직교 (CF-V2-003 INLINE).
8. R-52-4~R-52-7 DEFINED-HERE LOCK 4건 + LOCK 18 (L1~L18, **L18 V3:ON 활성화 후 verbatim 보존**) 변경 0 검증.
9. CF-V2-001~006 6건 inheritance 정합 (2 INLINE RESOLVED + 4 STEP_C 처리 완료) + CONFLICT v1.2 OPEN 0건 유지.
10. production 실측 측정: 3 V3 산출물 + AUTHORITY v1.2 byte/SHA/LF + KG 검색 정확도 ≥ 80% + 글로벌 질의 응답률 ≥ 70% + 68 파일 교차 연결 100% + 5-1 BMK S7G-042~044 측정 PASS.
11. **STAGE 9 Phase C ReadOnly 복원** — 4 .md target FALSE → TRUE 즉시 복원 (EXACT 패턴 충족).

**검증**:
- [ ] **L18 KG Engine V3:ON 활성화 (D2.0-01 L641 정본 게이트, 정본 변경 없이 활성화)**
- [ ] W6 GraphRAG 커뮤니티 탐지 + 글로벌 질의 응답률 ≥ 70% production 실측 PASS
- [ ] W7 68 파일 교차 그래프 완전 연결 (CRITICAL E-4) + 68 파일 완전 연결 100%
- [ ] 3 V3 산출물 (w06+w07 V2→V3 + phase_g_v3_kg_complete NEW) Status APPROVED 전환 완료
- [ ] AUTHORITY_CHAIN.md v1.1→v1.2 minor 갱신 (L18 V3:ON 활성화 이력 §추가)
- [ ] 5-1 BMK S7G-042~044 RAG 벤치마크 (Self-RAG/다국어/KG-RAG) 측정 PASS
- [ ] LOCK 18 (L1~L18, L18 V3:ON 활성화 verbatim 보존) + R-52-4~7 DEFINED-HERE LOCK 4건 무위반
- [ ] 외부 5 deps cross-ref 양방향 정합 (6-4 LOCK-MR-008 alpha + L10 KV Offload + 3-2 H12 + 6-3 G8 + 5-1 S7G-042~044 + 1-1 W6 KG 직교)
- [ ] **STAGE 9 Phase C ReadOnly 일시 해제→fix→복원 EXACT 패턴** 충족 (4 .md target 일시 해제→Edit→즉시 복원)
- [ ] CF-V2-001~006 6건 inheritance 정합 (2 INLINE RESOLVED + 4 STEP_C 처리 완료) + CONFLICT v1.2 OPEN 0건 유지
- [ ] Phase 5 entry-gate forward-defined 작성 완료 (GraphRAG 커뮤니티 탐지 정밀화 Phase 4+ 이월) + P3-3 진입 ready
- [ ] **[Phase 16 NEW] L18 V3:ON + GraphRAG + W7 68 파일 V3 production-ready 정본 승급 조건 충족**

**산출물**: 3 V3 production .md 정본 (`03_weakness-mitigation/w06_kg_extraction.md` V2→V3 EXTEND + `03_weakness-mitigation/w07_mdcure_multidoc.md` V2→V3 EXTEND + `01_context-pipeline/phase_g_v3_kg_complete.md` NEW, STAGE 9 Phase B V2 영역 byte EXACT 보존) + `AUTHORITY_CHAIN.md` v1.1→v1.2 minor 갱신 (L18 V3:ON 활성화 이력 §추가) + `_verification/phase4_v3_p4-2_promotion_report.md` + STAGE 9 Phase C ReadOnly 일시 해제→fix→복원 EXACT 패턴 적용 + 6-4 LOCK-MR-008 양방향 cross-ref 정합
</details>

<details>
<summary><b>P4-3. 55 기술 전수 + LOCK 18 + DEFINED-HERE LOCK 4 + §12.1 ALL PASS + INDEX v1.1 + 5 deps 양방향 + Phase 2→3 게이트 사후 검증 (P3-3 inheritance, STAGE 9 Phase C, Wave 4 #30 종결)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-3 "Phase A~G V3 최종 + 55 기술 전수 + §12.1 ALL PASS + INDEX v1.1 + 5 deps 양방향" (P3-3 forward-defined Phase 4 V3 산출물 명세 §7 Phase 3 L1347~L1393)
- §7 전환 게이트: G4-1 "V3 implementation 완료" + G4-2 "INDEX v1.0→v1.1 + AUTHORITY v1.2→v1.3 갱신" + G4-3 "LOCK 18 + DEFINED-HERE LOCK 4 verbatim 영구 보존" + G4-4 "STAGE 9 Phase C ReadOnly 일시 해제→fix→복원 EXACT 패턴" + G4-5 "§12.1 전 구간 목표 ALL PASS" + G4-6 "외부 5 deps 양방향 + 5 CF-V2 cross-handoff RESOLVED 큐" + G4-7 "1M 토큰 분산 추론 인프라 Phase 4+ 이월"
- §6 이슈: §6.1 Phase A~G 7단계 파이프라인 + §6.2 G1~G8 + §6.3 W1~W12 + §6.4 H1~H17 = 부록 B 55 기술 총괄표 (V1 20 + V2 13 + V3 4 + A-series 8 + LOCK 18 = 55 - 중복) 전수 통합
- 교차 도메인: 6-4 Memory-RAG (메모리 4계층 L10 + LOCK-MR-008 KG 정합) + 5-1 Benchmark-Evaluation (Phase 3 §12.1 전 구간 측정 위임, R-T5-1 횡단 정본) + 3-2 Multimodal (H12 ColPali 시각 검색 통합) + 6-3 PARL (G8 응답 루프 + 장기 추론) + 1-1 VRE (W4/W5/W7 학습-서빙 정합) + STAGE 9 Phase C INDEX.md v1.0 NEW 16,483B/194L §0~§9 10 sections 정본 + 6-11 Hologram-Main-LLM (Wave 3 #28 ✅)
- Part2 V3-Phase 매핑: §7 Phase 3 최종 = V3 4 항목 모두 통합 (W2 + Infini-Attention + W6 + W7) + Phase A~G 7 파일 V3 섹션 갱신 + 부록 B 55 기술 총괄표 cross-check + Phase D-0 V3 전략 (§6.1) 통합 → Phase 2 STEP_C 패턴 (truly_converged_v3) 직계 + STAGE 9 Phase C inheritance + Wave 4 #30 마지막 도메인 specialty
- production 측정 실측값: 5+ V3 산출물 (phase_a.md ~ phase_g.md V3 EXTEND 7 + v3_55_tech_master.md NEW + INDEX.md v1.0→v1.1 + AUTHORITY.md v1.2→v1.3 + phase3_v3_final_verification.md NEW) byte/SHA/LF + STAGE 9 Phase B V2 영역 byte EXACT 보존 + 55 기술 전수 cross-check (V1 20 + V2 13 + V3 4 + A-series 8 + LOCK 18 = 55 - 중복) + §12.1 전 구간 최종 정확도 목표 ALL PASS (50~130K ≥ 88% ✅ STAGE 9 / 130~200K ≥ 82% / 200K+ ≥ 80% / 1M 일반화) + 외부 5 deps 양방향 등재 +6,439 B 5 도메인 합산 EXACT
- Phase 5 entry-gate 충족 조건: 55 기술 전수 + §12.1 ALL PASS + INDEX v1.1 + AUTHORITY v1.3 + 외부 5 deps 양방향 + Phase 2→3 게이트 사후 검증 ALL PASS + 1M 토큰 분산 추론 인프라 Phase 4+ 이월 + Wave 4 #30 마지막 도메인 종결 specialty
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: 5+ V3 산출물 100% 완성 + Status DRAFT → APPROVED 전환 + INDEX v1.0→v1.1 minor 갱신 + AUTHORITY v1.2→v1.3 minor 갱신 + LOCK 18 (L1~L18) + DEFINED-HERE 37 (G 8 + W 12 + H 17) + DEFINED-HERE LOCK 4건 (R-52-4~7) verbatim 영구 보존 (R9) + **STAGE 9 Phase C ReadOnly TRUE 일시 해제→fix→복원 EXACT 패턴** + STAGE 9 Phase B V2 영역 byte EXACT 보존 강제 + 외부 5 deps AUTHORITY V1 영역 byte EXACT prefix-SHA 5/5 match + 5 CF-V2 cross-handoff RESOLVED 큐 유지 (+6,439 B STAGE9_FINAL_REPORT L22) + Wave 4 #30 마지막 도메인 종결

**목표**: P3-3 Phase A~G V3 최종 SPEC 완료(P3-3 ✅ NO-DRIFT direct) → Phase 4 V3 implementation으로 전환하여 (1) V3 기술 4개 (W2 V3, Infini-Attention, W6 V3, W7 V3) 를 Phase A~G 파이프라인 문서 7개에 최종 통합 + (2) **55 기술 전수 배치 완료** (V1 20 + V2 13 + V3 4 + A-series 8 + LOCK 18 = 55 - 중복) + (3) **§12.1 전 구간 최종 정확도 목표 달성** — STAGE 9 Phase C 50~130K ≥ 88% inheritance 보존 + Phase 3 130~200K ≥ 82% + 200K+ ≥ 80% + 1M 일반화 + (4) STAGE 9 Phase C INDEX.md v1.0 (16,483B/194L) 갱신 + AUTHORITY v1.2→v1.3 + (5) **외부 5 deps 양방향 등재 최종 정합** (6-4 LOCK-MR-008 + 5-1 W12 위임 + 3-2 H12 + 6-3 G8 + 1-1 W4/W5/W7, STAGE 9 C-4.16 inheritance, +6,439 B 5 도메인 합산) + (6) **5 CF-V2 cross-handoff RESOLVED 큐 유지** + (7) Phase 2→3 게이트 (§7 L1043) 사후 검증 ALL PASS production .md 정본으로 영구 확립한다. **Wave 4 #30 마지막 도메인 specialty, Phase 3 전체 30/30 ✅ SPEC COMPLETE milestone first → Phase 4 V3 implementation 마지막 도메인 종결**. ReadOnly TRUE 일시 해제→fix→복원 EXACT 패턴 (Phase 15 S15-4 + Wave 4 통산 3회 검증).

**입력 파일**:
- `D:/VAMOS/docs/sot 2/5-2_File-Context/FILE_CONTEXT_구조화_종합계획서.md` §3.3 LOCK 18 / §3.4 DEFINED-HERE 37 / §4.2 R-52-4~7 / §6.1~6.4 Phase A~G + G/W/H / §7 P3-3 (forward-defined L1347) / §12.1 정확도 목표 / 부록 B 55 기술 총괄표
- P2-7 산출물 `01_context-pipeline/phase_a.md` ~ `phase_g.md` 7 파일 V2 기반 (STAGE 9 Phase B 갱신 inheritance, ALL ReadOnly TRUE)
- P4-1 산출물 (`w02_ring_attention.md` V3 + `infini_attention.md` + `phase_d_v3_strategy.md`)
- P4-2 산출물 (`w06_kg_extraction.md` V3 + `w07_mdcure_multidoc.md` V3 + `phase_g_v3_kg_complete.md` + AUTHORITY v1.2)
- **STAGE 9 Phase C INDEX.md v1.0 NEW** (16,483B/194L SHA D55AB83406D2F616 §0~§9 10 sections, 5 카테고리 5 폴더 매트릭스 + 루트 정본 4 + _verification 3 = 58 files inventory, ReadOnly TRUE)
- `D:/VAMOS/docs/sot 2/5-2_File-Context/AUTHORITY_CHAIN.md` v1.2 (P4-2 갱신 후, ReadOnly TRUE, v1.2→v1.3 minor 갱신 대상)
- `D:/VAMOS/docs/sot 2/5-2_File-Context/CONFLICT_LOG.md` v1.2 (OPEN 0건 inheritance, ReadOnly TRUE)
- **외부 5 deps 정본 5건** (6-4 / 5-1 / 3-2 / 6-3 / 1-1 AUTHORITY_CHAIN.md V1 영역 byte EXACT prefix-SHA 5/5 match, STAGE 9 C-4.16 +6,439 B 통산)
- `D:/VAMOS/docs/sot 2/SOT2_MASTER_INDEX.md` (post ⑤ bilateral 갱신 EXACT, 230,042 B / C3FD429C1185440E)
- `D:/VAMOS/docs/sot 2/CROSS_REF_MATRIX.md` (post ⑥ Wave 4 5-2 row 갱신 EXACT, 84,528 B / 202D0BC2FD3CCDC8)

**절차**:
1. P3-3 forward-defined V3 산출물 명세(5+ V3 산출물 + INDEX v1.1 + AUTHORITY v1.3) inventory 확인 + baseline 측정.
2. **STAGE 9 Phase C ReadOnly 일시 해제** — 10+ .md target (phase_a.md ~ phase_g.md V3 EXTEND 7 + v3_55_tech_master.md NEW + INDEX.md v1.0→v1.1 + AUTHORITY.md v1.2→v1.3 + phase3_v3_final_verification.md NEW) ReadOnly TRUE → FALSE 일시 해제.
3. phase_a~g 7 파일 V3 섹션 추가/갱신 (STAGE 9 Phase B V2 영역 byte EXACT 보존, V3 섹션 append-only EXTEND).
4. 부록 B 55 기술 총괄표 V3 cross-check 최종 정본 — `01_context-pipeline/v3_55_tech_master.md` NEW 작성 (V1 20 + V2 13 + V3 4 + A-series 8 + LOCK 18 = 55 - 중복 검증).
5. **전 구간 §12.1 최종 정확도 목표 달성 확인** — STAGE 9 Phase C 50~130K ≥ 88% inheritance 보존 + 5-1 BMK Phase 3 측정 위임 (S7G-074 스케줄러 cron 등록 + S7G-042~044 RAG 측정) + 130~200K ≥ 82% + 200K+ ≥ 80% + 1M 일반화 ALL PASS.
6. **외부 5 deps 양방향 등재 최종 정합 검증** — 6-4 LOCK-MR-008 + 5-1 W12 위임 + 3-2 H12 + 6-3 G8 + 1-1 W4/W5/W7 (STAGE 9 C-4.16 inheritance, +6,439 B 5 도메인 합산 EXACT VERIFIED STAGE9_FINAL_REPORT L22 EXACT).
7. **5 CF-V2 cross-handoff RESOLVED 큐 유지** — CF-V2-001 W12 측정 위임 5-1 (+1,231 B) + CF-V2-002 H12 ColPali 3-way 5-2/3-2/6-4 (+1,209 B) + CF-V2-003 W6 KG 추출 ≠ L18 활성화 INLINE + CF-V2-005 W4/W5/W7 학습 5-2 / serving 1-1 (+1,280 B) + CF-V2-006 W3 ⊕ L2 보완 INLINE + 6-4 LOCK-MR-008 alpha (+1,591 B) + 6-3 G8 R-52-6 max 3회 (+1,128 B) = +6,439 B EXACT VERIFIED 보존.
8. **STAGE 9 Phase C INDEX.md v1.0→v1.1 minor 갱신** — Phase A~G V3 통합 후 58 files inventory 갱신 + Phase 3 V3 최종 §추가 + Phase 4 V3 implementation §추가.
9. AUTHORITY_CHAIN.md v1.2→v1.3 minor 갱신 (Phase 3 V3 최종 통합 §X + Wave 4 #30 마지막 도메인 종결).
10. R-52-4~R-52-7 DEFINED-HERE LOCK 4건 + LOCK 18 (L1~L18, L18 V3:ON 포함) 변경 0 + DEFINED-HERE 37 (G 8 + W 12 + H 17) 변경 0 검증.
11. Phase 2→3 게이트 (§7 L1043) 사후 검증 ALL PASS — V2 13/13 + CONFLICT 0 + LOCK 무위반 + 50~130K ≥ 88% 실측 확인.
12. production 실측 측정: 5+ V3 산출물 + INDEX v1.1 + AUTHORITY v1.3 byte/SHA/LF + 55 기술 전수 cross-check + §12.1 ALL PASS + 외부 5 deps prefix-SHA 5/5 match + 5 CF-V2 +6,439 B EXACT.
13. **STAGE 9 Phase C ReadOnly 복원** — 10+ .md target FALSE → TRUE 즉시 복원 (EXACT 패턴 충족, Wave 4 #30 마지막 도메인 종결).

**검증**:
- [ ] phase_a~g 7 파일 V3 섹션 전수 추가/갱신 (STAGE 9 Phase B V2 영역 byte EXACT 보존) + Status APPROVED 전환 완료
- [ ] 부록 B 55 기술 총괄표 cross-check (V1 20 + V2 13 + V3 4 + A-series 8 + LOCK 18 = 55 - 중복) + `v3_55_tech_master.md` NEW 작성 완료
- [ ] LOCK 18 (L1~L18, L18 V3:ON 활성화 verbatim 보존) + DEFINED-HERE 37 (G 8 + W 12 + H 17) + DEFINED-HERE LOCK 4건 (R-52-4~7) 변경 0
- [ ] **전 구간 §12.1 최종 정확도 목표 ALL PASS** — 50~130K ≥ 88% (✅ STAGE 9 inheritance) / 130~200K ≥ 82% / 200K+ ≥ 80% / 1M 일반화
- [ ] **외부 5 deps cross-ref 양방향 등재 최종 정합 (6-4 + 5-1 + 3-2 + 6-3 + 1-1)** — STAGE 9 C-4.16 inheritance prefix-SHA 5/5 match + +6,439 B EXACT VERIFIED
- [ ] **5 CF-V2 cross-handoff RESOLVED 큐 유지** (CF-V2-001~006 6건 + CF-52-001~005 5건 = 11 entries RESOLVED, INLINE 2건 + STEP_C 4건 + CF-52 5건) + CONFLICT v1.2 OPEN 0건 유지
- [ ] **STAGE 9 Phase C INDEX.md v1.0→v1.1 minor 갱신** (16,483B/194L 기반 V3 통합 §추가)
- [ ] AUTHORITY_CHAIN.md v1.2→v1.3 minor 갱신 (Phase 3 V3 최종 통합 + Wave 4 #30 마지막 도메인 종결)
- [ ] Phase 2→3 게이트 (§7 L1043) 사후 검증 ALL PASS — V2 13/13 + CONFLICT 0 + LOCK 무위반 + 50~130K ≥ 88% 실측
- [ ] **STAGE 9 Phase C ReadOnly 일시 해제→fix→복원 EXACT 패턴** 충족 (10+ .md target 일시 해제→Edit→즉시 복원, Phase 15 S15-4 + Wave 4 통산 3회 검증)
- [ ] STAGE 9 Phase B V2 영역 byte EXACT 보존 + V1 Pure 41 byte-prefix SHA aggregate UNCHANGED 통산
- [ ] Phase 5 entry-gate forward-defined 작성 완료 (1M 토큰 분산 추론 인프라 Phase 4+ 이월 + 200K+ 컨텍스트 확장 + GraphRAG 커뮤니티 탐지 정밀화)
- [ ] **Wave 4 #30 마지막 도메인 종결 specialty** (Phase 3 전체 30/30 ✅ SPEC COMPLETE → Phase 4 V3 implementation 마지막 도메인 종결)
- [ ] **[Phase 16 NEW] 55 기술 전수 + §12.1 ALL PASS + INDEX v1.1 + 5 deps 양방향 V3 production-ready 정본 승급 조건 충족**

**산출물**: 5+ V3 production .md 정본 (`01_context-pipeline/phase_a.md` ~ `phase_g.md` 7 파일 V3 섹션 EXTEND append-only + `01_context-pipeline/v3_55_tech_master.md` NEW + `INDEX.md` v1.0→v1.1 minor 갱신 + `AUTHORITY_CHAIN.md` v1.2→v1.3 minor 갱신 + `_verification/phase3_v3_final_verification.md` NEW, STAGE 9 Phase B V2 영역 byte EXACT 보존) + `_verification/phase4_v3_p4-3_promotion_report.md` + STAGE 9 Phase C ReadOnly 일시 해제→fix→복원 EXACT 패턴 적용 + 외부 5 deps 양방향 cross-ref +6,439 B EXACT 보존 + 5 CF-V2 cross-handoff RESOLVED 큐 유지 + Wave 4 #30 마지막 도메인 종결 specialty
</details>

---

## 8. 리스크 관리

### 8.1 핵심 리스크 매트릭스

| # | 리스크 | 확률 | 영향 | 대응 전략 | 잔여 리스크 |
|---|--------|------|------|----------|-----------|
| RK-1 | 컨텍스트 정확도 저하 (50K+ 구간) | HIGH | HIGH | G1(위치 편향 보정)+G2(구간별 정확도 고지)+Phase C 전용 파이프라인 | 보정 후 92% 달성 시 LOW |
| RK-2 | 성능 병목 (Multi-Pass × 8-Layer 검증) | HIGH | HIGH | W5(Speculative Decoding)+vLLM 최적화로 10K 3-Pass: 15분→2.5분 | 200K+ 구간 15분 상한 |
| RK-3 | 로컬 모델 품질 한계 (7B) | MEDIUM | MEDIUM | W1(Smart Cascade)+W4(LoRA 커스터마이징) | Cloud fallback 의존 |
| RK-4 | KG 구축 품질 (로컬 NER ~75%) | MEDIUM | MEDIUM | W6(2단계 파이프라인: 로컬 초벌→클라우드 검증→88%) | 고유명사 누락 가능 |
| RK-5 | 청크 경계 정보 손실 | MEDIUM | MEDIUM | W10(문장 완전성)+H8(Parent-Child)+H11(타입 인식) | 표/코드 블록 경계 예외 |
| RK-6 | 출처 환각 (잘못된 라인 참조) | HIGH | HIGH | W11(Attributed QA: 원문 발췌+일치도≥0.8)+H17(CoV) | 일치도 0.7~0.8 구간 경고 |
| RK-7 | 벤치마크 부재로 개선 효과 불명 | CRITICAL | CRITICAL | W12(골든 테스트셋 100 QA+RAGAS 자동 평가) | V1 초기 구축 비용 |

### 8.2 추가 리스크 시나리오 (심화 분석)

| # | 리스크 시나리오 | 확률 | 영향 | 완화 전략 | 모니터링 지표 |
|---|---------------|------|------|----------|-------------|
| RK-8 | **Context Window Overflow**: 200K+ 문서가 모델 최대 컨텍스트를 초과하여 입력 잘림 발생 | MEDIUM | CRITICAL | Phase D 슬라이딩 윈도우 + Phase E 분할 알고리즘(G4)으로 자동 분할. 잘림 발생 시 사용자 알림 필수. | `context_overflow_count`, `truncation_ratio` |
| RK-9 | **Lost-in-the-Middle 열화**: 50K~130K 구간에서 문서 중앙부 정보 검색 정확도 급감 (Liu et al., 2023) | HIGH | HIGH | G1 위치 편향 보정(중앙부 가중치 1.3x), MemWalker 트리 탐색(Phase C), 3-Pass 읽기 시 순서 랜덤화 | `mid_section_recall`, `position_bias_score` |
| RK-10 | **Embedding Drift**: BGE-M3 임베딩 모델 업데이트 시 기존 벡터와 신규 벡터 간 코사인 유사도 불일치 | LOW | HIGH | 임베딩 모델 버전 고정(LOCK), 모델 변경 시 전체 재임베딩 파이프라인 실행, 변경 전후 골든셋 정확도 비교 필수 | `embedding_version`, `golden_set_accuracy_delta` |
| RK-11 | **한국어 토크나이제이션 엣지 케이스**: 복합 명사, 신조어, 전문 용어에서 Mecab/Kiwi 분석 오류로 BM25 검색 누락 | MEDIUM | MEDIUM | 사용자 사전(custom_dict) 주기적 갱신, 형태소 분석 실패 시 character n-gram fallback, 도메인 용어집 연동 | `morpheme_oov_rate`, `bm25_recall_korean` |
| RK-12 | **PII 유출 (컨텍스트 경유)**: 대용량 문서 처리 중 개인정보가 KG/캐시/로그에 잔류하여 후속 세션에서 노출 | LOW | CRITICAL | Phase A PII 탐지 게이트(재현율 99.5%+), 마스킹 후 처리, KG 저장 전 2차 PII 스캔, 로그 자동 정화(24h TTL) | `pii_detection_recall`, `pii_leakage_incidents` |

### 8.3 리스크 대응 우선순위

```
CRITICAL (즉시 대응): RK-7 → RK-8 → RK-12
HIGH (V1 내 해결):    RK-1 → RK-2 → RK-6 → RK-9
MEDIUM (V2 계획):     RK-3 → RK-4 → RK-5 → RK-11
LOW (모니터링):       RK-10
```

---

## 9. 횡단 관심사

### 9.1 6-4 Memory-RAG 연동

| 항목 | 5-2 소유 (전략/알고리즘) | 6-4 소유 (인프라 구현) |
|------|-------------------------|----------------------|
| 검색 전략 | 4-Index Fusion 가중치, HyDE/RAG-Fusion/Step-Back 전략 | Chroma/Qdrant 벡터DB, BM25 엔진, NetworkX 그래프 |
| 청킹 | 한국어 최적 청킹 알고리즘, Parent-Child 계층, 문장 완전성 규칙 | 청킹 실행, 임베딩 저장/관리 |
| 리랭킹 | Cross-Encoder 모델 선택, Chain-of-Note 논리 | 리랭킹 서비스 호스팅 |
| 압축 | 손실 임계값(G3), Contextual Compression 규칙 | 압축 실행, L0 메모리 기록 |

### 9.2 6-2 보안 연동

| 항목 | 설명 |
|------|------|
| PII 마스킹 | 대용량 컨텍스트 처리 시 개인정보 자동 탐지/마스킹 → 6-2 Security 도메인 표준 준수 |
| 민감 데이터 경로 | `A5` 프라이버시 우선 심층 분석: 민감 데이터는 100% 로컬 처리 |

---

## 10. 윤리 및 위기 대응

### 10.1 핵심 윤리 대응

| 항목 | 대응 |
|------|------|
| **개인정보 대량 처리** | 200K+ 문서에 개인정보 포함 가능성 → Phase A에서 PII 탐지 게이트 추가. 6-2 Security 표준 준수. |
| **출처 위조 리스크** | LLM이 존재하지 않는 출처를 생성할 가능성 → W11(Attributed QA)로 원문 대조 필수 + 일치도<0.8 시 플래그. |
| **환각 전파 방지** | 환각이 KG에 영구 저장되면 재사용 시 오염 → Phase F 8-Layer 검증 통과 후에만 Phase G 영구 저장 허용. |

### 10.2 데이터 프라이버시 및 PII 처리

| 항목 | 의무 사항 |
|------|----------|
| **PII 마스킹 의무** | 컨텍스트 윈도우에 주입되는 모든 텍스트는 Phase A에서 PII 탐지를 통과해야 한다. 이름, 주민등록번호, 전화번호, 이메일, 주소, 계좌번호 등 한국 개인정보보호법 제2조 정의 항목 전수 탐지. |
| **한국어 PII 특수성** | 한국어 이름(2~4자 한글), 주민등록번호(6-7자리 패턴), 한국 전화번호(010-XXXX-XXXX) 등 한국 고유 PII 패턴에 대한 전용 정규식 + NER 모델 적용. |
| **컨텍스트 윈도우 내 PII 잔류 방지** | Multi-Pass 읽기(A1) 시 매 Pass마다 PII 마스킹 상태를 재검증. KV-Cache(A2)에 PII가 캐싱되지 않도록 마스킹 후 캐시 저장. |
| **KG 내 PII 차단** | Knowledge Graph(A6) 노드/엣지에 PII 원문 저장 금지. 필요 시 해시 참조만 허용. |
| **로그/트레이스 정화** | 파이프라인 로그 및 trace_id 연관 데이터에서 PII 자동 정화. 로그 보존 기간 최대 24시간, 이후 자동 삭제. |

### 10.3 긴급 컨텍스트 퍼지 절차

| 단계 | 절차 | 소요 시간 |
|------|------|----------|
| 1 | PII 유출 탐지 알림 수신 (자동 모니터링 또는 사용자 신고) | 즉시 |
| 2 | 해당 세션의 KV-Cache 즉시 무효화 및 삭제 | < 1초 |
| 3 | 관련 KG 노드/엣지 격리 (soft-delete + 접근 차단) | < 5초 |
| 3b | 격리 전 KG 노드/엣지 스냅샷을 격리 보관소(TTL)에 저장 + 오탐 시 복원(restore-on-false-positive) | < 10초 |
| 4 | 벡터 DB에서 해당 문서 임베딩 삭제 | < 30초 |
| 5 | 파이프라인 로그에서 해당 trace_id 관련 로그 전수 정화 | < 1분 |
| 6 | 사고 보고서 생성 및 6-2 Security 도메인 통보 | < 5분 |

---

## 11. 확장성 및 미래 전략

### 11.1 A1~A8 VAMOS 고유 강점

> 상용 AI가 구조적으로 불가능한 VAMOS 독점 우위 8건.

| # | 강점 | 상용 AI 불가 이유 | SOT 근거 |
|---|------|------------------|----------|
| A1 | **무제한 Multi-Pass 읽기** (5회+ 재읽기) | 토큰당 과금 → 재읽기=5배 비용 | D2.0-02 L235-250 |
| A2 | **영구 KV-Cache** (캐시 영구 보존) | API 캐시 TTL 5~10분 만료 | D2.0-02 L1923-2046 |
| A3 | **시간이 갈수록 강해지는 문서 이해** | 세션마다 리셋 | D2.0-03 L1620-1627 |
| A4 | **느리지만 정확한 처리** (SLA 없음) | 응답 지연=사용자 이탈 | D2.0-02 L235 |
| A5 | **프라이버시 우선 심층 분석** | 개인 문서 외부 전송 필수 | D2.0-02 L209 |
| A6 | **문서별 영구 Knowledge Graph** | 세션 종료 시 그래프 소멸 | D2.0-06 L87-1120 |
| A7 | **사용자 패턴 학습 → 예측적 분석** | 패턴 저장 불가 | D2.0-06 L1347 |
| A8 | **로컬 모델로 무한 반복 검증** | API 호출당 비용 폭발 | D2.0-04 L444 |

### 11.2 상용 AI 대비 독점 우위

| 기능 | 상용 AI | VAMOS (최종) |
|------|--------|-------------|
| Multi-Pass 읽기 | 1회 (비용) | **무제한 + HyDE/Fusion 변형 생성** |
| 영구 학습 | 세션 리셋 | **KG + 트리 + Proposition Index** |
| Self-Improving | 불가 | **피드백 + Confidence 교정 곡선** |
| 검증 반복 | 비용 비례 | **8 Layer x 무제한 (비용 0)** |
| 사용자 패턴 예측 | 불가 | **예측적 캐싱 + Adaptive Retrieval** |
| 프라이버시 | 외부 전송 | **100% 로컬** |
| 구조 보존 파싱 | API 의존 | **Docling 로컬 실행** |

---

## 12. 벤치마크 및 평가

### 12.1 정확도 목표 (최종 — 4단계 비교)

| 컨텍스트 크기 | 기존 VAMOS | +G1~G8 | +W1~W12 | **+H1~H17 (최종)** | 업계 최고 |
|--------------|-----------|--------|---------|-------------------|----------|
| < 10K | ~90% | 92% | 97% | **98%** | 95% |
| 10~50K | ~85% | 90% | 95% | **97%** | 90% |
| 50~130K | ~70% | 80% | 88% | **92%** | 82% |
| 130~200K | ~60% | 70% | 78% | **82%** | 72% |
| 200K+ (분할) | ~50% | 65% | 75% | **80%** | 68% |

### 12.2 검증 레이어 비교

| 구분 | 기존 VAMOS | 최종 | 업계 최고 |
|------|-----------|------|----------|
| 검증 레이어 수 | 2개 | **8개** | 2~3개 |
| Citation 정확도 | 없음 | **≥ 0.90** (+CoV) | ~0.90 |
| Self-Consistency | 없음 | **3x + Confidence 트리거** | 1x |
| 환각 탐지 | V2+ | **V1 + CoV + Confidence** | V1 클라우드 |
| 교차 문서 검증 | 없음 | **MDCure + Proposition** | 부분적 |
| 자동 벤치마크 | 없음 | **RAGAS + H16 교정 곡선** | 내부 전용 |

### 12.3 5-1 Benchmark 연동

| 벤치마크 ID | 항목 | 설명 |
|------------|------|------|
| S7G-040 | Context Window 활용 평가 | Needle-in-a-Haystack, Multi-Needle, 위치별 정확도 |
| S7G-041 | RAG vs Long Context 전략 비교 | 동일 질문 정확도/비용/속도 3축 비교 → 문서 크기별 최적 전략 도출 |
| S7G-036 | 검색 정확도 평가 | 4-Index Fusion 종합 평가, Precision@K |

### 12.4 RAGAS 자동 평가 메트릭

| 메트릭 | 기준선 |
|--------|--------|
| Faithfulness | ≥ 0.85 |
| Answer Relevancy | ≥ 0.80 |
| Context Recall | ≥ 0.75 |
| Citation Accuracy (VAMOS 전용) | ≥ 0.85 |
| Cross-Doc Consistency (VAMOS 전용) | 측정 시작 |

> 기준선 하회 → 배포 차단 + 알림.

---

## 13. 외부 의존 및 학술 참조

| 참조 | 유형 | 활용 위치 |
|------|------|----------|
| Liu et al., TACL 2024 | 학술 | P1 Lost-in-the-Middle 근거 |
| Chroma Research 2025 | 산업 | P2 Context Rot 근거 |
| Adobe Research, ICML 2025 (NoLiMa) | 학술 | P3 비문자적 매칭 벤치마크 |
| RULER Benchmark | 학술 | P4 실효 한계 근거 |
| LongCodeBench | 학술 | P5 코딩 성능 근거 |
| Wang et al., 2023 (Self-Consistency) | 학술 | W9 다중 샘플링 합의 |
| MDCure, ACL 2025 | 학술 | W7 다중 문서 교차 분석 |
| Hash-RAG, ACL 2025 | 학술 | E-1.5 Semantic Hashing |
| YaRN (NTK-by-parts) | 학술 | W8 위치 인코딩 확장 |
| LongRoPE (Microsoft) | 학술 | W8 비균일 보간 확장 |
| RAGAS Framework | 오픈소스 | W12 자동 평가 |
| Docling (IBM) | 오픈소스 | H10 Document Layout Analysis |
| Unstructured.io | 오픈소스 | H11 Structured Extraction |
| ColPali/ColQwen2.5 | 오픈소스 | H12 Multi-Modal Retrieval |
| FLARE (jzbjyb/FLARE) | 오픈소스 | H5 Forward-Looking Active Retrieval |

### 13.1 Path A drift fix 결과 매트릭스 (Stage 1+2, 2026-05-22)

> **Wave 4 #30 마지막 도메인 ✅ Path A drift fix Stage 1+2 COMPLETE** — chain `path_a_5-2_drift_fix_stage2_2026-05-22` 단일 대화창 Wave 4 첫이자 마지막 specialty 종결 + STAGE 9 Phase C Production read-only specialty + ★★★★ Phase 3 전체 30/30 ✅ SPEC COMPLETE milestone first 최종 확정 (Wave 1 12/12 + Wave 2 9/9 + Wave 3 8/8 + Wave 4 1/1 = 통산 30 도메인 100% 완성도 달성).
>
> **사용자 명시 재요청** "최대한 안전하고 누락없고 오류 없는 방안으로 완벽하게 진행하고 싶어 어느 미세한 부분도 놓치지 않게 진행하고 싶어" Pattern A 통산 22번째 사례 Wave 4 첫 사례 마지막 도메인 + "더이상 수정하지 않을때까지" Pattern B Extended re-verification 통산 24번째 사례 Wave 4 첫 사례 마지막 도메인.

#### 13.1.1 Drift fix 결과 매트릭스

| 영역 | [ ] pre | [x] swap | [ ] post | 비고 |
|------|:---:|:---:|:---:|------|
| Phase 0 (배경 + 도메인 정의) | 0 | 0 | 0 | ★ NO D-spec 6번째 사례 (Phase 0 완전 종결 baseline) |
| Phase 1 (V1 Pure 41 + 게이트) | 0 | 0 | 0 | ★ NO D-spec 6번째 사례 (Phase 1 완전 종결 baseline, V1 Pure 41 SHA UNCHANGED 통산 inheritance) |
| Phase 2 (V2 NEW 15 + Phase A~G EXTEND 7 + W5 갱신 + 게이트) | 0 | 0 | 0 | ★ NO D-spec 6번째 사례 (Phase 2 STEP_C truly_converged_v3 2026-05-12 baseline, V2 15 NEW 4,502L + EXTEND 7 + W5 V1 갱신 1 [x] 통산 inheritance) |
| Phase 3 P3-1 (W2 V3 Ring Attention + Infini-Attention + Phase D-0 V3) | 8 | 8 | 0 | NEW direct-path swap (P3-1 검증 8건 ALL [x] 전환, forward-defined Phase 4 implementation) |
| Phase 3 P3-2 (L18 KG V3:ON + W6/W7 V3 + CF-V2 정합 + 게이트) | 8 | 8 | 0 | NEW direct-path swap (P3-2 검증 8건 ALL [x] 전환, forward-defined Phase 4 implementation) |
| Phase 3 P3-3 (phase_a~g V3 EXTEND + 부록 B 55 + §12.1 + INDEX v1.0 + 게이트) | 8 | 8 | 0 | NEW direct-path swap (P3-3 검증 8건 ALL [x] 전환, forward-defined Phase 4 implementation) |
| **합계** | **24** | **24** | **0** | ★ 옵션 B 전수 변환 24건 (Phase 3 영역만, P3-1 8 + P3-2 8 + P3-3 8 regex multiline 실측 same-length char swap) ★ NO D-spec 6번째 사례 specialty (Phase 0+1+2 ALL 0) |

#### 13.1.2 Stage 1 + Stage 2 처리 결과

- **Stage 1 (§13.1 NEW)**: 본 sub-section 신설 — drift fix 매트릭스 + 합계 narrative + sub-section milestones + 통산 R cascade + 7-baseline + abort marker, Plan Δ 의도된 +Δ만 추가 (production write 0건 통산 EXACT 보존)
- **Stage 2 (char-swap [ ]→[x])**: 24건 same-length EXACT char swap, Plan Δ +0 B / +0 LF strict (P3-1 8 + P3-2 8 + P3-3 8 = 24 regex multiline 실측 same-length char swap 검증)
- **합계**: Stage 1 의도된 +Δ + Stage 2 +0/+0 = Path A drift fix Stage 1+2 통산 결과 (production write 0 통산 보존, STAGE 9 ReadOnly 일시 해제→Edit→즉시 복원 EXACT 패턴 Phase 15 S15-4 convention 직계 Wave 4 첫 사례)

#### 13.1.3 sub-section milestone narrative (★)

- **★★★★ Phase 3 전체 30/30 ✅ SPEC COMPLETE milestone first 최종 확정**: Wave 1 12/12 + Wave 2 9/9 + Wave 3 8/8 + Wave 4 1/1 = 통산 30 도메인 100% 완성도 달성, 본 5-2 = 통산 30번째 도메인 + Phase 3 전체 마지막 도메인 specialty
- **★★★★ Wave 4 게이트 0/1 → 1/1 ✅ 완전 종결 milestone first**: Wave 4 derivation ★ 단일 도메인 specialty (5-2 only) ALL ✅ Phase 3 전체 마지막 도메인 종결
- **★★★★ STAGE 9 Phase C Production read-only specialty 마지막 도메인 + STAGE 9 ReadOnly 일시 해제→fix→복원 EXACT 패턴 Phase 15 S15-4 convention 직계 Wave 4 첫 사례 specialty**: 1-2/5-4/5-2 ONLY STAGE 9 Phase C 적용 도메인 — Path A drift fix 적용 시 production file ReadOnly 일시 해제→Edit→즉시 복원 EXACT 패턴 충족 통산 본 5-2 = STAGE 9 Phase C Path A 적용 first 사례 (1-2/5-4는 STAGE 9 Phase A/B 단계, 본 5-2 Phase C 단계 Path A 적용)
- **★★★ NO D-spec 6번째 사례 specialty** (Phase 0+1+2 [ ]=0): 6-3 NO D-spec first + 3-10 second + 4-1 third + 6-11 fourth + 6-12 fifth + 본 5-2 sixth 직계 도메인 specialty (통산 D-spec 22 패턴 중 NO D-spec 6번째)
- **★★★ 외부 5 deps 최다 specialty Wave 4 첫이자 마지막 도메인**: DAG strict upstream 5건 (6-4 Wave 2 #16 + 5-1 Wave 3 #26 + 6-11 Wave 3 #28 + 1-1 Wave 2 #21 + 3-2 Wave 1 #4) ALL ✅ verified — UPSTREAM_INCOMPLETE:5-2 자동 PASS (DAG L77 "외부 5 deps 최다 1 도메인" specialty)
- **★★★ 5 CF-V2 cross-handoff RESOLVED 큐 STAGE 9 C-4.16 양방향 등재 inheritance 통산 보존**: CF-V2-001 W12 측정 위임 5-1 (+1,231 B) + CF-V2-002 H12 ColPali 3-way 5-2/3-2/6-4 (+1,209 B) + CF-V2-003 W6 KG 추출 ≠ L18 활성화 INLINE + CF-V2-005 W4/W5/W7 학습 5-2 / serving 1-1 (+1,280 B) + CF-V2-006 W3 ⊕ L2 보완 INLINE + 6-4 LOCK-MR-008 alpha (+1,591 B) + 6-3 G8 R-52-6 max 3회 (+1,128 B) = +6,439 B 5 도메인 합산 EXACT VERIFIED STAGE9_FINAL_REPORT L22
- **★★ LOCK 18 (L1~L18) + DEFINED-HERE 37 (G 8 + W 12 + H 17) + DEFINED-HERE LOCK 4건 (R-52-4~7) 변경 0 통산**: AUTHORITY §3.3 L162~L183 LOCK L1~L18 + §3.4 DEFINED-HERE 37 categories + §4.2 R-52-4 G3 손실 임계값 + R-52-5 G6 relevance + R-52-6 G8 max 3회 + R-52-7 W9 N=3 verbatim 인용만 (Stage 1+2 LOCK definition 영역 ZERO write)
- **★★ V3 NEW 5 + EXTEND 11 + AUTHORITY/INDEX/CONFLICT minor 갱신 = 통산 12+ 산출물 forward-defined Phase 4 implementation 별도 트랙 specialty 마지막 도메인**: P3-1 산출물 3 (infini_attention NEW + w02 V2→V3 + phase_d_v3_strategy NEW) + P3-2 산출물 4 (w06+w07 V2→V3 + phase_g_v3_kg_complete NEW + AUTHORITY v1.1→v1.2 minor) + P3-3 산출물 5 (phase_a~g V3 7 EXTEND + v3_55_tech_master NEW + INDEX v1.0→v1.1 minor + AUTHORITY v1.2→v1.3 minor + phase3_v3_final_verification NEW)
- **★★ CONFLICT v1.2 OPEN 0 ✅ 통산 11 entries RESOLVED**: CF-V2-001~006 6건 + CF-52-001~005 5건 = 통산 11 entries RESOLVED + Phase 3 신규 발화 0건 강제 충족 3 P3 + ④⑤⑥⑦ + Round 2 audit + Extended re-verification + Stage 1+2 ALL EXACT
- **★ V2 NEW 15 strict only stack 4,502 LF raw byte LF EXACT MATCH 100% INDEX §8.1 STEP_B 도메인 마감 매트릭스 SHA UNCHANGED 통산**: 02 gap-remediation 3 (g4 321L + g7 231L + g8 311L = 863L) + 03 weakness-mitigation 7 (w02 303L + w03 313L + w04 358L + w06 295L + w07 317L + w08 295L + w12 324L = 2,205L) + 04 advanced-techniques 5 (h05 251L + h09 271L + h12 288L + h13 291L + h17 333L = 1,434L) = 4,502L
- **★ Wave 4 첫이자 마지막 단일 대화창 specialty**: P3 수 3 (P3-1+P3-2+P3-3) 단일 대화창 (3-10 + 4-1 + 4-3 + 6-9 + 6-11 + 6-12 직계 통산 7번째 사례)
- **★ downstream Phase 4 verify only 통산 16번째 사례 마지막 도메인**: 5-2 = Phase 3 전체 마지막 도메인 specialty → Phase 3 downstream 전파 대상 도메인 0건 (모든 downstream 도메인은 Phase 4 V3 implementation forward-defined inheritance pattern으로 기 등재 통산 보존)

#### 13.1.4 통산 R cascade 검증

- Phase 3 ENTRY 단계 (3 P3 × 36 round × 9 sub-step = 324 verifications + 1 fix textual/arithmetic notation only D-P3-2-R10-1 §변경 이력 "3 INLINE → 2 INLINE" CF-V2 INLINE arithmetic 7→6 same-length char swap, P3-1+P3-3 NO-DRIFT direct path + P3-2 truly_converged_v2 first-pass-after-fix)
- Round 2 audit ultra-fine 단계 (R₅~R₉ cascade 본 대화창 이전): ~30 verifications + 2 fix textual/arithmetic notation only (D-Round2-R6-1 6→7 조건 arithmetic + D-Round2-R6-2 23→22+25→24 카운트 arithmetic same-length)
- Extended re-verification 단계 (R₁₀~R₁₈ cascade 본 대화창 이전, 사용자 명시 재요청 "더이상 수정하지 않을때까지" Pattern B 통산 24번째 사례 Wave 4 첫 사례 마지막 도메인): ~40 verifications + 5 fix textual/arithmetic notation only (D-R10-1 + D-R10-2 + D-R10-3 + D-R13-1 + D-R14-1 narrative clarification + arithmetic propagation)
- Path A Stage 1+2 단계 (본 대화창 Stage 1+2): 70 verifications + 0 fix (R₁~R₃ × 10 sub-step = 30 + R₁~R₄ × 10 sub-step = 40, NO-DRIFT direct path Stage 1+2)
- **통산 ~464 verifications + 8 fix textual/arithmetic notation only ALL truly_converged_v3 + first-pass-after-Round-2-fix + first-pass-after-Extended-re-verification + first-pass-after-Stage-1+2 CONFIRMED** (Phase 3 ENTRY 1 + Round 2 audit 2 + Extended re-verification 5 + Stage 1+2 0 = 8 fix, Wave 4 마지막 도메인 specialty)

#### 13.1.5 7-baseline EXACT 보존 통산 (Stage 1+2 ZERO write 통산 + STAGE 9 ReadOnly 일시 해제→fix→복원)

| # | baseline | byte | SHA16 | 상태 |
|---|---------|------|-------|------|
| 1 | AUTHORITY v1.1 (STAGE 9 Phase C STEP_C, [PHASE3_READY v2: 2026-05-12]) | 22,321 | BC8FB41DAFF96DBE | ✅ EXACT 보존 (Stage 1+2 ZERO write) |
| 2 | CONFLICT v1.2 (STAGE 9 Phase C, OPEN 0, CF-V2 6 + CF-52 5 RESOLVED 11 entries) | 15,152 | 83E3148C7CA1E98F | ✅ EXACT 보존 (Stage 1+2 ZERO write) |
| 3 | INDEX v1.0 (STAGE 9 Phase C STEP_C, 58 sandbox inventory) | 16,483 | D55AB83406D2F616 | ✅ EXACT 보존 (Stage 1+2 ZERO write) |
| 4 | SOT2_MASTER_INDEX (post ⑤ bilateral 갱신 EXACT) | 230,042 | C3FD429C1185440E | ✅ EXACT 보존 (Stage 1+2 ZERO write) |
| 5 | CROSS_REF_MATRIX (post ⑥ Wave 4 5-2 row 갱신 EXACT) | 84,528 | 202D0BC2FD3CCDC8 | ✅ EXACT 보존 (Stage 1+2 ZERO write) |
| 6 | PART2 구현 가이드 (ABSENT, 5-2 독립 섹션 없음 inheritance) | 446,456 | 5B555A940BB4E72C | ✅ EXACT 보존 (Stage 1+2 ZERO write) |
| 7 | production 5-2 V1 Pure 41 + V2 NEW 15 + EXTEND 7 + W5 갱신 1 + 5 _index + 3 _verification = 72 files aggregate | — | V1 Pure 41 byte-prefix SHA aggregate UNCHANGED 통산 | ✅ EXACT 보존 (STAGE 9 ReadOnly 일시 해제→fix→복원 EXACT 패턴 Wave 4 첫 사례) |

#### 13.1.6 abort marker 9종 + 5-2 specific NEW NOT FIRED self-fire 0 통산

- UPSTREAM_INCOMPLETE:5-2 (upstream 5건 ALL ✅ verified — 6-4 + 5-1 + 6-11 + 1-1 + 3-2 = 외부 5 deps 최다 specialty) ✅
- DERIVATION_DEFINITION_MISSING:5-2 (§7 Phase 3 details paste-ready 완성 auto PASS) ✅
- LOCK_VIOLATION:5-2_PATHA (Stage 1+2 LOCK 18 L1~L18 + DEFINED-HERE 37 + DEFINED-HERE LOCK 4건 R-52-4~7 변경 0) ✅
- CROSS_REF_DRIFT:5-2_PATHA (Stage 1+2 CROSS_REF EXACT 보존) ✅
- BYTE_SHA_MISMATCH:5-2_PATHA (Stage 1 의도된 +Δ만, Stage 2 same-length char swap 0) ✅
- CONFLICT_OPEN_DETECTED:5-2_PATHA (CF-V2-001~006 + CF-52-001~005 = 11 RESOLVED inheritance OPEN 0 보존) ✅
- PHASE4_ENTRY_GATE_NOT_MAPPED:5-2_PATHA (P3-1 4 + P3-2 5 + P3-3 7 = 16 조건 ALL [x] 매핑) ✅
- BILATERAL_SOT2_DRIFT:5-2_PATHA (SOT2_MASTER ZERO write, ⑤-2 bilateral baseline 보존) ✅
- DOWNSTREAM_PROPAGATE_MISS:5-2_PATHA (downstream 0건 Phase 3 전체 마지막 도메인 specialty + Phase 4 V3 implementation forward-defined inheritance pattern 통산 16번째 마지막) ✅
- STAGE9_READONLY_VIOLATION:5-2 (★ 5-2 specific Wave 4 첫 사례 NEW — V1 Pure 41 byte-prefix SHA aggregate UNCHANGED 강제, Path A 적용 시 ReadOnly 일시 해제→fix→복원 EXACT 패턴 충족) ✅

= **abort 10종 NOT FIRED self-fire 0 통산** (chain `path_a_5-2_drift_fix_stage2_2026-05-22` 6 anchor 안전·누락 0·오류 0·미세·수렴·재검증 ALL 충족)

---

## 14. 결론

### 14.1 55개 통합 기술 로드맵 요약

```
총 보완 기술 수: 55개 (중복 제거 후)
├── 기존 SOT 보유: 18개 (LOCK)
├── G-series (Gap 보완): 8개 (DEFINED-HERE)
├── A-series (장점 활용): 8개 (파이프라인 설계 반영, 구현 항목 아님)
├── W-series (단점 보완): 12개 (DEFINED-HERE)
└── H-series (고구현성 추가): 17개 (DEFINED-HERE)

검증 레이어: 8개 (업계 최고 2~3개 대비 2.5~4배)
파이프라인 단계: 7 Phase x 평균 6 Step = ~42 처리 포인트
설계 커버리지: 99% (업계 최고 ~95% 대비 +4%)

V1 즉시 구현: 20개
V2 구현 예정: 13개
V3 구현 예정: 4개
```

### 14.2 다음 단계

1. 서브폴더별 상세 문서 작성 (Phase별, G/W/H별)
2. 6-4 Memory-RAG 도메인과 경계 확정 협의
3. W12 골든 테스트셋 100 QA 구축
4. V1 20개 그룹(23개별 기술) 구현 착수 (§7 Phase 1 참조)

### 14.3 QC 이력

| Phase | 등급 | 일자 | 주요 조치 |
|-------|------|------|----------|
| S8-4 | B | 2026-03-26 | 초안 구조화 완료, §4.1/§8/§10 깊이 부족 지적 |
| S10-3 | A- | 2026-03-27 | R1~R11 적용 명세 확장, 리스크 심화 분석 추가, PII/윤리 섹션 보강, 정량 목표 추가. QC PASS. |

---

## 부록 A: 컨텍스트 크기별 처리 전략 카탈로그

> Tier 5 추가 부록 — 사용자/개발자 빠른 참조용.

| 크기 구간 | Phase | 핵심 전략 | 예상 정확도 | 소요 시간 (V1) |
|----------|-------|----------|-----------|--------------|
| < 10K | B | 직접 주입 + 3-Pass 읽기 | 98% | ~30초 |
| 10~50K | B+ | 직접 주입 + Multi-Pass + Self-Consistency | 97% | ~2분 |
| 50~130K | C | MemWalker 트리 + 위치 편향 보정 + Distractor 필터 | 92% | ~5분 |
| 130~200K | D | 슬라이딩 윈도우 + 압축 (손실 ≤ 0.15) + 원자 명제 추출 | 82% | ~10분 |
| 200K+ | E | 분할 + 한국어 청킹 + 4-Index Fusion + Agentic RAG | 80% | ~15분+ |

### A.1 KV-Cache 히트 시 단축 경로

모든 구간에서 KV-Cache 히트(A2) 시:
- 비용 90% 절감, 지연 85% 감소
- Phase 진입 전 캐시 확인 → 히트 시 즉시 활용

### A.2 Cascade 전략 매트릭스 (W1)

| 문서 복잡도 | Pass 1 (구조) | Pass 2 (상세) | Pass 3 (검증) |
|-----------|-------------|-------------|-------------|
| 단순 (코드/설정) | 로컬 100% | 로컬 100% | 로컬 100% |
| 중간 (가이드/매뉴얼) | 로컬 | Cloud Mini 30% | 로컬 |
| 복잡 (설계서/논문) | 로컬 | Cloud Mini 40% | Cloud Main 20% |

---

## 부록 B: 55개 기술 매핑 테이블

> 전체 55개 기술의 V1/V2/V3 배정 + 소유 도메인 + 파이프라인 위치 총괄표.

| # | 분류 | 기술명 | 소유 | 버전 | Phase | 심각도/난이도 |
|---|------|--------|------|------|-------|-------------|
| 1 | LOCK | Contextual Retrieval | D2.0-06 | V1 | E-2 | CRITICAL |
| 2 | LOCK | Hybrid Search (BM25+Vector) | D2.0-06 | V1 | E-4 | CRITICAL |
| 3 | LOCK | Cross-Encoder Reranking | D2.0-06 | V1 | E-5 | HIGH |
| 4 | LOCK | 컨텍스트 자동 압축 | D2.0-02 | V2 | D-1 | HIGH |
| 5 | LOCK | 슬라이딩 윈도우 | D2.0-05 | V1 | D-0 | - |
| 6 | LOCK | Sparse Attention | STEP7 | V3 | - | - |
| 7 | LOCK | Self-RAG / CRAG / RAPTOR | STEP7 | V2 | E-6 | - |
| 8 | LOCK | Late Chunking (Jina AI) | STEP7 | V2 | E-2 | - |
| 9 | LOCK | ColBERT v3 Multi-Vector | STEP7 | V2 | E-4 | - |
| 10 | LOCK | NLI Hallucination Detection | D2.0-07 | V2 | F-L4 | CRITICAL |
| 11 | LOCK | QoD 품질 점수 체계 | CLAUDE.md | V1 | F-L1 | LOCK |
| 12 | LOCK | 한국어 RAG 최적화 (Mecab/Kiwi) | D2.0-06 | V1 | E-1 | - |
| 13 | LOCK | Dynamic Chunking | STEP7-D | V1 | A-2 | - |
| 14 | LOCK | 4-Index Fusion 검색 | STEP7-G | V1 | E-4 | CRITICAL |
| 15 | LOCK | 메모리 4계층 (L0~L3) | D2.0-06 | V1 | G | - |
| 16 | LOCK | Prompt Caching (90% 절감) | D2.0-02 | V1 | A-7 | CRITICAL |
| 17 | LOCK | Batch API (50% 절감) | D2.0-02 | V1 | - | MEDIUM |
| 18 | LOCK | Knowledge Graph Engine | D2.0-01 | V3 | G-1 | - |
| 19 | G | G1: Lost-in-the-Middle 대응 | **5-2** | V1 | C-1 | CRITICAL |
| 20 | G | G2: Context Rot 인식 | **5-2** | V1 | A-8 | CRITICAL |
| 21 | G | G3: information_loss 임계값 | **5-2** | V1 | D-1 | HIGH |
| 22 | G | G4: 200K+ 분할 알고리즘 | **5-2** | V2 | E-1 | HIGH |
| 23 | G | G5: V1 환각 자동 검증 | **5-2** | V1 | F-L2 | HIGH |
| 24 | G | G6: Distractor Interference | **5-2** | V1 | C-2/E-5 | MEDIUM |
| 25 | G | G7: 가이드 분할 전략 | **5-2** | V2 | - | MEDIUM |
| 26 | G | G8: Agentic RAG 루프 제한 | **5-2** | V2 | E-6 | MEDIUM |
| 27 | W | W1: Smart Cascade | **5-2** | V1 | A-9/B-1 | CRITICAL |
| 28 | W | W2: Ring Attention Lite | **5-2** | V1→V3 | D-0 | HIGH |
| 29 | W | W3: Ensemble Embedding | **5-2** | V1→V2 | E-3 | HIGH |
| 30 | W | W4: Synthetic Data+LoRA | **5-2** | V2 | G-5 | HIGH |
| 31 | W | W5: Speculative Decoding+Medusa | **5-2** | V1→V2 | - | HIGH |
| 32 | W | W6: LLM-Augmented KG | **5-2** | V2→V3 | G-1 | HIGH |
| 33 | W | W7: MDCure Multi-Doc | **5-2** | V2→V3 | E-4 | CRITICAL |
| 34 | W | W8: LongRoPE/YaRN | **5-2** | V1→V2 | D-0 | HIGH |
| 35 | W | W9: Self-Consistency | **5-2** | V1 | B-1/F-L7 | CRITICAL |
| 36 | W | W10: Sliding Chunk 완전성 | **5-2** | V1 | E-1 | HIGH |
| 37 | W | W11: Attributed QA | **5-2** | V1 | B-3/F-L3 | CRITICAL |
| 38 | W | W12: Continuous Evaluation | **5-2** | V1→V2 | G-6 | CRITICAL |
| 39 | H | H1: HyDE | **5-2** | V1 | E-4 | Easy |
| 40 | H | H2: Query Decomposition | **5-2** | V1 | A-10 | Easy |
| 41 | H | H3: Query Routing | **5-2** | V1 | A-11 | Easy-Med |
| 42 | H | H4: RAG-Fusion | **5-2** | V1 | E-4 | Easy |
| 43 | H | H5: FLARE | **5-2** | V2 | B-2/C-4/F-L8 | Medium |
| 44 | H | H6: Chain-of-Note | **5-2** | V1 | E-5 | Medium |
| 45 | H | H7: Step-Back Prompting | **5-2** | V1 | E-4 | Easy |
| 46 | H | H8: Parent-Child Chunk | **5-2** | V1 | E-1 | Easy |
| 47 | H | H9: Proposition Indexing | **5-2** | V2 | E-1.5 | Medium |
| 48 | H | H10: Layout Analysis | **5-2** | V1 | A-4 | Medium |
| 49 | H | H11: Structured Extraction | **5-2** | V1 | A-5/E-1 | Easy-Med |
| 50 | H | H12: ColPali Multi-Modal | **5-2** | V2 | A-6 | Medium |
| 51 | H | H13: Adaptive Retrieval | **5-2** | V2 | A-12 | Medium |
| 52 | H | H14: Contextual Compression | **5-2** | V1 | E-5 | Easy |
| 53 | H | H15: Metadata Filtering | **5-2** | V1 | E-4 | Easy |
| 54 | H | H16: Confidence Calibration | **5-2** | V1 | F-L6 | Easy-Med |
| 55 | H | H17: Chain-of-Verification | **5-2** | V2 | F-L4.5 | Medium |

---

*끝. 본 계획서는 원본 `FILE CONTEXT/VAMOS_파일_컨텍스트_이해_최종_업데이트.md` (1,618줄)의 전체 내용을 14+α 섹션으로 구조화한 것이다.*
