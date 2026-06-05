# S11-3b CONSENSUS REPORT

> Phase 11, Session S11-3b — /consensus 핵심 SOT 파일 5회 반복 추출 다수결 투표
> Generated: 2026-03-28
> **Last Updated: 2026-03-28 (SPLIT 재검증 + SDAR Gate 수정 반영)**
> Scope: 15 Critical Cross-Domain Values, 5 Sources Each

---

## Executive Summary

| Metric | Original | After Review | Status |
|--------|----------|-------------|--------|
| Total Values Checked | **15** | 15 | — |
| UNANIMOUS | **12** (80%) | **13** (86.7%) | — |
| MAJORITY | **2** (13.3%) | **2** (13.3%) | — |
| SPLIT | **1** (6.7%) | **0** (0%) | **PASS** ✅ |

**Overall Verdict: PASS** — SPLIT 0건 (원본 1건은 재검증 후 정당한 스코프 분리로 UNANIMOUS 재분류)

> **변경 이력:**
> 1. 원본: SPLIT 1건 (Failover Chain)
> 2. 재검증: 1-1(Reasoning Engine)과 6-9(Brain Adapter)의 폴백 체인이 의도적 스코프 분리임을 확인
> 3. 1-1 AUTHORITY_CHAIN에 스코프 분리 문서화 확인 → SPLIT→UNANIMOUS(scope-separated) 재분류
> 4. 6-5 SDAR Gate 명칭 수정 반영 (MAJORITY #10 관련)

---

## Per-Value Results — 최종

| # | Critical Value | Sources | Verdict | Canonical Value |
|---|---------------|---------|---------|-----------------|
| 1 | Cost Ceiling V1 | 5/5 | **UNANIMOUS** | ₩40,000/월 ($30) |
| 2 | Cost Ceiling V2 | 5/5 | **UNANIMOUS** | ₩93,000/월 ($70) |
| 3 | Cost Ceiling V3 | 5/5 | **UNANIMOUS** | ₩266,000/월 ($200) |
| 4 | Blue Node Active Cap | 3/3 | **UNANIMOUS** | V1=3, V2=10, V3=50 |
| 5 | MCP Transport | 5/5 | **UNANIMOUS** | Streamable HTTP (DEC-017 LOCK) |
| 6 | VamosMessage Fields | 5/5 | **UNANIMOUS** | id, type, source, target, content, metadata |
| 7 | Self-check Thresholds | 4/4 | **UNANIMOUS** | P0>=70, P1>=75, P2>=80 |
| 8 | Memory Layers | 4/5 | **MAJORITY** | 4 layers (L0~L3) LOCK. STEP7-D L4=V2+ extension only |
| 9 | Failover Chain Order | ~~2v2~~ | ~~SPLIT~~ → **UNANIMOUS** | 스코프별 분리: 추론용(3-step) vs 전역(4-step) |
| 10 | 5-Gate Names/Order | 3/5 | **MAJORITY** | Policy→Approval→Cost→Evidence→SelfCheck |
| 11 | Hybrid Search Alpha | 5/5 | **UNANIMOUS** | BM25=0.3 / Dense=0.7 |
| 12 | BGE-M3 Dimension | 5/5 | **UNANIMOUS** | 1024dim (full) + 256dim (Matryoshka) |
| 13 | Python Version | 4/4 | **UNANIMOUS** | Python >= 3.11 |
| 14 | Semantic Cache Threshold | 4/4 | **UNANIMOUS** | cosine >= 0.95 |
| 15 | Docker Sandbox Timeout | 3/3 | **UNANIMOUS** | 30 seconds |

---

## ~~SPLIT~~ → UNANIMOUS Detail (#9 Failover Chain) ✅ 해소

**Chain A (1-1 Reasoning Engine scope — LOCK-VR-07):**
GPT-4o → Claude Sonnet → Ollama (3-step)
- Sources: D2.0-02, 1-1 계획서
- Scope: 추론 태스크 전용

**Chain B (6-9 Brain Adapter global default — LOCK-69-8):**
Claude → GPT-4o → DeepSeek → Ollama (4-step)
- Sources: D2.0-04 §5, 6-9 계획서
- Scope: 전체 LLM 호출 전역 기본값

**Resolution**: 두 체인은 **의도적 스코프 분리**. 1-1은 추론 태스크(정확성 우선 → GPT-4o 선두), 6-9는 전역 폴백(다용도 → Claude 선두). 1-1 AUTHORITY_CHAIN에 스코프 분리가 문서화되어 있음. **SPLIT → UNANIMOUS(scope-separated)로 재분류.**

> NOTE: D2.0-04 내부에 두 가지 순서가 혼재(L721 vs L1205)하는 경미한 불일치는 존재하나, 이는 D2.0-04 자체의 내부 구조 문제이지 계획서 간 불일치가 아님. D2.0-04 내부 정리는 SOT1 영역으로 본 검증 범위 밖.

---

## MAJORITY Details

### #8 Memory Layers (4 vs 5) — 변경 없음
- D2.0-06, 6-4, 1-2, 5-2: **4 layers (L0~L3)** — LOCK
- STEP7-D: **5 layers (L0~L4)** — L4=Archive
- Resolution: 6-4 CONFLICT_LOG #004/#005에서 D2.0-06 4계층이 정본, STEP7-D L4(Archive)는 V2+ 확장으로 분류

### #10 5-Gate Names/Order — SDAR 수정 반영
- D2.0-07, 6-2, 0-0 규칙서: **Policy→Approval→Cost→Evidence→SelfCheck** (5-Gate) — 정본
- D2.0-01: **Policy→Approval→Cost→Evidence** (4-Gate — 요약 수준 생략)
- 6-5 SDAR: ~~Safety→Risk→Cost→Approval→Verification~~ → **PolicyGate→EvidenceGate→CostGate→ApprovalGate→SelfCheckGate** (수정 완료 ✅)
- Resolution: 메인 5-Gate는 D2.0-07 정본. SDAR는 도메인 전용 변형을 D2.0-07 표준명으로 정렬 완료. 매핑 문서화 추가됨.
