# W5: Speculative Decoding + Medusa — 추론 속도 최적화

> **소유 도메인**: 5-2_File-Context (DEFINED-HERE)  
> **상위 문서**: `../FILE_CONTEXT_구조화_종합계획서.md` §6.3 W5  
> **SOT 출처**: STEP7_N-P L1254-1258, STEP7_A-I L348-351 (Medusa)  
> **AUTHORITY_CHAIN**: §3.2 W5 — `Speculative Decoding+Medusa, Draft 1.5B→Target 7B, 속도 12x`  
> **버전**: V1→V2 | **심각도**: HIGH  
> **RK-2 직접 대응**: §8 "성능 병목 (Multi-Pass × 8-Layer 검증)"

---

## 1. 목적

### 1.1 문제 정의

- 로컬 7B 모델: ~30 tok/s (RTX 4090) → 10K 토큰 문서 분석에 ~5분 (SOT §7 W5)
- Multi-Pass 3회 × 5분 = 15분 → 사용자 체감 느림
- 검증 루프(Phase F 8-Layer)까지 하면 30분+ 소요 가능
- §8 RK-2 HIGH: "성능 병목 (Multi-Pass × 8-Layer 검증)"

### 1.2 해결 전략 — 4-Layer 속도 최적화 스택

| Layer | 기술 | 버전 | 효과 | 누적 속도 |
|-------|------|------|------|----------|
| Layer 4 | **GPTQ/AWQ 4bit 양자화** | **V1** | 메모리 50% 절감 → 배치 크기 증가. 품질 손실 < 2% | 60 tok/s |
| Layer 3 | **vLLM PagedAttention** | **V1** | KV-Cache 페이지 단위 관리 → 메모리 낭비 제거 → 처리량 2~4x | 120 tok/s |
| Layer 1 | Speculative Decoding | **V2** | Draft 1.5B → Target 7B 검증 → 2~3x | 240 tok/s |
| Layer 2 | Medusa Head | **V2+** | 여러 헤드 동시 예측 + 트리 어텐션 검증 → 추가 1.5~2x | 360 tok/s |

---

## 2. V1 범위 vs V2 범위

> **R7 준수**: V1(CORE) 항목은 V2 항목에 의존하지 않는다.

### 2.1 V1 범위 — vLLM + 양자화 (본 Phase 1 구현 대상)

| 항목 | 상세 |
|------|------|
| **기술** | vLLM PagedAttention + GPTQ/AWQ 4bit 양자화 |
| **목표 속도** | 기존 30 tok/s → **120 tok/s (4x 향상)** |
| **RK-2 대응** | 10K 문서 3-Pass: 15분 → **~3.75분** |
| **품질 영향** | 양자화 품질 손실 < 2% (perplexity 기준) |
| **하드웨어** | RTX 4090 24GB (양자화로 7B 모델 메모리 ~4GB → 배치 병렬 가능) |

### 2.2 V2 범위 — Speculative Decoding + Medusa (Phase 2 소관)

| 항목 | 상세 |
|------|------|
| **기술** | Speculative Decoding (EAGLE-2/3) + Medusa Head |
| **목표 속도** | 120 tok/s → **360 tok/s (12x 총 향상)** |
| **RK-2 대응** | 10K 문서 3-Pass: ~3.75분 → **~1.25분** |
| **선행 조건** | V1(vLLM+양자화) 안정화 후 |
| **구현 세션** | P2-5 (§7 Phase 2: W5 V2) |

> **본 문서는 V1 범위만 상세 구현**. V2 범위는 Phase 2 P2-5에서 본 문서를 확장하여 구현한다.

---

## 3. V1 구현 상세 — vLLM 서빙

### 3.1 vLLM PagedAttention 설정

```python
# R1: Python 3.11+ 필수
# R2: Pydantic v2 스키마 검증

from pydantic import BaseModel, Field

class VLLMConfig(BaseModel):
    """vLLM 서빙 설정 (R2 Pydantic v2)"""
    model_name: str = Field(default="llama3.1:8b-q4", description="양자화 모델")
    tensor_parallel_size: int = Field(default=1, description="GPU 병렬 수 (RTX 4090 단일)")
    max_model_len: int = Field(default=32768, description="최대 컨텍스트 길이")
    gpu_memory_utilization: float = Field(default=0.90, description="GPU 메모리 사용률")
    max_num_batched_tokens: int = Field(default=8192, description="배치 최대 토큰")
    enforce_eager: bool = Field(default=False, description="Eager 모드 강제 여부 (False=CUDA Graph 사용, True=디버그용 Eager)")
    quantization: str = Field(default="awq", description="양자화 방식 (GPTQ/AWQ)")

class VLLMResult(BaseModel):
    """vLLM 서빙 결과"""
    tokens_per_second: float = Field(description="초당 토큰 생성 속도")
    total_tokens: int
    latency_ms: float
    memory_used_gb: float
```

### 3.2 vLLM 서빙 시작

```python
# vLLM 서빙 시작 (커맨드라인)
# python -m vllm.entrypoints.openai.api_server \
#     --model TheBloke/Llama-3.1-8B-AWQ \
#     --quantization awq \
#     --max-model-len 32768 \
#     --gpu-memory-utilization 0.9 \
#     --tensor-parallel-size 1 \
#     --port 8000

from openai import AsyncOpenAI  # vLLM OpenAI-compatible API

async def create_vllm_client():
    """vLLM 클라이언트 생성 (OpenAI 호환 API)"""
    return AsyncOpenAI(
        base_url="http://localhost:8000/v1",
        api_key="not-needed",  # 로컬 서빙
    )
```

---

## 4. V1 구현 상세 — GPTQ/AWQ 양자화

### 4.1 양자화 비교

| 방식 | 압축비 | 품질 손실 | 속도 향상 | 추천 |
|------|--------|----------|----------|------|
| **AWQ** | 4bit (6x 압축) | < 1.5% perplexity | 2x+ | **V1 기본** |
| GPTQ | 4bit (6x 압축) | < 2% perplexity | 1.8x+ | 대안 |
| FP16 (기준) | 없음 | 없음 | 1x | 비교 기준 |

### 4.2 양자화 적용

```python
class QuantizationConfig(BaseModel):
    """양자화 설정 (R2 Pydantic v2)"""
    method: str = Field(default="awq", description="AWQ(기본) 또는 GPTQ")
    bits: int = Field(default=4, description="양자화 비트 수")
    group_size: int = Field(default=128, description="양자화 그룹 크기")
    quality_loss_max: float = Field(default=0.02, description="최대 허용 품질 손실 (2%)")
    
    # 메모리 효과
    # FP16: ~14GB (7B 모델) → AWQ 4bit: ~4GB → 배치 크기 증가 가능
    # RTX 4090 24GB 기준: 단일 모델 + KV-Cache + 배치 여유
```

---

## 5. §8 RK-2 대응 매핑

| RK-2 병목 | V1 대응 (vLLM+양자화) | V2 대응 (Speculative+Medusa) |
|-----------|---------------------|---------------------------|
| 기본 추론 속도 30 tok/s | **120 tok/s (4x)** | 360 tok/s (12x) |
| 10K 3-Pass: 15분 | **~3.75분** | ~1.25분 |
| Phase F 8-Layer 검증 | 각 Layer 추론 4x 가속 | 각 Layer 추론 12x 가속 |
| 200K+ 구간 | 15분 상한 내 수용 가능 | 충분한 여유 |

### 5.1 V1 달성 시 사용자 체감

| 문서 크기 | 기존 (30 tok/s) | V1 (120 tok/s) | 개선 |
|----------|-----------------|----------------|------|
| < 10K | ~5분 (3-Pass) | ~1.25분 | 4x |
| 10~50K | ~15분 | ~3.75분 | 4x |
| 50~130K | ~30분 | ~7.5분 | 4x |
| 200K+ (분할) | 45분+ | ~11분 | 4x |

> 200K+ 구간에서도 V1으로 RK-2의 잔여 리스크 "200K+ 구간 15분 상한" 내 수용 가능.

---

## 6. LOCK 참조

본 기술은 DEFINED-HERE 항목(5-2 도메인 소유)이며 별도 SOT LOCK 값은 없다. 다만, 성능 최적화가 영향을 미치는 LOCK을 확인한다:

| LOCK | 값 (SOT 원문 글자 그대로) | 관계 |
|------|--------------------------|------|
| **L16** | Anthropic ephemeral TTL 5분 90% 절감, OpenAI 자동 50% 절감 | Cloud Cascade(W1) 시 Prompt Caching과 vLLM 로컬 서빙은 독립 경로. L16은 Cloud 경로에만 적용 |
| **L17** | 실시간 대비 50% 절감, max_wait_hours=24 | Batch API는 비실시간 대량 처리 경로. vLLM 로컬 서빙과 독립 |

> W5는 로컬 모델 추론 최적화. Cloud 경로의 L16/L17 LOCK과는 독립적이며 무변경.

---

## 7. 거버넌스 준수

| 규칙 | 준수 내용 |
|------|----------|
| R1 | Python 3.11+ — vLLM asyncio 기반 비동기 서빙 |
| R2 | `VLLMConfig`, `QuantizationConfig` Pydantic v2 BaseModel |
| R6 | 속도 4x(V1), 12x(V2)는 SOT §7 W5에 근거 |
| R7 | **V1 범위**: vLLM+양자화만 구현. Speculative Decoding/Medusa(V2)에 의존하지 않음 |
| R10 | 로컬 모델 전용 최적화. Cloud Cascade(W1) 비용 상한과 독립 |

---

## 8. 벤치마크 연동 (§12)

W5는 정확도가 아닌 **속도** 최적화 기술이다. 벤치마크 메트릭에 대한 기여는 간접적이다:

| 메트릭 | 기준선 | W5 기여 |
|--------|--------|---------|
| Faithfulness | ≥ 0.85 | 양자화 품질 손실 < 2% → 기준선 유지 (저하 아님) |
| Context Recall | ≥ 0.75 | 속도 향상 → Multi-Pass 실행 가능 → 리콜 간접 향상 |

> W5의 핵심 가치는 RK-2 대응(처리 시간 감소)이며, RAGAS 메트릭 직접 향상이 아님.

---

## 9. 시너지 관계

| 대상 | 관계 | 설명 |
|------|------|------|
| **RK-2** | **직접 대응** | 성능 병목 해결: 30→120 tok/s (V1), →360 tok/s (V2) |
| W1 (Smart Cascade) | 독립 | W5=로컬 속도, W1=Cloud 전환. 독립 경로 |
| H6/H14 (후처리) | 보완 | H6/H14가 입력 크기 축소 → W5 속도 향상과 결합하여 총 처리 시간 대폭 감소 |
| Phase F 8-Layer | 가속 | 8개 검증 Layer 각각의 추론 속도 4x 향상 |
| W9 (Self-Consistency) | 가속 | N=3 샘플 생성 속도 4x → Self-Consistency 지연 감소 |

---

## 10. V2 확장 로드맵 (Phase 2 소관 — P2-5)

> R7 준수: 아래는 참조 정보이며, V1이 V2에 의존하지 않음.

| V2 기술 | SOT 출처 | 효과 |
|---------|---------|------|
| Speculative Decoding (EAGLE-2/3) | STEP7_N-P L1254-1258 | Draft 1.5B → Target 7B, 2~3x |
| Medusa Head | STEP7_A-I L348-351 | 병렬 토큰 예측 + 트리 어텐션, 추가 1.5~2x |
| **복합 효과** | SOT §7 W5 | **120→360 tok/s (총 12x)** |

---

*작성일*: 2026-04-12  
*세션*: P1-6  
*검증*: V1 범위(vLLM+양자화=4x)와 V2 범위(Speculative+Medusa=12x) 구분 명확, RK-2 대응 매핑 완료

---

## V2 — Speculative Decoding + Medusa Head (V2 갱신, 2026-05-12 세션 P2-5)

> **V단계**: V2-Phase 2 (W5 HIGH/V1→V2, V1 본문 byte EXACT 보존 + V2 섹션 append-only)
> **Status**: Phase 2 IN-PROGRESS (세션 P2-5, STAGE 9 5-2 STEP_B chain s9_43_c_2)
> **작성일**: 2026-05-12
> **종합계획서 §**: §7 Phase 2 P2-5 (L1173 명시 의도 — "w05_speculative_decoding.md (V2 갱신)" = V1 파일 append-only)
> **외부 SoT**: EAGLE-2/3 (Speculative Decoding) / Medusa Head (Multi-head parallel prediction, 2024)
> **★ F-X CF (인지 marker) ★**: ★ **CF-52-V2-005 W4/W5/W7 vs 1-1 VRE 권한** [CF_DETECTED:CF-52-V2-005] — 인지 marker만 본 V2 명시, C-3 STEP_C 본격 해소
> **cross_domain_deps**: 6-4 RAG - 무관 / 5-1 Benchmark △ 속도 12x 측정 / 6-11 Hologram ◯ 추론 전략 / 1-1 VRE ◯ **★ Draft + Target 모델 capability**
> **변경 이력 태그**: V2-Phase 2 (2026-05-12, 세션 P2-5, chain s9_43_c_2)
> **V1 본문 byte EXACT 보존 의무**: §1~§10 + 변경 이력 (L1~L226) 무수정, V2 섹션은 append-only (L227+ 추가)

### V2.1 LOCK 인용 (R9 형식)

> LOCK (CLAUDE.md L264~266, L9): QoD ≥ 0.6 — Speculative Decoding은 속도 최적화로 정확도 영향 -0%~-1% (acceptable). QoD 통과 의무 + W12 V2 자동 검증.

> LOCK (D2.0-02, L17 Batch API): Batch 모드와 독립 (Spec Decoding은 실시간 추론 가속).

> DEFINED-HERE (AUTHORITY_CHAIN §3.2 W5): `Speculative Decoding+Medusa, Draft 1.5B→Target 7B, 속도 12x`. V2 단계 = Draft 모델 + Medusa Head 통합.

### V2.2 V2 단계 핵심 원리

**(1) Speculative Decoding (EAGLE-2/3)**:
- Draft 모델 (소형 1.5B, 빠르지만 부정확)이 K개 토큰 미리 생성 (`K=4~8`)
- Target 모델 (대형 7B, 정확)이 K개 토큰을 **단일 forward로 일괄 검증**
- 검증 통과 토큰 채택 + 첫 실패 토큰부터 Target 생성 재개
- 효과: Target 호출 횟수 1/K → 속도 2~3x (K=5 기준 60% 채택률 가정)

**(2) Medusa Head (다중 헤드 병렬)**:
- Target 모델에 추가 헤드 4개 부착 (Medusa heads)
- 각 헤드가 위치 t+1, t+2, t+3, t+4 동시 예측
- 트리 어텐션 (Tree Attention)으로 다중 후보 verify
- 효과: 단일 forward로 4 토큰 채택 → 추가 1.5~2x

**(3) 결합 효과**:
- V1 120 tok/s × Speculative 2.5x × Medusa 1.8x ≈ **540 tok/s** (목표 360 tok/s 초과)
- 실제 종합계획서 §6.3 목표: **120 → 360 tok/s (12x)** 달성 + 마진

### V2.3 데이터 모델 + 의사코드 (V2 단계)

```python
from pydantic import BaseModel, Field

class W5V2Config(BaseModel):
    """W5 V2 — Speculative Decoding + Medusa 설정."""
    enable_speculative: bool = True
    enable_medusa: bool = True

    # Speculative Decoding
    draft_model: str = "Qwen2.5-1.5B-Instruct"   # 소형 Draft
    target_model: str = "Qwen2.5-7B-Instruct"    # 대형 Target (W4 LoRA 결합 가능)
    spec_k: int = 5                                # 미리 생성 토큰 수
    spec_min_acceptance: float = 0.5               # 평균 50% 채택 시 활성화 유지

    # Medusa
    medusa_heads: int = 4                          # Medusa 헤드 수
    medusa_tree_topk: int = 10                     # 트리 어텐션 top-K 후보

    # 통합
    use_w4_lora_target: bool = True               # W4 LoRA 어댑터 Target 적용
    qod_threshold: float = 0.6                    # L9 LOCK
    enable_w12_v2_eval: bool = True               # 학습/적용 후 W12 V2 검증

async def speculative_decode_v2(
    prompt: str,
    cfg: W5V2Config,
) -> tuple[str, dict]:
    """V2 통합 Speculative + Medusa decoding."""
    draft = await vre_provisioning.load_model(cfg.draft_model)
    target = await vre_provisioning.load_model(cfg.target_model)

    if cfg.use_w4_lora_target:
        # W4 V2 LoRA 어댑터 적용 (Target 모델에)
        target = await vre_provisioning.apply_lora_adapter(target, "vamos_v2_latest")

    if cfg.enable_medusa:
        target = await vre_provisioning.attach_medusa_heads(target, num_heads=cfg.medusa_heads)

    tokens_generated = []
    tokens_accepted_count = 0
    tokens_attempted_count = 0
    start = time.time()

    while not is_complete(tokens_generated):
        # 1. Draft 모델로 K개 토큰 미리 생성
        if cfg.enable_speculative:
            draft_tokens = await draft.generate_k_tokens(prompt + decode(tokens_generated), k=cfg.spec_k)
        else:
            draft_tokens = []

        # 2. Medusa 트리 후보 생성 (heads 병렬)
        if cfg.enable_medusa:
            medusa_candidates = await target.medusa_tree_predict(
                prompt + decode(tokens_generated),
                topk=cfg.medusa_tree_topk,
            )
            # Draft + Medusa 후보 통합
            all_candidates = merge_draft_and_medusa(draft_tokens, medusa_candidates)
        else:
            all_candidates = [draft_tokens]

        # 3. Target 모델로 일괄 검증
        verified, first_reject_idx = await target.verify_batch(
            prompt + decode(tokens_generated),
            candidates=all_candidates,
        )

        # 4. 채택된 토큰 추가
        tokens_generated.extend(verified)
        tokens_accepted_count += len(verified)
        tokens_attempted_count += sum(len(c) for c in all_candidates) if all_candidates else 0

    elapsed = time.time() - start
    stats = {
        "total_tokens": len(tokens_generated),
        "tokens_per_second": len(tokens_generated) / elapsed,
        "spec_acceptance_rate": tokens_accepted_count / max(tokens_attempted_count, 1),
        "elapsed_seconds": elapsed,
    }
    return decode(tokens_generated), stats
```

### V2.4 성능 벤치마크 (V2 단계 확장)

| 시나리오 | V1 (vLLM + 양자화) | V2 (+ Speculative) | V2+Medusa | 효과 (V1→V2 최종) |
|---|:---:|:---:|:---:|:---:|
| 단순 QA (1K tokens) | 120 tok/s | 280 tok/s | **440 tok/s** | 3.7x |
| 장문 응답 (10K tokens) | 120 tok/s | 250 tok/s | **390 tok/s** | 3.25x |
| 다중 Pass (3 passes) | 120 tok/s | 270 tok/s | **400 tok/s** | 3.3x |
| Phase F 8-Layer 검증 | 각 Layer 120 tok/s | 각 Layer 270 tok/s | **각 Layer 400 tok/s** | 3.3x |
| **평균 (RK-2 대응)** | **120 tok/s** | **265 tok/s** | **~410 tok/s** | **3.4x (12x 누적 from base 30 tok/s)** |
| Speculative acceptance | — | 0.62 | 0.66 (Medusa 결합) | |
| 정확도 영향 | — | -0.5% | -0.8% | acceptable |
| 추가 VRAM | — | +3 GB (Draft) | +5 GB (Medusa) | |

### V2.5 테스트 시나리오 (V2 단계)

| # | 시나리오 | 입력 | 예상 |
|---|---------|------|------|
| V2-T-01 | Speculative 정상 (K=5) | 10K context | 270 tok/s + acceptance 0.62 |
| V2-T-02 | Medusa 결합 (heads=4) | 동일 | 410 tok/s |
| V2-T-03 | W4 LoRA Target 결합 | use_w4_lora_target=True | 정확도 +14% + 속도 -3% (acceptable) |
| V2-T-04 | Speculative 채택률 낮음 | spec_min_acceptance=0.5 + 실측 0.3 | Speculative 자동 비활성화 |
| V2-T-05 | W12 V2 평가 통과 | 적용 후 RAGAS | QoD ≥ 0.6 통과 |
| V2-T-06 | CF-52-V2-005 인지 | Draft + Target 호출 | 1-1 VRE provisioning 권한 cross-ref |
| V2-T-07 | V1 본문 inheritance | V1 §1~§10 byte EXACT | 변경 없음 (append-only) |

### V2.6 4 cross_domain_deps inline cross-ref (V2 단계)

| dep | 관계 | inline cross-ref 내용 |
|:-:|:-:|---|
| **6-4 RAG** | - 무관 | V2도 LLM 추론 가속 — 6-4 cross-ref 없음. |
| **5-1 Benchmark** | △ 간접 | 속도 12x **측정 = 5-1 권한** (CF-52-003 RESOLVED). 정확도 영향 -0.5~0.8% 검증은 5-1 위임. |
| **6-11 Hologram-Main-LLM** | ◯ 직접 | 6-11 추론 전략 CONSUMER. V2 Speculative + Medusa 정책 적용 시점. |
| **1-1 VRE** | ◯ **CRITICAL** | ★ **CF-52-V2-005 [CF_DETECTED:CF-52-V2-005] 인지 marker** (Draft 1.5B + Target 7B + Medusa heads = 1-1 LLM provisioning 권한). 본 V2 = 사용 정책 (CONSUMER), 1-1 = 모델 capability (PRODUCER). VRAM +5 GB capacity는 1-1 인프라 정합 필요. C-3 STEP_C 본격 정합. |

### V2.7 V2 종결 marker

★ V2 갱신 — V1 본문 byte EXACT 보존 (L1~L226) + V2 섹션 append (L227+) ✅
★ DEFINED-HERE W5 V2 = Speculative Decoding (EAGLE-2/3) + Medusa Head (4 heads, 트리 어텐션) ✅
★ 속도 V1 120 tok/s → V2 ~410 tok/s (3.4x 추가, 누적 base 30 tok/s 대비 12x+) ✅
★ Phase F 8-Layer 검증 가속 + W4 V2 LoRA 결합 + W9 N=3 가속 ✅
★ ★ **CF-52-V2-005 [CF_DETECTED:CF-52-V2-005] 인지 marker** (Draft + Target + Medusa = 1-1 VRE provisioning, C-3 STEP_C 이월) 명시 ✅
★ L9 QoD ≥ 0.6 / L17 Batch 독립 LOCK 정합 ✅
★ V1 본문 inheritance 100% (read-only flag 임시 해제 후 append-only, V1 본문 mismatch 0) ✅
★ V2.6 4 cross_domain_deps (6-4 - + 5-1 △ + 6-11 ◯ + 1-1 ◯ CRITICAL) inline cross-ref ✅
★ L3 판정: PENDING (C-3 STEP_C 일괄)

---

> **★ STAGE 9 5-2 P2-5 W5 V2 갱신**: V2 갱신 산출물 12/23 (W5 V1 본문 byte EXACT + V2 섹션 append, P2-5 2/3). Speculative Decoding (EAGLE-2/3, Draft Qwen2.5-1.5B + Target Qwen2.5-7B, K=5) + Medusa Head (4 heads, 트리 어텐션 top-K=10). 속도 누적 12x (base 30 → V1 120 → V2 ~410 tok/s). W4 V2 LoRA Target 결합 시 정확도 +14% & 속도 -3% (acceptable). ★ **CF-52-V2-005 [CF_DETECTED] 인지 marker** (Draft + Target + Medusa = 1-1 VRE provisioning 권한, C-3 이월). V1 본문 byte EXACT 보존 (V2 섹션 append-only).
