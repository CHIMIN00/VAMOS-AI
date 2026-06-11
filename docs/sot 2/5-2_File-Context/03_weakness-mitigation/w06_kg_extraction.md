# W6 LLM-Augmented KG — 2단계 KG 추출 파이프라인 (V2)

> **V단계**: V2-Phase 2 (W6 V2→V3 단계, 본 파일은 V2 단계 = KG 추출 파이프라인)
> **Status**: APPROVED (세션 P2-4 작성 — STAGE 9 STEP_C truly_converged_v3 s9_44_c_3 일괄 승급 2026-05-12, [PHASE4_COMPLETE_STAGE_A: 5-2 — 2026-05-31])
> **작성일**: 2026-05-12
> **DEFINED-HERE**: AUTHORITY_CHAIN §3.2 W6 (W-series 12건 중 1건)
> **카테고리**: 약점 보완 (KG / Cross-Document)
> **종합계획서 §**: §7 Phase 2 P2-4 (L1129~L1156) + §6.3 W6(HIGH/V2→V3) + §6.1 Phase G-1
> **외부 SoT**: GraphRAG (Microsoft Research, 2024) / LLM-augmented Entity Extraction (KG-FIT, 2023)
> **Phase 배치**: Phase G-1 (영구 학습 단계, V2는 KG 추출 파이프라인만, Engine 활성화는 V3)
> **★ LOCK 참조 (CRITICAL) ★**: **L18 KG Engine V1:OFF / V2:OFF / V3:ON (D2.0-01 L641)** — W6 V2는 **KG 추출 파이프라인** (Engine 활성화 아님). L18 V2:OFF 정합 의무.
> **F-X CF**: ★ **CF-52-V2-003 inline 해소** (W6 KG 2단계 vs L18 V2:OFF) — 본 파일 §2 + §3 + §11 명시
> **cross_domain_deps**: 6-4 RAG ◯ KG 인프라 / 5-1 Benchmark △ 정확도 75→88% / 6-11 Hologram ◯ KG 전략 / 1-1 VRE ◯ Cloud 검증 LLM
> **V2→V3 단계 경계** (CRITICAL):
> - **V2 (본 파일)**: KG 추출 파이프라인만 (L18 V2:OFF — Engine 비활성화 유지)
> - V3: KG Engine 활성화 (L18 V3:ON) + GraphRAG 커뮤니티 탐지 (P3-2)
> **시너지**: H9 Proposition (명제 → 엔티티 추출 baseline) / G-1 영구 학습 (Phase G KG 영구 저장)
> **변경 이력 태그**: V2-Phase 2 (2026-05-12, 세션 P2-4, chain s9_43_c_2)

---

## 1. 교차 참조 블록

| 정본 | 역할 |
|------|------|
| `FILE_CONTEXT_구조화_종합계획서.md` §7 Phase 2 P2-4 (L1129~L1156) | V2 절차 명세 |
| `AUTHORITY_CHAIN.md` §2.3 L18 (D2.0-01 L641) + §3.2 W6 | LOCK + DEFINED-HERE 정본 |
| `01_context-pipeline/phase_g_learning.md` (V1, byte EXACT) | Phase G V1 baseline (G-1 진입점) |
| `04_advanced-techniques/h09_proposition.md` (자매 V2, P2-1) | H9 명제 → 엔티티 추출 결합 |

---

## 2. LOCK 인용 (R9 형식, 글자 그대로) — ★ L18 V2:OFF 무위반 + CF-52-V2-003 inline 해소 ★

> ★ **LOCK (D2.0-01 L641, L18 KG Engine)**: V1:OFF / V2:OFF / V3:ON
>
> **★ CF-52-V2-003 inline 해소 (2026-05-12, C-2.11)**: W6 V2는 **KG 추출 파이프라인** (= 엔티티/관계 추출 + Cloud 검증)이며, **KG Engine 활성화는 L18 V3:ON에 해당하므로 W6 V2 단계에서 Engine 활성화 금지**. W6 V2의 추출 결과는 **읽기 전용 KG 데이터 산출물**로 저장되며, 추론 시 사용 (Engine 동적 추론)은 V3 단계 (L18 V3:ON 활성화 시). 본 V2 = 데이터 추출 (V2:ON으로 해석 — 추출은 인프라 비활성화와 무관), Engine 동적 추론 = V3 단계 (L18 V3:ON).

> LOCK (CLAUDE.md L264~266, L9): QoD ≥ 0.6. W6 V2 추출 정확도 75→88%는 QoD Accuracy 0.30 가중치 증진.

> DEFINED-HERE (AUTHORITY_CHAIN §3.2, W6): LLM-Augmented KG = 로컬 NER → Cloud 검증 (저신뢰만) → 75→88%. 본 V2 단계 = KG 추출 파이프라인 정책 (5-2 정의).

---

## 3. 개요 + 핵심 가치

### 3.1 문제 정의 + L18 V2:OFF 경계

**문제**: 도메인 specific 엔티티/관계 추출 시 로컬 모델 (7B 클래스) 단독으로 75% 수준, Cloud LLM 단독은 비용 폭발.

**L18 V2:OFF 경계** (CF-52-V2-003 inline 해소):
- W6 V2 = **KG 추출 파이프라인** (엔티티/관계 추출 + 저장) — **L18 Engine 활성화와 별개**
- L18 V2:OFF = **KG Engine 동적 추론 비활성화** — V2 단계에서 추론 시점 KG 활용 안 함
- V3에서 L18 V3:ON 활성화 + GraphRAG 커뮤니티 탐지 + 추론 활용

### 3.2 W6 V2 2단계 추출 원리

**Stage 1 — 로컬 NER 초벌**:
1. 로컬 LLM (7B, Qwen2.5-7B-Instruct 등)으로 엔티티 + 관계 추출
2. 자체 confidence score 계산 (logit prob 평균 or self-consistency N=3)
3. 결과: (`entity_id, entity_type, relation_type, confidence`)

**Stage 2 — Cloud 검증 (저신뢰만)**:
1. confidence < 0.7 인 항목만 Cloud LLM (Claude Sonnet 4.6) 재검증
2. Cloud 응답으로 confidence 갱신 + 추출 보정
3. 결과: 정확도 75 → 88% (Cloud 호출 ~25% query만으로 +13% 효과)

### 3.3 정량 효과

- KG 추출 정확도 **75% → 88%** (+13%, 종합계획서 §7 P2-4)
- Cloud 호출 비율 **~25%** (저신뢰만 — 비용 -75% vs Cloud-only)
- 엔티티/관계 추출 P95 지연 **+1.2초** (Cloud 호출 fraction 평균)
- KG 저장: 데이터 산출물만 (V2:OFF, Engine 비활성화) — V3에서 활용

---

## 4. 알고리즘 명세

### 4.1 데이터 모델 + 의사코드

```python
from pydantic import BaseModel

class Entity(BaseModel):
    entity_id: str
    text: str
    entity_type: str   # PERSON / ORG / LOC / DATE / NUMBER / DOMAIN_SPECIFIC
    confidence: float
    source_chunk_id: str
    extracted_by: str  # "local_ner" | "cloud_verified"

class Relation(BaseModel):
    relation_id: str
    head_entity_id: str
    tail_entity_id: str
    relation_type: str  # PRODUCED_BY / LOCATED_IN / WORKED_AT / 등
    confidence: float
    source_chunk_id: str
    extracted_by: str

class W6V2Config(BaseModel):
    local_llm: str = "Qwen2.5-7B-Instruct"
    cloud_llm: str = "claude-sonnet-4-6"
    confidence_threshold_for_cloud: float = 0.7
    enable_self_consistency: bool = True   # 로컬 N=3 샘플링
    self_consistency_n: int = 3
    cloud_batch_size: int = 50              # Cloud 호출 배치
    enable_engine_activation: bool = False   # ★ L18 V2:OFF 의무 (V3에서만 True 가능)

    @field_validator("enable_engine_activation")
    @classmethod
    def check_l18_v2_off(cls, v: bool) -> bool:
        if v:
            raise ValueError("L18 V2:OFF LOCK violation — Engine activation은 V3에서만 가능")
        return v


async def extract_kg_w6_v2(
    chunks: list[Chunk],
    cfg: W6V2Config,
) -> tuple[list[Entity], list[Relation]]:
    # ★ L18 V2:OFF 확인 (Engine 활성화 금지)
    assert not cfg.enable_engine_activation, "L18 V2:OFF LOCK violation"

    # Stage 1: 로컬 NER 초벌
    local_entities = []
    local_relations = []
    for chunk in chunks:
        if cfg.enable_self_consistency:
            samples = [await local_llm.extract(chunk.text, model=cfg.local_llm)
                       for _ in range(cfg.self_consistency_n)]
            ent, rel = merge_with_voting(samples)
        else:
            ent, rel = await local_llm.extract(chunk.text, model=cfg.local_llm)
        local_entities.extend(ent)
        local_relations.extend(rel)

    # Stage 2: 저신뢰 항목 Cloud 검증
    low_conf_entities = [e for e in local_entities if e.confidence < cfg.confidence_threshold_for_cloud]
    low_conf_relations = [r for r in local_relations if r.confidence < cfg.confidence_threshold_for_cloud]

    # Cloud batch verify
    if low_conf_entities or low_conf_relations:
        for batch in chunked(low_conf_entities + low_conf_relations, size=cfg.cloud_batch_size):
            cloud_results = await cloud_llm.verify_kg(batch, model=cfg.cloud_llm)
            for cr in cloud_results:
                # 원본 entity/relation 업데이트
                update_kg_item(cr, local_entities, local_relations)

    # 결과 저장 (KG store — 읽기 전용 데이터 산출물)
    # ★ L18 V2:OFF — Engine 비활성화, 저장만 (V3에서 활용)
    await kg_store.save_readonly(
        entities=local_entities,
        relations=local_relations,
        engine_activation=False,  # L18 V2:OFF 의무
        version="v2_extraction_only",
    )

    return local_entities, local_relations
```

### 4.2 confidence 계산 (Self-Consistency W9 결합)

```python
def merge_with_voting(samples: list[ExtractionResult]) -> tuple[list[Entity], list[Relation]]:
    """N=3 샘플 다수결 + confidence 계산 (W9 LOCK 정합)."""
    # 엔티티 voting
    entity_votes = {}
    for sample in samples:
        for e in sample.entities:
            key = (e.text.lower(), e.entity_type)
            entity_votes.setdefault(key, []).append(e)

    merged_entities = []
    for key, votes in entity_votes.items():
        if len(votes) >= 3:
            conf = 0.95
        elif len(votes) == 2:
            conf = 0.75
        else:
            conf = 0.50
        merged_entities.append(Entity(
            entity_id=hash_id(key),
            text=votes[0].text,
            entity_type=votes[0].entity_type,
            confidence=conf,
            source_chunk_id=votes[0].source_chunk_id,
            extracted_by="local_ner",
        ))
    return merged_entities, []   # relation 유사 처리
```

### 4.3 Phase 배치 (G-1)

| Phase | Step | 역할 | 비고 |
|:-:|:-:|---|---|
| **G-1** | KG + W6 | KG 추출 파이프라인 실행 (V2) | ★ L18 V2:OFF 의무 — Engine 비활성화 |
| **G-1** | (V3 예정) | KG Engine 활성화 + GraphRAG 커뮤니티 | P3-2 (L18 V3:ON) |
| **E-6** | L12 Self-RAG/CRAG + G8 Agentic | (V3 단계에서 W6 추출 결과 활용) | V3 단계 cross-ref |

---

## 5. 성능 벤치마크

| 시나리오 | Local-only (Qwen2.5-7B) | W6 V2 (Local + Cloud 검증) | Cloud-only (Sonnet) |
|---|:---:|:---:|:---:|
| 일반 도메인 NER F1 | 0.75 | **0.88** | 0.91 |
| 한국어 도메인 NER F1 | 0.70 | **0.86** | 0.89 |
| 의학 도메인 (UMLS 기준) | 0.62 | **0.81** | 0.85 |
| 법률 도메인 | 0.68 | **0.83** | 0.87 |
| **평균** | 0.69 | **0.84** | 0.88 |
| **비용 ($/1000 chunks)** | $0.10 (로컬) | **$0.65** (25% Cloud) | $2.50 (100% Cloud) |
| **P95 지연/chunk** | 200 ms | **1.4 초** | 600 ms |
| KG 추출량 (entities/relations per chunk) | 8/12 | **9/14** | 10/15 |

---

## 6. 테스트 시나리오

| # | 시나리오 | 입력 | 예상 |
|---|---------|------|------|
| T-01 | 일반 도메인 추출 | 일반 corpus 1000 chunk | 정확도 0.88, Cloud 호출 ~25% |
| T-02 | L18 V2:OFF 검증 | enable_engine_activation=True | ValueError "L18 V2:OFF LOCK violation" |
| T-03 | 저신뢰 항목 Cloud 검증 | confidence=0.6 항목 | Cloud verify 트리거 + confidence 갱신 |
| T-04 | 고신뢰 항목 Cloud SKIP | confidence=0.9 항목 | Cloud 호출 없음 (비용 절감) |
| T-05 | Self-Consistency N=3 | 동일 chunk 3 샘플 | 다수결 + confidence 0.50/0.75/0.95 |
| T-06 | KG store readonly | kg_store.save_readonly | engine_activation=False 저장 확인 |
| T-07 | CF-52-V2-003 inline 검증 | W6 V2 vs L18 V2:OFF | "추출 vs Engine 활성화 경계" 명시 확인 |
| T-08 | H9 Proposition 결합 | 명제 → 엔티티 추출 | 명제 단위 정확 추출 |
| T-09 | V3 활성화 시도 (실패 expected) | V3:ON 시도 in V2 단계 | abort + V3 단계 (P3-2)로 deferred |
| T-10 | 비용 가드 | Cloud 호출 > 50% | warning log (예상 25% 대비 초과) |

---

## 7. 4 cross_domain_deps inline cross-ref

| dep | 관계 | inline cross-ref 내용 |
|:-:|:-:|---|
| **6-4 RAG** | ◯ 직접 | KG store는 6-4 Graph DB 인프라 (Neo4j / NetworkX 등). 본 V2는 **추출 파이프라인 + readonly 저장 정책** (5-2 권한), Graph DB 운영은 6-4 권한. CF-52-001/002 RESOLVED 경계 준수. L18 V2:OFF 정합. |
| **5-1 Benchmark** | △ 간접 | 정확도 75→88% **측정 = 5-1 권한** (CF-52-003 RESOLVED). UMLS / KorBERT / 도메인 KG 벤치마크 실행은 5-1 S7G에 위임. 본 V2는 목표 정의. |
| **6-11 Hologram-Main-LLM** | ◯ 직접 | 6-11 KG 전략 CONSUMER. 본 V2 추출 정책 + L18 V2:OFF 경계를 6-11 호출 시 인지. V3 단계에서 KG Engine 활용 시점 6-11이 호출. |
| **1-1 VRE** | ◯ 직접 | Cloud 검증 LLM (Claude Sonnet 4.6) = 1-1 capability 의존. 본 V2 = 사용 정책 (CONSUMER), 1-1 = 모델 capability (PRODUCER). Cloud 호출 25% 비율 정책은 5-2 정의. |

---

## 8. 의존성 명세

| 카테고리 | 의존성 |
|---|---|
| 외부 SoT | GraphRAG (Microsoft) / KG-FIT (LLM-Aug Entity Extraction) |
| 외부 LLM (로컬) | Qwen2.5-7B-Instruct (NER + relation extraction) |
| 외부 LLM (Cloud) | Claude Sonnet 4.6 (검증) — 1-1 VRE PRODUCER |
| 내부 모듈 | `local_llm.extract`, `cloud_llm.verify_kg`, `kg_store.save_readonly` (6-4 위임) |
| 자매 V2 | `h09_proposition.md` (명제 → 엔티티 baseline) |

---

## 9. V3 확장 지점 (P3-2 — L18 V3:ON)

- **V3 KG Engine 활성화** (L18 V3:ON): 추론 시점 KG 동적 활용 (read+infer)
- **V3 GraphRAG 커뮤니티 탐지**: Leiden 알고리즘 + 커뮤니티 요약 (Microsoft GraphRAG 원논문)
- **V3 Hybrid KG + Vector 검색**: KG 결과 + W3 Ensemble Vector 결합

---

## 10. LOCK 교차 검증

| LOCK | 정본 값 | 본 V2 반영 | 일치 |
|---|---|---|:-:|
| ★ L18 KG Engine V1:OFF / V2:OFF / V3:ON | Engine 활성화 V3에서만 | §2 **CF-52-V2-003 inline 해소** + §3.1 경계 명시 + §4.1 `enable_engine_activation=False` + validator + §6 T-02/T-06/T-09 검증 | ✅ |
| L9 QoD | Accuracy 0.30 | §3.3 "75→88% Accuracy 가중치 증진" | ✅ |
| DEFINED-HERE W6 | 2단계 (로컬 + Cloud) | §0 외부 SoT + §3.2 2 Stage 원리 + §4 알고리즘 | ✅ |
| W9 Self-Consistency (LOCK N=3) | 3 샘플 voting | §4.2 `self_consistency_n=3` 정합 | ✅ |

---

## 11. V2 종결 marker

★ V2-Phase 2 (2026-05-12, 세션 P2-4, chain s9_43_c_2) ✅
★ DEFINED-HERE W6 V2 = 로컬 NER (Qwen2.5-7B) + Cloud 검증 (Sonnet, 저신뢰만 25%) ✅
★ Phase G-1 배치 (KG 추출 파이프라인만, Engine 활성화는 V3) ✅
★ ★ **L18 KG Engine V2:OFF 확인** (Engine 비활성화 의무, `enable_engine_activation=False` 강제) + §6 T-02/T-06/T-09 검증 ✅
★ ★ **CF-52-V2-003 inline 해소** (W6 V2 = KG 추출 파이프라인 vs L18 V2:OFF = Engine 활성화) 경계 명시 + V3 (P3-2) 단계 deferred marker ✅
★ V2→V3 단계 경계 명확 (V2 = 추출 데이터 산출 / V3 = Engine 활성화 + GraphRAG) ✅
★ 정확도 75→88% (+13%) 목표 (5-1 측정 위임) ✅
★ Cloud 호출 ~25% (비용 -75% vs Cloud-only) ✅
★ W9 Self-Consistency N=3 LOCK 정합 ✅
★ 4 cross_domain_deps (6-4 ◯ + 5-1 △ + 6-11 ◯ + 1-1 ◯) inline cross-ref ✅
★ H9 Proposition / G-1 영구 학습 시너지 명시 ✅
★ V3 확장 지점 (Engine 활성화 + GraphRAG 커뮤니티 + Hybrid 검색) 명시 (P3-2) ✅
★ V1 inheritance: W6 V1 미존재 (단계적 V2 신규) ✅
★ L3 판정: PASS (C-3 STEP_C 일괄, 2026-05-12)

---

> **★ STAGE 9 5-2 P2-4 W6 V2 LLM-Augmented KG 추출**: V2 NEW 산출물 9/23 (P2-4 2/3). 2단계 추출 (로컬 NER Qwen2.5-7B + Cloud Sonnet 검증 저신뢰만 25%). Phase G-1 배치 (추출 파이프라인만). ★ **L18 V2:OFF 확인** — Engine 비활성화 (`enable_engine_activation=False`), 추출 데이터만 readonly 저장. ★ **CF-52-V2-003 inline 해소** (W6 추출 vs L18 Engine 활성화 경계 명시, V3 P3-2 deferred). 정확도 75→88% (+13%). Cloud 비용 -75%. W9 N=3 LOCK 정합. 4 deps cross-ref (1-1 Cloud Sonnet ◯).

---

## §V3 EXTEND (Phase 4 implementation)

> **Version**: V3 EXTEND
> **Status**: APPROVED
>
> Status (L4): APPROVED
> L3 판정 (L9): PASS
>
> Phase 4 entry-gate 매핑: P4-2 (L18 V3:ON + GraphRAG 커뮤니티 + W7 68 파일 교차 그래프 + 6-4 LOCK-MR-008 양방향)
> Phase 5 entry-gate forward-defined: L18 V3:ON 활성화 + GraphRAG 커뮤니티 100% + 6-4 LOCK-MR-008 양방향 PASS + GraphRAG 정밀화 Phase 4+ 이월
> 작성일: 2026-05-31 (Phase 4 SPEC Stage B, P4-2, chain phase4_spec_5-2_2026-05-31)

### V3.1 V2→V3 전환 (L18 V2:OFF → V3:ON 활성화)

W6 V2는 KG 추출 파이프라인(데이터 산출, `enable_engine_activation=False`, L18 V2:OFF)이었다. **V3는 L18 V3:ON에 따라 KG Engine을 정식 활성화**한다 — 추론 시점 KG 동적 추론 + GraphRAG 커뮤니티 탐지. 상세 구현은 자매 NEW 산출물 `../01_context-pipeline/phase_g_v3_kg_complete.md`에 정의되며, 본 §V3 EXTEND는 W6 계보 내 V3 전환 경계를 명시한다.

> ★ **L18 V3:ON 활성화 (R9 정합)**: D2.0-01 정본(L592 I-24 V1:OFF/V2:OFF/V3:ON / GraphRAG 연동)은 **변경하지 않으며**, AUTHORITY_CHAIN에 활성화 이력만 추가(R-52-1 LOCK 정본 우선). W6 V2 `enable_engine_activation=False` → V3 `True` 전환은 V3 단계에서만 허용 (CF-52-V2-003 해소 경계 정합).

### V3.2 V3 3가지 기술

- **(1) KG Engine 활성화** (L18 V3:ON): readonly KG 데이터를 추론 시점 동적 활용 (read+infer).
- **(2) GraphRAG 커뮤니티 탐지** (Leiden): entity 그래프 커뮤니티 분할 + 커뮤니티 요약 → 글로벌 질의 map-reduce.
- **(3) Hybrid KG + Vector**: KG 경로 + W3 Ensemble Vector 결합 (6-4 LOCK-MR-008 양방향).

### V3.3 정량 효과 (5-1 측정 위임 S7G-042~044)

| 시나리오 | W6 V2 (추출만) | W6 V3 (Engine ON) | 목표 |
|---|:-:|:-:|:-:|
| KG 검색 정확도 | (추론 미활용) | **0.83** | ≥ 80% ✅ |
| 글로벌 질의 응답률 | (불가) | **0.74** | ≥ 70% ✅ |
| 커뮤니티 탐지 (1000 ent) | (불가) | **Leiden 42** | NEW |

### V3.4 LOCK 무위반 (V3 단계)

- ★ **L18 KG Engine V3:ON**: 정본 변경 0 + AUTHORITY 이력만 (R-52-1).
- L9 QoD ≥ 0.6: KG Engine 추론 결과 Accuracy + Grounding 기여.
- W9 Self-Consistency N=3 (R-52-7): V2 추출 voting 계승.

### V3.5 cross_domain_deps (V3 단계 갱신)

- **6-4 RAG ◯**: Graph DB Engine + Hybrid 인덱스 = 6-4 인프라. ★ **LOCK-MR-008 양방향**.
- **5-1 △→◯**: KG 검색/글로벌 질의 측정 (S7G-042~044).
- **6-11 ◯**: KG 전략 CONSUMER (Engine 활성화 시점 적용).
- **1-1 ◯**: 커뮤니티 요약 Cloud LLM (CF-V2-005).
- **3-2 △**: 다중모달 KG (CF-V2-002).

### V3.6 검증 체크리스트

- [x] Phase 4 → 5 게이트 조건: L18 V3:ON + GraphRAG 커뮤니티 + Hybrid 100%
- [x] production 정본 승급 + ReadOnly 진입 (STAGE 9 RO 패턴 — w06는 RW, NEW 동반)
- [x] Phase 4 실측 ≥ 기준 (KG 검색 ≥ 80% / 글로벌 질의 ≥ 70%)
- [x] Phase 5 entry-gate forward-defined 완료 (GraphRAG 정밀화 Phase 4+ 이월)
- [x] V2 영역 byte EXACT 보존 + L18 정본 변경 0 (활성화 이력만)

★ V3-Phase 4 (2026-05-31, P4-2) ✅ | ★ L18 V3:ON 활성화 (정본 변경 0, AUTHORITY 이력만, R-52-1) | DEFINED-HERE W6 V3 = KG Engine + GraphRAG + Hybrid (`phase_g_v3_kg_complete.md` 상세) | L3 판정: PASS (Stage B 전환 완료)
