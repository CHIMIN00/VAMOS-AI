# CLAUDE.md 검증 Step 4 — /claude-md-cross-examine 결과 (근거 교차 신문)

> 실행일: 2026-06-11 | 대상: `D:\VAMOS\CLAUDE.md` §7(7.1~7.6 전 행) + §8 Non-goal 7행 + §15 메모리 계층 수치 + §20 config LOCK 20키
> 방법: Agent A(CLAUDE.md 주장) ↔ Agent B(출처 파일·라인 직접 Read/Grep 확인). SOT(`D:\VAMOS\docs\sot\`) 및 SOT 2 정본에서 발견 시 CONFIRMED, 미발견 시 SUSPECT.
> CLAUDE.md·SOT 무수정 — 기록만.

**총괄: 검증 91건 중 CONFIRMED 90 / SUSPECT 1**

---

## 1. §7.1 아키텍처 LOCK (11행) — CONFIRMED 10 / SUSPECT 1

| # | 항목 | 판정 | 출처 (파일 · 라인) |
|---|------|------|--------------------|
| 1 | DEC-001 = 문서 우선순위 | **SUSPECT** | 규칙 자체(RULE>PLAN>DESIGN LOCK>본문>스키마)는 D2.0-01 L64·L752에 정본 존재(CONFIRMED). 그러나 **SOT의 실제 DEC-001은 "에이전트 프레임워크 확정(자체 프레임워크, LangChain 등 import 금지)"** (D2.0-02 §0.6-A L67-74). READINESS_GUIDE L601도 DEC-001을 "LangChain import 금지"로 기술. "문서 우선순위 = DEC-001"이라는 라벨 매핑은 SOT/SOT2 어디에서도 미발견 → 라벨 불일치 |
| 2 | DEC-002 LangChain import 금지(패턴만 참조) + Allowlist(V1-009) | CONFIRMED | D2.0-02 §0.7-A L85-90(패턴만 참조 확정, 직접 import 금지) + READINESS_GUIDE L601-603·L1087(Allowlist: langchain-core/community/openai adapter only, V1-009). ⚠️비고: D2.0-02 L69는 "DEC-002 LOCK"을 LangGraph 허용에도 사용 — SOT 원문 내 라벨 혼용 존재 |
| 3 | DEC-003 도구 승인 Allowlist | CONFIRMED | D2.0-05 L109 "결정 완료(DEC-003): 승인 모드 = Allowlist 자동승인 확정 (LOCK)", D2.0-07 L1208 |
| 4 | DEC-017 MCP Streamable HTTP | CONFIRMED | D2.0-03 L916(LOCK 확정)·L424(transport="streamable_http"), D2.0-01 L1195 |
| 5 | 변경관리(삭제 금지/창작 금지/Major 07 Approval) | CONFIRMED | D2.0-01 L82-84 |
| 6 | E-*/EVX-* 분리, E 변형 금지 | CONFIRMED | D2.0-01 L87-93·L119-121 |
| 7 | S-#(모듈) / S#_(상태) 분리 | CONFIRMED | D2.0-01 L100·L124-125·L756-760 |
| 8 | A-6=Federated / A-7=Remote Executor (LOCK) | CONFIRMED | D2.0-01 L102-106·L131-134 |
| 9 | Monorepo (PHASE_B2 정본) | CONFIRMED | PHASE_B2 L25 "결정: Monorepo (LOCK)"·L34 |
| 10 | LangGraph Agent Workflow 프레임워크 (LOCK) | CONFIRMED | D2.0-02 L69(워크플로우 오케스트레이션 전용 LOCK)·L609, D2.1-A1 L310 |
| 11 | config 포맷 config.toml (PHASE_B4 정본) | CONFIRMED | PHASE_B4 전체(§3 config.toml 블록 L152 등), D2.0-04 L1068 |

## 2. §7.2 핵심 엔진 LOCK (10행) — CONFIRMED 10

| # | 항목 | 판정 | 출처 |
|---|------|------|------|
| 12 | Decision Lock(한 시점/한 컨텍스트/한 결론, locked=true) | CONFIRMED | D2.0-02 L43·L536(원칙)·L564·L1743·L2876·L2898(locked=true), L3228; S3_DECISION_LOCKED 상태 |
| 13 | Gate 우회 불가 | CONFIRMED | D2.0-07 L55(개별 로직으로 Gate 대체 금지 — 우회 위험 명시) |
| 14 | Self-check 임계값 P0:70/P1:75/P2:80 | CONFIRMED | D2.0-02 L1828-1830·L1858, PHASE_B4 L327-329 |
| 15 | Soft loop 자동 1회만 | CONFIRMED | D2.0-02 L326·L2573(LOCK: 옵션 A), PHASE_B4 L330 |
| 16 | L2 저장 기본 "승인 필요" | CONFIRMED | D2.0-02 L2565(LOCK: 옵션 A), D2.0-06 L206(S03-MOD-001) |
| 17 | Docker 샌드박스 필수(네트워크 차단, 30초) | CONFIRMED | D2.0-02 §1.3-A L175-181(네트워크 기본 차단, 실행 30초 제한) |
| 18 | MAX_CONCURRENT_BLUE_NODES=3, TOOLS=5 | CONFIRMED | D2.0-02 §2.2-A L340 |
| 19 | Multi-Brain Failover GPT-4o→Claude→Ollama(3회 타임아웃) | CONFIRMED | D2.0-02 §11.1.2 L3884-3890(연속 3회 타임아웃 또는 5xx) |
| 20 | 대화 턴 상한 P0=5/P1=10/P2=20 | CONFIRMED | D2.0-05 L701, MASTER_SPEC §7.12 L870-871(LOCK), AGENT_TEAMS L2002(LOCK-AT-009) |
| 21 | TEE 최대 반복 P0=3/P1=5/P2=10 | CONFIRMED | D2.0-05 L735 |

## 3. §7.3 비용/안전 LOCK (11행) — CONFIRMED 11

| # | 항목 | 판정 | 출처 |
|---|------|------|------|
| 22 | V1 ₩40,000/월($30), ₩1,300/일($1), Mini 90%+ | CONFIRMED | BASE-1.3 L197-201, PHASE_B4 L274-275 |
| 23 | V2 ₩93,000/월($70), ₩3,100/일($2.3), Mini 60~70%/Main 30~40% | CONFIRMED | BASE-1.3 L203-207 |
| 24 | V3 ₩266,000/월($200), ₩8,900/일($6.7), Main 중심·플래그십 적극 | CONFIRMED | BASE-1.3 L209-213, D2.0-01 L1524 |
| 25 | Downshift 80% warn/force_mini, 100% block | CONFIRMED | D2.0-07 L14·L216·L1635-1636(LOCK), PHASE_B4 L276-277 |
| 26 | RBAC OWNER(L3,P2,₩266K)/ADMIN(L2,P2,₩93K)/OPERATOR(L1,₩40K)/VIEWER(L0,₩0) | CONFIRMED | MASTER_SPEC §9.2 L1038-1045(LOCK, 표 완전 일치), D2.0-07 L510-518. ⚠️비고: D2.0-07 L510은 "정본: CLAUDE.md §7.3 LOCK"이라 역참조(순환) — 실질 정본은 MASTER_SPEC §9.2 |
| 27 | Autonomy 기본 L1(SUPERVISED), L3에서도 자동불가 항목 | CONFIRMED | D2.0-07 L430·L434-435, MASTER_SPEC L1052·L1056 |
| 28 | Guardrails 4-Layer(NeMo/Guardrails AI/LlamaGuard/사후감사 V2+) | CONFIRMED | D2.0-07 §1.1 L94-96 + §15.8.1 L1743-1750(L4 사후감사), PHASE_B4 L303·L317(layer4 V2+ 전용), READINESS L577 |
| 29 | P2 자동 OFF: 세션 종료 시 즉시 OFF | CONFIRMED | BASE-1.3 §3.3 L145, D2.0-07 L107, D2.0-03 L78·L1545. ⚠️비고: "(LOCK: Option A)" 라벨 자체는 SOT에서 미발견(내용은 완전 일치) |
| 30 | Non-goal 7개 | CONFIRMED | BASE-1.3 §2 L96-122 |
| 31 | 7개 불변 구역(safety_rules~user_consent) | CONFIRMED | BASE-1.3 L612(7개 불변 구역 하드코딩, 동일 목록) |
| 32 | 승인 타임아웃 10분 미응답→자동 거부 | CONFIRMED | D2.0-07 L753, PHASE_B4 L344(timeout_s=600) |

## 4. §7.4 데이터/인프라 LOCK (14행) — CONFIRMED 14

| # | 항목 | 판정 | 출처 |
|---|------|------|------|
| 33 | DEC-004 하이브리드 RAG(V1 64%+/V2 83%+/V3 90%+) | CONFIRMED | D2.0-06 L1622-1624(단계·수치 일치)·§9.x L1477(DEC-004 LOCK) |
| 34 | DEC-005 BGE-M3(로컬,1024dim)/text-embedding-3-small | CONFIRMED | D2.0-06 L153·§9.y L1486-1494(UPDATED), PHASE_B4 L185-186 |
| 35 | DEC-010 QoD 0.0~1.0 | CONFIRMED | D2.0-06 L1331·§9.z L1498, D2.0-04 L309(DEC-010 LOCK) |
| 36 | DEC-014 QoD 가중치(RAG) rel.30+acc.25+fresh.25+comp.20 | CONFIRMED | D2.0-06 L1332-1333(공식 일치) |
| 37 | QoD 5요소(PLAN정본) Acc.30+Rel.25+Comp.20+Saf.15+Eff.10 | CONFIRMED | PLAN-3.0 L237-243(표 완전 일치) |
| 38 | Semantic Cache cosine ≥ 0.95 | CONFIRMED | D2.0-06 L751, PHASE_B4 L540·L547(LOCK) |
| 39 | Vector DB V1=Chroma/V2+=Qdrant | CONFIRMED | PHASE_B4 L204(enum), D2.1-D6 L135, A1 COMBO |
| 40 | RAG 6단계 + Chunk 300~500tok | CONFIRMED | D2.0-06 §1.1 L71-73(6단계 LOCK)·L687(한국어 300~500 토큰/청크) |
| 41 | 병렬 실행 상한 3 (LOCK) | CONFIRMED | D2.0-01 §7.4 L868-869(LOCK), D2.0-04 L954(max_parallel_tasks=3) |
| 42 | 설정 우선순위 ENV > config.toml > default | CONFIRMED | D2.0-04 L1068(환경변수 > .env > config.toml > 기본값)·L505 |
| 43 | 로깅 JSON Structured(평문 금지, trace_id 필수) | CONFIRMED | D2.0-04 §8.3 L847, MASTER_SPEC §6.10 L760-762(평문 금지 LOCK), PHASE_B4 L466 |
| 44 | 네이밍(lower.dot/UPPER_SNAKE/FB_/S#_/S-#) | CONFIRMED | D2.0-04 L817-819·L941-943, D2.0-01 L756-760 |
| 45 | Hybrid Search BM25 0.3+Dense 0.7, Top-K 20, Rerank Top 5, threshold 0.75 | CONFIRMED | alpha=0.3(BM25): D2.0-06 S7D-012 L785·L1104; Top-K 20·rerank top-3~5: S7D-018 L859-862; alpha 이중표기: GLOSSARY_CROSS_DOMAIN L179(LOCK-AX-06 정본). ⚠️비고: **threshold 0.75는 D2.0-06 본문에 미기재** — 실정본은 SOT2 6-4 AUTHORITY_CHAIN.md L39 LOCK-MR-009(0.75, ←S7D-018·PART2 L2038) + 종합계획서 L96. CLAUDE.md의 출처 표기("정본 D2.0-06 S7D-012/S7D-018")가 threshold에 한해 부정확하나 값 자체는 SOT2 정본 확인 |
| 46 | MCP max_retries V1/V2=2, V3=3 | CONFIRMED | PHASE_B4 §3.9 L359(2/2/3, exponential backoff 1s→2s, V3 +4s)·L638·L754 |

## 5. §7.5 Self-evo LOCK (4행) — CONFIRMED 4

| # | 항목 | 판정 | 출처 |
|---|------|------|------|
| 47 | 제안만 가능, 자동 적용 금지 | CONFIRMED | BASE-1.3 §(C) L85(제안만 가능)·L86(승인 필수), PLAN-3.0 L361(자동 복구 불허) |
| 48 | 허용 6개(프롬프트/도구 조합/메모리 관리/출력 포맷/워크플로우 순서/모델 선택) | CONFIRMED | BASE-1.3 L611 "6개 허용 도메인 화이트리스트" — 목록 완전 일치. (참고: BASE §6.1 L224-230에는 별도 관점의 6개 개선 범위도 존재) |
| 49 | 불변 7개(정체성/Non-goal/법규윤리/비용상한/승인구조/P0도메인/P2생성활성화) | CONFIRMED | BASE-1.3 §6.2 L234-241 — 7항목 완전 일치 |
| 50 | 롤백 후 14일 재적용 금지 | CONFIRMED | PLAN-3.0 §8.6.6 L359(14일간 재적용 금지). 비고: L191의 "1 스프린트(2주)" 표기와 동치 |

## 6. §7.6 UI/UX LOCK (6행) — CONFIRMED 6

| # | 항목 | 판정 | 출처 |
|---|------|------|------|
| 51 | Tauri 2.0 + React 18 (V2: +PWA) | CONFIRMED | D2.1-A1 L31(LOCK)·L164-165·L238(V2 PWA 병행), PHASE_B3 L50-51(react ^18.3.0) |
| 52 | 2-View: Builder + Hologram | CONFIRMED | D2.0-08 L56-57(2-View 분리 원칙)·L106-107·§2.1/§2.2 |
| 53 | 3-Panel: Left(Navigation/Timeline)+Center(Canvas/Stream)+Right(Control/HUD) | CONFIRMED | D2.0-08 L57(3단 패널 고정)·§3 L311 + L157-237(Left Navigation&Context/Timeline, Center Main Canvas/Stream Canvas, Right Glass HUD) |
| 54 | P2 재확인 모달 (DEC-011) | CONFIRMED | D2.0-08 L548-550·L1439(DEC-011: A 모달 — 화면 중앙) |
| 55 | 비용 경고 80%=#FBBF24 / 100%=#EF4444 (DEC-015) | CONFIRMED | D2.0-08 L544-545(헥스코드 일치)·L1440 |
| 56 | ORANGE #F97316 / BLUE NODE #00F6FF | CONFIRMED | D2.0-08 L1450-1451 |

## 7. §8 Non-goal 7행 — CONFIRMED 7

| # | 항목 | 판정 | 출처 (BASE-1.3 §2, L96-126 + 대응 L129~) |
|---|------|------|------|
| 57 | 2.1 실거래/주문/계좌/API 연동 | CONFIRMED | BASE-1.3 L98 |
| 58 | 2.2 불법 행위/해킹/권한 상승 | CONFIRMED | BASE-1.3 L102 |
| 59 | 2.3 의료/법률 단정적 판단/대리 결정 | CONFIRMED | BASE-1.3 L106 |
| 60 | 2.4 민감 개인정보 장기 저장 | CONFIRMED | BASE-1.3 L110 |
| 61 | 2.5 저작권/약관 위반 | CONFIRMED | BASE-1.3 L114 |
| 62 | 2.6 P2 도메인 자동 생성 금지 | CONFIRMED | BASE-1.3 L118 |
| 63 | 2.7 위험 기능 자동 실행 금지 | CONFIRMED | BASE-1.3 L122 |

## 8. §15 메모리/저장 계층 수치 (8건) — CONFIRMED 8

| # | 항목 | 판정 | 출처 |
|---|------|------|------|
| 64 | L0 Session 7일(최대 30일), B-4 Working | CONFIRMED | PLAN-3.0 L99(기본 7일, +7일 연장, 최대 30일)·L2668, D2.0-06 §2.1 L128(B-4, 세션 종료 시·최대 30일) |
| 65 | L1 Project 90일(연장 가능), B-1 Episodic | CONFIRMED | D2.0-06 L129(90일 TTL, 30일 연장 가능) |
| 66 | L2 무기한, B-3 Semantic, V1 OFF/V2 제한(승인)/V3 ON | CONFIRMED | D2.0-06 L130(무기한)·L200(V1 비활성)·L206(V2 제한+저장 시 승인 필수)·L209(V3) |
| 67 | L3 무기한, B-2 Procedural, V1 OFF/V2 제한/V3 ON | CONFIRMED | D2.0-06 L131·§2.4.2-A L239-241 |
| 68 | project_id 필수 + 프로젝트 간 혼합 금지 | CONFIRMED | D2.0-06 L55(RULE 1.3 §7.2 근거) |
| 69 | QoD < 0.4 → L2 벡터삽입 금지, < 0.7 → 출력 보류 | CONFIRMED | D2.0-06 L268-269·L743, MASTER_SPEC L1001(문구 그대로) |
| 70 | PII 마스킹 V1=정규식, V2+=NER 모델+문맥 분류기 | CONFIRMED | MASTER_SPEC L1011(문구 그대로), D2.0-06 L595·L601 |
| 71 | 검색 순서: 현재 프로젝트 → 글로벌 → 아카이브 | CONFIRMED | D2.0-06 L643(RULE 1.3 §8.1 근거) |

## 9. §20 config.v1.toml LOCK 20키 — CONFIRMED 20 (전수 PHASE_B4_CONFIG_SPEC.md)

| # | 설정 키 | 값 | 판정 | PHASE_B4 라인 |
|---|---------|-----|------|---------------|
| 72 | core.single_decision_lock | true | CONFIRMED | L144·L152 |
| 73 | embedding.model | bge-m3 | CONFIRMED | L185·L193 |
| 74 | embedding.dimension | 1024 | CONFIRMED | L186·L194 |
| 75 | vector_db.backend | chroma (V1) | CONFIRMED | L204·L212 |
| 76 | graph_db.backend | json_file (V1) | CONFIRMED | L223·L231 |
| 77 | cost.daily_limit | 1300 | CONFIRMED | L274·L284 (BASE-1.3 L198) |
| 78 | cost.monthly_limit | 40000 | CONFIRMED | L275·L285 (BASE-1.3 L199) |
| 79 | cost.warn_threshold | 80 | CONFIRMED | L276·L286 + L904(V2+ ADMIN 동적 조정 — CLAUDE.md 비고와 정합) |
| 80 | cost.block_threshold | 100 | CONFIRMED | L277·L287 |
| 81 | semantic_cache.similarity_threshold | 0.95 | CONFIRMED | L540·L547(LOCK) |
| 82 | logging.trace_id_required | true | CONFIRMED | L466·L499 |
| 83 | mcp.transport | streamable_http | CONFIRMED | L357·L368(DEC-017 LOCK) |
| 84 | self_check.threshold_p0 | 70 | CONFIRMED | L327·L334(LOCK) |
| 85 | self_check.threshold_p1 | 75 | CONFIRMED | L328·L335(LOCK) |
| 86 | self_check.threshold_p2 | 80 | CONFIRMED | L329·L336(LOCK) |
| 87 | self_check.soft_loop_max | 1 | CONFIRMED | L330·L337(LOCK) |
| 88 | approval.timeout_s | 600 | CONFIRMED | L344·L349(LOCK) |
| 89 | approval.p2_timeout_s | 300 | CONFIRMED | L345·L350(LOCK; D2.0-07 L106 HITL 5분과 정합) |
| 90 | blue_nodes.active_node_cap | 3 (V1) | CONFIRMED | L507·L513(LOCK: D2.0-03 §4.3-B) |
| 91 | ui.min_width | 1280 (V1) | CONFIRMED | L522·L529(D8 §3.1 LOCK) |

---

## 10. SUSPECT 목록 (1건)

1. **§7.1 DEC-001 "문서 우선순위"** — 문서 위계 규칙 자체는 D2.0-01 L64·L752 정본 확인. 그러나 SOT에서 DEC-001은 **"에이전트 프레임워크 확정(자체 프레임워크) FREEZE"** (D2.0-02 §0.6-A L67-74; READINESS_GUIDE L601·L1087, D2.0-01 L887도 동일 맥락). "문서 우선순위"에 DEC-001 번호를 부여한 출처는 SOT/SOT2 전수 grep에서 미발견. → CLAUDE.md의 DEC 번호-내용 매핑 오류 추정 (내용 자체는 유효, 라벨만 불일치).

## 11. 비고 (CONFIRMED이나 단서 있는 항목 — 수정 아닌 기록)

- **#2 DEC-002**: SOT 원문 자체가 라벨 혼용(D2.0-02 L69는 DEC-002를 LangGraph LOCK으로, §0.7-A L85는 LangChain 패턴 참조로 사용). CLAUDE.md 기술 내용은 §0.7-A·V1-009와 일치.
- **#26 RBAC**: D2.0-07 L510·L574가 "정본: CLAUDE.md §7.3 LOCK"으로 역참조(순환 참조 구조). 독립 정본은 MASTER_SPEC §9.2 L1038-1045에서 확인되어 CONFIRMED 유지.
- **#29 P2 자동 OFF**: "(LOCK: Option A)" 라벨 표기는 SOT 미발견(BASE-1.3 L145·D2.0-07 L107에 내용은 정확히 존재).
- **#45 Hybrid Search threshold 0.75**: CLAUDE.md가 지목한 D2.0-06 S7D-012/S7D-018에는 0.75 미기재. 실정본은 SOT2 6-4 LOCK-MR-009(AUTHORITY_CHAIN.md L39, 구현가이드 PART2 L2038 유래). 값은 정본 확인되나 출처 표기 부정확.
- **#14 Self-check 임계값**: D2.0-02 L1863에 별도 맥락의 "P0:60/P1:70/P2:80" 표가 공존하나, LOCK 정본(L1828-1830·L1858, PHASE_B4)은 70/75/80으로 일치.

— 끝 (Step 4 cross-examine, 2026-06-11)
