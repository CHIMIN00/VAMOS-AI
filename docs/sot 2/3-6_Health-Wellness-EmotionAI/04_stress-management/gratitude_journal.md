# gratitude_journal.md — 감사 일기

> **P-ID**: P-021
> **V단계**: V1
> **상태**: NEW
> **L3 완성**: 2026-04-10
> **정본 소유자**: sot 2/3-6_Health-Wellness-EmotionAI/04_stress-management/

---

## 교차 참조 블록

| 참조 문서 | 위치 | 참조 내용 |
|----------|------|----------|
| 종합계획서 §3.4 | LOCK-HW-04/12 | 비의료 면책, 감정 강도 1-10 |
| 종합계획서 §6.4 | 매핑 테이블 | P-021 배정 |
| 종합계획서 §4 | R-09-1~R-09-7 | 도메인 전용 거버넌스 규칙 |
| STEP7-P | P-021 | 감사 일기 원본 체크리스트 |
| AUTHORITY_CHAIN.md | §1~§5 | 정본 계층 및 충돌 해결 |
| 05_emotion-journal/emotion_journal_trend.md | 감정 일지 | 감정 기록 연동 |
| 04_stress-management/stress_detection.md | §3 스트레스 수준 | 스트레스 감소 효과 추적 |
| 06_ethics-privacy/ethics_framework.md | §3 7원칙 | 비의료 면책 적용 |

---

## 1. 개요

본 문서는 VAMOS 감사 일기 기능을 L3 구현 즉시 투입 가능 수준으로 정의한다. 일별 감사 항목 기록, 감사 습관 형성 프롬프트, 긍정 심리 효과 추적을 구현한다. 감사 실천이 스트레스 감소와 웰빙 향상에 미치는 효과를 정량적으로 추적한다.

**입력**: 사용자의 일별 감사 항목 (텍스트)
**출력**: `GratitudeEntry { items, mood_before, mood_after, streak, weekly_summary }`

---

## 2. LOCK 인용

> LOCK (LOCK-HW-04, STEP7-P 윤리원칙): "VAMOS는 의료 서비스가 아닙니다" 모든 건강 관련 응답에 포함

> LOCK (LOCK-HW-12, STEP7-P P-001): 1-10 정수 척도

---

## 3. 감사 일기 기록 구조

### 3.1 일별 기록 자료 구조

```python
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional
from enum import Enum

class GratitudeCategory(str, Enum):
    RELATIONSHIP = "RELATIONSHIP"     # 관계/사람
    ACHIEVEMENT = "ACHIEVEMENT"       # 성취/경험
    NATURE = "NATURE"                 # 자연/환경
    HEALTH = "HEALTH"                 # 건강/신체
    SIMPLE_JOY = "SIMPLE_JOY"         # 소소한 기쁨
    GROWTH = "GROWTH"                 # 성장/배움
    OTHER = "OTHER"                   # 기타

@dataclass
class GratitudeItem:
    """감사 항목 개별 기록."""
    text: str                                  # 감사 내용
    category: GratitudeCategory               # 자동 분류
    intensity: int                            # 감사 강도 (LOCK-HW-12: 1-10)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class DailyGratitudeEntry:
    """일별 감사 일기 엔트리."""
    date: date
    items: list[GratitudeItem]               # 1-5개 감사 항목
    mood_before: int                          # 기록 전 기분 (1-10, LOCK-HW-12)
    mood_after: Optional[int] = None          # 기록 후 기분 (1-10)
    reflection: Optional[str] = None          # 자유 회고 텍스트
    created_at: datetime = field(default_factory=datetime.now)
    disclaimer: str = "VAMOS는 의료 서비스가 아닙니다"
```

### 3.2 감사 항목 입력 프롬프트

| 프롬프트 유형 | 질문 | 목적 |
|-------------|------|------|
| 오픈형 | "오늘 감사한 것 3가지를 떠올려 보세요." | 자유로운 감사 탐색 |
| 카테고리형 | "오늘 사람/관계에서 감사했던 것은?" | 카테고리 균형 유도 |
| 구체적 | "오늘 가장 행복했던 순간은 언제인가요?" | 구체적 기억 연결 |
| 전환형 | "어려운 일에서도 배운 것이 있다면?" | 역경 속 성장 인식 |
| 신체 감사 | "오늘 몸이 해준 일에 감사한 것은?" | 신체 인식 연결 |

### 3.3 자동 카테고리 분류

```python
def classify_gratitude_category(text: str) -> GratitudeCategory:
    """
    감사 항목 텍스트를 자동 분류한다.
    키워드 매칭 + LLM fallback.
    Big-O: O(K) — K = 키워드 수 (상수, 약 50개)
    """
    keyword_map = {
        GratitudeCategory.RELATIONSHIP: ["가족", "친구", "동료", "사랑", "함께", "도움"],
        GratitudeCategory.ACHIEVEMENT: ["성공", "달성", "완료", "해냈", "합격", "승진"],
        GratitudeCategory.NATURE: ["날씨", "하늘", "꽃", "바람", "산", "바다", "자연"],
        GratitudeCategory.HEALTH: ["건강", "운동", "잘 잤", "에너지", "컨디션"],
        GratitudeCategory.SIMPLE_JOY: ["커피", "맛있", "음악", "산책", "쉬었", "편안"],
        GratitudeCategory.GROWTH: ["배운", "깨달", "성장", "발전", "새로운"],
    }
    for category, keywords in keyword_map.items():
        if any(kw in text for kw in keywords):
            return category
    return GratitudeCategory.OTHER
```

---

## 4. 긍정 심리 효과 추적

### 4.1 효과 메트릭

```python
@dataclass
class GratitudeEffectMetrics:
    """감사 일기의 긍정 심리 효과 메트릭."""
    avg_mood_before: float          # 기록 전 평균 기분
    avg_mood_after: float           # 기록 후 평균 기분
    avg_mood_lift: float            # 평균 기분 향상도
    streak_days: int                # 연속 작성일
    total_entries: int              # 총 기록 수
    total_items: int                # 총 감사 항목 수
    category_distribution: dict[str, int]  # 카테고리별 분포
    weekly_mood_trend: list[float]  # 주간 기분 추세

def compute_gratitude_effect(
    entries: list[DailyGratitudeEntry],
    window_days: int = 30
) -> GratitudeEffectMetrics:
    """
    최근 N일간 감사 일기 효과를 분석한다.
    Big-O: O(E) — E = 기간 내 엔트리 수
    """
    recent = [e for e in entries if (date.today() - e.date).days <= window_days]
    if not recent:
        return GratitudeEffectMetrics(
            avg_mood_before=0, avg_mood_after=0, avg_mood_lift=0,
            streak_days=0, total_entries=0, total_items=0,
            category_distribution={}, weekly_mood_trend=[]
        )

    # 쌍 필터: before/after 둘 다 존재하는 엔트리만 사용 (동일 모집단 비교)
    paired = [e for e in recent if e.mood_before is not None and e.mood_after is not None]
    mood_befores = [e.mood_before for e in paired]
    mood_afters = [e.mood_after for e in paired]

    avg_before = sum(mood_befores) / len(mood_befores) if mood_befores else 0
    avg_after = sum(mood_afters) / len(mood_afters) if mood_afters else avg_before
    avg_lift = avg_after - avg_before

    # 카테고리 분포
    cat_dist: dict[str, int] = {}
    total_items = 0
    for entry in recent:
        for item in entry.items:
            cat_dist[item.category.value] = cat_dist.get(item.category.value, 0) + 1
            total_items += 1

    return GratitudeEffectMetrics(
        avg_mood_before=round(avg_before, 1),
        avg_mood_after=round(avg_after, 1),
        avg_mood_lift=round(avg_lift, 1),
        streak_days=_compute_streak(recent),
        total_entries=len(recent),
        total_items=total_items,
        category_distribution=cat_dist,
        weekly_mood_trend=_compute_weekly_trend(recent)
    )
```

### 4.2 주간 리포트

| 항목 | 설명 | 산출 방법 |
|------|------|----------|
| 주간 감사 건수 | 이번 주 기록한 감사 항목 수 | count(items) in week |
| 기분 향상도 | 기록 전후 평균 기분 차이 | avg(mood_after - mood_before) |
| 가장 많은 카테고리 | 이번 주 가장 빈번한 감사 카테고리 | max(category_distribution) |
| 연속 작성일 | 현재 연속 기록 일수 | streak_days |
| 추천 메시지 | 감사 습관 유지 격려 | 조건부 메시지 |

---

## 5. 습관 형성 연동

### 5.1 감사 일기 리마인더

| 시간대 | 리마인더 유형 | 메시지 |
|--------|-------------|--------|
| 오전 | 아침 감사 | "좋은 아침이에요! 오늘 아침 감사한 것 1가지를 떠올려 보세요." |
| 저녁 (20시) | 하루 감사 정리 | "오늘 하루를 돌아보며 감사한 것 3가지를 적어볼까요?" |
| 미작성 시 | 부드러운 알림 | "감사 일기가 기다리고 있어요. 오늘도 써볼까요?" |

---

## 6. 세션 간 인터페이스

### 6.1 감정 일지 연동 (→ 05_emotion-journal/)

```python
# 감사 일기의 mood_before/mood_after를 감정 일지에 피드백
# emotion_journal_trend.md의 일별 감정 데이터에 감사 효과 반영
```

### 6.2 스트레스 감지 연동 (← stress_detection.md)

```python
# 높은 스트레스 시 감사 일기 프롬프트 자동 제안
# stress_level >= MODERATE 시 전환형 프롬프트 활용
```

---

## 7. R-01-7 로깅 구조

```json
{
  "log_type": "R-01-7",
  "module": "gratitude_journal",
  "event": "gratitude_entry_created",
  "timestamp": "2026-04-10T21:00:00Z",
  "data": {
    "entry_date": "2026-04-10",
    "items_count": 3,
    "categories": ["RELATIONSHIP", "SIMPLE_JOY", "GROWTH"],
    "mood_before": 5,
    "mood_after": 7,
    "mood_lift": 2,
    "streak_days": 12,
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
| T-1 | 기본 감사 기록 | 3개 감사 항목 | DailyGratitudeEntry 생성 | 기록 무결성 |
| T-2 | 기분 변화 측정 | mood_before=5, after=7 | mood_lift=2 | 전후 비교 |
| T-3 | 카테고리 자동 분류 | "가족이 따뜻한 밥을 해줬다" | RELATIONSHIP | 키워드 분류 |
| T-4 | 연속 기록 추적 | 7일 연속 기록 | streak_days=7 | 연속일 계산 |
| T-5 | 주간 리포트 | 7일 데이터 | 주간 요약 생성 | 리포트 정합 |
| T-6 | 카테고리 분포 | 30일 데이터 | category_distribution 정합 | 분포 계산 |
| T-7 | 리마인더 발송 | 20시, 미작성 | 리마인더 메시지 | 리마인더 로직 |
| T-8 | 스트레스 연동 | stress=MODERATE | 전환형 프롬프트 | 연동 정합 |
| T-9 | 비의료 면책 | 모든 응답 | LOCK-HW-04 포함 | 면책 문구 |
| T-10 | 빈 기록 처리 | 0개 항목 입력 | 유효성 오류 메시지 | 입력 검증 |
| T-11 | 강도 범위 검증 | intensity=11 | 범위 초과 오류 | LOCK-HW-12 1-10 |
| T-12 | 월간 효과 분석 | 30일 데이터 | GratitudeEffectMetrics | 효과 산출 |

---

## 9. 비의료 면책

> LOCK (LOCK-HW-04, STEP7-P 윤리원칙): "VAMOS는 의료 서비스가 아닙니다" 모든 건강 관련 응답에 포함

감사 일기는 긍정 심리학 기반의 자가 관리 도구이며, 우울증 등 임상적 증상에 대한 치료를 대체하지 않습니다. 지속적인 정서적 어려움이 있는 경우 전문가 상담을 권장합니다.
