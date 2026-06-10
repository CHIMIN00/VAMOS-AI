# knowledge_sharing.md — 지식 공유 및 협업 (M-028)

> **Status**: APPROVED (L3) — V2 NEW
> **작성일**: 2026-04-23
> **정본 소유 개념**: 팀 워크스페이스, 권한 모델(RBAC+ABAC 하이브리드), 공유 범위(개별/프로젝트/공개/API), 충돌 해결 정책, 공유 감사 로그, 링크 만료/권한 회수
> **SoT 근거**: STEP7-M Part 2 (M-028 L499-509) + 기존 명세 §7 (협업 공유) + 종합계획서 §6.3
> **담당 M-ID**: M-028 (V2 NEW)
> **상위 인덱스**: [_index.md](./_index.md)

---

## §1. 교차 참조 블록

| # | 종류 | 대상 | 역할 |
|---|------|------|------|
| #1 | 상위 SoT | `sot/STEP7-M_PKM_지식관리_작업가이드.md` Part 2 L499-509 | M-028 요구사항 원천 |
| #2 | 권한 체인 | `AUTHORITY_CHAIN.md` §2 (LOCK-PKM-04/05/07/08/10/12) | 노드/엣지/태그/카테고리/Zettelkasten/성숙도 정본 |
| #3 | 동일 폴더 | `version_control.md` | 버전 이력 기반 공유 스냅샷 |
| #4 | 동일 폴더 | `semantic_search.md` | 공유 지식 검색 경로 |
| #5 | 타 폴더 | `04_knowledge-conflict/conflict_detection.md` | 공유 시 충돌 탐지 |
| #6 | 타 폴더 | `04_knowledge-conflict/freshness_management.md` §V2 | Dream Mode 와 공유 스냅샷 정합 |
| #7 | 타 도메인 | `#9 Security-Governance (6-2)` | RBAC/ABAC 정책 소스 |
| #8 | 타 도메인 | `#7 Workflow-RPA (3-4)` | 팀 워크플로우 트리거 |

---

## §2. LOCK 인용 (verbatim)

> LOCK (기존 명세 §4.1 / LOCK-PKM-04): 지식그래프 노드 타입 — KnowledgeNote, Tag, Domain, Source, Person

> LOCK (기존 명세 §4.1 / LOCK-PKM-05): 지식그래프 엣지 타입 — RELATED_TO, TAGGED_WITH, BELONGS_TO, SOURCED_FROM, CONTRADICTS, SUPERSEDES, SUPPORTS, MENTIONS

> LOCK (STEP7-M M-011 / LOCK-PKM-07): 태그 분류 체계 — 주제/유형/감정/중요도/프로젝트 5차원

> LOCK (기존 명세 §3.2 / LOCK-PKM-08): 지식 카테고리 — concept, fact, procedure, decision, reference, opinion, code_snippet, bookmark

> LOCK (기존 명세 §8.1 / LOCK-PKM-10): Zettelkasten 노트 타입 — permanent, literature, fleeting, index, structure

> LOCK (STEP7-M M-017 / LOCK-PKM-12): 지식 성숙도 상태 — Seedling → Growing → Evergreen → Archived

본 문서는 위 6 LOCK 전수를 **참조 only** (재정의 ❌, 특히 LOCK-PKM-10 Zettelkasten 5종은 타입 인용만 허용).

---

## §3. 공통 자료 구조 재사용 (출처: 3-3 PKM `knowledge_graph_construction.md` §E1)

```python
# 출처: 02_knowledge-graph/knowledge_graph_construction.md §E1
# 본 §V2는 KnowledgeNote / Person / Domain 노드 타입을 소비만 함
class KnowledgeNote: ...     # LOCK-PKM-04
class Person: ...            # LOCK-PKM-04 (5 노드 중 Person)
class Domain: ...            # LOCK-PKM-04 (5 노드 중 Domain)
```

시간 복잡도:
- 권한 체크: O(1) (ACL hash lookup) ~ O(r) (r=역할 상속 체인)
- 공유 스냅샷 생성: O(n) (n=노트 수) + O(e) (e=그래프 서브셋 엣지)
- 충돌 해결 병합 (3-way): O(L) (L=변경 라인)

---

## §4. M-028 지식 공유 및 협업 [V2 NEW]

### §4.1 아키텍처 개요

```
[사용자 공유 요청]
        │
        ├── 공유 옵션: link / workspace / public / api
        └── 공유 범위: note / collection / project / domain
        │
        ↓
[권한 게이트] (RBAC + ABAC hybrid)
        │
        ├── RBAC: role ∈ {owner, editor, commenter, viewer}
        ├── ABAC: attribute (sensitivity, project, freshness, maturity)
        └── 정책 엔진: 6-2 Security-Governance 통합
        │
        ↓
[공유 아티팩트 생성]
        │
        ├── 스냅샷: KnowledgeNote + 인접 엣지 + metadata
        ├── 링크 ID: UUID v7 + 만료 시각
        └── 감사 엔트리: actor / target / action / timestamp
        │
        ↓
[배포 채널]
        │
        ├── Shareable Link (browser URL + OAuth2)
        ├── Team Workspace (동기 협업)
        ├── Public (블로그/위키 발행)
        └── API (외부 앱 GraphQL/REST)
```

### §4.2 공유 옵션 매트릭스 (STEP7-M M-028 L502-506 verbatim 매핑)

| 옵션 | STEP7-M 근거 | 기본 권한 | 만료 | 감사 |
|------|-------------|----------|------|------|
| 개별 지식 공유 (링크 생성) | L503 "개별 지식 공유: 링크 생성" | viewer (기본), editor (optional) | 7~365일 | per-link |
| 프로젝트 지식 공유 (팀 워크스페이스) | L504 "프로젝트 지식 공유: 팀 워크스페이스" | workspace role 상속 | 프로젝트 종료 | per-workspace |
| 공개 지식 (블로그/위키) | L505 "공개 지식: 블로그/위키 형태 발행" | public:view | 무기한 or 수동 철회 | 공개 게시 감사 |
| API (외부 앱 접근) | L506 "API: 외부 앱에서 지식 접근" | api_token scope 기반 | token rotation 90일 | API 호출 로그 |

### §4.3 권한 모델 (RBAC + ABAC)

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Literal, Optional
from uuid import UUID

class Role(str, Enum):
    OWNER = "owner"           # 전권 (삭제/공유/권한 위임)
    EDITOR = "editor"         # 편집 + 코멘트 + 제안
    COMMENTER = "commenter"   # 코멘트 + 제안 (본문 수정 ❌)
    VIEWER = "viewer"         # 조회 only
    API_SCOPE = "api_scope"   # scope 기반 제한적 접근

@dataclass
class AttributePolicy:
    """ABAC: 노트 속성 기반 가드"""
    max_sensitivity: Literal["public","internal","restricted","confidential"]
    allowed_categories: list[str]       # LOCK-PKM-08 8종 중 subset
    allowed_maturity: list[str]         # LOCK-PKM-12 4단계 subset (예: archived 공유 금지)
    block_contradictory: bool           # CONTRADICTS 엣지 있는 노트는 공유 금지 (옵션)

@dataclass
class SharingGrant:
    grant_id: UUID
    target_note_id: UUID                # LOCK-PKM-04 KnowledgeNote
    grantee: str                        # user_id / group_id / public
    role: Role
    attribute_policy: AttributePolicy
    expires_at: Optional[datetime]
    revoked_at: Optional[datetime]
    audit_chain_id: UUID
```

**권한 계산 함수**:
```python
def can_access(user, note, action) -> bool:
    # 1) 개인 소유 (항상 OWNER)
    if note.owner_id == user.id:
        return True
    # 2) RBAC: 역할 체크
    grants = get_active_grants(user, note)
    required_role = REQUIRED_ROLE_BY_ACTION[action]  # view→VIEWER, edit→EDITOR, share→OWNER
    if not any(g.role_rank >= required_role.rank for g in grants):
        return False
    # 3) ABAC: 속성 체크
    for g in grants:
        _SENS_ORDER = ["public", "internal", "restricted", "confidential"]
        if _SENS_ORDER.index(note.sensitivity) > _SENS_ORDER.index(g.attribute_policy.max_sensitivity):
            return False
        if note.category not in g.attribute_policy.allowed_categories:
            return False
        if note.maturity not in g.attribute_policy.allowed_maturity:
            return False
    return True
```

### §4.4 충돌 해결 정책 (협업 편집)

3-way merge (base / local / remote) 기본 전략:

```python
@dataclass
class MergeStrategy:
    text_body: Literal["3way_merge","last_writer_wins","manual_resolve"]
    tags: Literal["union","intersection","replace"]    # LOCK-PKM-07 5차원 태그
    category: Literal["keep_base","prefer_latest"]     # LOCK-PKM-08 8종 카테고리
    edges: Literal["union_non_contradicting","manual_resolve"]

DEFAULT_MERGE_STRATEGY = MergeStrategy(
    text_body="3way_merge",
    tags="union",
    category="keep_base",
    edges="union_non_contradicting",
)
```

충돌 우선순위 규칙 (IMPL-DETAIL, 사용자 설정 가능):
1. OWNER 변경사항 > EDITOR 변경사항
2. 최신 `updated_at` > 이전
3. `maturity=evergreen` 노트 편집은 OWNER 승인 필수
4. CONTRADICTS 엣지가 생기는 병합 → manual_resolve 강제

### §4.5 공유 감사 로그

```python
@dataclass
class SharingAuditEntry:
    audit_id: UUID
    actor_user_id: str
    action: Literal["create_link","grant","revoke","view","edit","publish","export"]
    target_type: Literal["note","collection","project","domain"]
    target_id: UUID
    grantee: Optional[str]
    metadata: dict
    timestamp: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
```

**보관 정책**: 기본 365일 (IMPL-DETAIL, 사용자/법무 팀 조정 가능). GDPR/개인정보 요청 시 소거.

### §4.6 Zettelkasten 타입 인용만 (LOCK-PKM-10 준수)

본 문서는 공유 범위 산정 시 Zettelkasten 타입을 참조만 한다:
- `permanent` → 공유 기본 허용 (영구 참조 대상)
- `literature` → 출처 라이센스 확인 후 공유 가능
- `fleeting` → 공유 기본 비허용 (개인 스케치)
- `index` → 공유 허용 (목차)
- `structure` → 공유 허용 (개요)

**재정의 ❌** (LOCK-PKM-10 기존 5종 타입 보호, 신규 타입 추가 금지).

### §4.7 팀 워크스페이스 동기 협업

- CRDT 기반 실시간 편집 (Yjs / Automerge 중 택일, V2 IMPL-DETAIL)
- presence: 참여자 커서 위치 + 선택 영역 (1초 throttle)
- offline 편집 버퍼: 30분 이내 재동기화 보장
- 동시 편집 수: 단일 노트당 ≤ 20 (IMPL-DETAIL)

### §4.8 공개 발행 (블로그/위키)

```python
@dataclass
class PublicationTarget:
    target: Literal["blog","wiki","static_site"]
    url_slug: str                     # /public/<slug>
    seo_metadata: dict                # title, description, og:image
    license: Literal["CC-BY","CC-BY-SA","CC-BY-NC","ARR","Public-Domain"]
    retraction_enabled: bool          # 철회 가능 여부
```

- 철회: 48시간 이내 CDN/검색 엔진 사후 제거 request
- 민감 카테고리 자동 차단: `decision` (결정) + `opinion` (의견) — 사용자 명시 승인 필수

### §4.9 API 접근 (외부 앱)

```
GET /api/v2/knowledge/notes/{id}
GET /api/v2/knowledge/search?q=...
POST /api/v2/knowledge/notes (scope: write)
POST /api/v2/knowledge/graph/query (Cypher subset, readonly)
```

**API 키 scope 예시** (IMPL-DETAIL):
- `knowledge:read` (기본 note 조회)
- `knowledge:write` (note 생성/수정)
- `graph:query` (읽기 전용 Cypher)
- `share:manage` (공유 링크 생성/철회)

rate limit: token bucket (기본 60 req/min, 사용자별 조정 가능)

---

## §5. 에스컬레이션 Pydantic

```python
from pydantic import BaseModel, Field
from typing import Literal

class SharingEscalation(BaseModel):
    severity: Literal["info","warning","error","critical"]
    reason: Literal[
        "grant_expired_but_accessed",
        "abac_policy_violation",
        "contradictory_merge_auto_blocked",
        "public_publication_of_sensitive",
        "api_rate_limit_exceeded",
        "external_license_incompatible",
        "crdt_sync_divergence_detected",
    ]
    actor: str
    target_id: str
    context: dict = Field(default_factory=dict)
    requires_user_review: bool = True
```

---

## §6. 로깅 (structured JSON 3-block)

```json
{"event":"sharing.grant_created","grant_id":"...","grantee":"user:42","role":"editor","expires_at":"2026-05-23T00:00:00Z","actor":"user:1"}
```

```json
{"event":"sharing.abac_block","target_id":"...","policy_violated":"max_sensitivity","attempted_role":"viewer","sensitivity":"restricted"}
```

```json
{"event":"sharing.publish_public","url_slug":"auth-best-practices","license":"CC-BY","category":"concept","maturity":"evergreen"}
```

---

## §7. Phase 3 테스트 시나리오 (10건)

| # | 시나리오 | 기대 | LOCK |
|---|---------|------|------|
| T1 | 링크 기반 viewer 공유 (7일 만료) | grant 생성 + 7일 후 자동 만료 | §4.3 |
| T2 | ABAC sensitivity=restricted 노트 → public 시도 | `public_publication_of_sensitive` escalation | §5 |
| T3 | 팀 워크스페이스 동시 3명 편집 | CRDT 병합 + 충돌 0 | §4.7 |
| T4 | 3-way merge (base+local+remote) | DEFAULT_MERGE_STRATEGY 적용 | §4.4 |
| T5 | Zettelkasten fleeting 노트 공유 시도 | 기본 비허용 warning | §4.6 |
| T6 | archived 성숙도 노트 공유 | ABAC policy 차단 | LOCK-PKM-12 |
| T7 | API rate limit 100 req/min 초과 | `api_rate_limit_exceeded` + 429 응답 | §4.9 |
| T8 | public 발행 후 48시간 내 철회 | CDN/검색 엔진 제거 request 전송 | §4.8 |
| T9 | CONTRADICTS 엣지 발생 병합 | manual_resolve 강제 | §4.4 |
| T10 | LOCK-PKM-10 신규 Zettelkasten 타입 추가 시도 | [VIOLATION:LOCK-PKM-10_redefinition] abort | §4.6 |

---

## §8. LOCK 5필드 매핑표

| LOCK ID | 항목 | 정본 출처 | 값 | 재정의 |
|---------|------|-----------|-----|--------|
| LOCK-PKM-04 | 그래프 노드 타입 | 기존 명세 §4.1 | KnowledgeNote, Tag, Domain, Source, Person | ❌ |
| LOCK-PKM-05 | 그래프 엣지 타입 | 기존 명세 §4.1 | RELATED_TO, TAGGED_WITH, BELONGS_TO, SOURCED_FROM, CONTRADICTS, SUPERSEDES, SUPPORTS, MENTIONS | ❌ |
| LOCK-PKM-07 | 태그 분류 체계 | STEP7-M M-011 | 주제/유형/감정/중요도/프로젝트 5차원 | ❌ |
| LOCK-PKM-08 | 지식 카테고리 | 기존 명세 §3.2 | concept, fact, procedure, decision, reference, opinion, code_snippet, bookmark | ❌ |
| LOCK-PKM-10 | Zettelkasten 노트 타입 | 기존 명세 §8.1 | permanent, literature, fleeting, index, structure | ❌ |
| LOCK-PKM-12 | 지식 성숙도 상태 | STEP7-M M-017 | Seedling → Growing → Evergreen → Archived | ❌ |

---

## §9. 세션 간 cross-check

| V2 피어 | 공유 계약 | 상태 |
|---------|-----------|------|
| `freshness_management.md` §V2 (M-042) | Dream Mode 스냅샷 ↔ 공유 정합 | 감사 로그 이벤트 연동 |
| `version_control.md` | 공유 스냅샷 = 특정 version hash | 직접 참조 |
| `02_knowledge-graph/graph_reasoning.md` §V2 | 공유 대상 서브그래프 추론 재사용 | kNN 결과 공유 |

---

## §10. 자가 체크리스트

- [x] LOCK-PKM-04/05/07/08/10/12 verbatim 인용 6건 (§2)
- [x] STEP7-M M-028 L499-509 line refs 실측
- [x] 공통 스키마 출처 (§3)
- [x] 4 공유 옵션 매트릭스 (§4.2)
- [x] RBAC + ABAC 하이브리드 권한 (§4.3)
- [x] 3-way 충돌 해결 정책 (§4.4)
- [x] 감사 로그 모델 (§4.5)
- [x] Zettelkasten LOCK-PKM-10 인용만 (§4.6)
- [x] CRDT 팀 워크스페이스 (§4.7)
- [x] 공개 발행 + API 접근 (§4.8~§4.9)
- [x] 에스컬레이션 Pydantic (§5)
- [x] 로깅 3-block (§6)
- [x] Phase 3 테스트 10건 (§7)
- [x] LOCK 매핑표 6 LOCK (§8)
- [x] 피어 cross-check (§9)
