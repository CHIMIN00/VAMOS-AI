# 1-1. Verifier / Reasoning Engines 상세명세

> **Tier**: 1 - Core Intelligence (ORANGE CORE 내부)
> **Part2 상태**: SHELL (이름 + 1줄 설명만 존재)
> **SOT 근거**: D2.0-01 S5.10~5.11, D2.0-02 S7
> **Part2 위치**: V1-Phase 3 (L2140~2147)

---

## 개요

ORANGE CORE 내부의 검증/추론 엔진 모듈군. Part2에는 모듈 이름과 1줄 설명만 존재하며, 입출력 스키마, 알고리즘, 상태 머신, fallback 규칙 등 구현에 필요한 상세내용이 전무함.

---

## C-1: Logic Verifier (논리 검증기)

### 현재 Part2 내용 (L2140)
```
C-1 Logic Verifier: 논리적 일관성 검증
```

### 필요한 상세내용

#### 1. 입출력 스키마
- **Input**: `LogicVerifyRequest`
  - `claim: str` -- 검증 대상 주장
  - `context: list[str]` -- 근거 문장 목록
  - `reasoning_chain: list[ReasoningStep]` -- 추론 체인 (선택)
  - `verification_depth: Literal["shallow", "standard", "deep"]`
- **Output**: `LogicVerifyResult`
  - `is_valid: bool`
  - `confidence: float` (0.0~1.0)
  - `contradictions: list[Contradiction]` -- 발견된 모순 목록
  - `fallacy_types: list[str]` -- 감지된 논리적 오류 유형
  - `evidence_mapping: dict[str, str]` -- 주장→근거 매핑

#### 2. 검증 알고리즘
- **Phase 1: 전제-결론 분해**: 주장을 전제(premise)와 결론(conclusion)으로 분리
- **Phase 2: 내부 일관성 검사**: 전제 간 모순 탐지 (부정, 범위 충돌, 시간 모순)
- **Phase 3: 추론 유효성 검사**: 전제→결론 추론의 타당성 평가
  - 연역적 타당성 (deductive validity)
  - 귀납적 강도 (inductive strength)
  - 유추 적합성 (analogical relevance)
- **Phase 4: 오류 분류**: 비형식적 오류(informal fallacy) 24종 탐지
  - Ad hominem, Straw man, False dilemma, Slippery slope, Circular reasoning 등

#### 3. BaseVerifier ABC 패턴
```python
class BaseVerifier(ABC):
    @abstractmethod
    async def verify(self, request: VerifyRequest) -> VerifyResult: ...

    @abstractmethod
    def get_confidence_threshold(self) -> float: ...

    async def should_escalate(self, result: VerifyResult) -> bool:
        """confidence < threshold 시 D-1 Think Engine으로 에스컬레이션"""
        return result.confidence < self.get_confidence_threshold()
```

#### 4. 판정 기준
- `confidence >= 0.8`: PASS (자동 승인)
- `0.5 <= confidence < 0.8`: REVIEW (I-19 ApprovalManager로 전달)
- `confidence < 0.5`: FAIL (자동 거부 + 근거 첨부)

#### 5. Fallback 규칙
- C-1 실패 시 → D-1 Think Engine으로 재검증 요청
- D-1도 실패 시 → 사용자에게 판단 요청 (HITL)

---

## C-2: Math Verifier (수학 검증기)

### 현재 Part2 내용 (L2142)
```
C-2 Math Verifier: 수학적 정확성 검증
```

### 필요한 상세내용

#### 1. 입출력 스키마
- **Input**: `MathVerifyRequest`
  - `expression: str` -- 수식/계산식
  - `expected_result: Optional[str]` -- 예상 결과값
  - `context: str` -- 수학적 맥락 (통계, 재무, 물리 등)
  - `precision: int` -- 소수점 정밀도 (기본 6)
- **Output**: `MathVerifyResult`
  - `is_correct: bool`
  - `computed_result: str` -- 계산 결과
  - `error_type: Optional[str]` -- 오류 유형 (단위 오류, 차원 불일치, 오버플로우 등)
  - `step_by_step: list[ComputeStep]` -- 단계별 계산 과정
  - `symbolic_verification: Optional[str]` -- SymPy 기호 검증 결과

#### 2. 수학 검증 파이프라인
- **Phase 1: 수식 파싱** -- LaTeX/ASCII math 파싱, AST 생성
- **Phase 2: 기호 연산** -- SymPy 기반 기호적 검증
  - 등식 검증: `sympy.simplify(lhs - rhs) == 0`
  - 부등식 검증: `sympy.solve(inequality)`
  - 극한/미분/적분 검증
- **Phase 3: 수치 연산** -- NumPy/SciPy 기반 수치적 교차검증
  - 기호 연산 결과와 수치 연산 결과 비교
  - 허용 오차: `abs(symbolic - numeric) < 1e-{precision}`
- **Phase 4: 단위/차원 분석** -- Pint 라이브러리 기반 차원 검증

#### 3. 재무 수학 특화 (AI Investing 연동)
- IRR, NPV, Sharpe Ratio, Sortino Ratio 등 재무 함수 내장 검증
- 통계적 유의성 검증 (p-value, confidence interval)
- 몬테카를로 시뮬레이션 결과 검증

#### 4. 정확도 기준
- 정수 연산: 완전 일치 필수
- 실수 연산: 상대 오차 < 1e-6
- 통계 연산: 95% 신뢰구간 내 일치

---

## C-3: Code Verifier (코드 검증기)

### 현재 Part2 내용 (L2144)
```
C-3 Code Verifier: 코드 정확성 검증
```

### 필요한 상세내용

#### 1. 입출력 스키마
- **Input**: `CodeVerifyRequest`
  - `code: str` -- 검증 대상 코드
  - `language: str` -- 프로그래밍 언어
  - `intent: str` -- 코드의 의도/목적 설명
  - `test_cases: Optional[list[TestCase]]` -- 테스트 케이스
  - `security_scan: bool` -- 보안 스캔 포함 여부 (기본 True)
- **Output**: `CodeVerifyResult`
  - `is_correct: bool` -- 기능적 정확성
  - `is_secure: bool` -- 보안 취약점 없음
  - `syntax_errors: list[SyntaxError]`
  - `logic_errors: list[LogicError]`
  - `security_issues: list[SecurityIssue]` -- OWASP Top 10 + CWE 매핑
  - `test_results: list[TestResult]`
  - `complexity_metrics: ComplexityMetrics` -- 순환 복잡도, 인지 복잡도

#### 2. 코드 검증 파이프라인
- **Phase 1: 정적 분석**
  - 문법 검사: 언어별 파서
  - 타입 검사: mypy(Python), tsc(TypeScript), rustc(Rust)
  - 스타일 검사: ruff(Python), eslint(TypeScript)
- **Phase 2: 보안 취약점 스캔**
  - Bandit (Python) / Semgrep (범용)
  - OWASP Top 10 매핑 (SQL injection, XSS, Command injection 등)
  - CWE ID 매핑
  - 비밀키/토큰 노출 감지
- **Phase 3: Sandbox 실행** (E-4 Code Executor 연동)
  - Docker sandbox 내 격리 실행 (LOCK)
  - 리소스 제한: CPU 1 core, RAM 512MB, timeout 30s
  - 테스트 케이스 실행 및 결과 비교
- **Phase 4: 의도-코드 일치 검증**
  - LLM 기반 코드 리뷰: 의도와 구현의 일치도 평가
  - 엣지 케이스 자동 생성 및 검증

#### 3. 보안 체크 규칙 (Part2 6.5 LOCK 연동)
- Command injection: `subprocess.run()` + 사용자 입력 조합 감지
- SQL injection: f-string/format + SQL 쿼리 조합 감지
- XSS: 이스케이프 없는 HTML 렌더링 감지
- Path traversal: `../` 패턴 + 파일 접근 조합 감지

---

## D-1: Think Engine (추론 엔진)

### 현재 Part2 내용 (L2146)
```
D-1 Think Engine: 심층 추론 엔진
```

### 필요한 상세내용

#### 1. 입출력 스키마
- **Input**: `ThinkRequest`
  - `problem: str` -- 추론 대상 문제
  - `context: list[ContextItem]` -- 참조 컨텍스트
  - `strategy: Literal["cot", "tot", "got", "auto"]` -- 추론 전략
  - `max_depth: int` -- 최대 추론 깊이 (기본 5)
  - `budget_tokens: int` -- 추론에 할당할 최대 토큰 수
- **Output**: `ThinkResult`
  - `answer: str` -- 최종 답변
  - `reasoning_trace: list[ReasoningStep]` -- 추론 과정
  - `strategy_used: str` -- 실제 사용된 전략
  - `confidence: float`
  - `tokens_used: int` -- 실제 사용 토큰
  - `alternative_paths: list[str]` -- 탐색했으나 선택하지 않은 경로

#### 2. 추론 알고리즘

##### CoT (Chain-of-Thought)
- 선형 단계별 추론
- 각 단계에서 중간 결론 생성
- 적합: 순차적 문제, 계산, 논리 추론

##### ToT (Tree-of-Thought)
- 분기 탐색: 각 단계에서 k개 후보 생성 (기본 k=3)
- 평가 함수: 각 후보의 유망도 점수 계산
- 가지치기: 유망도 하위 50% 제거
- BFS/DFS 선택: 문제 유형에 따라 자동 선택
- 적합: 창의적 문제, 다중 해법 존재

##### GoT (Graph-of-Thought)
- 비선형 추론: 추론 노드 간 자유 연결
- 병합/분할: 여러 추론 경로 합성
- 적합: 복잡한 의사결정, 다면적 분석

##### Auto 전략 선택
```
문제 유형 분류 → 전략 선택:
  분류 = "sequential" → CoT
  분류 = "creative" or "multi-solution" → ToT
  분류 = "complex" or "multi-factor" → GoT
  분류 = "unknown" → CoT (fallback)
```

#### 3. 추론 깊이 조절
- **Level 1** (shallow): 1~2 단계, < 500 토큰
- **Level 2** (standard): 3~5 단계, < 2000 토큰
- **Level 3** (deep): 5~10 단계, < 5000 토큰
- 비용 관리: `budget_tokens` 초과 시 현재까지의 최선 결과 반환

#### 4. 상태 머신
```
IDLE → ANALYZING → REASONING → EVALUATING → COMPLETE
  ↓                    ↓            ↓
FAILED ←──────── ESCALATING ←── TIMEOUT
```

---

## D-2: Multimodal Engine (멀티모달 추론 엔진)

### 현재 Part2 내용 (L2147)
```
D-2 Multimodal Engine: 멀티모달 처리 엔진
```

### 필요한 상세내용

#### 1. 입출력 스키마
- **Input**: `MultimodalRequest`
  - `modalities: list[ModalityInput]` -- 입력 모달리티 목록
    - `type: Literal["text", "image", "audio", "video", "document"]`
    - `data: bytes | str` -- 원본 데이터 또는 경로
    - `metadata: dict` -- 모달리티별 메타데이터
  - `task: str` -- 작업 유형 (분석/생성/변환)
  - `fusion_strategy: Literal["early", "late", "hybrid"]`
- **Output**: `MultimodalResult`
  - `outputs: list[ModalityOutput]` -- 출력 모달리티 목록
  - `cross_modal_relations: list[Relation]` -- 모달리티 간 관계
  - `confidence_per_modality: dict[str, float]`

#### 2. 멀티모달 융합 파이프라인
```
입력 모달리티들
  ↓
[Phase 1: 모달리티별 전처리]
  text → 토큰화 + 임베딩
  image → CLIP 임베딩 + OCR
  audio → Whisper STT + 감정 분석
  video → 프레임 샘플링 + 장면 분할
  document → 구조 파싱 + 텍스트 추출
  ↓
[Phase 2: 특징 추출]
  각 모달리티에서 feature vector 추출
  ↓
[Phase 3: 융합 (Fusion)]
  Early Fusion: 특징 벡터 연결(concat) → 단일 모델 처리
  Late Fusion: 모달리티별 독립 처리 → 결과 앙상블
  Hybrid Fusion: 관련 모달리티 그룹별 early → 그룹 간 late
  ↓
[Phase 4: 추론/생성]
  D-1 Think Engine 연동 (멀티모달 컨텍스트 전달)
  ↓
[Phase 5: 출력 합성]
  텍스트 + 차트 + 코드 등 복합 출력 구성
```

#### 3. 모달리티별 전처리 상세
| 모달리티 | 전처리 도구 | 출력 포맷 | 최대 크기 |
|---------|-----------|----------|----------|
| text | 토크나이저 | embedding vector | 128K tokens |
| image | CLIP + OCR (Tesseract) | feature vector + text | 20MB |
| audio | Whisper + Deepgram | transcript + emotion | 25MB / 10min |
| video | FFmpeg + frame sampler | keyframes + transcript | 100MB / 5min |
| document | docling / Unstructured | structured text + tables | 50MB |

#### 4. Cross-modal Attention
- 텍스트↔이미지: CLIP 유사도 기반 정렬
- 텍스트↔오디오: 시간축 정렬 (타임스탬프 매핑)
- 이미지↔텍스트(문서): OCR 영역 좌표 매핑

#### 5. I-4 / I-13 연동
- **I-4 Multimodal Interpreter** → D-2로 입력 전달
- D-2 처리 결과 → **I-13 Multimodal Renderer**로 출력 전달

---

## 공통사항

### 의존성
| 모듈 | 의존 대상 | 설명 |
|------|---------|------|
| C-1~C-3 | D-1 Think Engine | 검증 실패 시 에스컬레이션 |
| D-1 | I-5 Decision Engine | 추론 결과 → 의사결정 전달 |
| D-2 | I-4, I-13 | 멀티모달 입력/출력 연동 |
| 전체 | I-8 Self-check Engine | QoD 점수 산출 대상 |

### Part2 반영 필요사항
- V1-Phase 3 (L2140~2147): 현재 1줄 설명 → 위 상세내용으로 보강
- Section 6 cross-reference: 현재 "§6 참조" → 구체적 스키마/알고리즘 인라인

### SOT 참조 문서
- `D2.0-01` Section 5.10 (C-Series), Section 5.11 (D-Series)
- `D2.0-02` Section 7 (ORANGE CORE 상세 모듈)
- `VAMOS_MASTER_SPECIFICATION.md` Section 8 (모듈 카탈로그)
