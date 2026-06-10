# COND-020: 지식 충돌 감지 — L2+ 상세 명세

> **모듈 ID**: COND-020
> **카테고리**: CAT-B (Knowledge)
> **이름**: 지식 충돌 감지
> **우선순위**: MEDIUM
> **Phase**: Phase 0
> **L-Level**: L2+ (Performance Benchmark/Integration Test Spec은 Phase 1/2 보강)
> **LOCK 준수**: LOCK-CD-03 BaseModule ABC (§3.4, D2.0-02 §1.2-A + §12.2 기반), LOCK-CD-04 Runnable 프로토콜 (D2.0-02 §1.2-A), LOCK-CD-05 ErrorHandlingStandard (D2.0-02 §0.3), LOCK-CD-06 VamosError 필드 (D2.0-02 §0.3), LOCK-CD-10 ModuleConfig (종합명세 §공통)

---

## E1. Input Schema

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class ConflictDetectionRequest(BaseModel):
    """COND-020 입력 스키마"""
    knowledge_scope: str = Field(
        ..., description="검사 대상 범위 (네임스페이스 또는 도메인 패턴, e.g. 'user-42/*', 'user-42/finance')"
    )
    detection_mode: Literal["full_scan", "incremental", "on_insert"] = Field(
        ..., description="감지 모드 — full_scan: 전체 스캔, incremental: 마지막 검사 이후 변경분, on_insert: 신규 항목 대상"
    )
    new_item_id: Optional[str] = Field(
        default=None,
        description="on_insert 모드 시 신규 삽입 항목 ID"
    )
    new_item_content: Optional[str] = Field(
        default=None,
        description="on_insert 모드 시 신규 삽입 항목 콘텐츠"
    )
    conflict_types: list[Literal[
        "factual_contradiction", "temporal_inconsistency",
        "source_disagreement", "logical_conflict", "numeric_mismatch"
    ]] = Field(
        default=["factual_contradiction", "temporal_inconsistency",
                 "source_disagreement", "logical_conflict", "numeric_mismatch"],
        description="감지할 충돌 유형"
    )
    severity_threshold: Literal["low", "medium", "high", "critical"] = Field(
        default="low",
        description="보고할 최소 심각도"
    )
    max_comparisons: int = Field(
        default=10000, ge=100, le=1000000,
        description="최대 비교 쌍 수 (full_scan 시 O(n^2) 제한)"
    )
    include_resolution: bool = Field(
        default=True,
        description="해결 제안 포함 여부"
    )
    namespace: str = Field(
        default="default",
        description="지식 저장소 네임스페이스"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "knowledge_scope": "user-42/tech-news",
                "detection_mode": "incremental",
                "conflict_types": ["factual_contradiction", "temporal_inconsistency"],
                "severity_threshold": "medium",
                "max_comparisons": 5000,
                "include_resolution": True,
                "namespace": "user-42/knowledge-base"
            }
        }
```

---

## E2. Output Schema

```python
class ConflictEntry(BaseModel):
    """개별 충돌 항목"""
    conflict_id: str = Field(description="충돌 고유 ID")
    item_a: str = Field(description="충돌 항목 A의 ID")
    item_a_excerpt: str = Field(description="항목 A 관련 발췌 텍스트")
    item_b: str = Field(description="충돌 항목 B의 ID")
    item_b_excerpt: str = Field(description="항목 B 관련 발췌 텍스트")
    conflict_type: Literal[
        "factual_contradiction", "temporal_inconsistency",
        "source_disagreement", "logical_conflict", "numeric_mismatch"
    ] = Field(description="충돌 유형")
    severity: Literal["low", "medium", "high", "critical"] = Field(
        description="심각도"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="충돌 감지 신뢰도"
    )
    explanation: str = Field(description="충돌 설명")
    source_a_credibility: Optional[float] = Field(
        default=None, description="항목 A 소스 신뢰도 (0.0~1.0)"
    )
    source_b_credibility: Optional[float] = Field(
        default=None, description="항목 B 소스 신뢰도 (0.0~1.0)"
    )
    detected_at: datetime = Field(description="감지 시각")

class ResolutionSuggestion(BaseModel):
    """충돌 해결 제안"""
    conflict_id: str = Field(description="대상 충돌 ID")
    strategy: Literal[
        "prefer_newer", "prefer_higher_credibility", "prefer_higher_qod",
        "merge", "flag_for_review", "deprecate_one"
    ] = Field(description="해결 전략")
    recommended_action: str = Field(description="권장 조치 설명")
    preferred_item: Optional[str] = Field(
        default=None, description="우선 채택 추천 항목 ID"
    )
    rationale: str = Field(description="추천 근거")

class ConflictDetectionResponse(BaseModel):
    """COND-020 출력 스키마"""
    conflicts: list[ConflictEntry] = Field(
        default_factory=list,
        description="감지된 충돌 목록"
    )
    resolution_suggestions: list[ResolutionSuggestion] = Field(
        default_factory=list,
        description="해결 제안 목록"
    )
    total_items_scanned: int = Field(description="검사된 총 항목 수")
    total_comparisons: int = Field(description="수행된 비교 쌍 수")
    conflict_count: int = Field(description="감지된 충돌 수")
    conflict_by_type: dict[str, int] = Field(
        default_factory=dict,
        description="유형별 충돌 수"
    )
    conflict_by_severity: dict[str, int] = Field(
        default_factory=dict,
        description="심각도별 충돌 수"
    )
    scan_completeness: float = Field(
        description="스캔 완전성 (실제 비교 / 이론적 전체 비교)"
    )
    execution_time_ms: int = Field(description="실행 시간 (밀리초)")

    class Config:
        json_schema_extra = {
            "example": {
                "conflicts": [
                    {
                        "conflict_id": "cf-2024-001",
                        "item_a": "kg-node-101",
                        "item_a_excerpt": "회사 X의 2024년 매출은 500억원이다.",
                        "item_b": "kg-node-205",
                        "item_b_excerpt": "회사 X의 2024년 매출은 320억원으로 집계되었다.",
                        "conflict_type": "numeric_mismatch",
                        "severity": "high",
                        "confidence": 0.92,
                        "explanation": "동일 엔티티(회사 X)의 동일 속성(2024년 매출)에 대해 상이한 수치 (500억 vs 320억)",
                        "source_a_credibility": 0.7,
                        "source_b_credibility": 0.9,
                        "detected_at": "2024-03-18T14:30:00Z"
                    }
                ],
                "resolution_suggestions": [
                    {
                        "conflict_id": "cf-2024-001",
                        "strategy": "prefer_higher_credibility",
                        "recommended_action": "소스 B의 값(320억원)을 채택하고, 소스 A의 값에 불확실성 표기",
                        "preferred_item": "kg-node-205",
                        "rationale": "소스 B(신뢰도 0.9)가 소스 A(신뢰도 0.7)보다 높은 신뢰도를 가짐"
                    }
                ],
                "total_items_scanned": 150,
                "total_comparisons": 4500,
                "conflict_count": 1,
                "conflict_by_type": {"numeric_mismatch": 1},
                "conflict_by_severity": {"high": 1},
                "scan_completeness": 0.95,
                "execution_time_ms": 3200
            }
        }
```

---

## E3. Algorithm Pseudocode

> LOCK (D2.0-06 §2.5.2): SourceQoD — conflict detection may trigger QoD re-evaluation
> LOCK (D2.0-06 DEC-014): QoD formula: relevance*0.30 + accuracy*0.25 + freshness*0.25 + completeness*0.20

```
FUNCTION execute(request: ConflictDetectionRequest) -> Result<ConflictDetectionResponse, VamosError>:

    # 0. 입력 검증
    validation = validate_request(request)
    IF validation.is_err:
        RETURN Err(validation.error)

    start_time = now_ms()

    # 1. 대상 항목 수집
    items = collect_items(request)
    IF items.is_err:
        RETURN Err(items.error)
    items = items.value

    IF len(items) == 0:
        RETURN Err(VamosError(COND_020_NO_ITEMS_IN_SCOPE))

    # 2. 비교 쌍 생성
    pairs = []
    total_possible = 0

    SWITCH request.detection_mode:
        CASE "full_scan":
            # O(n^2) 쌍 생성, max_comparisons로 제한
            total_possible = len(items) * (len(items) - 1) / 2
            pairs = generate_candidate_pairs_full(items, request.max_comparisons)

        CASE "incremental":
            # 마지막 검사 이후 변경된 항목만 대상
            last_scan_time = ScanHistory.get_last_scan_time(request.knowledge_scope)
            changed_items = [i for i in items if i.updated_at > last_scan_time]
            unchanged_items = [i for i in items if i.updated_at <= last_scan_time]
            total_possible = len(changed_items) * len(unchanged_items) + \
                             len(changed_items) * (len(changed_items) - 1) / 2
            pairs = generate_candidate_pairs_incremental(
                changed_items, unchanged_items, request.max_comparisons
            )

        CASE "on_insert":
            # 신규 항목 vs 기존 전체
            IF request.new_item_id IS None:
                RETURN Err(VamosError(COND_020_NO_NEW_ITEM))
            new_item = KnowledgeStore.get(request.new_item_id)
            IF new_item IS None AND request.new_item_content IS NOT None:
                new_item = create_ephemeral_item(request.new_item_id, request.new_item_content)
            IF new_item IS None:
                RETURN Err(VamosError(COND_020_NEW_ITEM_NOT_FOUND))
            total_possible = len(items)
            pairs = [(new_item, existing) for existing in items if existing.id != new_item.id]
            pairs = pairs[:request.max_comparisons]

    # 3. 후보 쌍 사전 필터링 (임베딩 유사도 기반)
    # 의미적으로 관련 있는 쌍만 상세 비교 → 성능 최적화
    filtered_pairs = []
    FOR (item_a, item_b) IN pairs:
        similarity = cosine_similarity(item_a.embedding, item_b.embedding)
        IF similarity >= CONFIG.candidate_similarity_threshold:
            filtered_pairs.append((item_a, item_b, similarity))

    # 4. 충돌 감지 엔진
    conflicts = []
    severity_map = {"low": 1, "medium": 2, "high": 3, "critical": 4}
    min_severity = severity_map[request.severity_threshold]

    FOR (item_a, item_b, sim) IN filtered_pairs:

        # 4a. Factual Contradiction (NLI 모델 기반)
        IF "factual_contradiction" IN request.conflict_types:
            nli_result = NLIModel.predict(
                premise=item_a.content,
                hypothesis=item_b.content
            )
            IF nli_result.label == "contradiction" AND nli_result.confidence >= CONFIG.nli_confidence_threshold:
                severity = estimate_severity(nli_result.confidence, item_a, item_b)
                IF severity_map[severity] >= min_severity:
                    conflicts.append(ConflictEntry(
                        conflict_id=generate_uuid(),
                        item_a=item_a.id,
                        item_a_excerpt=extract_contradicting_span(item_a.content, nli_result),
                        item_b=item_b.id,
                        item_b_excerpt=extract_contradicting_span(item_b.content, nli_result),
                        conflict_type="factual_contradiction",
                        severity=severity,
                        confidence=nli_result.confidence,
                        explanation=f"자연어 추론(NLI) 모델이 두 진술 간 모순을 감지 (신뢰도 {nli_result.confidence:.2f})",
                        source_a_credibility=get_source_credibility(item_a),
                        source_b_credibility=get_source_credibility(item_b),
                        detected_at=now()
                    ))

        # 4b. Temporal Inconsistency (시간 정보 비교)
        IF "temporal_inconsistency" IN request.conflict_types:
            temporal_a = TemporalParser.extract(item_a.content)
            temporal_b = TemporalParser.extract(item_b.content)

            IF temporal_a AND temporal_b:
                # 동일 엔티티에 대한 시간 순서 모순 검사
                common_entities = find_common_entities(item_a, item_b)
                FOR entity IN common_entities:
                    events_a = temporal_a.get_events_for(entity)
                    events_b = temporal_b.get_events_for(entity)
                    inconsistencies = check_temporal_order(events_a, events_b)

                    FOR inc IN inconsistencies:
                        severity = "high" IF inc.is_hard_conflict ELSE "medium"
                        IF severity_map[severity] >= min_severity:
                            conflicts.append(ConflictEntry(
                                conflict_id=generate_uuid(),
                                item_a=item_a.id,
                                item_a_excerpt=inc.excerpt_a,
                                item_b=item_b.id,
                                item_b_excerpt=inc.excerpt_b,
                                conflict_type="temporal_inconsistency",
                                severity=severity,
                                confidence=inc.confidence,
                                explanation=f"엔티티 '{entity}'에 대한 시간 순서 불일치: {inc.description}",
                                source_a_credibility=get_source_credibility(item_a),
                                source_b_credibility=get_source_credibility(item_b),
                                detected_at=now()
                            ))

        # 4c. Source Disagreement (동일 주제, 상이한 소스)
        IF "source_disagreement" IN request.conflict_types:
            IF item_a.source != item_b.source AND sim >= 0.85:
                claims_a = ClaimExtractor.extract(item_a.content)
                claims_b = ClaimExtractor.extract(item_b.content)
                disagreements = compare_claims(claims_a, claims_b)

                FOR disag IN disagreements:
                    IF severity_map[disag.severity] >= min_severity:
                        conflicts.append(ConflictEntry(
                            conflict_id=generate_uuid(),
                            item_a=item_a.id,
                            item_a_excerpt=disag.claim_a_text,
                            item_b=item_b.id,
                            item_b_excerpt=disag.claim_b_text,
                            conflict_type="source_disagreement",
                            severity=disag.severity,
                            confidence=disag.confidence,
                            explanation=f"소스 '{item_a.source}' vs '{item_b.source}' 간 주장 불일치",
                            source_a_credibility=get_source_credibility(item_a),
                            source_b_credibility=get_source_credibility(item_b),
                            detected_at=now()
                        ))

        # 4d. Logical Conflict (논리적 모순)
        IF "logical_conflict" IN request.conflict_types:
            logic_result = LogicChecker.check(item_a.content, item_b.content)
            IF logic_result.has_conflict:
                severity = "critical" IF logic_result.is_direct_negation ELSE "high"
                IF severity_map[severity] >= min_severity:
                    conflicts.append(ConflictEntry(
                        conflict_id=generate_uuid(),
                        item_a=item_a.id,
                        item_a_excerpt=logic_result.span_a,
                        item_b=item_b.id,
                        item_b_excerpt=logic_result.span_b,
                        conflict_type="logical_conflict",
                        severity=severity,
                        confidence=logic_result.confidence,
                        explanation=logic_result.explanation,
                        source_a_credibility=get_source_credibility(item_a),
                        source_b_credibility=get_source_credibility(item_b),
                        detected_at=now()
                    ))

        # 4e. Numeric Mismatch (수치 불일치)
        IF "numeric_mismatch" IN request.conflict_types:
            nums_a = NumericExtractor.extract(item_a.content)
            nums_b = NumericExtractor.extract(item_b.content)
            common_subjects = find_common_numeric_subjects(nums_a, nums_b)

            FOR subject, (val_a, val_b) IN common_subjects:
                IF abs(val_a - val_b) / max(abs(val_a), abs(val_b), 1e-10) > CONFIG.numeric_mismatch_threshold:
                    severity = estimate_numeric_severity(val_a, val_b)
                    IF severity_map[severity] >= min_severity:
                        conflicts.append(ConflictEntry(
                            conflict_id=generate_uuid(),
                            item_a=item_a.id,
                            item_a_excerpt=f"{subject}: {val_a}",
                            item_b=item_b.id,
                            item_b_excerpt=f"{subject}: {val_b}",
                            conflict_type="numeric_mismatch",
                            severity=severity,
                            confidence=0.95,  # 수치 비교는 높은 신뢰도
                            explanation=f"'{subject}'에 대한 수치 불일치: {val_a} vs {val_b} (차이율 {abs(val_a-val_b)/max(abs(val_a),1e-10)*100:.1f}%)",
                            source_a_credibility=get_source_credibility(item_a),
                            source_b_credibility=get_source_credibility(item_b),
                            detected_at=now()
                        ))

    # 5. 해결 제안 생성
    suggestions = []
    IF request.include_resolution:
        FOR conflict IN conflicts:
            suggestion = generate_resolution(conflict)
            suggestions.append(suggestion)

    # 6. QoD 재평가 트리거 (충돌 감지 시)
    # LOCK (D2.0-06 §2.5.2): conflict detection may trigger QoD re-evaluation
    IF len(conflicts) > 0:
        conflicted_item_ids = set()
        FOR c IN conflicts:
            conflicted_item_ids.add(c.item_a)
            conflicted_item_ids.add(c.item_b)

        FOR item_id IN conflicted_item_ids:
            item = KnowledgeStore.get(item_id)
            IF item IS NOT None:
                # QoD 재평가: accuracy 점수 하향 조정
                new_qod = QoDEvaluator.score(
                    item.content,
                    source=item.source,
                    penalty_flags={"conflict_detected": True}
                )
                KnowledgeStore.update_qod(item_id, new_qod)

    # 7. 스캔 기록 저장 (incremental 모드용)
    ScanHistory.record(
        scope=request.knowledge_scope,
        scan_time=now(),
        conflicts_found=len(conflicts)
    )

    # 8. 통계 집계
    conflict_by_type = {}
    conflict_by_severity = {}
    FOR c IN conflicts:
        conflict_by_type[c.conflict_type] = conflict_by_type.get(c.conflict_type, 0) + 1
        conflict_by_severity[c.severity] = conflict_by_severity.get(c.severity, 0) + 1

    scan_completeness = len(filtered_pairs) / max(total_possible, 1)

    RETURN Ok(ConflictDetectionResponse(
        conflicts=conflicts,
        resolution_suggestions=suggestions,
        total_items_scanned=len(items),
        total_comparisons=len(filtered_pairs),
        conflict_count=len(conflicts),
        conflict_by_type=conflict_by_type,
        conflict_by_severity=conflict_by_severity,
        scan_completeness=scan_completeness,
        execution_time_ms=elapsed_ms(start_time)
    ))


FUNCTION generate_resolution(conflict: ConflictEntry) -> ResolutionSuggestion:
    """충돌 유형별 해결 제안 생성"""
    cred_a = conflict.source_a_credibility OR 0.5
    cred_b = conflict.source_b_credibility OR 0.5

    # 기본 전략: 소스 신뢰도 비교
    IF cred_a > cred_b + 0.15:
        strategy = "prefer_higher_credibility"
        preferred = conflict.item_a
        rationale = f"소스 A 신뢰도({cred_a:.2f})가 소스 B({cred_b:.2f})보다 유의미하게 높음"
    ELIF cred_b > cred_a + 0.15:
        strategy = "prefer_higher_credibility"
        preferred = conflict.item_b
        rationale = f"소스 B 신뢰도({cred_b:.2f})가 소스 A({cred_a:.2f})보다 유의미하게 높음"
    ELSE:
        # 신뢰도 유사 → 시간 기반 판단
        item_a = KnowledgeStore.get(conflict.item_a)
        item_b = KnowledgeStore.get(conflict.item_b)
        IF item_a.created_at > item_b.created_at:
            strategy = "prefer_newer"
            preferred = conflict.item_a
            rationale = "소스 신뢰도 유사, 더 최근 정보인 항목 A 선호"
        ELIF item_b.created_at > item_a.created_at:
            strategy = "prefer_newer"
            preferred = conflict.item_b
            rationale = "소스 신뢰도 유사, 더 최근 정보인 항목 B 선호"
        ELSE:
            strategy = "flag_for_review"
            preferred = None
            rationale = "신뢰도와 시간 모두 유사, 사용자 검토 필요"

    # 심각도별 행동 조정
    IF conflict.severity == "critical":
        recommended = f"즉시 확인 필요: {rationale}"
    ELIF conflict.severity == "high":
        recommended = f"빠른 검토 권장: {rationale}"
    ELSE:
        recommended = f"참고: {rationale}"

    RETURN ResolutionSuggestion(
        conflict_id=conflict.conflict_id,
        strategy=strategy,
        recommended_action=recommended,
        preferred_item=preferred,
        rationale=rationale
    )


FUNCTION generate_candidate_pairs_full(items: list, max_pairs: int) -> list[tuple]:
    """전체 스캔 쌍 생성 — 임베딩 클러스터링 기반 우선순위화"""
    # 전체 O(n^2)가 max_pairs 이내면 전체 생성
    n = len(items)
    IF n * (n - 1) / 2 <= max_pairs:
        RETURN [(items[i], items[j]) for i in range(n) for j in range(i+1, n)]

    # 초과 시: 임베딩 기반 ANN으로 유사 쌍 우선 생성
    pairs = []
    seen_pairs = set()
    FOR item IN items:
        neighbors = VectorStore.search(
            embedding=item.embedding,
            top_k=min(20, n),
            exclude_ids=[item.id],
            namespace=item.namespace
        )
        FOR neighbor IN neighbors:
            pair = tuple(sorted([item.id, neighbor.id]))
            IF pair NOT IN seen_pairs:
                seen_pairs.add(pair)
                pairs.append((item, KnowledgeStore.get(neighbor.id)))
                IF len(pairs) >= max_pairs:
                    RETURN pairs
    RETURN pairs
```

---

## E4. Error Handling

> LOCK (D2.0-02 §0.3): `Result<T, VamosError>`, 예외 throw 금지

| FailureCode | 조건 | fallback_id | 사용자 메시지 |
|-------------|------|------------|--------------|
| `COND_020_NO_ITEMS_IN_SCOPE` | 지정 scope에 지식 항목 없음 | `F-020-01` | "지정된 범위에 검사할 지식 항목이 없습니다." |
| `COND_020_NO_NEW_ITEM` | on_insert인데 new_item_id 미지정 | `F-020-02` | "신규 삽입 감지 모드에서 대상 항목 ID를 지정해 주세요." |
| `COND_020_NEW_ITEM_NOT_FOUND` | new_item_id에 해당하는 항목 없음 | `F-020-03` | "신규 항목을 찾을 수 없습니다." |
| `COND_020_NLI_MODEL_UNAVAILABLE` | NLI 모델 로드/추론 실패 | `F-020-04` | "충돌 감지 모델을 사용할 수 없습니다." |
| `COND_020_STORE_UNAVAILABLE` | 지식 저장소 연결 실패 | `F-020-05` | "지식 저장소에 연결할 수 없습니다." |
| `COND_020_SCAN_TIMEOUT` | 스캔 시간 초과 | `F-020-06` | "충돌 감지 시간이 초과되었습니다. 검사 범위를 줄여 주세요." |
| `COND_020_SCOPE_TOO_BROAD` | full_scan 대상이 최대 한도 초과 | `F-020-07` | "검사 범위가 너무 넓습니다. 도메인을 지정하거나 incremental 모드를 사용해 주세요." |

### VamosError 구조
```python
VamosError(
    failure_code="COND_020_NLI_MODEL_UNAVAILABLE",
    message="NLI model failed to load: {detail}",
    fallback_id="F-020-04",
    trace_id=context.trace_id
)
```

---

## E5. Dependency Map

> §A 의존성 매트릭스 (P0-1 산출물) 반영

### CAT-B 내부 의존 (§A.3.2)
| 관계 | 의존 모듈 | 의존 내용 | 추출 기준 |
|------|-----------|----------|----------|
| **소비** (B-1) | COND-020 → COND-018 | KG 트리플 기반 충돌 감지, 그래프 탐색 | ②③ |
| **제공** (B-2) | COND-108 → COND-020 | Zettelkasten이 노트 충돌 감지 호출 | ②③ |

> COND-020은 **Level 2** — COND-018(Level 1)을 소비

### I-Series 소비 (§A.2.4)
| I-Module | 용도 | 공통/추가 |
|----------|------|----------|
| I-1 (Intent) | 의도 해석 | 공통 (26개 전체) |
| I-5 (Decision) | 라우팅/결정 | 공통 |
| I-6 (Self-check) | 자기 검증 | 공통 |
| I-9 (Logging) | 로깅 | 공통 |

### 외부 라이브러리
| 라이브러리 | 버전 | 용도 |
|-----------|------|------|
| `transformers` | ≥4.36 | NLI 모델 (DeBERTa-v3-large-mnli) |
| `sentence-transformers` | ≥2.2 | BGE-M3 임베딩 (유사도 사전 필터) |
| `spacy` | ≥3.7 | 엔티티/시간 표현 추출 |
| `dateparser` | ≥1.2 | 다국어 시간 표현 파싱 |
| `neo4j` | ≥5.0 | KG 트리플 조회 (COND-018 경유) |

### 인프라
| 인프라 | 용도 |
|--------|------|
| GPU (권장) | NLI 모델 추론 가속 |
| ChromaDB | 임베딩 기반 후보 쌍 사전 필터링 |
| Redis | 스캔 히스토리 캐시 (incremental 모드) |
| 메모리 ≥ 6GB | NLI 모델 + 임베딩 인덱스 |

---

## E6. Performance Benchmark

> Phase 1 보강 예정 — basic SLA targets only

| 메트릭 | 기준 | 측정 방법 |
|--------|------|----------|
| **on_insert (1 vs 100)** | ≤ 2,000ms | 신규 1건 vs 기존 100건 비교 |
| **on_insert (1 vs 1K)** | ≤ 10,000ms | 신규 1건 vs 기존 1K건 (사전 필터 후) |
| **incremental (100 변경)** | ≤ 15,000ms | 변경 100건 vs 전체 |
| **full_scan (100 항목)** | ≤ 30,000ms | 100건 전수 비교 |
| **NLI 추론** | ≤ 50ms/쌍 (GPU) | DeBERTa-v3-large 단일 쌍 |
| **사전 필터링** | ≤ 500ms (1K 항목) | 임베딩 유사도 기반 |
| **해결 제안 생성** | ≤ 10ms/건 | 규칙 기반 |

### 병목 요인 및 최적화
- **NLI 추론**: GPU 배치 처리 (batch size 32)로 처리량 향상
- **full_scan O(n^2)**: 임베딩 ANN 사전 필터로 후보 쌍 축소
- **대규모 KG**: COND-018 서브그래프 추출로 탐색 범위 제한

---

## E7. Integration Test Spec

> Phase 2 보강 예정 — skeleton scenarios only

### 시나리오 1: 수치 불일치 감지 (on_insert)
```yaml
name: "numeric_mismatch_on_insert"
setup:
  - create_knowledge_item(id="ki-exist-001",
      content="삼성전자의 2024년 1분기 매출은 76조 원이다.", domain="finance")
input:
  knowledge_scope: "user-42/finance"
  detection_mode: "on_insert"
  new_item_id: "ki-new-001"
  new_item_content: "삼성전자의 2024년 1분기 매출은 54조 원으로 보고되었다."
  conflict_types: ["numeric_mismatch", "factual_contradiction"]
  severity_threshold: "medium"
  include_resolution: true
expected:
  - conflict_count >= 1
  - conflicts[0].conflict_type in ["numeric_mismatch", "factual_contradiction"]
  - conflicts[0].severity in ["high", "critical"]
  - len(resolution_suggestions) >= 1
```

### 시나리오 2: 시간적 모순 감지 (incremental)
```yaml
name: "temporal_inconsistency_incremental"
setup:
  - create_knowledge_item(id="ki-time-001",
      content="프로젝트 A는 2024년 3월에 시작되어 6월에 완료되었다.", created_at="2024-07-01")
  - create_knowledge_item(id="ki-time-002",
      content="프로젝트 A는 2024년 8월에 시작되었다.", created_at="2024-09-01")
  - set_last_scan_time("user-42/projects", "2024-08-15")
input:
  knowledge_scope: "user-42/projects"
  detection_mode: "incremental"
  conflict_types: ["temporal_inconsistency"]
  severity_threshold: "low"
expected:
  - conflict_count >= 1
  - conflicts[0].conflict_type == "temporal_inconsistency"
  - "프로젝트 A" in conflicts[0].explanation
```

### 시나리오 3: 충돌 없음 확인
```yaml
name: "no_conflicts_detected"
setup:
  - create_knowledge_item(id="ki-ok-001", content="서울의 인구는 약 950만 명이다.")
  - create_knowledge_item(id="ki-ok-002", content="부산의 인구는 약 340만 명이다.")
input:
  knowledge_scope: "user-42/geography"
  detection_mode: "full_scan"
  conflict_types: ["factual_contradiction", "numeric_mismatch"]
expected:
  - conflict_count == 0
  - total_items_scanned == 2
```

### 시나리오 4: 에러 — scope 내 항목 없음
```yaml
name: "error_no_items_in_scope"
input:
  knowledge_scope: "user-99/nonexistent"
  detection_mode: "full_scan"
expected:
  - error.failure_code == "COND_020_NO_ITEMS_IN_SCOPE"
  - error.fallback_id == "F-020-01"
```

---

## E8. Blue Node Integration

> §B.6.2 CAT-B 연동 프로토콜 (P0-2 산출물) 반영
> LOCK (D2.0-03 §1.1): NODE는 CORE 규칙 상속, **독립 실행 불가** (LOCK-CD-08)

### 연동 프로토콜 (§B.6.2)
| 항목 | 값 |
|------|-----|
| **연동 Blue Node** | Content Node |
| **Permission Level** | P0 (기본 활성) |
| **게이트 요구** | policy + evidence |
| **우선순위** | MEDIUM |

### 호출 패턴
```
COND-018 (Ingest 완료) → 이벤트: cond.b.018.ingest_done
  → ORANGE CORE (내부 트리거: knowledge_conflict_check)
    → I-5 라우팅 → Content Node
      → Content Node: COND-020.execute(detection_mode="on_insert", new_item_id="...")
        → 5-Gate 평가 (§B.7.1):
          [1] PolicyGate ✅ (자동 충돌 감지 정책)
          [3] EvidenceGate ✅ (NLI 모델 근거 충족)
          → COND-020 실행 → ConflictDetectionResponse 반환
            → Content Node (충돌 발견 시 알림 생성)
              → ORANGE CORE → User (충돌 알림)

User → "내 지식에 모순되는 정보가 있어?"
  → ORANGE CORE (I-1 Intent 해석: knowledge_conflict_scan)
    → I-5 라우팅 → Content Node
      → Content Node: COND-020.execute(detection_mode="full_scan", knowledge_scope="user-42/*")
        → COND-020 실행 → ConflictDetectionResponse
          → Content Node → ORANGE CORE → User
```

### 이벤트 매핑 (§B.4 lower.dot 네이밍, §B.4.1 LogEvent 8필드)

| 이벤트 | event_type | 트리거 |
|--------|-----------|--------|
| 모듈 초기화 | `cond.b.020.initialized` | initialize() 완료 |
| 충돌 감지 시작 | `cond.b.020.execute_start` | execute() 진입 |
| 충돌 감지 완료 | `cond.b.020.execute_done` | 정상 반환 |
| 충돌 감지 실패 | `cond.b.020.execute_fail` | VamosError 발생 |
| 충돌 발견 | `cond.b.020.conflict_found` | 개별 충돌 감지 시 |
| QoD 재평가 트리거 | `cond.b.020.qod_reevaluated` | 충돌로 인한 QoD 재평가 |
| 헬스체크 | `cond.b.020.health` | health_check() 호출 |
| 모듈 종료 | `cond.b.020.shutdown` | shutdown() 호출 |

### Decision 기록 연결 (§B.8, D2.0-03 §6.0 LOCK)
- **실행 전**: `ModuleRequest.decision_id` → Decision 레코드에 참조 기록
- **실행 후**: `Decision.optional_signals` ← `{ "cond_module_id": "COND-020", "execution_ms": N, "items_scanned": M, "conflicts_found": K, "qod_reevaluated_count": J }`
- **trace_id 필수**: decision_id 부재 시에도 trace_id로 추적 (D2.0-03 §5.2)

---

## E9. BaseModule ABC 적합성

> LOCK (§3.4 LOCK-CD-03): `initialize() / execute() / health_check() / shutdown()`
> LOCK (§3.4 LOCK-CD-04): Runnable 프로토콜 `run(input) → output, get_metadata(), health_check()`
> **CD-03 ↔ CD-04 관계**: execute()는 내부적으로 Runnable.run()을 위임, initialize()/shutdown()은 Runnable에 없는 생명주기 확장

```python
class Cond020KnowledgeConflictDetection(BaseModule):
    """COND-020 지식 충돌 감지"""

    async def initialize(self) -> Result[None, VamosError]:
        """NLI 모델 로드, KnowledgeStore 연결, VectorStore 연결, 스캔 히스토리 초기화"""
        self._nli_model = await NLIModel.load(self.config.nli_model_name)
        self._knowledge_store = await KnowledgeStore.connect(self.config.store_url)
        self._vector_store = await ChromaAdapter.connect(self.config.chroma_url)
        self._temporal_parser = TemporalParser(language=self.config.default_language)
        self._claim_extractor = ClaimExtractor()
        self._numeric_extractor = NumericExtractor()
        self._scan_history = ScanHistory(backend="redis", url=self.config.redis_url)
        self._qod_evaluator = QoDEvaluator()
        self._emit_event("cond.b.020.initialized")
        return Ok(None)

    async def execute(self, request: ConflictDetectionRequest) -> Result[ConflictDetectionResponse, VamosError]:
        """Runnable.run() 위임 — 지식 충돌 감지 수행"""
        return await self.run(request)

    async def health_check(self) -> Result[HealthStatus, VamosError]:
        """NLI 모델 + KnowledgeStore + VectorStore + Redis 상태 확인"""
        nli_ok = self._nli_model.is_loaded()
        store_ok = await self._knowledge_store.ping()
        vector_ok = await self._vector_store.ping()
        redis_ok = await self._scan_history.ping()
        healthy = nli_ok and store_ok and vector_ok and redis_ok
        return Ok(HealthStatus(
            healthy=healthy,
            latency_ms=elapsed,
            details={
                "nli_model": nli_ok,
                "knowledge_store": store_ok,
                "vector_store": vector_ok,
                "scan_history": redis_ok
            }
        ))

    async def shutdown(self) -> Result[None, VamosError]:
        """NLI 모델 언로드, 연결 해제, 리소스 정리"""
        self._nli_model.unload()
        await self._knowledge_store.disconnect()
        await self._vector_store.disconnect()
        await self._scan_history.close()
        self._emit_event("cond.b.020.shutdown")
        return Ok(None)

    def get_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            id="COND-020", version="1.0.0",
            capabilities=[
                "factual_contradiction_detection", "temporal_inconsistency_detection",
                "source_disagreement_detection", "logical_conflict_detection",
                "numeric_mismatch_detection", "conflict_resolution_suggestion",
                "qod_reevaluation_trigger"
            ]
        )
```

---

## E10. Configuration

> LOCK (종합명세 §공통 / LOCK-CD-10): ModuleConfig 표준 필드

```python
class Cond020Config(ModuleConfig):
    """COND-020 모듈 설정"""
    # ModuleConfig 상속 (enabled, priority, max_concurrent, timeout_ms, retry_policy)
    enabled: bool = True
    priority: Literal["critical", "high", "medium", "low"] = "medium"
    max_concurrent: int = 3
    timeout_ms: int = 60000
    retry_policy: RetryPolicy = RetryPolicy(max_retries=1, backoff_ms=2000)

    # COND-020 전용 설정
    store_url: str = "http://localhost:8000"
    chroma_url: str = "http://localhost:8000"
    redis_url: str = "redis://localhost:6379/3"
    nli_model_name: str = "microsoft/deberta-v3-large-mnli"
    nli_confidence_threshold: float = 0.8
    candidate_similarity_threshold: float = 0.6
    numeric_mismatch_threshold: float = 0.1      # 10% 이상 차이 시 불일치
    max_full_scan_items: int = 10000
    default_max_comparisons: int = 10000
    nli_batch_size: int = 32
    default_language: str = "ko"
    enable_qod_reevaluation: bool = True
    conflict_log_retention_days: int = 90
    incremental_scan_cron: str = "0 */12 * * *"  # 12시간마다
```
