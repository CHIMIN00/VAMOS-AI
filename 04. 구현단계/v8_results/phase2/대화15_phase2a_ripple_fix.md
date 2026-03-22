# Phase 2-A Ripple Fix 보고서

> **대상 문서**: `VAMOS_구현가이드_PART2_구현단계.md` v18.0.0 → v19.0.0
> **수정 기준**: Phase 1.5 적대적 재검증 최종 결과 (86 REAL_ERROR, 25 SOURCE_CONFLICT)
> **수정일**: 2026-03-06
> **수정자**: Phase 2-A Modifier (v8.1 Pipeline)

---

## STEP 1: Ripple Map

> 수정 대상 값의 모든 변형(old/new)에 대해 PART2 전문을 grep 검색한 결과.

| 수정ID | 원본값 | 신규값 | 영향위치(행번호) | 총 위치수 |
|--------|--------|--------|-----------------|----------|
| FIX-01 (C-6) | 상태 머신 참조만 (`D2.0-02 §2.2`) | S0~S8 인라인 삽입 | 1308 (산출물 참조) | 1 |
| FIX-02 (C-2) | VamosState 7필드 | +pipeline_state 8필드 | 888~895 | 1 |
| FIX-03 (C-5) | §7.x 참조 | v14.0.0 수정 완전성 검증 | 389,390,432,433,437,519,520,524,593,597,610,772,819,934,1287,1288,1289 | 17 (전수 PASS) |
| FIX-04 (H-B1) | G1=Trust Score, G2=Relevance | SOURCE_CONFLICT HTML 주석 추가 | 2933, 2934 | 2 |
| FIX-05 (H-B3) | `vectorbt 또는 backtrader` | `vectorbt(조건부 ADOPT: 전략 ≥3개 시 도입) 또는 backtrader` | 2708 | 1 |
| FIX-06 (H-B5) | [rate_limit] 미기재 | V1+ 4섹션 인라인 참조 추가 | 1054~1055 | 1 |
| FIX-07 | `D2.0-08 §4` (Layout/Route) | `D2.0-08 §2.1/§3` | 1402~1404 | 2 |
| FIX-08 | `D2.0-08 §7` (Component) | `D2.0-08 §10.4` | 1410 | 1 |
| FIX-09 | `vamos run/approve/status/cost/memory` | `+/policy` (6개) | 1415 | 1 |
| FIX-10 | `D2.1-D2 FailureCode/FallbackRegistry` | `D2.0-08 §7에 14개+9개` | 2451 | 1 |
| FIX-11 | `5 concurrent requests` | `BLUE_NODES=3 / TOOLS=5 concurrent` | 3355 | 1 |
| FIX-12 | A-1 MultiBrain Adapter (Failover 누락) | +Failover GPT-4o→Claude→Ollama 3회 LOCK | 1405 | 1 |
| SC-01 | CL-G1 "Trust Score" | SRC: "Content Quality" | 2933 | 1 (미수정, SC 기록) |
| SC-02 | CL-G2 "Relevance" | SRC: "Consistency" | 2934 | 1 (미수정, SC 기록) |

**Ripple Map 요약**: 14개 패턴, 총 31개 위치 검색, 11건 수정 + 2건 SOURCE_CONFLICT 기록 + 1건 검증 PASS(수정 불필요)

> **NOTE**: FIX-05는 PART2 HTML 주석에서 `Phase 2-A FIX-05`로 태깅됨. 초기 보고서에서 FIX-13으로 오기재되었으나 PART2 실물 기준으로 FIX-05로 정정.

---

## STEP 2: 수정 내역

### CRITICAL (3건)

#### FIX-01 (C-6): ORANGE CORE S0~S8 상태 머신 인라인 추가
- **수정 위치**: V1-Phase 1 산출물 참조 직전 (line ~1305)
- **Before**: `- 상태 머신: \`D2.0-02\` §2.2` (참조만)
- **After**: 9-State 전체 인라인 (`S0_RECEIVED → S1_INTENT_PARSED → ... → S8_DONE`) + 타임아웃(S1=5s, S2=30s 등) + LOCK 주석
- **정본 근거**: D2.0-02 §2.2

#### FIX-02 (C-2): VamosState pipeline_state 필드 추가
- **수정 위치**: line 888~896 (LangGraph StateGraph 코드블록)
- **Before**: 7필드 (trace_id ~ response_envelope)
- **After**: 8필드 (+`pipeline_state: str  # S0_RECEIVED~S8_DONE`)
- **정본 근거**: D2.0-02 §2.2 상태 머신 + CLAUDE.md §12

#### FIX-03 (C-5): §7.x 참조 정확성 검증
- **결과**: v14.0.0 GROUP C 수정 완전성 **PASS** (17개소 전수 검증)
- **수정**: 없음 (이미 정확)

### HIGH (6건)

#### FIX-04 (H-B1): Cloud Library G0-G4 의미 불일치 SOURCE_CONFLICT 기록
- **수정 위치**: line 2933~2934 (G0-G4 5-Gate 테이블)
- **Before**: G1="Trust Score", G2="Relevance" (주석 없음)
- **After**: HTML 주석으로 SRC 불일치 기록 (CLOUD_LIBRARY_SPEC §8: G1="Content Quality", G2="Consistency")
- **미수정 사유**: SOURCE_CONFLICT — 정본 간 의미 범위 차이. PART2 값 유지, SRC 우선 시 변경 필요 안내

#### FIX-05 (H-B3): AI Investing vectorbt 조건부 ADOPT 주석
- **수정 위치**: line 2708 (백테스트 라이브러리)
- **Before**: `vectorbt 또는 backtrader`
- **After**: `vectorbt(조건부 ADOPT: 전략 ≥3개 시 도입) 또는 backtrader`
- **정본 근거**: D-S3-05 (VAMOS_AI_INVESTING_SPEC §14)

#### FIX-06 (H-B5): V1+ 추가 config 4섹션 인라인 참조
- **수정 위치**: line ~1054 (VamosConfig 클래스 직후)
- **Before**: `V0=13개 섹션` + 주석만 (rate_limit/blue_nodes/ui/guardrails 미기재)
- **After**: V1+=17개 명시 + 4섹션별 주요 키/값/B4 참조 인라인 블록

#### FIX-07: V1-Phase 4 Layout/Route 출처 정정
- **수정 위치**: line 1402~1404
- **Before**: `D2.0-08 §4` / `§2.2`
- **After**: `D2.0-08 §2.1/§3` / `§2.2`

#### FIX-08: V1-Phase 4 Component Registry 출처 정정
- **수정 위치**: line 1410 (React 컴포넌트 ~44개)
- **Before**: `D2.0-08 §7` (§7=Failure/Fallback 섹션)
- **After**: `D2.0-08 §10.4` (컴포넌트 레지스트리 정본)
- **정본 근거**: D2.0-08 §10.4

#### FIX-09: CLI vamos policy 추가
- **수정 위치**: line 1415
- **Before**: `vamos run/approve/status/cost/memory` (5개)
- **After**: `vamos run/approve/status/cost/memory/policy` (6개, D2.0-08 §2.3.1)

#### FIX-12: MultiBrain Adapter Failover 체인 추가
- **수정 위치**: line 1405 (V1-Phase 3 구현 테이블)
- **Before**: `Ollama + GPT-4o-mini 통합 인터페이스`
- **After**: +`Failover: GPT-4o→Claude→Ollama (3회 타임아웃 시 전환, LOCK)`
- **정본 근거**: CLAUDE.md §7.2

### MEDIUM (2건)

#### FIX-10: Failure/Fallback 참조 정정
- **수정 위치**: line 2451
- **Before**: `D2.1-D2 FailureCode/FallbackRegistry`
- **After**: `D2.0-08 §7에 14개 FailureCodes + 9개 FallbackRegistry`

#### FIX-11: 동시성 메트릭 분리
- **수정 위치**: line 3355
- **Before**: `5 concurrent requests`
- **After**: `BLUE_NODES=3 / TOOLS=5 concurrent`
- **정본 근거**: CLAUDE.md §7.2 (MAX_CONCURRENT_BLUE_NODES=3, TOOLS=5 별도)

---

## 미수정 항목 및 사유

### PART2 대상이 아닌 항목 (CLAUDE.md 대상, Phase 2-B 수정)

| ID | 설명 | 사유 |
|----|------|------|
| C-3 | SDAR 명칭 CLAUDE.md 미반영 | 대상: CLAUDE.md (PART2 아님) |
| C-4 | L0 TTL CLAUDE.md 미반영 | 대상: CLAUDE.md (PART2 아님) |
| H-B6 | approval_status CLAUDE.md 불일치 | 대상: CLAUDE.md (PART2 아님) |

### PART2 대상이 아닌 항목 (PHASE_B 대상)

| # | 설명 | 대상 | 사유 |
|---|------|------|------|
| P2 #28 | B6 Rust nightly → stable | PHASE_B6 | PART2 아님 |
| P2 #29 | B1 IPC 47 → 72 정정 | PHASE_B1 | PART2 아님 |

### 이미 해소된 항목 — Priority 1 (v10~v18에서 수정 완료)

| ID | 설명 | 해소 버전 | PART2 확인 |
|----|------|----------|-----------|
| C-1 (P1 #1) | 9-State UI 상태명 | v15.0.0 | §6.1.6 UI_S0_BOOT~UI_S8_ARCHIVED 확인 |
| H-B2 (P1 #8) | Cloud Library LOCK L1~L13 | v10.0.0 M-29 | §6.10 LOCK 테이블 13항목 확인 |
| H-B4 (P1 #10 부분) | [rbac] 섹션 | v16.0.0 | VamosConfig rbac: RBACConfig 확인 |
| H-B7 (P1 #12) | §12→§2.2 참조 | v14.0.0 GROUP A | 4개소 전수 정정 확인 |

### 이미 해소된 항목 — Priority 2/3 (v10~v18에서 수정 완료)

| # | 설명 | 해소 버전 | PART2 확인 위치 |
|---|------|----------|----------------|
| P2 #16 | config 키 정합 (섹션명 core/guardrails) | v16.0.0 BLOCKER-1 | L1039 `core: CoreConfig`, L1047 `approval: ApprovalConfig` (general→core, safety→approval+rbac 완료) |
| P2 #17 | RAG Pipeline 구분 | v15.0.0 HIGH-1 | L1361 `6-Stage RAG Pipeline (D2.0-06 §1.1 LOCK)` + 스테이지명 교체 완료 |
| P2 #18 | EventTypeRegistry / ResponseEnvelope 정합 | v15.0.0 HIGH-3 | L462 `EventTypeRegistry 123`, ResponseEnvelope LOCK 유지 |
| P2 #19 | Hooks/Stores PHASE_B2 정정 | 15-0 해소 | §6.1.3 8/8 일치, §6.1.5 7/7 일치 |
| P2 #20 | 5→7 페이지 | 15-0 해소 | §6.1.4 7 pages 일치 |
| P2 #24 | E-5 V1/V2 표기 통일 | v14.0.0 이전 | L1412 `V1=단건 분석, V2=배치 처리 — D2.0-03 §4 V2 구분` |
| P3 #33 | AC 매핑 50→79 | v17.0.0 이전 | L2547 `AC 매핑 (50 AC → 79 테스트, PHASE_B5 §7.3 정본)` |
| P3 #34 | B7 10-Step + 사후검증 7항목 | v17.0.0 | L1527 10-Step 테이블 + L1542 사후검증 7항목 체크리스트 |
| P3 #35 | SDAR State Machine/5 Gates | v17.0.0 | L2829 SDAR 7상태 + L2847 5-Gate 통합 + BaseGate 코드 공유 |
| P3 #36 | VAL-001~VAL-010 B4 기준 | v16.0.0 이전 | L2532 `VAL-001~VAL-010 검증 규칙 (PHASE_B4 §6.2 정본)` |

### SOURCE_CONFLICT (수정 제외, HTML 주석 기록)

| ID | PART2 값 | SRC 값 | 사유 |
|----|----------|--------|------|
| SC-01 | CL-G1 "Trust Score" | CLOUD_LIBRARY_SPEC §8 "Content Quality" | 정본 간 의미 범위 차이. 동일 게이트, 다른 명명. HTML 주석 기록 |
| SC-02 | CL-G2 "Relevance" | CLOUD_LIBRARY_SPEC §8 "Consistency" | 정본 간 의미 범위 차이. 동일 게이트, 다른 명명. HTML 주석 기록 |

---

## 수정 통계

| 구분 | 건수 |
|------|------|
| CRITICAL 수정 | 2건 (FIX-01, FIX-02) + 1건 검증 PASS (FIX-03) |
| HIGH 수정 | 6건 (FIX-05, FIX-06, FIX-07, FIX-08, FIX-09, FIX-12) + 1건 SC 기록 (FIX-04) |
| MEDIUM 수정 | 2건 (FIX-10, FIX-11) |
| SOURCE_CONFLICT 기록 | 2건 (SC-01, SC-02) |
| 이미 해소 (v10~v18) | 14건 (P1: 4건, P2: 6건, P3: 4건) |
| CLAUDE.md 대상 (PART2 외) | 3건 |
| PHASE_B 대상 (PART2 외) | 2건 |
| **총 PART2 수정** | **11건** (FIX-01~FIX-12, FIX-03 제외) |

### 시정 조치 전수 매핑 (30건)

| Priority | 전체 | 수정 | 검증PASS | SC기록 | 이미해소 | CLAUDE.md | PHASE_B |
|----------|------|------|---------|--------|---------|----------|---------|
| P1 (12건) | 12 | 4 | 1 | 1 | 3 | 3 | 0 |
| P2 (15건) | 15 | 3 | 0 | 0 | 4 | 6 | 2 |
| P3 (3건*) | 3* | 0 | 0 | 0 | 4* | 0 | 0 |
| 추가 (Ripple) | 2 | 2 | 0 | 0 | 0 | 0 | 0 |
| **합계** | **32** | **9** | **1** | **1** | **11** | **9** | **2** |

> *P3는 15-0에서 3건으로 집계되었으나, PART2 실물 확인 결과 #33/#34/#35/#36 = 4건 모두 이미 해소. 대화14 P3 "3건" 산술에 1건 오차 존재 (8-5=3이나 실제 해소는 #30/#31/#32/#37=4건, 잔존=#33/#34/#35/#36=4건).
> **추가 2건**: FIX-09(CLI policy)와 FIX-10(Failure 참조 정정)은 30건 시정 조치 목록 외에 Ripple Map 과정에서 추가 발견된 PART2 오류로, 별도 수정함.

## P9 무결성 검증

- [x] Changelog 행 구조 유지 (파이프 구분자 정상)
- [x] v19.0.0 changelog 신규 행 추가 완료
- [x] 헤더 버전 v18.0.0 → v19.0.0 갱신
- [x] 최종갱신일 2026-03-03 → 2026-03-06 갱신
- [x] LOCK/FREEZE 값 변경 없음 확인
- [x] 기존 SOURCE_CONFLICT HTML 주석 훼손 없음

## 정정 이력

| # | 정정 내용 | 사유 |
|---|----------|------|
| 1 | FIX-13 → **FIX-05** (vectorbt) | PART2 HTML 주석 `Phase 2-A FIX-05`와 일치시킴. 초기 보고서에서 FIX-13으로 오기재 |
| 2 | FIX-08 STEP 2 상세 추가 | Ripple Map에만 존재하고 수정 내역에 누락되었던 Component 출처 정정 상세 추가 |
| 3 | HIGH 수정 4건 → **6건** + 1건 SC | FIX-08 누락 반영 + FIX-05 MEDIUM→HIGH 정정 (대화14 P1 #9 severity=HIGH) |
| 4 | 이미 해소 항목 4건 → **14건** | P2 #16~#20/#24 + P3 #33~#36 PART2 실물 확인 후 이미 해소 판정 추가 |
| 5 | PHASE_B 대상 2건 명시 | P2 #28(PHASE_B6), #29(PHASE_B1) 미수정 사유 추가 |
| 6 | P3 잔존 건수 오차 발견 | 대화14 "P3 3건" vs 실제 4건 (#33/#34/#35/#36) — 1건 산술 오차 기록 |

---

> **다음 단계**: Phase 2-B에서 (1) CLAUDE.md 대상 3건 (C-3, C-4, H-B6) 수정 + (2) PHASE_B 대상 2건 (#28, #29) 수정 + (3) Phase 0 전수 재실행 필요.
