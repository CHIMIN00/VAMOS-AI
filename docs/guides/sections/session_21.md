---
session: 21
sections: [25]
status: complete
---

# §25. SDAR — 자가진단 & 자동수리 시스템

> **비유**: 자동차에는 **자가진단 시스템(OBD)**이 있습니다. 엔진 경고등이 켜지면 원인을 자동으로 파악하고, 간단한 문제(예: 에어컨 재시작)는 스스로 고치고, 심각한 문제(예: 엔진 고장)는 운전자에게 알려줍니다. VAMOS의 **SDAR**도 똑같습니다 — AI 시스템에서 이상이 감지되면 원인을 분석하고, 안전한 수리는 자동으로, 위험한 수리는 사람에게 보고합니다.

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §1.1, §1.2]

---

## §25.1 SDAR이란?

### 비유: 자동차 자가진단 시스템

여러분의 자동차 계기판에 엔진 경고등이 켜진 상황을 생각해보세요:

1. **감지**: 센서가 이상을 발견 (경고등 ON)
2. **진단**: OBD가 오류 코드를 읽어 원인 파악
3. **수리 결정**: 간단하면 자동 수리, 복잡하면 정비소 안내
4. **확인**: 수리 후 경고등이 꺼지는지 확인

SDAR (Self-Diagnosis & Auto-Repair, 자가진단 & 자동수리)는 VAMOS AI 시스템에서 이 모든 과정을 자동으로 수행합니다.

### 핵심 정보

| 항목 | 내용 |
|------|------|
| **정식 명칭** | Self-Diagnosis & Auto-Repair (자가진단 & 자동수리) |
| **약어** | SDAR |
| **모듈 ID** | I-25 (신규 모듈) |
| **목적** | 시스템 오류를 실시간 감지 → 원인 분석 → 자동/반자동 수리 |
| **설계 영감** | ALZip의 오류 자동 복구 기능 |
| **연관 모듈** | I-6, I-16, I-18, I-20, S-1, S-4, S-8 |

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §1.1, §1.4]

### SDAR의 4대 핵심 가치

| 핵심 가치 | 비유 | 설명 |
|-----------|------|------|
| **가용성 극대화** | 자동차가 멈추지 않게 | 시스템 다운타임 (멈춤 시간) 최소화 |
| **자율적 복원력** | 면역 체계처럼 | 반복적인 장애는 인간 도움 없이 자동 해결 |
| **안전 우선 복구** | "치료가 병보다 나빠선 안 된다" | 수리 자체가 새 문제를 만들지 않도록 보장 |
| **점진적 자율 확대** | 초보 운전→ 베테랑 운전 | 검증된 패턴만 점차 자동화 범위 확대 |

### 버전별 활성 여부

| 버전 | 상태 | 설명 |
|------|------|------|
| **V0** | OFF | SDAR 미존재 (기본 에러 처리만) |
| **V1** | OFF | I-20 Failure/Fallback Manager의 기본 Fallback으로만 운영 |
| **V2** | COND (조건부) | AR-L2 수준의 안전 자동수리만 조건부 활성화 |
| **V3** | ON | AR-L3~AR-L4까지 단계적 확대, S-8 거버넌스 연동 |

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §1.4]

### SDAR과 기존 모듈의 연결

SDAR은 혼자 동작하지 않습니다. 기존 VAMOS 모듈들과 팀처럼 협력합니다:

| 기존 모듈 | 역할 비유 | SDAR와의 관계 |
|-----------|----------|--------------|
| **S-1 Self-check Engine** | 건강검진 센서 | SDAR에 "문제 신호" 제공 |
| **S-4 Error Pattern Miner** | 의료 기록 담당 | 반복 오류 패턴을 학습 데이터로 공급 |
| **I-6 Self-check Engine** | 출력 품질 검사관 | 출력 품질 검증 결과를 SDAR에 전달 |
| **I-16 Knowledge Search Engine** | 의학 도서관 | 과거 수리 이력, 수리 지식 검색 |
| **I-20 Failure/Fallback Manager** | 기존 응급실 | 기존 Fallback 체계를 SDAR가 확장·보강 |
| **I-19 Approval Manager** | 승인 담당자 | 중·고위험 수리 시 승인 요청 |
| **I-8 Policy Engine** | 규정 준수 감시관 | 수리 액션의 정책 준수 여부 검증 |
| **S-8 Self-evo Governance** | 경영진 보고 | SDAR 수리 결과를 거버넌스에 보고 |

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §1.3]

### 핵심 요약 (3줄)
1. SDAR(I-25)은 VAMOS의 자가진단 & 자동수리 시스템으로, 자동차 OBD처럼 이상 감지→원인 분석→수리→검증을 자동 수행합니다.
2. "안전한 것은 자동으로, 위험한 것은 사람이" 라는 핵심 원칙에 따라 점진적으로 자율 범위를 확대합니다.
3. V1은 OFF, V2에서 조건부 활성, V3에서 완전 활성되며, S-1/S-4/I-20 등 8개 기존 모듈과 긴밀히 연동합니다.

---

## §25.2 5-Layer Pipeline (5계층 파이프라인)

### 비유: 병원 진료 과정

SDAR의 5계층 파이프라인은 병원에서 환자를 치료하는 과정과 같습니다:

| 계층 | 병원 비유 | SDAR 역할 |
|------|----------|----------|
| **Layer 1** | 건강검진 (이상 발견) | DETECTION — 실시간 이상 감지 |
| **Layer 2** | 정밀 검사 (원인 파악) | DIAGNOSIS — 근본 원인 분석 |
| **Layer 3** | 치료 계획 수립 | PRESCRIPTION — 수리 계획 생성 |
| **Layer 4** | 수술/치료 실행 | REPAIR — 수리 액션 실행 |
| **Layer 5** | 퇴원 전 검사 | VERIFICATION — 수리 결과 검증 |

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §2.1]

### 전체 구조도

```
┌─────────────────────────────────────────────────────────────────┐
│                    SDAR 5-Layer Pipeline                        │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│  │ Layer 1  │─▶│ Layer 2  │─▶│ Layer 3  │─▶│ Layer 4  │─▶│ Layer 5  │
│  │DETECTION │  │DIAGNOSIS │  │PRESCRIPT.│  │ REPAIR   │  │VERIFICAT.│
│  │실시간 감지│  │원인 분석 │  │처방 생성 │  │수리 실행 │  │  검증    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘
│                                                                 │
│  ──────────────── Event Bus (이벤트 버스) ─────────────────────  │
└─────────────────────────────────────────────────────────────────┘
```

---

### Layer 1: DETECTION (감지) — "이상을 발견하다"

> **비유**: 자동차 센서가 온도, 압력, 속도를 실시간으로 측정하듯, SDAR Layer 1은 시스템 전반을 실시간으로 감시합니다.

Layer 1은 **3가지 감지 채널**을 통해 이상을 발견합니다:

#### Channel A: Health Monitoring (상태 모니터링)

주기적으로 시스템 건강 상태를 점검합니다 (기본 30초 간격).

| 모니터링 대상 | 경고 임계치 | 위험 임계치 |
|-------------|-----------|-----------|
| DB 커넥션 (데이터베이스 연결) | 응답 없음 | 연결 끊김 |
| Vector DB 상태 | 응답 지연 | 응답 없음 |
| LLM API 응답성 | 지연 증가 | 응답 없음 |
| 디스크 용량 | 85% 사용 | 95% 사용 |
| 메모리 사용률 | 80% 사용 | 90% 사용 |
| MCP 서버 상태 | 응답 지연 | 응답 없음 |
| Rate Limit 잔여량 | 잔여 적음 | 소진 |

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §2.2]

#### Channel B: Error Pattern Detection (오류 패턴 감지)

I-20 Failure/Fallback Manager에서 실패 이벤트를 수신하고, 패턴을 분석합니다:

| 감지 규칙 | 비유 | 조건 |
|----------|------|------|
| **빈도 기반** | "같은 증상이 자꾸 반복" | 동일 오류가 5분 내 3회 이상 발생 |
| **연쇄 기반** | "도미노처럼 연쇄 장애" | 서로 다른 오류가 60초 내 연속 발생 |
| **시간대 기반** | "매일 같은 시간에 아프다" | 특정 시간대에 반복되는 오류 |

#### Channel C: Anomaly Detection (이상 탐지)

정상 운영 기준선 (baseline, 기준점)과 비교하여 이상을 탐지합니다:

| 이상 지표 | 트리거 조건 |
|----------|-----------|
| 응답 시간 급증 | 기준선 대비 200% 초과 |
| Self-check 점수 급락 | 최근 10건 평균 대비 30% 이상 하락 |
| QoD 점수 지속 저하 | 이동 평균 < 0.5로 3회 연속 |
| 비용 소진 속도 이상 | 예상 일일 소진율 대비 150% 초과 |
| 토큰 사용량 급증 | 최근 1시간 평균 대비 300% 초과 |

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §2.2]

---

### Layer 2: DIAGNOSIS (진단) — "원인을 파악하다"

> **비유**: 의사가 혈액 검사, X-ray, MRI를 통해 정확한 원인을 찾듯, SDAR Layer 2는 감지된 이상의 근본 원인(Root Cause)을 분석합니다.

Layer 2는 **3단계 진단 프로세스**를 수행합니다:

**Step 2-1: Root Cause Analysis (근본 원인 분석)**
- 로그 상관 분석 (같은 trace_id에 연결된 모든 로그를 시간순으로 나열)
- 의존성 그래프 탐색 (실패한 모듈이 의존하는 다른 모듈을 따라감)
- 패턴 매칭 (S-4 Error Pattern Miner의 기존 패턴과 비교)
- 시간적 상관관계 (장애 직전에 무엇이 바뀌었는지 확인)

**Step 2-2: Error Classification (오류 분류)**
- 5가지 카테고리(A~E)로 분류 (§25.3에서 상세 설명)

**Step 2-3: Impact Assessment (영향 범위 평가)**

| 평가 항목 | 설명 | 등급 |
|----------|------|------|
| **scope** (범위) | 영향받는 모듈 목록 | 모듈 ID 리스트 |
| **user_impact** (사용자 영향) | 사용자 경험에 미치는 영향 | none / degraded / blocked / data_loss |
| **data_risk** (데이터 위험) | 데이터 손상/손실 위험도 | none / low / medium / high / critical |
| **propagation** (전파) | 연쇄 장애 가능성 | isolated / spreading / cascading |

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §2.3]

---

### Layer 3: PRESCRIPTION (처방) — "치료 계획을 세우다"

> **비유**: 의사가 진단 결과를 보고 여러 치료 옵션을 검토한 뒤 최적의 치료법을 선택하듯, Layer 3는 수리 후보를 생성하고 최적의 수리 계획을 수립합니다.

**Step 3-1: 수리 후보 생성** (최소 1개, 최대 5개)

후보 우선순위 결정 기준:
1. 성공률 (과거 동일 패턴 수리 성공률이 높을수록 우선)
2. 위험도 (낮을수록 우선)
3. 복구 시간 (빠를수록 우선)
4. 비용 영향 (적을수록 우선)

**Step 3-2: 위험도 평가** (각 후보마다)

| 평가 항목 | 설명 |
|----------|------|
| `risk_level` | LOW / MEDIUM / HIGH / CRITICAL |
| `reversibility` (되돌림 가능성) | 완전 / 부분 / 불가능 |
| `side_effects` (부작용) | 예상되는 부작용 목록 |
| `estimated_downtime` | 예상 수리 소요 시간 |

**Step 3-3: 수리 계획 수립**
- Pre-conditions (전제 조건): 수리 전 충족 필요 조건
- Repair Steps (수리 단계): 단계별 실행 계획
- Post-conditions (사후 조건): 수리 성공 판정 기준
- Rollback Plan (롤백 계획): 실패 시 복원 절차
- Verification Criteria (검증 기준): Layer 5에서 사용할 검증 항목

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §2.4]

---

### Layer 4: REPAIR (수리) — "실제로 고치다"

> **비유**: 의사가 치료 계획에 따라 실제 수술/치료를 진행하되, 위험도에 따라 간호사가 하거나 전문의가 하거나 환자 동의를 받는 것처럼, Layer 4는 AR-Level에 따라 실행 방식이 달라집니다.

#### AR-Level별 실행 흐름

| AR-Level | 동작 | 비유 |
|----------|------|------|
| **AR-L0** (수동) | 로그만 기록, 실행 안 함 | 의사가 "아프시군요" 기록만 |
| **AR-L1** (알림) | 진단 + 수리 제안을 사용자에게 전달 | 의사가 치료법을 설명, 환자가 결정 |
| **AR-L2** (안전 자동) | LOW risk만 즉시 자동 실행 | 간호사가 반창고 붙이기 |
| **AR-L3** (중간 자동) | MEDIUM까지 자동 + 즉시 알림 | 의사가 처치 후 보호자에게 연락 |
| **AR-L4** (적극 자동) | HIGH까지 자동 (스냅샷 필수) + 알림 | 응급 수술 후 즉시 보호자 통보 |

#### 수리 실행 공통 절차

```
1. Pre-flight Check (사전 점검)  → 전제 조건 확인
2. Snapshot (스냅샷)            → MEDIUM/HIGH 시 상태 저장
3. Execute (실행)               → 수리 액션 순차 실행
4. Monitor (모니터링)           → 실행 중 실시간 감시
5. Result Capture (결과 수집)    → 실행 결과 기록
6. Notification (알림)          → AR-Level에 따른 알림 발송
```

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §2.5]

---

### Layer 5: VERIFICATION (검증) — "제대로 고쳤는지 확인하다"

> **비유**: 수술 후 퇴원 전에 혈액 검사, 기능 테스트를 다시 하고, 이상 없으면 퇴원 승인하고, 문제가 있으면 재수술하는 것과 같습니다.

**Step 5-1: Post-Repair Validation (수리 후 검증)**
- 수리 계획의 사후 조건이 모두 충족되는지 확인
- 수리 대상 모듈의 Health Check 재실행
- 원래 오류가 재현되지 않는지 확인

**Step 5-2: Regression Check (회귀 검사)**
- 수리 전후 성능 지표 비교 (응답 시간, Self-check 점수, QoD 점수, 에러율)
- 새로운 오류가 발생하지 않았는지 확인 (**5분 관찰 기간**)

**Step 5-3: Rollback Trigger (롤백 판정)**

롤백 (되돌리기)이 자동 실행되는 조건:

| 조건 | 설명 |
|------|------|
| 사후 조건 미충족 | 수리가 제대로 되지 않음 |
| 새로운 심각한 이벤트 발생 | 수리 후 error/critical 심각도 이벤트 |
| Self-check 점수 하락 | 수리 전보다 점수가 오히려 내려감 |
| 사용자 수동 롤백 명령 | 사용자가 직접 되돌리기 요청 |

검증 최종 판정: **PASS** (통과) / **WARN** (경고) / **FAIL** (실패 → 롤백)

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §2.6]

### 핵심 요약 (3줄)
1. SDAR는 감지(Detection)→진단(Diagnosis)→처방(Prescription)→수리(Repair)→검증(Verification)의 5계층 파이프라인으로 동작합니다.
2. 각 계층은 독립적으로 실행 가능하되, 상위 계층의 출력이 하위 계층의 입력이 되는 순차 흐름을 따릅니다.
3. Layer 5 검증에서 문제가 발견되면 자동 롤백이 실행되며, 5분간의 관찰 기간을 거쳐 회귀(regression) 여부를 확인합니다.

---

## §25.3 에러 분류 체계 (5가지 카테고리)

### 비유: 병원의 진료과 분류

병원에 가면 증상에 따라 내과, 외과, 피부과 등 진료과가 나뉘듯, SDAR도 오류를 **5가지 카테고리**로 분류하여 각각에 맞는 치료법을 적용합니다.

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §4.1]

### 5대 오류 카테고리 요약

| 카테고리 | 명칭 | 비유 | 자동수리 가능? |
|---------|------|------|-------------|
| **A** | Infrastructure (인프라) | 건물 시설 고장 (전기, 수도) | 대부분 가능 |
| **B** | Model/AI (모델/AI) | 의사 판단력 저하 | 부분 가능 |
| **C** | Logic (로직) | 업무 절차 오류 | 제한적 가능 |
| **D** | Code (코드) | 설계도 결함 | 고위험만 가능 |
| **E** | Security (보안) | 도둑 침입 | **절대 자동수리 금지** |

---

### CATEGORY A: Infrastructure (인프라 오류)

> 건물의 전기, 수도, 인터넷이 끊기는 것과 같은 문제. **대부분 자동수리 가능**.

| 오류 코드 | 설명 | 위험도 | 자동수리 수준 |
|----------|------|--------|-------------|
| `SDAR_A01_DB_CONN_LOST` | DB 연결 끊김 | LOW | AR-L2 |
| `SDAR_A02_DB_TIMEOUT` | DB 응답 시간 초과 | LOW | AR-L2 |
| `SDAR_A03_DB_CORRUPT` | DB 데이터 손상 | HIGH | AR-L4 |
| `SDAR_A04_API_429` | LLM API 사용량 초과 | LOW | AR-L2 |
| `SDAR_A05_API_5XX` | LLM API 서버 오류 | LOW | AR-L2 |
| `SDAR_A06_API_AUTH_FAIL` | API 인증 실패 | MEDIUM | AR-L3 |
| `SDAR_A07_DISK_FULL` | 디스크 용량 부족 | MEDIUM | AR-L3 |
| `SDAR_A08_MEMORY_OOM` | 메모리 부족 | MEDIUM | AR-L3 |
| `SDAR_A09_PROCESS_CRASH` | 프로세스 비정상 종료 | LOW | AR-L2 |
| `SDAR_A10_NETWORK_UNREACHABLE` | 네트워크 불통 | LOW | AR-L2 |
| `SDAR_A11_VECTOR_DB_DOWN` | Vector DB 장애 | MEDIUM | AR-L3 |
| `SDAR_A12_MCP_SERVER_DOWN` | MCP 서버 응답 없음 | LOW | AR-L2 |

### CATEGORY B: Model/AI (모델/AI 오류)

> AI 모델의 응답 품질이 떨어지거나 엉뚱한 대답을 하는 문제.

| 오류 코드 | 설명 | 위험도 | 자동수리 수준 |
|----------|------|--------|-------------|
| `SDAR_B01_HALLUCINATION` | 할루시네이션 (거짓 정보 생성) 감지 | MEDIUM | AR-L3 |
| `SDAR_B02_QUALITY_DEGRADATION` | 출력 품질 저하 | MEDIUM | AR-L3 |
| `SDAR_B03_ROUTING_FAILURE` | 모델 라우팅 (연결 경로) 실패 | LOW | AR-L2 |
| `SDAR_B04_SELFCHECK_FAIL` | Self-check 지속 실패 | MEDIUM | AR-L3 |
| `SDAR_B05_QOD_COLLAPSE` | QoD 점수 급락 | MEDIUM | AR-L3 |
| `SDAR_B06_TOKEN_EXPLOSION` | 토큰 사용량 폭증 | MEDIUM | AR-L3 |
| `SDAR_B07_EMBEDDING_DRIFT` | 임베딩 (벡터 표현) 품질 저하 | HIGH | AR-L4 |
| `SDAR_B08_CONTEXT_OVERFLOW` | 컨텍스트 윈도우 (입력 제한) 초과 | LOW | AR-L2 |

### CATEGORY C: Logic (로직 오류)

> 업무 절차가 꼬이거나 설정이 잘못된 문제.

| 오류 코드 | 설명 | 위험도 | 자동수리 수준 |
|----------|------|--------|-------------|
| `SDAR_C01_WORKFLOW_STUCK` | 워크플로우 (작업 흐름) 교착 | MEDIUM | AR-L3 |
| `SDAR_C02_GATE_MISCONFIGURED` | Gate 설정 오류 | HIGH | AR-L4 |
| `SDAR_C03_SCHEMA_MISMATCH` | 스키마 (데이터 구조) 불일치 | HIGH | AR-L4 |
| `SDAR_C04_STATE_INCONSISTENCY` | 상태 머신 불일치 | MEDIUM | AR-L3 |
| `SDAR_C05_LOOP_DETECTED` | 무한 루프 감지 | MEDIUM | AR-L3 |
| `SDAR_C06_PIPELINE_BROKEN` | 파이프라인 단절 | HIGH | AR-L4 |

### CATEGORY D: Code (코드 오류)

> 프로그램 코드 자체에 버그가 있거나 의존성이 깨진 문제. **고위험 수리만 가능**.

| 오류 코드 | 설명 | 위험도 | 자동수리 수준 |
|----------|------|--------|-------------|
| `SDAR_D01_BUG_DETECTED` | 코드 버그 감지 | HIGH | AR-L4 |
| `SDAR_D02_REGRESSION` | 회귀 (이전엔 되던 것이 안 됨) 버그 | HIGH | AR-L4 |
| `SDAR_D03_DEPENDENCY_BREAK` | 의존성 (라이브러리) 깨짐 | HIGH | AR-L4 |
| `SDAR_D04_IMPORT_ERROR` | 모듈 임포트 (불러오기) 실패 | MEDIUM | AR-L3 |
| `SDAR_D05_TYPE_ERROR` | 타입 (데이터 형식) 불일치 | HIGH | AR-L4 |
| `SDAR_D06_CONFIG_SYNTAX_ERROR` | 설정 파일 구문 오류 | MEDIUM | AR-L3 |

### CATEGORY E: Security (보안 오류) — **LOCK: 자동수리 절대 금지** 🔒

> 도둑이 침입하거나 개인정보가 유출되는 문제. **어떤 상황에서도 자동수리 불가. 반드시 사람이 대응.**

| 오류 코드 | 설명 | 위험도 | 대응 |
|----------|------|--------|------|
| `SDAR_E01_INJECTION_DETECTED` | 프롬프트 인젝션 (악의적 입력) 감지 | CRITICAL | 즉시 차단 + 인간 알림 |
| `SDAR_E02_UNAUTHORIZED_ACCESS` | 무단 접근 시도 | CRITICAL | 즉시 차단 + 인간 알림 |
| `SDAR_E03_DATA_BREACH` | 데이터 유출 감지 | CRITICAL | 즉시 차단 + 인간 알림 |
| `SDAR_E04_PRIVILEGE_ESCALATION` | 권한 상승 시도 | CRITICAL | 즉시 차단 + 인간 알림 |
| `SDAR_E05_SAFETY_BYPASS` | 안전 필터 우회 시도 | CRITICAL | 즉시 차단 + 인간 알림 |
| `SDAR_E06_PII_EXPOSURE` | PII (개인식별정보) 노출 감지 | CRITICAL | 즉시 마스킹 + 인간 알림 |

> **변경 불가 (LOCK)**: CATEGORY E의 NEVER_AUTO (절대 자동수리 금지) 지정은 코드 수준에서 하드코딩되어 있으며, 설정으로 우회할 수 없습니다.

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §4.1, §9.5]

### 카테고리 × AR-Level 매트릭스

| 카테고리 | AR-L0 | AR-L1 | AR-L2 | AR-L3 | AR-L4 |
|---------|-------|-------|-------|-------|-------|
| **A (인프라)** | -- | 제안 | LOW 자동 | MEDIUM 자동 | HIGH 자동 |
| **B (모델)** | -- | 제안 | LOW 자동 | MEDIUM 자동 | HIGH 자동 |
| **C (로직)** | -- | 제안 | -- | MEDIUM 자동 | HIGH 자동 |
| **D (코드)** | -- | 제안 | -- | -- | HIGH 자동 |
| **E (보안)** | -- | 제안 | -- | -- | **NEVER** |

> `--` = 수리 안 함 / `제안` = 진단 결과만 알림 / `NEVER` = 어떤 수준에서도 자동수리 금지

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §4.2]

### 핵심 요약 (3줄)
1. SDAR는 오류를 5가지 카테고리(인프라/모델/로직/코드/보안)로 분류하며, 각 카테고리별 자동수리 가능 범위가 다릅니다.
2. 인프라(A) 오류는 대부분 자동수리 가능하지만, 코드(D) 오류는 AR-L4에서만, 보안(E) 오류는 절대 자동수리 금지입니다.
3. CATEGORY E의 NEVER_AUTO 지정은 LOCK(변경 불가) 규칙으로, 코드 레벨에서 하드코딩되어 우회 불가능합니다.

---

## §25.4 점진적 자율성 피라미드 (AR-L0 ~ AR-L4)

### 비유: 자녀의 자립 과정

아이가 성장하면서 자율성이 넓어지는 것과 같습니다:

| 단계 | 자녀 비유 | SDAR AR-Level |
|------|----------|--------------|
| 아기 | 모든 것을 부모가 결정 | AR-L0: 알림만 |
| 초등학생 | "이렇게 하면 어때?" 제안 | AR-L1: 진단 + 제안 |
| 중학생 | 용돈 범위 내에서 자유롭게 사용 | AR-L2: 안전한 수리 자동 |
| 고등학생 | 더 큰 결정도 하되, 부모에게 보고 | AR-L3: 복잡한 수리 자동 (알림) |
| 성인 | 대부분 자율적이지만 큰일은 상의 | AR-L4: 완전 자율 (V3 전용) |

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §3.1]

### AR-Level 상세 정의

| Level | 명칭 | 자동수리 범위 | 승인 방식 | 알림 |
|-------|------|-------------|----------|------|
| **AR-L0** | MANUAL (수동) | 수리 안 함 | 모든 수리에 인간 필요 | 로그만 기록 |
| **AR-L1** | NOTIFY_ONLY (알림만) | 진단 + 제안까지만 | 인간이 최종 결정 | UI 알림 + 수리 제안 |
| **AR-L2** | AUTO_SAFE (안전 자동) | LOW risk만 자동 | LOW는 자동, 나머지 인간 | 사후 요약 알림 |
| **AR-L3** | AUTO_MODERATE (중간 자동) | MEDIUM까지 자동 | 되돌릴 수 있는 것만 자동 + 즉시 알림 | 즉시 상세 알림 |
| **AR-L4** | AUTO_AGGRESSIVE (적극 자동) | HIGH까지 자동 | 스냅샷 필수 + 자동 + 즉시 알림 | 긴급 알림 + 롤백 가능 |

**시스템 기본값: AR-L2 (AUTO_SAFE)** — "안전한 것은 자동으로, 위험한 것은 확인 후"

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §3.1]

### 자율성 피라미드 다이어그램

```
                     ▲  AR-L4 (HIGH RISK)
                    ╱ ╲  코드 핫픽스, 마이그레이션
                   ╱   ╲  스냅샷 + 알림
                  ╱─────╲
                 ╱ AR-L3 ╲  설정 변경, 프롬프트 수정
                ╱ MODERATE╲  되돌릴 수 있는 것만 + 알림
               ╱───────────╲
              ╱   AR-L2     ╲  재시도, 재시작, 캐시 초기화
             ╱   AUTO_SAFE   ╲  완전 자동
            ╱─────────────────╲
           ╱  AR-L1 / AR-L0    ╲  수동 / 알림만
          ╱_____________________╲  사람이 결정
```

### AR-Level과 기존 Autonomy Level 관계

SDAR의 AR-Level은 기존 VAMOS Autonomy Level에 의해 **상한이 제한**됩니다:

| VAMOS Autonomy Level | 허용 가능한 최대 AR-Level | 제약 |
|---------------------|------------------------|------|
| **L0 (FULL_MANUAL)** | AR-L0 | 감지/진단만 가능 |
| **L1 (SUPERVISED)** | **AR-L2** (기본값) | LOW risk만 자동 |
| **L2 (SEMI_AUTO)** | AR-L3 | MEDIUM까지 자동 |
| **L3 (FULL_AUTO)** | AR-L4 | HIGH까지 자동 |

> **핵심 제약**: VAMOS Autonomy가 L3(FULL_AUTO)이라 해도, NEVER_AUTO 액션(안전 규칙, 비용 상한 변경 등)은 **절대** 자동 실행 불가.

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §3.2]

### AR-Level 변경 권한 (RBAC)

| RBAC 역할 | 설정 가능한 AR-Level | Emergency Kill Switch |
|----------|--------------------|--------------------|
| **OWNER** (소유자) | AR-L0 ~ AR-L4 | 사용 가능 |
| **ADMIN** (관리자) | AR-L0 ~ AR-L3 | 사용 가능 |
| **OPERATOR** (운영자) | AR-L0 ~ AR-L2 | 사용 가능 |
| **VIEWER** (조회자) | 변경 불가 (조회만) | 사용 가능 (비상 정지만) |

> AR-L4 설정은 **OWNER 권한 필수**. AR-Level 상승 시 I-19 Approval Manager 승인 필요.

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §3.3, §3.4]

### 알림 체계

| AR-Level | 감지 시 | 진단 완료 시 | 수리 실행 시 | 수리 완료 시 |
|----------|---------|------------|------------|------------|
| AR-L0 | 로그 기록 | 로그 기록 | N/A | N/A |
| AR-L1 | 로그 기록 | UI 팝업 + 수리 제안 | N/A (사용자 실행) | N/A |
| AR-L2 | 로그 기록 | 로그 기록 | 자동 실행 | 사후 요약 알림 |
| AR-L3 | 로그 기록 | 로그 기록 | 즉시 알림 + 자동 실행 | 즉시 상세 알림 |
| AR-L4 | 로그 기록 | 즉시 경고 | 긴급 알림 + 자동 실행 | 긴급 상세 알림 + 롤백 옵션 |

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §3.5]

### 핵심 요약 (3줄)
1. SDAR의 자율성은 AR-L0(수동)부터 AR-L4(적극 자동)까지 5단계 피라미드로 설계되어, 위험도에 따라 자동화 범위가 달라집니다.
2. 시스템 기본값은 AR-L2(AUTO_SAFE)이며, 기존 VAMOS Autonomy Level에 의해 AR-Level 상한이 제한됩니다.
3. AR-Level 상승에는 ADMIN 이상 권한이 필요하고, AR-L4는 OWNER만 설정할 수 있으며, NEVER_AUTO 액션은 어떤 수준에서도 절대 자동 실행 불가합니다.

---

## §25.5 SDAR 7-State 상태 머신

### 비유: 환자 진료 흐름도

병원 방문 과정을 생각해보세요:
- 대기실(Monitoring) → 접수(Detected) → 진단(Diagnosed) → 치료 계획(Prescribed) → 치료 중(Repairing) → 검사(Verified) → 퇴원(Done) → 다시 대기실

SDAR도 정확히 이 흐름으로 동작합니다.

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §7.1]

### 7가지 상태 (S0 ~ S6)

```
SDAR_S0_MONITORING  ──(이상 감지)──▶  SDAR_S1_DETECTED
       ▲                                   │
       │                             (진단 시작)
       │                                   ▼
  SDAR_S6_DONE  ◀──(완료)──  SDAR_S2_DIAGNOSED
       ▲                           │
       │                     (처방 생성)
       │                           ▼
       │                   SDAR_S3_PRESCRIBED
       │                           │
       │                     (수리 결정)
       │                           ▼
       │                   SDAR_S4_REPAIRING
       │                           │
       │                     (수리 완료)
       │                           ▼
       └────────────────  SDAR_S5_VERIFIED
```

### 상태별 상세

| 상태 | 설명 | 진입 조건 | 타임아웃 |
|------|------|---------|---------|
| **S0: MONITORING** | 정상 모니터링 대기 | 시스템 시작 / S6 완료 | 없음 (상시) |
| **S1: DETECTED** | 이상 감지 완료, 진단 대기 | Layer 1 신호 발행 | 30초 |
| **S2: DIAGNOSED** | 근본 원인 분석 완료 | Layer 2 완료 | 60초 |
| **S3: PRESCRIBED** | 수리 계획 수립 완료 | Layer 3 완료 | 30초 |
| **S4: REPAIRING** | 수리 실행 중 | Layer 4 실행 시작 | 액션별 상이 |
| **S5: VERIFIED** | 수리 후 검증 중 | Layer 5 시작 | 300초 (5분 관찰) |
| **S6: DONE** | 전체 프로세스 완료 | 최종 판정 | 10초 |

### 특수 전이 (분기점)

| 상황 | 전이 | 설명 |
|------|------|------|
| 오탐 (False Positive) | S1 → S0 | 이상이 아닌 것으로 판정, 모니터링 복귀 |
| 진단 실패 | S2 → S0 | 원인 특정 불가, 재시도 후 모니터링 복귀 |
| AR-L0/L1 | S3 → S6 | 알림만 발송 후 완료 (수리 실행 안 함) |
| 수리 불가 | S3 → S6 | 적용 가능한 수리 없음, 에스컬레이션 |
| 검증 실패 | S5 → S4 | 롤백 실행 후 재수리 시도 |

### 동시 실행 제한

| 제한 항목 | 값 | 사유 |
|----------|-----|------|
| 최대 동시 SDAR 인스턴스 | **3개** | 시스템 리소스 보호 |
| 동일 오류에 대한 병렬 SDAR | **1개** | 중복 수리 방지 |
| S4(수리 중) 동시 허용 | **1개** | 수리 간 간섭 방지 |

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §7.1, §7.2, §7.4]

### 핵심 요약 (3줄)
1. SDAR는 MONITORING→DETECTED→DIAGNOSED→PRESCRIBED→REPAIRING→VERIFIED→DONE의 7가지 상태로 순환합니다.
2. 각 상태에는 타임아웃이 설정되어 있어, 한 상태에 무한히 머무르지 않도록 보장합니다.
3. 동시 실행은 최대 3개 SDAR 인스턴스, 수리 실행은 1건만 허용되어 수리 간 간섭을 방지합니다.

---

## §25.6 수리 액션 카탈로그 (Repair Action Catalog)

### 비유: 의사의 처방전 목록

의사가 증상별로 "이 약 처방, 이 수술 처방" 이라는 정해진 카탈로그가 있듯, SDAR도 문제 유형별로 사용할 수 있는 **수리 액션 카탈로그**가 정해져 있습니다.

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §5.1]

### LOW Risk 수리 액션 (AR-L2 이상에서 자동 실행)

| 액션 ID | 명칭 | 비유 | 소요 시간 | 되돌림 |
|---------|------|------|----------|--------|
| `RA_001` | restart_service (서비스 재시작) | 컴퓨터 재부팅 | 10~60초 | 완전 가능 |
| `RA_002` | clear_cache (캐시 초기화) | 임시 파일 삭제 | 5~10초 | 완전 가능 |
| `RA_003` | retry_with_backoff (재시도) | "다시 한번 해볼게" | 1~12초 | 완전 가능 |
| `RA_004` | switch_model_fallback (모델 전환) | 주치의가 안 되면 다른 의사에게 | 5~15초 | 완전 가능 |
| `RA_005` | adjust_rate_limit (사용량 조절) | 속도 제한 조정 | 즉시 | 완전 가능 |

### MEDIUM Risk 수리 액션 (AR-L3 이상에서 자동 실행)

| 액션 ID | 명칭 | 비유 | 소요 시간 | 되돌림 |
|---------|------|------|----------|--------|
| `RA_006` | patch_prompt_template (프롬프트 수정) | 질문지 양식 수정 | 10~30초 | 완전 가능 |
| `RA_007` | update_config_parameter (설정 변경) | 온도 조절기 조절 | 5~15초 | 완전 가능 |
| `RA_008` | rotate_api_key (API 키 교체) | 열쇠 교체 | 15~60초 | 부분 가능 |
| `RA_009` | rollback_to_snapshot (스냅샷 복원) | 타임머신으로 되돌리기 | 30초~5분 | 완전 가능 |
| `RA_010` | compress_logs (로그 압축) | 오래된 서류 정리 | 30초~2분 | 부분 가능 |

### HIGH Risk 수리 액션 (AR-L4에서만 자동 실행)

| 액션 ID | 명칭 | 비유 | 소요 시간 | 되돌림 |
|---------|------|------|----------|--------|
| `RA_011` | patch_code_hotfix (코드 핫픽스) | 응급 수술 | 30초~5분 | 부분 가능 |
| `RA_012` | migrate_schema (스키마 마이그레이션) | 건물 구조 변경 | 1~10분 | 부분 가능 |
| `RA_013` | reinstall_dependency (의존성 재설치) | 부품 교체 | 1~5분 | 부분 가능 |
| `RA_014` | rebuild_vector_index (인덱스 재구축) | 도서관 색인 재정리 | 5~30분 | 완전 가능 |

### NEVER_AUTO 수리 액션 — **절대 자동 실행 금지** 🔒

| 액션 ID | 명칭 | 금지 사유 |
|---------|------|----------|
| `RA_NEVER_01` | modify_safety_rules (안전 규칙 변경) | 7개 불변 구역 (LOCK) |
| `RA_NEVER_02` | change_cost_ceiling (비용 상한 변경) | 7개 불변 구역 (LOCK) |
| `RA_NEVER_03` | alter_approval_flow (승인 흐름 변경) | 7개 불변 구역 (LOCK) |
| `RA_NEVER_04` | modify_non_goals (Non-goal 변경) | 7개 불변 구역 (LOCK) |
| `RA_NEVER_05` | change_audit_format (감사 형식 변경) | 7개 불변 구역 (LOCK) |
| `RA_NEVER_06` | alter_data_retention (보존 정책 변경) | 7개 불변 구역 (LOCK) |
| `RA_NEVER_07` | modify_user_consent (동의 설정 변경) | 7개 불변 구역 (LOCK) |
| `RA_NEVER_08` | escalate_own_privilege (자체 권한 상승) | RBAC 원칙 위반 |
| `RA_NEVER_09` | disable_guardrails (안전장치 비활성화) | 안전 Fail-safe 원칙 위반 |
| `RA_NEVER_10` | bypass_gate (Gate 우회) | Gate 우회 불가 (LOCK) |

> **변경 불가 (LOCK)**: NEVER_AUTO 액션은 코드에서 `frozenset`(변경 불가 집합)으로 하드코딩되어, 설정 파일로 우회할 수 없습니다.

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §5.1, §5.3]

### 수리 액션 실행 규칙

| 규칙 | 내용 |
|------|------|
| **반복 제한** | 동일 이슈에 동일 액션은 최소 60초 간격 (cooldown) |
| **스냅샷 의무** | MEDIUM/HIGH 수리 전 반드시 스냅샷 생성 |
| **NEVER_AUTO 절대 금지** | 코드 레벨에서 하드코딩 차단, 우회 불가 |
| **부작용 공개** | 모든 수리 알림에 예상 부작용 포함 필수 |
| **타임아웃** | 예상 소요 시간의 3배를 타임아웃으로 적용. 초과 시 강제 중단 + 롤백 |

### 버전별 활성화 수리 액션

| 버전 | 활성화 액션 | 위험도 범위 |
|------|-----------|-----------|
| **V1** | RA_001 ~ RA_005 | LOW만 |
| **V2** | V1 + RA_006 ~ RA_010 | LOW + MEDIUM |
| **V3** | V2 + RA_011 ~ RA_014 | LOW + MEDIUM + HIGH |
| **모든 버전** | RA_NEVER_01 ~ RA_NEVER_10은 **항상 금지** | NEVER_AUTO |

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §5.3, §10.1, §10.2, §10.3]

### 핵심 요약 (3줄)
1. SDAR 수리 액션은 LOW(5종)/MEDIUM(5종)/HIGH(4종)/NEVER_AUTO(10종)로 분류되며, 총 24종이 카탈로그에 등록되어 있습니다.
2. V1에서는 LOW 5종만, V2에서는 MEDIUM 5종 추가, V3에서는 HIGH 4종이 추가로 활성화됩니다.
3. NEVER_AUTO 10종은 모든 버전에서 절대 자동 실행이 금지되며, 코드 레벨 하드코딩으로 우회할 수 없습니다.

---

## §25.7 5-Gate 통합 (SDAR와 Gate 연동)

### 비유: 수리 전 안전 검문소

자동차 정비소에서도 수리 전에 여러 검문을 거칩니다:
- "이 수리가 규정에 맞나?" (PolicyGate)
- "수리비가 예산 내인가?" (CostGate)
- "고객 승인이 필요한가?" (ApprovalGate)
- "진단 근거가 충분한가?" (EvidenceGate)
- "수리 후 정상 작동하나?" (SelfCheckGate)

SDAR도 **모든 수리 액션이 5-Gate를 반드시 통과**해야 합니다. **Gate 우회는 절대 불가 (LOCK).**

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §6.1]

### Gate별 SDAR 연동 방식

| Gate | 검증 내용 | 적용 시점 |
|------|----------|---------|
| **PolicyGate** | 수리 액션이 Non-goal 위반하는가? | Layer 3 (처방 생성 시) + Layer 4 (실행 전) |
| **CostGate** | 수리로 추가 비용 발생하는가? (예: 모델 전환 시 비용 증가) | Layer 3 (처방 생성 시) |
| **ApprovalGate** | AR-L3/L4 수리 시 승인이 필요한가? | Layer 4 (실행 전) |
| **EvidenceGate** | 진단 근거가 충분한가? (근거 없는 수리 방지) | Layer 2 (진단 완료 시) |
| **SelfCheckGate** | 수리 후 품질이 유지되는가? | Layer 5 (검증 시) |

### Gate 통과 흐름

```
Layer 3 (처방 생성)
    ├──▶ PolicyGate:   정책 위반? → deny(거부) / restrict(제한) / allow(허용)
    ├──▶ CostGate:     비용 초과? → stop(중단) / downshift(저비용 대안) / normal(통과)
    └──▶ EvidenceGate: 근거 충분? → insufficient(부족) / sufficient(충분)

Layer 4 (수리 실행)
    └──▶ ApprovalGate: 승인 필요? → pending(대기, 10분) / denied(거부) / approved(승인)

Layer 5 (검증)
    └──▶ SelfCheckGate: 품질 유지? → FAIL(롤백) / WARN(경고) / PASS(통과)
```

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §6.1]

### 핵심 요약 (3줄)
1. SDAR의 모든 수리 액션은 PolicyGate, CostGate, ApprovalGate, EvidenceGate, SelfCheckGate의 5-Gate를 반드시 통과해야 합니다.
2. Gate 우회는 절대 불가(LOCK)이며, 각 Gate는 Layer 2~5의 적절한 시점에 검증을 수행합니다.
3. Gate에서 거부되면 해당 수리 후보는 제거되거나 대안 검색이 이루어집니다.

---

## §25.8 Emergency Kill Switch (긴급 중지)

### 비유: 공장의 비상 정지 버튼

공장에는 어디서든 누를 수 있는 빨간색 비상 정지 버튼이 있습니다. 누르면 모든 기계가 즉시 멈춥니다. SDAR의 **Emergency Kill Switch**도 동일합니다 — 누구든(VIEWER 포함) 즉시 SDAR 전체를 정지시킬 수 있습니다.

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §9.4]

### Kill Switch 상세

| 항목 | 내용 |
|------|------|
| **활성화 권한** | 모든 RBAC 역할 (VIEWER 포함) — 비상 상황이므로 권한 제한 없음 |
| **활성화 방법** | `vamos:sdar:kill_switch` IPC 명령 또는 UI 긴급 버튼 |
| **효과** | SDAR 전체 즉시 정지. 진행 중 수리는 안전 중단 (5초 유예 기간) |
| **중단 불가 시** | 강제 중단 + 스냅샷 복원 |
| **복구 방법** | ADMIN 이상 권한으로 Kill Switch 해제 후 SDAR 재시작 |
| **이벤트** | `oc.sdar.kill_switch.activated` / `oc.sdar.kill_switch.deactivated` |

### 자동 활성화 조건

Kill Switch는 수동으로만 누르는 것이 아닙니다. 특정 위험 상황에서 **자동으로 활성화**됩니다:

| 조건 | 설명 |
|------|------|
| `SDAR_ROLLBACK_FAILED` | 롤백마저 실패했을 때 — 수리도 실패하고, 되돌리기도 실패한 최악의 상황 |

> 이 경우 SDAR은 더 이상 어떤 자동 조치도 하지 않고, 즉시 인간에게 에스컬레이션합니다.

### 복구 절차

```
1. Kill Switch 활성화 → SDAR 전체 정지
2. 인간이 상황 파악 (로그, 진단 결과 확인)
3. 원인 해결
4. ADMIN 이상 권한으로 Kill Switch 해제
5. SDAR 재시작 → S0(MONITORING) 상태로 복귀
```

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §9.4]

### 핵심 요약 (3줄)
1. Emergency Kill Switch는 SDAR 전체를 즉시 정지시키는 비상 장치로, VIEWER를 포함한 모든 역할이 활성화할 수 있습니다.
2. 롤백 실패(SDAR_ROLLBACK_FAILED) 시 자동으로 Kill Switch가 활성화되어 인간에게 에스컬레이션됩니다.
3. Kill Switch 해제는 ADMIN 이상 권한만 가능하며, 해제 후 SDAR은 MONITORING 상태로 재시작됩니다.

---

## §25.9 보안 오류 특별 규칙 (LOCK) 🔒

### 비유: 은행 금고 보안

은행에서 금고 관련 이상이 감지되면, 어떤 직원도 혼자 판단해서 금고를 열거나 조치하지 않습니다. 반드시 경찰과 보안 담당자가 함께 확인합니다. SDAR도 **보안 오류(CATEGORY E)에 대해서는 절대 자동 수리를 하지 않습니다**.

> **변경 불가 (LOCK)**: 이 규칙은 어떤 AR-Level에서도, 어떤 설정으로도 변경할 수 없습니다.

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §9.5]

### CATEGORY E 특별 규칙 5가지

| # | 규칙 | 설명 |
|---|------|------|
| 1 | **자동수리 절대 금지** | 어떤 AR-Level에서도 CATEGORY E는 자동수리 불가 (NEVER_AUTO 고정) |
| 2 | **즉시 차단** | 감지 즉시 해당 요청/세션 차단 (피해 확산 방지) |
| 3 | **감사 로그 강제** | CRITICAL 심각도로 감사 로그 기록 (삭제/수정 불가) |
| 4 | **인간 알림 필수** | 모든 알림 채널로 즉시 통보 |
| 5 | **관련 데이터 보존** | 포렌식 (디지털 수사) 분석을 위해 관련 데이터 **30일 보존** |

### 보안 오류 대응 흐름

```
보안 이상 감지 (Layer 1)
     │
     ▼
  즉시 차단 (해당 요청/세션)
     │
     ▼
  CRITICAL 감사 로그 기록
     │
     ▼
  모든 채널로 인간에게 즉시 알림
     │
     ▼
  관련 데이터 30일 보존
     │
     ▼
  인간이 직접 조사 및 대응
```

> **중요**: SDAR는 보안 오류를 **감지하고 알리는 것까지만** 자동으로 합니다. 대응은 반드시 사람이 합니다.

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §9.5]

### 핵심 요약 (3줄)
1. 보안 오류(CATEGORY E)는 NEVER_AUTO 고정으로, 어떤 AR-Level에서도 절대 자동수리가 금지됩니다 (LOCK).
2. 보안 이상 감지 시 즉시 차단, CRITICAL 감사 로그 기록, 전채널 인간 알림, 30일 데이터 보존이 자동 실행됩니다.
3. SDAR은 보안 오류를 감지하고 알리는 것까지만 자동이며, 실제 대응은 반드시 인간이 수행합니다.

---

## §25.10 Self-evo 원칙 준수 (LOCK) 🔒

### 비유: 의사의 윤리 강령

의사가 아무리 뛰어나도 의료 윤리 강령을 위반할 수 없듯, SDAR도 VAMOS의 **Self-evo (자기진화) 7대 불변 규칙**을 절대 위반할 수 없습니다.

> **변경 불가 (LOCK)**: SDAR의 모든 수리 활동은 Self-evo 원칙을 준수해야 합니다.

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §9.1, §9.3]

### SDAR이 절대 자동 수정할 수 없는 10개 NEVER_AUTO 영역(7개 불변구역 + 3개 운영금지) [근거: v13 DELTA-005~006]

| # | 불변 구역 | SDAR 행동 | 위반 시 대응 |
|---|---------|----------|-----------|
| 1 | **safety_rules** (안전 규칙) | 감지/진단까지만, 수리 제안도 금지 | SDAR 즉시 중단 + CRITICAL 알림 |
| 2 | **cost_ceiling** (비용 상한) | 비용 상한 변경은 인간만 가능 | SDAR 즉시 중단 + CRITICAL 알림 |
| 3 | **approval_flow** (승인 흐름) | 승인 구조 변경은 인간만 가능 | SDAR 즉시 중단 + CRITICAL 알림 |
| 4 | **non_goals** (Non-goal) | Non-goal 목록 변경 불가 | SDAR 즉시 중단 + CRITICAL 알림 |
| 5 | **audit_format** (감사 형식) | 감사 로그 형식 변경 불가 | SDAR 즉시 중단 + CRITICAL 알림 |
| 6 | **data_retention** (데이터 보존) | 보존 정책 변경 불가 | SDAR 즉시 중단 + CRITICAL 알림 |
| 7 | **user_consent** (사용자 동의) | 동의 설정 변경 불가 | SDAR 즉시 중단 + CRITICAL 알림 |
| 8 | **escalate_own_privilege** (자체 권한 상승) | RBAC 원칙 위반 — 자체 권한 상승 금지 | SDAR 즉시 중단 + CRITICAL 알림 |
| 9 | **disable_guardrails** (안전장치 비활성화) | Fail-safe 원칙 위반 — Guardrails 비활성화 금지 | SDAR 즉시 중단 + CRITICAL 알림 |
| 10 | **bypass_gate** (Gate 우회) | Gate 우회 불가 (LOCK) — 검문소 우회 금지 | SDAR 즉시 중단 + CRITICAL 알림 |

> [근거: v13 DELTA-005~006] 기존 7개 불변구역에 3개 운영금지 항목 추가 → 총 10개 NEVER_AUTO 영역

### 코드 레벨 보장

이 10개 NEVER_AUTO 영역은 **코드에서 `frozenset`(변경 불가능한 집합)으로 하드코딩**되어 있습니다:

```python
NEVER_AUTO_TARGETS: frozenset = frozenset({
    "safety_rules", "cost_ceiling", "approval_flow",
    "non_goals", "audit_format", "data_retention",
    "user_consent", "escalate_own_privilege",
    "disable_guardrails", "bypass_gate",
})
```

> 설정 파일이나 관리자 권한으로도 이 제한을 우회할 수 없습니다. 코드 자체를 수정해야만 변경 가능하며, 그 코드 수정 자체가 Self-evo 거버넌스(S-8) 승인을 필요로 합니다.

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §9.1, §9.3]

### Self-evo 원칙과 SDAR의 관계

| 원칙 | SDAR에서의 적용 |
|------|---------------|
| **자동 적용 절대 금지** | Layer 3에서 생성된 수리 계획은 "제안"으로 간주. AR-L2~L4에서의 자동 실행은 "사전 승인된 안전 범위 내의 실행"이지, Self-evo 자동 적용이 아님 |
| **S-Module 변경 시 거버넌스 승인** | SDAR가 학습한 새로운 수리 패턴을 S-Module에 적용하려면 반드시 S-8 거버넌스 승인 필요 |
| **모든 수리 활동 보고** | SDAR의 모든 수리 활동은 SDARGovernanceReport로 S-8에 보고 |

### 추가 LOCK 규칙들

| 규칙 | 내용 (변경 불가) |
|------|----------------|
| 시간당 최대 자동 수리 횟수 | 동일 이슈당 **최대 3회** |
| 동시 수리 실행 | **최대 1건** |
| 동시 SDAR 인스턴스 | **최대 3건** |
| MEDIUM/HIGH 수리 전 스냅샷 | **필수** |
| 모든 수리 활동 알림 | **필수** |
| 승인 대기 타임아웃 | **최대 10분** |
| 수리 후 관찰 기간 | **최소 5분 (300초)** |
| 롤백 타임아웃 | **최대 300초** |
| 동일 액션 반복 간격 | **최소 60초** |

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §9.2, §9.3]

### 핵심 요약 (3줄)
1. SDAR는 Self-evo 원칙을 엄격히 준수하며, 10개 NEVER_AUTO 영역(7개 불변구역 + 3개 운영금지)은 절대 자동 수정 불가입니다 (LOCK). [근거: v13 DELTA-005~006]
2. 이 제한은 코드 레벨에서 `frozenset`으로 하드코딩되어 설정이나 권한으로 우회할 수 없습니다.
3. SDAR의 모든 수리 활동은 S-8 Self-evo Governance에 보고되며, 새로운 수리 패턴의 S-Module 적용은 반드시 거버넌스 승인이 필요합니다.

---

## 전체 검증 체크리스트

- [x] 5-Layer Pipeline 모두 설명 (§25.2)
- [x] AR-L0~L4 자율성 피라미드 (§25.4)
- [x] 7-State 상태 머신 (§25.5)
- [x] 수리 액션 카탈로그 (§25.6)
- [x] Kill Switch (§25.8)
- [x] 보안 오류 LOCK 규칙 (§25.9)
- [x] 비유 설명 포함 (각 섹션)
- [x] 근거 SOT 참조 표기 (각 섹션)
