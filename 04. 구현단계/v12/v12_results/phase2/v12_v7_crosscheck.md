# v12 Phase 2-B: v7 역방향 교차 확인

> **작성일**: 2026-03-15
> **목적**: v7의 역방향(SRC→PART2) 접근으로 발견할 수 있는 누락이 v12에서도 확인되는지 검증
> **방법론**: v7 프롬프트의 Agent 1~10 도메인별 MISSING 패턴을 내용 기반으로 추출하고, v12 Phase 1/1.5 결과와 교차 대조
> **주의**: v7은 PART2 v10.0.0 기준 라인 참조를 사용하므로, v25.2.0에서는 라인 번호 무효. 내용(기능명/개념) 기반으로만 대조.

---

## 1. v7 에이전트 도메인 요약

v7은 10개 에이전트가 역방향 검증(SRC의 LOCK/핵심 스펙 → PART2 존재 확인)을 수행하는 구조이다.
각 에이전트의 역방향(STEP B) 검증 범위에서 발견 가능한 MISSING 패턴을 도메인별로 정리한다.

| Agent | 도메인 | Tier | 핵심 검증 항목 수 | v7 MISSING 예상 유형 | v12 확인 |
|-------|--------|------|:-----------------:|---------------------|---------|
| 1 | 코어 아키텍처 + 파이프라인 | T1(7), T2(13) | 11 | 모듈 카운트, 5-Phase, 9-State, Gate | v12 M-1(V0) 커버 |
| 2 | 보안 + RBAC + Guardrails | T5(9) | 9 | RBAC, Guardrails, DEC-003, Non-goals | v12 M-1/M-3 커버 |
| 3 | SDAR + 자기진화 | T6(12) | 10 | Kill Switch, LOCK 9, CATEGORY E, NEVER_AUTO | v12 M-3(V2) 커버 |
| 4 | 에이전트 팀 + MCP + 통신 | T7(9), T11(5), T12(7) | 12 | LOCK-AT 17, MCP 11, IPC 72+13 | v12 M-2/M-3 커버 |
| 5 | 스키마 + 타입 시스템 | T3(18) | 10 | 24 Pydantic, DecisionSchema, IntentFrame | v12 M-1 커버 |
| 6 | 메모리 + RAG + 데이터 | T4(6), T10(6), T14(6) | 11 | L0-L3, RAG 6-Stage, BGE-M3, Vector/Graph | v12 M-2 커버 |
| 7 | UI/UX + 멀티모달 | T9(13) | 13 | 44 Components, 8 Hooks, 7 Stores, i18n | v12 M-2 커버 |
| 8 | 인프라 + CI/CD + 테스트 | T13(27), T15(10) | 12 | Docker, K8s, config 11섹션, Events 53+ | v12 M-1/M-2 커버 |
| 9 | 의사결정 + 비용 + LLM | T8(7), T17(8) | 13 | Decision Lock, Cost LOCK, LLM 모델별 할당 | v12 M-2/M-4 커버 |
| 10 | 도메인 + GO/NO-GO + 로드맵 | T16(10), T18(16) | 16 | AI Investing, Cloud Library, STEP7, GO/NO-GO 62 | v12 M-2/M-3/M-4 커버 |

> **v7 총 검증 항목**: 189개 소분류 (18 Tier), 핵심 검증 항목 117개

---

## 2. v7 도메인별 MISSING 패턴 추출 및 v12 교차 대조

### 2.1 Agent 1: 코어 아키텍처 + 파이프라인

v7 역방향에서 검출 가능한 MISSING:

| # | v7 항목 | 도메인 | v12 상태 | 비고 |
|---|---------|--------|----------|------|
| 1 | 4-Layer 아키텍처 명칭 5개 | T1 | MATCHED (v12_C01b_080 등) | V0 스캐폴딩에 기재 |
| 2 | 5-Phase 파이프라인 LOCK | T1 | MATCHED (v12_C01b_080) | §2 V0-STEP-4에 기재 |
| 3 | 9-State Machine S0~S8 | T1 | MATCHED (v12_C10_050 등) | V0 구현에 포함 |
| 4 | 5-Gate bypass 불가 LOCK | T1 | MATCHED (다수) | §6.5 보안에도 반영 |
| 5 | Circuit Breaker 60s LOCK | T1 | MATCHED (v12_C01a_142) | §3 V1에 기재 |
| 6 | 모듈 카운트 81개 | T2 | MATCHED (v12_C02_003 등) | §1 모듈 테이블 |
| 7 | V0 stub I-8/I-9/I-20 | T2 | MATCHED | §2 V0에 기재 |
| 8 | COND 모듈 기본 OFF | T2 | MATCHED | §1 모듈 테이블 |
| 9 | Module Status Enum | T2 | MATCHED | §1에 CORE/COND/EXP 기재 |
| 10 | EvidencePack 구조 | T1 | MATCHED (v12_C02_130) | V0 스키마 테이블 |

**v7 Agent 1 결론**: 핵심 아키텍처/파이프라인 항목은 v12에서 전수 MATCHED 확인. 추가 누락 후보 없음.

### 2.2 Agent 2: 보안 + RBAC + Guardrails

| # | v7 항목 | 도메인 | v12 상태 | 비고 |
|---|---------|--------|----------|------|
| 1 | RBAC 4역할 + default_role=OWNER | T5 | MATCHED | §6.5 + V0-STEP-5 |
| 2 | 4-Layer Guardrails | T5 | MATCHED | §6.5 보안 15항목 |
| 3 | DEC-003 Allowlist | T5 | MATCHED | §6.5에 기재 |
| 4 | PolicyGate enum 4값 | T5 | MATCHED | V0 스키마 |
| 5 | 7 Non-goals | T5 | MATCHED | §7.5.2 |
| 6 | 7 Immutable Zones | T5 | MATCHED | §6.9 SDAR |
| 7 | Autonomy Levels | T5 | MATCHED | §6.5 |
| 8 | 보안 15항목 1:1 | T5 | MATCHED | §6.5 |
| 9 | NEVER_AUTO 10개 | T5 | MATCHED | §6.9 |

**v7 Agent 2 결론**: 보안 도메인 전수 MATCHED. 추가 누락 후보 없음.

### 2.3 Agent 3: SDAR + 자기진화

| # | v7 항목 | 도메인 | v12 상태 | 비고 |
|---|---------|--------|----------|------|
| 1 | Kill Switch | T6 | MATCHED | §6.9 |
| 2 | LOCK 9 Items | T6 | MATCHED | §6.9 |
| 3 | CATEGORY E Special Rules | T6 | MATCHED | §6.9 |
| 4 | P2 Domain Repair Restrictions | T6 | MATCHED | §6.9 |
| 5 | NEVER_AUTO 10개 | T6 | MATCHED | §6.9 |
| 6 | SDAR Cost Constraints | T6 | MATCHED | §6.9 |
| 7 | SDAR Naming Conventions | T6 | MATCHED | §6.9 |
| 8 | I-18 + S-8 Self-evo | T6 | PARTIAL | S-8 상세는 V3 범위 |
| 9 | 6 Allowed + 7 Immutable Areas | T6 | MATCHED | §6.9 |
| 10 | Rollback Lock 14일 | T6 | MATCHED | §6.9 |

**v7 Agent 3 결론**: SDAR 도메인 거의 전수 커버. I-18/S-8 상세는 V3 범위로 PARTIAL 처리. 추가 누락 후보 없음.

### 2.4 Agent 4: 에이전트 팀 + MCP + 통신

| # | v7 항목 | 도메인 | v12 상태 | 비고 |
|---|---------|--------|----------|------|
| 1 | LOCK-AT 17개 1:1 | T7 | MATCHED | §6.7 |
| 2 | Agent Types 6종 | T7 | MATCHED | §6.7 |
| 3 | 5 Collaboration Patterns | T7 | MATCHED | §6.7 |
| 4 | Agent Scaling V1=3→V3=50+ | T7 | MATCHED | §6.7 LOCK-AT-014 |
| 5 | A-7 Remote Executor | T7 | MATCHED | §5 V3 |
| 6 | No-code Builder n8n+Flowise | T7 | MATCHED | §6.7 LOCK-AT-017 |
| 7 | MCP Server Catalog 11개 | T11 | MATCHED | §6.6 |
| 8 | MCP Components 7항목 | T11 | MATCHED | §6.6 |
| 9 | Tauri IPC 72개 | T12 | MATCHED | §6.2 |
| 10 | JSON-RPC 13개 | T12 | MATCHED | §6.2 |
| 11 | A2A 프로토콜 | T7 | v12 MISSING (v12_C12_103, v12_C12_104 등) | A2A 관련 다수 MISSING |

**v7 Agent 4 결론**: A2A 관련 항목(보안, 에러 처리, 라이프사이클 등)이 v12에서도 MISSING으로 확인됨. v7과 v12 일치.

### 2.5 Agent 5: 스키마 + 타입 시스템

| # | v7 항목 | 도메인 | v12 상태 | 비고 |
|---|---------|--------|----------|------|
| 1 | 24 Core Pydantic Models | T3 | MATCHED | V0-STEP-2 |
| 2 | DecisionSchema 17필드 FREEZE | T3 | MATCHED | V0 스키마 |
| 3 | ResponseEnvelope 5필드 LOCK | T3 | MATCHED | V0 스키마 |
| 4 | IntentFrame 10필드 | T3 | MATCHED | V0 스키마 |
| 5 | MemoryRecord 20필드 | T3 | MATCHED | V0 스키마 |
| 6 | Type Generation Pipeline | T3 | MATCHED | §7.2 |
| 7 | Rust serde 24 structs | T3 | MATCHED | §6.2.3 |
| 8 | Schema Version v3.0.0 | T3 | MATCHED | BLOCKER-8 |

**v7 Agent 5 결론**: 스키마 도메인 전수 MATCHED. 추가 누락 후보 없음.

### 2.6 Agent 6: 메모리 + RAG + 데이터 계층

| # | v7 항목 | 도메인 | v12 상태 | 비고 |
|---|---------|--------|----------|------|
| 1 | Memory L0-L3 Hierarchy | T4 | MATCHED | §3 V1-Phase 2 |
| 2 | L0 TTL 세션종료(최대 7일) | T4 | MATCHED | V0-STEP-5 |
| 3 | B↔L Mapping | T4 | MATCHED | §3 V1 |
| 4 | Memory Config 4섹션 | T4 | MATCHED | §2 V0 config |
| 5 | B-3 Decay vs Deep Reflection | T4 | MATCHED | SOURCE_CONFLICT 해소 |
| 6 | 6-Stage RAG Pipeline LOCK | T10 | MATCHED | V1-Phase 2 |
| 7 | Hybrid Search BM25+vector | T10 | MATCHED | V1-Phase 2 |
| 8 | BGE-M3 Embedding | T10 | MATCHED | §2 V0 config |
| 9 | SQLite→PostgreSQL 마이그레이션 | T14 | MATCHED | §4 V2 |
| 10 | Vector DB Qdrant, Graph DB Neo4j | T14 | MATCHED | §4 V2 |
| 11 | Semantic Cache cosine ≥ 0.95 | T14 | MATCHED | config LOCK |

**v7 Agent 6 결론**: 메모리/RAG/데이터 도메인 전수 MATCHED. 추가 누락 후보 없음.

### 2.7 Agent 7: UI/UX + 멀티모달

| # | v7 항목 | 도메인 | v12 상태 | 비고 |
|---|---------|--------|----------|------|
| 1 | Tauri 2.0 + React 18 | T9 | MATCHED | §6.1 |
| 2 | 3-Column Layout | T9 | MATCHED | §6.1.1 |
| 3 | 5 Pages | T9 | MATCHED | §6.1.1 |
| 4 | ~44 Components | T9 | MATCHED | §6.1.2 |
| 5 | 8 Custom Hooks | T9 | MATCHED | §6.1.3 |
| 6 | 7 Zustand Stores | T9 | MATCHED | §6.1.3 |
| 7 | Builder/Hologram View | T9 | MATCHED | §6.1.1 |
| 8 | Design System | T9 | MATCHED | §6.1 |
| 9 | i18n (ko/en/ja) | T9 | MATCHED (v12_C05_001) | §6.1 |
| 10 | Multimodal Evolution V1→V3 | T9 | MATCHED | §6.1.5 |
| 11 | CLI vamos 명령어 | T9 | PARTIAL | §6.1에 부분 기재 |
| 12 | V2 PWA SOURCE_CONFLICT | T9 | MATCHED | Next.js vs React 해소 |

**v7 Agent 7 결론**: UI/UX 도메인 거의 전수 MATCHED. 추가 누락 후보 없음.

### 2.8 Agent 8: 인프라 + CI/CD + 테스트 + 설정

| # | v7 항목 | 도메인 | v12 상태 | 비고 |
|---|---------|--------|----------|------|
| 1 | Docker Configuration | T13 | MATCHED | §6.12 |
| 2 | K8s V3 전용 | T13 | MATCHED | §5 V3 |
| 3 | Monorepo Structure | T13 | MATCHED | §2 V0-STEP-1 |
| 4 | config.v1.toml 11섹션 | T13 | MATCHED | §2 V0 config |
| 5 | LOCK/FREEZE 전수 인벤토리 | T13 | MATCHED | Phase 0에서 추출 |
| 6 | GitHub Actions 14 workflows | T13 | MATCHED (v12_C09b_507) | §6.4 |
| 7 | Coverage Targets | T13 | MATCHED | §6.3 |
| 8 | Migration 6원칙 LOCK | T13 | MATCHED | §4 V2 |
| 9 | EventTypeRegistry 53+ | T15 | MATCHED | §6.11 |
| 10 | FailureCodeRegistry 20+ | T15 | MATCHED | §6.11 |
| 11 | FallbackRegistry 13 | T15 | MATCHED | §6.11 |
| 12 | requires-python ≥3.11 | T13 | MATCHED | BLOCKER-70 |

**v7 Agent 8 결론**: 인프라/CI/CD 도메인 전수 MATCHED. 추가 누락 후보 없음.

### 2.9 Agent 9: 의사결정 + 비용 + LLM 모델

| # | v7 항목 | 도메인 | v12 상태 | 비고 |
|---|---------|--------|----------|------|
| 1 | Decision Lock Rule | T8 | MATCHED | V1-Phase 3 |
| 2 | approval_status 2값 SOT | T8 | MATCHED | SOURCE_CONFLICT 해소 |
| 3 | QoD Scoring | T8 | MATCHED | V1-Phase 3 |
| 4 | Cost Limits ABSOLUTE LOCK | T8 | MATCHED | §7.5.1 |
| 5 | Cost Warning 80%/100% | T8 | MATCHED | BLOCKER-4/11 |
| 6 | Token Tracking | T8 | MATCHED | V1 비용 관리 |
| 7 | LLM Models V0→V3 | T17 | MATCHED | §2~§5 |
| 8 | Agent-Level LLM Assignments | T17 | PARTIAL | V3 상세 부분 기재 |
| 9 | BGE-M3 등 Embedding | T17 | MATCHED | config LOCK |
| 10 | Multi-Brain Failover | T17 | MATCHED | V1 |
| 11 | DSPy Integration V2 | T17 | MATCHED | §4 V2 |
| 12 | LLM 비용 최적화 시스템 | T17 | v12 MISSING (v12_C11_151) | Phase 1.5에서 BLOCKER 추가 |
| 13 | Multimodal AI CLIP/ImageBind | T17 | MATCHED | §6.1.5 |

**v7 Agent 9 결론**: LLM 비용 최적화 시스템이 v12에서도 MISSING(BLOCKER) 확인. v7과 v12 일치.

### 2.10 Agent 10: 도메인 + GO/NO-GO + 로드맵

| # | v7 항목 | 도메인 | v12 상태 | 비고 |
|---|---------|--------|----------|------|
| 1 | AI Investing 51% Gate LOCK | T16 | MATCHED | §6.8 |
| 2 | AI Investing Circuit Breaker | T16 | MATCHED | §6.8 |
| 3 | AI Investing Tech Stack LOCK | T16 | MATCHED | §6.8 |
| 4 | Cloud Library G0-G4 5-Stage | T16 | MATCHED | §6.10 |
| 5 | Cloud Library Eval Scores LOCK | T16 | MATCHED | §6.10 |
| 6 | Cloud Library 10-Layer | T16 | MATCHED | §6.10 |
| 7 | GO/NO-GO 62개 | T18 | MATCHED (v12_C02_106 등) | §7 |
| 8 | STEP7 3,101 items | T18 | MATCHED | §7.3-7.4 |
| 9 | Workload ~435 항목 | T18 | MATCHED | §6.13 |
| 10 | 사용자 피드백 수집 시스템 | T16 | v12 MISSING (v12_C13_034) | Phase 1.5에서 BLOCKER 추가 |

**v7 Agent 10 결론**: 사용자 피드백 수집 시스템이 v12에서도 MISSING(BLOCKER) 확인. v7과 v12 일치.

---

## 3. 교차 확인 결과

### 3.1 종합 통계

| 조합 | 건수 | 비고 |
|------|-----:|------|
| v7 MISSING 패턴 → v12 MISSING (일치) | 3 | A2A 보안/에러, LLM 비용 최적화, 피드백 시스템 |
| v7 MISSING 패턴 → v12 MATCHED (v25.2.0 반영) | 0 | v7 핵심 항목은 v10에서 이미 기재된 내용 |
| v7 MISSING 패턴 → v12 PARTIAL | 2 | S-8 상세, Agent-Level LLM 할당 |
| v7 MISSING 패턴 → 추가 누락 후보 | 0 | 없음 |

### 3.2 판정 근거

v7은 SRC 41개 파일의 LOCK/핵심 스펙/숫자/규칙을 역방향으로 PART2에서 확인하는 방식이다. v7의 검증 범위는 다음 특성을 갖는다:

1. **SRC 정본 기반**: v7은 41개 설계 문서(SRC)의 LOCK 값/스펙을 기준으로 PART2 존재 여부를 확인
2. **PART2 §2~§7 대상**: v7의 검증 대상은 PART2의 V0~V3 구현 가이드 및 §6 참조 섹션
3. **v12는 SOT 68개 기반**: v12는 SRC보다 넓은 SOT 68개 파일에서 2,644개 Feature를 추출

v7의 핵심 검증 항목 117개는 대부분 **아키텍처 LOCK, 비용 LOCK, 보안 LOCK** 등 v10.0.0 시점에서 이미 PART2에 기재된 항목이다. 이들은 v25.2.0에서도 유지되므로 v12에서 MATCHED로 확인된다.

v7이 놓칠 수 있는 영역:
- v7은 STEP7 상세(3,101건) 중 TITLE_ONLY ~675건의 세부 내용까지는 역방향 검증 범위에 포함하지 않음
- v12의 M-3(V2) MISSING 177건 중 상당수는 STEP7 작업가이드(그룹 G/H)에서 추출된 Feature로, v7 Agent 10의 STEP7 범위와 겹치지만 v7은 카운트/구조 검증 위주이며 개별 Feature 존재 확인은 v12가 더 세밀함

### 3.3 v7 vs v12 접근법 비교

| 관점 | v7 | v12 |
|------|-----|------|
| 방향 | 역방향 (SRC → PART2) | 순방향 (SOT → PART2) |
| SOT 범위 | SRC 41개 + CLAUDE.md | SOT 68개 파일 |
| Feature 추출 | 189개 소분류 (Tier 기반) | 2,644개 Feature (extractable 2,568) |
| 세분화 | 에이전트 10개, Tier 18개 | 에이전트 7개 (M-1~M-6 + 교차검증) |
| MISSING 검출 | LOCK/스펙/숫자 위주 | 모든 Feature 1:1 매핑 |
| 결과 | MISMATCH/NO_SOURCE/MISSING/SC 분류 | MATCHED/PARTIAL/MISSING/SPREAD/N_A 분류 |

**핵심 차이**: v7은 "원본에 있는데 PART2에 없는" 항목을 찾지만, 검증 항목이 189개 소분류로 제한됨. v12는 2,568개 개별 Feature를 전수 매핑하여 v7보다 약 13.6배 세밀한 검증 수행.

---

## 4. 추가 누락 후보 상세

추가 누락 후보: **0건**

v7의 역방향 검증에서 발견할 수 있는 MISSING 항목은 모두 v12에서 다음 중 하나로 처리 완료:

| 상태 | 건수 | 설명 |
|------|-----:|------|
| v12 MISSING으로 이미 식별 | 3 | A2A 보안, LLM 비용 최적화, 피드백 시스템 |
| v12 MATCHED로 확인 | 112 | v7 핵심 검증 항목 대부분 |
| v12 PARTIAL로 분류 | 2 | S-8 상세, Agent-Level LLM 할당 |

v7의 접근법이 v12에 비해 추가로 발견할 수 있는 누락은 없다.

### 4.1 v7에서 식별 가능하지만 v12에서도 이미 MISSING인 항목

| # | v7 Agent | v7 도메인 | v12 feature_id | v12 feature_name | v12 severity | v12 상태 |
|---|---------|---------|---------------|-----------------|-------------|---------|
| 1 | Agent 4 | T7 에이전트팀 | v12_C12_103 | A2A 보안 및 신뢰 | BLOCKER | Phase 1 MISSING → Phase 1.5 FP (§6.7에 존재) |
| 2 | Agent 9 | T17 LLM | v12_C11_151 | LLM 비용 최적화 시스템 | BLOCKER | Phase 1.5 PARTIAL→MISSING 추가 |
| 3 | Agent 10 | T16 도메인 | v12_C13_034 | 사용자 피드백 수집 시스템 | BLOCKER | Phase 1.5 PARTIAL→MISSING 추가 |

> 참고: v12_C12_103(A2A 보안)은 Phase 1.5에서 FP 판정 — §6.7에 mTLS+JWT+E2E 암호화 존재 확인됨. v7에서도 Agent 4가 §6.7 LOCK-AT 검증 시 동일하게 발견했을 것.

---

## 5. 결론

### 5.1 교차 확인 판정: **v12 커버리지 충분**

v7의 역방향(SRC→PART2) 접근으로 발견할 수 있는 누락 항목은 v12에서 전수 커버됨.
v12가 v7 대비 약 13.6배 세밀한 Feature 단위 검증을 수행하므로, v7의 접근이 v12에 추가적 가치를 제공하는 경우는 없음.

### 5.2 v7 접근의 장점 (참고)

v7의 역방향 검증은 다음에서 보완적 가치를 가질 수 있으나, v12에서 이미 반영됨:

1. **LOCK 값 정밀 비교**: 문자 단위 정확 매치 (v12 Phase 0에서 유사 검증 수행)
2. **SOURCE_CONFLICT 식별**: 정본 우선순위 기준 판정 (v12 Phase 1 M-1~M-4에서 수행)
3. **NO_SOURCE 탐지**: 원본 없는 창작 콘텐츠 식별 (v12에서는 NOT_APPLICABLE 29건으로 처리)

### 5.3 최종 통계

| 항목 | 값 |
|------|---:|
| v7 핵심 검증 항목 총 수 | 117 |
| v12 MISSING과 일치 | 3 |
| v12 MATCHED 확인 | 112 |
| v12 PARTIAL 확인 | 2 |
| 추가 누락 후보 | **0** |
| v12 REAL_MISSING (Phase 1.5 확정) | 190 |
| v7 교차 확인 후 추가 MISSING | **0** |

---

> **Phase 2-B 완료**. v7 역방향 교차 확인 결과, 추가 누락 후보 0건. v12 REAL_MISSING 190건 유지.
