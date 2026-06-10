# DAG 기반 워크플로우 아키텍처 — L3 상세 명세

> **N-ID**: N-001 (EXTEND)
> **V단계**: V1
> **도메인**: 3-4_Workflow-RPA / 01_dag-engine
> **정본**: sot 2/3-4_Workflow-RPA/01_dag-engine/dag_architecture.md

---

## 1. 개요

VAMOS 워크플로우 엔진은 **LangGraph StateGraph** 기반의 DAG(Directed Acyclic Graph) 실행기이다. 워크플로우를 노드(Node)와 엣지(Edge)로 구성하며, 각 노드는 독립적인 작업 단위를 수행하고 엣지는 데이터 흐름과 조건 분기를 정의한다.

> LOCK (STEP7-N / LOCK-WF-05): LangGraph StateGraph 기반, 최대 동시 실행 수 = 10

---

## 2. 핵심 제약 (LOCK)

> LOCK (기존 명세 §2 / STEP7-N N-001 / LOCK-WF-01): LLMNode, APINode, ConditionNode, ParallelNode, HumanApprovalNode, TransformNode, NotificationNode, LoopNode, SubworkflowNode, ErrorHandlerNode, DelayNode, CodeNode — 12 타입은 제거 불가. 추가만 허용.

> LOCK (가이드 R-07-1 / LOCK-WF-02): 워크플로우 최대 노드 수 = 50개

> LOCK (기존 명세 §3 / LOCK-WF-04): 유향 비순환 그래프(DAG) 필수, 순환 감지 시 워크플로우 등록 거부

---

## 3. DAG 구조 정의

### 3.1 워크플로우 정의 스키마

```typescript
interface WorkflowDefinition {
  id: string;                        // UUID v7
  name: string;                      // 워크플로우 표시명
  description?: string;              // 설명
  version: number;                   // 버전 번호 (auto-increment)
  nodes: WorkflowNode[];             // 노드 목록 (최대 50개)
  edges: WorkflowEdge[];             // 엣지 목록
  entry_node: string;                // 시작 노드 ID
  end_nodes: string[];               // 종료 노드 ID 목록
  variables: Record<string, VariableDef>;  // 워크플로우 변수 정의
  trigger?: TriggerConfig;           // 트리거 설정
  metadata: WorkflowMetadata;        // 메타데이터
}

interface WorkflowEdge {
  id: string;                        // 엣지 ID
  source: string;                    // 출발 노드 ID
  target: string;                    // 도착 노드 ID
  condition?: EdgeCondition;         // 조건부 엣지 (optional)
}

interface EdgeCondition {
  expression: string;                // Jinja2 조건 표현식
  targets: Record<string, string>;   // {조건값: 대상노드ID}
}

interface WorkflowMetadata {
  created_at: string;                // ISO 8601
  updated_at: string;
  owner_id: string;
  tags: string[];
  execution_count: number;
}
```

### 3.2 노드 공통 스키마

```typescript
interface WorkflowNode {
  id: string;                        // UUID v7
  type: NodeType;                    // 12 타입 중 1
  name: string;                      // 사용자 표시명
  config: Record<string, any>;       // 타입별 설정
  inputs: string[];                  // 선행 노드 ID 목록
  outputs: string[];                 // 후속 노드 ID 목록
  retry_policy?: RetryPolicy;        // 재시도 정책
  timeout_seconds?: number;          // 타임아웃 (기본 30초)
  error_handler?: string;            // ErrorHandlerNode ID
  on_error: "fail" | "skip" | "retry" | "fallback";
  fallback_node?: string;            // on_error="fallback"일 때 대체 노드
  metadata?: Record<string, any>;    // 사용자 정의 메타데이터
}

type NodeType =
  | "LLMNode"
  | "APINode"
  | "ConditionNode"
  | "ParallelNode"
  | "HumanApprovalNode"
  | "TransformNode"
  | "NotificationNode"
  | "LoopNode"
  | "SubworkflowNode"
  | "ErrorHandlerNode"
  | "DelayNode"
  | "CodeNode";

interface RetryPolicy {
  max_retries: number;               // 최대 재시도 (기본 3)
  backoff_strategy: "fixed" | "exponential" | "linear";
  initial_delay_ms: number;          // 초기 지연 (기본 1000)
  max_delay_ms: number;              // 최대 지연 (기본 30000)
}
```

---

## 4. 12 노드 타입 상세 정의

### 4.1 LLMNode — LLM 호출

| 항목 | 값 |
|------|-----|
| **설명** | LLM API 호출 (프롬프트 → 응답) |
| **실행 규칙** | 모델 선택, temperature, max_tokens 파라미터. 타임아웃 30초. 실패 시 fallback 모델 |

```typescript
// 입력 스키마
interface LLMNodeInput {
  prompt: string;                    // 프롬프트 텍스트 (Jinja2 템플릿 지원)
  system_prompt?: string;            // 시스템 프롬프트
  context?: Record<string, any>;     // 템플릿 변수
}

// 설정 스키마
interface LLMNodeConfig {
  model: string;                     // "claude-3-sonnet" | "gpt-4o" | ...
  temperature: number;               // 0.0 ~ 2.0, 기본 0.7
  max_tokens: number;                // 기본 4096
  fallback_model?: string;           // 실패 시 대체 모델
  response_format?: "text" | "json"; // 출력 형식
}

// 출력 스키마
interface LLMNodeOutput {
  response: string;                  // LLM 응답 텍스트
  model_used: string;                // 실제 사용 모델
  tokens_used: { input: number; output: number };
  latency_ms: number;
}
```

**실행 로직 의사코드**:
```
function execute_llm_node(node, state):
    prompt = render_template(node.config.prompt, state.variables)
    try:
        response = call_llm(
            model=node.config.model,
            prompt=prompt,
            system=node.config.system_prompt,
            temperature=node.config.temperature,
            max_tokens=node.config.max_tokens,
            timeout=node.timeout_seconds or 30
        )
        return LLMNodeOutput(response=response.text, ...)
    except TimeoutError:
        if node.config.fallback_model:
            return call_llm(model=node.config.fallback_model, ...)
        raise
```

### 4.2 APINode — 외부 API 호출

| 항목 | 값 |
|------|-----|
| **설명** | 외부 REST/GraphQL API 호출 |
| **실행 규칙** | URL, method, headers, body 설정. 재시도 3회, 백오프 1/2/4초 |

```typescript
interface APINodeConfig {
  url: string;                       // URL (Jinja2 템플릿 지원)
  method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  headers?: Record<string, string>;
  body?: Record<string, any> | string;
  query_params?: Record<string, string>;
  auth?: { type: "bearer" | "basic" | "api_key"; credential_ref: string };
  response_path?: string;            // JSONPath로 응답 추출
}

interface APINodeOutput {
  status_code: number;
  headers: Record<string, string>;
  body: any;
  latency_ms: number;
}
```

**실행 로직 의사코드**:
```
function execute_api_node(node, state):
    url = render_template(node.config.url, state.variables)
    headers = resolve_credentials(node.config.auth, node.config.headers)
    body = render_template(node.config.body, state.variables)
    response = http_request(method=node.config.method, url=url, headers=headers, body=body)
    if node.config.response_path:
        extracted = jsonpath_extract(response.body, node.config.response_path)
        return APINodeOutput(body=extracted, ...)
    return APINodeOutput(body=response.body, ...)
```

### 4.3 ConditionNode — 조건 분기

| 항목 | 값 |
|------|-----|
| **설명** | 분기 조건 (if/else) |
| **실행 규칙** | 입력 데이터 기반 boolean 평가. Jinja2 표현식 지원 |

```typescript
interface ConditionNodeConfig {
  expression: string;                // Jinja2 조건: "{{ data.score > 80 }}"
  true_target: string;               // 참일 때 다음 노드 ID
  false_target: string;              // 거짓일 때 다음 노드 ID
}

interface ConditionNodeOutput {
  result: boolean;
  evaluated_expression: string;
  next_node: string;
}
```

**실행 로직 의사코드**:
```
function execute_condition_node(node, state):
    result = evaluate_jinja2(node.config.expression, state.variables)
    next_node = node.config.true_target if result else node.config.false_target
    return ConditionNodeOutput(result=result, next_node=next_node)
```

### 4.4 ParallelNode — 병렬 실행

| 항목 | 값 |
|------|-----|
| **설명** | 병렬 실행 (fork/join) |
| **실행 규칙** | 하위 노드 동시 실행. 전체 완료 대기 또는 any-of-N 완료 |

```typescript
interface ParallelNodeConfig {
  branches: string[];                // 병렬 실행할 노드 ID 목록
  join_strategy: "all" | "any" | "n_of";  // 합류 전략
  min_complete?: number;             // "n_of"일 때 최소 완료 수
  timeout_seconds?: number;          // 전체 병렬 타임아웃
}

interface ParallelNodeOutput {
  results: Record<string, any>;      // {branch_node_id: result}
  completed_count: number;
  failed_branches: string[];
}
```

**실행 로직 의사코드**:
```
function execute_parallel_node(node, state):
    tasks = [launch_async(branch_id, state) for branch_id in node.config.branches]
    if node.config.join_strategy == "all":
        results = await_all(tasks, timeout=node.config.timeout_seconds)
    elif node.config.join_strategy == "any":
        results = await_first(tasks, timeout=node.config.timeout_seconds)
    elif node.config.join_strategy == "n_of":
        results = await_n(tasks, n=node.config.min_complete)
    return ParallelNodeOutput(results=results, ...)
```

### 4.5 HumanApprovalNode — 사용자 승인 대기

| 항목 | 값 |
|------|-----|
| **설명** | 사용자 승인 대기 |
| **실행 규칙** | 알림 전송 → 대기 → 승인/거부. 타임아웃 10분 (LOCK-WF-03) |

```typescript
interface HumanApprovalNodeConfig {
  message: string;                   // 승인 요청 메시지 (Jinja2 지원)
  notification_channels: string[];   // 알림 채널 ["email", "slack", "push"]
  timeout_seconds: number;           // 기본 600 (10분, LOCK-WF-03)
  on_timeout: "reject" | "escalate";   // 'approve' 제거 — 타임아웃 자동승인 금지 (승인 게이트 우회 방지)
  approvers?: string[];              // 승인자 ID (비어있으면 워크플로우 소유자)
}

interface HumanApprovalNodeOutput {
  decision: "approved" | "rejected" | "timeout";
  approver_id?: string;
  comment?: string;
  decided_at: string;
}
```

**실행 로직 의사코드**:
```
function execute_human_approval_node(node, state):
    send_notification(node.config.notification_channels, node.config.message)
    decision = await_human_response(timeout=node.config.timeout_seconds)  # 기본 600초
    if decision is TIMEOUT:
        decision = node.config.on_timeout
    return HumanApprovalNodeOutput(decision=decision, ...)
```

### 4.6 TransformNode — 데이터 변환

| 항목 | 값 |
|------|-----|
| **설명** | 데이터 변환 (매핑/필터/집계) |
| **실행 규칙** | Jinja2/JSONPath 기반 변환. 입출력 스키마 검증 |

```typescript
interface TransformNodeConfig {
  transform_type: "map" | "filter" | "aggregate" | "flatten" | "custom";
  expression: string;                // Jinja2/JSONPath 변환 표현식
  input_schema?: JSONSchema;         // 입력 스키마 (검증용)
  output_schema?: JSONSchema;        // 출력 스키마 (검증용)
}

interface TransformNodeOutput {
  data: any;                         // 변환된 데이터
  record_count?: number;
}
```

**실행 로직 의사코드**:
```
function execute_transform_node(node, state):
    input_data = resolve_inputs(node.inputs, state)
    if node.config.input_schema:
        validate_schema(input_data, node.config.input_schema)
    result = apply_transform(node.config.transform_type, node.config.expression, input_data)
    if node.config.output_schema:
        validate_schema(result, node.config.output_schema)
    return TransformNodeOutput(data=result)
```

### 4.7 NotificationNode — 알림 전송

| 항목 | 값 |
|------|-----|
| **설명** | 알림 전송 (이메일/Slack/푸시) |
| **실행 규칙** | 채널 선택, 템플릿, 수신자 설정 |

```typescript
interface NotificationNodeConfig {
  channel: "email" | "slack" | "telegram" | "push" | "webhook";
  recipients: string[];              // 수신자 목록
  template: string;                  // 메시지 템플릿 (Jinja2)
  subject?: string;                  // 이메일 제목
  priority?: "low" | "normal" | "high" | "urgent";
}

interface NotificationNodeOutput {
  sent_count: number;
  failed_recipients: string[];
  channel: string;
}
```

**실행 로직 의사코드**:
```
function execute_notification_node(node, state):
    message = render_template(node.config.template, state.variables)
    subject = render_template(node.config.subject, state.variables) if subject else None
    results = send_notification(
        channel=node.config.channel,
        recipients=node.config.recipients,
        message=message, subject=subject
    )
    return NotificationNodeOutput(sent_count=len(results.success), ...)
```

### 4.8 LoopNode — 반복 실행

| 항목 | 값 |
|------|-----|
| **설명** | 반복 실행 (for-each / while) |
| **실행 규칙** | 컬렉션 순회 또는 조건 기반 반복. 최대 반복 1000회 |

```typescript
interface LoopNodeConfig {
  loop_type: "for_each" | "while";
  collection?: string;               // for_each: JSONPath로 컬렉션 참조
  condition?: string;                // while: Jinja2 조건
  body_nodes: string[];              // 반복 실행할 노드 ID 목록
  max_iterations: number;            // 기본 1000, 최대 1000
  parallel?: boolean;                // for_each 병렬 실행 여부
}

interface LoopNodeOutput {
  iterations: number;
  results: any[];
  terminated_by: "completion" | "condition_false" | "max_iterations";
}
```

**실행 로직 의사코드**:
```
function execute_loop_node(node, state):
    if node.config.loop_type == "for_each":
        collection = jsonpath_extract(state.variables, node.config.collection)
        for i, item in enumerate(collection):
            if i >= node.config.max_iterations: break
            execute_body(node.config.body_nodes, state, item)
    elif node.config.loop_type == "while":
        count = 0
        while evaluate_jinja2(node.config.condition, state) and count < node.config.max_iterations:
            execute_body(node.config.body_nodes, state)
            count += 1
    return LoopNodeOutput(iterations=count, ...)
```

### 4.9 SubworkflowNode — 다른 워크플로우 호출

| 항목 | 값 |
|------|-----|
| **설명** | 다른 워크플로우 호출 |
| **실행 규칙** | 워크플로우 ID 참조. 재귀 깊이 최대 5 |

```typescript
interface SubworkflowNodeConfig {
  workflow_id: string;               // 호출 대상 워크플로우 ID
  input_mapping: Record<string, string>;  // 부모 변수 → 자식 입력 매핑
  output_mapping: Record<string, string>; // 자식 출력 → 부모 변수 매핑
  max_recursion_depth: number;       // 기본 5, 최대 5
}

interface SubworkflowNodeOutput {
  workflow_id: string;
  execution_id: string;
  status: string;
  outputs: Record<string, any>;
  recursion_depth: number;
}
```

**실행 로직 의사코드**:
```
function execute_subworkflow_node(node, state):
    if state.recursion_depth >= node.config.max_recursion_depth:
        raise MaxRecursionDepthError("재귀 깊이 초과: " + state.recursion_depth)
    child_inputs = map_variables(node.config.input_mapping, state.variables)
    child_state = create_child_state(node.config.workflow_id, child_inputs, depth=state.recursion_depth+1)
    result = execute_workflow(node.config.workflow_id, child_state)
    parent_outputs = map_variables(node.config.output_mapping, result.outputs)
    state.variables.update(parent_outputs)
    return SubworkflowNodeOutput(outputs=parent_outputs, ...)
```

### 4.10 ErrorHandlerNode — 에러 처리

| 항목 | 값 |
|------|-----|
| **설명** | 에러 처리 (catch/retry) |
| **실행 규칙** | try-catch 패턴. 재시도 정책: 횟수, 간격, 백오프 |

```typescript
interface ErrorHandlerNodeConfig {
  target_nodes: string[];            // 감시 대상 노드 ID 목록
  error_types: string[];             // 처리할 에러 타입 ["timeout", "api_error", "validation", "*"]
  action: "retry" | "skip" | "fallback" | "notify" | "pause";
  retry_policy?: RetryPolicy;
  fallback_node?: string;            // action="fallback"일 때
  notification?: NotificationConfig; // action="notify"일 때
}

interface ErrorHandlerNodeOutput {
  handled_error: string;
  action_taken: string;
  retry_count?: number;
  resolved: boolean;
}
```

**실행 로직 의사코드**:
```
function execute_error_handler(node, error, state):
    if error.type not in node.config.error_types and "*" not in node.config.error_types:
        raise error  # 처리 대상이 아닌 에러는 전파
    match node.config.action:
        case "retry":
            return retry_with_policy(node.config.retry_policy, error.source_node, state)
        case "skip":
            return mark_skipped(error.source_node, state)
        case "fallback":
            return execute_node(node.config.fallback_node, state)
        case "notify":
            send_error_notification(node.config.notification, error)
            return ErrorHandlerNodeOutput(resolved=False)
        case "pause":
            return pause_workflow(state, reason=str(error))
```

### 4.11 DelayNode — 지연/대기

| 항목 | 값 |
|------|-----|
| **설명** | 지연/대기 |
| **실행 규칙** | 고정 시간 또는 cron 표현식. 최대 24시간 |

```typescript
interface DelayNodeConfig {
  delay_type: "fixed" | "until" | "cron";
  duration_seconds?: number;         // fixed: 대기 시간 (최대 86400 = 24h)
  until_datetime?: string;           // until: ISO 8601 대기 종료 시각
  cron_expression?: string;          // cron: 다음 실행 시점까지 대기
}

interface DelayNodeOutput {
  waited_seconds: number;
  resumed_at: string;
}
```

**실행 로직 의사코드**:
```
function execute_delay_node(node, state):
    match node.config.delay_type:
        case "fixed":
            if node.config.duration_seconds > 86400:
                raise ValidationError("최대 대기 시간 24시간 초과")
            await sleep(node.config.duration_seconds)
        case "until":
            target = parse_datetime(node.config.until_datetime)
            wait_seconds = (target - now()).total_seconds()
            if wait_seconds > 86400:
                raise ValidationError("최대 대기 시간 24시간 초과")
            if wait_seconds > 0:
                await sleep(wait_seconds)
        case "cron":
            next_run = cron_next(node.config.cron_expression)
            wait_seconds = (next_run - now()).total_seconds()
            await sleep(wait_seconds)
    return DelayNodeOutput(waited_seconds=elapsed, resumed_at=now().isoformat())
```

### 4.12 CodeNode — 사용자 코드 실행

| 항목 | 값 |
|------|-----|
| **설명** | 사용자 정의 Python/JS 코드 실행 |
| **실행 규칙** | 샌드박스 내 실행, 타임아웃 30초, 메모리 256MB 제한 |

```typescript
interface CodeNodeConfig {
  language: "python" | "javascript";
  code: string;                      // 실행할 코드
  sandbox: true;                     // 항상 샌드박스 (강제)
  timeout_seconds: number;           // 기본 30, 최대 60
  memory_limit_mb: number;           // 기본 256, 최대 512
  allowed_imports?: string[];        // 허용 라이브러리 화이트리스트. 미지정/생략 = deny-all(빈 목록 []) — 전체 허용 아님(LOCK-WF-10 샌드박스 탈출 방지)
}

interface CodeNodeOutput {
  result: any;                       // 코드 실행 결과
  stdout: string;
  stderr: string;
  execution_time_ms: number;
}
```

**실행 로직 의사코드**:
```
function execute_code_node(node, state):
    sandbox = create_sandbox(
        language=node.config.language,
        memory_limit=node.config.memory_limit_mb,
        timeout=node.config.timeout_seconds,
        allowed_imports=node.config.allowed_imports
    )
    injected_vars = { "inputs": resolve_inputs(node.inputs, state), "variables": state.variables }
    result = sandbox.execute(node.config.code, injected_vars)
    return CodeNodeOutput(result=result.return_value, stdout=result.stdout, stderr=result.stderr)
```

---

## 5. DAG 검증

### 5.1 순환 검증 알고리즘 (LOCK-WF-04)

> LOCK (기존 명세 §3 / LOCK-WF-04): 유향 비순환 그래프(DAG) 필수, 순환 감지 시 워크플로우 등록 거부

```python
def validate_dag_acyclic(workflow: WorkflowDefinition) -> ValidationResult:
    """
    Topological Sort(Kahn's Algorithm) 기반 DAG 순환 검증.
    순환 감지 시 워크플로우 등록을 거부한다.
    """
    # 인접 리스트 + 진입 차수 구축
    in_degree: dict[str, int] = {n.id: 0 for n in workflow.nodes}
    adjacency: dict[str, list[str]] = {n.id: [] for n in workflow.nodes}

    for edge in workflow.edges:
        adjacency[edge.source].append(edge.target)
        in_degree[edge.target] += 1

    # 진입 차수 0인 노드로 시작
    queue = deque([nid for nid, deg in in_degree.items() if deg == 0])
    sorted_nodes: list[str] = []

    while queue:
        node_id = queue.popleft()
        sorted_nodes.append(node_id)
        for neighbor in adjacency[node_id]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(sorted_nodes) != len(workflow.nodes):
        # 순환 감지 — 등록 거부
        cycle_nodes = [n.id for n in workflow.nodes if n.id not in sorted_nodes]
        return ValidationResult(
            valid=False,
            error=f"DAG 순환 감지: {cycle_nodes}. 워크플로우 등록 거부 (LOCK-WF-04)"
        )

    return ValidationResult(valid=True, topological_order=sorted_nodes)
```

### 5.2 노드 수 제한 검증 (LOCK-WF-02)

> LOCK (가이드 R-07-1 / LOCK-WF-02): 워크플로우 최대 노드 수 = 50개

```python
def validate_node_count(workflow: WorkflowDefinition) -> ValidationResult:
    """최대 50노드 제한 검증. 초과 시 서브워크플로우 분할 권고."""
    MAX_NODES = 50  # LOCK-WF-02
    if len(workflow.nodes) > MAX_NODES:
        return ValidationResult(
            valid=False,
            error=f"노드 수 {len(workflow.nodes)}개 > 최대 {MAX_NODES}개 (LOCK-WF-02). "
                  f"SubworkflowNode를 사용하여 분할하십시오."
        )
    return ValidationResult(valid=True)
```

### 5.3 종합 검증 파이프라인

```python
def validate_workflow(workflow: WorkflowDefinition) -> list[ValidationResult]:
    """워크플로우 등록 전 종합 검증 — 모든 검증을 통과해야 등록 가능."""
    validations = [
        validate_node_count(workflow),          # LOCK-WF-02: 최대 50 노드
        validate_dag_acyclic(workflow),          # LOCK-WF-04: 순환 금지
        validate_node_types(workflow),           # LOCK-WF-01: 12 타입 검증
        validate_entry_exit(workflow),           # 시작/종료 노드 존재 확인
        validate_edge_references(workflow),      # 엣지가 참조하는 노드 존재 확인
        validate_node_connections(workflow),      # 고립 노드 없음 확인
    ]
    return validations
```

---

## 6. LangGraph StateGraph 통합

### 6.1 그래프 빌드

```python
from langgraph.graph import StateGraph, END

class VamosWorkflowEngine:
    """LangGraph StateGraph 기반 DAG 워크플로우 빌드 및 실행 엔진."""

    NODE_EXECUTORS: dict[str, type] = {
        "LLMNode": LLMNodeExecutor,
        "APINode": APINodeExecutor,
        "ConditionNode": ConditionNodeExecutor,
        "ParallelNode": ParallelNodeExecutor,
        "HumanApprovalNode": HumanApprovalNodeExecutor,
        "TransformNode": TransformNodeExecutor,
        "NotificationNode": NotificationNodeExecutor,
        "LoopNode": LoopNodeExecutor,
        "SubworkflowNode": SubworkflowNodeExecutor,
        "ErrorHandlerNode": ErrorHandlerNodeExecutor,
        "DelayNode": DelayNodeExecutor,
        "CodeNode": CodeNodeExecutor,
    }

    def build_graph(self, workflow_def: WorkflowDefinition) -> CompiledGraph:
        """WorkflowDefinition → LangGraph StateGraph 컴파일."""
        # 사전 검증
        results = validate_workflow(workflow_def)
        if any(not r.valid for r in results):
            raise WorkflowValidationError(results)

        graph = StateGraph(WorkflowState)

        # 12 타입 노드 등록
        for node_def in workflow_def.nodes:
            executor = self.NODE_EXECUTORS[node_def.type](node_def)
            graph.add_node(node_def.id, executor.execute)

        # 엣지 등록 (조건부 포함)
        for edge in workflow_def.edges:
            if edge.condition:
                graph.add_conditional_edges(
                    edge.source,
                    self._build_condition_fn(edge.condition),
                    edge.condition.targets
                )
            else:
                graph.add_edge(edge.source, edge.target)

        # 시작/종료 설정
        graph.set_entry_point(workflow_def.entry_node)
        for end_node in workflow_def.end_nodes:
            graph.add_edge(end_node, END)

        return graph.compile()

    def _build_condition_fn(self, condition: EdgeCondition):
        """Jinja2 조건 표현식을 LangGraph 라우팅 함수로 변환."""
        def route(state: WorkflowState) -> str:
            result = evaluate_jinja2(condition.expression, state["variables"])
            return str(result)
        return route
```

### 6.2 WorkflowState 정의

```python
from typing import TypedDict, Any

class WorkflowState(TypedDict):
    """LangGraph State — 워크플로우 실행 중 공유 상태."""
    workflow_id: str
    execution_id: str
    current_node: str
    status: str                      # LOCK-WF-09 상태 머신
    node_results: dict[str, Any]     # {node_id: NodeOutput}
    variables: dict[str, Any]        # 워크플로우 변수
    error_stack: list[dict]          # 에러 스택
    recursion_depth: int             # SubworkflowNode 재귀 깊이
    started_at: str                  # ISO 8601
    elapsed_ms: int
```

---

## 7. 차별화 포인트

| 기존 도구 | VAMOS 차별점 |
|-----------|-------------|
| n8n | 오픈소스 유사성 높으나 VAMOS는 AI-first (자연어 생성 + LLMNode 네이티브) |
| Make.com | 비주얼 에디터 강점이나 VAMOS는 로컬 실행 + 프라이버시 보장 |
| Zapier | 5000+ 앱 연동이나 VAMOS는 커스텀 CodeNode + RPA + 개인화 특화 |

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| L3 v1.0 | 2026-04-09 | Phase 1 1-1 — 12 노드 타입 전수 I/O 스키마 + 의사코드, DAG 검증 알고리즘, LangGraph 통합 |
