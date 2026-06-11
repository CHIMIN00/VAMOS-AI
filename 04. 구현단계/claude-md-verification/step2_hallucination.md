# CLAUDE.md 검증 Step 2 — /claude-md-hallucination 결과

> **실행일**: 2026-06-11 | **대상**: `D:\VAMOS\CLAUDE.md` (944줄, §1~§28, 갱신 2026-06-11)
> **방법**: SKILL.md(RULE-C6 테이블 행=claim, RULE-C7 UNVERIFIED 사유 필수) — 신규/변경부 전수 + §5~§20 LOCK/비용/임계값 표본 33건
> **판정**: VERIFIED / PARTIAL / UNVERIFIED

---

## 1. 총괄

| 항목 | 값 |
|------|-----|
| **총 claim 수** | **185** |
| **VERIFIED** | **175 (94.6%)** |
| **PARTIAL** | **9 (4.9%)** |
| **UNVERIFIED** | **1 (0.5%)** |
| 목표 95%+ 대비 | 94.6% — 0.4%p 미달 (PARTIAL 9건 중 6건은 수치 자체는 정합, 표기/시차성 문제) |

### 섹션별 분포

| 섹션 | claim | V | P | U |
|------|-------|---|---|---|
| §2 산출물 경로 | 13 | 10 | 3 | 0 |
| §4 핵심 파일 8행 | 8 | 8 | 0 | 0 |
| §6 모듈(187·EVX 6행·COND 7행) | 19 | 17 | 2 | 0 |
| §7.4 신규 2행 (Hybrid/MCP) | 2 | 2 | 0 | 0 |
| §21 도메인 라우팅 36행+부속 | 40 | 39 | 1 | 0 |
| §22 COND 보충 | 9 | 8 | 1 | 0 |
| §23 용어 15행+부속 | 18 | 18 | 0 | 0 |
| §24 STEP7 17행+부속 | 19 | 18 | 1 | 0 |
| §25 의존성 수치 | 4 | 4 | 0 | 0 |
| §26 Obsidian | 5 | 4 | 0 | 1 |
| §27 .claude | 4 | 4 | 0 | 0 |
| §28 엔지니어링 | 11 | 10 | 1 | 0 |
| §5~§20 표본(LOCK/비용/임계값) | 33 | 33 | 0 | 0 |
| **합계** | **185** | **175** | **9** | **1** |

---

## 2. UNVERIFIED 전 목록 (1건)

### U-1. §26 매트릭스 노트 `12_IMPLEMENTATION\Engineering-Matrix.md`
- **주장**: 매트릭스 노트: `12_IMPLEMENTATION\Engineering-Matrix.md`
- **SOT에서 찾을 수 없는 이유**: `D:\VAMOS\VAMOS HOME\12_IMPLEMENTATION\` 폴더는 실존하나 **내용이 비어 있음**(파일 0개). Vault 전체(`D:\VAMOS\VAMOS HOME\`) 재귀 탐색에서도 `*Engineering*`/`*Matrix*` 명칭 파일 미발견. 해당 노트는 미생성 상태로 추정 — CLAUDE.md가 존재하지 않는 파일을 실존하는 것처럼 기술 (Engineering Matrix의 실제 정본은 `D:\VAMOS\VAMOS Engineering\STRATEGY_08_ENGINEERING_MATRIX.md`로 §28.1에 별도 기재됨).

---

## 3. PARTIAL 전 목록 (9건)

### P-1. §2 구현단계 파일 수 "782개 (실측 2026-06-11)"
- **재실측**: 783개 (`find "D:\VAMOS\04. 구현단계" -type f`)
- **차이 사유**: +1건은 금일 22:59 생성된 검증 산출물 `claude-md-verification\step5_symbolic.md` — CLAUDE.md 실측 시점(검증 파이프라인 가동 전)에는 782 정합. 시차성 차이.

### P-2. §2 그룹 A "설계 21개 (~35,472줄)"
- **재현 시도**: BASE-1.3(1)+PLAN-3.0(1)+D2.0-01~08(8)+D2.1-A1/D1~D8/Q1(10) = **20파일 32,969줄**
- **차이**: 주장 대비 1파일/~2,503줄 차이. CLAUDE.md에 그룹 구성 파일 목록이 명시되지 않아 21번째 파일 귀속 불명 — 합산 재현 불가. (나머지 그룹 B/C/D/E 파일 수는 모두 재현됨: 7/5/5/1)

### P-3. §2 그룹 B "구현가이드 7개 (~9,618줄)"
- **실측**: PHASE_B1~B7 7파일 합계 **9,754줄** (wc -l). 7개 파일 수는 정확, 줄 수 -136줄(1.4%) 과소 표기. (그룹 C 8,609/주장 8,543, D 9,033/9,019, E 1,844/1,853은 ±1% 이내로 VERIFIED 처리)

### P-4. §6 EVX-3 행 LOCK 셀 "-"
- **정본**: D2.0-01 §5.13 L745 — EVX-3 `change_lock = false` (명시값 존재)
- **차이**: CLAUDE.md는 "-"(미정 표기), 정본은 `false`. 나머지 셀(명칭 Log-prob Confidence·status EXP[D2.0-01 L1776]·OFF/OFF/ON)은 일치. EVX-1/2/4/5/6 5행은 전 셀 일치(EVX-2 LOCK true 포함, L743-748).

### P-5. §6 COND 하단 "**STEP7**: 16개 카테고리(A~P) 3,041건 AI기술보강"
- **정본**: `STEP7_STEP6통합_마스터인덱스.md` L4/L12 — **3,041 = STEP6 1,556 + STEP7 1,485**. A~P 16개 카테고리+보강의 합(STEP7측)은 **1,485건**.
- **차이**: "16개 카테고리(A~P) 3,041건"은 STEP6 포함 총계를 카테고리 합계처럼 기술한 합산 혼동. §24에서는 정확히 분리 기재되어 있음(자체 모순은 §24가 해소).

### P-6. §21 AINV 행 Tier "-" 표기
- **정본**: DEPENDENCY_GRAPH.md §1.1 L25 — "Tier 3 ─ Feature Domains (3-2 ~ 3-10, **AI-Investing**)" → AINV는 Tier 3 소속.
- **차이**: CLAUDE.md는 Tier 셀 "-" + 합산식 T3(9)+AINV(1)로 분리 표기. 총합 36 및 폴더명 `Ai-investing-detail/`은 정합(§7 L456 "36 (35 + 5-2 Phase 9 승격)").

### P-7. §22 CAT-B 행 주요 의존성 "ChromaDB, Neo4j"
- **정본**: COND_MODULES_DETAIL_구조화_종합계획서.md L70 — "ChromaDB, Neo4j, **LangChain**"
- **차이**: LangChain 누락. DEC-002(LangChain import 금지)와의 충돌 회피 의도로 추정되나 정본 표기와 불일치. 나머지 6행(CAT-A/C/D/E/F/G)의 Mixin·의존성·모듈 수는 전 셀 일치(L69-75).

### P-8. §24 우선순위 분포 행 "(범위 묶음 산정으로 카테고리 합 1,485와 별도 집계)"
- **정본**: 마스터인덱스 L24 수치(~670/~610/~248, 합 1,545)는 **전 셀 일치**. 단 L26은 차이(60건)의 사유를 "**K/L/M 유령 ID 60건 정정** 전 추정치"로 명시.
- **차이**: 사유 표현이 정본(유령 ID 정정)과 다름 — "범위 묶음" 표현은 READINESS CC-011 기원으로 혼용. 수치 자체는 할루시네이션 아님.

### P-9. §28.4 "**Phase 2 진행 중**"
- **정본**: `VAMOS_최종_로드맵.md` L6 — "Phase 2·4~8 **미착수**"
- **차이**: 로드맵 정본에서 Phase 2 진행 상태 확인 불가. 단 CLAUDE.md 헤더(2026-06-11 "Phase 2-1 보강") 및 본 검증 파이프라인 가동 자체가 Phase 2 활동의 정황 증거 — 로드맵 미갱신 시차로 판단. Phase 0 ✅(L16)/Phase 1 ✅ D1 PASS(L17)/Phase 3 ◐ 결정문서 7종 미생성(L19)/2층 구조·PART2 §4/§5(L23-24, L357, L570)는 모두 VERIFIED.

---

## 4. VERIFIED 주요 근거 요약 (영역별)

### §2 경로·파일 수
- SOT 68개 .md / SOT 2 2,658개 .md·36 도메인 / Guides 38개 — 전부 실측 일치
- D1 스냅샷 2,654: `v13_results/phase0/D1_RESULTS_INDEX.md` L22
- 핵심 39(=21+7+5+5+1)+기타 29=68 산술 정합, C/D/E 그룹 파일 실존(MASTER/INVESTING/CLOUD/TEAMS/SDAR 5종, STEP7 상세명세서 5종, BEGINNER_GUIDE)

### §4 8행 — 줄 수 8/8 전부 wc -l 정확 일치 (1,904/1,266/634/7,049/1,857/4,480/2,218/888)

### §6
- 187 = Named 81(MASTER_SPECIFICATION L172: "I25+E16+S8+A7+B6+C7+D6+EVX6 = 81") + COND 106(2-2 종합계획서 L76)
- D9 확정(I-1~I-25 단일레이어 25): `_targets\DECISION_REGISTER.md` D9 행
- EVX 6행: D2.0-01 §5.13 L743-748(change_lock/activation) + L1774-1779(CORE/EXP status)
- COND 7행: 종합계획서 L69-75 모듈 수·ID 범위 전 셀 일치, 합 13+13+53+8+7+8+4=106
- EVX-7+ 미정의: D2.0-01 L931

### §7.4 신규 2행
- **Hybrid Search**: alpha=0.3(BM25) D2.0-06 S7D-012 L785 + LOCK-AX-06(1-2 AUTHORITY_CHAIN L77) / Top-K 20·α=0.7 Dense(6-4 hybrid_search.md L7, LOCK-MR-008) / threshold 0.75(LOCK-MR-009) / Rerank Top 5 = S7D-018 L862 "top-20 → rerank → top-3~5"의 상한 표기 / 이중 표기 해설 = GLOSSARY #15 L176-179
- **MCP max_retries**: PHASE_B4 §3.9 L359 — V1/V2=2, V3=3, backoff 1s→2s·V3 +4s, D2.0-03/MASTER_SPEC 정본 명시. PART2(구현가이드 PART2) L312/L488 `max_retries = 3` 비정본 표기 실재 확인

### §21 — 36개 도메인 폴더명 36/36 ls 실측 일치(`FILE CONTEXT/` 포함), Tier 배치 DEPENDENCY_GRAPH §1.1 정합, 보조 폴더 5종·SOT2_MASTER_INDEX.md·DEPENDENCY_GRAPH.md 실존

### §22 — Mixin 7종 일치, R7(DEPENDENCY_GRAPH L43)+vamos_lint VL-003(STRATEGY_09 L850/L877 "CORE→COND 역방향 import 금지") 일치, CAT 폴더(CAT-A_AI-ML-Engine/, 04_cat-d-media/, 08_e-series-ops/) 실존

### §23 — 15행 전부 GLOSSARY_CROSS_DOMAIN.md 일치(#1 L24-27, #2 L35-37, #3 L45-47, #4 L55-56, #5 L66-67, #6 L77-80, #7 L88-89, #8~12 L97-129, #13 L156-160, #14 L166-168, #15 L176-179), 구성 7+5+3=15(L183), 접두사 규칙(L13-14), LOCK-BM/BE(L135-137)

### §24 — 17행(A 316 ~ 보강 82) 마스터인덱스 L50-66 전 셀 일치, 합 1,485 산술 정합, 총계 3,041=1,556+1,485(L4/L12)

### §25 — 단방향 90+양방향 27·총 144·36도메인(DEPENDENCY_GRAPH §7 L456-458, L227), 순환 0·R7 위반 0·Tier 위반 0(L460-462), 교차 Tier 6쌍 허용(L459), 방향 규칙 4종(L43-46)

### §26/§27 — Vault 17폴더(00_HUB~99_RAW)·OBSIDIAN-STRATEGY-v3.md·00_HUB 7파일(LOCK-DECISION-REGISTRY.md 포함) 실측 / .claude\CLAUDE.md 177줄·skills 63 dirs(55+신설 claude-md-* 8종)·settings.json hooks 16개·TOOL_GUIDE_46.md 전부 실측 일치

### §28 — STRATEGY_08 v1.1 헤더, STRATEGY_09 §7(L684)/§8(L814 — Layer 1 린터·CI), STRATEGY_11, 로드맵 Phase 0~8(L4), DECISION_REGISTER 17행+D19(L25), §28.3 테이블 9행 로드맵 A13 블록 전행 일치

### §5~§20 표본 33건 (전부 VERIFIED)
| # | claim | 근거 |
|---|-------|------|
| S1~S6 | V1/V2/V3 월·일 비용 상한 6건 | BASE-1.3 L198-211 |
| S7 | Downshift 80% warn/force_mini·100% block | PHASE_B4 L276-277 |
| S8 | Self-check P0:70/P1:75/P2:80 | PHASE_B4 L327-329, D2.0-07 L963 |
| S9 | Soft loop 1회 | PHASE_B4 L330 |
| S10 | Semantic Cache ≥0.95 | PHASE_B4 L540 |
| S11 | 코드 실행 30초 격리 | D2.0-02 L181 |
| S12 | MAX_CONCURRENT_BLUE_NODES=3/TOOLS=5 | D2.0-02 L340 |
| S13 | Failover GPT-4o→Claude→Ollama 3회 | MASTER_SPEC L1520 (※ D2.0-04 L728은 Claude→GPT-4o→DeepSeek→Ollama — SOT 내부 이형, CLAUDE.md 책임 아님) |
| S14 | 턴 상한 P0=5/P1=10/P2=20 | MASTER_SPEC §7.12 L871, D2.0-05 L701 |
| S15 | TEE P0=3/P1=5/P2=10회 | D2.0-05 L735 |
| S16 | RBAC 4역할+한도(L3·₩266K~L0·0) | MASTER_SPEC L1040-1045, D2.0-07 L510/L547 |
| S17 | Autonomy 기본 L1 SUPERVISED | D2.0-07 L430/L434 |
| S18 | Guardrails 4-Layer+L4 사후감사 | D2.0-07 §15.8.1 L1743/L1750 |
| S19 | P2 자동 OFF Option A | D2.0-03 L566 |
| S20 | Non-goal 7개(2.1~2.7) | BASE-1.3 L96-122 |
| S21 | 7개 불변 구역 | D2.0-07 L2276 |
| S22 | 승인 타임아웃 600s/P2 300s | PHASE_B4 L345-350 |
| S23 | DEC-004 64/83/90% | D2.0-06 L1622-1624 |
| S24 | DEC-005 BGE-M3 1024dim | D2.0-06 L1335-1339, PHASE_B4 L185-186 |
| S25 | DEC-010 QoD 0.0~1.0 | D2.0-06 L1331 |
| S26 | DEC-014 RAG 가중치 4요소 | D2.0-06 L1333 |
| S27 | QoD 5요소 PLAN 정본 | GLOSSARY L24 |
| S28 | 청크 300~500tok | D2.0-06 L687 |
| S29 | Self-evo 롤백 14일 | PLAN-3.0 L359 |
| S30 | DEC-015 색상+ORANGE/BLUE | D2.0-08 L544-545, L1450-1451 |
| S31 | DEC-017 Streamable HTTP | PHASE_B4 L357 |
| S32 | QoD <0.4 금지/<0.7 보류 | GLOSSARY L24 |
| S33 | §20 config 20개 LOCK 값 | PHASE_B4 §3 (L144/152/185-186/193-194/204/212/231/274-277/284-287/327-337/349-350/466/499/507/513/522/529/540/547) — 20/20 일치 |

---

## 5. 비고

- **수정 미실시**: 발견 오류는 기록만 함 (지시 준수). SOT 원본 무변경.
- PARTIAL 9건 중 즉시 교정 권고 대상: **P-4(EVX-3 LOCK "-"→false), P-5(§6 3,041 표기), P-7(CAT-B LangChain — 단 DEC-002와의 관계 결정 필요), U-1(§26 Engineering-Matrix 노트 부재)**. P-1/P-9는 시차성, P-6/P-8은 표기 차원.
- SOT 내부 이형 발견(참고): Multi-Brain Failover 체인이 MASTER_SPEC(GPT-4o→Claude→Ollama)과 D2.0-04 L728(Claude→GPT-4o→DeepSeek→Ollama)에서 상이 — Step 3(sot-conflict) 검토 대상.
