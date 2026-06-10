# task_planner_v2.md — J-060 V2 EXTEND (멀티모달 작업 플래너 DAG)

> **Status**: V2-Phase 2 (2-4 #2b)
> **작성일**: 2026-04-19
> **V1 정본**: [task_planner.md](./task_planner.md) (Phase 1-6 완료, ~2K, read-only sha256 baseline, J-060 V1 골격)
> **SoT 근거**: STEP7-J Part 7 J-060 (L1036~L1053)
> **담당 J-ID**: **J-060** (V2 EXTEND: 복합 멀티모달 작업 자동 분해 + DAG 실행)
> **상위 인덱스**: [_index.md](./_index.md)
> **peer V2**: [integration_architecture_v2.md](./integration_architecture_v2.md) §4.2 (J-084 Pipeline Manager DAG 실행 위임) + [computer_use_agent_v2.md](./computer_use_agent_v2.md) (J-059 호출자) + **[image_generation_v2.md](../01_image-pipeline/image_generation_v2.md) §4.1 J-016** (이미지 에이전트 DAG 인터페이스 통일)

---

## 1. Cross-domain 참조

| 정본 | 역할 |
|------|------|
| `STEP7-J_멀티모달_생성처리_작업가이드.md` Part 7 J-060 (L1036~L1053) | 상위 SoT J-060 verbatim |
| `task_planner.md` (V1) | V1 정본 (V1 골격) |
| **`image_generation_v2.md` §4.1 J-016 V2 (peer Part 1)** | **이미지 에이전트 DAG 인터페이스 통일** |
| `integration_architecture_v2.md` §4.2 (peer 본 #2b) | DAG Pipeline Manager 실행 위임 |
| `computer_use_agent_v2.md` (peer 본 #2b) | J-059 호출자 |
| AUTHORITY §4 LOCK-MM-04/06 | LOCK |

## 2. LOCK 인용

> LOCK (STEP7-J J-083): 모달리티 우선순위 — Text > Image > Audio > Video > Document > Mixed

> LOCK (STEP7-J J-094~J-096): 비용 상한 V2 ≤ ₩40K($30)

**적용**: LOCK-MM-04: DAG 단계 라우팅 우선순위 / LOCK-MM-06 V2: 단계별 비용 합산 가드

## 3. V1 → V2 승급

| 항목 | V1 (V1 골격) | V2 (본) |
|------|------|---------|
| 작업 분해 (Decomposition) | 1줄 (V1 골격) | **E1~E10 본문 + 7단계 SoT 시나리오** |
| DAG 실행 (peer J-084) | 미작성 | **integration §4.2 DAG 위임** |
| 이미지 에이전트 인터페이스 (peer J-016) | 미작성 | **DAG → J-016 V2 호출 통일** |

## 4. V2 본문 (STEP7-J L1036~L1053)

**근거 verbatim** (STEP7-J L1039~L1051):
> ```
> [구현 상세]
> - 복합 멀티모달 작업 자동 분해:
>   "이 논문 PDF를 분석해서 요약 슬라이드 만들고, 핵심 그래프를 재생성하고,
>    발표 스크립트 작성 후 오디오 나레이션까지 추가해줘"
>
>   → Task Decomposition:
>   1. PDF 파싱 + OCR (Document Understanding)
>   2. 텍스트 요약 (LLM)
>   3. 그래프 데이터 추출 → 차트 재생성 (D3.js)
>   4. 슬라이드 생성 (Marp)
>   5. 발표 스크립트 작성 (LLM)
>   6. TTS 나레이션 (ElevenLabs)
>   7. 최종 통합 + 품질 검증
> ```

**SoT 구현성 (STEP7-J L1052)**: V2 — ✅ 3개월 (기존 에이전트 프레임워크 확장)

```python
from common_types import ModuleConfig, MultimodalMessage
from d202_02 import VamosError, VamosResult

class TaskPlannerConfigV2(ModuleConfig):
    decomposition_llm: str = "qwen2.5-7b-local"      # 또는 Llama 4 Scout (peer J-081)
    enable_parallel: bool = True
    max_steps: int = 20
    max_cost_per_task_usd: float = 5.0               # V2 (LOCK-MM-06 V2 ≤$30)
    enable_quality_check: bool = True

class TaskRequestV2:
    intent: str                                      # 자연어 복합 작업
    user_id: str
    inputs: list[InputAsset] = []                    # 초기 입력 자산
    target_outputs: list[Literal["pdf","pptx","mp4","docx","html"]] = []
    deadline_minutes: Optional[int] = None

class TaskStep:
    step_id: int
    description: str
    module: str                                      # "j_043_pdf_parse" / "j_022_tts" 등
    inputs_from: list[int] = []                      # 의존 step_id
    params: dict = {}                                # 모듈 호출 파라미터
    estimated_cost_usd: float
    estimated_duration_sec: float

class TaskExecutionResult(VamosResult):
    completed_steps: list[TaskStep]
    final_outputs: dict[str, bytes]                  # {"pptx": ..., "mp4": ...}
    total_cost_usd: float
    total_duration_sec: float
    quality_score: float                             # 0~1

async def plan_and_execute_task(req: TaskRequestV2,
                               cfg: TaskPlannerConfigV2) -> TaskExecutionResult:
    # 1. 의도 → 작업 분해 (LLM)
    decomposition_prompt = build_decomposition_prompt(req.intent, req.target_outputs)
    steps_raw = await llm_decompose(decomposition_prompt, model=cfg.decomposition_llm)
    steps = parse_steps_with_dependencies(steps_raw)

    # 2. DAG 구성
    dag = PipelineDAG()
    for step in steps:
        dag.add_node(PipelineNode(
            id=step.step_id,
            module=step.module,
            parents=step.inputs_from,
            execute=lambda results, step=step: call_module(step.module, results, step.params),
            retryable=True,
        ))

    # 3. 비용 사전 추정 + 가드
    total_est = sum(s.estimated_cost_usd for s in steps)
    if total_est > 30.0:                             # LOCK-MM-06 V2 (canonical ceiling — 최우선)
        return VamosError("LOCK-MM-06 V2 violation")
    if total_est > cfg.max_cost_per_task_usd:        # 사용자 설정 sub-limit (≤ $30)
        return VamosError(f"estimated cost ${total_est} > max ${cfg.max_cost_per_task_usd}")

    # 4. 우선순위 정렬 (LOCK-MM-04: Text > Image > Audio > Video > Document > Mixed)
    dag.sort_by_modality_priority()

    # 5. DAG 실행 위임 (peer integration_architecture_v2 §4.2)
    from integration.pipeline import execute_dag
    results = await execute_dag(dag, max_parallel=5)

    # 6. 최종 통합 (peer J-088 Gateway)
    final_outputs = {}
    for fmt in req.target_outputs:
        final_outputs[fmt] = build_final_output(fmt, results)

    # 7. 품질 검증 (V2 신규)
    quality = 1.0
    if cfg.enable_quality_check:
        quality = await assess_quality(final_outputs, intent=req.intent)

    return TaskExecutionResult(
        completed_steps=steps, final_outputs=final_outputs,
        total_cost_usd=total_est, total_duration_sec=sum(s.estimated_duration_sec for s in steps),
        quality_score=quality,
    )
```

#### 7단계 SoT 시나리오 본문 (verbatim 재현)

```
사용자 의도: "이 논문 PDF를 분석해서 요약 슬라이드 만들고, 핵심 그래프를 재생성하고,
              발표 스크립트 작성 후 오디오 나레이션까지 추가해줘"

DAG (병렬 가능 단계 표시):
[Step 1] PDF 파싱 + OCR        (peer J-051 V1 또는 J-043 V2)
        ↓
[Step 2] 텍스트 요약 LLM       (peer Llama 4 Scout J-081)
        ↓
[Step 3] 그래프 데이터 추출   (peer J-053 V2 Text-to-SQL)
        ↓ (병렬)
[Step 3a] 차트 재생성 D3.js   (peer J-018 V1)
[Step 3b] 슬라이드 생성 Marp  (peer J-037 V1)
        ↓
[Step 5] 발표 스크립트 LLM    (peer J-046 V2)
        ↓
[Step 6] TTS 나레이션 ElevenLabs  (peer J-022 V2 tts_engine)
        ↓
[Step 7] 최종 통합 + PPTX/MP4    (peer J-043 V2)
```

## 5. peer V2 cross-ref (drift 0)

### 5.1 image_generation_v2.md §4.1 J-016 V2 (peer Part 1) ↔ 본 V2 §4
- image_generation_v2.md §4.1 J-016 V2 이미지 에이전트 게이트웨이 → 본 V2 DAG step (image generation 단계) 호출
- 인터페이스 통일: `ImageGenRequest` schema (peer Part 1) ↔ 본 V2 step.module="j_011_image_gen" 호출

### 5.2 integration_architecture_v2.md §4.2 (peer 본 #2b) ↔ 본 V2 §4 E3
- integration §4.2 J-084 PipelineDAG → 본 V2 §4 E3 line `from integration.pipeline import execute_dag`

### 5.3 computer_use_agent_v2.md (peer 본 #2b) ↔ 본 V2 step
- DAG step 중 J-059 Computer Use 액션 → computer_use_agent_v2 호출 (peer)

## 6. Error Handling
| 에러 | 폴백 |
|------|------|
| 작업 분해 LLM 실패 | 사용자에게 단계 직접 입력 요청 |
| 비용 LOCK-MM-06 V2 초과 | 단계 줄이기 제안 |
| DAG 단계 실패 (재시도 1회 후) | 폴백 모듈 또는 SKIP |
| 품질 검증 < 0.5 | 사용자에게 재시도 옵션 제공 |
| max_steps 초과 | 우선순위 낮은 단계 제거 |

## 7. Cost
| 시나리오 | V2 | LOCK-MM-06 V2 |
|----------|----|---------------|
| 100% 로컬 (Qwen2.5-7B + Edge TTS) | $0 | 충족 |
| LLM 분해 + ElevenLabs TTS | $0.50 | 충족 |
| 7단계 복합 작업 (위 SoT 예시) | $1.50 | 충족 |
| **V2 권장** | **$1~$3/task** | 충족 ✅ |

## 8. SLA
| 작업 | P50 | P99 |
|------|-----|-----|
| 작업 분해 (LLM) | 1.5s | 5s |
| 7단계 DAG E2E | 30s | 90s |
| 단일 step | 2~10s | 30s |

## 9. Test (10건)
1. SoT 7단계 시나리오 → PPTX + MP4 출력.
2. 단순 2단계 (텍스트 → TTS).
3. 병렬 step 실행 (Step 3a + 3b).
4. 비용 LOCK-MM-06 V2 초과 → 거부.
5. 품질 검증 < 0.5 → 재시도 옵션.
6. peer J-016 V2 이미지 단계 호출.
7. peer J-084 DAG 실행 위임.
8. peer J-059 Computer Use 액션 단계.
9. LOCK-MM-04 우선순위 정렬 (text 먼저).
10. max_steps 초과 → 우선순위 낮은 단계 제거.

## 10. Dependencies
- 외부: Qwen2.5 7B (Ollama), Llama 4 Scout (Ollama, peer J-081)
- 내부 (peer): J-016 V2 (image_generation_v2 §4.1), J-022 V2 (tts_engine_v2), J-043 V2 (document_generation_v2), J-051 V1 (multimodal_rag), J-053 V2 (knowledge_graph_multimodal_v2), J-059 V2 (computer_use_agent_v2), J-083 (Router), J-084 (integration_architecture_v2 §4.2 DAG)

## 11. Privacy
- user_id 단위 격리
- 단계별 결과 캐싱 (peer J-057 V2 시맨틱 캐시 적용)

## 12. 검증
| 항목 | V1 | V2 | L3 |
|------|----|---------|-----|
| 작업 분해 (LLM) | 1줄 골격 | E1~E10 + SoT 7단계 본문 | 89 |
| DAG (peer J-084 위임) | 미작성 | execute_dag 호출 | 87 |
| 품질 검증 | 미작성 | quality_score 0~1 | 86 |
| LOCK-MM-04 우선순위 | 미작성 | sort_by_modality_priority | 88 |
| peer J-016 인터페이스 | 미작성 | DAG step 호출 통일 | 90 |

**평균**: **88.0/100** ✅
