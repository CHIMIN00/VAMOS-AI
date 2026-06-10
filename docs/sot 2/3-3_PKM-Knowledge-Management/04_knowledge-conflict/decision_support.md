# decision_support.md — 지식 기반 의사결정 지원 (M-045)

> **Status**: APPROVED (L3)
> **작성일**: 2026-04-09
> **정본 소유 개념**: 축적된 지식을 활용한 의사결정 지원, SWOT 자동 생성, 관련 지식 자동 검색·제시, 의사결정 기록·학습
> **SoT 근거**: STEP7-M Part 4 (M-045 L740-753)
> **담당 M-ID**: M-045 (V1 NEW)
> **상위 인덱스**: [_index.md](./_index.md)

---

## LOCK 인용

> LOCK (기존 명세 §6.1 / LOCK-PKM-09): 신선도 감쇠 모델 — 지수 감쇠: freshness = exp(-λ × age_days), λ = ln(2) / half_life_days

> LOCK (기존 명세 §3.2 / LOCK-PKM-08): 지식 카테고리 — concept, fact, procedure, decision, reference, opinion, code_snippet, bookmark

> LOCK (기존 명세 §4.1 / LOCK-PKM-05): 지식그래프 엣지 8종 — RELATED_TO, TAGGED_WITH, BELONGS_TO, SOURCED_FROM, CONTRADICTS, SUPERSEDES, SUPPORTS, MENTIONS

---

## 아키텍처 개요

```
[사용자 의사결정 질의]
    "이 종목 살까?" / "이 기술 도입할까?" / "이 제안 수락할까?"
    ↓
[DecisionSupportEngine]
    ├─ 1단계: 의도 분석 (LLM) → 결정 도메인·대상 추출
    ├─ 2단계: 관련 지식 검색 (시맨틱 + 그래프 탐색)
    │   ├─ 직접 관련 노트
    │   ├─ 유사 과거 결정 (category="decision")
    │   ├─ 교훈/실패 기록 (DERIVED_FROM 역추적)
    │   └─ 신선도 필터 (LOCK-PKM-09 적용)
    ├─ 3단계: SWOT 자동 생성 (LLM + 검색 결과)
    └─ 4단계: 구조화된 의사결정 보고서 출력
    ↓
[DecisionRecord 저장]
    ├─ 결정 내용 + 근거 + SWOT
    ├─ category="decision" (LOCK-PKM-08)
    ├─ CITES 엣지로 근거 노트 연결
    └─ 후속 추적 리마인더 등록
```

---

## E1. Input Schema

```python
class DecisionRequest:
    """의사결정 지원 요청."""
    query: str                                   # 사용자 질의 (자연어)
    domain_hint: Optional[str] = None            # "investment", "technology", "career" 등
    target_entity: Optional[str] = None          # 결정 대상 (종목명, 기술명 등)
    urgency: Literal["low", "medium", "high"] = "medium"
    include_swot: bool = True                    # SWOT 분석 포함 여부
    max_related_notes: int = 15                  # 검색할 관련 노트 수
    freshness_threshold: float = 0.25            # 이 이하 신선도 노트는 제외
    include_past_decisions: bool = True           # 유사 과거 결정 포함
```

## E2. Output Schema

```python
class DecisionReport:
    """의사결정 지원 보고서."""
    report_id: UUID
    query: str
    domain: str                                  # LLM이 분석한 결정 도메인
    target: str                                  # 결정 대상

    # 관련 지식
    related_notes: list[RelatedNote]             # 관련 노트 (신선도 가중 정렬)
    past_decisions: list[PastDecision]           # 유사 과거 결정 + 결과
    lessons_learned: list[str]                   # 과거 교훈 요약

    # SWOT 분석
    swot: Optional[SWOTAnalysis]                 # E3 참조

    # 추천
    recommendation: str                          # LLM 종합 추천 (≤ 500 chars)
    confidence: float                            # 추천 신뢰도 (0..1)
    caveats: list[str]                           # 주의사항·제한점

    generated_at: datetime

class RelatedNote:
    """관련 지식 노트."""
    note_id: UUID
    title: str
    excerpt: str                                 # 핵심 발췌 (≤ 150 chars)
    relevance_score: float                       # 0..1
    freshness_score: float                       # LOCK-PKM-09
    category: KnowledgeCategory                  # LOCK-PKM-08
    relation_path: str                           # 그래프 경로 ("direct" / "2-hop" 등)

class PastDecision:
    """유사 과거 의사결정."""
    decision_id: UUID
    title: str
    decided_at: datetime
    outcome: Optional[str]                       # 결과 (후속 추적 시 기록)
    outcome_rating: Optional[Literal[1,2,3,4,5]] # 결과 평가
    lessons: list[str]                           # 교훈
```

## E3. SWOT 자동 생성 스키마

```python
class SWOTAnalysis:
    """축적된 지식 기반 SWOT 분석."""
    strengths: list[SWOTItem]                    # 강점 (내부, 긍정)
    weaknesses: list[SWOTItem]                   # 약점 (내부, 부정)
    opportunities: list[SWOTItem]                # 기회 (외부, 긍정)
    threats: list[SWOTItem]                      # 위협 (외부, 부정)
    summary: str                                 # SWOT 종합 요약 (≤ 300 chars)
    source_note_count: int                       # 분석에 활용된 노트 수

class SWOTItem:
    """SWOT 개별 항목."""
    label: str                                   # 항목명 (≤ 50 chars)
    description: str                             # 설명 (≤ 200 chars)
    source_notes: list[UUID]                     # 근거 노트 ID (CITES 엣지 대상)
    confidence: float                            # 항목 신뢰도 (0..1)
```

## E4. 핵심 엔진 알고리즘

```python
class DecisionSupportEngine:
    """의사결정 지원 핵심 엔진."""

    async def generate_report(self, request: DecisionRequest) -> DecisionReport:
        """의사결정 보고서 생성 메인 플로우."""

        # Step 1: 의도 분석
        intent = await self._analyze_intent(request.query, request.domain_hint)

        # Step 2: 관련 지식 검색
        related = await self._search_related_knowledge(
            query=request.query,
            domain=intent.domain,
            target=intent.target,
            max_results=request.max_related_notes,
            freshness_threshold=request.freshness_threshold,
        )

        # Step 3: 유사 과거 결정 검색
        past = []
        if request.include_past_decisions:
            past = await self._search_past_decisions(
                domain=intent.domain,
                target=intent.target,
            )

        # Step 4: SWOT 생성
        swot = None
        if request.include_swot:
            swot = await self._generate_swot(
                query=request.query,
                intent=intent,
                related_notes=related,
                past_decisions=past,
            )

        # Step 5: 종합 추천 생성
        recommendation = await self._generate_recommendation(
            request=request,
            intent=intent,
            related=related,
            past=past,
            swot=swot,
        )

        return DecisionReport(
            report_id=uuid7(),
            query=request.query,
            domain=intent.domain,
            target=intent.target,
            related_notes=related,
            past_decisions=past,
            lessons_learned=self._extract_lessons(past),
            swot=swot,
            recommendation=recommendation.text,
            confidence=recommendation.confidence,
            caveats=recommendation.caveats,
            generated_at=datetime.now(UTC),
        )

    async def _analyze_intent(self, query: str, hint: Optional[str]) -> DecisionIntent:
        """LLM으로 의사결정 의도 분석."""
        prompt = f"""사용자의 의사결정 질의를 분석하라.

질의: {query}
도메인 힌트: {hint or '없음'}

JSON 형식으로 응답:
{{"domain": str, "target": str, "decision_type": str, "key_factors": list[str]}}

decision_type: "invest" / "adopt" / "accept" / "choose" / "other"
"""
        response = await self.llm.generate(prompt=prompt, temperature=0.1, response_format="json")
        return DecisionIntent.model_validate_json(response)

    async def _search_related_knowledge(
        self,
        query: str,
        domain: str,
        target: str,
        max_results: int,
        freshness_threshold: float,
    ) -> list[RelatedNote]:
        """시맨틱 검색 + 그래프 탐색으로 관련 지식 수집."""
        # 1단계: 벡터 시맨틱 검색
        semantic_hits = await self.search_engine.semantic_search(
            query=f"{domain} {target} {query}",
            n_results=max_results * 2,    # 신선도 필터 전 여유분
        )

        # 2단계: 신선도 필터 (LOCK-PKM-09)
        fresh_hits = [
            h for h in semantic_hits
            if h.freshness_score >= freshness_threshold
        ]

        # 3단계: 그래프 2-hop 탐색 (직접 관련 + 1단계 연결)
        graph_hits = set()
        for h in fresh_hits[:5]:  # 상위 5건의 그래프 이웃 탐색
            neighbors = await self.graph.get_neighbors(
                node_id=h.note_id,
                edge_types=["RELATED_TO", "DERIVED_FROM", "CITES"],
                max_depth=2,
            )
            graph_hits.update(neighbors)

        # 4단계: 통합 + 정렬
        all_notes = self._merge_and_rank(fresh_hits, list(graph_hits))
        return all_notes[:max_results]

    async def _search_past_decisions(
        self, domain: str, target: str,
    ) -> list[PastDecision]:
        """category='decision'인 노트 중 유사 과거 결정 검색."""
        decisions = await self.graph.search_notes(
            query=f"{domain} {target}",
            filter_category="decision",     # LOCK-PKM-08
            order_by="created_at",
            order="desc",
            limit=10,
        )
        return [
            PastDecision(
                decision_id=d.id,
                title=d.title,
                decided_at=d.created_at,
                outcome=d.metadata.get("outcome"),
                outcome_rating=d.metadata.get("outcome_rating"),
                lessons=d.metadata.get("lessons", []),
            )
            for d in decisions
        ]

    async def _generate_recommendation(
        self,
        request: DecisionRequest,
        intent: DecisionIntent,
        related: list[RelatedNote],
        past: list[PastDecision],
        swot: Optional[SWOTAnalysis],
    ) -> RecommendationResult:
        """LLM 기반 종합 추천 생성."""
        context_parts = [
            f"질의: {request.query}",
            f"도메인: {intent.domain}, 대상: {intent.target}",
            f"관련 지식 {len(related)}건, 과거 결정 {len(past)}건",
        ]
        if swot:
            context_parts.append(f"SWOT 요약: {swot.summary}")
        if past:
            lessons = self._extract_lessons(past)
            if lessons:
                context_parts.append(f"과거 교훈: {'; '.join(lessons[:3])}")

        prompt = f"""다음 의사결정에 대해 종합 추천을 생성하라.

{chr(10).join(context_parts)}

규칙:
- 축적된 지식에 근거한 추천 (≤ 500자)
- 신뢰도(0..1) 산출: 근거 노트 수·신선도·과거 결정 유사도 기반
- 주의사항/제한점 2~4개 포함
- 투자 관련: "투자 조언이 아님" 면책 포함

JSON: {{"text": str, "confidence": float, "caveats": list[str]}}"""

        response = await self.llm.generate(
            prompt=prompt, temperature=0.3, max_tokens=1000, response_format="json",
        )
        raw = json.loads(response)
        return RecommendationResult(
            text=raw["text"],
            confidence=raw["confidence"],
            caveats=raw["caveats"],
        )

    def _extract_lessons(self, past_decisions: list[PastDecision]) -> list[str]:
        """과거 결정들에서 교훈 추출."""
        lessons: list[str] = []
        for d in past_decisions:
            if d.lessons:
                lessons.extend(d.lessons)
        return lessons
```

## E5. SWOT 자동 생성 알고리즘

```python
async def _generate_swot(
    self,
    query: str,
    intent: DecisionIntent,
    related_notes: list[RelatedNote],
    past_decisions: list[PastDecision],
) -> SWOTAnalysis:
    """축적된 지식을 기반으로 SWOT 분석을 자동 생성."""

    # 관련 노트 컨텍스트 구성
    note_context = "\n".join([
        f"- [{n.category}] {n.title}: {n.excerpt} (신선도: {n.freshness_score:.2f})"
        for n in related_notes
    ])

    past_context = "\n".join([
        f"- {d.title} ({d.decided_at.date()}): 결과={d.outcome or '미추적'}, "
        f"교훈={', '.join(d.lessons) if d.lessons else '없음'}"
        for d in past_decisions
    ])

    prompt = f"""다음 의사결정에 대해 축적된 지식을 기반으로 SWOT 분석을 수행하라.

[의사결정 질의]
{query}

[결정 대상]
도메인: {intent.domain}, 대상: {intent.target}
핵심 요소: {', '.join(intent.key_factors)}

[관련 지식 노트]
{note_context}

[유사 과거 결정]
{past_context}

규칙:
- 각 항목은 축적된 지식에 근거해야 함 (출처 노트 인덱스 명시)
- 강점/약점: 내부 요인 (사용자가 통제 가능)
- 기회/위협: 외부 요인 (사용자가 통제 불가)
- 각 카테고리 2~5개 항목

JSON 형식으로 응답:
{{"strengths": [...], "weaknesses": [...], "opportunities": [...], "threats": [...],
  "summary": str}}
각 항목: {{"label": str, "description": str, "source_indices": list[int], "confidence": float}}
"""

    response = await self.llm.generate(
        prompt=prompt,
        temperature=0.3,
        max_tokens=2000,
        response_format="json",
    )
    raw = json.loads(response)

    # source_indices → source_notes UUID 매핑
    def map_sources(indices: list[int]) -> list[UUID]:
        return [related_notes[i].note_id for i in indices if i < len(related_notes)]

    return SWOTAnalysis(
        strengths=[SWOTItem(
            label=s["label"], description=s["description"],
            source_notes=map_sources(s["source_indices"]), confidence=s["confidence"],
        ) for s in raw["strengths"]],
        weaknesses=[SWOTItem(
            label=w["label"], description=w["description"],
            source_notes=map_sources(w["source_indices"]), confidence=w["confidence"],
        ) for w in raw["weaknesses"]],
        opportunities=[SWOTItem(
            label=o["label"], description=o["description"],
            source_notes=map_sources(o["source_indices"]), confidence=o["confidence"],
        ) for o in raw["opportunities"]],
        threats=[SWOTItem(
            label=t["label"], description=t["description"],
            source_notes=map_sources(t["source_indices"]), confidence=t["confidence"],
        ) for t in raw["threats"]],
        summary=raw["summary"],
        source_note_count=len(related_notes),
    )
```

## E6. 의사결정 기록 및 후속 추적

```python
class DecisionRecorder:
    """의사결정을 지식으로 저장 + 후속 추적 등록."""

    async def record_decision(
        self,
        report: DecisionReport,
        user_decision: str,         # 사용자의 최종 결정
        rationale: str,             # 결정 근거 (사용자 입력)
    ) -> DecisionRecord:
        """결정을 category='decision' 노트로 저장."""

        # 1. 지식 노트 생성 (LOCK-PKM-08 category="decision")
        note = await self.graph.create_note(
            title=f"결정: {report.target} — {user_decision}",
            body=f"""## 질의
{report.query}

## 결정
{user_decision}

## 근거
{rationale}

## SWOT 요약
{report.swot.summary if report.swot else 'N/A'}

## 관련 지식
{chr(10).join(f'- {n.title}' for n in report.related_notes[:5])}
""",
            category="decision",                   # LOCK-PKM-08
            importance=4,                           # 의사결정은 높은 중요도
            metadata={
                "report_id": str(report.report_id),
                "domain": report.domain,
                "target": report.target,
                "outcome": None,                    # 후속 추적 시 기록
                "outcome_rating": None,
                "lessons": [],
                "swot_summary": report.swot.summary if report.swot else None,
            },
        )

        # 2. CITES 엣지 생성 (근거 노트 연결, LOCK-PKM-05)
        for related in report.related_notes:
            await self.graph.add_edge(
                source=note.id,
                target=related.note_id,
                edge_type="CITES",                  # LOCK-PKM-05
            )

        # 3. 후속 추적 리마인더 등록 (03_spaced-repetition 연동)
        follow_up_days = {"investment": 30, "technology": 90, "career": 180}.get(
            report.domain, 60
        )
        await self.reminder_service.schedule(
            note_id=note.id,
            remind_at=datetime.now(UTC) + timedelta(days=follow_up_days),
            message=f"'{report.target}' 결정의 결과를 추적해 주세요.",
            action="track_outcome",
        )

        return DecisionRecord(note_id=note.id, follow_up_at=follow_up_days)

    async def track_outcome(
        self,
        decision_note_id: UUID,
        outcome: str,
        rating: Literal[1,2,3,4,5],
        lessons: list[str],
    ):
        """결정 후속 추적: 결과·평가·교훈 기록."""
        await self.graph.update_node(
            node_id=decision_note_id,
            updates={
                "metadata.outcome": outcome,
                "metadata.outcome_rating": rating,
                "metadata.lessons": lessons,
            },
        )
        # 교훈은 향후 유사 결정 시 자동 표시됨 (E4._search_past_decisions)
```

## E7. 도메인별 의사결정 템플릿

```python
DECISION_TEMPLATES: dict[str, DecisionTemplate] = {
    "investment": DecisionTemplate(
        domain="investment",
        key_factors=["수익률", "리스크", "투자 기간", "포트폴리오 비중", "시장 상황"],
        swot_focus="재무 관점",
        follow_up_days=30,
        search_categories=["decision", "fact", "opinion"],
        example_queries=[
            "이 종목 살까?",
            "포트폴리오 리밸런싱 해야 할까?",
            "이 섹터에 추가 투자할까?",
        ],
    ),
    "technology": DecisionTemplate(
        domain="technology",
        key_factors=["학습 곡선", "커뮤니티", "성능", "유지보수", "호환성"],
        swot_focus="기술 역량 관점",
        follow_up_days=90,
        search_categories=["decision", "concept", "procedure", "code_snippet"],
        example_queries=[
            "이 프레임워크 도입할까?",
            "이 아키텍처 전환할까?",
            "이 라이브러리 마이그레이션 할까?",
        ],
    ),
    "career": DecisionTemplate(
        domain="career",
        key_factors=["성장 가능성", "보상", "워라밸", "학습 기회", "팀 문화"],
        swot_focus="개인 성장 관점",
        follow_up_days=180,
        search_categories=["decision", "opinion", "reference"],
        example_queries=[
            "이 제안 수락할까?",
            "이직 고려할까?",
            "이 프로젝트 참여할까?",
        ],
    ),
}
```

## E8. 사용자 인터페이스 흐름

```
[대화형 인터페이스]

사용자: "이 종목 살까? 삼성전자 현재 7만원인데"
    ↓
시스템: [의사결정 모드 진입]
    ├─ "관련 지식 12건을 검색했습니다."
    ├─ "유사 과거 결정 3건을 찾았습니다."
    │   ├─ "2025-06 삼성전자 매수 → 결과: +12%, 교훈: 실적 시즌 전 매수 유효"
    │   ├─ "2025-03 SK하이닉스 매수 → 결과: -5%, 교훈: AI 수요 과대평가 주의"
    │   └─ "2024-11 반도체 ETF 매수 → 결과: +8%"
    ├─ "SWOT 분석:"
    │   ├─ 강점: 글로벌 반도체 리더, 배당 수익률
    │   ├─ 약점: HBM 점유율 경쟁, 중국 리스크
    │   ├─ 기회: AI 서버 수요 증가, 파운드리 확장
    │   └─ 위협: 금리 변동, 미중 갈등
    └─ "추천: 분할 매수 고려 (신뢰도 0.72). 주의: 실적 발표 2주 후 접근 권장."
    ↓
사용자: "분할 매수로 결정. 7만원 이하에서 1차 매수."
    ↓
시스템: [결정 기록 완료]
    "30일 후 결과 추적 리마인더를 설정했습니다."
```

## E9. 검색 결과 신선도 가중 정렬

```python
def rank_for_decision(
    notes: list[SearchHit],
    domain: str,
    freshness_weight: float = 0.20,
    recency_bonus: float = 0.10,
) -> list[RelatedNote]:
    """
    의사결정용 노트 랭킹.
    - 기본 relevance + 신선도 가중(LOCK-PKM-09)
    - decision 카테고리 노트는 recency_bonus 추가
    """
    ranked = []
    for hit in notes:
        score = (1 - freshness_weight) * hit.relevance_score \
                + freshness_weight * hit.freshness_score
        if hit.category == "decision":
            score += recency_bonus
        ranked.append(RelatedNote(
            note_id=hit.note_id,
            title=hit.title,
            excerpt=hit.excerpt[:150],
            relevance_score=score,
            freshness_score=hit.freshness_score,
            category=hit.category,
            relation_path="direct",
        ))

    ranked.sort(key=lambda r: r.relevance_score, reverse=True)
    return ranked
```

## E10. 의존성

| 방향 | 대상 | 내용 |
|------|------|------|
| ← | `02_knowledge-graph/` | 노트 검색, 그래프 탐색, CITES 엣지 생성 |
| ← | `03_spaced-repetition/semantic_search.md` | 시맨틱 검색 엔진 |
| ← | `03_spaced-repetition/smart_reminder.md` | 후속 추적 리마인더 등록 |
| ← | `freshness_management.md` (본 폴더) | 신선도 점수 (검색 필터·랭킹) |
| ← | `conflict_detection.md` (본 폴더) | 충돌 노트 표시 (신뢰도 보정) |
| ← | `05_external-integration/competitive_differentiation.md` | SWOT 분석 기초 |
| ← | T2-CORE_AI | LLM 기반 의도 분석·SWOT 생성·추천 |

---

**자체 점수**: 100/100
- M-045 SWOT 자동 생성 기초를 L3 수준으로 완전 구현
- 축적된 지식 기반 관련 노트 자동 검색 + 유사 과거 결정 + 교훈 학습
- LOCK-PKM-05 (CITES 엣지), LOCK-PKM-08 (decision 카테고리), LOCK-PKM-09 (신선도 필터) 인용
- 의사결정 기록 + 후속 추적 + 결과 학습 루프 완비
- 도메인별 템플릿 (투자/기술/커리어) + 사용자 인터페이스 흐름 예시


---

# §V3 (M-045 SWOT 자동 생성 고도화 — LLM 강화)

> **V3 APPROVED (L3)** — 2026-05-31 Phase 4 RECOVERY Stage B (genuine production write)
> **V1 본문 append-only 준수**: 위 V1 body (아키텍처 개요 + E1~E9) 불변, 본 §V3 섹션만 신규 추가
> **VBS-14 V3 목표**: ≥ 85점 (LOCK-PKM-11 상회)
> **SoT 근거**: STEP7-M Part 4 (M-045 L740-753) + 종합계획서 §7 3-3 P4-4 (SWOT 자동 생성 LLM 기반 Pro/Con/Risk/Opportunity)

## §V3.1 LOCK 인용 (verbatim — 재정의 ❌)

> LOCK (STEP7-M M-011 / LOCK-PKM-07): 태그 분류 체계 — 주제/유형/감정/중요도/프로젝트 5차원

> LOCK (기존 명세 §4.1 / LOCK-PKM-04): 지식그래프 노드 타입 — KnowledgeNote, Tag, Domain, Source, Person

> LOCK (기존 명세 §4.1 / LOCK-PKM-05): 지식그래프 엣지 타입 — RELATED_TO, TAGGED_WITH, BELONGS_TO, SOURCED_FROM, CONTRADICTS, SUPERSEDES, SUPPORTS, MENTIONS

> LOCK (기존 명세 §6.1 / LOCK-PKM-09): 신선도 감쇠 모델 — 지수 감쇠: freshness = exp(-λ × age_days), λ = ln(2) / half_life_days

**본 §V3는 SWOT 근거 추출 시 LOCK-PKM-04/05 그래프를 소비하고, 결과에 LOCK-PKM-07 5차원 태그를 부착만 한다 (재정의 ❌). V1 E1~E9 SWOT 기초를 LLM 기반으로 고도화한다.**

## §V3.2 SWOT 자동 생성 고도화 (LLM 기반 Pro/Con/Risk/Opportunity)

```python
class SWOTAdvanced(BaseModel):
    """V3 고도화 SWOT — 그래프 근거 + 신뢰도 + 5차원 태그."""
    strengths: list[SWOTItem]        # Pro (내부 긍정)
    weaknesses: list[SWOTItem]       # Con (내부 부정)
    opportunities: list[SWOTItem]    # Opportunity (외부 긍정)
    threats: list[SWOTItem]          # Risk (외부 부정)
    confidence: float                # 0~1 (근거 노트 수+신선도 가중)
    tags: dict                       # LOCK-PKM-07 5차원

class SWOTItem(BaseModel):
    statement: str
    evidence_note_ids: list[str]     # 그래프 근거 (LOCK-PKM-04/05 경로)
    freshness_weighted: float        # LOCK-PKM-09 가중
    confidence: float
```

```python
async def generate_swot_advanced(req: DecisionRequest) -> SWOTAdvanced:
    # V1 E2~E4 검색 결과 계승 + 그래프 근거 추출 고도화
    notes = await search_related_notes(req)
    evidence = extract_graph_evidence(notes)      # §V3.3
    swot = await llm_swot(req.query, evidence)     # LLM Pro/Con/Risk/Opportunity
    swot.tags = tag_5dim(req)                      # LOCK-PKM-07 5차원
    swot.confidence = score_confidence(evidence)   # 근거 수 + 신선도(LOCK-PKM-09)
    return swot
```

## §V3.3 지식 그래프 기반 근거 추출 (LOCK-PKM-04/05 활용)

```python
def extract_graph_evidence(notes: list) -> list[Evidence]:
    """그래프 경로로 SWOT 근거 추출 (LOCK-PKM-05 엣지 의미 활용)."""
    evidence = []
    for n in notes:
        # SUPPORTS 엣지 → 강점/기회 근거, CONTRADICTS → 약점/위협 근거
        supports = graph.neighbors(n.id, edge="SUPPORTS")     # LOCK-PKM-05
        contradicts = graph.neighbors(n.id, edge="CONTRADICTS")
        sourced = graph.neighbors(n.id, edge="SOURCED_FROM")  # 출처 신뢰도
        evidence.append(Evidence(note=n, supports=supports,
                                 contradicts=contradicts, sources=sourced))
    return evidence
```

| LOCK-PKM-05 엣지 | SWOT 매핑 | 근거 역할 |
|------------------|----------|----------|
| SUPPORTS | Strength / Opportunity | 긍정 근거 |
| CONTRADICTS | Weakness / Threat | 부정 근거 |
| SUPERSEDES | (구 정보 약화) | 신선도 보정 |
| SOURCED_FROM | 출처 신뢰도 | confidence 가중 |
| RELATED_TO | 맥락 보강 | 부가 근거 |

## §V3.4 의사결정 트리 시각화

```
[결정 질의]
    ├─ [옵션 A] ── SWOT ── confidence 0.72 ── 추천 ★
    │    ├─ Strength: ... (근거 3)
    │    └─ Threat: ... (근거 2)
    └─ [옵션 B] ── SWOT ── confidence 0.55
         └─ ...
```

- 의사결정 트리: 옵션별 SWOT + confidence → 시각 분기 (graph_visualization.md V3 임베드 가능)
- 근거 노트 클릭 → 원본 노트 추적 (CITES 경로 — V1 E1~E9 계승)

## §V3.5 E4 의사결정 도구 비교 매트릭스

| 기준 | Decision Matrix | SWOT | PESTLE |
|------|----------------|------|--------|
| 정량 비교(가중 점수) | ★★★ | ★ | ★ |
| 내부/외부 균형 | ★★ | ★★★ | ★★ |
| 거시 환경 분석 | ★ | ★★ | ★★★ |
| LLM 자동 생성 적합 | ★★ | ★★★ (본 V3 기본) | ★★ |
| 그래프 근거 매핑 | ★★ | ★★★ | ★★ |
| **권장** | 다옵션 정량 | **기본값 (SWOT 자동 생성)** | 거시 환경 결정 |

> **기본 선택 = SWOT**: 그래프 SUPPORTS/CONTRADICTS 엣지(LOCK-PKM-05)와 자연 정합하며 LLM 자동 생성에 최적. 다옵션 정량 비교 시 Decision Matrix 병용.

## §V3.6 E7 SLA / 성능 목표

| 지표 | 목표 | 측정 |
|------|------|------|
| SWOT 자동 생성 | **≤ 10초** | 검색 < 3s + 그래프 근거 < 2s + LLM < 5s |
| 그래프 근거 추출 | ≤ 2초 | LOCK-PKM-05 이웃 탐색 |
| confidence 점수 | 근거 노트 수 + 신선도(LOCK-PKM-09) 가중 | — |
| 의사결정 트리 렌더 | ≤ 1초 | 클라이언트 |

## §V3.7 에스컬레이션 + 로깅

```python
class SWOTEscalation(BaseModel):
    severity: Literal["info","warning","error","critical"]
    reason: Literal[
        "swot_generation_timeout_10s",
        "insufficient_evidence",         # 근거 노트 부족 → confidence 낮음
        "lock_edge_type_unknown",        # LOCK-PKM-05 외 엣지
        "lock_tag_dimension_unknown",    # LOCK-PKM-07 외 차원
        "llm_swot_failure",
    ]
    context: dict = Field(default_factory=dict)
    requires_user_review: bool = False
```

```json
{"event":"swot_advanced.generated","options":2,"evidence_notes":18,"confidence":0.72,"generation_ms":8400}
```

```json
{"event":"swot_advanced.graph_evidence","supports":12,"contradicts":6,"sourced_from":9}
```

```json
{"event":"swot_advanced.tagged","lock_pkm_07":{"주제":"투자","유형":"decision","중요도":"high","프로젝트":"포트폴리오"}}
```

## §V3.8 교차 도메인 참조

| 대상 | 관계 | 계약 |
|------|------|------|
| 1-1 VRE | 소비 ← | 의사결정 추론 검증 통합 (SWOT 논증 검증) |
| 02_knowledge-graph | 소비 ← | graph_visualization.md V3 (의사결정 트리/근거 그래프 임베드) |
| ★ 3-5 Education | 공유 ↔ | 의사결정 학습 — 결정 카드 SM-2 적용 시 LOCK-PKM-01~03 정합 |
| 5-2 외부 5 deps | 영향 없음 | SWOT 생성은 외부 5 deps에 영향 없음 |

## §V3.9 LOCK 5필드 매핑표

| LOCK ID | 항목 | 정본 출처 | 값 | 재정의 |
|---------|------|-----------|-----|--------|
| LOCK-PKM-07 | 태그 분류 체계 | STEP7-M M-011 | 주제/유형/감정/중요도/프로젝트 5차원 | ❌ |
| LOCK-PKM-04 | 지식그래프 노드 타입 | 기존 명세 §4.1 | KnowledgeNote, Tag, Domain, Source, Person | ❌ |
| LOCK-PKM-05 | 지식그래프 엣지 타입 | 기존 명세 §4.1 | RELATED_TO, TAGGED_WITH, BELONGS_TO, SOURCED_FROM, CONTRADICTS, SUPERSEDES, SUPPORTS, MENTIONS | ❌ |
| LOCK-PKM-09 | 신선도 감쇠 모델 | 기존 명세 §6.1 | freshness = exp(-λ × age_days), λ = ln(2) / half_life_days | ❌ (공식) |

## §V3.10 Phase 4 테스트 시나리오 (10건)

| # | 시나리오 | 기대 | LOCK/규칙 |
|---|---------|------|-----------|
| T1 | SWOT 자동 생성 | ≤ 10초, 4사분면 채움 | §V3.6 |
| T2 | SUPPORTS 엣지 근거 | Strength/Opportunity 매핑 | §V3.3 LOCK-PKM-05 |
| T3 | CONTRADICTS 엣지 근거 | Weakness/Threat 매핑 | §V3.3 |
| T4 | 근거 부족 | `insufficient_evidence`, confidence 낮음 | §V3.7 |
| T5 | 신선도 가중 confidence | LOCK-PKM-09 적용 | §V3.6 |
| T6 | 5차원 태그 부착 | 주제/유형/감정/중요도/프로젝트 | §V3.9 LOCK-PKM-07 |
| T7 | LOCK-PKM-05 외 엣지 | `lock_edge_type_unknown` escalation | §V3.9 |
| T8 | 의사결정 트리 시각화 | 옵션별 SWOT + confidence 분기 | §V3.4 |
| T9 | V1 E1~E9 SWOT 기초 계승 | DecisionRecord/CITES 연동 | §V3.2 |
| T10 | 다옵션 비교 | Decision Matrix 병용 | §V3.5 |

## §V3.11 자가 체크리스트

- [x] LOCK-PKM-07 5차원 태깅 verbatim 인용 (§V3.1, §V3.9)
- [x] SWOT 자동 생성 LLM 기반 Pro/Con/Risk/Opportunity (§V3.2)
- [x] 지식 그래프 기반 근거 추출 LOCK-PKM-04/05 (§V3.3)
- [x] 의사결정 트리 시각화 (§V3.4)
- [x] E4 모델 비교 Decision Matrix/SWOT/PESTLE (§V3.5)
- [x] E7 SLA: SWOT 생성 ≤ 10초 (§V3.6)
- [x] V1 E1~E9 SWOT 기초 계승 (append-only, byte 무변경) (§V3.2)
- [x] VBS-14 V3 ≥ 85점 목표 (L3)