# Learner Profile — 학습자 프로필 생성/관리

| 항목 | 값 |
|------|-----|
| **파일** | `01_adaptive-learning/learner_profile.md` |
| **o_ids** | O-001-3 |
| **V단계** | V1 (로컬 MVP) |
| **Level** | L3 |
| **LOCK 참조** | LOCK-ED-07 |
| **SOT 출처** | STEP7-O O-001 (적응형 학습 엔진) |
| **상태** | COMPLETE |

---

## 1. 개요

학습자 프로필은 적응형 학습 엔진의 개인화 기반이다. 학습자의 현재 수준, 학습 속도, 선호 스타일, 가용 시간, 목표를 통합 관리하며, 모든 학습 활동에서 실시간 갱신된다.

---

## 2. 학습자 프로필 스키마 (LOCK-ED-07)

> LOCK (LOCK-ED-07, 기존 명세 §2): skill_levels, learning_speed, preferred_style, weekly_hours, goal

### 2.1 핵심 스키마

```typescript
interface LearnerProfile {
    // === 식별 ===
    id: string;                                    // 프로필 고유 ID
    user_id: string;                               // 사용자 ID

    // === LOCK-ED-07 필수 필드 (5개) ===
    skill_levels: Record<string, SkillLevel>;      // 주제별 스킬 수준
    learning_speed: "slow" | "normal" | "fast";    // 학습 속도
    preferred_style: LearningStyle;                // 선호 학습 스타일
    weekly_hours: number;                          // 주당 학습 가용 시간 (시간)
    goal: LearningGoal;                            // 학습 목표

    // === 기존 명세 §2.4 호환 필드 ===
    overall_level: number;                         // 1~5 (skill_levels 종합, 상세명세 §2.4)
    preferred_language: string;                    // "ko" (상세명세 §2.4)
    session_duration_pref_min: number;             // 선호 세션 길이 (분, 상세명세 §2.4)

    // === IRT 능력 파라미터 ===
    abilities: Record<string, LearnerAbility>;     // 주제별 θ/σ (difficulty_adjustment.md 참조)

    // === Bloom 진행도 ===
    bloom_progress: Record<string, BloomProgress>; // 주제별 Bloom 레벨 진행

    // === 학습 통계 ===
    stats: LearnerStats;

    // === SM-2 연동 ===
    sm2_summary: SM2Summary;

    // === 메타데이터 ===
    created_at: string;                            // ISO 8601
    updated_at: string;                            // ISO 8601
    version: number;                               // 프로필 버전 (낙관적 잠금)
}
```

### 2.2 LOCK-ED-07 필수 필드 상세

#### 2.2.1 skill_levels

```typescript
interface SkillLevel {
    level: number;             // 1~5 (1=입문, 5=고급)
    confidence: number;        // 0.0~1.0 (IRT σ 기반 신뢰도)
    last_assessed: string;     // ISO 8601 (마지막 평가 일시)
    exercises_done: number;    // 해당 주제 완료 문제 수
    correct_rate: number;      // 정답률 (0.0~1.0)
}

// 예시
skill_levels = {
    "python":     { level: 3, confidence: 0.85, last_assessed: "2026-04-09T10:00:00Z", exercises_done: 120, correct_rate: 0.78 },
    "javascript": { level: 2, confidence: 0.70, last_assessed: "2026-04-08T15:00:00Z", exercises_done: 45,  correct_rate: 0.72 },
    "investing":  { level: 1, confidence: 0.50, last_assessed: "2026-04-05T09:00:00Z", exercises_done: 10,  correct_rate: 0.65 }
}
```

#### 2.2.2 learning_speed

| 값 | 기준 | 학습 경로 영향 |
|-----|------|---------------|
| `"slow"` | 평균 대비 1.5배 이상 소요 | Phase 기간 ×1.5, 복습 빈도 ×1.3 |
| `"normal"` | 평균 범위 | Phase 기간 ×1.0, 복습 빈도 ×1.0 |
| `"fast"` | 평균 대비 0.7배 이하 소요 | Phase 기간 ×0.7, 복습 빈도 ×0.8 |

학습 속도는 최근 20개 세션의 문제당 평균 소요시간으로 자동 분류:

```
function classify_learning_speed(recent_sessions):
    avg_time = mean([s.avg_time_per_item for s in recent_sessions])
    baseline = get_topic_baseline_time(recent_sessions[0].topic)

    ratio = avg_time / baseline
    if ratio >= 1.5:
        return "slow"
    elif ratio <= 0.7:
        return "fast"
    else:
        return "normal"
```

#### 2.2.3 preferred_style

```typescript
type LearningStyle = "visual" | "reading" | "practice" | "mixed";
```

| 스타일 | 설명 | 콘텐츠 우선순위 |
|--------|------|----------------|
| `"visual"` | 시각적 학습 선호 | 다이어그램, 마인드맵, 영상 우선 |
| `"reading"` | 텍스트 기반 학습 선호 | 문서, 논문, 책 요약 우선 |
| `"practice"` | 실습 기반 학습 선호 | 코딩 실습, 퀴즈, 프로젝트 우선 |
| `"mixed"` | 혼합 (기본값) | 균형 배치 |

초기값은 사용자 설정 또는 진단 설문으로 결정, 이후 학습 패턴 분석으로 자동 보정.

#### 2.2.4 weekly_hours

```
weekly_hours: number  // 주당 학습 가용 시간 (단위: 시간)
// 범위: 1 ~ 40
// 기본값: 5
// 학습 경로 소요시간 추정에 직접 사용 (learning_path_generator.md 참조)
```

#### 2.2.5 goal

```typescript
interface LearningGoal {
    description: string;       // 자연어 목표 ("Python으로 퀀트 투자 시스템 만들기")
    target_topics: string[];   // 목표 주제 ["python", "pandas", "quant"]
    target_level: number;      // 목표 스킬 레벨 (1~5)
    deadline: string | null;   // ISO 8601 (선택, 기한)
    priority: "low" | "medium" | "high";  // 우선순위
}
```

### 2.3 보조 스키마

#### BloomProgress

```typescript
interface BloomProgress {
    topic: string;
    levels: {
        remember:    { completion: number; items_done: number; };  // 0.0~1.0
        understand:  { completion: number; items_done: number; };
        apply:       { completion: number; items_done: number; };
        analyze:     { completion: number; items_done: number; };
        evaluate:    { completion: number; items_done: number; };
        create:      { completion: number; items_done: number; };
    };
    current_level: BloomLevel;    // 현재 활성 레벨 (1~6)
    unlocked_up_to: BloomLevel;   // 잠금 해제된 최고 레벨
}
```

#### LearnerStats

```typescript
interface LearnerStats {
    total_study_hours: number;
    total_exercises_completed: number;
    current_streak_days: number;
    longest_streak_days: number;
    topics_mastered: string[];        // level ≥ 4 && confidence ≥ 0.8
    average_session_duration_min: number;
    last_active: string;              // ISO 8601
}
```

#### SM2Summary

```typescript
interface SM2Summary {
    active_flashcards: number;
    cards_due_today: number;
    average_retention_rate: number;   // 0.0~1.0
    average_ef: number;               // 평균 Easiness Factor
}
```

---

## 3. 프로필 API

### 3.1 프로필 생성

```
function create_profile(user_id, initial_data):
    // Step 1: 필수 필드 기본값 설정
    profile = LearnerProfile(
        id              = generate_uuid(),
        user_id         = user_id,
        skill_levels    = {},                      // 빈 상태 → 진단테스트 후 채움
        learning_speed  = "normal",                // 기본값
        preferred_style = initial_data.style ?? "mixed",
        weekly_hours    = initial_data.weekly_hours ?? 5,
        goal            = initial_data.goal ?? null,
        abilities       = {},
        bloom_progress  = {},
        stats           = default_stats(),
        sm2_summary     = default_sm2(),
        created_at      = now(),
        updated_at      = now(),
        version         = 1
    )

    // Step 2: 초기 진단 설문 (선택)
    if initial_data.run_diagnostic:
        diagnostic = run_diagnostic_survey(profile)
        profile.preferred_style = diagnostic.style
        profile.learning_speed  = diagnostic.speed

    // Step 3: 저장
    store.save(profile)
    return profile
```

### 3.2 프로필 갱신

```
function update_profile(profile_id, session_result):
    profile = store.load(profile_id)

    // Step 1: 스킬 레벨 갱신
    topic = session_result.topic
    if topic not in profile.skill_levels:
        profile.skill_levels[topic] = default_skill_level()

    skill = profile.skill_levels[topic]
    skill.exercises_done += session_result.items_count
    skill.correct_rate = recalculate_correct_rate(skill, session_result)
    skill.level = theta_to_skill_level(profile.abilities[topic].theta)
    skill.confidence = 1.0 - profile.abilities[topic].sigma
    skill.last_assessed = now()

    // Step 2: 학습 속도 재분류 (20세션마다)
    if profile.stats.total_exercises_completed // 20 != (profile.stats.total_exercises_completed + session_result.items_count) // 20:
        profile.learning_speed = classify_learning_speed(
            get_recent_sessions(profile_id, count=20)
        )

    // Step 3: Bloom 진행도 갱신
    update_bloom_progress(profile, topic, session_result)

    // Step 4: overall_level 재계산
    profile.overall_level = calculate_overall_level(profile.skill_levels)

    // Step 5: 통계 갱신
    profile.stats.total_study_hours += session_result.duration_hours
    profile.stats.total_exercises_completed += session_result.items_count
    profile.stats.last_active = now()
    update_streak(profile)

    // Step 6: SM-2 요약 갱신
    profile.sm2_summary = recalculate_sm2_summary(profile.user_id)

    // Step 7: 낙관적 잠금 + 저장
    profile.version += 1
    profile.updated_at = now()
    store.save(profile)  // version conflict → retry

    return profile

function update_weekly_hours(profile_id, new_weekly_hours):
    // R-PROF-03: weekly_hours 변경 시 학습 경로 소요시간 재계산 트리거
    profile = store.load(profile_id)
    old_hours = profile.weekly_hours
    profile.weekly_hours = new_weekly_hours
    profile.version += 1
    profile.updated_at = now()
    store.save(profile)

    // 진행 중인 학습 경로 소요시간 재추정 트리거
    active_paths = LearningPathManager.get_active_paths(profile.user_id)
    for path in active_paths:
        LearningPathManager.recalculate_estimates(path)

    return profile
```

### 3.3 프로필 조회

```
function get_profile(user_id):
    profile = store.load_by_user(user_id)
    if profile is null:
        return null

    // 캐시 유효성 검사
    if is_stale(profile.sm2_summary, threshold_hours=1):
        profile.sm2_summary = recalculate_sm2_summary(user_id)
        store.save(profile)

    return profile

function get_profile_summary(user_id):
    // 대시보드용 경량 조회
    profile = get_profile(user_id)
    return ProfileSummary(
        overall_level      = calculate_overall_level(profile.skill_levels),
        top_topics         = get_top_topics(profile.skill_levels, top_n=5),
        current_goal       = profile.goal,
        streak             = profile.stats.current_streak_days,
        weekly_progress    = calculate_weekly_progress(profile),
        cards_due          = profile.sm2_summary.cards_due_today
    )
```

### 3.4 θ → skill_level 변환

> **참고**: 경계값은 `difficulty_adjustment.md`의 `theta_to_level()` 함수와 동일하다. 해당 함수는 난이도 레벨(Very Easy~Very Hard)을 반환하고, 본 함수는 동일 경계를 스킬 레벨(입문~고급)로 재해석한다.

```
function theta_to_skill_level(theta):
    // IRT θ (-3 ~ +3) → skill level (1~5)
    // 경계값: LOCK-ED-02 기준 (-1.5, -0.5, 0.5, 1.5)과 동일
    if theta < -1.5:
        return 1  // 입문   (LOCK-ED-02: Very Easy)
    elif theta < -0.5:
        return 2  // 초급   (LOCK-ED-02: Easy)
    elif theta < 0.5:
        return 3  // 중급   (LOCK-ED-02: Medium)
    elif theta < 1.5:
        return 4  // 중상급 (LOCK-ED-02: Hard)
    else:
        return 5  // 고급   (LOCK-ED-02: Very Hard)
```

---

## 4. 프로필 생애주기

```
┌──────────┐     진단테스트      ┌───────────┐
│  CREATE   │ ──────────────── → │  ACTIVE    │
│ (가입 시)  │                    │ (학습 중)   │
└──────────┘                    └─────┬─────┘
                                      │
                          ┌───────────┼───────────┐
                          │           │           │
                    세션 완료    Bloom 승급   속도 재분류
                    θ 갱신      레벨 해제    (20세션마다)
                          │           │           │
                          └───────────┼───────────┘
                                      │
                                      ▼
                               ┌───────────┐
                               │  ARCHIVE   │
                               │ (비활성)    │
                               └───────────┘
                          30일 비활성 시 자동 전환
                          재활성화 시 진단테스트 재실시
```

---

## 5. 데이터 무결성 규칙

| 규칙 | 설명 |
|------|------|
| R-PROF-01 | `skill_levels`의 `level`은 `abilities[topic].theta`와 항상 동기화 |
| R-PROF-02 | `learning_speed`는 최근 20세션 기반 자동 분류, 수동 오버라이드 가능 |
| R-PROF-03 | `weekly_hours` 변경 시 진행 중인 학습 경로의 소요시간 재계산 트리거 (§3.2 `update_weekly_hours` API) |
| R-PROF-04 | `bloom_progress.unlocked_up_to`는 하위 레벨 completion ≥ 0.70 보장 (종합계획서 부록 §A.3 R-08-2: Bloom 순서 보장 규칙) |
| R-PROF-05 | `version` 충돌 시 최신 버전 기준 머지, 통계 필드는 max() 적용 |

---

## 6. 교차 참조

| 참조 대상 | 파일 | 관계 |
|-----------|------|------|
| 적응형 엔진 코어 | `adaptive_engine.md` | 프로필 로드·갱신 호출 원점 |
| IRT 난이도 조정 | `difficulty_adjustment.md` | θ/σ 추정 결과 → 프로필 저장 |
| 학습 경로 생성기 | `learning_path_generator.md` | weekly_hours, learning_speed, goal 참조 |
| SM-2 교육 확장 | `../02_spaced-repetition/sm2_education_extension.md` | SM2Summary 데이터 원천 (1-2 단계 생성 예정) |
| 학습 대시보드 | `../05_learning-analytics/learning_dashboard.md` | ProfileSummary 소비자 (1-5 단계 생성 예정) |
