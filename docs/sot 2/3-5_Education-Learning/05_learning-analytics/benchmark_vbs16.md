# Benchmark VBS-16 — 교육/학습 벤치마크

| 항목 | 값 |
|------|-----|
| **파일** | `05_learning-analytics/benchmark_vbs16.md` |
| **o_ids** | O-028-1 |
| **V단계** | V1 (로컬 MVP) |
| **Level** | L3 |
| **LOCK 참조** | LOCK-ED-09 |
| **SOT 출처** | STEP7-O O-028 (학습 VBS-16 벤치마크) |
| **상태** | COMPLETE |

---

## 1. 개요

VBS-16(VAMOS Benchmark Score-16)은 교육·학습 모듈 전반의 성능을 측정하는 **커스텀 벤치마크 프레임워크**다. 8개 핵심 지표를 통해 학습 시스템의 효과를 정량적으로 평가하며, 두 가지 핵심 기준값을 LOCK으로 보호한다.

> LOCK (LOCK-ED-09, VBS-16 벤치마크 기준):
> **학습 지속률(Retention Rate) ≥ 60%**, **기억 유지율(Memory Retention) ≥ 80%**
> 이 두 기준은 시스템의 최소 품질 보증 임계값이며, 변경 시 전체 교육 모듈 재검증이 필요하다.

---

## 2. VBS-16 지표 정의

### 2.1 8개 핵심 지표

| # | 지표명 | 코드 | 측정 대상 | 목표 | LOCK |
|---|--------|------|----------|------|------|
| 1 | 적응형 학습 정확도 | `VBS16-01` | 적응형 엔진의 난이도 조절 적합성 | ≥ 75% | — |
| 2 | 기억 유지율 | `VBS16-02` | 간격 반복 후 장기 기억 유지 | **≥ 80%** | **LOCK-ED-09** |
| 3 | 퀴즈 생성 품질 | `VBS16-03` | 자동 생성 퀴즈의 교육적 적합성 | ≥ 70% | — |
| 4 | 학습 경로 적절성 | `VBS16-04` | 추천 경로의 학습자 수준 적합도 | ≥ 70% | — |
| 5 | 코딩 튜터링 효과 | `VBS16-05` | 코딩 교육 전후 역량 향상도 | ≥ 20%p | — |
| 6 | 학습 지속률 | `VBS16-06` | 30일 이상 활성 사용자 비율 | **≥ 60%** | **LOCK-ED-09** |
| 7 | 게이미피케이션 참여도 | `VBS16-07` | XP 활동 참여율 / 배지 획득률 | ≥ 50% | — |
| 8 | 학습 시간 대비 효과 | `VBS16-08` | 투입 시간 대비 성과 향상 비율 | ≥ 1.5x | — |

### 2.2 가중치 배분

```
VBS-16 종합 점수 = Σ (지표 점수 × 가중치)

가중치 배분:
  VBS16-01 (적응형 정확도)     : 0.15
  VBS16-02 (기억 유지율)       : 0.20  ← LOCK-ED-09
  VBS16-03 (퀴즈 품질)         : 0.10
  VBS16-04 (경로 적절성)       : 0.10
  VBS16-05 (코딩 튜터링)       : 0.10
  VBS16-06 (학습 지속률)       : 0.20  ← LOCK-ED-09
  VBS16-07 (게이미피케이션)     : 0.05
  VBS16-08 (시간 대비 효과)     : 0.10
  ──────────────────────────────────
  합계                         : 1.00
```

LOCK-ED-09 지표 2개의 가중치 합이 0.40(40%)으로, 전체 벤치마크에서 가장 높은 비중을 차지한다.

---

## 3. 측정 방법론

### 3.1 VBS16-01: 적응형 학습 정확도

```
function measure_adaptive_accuracy(user_pool, period):
    // 적응형 엔진이 선택한 콘텐츠 난이도가 학습자 수준에 적합한지 측정
    results = []
    for user in user_pool:
        sessions = get_sessions(user, period)
        for session in sessions:
            predicted_difficulty = session.engine_selected_difficulty
            actual_performance = session.user_performance_score
            // 적합성: 정답률 40~80% 범위에 들면 적절한 난이도
            is_appropriate = 0.4 <= actual_performance <= 0.8
            results.append(is_appropriate)

    return sum(results) / len(results)  // 적합 비율
```

### 3.2 VBS16-02: 기억 유지율 (LOCK-ED-09: ≥ 80%)

```
function measure_memory_retention(user_pool, period):
    // 간격 반복 학습 후 일정 기간 경과 뒤 기억 유지 비율
    retention_scores = []
    for user in user_pool:
        sr_cards = get_reviewed_cards(user, period)
        for card in sr_cards:
            // 마지막 복습 후 7일 경과 시점에서 테스트
            if days_since_last_review(card) >= 7:
                test_result = administer_retention_test(user, card)
                retention_scores.append(test_result.correct)

    rate = sum(retention_scores) / max(len(retention_scores), 1)
    assert rate >= 0.80, f"LOCK-ED-09 위반: 기억 유지율 {rate:.1%} < 80%"
    return rate
```

### 3.3 VBS16-03: 퀴즈 생성 품질

```
function measure_quiz_quality(quiz_pool, evaluator_pool):
    // 자동 생성 퀴즈에 대한 교육 전문가 / 사용자 평가
    quality_scores = []
    for quiz in quiz_pool:
        evaluations = []
        for evaluator in evaluator_pool:
            score = evaluate_quiz(evaluator, quiz, criteria=[
                "relevance",       // 학습 내용과의 관련성
                "clarity",         // 문제/선지 명확성
                "difficulty_fit",  // 학습자 수준 적합성
                "bloom_alignment"  // Bloom 레벨 일치도
            ])
            evaluations.append(score.average)
        quality_scores.append(mean(evaluations))

    return mean(quality_scores)
```

### 3.4 VBS16-04: 학습 경로 적절성

```
function measure_path_relevance(user_pool, period):
    // 추천된 학습 경로를 따른 사용자의 성과 향상도
    relevance_scores = []
    for user in user_pool:
        recommended_path = get_recommended_path(user)
        actual_path = get_actual_path(user, period)
        overlap = path_overlap_ratio(recommended_path, actual_path)

        if overlap >= 0.5:  // 추천 경로 50% 이상 수강
            pre_score = get_pre_assessment(user, recommended_path.topic)
            post_score = get_post_assessment(user, recommended_path.topic)
            improvement = post_score - pre_score
            relevance_scores.append(1.0 if improvement > 0 else 0.0)

    return mean(relevance_scores)
```

### 3.5 VBS16-05: 코딩 튜터링 효과

```
function measure_coding_tutoring_effect(user_pool, period):
    // 코딩 튜터링 전후 역량 변화 (percentage point)
    improvements = []
    for user in user_pool:
        pre = get_coding_assessment(user, "pre", period)
        post = get_coding_assessment(user, "post", period)
        if pre and post:
            improvement_pp = post.score - pre.score  // percentage point
            improvements.append(improvement_pp)

    avg_improvement = mean(improvements)
    return avg_improvement  // 목표: ≥ 20pp
```

### 3.6 VBS16-06: 학습 지속률 (LOCK-ED-09: ≥ 60%)

```
function measure_learning_retention_rate(user_pool, period):
    // 가입 후 30일 이상 활성 상태를 유지하는 사용자 비율
    total_users = len(user_pool)
    retained_users = 0

    for user in user_pool:
        signup_date = user.created_at
        if (today() - signup_date).days < 30:
            continue  // 30일 미경과 사용자 제외

        // 최근 30일 내 활동일 ≥ 5일이면 '활성'
        active_days = db.query("""
            SELECT COUNT(DISTINCT date) FROM daily_activity
            WHERE user_id = :uid
              AND date >= current_date - interval '30 days'
        """, uid=user.id)

        if active_days >= 5:
            retained_users += 1

    rate = retained_users / max(total_users, 1)
    assert rate >= 0.60, f"LOCK-ED-09 위반: 학습 지속률 {rate:.1%} < 60%"
    return rate
```

### 3.7 VBS16-07: 게이미피케이션 참여도

```
function measure_gamification_engagement(user_pool, period):
    // XP 활동 참여율 + 배지 획득률 복합 지표
    engagement_scores = []
    for user in user_pool:
        xp_events = get_xp_events(user, period)
        badges = get_earned_badges(user, period)

        // 활동 다양성 (10가지 XP 활동 유형 중 몇 개 참여)
        activity_types = set(e.activity_type for e in xp_events)
        diversity = len(activity_types) / 10.0

        // 배지 획득률 (기본 배지 10개 중)
        badge_rate = len(badges) / 10.0

        engagement = 0.6 * diversity + 0.4 * badge_rate
        engagement_scores.append(engagement)

    return mean(engagement_scores)
```

### 3.8 VBS16-08: 학습 시간 대비 효과

```
function measure_time_effectiveness(user_pool, period):
    // 투입 시간 1시간당 성과 향상 비율
    ratios = []
    for user in user_pool:
        total_hours = get_total_study_hours(user, period)
        if total_hours < 5:  // 최소 5시간 이상 학습한 사용자만
            continue

        pre_score = get_overall_assessment(user, "pre", period)
        post_score = get_overall_assessment(user, "post", period)
        improvement_pct = (post_score - pre_score) / max(pre_score, 1) * 100

        ratio = improvement_pct / total_hours  // %향상/시간
        ratios.append(ratio)

    avg_ratio = mean(ratios)
    return avg_ratio  // 목표: ≥ 1.5 (%/h)
```

---

## 4. 데이터 수집 파이프라인

### 4.1 아키텍처

```
┌──────────────────────────────────────────────────────────┐
│                VBS-16 Benchmark Pipeline                   │
│                                                           │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐            │
│  │ Adaptive  │  │   SR      │  │   Quiz    │            │
│  │ Engine    │  │  Engine   │  │  Engine   │  ...       │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘            │
│        │              │              │                    │
│        └──────────────┼──────────────┘                    │
│                       ▼                                   │
│              ┌──────────────────┐                         │
│              │  Event Collector │                         │
│              │  (실시간 수집)    │                         │
│              └────────┬─────────┘                         │
│                       ▼                                   │
│              ┌──────────────────┐                         │
│              │  Data Store      │                         │
│              │  (Raw Metrics)   │                         │
│              └────────┬─────────┘                         │
│                       ▼                                   │
│              ┌──────────────────┐                         │
│              │  Aggregator      │                         │
│              │  (주기: 일/주)   │                         │
│              └────────┬─────────┘                         │
│                       ▼                                   │
│              ┌──────────────────┐                         │
│              │  Scorer          │                         │
│              │  (VBS-16 계산)   │                         │
│              └────────┬─────────┘                         │
│                       ▼                                   │
│              ┌──────────────────┐                         │
│              │  Report &        │                         │
│              │  Alert Engine    │                         │
│              └──────────────────┘                         │
└──────────────────────────────────────────────────────────┘
```

### 4.2 수집 주기 및 이벤트

| 데이터 소스 | 수집 이벤트 | 주기 | 저장 형식 |
|------------|-----------|------|----------|
| 적응형 엔진 | 세션 완료, 난이도 선택 로그 | 실시간 | event_log |
| SR 엔진 | 카드 복습 결과, retention 테스트 | 실시간 | sr_review_log |
| 퀴즈 엔진 | 퀴즈 생성·응시 결과 | 실시간 | quiz_result_log |
| 학습 경로 | 경로 진행·완료 | 실시간 | path_progress_log |
| 코딩 튜터 | 사전/사후 평가 결과 | 세션 단위 | coding_assessment |
| 사용자 활동 | 로그인, 학습 시간 | 일별 집계 | daily_activity |
| 게이미피케이션 | XP 이벤트, 배지 획득 | 실시간 | gamification_log |
| 시간 관리 | 포모도로 완료, 학습 시간 | 실시간 | time_log |

### 4.3 종합 점수 계산

```
function compute_vbs16_score(user_pool, period):
    metrics = {
        "VBS16-01": measure_adaptive_accuracy(user_pool, period),
        "VBS16-02": measure_memory_retention(user_pool, period),
        "VBS16-03": measure_quiz_quality(get_quizzes(period), get_evaluators()),
        "VBS16-04": measure_path_relevance(user_pool, period),
        "VBS16-05": measure_coding_tutoring_effect(user_pool, period),
        "VBS16-06": measure_learning_retention_rate(user_pool, period),
        "VBS16-07": measure_gamification_engagement(user_pool, period),
        "VBS16-08": measure_time_effectiveness(user_pool, period),
    }

    weights = {
        "VBS16-01": 0.15, "VBS16-02": 0.20, "VBS16-03": 0.10,
        "VBS16-04": 0.10, "VBS16-05": 0.10, "VBS16-06": 0.20,
        "VBS16-07": 0.05, "VBS16-08": 0.10,
    }

    // 각 지표를 0~100 스케일로 정규화
    normalized = {}
    for key, value in metrics.items():
        normalized[key] = normalize_to_100(key, value)

    total_score = sum(normalized[k] * weights[k] for k in weights)

    // LOCK-ED-09 경고 체크
    alerts = []
    if metrics["VBS16-02"] < 0.80:
        alerts.append(f"⚠ LOCK-ED-09 위반: 기억 유지율 {metrics['VBS16-02']:.1%} < 80%")
    if metrics["VBS16-06"] < 0.60:
        alerts.append(f"⚠ LOCK-ED-09 위반: 학습 지속률 {metrics['VBS16-06']:.1%} < 60%")

    assert not alerts, "LOCK-ED-09 위반: " + "; ".join(alerts)

    assert not alerts, "LOCK-ED-09 위반: " + "; ".join(alerts)

    return VBS16Report(
        total_score=total_score,
        metrics=metrics,
        normalized=normalized,
        alerts=alerts,
        period=period
    )
```

---

## 5. 교차 참조

| 참조 대상 | 파일 | 관계 |
|----------|------|------|
| 적응형 엔진 | `01_adaptive-learning/adaptive_engine.md` | VBS16-01 측정 대상 |
| 간격 반복 | `02_spaced-repetition/sm2_education_extension.md` | VBS16-02 측정 대상 |
| 퀴즈 엔진 | `04_content-generation/quiz_test_generation.md` | VBS16-03 측정 대상 |
| 코딩 튜터 | `03_coding-tutorial/interactive_tutorial.md` | VBS16-05 측정 대상 |
| 게이미피케이션 | `05_learning-analytics/gamification.md` | VBS16-07 측정 대상 |
| 시간 관리 | `05_learning-analytics/time_management.md` | VBS16-08 측정 대상 |
| 대시보드 | `05_learning-analytics/learning_dashboard.md` | 벤치마크 결과 표시 |

---

## 6. V2/V3 확장 계획

| V단계 | 확장 내용 |
|-------|----------|
| V2 | A/B 테스트 프레임워크 — 기능별 효과 비교 실험 |
| V2 | 자동 리그레션 감지 — 지표 하락 시 자동 알림 + 원인 분석 |
| V3 | 외부 벤치마크 비교 — 타 교육 플랫폼 대비 성능 벤치마킹 |
| V3 | 사용자 코호트 분석 — 가입 시기·학습 유형별 세분화 분석 |
