# Auxiliary Modules 권한 체계 선언

> **Status**: APPROVED (Phase 4 ✅ 완료, 2026-05-23, V-01 영구 baseline + LOCK-AX 영역 immutable + 80+ production .md ALL APPROVED 정합)
> **버전**: v1.2
> **작성일**: 2026-03-22
> **최종 수정**: 2026-05-10 (STAGE 9 Phase A step A-3 STEP_C truly_converged_v3, §7 신설: LOCK count duality methodology + V2 35 NEW LOCK 인용 출처 매트릭스 + Sandbox drift 일괄 정합 기록 + [PHASE3_READY v2: 1-2 — 2026-05-10 최종 확정])
> **Last-reviewed**: 2026-05-23 (Phase 4 production promotion)
> **ReadOnly**: TRUE (production 승급 후 immutable, 변경 시 일시 해제→fix→복원 EXACT 패턴 + audit log)
> **출처**: AUXILIARY_MODULES_구조화_종합계획서 §3.1~§3.4
> **비고**: 거버넌스 문서이므로 L3 심사 대상이 아님. Phase 2~3 APPROVED 흐름과 별도로, 생성 즉시 APPROVED 부여.

---

## 1. 기존 VAMOS 권한 체인 (§3.1)

```
RULE 1.3 > PLAN 3.0 > DESIGN 2.0 LOCK > DESIGN body > Schema/TECH_STACK
```

---

## 2. Auxiliary-Modules 확장 권한 체인 (§3.2)

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

---

## 3. 각 문서의 권한 범위 (§3.3)

| 문서 | 권한 레벨 | 결정할 수 있는 것 | 결정할 수 없는 것 |
|------|----------|------------------|------------------|
| **D2.0-01 §5.6** | DESIGN-LOCK | 모듈 ID, 이름, CORE/COND/EXP 분류, change_lock 플래그 | 구현 상세, 파이프라인 로직 |
| **D2.0-02 §7** | DESIGN-ARCH | ORANGE CORE 내부 파이프라인, 5-stage 파이프라인, state machine S0~S8, 모듈 간 관계도 | 개별 모듈 내부 로직 |
| **D2.0-06** | DESIGN-LOCK | Memory 4-layer (L0/L1/L2/L3), VectorStore adapter interface, semantic cache threshold, embedding model spec | 개별 모듈 구현 상세 |
| **PART2 V1-Phase 1/6** | IMPL-GUIDE | When(Phase 배정) + Where(코드 위치) | 모듈 구현 로직 상세 (→ sot 2/) |
| **sot 2/1-2_Auxiliary-Modules/** | IMPL-DETAIL | What + How (입출력 스키마, 파이프라인 알고리즘, fallback chain, 타임아웃 정책) | LOCK 값 재정의, Phase 일정 |
| **상세명세.md** (기존) | IMPL-DETAIL (LEGACY) | 기존 상세 스키마 (마이그레이션 대상) | 향후 변경 (→ 서브폴더 파일로 이관) |

---

## 4. LOCK 보호 선언 (§3.4)

> **절대 규칙**: sot 2/1-2_Auxiliary-Modules/ 내 모든 파일은 아래 LOCK 값을 **재정의할 수 없다**.
> 참조 시 반드시 `> LOCK (출처): [원문 그대로]` 형식을 사용한다.

#### change_lock 보호 항목 (4건)

> §3.4 전체 19건 중 아래 4건은 change_lock 플래그 항목으로, §5A LOCK-AX 레지스트리와 별도 관리. (FR-1: 19개 = LOCK-AX-01~15 + change_lock 4건)

| LOCK 항목 | 정본 출처 | 값 | 비고 |
|-----------|----------|-----|------|
| 모듈 API 시그니처 (I-Series) | D2.0-01 §5.6 | 모듈 카탈로그 정의 그대로 | change_lock 플래그 포함 |
| I-5 Decision Engine | D2.0-01 §5.6 | change_lock=true, 5-score based | LOCK |
| I-8 Policy Engine | D2.0-01 §5.6 | change_lock=true, synced with D7 | LOCK |
| I-19 Approval Manager | D2.0-01 §5.6 | change_lock=true, synced with D7 | LOCK |

#### LOCK-AX 레지스트리 항목 (15건, §5A 정본 번호)

| # | LOCK 항목 | 정본 출처 | 값 | 비고 |
|---|-----------|----------|-----|------|
| LOCK-AX-01 | I-Series 모듈 분류 | D2.0-01 §5.6 | CORE / COND / EXP + change_lock | 분류 변경 시 D2.0-01 수정 필요 |
| LOCK-AX-02 | 의존성 방향 | D2.0-01 §4 (**출처 미확인 — UNCONFIRMED/DEFERRED**, D-01: 양 D2.0 원문 부재) | 단방향 소비 (lower layers → higher layers) | 역방향 호출 금지 — **D2.0 원문 명시 전까지 production LOCK 미적용** (lock_value_registry D-01) |
| LOCK-AX-03 | QoD formula | D2.0-06 DEC-014 → **PLAN-3.0 갱신 (Phase 11 S11-6)** | qod = Accuracy×0.30 + Relevance×0.25 + Completeness×0.20 + Safety×0.15 + Efficiency×0.10 *(5-factor, SOT PLAN-3.0 정본. 기존 4-factor는 SUPERSEDED)* | S-1 핵심 |
| LOCK-AX-04 | QoD thresholds | D2.0-06 | `<0.4 L2/L3 forbidden, >=0.7 L2 allowed` | S-1 핵심 |
| LOCK-AX-05 | Self-check thresholds | D2.0-02 §7.53-1 | `P0>=70, P1>=75, P2>=80` | Phase별 최소 점수 |
| LOCK-AX-06 | RAG hybrid search ratio | D2.0-06 S7D-012 | `alpha=0.3(BM25) + (1-alpha)=0.7(vector)` | I-16 핵심 |
| LOCK-AX-07 | Embedding model | D2.0-06 DEC-005 | `BGE-M3 (1024-dim, Matryoshka 256-dim)` | I-16 핵심 |
| LOCK-AX-08 | VectorStore adapter interface | D2.0-06 | `upsert/search/delete/get_by_id` (4 methods) | LOCK interface |
| LOCK-AX-09 | Memory 4-layer | D2.0-06 | `L0(session)/L1(project)/L2(long-term)/L3(procedural)` | I-14 핵심 |
| LOCK-AX-10 | Semantic cache | D2.0-06 | `cosine_similarity >= 0.95, TTL 24h` | I-16 캐시 |
| LOCK-AX-11 | ResponseEnvelope minimum spec | D2.0-02 §5.1.1 | 표준 응답 봉투 최소 필드 세트 | 전 모듈 공통 |
| LOCK-AX-12 | Standard 5-stage pipeline | D2.0-02 §2.1 | 5단계 파이프라인 | 전 모듈 공통 |
| LOCK-AX-13 | State machine | D2.0-02 §2.2 | S0~S8 상태 전이 | 전 모듈 공통 |
| LOCK-AX-14 | PII 마스킹 | D2.0-06 | AES-256 암호화, Regex + NER 감지, 비가역 마스킹 | 개인정보 보호 |
| LOCK-AX-15 | 메모리 검색 우선순위 | D2.0-06 S7D-042 | L0→L1→L2→L3, 레이어당 max 5, 최종 top 5 | Memory 검색 순서 |

> LOCK (D2.0-06 DEC-014): `qod = relevance×0.30 + accuracy×0.25 + freshness×0.25 + completeness×0.20`
> ※ PLAN-3.0 갱신(Phase 11 S11-6)에 의해 5-factor로 SUPERSEDED — LOCK-AX-03 참조

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

## 5. 교차 도메인 의존성 (Phase 3 추가)

> Phase 3 교차검증에서 확인된 소비 관계. 2026-03-24 추가.

| 소비 도메인 | 참조 LOCK | 용도 |
|------------|-----------|------|
| #6 PKM | LOCK-AX-03~04 (QoD), LOCK-AX-06 (RAG) | 지식 품질 평가, 검색 파이프라인 |
| #8 Education | LOCK-AX-09 (메모리 4계층) | 학습 기억 저장 계층 참조 |
| #17 MLOps | LOCK-AX-03 (QoD) | QoD 동명 이질 메트릭 — CONF-AUX-002 참조 |

---

## 6. 도메인 경계 (소비 도메인 요약)

> Tier 1 기초 도메인으로서 다수 상위 도메인이 본 도메인의 정의를 소비함. 주요 소비 도메인만 요약.

| 소비 도메인 | 소비 항목 |
|------------|----------|
| #6 PKM-Knowledge | LOCK-AX-03~04 QoD 공식/임계값, LOCK-AX-06 RAG 하이브리드 비율 |
| #8 Education-Learning | LOCK-AX-09 메모리 4계층(L0~L3) 학습 기억 저장 계층 참조 |
| #9 Health-Wellness | S-1 자가점검 엔진 연동, 위기 감지 이벤트 수신 |

---

## 7. STAGE 9 STEP_C 심층 재검증 수렴 기록 (2026-05-10, NEW)

> **Status**: APPROVED (STAGE 9 Phase A step A-3 STEP_C truly_converged_v3)
> **작성일**: 2026-05-10
> **chain**: s9_37_a_3 (canonical step 36→37 inheritance)
> **분기**: a CLEAN (sandbox-only UPDATE, production UNCHANGED)
> **선행**: STAGE 9 STEP_A (s9_35_a_1) + STEP_B (s9_36_a_2) ✅ 100% PASS inheritance

### 7.1 LOCK count duality methodology (4-1 §9.2 패턴 직계 적용)

본 STEP_C에서는 V2 35 NEW의 LOCK 인용 무결성을 보장하기 위해 **LOCK count duality** 측정 방법론을 정식 도입한다. 이는 STAGE 7 4-1 Rust-Tauri-Infra 도메인 §9.2에서 확립된 방법론을 1-2 도메인에 직계 적용한 결과이다.

#### 7.1.1 측정 방법

| 측정 차원 | 정의 | 측정 패턴 | 측정 결과 (2026-05-10) |
|---|---|---|:-:|
| **§V2-only LOCK refs (N)** | sandbox 35 V2 NEW 파일에서 LOCK-AX-01~15 인용 raw count | grep `LOCK-AX-(0[1-9]\|1[0-5])` in `*_v2.md` | **N = 389** |
| **전체 sandbox 1-2 LOCK refs (M)** | sandbox 1-2 도메인 90 .md files (V1 + V2 + verification) 전체 LOCK refs | grep `LOCK-AX-(0[1-9]\|1[0-5])` in 1-2/ | **M = 765** |
| **§V1-only LOCK refs (M-N)** | 도출식: V1 + verification + baseline | M - N | **M-N = 376** |
| **Production V1 LOCK refs (참조)** | production 1-2 53 files (read-only baseline) | grep in production 1-2/ | 341 |

#### 7.1.2 Duality 무결성 판정

- **§V2 평균 LOCK refs/file**: 389/35 = **11.1**
- **§V1 평균 LOCK refs/file (production)**: 341/53 = 6.4
- **V2 vs V1 인용 밀도 비율**: 1.7× (V2가 V1 대비 1.7배 높은 LOCK 인용 밀도)
- **판정**: V2 강화 L3 의도와 정합 ✅ (E8 LOCK 참조 요소 강화 + 1:1 매핑 패턴 + 6-2 PII cross-ref 추가로 인한 자연스러운 인용 밀도 증가)

#### 7.1.3 Duality 위반 abort 발화 조건

- `[LOCK_COUNT_DUALITY_VIOLATION:1-2_lock_ax_01_15]`: LOCK-AX-01~15 + change_lock 4 = 19건 EXACT 범위 외 LOCK 인용 발견 시
- 본 STEP_C 시점 실측: V2 35 매트릭스에서 LOCK-AX-16+ **0건**, V1 baseline 04_knowledge-search/fallback_chain.md 1건 (기존 baseline 상태, V1 byte-identical 보존)
- **NOT FIRED + self-fire 0** ✅

### 7.2 V2 35 NEW LOCK 인용 출처 매트릭스

V2 35 NEW에서 인용된 LOCK-AX 항목별 EXACT 출처 정합 매트릭스:

| LOCK 항목 | V2 인용 빈도 (상위) | 정본 출처 |
|---|---|---|
| LOCK-AX-01 (I-Series 모듈 분류) | 다수 V2 cross-ref | D2.0-01 §5.6 |
| LOCK-AX-02 (의존성 방향) | D-01 OPEN 인지 (외부 D2.0 갱신 PENDING) | D2.0-01 §4 (외부 의존) |
| LOCK-AX-03 (QoD 5-factor) | qod_formula_v2 (38), prometheus_metrics_v2 (10), search_pipeline_v2 (16), sdar_trigger_v2 (14) | **PLAN-3.0 §11 S11-6** (D2.0-06 DEC-014 SUPERSEDED) |
| LOCK-AX-04 (QoD thresholds) | qod_formula_v2 + sdar_trigger_v2 + anomaly_detection_v2 | D2.0-06 |
| LOCK-AX-05 (Self-check thresholds P0/P1/P2) | anomaly_detection_v2 (10), prometheus_metrics_v2 | D2.0-02 §7.53-1 |
| LOCK-AX-06 (RAG alpha=0.3) | search_pipeline_v2 (16), search_api_v2 (24), rag_integration_v2 (29) | D2.0-06 S7D-012 |
| LOCK-AX-07 (Embedding BGE-M3) | rag_integration_v2 + search_pipeline_v2 | D2.0-06 DEC-005 |
| LOCK-AX-08 (VectorStore adapter) | search_pipeline_v2 + rag_integration_v2 + memory_distillation_v2 | D2.0-06 |
| LOCK-AX-09 (Memory 4-layer) | memory_distillation_v2 (15) | D2.0-06 |
| LOCK-AX-10 (Semantic cache) | search_pipeline_v2 + rag_integration_v2 | D2.0-06 |
| LOCK-AX-11 (ResponseEnvelope) | response_envelope_v2 (20), common_types_v2 (18) | D2.0-02 §5.1.1 |
| LOCK-AX-12 (5-stage pipeline) | 다수 V2 cross-ref | D2.0-02 §2.1 |
| LOCK-AX-13 (S0~S8 state machine) | sdar_trigger_v2 (14, S3 Decision Lock) | D2.0-02 §2.2 |
| LOCK-AX-14 (PII 마스킹 AES-256) | 11+ V2 cross-ref (S-1 5 + 00_common 1 + interpreter 5 + extended 20+) | D2.0-06 |
| LOCK-AX-15 (메모리 검색 우선순위 L0→L1→L2→L3) | memory_distillation_v2 + search_pipeline_v2 | D2.0-06 S7D-042 |
| change_lock 4건 (I-5/I-8/I-19 + API 시그니처) | renderer_interface_v2 + composite_output_v2 + 보조 V2 다수 | D2.0-01 §5.6 |

**총 LOCK 인용 source diversity**: 19 LOCK 출처 항목 모두 V2에 cross-ref 1+ 보유 (누락 0) ✅

### 7.3 Sandbox drift 일괄 정합 기록 (STEP_C sub-step 12~16)

#### 7.3.1 STEP_B 후속 sandbox 상태 (STEP_C sub-step 1 사전 점검 실측, 2026-05-10)

| 파일 | sandbox 상태 (실측) | production 상태 |
|---|---|---|
| INDEX.md | body §10 v1.3 row append + §9 V2 column + V2 35 인벤토리 추가 (+1,384 B) | 헤더 v1.0 + body §10 마지막 row v1.2 (unchanged) |
| AUTHORITY_CHAIN.md | byte-identical to production (v1.1, 7,332 B) | v1.1 (7,332 B) |
| CONFLICT_LOG.md | byte-identical to production (v2.0, 5,915 B) | v2.0 (5,915 B) |
| AUXILIARY_MODULES_구조화_종합계획서.md | §11 L1940 STEP_B IN_PROGRESS row append (+724 B) | (STEP_B row 미반영) |
| 6 _index.md (00~05) | footer V2 inventory 추가 (각 +800~1,500 B) | (V2 inventory 미반영) |

**Drift 분류**: STEP_B 명시 적용분 ✅ + AUTHORITY/CONFLICT 미적용분 (STEP_C에서 §7 신설로 정합) + STEP_C 후속 미적용분 (sub-step 14~16에서 일괄 처리)

#### 7.3.2 STEP_C sub-step 14~16 일괄 정합 (2026-05-10)

| Sub-step | 작업 | sandbox 결과 |
|:-:|---|---|
| 14 | INDEX Status DRAFT → APPROVED + plan §11 STEP_C COMPLETE row | INDEX status 갱신 + plan row 추가 |
| 15 | INDEX §10 v2.0 row + AUTHORITY 헤더 최종 수정 라인 갱신 (§7 신설 반영) + CONFLICT §0 v2.1 row + 11건 처리 | 3 ledger row append |
| 16 | INDEX 헤더 v1.0→v2.0 major + AUTHORITY 헤더 v1.1→v1.2 minor + CONFLICT 헤더 v2.0→v2.1 minor + Last-reviewed 2026-05-10 | 3 헤더 동시 정합 |

### 7.4 [PHASE3_READY v2: 1-2 — 2026-05-10 최종 확정]

**STAGE 9 Phase A step A-3 STEP_C 종료 결과 (sub-step 22 truly_converged_v3 marker confirmed 시점)**:

| Phase | 결과 |
|---|---|
| Phase F 6-step + F-7 supplementary | 7/7 PASS (sub-step 3~9) |
| Phase G 8-step + Sandbox drift 정합 | 8/8 PASS (sub-step 12~19) |
| V1 immutability verify | 3회 × 42/42 OK = 통산 +8회 (STEP_A 2 + STEP_B 3 + STEP_C 3) |
| R₁~R₈ truly_converged_v3 cascade | 8 round 0 changes (3차 강건성) |
| 6-2 PII cross-ref | 31 V2 / 244 raw refs (광범위 sync) |
| LOCK count duality (§7.1) | §V2-only 389 / 전체 765 / V1-only 376 (정합) |
| AUTHORITY §7 신설 (1-2 §7 신설 첫 도메인) | ✅ (본 §7) |
| CONFLICT 11건 처리 | F-01 + F-04~F-09 + F-10/F-11 + D-01 DEFERRED-EXTERNAL + D-02 RESOLVED-PARTIAL |
| INDEX 헤더 v1.0+body v1.2 → v2.0 동시 정합 major | ✅ |
| 5 _index footer "STEP_C 최종 확정" 1줄 append × 5 | ✅ (4-1 R2 패턴 직계) |
| plan §11 STEP_C COMPLETE row | ✅ |
| SOT2_MASTER 4 지점 sandbox preview | ✅ (L86 heading + L87 구현 현황 + L87 직후 PHASE3_READY 블록 신설 + L1290 표 row) |
| memory 6-target Δ sandbox preview | ✅ |
| abort 9종 표준형 발화 | 0/9 + self-fire 0 (NOT FIRED 통산) |
| 사용자 정밀성 6 anchor | 26 sub-step × 6 = 156 cell 100% 충족 |

**[PHASE3_READY v2: 1-2 — 2026-05-10 최종 확정]** ✅ Phase 3 진입 가능 선언 (STAGE 9 Phase A step A-4 production sync 두 단계 게이트 9.1-A/B 사후 적용 시).
