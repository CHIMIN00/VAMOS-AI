# 자연어 → 워크플로우 DAG 변환 — L3 상세 명세

> **N-ID**: N-002 (EXTEND)
> **V단계**: V1
> **도메인**: 3-4_Workflow-RPA / 02_nl-to-workflow
> **정본**: sot 2/3-4_Workflow-RPA/02_nl-to-workflow/nl_to_dag_conversion.md
> **교차참조**: intent_parsing.md (의도 파싱 엔진), dag_architecture.md (DAG 스키마/노드 타입)

---

## 1. 개요

자연어 명령을 DAG 워크플로우 정의로 변환하는 end-to-end 파이프라인이다. 사용자가 대화형으로 "매일 아침 9시에 관심 종목 시세 확인하고 변동 3% 이상이면 알려줘" 같은 자연어를 입력하면, LLM 기반 의도 파싱 → 노드 타입 매핑 → DAG 자동 생성 → 순환 검증 → 사용자 확인을 거쳐 실행 가능한 워크플로우 JSON을 생성한다.

> LOCK (기존 명세 §2 / STEP7-N N-001 / LOCK-WF-01): LLMNode, APINode, ConditionNode, ParallelNode, HumanApprovalNode, TransformNode, NotificationNode, LoopNode, SubworkflowNode, ErrorHandlerNode, DelayNode, CodeNode — 12 타입은 제거 불가. 추가만 허용.

> LOCK (기존 명세 §3 / LOCK-WF-04): 유향 비순환 그래프(DAG) 필수, 순환 감지 시 워크플로우 등록 거부

> LOCK (가이드 R-07-1 / LOCK-WF-02): 워크플로우 최대 노드 수 = 50개

**KPI**: NL→DAG 변환 성공률 ≥ 70% (의도 파싱 정확 + DAG 검증 PASS + 사용자 수정 없이 확인)

---

## 2. 변환 파이프라인 아키텍처

```
[자연어 입력]
    │
    ▼
[Stage 1: 의도 파싱] ─── intent_parsing.md 참조
    │  intent_category, trigger_hint, step_descriptions[], parameters{}
    ▼
[Stage 2: 템플릿 매칭]
    │  similarity ≥ 0.85 → 템플릿 인스턴스화 (fast path)
    │  similarity < 0.85 → Stage 3 (LLM DAG 생성)
    ▼
[Stage 3: LLM DAG 생성]
    │  프롬프트 + 노드 타입 카탈로그 → structured JSON
    ▼
[Stage 4: DAG 검증]
    │  순환 검증 (LOCK-WF-04) + 노드 타입 유효성 + 엣지 정합
    ▼
[Stage 5: 사용자 확인] ─── R-07-7: 자동 실행 금지
    │  미리보기 렌더링 → 승인/수정/취소
    ▼
[워크플로우 등록]
```

---

## 3. Stage 1: 의도 파싱

> 참조: `intent_parsing.md` — 의도 파싱 파이프라인 L3 상세

의도 파싱 엔진이 자연어 입력을 구조화된 `WorkflowIntent` 객체로 변환한다. 본 파일에서는 파싱 결과의 **소비(consumption)** 관점만 기술하고, 파싱 로직 상세는 `intent_parsing.md`에 위임한다.

### 3.1 의도 파싱 결과 스키마

```typescript
interface WorkflowIntent {
  intent_category: IntentCategory;         // 의도 분류
  confidence: number;                      // 0.0 ~ 1.0
  trigger_hint?: TriggerHint;              // 트리거 힌트 (시간/이벤트/조건 등)
  steps: StepDescription[];                // 추출된 단계 목록
  parameters: Record<string, any>;         // 추출된 파라미터
  raw_input: string;                       // 원본 자연어
}

type IntentCategory =
  | "scheduled_task"      // 시간 기반 반복 ("매일", "매주")
  | "event_triggered"     // 이벤트 기반 ("~하면", "~될 때")
  | "data_pipeline"       // 데이터 수집/처리 ("크롤링", "수집")
  | "notification"        // 알림/리포트 ("알려줘", "보내줘")
  | "automation"          // 범용 자동화 ("자동으로")
  | "approval_flow";      // 승인/결재 ("승인", "검토")

interface TriggerHint {
  type: "time" | "event" | "condition" | "webhook" | "manual" | "conversation" | "ambient";
                                           // LOCK-WF-06 7유형 전수
  cron?: string;                           // time일 때 cron 표현식
  event_source?: string;                   // event일 때 소스
  condition_expr?: string;                 // condition일 때 표현식
  webhook_path?: string;                   // webhook일 때 엔드포인트
  conversation_keyword?: string;           // conversation일 때 감지 키워드
  ambient_context?: string;                // ambient일 때 컨텍스트 조건
}

interface StepDescription {
  order: number;                           // 단계 순서
  action: string;                          // 동작 요약 ("시세 조회", "변동률 계산")
  inferred_node_type?: NodeType;           // 추론된 노드 타입 (optional)
  parameters: Record<string, any>;         // 단계별 파라미터
}
```

---

## 4. Stage 2: 템플릿 매칭

의도 파싱 결과를 기존 템플릿 라이브러리와 대조하여, 유사도가 높으면 템플릿을 인스턴스화하는 fast path를 제공한다.

### 4.1 매칭 알고리즘

```
function match_template(intent: WorkflowIntent) -> TemplateMatch | null:
    candidates = template_library.search(
        category=intent.intent_category,
        keywords=extract_keywords(intent.steps)
    )

    best_match = null
    best_score = 0.0

    for template in candidates:
        score = compute_similarity(intent, template)
        // 의도 카테고리 일치(0.3) + 단계 구조 유사도(0.4) + 파라미터 커버리지(0.3)
        if score > best_score:
            best_score = score
            best_match = template

    if best_score >= 0.85:
        return TemplateMatch(template=best_match, score=best_score)
    return null  // Stage 3으로 진행


function instantiate_template(match: TemplateMatch, intent: WorkflowIntent) -> WorkflowDefinition:
    workflow = deep_copy(match.template.workflow_definition)
    // 파라미터 바인딩: 의도 파싱에서 추출한 값으로 템플릿 변수 채우기
    for param_key, param_value in intent.parameters:
        workflow.variables[param_key].default = param_value
    // 트리거 설정
    if intent.trigger_hint:
        workflow.trigger = build_trigger(intent.trigger_hint)
    return workflow
```

### 4.2 유사도 계산 가중치

| 요소 | 가중치 | 설명 |
|------|--------|------|
| 의도 카테고리 일치 | 0.30 | intent_category == template.category |
| 단계 구조 유사도 | 0.40 | 단계 수·순서·액션 타입 LCS 기반 비교 |
| 파라미터 커버리지 | 0.30 | 템플릿 필수 파라미터 중 의도에서 추출된 비율 |

---

## 5. Stage 3: LLM DAG 생성

템플릿 매칭 실패 시 LLM을 사용하여 DAG를 직접 생성한다.

### 5.1 LLM 프롬프트 템플릿

```
SYSTEM:
당신은 VAMOS 워크플로우 DAG 생성기입니다.
사용자의 자연어 요청을 JSON 형식의 워크플로우 DAG로 변환합니다.

## 사용 가능한 노드 타입 (LOCK-WF-01)
| 타입 | 용도 | 주요 설정 |
|------|------|----------|
| LLMNode | LLM 텍스트 처리 (요약, 분류, 생성) | model, prompt, temperature |
| APINode | 외부 REST/GraphQL API 호출 | url, method, headers, body |
| ConditionNode | 조건 분기 (if/else) | expression, true_target, false_target |
| ParallelNode | 병렬 실행 (fork/join) | branches[], join_strategy |
| HumanApprovalNode | 사용자 승인 대기 | prompt, timeout=600 |
| TransformNode | 데이터 변환/매핑/필터 | transform_expression (Jinja2/JSONPath) |
| NotificationNode | 알림 전송 (이메일/Slack/푸시) | channel, template, recipients |
| LoopNode | 반복 처리 (for-each/while) | collection_path, max_iterations=1000 |
| SubworkflowNode | 다른 워크플로우 호출 | workflow_id, max_depth=5 |
| ErrorHandlerNode | 에러 처리 (catch/retry) | catch_types[], retry_policy |
| DelayNode | 지연/대기 | delay_seconds, max=86400 |
| CodeNode | Python/JS 코드 실행 | language, code, sandbox=true |

## 제약 조건
- 최대 노드 수: 50개 (LOCK-WF-02)
- DAG(비순환) 필수 — 순환(cycle) 절대 금지 (LOCK-WF-04)
- entry_node는 반드시 1개
- 모든 노드는 entry_node에서 도달 가능해야 함
- 미연결 엣지 금지

## 출력 형식
아래 JSON 스키마를 정확히 준수하세요:
{
  "name": "워크플로우 이름",
  "description": "설명",
  "nodes": [
    {
      "id": "node_1",
      "type": "NodeType",
      "name": "표시명",
      "config": { ... }
    }
  ],
  "edges": [
    { "source": "node_1", "target": "node_2" }
  ],
  "entry_node": "node_1",
  "end_nodes": ["node_N"],
  "trigger": { "type": "time|event|condition|webhook|manual|conversation|ambient", ... }
}

USER:
## 의도 파싱 결과
- 카테고리: {{ intent.intent_category }}
- 트리거: {{ intent.trigger_hint | tojson }}
- 단계: {{ intent.steps | tojson }}
- 파라미터: {{ intent.parameters | tojson }}

## 원본 요청
{{ intent.raw_input }}

위 정보를 바탕으로 워크플로우 DAG JSON을 생성하세요.
```

### 5.2 노드 타입 매핑 규칙

의도 파싱의 `StepDescription.action` 키워드를 노드 타입에 매핑하는 규칙 테이블. LLM 프롬프트 내 few-shot 예제와 병행하여, LLM이 올바른 노드 타입을 선택하도록 가이드한다.

| 액션 키워드 패턴 | 매핑 노드 타입 | 예시 |
|-----------------|---------------|------|
| 요약, 분류, 생성, 분석, 번역, 추출(텍스트) | LLMNode | "뉴스 요약" → LLMNode |
| 조회, 호출, 가져오기, API, 시세, 날씨 | APINode | "시세 조회" → APINode |
| ~이면, ~보다, 비교, 판단, 필터 | ConditionNode | "변동률 > 3%이면" → ConditionNode |
| 동시에, 병렬로, 각각 | ParallelNode | "3개 API 동시 호출" → ParallelNode |
| 승인, 확인, 검토, 결재 | HumanApprovalNode | "팀장 승인 대기" → HumanApprovalNode |
| 변환, 매핑, 포맷, 계산, 정리 | TransformNode | "변동률 계산" → TransformNode |
| 알림, 알려줘, 보내줘, 이메일, 슬랙 | NotificationNode | "슬랙으로 알려줘" → NotificationNode |
| 반복, 각각, 모든, 리스트별 | LoopNode | "모든 종목에 대해" → LoopNode |
| 워크플로우 호출, 서브 | SubworkflowNode | "보고서 워크플로우 호출" → SubworkflowNode |
| 에러, 실패 시, 재시도 | ErrorHandlerNode | "실패 시 3회 재시도" → ErrorHandlerNode |
| 대기, 기다려, ~후에 | DelayNode | "5분 대기 후" → DelayNode |
| 코드, 스크립트, 실행, 계산(복잡) | CodeNode | "Python으로 계산" → CodeNode |

### 5.3 DAG 자동 생성 알고리즘 의사코드

```
function generate_dag(intent: WorkflowIntent) -> WorkflowDefinition:
    // Step 1: 템플릿 매칭 시도 (fast path)
    template_match = match_template(intent)
    if template_match:
        return instantiate_template(template_match, intent)

    // Step 2: LLM 기반 생성
    prompt = render_dag_generation_prompt(intent)
    llm_response = call_llm(
        model="claude-sonnet-4-6",
        prompt=prompt,
        response_format="json",
        temperature=0.2,           // 구조화 출력 → 낮은 temperature
        max_tokens=4096
    )

    // Step 3: JSON 파싱 + 스키마 검증
    raw_dag = parse_json(llm_response)
    schema_errors = validate_schema(raw_dag, WorkflowDefinitionSchema)
    if schema_errors:
        // 1회 자동 수정 시도
        fix_prompt = build_fix_prompt(raw_dag, schema_errors)
        raw_dag = call_llm(model="claude-sonnet-4-6", prompt=fix_prompt, response_format="json")
        schema_errors = validate_schema(raw_dag, WorkflowDefinitionSchema)
        if schema_errors:
            return GenerationError(reason="schema_validation_failed", details=schema_errors)

    // Step 4: DAG 검증 (§6 참조)
    validation = validate_dag(raw_dag)
    if not validation.valid:
        return GenerationError(reason="dag_validation_failed", details=validation.errors)

    // Step 5: 워크플로우 정의 객체 생성
    workflow = build_workflow_definition(raw_dag, intent)
    workflow.metadata.source = "nl_generated"
    workflow.metadata.generation_model = "claude-sonnet-4-6"
    workflow.metadata.intent_confidence = intent.confidence

    return workflow
```

### 5.4 생성 예시

**입력**: "매일 아침 9시에 관심 종목 시세 확인하고 변동이 3% 이상이면 알려줘"

**의도 파싱 결과**:
```json
{
  "intent_category": "scheduled_task",
  "confidence": 0.92,
  "trigger_hint": { "type": "time", "cron": "0 9 * * *" },
  "steps": [
    { "order": 1, "action": "관심 종목 시세 조회", "inferred_node_type": "APINode" },
    { "order": 2, "action": "전일 대비 변동률 계산", "inferred_node_type": "TransformNode" },
    { "order": 3, "action": "변동률 3% 이상 판단", "inferred_node_type": "ConditionNode" },
    { "order": 4, "action": "알림 발송", "inferred_node_type": "NotificationNode" }
  ],
  "parameters": { "threshold": 3, "unit": "percent", "assets": "관심 종목" }
}
```

**생성 DAG**:
```json
{
  "name": "관심 종목 시세 모니터링",
  "description": "매일 09:00 관심 종목 시세를 확인하고 3% 이상 변동 시 알림",
  "nodes": [
    {
      "id": "node_1",
      "type": "APINode",
      "name": "관심 종목 시세 조회",
      "config": {
        "url": "{{ secrets.stock_api_url }}/quotes",
        "method": "GET",
        "query_params": { "symbols": "{{ variables.watchlist }}" },
        "auth": { "type": "api_key", "credential_ref": "stock_api_key" },
        "response_path": "$.data[*]"
      }
    },
    {
      "id": "node_2",
      "type": "TransformNode",
      "name": "전일 대비 변동률 계산",
      "config": {
        "transform_expression": "{{ (item.current_price - item.prev_close) / item.prev_close * 100 | round(2) }}",
        "input_path": "$.node_1.body",
        "output_key": "change_rates"
      }
    },
    {
      "id": "node_3",
      "type": "ConditionNode",
      "name": "변동률 3% 이상 판단",
      "config": {
        "expression": "{{ node_2.change_rates | selectattr('rate', 'gt', 3) | list | length > 0 }}",
        "true_target": "node_4",
        "false_target": "node_end"
      }
    },
    {
      "id": "node_4",
      "type": "NotificationNode",
      "name": "알림 발송",
      "config": {
        "channel": "push",
        "template": "{{ item.symbol }}: {{ item.rate }}% 변동 ({{ item.current_price }}원)",
        "recipients": ["{{ variables.user_id }}"]
      }
    },
    {
      "id": "node_end",
      "type": "DelayNode",
      "name": "종료",
      "config": { "delay_seconds": 0 }
    }
  ],
  "edges": [
    { "source": "node_1", "target": "node_2" },
    { "source": "node_2", "target": "node_3" },
    { "source": "node_3", "target": "node_4" },
    { "source": "node_3", "target": "node_end" },
    { "source": "node_4", "target": "node_end" }
  ],
  "entry_node": "node_1",
  "end_nodes": ["node_end"],
  "trigger": { "type": "time", "cron": "0 9 * * *", "timezone": "Asia/Seoul" }
}
```

---

## 6. Stage 4: DAG 검증 (LOCK-WF-04 통합)

생성된 DAG를 등록 전에 8개 규칙으로 검증한다. 순환 검증(LOCK-WF-04)은 **필수 PASS** 항목이며, 실패 시 즉시 등록 거부된다.

### 6.1 검증 규칙 목록

| # | 규칙 | 심각도 | LOCK | 설명 |
|---|------|--------|------|------|
| V-1 | no_cycles | ERROR | LOCK-WF-04 | DAG 순환 금지 — 토폴로지 정렬 불가 시 실패 |
| V-2 | single_entry | ERROR | — | entry_node 정확히 1개 |
| V-3 | all_nodes_reachable | ERROR | — | entry_node에서 모든 노드 도달 가능 |
| V-4 | no_dangling_edges | ERROR | — | 엣지의 source/target이 모두 존재하는 노드 |
| V-5 | valid_node_types | ERROR | LOCK-WF-01 | 12 타입 + 추가 허용 타입만 사용 |
| V-6 | max_nodes_limit | ERROR | LOCK-WF-02 | 노드 수 ≤ 50 |
| V-7 | required_configs | WARNING | — | 각 노드 타입의 필수 config 키 존재 |
| V-8 | compatible_io | WARNING | — | 엣지로 연결된 노드 간 입출력 타입 호환 |

### 6.2 순환 검증 알고리즘 (LOCK-WF-04)

Kahn 알고리즘 기반 토폴로지 정렬로 순환을 검출한다.

```
function detect_cycle(nodes: Node[], edges: Edge[]) -> CycleCheckResult:
    // Kahn's Algorithm — 토폴로지 정렬 기반 순환 검출
    in_degree = {}
    adjacency = {}

    for node in nodes:
        in_degree[node.id] = 0
        adjacency[node.id] = []

    for edge in edges:
        adjacency[edge.source].append(edge.target)
        in_degree[edge.target] += 1

    // 진입 차수 0인 노드로 큐 초기화
    queue = [node_id for node_id in in_degree if in_degree[node_id] == 0]
    sorted_order = []

    while queue is not empty:
        current = queue.pop_front()
        sorted_order.append(current)

        for neighbor in adjacency[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(sorted_order) != len(nodes):
        // 순환 발견 — 토폴로지 정렬에 포함되지 않은 노드가 순환 참여
        cycle_nodes = [n.id for n in nodes if n.id not in sorted_order]
        cycle_path = trace_cycle_path(adjacency, cycle_nodes)
        return CycleCheckResult(
            has_cycle=true,
            cycle_path=cycle_path,
            message=f"순환 감지: {' → '.join(cycle_path)}. DAG 등록 거부 (LOCK-WF-04)"
        )

    return CycleCheckResult(has_cycle=false, topological_order=sorted_order)


function trace_cycle_path(adjacency, cycle_nodes) -> list[string]:
    // DFS로 순환 경로 추적 (사용자에게 표시용)
    visited = set()
    path = []
    start = cycle_nodes[0]

    function dfs(node):
        if node in visited:
            // 순환 시작점 찾음 — 경로 반환
            cycle_start = path.index(node)
            return path[cycle_start:] + [node]
        visited.add(node)
        path.append(node)
        for neighbor in adjacency[node]:
            if neighbor in cycle_nodes:
                result = dfs(neighbor)
                if result:
                    return result
        path.pop()
        return null

    return dfs(start)
```

### 6.3 통합 검증 실행

```
function validate_dag(dag: RawDAG) -> ValidationResult:
    errors = []
    warnings = []

    // V-1: 순환 검증 (LOCK-WF-04, MUST PASS)
    cycle_check = detect_cycle(dag.nodes, dag.edges)
    if cycle_check.has_cycle:
        errors.append(ValidationError(
            rule="no_cycles",
            severity="ERROR",
            message=cycle_check.message,
            lock="LOCK-WF-04"
        ))
        // 순환 발견 시 즉시 반환 (이후 검증 무의미)
        return ValidationResult(valid=false, errors=errors, warnings=[])

    // V-2: 단일 진입점
    if not dag.entry_node or dag.entry_node not in [n.id for n in dag.nodes]:
        errors.append(ValidationError(rule="single_entry", severity="ERROR", ...))

    // V-3: 모든 노드 도달 가능 (BFS)
    reachable = bfs(dag.entry_node, dag.edges)
    unreachable = [n.id for n in dag.nodes if n.id not in reachable]
    if unreachable:
        errors.append(ValidationError(rule="all_nodes_reachable", severity="ERROR",
            message=f"도달 불가 노드: {unreachable}"))

    // V-4: 미연결 엣지
    node_ids = set(n.id for n in dag.nodes)
    for edge in dag.edges:
        if edge.source not in node_ids or edge.target not in node_ids:
            errors.append(ValidationError(rule="no_dangling_edges", severity="ERROR", ...))

    // V-5: 유효 노드 타입 (LOCK-WF-01)
    valid_types = LOCK_WF_01_TYPES + get_extension_types()
    for node in dag.nodes:
        if node.type not in valid_types:
            errors.append(ValidationError(rule="valid_node_types", severity="ERROR",
                message=f"미지원 노드 타입: {node.type}", lock="LOCK-WF-01"))

    // V-6: 최대 노드 수 (LOCK-WF-02)
    if len(dag.nodes) > 50:
        errors.append(ValidationError(rule="max_nodes_limit", severity="ERROR",
            message=f"노드 {len(dag.nodes)}개 > 최대 50개", lock="LOCK-WF-02"))

    // V-7: 필수 config 키
    for node in dag.nodes:
        missing = check_required_configs(node.type, node.config)
        if missing:
            warnings.append(ValidationWarning(rule="required_configs",
                message=f"{node.id}: 누락 config {missing}"))

    // V-8: 입출력 호환성
    for edge in dag.edges:
        source_node = find_node(dag.nodes, edge.source)
        target_node = find_node(dag.nodes, edge.target)
        if not check_io_compatible(source_node, target_node):
            warnings.append(ValidationWarning(rule="compatible_io",
                message=f"{edge.source} → {edge.target}: 입출력 타입 불일치 가능"))

    return ValidationResult(
        valid=(len(errors) == 0),
        errors=errors,
        warnings=warnings,
        topological_order=cycle_check.topological_order
    )
```

---

## 7. Stage 5: 사용자 확인

> LOCK (R-07-7): 자연어 → DAG 변환 시 사용자 확인 필수 (자동 실행 금지)

### 7.1 미리보기 인터페이스

```typescript
interface DAGPreview {
  workflow_name: string;
  description: string;
  node_summary: NodeSummary[];           // 노드 목록 요약
  edge_summary: string;                  // "node_1 → node_2 → ..."
  trigger_description: string;           // "매일 09:00 (Asia/Seoul)"
  estimated_duration?: string;           // 예상 실행 시간
  warnings: string[];                    // 검증 경고
  actions: ("approve" | "edit" | "cancel")[];
}

interface NodeSummary {
  id: string;
  type: NodeType;
  name: string;
  description: string;                   // 사용자 친화적 설명
}
```

### 7.2 사용자 확인 흐름

```
function present_preview(workflow: WorkflowDefinition, intent: WorkflowIntent) -> UserDecision:
    preview = build_preview(workflow)

    // 텍스트 기반 미리보기 렌더링
    display_to_user(f"""
        📋 워크플로우: {preview.workflow_name}
        📝 {preview.description}

        🔄 흐름:
        {render_flow_text(preview.node_summary, preview.edge_summary)}

        ⏰ 트리거: {preview.trigger_description}
        ⚠️ 경고: {preview.warnings or '없음'}

        [승인] [수정] [취소]
    """)

    decision = await_user_input()

    if decision == "approve":
        return UserDecision(action="register", workflow=workflow)
    elif decision == "edit":
        // 대화형 수정 루프
        modifications = collect_modifications()
        updated_workflow = apply_modifications(workflow, modifications)
        // 수정 후 재검증
        validation = validate_dag(updated_workflow)
        if not validation.valid:
            // 검증 실패: 오류를 사용자에게 노출 (무한 재귀 금지)
            return UserDecision(action="edit_failed", errors=validation.errors)
        // 검증 통과: 깊이 제한 하에 미리보기 재표시
        if edit_depth >= MAX_EDIT_DEPTH:
            return UserDecision(action="edit_aborted", reason="최대 수정 횟수 초과")
        return present_preview(updated_workflow, intent, edit_depth + 1)
    else:
        return UserDecision(action="cancel")
```

### 7.3 대화형 수정

```
function apply_nl_modification(workflow: WorkflowDefinition, user_input: string) -> WorkflowDefinition:
    // 예: "알림을 이메일로도 보내줘" → NotificationNode 추가
    modification_intent = parse_modification_intent(user_input, workflow)

    match modification_intent.type:
        case "add_node":
            new_node = generate_node(modification_intent)
            workflow.nodes.append(new_node)
            // 엣지 자동 연결 (선행/후행 노드 추론)
            auto_edges = infer_edges(new_node, workflow)
            workflow.edges.extend(auto_edges)

        case "remove_node":
            target_id = modification_intent.target_node
            workflow.nodes = [n for n in workflow.nodes if n.id != target_id]
            // 엣지 재연결 (선행 → 후행 직접 연결)
            reconnect_edges(workflow, target_id)

        case "modify_node":
            target = find_node(workflow.nodes, modification_intent.target_node)
            target.config.update(modification_intent.config_changes)

        case "change_trigger":
            workflow.trigger = build_trigger(modification_intent.trigger_hint)

    // 수정 후 재검증 필수
    validation = validate_dag(workflow)
    if not validation.valid:
        raise ModificationError(details=validation.errors)

    return workflow
```

---

## 8. 성공률 측정 (KPI ≥ 70%)

### 8.1 성공 정의

NL→DAG 변환 **성공** = 아래 3 조건 모두 충족:
1. 의도 파싱 완료 (confidence ≥ 0.6)
2. DAG 검증 PASS (8 규칙 중 ERROR 0건)
3. 사용자가 수정 없이 승인 (approve without edit)

### 8.2 측정 메트릭

| 메트릭 | 공식 | 기준 |
|--------|------|------|
| 파싱 정확률 | 파싱 성공 / 전체 요청 | ≥ 90% |
| DAG 검증 통과율 | 검증 PASS / 파싱 성공 | ≥ 92% |
| 사용자 무수정 승인율 | 무수정 승인 / 검증 PASS | ≥ 85% |
| **종합 성공률** | 파싱 × 검증 × 승인 | **≥ 70%** (0.90 × 0.92 × 0.85 ≈ 0.704 ≥ 0.70, 개별 목표 상향 반영 완료) |

### 8.3 실패 유형별 대응

| 실패 유형 | 원인 | 대응 |
|-----------|------|------|
| 의도 파싱 실패 | 모호한 자연어, 미지원 도메인 | 명확화 질문 생성 → 재파싱 |
| 스키마 검증 실패 | LLM 출력 JSON 구조 오류 | 1회 자동 수정 프롬프트 → 재생성 |
| 순환 검출 (LOCK-WF-04) | LLM이 순환 엣지 생성 | 순환 경로 표시 + 엣지 제거 제안 |
| 노드 수 초과 (LOCK-WF-02) | 복잡한 요청 → 50+ 노드 | SubworkflowNode로 분할 제안 |
| 사용자 수정 | 의도 해석 부정확 | 수정 내용 학습 → 유사 요청 정확도 향상 |

---

## 9. 전체 통합 API

### 9.1 NL→DAG 변환 엔트리포인트

```typescript
interface NLToDAGRequest {
  user_input: string;                    // 자연어 입력
  context?: {                            // 선택적 컨텍스트
    conversation_history?: Message[];    // 대화 이력 (수정 맥락)
    user_preferences?: Record<string, any>;  // 사용자 선호 설정
  };
}

interface NLToDAGResponse {
  status: "success" | "needs_clarification" | "error";
  workflow?: WorkflowDefinition;         // 생성된 워크플로우
  preview?: DAGPreview;                  // 미리보기
  clarification_question?: string;       // 명확화 필요 시 질문
  error?: GenerationError;               // 에러 상세
  metrics: {
    intent_confidence: number;
    template_match_score?: number;
    generation_model?: string;
    validation_warnings: string[];
    latency_ms: number;
  };
}
```

### 9.2 실행 흐름 요약

```
function nl_to_dag(request: NLToDAGRequest) -> NLToDAGResponse:
    start = now()

    // Stage 1: 의도 파싱
    intent = parse_intent(request.user_input, request.context)
    if intent.confidence < 0.6:
        question = generate_clarification(intent)
        return NLToDAGResponse(status="needs_clarification", clarification_question=question)

    // Stage 2: 템플릿 매칭
    template_match = match_template(intent)
    if template_match:
        workflow = instantiate_template(template_match, intent)
    else:
        // Stage 3: LLM DAG 생성
        workflow = generate_dag(intent)
        if workflow is GenerationError:
            return NLToDAGResponse(status="error", error=workflow)

    // Stage 4: DAG 검증
    validation = validate_dag(workflow)
    if not validation.valid:
        return NLToDAGResponse(status="error",
            error=GenerationError(reason="validation_failed", details=validation.errors))

    // Stage 5: 미리보기 생성 (사용자 확인은 UI 레이어에서 처리)
    preview = build_preview(workflow)

    return NLToDAGResponse(
        status="success",
        workflow=workflow,
        preview=preview,
        metrics={
            intent_confidence=intent.confidence,
            template_match_score=template_match.score if template_match else null,
            generation_model="claude-sonnet-4-6" if not template_match else null,
            validation_warnings=[w.message for w in validation.warnings],
            latency_ms=elapsed(start)
        }
    )
```
