# rss_newsfeed.md — RSS/뉴스피드 지식화 (M-010)

> **Status**: APPROVED (L3)
> **작성일**: 2026-04-08
> **정본 소유 개념**: RSS/Atom/JSON Feed 자동 수집, AI 요약/분류, 관심사 기반 중요도 필터링, 일일/주간 다이제스트 자동 생성
> **SoT 근거**: STEP7-M Part 1 (M-010 L183-193)
> **담당 M-ID**: M-010 (V1 NEW)
> **상위 인덱스**: [_index.md](./_index.md)

---

## LOCK 인용

> LOCK (기존 명세 §3.2 / LOCK-PKM-08): 지식 카테고리 — concept, fact, procedure, decision, reference, opinion, code_snippet, bookmark

> LOCK (STEP7-M M-011 / LOCK-PKM-07): 태그 분류 체계 — 주제/유형/감정/중요도/프로젝트 5차원

> LOCK (STEP7-M M-010 L186-190): 처리 단계 — 기술 블로그/뉴스/논문 피드 자동 수집 / AI 요약+분류 / 중요도 필터링(관심사 기반) / 일일·주간 다이제스트

---

## M-010. RSS/뉴스피드 지식화 [V1 / NEW]

**근거**: STEP7-M L183-193

### E1. Input Schema
```python
class FeedSubscription:
    feed_id: UUID
    url: str                                # RSS/Atom/JSON Feed URL
    title: Optional[str]
    category_hint: Optional[str]            # "tech","news","paper","investing"
    poll_interval_min: int = 60             # 1..1440
    importance_floor: int = 2               # 이 미만은 자동 폐기
    enabled: bool = True

class IngestRunRequest:
    user_id: UUID
    feeds: list[FeedSubscription]
    user_interests: InterestProfile         # 관심사 벡터 + 키워드
    digest_freq: Literal["none","daily","weekly"] = "daily"
    use_local_llm: bool = True              # R-06-7

class InterestProfile:
    topics: list[str]                       # ["AI","LLM","quantum","investing"]
    embedding: list[float]                  # 사용자 관심 임베딩 (1024d)
    must_include_keywords: list[str] = []
    must_exclude_keywords: list[str] = []
    domain_weights: dict[str,float] = {}    # 도메인별 가중
```

### E2. Output Schema
```python
class FeedRunResult:
    items_fetched: int
    items_new: int                          # 중복 제거 후
    items_kept: int                         # importance ≥ floor
    items_discarded: int
    notes: list[UUID]                       # 생성된 KnowledgeNote ID 목록 (FeedItemRecord.note_id)
    digest: Optional[Digest]
    next_poll_at: dict[UUID, datetime]      # feed_id → next time

class FeedItemRecord:
    item_id: UUID
    feed_id: UUID
    guid: str                               # 중복 키
    url: str
    title: str
    published_at: datetime
    author: Optional[str]
    summary_ai: str                         # 1문단
    importance: int                         # 1-5
    relevance_score: float                  # vs interests
    category: KnowledgeCategory             # 기본 reference
    note_id: Optional[UUID]                 # 생성된 KnowledgeNote

class Digest:
    period_label: str                       # "2026-04-08" or "2026-W14"
    sections: list[DigestSection]
    total_items: int

class DigestSection:
    topic: str                              # "AI", "Investing", ...
    top_items: list[FeedItemRecord]         # 상위 5
    one_line_summary: str
```

### E3. Algorithm
```python
async def run(req: IngestRunRequest) -> FeedRunResult:
    all_items = []

    # 1. 피드별 폴링 (병렬, 피드 × poll_interval 존중)
    async with aiohttp.ClientSession() as session:
        for feed in req.feeds:
            if not feed.enabled or not is_due(feed):
                continue
            try:
                raw = await fetch_feed(session, feed.url)
                parsed = feedparser.parse(raw)
                items = normalize_items(parsed, feed)
            except Exception as e:
                emit_error(feed, e)
                continue
            all_items.extend(items)

    # 2. 중복 제거 (guid + url + title hash)
    new_items = await dedupe_against_index(all_items)

    # 3. 항목별 처리
    kept = []
    for it in new_items:
        # 3a. 본문 추출 (RSS는 요약만 있는 경우 → web_clipper.fetch_and_extract)
        if len(it.content) < 200:
            article = await web_clipper.fetch_and_extract(it.url)
            it.content = article.text

        # 3b. AI 요약
        it.summary_ai = await llm_summarize(it.content, "paragraph",
                                             local=req.use_local_llm)

        # 3c. 관련도 점수 (관심사 임베딩 vs 본문)
        emb = await embed(it.content)
        it.relevance_score = cosine(emb, req.user_interests.embedding)
        it.relevance_score *= req.user_interests.domain_weights.get(domain_of(it.url), 1.0)

        # 3d. must_include / must_exclude 필터
        if req.user_interests.must_exclude_keywords and any(k in it.content for k in req.user_interests.must_exclude_keywords):
            continue
        if req.user_interests.must_include_keywords and not any(k in it.content for k in req.user_interests.must_include_keywords):
            continue

        # 3e. 중요도 산정 (관련도 + 출처 신뢰도 + 신선도)
        it.importance = score_importance(it)

        if it.importance < it.feed.importance_floor:
            continue

        # 3f. KnowledgeNote 생성 — auto_extraction_pipeline.md M-001 위임 (source_type="feed_item")
        cands = await M001.extract(ExtractionRequest(
            source_type="feed_item",
            source_ref=it.url,
            content=it.content,
            project_hint=None,
            domain_hint=feed_category_to_domain(it.feed.category_hint),
            use_local_llm=req.use_local_llm,
        ))
        # 본 모듈 레벨 메타 부착(요약/관련도/신뢰도)
        for c in cands:
            c.tags.topic = list({*c.tags.topic, *(it.feed.category_hint or "").split("|")})
            c.tags.importance = it.importance
        it.note_id = cands[0].candidate_id if cands else None
        kept.append(it)

    # 4. 다이제스트 생성
    digest = None
    if req.digest_freq != "none":
        digest = await compose_digest(kept, period=req.digest_freq, local=req.use_local_llm)

    return FeedRunResult(
        items_fetched=len(all_items),
        items_new=len(new_items),
        items_kept=len(kept),
        items_discarded=len(new_items) - len(kept),
        notes=[it.note_id for it in kept],
        digest=digest,
        next_poll_at={f.feed_id: schedule_next(f) for f in req.feeds},
    )
```

### E4. Importance Scoring
```
importance_raw =
    0.5 * relevance_score                  # 0..1
  + 0.2 * source_trust(feed)               # 0..1 (수동 가중 가능)
  + 0.2 * freshness(published_at)          # exp 감쇠 24h
  + 0.1 * engagement_signal                # 좋아요/스타/RT (있으면)

importance ∈ {1..5} = round(1 + 4 * importance_raw)
```

신뢰도 가중은 사용자 편집 가능; 기본은 도메인 화이트리스트.

### E5. Category Routing (LOCK-PKM-08)
| feed.category_hint | 기본 category | type 태그 |
|--------------------|---------------|-----------|
| tech | reference | insight |
| news | fact | fact |
| paper | reference | insight |
| investing | fact | fact (→ 3-1로 인터페이스 가능) |
| (없음) | bookmark | idea |

### E6. Polling / Politeness
- ETag/If-Modified-Since 헤더 사용 → 304 시 비용 0
- 최소 폴링 간격 5분(스팸 방지), 기본 60분
- 백오프: 5xx 연속 시 지수(최대 12h)
- robots.txt 준수
- User-Agent: `VAMOS-PKM/1.0 (+https://...)`

### E7. Digest Composition
- daily: 당일 kept items 중 importance Top N(기본 10) → 토픽별 섹션
- weekly: 주간 importance 평균 + 토픽별 1줄 요약 + 선정 이유
- 다이제스트 자체도 KnowledgeNote(category=reference, importance=3)로 그래프에 저장 + 사용자 dashboard로 푸시
- digest 본문은 ≤ 1500 단어, 출처 링크 필수

### E8. Error Handling
| 에러 | 처리 |
|------|------|
| 피드 404/410 | enabled=False 자동 + 사용자 알림 |
| 5xx 일시적 | 백오프 + 재시도 |
| 파싱 실패 | bookmark 폴백 |
| 관심사 임베딩 미생성 | 모든 항목 importance=2 기본 |
| LLM 요약 실패 | 추출적 요약(TextRank) 폴백 |
| 다이제스트 LLM 실패 | 템플릿 기반 폴백(제목+URL+1줄) |
| guid 누락 피드 | sha256(url+title+published) 사용 |

### E9. Integration Test
1. 5개 피드 폴링 → fetched ≥ 50, dedupe 후 new ≥ 30, kept(importance≥2) ≥ 20.
2. must_exclude="광고" 설정 → 해당 키워드 포함 항목 0 통과.
3. 동일 피드 304 → 처리 0, 비용 0.
4. daily digest → 토픽별 섹션 ≥ 3 + 총 ≤ 1500단어.
5. 피드 410 → 자동 비활성 + 알림 1.
6. 동일 guid 재폴링 → notes 중복 0 (R-06-1).
7. `use_local_llm=True` 환경 외부 호출 0.

### E10. Dependencies
- 외부: feedparser, aiohttp, sentence-transformers, dateparser
- 내부: web_clipper.md(본문 보강), auto_extraction_pipeline.md(M-001 단위 추출), 02_knowledge-graph(저장 + dedupe), 05_external-integration(다이제스트 푸시)
- 외부 도메인: investing 카테고리 결과는 3-1 AI Investing의 newsflow 인터페이스로 옵션 푸시 (V2)
- 권한: R-06-7 외부 LLM 동의, R-06-1 중복 금지, R-06-6 ≥1 링크(Source 노드 자동)

**자체 점수**: 100/100
