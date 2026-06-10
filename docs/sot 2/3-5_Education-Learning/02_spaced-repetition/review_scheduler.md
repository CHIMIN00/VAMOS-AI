# 복습 스케줄러 — SM-2 기반 복습 스케줄링 코어

| 항목 | 값 |
|------|-----|
| **파일** | `02_spaced-repetition/review_scheduler.md` |
| **o_ids** | O-002-6, O-002-7 (V1), O-002-8 (V2) |
| **V단계** | V1 (로컬 MVP) + V2 골격 |
| **Level** | L3 |
| **LOCK 참조** | LOCK-ED-04, LOCK-ED-05 |
| **PKM 참조** | LOCK-PKM-01, LOCK-PKM-02, LOCK-PKM-03 |
| **SOT 출처** | STEP7-O O-002 (간격 반복 시스템) |
| **상태** | COMPLETE |

---

## 1. 개요

복습 스케줄러는 SM-2 알고리즘 기반으로 각 플래시카드의 복습 일정을 관리하고, 학습 맥락에 따라 간격을 조정한다. 세 가지 축으로 구성된다:

1. **복습 스케줄러 코어** (O-002-6, V1) — EF × interval 계산, 일일 복습 큐 관리
2. **학습 맥락별 간격 조정** (O-002-7, V1) — 분야·시간대·학습 강도별 간격 계수
3. **복습 알림 시스템** (O-002-8, V2) — 알림 채널·타이밍·빈도 관리 (골격만 배치)

### SM-2 파라미터 참조 (R-08-1)

> **R-08-1**: SM-2 교육 커스터마이징은 #6 PKM 정본 파라미터 참조 필수. 단독 변경 금지, 변경 무효.

> LOCK (LOCK-ED-04, #6 PKM LOCK-PKM-01~03): MIN_EF=1.3, DEFAULT_EF=2.5, I(1)=1d, I(2)=6d → PKM 참조만, 단독 변경 금지

---

## 2. O-002-6: 복습 스케줄러 코어 (V1)

### 2.1 스케줄러 아키텍처

```
┌─────────────────────────────────────────────────────┐
│                Review Scheduler                      │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ Review Queue  │  │ SM-2 Engine  │  │ Context    │ │
│  │ Manager       │←→│ (정본 참조)   │←→│ Adjuster   │ │
│  └──────┬───────┘  └──────────────┘  └────────────┘ │
│         │                                            │
│  ┌──────▼───────┐  ┌──────────────┐                 │
│  │ Daily Planner │  │ Session      │                 │
│  │ (일일 카드    │←→│ Tracker      │                 │
│  │  할당)        │  │ (진행 추적)   │                 │
│  └──────────────┘  └──────────────┘                 │
└─────────────────────────────────────────────────────┘
```

### 2.2 핵심 스케줄링 알고리즘

```
function schedule_review(card, quality, bloom_level, context):
    // Step 1: SM-2 교육 확장 실행 (sm2_education_extension.md 위임)
    card = sm2_education_extended(card, quality, bloom_level, context)
    // → 내부에서 sm2_base + bloom_ef_adjustment + context_factor 적용 완료

    // Step 2: 일일 한도 체크
    today_count = get_today_review_count(card.owner)
    if today_count >= DAILY_CARD_LIMIT:
        // 한도 초과 시 다음 날로 밀기
        card.next_review = tomorrow()

    // Step 3: 최소 간격 보장
    if card.next_review <= now() + MIN_INTERVAL_HOURS:
        card.next_review = now() + MIN_INTERVAL_HOURS

    // Step 4: 결과 기록
    log_review_result(card, quality, bloom_level)

    return card
```

### 2.3 일일 복습 큐 관리

```
interface ReviewQueueConfig:
    daily_card_limit: number          // 하루 최대 복습 카드 수 (기본 50)
    new_cards_per_day: number         // 하루 신규 카드 수 (기본 10)
    review_time_preference: string    // "morning" | "evening" | "anytime"
    interleaving: boolean             // 주제 섞기 여부 (기본 true)
    min_interval_hours: number        // 같은 카드 최소 간격 (기본 4시간)

function build_daily_queue(learner_id, date):
    config = get_learner_config(learner_id)

    // Step 1: 복습 예정 카드 수집 (next_review <= date)
    due_cards = get_due_cards(learner_id, date)

    // Step 2: 우선순위 정렬
    due_cards = sort_by_priority(due_cards)
    // 정렬 기준:
    //   1순위: 연체 일수 (overdue_days DESC) — 오래 밀린 카드 우선
    //   2순위: EF 낮은 카드 우선 (어려운 카드 = 더 급함)
    //   3순위: Bloom 상위 레벨 우선 (고차 사고 카드가 망각 빠름)

    // Step 3: 일일 한도 적용
    review_cards = due_cards[:config.daily_card_limit]

    // Step 4: 신규 카드 추가
    new_cards = get_new_cards(learner_id, config.new_cards_per_day)

    // Step 5: 인터리빙 (선택적)
    if config.interleaving:
        queue = interleave_by_subject(review_cards + new_cards)
    else:
        queue = review_cards + new_cards

    return DailyQueue(
        date         = date,
        cards        = queue,
        review_count = len(review_cards),
        new_count    = len(new_cards),
        total        = len(queue)
    )
```

### 2.4 우선순위 정렬 상세

```
function sort_by_priority(cards):
    for card in cards:
        overdue_days = (today() - card.next_review).days
        overdue_days = max(0, overdue_days)

        // 복합 우선순위 점수 계산
        card.priority_score = (
            overdue_days * 3.0                      // 연체 가중치 (최우선)
            + max(0, 3.0 - card.ef) * 2.0           // 낮은 EF 가중치 (음수 방지 클램프)
            + card.bloom_level * 0.5                // 상위 Bloom 가중치
            + (card.repetition == 0 ? 1.0 : 0.0)   // 신규 카드 보너스
        )

    return sort(cards, key=card.priority_score, descending=True)
```

### 2.5 인터리빙 알고리즘

```
function interleave_by_subject(cards):
    // 주제별 그룹화
    groups = group_by(cards, key=card.subject_area)

    // 라운드 로빈으로 섞기
    interleaved = []
    while any(group is not empty for group in groups):
        for group in groups:
            if group is not empty:
                interleaved.append(group.pop_front())

    return interleaved
```

### 2.6 세션 추적

```
interface ReviewSession:
    session_id: string
    learner_id: string
    start_time: datetime
    cards_reviewed: number
    cards_remaining: number
    average_quality: number
    time_per_card_ms: number          // 카드당 평균 소요 시간

function track_session(session, card, quality, response_time_ms):
    session.cards_reviewed += 1
    session.cards_remaining -= 1
    session.average_quality = running_average(session.average_quality, quality)
    session.time_per_card_ms = running_average(session.time_per_card_ms, response_time_ms)

    // 과부하 감지: 평균 quality 급락 시 세션 중단 권고
    if session.cards_reviewed >= 10 and session.average_quality < 2.5:
        suggest_session_break(session)
        // "오늘은 여기까지! 내일 이어서 복습합시다."

    return session
```

---

## 3. O-002-7: 학습 맥락별 간격 조정 (V1)

### 3.1 맥락 조정 근거

동일한 SM-2 결과라도 학습 맥락에 따라 최적 복습 간격이 다르다:
- **코딩 실습**: 직접 코드를 작성하는 능동 학습 → 기억 안정성 높음 → 간격 확장
- **이론 독서**: 수동적 학습 → 기억 안정성 낮음 → 간격 축소
- **아침 학습**: 인지 능력 피크 → 학습 효과 높음
- **고강도 집중 학습**: 한 번에 많은 카드 → 간섭 효과 → 간격 축소

### 3.2 맥락 간격 계수 (Context Interval Factor)

```
function get_context_interval_factor(context):
    factor = 1.0  // 기본 배율

    // Factor 1: 학습 유형 (활동 기반)
    ACTIVITY_FACTOR = {
        "active_coding":   1.20,   // 코딩 실습 — 능동 학습, 간격 20% 확장
        "problem_solving": 1.15,   // 문제 풀이 — 능동
        "discussion":      1.10,   // 토론·질의응답 — 준능동
        "reading":         0.90,   // 독서·시청 — 수동, 간격 10% 축소
        "passive_review":  0.80    // 단순 넘기기 복습 — 가장 수동
    }
    factor *= ACTIVITY_FACTOR.get(context.activity_type, 1.0)

    // Factor 2: 시간대 (인지 피크)
    TIME_FACTOR = {
        "morning":   1.05,   // 06-12시: 인지 피크
        "afternoon": 1.00,   // 12-18시: 기준
        "evening":   0.95,   // 18-22시: 약간 감소
        "night":     0.85    // 22-06시: 비추천, 간격 축소
    }
    factor *= TIME_FACTOR.get(context.time_of_day, 1.0)

    // Factor 3: 세션 강도 (한 세션에서 리뷰한 카드 수)
    if context.session_card_count > 30:
        // 고강도 세션: 간섭 효과로 기억 안정성 감소
        intensity_penalty = 1.0 - min(0.15, (context.session_card_count - 30) * 0.005)
        factor *= intensity_penalty
    // 예: 50장 세션 → 1.0 - 0.10 = 0.90

    // Factor 4: 학습 분야 특성 (§B.2.2 context_factor 정합)
    // §B.2.2 방향: coding=0.8, concept=1.0, vocabulary=0.9, formula=0.85, history=1.1
    // 본 L3: 4축 분리 설계이므로 subject 단독 계수는 §B.2.2 방향 준수
    SUBJECT_FACTOR = {
        "coding":      0.85,   // 코딩은 빠른 반복 필요 (§B.2.2: 0.8)
        "math":        0.90,   // 수식은 빠른 반복 (§B.2.2 formula: 0.85)
        "language":    0.90,   // 어휘·문법 — 반복 빈도 필요 (§B.2.2 vocabulary: 0.9)
        "investment":  1.00,   // 개념 이해 — 기준 (§B.2.2 concept: 1.0)
        "history":     1.10,   // 역사/사실 — 느린 간격 가능 (§B.2.2: 1.1)
        "general":     1.00    // 일반 — 기준
    }
    factor *= SUBJECT_FACTOR.get(context.subject_area, 1.0)

    // 최종 factor 범위 제한: 0.5 ~ 2.0
    factor = clamp(factor, 0.5, 2.0)

    return factor
```

### 3.3 맥락 계수 적용 예시

**시나리오 A**: 아침(morning) + 코딩 실습(active_coding) + 20장 세션 + coding 분야

```
factor = 1.0
factor *= 1.20  // active_coding    → 1.20
factor *= 1.05  // morning          → 1.26
factor *= 1.0   // 20장 < 30 한도   → 1.26 (감소 없음)
factor *= 0.85  // coding 분야      → 1.071

// SM-2 기본 간격이 6일인 경우:
// 조정 간격 = round(6 * 1.071) = round(6.426) = 6일
// → 능동적 아침 코딩: 활동 보정(+20%)과 분야 보정(-15%)이 상쇄 → 기준과 유사
// (§B.2.2 coding=0.8 방향 존중: 코딩 분야는 반복 빈도 높이되, 능동 학습은 보상)
```

**시나리오 B**: 야간(night) + 독서(reading) + 45장 세션 + language 분야

```
factor = 1.0
factor *= 0.90  // reading          → 0.90
factor *= 0.85  // night            → 0.765
factor *= 0.925 // 45장: 1.0 - min(0.15, 15*0.005) = 0.925 → 0.708
factor *= 0.90  // language 분야    → 0.637

// SM-2 기본 간격이 6일인 경우:
// 조정 간격 = round(6 * 0.637) = round(3.82) = 4일
// → 수동적 야간 고강도 어학 학습은 간격이 36% 축소됨
```

**시나리오 C**: 오후(afternoon) + 단순 복습(passive_review) + 15장 세션 + coding 분야

```
factor = 1.0
factor *= 0.80  // passive_review   → 0.80
factor *= 1.00  // afternoon        → 0.80
factor *= 1.0   // 15장 < 30 한도   → 0.80 (감소 없음)
factor *= 0.85  // coding 분야      → 0.68

// SM-2 기본 간격이 6일인 경우:
// 조정 간격 = round(6 * 0.68) = round(4.08) = 4일
// → 수동적 코딩 복습은 간격 32% 축소 (§B.2.2 coding=0.8 방향과 일치)
```

### 3.4 LearningContext 스키마

```
interface LearningContext:
    activity_type: string             // "active_coding" | "problem_solving" | "discussion" | "reading" | "passive_review"
    time_of_day: string               // "morning" | "afternoon" | "evening" | "night"
    session_card_count: number        // 현재 세션에서 리뷰한 카드 수
    subject_area: string              // "coding" | "math" | "language" | "investment" | "history" | "general"
    session_duration_min: number      // 세션 경과 시간 (분)
```

---

## 4. 통계 및 분석

### 4.1 복습 통계 스키마

```
interface ReviewStats:
    total_cards: number               // 전체 카드 수
    cards_due: number                 // 복습 예정 카드 수
    retention_rate: number            // 유지율 (quality ≥ 3 비율)
    average_easiness_factor: number   // 평균 EF
    cards_by_stage: StageCount        // 카드 상태별 분류
    streak_days: number               // 연속 복습 일수

interface StageCount:
    new: number                       // 아직 한 번도 복습 안 한 카드
    learning: number                  // repetition 1~2 (초기 학습 중)
    mature: number                    // repetition ≥ 3 (안정 단계)

function calculate_stats(learner_id):
    cards = get_all_cards(learner_id)

    stats = ReviewStats(
        total_cards = len(cards),
        cards_due   = count(c for c in cards if c.next_review <= today()),
        retention_rate = count(recent where quality >= 3) / count(recent),
        average_easiness_factor = mean(c.ef for c in cards),
        cards_by_stage = StageCount(
            new      = count(c for c in cards if c.repetition == 0),
            learning = count(c for c in cards if 1 <= c.repetition <= 2),
            mature   = count(c for c in cards if c.repetition >= 3)
        ),
        streak_days = calculate_streak(learner_id)
    )

    return stats
```

### 4.2 Bloom 레벨별 유지율 분석

```
function retention_by_bloom(learner_id):
    // Bloom 레벨별로 유지율을 분리 추적 → EF 보정값 튜닝 근거
    results = {}
    for bloom_level in [1, 2, 3, 4, 5, 6]:
        cards = get_cards_by_bloom(learner_id, bloom_level)
        recent_reviews = get_recent_reviews(cards, days=30)
        retention = count(r for r in recent_reviews if r.quality >= 3) / len(recent_reviews)
        results[bloom_level] = retention

    return results
    // 목표: 모든 Bloom 레벨에서 retention ≥ 85% (에빙하우스 목표 유지율)
    // 특정 레벨 retention이 낮으면 해당 Bloom의 EF 보정을 더 보수적으로 조정
```

---

## 5. O-002-8: 복습 알림 시스템 (V2 골격)

> **V2 예정** — 본 절은 골격만 배치한다.

### 5.1 개념

복습 알림 시스템은 학습자에게 복습 시점을 알려주는 멀티채널 알림 서비스이다. 최적 시간대에 알림을 발송하고, 알림 피로를 관리한다.

### 5.2 V2 구현 골격

```
// V2 구현 예정
interface ReviewNotification:
    learner_id: string
    channel: NotificationChannel      // "push" | "email" | "in_app"
    scheduled_time: datetime
    cards_due_count: number
    estimated_review_time_min: number  // 예상 복습 소요 시간
    priority: string                   // "high" (연체) | "normal" | "low" (신규)

interface NotificationConfig:
    enabled: boolean                   // 알림 켜기/끄기
    channels: NotificationChannel[]    // 사용할 채널
    quiet_hours: TimeRange             // 방해 금지 시간
    max_notifications_per_day: number  // 일일 최대 알림 수 (기본 3)
    preferred_time: string             // 선호 알림 시간

// V2 알림 파이프라인 (골격):
// 1. 매일 자정: 다음 날 복습 예정 카드 집계
// 2. 학습자 선호 시간대에 맞춰 알림 스케줄링
// 3. quiet_hours 존중, max_notifications_per_day 한도 준수
// 4. 알림 열람/무시 데이터 → 알림 타이밍 최적화 학습
```

---

## 6. 교차 참조

| 참조 대상 | 파일 | 관계 |
|-----------|------|------|
| SM-2 교육 확장 | `sm2_education_extension.md` | sm2_education_extended() 호출, Bloom EF 보정 |
| 플래시카드 자동 생성 | `flashcard_auto_generation.md` | 생성된 카드의 SM-2 초기화 및 큐 등록 |
| PKM SM-2 정본 | `sot 2/3-3_PKM-Knowledge-Management/` LOCK-PKM-01~03 | SM-2 기본 파라미터 정본 (참조 전용) |
| 적응형 엔진 | `../01_adaptive-learning/adaptive_engine.md` | 학습 세션 → 복습 카드 quality 평가 연동 |
| 학습 분석 | `../05_learning-analytics/` | 복습 통계 데이터 제공 (1-5 단계 생성 예정) |
| 종합계획서 부록 §B | `EDUCATION_LEARNING_구조화_종합계획서.md` | 맥락별 간격 조정 상세 참조 |

---

## 7. V2/V3 확장 예정

| 버전 | 확장 내용 |
|------|-----------|
| V2 | 복습 알림 시스템(O-002-8) 본격 구현, 최적 복습 시간 AI 추천, 알림 A/B 테스트 |
| V3 | 그룹 복습 스케줄링, 학습 코치 연동, 장기 기억 안정성 예측 모델 |
