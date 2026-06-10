# grounding_technique.md — 5-4-3-2-1 그라운딩 기법 엔진

> **P-ID**: P-004-c
> **V단계**: V1
> **상태**: EXTEND
> **L3 완성**: 2026-04-10
> **정본 소유자**: sot 2/3-6_Health-Wellness-EmotionAI/04_stress-management/

---

## 교차 참조 블록

| 참조 문서 | 위치 | 참조 내용 |
|----------|------|----------|
| 종합계획서 §3.4 | LOCK-HW-08 | 그라운딩 5-4-3-2-1 기법 |
| 종합계획서 §6.4 | 매핑 테이블 | P-004-c 배정 |
| 종합계획서 §4 | R-09-1~R-09-7 | 도메인 전용 거버넌스 규칙 |
| 상세명세 §5 | §5.3 그라운딩 | 기존 명세 (레거시 참조) |
| STEP7-P | P-004 | 스트레스 관리 원본 체크리스트 |
| AUTHORITY_CHAIN.md | §1~§5 | 정본 계층 및 충돌 해결 |
| 04_stress-management/stress_detection.md | §7 중재 라우팅 | 그라운딩 라우팅 경로 |
| 04_stress-management/breathing_exercises.md | §3 호흡법 | 병행 중재 |
| 06_ethics-privacy/ethics_framework.md | §3 7원칙 | 비의료 면책 적용 |

---

## 1. 개요

본 문서는 VAMOS 5-4-3-2-1 그라운딩 기법 가이드 대화 엔진을 L3 구현 즉시 투입 가능 수준으로 정의한다. LOCK-HW-08에 따른 5감각 기반 그라운딩 기법(5가지보기-4가지만지기-3가지듣기-2가지맡기-1가지맛보기)의 대화형 가이드를 구현한다. 해리/패닉/불안 상황에서 현재 순간으로 되돌아오도록 돕는 감각 집중 기법이다.

**입력**: 스트레스 수준 + 사용자 상태 (해리/패닉/불안 구분)
**출력**: `GroundingSession { steps, user_responses, completion_record }`

---

## 2. LOCK 인용

> LOCK (LOCK-HW-08, 기존 명세 §5): 5가지보기-4가지만지기-3가지듣기-2가지맡기-1가지맛보기

> LOCK (LOCK-HW-04, STEP7-P 윤리원칙): "VAMOS는 의료 서비스가 아닙니다" 모든 건강 관련 응답에 포함

---

## 3. 5-4-3-2-1 기법 상세 정의

### 3.1 5단계 감각 집중 순서

> LOCK-HW-08 전수 적용

| 단계 | 감각 | 개수 | 질문 | 목적 |
|------|------|------|------|------|
| Step 5 | 시각 (보기) | 5가지 | "지금 주변에서 보이는 것 5가지를 말해주세요" | 시각적 현재 인식 |
| Step 4 | 촉각 (만지기) | 4가지 | "지금 만질 수 있는 것 4가지를 말해주세요" | 신체 감각 연결 |
| Step 3 | 청각 (듣기) | 3가지 | "지금 들리는 소리 3가지를 말해주세요" | 청각적 현재 인식 |
| Step 2 | 후각 (맡기) | 2가지 | "지금 맡을 수 있는 냄새 2가지를 말해주세요" | 후각적 현재 인식 |
| Step 1 | 미각 (맛보기) | 1가지 | "지금 맛볼 수 있는 것 1가지를 말해주세요" | 미각적 현재 인식 |

### 3.2 숫자 카운트다운 설계 의도

5→4→3→2→1 감소 패턴은 의도적 설계이다:
- **점진적 집중 심화**: 많은 항목(5)에서 적은 항목(1)으로 수렴하며 집중력이 한 점으로 모인다
- **인지 부하 감소**: 불안/패닉 상태에서 처리 가능한 인지 부하가 점진적으로 줄어든다
- **완료 가능성**: 감소하는 숫자가 진행감과 달성감을 제공한다

---

## 4. 가이드 대화 엔진

### 4.1 대화 상태 모델

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime

class GroundingPhase(str, Enum):
    INTRO = "INTRO"
    SEE_5 = "SEE_5"
    TOUCH_4 = "TOUCH_4"
    HEAR_3 = "HEAR_3"
    SMELL_2 = "SMELL_2"
    TASTE_1 = "TASTE_1"
    CLOSING = "CLOSING"
    COMPLETED = "COMPLETED"

GROUNDING_STEPS = [
    GroundingStep(
        phase=GroundingPhase.SEE_5,
        sense="시각",
        count=5,
        prompt="지금 주변을 천천히 둘러보세요. 보이는 것 5가지를 하나씩 말해주세요.",
        encouragements=[
            "좋아요, 하나 찾으셨네요.",
            "잘하고 계세요. 다음은 무엇이 보이나요?",
            "아주 잘하고 있어요. 계속해볼까요?",
        ]
    ),
    GroundingStep(
        phase=GroundingPhase.TOUCH_4,
        sense="촉각",
        count=4,
        prompt="이번에는 만질 수 있는 것 4가지를 느껴보세요. 질감이나 온도도 좋아요.",
        encouragements=[
            "좋아요, 그 느낌에 집중해보세요.",
            "잘하고 계세요. 또 무엇을 느끼시나요?",
        ]
    ),
    GroundingStep(
        phase=GroundingPhase.HEAR_3,
        sense="청각",
        count=3,
        prompt="이제 조용히 귀를 기울여보세요. 들리는 소리 3가지를 말해주세요.",
        encouragements=[
            "잘 들리시나요? 아주 작은 소리도 괜찮아요.",
            "좋아요, 소리에 집중하고 계시네요.",
        ]
    ),
    GroundingStep(
        phase=GroundingPhase.SMELL_2,
        sense="후각",
        count=2,
        prompt="코로 숨을 깊이 들이마셔보세요. 냄새 2가지를 찾아보세요.",
        encouragements=[
            "좋아요, 냄새에 집중해보세요.",
        ]
    ),
    GroundingStep(
        phase=GroundingPhase.TASTE_1,
        sense="미각",
        count=1,
        prompt="마지막으로, 지금 입안에서 느껴지는 맛 1가지를 말해주세요. 물을 한 모금 마셔도 좋아요.",
        encouragements=[]
    ),
]
```

### 4.2 대화 흐름 엔진

```python
class GroundingEngine:
    """5-4-3-2-1 그라운딩 대화 엔진."""

    def __init__(self):
        self.current_phase = GroundingPhase.INTRO
        self.responses: dict[GroundingPhase, list[str]] = {}
        self.start_time: Optional[datetime] = None

    def start(self) -> str:
        """세션 시작 인트로 메시지."""
        self.start_time = datetime.now()
        self.current_phase = GroundingPhase.INTRO
        return (
            "지금 이 순간으로 돌아오는 연습을 해볼까요? "
            "5-4-3-2-1 그라운딩 기법을 안내해 드릴게요. "
            "편안하게 자리에 앉아주세요.\n\n"
            "VAMOS는 의료 서비스가 아닙니다. "
            "심각한 증상이 지속되면 전문가 상담을 권합니다."
        )

    def advance(self, user_input: str) -> str:
        """
        사용자 응답을 처리하고 다음 단계로 진행한다.
        Big-O: O(1) — 고정 5단계 순회
        """
        if self.current_phase == GroundingPhase.INTRO:
            self.current_phase = GroundingPhase.SEE_5
            return GROUNDING_STEPS[0].prompt

        step_index = list(GroundingPhase).index(self.current_phase) - 1
        current_step = GROUNDING_STEPS[step_index]

        # 응답 기록
        if self.current_phase not in self.responses:
            self.responses[self.current_phase] = []
        self.responses[self.current_phase].append(user_input)

        # 필요 개수 충족 확인
        if len(self.responses[self.current_phase]) >= current_step.count:
            # 다음 단계로 진행
            next_phases = list(GroundingPhase)
            next_index = next_phases.index(self.current_phase) + 1
            if next_index >= len(next_phases) - 2:  # TASTE_1(마지막 단계) 완료 → COMPLETED (GROUNDING_STEPS index OOB 방지)
                self.current_phase = GroundingPhase.COMPLETED
                return self._closing_message()
            self.current_phase = next_phases[next_index]
            return GROUNDING_STEPS[step_index + 1].prompt
        else:
            # 격려 메시지
            remaining = current_step.count - len(self.responses[self.current_phase])
            enc_idx = min(
                len(self.responses[self.current_phase]) - 1,
                len(current_step.encouragements) - 1
            )
            encouragement = current_step.encouragements[enc_idx] if current_step.encouragements else "좋아요."
            return f"{encouragement} (앞으로 {remaining}개 더)"

    def _closing_message(self) -> str:
        return (
            "수고하셨어요. 5가지 감각을 통해 지금 이 순간에 머물러 보셨습니다. "
            "지금 기분이 조금 나아지셨나요? "
            "언제든 이 방법을 다시 사용하실 수 있어요."
        )

    def get_completion_record(self) -> GroundingCompletionRecord:
        return GroundingCompletionRecord(
            responses=self.responses,
            total_duration_seconds=(datetime.now() - self.start_time).total_seconds(),
            completed_all_steps=self.current_phase == GroundingPhase.COMPLETED,
            completed_at=datetime.now()
        )
```

---

## 5. 데이터 모델

```python
@dataclass
class GroundingStep:
    """그라운딩 단계 정의."""
    phase: GroundingPhase
    sense: str
    count: int
    prompt: str
    encouragements: list[str]

@dataclass
class GroundingCompletionRecord:
    """그라운딩 세션 완료 기록."""
    responses: dict[str, list[str]]   # 단계별 사용자 응답
    total_duration_seconds: float     # 총 소요 시간
    completed_all_steps: bool         # 전 단계 완료 여부
    completed_at: datetime
    pre_stress_score: Optional[float] = None
    post_stress_score: Optional[float] = None
    early_exit_phase: Optional[str] = None
    disclaimer: str = "VAMOS는 의료 서비스가 아닙니다"
```

---

## 6. 세션 간 인터페이스

### 6.1 입력 (stress_detection.md → grounding_technique.md)

```python
# stress_detection.md §7 중재 라우팅에서 MODERATE 이상 시 호출
# StressInterventionRequest.assessment.level >= MODERATE
```

### 6.2 출력 (→ stress_detection.md 효과 기록)

```python
# GroundingCompletionRecord를 stress_detection에 피드백
# post_stress_score 측정 후 중재 효과 기록
```

---

## 7. R-01-7 로깅 구조

```json
{
  "log_type": "R-01-7",
  "module": "grounding_technique",
  "event": "grounding_session_complete",
  "timestamp": "2026-04-10T15:00:00Z",
  "data": {
    "session_id": "sess_ground_001",
    "technique": "5-4-3-2-1",
    "steps_completed": {
      "SEE_5": 5,
      "TOUCH_4": 4,
      "HEAR_3": 3,
      "SMELL_2": 2,
      "TASTE_1": 1
    },
    "total_items": 15,
    "completed_all_steps": true,
    "total_duration_seconds": 420,
    "effect": {
      "pre_stress_score": 60.0,
      "post_stress_score": 35.0,
      "reduction": 25.0
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
| T-1 | 5-4-3-2-1 전수 순서 | 전체 흐름 실행 | SEE→TOUCH→HEAR→SMELL→TASTE 순서 | LOCK-HW-08 순서 |
| T-2 | 5가지 보기 완료 | 5개 시각 응답 | SEE_5 → TOUCH_4 전환 | count=5 충족 |
| T-3 | 4가지 만지기 완료 | 4개 촉각 응답 | TOUCH_4 → HEAR_3 전환 | count=4 충족 |
| T-4 | 3가지 듣기 완료 | 3개 청각 응답 | HEAR_3 → SMELL_2 전환 | count=3 충족 |
| T-5 | 2가지 맡기 완료 | 2개 후각 응답 | SMELL_2 → TASTE_1 전환 | count=2 충족 |
| T-6 | 1가지 맛보기 완료 | 1개 미각 응답 | 세션 완료 | count=1 충족 |
| T-7 | 조기 종료 | TOUCH_4에서 중단 | early_exit_phase="TOUCH_4" | 조기 종료 기록 |
| T-8 | 격려 메시지 | 3/5 응답 후 | 격려 + "앞으로 2개 더" | 격려 로직 |
| T-9 | 효과 측정 | pre=60, post=35 | reduction=25 | 전후 비교 |
| T-10 | 비의료 면책 | 인트로 메시지 | LOCK-HW-04 포함 | 면책 문구 |
| T-11 | 전체 세션 기록 | 15항목 완료 | CompletionRecord 정합 | 기록 무결성 |
| T-12 | MODERATE 라우팅 | stress_level=MODERATE | 그라운딩 선택됨 | 라우팅 정합 |

---

## 9. 비의료 면책

> LOCK (LOCK-HW-04, STEP7-P 윤리원칙): "VAMOS는 의료 서비스가 아닙니다" 모든 건강 관련 응답에 포함

그라운딩 기법은 일시적 불안/해리 증상 완화를 위한 자가 관리 도구이며, PTSD, 공황장애 등 임상적 증상에 대한 의학적 치료를 대체하지 않습니다.
