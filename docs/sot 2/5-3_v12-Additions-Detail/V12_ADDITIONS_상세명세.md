# 5-3. v12 Additions 상세명세

> **Tier**: 5 - Quality / Cross-cutting
> **Part2 상태**: PARTIAL (1-line descriptions across sections)
> **SOT 근거**: Part2 전반 v12 추가 항목 취합
> **Part2 위치**: 6.1, 6.7, 6.8, 6.10, V2-Phase 3, V3-Phase 2, V3-Phase 3

---

## 개요

Part2 각 섹션에 v12에서 추가된 항목들이 1줄 설명으로 산재해 있음. 이 문서는 모든 v12 추가 항목을 취합하여 구현에 필요한 상세 명세를 제공.

---

## 섹션 A: 6.1 UI/UX v12 추가 (4건)

### A-1. BreathingGuide / GroundingExercise / MeditationTimer

> 웰니스 도메인 UI 컴포넌트 3종

#### BreathingGuide

```typescript
interface BreathingGuideProps {
  pattern: BreathingPattern;       // "4-7-8" | "box" | "coherent" | "custom"
  duration_minutes: number;        // 1~30, 기본 5
  visual_mode: "circle" | "wave" | "particle";
  audio_enabled: boolean;          // 가이드 음성 + 배경음
  haptic_enabled: boolean;         // 모바일 진동 피드백
  onComplete: (stats: BreathingStats) => void;
  onEarlyExit: (elapsed_seconds: number) => void;
}

interface BreathingPattern {
  name: string;
  inhale_seconds: number;          // 들숨 (예: 4)
  hold_seconds: number;            // 멈춤 (예: 7)
  exhale_seconds: number;          // 날숨 (예: 8)
  cycles: number;                  // 반복 횟수
}

interface BreathingStats {
  total_cycles: number;
  total_duration_seconds: number;
  avg_cycle_duration: number;
  completion_rate: float;          // 0~1
}
```

**상태 머신**: `Idle → Inhale → Hold → Exhale → (반복) → Complete`

#### GroundingExercise

```typescript
interface GroundingExerciseProps {
  technique: "5-4-3-2-1" | "body_scan" | "progressive_relaxation";
  language: "ko" | "en";
  pace: "slow" | "normal" | "fast";
  onStepComplete: (step: number, response?: string) => void;
  onComplete: (log: ExerciseLog) => void;
}
// 5-4-3-2-1: 시각 5개, 촉각 4개, 청각 3개, 후각 2개, 미각 1개 식별
// 각 단계에서 사용자 입력 수집 → 마인드풀니스 기록
```

#### MeditationTimer

```typescript
interface MeditationTimerProps {
  duration_minutes: number;        // 1~60
  bell_interval_minutes?: number;  // 중간 종 간격
  ambient_sound?: "rain" | "ocean" | "forest" | "silence";
  guided: boolean;                 // 가이드 명상 여부
  guided_script_id?: string;       // 가이드 스크립트 선택
  onComplete: (session: MeditationSession) => void;
}

// API 연동: POST /api/wellness/meditation/log
// { duration, type, mood_before, mood_after, notes }
```

### A-2. ThoughtRecord / CognitiveDistortionDetector

> CBT(인지행동치료) 기반 도구

```typescript
interface ThoughtRecordProps {
  // ABC 모델 기반
  situation: string;               // A: Activating event
  automatic_thought: string;       // B: Belief (자동적 사고)
  emotion: EmotionEntry;           // C: Consequence (감정)
  cognitive_distortions?: string[];// 감지된 인지 왜곡
  alternative_thought?: string;    // 대안적 사고
  outcome_emotion?: EmotionEntry;  // 대안 사고 후 감정
}

interface CognitiveDistortionDetectorConfig {
  distortion_types: string[];      // 15가지 인지 왜곡 유형
  // "all_or_nothing", "overgeneralization", "mental_filter",
  // "disqualifying_positive", "mind_reading", "fortune_telling",
  // "catastrophizing", "minimization", "emotional_reasoning",
  // "should_statements", "labeling", "personalization",
  // "blaming", "fallacy_of_fairness", "fallacy_of_change"
  sensitivity: "low" | "medium" | "high";
  language: "ko" | "en";
  explain_distortion: boolean;     // 왜곡 설명 제공 여부
}

// API: POST /api/wellness/cbt/analyze
// Input: { text: string }
// Output: { distortions: [{type, evidence, confidence, explanation}] }
```

### A-3. WorkloadMonitor / ForcedBreakOverlay

```typescript
interface WorkloadMonitorConfig {
  tracking_metrics: string[];      // ["screen_time", "typing_speed", "break_frequency"]
  alert_thresholds: {
    continuous_work_minutes: number;  // 기본 90분
    daily_screen_hours: number;       // 기본 8시간
    typing_speed_drop_percent: number;// 타이핑 속도 20% 하락 시
  };
  data_retention_days: number;     // 기본 30일
}

interface ForcedBreakOverlayProps {
  trigger: "time_limit" | "fatigue_detected" | "manual";
  break_duration_minutes: number;  // 기본 5분
  dismissable: boolean;            // false면 강제 (설정으로 제어)
  activity_suggestion: string;     // "스트레칭", "눈 운동", "심호흡"
  onBreakComplete: () => void;
  onDismiss?: () => void;
}

// 상태: Monitoring → Alert → BreakOverlay → Monitoring
// 개인정보: 로컬 저장만, 서버 전송 안 함
```

### A-4. FlashcardEditor / SM2ReviewEngine / ReviewDashboard

```typescript
interface FlashcardEditorProps {
  mode: "create" | "edit" | "bulk_import";
  card: {
    front: string;                 // Markdown 지원
    back: string;                  // Markdown 지원
    tags: string[];
    deck_id: string;
    media?: { type: "image" | "audio", url: string }[];
    hints?: string[];
  };
  ai_assist: boolean;              // AI 자동 생성 보조
  onSave: (card: Flashcard) => void;
}

interface SM2ReviewEngine {
  // SuperMemo 2 알고리즘 구현
  calculate_next_review(
    quality: number,               // 0~5 (0=완전 망각, 5=완벽 기억)
    repetition: number,            // 현재 반복 횟수
    ease_factor: number,           // 현재 용이도 (기본 2.5)
    interval_days: number          // 현재 간격
  ): SM2Result;
}

interface SM2Result {
  next_interval_days: number;      // 다음 복습까지 일수
  new_ease_factor: number;         // 갱신된 용이도 (최소 1.3)
  new_repetition: number;          // 갱신된 반복 횟수
}

// SM2 공식:
// quality >= 3: interval = previous * ease_factor
// quality < 3: interval = 1 (리셋)
// ease_factor = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))

interface ReviewDashboardProps {
  stats: {
    cards_due_today: number;
    cards_reviewed_today: number;
    streak_days: number;
    retention_rate: number;        // 최근 30일 기억 유지율
    total_cards: number;
    mature_cards: number;          // interval >= 21일
  };
  heatmap_data: { date: string, count: number }[];  // GitHub 스타일 히트맵
  deck_progress: { deck_id: string, name: string, progress: number }[];
}
```

---

## 섹션 B: 6.7 Agent Teams v12 추가 (2건)

### B-1. Prompt Registry API with Versioning/A-B Test

> 4-4 MLOps 프롬프트 관리의 Agent Teams 전용 인터페이스

```python
class PromptRegistryAPI:
    # CRUD
    def register_prompt(self, prompt: PromptVersion) -> str: ...
    def get_prompt(self, name: str, version: str = "latest") -> PromptVersion: ...
    def list_prompts(self, tag: str = None) -> list[PromptSummary]: ...
    def deprecate_prompt(self, name: str, version: str) -> None: ...

    # 버전 관리
    def diff(self, name: str, v1: str, v2: str) -> PromptDiff: ...
    def rollback(self, name: str, target_version: str) -> None: ...
    def get_history(self, name: str) -> list[VersionEntry]: ...

    # A/B 테스트
    def create_ab_test(self, config: ABTestConfig) -> str: ...
    def get_ab_results(self, test_id: str) -> ABTestResult: ...
    def promote_winner(self, test_id: str) -> None: ...

    # Agent 전용
    def resolve_for_agent(self, agent_type: str, task_type: str) -> PromptVersion:
        """에이전트 유형과 태스크에 맞는 프롬프트 자동 선택"""
        ...
```

### B-2. 3 TemplateSets

#### TS_CORE (핵심 시스템 프롬프트 세트)

```yaml
TS_CORE:
  id: "ts_core_v2.0"
  templates:
    system_prompt:
      role: "VAMOS AI 어시스턴트 기본 역할 정의"
      variables: [user_name, language, context_window, safety_level]
      token_budget: 800
    conversation_guide:
      role: "대화 스타일 및 톤 가이드"
      variables: [formality, domain, user_expertise]
      token_budget: 400
    memory_injection:
      role: "관련 메모리 주입 포맷"
      variables: [memories, relevance_threshold]
      token_budget: 600
    safety_guard:
      role: "안전 가드레일 규칙"
      variables: [safety_level, blocked_topics]
      token_budget: 500
```

#### TS_WEB_RESEARCH (웹 리서치 에이전트 세트)

```yaml
TS_WEB_RESEARCH:
  id: "ts_web_research_v1.0"
  templates:
    planner:
      role: "검색 전략 수립"
      variables: [query, search_depth, language, time_range]
      token_budget: 600
    search_refiner:
      role: "검색 결과 정제 및 관련성 판단"
      variables: [results, original_query, relevance_threshold]
      token_budget: 800
    synthesizer:
      role: "다중 출처 정보 종합"
      variables: [sources, query, output_format, citation_style]
      token_budget: 1000
    fact_checker:
      role: "사실 검증 및 출처 확인"
      variables: [claims, sources]
      token_budget: 600
```

#### TS_CODE (코드 에이전트 세트)

```yaml
TS_CODE:
  id: "ts_code_v1.0"
  templates:
    code_planner:
      role: "코드 작성/수정 계획 수립"
      variables: [task, language, codebase_context, constraints]
      token_budget: 800
    code_generator:
      role: "코드 생성"
      variables: [plan, language, style_guide, existing_code]
      token_budget: 1500
    code_reviewer:
      role: "코드 리뷰 및 피드백"
      variables: [code, language, review_criteria]
      token_budget: 800
    test_generator:
      role: "테스트 코드 생성"
      variables: [code, language, test_framework, coverage_target]
      token_budget: 1000
```

---

## 섹션 C: 6.8 AI Investing v12 추가 (2건)

### C-1. Black-Litterman 모델

#### 수학적 공식

```
사전 기대수익률 (균형 수익률):
Π = δ Σ w_mkt

여기서:
  δ = 위험 회피 계수 (시장 Sharpe ratio 기반, 통상 2.5~3.5)
  Σ = 자산 수익률 공분산 행렬 (N x N)
  w_mkt = 시장 자본화 가중 벡터

투자자 견해 (Views):
P μ = Q + ε,  ε ~ N(0, Ω)

여기서:
  P = 견해 선택 행렬 (K x N, K=견해 수)
  Q = 견해 수익률 벡터 (K x 1)
  Ω = 견해 불확실성 행렬 (K x K, 대각)

사후 기대수익률 (Black-Litterman):
μ_BL = [(τΣ)⁻¹ + P'Ω⁻¹P]⁻¹ [(τΣ)⁻¹Π + P'Ω⁻¹Q]

여기서:
  τ = 스케일링 팩터 (통상 0.025~0.05)

최적 포트폴리오 가중치:
w_BL = (δΣ)⁻¹ μ_BL
```

#### 입출력 스키마

```python
class BlackLittermanInput:
    assets: list[str]                  # 자산 목록 ["AAPL", "MSFT", ...]
    market_caps: dict[str, float]      # 시가총액 {asset: cap}
    covariance_matrix: list[list[float]]  # N x N 공분산
    risk_free_rate: float              # 무위험 이자율
    views: list[InvestorView]          # 투자자 견해
    tau: float = 0.025                 # 스케일링 팩터
    risk_aversion: float = 2.5         # 위험 회피 계수

class InvestorView:
    assets: list[str]                  # 관련 자산
    weights: list[float]               # P 행렬의 해당 행
    expected_return: float             # Q 벡터 값
    confidence: float                  # 0~1 → Ω 역산

class BlackLittermanOutput:
    expected_returns: dict[str, float] # 사후 기대수익률
    optimal_weights: dict[str, float]  # 최적 비중
    risk_contribution: dict[str, float]# 자산별 리스크 기여도
    portfolio_return: float            # 포트폴리오 기대수익
    portfolio_risk: float              # 포트폴리오 변동성
    sharpe_ratio: float                # 샤프 비율
```

#### VAMOS 통합

- AI Investing 모듈에서 사용자 "견해"를 자연어로 입력 → NLP로 InvestorView 변환
- 시장 데이터: 외부 API (Yahoo Finance, KRX) → 자동 공분산 계산
- 면책 조항: 모든 결과에 "투자 조언이 아닙니다" 명시 (법적 필수)

### C-2. Factor Investing

#### 팩터 정의

| 팩터 | 정의 | 계산 | 데이터 소스 |
|------|------|------|-----------|
| **Value** | 저평가 주식 | PBR, PER, EV/EBITDA | 재무제표 |
| **Momentum** | 최근 상승세 | 12M 수익률 - 1M 수익률 | 가격 데이터 |
| **Quality** | 우량 기업 | ROE, 부채비율, 이익 안정성 | 재무제표 |
| **Size** | 소형주 효과 | 시가총액 역수 | 시장 데이터 |
| **Low Volatility** | 저변동성 | 12M 일간 수익률 표준편차 | 가격 데이터 |
| **Dividend** | 고배당 | 배당수익률, 배당 성장률 | 재무제표 |

#### 팩터 스키마

```python
class FactorScore:
    asset: str
    factor_name: str
    raw_value: float
    z_score: float                     # 표준화 점수
    percentile: float                  # 백분위 (0~100)
    as_of_date: date

class FactorPortfolio:
    name: str                          # "Multi-Factor Korea"
    factors: list[FactorWeight]        # [{factor, weight}]
    rebalance_frequency: str           # "monthly" | "quarterly"
    universe: str                      # "KOSPI200" | "S&P500"
    constraints: PortfolioConstraints
    holdings: list[Holding]            # 현재 보유 종목

class PortfolioConstraints:
    max_single_weight: float = 0.10    # 단일 종목 최대 10%
    max_sector_weight: float = 0.30    # 단일 섹터 최대 30%
    min_holdings: int = 20             # 최소 20종목
    turnover_limit: float = 0.30       # 월간 회전율 30% 이하
```

#### 백테스팅

- **기간**: 최소 5년, 권장 10년
- **리밸런싱**: 월말 또는 분기말
- **비용**: 거래 수수료 0.1%, 슬리피지 0.05% 반영
- **벤치마크**: KOSPI200 (한국), S&P500 (미국)
- **메트릭**: CAGR, Sharpe, Max Drawdown, Calmar Ratio, 승률

---

## 섹션 D: 6.10 Cloud Library v12 추가 (10건)

### D-1. Evolution Control Policy (진화 제어 정책)

- 노트/문서의 변경 이력 추적 + 자동 버전 태깅
- 병합 충돌 해결: LWW(Last Writer Wins) 또는 CRDT 기반
- 정책: `{ auto_version: bool, max_versions: int, retention_days: int, diff_threshold: float }`

### D-2. Korean Stopwords (한국어 불용어)

- 한국어 검색 품질 향상을 위한 커스텀 불용어 사전
- 기본 500개 + 도메인별 확장 (의학, 법률, IT)
- 형태소 분석기(Kiwi/Mecab) 연동, 동적 추가/제거 API
- 스키마: `{ word: str, category: str, added_by: str, added_at: datetime }`

### D-3. Code Snippets (코드 스니펫 라이브러리)

- 재사용 코드 저장/검색/공유
- 메타데이터: 언어, 태그, 설명, 사용 횟수, 평점
- 문법 하이라이팅 + 1-click 복사 + IDE 익스텐션 연동
- AI 자동 태깅 + 유사 스니펫 추천

### D-4. Idea Capture (아이디어 캡처)

- 빠른 아이디어 메모 (음성/텍스트/이미지)
- 자동 분류: 카테고리, 긴급도, 관련 프로젝트
- 성숙도 추적: Seed → Sprout → Bloom → Harvest
- 주간 리뷰 알림: 미처리 아이디어 리마인더

### D-5. SWOT Analysis (SWOT 분석 도구)

- 구조화된 SWOT 입력 UI (4분면 매트릭스)
- AI 보조: 입력된 내용 기반 추가 항목 제안
- 전략 매트릭스 자동 생성 (SO/ST/WO/WT)
- 히스토리 추적: 시간에 따른 SWOT 변화 비교

### D-6. Writing Support (글쓰기 지원)

- 글감 브레인스토밍, 아웃라인 생성, 초안 작성 보조
- 문체 분석: 가독성 점수, 문장 길이 분포, 어휘 다양성
- 한국어 특화: 맞춤법 검사(LanguageTool-ko), 경어/반말 일관성
- 장르별 템플릿: 블로그, 보고서, 에세이, 이메일

### D-7. Zettelkasten (제텔카스텐 메모 시스템)

- 원자적 노트 원칙: 하나의 노트에 하나의 아이디어
- 양방향 링크: `[[노트ID]]` 구문으로 연결
- 지식 그래프 시각화: 노트 간 관계 네트워크 뷰
- Fleeting → Literature → Permanent 노트 워크플로우
- 고유 ID: Luhmann 스타일 (`1a2b3`) 또는 timestamp 기반

### D-8. Knowledge Maturity (지식 성숙도)

- 노트/지식 항목의 성숙도 레벨 추적
- 레벨: `Draft(0)` → `Reviewed(1)` → `Validated(2)` → `Mature(3)` → `Canonical(4)`
- 자동 승격 조건: 인용 횟수, 수정 안정성, 외부 검증
- 대시보드: 성숙도 분포, 도메인별 성숙도 히트맵

### D-9. Task Checkpoint (태스크 체크포인트)

- 장기 태스크의 중간 저장/복원 기능
- 체크포인트 데이터: 진행률, 중간 결과, 컨텍스트 스냅샷
- 자동 체크포인트: 5분 간격 또는 주요 단계 완료 시
- 복원: 체크포인트 목록에서 선택하여 해당 상태로 복귀

### D-10. Zettelkasten Extension (제텔카스텐 확장)

- D-7의 확장 기능
- AI 링크 제안: 새 노트 작성 시 관련 기존 노트 자동 추천
- 클러스터 분석: 주제별 노트 군집 자동 생성
- 갭 분석: 연결이 부족한 영역 식별 → 탐구 주제 제안
- 내보내기: Obsidian/Logseq 호환 형식

---

## 섹션 E: V2-Phase 3 v12 HIGH/MEDIUM (~15건)

| # | 항목명 | 우선순위 | 도메인 | 상세 |
|---|--------|---------|--------|------|
| 1 | Enhanced Context Window Manager | HIGH | Core | 동적 컨텍스트 윈도우 관리, 중요도 기반 정보 선별 |
| 2 | Multi-turn Reasoning Tracker | HIGH | Core | 다턴 추론 체인 추적, 일관성 검증 |
| 3 | Adaptive Prompt Optimizer | HIGH | Agent | 응답 품질 기반 프롬프트 자동 최적화 |
| 4 | Cross-session Memory Bridge | HIGH | Memory | 세션 간 메모리 연결 및 참조 |
| 5 | Hybrid RAG Pipeline v2 | HIGH | Search | ColBERT + Self-RAG 통합 파이프라인 |
| 6 | Agent Collaboration Protocol | MEDIUM | Agent | 에이전트 간 작업 위임/결과 공유 프로토콜 |
| 7 | Real-time Fact Checker | MEDIUM | Core | 응답 생성 중 실시간 사실 검증 |
| 8 | Korean NLP Enhancement Pack | MEDIUM | Korean | 한국어 형태소 분석/NER/감성 분석 강화 |
| 9 | Workflow Template Marketplace | MEDIUM | Workflow | 커뮤니티 워크플로우 공유/설치 |
| 10 | Advanced Data Visualization | MEDIUM | UI | 대화형 차트/그래프 생성 강화 |
| 11 | Privacy-preserving Analytics | MEDIUM | Security | 차분 프라이버시 기반 사용 통계 |
| 12 | Multi-modal Output Generator | MEDIUM | Core | 텍스트+이미지+코드 복합 출력 |
| 13 | Smart Notification System | MEDIUM | UI | 컨텍스트 기반 알림 우선순위화 |
| 14 | API Rate Limiter v2 | MEDIUM | Infra | 사용자별/모델별 동적 레이트 리밋 |
| 15 | Telemetry Dashboard | MEDIUM | Infra | 실시간 시스템 메트릭 대시보드 |

---

## 섹션 F: V3-Phase 2 v12 MEDIUM (6건)

| # | 항목명 | 도메인 | 상세 |
|---|--------|--------|------|
| 1 | Federated Learning Adapter | MLOps | 연합 학습 기반 모델 개선 (로컬 데이터 활용, 프라이버시 보존) |
| 2 | Knowledge Graph Auto-builder | Knowledge | 대화/문서에서 자동 지식 그래프 구축 (엔티티 추출, 관계 추론) |
| 3 | Multi-agent Debate Protocol | Agent | 복수 에이전트 토론 기반 답변 품질 향상 (합의 알고리즘) |
| 4 | Contextual Code Completion | Code | 프로젝트 컨텍스트 인식 코드 자동완성 (LSP 통합) |
| 5 | Emotional Intelligence Module v2 | Wellness | 감정 인식 고도화 (음성 톤 분석, 미세 표현 감지) |
| 6 | Cross-lingual Transfer | Korean | 영한 양방향 지식 전이 (번역 없는 직접 전이 학습) |

---

## 섹션 G: V3-Phase 3 v12 LOW (6건)

| # | 항목명 | 도메인 | 상세 |
|---|--------|--------|------|
| 1 | Neuromorphic Attention Simulator | Core | 뉴로모픽 어텐션 메커니즘 실험 (효율성 연구) |
| 2 | Quantum-inspired Optimization | Search | 양자 영감 최적화 알고리즘 적용 (조합 검색 문제) |
| 3 | Self-evolving Agent Architecture | Agent | 자기 진화 에이전트 (태스크 수행 경험 기반 자동 개선) |
| 4 | Holographic Memory Model | Memory | 홀로그래픽 연상 기억 모델 (분산 표현 기반 검색) |
| 5 | Ambient Intelligence Interface | UI | 주변 환경 인식 UI (시간/장소/활동 기반 적응) |
| 6 | Autonomous Research Agent | Agent | 자율 연구 에이전트 (논문 검색→분석→요약→보고서 전자동) |
