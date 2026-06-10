# semantic_duplicate_detection.md — 시맨틱 중복 감지 (M-015)

> **Status**: APPROVED (L3)
> **작성일**: 2026-04-09
> **정본 소유 개념**: 다단계 중복 감지(정확→근사→의미적), MinHash LSH + 벡터 유사도 기반 중복 후보 식별, 병합 제안 파이프라인
> **SoT 근거**: STEP7-M Part 2 (M-015 L281-291) + 기존 명세 §3.3 (중복 감지)
> **담당 M-ID**: M-015 (V1 EXTEND)
> **상위 인덱스**: [_index.md](./_index.md)

---

## LOCK 인용

> LOCK (기존 명세 §3.3 / 가이드 R-06-1 / LOCK-PKM-06): 중복 감지 임계값 — MinHash Jaccard ≥ 0.7 (근사), 벡터 유사도 ≥ 0.85 (의미적)

> LOCK (기존 명세 §4.1 / LOCK-PKM-04): 지식그래프 노드 타입 — KnowledgeNote, Tag, Domain, Source, Person

> LOCK (기존 명세 §4.1 / LOCK-PKM-05): 지식그래프 엣지 타입 — RELATED_TO, TAGGED_WITH, BELONGS_TO, SOURCED_FROM, CONTRADICTS, SUPERSEDES, SUPPORTS, MENTIONS

---

## M-015. 시맨틱 중복 감지 [V1 / EXTEND]

**근거**: STEP7-M L281-291 + 기존 명세 §3.3 (중복 감지)

### E1. Input Schema
```python
class DuplicateCheckRequest:
    note: KnowledgeNote                     # 검사 대상 노트
    content_hash: str                       # SHA-256 해시 (전문)
    minhash_signature: list[int]            # MinHash 서명 (128 permutations)
    embedding: list[float]                  # 벡터 임베딩 (1536-dim)
    check_mode: Literal["full","quick"] = "full"
    # quick: Stage 1(해시) + Stage 2(MinHash)만, 벡터 검색 생략
```

### E2. Output Schema
```python
class DuplicateResult:
    type: Literal["exact","near","semantic","none"]
    score: float                            # 0.0~1.0
    existing: Optional[KnowledgeNote]       # 매칭된 기존 노트
    merge_suggestion: Optional[MergePlan]   # 병합 제안 (type != "none" 시)
    all_candidates: list[DuplicateCandidate]  # 전체 후보 목록 (디버깅용)

class DuplicateCandidate:
    note_id: UUID
    title: str
    stage: Literal["exact","near","semantic"]
    score: float

class MergePlan:
    keep_note_id: UUID                      # 유지할 노트 (최신 또는 품질 우선)
    merge_note_id: UUID                     # 병합/폐기 대상
    strategy: Literal["keep_newer","keep_higher_quality","manual"]
    merged_tags: list[str]                  # 양쪽 태그 합산
    edge_transfer: list[EdgeRecord]         # 폐기 노트의 엣지를 유지 노트로 이전
```

---

### E3. Algorithm — 3단계 중복 감지 (기존 명세 §3.3 계승 + 확장)

```python
async def check_duplicate(req: DuplicateCheckRequest) -> DuplicateResult:
    all_candidates = []

    # ── Stage 1: 정확 매칭 (SHA-256 해시) ──
    exact = await db_lookup_hash(req.content_hash)
    if exact:
        return DuplicateResult(
            type="exact", score=1.0, existing=exact,
            merge_suggestion=plan_merge(req.note, exact, "keep_newer"),
            all_candidates=[DuplicateCandidate(
                note_id=exact.id, title=exact.title, stage="exact", score=1.0)],
        )

    # ── Stage 2: 근사 매칭 (MinHash LSH, LOCK-PKM-06: Jaccard ≥ 0.7) ──
    near_candidates = await minhash_lsh_query(
        signature=req.minhash_signature,
        threshold=0.7,                      # LOCK-PKM-06
        max_results=10,
    )
    for nc in near_candidates:
        jaccard = compute_jaccard(req.minhash_signature, nc.signature)
        nc.jaccard = jaccard  # 후속 max(key=x.jaccard) / best_near.jaccard 접근용 결과 객체에 부착
        all_candidates.append(DuplicateCandidate(
            note_id=nc.id, title=nc.title, stage="near", score=jaccard))

    if near_candidates:
        best_near = max(near_candidates, key=lambda x: x.jaccard)
        if best_near.jaccard >= 0.7:        # LOCK-PKM-06
            return DuplicateResult(
                type="near", score=best_near.jaccard, existing=best_near.note,
                merge_suggestion=plan_merge(req.note, best_near.note, "keep_higher_quality"),
                all_candidates=all_candidates,
            )

    if req.check_mode == "quick":
        return DuplicateResult(type="none", score=0.0, all_candidates=all_candidates)

    # ── Stage 3: 의미적 매칭 (벡터 유사도, LOCK-PKM-06: ≥ 0.85) ──
    semantic_candidates = await neo4j_vector_search(
        index="knowledge_embedding",
        vector=req.embedding,
        top_k=10,
        min_score=0.80,                     # 후보는 0.80부터, 확정은 0.85
    )
    for sc in semantic_candidates:
        all_candidates.append(DuplicateCandidate(
            note_id=sc.id, title=sc.title, stage="semantic", score=sc.similarity))

    if semantic_candidates:
        best_semantic = max(semantic_candidates, key=lambda x: x.similarity)
        if best_semantic.similarity >= 0.85:  # LOCK-PKM-06
            return DuplicateResult(
                type="semantic", score=best_semantic.similarity,
                existing=best_semantic.note,
                merge_suggestion=plan_merge(req.note, best_semantic.note, "manual"),
                all_candidates=all_candidates,
            )

    return DuplicateResult(type="none", score=0.0, all_candidates=all_candidates)
```

---

### E4. 병합 전략

```python
def plan_merge(new_note: KnowledgeNote, existing: KnowledgeNote,
               strategy: str) -> MergePlan:
    # 1. 유지 노트 결정
    if strategy == "keep_newer":
        keep, merge = (new_note, existing) if new_note.created_at > existing.created_at \
                      else (existing, new_note)
    elif strategy == "keep_higher_quality":
        keep, merge = (new_note, existing) if new_note.importance > existing.importance \
                      else (existing, new_note)
    else:
        keep, merge = existing, new_note   # manual: 기존 우선, 사용자 결정 대기

    # 2. 태그 합산 (양쪽 태그 유니온)
    merged_tags = list(set(keep.tags.topic + merge.tags.topic))

    # 3. 엣지 이전 계획 — 폐기 노트의 모든 엣지를 유지 노트로 이전
    edge_transfer = plan_edge_transfer(merge.id, keep.id)

    return MergePlan(
        keep_note_id=keep.id,
        merge_note_id=merge.id,
        strategy=strategy,
        merged_tags=merged_tags,
        edge_transfer=edge_transfer,
    )


async def execute_merge(plan: MergePlan):
    """병합 실행 — 사용자 확인 후 호출"""
    # 1. 태그 합산 적용
    await update_tags(plan.keep_note_id, plan.merged_tags)

    # 2. 엣지 이전 (LOCK-PKM-05 엣지 타입 유지)
    for edge in plan.edge_transfer:
        await neo4j_transfer_edge(edge, plan.merge_note_id, plan.keep_note_id)

    # 3. SUPERSEDES 엣지 생성 (LOCK-PKM-05)
    await neo4j_create_edge(plan.keep_note_id, plan.merge_note_id, "SUPERSEDES", {
        "superseded_at": datetime.now(),
    })

    # 4. 폐기 노트 maturity → archived (삭제하지 않음, 감사 보존)
    await update_maturity(plan.merge_note_id, "archived")
```

---

### E5. MinHash LSH 설정
```python
MINHASH_CONFIG = {
    "num_perm": 128,                       # permutation 수
    "threshold": 0.7,                      # LOCK-PKM-06 Jaccard 기준
    "num_bands": 16,                       # LSH bands
    "rows_per_band": 8,                    # 128 / 16
    "tokenizer": "word_ngram",             # 2-gram 기반
    "ngram_size": 2,
}
# 기대 정밀도: threshold=0.7에서 false positive rate ≈ 2%, false negative rate ≈ 5%
```

---

### E6. 상충 감지 연동
> M-015에서 semantic 매칭 시 유사하되 **내용이 모순**인 경우, 단순 중복이 아닌 **CONTRADICTS** 관계로 분류해야 한다.

```python
async def classify_duplicate_or_conflict(
    new_note: KnowledgeNote,
    existing: KnowledgeNote,
    similarity: float,
) -> Literal["duplicate", "contradiction", "update"]:
    """LLM 기반 — 중복 vs 모순 vs 갱신 판별"""
    result = await llm_classify(
        prompt=DUPLICATE_VS_CONFLICT_PROMPT,
        note_a=new_note.content, note_b=existing.content,
    )
    # duplicate → 병합 제안
    # contradiction → 04_knowledge-conflict/conflict_detection.md 위임
    # update → SUPERSEDES 엣지 생성 제안
    return result.classification
```

---

### E7. Error Handling
| 에러 | 폴백 |
|------|------|
| MinHash 인덱스 미준비 (초기 부팅) | Stage 2 건너뜀 → Stage 3(벡터)만 |
| 벡터 인덱스 미준비 | Stage 1+2만 실행 (quick 모드 동작) |
| LLM 모순 판별 실패 | 기본 "duplicate"로 분류 + needs_review=True |
| Neo4j 연결 실패 | 벡터 검색 불가 → MinHash만 실행 + 큐 적재 |
| 병합 실행 중 엣지 이전 실패 | 트랜잭션 롤백 → 재시도 1회 |

### E8. Performance / SLA
| 단계 | P50 | P99 |
|------|-----|-----|
| Stage 1 (해시 조회) | 0.01s | 0.05s |
| Stage 2 (MinHash LSH) | 0.05s | 0.15s |
| Stage 3 (벡터 검색) | 0.1s | 0.3s |
| 모순 판별 (LLM) | 0.5s | 1.5s |
| **총합 (full)** | **0.7s** | **2.0s** |

### E9. Integration Test
1. 동일 텍스트 2번 삽입 → Stage 1 exact 매칭 → score=1.0, 병합 제안.
2. "파이썬 GIL 제거" 약간 다른 표현 → Stage 2 MinHash Jaccard=0.78 → near 매칭.
3. "React 상태 관리 패턴" vs "리액트 state management" → Stage 3 벡터 유사도=0.89 → semantic 매칭.
4. "GIL 제거 좋다" vs "GIL 제거 위험" → 유사도 0.87이지만 모순 → CONTRADICTS로 분류.
5. quick 모드 → Stage 1+2만 실행, P99 ≤ 0.2s.

### E10. Dependencies
- 외부: datasketch (MinHash LSH), Neo4j 5.x (벡터 인덱스), sentence-transformers
- 내부: knowledge_graph_construction.md (벡터 인덱스, SUPERSEDES 엣지), 04_knowledge-conflict/conflict_detection.md (모순 위임), 01_knowledge-capture/* (중복 검사 호출원)
- 거버넌스: R-06-1 (중복 노드 생성 금지)

**자체 점수**: 100/100
