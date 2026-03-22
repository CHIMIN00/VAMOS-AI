# VAMOS v8.1 Phase 0 Baseline Report

> **Generated**: 2026-03-04 (재생성)
> **PART2 Version**: v11.0.0 (1821 lines)
> **SRC**: PHASE_B_EXHAUSTIVE_ANALYSIS.md (B1~B7 통합 분석)
> **Scripts**: 14개 (Part I: 0-A~0-H, Part II: IMP-A~IMP-F)
> **v8 Prompt**: v8.1.0

---

## Summary

| Script | Name | Verdict | Errors | Notes |
|--------|------|---------|--------|-------|
| **0-A** | Table Structure | **FAIL** | 1 | Line 735: V3 RT-BNP 행에 5열 (헤더는 4열) |
| **0-B** | Arithmetic Sum | PASS | 0 | V0=5/V1=32/V2=42/V3=81 행합 정확 |
| **0-C** | Heading Hierarchy | PASS | 0 | 제목 레벨 점프 없음, TOC 앵커 정상 |
| **0-D** | LOCK/FREEZE/ABSOLUTE + V7-2 Cross-Check | PASS | 0 | 80건 추출 + SRC 교차 비교 완료 |
| **0-E** | Keyword Inconsistency | **FAIL** | 3 | 변경 이력 섹션 내 컨텍스트별 숫자 차이 (false positive) |
| **0-F** | ID Uniqueness | PASS | 0 | 고유 ID 식별 완료 |
| **0-G** | HTML Comment Integrity + Body Verification | PASS | 0 | 12건 SOURCE_CONFLICT 주석 감지, 본문 값 검증 완료 |
| **0-H** | Header Count vs Rows | **FAIL** | 1 | Section 6.2.1 "72개" vs 요약 테이블 5행 (요약 테이블이므로 허용) |
| **IMP-A** | Module Dependency Graph | **FAIL** | 1 | **BLOCKER**: I-10 ↔ I-11 순환 의존성 |
| **IMP-B** | Schema Field Count + SRC Cross-Check | **FAIL** | 1 | **HIGH**: DecisionSchema=17(PART2) ≠ 18(SOT D2.1-D2) |
| **IMP-C** | API Endpoint | **FAIL** | 3 | PART2 약칭 13 IPC vs SRC 72 IPC (구조적 차이) |
| **IMP-D** | Config Key + V7-1 Canonical Section Check | **FAIL** | 6 | 4건 값 불일치 + 섹션 이름 불일치 (B4 canonical vs PART2) |
| **IMP-E** | Module Activation Matrix | PASS | 0 | V0=5/V1=32/V2=42/V3=81 전수 검증 통과, 누적 증가 확인 |
| **IMP-F** | Tech Stack Conflict | PASS | 0 | V2+ 전용 기술의 V1 사용 없음 |

---

## PASS: 6 / 14
## FAIL: 8 / 14

---

## REAL Errors (Action Required for Phase 2)

### 1. [IMP-A] BLOCKER: I-10 ↔ I-11 Circular Dependency

**Severity**: **BLOCKER**
**Location**: V1-Phase 1, Week 3-4 모듈 구현 순서
**Issue**:
- I-11 (Output Composer) depends on I-5, **I-10**
- I-10 (Tool Registry/Router) depends on **I-11**
- Circular: `I-11 → I-10 → I-11`
**Fix**: I-10에서 I-11 의존성 제거. Tool Registry는 하위 레벨 컴포넌트.

### 2. [IMP-B] HIGH: DecisionSchema Field Count Mismatch

**Severity**: **HIGH**
**Location**: PART2 line 207
**Issue**:
- PART2: `DecisionSchema = 17 (FREEZE)` (14 required + 3 optional)
- SOT (D2.1-D2 §4.1): `DecisionSchema = 18` (14 required + 4 optional)
- 누락 필드: `s_module_hints` (optional)
**Fix**: PART2 line 207을 `18 (FREEZE)`로 수정, PART1 E.4-4에서 이미 18 확인

### 3. [IMP-D] HIGH: Config Section Name Mismatch

**Severity**: **HIGH**
**Location**: PART2 V0 config.v1.toml (lines 115-188)
**Issue**:
- B4 canonical에는 있으나 PART2에 없는 섹션: `core, guardrails, rate_limit, rbac`
- PART2에는 있으나 B4 canonical에 없는 섹션: `general, memory, safety, self_check`
- 매핑 추정: `general↔core`, `safety↔guardrails`
**Fix**: PART2 섹션명을 B4 canonical에 맞추어 통일 필요

### 4. [IMP-D] MEDIUM: Config Value Mismatches

**Severity**: MEDIUM (버전별 차이 가능)

| Section | Key | PART2 (V0) | SRC (B4) | Analysis |
|---------|-----|------------|----------|----------|
| embedding | matryoshka_dim | 256 | 512 | V0 vs B4 기본값 차이 |
| llm | max_tokens | 2048 | 4096 | PART2 v8.2.0에서 수정됨 |
| llm | main_model | ollama:llama3.1:8b | gpt-4o-mini | V0=ollama, V1+=gpt-4o-mini (정상) |
| semantic_cache | max_entries | 1000 | 10000 | 불일치 확인 필요 |

### 5. [0-A] LOW: Table Column Mismatch

**Severity**: LOW
**Location**: Line 735, V3-Phase 2 EXP 모듈 테이블
**Issue**: Row #14 (RT-BNP) has 5 columns but table header has 4
**Fix**: 참조를 구현 내용 셀로 이동 또는 열 추가

---

## Expected Differences (No Action Required)

### [0-E] Keyword Number Inconsistency (3 findings)

변경 이력 섹션(lines 1644-1818) 내 컨텍스트별 차이:
- "I-Series 25" (모듈 수) vs "I-Series 20" (구 changelog 참조)
- "V2=10" (Agent 병렬 한도) vs "V2: 9" (구 GO/NO-GO 수)
- 컨텍스트가 다른 false positive

### [0-H] Header Count (1 finding)

Section 6.2.1 "72개"는 전체 IPC 명령 수이며, 바로 아래 테이블은 카테고리별 5행 요약.

### [IMP-C] API Endpoint (3 findings)

PART2 §6.2는 약칭/요약 형식(13 IPC 예시), SRC는 전체 72개 개별 IPC.
구조적 차이이며 데이터 오류 아님.

---

## Extracted Data Summary

### LOCK/FREEZE/ABSOLUTE (80 entries + V7-2 Cross-Check)
- LOCK: 75 entries
- FREEZE: 2 entries (DecisionSchema=17 ← SOT는 18, V0 I-4 exclusion)
- ABSOLUTE: 2 entries (cost limits)
- Lock: 1 entry (case variant)
- V7-2 SRC 교차 비교: PART2 LOCK 값 vs SRC config 값 비교 완료

### Module Dependency Graph
- 17 nodes (I-Series modules)
- 17 edges
- 1 cycle (BLOCKER): I-10 ↔ I-11

### Schema Count
- 24 Pydantic v2 models extracted (24개 정확 — 25는 I-Series 모듈 수와 혼동)
- DecisionSchema = PART2에서 17(FREEZE)이나 SOT(D2.1-D2)는 **18** (14 required + 4 optional)

### Module Activation Matrix
- V0: 5+0+0+0+0+0+0+0 = **5** (CORRECT)
- V1: 17+6+1+2+1+3+2+0 = **32** (CORRECT)
- V2: 22+10+1+3+1+3+2+0 = **42** (CORRECT)
- V3: 25+16+8+7+6+7+6+6 = **81** (CORRECT)
- Cumulative increase: All series non-decreasing across versions (VERIFIED)

### Config Sections
- **PART2**: 13 sections — cost, embedding, general, graph_db, llm, logging, mcp, memory, safety, self_check, semantic_cache, storage, vector_db
- **B4 Canonical**: 13 sections — core, cost, embedding, graph_db, guardrails, llm, logging, mcp, rate_limit, rbac, semantic_cache, storage, vector_db
- **Mismatch**: PART2 `general/memory/safety/self_check` ↔ B4 `core/guardrails/rate_limit/rbac`

### SOURCE_CONFLICT Comments
- 12 HTML comments documenting known discrepancies between source documents
- All properly formed (opening/closing matched)
- Body text verification: 채택 값 본문 일치 확인 완료

---

## Phase 0 Conclusion

**Phase 1 진행 가능 여부**: **조건부 가능**

### Phase 2에서 수정해야 할 PART2 이슈:
1. **[BLOCKER]** I-10/I-11 순환 의존성 해소
2. **[HIGH]** DecisionSchema 17 → 18 수정 (s_module_hints 추가 반영)
3. **[HIGH]** Config 섹션명 B4 canonical 기준으로 통일
4. **[MEDIUM]** Config 값 4건 (matryoshka_dim, max_entries 등) 정합
5. **[LOW]** Line 735 테이블 열 수 정정

### Phase 1 진행 조건:
- 위 이슈들은 Phase 0이 **정확히 감지**한 PART2 문서 오류
- Phase 1 Agent들이 동일 항목을 SRC 교차 검증하므로 재발견됨
- Phase 2 (대화 15~17)에서 PART2 수정 후 Phase 0 재실행으로 최종 확인

---

## File Index

| File | Description |
|------|-------------|
| phase0_part1.py | Part I scripts (0-A ~ 0-H) + V7-2 SRC 교차 비교 |
| phase0_part2.py | Part II scripts (IMP-A ~ IMP-F) + SRC cross-check |
| 0-A.json | Table Structure results |
| 0-B.json | Arithmetic Sum results |
| 0-C.json | Heading Hierarchy results |
| 0-D.json | LOCK/FREEZE/ABSOLUTE extraction + V7-2 cross-check |
| 0-E.json | Keyword Inconsistency results |
| 0-F.json | ID Uniqueness results |
| 0-G.json | HTML Comment Integrity + Body Verification results |
| 0-H.json | Header Count vs Rows results |
| IMP-A.json | Module Dependency Graph results |
| IMP-B.json | Schema Field Count + SRC Cross-Check results |
| IMP-C.json | API Endpoint results |
| IMP-D.json | Config Key + V7-1 Canonical Section Check results |
| IMP-E.json | Module Activation Matrix results |
| IMP-F.json | Tech Stack Conflict results |
| phase0_baseline.md | This summary report |
