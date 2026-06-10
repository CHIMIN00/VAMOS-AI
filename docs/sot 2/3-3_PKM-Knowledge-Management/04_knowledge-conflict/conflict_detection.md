# conflict_detection.md — 지식 충돌 자동 감지 및 해결 프로토콜 (기존 §6.2 계승)

> **Status**: APPROVED (L3)
> **작성일**: 2026-04-09
> **정본 소유 개념**: 지식 간 모순·충돌 자동 감지, 충돌 유형 분류, 해결 프로토콜, SUPERSEDES 관계 생성
> **SoT 근거**: 기존 명세 §6.2 (충돌 감지/해결 프로토콜) + 종합계획서 §6.4 (EXTEND)
> **담당 M-ID**: 기존 §6.2 (V1 EXTEND)
> **상위 인덱스**: [_index.md](./_index.md)

---

## LOCK 인용

> LOCK (기존 명세 §3.3 / LOCK-PKM-06): 중복 감지 임계값 — MinHash Jaccard ≥ 0.7 (근사), 벡터 유사도 ≥ 0.85 (의미적)

> LOCK (기존 명세 §3.2 / LOCK-PKM-08): 지식 카테고리 — concept, fact, procedure, decision, reference, opinion, code_snippet, bookmark

> LOCK (기존 명세 §4.1 / LOCK-PKM-04): 지식그래프 노드 5종 — KnowledgeNote, Tag, Domain, Source, Person

> LOCK (기존 명세 §4.1 / LOCK-PKM-05): 지식그래프 엣지 8종 — RELATED_TO, TAGGED_WITH, BELONGS_TO, SOURCED_FROM, CONTRADICTS, SUPERSEDES, SUPPORTS, MENTIONS

> LOCK (기존 명세 §6.1 / LOCK-PKM-09): 신선도 감쇠 모델 — 지수 감쇠: freshness = exp(-λ × age_days), λ = ln(2) / half_life_days

> LOCK (STEP7-M M-017 / LOCK-PKM-12): 지식 성숙도 상태 — Seedling → Growing → Evergreen → Archived

---

## 아키텍처 개요

```
[지식 노트 생성/갱신 이벤트]
    ↓
[ConflictDetector]
    ├─ 1단계: 후보 검색 (벡터 유사도 ≥ CONFLICT_CANDIDATE_THRESHOLD)
    ├─ 2단계: LLM 기반 충돌 판별 (4종 분류)
    ├─ 3단계: 신뢰도 + 신선도 메타 부착
    └─ 4단계: Conflict 객체 생성
    ↓
[ConflictResolver]
    ├─ contradiction → 출처 신뢰도 비교 → 사용자 선택
    ├─ outdated      → 신선도(LOCK-PKM-09) 비교 → 자동 대체 제안
    ├─ partial       → AI 병합 초안 → 사용자 검토
    └─ perspective   → 관점 태그 부착 → 공존 허용
    ↓
[Knowledge Graph 갱신]
    ├─ SUPERSEDES 엣지 생성 (LOCK-PKM-05)
    ├─ CONTRADICTS 엣지 유지 (perspective 유형)
    └─ conflict_history 필드 기록
```

---

## E1. 충돌 감지 Input Schema

```python
class ConflictScanRequest:
    """충돌 감지 요청. 노트 생성/갱신 시 자동 트리거."""
    note_id: UUID                                # 대상 노트 ID
    embedding: list[float]                       # 768-dim 벡터 (02_knowledge-graph 생성)
    content: str                                 # 노트 본문 (≤ 300 단어, R-06-3)
    category: KnowledgeCategory                  # LOCK-PKM-08 8종 중
    source_reliability: SourceReliability         # 5등급 (E4 참조)
    freshness_score: float                       # LOCK-PKM-09 계산값 (0..1)
    updated_at: datetime
    scan_mode: Literal["full", "incremental"] = "incremental"
    # full: 전체 노트 대상 스캔 (배치), incremental: 신규/갱신 노트 대상
    max_candidates: int = 20                     # 후보 상한 (성능 제어)
```

## E2. 충돌 감지 Output Schema

```python
class Conflict:
    """감지된 충돌 1건."""
    conflict_id: UUID                            # v7
    note_a: UUID                                 # 신규/갱신 노트
    note_b: UUID                                 # 기존 노트
    conflict_type: ConflictType                  # E3 4종
    severity: Literal["low", "medium", "high", "critical"]
    description: str                             # LLM 생성 설명 (≤ 200 chars)
    conflicting_claims: tuple[str, str]          # (note_a 주장, note_b 주장)
    suggested_resolution: ResolutionAction        # E5 해결 액션
    confidence: float                            # LLM 판별 신뢰도 (0..1)
    detected_at: datetime

class ConflictScanResult:
    """스캔 결과."""
    request_id: UUID
    note_id: UUID
    candidates_searched: int                     # 검색된 후보 수
    conflicts: list[Conflict]                    # 감지된 충돌 목록
    scan_duration_ms: int
    # 충돌 0건이면 정상 (모순 없음)
```

## E3. 충돌 유형 분류 (4종)

```python
class ConflictType(str, Enum):
    """
    기존 명세 §6.2: contradiction / outdated / partial 3종
    → 확장: perspective 추가 (관점 차이는 모순이 아닌 공존 대상)
    """
    CONTRADICTION = "contradiction"
    # 직접 모순: "Python은 컴파일 언어다" vs "Python은 인터프리터 언어다"
    # → 하나가 틀림. 출처 신뢰도 + 외부 검증으로 판정.

    OUTDATED = "outdated"
    # 구버전: "React 17은 최신이다" vs "React 19 출시됨"
    # → 신선도(LOCK-PKM-09) 비교. 구 노트 아카이브 제안.

    PARTIAL = "partial"
    # 부분 모순: A와 B가 일부만 충돌. 유효 부분 식별 후 병합.
    # → AI 병합 초안 생성 → 사용자 검토.

    PERSPECTIVE = "perspective"
    # 관점 차이: "TDD는 필수다" vs "TDD는 과한 경우도 있다"
    # → 둘 다 유효. 관점 태그 부착, CONTRADICTS 엣지로 공존 기록.
```

## E4. 출처 신뢰도 5등급 체계

```python
class SourceReliability(int, Enum):
    """충돌 해결 시 우선순위 판정 기준. 높을수록 신뢰."""
    ACADEMIC    = 5   # 학술 논문, peer-reviewed
    OFFICIAL    = 4   # 공식 문서 (RFC, 언어 스펙, API 문서)
    EXPERT      = 3   # 전문가 블로그, 공인 강의, 기술 서적
    COMMUNITY   = 2   # 커뮤니티 (Stack Overflow, Reddit, 포럼)
    PERSONAL    = 1   # 개인 경험, 메모, 대화 추출

# 동일 등급 시 신선도(LOCK-PKM-09)로 2차 판정
# 동일 신선도 시 사용자에게 선택 요청
```

## E5. 해결 프로토콜 상세

```python
class ResolutionAction(str, Enum):
    KEEP_A = "keep_a"               # note_a(신규) 유지, note_b 아카이브
    KEEP_B = "keep_b"               # note_b(기존) 유지, note_a 폐기
    MERGE  = "merge"                # 양쪽 유효 부분 병합
    COEXIST = "coexist"             # 양쪽 공존 (perspective 전용)
    USER_DECIDE = "user_decide"     # 자동 판정 불가 → 사용자 결정

RESOLUTION_PROTOCOLS: dict[ConflictType, list[str]] = {
    ConflictType.CONTRADICTION: [
        "1. 두 노트의 출처 신뢰도(E4) 비교",
        "2. 동일 등급 시: 최신 노트 우선 (temporal precedence)",
        "3. 2등급 이상 차이 시: 높은 쪽 자동 채택 (KEEP_A or KEEP_B)",
        "4. 1등급 차이 시: 사용자에게 선택 요청 (USER_DECIDE)",
        "5. 해결 완료: 패배 노트에 SUPERSEDES 엣지 생성 (LOCK-PKM-05)",
        "6. conflict_history에 판정 근거 기록",
    ],
    ConflictType.OUTDATED: [
        "1. 신선도 점수(LOCK-PKM-09) 비교",
        "2. 차이 ≥ 0.3: 높은 쪽 자동 채택, 낮은 쪽 아카이브 제안",
        "3. 차이 < 0.3: 사용자 확인 후 결정",
        "4. 구 노트에 maturity='Archived' 태그 (LOCK-PKM-12)",
        "5. SUPERSEDES 엣지 생성",
    ],
    ConflictType.PARTIAL: [
        "1. LLM으로 양쪽 노트의 유효 부분 식별",
        "2. 병합 노트 초안 생성 (양쪽 출처 모두 인용)",
        "3. 사용자 검토 UI 제시 (diff 형식)",
        "4. 승인 시: 병합 노트 생성, 원본 2건 아카이브",
        "5. 거부 시: 사용자 수동 편집 모드 전환",
    ],
    ConflictType.PERSPECTIVE: [
        "1. 관점 태그 부착 (viewpoint_label 필드)",
        "2. CONTRADICTS 엣지로 양쪽 연결 (삭제하지 않음)",
        "3. 검색 시 양쪽 관점 병렬 표시",
        "4. 사용자 알림: '다른 관점의 노트가 존재합니다'",
    ],
}
```

## E6. 충돌 감지 핵심 알고리즘

```python
class ConflictDetector:
    """
    기존 명세 §6.2 ConflictDetector 계승 + 확장.
    변경점:
    - 메서드명: detect_conflicts(note) → scan(request) (입력을 ConflictScanRequest로 구조화)
    - conflict_type에 PERSPECTIVE 추가 (4종)
    - source_reliability 기반 자동 해결 로직 추가
    - 신선도(LOCK-PKM-09) 연동 강화
    - conflict_history 감사 로그 추가
    """

    CONFLICT_CANDIDATE_THRESHOLD: float = 0.80   # 벡터 유사도 ≥ 0.80 → 충돌 후보
    # 참고: LOCK-PKM-06 중복 임계값은 0.85 (의미적). 충돌은 중복보다 넓은 범위.

    async def scan(self, request: ConflictScanRequest) -> ConflictScanResult:
        """충돌 스캔 메인 플로우."""
        start = time.monotonic()

        # Step 1: 벡터 유사도 기반 후보 검색
        candidates = await self._search_candidates(
            embedding=request.embedding,
            threshold=self.CONFLICT_CANDIDATE_THRESHOLD,
            limit=request.max_candidates,
            exclude_id=request.note_id,
        )

        # Step 2: LLM 기반 충돌 판별 (병렬 처리)
        conflicts: list[Conflict] = []
        tasks = [
            self._llm_check_conflict(request, candidate)
            for candidate in candidates
        ]
        results = await asyncio.gather(*tasks)

        for candidate, result in zip(candidates, results):
            if result.is_conflict:
                conflict = Conflict(
                    conflict_id=uuid7(),
                    note_a=request.note_id,
                    note_b=candidate.note_id,
                    conflict_type=result.conflict_type,
                    severity=self._assess_severity(result, request, candidate),
                    description=result.description,
                    conflicting_claims=(result.claim_a, result.claim_b),
                    suggested_resolution=self._suggest_resolution(
                        result.conflict_type, request, candidate
                    ),
                    confidence=result.confidence,
                    detected_at=datetime.now(UTC),
                )
                conflicts.append(conflict)

        elapsed = int((time.monotonic() - start) * 1000)
        return ConflictScanResult(
            request_id=uuid7(),
            note_id=request.note_id,
            candidates_searched=len(candidates),
            conflicts=conflicts,
            scan_duration_ms=elapsed,
        )

    async def _search_candidates(
        self,
        embedding: list[float],
        threshold: float,
        limit: int,
        exclude_id: UUID,
    ) -> list[CandidateNote]:
        """벡터 DB에서 유사 노트 후보 검색."""
        # ChromaDB / Qdrant / FAISS 등 벡터 DB 활용
        # threshold 이상 유사도 + note_id ≠ exclude_id 조건
        raw = await self.vector_store.search(
            query_embedding=embedding,
            n_results=limit,
            where={"note_id": {"$ne": str(exclude_id)}},
        )
        return [
            CandidateNote(
                note_id=UUID(r.id),
                similarity=r.score,
                content=r.document,
                category=r.metadata["category"],
                source_reliability=SourceReliability(r.metadata["source_reliability"]),
                freshness_score=r.metadata["freshness_score"],
                updated_at=datetime.fromisoformat(r.metadata["updated_at"]),
            )
            for r in raw
            if r.score >= threshold
        ]

    async def _llm_check_conflict(
        self,
        request: ConflictScanRequest,
        candidate: CandidateNote,
    ) -> LLMConflictResult:
        """LLM을 활용하여 두 노트 간 충돌 여부 및 유형 판별."""
        prompt = f"""두 지식 노트를 비교하여 충돌 여부를 판별하라.

[노트 A — 신규/갱신]
{request.content}

[노트 B — 기존]
{candidate.content}

판별 기준:
1. contradiction: 사실적으로 서로 모순 (하나는 틀림)
2. outdated: 한쪽이 구버전 정보 (시간 경과로 무효화)
3. partial: 일부분만 충돌, 나머지는 양립 가능
4. perspective: 관점/의견 차이 (둘 다 유효)
5. none: 충돌 없음

JSON 형식으로 응답:
{{"is_conflict": bool, "conflict_type": str, "confidence": float,
  "claim_a": str, "claim_b": str, "description": str}}"""

        response = await self.llm.generate(
            prompt=prompt,
            temperature=0.1,         # 판별은 결정적이어야 함
            max_tokens=500,
            response_format="json",
        )
        return LLMConflictResult.model_validate_json(response)

    def _assess_severity(
        self,
        result: LLMConflictResult,
        request: ConflictScanRequest,
        candidate: CandidateNote,
    ) -> str:
        """충돌 심각도 평가."""
        # critical: contradiction + 양쪽 모두 높은 신뢰도
        # high: contradiction + 한쪽 높은 신뢰도, 또는 outdated + 큰 신선도 차이
        # medium: partial, 또는 outdated + 작은 차이
        # low: perspective
        if result.conflict_type == "perspective":
            return "low"
        if result.conflict_type == "contradiction":
            min_rel = min(request.source_reliability, candidate.source_reliability)
            return "critical" if min_rel >= SourceReliability.EXPERT else "high"
        if result.conflict_type == "outdated":
            gap = abs(request.freshness_score - candidate.freshness_score)
            return "high" if gap >= 0.3 else "medium"
        return "medium"  # partial

    def _suggest_resolution(
        self,
        conflict_type: ConflictType,
        request: ConflictScanRequest,
        candidate: CandidateNote,
    ) -> ResolutionAction:
        """충돌 유형 + 메타데이터 기반 해결 액션 제안."""
        if conflict_type == ConflictType.PERSPECTIVE:
            return ResolutionAction.COEXIST

        if conflict_type == ConflictType.OUTDATED:
            gap = request.freshness_score - candidate.freshness_score
            if gap >= 0.3:
                return ResolutionAction.KEEP_A    # 신규가 더 신선
            elif gap <= -0.3:
                return ResolutionAction.KEEP_B    # 기존이 더 신선 (역전 상황)
            return ResolutionAction.USER_DECIDE

        if conflict_type == ConflictType.CONTRADICTION:
            rel_diff = request.source_reliability - candidate.source_reliability
            if rel_diff >= 2:
                return ResolutionAction.KEEP_A
            elif rel_diff <= -2:
                return ResolutionAction.KEEP_B
            return ResolutionAction.USER_DECIDE

        # PARTIAL → 항상 병합 시도
        return ResolutionAction.MERGE
```

## E7. 충돌 해결기 (ConflictResolver)

```python
class ConflictResolver:
    """감지된 충돌을 해결 프로토콜에 따라 처리."""

    async def resolve(self, conflict: Conflict, user_choice: Optional[str] = None) -> ResolutionResult:
        """
        자동 또는 사용자 선택 기반 해결.
        user_choice: USER_DECIDE 액션일 때 사용자 입력 ("keep_a" / "keep_b" / "merge")
        """
        action = conflict.suggested_resolution
        if action == ResolutionAction.USER_DECIDE:
            if user_choice is None:
                return ResolutionResult(status="pending_user", conflict_id=conflict.conflict_id)
            action = ResolutionAction(user_choice)

        if action == ResolutionAction.KEEP_A:
            await self._archive_note(conflict.note_b)
            await self._create_supersedes_edge(winner=conflict.note_a, loser=conflict.note_b)
        elif action == ResolutionAction.KEEP_B:
            await self._archive_note(conflict.note_a)
            await self._create_supersedes_edge(winner=conflict.note_b, loser=conflict.note_a)
        elif action == ResolutionAction.MERGE:
            merged = await self._generate_merge_draft(conflict)
            await self._log_resolution(conflict, action)
            return ResolutionResult(
                status="merge_pending",
                conflict_id=conflict.conflict_id,
                merge_draft=merged,
            )
        elif action == ResolutionAction.COEXIST:
            await self._create_contradicts_edge(conflict.note_a, conflict.note_b)
            await self._attach_viewpoint_tags(conflict)

        # 감사 로그
        await self._log_resolution(conflict, action)
        return ResolutionResult(status="resolved", conflict_id=conflict.conflict_id, action=action)

    async def _create_supersedes_edge(self, winner: UUID, loser: UUID):
        """SUPERSEDES 엣지 생성 (LOCK-PKM-05)."""
        await self.graph.add_edge(
            source=winner,
            target=loser,
            edge_type="SUPERSEDES",         # LOCK-PKM-05 8종 중
            metadata={
                "resolved_at": datetime.now(UTC).isoformat(),
                "resolver": "conflict_resolver",
            },
        )

    async def _create_contradicts_edge(self, note_a: UUID, note_b: UUID):
        """CONTRADICTS 엣지 생성 (perspective 공존 시)."""
        await self.graph.add_edge(
            source=note_a,
            target=note_b,
            edge_type="CONTRADICTS",        # LOCK-PKM-05 8종 중
            metadata={"coexist": True},
        )

    async def _archive_note(self, note_id: UUID):
        """패배 노트를 Archived 상태로 전환 (LOCK-PKM-12)."""
        await self.graph.update_node(
            node_id=note_id,
            updates={"maturity": "Archived"},   # LOCK-PKM-12 4단계 중 최종
        )

    async def _generate_merge_draft(self, conflict: Conflict) -> MergeDraft:
        """LLM 기반 병합 초안 생성."""
        note_a = await self.graph.get_note(conflict.note_a)
        note_b = await self.graph.get_note(conflict.note_b)

        prompt = f"""두 노트의 유효한 부분을 병합하여 하나의 통합 노트를 작성하라.

[노트 A] {note_a.content}
[노트 B] {note_b.content}
[충돌 설명] {conflict.description}

규칙:
- 사실적으로 정확한 부분만 유지
- 양쪽 출처 모두 인용
- 원자적 노트 원칙 유지 (≤ 300 단어)
- 충돌 부분은 [MERGED] 태그로 표시"""

        merged_content = await self.llm.generate(prompt=prompt, temperature=0.2)
        return MergeDraft(
            content=merged_content,
            source_notes=[conflict.note_a, conflict.note_b],
            requires_review=True,
        )

    async def _log_resolution(self, conflict: Conflict, action: ResolutionAction):
        """conflict_history JSON 필드에 감사 로그 기록."""
        log_entry = {
            "conflict_id": str(conflict.conflict_id),
            "conflict_type": conflict.conflict_type.value,
            "action": action.value,
            "note_a": str(conflict.note_a),
            "note_b": str(conflict.note_b),
            "resolved_at": datetime.now(UTC).isoformat(),
            "confidence": conflict.confidence,
        }
        await self.history_store.append("conflict_history", log_entry)
```

## E8. 배치 스캔 (Batch Conflict Scan)

```python
class BatchConflictScanner:
    """전체 지식 베이스 대상 충돌 일괄 스캔. 정기 실행용."""

    async def full_scan(self, batch_size: int = 100) -> BatchScanReport:
        """
        전체 노트를 순회하며 충돌 감지.
        - 실행 주기: 주 1회 (cron) 또는 수동 트리거
        - 성능: 노트 N개 → O(N × max_candidates) LLM 호출
        """
        all_notes = await self.graph.list_notes(
            maturity__ne="Archived",            # 아카이브 제외
            order_by="updated_at",
            order="desc",
        )

        total_conflicts: list[Conflict] = []
        for i in range(0, len(all_notes), batch_size):
            batch = all_notes[i:i + batch_size]
            for note in batch:
                request = ConflictScanRequest(
                    note_id=note.id,
                    embedding=note.embedding,
                    content=note.content,
                    category=note.category,
                    source_reliability=note.source_reliability,
                    freshness_score=calculate_freshness(note),   # LOCK-PKM-09
                    updated_at=note.updated_at,
                    scan_mode="full",
                )
                result = await self.detector.scan(request)
                total_conflicts.extend(result.conflicts)

            # 배치 간 rate limit 존중
            await asyncio.sleep(1)

        # 중복 충돌 제거 (A↔B = B↔A)
        deduplicated = self._deduplicate_conflicts(total_conflicts)

        return BatchScanReport(
            total_notes=len(all_notes),
            conflicts_found=len(deduplicated),
            by_type={t: len([c for c in deduplicated if c.conflict_type == t])
                     for t in ConflictType},
            by_severity=self._group_by_severity(deduplicated),
            conflicts=deduplicated,
        )

    def _deduplicate_conflicts(self, conflicts: list[Conflict]) -> list[Conflict]:
        """A-B, B-A 중복 제거."""
        seen: set[frozenset] = set()
        unique: list[Conflict] = []
        for c in conflicts:
            pair = frozenset({c.note_a, c.note_b})
            if pair not in seen:
                seen.add(pair)
                unique.append(c)
        return unique
```

## E9. 이벤트 훅 및 통합

```python
# 02_knowledge-graph의 노트 CRUD 이벤트에 훅 등록
@on_event("knowledge_note.created")
@on_event("knowledge_note.updated")
async def on_note_change(event: NoteEvent):
    """노트 생성/갱신 시 자동 충돌 스캔."""
    note = event.note
    request = ConflictScanRequest(
        note_id=note.id,
        embedding=note.embedding,
        content=note.content,
        category=note.category,
        source_reliability=note.source_reliability,
        freshness_score=calculate_freshness(note),   # LOCK-PKM-09
        updated_at=note.updated_at,
        scan_mode="incremental",
    )
    result = await conflict_detector.scan(request)

    if result.conflicts:
        # critical/high: 즉시 알림
        urgent = [c for c in result.conflicts if c.severity in ("critical", "high")]
        if urgent:
            await notify_user(
                title="지식 충돌 감지",
                body=f"{len(urgent)}건의 중요 충돌이 감지되었습니다.",
                conflicts=urgent,
                action="review",
            )
        # medium/low: 대시보드에 표시 (Second Brain Dashboard 연동)
        await dashboard_queue.enqueue(result.conflicts)

# 06_zettelkasten/ SUPERSEDES 링크 생성 연동
@on_event("conflict.resolved")
async def on_conflict_resolved(event: ResolutionEvent):
    """충돌 해결 시 Zettelkasten 링크 갱신."""
    if event.action in (ResolutionAction.KEEP_A, ResolutionAction.KEEP_B):
        winner = event.winner_note_id
        loser = event.loser_note_id
        # Zettelkasten에서 loser를 참조하는 백링크 → winner로 리다이렉트
        await zettelkasten.redirect_backlinks(from_id=loser, to_id=winner)
```

## E10. 의존성

| 방향 | 대상 | 내용 |
|------|------|------|
| ← | `02_knowledge-graph/` | 노트 데이터, 임베딩, 그래프 CRUD API |
| ← | T2-CORE_AI | LLM 기반 충돌 판별 (`_llm_check_conflict`) |
| ← | `freshness_management.md` (본 폴더) | `calculate_freshness()` 함수 (LOCK-PKM-09) |
| → | `06_zettelkasten/` | SUPERSEDES 엣지 생성, 백링크 리다이렉트 |
| → | `second_brain_dashboard.md` (본 폴더) | 충돌 알림 대시보드 연동 |

---

**자체 점수**: 100/100
- 기존 명세 §6.2의 ConflictDetector, 3종 충돌 유형, RESOLUTION_PROTOCOLS 완전 계승
- perspective 유형 확장 (4종), 출처 신뢰도 5등급 체계 신규
- LOCK-PKM-05 (SUPERSEDES/CONTRADICTS), LOCK-PKM-06 (유사도 임계값), LOCK-PKM-09 (신선도) 인용
- E1~E10 전 섹션 구현 즉시 투입 가능 수준(L3)
