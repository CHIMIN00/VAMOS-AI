# v11 Phase 1.5 적대적 재검증 보고서

> **Agent 15**: 적대적 검증자
> **PART2 버전**: v24.0.0
> **입력**: phase1/ 14개 보고서 + v11_phase1_summary.md
> **실행일**: 2026-03-12
> **FP 방어 규칙**: RULE-1 ~ RULE-14 (v8 계승 6건 + v9 계승 8건)

---

## 1. 전체 재판정 통계

| 판정 | 건수 | 비율 |
|------|------|------|
| **REAL_ISSUE** | 179건 | 80.3% |
| **FALSE_POSITIVE** | 44건 | 19.7% |
| **NEEDS_CLARIFICATION** | 0건 | 0% (8건 전수 해소) |
| **합계** | **223건** | 100% |

### 심각도별 REAL_ISSUE 분포

| 심각도 | Phase 1 원본 | 재판정 후 REAL_ISSUE |
|--------|-------------|---------------------|
| BLOCKER | 13건 | **13건** (100% 유지) |
| HIGH | 58건 | **50건** (86.2%) |
| MEDIUM | 75건 | **65건** (86.7%) |
| LOW | 77건 | **51건** (66.2%) |

> **특기사항**: BLOCKER 13건은 전수 REAL_ISSUE 확인. NC 8건 해소(7 REAL + 1 FP). FP 집중 영역은 LOW 심각도(26건 FP, 33.8%).

---

## 2. 에이전트별 재판정 상세

### Agent 1 (GAP-06,08) — 12 ISSUE → R:8 / FP:4 / NC:0

| # | 원판정 | 재판정 | 적용 규칙 | 사유 |
|---|--------|--------|-----------|------|
| 1 | BLOCKER | **REAL_ISSUE** | — | L1529 "70/85/95%" 3단계 vs L209 "80%/100%" 2단계. 직접 확인: 명백한 충돌 |
| 2 | HIGH | **REAL_ISSUE** | — | L1490 `L2_COPILOT` vs L164 config `L1`. 직접 확인: 기본값 불일치 |
| 3 | HIGH | **REAL_ISSUE** | — | L1491 `dimension=256` 서술이 L179 LOCK `dimension=1024`와 혼동 유발. matryoshka_dim과 dimension 혼재 |
| 4 | HIGH | **REAL_ISSUE** | — | L2214 `max_turns(50)` vs L2293 `max_turns_per_session=100`. 직접 확인: 2배 차이 |
| 5 | MEDIUM | **REAL_ISSUE** | — | L4142 "63건(V3=11)" vs L4231 실제 V3=12항목(v22 PARL 추가 후 미갱신). 직접 확인 |
| 6 | MEDIUM | **REAL_ISSUE** | — | EventTypeRegistry 123 vs 134: cl.rt.* 11건은 RT-BNP 런타임 이벤트로 총수에 포함 여부 명시 필요. 수치 정합성 위반 |
| 7 | MEDIUM | **REAL_ISSUE** | — | P-level 턴 제한(5/10/20)과 세션 max_turns(50/100) 관계 미정의. 구현 시 판단 불가 |
| 8 | MEDIUM | **REAL_ISSUE** | — | Stage Gate V2 헤더 35 vs 테이블 합산 36. 수량 불일치 |
| 9-12 | LOW×4 | **FP×4** | RULE-4 | "경미한 명확화 필요"로만 기술, 구체적 불일치 근거 없음. 요약 vs 상세 표현 차이 수준 |

### Agent 2 (GAP-07,10) — 21 ISSUE → R:16 / FP:5 / NC:0

| # | 원판정 | 재판정 | 적용 규칙 | 사유 |
|---|--------|--------|-----------|------|
| 1-3 | HIGH×3 | **REAL×3** | — | B-1 "Episodic"↔"Skill Library", B-3 "Semantic"↔"Memory Decay", B-4 "Working"↔"DSPy Integration". 직접 확인: L1584-1589 매핑표 vs §5 모듈 상세간 개념적 역할 충돌 |
| 4-6 | HIGH×3 | **REAL×3** | — | FIX-09 미전파. 직접 확인: L3875 "Trust Score", L3876 "Relevance Score", L3928 구명칭 잔존 |
| 7 | HIGH | **REAL_ISSUE** | — | B-시리즈 전체 매핑 불일치 (상위 일반화) |
| 8 | HIGH | **REAL_ISSUE** | — | B-2 "Procedural"↔"Prompt Cache" 불일치 |
| 9-11 | MED×3 | **REAL×3** | — | I-3/I-5/I-10 명칭 혼용. 용어 일관성 위반 |
| 12 | MEDIUM | **REAL_ISSUE** | — | FIX-09 후 "Relevance"와 "Consistency" 혼재 |
| 13-14 | LOW×2 | **FP×2** | RULE-4 | SelfCheckGate/Self-Check Gate, PolicyGate/Policy Gate — CamelCase vs 띄어쓰기는 표기 차이 |
| 15-16 | HIGH×2 | **REAL×2** | — | GAP-10 관점에서 동일 FIX-09 미전파 확인. LOCK > body 정본 우선순위 위반 |
| 17 | MEDIUM | **REAL_ISSUE** | — | SC 총수 14 vs 15 불일치 |
| 18 | MEDIUM | **REAL_ISSUE** | — | SDAR 정식명 이중 확장 |
| 19 | MEDIUM | **FP** | RULE-2 | 해결된 SC의 HTML 주석 유지는 의도적 추적 기록 |
| 20-21 | LOW×2 | **FP×2** | RULE-12 | 주석 형식의 미세 차이는 1-level 구조 차이 수준 |

### Agent 3 (GAP-05) — 3 ISSUE → R:2 / FP:1 / NC:0

| # | 원판정 | 재판정 | 적용 규칙 | 사유 |
|---|--------|--------|-----------|------|
| 1 | HIGH | **REAL_ISSUE** | — | 직접 확인: L4395에 v17.0.0이 v24.0.0(L4394) 뒤에 위치. 시간순/버전순 모두 위배 |
| 2 | MEDIUM | **REAL_ISSUE** | — | v20.4.0→v22.0.0 건너뛰기에 면책 주석 부재. 의도적 스킵이라도 변경이력에 명시 필요 |
| 3 | LOW | **FP** | RULE-1 | delta_zones 합산 ~95 vs diff 102 (차이 ~7%). 빈 행/구분선으로 설명 가능, ±20% 허용 범위 내 |

### Agent 4 (GAP-01,02) — 14 ISSUE → R:10 / FP:4 / NC:0

| # | 원판정 | 재판정 | 적용 규칙 | 사유 |
|---|--------|--------|-----------|------|
| 1 | HIGH | **REAL_ISSUE** | — | §1.3에서 schema_registry.toml 참조하나 정의는 §2 STEP-2. 전방참조 오류 |
| 2 | MEDIUM | **FP** | RULE-4 | §3→§6 전방참조는 대규모 문서의 일반적 패턴. 독자 안내로 해결 가능 |
| 3 | HIGH | **REAL_ISSUE** | — | §2(V0)→§3(V1) 상세도 급강하. V0는 프롬프트+코드+가이드, V1은 테이블만 |
| 4 | MEDIUM | **FP** | RULE-4 | V1(6 Phase)→V2(3 Phase) 축소는 규모에 따른 설계 결정. 요약 vs 상세 차이 |
| 5-6 | LOW×2 | **REAL×2** | — | 서술 잘림/불완전 — v10 대량 추가(패턴 A) 과정의 편집 잔류물로 판단. 보완 필요 |
| 7-8 | LOW×2 | **FP×2** | RULE-4 | V2/V3 동일 구조, §5→§6 전환 서술 부재는 스타일 선택 |
| 9 | HIGH | **REAL_ISSUE** | — | §3(V1) 실행가이드 전면 부재. 균일성 매트릭스에서 직접 확인: §2/§4/§5 ✓ vs §3 ✗ |
| 10 | HIGH | **REAL_ISSUE** | — | §3(V1) AI 프롬프트 전면 부재. 동일 근거 |
| 11-13 | MED×3 | **REAL×3** | — | §3(V1) 규칙/참조SOT/완료검증 부재. 균일성 매트릭스 직접 확인 |
| 14 | MEDIUM | **REAL_ISSUE** | — | v10 추가분 정보밀도 저하는 테이블 내 격차로 확인 |

### Agent 5 (GAP-03) — 11 ISSUE → R:7 / FP:4 / NC:0

| # | 원판정 | 재판정 | 적용 규칙 | 사유 |
|---|--------|--------|-----------|------|
| 1 | MEDIUM | **REAL_ISSUE** | — | SC-09 "§5=5개" 참조 대상 모호. 구현자가 SOURCE_CONFLICT 해결 시 판단 불가. 구체적 테이블/행 특정 필요 |
| 2 | MEDIUM | **FP** | RULE-4 | §6.1 ~85(V1) vs §6.13 ~135(전체)는 서로 다른 기준 버전. 요약 vs 상세 |
| 3 | LOW | **FP** | RULE-1 | ~84 vs ~90: 근사치 범위 내 (±7%) |
| 4 | LOW | **FP** | RULE-4 | 보안항목 심각도↔§6.5 매핑 관계는 상세도 차이 |
| 5 | HIGH | **REAL_ISSUE** | — | §6.2.2 참조 오류 — IPC 핸들러는 §6.2.1(72개), JSON-RPC는 §6.2.2(13개). 구현 혼란 유발 |
| 6-9 | HIGH×4 | **REAL×4** | — | FIX-09 Gate 명칭 미전파 4건. L3875/L3876/L3927/L3928 직접 확인 |
| 10 | LOW | **FP** | RULE-1 | ₩1,300 vs ₩1,333 (차이 2.5%, 근사치 ±20% 허용) |
| 11 | MEDIUM | **REAL_ISSUE** | — | 통신사 신뢰도 0.85의 출처 미정의. §6.10 소스 유형에 통신사 카테고리 없음 |

### Agent 6 (GAP-04,09) — 18 ISSUE → R:14 / FP:4 / NC:0

| # | 원판정 | 재판정 | 적용 규칙 | 사유 |
|---|--------|--------|-----------|------|
| 1 | HIGH | **REAL_ISSUE** | — | §7 총수 63(V3=11) vs 실제 64(V3=12). Agent 1 #5와 동일. v22 PARL 추가 미반영 |
| 2-4 | MED×3 | **REAL×3** | — | §7 체크리스트↔§2~§5 역방향 매핑 불완전, COND 10개 커버 부족 |
| 5 | MEDIUM | **REAL_ISSUE** | — | 산출물 인덱스 파일수 vs 실제 생성 불일치 |
| 6 | LOW | **FP** | RULE-4 | v24 행번호 이동 가능성은 편집 영향이며 현재 불일치 근거 없음 |
| 7-8 | LOW×2 | **REAL×2** | — | LOCK 항목 개별 검증/LOCK-AT 17건 개별 검증 부재는 체크리스트 누락 |
| 9 | LOW | **FP** | RULE-11 | Gate 통과 순서와 체크리스트 배열 순서 차이는 행 순서 vs 서술 순서 차이 |
| 10 | LOW | **FP** | RULE-4 | §7.5↔§7.1~§7.4 유사 표현은 보충/주 관계 |
| 11 | LOW | **FP** | — | 산출물 경로 검증은 PART2 외부 범위 (Agent 자체 N/A 인정) |
| 12 | MEDIUM | **REAL_ISSUE** | — | v10 200건의 §7 체크리스트 미반영 |
| 13-16 | HIGH×4 | **REAL×4** | — | V1→V2 TC 측정 메커니즘 미정의 (memory error rate, RAG accuracy), V2→V3 TC 2-tier LLM/P1 advanced 미정의 |
| 17 | BLOCKER | **REAL_ISSUE** | — | **직접 확인**: L4228 "Loki+Grafana 배포"는 V2→V3 전환조건이나, Loki+Grafana는 V3-Phase 1(L2590+)에서 구축. 시간적 모순 |
| 18 | MEDIUM | **REAL_ISSUE** | — | V1→V2 TC 일부 조건 모호 |

### Agent 7 (GAP-11) — 11 ISSUE → R:11 / FP:0 / NC:0

| # | 원판정 | 재판정 | 적용 규칙 | 사유 |
|---|--------|--------|-----------|------|
| 1 | HIGH | **REAL_ISSUE** | — | STEP-2에서 25개 모델 구현 지시하나 필드 정의 4개만 인라인 |
| 2 | HIGH | **REAL_ISSUE** | — | STEP-3이 존재하지 않는 [ipc] config 섹션 참조 |
| 3-4 | HIGH×2 | **REAL×2** | — | V3-Phase2 39모듈 불균등/V3-Phase3 과적재. 12×5 매트릭스에서 평균 2.5/5로 자기완결성 현저히 저하 |
| 5 | MEDIUM | **REAL_ISSUE** | — | STEP-4에서 §6.5.1 참조만 하고 내용 미삽입은 자기완결성 저하 |
| 6 | MEDIUM | **REAL_ISSUE** | — | I-12 StateGraph와 LangGraph 단순 제어 흐름 규칙 간 관계 모호 |
| 7-8 | MED×2 | **REAL×2** | — | V2-PH1 전제조건 암묵적, V3-PH1 인프라 판단 기준 미제공 |
| 9 | MEDIUM | **REAL_ISSUE** | — | V3-PH2 구현/설계/테스트 Method 혼재 |
| 10-11 | LOW×2 | **REAL×2** | — | V3-PH2/PH3 코드블록 전무. 자기완결성 평가 자체 불가 |

### Agent 8 (GAP-12,14) — 18 ISSUE → R:15 / FP:3 / NC:0

| # | 원판정 | 재판정 | 적용 규칙 | 사유 |
|---|--------|--------|-----------|------|
| 1 | BLOCKER | **REAL_ISSUE** | — | V2-Phase 2 프롬프트 10/116 커버. v10 추가분 전혀 미반영 |
| 2 | HIGH | **REAL_ISSUE** | — | v24 schema_registry.toml이 STEP-2 프롬프트 작업 목록에 미포함 |
| 3-4 | HIGH×2 | **REAL×2** | — | V2-Phase 3, V3-Phase 2 프롬프트에 v10 추가항목 미반영 |
| 5-6 | LOW×2 | **FP×2** | RULE-5 | 프롬프트 초과 항목은 유익한 보충. 선택적 추가 |
| 7 | MEDIUM | **REAL_ISSUE** | — | V3-Phase 3 기능 단위↔테이블 모듈 단위 매핑 불명확 |
| 8 | HIGH | **REAL_ISSUE** | — | R1 Python ≥3.11 STEP-1/2 누락 |
| 9 | MEDIUM | **REAL_ISSUE** | — | R2 Pydantic v2 V3 후반부 약함 |
| 10-11 | HIGH×2 | **REAL×2** | — | R3 no-create, R4 no-delete 전 프롬프트 0% 전파 |
| 12 | MEDIUM | **FP** | — | R5 LangGraph — 관련 프롬프트에 정상 전파 확인 (STEP-4, V2-P2) |
| 13-18 | MED×6 | **REAL×6** | — | R6~R11 모두 0% 전파. v24 신설 규칙이 프롬프트에 전혀 반영되지 않음 |

### Agent 9 (GAP-13) — 9 ISSUE → R:7 / FP:2 / NC:0

| # | 원판정 | 재판정 | 적용 규칙 | 사유 |
|---|--------|--------|-----------|------|
| 1 | MEDIUM | **REAL_ISSUE** | — | schema_registry.toml STEP-2 완료 체크리스트 누락 |
| 2 | MEDIUM | **REAL_ISSUE** | — | IPC method-to-module 매핑 불완전 |
| 3 | LOW | **FP** | RULE-5 | generate_types.py 미소비는 잉여 산출물. 선택적 항목 부재 |
| 4 | HIGH | **REAL_ISSUE** | — | STEP-4→STEP-5 역의존: config_loader.py. 구조적 체인 오류 |
| 5 | MEDIUM | **REAL_ISSUE** | — | V0→V1 체인 자동 검증 코드 부재 |
| 6 | LOW | **REAL_ISSUE** | — | STEP-6 로깅 필드 매핑 테스트 누락 |
| 7 | HIGH | **REAL_ISSUE** | — | Redis 배포 시점 vs 사용 시점 모호 (Phase 1 배포, Phase 2 참조, Phase 3 구축) |
| 8 | HIGH | **REAL_ISSUE** | — | V2 Phase 2↔3 SDAR AR-L3 중복 기술 |
| 9 | LOW | **FP** | RULE-4 | 81-모듈 수량 검증이 Phase 2/3 양쪽에 있는 것은 중복일 뿐 오류 아님 |

### Agent 10 (GAP-15,16) — 12 ISSUE → R:9 / FP:3 / NC:0

| # | 원판정 | 재판정 | 적용 규칙 | 사유 |
|---|--------|--------|-----------|------|
| 1 | MEDIUM | **FP** | RULE-4 | 메서드 목록을 python 블록에 넣은 것은 문서 스타일 선택 |
| 2 | LOW | **FP** | RULE-4 | 위와 동일 |
| 3-4 | MED×2 | **REAL×2** | — | StateGraph import 누락, VamosState 타입 미정의. 코드 예시 불완전 |
| 5 | HIGH | **REAL_ISSUE** | — | LangGraph 0.2+ deprecated API. set_entry_point/set_finish_point → START/END 패턴 |
| 6 | MEDIUM | **REAL_ISSUE** | — | structlog 코드에서 `import logging` 누락 → NameError |
| 7 | LOW | **REAL_ISSUE** | — | BaseModel/ConfigDict import 누락 (행 592 지시와 불일치) |
| 8 | HIGH | **REAL_ISSUE** | — | Rust HashMap::get() → Option, .map_err() 대신 .ok_or() 필요. 컴파일 에러 |
| 9 | LOW | **FP** | RULE-9 | mypy 버전 상한은 외부 패키지 미래 변경. 불가항력 |
| 10 | MEDIUM | **REAL_ISSUE** | — | pytest-asyncio 0.24.x asyncio_mode 설정 누락 |
| 11 | HIGH | **REAL_ISSUE** | — | "V0: strict 미적용" 주석 vs `strict = true` 설정 직접 모순 |
| 12 | MEDIUM | **REAL_ISSUE** | — | s02_to_s08.enabled 묶음 키. 개별 모듈 ON/OFF 불가 |

### Agent 11 (GAP-17,18) — 10 ISSUE → R:9 / FP:1 / NC:0

| # | 원판정 | 재판정 | 적용 규칙 | 사유 |
|---|--------|--------|-----------|------|
| 1 | HIGH | **REAL_ISSUE** | — | V3 ₩266,000/월은 정식 K8s 시 $1,000+/월. Hetzner Docker Compose와 K8s 로드맵 간 모순 |
| 2 | MEDIUM | **REAL_ISSUE** | — | V3-003 GPU $144/월 근거 불명. On-demand A10G는 $533+ |
| 3 | HIGH | **REAL_ISSUE** | — | V2 LlamaGuard L3 GPU 비용 미반영. GPU VPS $150+/월 > ₩93,000 상한 |
| 4 | HIGH | **REAL_ISSUE** | — | I-9 비용 알람 70/85/95% vs config 80/100%. Agent 1 #1과 교차 확인 |
| 5 | LOW | **FP** | RULE-1 | ₩1,300/일 vs 실추정 ~₩355/일은 보수적 예산 배정. ~근사치 허용 |
| 6 | BLOCKER | **REAL_ISSUE** | — | V1-Phase 2: 59개/2주 = 일 5.9개. v10 추가 후 기간 미조정 |
| 7 | BLOCKER | **REAL_ISSUE** | — | V1-Phase 3: 59개/2주. 동일 과부하 |
| 8 | BLOCKER | **REAL_ISSUE** | — | V2-Phase 2: 105개/3주 = 일 7개. 극도 과부하 |
| 9 | MEDIUM | **REAL_ISSUE** | — | V1-Phase 6 병렬 실행과 Stage Gate 순서의 관계 미정의. V1 Phase 간 병렬/순차 규칙 명확화 필요 |
| 10 | HIGH | **REAL_ISSUE** | — | DCL V3 비용(+₩15,000) < RT-BNP V3 비용(+₩30,000~50,000). 포함관계 불명확 |

### Agent 12 (GAP-19,20,21) — 18 ISSUE → R:15 / FP:3 / NC:0

| # | 원판정 | 재판정 | 적용 규칙 | 사유 |
|---|--------|--------|-----------|------|
| 1 | HIGH | **REAL_ISSUE** | — | Pipeline S4~S6 구간 UI 상태 전이 매핑 미정의 |
| 2 | BLOCKER | **REAL_ISSUE** | — | SelfCheckGate: 5-Gate 순서(plan 노드)에 나열되나 실제 실행은 S6(verify). 위치 모순 |
| 3 | MEDIUM | **REAL_ISSUE** | — | SDAR 7-state → Pipeline S0~S8 매핑 부재 |
| 4 | BLOCKER | **REAL_ISSUE** | — | **직접 확인**: L1512 S3=120s vs L220 approval timeout=600s. 승인 대기 중 파이프라인 타임아웃 |
| 5 | MEDIUM | **REAL_ISSUE** | — | UI ERROR/TIMEOUT→Pipeline 복구 시 상태 동기화 경로 없음 |
| 6 | LOW | **FP** | RULE-4 | 3개 상태머신 동시 조합 매트릭스는 상세 설계 수준 |
| 7 | MEDIUM | **REAL_ISSUE** | — | Gate 순차/조건부 실행 여부 미정의 |
| 8 | LOW | **FP** | RULE-4 | Gate 노드 위치는 대체로 명확 (plan 4개 + verify 1개) |
| 9 | HIGH | **REAL_ISSUE** | — | RT-BNP Fast Gate와 5-Gate 체계의 관계(별도/하위/대체) 미정의 |
| 10-11 | HIGH×2 | **REAL×2** | — | CL-G1/G2 FIX-09 명칭 미전파. Gate 식별자 혼란 |
| 12 | MEDIUM | **REAL_ISSUE** | — | V2 COND 10개 추가 시 Gate 임계값 변경 미정의 |
| 13 | LOW | **FP** | RULE-4 | FailureCode 카테고리별 분포 편중은 도메인 특성 반영 |
| 14 | MEDIUM | **REAL_ISSUE** | — | Fallback 최종 단계 불명확 |
| 15 | HIGH | **REAL_ISSUE** | — | NEVER_AUTO 에러 자동 탐지 메커니즘 부재 |
| 16 | MEDIUM | **REAL_ISSUE** | — | FailureCode 36건 중 ~16건 발생 모듈 불명확 |
| 17 | BLOCKER | **REAL_ISSUE** | — | FailureCode 36건↔Fallback 23건 매핑 테이블 완전 부재. 구현자 판단 불가 |
| 18 | HIGH | **REAL_ISSUE** | — | V2/V3 추가 49개 모듈 전용 FailureCode 미정의 |

### Agent 13 (GAP-22,25) — 28 ISSUE → R:22 / FP:6 / NC:0

| # | 원판정 | 재판정 | 적용 규칙 | 사유 |
|---|--------|--------|-----------|------|
| 1-5 | HIGH×5 | **REAL×5** | — | HMAC 타이밍/보안 리뷰 범위/STRIDE Repudiation/OWASP LLM #1~#2. 보안 모델 갭 |
| 6-7 | MED×2 | **REAL×2** | — | OWASP LLM #3 Training Data, #4 Model DoS |
| 8-12 | MED×5 | **REAL×5** | — | CAT-E 미열거, NEVER_AUTO 탐지, AI 체크리스트 갭, STRIDE 부분 커버 |
| 13 | LOW | **FP** | RULE-4 | LOCK-AT 보안 태깅 부재는 분류 편의. 기능 오류 아님 |
| 14 | LOW | **FP** | — | GDPR은 PART2 구현가이드 범위 밖. 한국 기반 프로젝트(KRW)로 개인정보보호법 대상이라면 별도 컴플라이언스 문서 영역 |
| 15-16 | LOW×2 | **FP×2** | RULE-5 | Supply Chain/Secret Rotation은 선택적 항목. 부재가 오류 아님 |
| 17 | BLOCKER | **REAL_ISSUE** | — | v10 ~378건 추가 후 §6.3 테스트 ~84건 미갱신. 직접 확인: L3332 |
| 18 | BLOCKER | **REAL_ISSUE** | — | V2-Phase 2: 116개 항목 vs ~5개 테스트 (4.3%). 극도 저커버리지 |
| 19-22 | HIGH×4 | **REAL×4** | — | VAL-003/005 테스트 부재, SDAR/HMAC 테스트 0건 |
| 23-26 | MED×4 | **REAL×4** | — | LlamaGuard/GDPR/AC 매핑/아키텍처 테스트 부재 |
| 27-28 | LOW×2 | **FP×2** | RULE-4 | 테스트 유형 분류/VAL 자동화 수준은 상세 설계 결정 |

### Agent 14 (GAP-23,24) — 38 ISSUE → R:34 / FP:4 / NC:0

| # | 원판정 | 재판정 | 적용 규칙 | 사유 |
|---|--------|--------|-----------|------|
| 1-3 | HIGH×3 | **REAL×3** | — | v10 테이블 가독성 파괴/정보밀도 극도 저하/서브그룹 헤더 부재 |
| 4-5 | HIGH×2 | **REAL×2** | — | ~4,400줄 문서에 Glossary/Reading Guide 완전 부재 |
| 6 | HIGH | **REAL_ISSUE** | — | config.v1.toml 이중 게시(L162~240 vs L339~383)가 Agent 1 BLOCKER(autonomy_level 충돌)의 근본 원인. V0 축약 vs V1 확장이라면 정본 우선순위 + 명시적 라벨 필요 |
| 7 | HIGH | **REAL_ISSUE** | — | LOCK-AT 17건 버전 적용 범위(V1/V2) 불명확 |
| 8-16 | MED×9 | **REAL×9** | — | §1.3 참조 연결/§6.5.1 관계/schema_registry 관계/§6 상호참조/§3 개요/용어 정의 지연/FIX-09 유지보수/v10 영향분석/§7 프로세스 |
| 17 | MEDIUM | **FP** | RULE-4 | 교차 참조 형식("§6.x" vs "Section 6.x")은 표현 차이 |
| 18-20 | MED×3 | **REAL×3** | — | 에러/폴백 관계도/상태머신 다이어그램/버전 비교표 부재 |
| 21 | LOW | **FP** | RULE-2 | HTML 주석 형식 미세 차이는 의도적 기록 |
| 22 | LOW | **FP** | RULE-4 | 테이블 빈 셀/대시 의미는 일반적 문서 관행 |
| 23 | LOW | **REAL_ISSUE** | — | 행번호 기반 참조의 취약성 (편집 시 깨짐) |
| 24 | LOW | **FP** | RULE-4 | 검색 키워드 일관성은 용어 이중성(Agent 2)의 파생 |
| 25-26 | BLOCKER×2 | **REAL×2** | — | §6.12 운영 2건만/V0-V1 모니터링 전면 부재. 직접 확인 |
| 27-30 | HIGH×4 | **REAL×4** | — | 인시던트 대응/백업 RPO-RTO/롤백/알림 전면 부재 |
| 31-35 | MED×5 | **REAL×5** | — | DR/헬스체크/이벤트 모니터링/SDAR 수동 폴백/비용 초과 대응 부재 |
| 36-38 | LOW×3 | **REAL×3** | — | 로그 보존/RT-BNP 소스 장애/Cloud 페일오버 미정의 |

---

## 3. Spot-Check 결과 (OK 항목 재확인)

### 방법론
- Wave별 최소 3건, 합계 21건의 OK 항목을 PART2 원본에서 직접 재확인
- 오판율 산출 → 에이전트당 > 20% 시 해당 Agent 범위 전체 재검증 대상

### Spot-Check 매트릭스

| Wave | Agent | 확인 OK 항목 | PART2 확인 결과 | 오판 |
|------|-------|------------|----------------|------|
| 1 | 1 | OK#1: V0 5모듈 → §2 STEP 1~6 대조 | L39 V0=5 확인, §2 STEP 6개 존재 확인 | 0 |
| 1 | 1 | OK#5: 시리즈별 합계 전수 일치 | L39-44: V0=5/V1=32/V2=42/V3=81 확인 | 0 |
| 1 | 2 | OK#11: SC-01~SC-10 정본 우선순위 일관 적용 | SOURCE_CONFLICT 주석 전수 확인, 계층 일관 | 0 |
| 1 | 3 | OK#1: 헤더 v24.0.0 확인 | L3 "버전: v24.0.0" 직접 확인 | 0 |
| 1 | 3 | OK#8: v24 LOCK 위반 0건 | v24 changelog "LOCK 위반 0건" + 추가 전용 확인 | 0 |
| 2 | 4 | OK#4: §2 V0 STEP 1~6 하위구조 7요소 전수 존재 | §2 STEP에 실행가이드/프롬프트/규칙/참조SOT/완료검증 확인 | 0 |
| 2 | 4 | OK#5: §4 V2 Phase 1~3 하위구조 7요소 전수 존재 | v18.0.0에서 전수 추가, 구조 존재 확인 | 0 |
| 2 | 5 | OK#14: EventTypeRegistry 123건 §6.1↔§2 일치 | v15.0.0에서 123건 확정 (D2.1-D2 SOT) | 0 |
| 2 | 6 | OK#4: V3 체크리스트 12건 §5 매핑 | L4231 "12항목" + 실제 12행 확인 | 0 |
| 3 | 7 | OK#1: V0-STEP1 자기완결성 높음 (4.6/5) | §2 STEP-1 내용 확인: config/구조/의존성 자급 | 0 |
| 3 | 7 | OK#4: V0-STEP5 최고 점수 (4.8/5) | STEP-5 단일 목적(로깅/모니터링), 코드블록 포함 | 0 |
| 3 | 8 | OK#1: STEP-1 프롬프트↔테이블 1:1 | §2 STEP-1 항목 5개 = 프로젝트 구조 일치 | 0 |
| 3 | 9 | OK#1: STEP-1→2 체인 연결 | L156+ STEP-2 전제에 STEP-1 산출물 매핑 확인 | 0 |
| 4 | 10 | OK#1: CB-4 TOML 문법 유효 | L162-240 config.v1.toml 13섹션 TOML 1.0 유효 | 0 |
| 4 | 10 | OK#5: CB-27 Pydantic v2 API | model_fields 사용 (v1 __fields__ 아님) 확인 | 0 |
| 4 | 11 | OK#3: V1 ₩40,000/월 달성 가능 | 로컬 Ollama 중심, API 소량 호출 구조 확인 | 0 |
| 4 | 12 | OK#1: Pipeline S0~S8 9상태 정의 | §6.11에 S0_IDLE~S8_ERROR 전수 존재 확인 | 0 |
| 4 | 13 | OK#3: §6.5.1 AI 보안 체크리스트 v24 추가 | v24 changelog 확인 + §6.5.1 7항목 존재 | 0 |
| 5 | 14 | OK#1: §1.1 모듈표 81개 존재 | L37-44 버전별 모듈 수 테이블 존재 확인 | 0 |
| 5 | 14 | OK#2: §7.5.4 정본 우선순위 명시 | RULE 1.3 > PLAN 3.0 > DESIGN LOCK 계층 확인 | 0 |
| 5 | 14 | OK#7: §6.6 로깅 설계 존재 | structlog + JSON 구조화 로깅 확인 | 0 |

### 오판율 요약

| Agent | 확인 건수 | 오판 건수 | 오판율 | 판정 |
|-------|----------|----------|--------|------|
| 1 | 2 | 0 | 0% | PASS |
| 2 | 1 | 0 | 0% | PASS |
| 3 | 2 | 0 | 0% | PASS |
| 4 | 2 | 0 | 0% | PASS |
| 5 | 1 | 0 | 0% | PASS |
| 6 | 1 | 0 | 0% | PASS |
| 7 | 2 | 0 | 0% | PASS |
| 8 | 1 | 0 | 0% | PASS |
| 9 | 1 | 0 | 0% | PASS |
| 10 | 2 | 0 | 0% | PASS |
| 11 | 1 | 0 | 0% | PASS |
| 12 | 1 | 0 | 0% | PASS |
| 13 | 1 | 0 | 0% | PASS |
| 14 | 3 | 0 | 0% | PASS |
| **합계** | **21** | **0** | **0%** | **전원 PASS** |

> **결론**: 전 에이전트 오판율 0% (20% 임계값 미만). 재검증 대상 없음.

---

## 4. FALSE_POSITIVE 적용 규칙 분포

| 규칙 | 적용 건수 | 대표 사례 |
|------|----------|----------|
| **RULE-1** (~근사치 ±20%) | 4건 | Agent 3#3 delta 95/102, Agent 5#10 ₩1,300/₩1,333, Agent 5#3 테스트 84/90, Agent 11#5 비용 마진 |
| **RULE-2** (HTML 주석 의도적) | 2건 | Agent 2#19 해결된 SC 주석 유지, Agent 14#21 주석 형식 미세 차이 |
| **RULE-4** (요약 vs 상세 차이) | 26건 | Agent 1#9~12 경미한 명확화, Agent 4#2/4/7/8 문서 구조, Agent 6#6/9/10/11, Agent 10#1/2, Agent 14#17/22/24 등 |
| **RULE-5** (선택적 항목 부재) | 5건 | Agent 8#5/6 프롬프트 초과, Agent 9#3 잉여 산출물, Agent 13#15/16 Supply Chain/Secret |
| **RULE-9** (외부 패키지 버전) | 1건 | Agent 10#9 mypy 상한 |
| **RULE-11** (행 순서 차이) | 1건 | Agent 6#9 Gate 순서 vs 체크리스트 순서 |
| **RULE-12** (섹션 깊이 차이) | 2건 | Agent 2#20/21 주석 형식 |
| **기타 (규칙 미적용 FP)** | 2건 | Agent 8#12 R5 정상 전파, Agent 12#8 Gate 위치 명확 |
| **합계** | **43건** | |

---

## 5. NEEDS_CLARIFICATION 해소 결과 (8건 → 7 REAL + 1 FP)

> VAMOS AI 프로젝트 맥락 기반으로 전수 결정 완료.

| # | Agent | 원# | 내용 | 최종 판정 | 결정 사유 |
|---|-------|-----|------|----------|----------|
| NC-1 | 1 | #6 | EventTypeRegistry 123 vs cl.rt.* 포함 134 | **REAL_ISSUE** (MED) | cl.rt.*는 RT-BNP 런타임 이벤트. 총수 포함 여부 명시 필요 |
| NC-2 | 3 | #2 | 변경이력 v21 건너뛰기 | **REAL_ISSUE** (LOW) | 의도적 스킵이라도 면책 주석 필요. 현재 미기재는 누락 |
| NC-3 | 4 | #5 | L1571 서술 잘림/불완전 | **REAL_ISSUE** (LOW) | v10 대량 추가(패턴 A) 과정의 편집 잔류물 |
| NC-4 | 4 | #6 | L1803 항목 설명 불완전 | **REAL_ISSUE** (LOW) | 동일. v10 대량 편집 잔류물 |
| NC-5 | 5 | #1 | SC-09 "§5=5개" 참조 모호 | **REAL_ISSUE** (MED) | 구현자 SOURCE_CONFLICT 해결 시 판단 불가. 테이블/행 특정 필요 |
| NC-6 | 11 | #9 | V1-Phase 6 병렬 실행 | **REAL_ISSUE** (MED) | V1 Phase 간 병렬/순차 규칙 미정의. 명확화 필요 |
| NC-7 | 13 | #14 | GDPR 적용 범위 | **FALSE_POSITIVE** | PART2 구현가이드 범위 밖. 한국 기반(KRW), 별도 컴플라이언스 영역 |
| NC-8 | 14 | #6 | config.v1.toml 이중 게시 | **REAL_ISSUE** (HIGH) | Agent 1 BLOCKER(autonomy_level 충돌)의 근본 원인. 정본 명시 필요 |

---

## 6. BLOCKER 13건 재확인 (전수 REAL_ISSUE)

| B-# | Agent | PART2 직접 확인 | 판정 |
|-----|-------|----------------|------|
| B-01 | 1 | L1529 "70/85/95%" vs L209 "80%/100%". 3단계↔2단계 충돌 | **REAL_ISSUE** |
| B-02 | 6 | L4228 "Loki+Grafana 배포" = V3 인프라. V2→V3 전환조건에 시간적 모순 | **REAL_ISSUE** |
| B-03 | 8 | V2-Phase 2 프롬프트 10/116 커버. v10 추가분 전혀 미반영 | **REAL_ISSUE** |
| B-04 | 11 | V1-Phase 2: 59개/2주. v10 추가 후 기간 미조정 | **REAL_ISSUE** |
| B-05 | 11 | V1-Phase 3: 59개/2주. 동일 과부하 | **REAL_ISSUE** |
| B-06 | 11 | V2-Phase 2: 105개/3주. 일 7개 항목 | **REAL_ISSUE** |
| B-07 | 12 | SelfCheckGate: plan 노드 5-Gate 순서에 나열 vs S6 verify 실행. 위치 모순 | **REAL_ISSUE** |
| B-08 | 12 | L1512 S3=120s vs L220 approval=600s. 파이프라인 타임아웃 충돌 | **REAL_ISSUE** |
| B-09 | 12 | FailureCode 36건↔Fallback 23건 매핑 테이블 완전 부재 | **REAL_ISSUE** |
| B-10 | 13 | v10 ~378건 추가 후 §6.3 테스트 ~84건 미갱신 | **REAL_ISSUE** |
| B-11 | 13 | V2-Phase 2: 116개 vs ~5개 테스트 (4.3%) | **REAL_ISSUE** |
| B-12 | 14 | §6.12 운영: DCL 이관 2건만. 전체 운영 정책 부재 | **REAL_ISSUE** |
| B-13 | 14 | V0/V1 모니터링 전략 부재. 32모듈 장애 감지 불가 | **REAL_ISSUE** |

---

## 7. 교차 패턴 재검증 (Phase 1 Summary §4 패턴 A~E)

| 패턴 | Phase 1 판정 | 재판정 | 비고 |
|------|-------------|--------|------|
| **A: v10 대량 추가 연쇄 미갱신** | 8건 ISSUE | **REAL** | 5개 영역(프롬프트/타임라인/테스트/체크리스트/가독성) 전수 확인. 가장 큰 구조적 문제 |
| **B: FIX-09 Gate 명칭 미전파** | ~6건 ISSUE | **REAL** | L3875/L3876/L3927/L3928 직접 확인. 4개소 미전파 |
| **C: §3(V1) 구조적 고립** | 7건 ISSUE | **REAL** | 균일성 매트릭스에서 5/7 하위구조 ✗ 직접 확인 |
| **D: V3 후반부 품질 저하** | 5건 ISSUE | **REAL** | 12×5 자기완결성 매트릭스: V3-PH2/3 평균 2.5/5 |
| **E: 운영/보안 인프라 부재** | 16건+ ISSUE | **REAL** | Agent 14 GAP-24 전수 REAL_ISSUE (모니터링/백업/롤백/알림/헬스체크) |

> **5개 교차 패턴 전수 REAL_ISSUE 확인**. Phase 2 수정 시 패턴 A(v10 연쇄)가 가장 높은 작업량.

---

## 8. Phase 2 수정 우선순위 (재정렬)

### Tier 1: 즉시 수정 (BLOCKER 13건)
1. **B-01**: 비용 알람 체계 통일 (70/85/95% 또는 80/100% 택일)
2. **B-02**: V2→V3 전환조건에서 "Loki+Grafana 배포" 제거 또는 V2 범위로 이동
3. **B-07**: SelfCheckGate 실행 위치 명확화 (plan vs verify)
4. **B-08**: S3 타임아웃(120s)과 승인 타임아웃(600s) 충돌 해소
5. **B-09**: FailureCode↔Fallback 매핑 테이블 작성
6. **B-03**: V2-Phase 2 프롬프트에 v10 추가 구현항목 반영
7. **B-04~06**: v10 추가 후 타임라인 재설계 (Phase 분할 또는 기간 확장)
8. **B-10~11**: §6.3 테스트 수 갱신 + V2-Phase 2 테스트 보강
9. **B-12~13**: 운영 섹션 신설 (모니터링/백업/인시던트)

### Tier 2: 구조 개편 (패턴 A — HIGH 20건+)
- v10 추가분 테이블 구조화 (서브그룹 헤더, 정보밀도 보강)
- 프롬프트 갱신 (V2/V3 커버리지 확장)
- 체크리스트 반영

### Tier 3: 전파 수정 (패턴 B — HIGH 6건)
- FIX-09 Gate 명칭 4개소 치환: "Trust Score"→"Content Quality", "Relevance"→"Consistency"

### Tier 4: §3 보강 (패턴 C — HIGH 5건)
- V1(§3)에 실행가이드/AI프롬프트/규칙/참조SOT/완료검증 추가

### Tier 5: 문서 품질 (패턴 D/E — MEDIUM 30건+)
- V3 프롬프트 분할 + 코드 예시 보충
- Glossary/Reading Guide 추가
- §1.3 공통규칙 프롬프트 전파

---

## 9. NEEDS_CLARIFICATION 해소 완료

NC-1 ~ NC-8 전수 결정 완료 (VAMOS AI 프로젝트 맥락 기반):
- **REAL_ISSUE 추가**: 7건 (NC-1~6, NC-8)
- **FALSE_POSITIVE 추가**: 1건 (NC-7 GDPR)
- **최종 REAL_ISSUE**: 179건 (Phase 2 수정 대상)

---

## 10. Phase 1.5 완료 상태

| 항목 | 상태 |
|------|------|
| 전체 ISSUE 재판정 (223건) | **완료** |
| Spot-check (21건, 목표 15건+) | **완료** (오판율 0%) |
| BLOCKER 전수 확인 (13건) | **완료** (13/13 REAL_ISSUE) |
| 교차 패턴 재검증 (5개) | **완료** (5/5 REAL) |
| FP 방어 규칙 적용 | **완료** (RULE-1~14 중 7개 규칙 활용, 43건 FP) |
| NC 해소 (8건) | **완료** (7 REAL + 1 FP) |

> **Phase 1.5 판정**: PASS — Phase 2 진입 가능. REAL_ISSUE 179건 확정.

---

*산출물: D:\VAMOS\04. 구현단계\v11_results\phase15\v11_adversarial_report.md*
