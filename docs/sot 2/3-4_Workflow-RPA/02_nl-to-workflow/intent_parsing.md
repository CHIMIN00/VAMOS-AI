# 의도 파싱 파이프라인 — L3 상세 명세

> **N-ID**: 기존 명세 §3 (EXTEND)
> **V단계**: V1
> **도메인**: 3-4_Workflow-RPA / 02_nl-to-workflow
> **정본**: sot 2/3-4_Workflow-RPA/02_nl-to-workflow/intent_parsing.md
> **교차참조**: nl_to_dag_conversion.md (DAG 변환 파이프라인 Stage 1 소비자), WORKFLOW_RPA_상세명세.md §3 (기존 명세 원본)

---

## 1. 개요

자연어 워크플로우 요청에서 **의도(intent)**, **트리거(trigger)**, **실행 단계(steps)**, **파라미터(parameters)**를 추출하는 LLM 기반 파싱 엔진이다. 기존 명세 §3의 `WorkflowIntentParser`를 L3 수준으로 승급하여, 4단계 파이프라인(키워드 추출 → 의도 분류 → 파라미터 추출 → 노드 후보 생성)을 구현 즉시 투입 가능한 수준으로 정의한다.

> LOCK (기존 명세 §2 / STEP7-N N-001 / LOCK-WF-01): LLMNode, APINode, ConditionNode, ParallelNode, HumanApprovalNode, TransformNode, NotificationNode, LoopNode, SubworkflowNode, ErrorHandlerNode, DelayNode, CodeNode — 12 타입은 제거 불가. 추가만 허용.

> LOCK (LOCK-WF-06): 트리거 7유형 — Time(cron), Event(이벤트), Condition(조건), Webhook(웹훅), Manual(수동), Conversation(대화 기반), Ambient(앰비언트)

---

## 2. 파이프라인 아키텍처

```
[자연어 입력]
    │
    ▼
[Phase A: 키워드 추출]
    │  keywords[], temporal_markers[], action_verbs[]
    ▼
[Phase B: 의도 분류]
    │  intent_category, confidence
    ▼
[Phase C: 파라미터 추출]
    │  trigger_hint, parameters{}, entities[]
    ▼
[Phase D: 노드 후보 생성]
    │  StepDescription[] (order, action, inferred_node_type, parameters)
    ▼
[WorkflowIntent 출력] → nl_to_dag_conversion.md Stage 2~5
```

---

## 3. Phase A: 키워드 추출

자연어 입력에서 의도 분류에 필요한 키워드를 규칙 기반 + LLM 보조로 추출한다.

### 3.1 키워드 사전

```typescript
const KEYWORD_DICT: Record<string, string[]> = {
  // 시간 관련 (트리거 힌트)
  temporal: [
    "매일", "매주", "매월", "매년", "~마다", "~시에", "~분마다",
    "아침", "저녁", "오전", "오후", "평일", "주말",
    "월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"
  ],

  // 이벤트 관련 (트리거 힌트)
  event: [
    "~하면", "~될 때", "~가 오면", "새로운", "수신", "도착",
    "변경", "업데이트", "추가", "삭제", "생성"
  ],

  // 조건 관련 (트리거 힌트)
  condition: [
    "~이상", "~이하", "~초과", "~미만", "~보다",
    "변동", "넘으면", "떨어지면", "올라가면"
  ],

  // 데이터 처리
  data: [
    "수집", "크롤링", "스크래핑", "모니터링", "추출",
    "변환", "정리", "필터", "집계", "통계"
  ],

  // 알림/출력
  notification: [
    "알려줘", "알림", "보내줘", "전송", "리포트",
    "이메일", "슬랙", "텔레그램", "푸시"
  ],

  // 자동화 일반
  automation: [
    "자동으로", "자동화", "반복", "루틴",
    "매번", "항상", "자동 실행"
  ],

  // 승인/결재
  approval: [
    "승인", "검토", "결재", "확인", "리뷰"
  ]
};
```

### 3.2 키워드 추출 알고리즘

```
function extract_keywords(user_input: string) -> KeywordResult:
    tokens = tokenize_korean(user_input)   // 형태소 분석 (mecab/kiwi)
    result = KeywordResult(
        raw_input=user_input,              // 원본 입력 보존 (Phase B·C에서 참조)
        keywords=[],
        temporal_markers=[],
        action_verbs=[],
        entities=[]
    )

    // Phase A-1: 규칙 기반 매칭
    for category, patterns in KEYWORD_DICT:
        for pattern in patterns:
            if pattern in user_input or fuzzy_match(pattern, tokens, threshold=0.8):
                result.keywords.append(Keyword(text=pattern, category=category))

    // Phase A-2: 형태소 분석으로 동사/명사 추출
    for token in tokens:
        if token.pos == "VV" or token.pos == "VX":   // 동사
            result.action_verbs.append(token.surface)
        elif token.pos == "NNG" or token.pos == "NNP":  // 명사(일반/고유)
            result.entities.append(token.surface)

    // Phase A-3: 시간 표현 파싱
    temporal_patterns = [
        (r"매일\s*(아침|오전|오후|저녁)?\s*(\d{1,2})시", "daily"),
        (r"매주\s*(월|화|수|목|금|토|일)요일", "weekly"),
        (r"매월\s*(\d{1,2})일", "monthly"),
        (r"(\d+)분마다", "interval_min"),
        (r"(\d+)시간마다", "interval_hour"),
    ]
    for pattern, type in temporal_patterns:
        match = regex_search(pattern, user_input)
        if match:
            result.temporal_markers.append(TemporalMarker(
                raw=match.group(0), type=type, parsed=parse_temporal(match)
            ))

    return result
```

### 3.3 시간 표현 → cron 변환

| 자연어 표현 | 파싱 결과 | cron |
|------------|----------|------|
| 매일 아침 9시 | daily, hour=9 | `0 9 * * *` |
| 매일 오후 6시 | daily, hour=18 | `0 18 * * *` |
| 평일 오전 9시 | weekday, hour=9 | `0 9 * * 1-5` |
| 매주 월요일 10시 | weekly, dow=1, hour=10 | `0 10 * * 1` |
| 매월 1일 | monthly, day=1 | `0 0 1 * *` |
| 30분마다 | interval, min=30 | `*/30 * * * *` |
| 2시간마다 | interval, hour=2 | `0 */2 * * *` |

```
function temporal_to_cron(marker: TemporalMarker) -> string:
    match marker.type:
        case "daily":
            hour = marker.parsed.hour or 0
            return f"0 {hour} * * *"
        case "weekday":
            hour = marker.parsed.hour or 9
            return f"0 {hour} * * 1-5"
        case "weekly":
            dow = marker.parsed.day_of_week   // 0=일, 1=월, ..., 6=토
            hour = marker.parsed.hour or 0
            return f"0 {hour} * * {dow}"
        case "monthly":
            day = marker.parsed.day
            return f"0 0 {day} * *"
        case "interval_min":
            min = marker.parsed.minutes
            return f"*/{min} * * * *"
        case "interval_hour":
            hour = marker.parsed.hours
            return f"0 */{hour} * * *"
```

---

## 4. Phase B: 의도 분류

키워드 추출 결과를 기반으로 워크플로우 의도 카테고리를 분류한다.

### 4.1 분류 카테고리 (기존 명세 §3 계승)

| 카테고리 | 설명 | 대표 키워드 | 우선 트리거 |
|---------|------|------------|-----------|
| `scheduled_task` | 시간 기반 반복 작업 | 매일, 매주, ~시에 | Time |
| `event_triggered` | 이벤트 기반 반응 작업 | ~하면, ~될 때, 새로운 | Event |
| `data_pipeline` | 데이터 수집/처리 파이프라인 | 수집, 크롤링, 모니터링 | Time / Event |
| `notification` | 알림/리포트 생성 | 알려줘, 보내줘, 리포트 | (상위 의도에 종속) |
| `automation` | 범용 자동화 | 자동으로, 반복 | Manual / Time |
| `approval_flow` | 승인/결재 워크플로우 | 승인, 검토, 결재 | Manual / Event |

### 4.2 분류 알고리즘 (규칙 + LLM 하이브리드)

```
function classify_intent(keywords: KeywordResult) -> IntentClassification:
    // Step 1: 규칙 기반 스코어링
    scores = {}
    for category in IntentCategory:
        score = 0.0
        // 키워드 카테고리 매칭 가중치
        category_weights = {
            "scheduled_task":  { temporal: 0.5, automation: 0.2, data: 0.1, notification: 0.1 },
            "event_triggered": { event: 0.5, condition: 0.2, notification: 0.1 },
            "data_pipeline":   { data: 0.5, temporal: 0.1, automation: 0.2 },
            "notification":    { notification: 0.5, temporal: 0.1 },
            "automation":      { automation: 0.4, temporal: 0.2, data: 0.1 },
            "approval_flow":   { approval: 0.6, notification: 0.1 },
        }

        for keyword in keywords.keywords:
            weight = category_weights[category].get(keyword.category, 0.0)
            score += weight

        // 시간 표현 보너스
        if keywords.temporal_markers and category == "scheduled_task":
            score += 0.3

        scores[category] = min(score, 1.0)

    // Step 2: 규칙 기반으로 충분히 확신 (score ≥ 0.7) → LLM 스킵
    best_category = max(scores, key=scores.get)
    best_score = scores[best_category]

    if best_score >= 0.7:
        return IntentClassification(
            category=best_category,
            confidence=best_score,
            method="rule_based"
        )

    // Step 3: 불확실 → LLM 보조 분류
    llm_result = call_llm(
        model="claude-haiku-4-5",            // 분류는 경량 모델로 충분
        prompt=INTENT_CLASSIFICATION_PROMPT.format(
            user_input=keywords.raw_input,
            keyword_summary=summarize_keywords(keywords),
            rule_scores=scores
        ),
        response_format="json",
        temperature=0.1
    )
    // LLM 결과: { "category": "...", "confidence": 0.XX, "reasoning": "..." }
    return IntentClassification(
        category=llm_result.category,
        confidence=llm_result.confidence,
        method="llm_assisted",
        reasoning=llm_result.reasoning
    )
```

### 4.3 의도 분류 LLM 프롬프트

```
SYSTEM:
워크플로우 의도 분류기입니다. 사용자의 자연어 요청을 6개 카테고리 중 하나로 분류합니다.

카테고리:
- scheduled_task: 시간 기반 반복 작업 (매일, 매주, 정기적)
- event_triggered: 이벤트 발생 시 반응 (~하면, ~될 때)
- data_pipeline: 데이터 수집/처리/변환
- notification: 알림/리포트 생성 발송
- automation: 범용 자동화 (분류 불명확 시)
- approval_flow: 승인/결재 프로세스

JSON으로 응답: {"category": "...", "confidence": 0.0~1.0, "reasoning": "..."}

USER:
입력: {{ user_input }}
키워드 분석: {{ keyword_summary }}
규칙 스코어: {{ rule_scores }}

가장 적합한 카테고리를 선택하세요.
```

---

## 5. Phase C: 파라미터 추출

분류된 의도에 따라 트리거 힌트와 도메인 파라미터를 추출한다.

### 5.1 트리거 힌트 생성

```
function extract_trigger_hint(
    classification: IntentClassification,
    keywords: KeywordResult
) -> TriggerHint | null:

    // LOCK-WF-06 7유형: time, event, condition, webhook, manual, conversation, ambient

    match classification.category:
        case "scheduled_task":
            if keywords.temporal_markers:
                marker = keywords.temporal_markers[0]  // 첫 번째 시간 표현 사용
                return TriggerHint(
                    type="time",
                    cron=temporal_to_cron(marker),
                    raw_temporal=marker.raw
                )
            // 시간 표현 없이 "매일" 등만 → 기본값
            return TriggerHint(type="time", cron="0 9 * * *")

        case "event_triggered":
            // condition 키워드 우세 시 condition 트리거로 분기
            condition_count = count_keywords(keywords, "condition")
            event_count = count_keywords(keywords, "event")
            if condition_count > event_count:
                return TriggerHint(
                    type="condition",
                    condition_expr=infer_condition_expr(keywords)
                )
            // 대화 키워드 감지 시 conversation 트리거
            if has_conversation_keywords(keywords):
                return TriggerHint(
                    type="conversation",
                    conversation_keyword=extract_conversation_keyword(keywords)
                )
            event_source = infer_event_source(keywords)
            // webhook 소스일 때 webhook 트리거로 분류
            if event_source == "webhook":
                return TriggerHint(
                    type="webhook",
                    webhook_path=infer_webhook_path(keywords)
                )
            return TriggerHint(
                type="event",
                event_source=event_source,
                event_type=infer_event_type(keywords, event_source)
            )

        case "data_pipeline":
            // 시간 기반이면 time, 조건 기반이면 condition
            if keywords.temporal_markers:
                return TriggerHint(type="time", cron=temporal_to_cron(keywords.temporal_markers[0]))
            if count_keywords(keywords, "condition") > 0:
                return TriggerHint(type="condition", condition_expr=infer_condition_expr(keywords))
            return TriggerHint(type="manual")

        case "notification":
            // 알림은 상위 의도에 종속 — 시간 표현 있으면 time, 없으면 manual
            if keywords.temporal_markers:
                return TriggerHint(type="time", cron=temporal_to_cron(keywords.temporal_markers[0]))
            return TriggerHint(type="manual")

        case "automation":
            // 범용 자동화 — 시간 표현 우선, 없으면 manual
            if keywords.temporal_markers:
                return TriggerHint(type="time", cron=temporal_to_cron(keywords.temporal_markers[0]))
            return TriggerHint(type="manual")

        case "approval_flow":
            return TriggerHint(type="manual")

        case _:
            return TriggerHint(type="manual")


function infer_event_source(keywords: KeywordResult) -> string:
    // 이벤트 소스 추론 키워드 매핑
    source_keywords = {
        "email":       ["이메일", "메일", "수신"],
        "slack":       ["슬랙", "채널", "메시지"],
        "github":      ["PR", "커밋", "이슈", "푸시"],
        "file_system": ["파일", "폴더", "디렉토리", "업로드"],
        "webhook":     ["웹훅", "API", "요청"],
    }
    for source, kws in source_keywords:
        for kw in kws:
            if kw in keywords.raw_input:
                return source
    return "webhook"  // 기본값


function has_conversation_keywords(keywords: KeywordResult) -> bool:
    // 대화 기반 트리거 힌트 키워드
    conversation_kws = ["말하면", "물어보면", "대화", "채팅", "키워드"]
    return any(kw in keywords.raw_input for kw in conversation_kws)


function extract_conversation_keyword(keywords: KeywordResult) -> string:
    // 대화 트리거의 감지 키워드 추출 (LLM 보조)
    return call_llm(
        model="claude-haiku-4-5",
        prompt=f"다음 문장에서 대화 트리거 키워드를 추출하세요: {keywords.raw_input}",
        temperature=0.0
    )


function infer_condition_expr(keywords: KeywordResult) -> string:
    // 조건 트리거 표현식 추론 (키워드 기반)
    for kw in keywords.keywords:
        if kw.category == "condition":
            return kw.text  // 1차: 키워드 원문 반환 (DAG 생성 시 LLM이 정제)
    return ""


function infer_webhook_path(keywords: KeywordResult) -> string:
    // 웹훅 경로 추론
    return "/api/v1/webhooks/{workflow_id}"  // 기본 경로


function count_keywords(keywords: KeywordResult, category: string) -> int:
    return len([kw for kw in keywords.keywords if kw.category == category])
```

### 5.2 도메인 파라미터 추출 (LLM 기반)

키워드·규칙만으로 추출하기 어려운 도메인 파라미터(종목명, URL, 임계값 등)는 LLM으로 추출한다.

```
function extract_parameters(
    user_input: string,
    classification: IntentClassification,
    keywords: KeywordResult
) -> Record<string, any>:

    prompt = PARAMETER_EXTRACTION_PROMPT.format(
        user_input=user_input,
        intent_category=classification.category,
        keywords=keywords.entities
    )

    result = call_llm(
        model="claude-haiku-4-5",
        prompt=prompt,
        response_format="json",
        temperature=0.0       // 파라미터 추출 → deterministic
    )

    // 결과 예시:
    // { "threshold": 3, "unit": "percent", "assets": "관심 종목",
    //   "notification_channel": "push", "data_source": "yfinance" }

    return validate_parameters(result, classification.category)
```

### 5.3 파라미터 추출 LLM 프롬프트

```
SYSTEM:
워크플로우 파라미터 추출기입니다.
사용자의 자연어 요청에서 워크플로우 실행에 필요한 구체적 파라미터를 추출합니다.

## 추출 대상 파라미터
- 수치 (임계값, 개수, 비율 등)
- 대상 (종목명, URL, 파일 경로, 채널명 등)
- 설정 (알림 채널, 형식, 언어 등)
- 조건 (비교 연산자, 기준값 등)

## 응답 형식
JSON 객체로 응답. 불확실한 값은 null로 표시.
{ "param_name": value, ... }

USER:
입력: {{ user_input }}
의도: {{ intent_category }}
추출된 엔티티: {{ keywords }}

파라미터를 추출하세요.
```

---

## 6. Phase D: 노드 후보 생성

의도 분류·파라미터를 종합하여, DAG 생성에 사용할 `StepDescription[]` 목록을 생성한다.

### 6.1 노드 타입 추론 규칙

```typescript
// 액션 키워드 → 노드 타입 매핑 (nl_to_dag_conversion.md §5.2 정본 참조)
const ACTION_NODE_MAP: Record<string, NodeType> = {
  // LLMNode
  "요약": "LLMNode", "분류": "LLMNode", "생성": "LLMNode",
  "분석": "LLMNode", "번역": "LLMNode",

  // APINode
  "조회": "APINode", "호출": "APINode", "가져오기": "APINode",
  "검색": "APINode",

  // ConditionNode
  "판단": "ConditionNode", "비교": "ConditionNode", "확인": "HumanApprovalNode",

  // TransformNode
  "변환": "TransformNode", "계산": "TransformNode", "매핑": "TransformNode",
  "정리": "TransformNode", "포맷": "TransformNode",

  // NotificationNode
  "알림": "NotificationNode", "전송": "NotificationNode", "보내기": "NotificationNode",

  // LoopNode
  "반복": "LoopNode", "각각": "LoopNode",

  // HumanApprovalNode
  "승인": "HumanApprovalNode", "검토": "HumanApprovalNode",

  // ParallelNode
  "동시에": "ParallelNode", "병렬": "ParallelNode",

  // SubworkflowNode
  "워크플로우 호출": "SubworkflowNode", "서브": "SubworkflowNode",

  // ErrorHandlerNode
  "에러": "ErrorHandlerNode", "실패 시": "ErrorHandlerNode", "재시도": "ErrorHandlerNode",

  // DelayNode
  "대기": "DelayNode", "기다려": "DelayNode", "후에": "DelayNode",

  // CodeNode
  "코드": "CodeNode", "스크립트": "CodeNode", "실행": "CodeNode",
};
```

### 6.2 노드 후보 생성 알고리즘

```
function generate_step_candidates(
    user_input: string,
    classification: IntentClassification,
    keywords: KeywordResult,
    parameters: Record<string, any>
) -> StepDescription[]:

    // Step 1: LLM에게 단계 분해 요청
    steps_raw = call_llm(
        model="claude-haiku-4-5",
        prompt=STEP_DECOMPOSITION_PROMPT.format(
            user_input=user_input,
            intent_category=classification.category,
            parameters=parameters
        ),
        response_format="json",
        temperature=0.2
    )
    // 결과 예시:
    // [
    //   { "order": 1, "action": "관심 종목 시세 조회", "parameters": { "source": "yfinance" } },
    //   { "order": 2, "action": "전일 대비 변동률 계산", "parameters": { "formula": "..." } },
    //   { "order": 3, "action": "변동률 3% 이상 판단", "parameters": { "threshold": 3 } },
    //   { "order": 4, "action": "알림 발송", "parameters": { "channel": "push" } }
    // ]

    // Step 2: 각 단계에 노드 타입 추론 (규칙 기반)
    steps = []
    for step_raw in steps_raw:
        inferred_type = infer_node_type(step_raw.action)
        steps.append(StepDescription(
            order=step_raw.order,
            action=step_raw.action,
            inferred_node_type=inferred_type,
            parameters=step_raw.parameters
        ))

    // Step 3: 조건 분기 노드 뒤에 분기 경로 확인
    for i, step in enumerate(steps):
        if step.inferred_node_type == "ConditionNode":
            // 뒤에 최소 1개 노드가 있어야 true/false 분기 가능
            if i == len(steps) - 1:
                # ConditionNode는 true_target/false_target 양쪽이 필요 → 두 분기 후속 노드 모두 추가
                steps.append(StepDescription(
                    order=step.order + 1,
                    action="조건 충족 시 종료(true 분기)",
                    inferred_node_type="DelayNode",
                    parameters={"delay_seconds": 0, "branch": "true"}
                ))
                steps.append(StepDescription(
                    order=step.order + 2,
                    action="조건 불충족 시 종료(false 분기)",
                    inferred_node_type="DelayNode",
                    parameters={"delay_seconds": 0, "branch": "false"}
                ))

    return steps


function infer_node_type(action: string) -> NodeType | null:
    // 액션 문자열에서 키워드 매칭으로 노드 타입 추론
    for keyword, node_type in ACTION_NODE_MAP:
        if keyword in action:
            return node_type

    // 매칭 실패 → null (LLM DAG 생성 시 LLM이 결정)
    return null
```

### 6.3 단계 분해 LLM 프롬프트

```
SYSTEM:
워크플로우 단계 분해기입니다.
사용자의 자연어 요청을 실행 가능한 개별 단계로 분해합니다.

## 규칙
- 각 단계는 하나의 명확한 동작을 수행
- 단계 순서는 실행 순서를 반영
- 조건 분기가 있으면 명시 ("~이면", "~아니면")
- 단계 수는 2~15개 범위
- 파라미터는 최대한 구체적으로

## 응답 형식
JSON 배열: [{ "order": N, "action": "동작 설명", "parameters": { ... } }, ...]

USER:
입력: {{ user_input }}
의도: {{ intent_category }}
추출 파라미터: {{ parameters }}

위 요청을 워크플로우 단계로 분해하세요.
```

---

## 7. 통합 파싱 엔트리포인트

### 7.1 전체 파이프라인 실행

```
function parse_intent(user_input: string, context?: ConversationContext) -> WorkflowIntent:
    // Phase A: 키워드 추출
    keywords = extract_keywords(user_input)

    // Phase B: 의도 분류
    classification = classify_intent(keywords)

    // 대화 컨텍스트 보정 (수정 요청인 경우)
    if context and context.conversation_history:
        classification = adjust_for_context(classification, context)

    // Phase C: 파라미터 추출
    trigger_hint = extract_trigger_hint(classification, keywords)
    parameters = extract_parameters(user_input, classification, keywords)

    // Phase D: 노드 후보 생성
    steps = generate_step_candidates(user_input, classification, keywords, parameters)

    return WorkflowIntent(
        intent_category=classification.category,
        confidence=classification.confidence,
        trigger_hint=trigger_hint,
        steps=steps,
        parameters=parameters,
        raw_input=user_input
    )
```

### 7.2 대화 컨텍스트 보정

수정 요청("알림을 이메일로도 보내줘")의 경우, 이전 대화를 참조하여 의도를 보정한다.

```
function adjust_for_context(
    classification: IntentClassification,
    context: ConversationContext
) -> IntentClassification:
    // 수정 키워드 감지
    modification_keywords = ["추가", "변경", "삭제", "수정", "바꿔", "도", "대신"]
    user_input = context.conversation_history[-1].content if context.conversation_history else ""
    is_modification = any(kw in user_input for kw in modification_keywords)

    if is_modification and context.last_workflow:
        // 기존 워크플로우의 의도 카테고리 유지
        classification.category = context.last_workflow.intent_category
        classification.is_modification = true

    return classification
```

---

## 8. 에러 처리 및 명확화

### 8.1 파싱 실패 분류

| 실패 유형 | 조건 | 대응 |
|-----------|------|------|
| 의도 불명확 | confidence < 0.6 | 명확화 질문 생성 |
| 빈 단계 | steps = [] | "어떤 작업을 자동화하고 싶으신가요?" |
| 파라미터 부족 | 필수 파라미터 null | 구체적 파라미터 질문 |
| 복합 의도 | 2개 이상 카테고리 동점 | 우선순위 질문 |

### 8.2 명확화 질문 생성

```
function generate_clarification(intent: WorkflowIntent) -> string:
    if intent.confidence < 0.4:
        return "어떤 종류의 자동화를 원하시나요? (예: 정기 반복 작업, 이벤트 반응, 데이터 수집)"

    if not intent.steps:
        return "어떤 단계들을 자동화하고 싶으신가요? 구체적인 동작을 알려주세요."

    missing_params = find_missing_required_params(intent)
    if missing_params:
        return f"다음 정보가 필요합니다: {', '.join(missing_params)}"

    if not intent.trigger_hint:
        return "이 워크플로우를 어떻게 실행하고 싶으신가요? (예: 매일 특정 시간, 이벤트 발생 시, 수동 실행)"

    return "요청을 좀 더 구체적으로 설명해 주시겠어요?"
```

---

## 9. 성능 목표

| 메트릭 | 목표 | 측정 방법 |
|--------|------|----------|
| 의도 분류 정확률 | ≥ 85% | 테스트 셋 100건 기준 정답 매칭 |
| 파라미터 추출 완전성 | ≥ 80% | 필수 파라미터 추출 비율 |
| 노드 타입 추론 정확률 | ≥ 75% | 추론 노드 타입 vs 정답 노드 타입 |
| 파싱 지연 시간 | ≤ 3초 | 규칙 기반 ≤ 100ms, LLM 보조 ≤ 3초 |
| 명확화 질문 적절성 | ≥ 80% | 사용자가 질문 후 성공적으로 재파싱된 비율 |
