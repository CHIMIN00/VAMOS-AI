# 워크플로우 에러 처리 — L3 상세 명세

> **N-ID**: N-007 (EXTEND)
> **V단계**: V1
> **도메인**: 3-4_Workflow-RPA / 01_dag-engine
> **정본**: sot 2/3-4_Workflow-RPA/01_dag-engine/error_handling.md

---

## 1. 개요

워크플로우 실행 중 발생하는 에러를 체계적으로 분류하고, 노드 레벨/워크플로우 레벨의 에러 처리 전략을 정의한다. 재시도 정책, 폴백 전략, 에러 전파 규칙, AI 기반 에러 분석을 포함한다.

---

## 2. 에러 분류 체계

### 2.1 에러 유형

| 에러 유형 | 코드 | 설명 | 기본 정책 |
|-----------|------|------|----------|
| `node_timeout` | E-001 | 노드 실행 타임아웃 (기본 30초) | retry × 2, then skip_with_default |
| `api_error_4xx` | E-002 | 외부 API 클라이언트 에러 (400~499) | fail + notify |
| `api_error_5xx` | E-003 | 외부 API 서버 에러 (500~599) | retry × 3, exponential backoff |
| `llm_rate_limit` | E-004 | LLM API 속도 제한 (429) | retry × 5, exponential, 초기 5초 |
| `llm_token_limit` | E-005 | LLM 토큰 한도 초과 | fail + notify (프롬프트 축소 필요) |
| `browser_element_not_found` | E-006 | Playwright 요소 미발견 | retry × 2, then human_approval |
| `code_execution_error` | E-007 | CodeNode 실행 에러 (문법/런타임) | fail + notify |
| `validation_error` | E-008 | 입출력 스키마 검증 실패 | fail + notify |
| `subworkflow_error` | E-009 | SubworkflowNode 내부 에러 | 자식 에러 전파 |
| `unhandled` | E-999 | 분류 불가 에러 | pause + notify + await_human |

### 2.2 에러 심각도

| 심각도 | 설명 | 자동 복구 가능 |
|--------|------|:-------------:|
| LOW | 단순 재시도로 해결 가능 (일시적 네트워크, rate limit) | O |
| MEDIUM | 폴백/스킵으로 워크플로우 계속 가능 | △ |
| HIGH | 워크플로우 중단 필요, 사용자 개입 필요 | X |
| CRITICAL | 시스템 레벨 에러, 즉시 알림 | X |

---

## 3. 재시도 정책

### 3.1 재시도 설정

```typescript
interface RetryPolicy {
  max_retries: number;               // 최대 재시도 횟수 (기본 3)
  backoff_strategy: "fixed" | "exponential" | "linear";
  initial_delay_ms: number;          // 초기 지연 (기본 1000)
  max_delay_ms: number;              // 최대 지연 (기본 30000)
  jitter: boolean;                   // 지연에 랜덤 jitter 추가 (기본 true)
  retryable_errors: string[];        // 재시도 대상 에러 유형
}
```

### 3.2 백오프 계산

```python
def calculate_backoff(policy: RetryPolicy, attempt: int) -> int:
    """재시도 지연 시간 계산 (ms)."""
    if policy.backoff_strategy == "fixed":
        delay = policy.initial_delay_ms
    elif policy.backoff_strategy == "exponential":
        delay = policy.initial_delay_ms * (2 ** attempt)
    elif policy.backoff_strategy == "linear":
        delay = policy.initial_delay_ms * (attempt + 1)
    else:
        raise ValueError(f"지원하지 않는 backoff_strategy: {policy.backoff_strategy}")

    delay = min(delay, policy.max_delay_ms)

    if policy.jitter:
        import random
        delay = delay * (0.5 + random.random())  # ±50% jitter

    return int(delay)
```

### 3.3 에러별 기본 재시도 정책

| 에러 유형 | max_retries | backoff | initial_delay | max_delay |
|-----------|:-----------:|---------|:-------------:|:---------:|
| node_timeout | 2 | fixed | 1000ms | 1000ms |
| api_error_5xx | 3 | exponential | 1000ms | 30000ms |
| llm_rate_limit | 5 | exponential | 5000ms | 60000ms |
| browser_element_not_found | 2 | fixed | 2000ms | 2000ms |

---

## 4. 폴백 전략

### 4.1 폴백 유형

| 폴백 유형 | 설명 | 적용 대상 |
|-----------|------|----------|
| **fallback_node** | 에러 노드 대신 대체 노드 실행 | LLMNode (대체 모델), APINode (대체 API) |
| **skip_with_default** | 에러 무시하고 기본값으로 진행 | TransformNode, NotificationNode |
| **human_approval** | 사용자에게 개입 요청 후 대기 | Browser 에러, 분류 불가 에러 |
| **partial_result** | 부분 결과로 계속 진행 | ParallelNode (일부 branch 실패) |

### 4.2 폴백 실행 로직

```python
class FallbackExecutor:
    """에러 발생 시 폴백 전략 실행."""

    async def execute_fallback(
        self, node: WorkflowNode, error: WorkflowError, state: WorkflowState
    ) -> FallbackResult:
        match node.on_error:
            case "retry":
                return await self._retry(node, state)
            case "skip":
                return FallbackResult(
                    action="skipped",
                    output=self._get_default_output(node),
                )
            case "fallback":
                if not node.fallback_node:
                    raise ConfigError("fallback_node 미설정")
                fallback = self._get_node(node.fallback_node)
                result = await execute_node(fallback, state)
                return FallbackResult(action="fallback_executed", output=result)
            case "fail":
                raise error
```

---

## 5. 에러 전파 규칙

### 5.1 전파 체인

```
노드 에러 발생
  ├─ 1) 노드 자체 retry_policy 적용 → 재시도 성공 시 계속
  ├─ 2) 노드 on_error 폴백 적용 → 폴백 성공 시 계속
  ├─ 3) ErrorHandlerNode 존재 시 → 핸들러 실행
  ├─ 4) 워크플로우 레벨 에러 정책 적용
  └─ 5) 미복구 시 → 워크플로우 FAILED 전이
```

### 5.2 ErrorHandlerNode와의 연동

```python
async def handle_node_error(
    node: WorkflowNode, error: WorkflowError, state: WorkflowState
) -> ErrorAction:
    """에러 처리 체인 — 노드 → ErrorHandler → 워크플로우 레벨 순."""

    # 1단계: 노드 자체 재시도
    if node.retry_policy and state.retry_count < node.retry_policy.max_retries:
        delay = calculate_backoff(node.retry_policy, state.retry_count)
        return ErrorAction(type="retry", delay_ms=delay)

    # 2단계: 노드 on_error 폴백
    if node.on_error == "skip":
        return ErrorAction(type="skip", default_output=get_default(node))
    if node.on_error == "fallback" and node.fallback_node:
        return ErrorAction(type="fallback", target_node=node.fallback_node)

    # 3단계: ErrorHandlerNode
    if node.error_handler:
        handler = get_node(node.error_handler)
        return await handler.handle(error, state)

    # 4단계: 워크플로우 레벨 정책
    policy = WORKFLOW_ERROR_POLICIES.get(error.type, WORKFLOW_ERROR_POLICIES["unhandled"])
    return apply_workflow_policy(policy, error, state)
```

### 5.3 SubworkflowNode 에러 전파

```python
async def handle_subworkflow_error(
    node: SubworkflowNode, child_error: WorkflowError, state: WorkflowState
) -> ErrorAction:
    """자식 워크플로우 에러 → 부모 워크플로우로 전파."""
    wrapped_error = SubworkflowError(
        source_workflow=node.config.workflow_id,
        original_error=child_error,
        recursion_depth=state.recursion_depth,
    )
    # 자식 에러는 부모의 에러 핸들링 체인으로 전파
    return await handle_node_error(node, wrapped_error, state)
```

---

## 6. 워크플로우 레벨 에러 정책

```python
WORKFLOW_ERROR_POLICIES = {
    "node_timeout": {
        "action": "retry",
        "max_retries": 2,
        "then": "skip_with_default",
    },
    "api_error_4xx": {
        "action": "fail",
        "notify": True,
    },
    "api_error_5xx": {
        "action": "retry",
        "max_retries": 3,
        "backoff": "exponential",
    },
    "llm_rate_limit": {
        "action": "retry",
        "max_retries": 5,
        "backoff": "exponential",
        "initial_delay_ms": 5000,
    },
    "browser_element_not_found": {
        "action": "retry",
        "max_retries": 2,
        "then": "human_approval",
    },
    "unhandled": {
        "action": "pause",
        "notify": True,
        "await_human": True,
    },
}
```

---

## 7. AI 에러 분석

```python
class AIErrorAnalyzer:
    """LLM 기반 에러 원인 분석 + 수정 제안."""

    async def analyze(self, error: WorkflowError, context: ExecutionContext) -> ErrorAnalysis:
        """에러 로그와 실행 컨텍스트를 LLM에 전달하여 원인 분석."""
        prompt = f"""
        워크플로우 에러 분석:
        - 에러 유형: {error.type}
        - 에러 메시지: {error.message}
        - 스택 트레이스: {error.stack_trace}
        - 노드: {error.node_id} ({error.node_type})
        - 입력 데이터: {error.input_data}
        - 실행 컨텍스트: {context.summary()}

        다음을 분석해주세요:
        1. 에러 근본 원인
        2. 권장 수정 방법
        3. 재발 방지 제안
        """
        analysis = await llm_call(prompt, model="claude-3-sonnet")
        return ErrorAnalysis(
            root_cause=analysis.root_cause,
            suggested_fix=analysis.suggested_fix,
            prevention=analysis.prevention,
            confidence=analysis.confidence,
        )
```

---

## 8. 에러 알림

```python
class ErrorNotifier:
    """에러 발생 시 사용자 알림."""

    async def notify(self, error: WorkflowError, context: ExecutionContext):
        """에러 심각도에 따라 알림 채널 선택."""
        severity = classify_severity(error)

        notification = ErrorNotification(
            workflow_name=context.workflow_name,
            node_name=error.node_name,
            error_type=error.type,
            message=error.message,
            execution_id=context.execution_id,
            severity=severity,
            timestamp=datetime.utcnow().isoformat(),
        )

        if severity in ("HIGH", "CRITICAL"):
            await send_push_notification(notification)
            await send_email_notification(notification)
        elif severity == "MEDIUM":
            await send_push_notification(notification)
        else:  # LOW
            # 로그만 기록, 알림 미발송
            log_error(notification)
```

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| L3 v1.0 | 2026-04-09 | Phase 1 1-1 — 에러 분류 체계, 재시도 정책, 폴백 전략, 에러 전파 체인, AI 분석 |
