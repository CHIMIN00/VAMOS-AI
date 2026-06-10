# breathing_exercises.md — 호흡법 가이드 엔진

> **P-ID**: P-004-b
> **V단계**: V1
> **상태**: EXTEND
> **L3 완성**: 2026-04-10
> **정본 소유자**: sot 2/3-6_Health-Wellness-EmotionAI/04_stress-management/

---

## 교차 참조 블록

| 참조 문서 | 위치 | 참조 내용 |
|----------|------|----------|
| 종합계획서 §3.4 | LOCK-HW-07 | 호흡법 3패턴 타이밍 (4-7-8, Box, 횡격막) |
| 종합계획서 §6.4 | 매핑 테이블 | P-004-b 배정 |
| 종합계획서 §4 | R-09-1~R-09-7 | 도메인 전용 거버넌스 규칙 |
| 상세명세 §5 | §5.2 호흡법 | 기존 명세 (레거시 참조) |
| STEP7-P | P-004 | 스트레스 관리 원본 체크리스트 |
| AUTHORITY_CHAIN.md | §1~§5 | 정본 계층 및 충돌 해결 |
| 04_stress-management/stress_detection.md | §7 중재 라우팅 | 호흡법 라우팅 경로 |
| 06_ethics-privacy/ethics_framework.md | §3 7원칙 | 비의료 면책 적용 |

---

## 1. 개요

본 문서는 VAMOS 호흡법 가이드 엔진을 L3 구현 즉시 투입 가능 수준으로 정의한다. LOCK-HW-07에 따른 3가지 호흡 패턴(4-7-8, Box, 횡격막)의 정확한 타이밍 제어, 타이머 UI 인터페이스, 완료 기록 시스템을 구현한다.

**입력**: 스트레스 수준 + 사용자 선호도
**출력**: `BreathingSession { pattern, phases, timer_sequence, completion_record }`

---

## 2. LOCK 인용

> LOCK (LOCK-HW-07, STEP7-P P-004/기존 명세 §5): 4-7-8(흡4초-지7초-호8초), Box(4-4-4-4), 횡격막(4-2-6)

> LOCK (LOCK-HW-04, STEP7-P 윤리원칙): "VAMOS는 의료 서비스가 아닙니다" 모든 건강 관련 응답에 포함

---

## 3. 호흡 패턴 3종 정의

### 3.1 4-7-8 호흡법 (Relaxing Breath)

> LOCK-HW-07 전수 적용

| 단계 | 동작 | 지속 시간(초) | 가이드 메시지 |
|------|------|-------------|-------------|
| Phase 1 | 흡기 (Inhale) | 4초 | "코로 천천히 숨을 들이마세요..." |
| Phase 2 | 정지 (Hold) | 7초 | "숨을 편안하게 참아주세요..." |
| Phase 3 | 호기 (Exhale) | 8초 | "입으로 천천히 내쉬세요..." |
| **1 사이클 합계** | | **19초** | |

**권장 반복**: 4사이클 (약 76초)
**적용 상황**: 수면 전, 불안 완화, 전반적 이완
**난이도**: 초급~중급

### 3.2 Box 호흡법 (Box Breathing)

> LOCK-HW-07 전수 적용

| 단계 | 동작 | 지속 시간(초) | 가이드 메시지 |
|------|------|-------------|-------------|
| Phase 1 | 흡기 (Inhale) | 4초 | "코로 숨을 들이마세요..." |
| Phase 2 | 정지 (Hold) | 4초 | "숨을 참아주세요..." |
| Phase 3 | 호기 (Exhale) | 4초 | "천천히 내쉬세요..." |
| Phase 4 | 정지 (Hold) | 4초 | "잠시 머물러주세요..." |
| **1 사이클 합계** | | **16초** | |

**권장 반복**: 4~6사이클 (약 64~96초)
**적용 상황**: 집중력 회복, 급성 스트레스 관리, 업무 중 사용
**난이도**: 초급

### 3.3 횡격막 호흡법 (Diaphragmatic Breathing)

> LOCK-HW-07 전수 적용

| 단계 | 동작 | 지속 시간(초) | 가이드 메시지 |
|------|------|-------------|-------------|
| Phase 1 | 흡기 (Inhale) | 4초 | "배를 부풀리면서 코로 들이마세요..." |
| Phase 2 | 정지 (Hold) | 2초 | "잠깐 머물러주세요..." |
| Phase 3 | 호기 (Exhale) | 6초 | "배를 당기면서 천천히 내쉬세요..." |
| **1 사이클 합계** | | **12초** | |

**권장 반복**: 5~10사이클 (약 60~120초)
**적용 상황**: 깊은 이완, 복부 긴장 완화, 장기 습관화
**난이도**: 초급~중급 (복식호흡 인지 필요)

---

## 4. 호흡 패턴 선택 알고리즘

### 4.1 스트레스 수준 기반 자동 선택

```python
def select_breathing_pattern(
    stress_level: StressLevel,
    user_preference: Optional[str] = None,
    time_available_minutes: float = 5.0
) -> BreathingPattern:
    """
    스트레스 수준과 사용자 선호도에 따라 호흡 패턴을 선택한다.
    LOCK-HW-07: 3패턴 타이밍 정확히 준수.
    """
    if user_preference and user_preference in VALID_PATTERNS:
        return PATTERNS[user_preference]

    if stress_level == StressLevel.MILD:
        return PATTERNS["4-7-8"]  # 기본 이완
    elif stress_level == StressLevel.MODERATE:
        return PATTERNS["box"]    # 빠른 안정
    elif stress_level in (StressLevel.HIGH, StressLevel.SEVERE):
        return PATTERNS["diaphragmatic"]  # 깊은 이완
    else:
        return PATTERNS["4-7-8"]  # 기본값
```

### 4.2 패턴별 권장 매핑

| 스트레스 수준 | 1순위 패턴 | 2순위 패턴 | 사유 |
|-------------|----------|----------|------|
| MILD | 4-7-8 | Box | 기본 이완, 수면 전 사용 |
| MODERATE | Box | 4-7-8 | 빠른 안정, 업무 중 사용 가능 |
| HIGH | 횡격막 | Box | 깊은 이완 필요 |
| SEVERE | 횡격막 + Box 병행 | - | 위기 프로토콜 병행 |

---

## 5. 타이머 UI 인터페이스

### 5.1 타이머 상태 모델

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class TimerState(str, Enum):
    IDLE = "IDLE"
    INHALE = "INHALE"
    HOLD = "HOLD"
    EXHALE = "EXHALE"
    PAUSE = "PAUSE"       # 사이클 간 휴식
    COMPLETED = "COMPLETED"

@dataclass
class BreathingTimerEvent:
    """타이머 이벤트 (UI에 전달)."""
    state: TimerState
    remaining_seconds: float
    total_seconds: float
    current_cycle: int
    total_cycles: int
    guide_message: str
    progress_ratio: float  # 0.0 ~ 1.0
```

### 5.2 타이머 엔진

```python
@dataclass
class BreathingPattern:
    """호흡 패턴 정의 (LOCK-HW-07 준수)."""
    name: str
    phases: list[tuple[TimerState, float]]  # (상태, 초)
    recommended_cycles: int

# LOCK-HW-07 정확한 타이밍 정의
PATTERNS = {
    "4-7-8": BreathingPattern(
        name="4-7-8 호흡법",
        phases=[(TimerState.INHALE, 4.0), (TimerState.HOLD, 7.0), (TimerState.EXHALE, 8.0)],
        recommended_cycles=4
    ),
    "box": BreathingPattern(
        name="Box 호흡법",
        phases=[
            (TimerState.INHALE, 4.0), (TimerState.HOLD, 4.0),
            (TimerState.EXHALE, 4.0), (TimerState.HOLD, 4.0)
        ],
        recommended_cycles=5
    ),
    "diaphragmatic": BreathingPattern(
        name="횡격막 호흡법",
        phases=[(TimerState.INHALE, 4.0), (TimerState.HOLD, 2.0), (TimerState.EXHALE, 6.0)],
        recommended_cycles=8
    ),
}

async def run_breathing_session(
    pattern: BreathingPattern,
    cycles: int,
    on_event: Callable[[BreathingTimerEvent], Awaitable[None]]
) -> BreathingCompletionRecord:
    """
    호흡 세션을 실행하고 타이머 이벤트를 UI에 전달한다.
    Big-O: O(C × P) — C=사이클 수, P=페이즈 수 (상수, 최대 4×10)
    """
    for cycle in range(1, cycles + 1):
        for state, duration in pattern.phases:
            elapsed = 0.0
            while elapsed < duration:
                remaining = duration - elapsed
                await on_event(BreathingTimerEvent(
                    state=state,
                    remaining_seconds=remaining,
                    total_seconds=duration,
                    current_cycle=cycle,
                    total_cycles=cycles,
                    guide_message=GUIDE_MESSAGES[state],
                    progress_ratio=elapsed / duration
                ))
                await asyncio.sleep(0.1)  # 100ms 틱
                elapsed += 0.1

    return BreathingCompletionRecord(
        pattern_name=pattern.name,
        cycles_completed=cycles,
        total_duration_seconds=sum(d for _, d in pattern.phases) * cycles,
        completed_at=datetime.now()
    )
```

---

## 6. 완료 기록 시스템

### 6.1 완료 기록 자료 구조

```python
@dataclass
class BreathingCompletionRecord:
    """호흡 세션 완료 기록."""
    pattern_name: str                # 사용한 패턴명
    cycles_completed: int            # 완료 사이클 수
    total_duration_seconds: float    # 총 소요 시간
    completed_at: datetime           # 완료 시각
    pre_stress_score: Optional[float] = None   # 수행 전 스트레스
    post_stress_score: Optional[float] = None  # 수행 후 스트레스
    user_feedback: Optional[int] = None        # 1-5 만족도
    early_exit: bool = False         # 조기 종료 여부
    exit_cycle: Optional[int] = None # 조기 종료 사이클
```

### 6.2 효과 측정

```python
def measure_breathing_effect(record: BreathingCompletionRecord) -> dict:
    """호흡법 수행 전후 스트레스 점수 변화를 측정한다."""
    if record.pre_stress_score is not None and record.post_stress_score is not None:
        reduction = record.pre_stress_score - record.post_stress_score
        reduction_pct = (reduction / record.pre_stress_score) * 100
        return {
            "pre_score": record.pre_stress_score,
            "post_score": record.post_stress_score,
            "reduction": reduction,
            "reduction_pct": reduction_pct,
            "effective": reduction > 5.0  # 5점 이상 감소 시 효과적
        }
    return {"effective": None, "reason": "pre/post score unavailable"}
```

---

## 7. R-01-7 로깅 구조

```json
{
  "log_type": "R-01-7",
  "module": "breathing_exercises",
  "event": "breathing_session_complete",
  "timestamp": "2026-04-10T14:30:00Z",
  "data": {
    "session_id": "sess_breath_001",
    "pattern": {
      "name": "4-7-8 호흡법",
      "phases": [
        {"state": "INHALE", "duration_sec": 4},
        {"state": "HOLD", "duration_sec": 7},
        {"state": "EXHALE", "duration_sec": 8}
      ]
    },
    "cycles_completed": 4,
    "total_duration_seconds": 76,
    "effect": {
      "pre_stress_score": 55.0,
      "post_stress_score": 38.0,
      "reduction": 17.0,
      "reduction_pct": 30.9
    },
    "privacy": {
      "level": "PRIVATE",
      "retention_days": 180
    }
  }
}
```

---

## 8. Phase 2 테스트 시나리오

| # | 시나리오 | 입력 | 기대 결과 | 검증 항목 |
|---|---------|------|----------|----------|
| T-1 | 4-7-8 타이밍 정확성 | 4-7-8 패턴 실행 | 1사이클 = 정확히 19초 | LOCK-HW-07 타이밍 |
| T-2 | Box 타이밍 정확성 | Box 패턴 실행 | 1사이클 = 정확히 16초 | LOCK-HW-07 타이밍 |
| T-3 | 횡격막 타이밍 정확성 | 횡격막 패턴 실행 | 1사이클 = 정확히 12초 | LOCK-HW-07 타이밍 |
| T-4 | MILD 자동 선택 | stress_level=MILD | 4-7-8 패턴 선택 | 자동 선택 로직 |
| T-5 | MODERATE 자동 선택 | stress_level=MODERATE | Box 패턴 선택 | 자동 선택 로직 |
| T-6 | 사용자 선호도 우선 | preference="box", level=MILD | Box 패턴 선택 | 선호도 오버라이드 |
| T-7 | 조기 종료 기록 | 3/5 사이클 후 종료 | early_exit=True, exit_cycle=3 | 조기 종료 처리 |
| T-8 | 효과 측정 | pre=55, post=38 | reduction=17, 효과적 | 전후 비교 |
| T-9 | 타이머 이벤트 정합성 | 4-7-8 실행 중 이벤트 | progress_ratio 0.0→1.0 | 이벤트 순서 |
| T-10 | 비의료 면책 포함 | 가이드 메시지 | LOCK-HW-04 포함 | 면책 문구 |
| T-11 | 전체 세션 완료 기록 | 4사이클 완료 | CompletionRecord 정합 | 기록 무결성 |
| T-12 | 3패턴 전수 테스트 | 3패턴 순차 실행 | 각각 정확한 타이밍 | LOCK-HW-07 전수 |

---

## 9. 비의료 면책

> LOCK (LOCK-HW-04, STEP7-P 윤리원칙): "VAMOS는 의료 서비스가 아닙니다" 모든 건강 관련 응답에 포함

호흡법은 일반적인 이완 기법이며 의학적 치료를 대체하지 않습니다. 호흡곤란, 과호흡, 기저 호흡기 질환이 있는 경우 의료 전문가와 상담하시기 바랍니다.
