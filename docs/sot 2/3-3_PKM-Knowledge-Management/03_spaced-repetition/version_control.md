# version_control.md — 지식 버전 관리 (M-029)

> **Status**: APPROVED (L3)
> **작성일**: 2026-04-09
> **정본 소유 개념**: 지식 노트 변경 이력, Git-like 버전 관리, Diff 비교, 롤백
> **SoT 근거**: STEP7-M Part 3a (M-029 L511-521) — 지식 버전 관리
> **담당 M-ID**: M-029 (V1 NEW)
> **상위 인덱스**: [_index.md](./_index.md)

---

## LOCK 인용

> LOCK (기존 명세 §3.2 / LOCK-PKM-08): 지식 카테고리 — concept, fact, procedure, decision, reference, opinion, code_snippet, bookmark

> LOCK (기존 명세 §4.1 / LOCK-PKM-05): 지식그래프 엣지 타입 — RELATED_TO, TAGGED_WITH, BELONGS_TO, SOURCED_FROM, CONTRADICTS, SUPERSEDES, SUPPORTS, MENTIONS

---

## 아키텍처 개요

```
[지식 노트 편집]
    ↓
[Version Tracker]
    ├─ 변경 감지 (content diff)
    ├─ 스냅샷 생성 (불변 버전)
    ├─ 변경 유형 분류 (minor/major/structural)
    └─ 변경 사유 기록 (자동 또는 수동)
    ↓
[Version Store]
    ├─ versions: list[NoteVersion]
    ├─ diffs: list[VersionDiff]
    └─ metadata: 변경자, 시간, 사유
    ↓
[Version Operations]
    ├─ Diff: 두 버전 비교
    ├─ Rollback: 이전 버전 복원
    ├─ Timeline: 변경 이력 시각화
    └─ SUPERSEDES: 그래프 엣지 자동 생성 (LOCK-PKM-05)
```

---

## E1. Input / Output Schema

```python
# ─── 버전 저장 ───
@dataclass
class NoteVersion:
    version_id: UUID
    note_id: UUID
    version_number: int                          # 1, 2, 3, ...
    title: str
    content: str                                 # 전체 스냅샷
    category: KnowledgeCategory                  # LOCK-PKM-08
    tags: TagBundle
    metadata: VersionMetadata
    created_at: datetime
    is_current: bool                             # 최신 버전 여부

@dataclass
class VersionMetadata:
    change_type: Literal["minor", "major", "structural"]
    change_reason: str                           # "오타 수정" / "내용 보강" / "구조 변경"
    changed_by: Literal["user", "auto_update", "merge", "ai_suggestion"]
    content_hash: str                            # SHA-256
    word_count: int
    diff_summary: str                            # "title 변경, content 15줄 추가"

# ─── Diff 결과 ───
@dataclass
class VersionDiff:
    note_id: UUID
    from_version: int
    to_version: int
    diff_ops: list[DiffOp]
    additions: int                               # 추가된 줄 수
    deletions: int                               # 삭제된 줄 수
    similarity: float                            # 0..1 (두 버전 유사도)

@dataclass
class DiffOp:
    op_type: Literal["insert", "delete", "replace", "equal"]
    from_line: int
    to_line: int
    old_text: Optional[str]
    new_text: Optional[str]

# ─── 롤백 요청 ───
@dataclass
class RollbackRequest:
    note_id: UUID
    target_version: int                          # 복원할 버전 번호
    rollback_reason: str
    create_backup: bool = True                   # 현재 버전 백업 후 롤백

# ─── 이력 조회 ───
@dataclass
class VersionHistoryRequest:
    note_id: UUID
    limit: int = 20
    include_diffs: bool = False

@dataclass
class VersionHistoryResponse:
    note_id: UUID
    total_versions: int
    versions: list[NoteVersionSummary]
    timeline: list[TimelineEntry]

@dataclass
class NoteVersionSummary:
    version_number: int
    created_at: datetime
    change_type: str
    change_reason: str
    changed_by: str
    word_count: int
    diff_summary: str
```

## E2. Algorithm — 버전 생성

```python
# version_tracker.py
class VersionTracker:
    """지식 노트 변경 시 자동 버전 스냅샷"""
    
    MINOR_THRESHOLD = 0.95           # similarity > 0.95 → minor
    STRUCTURAL_INDICATORS = [        # 구조 변경 감지
        "category_changed",
        "title_changed",
        "tags_restructured",
    ]
    
    async def create_version(
        self, note: KnowledgeNote, previous: Optional[NoteVersion],
    ) -> NoteVersion:
        # 1. 변경 유형 분류
        if previous is None:
            change_type = "major"
            change_reason = "초기 생성"
            diff_summary = f"신규 노트 ({len(note.body.split())} 단어)"
        else:
            diff = self._compute_diff(previous.content, note.body)
            similarity = self._compute_similarity(previous.content, note.body)
            
            if any(self._check_structural(note, previous)):
                change_type = "structural"
                change_reason = self._auto_reason_structural(note, previous)
            elif similarity >= self.MINOR_THRESHOLD:
                change_type = "minor"
                change_reason = self._auto_reason_minor(diff)
            else:
                change_type = "major"
                change_reason = self._auto_reason_major(diff)
            
            diff_summary = f"+{diff.additions} -{diff.deletions} 줄"
        
        # 2. 스냅샷 생성
        version = NoteVersion(
            version_id=uuid7(),
            note_id=note.id,
            version_number=(previous.version_number + 1) if previous else 1,
            title=note.title,
            content=note.body,
            category=note.category,
            tags=note.tags,
            metadata=VersionMetadata(
                change_type=change_type,
                change_reason=change_reason,
                changed_by="user",
                content_hash=hashlib.sha256(note.body.encode()).hexdigest(),
                word_count=len(note.body.split()),
                diff_summary=diff_summary,
            ),
            created_at=datetime.now(),
            is_current=True,
        )
        
        # 3. 이전 버전 is_current = False
        if previous:
            previous.is_current = False
            await self.db.update_version(previous)
        
        await self.db.save_version(version)
        
        # 4. SUPERSEDES 엣지 생성 (LOCK-PKM-05)
        if previous and change_type == "major":
            await self.kg.create_edge(
                from_id=note.id,
                to_id=previous.version_id,  # 이전 스냅샷(version_id) 참조
                edge_type="SUPERSEDES",
                metadata={"from_version": previous.version_number, "to_version": version.version_number},
            )
        
        return version
```

## E3. Algorithm — Diff 비교

```python
# diff_engine.py
class DiffEngine:
    """두 버전 간 줄 단위 Diff 계산"""
    
    def compute(self, old_text: str, new_text: str) -> VersionDiff:
        old_lines = old_text.splitlines()
        new_lines = new_text.splitlines()
        
        # unified diff 계산 (difflib 기반)
        matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
        ops = []
        additions = 0
        deletions = 0
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                ops.append(DiffOp(op_type="equal", from_line=i1, to_line=j1,
                                  old_text=None, new_text=None))
            elif tag == "insert":
                inserted = "\n".join(new_lines[j1:j2])
                ops.append(DiffOp(op_type="insert", from_line=i1, to_line=j1,
                                  old_text=None, new_text=inserted))
                additions += j2 - j1
            elif tag == "delete":
                deleted = "\n".join(old_lines[i1:i2])
                ops.append(DiffOp(op_type="delete", from_line=i1, to_line=j1,
                                  old_text=deleted, new_text=None))
                deletions += i2 - i1
            elif tag == "replace":
                old = "\n".join(old_lines[i1:i2])
                new = "\n".join(new_lines[j1:j2])
                ops.append(DiffOp(op_type="replace", from_line=i1, to_line=j1,
                                  old_text=old, new_text=new))
                additions += j2 - j1
                deletions += i2 - i1
        
        similarity = matcher.ratio()
        
        return VersionDiff(
            diff_ops=ops,
            additions=additions,
            deletions=deletions,
            similarity=similarity,
        )
```

## E4. Algorithm — 롤백

```python
# rollback.py
class RollbackManager:
    """이전 버전으로 복원"""
    
    async def rollback(self, req: RollbackRequest) -> NoteVersion:
        # 1. 대상 버전 조회
        target = await self.db.get_version(req.note_id, req.target_version)
        if not target:
            raise VersionError("TARGET_VERSION_NOT_FOUND")
        
        # 2. 현재 버전 백업 (선택)
        current = await self.db.get_current_version(req.note_id)
        if req.create_backup:
            current.metadata.change_reason = f"롤백 전 백업 (v{current.version_number})"
            # 현재 상태를 그대로 보존 (이미 스냅샷이므로 추가 작업 불필요)
        
        # 3. 대상 버전 내용으로 새 버전 생성
        note = await self.db.get_note(req.note_id)
        note.title = target.title
        note.body = target.content
        note.category = target.category
        note.tags = target.tags
        
        # 4. 새 버전 번호로 스냅샷 (롤백도 새 버전)
        new_version = await self.version_tracker.create_version(note, current)
        new_version.metadata.change_type = "major"
        new_version.metadata.change_reason = (
            f"v{req.target_version}으로 롤백: {req.rollback_reason}"
        )
        new_version.metadata.changed_by = "user"
        
        await self.db.update_version(new_version)
        await self.db.update_note(note)
        
        return new_version
```

## E5. Algorithm — 변경 이력 타임라인

```python
# timeline.py
class VersionTimeline:
    """변경 이력 시각화용 타임라인 데이터"""
    
    async def get_timeline(self, req: VersionHistoryRequest) -> VersionHistoryResponse:
        versions = await self.db.get_versions(req.note_id, limit=req.limit)
        
        timeline = []
        for v in versions:
            entry = TimelineEntry(
                version_number=v.version_number,
                created_at=v.created_at,
                change_type=v.metadata.change_type,
                change_reason=v.metadata.change_reason,
                changed_by=v.metadata.changed_by,
                diff_summary=v.metadata.diff_summary,
                word_count=v.metadata.word_count,
                # 간단 차트용: 누적 단어 수 변화
                word_count_delta=self._calc_delta(v, versions),
            )
            timeline.append(entry)
        
        return VersionHistoryResponse(
            note_id=req.note_id,
            total_versions=len(versions),
            versions=[self._to_summary(v) for v in versions],
            timeline=timeline,
        )

@dataclass
class TimelineEntry:
    version_number: int
    created_at: datetime
    change_type: str
    change_reason: str
    changed_by: str
    diff_summary: str
    word_count: int
    word_count_delta: int                        # 이전 대비 변화
```

## E6. 자동 정리 정책

```python
# version_retention.py
RETENTION_POLICY = {
    "max_versions_per_note": 100,    # 최대 100개 버전
    "minor_retention_days": 30,      # minor 변경은 30일 후 정리
    "major_retention": "forever",    # major 변경은 영구 보존
    "structural_retention": "forever",  # 구조 변경은 영구 보존
}

async def cleanup_old_versions(note_id: UUID):
    """오래된 minor 버전 정리 (major/structural은 보존)"""
    versions = await db.get_versions(note_id)
    
    if len(versions) <= RETENTION_POLICY["max_versions_per_note"]:
        return
    
    cutoff = datetime.now() - timedelta(days=RETENTION_POLICY["minor_retention_days"])
    to_delete = [
        v for v in versions
        if v.metadata.change_type == "minor"
        and v.created_at < cutoff
        and not v.is_current
    ]
    
    # 최소 10개 버전은 보존
    keep_count = len(versions) - len(to_delete)
    if keep_count < 10:
        to_delete = to_delete[:len(versions) - 10]
    
    for v in to_delete:
        await db.delete_version(v.version_id)
```

## E7. 에러 처리 + 성능 요구사항

```python
VERSION_SLA = {
    "snapshot_creation_p50_ms": 50,
    "diff_computation_p50_ms": 100,
    "rollback_p50_ms": 200,
    "timeline_query_p50_ms": 100,
    "max_content_size_kb": 500,      # 버전당 최대 콘텐츠 크기
}

class VersionError(Exception):
    code: Literal[
        "TARGET_VERSION_NOT_FOUND",
        "CONTENT_TOO_LARGE",
        "MAX_VERSIONS_EXCEEDED",
        "ROLLBACK_CONFLICT",
    ]
```

---

## 의존성

| 방향 | 대상 | 내용 |
|------|------|------|
| ← | 01_knowledge-capture | 노트 생성/수정 이벤트 |
| ← | 02_knowledge-graph | SUPERSEDES 엣지 (LOCK-PKM-05) |
| → | knowledge_statistics.md (M-030) | 버전 통계 (변경 빈도, 롤백 수) |
| → | 04_knowledge-conflict | 충돌 해결 시 버전 비교 |
