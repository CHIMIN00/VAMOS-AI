# S11-1 SOT CONFLICT REPORT

> Phase 11, Session S11-1 (Pre-Check) — Full Conflict Scan
> Generated: 2026-03-28
> Scope: 6 scans executed in parallel

---

## Executive Summary

| Scan | CRITICAL | HIGH | MEDIUM | WARNING | LOW/INFO | Total |
|------|----------|------|--------|---------|----------|-------|
| 3. SOT 68 internal (`scan`) | 4 | — | — | 11 | 4 | **19** |
| 4. SOT2 internal (`sot2-scan`) | 1 | 2 | 3 | — | 1 | **7** |
| 5. SOT vs SOT2 (`sot2-vs-sot`) | 1 | 2 | 3 | — | 1 | **7** |
| 6. SOT2 vs Part2 (`sot2-vs-part2`) | — | — | — | 3 (OBS) | — | **3** |
| 7. SOT2 numbers (`sot2-numbers`) | 1 | — | 1 | — | 2 | **4** |
| 8. SOT2 terms (`sot2-terms`) | — | 2 | 4 | — | 9 | **15** |
| **Totals (deduplicated)** | **~7** | **~6** | **~11** | **~14** | **~17** | **~55 raw** |

> Note: Some conflicts overlap across scans (e.g., Failover Chain found in both scan 3 and scan 5). Deduplicated unique conflicts estimated at ~40 distinct issues.

---

## PART A: SOT 68 Internal Conflicts (Scan 3)

### CRITICAL (4)

| ID | Topic | Conflict | Files |
|----|-------|----------|-------|
| SOT-C001 | I-Series module count | I-21 (old) vs I-24 (D2.0-02) vs I-25 (LOCK) | 7+ |
| SOT-C002 | QoD weight formula | 4-factor (DEC-014) vs 5-factor (PLAN-3.0) — element order also reversed | 6+ |
| SOT-C003 | React version | React 18.3 (LOCK) vs React 19 (STEP7-F) | 5 |
| SOT-C004 | V1 security items | 14 items vs 15 items (DEC-003 Allowlist addition unclear) | 5 |

### WARNING (11)

| ID | Topic | Conflict |
|----|-------|----------|
| SOT-W001 | Budget alert thresholds | 6+ different stage definitions (50/60/70/80/85/90/95/100%) across 8+ files |
| SOT-W002 | Test coverage V1 | Unit: 70% (D2.0-04) vs 80%+ (PHASE_B5); Integration: 60% vs 90% |
| SOT-W003 | STEP7 total items | 1,050 vs 1,485 vs 1,545 |
| SOT-W004 | E-15 module name | "File System" vs "Cloud Collector" vs combined |
| SOT-W005 | S-5 module name | "Router Evolution" vs "Cloud Evolver" vs "Cloud Library Evolver" |
| SOT-W006 | SDAR full name | "Self-Directed Adaptive Reasoning" vs "Self-Diagnosis & Auto-Repair" |
| SOT-W007 | E-Series count | 8 (D2.0-02 section) vs 16 (full count) |
| SOT-W008 | V2 cost in STEP7_R4/R5 headers | W40K (V1 value) vs W93K (correct V2 LOCK) |
| SOT-W009 | V3 cost mixing | W100K (pricing) vs W200K (sub-budget) vs W266K (LOCK ceiling) |
| SOT-W010 | Python version | 3.11+ (LOCK) vs 3.12 (AI Investing D-S5-01) |
| SOT-W011 | D7 REF schema version | v2.1.0 inline refs vs v3.0.0 actual |

### INFO (4)

| ID | Topic |
|----|-------|
| SOT-I001 | D6 REF schema version v2.2.0 residual |
| SOT-I002 | AI Investing data sources 83 vs 93 (evolution, both valid) |
| SOT-I003 | D2.0-01 internal I-24 (section 10) vs I-25 (section 5.6) |
| SOT-I004 | STEP7 items 1,545 vs 1,547 (rounding, self-documented) |

---

## PART B: SOT2 Internal Conflicts (Scan 4)

### CRITICAL (1)

| ID | Topic | Conflict |
|----|-------|----------|
| S2-C001 | BGE-M3 embedding dimension | Body text: 768-dim vs LOCK-AX-07: 1024-dim (1-2 AUXILIARY_MODULES_상세명세 L251) |

### HIGH (2)

| ID | Topic | Conflict |
|----|-------|----------|
| S2-H001 | RAG hybrid weight | 2-way (LOCK: 0.7/0.3) vs 3-way in FILE CONTEXT (0.40/0.35/0.25) — different architectures |
| S2-H002 | CLIP model variant | `clip-vit-large-patch14` (1-2) vs `clip-vit-large-patch14-336` (3-2 LOCK-MM-07) |

### MEDIUM (3)

| ID | Topic | Conflict |
|----|-------|----------|
| S2-M001 | C-3 sandbox constraints | Hardcoded CPU=1/RAM=512MB vs LOCK-VR-15: "config-managed" |
| S2-M002 | Code sandbox timeout | 10s (5-1 benchmark) vs 30s (1-1 C-3 verifier) |
| S2-M003 | QoD AR-L1 trigger | "Immediate" (alert section) vs "3 consecutive" (trigger table) — same file L308-315 |

### LOW (1)

| ID | Topic |
|----|-------|
| S2-L001 | Education difficulty zone 50-70% gap (no adjustment rule) |

---

## PART C: SOT vs SOT2 Cross-Conflicts (Scan 5)

### CRITICAL (1)

| ID | Topic | SOT Value | SOT2 Value |
|----|-------|-----------|------------|
| X-C001 | V0 active module set (K-1) | 7 modules (I-1,I-2,I-5,I-8,I-9,I-19,I-20) | 5 modules (I-1,I-2,I-3,I-5,I-19) |

### HIGH (2)

| ID | Topic | SOT Value | SOT2 Value |
|----|-------|-----------|------------|
| X-H001 | Failover chain order | GPT-4o -> Claude -> Ollama (3) | Claude -> GPT-4o -> DeepSeek -> Ollama (4) |
| X-H002 | Guardrails layer count V1 | 3-layer (no version split) | V1=2, V2=3, V3=4 (4-layer total) |

### MEDIUM (3)

| ID | Topic |
|----|-------|
| X-M001 | Agent Teams sub-agent naming divergence (resolved internally in SOT2) |
| X-M002 | 5-Gate naming: G0~G4 (Agent Teams) vs standard (Policy/Approval/Cost/Evidence/SelfCheck) |
| X-M003 | V2 LLM stack: GPT-4o mini+Sonnet (SOT) vs Claude+Ollama (SOT2) |

### LOW (1)

| ID | Topic |
|----|-------|
| X-L001 | V0 module count: SOT section 1.4=5 vs section 8.5.2(B)=7 (pre-existing SOT ambiguity) |

### Verified Alignments (12 areas)

Cost ceilings, Authority chain, P2 timeout, 9-State pipeline, P2 auto-OFF, MCP transport, LangChain ban, Blue Node caps, RBAC levels, Node-to-Node prohibition, Self-check thresholds, Single Decision principle.

---

## PART D: SOT2 vs Part2 Conflicts (Scan 6)

| ID | Severity | Topic |
|----|----------|-------|
| P2-OBS001 | NOTED | Failover chain order divergence (D2.0-02 vs D2.0-04) — Phase 8 target |
| P2-OBS002 | NOTED | RAGAS thresholds: LOCK-BE-11 conservative vs Part2 STEP7-G source |
| P2-OBS003 | NOTED | 5-1 task table S7G-035 "each>=0.75" vs LOCK-BE-11 differentiated |

Additional: Embedding dimension LOCK wording ambiguity in Part2 prose (L1757, L1813: "256 Matryoshka" vs LOCK table: "1024").

CONFLICT_LOGs: 2-2 COND = 0 open (3 resolved); 0-0 Governance = 0 open (all resolved).

---

## PART E: SOT2 Numerical Consistency (Scan 7)

### Active Issues (2)

| ID | Severity | Topic | Conflict |
|----|----------|-------|----------|
| N-C001 | CRITICAL | Cost warning threshold | Governance=80% (2-stage) vs Operations LOCK-OP-07=70% (4-stage) |
| N-M001 | MEDIUM | DEFINED-HERE count | Registry header=40 vs summary docs=37 (stale after DH-BA-1~3 addition) |

### Documented Intentional (1)

| ID | Topic |
|----|-------|
| N-D001 | Circuit Breaker failure threshold: MCP=5 vs A2A=3 (different tolerance by design) |

### Stale Snapshots (1)

| ID | Topic |
|----|-------|
| N-S001 | Domain count: 34->35->36 evolution; current canonical=36 |

### Confirmed Consistent

COND 106, IPC 72, MCP tools 31, Serde models 25, all timeout hierarchies, file size limits, performance SLAs.

---

## PART F: SOT2 Terminology Consistency (Scan 8)

### High Priority (2)

| ID | Issue | Affected |
|----|-------|----------|
| T-H001 | ORANGE CORE vs Orange Core capitalization | 15+ files |
| T-H002 | SOT2_MASTER_INDEX LOCK-BM (should be LOCK-BE for 5-1) | 1 file |

### Medium Priority (4)

| ID | Issue |
|----|-------|
| T-M001 | "자가진단" vs "자기진단" (recommend: 자가진단) |
| T-M002 | 벡터 DB / 벡터DB / Vector DB / VectorDB (4 variants) |
| T-M003 | 지식그래프 vs 지식 그래프 spacing |
| T-M004 | 멀티에이전트 vs 멀티 에이전트 (mixed within same file) |

### Low Priority (9)

| ID | Issue |
|----|-------|
| T-L001 | 워크플로 vs 워크플로우 (1 file exception) |
| T-L002 | DCL: Domain Context Layer vs Dynamic Context Layer |
| T-L003 | COND ID formats: COND-011 vs COND_011 vs cond_011 (intentional by context) |
| T-L004 | CAT dual directory structure (CAT-A vs 01_cat-a — transitional) |
| T-L005 | 9-State numbering residual (S1~S9 reference in QC doc, resolved in spec) |
| T-L006 | LOCK-PR-XXX non-existent namespace in prompt file |
| T-L007 | 에이전트 팀 vs 에이전트 Teams mixed |
| T-L008 | I-25 SDAR three fullnames coexisting (SC-08 resolved to "Self-Diagnosis and Auto-Repair") |
| T-L009 | ease_factor vs easiness_factor (v12 vs PKM naming) |

---

## Completion Criteria Assessment

| Criterion | Status |
|-----------|--------|
| Changed files = 0 (or all changes traceable) | BASELINE ESTABLISHED (initial; no prior baseline to compare) |
| Conflict list complete | YES — 6 scans completed, ~55 raw findings catalogued |
| Skill availability = 100% | YES — 55/55 skills available |

---

## Top Priority Actions (CRITICAL items requiring resolution)

| # | Source | Issue | Recommended Action |
|---|--------|-------|--------------------|
| 1 | SOT-C001 / X-C001 | I-Series range I-21/I-24/I-25 + V0 module set K-1 (5 vs 7) | Align K-1 with D2.0-01 section 8.5.2(B) or reconcile which modules are V0-mandatory |
| 2 | SOT-C002 | QoD 4-factor vs 5-factor formula (V1-006) | Resolve: adopt PLAN-3.0 5-factor as canonical, update MASTER_SPEC |
| 3 | S2-C001 | BGE-M3 dimension 768 vs 1024 in 1-2 spec body | Edit line 251: 768 -> 1024 |
| 4 | N-C001 | Cost warning threshold 70% vs 80% | Decide: Governance 80% 2-stage OR Operations 70% 4-stage |
| 5 | X-H001 | Failover chain: GPT-4o-first vs Claude-first | Escalate to Phase 8 deep review (already OBS-001) |
| 6 | X-H002 | Guardrails: 3-layer (SOT) vs 4-layer (SOT2) | Define 4th layer or align with SOT 3-layer |
| 7 | SOT-C003 | React 18.3 vs 19 | Confirm PHASE_B3 LOCK (18.3); update or annotate STEP7-F |
| 8 | SOT-C004 | Security items 14 vs 15 | Clarify DEC-003 addition; update READINESS docs |
