# S11-2 CROSS-MATCH REPORT

> Phase 11, Session S11-2 (1차 검증 — Primary Pipeline)
> Generated: 2026-03-28
> Scope: 36 domains — C1~C8 교차 매칭, 28 LOCK namespaces
> **Session Status: COMPLETED** — 발견분 S11-6 이관

---

## Executive Summary

| Category | Verdict | Issues |
|----------|---------|--------|
| C1: Numerical Values | **PARTIAL** | 3-2 Multimodal 비용 별도 체계 (per-call vs monthly) |
| C2: Count/List | **PARTIAL** | 4-1 레지스트리 카운트 stale (123→134, 36→48, 23→35) |
| C3: LOCK Cross-Ref | **CONSISTENT** | 28 namespace 고유, 소비 참조만 확인 |
| C4: Dependency Graph | **CONSISTENT** | 역참조 갭 전부 RESOLVED, Phase 9 추가분 반영 |
| C5: Terminology | **INCONSISTENT** | 5-Gate 명칭 충돌, 자율성 L0~L3 vs L4, alpha 표기 반전 |
| C6: Interface Contracts | **CONSISTENT** | VamosMessage, VectorStore 4-method 일치 |
| C7: Version/Phase | **CONSISTENT** | V0~V3 배정 정합 |
| C8: Authority Chain | **PARTIAL** | 1-1 Verifier DRAFT 잔존 |

**Overall: 4 CONSISTENT / 3 PARTIAL / 1 INCONSISTENT**

---

## HIGH Priority Findings (3건)

### F1: 5-Gate 명칭 충돌
- **위치**: 6-5 SDAR AUTHORITY_CHAIN L3
- **내용**: SDAR "5-Gate 통합 아키텍처" (Safety→Risk→Cost→Approval→Verification) ≠ 정본 VAMOS 5-Gate (Policy→Approval→Cost→Evidence→SelfCheck)
- **조치**: 6-5 SDAR의 gate를 "SDAR-Gate" 등 별도 명칭으로 변경하거나, 정본과의 차이 명시

### F2: 자율성 레벨 범위 불일치
- **위치**: 6-2 Security (L14) vs 3-10 Agent-Protocol vs 6-3 Agent-Teams
- **내용**: 6-2는 L0~L3 (D2.0-07 §14), 3-10은 L0~L4 (정본 소유 주장), 6-5 SDAR는 L0~L4+NEVER
- **조치**: 교차 도메인 disambiguation 문서화 필요

### F3: 3-2 Multimodal 비용 임계값 별도 체계
- **위치**: 3-2 LOCK-MM-06
- **내용**: V1=₩10K, V2=₩40K, V3=₩200K (per-call media processing) ≠ 정본 월간 상한 (₩40K/₩93K/₩266K)
- **조치**: LOCK-MM-06에 "per-call media cost cap" 범위 명시, 정본 월간 상한과의 차이 주석 추가

---

## MEDIUM Priority Findings (3건)

### F4: 4-1 레지스트리 카운트 stale
- **위치**: 4-1 LOCK-RT-06/07/08
- **내용**: D2.1-D2 기준 123/36/23 → 6-12 정본 134/48/35 미반영
- **조치**: 4-1 LOCK-RT-06/07/08을 6-12 정본 참조로 갱신하거나 "D2.1-D2 baseline" 명시

### F5: Hybrid Search alpha 표기 반전
- **위치**: 1-2 LOCK-AX-06 / 5-2 vs 6-4 LOCK-MR-008
- **내용**: 1-2/5-2는 alpha=0.3(BM25 가중치), 6-4는 alpha=0.7(Dense 가중치) — 동일 값, 역 표기
- **조치**: 전역 alpha 정의 통일 (권장: alpha=BM25_weight=0.3)

### F6: LLM Fallback Chain 범위 미문서화
- **위치**: 1-1 LOCK-VR-07 vs 6-9 LOCK-69-8
- **내용**: GPT-4o→Claude→Ollama (Verifier) vs Claude→GPT-4o→DeepSeek→Ollama (HAL 일반)
- **조치**: 각 LOCK에 적용 범위(Verifier-only vs General routing) 명시

---

## LOW Priority Findings (2건)

### F7: 1-1 Verifier AUTHORITY_CHAIN Status "DRAFT"
- 모든 다른 도메인은 "APPROVED" — 형식적 누락

### F8: LOCK-AT-014 / LOCK-AP-05 표현 차이
- "V1=3" vs "Lead + max 2 Sub-Agent" — 동일 값, 다른 프레이밍

---

## LOCK Namespace Uniqueness — PASS

28개 고유 LOCK 접두사 확인:
```
LOCK-AX, LOCK-VR, LOCK-MR, LOCK-AT, LOCK-BN, LOCK-CD, LOCK-AP,
LOCK-MM, LOCK-PKM, LOCK-ED, LOCK-HW, LOCK-WF, LOCK-A2A, LOCK-DT,
LOCK-RT, LOCK-CI, LOCK-ML, LOCK-BE, LOCK-EL, LOCK-HM, LOCK-MCP,
LOCK-BM, LOCK-610, LOCK-63, LOCK-69, LOCK-V12, LOCK-V23, LOCK-OP
```
교차 도메인 참조는 전부 소비(consuming) 참조 — 재정의(redefining) 0건.

---

## Verified Alignments (S11-1 연속)

S11-1에서 확인된 12개 정합 영역 유지:
Cost ceilings, Authority chain, P2 timeout, 9-State pipeline, P2 auto-OFF, MCP transport, LangChain ban, Blue Node caps, RBAC levels, Node-to-Node prohibition, Self-check thresholds, Single Decision principle.

추가 확인:
- VamosMessage 6-field schema (2-1, 3-10, 3-8) ✅
- VectorStore 4-method interface (1-2, 6-4) ✅
- Docker sandbox 30s timeout (1-1, 6-2) ✅
- IPC 72 commands (4-1 across 6-1, 3-7, 4-2) ✅
- COND 106 modules (2-2 consistent) ✅
