# FINAL_TARGET_VERDICT — Phase 0·1 미스 타겟 갭 재검증 (T1~T8)

> 작성 2026-06-06 · **READ-ONLY** (어떤 SOT 정본도 수정/생성/삭제하지 않음 — 발견은 보고만, 정본 변경은 사람 위임)
> 본 문서는 기존 `D1_VERDICT.json`을 **대체하지 않는다**. Phase 0·1이 "놓친 부분"을 겨냥한 **별도 갭 재검증** 산출물이다.
> 심판 = **원본 소스**. 모델 신원(Claude/GPT) 가중치 0. 모든 판정은 현행 SOT 원문을 재독해 내렸다.
> 정본 우선순위: RULE 1.3 > PLAN 3.0 > DESIGN 2.0 LOCK > DESIGN 본문 > 스키마/STEP7.

---

## 0. 한 줄 결론

- **Phase 0 = ISSUES (비차단, 문서 드리프트)** — 로드맵의 `CONFLICT OPEN 0` overclaim·매트릭스 산술 오류(22→20)·인벤토리 수치 드리프트(5/12, 648/710/2,654)·태그 미푸시. 모두 **문서 정합** 문제이며 코드 결함 아님(Phase 2·4~6 미착수).
- **Phase 1 = PASS_CONDITIONAL 유지, 단 실질 결함 백로그 확인** — D1 값 게이트(CONFLICT active 0 / MISMATCH 0 / LOCK 0 / SDV-1 0)는 **유효**하다. 그러나 D1 게이트가 **구조적으로 검사하지 않는 영역**(설계 타당성·SOT 의도 충실도·참조 무결성)에서 **양측 AI가 독립 확인한 실제 설계 결함 343건 + GPT 단독 확인 130건**과 **참조 dangling 8건**이 존재한다. **새로운 차단성 수치 충돌은 0건**(GP-B 10건은 재독 결과 모두 비차단).
- **즉, "값/충돌 게이트는 깨끗하나, 설계 콘텐츠 품질은 사람 검토가 필요한 실결함 백로그를 안고 있다."**

---

## 1. 진짜 이슈 (심각도순 · 근거 · 양측 합의 여부)

> 분류: **A**=객관(수치/참조/LOCK/구조, 소스가 정답) · **B**=의미-검증가능(SOT 의도) · **C**=주관(설계 합리성, 단일 정답 없음→사람결정).

### [HIGH] 양측 AI 독립 확인 설계 결함 — 343건 source-confirmed (대표 예시)
**합의: Claude(CL-C 2모델) + GPT(GP-A) 양측 + 원본 재독 확인.** 유형 대부분 **C**(설계), 일부 **A/B**(객관적 오류). D1 게이트가 못 잡는 영역. 전체는 `crossAI_diff.json › design_convergence`.

| 도메인 | 결함 | 유형 | 근거(file) |
|---|---|---|---|
| 6-4 Memory-RAG | **SQL injection** — 테이블명 f-string 보간(미검증) | A(보안) | `01_memory-hierarchy/managed_db_v3.md` |
| 6-4 Memory-RAG | **assert 기반 tenant_id/project_id 검증** — `python -O`에서 무력화(테넌트 격리 우회) | A(보안) | `01_memory-hierarchy/multi_tenancy_v3.md` |
| 4-4 MLOps | **CanaryJudge가 p≥0.05에서 승급** — 귀무가설 비기각을 양성으로 오판(통계 역전) / `significance_level` le=0.10 허용이 LOCK-ML-04(0.05 전용) 위반 | A(로직) | `01_prompt-versioning/...` |
| 3-4 Workflow-RPA | **webhook `auth_mode=none`** — 미인증 워크플로 트리거 허용 | A(보안) | `03_trigger-system/webhook_trigger.md` |
| 3-4 Workflow-RPA | **PAUSED 상태가 LOCK-WF-09 정본 상태머신 위반** (status enum 분기) | A(로직) | `01_dag-engine/execution_engine.md` |
| 1-1 Verifier | **Failover 전역 데드라인 부재** — 3-tier 체인이 총 SLA 초과 가능 / LOCK-VR-06 타임박스·비용 SoT 미정의 | B/C | `00_common/failover_policy.md` |
| 0-0 Governance | **§2.9 R1~R11 적용 범위 20도메인** (Tier6·4-4 누락 — 거버넌스 정본이 전 도메인 미포괄) | A(누락) | `GOVERNANCE_RULES_META_규칙서.md` |
| Ai-investing | **trailing-stop이 마지막 바 기준** (`highest_price_since_entry` 슬라이스 버그) / **HMM 매 호출 재학습**(캐시 미사용) | A(로직) | `01_realtime-adaptive/*` |

→ 클러스터: **보안 fail-open**(SQLi·assert·auth none) · **통계/로직 오류**(p≥0.05·슬라이스·재학습) · **상태머신 정합** · **표준 구성요소/SLA 미정의**. 구현 전 정정 권고.

### [HIGH] GPT 단독 확인 결함 — 130건 source-confirmed (Claude 맹점, §5-3 더 엄격 검증 후 유효 확정)
**합의: GPT 단독 → 원본 재독으로 기각 아님 확정.** 대표:
- **6-13 Operations**: V2 RPO LOCK-OP-02=1시간인데 `pg_dump` cron이 `0 */6 * * *`(6시간) — 문서 스스로 "6시간(RPO 1시간 보장)" 모순. (A)
- **0-0**: §1.5 V0 비용 ₩0(로컬) vs §3.2 GO/NO-GO "V0=V1 동일 ₩40,000" 충돌. (A)
- **6-4**: `LOCK-MR-018` 확인 훅 미등록 + `user_confirmation_default=True` → 무확인 통과. (C)
- Ai-investing: P2 HITL 승인이 `actor_id`/세션 바인딩 없이 `is_explicit`만 검사. (A 보안)

→ Claude CL-C가 놓친 실결함이 존재함을 확인(상관편향 차단 작동). 전체는 `crossAI_diff.json › per_domain.top_gpt_only_confirmed`.

### [HIGH→deferred] T3 참조 무결성 — dangling 8건 (CL-A 발견 → 재독 CONFIRMED_REAL)
**합의: Claude 발견, GPT 미대상, 원본 확인.** 유형 **A**.
- 도메인명 변경 링크 3 (구 경로가 현행 파일에 잔존): `3-3_Personal-Knowledge-Management`→`3-3_PKM-Knowledge-Management` · `3-8_Conversation-Design-A2A`→`3-8_Conversation-A2A` · `6-12_Event-Logging-Observability`→`6-12_Event-Logging`.
- `D2.0-09 / D2.0-10 / D2.0-11` 참조 — 실존 설계문서는 `D2.0-01~08`뿐(SOT2_SESSION_EXECUTION_PROMPTS.md 등). → **정본 링크 교정 사람 위임**.

### [MED] 로드맵 overclaim·산술 (CL-B/T4 → 재독 CONFIRMED_REAL)
**합의: Claude 발견, 원본 확인.** 유형 **A**.
- **T4-OC-01**: `VAMOS_최종_로드맵.md:28/31` "CONFLICT OPEN 0"(무조건 불변식)이 **같은 문서** `:12/:17/:172`의 "5-3 C-04~C-08 5건 OPEN"과 직접 모순. 권고: "**active(차단) 0 · 비차단 이연 OPEN 5(5-3)**"로 한정 표기. (6-5 W-CB는 v1.3 RESOLVED — 반례 아님.)
- **T4-CON-02**: `STRATEGY_08:146` "실질 22셀" 산술 불성립 → 실제 **20셀**(D4+B6+R6+X4). `P0-2:301` "16 실질셀(F열 제외)"=20이 자기확정. 오수치 22가 5개 문서로 전파.
- **T4-CON-01/03**: 핵심 도메인 5 vs 12 (STRATEGY_02 문서 내 모순; 정답 5) · SOT2 파일수 648/710/2,654 혼재(디스크 실측 2,654). 유형 A.
- **T4-UNMET-01**: `phase0-complete`/`phase1-d1-pass` 태그·커밋 3개 **원격 미푸시**(origin/main=0d49b6c). 백업 본질 미성립. → `git push origin main --tags`.

### [MED→deferred] 동일개념 stale-text 공존 (GP-B 수치 재독) — 우선순위로 해소되나 잔존 텍스트 정리 필요
**합의: GPT(GP-B)가 표면 충돌로 검출 → 재독 결과 same-concept stale.** 유형 **A/B**. 우선순위가 정답을 정하나 **물리 텍스트 정리는 사람 위임**.
- **#5 BGE-M3 V1 기본 차원** — `D2.0-06` 내부에서 "V1 기본 256"(L772/845)과 "V1 기본 1024"(L1331)가 자기모순 + 자동선택(<5,000→1024)도 공존. LOCK-AX-07=`1024-dim/Matryoshka 256`.
- **#6 QoD 공식 4요소 vs 5요소** — `CLAUDE.md:269`(4요소)과 `:270`(5요소 PLAN정본) 공존, `:415 [ ] QoD 5요소 공식 통일 (V1-006)`이 **미완 체크박스**. 정본=5요소(PLAN-3.0), 4요소 SUPERSEDED.
- **#9 L0/Session TTL** — 7일 / 세션종료 즉시 / 최대30일 / `session_end or created_at+30일` 혼재. `AUTHORITY 6-4 LOCK-MR-003`이 `⚠️ CONFLICT_LOG #006`으로 자체 표기(관리 중).
- **#10 메모리 계층 수 4 vs 5** — 정본 4계층(L0~L3, `STEP7_J-M:451`이 "L4 Archive는 V2+ 참조용"으로 정리) vs STEP7-D/STEP7 가이드 "5계층" 표현 잔존.
- **memory_search 4 vs 5** (CL-A T2 신규후보 → CONFIRMED_REAL): `D2.0-03 BLUE_NODES:262`(4) vs `STEP7-K:29`(5), 동일 MCP 도구목록 K-001 내 동일 속성. 소형 실충돌.
- **#1 V1 비용상한 stale 1건**: `STEP7_보강_통합명세서:120` "I-9 비용상한 ₩10,000(V1)"이 정본 ₩40,000과 불일치(저우선순위 잔존). #2 `:525` "V2 ₩40,000"도 동종 stale.

### [LOW / 비이슈] GPT 과대검출 — 재독 결과 충돌 아님 (TWO_DIFFERENT_CONCEPTS)
**합의: GPT가 MISMATCH로 표기 → 원본 맥락 재독 시 서로 다른 개념. 소스가 Claude T1("신규 실 MISMATCH 0")을 지지.** 유형 **B**.
- **#1~#3 비용상한 대부분** — ₩40K/93K/266K = **사용자 월 예산 상한(LOCK-BM/CD)**; ₩10K/40K/20만 = (a)기능 **구현성 등급 임계**(`STEP7_A-E:29` "V1가능 ≤1만원") (b)**3-Tier 구독가격**(`통합:668` "Free/Starter ₩0~10,000") (c)MVP 운영목표. **별개 지표**. (단 #1 L120·#2 L525 stale 예외는 위 MED에 분리.)
- **#4 Python 3.11+ vs 3.12** — 3.11+는 **전역 스택 하한**, 3.12는 **AI-Investing 도메인 고정**(`D-S5-01 3.12 확정`). 3.12 ⊇ "3.11+" 충족 → 충돌 아닌 도메인 정제.
- **#7 QoD 0.7 조치** — `<0.4 L2금지`·`<0.7 출력보류`·`≥0.7 L2허용`은 **상보적 임계 구간**, 모순 아님.
- **#8 승인 타임아웃** — `P1=30/P2=15분`(BASE-1.3 우선순위 타임아웃)과 `일반10/HITL5분`(D2.0-07 승인게이트 타임아웃)은 **다른 게이트**.

### [KNOWN] 5-3 C-04~C-08 — 현행 OPEN 5건 (변동 없음)
조건부·비차단 이연. 본 재검증으로 신규 발생/해소 없음. D1 PASS_CONDITIONAL의 알려진 조건.

---

## 2. Claude ↔ GPT 교차 대조 요약 (crossAI_diff)

| 레이어 | Claude | GPT | 원본-심판 결과 |
|---|---|---|---|
| **수치/충돌 (GP-B 10)** | T1 0 auto-confirmed · T2 14 재도출 0회귀 | 10 MISMATCH 확정 | **genuine 신규 차단충돌 0** · same-concept stale 4(+2부분) deferred · two-concepts 과대검출 4 |
| **설계 타당성 (T8)** | CL-C 7,318 | GP-A 설계 다수 | **convergent source-confirmed 343** + GPT-only 130 = 실결함 백로그 |
| **SOT 충실도 (T6)** | CL-C 1,686 | GP-A FIDELITY | 사람 검토 대상(인용 원문 교차) |
| **메타 (T4)** | CL-B FAIL(4모순+1overclaim) | — | 전건 CONFIRMED_REAL |
| **참조 (T3)** | CL-A FAIL 8 | — | 8건 CONFIRMED_REAL |

- **상관편향 차단(§5-3) 작동**: GPT 단독 130건 / Claude 단독 235건 모두 기각 없이 원본 확인. "Claude니까 맞다" 기본승 미적용.
- **수렴 = 신뢰 상향**: 343 convergent는 두 모델군 독립 + 원본 3중 확인 → 최고 신뢰.

---

## 3. 커버리지 증명 (T1~T8 수행/판정)

| 타겟 | 수행 | 판정 | 근거 |
|---|---|---|---|
| **T1** LOCK/수치/날짜/버전 | CL-A 결정론 + GP-B 10 재독 | **PASS** (신규 차단충돌 0) | `T1_lock_numeric_scan.json` · `crossAI_diff`(GP-B) |
| **T2** SOT 내부충돌 재도출 | CL-A 14 재도출 + 신규후보 1 재독 | **PASS** (0 회귀; memory_search 1건 CONFIRMED) | `T2_independent_conflicts.json` |
| **T3** 참조 무결성 | CL-A + 재독 | **FAIL** (dangling 8 CONFIRMED → 사람 위임) | `T3_reference_validity.json` |
| **T4** 메타(로드맵·Phase0 산출물) | CL-B + 재독 | **FAIL** (overclaim 1·모순 3 CONFIRMED) | `T4_meta_audit.json` |
| **T5** 동의어/이의어 | CL-A 1,439 구조 + CL-C SYNONYM 1,521 | **REPORT_ONLY** (의미 확정 사람) | `T5_homonyms.json` · CL-C |
| **T6** SOT 의도 충실도 | CL-C 1,686 + GP-A | **REPORT** (사람 교차) | `T6T8_*.json` |
| **T7** SDV-2/5/6 추출 | CL-A 17,577 SC-item | **PASS** (SDV-2/5 FAIL 0; SDV-6 WARN 488) | `T7_sdv256.json` |
| **T8** 설계 타당성 | CL-C 7,318 + GP-A; 343 convergent + 130 GPT-only 확인 | **REPORT** (실결함 백로그 — 구현 전 정정 권고) | `crossAI_diff.json` |

게이트형(T1/T2/T3/T7) 중 **T3 FAIL**. 메타 **T4 FAIL**. 나머지 보고형은 사람 위임 백로그.

---

## 4. 이연 · 정본 변경 필요 목록 (자동 수정 안 함 — 사람 승인 후)

1. **T3 링크 교정 3건** — 도메인명 변경 cross-ref(3-3/3-8/6-12 구경로) 현행 파일에서 교체.
2. **T3 D2.0-09/10/11 참조 정리** — 미존재 설계문서 참조(SOT2_SESSION_EXECUTION_PROMPTS.md 등).
3. **로드맵 overclaim 한정** — `:28/:31` "CONFLICT OPEN 0" → "active 0 · 비차단 이연 OPEN 5(5-3)".
4. **매트릭스 22→20 정정** + 17폴더×20셀 통일(STRATEGY_08/P0-2/phase0_retro/STRATEGY_11 전파분).
5. **수치 드리프트 통일** — 핵심도메인 5(STRATEGY_01/02 "12"→5) · SOT2 파일수 2,654 기준.
6. **stale-text 정리(우선순위로 이미 해소, 텍스트만)** — QoD 5요소(V1-006 미완) · BGE V1 기본차원 · L0 TTL(CONFLICT_LOG #006) · 메모리 4계층 표기 · memory_search 4/5 · 비용상한 stale 2줄(통합:120/525).
7. **백업 푸시** — `git push origin main && git push origin --tags`(phase0-complete/phase1-d1-pass 원격 반영).
8. **설계 실결함 백로그(구현 전)** — 보안 fail-open(SQLi 6-4·assert -O 6-4·webhook auth none 3-4·P2 actor 미바인딩) · 통계/로직(CanaryJudge p≥0.05 4-4·trailing-stop/HMM Ai-investing) · 상태머신(PAUSED 3-4) · SLA/RPO(VR-06 1-1·OP-02 6-13) · 거버넌스 R1~R11 범위(0-0). 전체 `crossAI_diff.json`.
9. **5-3 C-04~C-08** — 기존 이연 유지(본 재검증 변동 없음).

---

## 5. 정직한 한계 (R16)

- **A·B(객관/의미-검증가능)**: 원본 재독으로 단정 가능 — 위 근거(file:line)로 확정. T3·T4·수치 stale·보안 SQLi 등.
- **C(주관·설계 합리성)**: 단일 정답 없음 → 양측 논거 + 원본 근거를 나란히 제시, **사람 결정**. 설계 백로그의 다수(아키텍처 선택·SLA 값·표준 구성요소 추가 여부)가 여기 해당. **"완벽/단정" 표기하지 않는다.**
- **샘플링 cap**: 도메인별 convergent는 ≤12로 cap → **343은 확인된 하한(floor)**, 실제 수렴은 더 많음. 단일모델 9,319(CL-C) + GP-A 단일은 전수 사람 검토 대상.
- **본 작업은 어떤 SOT 정본도 수정하지 않았다.** D1_VERDICT.json도 불변.

---

## 6. 산출물

- `_targets/crossAI_diff.json` — 본 교차대조 원자료(GP-B 10 · 메타 3 · 36도메인 수렴).
- `_targets/gpt/GP-A/*.json`(36) · `_targets/gpt/GP-B.json` — GPT 결과(MD에서 추출).
- `_targets/_integ/` — 추출/축약/워크플로 스크립트 · 워크플로 결과(`integ_result.json`).
- 입력: CL-A(`phase0/_targets/`) · CL-B `T4_meta_audit.json` · CL-C `T6T8_*.json`(36)·`_clc_aggregate.json`.

> **경로 주의**: CL-A는 `04. 구현단계/v13_results/phase0/_targets/`, CL-B·CL-C·GPT·본 통합은 `D:/VAMOS/_targets/`에 있다(작업 분기 결과). 본 최종 판정서 사본은 canonical `phase0/_targets/`에도 둔다.
