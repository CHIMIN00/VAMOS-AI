# Interactive Tutorial — 인터랙티브 코딩 튜토리얼 엔진

| 항목 | 값 |
|------|-----|
| **파일** | `03_coding-tutorial/interactive_tutorial.md` |
| **o_ids** | O-004-1, O-004-2 |
| **V단계** | V1 (로컬 MVP) |
| **Level** | L3 |
| **LOCK 참조** | LOCK-ED-06, LOCK-ED-02, LOCK-ED-05 |
| **SOT 출처** | STEP7-O O-004 (코딩 학습 특화), O-017 (실습 환경 통합) |
| **상태** | COMPLETE |

---

## 1. 개요

인터랙티브 코딩 튜토리얼 엔진은 학습자에게 "개념 설명 → 예제 코드 → 연습 문제 → 해설"의 4단계 학습 루프를 제공한다. 코드 실행 샌드박스를 내장하여 학습자가 브라우저/터미널에서 즉시 코드를 실행하고 실시간 피드백을 받을 수 있다.

소크라테스 교수법(LOCK-ED-06)을 힌트 시스템에 적용하여 직접 답을 주지 않고 학습자가 스스로 답에 도달하도록 유도하며, IRT 난이도(LOCK-ED-02)와 Bloom 택소노미(LOCK-ED-05)를 통해 학습자 수준에 맞는 문제를 적응적으로 제공한다.

---

## 2. 튜토리얼 세션 스키마

### 2.1 입력 스키마

```typescript
interface TutorialRequest {
    learner_id: string;                       // 학습자 프로필 ID
    topic: string;                            // 학습 주제 ("python_list", "react_hooks" 등)
    subtopic?: string;                        // 세부 주제 (선택)
    bloom_level?: BloomLevel;                 // 1~6 (지정 시 해당 레벨 문제만, 미지정 시 자동)
    language: ProgrammingLanguage;            // "python" | "javascript" | "typescript" | "java" | "go"
    session_duration_min?: number;            // 희망 세션 길이 (분, 기본 30)
}

type ProgrammingLanguage = "python" | "javascript" | "typescript" | "java" | "go";
type BloomLevel = 1 | 2 | 3 | 4 | 5 | 6;
```

### 2.2 출력 스키마

```typescript
interface TutorialSession {
    session_id: string;
    learner_id: string;
    topic: string;
    language: ProgrammingLanguage;

    // 4단계 학습 루프
    steps: TutorialStep[];

    // 세션 결과
    result: SessionResult;
}

interface TutorialStep {
    order: number;                            // 1~N
    phase: "explain" | "example" | "exercise" | "review";
    content: StepContent;
    bloom_level: BloomLevel;
    estimated_minutes: number;
}

interface StepContent {
    // Phase: explain
    explanation?: string;                     // 마크다운 개념 설명
    key_concepts?: string[];                  // 핵심 개념 키워드

    // Phase: example
    example_code?: string;                    // 예제 코드
    example_output?: string;                  // 예상 출력
    line_annotations?: Record<number, string>; // 줄별 주석

    // Phase: exercise
    exercise?: ExerciseSpec;

    // Phase: review
    review?: ReviewSummary;
}

interface ExerciseSpec {
    prompt: string;                           // 문제 설명
    starter_code: string;                     // 시작 코드 (빈칸 포함)
    test_cases: TestCase[];                   // 자동 채점 테스트
    hints: SocraticHint[];                    // 소크라테스 힌트 3단계
    time_limit_sec: number;                   // 코드 실행 제한 시간
    memory_limit_mb: number;                  // 메모리 제한
    difficulty_theta: number;                 // IRT θ (LOCK-ED-02)
}

interface TestCase {
    input: string;
    expected_output: string;
    is_hidden: boolean;                       // 숨김 테스트 여부
    explanation?: string;                     // 오답 시 표시할 설명
}

interface SessionResult {
    steps_completed: number;
    total_steps: number;
    exercises_attempted: number;
    exercises_passed: number;
    hints_used: number;
    time_spent_min: number;
    bloom_levels_covered: BloomLevel[];
    theta_delta: number;                      // θ 변화량
    xp_earned: number;                        // 경험치
}
```

---

## 3. 코드 실행 샌드박스

### 3.1 샌드박스 아키텍처

```
┌──────────────────────────────────────────┐
│              Tutorial Engine              │
│  ┌─────────┐  ┌──────────┐  ┌─────────┐ │
│  │ Content  │  │ Socratic │  │  IRT    │ │
│  │Generator │  │  Hint    │  │Selector │ │
│  └────┬─────┘  └────┬─────┘  └────┬────┘ │
│       └──────────────┼─────────────┘      │
│                      ▼                    │
│              ┌──────────────┐             │
│              │  Session Mgr  │             │
│              └──────┬───────┘             │
└─────────────────────┼─────────────────────┘
                      ▼
         ┌────────────────────────┐
         │    Sandbox Runtime     │
         │  ┌──────┐ ┌────────┐  │
         │  │Docker │ │Resource│  │
         │  │  /    │ │Limiter │  │
         │  │Wasm   │ │        │  │
         │  └──┬───┘ └────────┘  │
         │     ▼                 │
         │  ┌──────────────┐     │
         │  │  Code Runner  │     │
         │  │  (isolated)   │     │
         │  └──────────────┘     │
         └────────────────────────┘
```

### 3.2 샌드박스 실행 의사코드

```
function execute_code(submission: CodeSubmission):
    // Step 1: 보안 검증
    if contains_forbidden_patterns(submission.code):
        return ExecutionResult(
            status = "SECURITY_ERROR",
            message = "허용되지 않은 코드 패턴이 감지되었습니다."
        )

    // Step 2: 런타임 생성
    runtime = create_sandbox(
        language    = submission.language,
        time_limit  = submission.time_limit_sec,   // 기본 10초
        memory_limit = submission.memory_limit_mb,  // 기본 256MB
        network     = false,                        // 네트워크 차단
        filesystem  = "read_only"                   // 파일시스템 읽기 전용
    )

    // Step 3: 코드 실행
    try:
        result = runtime.run(submission.code, stdin=submission.input)
        return ExecutionResult(
            status = "SUCCESS",
            stdout = result.stdout,
            stderr = result.stderr,
            execution_time_ms = result.time_ms,
            memory_used_mb = result.memory_mb
        )
    catch TimeoutError:
        return ExecutionResult(status = "TIMEOUT")
    catch MemoryError:
        return ExecutionResult(status = "MEMORY_EXCEEDED")
    catch RuntimeError as e:
        return ExecutionResult(
            status = "RUNTIME_ERROR",
            error_explanation = explain_error(e, submission.language)
        )
    finally:
        runtime.destroy()

FORBIDDEN_PATTERNS = {
    "python":     ["os.system", "subprocess", "eval(", "exec(", "__import__", "open("],
    "javascript": ["child_process", "fs.", "eval(", "Function(", "require("],
    "java":       ["Runtime.getRuntime", "ProcessBuilder", "System.exit"],
    "go":         ["os/exec", "syscall", "unsafe.Pointer"]
}
```

### 3.3 에러 설명 엔진

```
function explain_error(error, language):
    // O-004-1: 에러 → 원인 → 해결법 → 유사 상황
    explanation = LLM.generate(
        system_prompt = ERROR_EXPLANATION_PROMPT,
        context = {
            "error_type":    error.type,
            "error_message": error.message,
            "code_snippet":  error.relevant_lines,
            "language":      language,
            "learner_level": get_learner_level()
        },
        output_format = {
            "error_summary":    "에러 한줄 요약",
            "cause":            "원인 설명 (학습자 수준에 맞게)",
            "fix":              "해결 방법 (코드 예시 포함)",
            "similar_cases":    "유사 상황 1~2개",
            "prevention_tip":   "예방 팁"
        }
    )
    return explanation
```

### 3.4 성능 SLA

| 지표 | 목표 | 비고 |
|------|------|------|
| 코드 실행 응답 시간 | ≤ 3초 (Python/JS), ≤ 5초 (Java/Go 컴파일) | 타임아웃 기본 10초 |
| 샌드박스 생성 시간 | ≤ 500ms (Wasm), ≤ 2초 (Docker) | 풀링으로 단축 |
| 동시 실행 세션 | ≥ 50 | V1 로컬 기준 10 |
| 가용성 | ≥ 99.5% | |
| LLM 피드백 응답 | ≤ 5초 | 에러 설명, 힌트 생성 포함 |

---

## 4. 소크라테스 힌트 시스템 (LOCK-ED-06)

> LOCK (LOCK-ED-06, STEP7-O O-001): 직접 답 금지 → 질문 유도 → 힌트 3단계 → 사고 과정 유도 → 격려 피드백

### 4.1 힌트 스키마

```typescript
interface SocraticHint {
    level: 1 | 2 | 3;
    trigger: HintTrigger;
    content: string;
    guiding_question: string;          // 역질문 (답 대신)
    metacognitive_prompt: string;      // 사고 과정 유도
    encouragement: string;             // 격려 피드백
    xp_penalty: number;               // 힌트 사용 시 XP 차감률 (0.0~0.3)
}

type HintTrigger =
    | "user_request"                   // 학습자가 힌트 요청
    | "timeout"                        // 제한 시간의 60% 경과
    | "repeated_error";                // 동일 에러 3회 반복

interface HintState {
    current_level: 0 | 1 | 2 | 3;     // 0 = 힌트 미사용
    hints_given: SocraticHint[];
    total_penalty: number;             // 누적 XP 차감률
}
```

### 4.2 3단계 힌트 의사코드

```
function provide_hint(exercise, learner_state, hint_state):
    // LOCK-ED-06 원칙: 직접 답을 절대 제공하지 않는다
    next_level = hint_state.current_level + 1
    if next_level > 3:
        // 3단계 모두 소진 → 부분 답 공개 + 유사 문제로 전환
        return HintResponse(
            action = "REDIRECT",
            message = "이 문제는 잠시 넘어가고, 비슷하지만 조금 더 쉬운 문제를 풀어볼까요?",
            redirect_exercise = find_easier_variant(exercise, learner_state.theta)
        )

    // === Level 1: 방향 제시 ===
    if next_level == 1:
        hint = SocraticHint(
            level = 1,
            content = generate_direction_hint(exercise),
            // 예: "이 문제에서 어떤 자료구조가 가장 적합할지 생각해보세요."
            guiding_question = generate_guiding_question(exercise, "direction"),
            // 예: "배열을 순회하면서 무언가를 빠르게 찾아야 한다면, 어떤 자료구조가 떠오르나요?"
            metacognitive_prompt = "지금까지 시도한 접근 방식을 한 문장으로 정리해볼까요?",
            encouragement = "좋은 시도예요! 방향을 조금만 바꿔보면 됩니다.",
            xp_penalty = 0.0    // Level 1은 패널티 없음
        )

    // === Level 2: 핵심 개념 명시 ===
    elif next_level == 2:
        hint = SocraticHint(
            level = 2,
            content = generate_concept_hint(exercise),
            // 예: "HashMap의 lookup 시간 복잡도는 O(1)입니다. 이걸 활용할 수 있을까요?"
            guiding_question = generate_guiding_question(exercise, "concept"),
            // 예: "target에서 현재 숫자를 빼면 무엇이 남나요? 그 값을 어떻게 빠르게 찾을 수 있을까요?"
            metacognitive_prompt = "힌트를 보고 떠오른 아이디어를 코드로 표현해볼 수 있을까요?",
            encouragement = "핵심에 가까워지고 있어요!",
            xp_penalty = 0.1
        )

    // === Level 3: 부분 답 공개 ===
    elif next_level == 3:
        hint = SocraticHint(
            level = 3,
            content = generate_partial_solution_hint(exercise),
            // 예: "complement = target - nums[i]를 key로 사용하는 방식을 생각해보세요."
            guiding_question = generate_guiding_question(exercise, "implementation"),
            // 예: "이 로직을 for 루프 안에 넣으면 어떻게 될까요? 반환 조건은 무엇일까요?"
            metacognitive_prompt = "이 접근법의 시간 복잡도는 어떻게 되는지 분석해보세요.",
            encouragement = "거의 다 왔어요! 마지막 퍼즐 조각만 맞추면 됩니다.",
            xp_penalty = 0.2
        )

    // 힌트 상태 갱신
    hint_state.current_level = next_level
    hint_state.hints_given.append(hint)
    hint_state.total_penalty += hint.xp_penalty

    return HintResponse(action = "HINT", hint = hint)
```

### 4.3 자동 힌트 트리거

```
function check_auto_hint_trigger(exercise, learner_activity):
    // Trigger 1: 타임아웃 — 제한 시간의 60% 경과 시
    elapsed_ratio = learner_activity.elapsed_sec / exercise.time_limit_sec
    if elapsed_ratio >= 0.6 and learner_activity.submissions == 0:
        return "timeout"

    // Trigger 2: 반복 에러 — 동일 에러 타입 3회
    recent_errors = learner_activity.recent_errors[-5:]
    error_counts = count_by_type(recent_errors)
    if any(count >= 3 for count in error_counts.values()):
        return "repeated_error"

    // Trigger 3: 무활동 — 2분 이상 입력 없음
    if learner_activity.idle_seconds >= 120:
        return "idle"

    return null  // 트리거 없음
```

### 4.4 소크라테스 대화 전략 (오답 시)

```
function handle_wrong_answer(exercise, submission, learner_state):
    // LOCK-ED-06: 오답에도 직접 답을 주지 않는다
    analysis = analyze_submission(exercise, submission)

    response = SocraticResponse()

    // 1. 올바른 부분 인정
    if analysis.correct_parts:
        response.encouragement = f"'{analysis.correct_parts[0]}'은 좋은 접근이에요!"

    // 2. 오류 부분에 역질문
    if analysis.error_type == "logic_error":
        response.question = f"line {analysis.error_line}에서 {analysis.variable}의 값이 " +
                           f"어떻게 변하는지 손으로 추적해볼 수 있을까요?"
    elif analysis.error_type == "edge_case":
        response.question = f"입력이 {analysis.failing_input}일 때 어떤 일이 일어나나요?"
    elif analysis.error_type == "wrong_algorithm":
        response.question = "현재 접근법의 시간 복잡도는 어떻게 되나요? 더 효율적인 방법이 있을까요?"

    // 3. 반례 제시 (답이 아닌 반례)
    if analysis.counterexample:
        response.counterexample = analysis.counterexample

    // 4. 메타인지 유도
    response.metacognitive = "지금까지의 접근 방식에서 어떤 가정을 했는지 돌아볼까요?"

    return response
```

---

## 5. 4단계 학습 루프

### 5.1 루프 파이프라인

```
function run_tutorial_session(request: TutorialRequest):
    profile = load_learner_profile(request.learner_id)
    theta = profile.abilities[request.topic]?.theta ?? 0.0
    bloom = profile.bloom_progress[request.topic]?.current_level ?? 1

    // Step 1: 커리큘럼 생성
    curriculum = generate_curriculum(
        topic          = request.topic,
        language       = request.language,
        theta          = theta,
        bloom_level    = request.bloom_level ?? bloom,
        duration_min   = request.session_duration_min ?? 30
    )

    session = TutorialSession(steps = [])

    for unit in curriculum.units:
        // Phase 1: EXPLAIN — 개념 설명
        explanation = generate_explanation(
            topic       = unit.concept,
            bloom_level = unit.bloom_level,
            learner_level = theta,
            language    = request.language
        )
        session.steps.append(TutorialStep(
            phase = "explain",
            content = StepContent(
                explanation  = explanation.text,
                key_concepts = explanation.keywords
            ),
            bloom_level = unit.bloom_level
        ))

        // Phase 2: EXAMPLE — 예제 코드
        example = generate_example(
            concept  = unit.concept,
            language = request.language,
            theta    = theta
        )
        session.steps.append(TutorialStep(
            phase = "example",
            content = StepContent(
                example_code     = example.code,
                example_output   = example.output,
                line_annotations = example.annotations
            ),
            bloom_level = unit.bloom_level
        ))

        // Phase 3: EXERCISE — 연습 문제
        exercise = select_exercise(
            concept     = unit.concept,
            language    = request.language,
            theta       = theta,
            bloom_level = unit.bloom_level
        )
        session.steps.append(TutorialStep(
            phase = "exercise",
            content = StepContent(exercise = exercise),
            bloom_level = unit.bloom_level
        ))
        hint_state = HintState(current_level = 0)
        exercise_result = await run_exercise_loop(exercise, hint_state)

        // Phase 4: REVIEW — 해설 + 피드백
        review = generate_review(exercise, exercise_result, profile)
        session.steps.append(TutorialStep(
            phase = "review",
            content = StepContent(review = review),
            bloom_level = unit.bloom_level
        ))

        // θ 갱신
        theta = update_theta(theta, exercise_result)

    // 세션 결과 저장
    session.result = calculate_session_result(session)
    update_learner_profile(profile, session.result)
    return session
```

### 5.2 커리큘럼 생성

```
function generate_curriculum(topic, language, theta, bloom_level, duration_min):
    // 세션 시간 내 소화 가능한 유닛 수 계산
    avg_unit_min = 8   // explain(2) + example(2) + exercise(3) + review(1)
    max_units = floor(duration_min / avg_unit_min)
    max_units = clamp(max_units, min=2, max=6)

    // Bloom 레벨에 맞는 개념 선택
    concepts = get_topic_concepts(topic)
    selected = []
    for concept in concepts:
        if len(selected) >= max_units:
            break
        if concept.bloom_level == bloom_level:
            // IRT: θ 기준 ±0.5 범위 내 난이도 선택 (LOCK-ED-02)
            if abs(concept.difficulty_theta - theta) <= 0.5:
                selected.append(concept)

    // 부족하면 인접 Bloom 레벨에서 보충
    if len(selected) < 2:
        selected += get_adjacent_bloom_concepts(topic, bloom_level, theta, needed=2-len(selected))

    return Curriculum(units = selected)
```

---

## 6. 에러 처리

| 에러 상황 | 감지 조건 | 복구 전략 |
|-----------|-----------|-----------|
| 샌드박스 생성 실패 | Docker/Wasm 초기화 에러 | Wasm 폴백 → 실패 시 정적 실행 결과 표시 |
| 코드 실행 타임아웃 | time_limit_sec 초과 | 타임아웃 메시지 + 무한루프 힌트 제공 |
| 메모리 초과 | memory_limit_mb 초과 | 메모리 사용량 안내 + 최적화 힌트 |
| LLM 힌트 생성 실패 | API 타임아웃/에러 | 사전 생성된 정적 힌트 폴백 |
| 학습자 프로필 로드 실패 | DB 연결 에러 | 임시 프로필로 세션 진행, 종료 시 머지 |
| 보안 패턴 감지 | FORBIDDEN_PATTERNS 매칭 | 실행 차단 + 보안 설명 메시지 |

---

## 7. 프라이버시 / 보안

| 규칙 | 설명 |
|------|------|
| SEC-TUT-01 | 학습자 코드는 세션 종료 후 24시간 내 샌드박스에서 삭제 |
| SEC-TUT-02 | 코드 실행 시 네트워크 접근 완전 차단 (egress = none) |
| SEC-TUT-03 | 파일시스템 읽기 전용, /tmp만 쓰기 허용 |
| SEC-TUT-04 | 힌트/피드백 LLM 호출 시 학습자 개인정보 마스킹 |
| SEC-TUT-05 | 실행 로그는 통계 목적으로만 보존 (코드 원문 미저장, 해시만 보관) |

---

## 8. 통합 테스트 시나리오

| # | 시나리오 | 입력 | 기대 결과 |
|---|----------|------|-----------|
| T1 | 정상 세션 완료 | Python 리스트 주제, θ=0.0 | 4단계 루프 2~4회 실행, θ 변화량 기록 |
| T2 | 힌트 3단계 소진 | 학습자 3회 힌트 요청 | Level 1→2→3 순차 제공 후 유사 문제 전환 |
| T3 | 자동 힌트 트리거 | 60% 시간 경과 + 제출 0회 | 자동 Level 1 힌트 팝업 |
| T4 | 보안 패턴 차단 | `os.system("rm -rf /")` 제출 | SECURITY_ERROR 반환, 실행 차단 |
| T5 | 타임아웃 처리 | 무한루프 코드 제출 | TIMEOUT 반환 + 무한루프 설명 힌트 |
| T6 | 에러 설명 | IndexError 발생 코드 | 원인/해결법/유사상황/예방팁 4항목 반환 |
| T7 | Bloom 순서 보장 | Apply(3) 미달 학습자가 Analyze(4) 요청 | 거부 + Apply 문제 제공 (R-08-2) |
| T8 | 오답 소크라테스 응답 | 오답 제출 | 직접 답 없이 역질문 + 반례 + 격려 반환 |

---

## 9. UX / 게이미피케이션

| 요소 | 설명 |
|------|------|
| XP 획득 | 연습 문제 정답 시 기본 10 XP, 힌트 미사용 보너스 +5 XP |
| 힌트 패널티 | Level 1: 0%, Level 2: -10%, Level 3: -20% |
| 스트릭 보너스 | 연속 정답 3문제: ×1.5 XP, 5문제: ×2.0 XP |
| 진행 바 | 세션 내 단계 진행률 시각화 |
| 코드 실행 결과 | 성공 시 녹색 체크, 실패 시 빨간 X + 실패 테스트 표시 |
| 시간 표시 | 코드 실행 시간 + 메모리 사용량 표시 |

---

## 10. 교차 참조

| 참조 대상 | 파일 | 관계 |
|-----------|------|------|
| IRT 난이도 조정 | `../01_adaptive-learning/difficulty_adjustment.md` | θ 파라미터 기반 문제 난이도 선택 |
| 학습자 프로필 | `../01_adaptive-learning/learner_profile.md` | 세션 결과 → 프로필 θ/Bloom 갱신 |
| Bloom 택소노미 | 종합계획서 부록 §A.3 | Bloom 순서 보장 규칙 (R-08-2) 적용 |
| SM-2 플래시카드 | `../02_spaced-repetition/sm2_education_extension.md` | 세션 중 핵심 개념 → 플래시카드 자동 생성 |
| LeetCode 문제 | `leetcode_style_problems.md` | exercise 단계에서 LeetCode 풀 활용 |
| 코드 리뷰 학습 | `code_review_learning.md` | review 단계에서 코드 리뷰 피드백 연동 |
| 학습 대시보드 | `../05_learning-analytics/learning_dashboard.md` | 세션 결과 시각화 (1-5 단계 생성 예정) |

---

## 11. V2/V3 확장 예정

| V단계 | 항목 | 설명 |
|-------|------|------|
| V2 | 멀티 언어 동시 비교 | 동일 문제를 Python/JS/Java로 동시 풀이 비교 |
| V2 | 협업 세션 | 페어 프로그래밍 모드 (학습자 2인 동시 참여) |
| V3 | GPU 샌드박스 | ML/딥러닝 튜토리얼용 GPU 실행 환경 |
| V3 | 음성 인터랙션 | 소크라테스 대화를 음성으로 진행 |
