# CLAUDE.md 검증 Step 3 — /claude-md-fact-audit 결과 (3-Agent 토론 재검증)

> **실행일**: 2026-06-11 | **입력**: `step2_hallucination.md` (UNVERIFIED 1 + PARTIAL 9 = 10건)
> **방법**: SKILL.md 3-Agent 토론 — 감사자(일치 근거) / 반박자(불일치 근거) / 판정자(SOT 직접 Read, RULE-C8)
> **원칙**: CLAUDE.md·SOT 수정 미실시 — 기록만. 모든 판정에 파일+라인 근거.

---

## 1. 총괄

| 판정 | 건수 | 항목 |
|------|------|------|
| **승격 (→VERIFIED)** | **2** | P-1, P-8 |
| **확정 (→UNVERIFIED)** | **0** | — |
| **유지 (→PARTIAL)** | **8** | U-1(UNVERIFIED→PARTIAL 완화), P-2, P-3, P-4, P-5, P-6, P-7, P-9 |

재집계 (185 claim 기준): VERIFIED 175→**177 (95.7%)** / PARTIAL 9→**8** / UNVERIFIED 1→**0** — 목표 95%+ **달성**.

---

## 2. 항목별 판정

### U-1. §26 매트릭스 노트 `12_IMPLEMENTATION\Engineering-Matrix.md` — 판정: **유지 → PARTIAL (UNVERIFIED에서 완화)**

- **감사자**: 경로 자체는 발명이 아님. 정본 체계에 동일 경로가 명시됨 — `VAMOS Engineering\STRATEGY_10_VERIFICATION_SYSTEM.md` L231 "□ 매트릭스 노트: 12_IMPLEMENTATION/Engineering-Matrix.md 존재?" / `VAMOS Engineering\ROADMAP_SESSION_EXECUTION_PROMPTS.md` L594 "매트릭스 노트: 12_IMPLEMENTATION/Engineering-Matrix.md". 로드맵 정본 `D:\VAMOS\VAMOS_최종_로드맵.md` L252는 Phase **2-3** 산출물로 "Obsidian 노트 생성 | Strategy v3.0 → 120+ 노트 + **매트릭스 노트**"를 명시 — 생성 예정 파일의 확정된 위치.
- **반박자**: 실측상 `D:\VAMOS\VAMOS HOME\12_IMPLEMENTATION\`는 **빈 폴더**(파일 0개, ls 재확인)이고 Vault 전체에 `Engineering-Matrix` 명칭 파일 없음. CLAUDE.md §26 L895는 "예정" 표기 없이 실존 항목처럼 나열(같은 절의 다른 항목들은 모두 실존).
- **판정자 (직접 확인)**: 빈 폴더 사실 + 경로의 SOT 근거 모두 확인. 경로는 **SOT가 지정한 정본 위치**(STRATEGY_10 L231·로드맵 L252 Phase 2-3 산출물)이므로 "SOT에서 찾을 수 없는 주장"(UNVERIFIED) 요건 불충족. 다만 미생성 파일을 무표기 나열한 점은 불완전 → **PARTIAL**. 권고: §26 해당 행에 "(Phase 2-3 생성 예정)" 주석.

### P-1. §2 구현단계 "782개 파일" — 판정: **승격 → VERIFIED**

- **감사자**: CLAUDE.md L25 "(782개 파일, v8~v13 검증 산출물)"은 실측 시점(2026-06-11, 검증 파이프라인 가동 전) 기준 정확. 동적 값.
- **반박자**: 재실측 `find -type f` = **786개**, 4개 차이.
- **판정자 (직접 확인)**: 786 − 782 = 4. 증가분 전수가 `claude-md-verification\` 본 검증 파이프라인 산출물 4개로 규명됨(실측 ls: step5 22:59 / step7 23:05 / step1 23:07 / step2 23:14 — 전부 2026-06-11 금일 생성). 측정 시점에 782 정합 + 차이 전수 설명 가능 + §2 맥락이 동적 실측값임을 명시("실측 2026-06-11") → **VERIFIED**. 권고(비차단): 검증 파이프라인 종료 시 일괄 재실측 갱신.

### P-2. §2 그룹 A "설계 21개 (~35,472줄)" — 판정: **유지 → PARTIAL**

- **감사자**: 그룹 구성 "BASE+PLAN+DESIGN+SCHEMA"에 PLAN-2.0을 포함하면 BASE-1.3(1)+PLAN-2.0(1)+PLAN-3.0(1)+D2.0×8+D2.1×10 = 정확히 **21개** 재현 가능.
- **반박자**: ① `PLAN-2.0_VAMOS_PLAN_2.0_.md` L1 헤더가 "⚠️ **SUPERSEDED**: PLAN-3.0에 의해 전면 대체" — CLAUDE.md §2 자체가 기타 29개에 "SUPERSEDED 등"을 귀속시키므로 그룹 A 포함은 자기모순. ② 줄 수: 20파일 wc -l 합 = **32,969줄**, PLAN-2.0(4,350줄) 포함 21파일 = **37,319줄** — 어느 조합도 35,472 재현 불가(각 −2,503 / +1,847).
- **판정자 (직접 확인)**: wc -l 전수 재실측으로 반박자 수치 확인. 35,472에 해당하는 단일 파일(2,503줄)도 sot 내 부재. 파일 수 21은 SUPERSEDED 모순, 줄 수는 재현 불가 → **PARTIAL 유지**. 권고: 그룹 A 구성 목록 명시 + "설계 20개 (~32,969줄)" 재실측 정정(또는 PLAN-2.0 포함 기준이면 21개/~37,319줄로 일관화).

### P-3. §2 그룹 B "구현가이드 7개 (~9,618줄)" — 판정: **유지 → PARTIAL**

- **감사자**: 파일 수 7개(PHASE_B1~B7) 정확, "~" 근사 표기이며 오차 1.4%.
- **반박자**: wc -l 합 실측 **9,754줄** — 9,618은 어떤 산정으로도 재현 불가(−136줄). 같은 §2의 C/D/E 그룹은 ±1% 이내인데 B만 이탈.
- **판정자 (직접 확인)**: `wc -l PHASE_B*.md` = 9,754 total 재확인. 파일 수 정확·줄 수만 재현 불가 → **PARTIAL 유지**. 권고: "~9,754줄"로 정정.

### P-4. §6 EVX-3 행 LOCK 셀 "-" — 판정: **유지 → PARTIAL**

- **감사자**: "-"는 'LOCK 아님'의 관용 표기로 `false`와 의미상 동치 가능. 나머지 셀(명칭·status EXP·OFF/OFF/ON) 전부 정합.
- **반박자**: 정본 `D2.0-01` §5.13 **L745** "| EVX-3 | Log-prob Confidence | RE-ADD | **false** | V1:OFF / V2:OFF / V3:ON |" — 명시값 존재. 게다가 CLAUDE.md 같은 표에서 EVX-1/4/5/6은 "false"로 적었으므로(L214~219) "-"는 표 내부 일관성도 깨짐 — 미정으로 오독될 위험.
- **판정자 (직접 확인)**: D2.0-01 L743-748 직접 Read — EVX-3 change_lock = `false` 명시 확인. 값이 존재하는데 "-"로 표기 → 의미 동치 주장 기각, **PARTIAL 유지**. 권고: §6 EVX-3 LOCK 셀 "-"→"false".

### P-5. §6 하단 "**STEP7**: 16개 카테고리(A~P) 3,041건" — 판정: **유지 → PARTIAL**

- **감사자**: 3,041 자체는 정본 수치(총계)이고, CLAUDE.md §24 L852가 "총 3,041건 = STEP6 1,556 + STEP7 1,485"로 정확 분해 — 문서 내 자체 해소.
- **반박자**: 정본 `STEP7_STEP6통합_마스터인덱스.md` L4 "STEP6 1,556건 + STEP7 1,485건 = 총 3,041건" / L10-12 표 동일. A~P 16개 카테고리(+보강)의 합은 **1,485**(STEP7측)이지 3,041이 아님 — L238 문장은 STEP6 포함 총계를 카테고리 귀속처럼 기술한 합산 혼동.
- **판정자 (직접 확인)**: 마스터인덱스 L1-14 직접 Read로 양측 수치 모두 확인. 수치는 실존하나 귀속 서술이 정본과 불일치(§24가 해소하므로 모순은 비치명) → **PARTIAL 유지**. 권고: L238을 "16개 카테고리(A~P)+보강 1,485건 (STEP6 포함 총 3,041건)"으로 정정.

### P-6. §21 AINV 행 Tier "-" — 판정: **유지 → PARTIAL**

- **감사자**: CLAUDE.md L797 합산식 "T3(9)+AINV(1) = 36"은 총합 36 정합(DEPENDENCY_GRAPH §7 L456 "36 (35 + 5-2 Phase 9 승격)"과 일치), 폴더명 `Ai-investing-detail/`도 실존. AINV는 '상세 하위도메인' 성격이라 별도 표기에 운영상 이유 있음.
- **반박자**: 정본 `DEPENDENCY_GRAPH.md` §1.1 **L25** "Tier 3 ─ Feature Domains (3-2 ~ 3-10, **AI-Investing**)" — AINV의 Tier 소속은 명시적으로 **Tier 3**. "-"는 정본에 존재하는 값을 비워둔 것.
- **판정자 (직접 확인)**: DEPENDENCY_GRAPH L20-30·§7 L450-465 직접 Read. AINV Tier 3 소속 명시 확인 — 총합·폴더명은 정합하나 Tier 셀이 정본 값과 다름 → **PARTIAL 유지**. 권고: Tier 셀 "-"→"T3"(합산식은 'T3(9+AINV 1)' 등으로 일관화).

### P-7. §22 CAT-B 의존성 "ChromaDB, Neo4j" — 판정: **유지 → PARTIAL**

- **감사자**: 기재된 2개는 정본과 일치하고, LangChain 누락은 DEC-002(CLAUDE.md L249: "LangChain import 금지, Allowlist `langchain-core`/`langchain-community`/`langchain-openai`만 허용")와의 충돌 회피로 해석 가능한 의도적 생략.
- **반박자**: 정본 `COND_MODULES_DETAIL_구조화_종합계획서.md` **L70** "| **B** | Knowledge | 13 | ... | KnowledgeMixin | ChromaDB, Neo4j, **LangChain** |" — 정본 표기에서 1개 누락. 나머지 6행은 전 셀 일치이므로 단순 전사라면 B행만 빠질 이유 없고, '의도적 생략'이라면 주석 없는 무단 변형.
- **판정자 (직접 확인)**: 종합계획서 L65-78 직접 Read — LangChain 명시 확인. DEC-002 Allowlist 체계상 LangChain 표기와 금지 결정은 양립 가능(본체 금지·어댑터 허용)하므로 생략의 정당화 근거 부족 → **PARTIAL 유지**. 권고: "ChromaDB, Neo4j, LangChain(DEC-002 Allowlist 한정)"으로 정본 정합 + 결정 참조 병기.

### P-8. §24 "(합 ~1,545는 범위 묶음 산정으로 카테고리 합 1,485와 별도 집계)" — 판정: **승격 → VERIFIED**

- **감사자**: ① 수치 전수 정합 — 마스터인덱스 L18-24 우선순위 표(V1 ~670 / V2 ~610 / V3 ~248, 합 1,545) 전 셀 일치. ② "범위 묶음" 표현은 SOT 직접 근거 보유 — `VAMOS_IMPLEMENTATION_READINESS_GUIDE.md` §6.12 **L998** "STEP7 항목 수 60건 차이 (CC-011)" / **L1003** "**해소** | 범위 묶음(range bundle) 전개 시 차이 발생 — 개별 문서 참조 기준이 정본" / **L1107** ""범위 묶음 전개 후 실제: ~1,485건" 비고".
- **반박자**: §24의 인용 출처인 마스터인덱스 **L26**은 차이 사유를 "K/L/M 유령 ID 60건 정정... 정정 전 추정치"로 명시 — 인용 출처와 사유 표현이 다름.
- **판정자 (직접 확인)**: 양 문서 직접 Read. 동일한 60건 차이(1,545 vs 1,485)에 대해 SOT 두 문서가 각기 다른 설명(유령 ID 정정 / 범위 묶음 전개)을 보유 — CLAUDE.md는 그중 READINESS CC-011의 정본 표현을 채택했고 수치는 전수 정합. 이는 CLAUDE.md 할루시네이션이 아니라 **SOT 내부 이형**(Step 1 sot-conflict 관할) → **승격 VERIFIED**. 비고: 마스터인덱스 L26 ↔ READINESS L1003 사유 이형은 SOT 충돌 목록에 기록 권고(CLAUDE.md 귀책 아님).

### P-9. §28.4 "**Phase 2 진행 중**" — 판정: **유지 → PARTIAL**

- **감사자**: 본 검증 파이프라인 자체가 Phase 2 활동(로드맵 L53 "Phase 2 = CLAUDE.md 보강 + Obsidian 생성 + 린터/CI"). CLAUDE.md 헤더 L3 "최종 갱신: 2026-06-11 (Phase 2-1 보강 — §21~§28 신설)" — 보강된 CLAUDE.md의 실존 자체가 로드맵 L18 비고("보강된 CLAUDE.md 미생성")가 stale함을 입증. 사실관계상 Phase 2는 진행 중.
- **반박자**: 로드맵 정본 `D:\VAMOS\VAMOS_최종_로드맵.md` **L6** "진행: ... Phase 2·4~8 **미착수**" / **L18** "| **2** 보강/환경 | ⬜ **미착수** |" — 인용 가능한 정본 텍스트는 명백히 '미착수'. 정본이 갱신되기 전까지 CLAUDE.md 주장은 SOT 무근거.
- **판정자 (직접 확인)**: 로드맵 L1-30 직접 Read — L6/L18 '미착수' 확인, 동시에 L18 비고의 "보강된 CLAUDE.md 미생성"이 실측과 모순(보강본 실존)임도 확인 — 로드맵 측이 stale. 사실은 진행 중이나 정본 텍스트와 불일치하는 **시차성** 사안(로드맵 헤더는 세션 종료 시 갱신 예정) → **PARTIAL 유지**. 권고: 세션 종료 시 로드맵 L6/L18 갱신으로 자동 해소(본 단계에서는 수정 금지 준수, 기록만).

---

## 3. 수정 권고 목록 (기록만 — 본 단계 수정 미실시)

| # | 위치 | 권고 | 출처 근거 |
|---|------|------|----------|
| R-1 | CLAUDE.md §26 L895 | "(Phase 2-3 생성 예정)" 주석 추가 | 로드맵 L252, STRATEGY_10 L231 |
| R-2 | CLAUDE.md §2 L30 | 그룹 A "21개/~35,472줄" → 구성 목록 명시 + "20개/~32,969줄" 재실측 정정(PLAN-2.0 포함 기준이면 21개/~37,319줄) | sot wc -l 실측, PLAN-2.0 L1 SUPERSEDED |
| R-3 | CLAUDE.md §2 L31 | 그룹 B "~9,618줄" → "~9,754줄" | PHASE_B1~B7 wc -l |
| R-4 | CLAUDE.md §6 L216 | EVX-3 LOCK 셀 "-" → "false" | D2.0-01 §5.13 L745 |
| R-5 | CLAUDE.md §6 L238 | "16개 카테고리(A~P) 3,041건" → "16개 카테고리(A~P)+보강 1,485건 (STEP6 포함 총 3,041건)" | 마스터인덱스 L4/L10-12 |
| R-6 | CLAUDE.md §21 L795 | AINV Tier 셀 "-" → "T3" (합산식 일관화) | DEPENDENCY_GRAPH §1.1 L25 |
| R-7 | CLAUDE.md §22 L811 | CAT-B 의존성에 "LangChain(DEC-002 Allowlist 한정)" 병기 | 종합계획서 L70 + CLAUDE.md L249 |
| R-8 | (SOT 측, Step 1 관할) | 마스터인덱스 L26(유령 ID) ↔ READINESS L1003(범위 묶음) 60건 차이 사유 이형 — SOT 충돌 목록 등재 | P-8 판정 |
| R-9 | (SOT 측, 세션 종료 시) | 로드맵 L6/L18 Phase 2 상태 갱신 — P-9 자동 해소 | 로드맵 stale 확인 |
| R-10 | (비차단) CLAUDE.md §2 L25 | 검증 파이프라인 종료 후 파일 수 일괄 재실측 | 786 실측(검증 산출물 +4) |

---

## 4. 비고

- 판정자는 10건 전건에 대해 SOT 원본을 직접 Read 확인함(RULE-C8): D2.0-01, STEP7_STEP6통합_마스터인덱스, DEPENDENCY_GRAPH, COND 종합계획서, VAMOS_IMPLEMENTATION_READINESS_GUIDE, VAMOS_최종_로드맵, PLAN-2.0, PHASE_B1~B7, OBSIDIAN-STRATEGY-v3, STRATEGY_10, ROADMAP_SESSION_EXECUTION_PROMPTS + 폴더/파일 수 실측.
- CLAUDE.md·SOT 무수정 — 기록만 수행.
- UNVERIFIED 0 달성: U-1은 경로의 SOT 근거(예정 산출물 정본 위치) 확인으로 PARTIAL로 완화. 잔여 PARTIAL 8건 중 6건(P-2/3/4/5/6/7)은 단순 표기 정정으로 해소 가능, 2건(U-1/P-9)은 Phase 2-3 진행·로드맵 갱신으로 자연 해소 예정.
