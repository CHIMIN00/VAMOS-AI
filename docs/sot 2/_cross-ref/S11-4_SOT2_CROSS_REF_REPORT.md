# S11-4 SOT2 CROSS-REF REPORT (P2)

> Phase 11, Session S11-4 | Procedure 2: /sot2-cross-ref all
> Generated: 2026-03-28 (RE-EXECUTION)
> Scope: 36 domains, Layer 1~4 full cross-reference
> Validator: Claude Opus 4.6

---

## Executive Summary

| Layer | Check | Result |
|-------|-------|--------|
| Layer 1 | SS5 Dependency Bidirectional | 27 bidirectional PASS / 6 gaps (2 MEDIUM, 4 LOW) |
| Layer 2 | LOCK Source Traceability | 469/469 traceable (5 weak source labels) |
| Layer 3 | Terminology Consistency | 1 HIGH (ORANGE CORE casing) / 1 MEDIUM (alpha notation) |
| Layer 4 | Numerical Consistency | 12/12 key values CONSISTENT (2 LOW exceptions) |

---

## Layer 1: SS5 Dependency Bidirectional Match

### Dependency Graph Statistics

| Metric | Count |
|--------|-------|
| Total edge-directions | 139 |
| Unidirectional edges | 85 |
| Bidirectional pairs | 27 |
| Circular dependencies (cross-tier) | 0 |
| Same-tier cycles (permitted) | 4 |
| Cross-tier bidirectional pairs | 6 (all justified) |

### 27 Bidirectional Pairs Verified

| # | Domain A | Domain B | Status |
|---|----------|----------|--------|
| B1 | 2-1 Blue-Node | 2-2 COND | PASS |
| B2 | 3-2 Multimodal | 3-3 PKM | PASS |
| B3 | 3-2 Multimodal | 3-6 Health | PASS |
| B4 | 3-3 PKM | 3-5 Education | PASS |
| B5 | 3-4 Workflow | 3-6 Health | PASS |
| B6 | 3-4 Workflow | 3-7 Dev-Tools | PASS |
| B7 | 3-5 Education | 3-6 Health | PASS |
| B8 | 3-7 Dev-Tools | 3-10 Agent-Protocol | PASS |
| B9 | 3-8 A2A | 3-10 Agent-Protocol | PASS |
| B10 | 3-8 A2A | 4-3 MCP | PASS |
| B11 | 4-1 Rust-Tauri | 4-2 CI/CD | PASS |
| B12 | 4-2 CI/CD | 4-4 MLOps | PASS |
| B13 | 6-1 UI | 6-11 Hologram | PASS |
| B14 | 6-2 Security | 6-5 SDAR | PASS |
| B15 | 6-2 Security | 6-12 Event-Logging | PASS |
| B16 | 6-3 Agent-Teams | 6-2 Security | PASS |
| B17 | 6-3 Agent-Teams | 6-5 SDAR | PASS |
| B18 | 6-4 Memory-RAG | 6-5 SDAR | PASS |
| B19 | 6-5 SDAR | 6-6 Self-Evolution | PASS |
| B20 | 6-7 RT-BNP | 6-8 Cloud-Library | PASS |
| B21 | 6-12 Event-Logging | 6-13 Operations | PASS |
| B22 | 6-3 Agent-Teams | 3-8 A2A | PASS |
| B23 | 6-3 Agent-Teams | 3-10 Agent-Protocol | PASS |
| B24 | 6-4 Memory-RAG | 1-2 Auxiliary | PASS |
| B25 | 6-4 Memory-RAG | 3-3 PKM | PASS |
| B26 | 6-5 SDAR | 1-2 Auxiliary | PASS |
| B27 | 6-9 Brain-Adapter | 6-11 Hologram | PASS |

### Gaps Found (6 items)

| # | Issue | Severity | Detail |
|---|-------|----------|--------|
| G1 | 6-10 EXP dependencies missing from central graph | MEDIUM | AUTHORITY_CHAIN references 1-1, 1-2, 6-6 but DEPENDENCY_GRAPH.md adjacency matrix shows empty row for 6-10 |
| G2 | 3-4 Workflow -> 3-5 Education provision not in matrix | MEDIUM | 3-4 declares "provide to #8 Education" locally, 3-5 lists 3-4 as dependency, but adjacency matrix row 3-4 lacks arrow to 3-5 |
| G3 | 3-1 AI-Investing missing 6-7 RT-BNP dependency | LOW | 6-7 provides breaking news to AI-Investing, but 3-1's own SS5 does not list 6-7 |
| G4 | 3-9 Business-Model has no outbound arrows | LOW | Strategy domain is consumer by nature; no outbound provision expected |
| G5 | 3-1 AI-Investing has no outbound arrows | LOW | Application domain consuming multiple infra services; consumer nature |
| G6 | 5-2 File-Context cross-tier refs | LOW | Added in S9-2 update, correctly reflected in both local and central graph |

---

## Layer 2: LOCK Source Traceability

### Summary

| Metric | Result |
|--------|--------|
| Total LOCKs | 469 (MASTER_INDEX 472건 대비 -3, DEFINED-HERE 카운팅 방식 차이) |
| Traceable sources | **469/469 (100%)** |
| "unknown" or "TBD" sources | **0** |
| Weak source labels | 5 (in 0-0 Governance) |
| SOT2 DEFINED-HERE items | 47 (all with derivation paths) |
| "existing spec" informal refs | ~32 (in T3 domains, all real and traceable) |

### Weak Source Details (5 items in 0-0 Governance)

| LOCK | Current Source | Recommended Fix |
|------|---------------|-----------------|
| L3 (V1 cost) | "ABSOLUTE LOCK" | Add "RULE 1.3 SS5 / D2.0-07 SS4" |
| L4 (V2 cost) | "ABSOLUTE LOCK" | Add "RULE 1.3 SS5 / D2.0-07 SS4" |
| L5 (V3 cost) | "ABSOLUTE LOCK" | Add "RULE 1.3 SS5 / D2.0-07 SS4" |
| L6 (5-Gate) | "pipeline.py" | Add "D2.0-02 SS3.3" |
| L7 (9-State) | "pipeline.py" | Add "D2.0-02 SS2.2" |

### SOT2 Newly Defined LOCKs (no upstream design doc)

| Domain | LOCKs | Justification |
|--------|-------|---------------|
| 6-12 Event-Logging | EL-01, EL-07, EL-08 | New horizontal service; no pre-existing design doc for event schema |

---

## Layer 3: Terminology Consistency

### Check Results

| # | Term | Expected | Status | Issues |
|---|------|----------|--------|--------|
| 1 | ORANGE CORE | ALL CAPS | **HIGH** | 22+ occurrences of "Orange Core" in 8+ files |
| 2 | Blue Node | Title Case (prose) | PASS | Consistent; BLUE NODE only in formal refs |
| 3 | 5-Gate / 07 Gate | Two distinct concepts | PASS | Correctly distinguished |
| 4 | S0-S8 | Consistent | PASS | No conflicts |
| 5 | LOCK | ALL CAPS | PASS | lowercase only in code field names |
| 6 | Part2 / PART2 | Contextual | PASS | Different referents (doc vs section) |
| 7 | V0/V1/V2/V3 | Consistent | PASS | Uniform across all domains |
| 8 | COND | ALL CAPS | PASS | No variants |
| 9 | EXP | ALL CAPS | PASS | No variants |
| 10 | MCP | ALL CAPS | PASS | 127 occurrences, all caps |
| 11 | A2A | ALL CAPS | PASS | 43 occurrences, all caps |
| 12 | Cost values | Multi-format | PASS | W, W-abbreviated, USD -- all intentional |

### HIGH: "Orange Core" Violations (22+ occurrences)

Files affected:
- `5-2_File-Context/FILE_CONTEXT_구조화_종합계획서.md`
- `6-3_Agent-Teams-PARL/AGENT_TEAMS_PARL_구조화_종합계획서.md` (7 occurrences)
- `6-3_Agent-Teams-PARL/AUTHORITY_CHAIN.md`
- `6-9_Brain-Adapter-HAL/BRAIN_ADAPTER_HAL_구조화_종합계획서.md`
- `6-10_EXP-Modules-Detail/EXP_MODULES_DETAIL_카탈로그.md`
- `6-10_EXP-Modules-Detail/AUTHORITY_CHAIN.md`
- `6-11_Hologram-Main-LLM/HOLOGRAM_MAIN_LLM_구조화_종합계획서.md` (3 occurrences)
- `SOT2_MASTER_INDEX.md`
- `S8-6_QC_RESULT.md`

> Previously flagged as T-H001 in S11-1 but remains unfixed.

### MEDIUM: Hybrid Search Alpha Notation

| Domain | Alpha means | Value |
|--------|------------|-------|
| 1-2 Auxiliary, 5-2 File-Context | BM25 weight | alpha=0.3 |
| 6-4 Memory-RAG, MASTER_INDEX | Dense weight | alpha=0.7 |

> Canonical definition: `alpha = BM25_weight = 0.3`. Same 70/30 split, different label assignment.

---

## Layer 4: Numerical Consistency

### 12 Key Values Cross-Checked

| # | Value | Expected | Domains Checked | Result |
|---|-------|----------|----------------|--------|
| 1 | Cost cap V1 | W40,000 | 15+ domains | **CONSISTENT** |
| 2 | Cost cap V2 | W93,000 | 15+ domains | **CONSISTENT** |
| 3 | Cost cap V3 | W266,000 | 15+ domains | **CONSISTENT** |
| 4 | Self-check threshold | P0>=70, P1>=75, P2>=80 | 13+ refs | **UNANIMOUS** |
| 5 | Active node cap | V1=3, V2=10, V3=50 | 2-1, 6-3 | **CONSISTENT** |
| 6 | P2 approval timeout | 10min / HITL 5min | 8+ domains | **CONSISTENT** |
| 7 | Turn limits | P0=5, P1=10, P2=20 | 6-3, 3-8 | **CONSISTENT** |
| 8 | Hybrid search | BM25=0.3, Dense=0.7 | 1-2, 5-2, 6-4 | **CONSISTENT** |
| 9 | Semantic cache | cosine>=0.95 | 25+ refs | **UNANIMOUS** |
| 10 | BGE-M3 | 1024-dim | All embedding refs | **CONSISTENT** |
| 11 | HMAC key | 32 bytes | 6-2, 6-3, Part2 | **CONSISTENT** |
| 12 | RAGAS Faithfulness | >=0.90 | 5-1, S11-5 | **CONSISTENT** |

### Known Exceptions (by design, not conflicts)

| # | Value | Domain | Difference | Reason |
|---|-------|--------|-----------|--------|
| E1 | Multimodal cost sub-budget | 3-2 | V1=W10K (vs global W40K) | Domain-specific sub-allocation |
| E2 | Benchmark sandbox timeout | 5-1 | 10s (vs LOCK 30s) | Benchmark-specific setting |
| E3 | MCP Circuit Breaker | 4-3 | 5 failures (vs A2A 3) | Different protocol tolerance by design |

---

## P2 Overall Assessment

| Layer | Verdict |
|-------|---------|
| Layer 1: Dependency Bidirectional | **PASS** (2 MEDIUM gaps to fix in DEPENDENCY_GRAPH.md) |
| Layer 2: LOCK Source Traceability | **PASS** (469/469 traceable, 0 unknown) |
| Layer 3: Terminology | **CONDITIONAL** (ORANGE CORE casing fix needed) |
| Layer 4: Numerical | **PASS** (all 12 key values consistent) |

**P2 VERDICT: CONDITIONAL PASS -- "ORANGE CORE" casing fix required for FULL PASS**

> **Note**: 6-11 Hologram 도메인에서도 "Orange Core" 3건 확인. 6-3 Agent-Teams와 동일 기준 적용하여 Quality Gate에서 SILVER로 재조정됨.
