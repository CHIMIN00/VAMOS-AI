# Quiz / Test Generation — 퀴즈·테스트 자동 생성 엔진

| 항목 | 값 |
|------|-----|
| **파일** | `04_content-generation/quiz_test_generation.md` |
| **o_ids** | O-008-1, O-008-2, O-008-3 |
| **V단계** | V1 (로컬 MVP) |
| **Level** | L3 |
| **LOCK 참조** | LOCK-ED-05, LOCK-ED-03, LOCK-ED-02 |
| **SOT 출처** | STEP7-O O-008 (퀴즈/테스트 자동 생성) |
| **상태** | COMPLETE |

---

## 1. 개요

퀴즈·테스트 자동 생성 엔진은 학습 콘텐츠(마크다운, 텍스트, 코드)를 입력받아 Bloom 택소노미 6단계(LOCK-ED-05)에 맞춘 다양한 유형의 문제를 자동 생성한다. 평가 기준(LOCK-ED-03)에 따라 진단 테스트, 진행 평가, 최종 평가를 구분하며, IRT 난이도(LOCK-ED-02)와 연동하여 학습자 수준에 적응적으로 문제를 배분한다.

> LOCK (LOCK-ED-05, STEP7-O O-001): Bloom 택소노미 6단계 — Remember / Understand / Apply / Analyze / Evaluate / Create (순서 불변)

> LOCK (LOCK-ED-03, 기존 명세 §2): 평가 기준 — 진단테스트 + 진행평가 + 최종평가, 3등급 (미달 / 달성 / 우수)

> LOCK (LOCK-ED-02, 기존 명세 §2): IRT 5단계 — Very Easy / Easy / Medium / Hard / Very Hard, 목표 정답률 70-85%

**교수법 모델**: Bloom 택소노미 기반 문제 분류 + IRT 적응형 난이도 + 오답 분석 기반 개념 복습 유도

---

## 2. 입력 스키마 (E1)

```typescript
interface QuizGenerationRequest {
    learner_id: string;                         // 학습자 ID
    content_source: ContentSource;              // 학습 콘텐츠 소스
    assessment_type: AssessmentType;            // 평가 유형 (LOCK-ED-03)
    config: QuizConfig;                         // 생성 설정
}

interface ContentSource {
    type: "markdown" | "text" | "code" | "url" | "flashcard_deck";
    content: string;                            // 원본 텍스트 또는 URL
    topic: string;                              // 주제
    subtopic?: string;                          // 세부 주제
    language?: string;                          // 코드 언어 (type="code" 시)
}

// LOCK-ED-03: 평가 유형
type AssessmentType = "diagnostic" | "progress" | "final";

interface QuizConfig {
    question_count: number;                     // 문제 수 (기본 10)
    bloom_distribution?: BloomDistribution;     // Bloom 레벨별 비율 (미지정 시 자동)
    question_types: QuestionType[];             // 허용 문제 유형
    difficulty_range?: {                        // IRT θ 범위 (미지정 시 학습자 θ 기반 자동)
        min_theta: number;
        max_theta: number;
    };
    time_limit_min?: number;                    // 제한 시간 (분)
    shuffle_options: boolean;                   // 보기 셔플 여부 (기본 true)
}

// LOCK-ED-05: Bloom 6단계 비율 배분
interface BloomDistribution {
    remember: number;       // 1단계 — 기억 (비율 0.0~1.0)
    understand: number;     // 2단계 — 이해
    apply: number;          // 3단계 — 적용
    analyze: number;        // 4단계 — 분석
    evaluate: number;       // 5단계 — 평가
    create: number;         // 6단계 — 창조
}

type QuestionType =
    | "multiple_choice"     // 4지선다 객관식
    | "true_false"          // O/X
    | "short_answer"        // 주관식 서술형
    | "fill_blank"          // 빈칸 채우기
    | "code_completion"     // 코드 완성
    | "scenario"            // 시나리오 문제
    | "matching"            // 연결하기
    | "ordering";           // 순서 배열
```

---

## 3. 출력 스키마 (E2)

```typescript
interface QuizResult {
    quiz_id: string;
    learner_id: string;
    assessment_type: AssessmentType;            // LOCK-ED-03
    questions: GeneratedQuestion[];
    metadata: QuizMetadata;
}

interface GeneratedQuestion {
    question_id: string;
    bloom_level: BloomLevel;                    // LOCK-ED-05: 1~6
    question_type: QuestionType;
    difficulty_theta: number;                   // IRT θ (LOCK-ED-02)
    content: QuestionContent;
    answer: AnswerSpec;
    explanation: string;                        // 해설
    related_concepts: string[];                 // 관련 개념 (오답 시 복습 유도)
    estimated_time_sec: number;                 // 예상 풀이 시간
}

// LOCK-ED-05: Bloom 레벨
type BloomLevel = 1 | 2 | 3 | 4 | 5 | 6;

interface QuestionContent {
    stem: string;                               // 문제 본문 (마크다운)
    code_block?: string;                        // 코드 블록 (코드 문제)
    options?: OptionItem[];                     // 객관식 보기
    pairs?: MatchPair[];                        // 연결하기 쌍
    ordering_items?: string[];                  // 순서 배열 항목
    scenario_context?: string;                  // 시나리오 배경
}

interface OptionItem {
    label: string;                              // "A", "B", "C", "D"
    text: string;                               // 보기 텍스트
    is_correct: boolean;
    distractor_rationale?: string;              // 오답 근거 (내부용)
}

interface AnswerSpec {
    correct_answer: string | string[];          // 정답 (단일/복수)
    scoring_rubric?: string;                    // 서술형 채점 기준
    code_test_cases?: TestCase[];               // 코드 문제 테스트 케이스
    acceptable_variations?: string[];           // 허용 변형 답안
}

interface QuizMetadata {
    generated_at: string;                       // ISO 8601
    content_source_hash: string;                // 원본 콘텐츠 해시
    bloom_coverage: Record<BloomLevel, number>; // 실제 Bloom 분포
    avg_difficulty_theta: number;               // 평균 난이도 θ
    total_estimated_time_min: number;           // 총 예상 시간
}
```

---

## 4. 퀴즈 생성 파이프라인 (E3)

### 4.1 전체 파이프라인

```
콘텐츠 입력 → 개념 추출 → Bloom 레벨 분류 → 문제 유형 선택
    → LLM 문제 생성 → 난이도 태깅(IRT) → 품질 검증 → 출력
```

### 4.2 핵심 알고리즘

```python
class QuizGenerationPipeline:
    """퀴즈 자동 생성 파이프라인"""

    # LOCK-ED-05: Bloom 6단계 (순서 불변)
    BLOOM_LEVELS = {
        1: "Remember",     # 기억: 사실, 용어, 정의 회상
        2: "Understand",   # 이해: 개념 설명, 비교, 요약
        3: "Apply",        # 적용: 절차 수행, 규칙 적용
        4: "Analyze",      # 분석: 구성요소 분해, 관계 파악
        5: "Evaluate",     # 평가: 판단, 비평, 정당화
        6: "Create",       # 창조: 설계, 합성, 새로운 산출물
    }

    # Bloom 레벨 → 적합 문제 유형 매핑
    BLOOM_QUESTION_TYPE_MAP = {
        1: ["multiple_choice", "true_false", "fill_blank", "matching"],
        2: ["multiple_choice", "short_answer", "matching", "ordering"],
        3: ["code_completion", "fill_blank", "scenario", "short_answer"],
        4: ["scenario", "short_answer", "code_completion", "ordering"],
        5: ["scenario", "short_answer"],
        6: ["scenario", "short_answer", "code_completion"],
    }

    # LOCK-ED-03: 평가 유형별 기본 Bloom 분포
    ASSESSMENT_BLOOM_DEFAULTS = {
        "diagnostic": {1: 0.30, 2: 0.30, 3: 0.20, 4: 0.10, 5: 0.05, 6: 0.05},
        "progress":   {1: 0.10, 2: 0.20, 3: 0.30, 4: 0.20, 5: 0.10, 6: 0.10},
        "final":      {1: 0.05, 2: 0.10, 3: 0.20, 4: 0.25, 5: 0.20, 6: 0.20},
    }

    async def generate_quiz(self, request: QuizGenerationRequest) -> QuizResult:
        """메인 퀴즈 생성 엔트리포인트"""

        # 1. 콘텐츠에서 핵심 개념 추출
        concepts = await self._extract_concepts(request.content_source)

        # 2. 개념별 Bloom 레벨 분류
        bloom_tagged = self._classify_bloom_levels(concepts)

        # 3. Bloom 분포 결정 (사용자 지정 or 평가 유형별 기본값)
        bloom_dist = request.config.bloom_distribution or \
                     self.ASSESSMENT_BLOOM_DEFAULTS[request.assessment_type]

        # 4. 문제 수 배분: Bloom 레벨별 × 문제 유형
        allocation = self._allocate_questions(
            total=request.config.question_count,
            bloom_dist=bloom_dist,
            allowed_types=request.config.question_types,
        )

        # 5. 학습자 θ 조회 (IRT 연동)
        learner_theta = await self._get_learner_theta(request.learner_id)

        # 6. 문제별 생성
        questions = []
        for bloom_level, q_type, count in allocation:
            batch = await self._generate_questions_batch(
                concepts=bloom_tagged[bloom_level],
                bloom_level=bloom_level,
                question_type=q_type,
                count=count,
                target_theta=self._compute_target_theta(
                    learner_theta, bloom_level, request.assessment_type
                ),
            )
            questions.extend(batch)

        # 7. 품질 검증 (중복/모호성/정답 검증)
        validated = await self._validate_questions(questions)

        # 8. 결과 조립
        return QuizResult(
            quiz_id=generate_uuid(),
            learner_id=request.learner_id,
            assessment_type=request.assessment_type,
            questions=validated,
            metadata=self._build_metadata(validated, request),
        )

    async def _extract_concepts(self, source: ContentSource) -> list[Concept]:
        """LLM으로 콘텐츠에서 핵심 개념 추출"""
        prompt = f"""
        다음 학습 콘텐츠에서 핵심 개념을 추출하세요.
        각 개념에 대해:
        - 개념명
        - 정의 (1~2문장)
        - 관련 키워드
        - 선수 개념 (있다면)
        를 JSON 배열로 반환하세요.

        콘텐츠:
        {source.content}
        """
        return await llm_call(prompt, response_format=list[Concept])

    def _classify_bloom_levels(
        self, concepts: list[Concept]
    ) -> dict[BloomLevel, list[Concept]]:
        """개념을 Bloom 6단계로 분류 (LOCK-ED-05)"""
        classified = {level: [] for level in range(1, 7)}
        for concept in concepts:
            # 각 개념은 여러 Bloom 레벨에서 문제 생성 가능
            # 기본: 모든 개념은 Remember(1)~Apply(3) 가능
            # Analyze(4)~Create(6)는 개념 복잡도에 따라 결정
            for level in range(1, 4):
                classified[level].append(concept)
            if concept.complexity >= 0.5:
                classified[4].append(concept)
            if concept.complexity >= 0.7:
                classified[5].append(concept)
            if concept.complexity >= 0.85:
                classified[6].append(concept)
        return classified

    def _allocate_questions(
        self,
        total: int,
        bloom_dist: dict[int, float],
        allowed_types: list[QuestionType],
    ) -> list[tuple[BloomLevel, QuestionType, int]]:
        """Bloom 분포 + 허용 유형에 따른 문제 수 배분"""
        allocation = []
        for bloom_level in range(1, 7):
            count = round(total * bloom_dist.get(bloom_level, 0))
            if count == 0:
                continue
            # 해당 Bloom에 적합한 유형 중 허용된 것만
            eligible = [
                t for t in self.BLOOM_QUESTION_TYPE_MAP[bloom_level]
                if t in allowed_types
            ]
            if not eligible:
                eligible = [allowed_types[0]]
            # 균등 배분 (count를 eligible 유형 전체에 분배, 나머지는 앞에서부터 +1)
            base, remainder = divmod(count, len(eligible))
            for idx, qt in enumerate(eligible):
                qty = base + (1 if idx < remainder else 0)
                if qty == 0:
                    continue
                allocation.append((bloom_level, qt, qty))
        return allocation

    def _compute_target_theta(
        self,
        learner_theta: float,
        bloom_level: BloomLevel,
        assessment_type: AssessmentType,
    ) -> float:
        """평가 유형 + Bloom 레벨에 따른 목표 θ 계산"""
        # 진단: 넓은 범위 (θ ± 1.0)
        # 진행: 학습자 수준 근처 (θ ± 0.5)
        # 최종: 살짝 상향 (θ + 0.3)
        type_offset = {"diagnostic": 0.0, "progress": 0.0, "final": 0.3}
        # 상위 Bloom은 θ 상향 보정
        bloom_offset = (bloom_level - 3) * 0.15
        return learner_theta + type_offset[assessment_type] + bloom_offset

    async def _generate_questions_batch(
        self,
        concepts: list[Concept],
        bloom_level: BloomLevel,
        question_type: QuestionType,
        count: int,
        target_theta: float,
    ) -> list[GeneratedQuestion]:
        """LLM으로 문제 배치 생성"""
        bloom_name = self.BLOOM_LEVELS[bloom_level]
        prompt = f"""
        Bloom 택소노미 레벨: {bloom_name} ({bloom_level}/6)
        문제 유형: {question_type}
        목표 난이도 θ: {target_theta:.2f}
        생성 수: {count}

        다음 개념들을 기반으로 문제를 생성하세요:
        {[c.name for c in concepts[:5]]}

        각 문제에:
        - 문제 본문 (stem)
        - 정답 + 해설
        - 관련 개념 (오답 시 복습 포인트)
        - Bloom 레벨에 적합한 인지 요구 수준
        """
        return await llm_call(prompt, response_format=list[GeneratedQuestion])

    async def _validate_questions(
        self, questions: list[GeneratedQuestion]
    ) -> list[GeneratedQuestion]:
        """품질 검증: 중복, 모호성, 정답 정확도"""
        validated = []
        seen_stems = set()
        for q in questions:
            stem_hash = hash(q.content.stem.strip().lower())
            if stem_hash in seen_stems:
                continue  # 중복 제거
            seen_stems.add(stem_hash)

            # 객관식: 정답이 보기에 포함되는지 확인
            if q.question_type == "multiple_choice":
                correct_count = sum(1 for o in q.content.options if o.is_correct)
                if correct_count != 1:
                    continue  # 정답 1개가 아니면 제외

            # 코드 문제: 테스트 케이스 존재 확인
            if q.question_type == "code_completion":
                if not q.answer.code_test_cases:
                    continue

            validated.append(q)
        return validated
```

### 4.3 Bloom 레벨별 문제 생성 전략

| Bloom 레벨 | 인지 요구 | 문제 생성 전략 | 예시 |
|------------|----------|--------------|------|
| 1 Remember | 사실·정의 회상 | 용어 정의, 사실 확인, 목록 나열 | "Python에서 리스트를 생성하는 키워드는?" |
| 2 Understand | 의미 파악·요약 | 개념 비교, 예시 식별, 요약 | "Stack과 Queue의 차이를 설명하시오" |
| 3 Apply | 절차 수행 | 코드 작성, 공식 적용, 절차 실행 | "이진 탐색을 구현하시오" |
| 4 Analyze | 구조 분해 | 코드 디버깅, 원인 분석, 패턴 식별 | "이 코드의 버그를 찾고 원인을 분석하시오" |
| 5 Evaluate | 판단·비평 | 최적 솔루션 선택, 트레이드오프 평가 | "두 알고리즘 중 어떤 것이 이 상황에 적합한가?" |
| 6 Create | 설계·합성 | 시스템 설계, 새 알고리즘 고안 | "실시간 채팅 시스템을 설계하시오" |

---

## 5. 평가 연동 — LOCK-ED-03 (E4)

### 5.1 평가 유형별 설정

> LOCK (LOCK-ED-03, 기존 명세 §2): 진단테스트 + 진행평가 + 최종평가, 3등급 (미달 / 달성 / 우수)

| 평가 유형 | 목적 | 문제 수 | Bloom 비중 | 시간 | 등급 기준 |
|----------|------|---------|-----------|------|----------|
| **진단 (diagnostic)** | 학습 시작 전 수준 파악 | 15~20 | Remember·Understand 60% | 20분 | 미달 <50% / 달성 / 우수 ≥85% |
| **진행 (progress)** | 학습 중간 이해도 확인 | 8~12 | Apply·Analyze 50% | 15분 | 미달 <60% / 달성 / 우수 ≥85% |
| **최종 (final)** | 학습 완료 종합 평가 | 20~30 | Analyze~Create 65% | 40분 | 미달 <70% / 달성 / 우수 ≥90% |

### 5.2 오답 분석 + 복습 유도

```python
class AnswerAnalyzer:
    """오답 분석 및 복습 유도"""

    async def analyze_submission(
        self, quiz_result: QuizResult, answers: list[SubmittedAnswer]
    ) -> AnalysisReport:
        """제출 답안 분석"""
        report = AnalysisReport()

        for q, ans in zip(quiz_result.questions, answers):
            is_correct = self._check_answer(q, ans)
            report.add_result(q.question_id, is_correct)

            if not is_correct:
                # 오답 원인 분류
                error_type = await self._classify_error(q, ans)
                # 관련 개념 복습 유도
                report.add_review_suggestion(
                    concept=q.related_concepts,
                    bloom_level=q.bloom_level,
                    error_type=error_type,
                    # SM-2 플래시카드 연동 (02_spaced-repetition)
                    flashcard_action="create_or_reschedule",
                )

        # 등급 판정 (LOCK-ED-03)
        report.grade = self._determine_grade(
            score_pct=report.score_percentage,
            assessment_type=quiz_result.assessment_type,
        )
        return report

    def _determine_grade(
        self, score_pct: float, assessment_type: AssessmentType
    ) -> str:
        """LOCK-ED-03 3등급 판정"""
        thresholds = {
            "diagnostic": {"fail": 50, "excellent": 85},
            "progress":   {"fail": 60, "excellent": 85},
            "final":      {"fail": 70, "excellent": 90},
        }
        t = thresholds[assessment_type]
        if score_pct < t["fail"]:
            return "미달"
        elif score_pct >= t["excellent"]:
            return "우수"
        else:
            return "달성"

    async def _classify_error(
        self, question: GeneratedQuestion, answer: SubmittedAnswer
    ) -> ErrorType:
        """오답 원인 분류"""
        # 1. 개념 미숙: 기본 정의/사실 오류
        # 2. 적용 오류: 개념은 아나 적용 실패
        # 3. 분석 미흡: 구조 분해 불완전
        # 4. 부주의: 시간 부족 / 실수
        prompt = f"""
        문제 Bloom 레벨: {question.bloom_level}
        문제: {question.content.stem}
        정답: {question.answer.correct_answer}
        학습자 답: {answer.response}
        
        오답 원인을 분류하세요: concept_gap | application_error | analysis_gap | carelessness
        """
        return await llm_call(prompt, response_format=ErrorType)
```

---

## 6. Bloom 레벨 태깅 엔진 — O-008-2 (E3)

```python
class BloomTagger:
    """학습 콘텐츠 및 문제의 Bloom 레벨 자동 태깅"""

    # LOCK-ED-05: 6단계 순서 불변
    BLOOM_TAXONOMY = [
        (1, "Remember",    ["정의", "나열", "식별", "회상", "명명"]),
        (2, "Understand",  ["설명", "비교", "분류", "요약", "해석"]),
        (3, "Apply",       ["실행", "구현", "사용", "해결", "시연"]),
        (4, "Analyze",     ["구별", "조직", "귀인", "분해", "관계"]),
        (5, "Evaluate",    ["판단", "비평", "정당화", "검증", "추천"]),
        (6, "Create",      ["설계", "구성", "생성", "계획", "발명"]),
    ]

    async def tag_content(self, content: str) -> list[BloomTaggedSegment]:
        """콘텐츠를 Bloom 레벨별로 태깅"""
        segments = self._split_into_segments(content)
        tagged = []
        for seg in segments:
            level = await self._classify_segment(seg)
            tagged.append(BloomTaggedSegment(
                text=seg,
                bloom_level=level,
                action_verbs=self._extract_action_verbs(seg, level),
            ))
        return tagged

    async def tag_question(self, question: GeneratedQuestion) -> BloomLevel:
        """생성된 문제의 Bloom 레벨 검증·재태깅"""
        prompt = f"""
        다음 문제의 Bloom 택소노미 레벨을 판정하세요.
        문제: {question.content.stem}
        유형: {question.question_type}
        
        Bloom 6단계:
        1-Remember: 사실 회상
        2-Understand: 의미 파악
        3-Apply: 절차 수행
        4-Analyze: 구조 분해
        5-Evaluate: 판단/비평
        6-Create: 설계/합성
        
        레벨 번호만 반환: 1~6
        """
        return await llm_call(prompt, response_format=int)

    def validate_bloom_coverage(
        self, questions: list[GeneratedQuestion], target_dist: BloomDistribution
    ) -> BloomCoverageReport:
        """Bloom 분포 목표 대비 실제 분포 검증"""
        actual = {level: 0 for level in range(1, 7)}
        for q in questions:
            actual[q.bloom_level] += 1
        total = len(questions)
        actual_pct = {k: v / total for k, v in actual.items()}
        deviations = {
            k: abs(actual_pct[k] - getattr(target_dist, self.BLOOM_TAXONOMY[k-1][1].lower(), 0))
            for k in range(1, 7)
        }
        return BloomCoverageReport(
            target=target_dist,
            actual=actual_pct,
            deviations=deviations,
            is_acceptable=all(d < 0.15 for d in deviations.values()),
        )
```

---

## 7. 테스트 결과 분석 — O-008-3 (E3)

```python
class TestResultAnalyzer:
    """테스트 결과 종합 분석"""

    async def analyze(
        self, quiz: QuizResult, submissions: list[SubmittedAnswer]
    ) -> TestAnalysisReport:
        """종합 분석 리포트 생성"""

        # 1. 기본 통계
        stats = self._compute_basic_stats(quiz, submissions)

        # 2. Bloom 레벨별 성취도
        bloom_performance = self._analyze_by_bloom(quiz, submissions)

        # 3. 문제 유형별 성취도
        type_performance = self._analyze_by_type(quiz, submissions)

        # 4. 약점 개념 식별
        weak_concepts = self._identify_weak_concepts(quiz, submissions)

        # 5. 학습 권장 사항 생성
        recommendations = await self._generate_recommendations(
            bloom_performance, weak_concepts
        )

        # 6. IRT θ 갱신 제안 (→ 01_adaptive-learning/difficulty_adjustment 연동)
        theta_update = self._suggest_theta_update(stats, bloom_performance)

        return TestAnalysisReport(
            stats=stats,
            bloom_performance=bloom_performance,
            type_performance=type_performance,
            weak_concepts=weak_concepts,
            recommendations=recommendations,
            theta_update=theta_update,
            grade=stats.grade,  # LOCK-ED-03 등급
        )

    def _analyze_by_bloom(
        self, quiz: QuizResult, submissions: list[SubmittedAnswer]
    ) -> dict[BloomLevel, BloomPerformance]:
        """Bloom 레벨별 정답률·소요시간 분석"""
        by_bloom = {}
        for q, sub in zip(quiz.questions, submissions):
            bl = q.bloom_level
            if bl not in by_bloom:
                by_bloom[bl] = BloomPerformance(level=bl)
            by_bloom[bl].add(
                correct=sub.is_correct,
                time_sec=sub.time_spent_sec,
            )
        return by_bloom

    def _identify_weak_concepts(
        self, quiz: QuizResult, submissions: list[SubmittedAnswer]
    ) -> list[WeakConcept]:
        """오답 빈도 높은 개념 식별 — SM-2 플래시카드 재스케줄 트리거"""
        concept_errors = {}
        for q, sub in zip(quiz.questions, submissions):
            if not sub.is_correct:
                for concept in q.related_concepts:
                    concept_errors.setdefault(concept, 0)
                    concept_errors[concept] += 1
        return [
            WeakConcept(name=c, error_count=n)
            for c, n in sorted(concept_errors.items(), key=lambda x: -x[1])
            if n >= 2  # 2회 이상 오답 개념만
        ]
```

---

## 8. 에러 핸들링 (E5)

| 에러 코드 | 상황 | 복구 전략 |
|----------|------|----------|
| `QUIZ_E01` | 콘텐츠에서 개념 추출 실패 | 원본 텍스트 기반 단순 문제 생성 (fallback) |
| `QUIZ_E02` | LLM 응답 파싱 실패 | 최대 3회 재시도 + 구조화된 프롬프트 변경 |
| `QUIZ_E03` | Bloom 분포 목표 미달 | 부족 레벨 추가 생성 시도, 불가 시 가용 레벨로 재배분 |
| `QUIZ_E04` | 객관식 정답 없음/복수 | 해당 문제 제외 + 대체 생성 |
| `QUIZ_E05` | 코드 테스트 케이스 실행 실패 | 테스트 케이스 재생성, 불가 시 문제 유형 변경 |
| `QUIZ_E06` | 시간 초과 (생성 >30s) | 배치 크기 축소 + 병렬 처리 |
| `QUIZ_E07` | 학습자 θ 조회 실패 | 기본 θ=0.0 (중간 난이도) 사용 |

---

## 9. 프라이버시 · 보안 (E6)

| 규칙 | 내용 |
|------|------|
| 답안 데이터 | 학습자 답안은 분석 후 90일 보관, 이후 익명화 집계만 유지 |
| 콘텐츠 권한 | 사용자 제공 콘텐츠의 퀴즈 생성 결과는 해당 사용자에게만 노출 |
| LLM 호출 | 학습자 식별 정보(이름, ID)를 LLM 프롬프트에 포함하지 않음 |
| 서술형 답안 | 서술형 답안은 암호화 저장 (AES-256) |
| 오답 분석 | 오답 패턴 집계 시 개인 식별 불가 형태로 변환 |

---

## 10. 성능 SLA (E7)

| 지표 | 목표 | 비고 |
|------|------|------|
| 퀴즈 생성 (10문제) | ≤ 8s | LLM 병렬 호출 (Bloom 레벨별 배치) |
| 퀴즈 생성 (30문제) | ≤ 20s | 배치 크기 5 × 6 병렬 |
| 답안 채점 (객관식) | ≤ 100ms | 로컬 연산 |
| 답안 채점 (서술형) | ≤ 3s | LLM 기반 채점 |
| 코드 문제 실행 | ≤ 5s | 샌드박스 타임아웃 포함 |
| 오답 분석 리포트 | ≤ 5s | 통계 연산 + LLM 권장 사항 |
| 가용성 | 99.5% | 로컬 MVP — 네트워크 의존 시 LLM 호출만 |

---

## 11. 통합 테스트 시나리오 (E8)

| # | 시나리오 | 입력 | 기대 결과 |
|---|---------|------|----------|
| T1 | 진단 테스트 생성 | Python 기초 콘텐츠, diagnostic, 15문제 | Bloom 1~2 비중 60%, θ 범위 -1.5~1.5 |
| T2 | 진행 평가 생성 | React Hooks 학습 후, progress, 10문제 | Bloom 3~4 비중 50%, 학습자 θ 근처 |
| T3 | 최종 평가 생성 | 알고리즘 전체, final, 25문제 | Bloom 4~6 비중 65%, θ 상향 0.3 |
| T4 | 오답→SM-2 연동 | T2 완료 + 오답 3건 | 오답 개념 플래시카드 생성/재스케줄 트리거 |
| T5 | Bloom 분포 검증 | 임의 콘텐츠, 커스텀 분포 | 실제 분포와 목표 분포 편차 <15% |
| T6 | 코드 문제 생성+채점 | JavaScript 코드, code_completion | 테스트 케이스 통과 여부 자동 채점 |
| T7 | 등급 판정 | 최종평가 65점 | "미달" (LOCK-ED-03: <70%) |

---

## 12. 의존성 (E9)

| 의존 대상 | 방향 | 용도 |
|----------|------|------|
| `01_adaptive-learning/difficulty_adjustment` | → 사용 | IRT θ 조회 + θ 갱신 제안 (LOCK-ED-02) |
| `01_adaptive-learning/learner_profile` | → 사용 | 학습자 프로필 (Bloom 진행 상태) |
| `01_adaptive-learning/adaptive_engine` | → 사용 | Bloom 분류 로직 재사용 (LOCK-ED-05) |
| `02_spaced-repetition/flashcard_auto_generation` | → 트리거 | 오답 개념 → 플래시카드 자동 생성 |
| `02_spaced-repetition/review_scheduler` | → 트리거 | 오답 개념 → 복습 재스케줄 (SM-2) |
| `05_learning-analytics/learning_dashboard` | ← 제공 | 퀴즈 결과 통계 데이터 제공 (1-5 생성 예정) |
| `05_learning-analytics/gamification` | ← 제공 | 퀴즈 완료 XP 데이터 제공 (1-5 생성 예정) |
| T2-CORE_AI | → 사용 | LLM 호출 (문제 생성, 채점, 오답 분석) |

---

## 13. UX · 게이미피케이션 (E10)

| 요소 | 내용 |
|------|------|
| 퀴즈 완료 XP | 진단 +10 XP, 진행 +20 XP, 최종 +50 XP |
| 만점 보너스 | 우수 등급 시 +30% 보너스 XP |
| 연속 정답 | Streak 3 이상 시 콤보 표시 + 추가 XP |
| 오답 복습 | 오답 개념 하이라이트 + "복습하기" 버튼 → SM-2 플래시카드 |
| 진행 표시 | 문제 풀이 중 Bloom 레벨 아이콘 + 진행률 바 |
| 결과 화면 | Bloom 레이더 차트 (6축) + 등급 뱃지 + 오답 개념 목록 |
| 재도전 | 오답 문제만 재도전 모드 제공 |
