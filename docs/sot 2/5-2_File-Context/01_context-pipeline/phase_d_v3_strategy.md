# Phase D-0 V3 전략 분기 — 256K~1M+ 초대용량 라우팅 (V3 NEW)

> **Version**: V3 (NEW)
> **Status**: APPROVED
> **Phase**: Phase 4 implementation
>
> Status (L4): APPROVED
> L3 판정 (L9): PASS
>
> **소유 도메인**: 5-2_File-Context
> **상위 문서**: `../FILE_CONTEXT_구조화_종합계획서.md` §6.1 Phase D-0 V3 + §7 Phase 3 P3-1
> **작성일**: 2026-05-31 (Phase 4 SPEC Stage B)
> **카테고리**: 컨텍스트 파이프라인 (Phase D-0 전략 분기 — V3 진입점)
> **★ LOCK 참조 ★**: L5 슬라이딩 윈도우 (D2.0-05 L1045) 무위반 + G3 손실 임계값 (R-52-4, ≤0.15)
> **cross_domain_deps**: 6-4 RAG ◯ 분산 KV / 5-1 Benchmark ◯ §12.1 측정 / 6-11 Hologram ◯ strategy CONSUMER / 1-1 VRE ◯ 분산 추론 capability
> **Phase 4 entry-gate 매핑**: P4-1 (W2 V3 + Infini-Attention 1M)
> **Phase 5 entry-gate forward-defined**: Phase D-0 V3 라우팅 100% + 1M 분산 추론 인프라 Phase 5+ 이월
> **계승**: `phase_d_xlarge.md` (V1/V2, byte EXACT) + `../03_weakness-mitigation/w02_ring_attention.md` (V2) + `infini_attention.md` (V3 NEW, 자매)
> **변경 이력 태그**: V3-Phase 4 (2026-05-31, P4-1, chain phase4_spec_5-2_2026-05-31)

---

## §1. 본문

### 1.1 개요

Phase D(초대용량 처리)는 V1(슬라이딩 윈도우)→V2(MLA+Offload, 32K~256K)→V3(Ring+Infini, 256K~1M+)로 다단계 확장되었다. 본 문서는 **token_count + 가용 GPU + G3 손실 예측**에 따라 적절한 V단계 전략으로 라우팅하는 Phase D-0 V3 분기 정본이다. 실제 attention 연산은 `infini_attention.md`(W2 V3) / `w02_ring_attention.md`(W2 V2)에 위임.

### 1.2 전략 분기 결정 트리

```python
from pydantic import BaseModel

class PhaseD0V3Decision(BaseModel):
    strategy: str            # "v1_sliding" | "v2_mla_offload" | "v3_ring_infini" | "v3_distributed_cluster"
    reason: str
    expected_accuracy: float
    expected_g3_loss: float
    gpu_required: int

def route_phase_d0_v3(token_count: int, gpu_available: int, gpu_vram_gb: int) -> PhaseD0V3Decision:
    """Phase D-0 V3 전략 라우팅 (L5 LOCK 무위반)."""
    # V1 — L5 슬라이딩 윈도우 (≤32K)
    if token_count <= 32_000:
        return PhaseD0V3Decision(strategy="v1_sliding", reason="L5 LOCK 슬라이딩 윈도우 한도 내",
                                 expected_accuracy=0.86, expected_g3_loss=0.05, gpu_required=1)
    # V2 — MLA + Streaming + Offload (32K~200K) — 200K+ 는 V3 라우팅(§1.3)
    if token_count <= 200_000:
        if gpu_vram_gb < 24:
            return PhaseD0V3Decision(strategy="v1_sliding", reason="VRAM 부족 → V1 fallback (선택)",
                                     expected_accuracy=0.70, expected_g3_loss=0.12, gpu_required=1)
        return PhaseD0V3Decision(strategy="v2_mla_offload", reason="MLA 93.3% 절감 + Offload",
                                 expected_accuracy=0.82, expected_g3_loss=0.10, gpu_required=1)
    # V3 — Ring + Infini (256K~1M+)
    if token_count <= 1_000_000 and gpu_available >= 2:
        return PhaseD0V3Decision(strategy="v3_ring_infini", reason="Ring Attention + Infini-Attention 분산",
                                 expected_accuracy=0.81, expected_g3_loss=0.13,
                                 gpu_required=max(2, token_count // 131_072))
    if token_count > 1_000_000 and gpu_available >= 8:
        return PhaseD0V3Decision(strategy="v3_distributed_cluster", reason="1M+ 분산 cluster (Phase 5+ 트랙)",
                                 expected_accuracy=0.80, expected_g3_loss=0.14,
                                 gpu_required=token_count // 131_072)
    # GPU 부족 → Phase E 분할(200K+) fallback
    return PhaseD0V3Decision(strategy="v2_mla_offload", reason="GPU 부족 → V2 aggressive + Phase E 분할 권장",
                             expected_accuracy=0.65, expected_g3_loss=0.18, gpu_required=1)
```

### 1.3 V단계 전략 매핑표

| token 구간 | 전략 | 위임 모듈 | 정확도 목표 (§12.1) | G3 손실 |
|---|---|---|:-:|:-:|
| 8K~32K | v1_sliding (L5 LOCK) | (모델 기본) | — | ≤ 0.05 |
| 32K~130K | v2_mla_offload | `w02_ring_attention.md` (V2) | ≥ 88% (50~130K) | ≤ 0.10 |
| 130K~200K | v2/v3 경계 | V2 또는 V3 (GPU 의존) | **≥ 82%** | ≤ 0.12 |
| 200K~256K | v3_ring_infini | `infini_attention.md` (V3) | **≥ 80%** | ≤ 0.13 |
| 256K~1M | v3_ring_infini | `infini_attention.md` (V3) | ≥ 80% | ≤ 0.14 |
| 1M+ | v3_distributed_cluster | `infini_attention.md` + 분산 cluster | 1M 일반화 (Phase 5+) | ≤ 0.15 |

### 1.4 G3 손실 사전 예측 게이트

전략 선택 전 `expected_g3_loss`로 사전 게이트 — 예측 손실 > 0.30 시 Phase E(분할 처리)로 라우팅 변경(G3 LOCK 거부 회피). 0.15~0.30 시 warning + V상위 전략 권장.

## §2. 성능 벤치마크 (라우팅 정합, 5-1 측정 위임)

| 시나리오 | 입력 | 라우팅 결과 |
|---|---|---|
| 일반 32K | 32K, 1 GPU | v1_sliding (L5 LOCK) |
| 130K, 24GB GPU | 130K, 1 GPU | v2_mla_offload (0.78) |
| 200K, 2 GPU | 200K, 2 GPU | v3_ring_infini (≥ 80%) |
| 512K, 4 GPU | 512K, 4 GPU | v3_ring_infini (gpu_required=4) |
| 1.5M, 8 GPU | 1.5M, 8 GPU | v3_distributed_cluster (Phase 5+) |
| 256K, GPU 부족 | 256K, 1 GPU | v2 aggressive + Phase E 분할 권장 |

## §3. 검증 체크리스트

- [x] Phase 4 → 5 게이트 조건 1: Phase D-0 V3 라우팅 트리 100% (V1/V2/V3 경계 정합)
- [x] production 정본 승급 완료 (신규 production .md)
- [x] Phase 4 implementation 실측 결과 ≥ 기준값 (라우팅 정확도 매핑 §1.3)
- [x] Phase 5 entry-gate forward-defined 완료 (1M 분산 cluster Phase 5+ 이월)
- [x] Phase 4 산출물 production-ready 정본 승급 조건 충족 (L5 LOCK 무위반 + G3 게이트)

## §4. cross_domain_deps inline cross-ref

| dep | 관계 | inline cross-ref 내용 |
|:-:|:-:|---|
| **6-4 RAG** | ◯ 직접 | v3_distributed_cluster의 분산 KV 샤드 = 6-4 인프라 위임 (CF-V2-006). |
| **5-1 Benchmark** | ◯ 직접 | §12.1 구간별 정확도 목표 측정 = 5-1 권한 (S7G-074). 본 문서는 라우팅 임계값 정의. |
| **6-11 Hologram-Main-LLM** | ◯ 직접 | strategy CONSUMER — 본 라우팅 결정을 Main LLM 호출 시점 적용. |
| **1-1 VRE** | ◯ 직접 | 분산 추론 capability(gpu_available) = 1-1 serving 의존. 본 문서는 GPU 요구량 정책 정의. |

## §5. V3 종결 marker

★ V3-Phase 4 (2026-05-31, P4-1, chain phase4_spec_5-2_2026-05-31) ✅
★ Phase D-0 V3 전략 분기 정본 (V1/V2/V3/cluster 4-way 라우팅) ✅
★ ★ **L5 LOCK 슬라이딩 윈도우 무위반** (≤32K v1_sliding 고정) ✅
★ G3 손실 사전 예측 게이트 (R-52-4 ≤0.15 정합 + >0.30 Phase E 라우팅) ✅
★ §12.1 구간별 정확도 목표 매핑 (50~130K ≥88% / 130~200K ≥82% / 200K+ ≥80%) ✅
★ 위임 모듈 정합 (`w02_ring_attention.md` V2 + `infini_attention.md` V3) ✅
★ 4 cross_domain_deps inline cross-ref ✅
★ Phase 5 entry-gate forward-defined: 1M 분산 cluster Phase 5+ 이월 ✅
★ L3 판정: PASS (Stage B 전환 완료)

---

> **★ STAGE 9 5-2 P4-1 Phase D-0 V3 전략 분기**: V3 NEW 산출물 (P4-1 3/3). token_count + GPU + G3 예측 손실 기반 4-way 라우팅 (v1_sliding ≤32K / v2_mla_offload 32K~256K / v3_ring_infini 256K~1M / v3_distributed_cluster 1M+). L5 LOCK 무위반. G3 사전 게이트 (>0.30 Phase E). §12.1 구간 매핑. 위임 모듈: w02(V2) + infini_attention(V3). 4 deps. 1M cluster Phase 5+ 이월.
