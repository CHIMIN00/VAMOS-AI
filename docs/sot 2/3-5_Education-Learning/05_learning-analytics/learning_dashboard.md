# Learning Dashboard — 학습 분석 대시보드

| 항목 | 값 |
|------|-----|
| **파일** | `05_learning-analytics/learning_dashboard.md` |
| **o_ids** | O-010-1 |
| **V단계** | V1 (로컬 MVP) |
| **Level** | L3 |
| **LOCK 참조** | — |
| **SOT 출처** | STEP7-O O-010 (학습 분석 대시보드) |
| **상태** | COMPLETE |

---

## 1. 개요

학습 분석 대시보드는 학습자의 진도·성과·시간 데이터를 시각화하여 자기 주도 학습을 촉진하는 중앙 모니터링 허브다. V1에서는 **텍스트 기반 대시보드**로 핵심 메트릭을 제공하며, V2에서 비주얼 차트·리포트 생성으로 확장한다.

핵심 기능:

1. **진도 추적** (O-010-1) — 학습 경로별 완료율, 활성 모듈 수, 연속 학습일
2. **성과 메트릭** — 정답률, 난이도별 분포, 평균 풀이 시간
3. **시간 분석** — 일별/주별 학습 시간, 주제별 시간 분배
4. **Bloom 레벨별 달성도** — 6단계 인지 수준별 콘텐츠 소화 현황

---

## 2. O-010-1: 학습 대시보드 코어

### 2.1 데이터 모델

```typescript
interface LearningAnalytics {
  user_id: string;
  period: "daily" | "weekly" | "monthly" | "all_time";

  // 진도 추적
  progress: {
    active_paths: number;
    completed_modules: number;
    total_modules: number;
    completion_rate: number;          // 0.0 ~ 1.0
    current_streak_days: number;
  };

  // 성과 메트릭
  performance: {
    average_score: number;            // 0~100
    exercises_attempted: number;
    exercises_correct: number;
    accuracy_rate: number;            // 0.0 ~ 1.0
    average_time_per_exercise_sec: number;
    difficulty_distribution: Record<number, number>;
  };

  // SM-2 간격 반복 통계
  spaced_repetition: {
    total_cards: number;
    cards_due: number;
    retention_rate: number;
    average_easiness_factor: number;
    cards_by_stage: Record<string, number>;
  };

  // 약점 분석
  weaknesses: WeaknessAnalysis[];

  // 추천
  recommendations: Recommendation[];
}

interface WeaknessAnalysis {
  topic: string;
  skill: string;
  bloom_level: number;               // 1~6
  accuracy_rate: number;
  attempts: number;
  common_errors: string[];
  suggested_action: string;
  suggested_resources: string[];
}

interface Recommendation {
  type: "review" | "practice" | "advance" | "break";
  target_topic: string;
  title: string;
  description: string;
  priority: "high" | "medium" | "low";
  action_url?: string;
}
```

### 2.2 대시보드 구성 레이아웃

```
┌──────────────────────────────────────────────────────────────┐
│                    VAMOS Learning Dashboard                   │
├────────────────────┬─────────────────────────────────────────┤
│  📊 진도 요약       │  📈 성과 트렌드                          │
│                    │                                         │
│  활성 경로: 3      │  이번 주 정답률: 78% (↑5%)               │
│  완료 모듈: 12/30  │  평균 풀이시간: 45초                      │
│  완료율: 40%       │  누적 문제 수: 342                       │
│  연속 학습: 7일    │  난이도 분포: ■■■□□ (3.2/5)              │
├────────────────────┼─────────────────────────────────────────┤
│  ⏱ 시간 분석       │  🎯 Bloom 달성도                         │
│                    │                                         │
│  오늘: 1.5h       │  6-Create    : ██░░░░░░░░  20%          │
│  이번 주: 8.2h    │  5-Evaluate  : ████░░░░░░  40%          │
│  월 누적: 32h     │  4-Analyze   : ██████░░░░  60%          │
│                    │  3-Apply     : ████████░░  80%          │
│  Python  : 45%    │  2-Understand: █████████░  90%          │
│  Math    : 30%    │  1-Remember  : ██████████  100%         │
│  Finance : 25%    │                                         │
├────────────────────┴─────────────────────────────────────────┤
│  ⚠ 약점 분석 & 추천                                          │
│  • [Review] 미적분 - 분석 레벨 정답률 42% → 복습 추천         │
│  • [Practice] 파이썬 OOP - 적용 레벨 연습 부족 → 문제 풀기    │
│  • [Advance] 통계 기초 - 이해 레벨 완료 → 분석 단계 진입 추천  │
└──────────────────────────────────────────────────────────────┘
```

### 2.3 메트릭 수집 파이프라인

```
function collect_dashboard_metrics(user_id, period):
    // 1. 진도 데이터 수집
    progress = db.query("""
        SELECT
            COUNT(DISTINCT path_id) as active_paths,
            SUM(CASE WHEN status='complete' THEN 1 ELSE 0 END) as completed,
            COUNT(*) as total
        FROM learning_modules
        WHERE user_id = :user_id
          AND updated_at >= period_start(:period)
    """, user_id=user_id, period=period)

    // 2. 성과 데이터 수집
    performance = db.query("""
        SELECT
            AVG(score) as avg_score,
            COUNT(*) as attempted,
            SUM(CASE WHEN correct THEN 1 ELSE 0 END) as correct_count,
            AVG(time_spent_sec) as avg_time
        FROM exercise_attempts
        WHERE user_id = :user_id
          AND attempted_at >= period_start(:period)
    """, user_id=user_id, period=period)

    // 3. Bloom 레벨별 달성도
    bloom_stats = {}
    for level in [1..6]:
        stats = db.query("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN mastered THEN 1 ELSE 0 END) as mastered
            FROM content_mastery
            WHERE user_id = :user_id AND bloom_level = :level
        """, user_id=user_id, level=level)
        bloom_stats[level] = stats.mastered / max(stats.total, 1)

    // 4. 약점 식별
    weaknesses = identify_weaknesses(user_id, period)

    // 5. 추천 생성
    recommendations = generate_recommendations(weaknesses, bloom_stats)

    return LearningAnalytics(
        user_id=user_id, period=period,
        progress=progress, performance=performance,
        spaced_repetition=get_sr_stats(user_id),
        weaknesses=weaknesses, recommendations=recommendations
    )
```

### 2.4 약점 식별 알고리즘

```
function identify_weaknesses(user_id, period):
    // 주제 × Bloom 레벨 매트릭스에서 정답률 하위 항목 추출
    topic_bloom_matrix = db.query("""
        SELECT topic, bloom_level,
               AVG(CASE WHEN correct THEN 1.0 ELSE 0.0 END) as accuracy,
               COUNT(*) as attempts
        FROM exercise_attempts
        WHERE user_id = :user_id
          AND attempted_at >= period_start(:period)
        GROUP BY topic, bloom_level
        HAVING COUNT(*) >= 3
        ORDER BY accuracy ASC
    """, user_id=user_id, period=period)

    weaknesses = []
    for row in topic_bloom_matrix:
        if row.accuracy < 0.6:                       // 정답률 60% 미만
            action = determine_action(row.bloom_level, row.accuracy)
            errors = get_common_errors(user_id, row.topic, row.bloom_level)
            resources = get_suggested_resources(row.topic, row.bloom_level)
            weaknesses.append(WeaknessAnalysis(
                topic=row.topic,
                skill=row.skill,
                bloom_level=row.bloom_level,
                accuracy_rate=row.accuracy,
                attempts=row.attempts,
                common_errors=errors,
                suggested_action=action,
                suggested_resources=resources
            ))
    return weaknesses[:5]                             // 상위 5개만 표시

function determine_action(bloom_level, accuracy):
    if accuracy < 0.3:
        return "기초 개념 재학습 필요"
    elif bloom_level >= 4 and accuracy < 0.5:
        return "하위 Bloom 단계 복습 후 재도전"
    else:
        return "추가 연습 문제 풀이 추천"
```

### 2.5 Bloom 레벨별 달성도 시각화

Bloom 택소노미 6단계에 대해 각 주제의 마스터리 진행 상황을 매핑한다.

| Bloom 단계 | 설명 | 달성 기준 |
|-----------|------|----------|
| 1 — Remember | 사실·용어 회상 | SR 카드 retention ≥ 80% |
| 2 — Understand | 개념 설명 가능 | 이해 확인 퀴즈 정답률 ≥ 70% |
| 3 — Apply | 새 상황에 적용 | 코딩/연습 문제 정답률 ≥ 65% |
| 4 — Analyze | 구조·관계 분석 | 분석형 문제 정답률 ≥ 60% |
| 5 — Evaluate | 판단·비평 | 평가형 문제 정답률 ≥ 55% |
| 6 — Create | 새로운 산출물 생성 | 프로젝트/과제 제출 및 평가 |

```
function compute_bloom_achievement(user_id, topic):
    achievements = {}
    for level in [1..6]:
        mastery = get_mastery_score(user_id, topic, level)
        achievements[level] = {
            "score": mastery,
            "status": "mastered" if mastery >= threshold(level) else "in_progress",
            "bar": render_progress_bar(mastery, 10)
        }
    return achievements

function threshold(bloom_level):
    // 상위 레벨일수록 기준 완화 (고차원적 사고는 달성 자체가 어려움)
    thresholds = {1: 0.80, 2: 0.70, 3: 0.65, 4: 0.60, 5: 0.55, 6: 0.50}
    return thresholds[bloom_level]
```

---

## 3. 추천 시스템

### 3.1 추천 유형 및 트리거

| 추천 유형 | 트리거 조건 | 우선순위 |
|----------|-----------|---------|
| `review` | 정답률 < 60% 또는 SR 카드 retention 하락 | 1 (최고) |
| `practice` | 시도 횟수 < 5 이면서 해당 Bloom 레벨 미달 | 2 |
| `advance` | 현재 Bloom 레벨 마스터리 ≥ threshold → 다음 레벨 | 3 |
| `break` | 연속 학습 시간 > 90분 또는 정답률 급락 | 4 |

### 3.2 추천 생성 로직

```
function generate_recommendations(weaknesses, bloom_stats, analytics):
    recs = []

    // 약점 기반 복습/연습 추천
    for w in weaknesses:
        if w.accuracy_rate < 0.4:
            recs.append(Recommendation(
                type="review", target_topic=w.topic,
                title=f"{w.topic} 복습 필요",
                description=f"Bloom L{w.bloom_level} 정답률 {w.accuracy_rate:.0%} — 기초부터 재학습",
                priority="high"
            ))
        else:
            recs.append(Recommendation(
                type="practice", target_topic=w.topic,
                title=f"{w.topic} 추가 연습",
                description=f"정답률 {w.accuracy_rate:.0%} — 연습 문제로 향상 가능",
                priority="medium"
            ))

    // 간격 반복 카드 복습 독려
    if analytics.spaced_repetition.cards_due > 20:
        recs.append(Recommendation(
            type="review", target_topic="spaced_repetition",
            title=f"밀린 플래시카드 {analytics.spaced_repetition.cards_due}장",
            description="복습 지연이 기억 유지율을 낮춥니다. 오늘 복습을 완료하세요.",
            priority="high"
        ))

    // Bloom 진급 추천
    for topic, levels in bloom_stats.items():
        for level in [1..5]:
            if levels[level] >= threshold(level) and levels[level+1] < threshold(level+1):
                recs.append(Recommendation(
                    type="advance", target_topic=topic,
                    title=f"Bloom L{level} 완료 → L{level+1} 진입",
                    description=f"{topic} Bloom L{level} 마스터리 달성. 다음 단계로 진행하세요.",
                    priority="medium"
                ))

    // 번아웃 방지 — 연속 학습 > 90분 또는 정답률 급락 감지
    if detect_burnout_risk(analytics):
        recs.append(Recommendation(
            type="break", target_topic="general",
            title="휴식 권장",
            description="최근 학습량이 많고 성과가 하락 중입니다. 하루 쉬어가는 것을 추천합니다.",
            priority="high"
        ))

    return sorted(recs, key=lambda r: {"high": 0, "medium": 1, "low": 2}[r.priority])[:5]

function detect_burnout_risk(analytics):
    // 연속 학습 시간 > 90분 + 최근 정답률 하락 추세
    recent_accuracy_trend = get_accuracy_trend(analytics.user_id, days=7)
    long_session = analytics.progress.current_session_minutes > 90
    declining = recent_accuracy_trend < -0.05  // 5%p 이상 하락
    return long_session and declining
```

---

## 4. 시각화 차트 목록

V1에서는 텍스트/ASCII 기반으로 표현하며, V2에서 인터랙티브 차트로 전환한다.

| 차트 | 데이터 | 목적 | V단계 |
|------|------|------|-------|
| 학습 히트맵 | 일별 학습 시간 | GitHub contributions 스타일 연간 활동 | V2 |
| 스킬 레이더 | 주제별 수준 | 강점/약점 한눈에 파악 | V2 |
| 진도 바 차트 | 경로별 완료율 | 전체 학습 진행 상황 | V1 (텍스트) |
| 정답률 트렌드 | 주별 정답률 | 성장 추이 확인 | V1 (텍스트) |
| 난이도 분포 | 시도한 문제 난이도 | 학습 수준 변화 | V1 (텍스트) |
| SM-2 분포 | 카드 상태별 수 | 복습 상태 파악 | V1 (텍스트) |
| 시간 분배 | 주제별 학습 시간 | 학습 균형 확인 | V1 (텍스트) |

---

## 5. 교차 참조

| 참조 대상 | 파일 | 관계 |
|----------|------|------|
| 적응형 학습 엔진 | `01_adaptive-learning/adaptive_engine.md` | 학습 데이터 생성원 |
| 간격 반복 시스템 | `02_spaced-repetition/sm2_education_extension.md` | SR 통계 제공 |
| 퀴즈/평가 | `04_content-generation/quiz_test_generation.md` | 성과 메트릭 제공 |
| 게이미피케이션 | `05_learning-analytics/gamification.md` | XP/레벨 표시 연동 |
| 목표 관리 | `05_learning-analytics/goal_management.md` | 목표 진행률 표시 |
| 시간 관리 | `05_learning-analytics/time_management.md` | 시간 분석 데이터 |

---

## 6. V2/V3 확장 계획

| V단계 | 확장 내용 |
|-------|----------|
| V2 (O-010-2) | 인터랙티브 시각화 차트 (히트맵, 레이더, 트렌드 라인) |
| V2 (O-010-3) | 학습 리포트 PDF/마크다운 자동 생성, 주간/월간 이메일 리포트 |
| V3 | AI 기반 예측 분석 (이탈 예측, 최적 학습 시간 추천) |

---

# §V2. O-010-2 학습 통계 시각화 확장 (V2-Phase 2, 2026-04-20)

> **범위**: STAGE 7 Phase 7-II, 3-5 STEP_B #2a 세션 2-4. V1 본문 (§1~§6) 불변 append-only. STEP7-O O-010 (L190~L207) + O-028 (L460~L482 VBS-16) 정본 계승. LOCK-ED-09 (VBS-16) 전수 verbatim 적용.

## §V2.1 STEP7-O 정본 인용

O-010 L192~L200 verbatim:
> - 학습 메트릭:
>   ├─ 일일/주간/월간 학습 시간
>   ├─ 주제별 진행률
>   ├─ 테스트 성적 추이
>   ├─ 간격 반복 통계 (기억률)
>   ├─ 목표 대비 진행률
>   └─ 강점/약점 분석 차트
>
> [구현성] V1: ✅ 텍스트 즉시 | **V2: ✅ 비주얼 2개월**

O-028 L464~L472 verbatim (VBS-16 정본):
> VBS-16: Education & Learning Score
>
> 1. 적응형 학습 정확도
> 2. 간격 반복 효과 (기억 유지율)
> 3. 퀴즈 생성 품질
> 4. 학습 경로 적절성
> 5. 코딩 튜터링 효과
> 6. 사용자 학습 지속률
> 7. 게이미피케이션 참여도
> 8. 학습 시간 대비 효과
>
> 목표: 학습 지속률 ≥ 60%, 기억 유지율 ≥ 80%

## §V2.2 V2 인터랙티브 시각화 (4 차트 유형)

| 차트 | 용도 | 라이브러리 권장 | Bloom 맥락 |
|------|------|----------------|-----------|
| **히트맵** | 시간대 × 요일 학습 밀도 | D3.js / Observable Plot | 2-3 |
| **레이더 차트** | VBS-16 8 항목 동시 | Chart.js radar | 4-5 |
| **트렌드 라인** | 주간/월간 지표 추이 | ECharts line | 3-4 |
| **간격 반복 곡선** | SM-2 기억률 시뮬레이션 | Recharts | 4-5 |

## §V2.3 VBS-16 대시보드 패널

```
[VBS-16 8 항목 실시간 대시보드]

  ┌──────────────────────────────────────────────┐
  │  VBS-16 Education & Learning Score           │
  │  ─────────────────────────────────────────   │
  │  [Radar Chart]                                │
  │    1. 적응형 학습 정확도:      87% ✅         │
  │    2. 간격 반복 효과:          82% ✅ (≥80)  │
  │    3. 퀴즈 생성 품질:          78% 🟡         │
  │    4. 학습 경로 적절성:        85% ✅         │
  │    5. 코딩 튜터링 효과:        76% 🟡         │
  │    6. 사용자 학습 지속률:      65% ✅ (≥60)  │
  │    7. 게이미피케이션 참여도:   72% 🟡         │
  │    8. 학습 시간 대비 효과:     80% ✅         │
  │  ─────────────────────────────────────────   │
  │  목표 달성 (LOCK-ED-09):                      │
  │    ✅ 학습 지속률 ≥ 60% (현재 65%)            │
  │    ✅ 기억 유지율 ≥ 80% (현재 82%)            │
  └──────────────────────────────────────────────┘
```

## §V2.4 V2 데이터 수집 파이프라인

```python
from pydantic import BaseModel, Field
from datetime import date

class VBS16Snapshot(BaseModel):
    snapshot_id: str
    learner_id: str
    captured_on: date
    adaptive_accuracy_pct: float = Field(..., ge=0.0, le=100.0)
    sm2_retention_pct: float = Field(..., ge=0.0, le=100.0)
    quiz_quality_pct: float = Field(..., ge=0.0, le=100.0)
    path_appropriateness_pct: float = Field(..., ge=0.0, le=100.0)
    coding_tutor_effectiveness_pct: float = Field(..., ge=0.0, le=100.0)
    continuation_rate_pct: float = Field(..., ge=0.0, le=100.0)
    gamification_engagement_pct: float = Field(..., ge=0.0, le=100.0)
    time_efficacy_pct: float = Field(..., ge=0.0, le=100.0)

    @property
    def meets_lock_ed_09(self) -> bool:
        return self.continuation_rate_pct >= 60.0 and self.sm2_retention_pct >= 80.0
```

## §V2.5 주제별 진행률 + 강점/약점

- `learner_profile.md` skill_levels 시계열 저장
- Bloom 레벨 × 주제 매트릭스 시각화 (히트맵)
- 약점 자동 하이라이트 → learning_path_generator 에 재조정 요청

## §V2.6 V2 Phase 3 테스트 시나리오 (10건)

| # | 시나리오 | 주입 | 기대 결과 |
|---|----------|------|-----------|
| V2-S1 | 히트맵 렌더링 | 30일 학습 데이터 | 7×24 셀 |
| V2-S2 | 레이더 차트 8 항목 | VBS16Snapshot | 8 축 표시 |
| V2-S3 | 지속률 60% 미만 | 경고 trigger | 빨간 알림 |
| V2-S4 | 기억 유지율 80% 미만 | 경고 trigger | 노란 알림 |
| V2-S5 | 트렌드 라인 개선 | 월간 +5% | 녹색 화살표 |
| V2-S6 | 약점 식별 | Bloom 4 Analyze 65% | 재조정 제안 |
| V2-S7 | VBS-16 전 항목 ≥80 | snapshot | "마스터" 배지 |
| V2-S8 | 간격 반복 곡선 | SM-2 30일 | 망각 곡선 시각화 |
| V2-S9 | 값 100 초과 | 잘못된 입력 | 거부 |
| V2-S10 | LOCK-ED-09 위반 (목표 임의 변경) | threshold=50 | 거부 |

## §V2.7 V1 ↔ V2 정합 표 (append)

| 항목 | V1 (§1~§6) | V2 (§V2) | 출처 |
|------|-----------|----------|------|
| 학습 메트릭 | 텍스트 요약 | 4 차트 + 히트맵 (§V2.2) | STEP7-O L192~L200 |
| VBS-16 8 항목 | 언급만 | 레이더 패널 + 임계값 (§V2.3) | LOCK-ED-09 + STEP7-O L464~L472 |
| VBS16Snapshot | 미정의 | Pydantic + property (§V2.4) | 본 문서 |
| 강점/약점 | 언급만 | Bloom × 주제 매트릭스 (§V2.5) | STEP7-O L199 |
| Phase 3 시나리오 | 미정의 | 10건 | 본 문서 |

## §V2.8 변경 이력 (V2 append)

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-04-20 | **V2-Phase 2** | STAGE 7 3-5 STEP_B #2a 세션 2-4 — §V2 append. O-010-2 인터랙티브 4 차트 + VBS-16 레이더 대시보드 + VBS16Snapshot Pydantic + LOCK-ED-09 목표 임계값 (지속률≥60, 기억률≥80) verbatim, Phase 3 10건. V1 본문 §1~§6 미수정. V1 168회 기준 |
