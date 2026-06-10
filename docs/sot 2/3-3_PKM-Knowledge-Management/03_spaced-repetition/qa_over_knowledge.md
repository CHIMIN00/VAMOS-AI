# qa_over_knowledge.md — 지식 기반 QA 파이프라인 (M-024)

> **Status**: APPROVED (L3)
> **작성일**: 2026-04-09
> **정본 소유 개념**: 개인 지식 기반 질의응답, 멀티홉 QA, 시간 인식 QA, 대화형 후속 질문
> **SoT 근거**: STEP7-M Part 3a (M-024 L437-450) — 질의응답 (QA over Knowledge)
> **담당 M-ID**: M-024 (V1 NEW)
> **상위 인덱스**: [_index.md](./_index.md)

---

## LOCK 인용

> LOCK (기존 명세 §3.2 / LOCK-PKM-08): 지식 카테고리 — concept, fact, procedure, decision, reference, opinion, code_snippet, bookmark

> LOCK (기존 명세 §6.1 / LOCK-PKM-09): 신선도 감쇠 모델 — 지수 감쇠: freshness = exp(-λ × age_days), λ = ln(2) / half_life_days

---

## 아키텍처 개요

```
[사용자 질문]
    ↓
[QA Intent Classifier]
    ├─ 단일 사실 질문 → SingleHopQA
    ├─ 복합 질문      → MultiHopQA (분해 → 서브쿼리)
    ├─ 시간 질문      → TemporalQA ("3개월 전에는...")
    ├─ 비교 질문      → CompareQA ("A vs B")
    └─ 후속 질문      → FollowUpQA (대화 이력 참조)
    ↓
[RAG Pipeline (M-023)]
    4-Index Fusion → 소스 우선순위 → Context Build
    ↓
[Answer Generator]
    ├─ 답변 생성 (with citations)
    ├─ 답변 불가 시 "해당 지식이 없습니다" 명시
    └─ 후속 질문 제안 (3개)
    ↓
[Faithfulness + Relevance Check]
    ↓
[QA Response + Citations + Follow-ups]
```

---

## E1. Input Schema

```python
class QARequest:
    question: str                                # 사용자 질문 (≤ 1000 chars)
    conversation_id: Optional[UUID]              # 멀티턴 대화 ID
    conversation_history: list[QATurn] = []      # 이전 Q&A 히스토리 (≤ 10턴)
    
    # 검색 범위
    scope: QAScope = QAScope()
    
    # 응답 옵션
    answer_style: Literal["brief", "detailed", "structured"] = "detailed"
    include_citations: bool = True
    include_follow_ups: bool = True
    max_follow_ups: int = 3
    language: Literal["ko", "en", "auto"] = "auto"

class QATurn:
    question: str
    answer: str
    citations: list[UUID]                        # 참조된 노트 ID
    timestamp: datetime

class QAScope:
    domains: Optional[list[str]] = None          # 특정 도메인 한정
    categories: Optional[list[KnowledgeCategory]] = None  # LOCK-PKM-08
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    project: Optional[str] = None                # 특정 프로젝트 한정
    note_ids: Optional[list[UUID]] = None        # 특정 노트 집합 한정
```

## E2. Output Schema

```python
class QAResponse:
    answer: str                                  # 생성된 답변
    answer_type: Literal[
        "direct",          # 직접 답변 가능
        "synthesized",     # 여러 노트 종합
        "partial",         # 부분적 답변 (일부 정보 부재)
        "not_found",       # 관련 지식 없음
    ]
    confidence: float = 0.0                       # 0..1 (미산정 시 0.0, confidence 계산 E-섹션 연동 대상)
    citations: list[QACitation] = field(default_factory=list)
    follow_up_questions: list[str] = field(default_factory=list)  # 후속 질문 제안
    reasoning_chain: Optional[list[str]] = None  # 멀티홉 시 추론 경로
    latency_ms: float

class QACitation:
    note_id: UUID
    title: str
    cited_text: str                              # 인용된 원문 (≤ 300 chars)
    category: KnowledgeCategory
    created_at: datetime                         # 원본 노트 생성 시각 (시간순 정렬용)
    freshness_score: float
    citation_marker: str                         # "[1]"
    relevance: float                             # 이 질문에 대한 관련도
```

## E3. Algorithm — Intent Classifier

```python
# qa_intent_classifier.py
class QAIntentClassifier:
    """질문 의도 분류 → QA 전략 결정"""
    
    async def classify(self, question: str, history: list[QATurn]) -> QAIntent:
        # 후속 질문 감지 (대명사, 생략 표현)
        if history and self._is_follow_up(question, history[-1]):
            resolved = await self._resolve_coreference(question, history)
            return QAIntent(type="follow_up", resolved_question=resolved)
        
        # 시간 표현 감지
        temporal = self._detect_temporal(question)
        if temporal:
            return QAIntent(type="temporal", time_range=temporal)
        
        # 비교 표현 감지 ("A vs B", "차이점", "비교")
        if self._detect_comparison(question):
            entities = await self._extract_comparison_entities(question)
            return QAIntent(type="compare", entities=entities)
        
        # 복합 질문 감지 (접속사, 여러 질문 포함)
        sub_questions = await self._decompose_if_complex(question)
        if len(sub_questions) > 1:
            return QAIntent(type="multi_hop", sub_questions=sub_questions)
        
        return QAIntent(type="single_hop")
    
    def _is_follow_up(self, question: str, last_turn: QATurn) -> bool:
        follow_up_signals = ["그거", "그건", "위에서", "방금", "더 자세히", "왜", "어떻게"]
        return any(s in question for s in follow_up_signals)
    
    def _detect_temporal(self, question: str) -> Optional[TimeRange]:
        patterns = [
            (r"(\d+)개월\s*전", lambda m: timedelta(days=int(m.group(1)) * 30)),
            (r"(\d+)주\s*전", lambda m: timedelta(weeks=int(m.group(1)))),
            (r"지난\s*(주|달|분기)", lambda m: self._last_period(m.group(1))),
            (r"최근", lambda m: timedelta(days=30)),
        ]
        for pattern, delta_fn in patterns:
            match = re.search(pattern, question)
            if match:
                delta = delta_fn(match)
                return TimeRange(start=datetime.now() - delta, end=datetime.now())
        return None
```

## E4. Algorithm — 멀티홉 QA

```python
# multihop_qa.py
class MultiHopQA:
    """복합 질문 → 서브 질문 분해 → 순차 답변 → 종합"""
    
    async def answer(self, intent: QAIntent, rag: RAGPipeline) -> QAResponse:
        sub_questions = intent.sub_questions
        reasoning_chain = []
        accumulated_context = []
        
        for i, sub_q in enumerate(sub_questions):
            # 이전 서브 답변을 컨텍스트에 추가
            enriched_query = sub_q
            if accumulated_context:
                enriched_query = f"{sub_q}\n\n이전 정보:\n" + "\n".join(accumulated_context)
            
            # RAG 검색 + 답변 생성
            sub_result = await rag.query(RAGRequest(query=enriched_query))
            
            reasoning_chain.append(
                f"[Step {i+1}] {sub_q} → {sub_result.answer[:100]}..."
            )
            accumulated_context.append(f"Q: {sub_q}\nA: {sub_result.answer}")
        
        # 최종 종합 답변
        final_answer = await self._synthesize(
            original_question=intent.original_question,
            sub_answers=accumulated_context,
        )
        
        return QAResponse(
            answer=final_answer,
            answer_type="synthesized",
            reasoning_chain=reasoning_chain,
        )
```

## E5. Algorithm — 시간 인식 QA

```python
# temporal_qa.py
class TemporalQA:
    """시간 범위가 포함된 질문 처리"""
    
    async def answer(self, intent: QAIntent, rag: RAGPipeline) -> QAResponse:
        time_range = intent.time_range
        
        # 시간 범위 필터로 RAG 검색
        result = await rag.query(RAGRequest(
            query=intent.resolved_question or intent.original_question,
            scope=QAScope(
                date_from=time_range.start,
                date_to=time_range.end,
            ),
        ))
        
        # 시간순 정렬이 의미 있는 경우
        if self._needs_chronological(intent.original_question):
            result.citations.sort(key=lambda c: c.created_at)
            # 답변에 시간 맥락 추가
            result.answer = await self._add_temporal_context(
                result.answer, result.citations,
            )
        
        return result
```

## E6. Algorithm — 비교 QA

```python
# compare_qa.py
class CompareQA:
    """A vs B 비교 질문 처리"""
    
    async def answer(self, intent: QAIntent, rag: RAGPipeline) -> QAResponse:
        entities = intent.entities  # ["A", "B"]
        
        # 각 엔티티별 독립 검색
        entity_knowledge = {}
        for entity in entities:
            result = await rag.query(RAGRequest(query=entity))
            entity_knowledge[entity] = result
        
        # 비교 답변 생성
        comparison_prompt = f"""다음 두 주제에 대한 개인 지식을 비교하세요:

{chr(10).join(f"## {e}{chr(10)}{entity_knowledge[e].answer}" for e in entities)}

비교 관점: 공통점, 차이점, 장단점
구조화된 비교표 포함"""
        
        comparison = await self.llm.generate(comparison_prompt)
        
        # 양쪽 인용 합침
        all_citations = []
        for ek in entity_knowledge.values():
            all_citations.extend(ek.citations)
        
        return QAResponse(
            answer=comparison,
            answer_type="synthesized",
            citations=all_citations,
        )
```

## E7. Algorithm — 후속 질문 생성

```python
# follow_up_generator.py
class FollowUpGenerator:
    """답변 기반 후속 질문 3개 자동 생성"""
    
    async def generate(
        self, question: str, answer: str, citations: list[QACitation], max_count: int = 3,
    ) -> list[str]:
        prompt = f"""다음 Q&A를 읽고, 사용자가 추가로 궁금해할 만한 후속 질문 {max_count}개를 생성하세요.

Q: {question}
A: {answer[:500]}

참조 지식 주제: {', '.join(c.title for c in citations[:5])}

규칙:
- 답변에서 다루지 않은 관련 측면
- 더 깊은 이해를 위한 질문
- 실용적/행동 가능한 질문 우선

JSON: [{{"question": "..."}}]"""
        
        result = await self.llm.generate(prompt, temperature=0.7)
        parsed = parse_json(result)
        return [item["question"] for item in parsed[:max_count]]
```

## E8. 에러 처리 + 성능 요구사항

```python
QA_SLA = {
    "single_hop_p50_ms": 2000,
    "single_hop_p95_ms": 5000,
    "multi_hop_p50_ms": 5000,
    "multi_hop_p95_ms": 15000,
    "max_sub_questions": 5,          # 멀티홉 분해 상한
    "min_confidence": 0.3,           # 이 이하면 "not_found" 반환
}

# 답변 불가 처리
NOT_FOUND_RESPONSES = {
    "ko": "이 주제에 대해 저장된 지식이 없습니다. 관련 정보를 추가하시겠어요?",
    "en": "No stored knowledge found on this topic. Would you like to add related information?",
}

# 낮은 신뢰도 경고
LOW_CONFIDENCE_WARNING = "⚠ 이 답변은 제한된 지식에 기반합니다. 정확도를 확인해주세요."
```

---

## 의존성

| 방향 | 대상 | 내용 |
|------|------|------|
| ← | rag_optimization.md (M-023) | RAG 파이프라인 (4-Index Fusion) |
| ← | semantic_search.md (M-021) | 검색 엔진 |
| ← | context_aware_recommendation.md (M-022) | 컨텍스트 기반 스코프 |
| ← | T2-CORE_AI | LLM 답변 생성 |
| → | knowledge_summary.md (M-025) | QA 결과 → 자동 요약 입력 |
| → | smart_reminder.md (M-027) | 자주 묻는 질문 → 복습 큐 |
