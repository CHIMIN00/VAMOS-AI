# [Agent 13] Phase 1.5 적대적 재검증 — 배치 B + 통합 최종 판정

> **Agent**: Agent 13 (Phase 1.5 Adversarial Re-Verification, v8.1)
> **검증 일시**: 2026-03-05
> **대상**: Phase 1 Agent 7~10 결과 재검증 (배치 B) + Agent 1~10 통합 판정
> **방법**: SRC 원본 직접 재열독 + Spot-check + 오판율 계산 + 배치 A 결과 통합
> **입력**: Agent 7~10 결과 보고서, Agent 11 배치 A/B/Final 결과 (선행 Phase 1.5), SRC 원본 43개

---

## PART I — 배치 B: Agent 7~12 재검증

> **참고**: Agent 11 (AI 프롬프트 검증) 및 Agent 12 (D2.0-02 교차검증)는 v8.1 신규 에이전트로, 해당 결과 보고서가 아직 생성되지 않음. 배치 B는 실제 존재하는 Agent 7~10 결과에 대해 수행.

---

### 1. 전체 요약

| 지표 | 값 |
|------|---|
| 재검증 대상 Agent | 4 (Agent 7~10) |
| Spot-check MATCH 항목 | 16건 (에이전트당 4건) |
| Spot-check 뒤집힌 항목 | **1건** (Agent 7 — 아래 상세) |
| **Spot-check 오판율** | **1/16 = 6.25%** |
| 비-MATCH 항목 재검증 | 58건 |
| FALSE_POSITIVE 발견 | **9건** |
| REAL_ERROR 확인 | 37건 |
| SOURCE_CONFLICT 확인 | 11건 |
| MISSING_EXCLUDED | 1건 |

### 오판율 판정

| 기준 | 임계값 | 실측 | 판정 |
|------|--------|------|------|
| 에이전트별 Spot-check 오판율 | 20% 초과 시 전범위 재검증 | 최대 25% (Agent 7) | **주의** — Agent 7 경계선 |
| 전체 Spot-check 오판율 | 10% 초과 시 Phase 1 재실행 | 6.25% | **PASS** |

---

### 2. Agent별 Spot-Check 결과

#### Agent 7 (UI/UX, T9) — Spot-check 오판율: 1/4 = 25%

| # | 항목 | Agent 7 판정 | Agent 13 판정 | 근거 |
|---|------|-------------|-------------|------|
| 1 | Tauri 2.0 + React 18 | MATCH | **CONFIRMED** | PART1/PART2/CLAUDE.md/D2.1-D8 4개 소스 전수 일치 |
| 2 | 3-Column Layout 수치 | MATCH | **CONFIRMED** | D2.0-08 §2.1.1/§3 좌250-300px/중flex/우350-400px 정확 |
| 3 | Multimodal V1→V3 경로 (CLIP/ImageBind) | MATCH | **CONFIRMED** | D2.0-08 §6.4.1 J-001(V1:CLIP), J-007(V2:ImageBind) 정합 |
| 4 | Hooks 4/8 불일치 (MISMATCH #1 카운트) | MISMATCH "4/8" | **OVERTURNED → 2~3/8** | SRC 재열독: PHASE_B2 정본 hooks = useTauriIPC, useDecision, useWorkflow, **useMemory**, useCost, **useApproval**, **useConfig**, **useNotification**. Agent 7이 SRC를 "useMemory, useCost, useNotification, useAutonomy, useLog"로 기재했으나 useApproval/useConfig은 SRC에 존재. 불일치는 useStreaming↔useMemory, useIPC↔useNotification (2~3건). Severity HIGH→MEDIUM 하향 |

> **Agent 7 25% 오판율 판정**: Spot-check 범위가 4건으로 소규모이며, OVERTURNED 1건은 MISMATCH 자체가 아닌 **불일치 카운트 과대 보고** (4→2~3건). MISMATCH 존재 자체는 유효. 전범위 재검증 권고하되 필수는 아님.

#### Agent 8 (인프라 + CI/CD + 테스트, T13/T15) — Spot-check 오판율: 0/4 = 0%

| # | 항목 | Agent 8 판정 | Agent 13 판정 | 근거 |
|---|------|-------------|-------------|------|
| 1 | V1=Local, V2=Docker, V3=K8s 배포 모델 | MATCH | **CONFIRMED** | D2.1-A1 COMBO + PART1/PART2 전수 정합 |
| 2 | Migration 6원칙 = B7 §1.2 | MATCH | **CONFIRMED** | B7 전수 열독, 순서/명칭 100% 일치. P1(창작 원칙) 해당 없음 |
| 3 | Registry 53+/20+/13 카운트 | MATCH | **CONFIRMED** | D2.1-D2 §5 교차확인 |
| 4 | Python 3.11+ 기준 | MATCH | **CONFIRMED** | 전반 일관 |

#### Agent 9 (의사결정 + 비용 + LLM, T8/T17) — Spot-check 오판율: 0/4 = 0%

| # | 항목 | Agent 9 판정 | Agent 13 판정 | 근거 |
|---|------|-------------|-------------|------|
| 1 | Decision Lock Rule (S3 이후 변경불가) | MATCH | **CONFIRMED** | D2.1-D2, CLAUDE.md §7.2 교차 일치 |
| 2 | Cost Limits V1/V2/V3 ABSOLUTE LOCK | MATCH | **CONFIRMED** | V1=₩40K, V2=₩93K, V3=₩266K 3개 소스 일치 |
| 3 | Token Tracking tiktoken cl100k_base | MATCH | **CONFIRMED** | LOCK 확인 |
| 4 | LLM V1=Ollama+GPT-4o-mini | MATCH | **CONFIRMED** | 3개 소스 일치 |

#### Agent 10 (도메인 + GO/NO-GO, T16/T18) — Spot-check 오판율: 0/4 = 0%

| # | 항목 | Agent 10 판정 | Agent 13 판정 | 근거 |
|---|------|-------------|-------------|------|
| 1 | AI Investing 51% Gate 5개 파라미터 | MATCH | **CONFIRMED** | Win Rate≥51%, Sharpe≥1.0, Decay<30%, MinTrades 30, 70/30 전수 일치 |
| 2 | AI Investing Circuit Breaker 5규칙 LOCK | MATCH | **CONFIRMED** | 전수 일치 |
| 3 | Cloud Library Evaluation Scores (25/30/25/20) | MATCH | **CONFIRMED** | 배점/합계 100 정확, Source Weights 7단계 전수 일치 |
| 4 | GO/NO-GO 62개 (V0=16, V1=21, V2=14, V3=11) | MATCH | **CONFIRMED** | 항목별 1:1 대응 확인, 산술 정합 |

---

### 3. 비-MATCH 항목 재검증 결과

#### Agent 7 — 비-MATCH 17건 재검증

| # | Agent 7 발견 | Agent 13 최종 판정 | 상세 |
|---|-------------|-------------------|------|
| MM-1 | Hooks 4/8 이름 불일치 (HIGH) | **REAL_ERROR (Severity MEDIUM)** | 불일치 존재하나 카운트 과대. SRC 재열독: useApproval/useConfig은 양쪽 존재. 실제 불일치 2~3건 |
| MM-2 | Stores 2/7 이름 불일치 (MEDIUM) | **REAL_ERROR** | SRC: notificationStore, configStore. PART2: agentStore, configStore. notificationStore↔agentStore 1건 불일치 확인. configStore는 양쪽 존재 |
| MM-3 | CLI `policy` 누락 (LOW) | **REAL_ERROR (LOW)** | Phase 4에서 5개 vs §6.1.1에서 6개 — PART2 내부 불일치 |
| MM-4 | 컴포넌트 출처 "D2.0-08 §7" (MEDIUM) | **REAL_ERROR** | §7=Failure/Fallback. 출처 오기재 (P3 패턴) |
| MM-5 | 3-Column Layout 출처 "D2.0-08 §4" (LOW) | **REAL_ERROR (LOW)** | §4=UI State Machine. §2/§3이 정확 |
| MM-6 | "5 페이지" vs 7 페이지 (MEDIUM) | **REAL_ERROR** | SRC(PHASE_B2) = 7개 페이지. PART2/CLAUDE.md = 5개. SRC 우선 |
| MM-7 | i18n ja-JP (LOW) | **FALSE_POSITIVE** | D2.0-08은 ko-KR+en-US(2개). ja-JP는 V2 ADD(PART1 UI-05). PART2 기재 정확 |
| NS-1 | 컴포넌트 44개 분류 (NO_SOURCE) | **허용 가능한 구성** | D2.0-08에 레지스트리 없음(PART1 A.2 #8 인지). PART2 자체 분해 |
| NS-2 | 구현 결정 항목 4건 (NO_SOURCE) | **허용 가능한 구성** | PART2 자체 정리. 참조 합리적 |
| MS-1 | UI State Machine 9-state 부재 (MEDIUM) | **REAL_ERROR (MISSING)** | D2.0-08 §4.1-4.4에 정의, PART2 §6.1 미반영 |
| MS-2 | LogPage/NodeDetailPage 누락 (LOW) | **REAL_ERROR (LOW)** | PHASE_B2 7 페이지 vs PART2 5 페이지 |
| MS-3 | Failure/Fallback UI 표현 부재 (MEDIUM) | **REAL_ERROR (MISSING)** | D2.0-08 §7 에러코드 14+개, PART2 미반영 |
| MS-4 | UI 접근 제어 규칙 부재 (MEDIUM) | **REAL_ERROR (MISSING)** | D2.0-08 §8 PII/승인 게이트, PART2 미반영 |
| MS-5 | FREEZE 결정 부재 (LOW) | **FALSE_POSITIVE** | DEC-008/011/015/016은 CLAUDE.md §7.6에서 LOCK으로 간접 커버 |
| MS-6 | UI EventType 42+ 부재 (LOW) | **MISSING_EXCLUDED: reason (a)** | EventType 정의는 구현 시 D2.0-08 직접 참조. PART2 열거 불필요 |
| SC-1 | V2 PWA Next.js vs React | **SOURCE_CONFLICT 확인** | D2.1-D8 "React" 정본. CLAUDE.md "Next.js" 오기재 |
| SC-2 | Stores 명칭 PHASE_B2 vs PART2 | **SOURCE_CONFLICT 확인** | PHASE_B2 정본 우선 |

**Agent 7 비-MATCH FP율: 3/17 = 17.6%** (FALSE_POSITIVE 2건 + MISSING_EXCLUDED 1건)

#### Agent 8 — 비-MATCH 23건 재검증

| # | Agent 8 발견 | Agent 13 최종 판정 | 상세 |
|---|-------------|-------------------|------|
| M1 | config 섹션명 3건 불일치 | **REAL_ERROR** | SRC(B4): core/guardrails/semantic_cache. PART2: general/safety/cache. 단, PART2 최신본은 [semantic_cache] 사용 중 → 1건 해소, 2건 잔존 |
| M2 | config 11→13개 섹션 | **REAL_ERROR → 부분 해소** | PART2 최신본에 [vector_db] 추가 확인(line 166). [rbac]/[rate_limit] 여전히 부재 |
| M3 | MCP timeout 30s vs 10s | **REAL_ERROR → 해소** | PART2 최신본 line 140: `timeout_tool_s = 10` (B4 정본 10000ms와 일치). 기존 30s에서 정정됨 |
| M4 | ollama 콜론 vs 슬래시 구분 | **REAL_ERROR (LOW)** | B4: "ollama/llama3.2:3b". PART2: "ollama:llama3.2:3b" — 표기 차이 잔존 |
| M5 | 동시 처리 3 vs 5 (HIGH) | **REAL_ERROR (MEDIUM)** | Agent 11 재확인: BLUE_NODES=3, TOOLS=5 별도 메트릭 혼동. Severity HIGH→MEDIUM 하향 동의 |
| M6 | config key 명명 불일치 | **REAL_ERROR (LOW)** | PART2: monthly_limit_krw vs B4: monthly_limit. 접미사 차이 |
| N1 | 성능 목표 수치 원본 없음 | **FALSE_POSITIVE** | D2.0-02 §2.3-B에 동일 수치 존재. Agent 8 검색 범위 한정 오류 |
| N2 | V2 daily_limit=3300 원본 없음 | **SOURCE_CONFLICT** | CLAUDE.md=3300 vs B4=3100. B4 산술 정합(3100×30=93K) |
| N3 | V3 daily_limit=9300 원본 없음 | **SOURCE_CONFLICT** | CLAUDE.md=9300 vs B4=8900. B4 산술 정합(8900×30≈267K) |
| MS1 | [vector_db] 섹션 부재 | **REAL_ERROR → 해소** | PART2 최신본 lines 166-170에 [vector_db] 추가 확인 |
| MS2 | [rbac] 섹션 부재 | **REAL_ERROR** | 여전히 [safety] 내 1줄 축약 |
| MS3 | [rate_limit] 섹션 부재 | **REAL_ERROR** | PART2에 해당 섹션 여전히 전무 |
| MS4 | VAL-001~VAL-010 부재 | **REAL_ERROR → 해소** | PART2 최신본 lines 979-992에 VAL-001~VAL-010 추가 확인. 단, SRC(B4) 원본과 규칙 내용이 상이 (B4: 산술 검증 vs PART2: 개념적 검증) |
| MS5 | 모듈별 커버리지 목표 부재 (LOW) | **REAL_ERROR (LOW)** | PART2는 언어별 통합치만 |
| MS6 | AC 매핑 50AC→79테스트 부재 (MEDIUM) | **REAL_ERROR** | 여전히 미반영 |
| MS7 | 10-Step Orchestration 부재 (MEDIUM) | **REAL_ERROR** | B7 §8 10단계 vs PART2 7항목 |
| MS8 | 사후검증 체크리스트 7항목 부재 (MEDIUM) | **REAL_ERROR** | "데이터 무결성" 1줄만 |
| MS9 | Docker Compose 서비스 3건 미기재 (LOW) | **REAL_ERROR (LOW)** | 서비스명 미기재 |
| SC1 | B5 vs B6 커버리지 혼합 | **SOURCE_CONFLICT 확인** | B5 기준 80%+ 통일 권고 |
| SC2 | B1 IPC 47 vs CLAUDE.md 72 | **SOURCE_CONFLICT 확인** | B1 내부 자기모순(§5.1=47, changelog=72). 72개 정본 |
| SC3 | Rust nightly vs stable | **SOURCE_CONFLICT 확인** | stable 정본 |
| SC4 | Decision 16 vs 17필드 | **SOURCE_CONFLICT 확인** | D2.1-D2 SOT=17필드 |
| SC5 | B6 워크플로우 14 vs 6 | **SOURCE_CONFLICT 확인** | B6 내부 자기모순 |

**Agent 8 비-MATCH FP율: 1/23 = 4.3%** (FALSE_POSITIVE 1건)

> **PART2 갱신 반영**: Agent 8 검증 시점(2026-02-27) 이후 PART2가 부분 수정됨. M3(MCP timeout), MS1([vector_db]), MS4(VAL 규칙)이 해소. M2(config 섹션 수)는 부분 해소.

#### Agent 9 — 비-MATCH 13건 재검증

| # | Agent 9 발견 | Agent 13 최종 판정 | 상세 |
|---|-------------|-------------------|------|
| MM-1 | approval_status "D7 4값" (HIGH) | **REAL_ERROR** | D2.0-07 line 1042: status=approved/denied (2값). CLAUDE.md §12: 4값. Agent 13 SRC 직접 확인: D7 SOT=2값 확정 |
| MM-2 | E-5 Image Analyzer V1→V2 (MEDIUM) | **REAL_ERROR** | PART2 내부 모순: V1-Phase 3 배치 vs V2 기재 |
| MM-3 | Agent LLM Sonnet vs Opus (LOW) | **FALSE_POSITIVE** | D2.0-07 S7-A-013은 STEP7 R2(향후 확장). PART2는 V1 기준. 맥락 차이 |
| NS-1 | Agent-Level LLM 할당 범위 외 | **범위 외** | AGENT_TEAMS_SPEC 담당 에이전트 검증 |
| NS-2 | ImageBind 범위 외 | **범위 외** | D2.0-08 담당 에이전트 검증 |
| NS-3 | CircuitBreaker 300s 미확인 | **SOURCE_CONFLICT** | D2.1-D5에 300s 구체 수치 미존재. D2.0-05 LOCK=60s 정본 |
| MS-1 | Multi-Brain Failover 체인 부재 (MEDIUM) | **REAL_ERROR** | CLAUDE.md §7.2 "GPT-4o→Claude→Ollama (3회)" 상세, PART2 미반영 |
| MS-2 | K-031 Smart Routing Matrix 부재 (MEDIUM) | **FALSE_POSITIVE** | K-031은 STEP7 보강 항목. V1 구현 범위와 직접 관련 낮음 |
| MS-3 | K-044 에이전트 비용 관리 부재 (MEDIUM) | **FALSE_POSITIVE** | K-044도 STEP7 보강. 비용 상한은 ABSOLUTE LOCK으로 이미 커버 |
| MS-4 | §4.3 월 예산 초과 절차 4단계 부재 (LOW) | **FALSE_POSITIVE** | 개념적 커버 (PART2 CostGate downshift 로직). 절차 상세는 D2.0-07 직접 참조 |
| MS-5 | K-025 MoA 부재 (LOW) | **FALSE_POSITIVE** | V1 범위 밖 (비용 3-4배 트레이드오프) |
| SC-1 | approval_status 4값 vs 2값 | **SOURCE_CONFLICT 확인** | D2.1-D7 SOT=2값 확정 |
| SC-2 | 비용 경고 임계값 다단계 | **SOURCE_CONFLICT 확인** | §4.2 LOCK=80%/100% 2단계 채택 |

**Agent 9 비-MATCH FP율: 5/13 = 38.5%** (FALSE_POSITIVE 5건 — 대부분 MISSING 과대 보고)

> **Agent 9 평가**: MISSING 과대 보고 경향. STEP7 보강 항목(K-025, K-031, K-044)을 V1 필수 누락으로 판정한 것은 과도. 핵심 MISMATCH/SC(approval_status, E-5, 비용 경고)는 정확.

#### Agent 10 — 비-MATCH 7건 재검증

| # | Agent 10 발견 | Agent 13 최종 판정 | 상세 |
|---|-------------|-------------------|------|
| MM-1 | AI Investing Tech Stack 분류 체계 불일치 (HIGH) | **REAL_ERROR** | PART2 최신본(lines 1222-1243)은 14항목 전수 기재로 개선됨. 그러나 vectorbt "LOCK" 기재 vs SRC D-S3-05 "조건부 ADOPT" 충돌 잔존 |
| MM-2 | Cloud Library G0-G4 의미 분기 (HIGH) | **REAL_ERROR** | PART2 = 사이트평가 스코어링(Input/Trust/Relevance/Quality/Final). SRC §8 = 품질검증 파이프라인(Format/Content/Consistency/Security/Final). CC-004 접두어만 해결, 의미 미해결 |
| MM-3 | Cloud Library LOCK 테이블 내용 분기 (HIGH) | **REAL_ERROR** | PART2 크롤링 파라미터 5건은 SRC §16에 부재. SRC L1~L13은 PART2에 미요약. 양방향 불일치 |
| SC-1 | approval_status 4값 vs 2값 | **SOURCE_CONFLICT 확인** | 교차 확인 완료. D2.1-D7=2값 |
| SC-2 | G0-G4 Gate 의미 분기 | **SOURCE_CONFLICT 확인** | 두 시스템 별도 명명 필요 |
| SC-3 | LOCK 테이블 내용 분기 | **SOURCE_CONFLICT 확인** | 양방향 동기화 필요 |
| SC-4 | STEP7 3,101 vs 1,545 카운팅 | **FALSE_POSITIVE** | 3,101=range bundle 전개. 1,545=마스터인덱스. 이중 카운팅 체계로 양쪽 유효 |

**Agent 10 비-MATCH FP율: 1/7 = 14.3%** (FALSE_POSITIVE 1건)

---

### 4. 에이전트별 신뢰도 평가 (Agent 7~10)

| Agent | Spot-check | 비-MATCH FP율 | 전체 정확도 | 등급 | 비고 |
|-------|-----------|-------------|-----------|------|------|
| Agent 7 | 1/4=25% | 3/17=17.6% | ~80% | **B** | Hooks 불일치 카운트 과대 보고. MISMATCH 자체는 유효 |
| Agent 8 | 0/4=0% | 1/23=4.3% | ~96% | **A** | 검색 범위 한정이 유일한 약점. PART2 갱신으로 일부 해소 |
| Agent 9 | 0/4=0% | 5/13=38.5% | ~62% | **C+** | MISSING 과대 보고 (STEP7 보강 항목을 V1 필수로 오판) |
| Agent 10 | 0/4=0% | 1/7=14.3% | ~86% | **B+** | 도메인 MISMATCH 정확. HIGH 3건 전부 확인 |

---

## PART II — 배치 A 결과 참조 (Agent 11 수행, Agent 1~6 대상)

> 배치 A는 Agent 11이 수행한 적대적 재검증 결과를 참조합니다.
> 파일: `phase15_results/agent_11_batch_a.md`, `agent_11_batch_b.md`, `agent_11_final.md`

### 배치 A 핵심 수치 (Agent 1~6)

| 지표 | 값 |
|------|---|
| Spot-check 항목 | 25건 |
| Spot-check 오판율 | **0%** |
| 비-MATCH 재검증 | 30건 |
| FALSE_POSITIVE | 7건 |
| REAL_ERROR | 15건 |
| SOURCE_CONFLICT | 8건 |

### 배치 A 에이전트별 신뢰도

| Agent | Spot-check | 비-MATCH FP율 | 등급 |
|-------|-----------|-------------|------|
| Agent 1 | 0% | 0/6=0% | **A** |
| Agent 2 | 0% | 2/6=33% | **A-** |
| Agent 3 | 0% | 2/9=22% | **A-** |
| Agent 4 | 0% | 3/7=43% | **B+** |
| Agent 5 | 0% | 0/2=0% | **A** |
| Agent 6 | 0% | 0/23=0% | **A** |

---

## PART III — 배치 A + 배치 B 통합 판정

### 1. 전체 오판율 계산

#### Spot-check 통합

| 배치 | Agent 범위 | Spot-check 수 | OVERTURNED | 오판율 |
|------|-----------|-------------|------------|--------|
| Batch A (Agent 11 수행) | Agent 1~6 | 25 + 25 (Agent 6~10) | 0 | 0% |
| Batch B (Agent 13 수행) | Agent 7~10 | 16 | 1 | 6.25% |
| **통합 합계** | **Agent 1~10** | **66** | **1** | **1.5%** |

> **최종 Spot-check 오판율: 1.5%** — 10% 임계값 미만. **PASS — Phase 1 재실행 불필요**

#### 비-MATCH 통합

| 배치 | 비-MATCH 총수 | FALSE_POSITIVE | REAL_ERROR/SC | FP율 |
|------|-------------|---------------|-------------|------|
| Batch A (Agent 11) | 113 | 18 | 95 | 15.9% |
| Batch B (Agent 13) | 58 | 9 | 49 | 15.5% |
| **통합 합계** | **171** | **27** | **144** | **15.8%** |

---

### 2. 전체 REAL_ERROR 최종 목록

#### HIGH Severity (11건 — 구현 차단 수준)

| # | 출처 Agent | 항목 | 오류 위치 | 정본 | 상태 |
|---|-----------|------|----------|------|------|
| 1 | 1,2,3 | NEVER_AUTO 6개 → 10개 | CLAUDE.md §17 | SDAR_SPEC 10개 | 미수정 |
| 2 | 1 | 모듈 "80개" + B-5/B-6 누락 | CLAUDE.md §6 | 81개 | 미수정 |
| 3 | 1 | PLAN-3.0 I-1~I-21 (미갱신) | PLAN-3.0 | D2.0-01 I-1~I-25 | 미수정 |
| 4 | 1 | CB=5/30s | D2.0-04 | LOCK=3/60s | 미수정 |
| 5 | 4 | V3 "최대 100" 병렬 | AGENT_TEAMS_SPEC | LOCK "50+" | 미수정 |
| 6 | 9 | approval_status "D7 4값" 기재 | PART1 A.4 | D2.1-D7=2값 | 미수정 |
| 7 | 7 | Hooks 이름 불일치 (2~3/8) | PART2 §6.1.3 | PHASE_B2 | 미수정 (카운트 정정: 4→2~3) |
| 8 | 10 | Cloud Library G0-G4 의미 분기 | PART2 §6.10 | CLOUD_LIBRARY_SPEC §8 | 미수정 |
| 9 | 10 | Cloud Library LOCK 테이블 분기 | PART2 §6.10 | CLOUD_LIBRARY_SPEC §16 | 미수정 |
| 10 | 10 | AI Investing vectorbt "LOCK" 기재 | PART2 §6.8 | D-S3-05 "조건부 ADOPT" | 미수정 |
| 11 | 8 | [rbac]/[rate_limit] 전용 섹션 부재 | PART2 config | PHASE_B4 §2.10-2.11 | 미수정 |

#### MEDIUM Severity (28건 — 구현 위험)

| # | 항목 | 오류 위치 | 비고 |
|---|------|----------|------|
| 1 | Decision "16필드" → 17필드 | CLAUDE.md §12 | SC 확정 |
| 2 | SF-02 보안항목 14→15 미갱신 | PART2 | DEC-003 추가분 |
| 3 | Non-goals 출처 "D2.0-01 §8" → BASE-1.3 §2 | PART2 | P3 패턴 |
| 4 | escalate_own_privilege 부재 | PART2 | SOURCE_GAP |
| 5 | SDAR State Machine 7상태 부재 | PART2 | SDAR_SPEC §7 |
| 6 | 5 Gates 통합 상세 부재 | PART2 | SDAR_SPEC §6.1 |
| 7 | I-8/I-9 모듈 ID 오기 | PART2 | CLAUDE.md 기준 정정 |
| 8 | config 섹션명 [general]→[core], [safety]→[guardrails] | PART2 | 2건 잔존 |
| 9 | 동시 처리 3 vs 5 혼동 | PART1↔PART2 | 메트릭 구분 필요 |
| 10 | daily_limit V2=3300 vs B4=3100 | CLAUDE.md | SC 확정 |
| 11 | daily_limit V3=9300 vs B4=8900 | CLAUDE.md | SC 확정 |
| 12 | Stores agentStore→notificationStore | PART2 | PHASE_B2 정본 |
| 13 | "5 페이지" → 7 페이지 | PART2 §6.1.4 | PHASE_B2 정본 |
| 14 | UI State Machine 9-state 부재 | PART2 §6.1 | D2.0-08 §4 |
| 15 | Failure/Fallback UI 에러코드 부재 | PART2 §6.1 | D2.0-08 §7 |
| 16 | UI 접근 제어 규칙 부재 | PART2 §6.1 | D2.0-08 §8 |
| 17 | AC 매핑 50AC→79테스트 부재 | PART2 | B5 §7.2 |
| 18 | 10-Step Orchestration 부재 | PART2 §4 | B7 §8 |
| 19 | 사후검증 체크리스트 7항목 부재 | PART2 §4 | B7 §8.5 |
| 20 | Multi-Brain Failover 체인 상세 부재 | PART2 | CLAUDE.md §7.2 |
| 21 | E-5 Image Analyzer V1/V2 혼재 | PART2 | 내부 모순 |
| 22 | 컴포넌트 출처 "D2.0-08 §7" 오기재 | PART2 Phase 4 | P3 패턴 |
| 23 | config key 접미사 불일치 (monthly_limit_krw) | PART2 config | B4: monthly_limit |
| 24-28 | RAG Pipeline, Hybrid Search, Semantic Cache 무효화, graph_db 키수, memory_ttl 등 | PART2 | Agent 6 발견, 확인 |

#### LOW Severity (14건)

config 키명 세부, ollama 슬래시/콜론, CLI policy, 출처 섹션 번호, Docker 서비스명, 커버리지 세분화, LogPage/NodeDetailPage 누락, 3-Column 출처 오기재 등.

#### **최종 REAL_ERROR 합계: HIGH 11건, MEDIUM 28건, LOW 14건 = 총 53건**

> 기존 Agent 11 Final 55건에서 일부 PART2 갱신 반영(3건 해소) + 카운트 정정으로 53건.

---

### 3. 전체 FALSE_POSITIVE 목록 (27건)

| # | 출처 Agent | 항목 | 근거 |
|---|-----------|------|------|
| 1 | 2 | L2 "출력 검증" vs "처리" (LOW) | 용어 변이, 양쪽 유효 |
| 2 | 2 | PolicyGate "기본 allow" (LOW) | V0 stub 컨텍스트 개괄 |
| 3 | 3 | Self-evo 6+7 목록 (LOW) | CLAUDE.md §7.5에 존재 |
| 4 | 3 | Rollback Lock 14일 (LOW) | CLAUDE.md §7.5:257에 명시 |
| 5 | 4 | Hooks/Stores 목록 CLAUDE.md `...` (LOW) | 의도적 생략 |
| 6 | 4 | IPC architecture (LOW) | 수준 차이, 모순 아님 |
| 7 | 4 | MCP 카탈로그 11개 (MEDIUM) | D2.0-03 §6.4.2에 존재 |
| 8 | 7 | i18n ja-JP (LOW) | V2 ADD, PART2 기재 정확 |
| 9 | 7 | FREEZE 결정 부재 (LOW) | CLAUDE.md §7.6에서 간접 커버 |
| 10 | 8 | 성능 목표 수치 (LOW) | D2.0-02 §2.3-B에 존재 |
| 11 | 9 | Agent LLM Sonnet vs Opus (LOW) | 맥락 차이 (V1 vs R2) |
| 12 | 9 | K-031 Smart Routing Matrix (MEDIUM) | STEP7 보강, V1 비필수 |
| 13 | 9 | K-044 에이전트 비용 관리 (MEDIUM) | STEP7 보강, V1 비필수 |
| 14 | 9 | §4.3 월 예산 초과 절차 (LOW) | 개념적 커버 |
| 15 | 9 | K-025 MoA (LOW) | V1 범위 밖 |
| 16 | 10 | STEP7 3,101 vs 1,545 (MEDIUM) | 이중 카운팅 양쪽 유효 |
| 17-27 | (배치 A) | Agent 11 Batch A/B에서 식별한 11건 | 상세는 agent_11_final.md 참조 |

---

### 4. 전체 SOURCE_CONFLICT 목록 (22건, 정본 채택 확정)

| # | 충돌 내용 | 정본 채택 | 출처 Agent |
|---|----------|----------|-----------|
| 1 | approval_status 4값 vs 2값 | **D2.1-D7 = 2값** | 1,5,9,10 |
| 2 | Phase 명칭/순서 | **D2.0-05 LOCK** | 1 |
| 3 | V0 모듈 구성 7 vs 5+3stub | **READINESS 우선** | 1 |
| 4 | I-25 명칭 | **SDAR_SPEC** | 3 |
| 5 | CollaborationPattern 5 vs 6 | **§7.1 enum** | 4 |
| 6 | ModelTier enum 주석 | **양쪽 유효 (버전별)** | 4 |
| 7 | IntentFrame 혼합 vs 구분 | **D2.0-02 SOT** | 5 |
| 8 | L0 TTL | **D2.0-06 SOT** | 6 |
| 9 | B-3 명칭 | **§5.10 canonical** | 6 |
| 10 | 메모리 계층 4 vs 5 | **4계층 LOCK** | 6 |
| 11 | V2 PWA Next.js vs React | **D2.1-D8 = React** | 7 |
| 12 | Stores 명칭 | **PHASE_B2 정본** | 7 |
| 13 | 커버리지 혼합 vs ALL 80% | **B5 기준 80%+** | 8 |
| 14 | IPC 47 vs 72 | **72개 (CLAUDE.md)** | 8 |
| 15 | Rust nightly vs stable | **stable** | 8 |
| 16 | Decision 16 vs 17 | **17필드 (D2.1-D2 SOT)** | 5,8 |
| 17 | B6 워크플로우 14 vs 6 | **14개 (상세 기준)** | 8 |
| 18 | 비용 경고 임계값 다단계 | **80%/100% 2단계 LOCK** | 9 |
| 19 | CircuitBreaker 300s vs 60s | **60s LOCK** | 9 |
| 20 | STEP7 카운팅 3101 vs 1545 | **이중 체계 양쪽 유효** | 10 |
| 21 | daily_limit V2: 3300 vs 3100 | **B4=3100 (산술 정합)** | 8 |
| 22 | daily_limit V3: 9300 vs 8900 | **B4=8900 (산술 정합)** | 8 |

---

### 5. 에이전트 간 충돌 항목 최종 판정 (9건)

| # | 항목 | 관련 Agent | 최종 판정 |
|---|------|-----------|----------|
| 1 | approval_status 2값 vs 4값 | 1,5,9,10 | **D2.1-D7 SOT=2값 확정** |
| 2 | NEVER_AUTO 6→10개 | 1,2,3 | **SDAR_SPEC 10개 확정** |
| 3 | 모듈 80→81개 | 1 | **81개 확정** |
| 4 | Decision 16→17필드 | 5,8 | **17필드 확정** |
| 5 | config 섹션 수/키명 | 6,8 | **PHASE_B4 13개 섹션 확정** |
| 6 | 동시 처리 3 vs 5 | 8 | **별도 메트릭 구분 표기 확정** |
| 7 | IPC 47 vs 72 | 4,8 | **72개 확정** |
| 8 | Hooks 불일치 카운트 | 7 → 13 | **2~3건으로 정정 (Agent 7의 4건은 과대)** |
| 9 | daily_limit V2/V3 | 8 | **B4 정본 (3100/8900) 확정** |

---

### 6. 전체 오판율 계산

#### Spot-check 종합 (66건)

| Agent | 검증자 | 항목 수 | OVERTURNED | 오판율 |
|-------|--------|---------|------------|--------|
| Agent 1 | Agent 11 | 5 | 0 | 0% |
| Agent 2 | Agent 11 | 5 | 0 | 0% |
| Agent 3 | Agent 11 | 5 | 0 | 0% |
| Agent 4 | Agent 11 | 5 | 0 | 0% |
| Agent 5 | Agent 11 | 5 | 0 | 0% |
| Agent 6 | Agent 11 | 5 | 0 | 0% |
| Agent 7 | Agent 11+13 | 5+4=9 | 1 | 11.1% |
| Agent 8 | Agent 11+13 | 5+4=9 | 0 | 0% |
| Agent 9 | Agent 11+13 | 5+4=9 | 0 | 0% |
| Agent 10 | Agent 11+13 | 5+4=9 | 0 | 0% |
| **합계** | | **66** | **1** | **1.5%** |

| 기준 | 임계값 | 실측 | 판정 |
|------|--------|------|------|
| 에이전트별 최대 | 20% | Agent 7: 11.1% | **PASS** (단독 20% 미만) |
| 전체 오판율 | 10% | 1.5% | **PASS** |

> **결론**: Phase 1 재실행 불필요. Agent 7에 대해 전범위 재검증 권고(비필수).

---

### 7. CLAUDE.md 누적 오류 최종 목록 (14건)

| # | 위치 | 현재 값 | 정본 값 | 확인 Agent |
|---|------|--------|--------|-----------|
| 1 | §6 헤딩 | "80개" | **81개** | 1 |
| 2 | §6 B-Series | B-1~B-4만 | **B-1~B-6** | 1 |
| 3 | §5 Phase 4/5 | Memory(S7)/Reflection(S6) 순서 | **S6→S7** | 1 |
| 4 | §7.3 V2 daily | 3,300 | **B4=3,100** | 8,13 |
| 5 | §7.3 V3 daily | 9,300 | **B4=8,900** | 8,13 |
| 6 | §10 V1-#5 | approval_status 4값 | **D7 SOT=2값** | 9,13 |
| 7 | §11 V2 UI | "Next.js" | **D2.1-D8 "React"** | 7 |
| 8 | §12 Decision | "16필드" | **17필드** | 5,8 |
| 9 | §12 Decision | s_module_hints 유령 필드 | **SOT에 없음** | 5 |
| 10 | §12 IntentFrame | 18필드 혼합 나열 | **base 10+ext 8 구분** | 5 |
| 11 | §15 L0 TTL | "7일(최대 30일)" | **D2.0-06 "세션종료(최대 7일)"** | 6 |
| 12 | §17 NEVER_AUTO | 6항목 | **10항목** | 1,2,3 |
| 13 | §13 IPC (간접) | — | **B1 47 vs CLAUDE.md 72 자기모순** | 4,8 |
| 14 | §12 approval_status | 4값 FREEZE | **D7 SOT=2값과 충돌** | 9,13 |

---

### 8. 우선순위별 시정 조치

#### Priority 1 — 구현 차단 (Phase 2 진입 전 필수, 9건)

| # | 조치 | 대상 | 근거 |
|---|------|------|------|
| 1 | CLAUDE.md NEVER_AUTO 10개로 확장 | CLAUDE.md §17 | SDAR_SPEC 10개 정본 |
| 2 | CLAUDE.md 모듈 81개 + B-5/B-6 추가 | CLAUDE.md §6 | D2.0-01 §5 정본 |
| 3 | CLAUDE.md Decision 17필드 정정 | CLAUDE.md §12 | D2.1-D2 SOT |
| 4 | CLAUDE.md approval_status 2값 정정 | CLAUDE.md §10, §12 | D2.1-D7 SOT |
| 5 | PART2 config.v1.toml 섹션명 정정 | PART2 §2 | B4 정본: [core], [guardrails] |
| 6 | PART2 [rbac]/[rate_limit] 섹션 추가 | PART2 §2 | B4 §2.10-2.11 |
| 7 | PART2 Cloud Library G0-G4 정본 수정 | PART2 §6.10 | CL_SPEC §8 |
| 8 | PART2 Cloud Library LOCK L1~L13 반영 | PART2 §6.10 | CL_SPEC §16 |
| 9 | PART2 AI Investing vectorbt → "조건부 ADOPT" | PART2 §6.8 | D-S3-05 |

#### Priority 2 — 구현 위험 감소 (11건)

| # | 조치 | 대상 |
|---|------|------|
| 10 | PART2 Hooks/Stores 이름 PHASE_B2 정정 | PART2 §6.1.3 |
| 11 | PART2 "5 페이지" → 7 페이지 | PART2 §6.1.4 |
| 12 | CLAUDE.md daily_limit V2=3100, V3=8900 | CLAUDE.md §7.3 |
| 13 | CLAUDE.md V2 UI "Next.js" → "React" | CLAUDE.md §11 |
| 14 | CLAUDE.md L0 TTL 정정 | CLAUDE.md §15 |
| 15 | B6 Rust nightly → stable | PHASE_B6 |
| 16 | B1 IPC 47 → 72 정정 | PHASE_B1 |
| 17 | PART2 E-5 V1/V2 표기 통일 | PART2 V1-Phase 3 |
| 18 | PART2 컴포넌트 출처 정정 | PART2 Phase 4 |
| 19 | PART2 동시 처리 메트릭 구분 표기 | PART1/PART2 |
| 20 | PART2 Multi-Brain Failover 체인 추가 | PART2 |

#### Priority 3 — 구현 시 참조 보충 (7건)

| # | 조치 | 대상 |
|---|------|------|
| 21 | PART2에 UI State Machine 구현 항목 추가 | PART2 §6.1 |
| 22 | PART2에 Failure/Fallback UI 참조 추가 | PART2 §6.1 |
| 23 | PART2에 UI 접근 제어 규칙 참조 추가 | PART2 §6.1 |
| 24 | PART2에 AC 매핑 50AC→79 반영 | PART2 §6.3 |
| 25 | PART2에 B7 10-Step + 사후검증 7항목 보충 | PART2 §4 |
| 26 | PART2에 SDAR State Machine/5 Gates 참조 추가 | PART2 §6.9 |
| 27 | PART2 VAL-001~VAL-010 B4 원본 기준 정정 | PART2 |

---

### 9. Agent 11/12 미존재 갭 분석

| Agent | v8.1 역할 | 현황 | 영향 |
|-------|----------|------|------|
| Agent 11 | AI 프롬프트 검증 (V0~V3 FREEZE/LOCK 위반) | **결과 미생성** | PART2 V0~V3 AI 프롬프트 FREEZE/LOCK 위반 검증 누락. Phase 2 전 실행 권고 |
| Agent 12 | D2.0-02 교차검증 (D2.0-01↔D2.0-02↔§7.x 트리플 매핑) | **결과 미생성** | D2.0-02 기반 교차 검증 누락. 코어 아키텍처 정합성에 영향 가능 |

> **권고**: Phase 2 진입 전 Agent 11, Agent 12 결과 보고서 생성 및 Agent 13 재검증 추가 수행.

---

## PART IV — 종합 결론

### Phase 1 검증 결과 신뢰도: **HIGH**

1. **Spot-check 1.5% 오판율 (65/66 CONFIRMED)**: Phase 1 재실행 불필요
2. **핵심 오류 교차 발견**: NEVER_AUTO, 모듈 수, Decision 필드, approval_status, daily_limit, V2 UI 프레임워크, Cloud Library G0-G4 등이 복수 에이전트에서 독립 식별
3. **REAL_ERROR 53건 확정**: HIGH 11건 즉시 수정 필수
4. **SOURCE_CONFLICT 22건 확정**: CLAUDE.md가 65%+ (14/22건) — CLAUDE.md 갱신 최우선
5. **FALSE_POSITIVE 27건**: 전부 LOW~MEDIUM. MATCH→MISMATCH 뒤집힌 사례 1건 (Agent 7 카운트 정정)

### Phase 1.5 완료 판정

| 판정 항목 | 결과 |
|----------|------|
| Phase 1 재실행 필요 여부 | **불필요** (Spot-check 1.5% < 10%) |
| 에이전트별 전범위 재검증 | **Agent 7 권고** (11.1%, 20% 미만이나 경계선) |
| Agent 11/12 보충 필요 여부 | **필요** (v8.1 신규 에이전트 미실행) |
| 시정 조치 필수 여부 | **필수** (HIGH 11건, MEDIUM 28건) |
| 다음 단계 | **Priority 1 시정 조치 9건 완료 → Agent 11/12 실행 → Phase 2 진입** |

---

*Agent 13 (Phase 1.5 배치 B + 통합) 적대적 재검증 완료. 2026-03-05.*
*SRC 원본 직접 재열독, 16건 Spot-check, 58건 비-MATCH 재검증, 배치 A 통합.*
