# cbt_self_care.md — CBT 자가 관리 도구

> **P-ID**: P-020, P-020-a
> **V단계**: V1
> **상태**: P-020 EXTEND / P-020-a NEW
> **L3 완성**: 2026-04-10
> **정본 소유자**: sot 2/3-6_Health-Wellness-EmotionAI/04_stress-management/

---

## 교차 참조 블록

| 참조 문서 | 위치 | 참조 내용 |
|----------|------|----------|
| 종합계획서 §3.4 | LOCK-HW-01/04/09 | 감정 분류, 비의료 면책, 7원칙 |
| 종합계획서 §6.4 | 매핑 테이블 | P-020/P-020-a 배정 |
| 종합계획서 부록 §C | §C.1~§C.3 | CBT 인지왜곡 15유형, 감지 알고리즘, 대화 템플릿 |
| 종합계획서 §4 | R-09-1~R-09-7 | 도메인 전용 거버넌스 규칙 |
| STEP7-P | P-020 | CBT 자가관리 원본 체크리스트 |
| AUTHORITY_CHAIN.md | §1~§5 | 정본 계층 및 충돌 해결 |
| 06_ethics-privacy/cbt_distortion_taxonomy.md | §3~§5 | 인지왜곡 15유형 정본 (감지+대화 템플릿) |
| 06_ethics-privacy/ethics_framework.md | §3 7원칙 | 비진단/비조작/자율성 적용 |
| 01_emotion-recognition/text_emotion_analysis.md | §4 파이프라인 | 감정 분석 결과 입력 |
| 04_stress-management/stress_detection.md | §7 중재 라우팅 | CBT 라우팅 경로 |

---

## 1. 개요

본 문서는 VAMOS CBT(인지행동치료) 자가 관리 도구를 L3 구현 즉시 투입 가능 수준으로 정의한다. 부록 §C의 15개 인지왜곡 유형 감지와 연동하여, 인지 재구조화 4단계 대화(부록 §C.3)를 적용한다. 7원칙(LOCK-HW-09) 중 "비진단", "비조작", "자율성 존중"을 핵심 제약으로 적용한다.

**입력**: 사용자 텍스트 + 감정 분석 결과 (LOCK-HW-01)
**출력**: `CBTSessionResult { detected_distortions, restructuring_dialogue, completion_record }`

---

## 2. LOCK 인용

> LOCK (LOCK-HW-01, 기존 명세 §2/STEP7-P P-001): 기본7(기쁨,슬픔,분노,불안,놀람,혐오,중립)+세부5(피로,스트레스,좌절,열정,호기심)+차원2(arousal,valence)

> LOCK (LOCK-HW-04, STEP7-P 윤리원칙): "VAMOS는 의료 서비스가 아닙니다" 모든 건강 관련 응답에 포함

> LOCK (LOCK-HW-09, STEP7-P P-010): 비진단/프라이버시/투명성/전문가연결/비조작/자율성/기능끄기

---

## 3. 인지왜곡 15유형 연동 (P-020-a)

### 3.1 인지왜곡 감지 연동

> 부록 §C.1 15유형 전수 참조 (06_ethics-privacy/cbt_distortion_taxonomy.md 정본)

| # | 한국어명 | 영문 | 감지 키워드 패턴 예시 |
|---|---------|------|---------------------|
| 1 | 전부 아니면 전무 | All-or-Nothing Thinking | "완벽하지 않으면", "전부 아니면", "100% 아니면" |
| 2 | 과잉일반화 | Overgeneralization | "항상", "매번", "절대", "모든", "언제나" |
| 3 | 정신적 필터 | Mental Filter | "그것만", "오직", "~만 보여" |
| 4 | 긍정 격하 | Disqualifying the Positive | "운이 좋았을 뿐", "별거 아니" |
| 5 | 성급한 결론 - 독심술 | Mind Reading | "분명 ~할 거야", "~라고 생각할 거야" |
| 6 | 성급한 결론 - 점쟁이 오류 | Fortune Telling | "반드시 ~할 거야", "절대 안 될 거야" |
| 7 | 파국화/축소화 | Catastrophizing | "최악", "끝났", "인생이 망했" |
| 8 | 감정적 추론 | Emotional Reasoning | "느끼니까 ~인 거야", "불안하니까" |
| 9 | 당위 진술 | Should Statements | "~해야 해", "~해야만" |
| 10 | 낙인 찍기 | Labeling | "난 ~야", "나는 ~인 사람" |
| 11 | 개인화 | Personalization | "다 내 탓", "내가 ~해서" |
| 12 | 비난 | Blaming | "다 ~때문", "네가 ~해서" |
| 13 | 공정성 오류 | Fallacy of Fairness | "불공평", "내가 더 ~했는데" |
| 14 | 변화 기대 | Fallacy of Change | "~가 변하면", "~만 바뀌면" |
| 15 | 통제 오류 | Control Fallacy | "할 수 있는 게 없", "다 내가 해야" |

### 3.2 감지 파이프라인

> 부록 §C.2 감지 알고리즘 적용

```python
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class DetectedDistortion:
    """감지된 인지왜곡."""
    distortion_id: int           # 1-15
    distortion_name_kr: str
    distortion_name_en: str
    confidence: float            # 0.0-1.0
    source: str                  # "keyword" | "llm" | "combined"
    matched_text: str            # 매칭된 원문 부분
    restructuring_strategy: str  # 재구조화 전략

def detect_and_filter_distortions(
    user_text: str,
    context: list[str],
    emotion_result: Optional[dict] = None
) -> list[DetectedDistortion]:
    """
    부록 §C.2 3단계 파이프라인 적용.

    Stage 1: 키워드 패턴 매칭 (confidence 0.5)
    Stage 2: LLM 기반 의미 분석 (confidence 조정)
    Stage 3: 필터링 (confidence >= 0.4) + 정렬 (상위 3건)

    Big-O: O(P × K + L)
      P = 15 유형 (상수)
      K = 유형당 키워드 수 (평균 4, 상수)
      L = LLM 추론 1회 (상수 시간)
    => 실질적 O(1)
    """
    results = []

    # Stage 1: 키워드 패턴 매칭
    for distortion in DISTORTION_TAXONOMY_15:
        for pattern in distortion.keyword_patterns:
            if regex_match(pattern, user_text):
                results.append(DetectedDistortion(
                    distortion_id=distortion.id,
                    distortion_name_kr=distortion.name_kr,
                    distortion_name_en=distortion.name_en,
                    confidence=0.5,
                    source="keyword",
                    matched_text=extract_match(pattern, user_text),
                    restructuring_strategy=distortion.strategy
                ))
                break  # 유형당 1회 매칭

    # Stage 2: LLM 기반 의미 분석
    if results or _emotional_context_present(emotion_result):
        llm_result = llm_analyze_distortion(user_text, context)
        for r in results:
            if r.distortion_id in llm_result.confirmed:
                r.confidence = min(r.confidence + 0.3, 0.95)
                r.source = "combined"
            else:
                r.confidence = max(r.confidence - 0.2, 0.1)
        for new_id in llm_result.new_detections:
            # 범위/키 검증 (1..15 + map 존재) — malformed LLM 응답 IndexError/KeyError 방지
            if not (1 <= new_id <= 15 and new_id in llm_result.confidence_map and new_id in llm_result.evidence):
                continue
            d = DISTORTION_TAXONOMY_15[new_id - 1]
            results.append(DetectedDistortion(
                distortion_id=new_id,
                distortion_name_kr=d.name_kr,
                distortion_name_en=d.name_en,
                confidence=llm_result.confidence_map[new_id],
                source="llm",
                matched_text=llm_result.evidence[new_id],
                restructuring_strategy=d.strategy
            ))

    # Stage 3: 필터링 + 정렬 + 최대 3건
    results = [r for r in results if r.confidence >= 0.4]
    results.sort(key=lambda r: r.confidence, reverse=True)
    return results[:3]
```

---

## 4. 인지 재구조화 대화 4단계 (P-020)

### 4.1 대화 4단계 구조

> 부록 §C.3 인지 재구조화 대화 템플릿 적용

| 단계 | 목적 | 원칙 | 예시 |
|------|------|------|------|
| Step 1 | 감정 인정 | 공감 우선 (LOCK-HW-09: 비조작) | "그런 생각이 드는 것은 자연스러운 일이에요." |
| Step 2 | 왜곡 부드럽게 안내 | 직접 지적 금지 (LOCK-HW-09: 비진단) | "혹시 다른 관점에서도 한 번 생각해 보실래요?" |
| Step 3 | 대안적 사고 탐색 | 함께 탐색 | "예를 들어, ~라고 볼 수도 있을까요?" |
| Step 4 | 자율성 존중 | LOCK-HW-09: 자율성 | "물론 이건 하나의 관점일 뿐이에요." |

### 4.2 대화 엔진

```python
class CBTDialogueEngine:
    """CBT 인지 재구조화 대화 엔진. 부록 §C.3 4단계 적용."""

    FORBIDDEN_EXPRESSIONS = [
        "당신의 생각은 왜곡되었습니다",
        "이것은 인지왜곡입니다",
        "이렇게 생각해야 합니다",
    ]
    FORBIDDEN_WORDS = ["치료", "진단", "장애", "질환", "환자"]

    def __init__(self, distortion: DetectedDistortion):
        self.distortion = distortion
        self.current_step = 1
        self.dialogue_history: list[dict] = []

    def generate_step(self, user_response: Optional[str] = None) -> str:
        """현재 단계의 대화를 생성한다."""
        if self.current_step == 1:
            return self._step1_empathy()
        elif self.current_step == 2:
            return self._step2_gentle_guide()
        elif self.current_step == 3:
            return self._step3_alternative_thinking(user_response)
        elif self.current_step == 4:
            return self._step4_autonomy()
        else:
            return self._closing()

    def _step1_empathy(self) -> str:
        """Step 1: 감정 인정."""
        messages = [
            "그런 생각이 드는 것은 자연스러운 일이에요.",
            "많이 힘드셨겠어요.",
            "그런 마음이 드시는 게 충분히 이해가 돼요.",
        ]
        self.current_step = 2
        # 안정적(결정적) 인덱스 — 내장 hash() 는 PYTHONHASHSEED 로 프로세스마다 달라져 T-4/T-7 깨짐
        return messages[sum(map(ord, self.distortion.matched_text)) % len(messages)]

    def _step2_gentle_guide(self) -> str:
        """Step 2: 왜곡 부드럽게 안내 (직접 지적 금지)."""
        self.current_step = 3
        return (
            f"혹시 다른 관점에서도 한 번 생각해 보실래요? "
            f"{self.distortion.restructuring_strategy}"
        )

    def _step3_alternative_thinking(self, user_response: Optional[str]) -> str:
        """Step 3: 대안적 사고 함께 탐색."""
        self.current_step = 4
        alternative = self._generate_alternative(self.distortion)
        return f"예를 들어, {alternative}라고 볼 수도 있을까요? 어떻게 생각하세요?"

    def _step4_autonomy(self) -> str:
        """Step 4: 자율성 존중."""
        self.current_step = 5
        return (
            "물론 이건 하나의 관점일 뿐이에요. "
            "스스로의 생각이 가장 중요합니다.\n\n"
            "이 도구는 자가 관리 보조 도구이며, "
            "전문 심리 상담을 대체하지 않습니다."
        )

    def _closing(self) -> str:
        return (
            "오늘 함께 다른 관점을 살펴봐 주셔서 감사해요. "
            "언제든 다시 이야기 나눠요."
        )

    def _generate_alternative(self, distortion: DetectedDistortion) -> str:
        """왜곡 유형별 대안적 사고 생성."""
        alternatives = {
            1: "80점도 충분히 좋은 성과",
            2: "이번 한 번의 결과가 항상을 의미하지는 않는다",
            3: "긍정적인 부분도 함께 살펴보면 전체 그림이 달라질 수 있다",
            4: "그 결과를 만든 당신의 노력도 분명히 있었다",
            5: "상대방의 실제 생각은 직접 확인해봐야 알 수 있다",
            6: "미래에는 지금 예상하지 못한 좋은 결과도 있을 수 있다",
            7: "실제로 일어날 수 있는 최악의 결과와 최선의 결과 사이에 더 많은 가능성이 있다",
            8: "감정은 중요한 신호이지만, 그것이 곧 사실은 아닐 수 있다",
            9: "'~하면 좋겠다'로 바꿔 생각해보면 마음이 조금 편해질 수 있다",
            10: "행동 하나가 당신의 정체성을 결정하지 않는다",
            11: "여러 요인이 함께 작용한 결과일 수 있다",
            12: "이 상황에서 내가 할 수 있는 작은 변화부터 시작해볼 수 있다",
            13: "공정성에 대한 기대와 현실적 대처를 분리해볼 수 있다",
            14: "내가 먼저 변화할 수 있는 작은 부분이 있을 수 있다",
            15: "내가 통제할 수 있는 것과 없는 것을 나누어 보면 마음이 가벼워질 수 있다",
        }
        return alternatives.get(distortion.distortion_id, "다른 관점도 있을 수 있다")

    def validate_output(self, text: str) -> bool:
        """금지 표현 검증. 부록 §C.3 금지 표현 체크."""
        for forbidden in self.FORBIDDEN_EXPRESSIONS + self.FORBIDDEN_WORDS:
            if forbidden in text:
                return False
        return True
```

---

## 5. CBT 세션 전체 흐름

### 5.1 세션 파이프라인

```
[사용자 텍스트 입력]
        │
        ▼
[1. 감정 분석] ← text_emotion_analysis.md (LOCK-HW-01)
        │
        ▼
[2. 인지왜곡 감지] ← cbt_distortion_taxonomy.md (부록 §C)
        │  3단계 파이프라인: 키워드 → LLM → 필터
        ▼
[3. 왜곡 감지됨?]
        │ Yes          │ No
        ▼              ▼
[4. 재구조화 대화]   [일반 공감 응답]
   4단계 진행
        │
        ▼
[5. 세션 기록]
        │
        ▼
[6. 효과 측정]
```

### 5.2 데이터 모델

```python
@dataclass
class CBTSessionResult:
    """CBT 세션 결과."""
    session_id: str
    detected_distortions: list[DetectedDistortion]
    dialogue_steps_completed: int    # 0-4
    user_engaged: bool               # 사용자가 대화에 참여했는지
    pre_emotion: Optional[dict] = None
    post_emotion: Optional[dict] = None
    completed_at: datetime = field(default_factory=datetime.now)
    disclaimer: str = "VAMOS는 의료 서비스가 아닙니다"

@dataclass
class CBTProgress:
    """CBT 장기 진행 추적."""
    user_id: str
    total_sessions: int = 0
    distortion_frequency: dict[int, int] = field(default_factory=dict)  # 왜곡 ID별 빈도
    top_3_distortions: list[int] = field(default_factory=list)
    improvement_trend: Optional[str] = None  # "improving" | "stable" | "needs_attention"
```

---

## 6. R-01-7 로깅 구조

```json
{
  "log_type": "R-01-7",
  "module": "cbt_self_care",
  "event": "cbt_session_complete",
  "timestamp": "2026-04-10T17:00:00Z",
  "data": {
    "session_id": "sess_cbt_001",
    "detected_distortions": [
      {
        "id": 2,
        "name_kr": "과잉일반화",
        "confidence": 0.82,
        "source": "combined",
        "matched_text": "난 항상 실패해"
      }
    ],
    "dialogue_steps_completed": 4,
    "user_engaged": true,
    "forbidden_expression_check": "PASS",
    "effect": {
      "pre_emotion": {"emotion": "frustration", "intensity": 7},
      "post_emotion": {"emotion": "neutral", "intensity": 3}
    },
    "privacy": {
      "level": "PRIVATE",
      "retention_days": 180
    }
  }
}
```

---

## 7. Phase 2 테스트 시나리오

| # | 시나리오 | 입력 | 기대 결과 | 검증 항목 |
|---|---------|------|----------|----------|
| T-1 | 과잉일반화 감지 | "난 항상 실패해" | 왜곡 #2 감지, confidence>=0.5 | 15유형 연동 |
| T-2 | 파국화 감지 | "이번 실수로 인생이 끝났어" | 왜곡 #7 감지 | 키워드 매칭 |
| T-3 | 당위 진술 감지 | "나는 항상 완벽해야 해" | 왜곡 #9 감지 | 키워드 매칭 |
| T-4 | 4단계 대화 완료 | 왜곡 #2 감지 후 | 4단계 순차 진행 | §C.3 대화 템플릿 |
| T-5 | 금지 표현 필터 | "인지왜곡입니다" 포함 시도 | validate=False | 금지 표현 체크 |
| T-6 | 금지 단어 필터 | "치료", "진단" 등 | validate=False | 금지 단어 체크 |
| T-7 | 자율성 존중 (Step 4) | 4단계 도달 | "하나의 관점" 문구 포함 | LOCK-HW-09 자율성 |
| T-8 | 비의료 면책 | CBT 세션 종료 | LOCK-HW-04 포함 | 면책 문구 |
| T-9 | 복수 왜곡 감지 | "항상 실패하고 인생 끝났어" | #2+#7 감지, 상위 3건 제한 | 다중 감지 |
| T-10 | 왜곡 미감지 | "오늘 날씨가 좋네요" | 왜곡 0건, 일반 응답 | 정상 분류 |
| T-11 | 장기 빈도 추적 | 10회 세션 후 | top_3_distortions 산출 | 진행 추적 |
| T-12 | LLM 단독 감지 | 키워드 없는 미묘한 왜곡 | source="llm" | Stage 2 감지 |

---

## 8. 비의료 면책

> LOCK (LOCK-HW-04, STEP7-P 윤리원칙): "VAMOS는 의료 서비스가 아닙니다" 모든 건강 관련 응답에 포함

이 CBT 자가 관리 도구는 전문 심리 상담/치료를 대체하지 않습니다. 인지왜곡 감지 결과는 의학적/심리학적 진단이 아니며, 자기 이해를 위한 참고 정보입니다. 지속적인 정서적 어려움이 있는 경우 전문 상담사와 상담하시기 바랍니다.
