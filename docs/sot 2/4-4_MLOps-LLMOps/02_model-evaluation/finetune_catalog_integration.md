# Fine-tuned 모델 카탈로그 통합 — V3 (4-4 P4-2)

> **카테고리**: 02_model-evaluation
> **세션**: P4-2 (Phase 4 RECOVERY Stage A+B 통합, genuine production write)
> **목적**: LOCK-ML-11 모델 카탈로그 필수 7 필드(id/provider/strengths/cost/context_window/speed/eval_score)에 Fine-tuned(LoRA/QLoRA) 모델을 통합 등록하는 절차를 정본화한다. base_model + adapter weights URI + 메타데이터 + R-17-6 전체 벤치마크 eval_score 연동.
> **버전**: v3.0 (NEW, 2026-06-01)
> **상태**: DRAFT → APPROVED (Phase 4 RECOVERY Stage B Gate 2 PROCEED, 2026-06-01)
> **LOCK**: LOCK-ML-11 (카탈로그 필수 필드) — STEP7-F S7F-076 정본 (정의 변경 0, R9)
> **ReadOnly**: FALSE
> **상위 SoT**: STEP7-F Part 9 S7F-076 / model_catalog_spec.md (Phase 1 V1)

---

## §1. 교차 참조 블록

| 대상 | 경로 / 섹션 | 용도 |
|------|-----------|------|
| AUTHORITY | `AUTHORITY_CHAIN.md` LOCK-ML-11 (L39) | 카탈로그 7 필드 정본 |
| V1 카탈로그 | `02_model-evaluation/model_catalog_spec.md` (Phase 1) | 카탈로그 스키마 base |
| LoRA/QLoRA | `lora_finetune_pipeline.md` + `qlora_finetune_pipeline.md` (P4-2) | 학습 산출물 |
| 벤치마크 | `auto_benchmark_pipeline.md` §3 (8차원 D1~D8 → eval_score) | eval_score 산출 |
| 5-1 BMK | `5-1_Benchmark-Evaluation/` (S7G-076 모델 카탈로그) | 양방향 cross-ref |

---

## §2. LOCK-ML-11 정본 (verbatim 인용 — 재정의 0)

> AUTHORITY_CHAIN.md 정본 verbatim (R9 재정의 0):
> `LOCK-ML-11 | 모델 버저닝 규칙 (카탈로그 필수 필드) | STEP7-F S7F-076 | id, provider, strengths, cost, context_window, speed, eval_score | STEP7-F 승인`

---

## §3. 카탈로그 7 필수 필드 (LOCK-ML-11) + Fine-tuned 확장

| # | 필드 (LOCK-ML-11 verbatim) | Fine-tuned 모델 값 예시 |
|---|----------------------------|--------------------------|
| 1 | `id` | `vamos-ko-coding-lora-v1.2.0` |
| 2 | `provider` | `local-finetune` (base: anthropic/openai) |
| 3 | `strengths` | `["korean", "coding", "tool_use"]` |
| 4 | `cost` | `$0.012/1k tok` (추론 비용) |
| 5 | `context_window` | `200000` (base 상속) |
| 6 | `speed` | `tps: 85, ttft_ms: 320` |
| 7 | `eval_score` | `87.0` (0~100 스케일, 8차원 D1~D8 가중평균, R-17-6 산출 — model_catalog_spec eval_score ge=0.0 le=100.0 정합) |

### §3.1 Fine-tuned 전용 메타데이터 (7 필드 + 확장)
```yaml
- id: vamos-ko-coding-lora-v1.2.0
  provider: local-finetune
  strengths: [korean, coding, tool_use]
  cost: 0.012
  context_window: 200000
  speed: { tps: 85, ttft_ms: 320 }
  eval_score: 0.87
  # 확장 메타데이터 (Fine-tuned 전용)
  base_model: anthropic/claude-haiku-4-5
  adapter_type: lora                 # lora | qlora
  adapter_weights_uri: s3://local/adapters/ko-coding-v1.2.0/
  training_recipe: { r: 16, alpha: 32, dropout: 0.1, lr: 2.0e-4 }
  improvement_pp: { coding: 6.2, korean: 5.8 }   # base 대비 ≥ 5%p
  safety_rate: 0.0008                # < 0.1% (LOCK-ML-05 D6)
  benchmark_run_id: bench-2026-06-01-001   # R-17-6 전체 벤치마크
  available: true                    # 게이트 통과 시에만 true
```

---

## §4. 등록 절차 (R-17-6 게이트)

1. LoRA/QLoRA 학습 완료 → adapter weights 저장.
2. **R-17-6 전체 벤치마크 자동 트리거** → 8차원 D1~D8 풀 스위트 → `eval_score` 산출.
3. LOCK-ML-05 품질 게이트: task ≥ 85% / QoD ≥ 0.85 / safety < 0.1% / p95 < 3s / cost < $0.05.
4. base 대비 ≥ 5%p 개선 검증.
5. 게이트 통과 시에만 `available: true` 등록 (미통과 → 등록 차단, 카나리 진입 불가).
6. LOCK-ML-08 카나리 5단계 적용 → Full(100%) 도달 시 production 정본.

> **데이터 무결성 (R-17-6)**: eval_score는 모델 교체/Fine-tuning 시마다 전체 벤치마크로 재산출. 캐시된 점수 사용 금지.

---

## §5. L3 인프라 완성도 매트릭스 (M-1~M-7)

- **M-1** API: `POST /v1/catalog/models` (7 필드 + 확장 메타) + `ModelCatalogEntry` JSON Schema (7 필드 required).
- **M-2** 에러 코드: `CAT_E01` 필수 7 필드 누락(block) / `CAT_E02` eval_score 미산출(R-17-6 미트리거) / `CAT_E03` 게이트 미통과 등록 시도 / `CAT_E04` adapter URI 무효.
- **M-3** Prometheus: `vamos_catalog_models_total{available}` / `vamos_catalog_eval_score`.
- **M-4** 운영 런북: 게이트 미통과 모델 처리 / eval_score 재산출 / 카탈로그 버전 폐기.
- **M-5** 보안: adapter weights URI 접근 제어 (서명 URL) + 카탈로그 변경 감사 로그.
- **M-6** 성능: 카탈로그 조회 < 10ms + eval_score 산출 배치 시간.
- **M-7** 문서화: 본 통합 + model_catalog_spec + lora/qlora + `_index.md` 정합.

---

## §6. 5-1 BMK 양방향 정합

- **S7G-076 모델 카탈로그**: 5-1 BMK 카탈로그 스키마와 LOCK-ML-11 7 필드 1:1 정합 (양방향 cross-ref AUTHORITY 등재).
- **S7G-071 모델 평가 파이프라인**: eval_score 산출은 5-1 벤치마크 측정 위임 (4-4는 카탈로그 등록 정본, 5-1은 측정 정본 — 경계 분리).

---

## §7. Phase 5 entry-gate (forward-defined)

- 멀티 어댑터 카탈로그 (도메인별 hot-swap 라우팅) — Phase 5+ 이월.
- A/B 카탈로그 버전 자동 승격 — Phase 5+ 별도 트랙.

---

## §8. LOCK 준수 / 검증 선언

- **LOCK-ML-11 verbatim 보존**: §2/§3 7 필드 정본 인용, 재정의 0 (R9).
- **R-17-6 정합**: §4 eval_score 전체 벤치마크 재산출 verbatim.
- **LOCK-ML-08 카나리 적용**: §4 인용 (정의 변경 0).
- **model_catalog_spec.md EXACT 보존**: V1 스키마 base 인용만.

> **정본 선언**: 본 문서는 4-4 Fine-tuned 모델 카탈로그 통합 정본(V3, P4-2)이다. LOCK-ML-11 7 필드 + adapter 확장 메타데이터 정본.
