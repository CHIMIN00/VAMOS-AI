# FIX_MANIFEST — Phase 0·1 정본 수정 매니페스트 (전수 재검증 · 수렴 확정)

> 2026-06-06 · **READ-ONLY 보고** (자동 수정 안 함 — 사람 승인 후 적용) · 모든 발생 위치를 grep 전수 열거(예시 아님).
> 수렴 기준: 객관(Type-A) 문서 드리프트는 전수 스캔으로 **모든 occurrence 확정** → 더 늘지 않음. 설계 결함(C)은 R16상 "완전/완벽" 단정 불가.

---

## TIER 1 — Phase 0·1 "문서 완벽화"용 신규 교정 (프로젝트 자체 레지스트리 미등록 → 반드시 처리)

### 1-1. T3 도메인명 변경 링크 — **3줄 / 2파일** (전수, 더 없음 확인)
| # | 파일:줄 | 현재(구 경로) | 교정값 |
|---|---|---|---|
| 1 | `docs/sot 2/3-5_Education-Learning/05_learning-analytics/challenge_leaderboard.md:39` | `../../3-3_Personal-Knowledge-Management/` | `../../3-3_PKM-Knowledge-Management/` |
| 2 | `docs/sot 2/3-7_Developer-Tools-API-SDK/02_code-completion/realtime_collaboration.md:40` | `../../3-8_Conversation-Design-A2A/` | `../../3-8_Conversation-A2A/` |
| 3 | `docs/sot 2/3-7_Developer-Tools-API-SDK/02_code-completion/realtime_collaboration.md:41` | `../../6-12_Event-Logging-Observability/` | `../../6-12_Event-Logging/` |

### 1-2. T3 미존재 설계문서 참조 D2.0-09/10/11 — **SOT2_SESSION_EXECUTION_PROMPTS.md** (실존 D2.0-01~08뿐)
| 파일:줄 | 참조 | 조치 |
|---|---|---|
| `docs/sot 2/SOT2_SESSION_EXECUTION_PROMPTS.md:7678` | `D2.0-09 ...INFRASTRUCTURE.md` | 참조 제거 또는 실존 SOT로 교체 |
| `:7803` | `D2.0-10 ...BENCHMARK.md` | 〃 |
| `:7804` | `D2.0-11 ...TECHNICAL_STACK.md` | 〃 |
| `:8015` | `D2.0-09 ...INFRASTRUCTURE.md` | 〃 |
| `:8016` | `D2.0-11 ...TECHNICAL_STACK.md` | 〃 |
> 전수 grep: 본 파일 외 1건(메타/로드맵 영역) 가능 → `grep -rn "D2\.0-09\|D2\.0-10\|D2\.0-11"`로 잔여 0 확인 후 종료.

### 1-3. 로드맵 overclaim "CONFLICT OPEN 0" — **2줄** (PROGRESS.md:22는 이미 정확 — 수정 불요)
| 파일:줄 | 현재 | 교정 |
|---|---|---|
| `VAMOS_최종_로드맵.md:28` | `... CONFLICT OPEN 0` | `CONFLICT active(차단) 0 · 비차단 이연 OPEN 5(5-3 C-04~C-08)` |
| `VAMOS_최종_로드맵.md:31` | `불변식 전 도메인 유지: CONFLICT OPEN 0 ...` | 동일 한정 표기 |

### 1-4. 매트릭스 산술 "22셀" → **20셀** — **14줄 / 7파일** (전수)
정답 20 = D4 + B6 + R6 + X4 (B2/R2 부모-자식 이중계상이 22의 원인). 자기확정 근거: `P0-2_OBSIDIAN_MATRIX_MAPPING.md:301` "16 실질셀(F열 제외)"=20.
- `VAMOS_최종_로드맵.md:596`
- `VAMOS Engineering/STRATEGY_08_ENGINEERING_MATRIX.md:82, 146, 182, 1327, 1386`
- `VAMOS Engineering/P0-2_OBSIDIAN_MATRIX_MAPPING.md:6` (그리고 :13-16 약어 열거는 이미 20)
- `VAMOS Engineering/STRATEGY_10_VERIFICATION_SYSTEM.md:51, 150`
- `VAMOS Engineering/STRATEGY_11_ASSET_INVENTORY.md:179`
- `VAMOS Engineering/ROADMAP_SESSION_EXECUTION_PROMPTS.md:56, 238`
- `VAMOS Engineering/decisions/phase0_retro.md:14, 22`

### 1-5. 핵심 도메인 "12개" → **5개** — **4줄** (정답 5: STRATEGY_02:118 자체 열거 T0(1)+T1(2)+T2(2))
- `VAMOS Engineering/STRATEGY_01_FAILURE_AND_RISK.md:61, 180`
- `VAMOS Engineering/STRATEGY_02_SCOPE_AND_PRIORITY.md:51, 175`
> 로드맵(:177,187,223,518)은 이미 "5개"로 정합 — 수정 불요.

### 1-6. SOT2 파일수 648/710 → 디스크 실측 통일 — **12줄** (실측 2,654 전체 / 1,979 검증대상[_automation 제외])
- "648": `STRATEGY_11:98, 434` · `STRATEGY_08:162, 169, 1042`
- "710": `STRATEGY_11:29, 102, 554` · `STRATEGY_08:1365` · `P0-2_DESIGN_ASSET_MAP:37, 167` · `VAMOS_최종_로드맵.md:187`
> 권고: "상세화 대상 710 ↔ 전체 산출 2,654(검증대상 1,979)"로 명시 구분, 또는 2,654 기준 통일. 폴더수 "38" → 실측 확인 권장.

### 1-7. 백업 푸시 (UNMET-01) — 태그·커밋 원격 미반영
`phase0-complete`·`phase1-d1-pass` 로컬 존재하나 **원격 없음**, 로컬 main이 origin/main보다 **3 커밋 앞섬**(미푸시: D1정정/Phase0소급/Phase1완료).
조치: `git push origin main && git push origin --tags`.

### 1-8. 경미 (MIN) — 선택
- `STRATEGY_11:52, 423` benchmark_results "5개" → 실측 4.
- 로드맵 리스크 "15건"(intro/0-6/0-V) vs 레지스터 R01~R16(16건): Phase0 시점 15 / Phase4~6 R16 추가 — "15(+R16 후속)" 표기 권장.

---

## TIER 2 — 이미 프로젝트 자체 레지스트리에 등록·정본확정된 stale-text (신규 아님 → 기존 항목 실행)
> GP-B가 "MISMATCH"로 검출했으나, 재독 결과 **우선순위로 이미 정본 확정 + 프로젝트가 이미 추적 중**. 텍스트 정리만 남음.

| 개념 | 등록 ID | 정본(확정값) | 잔존 stale 위치(대표) |
|---|---|---|---|
| 비용상한 수치 통일 | **V1-013**(₩40,000 통일 ☐) · V0-001 · V3-003 | V1=₩40K/V2=₩93K/V3=₩266K (RULE 1.3 §5, LOCK-BM/CD, **ABSOLUTE LOCK**) | `STEP7_보강_통합명세서:120`(I-9 ₩10,000)·`:525`(V2 ₩40,000) |
| QoD 4요소→5요소 | **V1-006**(☐, fix파일 명시) | PLAN-3.0 5요소(Acc.30/Rel.25/Comp.20/Safe.15/Eff.10) | `CLAUDE.md:269`·`MASTER_SPEC:1542`·`BASE-1.3:503,543`·`D2.0-06` |
| L0/Session TTL | **CONFLICT_LOG #006**(AUTHORITY 6-4 자체표기) | LOCK-MR-003 `session_end or created_at+30일 중 먼저` | `BASE-1.3:183,258`·`D2.0-06:121,268`·`PLAN-3.0:1279,2666` |
| 메모리 4계층 vs 5계층 | (REVIEW:35,744 "4계층 확정") | 정본 4계층 L0~L3 (L4 Archive=V2+ 참조용, `STEP7_J-M:451` 정리) | STEP7-C/D/E/H/J 5-Layer 표현·`D2.0-07:545`/`STEP7-E:293` L0~L4 |
| memory_search 4 vs 5 | (= 위 메모리 계층 드리프트의 발현) | 4계층(L0~L3) | `D2.0-03 BLUE_NODES:262`(4) vs `STEP7-K:29`(5) |
| BGE-M3 V1 기본 차원 | (LOCK-AX-07) | `1024-dim / Matryoshka 256-dim`, 자동선택 <5,000→1024 | `D2.0-06:772,845`("V1기본 256") vs `:1331`("V1기본 1024") — D2.0-06 내부 자기모순 |

> **비이슈(과대검출)**: GP-B #3 V3, #4 Python(3.11+ 전역 vs 3.12 AI-Investing 도메인고정, 3.12⊇3.11+), #7 QoD 0.7(상보적 임계구간), #8 승인 타임아웃(BASE-1.3 우선순위 vs D2.0-07 승인게이트 = 다른 게이트) → 재독 결과 **충돌 아님**, 수정 불필요.

---

## TIER 3 — 설계 명세 실결함 백로그 (구현 전 정정 권고 · R16: "완전" 단정 불가)
양측 AI 독립 확인 **343건**(source-confirmed) + GPT 단독 **130건**. 대표: SQLi(6-4), assert `-O` 테넌트우회(6-4), CanaryJudge p≥0.05 승급(4-4), webhook auth none(3-4), PAUSED 상태머신 위반(3-4), RPO/cron 모순(6-13), 거버넌스 R1~R11 범위(0-0), trailing-stop/HMM(Ai-investing). 전체 `crossAI_diff.json`.
> **수렴 불가 선언**: 이 레이어는 설계 판단(C)이라 검토를 더 할수록 후보가 늘 수 있음 → "더 이상 없음" 단정 금지(R16). Phase 0·1의 *문서 정합*과 별개의 *구현 품질* 백로그.

---

## 수렴 판정
- **TIER 1·2 (객관 문서 드리프트)**: 전수 grep으로 **모든 occurrence 열거 완료** → 이 목록은 **더 늘지 않는다**(수렴). 처리하면 Phase 0·1 문서 정합 = 완결.
- **TIER 3 (설계 결함)**: 본질적으로 비수렴 → 별도 트랙(구현 전), "완벽" 표기 불가.
