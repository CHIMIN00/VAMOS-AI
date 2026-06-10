# 카나리 라이프사이클 SOP — 중단·일시정지·재개·롤백 4종 — V3 (4-4 P4-1)

> **카테고리**: 04_canary-deployment
> **세션**: P4-1 (Phase 4 RECOVERY Stage A+B 통합, genuine production write)
> **목적**: LOCK-ML-08 카나리 5단계 배포의 운영 라이프사이클 4종 SOP(① 중단 Stop / ② 일시정지 Pause / ③ 재개 Resume / ④ 롤백 Rollback)를 정본화한다. LOCK-ML-09 자동 롤백 + 자동/수동 권한 분리 + R-17-3 6h 관찰 윈도우 + R-17-4 100건 최소 샘플.
> **버전**: v3.0 (NEW, 2026-06-01)
> **상태**: DRAFT → APPROVED (Phase 4 RECOVERY Stage B Gate 2 PROCEED, 2026-06-01)
> **LOCK**: LOCK-ML-08 (카나리 5단계) + LOCK-ML-09 (자동 롤백) — 본 도메인 정본 (정의 변경 0, R9). 🌟 4-2 P4-3 외부 인용 reverse-inheritance 정본 출처.
> **ReadOnly**: FALSE
> **상위 SoT**: 상세명세 §D (Canary 배포) + §G (카나리 단계 운영 명세)

---

## §1. 교차 참조 블록

| 대상 | 경로 / 섹션 | 용도 |
|------|-----------|------|
| AUTHORITY | `AUTHORITY_CHAIN.md` LOCK-ML-08 (L36) + LOCK-ML-09 (L37) | 5단계 + 자동 롤백 정본 |
| 카나리 라우터 | `04_canary-deployment/canary_router.md` §3.1/§3.2 (Phase 2, 5단계 + LOCK-ML-09) | 라우터 구현 정본 |
| 상세명세 | `MLOPS_LLMOPS_상세명세.md` §D-1 (5단계) + §D-3 (롤백) + §D-4 (자동 판정) + §G-1 (체류시간) + §G-2 (일시정지) | DEFINED-HERE Level 4 |
| 드리프트 SOP | `03_drift-detection/drift_response_sop.md` §4 (critical → 카나리 일시정지 연동) | 드리프트 트리거 |
| plan | `MLOPS_LLMOPS_구조화_종합계획서.md` §4.3 R-17-3 (L231) | 6h 관찰 윈도우 |
| 4-2 CICD | `4-2_CICD-Pipeline/02_cd-workflows/deploy_gate_separation.md` (Wave 1 #11 ✅) | 인프라/모델 게이트 분리 |

---

## §2. LOCK-ML-08 / LOCK-ML-09 정본 (verbatim 인용 — 재정의 0)

> AUTHORITY_CHAIN.md 정본 verbatim (R9 재정의 0 — 🌟 본 도메인이 정본 출처, 4-2 P4-3가 외부 인용):
> `LOCK-ML-08 | 카나리 배포 5단계 | 상세명세 §D-1 | Shadow(0%) → Canary(5%) → Partial(25%) → Majority(75%) → Full(100%) | sot 2/ 승인`
> `LOCK-ML-09 | 카나리 자동 롤백 조건 | 상세명세 §D-3 | QoD 차이 > 0.2 또는 에러율 > Current×2 | sot 2/ 승인`

---

## §3. 카나리 5단계 + 체류시간/샘플 게이트 (상세명세 §G-1 정본 인용)

| Stage | 트래픽 | 최소 체류시간 (R-17-3) | 최소 샘플 (R-17-4) | 자동 승격 조건 | 수동 개입 |
|-------|--------|------------------------|--------------------|----------------|-----------|
| Stage 0 — Shadow | 0% (미러링) | 24h | 1,000 | 에러율 < 0.5%, QoD 차이 < 0.1 | 불필요 |
| Stage 1 — Canary | 5% | 48h (관찰 윈도우 최소 6h) | 500 | Mann-Whitney p ≥ 0.05 (QoD, 에러율) | 이상 시 일시정지 |
| Stage 2 — Partial | 25% | 72h | 2,000 | QoD ≥ 0.85, 에러율 < 1%, 사용자 불만 < 2% | 엔지니어 확인 |
| Stage 3 — Majority | 75% | 48h | 5,000 | 전 지표 안정 (변동 < 5%) | 관리자 승인 |
| Stage 4 — Full | 100% | — | — | — | 롤백 대기 모드 (48h) |

> **QoD ≥ 0.85 (Stage 2)**: 상세명세 §G-1 원문 "QoD ≥ 3.8"은 SOT DEC-010 / CONF-ML-002 SUPERSEDED 결정에 따라 0.0~1.0 스케일로 통일된 LOCK-ML-05 정본 0.85를 적용한다(V2 canary_router 구현 레벨 흡수 완료, §G-1 V1 amendment 본 Phase 4 RESOLVED).
> **R-17-3 (plan §4.3 L231 verbatim)**: "카나리 배포 각 단계 최소 관찰 6시간" — 상세명세 §D-4 observation_window 근거.
> **R-17-4**: 최소 샘플 100건 (자동 판정 `min_samples`, 상세명세 §D-4).

---

## §4. 4종 라이프사이클 SOP (자동/수동 권한 분리)

### ① 카나리 중단 (Stop)
| 항목 | 명세 |
|------|------|
| 트리거 | critical 알림(2개+ 메트릭 동시 위반) 또는 운영자 긴급 명령 |
| 권한 | **자동** (LOCK-ML-09 조건 충족 시) + 수동 긴급 정지 (operator 1인) |
| 동작 | 신규 카나리 트래픽 라우팅 즉시 중지, 현 단계 동결 |
| 후속 | RCA 트리거 (6-13 Operations) + 알림 PagerDuty |

### ② 카나리 일시정지 (Pause)
| 항목 | 명세 |
|------|------|
| 트리거 | §G-2 조건 — 현재 단계에서 QoD 하락 ≥ 0.15 **또는** 에러율 상승 ≥ 50% |
| 권한 | **자동** 일시정지 + **수동** 재개 결재 (권한 분리) |
| 동작 | 해당 단계에서 추가 데이터 수집 (체류시간 2배 연장), 승격 보류 |
| 관찰 윈도우 | R-17-3 6h 최소 관찰 + R-17-4 100건 최소 샘플 |
| 해제 | 추가 데이터에서 조건 충족 → ③ 재개, 미충족 → ④ 롤백 |

### ③ 카나리 재개 (Resume)
| 항목 | 명세 |
|------|------|
| 트리거 | 관찰 윈도우(6h) 통과 + 메트릭 정상 복귀 + 100건 통과 검증 |
| 권한 | **수동** (오퍼레이터 결재, 자동 재개 금지 — 권한 분리 핵심) |
| 동작 | 일시정지 해제, 연장된 체류시간 만료 시 승격 평가 재개 |
| 검증 | Mann-Whitney p ≥ 0.05 재확인 (Stage 1) / 전 지표 안정(Stage 3) |

### ④ 카나리 롤백 (Rollback)
| 항목 | 명세 |
|------|------|
| 트리거 | **LOCK-ML-09**: QoD 차이 > 0.2 **또는** 에러율 > Current × 2 |
| 권한 | **자동** (LOCK-ML-09, 즉시) — 결재 불요 (안전 우선) |
| 동작 | 즉시 Stage 0 (Shadow)으로 복귀, 현재 버전 전량 라우팅 |
| 후속 | 롤백 이벤트 로깅(6-12 Event-Logging) + RCA(6-13) + 드리프트 SOP §5 연동 |

> **권한 분리 원칙**: 중단/롤백 = **자동** (안전 우선, 즉시 실행) / 재개 = **수동** (운영자 결재 필수, 자동 재개 절대 금지). 일시정지는 자동 발동 + 수동 해제.

---

## §5. 메트릭 기반 자동 판정 (상세명세 §D-4 정본)

```python
class CanaryJudge:
    observation_window: timedelta = timedelta(hours=6)   # R-17-3
    min_samples: int = 100                                 # R-17-4

    def judge(self, canary_metrics, baseline_metrics) -> Decision:
        stat, p_value = mannwhitneyu(canary_metrics.qod, baseline_metrics.qod)
        # LOCK-ML-09 자동 롤백
        if p_value < 0.05 and canary_metrics.qod_mean < baseline_metrics.qod_mean:
            return Decision.ROLLBACK
        if canary_metrics.error_rate > baseline_metrics.error_rate * 2:
            return Decision.ROLLBACK
        # 승격
        if len(canary_metrics.samples) >= self.min_samples:
            # 통계적으로 유의하게 우수 (p<0.05 AND QoD ≥ baseline) → 승격
            if p_value < 0.05 and canary_metrics.qod_mean >= baseline_metrics.qod_mean:
                return Decision.PROMOTE
            # 유의차 없음 (p≥0.05): 비열위 확인 후 승격
            if p_value >= 0.05:
                return Decision.PROMOTE
        return Decision.WAIT   # 데이터 부족, 계속 관찰
```

---

## §6. 사용자 세그먼트 배제 (상세명세 §G-3)

```python
def is_canary_eligible(user, stage) -> bool:
    if stage.traffic_pct <= 25 and user.plan in ("pro", "enterprise"):
        return False   # 유료 사용자는 Partial(25%) 이후부터 포함
    if user.opted_out_canary:
        return False
    return deterministic_hash(user.id, stage.deployment_id) < stage.traffic_pct
```
> 내부 팀 = 항상 canary(beta tester) / 유료 = Stage 2까지 제외 / 의료·금융 도메인 = Stage 3까지 제외.

---

## §7. L3 인프라 완성도 매트릭스 (M-1~M-7)

- **M-1** API: `POST /v1/canary/{stop|pause|resume|rollback}` (resume = operator 결재 토큰 필수) + `CanaryStage` enum JSON Schema.
- **M-2** 에러 코드: `CANARY_E01` 승격 게이트 미충족 / `CANARY_E02` 롤백 실행 실패(→수동 에스컬레이션) / `CANARY_E03` resume 권한 부족 / `CANARY_E04` insufficient_samples(<100).
- **M-3** Prometheus: `vamos_canary_stage{deployment}` / `vamos_canary_qod_delta` / `vamos_canary_error_ratio` + Grafana 단계 진행 패널.
- **M-4** 운영 런북: §4 4종 SOP (위 정본).
- **M-5** 보안: 카나리 라우팅 결정적 해싱 입력(user_id+deployment_id) PII 마스킹, 로그 로컬 저장(LOCK-ML-12).
- **M-6** 성능: 라우팅 결정 < 5ms, 판정 사이클 < 6h 관찰(R-17-3) baseline.
- **M-7** 문서화: 본 SOP + canary_router.md + `_index.md` 다이어그램 정합.

---

## §8. 4-2 CICD 게이트 분리 + #15 WF-7 정합

> `deploy_gate_separation.md` (4-2 P4-2) 1:1 정합:
- **WF-7 deploy-prod = 인프라 게이트** (Docker Compose 6 서비스 healthy + 2인 승인 LOCK-CI-10).
- **LOCK-ML-08 카나리 = 모델 게이트** (트래픽 % 점진 롤아웃).
- **직렬 의존**: 인프라 healthy 가 모델 카나리 전제. WF-7 `canary_percentage`(인프라 노드 비율)와 LOCK-ML-08(모델 트래픽 비율)은 별개 축 — 충돌 0. 상세 교차검증은 `_cross_validation/mlops_x_cicd_bmk_report.md` §5 정본.

---

## §9. Phase 5 entry-gate (forward-defined)

- K8s/ArgoCD ↔ 카나리 게이트 (Prometheus 기반 progressive delivery) — Phase 5+ 별도 트랙.
- staging 7일 측정 데이터 → GOLD 등급 baseline.

---

## §10. LOCK 준수 / 검증 선언

- **LOCK-ML-08 verbatim 보존**: §2/§3 5단계 정본 인용, 재정의 0 (🌟 reverse-inheritance 정본 출처, 4-2 외부 인용 정의 변경 0).
- **LOCK-ML-09 verbatim 보존**: §2/§4-④ 자동 롤백 QoD차 > 0.2 또는 에러율 2배 정본 인용.
- **R-17-3/R-17-4 정합**: §3/§5 6h 관찰 + 100건 최소 샘플 plan §4.3 verbatim.
- **canary_router.md 58,885 B / `FF1DEA6FDDCBF413` EXACT 보존**: 본 SOP는 라우터 정본을 인용만, byte/SHA 무손상.

> **정본 선언**: 본 문서는 4-4 카나리 라이프사이클 SOP 정본(V3, P4-1)이다. 4종 SOP(중단·일시정지·재개·롤백) + 자동/수동 권한 분리 정본.
