# S11-2 SOT-CHECK REPORT

> Phase 11, Session S11-2 (1차 검증 — Primary Pipeline)
> Generated: 2026-03-28
> Scope: S11-1 CRITICAL 8건 + S11-2 추가 의심 6건 SOT 원본 직접 대조
> **Session Status: COMPLETED** — 발견분 S11-6 이관

---

## Executive Summary

| # | ID | Topic | SOT-Check Verdict | Action Required |
|---|-----|-------|-------------------|-----------------|
| 1 | SOT-C001 / X-C001 | I-Series 범위 + V0 모듈 K-1 | **MISMATCH** | 설계 결정 필요 |
| 2 | SOT-C002 | QoD 4-factor vs 5-factor | **MISMATCH** | PLAN-3.0 5-factor 채택 권장 |
| 3 | S2-C001 | BGE-M3 768 vs 1024 dim | **MISMATCH** | 1-2 상세명세 L251 수정 (768→1024) |
| 4 | N-C001 | 비용 경고 임계값 70% vs 80% | **MISMATCH** | 거버넌스 80% 2단계 vs 운영 70% 4단계 결정 |
| 5 | X-H001 | Failover chain 순서 | **MISMATCH** | Phase 8 심층 리뷰 대상 (OBS-001) |
| 6 | X-H002 | Guardrails 3-layer vs 4-layer | **MISMATCH** | 4th layer 정의 또는 SOT 3-layer 정렬 |
| 7 | SOT-C003 | React 18.3 vs 19 | **MISMATCH** | PHASE_B3 LOCK(18.3) 확인, STEP7-F 주석 |
| 8 | SOT-C004 | 보안 항목 14 vs 15 | **MISMATCH** | DEC-003 추가 명확화 |

**S11-1 분: 8/8 MISMATCH 확인 — 모두 SOT 원본에서 실제 충돌 확인됨**

### S11-2 추가 의심 항목 (프롬프트 요구: "추가 의심 항목")

| # | ID | Source | Topic | SOT-Check Verdict | Action Required |
|---|-----|--------|-------|-------------------|-----------------|
| 9 | S2-M003 | AUDIT CF-1 | 4-4 QoD AR-L1 트리거 "즉시 대응" vs "3회 연속 실패" | **MISMATCH** | CONFLICT_LOG C-05 등록 |
| 10 | S2-H001 | AUDIT CF-2 | 5-2 RAG 가중치 2-way(alpha=0.3) vs 3-way(0.40/0.35/0.25) | **PARTIAL** | AUTHORITY_CHAIN L2 관계 명시 |
| 11 | S2-M002 | VALIDATE W-4 | 5-1 샌드박스 타임아웃 10s vs 30s | **MISMATCH** | CONFLICT_LOG C-09 등록, 1-1 Verifier 협의 |
| 12 | CM-F3 | CROSS-MATCH F3 | 3-2 Multimodal 비용 per-call vs monthly 별도 체계 | **PARTIAL** | LOCK-MM-06 범위 명시 |
| 13 | CM-F4 | CROSS-MATCH F4 | 4-1 레지스트리 카운트 123→134, 36→48, 23→35 stale | **SHIFTED** | 4-1 LOCK-RT-06/07/08 갱신 또는 baseline 명시 |
| 14 | CM-F6 | CROSS-MATCH F6 | LLM Fallback chain 범위 미문서화 (Verifier vs General) | **PARTIAL** | 각 LOCK에 적용 범위 명시 |

**추가분: 2 MISMATCH / 3 PARTIAL / 1 SHIFTED**
**전체 합산: 10 MISMATCH / 3 PARTIAL / 1 SHIFTED (총 14건)**

---

## Detail

### 1. SOT-C001 / X-C001: I-Series 범위 + V0 모듈 세트

| Source | Value |
|--------|-------|
| D2.0-02 §2 (old) | I-21 modules |
| D2.0-02 (D2.0 update) | I-24 modules |
| LOCK (최신) | I-25 modules |
| V0 K-1 (SOT) | 7 modules (I-1,I-2,I-5,I-8,I-9,I-19,I-20) |
| V0 K-1 (SOT2) | 5 modules (I-1,I-2,I-3,I-5,I-19) |

**Verdict**: MISMATCH — I-Series 총 수 및 V0 활성 세트 양쪽 불일치
**Resolution**: D2.0-01 §8.5.2(B) 기준으로 K-1 통일 필요, I-Series 범위는 LOCK I-25 채택

### 2. SOT-C002: QoD Formula

| Source | Formula |
|--------|---------|
| DEC-014 | 4-factor (element order A) |
| PLAN-3.0 | 5-factor (element order B, reversed) |

**Verdict**: MISMATCH — 인자 수 + 순서 모두 상이
**Resolution**: PLAN-3.0이 상위 권한 → 5-factor 채택, MASTER_SPEC 갱신 권장

### 3. S2-C001: BGE-M3 Embedding Dimension

| Source | Value |
|--------|-------|
| 1-2 상세명세 본문 L251 | 768-dim |
| LOCK-AX-07 | 1024-dim |
| 6-4 LOCK-MR-011 | 1024-dim + Matryoshka 256-dim |

**Verdict**: MISMATCH — 본문 768 vs LOCK 1024
**Resolution**: L251 텍스트 768→1024 수정 (LOCK-AX-07이 정본)

### 4. N-C001: Cost Warning Threshold

| Source | Value |
|--------|-------|
| 0-0 Governance | 80% 2-stage alert |
| 6-13 Operations LOCK-OP-07 | 70% 4-stage alert (70/80/90/95%) |

**Verdict**: MISMATCH — 임계값 시작점 및 단계 수 상이
**Resolution**: 아키텍처 결정 필요 — 운영 4단계(70%) 채택 시 거버넌스 갱신

### 5. X-H001: Failover Chain Order

| Source | Chain |
|--------|-------|
| SOT (D2.0-02) | GPT-4o → Claude → Ollama (3-tier) |
| SOT2 (6-9 Brain-Adapter) | Claude → GPT-4o → DeepSeek → Ollama (4-tier) |

**Verdict**: MISMATCH — 순서 및 단계 수 상이
**Resolution**: Phase 8 심층 리뷰 대상 (이미 OBS-001 등록). 범위별 분리 가능 (Verifier vs General)

### 6. X-H002: Guardrails Layer Count

| Source | Layers |
|--------|--------|
| SOT | 3-layer (버전 구분 없음) |
| SOT2 | V1=2, V2=3, V3=4 (progressive) |

**Verdict**: MISMATCH — SOT 단일 3-layer vs SOT2 버전별 진화
**Resolution**: SOT2 progressive 모델 채택 시 SOT 갱신, 또는 4th layer 정의 명확화

### 7. SOT-C003: React Version

| Source | Version |
|--------|---------|
| LOCK (PHASE_B3) | React 18.3 |
| STEP7-F | React 19 |

**Verdict**: MISMATCH — LOCK 18.3 vs STEP7-F 19
**Resolution**: PHASE_B3 LOCK(18.3) 우선, STEP7-F에 "V1-014: React 18.3 (LOCK)" 주석 추가

### 8. SOT-C004: V1 Security Items

| Source | Count |
|--------|-------|
| READINESS docs | 14 items |
| DEC-003 이후 | 15 items (Allowlist 추가) |

**Verdict**: MISMATCH — DEC-003 추가분 미반영
**Resolution**: READINESS docs에 15번째 항목(DEC-003 Allowlist) 추가 명시

---

## Resolution Priority

| Priority | Items | Action |
|----------|-------|--------|
| **즉시 수정 가능** | #3 (BGE-M3), #7 (React), #8 (Security), #13 (카운트 stale) | 텍스트 수정만으로 해결 |
| **설계 결정 필요** | #1 (K-1), #2 (QoD), #4 (Cost), #6 (Guardrails), #9 (AR-L1 트리거), #11 (타임아웃) | 아키텍처 리뷰 후 정본 결정 |
| **문서화/명시 필요** | #10 (RAG 관계), #12 (비용 범위), #14 (Fallback 범위) | LOCK/AUTHORITY_CHAIN 주석 추가 |
| **Phase 8 이관** | #5 (Failover) | 기등록 OBS-001, 심층 리뷰 대기 |
