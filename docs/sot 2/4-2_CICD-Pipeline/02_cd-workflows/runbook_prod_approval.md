# 프로덕션 배포 승인 SOP 런북 — V3 (4-2 P4-1)

> **카테고리**: 02_cd-workflows
> **세션**: P4-1 (Phase 4 RECOVERY Stage A+B 통합)
> **목적**: LOCK-CI-10 2인 승인 정책 + LOCK-CI-11 concurrency 의 운영 SOP를 정본화한다. 승인자 풀·48시간 타임아웃·긴급 롤백 권한을 명세하여 FR-4 (배포 게이트) 를 충족한다.
> **버전**: v3.0 (NEW, 2026-06-01)
> **상태**: DRAFT → APPROVED (Phase 4 RECOVERY Stage B Gate 2 PROCEED, 2026-06-01)
> **LOCK**: LOCK-CI-10 (2인 승인), LOCK-CI-11 (concurrency)
> **ReadOnly**: FALSE

---

## §1. 교차 참조 블록

| 대상 | 경로 / 섹션 | 용도 |
|------|-----------|------|
| AUTHORITY | `AUTHORITY_CHAIN.md` LOCK-CI-10 + LOCK-CI-11 | 승인/concurrency 정본 (verbatim) |
| WF | `02_cd-workflows/WF-7_deploy-prod.md` §3 Environment Protection + §5 배포 게이트 + §6 롤백 트리 | 프로덕션 배포 구조 |
| 종합계획서 | `CICD_PIPELINE_구조화_종합계획서.md` §11.2 FR-4 | 배포 게이트 요구 |
| 장애 대응 | `02_cd-workflows/incident_response_playbook.md` (P4-2) | 긴급 롤백 → 장애 플레이북 연계 |
| 게이트 분리 | `02_cd-workflows/deploy_gate_separation.md` (P4-2) | 인프라 게이트 vs 모델 게이트 |
| 횡단 | `6-13_Operations/` 배포 롤백 절차 §9.4 | 운영 표준 정합 |

---

## §2. LOCK 정본 (verbatim 인용)

> AUTHORITY_CHAIN.md 정본 verbatim (재정의 0):
> `LOCK-CI-10 | 프로덕션 배포 승인 | 상세명세 WF-7 | 2인 이상 승인 필수 (GitHub Environment protection) | 운영팀 승인`
> `LOCK-CI-11 | concurrency 설정 | 상세명세 §병렬화 | group: workflow-ref, cancel-in-progress: true | PHASE_B6 승인`

---

## §3. 2인 승인 SOP (LOCK-CI-10)

### §3.1 Environment Protection Rules (WF-7 §3 정합)

| 항목 | 설정 |
|------|------|
| Environment 이름 | `production` |
| Required reviewers | **2명 이상** (GitHub Environment protection) |
| Wait timer | 0분 (즉시 리뷰 요청) |
| Deployment branches | `main` 만 허용 |
| 승인 대기 타임아웃 | **48시간 → 자동 취소** |

### §3.2 승인자 풀

| 풀 | 구성 | 최소 인원 | 비고 |
|----|------|----------|------|
| Primary reviewers | 릴리스 매니저 + 운영 리드 | 2 | 평시 승인 |
| Secondary reviewers | DevOps 리드 + 백엔드 리드 | 2 | primary 부재 시 |
| 긴급 승인자 | on-call + 운영 리드 | 1 (긴급 롤백 한정) | §3.4 참조 |

> **이해상충 방지**: 배포를 trigger 한 사람은 승인자 2인에 포함될 수 없다 (self-approval 금지). GitHub Environment 의 "Prevent self-review" 옵션 활성화.

### §3.3 48시간 타임아웃 절차

1. `workflow_dispatch` trigger → `preflight` + `validate-inputs` 통과 → Environment 승인 대기 진입.
2. 승인 요청 Slack `#release` + 개별 reviewer 알림.
3. 48시간 내 2인 승인 미충족 → **GitHub Actions 자동 취소** (`TIMEOUT_APPROVAL` 로그).
4. 취소 후 재배포는 신규 `workflow_dispatch` 로 처음부터 (승인 carry-over 금지).

### §3.4 긴급 롤백 권한

| 시나리오 | 권한 | 승인 요건 |
|----------|------|----------|
| 카나리 자동 롤백 (에러율 > 2%) | 자동 | 승인 불요 (시스템 자동) |
| smoke 실패 즉시 롤백 | 자동 | 승인 불요 (< 2분) |
| monitor-30min 이상 → 수동 롤백 | on-call 단독 | **1인 긴급 권한** (사후 운영 리드 통보 필수) |
| 신규 버전 재배포 | 표준 2인 승인 | LOCK-CI-10 적용 |

> 긴급 롤백(이전 안정 버전 복귀)은 2인 승인 예외이나, 신규 버전 *배포*는 항상 2인 승인 적용. 롤백 후 48시간 내 RCA 작성(`rca_template.md`).

---

## §4. concurrency SOP (LOCK-CI-11)

- 일반 WF: `group: <workflow-ref>`, `cancel-in-progress: true` (LOCK-CI-11 정본).
- **WF-7 deploy-prod 예외**: `group: deploy-prod`, `cancel-in-progress: false` (배포 중단 안전 — WF-7 §2 정합). 동시 배포 2건은 대기 큐 처리(취소 없음).
- cron WF (WF-9/11/13) + benchmark-baseline: `cancel-in-progress: false` (시계열/배포 보호).

> cancel-in-progress=false 는 LOCK-CI-11 의 정당 예외(배포 안전·시계열 보호)이며 정본 재정의가 아니다.

---

## §5. 배포 게이트 체크리스트 (WF-7 §5 정합)

| 조건 | 유형 | 실패 시 |
|------|------|--------|
| 스테이징 E2E 전부 통과 (WF-12 all scope) | 자동 | 배포 차단 |
| 2명 이상 승인 (GitHub Environment) | 수동 | 48시간 대기 → 자동 취소 |
| 카나리 QoD ≥ 0.85 | 자동 | 자동 롤백 |
| 카나리 에러율 < 2% | 자동 | 자동 롤백 |
| 스모크 5/5 통과 | 자동 | 즉시 롤백 |

---

## §6. 담당 / 에스컬레이션

- **1차**: 릴리스 매니저 (배포 trigger + 승인 조율)
- **2차**: 운영 리드 (승인 + 긴급 롤백 판단)
- **에스컬레이션**: L2 (릴리스 매니저) → L3 (운영 리드 + on-call PagerDuty P2) → L4 (운영 리드 P1, 프로덕션 장애 시)

---

## §7. LOCK 준수 선언

- **LOCK-CI-10 verbatim 보존**: §2 정본 인용, 2인 승인 정책 재정의 0.
- **LOCK-CI-11 verbatim 보존**: §2 정본 인용 + §4 정당 예외(cancel-in-progress=false) 명시.

> **정본 선언**: 본 문서는 4-2 도메인 프로덕션 배포 승인 SOP 정본(V3)이다. LOCK-CI-10 변경 시 운영팀 승인 필수.
