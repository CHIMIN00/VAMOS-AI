# WORKFLOW_RPA 상세명세

> **Tier**: 3 (Feature Domains) | **Part2 Status**: SHELL (I-12 4줄만) | **SOT**: STEP7-N (72 items)
> **Version**: 1.0.0 | **최종수정**: 2026-03-22
> **교차참조**: T2-CORE_AI → LLM 의도파싱, T2-AGENT_TOOL → 도구 실행, T3-PKM → 워크플로우 지식화

---

## 1. 개요

VAMOS 워크플로우/RPA 모듈은 사용자의 반복 작업을 DAG(Directed Acyclic Graph) 기반
워크플로우로 자동화한다. 자연어 명령으로 워크플로우를 생성하고, 시간/이벤트/조건
기반 트리거로 자동 실행하며, 브라우저 및 데스크톱 RPA를 통해 외부 시스템과 연동한다.

### 1.1 아키텍처 개요

```
[사용자 자연어 명령]
    ↓
[NL→DAG 변환기] → [DAG 검증] → [워크플로우 등록]
    ↓                                  ↓
[LangGraph StateGraph 엔진]     [트리거 시스템]
    ↓                                  ↓
[노드 실행] ←─── 트리거 발화 ─────────┘
    ├─→ [LLM 노드]
    ├─→ [API 호출 노드]
    ├─→ [브라우저 자동화 노드]
    ├─→ [데스크톱 RPA 노드]
    ├─→ [조건 분기 노드]
    └─→ [Human-in-the-Loop 노드]
        ↓
[결과 집계 + 알림]
```

---

## 2. DAG 워크플로우 엔진

### 2.1 LangGraph StateGraph 기반 DAG 정의

```python
# workflow_engine.py
from langgraph.graph import StateGraph, END

class WorkflowEngine:
    """LangGraph StateGraph 기반 DAG 워크플로우 실행 엔진"""

    def build_graph(self, workflow_def: WorkflowDefinition) -> StateGraph:
        graph = StateGraph(WorkflowState)

        # 노드 등록
        for node_def in workflow_def.nodes:
            executor = self._resolve_executor(node_def.type)
            graph.add_node(node_def.id, executor)

        # 엣지 등록 (조건부 포함)
        for edge in workflow_def.edges:
            if edge.condition:
                graph.add_conditional_edges(
                    edge.source,
                    self._build_condition(edge.condition),
                    edge.targets    # {condition_value: target_node_id}
                )
            else:
                graph.add_edge(edge.source, edge.target)

        # 시작/종료 설정
        graph.set_entry_point(workflow_def.entry_node)
        for end_node in workflow_def.end_nodes:
            graph.add_edge(end_node, END)

        return graph.compile()
```

### 2.2 노드 타입 정의

```typescript
// workflow_node_types.ts
// LOCK-WF-01 (AUTHORITY_CHAIN §2): 12 타입 — 제거·재정의 불가, 추가만 허용
type NodeType =
  | "LLMNode"            // LLM API 호출 (프롬프트 실행)
  | "APINode"            // 외부 REST/GraphQL API 호출
  | "ConditionNode"      // 조건 분기 (if/else)
  | "ParallelNode"       // 병렬 실행
  | "HumanApprovalNode"  // 사람 승인 대기
  | "TransformNode"      // 데이터 변환/매핑/필터
  | "NotificationNode"   // 알림 (이메일/슬랙/텔레그램)
  | "LoopNode"           // 반복 (for each / while)
  | "SubworkflowNode"    // 다른 워크플로우 호출
  | "ErrorHandlerNode"   // 에러 처리 (catch/retry)
  | "DelayNode"          // 지연/대기
  | "CodeNode";          // 사용자 정의 Python/JS 코드 (브라우저/데스크톱 RPA는 CodeNode 프리셋)

interface WorkflowNode {
  id: string;
  type: NodeType;
  name: string;                   // 표시 이름
  config: Record<string, any>;    // 노드별 설정
  retry_policy?: RetryPolicy;
  timeout_ms?: number;            // 기본 30000
  on_error: "fail" | "skip" | "retry" | "fallback";
  fallback_node?: string;         // on_error="fallback"일 때 대체 노드
}

interface RetryPolicy {
  max_retries: number;            // default 3
  backoff_strategy: "fixed" | "exponential" | "linear";
  initial_delay_ms: number;       // default 1000
  max_delay_ms: number;           // default 30000
}
```

### 2.3 실행 전략

```python
# execution_strategy.py
class ExecutionStrategy(Enum):
    SEQUENTIAL = "sequential"       # 순차 실행
    PARALLEL = "parallel"           # 병렬 실행 (독립 노드)
    STREAMING = "streaming"         # 스트리밍 (파이프라인)

class WorkflowState(TypedDict):
    """워크플로우 실행 상태 (LangGraph State)"""
    workflow_id: str
    execution_id: str
    current_node: str
    status: str                     # LOCK-WF-09: "PENDING" | "RUNNING" | "SUCCESS" | "FAILED" | "CANCELLED" | "TIMEOUT"
    node_results: dict[str, Any]    # {node_id: result}
    variables: dict[str, Any]       # 공유 변수
    error_stack: list[str]
    started_at: str
    elapsed_ms: int
```

### 2.4 에러 핸들링

```python
# error_handler.py
class WorkflowErrorHandler:
    """워크플로우 레벨 에러 핸들링"""

    ERROR_POLICIES = {
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

    async def handle(self, error: WorkflowError, context: ExecutionContext) -> ErrorAction:
        policy = self._match_policy(error)
        if policy["action"] == "retry" and context.retry_count < policy["max_retries"]:
            delay = self._calculate_backoff(policy, context.retry_count)
            return ErrorAction(type="retry", delay_ms=delay)
        elif policy.get("then") == "human_approval":
            return ErrorAction(type="pause", reason=str(error), notify=True)
        elif policy.get("then") == "skip_with_default":
            return ErrorAction(type="skip", reason=str(error), default_output=self._get_default_output(error))
        else:
            return ErrorAction(type="fail", reason=str(error))
```

---

## 3. NL → 워크플로우 생성

### 3.1 자연어 → DAG 변환 파이프라인

```
[자연어 입력] → [의도 파싱 (LLM)] → [엔티티 추출]
    ↓
[템플릿 매칭] ─── 매칭됨 ──→ [템플릿 인스턴스화] → [파라미터 채우기]
    │
    └── 매칭 안됨 ──→ [LLM DAG 생성] → [DAG 구조 검증] → [실행 가능성 검증]
                                                              ↓
                                                    [사용자 확인/수정]
                                                              ↓
                                                    [워크플로우 등록]
```

### 3.2 의도 파싱

```python
# intent_parser.py
class WorkflowIntentParser:
    """자연어에서 워크플로우 의도를 파싱"""

    INTENT_CATEGORIES = {
        "scheduled_task":     ["매일", "매주", "매월", "~마다", "~시에"],
        "event_triggered":    ["~하면", "~될 때", "~가 오면", "새로운"],
        "data_pipeline":      ["수집", "크롤링", "스크래핑", "모니터링"],
        "notification":       ["알려줘", "알림", "보내줘", "리포트"],
        "automation":         ["자동으로", "자동화", "반복"],
        "approval_flow":      ["승인", "검토", "결재"],
    }

    async def parse(self, user_input: str) -> WorkflowIntent:
        """
        예: "매일 아침 9시에 네이버 뉴스 경제 섹션 크롤링해서 요약 후 슬랙으로 보내줘"

        결과:
        WorkflowIntent(
            trigger=TimeTrigger(cron="0 9 * * *"),
            steps=[
                Step(type="browser_action", action="crawl", target="naver_news_economy"),
                Step(type="llm_call", action="summarize"),
                Step(type="notification", channel="slack"),
            ]
        )
        """
```

### 3.3 DAG 검증

```python
# dag_validator.py
class DAGValidator:
    """생성된 DAG의 유효성 검증"""

    VALIDATION_RULES = [
        "no_cycles",                    # 사이클 없음 (토폴로지 정렬 가능)
        "single_entry",                 # 단일 진입점
        "all_nodes_reachable",          # 모든 노드 도달 가능
        "no_dangling_edges",            # 미연결 엣지 없음
        "valid_node_types",             # 모든 노드 타입 유효
        "required_configs_present",     # 필수 설정 존재
        "compatible_io",               # 노드 간 입출력 타입 호환
        "resource_limits_ok",          # 리소스 한도 내
    ]

    def validate(self, dag: WorkflowDefinition) -> ValidationResult:
        errors = []
        warnings = []
        for rule in self.VALIDATION_RULES:
            result = getattr(self, f"_check_{rule}")(dag)
            if result.severity == "error":
                errors.append(result)
            elif result.severity == "warning":
                warnings.append(result)
        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
```

---

## 4. 트리거 시스템

### 4.1 트리거 유형

```typescript
// trigger_types.ts
type TriggerType = "time" | "event" | "condition" | "manual" | "webhook";

interface TimeTrigger {
  type: "time";
  cron: string;                     // "0 9 * * 1-5" (평일 9시)
  timezone: string;                 // "Asia/Seoul"
  start_date?: string;
  end_date?: string;
  max_executions?: number;
}

interface EventTrigger {
  type: "event";
  event_source: string;             // "email" | "slack" | "github" | "webhook" | "file_system"
  event_type: string;               // "new_message" | "push" | "file_created"
  filter?: Record<string, any>;     // 이벤트 필터 조건
}

interface ConditionTrigger {
  type: "condition";
  check_interval_sec: number;       // 폴링 간격
  condition: {
    source: string;                 // "api" | "database" | "metric"
    query: string;                  // API URL, SQL 쿼리, 메트릭 쿼리
    operator: "gt" | "lt" | "eq" | "contains" | "changed";
    threshold: any;
  };
}

interface WebhookTrigger {
  type: "webhook";
  endpoint: string;                 // "/api/v1/webhooks/{workflow_id}"
  method: "POST" | "GET";
  auth: "none" | "api_key" | "hmac_signature";
  secret?: string;
}
```

### 4.2 크론 표현식 파서

```python
# cron_parser.py
CRON_EXAMPLES = {
    "매일 아침 9시": "0 9 * * *",
    "평일 오전 9시": "0 9 * * 1-5",
    "매주 월요일": "0 0 * * 1",
    "매월 1일": "0 0 1 * *",
    "10분마다": "*/10 * * * *",
    "매시간": "0 * * * *",
    "매일 9시, 18시": "0 9,18 * * *",
}

class NaturalLanguageCronParser:
    """자연어 → 크론 표현식 변환"""

    async def parse(self, nl_schedule: str) -> str:
        """LLM 기반 자연어 → cron 변환 + 검증"""
        cron_expr = await self._llm_parse(nl_schedule)
        self._validate_cron(cron_expr)
        return cron_expr
```

### 4.3 이벤트 버스

```python
# event_bus.py
class EventBus:
    """워크플로우 트리거를 위한 내부 이벤트 버스"""

    CHANNELS = {
        "email":       RedisStream("events:email"),
        "slack":       RedisStream("events:slack"),
        "github":      RedisStream("events:github"),
        "file_system": RedisStream("events:fs"),
        "webhook":     RedisStream("events:webhook"),
        "schedule":    RedisStream("events:schedule"),
        "internal":    RedisStream("events:internal"),
    }

    async def publish(self, channel: str, event: Event):
        await self.CHANNELS[channel].add(event.serialize())

    async def subscribe(self, channel: str, handler: Callable):
        stream = self.CHANNELS[channel]
        async for event in stream.listen():
            matched_workflows = await self._match_triggers(event)
            for wf in matched_workflows:
                await self._enqueue_execution(wf, event)
```

---

## 5. 템플릿 라이브러리

### 5.1 도메인별 템플릿 카탈로그

| 도메인 | 템플릿명 | 트리거 | 노드 수 | V1 |
|-------|---------|--------|--------|-----|
| **투자** | 주식 모니터링 + 알림 | condition (가격변동) | 4 | O |
| **투자** | 일간 시장 리포트 | time (매일 18시) | 5 | O |
| **투자** | 포트폴리오 리밸런싱 알림 | condition (비중 이탈) | 6 | - |
| **코딩** | GitHub PR 자동 리뷰 | event (PR 생성) | 4 | O |
| **코딩** | 의존성 업데이트 체크 | time (매주 월) | 3 | O |
| **코딩** | 에러 로그 분석 + 알림 | event (로그 패턴) | 5 | - |
| **생산성** | 이메일 자동 분류/요약 | event (새 이메일) | 4 | O |
| **생산성** | 미팅 노트 자동 정리 | event (미팅 종료) | 5 | - |
| **생산성** | 일간 할일 생성 | time (매일 08시) | 3 | O |
| **컨텐츠** | 블로그 아이디어 → 초안 | manual | 6 | O |
| **컨텐츠** | SNS 자동 포스팅 | time (설정 시간) | 4 | - |
| **컨텐츠** | 뉴스레터 큐레이션 | time (매주) | 5 | - |

### 5.2 템플릿 스키마 및 CRUD API

```typescript
// workflow_template.ts
interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  domain: "investment" | "coding" | "productivity" | "content" | "custom";
  version: string;                   // semver
  tags: string[];
  difficulty: "beginner" | "intermediate" | "advanced";

  // DAG 정의
  nodes: TemplateNode[];
  edges: TemplateEdge[];
  default_trigger: TriggerConfig;

  // 파라미터 (사용자 커스터마이징)
  parameters: TemplateParameter[];

  // 메타데이터
  author: string;
  usage_count: number;
  rating: number;
  created_at: string;
  updated_at: string;
}

interface TemplateParameter {
  name: string;
  label: string;                     // 한글 표시명
  type: "string" | "number" | "boolean" | "select" | "cron" | "url";
  required: boolean;
  default?: any;
  options?: string[];                // type="select"일 때
  description: string;
  validation?: string;               // regex pattern
}
```

```
// REST API
GET    /api/v1/templates                  // 목록 (필터: domain, tags)
GET    /api/v1/templates/:id              // 상세
POST   /api/v1/templates                  // 생성 (관리자)
PUT    /api/v1/templates/:id              // 수정
DELETE /api/v1/templates/:id              // 삭제
POST   /api/v1/templates/:id/instantiate  // 템플릿 → 워크플로우 인스턴스 생성
GET    /api/v1/templates/:id/versions     // 버전 이력
```

---

## 6. 브라우저 자동화 (Playwright)

### 6.1 브라우저 액션 정의

```python
# browser_automation.py
class BrowserAction(Enum):
    NAVIGATE = "navigate"            # URL 이동
    CLICK = "click"                  # 요소 클릭
    TYPE = "type"                    # 텍스트 입력
    SELECT = "select"                # 드롭다운 선택
    SCREENSHOT = "screenshot"        # 스크린샷
    EXTRACT = "extract"              # 데이터 추출 (CSS/XPath)
    WAIT = "wait"                    # 요소 대기
    SCROLL = "scroll"                # 스크롤
    HOVER = "hover"                  # 요소 호버 (LOCK-WF-07)
    FILL_FORM = "fill_form"          # 폼 자동 입력
    DOWNLOAD = "download"            # 파일 다운로드
    EXECUTE_JS = "execute_js"        # JavaScript 실행

class PlaywrightExecutor:
    """Playwright 기반 브라우저 자동화 실행기"""

    BROWSER_CONFIG = {
        "browser": "chromium",
        "headless": True,
        "viewport": {"width": 1920, "height": 1080},
        "timeout_ms": 30000,
        "user_agent": "VAMOS-Bot/1.0",
        "proxy": None,                  # 필요시 설정
    }

    async def execute(self, actions: list[BrowserActionStep]) -> BrowserResult:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.BROWSER_CONFIG["headless"])
            context = await browser.new_context(
                viewport=self.BROWSER_CONFIG["viewport"],
                user_agent=self.BROWSER_CONFIG["user_agent"],
            )
            page = await context.new_page()

            results = []
            for action in actions:
                result = await self._execute_action(page, action)
                results.append(result)

            await browser.close()
            return BrowserResult(steps=results)
```

### 6.2 웹 스크래핑 구조

```python
# web_scraper.py
class ScrapingConfig:
    url: str
    selectors: dict[str, str]        # {"title": "h1.title", "price": "span.price"}
    pagination: Optional[PaginationConfig]
    rate_limit: float = 1.0          # 요청/초
    max_pages: int = 10
    output_format: "json" | "csv" | "markdown"
    respect_robots_txt: bool = True
    cache_ttl_sec: int = 3600
```

---

## 7. RPA 데스크톱 자동화

### 7.1 데스크톱 액션 유형

```python
# desktop_rpa.py
class DesktopAction(Enum):
    LAUNCH_APP = "launch_app"        # 앱 실행
    FOCUS_WINDOW = "focus_window"    # 창 포커스
    KEYBOARD = "keyboard"            # 키보드 입력/단축키
    MOUSE_CLICK = "mouse_click"      # 마우스 클릭 (좌표/이미지)
    MOUSE_MOVE = "mouse_move"        # 마우스 이동
    SCREEN_CAPTURE = "screen_capture" # 화면 캡처
    OCR_REGION = "ocr_region"        # 특정 영역 OCR
    FIND_IMAGE = "find_image"        # 이미지 매칭 (템플릿)
    WAIT_IMAGE = "wait_image"        # 이미지 나타날 때까지 대기
    CLIPBOARD = "clipboard"          # 클립보드 읽기/쓰기
    FILE_DIALOG = "file_dialog"      # 파일 대화상자 처리

class DesktopRPAConfig:
    screen_resolution: tuple = (1920, 1080)
    ocr_engine: str = "tesseract"
    image_match_confidence: float = 0.8
    action_delay_ms: int = 200       # 액션 간 딜레이
    screenshot_on_error: bool = True
    max_execution_time_sec: int = 300
```

### 7.2 스크린 인식 기반 자동화

```python
# screen_recognition.py
class ScreenRecognizer:
    """화면 요소 인식 (OCR + 이미지 매칭 + AI)"""

    async def find_element(self, target: ElementTarget) -> ScreenLocation:
        """
        3단계 요소 탐색:
        1. 이미지 템플릿 매칭 (OpenCV matchTemplate)
        2. OCR 텍스트 검색 (문자열 위치 찾기)
        3. AI 비전 (GPT-4o로 요소 위치 추론) — fallback
        """
        # Stage 1: 템플릿 매칭
        if target.template_image:
            loc = await self._template_match(target.template_image)
            if loc and loc.confidence >= self.image_match_confidence:
                return loc

        # Stage 2: OCR 기반
        if target.text:
            loc = await self._ocr_find(target.text)
            if loc:
                return loc

        # Stage 3: AI 비전 fallback
        screenshot = await self._capture_screen()
        loc = await self._ai_vision_find(screenshot, target.description)
        return loc
```

---

## 8. 교차참조

| 참조 모듈 | 연관 항목 | 참조 방향 |
|----------|---------|----------|
| T2-CORE_AI (2-2) | LLM 의도파싱, NL→DAG 변환 | ← 사용 |
| T2-AGENT_TOOL (2-4) | 도구 실행, API 호출 | ← 사용 |
| T3-Multimodal (3-2) | 스크린 캡처/OCR | ← 사용 |
| T3-PKM (3-3) | 워크플로우 실행 기록 지식화 | → 제공 |
| T4-Frontend (4-1) | 워크플로우 빌더 UI, 모니터링 대시보드 | → 제공 |
| T1-INFRA (1-x) | 스케줄러, 이벤트 버스 인프라 | ← 사용 |

---

*끝 — WORKFLOW_RPA 상세명세 v1.0.0*
