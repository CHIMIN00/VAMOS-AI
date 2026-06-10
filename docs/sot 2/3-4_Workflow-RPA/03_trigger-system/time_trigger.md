# Time 트리거 (Cron 스케줄러) — L3 상세 명세

> **N-ID**: N-003a (EXTEND)
> **V단계**: V1
> **도메인**: 3-4_Workflow-RPA / 03_trigger-system
> **정본**: sot 2/3-4_Workflow-RPA/03_trigger-system/time_trigger.md
> **교차참조**: dag_architecture.md (DAG 스키마), execution_engine.md (실행 엔진), event_trigger.md (이벤트 버스 공유)

---

## 1. 개요

시간 기반 트리거는 Cron 표현식으로 정의된 스케줄에 따라 워크플로우를 자동 실행한다. APScheduler 기반 스케줄러가 등록된 Cron 잡을 관리하며, 자연어 → Cron 변환(LLM 기반), 타임존 처리, 중복 실행 방지, 미스파이어(misfire) 복구를 제공한다.

> LOCK (기존 명세 §4(5종) + STEP7-N N-003(+2종) / LOCK-WF-06): Time(cron), Event(이벤트), Condition(조건), Webhook(웹훅), Manual(수동), Conversation(대화 기반), Ambient(앰비언트) — 7유형 트리거 체계

---

## 2. 핵심 제약 (LOCK)

> LOCK (기존 명세 §4(5종) + STEP7-N N-003(+2종) / LOCK-WF-06): Time(cron), Event(이벤트), Condition(조건), Webhook(웹훅), Manual(수동), Conversation(대화 기반), Ambient(앰비언트) — 7유형 트리거 체계

> LOCK (가이드 R-07-2 / LOCK-WF-03): Human Approval 타임아웃 = 10분 (600초)

---

## 3. 입력 스키마

```typescript
interface TimeTriggerConfig {
  type: "time";
  trigger_id: string;                  // UUID v7
  workflow_id: string;                 // 대상 워크플로우 ID

  // --- Cron 설정 ---
  cron_expression: string;             // 5-field cron: "0 9 * * 1-5"
  timezone: string;                    // IANA 타임존 (기본: "Asia/Seoul")

  // --- 실행 범위 ---
  start_date?: string;                 // ISO 8601 시작일 (null = 즉시)
  end_date?: string;                   // ISO 8601 종료일 (null = 무한)
  max_executions?: number;             // 최대 실행 횟수 (null = 무한)

  // --- 중복 방지 ---
  overlap_policy: "skip" | "queue" | "allow";
  // skip: 이전 실행 진행 중이면 스킵
  // queue: 이전 실행 완료 후 즉시 실행
  // allow: 동시 실행 허용

  // --- 미스파이어 ---
  misfire_grace_seconds: number;       // 기본 300 (5분)
  misfire_policy: "run_once" | "skip" | "run_all";

  // --- 메타데이터 ---
  enabled: boolean;                    // 활성화 여부
  description?: string;                // 트리거 설명
  created_at: string;                  // ISO 8601
  updated_at: string;
}
```

### 3.1 Cron 표현식 규칙

| 필드 | 범위 | 특수문자 |
|------|------|---------|
| 분 (minute) | 0-59 | `*`, `,`, `-`, `/` |
| 시 (hour) | 0-23 | `*`, `,`, `-`, `/` |
| 일 (day of month) | 1-31 | `*`, `,`, `-`, `/` |
| 월 (month) | 1-12 | `*`, `,`, `-`, `/` |
| 요일 (day of week) | 0-6 (0=일) | `*`, `,`, `-`, `/` |

---

## 4. 자연어 → Cron 변환

### 4.1 변환 파이프라인

```
[자연어 스케줄 입력]
    │
    ▼
[Phase 1: 패턴 매칭] ─── 정규식 기반 빈출 패턴 직접 변환
    │  매칭 성공 → cron 후보 생성
    │  매칭 실패 → Phase 2
    ▼
[Phase 2: LLM 파싱] ─── 프롬프트 기반 자연어 → cron 변환
    │  structured output → cron 후보 생성
    ▼
[Phase 3: 검증]
    │  문법 검증 + 의미 검증 (과도한 빈도 경고)
    ▼
[cron_expression 확정]
```

### 4.2 빈출 패턴 직접 매핑

```python
# cron_pattern_map.py
NL_CRON_PATTERNS: dict[str, str] = {
    # 일간
    r"매일\s*(아침\s*)?(\d{1,2})시": "0 {hour} * * *",
    r"매일\s*오전\s*(\d{1,2})시": "0 {hour} * * *",
    r"매일\s*오후\s*(\d{1,2})시": "0 {hour+12} * * *",

    # 주간
    r"매주\s*(월|화|수|목|금|토|일)요일": "0 0 * * {dow}",
    r"평일\s*(오전\s*)?(\d{1,2})시": "0 {hour} * * 1-5",
    r"주말\s*(오전\s*)?(\d{1,2})시": "0 {hour} * * 0,6",

    # 월간
    r"매월\s*(\d{1,2})일": "0 0 {day} * *",
    r"매달\s*(\d{1,2})일,?\s*(\d{1,2})일": "0 0 {day1},{day2} * *",

    # 간격
    r"(\d+)분마다": "*/{min} * * * *",
    r"(\d+)시간마다": "0 */{hour} * * *",
    r"매시간": "0 * * * *",
}

DOW_MAP = {"일": 0, "월": 1, "화": 2, "수": 3, "목": 4, "금": 5, "토": 6}
```

### 4.3 LLM 프롬프트 (Phase 2)

```python
NL_TO_CRON_PROMPT = """
사용자의 자연어 스케줄 설명을 5-field cron 표현식으로 변환하라.

## 규칙
- 5-field cron: minute hour day_of_month month day_of_week
- day_of_week: 0=일, 1=월, ..., 6=토
- 타임존은 별도 처리하므로 UTC 기준 아님 (로컬 시간 그대로)
- 변환 불가능하면 error 필드에 사유 기술

## 입력
"{user_input}"

## 출력 (JSON)
{
  "cron": "<cron expression>",
  "description": "<한국어 해석>",
  "error": null | "<에러 사유>"
}
"""
```

### 4.4 검증 규칙

```python
class CronValidator:
    """Cron 표현식 문법·의미 검증"""

    MAX_EXECUTIONS_PER_HOUR = 60     # 분당 1회 = 시간당 60회 상한
    MIN_INTERVAL_SECONDS = 60        # 최소 간격 1분

    def validate(self, cron_expr: str) -> ValidationResult:
        errors, warnings = [], []

        # V-1: 문법 검증 (5-field)
        if not self._is_valid_syntax(cron_expr):
            errors.append("Cron 표현식 문법 오류")

        # V-2: 과도한 빈도 경고
        interval = self._estimate_min_interval(cron_expr)
        if interval < self.MIN_INTERVAL_SECONDS:
            errors.append(f"최소 간격 {self.MIN_INTERVAL_SECONDS}초 미만")
        elif interval < 300:
            warnings.append(f"높은 실행 빈도: 약 {interval}초 간격")

        # V-3: 불가능 스케줄 (예: 2월 31일)
        if self._has_impossible_date(cron_expr):
            warnings.append("실행되지 않는 날짜 조합 포함")

        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
```

---

## 5. 평가 로직 (스케줄러)

### 5.1 APScheduler 기반 아키텍처

```python
# time_trigger_scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

class TimeTriggerScheduler:
    """APScheduler 기반 Time 트리거 스케줄러"""

    def __init__(self, db_url: str, event_bus: EventBus):
        self.event_bus = event_bus
        self.scheduler = AsyncIOScheduler(
            jobstores={"default": SQLAlchemyJobStore(url=db_url)},
            job_defaults={
                "coalesce": True,           # 미스파이어 시 1회만 실행
                "max_instances": 1,          # overlap_policy="skip" 기본
                "misfire_grace_time": 300,   # 5분 grace period
            },
        )

    async def register(self, config: TimeTriggerConfig) -> str:
        """트리거 등록 → APScheduler Job 생성"""
        trigger = CronTrigger.from_crontab(
            config.cron_expression,
            timezone=config.timezone,
        )

        job = self.scheduler.add_job(
            func=self._fire_trigger,
            trigger=trigger,
            id=config.trigger_id,
            kwargs={"config": config},
            start_date=config.start_date,
            end_date=config.end_date,
            max_instances=self._overlap_to_max_instances(config.overlap_policy),
            misfire_grace_time=config.misfire_grace_seconds,
            replace_existing=True,
        )
        return job.id

    async def _fire_trigger(self, config: TimeTriggerConfig):
        """트리거 발화 → EventBus 게시 → 워크플로우 실행 큐 등록"""
        # 1. max_executions 검사
        if config.max_executions is not None:
            count = await self._get_execution_count(config.trigger_id)
            if count >= config.max_executions:
                await self.unregister(config.trigger_id)
                return

        # 2. 이벤트 생성 + 발행
        now = datetime.now(ZoneInfo(config.timezone))
        event = TriggerEvent(
            trigger_id=config.trigger_id,
            trigger_type="time",
            workflow_id=config.workflow_id,
            fired_at=now.isoformat(),
            payload={
                "cron": config.cron_expression,
                "scheduled_at": now.isoformat(),       # 원래 예정 시각
                "misfire": False,                      # 미스파이어 여부
                "execution_number": (count if config.max_executions is not None else await self._get_execution_count(config.trigger_id)) + 1,
            },
        )
        await self.event_bus.publish("schedule", event)

    async def unregister(self, trigger_id: str):
        """트리거 해제"""
        self.scheduler.remove_job(trigger_id)

    async def pause(self, trigger_id: str):
        """트리거 일시 중지"""
        self.scheduler.pause_job(trigger_id)

    async def resume(self, trigger_id: str):
        """트리거 재개"""
        self.scheduler.resume_job(trigger_id)

    def _overlap_to_max_instances(self, policy: str) -> int:
        return {"skip": 1, "queue": 1, "allow": 3}[policy]
```

### 5.2 미스파이어(Misfire) 복구

| misfire_policy | 동작 | 사용 케이스 |
|---------------|------|-----------|
| `run_once` | 놓친 실행을 1회만 즉시 실행 (APScheduler coalesce=True) | 일일 리포트 (1회 실행이면 충분) |
| `skip` | 놓친 실행 무시, 다음 스케줄까지 대기 | 실시간성 낮은 알림 |
| `run_all` | 놓친 실행 횟수만큼 순차 실행 (coalesce=False) | 결제 처리 등 정확한 실행 필요 |

미스파이어 판정 기준:
- `misfire_grace_seconds` 이내: 미스파이어 정책 적용
- `misfire_grace_seconds` 초과: 자동 스킵 + 로그 경고

### 5.3 중복 실행 방지

```python
async def _check_overlap(self, config: TimeTriggerConfig) -> bool:
    """이전 실행이 진행 중인지 확인"""
    running = await self._get_running_executions(config.workflow_id)
    if not running:
        return False  # 중복 없음

    match config.overlap_policy:
        case "skip":
            logger.info(f"Skipping trigger {config.trigger_id}: workflow already running")
            return True   # 스킵
        case "queue":
            await self._enqueue_pending(config)
            return True   # 큐에 등록 후 현재 발화 스킵
        case "allow":
            return False  # 동시 실행 허용
```

---

## 6. 트리거 이벤트 스키마

```typescript
interface TriggerEvent {
  event_id: string;                    // UUID v7
  trigger_id: string;                  // 트리거 ID
  trigger_type: "time";                // 트리거 유형
  workflow_id: string;                 // 대상 워크플로우 ID
  fired_at: string;                    // ISO 8601 발화 시각
  payload: {
    cron: string;                      // 실행된 cron 표현식
    scheduled_at: string;              // 원래 예정 시각
    misfire: boolean;                  // 미스파이어 여부
    execution_number: number;          // 누적 실행 횟수
  };
}
```

---

## 7. 관리 API

### 7.1 CRUD 인터페이스

```python
class TimeTriggerManager:
    """Time 트리거 CRUD + 상태 관리"""

    async def create(self, config: TimeTriggerConfig) -> TriggerResult:
        """트리거 생성 + 스케줄러 등록"""
        validated = CronValidator().validate(config.cron_expression)
        if not validated.valid:
            return TriggerResult(success=False, errors=validated.errors)

        await self.store.save(config)
        await self.scheduler.register(config)
        return TriggerResult(success=True, trigger_id=config.trigger_id)

    async def update(self, trigger_id: str, updates: dict) -> TriggerResult:
        """트리거 설정 변경 (cron, timezone, overlap_policy 등)"""
        config = await self.store.get(trigger_id)
        config = config.copy(update=updates)

        if "cron_expression" in updates:
            validated = CronValidator().validate(config.cron_expression)
            if not validated.valid:
                return TriggerResult(success=False, errors=validated.errors)

        await self.store.save(config)
        await self.scheduler.register(config)  # replace_existing=True
        return TriggerResult(success=True, trigger_id=trigger_id)

    async def delete(self, trigger_id: str) -> TriggerResult:
        """트리거 삭제"""
        await self.scheduler.unregister(trigger_id)
        await self.store.delete(trigger_id)
        return TriggerResult(success=True, trigger_id=trigger_id)

    async def get_next_fires(self, trigger_id: str, count: int = 5) -> list[str]:
        """다음 N회 예정 실행 시각 조회"""
        config = await self.store.get(trigger_id)
        trigger = CronTrigger.from_crontab(config.cron_expression, timezone=config.timezone)
        fires = []
        next_time = datetime.now(ZoneInfo(config.timezone))
        for _ in range(count):
            next_time = trigger.get_next_fire_time(None, next_time)
            fires.append(next_time.isoformat())
            next_time += timedelta(seconds=1)
        return fires
```

---

## 8. 자연어 → Cron 예시

| 자연어 입력 | 변환 결과 | 해석 |
|------------|----------|------|
| "매일 아침 9시" | `0 9 * * *` | 매일 09:00 |
| "평일 오전 9시" | `0 9 * * 1-5` | 월~금 09:00 |
| "매주 월요일 오후 2시" | `0 14 * * 1` | 월요일 14:00 |
| "매달 1일, 15일" | `0 0 1,15 * *` | 매월 1일, 15일 00:00 |
| "2시간마다" | `0 */2 * * *` | 짝수 시간 정각 |
| "10분마다" | `*/10 * * * *` | 매 10분 |
| "매일 9시, 18시" | `0 9,18 * * *` | 매일 09:00, 18:00 |
| "매주 금요일 오후 5시" | `0 17 * * 5` | 금요일 17:00 |

---

## 9. 교차참조

| 참조 대상 | 관계 |
|----------|------|
| `execution_engine.md` | 트리거 발화 → 워크플로우 실행 큐 등록 (LOCK-WF-05: 최대 동시 10) |
| `event_trigger.md` | EventBus "schedule" 채널 공유 |
| `dag_architecture.md` | 실행 대상 워크플로우 DAG 정의 참조 |
| `intent_parsing.md` | 자연어 스케줄 파싱 시 IntentCategory "scheduled_task" 연동 |
| 부록 §B.1 | Time 트리거 설정 정본 |

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-04-09 | v1.0 | L3 초판 작성 (N-003a EXTEND, APScheduler 기반 스케줄러, NL→Cron 변환, 미스파이어 복구) |
