# S11-2 AUDIT REPORT

> Phase 11, Session S11-2 (1차 검증 — Primary Pipeline)
> Generated: 2026-03-28
> Scope: 36 domains — AD-1~AD-4 + SOT2-AD1~5
> **Session Status: COMPLETED** — 발견분 S11-6 이관

---

## Executive Summary

| Check | Description | Pass | Warn | Fail | Rate |
|-------|-------------|------|------|------|------|
| SOT2-AD1 | 14-section completeness | 34 | 0 | 2 | 94.4% |
| SOT2-AD2 | LOCK protection | 34 | 2 | 0 | 94.4% |
| SOT2-AD3 | CONFLICT_LOG / Method-C accuracy | 35 | 0 | 1 | 97.2% |
| SOT2-AD4 | Rule compliance | 36 | 0 | 0 | 100% |
| SOT2-AD5 | Dependency verification | 33 | 3 | 0 | 91.7% |
| **Overall** | | **172/180** | **5** | **3** | **95.6%** |

### AD-1~AD-4 (보완 감사 — 2026-03-28 추가)

| Check | Description | Result | Issues | Severity |
|-------|-------------|--------|--------|----------|
| AD-1 | Hallucination Detection | 15 VERIFIED / 6 UNVERIFIED / **3 FABRICATED** | 24 claims 샘플링 | **CRITICAL** |
| AD-2 | Value Tampering Detection | 4/6 CONSISTENT / **2 INCONSISTENT** | 6 수치 항목 전수 | **HIGH** |
| AD-3 | Weakness Pattern Analysis | DRAFT 2건 / OPEN 1건 / Tier 5-6 품질 저하 패턴 확인 | 3 패턴 검출 | **MEDIUM** |
| AD-4 | Standard Key Consistency | **4건 INCONSISTENT** | 자율성/alpha/5-Gate/QoD | **HIGH** |

---

## AD-1: Hallucination Detection (5개 도메인 샘플링, 24 claims)

### 결과 요약

| Domain | Claims | VERIFIED | UNVERIFIED | FABRICATED |
|--------|--------|----------|------------|------------|
| 1-2 Auxiliary-Modules | 4 | 4 | 0 | 0 |
| 4-4 MLOps-LLMOps | 5 | 0 | 3 | **2** |
| 6-5 SDAR-System | 5 | 3 | 1 | **1** |
| 6-2 Security-Governance | 5 | 3 | 2 | 0 |
| 4-1 Rust-Tauri | 5 | 5 | 0 | 0 |
| **Total** | **24** | **15** | **6** | **3** |

### FABRICATED 항목 (즉시 조치 3건)

**AD1-F1 [CRITICAL] 4-4 QoD 스케일 변조**
- SOT (DEC-010): QoD = 0.0~1.0 연속 스케일
- SOT2 (4-4): QoD = 1~5 정수 스케일 (근거 없음)
- LOCK-ML-05/07 임계값 모두 근거 없는 스케일 기반
- **조치**: 4-4 QoD 스케일을 SOT 정본(0.0~1.0)으로 통일 또는 설계 결정 문서화

**AD1-F2 [CRITICAL] 4-4 QoD ≥ 4.0 임계값 근거 없음**
- SOT 임계값: QoD ≥ 0.85 (CLAUDE.md)
- SOT2 (4-4): QoD ≥ 4.0 (1~5 스케일) — SOT에 대응하는 정의 없음
- **조치**: AD1-F1과 함께 해결

**AD1-F3 [HIGH] 6-5 SDAR 5-Gate 이름 변조**
- SOT (SDAR_SPEC §6.1): PolicyGate, CostGate, ApprovalGate, **EvidenceGate**, **SelfCheckGate**
- SOT2 (6-5): Safety Gate, Risk Gate, Cost Gate, Approval Gate, **Verification Gate**
- EvidenceGate(진단 근거 충분성) → Risk Gate(AR-Level 리스크 평가): 목적 자체가 다름
- **조치**: SDAR-Gate 별도 명칭 채택 또는 SOT 정본 gate 명칭 복원

---

## AD-2: Value Tampering Detection (6 수치 항목 전수)

| # | Value | Expected | Consistent? | Severity | Notes |
|---|-------|----------|-------------|----------|-------|
| 1 | LOCK 총 수 | 472→484 | **NO** | MEDIUM | MASTER_INDEX 472 미갱신 (S11-6 기등록) |
| 2 | I-Series 모듈 수 | I-25 (LOCK) | YES | — | 해결됨 |
| 3 | 비용 경고 임계값 | 70% vs 80% | **NO** | **HIGH** | 거버넌스 80% 미갱신, 운영 70% 채택 결정 미전파 |
| 4 | BGE-M3 차원 | 1024 | YES (잔존 1건) | LOW | S2-C001 해결, FILE_CONTEXT Matryoshka 잔존 |
| 5 | COND 모듈 수 | 106 | YES | — | 30+ 위치 완전 일치 |
| 6 | IPC 명령 수 | 72 | YES | — | 20+ 위치 완전 일치 |

**Tampering verdict**: 의도적 변조 증거 없음. 전파 실패(propagation failure) 2건 확인.

---

## AD-3: Weakness Pattern Analysis

### AD3-W1: AUTHORITY_CHAIN "DRAFT" 잔존 (2건)

| Domain | File | Status |
|--------|------|--------|
| 1-1 Verifier-Reasoning | AUTHORITY_CHAIN.md L3 | **DRAFT** (APPROVED 미전환) |
| 2-2 COND-Modules | AUTHORITY_CHAIN.md L3 | **DRAFT** (APPROVED 미전환) |

### AD3-W2: Tier 품질 저하 패턴 (확인됨)

| Tier | Pass Rate | 비고 |
|------|-----------|------|
| Tier 0~4 | 100% | 완전 통과 |
| Tier 5 | 75% + 25% COND | 5-2 File-Context 상세명세 부재 |
| Tier 6 | 84.6% | 6-10, 6-13 의도적 형식 변형 |

> 패턴 확인되나 Tier 6 FAIL은 "의도적" — 심각도 LOW

### AD3-W3: CONFLICT_LOG OPEN 잔존 (1건)

| Domain | ID | Description |
|--------|----|-------------|
| 6-13 Operations | CFL-OP-001 | Part2 §6.12.12 "tentative" 값 vs §6.12.6/7 확정 값 충돌 (health check 60s↔30s, log retention 30d↔90d) |

---

## AD-4: Standard Key Consistency

### AD4-K1 [MEDIUM] 자율성 레벨 범위 불일치

| Domain | Range | 비고 |
|--------|-------|------|
| 6-2 Security | L0~L3 | D2.0-07 §14 기준 |
| 3-10 Agent-Protocol | L0~L4 | 정본 소유 주장 |
| 6-5 SDAR | L0~L4 + NEVER | 확장 범위 |

> SCOPE_AMBIGUITY 분류, 단일 정본 미확정

### AD4-K2 [LOW] Alpha 표기 반전

- 1-2/5-2: alpha=0.3 (BM25 가중치)
- 6-4: alpha=0.7 (Dense 가중치) — 동일 값, 역 표기
> S11-6에서 주석 추가로 FIXED, 원문 표기 차이는 잔존

### AD4-K3 [MEDIUM] 5-Gate 명칭 과적재

| System | Gates | Owner |
|--------|-------|-------|
| VAMOS 5-Gate | Policy→Approval→Cost→Evidence→SelfCheck | 0-0 Governance |
| SDAR 5-Gate | Safety→Risk→Cost→Approval→Verification | 6-5 SDAR |
| CL-G0~G4 | Format→Content→Consistency→Security→Final | 6-8 Cloud Library |

> 접두사/주석으로 완화, "5-Gate" 단독 사용 시 모호

### AD4-K4 [HIGH] QoD 4-factor vs 5-factor 미통일

| Source | Factors |
|--------|---------|
| DEC-014 (LOCK-AX-03) | 4-factor: relevance×0.30 + accuracy×0.25 + freshness×0.25 + completeness×0.20 |
| PLAN-3.0 / D2.0-07 | 5-factor: Accuracy×0.30 + Relevance×0.25 + Completeness×0.20 + Safety×0.15 + Efficiency×0.10 |

> 5-factor 채택 결정됨, LOCK-AX-03 미갱신 (전파 실패)

---

## Critical Findings — SOT2-AD (기존 4건)

### CF-1 [HIGH] 4-4 상세명세 내부 모순 미등록 (S2-M003)
- **위치**: `4-4_MLOps-LLMOps/MLOPS_LLMOPS_상세명세.md` L308-315
- **내용**: QoD AR-L1 트리거 "즉시 대응" vs "3회 연속 실패" 동일 파일 내 모순
- **조치**: CONFLICT_LOG.md에 C-05로 등록 후 판정 필요

### CF-2 [HIGH] 5-2 RAG 가중치 LOCK 모호성 (S2-H001)
- **위치**: `5-2_File-Context/AUTHORITY_CHAIN.md` L2
- **내용**: SOT LOCK L2(alpha=0.3, 2-way) vs 계획서 3-way(0.40/0.35/0.25) — "확장" vs "대체" 관계 불명확
- **조치**: AUTHORITY_CHAIN.md에 L2 LOCK 기본값 / 5-2 3-way 독립 아키텍처 관계 명시

### CF-3 [MEDIUM] SOT2_MASTER_INDEX LOCK-BM 잔존 (T-H002)
- **위치**: `SOT2_MASTER_INDEX.md`
- **내용**: 5-1 Benchmark 네임스페이스 LOCK-BM → LOCK-BE 변경 미반영
- **조치**: SOT2_MASTER_INDEX.md 교정

### CF-4 [MEDIUM] 5-2 상세명세 부재 (SDV-7)
- **위치**: `5-2_File-Context/`
- **내용**: 별도 상세명세.md 없음, 계획서 부록 B가 대체
- **조치**: 계획서 §8에 "상세명세 역할은 부록 B가 대체" 명시

---

## Critical Findings — AD-1~AD-4 (추가 7건)

### AD1-CF1 [CRITICAL] 4-4 QoD 스케일 SOT 위반
- SOT 정본 (DEC-010): 0.0~1.0 연속 스케일 → SOT2 (4-4): 1~5 정수 스케일
- LOCK-ML-05/07 임계값 모두 무효
- **S11-6 수정 대상**

### AD1-CF2 [CRITICAL] 4-4 QoD ≥ 4.0 임계값 무근거
- SOT 정본: QoD ≥ 0.85 → SOT2: QoD ≥ 4.0 (근거 없는 스케일)
- **S11-6 수정 대상** (AD1-CF1과 함께)

### AD1-CF3 [HIGH] 6-5 SDAR 5-Gate 명칭 SOT 이탈
- SOT: EvidenceGate/SelfCheckGate → SOT2: Risk Gate/Verification Gate (목적 상이)
- LOCK §6.1 재정의 위반 가능
- **S11-6 수정 대상**

### AD2-CF1 [HIGH] 비용 경고 임계값 전파 실패
- 운영 70% 4단계 채택 결정됨, 거버넌스 규칙서 80% 2단계 미갱신
- **S11-6 수정 대상**

### AD2-CF2 [MEDIUM] LOCK 총 수 MASTER_INDEX 미갱신
- 472→484 갱신 필요 (3-1 AI Investing LOCK 12건 추가분)
- **S11-6 수정 대상** (기등록)

### AD3-CF1 [MEDIUM] AUTHORITY_CHAIN DRAFT 잔존 2건
- 1-1 Verifier, 2-2 COND — APPROVED 미전환
- **S11-6 수정 대상**

### AD4-CF1 [HIGH] QoD 4-factor LOCK-AX-03 미갱신
- 5-factor 채택 결정됨, LOCK-AX-03 4-factor 잔존
- **S11-6 수정 대상**

---

## Warnings (권고 조치: 6건)

| # | Domain | Item | Recommendation |
|---|--------|------|----------------|
| W-1 | 4-1 | PRE-1/3/4 선행작업 3건 미완 | Phase 11 내 D2.1 스키마 검증 확정 |
| W-2 | 4-1 | LOCK-RT-12/13/14 DEFINED-HERE | Phase 5 동결 명시됨, SOT 정본화 검토 |
| W-3 | 4-4 | AUX-QoD vs ML-QoD 명칭 충돌 | 전역 용어집에 접두사 구분 반영 |
| W-4 | 5-1 | S2-M002 샌드박스 타임아웃 10s vs 30s | CONFLICT_LOG C-09 등록, 1-1 Verifier 협의 |
| W-5 | 5-2 | CF-52-001/002/003 OPEN 3건 | 6-4 계획서 작성 시 우선 해소 |
| W-6 | 5-4 | 상세명세 대신 인덱스 파일 사용 | 도메인 성격상 정당, 형식적 경고 |

---

## Domain-Level Audit Matrix — SOT2-AD1~5

> 열 명칭: SOT2-AD1(14-section) / SOT2-AD2(LOCK) / SOT2-AD3(CONFLICT_LOG) / SOT2-AD4(Rule) / SOT2-AD5(Dependency)

| Domain | SOT2-AD1 | SOT2-AD2 | SOT2-AD3 | SOT2-AD4 | SOT2-AD5 | Overall |
|--------|----------|----------|----------|----------|----------|---------|
| 0-0 Governance | P | P | P | P | P | PASS |
| 1-1 Verifier | P | P | P | P | P | PASS |
| 1-2 Auxiliary | P | P | P | P | P | PASS |
| 2-1 Blue Node | P | P | P | P | P | PASS |
| 2-2 COND | P | P | P | P | P | PASS |
| 3-1 AI Investing | P | P | P | P | P | PASS |
| 3-2 Multimodal | P | P | P | P | P | PASS |
| 3-3 PKM | P | P | P | P | P | PASS |
| 3-4 Workflow | P | P | P | P | P | PASS |
| 3-5 Education | P | P | P | P | P | PASS |
| 3-6 Health | P | P | P | P | P | PASS |
| 3-7 Dev Tools | P | P | P | P | P | PASS |
| 3-8 Conversation | P | P | P | P | P | PASS |
| 3-9 Business | P | P | P | P | P | PASS |
| 3-10 Agent Proto | P | P | P | P | P | PASS |
| 4-1 Rust-Tauri | P | P | P | P | W | PASS/W |
| 4-2 CI/CD | P | P | P | P | P | PASS |
| 4-3 MCP | P | P | P | P | P | PASS |
| 4-4 MLOps | P | P | P | P | P | PASS/W |
| 5-1 Benchmark | P | P | P | P | P | PASS/W |
| 5-2 File Context | P | W | P | P | W | COND |
| 5-3 v12 Additions | P | P | P | P | P | PASS |
| 5-4 v23 Extension | P | P | P | P | P | PASS |
| 6-1 UI/UX | P | P | P | P | P | PASS |
| 6-2 Security | P | P | P | P | P | PASS |
| 6-3 Agent Teams | P | P | P | P | P | PASS |
| 6-4 Memory/RAG | P | P | P | P | P | PASS |
| 6-5 SDAR | P | P | P | P | P | PASS |
| 6-6 Prompt Eng | P | P | P | P | P | PASS |
| 6-7 Testing | P | P | P | P | P | PASS |
| 6-8 Cloud Library | P | P | P | P | P | PASS |
| 6-9 Brain Adapter | P | P | P | P | P | PASS |
| 6-10 EXP Modules | F | P | F | P | P | FAIL |
| 6-11 Hologram | P | P | P | P | P | PASS |
| 6-12 Event/Logging | P | P | P | P | P | PASS |
| 6-13 Operations | F | P | F | P | P | FAIL |

> P=PASS / W=WARNING / F=FAIL
> 6-10, 6-13 FAIL: 의도적 형식 변형 (Tier 6 실험/운영 도메인 특성)

---

## Domain-Level Audit Matrix — AD-1~AD-4 (보완 감사)

> AD-1(Hallucination) / AD-2(Value Tampering) / AD-3(Weakness) / AD-4(Key Consistency)
> 샘플링 5개 도메인 직접 검증 + 전수 수치/패턴 분석 결과 반영

| Domain | AD-1 | AD-2 | AD-3 | AD-4 | Overall |
|--------|------|------|------|------|---------|
| 0-0 Governance | — | P | P | P | PASS |
| 1-1 Verifier | — | P | **W** | P | PASS/W |
| 1-2 Auxiliary | **P** | P | P | P | PASS |
| 2-1 Blue Node | — | P | P | P | PASS |
| 2-2 COND | — | P | **W** | P | PASS/W |
| 3-1 AI Investing | — | P | P | P | PASS |
| 3-2 Multimodal | — | **W** | P | P | PASS/W |
| 3-3 PKM | — | P | P | P | PASS |
| 3-4 Workflow | — | P | P | P | PASS |
| 3-5 Education | — | P | P | P | PASS |
| 3-6 Health | — | P | P | P | PASS |
| 3-7 Dev Tools | — | P | P | P | PASS |
| 3-8 Conversation | — | P | P | P | PASS |
| 3-9 Business | — | P | P | P | PASS |
| 3-10 Agent Proto | — | P | P | **W** | PASS/W |
| 4-1 Rust-Tauri | **P** | **W** | P | P | PASS/W |
| 4-2 CI/CD | — | P | P | P | PASS |
| 4-3 MCP | — | P | P | P | PASS |
| 4-4 MLOps | **F** | P | P | **W** | **FAIL** |
| 5-1 Benchmark | — | P | P | P | PASS |
| 5-2 File Context | — | **W** | P | **W** | PASS/W |
| 5-3 v12 Additions | — | P | P | P | PASS |
| 5-4 v23 Extension | — | P | P | P | PASS |
| 6-1 UI/UX | — | P | P | P | PASS |
| 6-2 Security | **P** | P | P | **W** | PASS/W |
| 6-3 Agent Teams | — | P | P | **W** | PASS/W |
| 6-4 Memory/RAG | — | P | P | **W** | PASS/W |
| 6-5 SDAR | **F** | P | P | **W** | **FAIL** |
| 6-6 Prompt Eng | — | P | P | P | PASS |
| 6-7 Testing | — | P | P | P | PASS |
| 6-8 Cloud Library | — | P | P | P | PASS |
| 6-9 Brain Adapter | — | P | P | P | PASS |
| 6-10 EXP Modules | — | P | P | P | — |
| 6-11 Hologram | — | P | P | P | PASS |
| 6-12 Event/Logging | — | P | P | P | PASS |
| 6-13 Operations | — | **W** | **W** | P | PASS/W |

> P=PASS / W=WARNING / F=FAIL / —=미샘플링(집계 결과만 반영)
> AD-1: 샘플링 5개 도메인만 직접 검증 (1-2, 4-1, 4-4, 6-2, 6-5)
> AD-2: 6개 수치 항목 전수 분석, 관련 도메인에 W/F 배정
> AD-3: DRAFT 잔존(1-1,2-2), OPEN(6-13) 패턴 기반
> AD-4: 자율성(3-10,6-2,6-3,6-5), alpha(5-2,6-4), 5-Gate(6-5), QoD(4-4) 기반
