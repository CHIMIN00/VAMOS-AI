# EXP-Modules-Detail 카탈로그

> **버전**: v1.0
> **작성일**: 2026-03-25
> **목적**: sot 2/6-10_EXP-Modules-Detail/를 V3 EXP 확장 모듈 카탈로그 정본으로 구조화. B-시리즈(학습), EVX(실험), A-시리즈(고급AI), D-시리즈(생성) 전체 모듈의 인덱스 + 모듈별 L3 시트 제공
> **Status**: APPROVED — Phase 7 FINAL PASS (S7-5, 2026-03-25) · Content A (S10-5)
> **Tier**: 6 (System-wide Components)
> **SOT 출처**: D2.0-02 (Orange Core — I-Series/모듈 인덱스), D2.0-01 (§5.6~§5.13 모듈 카탈로그 정본)
> **Part2 상태**: FULL (V3-Phase 2 L3993-4335: EXP 모듈 전체 활성화)
> **세션**: S6-8
> **형식**: 카탈로그 (§1 인덱스 + §2 모듈별 L3 시트) — SOT2_PART2_FULL_INTEGRATION_PLAN.md §7 문제2 참조

---

## §1. EXP 모듈 인덱스

### 1.1 모듈 분류 체계

| 시리즈 | 카테고리 | 모듈 수 | 서브폴더 | 정본 출처 | V-Phase |
|--------|---------|---------|---------|----------|---------|
| **B-시리즈** | Learning (학습) | 5 (B-1~B-6, B-3 제외) | 01_b-series | D2.0-01 §5.10 | V3-P2 |
| **EVX** | Experimental (실험) | 6 (EVX-1~EVX-6) | 02_evx-modules | D2.0-01 §5.13, D2.0-02 §7.4.1 | V3-P2 |
| **A-시리즈** | Advanced AI (고급AI) | 4 (A-3, A-5, A-6, A-7) | 03_a-series | D2.0-01 (산재: §0.5, §0.6, §5.10 등) | V3-P2 |
| **D-시리즈** | Generation (생성) | 4 (D-3~D-6) | 04_d-series | D2.0-01 §5.12 | V3-P2 |
| | **합계** | **19** | | | |

> **참고**: I-시리즈(I-18, I-21, I-24)와 S-시리즈(S-2~S-8), E-시리즈(E-7~E-12), C-시리즈(C-4~C-7)는 각각 기존 도메인(1-2 Auxiliary, 6-6 Self-Evolution, 3-2 Multimodal, 1-1 Verifier)에서 관리. 본 카탈로그는 기존 도메인에 매핑되지 않는 확장 모듈(B/EVX/A/D)만 수록.
>
> **A-시리즈 출처 참고**: A-시리즈 모듈은 D2.0-01 내 단일 카탈로그 섹션에 모여 있지 않고 여러 곳에 산재(§0.5, §0.6, §5.10 B-시리즈 영역 등). 기존 §5.14 참조는 "공통 규칙" 섹션이므로 A-시리즈 정본 출처로 부정확하여 수정함.

### 1.2 전체 모듈 목록 + 상태

| # | 모듈 ID | 모듈명 | 시리즈 | 파일 경로 | L3 상태 | 의존성 | 비고 |
|---|---------|--------|--------|----------|---------|--------|------|
| 1 | B-1 | Skill Library | B | `backend/vamos_core/learning/b01_skill_library.py` | ⬜ L1 | I-5(Decision), I-14(Benchmark) | 학습된 스킬 저장/검색/재사용 |
| 2 | B-2 | Procedural Memory | B | `backend/vamos_core/learning/b02_procedural_memory.py` | ⬜ L1 | B-1, I-3(Memory) | 절차적 기억 (how-to) |
| 3 | B-4 | DSPy Integration | B | `backend/vamos_core/learning/b04_dspy.py` | ⬜ L1 | I-1(Intent), I-5(Decision) | 프롬프트 최적화 (DSPy 프레임워크) |
| 4 | B-5 | Few-Shot Manager | B | `backend/vamos_core/learning/b05_few_shot_manager.py` | ⬜ L1 | B-1, I-2(RAG) | 동적 Few-Shot 예제 관리 |
| 5 | B-6 | Reinforcement Learner | B | `backend/vamos_core/learning/b06_rl_learner.py` | ⬜ L1 | I-8(Cost), S-5(Feedback) | 보상 기반 행동 학습 |
| 6 | EVX-1 | Code-as-Policy | EVX | `backend/vamos_core/experimental/evx01_code_as_policy.py` | ⬜ L1 | I-5(Decision), 07(Policy) | 코드 생성 → 정책 자동 적용 |
| 7 | EVX-2 | Adversarial Verifier | EVX | `backend/vamos_core/experimental/evx02_adversarial.py` | ⬜ L1 | I-6(Self-check) | 적대적 입력 자동 생성 + 견고성 테스트 |
| 8 | EVX-3 | Log-prob Analyzer | EVX | `backend/vamos_core/experimental/evx03_logprob.py` | ⬜ L1 | I-5(Decision), Brain Adapter | LLM 로그 확률 분석 → 불확실성 측정 |
| 9 | EVX-4 | Thought Buffer | EVX | `backend/vamos_core/experimental/evx04_thought_debug.py` | ⬜ L1 | I-6(Self-check), I-9(Trace) | 추론 체인 시각화/디버깅 |
| 10 | EVX-5 | Gen-Verify-Learn | EVX | `backend/vamos_core/experimental/evx05_synthetic_data.py` | ⬜ L1 | I-2(RAG), Brain Adapter | 합성 학습 데이터 생성 |
| 11 | EVX-6 | Z3 Solver Routing | EVX | `backend/vamos_core/experimental/evx06_multi_obj.py` | ⬜ L1 | I-8(Cost), I-6(Self-check) | 다목적 최적화 (품질/비용/속도) |
| 12 | A-3 | Meta AI | A | `backend/vamos_core/modules/a03_meta_ai.py` | ⬜ L1 | I-18(Self-evo), S-4(Monitor) | 메타 AI: 다른 AI 모듈 분석/최적화 |
| 13 | A-5 | Lazy Generation | A | `backend/vamos_core/modules/a05_lazy_generation.py` | ⬜ L1 | I-8(Cost), Brain Adapter | 지연 생성: 필요 시점까지 LLM 호출 지연 |
| 14 | A-6 | Federated | A | `backend/vamos_core/modules/a06_federated.py` | ⬜ L0 | A-7(Remote), 07(Approval) | 연합 모듈 네트워크 (DEFER-AT-004) |
| 15 | A-7 | Remote Executor | A | `backend/vamos_core/modules/a07_remote_executor.py` | ⬜ L1 | 07(Policy, Cost) | 원격 컴퓨트 리소스 태스크 실행 |
| 16 | D-3 | Long Horizon Planner | D | `backend/vamos_core/generation/d03_long_horizon.py` | ⬜ L1 | I-5(Decision), I-3(Memory) | 장기 계획 수립 (다단계 목표) |
| 17 | D-4 | Personality Engine | D | `backend/vamos_core/generation/d04_personality.py` | ⬜ L1 | I-1(Intent), I-10(UI) | AI 페르소나 관리 |
| 18 | D-5 | Parallel Generator | D | `backend/vamos_core/generation/d05_parallel_gen.py` | ⬜ L1 | Brain Adapter, I-8(Cost) | 병렬 콘텐츠 생성 |
| 19 | D-6 | GraphRAG | D | `backend/vamos_core/generation/d06_graphrag.py` | ⬜ L1 | I-24(KG), I-2(RAG) | 지식 그래프 기반 RAG (V3-004 벤치마크) |

### 1.3 모듈 ID 체계 (LOCK-610-01)

| 규칙 | 설명 | LOCK 참조 |
|------|------|-----------|
| **접두사** | B(학습), EVX(실험), A(고급AI), D(생성) | LOCK-610-01 |
| **번호** | 시리즈 내 순번 (기존 D2.0-01 번호 유지) | LOCK-610-01 |
| **category 필드** | `"EXP"` (Module Catalog 표준 — D2.0-01 §5.5) | LOCK-610-03 |
| **기본 상태** | `enabled = false` (config에서 명시적 활성화 필수) | LOCK-610-04 |
| **네임스페이스** | EVX 모듈: `vamos-experimental` (프로덕션 격리) | LOCK-610-05 |

### 1.4 모듈 간 의존성 그래프 (LOCK-610-02)

```
B-1 (Skill Library) ←─── B-2 (Procedural Memory)
  │                        │
  └──→ B-5 (Few-Shot) ←───┘
         │
         └──→ B-4 (DSPy Integration)
                │
                └──→ B-6 (RL Learner) ──→ S-5 (Feedback Loop)

A-3 (Meta AI) ←── I-18 (Self-evo Engine)
  │
  └──→ A-5 (Lazy Generation)
  └──→ A-7 (Remote Executor) ←── A-6 (Federated)

D-3 (Long Horizon) ──→ D-5 (Parallel Gen)
D-6 (GraphRAG) ←── I-24 (KG Engine)

EVX-1 (Code-as-Policy) ──→ 07 Policy Gate
EVX-2 (Adversarial Verifier) ──→ I-6 (Self-check)
EVX-3 (Log-prob) ──→ Brain Adapter
EVX-4 (Thought Buffer) ──→ I-9 (Trace)
EVX-5 (Gen-Verify-Learn) ──→ I-2 (RAG)
EVX-6 (Z3 Solver Routing) ──→ I-8 (Cost) + I-6 (Self-check)
```

### Part2 상태 및 방식 C 접근법
- **Part2 상태**: FULL
- **방식 C 접근법**: 요약 + 정본 인용

---

## §2. 모듈별 L3 시트

### B-1: Skill Library

| 항목 | 내용 |
|------|------|
| **Input** | `SkillQuery(name: str, domain: Optional[str], tags: list[str])` |
| **Output** | `SkillResult(skill: Skill, confidence: float, usage_count: int)` |
| **알고리즘** | 임베딩 기반 유사도 검색 (Chroma/Qdrant) + 최근 사용 가중치 |
| **의존성** | I-5 Decision (스킬 선택 확인), I-14 Benchmark (스킬 성능 평가) |
| **에러 처리** | `SKILL_NOT_FOUND` → 유사 스킬 추천, `SKILL_DEPRECATED` → 대체 스킬 안내 |
| **테스트 기준** | 스킬 검색 정확도 ≥ 85%, 검색 지연 < 200ms |
| **config** | `modules.exp.b_series.enabled`, `b01.max_cache_size = 1000` |

### B-2: Procedural Memory

| 항목 | 내용 |
|------|------|
| **Input** | `ProcedureQuery(task_type: str, context: dict)` |
| **Output** | `Procedure(steps: list[Step], estimated_time: float, success_rate: float)` |
| **알고리즘** | 과거 성공 세션에서 절차 추출 (SequenceMining) + 일반화 |
| **의존성** | B-1 (스킬 단위 재사용), I-3 Memory (과거 세션 데이터) |
| **에러 처리** | `PROCEDURE_AMBIGUOUS` → 후보 절차 목록 반환, `PROCEDURE_OUTDATED` → 재학습 트리거 |
| **테스트 기준** | 절차 재현 성공률 ≥ 80%, 추출 지연 < 1s |
| **config** | `b02.min_success_sessions = 3`, `b02.generalization_threshold = 0.7` |

### B-4: DSPy Integration

| 항목 | 내용 |
|------|------|
| **Input** | `PromptOptRequest(template: str, examples: list[Example], metric: str)` |
| **Output** | `OptimizedPrompt(template: str, score: float, iterations: int)` |
| **알고리즘** | DSPy BootstrapFewShot + MIPROv2 (자동 프롬프트 최적화) |
| **의존성** | I-1 Intent (프롬프트 컨텍스트), I-5 Decision (최적화 결과 적용 승인) |
| **에러 처리** | `DSPY_NO_IMPROVEMENT` → 원본 유지, `DSPY_BUDGET_EXCEEDED` → 조기 종료 |
| **테스트 기준** | 최적화 후 메트릭 개선 ≥ 5%, 실행 시간 < 5분 |
| **config** | `b04.max_iterations = 50`, `b04.budget_tokens = 100000` |
| **패키지** | `dspy-ai` |

### B-5: Few-Shot Manager

| 항목 | 내용 |
|------|------|
| **Input** | `FewShotRequest(task_type: str, max_examples: int, diversity: float)` |
| **Output** | `FewShotSet(examples: list[Example], diversity_score: float)` |
| **알고리즘** | MMR(Maximal Marginal Relevance) 기반 예제 선택 (관련성 + 다양성 균형) |
| **의존성** | B-1 (스킬 예제 풀), I-2 RAG (벡터 검색) |
| **에러 처리** | `FEWSHOT_INSUFFICIENT` → 가용 예제 수 반환 + 합성 예제 생성 권고 |
| **테스트 기준** | 선택된 예제의 task 정확도 향상 ≥ 10%, 다양성 ≥ 0.6 |
| **config** | `b05.default_max_examples = 5`, `b05.mmr_lambda = 0.7` |

### B-6: Reinforcement Learner

| 항목 | 내용 |
|------|------|
| **Input** | `RLState(observation: dict, action_space: list[str], reward_history: list[float])` |
| **Output** | `RLAction(action: str, q_value: float, exploration_rate: float)` |
| **알고리즘** | DQN(Deep Q-Network) + ε-greedy 탐색 (V3에서 PPO 옵션 추가) |
| **의존성** | I-8 Cost (보상 함수에 비용 반영), S-5 Feedback Loop (사용자 피드백 보상) |
| **에러 처리** | `RL_DIVERGENCE` → 학습률 하향 + 체크포인트 복원, `RL_REWARD_ANOMALY` → 보상 스케일링 |
| **테스트 기준** | 100 에피소드 후 누적 보상 수렴, 학습 안정성 (분산 < 0.1) |
| **config** | `b06.learning_rate = 0.001`, `b06.epsilon_start = 1.0`, `b06.epsilon_end = 0.01` |
| **패키지** | `torch` |

### EVX-1: Code-as-Policy

| 항목 | 내용 |
|------|------|
| **Input** | `PolicySpec(description: str, constraints: list[str], target_system: str)` |
| **Output** | `GeneratedPolicy(code: str, test_results: TestSuite, verified: bool)` |
| **알고리즘** | LLM 코드 생성 → 정적 분석 → 샌드박스 실행 → 07 Policy Gate 검증 |
| **의존성** | I-5 Decision, 07 Policy Gate (생성된 정책의 안전성 검증) |
| **에러 처리** | `POLICY_UNSAFE` → 거부 + 위험 요소 보고, `POLICY_SYNTAX_ERROR` → 재생성 (1회) |
| **테스트 기준** | 생성된 정책 코드 안전성 검사 통과율 ≥ 95%, 실행 시간 < 30s |
| **격리** | `vamos-experimental` 네임스페이스 (프로덕션 격리) |

### EVX-2: Adversarial Verifier

| 항목 | 내용 |
|------|------|
| **Input** | `TestTarget(module_id: str, input_schema: type, num_cases: int)` |
| **Output** | `AdversarialReport(cases: list[TestCase], failures: list[Failure], robustness_score: float)` |
| **알고리즘** | Mutation-based fuzzing + LLM 기반 adversarial 생성 (ART 라이브러리) |
| **의존성** | I-6 Self-check (견고성 점수 반영) |
| **에러 처리** | `ADVERSARIAL_TIMEOUT` → 부분 결과 반환, `TARGET_CRASHED` → 긴급 보고 |
| **테스트 기준** | 발견된 취약점 중 False Positive < 10% |
| **패키지** | `adversarial-robustness-toolbox` |
| **격리** | `vamos-experimental` 네임스페이스 |

### EVX-3: Log-prob Analyzer

| 항목 | 내용 |
|------|------|
| **Input** | `LogprobRequest(response: ConnectorResponse, threshold: float)` |
| **Output** | `UncertaintyReport(entropy: float, low_confidence_spans: list[Span], recommendation: str)` |
| **알고리즘** | 토큰별 log probability 분석 → 엔트로피 계산 → 불확실 구간 추출 |
| **의존성** | Brain Adapter (logprobs 지원 모델 필수), I-5 Decision |
| **에러 처리** | `LOGPROB_UNAVAILABLE` → 모델 미지원 시 스킵 + 경고 |
| **테스트 기준** | 불확실 구간 탐지 정밀도 ≥ 80% |
| **격리** | `vamos-experimental` 네임스페이스 |

### EVX-4: Thought Buffer

| 항목 | 내용 |
|------|------|
| **Input** | `DebugRequest(trace_id: str, depth: int)` |
| **Output** | `ThoughtGraph(nodes: list[ThoughtNode], edges: list[Edge], bottlenecks: list[str])` |
| **알고리즘** | 추론 체인 trace → DAG 구성 → 병목 탐지 (임계 경로 분석) |
| **의존성** | I-6 Self-check, I-9 Trace/Logs |
| **에러 처리** | `TRACE_NOT_FOUND` → trace_id 검색 실패, `TRACE_INCOMPLETE` → 부분 그래프 반환 |
| **테스트 기준** | 추론 체인 정확도 ≥ 90%, 시각화 렌더링 < 2s |
| **격리** | `vamos-experimental` 네임스페이스 |

### EVX-5: Gen-Verify-Learn

| 항목 | 내용 |
|------|------|
| **Input** | `SyntheticRequest(schema: type, num_samples: int, constraints: dict)` |
| **Output** | `SyntheticDataset(samples: list[dict], quality_score: float, diversity_score: float)` |
| **알고리즘** | LLM 기반 생성 + 통계적 검증 (KS test, chi-square) + 제약 조건 필터링 |
| **의존성** | I-2 RAG (실제 데이터 분포 참조), Brain Adapter |
| **에러 처리** | `SYNTHETIC_LOW_QUALITY` → 재생성 + 제약 조건 완화 권고 |
| **테스트 기준** | 합성 데이터-실제 데이터 분포 유사도 ≥ 0.85 (KS test p > 0.05) |
| **격리** | `vamos-experimental` 네임스페이스 |

### EVX-6: Z3 Solver Routing

| 항목 | 내용 |
|------|------|
| **Input** | `OptRequest(objectives: dict[str, float], constraints: list[Constraint])` |
| **Output** | `ParetoFront(solutions: list[Solution], trade_off_analysis: str)` |
| **알고리즘** | Z3 SMT solver로 제약 충족성(feasibility) 사전 검사 → NSGA-II (Non-dominated Sorting Genetic Algorithm) 기반 다목적 최적화 |
| **의존성** | I-8 Cost (비용 목표), I-6 Self-check (품질 목표) |
| **에러 처리** | `OPTIM_NO_FEASIBLE` → 제약 완화 후 재실행, `OPTIM_CONVERGENCE_FAIL` → 세대 수 증가 |
| **테스트 기준** | Pareto 최적 해 ≥ 5개, 수렴 세대 < 200 |
| **패키지** | `torch`, `z3-solver` |
| **격리** | `vamos-experimental` 네임스페이스 |

### A-3: Meta AI

| 항목 | 내용 |
|------|------|
| **Input** | `MetaAnalysisRequest(module_ids: list[str], period_days: int)` |
| **Output** | `MetaReport(rankings: list[ModuleRank], tuning_suggestions: list[Suggestion])` |
| **알고리즘** | 모듈 성능 메트릭 수집 → 통계 분석 → 자동 파라미터 튜닝 권고 |
| **의존성** | I-18 Self-evo Engine (진화 엔진 연동), S-4 Performance Monitor |
| **에러 처리** | `META_INSUFFICIENT_DATA` → 최소 7일 데이터 필요, `META_TUNING_REJECTED` → 07 승인 실패 |
| **테스트 기준** | 파라미터 튜닝 후 전체 QoD 개선 ≥ 3% |

### A-5: Lazy Generation

| 항목 | 내용 |
|------|------|
| **Input** | `LazyRequest(content_type: str, priority: str, deadline: Optional[datetime])` |
| **Output** | `LazyResult(content: str, generated_at: datetime, tokens_saved: int)` |
| **알고리즘** | 필요 시점까지 LLM 호출 지연 → 배치 가능 여부 판단 → 불필요 호출 사전 차단 |
| **의존성** | I-8 Cost (비용 절약 추적), Brain Adapter (배치 큐 연동) |
| **에러 처리** | `LAZY_DEADLINE_MISSED` → 즉시 실행으로 전환, `LAZY_CANCELLED` → 리소스 해제 |
| **테스트 기준** | 불필요 LLM 호출 절감 ≥ 20%, deadline 준수율 ≥ 99% |

### A-6: Federated

| 항목 | 내용 |
|------|------|
| **Input** | `FederatedRequest(task: str, peer_instances: list[PeerInfo])` |
| **Output** | `FederatedResult(aggregated_output: dict, participant_count: int)` |
| **알고리즘** | Federated Learning: 로컬 학습 → 그래디언트만 교환 → 글로벌 모델 집계 (FedAvg) |
| **의존성** | A-7 Remote Executor (원격 피어 통신), 07 Approval (인증 프로토콜) |
| **에러 처리** | `FEDERATED_AUTH_FAIL` → mTLS 인증 실패, `FEDERATED_QUORUM_FAIL` → 최소 피어 미달 |
| **테스트 기준** | 글로벌 모델 정확도 ≥ 로컬 모델 대비 95% |
| **상태**: DEFER-AT-004 (인증/승인 프로토콜 미확정) |

### A-7: Remote Executor

| 항목 | 내용 |
|------|------|
| **Input** | `RemoteTask(command: str, resource_req: ResourceSpec, timeout: int)` |
| **Output** | `RemoteResult(output: str, exit_code: int, execution_time: float)` |
| **알고리즘** | SSH/K8s Job 기반 원격 실행 → 결과 수집 → 실패 시 재시도 (max 3회) |
| **의존성** | 07 Policy/Cost Gate |
| **에러 처리** | `REMOTE_TIMEOUT` → 재시도, `REMOTE_AUTH_FAIL` → 즉시 실행 중단(suspend) + 07 Gate 통보 (자동 키/인증 갱신 금지), `REMOTE_RESOURCE_UNAVAIL` → 대기 큐 |
| **테스트 기준** | 원격 실행 성공률 ≥ 95%, 재시도 포함 평균 지연 < 2× 로컬 |
| **패키지** | `paramiko` (SSH), `kubernetes` (K8s Job) |

### D-3: Long Horizon Planner

| 항목 | 내용 |
|------|------|
| **Input** | `PlanRequest(goal: str, constraints: list[str], max_steps: int)` |
| **Output** | `Plan(steps: list[PlanStep], estimated_cost: float, risk_assessment: str)` |
| **알고리즘** | 계층적 태스크 분해 (HTN) + MCTS(Monte Carlo Tree Search) 기반 최적 경로 탐색 |
| **의존성** | I-5 Decision (계획 승인), I-3 Memory (과거 성공 계획 참조) |
| **에러 처리** | `PLAN_INFEASIBLE` → 제약 완화 제안, `PLAN_DEPTH_EXCEEDED` → 서브골 분할 |
| **테스트 기준** | 10-step 계획 성공률 ≥ 70%, 계획 생성 시간 < 30s |

### D-4: Personality Engine

| 항목 | 내용 |
|------|------|
| **Input** | `PersonalityConfig(traits: dict[str, float], tone: str, language_style: str)` |
| **Output** | `PersonalityState(active_persona: str, adaptation_level: float)` |
| **알고리즘** | Big Five 성격 모델 기반 페르소나 파라미터 → 프롬프트 시스템 메시지 동적 생성 |
| **의존성** | I-1 Intent (사용자 선호 감지), I-10 UI (페르소나 전환 표시) |
| **에러 처리** | `PERSONA_CONFLICT` → 기본 페르소나로 폴백 |
| **테스트 기준** | 페르소나 일관성 ≥ 90% (동일 페르소나 내 스타일 편차 < 10%) |

### D-5: Parallel Generator

| 항목 | 내용 |
|------|------|
| **Input** | `ParallelGenRequest(prompts: list[str], strategy: str)` |
| **Output** | `ParallelGenResult(outputs: list[str], best_idx: int, diversity_score: float)` |
| **알고리즘** | N개 프롬프트 병렬 실행 → Best-of-N 선택 또는 합성 (merge) |
| **의존성** | Brain Adapter (병렬 호출), I-8 Cost (N × 비용 추적) |
| **에러 처리** | `PARALLEL_PARTIAL_FAIL` → 성공분만 반환 + 경고, `PARALLEL_BUDGET_EXCEEDED` → N 축소 |
| **테스트 기준** | Best-of-N 품질 향상 ≥ 15% (vs 단일 생성), 병렬 오버헤드 < 20% |

### D-6: GraphRAG

| 항목 | 내용 |
|------|------|
| **Input** | `GraphRAGQuery(query: str, top_k: int, graph_depth: int)` |
| **Output** | `GraphRAGResult(answer: str, subgraph: nx.DiGraph, evidence_nodes: list[str])` |
| **알고리즘** | I-24 KG 서브그래프 추출 → 벡터 검색 + 그래프 탐색 결합 → LLM 합성 |
| **의존성** | I-24 Knowledge Graph Engine (Neo4j), I-2 RAG (벡터 검색) |
| **에러 처리** | `GRAPHRAG_EMPTY_SUBGRAPH` → 벡터 검색으로 폴백, `GRAPHRAG_NEO4J_ERROR` → I-2 RAG only |
| **테스트 기준** | 벤치마크 정확도 ≥ 90% (V3-004), 검색 지연 < 3s |
| **패키지** | `neo4j`, `networkx` |

---

## §3. 공통 규칙

### 3.0 LOCK 보호 항목 테이블

> **AD2 감사 대응**: 기존 인라인 `(LOCK)` 주석을 정식 `LOCK-610-XX` 식별자로 통합 관리한다.

| LOCK ID | 항목 | 값 | 정본 출처 |
|---------|------|-----|-----------|
| LOCK-610-01 | 모듈 ID 체계 | B/EVX/A/D + 순번 (D2.0-01 번호 유지) | D2.0-01 §5.6, D2.0-02 §7.4.1 |
| LOCK-610-02 | 모듈 간 의존성 그래프 | §1.4 DAG 구조 (단방향, 순환 금지) | D2.0-01 §4, 본 문서 §1.4 |
| LOCK-610-03 | category 필드 | `"EXP"` (Module Catalog 표준) | D2.0-01 §5.5 |
| LOCK-610-04 | 기본 상태 | `enabled = false` (config 명시적 활성화 필수) | D2.0-01 §5.5, 본 문서 §3.2 R-610-3 |
| LOCK-610-05 | EVX 네임스페이스 | `vamos-experimental` (프로덕션 격리) | D2.0-01 §5.13 |
| LOCK-610-06 | V3 비용 상한 | KRW 266,000/월 | D2.0-01 §5.13, 본 문서 §3.3 |
| LOCK-610-07 | BaseModule(ABC) 상속 필수 | 모든 EXP 모듈은 `BaseModule(ABC)` 상속 | D2.0-01 §5.5, 본 문서 §3.1 |
| LOCK-610-08 | 07 Gate 승인 없이 자동 ON 금지 | EXP 모듈 자동 활성화 절대 금지 | D2.0-02 §7, 본 문서 §3.2 R-610-6 |

### 3.1 EXP 모듈 공통 인터페이스

```python
class MyExpModule(BaseModule):
    """category='EXP', 기본 OFF, config에서 enabled=true로 활성화"""
    category = "EXP"

    async def execute(self, input_data: BaseModel) -> BaseModel:
        if not self.config.enabled:
            raise RuntimeError(f"{self.name} is disabled")
        # 모듈 로직 구현
        ...
```

### 3.2 거버넌스 규칙

> **글로벌 거버넌스 규칙**: 본 도메인은 0-0_Governance-Rules-Meta에서 정의한 R1~R11 글로벌 규칙을 전체 준수합니다.
> 아래는 글로벌 규칙에 추가되는 도메인 고유 규칙입니다.

- **R-610-1**: 모든 EXP 모듈은 `BaseModule(ABC)` 상속, `category="EXP"` 필수 → LOCK-610-07, LOCK-610-03
- **R-610-2**: EVX 모듈은 `vamos-experimental` K8s 네임스페이스에 격리 배포 → LOCK-610-05
- **R-610-3**: EXP 모듈은 기본 `enabled=false`, config에서 명시적 활성화 필수 → LOCK-610-04
- **R-610-4**: Module Catalog 표준 필드 준수 (D2.0-01 §5.5) → LOCK-610-03
- **R-610-5**: LOCK/FREEZE 값 변경 금지 → §3.0 LOCK 테이블 전체 적용
- **R-610-6**: EXP 모듈은 07 Gate 승인/비용 통과 없이 자동 ON 절대 금지 → LOCK-610-08

### 3.3 비용 상한

- V3 비용 상한: ₩266,000/월 (LOCK-610-06)
- GPU 공유: vLLM, E-7(STT), EVX 모듈 간 GPU 스케줄링 (NVIDIA MPS 또는 time-sharing)
