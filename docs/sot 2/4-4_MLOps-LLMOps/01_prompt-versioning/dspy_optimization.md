# DSPy 프롬프트 최적화 통합 정의서 — `dspy_optimization.md`

> **정본 파일**: `D:\VAMOS\docs\sot 2\4-4_MLOps-LLMOps\01_prompt-versioning\dspy_optimization.md`
> **세션**: SOT 2 Phase 2 / 도메인 4-4 / 세션 2-6 (DSPy 프롬프트 최적화, **주 폴더**)
> **LABEL**: `S7F-073 HIGH V2`
> **Part2 버전**: V2-Phase 2
> **TEST_MODE**: true (sandbox `D:\VAMOS\docs\test_iso_p2\sot 2\` 에서 작성, production UNCHANGED)

---

## §0 메타 블록

### §0.1 V2 태그 / 변경 이력

| 버전 | 날짜 | 변경 | 작성자 |
|------|------|------|--------|
| V2-Phase2 초안 | 2026-04-18 | 2-6 세션 Step1 — `01+05` 분산 배치 중 **주 폴더** 산출물 신규 작성 | 4-4 / 2-6 서브에이전트 |

### §0.2 정본 계보

```
Level 0: VAMOS 마스터 플랜 (PLAN-3.0)
Level 1: D2.0 DESIGN 문서
Level 2: STEP7-F Part 9 — MLOps/LLMOps 항목 정본 (S7F-069~078)
Level 3: (Part2 NOT COVERED — 비어 있음)
Level 4: sot 2/4-4_MLOps-LLMOps/                      ← 본 산출물 (Level 3+4 겸임)
         ├─ MLOPS_LLMOPS_구조화_종합계획서.md §7 2-6 블록 (L1612~L1684)
         ├─ MLOPS_LLMOPS_상세명세.md §A-6 / §E-3 / §F-2
         ├─ AUTHORITY_CHAIN.md LOCK-ML-01~12
         └─ 01_prompt-versioning/_index.md (S7F-073 주 폴더, HIGH V2)
Level 5: 구현 코드 (backend/vamos_core/mlops/prompts/dspy/)
```

### §0.3 LOCK 정본 강제 (본 산출물이 직접 준수)

| LOCK ID | 값 / 기준 | 본 산출물 적용 섹션 |
|---------|-----------|--------------------|
| LOCK-ML-04 | A/B 테스트 유의수준 `p < 0.05` (상세명세 §A-6) | §5 (DSPy optimizer 검증 A/B gate), §8 (2-5 CONSUMER 인터페이스) |
| LOCK-ML-05 | 품질 게이트 5규칙 (task_completion≥0.85, QoD≥0.85, safety<0.001, p95<3000ms, cost<$0.05) | §6 최적화 루프 승인 gate, §8 2-1 EvalResults CONSUMER |
| LOCK-ML-09 | 카나리 자동 롤백 조건 (QoD 차이 > 0.2 또는 에러율 > Current×2) | §7 롤백 API — 단, 본 산출물은 **프롬프트 차원 rollback** 이며 카나리 gate 와 구분 |
| LOCK-ML-10 | 피드백 루프 2주 스프린트 주기 (QoD +0.1/스프린트) | §5 trainset 구성 주기, §8 2-4 CONSUMER |
| LOCK-ML-12 | 피드백 데이터 100% 로컬 저장 원칙 | §5 trainset 저장 위치, §7 prompt_version_history 저장소 |

### §0.4 교차 참조 블록

| 참조 대상 | 경로 | 관계 |
|-----------|------|------|
| 종합계획서 §7 2-6 블록 | `MLOPS_LLMOPS_구조화_종합계획서.md` L1612~L1684 | 본 산출물 지시서 |
| 상위 SoT STEP7-F Part 9 | `D:\VAMOS\docs\sot\STEP7-F_인프라_배포_MLOps_작업가이드.md` L1199~L1204 S7F-073 | 본 §2 verbatim 인용 |
| 상세명세 §A-6 A/B 테스트 인프라 | `MLOPS_LLMOPS_상세명세.md` L88~L115 | 본 §5 (DSPy optimizer 검증 인프라) |
| 상세명세 §E-3 RLHF-lite 파이프라인 | `MLOPS_LLMOPS_상세명세.md` L330~L354 | 본 §5 (trainset 구성), §8 (2-4 CONSUMER) |
| 상세명세 §F-2 Few-shot 생성 파이프라인 | `MLOPS_LLMOPS_상세명세.md` L412~L418 | 본 §5 / §6 (DSPy Module few-shot injection) |
| 2-1 Benchmark Pipeline | `02_model-evaluation/auto_benchmark_pipeline.md` | §8 CONSUMER (EvalResults → valset metric) |
| 2-4 Feedback Pipeline | `05_feedback-loop/feedback_pipeline.md` | §8 CONSUMER (FeedbackRecord / Top10PatternCluster → trainset) |
| 2-5 A/B Test Framework | `01_prompt-versioning/ab_test_framework.md` | §8 CONSUMER (ABTestConfig / ABTestResult / IABTestRunner → candidate prompt 검증) |
| peer — 2-6 optimization_loop | `05_feedback-loop/optimization_loop.md` | 본 문서와 공동 2-6 산출물. 본 §3~§9 스키마를 verbatim 참조. S7F-073 인용은 본 §2 가 정본, peer §2 는 요약+링크. |

### §0.5 페이지·줄수 목표

- 목표 분량: **~960 줄** (±60 허용 범위)
- §2 상위 SoT 원문 인용은 **verbatim** (재작성 금지)
- §13 Phase 3 시나리오: **≥10건** (TS-DSPY-01~10+)

---

## §1 Purpose / Scope

### §1.1 목적

종합계획서 §7 2-6 블록 L1515: *"DSPy 프레임워크를 통합하여 프롬프트 자동 최적화 루프(평가 → 피드백 → 개선)를 구축하고, 수동 프롬프트 튜닝 의존도를 최소화한다."*

본 산출물은 위 목적을 달성하기 위한 **DSPy Signature / Module / Optimizer 통합 정의서** 로,
다음 4가지를 `LOCK-ML-12` (100% 로컬 저장) 제약 아래 표준화한다:

1. **Signature 정의**: Pydantic v2 기반 Input/Output field 타입 ↔ `dspy.Signature` 매핑 규칙
2. **Module 통합**: `dspy.Predict` / `dspy.ChainOfThought` / `dspy.ReAct` 3종 서브클래스 정본 + LM 백엔드 설정
3. **Optimizer 체계**: `BootstrapFewShot` / `MIPROv2` / `COPRO` 3종 teleprompter 파라미터 + trainset/valset 계약
4. **프롬프트 자동 최적화 루프**: V1(수동) → V2(DSPy 반자동) → V3(완전 자동화) 단계별 스펙

### §1.2 Scope IN (Phase 2 / 2-6 담당)

- DSPy 프레임워크 통합 스펙 (본 산출물)
- 2-1 벤치마크 + 2-4 피드백 → DSPy 입력 end-to-end 파이프라인 (peer `optimization_loop.md`)
- 최적화 이력 관리 (`PromptVersionRecord` 스키마 + rollback API)
- Phase 3 테스트 시나리오 ≥10건

### §1.3 Scope OUT (Phase 3 이월)

- `dspy.LM` 실제 클라이언트 구현 (Claude API 키 로드, 로컬 fallback, 토큰 카운팅 — 구현 코드)
- `BootstrapFewShot` 내부 `max_rounds` / `max_bootstrapped_demos` 실측 튜닝 (Phase 3 baseline 확정 예정)
- Stanford DSPy 신규 teleprompter 릴리즈 (0.4+) 추가 optimizer — Phase 3 이후 도입 재검토
- GPU 비용 벤치마크 (로컬 LM 실행 시) — Phase 3 인프라 작업
- DSPy 와 promptfoo CI 실행 병행 워크플로우 (S7F-070 / `promptfoo_test_spec.md`) — Phase 3 이월

### §1.4 관계 있는 LOCK 경고 보호

- `LOCK-ML-12`: 본 산출물이 생성하는 **모든** DSPy 산출물 (signature JSON, compiled program, prompt_version_history) 은 `~/vamos/dspy/` 로컬 디렉터리에 저장. 외부 LM 호출 **응답** 은 감쇠된 요약만 보관 (원문 transcript 저장 금지 — LOCK-ML-12 정본 해석).
- `LOCK-ML-04`: DSPy optimizer 가 생성한 candidate prompt 의 **production 배포 승인** 은 반드시 2-5 `ab_test_framework.md` 의 `decide_winner()` 에서 `p_value < 0.05` 판정 필요. DSPy 내부 evaluator 가 "winner" 라고 판정하더라도 2-5 gate 우회 금지.

---

## §2 S7F-073 상위 SoT 직접 Read 결과 (정본 인용 원문)

본 세션은 `D:\VAMOS\docs\sot\STEP7-F_인프라_배포_MLOps_작업가이드.md` Part 9 S7F-073 (L1199~L1204) 를 **직접 Read** 하였다.

### §2.1 verbatim 5 bullets 인용 원문 (재작성 없음)

```text
[STEP7-F L1199~L1204 원문]

**S7F-073** | HIGH | V2 | 프롬프트 최적화 — 자동 프롬프트 개선
- 내용: 사용자 피드백 기반 프롬프트 자동 최적화
- 구현:
  - DSPy 프레임워크 (Stanford, 무료): 프롬프트 자동 최적화
  - 방법: 성공/실패 사례 수집 → 패턴 분석 → 프롬프트 수정 → A/B 테스트
  - V1: 수동 개선 → V2: DSPy 반자동 → V3: 완전 자동화
```

### §2.2 5 bullets 해석 / 본 산출물 매핑

| bullet | 원문 | 본 산출물 매핑 |
|--------|------|----------------|
| 1 | 내용: 사용자 피드백 기반 프롬프트 자동 최적화 | §5 (trainset = feedback 기반 성공/실패 사례), §6 (자동 최적화 루프) |
| 2 | DSPy 프레임워크 (Stanford, 무료): 프롬프트 자동 최적화 | §3 Signature / §4 Module / §5 Optimizer 3계층 표준 |
| 3 | 방법: 성공/실패 사례 수집 → 패턴 분석 → 프롬프트 수정 → A/B 테스트 | §5.1 trainset 구성 (성공) → §5.2 valset 구성 (실패 차단) → §6.2 compile (수정) → §6.3 A/B gate (2-5 CONSUMER) |
| 4 (V1) | V1: 수동 개선 | §6.5 V1 fallback 경로 — DSPy 실패 시 human-in-the-loop 수동 개선 복귀 |
| 4 (V2) | V2: DSPy 반자동 | §6.1 **본 Phase 2 목표** — DSPy compile + human 승인 gate |
| 4 (V3) | V3: 완전 자동화 | §6.6 Phase 3 이월 — `auto_promote=True` + 무인 rollback |

### §2.3 ID ↔ 이름 매핑 drift 검사 (§4.3 규칙)

- STEP7-F L1199 정본 이름: **"프롬프트 최적화 — 자동 프롬프트 개선"**
- `01_prompt-versioning/_index.md` L15 표기: **"프롬프트 최적화 (DSPy)"**
- drift 판정: 상위 SoT 이름은 "자동 프롬프트 개선" 을 포함하나 `_index.md` 표기는 "DSPy" 기술 한정. **정합성 유지** — "DSPy" 는 상위 SoT L1202 구현 수단으로 명시되어 있어 축약 타당. **`[CONFLICT_CANDIDATE]` 발행하지 않음** (2-5 S7F-075 / "실험 관리 (A/B 테스트)" 정합 선례 준용).

### §2.4 임계값 미정의 항목 처리

상위 SoT S7F-073 은 **임계값을 정량화하지 않음** (정성적 가이드). 본 산출물은 다음을 명시한다:

- DSPy optimizer 수렴 판정 기준 (loss, iter count) → Phase 3 baseline 확정 예정
- trainset 최소 샘플 수 → `MIN_TRAINSET_SIZE = 50` (본 §5.1 잠정 기준, Phase 3 검증 대상)
- valset 최소 샘플 수 → `MIN_VALSET_SIZE = 20` (본 §5.2 잠정 기준)
- 위 3개 수치는 "Phase 3 baseline 확정 예정" 라벨 부착 — 임의 추정 금지.

---

## §3 DSPy Signature 정의

### §3.1 Signature 개념

DSPy `Signature` 는 "LM 이 수행해야 할 task 의 **선언적 계약**" 이다.
본 도메인은 Pydantic v2 `BaseModel` 을 **Input/Output 컨테이너** 로 두고, `dspy.Signature` 로 브릿지한다.

### §3.2 Input Field / Output Field 타입 정본

| Pydantic v2 타입 | DSPy InputField type | DSPy OutputField type | 주석 |
|------------------|---------------------|----------------------|------|
| `str` (Free text) | `dspy.InputField(desc="...")` | `dspy.OutputField(desc="...")` | Korean desc + English desc 2개 언어 필수 |
| `list[str]` | `dspy.InputField(desc="...", format=list)` | `dspy.OutputField(desc="...", format=list)` | 리스트 크기 hint 포함 |
| `int` / `float` | `dspy.InputField(desc="...")` (파싱 책임) | `dspy.OutputField(desc="...")` | 단위 명시 (ms, USD, count) |
| `Literal["A", "B", "C"]` | `dspy.InputField(desc="choose one: A|B|C")` | `dspy.OutputField(desc="one of: A|B|C")` | enum 치환 |
| `datetime` | `dspy.InputField(desc="ISO8601 datetime")` | `dspy.OutputField(desc="ISO8601 datetime")` | timezone aware |

### §3.3 DSPySignatureSpec Pydantic 모델 (§9 통합 정의서 일부)

```python
from __future__ import annotations
from enum import Enum
from typing import Literal, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class FieldKind(str, Enum):
    INPUT = "input"
    OUTPUT = "output"


class SignatureField(BaseModel):
    """DSPy Signature 내 단일 field 정본."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(..., pattern=r"^[a-z][a-z0-9_]{1,48}$",
                      description="snake_case, 1~49 chars")
    kind: FieldKind
    pydantic_type: str = Field(..., description="예: 'str', 'list[str]', 'Literal[\"A\",\"B\"]'")
    desc_ko: str = Field(..., min_length=1, max_length=400)
    desc_en: str = Field(..., min_length=1, max_length=400)
    required: bool = True
    example: Optional[str] = Field(default=None, max_length=1000)


class DSPySignatureSpec(BaseModel):
    """DSPy Signature 통합 정의 — dspy.Signature(_for=name) 로 변환 가능."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    signature_id: str = Field(..., pattern=r"^sig-[a-z0-9_\-]{3,64}$")
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")  # Semantic Versioning
    task_description_ko: str = Field(..., min_length=10, max_length=2000)
    task_description_en: str = Field(..., min_length=10, max_length=2000)
    inputs: list[SignatureField] = Field(..., min_length=1, max_length=20)
    outputs: list[SignatureField] = Field(..., min_length=1, max_length=10)
    created_at: datetime
    parent_signature_id: Optional[str] = Field(default=None,
        description="이전 version 의 signature_id — 롤백 시 복구 타깃")
```

### §3.4 dspy.Signature 매핑 예시

```python
# 본 예시는 DSPy 문법 참고용 — 실제 구현은 Phase 3.
import dspy

class CoreSystemPrompt(dspy.Signature):
    """
    VAMOS Core System 턴 응답.
    DSPySignatureSpec.signature_id = 'sig-core-system-v3.2.0'
    """

    user_query: str = dspy.InputField(
        desc="사용자 자연어 입력 / User natural-language query")
    session_context: str = dspy.InputField(
        desc="직전 3턴 요약 / Previous 3-turn summary")

    answer: str = dspy.OutputField(
        desc="최종 응답 문장 / Final answer sentence")
    safety_flag: Literal["safe", "warn", "block"] = dspy.OutputField(
        desc="안전성 라벨 / Safety label: safe|warn|block")
```

### §3.5 Signature 버저닝 연계

`DSPySignatureSpec.version` 은 `LOCK-ML-02` (PATCH=문구조정, MINOR=구조변경, MAJOR=역할변경) 를 준수한다.
- field `desc_ko` / `desc_en` 수정 → PATCH (`3.2.0` → `3.2.1`)
- field 추가 / 삭제 → MINOR (`3.2.0` → `3.3.0`)
- task semantics 변경 → MAJOR (`3.2.0` → `4.0.0`) + 하위 호환성 명시 필수

---

## §4 DSPy Module 통합

### §4.1 3종 Module subclass 정본

| Module | dspy 클래스 | 용도 | 본 도메인 적용 |
|--------|-------------|------|----------------|
| Predict | `dspy.Predict(signature)` | 직접 signature → output | Core System 주 응답 (Signature: `sig-core-system-*`) |
| ChainOfThought | `dspy.ChainOfThought(signature)` | 중간 추론 chain 포함 | 복잡 쿼리 (Signature: `sig-reasoning-*`) — VRE 1-1 연계 |
| ReAct | `dspy.ReAct(signature, tools=[...])` | tool-use 루프 | Agent Teams 6-3 Tool Use (Signature: `sig-agent-tool-*`) |

### §4.2 DSPyModuleSpec Pydantic

```python
class ModuleKind(str, Enum):
    PREDICT = "Predict"
    CHAIN_OF_THOUGHT = "ChainOfThought"
    REACT = "ReAct"


class DSPyModuleSpec(BaseModel):
    """DSPy Module 통합 정의 — dspy.Module subclass 생성 규칙."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    module_id: str = Field(..., pattern=r"^mod-[a-z0-9_\-]{3,64}$")
    kind: ModuleKind
    signature_id: str = Field(..., description="DSPySignatureSpec.signature_id")
    lm_backend: Literal["claude-3-5-sonnet-20241022",
                        "claude-3-7-sonnet-20250219",
                        "gpt-4o-2024-08-06",
                        "gpt-4o-mini-2024-07-18",
                        "local-llama-3-70b"] = "claude-3-5-sonnet-20241022"
    max_tokens: int = Field(default=2048, ge=128, le=100_000)
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    top_p: float = Field(default=0.95, ge=0.0, le=1.0)
    tools: list[str] = Field(default_factory=list,
        description="ReAct 전용. tool_name 목록. 다른 kind 에서는 반드시 빈 리스트.")
    retry_max: int = Field(default=3, ge=0, le=10)
    timeout_seconds: float = Field(default=30.0, ge=1.0, le=600.0)

    def validate_consistency(self) -> None:
        """ReAct 아닌 경우 tools 비어야 함 — Phase 3 실구현 validator."""
        if self.kind != ModuleKind.REACT and self.tools:
            raise ValueError(f"{self.kind} module 는 tools 를 가질 수 없습니다.")
```

### §4.3 forward() 계약

```python
# Predict 예시 (Phase 3 실구현 템플릿)
class CoreSystemPredictor(dspy.Module):
    """dspy.Module subclass — DSPyModuleSpec.module_id = 'mod-core-system-predict'."""

    def __init__(self, spec: DSPyModuleSpec):
        super().__init__()
        self.spec = spec
        self.predict = dspy.Predict(CoreSystemPrompt)  # §3.4 Signature

    def forward(self, user_query: str, session_context: str):
        """반환: dspy.Prediction with .answer / .safety_flag."""
        return self.predict(user_query=user_query,
                            session_context=session_context)
```

### §4.4 LM 백엔드 구성 (LOCK-ML-12 준수)

- 프로덕션 기본: `claude-3-5-sonnet-20241022` (Anthropic API, TLS).
- fallback: `local-llama-3-70b` (로컬 추론, 외부 전송 없음 — LOCK-ML-12 정본 경로).
- DSPy LM 레벨에서 **응답 원문** 보관 금지 (LOCK-ML-12 해석). DSPy 내부 cache 는 메타만 (hash, latency, token_count) 보관.

### §4.5 Module ↔ Signature 1:1 관계

하나의 `DSPyModuleSpec.signature_id` 는 하나의 `DSPySignatureSpec.signature_id` 와 1:1 매칭.
여러 Module 이 동일 Signature 를 참조할 수 있으나, 동일 Module 이 2개 이상 Signature 참조는 **금지**.

---

## §5 DSPy Optimizer (Teleprompter)

### §5.1 3종 Optimizer 체계 정본

| Optimizer | dspy 클래스 | 용도 | trainset 요구 |
|-----------|-------------|------|---------------|
| BootstrapFewShot | `dspy.teleprompt.BootstrapFewShot` | few-shot example 자동 생성 | ≥50건 (잠정) |
| MIPROv2 | `dspy.teleprompt.MIPROv2` | instruction + few-shot 공동 최적화 | ≥100건 (잠정) |
| COPRO | `dspy.teleprompt.COPRO` | instruction 만 최적화 (cost 효율) | ≥30건 (잠정) |

> 위 3개 수치 (50/100/30) 는 **Phase 3 baseline 확정 예정** 잠정치 — §2.4 처리 규칙 적용.

### §5.2 DSPyOptimizerConfig Pydantic

```python
class OptimizerKind(str, Enum):
    BOOTSTRAP_FEW_SHOT = "BootstrapFewShot"
    MIPRO_V2 = "MIPROv2"
    COPRO = "COPRO"


class DSPyOptimizerConfig(BaseModel):
    """DSPy teleprompter 설정 정본."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    optimizer_id: str = Field(..., pattern=r"^opt-[a-z0-9_\-]{3,64}$")
    kind: OptimizerKind
    module_id: str = Field(..., description="DSPyModuleSpec.module_id")
    max_rounds: int = Field(default=3, ge=1, le=20,
        description="teleprompter 재시도 라운드. Phase 3 baseline 확정 예정.")
    max_bootstrapped_demos: int = Field(default=4, ge=1, le=16,
        description="BootstrapFewShot 전용. 타 kind 는 무시.")
    max_labeled_demos: int = Field(default=4, ge=1, le=16,
        description="labeled demo (2-4 positive_examples) 주입 상한")
    num_threads: int = Field(default=1, ge=1, le=16,
        description="병렬 compile worker 수. 로컬 LM 시 1 권장.")
    metric_name: str = Field(..., description="valset evaluation metric — 예: 'qod_score'")
    trainset_source: Literal["feedback_positive",  # 2-4 positive_examples
                             "feedback_mixed",      # 2-4 positive + negative
                             "benchmark_gold",      # 2-1 golden dataset
                             "manual"] = "feedback_positive"
    valset_source: Literal["benchmark_eval",        # 2-1 EvalResults.dimension_results
                           "feedback_holdout",
                           "manual"] = "benchmark_eval"
    min_trainset_size: int = Field(default=50, ge=10, le=10_000,
        description="trainset_source 로부터 수집할 최소 샘플 수")
    min_valset_size: int = Field(default=20, ge=5, le=5_000)
```

### §5.3 trainset / valset 데이터 계약

- **trainset**: `list[dspy.Example]` — 각 example 은 Signature 의 `inputs` field 전체 + 기대 `outputs` field 전체를 attribute 로 포함.
- **valset**: `list[dspy.Example]` — trainset 과 동일 구조, 단 `with_inputs(*names)` 로 input 필드 명시.
- trainset ∩ valset = ∅ (중복 샘플 금지 — DSPy 내부 무작위 split 가 아닌 **명시적 분리** 필수).

### §5.4 trainset 수집 경로 (2-4 CONSUMER)

```
2-4 feedback_pipeline.md
  ├─ FeedbackRecord (signal_score ≥ +1.0)   ── positive → trainset
  ├─ FeedbackRecord (signal_score ≤ -1.0)   ── negative → trainset (augment with preferred correction)
  └─ Top10PatternCluster.clusters[].representative_feedback_ids
        ↓ 본 §5.4 ConvertToTrainset()
     list[dspy.Example]   (min_trainset_size ≥ 50)
```

### §5.5 valset 수집 경로 (2-1 CONSUMER)

```
2-1 auto_benchmark_pipeline.md
  └─ EvalResults.dimension_results (D1~D8)
        ↓ 본 §5.5 ConvertToValset()
     list[dspy.Example] with_inputs(...)   (min_valset_size ≥ 20)
```

### §5.6 metric function 계약

DSPy teleprompter 는 `metric: Callable[[dspy.Example, dspy.Prediction], float]` 를 요구한다.
본 도메인은 2-1 `EvalResults.qod_score` (0.0~1.0) 를 기본 metric 으로 채택한다 (LOCK-ML-05 정본):

```python
def qod_metric(example: dspy.Example, prediction: dspy.Prediction) -> float:
    """DSPy metric — 예측 출력에 대한 QoD 점수. 높을수록 좋음.

    상세명세 §B-5 정본 5규칙 중 QoD ≥ 0.85 기준 통과 확인.
    """
    # Phase 3 실구현: LLM-judge 호출 → 0.0~1.0 점수 반환
    # 본 Phase 2 정의서 단계에서는 계약만 확정
    raise NotImplementedError("Phase 3 baseline 확정 예정")
```

### §5.7 IDSPyOptimizer ABC (§10 재인용)

```python
from abc import ABC, abstractmethod


class CompiledProgram(BaseModel):
    """DSPy teleprompter compile 결과 직렬화."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    program_id: str = Field(..., pattern=r"^prog-[a-z0-9_\-]{3,64}$")
    optimizer_id: str
    compiled_at: datetime
    compiled_state_path: str = Field(..., description="~/vamos/dspy/compiled/{program_id}.json")
    metric_name: str
    valset_score_before: float = Field(..., ge=0.0, le=1.0)
    valset_score_after: float = Field(..., ge=0.0, le=1.0)
    delta: float = Field(..., description="after - before")
    trainset_size: int = Field(..., ge=1)
    valset_size: int = Field(..., ge=1)


class IDSPyOptimizer(ABC):
    """DSPy teleprompter 책임 ABC (본 산출물 §10 정본)."""

    @abstractmethod
    async def compile(
        self,
        signature: DSPySignatureSpec,
        trainset: list,   # list[dspy.Example]
        valset: list,     # list[dspy.Example]
        config: DSPyOptimizerConfig,
    ) -> CompiledProgram:
        """teleprompter 실행 → 최적화된 프로그램 반환.

        - 실패 시 raise — 상위 루프 (§6) 가 rollback 여부 결정.
        - valset_score_after < valset_score_before 시 자동 reject (§6.4).
        """
```

---

## §6 프롬프트 자동 최적화 루프 (로컬 V2 반자동)

### §6.1 V1 → V2 → V3 3단계 정본 비교

| 단계 | 트리거 | 주 행위자 | DSPy 참여 | A/B gate | 승인 gate | 본 Phase 2 대응 |
|------|--------|-----------|-----------|----------|-----------|----------------|
| **V1** | 수동 (2주 스프린트 Day 11) | QA 엔지니어 | ✗ | 2-5 수동 제출 | 인간 리뷰 | §6.5 fallback 경로 |
| **V2** | 반자동 (feedback trainset 준비 완료) | DSPy optimizer + 인간 승인자 | ✓ (§5) | 2-5 자동 호출 | 인간 승인 필수 (§6.4) | **본 Phase 2 목표** |
| **V3** | 완전 자동 (Phase 3 이후) | DSPy + decide_winner + canary | ✓ | 2-5 자동 + auto_promote | 무인 (rollback 자동) | §6.6 Phase 3 이월 |

### §6.2 V2 반자동 루프 플로우 (본 Phase 2 정본)

```
[1] Trigger (매일 1회 또는 Day 11 스프린트 gate)
        │
[2] trainset 수집 (§5.4) ← 2-4 feedback_pipeline
        │
[3] valset 수집 (§5.5) ← 2-1 auto_benchmark_pipeline
        │
[4] 크기 검증: len(trainset) ≥ min_trainset_size AND len(valset) ≥ min_valset_size
        │  (불만족 시 §6.4 reject + 로그)
        │
[5] IDSPyOptimizer.compile(signature, trainset, valset, config)
        │  → CompiledProgram (valset_score_before / after / delta)
        │
[6] delta >= 0 확인
        │  (delta < 0 시 §6.4 reject + rollback 제안)
        │
[7] candidate prompt 추출 (compiled_state_path JSON 에서 instruction + few-shots)
        │
[8] 2-5 ab_test_framework.IABTestRunner.start(ABTestConfig)
        │  variant_a = 현행 production prompt
        │  variant_b = DSPy candidate prompt
        │
[9] 2-5 runner.evaluate(test_id) → ABTestResult
        │
[10] winner 판정 + human gate
        │  - winner == "b" AND p_value < 0.05  →  승인 요청 (human)
        │  - 인간 승인  →  promote (prompt_version_history 업데이트, §7)
        │  - 인간 거부 또는 winner != "b"  →  archive + log
```

### §6.3 A/B gate — 2-5 CONSUMER 정합

candidate prompt 는 반드시 `ABTestConfig.variant_b.prompt_patch` 에 매핑한다:

```python
# dspy_optimization → ab_test_framework 핸드오프
variant_b = ABTestVariant(
    prompt_id=f"prompt-dspy-{compiled.program_id}",
    model_id=config.module_spec.lm_backend,
    temperature=config.module_spec.temperature,
    max_tokens=config.module_spec.max_tokens,
    prompt_patch=f"DSPy compiled: program_id={compiled.program_id}, "
                 f"valset_delta=+{compiled.delta:.3f}",
    provenance=f"dspy_optimizer:{config.optimizer_id}",
)
```

`ABTestConfig.significance_level=0.05` (LOCK-ML-04 정본) + `bonferroni_correction=True` 는 2-5 기본값 유지.

### §6.4 승인 / 반려 분기 (human-in-the-loop gate)

| 조건 | 분기 | 후속 조치 |
|------|------|-----------|
| `len(trainset) < min_trainset_size` | reject | §5.4 trainset 보강 대기 → 다음 라운드 재시도 |
| `compile` 예외 발생 | reject | I-20 에스컬레이션 (§11 payload) + retry_count ≤ retry_max 재시도 |
| `compiled.delta < 0` | reject | trainset 재검토 플래그 + Phase 3 TS-DSPY-05 시나리오 |
| `decide_winner.winner != "b"` | reject | archive `CompiledProgram` + log (2-5 ABTestResult 동봉) |
| `winner == "b" AND p < 0.05 AND human APPROVE` | **promote** | §7 prompt_version_history UPDATE + 2-3 canary 진입 (간접) |
| `winner == "b" AND p < 0.05 AND human REJECT` | reject | 사유 기록 + 차기 라운드 피드백 재분석 |

### §6.5 V1 fallback (DSPy 실패 시)

다음 경우 V1 수동 개선 경로로 복귀:
- `compile` 3회 연속 실패 (retry_max 초과)
- `trainset` 부족이 2 스프린트 (4주) 지속
- LM 백엔드 장애 지속 24h 초과

V1 복귀는 `FeedbackSprint.applied_changes` 에 `"v1_manual_revert:<reason>"` 로 기록 (LOCK-ML-10 gate 직전).

### §6.6 V3 완전 자동화 (Phase 3 이월)

- `auto_promote=True` + decide_winner 후 자동 2-3 canary 진입
- 24h 카나리 QoD 모니터링 후 LOCK-ML-09 rollback 조건 충족 시 자동 rollback
- **본 Phase 2 에서는 auto_promote=False 로 강제 고정** — §9 `DSPyOptimizerConfig` validator 에 경고 추가 예정 (Phase 3).

---

## §7 최적화 이력 관리 — PromptVersionRecord

### §7.1 prompt_version_history 스키마

```python
class PromptVersionStatus(str, Enum):
    DRAFT = "draft"
    STAGING = "staging"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    ROLLED_BACK = "rolled_back"


class PromptVersionRecord(BaseModel):
    """DSPy 생성 / 승격 / 롤백된 프롬프트의 이력 엔트리.

    저장 위치: ~/vamos/dspy/history/prompt_version_history.jsonl (LOCK-ML-12)
    append-only, rollback 시에도 과거 엔트리 수정 금지.
    """
    model_config = ConfigDict(frozen=True, extra="forbid")

    version_id: str = Field(..., pattern=r"^pv-[0-9a-z._\-]{3,80}$",
                             description="예: 'pv-core-sys-v3.2.1' ('.' 허용 — dotted semver 예시 정합)")
    parent_version_id: Optional[str] = Field(default=None,
        description="직전 버전 — MAJOR/MINOR/PATCH 계승 트리")
    signature_id: str = Field(..., description="DSPySignatureSpec.signature_id")
    module_id: str = Field(..., description="DSPyModuleSpec.module_id")
    dspy_config: DSPyOptimizerConfig
    optimizer_used: OptimizerKind
    compiled_program_id: str = Field(..., description="CompiledProgram.program_id")
    benchmark_delta: float = Field(..., description="valset_score_after - valset_score_before")
    ab_test_id: Optional[str] = Field(default=None,
        description="2-5 ABTestResult.test_id — promote 전 None")
    ab_test_winner: Optional[Literal["a", "b", "inconclusive"]] = None
    ab_test_p_value: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    approved_by: Optional[str] = Field(default=None,
        description="human-in-the-loop 승인자 ID (V2 필수)")
    approved_at: Optional[datetime] = None
    status: PromptVersionStatus = PromptVersionStatus.DRAFT
    rollback_target: Optional[str] = Field(default=None,
        description="이 버전 롤백 시 복구할 이전 version_id (보통 parent_version_id)")
    created_at: datetime
```

### §7.2 version tree 예시

```
pv-core-sys-v3.0.0 (production, 2026-03-01)
      │
      ├── pv-core-sys-v3.1.0 (MINOR, DSPy COPRO, DEPRECATED)
      │       │
      │       └── pv-core-sys-v3.2.0 (PATCH, DSPy BootstrapFewShot, PRODUCTION)
      │                 │
      │                 └── pv-core-sys-v3.2.1 (PATCH, DSPy MIPROv2, STAGING, A/B pending)
      │
      └── pv-core-sys-v3.0.1 (PATCH, rolled back from v3.1.0)
```

### §7.3 rollback API

```python
class IPromptVersionRegistry(ABC):
    """prompt_version_history 저장소 ABC."""

    @abstractmethod
    async def rollback_to(self, current_version_id: str,
                           target_version_id: Optional[str] = None) -> PromptVersionRecord:
        """
        current → target 으로 롤백.
        target 미지정 시 current.rollback_target 또는 current.parent_version_id 순으로 자동 선정.

        부작용:
          - current.status 를 ROLLED_BACK 으로 갱신 (새 엔트리 append, 기존 엔트리 불변)
          - target.status 를 PRODUCTION 으로 복원 (새 엔트리 append)
          - R-01-7 로그 emit (source_module='dspy_optimization', event='rollback')

        반환: 복원된 target 의 최신 PromptVersionRecord.
        """
```

### §7.4 rollback 권고 윈도우

- V2 반자동 단계: promote 후 **7일 이내** rollback 권고 (LOCK-ML-10 2주 스프린트의 전반부).
- 7일 경과 후에는 새 버전 promote 권고 (과거 rollback 은 여전히 가능하나 warning 로그).

### §7.5 저장소 불변성 (LOCK-ML-12 강화)

- `prompt_version_history.jsonl` 은 append-only
- 과거 엔트리의 `status` 는 "현재 스냅샷" 이 아닌 "엔트리 생성 당시" 값
- 현재 status 조회 시 `version_id` 별 **최신** 엔트리를 GROUP BY 로 집계

---

## §8 인터페이스 정합 — 2-1 / 2-4 / 2-5 verbatim 필드 매핑

본 세션은 sandbox 인터페이스 정합 Read 결과 **3종 계약** 이 본 산출물과 verbatim 일치함을 확인하였다.

### §8.1 2-1 EvalResults (CONSUMER ← `02_model-evaluation/auto_benchmark_pipeline.md` §5.3)

```python
# 2-1 원문 정본 (verbatim — sandbox L295~L323)
class EvalResults(BaseModel):
    """게이트 입력 통합 결과 (LOCK-ML-05 평가 대상)."""
    benchmark_run_id: str
    model_id: str
    profile: BenchmarkProfile
    started_at: datetime
    completed_at: datetime
    correlation_id: str
    task_completion: float       # ≥0.0, ≤1.0
    qod_score: float             # ≥0.0, ≤1.0
    safety_violation: float      # ≥0.0, ≤1.0
    p95_latency_ms: float        # ≥0.0
    cost_per_interaction: float  # ≥0.0
    dimension_results: list[DimensionResult]  # min=8, max=8
```

| 필드 | 본 산출물 매핑 |
|------|----------------|
| `qod_score` | §5.6 기본 metric, §7 `PromptVersionRecord.benchmark_delta` 계산 입력 |
| `dimension_results` | §5.5 valset 구성 원천 (D1~D8 각 샘플 → dspy.Example) |
| `benchmark_run_id` | `PromptVersionRecord` 에 참조 불필요 (간접 — CompiledProgram 로그 태그) |
| `task_completion` / `safety_violation` / `p95_latency_ms` / `cost_per_interaction` | §6.4 promote gate 동시 충족 필요 (LOCK-ML-05 5규칙) |

**정합 판정**: ✅ VERBATIM — 본 산출물 §5.5 / §5.6 / §7 은 위 필드명을 재정의 없이 인용.

### §8.2 2-4 Feedback / Top10PatternCluster (CONSUMER ← `05_feedback-loop/feedback_pipeline.md` §4.3~§4.5)

```python
# 2-4 원문 정본 (verbatim — sandbox L251~L324)
class FeedbackRecord(BaseModel):
    id: str; session_id: str; turn_id: str
    feedback_type: FeedbackType
    signal: FeedbackSignal
    score: Optional[float]          # ⭐ 1~5
    text: Optional[str]
    context: FeedbackContext
    timestamp: datetime
    user_segment: str
    signal_score: float             # FR-7 정규화 수치 (-2.0 ~ +2.0)
    collection_device: Literal["desktop", "mobile", "web"]
    consent_flag: bool
    rejected_duplicate: bool

class Top10PatternCluster(BaseModel):
    sprint_id: str
    generated_at: datetime
    clusters: list[FeedbackCluster]  # max=10

class FeedbackSprint(BaseModel):
    sprint_id: str
    start: datetime
    end: datetime
    top_patterns: Top10PatternCluster
    applied_changes: list[str]
    qod_delta: float
    deploy_approved: bool
```

| 필드 | 본 산출물 매핑 |
|------|----------------|
| `FeedbackRecord.signal_score` | §5.4 trainset 분류 기준 (`≥ +1.0` → positive_example, `≤ -1.0` → negative_example) |
| `FeedbackRecord.consent_flag` | §5.4 수집 필터 — `False` 면 trainset 에서 제외 (LOCK-ML-12) |
| `Top10PatternCluster.clusters[].representative_feedback_ids` | §5.4 representative example seed — few-shot injection 용 |
| `FeedbackSprint.qod_delta` | §6.1 V2 트리거 gate — `qod_delta < 0` 연속 2스프린트 시 DSPy compile 보류 (TS-DSPY-07) |
| `FeedbackSprint.applied_changes` | §6.5 V1 fallback 기록 포맷 (`"v1_manual_revert:<reason>"`) |

**정합 판정**: ✅ VERBATIM — 본 산출물 §5.4 / §6.5 은 위 필드명을 재정의 없이 인용.

### §8.3 2-5 ABTestConfig / ABTestResult / IABTestRunner (CONSUMER ← `01_prompt-versioning/ab_test_framework.md` §4.3~§9.2)

```python
# 2-5 원문 정본 (verbatim — sandbox L227~L292, L390~L427, L813~L842)
class ABTestConfig(BaseModel):
    test_id: str
    created_at: datetime
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    status: TestStatus
    variant_a: ABTestVariant
    variant_b: ABTestVariant            # prompt_patch / provenance → DSPy candidate 주입점
    traffic_split: float                # 0.001 ~ 0.5
    metrics: list[MetricSpec]
    min_sample_size: int                # 30 ~ 1_000_000
    max_duration_hours: int             # 1 ~ 720
    significance_level: float           # LOCK-ML-04 = 0.05
    statistical_power_target: float
    bonferroni_correction: bool
    auto_promote: bool                  # V2 단계에서 False 고정 (§6.6)
    langfuse_experiment_id: Optional[str]
    traffic_salt: str

class ABTestResult(BaseModel):
    test_id: str
    config_snapshot: ABTestConfig
    variant_a_metrics: VariantMetrics
    variant_b_metrics: VariantMetrics
    sample_size: int
    duration_hours: float
    per_metric: list[MetricStatResult]
    primary_metric_result: MetricStatResult
    p_value: float
    confidence_interval: ConfidenceInterval
    statistical_power: float
    winner: Winner                       # Literal["a","b","inconclusive"]
    decision_rationale: str
    decided_at: datetime
    langfuse_experiment_id: Optional[str]
    archived: bool
    archive_path: Optional[str]

class IABTestRunner(ABC):
    async def start(self, config: ABTestConfig) -> str: ...
    async def route(self, user_id: str, test_id: str) -> Literal["a", "b"]: ...
    async def log(self, test_id, user_id, variant, metrics, trace_id) -> None: ...
    async def evaluate(self, test_id: str) -> ABTestResult: ...
    async def archive(self, result: ABTestResult) -> None: ...
```

| 필드 | 본 산출물 매핑 |
|------|----------------|
| `ABTestConfig.variant_b.prompt_patch` | §6.3 DSPy candidate prompt 주입점 |
| `ABTestConfig.variant_b.provenance` | §6.3 `"dspy_optimizer:<optimizer_id>"` |
| `ABTestConfig.significance_level` | §6.2 [10] human gate 조건 (LOCK-ML-04) |
| `ABTestConfig.auto_promote` | §6.6 V2 단계에서 False 고정 (V3 이월) |
| `ABTestResult.winner` | §6.4 promote/reject 분기 |
| `ABTestResult.p_value` | §6.4 promote gate 동시 충족 필요 |
| `IABTestRunner.evaluate` | §6.2 [9] 호출점 |
| `IABTestRunner.start` | §6.2 [8] 호출점 |

**정합 판정**: ✅ VERBATIM — 본 산출물 §6.2 / §6.3 / §6.4 는 위 필드/메소드명을 재정의 없이 인용.

### §8.4 3종 interface 정합 요약

| 인터페이스 | 정합 상태 | 불일치 필드 | 마커 |
|-----------|-----------|-------------|------|
| 2-1 EvalResults | ✅ VERBATIM | 0건 | — |
| 2-4 FeedbackRecord / Top10PatternCluster / FeedbackSprint | ✅ VERBATIM | 0건 | — |
| 2-5 ABTestConfig / ABTestResult / IABTestRunner | ✅ VERBATIM | 0건 | — |

**`[INTERFACE_MISMATCH]` 마커 발행 없음** — 3종 interface 모두 정합.

---

## §9 Pydantic v2 공통 자료 구조 (통합 선언)

본 섹션은 §3~§8 에서 분산 정의한 Pydantic v2 모델의 **통합 선언부** 이다 — 구현 시 단일 파일 (`backend/vamos_core/mlops/dspy/schemas.py`) 로 배포.

### §9.1 import 블록

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Literal, Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator, field_validator
```

### §9.2 Enum 선언

```python
class FieldKind(str, Enum):
    INPUT = "input"
    OUTPUT = "output"


class ModuleKind(str, Enum):
    PREDICT = "Predict"
    CHAIN_OF_THOUGHT = "ChainOfThought"
    REACT = "ReAct"


class OptimizerKind(str, Enum):
    BOOTSTRAP_FEW_SHOT = "BootstrapFewShot"
    MIPRO_V2 = "MIPROv2"
    COPRO = "COPRO"


class PromptVersionStatus(str, Enum):
    DRAFT = "draft"
    STAGING = "staging"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    ROLLED_BACK = "rolled_back"
```

### §9.3 모델 선언 (§3~§7 재수록, 참조 편의)

- `SignatureField` (§3.3)
- `DSPySignatureSpec` (§3.3)
- `DSPyModuleSpec` (§4.2)
- `DSPyOptimizerConfig` (§5.2)
- `CompiledProgram` (§5.7)
- `PromptVersionRecord` (§7.1)

### §9.4 model_config 규칙

모든 모델: `ConfigDict(frozen=True, extra="forbid")` 강제.
- `frozen=True`: 불변 객체 — LOCK-ML-12 append-only 원칙 지원
- `extra="forbid"`: 정의되지 않은 필드 차단 — schema drift 방지

### §9.5 cross-reference 무결성

- `DSPyModuleSpec.signature_id` → 존재하는 `DSPySignatureSpec.signature_id` 와 매칭 (런타임 validator, Phase 3)
- `DSPyOptimizerConfig.module_id` → 존재하는 `DSPyModuleSpec.module_id` 와 매칭
- `PromptVersionRecord.signature_id` / `module_id` / `compiled_program_id` → 각 원본 ID 존재 확인
- `PromptVersionRecord.parent_version_id` / `rollback_target` → 존재하는 `version_id` 와 매칭 또는 `None`

---

## §10 ABC 패턴 — IDSPyOptimizer / IPromptVersionRegistry

### §10.1 IDSPyOptimizer (§5.7 재인용)

```python
class IDSPyOptimizer(ABC):
    @abstractmethod
    async def compile(
        self,
        signature: DSPySignatureSpec,
        trainset: list,
        valset: list,
        config: DSPyOptimizerConfig,
    ) -> CompiledProgram: ...
```

### §10.2 IPromptVersionRegistry (§7.3 재인용)

```python
class IPromptVersionRegistry(ABC):
    @abstractmethod
    async def append(self, record: PromptVersionRecord) -> None: ...

    @abstractmethod
    async def get_latest(self, version_id: str) -> PromptVersionRecord: ...

    @abstractmethod
    async def list_tree(self, root_version_id: str) -> list[PromptVersionRecord]: ...

    @abstractmethod
    async def rollback_to(self, current_version_id: str,
                           target_version_id: Optional[str] = None) -> PromptVersionRecord: ...
```

### §10.3 ABC 준수 체크리스트

- [x] `IDSPyOptimizer.compile` 비동기 (async) — 외부 LM 호출 대비
- [x] `IPromptVersionRegistry` 모든 메소드 비동기 — 로컬 파일 I/O 대응 (aiofiles)
- [x] 모든 ABC 는 `base_service_abc.md` (6-3 기반 패턴) 와 호환 — import 순환 없음
- [x] 구현체 (Phase 3) 는 반드시 `IDSPyOptimizer` / `IPromptVersionRegistry` 를 상속

---

## §11 로깅 (R-01-7 중첩 JSON)

### §11.1 EscalationPayload 선언

```python
class EscalationPayload(BaseModel):
    """R-01-7 에스컬레이션 표준 페이로드."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    source_module: Literal["dspy_optimization"]
    error_code: str = Field(..., pattern=r"^DSPY-[0-9]{3}$")
    partial_result: Optional[dict] = Field(default=None,
        description="compile 중단 시 부분 결과 (valset_score_before 등)")
    retry_count: int = Field(..., ge=0, le=10)
    trace_id: str = Field(..., pattern=r"^trace-[0-9a-z]{16,64}$")
```

### §11.2 error_code 정본

| Code | 의미 | 트리거 위치 |
|------|------|-------------|
| DSPY-001 | trainset 부족 | §6.4 [4] |
| DSPY-002 | valset 부족 | §6.4 [4] |
| DSPY-003 | compile 예외 | §6.4 [5] |
| DSPY-004 | valset_score 하락 (delta<0) | §6.4 [6] |
| DSPY-005 | A/B 패배 (winner != "b") | §6.4 [10] |
| DSPY-006 | human reject | §6.4 [10] |
| DSPY-007 | LM 타임아웃 | §4.2 retry_max 초과 |
| DSPY-008 | token limit 초과 | §4.2 max_tokens |
| DSPY-009 | rollback 발생 | §7.3 |
| DSPY-010 | signature cross-ref 무결성 실패 | §9.5 |

### §11.3 중첩 JSON 로그 포맷 예시

```json
{
  "timestamp": "2026-04-18T09:30:00Z",
  "level": "ERROR",
  "logger": "vamos.mlops.dspy.optimizer",
  "trace_id": "trace-abcdef0123456789",
  "error": {
    "code": "DSPY-004",
    "message": "valset score regressed (delta=-0.031)"
  },
  "context": {
    "signature_id": "sig-core-system-v3.2.0",
    "module_id": "mod-core-system-predict",
    "optimizer_id": "opt-mipro-v2-default",
    "trainset_size": 87,
    "valset_size": 24,
    "valset_score_before": 0.841,
    "valset_score_after": 0.810
  },
  "recovery": {
    "action": "reject_and_log",
    "retry_planned": false,
    "next_step": "trainset_reinspection_flag"
  }
}
```

### §11.4 복구 전략 매트릭스 (Phase별)

| Phase | 실패 유형 | 1차 복구 | 2차 복구 | Phase 3 escalation |
|-------|-----------|----------|----------|--------------------|
| compile | LM timeout / token limit | retry (exp backoff, max 3회) | reduce `max_tokens` 10% | I-20 + V1 fallback |
| compile | trainset 부족 | 2-4 스프린트 1회 wait | 수동 seed example 주입 | I-20 + V1 fallback |
| compile | delta<0 | 단일 reject 기록 | trainset 정제 재시도 (1회) | V1 fallback 후보 |
| A/B gate | p>=0.05 | 기간 연장 (max 30일) | 포기 (archive) | V1 fallback 후보 |
| A/B gate | 인간 거부 | 사유 기록 후 포기 | — | — |
| registry | append 실패 (디스크 full) | 지수 backoff (5회) | `~/vamos/dspy/history.jsonl.tmp` 로 export | I-20 디스크 관리 alert |

---

## §12 Phase 2 → Phase 3 Exit Gate 기여 항목

본 세션 (2-6) 이 Phase 3 exit gate 에서 담당하는 항목:

| Exit Gate | 담당 본 세션 기여 | 본 산출물 근거 섹션 |
|-----------|-------------------|---------------------|
| G2-1 (Phase 2 산출물 수량/분량) | 2 V2 파일 생성 (`dspy_optimization.md` + `optimization_loop.md`), 각 ~900~1,000줄 | 본 §0~§13, peer §0~§12 |
| G2-2 (LOCK 정본 강제 0 위반) | LOCK-ML-04 / 05 / 09 / 10 / 12 적용 | 본 §0.3 매핑표 |
| G2-3 (인터페이스 정합) | 3종 interface VERBATIM 일치 | 본 §8 매핑표 |
| G2-4 (Phase 3 시나리오 ≥10건 × 2 파일) | TS-DSPY-01~10+ (본 §13) + TS-OPT-01~10+ (peer §12) | 본 §13 + peer §12 |

### §12.1 Phase 2 범위 확정

본 산출물이 **Phase 2 에서 완결** 하는 항목:
- Signature / Module / Optimizer 3계층 스펙
- V1/V2/V3 3단계 정본 비교표
- prompt_version_history 스키마
- rollback API 계약
- 3종 interface VERBATIM 매핑
- Phase 3 테스트 시나리오 정의

### §12.2 Phase 3 이월 항목

- DSPy 실구현 코드 (backend/vamos_core/mlops/dspy/)
- LM 백엔드 fallback 실측
- teleprompter 파라미터 baseline 튜닝
- V3 완전 자동화 (`auto_promote=True`)
- GPU 비용 벤치마크
- 임계값 3종 (MIN_TRAINSET_SIZE / MIN_VALSET_SIZE / max_rounds) baseline 확정

---

## §13 Phase 3 테스트 시나리오 (TS-DSPY-01 ~ TS-DSPY-12)

### TS-DSPY-01 — BootstrapFewShot 정상 경로 (positive)

- **주입**: trainset=80 (positive 60 + negative 20), valset=25, `kind=BOOTSTRAP_FEW_SHOT`, `max_bootstrapped_demos=4`
- **기대**: `CompiledProgram.delta > 0` (valset_score_after > before), `compile` 30초 이내 완료
- **검증**: `compiled_state_path` 파일 존재 + 읽기 가능, history append 1건

### TS-DSPY-02 — MIPROv2 정상 경로 (positive)

- **주입**: trainset=120, valset=30, `kind=MIPRO_V2`, `max_rounds=3`
- **기대**: `delta > 0`, 인스트럭션+few-shot 동시 최적화 완료
- **검증**: compiled instruction 에 2-4 Top10PatternCluster 대표 예시 포함 확인

### TS-DSPY-03 — COPRO cost-efficient 경로 (positive)

- **주입**: trainset=35, valset=20, `kind=COPRO`, `num_threads=1`
- **기대**: `delta > 0`, LM 호출 회수 MIPROv2 대비 30% 이하
- **검증**: 로그에 LM call count 집계 + cost 계산 정확

### TS-DSPY-04 — trainset 부족 reject (negative)

- **주입**: trainset=45 (< `min_trainset_size=50`)
- **기대**: `DSPY-001` emit, `compile` 호출 차단, history append 0건
- **검증**: `EscalationPayload.error_code == "DSPY-001"`, `retry_count=0` (즉시 종료)

### TS-DSPY-05 — valset_score 하락 reject (negative)

- **주입**: trainset 오염 (부정 예시가 positive 라벨) → compile 후 `delta=-0.031`
- **기대**: `DSPY-004` emit, §6.4 [6] 분기 reject
- **검증**: `PromptVersionRecord` append 없음, rollback 제안 로그 포함

### TS-DSPY-06 — LM 타임아웃 재시도 (recovery)

- **주입**: LM 백엔드 응답 지연 40s × 2회 → 3회차 정상 응답
- **기대**: `retry_count=2`, 최종 `CompiledProgram` 성공, `DSPY-007` warning 로그 2건
- **검증**: 지수 backoff 간격 (2s, 4s) 준수

### TS-DSPY-07 — qod_delta 부진 2스프린트 시 DSPy 보류 (gate)

- **주입**: `FeedbackSprint.qod_delta` 연속 2회 `< 0` (4주)
- **기대**: `compile` 자동 보류 + V1 fallback 권고 + `DSPY-001` 또는 `DSPY-004` 선제 경보
- **검증**: `applied_changes` 에 `"v1_manual_revert:qod_stagnation"` 자동 기록

### TS-DSPY-08 — A/B 패배 후 자동 archive (negative)

- **주입**: DSPy candidate + 현행 prompt A/B → `winner="a"`, `p_value=0.003`
- **기대**: `DSPY-005` emit, archive path 생성, history `status=DRAFT` 유지
- **검증**: production 프롬프트 UNCHANGED

### TS-DSPY-09 — human reject after A/B win (gate)

- **주입**: A/B `winner="b"` `p=0.02` → human 승인자 "reject (tone drift)"
- **기대**: `DSPY-006` emit, history append `status=DRAFT` + `approved_by=None`
- **검증**: 사유 로그 200자 이상 기록, 차기 라운드 trainset 힌트 기록

### TS-DSPY-10 — rollback 7일 이내 정상 (recovery)

- **주입**: `pv-core-sys-v3.2.1` promote 후 5일째 QoD 급락 → `rollback_to("pv-core-sys-v3.2.1", None)`
- **기대**: 새 엔트리 2건 append (current.status=ROLLED_BACK, target.status=PRODUCTION 복원)
- **검증**: `IPromptVersionRegistry.get_latest()` 반환값이 parent 와 일치

### TS-DSPY-11 — cross-reference 무결성 실패 (guard)

- **주입**: `DSPyModuleSpec.signature_id` 가 존재하지 않는 ID (`sig-ghost`)
- **기대**: Phase 3 validator 가 `DSPY-010` emit, 저장소 write 차단
- **검증**: history 파일 라인 수 불변

### TS-DSPY-12 — token limit 초과 (boundary)

- **주입**: compile 중 LM 응답이 `max_tokens=2048` 초과 truncate
- **기대**: `DSPY-008` emit, max_tokens 10% 축소 재시도 (1회)
- **검증**: 2차 재시도 성공 또는 `DSPY-007` fallback 전이

### §13.1 시나리오 커버리지 매트릭스

| 영역 | 시나리오 |
|------|----------|
| optimizer 3종 성공 | TS-DSPY-01 (Bootstrap) / TS-DSPY-02 (MIPROv2) / TS-DSPY-03 (COPRO) |
| trainset / valset 부족 | TS-DSPY-04 |
| compile 내부 실패 | TS-DSPY-05 (delta<0), TS-DSPY-11 (cross-ref) |
| LM 장애 / token | TS-DSPY-06 (timeout), TS-DSPY-12 (token limit) |
| gate 실패 | TS-DSPY-07 (feedback qod), TS-DSPY-08 (A/B 패배), TS-DSPY-09 (human reject) |
| 복구 | TS-DSPY-10 (rollback) |

**총 12건** (≥10건 요건 충족).

---

## §14 마감 체크리스트

- [x] §2 STEP7-F L1199~L1204 S7F-073 5 bullets verbatim 인용
- [x] §3~§7 DSPy Signature / Module / Optimizer / Loop / VersionRecord 4계층 완비
- [x] §8 3종 인터페이스 VERBATIM 정합 (`[INTERFACE_MISMATCH]` 0건)
- [x] §9 Pydantic v2 통합 선언
- [x] §10 ABC 2종 (`IDSPyOptimizer` / `IPromptVersionRegistry`)
- [x] §11 R-01-7 중첩 JSON 로깅 + error_code 정본 (DSPY-001~010)
- [x] §12 G2-1~G2-4 담당 항목 매핑
- [x] §13 Phase 3 시나리오 12건 (≥10건)
- [x] LOCK-ML-04 / 05 / 09 / 10 / 12 본 산출물 직접 강제 확인
- [x] peer `optimization_loop.md` 와 §3~§9 스키마 verbatim 참조 정합 (§8, §9 재인용 구조)
- [x] production 경로 미변경 (TEST_MODE=true, sandbox only)

---

**산출물 끝** — `dspy_optimization.md` (V2-Phase 2 / 2-6 주 폴더)
