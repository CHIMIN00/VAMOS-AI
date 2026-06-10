# graph_reasoning.md — 그래프 추론 (M-032)

> **Status**: SKELETON (V2)
> **작성일**: 2026-04-09
> **담당 M-ID**: M-032 (V2)
> **상위 인덱스**: [_index.md](./_index.md)
> **SoT 근거**: STEP7-M Part 3 (M-032 L561-571)

---

## 범위 요약

- **V2**: 경로 추론 (A→B→C 관계), 유사 패턴 감지, 누락 관계 예측, 이상 감지

## LOCK 참조 (작성 시 적용)

> LOCK-PKM-04 (노드 타입), LOCK-PKM-05 (엣지 타입)

## 핵심 의존성

- knowledge_graph_construction.md (Neo4j GDS 라이브러리)
- ontology_construction.md (온톨로지 기반 추론)

---

*V2 L3 작성은 Phase 2에서 진행 예정.*

---

# §V2 (M-032 그래프 추론)

> **V2 APPROVED (L3)** — 2026-04-23 STEP_B #2a 세션 2-2
> **V1 본문 append-only 준수**: 위 V1 body 26줄 불변, 본 §V2 섹션만 신규 추가

## §V2.1 교차 참조 블록

| # | 종류 | 대상 | 역할 |
|---|------|------|------|
| #1 | 상위 SoT | `sot/STEP7-M_PKM_지식관리_작업가이드.md` Part 3 L561-571 | M-032 요구사항 원천 |
| #2 | 권한 체인 | `AUTHORITY_CHAIN.md` §2 (LOCK-PKM-04/05) | 노드/엣지 타입 정본 |
| #3 | 동일 폴더 | `knowledge_graph_construction.md` (M-012) | Neo4j GDS 라이브러리 기반 |
| #4 | 동일 폴더 | `ontology_construction.md` (M-031) | 온톨로지 기반 추론 규칙 |
| #5 | 동일 폴더 | `graph_query_language.md` (M-033) | Cypher 쿼리 발행 계층 |
| #6 | 동일 폴더 | `graph_visualization.md` (M-034) | 추론 결과 시각화 공유 |
| #7 | 동일 폴더 | `graph_recommendation.md` (M-038) | 경로 추론 기반 추천 재사용 |
| #8 | 타 폴더 | `04_knowledge-conflict/conflict_detection.md` | 모순 탐지 결과 전달 |

## §V2.2 LOCK 인용 (verbatim)

> LOCK (기존 명세 §4.1 / LOCK-PKM-04): 지식그래프 노드 타입 — KnowledgeNote, Tag, Domain, Source, Person — **기존 타입 보호, 확장(추가)만 가능**

> LOCK (기존 명세 §4.1 / LOCK-PKM-05): 지식그래프 엣지 타입 — RELATED_TO, TAGGED_WITH, BELONGS_TO, SOURCED_FROM, CONTRADICTS, SUPERSEDES, SUPPORTS, MENTIONS — **기존 타입 보호, 확장(추가)만 가능**

**본 §V2는 기존 5 노드 + 8 엣지 타입을 소비만 한다 (재정의 ❌, 확장 ❌). 추론 결과는 기존 엣지 타입 위에 `inferred=true` 속성으로 마킹한다.**

## §V2.3 공통 자료 구조 재사용 (출처: 3-3 PKM `knowledge_graph_construction.md` §E1)

```python
# 출처: 02_knowledge-graph/knowledge_graph_construction.md §E1 노드/엣지 스키마
# 본 §V2는 재정의 없이 참조만 수행
class KnowledgeNote: ...     # LOCK-PKM-04 (5 노드 중 1개)
class EdgeRelated: ...       # LOCK-PKM-05 RELATED_TO
class EdgeContradicts: ...   # LOCK-PKM-05 CONTRADICTS
```

시간 복잡도:
- 경로 추론 (k-hop): O(|V| + |E|·b^k), b=분지수, k=홉수. 실무 k≤4 제한.
- 유사 패턴 매칭: Weisfeiler-Lehman O(k·|V|+|E|), 커뮤니티 감지 Louvain O(n·log n)
- 누락 관계 예측: Adamic-Adar / TransE — 임베딩 공간 근사 kNN O(log n)
- 모순 탐지: Rule engine O(|V|·r), r=규칙 수

## §V2.4 멀티홉 경로 추론

```python
from dataclasses import dataclass
from typing import Literal
from uuid import UUID

@dataclass
class MultiHopPath:
    start_node_id: UUID           # KnowledgeNote
    end_node_id: UUID             # KnowledgeNote / Domain / Tag
    hops: list[tuple[UUID, str]]  # [(node_id, edge_type), ...] edge_type ∈ LOCK-PKM-05 8종
    path_length: int              # = len(hops), 제한 ≤ 4 (b^k 폭발 방지)
    confidence: float             # 0~1, 엣지 가중치 누적
    inferred_relation: Literal["RELATED_TO","SUPPORTS","CONTRADICTS","SUPERSEDES"]

def infer_path(graph, start: UUID, end: UUID, max_hops: int = 4) -> list[MultiHopPath]:
    """
    Cypher 쿼리:
      MATCH p = (a:KnowledgeNote {id:$start})-[*1..$k]-(b:KnowledgeNote {id:$end})
      WHERE ALL(r IN relationships(p) WHERE type(r) IN $allowed_types)
      RETURN p ORDER BY length(p) LIMIT 100
    """
    ...
```

**신뢰도 전파 공식** (Belief Propagation 변형, IMPL-DETAIL):
```
confidence(path) = ∏ |edge_weight[i]|  (i=0..path_length-1)  # 크기(절댓값)만 사용 → confloat(ge=0,le=1) 보장; 모순 극성(부호)은 inferred_relation으로 별도 추적
edge_weight[i] = base_weight[edge_type] × freshness_score[target_node] × (1 - age_decay)
base_weight = {
    RELATED_TO: 0.60, TAGGED_WITH: 0.55, BELONGS_TO: 0.80,
    SOURCED_FROM: 0.75, SUPPORTS: 0.90, MENTIONS: 0.50,
    CONTRADICTS: -0.85, SUPERSEDES: 0.70
}
```

## §V2.5 유사 패턴 매칭 (유추 엔진)

- 서브그래프 동형성 완화 버전: Weisfeiler-Lehman 커널 k≤3 (정확 매칭은 NP-hard → 근사)
- 노드 구조 임베딩: node2vec (dim=128, window=5, p=1, q=1) — M-035 하이브리드 검색 공유
- 패턴 예시: "A가 B에 도움이 되었다 (SUPPORTS)" + "A 유사 C 존재" → "C는 B와 유사한 D에 도움 가능성"
- 유사도 임계: cosine ≥ 0.80 (AUTHORITY §10.3 IMPL-DETAIL, LOCK-PKM-06 참조만)

## §V2.6 누락 관계 예측

```python
@dataclass
class MissingEdgePrediction:
    src_id: UUID
    dst_id: UUID
    predicted_type: str           # LOCK-PKM-05 8종 중 하나
    score: float                  # 0~1
    model: Literal["adamic_adar","trans_e","graph_sage"]
    suggested_action: Literal["auto_create","user_confirm","discard"]
    threshold_hit: bool           # score ≥ auto_create_threshold (기본 0.90)
```

- 자동 생성 threshold: ≥ 0.90 → `auto_create` (감사 로그 남김)
- 사용자 확인 threshold: 0.70 ≤ score < 0.90 → `user_confirm` (UI 배지)
- 미만: `discard`

## §V2.7 모순 탐지

규칙 엔진 (Cypher + Python hybrid):

```cypher
// 규칙 R1: 명시적 CONTRADICTS 엣지
MATCH (a:KnowledgeNote)-[:CONTRADICTS]->(b:KnowledgeNote)
WHERE a.maturity IN ['evergreen','growing'] AND b.maturity IN ['evergreen','growing']
RETURN a, b

// 규칙 R2: 동일 Domain 내 상반 태그 감정값
MATCH (a:KnowledgeNote)-[:BELONGS_TO]->(d:Domain)<-[:BELONGS_TO]-(b:KnowledgeNote)
WHERE a.id <> b.id
  AND has_opposite_sentiment_tags(a, b)
  AND similarity(a.embedding, b.embedding) > 0.75
RETURN a, b
```

규칙 추가 시 LOCK-PKM-04/05 재정의 없음 — 기존 엣지 타입 위에 쿼리만 확장.

## §V2.8 이상 감지

- 그래프 중심성 급변 (PageRank delta > 3σ over 30일)
- 고립 노드 급증 (orphan ratio > 10%)
- 특정 태그 engagement 0 (사용된 적 없는 태그 30일 경과)

## §V2.9 에스컬레이션 Pydantic

```python
from pydantic import BaseModel, Field, confloat, conint
from typing import Literal

class GraphReasoningEscalation(BaseModel):
    reasoning_type: Literal["multihop","analogy","missing_edge","contradiction","anomaly"]
    severity: Literal["info","warning","error","critical"]
    reason: Literal[
        "path_explosion_detected",
        "contradiction_unresolved",
        "orphan_ratio_spike",
        "embedding_staleness_gt_90d",
        "missing_edge_auto_create_blocked",
    ]
    confidence_observed: confloat(ge=0.0, le=1.0)
    hop_count: conint(ge=0, le=8)
    context: dict
    requires_user_review: bool = True
```

## §V2.10 로깅 (structured JSON 3-block)

```json
{"event":"graph_reasoning.multihop_inferred","start_id":"...","end_id":"...","path_length":3,"confidence":0.78,"duration_ms":120}
```

```json
{"event":"graph_reasoning.contradiction_detected","pair":["A-id","B-id"],"rule":"R2","similarity":0.82,"action":"escalate"}
```

```json
{"event":"graph_reasoning.missing_edge_predicted","src":"...","dst":"...","type":"RELATED_TO","score":0.92,"action":"auto_create"}
```

## §V2.11 Phase 3 테스트 시나리오 (10건)

| # | 시나리오 | 기대 | LOCK |
|---|---------|------|------|
| T1 | A→B→C 3-hop 추론 | path_length=3, confidence > 0.4 | §V2.4 |
| T2 | k=5 경로 요청 (제한 초과) | `path_explosion_detected` escalation | §V2.9 |
| T3 | 유사 패턴 top-5 검색 | cosine ≥ 0.80 결과만 반환 | §V2.5 |
| T4 | Missing edge score 0.95 | `auto_create=True` + 감사 로그 | §V2.6 |
| T5 | Missing edge score 0.78 | `user_confirm` UI 배지 | §V2.6 |
| T6 | 명시적 CONTRADICTS 엣지 존재 | 모순 목록에 포함 | §V2.7 R1 |
| T7 | 동일 Domain 상반 감정 태그 2 노트 | R2 매칭 | §V2.7 R2 |
| T8 | PageRank Δ > 3σ 노드 감지 | 이상 목록 포함 | §V2.8 |
| T9 | LOCK-PKM-04 신규 노드 타입 추가 시도 | [VIOLATION:LOCK-PKM-04_redefinition] abort | §V2.2 |
| T10 | 신뢰도 전파 공식 검증 | 수식 결과 ±0.001 일치 | §V2.4 |

## §V2.12 LOCK 5필드 매핑표

| LOCK ID | 항목 | 정본 출처 | 값 | 재정의 |
|---------|------|-----------|-----|--------|
| LOCK-PKM-04 | 그래프 노드 타입 | 기존 명세 §4.1 | KnowledgeNote, Tag, Domain, Source, Person | ❌ |
| LOCK-PKM-05 | 그래프 엣지 타입 | 기존 명세 §4.1 | RELATED_TO, TAGGED_WITH, BELONGS_TO, SOURCED_FROM, CONTRADICTS, SUPERSEDES, SUPPORTS, MENTIONS | ❌ |

## §V2.13 피어 cross-check

| V2 피어 | 공유 계약 | 상태 |
|---------|-----------|------|
| `graph_visualization.md` §V2 | 추론 결과 → inferred 엣지 시각 마킹 | 계약 확정 |
| `graph_recommendation.md` §V2 | 경로 추론 → 학습 경로 추천 | 재사용 |
| `graph_maintenance.md` §V2 | missing_edge `auto_create` → 유지보수 타임라인 | 감사 로그 연동 |

## §V2.14 자가 체크리스트

- [x] LOCK-PKM-04/05 verbatim 인용 (§V2.2)
- [x] STEP7-M M-032 L561-571 line refs
- [x] 공통 스키마 출처 (§V2.3)
- [x] 멀티홉 경로 추론 공식 (§V2.4)
- [x] 유추 / 누락 관계 / 모순 / 이상 4 기능 전수 (§V2.5~§V2.8)
- [x] 에스컬레이션 Pydantic (§V2.9)
- [x] 로깅 3-block (§V2.10)
- [x] Phase 3 테스트 10건 (§V2.11)
- [x] LOCK 매핑표 (§V2.12)
- [x] 피어 cross-check (§V2.13)
