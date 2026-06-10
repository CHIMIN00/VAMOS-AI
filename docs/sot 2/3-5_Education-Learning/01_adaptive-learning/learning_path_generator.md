# Learning Path Generator — 학습 경로 생성기

| 항목 | 값 |
|------|-----|
| **파일** | `01_adaptive-learning/learning_path_generator.md` |
| **o_ids** | O-003-1, O-003-2, O-003-3, O-003-4 |
| **V단계** | V1 (로컬 MVP) |
| **Level** | L3 |
| **LOCK 참조** | LOCK-ED-01, LOCK-ED-02, LOCK-ED-03, LOCK-ED-05 |
| **SOT 출처** | STEP7-O O-003 (학습 경로 생성) |
| **상태** | COMPLETE |

---

## 1. 개요

학습 경로 생성기는 사용자의 목표와 현재 수준을 분석하여 개인화된 학습 커리큘럼을 자동 생성한다. 4가지 핵심 기능으로 구성된다:

1. **학습 경로 자동 생성** (O-003-1) — 목표 → 스킬 분해 → 경로 구성
2. **Phase 분해 알고리즘** (O-003-2) — 학습 경로를 Phase 단위로 분해
3. **체크포인트 시스템** (O-003-3) — Phase 종료 시 평가 및 승급 판정
4. **소요 시간 추정** (O-003-4) — 학습자 속도 기반 일정 예측

---

## 2. 학습 경로 구조 (LOCK-ED-01)

> LOCK (LOCK-ED-01, STEP7-O O-003): 목표 → Phase 분해 → 각 Phase(자료 + 실습 + 체크포인트 + 소요시간)

### 2.1 경로 스키마

```typescript
interface LearningPath {
    id: string;
    learner_id: string;
    goal: LearningGoal;                // learner_profile.md 참조

    // === LOCK-ED-01 구조 ===
    phases: Phase[];                   // Phase 분해 결과
    total_estimated_hours: number;     // 총 예상 소요시간
    estimated_completion: string;      // ISO 8601 예상 완료일

    // === 메타데이터 ===
    prerequisites: string[];           // 선행 조건 (스킬 ID 목록)
    difficulty_range: [number, number]; // IRT θ 범위 [min, max]
    bloom_range: [BloomLevel, BloomLevel]; // Bloom 시작~종료 레벨

    status: "draft" | "active" | "paused" | "completed" | "abandoned";
    progress: number;                  // 0.0~1.0 전체 진행률
    created_at: string;
    updated_at: string;
}

interface Phase {
    id: string;
    order: number;                     // Phase 순서 (1-based)
    title: string;                     // "Phase 1: Python 기초"
    description: string;

    // === LOCK-ED-01: 각 Phase 4요소 ===
    resources: Resource[];             // 자료
    exercises: Exercise[];             // 실습
    checkpoint: Checkpoint;            // 체크포인트
    estimated_hours: number;           // 소요시간

    // === 부가 정보 ===
    skills: string[];                  // 이 Phase에서 학습하는 스킬
    bloom_level: BloomLevel;           // 이 Phase의 Bloom 레벨 (LOCK-ED-05)
    difficulty_target: number;         // IRT θ 목표 (LOCK-ED-02)
    prerequisites: string[];           // 선행 Phase ID

    status: "locked" | "available" | "in_progress" | "completed";
    progress: number;                  // 0.0~1.0
    actual_hours: number;              // 실제 소요시간 (추적용)
}
```

### 2.2 Phase 4요소 상세

#### 자료 (Resource)

```typescript
interface Resource {
    id: string;
    type: "document" | "video" | "interactive" | "external_link";
    title: string;
    url: string | null;                // 외부 자료 URL
    content: string | null;            // 내부 콘텐츠
    estimated_read_min: number;        // 예상 학습 시간 (분)
    bloom_level: BloomLevel;           // 자료의 Bloom 레벨
    is_required: boolean;              // 필수 여부
}
```

#### 실습 (Exercise)

```typescript
interface Exercise {
    id: string;
    type: "quiz" | "coding" | "project" | "essay" | "discussion";
    title: string;
    description: string;
    difficulty: number;                // IRT θ
    bloom_level: BloomLevel;
    hints: Hint[];                     // 소크라테스 3단계 힌트
    estimated_min: number;             // 예상 소요시간 (분)
    is_required: boolean;
    grading: "auto" | "self" | "peer";
}
```

#### 체크포인트 (Checkpoint)

```typescript
interface Checkpoint {
    id: string;
    phase_id: string;
    type: "diagnostic" | "progress" | "final";  // LOCK-ED-03
    items_count: number;               // 문제 수
    pass_threshold: number;            // 통과 기준 (0.0~1.0)
    bloom_levels_tested: BloomLevel[]; // 평가 대상 Bloom 레벨
    time_limit_min: number | null;     // 제한 시간 (선택)
    retry_allowed: boolean;            // 재시도 허용 여부
    max_retries: number;               // 최대 재시도 횟수
}
```

---

## 3. O-003-1: 학습 경로 자동 생성

### 3.1 생성 파이프라인

```
function generate_learning_path(learner_id, goal):
    profile = LearnerProfileManager.load(learner_id)

    // === Step 1: 목표 분석 ===
    // 자연어 목표 → 필요 스킬 목록으로 분해
    required_skills = decompose_goal(goal)
    // 예: "Python으로 퀀트 투자 시스템" →
    //     ["python_basics", "pandas", "numpy", "yfinance", "technical_analysis",
    //      "backtesting", "portfolio_theory", "system_design"]

    // === Step 2: 현재 수준 평가 ===
    current_skills = {}
    for skill in required_skills:
        if skill in profile.skill_levels:
            current_skills[skill] = profile.skill_levels[skill]
        else:
            current_skills[skill] = SkillLevel(level=0, confidence=0)

    // === Step 3: 갭 분석 ===
    gaps = []
    for skill in required_skills:
        current = current_skills[skill].level
        target  = goal.target_level
        if current < target:
            gaps.append(SkillGap(
                skill        = skill,
                current      = current,
                target       = target,
                gap_size     = target - current,
                bloom_start  = level_to_bloom(current),
                bloom_target = level_to_bloom(target)
            ))

    // === Step 4: 선행 조건 그래프 구성 ===
    prereq_graph = build_prerequisite_graph(gaps)
    // 예: pandas → python_basics, technical_analysis → pandas

    // === Step 5: 토폴로지 정렬 ===
    sorted_skills = topological_sort(prereq_graph)

    // === Step 6: Phase 분해 ===
    phases = decompose_into_phases(sorted_skills, profile)

    // === Step 7: 소요시간 추정 ===
    for phase in phases:
        phase.estimated_hours = estimate_phase_hours(phase, profile)

    // === Step 8: 경로 조합 ===
    path = LearningPath(
        learner_id           = learner_id,
        goal                 = goal,
        phases               = phases,
        total_estimated_hours = sum(p.estimated_hours for p in phases),
        estimated_completion  = calculate_completion_date(
            phases, profile.weekly_hours
        )
    )

    return path
```

### 3.2 목표 분해 (Goal Decomposition)

```
function decompose_goal(goal):
    // LLM 기반 목표 분해 + 스킬 그래프 참조

    // Step 1: LLM으로 필요 스킬 후보 추출
    prompt = """
    학습 목표: {goal.description}
    이 목표를 달성하기 위해 필요한 스킬을 계층적으로 분해하세요.
    각 스킬에 대해: 이름, 설명, 예상 수준(1-5), 선행 스킬을 제공하세요.
    """
    skill_candidates = llm.generate(prompt, schema=SkillListSchema)

    // Step 2: 스킬 그래프 DB에서 기존 스킬 매칭
    matched_skills = []
    for candidate in skill_candidates:
        match = skill_graph_db.find_closest(candidate.name)
        if match and match.similarity > 0.8:
            matched_skills.append(match)
        else:
            // 새 스킬 노드 생성
            new_skill = create_skill_node(candidate)
            matched_skills.append(new_skill)

    // Step 3: 선행 관계 검증
    validate_prerequisites(matched_skills)

    return matched_skills
```

---

## 4. O-003-2: Phase 분해 알고리즘

### 4.1 분해 전략

Phase 분해는 Bloom 택소노미 순서(LOCK-ED-05: Remember → Create)와 IRT 난이도(LOCK-ED-02)를 함께 고려한다.

```
function decompose_into_phases(sorted_skills, profile):
    phases = []
    phase_order = 1

    for skill in sorted_skills:
        gap = get_gap(skill)

        // Bloom 레벨별로 Phase 생성
        // R-08-2 (종합계획서 부록 §A.3): 하위 단계 70% 이상 완료 후 상위 단계 해제
        // "반드시 1단계부터 순차 배치" 규칙: bloom_start는 갭 분석에서
        // 이미 완료된 하위 레벨을 건너뛴 값. 기존 학습자의 경우
        // 진단테스트(CAT)로 현재 Bloom 레벨을 확인한 후 해당 레벨부터 시작.
        // 진단 결과가 없는 신규 학습자는 bloom_start = 1 (Remember)로 설정.
        bloom_start = gap.bloom_start  // 진단 기반 현재 Bloom 레벨
        bloom_end   = gap.bloom_target // 목표 Bloom 레벨

        for bloom_level in range(bloom_start, bloom_end + 1):
            // 해당 스킬 + Bloom 레벨의 Phase 생성
            phase = Phase(
                order            = phase_order,
                title            = "Phase {}: {} — {}".format(
                    phase_order, skill.name, BLOOM_NAMES[bloom_level]
                ),
                skills           = [skill.id],
                bloom_level      = bloom_level,
                difficulty_target = bloom_to_theta(bloom_level),
                prerequisites    = get_phase_prerequisites(phases, skill, bloom_level)
            )

            // 자료 배치
            phase.resources = select_resources(skill, bloom_level, profile.preferred_style)

            // 실습 배치
            phase.exercises = generate_exercises(skill, bloom_level, phase.difficulty_target)

            // 체크포인트 배치
            phase.checkpoint = create_checkpoint(phase, bloom_level)

            phases.append(phase)
            phase_order += 1

    // 관련 스킬 병합 최적화
    // 같은 Bloom 레벨의 관련 스킬은 하나의 Phase로 병합 가능
    phases = merge_related_phases(phases, max_skills_per_phase=3)

    return phases
```

### 4.2 Bloom-θ 매핑 (Phase 난이도 설정)

```
function bloom_to_theta(bloom_level):
    // Bloom 레벨 → 권장 IRT θ 중심값
    // LOCK-ED-02 경계: -1.5(VE/E), -0.5(E/M), 0.5(M/H), 1.5(H/VH)
    mapping = {
        1: -1.0,   // Remember   → Easy 범위 중심 (-1.5 ≤ θ < -0.5)
        2: -0.5,   // Understand → Easy/Medium 경계
        3:  0.0,   // Apply      → Medium 범위 중심 (-0.5 ≤ θ < 0.5)
        4:  0.5,   // Analyze    → Medium/Hard 경계
        5:  1.0,   // Evaluate   → Hard 범위 중심 (0.5 ≤ θ < 1.5)
        6:  1.5    // Create     → Very Hard 경계 (θ ≥ 1.5)
    }
    return mapping[bloom_level]
```

### 4.3 Phase 병합 규칙

```
function merge_related_phases(phases, max_skills_per_phase):
    // 병합 조건:
    // 1. 같은 Bloom 레벨
    // 2. 스킬 간 선행 관계 없음 (병렬 학습 가능)
    // 3. 병합 후 Phase 스킬 수 ≤ max_skills_per_phase
    // 4. 예상 소요시간 합계 ≤ 20시간 (Phase가 너무 커지지 않도록)

    merged = []
    i = 0
    while i < len(phases):
        current = phases[i]
        j = i + 1
        while j < len(phases):
            candidate = phases[j]
            if can_merge(current, candidate, max_skills_per_phase):
                current = merge(current, candidate)
                phases.pop(j)
            else:
                j += 1
        merged.append(current)
        i += 1

    // Phase 순서 재정렬
    reorder(merged)
    return merged
```

---

## 5. O-003-3: 체크포인트 시스템

### 5.1 체크포인트 유형 (LOCK-ED-03 연동)

> LOCK (LOCK-ED-03, 기존 명세 §2): 진단테스트 + 진행평가 + 최종평가, 3등급 (미달 / 달성 / 우수)

| 유형 | LOCK-ED-03 대응 | 시점 | 문제 수 | 통과 기준 | 실패 시 |
|------|----------------|------|---------|-----------|---------|
| **Phase 진행평가** | 진행평가 | Phase 종료 시 | 5-10문항 | 정답률 ≥ 70% | 보충 학습 + 재시도 |
| **Bloom 레벨업 진행평가** | 진행평가 | Bloom 레벨 전환 시 | 8-15문항 | 정답률 ≥ 70% (R-08-2) | 현재 레벨 심화 학습 |
| **경로 최종평가** | 최종평가 | 전체 경로 완료 시 | 15-25문항 | 정답률 ≥ 70% | 약점 Phase 복습 |

> **참고**: 진단테스트는 학습 경로 생성 전 `difficulty_adjustment.md` §5.2의 CAT 알고리즘으로 수행된다.

### 5.2 체크포인트 생성 알고리즘

```
function create_checkpoint(phase, bloom_level, is_final_path_checkpoint=false):
    // Step 1: 문제 수 결정
    if is_final_path_checkpoint:
        // 경로 최종평가: 15-25문항 (§5.1 테이블 기준)
        items_count = 15 + min(bloom_level * 2, 10)  // 15~25
    elif bloom_level <= 2:     // Remember, Understand
        items_count = 5
    elif bloom_level <= 4:     // Apply, Analyze
        items_count = 8
    else:                      // Evaluate, Create
        items_count = 10

    // Step 2: Bloom 레벨 분포 결정
    // 현재 레벨 문제 70% + 이전 레벨 복습 문제 30%
    bloom_distribution = {
        bloom_level: int(items_count * 0.7),
        bloom_level - 1: int(items_count * 0.3) if bloom_level > 1 else 0
    }

    // Step 3: 체크포인트 유형 결정
    if is_final_path_checkpoint:
        cp_type = "final"          // 최종평가 (LOCK-ED-03)
    else:
        cp_type = "progress"       // 진행평가 (LOCK-ED-03)

    // Step 4: 체크포인트 구성
    checkpoint = Checkpoint(
        phase_id          = phase.id,
        type              = cp_type,
        items_count       = items_count,
        pass_threshold    = 0.70,      // 70% 통과 기준
        bloom_levels_tested = list(bloom_distribution.keys()),
        time_limit_min    = items_count * 3,  // 문제당 3분
        retry_allowed     = true,
        max_retries       = 3
    )

    return checkpoint
```

### 5.3 체크포인트 평가 흐름

```
function evaluate_checkpoint(learner, checkpoint, responses):
    // Step 1: 채점
    score = grade_responses(checkpoint, responses)

    // Step 2: 등급 판정 (LOCK-ED-03: 미달/달성/우수)
    // 기준은 adaptive_engine.md §2.4 평가 체계와 동일
    if checkpoint.type == "progress":
        // 진행평가: 미달 < 70%, 달성 70-84%, 우수 >= 85%
        if score < 0.70:
            grade = "미달"
        elif score < 0.85:
            grade = "달성"
        else:
            grade = "우수"
    elif checkpoint.type == "final":
        // 최종평가: 미달 < 70%, 달성 70-89%, 우수 >= 90%
        if score < 0.70:
            grade = "미달"
        elif score < 0.90:
            grade = "달성"
        else:
            grade = "우수"

    // Step 3: 통과 여부
    passed = score >= checkpoint.pass_threshold  // 0.70

    // Step 4: 실패 시 보충 학습 생성
    if not passed:
        weak_areas = identify_weak_areas(responses)
        remediation = generate_remediation_plan(
            learner    = learner,
            weak_areas = weak_areas,
            phase      = checkpoint.phase_id
        )
        return CheckpointResult(
            passed      = false,
            score       = score,
            grade       = grade,
            remediation = remediation,
            retry_count = checkpoint.current_retries + 1,
            can_retry   = checkpoint.current_retries < checkpoint.max_retries
        )

    // Step 5: 통과 시 다음 Phase 잠금 해제
    unlock_next_phase(learner, checkpoint.phase_id)

    // Step 6: Bloom 레벨업 판정
    if is_bloom_checkpoint(checkpoint):
        if score >= 0.70:  // R-08-2
            unlock_bloom_level(learner, phase.topic, phase.bloom_level + 1)

    return CheckpointResult(
        passed = true,
        score  = score,
        grade  = grade
    )
```

### 5.4 보충 학습 생성

```
function generate_remediation_plan(learner, weak_areas, phase):
    plan = RemediationPlan()

    for area in weak_areas:
        // 약점 영역별 추가 자료 + 실습 생성
        plan.add(RemediationItem(
            topic            = area.topic,
            bloom_level      = area.bloom_level,
            difficulty_target = area.avg_difficulty - 0.3,  // 약간 쉬운 난이도
            resources        = select_resources(area.topic, area.bloom_level, learner.preferred_style),
            exercises        = generate_exercises(area.topic, area.bloom_level, area.avg_difficulty - 0.3),
            estimated_hours  = estimate_remediation_hours(area)
        ))

    return plan
```

---

## 6. O-003-4: 소요 시간 추정 모델

### 6.1 추정 공식

```
function estimate_phase_hours(phase, profile):
    base_hours = 0

    // Step 1: 자료 학습 시간
    for resource in phase.resources:
        base_hours += resource.estimated_read_min / 60

    // Step 2: 실습 시간
    for exercise in phase.exercises:
        base_hours += exercise.estimated_min / 60

    // Step 3: 체크포인트 시간
    base_hours += phase.checkpoint.items_count * 3 / 60  // 문제당 3분

    // Step 4: 학습 속도 보정
    speed_multiplier = {
        "slow":   1.5,
        "normal": 1.0,
        "fast":   0.7
    }[profile.learning_speed]

    // Step 5: 난이도 보정
    // 높은 Bloom 레벨일수록 시간 증가
    bloom_multiplier = {
        1: 0.8,   // Remember  — 빠른 학습
        2: 0.9,   // Understand
        3: 1.0,   // Apply     — 기준
        4: 1.2,   // Analyze
        5: 1.4,   // Evaluate
        6: 1.6    // Create    — 가장 시간 소요
    }[phase.bloom_level]

    // Step 6: 최종 추정
    estimated = base_hours * speed_multiplier * bloom_multiplier

    // Step 7: 보충 학습 버퍼 (10%)
    estimated *= 1.1

    return round(estimated, 1)
```

### 6.2 완료일 추정

```
function calculate_completion_date(phases, weekly_hours):
    total_hours = sum(p.estimated_hours for p in phases)

    // 주당 학습 시간 기반 주 수 계산
    weeks_needed = total_hours / weekly_hours

    // 여유 버퍼 20% (예상치 못한 지연)
    weeks_with_buffer = weeks_needed * 1.2

    completion_date = today() + timedelta(weeks=weeks_with_buffer)
    return completion_date
```

### 6.3 동적 재추정

```
function recalculate_estimates(path):
    // 실제 소요시간 데이터가 쌓이면 추정 정확도 향상

    completed_phases = [p for p in path.phases if p.status == "completed"]
    if len(completed_phases) < 2:
        return  // 데이터 부족

    // 실제 vs 예상 비율 계산
    actual_ratios = [
        p.actual_hours / p.estimated_hours
        for p in completed_phases
    ]
    avg_ratio = mean(actual_ratios)

    // 남은 Phase 추정치 보정
    remaining = [p for p in path.phases if p.status != "completed"]
    for phase in remaining:
        phase.estimated_hours *= avg_ratio

    // 완료일 재계산
    path.estimated_completion = calculate_completion_date(
        remaining, path.learner.weekly_hours
    )
    path.total_estimated_hours = sum(p.estimated_hours for p in path.phases)
```

---

## 7. 동적 경로 조정

### 7.1 조정 트리거

| 트리거 | 조건 | 조정 내용 |
|--------|------|-----------|
| 체크포인트 우수 통과 | 점수 ≥ 90% | 다음 Phase 일부 스킵 가능 |
| 체크포인트 반복 실패 | 3회 연속 미달 | 보충 Phase 삽입 + 난이도 하향 |
| 학습 속도 변동 | 속도 분류 변경 | 남은 Phase 소요시간 재추정 |
| 목표 변경 | 사용자 목표 수정 | 경로 전체 재생성 |
| 장기 휴식 | 14일 이상 미접속 | 복습 Phase 삽입 + θ 감쇠 적용 |

### 7.2 경로 재조정 알고리즘

```
function adjust_path(path, trigger):
    if trigger == "excellent_pass":
        // 학습자가 예상보다 빠름 → 심화 콘텐츠로 전환
        next_phase = get_next_phase(path)
        if next_phase.bloom_level <= current_bloom - 1:
            skip_phase(next_phase)  // 이미 마스터한 레벨 스킵

    elif trigger == "repeated_failure":
        // 보충 Phase 삽입
        remediation_phase = create_remediation_phase(
            failed_phase = current_phase,
            learner      = path.learner
        )
        insert_phase_before(path, current_phase, remediation_phase)

    elif trigger == "long_break":
        // 복습 Phase 삽입 + θ 감쇠
        decay_theta(path.learner, days_inactive)
        review_phase = create_review_phase(
            last_completed = get_last_completed_phase(path),
            learner        = path.learner
        )
        insert_phase_after(path, get_last_completed_phase(path), review_phase)

    // 소요시간 재추정
    recalculate_estimates(path)
```

---

## 8. 학습 경로 예시

```
목표: "Python으로 퀀트 투자 시스템을 만들고 싶어"
학습자: learning_speed=normal, weekly_hours=10, skill_levels.python=level 1

생성 결과:

Phase 1 (10h): Python 기초 — Remember/Understand
  ├─ 자료: Python 기초 문법 가이드, 변수/함수/클래스 튜토리얼
  ├─ 실습: 기초 코딩 문제 10개 (θ=-1.0)
  ├─ 체크포인트: 5문항 (통과 70%)
  └─ 소요: ~10시간 (1주)

Phase 2 (12h): Python 중급 — Apply
  ├─ 자료: 모듈, 파일 I/O, 예외 처리
  ├─ 실습: 미니 프로젝트 2개 (θ=0.0)
  ├─ 체크포인트: 8문항 (통과 70%)
  └─ 소요: ~12시간 (1.2주)

Phase 3 (15h): 데이터 분석 (pandas, numpy) — Apply/Analyze
  ├─ 자료: pandas 공식 튜토리얼, numpy 기초
  ├─ 실습: 데이터 분석 프로젝트 1개 (θ=0.3)
  ├─ 체크포인트: 8문항 (통과 70%)
  └─ 소요: ~15시간 (1.5주)

Phase 4 (12h): 금융 데이터 (yfinance, DART API) — Apply
  ├─ 자료: yfinance 문서, DART API 가이드
  ├─ 실습: 실시간 데이터 수집 스크립트 (θ=0.3)
  ├─ 체크포인트: 8문항 (통과 70%)  // Apply(bloom=3) → 8문항
  └─ 소요: ~12시간 (1.2주)

Phase 5 (18h): 기술적 분석 (RSI, MACD, 볼린저) — Analyze/Evaluate
  ├─ 자료: 기술적 분석 이론, 지표 구현 가이드
  ├─ 실습: 지표 구현 + 백테스트 기초 (θ=0.7)
  ├─ 체크포인트: 10문항 (통과 70%)
  └─ 소요: ~18시간 (1.8주)

Phase 6 (20h): 백테스트 (backtrader) — Evaluate/Create
  ├─ 자료: backtrader 문서, 전략 설계 패턴
  ├─ 실습: 완전한 백테스트 시스템 구축 (θ=1.0)
  ├─ 체크포인트: 10문항 (통과 70%)
  └─ 소요: ~20시간 (2주)

Phase 7 (25h): 실전 시스템 구축 — Create
  ├─ 자료: 시스템 아키텍처, 리스크 관리
  ├─ 실습: 완전한 퀀트 투자 시스템 프로젝트 (θ=1.5)  // bloom_to_theta(Create)=1.5
  ├─ 체크포인트: 최종평가 25문항 (통과 70%)  // is_final_path_checkpoint=true → 15+min(6*2,10)=25문항
  └─ 소요: ~25시간 (2.5주)

총 소요: ~112시간 (~11.2주, 주 10시간 기준)
예상 완료일: 약 13.4주 후 (버퍼 20% 포함)
```

---

## 9. 교차 참조

| 참조 대상 | 파일 | 관계 |
|-----------|------|------|
| 적응형 엔진 코어 | `adaptive_engine.md` | 세션 오케스트레이션에서 경로 활용 |
| IRT 난이도 조정 | `difficulty_adjustment.md` | Phase 난이도 설정·θ 파라미터 |
| 학습자 프로필 | `learner_profile.md` | weekly_hours, learning_speed, goal, skill_levels 참조 |
| SM-2 교육 확장 | `../02_spaced-repetition/sm2_education_extension.md` | 체크포인트 결과 → 복습 카드 생성 (1-2 단계 생성 예정) |
| 종합계획서 부록 §A.3 | `EDUCATION_LEARNING_구조화_종합계획서.md` | Bloom 택소노미 적용 규칙 |
