# Gamification — 게이미피케이션 XP 체계

| 항목 | 값 |
|------|-----|
| **파일** | `05_learning-analytics/gamification.md` |
| **o_ids** | O-027-1, O-027-2, O-027-3 |
| **V단계** | V1 (로컬 MVP) |
| **Level** | L3 |
| **LOCK 참조** | LOCK-ED-10 |
| **SOT 출처** | STEP7-O O-027 (게이미피케이션 시스템) |
| **상태** | COMPLETE |

---

## 1. 개요

게이미피케이션 시스템은 학습 동기를 지속시키기 위해 게임 메커니즘을 학습 환경에 적용한다. V1에서는 LOCK-ED-10이 정의한 **6요소 체계**를 기본 구현한다.

> LOCK (LOCK-ED-10, 게이미피케이션 XP 체계):
> **XP → 레벨 → 배지 → Streak → 챌린지 → 리더보드**
> V1은 XP·레벨·배지·Streak·챌린지 5요소를 구현하며, 리더보드는 V2에서 확장한다.

핵심 구성:

1. **XP 시스템** (O-027-1) — 학습 활동별 경험치 획득·누적
2. **레벨/배지 시스템** (O-027-2) — XP 기반 레벨업, 목표 달성 배지
3. **Streak/챌린지** (O-027-3) — 연속 학습일 보상, 주간/월간 도전 과제

---

## 2. O-027-1: XP 시스템

### 2.1 XP 획득 공식

```
function calculate_xp(activity):
    base_xp = XP_TABLE[activity.type]

    // 난이도 보너스 (1.0x ~ 2.0x)
    difficulty_mult = 1.0 + (activity.difficulty - 1) * 0.25
    // difficulty: 1(쉬움) ~ 5(매우 어려움) → mult: 1.0 ~ 2.0

    // Bloom 레벨 보너스
    bloom_mult = BLOOM_MULTIPLIER[activity.bloom_level]

    // Streak 보너스 (연속일 기반)
    streak_bonus = min(streak_days * 0.02, 0.5)
    // 최대 50% 보너스 (25일 연속 시 cap)

    // 첫 시도 보너스
    first_attempt_bonus = 1.2 if activity.is_first_attempt else 1.0

    total_xp = base_xp * difficulty_mult * bloom_mult * first_attempt_bonus
    total_xp = total_xp * (1 + streak_bonus)

    return round(total_xp)
```

### 2.2 활동별 기본 XP 테이블

| 활동 유형 | 기본 XP | 설명 |
|----------|---------|------|
| `quiz_correct` | 10 | 퀴즈 정답 |
| `quiz_attempt` | 3 | 퀴즈 시도 (오답도 보상) |
| `module_complete` | 50 | 학습 모듈 1개 완료 |
| `path_complete` | 200 | 학습 경로 1개 완료 |
| `sr_review` | 5 | 간격 반복 카드 복습 (1장) |
| `sr_session_complete` | 20 | SR 세션 전체 완료 |
| `coding_exercise` | 15 | 코딩 연습 문제 풀기 |
| `project_submit` | 100 | 프로젝트/과제 제출 |
| `daily_login` | 5 | 일일 접속 보상 |
| `note_create` | 8 | 학습 노트 작성 |
| `goal_achieve` | 30 | 목표 달성 |

### 2.3 Bloom 레벨 배율표

| Bloom Level | 배율 | 근거 |
|------------|------|------|
| 1 — Remember | 1.0x | 기본 |
| 2 — Understand | 1.1x | 개념 이해 확인 |
| 3 — Apply | 1.3x | 실제 적용 필요 |
| 4 — Analyze | 1.5x | 고차원적 분석 |
| 5 — Evaluate | 1.8x | 비판적 사고 |
| 6 — Create | 2.0x | 창조적 산출물 |

### 2.4 XP 데이터 모델

```typescript
interface XPEvent {
  event_id: string;
  user_id: string;
  activity_type: string;
  base_xp: number;
  multipliers: {
    difficulty: number;
    bloom: number;
    streak: number;
    first_attempt: number;
  };
  total_xp: number;
  earned_at: datetime;
  source_id: string;          // 퀴즈/모듈/경로 ID
}

interface UserXPProfile {
  user_id: string;
  total_xp: number;
  current_level: number;
  xp_to_next_level: number;
  xp_history: XPEvent[];      // 최근 100건
  daily_xp: number;
  weekly_xp: number;
}
```

---

## 3. O-027-2: 레벨/배지 시스템

### 3.1 레벨 테이블

레벨 진행은 **누적 XP 기반**이며, 상위 레벨일수록 필요 XP가 비선형적으로 증가한다.

```
function xp_for_level(level):
    // 공식: base * level^exponent
    // Level 1: 0 XP, Level 2: 100 XP, Level 10: ~5000 XP
    if level <= 1: return 0
    return round(100 * (level - 1) ^ 1.5)
```

| 레벨 | 누적 XP | 칭호 |
|------|---------|------|
| 1 | 0 | 🌱 Seedling |
| 2 | 100 | 🌿 Sprout |
| 3 | 283 | 🌳 Sapling |
| 5 | 800 | 📖 Learner |
| 10 | 2,700 | 🎓 Scholar |
| 15 | 5,422 | 🔬 Researcher |
| 20 | 8,718 | 🧠 Expert |
| 30 | 17,029 | 💎 Master |
| 50 | 34,293 | 🏆 Grandmaster |

### 3.2 배지 시스템

배지는 **특정 목표 달성** 시 수여되며, 일회성(one-time)과 반복성(recurring)으로 구분된다.

```typescript
interface Badge {
  badge_id: string;
  name: string;
  icon: string;
  description: string;
  category: "streak" | "achievement" | "milestone" | "special";
  condition: BadgeCondition;
  recurring: boolean;
  tier: "bronze" | "silver" | "gold" | "platinum";
}

interface BadgeCondition {
  type: string;
  threshold: number;
  metric: string;
}
```

### 3.3 VAMOS 기본 배지 목록

| 배지 | 조건 | 카테고리 | 등급 |
|------|------|---------|------|
| 🔥 Streak Starter | 7일 연속 학습 | streak | bronze |
| 🔥 Streak Master | 30일 연속 학습 | streak | gold |
| 🔥 Streak Legend | 100일 연속 학습 | streak | platinum |
| 📚 Book Worm | 독서 10권 완료 | achievement | silver |
| 💻 Code Ninja | 코딩 문제 100개 풀기 | achievement | gold |
| 📈 Quant Explorer | 첫 백테스트 완료 | milestone | bronze |
| 🧠 Knowledge Builder | 지식 카드 1000개 축적 | milestone | gold |
| ⚡ Speed Learner | 1시간 내 모듈 3개 완료 | special | silver |
| 🎯 Perfect Score | 퀴즈 10회 연속 만점 | achievement | gold |
| 🌅 Early Bird | 오전 6시 전 학습 시작 7회 | special | bronze |

### 3.4 배지 수여 로직

```
function check_badge_eligibility(user_id, event):
    user_stats = get_user_stats(user_id)
    earned_badges = get_earned_badges(user_id)

    for badge in ALL_BADGES:
        if badge.badge_id in earned_badges and not badge.recurring:
            continue

        if evaluate_condition(badge.condition, user_stats, event):
            award_badge(user_id, badge)
            grant_bonus_xp(user_id, badge.tier)
            // 배지 등급별 보너스 XP
            // bronze: 25, silver: 50, gold: 100, platinum: 250

function evaluate_condition(condition, stats, event):
    metric_value = stats[condition.metric]
    match condition.type:
        case "gte": return metric_value >= condition.threshold
        case "streak": return stats.current_streak >= condition.threshold
        case "consecutive": return check_consecutive(stats, condition)
```

---

## 4. O-027-3: Streak / 챌린지

### 4.1 Streak (연속 학습일) 시스템

```
function update_streak(user_id):
    last_activity = db.query(
        "SELECT MAX(date) FROM daily_activity WHERE user_id = :uid",
        uid=user_id
    )
    today = current_date()

    current_streak, longest_streak = db.query(
        "SELECT current_streak, longest_streak FROM user_streaks WHERE user_id = :uid",
        uid=user_id
    )

    if last_activity == today - 1:
        // 연속 유지
        db.increment("user_streaks", user_id, "current_streak", 1)
    elif last_activity == today:
        // 이미 오늘 활동함 — 변경 없음
        pass
    else:
        // 연속 끊김 — 리셋
        db.update("user_streaks", user_id, {
            "longest_streak": max(current_streak, longest_streak),
            "current_streak": 1
        })

    // Streak 마일스톤 체크 (7, 14, 30, 60, 100일)
    check_streak_milestones(user_id)
```

### 4.2 Streak 보상 체계

| 연속일 | 보상 | XP 보너스 |
|-------|------|----------|
| 3일 | Streak 시작 알림 | +5% |
| 7일 | 🔥 Streak Starter 배지 | +10% |
| 14일 | Streak 방어권 1회 (1일 미접속 허용) | +15% |
| 30일 | 🔥 Streak Master 배지 | +25% |
| 60일 | Streak 방어권 2회 추가 | +35% |
| 100일 | 🔥 Streak Legend 배지 + 특별 테마 | +50% (cap) |

### 4.3 챌린지 시스템

챌린지는 기간 한정 도전 과제로, 주간(weekly)과 월간(monthly)으로 구분된다.

```typescript
interface Challenge {
  challenge_id: string;
  title: string;
  description: string;
  type: "weekly" | "monthly";
  start_date: date;
  end_date: date;
  goal: ChallengeGoal;
  reward_xp: number;
  reward_badge?: string;
  participants: number;
}

interface ChallengeGoal {
  metric: string;             // "quizzes_completed", "study_hours", etc.
  target: number;
  current: number;
}
```

### 4.4 기본 챌린지 템플릿

| 챌린지 | 주기 | 목표 | 보상 XP |
|--------|------|------|---------|
| 퀴즈 마라톤 | 주간 | 퀴즈 50문제 풀기 | 150 |
| 시간 투자자 | 주간 | 주간 학습 10시간 | 100 |
| 복습왕 | 주간 | SR 카드 100장 복습 | 80 |
| 다독가 | 월간 | 독서 3권 완료 | 300 |
| 올라운더 | 월간 | 5개 이상 주제 학습 | 250 |
| 코딩 챌린지 | 월간 | 코딩 문제 30개 풀기 | 200 |

---

## 5. 전체 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                  Gamification Engine                      │
│                                                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────────────┐     │
│  │    XP    │   │  Level   │   │     Badge        │     │
│  │ Calculator│──→│  Manager │   │    Evaluator     │     │
│  └────┬─────┘   └────┬─────┘   └────────┬─────────┘     │
│       │              │                   │               │
│       └──────────────┼───────────────────┘               │
│                      │                                   │
│  ┌───────────────────▼────────────────────────────┐      │
│  │              User Profile Store                 │      │
│  │  (total_xp, level, badges[], streak, challenges)│     │
│  └───────────────────┬────────────────────────────┘      │
│                      │                                   │
│  ┌──────────┐   ┌────▼─────┐   ┌──────────────────┐     │
│  │  Streak  │   │ Challenge│   │   Notification    │     │
│  │  Tracker │   │  Manager │   │   Service         │     │
│  └──────────┘   └──────────┘   └──────────────────┘     │
└─────────────────────────────────────────────────────────┘
         ▲                              │
         │  학습 이벤트 수신              │  레벨업/배지 알림
    ─────┘                              └─────→ Dashboard
```

---

## 6. 교차 참조

| 참조 대상 | 파일 | 관계 |
|----------|------|------|
| 학습 대시보드 | `05_learning-analytics/learning_dashboard.md` | XP/레벨/배지 표시 |
| 적응형 엔진 | `01_adaptive-learning/adaptive_engine.md` | 학습 이벤트 발생원 |
| 퀴즈 엔진 | `04_content-generation/quiz_test_generation.md` | 퀴즈 정답 → XP 이벤트 |
| 간격 반복 | `02_spaced-repetition/sm2_education_extension.md` | SR 복습 → XP 이벤트 |
| 목표 관리 | `05_learning-analytics/goal_management.md` | 목표 달성 → XP/배지 |
| 벤치마크 | `05_learning-analytics/benchmark_vbs16.md` | 게이미피케이션 참여도 측정 |

---

## 7. V2/V3 확장 계획

| V단계 | 확장 내용 |
|-------|----------|
| V2 (O-027-4) | 리더보드 — 자기 자신과의 경쟁 (주간 최고 기록), 익명 커뮤니티 순위 |
| V2 | 챌린지 커스터마이징 — 사용자 정의 도전 과제 생성 |
| V3 | 커뮤니티 리더보드 — 실명 기반 그룹 내 경쟁, 팀 챌린지 |
| V3 | 아이템/스킨 상점 — XP로 구매 가능한 테마/아바타 커스터마이징 |

---

# §V2. O-027-4 리더보드 확장 (V2-Phase 2, 2026-04-20)

> **범위**: STAGE 7 Phase 7-II, 3-5 STEP_B #2a 세션 2-4. V1 본문 (§1~§7) 불변 append-only. STEP7-O O-027 (L439~L459) 정본 verbatim 계승. LOCK-ED-10 (게이미피케이션 XP 체계) 전수 적용.

## §V2.1 STEP7-O 정본 인용 (L441~L456 verbatim)

> - 학습 동기 부여:
>   ├─ XP (경험치): 학습 활동 → XP 획득
>   ├─ 레벨: XP 누적 → 레벨업
>   ├─ 배지: 특정 목표 달성 → 배지
>   ├─ 연속 기록 (Streak): 일일 학습 연속일
>   ├─ 챌린지: 주간/월간 도전 과제
>   └─ **리더보드: 자기 자신과의 경쟁 (V3: 커뮤니티)**
>
> - VAMOS 고유 배지 예시:
>   ├─ 🔥 Streak Master: 30일 연속 학습
>   ├─ 📚 Book Worm: 10권 독서 완료
>   ├─ 💻 Code Ninja: 100문제 풀기
>   ├─ 📈 Quant Explorer: 첫 백테스트 완료
>   └─ 🧠 Knowledge Builder: 1000개 지식 축적

## §V2.2 LOCK-ED-10 정본 verbatim

AUTHORITY_CHAIN §4 LOCK-ED-10:
> XP → 레벨 → 배지 → Streak → 챌린지 → 리더보드

V2 는 위 체계를 전수 구현하며 **리더보드 단계 (자기 자신 경쟁)** 를 본 V2 추가 범위로 한정.

## §V2.3 리더보드 스키마

```python
from pydantic import BaseModel, Field
from typing import Literal
from datetime import date, datetime

class PersonalRecord(BaseModel):
    record_id: str
    learner_id: str
    metric: Literal[
        "weekly_xp",
        "daily_streak",
        "flashcards_reviewed",
        "coding_problems_solved",
        "study_hours"
    ]
    value: float
    period: Literal["daily", "weekly", "monthly", "all_time"]
    achieved_on: date

class LeaderboardEntry(BaseModel):
    rank: int
    learner_id: str
    display_name: str  # V2 는 자기 자신 only → 학습자 본인 또는 "Past Me"
    total_score: float
    week_of: date  # 주간 리더보드 week

class LeaderboardView(BaseModel):
    view_id: str
    type: Literal["self_only", "anonymous_community"]  # V2 범위
    entries: list[LeaderboardEntry]
    learner_rank: int
    learner_percentile: float = Field(..., ge=0.0, le=100.0)
```

## §V2.4 자기 자신과의 경쟁 (V2 초점)

```
[자기 경쟁 리더보드 흐름]

매주 일요일 00:00 KST
    │
    ├─ PersonalRecord 스냅샷 생성 (7 metrics)
    │
    ├─ 지난 4주 기록 + 이번 주 기록 비교
    │   ├─ 신기록 달성 → XP +30 + "New Record!" 배지
    │   └─ 기존 기록 유지 → XP +5
    │
    └─ "Past Me" vs "Present Me" 리더보드 표시
```

## §V2.5 익명 커뮤니티 순위 (V2 opt-in)

- 기본 비활성 (opt-in 필수)
- 표시: 상위 10% / 상위 25% / 중간 50% / 하위 25% (퍼센타일만)
- 개인 식별 정보 노출 0
- 학습자 주간 점수를 집계 테이블에 anonymous hash 로 기여
- opt-out 즉시 데이터 제외

## §V2.6 XP 공식 (LOCK-ED-10 세부)

STEP7-O L455 "🧠 Knowledge Builder: 1000개 지식 축적" 기준 참조:

```
[XP 공식 — 모든 학습 활동 집계]

XP = Σ (activity_xp)

activity_xp 테이블:
  - 플래시카드 복습 정답     +5
  - 플래시카드 신규 학습       +3
  - 퀴즈 정답 (Bloom 3+)       +10
  - 코딩 문제 정답 (Easy)      +15
  - 코딩 문제 정답 (Medium)    +25
  - 코딩 문제 정답 (Hard)      +40
  - 프로젝트 마일스톤 완료     +50
  - 자격증 모의고사 ≥80%       +30
  - Streak 7일 마일스톤       +50
  - Streak 30일 마일스톤      +300
  - VBS-16 전 항목 ≥80%       +500 (마스터)

레벨 = floor(sqrt(XP / 100))
  (예: XP 10,000 = Lv 10, XP 40,000 = Lv 20)
```

## §V2.7 V2 Phase 3 테스트 시나리오 (10건)

| # | 시나리오 | 주입 | 기대 결과 |
|---|----------|------|-----------|
| V2-S1 | 주간 신기록 달성 | XP 900 (기존 800) | "New Record!" + XP +30 |
| V2-S2 | 기록 유지 | XP 동일 | XP +5 |
| V2-S3 | 익명 커뮤니티 opt-in | consent | hash 기여 |
| V2-S4 | 익명 opt-out | withdraw | 데이터 제외 |
| V2-S5 | 퍼센타일 상위 10% | 고점수 | "Top 10%" 표시 |
| V2-S6 | 🔥 Streak Master 획득 | 30일 | XP +300 + 배지 |
| V2-S7 | 🧠 Knowledge Builder | 지식 1000 | XP +500 + 배지 (STEP7-O L455) |
| V2-S8 | Level 10 달성 | XP 10,000 | level=10 |
| V2-S9 | 커뮤니티 실명 시도 | V3 전용 | 거부 (V2 익명 only) |
| V2-S10 | LOCK-ED-10 위반 (XP 순서 변경) | order hack | 거부 |

## §V2.8 V1 ↔ V2 정합 표 (append)

| 항목 | V1 (§1~§7) | V2 (§V2) | 출처 |
|------|-----------|----------|------|
| XP/레벨 | 기본 구현 | 활동별 XP 테이블 + 레벨 공식 (§V2.6) | STEP7-O L443~L444 |
| 배지 | 5 기본 배지 | 유지 (V1 활용) + New Record 추가 | STEP7-O L451~L455 |
| Streak | 언급만 | 7/30일 마일스톤 XP (§V2.6) | STEP7-O L446 |
| 챌린지 | 언급만 | coding_challenge.md 연동 | STEP7-O L447 |
| **리더보드** | 미정의 | self + anonymous community (§V2.3~§V2.5) | STEP7-O L448 |
| Phase 3 시나리오 | 미정의 | 10건 | 본 문서 |

## §V2.9 변경 이력 (V2 append)

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-04-20 | **V2-Phase 2** | STAGE 7 3-5 STEP_B #2a 세션 2-4 — §V2 append. O-027-4 PersonalRecord + LeaderboardEntry + LeaderboardView Pydantic + 자기 경쟁 흐름 + 익명 커뮤니티 opt-in + XP 활동별 테이블 + 레벨 공식 floor(sqrt(XP/100)) + STEP7-O 5 배지 verbatim + Streak XP 마일스톤, Phase 3 10건. V1 본문 §1~§7 미수정. V1 168회 기준 |
