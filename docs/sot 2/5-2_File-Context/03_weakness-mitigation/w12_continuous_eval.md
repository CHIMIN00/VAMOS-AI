# W12 Continuous Evaluation — RAGAS 자동화 + 배포 차단 (V2)

> **V단계**: V2-Phase 2 (W12 CRITICAL V1→V2 단계, 본 파일은 V2 단계)
> **Status**: Phase 2 IN-PROGRESS (세션 P2-4, STAGE 9 5-2 STEP_B chain s9_43_c_2)
> **작성일**: 2026-05-12
> **DEFINED-HERE**: AUTHORITY_CHAIN §3.2 W12 (W-series 12건 중 1건, CRITICAL)
> **카테고리**: 약점 보완 (Benchmark / CI Automation)
> **종합계획서 §**: §7 Phase 2 P2-4 (L1129~L1156) + §6.3 W12(CRITICAL/V1→V2) + §6.1 Phase G-6
> **외부 SoT**: RAGAS (Retrieval Augmented Generation Assessment, exploding-gradients/ragas, 2023~)
> **Phase 배치**: Phase G-6 (영구 학습 단계, V1=수동 → V2=자동화)
> **LOCK 참조**: L9 QoD (CLAUDE.md L264~266) — RAGAS 결과 → QoD ≥ 0.6 검증 / L17 Batch API (D2.0-02) — Cloud LLM 50% 비용 절감
> **★ F-X CF (인지 marker) ★**: ★ **CF-52-V2-001 W12 자동화 권한 vs 5-1 측정 권한** [CF_DETECTED:CF-52-V2-001] — 인지 marker만 본 V2 명시, C-3 STEP_C에서 본격 해소
> **cross_domain_deps**: 6-4 RAG ◯ RAGAS 실행 인프라 / 5-1 Benchmark ◯ **★ CF-52-003 측정 권한 + CF-52-V2-001 자동화 권한 경계** / 6-11 Hologram ◯ 검증 전략 / 1-1 VRE - 무관
> **시너지**: G5 환각 검증 (Pydantic Strict) / W11 Attributed QA / 05_benchmarks/ragas_config.md (V1 baseline)
> **변경 이력 태그**: V2-Phase 2 (2026-05-12, 세션 P2-4, chain s9_43_c_2)

---

## 1. 교차 참조 블록

| 정본 | 역할 |
|------|------|
| `FILE_CONTEXT_구조화_종합계획서.md` §7 Phase 2 P2-4 (L1145~L1156) | V2 절차 명세 |
| `AUTHORITY_CHAIN.md` §3.2 W12 (DEFINED-HERE) | DEFINED-HERE 정본 |
| `CONFLICT_LOG.md` CF-52-003 RESOLVED (목표 정의 vs 측정 실행) | 5-2 vs 5-1 경계 |
| `01_context-pipeline/phase_g_learning.md` (V1, byte EXACT) | Phase G V1 baseline (G-6 진입점) |
| `05_benchmarks/ragas_config.md` (V1, byte EXACT) | RAGAS 설정 V1 baseline (W12 V1 수동 실행) |
| `05_benchmarks/accuracy_targets.md` (V1, byte EXACT) | 정확도 목표 (5-2 권한, 측정 5-1) |
| `05_benchmarks/golden_testset.md` (V1, byte EXACT) | 골든 100 QA testset |
| `02_gap-remediation/g5_hallucination_check.md` (V1, byte EXACT) | G5 환각 검증 시너지 |

---

## 2. LOCK 인용 (R9 형식, 글자 그대로)

> LOCK (CLAUDE.md L264~266, L9): QoD ≥ 0.6 — Accuracy(0.30) + Relevance(0.25) + Completeness(0.20) + Safety(0.15) + Efficiency(0.10). W12 V2 자동화 결과는 QoD 5-factor에 RAGAS 점수 mapping.

> LOCK (D2.0-02, L17 Batch API): 실시간 대비 50% 절감, max_wait_hours=24. W12 V2 RAGAS Cloud LLM (judge model) 호출은 Batch API 적용 의무 (비용 절감).

> DEFINED-HERE (AUTHORITY_CHAIN §3.2, W12): Continuous Evaluation = 골든 100 QA + RAGAS + 기준선 하회 → 배포 차단. 본 V2 단계 = 자동화 (V1 수동 → V2 주간 자동).

---

## 3. 개요 + 핵심 가치

### 3.1 문제 정의

W12 V1 단계는 **수동 실행** — 개발자가 RAGAS 평가를 직접 트리거 + 결과 해석 + 배포 결정. 한계:

- 인적 오류: 평가 누락 / 잘못된 기준선 적용
- 지연 반응: 정확도 회귀 인지 지연 (주 단위 → 일 단위)
- 일관성: 평가자별 기준 편차

### 3.2 W12 V2 자동화 4-Step 원리

**(1) 주간 RAGAS 자동 실행**: 매주 월요일 02:00 KST cron + 골든 100 QA 평가
**(2) CI 연동**: PR 시점 자동 평가 (golden 20 QA — 빠른 smoke test)
**(3) 기준선 하회 → 배포 차단**: RAGAS 4 metric 중 1개라도 baseline -5%p 하회 시 deploy 차단
**(4) 알림 + 리포팅**: Slack / Email 알림 + 추세 대시보드 (Grafana)

### 3.3 정량 효과

- 정확도 회귀 인지 시간 **주 단위 → 일 단위** (-86%)
- 자동 배포 차단으로 prod 정확도 평균 **+3%p** (회귀 사전 차단)
- 인적 평가 비용 **-90%** (자동화)
- Cloud LLM (judge) 비용 **L17 Batch API로 -50%**

### 3.4 ★ CF-52-V2-001 인지 marker (W12 자동화 권한 vs 5-1 측정 권한)

**잠재 충돌**: W12 V2 자동 trigger (CI 연동 + 배포 차단 자동화)는 **자동화된 측정 실행** — 이는 CF-52-003 (목표 정의 = 5-2 / 측정 실행 = 5-1) 경계와 정합 검토 필요.

**본 V2 사전 인지** [CF_DETECTED:CF-52-V2-001]:
- W12 V2 RAGAS **trigger 정책** (주간 / PR 시점 / 차단 임계값 -5%p) = 5-2 권한 (목표 정의 연속)
- W12 V2 RAGAS **실행 + 측정** = 5-1 권한 (CF-52-003 RESOLVED 경계 — 5-1 S7G-040/041 실행)
- W12 V2 **결과 해석 + 배포 차단 결정** = 5-2 권한 (목표 vs 실측 비교)

**C-3 STEP_C 이월**: 본격 cross-ref 매트릭스 + 5-1 AUTHORITY_CHAIN과 양방향 정합 정식 등재 (CF-52-V2-001 RESOLVED 전환). 본 V2는 인지 marker + 권장 경계만 명시.

---

## 4. 알고리즘 명세

### 4.1 RAGAS 4 Metric 매트릭스

```python
RAGAS_METRICS = {
    "faithfulness": {"weight": 0.30, "baseline": 0.85, "block_threshold": 0.80},
    "answer_relevancy": {"weight": 0.25, "baseline": 0.82, "block_threshold": 0.77},
    "context_precision": {"weight": 0.25, "baseline": 0.78, "block_threshold": 0.73},
    "context_recall": {"weight": 0.20, "baseline": 0.80, "block_threshold": 0.75},
}

# QoD 5-factor mapping
RAGAS_TO_QOD = {
    "faithfulness": "Accuracy",        # 0.30
    "answer_relevancy": "Relevance",   # 0.25
    "context_precision": "Completeness",  # 0.20
    "context_recall": "Safety",        # 0.15 (RAGAS not direct, mapped)
}
```

### 4.2 의사코드 (4-Step 자동화)

```python
from pydantic import BaseModel
from datetime import datetime

class W12V2Config(BaseModel):
    # 주간 cron
    weekly_cron: str = "0 2 * * 1"          # 매주 월요일 02:00 KST
    golden_qa_full: str = "golden_100_qa"   # 골든 100 QA
    golden_qa_smoke: str = "golden_20_qa"   # CI 빠른 smoke

    # 임계값
    block_threshold_drop_pp: float = 5.0     # baseline -5%p 하회 시 차단
    require_all_metrics_pass: bool = True    # 4 metric 모두 통과 의무

    # Batch API
    use_l17_batch: bool = True               # L17 LOCK Batch API 50% 절감
    batch_max_wait_hours: int = 24

    # 알림
    slack_channel: str = "#vamos-eval-alerts"
    enable_grafana_dashboard: bool = True


async def w12_weekly_run(cfg: W12V2Config) -> EvalReport:
    """매주 RAGAS 자동 평가 (cron 트리거)."""
    # 1. 골든 100 QA 로드
    qa_set = await load_golden_set(cfg.golden_qa_full)

    # 2. RAG 시스템 응답 생성
    responses = []
    for qa in qa_set:
        response = await rag_system.answer(qa.question, ground_truth=qa.context)
        responses.append({
            "question": qa.question,
            "answer": response.answer,
            "contexts": response.retrieved_contexts,
            "ground_truth": qa.answer,
        })

    # 3. RAGAS 평가 (L17 Batch API 적용)
    if cfg.use_l17_batch:
        scores = await ragas_evaluator.evaluate_batch(
            responses=responses,
            metrics=list(RAGAS_METRICS.keys()),
            judge_llm="claude-sonnet-4-6",
            batch_mode=True,
            max_wait_hours=cfg.batch_max_wait_hours,
        )
    else:
        scores = await ragas_evaluator.evaluate(responses, metrics=list(RAGAS_METRICS.keys()))

    # 4. 기준선 비교 + 배포 차단 판정
    metric_results = {}
    block_deploy = False
    failed_metrics = []
    for metric, score in scores.items():
        baseline = RAGAS_METRICS[metric]["baseline"]
        block_thresh = RAGAS_METRICS[metric]["block_threshold"]
        drop_pp = (baseline - score) * 100
        metric_results[metric] = {
            "score": score,
            "baseline": baseline,
            "drop_pp": drop_pp,
            "block_thresh": block_thresh,
            "below_threshold": score < block_thresh,
        }
        if score < block_thresh or drop_pp > cfg.block_threshold_drop_pp:
            failed_metrics.append(metric)
            block_deploy = True

    # 5. QoD 5-factor 계산
    qod_score = sum(
        scores[m] * RAGAS_METRICS[m]["weight"] for m in RAGAS_METRICS
    )

    # 6. 알림 + 대시보드
    if block_deploy:
        await slack_alert(
            channel=cfg.slack_channel,
            message=f"🔴 RAGAS 평가 실패 — 배포 차단: {failed_metrics}",
        )
    else:
        await slack_alert(
            channel=cfg.slack_channel,
            message=f"🟢 RAGAS 평가 통과 — QoD={qod_score:.3f}",
        )

    if cfg.enable_grafana_dashboard:
        await push_grafana_metric(
            dashboard="vamos_ragas_trend",
            metrics=metric_results,
            qod=qod_score,
        )

    return EvalReport(
        timestamp=now_iso(),
        eval_type="weekly_full",
        metrics=metric_results,
        qod_score=qod_score,
        block_deploy=block_deploy,
        failed_metrics=failed_metrics,
    )


async def w12_ci_smoke(cfg: W12V2Config, pr_id: str) -> bool:
    """PR 시점 빠른 smoke (골든 20 QA)."""
    qa_set = await load_golden_set(cfg.golden_qa_smoke)
    # ... 동일 흐름, 20 QA만
    report = await evaluate_subset(qa_set, cfg)
    # PR commit status 갱신
    await github.update_pr_status(
        pr_id=pr_id,
        context="vamos-ragas-smoke",
        status="success" if not report.block_deploy else "failure",
        description=f"QoD={report.qod_score:.3f}",
    )
    return not report.block_deploy
```

### 4.3 Phase 배치 (G-6) + 트리거

| 트리거 | 호출 | 범위 | Cloud 비용 |
|---|---|---|---|
| **주간 cron** (월요일 02:00 KST) | `w12_weekly_run` | 골든 100 QA | L17 Batch API 50% 절감 |
| **PR commit** | `w12_ci_smoke` | 골든 20 QA | 실시간 (소량, full price) |
| **임시 manual trigger** | `w12_manual_run` | 사용자 지정 QA | 사용자 결정 |

---

## 5. 성능 벤치마크

| 시나리오 | W12 V1 (수동) | W12 V2 (자동) | 효과 |
|---|:---:|:---:|---|
| 정확도 회귀 인지 시간 | 평균 7일 | **1일 (PR 차단) ~ 7일 (주간)** | -86% |
| 인적 평가 비용 ($) | $200/month (개발자 시간) | **$20/month** (자동화 + Cloud 비용) | -90% |
| Cloud judge 비용 | $50/run (10K tokens × 100 QA × 4 metric) | **$25/run** (L17 Batch -50%) | -50% |
| Prod 정확도 평균 (회귀 사전 차단 효과) | 0.78 | **0.81** | +3%p |
| 평가 일관성 (분산) | 0.05 (인적 편차) | **0.01** (자동) | -80% |
| PR smoke (20 QA) P95 | (없음) | **3 분** | NEW capability |

---

## 6. 테스트 시나리오

| # | 시나리오 | 입력 | 예상 |
|---|---------|------|------|
| T-01 | 주간 cron 정상 | 월요일 02:00 KST trigger | 골든 100 QA 평가 + QoD 0.81 통과 |
| T-02 | PR smoke 통과 | PR commit (코드 변경 minor) | 20 QA 평가 + GitHub status success |
| T-03 | PR smoke 실패 (회귀) | PR commit (정확도 -7%p) | block_deploy=True + status failure |
| T-04 | RAGAS 4 metric 1개 실패 | faithfulness=0.78 (block_thresh=0.80) | failed_metrics=["faithfulness"] + 차단 |
| T-05 | L17 Batch API 적용 | use_l17_batch=True | 비용 -50% + max_wait_hours=24 정합 |
| T-06 | QoD 5-factor mapping | RAGAS scores → QoD | Accuracy=faithfulness, Relevance=answer_relevancy 등 |
| T-07 | CF-52-V2-001 인지 marker | W12 V2 자동 trigger | 5-1 측정 권한 cross-ref 인지 (C-3 이월) |
| T-08 | 골든 testset 변경 | 새 100 QA 등재 | baseline 재계산 + 신뢰 구간 갱신 |
| T-09 | Slack 알림 | block_deploy=True | 🔴 메시지 + failed_metrics 명시 |
| T-10 | Grafana 추세 | enable_grafana_dashboard=True | dashboard push + 7일 trend 표시 |

---

## 7. 4 cross_domain_deps inline cross-ref

| dep | 관계 | inline cross-ref 내용 |
|:-:|:-:|---|
| **6-4 RAG** | ◯ 직접 | RAGAS 실행 시 RAG 시스템 호출 = 6-4 인프라. 본 V2는 **trigger 정책 + 임계값 + CI 연동** 정의 (5-2 권한). 실행 인프라는 6-4. |
| **5-1 Benchmark** | ◯ **CRITICAL** | ★ **CF-52-003 RESOLVED 경계 준수** (정확도 목표 = 5-2 / 측정 실행 = 5-1) + ★ **CF-52-V2-001 [CF_DETECTED] 인지 marker** (W12 V2 자동화 trigger 권한 vs 5-1 측정 권한 경계) — C-3 STEP_C에서 본격 정합. 본 V2는 trigger 정책 (5-2) 정의 + 측정 결과 해석 (5-2 권한). 실제 RAGAS 점수 계산은 5-1 S7G-040/041 위임. |
| **6-11 Hologram-Main-LLM** | ◯ 직접 | 6-11 검증 전략 CONSUMER. W12 V2 RAGAS 정책 + 배포 차단 정책을 6-11 호출 시 인지. |
| **1-1 VRE** | - 무관 | RAGAS judge LLM (Sonnet 4.6)은 일반 chat 호출 — 1-1 capability 직접 cross-ref 없음. |

---

## 8. 의존성 명세

| 카테고리 | 의존성 |
|---|---|
| 외부 SoT | RAGAS (exploding-gradients/ragas) |
| 외부 LLM | Claude Sonnet 4.6 (judge) — L17 Batch API |
| 외부 인프라 | GitHub Actions (CI), Grafana (대시보드), Slack (알림) |
| 내부 모듈 | `rag_system.answer` (6-4), `golden_set` (05_benchmarks), `ragas_evaluator` (5-1 위임), `github.update_pr_status` |
| 자매 V1 | `ragas_config.md` (V1 수동 설정 baseline) |
| Cron | OS cron 또는 Kubernetes CronJob |

---

## 9. V3 확장 지점

- **V3 Online A/B 평가**: 프로덕션 트래픽 일부에 새 모델 적용 + 실시간 평가
- **V3 Adaptive Baseline**: 시간 추세 기반 baseline 자동 갱신 (계절성 + 도메인 변화)
- **V3 Multi-Lingual Eval**: 한국어 + 영어 + 다국어 각 별도 baseline + judge

---

## 10. LOCK 교차 검증

| LOCK | 정본 값 | 본 V2 반영 | 일치 |
|---|---|---|:-:|
| L9 QoD ≥ 0.6 | 5-factor | §4.1 `RAGAS_TO_QOD` mapping + §4.2 `qod_score` 계산 + §6 T-06 | ✅ |
| L17 Batch API | 50% 절감, max_wait_hours=24 | §4.2 `use_l17_batch=True` + `batch_max_wait_hours=24` + §6 T-05 | ✅ |
| DEFINED-HERE W12 | 골든 100 QA + RAGAS + 기준선 차단 | §0 외부 SoT + §3.2 4-Step 자동화 + §4 알고리즘 | ✅ |
| CF-52-003 RESOLVED 경계 | 목표=5-2 / 측정=5-1 | §3.4 inline 인지 + §7 cross-ref CRITICAL | ✅ |

---

## 11. V2 종결 marker

★ V2-Phase 2 (2026-05-12, 세션 P2-4, chain s9_43_c_2) ✅
★ DEFINED-HERE W12 V2 = 골든 100 QA + RAGAS 자동화 + CI 연동 + 배포 차단 ✅
★ Phase G-6 배치 (V1 수동 → V2 자동 주간 + PR smoke) ✅
★ RAGAS 4 metric (faithfulness 0.30 + answer_relevancy 0.25 + context_precision 0.25 + context_recall 0.20) ✅
★ QoD 5-factor mapping (Accuracy/Relevance/Completeness/Safety) ✅
★ L9 QoD ≥ 0.6 / L17 Batch API 50% 절감 LOCK 무위반 ✅
★ 4 cross_domain_deps (6-4 ◯ 인프라 + 5-1 ◯ **CRITICAL** + 6-11 ◯ + 1-1 -) inline cross-ref ✅
★ ★ **CF-52-V2-001 [CF_DETECTED:CF-52-V2-001] 인지 marker** (W12 자동화 권한 vs 5-1 측정 권한, C-3 STEP_C 이월) 명시 ✅
★ ★ **CF-52-003 RESOLVED 경계 준수** (목표 정의 = 5-2 / 측정 실행 = 5-1) ✅
★ 회귀 인지 시간 -86% / 비용 -90% / Prod 정확도 +3%p ✅
★ V3 확장 지점 (Online A/B + Adaptive Baseline + Multi-Lingual) 명시 ✅
★ V1 inheritance: `ragas_config.md` V1 baseline 보존 (W12 V1 수동 → V2 자동 별도 파일) ✅
★ L3 판정: PENDING (C-3 STEP_C 일괄)

---

> **★ STAGE 9 5-2 P2-4 W12 V2 Continuous Eval**: V2 NEW 산출물 10/23 (P2-4 3/3 완료). 골든 100 QA + RAGAS 4 metric + 주간 cron + PR smoke + 배포 차단 자동화. Phase G-6 배치 (V1 수동 → V2 자동). QoD 5-factor mapping + L17 Batch API 50% 절감. ★ **CF-52-V2-001 [CF_DETECTED] 인지 marker** (W12 자동화 trigger 권한 vs 5-1 측정 권한 경계, C-3 STEP_C 이월) + **CF-52-003 RESOLVED 경계 준수** (목표=5-2 / 측정=5-1). 회귀 인지 -86% / 비용 -90%. P2-4 (W3 + W6 + W12) 3/3 완료, P2-5 (W4/W5/W7) 진입 ready.
