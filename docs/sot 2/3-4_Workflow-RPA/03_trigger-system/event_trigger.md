# Event 트리거 (이벤트 기반) — L3 상세 명세

> **N-ID**: N-003b (EXTEND)
> **V단계**: V1
> **도메인**: 3-4_Workflow-RPA / 03_trigger-system
> **정본**: sot 2/3-4_Workflow-RPA/03_trigger-system/event_trigger.md
> **교차참조**: time_trigger.md (EventBus 공유), webhook_trigger.md (웹훅 이벤트 수신), condition_trigger.md (조건 평가 연동)

---

## 1. 개요

이벤트 트리거는 외부 시스템(이메일, Slack, GitHub, 파일시스템)에서 발생하는 이벤트를 감지하여 워크플로우를 자동 실행한다. 내부 EventBus(Redis Streams 기반)를 통해 이벤트를 수신·필터링·매칭하며, 이벤트 소스별 어댑터가 외부 시스템과의 연동을 담당한다.

> LOCK (기존 명세 §4(5종) + STEP7-N N-003(+2종) / LOCK-WF-06): Time(cron), Event(이벤트), Condition(조건), Webhook(웹훅), Manual(수동), Conversation(대화 기반), Ambient(앰비언트) — 7유형 트리거 체계

---

## 2. 핵심 제약 (LOCK)

> LOCK (기존 명세 §4(5종) + STEP7-N N-003(+2종) / LOCK-WF-06): Time(cron), Event(이벤트), Condition(조건), Webhook(웹훅), Manual(수동), Conversation(대화 기반), Ambient(앰비언트) — 7유형 트리거 체계

> LOCK (가이드 R-07-2 / LOCK-WF-03): Human Approval 타임아웃 = 10분 (600초)

---

## 3. 입력 스키마

```typescript
interface EventTriggerConfig {
  type: "event";
  trigger_id: string;                  // UUID v7
  workflow_id: string;                 // 대상 워크플로우 ID

  // --- 이벤트 소스 ---
  event_source: EventSource;           // 이벤트 소스 유형
  event_type: string;                  // 이벤트 타입 (소스별 상이)

  // --- 필터 ---
  filters: EventFilter[];              // 이벤트 필터 조건 (AND 결합)

  // --- 디바운싱 ---
  debounce_seconds?: number;           // 디바운스 간격 (기본 0 = 즉시)
  batch_window_seconds?: number;       // 배치 수집 윈도우 (기본 null = 개별)

  // --- 메타데이터 ---
  enabled: boolean;
  description?: string;
  created_at: string;
  updated_at: string;
}

type EventSource = "email" | "slack" | "github" | "file_system" | "webhook";

interface EventFilter {
  field: string;                       // 이벤트 필드 경로 (dot notation)
  operator: "eq" | "neq" | "contains" | "regex" | "in" | "exists";
  value: any;                          // 비교 값
}
```

### 3.1 이벤트 소스별 event_type

| event_source | event_type | 설명 |
|-------------|-----------|------|
| `email` | `new_message` | 새 이메일 수신 |
| `email` | `label_changed` | 라벨 변경 |
| `slack` | `message` | 채널 메시지 |
| `slack` | `mention` | 멘션 |
| `slack` | `reaction` | 리액션 추가 |
| `github` | `push` | 코드 푸시 |
| `github` | `pull_request` | PR 생성/업데이트 |
| `github` | `issue` | 이슈 생성/업데이트 |
| `github` | `release` | 릴리스 게시 |
| `github` | `workflow_run` | GitHub Actions 완료 |
| `file_system` | `created` | 파일 생성 |
| `file_system` | `modified` | 파일 수정 |
| `file_system` | `deleted` | 파일 삭제 |
| `webhook` | `received` | 외부 웹훅 수신 (→ webhook_trigger.md 위임) |

---

## 4. EventBus 아키텍처

### 4.1 Redis Streams 기반 이벤트 버스

```python
# event_bus.py
class EventBus:
    """Redis Streams 기반 내부 이벤트 버스"""

    CHANNELS: dict[str, str] = {
        "email":       "events:email",
        "slack":       "events:slack",
        "github":      "events:github",
        "file_system": "events:fs",
        "webhook":     "events:webhook",
        "schedule":    "events:schedule",     # time_trigger.md 공유
        "internal":    "events:internal",
    }

    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.consumer_group = "trigger_evaluator"

    async def publish(self, channel: str, event: Event):
        """이벤트 발행 → Redis Stream XADD"""
        stream_key = self.CHANNELS[channel]
        await self.redis.xadd(stream_key, event.serialize(), maxlen=10000)

    async def subscribe(self, channel: str, handler: Callable[[Event], Awaitable[None]]):
        """이벤트 구독 → Consumer Group 기반 소비"""
        stream_key = self.CHANNELS[channel]
        # Consumer Group 생성 (이미 존재하면 무시)
        try:
            await self.redis.xgroup_create(stream_key, self.consumer_group, "$", mkstream=True)
        except Exception:
            pass

        while True:
            messages = await self.redis.xreadgroup(
                groupname=self.consumer_group,
                consumername=f"worker-{os.getpid()}",
                streams={stream_key: ">"},
                count=10,
                block=5000,
            )
            for _, entries in messages:
                for msg_id, data in entries:
                    event = Event.deserialize(data)
                    try:
                        await handler(event)
                    except Exception as e:
                        # 핸들러 실패: 루프 보호 + 이벤트 유실 방지 (DLQ 적재 후 ack)
                        logger.exception(f"handler failed for {msg_id}: {e}")
                        await self.redis.xadd(f"{stream_key}:dlq", data, maxlen=10000)
                    finally:
                        # PEL 진행 보장: 성공/실패 모두 ack (실패분은 DLQ에 보존)
                        await self.redis.xack(stream_key, self.consumer_group, msg_id)
```

### 4.2 이벤트 스키마

```typescript
interface Event {
  event_id: string;                    // UUID v7
  source: EventSource;                 // 이벤트 소스
  event_type: string;                  // 이벤트 타입
  timestamp: string;                   // ISO 8601
  payload: Record<string, any>;        // 소스별 페이로드
  metadata: {
    correlation_id?: string;           // 관련 이벤트 추적 ID
    retry_count: number;               // 재처리 횟수
  };
}
```

---

## 5. 이벤트 소스 어댑터

### 5.1 어댑터 아키텍처

```python
class EventSourceAdapter(ABC):
    """이벤트 소스 어댑터 공통 인터페이스"""

    @abstractmethod
    async def start(self):
        """어댑터 시작 (폴링/웹훅 리스너 등)"""

    @abstractmethod
    async def stop(self):
        """어댑터 중지"""

    @abstractmethod
    async def health_check(self) -> bool:
        """연결 상태 확인"""
```

### 5.2 Email 어댑터

```python
class EmailAdapter(EventSourceAdapter):
    """Gmail/Outlook API 기반 이메일 이벤트 감지"""

    POLL_INTERVAL_SECONDS = 30         # Gmail push notification 미사용 시 폴링 간격

    async def start(self):
        # Gmail API Watch (push notification) 우선 시도
        # 실패 시 IMAP IDLE 또는 폴링 폴백
        if self.gmail_push_available:
            await self._setup_gmail_watch()
        else:
            await self._start_polling()

    async def _on_new_email(self, email: EmailMessage):
        event = Event(
            source="email",
            event_type="new_message",
            payload={
                "from": email.sender,
                "to": email.recipients,
                "subject": email.subject,
                "labels": email.labels,
                "has_attachment": email.has_attachment,
                "snippet": email.snippet[:200],
            },
        )
        await self.event_bus.publish("email", event)
```

### 5.3 Slack 어댑터

```python
class SlackAdapter(EventSourceAdapter):
    """Slack Events API / Socket Mode 기반 이벤트 감지"""

    async def start(self):
        # Slack Socket Mode (웹소켓 기반, 서버 불필요)
        self.socket_client = AsyncSocketModeClient(
            app_token=self.config.slack_app_token,
            web_client=AsyncWebClient(token=self.config.slack_bot_token),
        )
        self.socket_client.socket_mode_request_listeners.append(self._handle_event)
        await self.socket_client.connect()

    async def _handle_event(self, req: SocketModeRequest):
        if req.type == "events_api":
            event_data = req.payload["event"]
            event = Event(
                source="slack",
                event_type=self._map_event_type(event_data["type"]),
                payload={
                    "channel": event_data.get("channel"),
                    "user": event_data.get("user"),
                    "text": event_data.get("text", ""),
                    "thread_ts": event_data.get("thread_ts"),
                },
            )
            await self.event_bus.publish("slack", event)
```

### 5.4 GitHub 어댑터

```python
class GitHubAdapter(EventSourceAdapter):
    """GitHub Webhooks 기반 이벤트 감지"""

    SUPPORTED_EVENTS = ["push", "pull_request", "issues", "release", "workflow_run"]

    async def _handle_webhook(self, headers: dict, body: bytes):
        """GitHub Webhook 수신 → 검증 → 이벤트 발행"""
        # HMAC-SHA256 서명 검증
        signature = headers.get("X-Hub-Signature-256")
        if not self._verify_signature(body, signature):
            raise AuthenticationError("Invalid GitHub webhook signature")

        event_type = headers["X-GitHub-Event"]
        payload = json.loads(body)

        event = Event(
            source="github",
            event_type=event_type,
            payload={
                "action": payload.get("action"),
                "repository": payload["repository"]["full_name"],
                "sender": payload["sender"]["login"],
                "data": self._extract_relevant_data(event_type, payload),
            },
        )
        await self.event_bus.publish("github", event)
```

### 5.5 파일시스템 어댑터

```python
class FileSystemAdapter(EventSourceAdapter):
    """watchdog 기반 파일시스템 이벤트 감지"""

    async def start(self):
        self.observer = Observer()
        handler = FileEventHandler(self.event_bus, self.config.watch_paths)
        for path in self.config.watch_paths:
            self.observer.schedule(handler, path, recursive=self.config.recursive)
        self.observer.start()

class FileEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        asyncio.run_coroutine_threadsafe(
            self._publish("created", event.src_path), self.loop
        )

    def on_modified(self, event):
        asyncio.run_coroutine_threadsafe(
            self._publish("modified", event.src_path), self.loop
        )

    def on_deleted(self, event):
        asyncio.run_coroutine_threadsafe(
            self._publish("deleted", event.src_path), self.loop
        )

    async def _publish(self, event_type: str, path: str):
        event = Event(
            source="file_system",
            event_type=event_type,
            payload={
                "path": path,
                "filename": os.path.basename(path),
                "extension": os.path.splitext(path)[1],
                "is_directory": os.path.isdir(path),
            },
        )
        await self.event_bus.publish("file_system", event)
```

---

## 6. 평가 로직 (필터 매칭)

### 6.1 트리거 매칭 엔진

```python
class EventTriggerEvaluator:
    """이벤트 수신 → 등록된 트리거 필터 매칭 → 워크플로우 실행 결정"""

    async def evaluate(self, event: Event) -> list[str]:
        """매칭되는 워크플로우 ID 목록 반환"""
        triggers = await self.store.get_active_triggers(
            event_source=event.source,
            event_type=event.event_type,
        )

        matched_workflow_ids = []
        for trigger in triggers:
            if self._match_filters(event, trigger.filters):
                # 디바운싱 검사
                if trigger.debounce_seconds and trigger.debounce_seconds > 0:
                    if await self._is_debounced(trigger.trigger_id, trigger.debounce_seconds):
                        continue

                matched_workflow_ids.append(trigger.workflow_id)

                # 트리거 이벤트 발행
                trigger_event = TriggerEvent(
                    trigger_id=trigger.trigger_id,
                    trigger_type="event",
                    workflow_id=trigger.workflow_id,
                    fired_at=datetime.utcnow().isoformat(),
                    payload={
                        "source_event_id": event.event_id,
                        "event_source": event.source,
                        "event_type": event.event_type,
                    },
                )
                await self.event_bus.publish("internal", trigger_event)

        return matched_workflow_ids

    def _match_filters(self, event: Event, filters: list[EventFilter]) -> bool:
        """AND 결합 필터 매칭"""
        for f in filters:
            value = self._get_nested_value(event.payload, f.field)
            if not self._evaluate_operator(value, f.operator, f.value):
                return False
        return True

    def _evaluate_operator(self, actual: any, operator: str, expected: any) -> bool:
        match operator:
            case "eq":       return actual == expected
            case "neq":      return actual != expected
            case "contains": return expected in str(actual)
            case "regex":    return bool(re.match(expected, str(actual)))
            case "in":       return actual in expected
            case "exists":   return actual is not None
```

### 6.2 디바운싱

```python
async def _is_debounced(self, trigger_id: str, debounce_seconds: int) -> bool:
    """Redis 기반 디바운스: 마지막 발화 후 debounce_seconds 이내이면 True"""
    key = f"debounce:{trigger_id}"
    # 원자적 check-and-set: SET NX EX. 신규 설정 성공 = 디바운스 아님(False),
    # 이미 존재 = 윈도우 내 재발화이므로 디바운스됨(True). GET+SETEX 경쟁 조건 제거.
    was_set = await self.redis.set(key, str(time.time()), nx=True, ex=debounce_seconds)
    if was_set:
        return False
    return True
```

### 6.3 배치 수집

```python
async def _batch_collect(self, trigger_id: str, event: Event, window_seconds: int):
    """배치 윈도우 내 이벤트를 모아서 1회 트리거 발화"""
    batch_key = f"batch:{trigger_id}"
    await self.redis.rpush(batch_key, event.serialize())
    await self.redis.expire(batch_key, window_seconds + 10)

    # 윈도우 타이머가 없으면 신규 생성
    timer_key = f"batch_timer:{trigger_id}"
    if not await self.redis.exists(timer_key):
        await self.redis.setex(timer_key, window_seconds, "1")
        # window_seconds 후 배치 발화 스케줄
        loop = asyncio.get_running_loop()
        loop.call_later(
            window_seconds,
            lambda: asyncio.ensure_future(self._fire_batch(trigger_id, batch_key)),
        )
```

---

## 7. 트리거 이벤트 스키마

```typescript
interface TriggerEvent {
  event_id: string;                    // UUID v7
  trigger_id: string;
  trigger_type: "event";
  workflow_id: string;
  fired_at: string;                    // ISO 8601
  payload: {
    source_event_id: string;           // 원본 이벤트 ID
    event_source: EventSource;
    event_type: string;
    matched_filters: string[];         // 매칭된 필터 필드 목록
    batch_count?: number;              // 배치 수집 시 이벤트 수
  };
}
```

---

## 8. 필터 예시

### 8.1 이메일: 특정 발신자의 첨부파일 포함 메일

```json
{
  "event_source": "email",
  "event_type": "new_message",
  "filters": [
    {"field": "from", "operator": "eq", "value": "boss@company.com"},
    {"field": "has_attachment", "operator": "eq", "value": true}
  ]
}
```

### 8.2 GitHub: 특정 리포지토리 PR 생성

```json
{
  "event_source": "github",
  "event_type": "pull_request",
  "filters": [
    {"field": "action", "operator": "eq", "value": "opened"},
    {"field": "repository", "operator": "eq", "value": "myorg/myrepo"}
  ]
}
```

### 8.3 파일시스템: CSV 파일 생성 감지

```json
{
  "event_source": "file_system",
  "event_type": "created",
  "filters": [
    {"field": "extension", "operator": "eq", "value": ".csv"},
    {"field": "path", "operator": "contains", "value": "/data/inbox/"}
  ]
}
```

### 8.4 Jinja2 고급 필터

복잡한 조건은 Jinja2 표현식으로도 지원한다:

```python
# Jinja2 조건 표현식 (향후 확장)
JINJA2_FILTER_EXAMPLE = "{{ event.sender == 'boss@company.com' and 'urgent' in event.subject.lower() }}"
```

---

## 9. 교차참조

| 참조 대상 | 관계 |
|----------|------|
| `time_trigger.md` | EventBus "schedule" 채널 공유 |
| `webhook_trigger.md` | 외부 웹훅 수신 → EventBus "webhook" 채널로 전달 |
| `condition_trigger.md` | 조건 트리거가 이벤트를 소스로 사용 가능 |
| `execution_engine.md` | 트리거 발화 → 워크플로우 실행 큐 등록 |
| `dag_architecture.md` | 실행 대상 워크플로우 DAG 참조 |
| 부록 §B.2 | Event 트리거 설정 정본 |

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-04-09 | v1.0 | L3 초판 작성 (N-003b EXTEND, Redis Streams EventBus, 5종 어댑터, 필터 매칭, 디바운싱/배치) |
