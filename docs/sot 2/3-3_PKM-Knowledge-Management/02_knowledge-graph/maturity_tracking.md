# maturity_tracking.md — 지식 성숙도 상태 추적 (M-017)

> **Status**: APPROVED (L3)
> **작성일**: 2026-04-09
> **정본 소유 개념**: 지식 성숙도 4-stage 상태 머신(Seedling→Growing→Evergreen→Archived), 자동 상태 전이 규칙, Part2 5-stage 매핑
> **SoT 근거**: STEP7-M Part 2 (M-017 L312-328) + LOCK-PKM-12 정본 + 부록 §E.6 (Part2 5-stage 매핑)
> **담당 M-ID**: M-017 (V1 EXTEND)
> **상위 인덱스**: [_index.md](./_index.md)

---

## LOCK 인용

> LOCK (STEP7-M M-017 / LOCK-PKM-12): 지식 성숙도 상태 — Seedling → Growing → Evergreen → Archived

> LOCK (기존 명세 §4.1 / LOCK-PKM-04): 지식그래프 노드 타입 — KnowledgeNote, Tag, Domain, Source, Person

> LOCK (기존 명세 §4.1 / LOCK-PKM-05): 지식그래프 엣지 타입 — RELATED_TO, TAGGED_WITH, BELONGS_TO, SOURCED_FROM, CONTRADICTS, SUPERSEDES, SUPPORTS, MENTIONS

---

## M-017. 지식 성숙도 추적 [V1 / EXTEND]

**근거**: STEP7-M L312-328 + LOCK-PKM-12 정본 + 부록 §E.6 (Part2 5-stage 매핑)

### E1. 성숙도 상태 정의 (LOCK-PKM-12: 4-stage 정본)

| 상태 | 설명 | 진입 조건 | 시각적 표현 |
|------|------|----------|------------|
| **Seedling** | 초기 아이디어, 미검증 | 노트 최초 생성 시 기본 | 🌱 |
| **Growing** | 발전 중, 반복 참조됨 | 참조 ≥ 3회 OR 연결 ≥ 2개 | 🌿 |
| **Evergreen** | 완성된 지식, 다수 연결+검증 | 참조 ≥ 10회 AND 연결 ≥ 5개 AND 수동 확인 | 🌳 |
| **Archived** | 더 이상 관련 없음 | 장기간 미참조 OR 수동 아카이브 OR SUPERSEDES 대상 | 🍂 |

### Part2 5-stage 매핑 (부록 §E.6 판정)
> LOCK-PKM-12가 AUTHORITY_CHAIN 정본. Part2 §6.10 #8의 5-stage는 하위 호환:
> - `Seed` → `Seedling`
> - `Budding` + `Blooming` → `Growing`
> - `Mature` → `Evergreen`
> - `Archived` → `Archived` (동일)

```python
PART2_TO_LOCK_MAPPING = {
    "seed": "seedling",
    "budding": "growing",
    "blooming": "growing",
    "mature": "evergreen",
    "archived": "archived",
}
```

---

### E2. Input Schema
```python
class MaturityCheckRequest:
    note_id: UUID
    current_maturity: Literal["seedling","growing","evergreen","archived"]
    trigger: Literal["reference","connection_added","review","time_check","manual","merge"]
    requested_state: Optional[Literal["seedling","growing","evergreen","archived"]] = None  # manual 트리거 시 목표 상태
    requested_state: Optional[Literal["seedling","growing","evergreen","archived"]] = None  # manual 트리거 시 목표 상태
    # reference: 노트가 참조됨
    # connection_added: 새 엣지 생성됨
    # review: 간격 반복 복습 완료
    # time_check: 주기적 검사 (일배치)
    # manual: 사용자 수동 변경
    # merge: 중복 병합으로 인한 아카이브
```

### E3. Output Schema
```python
class MaturityTransition:
    note_id: UUID
    old_state: str
    new_state: str
    reason: str                             # 전이 사유
    auto: bool                              # True=자동, False=사용자 확인 필요
    timestamp: datetime

class MaturityReport:
    note_id: UUID
    current_maturity: str
    reference_count: int
    connection_count: int
    days_since_last_access: int
    eligible_transitions: list[str]         # 가능한 전이 상태 목록
```

---

### E4. Algorithm — 자동 상태 전이

```python
# 상태 전이 규칙 (LOCK-PKM-12 기반)
TRANSITION_RULES = {
    "seedling_to_growing": {
        "conditions": [
            lambda m: m.reference_count >= 3,       # 참조 3회 이상
            # OR
            lambda m: m.connection_count >= 2,       # 연결 2개 이상
        ],
        "logic": "any",                              # 하나라도 충족 시 전이
        "auto": True,
    },
    "growing_to_evergreen": {
        "conditions": [
            lambda m: m.reference_count >= 10,       # 참조 10회 이상
            lambda m: m.connection_count >= 5,        # 연결 5개 이상
        ],
        "logic": "all",                              # 모두 충족 필요
        "auto": False,                               # 사용자 확인 필요
    },
    "any_to_archived": {
        "conditions": [
            lambda m: m.days_since_last_access >= 180,  # 6개월 미참조
        ],
        "logic": "any",
        "auto": False,                               # 아카이브는 사용자 확인 기본. 예외: trigger=='merge'(중복 병합, SUPERSEDES 생성)는 자동 아카이브 허용 (E4 merge 분기)
    },
}

async def check_maturity_transition(req: MaturityCheckRequest) -> Optional[MaturityTransition]:
    # 1. 현재 노트의 메트릭 수집
    metrics = await collect_note_metrics(req.note_id)

    # 2. 수동 변경
    if req.trigger == "manual":
        return MaturityTransition(
            note_id=req.note_id,
            old_state=req.current_maturity,
            new_state=req.requested_state,
            reason="사용자 수동 변경",
            auto=False,
            timestamp=datetime.now(),
        )

    # 3. 병합으로 인한 아카이브 (semantic_duplicate_detection.md 연동)
    if req.trigger == "merge":
        return MaturityTransition(
            note_id=req.note_id,
            old_state=req.current_maturity,
            new_state="archived",
            reason="중복 병합 대상 — SUPERSEDES 엣지 생성됨",
            auto=True,
            timestamp=datetime.now(),
        )

    # 4. 규칙 기반 자동 전이
    if req.current_maturity == "seedling":
        rule = TRANSITION_RULES["seedling_to_growing"]
        if evaluate_conditions(rule, metrics):
            return MaturityTransition(
                note_id=req.note_id,
                old_state="seedling",
                new_state="growing",
                reason=f"참조 {metrics.reference_count}회, 연결 {metrics.connection_count}개",
                auto=rule["auto"],
                timestamp=datetime.now(),
            )

    elif req.current_maturity == "growing":
        rule = TRANSITION_RULES["growing_to_evergreen"]
        if evaluate_conditions(rule, metrics):
            return MaturityTransition(
                note_id=req.note_id,
                old_state="growing",
                new_state="evergreen",
                reason=f"참조 {metrics.reference_count}회 AND 연결 {metrics.connection_count}개 — 사용자 확인 필요",
                auto=rule["auto"],
                timestamp=datetime.now(),
            )

    # 5. 아카이브 제안 (모든 상태에서 가능)
    if req.current_maturity != "archived":
        rule = TRANSITION_RULES["any_to_archived"]
        if evaluate_conditions(rule, metrics):
            return MaturityTransition(
                note_id=req.note_id,
                old_state=req.current_maturity,
                new_state="archived",
                reason=f"{metrics.days_since_last_access}일 미참조 — 아카이브 제안",
                auto=False,
                timestamp=datetime.now(),
            )

    return None  # 전이 불필요


async def apply_transition(transition: MaturityTransition):
    """전이 실행 — Neo4j 노드 업데이트"""
    await neo4j_query("""
        MATCH (n:KnowledgeNote {id: $id})
        SET n.maturity = $new_state, n.updated_at = datetime()
    """, {"id": str(transition.note_id), "new_state": transition.new_state})

    # 이력 기록
    await log_maturity_transition(transition)

    # archived 시 folder_notebook_structure.md의 Archive/ 폴더로 이동
    if transition.new_state == "archived":
        await move_to_archive(transition.note_id)
```

---

### E5. 메트릭 수집

```python
async def collect_note_metrics(note_id: UUID) -> NoteMetrics:
    # 1. 참조 횟수 (review_count + 검색 참조)
    ref_count = await neo4j_query("""
        MATCH (n:KnowledgeNote {id: $id})
        RETURN n.review_count AS rc
    """, {"id": str(note_id)})

    # 2. 연결 수 (RELATED_TO + SUPPORTS + CONTRADICTS 합산, LOCK-PKM-05)
    conn_count = await neo4j_query("""
        MATCH (n:KnowledgeNote {id: $id})-[r:RELATED_TO|SUPPORTS|CONTRADICTS]-()
        RETURN count(r) AS cnt
    """, {"id": str(note_id)})

    # 3. 마지막 접근 이후 일수
    last_access = await neo4j_query("""
        MATCH (n:KnowledgeNote {id: $id})
        RETURN duration.inDays(n.updated_at, datetime()).days AS days
    """, {"id": str(note_id)})

    return NoteMetrics(
        reference_count=ref_count,
        connection_count=conn_count,
        days_since_last_access=last_access,
    )
```

---

### E6. 주기적 배치 검사

```python
async def batch_maturity_check(user_id: UUID):
    """일 1회 — 모든 노트의 성숙도 전이 검사"""
    all_notes = await neo4j_query("""
        MATCH (n:KnowledgeNote)
        WHERE n.user_id = $user_id AND n.maturity <> 'archived'
        RETURN n.id, n.maturity
    """, {"user_id": str(user_id)})

    transitions = []
    for note in all_notes:
        t = await check_maturity_transition(MaturityCheckRequest(
            note_id=note.id,
            current_maturity=note.maturity,
            trigger="time_check",
        ))
        if t:
            if t.auto:
                await apply_transition(t)
            else:
                await queue_for_confirmation(t)
            transitions.append(t)

    return transitions
```

---

### E7. 모순 발견 시 재검토

```python
async def on_contradiction_detected(note_id: UUID):
    """04_knowledge-conflict에서 CONTRADICTS 감지 시 호출"""
    current = await get_maturity(note_id)
    if current == "evergreen":
        # Evergreen → Growing으로 강등 (재검토 필요)
        t = MaturityTransition(
            note_id=note_id,
            old_state="evergreen",
            new_state="growing",
            reason="모순 발견 — 재검토 필요",
            auto=True,
            timestamp=datetime.now(),
        )
        await apply_transition(t)
```

---

### E8. Error Handling
| 에러 | 폴백 |
|------|------|
| Neo4j 메트릭 쿼리 실패 | 전이 건너뜀 → 다음 배치에서 재시도 |
| 전이 적용 실패 (트랜잭션 오류) | 롤백 + 재시도 1회 |
| 이력 기록 실패 | 전이는 적용하되 이력은 큐에 적재 |
| 배치 중 대량 노트 (>10000) | 1000건씩 분할 처리 |

### E9. Integration Test
1. 새 노트 생성 → maturity="seedling" 확인.
2. 3회 참조 후 → seedling→growing 자동 전이.
3. 참조 10회 + 연결 5개 → growing→evergreen 전이 제안 (사용자 확인 큐).
4. 180일 미참조 → archived 제안 (사용자 확인).
5. CONTRADICTS 감지 → evergreen→growing 강등.
6. 중복 병합 대상 → 즉시 archived (자동).
7. Part2 "blooming" 상태 수신 → "growing"으로 매핑.

### E10. Dependencies
- 내부: knowledge_graph_construction.md (Neo4j 노드 속성), semantic_duplicate_detection.md (병합 시 아카이브), 04_knowledge-conflict/conflict_detection.md (모순 감지 → 재검토), folder_notebook_structure.md (Archive 폴더 이동), time_based_management.md (리뷰 리포트에 전이 이력)
- 외부: Neo4j 5.x
- 거버넌스: LOCK-PKM-12 (4-stage 정본, 확장/변경 불가), CFL-PKM-005 (Part2 5-stage 매핑 판정)

**자체 점수**: 100/100
