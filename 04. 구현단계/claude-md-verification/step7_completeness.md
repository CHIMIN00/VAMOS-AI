# Step 7 — /claude-md-completeness 누락 탐지 보고서

> 실행일: 2026-06-11 | 대상: `D:\VAMOS\CLAUDE.md` (945줄 실측) | 방법: RULE-C12 — ls/grep 실측 직접 비교 (기억 의존 0)
> 스킬 정본: `D:\VAMOS\.claude\skills\claude-md-completeness\SKILL.md` | 수정 0건 — 기록만

---

## 결론 요약

| # | 비교 | 결과 | 참조율 | 실질 누락 |
|---|------|------|--------|----------|
| 1 | SOT 68 파일명 vs CLAUDE.md | 핵심 39/39 식별 가능, 비핵심 26 비참조=설계 | 핵심 100% (전체 식별 42/68=62%) | 1건 (경미 — CLOUD_LIBRARY_SPEC 전체 경로 비대칭) |
| 2 | SOT 2 도메인 폴더 vs §21 | **실측 37 ≠ §21 36** | 36/37 = 97.3% | **1건 (`5-2_File-Context\` 미라우팅)** |
| 3 | 모듈 187 vs §6 | 81 Named + COND 106 전수 확인 | 187/187 = 100% | 0건 |
| 4 | LOCK 네임스페이스 vs §7/§23 | 5종 중 직접 3 + 간접 2, 핵심 체계 커버 | 직접 60% / 커버 100% | 0건 (정성 PASS) |
| 5 | Non-goal 7 vs §8 | 2.1~2.7 항목별 일치 | 7/7 = 100% | 0건 |
| 6 | 교차 용어 15 vs §23 | #1~#15 번호·용어 일치 | 15/15 = 100% | 0건 |

**실질 누락 합계: 2건** (상세는 각 절)

---

## 비교 1 — SOT 68개 파일명 vs CLAUDE.md 언급

- 실측: `Get-ChildItem "D:\VAMOS\docs\sot" -Filter *.md` → **68개** (§2 "68개 .md" 표기와 일치 ✅. sot 내부 `CLAUDE.md` 사본 포함)
- grep 매칭 기준: 전체 파일명 / 코드 토큰(예: `D2.1-Q1`) / 범위 표기 / 그룹 약칭

### 1-A. 핵심 39 (§2 5그룹) — 39/39 식별 가능 (100%)

| 참조 형태 | 건수 | 대상 |
|----------|------|------|
| 직접 토큰 언급 | 28 | BASE-1.3, PLAN-3.0, D2.0-01~08(8), D2.1 D1·D2·D5·D6·D7·D8·A1·Q1(8), PHASE_B1·B2·B3·B4·B7(5), MASTER_SPEC, READINESS_GUIDE, AI_INVESTING, AGENT_TEAMS, SDAR(5) |
| 범위 표기 경유 | 4 | D2.1-D3, D2.1-D4 (§18 "D2.1-D1~D8"), PHASE_B5, PHASE_B6 (§18 "PHASE_B2~B7", §19 "B5") |
| 단축명 | 1 | VAMOS_BEGINNER_GUIDE (§2·CC-002 "BEGINNER_GUIDE") |
| 그룹 약칭만 | 6 | VAMOS_CLOUD_LIBRARY_SPEC (§2 "CLOUD"), VAMOS_STEP7 상세명세서 5종 (§2 "D: STEP7 상세명세 5개 — A-E/F-I/J-M/N-P/보강") |

### 1-B. 비핵심 29 — 설계상 비참조 (누락 아님)

§2 비고("나머지 29개: STEP7 작업가이드·보고서/인덱스 + Readiness 3종 + SUPERSEDED 등") + 스킬 정의("§21/§24 경유 참조로 판정")에 따라 설계로 판정:

- 언급됨 3: `PLAN-2.0_VAMOS_PLAN_2.0_.md` (CC-010 SUPERSEDED), `STEP7_STEP6통합_마스터인덱스.md` (§24 출처), `CLAUDE.md` (sot 사본 — 자기명 일치)
- 미언급 26 (설계상 비참조): STEP7-B~P 작업가이드 15종, `STEP7_작업가이드.md`, `STEP7_A-I_보강_추가항목_통합.md`, `STEP7_PHASE7_최종검증보고서.md`, `STEP7_R1~R6` 6종, `VAMOS_IMPLEMENTATION_READINESS_REVIEW.md`, `VAMOS_V0_READINESS_FINAL_REVIEW.md`
  - STEP7-B~P·상세명세 계열은 §24 카테고리 매핑(A~P, 마스터인덱스 경유)으로 간접 도달 가능

### 1-C. 실질 누락 1건 (경미) — VAMOS_CLOUD_LIBRARY_SPEC.md 참조 비대칭

- §2 그룹 C "특화 SPEC 5개 — MASTER/INVESTING/CLOUD/TEAMS/SDAR"에 약칭 "CLOUD"로만 존재
- grep 확인: `CLOUD_LIBRARY` 문자열 CLAUDE.md 내 **0회**
- 비대칭 근거: 동급 SPEC 4종(MASTER §4 / INVESTING·TEAMS·SDAR §17+§18)은 전체 파일명+경로 제공, Cloud Library SPEC만 §17 특화 시스템·§18 참조 경로 목록에서 부재 (6-8 도메인 라우팅은 §21에 존재)
- 판정: 실질 누락 (심각도 낮음 — 약칭으로 식별은 가능)
- ※ 상세명세 5종의 약칭 처리는 5종 모두 동일 방식(비대칭 없음)이므로 설계상 약칭으로 판정 — CLOUD와 구분

---

## 비교 2 — SOT 2 도메인 폴더 vs §21 라우팅 테이블

- 실측: `Get-ChildItem "D:\VAMOS\docs\sot 2" -Directory` 후 보조 5폴더(`_cross-ref`/`_extractions`/`_automation`/`PHASE3_ORCHESTRATION`/`PHASE4_ORCHESTRATION`) 제외 → **37개** (§2·§21의 "36개"와 불일치 ⚠️)
- §21 매칭: 36/37 폴더명 일치

### 실질 누락 1건 — `5-2_File-Context\` 폴더 §21 미라우팅

| 항목 | `5-2_File-Context\` | `FILE CONTEXT\` (§21이 5-2로 지시하는 폴더) |
|------|---------------------|---------------------------------------------|
| §21 등재 | **없음** | 있음 (T5 5-2 행, "⚠️ 폴더명 주의") |
| 파일 수 (재귀 실측) | **68개** | **1개** (`VAMOS_파일_컨텍스트_이해_최종_업데이트.md`) |
| 구조 | INDEX.md, AUTHORITY_CHAIN.md, CONFLICT_LOG.md, 01_context-pipeline~05_benchmarks, _verification — 구조화 도메인 | 단일 문서 |
| 타임스탬프 | 생성 2026-03-27 / 최종수정 **2026-05-31** | 생성·수정 2026-03-21 (이후 변경 없음) |

- 교차 근거: GLOSSARY_CROSS_DOMAIN.md L93 "5-2 File-Context 도메인 신규 용어" — 정본 용어 5종(Context Rot 등)의 소유 도메인 표기가 구조화 폴더 명칭(`5-2_File-Context`)과 일치
- 판정: **실질 누락** — §21의 5-2 라우팅이 1-파일 레거시 폴더만 지시하고, 68-파일 구조화 도메인 폴더는 미참조. §2/§21의 "36개 도메인" 수치도 실측 37과 불일치. (어느 폴더가 5-2 정본인지의 확정은 본 Step 권한 밖 — 기록만, 수정 0)

---

## 비교 3 — 모듈 187개 vs §6

- §6 테이블 행 수 grep 실측 (`^\| {ID}-\d+ \|` 패턴):
  - I=**25**, E=**16**, S=**8**, A=**7**, B=**6**, C=**7**, D=**6**, EVX=**6** → 합 **81** = 명세(I25+E16+S8+A7+B6+C7+D6+EVX6) 정확 일치
- COND: §6 테이블 CAT-A~G = 13+13+53+8+7+8+4 = **106** ✅ (본문 합산식 명기)
- 총계: 81 + 106 = **187** ✅ (§6 제목 "187개: Named 81 + COND 106" 일치)
- 참조율 100%, 누락 0건

---

## 비교 4 — LOCK 네임스페이스 vs §7/§23 (정성 판정)

- GLOSSARY_CROSS_DOMAIN.md grep 실측 네임스페이스 5종: **LOCK-AX, LOCK-ML, LOCK-BM, LOCK-BE, LOCK-AP**
- CLAUDE.md grep (`LOCK-[A-Z0-9]+`): LOCK-AX(L307 §7.4, L843 §23#15) / LOCK-BM(L772 §21, L846 §23) / LOCK-BE(L778 §21, L846 §23) / LOCK-DECISION(L894 §26 레지스트리)

| 네임스페이스 | 직접 표기 | 간접 커버 |
|-------------|----------|----------|
| LOCK-AX (1-2) | ✅ §7.4 Hybrid Search + §23 #15 | - |
| LOCK-BM (3-9) | ✅ §21 + §23 충돌해결 문구 | - |
| LOCK-BE (5-1) | ✅ §21 + §23 충돌해결 문구 | - |
| LOCK-ML (4-4) | ❌ 토큰 부재 | §23 #1 ML-QoD(4-4) + §21 4-4 "ML-QoD, QA-Gate" |
| LOCK-AP (3-10) | ❌ 토큰 부재 | §23 #14 Autonomy 정본 L0~L4(3-10) + §21 3-10 "Autonomy L0~L4 정본" |

- 핵심 LOCK 체계 커버 정성 판정: **PASS**
  - DEC-001/002/003/017 (§7.1), DEC-004/005/010/014 (§7.4), DEC-011/015 (§7.6) — DEC 개별 표기 10건
  - 비용/안전 LOCK §7.3 전수(V1~V3 상한·Downshift·RBAC·Autonomy·Guardrails·Non-goal·불변 7구역·승인 타임아웃) ✅
  - Self-evo LOCK §7.5 (허용 6/불변 7/롤백 14일) ✅ / config LOCK 20개 §20 ✅ / Gate 5종 §5 ✅
- 실질 누락 0건. 비고: LOCK-ML·LOCK-AP 네임스페이스 토큰 2건 미표기는 간접 커버로 경미(개선 여지로만 기록)

---

## 비교 5 — Non-goal 7개 vs §8

- 정본 grep: `BASE-1.3_VAMOS_RULE_1.3_BASE.md` L96 "## 2. Non-goal(절대 금지)" — 2.1~2.7 7건 실측
- §8 대조 (항목별):

| # | BASE-1.3 §2 (실측) | CLAUDE.md §8 | 일치 |
|---|---------------------|--------------|------|
| 2.1 | 실거래·주문·계좌·API 연동 | 실거래/주문/계좌/API 연동 | ✅ |
| 2.2 | 불법 행위·해킹·권한 상승 | 불법 행위/해킹/권한 상승 | ✅ |
| 2.3 | 의료·법률 단정적 판단/대리 결정 | 의료/법률 단정적 판단/대리 결정 | ✅ |
| 2.4 | 민감 개인정보 장기 저장 | 민감 개인정보 장기 저장 | ✅ |
| 2.5 | 저작권·약관 위반 | 저작권/약관 위반 | ✅ |
| 2.6 | P2 도메인 자동 생성 금지 | P2 도메인 자동 생성 금지 | ✅ |
| 2.7 | 위험 기능 자동 실행 금지 | 위험 기능 자동 실행 금지 | ✅ |

- **7/7 = 100%**, 누락 0건

---

## 비교 6 — 교차 용어 15개 vs §23

- GLOSSARY_CROSS_DOMAIN.md 헤더 grep 실측: #1 QoD / #2 Gate / #3 Pipeline / #4 Agent / #5 Discovery / #6 Score / #7 Breaking / #8 Context Rot / #9 Lost-in-the-Middle / #10 Ms-PoE / #11 NoLiMa / #12 Agentic RAG / #13 5-Gate / #14 Autonomy Level / #15 Alpha 표기
- §23 테이블 #1~#15와 번호·용어·구분 내용(AUX-QoD vs ML-QoD, 5-2 정본 5종, VAMOS-5-Gate/SDAR-Gate/CL-Gate, L0~L4/L0~L3/L0~L4+NEVER, alpha=BM25 0.3) 전부 일치
- §23 출처 표기 "(충돌 7 + 5-2 참조 5 + Phase 11 신규 3)" = GLOSSARY 구성과 일치
- **15/15 = 100%**, 누락 0건

---

## 실질 누락 종합 (2건)

| # | 항목 | 위치 | 심각도 | 근거 |
|---|------|------|--------|------|
| 1 | `5-2_File-Context\` 도메인 폴더 §21 미라우팅 (실측 37 vs 표기 36) | §2, §21 | 중 | 68-파일 구조화 도메인(최종수정 2026-05-31) 미참조, §21은 1-파일 레거시 `FILE CONTEXT\`(2026-03-21)만 지시 |
| 2 | `VAMOS_CLOUD_LIBRARY_SPEC.md` 전체 파일명/경로 미기재 | §2(약칭만), §17·§18(부재) | 하 | 동급 특화 SPEC 4종은 전체 경로 제공 — 단독 비대칭 |

수정 미실시 (Step 7 임무 = 탐지·기록 한정).
