# Difficulty Adjustment — IRT 기반 난이도 조정 알고리즘

| 항목 | 값 |
|------|-----|
| **파일** | `01_adaptive-learning/difficulty_adjustment.md` |
| **o_ids** | O-001-2 |
| **V단계** | V1 (로컬 MVP) |
| **Level** | L3 |
| **LOCK 참조** | LOCK-ED-02, LOCK-ED-03 |
| **SOT 출처** | STEP7-O O-001 (적응형 학습 엔진) |
| **상태** | COMPLETE |

---

## 1. 개요

IRT(Item Response Theory) 기반 난이도 조정 알고리즘은 학습자의 능력 파라미터(θ)를 실시간 추정하고, 정답률 목표 70-85%(Target Zone)를 유지하도록 다음 문제의 난이도를 자동 선택한다.

---

## 2. 5단계 난이도 분류 체계 (LOCK-ED-02)

> LOCK (LOCK-ED-02, 기존 명세 §2): IRT 기반 5단계 (Very Easy / Easy / Medium / Hard / Very Hard), 정답률 목표 70-85%

| 레벨 | 명칭 | θ 범위 | 예상 정답률 | 설명 |
|------|------|--------|------------|------|
| 1 | **Very Easy** | θ < −1.5 | > 90% | 기초 개념 확인, 자신감 형성 |
| 2 | **Easy** | −1.5 ≤ θ < −0.5 | 80-90% | 기본 적용, 개념 강화 |
| 3 | **Medium** | −0.5 ≤ θ < 0.5 | 70-85% | 표준 문제, Target Zone 중심 |
| 4 | **Hard** | 0.5 ≤ θ < 1.5 | 50-70% | 응용/분석, 도전적 학습 |
| 5 | **Very Hard** | θ ≥ 1.5 | < 50% | 창의적 문제 해결, 최고 수준 |

### 2.1 Target Zone: 정답률 70-85%

- 학습 효과가 최대화되는 구간 (Vygotsky ZPD 이론 기반)
- 너무 쉬우면(> 85%) 학습 효과 저하 → 난이도 상향
- 너무 어려우면(< 70%) 좌절 위험 → 난이도 하향
- ZPD 범위: θ + 0.3 ~ θ + 1.0 (정답률 50-70% 예상 구간)

---

## 3. IRT 모델 상세

### 3.1 2PL IRT 모델 (Two-Parameter Logistic)

```
P(θ, b, a) = 1 / (1 + exp(-a * (θ - b)))

where:
    θ = 학습자 능력 파라미터
    b = 문제 난이도 파라미터
    a = 문제 변별도 파라미터 (V1에서는 전체 문제 고정값 1.7 사용,
        V2에서 문제별 개별 변별도 도입 예정)
    P = 정답 확률
```

> **참고**: 종합계획서 부록 §A.2 의사코드는 `a = 1.7` 고정 상수로 정의한다. V1에서는 이 관례를 따르며, 모든 문제에 동일한 변별도 1.7을 적용한다.

### 3.2 θ 파라미터 추정 알고리즘 (EAP 방식)

```
function estimate_theta(learner, item_result):
    // EAP (Expected A Posteriori) 추정
    // 사전 분포: N(current_theta, sigma^2)
    // 우도: 2PL IRT 모델

    prior_theta = learner.theta
    sigma = 0.5  // 사전 분포 표준편차 (학습 초기 1.0, 안정기 0.3)

    // Step 1: 우도 계산
    p = probability_2pl(prior_theta, item.difficulty, item.discrimination)

    // Step 2: θ 업데이트 (간소화된 EAP)
    if item_result.correct:
        delta = LEARNING_RATE * (1 - p)  // 맞춤 → 능력 상향
    else:
        delta = -LEARNING_RATE * p       // 틀림 → 능력 하향

    // Step 3: 업데이트 크기 제한 (급격한 변동 방지)
    delta = clamp(delta, -0.3, +0.3)

    // Step 4: 새 θ 계산
    new_theta = prior_theta + delta

    // Step 5: θ 범위 제한
    new_theta = clamp(new_theta, -3.0, +3.0)

    return new_theta

LEARNING_RATE = 0.1  // 기본 학습률
```

### 3.3 σ(불확실성) 동적 조정

```
function update_sigma(learner, item_result):
    // 새로운 정보가 들어올수록 불확실성 감소
    // Fisher 정보량 기반
    p = probability_2pl(learner.theta, item.difficulty, item.discrimination)
    information = item.discrimination^2 * p * (1 - p)

    // σ 업데이트 (정보가 많을수록 σ 감소)
    learner.sigma = 1 / sqrt(1/learner.sigma^2 + information)

    // σ 범위 제한
    learner.sigma = clamp(learner.sigma, 0.1, 2.0)
```

---

## 4. 난이도 조정 알고리즘

### 4.1 핵심 알고리즘 의사코드

```
function adjust_difficulty(learner, item_result):
    // Phase 1: θ 업데이트
    learner.theta = estimate_theta(learner, item_result)

    // Phase 2: 최근 정답률 계산
    recent_accuracy = calculate_accuracy(learner.recent_items, window=10)

    // Phase 3: Target Zone 기반 난이도 선택
    if recent_accuracy > 0.85:
        // 너무 쉬움 → 난이도 상향
        target_difficulty = learner.theta + 0.3
        reason = "정답률 초과(>{:.0f}%) → 상향".format(recent_accuracy * 100)
    elif recent_accuracy < 0.70:
        // 너무 어려움 → 난이도 하향
        target_difficulty = learner.theta - 0.3
        reason = "정답률 미달(<{:.0f}%) → 하향".format(recent_accuracy * 100)
    else:
        // Target Zone 유지
        target_difficulty = learner.theta
        reason = "Target Zone 유지({:.0f}%)".format(recent_accuracy * 100)

    // Phase 4: 연속 패턴 보정
    streak = get_streak(learner.recent_items)
    if streak >= 3:      // 연속 3정답
        target_difficulty += 0.2
        reason += " + 연속정답 보정"
    elif streak <= -2:   // 연속 2오답
        target_difficulty -= 0.2
        reason += " + 연속오답 보정"

    // Phase 5: 좌절 방지 안전장치 (ZPD-5)
    // ZPD-5 원문: "정답률이 40% 이하로 3회 연속 하락 시 난이도 자동 하향"
    // 판정: 최근 3개 평가 윈도우의 정답률이 연속 하락 + 현재 40% 이하
    recent_windows = get_accuracy_windows(learner, window_size=5, count=3)
    declining_3times = all(
        recent_windows[i] > recent_windows[i+1]
        for i in range(len(recent_windows) - 1)
    )  // 3회 연속 정답률 하락 추세
    if declining_3times and recent_windows[-1] <= 0.40:
        target_difficulty = learner.theta - 1.0
        reason = "좌절 방지(ZPD-5) → 대폭 하향"

    // Phase 6: 문제 선택
    selected_item = select_item(
        target_difficulty = target_difficulty,
        tolerance         = 0.5,
        bloom_level       = learner.current_bloom_level,
        exclude           = learner.recently_seen_items
    )

    return DifficultyAdjustment(
        new_theta         = learner.theta,
        target_difficulty = target_difficulty,
        selected_item     = selected_item,
        reason            = reason,
        difficulty_level  = theta_to_level(target_difficulty)
    )
```

### 4.2 θ → 난이도 레벨 변환

```
function theta_to_level(theta):
    if theta < -1.5:
        return 1  // Very Easy
    elif theta < -0.5:
        return 2  // Easy
    elif theta < 0.5:
        return 3  // Medium
    elif theta < 1.5:
        return 4  // Hard
    else:
        return 5  // Very Hard
```

### 4.3 문제 선택 전략

```
function select_item(target_difficulty, tolerance, bloom_level, exclude):
    // Step 1: 후보 필터링
    candidates = item_pool.filter(
        difficulty  in [target_difficulty - tolerance, target_difficulty + tolerance],
        bloom_level == bloom_level,
        id not in exclude
    )

    // Step 2: 최적 문제 선택 (난이도 거리 최소화)
    if candidates.empty:
        // 풀에 적합한 문제 없음 → Bloom ±1 확장 탐색
        candidates = item_pool.filter(
            difficulty in [target_difficulty - tolerance * 1.5, target_difficulty + tolerance * 1.5],
            bloom_level in [bloom_level - 1, bloom_level, bloom_level + 1]
        )

    // Step 3: 변별도 우선 정렬 (변별도 높은 문제 = 능력 추정에 유리)
    candidates.sort_by(
        key = abs(candidate.difficulty - target_difficulty),
        secondary_key = -candidate.discrimination  // 변별도 높은 것 우선
    )

    // 확장 탐색 후에도 후보가 없으면 폴백: 미출제 문제 중 가장 쉬운 것
    if candidates.empty:
        return item_pool.easiest_unseen(exclude=exclude)
    // 확장 탐색 후에도 후보가 없으면 폴백: 미출제 문제 중 가장 쉬운 것
    if candidates.empty:
        return item_pool.easiest_unseen(exclude=exclude)
    return candidates[0]
```

---

## 5. 평가 기준 (LOCK-ED-03)

> LOCK (LOCK-ED-03, 기존 명세 §2): 진단테스트 + 진행평가 + 최종평가, 3등급 (미달 / 달성 / 우수)

### 5.1 평가 유형별 θ 추정 활용

| 평가 유형 | θ 활용 방식 | 문제 수 | σ 초기값 |
|-----------|-------------|---------|---------|
| **진단테스트** | CAT(Computerized Adaptive Testing) 방식으로 최소 문제로 θ 추정 | 10-20문항 | 1.0 (높은 불확실성) |
| **진행평가** | 현재 θ 기준 Target Zone 문제 출제 | 5-10문항 | 현재 σ 유지 |
| **최종평가** | θ 근처 + Bloom 상위 레벨 문제 혼합 출제 | 15-25문항 | 현재 σ 유지 |

### 5.2 진단테스트 CAT 알고리즘

```
function run_diagnostic_cat(learner, topic):
    // CAT: 적응적 검사 — 최소 문제로 θ 추정
    learner.theta = 0.0    // 중간 난이도에서 시작
    learner.sigma = 1.0    // 높은 불확실성

    for i in range(MAX_ITEMS = 20):
        // 현재 θ에 가장 정보량이 높은 문제 선택
        item = select_most_informative_item(learner.theta, topic)

        // 응답 수집
        result = await get_response(learner, item)

        // θ 업데이트
        learner.theta = estimate_theta(learner, result)
        update_sigma(learner, result)

        // 종료 조건: σ < 0.3 이면 충분히 정밀
        if learner.sigma < 0.3:
            break

    return DiagnosticResult(
        theta          = learner.theta,
        sigma          = learner.sigma,
        items_used     = i + 1,
        difficulty_level = theta_to_level(learner.theta),
        bloom_start    = determine_bloom_start(learner.theta)
    )
```

---

## 6. 데이터 구조

### 6.1 문제(Item) 스키마

```typescript
interface Item {
    id: string;
    topic: string;
    difficulty: number;        // IRT b 파라미터 (-3.0 ~ +3.0)
    discrimination: number;    // IRT a 파라미터 (0.5 ~ 2.5, 기본 1.7)
    bloom_level: BloomLevel;   // 1~6 (LOCK-ED-05)
    content: string;
    hints: Hint[];             // 3단계 힌트 (LOCK-ED-06)
    tags: string[];
    created_at: string;        // ISO 8601
}

type BloomLevel = 1 | 2 | 3 | 4 | 5 | 6;
// 1=Remember, 2=Understand, 3=Apply, 4=Analyze, 5=Evaluate, 6=Create

interface DifficultyLevel {
    level: 1 | 2 | 3 | 4 | 5;
    name: "Very Easy" | "Easy" | "Medium" | "Hard" | "Very Hard";
    theta_range: [number, number];
    expected_accuracy: [number, number];
}
```

### 6.2 학습자 능력 추적 스키마

```typescript
interface LearnerAbility {
    learner_id: string;
    topic: string;
    theta: number;             // 현재 능력 추정치
    sigma: number;             // 추정 불확실성
    recent_items: ItemResult[]; // 최근 10개 결과
    total_items: number;       // 총 응답 수
    current_streak: number;    // 양수=연속정답, 음수=연속오답
    difficulty_level: number;  // 현재 난이도 레벨 (1~5)
    last_updated: string;      // ISO 8601
}

interface ItemResult {
    item_id: string;
    correct: boolean;
    response_time_ms: number;
    hint_level_used: number;   // 0=힌트없음, 1~3=사용 단계
    bloom_level: BloomLevel;
    timestamp: string;
}
```

---

## 7. 교차 참조

| 참조 대상 | 파일 | 관계 |
|-----------|------|------|
| 적응형 엔진 코어 | `adaptive_engine.md` | DifficultyAdjuster 호출 원점 |
| 학습자 프로필 | `learner_profile.md` | θ, sigma 저장 대상 |
| 학습 경로 생성기 | `learning_path_generator.md` | Phase별 난이도 범위 지정 |
| 종합계획서 부록 §A.2 | `EDUCATION_LEARNING_구조화_종합계획서.md` | IRT 난이도 조정 프레임워크 |
| 종합계획서 부록 §A.4 | `EDUCATION_LEARNING_구조화_종합계획서.md` | ZPD 적용 규칙 |
