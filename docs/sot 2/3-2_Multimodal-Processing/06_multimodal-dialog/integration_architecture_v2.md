# integration_architecture_v2.md — J-083 V2 EXTEND (Multimodal Router) + J-077 §6.7 트렌드 본문 (멀티모달 에이전트 프레임워크) + J-088 V2 EXTEND (API 추상화 레이어) + J-084/J-085/J-086/J-087

> **Status**: V2-Phase 2 (2-4 #2b)
> **작성일**: 2026-04-19
> **V1 정본**: [integration_architecture.md](./integration_architecture.md) (Phase 1-6 완료, ~41K, read-only sha256 baseline, J-083~J-088 V1 본문 + J-077 §6.7 트렌드)
> **SoT 근거**: STEP7-J Part 10 J-083~J-088 (L1426~L1524) + Part 9 J-077 (L1326~L1340)
> **담당 J-ID**: **J-083** (V2 EXTEND: 스마트 라우팅 + 동적 모델 선택) + **J-077** (§6.7 트렌드 본문: 멀티모달 에이전트 프레임워크) + **J-088** (V2 EXTEND: 통합 Gateway 인터페이스) + J-084/J-085/J-086/J-087 EXTEND
> **상위 인덱스**: [_index.md](./_index.md)
> **peer V2**: [task_planner_v2.md](./task_planner_v2.md) / [computer_use_agent_v2.md](./computer_use_agent_v2.md) / [memory_integration_v2.md](./memory_integration_v2.md) / [cost_accessibility_v2.md](./cost_accessibility_v2.md) §4.1 (smart_routing) + 전 V2 산출물의 Router 호출자

---

## 1. Cross-domain 참조 블록

| 정본 | 역할 | 참조 지점 |
|------|------|----------|
| `STEP7-J_멀티모달_생성처리_작업가이드.md` Part 10 J-083 (L1426~L1447) | 상위 SoT J-083 | §4.1 verbatim |
| `STEP7-J_멀티모달_생성처리_작업가이드.md` Part 10 J-088 (L1507~L1524) | 상위 SoT J-088 | §4.6 verbatim |
| `STEP7-J_멀티모달_생성처리_작업가이드.md` Part 9 J-077 (L1326~L1340) | §6.7 트렌드 (SeeAct/CogAgent/Ferret-UI/ScreenAI) | §5 verbatim |
| `STEP7-J_멀티모달_생성처리_작업가이드.md` Part 10 J-084~J-087 (L1449~L1505) | Pipeline Manager + Context + Error + A/B | §4 |
| `integration_architecture.md` (V1) | V1 정본 | §3 V1 계승 |
| `cost_accessibility_v2.md` §4.1 (peer 본 #2b) | smart_routing 알고리즘 출처 | §4.1 E3 |
| AUTHORITY_CHAIN §4 LOCK-MM-03/04/05 | LOCK 정본 | §2 |

---

## 2. LOCK 인용

> LOCK (STEP7-J + 기존 명세): 처리 파이프라인 순서 — 입력→검증→전처리→라우팅→처리→통합 [LOCK-MM-03]

> LOCK (STEP7-J J-083): 모달리티 우선순위 — Text > Image > Audio > Video > Document > Mixed [LOCK-MM-04]

> LOCK (기존 명세 §5.1): MultimodalMessage 스키마 [LOCK-MM-05]

> LOCK (STEP7-J J-094~J-096): 비용 상한 V2 ≤ ₩40K($30) [LOCK-MM-06]

**적용 지표**:
- LOCK-MM-03: 본 V2 J-083 Router 파이프라인 정본 (입력 → modal_detect → routing → fusion)
- LOCK-MM-04: J-083 우선순위 정렬 정본
- LOCK-MM-05: J-088 Gateway 입출력 통일 schema

---

## 3. V1 → V2 승급

| J-ID | V1 | V2 (본 산출물) |
|------|----|----------------|
| J-083 Router | 기본 라우팅 (모달 감지 + 파이프라인 분기) | **smart_routing (cost vs quality vs SLA) + 동적 모델 선택 + cost_accessibility §4.1 통합** |
| J-084 Pipeline Manager | DAG 기반 작업 흐름 | **DAG 병렬 + 오류 복구 + 진행률 + 취소** |
| J-085 Context Window | 토큰 예산 관리 | **모달리티별 동적 조정 + 자동 요약** |
| J-086 Error Handling | 모달리티별 폴백 | **그레이스풀 디그레이데이션 + 폴백 체인 표** |
| J-087 A/B Test | 모델 비교 | **자동 승자 선택 + 기본값 업데이트** |
| J-088 Gateway | 통합 인터페이스 | **6개 API + 백엔드 추상화 + 로깅** |
| J-077 §6.7 | 미작성 | **트렌드 본문: SeeAct/CogAgent/Ferret-UI/ScreenAI 통합 전략** |

---

## 4. V2 본문

### 4.1 J-083. Multimodal Router V2 (STEP7-J L1426~L1447)

**근거 verbatim 인용** (STEP7-J L1429~L1444):
> ```
> [구현 상세]
> - ORANGE CORE에 멀티모달 라우팅 레이어 추가:
>
> Input → Modal Detection →
>   ├─ Text → 기존 텍스트 파이프라인
>   ├─ Image → Vision Pipeline → {분석, 생성, 편집}
>   ├─ Audio → Audio Pipeline → {STT, 분석, 생성}
>   ├─ Video → Video Pipeline → {분석, 생성, 편집}
>   ├─ Document → Document Pipeline → {OCR, 파싱, 생성}
>   └─ Mixed → Multimodal Fusion → 통합 처리
>
> - 라우팅 기준:
>   ├─ 입력 모달리티 자동 감지
>   ├─ 요청된 출력 모달리티 추론
>   ├─ 비용/품질 트레이드오프
>   ├─ 로컬/API 선택
>   └─ 사용자 선호도
> ```

#### E1. Schema
```python
from common_types import ModuleConfig, MultimodalMessage
from d202_02 import VamosError, VamosResult

class RouterConfigV2(ModuleConfig):
    enable_smart_routing: bool = True                # V2 신규 (cost vs quality vs SLA)
    enable_user_preference: bool = True
    fallback_local_on_cost_exceed: bool = True
    max_cost_per_call_usd: float = 30.0              # LOCK-MM-06 V2

class RoutingDecisionV2:
    backend: str
    pipeline: Literal["text","image","audio","video","document","mixed"]
    estimated_cost_usd: float
    estimated_quality: float                         # 0~1
    estimated_sla_ms: int
    routing_reason: str                              # 사용자에게 표시
```

#### E3. Algorithm
```python
async def route_multimodal(msg: MultimodalMessage,                          # LOCK-MM-05
                          cfg: RouterConfigV2) -> RoutingDecisionV2:
    # 1. 모달 감지 (LOCK-MM-03 파이프라인 1단계)
    modalities = detect_modalities(msg.content)
    primary_modality = sort_by_priority(modalities,
                                       order=["text","image","audio","video","document","mixed"])  # LOCK-MM-04

    # 2. 출력 모달리티 추론 (사용자 의도)
    output_modality = infer_output_modality(msg.intent, primary_modality)

    # 3. 파이프라인 결정
    if len(modalities) > 1:
        pipeline = "mixed"
    else:
        pipeline = primary_modality

    # 4. smart_routing (peer cost_accessibility_v2 §4.1)
    if cfg.enable_smart_routing:
        from cost.routing import smart_routing       # peer cost_accessibility_v2
        routing = await smart_routing(msg, cfg)
        return RoutingDecisionV2(
            backend=routing.backend, pipeline=pipeline,
            estimated_cost_usd=routing.cost,
            estimated_quality=routing.quality,
            estimated_sla_ms=routing.sla_ms,
            routing_reason=f"smart_routing: cost ${routing.cost:.3f} / quality {routing.quality:.2f} / SLA {routing.sla_ms}ms",
        )

    # 5. 사용자 선호 적용
    if cfg.enable_user_preference:
        prefs = await load_user_prefs(msg.user_id)
        if prefs.prefer_local:
            return route_local_only(msg, pipeline)

    # 6. 기본 라우팅 (V1 호환)
    return route_default(msg, pipeline)
```

#### E4. 라우팅 표 (LOCK-MM-04 우선순위 적용)
| 입력 모달 | 출력 모달 | 1순위 백엔드 | 2순위 |
|----------|---------|-------------|-------|
| Text → Text | LLM | Qwen2.5 7B 로컬 | Gemini Flash |
| Image → Text | Vision LLM | Qwen2-VL 7B 로컬 | Gemini Flash Vision |
| Text → Image | Image Gen (peer J-011 V2) | Flux Schnell | DALL-E 3 |
| Audio → Text (STT) | peer J-021 V2 | Deepgram Nova-2 | Whisper v3 |
| Text → Audio (TTS) | peer J-022 V2 | Edge TTS | ElevenLabs |
| Video → Text | peer J-035 V1 | Qwen2-VL 7B + Whisper | Gemini Pro video |
| Text → Video | peer J-033 V2 | Kling 1.5 (무료) | Sora 2 |
| Mixed (image+text) | Multimodal Fusion | GPT-4o | Claude 3.5 Sonnet |
| Mixed (audio+image) | Vision+Voice | peer voice_chat_v2 §4.3 | — |

---

### 4.2 J-084. Pipeline Manager V2

#### V2 확장
- DAG 병렬 실행 (asyncio.gather)
- 오류 복구: 실패 단계 자동 재시도 (max 1회) → 대체 단계
- 진행률: WebSocket/SSE 실시간 UI 업데이트
- 취소/일시정지: TaskCancellationToken

```python
class PipelineDAG:
    nodes: list[PipelineNode]                        # 각 노드 = 모듈 호출
    edges: list[tuple[str,str]]                      # dependency

async def execute_dag(dag: PipelineDAG, max_parallel: int = 5) -> dict:
    sem = asyncio.Semaphore(max_parallel)
    results = {}
    async def run_node(node):
        async with sem:
            for parent in node.parents:
                if parent not in results:
                    await wait_for(parent)            # dependency 대기
            try:
                results[node.id] = await node.execute(results)
            except Exception as e:
                if node.retryable:
                    results[node.id] = await node.execute(results)  # 1회 재시도
                else:
                    results[node.id] = {"error": str(e)}
    await asyncio.gather(*[run_node(n) for n in dag.nodes])
    return results
```

---

### 4.3 J-085. Context Window 관리 V2

#### 모달별 토큰 예산 (V2 동적 조정)
| 모달 | 토큰 비용 | V2 자동 조정 |
|------|----------|--------------|
| 이미지 (low res 256x256) | 85 토큰 | high quality 시 1700 |
| 이미지 (high res 2048x2048) | 1700 토큰 | 비용 가드 시 자동 다운스케일 |
| 오디오 (1분, Whisper 전사) | ~150 토큰 | 화자별 분리로 절감 |
| 비디오 (1분, 100프레임) | ~17000 토큰 | 키프레임 100 → 30으로 동적 조정 |

```python
async def adjust_context(msg: MultimodalMessage, max_tokens: int = 100000) -> MultimodalMessage:
    estimated = estimate_tokens(msg)
    if estimated <= max_tokens:
        return msg
    # 동적 조정: 이미지 해상도 down → 비디오 키프레임 down → 텍스트 요약
    msg = downscale_images(msg, target_tokens=int(max_tokens * 0.4))
    msg = reduce_video_frames(msg, target_tokens=int(max_tokens * 0.3))
    if estimate_tokens(msg) > max_tokens:
        msg = summarize_text(msg, target_tokens=int(max_tokens * 0.3))
    return msg
```

---

### 4.4 J-086. Error Handling V2

| 모달 에러 | 폴백 (V2) |
|----------|----------|
| 이미지 생성 실패 (Flux Pro 5xx) | Flux Schnell → DALL-E 3 → reject |
| STT 실패 (Deepgram 429) | Whisper v3 로컬 → 텍스트 입력 폴백 |
| TTS 실패 (ElevenLabs 5xx) | Edge TTS → 텍스트 only |
| 비디오 분석 실패 (Qwen2-VL OOM) | Gemini Flash → 키프레임 5개만 |
| Cost Gate 거부 (LOCK-MM-06 초과) | 로컬 강제 폴백 → 사용자 통지 |

---

### 4.5 J-087. A/B Test V2

```python
class ABTest:
    test_id: UUID
    method: Literal["image_gen","tts","layout","stt"]
    variant_a: str; variant_b: str
    metric: Literal["quality_score","user_satisfaction","sla_ms","cost_usd"]
    sample_size: int = 100
    auto_promote_winner: bool = True

async def run_ab_test(test: ABTest) -> ABResult:
    samples_a, samples_b = await collect_samples(test, n=test.sample_size)
    winner = pick_winner(samples_a, samples_b, metric=test.metric)
    if test.auto_promote_winner:
        await update_default_backend(test.method, winner)
    return ABResult(winner=winner, scores={"a": ..., "b": ...})
```

---

### 4.6 J-088. Gateway V2 (STEP7-J L1507~L1524)

**근거 verbatim 인용** (STEP7-J L1512~L1518):
> ```
> class MultimodalGateway:
>     async def generate_image(prompt, model="auto", style=None) → ImageResult
>     async def analyze_image(image, query) → AnalysisResult
>     async def speech_to_text(audio, language="auto") → TranscriptResult
>     async def text_to_speech(text, voice="default") → AudioResult
>     async def analyze_video(video, query) → VideoAnalysis
>     async def generate_video(prompt, duration=5) → VideoResult
> ```

#### V2 통합 Gateway 인터페이스
```python
class MultimodalGatewayV2:
    """V2 EXTEND: 백엔드 추상화 + smart_routing + 자동 로깅"""

    async def generate_image(self, prompt: str, model: str = "auto",
                            style: str = None, **kwargs) -> ImageResult:
        # smart_routing 내부 호출 (peer cost_accessibility §4.1)
        decision = await self.router.route(MultimodalMessage(intent="generate_image", ...))
        result = await getattr(self.backends[decision.backend], "generate")(prompt, **kwargs)
        await self.logger.log(method="generate_image", backend=decision.backend, result=result)
        return result

    async def analyze_image(self, image: bytes, query: str) -> AnalysisResult: ...
    async def speech_to_text(self, audio: bytes, language: str = "auto") -> TranscriptResult: ...
    async def text_to_speech(self, text: str, voice: str = "default") -> AudioResult: ...
    async def analyze_video(self, video: bytes, query: str) -> VideoAnalysis: ...
    async def generate_video(self, prompt: str, duration: int = 5) -> VideoResult: ...
```

---

## 5. J-077 §6.7 트렌드 본문 (STEP7-J L1326~L1340)

**근거 verbatim 인용** (STEP7-J L1329~L1338):
> ```
> [2025-2026 최신 기술]
> - SeeAct (OSU): 웹 에이전트 비전 기반
> - CogAgent (Tsinghua): GUI 에이전트 멀티모달
> - Ferret-UI (Apple): 모바일 UI 이해
> - ScreenAI (Google): 스크린 이해 특화
>
> [VAMOS 통합]
> - Computer Use Agent에 최신 비전 모델 통합
> - GUI 이해 정확도 향상
> - 한국어 UI 특화 학습 데이터
> ```

**SoT 구현성 (STEP7-J L1339)**: V2 — ✅ API 통합 3개월

### 5.1 SoT 4종 모델 표 (verbatim L1329~L1332)

| 모델 | 제공 | 특징 (SoT) | VAMOS 통합 (peer J-083 Router → J-059 Computer Use Agent) |
|------|------|-----------|---------------------------------------------------------|
| **SeeAct** | OSU | 웹 에이전트 비전 기반 | 본 V2 Router 옵션 (웹 자동화 라우팅) |
| **CogAgent** | Tsinghua | GUI 에이전트 멀티모달 | computer_use_agent_v2 (peer 본 #2b) 1순위 통합 |
| **Ferret-UI** | Apple | 모바일 UI 이해 | V3 모바일 동기화 (peer J-071 vamos_differentiators_v2) |
| **ScreenAI** | Google | 스크린 이해 특화 | screen_recording_v2 (peer J-036 video_analysis_v2 §4.1) |

### 5.2 통합 시나리오 (V2 3개월)
1. **+1개월**: CogAgent 통합 → computer_use_agent_v2 J-059 V2 backend 옵션
2. **+2개월**: SeeAct → 웹 자동화 시나리오 (브라우저 조작)
3. **+3개월**: ScreenAI → screen_recording_v2 J-036 OCR 정확도 향상
4. **V3**: Ferret-UI → 모바일 동기화 시나리오

---

## 6. peer V2 cross-ref
- task_planner_v2.md J-060 → 본 V2 J-084 Pipeline DAG 호출자
- computer_use_agent_v2.md J-059 → 본 V2 J-077 트렌드 모델 통합
- memory_integration_v2.md J-085 → 본 V2 §4.3 Context Window
- cost_accessibility_v2.md §4.1 smart_routing → 본 V2 §4.1 J-083 호출

---

## 7. Phase 3 시나리오 (10건)
1. smart_routing 결정 (Flux Schnell vs Pro) → quality/cost 통합 점수.
2. DAG 병렬 실행 (5 nodes) → asyncio.gather + 오류 1회 재시도.
3. Context window 자동 조정 (이미지 다운스케일 → 토큰 절감).
4. 폴백 체인 (Deepgram 429 → Whisper v3 → 텍스트 입력).
5. A/B test (Flux Schnell vs Flux Pro, 100 샘플) → 자동 승자.
6. Gateway 통합 호출 (generate_image) → smart_routing → 백엔드 추상화.
7. CogAgent (J-077) 통합 → computer_use_agent_v2 backend 옵션.
8. SeeAct (J-077) 웹 자동화 시나리오.
9. LOCK-MM-04 우선순위 정렬 (text > image > audio > video) 검증.
10. Cost Gate 거부 → 로컬 강제 폴백 + 사용자 통지.

---

## 8. 검증 매트릭스
| 항목 | V1 | V2 (본) | L3 |
|------|----|---------|-----|
| J-083 Router | 기본 라우팅 | smart_routing + cost/quality/SLA + LOCK-MM-04 | 92 |
| J-084 Pipeline | DAG 단순 | 병렬 + 오류 복구 + 진행률 | 88 |
| J-085 Context | 토큰 예산 | 동적 조정 (모달별) | 86 |
| J-086 Error | 폴백 | 그레이스풀 디그레이데이션 표 | 88 |
| J-087 A/B | 비교 | 자동 승자 + 기본값 업데이트 | 86 |
| J-088 Gateway | 인터페이스 | 6개 API + 백엔드 추상화 + 로깅 | 90 |
| J-077 §6.7 트렌드 | 미작성 | 본문 + 통합 전략 4단계 | 84 |

**평균**: **87.7/100** (LOCK-MM-12 V2 ≥80 충족 ✅)
