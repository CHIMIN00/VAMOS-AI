# VAMOS AI 프로젝트 컨텍스트

> **자동 로딩 파일** | 최종 갱신: 2026-02-24
> **목적**: Claude Code 대화 시작 시 VAMOS 프로젝트 전체 맥락을 즉시 제공

---

## 1. 프로젝트 개요

- **한줄 설명**: 사용자의 지능적 결정을 돕는 개인 맞춤형 AI 보조 지능 (투자/생산성/분석), AGI 구조 지향
- **아키텍처**: Front Mini LLM → ORANGE CORE → BLUE NODES → OTHER BRAINS → Main LLM
- **기술 스택**: Tauri 2.0 + React 18 / Rust (IPC) / Python 3.11+ (AI/ML) / LangGraph / BGE-M3 / Chroma→Qdrant
- **통신 계층**: React UI ↔ Tauri IPC ↔ Rust Backend ↔ JSON-RPC stdin/stdout ↔ Python AI/ML ↔ MCP Streamable HTTP
- **버전**: V0(구조기반, 1~2주) → V1(₩40K/월 MVP, 8~12주) → V2(₩93K/월 Pro) → V3(₩266K/월 Enterprise)
- **6대 철학**: 사용자 중심 | 정확성/근거 기반 | 최신성 확보 | 장기 맥락 유지 | 다중 의도 처리 | 구조적 모듈화

---

## 2. 산출물 경로

```
정본 경로: D:\VAMOS\00. 통합\02. TECH\00. FINAL SUMMARY\STEP6_pipeline\output\updated\
```

- **총 39개 파일, 5그룹**:
  - **A: 설계 21개** (~35,472줄) — BASE+PLAN+DESIGN+SCHEMA: "무엇을 만들지" 정의
  - **B: 구현가이드 7개** (~9,618줄) — PHASE_B1~B7: "어떻게 코딩하지" 정의 (= IMPLEMENTATION 계층)
  - **C: 특화 SPEC 5개** (~8,543줄) — MASTER/INVESTING/CLOUD/TEAMS/SDAR: 도메인별 상세
  - **D: STEP7 상세명세 5개** (~9,019줄) — A-E/F-I/J-M/N-P/보강: AI기술보강 3,101건
  - **E: 기타 1개** (~1,853줄) — BEGINNER_GUIDE: 초보자 온보딩

---

## 3. 문서 위계 (ABSOLUTE)

```
RULE 1.3 (절대규칙) > PLAN 3.0 (상위원칙) > DESIGN 2.0 LOCK > DESIGN 본문(01~08) > 스키마/TECH_STACK(D1~D8, A1)
```

- **충돌 시**: 상위 번호가 하위를 override
- **변경관리**: 삭제 금지 (DEPRECATE만), 없는 내용 창작 금지, Major 변경은 07 Approval Gate 필수

---

## 4. 핵심 파일 (대화 시작 시 우선 참조)

| # | 파일명 | 줄 수 | 역할 |
|---|--------|------|------|
| 1 | `VAMOS_MASTER_SPECIFICATION.md` | 1,893 | 전체 통합 참조점 (SOT) — 모든 흐름/구조/규칙/API/스키마 |
| 2 | `VAMOS_IMPLEMENTATION_READINESS_GUIDE.md` | 1,256 | V0~V3 구현 준비 현황 + 45개 이슈 + 62개 GO/NO-GO |
| 3 | `BASE-1.3_VAMOS_RULE_1.3_BASE.md` | 633 | 절대 불변 규칙 (Identity/Safety/Cost/Non-goal) |
| 4 | `PLAN-3.0_VAMOS_PLAN_3_0_최종완성본.md` | 6,948 | 로드맵/비용/버전 정본 |
| 5 | `D2.0-01_01. VAMOS_DESIGN_2_0_OVERVIEW.md` | 1,718 | 아키텍처 허브/레지스트리/LOCK 규칙 |
| 6 | `D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md` | 4,230 | ORANGE CORE I-1~I-25 상세설계 |
| 7 | `PHASE_B1_API_CONTRACT.md` | 2,218 | API 계약 88개 엔드포인트 |
| 8 | `PHASE_B2_PROJECT_STRUCTURE.md` | 886 | 모노레포 디렉토리 레이아웃 |

---

## 5. 4계층 아키텍처

```
Front Mini LLM (의도/보안/도메인 판별) — I-1 내부 서브컴포넌트
  → ORANGE CORE (정책/룰/비용/라우팅/안전/Self-check)
    → BLUE NODE (도메인 전용 실행 스택: Dev/Research/Productivity/Content/Quant/Trading)
      → OTHER BRAINS (검색/RAG/DB/API/코드실행/분석엔진)
        → Main/Hologram LLM (최종 출력/시각화/보고서)
```

### 5-Phase 파이프라인 (LOCK)

| # | 단계 | 담당 | 산출물 | 상태코드 |
|---|------|------|--------|---------|
| 1 | Perception/Intake | Front Mini + I-1 | IntentFrame | S0→S1 |
| 2 | Reasoning/Plan | I-2 + I-5 + Gates | EvidencePack + Decision | S2→S3 |
| 3 | Action/Execute | BLUE NODE + D4 | Artifacts/Results | S4→S5 |
| 4 | Reflection/Verify | I-6 + EVX | Self-check 결과 | S6 |
| 5 | Memory/Store | I-3 + D6 | L0/L1/L2/L3 저장 | S7→S8 |

### Gate 시스템 (우회 불가, LOCK)

| Gate | 위치 | 역할 | 실패 시 |
|------|------|------|--------|
| PolicyGate | S1~S3, S6 | block/require_approval/mask/allow | deny + 감사로그 |
| CostGate | S2~S3, S4 | normal/downshift/split/stop | FB_COST_DOWNSHIFT |
| ApprovalGate | S1~S3 | approved/denied/pending/expired | FB_REQUIRE_APPROVAL |
| EvidenceGate | S2 | sufficient/insufficient | HOLD/ESCALATE + 재검색 |
| SelfCheckGate | S5→S6 | PASS/WARN/FAIL | Soft loop 1회 → 승인/deny |

---

## 6. 모듈 시스템 (81개: I25+E16+S8+A7+B6+C7+D6+EVX6)

### I-Series (I-1~I-25) 내부 기능

| ID | 명칭 | status | V1 | V2 | V3 |
|---|---|---|---|---|---|
| I-1 | Intent Detector (대화 이해/추론) | CORE | ON | ON | ON |
| I-2 | Context Builder (RAG/지식 검색) | CORE | ON | ON | ON |
| I-3 | Memory System (4계층: L0~L3) | CORE | ON | ON | ON |
| I-4 | Multimodal Interpreter | CORE | ON | ON | ON |
| I-5 | Condition & Decision Engine | CORE(LOCK) | ON | ON | ON |
| I-6 | Self-check Engine | CORE | ON | ON | ON |
| I-7 | Project/Session Manager | COND | OFF | COND | ON |
| I-8 | Policy Engine | CORE(LOCK) | ON | ON | ON |
| I-9 | Cost Manager | CORE(LOCK) | ON | ON | ON |
| I-10 | Tool Registry/Router | CORE | ON | ON | ON |
| I-11 | Output Composer | CORE | ON | ON | ON |
| I-12 | Workflow Builder | COND | OFF | COND | ON |
| I-13 | Multimodal Output Renderer | CORE | ON | ON | ON |
| I-14 | Summarizer & Memory Distiller | CORE | ON | ON | ON |
| I-15 | Evidence & QoD Manager | CORE | ON | ON | ON |
| I-16 | Knowledge Search Engine | CORE | ON | ON | ON |
| I-17 | Blue Node Manager | CORE | ON | ON | ON |
| I-18 | Self-evo Engine | EXP | OFF | OFF | ON |
| I-19 | Approval Manager | CORE(LOCK) | ON | ON | ON |
| I-20 | Failure/Fallback Manager | CORE | ON | ON | ON |
| I-21 | Source Evolution | EXP | OFF | OFF | ON |
| I-22 | Task/Project Manager | COND | OFF | COND | ON |
| I-23 | Doc/Code Structuring | COND | OFF | COND | ON |
| I-24 | Knowledge Graph Engine | EXP | OFF | OFF | ON |
| I-25 | SDAR Engine (자가진단/수리) — D2.0-02 미수록, VAMOS_SDAR_DESIGN_SPECIFICATION 참조 | COND | OFF | COND | ON |

### E-Series (E-1~E-16) 외부 기능

| ID | 명칭 | V1 | V2 | V3 |
|---|---|---|---|---|
| E-1 | Coding & System Design Helper | ON | ON | ON |
| E-2 | Web Search | ON | ON | ON |
| E-3 | Document Parser | ON | ON | ON |
| E-4 | Code Executor | ON | ON | ON |
| E-5 | Image Analyzer | ON | ON | ON |
| E-6 | Z3 Solver | ON | ON | ON |
| E-7 | Speech-to-Text | OFF | OFF | ON |
| E-8 | Text-to-Speech | OFF | OFF | ON |
| E-9 | Video Analyzer | OFF | OFF | ON |
| E-10 | External API Gateway | OFF | OFF | ON |
| E-11 | Browser Automation | OFF | OFF | ON |
| E-12 | DB Connector | OFF | OFF | ON |
| E-13 | Calendar/Task Sync | OFF | COND | ON |
| E-14 | Email Handler | OFF | COND | ON |
| E-15 | File System (V1) → Cloud Collector (V2+) — 단일 모듈, 버전별 역할 확장. V1: 로컬 파일 I/O, V2+: Cloud Library 수집 추가 | OFF | COND | ON |
| E-16 | Cloud Storage Sync | OFF | COND | ON |

### S-Series (S-1~S-8) 자기진화

| ID | 명칭 | V1 | V2 | V3 | I-연결 |
|---|---|---|---|---|---|
| S-1 | Self-check Engine | ON | ON | ON | I-6, I-15 |
| S-2 | Benchmark QA Suite | OFF | OFF | ON | I-24 |
| S-3 | Template Evolution | OFF | OFF | ON | I-12, I-18 |
| S-4 | Error Pattern Miner | OFF | OFF | ON | I-20, I-18 |
| S-5 | Router Evolution (V3) → Cloud Evolver (V3) — 단일 모듈, 이중 역할. Router Evolution: I-10 라우팅 자기진화, Cloud Evolver: Cloud Library 전략 진화 | OFF | OFF | ON | I-10, I-18 |
| S-6 | Search Evolution | OFF | OFF | ON | I-16, I-18 |
| S-7 | User-Coop Designer | OFF | OFF | ON | I-19, I-18 |
| S-8 | Self-evo Governance | OFF | OFF | ON | I-19, I-8, I-9, I-24 |

### A-Series (A-1~A-7) 아키텍처 확장

| ID | 명칭 | V1 | V2 | V3 |
|---|---|---|---|---|
| A-1 | MultiBrain Adapter | ON | ON | ON |
| A-2 | Preset Modularization | ON | ON | ON |
| A-3 | Meta AI | OFF | OFF | ON |
| A-4 | Debate Mode | OFF | COND | ON |
| A-5 | Lazy Generation | OFF | OFF | ON |
| A-6 | Federated Module Network (LOCK) | OFF | OFF | ON |
| A-7 | Remote Executor (LOCK) | OFF | OFF | ON |

### B-Series (B-1~B-6) Memory/Skill/Self-evo 자산

| ID | 명칭 | status | V1 | V2 | V3 |
|---|---|---|---|---|---|
| B-1 | Skill Library (스킬 라이브러리) | EXP | OFF | OFF | ON |
| B-2 | Procedural Memory (방법론 메모리) | EXP | OFF | OFF | ON |
| B-3 | Memory Decay (망각/감쇠) | CORE | ON | ON | ON |
| B-4 | Auto Curriculum Generator | EXP | OFF | OFF | ON |
| B-5 | RL-like Self Trainer | EXP | OFF | OFF | ON |
| B-6 | DSPy Prompt Optimizer | EXP | OFF | OFF | ON |

### C-Series (C-1~C-7) Verifier/Reasoning 확장

| ID | 명칭 | status | V1 | V2 | V3 |
|---|---|---|---|---|---|
| C-1 | Logic Verifier | CORE | ON | ON | ON |
| C-2 | Math Verifier | CORE | ON | ON | ON |
| C-3 | Code Verifier | CORE | ON | ON | ON |
| C-4 | Domain Simulator | EXP | OFF | OFF | ON |
| C-5 | Bayesian Belief Engine | EXP | OFF | OFF | ON |
| C-6 | RL Advisor | EXP | OFF | OFF | ON |
| C-7 | GNN Score Model | EXP | OFF | OFF | ON |

### D-Series (D-1~D-6) Brain/Planner/RAG 확장

| ID | 명칭 | status | V1 | V2 | V3 |
|---|---|---|---|---|---|
| D-1 | Think Engine | CORE | ON | ON | ON |
| D-2 | Multimodal Engine | CORE | ON | ON | ON |
| D-3 | Long Horizon Planner | EXP | OFF | OFF | ON |
| D-4 | Personality/Tone Engine | EXP | OFF | OFF | ON |
| D-5 | General Brain (Parallel) | EXP | OFF | OFF | ON |
| D-6 | GraphRAG / Hybrid RAG | EXP | OFF | OFF | ON |

- **EVX-1~EVX-6**: 검증 체인 (Code-as-Policy, Adversarial, Log-prob Confidence, Thought Buffer, Gen-Verify-Learn, Z3 Solver Routing)
- **STEP7**: 16개 카테고리(A~P) 3,101건 AI기술보강

---

## 7. LOCK 결정사항 (전수)

### 7.1 아키텍처 LOCK

| 항목 | LOCK 내용 |
|------|----------|
| DEC-001 | 문서 우선순위: RULE > PLAN > DESIGN LOCK > DESIGN 본문 > 스키마 |
| DEC-002 | LangChain import 금지 (패턴만 참조). **Allowlist(V1-009)**: `langchain-core`, `langchain-community`, `langchain-openai` adapter만 허용. `langchain` 본체 패키지 import 금지. "패턴 참조"란 LangChain의 설계 패턴(Chain/Agent/Tool 추상화)을 VAMOS 자체 구현에 참고하는 것을 의미하며, 런타임 의존성은 Allowlist 패키지에 한정 |
| DEC-003 | 도구 승인 Allowlist: 읽기전용=자동, 외부API/쓰기/코드실행=확인 필요 |
| DEC-017 | MCP 전송: Streamable HTTP (LOCK) |
| 변경관리 | 삭제 금지, 창작 금지, Major는 07 Approval |
| E-*/EVX-* | E-*=외부기능, EVX-*=Verify 확장, E 변형 금지 |
| S-#/S#_ | S-#=모듈 ID(하이픈), S#_=상태(언더스코어) — 충돌 원천 분리 |
| A-6/A-7 | A-6=Federated(LOCK), A-7=Remote Executor(LOCK) |
| Monorepo | 저장소 구조 확정 (PHASE_B2 정본) |
| LangGraph | Agent Workflow 프레임워크 (LOCK) |
| config 포맷 | config.toml (PHASE_B4 정본) |

### 7.2 핵심 엔진 LOCK

| 항목 | LOCK 내용 |
|------|----------|
| Decision Lock | 한 시점/한 컨텍스트/한 결론 → locked=true (S3 이후 변경불가) |
| Gate 우회 불가 | Policy→Approval→Cost→Evidence 필수 통과 |
| Self-check 임계값 | P0:70, P1:75, P2:80 |
| Self-check 루프 | Soft loop 자동 1회만, 이후 승인 필요 |
| L2 저장 정책 | 기본 "승인 필요" |
| 코드 실행 격리 | Docker 샌드박스 필수 (네트워크 차단, 30초) |
| 동시성 | MAX_CONCURRENT_BLUE_NODES=3, TOOLS=5 |
| Multi-Brain Failover | GPT-4o→Claude→Ollama (3회 타임아웃 시 전환) |
| 대화 턴 상한 | P0=5, P1=10, P2=20 |
| TEE 최대 반복 | P0=3회, P1=5회, P2=10회 |

### 7.3 비용/안전 LOCK (ABSOLUTE)

| 항목 | LOCK 내용 |
|------|----------|
| V1 비용 상한 | ₩40,000/월 ($30), ₩1,300/일 ($1) — Mini 90%+ |
| V2 비용 상한 | ₩93,000/월 ($70), ₩3,100/일 ($2.3) — Mini 60-70% / Main 30-40% |
| V3 비용 상한 | ₩266,000/월 ($200), ₩8,900/일 ($6.7) — Main 중심, Flagship 적극 |
| Downshift | 80% warn/force_mini, 100% block (자동 차단) |
| RBAC | OWNER(L3,P2,₩266K) / ADMIN(L2,P2,₩93K) / OPERATOR(L1,₩40K) / VIEWER(L0,₩0) |
| Autonomy 기본 | L1 (SUPERVISED) — L3에서도 Non-goal/RBAC/CostBudget/안전필터 자동불가 |
| Guardrails | 4-Layer: L1(NeMo 입력방어) + L2(Guardrails AI 처리) + L3(LlamaGuard 출력) + L4(사후감사, V2+) |
| P2 자동 OFF | 세션 종료 시 즉시 OFF (LOCK: Option A) |
| Non-goal | 7개 절대 금지 항목 |
| 7개 불변 구역 | safety_rules, cost_ceiling, approval_flow, non_goals, audit_format, data_retention, user_consent |
| 승인 타임아웃 | 10분 미응답 → 자동 거부 |

### 7.4 데이터/인프라 LOCK

| 항목 | LOCK 내용 |
|------|----------|
| DEC-004 | GraphRAG: 하이브리드 RAG (V1=Basic 64%+, V2=Hybrid+Rerank 83%+, V3=Self-RAG+Graph 90%+) |
| DEC-005 | Embedding: V1=BGE-M3(로컬,1024dim)/text-embedding-3-small(클라우드) |
| DEC-010 | QoD 스케일: 0.0~1.0 |
| DEC-014 | QoD 가중치(RAG): relevance 0.30 + accuracy 0.25 + freshness 0.25 + completeness 0.20 |
| QoD 5요소(PLAN정본) | Accuracy 0.30 + Relevance 0.25 + Completeness 0.20 + Safety 0.15 + Efficiency 0.10 |
| Semantic Cache | cosine ≥ 0.95 (LOCK) |
| Vector DB | V1=Chroma로컬, V2+=Qdrant 서버 |
| RAG Pipeline | 6단계: Collect→Chunk(300~500tok)→Embed→Store→Retrieve→Generate |
| 병렬 실행 상한 | 3 (LOCK) |
| 설정 우선순위 | ENV > config.toml > default |
| 로깅 | JSON Structured (평문 금지, trace_id 필수) |
| 네이밍 | event: lower.dot / failure: UPPER_SNAKE / fallback: FB_UPPER_SNAKE / state: S#_ / module: S-# |

### 7.5 Self-evo LOCK

| 항목 | LOCK 내용 |
|------|----------|
| 원칙 | 제안만 가능, 자동 적용 절대 금지 |
| 허용 6개 | 프롬프트 / 도구 조합 / 메모리 관리 / 출력 포맷 / 워크플로우 순서 / 모델 선택 |
| 불변 7개 | 정체성 / Non-goal / 법규윤리 / 비용상한 / 승인구조 / P0도메인 / P2생성활성화 |
| 롤백 잠금 | 동일 제안 롤백 후 14일 재적용 금지 |

### 7.6 UI/UX LOCK

| 항목 | LOCK 내용 |
|------|----------|
| 프레임워크 | Tauri 2.0 + React 18 (V2: +PWA) |
| 2-View | Builder(개발/관리) + Hologram(사용자 대화) |
| 3-Panel | Left(Navigation/Timeline) + Center(Canvas/Stream) + Right(Control/HUD) |
| P2 재확인 | 모달 (DEC-011) |
| 비용 경고 색상 | 80%=#FBBF24(노란), 100%=#EF4444(빨간) (DEC-015) |
| ORANGE 색상 | #F97316, BLUE NODE: #00F6FF |

---

## 8. Non-goal (절대 금지 7개, BASE-1.3 section 2)

| # | Non-goal | 위반 시 대응 |
|---|----------|-------------|
| 2.1 | 실거래/주문/계좌/API 연동 | 즉시 거부. 분석 보조만 가능 |
| 2.2 | 불법 행위/해킹/권한 상승 | 즉시 차단. 법적 책임 고지 |
| 2.3 | 의료/법률 단정적 판단/대리 결정 | 단정 금지. "전문가 상담 필요" + 참고정보만 |
| 2.4 | 민감 개인정보 장기 저장 | 저장 거부. 세션 내 임시 사용 후 즉시 파기 |
| 2.5 | 저작권/약관 위반 | 거부. 합법적 접근 방법 안내 |
| 2.6 | P2 도메인 자동 생성 금지 | 활성화 전 반드시 명시적 승인 요청 |
| 2.7 | 위험 기능 자동 실행 금지 | HITL 승인 없이 실행 불가 |

---

## 9. 45개 미해소 이슈 (전수)

### HIGH (10건)

| ID | 요약 | 해소 시점 |
|---|---|---|
| V0-002 | IMPLEMENTATION 계층 문서 부재 → PHASE_B = IMPLEMENTATION 계층 명시 | V0 전 |
| V0-004 | 통신 계층: Python 백엔드 확정 (PLAN-3.0 정본, Node.js sidecar는 대안) | V0 전 |
| V1-001 | I-Series 모듈 카운트 통일: I-1~I-25 (25개) 정본 확정 | V1 전 |
| V1-002 | E-15 명칭 충돌: "File System / Cloud Collector" 겸용 처리 | V1 전 |
| V1-003 | S-5 명칭 충돌: "Router Evolution / Cloud Evolver" 겸용 처리 | V1 전 |
| V1-008 | 38개 DEFER/TBD 분류 → V1 차단 0건 확인 완료 | V1 전 |
| V1-015 | Python 백엔드 진입점 정의 → V0에서 해소 | V0 |
| V1-016 | I-21~I-25 모듈 정의 추가 (Source Evolution/Task/Doc/KG/SDAR) | V1 전 |
| V2-003 | Agent Teams vs FREEZE 충돌: Lead Agent 단방향만 V1, MessageBus는 V2 | V2 전 |
| V2-008 | STEP7 TITLE_ONLY 44% (~675건): V2 CRITICAL ~190건 상세 스펙 보강 필요 | V2 전 |

### MEDIUM (21건)

| ID | 요약 | 해소 시점 |
|---|---|---|
| V0-001 | V0 비용 상한 미정의 → V1 동일 적용 (₩40,000/월) | V0 전 |
| V0-003 | 디렉토리 구조 불일치 → PHASE_B2 모노레포가 정본 | V0 전 |
| V1-004 | Decision.approval_status enum 통일 → D7 SOT (approved/denied/pending/expired) | V1 전 |
| V1-005 | datetime.utcnow() → datetime.now(timezone.utc) 전수 교체 | V1 전 |
| V1-006 | QoD 가중치 통일 → PLAN-3.0 5요소 공식 정본 | V1 전 |
| V1-007 | Front Mini LLM = I-1 내부 서브컴포넌트 명시 (별도 모듈 ID 불필요) | V1 전 |
| V1-010 | Guardrails 계층 수 통일 → 4-Layer 정본 (L4=V2+에서 활성) | V1 전 |
| V1-013 | 비용 상한 통일 → BASE-1.3 ₩40,000/월 정본 (STEP7 $8은 최소운영목표) | V1 전 |
| V2-001 | 10-Layer 명칭 충돌 → Cloud Library를 CL-Layer 접두어로 구분 | V2 전 |
| V2-002 | SDAR V2 COND 활성화 조건 (AR-L2→AR-L3, LOW성공률≥95%) | V2 전 |
| V2-004 | JSONL→PostgreSQL+Loki 로그 마이그레이션 | V2 전 |
| V2-005 | Chroma→Qdrant 벡터 재임베딩 (4-Phase, needs_reembedding 플래그) | V2 전 |
| V2-006 | NetworkX JSON→Neo4j Community 변환 | V2 전 |
| V2-007 | STEP7 비용 vs BASE 비용 괴리 인지 | V2 전 |
| V3-001 | K8s 배포 명세 보강 (Helm Chart, ArgoCD, 멀티리전) | V3 전 |
| V3-002 | S-8 Self-evo 거버넌스 상세화 | V3 전 |
| CC-001 | 스키마 버전 통일 → V0 진입 시 전체 v3.0.0 승격 | V0 |
| CC-003 | QoD 가중치 이중 체계: RAG 소스 신뢰도 vs Cloud Library 수집 품질 (별도 목적) | V2 전 |
| CC-006 | EventTypeRegistry 미완성: agent.* + sdar.* 이벤트 통합 등록 | V1 전 |
| CC-007 | Python/TypeScript 스키마 동기화 메커니즘 (Pydantic→Zod 자동변환) | V1 전 |
| CC-012 | HMAC-SHA256 키관리/검증 상세화 (Agent Teams MessageBus) | V2 전 |

### LOW (9건)

| ID | 요약 |
|---|---|
| V0-005 | config 포맷 혼재 → config.toml 통일 (PHASE_B4 정본) |
| V1-009 | LangChain Allowlist 명시 (langchain-core adapter만 허용) |
| V1-011 | (정합성 확인 완료됨) |
| V1-014 | React 버전 통일 → React 18.3 (PHASE_B3 정본) |
| V3-003 | V3 비용 상한 현실성 (GPU+K8s+DB → V2 운영 데이터 기반 재산정) |
| V3-004 | GraphRAG 90% 목표 벤치마크 기준/측정 방법 미정의 |
| CC-002 | BEGINNER_GUIDE 갱신 (I-21~I-25, E-15/S-5 명칭) |
| CC-004 | Gate G0~G4 이중 사용 → Cloud Library를 CL-G0~CL-G4 접두어 |
| CC-005 | STEP7 모듈 연동 추상적 → V2 보강 시 구체적 모듈 ID 매핑 |

### INFO (5건)

| ID | 요약 |
|---|---|
| V1-012 | (정합 확인 완료) |
| CC-008 | 테스트 케이스 목록 부재 → V1 구현 시 AC 기반 자동 도출 |
| CC-009 | B↔L 매핑 교차(비직관적) → LOCK 변경불가, 가이드에 매핑표 명시 |
| CC-010 | 문서 인덱스 39 vs 실제 38 (PLAN-2.0 SUPERSEDED) |
| CC-011 | STEP7 항목 수 60건 차이 (범위 묶음 전개 → 개별 문서 기준이 정본) |

---

## 10. V0~V3 GO/NO-GO 체크리스트

### V0 진입 전 (16항목)

```
[ ] 통신 계층: Python 백엔드 확정 (V0-004)
[ ] IMPLEMENTATION 계층 = PHASE_B 명시 (V0-002)
[ ] V0 비용 상한 = V1 동일 명시 (V0-001)
[ ] 디렉토리 구조: PHASE_B2 정본 명시 (V0-003)
[ ] config 포맷: config.toml 통일 (V0-005)
[ ] D2.1 스키마 v3.0.0 통일 승격 (CC-001)
[ ] PLAN-2.0 "(대체됨)" 표기 (CC-010)
[ ] BASE-1.3 전 24개 규칙 코드 매핑
[ ] 스캐폴딩 + 의존성 설치 (pip/npm/cargo)
[ ] config.v1.toml LOCK 값 배치
[ ] 24개 스키마 코드 생성 (Pydantic v2/Zod/serde)
[ ] I-1~I-5 + I-19 스켈레톤 생성
[ ] L0 세션 메모리 최소 구현
[ ] 비용 엔진 ₩40,000/월 하드코딩
[ ] Guardrails L1+L2 설정
[ ] Ollama + Chroma + SQLite 초기화
```

### V1 진입 전 (21항목, V0 완료 전제)

```
[ ] I-Series 25개 모듈 정본 확정 (V1-001, V1-016)
[ ] E-15, S-5 명칭 겸용 처리 (V1-002, V1-003)
[ ] 38개 DEFER/TBD V1 차단 0건 확인 (V1-008)
[ ] datetime.utcnow() 전수 교체 (V1-005)
[ ] approval_status enum 4개 통일 (V1-004)
[ ] QoD 5요소 공식 통일 (V1-006)
[ ] Front Mini LLM = I-1 내부 명시 (V1-007)
[ ] Guardrails 4-Layer 명시 (V1-010)
[ ] 비용 상한 ₩40,000 통일 (V1-013)
[ ] React 18.3 통일 (V1-014)
[ ] LangChain Allowlist 명시 (V1-009)
[ ] 15개 보안 항목 (S7E + DEC-003 Allowlist) 구현
[ ] 테스트 인프라 구축 (80%+ 커버리지)
[ ] CI/CD 설정 완료 (GitHub Actions 8-stage)
[ ] 스토리지 스택 구축 (SQLite+Chroma+JSONL+Graph)
[ ] EventTypeRegistry 통합 (CC-006)
[ ] Python/TS 스키마 동기화 도구 (CC-007)
[ ] BEGINNER_GUIDE 모듈 목록 갱신 (CC-002)
[ ] B↔L 매핑표 추가 (CC-009)
[ ] STEP7 항목 수 비고 추가 (CC-011)
[ ] V0 GO 체크리스트 전수 통과
```

### V1→V2 전환 조건

```
QoD ≥ 0.85 (30일) / RAG 정확도 ≥ 60% / 메모리 승격/강등 오류율 < 1%
P0 테스트 100% / 비용 초과 없이 30일 / 사용자 승인
```

### V2 진입 전 (14항목, V1 완료 전제)

```
[ ] V1→V2 전환 조건 6개 충족
[ ] Agent Teams FREEZE 해석 확정 (V2-003)
[ ] STEP7 V2 CRITICAL ~190건 상세 스펙 보강 (V2-008)
[ ] 10-Layer/Gate 접두어 변경 (V2-001, CC-004)
[ ] SQLite→PostgreSQL 마이그레이션 (V2-004)
[ ] Chroma→Qdrant 재임베딩 (V2-005)
[ ] NetworkX→Neo4j 변환 (V2-006)
[ ] SDAR V2 COND 활성화 조건 확정 (V2-002)
[ ] MessageBus 구현 결정 (Redis vs In-Memory)
[ ] HMAC 프로토콜 상세 완성 (CC-012)
[ ] STEP7 모듈 연동 구체화 (CC-005)
[ ] V2 인프라 10개 컴포넌트 구축
[ ] V2 비용 모니터링 대시보드 (₩93,000 이내)
[ ] QoD 가중치 이중 체계 구분 명시 (CC-003)
```

### V2→V3 전환 조건

```
QoD ≥ 0.90 (60일) / 2-tier LLM 최적화 완료 / P1 고급 테스트 통과
Self-evo 체계 검증 / V3 비용 재검토 + 승인 / Loki+Grafana 배포
```

### V3 진입 전 (11항목, V2 완료 전제)

```
[ ] V2→V3 전환 조건 충족
[ ] K8s 배포 명세 상세 완성 (V3-001)
[ ] S-8 Self-evo 거버넌스 상세화 (V3-002)
[ ] V3 비용 상한 재산정 + 승인 (V3-003)
[ ] GraphRAG 벤치마크 정의 (V3-004)
[ ] SDAR V3 ON 조건 충족 (AR-L4, 수리성공률≥95%, 스냅샷복원100%)
[ ] STEP7 TITLE_ONLY ~317건 상세 보강
[ ] 에이전트 50+ 병렬 인프라 구축
[ ] A2A 프로토콜 설계
[ ] Federated Agent 승인 체계
[ ] Agent Marketplace 기준 확정
```

---

## 11. 기술 스택 (Tech Combo)

| 항목 | V1 (로컬/개인) | V2 (서버) | V3 (운영형) |
|------|---------------|-----------|------------|
| LLM | Ollama + GPT-4o mini | GPT-4o mini + Sonnet | vLLM + 외부 조합 |
| Embedding | BGE-M3 (로컬, 1024dim) | + text-embedding-3-small | + text-embedding-3-large |
| Vector | Chroma 로컬 | Qdrant 서버 | Qdrant Cloud |
| Graph | JSON (NetworkX) | Neo4j Community | Neo4j Aura |
| Storage | SQLite + JSONL | Postgres | Managed Postgres |
| Logging | JSONL + SQLite | Postgres + JSONL | Loki/ELK |
| Deploy | Windows/WSL | Docker Compose | K8s |
| UI | Tauri 2.0 + React | + PWA (Next.js) | + 모바일 네이티브 |
| Guardrails | NeMo + Guardrails AI | + LlamaGuard + 사후감사 (4층) | 동일 (4층) |
| Framework | LangGraph (LOCK) | 동일 | 동일 |
| MCP | Streamable HTTP (LOCK) | 동일 | 동일 |

---

## 12. 핵심 스키마 (코드 생성 대상)

### Decision (18필드, FREEZE)

```python
decision_id, trace_id, timestamp, intent_frame_ref, evidence_pack_ref,
policy_gate(block|require_approval|mask|allow), approval_required, approval_status(approved|denied|pending|expired),
cost_gate(normal|downshift|split|stop), routing{blue_node_id, execution_mode},
memory_plan{save_candidate, target_layer, requires_user_approval},
output_spec{format_constraints}, conclusion(ACCEPT|REJECT|HOLD|ESCALATE),
locked=True, optional_signals[], verify{}, gates{}, s_module_hints{}
```

### IntentFrame

```python
intent_id, trace_id, timestamp, user_goal, task_type, domain_hint(P0|P1|P2),
constraints{format, must_include, must_not_include}, risk_flags{safety, approval, cost},
ambiguity{is_ambiguous, missing_slots, clarification_questions(0~3)},
required_artifacts[], query, domain, intent_type, complexity, risk_level,
required_tools, confidence(0~1, <0.5시 HITL), sub_intents
```

### ResponseEnvelope (LOCK)

```python
answer{summary, details, next_actions[]},
evidence{coverage(0~1), items[], qod(0~1)},
self_check{score(0~1), verdict(PASS|WARN|FAIL), reasons[], retry_allowed},
decision_ref{decision_id, gates{}},
audit{event_ids[], failure_codes[], fallback_ids[]}
```

### 상태 머신 (S0~S8)

```
S0_RECEIVED → S1_INTENT_PARSED(5s) → S2_EVIDENCE_READY(30s)
→ S3_DECISION_LOCKED(120s) → S4_EXECUTING(10s) → S5_OUTPUT_READY(15s)
→ S6_SELF_CHECKED → S7_MEMORY_COMMITTED → S8_DONE
```

---

## 13. API 계약 (88개 엔드포인트)

- **Tauri IPC**: 72개 (`vamos:{category}:{action}`)
  - Core(decision/workflow/session): 15개
  - Agent(node/pipeline/marketplace): 15개
  - Storage(memory/vector/cache/graphrag/qod): 18개
  - Safety(policy/cost/approval/guardrails/rbac/autonomy): 19개
  - UI(log/config/theme/notification): 5개
- **Python-Rust JSON-RPC**: 13개 (langgraph.*, embedding.*, llm.*, mcp.*)
- **MCP Tool Protocol**: 3개 (tools/call, tool_registry.get/list)
- **응답 규격**: `{success, data/error, trace_id}`

---

## 14. 프로젝트 구조 (Monorepo, LOCK)

```
vamos/
├── .github/workflows/       # CI/CD (8-stage)
├── src/                     # React 프론트엔드
│   ├── components/          # decision, memory, cost, log...
│   ├── pages/               # Dashboard, Chat, Workflow, Memory, Settings
│   ├── hooks/               # useTauriIPC, useDecision, useWorkflow...
│   ├── stores/              # zustand (appStore, decisionStore...)
│   └── types/               # Zod 스키마
├── src-tauri/               # Rust Tauri 백엔드
│   └── src/
│       ├── commands/        # IPC 핸들러
│       ├── bridge/          # python_manager.rs, ipc_protocol.rs
│       └── models/          # serde 구조체
├── backend/                 # Python AI/ML
│   └── vamos_core/
│       ├── orange_core/     # I-1~I-5 + decision_kernel
│       ├── blue_nodes/      # base_node + dev/research/content/quant/trading
│       ├── infra/           # brain/tools/prompt/rate_limit/backup
│       ├── agent/           # LangGraph StateGraph + pipeline
│       ├── storage/         # memory/vector/graph/cache/db/logging/kb
│       ├── safety/          # policy/approval/cost/guardrails/rbac/autonomy
│       ├── schemas/         # contracts.py (Pydantic v2 SOT) + enums.py
│       └── mcp/             # bridge/server/client/tool_discovery
├── shared/types/            # JSON Schema (Golden Source)
├── config/                  # default.toml, llm/, embedding/, storage/, safety/, mcp/
├── data/                    # sqlite/, chroma/, logs/, graph/, backups/
└── tests/                   # unit, integration, e2e
```

**타입 동기화**: Python `contracts.py`가 SOT → TypeScript Zod / Rust serde 타입 생성

---

## 15. 메모리/저장 계층

| 계층 | 범위 | TTL | B-Series | V1 | V2 | V3 |
|------|------|-----|----------|----|----|-----|
| L0 Session | 단일 세션 | 7일 (최대 30일) | B-4 Working | ON | ON | ON |
| L1 Project | project_id 단위 | 90일 (연장 가능) | B-1 Episodic | 선택적 | ON | ON |
| L2 Long-term | 전역 (검색 기반) | 무기한 | B-3 Semantic | OFF | 제한(승인) | ON |
| L3 Procedural | 전역/프로젝트 | 무기한 | B-2 Procedural | OFF | 제한 | ON |

- **프로젝트 네임스페이스**: project_id 필드 필수, 프로젝트 간 데이터 혼합 금지
- **QoD 임계값**: < 0.4 → L2 벡터삽입 금지, < 0.7 → 출력 보류
- **PII 마스킹**: V1=정규식, V2+=NER 모델+문맥 분류기
- **검색 순서**: 현재 프로젝트 → 글로벌 → 아카이브

---

## 16. 레지스트리 요약

- **EventTypeRegistry**: 53+ 이벤트 (oc.i1.*, oc.i2.*, wf.*, ui.*, mem.*, agent.*, sdar.*)
- **FailureCodeRegistry**: 20개 (OC_I1_*, OC_I2_*, OC_I3_*, OC_I4_*, OC_I5_*, POLICY_DENY, GT_ERR_*, TOOL_*)
- **FallbackRegistry**: 13개 (FB_ASK_CLARIFICATION, FB_RAG_*, FB_COST_*, FB_REQUIRE_*, FB_OUTPUT_*, FB_MEMORY_*, FB_ROUTE_*, FB_DENY_*, FB_RESTRICT_*)
- **ToolRegistry**: tool_id, category(8종), adapter_id, risk_class, cost_class, required_gates
- **NodeRegistry**: domain_name 기반
- **VerifyChainRegistry**: EVX-1~EVX-6

---

## 17. 주요 특화 시스템

### AI Investing (AINV) — 분석 전용 (실거래 절대 금지)

- 83개 데이터 소스, 96개 전략 카탈로그
- 51% Gate: Win Rate≥51%, Sharpe≥1.0, Decay<30%
- 5-Agent 구조: Perplexity→Gemini→ChatGPT→Claude→Copilot
- 법적 준수: Wash Sale/PDT/Uptick Rule 자동 감지

### SDAR (I-25) — 자가진단/자동복구

- 5-Layer: Detection→Diagnosis→Prescription→Repair→Verification
- AR-Level: AR-L0(수동)~AR-L4(고위험자동), 기본 AR-L2
- NEVER_AUTO: safety_rules/cost_ceiling/approval_flow/non_goals/audit_format/data_retention/user_consent/escalate_own_privilege/guardrails/gate

### Agent Teams — 멀티에이전트 위임

- Lead Agent + Sub-Agents (최대 위임 깊이 3단계)
- 5가지 협업 패턴: Sequential, Parallel, Debate, Supervisor, Handoff
- V1=3에이전트, V2=10, V3=50+

---

## 18. 작업 시 주의사항

### 파일 수정 규칙
- **SOT/REF 규칙**: Python contracts.py가 스키마 정본(SOT) → 타 언어 파생
- **정본 우선순위**: RULE 1.3 > PLAN 3.0 > DESIGN LOCK > DESIGN 본문 > 스키마
- **LOCK/FREEZE 항목**: 변경 절대 불가 (비용상한, Non-goal, 정체성, 승인구조 등)
- **삭제 금지**: 모든 변경은 `[DEPRECATE] + (대체 경로)` 로만 처리
- **없는 내용 창작 금지**: 신규 정책/레지스트리 값/임계값 임의 생성 불가

### 코딩 컨벤션
- **Python**: PEP 8, 타입 힌트 필수, Pydantic v2, async/await
- **TypeScript**: strict mode, Zod 검증, React 18 + zustand
- **Rust**: stable, serde derive, thiserror/anyhow
- **로깅**: JSON structured only (평문 금지), trace_id 필수

### 대화 중 참조 필요시
- 특정 모듈 상세 → 해당 DESIGN 문서 직접 읽기 (D2.0-02~08)
- 스키마 상세 → D2.1-D1~D8 직접 읽기
- API 계약 → PHASE_B1 직접 읽기
- 구현 가이드 → PHASE_B2~B7 직접 읽기
- 투자 도메인 → VAMOS_AI_INVESTING_SPEC 직접 읽기
- Agent Teams → VAMOS_AGENT_TEAMS_SPEC 직접 읽기
- SDAR → VAMOS_SDAR_DESIGN_SPECIFICATION 직접 읽기

### 성공 기준 (우선순위)
1. **정확성/근거** > 2. 이해도/품질 > 3. 안전/규제 > 4. 속도/효율 > 5. 비용

---

## 19. V1 구현 순서 (주차별 참조)

| 주차 | 구현 대상 | 핵심 참조 |
|------|----------|----------|
| 1~2 | ORANGE CORE 기본 파이프라인 (I-1→I-2→I-5→I-8) | D2.0-02, D2.1-D2, B1 |
| 3~4 | Storage/Memory + RAG (L0/L1, Chroma, BM25+Vector) | D2.0-06, D2.1-D6, B1 |
| 5~6 | Workflow Engine (LangGraph StateGraph, 5-Pipeline, TEE) | D2.0-05, D2.1-D5, B1 |
| 7~9 | UI/UX (Tauri+React, Builder/Hologram View, 3-Panel) | D2.0-08, D2.1-D8, B1 |
| 10~12 | 통합 + AI Investing Paper Trading MVP + E2E 테스트 | AI_INVESTING_SPEC, B5 |

---

## 20. 핵심 config.v1.toml LOCK 값 (20개 — 정본: PHASE_B4_CONFIG_SPEC §3 LOCK 표기 10 ∪ BASE-1.3/DESIGN 2.0 LOCK 12, 중복 2 제외)

| 설정 키 | 값 | LOCK |
|---------|-----|------|
| core.single_decision_lock | true | LOCK |
| embedding.model | bge-m3 | LOCK |
| embedding.dimension | 1024 | LOCK |
| vector_db.backend | chroma | LOCK (V1) |
| graph_db.backend | json_file | LOCK (V1) |
| cost.daily_limit | 1300 | ABSOLUTE LOCK |
| cost.monthly_limit | 40000 | ABSOLUTE LOCK |
| cost.warn_threshold | 80 | LOCK |
| cost.block_threshold | 100 | LOCK |
| semantic_cache.similarity_threshold | 0.95 | LOCK |
| logging.trace_id_required | true | LOCK |
| mcp.transport | streamable_http | LOCK |
| self_check.threshold_p0 | 70 | LOCK |
| self_check.threshold_p1 | 75 | LOCK |
| self_check.threshold_p2 | 80 | LOCK |
| self_check.soft_loop_max | 1 | LOCK |
| approval.timeout_s | 600 | LOCK |
| approval.p2_timeout_s | 300 | LOCK |
| blue_nodes.active_node_cap | 3 | LOCK (V1) |
| ui.min_width | 1280 | LOCK (V1) |
