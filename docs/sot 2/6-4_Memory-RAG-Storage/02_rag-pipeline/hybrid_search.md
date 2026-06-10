# Hybrid Search 통합 상세 (V1)

> **세션**: P1-11 (2026-04-13)
> **산출물 버전**: v1.0
> **상태**: COMPLETE
> **LOCK 준수**: LOCK-MR-008 (Hybrid Search α=0.7 Dense), LOCK-MR-009 (Similarity threshold=0.75)
> **정본**: Part2 V1-P2 (L2034: α=0.7 + Top-K=20), (L2038: threshold=0.75), D2.0-06 §1.1 (L778: BM25_alpha=0.3)
> **교차 참조**: P0-3 chroma_collection_strategy (§5 Hybrid Search 파라미터), P0-4 vectorstore_abc.py (VectorStoreABC), P1-3 chroma_adapter (BM25IndexManager + Dense search), P1-10 rag_6stage_pipeline (Stage 5 Retrieve — §7.3 HybridSearcher 인터페이스)
> **권한 체인**: RULE 1.3 > PLAN 3.0 > D2.0-06 (LOCK) > Part2 V1-P2 (구현가이드) > _index.md (Phase 0 총괄) > 본 문서 (IMPL-DETAIL)
>
> **LOCK 준수 상세**:
>   - LOCK-MR-008: Hybrid Search α=0.7 Dense, Sparse 1-α=0.3 (Part2 V1-P2 L2034 ← S7D-012 ← D2.0-06 L778)
>   - LOCK-MR-009: Similarity threshold=0.75 (Part2 V1-P2 L2038 ← S7D-018)
>   - LOCK-MR-011: BGE-M3 1024dim 원본 + Matryoshka 256dim 검색용 (Stage 3 Embed → 쿼리 임베딩)
>   - LOCK-MR-012: V1 Chroma (Dense 검색 백엔드)
>   - LOCK-MR-014: VectorStore 4메서드 — search() 활용 (P0-4 ABC)
>   - LOCK-MR-015: Deny 판정 시 벡터 삽입 금지 (인덱스 대상 제외)
>   - LOCK-MR-017: project_id 격리 (Dense + Sparse 모두 격리)
>   - LOCK-MR-019: 루프 저장 폭주 방지 (BM25 인덱스 대상도 content_summary만)
>
> **입력 파일**:
>   - D2.0-06 §1.1 (L778: BM25_alpha=0.3 → Dense α=1-0.3=0.7)
>   - Part2 V1-P2 (L2034: Hybrid Search 파라미터 LOCK, L2038: threshold=0.75 LOCK)
>   - P0-3: chroma_collection_strategy.md (§5.1 α=0.7, threshold=0.75, §5.2 애플리케이션 레벨 Hybrid, §5.3 BM25 인덱스 관리)
>   - P0-4: vectorstore_abc.py (VectorStoreABC.search() — Dense 검색 인터페이스)
>   - P1-3: chroma_adapter.md (ChromaVectorStore.search() Dense 구현 + BM25IndexManager Sparse 구현)
>   - P1-10: rag_6stage_pipeline.md (§7.3 HybridSearcher 인터페이스 예약, §7.2 RetrieveConfig)
>   - STEP7-D: S7D-012 (하이브리드 검색), S7D-018 (Cross-Encoder 재순위화)
>
> **이전 단계 이월 사항**: P1-1~P1-10 이월 없음. P1-10 §7.3에서 HybridSearcher 인터페이스(search 시그니처)를 예약하였으며, 본 문서에서 상세 구현을 제공한다.

---

## 목차

1. [Purpose / Scope](#1-purpose--scope)
2. [아키텍처 개요](#2-아키텍처-개요)
3. [HybridSearchConfig 데이터클래스](#3-hybridsearchconfig-데이터클래스)
4. [HybridSearchResult 데이터클래스](#4-hybridsearchresult-데이터클래스)
5. [Semantic Search (Dense) 구현](#5-semantic-search-dense-구현)
6. [Keyword Search (Sparse/BM25) 구현](#6-keyword-search-sparsebm25-구현)
7. [점수 정규화](#7-점수-정규화)
8. [점수 결합 — 가중 합산](#8-점수-결합--가중-합산)
9. [Threshold 필터링](#9-threshold-필터링)
10. [RRF (Reciprocal Rank Fusion) 대체 전략](#10-rrf-reciprocal-rank-fusion-대체-전략)
11. [HybridSearcher 클래스 전체 구현](#11-hybridsearcher-클래스-전체-구현)
12. [P1-10 RAG Pipeline Stage 5 통합](#12-p1-10-rag-pipeline-stage-5-통합)
13. [에러 코드 정의](#13-에러-코드-정의)
14. [복구/재시도 전략](#14-복구재시도-전략)
15. [에스컬레이션 정책](#15-에스컬레이션-정책)
16. [로깅 규격 (R-01-7)](#16-로깅-규격-r-01-7)
17. [시간복잡도 분석 (Big-O)](#17-시간복잡도-분석-big-o)
18. [메트릭 수집 포인트](#18-메트릭-수집-포인트)
19. [단위 테스트 시나리오](#19-단위-테스트-시나리오)
20. [Phase 2 통합 테스트](#20-phase-2-통합-테스트)
21. [세션 간 인터페이스 cross-check](#21-세션-간-인터페이스-cross-check)
22. [LOCK-MR 참조 추적표](#22-lock-mr-참조-추적표)
23. [교차 참조 블록](#23-교차-참조-블록)

---

## 1. Purpose / Scope

### 1.1 목적

본 문서는 VAMOS V1의 **Hybrid Search**(Semantic + Keyword 통합 검색)를 L3 수준(입출력/에러/메트릭/파라미터 상세)으로 기술한다. Dense(벡터 코사인 유사도) 검색과 Sparse(BM25 키워드) 검색의 점수를 가중 합산하여 최종 후보를 산출하며, LOCK-MR-008(α=0.7)과 LOCK-MR-009(threshold=0.75)를 정본 값으로 준수한다.

### 1.2 범위

| 범위 | 포함 | 미포함 |
|------|------|--------|
| Dense 검색 | ChromaVectorStore.search() 호출 (P1-3) | ChromaVectorStore 내부 구현 (P1-3 소관) |
| Sparse 검색 | BM25IndexManager.search() 호출 (P1-3) | BM25 인덱스 동기화 로직 (P1-3 소관) |
| 점수 결합 | 가중 합산 (V1 기본) + RRF (V1 대체) | 학습 기반 결합 (V2+ scope) |
| Threshold | 0.75 필터링 (LOCK-MR-009) | 동적 threshold 조정 (V2+ scope) |
| 통합 접점 | P1-10 Stage 5 Retrieve 내 HybridSearcher 호출 | Cross-Encoder Rerank (P1-10 §7.4 소관) |

### 1.3 α 표기 통일

> **표기 통일** (_index.md §2, P0-3 §5.1 참조): 본 도메인에서 α(alpha)는 **Dense 가중치(0.7)**를 의미한다. D2.0-06 원문 `alpha=0.3`은 BM25(Sparse) 가중치이며, 본 문서의 α와는 반대 방향이다. BM25 가중치는 1-α=0.3이다.

---

## 2. 아키텍처 개요

### 2.1 Hybrid Search 전체 흐름

```
[쿼리 입력]
    │
    ├── (1) Dense Search: ChromaVectorStore.search(query_vec_256, project_id, top_k=20)
    │        → cosine similarity 점수 반환
    │        → P1-3 chroma_adapter §5.1 구현
    │
    └── (2) Sparse Search: BM25IndexManager.search(project_id, query_text, top_k=20)
             → BM25 점수 반환
             → P1-3 chroma_adapter §8 구현
    │
    ▼
[점수 정규화] — §7 min-max normalization
    │
    ▼
[점수 결합] — §8 가중 합산 (V1 기본)
    score = α(0.7) × norm_dense + (1-α)(0.3) × norm_sparse
    │
    ▼
[Threshold 필터링] — §9 (LOCK-MR-009)
    score < 0.75 → 제거
    │
    ▼
[결과 반환] → P1-10 Stage 5 Retrieve (§7.3)
    → Cross-Encoder Rerank (P1-10 §7.4)
    → Top-5 최종 결과
```

### 2.2 컴포넌트 관계

```
P1-10 RAG Pipeline Stage 5 (Retrieve)
    │
    ├── SemanticCache.get() (P1-5)       ← 캐시 히트 시 바이패스
    │
    ├── HybridSearcher.search()          ← 본 문서 (P1-11)
    │       ├── ChromaVectorStore.search()  ← Dense (P1-3)
    │       ├── BM25IndexManager.search()   ← Sparse (P1-3)
    │       ├── ScoreNormalizer              ← 정규화 (본 문서 §7)
    │       └── ScoreFuser                   ← 결합 (본 문서 §8)
    │
    ├── ThresholdFilter                   ← 본 문서 §9 (LOCK-MR-009)
    │
    ├── CrossEncoderReranker             ← P1-10 §7.4
    │
    └── GraphStore.traverse() (P1-4)     ← 컨텍스트 보강
```

---

## 3. HybridSearchConfig 데이터클래스

```python
from dataclasses import dataclass


@dataclass
class HybridSearchConfig:
    """Hybrid Search 설정.

    LOCK-MR-008: α=0.7 (Dense 가중치). 변경 금지.
    LOCK-MR-009: threshold=0.75. 변경 금지.
    Top-K: 기본값 20 (Part2 L2034 LOCK=N — config.toml 조정 가능).
    """

    # --- LOCK 파라미터 (변경 금지) ---
    alpha: float = 0.7                  # LOCK-MR-008: Dense 가중치
    threshold: float = 0.75             # LOCK-MR-009: 유사도 임계값

    # --- 조정 가능 파라미터 (LOCK=N) ---
    top_k_retrieve: int = 20            # Part2 L2034: 초기 후보 수 (LOCK=N)
    fusion_method: str = "weighted_sum" # V1 기본: "weighted_sum" | "rrf"
    rrf_k: int = 60                     # RRF 파라미터 (D2.0-06 L780, fusion_method="rrf" 시)
    normalize_scores: bool = True       # 점수 정규화 활성화 (V1 기본: True)

    def __post_init__(self):
        """LOCK 값 무결성 검증."""
        if self.alpha != 0.7:
            raise ValueError(
                f"alpha must be 0.7 (LOCK-MR-008). Got: {self.alpha}"
            )
        if self.threshold != 0.75:
            raise ValueError(
                f"threshold must be 0.75 (LOCK-MR-009). Got: {self.threshold}"
            )
        if self.top_k_retrieve < 1:
            raise ValueError("top_k_retrieve must be >= 1")
        if self.fusion_method not in ("weighted_sum", "rrf"):
            raise ValueError(
                f"fusion_method must be 'weighted_sum' or 'rrf'. Got: {self.fusion_method}"
            )
```

---

## 4. HybridSearchResult 데이터클래스

```python
from dataclasses import dataclass, field
from typing import Any


@dataclass
class HybridCandidate:
    """Hybrid Search 개별 후보 결과.

    P1-10 §7.2 RankedChunk와의 매핑:
      chunk_id = record_id
      semantic_score = dense_score
      keyword_score = sparse_score
      final_score = hybrid_score
    """

    record_id: str                      # VectorRecord.id (P0-4)
    document: str                       # content_summary (LOCK-MR-019)
    dense_score: float                  # Semantic(Dense) 코사인 유사도
    sparse_score: float                 # BM25(Sparse) 점수 (정규화 후)
    hybrid_score: float                 # 가중 합산 점수: α*dense + (1-α)*sparse
    metadata: dict[str, Any] = field(default_factory=dict)
    # metadata 표준 키: project_id, scope, memory_type, policy_decision, record_id

    # 원본 점수 (정규화 전) — 디버깅/메트릭용
    raw_dense_score: float = 0.0
    raw_sparse_score: float = 0.0


@dataclass
class HybridSearchResult:
    """Hybrid Search 전체 결과.

    P1-10 §7.3 retrieve() 메서드에서 소비.
    """

    candidates: list[HybridCandidate]   # threshold 필터링 후 결과
    total_before_threshold: int         # threshold 적용 전 후보 수
    total_after_threshold: int          # threshold 적용 후 후보 수
    fusion_method: str                  # "weighted_sum" | "rrf"
    alpha: float                        # 적용된 α 값 (항상 0.7)
    threshold: float                    # 적용된 threshold (항상 0.75)
    dense_search_ms: float              # Dense 검색 소요 시간 (ms)
    sparse_search_ms: float             # Sparse 검색 소요 시간 (ms)
    fusion_ms: float                    # 결합 + 필터링 소요 시간 (ms)
    total_ms: float                     # 전체 Hybrid Search 소요 시간 (ms)
```

---

## 5. Semantic Search (Dense) 구현

### 5.1 입력/출력

| 항목 | 값 | 근거 |
|------|---|------|
| **입력** | query_vector (Matryoshka 256dim), project_id, top_k=20 | LOCK-MR-011 (256dim 검색용), LOCK-MR-017 (격리) |
| **출력** | list[VectorRecord] — cosine similarity 포함 (metadata._similarity) | P1-3 §5.1 search() 반환값 |
| **백엔드** | ChromaVectorStore.search() (P1-3) | LOCK-MR-012 (V1 Chroma) |

### 5.2 호출 코드

```python
def _dense_search(
    self,
    query_vector: list[float],
    project_id: str,
    top_k: int = 20,
) -> list[tuple[str, float, str, dict]]:
    """Dense(Semantic) 검색.

    ChromaVectorStore.search()를 호출하여 코사인 유사도 기반 결과를 반환한다.

    Args:
        query_vector: 쿼리 임베딩 벡터 (Matryoshka 256dim)
        project_id: 프로젝트 ID (LOCK-MR-017)
        top_k: 반환 후보 수

    Returns:
        list[(record_id, similarity_score, document, metadata)]
        similarity_score: 1 - cosine_distance (0~1 범위)
    """
    try:
        results: list[VectorRecord] = self._vector_store.search(
            query_vector=query_vector,
            project_id=project_id,
            top_k=top_k,
        )
        return [
            (
                r.id,
                r.metadata.get("_similarity", 0.0),  # P1-3 §5.1: 1 - distance
                r.document,
                r.metadata,
            )
            for r in results
        ]
    except Exception as e:
        self._log("ERROR", "HYB_ERR_001", f"Dense search failed: {e}",
                  project_id=project_id)
        raise HybridSearchError("HYB_ERR_001", f"Dense search failed: {e}")
```

### 5.3 코사인 유사도 변환

P1-3 §5.1에서 Chroma의 cosine distance를 similarity로 변환하는 로직이 이미 구현되어 있음:

```
similarity = 1 - cosine_distance
```

> **검증 완료** (P0-3 §6.1): Chroma는 `distance` 값을 반환하며, `similarity = 1 - distance`로 변환. cosine 유사도 범위는 [0, 1] (음수 벡터 없는 경우).

---

## 6. Keyword Search (Sparse/BM25) 구현

### 6.1 입력/출력

| 항목 | 값 | 근거 |
|------|---|------|
| **입력** | query_text (원문 쿼리), project_id, top_k=20 | LOCK-MR-017 (격리) |
| **출력** | list[(record_id, bm25_score)] — 점수 내림차순 | P1-3 §8.1 BM25IndexManager.search() |
| **라이브러리** | rank_bm25 (BM25Okapi) | P0-3 §5.3 |
| **토크나이저** | 공백 분할 (V1) | P1-3 §8.1 — V2+에서 형태소 분석기로 교체 가능 |

### 6.2 호출 코드

```python
def _sparse_search(
    self,
    query_text: str,
    project_id: str,
    top_k: int = 20,
) -> list[tuple[str, float]]:
    """Sparse(BM25) 키워드 검색.

    P1-3 BM25IndexManager.search()를 호출하여 키워드 매칭 점수를 반환한다.

    Args:
        query_text: 쿼리 텍스트 (원문)
        project_id: 프로젝트 ID (LOCK-MR-017)
        top_k: 반환 후보 수

    Returns:
        list[(record_id, bm25_score)] — 내림차순
        bm25_score: BM25Okapi 원시 점수 (0 이상, 상한 가변)
    """
    try:
        results = self._bm25_manager.search(
            project_id=project_id,
            query=query_text,
            top_k=top_k,
        )
        return results  # list[(record_id, bm25_score)]
    except Exception as e:
        self._log("WARNING", "HYB_ERR_002", f"Sparse search failed: {e}",
                  project_id=project_id)
        # Graceful degradation: Sparse 실패 시 빈 결과 반환 (Dense만으로 검색 계속)
        return []
```

### 6.3 BM25 점수 특성

| 특성 | 값 |
|------|---|
| 범위 | [0, +∞) — 상한 없음 |
| 분포 | 쿼리 단어 출현 빈도에 비례, 문서 길이에 반비례 |
| 의미 | 0 = 쿼리 단어 미포함, 높을수록 관련성 높음 |
| 정규화 필요 | **필수** — Dense(0~1)와 결합하려면 min-max 정규화 |

---

## 7. 점수 정규화

### 7.1 필요성

Dense(코사인 유사도)와 Sparse(BM25) 점수는 스케일이 다르므로 가중 합산 전 정규화가 필요하다:

| 검색 유형 | 점수 범위 | 스케일 |
|----------|----------|--------|
| Dense (cosine similarity) | [0, 1] | 고정 |
| Sparse (BM25) | [0, +∞) | 쿼리/코퍼스 의존 |

### 7.2 Min-Max 정규화

```python
def _normalize_scores(
    self,
    scores: list[tuple[str, float]],
) -> list[tuple[str, float]]:
    """Min-Max 정규화 — [0, 1] 범위로 변환.

    Args:
        scores: list[(record_id, raw_score)]

    Returns:
        list[(record_id, normalized_score)] — 0~1 범위
    """
    if not scores:
        return []

    raw_values = [s[1] for s in scores]
    min_val = min(raw_values)
    max_val = max(raw_values)

    if max_val == min_val:
        # 단일 후보(degenerate) → 원시 점수 보존 (1.0 perfect match가 threshold에서 누락되지 않도록)
        if len(scores) == 1:
            return [(record_id, raw) for record_id, raw in scores]
        # 복수 후보 동일 점수 → 0.5 중립값
        return [(record_id, 0.5) for record_id, _ in scores]

    return [
        (record_id, (score - min_val) / (max_val - min_val))
        for record_id, score in scores
    ]
```

### 7.3 Dense 점수 정규화

Dense 점수(코사인 유사도)는 이미 [0, 1] 범위이므로 추가 정규화는 선택적이다. 그러나 결과 집합 내에서의 상대 비교를 위해 동일한 min-max 정규화를 적용한다 (config.normalize_scores=True 시).

> **정규화 비활성화 옵션**: config.toml `[memory.vector].normalize_scores=false` 설정 시 Dense는 원시 코사인 유사도, Sparse는 원시 BM25 점수를 사용한다. 이 경우 α=0.7 가중치의 의미가 달라지므로 주의. V1 기본값은 True(정규화 활성화).

---

## 8. 점수 결합 — 가중 합산

### 8.1 공식

```
final_score = α × norm_dense_score + (1 - α) × norm_sparse_score
```

| 변수 | 값 | LOCK |
|------|---|------|
| α | 0.7 | **LOCK-MR-008** |
| 1 - α | 0.3 | **LOCK-MR-008** |

### 8.2 결합 알고리즘

```python
def _fuse_weighted_sum(
    self,
    dense_results: list[tuple[str, float, str, dict]],
    sparse_results: list[tuple[str, float]],
    alpha: float = 0.7,
    normalize: bool = True,
) -> list[HybridCandidate]:
    """가중 합산 결합. LOCK-MR-008: α=0.7.

    Dense와 Sparse 결과를 record_id 기준으로 병합하고
    가중 합산 점수를 산출한다.

    처리 규칙:
      - Dense에만 존재: sparse_score = 0.0 (키워드 미매칭)
      - Sparse에만 존재: dense_score = 0.0 (벡터 미매칭)
      - 양쪽 모두 존재: 가중 합산

    Args:
        dense_results: [(record_id, similarity, document, metadata)]
        sparse_results: [(record_id, bm25_score)]
        alpha: Dense 가중치 (LOCK-MR-008: 0.7)
        normalize: 점수 정규화 활성화 여부

    Returns:
        list[HybridCandidate] — hybrid_score 내림차순 정렬
    """
    # Step 1: Dense 점수 맵 구축
    dense_map: dict[str, tuple[float, str, dict]] = {}
    for record_id, score, document, metadata in dense_results:
        dense_map[record_id] = (score, document, metadata)

    # Step 2: Sparse 점수 맵 구축
    sparse_map: dict[str, float] = {}
    for record_id, score in sparse_results:
        sparse_map[record_id] = score

    # Step 3: 전체 record_id 합집합
    all_ids = set(dense_map.keys()) | set(sparse_map.keys())

    # Step 4: 원시 점수 수집
    dense_scores = [(rid, dense_map[rid][0]) if rid in dense_map else (rid, 0.0)
                    for rid in all_ids]
    sparse_scores = [(rid, sparse_map.get(rid, 0.0)) for rid in all_ids]

    # Step 5: 정규화
    if normalize:
        norm_dense = dict(self._normalize_scores(dense_scores))
        norm_sparse = dict(self._normalize_scores(sparse_scores))
    else:
        norm_dense = dict(dense_scores)
        norm_sparse = dict(sparse_scores)

    # Step 6: 가중 합산
    candidates: list[HybridCandidate] = []
    for rid in all_ids:
        d_score = norm_dense.get(rid, 0.0)
        s_score = norm_sparse.get(rid, 0.0)
        hybrid = alpha * d_score + (1 - alpha) * s_score

        # document/metadata는 Dense 결과에서 가져옴 (Dense 미존재 시 빈 값)
        document = ""
        metadata = {}
        raw_dense = 0.0
        if rid in dense_map:
            raw_dense, document, metadata = dense_map[rid]

        candidates.append(HybridCandidate(
            record_id=rid,
            document=document,
            dense_score=d_score,
            sparse_score=s_score,
            hybrid_score=hybrid,
            metadata=metadata,
            raw_dense_score=raw_dense,
            raw_sparse_score=sparse_map.get(rid, 0.0),
        ))

    # Step 7: hybrid_score 내림차순 정렬
    candidates.sort(key=lambda c: c.hybrid_score, reverse=True)

    return candidates
```

### 8.3 Sparse-Only 후보 처리

Sparse에만 존재하는 후보(Dense 미반환)는 dense_score=0.0이므로 hybrid_score가 낮게 산출된다 (최대 0.3 × 1.0 = 0.3). 이는 threshold=0.75에 의해 자동 필터링되므로 실질적으로 Dense 결과가 없는 후보는 최종 결과에 포함되지 않는다.

> **설계 의도**: α=0.7로 Dense를 우선하는 LOCK 값 설계에 부합. Sparse는 보충적 역할로, Dense와 함께 매칭되는 경우에만 최종 후보에 유의미하게 기여한다.

---

## 9. Threshold 필터링

### 9.1 규칙

> LOCK-MR-009: final_score < 0.75인 결과를 제거한다.

```python
def _apply_threshold(
    self,
    candidates: list[HybridCandidate],
    threshold: float = 0.75,
) -> list[HybridCandidate]:
    """Threshold 필터링. LOCK-MR-009: 0.75.

    Args:
        candidates: 가중 합산 결과 (hybrid_score 내림차순)
        threshold: 유사도 임계값 (LOCK-MR-009: 0.75)

    Returns:
        threshold 이상인 후보만 포함한 리스트 (순서 유지)
    """
    return [c for c in candidates if c.hybrid_score >= threshold]
```

### 9.2 Threshold 적용 시점

```
Dense + Sparse → 정규화 → 가중 합산 → [Threshold 필터링] → Rerank (P1-10)
                                        ^^^^^^^^^^^^^^^^
                                        본 문서 §9 (여기)
```

Threshold는 가중 합산 후, Cross-Encoder Rerank 전에 적용한다. 이유:
1. Rerank는 계산 비용이 높음 (Cross-Encoder 모델 추론) → 사전 필터링으로 비용 절감
2. threshold 미달 후보를 Rerank에 전달하는 것은 불필요

### 9.3 결과 0건 처리

threshold 적용 후 결과가 0건인 경우:
- 에러 코드 HYB_ERR_005 (THRESHOLD_EMPTY) 발생 — WARNING 레벨
- P1-10 §7.5 RAG_ERR_017과 연동: "검색 결과 없음" 안내 메시지 반환
- 빈 리스트 반환 (예외 발생 아님)

---

## 10. RRF (Reciprocal Rank Fusion) 대체 전략

### 10.1 개요

V1 기본은 가중 합산이나, config.toml `[memory.vector].fusion_method="rrf"` 설정 시 RRF로 전환 가능 (P0-3 §5.2).

### 10.2 RRF 공식

```
RRF_score(d) = Σ 1 / (k + rank_i(d))
```

- k = 60 (D2.0-06 L780 기본값)
- rank_i(d) = 검색 시스템 i에서 문서 d의 순위 (1-based)
- Dense 순위 + Sparse 순위를 합산

### 10.3 구현

```python
def _fuse_rrf(
    self,
    dense_results: list[tuple[str, float, str, dict]],
    sparse_results: list[tuple[str, float]],
    k: int = 60,
) -> list[HybridCandidate]:
    """Reciprocal Rank Fusion 결합.

    D2.0-06 L780: RRF k=60.
    config.toml fusion_method="rrf" 시 사용.

    Args:
        dense_results: Dense 결과 (순위 순)
        sparse_results: Sparse 결과 (순위 순)
        k: RRF 파라미터 (기본 60)

    Returns:
        list[HybridCandidate] — RRF 점수 내림차순 정렬
    """
    rrf_scores: dict[str, float] = {}
    dense_docs: dict[str, tuple[str, dict]] = {}

    # Dense RRF
    for rank, (record_id, score, document, metadata) in enumerate(dense_results, 1):
        rrf_scores[record_id] = rrf_scores.get(record_id, 0.0) + 1.0 / (k + rank)
        dense_docs[record_id] = (document, metadata)

    # Sparse RRF
    for rank, (record_id, score) in enumerate(sparse_results, 1):
        rrf_scores[record_id] = rrf_scores.get(record_id, 0.0) + 1.0 / (k + rank)

    # 후보 구성
    candidates = []
    for record_id, rrf_score in rrf_scores.items():
        document, metadata = dense_docs.get(record_id, ("", {}))
        candidates.append(HybridCandidate(
            record_id=record_id,
            document=document,
            dense_score=0.0,        # RRF 모드에서는 개별 점수 미사용
            sparse_score=0.0,
            hybrid_score=rrf_score,  # RRF 점수
            metadata=metadata,
        ))

    candidates.sort(key=lambda c: c.hybrid_score, reverse=True)
    return candidates
```

### 10.4 RRF 모드에서의 Threshold 적용

RRF 점수는 가중 합산과 스케일이 다르므로 (최대값 ≈ 2/(k+1)), threshold=0.75를 직접 적용할 수 없다. V1에서는 RRF 모드 사용 시 threshold 필터링을 **건너뛰고**, Top-K만으로 결과를 제한한다.

> **주의**: RRF 모드는 V1 대체 전략으로, 가중 합산이 기본이다. RRF 모드 사용 시 LOCK-MR-009 threshold가 사실상 비활성화됨을 인지해야 한다. 이 제약은 Phase 2에서 RRF 점수 정규화 구현으로 해소 예정.

---

## 11. HybridSearcher 클래스 전체 구현

```python
import time
import logging
from dataclasses import dataclass
from typing import Any, Optional

# 내부 임포트 (P1-3 산출물)
# from .chroma_adapter import ChromaVectorStore, BM25IndexManager
# from .vectorstore_abc import VectorRecord

logger = logging.getLogger("vamos.memory.hybrid_search")


class HybridSearchError(Exception):
    """Hybrid Search 전용 예외."""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


class HybridSearcher:
    """Hybrid Search (Dense + Sparse) 통합 검색기.

    P1-10 §7.3 HybridSearcher 인터페이스 구현.
    LOCK-MR-008: α=0.7 (Dense 가중치)
    LOCK-MR-009: threshold=0.75 (유사도 임계값)
    LOCK-MR-017: project_id 격리 (Dense + Sparse 모두)

    P1-10 호출 시그니처:
        candidates = self.hybrid_searcher.search(
            query_vector=query_vector,
            query_text=input.query_text,
            project_id=input.project_id,
            top_k=input.retrieve_config.top_k_retrieve,
            alpha=input.retrieve_config.alpha
        )
    """

    def __init__(
        self,
        vector_store,       # ChromaVectorStore (P1-3)
        bm25_manager,       # BM25IndexManager (P1-3)
        config: Optional[HybridSearchConfig] = None,
    ):
        """HybridSearcher 초기화.

        Args:
            vector_store: VectorStoreABC 구현체 (V1: ChromaVectorStore)
            bm25_manager: BM25IndexManager 인스턴스 (P1-3 §8)
            config: Hybrid Search 설정 (None이면 기본값 사용)
        """
        self._vector_store = vector_store
        self._bm25_manager = bm25_manager
        self._config = config or HybridSearchConfig()

    def search(
        self,
        query_vector: list[float],
        query_text: str,
        project_id: str,
        top_k: int = 20,
        alpha: float = 0.7,
    ) -> HybridSearchResult:
        """Hybrid Search 실행.

        P1-10 §7.3에서 정의한 인터페이스 시그니처를 구현한다.

        Args:
            query_vector: 쿼리 임베딩 벡터 (Matryoshka 256dim, LOCK-MR-011)
            query_text: 쿼리 텍스트 (BM25 키워드 검색용)
            project_id: 프로젝트 ID (LOCK-MR-017 격리)
            top_k: 반환 후보 수 (기본 20, LOCK=N)
            alpha: Dense 가중치 (LOCK-MR-008: 0.7)

        Returns:
            HybridSearchResult — threshold 필터링 후 결과

        Raises:
            HybridSearchError: Dense 검색 실패 시 (HYB_ERR_001)
            ValueError: project_id 미제공 시
        """
        start_time = time.monotonic()

        # LOCK 검증
        if alpha != 0.7:
            self._log("WARNING", "HYB_WARN_001",
                      f"alpha={alpha} overridden to 0.7 (LOCK-MR-008)",
                      project_id=project_id)
            alpha = 0.7  # LOCK-MR-008 강제

        if not project_id:
            raise ValueError("project_id is required (LOCK-MR-017)")

        # Step 1: Dense Search
        t0 = time.monotonic()
        dense_results = self._dense_search(query_vector, project_id, top_k)
        dense_ms = (time.monotonic() - t0) * 1000

        # Step 2: Sparse Search
        t0 = time.monotonic()
        sparse_results = self._sparse_search(query_text, project_id, top_k)
        sparse_ms = (time.monotonic() - t0) * 1000

        # Step 3: Score Fusion
        t0 = time.monotonic()
        if self._config.fusion_method == "rrf":
            candidates = self._fuse_rrf(
                dense_results, sparse_results, k=self._config.rrf_k
            )
            # RRF 모드: threshold 비적용 (§10.4)
            filtered = candidates[:top_k]
            total_before = len(candidates)
            total_after = len(filtered)
        else:
            candidates = self._fuse_weighted_sum(
                dense_results, sparse_results,
                alpha=alpha,
                normalize=self._config.normalize_scores,
            )
            total_before = len(candidates)

            # Step 4: Threshold Filtering (LOCK-MR-009)
            filtered = self._apply_threshold(
                candidates, self._config.threshold
            )
            total_after = len(filtered)

            if total_after == 0 and total_before > 0:
                self._log("WARNING", "HYB_ERR_005",
                          f"All {total_before} candidates below threshold "
                          f"{self._config.threshold}",
                          project_id=project_id)

        fusion_ms = (time.monotonic() - t0) * 1000
        total_ms = (time.monotonic() - start_time) * 1000

        # 로깅
        self._log("INFO", "HYB_SEARCH_OK",
                  f"Hybrid search complete: {total_after}/{total_before} "
                  f"candidates, method={self._config.fusion_method}, "
                  f"total_ms={total_ms:.1f}",
                  project_id=project_id)

        return HybridSearchResult(
            candidates=filtered,
            total_before_threshold=total_before,
            total_after_threshold=total_after,
            fusion_method=self._config.fusion_method,
            alpha=alpha,
            threshold=self._config.threshold,
            dense_search_ms=dense_ms,
            sparse_search_ms=sparse_ms,
            fusion_ms=fusion_ms,
            total_ms=total_ms,
        )

    # --- 내부 메서드: §5, §6, §7, §8, §9 참조 ---

    def _dense_search(
        self,
        query_vector: list[float],
        project_id: str,
        top_k: int = 20,
    ) -> list[tuple[str, float, str, dict]]:
        """Dense(Semantic) 검색. §5 참조."""
        try:
            results = self._vector_store.search(
                query_vector=query_vector,
                project_id=project_id,
                top_k=top_k,
            )
            return [
                (r.id, r.metadata.get("_similarity", 0.0), r.document, r.metadata)
                for r in results
            ]
        except Exception as e:
            self._log("ERROR", "HYB_ERR_001", f"Dense search failed: {e}",
                      project_id=project_id)
            raise HybridSearchError("HYB_ERR_001", f"Dense search failed: {e}")

    def _sparse_search(
        self,
        query_text: str,
        project_id: str,
        top_k: int = 20,
    ) -> list[tuple[str, float]]:
        """Sparse(BM25) 검색. §6 참조."""
        try:
            return self._bm25_manager.search(
                project_id=project_id,
                query=query_text,
                top_k=top_k,
            )
        except Exception as e:
            self._log("WARNING", "HYB_ERR_002", f"Sparse search failed: {e}",
                      project_id=project_id)
            return []  # Graceful degradation

    def _normalize_scores(
        self,
        scores: list[tuple[str, float]],
    ) -> list[tuple[str, float]]:
        """Min-Max 정규화. §7 참조."""
        if not scores:
            return []
        raw = [s[1] for s in scores]
        min_val, max_val = min(raw), max(raw)
        if max_val == min_val:
            return [(rid, 0.5) for rid, _ in scores]
        return [
            (rid, (score - min_val) / (max_val - min_val))
            for rid, score in scores
        ]

    def _fuse_weighted_sum(
        self,
        dense_results: list[tuple[str, float, str, dict]],
        sparse_results: list[tuple[str, float]],
        alpha: float = 0.7,
        normalize: bool = True,
    ) -> list[HybridCandidate]:
        """가중 합산 결합. §8 참조. LOCK-MR-008."""
        dense_map: dict[str, tuple[float, str, dict]] = {}
        for record_id, score, document, metadata in dense_results:
            dense_map[record_id] = (score, document, metadata)

        sparse_map: dict[str, float] = dict(sparse_results)

        all_ids = set(dense_map.keys()) | set(sparse_map.keys())

        dense_scores = [(rid, dense_map[rid][0]) if rid in dense_map
                        else (rid, 0.0) for rid in all_ids]
        sparse_scores_list = [(rid, sparse_map.get(rid, 0.0)) for rid in all_ids]

        if normalize:
            norm_dense = dict(self._normalize_scores(dense_scores))
            norm_sparse = dict(self._normalize_scores(sparse_scores_list))
        else:
            norm_dense = dict(dense_scores)
            norm_sparse = dict(sparse_scores_list)

        candidates = []
        for rid in all_ids:
            d = norm_dense.get(rid, 0.0)
            s = norm_sparse.get(rid, 0.0)
            hybrid = alpha * d + (1 - alpha) * s

            document, metadata, raw_d = "", {}, 0.0
            if rid in dense_map:
                raw_d, document, metadata = dense_map[rid]

            candidates.append(HybridCandidate(
                record_id=rid,
                document=document,
                dense_score=d,
                sparse_score=s,
                hybrid_score=hybrid,
                metadata=metadata,
                raw_dense_score=raw_d,
                raw_sparse_score=sparse_map.get(rid, 0.0),
            ))

        candidates.sort(key=lambda c: c.hybrid_score, reverse=True)
        return candidates

    def _fuse_rrf(
        self,
        dense_results: list[tuple[str, float, str, dict]],
        sparse_results: list[tuple[str, float]],
        k: int = 60,
    ) -> list[HybridCandidate]:
        """RRF 결합. §10 참조."""
        rrf_scores: dict[str, float] = {}
        dense_docs: dict[str, tuple[str, dict]] = {}

        for rank, (rid, score, doc, meta) in enumerate(dense_results, 1):
            rrf_scores[rid] = rrf_scores.get(rid, 0.0) + 1.0 / (k + rank)
            dense_docs[rid] = (doc, meta)

        for rank, (rid, score) in enumerate(sparse_results, 1):
            rrf_scores[rid] = rrf_scores.get(rid, 0.0) + 1.0 / (k + rank)

        candidates = []
        for rid, rrf_score in rrf_scores.items():
            doc, meta = dense_docs.get(rid, ("", {}))
            candidates.append(HybridCandidate(
                record_id=rid, document=doc,
                dense_score=0.0, sparse_score=0.0,
                hybrid_score=rrf_score, metadata=meta,
            ))

        candidates.sort(key=lambda c: c.hybrid_score, reverse=True)
        return candidates

    def _apply_threshold(
        self,
        candidates: list[HybridCandidate],
        threshold: float = 0.75,
    ) -> list[HybridCandidate]:
        """Threshold 필터링. §9 참조. LOCK-MR-009."""
        return [c for c in candidates if c.hybrid_score >= threshold]

    def _log(
        self,
        level: str,
        code: str,
        message: str,
        project_id: str = "",
        **extra,
    ) -> None:
        """구조화 로깅. R-01-7 규격.

        로그 형식:
        {
            "ts": "ISO-8601",
            "level": "INFO|WARNING|ERROR",
            "code": "HYB_ERR_001",
            "component": "HybridSearcher",
            "project_id": "...",
            "message": "...",
            "extra": { ... }
        }
        """
        log_data = {
            "code": code,
            "component": "HybridSearcher",
            "project_id": project_id,
            "message": message,
            **extra,
        }
        log_fn = getattr(logger, level.lower(), logger.info)
        log_fn(str(log_data))
```

---

## 12. P1-10 RAG Pipeline Stage 5 통합

### 12.1 통합 접점

P1-10 §7.3에서 예약한 HybridSearcher 인터페이스를 본 문서가 구현한다:

| P1-10 예약 시그니처 | 본 문서 구현 | 정합 |
|-------------------|-------------|------|
| `hybrid_searcher.search(query_vector, query_text, project_id, top_k, alpha)` | `HybridSearcher.search(query_vector, query_text, project_id, top_k, alpha)` | **일치** |
| 반환: candidates (final_score >= threshold) | `HybridSearchResult.candidates` (list[HybridCandidate]) | **일치** |
| alpha=0.7 (RetrieveConfig) | α=0.7 (HybridSearchConfig, LOCK-MR-008) | **일치** |
| threshold=0.75 (RetrieveConfig) | threshold=0.75 (HybridSearchConfig, LOCK-MR-009) | **일치** |

### 12.2 P1-10 RetrieveConfig → HybridSearchConfig 매핑

```python
# P1-10 Stage 5 retrieve() 내부에서:
retrieve_config = input.retrieve_config  # P1-10 RetrieveConfig

# HybridSearcher는 생성 시 HybridSearchConfig로 초기화되며,
# search() 호출 시 top_k와 alpha를 오버라이드한다.
result = self.hybrid_searcher.search(
    query_vector=query_vector,
    query_text=input.query_text,
    project_id=input.project_id,
    top_k=retrieve_config.top_k_retrieve,   # 20
    alpha=retrieve_config.alpha,            # 0.7 (LOCK)
)

# P1-10 RankedChunk 변환
ranked_chunks = [
    RankedChunk(
        chunk_id=c.record_id,
        doc_id=c.metadata.get("doc_id", ""),
        text=c.document,
        final_score=c.hybrid_score,
        semantic_score=c.dense_score,
        keyword_score=c.sparse_score,
        rerank_score=None,  # Rerank 전
        metadata=c.metadata,
    )
    for c in result.candidates
]
```

### 12.3 Stage 2 (Chunk) 통합 접점

Stage 2에서 청킹된 텍스트가 Stage 4(Store)를 거쳐 Chroma에 저장되면, 동시에 BM25 인덱스에도 동기화된다 (P1-3 §8.2 `_sync_bm25_index`). 이 인덱스가 본 문서의 Sparse 검색 대상이다.

```
Stage 2 (Chunk) → Stage 4 (Store) → ChromaVectorStore.upsert()
                                      └── _sync_bm25_index() → BM25 인덱스 갱신
                                                                    │
Stage 5 (Retrieve) → HybridSearcher.search()                      │
                       └── _sparse_search() ← BM25IndexManager ←──┘
```

### 12.4 Stage 3 (Embed) 통합 접점

Stage 3에서 생성된 Matryoshka 256dim 쿼리 임베딩이 HybridSearcher.search()의 `query_vector` 파라미터로 전달된다. 임베딩 모델 일관성(BGE-M3, LOCK-MR-011)은 Stage 3 → Stage 5 간에 보장되어야 한다.

---

## 13. 에러 코드 정의

| 에러 코드 | 명칭 | 레벨 | 설명 | 복구 |
|----------|------|------|------|------|
| `HYB_ERR_001` | DENSE_SEARCH_FAIL | ERROR | Dense 검색 실패 (Chroma 오류) | 재시도 2회 → 실패 시 에스컬레이션 LEVEL-2 |
| `HYB_ERR_002` | SPARSE_SEARCH_FAIL | WARNING | BM25 검색 실패 | Sparse 결과 비움, Dense만으로 계속 (graceful degradation) |
| `HYB_ERR_003` | NORMALIZATION_FAIL | WARNING | 점수 정규화 실패 (빈 결과 등) | 원시 점수로 폴백 |
| `HYB_ERR_004` | FUSION_FAIL | ERROR | 점수 결합 실패 | 빈 결과 반환 + 에스컬레이션 LEVEL-2 |
| `HYB_ERR_005` | THRESHOLD_EMPTY | WARNING | Threshold 후 결과 0건 | 빈 결과 반환 + "검색 결과 없음" (P1-10 RAG_ERR_017) |
| `HYB_ERR_006` | INVALID_PROJECT_ID | ERROR | project_id 미제공/빈 값 | ValueError 발생 (LOCK-MR-017) |
| `HYB_ERR_007` | ALPHA_OVERRIDE | WARNING | α ≠ 0.7 값 시도 | 0.7로 강제 복원 (LOCK-MR-008) |
| `HYB_ERR_008` | DENSE_EMPTY | INFO | Dense 결과 0건 | Sparse만으로 계속 (최종 threshold에서 필터링 가능성 높음) |
| `HYB_ERR_009` | SPARSE_EMPTY | INFO | Sparse 결과 0건 | Dense만으로 계속 |
| `HYB_ERR_010` | CONFIG_INVALID | ERROR | HybridSearchConfig 검증 실패 | 기본 설정으로 폴백 |

---

## 14. 복구/재시도 전략

| 에러 코드 | 재시도 | 재시도 간격 | 최대 시도 | 폴백 |
|----------|--------|-----------|----------|------|
| HYB_ERR_001 (Dense 실패) | O | 100ms → 200ms (지수 백오프) | 3회 | 에스컬레이션 LEVEL-2 |
| HYB_ERR_002 (Sparse 실패) | O | 100ms | 2회 | Sparse 비활성화, Dense-only 모드 |
| HYB_ERR_003 (정규화 실패) | X | — | — | 원시 점수 사용 |
| HYB_ERR_004 (결합 실패) | X | — | — | 빈 결과 반환 |
| HYB_ERR_005 (결과 0건) | X | — | — | 빈 결과 반환 |

### 14.1 Graceful Degradation 순서

```
1. Dense + Sparse (정상)
    ↓ Sparse 실패
2. Dense-only (Sparse=0.0 → hybrid=α×dense, α=0.7 유지(LOCK-MR-008), threshold 유지)
    ↓ Dense 실패
3. 빈 결과 반환 + 에스컬레이션 LEVEL-2 (P1-10 RAG_ERR_015)
```

---

## 15. 에스컬레이션 정책

### 15.1 레벨 정의

| 레벨 | 조건 | 조치 | 대상 |
|------|------|------|------|
| LEVEL-1 | Sparse 검색 실패 + Dense 정상 | 경고 로그 + 운영 대시보드 알림 | 운영팀 |
| LEVEL-2 | Dense 검색 실패 (재시도 소진) | 에러 로그 + 즉시 알림 + 자동 티켓 | 개발팀 |
| LEVEL-3 | Dense + Sparse 동시 실패 (검색 불가) | 에러 로그 + 긴급 알림 + 서비스 상태 전환 | CTO / 인프라팀 |

### 15.2 에스컬레이션 페이로드

```python
@dataclass
class EscalationPayload:
    """에스컬레이션 이벤트 페이로드.

    P1-3 chroma_adapter §14, P1-4 json_graphrag §11, P1-5 semantic_cache §6.5,
    P1-10 rag_6stage_pipeline §14 에스컬레이션 표준과 정합.
    """
    escalation_id: str          # UUID (고유 ID)
    level: str                  # "LEVEL-1" | "LEVEL-2" | "LEVEL-3"
    error_code: str             # HYB_ERR_xxx
    component: str              # "HybridSearcher"
    project_id: str             # 영향받는 프로젝트
    message: str                # 사람이 읽을 수 있는 설명
    timestamp: str              # ISO-8601
    context: dict               # 추가 컨텍스트 (query_text 해시, dense_ms, sparse_ms 등)
    retry_count: int = 0        # 재시도 횟수
    resolved: bool = False      # 자동 해결 여부
```

---

## 16. 로깅 규격 (R-01-7)

### 16.1 로그 포맷

```json
{
    "ts": "2026-04-13T12:00:00.000Z",
    "level": "INFO",
    "code": "HYB_SEARCH_OK",
    "component": "HybridSearcher",
    "project_id": "proj_abc123",
    "message": "Hybrid search complete: 5/18 candidates, method=weighted_sum, total_ms=42.3",
    "extra": {
        "alpha": 0.7,
        "threshold": 0.75,
        "dense_count": 20,
        "sparse_count": 15,
        "candidates_before_threshold": 18,
        "candidates_after_threshold": 5,
        "fusion_method": "weighted_sum",
        "dense_ms": 15.2,
        "sparse_ms": 8.1,
        "fusion_ms": 1.5,
        "total_ms": 42.3
    }
}
```

### 16.2 로그 레벨 매핑

| 이벤트 | 레벨 | 코드 |
|--------|------|------|
| 검색 성공 | INFO | HYB_SEARCH_OK |
| Sparse 실패 (degraded) | WARNING | HYB_ERR_002 |
| Dense 실패 | ERROR | HYB_ERR_001 |
| α 강제 복원 | WARNING | HYB_ERR_007 |
| Threshold 후 0건 | WARNING | HYB_ERR_005 |
| Config 무효 | ERROR | HYB_ERR_010 |

---

## 17. 시간복잡도 분석 (Big-O)

| 연산 | 시간복잡도 | 설명 |
|------|-----------|------|
| Dense 검색 | O(N × D) | N = 벡터 수 (V1: ~450/프로젝트), D = 차원 (256). Chroma HNSW 인덱스에서 O(log N × D) 근사 |
| Sparse 검색 (BM25) | O(V × L) | V = 어휘 크기, L = 평균 문서 길이. V1 소규모에서 O(N) 근사 |
| 점수 정규화 | O(K) | K = top_k (20) |
| 가중 합산 | O(K₁ + K₂) | K₁ = Dense 결과 수, K₂ = Sparse 결과 수. 합집합 처리 |
| RRF 결합 | O(K₁ + K₂) | 순위 기반 합산 |
| Threshold 필터링 | O(M) | M = 결합 후 후보 수 |
| **전체 (V1)** | **O(N × D + N)** | V1 소규모 데이터: 총 450 벡터/프로젝트, 실측 < 50ms 기대 |

### 17.1 V1 성능 예측

| 시나리오 | 프로젝트당 벡터 수 | 예상 Dense (ms) | 예상 Sparse (ms) | 예상 전체 (ms) |
|---------|------------------|----------------|-----------------|---------------|
| 소규모 | 100 | < 5 | < 3 | < 15 |
| 중규모 | 300 | < 10 | < 5 | < 25 |
| 최대 (V1) | 450 | < 15 | < 8 | < 35 |

---

## 18. 메트릭 수집 포인트

| ID | 메트릭 | 타입 | 단위 | 수집 시점 |
|----|--------|------|------|----------|
| MET-HYB-001 | dense_search_latency | histogram | ms | Dense 검색 완료 |
| MET-HYB-002 | sparse_search_latency | histogram | ms | Sparse 검색 완료 |
| MET-HYB-003 | fusion_latency | histogram | ms | 점수 결합 완료 |
| MET-HYB-004 | total_search_latency | histogram | ms | 전체 Hybrid Search 완료 |
| MET-HYB-005 | candidates_before_threshold | gauge | count | Threshold 적용 전 |
| MET-HYB-006 | candidates_after_threshold | gauge | count | Threshold 적용 후 |
| MET-HYB-007 | threshold_filter_ratio | gauge | ratio | after/before 비율 |
| MET-HYB-008 | dense_only_fallback_count | counter | count | Sparse 실패로 Dense-only 모드 전환 시 |
| MET-HYB-009 | search_error_count | counter | count | 에러 발생 시 (코드별 레이블) |
| MET-HYB-010 | alpha_override_count | counter | count | α 강제 복원 발생 시 |
| MET-HYB-011 | empty_result_count | counter | count | Threshold 후 0건 발생 시 |
| MET-HYB-012 | fusion_method_usage | counter | count | weighted_sum vs rrf 사용 빈도 |

---

## 19. 단위 테스트 시나리오

| ID | 테스트명 | 대상 | 검증 조건 | LOCK |
|----|---------|------|----------|------|
| T-HYB-01 | α=0.7 가중치 검증 | _fuse_weighted_sum | dense=1.0, sparse=1.0 → hybrid=0.7+0.3=1.0 | LOCK-MR-008 |
| T-HYB-02 | α=0.7 비대칭 검증 | _fuse_weighted_sum | dense=1.0, sparse=0.0 → hybrid=0.7 | LOCK-MR-008 |
| T-HYB-03 | α=0.7 역비대칭 검증 | _fuse_weighted_sum | dense=0.0, sparse=1.0 → hybrid=0.3 | LOCK-MR-008 |
| T-HYB-04 | threshold=0.75 통과 | _apply_threshold | hybrid=0.80 → 포함 | LOCK-MR-009 |
| T-HYB-05 | threshold=0.75 차단 | _apply_threshold | hybrid=0.74 → 제외 | LOCK-MR-009 |
| T-HYB-06 | threshold=0.75 경계 | _apply_threshold | hybrid=0.75 → 포함 (>=) | LOCK-MR-009 |
| T-HYB-07 | Dense+Sparse 결합 순위 | search | 3개 후보, 순위 정확성 확인 | — |
| T-HYB-08 | Dense-only 모드 | search | Sparse 빈 결과 → Dense만으로 결합 | — |
| T-HYB-09 | Sparse-only 후보 필터링 | _fuse_weighted_sum | Sparse만 존재 후보 → hybrid < 0.75 → threshold에서 제거 | LOCK-MR-009 |
| T-HYB-10 | 정규화 — 동일 점수 | _normalize_scores | 모든 점수 동일 → 0.5 반환 | — |
| T-HYB-11 | 정규화 — min-max | _normalize_scores | [2, 4, 8] → [0.0, 0.333, 1.0] | — |
| T-HYB-12 | 정규화 — 빈 입력 | _normalize_scores | [] → [] | — |
| T-HYB-13 | project_id 격리 | search | project_id 필수 검증 (ValueError) | LOCK-MR-017 |
| T-HYB-14 | α LOCK 강제 | search | alpha=0.5 전달 → 0.7로 강제 복원 + WARNING | LOCK-MR-008 |
| T-HYB-15 | HybridSearchConfig LOCK 검증 | HybridSearchConfig | alpha=0.6 → ValueError | LOCK-MR-008 |
| T-HYB-16 | HybridSearchConfig threshold LOCK | HybridSearchConfig | threshold=0.5 → ValueError | LOCK-MR-009 |
| T-HYB-17 | RRF 결합 | _fuse_rrf | 2개 검색 결과 → RRF 점수 정확성 | — |
| T-HYB-18 | RRF threshold 비적용 | search (rrf) | RRF 모드에서 threshold 미적용 확인 | — |
| T-HYB-19 | Graceful degradation | search | Sparse 예외 → Dense-only 계속 | — |
| T-HYB-20 | Dense 실패 → 에스컬레이션 | search | Dense 예외 → HybridSearchError 발생 | — |
| T-HYB-21 | Threshold 후 0건 | search | 모든 후보 < 0.75 → 빈 리스트 + WARNING | LOCK-MR-009 |
| T-HYB-22 | 메트릭 수집 | search | dense_ms, sparse_ms, total_ms 양수 확인 | — |
| T-HYB-23 | P1-10 시그니처 정합 | search | P1-10 §7.3 호출 시그니처와 일치 | — |
| T-HYB-24 | 대규모 결과 결합 | _fuse_weighted_sum | Dense 20 + Sparse 20 → 합집합 정확 | — |
| T-HYB-25 | 로깅 R-01-7 준수 | _log | 구조화 로그 출력 검증 | — |

---

## 20. Phase 2 통합 테스트

| ID | 테스트명 | 관련 세션 | 검증 조건 |
|----|---------|----------|----------|
| P2-T-HYB-01 | RAG Pipeline E2E — Hybrid Search 경유 | P1-10 | Stage 1~6 전체 파이프라인에서 Stage 5 Hybrid Search 정상 동작 |
| P2-T-HYB-02 | Semantic Cache 히트 시 Hybrid Search 바이패스 | P1-5 | cache_hit=True 시 HybridSearcher 미호출 확인 |
| P2-T-HYB-03 | ChromaVectorStore Dense + BM25 Sparse 통합 | P1-3 | 실제 Chroma 인덱스 + BM25 인덱스에서 결합 검색 |
| P2-T-HYB-04 | Cross-Encoder Rerank 후 최종 순위 | P1-10 | Hybrid → Threshold → Rerank Top-5 정확성 |
| P2-T-HYB-05 | project_id 격리 통합 | P1-1, P1-2 | 프로젝트 A 검색 시 프로젝트 B 결과 미포함 |
| P2-T-HYB-06 | PII 마스킹 후 Hybrid Search | P1-7 | restrict 데이터 마스킹 후 검색 가능 확인 |
| P2-T-HYB-07 | GraphRAG 컨텍스트 보강 통합 | P1-4 | Hybrid → Rerank → GraphRAG traverse 체인 |
| P2-T-HYB-08 | DCL 수집 → 벡터 저장 → Hybrid 검색 E2E | P1-9 | DCL 문서 수집 → Chroma+BM25 저장 → Hybrid 검색 |
| P2-T-HYB-09 | Sparse 장애 시 Graceful Degradation | P1-3 | BM25 인덱스 손상 → Dense-only 검색 정상 |
| P2-T-HYB-10 | 다중 프로젝트 동시 검색 | P1-2 | 프로젝트 3개 동시 Hybrid Search — 격리 확인 |
| P2-T-HYB-11 | 메트릭 → SDAR 연동 | 6-5 | MET-HYB-001~012 메트릭이 SDAR 대시보드에 표시 |
| P2-T-HYB-12 | 감사 로그 → Event-Logging 연동 | 6-12 | Hybrid Search 로그가 6-12 Event-Logging에 전달 |

---

## 21. 세션 간 인터페이스 cross-check

| 세션 | 파일 | 본 문서 접점 | 인터페이스 정합 |
|------|------|-------------|---------------|
| **P0-3** | `chroma_collection_strategy.md` | §5.1 Hybrid Search 파라미터 | α=0.7, threshold=0.75, Top-K=20 **일치** |
| **P0-4** | `vectorstore_abc.py` | §5 Dense — VectorStoreABC.search() | search(query_vector, project_id, top_k, filters) **일치** |
| **P1-1** | `L0_session_memory_crud.md` | §20 P2-T-HYB-05 — L0 project_id 격리 | project_id 필수 **일치** |
| **P1-2** | `L1_project_memory_crud.md` | §20 P2-T-HYB-05/10 — L1 프로젝트 격리 | project_id 필수 **일치** |
| **P1-3** | `chroma_adapter.md` | §5 Dense — ChromaVectorStore.search(), §6 Sparse — BM25IndexManager.search() | search() 시그니처 **일치**, BM25IndexManager.search(project_id, query, top_k) **일치** |
| **P1-4** | `json_graphrag.md` | §12.3 Stage 5 → GraphRAG 통합 | traverse(project_id, start_node_id, max_hops=2) **일치** |
| **P1-5** | `semantic_cache.md` | §2.2 캐시 히트 시 바이패스 | get(query_text, project_id) → cache_hit **일치** |
| **P1-7** | `pii_masking.md` | §20 P2-T-HYB-06 — PII 마스킹 후 검색 | mask(text) → MaskResult **일치** |
| **P1-9** | `dcl_basic.md` | §20 P2-T-HYB-08 — DCL → 검색 E2E | dcl_collector → Stage 1 **일치** |
| **P1-10** | `rag_6stage_pipeline.md` | §12 Stage 5 통합 — HybridSearcher.search() 시그니처 | search(query_vector, query_text, project_id, top_k, alpha) **일치** |

---

## 22. LOCK-MR 참조 추적표

| LOCK ID | 항목 | 본 문서 준수 위치 | 위반 여부 |
|---------|------|-----------------|----------|
| LOCK-MR-008 | Hybrid Search α=0.7 | §3 HybridSearchConfig.alpha=0.7, §8 가중 합산 공식, §11 LOCK 강제 | **무위반** |
| LOCK-MR-009 | Similarity threshold=0.75 | §3 HybridSearchConfig.threshold=0.75, §9 필터링, §11 _apply_threshold | **무위반** |
| LOCK-MR-011 | BGE-M3 256dim 검색용 | §5.1 query_vector=256dim | **무위반** |
| LOCK-MR-012 | V1 Chroma | §5 Dense 검색 백엔드 = ChromaVectorStore | **무위반** |
| LOCK-MR-014 | VectorStore 4메서드 | §5 search() 활용 | **무위반** |
| LOCK-MR-015 | Deny 벡터 삽입 금지 | §12.3 인덱스 대상 제외 (upsert 시 P1-3 검사) | **무위반** |
| LOCK-MR-017 | project_id 격리 | §5 Dense project_id 필터, §6 Sparse project_id 격리, §11 ValueError | **무위반** |
| LOCK-MR-019 | 루프 저장 폭주 방지 | §6 BM25 인덱스 대상 = content_summary (요약만) | **무위반** |

---

## 23. 교차 참조 블록

### 23.1 선행 세션 산출물

| 세션 | 파일 | 경로 |
|------|------|------|
| P0-3 | chroma_collection_strategy.md | `03_vector-db/chroma_collection_strategy.md` |
| P0-4 | vectorstore_abc.py | `03_vector-db/vectorstore_abc.py` |
| P1-1 | L0_session_memory_crud.md | `01_memory-hierarchy/L0_session_memory_crud.md` |
| P1-2 | L1_project_memory_crud.md | `01_memory-hierarchy/L1_project_memory_crud.md` |
| P1-3 | chroma_adapter.md | `03_vector-db/chroma_adapter.md` |
| P1-4 | json_graphrag.md | `02_rag-pipeline/json_graphrag.md` |
| P1-5 | semantic_cache.md | `04_memory-distillation/semantic_cache.md` |
| P1-7 | pii_masking.md | `04_memory-distillation/pii_masking.md` |
| P1-9 | dcl_basic.md | `02_rag-pipeline/dcl_basic.md` |
| P1-10 | rag_6stage_pipeline.md | `02_rag-pipeline/rag_6stage_pipeline.md` |

### 23.2 후속 세션 접점

| 세션 | 내용 | 본 문서 접점 |
|------|------|-------------|
| P1-12 | (종합계획서 확인 필요) | — |

### 23.3 인접 도메인 접점

| 도메인 | 접점 | 본 문서 위치 |
|--------|------|-------------|
| 5-2 File-Context | 청킹/검색 전략·알고리즘 설계 (What) vs 6-4 실행 인프라 (How) | §12.3 Stage 2 통합 |
| 6-2 Security | PII 마스킹 정책 | §20 P2-T-HYB-06 |
| 6-5 SDAR | 메트릭 소비 | §18 MET-HYB-001~012 |
| 6-12 Event-Logging | 감사 로그 | §16 로깅 규격 |

---

*End of Document*
