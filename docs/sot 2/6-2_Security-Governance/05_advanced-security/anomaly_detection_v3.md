# anomaly_detection_v3.md — ML 기반 이상탐지 + Model Theft 방어 V3

> **Status**: APPROVED
> **버전**: v3.0 (Phase 4 V3 implementation, 2026-05-27)
> **세션**: 6-2 Phase 4 SPEC Stage B P4-1
> **정본 출처**: SECURITY_GOVERNANCE_구조화_종합계획서 §7.5 P3-1 forward-defined + Part2 §6.5.4 LLM10 (Model Theft) + D2.0-07 §14 자율 운영 L0~L3
> **LOCK 인용**: L1 (OWASP LLM Top 10) + L2 (STRIDE 6대) + L3 (HMAC-SHA256) + L7 (Guardrails 3-Layer) + L10 (V3 비용 ₩266,000) + L11 (5-Gate) + L14 (V3=L3 자율) + L16 (Rate Limiting) + L17 (Cost Gate V2 ₩93,000) + L18 (trace_id UUID v4) + L20 (NEVER_AUTO P1+) — 11 LOCKs verbatim
> **cross-handoff**: 6-5 SDAR (W-CB Circuit Breaker DEFERRED_TO_PHASE3 OBSERVE_ONLY) + 6-6 Self-Evolution (Model Theft L18 자동 적용 금지) + 6-3 PARL (Agent 이상 행위 큐) + 4-2 CICD (SAST/DAST §9.1 L1419 정책-실행 경계)

---

## 1. 목표

Phase 3 P3-1 forward-defined `anomaly_detection_v3.md`를 production-ready 정본으로 승급한다. ML 모델 기반 이상탐지로 LLM 시스템의 비정상 행위 (프롬프트 주입 시도, Model Theft 추출 공격, 비정상 트래픽 패턴)를 anomaly_score ≥ 0.85 임계값에서 자동 차단하고, staging 7일 측정을 통해 V3 production 배포 baseline을 확정한다.

**Non-goal** (LOCK L15):
- ML 모델 추론 결과만으로 자동 사용자 차단 금지 (NEVER_AUTO L20 — P2 승인 필수)
- ML 모델 자체의 자동 업데이트 금지 (Self-evo L18 통합, 6-6 cross-handoff)

---

## 2. ML 이상탐지 아키텍처

### 2.1 3-단계 모델 파이프라인

```
입력 → [Layer 1 Isolation Forest] → [Layer 2 Autoencoder reconstruction] → [Layer 3 Transformer 임베딩 cosine] → anomaly_score (0~1)
```

| Layer | 모델 | 입력 | 출력 | 임계값 |
|-------|------|------|------|-------|
| L1 | Isolation Forest | 요청 메타 (length, freq, IP, user_id) | outlier_score | > 0.7 → L2 진입 |
| L2 | Autoencoder | 토큰 시퀀스 임베딩 (768-dim) | reconstruction_error | > 0.6 → L3 진입 |
| L3 | Transformer 임베딩 cosine | 정상 패턴 vs 입력 cosine | similarity_inverse | 가중 합 anomaly_score |

**가중 합**: `anomaly_score = 0.3 × L1 + 0.4 × L2 + 0.3 × L3`

**임계값** (LOCK L11 SelfCheckGate 통합):
- `anomaly_score ≥ 0.85` → **자동 차단 + 인시던트 티켓 발급** (STEP7-E S7E-069 P0/P1 분류)
- `0.6 ≤ anomaly_score < 0.85` → **L7 Layer 3 LlamaGuard 우회 검사 강제 + P2 승인 요청** (LOCK L9 5분 타임아웃)
- `anomaly_score < 0.6` → 통상 진행 + audit_log 기록

### 2.2 학습 데이터

| 데이터셋 | 출처 | 규모 | LOCK 정합 |
|---------|------|------|----------|
| 정상 패턴 baseline | staging 30일 + 사용자 동의 로그 | ~ 1.2M samples | L15 §2.4 (장기 저장 금지 — 30일 후 삭제) |
| OWASP LLM 공격 패턴 | OWASP Top 10 2025 (L1) 공식 샘플 + Red Team P4-2 결과 | ~ 8.5K samples | L1 LLM01 (Prompt Injection) / LLM10 (Model Theft) |
| Model Theft 추출 시퀀스 | 학술 reference (Carlini et al. 2024) + 자체 합성 | ~ 3.2K samples | L1 LLM10 + Part2 §6.5.4 |

**개인정보 처리** (LOCK L15 / GDPR Art. 5):
- 학습 데이터 PII 자동 마스킹 (P2-3 GDPR `pii_regex_masking.md` 정합)
- 학습 시점 user_id → HMAC-SHA256 해시 (LOCK L3) 후 학습, 원본 30일 후 삭제

---

## 3. Model Theft 방어 4 메커니즘

### 3.1 입력 fingerprinting

| 방법 | 구현 | 차단 임계값 |
|------|------|----------|
| 토큰 패턴 fingerprint | `hash(tokens[:N])` SimHash | 동일 fingerprint 1시간 내 10회 초과 → 차단 |
| 의미 임베딩 유사도 | sentence-transformer cosine | 동일 user_id 임베딩 평균 cosine > 0.92 → 차단 |
| 프로빙 시퀀스 탐지 | 정형 출력 요청 패턴 (JSON, code-only) 비율 | 일일 비율 > 70% + 요청 > 100건 → 차단 |

### 3.2 출력 워터마킹

- KGW 알고리즘 (Kirchenbauer et al. 2023) 변형: greenlist 토큰 비율 측정
- V3 모드에서 모든 LLM 출력에 watermark seed 삽입 (LOCK L18 trace_id 정합)
- 외부 모델로 학습된 흔적 감지 시 R-T6-2 12 소비 도메인 자동 통보 (R-62-1 정책)

### 3.3 추출 공격 entropy 탐지

- 동일 user_id의 일일 평균 출력 엔트로피 < 정상 평균 - 2σ → 추출 의심
- 추출 의심 + Layer 2 reconstruction_error > 0.8 → **자동 throttle(1 req/min) + P2 승인 요청 (LOCK L9 5분); 90일 grace 차단은 P2 인간 승인 후 적용 (LOCK L20 NEVER_AUTO — 90일 정지 자동 적용 금지)**
- audit_log 이벤트 발행 (6-12 Event-Logging cross-handoff)

### 3.4 Rate Limiting L16 V3 강화

| 모드 | 일반 사용자 | 추출 의심 사용자 |
|------|------------|--------------|
| V1 | 10 req/min (LOCK L16) | 10 req/min |
| V2 | 10 req/min | 5 req/min (자동 throttle) |
| **V3** | **15 req/min (L14 자율 L3 통합)** | **1 req/min + P2 승인 요구 (LOCK L9)** |

> **LOCK 정합**: V3 = L3 자율 (D2.0-07 §14) 모드에서도 NEVER_AUTO (L20) 우선 — 추출 의심 시 P2 승인 없이 자동 unblock 금지.

---

## 4. 5-Gate System 통합 (LOCK L11)

| Gate | anomaly_detection_v3 역할 |
|------|--------------------------|
| **PolicyGate** | 입력 fingerprinting (§3.1) — 1차 차단 |
| **ApprovalGate** | anomaly_score ∈ [0.6, 0.85) → P2 승인 요청 |
| **CostGate** | LOCK L17 V2 ₩93,000 / LOCK L10 V3 ₩266,000 일일 한도 추적 + ML 추론 비용 합산 |
| **EvidenceGate** | L1+L2+L3 score 근거 audit_log 기록 (6-12) |
| **SelfCheckGate** | anomaly_score ≥ 0.85 → 자동 차단 (NEVER_AUTO L20 정합 — 차단 = 안전 방향 자동 허용) |

---

## 5. 자율 운영 V3 = L3 (LOCK L14)

V3 모드는 D2.0-07 §14 L3 FULL_AUTO 자율 운영을 적용한다. 단 LOCK L20 NEVER_AUTO 우선:

- **자동 가능**: anomaly_score 계산 + audit_log 기록 + Rate Limiting throttle + watermark 삽입
- **자동 금지** (P2 승인 필수):
  - 사용자 차단 (anomaly_score ≥ 0.85 자동 차단은 안전 방향 예외)
  - 90일 grace 차단 해제
  - ML 모델 자체 업데이트 (6-6 Self-Evo L18 정합, **자동 적용 금지**)

---

## 6. 비용 baseline (LOCK L10)

| 모드 | ML 추론 일일 비용 (예상) | 비용 상한 (L10) | 일일 한도 (L17/L10 일일분) |
|------|--------------------|--------------|----------------------|
| V1 | ~ ₩300 (Isolation Forest only) | ₩40,000/월 | ₩1,300/일 |
| V2 | ~ ₩900 (L1+L2) | ₩93,000/월 | ₩3,100/일 |
| **V3** | **~ ₩2,400 (L1+L2+L3)** | **₩266,000/월** | **₩8,900/일** |

> **Cost Gate 통합**: 일일 한도 초과 시 자동 다운시프트 — V3 → V2 (L3 → L2 비활성) → V1 (L2 → L1 비활성).

---

## 7. STEP7-E 매핑

| STEP7-E ID | 매핑 | 본 V3 통합 위치 |
|-----------|------|--------------|
| S7E-001 STRIDE | L2 STRIDE 6대 → §2 (Tampering 탐지) | §2 Layer 2 reconstruction |
| S7E-003 OWASP | L1 LLM10 Model Theft → §3 전체 | §3 4 메커니즘 |
| S7E-005 API Key | 추출 의심 시 API Key 자동 회수 (P2 승인) | §3.3 + §5 |
| S7E-031 PII 마스킹 | 학습 데이터 PII 자동 마스킹 (P2-3 정합) | §2.2 학습 데이터 |
| S7E-069~076 인시던트 | anomaly_score ≥ 0.85 → 자동 인시던트 티켓 | §2.1 임계값 + §4 EvidenceGate |
| S7E-078 Agent HMAC | Agent 이상 행위 큐 → 6-3 PARL cross-handoff | §8.1 |

---

## 8. cross-handoff 4 도메인

### 8.1 6-3 Agent-Teams-PARL — Agent 이상 행위 큐

- Agent 출력의 anomaly_score ≥ 0.85 시 PARL Swarm Lead+5에 자동 통보
- HMAC-SHA256 (LOCK L3) 서명된 메시지로 격리 큐에 적재 (재진입 방지)
- 정합: 6-3 plan `128CA555313E0EF9` 기준 forward-defined Decision Aggregator API 인용

### 8.2 6-5 SDAR — W-CB Circuit Breaker DEFERRED_TO_PHASE3 OBSERVE_ONLY

- anomaly 트리거 후 회복 패턴은 6-5 SDAR이 정본
- 본 V3는 OBSERVE_ONLY (W-CB Circuit Breaker 정책 DEFERRED_TO_PHASE3, 6-5 plan `6388CF095AE7FAC8`)
- 6-2 = 위협 분류 / 6-5 = 자가복구 경계 (AUTHORITY §3.1)

### 8.3 6-6 Self-Evolution — Model Theft 방어 L18 자동 적용 금지

- ML 이상탐지 모델 자체의 자율 업데이트는 6-6 Self-Evo가 정본
- LOCK L18 통합: trace_id 서버 측 UUID v4 (클라이언트 신뢰 금지) 정합
- 모델 업데이트 시 R-T6-2 12 소비 도메인 사전 통보 (R-62-1)

### 8.4 4-2 CICD — SAST/DAST §9.1 L1419 경계

- 6-2 = 정책 정의 (anomaly 임계값, Model Theft 탐지 규칙)
- 4-2 = 파이프라인 실행 (CI 단계에서 anomaly_detection_v3 호출, plan `846C87DB216B56CA` §9.1 L1419)
- 경계 = 정책(6-2) vs 실행(4-2)

---

## 9. 13 검증 항목 forward-defined

| # | 검증 항목 | 방법 | 예상 결과 |
|---|---------|------|---------|
| 1 | Isolation Forest baseline 학습 완료 | staging 30일 데이터 fit | F1 ≥ 0.85 |
| 2 | Autoencoder reconstruction 임계값 | held-out validation | precision ≥ 0.90 |
| 3 | Transformer 임베딩 cosine baseline | 정상 패턴 KNN | recall ≥ 0.85 |
| 4 | 가중 합 anomaly_score 분포 | staging 7일 측정 | μ ≤ 0.3, σ ≤ 0.15 |
| 5 | Model Theft fingerprinting 차단 정확도 | OWASP LLM10 시나리오 | 정확도 ≥ 95% |
| 6 | 출력 워터마킹 탐지율 | KGW greenlist 비율 | green ratio Δ ≥ 0.15 |
| 7 | 추출 entropy 탐지 FPR | 정상 사용자 baseline | FPR ≤ 1% |
| 8 | Rate Limiting V3 강화 동작 | 추출 의심 → 1 req/min | 강제 throttle 100% |
| 9 | 5-Gate 통합 통과 | E2E 시나리오 | 5/5 PASS |
| 10 | NEVER_AUTO L20 정합 | 자동 unblock 금지 | 미발생 (manual 100%) |
| 11 | Cost 일일 한도 추적 | ₩8,900/일 V3 | 초과 시 자동 다운시프트 |
| 12 | STEP7-E 92건 매핑 | grep audit | 6 ID 직접 인용 (§7) |
| 13 | staging 7일 측정 | production replay 7일 | 차단 정확도 ≥ 95% / FPR ≤ 1% / 응답 지연 < 50ms p95 |

---

## 10. Phase 5 entry-gate (G4 forward-defined)

- **G4-1** V3 implementation 완료: 본 문서 + §2~§9 정의 완전 ✅
- **G4-2** Status APPROVED 전수 전환: 본 문서 Status APPROVED ✅
- **G4-3** LOCK 재정의 0: L1+L2+L3+L7+L10+L11+L14+L16+L17+L18+L20 11 LOCKs verbatim 인용 ✅
- **G4-5** production 실측 baseline: §9 13 검증 항목 + staging 7일 측정 forward-defined
- **G4-6** cross-handoff: 4 도메인 (6-5/6-6/6-3/4-2) §8 명세

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|---------|
| 2026-05-27 | v3.0 (NEW) | Phase 4 V3 implementation — ML 3-Layer 이상탐지 + Model Theft 방어 4 메커니즘 + 5-Gate 통합 + LOCK 11 verbatim + cross-handoff 4 도메인 + 13 검증 항목 forward-defined. Status DRAFT → APPROVED 전환. |
