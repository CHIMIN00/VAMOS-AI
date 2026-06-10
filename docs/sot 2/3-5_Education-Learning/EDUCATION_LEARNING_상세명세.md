# EDUCATION_LEARNING 상세명세

> **Tier**: 3 (Feature Domains) | **Part2 Status**: SHELL (CAT-E + UI 1개) | **SOT**: STEP7-O (68 items)
> **Version**: 1.0.0 | **최종수정**: 2026-03-22
> **교차참조**: T2-CORE_AI → LLM 교육응답, T3-PKM → SM-2 공유/지식그래프, T3-Multimodal → 교육미디어

---

## 1. 개요

VAMOS Education/Learning 모듈은 개인화된 적응형 학습 경험을 제공한다.
Khanmigo 스타일의 소크라틱 메서드, SM-2 간격 반복, 코딩 튜토리얼,
자동 콘텐츠 생성, 학습 분석을 통합하여 사용자의 지속적 성장을 지원한다.

### 1.1 학습 모듈 구성

```
[적응형 학습 엔진] ←→ [SM-2 간격 반복]
       ↕                     ↕
[코딩 튜토리얼] ←→ [교육 컨텐츠 생성]
       ↕                     ↕
       └──→ [학습 분석 대시보드] ←──┘
```

---

## 2. 적응형 학습 엔진

### 2.1 소크라틱 메서드 구현 (Khanmigo-style)

```python
# socratic_engine.py
class SocraticEngine:
    """소크라틱 대화법 기반 학습 지원 엔진"""

    SOCRATIC_PRINCIPLES = [
        "직접 답을 주지 않는다",
        "유도 질문으로 사고를 이끈다",
        "학습자의 기존 지식을 확인한다",
        "오류를 지적하되 스스로 수정하게 한다",
        "단계적으로 난이도를 높인다",
    ]

    RESPONSE_STRATEGIES = {
        "stuck": [
            "힌트 제공 (직접 답 X)",
            "문제를 더 작은 단위로 분해",
            "유사한 쉬운 문제 제시",
            "관련 개념 복습 유도",
        ],
        "wrong_answer": [
            "왜 그렇게 생각했는지 질문",
            "반례 제시",
            "가정을 다시 검토하도록 유도",
        ],
        "correct": [
            "이해도 확인 질문",
            "심화 문제 제시",
            "관련 개념 연결",
        ],
        "partial": [
            "맞는 부분 인정",
            "부족한 부분에 대한 유도 질문",
        ],
    }

    async def generate_response(
        self, context: LearningContext, student_input: str
    ) -> SocraticResponse:
        # 1. 학생 답변 평가
        evaluation = await self._evaluate_answer(context, student_input)

        # 2. 전략 선택
        strategy = self.RESPONSE_STRATEGIES[evaluation.category]

        # 3. 소크라틱 응답 생성
        response = await self._generate_with_strategy(
            context=context,
            evaluation=evaluation,
            strategy=strategy,
            difficulty_level=context.current_difficulty,
        )

        # 4. 난이도 조절 판단
        new_difficulty = self._adjust_difficulty(context, evaluation)

        return SocraticResponse(
            message=response,
            hints_remaining=context.hints_remaining - (1 if evaluation.hint_used else 0),
            new_difficulty=new_difficulty,
            understanding_score=evaluation.understanding,
        )
```

### 2.2 난이도 자동 조절 알고리즘

```python
# difficulty_adjuster.py
class HeuristicDifficultyAdjuster:
    """휴리스틱(연속/정답률) 기반 난이도 조절 — IRT(θ 추정/2PL/EAP)는 difficulty_adjustment.md §3~§5 정본 참조 (본 레거시 명세는 MVP 휴리스틱)"""

    DIFFICULTY_LEVELS = {
        1: "입문 (기초 개념)",
        2: "초급 (단순 적용)",
        3: "중급 (복합 문제)",
        4: "중상급 (응용/분석)",
        5: "고급 (창의적 문제해결)",
    }

    def adjust(self, history: list[AttemptRecord]) -> DifficultyAdjustment:
        """
        최근 N개 시도 기반 난이도 조절:
        - 연속 3회 정답 → 난이도 +1
        - 연속 2회 오답 → 난이도 -1
        - 정답률 70~85% → 유지 (최적 학습 구간)
        - 정답률 > 85% → +1
        - 정답률 < 50% → -1
        """
        recent = history[-10:]  # 최근 10개
        correct_rate = sum(1 for a in recent if a.correct) / len(recent) if recent else 0.5

        # 연속 패턴 검사
        streak = self._get_streak(recent)

        if streak >= 3 and streak > 0:
            return DifficultyAdjustment(delta=+1, reason="연속 정답")
        elif streak <= -2:
            return DifficultyAdjustment(delta=-1, reason="연속 오답")
        elif correct_rate > 0.85:
            return DifficultyAdjustment(delta=+1, reason="높은 정답률")
        elif correct_rate < 0.50:
            return DifficultyAdjustment(delta=-1, reason="낮은 정답률")
        else:
            return DifficultyAdjustment(delta=0, reason="최적 학습 구간")

    def _get_streak(self, attempts: list[AttemptRecord]) -> int:
        """양수=연속정답, 음수=연속오답"""
        if not attempts:
            return 0
        streak = 0
        last_correct = attempts[-1].correct
        for a in reversed(attempts):
            if a.correct == last_correct:
                streak += 1 if last_correct else -1
            else:
                break
        return streak
```

### 2.3 학습 경로 생성

```python
# learning_path_generator.py
class LearningPathGenerator:
    """사용자 목표/수준 기반 개인화 학습 경로 생성"""

    async def generate(self, profile: LearnerProfile, goal: LearningGoal) -> LearningPath:
        """
        1. 목표 분석: 최종 목표 → 필수 스킬/지식 분해
        2. 현재 수준 평가: 진단 테스트 or 이전 학습 데이터
        3. 갭 분석: 목표 스킬 - 현재 스킬
        4. 경로 생성: 전제 조건 그래프 기반 토폴로지 정렬
        5. 일정 추정: 주당 학습 시간 기반 완료 예상일
        """
        required_skills = await self._decompose_goal(goal)
        current_skills = await self._assess_current(profile)
        gaps = self._analyze_gaps(required_skills, current_skills)
        path = self._topological_sort(gaps, prerequisites=self.skill_graph)

        return LearningPath(
            goal=goal,
            modules=[
                LearningModule(
                    skill=skill,
                    estimated_hours=self._estimate_hours(skill, profile.learning_speed),
                    resources=await self._find_resources(skill),
                    exercises=await self._generate_exercises(skill, profile.level),
                )
                for skill in path
            ],
            estimated_completion=self._estimate_completion(path, profile.weekly_hours),
        )
```

### 2.4 학습자 프로필 스키마

```typescript
// learner_profile.ts
interface LearnerProfile {
  id: string;
  user_id: string;

  // 수준 정보
  skill_levels: Record<string, SkillLevel>;   // {"python": {level: 3, confidence: 0.8}}
  overall_level: number;                       // 1~5
  learning_speed: "slow" | "normal" | "fast";

  // 학습 선호
  preferred_style: "visual" | "reading" | "practice" | "mixed";
  preferred_language: string;                  // "ko"
  session_duration_pref_min: number;           // 선호 세션 길이 (분)
  weekly_hours: number;                        // 주당 학습 가용 시간

  // 통계
  total_study_hours: number;
  total_exercises_completed: number;
  current_streak_days: number;
  longest_streak_days: number;
  topics_mastered: string[];

  // SM-2 통합
  active_flashcards: number;
  cards_due_today: number;
  average_retention_rate: number;              // 0.0 ~ 1.0
}

interface SkillLevel {
  level: number;           // 1~5
  confidence: number;      // 0.0 ~ 1.0
  last_assessed: string;   // ISO 8601
  exercises_done: number;
  correct_rate: number;
}
```

---

## 3. SM-2 간격 반복 (교육 특화)

### 3.1 교육용 SM-2 확장

```python
# education_sm2.py
class EducationSM2(SM2Algorithm):
    """교육 도메인 특화 SM-2 확장 (T3-PKM SM-2 상속)"""

    async def calculate_next_review(self, card: EducationFlashCard, quality: int) -> ReviewSchedule:
        # 기본 SM-2 계산
        schedule = super().calculate_next_review(card, quality)

        # 교육 특화 보정
        # 1. 난이도 가중: 어려운 카드는 간격 축소
        if card.difficulty >= 4:
            schedule.interval_days = int(schedule.interval_days * 0.8)

        # 2. 관련 카드 연쇄 복습: 전제 카드가 틀리면 후속 카드도 복습
        if quality < 3 and card.dependent_cards:
            for dep_card_id in card.dependent_cards:
                await self._schedule_cascade_review(dep_card_id)

        # 3. 망각 곡선 기반 최적 타이밍 보정
        optimal_timing = self._ebbinghaus_correction(card)
        schedule.next_review = max(schedule.next_review, optimal_timing)

        return schedule

    def _ebbinghaus_correction(self, card: EducationFlashCard) -> datetime:
        """에빙하우스 망각곡선: R = e^(-t/S), S=기억 안정성"""
        stability = card.easiness_factor * card.repetition * 0.5
        target_retention = 0.85  # 85% 유지 목표
        optimal_days = -stability * math.log(target_retention)
        return datetime.now() + timedelta(days=max(1, optimal_days))
```

### 3.2 플래시카드 자동 생성

```python
# flashcard_generator.py
class FlashCardGenerator:
    """학습 콘텐츠에서 플래시카드 자동 생성"""

    CARD_TYPES = {
        "concept_definition": {
            "front_template": "{concept}이란 무엇인가?",
            "back_template": "{definition}",
        },
        "code_output": {
            "front_template": "다음 코드의 출력은?\n```\n{code}\n```",
            "back_template": "{output}\n\n설명: {explanation}",
        },
        "cloze_deletion": {
            "front_template": "{text_with_blank}",
            "back_template": "{answer}",
        },
        "comparison": {
            "front_template": "{concept_a}와 {concept_b}의 차이점은?",
            "back_template": "{differences}",
        },
    }

    async def generate_from_content(
        self, content: str, topic: str, difficulty: int
    ) -> list[EducationFlashCard]:
        """LLM 기반 콘텐츠 → 플래시카드 변환"""
        prompt = f"""
        다음 학습 내용에서 핵심 개념을 플래시카드로 변환하세요.
        주제: {topic}, 난이도: {difficulty}/5
        카드 유형: concept_definition, code_output, cloze_deletion, comparison

        내용:
        {content}
        """
        cards = await self.llm.generate(prompt, output_schema=FlashCardListSchema)
        return cards
```

### 3.3 복습 스케줄링

```typescript
// review_scheduler.ts
interface ReviewSession {
  date: string;                    // ISO 8601
  cards_due: FlashCardSummary[];
  estimated_duration_min: number;
  priority_order: string[];        // 카드 ID 순서 (중요도+긴급도 정렬)
}

interface ReviewScheduleConfig {
  daily_card_limit: number;        // 하루 최대 복습 카드 수 (default 50)
  new_cards_per_day: number;       // 하루 신규 카드 수 (default 10)
  review_time_preference: string;  // "morning" | "evening" | "anytime"
  interleaving: boolean;           // 주제 섞기 여부 (default true)
  min_interval_hours: number;      // 같은 카드 최소 간격 (default 4)
}
```

---

## 4. 코딩 튜토리얼 시스템

### 4.1 LeetCode-style 문제 구조

```typescript
// coding_problem.ts
interface CodingProblem {
  id: string;
  title: string;
  description: string;             // 마크다운 (예제 포함)
  difficulty: 1 | 2 | 3 | 4 | 5;
  category: string;                // "array", "dp", "graph", "string"...
  tags: string[];
  constraints: string[];           // 제약 조건
  examples: Example[];
  test_cases: TestCase[];          // 숨겨진 테스트 케이스
  hints: Hint[];                   // 단계별 힌트
  solution_template: Record<string, string>;  // 언어별 템플릿
  time_limit_ms: number;
  memory_limit_mb: number;
  related_concepts: string[];      // 연관 학습 개념
  prerequisite_problems: string[]; // 선행 문제
}

interface Hint {
  level: number;                   // 1=약한 힌트, 3=강한 힌트
  content: string;
  penalty: number;                 // 힌트 사용 시 점수 감점 (0.0~0.3)
}

interface Example {
  input: string;
  output: string;
  explanation?: string;
}
```

### 4.2 단계별 힌트 시스템

```python
# hint_system.py
class HintSystem:
    """단계별 힌트 제공 (소크라틱 메서드 연동)"""

    HINT_LEVELS = {
        1: "방향 제시 (어떤 자료구조/알고리즘을 고려해볼까?)",
        2: "접근법 힌트 (구체적 알고리즘 이름/패턴)",
        3: "핵심 로직 설명 (의사코드 수준)",
        4: "부분 코드 제공 (핵심 함수 시그니처 + 주석)",
        5: "전체 풀이 (최후 수단, 학습 효과 최소)",
    }

    HINT_LEVELS_PENALTY = {1: 0.0, 2: 0.1, 3: 0.2, 4: 0.25, 5: 0.3}

    async def get_hint(self, problem_id: str, attempt: CodeAttempt, level: int) -> HintResponse:
        """
        힌트 제공 전 학생 시도 분석:
        - 어디에서 막혔는지 파악
        - 기존 코드의 올바른 부분 인정
        - 틀린 부분에 대한 유도 질문 우선
        """
        analysis = await self._analyze_attempt(problem_id, attempt)
        hint = await self._generate_contextual_hint(analysis, level)
        return HintResponse(
            hint=hint,
            penalty=self.HINT_LEVELS_PENALTY[level],
            remaining_hints=5 - level,
        )
```

### 4.3 코드 리뷰 AI

```python
# code_reviewer.py
class AICodeReviewer:
    """제출 코드 자동 리뷰"""

    REVIEW_ASPECTS = [
        "correctness",       # 정확성 (테스트 케이스 통과)
        "efficiency",        # 시간/공간 복잡도
        "readability",       # 가독성 (변수명, 구조)
        "best_practices",    # 언어별 베스트 프랙티스
        "edge_cases",        # 엣지 케이스 처리
    ]

    async def review(self, submission: CodeSubmission) -> CodeReview:
        # 1. 테스트 실행
        test_result = await self._run_tests(submission)

        # 2. 정적 분석
        static = await self._static_analysis(submission.code, submission.language)

        # 3. LLM 리뷰
        llm_review = await self._llm_review(submission, test_result, static)

        # 4. 개선 제안 (점진적)
        suggestions = await self._generate_suggestions(
            submission, llm_review,
            max_suggestions=3,  # 한 번에 너무 많은 피드백 X
        )

        return CodeReview(
            test_result=test_result,
            score=self._calculate_score(test_result, static, llm_review),
            aspects=llm_review.aspects,
            suggestions=suggestions,
            time_complexity=llm_review.time_complexity,
            space_complexity=llm_review.space_complexity,
        )
```

### 4.4 프로젝트 기반 학습

```typescript
// project_based_learning.ts
interface LearningProject {
  id: string;
  title: string;
  description: string;
  difficulty: 1 | 2 | 3 | 4 | 5;
  estimated_hours: number;
  tech_stack: string[];
  milestones: Milestone[];
  skills_practiced: string[];
  starter_code_repo?: string;       // GitHub 템플릿
}

interface Milestone {
  order: number;
  title: string;
  description: string;
  acceptance_criteria: string[];
  hints: string[];
  estimated_hours: number;
  auto_check: boolean;              // 자동 검증 가능 여부
  check_command?: string;           // "npm test", "pytest" 등
}
```

---

## 5. 교육 컨텐츠 생성

### 5.1 퀴즈 자동 생성

```python
# quiz_generator.py
class QuizGenerator:
    """학습 내용 기반 퀴즈 자동 생성"""

    QUESTION_TYPES = {
        "multiple_choice": {
            "options_count": 4,
            "distractor_strategy": "plausible_wrong",  # 그럴듯한 오답 생성
        },
        "true_false": {},
        "short_answer": {
            "max_words": 50,
        },
        "fill_blank": {
            "blank_count": 1,
        },
        "code_completion": {
            "language": "python",
        },
        "matching": {
            "pair_count": 5,
        },
        "ordering": {
            "items_count": 5,
        },
    }

    async def generate(
        self, content: str, config: QuizConfig
    ) -> Quiz:
        """
        content: 학습 내용 (마크다운)
        config: 문제 수, 유형 비율, 난이도
        """
        questions = []
        for q_type, count in config.type_distribution.items():
            batch = await self._generate_questions(
                content=content,
                question_type=q_type,
                count=count,
                difficulty=config.difficulty,
            )
            questions.extend(batch)

        # 블룸 분류법 기반 검증: 기억/이해/적용/분석/평가/창조
        validated = self._validate_bloom_coverage(questions, config.bloom_targets)
        return Quiz(questions=validated, metadata=QuizMetadata(...))
```

### 5.2 교육 자료 포맷

```typescript
// educational_content.ts
interface EducationalContent {
  id: string;
  title: string;
  topic: string;
  difficulty: number;
  format: ContentFormat;
  content: string;                   // 마크다운
  media: MediaAttachment[];
  learning_objectives: string[];
  prerequisites: string[];
  estimated_read_time_min: number;
  flashcards_generated: number;
  quiz_generated: boolean;
}

type ContentFormat =
  | "lesson"           // 강의 노트
  | "tutorial"         // 단계별 튜토리얼
  | "reference"        // 참조 문서
  | "cheatsheet"       // 치트시트
  | "comparison"       // 비교표
  | "case_study"       // 사례 연구
  | "exercise_set";    // 연습문제 세트
```

---

## 6. 학습 분석 대시보드

### 6.1 데이터 모델

```typescript
// learning_analytics.ts
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
    accuracy_rate: number;
    average_time_per_exercise_sec: number;
    difficulty_distribution: Record<number, number>; // {1: 20, 2: 35, ...}
  };

  // SM-2 통계
  spaced_repetition: {
    total_cards: number;
    cards_due: number;
    retention_rate: number;
    average_easiness_factor: number;
    cards_by_stage: Record<string, number>;  // {"new": 10, "learning": 25, "mature": 100}
  };

  // 약점 분석
  weaknesses: WeaknessAnalysis[];

  // 추천
  recommendations: Recommendation[];
}

interface WeaknessAnalysis {
  topic: string;
  skill: string;
  accuracy_rate: number;
  attempts: number;
  common_errors: string[];
  suggested_resources: string[];
}

interface Recommendation {
  type: "review" | "practice" | "advance" | "break";
  priority: "high" | "medium" | "low";
  title: string;
  description: string;
  action_url?: string;
}
```

### 6.2 추천 시스템

```python
# recommendation_engine.py
class LearningRecommendationEngine:
    """학습 분석 기반 개인화 추천"""

    async def generate_recommendations(self, analytics: LearningAnalytics) -> list[Recommendation]:
        recommendations = []

        # 1. 약점 기반 추천
        for weakness in analytics.weaknesses:
            if weakness.accuracy_rate < 0.5:
                recommendations.append(Recommendation(
                    type="review",
                    priority="high",
                    title=f"{weakness.topic} 복습 필요",
                    description=f"정답률 {weakness.accuracy_rate:.0%}로 기초 복습이 필요합니다.",
                ))

        # 2. 간격 반복 카드 복습 독려
        if analytics.spaced_repetition.cards_due > 20:
            recommendations.append(Recommendation(
                type="review",
                priority="high",
                title=f"밀린 플래시카드 {analytics.spaced_repetition.cards_due}장",
            ))

        # 3. 학습 연속성 유지
        if analytics.progress.current_streak_days >= 7:
            recommendations.append(Recommendation(
                type="advance",
                priority="medium",
                title="훌륭한 학습 연속성! 다음 단계로",
            ))

        # 4. 번아웃 방지
        if self._detect_burnout_risk(analytics):
            recommendations.append(Recommendation(
                type="break",
                priority="high",
                title="휴식 권장",
                description="최근 학습량이 많고 성과가 하락 중입니다. 하루 쉬어가는 것을 추천합니다.",
            ))

        return sorted(recommendations, key=lambda r: {"high": 0, "medium": 1, "low": 2}[r.priority])
```

### 6.3 시각화 차트 목록

| 차트 | 데이터 | 목적 |
|------|------|------|
| 학습 히트맵 | 일별 학습 시간 | GitHub contributions 스타일 연간 활동 |
| 스킬 레이더 | 주제별 수준 | 강점/약점 한눈에 파악 |
| 진도 바 차트 | 경로별 완료율 | 전체 학습 진행 상황 |
| 정답률 트렌드 | 주별 정답률 | 성장 추이 확인 |
| 난이도 분포 | 시도한 문제 난이도 | 학습 수준 변화 |
| SM-2 분포 | 카드 상태별 수 | 복습 상태 파악 |
| 시간 분배 | 주제별 학습 시간 | 학습 균형 확인 |

---

## 7. 교차참조

| 참조 모듈 | 연관 항목 | 참조 방향 |
|----------|---------|----------|
| T2-CORE_AI (2-2) | LLM 소크라틱 응답, 콘텐츠 생성 | ← 사용 |
| T3-PKM (3-3) | SM-2 알고리즘 공유, 지식 그래프 | ↔ 공유 |
| T3-Multimodal (3-2) | 교육 미디어 (이미지/오디오/비디오) | ← 사용 |
| T3-Health (3-6) | 학습 스트레스 모니터링, 번아웃 감지 | ← 사용 |
| T4-Frontend (4-1) | 학습 UI, 대시보드, 플래시카드 UI | → 제공 |

---

*끝 — EDUCATION_LEARNING 상세명세 v1.0.0*
