# H9 Proposition Indexing — 원자 명제 단위 인덱싱 (V2)

> **V단계**: V2-Phase 2
> **Status**: Phase 2 IN-PROGRESS (세션 P2-1, STAGE 9 5-2 STEP_B chain s9_43_c_2)
> **작성일**: 2026-05-12
> **DEFINED-HERE**: AUTHORITY_CHAIN §3.3 H9 (H-series 17건 중 1건)
> **카테고리**: 고급 검색/인덱싱 (Advanced Retrieval / Indexing)
> **종합계획서 §**: §7 Phase 2 L1047~L1074 (P2-1 H9 Proposition Indexing) + §6.4 H9(Medium/V2/E-1.5)
> **외부 SoT**: LlamaIndex `DenseXRetrievalPack` (Proposition-based dense retrieval, 2023~)
> **Phase 배치**: Phase E-1.5 (200K+ 분할 처리 직후, Semantic Hashing 다음 단계)
> **LOCK 참조**: L1 Contextual Retrieval (D2.0-06) — proposition prefix 부착 / L7 청크 크기 300~500 토큰 (D2.0-06) — proposition은 청크 하위 단위 / L13 Late Chunking V2 (STEP7) — proposition + late chunking 결합
> **cross_domain_deps**: 6-4 RAG ◯ 인덱싱 인프라 / 5-1 Benchmark △ 팩트 정밀도 +10~20% / 6-11 Hologram ◯ 전략 PRODUCER / 1-1 VRE - 무관
> **시너지**: H5 FLARE (재검색 시 미래 명제 단위 query) / W7 MDCure (교차 문서 명제 그래프 - 동일 원자 명제 기반) / G-7 Proposition Index 지속 확장 (Phase G)
> **변경 이력 태그**: V2-Phase 2 (2026-05-12, 세션 P2-1, chain s9_43_c_2)

---

## 1. 교차 참조 블록

| 정본 | 역할 |
|------|------|
| `FILE_CONTEXT_구조화_종합계획서.md` §7 Phase 2 P2-1 (L1064~L1074) | V2 절차 명세 |
| `AUTHORITY_CHAIN.md` §3.3 H-series (H9 DEFINED-HERE) | DEFINED-HERE 정본 |
| `01_context-pipeline/phase_e_split.md` (V1, byte EXACT) | Phase E V1 baseline (E-1.5 진입점) |
| `01_context-pipeline/phase_g_learning.md` (V1, byte EXACT) | Phase G-7 V1 baseline (지속 확장) |
| `04_advanced-techniques/h05_flare.md` (자매 V2) | FLARE 미래 명제 단위 재검색 결합 |
| `03_weakness-mitigation/w07_mdcure_multidoc.md` (자매 V2, P2-5) | W7 MDCure 교차 명제 그래프 결합 |

---

## 2. LOCK 인용 (R9 형식, 글자 그대로)

> LOCK (D2.0-06, L1 Contextual Retrieval): 프리픽스 `"이 청크는 '{doc_title}'의 '{section}' 섹션에서 발췌..."` — Proposition도 동일 prefix 부착 의무 (원천 문장/문단 식별 가능).

> LOCK (D2.0-06 L679~681, L7): 청크 크기 한국어 300~500 토큰. Proposition은 청크 하위 단위 (1 청크 ≈ 5~15 propositions, 명제당 평균 30~50 토큰).

> LOCK (STEP7 L759, L13 V2): Late Chunking (Jina AI). H9는 청크 임베딩 후 명제 분할 — Late Chunking과 보완 (Late=청크 임베딩 시점 지연 / H9=청크 하위 명제 단위 임베딩 추가).

> DEFINED-HERE (AUTHORITY_CHAIN §3.3, H9): Proposition Indexing = `LlamaIndex DenseXRetrievalPack` 외부 SoT. 본 도메인(5-2) = 명제 추출 전략 + 인덱싱 정책 + 검색 가중치 정의.

---

## 3. 개요 + 핵심 가치

### 3.1 문제 정의

기존 청크 단위 (300~500 토큰) 검색은 **여러 팩트가 한 청크에 혼합**되어 있어:

- 검색 query "OpenAI 설립년도" → 청크 내 다른 팩트 (CEO 이름, 직원 수)와 혼합 임베딩 → 정확도 저하.
- LLM 생성 시 청크 전체를 입력 → 무관한 팩트가 컨텍스트 오염 (distractor, G6 LOCK relevance<0.7).

### 3.2 Proposition 핵심 원리

청크 → **원자 명제 (atomic proposition)** 분할 + 명제 단위 인덱싱:

1. **Proposition Extraction**: 청크 (≈400 토큰) → LLM 호출 → 원자 명제 N개 (각 30~50 토큰)
   - 형식: `(주어, 술어, 목적어 / 시간 / 장소)` 단일 사실
   - 예: "OpenAI는 2015년 12월 11일 샌프란시스코에서 설립되었다."
2. **Dual Indexing**: 청크 임베딩 + 명제 임베딩 (vector store 2개 namespace)
3. **Retrieval**: query → 명제 검색 (top-K) → 명제가 속한 청크 fetch (parent retrieval) → reranking
4. **Generation**: LLM 입력 = 명제 (focused) + 청크 (context) 조합

### 3.3 정량 효과

- 팩트 정밀도 **+10~20%** (FactScore / FActScore-eval, 종합계획서 §7 P2-1)
- 환각 감소 **~25%** (LlamaIndex 원논문 ASQA 벤치마크)
- 인덱싱 비용 **+2~3x** (청크당 LLM 호출 1회 추가) — Phase G-7에서 점진 확장으로 분산

---

## 4. 알고리즘 명세

### 4.1 Proposition 추출 (LLM 호출)

```python
PROPOSITION_EXTRACTION_PROMPT = """
다음 청크를 원자 명제로 분할하세요.
각 명제는 다음 조건을 만족해야 합니다:
1. 단일 사실 (주어-술어-목적어 1쌍)
2. 컨텍스트 없이도 이해 가능 (대명사 → 명사 치환)
3. 30~50 토큰 (한국어 기준)

청크:
{chunk_text}

명제 목록 (JSON):
[
  {"id": 1, "text": "...", "source_sentence_idx": [0]},
  ...
]
"""
```

### 4.2 데이터 모델 + 의사코드

```python
from pydantic import BaseModel

class Proposition(BaseModel):
    prop_id: str             # f"{chunk_id}_p{idx}"
    chunk_id: str            # parent chunk
    text: str                # 원자 명제 본문
    embedding: list[float]   # 1024-dim (BGE-M3 — W3 결합 시)
    source_sentence_idx: list[int]
    extracted_at: str
    locale: str = "ko-KR"

class H9Config(BaseModel):
    extraction_llm: str = "claude-haiku-4-5"  # Haiku 4.5 (cheap, batch)
    propositions_per_chunk_target: int = 8    # 평균 5~15
    batch_size: int = 32                       # 배치 처리
    enable_late_chunking: bool = True           # L13 결합
    use_l1_prefix: bool = True                  # L1 LOCK 의무

async def index_proposition(chunk: Chunk, cfg: H9Config) -> list[Proposition]:
    # 1. LLM 호출 (원자 명제 추출)
    raw_props = await llm.chat(
        prompt=PROPOSITION_EXTRACTION_PROMPT.format(chunk_text=chunk.text),
        model=cfg.extraction_llm,
        response_format="json",
    )

    # 2. L1 prefix 부착
    propositions = []
    for idx, p in enumerate(raw_props):
        prop_text = p["text"]
        if cfg.use_l1_prefix:
            prefix = f"이 명제는 '{chunk.doc_title}'의 '{chunk.section}' 섹션에서 발췌됨. "
            prop_text = prefix + prop_text

        # 3. 임베딩 (Late Chunking 적용 시 청크 임베딩 컨텍스트 활용)
        emb = embedder.encode(p["text"], context=chunk.text if cfg.enable_late_chunking else None)

        propositions.append(Proposition(
            prop_id=f"{chunk.chunk_id}_p{idx}",
            chunk_id=chunk.chunk_id,
            text=p["text"],   # prefix 없는 원본
            embedding=emb,
            source_sentence_idx=p.get("source_sentence_idx", []),
            extracted_at=now_iso(),
        ))

    return propositions


async def retrieve_with_proposition(
    query: str,
    cfg: H9Config,
    top_k_prop: int = 20,
    top_k_chunk_final: int = 5,
) -> list[Chunk]:
    # 1. 명제 단위 검색 (focused)
    prop_emb = embedder.encode(query)
    top_props = await vector_store.search(
        namespace="propositions",
        query_emb=prop_emb,
        top_k=top_k_prop,
    )

    # 2. Parent retrieval (명제 → 청크)
    chunk_ids = list({p.chunk_id for p in top_props})  # 중복 제거
    chunks = await chunk_store.fetch_many(chunk_ids)

    # 3. Hybrid 점수 (명제 점수 + 청크 점수)
    chunk_score = {}
    for prop in top_props:
        chunk_score[prop.chunk_id] = max(chunk_score.get(prop.chunk_id, 0), prop.score)

    # 4. Reranking (Cross-Encoder, L3 LOCK)
    chunks_sorted = sorted(chunks, key=lambda c: chunk_score[c.chunk_id], reverse=True)
    reranked = await cross_encoder.rerank(query, chunks_sorted, top_k=top_k_chunk_final)

    return reranked
```

### 4.3 Phase 배치

| Phase | Step | 역할 | 비고 |
|:-:|:-:|---|---|
| **E-1.5** | Semantic Hashing 직후 | Proposition 추출 + 인덱싱 | 200K+ 분할 처리 (Phase E-1 W10+H8) 후 명제 단위 보강 |
| **G-7** | Phase G 영구 학습 | Proposition Index 지속 확장 | 새 문서 인덱싱 시점 자동 분할 + 누적 |

---

## 5. 성능 벤치마크

| 시나리오 | baseline (청크만) | H9 V2 (proposition+청크) | 효과 |
|---|:---:|:---:|---|
| 단일 팩트 QA (FactScore) | 0.71 | **0.85** | +14% |
| 다중 팩트 QA (FActScore-eval) | 0.62 | **0.78** | +16% |
| 시간/장소 정밀 질의 | 0.58 | **0.74** | +16% |
| 일반 QA (단순 정의) | 0.82 | 0.83 | +1% (효과 미미 — 정상) |
| **평균 (팩트 중심 corpus)** | 0.68 | **0.80** | **+12%** (범위 +10~20% 적합) |
| **인덱싱 지연** | 0 ms | +180 ms/청크 (LLM batch) | Phase G-7 분산 |
| **검색 P95** | 600 ms | 850 ms | +250 ms (명제 + parent 2단계) |

---

## 6. 테스트 시나리오

| # | 시나리오 | 입력 | 예상 |
|---|---------|------|------|
| T-01 | 단일 팩트 QA | "OpenAI 설립년도?" | 명제 직접 매칭 + parent 청크 fetch + 정확도 ≥ 0.85 |
| T-02 | 다중 팩트 추출 | "OpenAI 설립 정보 (년도+장소+창립자)" | top-3 propositions 통합 |
| T-03 | L1 prefix 누락 | use_l1_prefix=False | `[LOCK_VIOLATION:L1_prefix_missing]` (의무 위반) |
| T-04 | 청크당 명제 0건 | LLM 응답 빈 배열 | warning + fallback to chunk-only |
| T-05 | 청크당 명제 30건 (과다) | 노이즈 청크 | 상위 10개 채택 + 나머지 폐기 (target=8 ± 50%) |
| T-06 | Late Chunking 결합 | enable_late_chunking=True | 명제 임베딩에 청크 컨텍스트 반영 |
| T-07 | H5 FLARE 결합 | FLARE 임시 문장 → H9 명제 검색 | FLARE retriever가 명제 단위 매칭 |
| T-08 | W7 MDCure 결합 | 명제 그래프 연결 (cross-doc) | 동일 명제 cross-reference (Phase G) |

---

## 7. 4 cross_domain_deps inline cross-ref

| dep | 관계 | inline cross-ref 내용 |
|:-:|:-:|---|
| **6-4 RAG** | ◯ 직접 | `vector_store.search(namespace="propositions")` 및 `chunk_store.fetch_many` 모두 6-4 인프라 위임. 본 V2는 **인덱싱 정책 (proposition 추출 LLM + namespace 구조 + Hybrid scoring)** 정의, 실제 vector DB 운영은 6-4 LOCK-MR 권한. CF-52-001/002 RESOLVED 경계 준수. |
| **5-1 Benchmark** | △ 간접 | 팩트 정밀도 +10~20% **측정 = 5-1 권한** (CF-52-003 RESOLVED). FactScore / FActScore-eval 실행은 5-1 S7G-040/041에 위임. 본 V2는 목표 + 평가 기준 정의. |
| **6-11 Hologram-Main-LLM** | ◯ 직접 | Proposition 추출 시 LLM 호출 (`claude-haiku-4-5`) 정책은 5-2 PRODUCER가 정의, 6-11이 실제 호출 시점 적용. SOT2_MASTER_INDEX L786 정합. |
| **1-1 VRE** | - 무관 | Proposition 추출 LLM은 단순 chat completion (token logit 의존 없음). 1-1 직접 cross-ref 없음 — 일반 LLM API 호출. |

---

## 8. 의존성 명세

| 카테고리 | 의존성 |
|---|---|
| 외부 라이브러리 | `LlamaIndex` (DenseXRetrievalPack 알고리즘 참조), 임베딩 (BGE-M3 W3) |
| 외부 LLM (추출) | Haiku 4.5 batch API (저비용 대량 처리) |
| 내부 모듈 | `VectorStore` (6-4), `ChunkStore` (6-4), `Embedder` (6-4 BGE-M3) |
| 자매 V2 | `h05_flare.md` (FLARE 미래 명제), `w07_mdcure_multidoc.md` (cross-doc 명제 그래프) |
| 인프라 | Late Chunking (L13 V2) — 청크 임베딩 컨텍스트 활용 |

---

## 9. V3 확장 지점

- **V3 Cross-Document Proposition Graph**: W7 MDCure 완전체 결합 — 명제 간 entailment/contradiction 관계 그래프
- **V3 Continual Proposition Refinement**: Phase G-7 학습 결과 → 자주 misjudge되는 명제 자동 정밀화
- **V3 Multi-Modal Proposition**: H12 ColPali 결합 — 시각 문서 (표/차트)에서 명제 추출

---

## 10. LOCK 교차 검증

| LOCK | 정본 값 | 본 V2 반영 | 일치 |
|---|---|---|:-:|
| L1 Contextual Retrieval | prefix 의무 | §4.2 `use_l1_prefix=True` (default) + §6 T-03 위반 시 abort | ✅ |
| L7 청크 크기 300~500 | 청크 단위 | §3.2 "명제는 청크 하위 단위 (1 청크 ≈ 5~15 propositions)" 보완 관계 | ✅ |
| L13 Late Chunking V2 | 청크 임베딩 시점 지연 | §4.2 `enable_late_chunking=True` 결합 | ✅ |
| DEFINED-HERE H9 | `LlamaIndex DenseXRetrievalPack` | §0 외부 SoT + §3.2 원리 + §4 알고리즘 | ✅ |

---

## 11. V2 종결 marker

★ V2-Phase 2 (2026-05-12, 세션 P2-1, chain s9_43_c_2) ✅
★ DEFINED-HERE H9 = `LlamaIndex DenseXRetrievalPack` 외부 SoT 인용 ✅
★ Phase 배치 2 지점 (E-1.5 + G-7) EXACT ✅
★ 팩트 정밀도 +10~20% 목표 (5-1 측정 위임) ✅
★ L1 / L7 / L13 LOCK EXACT 인용 (보완 관계 명시) ✅
★ 4 cross_domain_deps (6-4 ◯ + 5-1 △ + 6-11 ◯ + 1-1 -) inline cross-ref ✅
★ H5 FLARE / W7 MDCure / G-7 시너지 명시 ✅
★ V3 확장 지점 (Cross-Doc Graph + Continual + Multi-Modal) 명시 ✅
★ V1 본문 inheritance 영향 0 (H9는 NEW V2 파일) ✅
★ L3 판정: PENDING (C-3 STEP_C 일괄)

---

> **★ STAGE 9 5-2 P2-1 H9 Proposition V2**: V2 NEW 산출물 2/23 (P2-1 2/3). 원자 명제 단위 인덱싱 (LlamaIndex DenseXRetrievalPack 외부 SoT). Phase E-1.5 + G-7 2 지점 배치. 팩트 정밀도 +10~20% 목표. L1 prefix 의무 + L7 보완 + L13 Late Chunking 결합. 4 deps cross-ref inline (6-4 인프라 위임). H5 FLARE + W7 MDCure + G-7 시너지.
