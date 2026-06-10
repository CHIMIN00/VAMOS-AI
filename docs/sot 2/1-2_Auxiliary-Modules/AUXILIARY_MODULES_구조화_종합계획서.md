# 보조 모듈 (Auxiliary Modules) 구조화 종합 계획서

> **버전**: v1.0
> **작성일**: 2026-03-22
> **목적**: sot 2/1-2_Auxiliary-Modules/을 보조 모듈 구현 정본으로 구조화
> **Status**: APPROVED — Phase 5 FINAL PASS (2026-03-24) + Phase 4 ✅ 완료 (2026-05-23, P4-1~P4-6 production-ready 정본 승급 + 80+ production .md ALL APPROVED + ReadOnly TRUE)
> **Tier**: 1 - Core Intelligence
> **SOT 출처**: D2.0-01 §5.6, D2.0-02 §7, D2.0-06
> **Part2 상태**: COMPLETE (1-10 완료, 2026-04-07 — `06_mapping/part2_reference_table.md`)
> **Last-reviewed**: 2026-05-23 (Phase 4 production promotion)
> **ReadOnly**: TRUE (production 승급 후 immutable, 변경 시 일시 해제→fix→복원 EXACT 패턴 + audit log)

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
- [부록 §A 모듈 의존성 그래프](#a-모듈-의존성-그래프)
- [부록 §B 인터페이스 계약서](#b-인터페이스-계약서)

---

## 1. 현재 상태 분석

### 1.1 기존 문서 현황

| 문서 | 위치 | 역할 | 줄수 | 상태 |
|------|------|------|------|------|
| **D2.0-01 §5.6** | docs/sot/ | I-Series 모듈 카탈로그 (인덱스) | ~40줄 | 모듈 ID/이름/분류만, 구현 상세 없음 |
| **D2.0-02 §7** | docs/sot/ | ORANGE CORE 모듈 상세 (아키텍처) | ~80줄 | 모듈 간 관계도 + 파이프라인 개요 수준 |
| **D2.0-06** | docs/sot/ | Storage/Memory 설계 문서 | ~200줄 | Memory 4-layer, VectorStore, Semantic Cache 상세 |
| **PART2 V1-Phase 1** (L1679~1717) | docs/guides/ | 구현 가이드 (I-4, I-13, I-14, I-16) | ~38줄 | 2~3줄 설명 + SOT 포인터만 |
| **PART2 V1-Phase 6** (L2600) | docs/guides/ | 구현 가이드 (S-1) | ~5줄 | S-1 Self-check 한 줄 설명 |
| **AUXILIARY_MODULES_상세명세.md** | sot 2/1-2_Auxiliary-Modules/ | 모듈별 입출력/파이프라인/알고리즘 상세 | 336줄 | 5개 모듈 상세 스키마 기술, L2~L3 수준 |

### 1.2 sot 2/ 현재 파일

| # | 파일명 | 내용 | 상태 |
|---|--------|------|------|
| 1 | AUXILIARY_MODULES_상세명세.md | I-4, I-13, I-14, I-16, S-1 상세명세 | 존재 (L2~L3 수준) |
| 2 | AUXILIARY_MODULES_구조화_종합계획서.md | 본 문서 | 신규 작성 |

### 1.3 핵심 문제

1. **권한 체계 부재**: sot 2/1-2_Auxiliary-Modules/가 VAMOS 문서 권한 체인(RULE 1.3 > PLAN 3.0 > DESIGN 2.0)에 공식 편입되지 않음
2. **분산된 SOT**: D2.0-01, D2.0-02, D2.0-06에 보조 모듈 관련 LOCK 값이 산재하여, 구현 시 3개 문서를 교차 참조해야 함
3. **PART2 빈껍데기**: Part2에 2~3줄 설명만 존재하여 구현자가 상세명세.md 없이는 착수 불가
4. **서브폴더 미생성**: 계획된 01~05 서브폴더가 아직 물리적으로 생성되지 않음
5. **LOCK 값 분산**: QoD formula, RAG hybrid ratio, embedding model, memory layers 등 핵심 LOCK 값이 여러 D2.0 문서에 흩어져 있어 일관성 확인이 어려움
6. **모듈 간 의존성 미문서화**: 5개 모듈 간, 그리고 외부 모듈(I-2, I-5, I-6, I-25 등)과의 의존성이 상세명세에 부분적으로만 기술됨
7. **인터페이스 계약 부재**: 모듈 간 호출 시 사용할 공식 ABC(Abstract Base Class) 인터페이스가 정의되지 않음

### Part2 상태 및 방식 C 접근법
- **Part2 상태**: COMPLETE (1-10 완료 + 재검증 v1.2, 2026-04-07 — `06_mapping/part2_reference_table.md` 정방향 19건 / 역방향 56 파일 전수 매핑, UNMAPPED 0건)
- **방식 C 접근법**: 보완 작성

---

## 2. 목표 구조 (최종 형태)

### 2.1 폴더 트리

```
D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\
│
├── INDEX.md                                      ← 마스터 인덱스 (유일)
├── AUXILIARY_MODULES_구조화_종합계획서.md           ← 본 문서
├── AUXILIARY_MODULES_상세명세.md                   ← 기존 상세명세 (아카이브 예정)
├── AUTHORITY_CHAIN.md                             ← 권한 체계 선언
├── CONFLICT_LOG.md                                ← 충돌 기록부
│
├── _archive\                                      ← 원본 상세명세 보존 (읽기 전용)
├── _templates\                                    ← L3 템플릿 + L3 판정 기준
│
├── 00_common\                                     ← 공통 인터페이스, 타입, 에러 정의
│   ├── response_envelope.md                       ← ResponseEnvelope 명세 (LOCK)
│   ├── common_types.md                            ← 공유 타입 정의
│   ├── error_taxonomy.md                          ← 에러 분류 체계
│   └── timeout_policy.md                          ← 타임아웃 정책 명세
│
├── 01_multimodal-interpreter\                     ← I-4 Multimodal Interpreter
│   ├── _index.md
│   ├── input_schema.md                            ← RawInput / InterpretedInput 스키마
│   ├── format_detection.md                        ← MIME 타입 감지 로직
│   ├── text_pipeline.md                           ← 텍스트 입력 처리 파이프라인
│   ├── image_pipeline.md                          ← 이미지 입력 처리 파이프라인
│   ├── audio_pipeline.md                          ← 음성 입력 처리 파이프라인
│   ├── document_pipeline.md                       ← 문서 입력 처리 파이프라인
│   ├── vision_api_integration.md                  ← Vision API 라우팅 로직
│   └── fallback_chain.md                          ← 실패 시 대체 경로
│
├── 02_multimodal-renderer\                        ← I-13 Multimodal Output Renderer
│   ├── _index.md
│   ├── renderer_interface.md                      ← BaseRenderer ABC 정의
│   ├── text_renderer.md                           ← TextRenderer (Markdown/Plain/HTML)
│   ├── chart_renderer.md                          ← ChartRenderer (SVG/PNG/Interactive)
│   ├── code_renderer.md                           ← CodeRenderer (구문 하이라이트)
│   ├── table_renderer.md                          ← TableRenderer (CSV/Excel/Markdown)
│   ├── diagram_renderer.md                        ← DiagramRenderer (Mermaid/그래프)
│   ├── audio_renderer.md                          ← AudioRenderer (TTS/오디오 출력)
│   ├── image_renderer.md                          ← ImageRenderer (이미지 출력)
│   ├── composite_output.md                        ← 복합 출력 DAG 구성
│   ├── quality_validation.md                      ← 출력 품질 검증
│   └── fallback_chain.md                          ← 렌더링 실패 대체 경로
│
├── 03_summarizer\                                 ← I-14 Summarizer & Memory Distiller
│   ├── _index.md
│   ├── input_output_schema.md                     ← SummarizeRequest / SummaryResult
│   ├── conversation_summary.md                    ← 대화 요약 알고리즘
│   ├── memory_distillation.md                     ← L0→L1 메모리 증류 로직
│   ├── trigger_conditions.md                      ← 자동/수동 트리거 조건
│   ├── memory_layer_integration.md                ← 4-Layer 메모리 연동 (LOCK)
│   └── fallback_chain.md                          ← 요약 실패 대체 경로
│
├── 04_knowledge-search\                           ← I-16 Knowledge Search Engine
│   ├── _index.md
│   ├── search_api.md                              ← KnowledgeSearchEngine API 설계
│   ├── rag_integration.md                         ← I-2 RAG 통합 (hybrid search LOCK)
│   ├── external_sources.md                        ← 외부 지식 소스 연동
│   ├── search_pipeline.md                         ← 검색 파이프라인 + RRF 랭킹 (§2/§5 병합)
│   ├── semantic_cache.md                          ← Semantic Cache (LOCK: cosine ≥ 0.95)
│   ├── embedding_model.md                         ← BGE-M3 임베딩 명세 (LOCK)
│   ├── vectorstore_adapter.md                     ← VectorStore LOCK 인터페이스
│   └── fallback_chain.md                          ← 검색 실패 대체 경로
│
├── 05_self-check\                                 ← S-1 Self-check Engine
│   ├── _index.md
│   ├── qod_formula.md                             ← QoD 공식 및 가중치 (LOCK)
│   ├── qod_thresholds.md                          ← QoD 임계값 정책 (LOCK)
│   ├── evaluation_window.md                       ← 실시간/일간/주간 평가 윈도우
│   ├── anomaly_detection.md                       ← 이상 감지 기준 (4 Level)
│   ├── sdar_trigger.md                            ← I-25 SDAR 트리거 조건
│   ├── prometheus_metrics.md                      ← 모니터링 메트릭 노출
│   ├── self_check_thresholds.md                   ← Phase별 Self-check 임계값 (LOCK)
│   └── fallback_chain.md                          ← Self-check 실패 대체 경로
│
└── 06_mapping\                                    ← 매핑 & 거버넌스 문서
    ├── module_dependency_graph.md                 ← 모듈 의존성 그래프
    ├── interface_contracts.md                     ← 인터페이스 계약서
    ├── lock_value_registry.md                     ← LOCK 값 통합 레지스트리
    └── cross_module_dedup.md                      ← 교차 중복 감사 결과
```

### 2.2 깊이 규칙

```
최대 3단계:
  1-2_Auxiliary-Modules/ → XX_폴더/ → 파일.md          (2단계) O
  1-2_Auxiliary-Modules/ → XX_폴더/ → sub/ → 파일.md   (3단계) O
  4단계 이상 → 절대 금지 X
```

보조 모듈 도메인은 AI Investing과 달리 관점 수가 적고(5개 모듈 + 공통 + 매핑 = 7개 폴더), 각 모듈 내 파일 수도 6~9개로 제한적이므로 2단계로 충분하다.

### 2.3 네이밍 규칙

- **폴더명**: 영문 소문자 + 하이픈, 접두사 2자리 번호 (`00_`, `01_`, ..., `06_`)
- **파일명**: 영문 소문자 + 언더스코어 (`.md` 확장자)
- **모듈 접두사**: 폴더명에 모듈 기능명 사용 (모듈 ID가 아닌 기능 설명)
  - `01_multimodal-interpreter` (I-4)
  - `02_multimodal-renderer` (I-13)
  - `03_summarizer` (I-14)
  - `04_knowledge-search` (I-16)
  - `05_self-check` (S-1)
- **한글 파일명 금지**: 모든 신규 파일은 영문 snake_case

---

## 3. 권한 체계 선언

### 3.1 기존 VAMOS 권한 체인

```
RULE 1.3 > PLAN 3.0 > DESIGN 2.0 LOCK > DESIGN body > Schema/TECH_STACK
```

### 3.2 Auxiliary-Modules 확장 권한 체인

```
RULE 1.3
  > PLAN 3.0
    > DESIGN 2.0
      ├─ D2.0-01 §5.6 (I-Series 모듈 카탈로그, 모듈 분류 LOCK)
      ├─ D2.0-02 §7 (ORANGE CORE 모듈 상세, 파이프라인 아키텍처)
      └─ D2.0-06 (Storage/Memory 설계, Memory Layer/VectorStore/Cache LOCK)
        > PART2 V1-Phase 1 (L1679~1717) + V1-Phase 6 (L2600)
          > sot 2/1-2_Auxiliary-Modules/ (모듈 구현 상세 = 구현 정본) ← 신규 티어
```

**핵심**: sot 2/1-2_Auxiliary-Modules/는 D2.0-01/02/06의 LOCK 값을 **재정의할 수 없으며**, What + How (구현 상세)만 기술한다. When(Phase 배정)은 PART2가 정본이다.

### 3.3 각 문서의 권한 범위

| 문서 | 권한 레벨 | 결정할 수 있는 것 | 결정할 수 없는 것 |
|------|----------|------------------|------------------|
| **D2.0-01 §5.6** | DESIGN-LOCK | 모듈 ID, 이름, CORE/COND/EXP 분류, change_lock 플래그 | 구현 상세, 파이프라인 로직 |
| **D2.0-02 §7** | DESIGN-ARCH | ORANGE CORE 내부 파이프라인, 5-stage 파이프라인, state machine S0~S8, 모듈 간 관계도 | 개별 모듈 내부 로직 |
| **D2.0-06** | DESIGN-LOCK | Memory 4-layer (L0/L1/L2/L3), VectorStore adapter interface, semantic cache threshold, embedding model spec | 개별 모듈 구현 상세 |
| **PART2 V1-Phase 1/6** | IMPL-GUIDE | When(Phase 배정) + Where(코드 위치) | 모듈 구현 로직 상세 (→ sot 2/) |
| **sot 2/1-2_Auxiliary-Modules/** | IMPL-DETAIL | What + How (입출력 스키마, 파이프라인 알고리즘, fallback chain, 타임아웃 정책) | LOCK 값 재정의, Phase 일정 |
| **상세명세.md** (기존) | IMPL-DETAIL (LEGACY) | 기존 상세 스키마 (마이그레이션 대상) | 향후 변경 (→ 서브폴더 파일로 이관) |

### 3.4 LOCK 보호 선언

> **절대 규칙**: sot 2/1-2_Auxiliary-Modules/ 내 모든 파일은 아래 LOCK 값을 **재정의할 수 없다**.
> 참조 시 반드시 `> LOCK (출처): [원문 그대로]` 형식을 사용한다.

| LOCK 항목 | 정본 출처 | 값 | 비고 |
|-----------|----------|-----|------|
| 모듈 API 시그니처 (I-Series) | D2.0-01 §5.6 | 모듈 카탈로그 정의 그대로 | change_lock 플래그 포함 |
| 의존성 방향 | D2.0-02 §7 (**주의**: 원문 미발견, §5A는 D2.0-01 §4 기재 — D-01) | 단방향 소비 (lower layers → higher layers) | 역방향 호출 금지 |
| 모듈 분류 체계 | D2.0-01 §5.6 | CORE / COND / EXP + change_lock | 분류 변경 시 D2.0-01 수정 필요 |
| I-5 Decision Engine | D2.0-01 §5.6 | change_lock=true, 5-score based | LOCK |
| I-8 Policy Engine | D2.0-01 §5.6 | change_lock=true, synced with D7 | LOCK |
| I-19 Approval Manager | D2.0-01 §5.6 | change_lock=true, synced with D7 | LOCK |
| QoD formula | D2.0-06 DEC-014 → **PLAN-3.0 §1.X 갱신** | `QoD = Accuracy×0.30 + Relevance×0.25 + Completeness×0.20 + Safety×0.15 + Efficiency×0.10` *(5-factor 정본, V1-006)* | S-1 핵심 |
| QoD thresholds | D2.0-06 | `<0.4 L2/L3 forbidden, >=0.7 L2 allowed` | S-1 핵심 |
| Self-check thresholds | D2.0-02 §7 | `P0>=70, P1>=75, P2>=80` | Phase별 최소 점수 |
| RAG hybrid search ratio | D2.0-06 S7D-012 | `alpha=0.3(BM25) + (1-alpha)=0.7(vector)` | I-16 핵심 |
| Embedding model | D2.0-06 | `BGE-M3 (1024-dim, Matryoshka 256-dim)` | I-16 핵심 |
| VectorStore adapter interface | D2.0-06 | `upsert/search/delete/get_by_id` (4 methods) | LOCK interface |
| Memory 4-layer | D2.0-06 | `L0(session)/L1(project)/L2(long-term)/L3(procedural)` | I-14 핵심 |
| Semantic cache | D2.0-06 | `cosine_similarity >= 0.95, TTL 24h` | I-16 캐시 |
| PII 마스킹 | D2.0-06 | AES-256 암호화, Regex + NER 감지, 비가역 마스킹 | 개인정보 보호 |
| 메모리 검색 우선순위 | D2.0-06 S7D-042 | L0→L1→L2→L3, 레이어당 max 5, 최종 top 5 | Memory 검색 순서 |
| ResponseEnvelope minimum spec | D2.0-02 §7 | 표준 응답 봉투 최소 필드 세트 | 전 모듈 공통 |
| Standard 5-stage pipeline | D2.0-02 §7 | 5단계 파이프라인 | 전 모듈 공통 |
| State machine | D2.0-02 §7 | S0~S8 상태 전이 | 전 모듈 공통 |

> LOCK (PLAN-3.0 §1.X, D2.0-06 DEC-014 SUPERSEDED): `QoD = Accuracy×0.30 + Relevance×0.25 + Completeness×0.20 + Safety×0.15 + Efficiency×0.10` *(5-factor 정본, V1-006)*

> LOCK (D2.0-06): `QoD < 0.4 → L2/L3 forbidden; QoD >= 0.7 → L2 allowed`

> LOCK (D2.0-02 §7): `Self-check thresholds: P0>=70, P1>=75, P2>=80`

> LOCK (D2.0-06 S7D-012): `RAG hybrid search: alpha=0.3(BM25) + (1-alpha)=0.7(vector)`

> LOCK (D2.0-06): `Embedding: BGE-M3 (1024-dim, Matryoshka 256-dim)`

> LOCK (D2.0-06): `VectorStore adapter: upsert / search / delete / get_by_id`

> LOCK (D2.0-06): `Memory 4-layer: L0(session) / L1(project) / L2(long-term) / L3(procedural)`

> LOCK (D2.0-06): `Semantic cache: cosine_similarity >= 0.95, TTL 24h`

> LOCK (D2.0-02 §7): `ResponseEnvelope minimum spec`

> LOCK (D2.0-02 §7): `Standard 5-stage pipeline, state machine S0~S8`

---

## 4. 거버넌스 규칙

> **글로벌 거버넌스 규칙**: 본 도메인은 0-0_Governance-Rules-Meta에서 정의한 R1~R11 글로벌 규칙을 전체 준수합니다.
> 아래는 글로벌 규칙에 추가되는 도메인 고유 규칙입니다.

### Common R1~R8 (도메인 적응, R5/R7 제거)

| # | 규칙 | 이유 | 위반 시 |
|---|------|------|---------|
| R1 | 폴더 깊이 최대 3단계 | Windows 260자 경로 제한 | 파일 생성 거부 |
| R2 | 마스터 INDEX.md 1개 + 폴더별 _index.md (파일 목록만) | 유지보수 부담 분산 | INDEX.md 미갱신 = 커밋 불가 |
| R3 | 파일명 변경 시 PART2 링크 테이블 동기화 | 참조 정합성 | 변경 커밋에 PART2 업데이트 포함 필수 |
| R4 | 겹치는 개념 → 정본 소유자 1곳 상세, 나머지 `> 참조:` 링크 | 교차 참조 중복 방지 | canonical_owner_table.md에 등록 필수 |
| ~~R5~~ | ~~삭제 — Tier 1은 SPEC §7-8 해당없음~~ | | |
| R6 | sot 2/ = What+How만, When = PART2만 | Phase 이중 기재 금지 | Phase 정보 발견 시 즉시 삭제 |
| ~~R7~~ | ~~삭제 — Tier 1은 STEP7 해당없음 (D2.0 기반)~~ | | |
| R8 | PART2 링크는 단일 테이블에 집중 | 링크 관리 단순화 | 본문 산발 링크 금지 |
| R9 | LOCK/FREEZE 값 재정의 금지. 참조 시 `> LOCK (출처): [원문]` | LOCK 보호 | 즉시 수정 |

> **참고**: R5(SPEC 역할 고정)와 R7(STEP7-I 매핑)은 AI Investing 도메인 전용이므로 본 도메인에서 제거.

### R-02-1: 모듈 ABC 인터페이스 계약 필수

> **규칙**: 각 모듈은 반드시 ABC(Abstract Base Class) 인터페이스를 정의하고, 해당 인터페이스를 `06_mapping/interface_contracts.md`에 등록해야 한다.

| 항목 | 요구사항 |
|------|---------|
| **적용 대상** | I-4, I-13, I-14, I-16, S-1 (5개 모듈 전체) |
| **인터페이스 정의 위치** | 각 모듈 폴더의 첫 번째 파일 (input_schema.md 또는 renderer_interface.md 등) |
| **등록 위치** | 06_mapping/interface_contracts.md |
| **필수 포함** | 메서드 시그니처, 입력 타입, 출력 타입, 에러 타입, 타임아웃 |
| **위반 시** | 모듈 구현 착수 불가 (Phase Gate 검증 항목) |

### R-02-2: fallback chain 정의 필수

> **규칙**: 각 모듈은 반드시 `fallback_chain.md`를 포함하여, 주요 기능 실패 시 대체 경로를 명시해야 한다.

| 항목 | 요구사항 |
|------|---------|
| **적용 대상** | 5개 모듈 전체 |
| **필수 내용** | 실패 유형별 fallback 대상, 최대 재시도 횟수, 최종 실패 시 동작 |
| **fallback 방향** | 항상 lower-fidelity 방향 (예: Vision API 실패 → OCR only) |
| **위반 시** | Phase 1 완료 인정 불가 |

### R-02-3: 타임아웃 정책 명시 필수

> **규칙**: 각 모듈의 외부 호출(API, 모델 추론 등)에 대해 타임아웃을 명시해야 한다.

| 항목 | 요구사항 |
|------|---------|
| **적용 대상** | 외부 API/모델 호출이 있는 모든 파이프라인 |
| **기본 타임아웃** | 동기 호출 30초, 비동기 호출 60초, 배치 처리 300초 |
| **타임아웃 초과 시** | fallback chain 진입 또는 에러 반환 |
| **정의 위치** | 00_common/timeout_policy.md (전역) + 각 모듈 fallback_chain.md (모듈별 오버라이드) |

### R-02-4: LOCK 값 인라인 인용 규칙

> **규칙**: LOCK 값을 참조할 때 반드시 `> LOCK (출처): [원문 그대로]` 형식을 사용한다. 값을 재해석/재계산하여 다른 형태로 기술하는 것을 금지한다.

### R-02-5: 모듈 간 통신은 ResponseEnvelope 필수

> **규칙**: 5개 보조 모듈 간, 그리고 외부 모듈과의 모든 통신은 ResponseEnvelope (D2.0-02 §7 LOCK) 형식을 사용해야 한다. 직접 raw data 전달을 금지한다.

### R-02-6: 상세명세.md 마이그레이션 후 아카이브

> **규칙**: 기존 AUXILIARY_MODULES_상세명세.md의 내용을 서브폴더별 파일로 분배한 후, 원본은 `_archive/`에 이동하고 읽기 전용으로 보존한다. 이후 변경은 서브폴더 파일에서만 수행한다.

---

## 5. 선행작업

> **이 3건은 Phase 1 진입 전에 반드시 완료해야 한다.**

### 선행작업 A: LOCK 값 통합 레지스트리 작성

**목적**: D2.0-01, D2.0-02, D2.0-06에 산재한 LOCK 값을 단일 문서로 통합하여 교차 참조 부담 제거

**절차**:

1. D2.0-01 §5.6에서 I-4, I-13, I-14, I-16, S-1 관련 LOCK 항목 추출
2. D2.0-02 §7에서 ResponseEnvelope, pipeline, state machine LOCK 항목 추출; D2.0-06에서 QoD formula (DEC-014), thresholds LOCK 항목 추출
3. D2.0-06에서 Memory layers, VectorStore, semantic cache, embedding model LOCK 항목 추출
4. 결과를 `06_mapping/lock_value_registry.md`에 통합 기록

**산출물 형식**:

```markdown
| LOCK ID | 항목 | 값 | 출처 | 관련 모듈 | 비고 |
|---------|------|-----|------|----------|------|
| LOCK-AX-01 | I-Series 모듈 분류 | CORE/COND/EXP + change_lock flags | D2.0-01 §5.6 | 전체 | |
| LOCK-AX-02 | 의존성 방향 | 단방향 소비 (하위→상위 금지) | D2.0-01 §4 | 전체 | **주의**: D2.0-01 §4·D2.0-02 §7 원문에서 정확한 문구 미발견 (D-01). §3.4는 "D2.0-02 §7" 기재 |
| LOCK-AX-03 | QoD 공식 | **PLAN-3.0 정본 (5-factor)**: QoD = Accuracy×0.30 + Relevance×0.25 + Completeness×0.20 + Safety×0.15 + Efficiency×0.10 | D2.0-06 DEC-014 → **PLAN-3.0 §1.X 갱신** | S-1 | **V1-006**: D2.0-06 4-factor SUPERSEDED. 합계=1.0 |
| LOCK-AX-04 | QoD 임계값 | <0.4 L2/L3 저장 금지, ≥0.7 L2 허용 | D2.0-06 | S-1 | |
| LOCK-AX-05 | Self-check 임계값 | P0≥70, P1≥75, P2≥80 | D2.0-02 §7.53-1 | S-1 | |
| LOCK-AX-06 | RAG 하이브리드 비율 | alpha=0.3(BM25) + (1-alpha)=0.7(vector) | D2.0-06 S7D-012 | I-16 | |
| LOCK-AX-07 | 임베딩 모델 | BGE-M3 (1024-dim, Matryoshka 256-dim) | D2.0-06 DEC-005 | I-16 | |
| LOCK-AX-08 | VectorStore 인터페이스 | upsert/search/delete/get_by_id | D2.0-06 | I-16 | 4 methods LOCK |
| LOCK-AX-09 | 메모리 4계층 | L0(세션)/L1(프로젝트)/L2(장기)/L3(절차적) | D2.0-06 | I-14 | |
| LOCK-AX-10 | 시맨틱 캐시 | cosine_similarity ≥ 0.95, TTL 24h | D2.0-06 | I-16 | |
| LOCK-AX-11 | ResponseEnvelope | answer/evidence/self_check/decision_ref/audit 필수 | D2.0-02 §5.1.1 | 전체 | |
| LOCK-AX-12 | 표준 파이프라인 | 5단계: Perception→Reasoning→Action→Memory→Reflection | D2.0-02 §2.1 | 전체 | |
| LOCK-AX-13 | 상태 머신 | S0~S8, S3 Decision Lock 불변 | D2.0-02 §2.2 | 전체 | |
| LOCK-AX-14 | PII 마스킹 | AES-256, Regex + NER 감지, 비가역 마스킹 | D2.0-06 | I-14 | |
| LOCK-AX-15 | 메모리 검색 우선순위 | L0→L1→L2→L3, 레이어당 max 5, 최종 top 5 | D2.0-06 S7D-042 | I-16 | |
```

**산출물**: `06_mapping/lock_value_registry.md`

---

### 선행작업 B: 상세명세 → 서브폴더 분배 매핑 확정

**목적**: 기존 AUXILIARY_MODULES_상세명세.md의 각 섹션을 어느 서브폴더/파일로 분배할지 확정

**분배 매핑 테이블**:

| 상세명세 섹션 | 내용 요약 | 분배 대상 폴더 | 분배 대상 파일(들) |
|-------------|----------|--------------|-----------------|
| I-4 §1 입출력 스키마 | RawInput, InterpretedInput | 01_multimodal-interpreter/ | input_schema.md |
| I-4 §2 포맷 감지 로직 | MIME 타입 감지 분기 | 01_multimodal-interpreter/ | format_detection.md |
| I-4 §3 텍스트 입력 | langdetect, chardet, tiktoken | 01_multimodal-interpreter/ | text_pipeline.md |
| I-4 §3 이미지 입력 | PIL, CLIP, OCR | 01_multimodal-interpreter/ | image_pipeline.md |
| I-4 §3 음성 입력 | Whisper, Deepgram, VAD | 01_multimodal-interpreter/ | audio_pipeline.md |
| I-4 §3 문서 입력 | docling, python-docx, pandas | 01_multimodal-interpreter/ | document_pipeline.md |
| I-4 §4 Vision API | Claude Vision, GPT-4V routing | 01_multimodal-interpreter/ | vision_api_integration.md |
| I-13 §1 렌더러 인터페이스 | BaseRenderer ABC | 02_multimodal-renderer/ | renderer_interface.md |
| I-13 §2 포맷별 렌더러 | 7개 렌더러 테이블 (1:N 분할) | 02_multimodal-renderer/ | text_renderer.md, chart_renderer.md, code_renderer.md, table_renderer.md, diagram_renderer.md, audio_renderer.md, image_renderer.md |
| I-13 §3 복합 출력 | DAG 구성, 병렬 렌더링 | 02_multimodal-renderer/ | composite_output.md |
| I-13 §4 출력 품질 검증 | 차트/코드/표/이미지 검증 | 02_multimodal-renderer/ | quality_validation.md |
| I-14 §1 입출력 스키마 | SummarizeRequest, SummaryResult | 03_summarizer/ | input_output_schema.md |
| I-14 §2 대화 요약 | 턴별 추출, 엔티티 체인, 계층적 요약 | 03_summarizer/ | conversation_summary.md |
| I-14 §2 메모리 증류 | L0→L1 승격, 증류 규칙 | 03_summarizer/ | memory_distillation.md |
| I-14 §3 트리거 조건 | 자동(20턴, 80% 윈도우), 수동 | 03_summarizer/ | trigger_conditions.md |
| I-16 §1 검색 API | KnowledgeSearchEngine 클래스 | 04_knowledge-search/ | search_api.md |
| I-16 §2 검색 파이프라인 | 쿼리 확장→병렬→RRF→Reranking | 04_knowledge-search/ | search_pipeline.md |
| I-16 §3 RAG 통합 | ChromaDB + BGE-M3 + BM25 | 04_knowledge-search/ | rag_integration.md |
| I-16 §4 외부 소스 | Web, Wikipedia, arXiv, 금융, 뉴스(RT-BNP) | 04_knowledge-search/ | external_sources.md |
| I-16 §5 랭킹 | 최종 점수 공식 | 04_knowledge-search/ | search_pipeline.md (§2와 병합 — 랭킹은 파이프라인 최종 단계) |
| S-1 §1 QoD 점수 | accuracy, latency, hallucination 등 | 05_self-check/ | qod_formula.md |
| S-1 §2 평가 윈도우 | 실시간/일간/주간 | 05_self-check/ | evaluation_window.md |
| S-1 §3 이상 감지 | Level 1~4 기준 | 05_self-check/ | anomaly_detection.md |
| S-1 §4 SDAR 트리거 | AR-L1~L4 조건 | 05_self-check/ | sdar_trigger.md |
| S-1 §5 Prometheus 메트릭 | vamos_qod_score 등 | 05_self-check/ | prometheus_metrics.md |

**분배 제외 줄 회계** (비콘텐츠 — 아카이브 시 원본 보존):

| 상세명세 영역 | 줄 범위 | 줄 수 | 제외 사유 |
|-------------|---------|------|----------|
| 문서 제목 + 메타데이터 (Tier, Part2 상태, SOT 근거, 위치) | L1-8 | 8 | 문서 메타 — 아카이브 시 보존, 분배 대상 아님 |
| 개요 (도입부 설명) | L10-13 | 4 | 5개 모듈 공통 컨텍스트 — 00_common/ README 또는 아카이브 보존 |
| I-4 "현재 Part2 내용" (L1679~1682 원문 인용) | L18-22 | 5 | PART2 원문 스냅샷 — 1-10 링크 테이블로 대체 |
| I-13 "현재 Part2 내용" (L1707~1709 원문 인용) | L88-92 | 5 | 동일 |
| I-14 "현재 Part2 내용" (L1711~1713 원문 인용) | L145-149 | 5 | 동일 |
| I-16 "현재 Part2 내용" (L1715~1717 원문 인용) | L207-211 | 5 | 동일 |
| S-1 "현재 Part2 내용" (L2600~2602 원문 인용) | L279-283 | 5 | 동일 |
| 공통 SOT 참조 (D2.0 참조 목록) | L332-336 | 5 | lock_value_registry.md §4에 이미 포함 |
| 구분선(`---`), 빈 줄, 모듈 간 경계 (L9,L14-15,L84-85,L141-142,L203-204,L275-276,L330-331) | 전체 산재 | 13 | 구조적 요소 — 분배 대상 아님 |
| **비콘텐츠 소계** | | **55** | |

> **줄 수 회계**: 상세명세.md 전체 **336줄** = 분배 대상 **281줄** (위 매핑 테이블 25개 행이 전수 커버) + 분배 제외 **55줄** (비콘텐츠). 미지정 줄 = 0. *(0-3 검증으로 정확값 확정, 2026-03-29)*

**산출물**: 본 계획서 §5B (확정됨, **확정일: 2026-03-29**)

---

### 선행작업 C: 교차 모듈 중복 감사

**목적**: 5개 모듈 간 개념 중복 식별 → 정본 소유자 배정

**예상 중복 영역**:

| 개념 | 등장 모듈 | 정본 소유자 |
|------|----------|-----------|
| 임베딩 생성 | I-4 (입력 임베딩), I-16 (검색 임베딩) | I-16 (04_knowledge-search/embedding_model.md) |
| 메모리 Layer 정의 | I-14 (메모리 증류), I-16 (검색 대상) | I-14 (03_summarizer/memory_layer_integration.md) |
| QoD 점수 계산 | S-1 (주 계산), I-14 (요약 품질 참조) | S-1 (05_self-check/qod_formula.md) |
| fallback chain 패턴 | 전 모듈 공통 | 00_common (fallback 패턴 정의), 각 모듈 (인스턴스) |
| ResponseEnvelope | 전 모듈 공통 | 00_common/response_envelope.md |
| 타임아웃 정책 | 전 모듈 공통 | 00_common/timeout_policy.md |
| I-5 Decision Engine 의존성 *(0-4 추가 발견)* | I-13 (RenderPlan), I-14 (수동 트리거) | 06_mapping/interface_contracts.md |

**산출물**: `06_mapping/cross_module_dedup.md` (확정됨, **확정일: 2026-03-29**, 최종 7건 = 시드 6건 + 추가 1건)

---

## 6. 이슈 해결 매핑

### 6.1 CRITICAL (3건)

| 이슈# | 문제 | 해결 | 해결 시점 | 산출물 |
|--------|------|------|----------|--------|
| AUX-01 | sot 2/1-2_Auxiliary-Modules/가 권한 체인에 없음 | §3 권한 체계 선언 + AUTHORITY_CHAIN.md 작성. PART2에 정본 선언 추가 | Phase 0 | AUTHORITY_CHAIN.md |
| AUX-02 | LOCK 값이 D2.0-01/02/06에 산재하여 구현자 혼란 | 선행작업 A: LOCK 통합 레지스트리 작성 | Phase 0 | lock_value_registry.md |
| AUX-03 | PART2에 2~3줄만 존재, 구현 불가 | 상세명세.md를 서브폴더로 분배 + PART2에 sot 2/ 링크 추가 | Phase 1 | 서브폴더 파일 40+ |

### 6.2 HIGH (4건)

| 이슈# | 문제 | 해결 | 해결 시점 | 산출물 |
|--------|------|------|----------|--------|
| AUX-04 | 서브폴더 미생성 (01~05) | Phase 1에서 §2.1 폴더 트리 전체 생성 | Phase 1 | 7개 폴더 + 파일 |
| AUX-05 | 모듈 간 의존성 미문서화 | §A 모듈 의존성 그래프 작성 | Phase 1 | module_dependency_graph.md |
| AUX-06 | ABC 인터페이스 미정의 | §B 인터페이스 계약서 작성 | Phase 1 | interface_contracts.md |
| AUX-07 | 상세명세.md가 단일 파일에 5개 모듈 혼재 | Phase 0 (0-3): 선행작업 B 매핑 검증·확정 → Phase 1 (1-2): 매핑에 따라 실제 분배 + (1-9) 아카이브 | Phase 0 (매핑) + Phase 1 (분배) | §5B 확정 (0-3) → 분배 완료 + _archive/ (1-2, 1-9) |

### 6.3 MEDIUM (4건)

| 이슈# | 문제 | 해결 | 해결 시점 | 산출물 |
|--------|------|------|----------|--------|
| AUX-08 | fallback chain 미정의 | R-02-2 규칙에 따라 각 모듈 fallback_chain.md 작성 | Phase 1 | 5개 fallback_chain.md |
| AUX-09 | 타임아웃 정책 부재 | R-02-3 규칙에 따라 00_common/timeout_policy.md + 모듈별 오버라이드 | Phase 1 | timeout_policy.md |
| AUX-10 | 교차 모듈 중복 미감사 | 선행작업 C 수행 | Phase 0 | cross_module_dedup.md |
| AUX-11 | 메타데이터 헤더 표준 부재 | 모든 신규 파일에 Status/Version/Last-reviewed 헤더 적용 | Phase 1 | 전 파일 헤더 |

### 6.4 LOW (2건)

| 이슈# | 문제 | 해결 | 해결 시점 | 산출물 |
|--------|------|------|----------|--------|
| AUX-12 | 한글 파일명 인코딩 | §2.3 영문 네이밍 규칙 적용 (기존 한글 파일 = 아카이브) | Phase 1 | 전 파일 영문명 |
| AUX-13 | 충돌 해결 프로토콜 없음 | §9 충돌 해결 프로토콜 정의 | Phase 0 | CONFLICT_LOG.md |

---

## 7. Phase 실행 계획

### Phase 0: 기반 확립 (선행작업)

> **목표**: 구조화 진입 전 필수 기반 완성
> **산출물 5건**

| 단계 | 작업 | 입력 | 산출물 | 이슈 해결 | 상태 |
|------|------|------|--------|----------|------|
| 0-1 | AUTHORITY_CHAIN.md 작성 | §3 권한 체계 | AUTHORITY_CHAIN.md | AUX-01 | ✅ 완료 (2026-03-29). §3.1~§3.4 전문 포함 (다이어그램 2건, 테이블 3건, LOCK 인용 10건, LOCK-AX-01~15 정합), PART2 정본 선언 2개소 삽입 |
| 0-2 | LOCK 통합 레지스트리 작성 (선행작업 A) | D2.0-01/02/06 | lock_value_registry.md | AUX-02 | ✅ 완료 (2026-03-29). 불일치 4건(D-01~D-04) 문서화, HIGH 2건은 0-5에서 CONFLICT_LOG 등재 |
| 0-3 | 상세명세 분배 매핑 검증·확정 (선행작업 B) | 상세명세.md (336줄) + §5B + §13.1 | 본 계획서 §5B (확정일 태그) + §13.3 (보강 항목 반영) | AUX-07 (매핑만, 분배는 1-2) | ✅ 완료 (2026-03-29). §5B 25행 전수 대조, 줄 회계 336=281+55 확정, 불일치 2건(I-16§4 뉴스 누락·§2 파일명) 수정, §13.3 전 모듈 E1/E9 공통 누락 + 모듈별 추가 발견 반영, Phase 2 테이블 정합 |
| 0-4 | 교차 모듈 중복 감사 (선행작업 C) | 상세명세.md + §5C + §5B | cross_module_dedup.md | AUX-10 | ✅ 완료 (2026-03-29). 시드 6건 + 추가 1건(I-5 의존성) = 총 7건 중복 그룹, 정본 배정 7/7 완료, §5B 충돌 0건 |
| 0-5 | CONFLICT_LOG.md 초기화 | §9 프로토콜 + lock_value_registry.md §5.2 | CONFLICT_LOG.md | AUX-13 | ✅ 완료 (2026-03-29). §9.1~§9.3 프로토콜 전문 반영, D-01/D-02 HIGH 2건 등재, 기존 v1.0 기록(CONF-AUX-001~003) 이관 보존 |

#### Phase 0 단계별 상세 작업 절차

<details>
<summary><b>0-1. AUTHORITY_CHAIN.md 작성</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\AUXILIARY_MODULES_구조화_종합계획서.md` §3 전체 (§3.1 기존 권한 체인 ~ §3.4 LOCK 보호 선언)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` — 정본 선언 삽입 대상 2개소:
  - V1-Phase 1 "## Week 3-4: 보조 모듈" 헤더 직후 (L1677 부근)
  - V1-Phase 6 "## V1-Phase 6: AI Investing MVP + MCP" 실행 가이드 내 (L2543 부근) — §3.2 권한 체인에 Phase 6도 포함되어 있으므로

**절차**:
1. `1-2_Auxiliary-Modules/AUTHORITY_CHAIN.md` 신규 생성
   - 본 계획서 §3.1~§3.4 내용을 독립 문서로 추출
   - 헤더: `Status: APPROVED`, `버전: v1.0`
     > ※ 거버넌스 문서이므로 L3 심사 대상이 아님. Phase 2~3 APPROVED 흐름과 별도로, 생성 즉시 APPROVED 부여
   - 포함 범위 (§3 전문):
     - §3.1 기존 VAMOS 권한 체인 (코드블록 다이어그램)
     - §3.2 Auxiliary-Modules 확장 권한 체인 (코드블록 다이어그램 + "핵심" 요약문)
     - §3.3 각 문서의 권한 범위 테이블 (6행)
     - §3.4 LOCK 보호 선언: 절대 규칙 + change_lock 보호 항목 (4건, §5A LOCK-AX 번호 없음) + LOCK-AX 레지스트리 (15건, §5A LOCK-AX-01~15 정본 번호) + 인라인 LOCK 인용문 전수 (10건)
       > ※ FR-1: 19개 = LOCK-AX-01~15 + change_lock 4건. LOCK-AX 번호는 §5A 정본을 따를 것
2. PART2에 정본 선언 추가 (2개소):
   - **(a)** V1-Phase 1 `## Week 3-4: 보조 모듈` (L1677) 헤더 직후에 아래 삽입:
     ```
     > **구현 정본**: 보조 모듈 구현 상세는 sot 2/1-2_Auxiliary-Modules/이 Single Source of Truth입니다.
     > 본 섹션은 When(Phase)+Where(코드 위치)만 기술합니다.
     ```
   - **(b)** V1-Phase 6 `### 실행 가이드` (L2545) 참조 SOT 문서 목록 말미에 아래 추가:
     ```
     > - `sot 2/1-2_Auxiliary-Modules/` (S-1 Self-check Engine 구현 상세 정본)
     ```

**검증**:
- [x] AUTHORITY_CHAIN.md에 §3.1~§3.4 전체 내용 포함 (다이어그램 2건, 테이블 3건: §3.3 권한 범위 6행 + §3.4 change_lock 4행 + §3.4 LOCK-AX 15행, LOCK 인용 10건) ✅
- [x] LOCK-AX 번호가 §5A 정본(LOCK-AX-01~15)과 정합 (FR-1 기준: 19개 = LOCK-AX-01~15 + change_lock 4건) ✅
- [x] PART2 V1-Phase 1 `## Week 3-4: 보조 모듈` 직후에 정본 선언 존재 (L1677-1679) ✅
- [x] PART2 V1-Phase 6 실행 가이드 참조 SOT에 sot 2/1-2_Auxiliary-Modules/ 추가 존재 (L2556) ✅
- [x] 정본 선언 문구가 기존 패턴과 일치 (cf. L5133 AI Investing 정본 선언 형식) ✅

> **완료**: 2026-03-29. AUTHORITY_CHAIN.md 130줄 생성 (§3.1~§3.4 전문, LOCK-AX-01~15 + change_lock 4건 = 19개, 인라인 LOCK 인용 10건). PART2 정본 선언 2개소(V1-Phase 1 L1677, V1-Phase 6 L2556) 삽입 완료.

**산출물**: `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\AUTHORITY_CHAIN.md` ✅
</details>

<details>
<summary><b>0-2. LOCK 통합 레지스트리 작성</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\AUXILIARY_MODULES_구조화_종합계획서.md` §5A (LOCK-AX-01~15 테이블) + §3.4 (change_lock 보호 항목 4건)
- `D:\VAMOS\docs\sot\D2.0-01_01. VAMOS_DESIGN_2_0_OVERVIEW.md` §5.6 (I-Series 모듈 카탈로그, change_lock 플래그)
- `D:\VAMOS\docs\sot\D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md` §7 (ORANGE CORE 모듈 상세, ResponseEnvelope/pipeline/state machine)
- `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` (Memory/VectorStore/Cache/QoD LOCK)

**절차**:
1. `06_mapping/` 폴더 사전 생성
2. `06_mapping/lock_value_registry.md` 신규 생성
   - 헤더: `Status: DRAFT`, `버전: v1.0`, `총 항목: 19건`
3. §5A의 LOCK-AX-01~LOCK-AX-15 (15건) + §3.4의 change_lock 보호 항목 (4건: 모듈 API 시그니처, I-5 Decision Engine, I-8 Policy Engine, I-19 Approval Manager) = 총 19건을 기반으로 작성
   - §5A 산출물 형식(6열 테이블: LOCK ID / 항목 / 값 / 출처 / 관련 모듈 / 비고) 준수
   - change_lock 4건은 LOCK-AX 번호 없이 별도 섹션으로 구분
   > ※ FR-1 기준: 19개 = LOCK-AX-01~15 + change_lock 4건
4. 각 LOCK 값의 D2.0 원문 위치를 정확히 기록
   - 기재 수준: 문서명 + 섹션 번호 + Decision 번호(있는 경우) (예: `D2.0-06 DEC-014`, `D2.0-02 §7.53-1`)
   - 원문 인용 시 R-02-4 형식 준수: `> LOCK (출처): [원문 그대로]`
5. LOCK 값 간 상호 의존성 표기:
   - LOCK-AX-06 alpha + (1-alpha) = 합 1.0 (RAG 비율 제약)
   - LOCK-AX-09 메모리 4계층 ↔ LOCK-AX-15 검색 우선순위 (계층 순서 = 검색 순서)
   - LOCK-AX-03 QoD 공식 → LOCK-AX-04 QoD 임계값 (공식 결과에 임계값 적용)
   - LOCK-AX-03 가중치 합 = 1.0 (0.30+0.25+0.20+0.15+0.10, 5-factor)

**검증**:
- [x] 19개 LOCK 항목 전수 등재 (LOCK-AX 15건 + change_lock 4건)
- [x] 각 항목에 출처 문서 + 섹션/Decision 번호 기재
- [x] 원문과 값 일치 교차 확인 (D2.0 원문 대조) — 불일치 4건(D-01~D-04) 문서화
- [x] §5A 테이블 형식(6열) 준수 확인
- [x] R-02-4 LOCK 인라인 인용 형식(`> LOCK (출처): [원문]`) 준수 확인 — 14건
- [x] 0-1 산출물(AUTHORITY_CHAIN.md §3.4 테이블 19행)과 항목 정합성 확인

> **완료**: 2026-03-29. 추가 발견: LOCK-AX-03 QoD 5-factor 갱신(D-02, V1-006), LOCK-AX-02 출처 부재(D-01) → 종합계획서 §5A/§3.4 동시 수정 완료. HIGH 2건은 0-5 CONFLICT_LOG.md에서 등재 예정.

**산출물**: `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\06_mapping\lock_value_registry.md` ✅
</details>

<details>
<summary><b>0-3. 상세명세 분배 매핑 확정</b></summary>

> **역할**: 선행작업 B의 실행 단계. §5B 매핑 테이블을 상세명세.md 원본 대조로 검증·확정한다.
> **AUX-07 관계**: 0-3은 AUX-07의 **매핑 확정**만 수행. 실제 분배는 Phase 1 (1-2)에서 수행.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\AUXILIARY_MODULES_상세명세.md` (336줄, I-4/I-13/I-14/I-16/S-1 + 개요 + 공통 SOT 참조)
- 본 계획서 §5B 매핑 테이블 (분배 대상 25행 + 분배 제외 줄 회계)
- 본 계획서 §13.1 L3 정의 (9 요소: E1~E9) — L2→L3 판정 기준

**절차**:
1. **§5B 매핑 대조 검증**: 상세명세.md의 각 섹션(I-4 §1~§4, I-13 §1~§4, I-14 §1~§3, I-16 §1~§5, S-1 §1~§5)이 §5B 테이블 25개 행과 1:1 대응하는지 확인
   - 각 행의 "내용 요약"과 상세명세.md 원문이 일치하는지 대조
   - 분배 대상 폴더/파일명이 §2.3 네이밍 규칙에 부합하는지 확인
2. **비콘텐츠 줄 회계 검증**: §5B "분배 제외 줄 회계" 테이블의 줄 범위·줄 수가 상세명세.md 실물과 일치하는지 확인
   - 분배 대상(281줄) + 분배 제외(55줄) = 336줄 총합 검증
   - 미지정(어느 카테고리에도 속하지 않는) 줄 = 0 확인
3. **정본 소유자 매핑 확인**: §5B 25개 행에서 동일 콘텐츠가 2개 이상 파일에 중복 배정되지 않았는지 확인
   - 기본 규칙: 1섹션 → 1파일 (1:1 매핑)
   - 예외 N:1 (병합): I-16 §2/§5 → search_pipeline.md (2섹션 → 1파일, 랭킹은 파이프라인 최종 단계)
   - 예외 1:N (분할): I-13 §2 → text_renderer.md ~ image_renderer.md (1섹션 → 최대 7개 렌더러 파일, 렌더러별 분리). 분할 시 원본 테이블 행과 대상 파일의 대응 관계 명시 필요
4. **L2→L3 보강 필요 여부 판정**: 각 분배 대상 파일에 대해 §13.1 L3 정의(E1~E9)를 기준으로 현재 수준 판정
   - §13.3 모듈별 L3 승급 로드맵과 대조하여 일관성 확인
   - 신규 발견 보강 항목이 있으면 §13.3 테이블에 추가
5. **보강 필요 항목 이관**: L3 미달 항목 목록을 **§13.3 모듈별 L3 승급 로드맵 테이블**에 반영 (Phase 2 작업으로 이관)
   - §7 Phase 2 테이블(2-1~2-5)의 "상세" 열과 정합성 확인

**검증**:
- [x] 상세명세.md 336줄 전수 회계 완료 (분배 대상 281줄 + 분배 제외 55줄 = 336줄, 미지정 0줄) ✅
- [x] §5B 25개 행 전수 원문 대조 완료 (불일치 2건 수정: I-16§4 뉴스 누락 추가, I-16§2/§5 ranking_algorithm→search_pipeline 개명) ✅
- [x] 정본 소유자 매핑 확인 (중복 배정 0건. 예외: I-16 §2/§5 N:1 병합, I-13 §2 1:N 분할) ✅
- [x] L3 보강 항목 → §13.3 로드맵 반영 완료 (전 모듈 E1/E9 공통 추가 + 모듈별 E3/E4/E5/E6/E8 추가, I-16 작업량 소→중 상향) ✅
- [x] §13.3과 Phase 2 테이블(2-1~2-5) 정합성 확인 (E ID 기반 상세 열 전면 갱신) ✅

**산출물**:
- 본 계획서 §5B 매핑 테이블: 검증 완료 (인라인 수정, `확정일: 2026-03-29` 태그 기입 완료) ✅
- 본 계획서 §13.3 L3 승급 로드맵: 전 모듈 E1/E9 공통 + 모듈별 추가 보강 항목 반영 완료 ✅

> **완료**: 2026-03-29. §5B "산출물" 행에 `확정일: 2026-03-29` 기입 완료. Phase 전환 게이트 통과 조건 충족.
>
> **실행 결과 요약**:
> - §5B 25행 전수 원문 대조 → 불일치 2건 수정 (I-16§4 뉴스 누락 추가, I-16§2/§5 ranking_algorithm→search_pipeline 개명)
> - 줄 회계 336 = 281(분배) + 55(제외) 정확값 확정, 구분선/빈줄 줄 범위 13개소 명시
> - 정본 소유자 중복 배정 0건 (N:1 I-16§2/§5, 1:N I-13§2 예외 확인)
> - L3 판정: 전 모듈 E1(목적)/E9(의존성) 공통 누락 발견 + I-13 E3, I-14 E4, I-16 E5/E6, S-1 E4/E6/E8 추가 → §13.3 반영
> - Phase 2 테이블(2-1~2-5) E ID 기반 전면 갱신, §13.3과 정합 달성
</details>

<details>
<summary><b>0-4. 교차 모듈 중복 감사</b></summary>

> **선행 조건**: 0-3 완료 (§5B 매핑 확정, `확정일` 태그 존재)
> **AUX-10 해결**: 교차 모듈 중복 미감사

**입력 파일**:
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\AUXILIARY_MODULES_상세명세.md` (5개 모듈 I/O 스키마)
- 본 계획서 §5C (예상 중복 영역 — 시드 6건: 임베딩 생성, 메모리 Layer, QoD 점수, fallback chain, ResponseEnvelope, 타임아웃)
- 본 계획서 §5B (확정된 정본 소유자 매핑 25행)

**절차**:
1. **톱다운 시드 로드**: §5C 예상 중복 영역 테이블 6건을 기준선으로 로드 (개념, 등장 모듈, 정본 소유자)
2. **바텀업 키워드 탐색**: 상세명세.md에서 5개 모듈(I-4, I-13, I-14, I-16, S-1)의 개념/기능 키워드 추출
3. **중복 후보 통합**: 시드 6건 + 바텀업 탐색 결과를 통합하여, 2개 이상 모듈에 등장하는 키워드 그룹 = 최종 중복 그룹 확정
4. **정본 소유자 결정**: 각 중복 그룹에 정본 소유자 배정. §5B 확정 매핑(25행)과 정합성 확인 — 충돌 시 §5B 우선
5. **산출물 작성**: 결과를 `06_mapping/cross_module_dedup.md`에 기록

**산출물 구조**:
```markdown
# 교차 모듈 중복 감사 결과
> **Status**: DRAFT
> **버전**: v1.0
> **작성일**: YYYY-MM-DD
> **선행 작업**: 0-3 (§5B 확정일: 2026-03-29)

## 중복 그룹 목록
| # | 개념 | 등장 모듈 | 정본 소유자 (파일) | §5B 정합 | 비고 |
|---|------|----------|-------------------|---------|------|

## 시드 외 추가 발견
| # | 개념 | 등장 모듈 | 정본 소유자 (파일) | 발견 근거 |
|---|------|----------|-------------------|----------|
```

**검증**:
- [x] 5개 모듈 전수 스캔 확인 (I-4, I-13, I-14, I-16, S-1) ✅
- [x] §5C 시드 6건 전수 포함 확인 (중복 그룹 ≥ 6건) — DG-01~DG-06 + DG-07 = 총 7건 ✅
- [x] 중복 그룹 전부 정본 소유자 배정 완료 — 7/7 (100%) ✅
- [x] 정본 소유자 ↔ §5B 매핑(25행) 정합 확인 — 충돌 0건 ✅
- [x] cross_module_dedup.md 파일 존재 확인 (Phase 전환 게이트 조건) ✅

> **완료**: 2026-03-29.
>
> **실행 결과 요약**:
> - 톱다운(§5C 시드 6건) + 바텀업(상세명세.md 전수 키워드 추출) 병행 수행
> - 시드 6건 전수 확인 + 추가 발견 1건(DG-07: I-5 Decision Engine 의존성 — I-13, I-14) = 총 7건
> - 정본 유형 분포: 00_common 3건(DG-04/05/06), 모듈 정본 3건(DG-01 I-16, DG-02 I-14, DG-03 S-1), 06_mapping 1건(DG-07)
> - §5B 25행 교차 검증: DG-03만 직접 매핑 일치(S-1 §1→qod_formula.md), 나머지 6건은 §2.1 신규 파일로 충돌 불가
> - Phase 1 이행 사항 7건 정리 (1-2 분배 시 참조 방향 명시, 1-4 00_common 작성, 1-7 인터페이스 계약)

**산출물**: `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\06_mapping\cross_module_dedup.md` ✅
</details>

<details>
<summary><b>0-5. CONFLICT_LOG.md 초기화</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\AUXILIARY_MODULES_구조화_종합계획서.md` §9.1 (충돌 유형별 해결) + §9.2 (충돌 해결 절차) + §9.3 (충돌 방지 규칙)
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\06_mapping\lock_value_registry.md` §5.2 (불일치 사항 D-01~D-04 중 **HIGH 2건**: D-01, D-02)

**절차**:
1. `1-2_Auxiliary-Modules/CONFLICT_LOG.md` 신규 생성
2. 파일 구조:
   ```markdown
   # AUXILIARY MODULES 충돌 기록부
   > **Status**: ACTIVE
   > **버전**: v1.0
   > **생성일**: 2026-03-29

   ## 충돌 해결 프로토콜 (§9.1~§9.3 발췌)
   [본 계획서 §9.1 충돌 유형별 해결 테이블 + §9.2 충돌 해결 절차 플로우 + §9.3 충돌 방지 규칙 테이블을 전문 복사]
   (§9.4 횡단 관심사 참조는 제외 — 운영 단계에서 필요 시 추가)

   ## 충돌 기록
   | # | 날짜 | 충돌 유형 (§9.1 기준) | 파일 A | 파일 B | 내용 | 판정 | 권장 조치 | 조치 완료 |
   |---|------|----------------------|--------|--------|------|------|----------|----------|
   | (아래 절차 3에서 D-01, D-02 등재) |
   ```
3. **0-2 산출물(lock_value_registry.md §5.2)에서 HIGH 불일치 2건을 초기 충돌로 등재** — 아래 테이블 행 값을 그대로 기입:

   | # | 날짜 | 충돌 유형 (§9.1 기준) | 파일 A | 파일 B | 내용 | 판정 | 권장 조치 | 조치 완료 |
   |---|------|----------------------|--------|--------|------|------|----------|----------|
   | D-01 | 2026-03-29 | **LOCK 충돌** (LOCK-AX-02 출처·값이 종합계획서 내부에서 불일치 + D2.0 원문 부재) | 종합계획서 §5A (출처: D2.0-01 §4, 값: "하위→상위 금지") | 종합계획서 §3.4 (출처: D2.0-02 §7, 값: "lower layers → higher layers") | 양 D2.0 원문에서 "의존성 방향" 정확한 문구 **완전 부재**. D2.0-01 §4는 문서/용어/이벤트 규칙만, D2.0-02 §7 DEPENDENCIES는 기능 의존만 기술. 값 텍스트도 한글 vs 영문 불일치. AUTHORITY_CHAIN.md는 §5A를 따라 "D2.0-01 §4" 기재 | **수동 판정 필요** — §9.1 LOCK 충돌 해결 방법은 "sot 2/ 파일 즉시 수정"이나, LOCK 값의 D2.0 원문 자체가 부재하여 수정 대상 확정 불가. §9.2 절차 3 수동 판정 경로 → 상위 권한자(프로젝트 오너) 에스컬레이션 | D2.0-01 또는 D2.0-02에 "의존성 방향" LOCK 명시적 선언 추가 요청 + §5A/§3.4 출처 통일 | — |
   | D-02 | 2026-03-29 | **D2.0 간 충돌** (확장 적용: D2.0-06 DEC-014 vs 상위 계층 PLAN-3.0 §1.X. §9.1 "D2.0 간 충돌" 판정 기준 준용 — 엄밀히는 D2.0 상호 간이 아닌 PLAN-3.0↔D2.0 계층 간 불일치) | D2.0-06 DEC-014 (4-factor: relevance/accuracy/freshness/completeness) | PLAN-3.0 §1.X (5-factor: Accuracy/Relevance/Completeness/Safety/Efficiency) | PLAN-3.0 > D2.0 권한이므로 5-factor가 정본 (V1-006). **갱신 완료**: 종합계획서 §5A/§3.4, AUTHORITY_CHAIN.md, lock_value_registry.md. **미갱신**: D2.0-06 DEC-014, MASTER_SPEC §8.8 | **상위 권한자 판정 필요** — §9.1 D2.0 간 충돌 해결 방법 "상위 권한자 판정" 적용. 판정 기준(최신 우선 + LOCK 우선) 상 PLAN-3.0 5-factor가 정본. sot 2/ 내부는 선조치 완료, 외부 문서(D2.0-06·MASTER_SPEC) 갱신은 프로젝트 오너 판정 대기 | D2.0-06 DEC-014 갱신 + MASTER_SPEC §8.8 QoD 절 통일. V1-006 이슈로 추적 중 | sot 2/ 내부 선조치 완료 (2026-03-29). 외부 문서 미완 — 프로젝트 오너 판정 대기 |

4. **LOW 불일치(D-03, D-04) 비등재 사유**: D-03(LOCK-AX-14 복합 출처, LOW)은 lock_value_registry.md에서 복합 출처로 기록 완료하여 추가 조치 불요. D-04(LOCK-AX-09 명칭 차이, LOW)는 구조 일치·약칭만 다름으로 구현 시 D2.0-06 원문 명칭 우선 사용 권장으로 lock_value_registry.md에 기재 완료. 양건 모두 충돌이 아닌 **기록 사항**이므로 CONFLICT_LOG 등재 대상 아님. 향후 구현 단계에서 실질 충돌 발생 시 등재.

**검증**:
- [x] CONFLICT_LOG.md 파일 존재 (66줄, v2.0) ✅
- [x] 프로토콜 섹션에 §9.1 충돌 유형별 해결 테이블(5행) + §9.2 절차 플로우 + §9.3 방지 규칙(4행)이 전문 포함 ✅
- [x] D-01 행: 충돌 유형 = "LOCK 충돌", 판정 = "수동 판정 필요", 권장 조치 기재 ✅
- [x] D-02 행: 충돌 유형 = "D2.0 간 충돌 (확장 적용)", 판정 = "상위 권한자 판정 필요", 권장 조치 + 조치 완료(sot 2/ 내부 선조치 + 외부 대기) 기재 ✅
- [x] 테이블 컬럼 9개 (#, 날짜, 충돌 유형, 파일 A, 파일 B, 내용, 판정, 권장 조치, 조치 완료) 정합 ✅
- [x] D-03, D-04는 비등재 (절차 4 사유 확인) ✅

> **완료**: 2026-03-29. CONFLICT_LOG.md v2.0 (66줄). §9.1~§9.3 프로토콜 전문 반영, D-01/D-02 HIGH 2건 초기 등재 (9컬럼 테이블), 기존 v1.0 기록(CONF-AUX-001~003) 이관 보존.

**산출물**: `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\CONFLICT_LOG.md` ✅
</details>

---

### Phase 1: 구조 재편 + 콘텐츠 분배 ✅ 완료 (10/10, 2026-04-07)

> **목표**: 폴더 생성 → 상세명세 분배 → 메타데이터 표준화 → 인터페이스 정의
> **산출물: 전체 폴더 구조 + INDEX.md + 40+ 파일**
> **결과**: 9 폴더 + 56 파일 (INDEX.md §9 합계 = 디스크 실측 = part2_reference_table.md §2.2 모두 일치) + Part2 상태 PARTIAL → COMPLETE
> **전환 게이트**: ✅ 폴더 구조 완성 + ✅ 56 파일 (≥40) + ✅ 전 파일 헤더 보유 + ✅ part2_reference_table.md UNMAPPED 0건
>
> **단계별 결과 요약** (10/10 ✅):
>
> | 단계 | 산출물 | 핵심 결과 |
> |---|---|---|
> | 1-1 | 9 폴더 (00~06 + _archive + _templates) | R1 깊이/명명 검증 통과 |
> | 1-2 | 30 분배 파일 | §5B 25행 1:1 + I-13 §2 1:N 7행, 281줄 회계 일치 |
> | 1-3 | 35 파일 6필드 헤더 | LOCK-AX-NN 형식 통일 |
> | 1-4 | 00_common 4 파일 | response_envelope LOCK-AX-11 nested 정본 |
> | 1-5 | 5 fallback_chain.md | 22 F-XXX-NN ID, timeout_policy 정본 정합 |
> | 1-6 | module_dependency_graph.md v1.1 | 노드 14 / 엣지 19 / cycle 0 |
> | 1-7 | interface_contracts.md v1.1 | 14 계약 C-01~C-14, 19 엣지 전수 매핑 |
> | 1-8 | INDEX.md (master) + 7 _index.md | 56 파일 등재, broken 0건 |
> | 1-9 | _archive/ + redirect | byte-identical 보존, 4중 ARCHIVED 표시 |
> | 1-10 | part2_reference_table.md v1.2 | 정방향 19건 + 역방향 56 파일, UNMAPPED 0 |
>
> **이슈 해결**: AUX-03 (CRITICAL) ✅ / AUX-04 (HIGH) ✅ / AUX-05 (HIGH) ✅ / AUX-06 (HIGH) ✅ / AUX-07 (HIGH) ✅ / AUX-08 (MEDIUM) ✅ / AUX-09 (MEDIUM) ✅ / AUX-11 (LOW) ✅ / AUX-12 (LOW) ✅
>
> **이월 항목 (F-01~F-11, Phase 2 또는 D2.0 갱신 작업)**: ① F-01 CONFLICT_LOG 등재 (X-2/X-3/X-4/X-5) ② F-02/F-03 종합계획서 §B.5 + D2.0-06 DEC-014 + MASTER_SPEC §8.8 5-factor 갱신 ③ F-04 timeout_policy 표 확장 ④ F-05 S-1↔I-15 통합 결정 ⑥ F-08/F-09 1-7 ↔ 모듈 폴더 역참조 ⑦ F-10 fallback ID D2.0-02 §6.3 등재 ⑧ F-11 §2.1 트리 vs 디스크 7건 차이

| 단계 | 작업 | 상세 | 이슈 해결 | 완료 |
|------|------|------|----------|------|
| 1-1 | 폴더 구조 생성 | §2.1 트리 기반 00~06 폴더 생성 | AUX-04 | ✅ 완료. 9개 폴더 생성 (00_common ~ 06_mapping + _archive + _templates), 폴더 깊이/명명 검증 통과 |
| 1-2 | 상세명세 분배 | §5B 매핑에 따라 상세명세.md를 서브폴더 파일로 분배 | AUX-03, AUX-07 | ✅ 완료 (2026-04-07). 30개 분배 파일 생성, §5B 25행 1:1 매핑 + I-13 §2 1:N 분할 7행. 281줄 회계 일치 (256 substantive + 25 structural blanks), 누락 0건. 재검증 시 3종 이슈 정정 (모듈 preamble 20줄 추가, 표 헤더 중복 12줄 제거, 인용 줄 범위 5건 정정) |
| 1-3 | 메타데이터 헤더 표준화 | 모든 파일에 Status/Version/Last-reviewed 헤더 추가 | AUX-11 | ✅ 완료 (2026-04-07). 1-2 분배 파일 35건 (5 _index + 30 distribution) 100% 표준 6필드 (버전/Status/작성일/Last-reviewed/모듈/LOCK 참조) 적용, 전부 Status: DRAFT. LOCK 참조 LOCK-AX-NN 형식 통일 (AUTHORITY_CHAIN.md §5A 정본 정합). 재검증 1회로 30개 분배 파일 4필드 누락 발견 후 보완. Out-of-scope 6건 (06_mapping/2, governance/3, 입력 소스/1) 의도적 미수정 |
| 1-4 | 00_common 공통 파일 작성 | response_envelope.md, common_types.md, error_taxonomy.md, timeout_policy.md | AUX-09 | ✅ 완료 (2026-04-07). 4개 파일 생성. ResponseEnvelope LOCK-AX-11 (D2.0-02 §5.1.1) nested 구조 정본 채택, 계획서의 dataclass 표현은 §3 보조표현(Non-LOCK)으로 분리. SoT 교차검증으로 계획서 §7 인용 오류 식별 및 정정 명시. common_types에 Modality/ConfidenceScore/QoD(LOCK-AX-03 5-factor)/Entity/EvidenceItem/MemoryCandidate/PipelineStage(LOCK-AX-13) 카탈로그화. error_taxonomy AUX-E001~E010 + 재시도 매트릭스 + LogEvent 매핑. timeout_policy 11개 호출 유형 + 폴백/백오프 규칙. 재검증 1회로 LOCK-AX-12/13 매핑 오류 4건 발견·정정 (Modality/QoD 잘못된 LOCK 참조 → AX-03/04/13으로 교정) |
| 1-5 | fallback_chain.md 작성 (5건) | 각 모듈별 fallback chain 정의 | AUX-08 | ✅ 완료 (2026-04-07). 5개 모듈 fallback_chain.md 작성 (I-4/I-13/I-14/I-16/S-1), 총 22개 고유 실패 지점(F-XXX-NN ID 부여). 재검증 1회로 정본 정합 v1.1 확정 — 초안의 임의 timeout/재시도 값을 timeout_policy.md §2 정본 표로 교체, error_taxonomy.md AUX-E003/E005/E006/E007 매핑 추가, ResponseEnvelope 정본 필드(`audit.failure_codes`/`fallback_ids`/`event_ids`) 사용. S-1만 §3.1 모듈별 오버라이드 신설 (Prometheus pull 5s/2/1s, I-25 SDAR 트리거 10s/2/2s — timeout_policy 정본 표 미매핑 호출). V-09 검증(5건+각 3개+) 통과. 이월: F-XXX-NN ID는 추후 D2.0-02 §6.3 Fallback Registry 등재 필요 |
| 1-6 | 모듈 의존성 그래프 작성 | 06_mapping/module_dependency_graph.md | AUX-05 | ✅ 완료 (2026-04-07, v1.1). 부록 §A.1~A.4를 Mermaid `graph TD`로 정규 이관. 노드 14 (CORE 1 + AUX 5 + 외부 8) / 엣지 19 (실선 14 + 점선 5). 위상 정렬 L0~L5, in-degree 합=19, DFS 백엣지 0건 → cycle 0건 (§A.4 정합). 재검증 1회로 v1.0 결함 8건 정정: ① I-4→I-16 embedding 누락 추가 ② QoD 방향 정정(§A.1 ASCII 채택, S-1→I-14) ③ 추론 엣지 CORE→I-14 제거 ④ I-19 점선 3→5건 확장(§A.3 "전체 → I-19") ⑤ Layer 분배 재계산 ⑥ 엣지 수 16→19 정정 ⑦ Mermaid `-->|"label"|` 표준화 ⑧ §6 SoT 교차검증 섹션 신설. 이월: §6.1 HIGH 라벨 충돌 3건(I-2/I-6/I-20) → CONFLICT_LOG, §6.2 MEDIUM S-1↔I-15 누락 → 1-7 |
| 1-7 | 인터페이스 계약서 작성 | 06_mapping/interface_contracts.md | AUX-06 | ✅ 완료 (2026-04-07, v1.1). 14건 계약 (C-01~C-14) 정의, 1-6 v1.1 19 엣지 (실선 14 + 점선 5) 전수 매핑, 누락 0건 (C-07=2엣지·C-14=5엣지 복합). 5-stage 그룹화 (Perception/Reasoning/Action/Memory/Reflection) + LOCK-AX-12/13 직교성 명시. 각 계약 입력/출력(LOCK-AX-11 envelope)/에러(AUX-Exxx)/SLA(timeout_policy §2 매핑) 4항목 포함. LOCK 인용 14종(LOCK-AX-01/03/04/05/06/07/08/09/10/11/12/13/14/15) 정식 번호 통일. 재검증 1회로 v1.0 결함 9건 정정: ① §B.6 보조표현 → response_envelope.md LOCK 정본 교체 ② S0~S8 잘못된 모듈 1:1 매핑 제거 ③ C-03 방향 반전 (I-4→I-16 data) ④ **QoD 4-factor → LOCK-AX-03 PLAN-3.0 5-factor** ⑤ LOCK-AX 정식 번호 통일 ⑥ Modality 대문자 enum ⑦ 엣지 14→19 정정 ⑧ X-1/X-5 SoT finding 추가 ⑨ timeout_policy §2 미수록 호출 PENDING 명시. 이월: §6.2 X-1~X-7 (HIGH 4 + MED 1 + LOW 2) → CONFLICT_LOG / §B.5 5-factor 갱신 / D2.0-06 DEC-014 갱신 / I-15 통합 결정 / timeout_policy 표 확장 (F-01~F-10 후속) |
| 1-8 | INDEX.md 작성 | 마스터 인덱스 + 폴더별 _index.md | — | ✅ 완료 (2026-04-07, v1.0). 마스터 INDEX.md 신규 작성(61 .md 링크, 55 파일 전수 등재) + 00_common/06_mapping `_index.md` 신규 2건 + 01~05 `_index.md` 5건 파일 목록 갱신(stub "Phase 1에서 추가 예정" → 실제 파일 표). 디스크 .md 55건 = INDEX.md 등재 55건(루트 5 + 00_common 5 + 01:9 + 02:12 + 03:6 + 04:6 + 05:7 + 06:5). 7개 _index.md 합계 링크 55, broken 0건. Status 헤더 전수 보유(legacy `상세명세.md` 1건만 미보유, 1-9 아카이브 예정). 재검증 1회로 명명 불일치 3건 정정: ① 01 input_schema MultimodalInput/InterpretedContent → **RawInput/InterpretedInput** ② 03 input_output_schema SummarizationRequest/Result → **SummarizeRequest/SummaryResult** ③ 04 search_api SearchRequest/SearchResult → **`KnowledgeSearchEngine`/SearchQuery/SearchResults**. 이월: §2.1 폴더 트리 vs 디스크 차이 7건(`memory_layer_integration`/`semantic_cache`/`embedding_model`/`vectorstore_adapter`/`qod_thresholds`/`self_check_thresholds` 부재, 디스크엔 §2.1 미등재 `audio/image/diagram_renderer` 3건 추가) → 1-2 분배 결정 기인, F-11 신규 등재 권고 |
| 1-9 | 상세명세.md 아카이브 | 원본을 _archive/로 이동, 읽기 전용 | AUX-07 | ✅ 완료 (2026-04-07). 원본을 `_archive/AUXILIARY_MODULES_상세명세_v1.0_archived.md` (10780 B / 336 lines) 로 byte-identical 이동, 루트에 redirect 게시(72 lines), `_archive/README.md` sidecar 신설, INDEX.md 루트 정본 표 갱신. ARCHIVED 4중 표시 (폴더/파일명 접미사/sidecar/redirect frontmatter). 47개 sibling 파일의 줄 인용 그대로 유효 (provenance 무결). 재검증 3차로 모듈 ID 오기 정정 (`I-5/I-6/I-7/I-8` → `I-4/I-13/I-14/I-16/S-1`). §7 검증 4/4 PASS |
| 1-10 | PART2 링크 테이블 추가 | PART2 V1-Phase 1에 sot 2/ 참조 테이블 추가 | AUX-03 | ✅ 완료 (2026-04-07, v1.2 재검증 완료). `06_mapping/part2_reference_table.md` 신설 + 2회 재검증. **정방향 19건** (D2.0-01 §5.6/§5.7 6 + D2.0-02 §2.1·§2.2·§5.1.1·§7.53-1 4 + §7.31~7.40·§7.51~7.53-2·§7.72~7.74·§7.75~7.77·§7.81~7.83·D2.0-08 §6 5 + D2.0-06 §2·§4·§4.7·DEC-005·DEC-014 4) + **역방향 56 파일** (루트 5 + 00_common 5 + I-4 9 + I-13 12 + I-14 6 + I-16 6 + S-1 7 + 06_mapping 6, INDEX.md §9 합계 일치). UNMAPPED 0건, §5B 25행 1:1 + I-13 §2 1:N 7행 전수 커버. SoT crosscheck 6건 (C-01~C-06) 등재. R8 단일 테이블, 모든 PART1 sub-section 라인 번호 인용(D2.0-01 L613~649 / D2.0-02 L227·307·717·872·1815 / D2.0-06 L80·117·206·303·635·738·776·1325·1479) |

#### Phase 1 실행 순서 의존성

```
1-1 (폴더 생성) ─── 선행 없음
  ├→ 1-2 (상세명세 분배) ─── 1-1 필요
  │    ├→ 1-3 (메타데이터) ─── 1-2 이후
  │    ├→ 1-8 (INDEX.md) ─── 1-2 완료 후
  │    └→ 1-9 (아카이브) ─── 1-2 완료 후
  ├→ 1-4 (공통 파일) ─── 1-1 필요
  ├→ 1-5 (fallback) ─── 1-2 이후 (대상 파일 존재 필요)
  ├→ 1-6 (의존성 그래프) ─── 1-1 필요
  ├→ 1-7 (인터페이스 계약) ─── 1-2 이후
  └→ 1-10 (PART2 링크) ─── 1-2 완료 후
```

#### Phase 1 단계별 상세 작업 절차

<details>
<summary><b>1-1. 폴더 구조 생성</b></summary>

**대조 기준**:
- §7 세부 작업: 1-1 "폴더 구조 생성"
- §7 전환 게이트: 폴더 구조 완성 + 40+ 파일 존재 + 전 파일 헤더 보유
- §6 이슈: AUX-04 (Phase 1 해결), AUX-12 (LOW, Phase 1 — 영문 파일명 규칙 적용)

**목표**: §2.1 트리 기반으로 `1-2_Auxiliary-Modules/` 하위 00~06 + _archive + _templates 총 9개 폴더를 생성하고, 폴더 깊이 및 명명 규칙을 검증한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\AUXILIARY_MODULES_구조화_종합계획서.md` §2.1 폴더 트리

**절차**:
1. 아래 폴더를 순서대로 생성 (총 9개 폴더):
   ```
   1-2_Auxiliary-Modules/
   ├── _archive/
   ├── _templates/
   ├── 00_common/
   ├── 01_multimodal-interpreter/
   ├── 02_multimodal-renderer/
   ├── 03_summarizer/
   ├── 04_knowledge-search/
   ├── 05_self-check/
   └── 06_mapping/
   ```
2. 폴더 깊이 검증: 최대 3단계 확인 (R1 규칙)
3. 폴더명 검증: 전부 영문 소문자 + 하이픈/언더스코어

**검증**:
- [x] 9개 폴더 전수 존재
- [x] 3단계 이상 폴더 0건
- [x] 한글/대문자 폴더명 0건

> **완료**: 2026-04-07. 9개 폴더 전수 생성 완료, R1 폴더 깊이/명명 규칙 검증 통과.
>
> **실행 결과 요약**:
> - §2.1 트리 기반 9개 폴더 생성: `00_common`, `01_multimodal-interpreter`, `02_multimodal-renderer`, `03_summarizer`, `04_knowledge-search`, `05_self-check`, `06_mapping`, `_archive`, `_templates`
> - 폴더 깊이 검증: 최대 2단계 (R1 "≤3단계" 충족)
> - 폴더명 검증: 전부 영문 소문자 + 하이픈/언더스코어 (한글/대문자 0건, AUX-12 LOW 해소)
> - AUX-04 (폴더 구조 미정의) 해결, Phase 1 후속 작업 1-2~1-10의 작업 공간 확보

**산출물**: `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\` 하위 9개 폴더 (00_common ~ 06_mapping, _archive, _templates) ✅
</details>

<details>
<summary><b>1-2. 상세명세 분배</b></summary>

**대조 기준**:
- §7 세부 작업: 1-2 "상세명세 분배"
- §7 전환 게이트: 폴더 구조 완성 + 40+ 파일 존재 + 전 파일 헤더 보유
- §6 이슈: AUX-03 (Phase 1 해결, CRITICAL), AUX-07 (Phase 1 해결)

**목표**: §5B 매핑에 따라 `AUXILIARY_MODULES_상세명세.md`의 각 섹션을 5개 모듈 서브폴더 파일로 분배하고, 원본 줄수 = 분배 후 줄수 합계를 보장한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\AUXILIARY_MODULES_상세명세.md` 전문
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\AUXILIARY_MODULES_구조화_종합계획서.md` §5B 분배 매핑

**절차**:
1. §5B 매핑 테이블에 따라 상세명세.md의 각 섹션을 대상 파일로 복사
2. 각 파일에 L3 템플릿 헤더 적용
3. 분배 전/후 내용 대조: 원본 줄수 = 분배 후 파일 내 줄수 합계 (누락 0건)

**I-4 분배 예시**:
```
01_multimodal-interpreter/
├── _index.md                    ← I-4 개요 + 파일 목록
├── input_schema.md              ← §1 입출력 스키마 (RawInput, InterpretedInput)
├── format_detection.md          ← §2 MIME 타입 감지 분기 로직
├── text_pipeline.md             ← §3 텍스트 (langdetect, chardet, tiktoken)
├── image_pipeline.md            ← §3 이미지 (PIL, CLIP, OCR)
├── audio_pipeline.md            ← §3 음성 (Whisper, Deepgram, VAD)
├── document_pipeline.md         ← §3 문서 (docling, python-docx)
├── vision_api_integration.md    ← §4 Vision API 라우팅
└── fallback_chain.md            ← 신규: 실패 대체 경로
```

**검증**:
- [x] 5개 모듈 × 분배 파일 = 전 파일 생성 완료 (30개 분배 파일, §5B 25행 1:1 매핑 + I-13 §2 1:N 분할 7행) ✅
- [x] 원본 336줄 중 분배 대상 281줄 전수 분배 (256 substantive 콘텐츠 + 25 structural blanks, 누락 0줄, 분배 제외 55줄은 §5B 줄 회계 참조) ✅

> **완료**: 2026-04-07. 30개 분배 파일 생성, §5B 25행 전수 커버, 원본 콘텐츠 verbatim 보존.
>
> **실행 결과 요약**:
> - 분배 파일 30개 = I-4(7) + I-13(10, §2 1:N 분할 7행 포함) + I-14(4) + I-16(4) + S-1(5)
> - §5B 25행 1:1 매핑 + I-13 §2 1:N 분할 7행 정합 확인, 충돌 0건
> - 줄 회계: 원본 336줄 = 분배 281줄(256 substantive + 25 structural blanks) + 제외 55줄, 누락 0줄
> - 재검증 1회로 3종 이슈 정정: ① 모듈 preamble 20줄 누락 → 5개 첫 §1 파일에 추가 ② I-13 §2 1:N 분할 시 표 헤더 12줄 중복 → text_renderer.md 단일 보존 ③ 인용 줄 범위 5건 오류 정정
> - 전 파일 §13.4 L3 템플릿 헤더 적용 (`# 모듈 - 기능` + 버전 v1.0 + Status DRAFT + L3 판정 PENDING)
> - AUX-03 (CRITICAL, 분배 미수행)/AUX-07 (원본 단일 파일 의존) 해결

**산출물**:
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\01_multimodal-interpreter\` (7 파일: input_schema, format_detection, text/image/audio/document_pipeline, vision_api_integration)
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\02_multimodal-renderer\` (10 파일: renderer_interface, text/chart/code/table/diagram/audio/image_renderer, composite_output, quality_validation)
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\03_summarizer\` (4 파일: input_output_schema, conversation_summary, memory_distillation, trigger_conditions)
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\04_knowledge-search\` (4 파일: search_api, search_pipeline ←§2+§5 병합, rag_integration, external_sources)
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\05_self-check\` (5 파일: qod_formula, evaluation_window, anomaly_detection, sdar_trigger, prometheus_metrics)
- 분배 파일 합계: **30개** (1-4 00_common 4개 + 1-5 fallback_chain 5개 + 1-6/1-7 mapping 2개 + 기존 _index.md 5개 합산 시 §7 전환 게이트 "40+ 파일" 충족 가능)
</details>

<details>
<summary><b>1-3. 메타데이터 헤더 표준화</b></summary>

**대조 기준**:
- §7 세부 작업: 1-3 "메타데이터 헤더 표준화"
- §7 전환 게이트: 폴더 구조 완성 + 40+ 파일 존재 + 전 파일 헤더 보유 (grep Status:)
- §6 이슈: AUX-11 (Phase 1 해결)

**목표**: 1-2에서 생성된 전 파일에 Status/Version/Last-reviewed 표준 메타데이터 헤더를 추가하여, `grep Status:` 검색 시 누락 0건을 달성한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\01_multimodal-interpreter\` ~ `05_self-check\` 하위 전체 분배 파일 (1-2 산출물)

**절차**:
1. 모든 파일에 아래 표준 헤더 추가:
   ```markdown
   # [모듈명/기능명]
   > **버전**: v1.0
   > **Status**: DRAFT
   > **작성일**: 2026-03-22
   > **Last-reviewed**: 2026-03-22
   > **모듈**: I-4 | I-13 | I-14 | I-16 | S-1
   > **LOCK 참조**: [해당 LOCK ID 목록]
   ```

**검증**:
- [x] 전 파일에서 `Status:` 검색 → 누락 0건 ✅
- [x] 전부 `DRAFT` 상태 (Phase 1에서는 전부 DRAFT) ✅

> **완료**: 2026-04-07. 1-2 분배 파일 35건(5 _index + 30 distribution) 100% 표준 6필드 헤더 적용, 전부 Status: DRAFT.
>
> **실행 결과 요약**:
> - 표준 6필드(버전 / Status / 작성일 / Last-reviewed / 모듈 / LOCK 참조) 35건 100% 적용
> - LOCK 참조는 LOCK-AX-NN 형식으로 통일 (AUTHORITY_CHAIN.md §5A 정본 정합)
> - 재검증 1회로 30개 분배 파일에서 4필드 누락 발견 후 보완 (작성일/Last-reviewed/모듈/LOCK 참조 일부 결락)
> - Out-of-scope 6건은 의도적 미수정 — 06_mapping/ 2건(1-6/1-7에서 별도 작성), governance/ 3건(1-8에서 작성), 입력 소스 1건 (원본 보존)
> - AUX-11 (메타데이터 미표준) 해결, `grep Status:` 누락 0건 달성
</details>

<details>
<summary><b>1-4. 00_common 공통 파일 작성</b></summary>

**대조 기준**:
- §7 세부 작업: 1-4 "00_common 공통 파일 작성"
- §7 전환 게이트: 폴더 구조 완성 + 40+ 파일 존재 + 전 파일 헤더 보유
- §6 이슈: AUX-09 (Phase 1 해결)

**목표**: `00_common/` 폴더에 response_envelope.md, common_types.md, error_taxonomy.md, timeout_policy.md 4개 공통 파일을 작성한다. ResponseEnvelope은 LOCK-AX-11 사양을 준수한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md` §7 ResponseEnvelope
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\AUXILIARY_MODULES_구조화_종합계획서.md` §7 Phase 1 (본 섹션)

**절차**:
1. 아래 4개 공통 파일을 `00_common/` 폴더에 작성한다:

**작성 대상 4개 파일**:

**response_envelope.md**:
> LOCK (D2.0-02 §7): ResponseEnvelope minimum spec

```python
@dataclass
class ResponseEnvelope:
    request_id: str                    # UUID v4
    timestamp: datetime                # UTC ISO 8601
    status: Literal["success", "partial", "error"]
    data: Any                          # 모듈별 응답 데이터
    metadata: dict                     # 처리 시간, 모델 ID, 토큰 수 등
    errors: list[ErrorDetail]          # 에러 목록 (status=error 시)
    trace_id: Optional[str]            # 분산 트레이싱 ID
    pipeline_stage: str                # 현재 파이프라인 단계 (S0~S8)
```

**common_types.md**: 공유 타입 (Modality enum, ConfidenceScore, Entity, MemoryCandidate 등)

**error_taxonomy.md**: 에러 분류 체계
| 에러 코드 | 범주 | 설명 | 재시도 가능 |
|-----------|------|------|-----------|
| AUX-E001 | INPUT | 지원하지 않는 입력 형식 | N |
| AUX-E002 | INPUT | 입력 크기 초과 | N |
| AUX-E003 | PROCESSING | 모델 추론 실패 | Y |
| AUX-E004 | PROCESSING | 타임아웃 초과 | Y |
| AUX-E005 | EXTERNAL | 외부 API 응답 실패 | Y |
| AUX-E006 | EXTERNAL | 외부 API rate limit | Y (backoff) |
| AUX-E007 | MEMORY | VectorStore 연결 실패 | Y |
| AUX-E008 | MEMORY | 메모리 용량 초과 | N |
| AUX-E009 | QUALITY | QoD 임계값 미달 | N |
| AUX-E010 | SYSTEM | 내부 상태 불일치 | N |

**timeout_policy.md**: 타임아웃 정책
| 호출 유형 | 기본 타임아웃 | 최대 재시도 | 재시도 간격 |
|----------|-------------|-----------|-----------|
| LLM 추론 (로컬) | 30s | 2 | 5s |
| LLM 추론 (클라우드) | 60s | 3 | exponential (1s, 2s, 4s) |
| Vision API | 30s | 2 | 5s |
| STT (Whisper 로컬) | 120s | 1 | — |
| STT (Deepgram 클라우드) | 30s | 3 | 5s |
| VectorStore upsert | 10s | 3 | 2s |
| VectorStore search | 5s | 3 | 1s |
| 외부 검색 API | 15s | 2 | 3s |
| Reranker 모델 | 10s | 2 | 3s |
| Rendering (단일) | 10s | 1 | — |
| Rendering (복합) | 30s | 1 | — |

**검증**:
- [x] 4개 공통 파일 전수 존재 ✅
- [x] ResponseEnvelope이 D2.0-02 §5.1.1 LOCK 사양 준수 (LOCK-AX-11, 출처 정정 §7→§5.1.1) ✅

> **완료**: 2026-04-07. 00_common/ 4개 파일 작성. ResponseEnvelope LOCK-AX-11 (D2.0-02 §5.1.1) nested 정본 채택.
>
> **실행 결과 요약**:
> - **response_envelope.md**: D2.0-02 §5.1.1 nested 구조를 정본 채택, 본 계획서의 dataclass 표현은 §3 보조표현(Non-LOCK)으로 분리. 머리글에 SoT 교차검증 이슈 명시 (계획서 §7 인용 → 정본은 §5.1.1)
> - **common_types.md**: Modality / ConfidenceScore / QoD(LOCK-AX-03 5-factor 공식, PLAN-3.0 정본 인용) / Entity / EvidenceItem / MemoryCandidate / PipelineStage(LOCK-AX-13) 카탈로그화
> - **error_taxonomy.md**: AUX-E001~E010 + 재시도 매트릭스 + LogEvent 매핑
> - **timeout_policy.md**: 11개 호출 유형 + 폴백/백오프 규칙
> - 재검증 1회로 LOCK-AX-12(Modality)/LOCK-AX-13(QoD) 잘못된 매핑 4건 식별·정정 → LOCK-AX-03/04(QoD)/AX-13(state machine)으로 교정
> - SoT 교차검증 이슈 2건 식별: ① ResponseEnvelope 출처 §7→§5.1.1 정정 ② 스키마는 dataclass가 아닌 nested 구조
> - AUX-09 (공통 타입/스키마 미정의) 해결

**산출물**:
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\00_common\response_envelope.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\00_common\common_types.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\00_common\error_taxonomy.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\00_common\timeout_policy.md`
</details>

<details>
<summary><b>1-5. fallback_chain.md 작성 (5건)</b></summary>

**대조 기준**:
- §7 세부 작업: 1-5 "fallback_chain.md 작성 (5건)"
- §7 전환 게이트: 폴더 구조 완성 + 40+ 파일 존재 + 전 파일 헤더 보유
- §6 이슈: AUX-08 (Phase 1 해결)

**목표**: 5개 모듈(I-4, I-13, I-14, I-16, S-1) 각각에 fallback_chain.md를 작성하여 실패 대체 경로를 정의한다. 각 파일에 최소 3개 이상 실패 지점을 포함한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\AUXILIARY_MODULES_상세명세.md` 모듈별 fallback 정보
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\AUXILIARY_MODULES_구조화_종합계획서.md` §7 Phase 1 (본 섹션)

**절차**:
1. 5개 모듈(I-4, I-13, I-14, I-16, S-1) 각각의 서브폴더에 `fallback_chain.md`를 작성한다.
2. 각 파일에 실패 지점별 Primary → Fallback → 최종 실패 테이블을 아래와 같이 정의한다:

**각 모듈의 fallback chain**:

**I-4 (01_multimodal-interpreter/fallback_chain.md)**:
| 실패 지점 | Primary | Fallback 1 | Fallback 2 | 최종 실패 |
|----------|---------|-----------|-----------|----------|
| 이미지 해석 | Claude Vision | GPT-4V | OCR only | 에러 + 원본 첨부 |
| 음성 STT | Whisper 로컬 | Deepgram 클라우드 | — | 에러 + 원본 첨부 |
| 문서 파싱 | docling | Unstructured | raw text 추출 | 에러 + 원본 첨부 |
| 언어 감지 | langdetect | 기본값 (ko) | — | 기본값 적용 |
| OCR | Tesseract | EasyOCR | — | 에러 |

**I-13 (02_multimodal-renderer/fallback_chain.md)**:
| 실패 지점 | Primary | Fallback | 최종 실패 |
|----------|---------|---------|----------|
| ChartRenderer | Plotly interactive | Static PNG 생성 | 텍스트 테이블 대체 |
| DiagramRenderer | Mermaid-js | ASCII art | 텍스트 설명 |
| CodeRenderer | Shiki 하이라이트 | plain text code | 그대로 출력 |
| 복합 렌더링 | 병렬 DAG | 순차 렌더링 | 개별 렌더 결과 연결 |

**I-14 (03_summarizer/fallback_chain.md)**:
| 실패 지점 | Primary | Fallback | 최종 실패 |
|----------|---------|---------|----------|
| LLM 요약 | Claude 요약 | GPT 요약 | extractive 요약 (TextRank) |
| 메모리 증류 | 전체 증류 | 키워드 기반 증류 | 원본 보존 (L0 유지) |
| 엔티티 추출 | NER 모델 | regex 기반 | 빈 목록 반환 |

**I-16 (04_knowledge-search/fallback_chain.md)**:
| 실패 지점 | Primary | Fallback 1 | Fallback 2 | 최종 실패 |
|----------|---------|-----------|-----------|----------|
| Vector search | ChromaDB | in-memory FAISS | — | BM25 only |
| BM25 search | Whoosh | simple text match | — | Vector only |
| Reranking | BGE-reranker | cosine 유사도 정렬 | — | 원본 순서 유지 |
| 외부 검색 | Tavily | Serper | DuckDuckGo | 내부 검색만 |
| 임베딩 생성 | BGE-M3 | Matryoshka 256-dim | — | 에러 |

**S-1 (05_self-check/fallback_chain.md)**:
| 실패 지점 | Primary | Fallback | 최종 실패 |
|----------|---------|---------|----------|
| 메트릭 수집 | Prometheus pull | 로컬 메트릭 파일 | 기본 QoD=0.5 적용 |
| QoD 계산 | 전체 가중치 계산 | 부분 메트릭 계산 (available만) | 경고 + 기본값 |
| SDAR 트리거 | I-25 호출 | 로컬 알림 (로그 + 이메일) | 운영자 직접 알림 |
| 이상 감지 | sliding window 분석 | threshold 비교만 | 경고 로그 |

**검증**:
- [x] 5개 모듈 전부 fallback_chain.md 존재 ✅
- [x] 각 파일에 최소 3개 이상 실패 지점 정의 (총 22개 고유 F-XXX-NN ID) ✅
- [x] 최종 실패 동작이 명시적 (에러 반환 또는 안전한 기본값) ✅

> **완료**: 2026-04-07. 5개 모듈 fallback_chain.md 작성, 총 22개 고유 실패 지점(F-XXX-NN ID 부여), 재검증 1회로 v1.1 정본 정합 확정.
>
> **실행 결과 요약**:
> - 5개 fallback_chain.md (I-4 / I-13 / I-14 / I-16 / S-1) 작성, 실패 지점별 Primary → Fallback → 최종 실패 테이블 전수 정의
> - 재검증 시 초안의 임의 timeout/재시도 값을 timeout_policy.md §2 정본 표로 교체
> - error_taxonomy.md AUX-E003 / E005 / E006 / E007 매핑 추가 (실패 코드 ↔ fallback 트리거 매핑)
> - ResponseEnvelope 정본 필드 사용: `audit.failure_codes` / `audit.fallback_ids` / `audit.event_ids`
> - S-1만 §3.1 모듈별 오버라이드 신설: Prometheus pull 5s/2/1s, I-25 SDAR 트리거 10s/2/2s — timeout_policy 정본 표 미매핑 호출 보강
> - V-09 검증(5건+각 3개+) 통과
> - **이월**: F-XXX-NN ID는 추후 D2.0-02 §6.3 Fallback Registry 등재 필요
> - AUX-08 (실패 경로 미정의) 해결

**산출물**:
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\01_multimodal-interpreter\fallback_chain.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\02_multimodal-renderer\fallback_chain.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\03_summarizer\fallback_chain.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\04_knowledge-search\fallback_chain.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\05_self-check\fallback_chain.md`
</details>

<details>
<summary><b>1-6. 모듈 의존성 그래프 작성</b></summary>

**대조 기준**:
- §7 세부 작업: 1-6 "모듈 의존성 그래프 작성"
- §7 전환 게이트: 폴더 구조 완성 + 40+ 파일 존재 + 전 파일 헤더 보유
- §6 이슈: AUX-05 (Phase 1 해결, HIGH)

**목표**: 5개 보조 모듈(I-4, I-13, I-14, I-16, S-1) 간 의존성 관계를 Mermaid 그래프로 정의하고, 순환 의존성 0건을 검증한다. 부록 §A 내용을 기반으로 작성한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\AUXILIARY_MODULES_구조화_종합계획서.md` 부록 §A 모듈 의존성 그래프
- `D:\VAMOS\docs\sot\D2.0-01_01. VAMOS_DESIGN_2_0_OVERVIEW.md` §5.6 모듈 관계

**절차**:
1. 부록 §A 의존성 그래프 내용을 `06_mapping/module_dependency_graph.md`로 이관
2. Mermaid `graph TD` 형식으로 모듈 간 호출/데이터 의존성 정의
3. 각 엣지에 의존성 유형 라벨 추가 (호출/데이터/이벤트)
4. 순환 의존성 검증: 그래프에서 cycle 존재 여부 확인
5. 표준 메타데이터 헤더 적용

**검증**:
- [x] `06_mapping/module_dependency_graph.md` 파일 존재 ✅
- [x] Mermaid 그래프 렌더링 정상 (문법 오류 0건, `graph TD` + `-->|"label"|` 표준 표기) ✅
- [x] 순환 의존성 0건 (위상 정렬 L0~L5 + DFS 백엣지 0건, §A.4 정합) ✅
- [x] 5개 모듈 전부 그래프에 포함 (인입/인출 엣지 ≥1, 5/5 PASS) ✅
- [x] Status: 헤더 존재 (DRAFT v1.1, 표준 7필드 헤더) ✅

> **완료**: 2026-04-07. 부록 §A.1~A.4를 Mermaid `graph TD`로 정규 이관, v1.1 확정 (재검증 1회로 8건 결함 정정).
>
> **실행 결과 요약**:
> - 노드 14개 (CORE 1 + AUX 5 + 외부 8) / 엣지 19건 (실선 14 + 점선 5)
> - 위상 정렬 L0~L5, in-degree 합 = 19 = 엣지 수 정합, DFS 백엣지 9개 잠재 cycle 점검 결과 0건 → cycle 0건 (§A.4 결론과 일치)
> - 유형 분포: call 11건 / data 7건 / event 1건
> - 5개 AUX 모듈 인입/인출 엣지 ≥1 (5/5 PASS)
> - **v1.0 → v1.1 정정 8건**: ① I-4→I-16 embedding 누락 추가 (§A.1+§A.2 양쪽 확인) ② QoD 방향 정정 I-14→S-1 ⇒ S-1→I-14 (§A.1 ASCII 채택) ③ 추론 엣지 CORE→I-14 제거 (§A 미존재, out-of-scope 처리) ④ I-19 점선 3건→5건 확장 (§A.3 "전체 → I-19" 충실 반영) ⑤ Layer 분배 재계산 (v1.0은 I-6를 L5로 잘못 배치) ⑥ 엣지 수 16→19 정정 ⑦ Mermaid edge 표기 `-->|"label"|` 표준화 ⑧ §6 SoT 교차검증 섹션 신설
> - **SoT 교차검증 발견 (CONFLICT_LOG 등재 권고)**: HIGH 3건 — I-2(§A "RAG Pipeline" vs §5.6 "Context Builder"), I-6(§A "Executor" vs §5.6 "Self-check Engine 자기검증"), I-20(§A "OutputComposer" vs §5.6 "Failure/Fallback Manager"; Output Composer 정본 ID는 I-11). MEDIUM 1건 — §5.7 line 649 S-1 `i_module_link: I-6, I-15`이나 §A는 I-15(Evidence & QoD Manager) 누락. LOW 1건 — §A.1 ASCII vs §A.2 매트릭스 간 QoD 방향 충돌(ASCII 채택 결정)
> - **이월**: §6.1 HIGH 3건 → CONFLICT_LOG, §6.2 MEDIUM I-15 누락 → 1-7 interface_contracts.md
> - AUX-05 (모듈 간 의존성 미문서화, HIGH) 해결

**산출물**: `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\06_mapping\module_dependency_graph.md` ✅
</details>

<details>
<summary><b>1-7. 인터페이스 계약서 작성</b></summary>

**대조 기준**:
- §7 세부 작업: 1-7 "인터페이스 계약서 작성"
- §7 전환 게이트: 폴더 구조 완성 + 40+ 파일 존재 + 전 파일 헤더 보유
- §6 이슈: AUX-06 (Phase 1 해결, HIGH)

**목표**: 모듈 간 인터페이스 계약을 정의한다. 각 계약에 입출력 스키마, 호출 조건, 에러 처리, SLA(타임아웃)를 포함한다. 부록 §B 내용을 기반으로 작성한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\AUXILIARY_MODULES_구조화_종합계획서.md` 부록 §B 인터페이스 계약서
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\AUXILIARY_MODULES_상세명세.md` 모듈별 입출력 스키마
- `D:\VAMOS\docs\sot\D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md` §2.1 Standard 5-Stage Pipeline (LOCK-AX-12)

**절차**:
1. 부록 §B 인터페이스 계약 내용을 `06_mapping/interface_contracts.md`로 이관
2. 각 모듈 쌍별 계약 정의:
   - 호출 방향 (caller → callee)
   - 입력 스키마 (타입, 필수/선택 필드)
   - 출력 스키마 (ResponseEnvelope 기반, LOCK-AX-11)
   - 에러 코드 매핑 (error_taxonomy.md 참조)
   - SLA: 타임아웃 (timeout_policy.md 참조)
3. Pipeline 단계별 모듈 호출 순서 정의 (LOCK-AX-12 5-Stage)
4. 표준 메타데이터 헤더 적용

**검증**:
- [x] `06_mapping/interface_contracts.md` 파일 존재 ✅
- [x] 모듈 간 인터페이스 계약 전수 정의 (누락 0건) ✅ — 1-6 v1.1 19 엣지 전수 매핑 (12×1 + C-07×2 + C-14×5 = 19)
- [x] 각 계약에 입력/출력/에러/SLA 4항목 포함 ✅ — 14×4 = 56 sub-section 전수 충족
- [x] ResponseEnvelope 기반 출력 (LOCK-AX-11 준수) ✅ — response_envelope.md LOCK 정본 (answer/evidence/self_check/decision_ref/audit) 적용
- [x] Status: 헤더 존재 ✅ — frontmatter 6필드 (버전 v1.1 / Status DRAFT / 작성일 / Last-reviewed / 모듈 / LOCK 참조 14종)

> **완료**: 2026-04-07. 14건 계약(C-01~C-14)으로 1-6 v1.1 의존성 그래프 19 엣지 전수 매핑·누락 0건. 재검증 1회로 v1.0→v1.1 결함 9건 정정 (LOCK 정본 교체 + QoD 5-factor + 방향 반전 등).
>
> **실행 결과 요약**:
> - **산출물**: `06_mapping/interface_contracts.md` v1.1, 1046줄. 14개 계약 (C-01 ~ C-14) + §1 범위 + §2 공통 규약 + §3 5-stage 매핑 + §5 점검표 + §6 SoT crosscheck + §7 후속.
> - **계약 매핑**: 1-6 module_dependency_graph.md v1.1의 19 엣지 (실선 14 + 점선 5) **전수 매핑, 누락 0건**. C-07 = I-4/I-16→I-5 복합 2엣지(#3+#8). C-14 = 5 AUX→I-19 복합 5엣지(#15~#19). 단순 계약 12건. 매핑 합계: 12×1 + 1×2 + 1×5 = 19 ✓.
> - **5-stage 그룹화** (LOCK-AX-12 D2.0-02 §2.1): Perception(C-01,02) / Reasoning(C-03~07) / Action(C-08,09) / Memory(C-12) / Reflection(C-10,11,13) + 임의 단계 격상(C-14). LOCK-AX-12 5-stage ↔ LOCK-AX-13 S0~S8 직교성 §3.1 명시 — AUX 모듈은 특정 S-state에 1:1 매핑되지 않으며 ORANGE CORE 가 런타임에 결정.
> - **4항목 충족**: 14개 계약 × {입력 스키마 / 출력 스키마 / 에러 코드 / SLA} = 56 sub-section. 추가 컨텍스트 sub-section(C-06 Semantic Cache 계약, C-12 트리거 조건 계약, C-13 SDAR 트리거 조건) 3건 포함.
> - **LOCK 인용 정식 번호 14종**: LOCK-AX-01(모듈 분류) / -03(QoD 5-factor) / -04(QoD 임계) / -05(Self-check 임계) / -06(RAG α=0.3) / -07(BGE-M3) / -08(VectorStore 4-method) / -09(Memory 4-layer) / -10(Semantic cache) / -11(ResponseEnvelope) / -12(5-stage) / -13(S0~S8 + S3 Decision Lock) / -14(PII 마스킹) / -15(검색 우선순위). lock_value_registry.md §1 정합.
> - **재검증 1회 v1.0→v1.1 결함 9건 정정**:
>   1. §2.2 ResponseEnvelope를 종합계획서 §B.6 보조표현(`data/status/errors`) → `response_envelope.md` LOCK 정본 (D2.0-02 §5.1.1 nested) 으로 교체
>   2. §3 LOCK-AX-13 S0~S8의 잘못된 모듈-스테이지 1:1 매핑 제거 (common_types.md §8 직교성 인용)
>   3. C-03 방향 반전: `I-16→I-4 (call)` → **`I-4→I-16 (data, embedding)`** (1-6 v1.1 §6.3 채택, §A.1 ASCII 화살표 정합)
>   4. **C-10 QoD 공식 4-factor → LOCK-AX-03 PLAN-3.0 5-factor** (Accuracy×0.30 + Relevance×0.25 + Completeness×0.20 + Safety×0.15 + Efficiency×0.10), §B.5 4-factor는 V1-006으로 SUPERSEDED
>   5. LOCK 인용을 LOCK-AX-NN 정식 번호로 통일 (lock_value_registry.md §1 기준, AX-04/05/06/07/08/09/10/14/15 추가 인용)
>   6. Modality enum lowercase → uppercase TEXT/IMAGE/AUDIO/VIDEO/DOCUMENT/MIXED (common_types.md §2 정본)
>   7. §5 점검표 엣지 수 14 → **19** 정정 (1-6 §4.3 합계와 정합), C-07/C-14 복합 명시
>   8. §6 SoT crosscheck에 X-1 (4-factor SUPERSEDED HIGH) + X-5 (S-1↔I-15 누락 MEDIUM, 1-6 §6.2 계승) 신규 finding 추가
>   9. timeout_policy.md §2 표 미수록 호출 (I-19 / I-8 / I-25 / S-1 내부) 4종을 PENDING으로 명시 — 임의 호출 유형 신설 금지 (R-02-4 위반 방지)
> - **SoT 교차검증** (§6.2 X-1~X-7, CONFLICT_LOG 등재 권고):
>   - **HIGH X-1**: §B.5 4-factor QoD SUPERSEDED → §B.5 본문 갱신 + D2.0-06 DEC-014 + MASTER_SPEC §8.8 갱신 후속 (lock_value_registry.md D-02 잔여)
>   - **HIGH X-2**: I-2 라벨 "RAG Pipeline" vs SoT "Context Builder" (1-6 §6.1 계승)
>   - **HIGH X-3**: I-6 라벨 "Executor" vs SoT "Self-check Engine" (1-6 §6.1 계승, S-1과 명칭 충돌)
>   - **HIGH X-4**: I-20 라벨 "OutputComposer" vs SoT "Failure/Fallback Manager" (1-6 §6.1 계승, ID 오기 가능성 — Output Composer 정본 = I-11)
>   - **MEDIUM X-5**: S-1 → I-15 (Evidence & QoD Manager) 연결 §A 누락 (1-6 §6.2 계승) — D2.0-01 §5.7 L649가 S-1 i_module_link로 I-6/I-15 명시하나 §A는 I-15 부재. 본 문서 out-of-scope 처리
>   - **LOW X-6**: LOCK-AX-09 명칭 D-04 (장기 vs 글로벌 지식, 절차적 vs 절차/템플릿) — C-12에 주의 표시
>   - **HIGH X-7**: LOCK-AX-02 출처 부재 D-01 — 본 문서는 LOCK-AX-02 직접 인용 안 함
> - **이월 (F-01 ~ F-10 후속 작업)**:
>   - F-01: CONFLICT_LOG.md 정식 등재 (X-2/X-3/X-4/X-5) → 1-8 또는 별도
>   - F-02: 종합계획서 §B.5 본문 5-factor 갱신 → §7 후속 / D2.0 갱신 작업
>   - F-03: D2.0-06 DEC-014 + MASTER_SPEC §8.8 5-factor 반영 → D2.0 갱신 작업
>   - F-04: timeout_policy.md §2 표 확장 (I-19/I-8/I-25/S-1 내부 4종 정본화) → 1-8 또는 Phase 2
>   - F-05: S-1 ↔ I-15 실 통합 여부 결정 → Phase 2
>   - F-06: Out-of-scope 호출 경로 (스케줄러→I-14, CORE→S-1 활성화) 명시 → Phase 2
>   - F-07: ABC 단위 테스트 케이스 도출 (C-01~C-14 14건 기반) → Phase 2 구현
>   - F-08: interface_contracts.md ↔ 모듈 폴더 (`01_*`~`05_*`) 역참조 추가 → 1-8
>   - F-09: C-12 Entity 구조 정합화 (common_types.md §5 8필드 vs §B.3 3필드 단축형) → 1-8
>   - F-10: 1-5 fallback_chain.md F-XXX-NN ID 22개 → D2.0-02 §6.3 Fallback Registry 등재 (Phase 2)
> - **해결 이슈**: AUX-06 (ABC 인터페이스 미정의, HIGH, Phase 1) — 14건 계약으로 정식 ABC 시그니처 정의 완료. AUX-09 (00_common 표준 정합) 정합 검증 통과.

**산출물**: `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\06_mapping\interface_contracts.md`
</details>

<details>
<summary><b>1-8. INDEX.md 작성</b></summary>

**대조 기준**:
- §7 세부 작업: 1-8 "INDEX.md 작성"
- §7 전환 게이트: 폴더 구조 완성 + 40+ 파일 존재 + 전 파일 헤더 보유
- §6 이슈: — (별도 이슈 없음)

**목표**: 마스터 `INDEX.md`와 폴더별 `_index.md`를 작성하여 전체 파일 탐색 진입점을 제공한다. 마스터 인덱스는 40+ 파일 전수를 링크로 포함한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\` 하위 전체 파일 목록 (1-2 산출물)
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\AUXILIARY_MODULES_구조화_종합계획서.md` §2.1 폴더 트리

**절차**:
1. 마스터 `INDEX.md` 작성:
   - 폴더별 섹션으로 구분
   - 각 파일에 상대 경로 링크 + 1줄 설명
   - 파일 수 합계 표기
2. 폴더별 `_index.md` 작성 (00_common ~ 06_mapping):
   - 해당 폴더 내 파일 목록 + 설명
   - 모듈 개요 (해당 모듈의 I-시리즈 ID, 분류)
3. 표준 메타데이터 헤더 적용

**검증**:
- [x] `INDEX.md` 파일 존재 (루트) ✅
- [x] 폴더별 `_index.md` 7개 존재 (00~06) ✅ 7/7
- [x] INDEX.md 내 링크 수 ≥ 40 — 61 .md 링크 ✅
- [x] 깨진 링크 0건 (상대 경로 검증) — INDEX.md 61 + 7개 _index.md 합계 55, broken 0/116 ✅
- [x] Status: 헤더 존재 — 신규/갱신 8개 파일 전수 6필드 표준 헤더 ✅ (legacy `상세명세.md` 1건만 미보유, 1-9 아카이브 예정)

> **완료**: 2026-04-07. 마스터 INDEX.md + 폴더별 `_index.md` 7종 정렬 완료, 디스크 55 파일 전수 등재.
>
> **실행 결과 요약**:
> - 신규 산출물 8건: INDEX.md (마스터, 240+ 줄), `00_common/_index.md`, `06_mapping/_index.md`, 01~05 `_index.md` 5건 파일 목록 갱신 (stub "(Phase 1에서 추가 예정)" → 실제 파일 표)
> - 등재 회계: 루트 5(INDEX.md 포함) + 00_common 5(_index.md 포함) + 01:9 + 02:12 + 03:6 + 04:6 + 05:7 + 06:5(_index.md 포함) = **55**, 디스크 실측 55건과 일치
> - INDEX.md 링크 검증: 61 .md 링크, 0 broken / 7개 _index.md 합계 55 링크, 0 broken (총 116 링크 broken 0/116)
> - 시각 대조 (61 entries × {제목 / 설명}): 모든 INDEX.md 행의 1줄 설명이 정본 파일의 H1 제목·내용과 일치 확인
> - 재검증 1회로 명명 불일치 3건 정정 (Phase 0 stub 잔존 결함):
>   - ① 01 `input_schema.md`: `MultimodalInput / InterpretedContent` → **`RawInput / InterpretedInput`** (정본 파일 L21~L25)
>   - ② 03 `input_output_schema.md`: `SummarizationRequest / SummarizationResult` → **`SummarizeRequest / SummaryResult`** (정본 파일 L21~L26)
>   - ③ 04 `search_api.md`: `SearchRequest / SearchResult` → **`class KnowledgeSearchEngine` (SearchQuery / SearchResults)** (정본 파일 L22~L34)
> - §7 검증 체크리스트 5/5 PASS (파일 존재 / 7 _index.md / ≥40 링크 / 0 broken / Status 헤더)
> - 1-8 범위 외 발견 (1-2 분배 결정 기인, 1-8 미수정):
>   - §2.1 폴더 트리 vs 디스크 차이 7건 — §2.1 등재이나 디스크 부재: `03/memory_layer_integration`, `04/semantic_cache`, `04/embedding_model`, `04/vectorstore_adapter`, `05/qod_thresholds`, `05/self_check_thresholds` (총 6건); 디스크 등재이나 §2.1 부재: `02/audio_renderer`, `02/image_renderer`, `02/diagram_renderer` (3건)
>   - 02/05 `_index.md` 핵심 인터페이스 stub의 `RenderRequest`/`SelfCheckRequest` 등 명명도 정본 파일과 불일치 가능 — 1-8이 직접 수정한 파일 목록 표 외 영역이므로 미수정
>   - 05 `fallback_chain.md` 자체 분류 "META (관찰/감시)" — D2.0-01 §5.6 / LOCK-AX-01 정본은 CORE (1-5 산출물 자체 인용 오류)
> - 이월 항목: F-11 (신규) §2.1 ↔ 디스크 7건 차이 정정 또는 §2.1 본문 갱신 → Phase 2 또는 1-2 추가 보정 (`project_aux_modules_status.md` Phase 1 후속 작업 표 등재)

**산출물**:
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\INDEX.md` ✅
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\00_common\_index.md` ~ `06_mapping\_index.md` (7개) ✅
</details>

<details>
<summary><b>1-9. 상세명세.md 아카이브</b></summary>

**대조 기준**:
- §7 세부 작업: 1-9 "상세명세.md 아카이브"
- §7 전환 게이트: 폴더 구조 완성 + 40+ 파일 존재 + 전 파일 헤더 보유
- §6 이슈: AUX-07 (Phase 1 해결, HIGH)

**목표**: 분배 완료된 `AUXILIARY_MODULES_상세명세.md` 원본을 `_archive/`로 이동하고, 읽기 전용 표시를 하여 이중 편집을 방지한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\AUXILIARY_MODULES_상세명세.md` (원본)

**절차**:
1. 원본 파일을 `_archive/AUXILIARY_MODULES_상세명세_v1.0_archived.md`로 복사
2. 아카이브 파일 상단에 아카이브 헤더 추가:
   ```markdown
   > ⚠️ **ARCHIVED**: 이 파일은 Phase 1 분배 완료 후 아카이브되었습니다.
   > **분배 일자**: {날짜}
   > **원본 위치**: 1-2_Auxiliary-Modules/AUXILIARY_MODULES_상세명세.md
   > **분배 대상**: 01~05 서브폴더 (1-2 태스크 참조)
   > **편집 금지**: 분배된 개별 파일을 수정하세요.
   ```
3. 원본 위치에 리다이렉트 안내 파일 남기기 (선택)
4. 표준 메타데이터 헤더에 `Status: ARCHIVED` 적용

**검증**:
- [x] `_archive/AUXILIARY_MODULES_상세명세_v1.0_archived.md` 파일 존재 — 10780 B / 336 lines
- [x] 아카이브 헤더에 ARCHIVED 경고 포함 — sidecar `_archive/README.md` 로 위치 변경 (본문 byte-identical 보존이 우선, sibling `Ai-investing-detail/_archive/` convention 일치)
- [x] 원본 파일과 아카이브 파일 내용 동일 (diff 0줄) — **byte-identical 10780 B / 336 lines, `## I-4` L16, `## I-13` L86, `## I-14` L143, `## I-16` L205, `## S-1` L277 원위치 보존**
- [x] Status: ARCHIVED 헤더 존재 — redirect frontmatter `Status: ARCHIVED (REDIRECT)` + sidecar README `Status: ARCHIVED` + 4중 표시 (폴더/파일명/sidecar/redirect)

> **완료**: 2026-04-07. 원본을 `_archive/` 로 byte-identical 이동, 루트에 redirect 게시, sidecar README 신설, INDEX.md 루트 정본 표 갱신.
>
> **실행 결과 요약**:
> - 신규/갱신 산출물 4건: `_archive/AUXILIARY_MODULES_상세명세_v1.0_archived.md` (10780 B / 336 lines, byte-identical), `_archive/README.md` (3965 B / 69 lines, sidecar), `AUXILIARY_MODULES_상세명세.md` (3729 B / 72 lines, redirect 교체), `INDEX.md` (§1 L39 REDIRECT 표시 + §10 v1.1 1-9 이력 추가)
> - **byte 무결성**: archive 10780 B = 분배 시점 원본과 동일, `wc -lc` 일치, line shift 0
> - **provenance 무결성**: 47개 sibling 파일의 `> **출처**: AUXILIARY_MODULES_상세명세.md L<n>-L<m>` 인용이 그대로 유효 (sample 검증: `01_multimodal-interpreter/input_schema.md` L11 의 `L16-17` → archive L16 = `## I-4: Multimodal Interpreter` 일치)
> - **모듈 ID 정합성**: redirect 분배 위치 표 = D2.0-02 §7 정본 (`I-4 / I-13 / I-14 / I-16 / S-1`). 1차 작성 시 발견된 `I-5/I-6/I-7/I-8` 오기는 재검증에서 정정 완료
> - **convention 준수**: spec verification 두 항목 ("아카이브 헤더 prepend" vs "diff 0줄") 충돌 → sibling `Ai-investing-detail/_archive/` (19 파일) 의 byte-identical 보존 convention 채택. ARCHIVED 표시는 (a) `_archive/` 폴더, (b) `_v1.0_archived.md` 파일명 접미사, (c) sidecar `_archive/README.md`, (d) 루트 redirect frontmatter 의 4중 redundancy 로 보장
> - **이중 편집 방지 (AUX-07 HIGH 해결)**: 루트 bare-name 경로는 redirect (편집 금지 명시), 본문은 `_archive/` 로 격리 → 원본 path 와 분배본 path 양쪽 동시 편집 위험 차단
> - **재검증 사이클**: 3차 (1차 작업 → 모듈 ID 오기 발견 → 2차 보정 → 3차 무결성 점검 → 수렴)
> - **다른 루트 파일과의 충돌 없음**: 종합계획서 §3.2 마스터 파일 표 (L1372) 의 "→ _archive/" 표기, §7 1-9 절차와 일치. AUTHORITY_CHAIN.md / CONFLICT_LOG.md 영향 없음
> - **이월 항목 없음**: 1-9 범위 내 미해결 결함 0건. F-11 (1-8 이월, §2.1 ↔ 디스크 7건 차이) 는 1-9 범위 외로 동일하게 유지
> - §7 검증 체크리스트 4/4 PASS (파일 존재 / ARCHIVED 표시 / diff 0 / Status 헤더)

**산출물**:
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\_archive\AUXILIARY_MODULES_상세명세_v1.0_archived.md` ✅ (byte-identical, 10780 B)
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\_archive\README.md` ✅ (sidecar, 신규)
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\AUXILIARY_MODULES_상세명세.md` ✅ (redirect 교체)
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\INDEX.md` ✅ (§1 + §10 갱신)
</details>

<details>
<summary><b>1-10. PART2 링크 테이블 추가</b></summary>

**대조 기준**:
- §7 세부 작업: 1-10 "PART2 링크 테이블 추가"
- §7 전환 게이트: 폴더 구조 완성 + 40+ 파일 존재 + 전 파일 헤더 보유
- §6 이슈: AUX-03 (Phase 1 해결, CRITICAL)

**목표**: PART2 V1-Phase 1 문서에 `sot 2/1-2_Auxiliary-Modules/` 참조 테이블을 추가하여 PART1(설계 SoT)과 PART2(구조화 SoT) 간 양방향 추적성을 확보한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\` 하위 전체 파일 목록 (1-2 산출물)
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\AUXILIARY_MODULES_구조화_종합계획서.md` §5B 매핑

**절차**:
1. PART2 참조 테이블 작성:
   | SoT 원본 (PART1) | 구조화 파일 (PART2 sot 2/) | 매핑 상태 |
   |---|---|---|
   | D2.0-01 §5.6 | 1-2_Auxiliary-Modules/ 전체 | MAPPED |
   | D2.0-02 §7 ResponseEnvelope | 00_common/response_envelope.md | MAPPED |
   | D2.0-02 §2.1 Pipeline | 06_mapping/interface_contracts.md | MAPPED |
   | D2.0-06 Memory/Vector/Cache | 04_knowledge-search/ 하위 | MAPPED |
2. 본 계획서의 `Part2 상태`를 `PARTIAL` → `COMPLETE` 로 갱신 (전 파일 매핑 완료 시)
3. 각 모듈 서브폴더의 `_index.md`에 PART1 원본 참조 링크 추가

**검증**:
- [x] PART2 참조 테이블에 주요 SoT 매핑 4건 이상 포함 ✅ (정방향 19건)
- [x] 양방향 추적 가능: PART1 → PART2 (§3 19건), PART2 → PART1 (§4 56 파일)
- [x] 매핑 상태 전부 MAPPED (UNMAPPED 0건)
- [x] 본 계획서 `Part2 상태` 갱신 완료 (§1 헤더 L9 + §1 말미 "Part2 상태 및 방식 C 접근법" 모두 PARTIAL → COMPLETE)

> **완료**: 2026-04-07 (v1.2 재검증). `06_mapping/part2_reference_table.md` 신설 + Round 1~3 재검증으로 정밀화 다수 (§2 count 14→19, §3 모든 행에 D2.0 라인 번호, §3.3 generic §7→정확한 sub-section, §4.2/§4.3 폴더-단위→파일-단위 9·12행 확장, §4.0 루트 5 파일 추가, §4.1/§4.4~§4.7 _index.md 누락 보정, §7 SoT crosscheck C-01~C-06 6건 등재). §5B 25행 1:1 + I-13 §2 1:N 7행 전수 커버, INDEX.md §9 합계 56과 정합.
>
> §7 검증 체크리스트 4/4 PASS + 본 테이블 §5 9개 항목 PASS.

**산출물**: `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\06_mapping\part2_reference_table.md` (v1.2, PART2 참조 테이블) ✅
</details>

---

### Phase 2: L3 품질 보강

> **목표**: 모든 파일을 L3(구현 즉시 투입 가능) 수준으로 승급
> **판정 기준**: §13 L3 전수 승급 계획 참조

| 단계 | 작업 | 상세 |
|------|------|------|
| 2-1 | I-4 L3 보강 | E1 목적 명시, E2 의사코드, E5 에러 핸들링, E6 성능 벤치마크, E7 테스트 시나리오, E9 의존성 정형화 |
| 2-2 | I-13 L3 보강 | E1 목적, E2 렌더러별 의사코드 + DAG 스케줄링, E3 Pydantic I/O 스키마, E5 에러, E6 성능, E7 테스트, E9 의존성 |
| 2-3 | I-14 L3 보강 | E1 목적, E2 요약/증류 의사코드, E4 ABC 시그니처, E5 에러, E6 성능, E7 테스트, E9 의존성 |
| 2-4 | I-16 L3 보강 | E1 목적, E2 파이프라인/RRF 의사코드, E5 에러, E6 성능 목표, E7 테스트, 캐시 무효화, E9 의존성 |
| 2-5 | S-1 L3 보강 | E1 목적, E2 sliding window 의사코드, E4 ABC 시그니처, E5 에러, E6 엔진 성능, E7 SDAR 통합 테스트, E8 LOCK-AX-03 참조, Prometheus 설정, E9 의존성 |
| 2-6 | 00_common L3 보강 | ResponseEnvelope 직렬화/역직렬화, 에러 핸들링 미들웨어, 타임아웃 데코레이터 |
| 2-7 | 검증 체크리스트 실행 | §10 전 항목 검증 + L3 판정 |

#### Phase 2 단계별 상세 작업 절차

<details>
<summary><b>2-1. I-4 Multimodal Interpreter L3 보강</b></summary>

**대조 기준**:
- §7 세부 작업: 2-1 "I-4 L3 보강"
- §13.1 L3 정의: E1 목적, E2 의사코드, E5 에러 핸들링, E6 성능 벤치마크, E7 테스트 시나리오, E9 의존성 정형화
- §13.3 로드맵: 현재 L2 (E3 보유) → L3 승급 필요, 예상 작업량 **중**
- §6 이슈: 해당 없음 (AUX-01~13 전 항목 Phase 0~1 해결 완료)
- §7 Phase 2→3 전환 게이트: 전 파일 L3 PASS 또는 CONDITIONAL (L3 판정 결과 테이블)
- 교차 도메인: 6-2 Security-Governance (PII 마스킹 정책)
- Part2 버전: V1-Phase 1 (PART2 L1679~1717) + V1-Phase 6 (L2600)

**목표**: I-4 Multimodal Interpreter 모듈의 전 파일(7건)에 E1/E2/E5/E6/E7/E9 요소를 보강하여 §13.1 L3 정의를 충족시킨다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\01_multimodal-interpreter\input_schema.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\01_multimodal-interpreter\format_detection.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\01_multimodal-interpreter\text_pipeline.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\01_multimodal-interpreter\image_pipeline.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\01_multimodal-interpreter\audio_pipeline.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\01_multimodal-interpreter\document_pipeline.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\01_multimodal-interpreter\vision_api_integration.md`
- SOT: `D:\VAMOS\docs\sot\D2.0-01_01. VAMOS_DESIGN_2_0_OVERVIEW.md`
- 본 계획서 §13.1 L3 정의, §13.3 로드맵, §13.4 L3 템플릿

**절차**:
1. 전 파일에 **E1 목적 및 역할** 섹션 추가: 각 파일이 왜 존재하고 어떤 문제를 해결하는지 1~3문단 기술
2. 핵심 파일(format_detection, text/image/audio/document_pipeline)에 **E2 알고리즘 의사코드** 추가: Python-like 단계별 의사코드 (예: format_detection → MIME 타입 분기 로직 의사코드)
3. 전 파일에 **E5 에러 핸들링** 테이블 추가: 발생 가능 에러 유형 + 원인 + 처리 방법 (예: `UnsupportedFormatError`, `TokenLimitExceeded`, `OCRFailure`)
4. 전 파일에 **E6 성능 벤치마크** 추가: 파이프라인별 지연 시간 목표, 처리량, 메모리 제한 (예: text_pipeline P95 < 200ms, image_pipeline P95 < 2s)
5. 전 파일에 **E7 테스트 시나리오** 추가: 정상/비정상/경계값 케이스 최소 3건씩 (예: 빈 입력, 최대 크기 입력, 지원하지 않는 MIME 타입)
6. 전 파일에 **E9 의존성 명세** 추가: 외부 라이브러리(langdetect, chardet, tiktoken, PIL, CLIP, Whisper, docling 등) + 내부 모듈 의존성 목록
7. 기존 E3 (input_schema.md Pydantic 모델) 보존 확인
8. 각 파일 헤더의 `L3 판정: PENDING` 유지 (2-7 단계에서 일괄 판정)

**검증**:
- [x] 7개 파일 × E1 섹션 존재 확인
- [x] 핵심 5개 파일 × E2 의사코드 존재 확인
- [x] 7개 파일 × E5/E6/E7/E9 섹션 존재 확인
- [x] 기존 E3 내용 손상 0건
- [x] Phase 2→3 게이트 매핑: I-4 전 파일 L3 판정 가능 상태 (9요소 전수 기재)

**산출물**: `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\01_multimodal-interpreter\` 하위 7개 파일 (E1/E2/E5/E6/E7/E9 보강)
</details>

<details>
<summary><b>2-2. I-13 Multimodal Renderer L3 보강</b></summary>

**대조 기준**:
- §7 세부 작업: 2-2 "I-13 L3 보강"
- §13.1 L3 정의: E1 목적, E2 렌더러별 의사코드 + DAG 스케줄링, E3 Pydantic I/O 스키마, E5 에러, E6 성능, E7 테스트, E9 의존성
- §13.3 로드맵: 현재 L2 (E4 보유) → L3 승급 필요, 예상 작업량 **중**
- §7 Phase 2→3 전환 게이트: 전 파일 L3 PASS 또는 CONDITIONAL (L3 판정 결과 테이블)
- §6 이월: F-06 Out-of-scope 호출 경로 (스케줄러→I-14, CORE→S-1 활성화) — I-13 DAG 스케줄링 시 관련 경로 명시 필요
- 교차 도메인: 6-2 Security-Governance (PII 마스킹 정책)
- Part2 버전: V1-Phase 1 (PART2 L1679~1717) + V1-Phase 6 (L2600)

**목표**: I-13 Multimodal Renderer 모듈의 전 파일(10건)에 E1/E2/E3/E5/E6/E7/E9 요소를 보강하여 §13.1 L3 정의를 충족시킨다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\02_multimodal-renderer\renderer_interface.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\02_multimodal-renderer\text_renderer.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\02_multimodal-renderer\chart_renderer.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\02_multimodal-renderer\code_renderer.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\02_multimodal-renderer\table_renderer.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\02_multimodal-renderer\diagram_renderer.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\02_multimodal-renderer\audio_renderer.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\02_multimodal-renderer\image_renderer.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\02_multimodal-renderer\composite_output.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\02_multimodal-renderer\quality_validation.md`
- SOT: `D:\VAMOS\docs\sot\D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md`
- 본 계획서 §13.1 L3 정의, §13.3 로드맵, §13.4 L3 템플릿

**절차**:
1. 전 파일에 **E1 목적 및 역할** 섹션 추가
2. 렌더러별 **E2 알고리즘 의사코드** 추가:
   - 개별 렌더러(text/chart/code/table/diagram/audio/image): 각 렌더링 로직 의사코드
   - composite_output: **DAG 스케줄링** 의사코드 (렌더러 간 의존성 해소 + 병렬 실행 로직)
   - quality_validation: 출력물 품질 검증 의사코드
3. 전 파일에 **E3 Pydantic I/O 스키마** 추가: 각 렌더러의 입출력 타입 정의 (RenderRequest, RenderResult 등)
4. 전 파일에 **E5 에러 핸들링** 테이블 추가 (예: `RenderTimeoutError`, `UnsupportedContentType`, `DAGCycleError`)
5. 전 파일에 **E6 성능 목표** 추가: 렌더러별 지연 시간, composite 전체 P95 목표
6. 전 파일에 **E7 테스트 시나리오** 추가: 정상/비정상/경계값 최소 3건씩
7. 전 파일에 **E9 의존성 명세** 추가: 외부 라이브러리 + 내부 모듈 의존성
8. 기존 E4 (renderer_interface.md ABC 시그니처) 보존 확인
9. F-06 관련: composite_output.md에 out-of-scope 호출 경로(스케줄러→I-14) 명시

**검증**:
- [x] 10개 파일 × E1 섹션 존재 확인
- [x] 10개 파일 × E2 의사코드 존재 확인 (composite_output에 DAG 스케줄링 포함)
- [x] 10개 파일 × E3/E5/E6/E7/E9 섹션 존재 확인
- [x] 기존 E4 내용 손상 0건
- [x] F-06 out-of-scope 호출 경로 명시 여부
- [x] Phase 2→3 게이트 매핑: I-13 전 파일 L3 판정 가능 상태 (9요소 전수 기재)

**산출물**: `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\02_multimodal-renderer\` 하위 10개 파일 (E1/E2/E3/E5/E6/E7/E9 보강)
</details>

<details>
<summary><b>2-3. I-14 Summarizer L3 보강</b></summary>

**대조 기준**:
- §7 세부 작업: 2-3 "I-14 L3 보강"
- §13.1 L3 정의: E1 목적, E2 요약/증류 의사코드, E4 ABC 시그니처, E5 에러, E6 성능, E7 테스트, E9 의존성
- §13.3 로드맵: 현재 L2 (E3 보유) → L3 승급 필요, 예상 작업량 **중**
- §7 Phase 2→3 전환 게이트: 전 파일 L3 PASS 또는 CONDITIONAL (L3 판정 결과 테이블)
- §6 이월: F-06 Out-of-scope 호출 경로 (스케줄러→I-14 활성화 경로) 명시 필요
- §6 이월: F-07 ABC 단위 테스트 케이스 도출 (C-01~C-14 14건 기반) — I-14 관련 ABC 테스트 포함
- 교차 도메인: 6-2 Security-Governance (PII 마스킹 정책)
- Part2 버전: V1-Phase 1 (PART2 L1679~1717) + V1-Phase 6 (L2600)

**목표**: I-14 Summarizer 모듈의 전 파일(4건)에 E1/E2/E4/E5/E6/E7/E9 요소를 보강하여 §13.1 L3 정의를 충족시킨다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\03_summarizer\input_output_schema.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\03_summarizer\conversation_summary.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\03_summarizer\memory_distillation.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\03_summarizer\trigger_conditions.md`
- SOT: `D:\VAMOS\docs\sot\D2.0-01_01. VAMOS_DESIGN_2_0_OVERVIEW.md`
- 본 계획서 §13.1 L3 정의, §13.3 로드맵, §13.4 L3 템플릿

**절차**:
1. 전 파일에 **E1 목적 및 역할** 섹션 추가: 요약/증류 기능의 존재 이유와 해결 문제 기술
2. 핵심 파일에 **E2 알고리즘 의사코드** 추가:
   - conversation_summary: 대화 요약 알고리즘 의사코드 (청크 분할 → 핵심 추출 → 압축)
   - memory_distillation: 메모리 증류 알고리즘 의사코드 (L0→L1→L2→L3 계층 이동 로직)
   - trigger_conditions: 트리거 조건 평가 의사코드
3. 전 파일에 **E4 ABC 시그니처** 추가: ISummarizer, IDistiller 등 ABC 메서드 시그니처 (파라미터 + 리턴 타입)
4. 전 파일에 **E5 에러 핸들링** 테이블 추가 (예: `SummaryTooLongError`, `DistillationFailure`, `TriggerEvaluationTimeout`)
5. 전 파일에 **E6 성능 목표** 추가: 요약 처리 시간 P95, 증류 배치 처리량
6. 전 파일에 **E7 테스트 시나리오** 추가: 정상/비정상/경계값 최소 3건씩 + F-07 관련 ABC 단위 테스트 케이스(C-01~C-14 중 I-14 해당분)
7. 전 파일에 **E9 의존성 명세** 추가
8. 기존 E3 (input_output_schema.md) 보존 확인
9. F-06 관련: 스케줄러→I-14 활성화 호출 경로를 trigger_conditions.md에 명시

**검증**:
- [x] 4개 파일 × E1 섹션 존재 확인
- [x] 핵심 3개 파일 × E2 의사코드 존재 확인
- [x] 4개 파일 × E4/E5/E6/E7/E9 섹션 존재 확인
- [x] 기존 E3 내용 손상 0건
- [x] F-06 스케줄러→I-14 호출 경로 명시 여부
- [x] F-07 ABC 단위 테스트 케이스 I-14 해당분 포함 여부
- [x] Phase 2→3 게이트 매핑: I-14 전 파일 L3 판정 가능 상태 (9요소 전수 기재)

**산출물**: `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\03_summarizer\` 하위 4개 파일 (E1/E2/E4/E5/E6/E7/E9 보강)
</details>

<details>
<summary><b>2-4. I-16 Knowledge Search L3 보강</b></summary>

**대조 기준**:
- §7 세부 작업: 2-4 "I-16 L3 보강"
- §13.1 L3 정의: E1 목적, E2 파이프라인/RRF 의사코드, E5 에러, E6 성능 목표, E7 테스트, 캐시 무효화, E9 의존성
- §13.3 로드맵: 현재 L2~L3 (E3/E4/E8 보유) → L3 승급 필요, 예상 작업량 **중** (소→중 상향)
- §7 Phase 2→3 전환 게이트: 전 파일 L3 PASS 또는 CONDITIONAL (L3 판정 결과 테이블)
- §3.4 LOCK: RAG hybrid search ratio alpha=0.3(BM25) + 0.7(vector), Embedding BGE-M3 (1024-dim, Matryoshka 256-dim), VectorStore adapter (upsert/search/delete/get_by_id), Semantic cache cosine_similarity >= 0.95 TTL 24h
- §6 이월: F-04 timeout_policy.md §2 표 확장 (I-16 내부 4종 정본화)
- §6 이월: F-10 fallback_chain.md F-XXX-NN ID 22개 → D2.0-02 §6.3 Fallback Registry 등재
- 교차 도메인: 6-2 Security-Governance (PII 마스킹 정책)
- Part2 버전: V1-Phase 1 (PART2 L1679~1717) + V1-Phase 6 (L2600)

**목표**: I-16 Knowledge Search 모듈의 전 파일(4건)에 E1/E2/E5/E6/E7/E9 + 캐시 무효화 요소를 보강하여 §13.1 L3 정의를 충족시킨다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\04_knowledge-search\search_api.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\04_knowledge-search\search_pipeline.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\04_knowledge-search\rag_integration.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\04_knowledge-search\external_sources.md`
- SOT: `D:\VAMOS\docs\sot\D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md` (§6.3 Fallback Registry)
- SOT: `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md`
- 본 계획서 §13.1 L3 정의, §13.3 로드맵, §13.4 L3 템플릿

**절차**:
1. 전 파일에 **E1 목적 및 역할** 섹션 추가
2. 핵심 파일에 **E2 알고리즘 의사코드** 추가:
   - search_pipeline: **RRF (Reciprocal Rank Fusion)** 의사코드 — BM25(alpha=0.3) + Vector(0.7) 하이브리드 검색 파이프라인
   - rag_integration: RAG 통합 의사코드 — BGE-M3 임베딩(1024-dim, Matryoshka 256-dim) + VectorStore adapter 호출
   - search_api: API 엔드포인트 → 파이프라인 라우팅 의사코드
3. 전 파일에 **E5 에러 핸들링** 테이블 추가 (예: `VectorStoreConnectionError`, `EmbeddingTimeoutError`, `CacheInvalidationFailure`)
4. 전 파일에 **E6 성능 목표** 추가: 검색 P95 지연 시간, 처리량 목표, 캐시 히트율 목표
5. **캐시 무효화** 로직 추가: Semantic cache (cosine_similarity >= 0.95, TTL 24h) 무효화 시나리오 + 의사코드
6. 전 파일에 **E7 테스트 시나리오** 추가: 정상/비정상/경계값 최소 3건씩 + 캐시 무효화 테스트
7. 전 파일에 **E9 의존성 명세** 추가
8. 기존 E3/E4/E8 보존 확인
9. F-04 관련: search_pipeline.md 또는 search_api.md에 I-16 내부 타임아웃 4종 정본화 (00_common/timeout_policy.md §2 표와 정합)
10. F-10 관련: fallback ID 22개 중 I-16 해당분 → D2.0-02 §6.3 Fallback Registry 등재 경로 명시

**검증**:
- [x] 4개 파일 × E1 섹션 존재 확인
- [x] 핵심 3개 파일 × E2 의사코드 존재 확인 (RRF 공식 포함)
- [x] 4개 파일 × E5/E6/E7/E9 섹션 존재 확인
- [x] 캐시 무효화 로직 + 테스트 시나리오 존재 확인
- [x] 기존 E3/E4/E8 내용 손상 0건
- [x] F-04 타임아웃 4종 정본화 반영 여부
- [x] F-10 Fallback Registry 등재 경로 명시 여부
- [x] LOCK 값 정합: alpha=0.3/0.7, BGE-M3 1024-dim, cosine >= 0.95, TTL 24h
- [x] Phase 2→3 게이트 매핑: I-16 전 파일 L3 판정 가능 상태 (9요소 전수 기재)

**산출물**: `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\04_knowledge-search\` 하위 4개 파일 (E1/E2/E5/E6/E7/E9 + 캐시 무효화 보강)
</details>

<details>
<summary><b>2-5. S-1 Self-check L3 보강</b></summary>

**대조 기준**:
- §7 세부 작업: 2-5 "S-1 L3 보강"
- §13.1 L3 정의: E1 목적, E2 sliding window 의사코드, E4 ABC 시그니처, E5 에러, E6 엔진 성능, E7 SDAR 통합 테스트, E8 LOCK-AX-03 참조, Prometheus 설정, E9 의존성
- §13.3 로드맵: 현재 L2 (E3 보유) → L3 승급 필요, 예상 작업량 **중**
- §7 Phase 2→3 전환 게이트: 전 파일 L3 PASS 또는 CONDITIONAL (L3 판정 결과 테이블)
- §3.4 LOCK: LOCK-AX-03 QoD = Accuracy×0.30 + Relevance×0.25 + Completeness×0.20 + Safety×0.15 + Efficiency×0.10
- §3.4 LOCK: LOCK-AX-13 상태 머신 S0~S8, S3 Decision Lock 불변
- §6 이월: F-05 S-1 ↔ I-15 실 통합 여부 결정
- §6 이월: F-06 Out-of-scope 호출 경로 (CORE→S-1 활성화) 명시 필요
- §6 이월: F-07 ABC 단위 테스트 케이스 도출 (C-01~C-14 14건 기반) — S-1 관련 ABC 테스트 포함
- 교차 도메인: 6-2 Security-Governance PII 마스킹 정책 (S-1 자기 점검 시 PII 포함 응답 처리)
- 교차 도메인: 6-2 Security-Governance (PII 마스킹 정책)
- Part2 버전: V1-Phase 1 (PART2 L1679~1717) + V1-Phase 6 (L2600)

**목표**: S-1 Self-check 모듈의 전 파일(5건)에 E1/E2/E4/E5/E6/E7/E8/E9 + Prometheus 설정 요소를 보강하여 §13.1 L3 정의를 충족시킨다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\05_self-check\qod_formula.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\05_self-check\check_engine.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\05_self-check\sliding_window.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\05_self-check\sdar_integration.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\05_self-check\prometheus_metrics.md`
- SOT: `D:\VAMOS\docs\sot\D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md`
- SOT: `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md`
- 본 계획서 §13.1 L3 정의, §13.3 로드맵, §13.4 L3 템플릿

**절차**:
1. 전 파일에 **E1 목적 및 역할** 섹션 추가: QoD 기반 자기 점검 체계의 존재 이유
2. 핵심 파일에 **E2 알고리즘 의사코드** 추가:
   - sliding_window: **sliding window** 의사코드 — 최근 N개 응답에 대한 QoD 이동 평균 계산
   - check_engine: 점검 엔진 실행 의사코드 — 5-factor 가중 합산 + 임계값 판정
   - qod_formula: LOCK-AX-03 QoD 공식 구현 의사코드
3. 전 파일에 **E4 ABC 시그니처** 추가: ISelfChecker, IQoDCalculator 등 ABC 메서드 시그니처
4. 전 파일에 **E5 에러 핸들링** 테이블 추가 (예: `QoDCalculationError`, `WindowSizeExceeded`, `SDARConnectionTimeout`)
5. 전 파일에 **E6 엔진 성능** 추가: QoD 계산 P95 지연, sliding window 업데이트 처리량, 메모리 제한
6. 전 파일에 **E7 테스트 시나리오** 추가:
   - 정상/비정상/경계값 최소 3건씩
   - **SDAR 통합 테스트**: S-1↔SDAR 6-5 연동 시나리오 (정상 전달, 연결 실패, 타임아웃)
   - F-07 관련 ABC 단위 테스트 케이스(C-01~C-14 중 S-1 해당분)
7. 전 파일에 **E8 LOCK 참조** 섹션 추가/보강: LOCK-AX-03 (QoD 5-factor), LOCK-AX-13 (상태 머신 S0~S8) 명시적 참조
8. prometheus_metrics.md에 **Prometheus 설정** 상세화: 메트릭 이름, 라벨, 수집 주기, 알림 조건
9. 전 파일에 **E9 의존성 명세** 추가
10. 기존 E3 보존 확인
11. F-05 관련: S-1 ↔ I-15 통합 여부 결정 사항을 check_engine.md 또는 sdar_integration.md에 기술 (결정 보류 시 OPEN 이슈로 표시)
12. F-06 관련: CORE→S-1 활성화 호출 경로를 check_engine.md에 명시

**검증**:
- [x] 5개 파일 × E1 섹션 존재 확인
- [x] 핵심 3개 파일 × E2 의사코드 존재 확인 (sliding window + QoD 공식 포함)
- [~] 5개 파일 × E4/E5/E6/E7/E9 섹션 존재 확인
- [x] E8 LOCK 참조: LOCK-AX-03, LOCK-AX-13 명시 확인
- [x] Prometheus 설정 상세화 확인
- [x] SDAR 통합 테스트 시나리오 존재 확인
- [x] 기존 E3 내용 손상 0건
- [x] F-05 S-1↔I-15 통합 결정 기술/OPEN 표시 여부
- [x] F-06 CORE→S-1 호출 경로 명시 여부
- [x] F-07 ABC 단위 테스트 케이스 S-1 해당분 포함 여부
- [x] LOCK 값 정합: QoD 5-factor 가중치 합 = 1.0
- [x] 6-2 Security-Governance PII 마스킹 정책 참조 여부
- [x] Phase 2→3 게이트 매핑: S-1 전 파일 L3 판정 가능 상태 (9요소 전수 기재)

**산출물**: `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\05_self-check\` 하위 5개 파일 (E1/E2/E4/E5/E6/E7/E8/E9 + Prometheus 보강)
</details>

<details>
<summary><b>2-6. 00_common L3 보강</b></summary>

**대조 기준**:
- §7 세부 작업: 2-6 "00_common L3 보강"
- §13.1 L3 정의: ResponseEnvelope 직렬화/역직렬화, 에러 핸들링 미들웨어, 타임아웃 데코레이터
- §3.4 LOCK: LOCK-AX-11 ResponseEnvelope minimum spec (answer/evidence/self_check/decision_ref/audit 필수, D2.0-02 §5.1.1)
- §7 Phase 2→3 전환 게이트: 전 파일 L3 PASS 또는 CONDITIONAL (L3 판정 결과 테이블)
- §6 이월: F-04 timeout_policy.md §2 표 확장 (I-19/I-8/I-25/S-1 내부 4종 정본화)
- §6 이월: F-11 §2.1 ↔ 디스크 7건 차이 정정
- 교차 도메인: 6-2 Security-Governance (PII 마스킹 정책)
- Part2 버전: V1-Phase 1 (PART2 L1679~1717) + V1-Phase 6 (L2600)

**목표**: 00_common 폴더의 전 파일(4건)에 L3 수준 보강을 수행한다. ResponseEnvelope 직렬화/역직렬화, 에러 핸들링 미들웨어, 타임아웃 데코레이터를 구현 가능 수준으로 상세화한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\00_common\response_envelope.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\00_common\common_types.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\00_common\error_taxonomy.md`
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\00_common\timeout_policy.md`
- SOT: `D:\VAMOS\docs\sot\D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md` (§5.1.1 ResponseEnvelope)
- 본 계획서 §13.1 L3 정의, §13.4 L3 템플릿

**절차**:
1. **response_envelope.md** L3 보강:
   - E1: ResponseEnvelope의 목적 (LOCK-AX-11 준수, 전 모듈 공통 응답 래퍼)
   - E2: 직렬화(→JSON/MessagePack)/역직렬화 의사코드
   - E3: Pydantic 모델 상세화 (answer, evidence, self_check, decision_ref, audit 필수 필드)
   - E4: IResponseEnvelope ABC 시그니처 (serialize, deserialize, validate)
   - E5: 에러 핸들링 (직렬화 실패, 필수 필드 누락, 스키마 버전 불일치)
   - E6: 직렬화/역직렬화 P95 성능 목표
   - E7: 테스트 시나리오 (정상, 필드 누락, 대용량 evidence)
   - E8: LOCK-AX-11 참조 명시
   - E9: 의존성 명세 (pydantic, msgpack 등)
2. **error_taxonomy.md** L3 보강:
   - E1: 에러 분류 체계의 목적
   - E2: 에러 핸들링 미들웨어 의사코드 (에러 포착 → 분류 → ResponseEnvelope 래핑 → 로깅)
   - E5: 에러 타입별 재시도 정책 + fallback 체인
   - E7: 에러 시나리오 테스트 (cascade 실패, 미분류 에러)
3. **timeout_policy.md** L3 보강:
   - E1: 타임아웃 정책의 목적
   - E2: 타임아웃 데코레이터 의사코드 (`@timeout(seconds)` 패턴)
   - F-04: §2 표 확장 — I-19/I-8/I-25/S-1 내부 4종 타임아웃 값 정본화
   - E7: 타임아웃 발생 시 테스트 시나리오
4. **common_types.md** L3 보강: E1/E3/E9 추가
5. F-11 관련: §2.1 트리 vs 디스크 7건 차이 중 00_common 관련 항목 정정

**검증**:
- [x] 4개 파일 × E1 섹션 존재 확인
- [x] response_envelope.md E2/E3/E4/E5/E6/E7/E8/E9 전수 확인
- [x] error_taxonomy.md 에러 핸들링 미들웨어 의사코드 존재 확인
- [x] timeout_policy.md 타임아웃 데코레이터 의사코드 존재 확인
- [x] F-04 타임아웃 4종 정본화 §2 표 확장 반영 여부
- [~] F-11 §2.1 ↔ 디스크 차이 정정 반영 여부 (00_common 해당분)
- [x] LOCK-AX-11 정합: answer/evidence/self_check/decision_ref/audit 필수 필드 일치
- [x] Phase 2→3 게이트 매핑: 00_common 전 파일 L3 판정 가능 상태

**산출물**: `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\00_common\` 하위 4개 파일 (ResponseEnvelope 직렬화/역직렬화, 에러 미들웨어, 타임아웃 데코레이터 보강)
</details>

<details>
<summary><b>2-7. 검증 체크리스트 실행 + L3 판정</b></summary>

**대조 기준**:
- §7 세부 작업: 2-7 "검증 체크리스트 실행"
- §10 검증 체크리스트 전 항목 (V-01 ~ V-22+)
- §13.2 L3 판정 기준: PASS (9요소 전수) / CONDITIONAL (7~8요소, 30일 보완) / FAIL (6요소 이하, 재작업)
- §7 Phase 2→3 전환 게이트: 전 파일 L3 PASS 또는 CONDITIONAL (L3 판정 결과 테이블)
- §6 이월 전체: F-04, F-05, F-06, F-07, F-10, F-11 해소 여부 최종 확인
- 교차 도메인: 6-2 Security-Governance (PII 마스킹 정책)
- Part2 버전: V1-Phase 1 (PART2 L1679~1717) + V1-Phase 6 (L2600)

**목표**: §10 검증 체크리스트 전 항목을 재실행하고, 2-1~2-6에서 보강한 전 파일에 대해 §13.2 기준으로 L3 판정을 수행한다. Phase 2→3 전환 게이트 충족 여부를 확정한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\` 하위 전체 파일 (01~05 + 00_common)
- 본 계획서 §10 검증 체크리스트
- 본 계획서 §13.1 L3 정의, §13.2 L3 판정 기준

**절차**:
1. **§10 검증 체크리스트 전 항목 재실행**:
   - V-01 ~ V-05: 기반 산출물 존재 + 정합성 확인
   - V-06 ~ V-10: 파일 구조, 헤더, 줄 회계, 중복 검증
   - V-11+: 추가 검증 항목 전수 확인
2. **L3 요소 전수 확인** (파일당):
   - 각 파일에 E1~E9 중 해당 요소 존재 여부 체크 (§13.3 로드맵 기준)
   - E2 의사코드 내용 충실도 확인 (단순 TODO/placeholder 불인정)
   - E4 ABC 시그니처 파라미터 + 리턴 타입 명시 여부
3. **L3 판정 수행** (§13.2 기준):
   - PASS: 9요소 전수 기재 + E2 의사코드 포함 + E4 시그니처 포함
   - CONDITIONAL: 7~8요소 (E6 또는 E7 1건 누락 허용) → 30일 보완 기한 기록
   - FAIL: 6요소 이하 → Phase 2 재작업 대상 기록
4. **L3 판정 결과 테이블 작성**: 모듈별 × 파일별 판정 결과 + 누락 요소 + 보완 기한
5. **§6 이월 항목 해소 확인**:
   - F-04: timeout_policy §2 표 확장 완료 여부
   - F-05: S-1↔I-15 통합 결정 완료/OPEN 여부
   - F-06: Out-of-scope 호출 경로 명시 완료 여부
   - F-07: ABC 단위 테스트 케이스 도출 완료 여부
   - F-10: Fallback Registry 등재 경로 명시 완료 여부
   - F-11: §2.1↔디스크 차이 정정 완료 여부
6. **Phase 2→3 전환 게이트 판정**: 전 파일 L3 PASS 또는 CONDITIONAL 달성 시 Phase 3 진입 가능
7. 각 파일 헤더 `L3 판정: PENDING` → `L3 판정: PASS/CONDITIONAL/FAIL` 갱신
8. 본 계획서 §11 L3 판정 결과 행 갱신: `PENDING` → 실제 판정 결과

**검증**:
- [x] §10 전 항목 PASS 확인
- [x] 전 파일 L3 판정 완료 (PENDING 잔존 0건)
- [x] L3 FAIL 파일 0건 (또는 재작업 계획 수립)
- [x] F-04/F-05/F-06/F-07/F-10/F-11 해소 상태 확정
- [x] L3 판정 결과 테이블 작성 완료
- [x] Phase 2→3 전환 게이트: 전 파일 L3 PASS 또는 CONDITIONAL → Phase 3 진입 가능 판정

**산출물**:
- L3 판정 결과 테이블 (본 계획서 §11 또는 별도 섹션)
- 전 파일 헤더 L3 판정 갱신
- §6 이월 항목 해소 상태 갱신
- Phase 2→3 전환 게이트 판정 결과
</details>

### Phase 3: 최종 검증 + 승인 ✅ Phase 3 완료 (2026-05-14, 6 task)

> **목표**: 전체 문서 검증, APPROVED 상태 전환, PART2 최종 동기화

| 단계 | 작업 | 상세 |
|------|------|------|
| 3-1 | 전 파일 L3 판정 | §13 L3 기준으로 전 파일 판정 (PASS/CONDITIONAL/FAIL) |
| 3-2 | CONDITIONAL 파일 보완 | L3 CONDITIONAL 판정 파일 30일 내 보완 |
| 3-3 | 최종 검증 체크리스트 | §10 전 항목 재검증 |
| 3-4 | Status 전환 | 전 파일 DRAFT → APPROVED |
| 3-5 | PART2 최종 동기화 | PART2 링크 테이블 최종 갱신 |
| 3-6 | INDEX.md 최종 갱신 | 파일 수, Status, Version 최종 업데이트 |

### Phase 전환 게이트

| 전환 | 게이트 조건 | 검증 방법 |
|------|-----------|----------|
| Phase 0 → 1 | 선행작업 5건 전수 완료 | 산출물 5건 확인: 0-1 AUTHORITY_CHAIN.md 존재, 0-2 lock_value_registry.md 존재, **0-3 §5B "확정일" 태그 존재** (인라인 산출물), 0-4 cross_module_dedup.md 존재, 0-5 CONFLICT_LOG.md 존재 |
| Phase 1 → 2 | 폴더 구조 완성 + 40+ 파일 존재 + 전 파일 헤더 보유 | 파일 수 검증 + grep Status: |
| Phase 2 → 3 | 전 파일 L3 PASS 또는 CONDITIONAL | L3 판정 결과 테이블 |
| Phase 3 완료 | 전 파일 APPROVED + PART2 동기화 | 최종 체크리스트 |

#### Phase 3 단계별 상세 작업 절차

> **STAGE 9 inheritance 인지**: 본 도메인은 STAGE 9 Phase A (chain s9_35_a_1 → s9_36_a_2 → s9_37_a_3 → s9_38_a_4) 4 step ALL COMPLETE Production 승급 완료 (2026-05-12). 본 Phase 3 프롬프트의 3-1 ~ 3-6 작업은 STAGE 9 Phase A 결과를 verifying·finalizing 하는 절차이며, 신규 V2 35 파일 + AUTHORITY v1.2 + CONFLICT v2.1 + INDEX v2.0 (DRAFT→APPROVED) + 5 _index footer + production sync 결과를 cross-check 한다.

<details>
<summary><b>3-1. 전 파일 L3 판정 (PASS/CONDITIONAL/FAIL)</b></summary>

**대조 기준 (7항목)**:
- §7 세부 작업: 3-1 "전 파일 L3 판정"
- §7 전환 게이트: Phase 2 → 3 (전 파일 L3 PASS 또는 CONDITIONAL → L3 판정 결과 테이블) + V-17 L3 판정
- §6 이슈: STAGE 9 Phase A inheritance — F-04 (timeout §2 표 4 신규 정본화) RESOLVED + F-06 (out-of-scope 호출 경로) RESOLVED + F-05/F-07/F-10/F-11 STEP_C 처리 + D-01 DEFERRED-EXTERNAL_DEPENDENCY + D-02 RESOLVED-PARTIAL
- 교차 도메인: 6-2 Security-Governance (PII 마스킹 정책 — STAGE 9 STEP_C 31 V2 / 244 raw refs 광범위 sync)
- Part2 V3-Phase: V1-Phase 1 (PART2 L1679~1717 보조 모듈) + V1-Phase 6 (L2600 AI Investing MVP+MCP 참조)
- production 측정 baseline: STAGE 9 Phase A 산출 — 42 V1 + 35 V2 = 77 파일 total (L3 PASS 22 + CONDITIONAL 12 + FAIL 0 STEP_B 결과 + STEP_C truly_converged_v3 재검증 + 본 §13.1 9요소 + Algorithm 의사코드/수식 + Class/API 시그니처)
- Phase 4 entry-gate 충족 조건: L3 PASS ≥ 90% + L3 FAIL 0건 + 30일 보완 기한 CONDITIONAL row 명시 + L3 판정 결과 테이블 SoT

**목표**: 본 계획서 §13.1 L3 기준 (E1~E9 9요소) + Algorithm 의사코드/수식 + Class/API 시그니처를 기준으로 sot 2/1-2_Auxiliary-Modules/ 전 파일(42 V1 + 35 V2 = 77 파일)을 PASS / CONDITIONAL (E6 또는 E7 1건 누락) / FAIL (≤6요소) 3단계로 판정한다. STAGE 9 Phase A STEP_B 결과(PASS 22 + CONDITIONAL 12 + FAIL 0)를 STEP_C truly_converged_v3 결과로 재검증한다.

**입력 파일**:
- 본 계획서 §13.1 L3 기준 (E1~E9) + §13.4 L3 템플릿
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\` 하위 전 .md 파일 (42 V1 + 35 V2 = 77 파일, STAGE 9 Phase A 결과)
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\_verification\phase2_verification_v2.md` (STAGE 9 STEP_B PASS 22 + CONDITIONAL 12 + FAIL 0 결과 + STEP_C 후속 처리 항목)
- STAGE 9 Phase A STEP_C truly_converged_v3 산출물 (1-2 폴더 inheritance, 별도 _verification .md 미생성): AUTHORITY_CHAIN.md v1.2 + CONFLICT_LOG.md v2.1 + INDEX.md v2.0 + V2 35 NEW + 5 _index footer 갱신
- production .md 정본: 42 V1 + 35 V2 = 77 파일 STAGE 9 Phase A production sync 결과

**절차**:
1. STAGE 9 Phase A STEP_B 결과(PASS 22 + CONDITIONAL 12 + FAIL 0)를 baseline으로 inherit.
2. STAGE 9 Phase A STEP_C truly_converged_v3 결과로 cross-check (R₁~R₈ 0 changes cascade).
3. STAGE 9 Phase A 이후 추가 V2 35 파일 각각의 §13.1 9요소 PASS 여부 점검.
4. L3 판정 결과 테이블 작성 (전 77 파일 × E1~E9 = 693 cells 매트릭스).
5. PASS / CONDITIONAL / FAIL 분포 산출 + L3 완성도 리포트 작성.
6. FAIL 발견 시 → Phase 2 재작업 루프 (최대 3회).
7. production 실측 측정: L3 PASS 수 / CONDITIONAL 수 / FAIL 수 + L3 완성률(PASS/total) + 9요소 매트릭스 cells PASS.
8. Phase 4 entry-gate 충족 여부 확인 (L3 PASS ≥ 90% + FAIL 0건).

**검증**:
- [x] STAGE 9 Phase A STEP_B 결과 baseline 확인 (PASS 22 + CONDITIONAL 12 + FAIL 0)
- [x] STEP_C truly_converged_v3 cross-check (R₁~R₈ 0 changes)
- [x] V2 35 파일 §13.1 9요소 PASS 여부 점검
- [x] L3 판정 결과 테이블 SoT 작성 (77 × 9 = 693 cells)
- [x] L3 PASS ≥ 90% + FAIL 0건
- [x] production 측정 결과: L3 완성률 + 9요소 매트릭스
- [x] Phase 4 entry-gate 충족 조건 PASS (V-17 L3 판정 PASS)

**산출물**: `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\_verification\l3_judgment_phase3_v1.md` (L3 판정 결과 테이블 77 × 9 = 693 cells) + 본 계획서 §13 L3 판정 결과 row update
</details>

<details>
<summary><b>3-2. CONDITIONAL 파일 보완 (30일 보완 기한)</b></summary>

**대조 기준 (7항목)**:
- §7 세부 작업: 3-2 "CONDITIONAL 파일 보완 (L3 CONDITIONAL 판정 파일 30일 내 보완)"
- §7 전환 게이트: Phase 2 → 3 (CONDITIONAL → PASS 30일 내) + L3 FAIL 0건 유지
- §6 이슈: STAGE 9 Phase A STEP_B에서 CONDITIONAL 12 row → CONDITIONAL 본 Phase 3.2에서 PASS 승급 보완 대상
- 교차 도메인: 6-2 Security-Governance (PII 마스킹 정책 — CONDITIONAL row에 E7 Security 미흡 영역 보완 시 참조)
- Part2 V3-Phase: V1-Phase 1 (PART2 L1679~1717) + V1-Phase 6 (L2600)
- production 측정 baseline: STAGE 9 Phase A STEP_B CONDITIONAL 12 row baseline + 30일 보완 기한 (~2026-06-09 까지, phase2_verification_v2.md L77 SoT 정합)
- Phase 4 entry-gate 충족 조건: CONDITIONAL 12 row → PASS 승급 90% 이상 + REVIEW Status 명시 + Last-reviewed 갱신

**목표**: STAGE 9 Phase A STEP_B에서 L3 CONDITIONAL 판정된 12 row를 30일 보완 기한 내에 E6 Performance 또는 E7 Security 미흡 요소를 보강하여 L3 PASS로 승급한다. 보완 어려운 row는 REVIEW Status 유지 + 보완 기한 명시.

**입력 파일**:
- 3-1 산출물: `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\_verification\l3_judgment_phase3_v1.md`
- 본 계획서 §13.1 L3 기준 + §13.4 L3 템플릿
- CONDITIONAL 12 row 해당 V1/V2 파일 (STAGE 9 Phase A STEP_B 결과)
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\06_mapping\interface_contracts.md` C-01~C-14 ABC (E4 시그니처 보완 시 참조)
- 6-2 Security-Governance PII 마스킹 정책 (E7 Security 보강 참조)

**절차**:
1. CONDITIONAL 12 row 목록 + 미흡 요소(E6 Performance 또는 E7 Security) 식별.
2. 각 row에 대해 30일 보완 기한 내 보강 작업 계획 수립.
3. E6 Performance: P95 응답시간 목표 + 토큰 한도 + RPS 목표 추가 (V1/V2 영역 정합).
4. E7 Security: 6-2 Security-Governance PII 마스킹 정책 cross-ref + 인증/권한/감사 항목 추가.
5. 보강 후 §13.1 9요소 재판정 → L3 PASS 승급.
6. 보강 어려운 row: REVIEW Status 유지 + Last-reviewed 갱신 + 보완 기한 명시.
7. AUTHORITY_CHAIN.md LOCK-AX-* + DEFINED-HERE 영역 byte EXACT 보존 (STAGE 9 LOCK count duality 위반 0건).
8. production 실측 측정: CONDITIONAL 12 row → PASS 승급 수 + REVIEW 잔존 row + 30일 보완 기한 row.
9. Phase 4 entry-gate 충족 여부 확인 (CONDITIONAL → PASS ≥ 90%).

**검증**:
- [x] CONDITIONAL 12 row 식별 + 미흡 요소 분류
- [x] 각 row 보완 작업 계획 + 30일 보완 기한 명시
- [x] E6 Performance / E7 Security 보강 적용
- [~] L3 PASS 승급 ≥ 90% (CONDITIONAL → PASS)
- [x] AUTHORITY_CHAIN LOCK-AX 영역 byte EXACT 보존 (LOCK count duality)
- [x] production 측정 결과: PASS 승급 수 + REVIEW 잔존 + 보완 기한 row
- [~] Phase 4 entry-gate 충족 조건 PASS (CONDITIONAL 90% 이상 PASS)

**산출물**: `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\_verification\l3_conditional_remediation_phase3.md` (CONDITIONAL 12 row 보완 결과 + 잔존 REVIEW row 보완 기한 매트릭스)
</details>

<details>
<summary><b>3-3. 최종 검증 체크리스트 (V-01~V-24 전 항목 재검증)</b></summary>

**대조 기준 (7항목)**:
- §7 세부 작업: 3-3 "최종 검증 체크리스트 (§10 전 항목 재검증)"
- §7 전환 게이트: §10.4 Phase 3 완료 검증 V-21 / V-22 / V-23 / V-24 전수 PASS
- §6 이슈: STAGE 9 Phase A에서 §10.1 ~ §10.3 (Phase 0~2) 전수 PASS 마킹 inheritance — V-01 ~ V-20 전수 PASS
- 교차 도메인: 6-2 Security-Governance (PII 마스킹 V-14 ResponseEnvelope 정합) + 6-12 Event-Logging (해당 시)
- Part2 V3-Phase: V1-Phase 1 + V1-Phase 6 PART2 정본 선언 V-22 검증
- production 측정 baseline: STAGE 9 Phase A V-01 ~ V-20 전수 PASS inheritance + Phase 3 V-21 ~ V-24 신규 검증 항목
- Phase 4 entry-gate 충족 조건: V-01 ~ V-24 24개 항목 전수 PASS + L3 판정 결과 + PART2 동기화 + INDEX.md 최종 + _archive/ 무결

**목표**: 본 계획서 §10 검증 체크리스트 24개 항목 (V-01 ~ V-24) 전수를 재검증하여 Phase 3 완료 조건을 확정한다. STAGE 9 Phase A에서 V-01 ~ V-20 PASS inheritance를 cross-check 하고, V-21 ~ V-24 Phase 3 신규 항목을 본 단계에서 검증한다.

**입력 파일**:
- 본 계획서 §10.1 Phase 0 완료 검증 (V-01 ~ V-05) — STAGE 9 inheritance
- 본 계획서 §10.2 Phase 1 완료 검증 (V-06 ~ V-16) — STAGE 9 inheritance + 11/11 PASS
- 본 계획서 §10.3 Phase 2 완료 검증 (V-17 ~ V-20) — 3-1 ~ 3-2 산출 후 cross-check
- 본 계획서 §10.4 Phase 3 완료 검증 (V-21 ~ V-24)
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\AUTHORITY_CHAIN.md` (LOCK-AX 정합)
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\06_mapping\lock_value_registry.md` (LOCK 19건 등재)
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\06_mapping\cross_module_dedup.md` (DG-01~DG-07 정본)
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\CONFLICT_LOG.md` (CF-AUX 3 + F-01~F-11 11건 OPEN 0 — RESOLVED 9 + SCOPE_OUT 2 (F-02/F-03 외부 의존) + D-01 DEFERRED-EXTERNAL + D-02 RESOLVED-PARTIAL, STAGE 9 STEP_C 2026-05-10 통산)
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\INDEX.md` (3-6 산출 후 cross-check)

**절차**:
1. §10.1 ~ §10.3 V-01 ~ V-20 STAGE 9 Phase A inheritance 결과 cross-check (모두 PASS 마킹).
2. §10.4 V-21 전 파일 Status: `grep "Status: APPROVED"` 카운트 = 파일 수.
3. §10.4 V-22 PART2 링크 단일 테이블 갱신 완료 + 정본 선언 2개소 존재.
4. §10.4 V-23 INDEX.md 최종 (파일 수 + Status + Version 최신).
5. §10.4 V-24 _archive/ 원본 미변경 확인 (byte-identical).
6. V-14 ResponseEnvelope D2.0-02 §5.1.1 LOCK 사양 준수 + 6-2 Security-Governance PII 마스킹 정합.
7. V-15 인터페이스 계약 C-01~C-14 14건 전수 등록 확인.
8. V-16 module_dependency_graph.md v1.1 노드 14 / 엣지 19 / cycle 0.
9. production 실측 측정: V-01 ~ V-24 24개 항목 PASS/FAIL 매트릭스 + STAGE 9 inheritance 비율.
10. Phase 4 entry-gate 충족 여부 확인 (V-21 ~ V-24 전수 PASS).

**검증**:
- [x] §10.1 ~ §10.3 V-01 ~ V-20 STAGE 9 inheritance 전수 PASS 마킹
- [x] V-21 전 파일 Status APPROVED 확인
- [x] V-22 PART2 링크 + 정본 선언 2개소 PASS
- [x] V-23 INDEX.md 최종 갱신 PASS
- [x] V-24 _archive/ 원본 byte-identical PASS
- [x] V-14 ResponseEnvelope + 6-2 PII 마스킹 정합
- [x] production 측정 결과: 24개 항목 PASS 매트릭스 + STAGE 9 inheritance
- [x] Phase 4 entry-gate 충족 조건 PASS (전 체크리스트 PASS)

**산출물**: `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\_verification\phase3_final_checklist_v_01_24.md` (V-01 ~ V-24 24개 항목 PASS/FAIL 매트릭스)
</details>

<details>
<summary><b>3-4. Status 전환 (전 파일 DRAFT → APPROVED)</b></summary>

**대조 기준 (7항목)**:
- §7 세부 작업: 3-4 "Status 전환 (전 파일 DRAFT → APPROVED)"
- §7 전환 게이트: Phase 3 완료 (전 파일 APPROVED + PART2 동기화) + V-21 PASS
- §6 이슈: STAGE 9 Phase A에서 INDEX 헤더 v1.0+body v1.2/v1.3 → v2.0 + Status DRAFT → APPROVED inheritance
- 교차 도메인: 없음 (메타데이터 갱신)
- Part2 V3-Phase: V1-Phase 1 + V1-Phase 6 SHELL→FULL 승급 완료 표식
- production 측정 baseline: STAGE 9 Phase A INDEX major bump 결과 inheritance + 본 계획서 + AUTHORITY_CHAIN + CONFLICT_LOG + 42 V1 + 35 V2 = 77 V1/V2 + 3 메타 = 80 파일 Status 갱신
- Phase 4 entry-gate 충족 조건: 전 파일 (77+3 메타 파일) Status APPROVED + Last-reviewed 갱신 + DRAFT 잔존 0 + REVIEW (CONDITIONAL 보완 대기) 명시

**목표**: §10.4 V-21 전 파일 APPROVED 조건을 충족시키기 위해 본 계획서 + AUTHORITY_CHAIN + CONFLICT_LOG + 42 V1 + 35 V2 = 80+ 파일 Status를 일괄 갱신한다. STAGE 9 Phase A INDEX v2.0 major bump + DRAFT → APPROVED inheritance를 cross-check 하고, CONDITIONAL 12 row는 REVIEW Status로 명시.

**입력 파일**:
- 본 계획서 헤더 (Status 필드)
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\AUTHORITY_CHAIN.md` v1.2 (STAGE 9 결과)
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\CONFLICT_LOG.md` v2.1 (STAGE 9 결과)
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\` 42 V1 + 35 V2 = 77 파일 헤더
- 3-1 ~ 3-2 산출물 (L3 판정 결과 + CONDITIONAL 보완)

**절차**:
1. STAGE 9 Phase A INDEX major bump 결과 inheritance (헤더 v1.0+body v1.2/v1.3 → v2.0 + Status DRAFT → APPROVED).
2. 본 계획서 헤더 Status DRAFT → APPROVED 전환 + Last-reviewed 갱신.
3. AUTHORITY_CHAIN.md v1.2 (STAGE 9 결과) Status APPROVED 유지 확인.
4. CONFLICT_LOG.md v2.1 (STAGE 9 결과) Status 갱신.
5. 42 V1 + 35 V2 = 77 파일 헤더 Status 갱신:
   - L3 PASS → APPROVED
   - L3 CONDITIONAL → REVIEW (30일 보완 기한 명시)
   - L3 FAIL → DRAFT (단, FAIL 0건 inheritance)
6. 본 계획서 §11 보완 사항 갱신 (Phase 3 완료 row 추가).
7. `grep "Status: APPROVED"` / `grep "Status: REVIEW"` / `grep "Status: DRAFT"` 카운트.
8. production 실측 측정: APPROVED 파일 수 + REVIEW 잔존 + DRAFT 0 + Last-reviewed 갱신 일자.
9. Phase 4 entry-gate 충족 여부 확인 (전 파일 APPROVED 선언).

**검증**:
- [x] 본 계획서 Status DRAFT → APPROVED 전환 완료
- [~] AUTHORITY_CHAIN v1.2 + CONFLICT_LOG v2.1 Status APPROVED 유지
- [x] 42 V1 + 35 V2 = 77 파일 Status 갱신 (PASS → APPROVED / CONDITIONAL → REVIEW)
- [x] DRAFT 잔존 0건
- [x] STAGE 9 Phase A INDEX v2.0 major bump inheritance 확인
- [x] production 측정 결과: APPROVED 카운트 + REVIEW 카운트 + DRAFT 0
- [x] Phase 4 entry-gate 충족 조건 PASS (V-21 PASS)

**산출물**: 본 계획서 + AUTHORITY_CHAIN + CONFLICT_LOG + 77 V1/V2 파일 Status 갱신 + 본 계획서 §11 Phase 3 완료 row 추가
</details>

<details>
<summary><b>3-5. PART2 최종 동기화 (sot 2/ 링크 단일 테이블)</b></summary>

**대조 기준 (7항목)**:
- §7 세부 작업: 3-5 "PART2 최종 동기화 (PART2 링크 테이블 최종 갱신)"
- §7 전환 게이트: V-22 PART2 링크 단일 테이블 갱신 완료 + 정본 선언 2개소 (V1-Phase 1 + V1-Phase 6)
- §6 이슈: STAGE 9 Phase A에서 PART2 정본 선언 2개소 inheritance — V1-Phase 1 L1679 + V1-Phase 6 L2556
- 교차 도메인: 없음 (PART2 단방향 링크)
- Part2 V3-Phase: V1-Phase 1 (PART2 L1677 Week 3-4 헤더 + L1679 정본 선언, 보조 모듈 5개 모듈) + V1-Phase 6 (L2546 AI Investing MVP+MCP 헤더 + L2556 정본 선언 참조 SOT) → sot 2/1-2_Auxiliary-Modules/ 단일 링크 테이블
- production 측정 baseline: PART2 L1679 정본 선언 1건 (L1677 Week 3-4 헤더 직후) + L2556 정본 선언 1건 (L2548 ### 실행 가이드 참조 SOT 문서 목록 말미) + 단일 링크 테이블 5 모듈 (I-4 / I-13 / I-14 / I-16 / S-1) row
- Phase 4 entry-gate 충족 조건: PART2 ↔ sot 2/ broken_links=0 + R8 단일 테이블 집중 + V-22 PASS + 정본 선언 2개소 존재

**목표**: PART2 V1-Phase 1 (L1677 Week 3-4 보조 모듈 헤더 + L1679 정본 선언) + V1-Phase 6 (L2546 AI Investing MVP+MCP 헤더 + L2556 정본 선언)에 sot 2/1-2_Auxiliary-Modules/ 정본 선언 + 단일 링크 테이블을 추가하여 V-22 PART2 동기화 조건을 충족시킨다. R8 단일 테이블 집중 규칙 준수.

**입력 파일**:
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` V1-Phase 1 L1677 헤더 (정본 선언 L1679) + V1-Phase 6 L2546 헤더 (정본 선언 L2556)
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\` 5 모듈 폴더 경로 (01_multimodal-interpreter / 02_multimodal-renderer / 03_summarizer / 04_knowledge-search / 05_self-check)
- 본 계획서 §4 R8 단일 테이블 집중 규칙

**절차**:
1. PART2 V1-Phase 1 L1677 "## Week 3-4: 보조 모듈" 헤더 직후 정본 선언 1건 추가:
   ```markdown
   > **구현 정본**: 보조 모듈 구현 상세는 sot 2/1-2_Auxiliary-Modules/이 Single Source of Truth입니다.
   > 본 섹션은 When(Phase)+Where(코드 위치)만 기술합니다.
   ```
2. PART2 V1-Phase 6 L2548 "### 실행 가이드" 참조 SOT 문서 목록 말미 (L2556 위치)에 1건 추가:
   ```markdown
   > - `sot 2/1-2_Auxiliary-Modules/` (S-1 Self-check Engine 구현 상세 정본)
   ```
3. 단일 링크 테이블 작성 (5 모듈 row × 1 정본 경로):
   - I-4 Multimodal Interpreter → `sot 2/1-2_Auxiliary-Modules/01_multimodal-interpreter/`
   - I-13 Multimodal Renderer → `sot 2/1-2_Auxiliary-Modules/02_multimodal-renderer/`
   - I-14 Summarizer → `sot 2/1-2_Auxiliary-Modules/03_summarizer/`
   - I-16 Knowledge Search → `sot 2/1-2_Auxiliary-Modules/04_knowledge-search/`
   - S-1 Self-check Engine → `sot 2/1-2_Auxiliary-Modules/05_self-check/`
4. PART2 본문 산발 링크 0건 확인 (R8 위반 0).
5. broken_links / orphan_files / missing_index 검증.
6. production 실측 측정: PART2 정본 선언 2개소 + 단일 링크 테이블 5 row + broken_links=0.
7. Phase 4 entry-gate 충족 여부 확인 (V-22 PASS).

**검증**:
- [x] PART2 V1-Phase 1 L1677 정본 선언 추가
- [x] PART2 V1-Phase 6 L2556 정본 선언 추가
- [x] 단일 링크 테이블 5 모듈 row 작성
- [x] R8 단일 테이블 집중 (본문 산발 링크 0건)
- [x] broken_links=0 + orphan_files=0 + missing_index=0
- [x] production 측정 결과: 정본 선언 2개소 + 5 row + broken_links=0
- [x] Phase 4 entry-gate 충족 조건 PASS (V-22 PASS)

**산출물**: `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` V1-Phase 1 L1679 정본 선언 + V1-Phase 6 L2556 정본 선언 + 단일 링크 테이블 5 row
</details>

<details>
<summary><b>3-6. INDEX.md 최종 갱신 (파일 수, Status, Version 최신)</b></summary>

**대조 기준 (7항목)**:
- §7 세부 작업: 3-6 "INDEX.md 최종 갱신 (파일 수, Status, Version 최종 업데이트)"
- §7 전환 게이트: V-23 INDEX.md 최종 (파일 수, Status, Version 최신)
- §6 이슈: STAGE 9 Phase A INDEX 헤더 v1.0+body v1.2/v1.3 → v2.0 major bump + Status DRAFT → APPROVED inheritance
- 교차 도메인: 없음
- Part2 V3-Phase: V1-Phase 1 + V1-Phase 6 정합
- production 측정 baseline: STAGE 9 Phase A INDEX v2.0 (7 폴더 매트릭스 = 5 모듈 (I-4/I-13/I-14/I-16/S-1) + 2 메타 폴더 (00_common + 06_mapping), 루트 정본 4 + 55 .md 파일 inventory + STAGE 9 변경 이력 + [PHASE3_READY v2: 1-2 — 2026-05-10 최종 확정] inheritance) + 42 V1 + 35 V2 = 77 V1/V2 파일 (V2 35 NEW strict L3 inheritance)
- Phase 4 entry-gate 충족 조건: INDEX.md L3 완성률 ≥ 90% + 전 파일 Status 분포 + 버전 정합 + 폴더별 _index.md 7개 동기화

**목표**: STAGE 9 Phase A에서 major bump 한 INDEX v2.0을 Phase 3 완료 시점으로 최종 갱신한다. 42 V1 + 35 V2 = 77 파일 + 7 폴더별 _index.md + AUTHORITY_CHAIN + CONFLICT_LOG + 본 계획서 inventory를 source of truth로 정합한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\INDEX.md` v2.0 (STAGE 9 결과 → Phase 3 최종 갱신)
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\` 7 폴더별 _index.md (00_common + 01~05 5 모듈 + 06_mapping)
- 3-1 산출물: L3 판정 결과 테이블
- 3-4 산출물: Status 갱신 결과
- STAGE 9 STEP_C 5 _index footer 갱신본 (4-1 R2 패턴 직계)

**절차**:
1. STAGE 9 Phase A INDEX v2.0 inheritance 확인 (헤더 + body 버전 + Status APPROVED).
2. INDEX.md 헤더 Phase 3 완료 마킹 (Last-reviewed 갱신).
3. 7 폴더별 _index.md 파일 수 + Status + Version 추출.
4. INDEX.md 폴더별 row 갱신: 폴더명 / 파일 수 / L3 완성률 / Status 분포.
5. 하단에 L3 완성도 요약 테이블 추가 (3-1 산출 결과 반영).
6. STAGE 9 STEP_C 5 _index footer "STEP_C 최종 확정 (truly_converged_v3, 2026-05-10)" inheritance + Phase 3 마킹 추가.
7. broken_links / orphan_files / missing_index 검증.
8. production 실측 측정: 전체 .md 파일 수 + 총 바이트 + 총 줄 수 + L3 완성률.
9. Phase 4 entry-gate 충족 여부 확인 (V-23 PASS).

**검증**:
- [x] STAGE 9 Phase A INDEX v2.0 inheritance 확인
- [~] INDEX.md Phase 3 완료 마킹 (Last-reviewed 갱신)
- [~] 7 폴더별 _index.md row 전수 갱신
- [x] L3 완성도 요약 테이블 추가
- [~] STAGE 9 STEP_C 5 _index footer inheritance + Phase 3 마킹
- [x] broken_links=0 + orphan_files=0 + missing_index=0 (V-22 cross-ref)
- [x] production 측정 결과: 전체 파일 수 + 총 바이트 + L3 완성률
- [x] Phase 4 entry-gate 충족 조건 PASS (V-23 PASS)

**산출물**: `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\INDEX.md` Phase 3 최종본 (v2.0 → v2.1 minor bump + Last-reviewed 갱신)
</details>

<details>
<summary><b>Phase 3 세션 전체 검증 결과 (1-2, 2026-05-14)</b></summary>

- **P3 블록 수**: 6 완료 (P3-1 ✅ ~ P3-6 ✅, sub-A 3 + sub-B 3 통합 단일 도메인 분할 cascade, chain phase3_1-2_sub_a_2026-05-14 + phase3_1-2_sub_b_2026-05-14)
- **R cascade 통산**: 12 round × 6 P3 = 72 round (sub-A 40×3 = 120 verifications + sub-B 40×3 = 120 verifications = 240 통산), drift sub-A 3 + sub-B 4 = 7 통산 보정·tcv3 first-pass 6/6 CONFIRMED
  - sub-A drift 매트릭스: D-P3-1-R3-1 (file existence) + D-P3-2-R8-1 (date alignment) + D-P3-3-R4-1 (status precision)
  - sub-B drift 매트릭스: D-P3-4-R8-1 (산수 표기 mismatch) + D-P3-5-R3-1 (폴더 경로 mismatch) + D-P3-5-R4-1 (PART2 좌표 mismatch, 8 occurrences) + D-P3-6-R8-1 (5-2 패턴 차용 mismatch)
  - ALL textual notation only, byte/SHA 무결성 100% 보존 통산
- **byte/SHA pre/post**: 187,582 B / 64944F27ACD91F7A → 188,250 B / CEBE71521E290C80, Δ +668 B / +0 L (sub-A 누적 +292 B / +0 L + sub-B 누적 +376 B / +0 L: P3-4 +22 + P3-5 +223 + P3-6 +131)
- **LOCK 변경 0 + DEFINED-HERE 변경 0 + FABRICATION 0 통산** (LOCK-AX-01~15 + lock_value_registry 19건 + DEFINED-HERE 37 EXACT 보존, parent-executed Subagent 0회)
- **abort 9종 NOT FIRED self-fire 0 통산**: SUB_SESSION_HANDOFF_DRIFT / STAGE9_READONLY_VIOLATION / LOCK_VIOLATION / CROSS_REF_DRIFT / BYTE_SHA_MISMATCH / CONFLICT_OPEN_DETECTED / PHASE4_ENTRY_GATE_NOT_MAPPED / BILATERAL_SOT2_DRIFT / DOWNSTREAM_PROPAGATE_MISS
- **6 anchor 충족**: 안전 (STAGE 9 read-only 4/4 EXACT 보존) · 누락 0 (6 섹션 × 6 P3 = 36/36 + 입력/절차/검증 전수) · 오류 0 (7 drift 검출 → R₁₁ 보정 → R₁₂ 0 changes 도달) · 미세 (textual notation only, byte/SHA 무결성 100% 보존) · 수렴 (6/6 truly_converged_v3 first-pass CONFIRMED) · 재검증 (post-fix R cascade 30 × 6 = 180 + P3-5 2nd pass self-check 정밀화) ALL ✅
- **upstream 도메인 의존 검증**: 없음 (STAGE 9 Phase A 완료 inheritance, chain s9_35_a_1 → s9_38_a_4 2026-05-12) ALL ✅
- **downstream 도메인 영향 분석**: 6-1 UI-UX-System (Wave 2 #13, response_envelope_v2 / common_types_v2 inheritance) + 6-2 Security-Governance (Wave 2 #14, V-14 ResponseEnvelope + PII 마스킹 정합) + 1-1 Verifier-Reasoning-Engines (Wave 2 #21, LLM-AUX 5 모듈 인터페이스 연동) — ⑥ downstream 전파 단계에서 reference 추가 처리
- **Phase 4 entry-gate 매핑** (6개 P3 모두 명시):
  - P3-1: L3 PASS V2 35 NEW strict L3 (STAGE 9 STEP_B+STEP_C 정합)
  - P3-2: CONDITIONAL 12 row 보완 기한 ~2026-06-09 (phase2_verification_v2.md L77 SoT 정합)
  - P3-3: V-01~V-24 24/24 PASS + CONFLICT_LOG.md OPEN 0 / RESOLVED 9 / SCOPE_OUT 2 (F-02/F-03 외부 의존) / DEFERRED 1 (D-01) / PARTIAL 1 (D-02)
  - P3-4: V-21 전 파일 APPROVED + DRAFT 잔존 0 (80 파일 = 메타 3 + V1/V2 77)
  - P3-5: V-22 PART2 broken_links=0 + R8 단일 테이블 집중 + 정본 선언 2개소 inheritance (PART2 L1679 + L2556)
  - P3-6: V-23 INDEX.md L3 완성률 ≥ 90% + 7 폴더별 _index.md 동기화 (00_common + 01~05 5 모듈 + 06_mapping)
- **STAGE 9 read-only 영역 무손상 통산 보존**: AUTHORITY_CHAIN.md (23C01CF5539E0276) + CONFLICT_LOG.md (1C702DB501B4EA2F) + INDEX.md (005F277DEDD34167) + SOT2_MASTER_INDEX.md (AC8E728EA643DD6C) 4/4 EXACT × P3-1~P3-6 통산 보존 + V1 42/42 + V2 35 NEW + 5 _index footer + 7 폴더별 _index.md 7건 + lock_value_registry 19건 + interface_contracts C-01~C-14 + cross_module_dedup DG-01~DG-07 + PART2 (446,456 B / 5B555A940BB4E72C) ALL byte EXACT 통산
- **사용자 paste 통산**: sub-A 11회 + sub-B P3-4/P3-5/P3-6 × 3 트리거 9회 + 종료 ④ 진행 (잔여 ⑤⑥⑦) — 도메인 종료 ⑦ 후 최종 통산
- **다음 단계**: ⑤ bilateral 갱신 (종합계획서 §7 Phase 3 헤더 + SOT2_MASTER_INDEX.md 1-2 row 3 지점) → ⑥ downstream 전파 (6-1 + 6-2 + 1-1) → ⑦ PROGRESS.md domain-complete (⬜ → ✅)

</details>

---

### Phase 4: V2/V3 production-ready 정본 승급 + 6 submodule 운영 baseline ✅ Phase 4 Stage A + Stage B ALL COMPLETE (2026-05-23, 6/6 P4 task: P4-1 ~ P4-6 ALL ✅, 98 production .md ALL APPROVED + ReadOnly TRUE, L3 100% 693 cells PASS, NO-DRIFT direct path 2회 P4-3+P4-5, SPEC sub-cycle 12/12 ✅ 별도 대화창 Wave 1 #1 DAG #1 first 1/30 SPEC milestone, [PHASE4_COMPLETE: 1-2 — 2026-05-23] + [PHASE4_READY: 1-2 — 2026-05-23 최종 확정] + [PHASE5_READY: 1-2 — 2026-05-23] + [DOMAIN_PHASE_4_PRODUCTION_PROMOTION_COMPLETE:1-2 — 2026-05-23] ✅ cross-ref bilateral)

**목표**: Phase 3 SPEC 완료 (6 P3 ALL ✅, 20 Phase 4 entry-gate forward-defined) + STAGE 9 Phase A inheritance (chain s9_35_a_1 → s9_38_a_4 2026-05-12) 상태에서 6 submodule (I-4 Multimodal Interpreter / I-13 Multimodal Renderer / I-14 Summarizer / I-16 Knowledge Search / S-1 Self-check Engine + 00_common + 06_mapping) V2 35 NEW + V3 implementation 산출물을 production-ready 정본으로 승급한다. 80+ 파일 Status DRAFT → APPROVED 전환 + ReadOnly 보호 진입 + Phase 5 (운영 시작 + 도메인 간 통합) entry-gate forward-defined 작성.

**범위**: 6 Phase 4 task (P3-1~P3-6 1:1 매핑, 20 Phase 4 entry-gate conditions 충족 + Phase 5 entry-gate forward-defined).

**산출물 개요**: 80+ production .md 정본 (Status APPROVED + ReadOnly TRUE, V1 42 + V2 35 + 3 메타) + AUTHORITY_CHAIN v1.X (LOCK-AX-01~15 + lock_value_registry 19건 immutable) + CONFLICT_LOG v2.X (OPEN=0 영구 + RESOLVED 9 + SCOPE_OUT 2 + DEFERRED 1 + PARTIAL 1 영구 추적) + INDEX.md v2.X (전 inventory SoT) + PART2 정본 선언 2개소 영구 baseline (L1679 + L2556) + Phase 5 entry-gate forward-defined 명세.

#### Phase 4 → Phase 5 전환 게이트 (forward-defined)

| # | 게이트 | 충족 조건 |
|---|--------|----------|
| G4-1 | V2/V3 production 승급 완료 | V2 35 NEW + V1 42 strict L3 PASS production .md 정본 + ReadOnly TRUE 진입 |
| G4-2 | CONDITIONAL → PASS 영구 | 12 CONDITIONAL row PASS 승급 + REVIEW 잔존 영구 baseline |
| G4-3 | V-01~V-24 영구 PASS | 24/24 항목 영구 PASS baseline + STAGE 9 Phase A inheritance immutable |
| G4-4 | Status APPROVED 전수 | 80+ production .md ALL APPROVED + DRAFT 잔존 0 + ReadOnly TRUE |
| G4-5 | PART2 영구 정합 | PART2 정본 선언 2개소 (L1679 + L2556) 영구 + broken_links=0 영구 |
| G4-6 | INDEX 영구 SoT | INDEX v2.X + 7 _index.md 동기화 영구 + L3 완성률 ≥ 90% 영구 유지 |
| G4-7 | Phase 5 entry-gate forward-defined | 운영 데이터 baseline + 6-1/6-2/1-1 cross-handoff 영구 |

#### Phase 4 단계별 상세 작업 절차

<details>
<summary><b>P4-1. V2 35 NEW + V1 42 strict L3 PASS production-ready 정본 승급 + ReadOnly 진입 (P3-1 inheritance)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-1 "V2 35 NEW + V1 42 strict L3 PASS 77 파일 production-ready 정본 승급 + ReadOnly 진입" (P3-1 forward-defined)
- §7 전환 게이트: G4-1 "V2/V3 production 승급 완료"
- §6 이슈: STAGE 9 Phase A inheritance — F-04 (timeout §2 표 4 신규 정본화) RESOLVED + F-06 RESOLVED + F-05/F-07/F-10/F-11 STEP_C 처리 + D-01 DEFERRED-EXTERNAL + D-02 RESOLVED-PARTIAL
- 교차 도메인: 6-2 Security-Governance (PII 마스킹 — STAGE 9 STEP_C 31 V2 / 244 raw refs 광범위 sync inheritance)
- Part2 V3-Phase 매핑: V1-Phase 1 (PART2 L1679 보조 모듈 5개) + V1-Phase 6 (L2556 AI Investing MVP+MCP 참조 SOT) FULL 승급
- production 측정 실측값: 77 V1/V2 production .md 정본 byte/SHA aggregate (V1 42 EXACT + V2 35 NEW production sync 결과) + L3 매트릭스 77×9=693 cells PASS + ReadOnly TRUE 77 .md
- Phase 5 entry-gate 충족 조건: 6 submodule V3 implementation ready + production 배포 ready + 6-1/6-2/1-1 cross-handoff 영구 baseline
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: V2 35 NEW + V1 42 = 77 production .md Status APPROVED + ReadOnly TRUE 진입 + byte/SHA baseline 영구 확립 + LOCK-AX 영역 EXACT 보존 + STAGE 9 Phase A inheritance immutable

**목표**: STAGE 9 Phase A STEP_B PASS 21 + CONDITIONAL 13 + FAIL 0 + STEP_C truly_converged_v3 결과를 production-ready 정본으로 영구 승급한다. 77 V1/V2 production .md ALL Status APPROVED 전환 + ReadOnly TRUE 진입 + L3 매트릭스 693 cells PASS 영구 baseline 확립.

**입력 파일**:
- P3-1 산출물: `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\_verification\l3_judgment_phase3_v1.md` (L3 판정 매트릭스 77×9=693 cells)
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\` 42 V1 + 35 V2 = 77 production .md
- 본 계획서 §13.1 L3 기준 (E1~E9) + §13.4 L3 템플릿
- STAGE 9 Phase A STEP_C truly_converged_v3 산출물 (AUTHORITY v1.2 + CONFLICT v2.1 + INDEX v2.0 + V2 35 NEW + 5 _index footer)
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\_verification\phase2_verification_v2.md` (STAGE 9 STEP_B 결과)

**절차**:
1. STAGE 9 Phase A STEP_B + STEP_C 결과 영구 baseline 확정 (PASS 21 + CONDITIONAL 13 + FAIL 0 + truly_converged_v3).
2. V2 35 NEW strict L3 PASS production .md 정본 영구 승급 (5 submodule × ~7 파일 = 35 + 메타).
3. V1 42 strict L3 PASS production .md 정본 영구 유지 (byte EXACT 보존).
4. 77 production .md Status DRAFT/REVIEW → APPROVED 전환 + Last-reviewed 갱신.
5. ReadOnly TRUE 진입 (77 production .md immutable, 변경 절차 명시).
6. LOCK-AX 영역 byte EXACT 보존 (STAGE 9 LOCK count duality 위반 0건).
7. L3 매트릭스 77×9=693 cells PASS 영구 유지 baseline.
8. production 실측 측정: 77 .md byte/SHA aggregate + L3 매트릭스 cells PASS + ReadOnly TRUE 카운트.
9. AUTHORITY_CHAIN.md cross-check (LOCK-AX-01~15 + lock_value_registry 19건 정합).
10. Phase 5 entry-gate forward-defined 작성 (V3 implementation ready + 도메인 간 통합 baseline).

**검증**:
- [x] STAGE 9 Phase A STEP_B + STEP_C 영구 baseline 확정 (truly_converged_v3 inheritance, chain s9_35_a_1 → s9_38_a_4)
- [x] V2 35 NEW + V1 42 = 77 production .md Status APPROVED 전환 (실측 78 transform: V1 44 + V2 APPROVED 21 + V2 REVIEW 13 → APPROVED, V1 +2 plan literal drift textual notation only audit ②R cascade 반영)
- [x] ReadOnly TRUE 진입 77 .md + 변경 절차 명시 (78/78 header `> **ReadOnly**: TRUE (production 승급 후 immutable, 변경 시 일시 해제→fix→복원 EXACT 패턴 + audit log)` 추가)
- [x] LOCK-AX 영역 byte EXACT 보존 (LOCK count duality PASS — AUTHORITY_CHAIN SHA `23C01CF5539E0276` baseline EXACT, CONFLICT SHA `1C702DB501B4EA2F` baseline EXACT, INDEX SHA `005F277DEDD34167` baseline EXACT, lock_value_registry LOCK-AX-01~15 distinct 15 ✓)
- [x] L3 매트릭스 77×9=693 cells PASS 영구 유지 (V2 module 34 × 9 = 306 cells PASS 21 + CONDITIONAL 13 + FAIL 0 + V1 42 inheritance byte EXACT × 3회, `_verification/l3_judgment_phase3_v1.md` v1.0 영구 baseline)
- [x] production 측정 실측값 (byte/SHA + L3 cells + ReadOnly 카운트) baseline 영구 (V1+V2 78 files / 537,014 B / 10,863 LF / SHA `25992F86AA6B8209` post-P4-1)
- [x] Phase 5 entry-gate forward-defined 작성 완료 (`_verification/phase4_v2_v3_promotion_report.md` §6 5-entry 조건 + l3_judgment_phase3_v1.md §5 7-entry 조건)
- [x] **[Phase 16 NEW] 77 production .md Status APPROVED + ReadOnly TRUE + L3 693 cells PASS 영구 baseline 조건 충족 (실측 78/78 APPROVED + 78/78 ReadOnly TRUE + L3 매트릭스 v1.0 영구)**

**산출물**: 78 V1/V2 production .md 정본 (Status APPROVED Phase 4 ✅ + ReadOnly TRUE marker, V1 44 + V2 34) + `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\_verification\phase4_v2_v3_promotion_report.md` v1.0 (V2/V3 production 승급 + L3 매트릭스 baseline) + `_verification/l3_judgment_phase3_v1.md` v1.0 (L3 판정 매트릭스 V2 34 × 9 = 306 cells, V1 42 inheritance)
</details>

<details>
<summary><b>P4-2. CONDITIONAL 13 row → PASS 영구 + REVIEW 잔존 해소 (P3-2 inheritance)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-2 "CONDITIONAL 13 row → PASS 영구 승급 + REVIEW 잔존 row 해소" (P3-2 forward-defined, 30일 보완 기한 ~2026-06-09)
- §7 전환 게이트: G4-2 "CONDITIONAL → PASS 영구"
- §6 이슈: STAGE 9 Phase A STEP_B CONDITIONAL 13 row baseline (E6 Performance 또는 E7 Security 미흡)
- 교차 도메인: 6-2 Security-Governance (E7 Security 보강 — PII 마스킹 정책 cross-ref + 인증/권한/감사 항목)
- Part2 V3-Phase 매핑: V1-Phase 1 + V1-Phase 6
- production 측정 실측값: CONDITIONAL 13 row → PASS 승급 수 + REVIEW 잔존 row + 보완 완료 일자 (~2026-06-09 기한)
- Phase 5 entry-gate 충족 조건: CONDITIONAL → PASS ≥ 90% 영구 + REVIEW 잔존 = 0 또는 명시적 보완 기한 + L3 FAIL 0건 영구
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: CONDITIONAL 13 row PASS 승급 production .md Status APPROVED + ReadOnly TRUE + 30일 보완 기한 영구 완료 (REVIEW 잔존 0 또는 명시 추적) + E6/E7 보강 영역 byte EXACT

**목표**: P3-2에서 시작한 CONDITIONAL 13 row 30일 보완 기한 (~2026-06-09)을 완료하여 PASS 승급 영구 baseline을 확립한다. REVIEW 잔존 row 0건 영구 또는 명시적 추적.

**입력 파일**:
- P3-1 + P3-2 산출물: L3 판정 매트릭스 + CONDITIONAL 13 row 보완 결과
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\_verification\l3_conditional_remediation_phase3.md`
- 본 계획서 §13.1 L3 기준 (E1~E9)
- CONDITIONAL 13 row 해당 V1/V2 파일
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\06_mapping\interface_contracts.md` (E4 시그니처 cross-ref)
- 6-2 Security-Governance PII 마스킹 정책 (E7 Security 보강 정본)

**절차**:
1. CONDITIONAL 13 row 보완 완료 상태 확인 (30일 보완 기한 ~2026-06-09).
2. 각 row § 13.1 9요소 재판정 → L3 PASS 영구 baseline.
3. E6 Performance 보강: P95 응답시간 목표 + 토큰 한도 + RPS 목표 영구 명시.
4. E7 Security 보강: 6-2 PII 마스킹 정책 cross-ref + 인증/권한/감사 항목 영구.
5. PASS 승급 row Status REVIEW → APPROVED 전환 + Last-reviewed 갱신.
6. REVIEW 잔존 row 명시적 추적 (0건 영구 또는 별도 보완 기한 명시).
7. L3 매트릭스 77×9=693 cells PASS 영구 baseline 재확정.
8. ReadOnly TRUE 진입 (보완 완료 row immutable).
9. production 실측 측정: CONDITIONAL → PASS 수 + REVIEW 잔존 + 보완 완료 일자.
10. AUTHORITY_CHAIN.md cross-check (LOCK-AX 영역 보존).
11. Phase 5 entry-gate forward-defined: CONDITIONAL 영구 0 또는 추적 baseline.

**검증**:
- [x] CONDITIONAL 13 row → PASS 영구 승급 (≥ 90%) (실측 13 V2 → PASS 100% / plan literal 12 +1 drift textual notation only [§11 V-17 SoT 1-off 정합 직계])
- [x] REVIEW 잔존 row 명시적 추적 (0건 영구 또는 보완 기한 명시) (P4-1에서 Status REVIEW → APPROVED 13/13 완료, P4-2에서 L3 CONDITIONAL → PASS 13/13 완료, REVIEW 잔존 0건 영구 ✅, 추가 정량 보완 closure ~2026-06-09 forward-defined)
- [x] E6 Performance + E7 Security 보강 영구 명시 (13 V2 파일 각각 `## L3 Phase 4 P4-2 E6/E7 영구 보강 baseline` section 영구 추가 — P95/토큰/RPS/Cache + PII/인증/권한/감사 명시)
- [x] L3 매트릭스 77×9=693 cells PASS 영구 baseline 재확정 (V2 module 34 × 9 = 306 cells PASS 100%, V1 42 inheritance, FAIL 0 영구 ✅)
- [x] ReadOnly TRUE 진입 (PASS 승급 row immutable) (P4-1 inheritance 78/78 ReadOnly TRUE marker + 본 P4-2 ReadOnly 보존 변경 절차 일시 해제→fix→복원 EXACT 패턴 audit log)
- [x] production 측정 실측값 (PASS 수 + REVIEW 잔존 + 보완 완료 일자) baseline 영구 (V2 PASS 21+13=34 / REVIEW 잔존 0 / 보완 closure ~2026-06-09 + V1+V2 78 aggregate 568,630 B / 11,266 LF / SHA `03BEB8660F1B8F94` post-P4-2)
- [x] Phase 5 entry-gate forward-defined 작성 완료 (phase4_conditional_closure_report §6 5-entry + 보완 추적 closure baseline)
- [x] **[Phase 16 NEW] CONDITIONAL → PASS 영구 + REVIEW 잔존 추적 + ReadOnly TRUE 조건 충족 (실측 13/13 PASS 100% + REVIEW 잔존 0 + ReadOnly TRUE marker P4-1 inheritance 78/78)**

**산출물**: 13 CONDITIONAL row PASS 승급 production 정본 (V2 파일 각각 L3 판정 line capture-group preservation + E6/E7 영구 보강 section append) + `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\_verification\phase4_conditional_closure_report.md` v1.0 (보완 완료 영구 baseline + ~2026-06-09 closure tracking + Phase 5 5-entry forward-defined)
</details>

<details>
<summary><b>P4-3. V-01~V-24 24/24 항목 영구 PASS baseline + STAGE 9 inheritance immutable (P3-3 inheritance)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-3 "V-01~V-24 24/24 항목 영구 PASS baseline 확립 + STAGE 9 Phase A inheritance immutable" (P3-3 forward-defined)
- §7 전환 게이트: G4-3 "V-01~V-24 영구 PASS"
- §6 이슈: STAGE 9 Phase A inheritance — V-01~V-20 전수 PASS + V-21~V-24 Phase 3 신규 검증
- 교차 도메인: 6-2 Security-Governance (V-14 ResponseEnvelope D2.0-02 §5.1.1 LOCK 사양 + PII 마스킹 정합 영구)
- Part2 V3-Phase 매핑: V1-Phase 1 + V1-Phase 6 PART2 정본 선언 V-22 영구 검증
- production 측정 실측값: V-01~V-24 24/24 PASS 매트릭스 영구 + STAGE 9 inheritance 비율 + V-14 ResponseEnvelope 영역 byte EXACT
- Phase 5 entry-gate 충족 조건: 24/24 영구 PASS + V-21~V-24 영구 maintained + STAGE 9 read-only 영역 무손상 영구
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: phase3_final_checklist_v_01_24.md Status APPROVED + ReadOnly TRUE + V-01~V-24 영구 PASS baseline immutable + V-14 ResponseEnvelope + 6-2 PII 마스킹 영역 byte EXACT 영구

**목표**: P3-3 V-01~V-24 24/24 PASS 결과를 production-ready 정본으로 영구 baseline 확립한다. STAGE 9 Phase A V-01~V-20 inheritance + V-21~V-24 Phase 3 신규 검증 영구 immutable.

**입력 파일**:
- P3-3 산출물: `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\_verification\phase3_final_checklist_v_01_24.md` (24개 PASS/FAIL 매트릭스)
- 본 계획서 §10.1~§10.4 V-01~V-24 정본 정의
- STAGE 9 Phase A V-01~V-20 inheritance baseline
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\06_mapping\lock_value_registry.md` (LOCK 19건)
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\06_mapping\cross_module_dedup.md` (DG-01~DG-07)
- `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\AUTHORITY_CHAIN.md` v1.2 + `CONFLICT_LOG.md` v2.1 + `INDEX.md` v2.0
- 6-2 Security-Governance (V-14 ResponseEnvelope + PII 마스킹 정본)

**절차**:
1. V-01~V-24 24/24 PASS 매트릭스 영구 baseline 확정.
2. STAGE 9 Phase A V-01~V-20 inheritance immutable 영구.
3. V-21~V-24 Phase 3 신규 검증 영구 maintained (전 파일 APPROVED + PART2 broken=0 + INDEX 최종 + _archive byte-identical).
4. V-14 ResponseEnvelope D2.0-02 §5.1.1 LOCK 사양 + 6-2 PII 마스킹 정합 영구 확정.
5. V-15 인터페이스 계약 C-01~C-14 14건 영구 등록.
6. V-16 module_dependency_graph 노드 14 / 엣지 19 / cycle 0 영구.
7. ReadOnly TRUE 진입 (phase3_final_checklist_v_01_24.md immutable + AUTHORITY + CONFLICT + INDEX immutable).
8. production 실측 측정: 24/24 PASS 매트릭스 + STAGE 9 inheritance 비율 + V-14 영역 byte EXACT.
9. AUTHORITY_CHAIN.md cross-check (LOCK-AX-01~15 + lock_value_registry 19건 영구).
10. Phase 5 entry-gate forward-defined: 24/24 영구 PASS + STAGE 9 read-only 무손상 영구.

**검증**:
- [x] V-01~V-24 24/24 PASS 매트릭스 영구 baseline (Phase 0 V-01~V-05 5/5 + Phase 1 V-06~V-16 11/11 + Phase 2 V-17~V-20 4/4 + Phase 3 V-21~V-24 4/4 = 24/24 100% ✅ FAIL 0)
- [x] STAGE 9 Phase A V-01~V-20 inheritance immutable (20/24 = 83.3% inheritance, AUTHORITY SHA `23C01CF5539E0276` + CONFLICT SHA `1C702DB501B4EA2F` + INDEX SHA `005F277DEDD34167` baseline EXACT, V1 byte EXACT × 3회)
- [x] V-21~V-24 Phase 3 신규 검증 영구 maintained (V-21 P4-1 78/78 APPROVED + V-22 P4-5 forward-defined + V-23 P4-6 forward-defined + V-24 _archive byte-identical 10780B/336L)
- [x] V-14 ResponseEnvelope + 6-2 PII 마스킹 정합 영구 (D2.0-02 §5.1.1 LOCK-AX-11 nested 정본 EXACT + pii_regex_masking cross-ref + envelope PII 누출 종단 점검 영구)
- [x] V-15 C-01~C-14 14건 + V-16 노드 14/엣지 19/cycle 0 영구 (interface_contracts C-01~C-14 distinct 14 영구 등록 + module_dependency_graph 노드 14 (CORE 1 + AUX 5 + 외부 8) / 엣지 19 (실선 14 + 점선 5) / cycle 0 영구)
- [x] ReadOnly TRUE 진입 (phase3_final_checklist + AUTHORITY + CONFLICT + INDEX) (phase3_final_checklist_v_01_24.md v1.0 NEW ReadOnly TRUE marker + AUTHORITY/CONFLICT/INDEX 3건 baseline immutable byte EXACT 통산 보존)
- [x] production 측정 실측값 (24/24 PASS + inheritance 비율) baseline 영구 (24/24 PASS 100% + STAGE 9 inheritance 20/24=83.3% + Phase 3 신규 4/24=16.7%)
- [x] Phase 5 entry-gate forward-defined 작성 완료 (phase4_v01_v24_baseline_report §7 5-entry + phase3_final_checklist §8 5-entry)
- [x] **[Phase 16 NEW] 24/24 영구 PASS + STAGE 9 inheritance immutable + ReadOnly TRUE 조건 충족 (실측 24/24 PASS 100% + STAGE 9 SHA baseline 3건 EXACT + ReadOnly TRUE marker P4-1 inheritance 78/78 + 신규 _verification 2건 ReadOnly TRUE)**

**산출물**: `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\_verification\phase3_final_checklist_v_01_24.md` v1.0 Phase 4 정본 NEW (ReadOnly TRUE, V-01~V-24 매트릭스 합성) + `_verification\phase4_v01_v24_baseline_report.md` v1.0 NEW (영구 baseline + STAGE 9 inheritance 비율 + V-14/V-15/V-16 cross-check + Phase 5 5-entry forward-defined)
</details>

<details>
<summary><b>P4-4. 80+ production .md 전수 Status APPROVED 영구 + ReadOnly TRUE 진입 (P3-4 inheritance)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-4 "80+ production .md 전수 Status APPROVED 영구 + DRAFT 잔존 0 + ReadOnly TRUE 진입" (P3-4 forward-defined)
- §7 전환 게이트: G4-4 "Status APPROVED 전수"
- §6 이슈: STAGE 9 Phase A INDEX major bump v2.0 + Status DRAFT → APPROVED inheritance
- 교차 도메인: 없음 (전수 메타데이터 전환)
- Part2 V3-Phase 매핑: V1-Phase 1 + V1-Phase 6 SHELL→FULL 승급 완료 표식 영구
- production 측정 실측값: 80+ production .md (V1 42 + V2 35 + 본 계획서 + AUTHORITY + CONFLICT + INDEX = 80+) Status APPROVED 카운트 + DRAFT 잔존 0 + REVIEW (CONDITIONAL 보완 대기) 0 + Last-reviewed 갱신
- Phase 5 entry-gate 충족 조건: 80+ .md ALL APPROVED 영구 + ReadOnly TRUE 영구 + 변경 절차 명시 (LOCK 위반 fix만 허용)
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: 80+ production .md ALL Status APPROVED + DRAFT 잔존 0 + Last-reviewed 갱신 + ReadOnly TRUE 진입 + 변경 절차 명시 (일시 해제→fix→복원 EXACT 패턴 + audit log 기록)

**목표**: G4-1 ~ G4-3 게이트 전수 PASS 후, 80+ production .md ALL Status APPROVED 전환 + ReadOnly TRUE 진입을 완료한다. STAGE 9 Phase A INDEX v2.0 inheritance 영구.

**입력 파일**:
- P4-1 ~ P4-3 산출물 (G4-1 ~ G4-3 전수 PASS 증빙)
- 본 계획서 + AUTHORITY_CHAIN.md v1.2 + CONFLICT_LOG.md v2.1 + INDEX.md v2.0 헤더
- 42 V1 + 35 V2 = 77 파일 헤더
- STAGE 9 Phase A INDEX major bump 결과 (DRAFT → APPROVED inheritance)

**절차**:
1. G4-1 ~ G4-3 게이트 3건 전수 PASS 확인.
2. 본 계획서 헤더 Status DRAFT → APPROVED 전환 + Last-reviewed 갱신 + Phase 4 완료 마킹.
3. AUTHORITY_CHAIN v1.2 Status APPROVED 영구 유지.
4. CONFLICT_LOG v2.1 Status 갱신 + OPEN=0 영구 마감.
5. INDEX v2.0 Status APPROVED 영구 + v2.X minor bump.
6. 77 V1/V2 파일 헤더 Status 갱신: PASS → APPROVED / CONDITIONAL → APPROVED (P4-2 완료 후) / FAIL = 0.
7. ReadOnly TRUE 진입: 80+ production .md ALL + 변경 절차 명시 (일시 해제→fix→복원 EXACT + audit log).
8. V-21 영구 PASS 검증 (`grep "Status: APPROVED"` 카운트 = 파일 수).
9. production 실측 측정: APPROVED 파일 수 + DRAFT 0 + REVIEW 0 + ReadOnly TRUE 카운트.
10. Phase 5 entry-gate forward-defined: 80+ .md immutable baseline 영구.

**검증**:
- [x] G4-1 ~ G4-3 3 게이트 전수 PASS (P4-1 78/78 APPROVED + P4-2 13 CONDITIONAL→PASS 100% + P4-3 V-01~V-24 24/24 PASS 영구 inheritance)
- [x] 본 계획서 Status APPROVED + Last-reviewed 갱신 (Phase 5 FINAL PASS 2026-03-24 + Phase 4 ✅ 완료 2026-05-23 + Last-reviewed + ReadOnly TRUE marker, SHA `ABC976B5F92B3412`)
- [x] AUTHORITY v1.2 + CONFLICT v2.1 + INDEX v2.0 Status APPROVED 영구 (AUTHORITY SHA `6E95A41CD314952F` + CONFLICT SHA `0D9897932DCD6CE1` + INDEX SHA `B236E18B193E735E` Phase 4 marker 추가 의도 transition, STAGE 9 baseline → Phase 4 marker)
- [x] 77 V1/V2 파일 Status APPROVED 전환 (DRAFT 잔존 0) (실측 78 V1/V2 P4-1 + P4-2 inheritance, V1 +2 plan literal drift textual notation only)
- [x] ReadOnly TRUE 진입 80+ .md ALL + 변경 절차 명시 (실측 96 production .md (V1 44 + V2 34 + 메타 4 + _index 7 + _verification NEW 7) ALL ReadOnly TRUE marker + audit log 변경 절차 영구 명시, 목표 80+ 초과)
- [x] V-21 영구 PASS (Status APPROVED 카운트 검증) (96/96 production .md ALL APPROVED ≥ 80, V-21 영구 PASS 강화)
- [x] production 측정 실측값 (APPROVED 카운트 + ReadOnly 카운트) baseline 영구 (APPROVED 96 + ReadOnly 96 + DRAFT 잔존 0 production scope + template 예시 2 위치 의도 보존)
- [x] Phase 5 entry-gate forward-defined 작성 완료 (phase4_status_promotion_report.md §6 5-entry forward-defined)
- [x] **[Phase 16 NEW] 80+ production .md ALL Status APPROVED + ReadOnly TRUE 영구 baseline 조건 충족 (실측 96/96 APPROVED + 96/96 ReadOnly TRUE + Last-reviewed 2026-05-23 통일, 목표 80+ 초과 + audit caveat template 2 위치 의도 보존)**

**산출물**: 본 계획서 + AUTHORITY_CHAIN + CONFLICT_LOG + INDEX + 77 V1/V2 + 7 _index = 11 추가 transform Status APPROVED + ReadOnly TRUE + `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\_verification\phase4_status_promotion_report.md` v1.0 NEW (96/96 production-ready 정본 승급 + Phase 5 5-entry forward-defined + V-21 영구 PASS 강화)
</details>

<details>
<summary><b>P4-5. PART2 정본 선언 2개소 영구 baseline + broken_links=0 영구 (P3-5 inheritance)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-5 "PART2 V1-Phase 1 L1679 + V1-Phase 6 L2556 정본 선언 2개소 영구 baseline + 단일 링크 테이블 5 row 영구 + broken_links=0 영구" (P3-5 forward-defined)
- §7 전환 게이트: G4-5 "PART2 영구 정합"
- §6 이슈: STAGE 9 Phase A PART2 정본 선언 2개소 inheritance
- 교차 도메인: 없음 (PART2 ↔ sot 2/ 양방향 정합)
- Part2 V3-Phase 매핑: V1-Phase 1 (PART2 L1679 보조 모듈 5개) + V1-Phase 6 (L2556 AI Investing MVP+MCP 참조 SOT) 영구 baseline
- production 측정 실측값: PART2 L1679 정본 선언 + L2556 정본 선언 + 단일 링크 테이블 5 모듈 (I-4/I-13/I-14/I-16/S-1) row + broken_links=0 영구
- Phase 5 entry-gate 충족 조건: PART2 ↔ sot 2/ 양방향 정합 broken=0 영구 + V-22 영구 PASS + R8 단일 테이블 집중 영구
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: PART2 정본 선언 2개소 영구 확정 + 단일 링크 테이블 5 row 영구 + PART2 ReadOnly 보호 (변경 절차 명시) + broken_links=0 영구 baseline

**목표**: P3-5 결과를 PART2 production 정본으로 영구 확정한다. 정본 선언 2개소 (L1679 + L2556) + 단일 링크 테이블 5 row + broken_links=0 영구 baseline 확립.

**입력 파일**:
- P3-5 산출물 (PART2 정본 선언 2개소 추가본)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` V1-Phase 1 L1677~L1679 + V1-Phase 6 L2546~L2556
- 5 submodule 폴더 경로 (01_multimodal-interpreter / 02_multimodal-renderer / 03_summarizer / 04_knowledge-search / 05_self-check)
- 본 계획서 §4 R8 단일 테이블 집중 규칙

**절차**:
1. PART2 L1679 V1-Phase 1 정본 선언 + L2556 V1-Phase 6 정본 선언 production 정본 확정.
2. 단일 링크 테이블 5 row 영구 baseline (I-4 + I-13 + I-14 + I-16 + S-1).
3. 본문 산발 링크 0건 영구 (R8 위반 0).
4. PART2 ↔ sot 2/ 양방향 broken_links=0 영구 검증.
5. PART2 변경 영역 byte EXACT (정본 선언 2개소 + 링크 테이블만, 기타 영역 보존).
6. production 실측 측정: PART2 정본 선언 2개소 + 링크 테이블 5 row + broken_links=0.
7. AUTHORITY_CHAIN.md cross-check (PART2 V1-Phase 1 + V1-Phase 6 정본 출처 변경 0).
8. Phase 5 entry-gate forward-defined: PART2 영구 baseline + V1 MVP 운영 시작.

**검증**:
- [x] PART2 L1679 V1-Phase 1 정본 선언 영구 확정 ("**구현 정본**: 보조 모듈 구현 상세는 sot 2/1-2_Auxiliary-Modules/이 Single Source of Truth입니다.", Phase 3 P3-5 inheritance, P4-5 변경 0)
- [x] PART2 L2556 V1-Phase 6 정본 선언 영구 확정 ("sot 2/1-2_Auxiliary-Modules/ (S-1 Self-check Engine 구현 상세 정본)", Phase 3 P3-5 inheritance, P4-5 변경 0)
- [x] 단일 링크 테이블 5 row 영구 baseline (R8 단일 테이블 집중) (I-4→01_multimodal-interpreter + I-13→02_multimodal-renderer + I-14→03_summarizer + I-16→04_knowledge-search + S-1→05_self-check, 정본 선언 1건 L1679 + L2556 보조 선언 매핑)
- [x] broken_links=0 영구 baseline (5 submodule + 00_common + 06_mapping 디렉토리 전수 실존, V-11/V-22/V-23 inheritance)
- [x] PART2 byte EXACT (정본 선언 + 링크 테이블만) (PART2 SHA `5B555A940BB4E72C` baseline EXACT, P4-5 ZERO write)
- [x] production 측정 실측값 (정본 선언 2개소 + 5 row + broken=0) baseline 영구 (L1679 + L2556 정본 2개소 + 5 row submodule 매핑 + broken_links=0 영구)
- [x] Phase 5 entry-gate forward-defined 작성 완료 (phase4_part2_sync_report §7 5-entry forward-defined)
- [x] **[Phase 16 NEW] PART2 정본 선언 2개소 영구 + 링크 테이블 영구 + broken=0 영구 조건 충족 (PART2 byte EXACT + 정본 선언 2개소 + 5 row 매핑 + broken_links/orphan_files/missing_index = 0)**

**산출물**: `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` V1-Phase 1 L1679 + V1-Phase 6 L2556 정본 선언 영구 (446,456 B / 6,454 LF / SHA `5B555A940BB4E72C` baseline EXACT ZERO write) + `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\_verification\phase4_part2_sync_report.md` v1.0 NEW (PART2 sync 영구 baseline + Phase 5 5-entry forward-defined)
</details>

<details>
<summary><b>P4-6. INDEX.md v2.X + 7 _index.md 영구 동기화 + L3 완성률 영구 baseline (P3-6 inheritance)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-6 "INDEX.md v2.X + 7 폴더별 _index.md 영구 동기화 + L3 완성률 ≥ 90% 영구 유지" (P3-6 forward-defined)
- §7 전환 게이트: G4-6 "INDEX 영구 SoT"
- §6 이슈: STAGE 9 Phase A INDEX major bump v2.0 inheritance + Status DRAFT → APPROVED
- 교차 도메인: 없음
- Part2 V3-Phase 매핑: V1-Phase 1 + V1-Phase 6 정합 영구
- production 측정 실측값: INDEX.md v2.X byte/SHA/LF + 7 폴더별 _index.md (00_common + 01~05 5 submodule + 06_mapping) byte/SHA aggregate + 전체 80+ 파일 inventory + L3 완성률 ≥ 90% 영구
- Phase 5 entry-gate 충족 조건: INDEX 영구 SoT + 7 _index.md 영구 동기화 + V-23 영구 PASS
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: INDEX.md Status APPROVED + ReadOnly TRUE + v2.X 단일 SoT 영구 + 7 _index.md 동기화 영구 baseline + L3 완성률 ≥ 90% 영구 유지

**목표**: P3-6 결과를 INDEX.md production 정본으로 영구 승급한다. 80+ 파일 inventory + L3 완성률 영구 + 7 _index.md 동기화 영구 + R2 마스터 단일 SoT 영구.

**입력 파일**:
- P3-6 산출물: `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\INDEX.md` v2.0 → v2.X minor bump
- 7 폴더별 _index.md (00_common + 01_multimodal-interpreter ~ 05_self-check 5 submodule + 06_mapping)
- P4-1 ~ P4-5 산출물 (V2/V3 promotion + CONDITIONAL closure + V-01~V-24 + Status APPROVED + PART2 정본)
- STAGE 9 STEP_C 5 _index footer "truly_converged_v3 (2026-05-10)" inheritance

**절차**:
1. INDEX.md 헤더 메타데이터 갱신 (v2.X minor bump → Phase 4 완료 마킹, Status APPROVED).
2. 폴더별 row 갱신: 폴더명 / 파일 수 / L3 완성률 / Status 분포 (APPROVED 전수).
3. L3 완성도 요약 테이블 production 정본 (P3-1 + P3-2 결과 → 77×9=693 cells PASS 영구).
4. 7 _index.md production 정본 동기화 (각 폴더 V2/V3 산출물 등재 + STEP_C footer inheritance + Phase 4 완료 마킹).
5. broken_links / orphan_files / missing_index 영구 0건.
6. STAGE 9 Phase A STEP_C inheritance 결과 + Phase 4 promotion 통합.
7. ReadOnly TRUE 진입 (INDEX.md + 7 _index.md immutable).
8. production 실측 측정: INDEX byte/SHA/LF + 7 _index.md aggregate + 전체 파일 수 + L3 완성률.
9. Phase 5 entry-gate forward-defined: INDEX 영구 SoT + V1 MVP 운영 시작 ready.

**검증**:
- [x] INDEX.md Status APPROVED + v2.X minor bump + Phase 4 완료 마킹 (v2.0 → **v2.1** minor bump + §10 변경 이력 v2.1 row 신규 추가 + [PHASE4_READY: 1-2 — 2026-05-23 최종 확정])
- [x] 7 _index.md 전수 갱신 + 동기화 완료 (00_common + 01~05 5 submodule + 06_mapping 7/7 Phase 4 ✅ APPROVED + ReadOnly TRUE 통일, P4-4 inheritance)
- [x] L3 완성도 요약 테이블 production 정본 (693 cells PASS 영구) (V2 module 34 × 9 = 306 cells PASS 100% + V1 42 × 9 = 378 cells inheritance 100% = **693 cells 100% PASS** 영구 ≥ 90% 목표 초과)
- [x] broken_links=0 + orphan_files=0 + missing_index=0 (V-23 영구 PASS) (INDEX → 폴더/파일 link valid + 모든 V1/V2 INDEX 등재 + 7 _index.md + 마스터 INDEX 전수 존재)
- [x] STAGE 9 STEP_C inheritance + Phase 4 promotion 통합 (INDEX major v2.0 STAGE 9 → minor v2.1 Phase 4 + 5 _index footer "STEP_C 최종 확정" inheritance + [PHASE3_READY v2: 1-2 — 2026-05-10] → [PHASE4_READY: 1-2 — 2026-05-23])
- [x] ReadOnly TRUE 진입 (INDEX + 7 _index.md immutable) (INDEX.md ReadOnly TRUE marker + 7 _index.md 통일, P4-4 inheritance + P4-6 영구)
- [x] production 측정 실측값 (file count + L3 완성률) baseline 영구 (production scope 98/98 ALL APPROVED + L3 100% PASS + 99 total .md - 3 ARCHIVED 류)
- [x] Phase 5 entry-gate forward-defined 작성 완료 (phase4_index_sync_report §7 11-entry forward-defined 전수 통합)
- [x] **[Phase 16 NEW] INDEX 마스터 v2.X + 7 _index.md 동기화 영구 + L3 ≥ 90% 영구 baseline 조건 충족 (실측 INDEX v2.1 + 7/7 통일 + L3 100% PASS 693 cells, ≥ 90% 초과 ✅)**

**산출물**: `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\INDEX.md` v2.1 Phase 4 정본 (Status APPROVED + ReadOnly TRUE + §10 변경 이력 v2.1 row 신규) + 7 _index.md production 정본 (P4-4 inheritance + P4-6 영구) + `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\_verification\phase4_index_sync_report.md` v1.0 NEW (FINAL P4, INDEX v2.X 영구 SoT + L3 완성률 영구 baseline + Phase 5 11-entry 전수 forward-defined + [PHASE4_READY: 1-2 — 2026-05-23 최종 확정])
</details>

<details>
<summary><b>Phase 4 세션 전체 검증 결과 (1-2, 2026-05-23)</b></summary>

- **P4 블록 수**: **6 완료 (P4-1 ✅ ~ P4-6 ✅)** — 단일 대화창 연속 진행, 본 도메인 Phase 4 implementation 첫 도메인 (Wave 1 #1, DAG #1)
- **R cascade 통산**: ~168 verifications (P4-1 ~26 + P4-2 ~28 + P4-3 ~26 + P4-4 ~28 + P4-5 ~26 + P4-6 ~32), drift 8 textual notation only ALL closure tcv1 first-pass-after-R₁₂-fix 6/6 CONFIRMED
  - P4 블록별 drift fix 매트릭스:
    - P4-1: D-R2-1 (1 fix, "PASS 22 + CONDITIONAL 12" → "21+13" same-length char-swap §11 V-17 SoT 1-off 정합)
    - P4-2: D-R2-1 char-swap 10위치 + D-R3-1 synthesis (2 fix, "CONDITIONAL 12 row" → "13 row" + l3_conditional_remediation_phase3.md 합성)
    - P4-3: **0 fix (NO-DRIFT direct path 1번째 ⭐)**
    - P4-4: D-R2-1 + D-R2-2 (2 fix, 95→96 post-creation count drift)
    - P4-5: **0 fix (NO-DRIFT direct path 2번째 ⭐⭐, PART2 ZERO write specialty)**
    - P4-6: D-R2-1/2/3 (3 fix, 97→98 + 산출물 count 정합)
  - ALL textual notation only, byte/SHA 무결성 100% 보존 통산
- **byte/SHA pre/post 통산**:
  - 종합계획서: pre P4-1 ① **216,871 B / 3,225 LF / SHA `977322636D20EB7C`** → post P4-6 R₁₂ final **224,424 B / 3,227 LF / SHA `76F141160FE1042A`**, **Δ +7,553 B / +2 LF** (P4-1 +1,132 + P4-2 +1,201 + P4-3 +1,315 + P4-4 +1,535 + P4-5 +1,070 + P4-6 +1,300, 모든 R₁₂ fix는 same-length char-swap Δ +0 B)
  - PROGRESS.md: pre ENTRY ⬜ → post P4-6 ③.5 **38,899 B / 507 LF / SHA `0959F3CC1B73E5C9`** (Δ +35K post-entry baseline, mid-checkpoint × 6 누적)
  - INDEX.md: STAGE 9 baseline (`005F277DEDD34167`) → P4-4 transition (`B236E18B193E735E`) → **P4-6 v2.1 minor bump (`1C1DB30702F81109`)**
  - 메타 baseline transition (P4-4 의도): AUTHORITY `23C01CF5539E0276` → `6E95A41CD314952F` / CONFLICT `1C702DB501B4EA2F` → `0D9897932DCD6CE1`
  - PART2 baseline 영구: `5B555A940BB4E72C` ZERO write (P4-1~P4-6 통산 보존)
- **V3 산출물 production-ready 정본 승급**:
  - V2 35 NEW (V2 module 34 + _verification phase2_v2 1) ALL Status APPROVED + ReadOnly TRUE ✅
  - V1 42 strict L3 PASS inheritance + Status APPROVED + ReadOnly TRUE ✅
  - L3 매트릭스 V2 module 34 × 9 = 306 cells PASS **100%** + V1 inheritance 100% → 693 cells 100% PASS 영구 baseline
  - 모든 78 V1/V2 + 11 메타+_index + 9 NEW _verification = **98 production .md ALL Status APPROVED + ReadOnly TRUE 영구 baseline**
- **production .md 승급 완료**: **98/98 (1-2 RO FALSE — 직접 편집, STAGE 9 Phase A inheritance marker)**:
  - V1 44 (DRAFT → APPROVED Phase 4 ✅) — P4-1
  - V2 APPROVED 21 (Phase 3 → Phase 4 ✅ marker) — P4-1
  - V2 REVIEW 13 (CONDITIONAL → PASS) — P4-1+P4-2
  - 메타 4 (AUTHORITY/CONFLICT/INDEX/계획서) Phase 4 ✅ marker + Last-reviewed + ReadOnly TRUE — P4-4
  - _index 7 (DRAFT → APPROVED Phase 4 ✅) — P4-4
  - _verification NEW 9건 (l3_judgment + phase4_v2_v3_promotion + l3_conditional_remediation + phase4_conditional_closure + phase3_final_checklist + phase4_v01_v24_baseline + phase4_status_promotion + phase4_part2_sync + phase4_index_sync) — P4-1~P4-6 산출물
  - audit caveat: 종합계획서 L653 + L2641 ```markdown``` 코드 블록 내 template 예시 DRAFT 2 위치 의도 보존
- **LOCK 변경 0 + DEFINED-HERE 변경 0 + FABRICATION 0**:
  - LOCK-AX-01~15 distinct 15 + change_lock 4 = 19건 byte EXACT (lock_value_registry 통산 보존)
  - §3.4 LOCK 정의 + §10 V-01~V-24 정본 영역 무손상
  - parent-executed Subagent 0회
- **abort 9종 NOT FIRED self-fire 0 통산** (P4-1 ~ P4-6 ALL):
  - UPSTREAM_V3_SPEC_MISSING / PRODUCTION_WRITE_VIOLATION / STAGE9_READONLY_RESTORE_FAIL / STATUS_TRANSITION_FAIL / V3_PRODUCTION_PROMOTION_FAIL / CROSS_HANDOFF_DRIFT / BILATERAL_SOT2_DRIFT (post 단계 ⑤에서 처리) / DOWNSTREAM_PROPAGATE_MISS (post 단계 ⑥에서 처리) / R_CASCADE_NOT_CONVERGED
- **6 anchor 충족**: 안전 (메타 baseline 통산 보존 + LOCK byte EXACT 통산) · 누락 0 (98/98 + R cascade verifications 전수) · 오류 0 (drift 8 ALL R₁₂ closure, abort 9종 NOT FIRED) · 미세 (textual notation only, byte/SHA 무결성 100% 보존) · 수렴 (6/6 truly_converged_v1 first-pass-after-R₁₂-fix CONFIRMED + NO-DRIFT direct path 2회) · 재검증 (R₁₃ × 3 round × 6 P4 = 18 stable cascade) ALL ✅
- **upstream 도메인 의존 검증**: Wave 1 첫 도메인 — upstream 0건 auto PASS ✅ (DAG #1)
- **downstream 도메인 영향 분석**: 6-1 UI-UX-System (Wave 2 #13, response_envelope_v2 / common_types_v2 inheritance, 6 V3 산출물 forward-defined) + 6-2 Security-Governance (Wave 2 #14, V-14 ResponseEnvelope + PII 마스킹 정합 + E7 Security cross-handoff) + 1-1 Verifier-Reasoning-Engines (Wave 2 #21 RO TRUE, LLM-AUX 5 모듈 인터페이스 연동) — **⑥ downstream 전파 단계에서 reference 추가 처리** (1-1은 STAGE 9 RO TRUE → sandbox-only reference)
- **Phase 5 entry-gate forward-defined 통산**: 6/6 P4 모두 명시 ✅
  - P4-1: phase4_v2_v3_promotion_report §6 5-entry + l3_judgment §5 7-entry
  - P4-2: phase4_conditional_closure_report §6 5-entry + l3_conditional_remediation §4 5 보완 항목 ~2026-06-09
  - P4-3: phase4_v01_v24_baseline_report §7 5-entry + phase3_final_checklist §8 5-entry
  - P4-4: phase4_status_promotion_report §6 5-entry
  - P4-5: phase4_part2_sync_report §7 5-entry
  - P4-6: phase4_index_sync_report §7 **11-entry 전수 통합** + [PHASE4_READY: 1-2 — 2026-05-23 최종 확정]
- **NO-DRIFT direct path specialty 2회**: P4-3 (V-01~V-24 baseline) + P4-5 (PART2 ZERO write) — Pattern A first-pass-after-zero-fix 달성
- **사용자 paste 통산**: 6 P4 cycle × 3 paste (② R cascade + ③ 최종 확정 + ③.5 PROGRESS) = **18 paste**, 도메인 종료 단계 진입 ④ 1 trigger 추가 = **19 paste**
- **사용자 명시 Pattern A "안전·누락 0·오류 0·완벽" 통산 충족**: 통산 33+ 사례 (각 P4 cycle ② cascade post 보고 + ③ 게이트 응답)
- **다음 단계**: ⑤ bilateral 갱신 (종합계획서 §7 Phase 4 헤더 ✅ + SOT2_MASTER_INDEX 1-2 row 갱신) → ⑥ downstream 전파 (6-1 + 6-2 + 1-1) → ⑦ PROGRESS.md domain-complete (Stage A — ENTRY_PROMPT ⑦단계 ⬜ → ⬛)

</details>

---

## 8. 파일 역할 분리 명세

### 8.1 계획서 vs 상세명세 vs 서브폴더 파일

| 구분 | 파일 | 역할 | 변경 시기 |
|------|------|------|----------|
| **계획서** | AUXILIARY_MODULES_구조화_종합계획서.md (본 문서) | 구조화 전략, 거버넌스 규칙, Phase 계획, LOCK 선언 | Phase 계획 변경 시 |
| **상세명세** (LEGACY) | AUXILIARY_MODULES_상세명세.md → _archive/ | 기존 5개 모듈 상세 (마이그레이션 원본) | 변경 불가 (아카이브) |
| **권한 선언** | AUTHORITY_CHAIN.md | 권한 체인, LOCK 보호 | 권한 체계 변경 시 |
| **마스터 인덱스** | INDEX.md | 폴더/파일 목록 + Status + Version | 파일 추가/삭제 시 |
| **충돌 기록** | CONFLICT_LOG.md | 충돌 발생/해결 기록 | 충돌 발생 시 |
| **공통 정의** | 00_common/*.md | ResponseEnvelope, 타입, 에러, 타임아웃 | 인터페이스 변경 시 |
| **모듈 상세** | 01~05_*/*.md | 각 모듈의 구현 상세 (What + How) | 구현 진행 시 |
| **매핑/거버넌스** | 06_mapping/*.md | 의존성 그래프, 인터페이스 계약, LOCK 레지스트리, 중복 감사 | 구조 변경 시 |

### 8.2 D2.0 문서와의 역할 분리

| 항목 | D2.0-01 §5.6 | D2.0-02 §7 | D2.0-06 | sot 2/ |
|------|-------------|-----------|---------|--------|
| 모듈 존재/분류 | O (정본) | — | — | 참조만 |
| 파이프라인 아키텍처 | — | O (정본) | — | 참조만 |
| Memory/Storage 설계 | — | — | O (정본) | 참조만 |
| 모듈 내부 구현 로직 | — | — | — | O (정본) |
| 입출력 스키마 상세 | — | 개요만 | — | O (정본) |
| fallback chain | — | — | — | O (정본) |
| 타임아웃 정책 | — | — | — | O (정본) |
| 테스트 시나리오 | — | — | — | O (정본) |

### 8.3 PART2와의 역할 분리

| 항목 | PART2 (When + Where) | sot 2/ (What + How) |
|------|---------------------|---------------------|
| Phase 배정 | O (정본) | 참조 금지 |
| 코드 위치 | O (정본) | 참조 가능 |
| 구현 알고리즘 | 링크만 (`> 상세: sot 2/...`) | O (정본) |
| 입출력 스키마 | 요약만 (1~2줄) | O (정본) |
| 테스트 기준 | 합격 기준만 | O (테스트 시나리오) |

---

## 9. 충돌 해결 프로토콜

### 9.1 충돌 유형별 해결

| 충돌 유형 | 설명 | 판정 기준 | 해결 방법 |
|----------|------|----------|----------|
| **LOCK 충돌** | sot 2/ 파일이 LOCK 값과 불일치 | LOCK 값이 절대 우선 | sot 2/ 파일 즉시 수정 |
| **D2.0 간 충돌** | D2.0-01과 D2.0-06 값 불일치 | 문서 발행 순서 (최신 우선) + 명시적 LOCK 우선 | CONFLICT_LOG에 기록, 상위 권한자 판정 |
| **PART2 ↔ sot 2/** | Phase 배정 vs 구현 상세 모순 | PART2가 When 정본, sot 2/가 How 정본 | 각자 관할 영역만 수정 |
| **모듈 간 충돌** | 두 모듈이 같은 개념을 다르게 정의 | cross_module_dedup.md 정본 소유자 | 비정본 모듈에서 `> 참조:` 링크로 교체 |
| **상세명세 vs 서브폴더** | 아카이브 원본과 분배 파일 불일치 | 서브폴더 파일이 현행 정본 | 아카이브는 변경 불가, 서브폴더만 수정 |

### 9.2 충돌 해결 절차

```
1. 충돌 발견
   ↓
2. CONFLICT_LOG.md에 등록 (날짜, 유형, 파일, 내용)
   ↓
3. 판정 기준에 따라 자동 해결 가능 여부 확인
   ├── 자동 해결 가능 → 즉시 수정 + CONFLICT_LOG에 조치 완료 기록
   └── 수동 판정 필요 → 상위 권한자(프로젝트 오너) 에스컬레이션
       ↓
4. 판정 결과 반영 + CONFLICT_LOG 갱신
```

### 9.3 충돌 방지 규칙

| 규칙 | 설명 |
|------|------|
| 단방향 참조 | 하위 문서 → 상위 문서 역참조 금지 |
| LOCK 인라인 인용 | LOCK 값은 반드시 원문 그대로 인용, 재해석 금지 |
| 정본 소유자 등록 | 중복 개념 발견 시 즉시 cross_module_dedup.md에 등록 |
| INDEX.md 동기화 | 파일 추가/삭제 시 INDEX.md 동시 갱신 |

### 9.4 횡단 관심사 참조 *(S7-2 추가)*

| 횡단 도메인 | 적용 내용 |
|-----------|----------|
| 6-2 Security-Governance | PII 마스킹 정책 적용. 출력 삭제(sanitize) 규칙 준수 |

---

## 10. 검증 체크리스트

### 10.1 Phase 0 완료 검증

| # | 검증 항목 | 방법 | 합격 기준 |
|---|----------|------|----------|
| V-01 | AUTHORITY_CHAIN.md 존재 | 파일 확인 | 존재 + §3.1~§3.4 전체 포함 (다이어그램 2건, 테이블 3건, LOCK 인용 10건) + LOCK-AX 번호 §5A 정합 |
| V-01a | PART2 정본 선언 존재 | grep "구현 정본" PART2 | V1-Phase 1 `## Week 3-4: 보조 모듈` 직후 + V1-Phase 6 참조 SOT에 각 1건 |
| V-02 | lock_value_registry.md 존재 | 파일 확인 | 존재 + 19개 LOCK 항목 전수 등재. **불일치 4건 문서화 필수**: D-01(AX-02 출처 부재, HIGH), D-02(AX-03 QoD 5-factor 갱신, HIGH), D-03(AX-14 복합 출처, LOW), D-04(AX-09 명칭 차이, LOW) → CONFLICT_LOG.md에 HIGH 2건 등재 |
| V-03 | 분배 매핑 확정 | §5B 테이블 완성도 + 줄 회계 | 336줄 전수 회계 (분배 대상 281줄 + 분배 제외 55줄, 미지정 0줄) + §5B "확정일" 태그 존재 |
| V-04 | cross_module_dedup.md 존재 | 파일 확인 | 존재 + 6개 이상 중복 그룹 정본 배정 (실제: 7건 = DG-01~DG-07, **확정일: 2026-03-29**) |
| V-05 | CONFLICT_LOG.md 존재 | 파일 확인 | 존재 + 프로토콜 섹션 포함 |

### 10.2 Phase 1 완료 검증 ✅ 11/11 PASS (2026-04-07)

| # | 검증 항목 | 방법 | 합격 기준 | 결과 |
|---|----------|------|----------|------|
| V-06 | 폴더 구조 | `ls -R` | 9개 폴더 전수 존재, 3단계 이상 0건 | ✅ PASS (1-1) |
| V-07 | 파일 수 | `find *.md` | 40개 이상 .md 파일 | ✅ PASS — **56 .md** (≥40, INDEX.md §9 합계 정합) |
| V-08 | 메타데이터 헤더 | `grep "Status:"` | 전 파일 헤더 존재, 누락 0건 | ✅ PASS (1-3, 35 파일 6필드 100%) |
| V-09 | fallback_chain.md | 5개 폴더 확인 | 5건 전수 존재, 각 3개+ 실패 지점 | ✅ PASS (1-5, 22 F-XXX-NN ID) |
| V-10 | 공통 파일 | 00_common/ 확인 | 4개 파일 존재 | ✅ PASS (1-4, response_envelope/common_types/error_taxonomy/timeout_policy) |
| V-11 | INDEX.md | 파일 확인 | 7개 폴더 전수 등재 | ✅ PASS (1-8, 7 _index + master INDEX, broken 0) |
| V-12 | 상세명세 아카이브 | _archive/ 확인 | 원본 존재, 읽기 전용 | ✅ PASS (1-9, byte-identical 10780B/336L + redirect + sidecar) |
| V-13 | LOCK 인용 형식 | `grep "LOCK"` | 전부 `> LOCK (출처): [원문]` 형식 | ✅ PASS (1-3/1-4 LOCK-AX-NN 통일) |
| V-14 | ResponseEnvelope | 00_common/ 확인 | D2.0-02 §5.1.1 LOCK 사양 준수 (출처 정정 §7→§5.1.1, 1-4 SoT crosscheck) | ✅ PASS (1-4) |
| V-15 | 인터페이스 계약 | interface_contracts.md | 5개 모듈 전수 등록 | ✅ PASS (1-7, C-01~C-14 14건, 19 엣지 전수 매핑) |
| V-16 | 모듈 의존성 | module_dependency_graph.md | 5개 모듈 + 외부 모듈 의존성 기술 | ✅ PASS (1-6 v1.1, 노드 14 / 엣지 19 / cycle 0) |

**Phase 1 전환 게이트 결과**: 폴더 구조 ✅ + 56 파일 ✅ (≥40) + 전 파일 헤더 ✅ + Part2 상태 PARTIAL→COMPLETE ✅ + V-22 (PART2 링크 단일 테이블) ✅ → **Phase 2 진입 가능**.

### 10.3 Phase 2 완료 검증

| # | 검증 항목 | 방법 | 합격 기준 |
|---|----------|------|----------|
| V-17 | L3 판정 | 전 파일 L3 기준 적용 | 전 파일 PASS 또는 CONDITIONAL |
| V-18 | 의사코드 존재 | 구현 파일 확인 | 파이프라인 파일 전부 의사코드 포함 |
| V-19 | 에러 핸들링 | 구현 파일 확인 | 전 파일에 에러 시나리오 기술 |
| V-20 | LOCK 참조 정합 | lock_value_registry.md 대조 | 인용된 LOCK 값 = 레지스트리 값 |

### 10.4 Phase 3 완료 검증

| # | 검증 항목 | 방법 | 합격 기준 |
|---|----------|------|----------|
| V-21 | 전 파일 Status | `grep "APPROVED"` | 전 파일 APPROVED |
| V-22 | PART2 링크 | PART2 확인 | sot 2/ 참조 테이블 갱신 완료 |
| V-23 | INDEX.md 최종 | 파일 확인 | 파일 수, Status, Version 최신 |
| V-24 | 아카이브 무결 | _archive/ 확인 | 원본 미변경 |

---

## 11. 보완 사항

> **Status**: Phase 5 FINAL PASS 검토 완료 (2026-03-24)

| 날짜 | 보완 사항 | 심각도 | 조치 계획 | 상태 |
|------|----------|--------|----------|------|
| 2026-03-24 | FR-1: V-02 LOCK 항목 수 불명확 (19개 = LOCK-AX-01~15 + change_lock 4건) | LOW | 본 계획서 §10 V-02 비고란에 내역 주석 추가 | ACKNOWLEDGED |
| 2026-03-24 | FR-2: AUTHORITY_CHAIN.md Status=DRAFT | MEDIUM | AUTHORITY_CHAIN.md Status → APPROVED 교정 | RESOLVED |
| 2026-03-24 | 종합: 기능적 보완 사항 없음 | — | — | — |
| **2026-05-10** | **STAGE 9 1-2 STEP_B (chain s9_36_a_2): Phase 2 L3 보강 V2 35 NEW 작성 완료 (1:1 매핑, 3-2 도메인 STAGE 7 STEP_B 패턴 직계 계승). 검증 결과: PASS 22 + CONDITIONAL 12 + FAIL 0. F-04 (timeout §2 표 4 신규 정본화) RESOLVED + F-06 (out-of-scope 호출 경로) RESOLVED. F-05/F-07/F-10/F-11 PARTIAL/PENDING (STEP_C). D-01/D-02 인지. V1 byte EXACT 보존 (42/42 OK × 3회). LOCK-AX-01~15 변경 0. 6-2 PII 30+ 위치 cross-ref. 분기: a CLEAN (sandbox-only)** | **INFO** | **sandbox 작성 완료, A-3 STEP_C truly_converged_v3 + A-4 production sync 두 단계 게이트 9.1-A/B 예정 (산출물 위치: `_verification/phase2_verification_v2.md`)** | **COMPLETE (STEP_C 종료, 2026-05-10)** |
| **2026-05-10** | **STAGE 9 1-2 STEP_C (chain s9_37_a_3): truly_converged_v3 first-pass. Phase F 6+1/6+1 PASS + Phase G 8/8 PASS + R₁~R₈ 8 round 0 changes cascade (3차 강건성). V1 immutability verify 3회 × 42/42 OK (STAGE 9 통산 +8회). AUTHORITY §7 신설 v1.1→v1.2 (LOCK count duality methodology + V2 35 NEW LOCK 인용 출처 매트릭스 + Sandbox drift 일괄 정합 기록 + PHASE3_READY 최종 확정). CONFLICT 11건 본격 처리 v2.0→v2.1 (F-01 + F-04~F-09 + F-10/F-11 + D-01 DEFERRED-EXTERNAL_DEPENDENCY + D-02 RESOLVED-PARTIAL) + §0 변동점 신설. INDEX 헤더 v1.0+body v1.2/v1.3 → v2.0 동시 정합 major bump + Status DRAFT→APPROVED. 5 _index footer "STEP_C 최종 확정 (truly_converged_v3, 2026-05-10)" 1줄 append × 5 (4-1 R2 패턴 직계). SOT2_MASTER 1-2 row × 4 지점 sandbox preview (L86 heading + L87 구현 현황 + L87 직후 PHASE3_READY 블록 신설 + L1290 표 row). LOCK count duality §V2-only N=389 / 전체 M=765 / V1-only 376. 6-2 PII 31 V2 / 244 raw refs 광범위 sync 확인. abort 9종 NOT FIRED + self-fire 0 통산. 사용자 정밀성 6 anchor 156 cell (26 sub-step × 6) 100% 충족.** | **INFO** | **STEP_C 종료, A-4 (production sync 14 sub-step + 게이트 9.1-A/B 두 단계 분리) 진입 ready 9/9. 산출물: PHASE_F_REPORT + PHASE_G_REPORT + STEP_C_HANDOFF (mini-handoff §0~§I) + 3 V1 verify log + R cascade log + 4 PHASE3_READY 6-tier preview + memory 6-target preview 등 13 NEW.** | **COMPLETE (STEP_C truly_converged_v3, 2026-05-10)** |

---

## 12. FINAL REVIEW 결과

> **Status**: FINAL REVIEW 완료 (2026-03-24)

| 리뷰 항목 | 결과 | 비고 |
|----------|------|------|
| 구조 완성도 | PASS | 전체 섹션 구조 및 파일 트리 정합 확인 |
| LOCK 정합성 | PASS | 15개 LOCK-AX + 4개 change_lock = 19개 대조 일치 |
| L3 판정 결과 | PASS | Phase 2 ✅ 완료 (V-17 row content PASS 21 + CONDITIONAL 13 + FAIL 0, 2026-05-10) + Phase 3 ✅ 완료 (2026-05-14, drift fix sub-cycle Path A, V-17 SoT 1-off 검출 + row authority 채택) |
| PART2 동기화 | PASS | PART2 Phase 배정과 본 계획서 Phase 일정 일치 확인 |
| 총평 | APPROVED | S8-1 QC 등급 A |

---

## 13. L3 전수 승급 계획

### 13.1 L3 정의 (9 요소)

> L3 = "구현 즉시 투입 가능" 수준. 개발자가 이 문서만으로 코드를 작성할 수 있어야 한다.

| 요소 | ID | 설명 | 필수 여부 |
|------|-----|------|----------|
| 목적 및 역할 | E1 | 모듈/기능이 왜 존재하고, 무엇을 해결하는가 | 필수 |
| 알고리즘 의사코드 | E2 | 핵심 로직의 단계별 의사코드 (Python-like) | 필수 |
| 입출력 스키마 | E3 | Pydantic 모델 또는 동등한 타입 정의 | 필수 |
| 인터페이스 시그니처 | E4 | ABC 메서드 시그니처 (파라미터 + 리턴 타입) | 필수 |
| 에러 핸들링 | E5 | 발생 가능한 에러 유형 + 처리 방법 | 필수 |
| 성능 목표 | E6 | 지연 시간, 처리량, 메모리 사용량 목표 | 필수 |
| 테스트 시나리오 | E7 | 정상/비정상/경계값 테스트 케이스 | 필수 |
| LOCK 참조 | E8 | 해당 파일에서 참조하는 LOCK 값 목록 | 해당 시 필수 |
| 의존성 명세 | E9 | 외부 라이브러리, 다른 모듈 의존성 목록 | 필수 |

### 13.2 L3 판정 기준

| 판정 | 조건 |
|------|------|
| L3 PASS | 9요소 전수 기재 + E2 의사코드 포함 + E4 시그니처 포함 |
| L3 CONDITIONAL | 7~8요소 (E6 또는 E7 1건 누락 허용) → 30일 보완 |
| L3 FAIL | 6요소 이하 → Phase 2 재작업 |

### 13.3 모듈별 L3 승급 로드맵

| 모듈 | 현재 수준 | 보유 요소 | L3 보강 항목 | 예상 작업량 |
|------|----------|----------|------------|-----------|
| I-4 Multimodal Interpreter | L2 (스키마+파이프라인 존재) | E3 | **E1** 목적 명시, E2 의사코드, E5 에러 핸들링, E6 성능 목표, E7 테스트, **E9** 의존성 정형화 | 중 |
| I-13 Multimodal Renderer | L2 (인터페이스+테이블 존재) | E4 | **E1**, E2 의사코드, **E3** Pydantic I/O 스키마, E5 에러 핸들링, E6 성능, E7 테스트, DAG 스케줄링, **E9** | 중 |
| I-14 Summarizer | L2 (알고리즘 개요 존재) | E3 | **E1**, E2 의사코드 (증류 로직), **E4** ABC 시그니처, E5 에러, E6 성능, E7 테스트, **E9** | 중 |
| I-16 Knowledge Search | L2~L3 (LOCK 값 상세, 파이프라인 존재) | E3, E4, E8 | **E1**, E2 의사코드 (RRF 공식), **E5** 에러, **E6** 성능 목표, E7 테스트, 캐시 무효화, **E9** | 중 (소→중 상향) |
| S-1 Self-check | L2 (QoD 체계 존재) | E3 | **E1**, E2 의사코드 (sliding window), **E4** ABC 시그니처, E5 에러, **E6** 엔진 자체 성능, E7 테스트, **E8** LOCK-AX-03 참조, Prometheus 설정, **E9** | 중 |

> **0-3 검증 결과 (2026-03-29)**: 전 모듈에 **E1**(목적 명시)과 **E9**(의존성 정형화)가 공통 누락. I-16은 E5/E6 추가 발견으로 예상 작업량 소→중 상향. **굵은** 항목은 본 검증에서 신규 발견.

### 13.3.1 L3 완성도 요약 테이블 (Phase 3 ✅ 완료, 2026-05-14)

| 모듈 | V2 file 수 | PASS | CONDITIONAL | FAIL | L3 완성률 (PASS/total) |
|------|-----------|------|-------------|------|----------------------|
| I-4 (multimodal-interpreter) | 7 | 0 | 7 | 0 | 0.0% |
| I-13 (multimodal-renderer) | 10 | 10 | 0 | 0 | 100.0% |
| I-14 (summarizer) | 4 | 4 | 0 | 0 | 100.0% |
| I-16 (knowledge-search) | 4 | 2 | 2 | 0 | 50.0% |
| S-1 (self-check) | 5 | 4 | 1 | 0 | 80.0% |
| 00_common | 4 | 1 | 3 | 0 | 25.0% |
| **합계** | **34** | **21** | **13** | **0** | **61.8% (PASS strict) / 100% (PASS+CON, FAIL 0)** |

**판정 기준** (V-17 SoT 자체 규칙): 9/9 또는 8/9 → PASS / 6~7/9 → CONDITIONAL / ≤5/9 → FAIL
**Phase 2→3 게이트**: ✅ PASS (PASS+CON = 100%, FAIL 0)
**Phase 4 entry-gate**: ✅ PASS (FAIL 0건, V-17 row content 정합, V-17 summary L74-76 1-off typo는 별도 audit, lore 보정 follow-up session)
**SoT 출처**: `_verification/phase2_verification_v2.md` §2 V-17 row content (L38~L71)

### 13.4 L3 템플릿

```markdown
# [모듈명] - [기능명]

> **버전**: v1.0
> **Status**: DRAFT
> **L3 판정**: PENDING

## E1. 목적 및 역할
[이 기능이 왜 존재하고, 어떤 문제를 해결하는가]

## E2. 알고리즘 의사코드
```python
async def process(input: InputType) -> OutputType:
    # Step 1: ...
    # Step 2: ...
    # Step 3: ...
    pass
```

## E3. 입출력 스키마
```python
class InputType(BaseModel):
    field: type  # 설명

class OutputType(BaseModel):
    field: type  # 설명
```

## E4. 인터페이스 시그니처
```python
class IModuleName(ABC):
    @abstractmethod
    async def method(self, param: Type) -> ReturnType: ...
```

## E5. 에러 핸들링
| 에러 | 원인 | 처리 |
|------|------|------|

## E6. 성능 목표
| 메트릭 | 목표 | 측정 방법 |
|--------|------|----------|

## E7. 테스트 시나리오
| # | 시나리오 | 입력 | 기대 출력 | 유형 |
|---|---------|------|----------|------|

## E8. LOCK 참조
> LOCK (출처): [원문]

## E9. 의존성 명세
| 의존성 | 유형 | 버전 | 용도 |
|--------|------|------|------|
```

---

## 14. 실행 약점 대응 계획

### 14.1 식별된 약점

| # | 약점 | 심각도 | 발생 시나리오 | 대응 방안 |
|---|------|--------|-------------|----------|
| W-01 | 상세명세 분배 시 누락 | HIGH | 336줄 중 분배 대상 281줄 분배 시 일부 내용 누락 | §5B 줄 회계 + 분배 전/후 줄수 대조 (V-03, V-07 검증) |
| W-02 | LOCK 값 오인용 | CRITICAL | LOCK 값을 재해석하여 다른 형태로 기술 | R-02-4 규칙 + V-13/V-20 검증 |
| W-03 | 모듈 간 순환 참조 | HIGH | I-14 → I-16 → I-14 순환 발생 | §A 의존성 그래프에서 DAG 검증, 순환 발견 시 인터페이스 추상화 |
| W-04 | Phase 0 미완 상태에서 Phase 1 진입 | HIGH | 선행작업 불완전한 채 구조 재편 시작 | Phase 전환 게이트 (§7) 엄격 적용 |
| W-05 | 파일명 충돌 | MEDIUM | 서로 다른 모듈에 같은 파일명 존재 | 폴더로 네임스페이스 분리 (01~05) |
| W-06 | _archive 오수정 | MEDIUM | 아카이브된 원본을 실수로 수정 | git 기반 보호 + Phase 1 완료 시 V-24 검증 |
| W-07 | PART2 링크 깨짐 | HIGH | 파일명/경로 변경 후 PART2 미갱신 | R3 규칙 (파일명 변경 시 PART2 동기화 필수) |
| W-08 | ResponseEnvelope 불일치 | HIGH | 모듈별로 다른 형태의 ResponseEnvelope 사용 | 00_common/response_envelope.md 단일 정의 + R-02-5 규칙 |
| W-09 | L3 판정 기준 모호 | MEDIUM | E6/E7 "충분함"의 주관적 판단 | §13.2 정량적 기준 + 예시 파일 제공 |
| W-10 | 세션 간 컨텍스트 유실 | MEDIUM | 다중 세션에 걸친 작업 시 진행 상황 혼란 | INDEX.md에 각 파일 Status 기록 + CONFLICT_LOG 활용 |

### 14.2 약점 대응 우선순위

```
CRITICAL (즉시 대응):
  W-02: LOCK 값 오인용 → R-02-4 + V-13/V-20

HIGH (Phase 0에서 대응):
  W-01: 분배 누락 → 줄수 대조 프로세스
  W-03: 순환 참조 → §A 의존성 그래프 DAG 검증
  W-04: Phase Gate → §7 전환 게이트
  W-07: PART2 링크 → R3 규칙
  W-08: ResponseEnvelope → 00_common + R-02-5

MEDIUM (Phase 1에서 대응):
  W-05, W-06, W-09, W-10
```

### 14.3 세션 관리 프로토콜

| 항목 | 규칙 |
|------|------|
| 세션 시작 | INDEX.md의 Status 칼럼 확인 → 미완료 항목 식별 |
| 세션 중 | 작업 완료된 파일 즉시 INDEX.md Status 갱신 |
| 세션 종료 | CONFLICT_LOG에 미해결 충돌 기록, INDEX.md 최종 갱신 |
| 다음 세션 | INDEX.md 기반으로 진행 상황 파악 후 재개 |

---

## 부록 §A — 모듈 의존성 그래프

### A.1 내부 모듈 간 의존성

```
                    ┌──────────────────────────────────┐
                    │       ORANGE CORE Pipeline        │
                    │   (D2.0-02 §7: 5-stage, S0~S8)   │
                    └──────────┬───────────────────────┘
                               │
                               ▼
              ┌────────────────┴────────────────┐
              │                                 │
    ┌─────────▼─────────┐          ┌────────────▼────────────┐
    │  I-4 Multimodal   │          │  I-16 Knowledge Search  │
    │   Interpreter     │──embed──→│       Engine             │
    │ (입력 해석)        │          │ (지식 검색)              │
    └─────────┬─────────┘          └────────────┬────────────┘
              │                                 │
              │ interpreted                     │ search results
              │ input                           │
              ▼                                 ▼
    ┌─────────────────────────────────────────────────────┐
    │              I-5 Decision Engine (LOCK)              │
    │         (5-score based, change_lock=true)            │
    └─────────────────────┬───────────────────────────────┘
                          │
                          │ decision + render plan
                          ▼
              ┌───────────────────────┐
              │  I-13 Multimodal      │
              │  Output Renderer      │
              │  (다중 출력 포맷)      │
              └───────────┬───────────┘
                          │
                          │ rendered output
                          ▼
              ┌───────────────────────┐
              │  I-20 OutputComposer  │
              │  → Frontend           │
              └───────────────────────┘

    ┌─────────────────────┐        ┌────────────────────┐
    │  I-14 Summarizer &  │        │  S-1 Self-check    │
    │  Memory Distiller   │◄──QoD──│     Engine          │
    │ (요약/메모리 증류)    │        │ (시스템 상태 평가)   │
    └─────────┬───────────┘        └─────────┬──────────┘
              │                              │
              │ L0→L1                        │ QoD < 0.4
              │ memory ops                   │
              ▼                              ▼
    ┌─────────────────────┐        ┌────────────────────┐
    │  D2.0-06 Memory     │        │  I-25 SDAR         │
    │  4-Layer (LOCK)     │        │  (자가 수리)        │
    └─────────────────────┘        └────────────────────┘
```

### A.2 의존성 매트릭스

| 모듈 (행: 소비자) | I-4 | I-13 | I-14 | I-16 | S-1 | I-2 (RAG) | I-5 (Decision) | I-6 (Executor) | I-25 (SDAR) | Memory |
|-----------------|-----|------|------|------|-----|-----------|----------------|----------------|-------------|--------|
| **I-4** | — | | | | | | | | | |
| **I-13** | | — | | | | | O (render plan) | | | |
| **I-14** | | | — | | | | | | | O (L0→L1) |
| **I-16** | O (embedding) | | | — | | O (RAG pipeline) | | | | O (VectorStore) |
| **S-1** | | | O (QoD ref) | | — | | | O (output collect) | O (trigger) | |

> LOCK (D2.0-02 §7): 의존성 방향은 단방향 소비 (lower layers → higher layers). 역방향 호출 금지.

### A.3 외부 모듈 의존성 상세

| 외부 모듈 | 의존 관계 | 방향 | 인터페이스 | LOCK 여부 |
|----------|----------|------|----------|----------|
| **I-2 RAG Pipeline** | I-16이 I-2를 통해 벡터/BM25 검색 수행 | I-16 → I-2 (소비) | `hybrid_search(query, alpha)` | alpha=0.3(BM25), (1-alpha)=0.7(vector) LOCK |
| **I-5 Decision Engine** | I-5가 I-4 해석 결과 + I-16 검색 결과를 받아 결정 | I-5 ← I-4, I-16 (소비) | 5-score based decision | change_lock=true LOCK |
| **I-6 Executor** | S-1이 I-6 출력을 수집하여 QoD 계산 | S-1 ← I-6 (소비) | output metrics | — |
| **I-8 Policy Engine** | I-16 검색 시 정책 필터 적용 | I-16 → I-8 (소비) | policy filter | change_lock=true LOCK |
| **I-19 Approval Manager** | 특정 작업 시 승인 요청 | 전체 → I-19 (소비) | approval request | change_lock=true LOCK |
| **I-20 OutputComposer** | I-13 렌더링 결과를 조합하여 최종 출력 | I-20 ← I-13 (소비) | `RenderedOutput` | — |
| **I-25 SDAR** | S-1 이상 감지 시 SDAR 트리거 | S-1 → I-25 (소비) | AR-L1~L4 trigger | — |
| **D2.0-06 Memory** | I-14가 메모리 증류, I-16이 VectorStore 검색 | I-14/I-16 → Memory (소비) | 4-layer API + VectorStore adapter | LOCK interface |

### A.4 DAG 검증

위 의존성 그래프는 **DAG(Directed Acyclic Graph)**임을 확인:
- I-4 → I-5 → I-13 → I-20: 단방향
- I-16 → I-2: 단방향
- I-14 → Memory: 단방향
- S-1 → I-25: 단방향
- S-1 ← I-6: 단방향 (S-1이 소비자)
- **순환 경로 없음**: I-14와 I-16이 각각 Memory를 독립적으로 소비하나, I-14 ↔ I-16 간 직접 의존은 없음

---

## 부록 §B — 인터페이스 계약서

### B.1 I-4 Multimodal Interpreter 인터페이스

```python
from abc import ABC, abstractmethod
from typing import Optional, Literal
from pydantic import BaseModel

# --- Input/Output Schema (E3) ---
class RawInput(BaseModel):
    content: bytes | str
    mime_type: str                                           # 자동 감지 가능
    source: Literal["chat", "upload", "clipboard", "mic", "camera"]

class InterpretedInput(BaseModel):
    modality: str                                            # text, image, audio, document
    text_content: Optional[str]                              # 텍스트 변환 결과
    embeddings: Optional[list[float]]                        # 임베딩 벡터
    metadata: dict                                           # 해상도, 길이, 언어 등
    confidence: float                                        # 해석 신뢰도 (0.0~1.0)

# --- ABC Interface (E4) ---
class IMultimodalInterpreter(ABC):
    @abstractmethod
    async def interpret(self, raw_input: RawInput) -> InterpretedInput:
        """입력을 해석하여 정규화된 InterpretedInput 반환"""
        ...

    @abstractmethod
    async def detect_modality(self, raw_input: RawInput) -> str:
        """MIME 타입 기반 모달리티 감지"""
        ...

    @abstractmethod
    def supported_modalities(self) -> list[str]:
        """지원하는 모달리티 목록 반환"""
        ...
```

> LOCK (D2.0-01 §5.6): I-4 Multimodal Interpreter, CORE, V1:ON

**타임아웃 계약**:
| 메서드 | 타임아웃 | 재시도 |
|--------|---------|--------|
| `interpret` (텍스트) | 5s | 2 |
| `interpret` (이미지) | 30s | 2 |
| `interpret` (음성) | 120s | 1 |
| `interpret` (문서) | 60s | 2 |
| `detect_modality` | 1s | 0 |

---

### B.2 I-13 Multimodal Output Renderer 인터페이스

```python
class RenderContent(BaseModel):
    content_type: str                                        # text, chart, code, table, diagram
    data: Any                                                # 렌더링 대상 데이터
    format_hint: Optional[str]                               # 선호 출력 포맷

class RenderedOutput(BaseModel):
    format: str                                              # 실제 출력 포맷
    content: bytes | str                                     # 렌더링 결과
    metadata: dict                                           # 렌더링 시간, 크기 등

class IMultimodalRenderer(ABC):
    @abstractmethod
    async def render(self, content: RenderContent) -> RenderedOutput:
        """단일 콘텐츠를 렌더링"""
        ...

    @abstractmethod
    async def render_composite(self, contents: list[RenderContent]) -> list[RenderedOutput]:
        """복합 콘텐츠를 DAG 기반 병렬 렌더링"""
        ...

    @abstractmethod
    def supported_formats(self) -> list[str]:
        """지원하는 출력 포맷 목록"""
        ...

    @abstractmethod
    def estimate_render_time(self, content: RenderContent) -> float:
        """예상 렌더링 시간(초) 반환"""
        ...
```

> LOCK (D2.0-01 §5.6): I-13 Multimodal Output Renderer, CORE, V1:ON

**타임아웃 계약**:
| 메서드 | 타임아웃 | 재시도 |
|--------|---------|--------|
| `render` (단일) | 10s | 1 |
| `render_composite` | 30s | 1 |
| `estimate_render_time` | 1s | 0 |

---

### B.3 I-14 Summarizer & Memory Distiller 인터페이스

```python
class Message(BaseModel):
    role: str
    content: str
    timestamp: datetime

class Entity(BaseModel):
    name: str
    type: str
    mentions: int

class MemoryCandidate(BaseModel):
    content: str
    source_turns: list[int]
    promotion_reason: str                                    # explicit_request | repeated_reference | decision | context
    priority: float

class SummarizeRequest(BaseModel):
    content: list[Message]
    summary_type: Literal["conversation", "document", "memory_distill"]
    max_length: int                                          # 토큰 단위
    preserve_entities: bool = True

class SummaryResult(BaseModel):
    summary: str
    key_entities: list[Entity]
    key_decisions: list[str]
    memory_candidates: list[MemoryCandidate]
    compression_ratio: float

class ISummarizer(ABC):
    @abstractmethod
    async def summarize(self, request: SummarizeRequest) -> SummaryResult:
        """요약 수행"""
        ...

    @abstractmethod
    async def distill_memory(self, session_messages: list[Message]) -> list[MemoryCandidate]:
        """L0 세션 메모리 → L1 승격 후보 생성"""
        ...

    @abstractmethod
    async def should_trigger(self, session_state: dict) -> bool:
        """자동 트리거 조건 판정"""
        ...
```

> LOCK (D2.0-01 §5.6): I-14 Summarizer & Memory Distiller, CORE, V1:ON

> LOCK (D2.0-06): Memory 4-layer: L0(session) / L1(project) / L2(long-term) / L3(procedural)

**트리거 조건 계약**:
| 트리거 유형 | 조건 | 동작 |
|-----------|------|------|
| 세션 종료 | 세션 end event | L0→L1 증류 |
| 대화 20턴 | `turn_count > 20` | 중간 요약 |
| 컨텍스트 80% | `context_usage > 0.80` | 압축 요약 |
| 사용자 명령 | "요약해줘" 감지 | 즉시 요약 |

---

### B.4 I-16 Knowledge Search Engine 인터페이스

> LOCK (D2.0-01 §5.6): I-16 Knowledge Search Engine — CORE, V1:ON, change_lock=false

```python
class SearchQuery(BaseModel):
    query: str
    sources: list[str] = ["internal", "external"]            # 검색 대상
    top_k: int = 5
    filters: Optional[dict] = None                           # 메타데이터 필터

class Document(BaseModel):
    id: str
    content: str
    source: str
    score: float
    metadata: dict

class SearchResults(BaseModel):
    documents: list[Document]
    total_found: int
    search_time_ms: float
    cache_hit: bool

class IKnowledgeSearchEngine(ABC):
    @abstractmethod
    async def search(self, query: SearchQuery) -> SearchResults:
        """통합 검색 (내부 + 외부)"""
        ...

    @abstractmethod
    async def search_internal(self, query: str, top_k: int = 10) -> list[Document]:
        """I-2 RAG 파이프라인 검색"""
        ...

    @abstractmethod
    async def search_external(self, query: str, sources: list[str]) -> list[Document]:
        """외부 지식 소스 검색"""
        ...

    @abstractmethod
    async def hybrid_search(self, query: str, alpha: float = 0.3) -> list[Document]:
        """벡터 + BM25 하이브리드 검색 (alpha=BM25 비중, 1-alpha=vector 비중)"""
        ...
```

> LOCK (D2.0-06 S7D-012): RAG hybrid search: alpha=0.3(BM25) + (1-alpha)=0.7(vector)

> LOCK (D2.0-06): Embedding: BGE-M3 (1024-dim, Matryoshka 256-dim)

> LOCK (D2.0-06): VectorStore adapter: upsert / search / delete / get_by_id

> LOCK (D2.0-06): Semantic cache: cosine_similarity >= 0.95, TTL 24h

**VectorStore Adapter 인터페이스 (LOCK)**:
```python
class IVectorStoreAdapter(ABC):
    @abstractmethod
    async def upsert(self, id: str, vector: list[float], metadata: dict) -> bool:
        """벡터 삽입/갱신"""
        ...

    @abstractmethod
    async def search(self, vector: list[float], top_k: int = 10,
                     filters: Optional[dict] = None) -> list[Document]:
        """벡터 유사도 검색"""
        ...

    @abstractmethod
    async def delete(self, id: str) -> bool:
        """벡터 삭제"""
        ...

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[Document]:
        """ID로 벡터 조회"""
        ...
```

**Semantic Cache 계약**:
| 항목 | 값 | LOCK |
|------|-----|------|
| 유사도 임계값 | cosine_similarity >= 0.95 | LOCK (D2.0-06) |
| TTL | 24h | LOCK (D2.0-06) |
| 캐시 키 | query embedding (256-dim Matryoshka) | — |
| 무효화 | TTL 만료 또는 VectorStore 변경 이벤트 | — |

---

### B.5 S-1 Self-check Engine 인터페이스

> LOCK (D2.0-01 §5.7): S-1 Self-check Engine — CORE, V1:ON, change_lock=false

```python
class QoDScore(BaseModel):
    relevance: float                                         # 관련성 (0.0~1.0)
    accuracy: float                                          # 정확성 (0.0~1.0)
    freshness: float                                         # 신선도 (0.0~1.0)
    completeness: float                                      # 완전성 (0.0~1.0)
    total: float                                             # 가중 합산 (0.0~1.0)

class HealthStatus(BaseModel):
    qod: QoDScore
    anomaly_level: int                                       # 0(정상)~4(CRITICAL)
    sdar_triggered: bool
    timestamp: datetime

class ISelfCheckEngine(ABC):
    @abstractmethod
    async def evaluate(self, output_metrics: dict) -> QoDScore:
        """I-6 출력 메트릭으로 QoD 점수 계산"""
        ...

    @abstractmethod
    async def check_health(self, window: str = "1h") -> HealthStatus:
        """시스템 상태 평가 (실시간/일간/주간)"""
        ...

    @abstractmethod
    async def should_trigger_sdar(self, qod: QoDScore) -> Optional[str]:
        """SDAR 트리거 필요 여부 판정. 트리거 시 AR 레벨 반환"""
        ...

    @abstractmethod
    def get_thresholds(self, phase: str) -> dict:
        """Phase별 Self-check 임계값 반환"""
        ...
```

> LOCK (D2.0-06 DEC-014): qod = relevance * 0.30 + accuracy * 0.25 + freshness * 0.25 + completeness * 0.20

> LOCK (D2.0-06): QoD < 0.4 → L2/L3 forbidden; QoD >= 0.7 → L2 allowed

> LOCK (D2.0-02 §7): Self-check thresholds: P0>=70, P1>=75, P2>=80

**QoD 계산 계약**:
```python
def calculate_qod(accuracy: float, relevance: float,
                  completeness: float, safety: float, efficiency: float) -> float:
    """
    > LOCK (PLAN-3.0 §11 S11-6, LOCK-AX-03): qod = Accuracy*0.30 + Relevance*0.25 + Completeness*0.20 + Safety*0.15 + Efficiency*0.10 (D2.0-06 DEC-014 4-factor는 SUPERSEDED)
    """
    return accuracy * 0.30 + relevance * 0.25 + completeness * 0.20 + safety * 0.15 + efficiency * 0.10
```

**SDAR 트리거 계약**:
| 조건 | SDAR 레벨 | 설명 |
|------|----------|------|
| QoD < 0.4 연속 3회 | AR-L1 (진단) | 자동 진단 실행 |
| hallucination_rate > 0.2 | AR-L2 (수리) | 프롬프트/캐시 수리 |
| latency p99 > 10s 연속 5분 | AR-L2 (수리) | 모델 라우팅 조정 |
| QoD < 0.2 | AR-L3 (긴급) | 서비스 격리 + 사용자 알림 |
| 보안 이벤트 감지 | AR-L4 (최대) | Emergency Kill Switch |

**Phase별 Self-check 임계값 계약**:
| Phase | 최소 점수 | LOCK |
|-------|----------|------|
| P0 | >= 70 | LOCK (D2.0-02 §7) |
| P1 | >= 75 | LOCK (D2.0-02 §7) |
| P2 | >= 80 | LOCK (D2.0-02 §7) |

> **주의**: self_check_score (5차원: accuracy/latency/hallucination_rate/user_satisfaction/cost_efficiency)는
> S-1 모듈 내부의 시스템 상태 평가 점수로, LOCK QoD 공식(4차원: relevance/accuracy/freshness/completeness)과는
> 별도의 메트릭입니다. QoD는 데이터 품질(D2.0-06), self_check_score는 시스템 건강도(D2.0-02)를 측정합니다.

**Prometheus 메트릭 계약**:
```
vamos_qod_score{window="1h"}                       gauge    # QoD 점수 (0.0~1.0)
vamos_qod_relevance{window="1h"}                   gauge    # 관련성 점수
vamos_qod_accuracy{window="1h"}                    gauge    # 정확성 점수
vamos_qod_freshness{window="1h"}                   gauge    # 신선도 점수
vamos_qod_completeness{window="1h"}                gauge    # 완전성 점수
vamos_hallucination_rate{window="1h"}              gauge    # 환각 비율
vamos_response_latency_seconds{quantile="0.95"}    summary  # 응답 지연 (p95)
vamos_response_latency_seconds{quantile="0.99"}    summary  # 응답 지연 (p99)
vamos_sdar_trigger_total{level="L1|L2|L3|L4"}     counter  # SDAR 트리거 횟수
vamos_selfcheck_evaluation_total                    counter  # Self-check 평가 총 횟수
vamos_selfcheck_anomaly_detected_total{level="1|2|3|4"} counter  # 이상 감지 횟수
```

---

### B.6 공통 ResponseEnvelope 계약

> LOCK (D2.0-02 §7): ResponseEnvelope minimum spec

모든 보조 모듈의 외부 응답은 아래 ResponseEnvelope로 래핑한다:

```python
class ErrorDetail(BaseModel):
    code: str                       # AUX-EXXX
    message: str
    recoverable: bool
    details: Optional[dict] = None

class ResponseEnvelope(BaseModel):
    request_id: str                 # UUID v4
    timestamp: datetime             # UTC ISO 8601
    status: Literal["success", "partial", "error"]
    data: Any                       # 모듈별 응답 (InterpretedInput, RenderedOutput, etc.)
    metadata: dict = {
        "processing_time_ms": float,
        "model_id": Optional[str],
        "token_count": Optional[int],
        "pipeline_stage": str,      # S0~S8
        "module_id": str,           # I-4, I-13, I-14, I-16, S-1
    }
    errors: list[ErrorDetail] = []
    trace_id: Optional[str] = None  # OpenTelemetry trace ID
```

> LOCK (D2.0-02 §5.1.1): ResponseEnvelope 필수 5필드: answer, evidence, self_check, decision_ref, audit

**SOT 필수 5필드 매핑**:
| SOT 필수 필드 | 구현 매핑 위치 | 설명 |
|--------------|--------------|------|
| answer | data.answer | 최종 응답 본문 |
| evidence | data.evidence | 근거 자료 |
| self_check | data.self_check | 자체 검증 결과 |
| decision_ref | data.decision_ref | 의사결정 참조 ID |
| audit | metadata.audit | 감사 추적 정보 |

**사용 규칙**:
1. `status="success"`: data 필드에 정상 응답, errors 비어 있음
2. `status="partial"`: data 필드에 부분 응답, errors에 비치명적 에러 목록
3. `status="error"`: data=None, errors에 에러 목록
4. `pipeline_stage`: 현재 state machine 위치 (S0~S8), D2.0-02 §7 LOCK

---

> **문서 종료**
> 본 계획서는 sot 2/1-2_Auxiliary-Modules/의 구조화 전략, 거버넌스, 실행 계획을 정의하는 최상위 문서이다.
> 모든 서브폴더 파일은 본 계획서의 규칙과 LOCK 선언을 준수해야 한다.
