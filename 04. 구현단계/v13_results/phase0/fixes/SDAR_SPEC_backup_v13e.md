# VAMOS SDAR (Self-Diagnosis & Auto-Repair) 설계 명세서

> **버전**: v1.0.0 | **생성일**: 2026-02-23
> **소스**: VAMOS_MASTER_SPECIFICATION v1.0.0, BASE-1.3, PLAN-3.0
> **목적**: VAMOS AI 시스템의 자기진단 및 자동수리 기능에 대한 완전한 설계 명세
> **모듈 ID**: I-25 (신규) | **연관 모듈**: I-6, I-16, I-18, I-20, S-1, S-4, S-8

---

## 목차

1. [시스템 개요 (System Overview)](#1-시스템-개요-system-overview)
2. [SDAR 아키텍처 (5-Layer Pipeline)](#2-sdar-아키텍처-5-layer-pipeline)
3. [단계적 자율 모델 (Graduated Autonomy Model)](#3-단계적-자율-모델-graduated-autonomy-model)
4. [오류 분류 체계 (Error Classification System)](#4-오류-분류-체계-error-classification-system)
5. [수리 액션 카탈로그 (Repair Action Catalog)](#5-수리-액션-카탈로그-repair-action-catalog)
6. [기존 VAMOS 시스템 통합](#6-기존-vamos-시스템-통합)
7. [상태 머신 (State Machine)](#7-상태-머신-state-machine)
8. [스키마 설계 (Schema Design)](#8-스키마-설계-schema-design)
9. [제약 및 안전 규칙 (LOCK)](#9-제약-및-안전-규칙-lock)
10. [버전 로드맵 (Version Roadmap)](#10-버전-로드맵-version-roadmap)

---

# 1. 시스템 개요 (System Overview)

## 1.1 목적 및 배경

VAMOS SDAR (Self-Diagnosis & Auto-Repair)는 ALZip의 오류 자동 복구 기능에서 영감을 받아 설계된 **자기진단 및 자동수리 시스템**이다. VAMOS 운영 중 발생하는 다양한 오류(인프라 장애, 모델 품질 저하, 로직 오류, 코드 버그 등)를 실시간으로 감지하고, 근본 원인을 분석하며, 위험 수준에 따라 자동 또는 반자동으로 수리를 수행한다.

**핵심 가치**:
- **가용성 극대화**: 시스템 다운타임 최소화, 사용자 경험 중단 방지
- **자율적 복원력**: 반복적/일상적 장애에 대한 인간 개입 부담 제거
- **안전 우선 복구**: 수리 자체가 새로운 장애를 유발하지 않도록 보장
- **점진적 자율 확대**: 검증된 수리 패턴만 자동화 범위 확대

## 1.2 핵심 원칙: 단계적 자율수준 (Graduated Autonomy)

SDAR의 가장 중요한 설계 원칙은 **단계적 자율수준(Graduated Autonomy)**이다. ALZip이 파일 복구 시 "안전한 복구는 자동, 위험한 복구는 사용자 확인"이라는 원칙을 따르듯, SDAR도 동일한 철학을 적용한다.

```
                    ┌──────────────────────────────────────────┐
                    │         GRADUATED AUTONOMY PYRAMID        │
                    │                                          │
                    │           ▲  AR-L4 (HIGH RISK)           │
                    │          ╱ ╲  Code Patch, Migration      │
                    │         ╱   ╲  Snapshot + Notify         │
                    │        ╱─────╲                           │
                    │       ╱ AR-L3 ╲  Config, Prompt Patch    │
                    │      ╱ MODERATE╲  Reversible + Notify    │
                    │     ╱───────────╲                        │
                    │    ╱   AR-L2     ╲  Retry, Restart       │
                    │   ╱   AUTO_SAFE   ╲  Full Auto           │
                    │  ╱─────────────────╲                     │
                    │ ╱  AR-L1 / AR-L0    ╲  Manual / Notify   │
                    │╱_____________________╲  Human Decides    │
                    └──────────────────────────────────────────┘
```

- **저위험 수리**: 자동 실행 (재시도, 캐시 초기화, 서비스 재시작 등)
- **중위험 수리**: 자동 실행 + 사후 알림 (되돌릴 수 있는 변경만)
- **고위험 수리**: 스냅샷 생성 후 자동 실행 + 즉시 알림 (사전 승인 선택적)
- **금지 수리**: 절대 자동 수행 불가 (안전 규칙, 비용 상한, 승인 흐름 변경)

## 1.3 기존 시스템과의 통합 지점

SDAR는 독립적인 신규 시스템이 아니라, 기존 VAMOS 모듈과 긴밀하게 연결되어 동작한다.

| 기존 모듈 | SDAR와의 관계 | 연결 방식 |
|-----------|-------------|----------|
| **S-1 Self-check Engine** | SDAR에 "문제 신호" 제공 | S-1 → SDAR Layer 1 (DETECTION) 입력 |
| **S-4 Error Pattern Miner** | 반복 오류 패턴을 SDAR에 학습 데이터로 공급 | S-4 → SDAR Layer 2 (DIAGNOSIS) 패턴 DB |
| **I-6 Self-check Engine** | 출력 품질 검증 결과를 SDAR에 전달 | I-6 verdict → SDAR 트리거 |
| **I-16 Knowledge Search Engine** | 수리 지식 검색 (과거 수리 이력, Best Practice) | SDAR Layer 3 → I-16 쿼리 |
| **I-20 Failure/Fallback Manager** | 기존 Fallback 체계를 SDAR가 확장/보강 | I-20 → SDAR (실패 이벤트 라우팅) |
| **S-8 Self-evo Governance** | SDAR 수리 결과를 Self-evo 개선 후보로 전달 | SDAR Layer 5 → S-8 보고 |
| **I-19 Approval Manager** | MEDIUM/HIGH 수리 시 승인 요청 | SDAR Layer 4 → I-19 연동 |
| **I-8 Policy Engine** | 수리 액션의 정책 준수 여부 검증 | SDAR Layer 3 → I-8 PolicyCheck |

## 1.4 모듈 등록 정보

```
| ID   | 명칭                                 | status | change_lock | V1  | V2  | V3  |
|------|--------------------------------------|--------|-------------|-----|-----|-----|
| I-25 | Self-Diagnosis & Auto-Repair (SDAR)  | COND   | false       | OFF | COND| ON  |
```

- **V1**: OFF (I-20 Failure/Fallback Manager의 기본 Fallback으로만 운영)
- **V2**: COND (AR-L2 수준의 안전 자동수리만 조건부 활성화)
- **V3**: ON (AR-L3~AR-L4까지 단계적 확대, S-8 거버넌스 연동)

---

# 2. SDAR 아키텍처 (5-Layer Pipeline)

## 2.1 전체 구조

SDAR는 5개 계층(Layer)으로 구성된 진단-수리 파이프라인을 통해 동작한다. 각 계층은 독립적으로 실행 가능하되, 상위 계층의 출력이 하위 계층의 입력이 되는 순차적 흐름을 따른다.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SDAR 5-Layer Pipeline                            │
│                                                                     │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│  │ Layer 1  │──▶│ Layer 2  │──▶│ Layer 3  │──▶│ Layer 4  │──▶│ Layer 5  │
│  │DETECTION │   │DIAGNOSIS │   │PRESCRIPT.│   │ REPAIR   │   │VERIFICAT.│
│  │실시간 감지│   │근본원인분석│   │처방 생성  │   │수리 실행  │   │  검증    │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
│       │              │              │              │              │
│       ▼              ▼              ▼              ▼              ▼
│   HealthMon      RootCause       FixGen        Executor       Validator
│   ErrorDet       Classifier     RiskAssess     GradAuto       Regression
│   AnomalyDet    ImpactAssess    RepairPlan     Rollback       Rollback
│                                                                     │
│  ──────────────────── Event Bus (oc.sdar.*) ────────────────────── │
│  ──────────────────── LogEvent Sink ─────────────────────────────── │
└─────────────────────────────────────────────────────────────────────┘
         ▲                                              │
         │         ┌────────────────────┐               │
         └─────────│  Circuit Breaker   │◀──────────────┘
                   │  (기존 7.4 연동)    │
                   └────────────────────┘
```

## 2.2 Layer 1: DETECTION (실시간 감지)

### 목적
시스템 전반에서 발생하는 이상 신호를 실시간으로 감지하여 SDAR 파이프라인을 트리거한다.

### 3대 감지 채널

**Channel A: Health Monitoring (상태 모니터링)**
- 주기적 Health Check (기본 30초 간격, 설정 가능)
- 모니터링 대상:
  - DB 커넥션 상태 (SQLite/Postgres)
  - Vector DB 상태 (Chroma/Qdrant)
  - LLM API 응답성 (ping/latency 측정)
  - 디스크 용량 (임계치: 85% 경고, 95% 위험)
  - 메모리 사용률 (임계치: 80% 경고, 90% 위험)
  - MCP 서버 상태 (mcp.bridge.health 연동)
  - Rate Limit 잔여량 (분당 60회 중 잔여)

**Channel B: Error Pattern Detection (오류 패턴 감지)**
- I-20 Failure/Fallback Manager로부터 실패 이벤트 수신
- 기존 FailureCodeRegistry 20개 코드 실시간 추적
- 패턴 감지 규칙:
  - **빈도 기반**: 동일 failure_code가 5분 내 3회 이상 발생
  - **연쇄 기반**: 서로 다른 failure_code가 60초 내 연속 발생 (cascade 감지)
  - **시간대 기반**: 특정 시간대에 반복되는 오류 (cron 패턴)
- S-4 Error Pattern Miner의 학습된 패턴과 대조

**Channel C: Anomaly Detection (이상 탐지)**
- 정상 운영 기준선(baseline) 대비 편차 감지:
  - 응답 시간 급증 (baseline 대비 200% 초과)
  - Self-check score 급락 (최근 10건 평균 대비 30% 이상 하락)
  - QoD score 지속 저하 (이동 평균 < 0.5로 3회 연속)
  - 비용 소진 속도 이상 (예상 일일 소진율 대비 150% 초과)
  - 토큰 사용량 급증 (최근 1시간 평균 대비 300% 초과)

### Layer 1 출력: `SDARDetectionSignal`

```python
class SDARDetectionSignal(BaseModel):
    signal_id: str                    # UUID v4
    trace_id: str                     # 연관 trace_id
    detected_at: str                  # ISO8601 UTC
    channel: Literal["health", "error_pattern", "anomaly"]
    severity: Literal["info", "warn", "error", "critical"]
    source_module: str                # 감지 원점 모듈 (e.g., "I-20", "I-6")
    source_event: str                 # 원본 이벤트 (e.g., "oc.i2.fetch.failed")
    failure_code: Optional[str]       # 기존 FailureCode (있는 경우)
    metrics: dict                     # 감지 관련 수치 (latency, error_count 등)
    raw_context: dict                 # 감지 시점의 시스템 상태 스냅샷
```

### Layer 1 이벤트
- `oc.sdar.detection.started` — 감지 루프 시작
- `oc.sdar.detection.signal_emitted` — 이상 신호 발생
- `oc.sdar.detection.false_positive` — 오탐 판정 (Layer 2에서 역전파)

## 2.3 Layer 2: DIAGNOSIS (근본 원인 분석)

### 목적
Layer 1에서 수신한 감지 신호의 근본 원인(Root Cause)을 분석하고, 오류를 분류하며, 영향 범위를 평가한다.

### 3단계 진단 프로세스

**Step 2-1: Root Cause Analysis (근본 원인 분석)**
- **증상 → 원인 역추적**: 감지 신호로부터 원인 체인을 거슬러 올라감
- **분석 기법**:
  - **로그 상관 분석**: 동일 trace_id에 연결된 모든 LogEvent를 시간순 나열
  - **의존성 그래프 탐색**: 실패 모듈의 의존 관계를 따라가며 원인 탐색
  - **패턴 매칭**: S-4 Error Pattern Miner의 기존 패턴 DB와 비교
  - **시간적 상관관계**: 장애 발생 직전의 변경 사항 확인 (최근 config 변경, 모듈 업데이트 등)

**Step 2-2: Error Classification (오류 분류)**
- 5개 카테고리(CATEGORY A~E)로 분류 (Section 4 참조)
- 분류 결과에 따라 적용 가능한 AR-Level 결정

**Step 2-3: Impact Assessment (영향 범위 평가)**
- **Blast Radius** 산출:
  - `scope`: 영향받는 모듈 목록 (I-Series, S-Series, E-Series)
  - `user_impact`: 사용자 경험 영향도 (none / degraded / blocked / data_loss)
  - `data_risk`: 데이터 손상/손실 위험도 (none / low / medium / high / critical)
  - `propagation`: 연쇄 장애 가능성 (isolated / spreading / cascading)

### Layer 2 출력: `SDARDiagnosis`
(상세 스키마는 Section 8 참조)

### Layer 2 이벤트
- `oc.sdar.diagnosis.started` — 진단 시작
- `oc.sdar.diagnosis.root_cause_found` — 근본 원인 특정
- `oc.sdar.diagnosis.classified` — 오류 분류 완료
- `oc.sdar.diagnosis.impact_assessed` — 영향 범위 평가 완료
- `oc.sdar.diagnosis.completed` — 진단 완료
- `oc.sdar.diagnosis.failed` — 진단 실패 (원인 특정 불가)

## 2.4 Layer 3: PRESCRIPTION (처방 생성)

### 목적
진단 결과를 기반으로 수리 후보를 생성하고, 각 후보의 위험도를 평가하며, 최적의 수리 계획을 수립한다.

### 3단계 처방 프로세스

**Step 3-1: Fix Candidate Generation (수리 후보 생성)**
- **Repair Action Catalog** (Section 5)에서 적용 가능한 액션 검색
- **과거 수리 이력** 조회 (I-16 Knowledge Search Engine 연동)
- **다중 후보 생성**: 최소 1개, 최대 5개 후보 생성
- **우선순위 결정 기준**:
  1. 성공률 (과거 동일 패턴 수리 성공률)
  2. 위험도 (낮을수록 우선)
  3. 복구 시간 (빠를수록 우선)
  4. 비용 영향 (적을수록 우선)

**Step 3-2: Risk Assessment (위험도 평가)**
- 각 수리 후보에 대해:
  - `risk_level`: LOW / MEDIUM / HIGH / CRITICAL
  - `reversibility`: fully_reversible / partially_reversible / irreversible
  - `side_effects`: 예상 부작용 목록
  - `estimated_downtime`: 예상 수리 소요 시간
  - `required_ar_level`: 실행에 필요한 최소 AR-Level

**Step 3-3: Repair Plan Generation (수리 계획 수립)**
- 선택된 수리 후보를 실행 가능한 단계별 계획으로 구체화
- **Pre-conditions** (전제 조건): 수리 실행 전 충족되어야 할 조건
- **Repair Steps** (수리 단계): 순차적 실행 단계
- **Post-conditions** (사후 조건): 수리 성공 판정 기준
- **Rollback Plan** (롤백 계획): 실패 시 복원 절차
- **Verification Criteria** (검증 기준): Layer 5에서 사용할 검증 항목

### Layer 3 출력: `SDARRepairPlan`
(상세 스키마는 Section 8 참조)

### Layer 3 이벤트
- `oc.sdar.prescription.started` — 처방 생성 시작
- `oc.sdar.prescription.candidates_generated` — 후보 생성 완료
- `oc.sdar.prescription.risk_assessed` — 위험도 평가 완료
- `oc.sdar.prescription.plan_ready` — 수리 계획 수립 완료
- `oc.sdar.prescription.no_fix_available` — 적용 가능한 수리 없음

## 2.5 Layer 4: REPAIR (수리 실행)

### 목적
수리 계획을 단계적 자율수준(Graduated Autonomy)에 따라 실행한다. 이 계층이 SDAR의 핵심이며, AR-Level에 따른 실행 흐름이 달라진다.

### 실행 흐름 (AR-Level별)

```
┌──────────────────────────────────────────────────────┐
│               Layer 4: REPAIR 실행 흐름                │
│                                                       │
│  RepairPlan 수신                                      │
│       │                                               │
│       ▼                                               │
│  ┌─────────────────┐                                  │
│  │ AR-Level 확인    │                                  │
│  └────────┬────────┘                                  │
│           │                                           │
│     ┌─────┼─────┬──────────┬──────────┐              │
│     ▼     ▼     ▼          ▼          ▼              │
│  AR-L0  AR-L1  AR-L2     AR-L3     AR-L4            │
│  STOP   NOTIFY  AUTO      AUTO      AUTO             │
│  (log)  (suggest)(execute) (snap+    (snap+          │
│                            notify+   notify+         │
│                            execute)  execute)        │
│                                                       │
│  ※ AR-L2: 즉시 실행 (LOW risk only)                   │
│  ※ AR-L3: 스냅샷 → 실행 → 알림 (MEDIUM, reversible)   │
│  ※ AR-L4: 스냅샷 → [선택적 승인] → 실행 → 알림 (HIGH) │
└──────────────────────────────────────────────────────┘
```

**AR-L0 (MANUAL)**: 로그만 기록, 실행 안 함
**AR-L1 (NOTIFY_ONLY)**: 진단 + 수리 제안을 사용자에게 전달, 사용자가 직접 실행 결정
**AR-L2 (AUTO_SAFE)**: LOW risk 수리를 즉시 자동 실행 (retry, restart, cache clear 등)
**AR-L3 (AUTO_MODERATE)**: MEDIUM risk까지 자동 실행 (reversible only) + 즉시 알림
**AR-L4 (AUTO_AGGRESSIVE)**: HIGH risk까지 자동 실행 (스냅샷 필수) + 즉시 알림

### 수리 실행 절차 (공통)

1. **Pre-flight Check**: 전제 조건 확인, 현재 시스템 상태 재검증
2. **Snapshot** (MEDIUM/HIGH): 수리 대상 시스템 상태 스냅샷 저장
3. **Execute**: 수리 액션 순차 실행
4. **Monitor**: 실행 중 실시간 모니터링 (타임아웃, 이상 감지)
5. **Result Capture**: 실행 결과 수집
6. **Notification**: AR-Level에 따른 알림 발송

### Layer 4 출력: `SDARRepairResult`
(상세 스키마는 Section 8 참조)

### Layer 4 이벤트
- `oc.sdar.repair.started` — 수리 실행 시작
- `oc.sdar.repair.snapshot_created` — 스냅샷 생성 완료
- `oc.sdar.repair.approval_requested` — 승인 요청 (AR-L4 시)
- `oc.sdar.repair.step_completed` — 개별 단계 완료
- `oc.sdar.repair.succeeded` — 수리 성공
- `oc.sdar.repair.failed` — 수리 실패
- `oc.sdar.repair.rollback_triggered` — 롤백 시작

## 2.6 Layer 5: VERIFICATION (검증)

### 목적
수리 결과를 검증하고, 회귀(regression)가 없는지 확인하며, 필요 시 롤백을 트리거한다.

### 3단계 검증 프로세스

**Step 5-1: Post-Repair Validation (수리 후 검증)**
- 수리 계획의 `post_conditions`가 모두 충족되는지 확인
- 수리 대상 모듈의 Health Check 재실행
- 수리로 인해 해결되어야 할 원래 오류가 재현되지 않는지 확인

**Step 5-2: Regression Check (회귀 검사)**
- 수리 영향 범위(Blast Radius) 내 모든 모듈의 상태 확인
- 수리 전후 성능 지표 비교:
  - 응답 시간 변화
  - Self-check score 변화
  - QoD score 변화
  - 에러율 변화
- 새로운 오류가 발생하지 않았는지 확인 (5분 관찰 기간)

**Step 5-3: Rollback Trigger (롤백 판정)**
- 롤백 트리거 조건 (하나라도 해당되면 자동 롤백):
  - `post_conditions` 미충족
  - 수리 후 새로운 `error`/`critical` 심각도 이벤트 발생
  - Self-check score가 수리 전보다 하락
  - 사용자가 수동 롤백 명령 발행
- 롤백 실행:
  - MEDIUM/HIGH 수리: 스냅샷에서 복원
  - LOW 수리: 역동작 실행 (e.g., 재시작한 서비스 원상복구)

### Layer 5 출력: `SDARVerificationResult`

```python
class SDARVerificationResult(BaseModel):
    verification_id: str              # UUID v4
    repair_result_ref: str            # SDARRepairResult.result_id 참조
    trace_id: str
    verified_at: str                  # ISO8601 UTC
    post_condition_results: List[dict] # {condition, passed: bool, detail}
    regression_check: dict            # {passed: bool, metrics_before, metrics_after, new_errors}
    verdict: Literal["PASS", "WARN", "FAIL"]
    rollback_triggered: bool
    rollback_result: Optional[dict]   # 롤백 실행 시 결과
    observation_period_s: int         # 관찰 기간 (초)
    recommendations: List[str]       # 후속 조치 권고
```

### Layer 5 이벤트
- `oc.sdar.verification.started` — 검증 시작
- `oc.sdar.verification.passed` — 검증 통과
- `oc.sdar.verification.warned` — 경고 (부분적 문제)
- `oc.sdar.verification.failed` — 검증 실패
- `oc.sdar.verification.rollback_executed` — 롤백 실행 완료
- `oc.sdar.verification.completed` — 검증 프로세스 종료

---

# 3. 단계적 자율 모델 (Graduated Autonomy Model)

## 3.1 Auto-Repair Level 정의

SDAR의 핵심인 단계적 자율 모델은 5개 수준으로 구성된다. 이는 기존 VAMOS Autonomy Level(L0~L3)과 병렬적으로 동작하되, **수리(Repair) 행위에 특화**된 세분화된 자율 수준이다.

| Level | 명칭 | 자동수리 범위 | 승인 방식 | 예시 | 알림 |
|-------|------|-------------|----------|------|------|
| **AR-L0** | MANUAL | 수리 안 함 | 모든 수리에 인간 개입 필요 | 전체 수동 운영 시 | 로그만 기록 |
| **AR-L1** | NOTIFY_ONLY | 진단 + 제안까지만 | 인간이 최종 결정 | "Config 오류 감지, 수정안 제시" | UI 알림 + 제안 |
| **AR-L2** | AUTO_SAFE | LOW risk 자동 수리 | LOW risk는 자동, 나머지 인간 | retry, restart, cache clear, model switch | 사후 요약 알림 |
| **AR-L3** | AUTO_MODERATE | MEDIUM risk까지 자동 | reversible만 자동 + 즉시 알림 | prompt patch, config adjust, rate limit, index rebuild | 즉시 알림 + 상세 |
| **AR-L4** | AUTO_AGGRESSIVE | HIGH risk까지 자동 | 스냅샷 필수 + 자동 + 즉시 알림 | code hotfix, schema migration, dependency reinstall | 긴급 알림 + 롤백 가능 |

**시스템 기본값: AR-L2 (AUTO_SAFE)**

이 기본값은 기존 VAMOS Autonomy Level의 기본값인 L1(SUPERVISED)과 철학적으로 일치한다. "안전한 것은 자동으로, 위험한 것은 확인 후"라는 원칙을 수리 영역에 적용한 것이다.

## 3.2 AR-Level과 기존 Autonomy Level 매핑

SDAR의 AR-Level은 기존 VAMOS Autonomy Level에 의해 상한이 제한된다.

| VAMOS Autonomy | 허용 가능한 최대 AR-Level | 제약 |
|---------------|------------------------|------|
| **L0 (FULL_MANUAL)** | AR-L0 | 수리 불가, 감지/진단만 |
| **L1 (SUPERVISED)** | **AR-L2** (기본값) | LOW risk만 자동 |
| **L2 (SEMI_AUTO)** | AR-L3 | MEDIUM까지 자동 |
| **L3 (FULL_AUTO)** | AR-L4 | HIGH까지 자동 (NEVER_AUTO 제외) |

**핵심 제약**: VAMOS Autonomy Level이 L3(FULL_AUTO)라 하더라도, NEVER_AUTO로 지정된 수리 액션(safety_rules, cost_ceiling, approval_flow, non_goals 변경)은 **절대** 자동 실행할 수 없다.

## 3.3 AR-Level 전환 규칙

AR-Level은 사용자가 명시적으로 설정하며, 자동 상승은 금지된다.

```python
class SDARConfig(BaseModel):
    """SDAR 전역 설정"""
    ar_level: Literal["AR-L0", "AR-L1", "AR-L2", "AR-L3", "AR-L4"] = "AR-L2"
    max_auto_repairs_per_hour: int = 3          # 시간당 최대 자동 수리 횟수
    observation_period_s: int = 300             # 수리 후 관찰 기간 (5분)
    snapshot_retention_hours: int = 168         # 스냅샷 보존 기간 (7일)
    notification_channel: Literal["ui", "log", "both"] = "both"
    emergency_kill_switch: bool = False         # True 시 SDAR 전체 비활성화

    model_config = ConfigDict(extra="forbid")
```

**AR-Level 변경 시 규칙**:
1. 상승: ADMIN 이상 권한 필요, I-19 Approval Manager를 통한 승인 후 적용
2. 하락: OPERATOR 이상 권한으로 즉시 적용 가능
3. Emergency Kill Switch: 모든 권한 수준에서 즉시 활성화 가능 (SDAR 전체 정지)
4. AR-L4 설정: OWNER 권한 필수

## 3.4 RBAC과 AR-Level

| RBAC 역할 | 설정 가능한 AR-Level | Emergency Kill Switch |
|----------|--------------------|--------------------|
| **OWNER** | AR-L0 ~ AR-L4 | O |
| **ADMIN** | AR-L0 ~ AR-L3 | O |
| **OPERATOR** | AR-L0 ~ AR-L2 | O |
| **VIEWER** | 변경 불가 (조회만) | O (비상 정지만) |

## 3.5 알림 체계

모든 SDAR 활동은 알림을 생성하며, AR-Level에 따라 알림 수준이 달라진다.

| AR-Level | 감지 시 | 진단 완료 시 | 수리 실행 시 | 수리 완료 시 |
|----------|---------|------------|------------|------------|
| AR-L0 | 로그 기록 | 로그 기록 | N/A | N/A |
| AR-L1 | 로그 기록 | UI 팝업 + 수리 제안 | N/A (사용자 실행) | N/A |
| AR-L2 | 로그 기록 | 로그 기록 | 자동 실행 | 사후 요약 알림 |
| AR-L3 | 로그 기록 | 로그 기록 | 즉시 알림 + 자동 실행 | 즉시 상세 알림 |
| AR-L4 | 로그 기록 | 즉시 경고 | 긴급 알림 + 자동 실행 | 긴급 상세 알림 + 롤백 옵션 |

---

# 4. 오류 분류 체계 (Error Classification System)

## 4.1 5대 오류 카테고리

SDAR는 VAMOS 시스템에서 발생 가능한 모든 오류를 5개 카테고리로 분류한다. 각 카테고리마다 자동수리 가능 여부와 적용 가능한 AR-Level이 정의된다.

### CATEGORY A: Infrastructure (인프라 오류)

인프라 계층(DB, API, 네트워크, 디스크, 프로세스)에서 발생하는 오류. **대부분 자동수리 가능**.

| 오류 코드 | 설명 | 위험도 | 자동수리 AR-Level | 수리 액션 |
|----------|------|--------|------------------|----------|
| `SDAR_A01_DB_CONN_LOST` | DB 커넥션 끊김 | LOW | AR-L2 | `restart_service`, `retry_with_backoff` |
| `SDAR_A02_DB_TIMEOUT` | DB 쿼리 타임아웃 | LOW | AR-L2 | `retry_with_backoff`, `clear_cache` |
| `SDAR_A03_DB_CORRUPT` | DB 데이터 손상 | HIGH | AR-L4 | `rollback_to_snapshot` |
| `SDAR_A04_API_429` | LLM API Rate Limit 초과 | LOW | AR-L2 | `retry_with_backoff`, `switch_model_fallback` |
| `SDAR_A05_API_5XX` | LLM API 서버 오류 | LOW | AR-L2 | `retry_with_backoff`, `switch_model_fallback` |
| `SDAR_A06_API_AUTH_FAIL` | API 인증 실패 | MEDIUM | AR-L3 | `rotate_api_key` |
| `SDAR_A07_DISK_FULL` | 디스크 용량 부족 | MEDIUM | AR-L3 | `clear_cache`, `compress_logs` |
| `SDAR_A08_MEMORY_OOM` | 메모리 부족 | MEDIUM | AR-L3 | `restart_service`, `clear_cache` |
| `SDAR_A09_PROCESS_CRASH` | 프로세스 크래시 | LOW | AR-L2 | `restart_service` |
| `SDAR_A10_NETWORK_UNREACHABLE` | 네트워크 불통 | LOW | AR-L2 | `retry_with_backoff`, `switch_model_fallback` |
| `SDAR_A11_VECTOR_DB_DOWN` | Vector DB 장애 | MEDIUM | AR-L3 | `restart_service`, `rebuild_vector_index` |
| `SDAR_A12_MCP_SERVER_DOWN` | MCP 서버 응답 없음 | LOW | AR-L2 | `restart_service`, `retry_with_backoff` |

### CATEGORY B: Model/AI (모델/AI 오류)

LLM 응답 품질, 라우팅, 할루시네이션 관련 오류.

| 오류 코드 | 설명 | 위험도 | 자동수리 AR-Level | 수리 액션 |
|----------|------|--------|------------------|----------|
| `SDAR_B01_HALLUCINATION` | 할루시네이션 감지 | MEDIUM | AR-L3 | `switch_model_fallback`, `patch_prompt_template` |
| `SDAR_B02_QUALITY_DEGRADATION` | 출력 품질 저하 | MEDIUM | AR-L3 | `switch_model_fallback`, `patch_prompt_template` |
| `SDAR_B03_ROUTING_FAILURE` | 모델 라우팅 실패 | LOW | AR-L2 | `switch_model_fallback` |
| `SDAR_B04_SELFCHECK_FAIL` | Self-check 지속 실패 | MEDIUM | AR-L3 | `switch_model_fallback`, `patch_prompt_template` |
| `SDAR_B05_QOD_COLLAPSE` | QoD 점수 급락 | MEDIUM | AR-L3 | `rebuild_vector_index`, `clear_cache` |
| `SDAR_B06_TOKEN_EXPLOSION` | 토큰 사용량 폭증 | MEDIUM | AR-L3 | `adjust_rate_limit`, `patch_prompt_template` |
| `SDAR_B07_EMBEDDING_DRIFT` | 임베딩 품질 저하 | HIGH | AR-L4 | `rebuild_vector_index` |
| `SDAR_B08_CONTEXT_OVERFLOW` | 컨텍스트 윈도우 초과 | LOW | AR-L2 | `clear_cache`, `patch_prompt_template` |

### CATEGORY C: Logic (로직 오류)

워크플로우, Gate 설정, 스키마 관련 오류.

| 오류 코드 | 설명 | 위험도 | 자동수리 AR-Level | 수리 액션 |
|----------|------|--------|------------------|----------|
| `SDAR_C01_WORKFLOW_STUCK` | 워크플로우 교착 상태 | MEDIUM | AR-L3 | `restart_service`, `update_config_parameter` |
| `SDAR_C02_GATE_MISCONFIGURED` | Gate 설정 오류 | HIGH | AR-L4 (주의) | `update_config_parameter` |
| `SDAR_C03_SCHEMA_MISMATCH` | 스키마 불일치 | HIGH | AR-L4 | `migrate_schema` |
| `SDAR_C04_STATE_INCONSISTENCY` | 상태 머신 불일치 | MEDIUM | AR-L3 | `restart_service`, `update_config_parameter` |
| `SDAR_C05_LOOP_DETECTED` | 무한 루프 감지 | MEDIUM | AR-L3 | `restart_service` |
| `SDAR_C06_PIPELINE_BROKEN` | 파이프라인 단절 | HIGH | AR-L4 | `restart_service`, `update_config_parameter` |

### CATEGORY D: Code (코드 오류)

버그, 회귀, 의존성 관련 오류.

| 오류 코드 | 설명 | 위험도 | 자동수리 AR-Level | 수리 액션 |
|----------|------|--------|------------------|----------|
| `SDAR_D01_BUG_DETECTED` | 코드 버그 감지 | HIGH | AR-L4 | `patch_code_hotfix` |
| `SDAR_D02_REGRESSION` | 회귀 버그 | HIGH | AR-L4 | `rollback_to_snapshot`, `patch_code_hotfix` |
| `SDAR_D03_DEPENDENCY_BREAK` | 의존성 깨짐 | HIGH | AR-L4 | `reinstall_dependency` |
| `SDAR_D04_IMPORT_ERROR` | 모듈 임포트 실패 | MEDIUM | AR-L3 | `reinstall_dependency` |
| `SDAR_D05_TYPE_ERROR` | 타입 불일치 | HIGH | AR-L4 | `patch_code_hotfix` |
| `SDAR_D06_CONFIG_SYNTAX_ERROR` | 설정 파일 구문 오류 | MEDIUM | AR-L3 | `update_config_parameter` |

### CATEGORY E: Security (보안 오류)

보안 관련 오류. **절대 자동수리 금지 (NEVER_AUTO)**.

| 오류 코드 | 설명 | 위험도 | 자동수리 AR-Level | 대응 |
|----------|------|--------|------------------|------|
| `SDAR_E01_INJECTION_DETECTED` | 프롬프트 인젝션 감지 | CRITICAL | **NEVER_AUTO** | 즉시 차단 + 인간 알림 |
| `SDAR_E02_UNAUTHORIZED_ACCESS` | 무단 접근 시도 | CRITICAL | **NEVER_AUTO** | 즉시 차단 + 인간 알림 |
| `SDAR_E03_DATA_BREACH` | 데이터 유출 감지 | CRITICAL | **NEVER_AUTO** | 즉시 차단 + 인간 알림 |
| `SDAR_E04_PRIVILEGE_ESCALATION` | 권한 상승 시도 | CRITICAL | **NEVER_AUTO** | 즉시 차단 + 인간 알림 |
| `SDAR_E05_SAFETY_BYPASS` | 안전 필터 우회 시도 | CRITICAL | **NEVER_AUTO** | 즉시 차단 + 인간 알림 |
| `SDAR_E06_PII_EXPOSURE` | PII 노출 감지 | CRITICAL | **NEVER_AUTO** | 즉시 마스킹 + 인간 알림 |

## 4.2 카테고리별 AR-Level 매핑 요약

```
┌──────────────────────────────────────────────────────────────┐
│           카테고리 × AR-Level 자동수리 허용 매트릭스            │
│                                                              │
│              AR-L0   AR-L1   AR-L2   AR-L3   AR-L4          │
│  CAT-A(Infra)  --    제안    LOW     MED     HIGH           │
│  CAT-B(Model)  --    제안    LOW     MED     HIGH           │
│  CAT-C(Logic)  --    제안     --     MED     HIGH           │
│  CAT-D(Code)   --    제안     --      --     HIGH           │
│  CAT-E(Sec)    --    제안     --      --     NEVER          │
│                                                              │
│  -- = 수리 안 함  /  제안 = 진단 결과만 알림                    │
│  LOW/MED/HIGH = 해당 위험도까지 자동수리 허용                   │
│  NEVER = 어떤 AR-Level에서도 자동수리 금지                     │
└──────────────────────────────────────────────────────────────┘
```

---

# 5. 수리 액션 카탈로그 (Repair Action Catalog)

## 5.1 전체 수리 액션 목록

모든 수리 액션은 고유 ID, 위험도, 필요 AR-Level, 적용 카테고리, 되돌림 가능 여부를 가진다.

### LOW Risk 수리 액션

| 액션 ID | 명칭 | 설명 | 최소 AR-Level | 되돌림 | 적용 카테고리 | 예상 소요 시간 |
|---------|------|------|-------------|--------|------------|-------------|
| `RA_001` | `restart_service` | 대상 서비스/프로세스 재시작 | AR-L2 | fully_reversible | A, C | 10~60초 |
| `RA_002` | `clear_cache` | 응답 캐시/Semantic Cache 초기화 | AR-L2 | fully_reversible | A, B | 5~10초 |
| `RA_003` | `retry_with_backoff` | 지수 백오프로 재시도 (1초/2초/4초, max 3회) | AR-L2 | fully_reversible | A | 1~12초 |
| `RA_004` | `switch_model_fallback` | 대체 모델로 전환 (GPT-4o→Claude→Ollama) | AR-L2 | fully_reversible | A, B | 5~15초 |
| `RA_005` | `adjust_rate_limit` | Rate Limit 임시 조정 (하향만 자동) | AR-L2 | fully_reversible | A, B | 즉시 |

### MEDIUM Risk 수리 액션

| 액션 ID | 명칭 | 설명 | 최소 AR-Level | 되돌림 | 적용 카테고리 | 예상 소요 시간 |
|---------|------|------|-------------|--------|------------|-------------|
| `RA_006` | `patch_prompt_template` | 프롬프트 템플릿 수정 (S-3 Template Evolution 연동) | AR-L3 | fully_reversible | B | 10~30초 |
| `RA_007` | `update_config_parameter` | 설정 파라미터 변경 (config.yaml 수정) | AR-L3 | fully_reversible | A, C, D | 5~15초 |
| `RA_008` | `rotate_api_key` | API 키 갱신 (보안 저장소에서 교체) | AR-L3 | partially_reversible | A | 15~60초 |
| `RA_009` | `rollback_to_snapshot` | 스냅샷으로 복원 (기존 6.6 Backup/Recovery 연동) | AR-L3 | fully_reversible | A, C, D | 30초~5분 |
| `RA_010` | `compress_logs` | 오래된 JSONL 로그 압축/삭제 | AR-L3 | partially_reversible | A | 30초~2분 |

### HIGH Risk 수리 액션

| 액션 ID | 명칭 | 설명 | 최소 AR-Level | 되돌림 | 적용 카테고리 | 예상 소요 시간 |
|---------|------|------|-------------|--------|------------|-------------|
| `RA_011` | `patch_code_hotfix` | 코드 핫픽스 적용 (제한적 범위) | AR-L4 | partially_reversible | D | 30초~5분 |
| `RA_012` | `migrate_schema` | DB 스키마 마이그레이션 | AR-L4 | partially_reversible | C, D | 1~10분 |
| `RA_013` | `reinstall_dependency` | Python/npm 의존성 재설치 | AR-L4 | partially_reversible | D | 1~5분 |
| `RA_014` | `rebuild_vector_index` | Vector DB 인덱스 재구축 | AR-L4 | fully_reversible | A, B | 5~30분 |

### NEVER_AUTO 수리 액션 (절대 자동 실행 금지)

| 액션 ID | 명칭 | 설명 | 사유 |
|---------|------|------|------|
| `RA_NEVER_01` | `modify_safety_rules` | 안전 규칙 변경 | 7개 불변 구역 (LOCK) |
| `RA_NEVER_02` | `change_cost_ceiling` | 비용 상한 변경 | 7개 불변 구역 (LOCK) |
| `RA_NEVER_03` | `alter_approval_flow` | 승인 흐름 변경 | 7개 불변 구역 (LOCK) |
| `RA_NEVER_04` | `modify_non_goals` | Non-goal 목록 변경 | 7개 불변 구역 (LOCK) |
| `RA_NEVER_05` | `change_audit_format` | 감사 로그 형식 변경 | 7개 불변 구역 (LOCK) |
| `RA_NEVER_06` | `alter_data_retention` | 데이터 보존 정책 변경 | 7개 불변 구역 (LOCK) |
| `RA_NEVER_07` | `modify_user_consent` | 사용자 동의 설정 변경 | 7개 불변 구역 (LOCK) |
| `RA_NEVER_08` | `escalate_own_privilege` | SDAR 자체 권한 상승 | RBAC 원칙 위반 |
| `RA_NEVER_09` | `disable_guardrails` | Guardrails 비활성화 | 안전 Fail-safe 원칙 위반 |
| `RA_NEVER_10` | `bypass_gate` | Gate 우회 | Gate 우회 불가 (LOCK) |

## 5.2 수리 액션 스키마

```python
class RepairAction(BaseModel):
    """수리 액션 카탈로그 항목"""
    action_id: str                     # RA_001 ~ RA_014, RA_NEVER_01 ~ RA_NEVER_10
    action_name: str                   # e.g., "restart_service"
    description: str                   # 액션 설명
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    min_ar_level: Literal["AR-L2", "AR-L3", "AR-L4", "NEVER_AUTO"]
    reversibility: Literal["fully_reversible", "partially_reversible", "irreversible"]
    applicable_categories: List[Literal["A", "B", "C", "D", "E"]]
    requires_snapshot: bool            # MEDIUM/HIGH는 True
    estimated_duration_s: int          # 예상 소요 시간 (초)
    max_retries: int = 1              # 액션 자체의 최대 재시도 횟수
    cooldown_s: int = 60              # 동일 액션 반복 실행 간 최소 대기 시간
    pre_conditions: List[str]         # 실행 전제 조건
    side_effects: List[str]           # 예상 부작용

    model_config = ConfigDict(extra="forbid")
```

## 5.3 수리 액션 실행 규칙

1. **동일 이슈 동일 액션 반복 제한**: 동일 issue에 대해 동일 액션은 `cooldown_s` 내 재실행 금지
2. **스냅샷 의무**: `requires_snapshot == True`인 액션은 스냅샷 생성 성공 후에만 실행
3. **NEVER_AUTO 절대 금지**: `min_ar_level == "NEVER_AUTO"`인 액션은 어떤 AR-Level에서도 자동 실행 불가. 코드 레벨에서 하드코딩 차단.
4. **Side Effect 공개**: 모든 수리 액션의 `side_effects`는 알림 메시지에 반드시 포함
5. **타임아웃**: 각 수리 액션은 `estimated_duration_s * 3`을 타임아웃으로 적용. 초과 시 강제 중단 + 롤백

---

# 6. 기존 VAMOS 시스템 통합

## 6.1 5 Gates와의 통합

SDAR는 수리 액션 실행 전 기존 Gate 시스템을 반드시 통과해야 한다. Gate 우회는 절대 불가(LOCK).

| Gate | SDAR 연동 방식 | 적용 시점 |
|------|--------------|---------|
| **PolicyGate** | 수리 액션이 Non-goal 위반 여부 확인, P2 관련 수리 시 재확인 | Layer 3 (처방 생성 시) + Layer 4 (실행 전) |
| **CostGate** | 수리로 인한 추가 비용 발생 여부 확인 (e.g., 모델 전환 시 비용 증가) | Layer 3 (처방 생성 시) |
| **ApprovalGate** | AR-L3/L4 수리 시 승인 필요 여부 확인, P2 관련 수리 시 반드시 승인 | Layer 4 (실행 전) |
| **EvidenceGate** | 진단 근거의 충분성 확인 (근거 없는 수리 방지) | Layer 2 (진단 완료 시) |
| **SelfCheckGate** | 수리 후 Self-check 재실행하여 품질 확인 | Layer 5 (검증 시) |

### Gate 통과 흐름

```
Layer 3 (PRESCRIPTION)
    │
    ├──▶ PolicyGate: 수리 액션이 정책 위반하는가?
    │       ├── deny → 해당 수리 후보 제거
    │       ├── restrict → 승인 필요 플래그 설정
    │       └── allow → 통과
    │
    ├──▶ CostGate: 수리로 추가 비용 발생하는가?
    │       ├── stop → 수리 포기 (비용 초과)
    │       ├── downshift → 저비용 대안 검색
    │       └── normal → 통과
    │
    └──▶ EvidenceGate: 진단 근거가 충분한가?
            ├── insufficient → 추가 진단 필요
            └── sufficient → 통과

Layer 4 (REPAIR)
    │
    └──▶ ApprovalGate: 승인이 필요한 수리인가?
            ├── pending → 사용자 승인 대기 (타임아웃: 10분)
            ├── denied → 수리 취소
            └── approved → 실행 진행

Layer 5 (VERIFICATION)
    │
    └──▶ SelfCheckGate: 수리 후 품질이 유지되는가?
            ├── FAIL → 롤백 트리거
            ├── WARN → 알림 + 관찰 연장
            └── PASS → 수리 완료 확정
```

## 6.2 S-8 Self-evo Governance 보고

SDAR의 모든 수리 활동은 S-8 Self-evo Governance에 보고된다. 이를 통해:

1. **학습 데이터 축적**: 성공/실패한 수리 이력이 S-4 Error Pattern Miner에 피드백
2. **수리 패턴 진화**: 반복적으로 성공하는 수리 패턴은 S-3 Template Evolution에 의해 최적화
3. **거버넌스 감사**: 모든 자동수리가 정책/비용/승인 규칙을 준수했는지 사후 감사

### SDAR → S-8 보고 형식

```python
class SDARGovernanceReport(BaseModel):
    """S-8에 전달되는 SDAR 거버넌스 보고"""
    report_id: str                     # UUID v4
    period_start: str                  # ISO8601 UTC
    period_end: str                    # ISO8601 UTC
    total_detections: int              # 총 감지 건수
    total_diagnoses: int               # 총 진단 건수
    total_repairs_attempted: int       # 총 수리 시도 건수
    total_repairs_succeeded: int       # 총 수리 성공 건수
    total_repairs_failed: int          # 총 수리 실패 건수
    total_rollbacks: int               # 총 롤백 건수
    ar_level_used: str                 # 적용된 AR-Level
    policy_violations: int             # 정책 위반 감지 건수
    cost_impact_total: float           # 수리로 인한 총 비용 변동
    top_error_codes: List[dict]        # 빈도 상위 오류 코드 [{code, count}]
    improvement_suggestions: List[str] # S-8에 대한 개선 제안
```

## 6.3 Circuit Breaker 통합

SDAR는 기존 Circuit Breaker (Section 7.4)와 양방향으로 통합된다.

### Circuit Breaker → SDAR
- Circuit Breaker가 **OPEN** 상태로 전환될 때, SDAR에 `SDARDetectionSignal` 발행
- SDAR가 근본 원인을 진단하고 수리를 시도

### SDAR → Circuit Breaker
- SDAR 수리 성공 후, Circuit Breaker를 **HALF-OPEN**으로 전환 시도
- 수리 후 검증(Layer 5) 통과 시, Circuit Breaker를 **CLOSED**로 복원

### P2 도메인 특별 규칙
- P2 이상 모듈의 Circuit Breaker가 OPEN일 때:
  - SDAR는 진단까지만 자동 수행
  - 수리 및 Circuit Breaker 복원은 **반드시 인간 승인** 필요 (AR-Level 무관)

```
┌─────────────────────────────────────────────────┐
│         Circuit Breaker × SDAR 통합 흐름          │
│                                                   │
│  CLOSED ──(연속 3회 실패)──▶ OPEN                  │
│    ▲                          │                   │
│    │                          ▼                   │
│    │                    SDAR 감지 (Layer 1)        │
│    │                          │                   │
│    │                    SDAR 진단 (Layer 2)        │
│    │                          │                   │
│    │                    SDAR 수리 (Layer 3~4)      │
│    │                          │                   │
│    │   ┌───(P2: 승인 필요)────┤                   │
│    │   │                      │                   │
│    │   ▼                      ▼                   │
│    │  HALF-OPEN ◀── SDAR 검증 통과 (Layer 5)      │
│    │     │                                        │
│    │     │──(시도 성공)──▶ CLOSED                   │
│    │     │──(시도 실패)──▶ OPEN (SDAR 재시작)       │
│    └─────────────────────────────────────────────┘
```

## 6.4 LogEvent 시스템 통합

SDAR의 모든 이벤트는 기존 LogEvent 스키마(Section 12.6)를 따른다.

### SDAR 이벤트 타입 (EventTypeRegistry 확장)

```
# Layer 1: Detection
oc.sdar.detection.started
oc.sdar.detection.signal_emitted
oc.sdar.detection.false_positive

# Layer 2: Diagnosis
oc.sdar.diagnosis.started
oc.sdar.diagnosis.root_cause_found
oc.sdar.diagnosis.classified
oc.sdar.diagnosis.impact_assessed
oc.sdar.diagnosis.completed
oc.sdar.diagnosis.failed

# Layer 3: Prescription
oc.sdar.prescription.started
oc.sdar.prescription.candidates_generated
oc.sdar.prescription.risk_assessed
oc.sdar.prescription.plan_ready
oc.sdar.prescription.no_fix_available

# Layer 4: Repair
oc.sdar.repair.started
oc.sdar.repair.snapshot_created
oc.sdar.repair.approval_requested
oc.sdar.repair.step_completed
oc.sdar.repair.succeeded
oc.sdar.repair.failed
oc.sdar.repair.rollback_triggered

# Layer 5: Verification
oc.sdar.verification.started
oc.sdar.verification.passed
oc.sdar.verification.warned
oc.sdar.verification.failed
oc.sdar.verification.rollback_executed
oc.sdar.verification.completed

# 전역
oc.sdar.config.changed
oc.sdar.kill_switch.activated
oc.sdar.kill_switch.deactivated
```

### SDAR Failure Code (FailureCodeRegistry 확장)

```
# SDAR 내부 실패 코드
SDAR_DETECTION_TIMEOUT          # 감지 루프 타임아웃
SDAR_DIAGNOSIS_FAILED           # 진단 실패 (원인 특정 불가)
SDAR_PRESCRIPTION_NO_FIX        # 적용 가능한 수리 없음
SDAR_PRESCRIPTION_POLICY_BLOCK  # 정책에 의해 수리 차단
SDAR_PRESCRIPTION_COST_BLOCK    # 비용에 의해 수리 차단
SDAR_REPAIR_TIMEOUT             # 수리 실행 타임아웃
SDAR_REPAIR_FAILED              # 수리 실행 실패
SDAR_REPAIR_APPROVAL_DENIED     # 수리 승인 거부
SDAR_REPAIR_APPROVAL_TIMEOUT    # 수리 승인 타임아웃 (10분)
SDAR_VERIFICATION_FAILED        # 수리 후 검증 실패
SDAR_ROLLBACK_FAILED            # 롤백 실패 (긴급 인간 개입 필요)
SDAR_MAX_ATTEMPTS_EXCEEDED      # 시간당 최대 수리 횟수 초과
SDAR_KILL_SWITCH_ACTIVE         # Kill Switch 활성화로 전체 정지
```

### SDAR Fallback (FallbackRegistry 확장)

| fallback_id | 목표 | 주요 트리거 |
|------------|------|-----------|
| `FB_SDAR_MANUAL_ESCALATION` | 안전 | 자동수리 실패/불가 시 인간에게 에스컬레이션 |
| `FB_SDAR_DEGRADE_AR_LEVEL` | 안전 | 수리 실패 시 AR-Level 1단계 하향 |
| `FB_SDAR_RETRY_DIAGNOSIS` | 정확도 | 진단 불완전 시 추가 정보 수집 후 재진단 |
| `FB_SDAR_SNAPSHOT_ROLLBACK` | 안전 | 수리 후 검증 실패 시 스냅샷 복원 |

### SDAR Failure → Fallback 매핑

| failure_code | fallback_id |
|---|---|
| `SDAR_DIAGNOSIS_FAILED` | `FB_SDAR_RETRY_DIAGNOSIS` |
| `SDAR_PRESCRIPTION_NO_FIX` | `FB_SDAR_MANUAL_ESCALATION` |
| `SDAR_PRESCRIPTION_POLICY_BLOCK` | `FB_SDAR_MANUAL_ESCALATION` |
| `SDAR_PRESCRIPTION_COST_BLOCK` | `FB_SDAR_DEGRADE_AR_LEVEL` |
| `SDAR_REPAIR_FAILED` | `FB_SDAR_SNAPSHOT_ROLLBACK` |
| `SDAR_REPAIR_APPROVAL_DENIED` | `FB_SDAR_MANUAL_ESCALATION` |
| `SDAR_REPAIR_APPROVAL_TIMEOUT` | `FB_SDAR_MANUAL_ESCALATION` |
| `SDAR_VERIFICATION_FAILED` | `FB_SDAR_SNAPSHOT_ROLLBACK` |
| `SDAR_ROLLBACK_FAILED` | `FB_SDAR_MANUAL_ESCALATION` |
| `SDAR_MAX_ATTEMPTS_EXCEEDED` | `FB_SDAR_MANUAL_ESCALATION` |

## 6.5 Monorepo 프로젝트 구조 확장

기존 프로젝트 구조(Section 14)에 SDAR 모듈을 추가한다.

```
vamos/
├── backend/
│   └── vamos_core/
│       ├── orange_core/         # 기존
│       ├── blue_nodes/          # 기존
│       ├── infra/               # 기존
│       ├── agent/               # 기존
│       ├── storage/             # 기존
│       ├── safety/              # 기존
│       ├── schemas/             # 기존 (SDAR 스키마 추가)
│       ├── mcp/                 # 기존
│       └── sdar/                # ★ 신규: SDAR 모듈
│           ├── __init__.py
│           ├── config.py              # SDARConfig
│           ├── detection/             # Layer 1
│           │   ├── health_monitor.py
│           │   ├── error_pattern_detector.py
│           │   └── anomaly_detector.py
│           ├── diagnosis/             # Layer 2
│           │   ├── root_cause_analyzer.py
│           │   ├── error_classifier.py
│           │   └── impact_assessor.py
│           ├── prescription/          # Layer 3
│           │   ├── fix_generator.py
│           │   ├── risk_assessor.py
│           │   └── plan_builder.py
│           ├── repair/                # Layer 4
│           │   ├── executor.py
│           │   ├── graduated_autonomy.py
│           │   ├── snapshot_manager.py
│           │   └── actions/           # 개별 수리 액션 구현
│           │       ├── restart_service.py
│           │       ├── clear_cache.py
│           │       ├── retry_with_backoff.py
│           │       ├── switch_model_fallback.py
│           │       ├── patch_prompt_template.py
│           │       ├── update_config.py
│           │       ├── rotate_api_key.py
│           │       ├── rollback_snapshot.py
│           │       ├── patch_code_hotfix.py
│           │       ├── migrate_schema.py
│           │       ├── reinstall_dependency.py
│           │       └── rebuild_vector_index.py
│           ├── verification/          # Layer 5
│           │   ├── post_repair_validator.py
│           │   ├── regression_checker.py
│           │   └── rollback_trigger.py
│           ├── catalog/               # 수리 액션 카탈로그
│           │   └── repair_action_catalog.py
│           └── state_machine.py       # SDAR 상태 머신
```

---

# 7. 상태 머신 (State Machine)

## 7.1 SDAR 상태 정의

SDAR는 7개 상태(S0~S6)를 가진 상태 머신으로 동작한다. 기존 VAMOS 상태 머신(S0_RECEIVED ~ S8_DONE)과 독립적으로 동작하되, 병렬 실행된다.

```
┌──────────────────────────────────────────────────────────────────┐
│                    SDAR 상태 머신 (State Machine)                  │
│                                                                   │
│  SDAR_S0_MONITORING                                               │
│       │ (이상 감지)                                                │
│       ▼                                                           │
│  SDAR_S1_DETECTED                                                 │
│       │ (진단 시작)                                                │
│       ▼                                                           │
│  SDAR_S2_DIAGNOSED                                                │
│       │ (처방 생성)                                                │
│       │                                                           │
│       ├──▶ [진단 실패] ──▶ SDAR_S0_MONITORING (FB_SDAR_RETRY)     │
│       ▼                                                           │
│  SDAR_S3_PRESCRIBED                                               │
│       │ (수리 결정)                                                │
│       │                                                           │
│       ├──▶ [AR-L0/L1] ──▶ SDAR_S6_DONE (알림만)                  │
│       ├──▶ [수리 불가] ──▶ SDAR_S6_DONE (에스컬레이션)             │
│       ▼                                                           │
│  SDAR_S4_REPAIRING                                                │
│       │ (수리 실행)                                                │
│       │                                                           │
│       ├──▶ [수리 실패] ──▶ SDAR_S5_VERIFIED (롤백 판정)           │
│       ├──▶ [승인 대기] ──▶ SDAR_S4_REPAIRING (대기)               │
│       ▼                                                           │
│  SDAR_S5_VERIFIED                                                 │
│       │ (검증 완료)                                                │
│       │                                                           │
│       ├──▶ [검증 FAIL] ──▶ SDAR_S4_REPAIRING (롤백 실행)         │
│       ├──▶ [검증 WARN] ──▶ SDAR_S6_DONE (경고 + 관찰)            │
│       ▼                                                           │
│  SDAR_S6_DONE                                                     │
│       │ (완료)                                                    │
│       └──▶ SDAR_S0_MONITORING (대기 복귀)                         │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

## 7.2 상태별 상세

| 상태 | 설명 | 진입 조건 | 종료 조건 | 타임아웃 |
|------|------|---------|---------|---------|
| **SDAR_S0_MONITORING** | 정상 모니터링 대기 | 시스템 시작 / S6 완료 | 이상 신호 감지 | 없음 (상시) |
| **SDAR_S1_DETECTED** | 이상 감지 완료, 진단 대기 | Layer 1 신호 발행 | 진단 시작 | 30초 |
| **SDAR_S2_DIAGNOSED** | 근본 원인 분석 완료 | Layer 2 완료 | 처방 생성 시작 | 60초 |
| **SDAR_S3_PRESCRIBED** | 수리 계획 수립 완료 | Layer 3 완료 | 수리 실행 결정 | 30초 |
| **SDAR_S4_REPAIRING** | 수리 실행 중 | Layer 4 실행 시작 | 수리 완료/실패 | 액션별 (estimated_duration_s * 3) |
| **SDAR_S5_VERIFIED** | 수리 후 검증 중 | Layer 5 시작 | 검증 판정 | 300초 (관찰 기간) |
| **SDAR_S6_DONE** | 전체 프로세스 완료 | 최종 판정 | S0 복귀 | 10초 |

## 7.3 상태 전이 이벤트 매핑

| 전이 | 이벤트 | 조건 |
|------|--------|------|
| S0 → S1 | `oc.sdar.detection.signal_emitted` | severity >= "warn" |
| S1 → S2 | `oc.sdar.diagnosis.completed` | root_cause 특정 성공 |
| S1 → S0 | `oc.sdar.detection.false_positive` | 오탐 판정 |
| S2 → S3 | `oc.sdar.prescription.plan_ready` | 수리 계획 수립 완료 |
| S2 → S0 | `oc.sdar.diagnosis.failed` | 진단 실패 (재시도 후) |
| S3 → S4 | `oc.sdar.repair.started` | AR-Level >= AR-L2 & 수리 가능 |
| S3 → S6 | (AR-L0/L1) | 알림만 발송 후 완료 |
| S3 → S6 | `oc.sdar.prescription.no_fix_available` | 수리 불가 |
| S4 → S5 | `oc.sdar.repair.succeeded` / `oc.sdar.repair.failed` | 수리 실행 완료 |
| S5 → S6 | `oc.sdar.verification.passed` / `oc.sdar.verification.warned` | 검증 통과/경고 |
| S5 → S4 | `oc.sdar.verification.failed` | 검증 실패 → 롤백 |
| S6 → S0 | `oc.sdar.verification.completed` | 프로세스 종료 |

## 7.4 동시 실행 제한

- **최대 동시 SDAR 인스턴스**: 3개 (기존 병렬 실행 상한 LOCK과 일치)
- **동일 failure_code에 대한 병렬 SDAR**: 1개만 허용 (중복 수리 방지)
- **SDAR_S4_REPAIRING 상태 동시 허용**: 1개만 (수리 직렬화)

---

# 8. 스키마 설계 (Schema Design)

## 8.1 SDARDiagnosis 스키마 (Pydantic v2)

```python
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Literal
from datetime import datetime


class SDARRootCause(BaseModel):
    """근본 원인 분석 결과"""
    cause_id: str = Field(..., description="원인 식별자")
    description: str = Field(..., description="원인 설명")
    confidence: float = Field(..., ge=0.0, le=1.0, description="원인 확신도")
    evidence_refs: List[str] = Field(default_factory=list, description="근거 LogEvent ID 목록")
    related_modules: List[str] = Field(default_factory=list, description="관련 모듈 ID (I-#, S-#, E-#)")
    causal_chain: List[str] = Field(
        default_factory=list,
        description="인과 체인 (원인 → 중간 → 증상 순서)"
    )


class SDARImpactAssessment(BaseModel):
    """영향 범위 평가"""
    scope: List[str] = Field(default_factory=list, description="영향받는 모듈 목록")
    user_impact: Literal["none", "degraded", "blocked", "data_loss"] = Field(
        ..., description="사용자 영향도"
    )
    data_risk: Literal["none", "low", "medium", "high", "critical"] = Field(
        ..., description="데이터 위험도"
    )
    propagation: Literal["isolated", "spreading", "cascading"] = Field(
        ..., description="연쇄 장애 가능성"
    )
    blast_radius_score: float = Field(
        ..., ge=0.0, le=1.0, description="영향 범위 종합 점수"
    )


class SDARDiagnosis(BaseModel):
    """Layer 2 진단 결과 스키마"""
    diagnosis_id: str = Field(..., description="진단 고유 ID (UUID v4)")
    trace_id: str = Field(..., description="연관 trace_id")
    signal_ref: str = Field(..., description="Layer 1 SDARDetectionSignal.signal_id 참조")
    diagnosed_at: str = Field(..., description="진단 완료 시각 (ISO8601 UTC)")

    # 오류 분류
    error_category: Literal["A", "B", "C", "D", "E"] = Field(
        ..., description="오류 카테고리 (A=Infra, B=Model, C=Logic, D=Code, E=Security)"
    )
    error_code: str = Field(..., description="SDAR 오류 코드 (e.g., SDAR_A04_API_429)")
    severity: Literal["info", "warn", "error", "critical"] = Field(
        ..., description="심각도"
    )

    # 근본 원인 분석
    root_causes: List[SDARRootCause] = Field(
        ..., min_length=1, description="근본 원인 목록 (최소 1개)"
    )
    primary_root_cause_idx: int = Field(
        default=0, description="주요 근본 원인 인덱스"
    )

    # 영향 범위
    impact: SDARImpactAssessment = Field(..., description="영향 범위 평가")

    # 메타데이터
    diagnosis_duration_ms: int = Field(..., description="진단 소요 시간 (ms)")
    pattern_match_ref: Optional[str] = Field(
        None, description="S-4 Error Pattern Miner 매칭 패턴 ID"
    )
    previous_occurrences: int = Field(
        default=0, description="동일 오류의 과거 발생 횟수 (최근 24시간)"
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "diagnosis_id": "diag_550e8400-e29b-41d4-a716-446655440001",
                "trace_id": "550e8400-e29b-41d4-a716-446655440000",
                "signal_ref": "sig_550e8400-e29b-41d4-a716-446655440002",
                "diagnosed_at": "2026-02-23T10:30:00Z",
                "error_category": "A",
                "error_code": "SDAR_A04_API_429",
                "severity": "warn",
                "root_causes": [{
                    "cause_id": "rc_001",
                    "description": "LLM API Rate Limit 초과 (분당 60회 상한 도달)",
                    "confidence": 0.95,
                    "evidence_refs": ["evt_001", "evt_002"],
                    "related_modules": ["I-10", "I-5"],
                    "causal_chain": ["높은 요청 빈도", "Rate Limit 임계치 도달", "429 응답"]
                }],
                "primary_root_cause_idx": 0,
                "impact": {
                    "scope": ["I-10", "I-5", "I-4"],
                    "user_impact": "degraded",
                    "data_risk": "none",
                    "propagation": "isolated",
                    "blast_radius_score": 0.3
                },
                "diagnosis_duration_ms": 250,
                "pattern_match_ref": "pat_api_429_v1",
                "previous_occurrences": 5
            }
        }
    )


```

## 8.2 SDARRepairPlan 스키마 (Pydantic v2)

```python
class SDARRepairStep(BaseModel):
    """개별 수리 단계"""
    step_order: int = Field(..., ge=1, description="실행 순서")
    action_id: str = Field(..., description="Repair Action Catalog ID (e.g., RA_003)")
    action_name: str = Field(..., description="액션 명칭 (e.g., retry_with_backoff)")
    parameters: dict = Field(default_factory=dict, description="액션별 실행 파라미터")
    expected_duration_s: int = Field(..., description="예상 소요 시간 (초)")
    timeout_s: int = Field(..., description="타임아웃 (초)")
    on_failure: Literal["abort", "skip", "rollback"] = Field(
        default="rollback", description="실패 시 행동"
    )


class SDARRollbackPlan(BaseModel):
    """롤백 계획"""
    strategy: Literal["snapshot_restore", "reverse_actions", "manual"] = Field(
        ..., description="롤백 전략"
    )
    snapshot_ref: Optional[str] = Field(None, description="복원 대상 스냅샷 ID")
    reverse_steps: List[SDARRepairStep] = Field(
        default_factory=list, description="역순 수리 단계 (reverse_actions 전략 시)"
    )
    estimated_rollback_duration_s: int = Field(
        ..., description="예상 롤백 소요 시간 (초)"
    )


class SDARRepairCandidate(BaseModel):
    """수리 후보"""
    candidate_id: str = Field(..., description="후보 ID")
    rank: int = Field(..., ge=1, description="우선순위 (1이 최우선)")
    success_probability: float = Field(
        ..., ge=0.0, le=1.0, description="예상 성공률"
    )
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(
        ..., description="위험도"
    )
    reversibility: Literal["fully_reversible", "partially_reversible", "irreversible"] = Field(
        ..., description="되돌림 가능 여부"
    )
    steps: List[SDARRepairStep] = Field(..., min_length=1, description="수리 단계")
    side_effects: List[str] = Field(default_factory=list, description="예상 부작용")
    estimated_total_duration_s: int = Field(..., description="전체 예상 소요 시간 (초)")


class SDARRepairPlan(BaseModel):
    """Layer 3 수리 계획 스키마"""
    plan_id: str = Field(..., description="수리 계획 고유 ID (UUID v4)")
    trace_id: str = Field(..., description="연관 trace_id")
    diagnosis_ref: str = Field(..., description="SDARDiagnosis.diagnosis_id 참조")
    created_at: str = Field(..., description="계획 수립 시각 (ISO8601 UTC)")

    # 수리 후보
    candidates: List[SDARRepairCandidate] = Field(
        ..., min_length=1, max_length=5, description="수리 후보 목록 (최대 5개)"
    )
    selected_candidate_idx: int = Field(
        default=0, description="선택된 후보 인덱스"
    )

    # 자율 수준 판정
    required_ar_level: Literal["AR-L2", "AR-L3", "AR-L4", "NEVER_AUTO"] = Field(
        ..., description="실행에 필요한 최소 AR-Level"
    )
    current_ar_level: str = Field(..., description="현재 시스템 AR-Level 설정")
    can_auto_execute: bool = Field(..., description="현재 AR-Level로 자동 실행 가능 여부")

    # Gate 결과
    gate_results: dict = Field(
        default_factory=dict,
        description="Gate 검증 결과 {policy: allow/deny, cost: normal/stop, evidence: sufficient}"
    )

    # 전제 조건
    pre_conditions: List[str] = Field(default_factory=list, description="실행 전제 조건")
    post_conditions: List[str] = Field(default_factory=list, description="수리 성공 판정 기준")

    # 롤백 계획
    rollback_plan: SDARRollbackPlan = Field(..., description="롤백 계획")

    # 스냅샷 필요 여부
    requires_snapshot: bool = Field(..., description="수리 전 스냅샷 필요 여부")

    # 승인 필요 여부
    requires_approval: bool = Field(
        ..., description="I-19 Approval 필요 여부"
    )
    approval_reason: Optional[str] = Field(
        None, description="승인 필요 사유"
    )

    model_config = ConfigDict(extra="forbid")
```

## 8.3 SDARRepairResult 스키마 (Pydantic v2)

```python
class SDARRepairStepResult(BaseModel):
    """개별 수리 단계 실행 결과"""
    step_order: int
    action_id: str
    action_name: str
    status: Literal["success", "failed", "skipped", "timeout"] = Field(
        ..., description="실행 결과"
    )
    started_at: str = Field(..., description="시작 시각 (ISO8601 UTC)")
    completed_at: str = Field(..., description="완료 시각 (ISO8601 UTC)")
    duration_ms: int = Field(..., description="실행 소요 시간 (ms)")
    output: dict = Field(default_factory=dict, description="액션 실행 결과 데이터")
    error: Optional[str] = Field(None, description="오류 메시지 (실패 시)")


class SDARRepairResult(BaseModel):
    """Layer 4 수리 실행 결과 스키마"""
    result_id: str = Field(..., description="수리 결과 고유 ID (UUID v4)")
    trace_id: str = Field(..., description="연관 trace_id")
    plan_ref: str = Field(..., description="SDARRepairPlan.plan_id 참조")
    diagnosis_ref: str = Field(..., description="SDARDiagnosis.diagnosis_id 참조")

    # 실행 정보
    ar_level_used: str = Field(..., description="실행에 사용된 AR-Level")
    started_at: str = Field(..., description="수리 시작 시각 (ISO8601 UTC)")
    completed_at: str = Field(..., description="수리 완료 시각 (ISO8601 UTC)")
    total_duration_ms: int = Field(..., description="전체 수리 소요 시간 (ms)")

    # 결과
    overall_status: Literal["success", "partial_success", "failed", "rollback_executed"] = Field(
        ..., description="전체 수리 결과"
    )
    step_results: List[SDARRepairStepResult] = Field(
        ..., description="개별 단계 결과"
    )

    # 스냅샷
    snapshot_id: Optional[str] = Field(
        None, description="수리 전 생성된 스냅샷 ID"
    )

    # 승인
    approval_id: Optional[str] = Field(
        None, description="I-19 승인 ID (승인이 필요했던 경우)"
    )
    approval_status: Optional[Literal["approved", "denied", "timeout"]] = Field(
        None, description="승인 결과"
    )

    # 롤백
    rollback_triggered: bool = Field(default=False, description="롤백 실행 여부")
    rollback_result: Optional[dict] = Field(
        None, description="롤백 실행 결과"
    )

    # 알림
    notification_sent: bool = Field(default=False, description="알림 발송 여부")
    notification_channel: Optional[str] = Field(
        None, description="알림 채널 (ui/log/both)"
    )

    # 후속 조치
    follow_up_required: bool = Field(default=False, description="추가 후속 조치 필요 여부")
    follow_up_actions: List[str] = Field(
        default_factory=list, description="권장 후속 조치"
    )

    # S-8 거버넌스 보고용
    governance_summary: dict = Field(
        default_factory=dict,
        description="거버넌스 보고 요약 {error_category, error_code, repair_action, success, cost_impact}"
    )

    model_config = ConfigDict(extra="forbid")
```

## 8.4 스키마 간 관계도

```
SDARDetectionSignal
    │
    │  signal_ref
    ▼
SDARDiagnosis
    │
    │  diagnosis_ref
    ▼
SDARRepairPlan
    │
    │  plan_ref
    ▼
SDARRepairResult
    │
    │  repair_result_ref
    ▼
SDARVerificationResult
    │
    │  보고
    ▼
SDARGovernanceReport ──▶ S-8 Self-evo Governance
```

---

# 9. 제약 및 안전 규칙 (LOCK)

## 9.1 RULE 1.3 준수 (절대 규칙)

SDAR는 VAMOS의 최상위 규칙인 RULE 1.3을 엄격히 준수한다.

**SDAR에서 절대 자동 수정 불가한 7개 불변 구역** (LOCK):

| # | 불변 구역 | SDAR 행동 | 위반 시 대응 |
|---|---------|----------|-----------|
| 1 | `safety_rules` (안전 규칙) | **NEVER_AUTO**: 감지/진단까지만, 수리 제안도 금지 | SDAR 즉시 중단 + CRITICAL 알림 |
| 2 | `cost_ceiling` (비용 상한) | **NEVER_AUTO**: 비용 상한 변경은 인간만 가능 | SDAR 즉시 중단 + CRITICAL 알림 |
| 3 | `approval_flow` (승인 흐름) | **NEVER_AUTO**: 승인 구조 변경은 인간만 가능 | SDAR 즉시 중단 + CRITICAL 알림 |
| 4 | `non_goals` (Non-goal) | **NEVER_AUTO**: Non-goal 목록 변경 불가 | SDAR 즉시 중단 + CRITICAL 알림 |
| 5 | `audit_format` (감사 형식) | **NEVER_AUTO**: 감사 로그 형식 변경 불가 | SDAR 즉시 중단 + CRITICAL 알림 |
| 6 | `data_retention` (데이터 보존) | **NEVER_AUTO**: 보존 정책 변경 불가 | SDAR 즉시 중단 + CRITICAL 알림 |
| 7 | `user_consent` (사용자 동의) | **NEVER_AUTO**: 동의 설정 변경 불가 | SDAR 즉시 중단 + CRITICAL 알림 |

**코드 레벨 보장**: NEVER_AUTO 수리 액션은 코드에서 하드코딩으로 차단하며, 설정 파일로 우회할 수 없다.

```python
# 절대 수정 불가 영역 (하드코딩)
NEVER_AUTO_TARGETS: frozenset = frozenset({
    "safety_rules",
    "cost_ceiling",
    "approval_flow",
    "non_goals",
    "audit_format",
    "data_retention",
    "user_consent",
    "escalate_own_privilege",
    "disable_guardrails",
    "bypass_gate",
})

def validate_repair_target(action: RepairAction, target: str) -> bool:
    """수리 대상이 불변 구역인지 검증. 불변 구역이면 무조건 False 반환."""
    if target in NEVER_AUTO_TARGETS:
        return False  # 절대 허용 안 함. 설정으로 override 불가.
    return True
```

## 9.2 자동수리 제한 규칙 (LOCK)

| 규칙 | 내용 | 사유 |
|------|------|------|
| **MAX_AUTO_REPAIRS_PER_ISSUE_PER_HOUR** | 동일 이슈에 대해 시간당 **최대 3회** 자동수리 | 무한 수리 루프 방지 |
| **MAX_CONCURRENT_REPAIRS** | 동시 수리 실행 **최대 1건** | 수리 간 간섭 방지 |
| **MAX_CONCURRENT_SDAR_INSTANCES** | 동시 SDAR 인스턴스 **최대 3건** | 시스템 리소스 보호 |
| **SNAPSHOT_MANDATORY** | MEDIUM/HIGH risk 수리 전 **스냅샷 필수** | 롤백 보장 |
| **NOTIFICATION_MANDATORY** | 모든 수리 활동에 대해 **알림 필수** (AR-Level 무관) | 감사 추적 |
| **APPROVAL_TIMEOUT** | 승인 대기 **최대 10분**, 초과 시 자동 거부 | 기존 9.5 규칙 준수 |
| **OBSERVATION_PERIOD** | 수리 후 **최소 300초 (5분)** 관찰 | 회귀 감지 |
| **ROLLBACK_TIMEOUT** | 롤백 실행 **최대 300초**, 초과 시 인간 에스컬레이션 | 롤백 실패 대비 |
| **COOLDOWN_BETWEEN_REPAIRS** | 동일 액션 반복 실행 간 **최소 60초 대기** | 과도한 반복 방지 |

## 9.3 Self-evo 원칙 준수 (LOCK)

기존 VAMOS Self-evo 원칙(Section 11.1)에 따라:

- SDAR의 수리 결과는 "**자동 적용 절대 금지**" 원칙을 준수
- 구체적으로:
  - Layer 3에서 생성된 수리 계획은 "**제안**"으로 간주
  - AR-L2~AR-L4에서의 자동 실행은 "사전 승인된 안전 범위 내의 실행"이지, Self-evo 자동 적용이 아님
  - SDAR가 학습한 새로운 수리 패턴을 S-Module에 적용하려면 반드시 S-8 거버넌스 승인 필요

## 9.4 Emergency Kill Switch (비상 정지)

| 항목 | 내용 |
|------|------|
| **활성화 권한** | 모든 RBAC 역할 (VIEWER 포함) |
| **활성화 방법** | `vamos:sdar:kill_switch` IPC 명령 또는 UI 긴급 버튼 |
| **효과** | SDAR 전체 즉시 정지. 진행 중인 수리는 안전하게 중단 (가능한 경우 롤백) |
| **복구 방법** | ADMIN 이상 권한으로 Kill Switch 해제 후 SDAR 재시작 |
| **이벤트** | `oc.sdar.kill_switch.activated` / `oc.sdar.kill_switch.deactivated` |
| **자동 활성화 조건** | SDAR_ROLLBACK_FAILED 발생 시 자동 Kill Switch ON |

```python
class SDARKillSwitch:
    """비상 정지 스위치"""

    def activate(self, reason: str, triggered_by: str) -> None:
        """SDAR 전체 즉시 정지

        - 진행 중인 수리: 안전 중단 시도 (5초 grace period)
        - 중단 불가 시: 강제 중단 + 스냅샷 복원
        - 모든 SDAR 상태: SDAR_S0_MONITORING으로 강제 전이
        """
        ...

    def deactivate(self, authorized_by: str) -> None:
        """Kill Switch 해제 (ADMIN 이상 권한 필수)"""
        ...
```

## 9.5 보안 오류(CATEGORY E) 특별 규칙 (LOCK)

보안 관련 오류(CATEGORY E)에 대해 SDAR는 다음 특별 규칙을 적용한다:

1. **자동수리 절대 금지**: 어떤 AR-Level에서도 CATEGORY E는 자동수리 불가
2. **즉시 차단**: 감지 즉시 해당 요청/세션 차단
3. **감사 로그 강제**: CRITICAL 심각도로 감사 로그 기록 (삭제/수정 불가)
4. **인간 알림 필수**: 모든 알림 채널로 즉시 통보
5. **관련 데이터 보존**: 포렌식 분석을 위해 관련 데이터 30일 보존 (기존 data_retention 정책과 별도)

## 9.6 P2 도메인 관련 수리 제한 (LOCK)

기존 P2 규칙(세션 종료 시 즉시 OFF, 세션별 승인 필수)에 따라:

- P2 관련 모듈의 수리는 **AR-Level 무관하게 반드시 인간 승인** 필요
- P2 관련 Circuit Breaker OPEN 시 자동 복구 금지 (승인 후 HALF-OPEN만)
- P2 도메인 자동 생성/활성화 관련 수리는 **절대 금지** (Non-goal 2.6)

## 9.7 비용 영향 제한 (LOCK)

- SDAR 수리로 인한 추가 비용은 기존 CostBudget 상한(V1: 40,000원/월) 내에서만 허용
- 수리 비용이 일일 상한의 10%를 초과할 것으로 예상되면 인간 승인 필요
- `switch_model_fallback` 실행 시 CostGate 재검증 필수

---

# 10. 버전 로드맵 (Version Roadmap)

## 10.1 V1: AR-L2 (AUTO_SAFE) -- 안전 자동수리만

### 목표
- 기존 I-20 Failure/Fallback Manager의 기본 Fallback을 SDAR Layer 1~2로 확장
- LOW risk 수리 액션만 자동 실행

### 활성화 수리 액션
| 액션 ID | 명칭 | 위험도 |
|---------|------|--------|
| `RA_001` | `restart_service` | LOW |
| `RA_002` | `clear_cache` | LOW |
| `RA_003` | `retry_with_backoff` | LOW |
| `RA_004` | `switch_model_fallback` | LOW |
| `RA_005` | `adjust_rate_limit` | LOW |

### V1 구현 범위
- [x] Layer 1: Health Monitoring (기본), Error Pattern Detection (기존 I-20 연동)
- [x] Layer 2: 기본 Root Cause Analysis, CATEGORY A 분류
- [x] Layer 3: LOW risk 후보만 생성
- [x] Layer 4: AR-L2 실행 로직
- [x] Layer 5: 기본 Post-Repair Validation
- [x] SDAR 상태 머신 (S0~S6)
- [x] 기본 로깅 (기존 LogEvent 확장)
- [x] Emergency Kill Switch

### V1 미포함
- Anomaly Detection (Channel C)
- MEDIUM/HIGH risk 수리
- S-4/S-8 연동
- 코드 핫픽스, 스키마 마이그레이션

### V1 출시 조건
- I-20 기존 Fallback 정상 동작 확인
- LOW risk 수리 5종 단위 테스트 통과
- 5분 관찰 기간 동안 회귀 없음 확인
- Emergency Kill Switch 동작 확인

## 10.2 V2: AR-L3 (AUTO_MODERATE) -- 중위험 수리 추가

### 목표
- MEDIUM risk 수리 액션까지 자동화 범위 확대
- 스냅샷 기반 롤백 체계 완성
- S-4 Error Pattern Miner 연동

### 추가 활성화 수리 액션
| 액션 ID | 명칭 | 위험도 |
|---------|------|--------|
| `RA_006` | `patch_prompt_template` | MEDIUM |
| `RA_007` | `update_config_parameter` | MEDIUM |
| `RA_008` | `rotate_api_key` | MEDIUM |
| `RA_009` | `rollback_to_snapshot` | MEDIUM |
| `RA_010` | `compress_logs` | MEDIUM |

### V2 추가 구현 범위
- [ ] Layer 1: Anomaly Detection (Channel C) 추가
- [ ] Layer 2: CATEGORY B, C 분류, S-4 패턴 매칭 연동
- [ ] Layer 3: MEDIUM risk 후보 생성, 스냅샷 계획 포함
- [ ] Layer 4: AR-L3 실행 로직, 스냅샷 관리자
- [ ] Layer 5: Regression Check 강화
- [ ] S-4 Error Pattern Miner 양방향 연동
- [ ] 수리 이력 기반 성공률 학습

### V2 출시 조건
- V1 수리 액션 100% 성공률 30일 유지
- 스냅샷 생성/복원 테스트 통과
- MEDIUM risk 수리 5종 통합 테스트 통과
- S-4 연동 테스트 통과

## 10.3 V3: AR-L4 (AUTO_AGGRESSIVE) -- 고위험 수리 + 완전 거버넌스

### 목표
- HIGH risk 수리 액션까지 자동화 (스냅샷 필수)
- S-8 Self-evo Governance 완전 연동
- 코드 핫픽스, 스키마 마이그레이션 자동화

### 추가 활성화 수리 액션
| 액션 ID | 명칭 | 위험도 |
|---------|------|--------|
| `RA_011` | `patch_code_hotfix` | HIGH |
| `RA_012` | `migrate_schema` | HIGH |
| `RA_013` | `reinstall_dependency` | HIGH |
| `RA_014` | `rebuild_vector_index` | HIGH |

### V3 추가 구현 범위
- [ ] Layer 2: CATEGORY D 분류, 코드 분석 기반 진단
- [ ] Layer 3: HIGH risk 후보 생성, 코드 분석 통합
- [ ] Layer 4: AR-L4 실행 로직, 코드 패치 엔진
- [ ] Layer 5: 전체 회귀 테스트 실행 (기존 tests/ 연동)
- [ ] S-8 Self-evo Governance 완전 연동
- [ ] SDARGovernanceReport 주기적 생성
- [ ] 수리 패턴 자동 진화 (S-3 Template Evolution 연동)
- [ ] 대시보드 (UI Builder View에 SDAR 탭 추가)

### V3 출시 조건
- V2 수리 액션 95%+ 성공률 60일 유지
- S-8 거버넌스 감사 통과
- 코드 핫픽스 안전성 검증 (샌드박스 테스트)
- 스키마 마이그레이션 롤백 테스트 통과
- 전체 회귀 테스트 통과

## 10.4 버전 전환 체크리스트

### V1 → V2 전환 조건
- [ ] LOW risk 수리 성공률 ≥ 95% (30일 기준)
- [ ] false positive (오탐) 비율 < 5%
- [ ] Emergency Kill Switch 사용 횟수 = 0 (30일)
- [ ] 사용자 수동 롤백 요청 < 3건/월
- [ ] 기존 I-20 Fallback 대비 MTTR(평균 복구 시간) 50% 이상 단축

### V2 → V3 전환 조건
- [ ] MEDIUM risk 수리 성공률 ≥ 90% (60일 기준)
- [ ] 스냅샷 복원 성공률 100%
- [ ] S-4 패턴 매칭 정확도 ≥ 80%
- [ ] 수리 후 회귀 발생률 < 2%
- [ ] S-8 거버넌스 감사 통과
- [ ] OWNER 승인

---

# 부록 A: SDAR API 엔드포인트

## Tauri IPC Commands (SDAR 전용)

| 명령 | 설명 | 최소 권한 |
|------|------|---------|
| `vamos:sdar:status` | SDAR 현재 상태 조회 | VIEWER |
| `vamos:sdar:config:get` | SDAR 설정 조회 | VIEWER |
| `vamos:sdar:config:set` | SDAR 설정 변경 | ADMIN |
| `vamos:sdar:ar_level:get` | 현재 AR-Level 조회 | VIEWER |
| `vamos:sdar:ar_level:set` | AR-Level 변경 | ADMIN (L4는 OWNER) |
| `vamos:sdar:kill_switch` | Emergency Kill Switch 활성화 | VIEWER |
| `vamos:sdar:kill_switch:release` | Kill Switch 해제 | ADMIN |
| `vamos:sdar:history:list` | 수리 이력 조회 | VIEWER |
| `vamos:sdar:history:detail` | 수리 상세 조회 | VIEWER |
| `vamos:sdar:diagnosis:list` | 진단 이력 조회 | VIEWER |
| `vamos:sdar:repair:approve` | 수리 승인 | ADMIN |
| `vamos:sdar:repair:deny` | 수리 거부 | OPERATOR |
| `vamos:sdar:repair:rollback` | 수동 롤백 실행 | ADMIN |
| `vamos:sdar:governance:report` | 거버넌스 보고서 조회 | ADMIN |

## Python-Rust JSON-RPC (SDAR 전용)

| Method | 설명 |
|--------|------|
| `sdar.pipeline.trigger` | SDAR 파이프라인 수동 트리거 |
| `sdar.diagnosis.run` | 진단 수동 실행 |
| `sdar.repair.execute` | 수리 수동 실행 |
| `sdar.snapshot.create` | 스냅샷 수동 생성 |
| `sdar.snapshot.restore` | 스냅샷 수동 복원 |

---

# 부록 B: SDAR 설정 파일 (config/sdar/default.toml)

```toml
[sdar]
enabled = true
ar_level = "AR-L2"                    # 기본값: AUTO_SAFE
emergency_kill_switch = false

[sdar.detection]
health_check_interval_s = 30          # Health Check 주기
error_pattern_window_s = 300          # 오류 패턴 감지 윈도우 (5분)
error_pattern_threshold = 3           # 윈도우 내 동일 오류 임계치
anomaly_baseline_window_h = 24        # 이상 탐지 기준선 윈도우 (24시간)
anomaly_deviation_threshold = 2.0     # 기준선 대비 편차 임계치 (200%)

[sdar.diagnosis]
max_duration_s = 60                   # 진단 최대 소요 시간
min_root_cause_confidence = 0.5       # 근본 원인 최소 확신도
enable_s4_pattern_match = false       # S-4 패턴 매칭 (V2+)

[sdar.prescription]
max_candidates = 5                    # 최대 수리 후보 수
min_success_probability = 0.6         # 최소 예상 성공률

[sdar.repair]
max_auto_repairs_per_issue_per_hour = 3
max_concurrent_repairs = 1
snapshot_retention_hours = 168        # 7일
approval_timeout_s = 600             # 10분
cooldown_between_repairs_s = 60

[sdar.verification]
observation_period_s = 300            # 5분
regression_check_enabled = true
auto_rollback_on_failure = true
rollback_timeout_s = 300

[sdar.notification]
channel = "both"                      # ui | log | both
```

---

# 부록 C: 용어 사전

| 용어 | 정의 |
|------|------|
| **SDAR** | Self-Diagnosis & Auto-Repair. VAMOS의 자기진단 및 자동수리 시스템 |
| **AR-Level** | Auto-Repair Level. 자동수리 자율 수준 (AR-L0 ~ AR-L4) |
| **Graduated Autonomy** | 단계적 자율. 위험 수준에 따라 자동화 범위를 차등 적용하는 원칙 |
| **Blast Radius** | 장애 영향 범위. 오류가 영향을 미치는 모듈/기능의 범위 |
| **Repair Action** | 수리 액션. SDAR가 실행할 수 있는 개별 복구 동작 |
| **NEVER_AUTO** | 절대 자동 수행 불가 지정. 어떤 AR-Level에서도 자동 실행이 금지된 액션 |
| **Kill Switch** | 비상 정지 스위치. SDAR 전체를 즉시 중단시키는 안전장치 |
| **Detection Signal** | 감지 신호. Layer 1에서 이상을 감지했을 때 발행하는 신호 |
| **Root Cause** | 근본 원인. 오류의 최초 발생 원인 |
| **Snapshot** | 스냅샷. 수리 전 시스템 상태를 저장한 복원 지점 |
| **Regression** | 회귀. 수리 후 기존에 정상이던 기능이 오작동하는 현상 |
| **MTTR** | Mean Time To Repair. 평균 복구 시간 |

---

> **끝** -- 본 문서는 VAMOS AI의 Self-Diagnosis & Auto-Repair (SDAR) 시스템에 대한 완전한 설계 명세서이다. VAMOS_MASTER_SPECIFICATION v1.0.0의 기존 아키텍처, Gate 시스템, Failure/Fallback 체계, Self-evo 원칙, RBAC, Circuit Breaker, LogEvent 규격을 준수하며, 기존 7개 불변 구역(LOCK)에 대한 자동 수정을 절대 금지한다. 구현 시 본 문서와 VAMOS_MASTER_SPECIFICATION을 함께 참조하십시오.

---

<\!-- END OF DOCUMENT -->
