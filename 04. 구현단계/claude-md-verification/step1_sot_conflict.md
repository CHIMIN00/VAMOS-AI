# Step 1 — SOT 원본 모순 탐지 보고서 (/claude-md-sot-conflict)

- **실행일**: 2026-06-11
- **대상**: `D:\VAMOS\docs\sot\*.md` 68개 (읽기 전용 — 수정 0건, RULE-C3/C4 준수)
- **방법**: 핵심 수치 10개 항목 Grep 전수 교차 수집 → 값 비교 → 불일치 CONFLICT 기록
- **정본 우선순위**: RULE 1.3 > PLAN 3.0 > DESIGN 2.0 LOCK > DESIGN 본문 > 스키마

---

## A. 검사한 핵심 수치 목록 및 일치 여부

| # | 항목 | 기대값 | SOT 교차 검증 결과 | 판정 |
|---|------|--------|--------------------|------|
| 1 | 모듈 수 | I-모듈 25 / Named 81 / COND 106 / 전체 187 | I-25개·81개 일관 (CLAUDE.md L96, MASTER_SPEC L172, D2.0-02 L4190). **106(COND)/187(전체)은 docs\sot 내 미출현** — SOT의 106은 AI Investing 항목 수(S7I-001~106)뿐. 구체계 잔존 1건 | ⚠️ CONFLICT-008 + 미출현 주의 |
| 2 | 비용 한도 | V1 ₩40,000/₩1,300 · V2 ₩93,000/₩3,100 · V3 ₩266,000/₩8,900 | BASE-1.3 L198-211 = D2.0-01 L214-216 = D2.0-07 L643-645 = PHASE_B4 L275 = MASTER_SPEC L1088-1090 등 전면 일치. 예외 1건(V2를 ₩40,000으로 표기) | ⚠️ CONFLICT-006 |
| 3 | Self-check | P0 70/P1 75/P2 80, soft loop 1회 | D2.0-02 §7.53-1 L1828-1830(LOCK) = PHASE_B4 L334-337 = CLAUDE.md L702-705 일치. soft loop 1회 전 문서 일치. PLAN-3.0 내부에 70/80 혼용 | ⚠️ CONFLICT-003 |
| 4 | QoD | <0.4 금지 / <0.7 보류, 5요소 가중치 | 0.4/0.7 일치 (PLAN-3.0 L250-251, D2.0-06 L268-269/743, CLAUDE.md L605, MASTER_SPEC L1001). 가중치는 4요소/5요소 병존 잔존 | ⚠️ CONFLICT-005 |
| 5 | Gate | 5-Gate (Policy→Approval→Cost→Evidence→SelfCheck) | 5-Gate 정의 일치 (D2.0-02 §8.1 L2531, D2.0-07 L969). 단 4-게이트 열거·G0~G4 라벨 혼용 잔존 | ⚠️ CONFLICT-001/002 |
| 6 | 동시성 | BLUE_NODES 3, TOOLS 5 | D2.0-02 L340, CLAUDE.md L241/L708, MASTER_SPEC L1519, BEGINNER L1379, READINESS_GUIDE L368 전면 일치 | ✅ 일치 |
| 7 | MCP max_retries | V1/V2=2, V3=3 | V1/V2=2 일치. **V3=3은 PHASE_B4 §3.9 L359에만 존재** — 인용된 정본(D2.0-03 L428, MASTER_SPEC L572/L580)은 2만 규정, B4 V3 예시 config에 3 미반영 | ⚠️ CONFLICT-004 |
| 8 | Hybrid Search | BM25 0.3/Vector 0.7, Top-K 20, threshold 0.75 | alpha=0.3(BM25)/0.7(Vector) 일치 (D2.0-06 L785, STEP7_R1 L378, D2.0-05 L915). Top-K는 컨텍스트별 의도적 상이(L2 top_k=10 [D2.0-06 L184] / L3·API 5 [L242, B1 L821] / rerank 1차 후보 20 [L859]). **threshold 0.75는 SOT 미출현**(D2.0-06 L1928의 cosine>0.75는 PKM 노트 추천용 별개) | ✅ 가중치 일치 / ⚠️ Top-K·0.75 표기 주의 |
| 9 | 캐시·승인·턴 | cosine 0.95, 600s/10분(P2 300s/5분), 턴 P0=5/P1=10/P2=20 | 0.95 LOCK 전면 일치 (D2.1-D6 L193, PHASE_B4 L540, AC-D6-010). 600s/10분 일치 (D2.0-07 L753, PHASE_B4 L344/349, SDAR L1609). P2 5분=300s 일치 (D2.0-07 L106, CLAUDE.md L707). 턴 상한 일치 (D2.0-05 L701, CLAUDE.md L243) | ✅ 일치 |
| 10 | config LOCK 키 분모 | 20 | CLAUDE.md L686 §20 표 실측 20행 ✓, READINESS_REVIEW L255, READINESS_GUIDE L337 모두 "20개" 일치 | ✅ 일치 (단 키 내부 값 1건 충돌 → CONFLICT-007) |

---

## B. CONFLICT 목록

### CONFLICT-001 — 5-Gate 구성 열거 불일치 (SelfCheckGate 누락 4-게이트 표기)
| 측 | 파일 | 라인 | 값 |
|----|------|------|-----|
| 정본 | D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md | L2531-2533 | §8.1 5-Gate 체계 정의 (LOCK): 3-Gate + ApprovalGate + SelfCheckGate = 5-Gate |
| 정본 | D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md | L969 | PolicyGate → ApprovalGate → CostGate → EvidenceGate → SelfCheckGate |
| 불일치 | D2.0-01_01. VAMOS_DESIGN_2_0_OVERVIEW.md | L208 | "모든 액션은 Policy → Approval → Cost → Evidence 게이트를 반드시 통과" (4개, SelfCheck 누락) |
| 불일치 | CLAUDE.md (sot) | L236 | "Gate 우회 불가: Policy→Approval→Cost→Evidence 필수 통과" (자체 L84-92 표는 5개 — 내부 비일관) |
| 불일치 | VAMOS_MASTER_SPECIFICATION.md | L1512 | 동일 4-게이트 열거 |
| 불일치 | VAMOS_BEGINNER_GUIDE.md | L1376 | 동일 4-게이트 열거 |

**판정**: DESIGN 2.0 LOCK(D2.0-02 §8.1) 정본 → **5-Gate**. 4-게이트 표기는 [OC-06] SelfCheckGate 추가 이전 잔존 문구. CLAUDE.md 작성 시 반드시 5개 열거.

### CONFLICT-002 — "5-Gate" 명칭/라벨 혼용 (G0~G4 충돌)
| 측 | 파일 | 라인 | 값 |
|----|------|------|-----|
| 정본 | D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md | L2531 | 5-Gate = Policy/Approval/Cost/Evidence/SelfCheck (이름 기반) |
| 별개 체계 | PLAN-2.0_VAMOS_PLAN_2.0_.md | L3094 | Cloud Library Layer 8 "5-Gate 검증 체계(G0~G4)" — 데이터 품질 게이트 |
| 별개 체계 | D2.1-D3_D3_SCHEMA_BLUE_NODES.md | L18, L315 | CloudLibraryGateResultSchema — S-5 Gate G0-G4 |
| 혼용 | VAMOS_AGENT_TEAMS_SPEC.md | L50 | "**5-Gate 안전장치(G0~G4)**가 전 파이프라인에 내장 … 정책/비용/승인 제어" — 안전 5-Gate에 Cloud Library 라벨(G0~G4)을 부착 |
| 혼용 | VAMOS_STEP7_A-E_상세명세서.md | L502, L977 | "5-Gate 시스템 — Policy/Cost/Evidence 5중 게이트" (5중이라 하면서 3개만 열거) |

**판정**: D2.0-02 §8.1 명칭 정본. "G0~G4"는 Cloud Library S-5 검증 게이트 전용 라벨로 한정해야 함. CLAUDE.md에서 두 체계를 구분 표기 필요.

### CONFLICT-003 — Self-check 임계값: PLAN-3.0 내부 70/80 혼용 vs DESIGN 70/75/80
| 측 | 파일 | 라인 | 값 |
|----|------|------|-----|
| 정본 | D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md | L1828-1830 | §7.53-1 (LOCK) P0≥70 / P1≥75 / P2≥80 |
| 일치 | PHASE_B4_CONFIG_SPEC.md | L334-337 | threshold_p0=70/p1=75/p2=80, soft_loop_max=1 |
| 불일치 | PLAN-3.0_VAMOS_PLAN_3_0_최종완성본.md | L3760 | "품질 부족(Self-check < 70)" (P0 70 기준 사용) |
| 불일치 | PLAN-3.0_VAMOS_PLAN_3_0_최종완성본.md | L3776 | "루프 종료조건: Self-check ≥ 80" (위험도 무관 고정 80) |
| 불일치 | PLAN-3.0_VAMOS_PLAN_3_0_최종완성본.md | L6604 | "Self-check 점수가 80점 이상" |
| 불일치(레거시) | PLAN-2.0_VAMOS_PLAN_2.0_.md | L332 | "Self-check < 80" |

**판정**: 우선순위상 PLAN 3.0 > DESIGN이나, PLAN-3.0 자체가 70(L3760)과 80(L3776)을 혼용해 내부 비일관. D2.0-02 §7.53-1이 "PLAN의 '고정 관문' 원칙 유지 + 런타임 위험도 가변(70/75/80)"으로 명시 조정(L1823-1824)했으므로 **운영 정본 = 70/75/80 (D2.0-02 LOCK)**. PLAN-3.0 L3776의 80은 P2 케이스 또는 보수적 단순화 표현으로 해석.
※ 참고: D2.0-02 L1863 "P0:60/P1:70/P2:80"은 §7.53-2.2 **(KEEP) 대안, Not Default** 명시 → 모순 아님.

### CONFLICT-004 — MCP max_retries V3=3의 근거 불일치 + 예시 config 자기모순
| 측 | 파일 | 라인 | 값 |
|----|------|------|-----|
| 주장 | PHASE_B4_CONFIG_SPEC.md | L359 | 표: max_retries V1=`2` / V2=`2` / V3=`3` — "D2.0-03/MASTER_SPEC 정본" 주석 |
| 인용된 정본 | D2.0-03_03. VAMOS_DESIGN_2.0_BLUE_NODES.md | L428, L1199 | max_retries = 2 (버전 구분 없음, V3=3 근거 부재) |
| 인용된 정본 | VAMOS_MASTER_SPECIFICATION.md | L572, L580 | "최대 2회" / max_retries = 2 (버전 구분 없음) |
| 자기모순 | PHASE_B4_CONFIG_SPEC.md | L638, L754 vs L825-830 | V1/V2 예시 config max_retries=2 명기, **V3 예시 config [mcp] 블록(L829-830)에는 max_retries 누락** → Pydantic 기본값 2(L1118) 적용 시 표(V3=3)와 모순 |

**판정**: 인용 구조상 PHASE_B4가 D2.0-03을 정본이라 인용하면서 D2.0-03에 없는 V3=3을 추가한 형태. DESIGN(D2.0-03) 우선 적용 시 전 버전 2. V3=3을 유지하려면 D2.0-03 측 버전별 명세 보강 + B4 V3 예시 config에 `max_retries = 3` 명기가 필요. **기록만 — 수정 금지**. CLAUDE.md에는 "V1/V2=2 (D2.0-03 LOCK), V3=3 (PHASE_B4 §3.9 단독 표기, 근거 불일치 미해결)"로 주의 표기 권장.

### CONFLICT-005 — QoD 가중치 4요소 vs 5요소 (V1-006 물리 수정 미반영 잔존)
| 측 | 파일 | 라인 | 값 |
|----|------|------|-----|
| 정본 | PLAN-3.0_VAMOS_PLAN_3_0_최종완성본.md | L239-243 | 5요소: Accuracy 0.30 + Relevance 0.25 + Completeness 0.20 + Safety 0.15 + Efficiency 0.10 |
| 확정 기록 | VAMOS_IMPLEMENTATION_READINESS_GUIDE.md | L557-559 | V1-006: "PLAN-3.0 5요소 공식이 정본, MASTER_SPEC §8.8 수정" 확정 |
| 불일치 잔존 | VAMOS_MASTER_SPECIFICATION.md | L990 | qod_score = relevance×0.30 + accuracy×0.25 + freshness×0.25 + completeness×0.20 (4요소, 미수정) |
| 불일치 잔존 | VAMOS_MASTER_SPECIFICATION.md | L1542 | "QoD 가중치: relevance 0.30 + accuracy 0.25 + freshness 0.25 + completeness 0.20 (DEC-014)" |
| 컨텍스트 분리 | D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md | L1333 | SourceQoD(소스 품질) 4요소 공식 — RAG 소스 전용 |
| 병기 | CLAUDE.md (sot) | L269-270 | L269 DEC-014 "QoD 가중치(RAG)" 4요소 + L270 "QoD 5요소(PLAN정본)" — 용도 라벨로 구분 시도 |

**판정**: **출력 QoD = PLAN-3.0 5요소 정본** (RULE 1.3 다음 순위 PLAN 3.0). 4요소는 SourceQoD(RAG 소스 품질, D2.0-06 L1333)로 한정 시에만 유효. MASTER_SPEC L990/L1542는 용도 한정 없이 "QoD 가중치"로 표기 → V1-006 확정 후 물리 수정 미반영 상태. CLAUDE.md에는 "출력 QoD 5요소(정본) / SourceQoD(RAG) 4요소" 이원 명기 필수.

### CONFLICT-006 — V2 비용 상한 ₩93,000 vs ₩40,000 표기
| 측 | 파일 | 라인 | 값 |
|----|------|------|-----|
| 정본 | BASE-1.3_VAMOS_RULE_1.3_BASE.md | L204-205 | V2: 일 3,100원 / 월 93,000원 (ABSOLUTE LOCK) |
| 불일치 | VAMOS_STEP7_보강_통합명세서.md | L526 | "I-9 비용 상한 → **V2 월간 ₩40,000 예산** 내 스케일링" |
| 모호(참고) | D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md | L1256 | J-095 "V2 3개월 구현 항목 … 비용: 월 ≤₩40,000" — L1254 [D8-M10]은 "V1 ₩40,000 내 서브예산"으로 주석되어 V2 항목과 라벨 불일치 |

**판정**: RULE 1.3(BASE-1.3 §5) 정본 → **V2 = ₩93,000/월**. 보강_통합명세서 L526의 ₩40,000은 멀티모달/스케일링 서브예산 의도로 추정되나 "비용 상한"으로 표기되어 충돌. (L673/L1295의 ₩20,000~40,000은 사용자 대상 가격(pricing)으로 PLAN-3.0 L6865가 LOCK 상한과 별개임을 명시 → 모순 아님.)

### CONFLICT-007 — Embedding 차원 V1 기본값: 1024(LOCK) vs 256
| 측 | 파일 | 라인 | 값 |
|----|------|------|-----|
| 정본 | CLAUDE.md (sot) | L692 | config LOCK: embedding.dimension = **1024** (LOCK) |
| 정본 | D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md | L1338 | "V1 기본: 1024차원 (BGE-M3)" (§기본값 결정, L1487-1488 BGE-M3 단일 기본값 UPDATED) |
| 불일치 | D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md | L779 | S7D-027: "V1 기본: 256차원 (Matryoshka)" |
| 불일치 | D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md | L852, L854 | S7D-014: "V1 기본: 256차원" + 자동 선택(문서 수 <5,000 → 1024 / >5,000 → 256) |

**판정**: DESIGN LOCK + 결정 섹션(D2.0-06 L1338/L1487) 및 config LOCK 20 정본 → **V1 기본 1024차원**, 256은 Matryoshka 경량 옵션. D2.0-06 내부(STEP7 편입분 S7D-014/027)가 결정 섹션과 자기모순. config LOCK 키 20개 중 1개(embedding.dimension)의 값 충돌이므로 항목 10에도 영향.

### CONFLICT-008 — I-모듈 분모: 25(정본) vs 구체계 24/21 잔존
| 측 | 파일 | 라인 | 값 |
|----|------|------|-----|
| 정본 | D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md | L4190-4192 | "I-모듈 25개(I-1~I-25)" — 정본: D2.0-01 §5.6 LOCK 인덱스 |
| 보호됨 | PLAN-3.0_VAMOS_PLAN_3_0_최종완성본.md | L465, L4737 | 정본 고지/LEGACY 배너 존재 (구 번호 I-1~I-21 경고) |
| 불일치(배너 없음) | PLAN-2.0_VAMOS_PLAN_2.0_.md | L58 | "예: I-1, I-2 … **I-24 (I-모듈 전체)**" — 25개 정본과 불일치, 경고 주석 부재 |

**판정**: D2.0-01 §5.6 LOCK → **25개 정본**. PLAN-3.0/D2.0-02 쪽은 이미 정본 고지로 관리 중(X-01/BLK-1 해소 이력: READINESS_REVIEW L44/L64). PLAN-2.0 L58만 무배너 잔존 — 단 PLAN-2.0 자체가 PLAN-3.0으로 대체된 구버전 문서.

---

## C. 미출현/주의 항목 (모순은 아니나 CLAUDE.md 작성 시 검증 필요)

| 항목 | 내용 |
|------|------|
| 모듈 분모 106/187 | "COND 106 / 전체 187"은 docs\sot 68개 파일 어디에도 모듈 수로 미출현 (`\b187\b` 0건). SOT 정의 분모는 **81개(I25+E16+S8+A7+B6+C7+D6+EVX6)** (CLAUDE.md L96, MASTER_SPEC L172). 106은 AI Investing 항목 수(STEP7-I L56 등)로만 존재 — CLAUDE.md에 106/187 기재 시 SOT 근거 부재 |
| Hybrid threshold 0.75 | SOT 미출현. D2.0-06 L1928의 cosine>0.75는 PKM 관련 노트 추천 임계값(별개), PLAN-3.0 L343의 0.75는 DomainScore. 하이브리드 검색 threshold로 0.75를 CLAUDE.md에 기재하려면 근거 보강 필요 |
| Top-K | 단일값 아님(의도적 분화): L2 top_k=10 기본(D2.0-06 L184), L3/B1 API top_k=5(L242, PHASE_B1 L821), Cross-Encoder rerank 1차 후보 top-20(L859, 최종 top-3~5). "Top-K 20" 단독 표기는 rerank 후보 수로 한정해야 함 |
| 4중 인덱스 가중치 | D2.0-06 L1127 vector 0.35/bm25 0.25/graph 0.25/summary 0.15는 V2 4-Index Fusion 별개 체계 — 2-way alpha=0.3(L785)과 혼동 금지 |
| 승인 타임아웃 이원화 | 일반 600s/10분 + P2(HITL 고위험) 300s/5분 (D2.0-07 L106 정본 명시, CLAUDE.md L706-707 일치) — 단일 "600s"로만 쓰면 불완전 |

---

## D. 종합

- **검사 항목**: 10개 영역 (모듈 수/비용/Self-check/QoD/Gate/동시성/max_retries/Hybrid/캐시·승인·턴/config LOCK)
- **완전 일치**: 동시성(3/5), cosine 0.95, 승인 600s+300s, 대화 턴 5/10/20, soft loop 1회, QoD 임계 0.4/0.7, 비용 한도 3단(예외 1건 제외), config LOCK 분모 20
- **모순: 8건 (CONFLICT-001 ~ CONFLICT-008)** — 수정 0건 (기록만, RULE-C4)
- **미출현 주의: 2건** (모듈 분모 106/187, Hybrid threshold 0.75 — CLAUDE.md 기재 전 근거 확보 필요)
