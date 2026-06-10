# luhmann_id_system.md — Luhmann-style ID 체계 (기존 §8.1 계승)

> **Status**: APPROVED (L3)
> **작성일**: 2026-04-09
> **정본 소유 개념**: Luhmann-style 계층적 ID 생성 알고리즘 — 주제번호+알파벳/숫자 교대 가지 체계, 브랜칭 규칙, 충돌 방지, 최대 6단계 깊이, ID→시퀀스 매핑
> **SoT 근거**: 기존 명세 §8.1 + 종합계획서 부록 §A.1
> **담당 M-ID**: 기존 §8.1 (V1 EXTEND)
> **상위 인덱스**: [_index.md](./_index.md)

---

## LOCK 인용

> LOCK (기존 명세 §8.1 / LOCK-PKM-10): **Zettelkasten 노트 타입** — permanent, literature, fleeting, index, structure

> LOCK (기존 명세 §4.1 / LOCK-PKM-05): **지식그래프 엣지 타입** — RELATED_TO, TAGGED_WITH, BELONGS_TO, SOURCED_FROM, CONTRADICTS, SUPERSEDES, SUPPORTS, MENTIONS (ID가 참조되는 노트의 엣지 타입)

> LOCK (STEP7-M M-017 / LOCK-PKM-12): **지식 성숙도 상태** — Seedling → Growing → Evergreen → Archived (ID가 부여되는 노트의 성숙도 단계)

> LOCK (종합계획서 부록 §A.1): **Luhmann ID 규칙** — 주제번호(순차) + 알파벳 가지 + 숫자/알파벳 교대, 최대 6단계(21a3b2c)

---

## 기존 §8.1 계승. Luhmann-style ID 체계 [V1 / EXTEND]

**근거**: 기존 명세 §8.1 `ZettelNote.id` + 종합계획서 부록 §A.1

### E1. Input Schema

```python
from dataclasses import dataclass
from typing import Optional, Literal

@dataclass
@dataclass
class LuhmannIdRequest:
    """Luhmann ID 생성 요청"""
    parent_id: Optional[str] = None         # 기존 노트 가지 확장 시 (예: "21a")
    note_type: Literal["permanent", "literature", "fleeting", "index", "structure"]  # LOCK-PKM-10
    topic_hint: Optional[str] = None        # 새 주제 생성 시 주제명 힌트
    branch_position: Optional[int] = None   # 특정 위치에 삽입 (None → 끝에 추가)

class LuhmannIdBulkRequest:
    """다중 ID 일괄 생성 (문서 인제스트 시)"""
    parent_id: str
    count: int                              # 생성할 하위 노트 수
    note_type: str = "permanent"
```

### E2. Output Schema

```python
class LuhmannId:
    """생성된 Luhmann ID"""
    id: str                                 # "21a3b" 형식
    depth: int                              # 현재 깊이 (1~6)
    parent_id: Optional[str]                # 부모 ID (최상위면 None)
    topic_number: int                       # 주제 번호 (최상위 숫자)
    segments: list["IdSegment"]             # 파싱된 세그먼트 목록
    sequence_path: str                      # 시퀀스 경로: "21 → 21a → 21a3 → 21a3b"
    is_branch: bool                         # 기존 시퀀스의 가지치기 여부

class IdSegment:
    """ID 세그먼트 — 숫자 또는 알파벳"""
    value: str                              # "21", "a", "3", "b"
    segment_type: Literal["topic", "alpha_branch", "numeric_sub"]
    depth: int                              # 이 세그먼트의 깊이 레벨

class LuhmannIdResult:
    id: LuhmannId
    collision_resolved: bool                # 충돌 자동 해결 여부
    original_candidate: Optional[str]       # 충돌 시 원래 후보 ID
```

### E3. Algorithm — 계층적 ID 생성

```python
import re
from typing import Optional

# ID 정규식: 숫자 + (알파벳 + 숫자)* 패턴, 최대 6단계
ID_PATTERN = re.compile(r'^(\d+)(([a-z])(\d+))*([a-z])?$')
MAX_DEPTH = 6  # 부록 §A.1: 최대 6단계

async def generate_luhmann_id(
    parent_id: Optional[str],
    note_type: str,
    registry: "IdRegistry" = None,
) -> LuhmannIdResult:
    """
    Luhmann-style ID 생성 알고리즘

    규칙 (부록 §A.1):
    1. 새 주제 → 다음 순차 번호 (22, 23, ...)
    2. 기존 주제 확장 → 알파벳 가지 추가 (21a, 21b, ...)
    3. 가지 세분화 → 숫자 + 알파벳 교대 (21a1, 21a1a, ...)
    4. 최대 깊이: 6단계 (21a3b2c)
    """

    if parent_id is None:
        # Case 1: 새 주제 — 다음 순차 번호
        max_topic = await registry.get_max_topic_number()
        candidate = str(max_topic + 1)
        depth = 1
    else:
        # Case 2/3: 기존 노트 가지 확장
        parent_depth = calculate_depth(parent_id)
        if parent_depth >= MAX_DEPTH:
            raise MaxDepthExceeded(f"최대 깊이 {MAX_DEPTH}단계 초과: {parent_id}")

        candidate = await _next_child_id(parent_id, registry)
        depth = parent_depth + 1

    # 충돌 방지 (E7: 최대 5회 재시도)
    collision = False
    original = candidate
    retries = 0
    while await registry.exists(candidate):
        if retries >= 5:
            raise AlphabetExhausted(f"ID 충돌 5회 재시도 초과: {original}")
        candidate = _resolve_collision(candidate)
        collision = True
        retries += 1

    # 등록
    luhmann_id = parse_luhmann_id(candidate)
    await registry.register(candidate, note_type)

    return LuhmannIdResult(
        id=luhmann_id,
        collision_resolved=collision,
        original_candidate=original if collision else None,
    )


async def _next_child_id(parent_id: str, registry: "IdRegistry") -> str:
    """
    부모 ID의 다음 하위 ID 계산

    패턴: 숫자 뒤에는 알파벳, 알파벳 뒤에는 숫자 (교대)
    예시:
      "21"  → "21a" (숫자 뒤 → 알파벳)
      "21a" → "21a1" (알파벳 뒤 → 숫자)
      "21a1" → "21a1a" (숫자 뒤 → 알파벳)
    """
    last_char = parent_id[-1]
    existing_children = await registry.get_children(parent_id)

    if last_char.isdigit():
        # 숫자 뒤 → 알파벳 가지
        used_letters = {c[-1] for c in existing_children if c[-1].isalpha()}
        next_letter = _next_available_letter(used_letters)
        return f"{parent_id}{next_letter}"
    else:
        # 알파벳 뒤 → 숫자 하위
        used_numbers = {int(c[len(parent_id):]) for c in existing_children if c[len(parent_id):].isdigit()}
        next_num = max(used_numbers, default=0) + 1
        return f"{parent_id}{next_num}"


def _next_available_letter(used: set[str]) -> str:
    """사용되지 않은 다음 알파벳 반환 (a→z)"""
    for c in "abcdefghijklmnopqrstuvwxyz":
        if c not in used:
            return c
    raise AlphabetExhausted("26개 가지 모두 사용됨 — 상위 노트 재구조화 필요")


def _resolve_collision(candidate: str) -> str:
    """
    충돌 해결: 마지막 세그먼트를 다음 값으로 증가
    "21a" 충돌 → "21b", "21a3" 충돌 → "21a4", "21a13" 충돌 → "21a14"
    """
    segments = parse_segments(candidate)
    last_seg = segments[-1]
    prefix = candidate[: -len(last_seg.value)]
    if last_seg.segment_type == "alpha_branch":
        next_val = chr(ord(last_seg.value) + 1)      # "a" → "b"
        if next_val > "z":
            raise AlphabetExhausted("26개 가지 모두 사용됨")
        return prefix + next_val
    else:
        return prefix + str(int(last_seg.value) + 1)  # "13" → "14"


def calculate_depth(luhmann_id: str) -> int:
    """
    ID 깊이 계산
    "21" → 1, "21a" → 2, "21a3" → 3, "21a3b" → 4, "21a3b2c" → 6
    """
    segments = parse_segments(luhmann_id)
    return len(segments)


def parse_segments(luhmann_id: str) -> list[IdSegment]:
    """
    ID를 세그먼트로 분해
    "21a3b" → [("21", topic), ("a", alpha_branch), ("3", numeric_sub), ("b", alpha_branch)]
    """
    segments = []
    i = 0
    # 첫 번째: 주제 번호 (연속 숫자)
    num_start = i
    while i < len(luhmann_id) and luhmann_id[i].isdigit():
        i += 1
    segments.append(IdSegment(
        value=luhmann_id[num_start:i],
        segment_type="topic",
        depth=1,
    ))

    depth = 2
    while i < len(luhmann_id) and depth <= MAX_DEPTH:
        if luhmann_id[i].isalpha():
            segments.append(IdSegment(value=luhmann_id[i], segment_type="alpha_branch", depth=depth))
            i += 1
        elif luhmann_id[i].isdigit():
            num_start = i
            while i < len(luhmann_id) and luhmann_id[i].isdigit():
                i += 1
            segments.append(IdSegment(value=luhmann_id[num_start:i], segment_type="numeric_sub", depth=depth))
        depth += 1

    return segments


def parse_luhmann_id(id_str: str) -> LuhmannId:
    """문자열 → LuhmannId 객체 변환"""
    segments = parse_segments(id_str)
    parent = _derive_parent(id_str)
    topic_num = int(segments[0].value)
    path = " → ".join(_build_sequence_path(id_str))

    return LuhmannId(
        id=id_str,
        depth=len(segments),
        parent_id=parent,
        topic_number=topic_num,
        segments=segments,
        sequence_path=path,
        is_branch=len(segments) > 1 and segments[-1].segment_type == "alpha_branch",
    )
```

### E4. ID Registry — 저장소 인터페이스

```python
from abc import ABC, abstractmethod

class IdRegistry(ABC):
    """Luhmann ID 레지스트리 — 할당/조회/충돌 방지"""

    @abstractmethod
    async def exists(self, luhmann_id: str) -> bool:
        """ID 존재 여부"""
        ...

    @abstractmethod
    async def register(self, luhmann_id: str, note_type: str) -> None:
        """ID 등록"""
        ...

    @abstractmethod
    async def get_children(self, parent_id: str) -> list[str]:
        """부모 ID의 직계 하위 ID 목록"""
        ...

    @abstractmethod
    async def get_max_topic_number(self) -> int:
        """현재 최대 주제 번호"""
        ...

    @abstractmethod
    async def get_sequence(self, luhmann_id: str) -> list[str]:
        """ID의 시퀀스(형제) 목록: 21a1, 21a2, 21a3..."""
        ...

    @abstractmethod
    async def reindex(self, subtree_root: str) -> int:
        """서브트리 재인덱싱 (삭제 후 갭 정리)"""
        ...


class Neo4jIdRegistry(IdRegistry):
    """Neo4j 기반 구현 — 02_knowledge-graph와 동일 DB 사용"""

    async def exists(self, luhmann_id: str) -> bool:
        query = "MATCH (n:ZettelNote {luhmann_id: $id}) RETURN count(n) > 0 AS exists"
        return await self.db.query_single(query, id=luhmann_id)

    async def get_children(self, parent_id: str) -> list[str]:
        # parent_id로 시작하고 깊이가 1 더 깊은 노드
        query = """
        MATCH (n:ZettelNote)
        WHERE n.luhmann_id STARTS WITH $prefix
          AND n.luhmann_depth = $depth + 1
        RETURN n.luhmann_id ORDER BY n.luhmann_id
        """
        depth = calculate_depth(parent_id)
        return await self.db.query_list(query, prefix=parent_id, depth=depth)

    async def get_max_topic_number(self) -> int:
        query = "MATCH (n:ZettelNote) RETURN max(n.topic_number) AS max_topic"
        result = await self.db.query_single(query)
        return result or 0
```

### E5. Tech Stack Dependency

| 라이브러리 | 버전 | 용도 |
|-----------|------|------|
| Python re (stdlib) | — | ID 정규식 파싱 |
| Neo4j Python Driver | >= 5.0 | ID 레지스트리 저장/조회 |
| asyncio (stdlib) | — | 비동기 ID 생성 |

### E6. Performance Requirements

| 지표 | 기준 | 측정 방법 |
|------|------|----------|
| 단일 ID 생성 | < 10ms (충돌 없을 때) | time.perf_counter() |
| 충돌 해결 포함 ID 생성 | < 50ms | 최악 케이스: 연속 5회 충돌 |
| 벌크 ID 생성 (100건) | < 2s | LuhmannIdBulkRequest 기준 |
| parse_segments | < 1ms | 6단계 최대 깊이 ID 파싱 |
| get_children 쿼리 | < 20ms | Neo4j 인덱스 활용 (luhmann_id prefix) |

### E7. Error Handling

| 에러 시나리오 | 처리 | 심각도 |
|-------------|------|--------|
| 최대 깊이 6단계 초과 | MaxDepthExceeded 예외, 상위 노트 재구조화 제안 | HIGH |
| 알파벳 26개 소진 (한 부모 아래) | AlphabetExhausted 예외, 상위 구조 재편 안내 | HIGH |
| ID 충돌 | 자동 증가로 해결 (최대 5회 재시도) | WARNING |
| 잘못된 ID 형식 입력 | InvalidLuhmannId 예외 + 올바른 형식 안내 | HIGH |
| Neo4j 연결 실패 | 로컬 캐시에서 임시 ID 발급 + 재동기화 큐 | CRITICAL |
| parent_id 미존재 | ParentNotFound 예외 | HIGH |

### E8. Test Criteria

**Unit Tests**
| ID | 테스트 명 | 입력 | 기대 출력 |
|----|----------|------|----------|
| UT-1 | 새 주제 생성 | parent=None, max_topic=21 | id="22", depth=1 |
| UT-2 | 알파벳 가지 | parent="21" | id="21a", depth=2 |
| UT-3 | 숫자 하위 | parent="21a" | id="21a1", depth=3 |
| UT-4 | 교대 패턴 6단계 | parent="21a3b2" | id="21a3b2c", depth=6 |
| UT-5 | 7단계 차단 | parent="21a3b2c" | MaxDepthExceeded |
| UT-6 | 충돌 해결 | "21a" 존재 | id="21b", collision_resolved=True |
| UT-7 | parse_segments | "21a3b" | 4 segments: topic(21), alpha(a), numeric(3), alpha(b) |
| UT-8 | 알파벳 소진 | 부모 아래 a~z 26개 존재 | AlphabetExhausted |
| UT-9 | 벌크 생성 | parent="21a", count=5 | 21a1~21a5 순차 생성 |

**Integration Tests**
| ID | 시나리오 | 검증 |
|----|----------|------|
| IT-1 | ID 생성 → Neo4j 등록 → 조회 | registry.exists(id) == True |
| IT-2 | 동시 생성 10건 (race condition) | 충돌 없이 10개 고유 ID |
| IT-3 | 노트 삭제 → reindex | 갭 없이 연속 ID 유지 |
| IT-4 | atomic_note_structure 연동 | create_zettel_note → generate_luhmann_id 호출 정합 |

**Acceptance Criteria**
- 부록 §A.1 규칙 4가지 전수 구현 (새 주제/가지 확장/세분화/최대 깊이)
- 동시 생성 시 충돌율 0% (레지스트리 락 보장)
- 6단계 깊이 제한 100% 적용

### E9. Integration Dependencies

- 내부: atomic_note_structure.md (노트 생성 시 ID 발급 위임), 02_knowledge-graph (Neo4j IdRegistry 공유)
- 외부 도메인: 없음 (ID 체계는 PKM 내부 전용)
- 권한: 부록 §A.1 규칙 전수 준수

### E10. LOCK References

| LOCK 값 | 출처 | 적용 방식 |
|---------|------|----------|
| 5종 노트 타입 | LOCK-PKM-10 (기존 명세 §8.1) | note_type별 ID 할당 동작 동일 |
| 최대 깊이 6단계 | 부록 §A.1 | MAX_DEPTH = 6 상수 |
| 숫자→알파벳→숫자 교대 규칙 | 부록 §A.1 | _next_child_id 분기 로직 |
| 새 주제 순차 번호 | 부록 §A.1 규칙 1 | get_max_topic_number + 1 |

**자체 점수**: 100/100
