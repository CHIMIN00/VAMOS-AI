# Obsidian-매트릭��� 매핑

> **세션**: P0-2
> **작성일**: 2026-04-04
> **근거**: Obsidian Strategy v3.0 §3 + STRATEGY_08 매트릭스 v1.0 §3~§4
> **대상**: 17개 폴더 (00~15 + 99_RAW) × 매트릭스 20개 셀 단위

---

## 매트릭스 셀 약어 참조

```
D행(설계):  D1(설계 정합성) | D2(변경 추적) | D3(설계↔코드 정합) | DF(설계 역류)
B행(구축):  B1(환경 세팅) | B2a(하네스) | B2b(컨텍스트) | B2c(다중언어) | B3(품질 평가) | BF(구축 역류)
R행(작동):  R1(런타임 설계) | R2a(코어) | R2b(도메인) | R2c(프론트) | R3(운영) | RF(런타임 역류)
X행(횡��):  X1(전략 수립) | X2(횡단 실행) | X3(횡단 운영) | XF(횡단 역류)
```

---

## 폴더별 매트릭스 매핑

### 00_HUB — 전체 진입점 (7개 노트)

| 노트 | 1차 셀 | 2차 셀 | 역할 |
|------|--------|--------|------|
| VAMOS-HOME.md | B2b | X1 | 전체 시스템 홈 — 컨텍스트 진��점 |
| TIER-MAP.md | D1 | B2b | T0~T6 계층 시각화 — 설계 정합 참조 |
| DEPENDENCY-GRAPH.md | D1 | D2 | 112개 엣지 매핑 — 정합성 + 변경 영향 분석 |
| LOCK-DECISION-REGISTRY.md | D1 | D3 | 469+ LOCK — 설계 정합 + 코드 대조 |
| MODULE-MAP.md | D1 | R2b | 187개 모듈 전체 — 설계 + 도메인 구현 참조 |
| 39-FILE-MASTER-INDEX.md | D1 | B2b | SOT 39파일 계층 — 정합 + 컨텍스트 |
| SOT2-STRUCTURE-MAP.md | D1 | B2b | SOT 2 38폴더 구조 — 정합 + 라우팅 |

**요약**: 00_HUB는 **D1(설계 정합성)**을 1차 기능으로, **B2b(컨텍스트 관리)**를 2차 기능으로 수행.

---

### 01_GOVERNANCE — T0 거버넌스 (1개 노트)

| 노트 | 1차 �� | 2차 셀 | 역할 |
|------|--------|--------|------|
| T0-Governance.md | D1 | X1 | R1~R11 규칙, LOCK, 비용한도 — 정합 원천 + 횡단 전략 근거 |

**요약**: **D1** 정합성 원천. T0는 전체 시스템의 규칙 정의이므로 D1의 핵심 입력.

---

### 02_CORE-INTELLIGENCE — T1 검증/보조 (2개 노트)

| 노트 | 1차 셀 | 2�� 셀 | 역할 |
|------|--------|--------|------|
| T1-Verifier-Engines.md | R2a | D3 | C/D 시리즈 검증엔진 — 코어 런타임 + 설계 대조 |
| T1-Auxiliary-Modules.md | R2a | D1 | I-1~I-25 보조모듈 — 코어 런타임 + 정합 참��� |

**요약**: **R2a(코어 런타임)** 중심. 검증 엔진은 D3(설계↔코드 정합)에도 관여.

---

### 03_EXECUTION — T2 실행 (2개 노트)

| 노트 | 1차 셀 | 2차 셀 | 역할 |
|------|--------|--------|------|
| T2-Blue-Node.md | R2b | R1 | 7 BN 컴포넌트 — 도메인 실행 + 런타임 설계 |
| T2-COND-Modules.md | R2b | D1 | 106 COND, CAT-A~G — 도메인 실행 + 정합 |

**요약**: **R2b(도메인 실행)** 중심. Blue Node 아키텍처와 조건부 모듈.

---

### 04_FEATURES — T3 기능 도메인 (9개 노트)

| 노트 | 1차 셀 | 2차 셀 | 역할 |
|------|--------|--------|------|
| T3-Multimodal.md | R2b | R2a | 미디어 처리, IO Pipeline |
| T3-PKM.md | R2b | R2a | 지식관리, SM-2 |
| T3-Workflow-RPA.md | R2b | — | RPA, 자동화 |
| T3-Education.md | R2b | — | 교육, 학습 |
| T3-Health-EmotionAI.md | R2b | — | 웰니스, EmotionAI |
| T3-Dev-Tools.md | R2b | B2c | API/SDK — 도메인 + 다중언어 동기화 |
| T3-A2A-Protocol.md | R2b | R2a | 에이전트 통신 JSON-RPC |
| T3-Business-Model.md | R2b | — | 비즈니스 모델 |
| T3-Agent-Protocol.md | R2b | R1 | L0~L4 상호운용 — 런타임 설계 |

**요약**: 전부 **R2b(도메인 실행)**. 일부(Dev-Tools, Agent-Protocol)는 B2c/R1에도 관여.

---

### 05_INFRASTRUCTURE — T4 인프라 (4개 노트)

| 노트 | 1차 셀 | 2차 �� | 역할 |
|------|--------|--------|------|
| T4-Rust-Tauri.md | B2c | R2c | IPC, serde — 다중언어 동기화 + 프론트 |
| T4-CICD.md | B2a | X2 | GitHub Actions — 하네스 + 횡단 실행 |
| T4-MCP.md | R2a | B2c | Streamable HTTP — 코어 런타임 + 타입 동기화 |
| T4-MLOps.md | R3 | B3 | 모델 운영 — 운영 + 품질 평가 |

**요약**: 인프라는 **B2a/B2c/R2a/R3** 복수 셀에 분산. Build와 Run 경계에 걸침.

---

### 06_QUALITY — T5 품질 (4��� 노트)

| 노트 | 1차 셀 | 2차 셀 | 역할 |
|------|--------|--------|------|
| T5-Benchmark.md | B3 | X2 | 평가/벤치마크 — 품질 + 횡단 테스트 |
| T5-File-Context.md | B2b | — | 컨텍스트 관리 (Lost-in-Middle, Ms-PoE) |
| T5-v12-Additions.md | R2b | — | 웰니스/CBT/SM2 구현 상��� |
| T5-v23-Extensions.md | R2b | — | 87개 확장 항목 |

**요약**: **B3(품질 평가)** + **B2b(컨텍��트)** + **R2b(도메인 확장)**.

---

### 07_SYSTEM-WIDE — T6 시스템 전역 (13개 노���)

| 노트 | 1차 셀 | 2차 셀 | 역할 |
|------|--------|--------|------|
| T6-UI-UX.md | R2c | — | Tauri+React 프론트엔드 |
| T6-Security.md | X1 | X2 | STRIDE/RBAC — 횡단 보안 전략 + 실행 |
| T6-Agent-Teams.md | R2b | R1 | PARL 9 types — 도메인 + 런타임 설계 |
| T6-Memory-RAG.md | R2a | D1 | L0~L3, 6-stage RAG — 코어 + 정합 |
| T6-SDAR.md | R2a | R3 | 자가진단/복구 — 코어 + 운영 |
| T6-Self-Evolution.md | R2a | �� | I-18, S-series 자기 진화 |
| T6-RT-BNP-DCL.md | R2b | — | 실시간 뉴스 처리 |
| T6-Cloud-Library.md | R2b | R3 | 클라우드 라이브러리 |
| T6-Brain-Adapter.md | R2a | R1 | HAL Multi-LLM — 코어 + 런타임 설계 |
| T6-EXP-Modules.md | R2b | — | B/D/EVX 실험 모듈 |
| T6-Hologram.md | R2c | R2a | Main LLM 출력 — 프론트 + 코�� |
| T6-Event-Logging.md | X2 | R3 | trace_id JSON — 횡단 + 운영 |
| T6-Operations.md | R3 | X3 | 운영/장애대응 — 작동 + 횡단 |

**요약**: T6는 가장 넓게 분산. **R2a/R2b/R2c/R3/X1/X2/X3** 모두 커버.

---

### 08_AI-INVESTING — 특화 도메인 (4개 노트)

| ��트 | 1차 ��� | 2차 셀 | 역할 |
|------|--------|--------|------|
| AI-Investing-Overview.md | R2b | D1 | 28 하위도메인 맵 |
| AI-Investing-Core.md | R2b | �� | 00_core~07 |
| AI-Investing-Advanced.md | R2b | — | 08~15 |
| AI-Investing-Infrastructure.md | R2b | R2a | 16~21 인프라 |

**요약**: 전부 **R2b(도메인 실행)**. 투자 특화 도메인.

---

### 09_DESIGN-DOCS — 설계 문서 (12개 노트)

| 노트 | 1차 셀 | 2차 셀 | 역할 |
|------|--------|--------|------|
| D2.0-01~08 (8개) | D1 | D3 | 아키텍처 정본 — 정합 + 코드 대조 |
| D2.1-Schema-Index.md | D1 | B2c | 스키마 인덱스 — 정합 + 타입 동기화 |
| SPEC-Agent-Teams.md | D1 | R2b | Agent Teams 특화 스펙 |
| SPEC-SDAR.md | D1 | R2a | SDAR 특화 스펙 |
| SPEC-Cloud-Library.md | D1 | R2b | Cloud 특화 스펙 |

**요약**: 전부 **D1(설계 정합성)** 1차. 설계 문서의 본거지.

---

### 10_CONCEPTS — 횡단 개념 (37개 노트)

| 노트 그룹 | 개수 | 1차 셀 | 2차 셀 | 역할 |
|----------|------|--------|--------|------|
| 시스템 개념 (5-Gate, LOCK 등) | 10 | D1 | X1 | 핵심 개념 정합 + 횡단 전략 |
| 모듈 시리즈 (A/B/C/D/EVX) | 5 | D1 | R2b | 시리즈별 요약 |
| COND 카테고리 (CAT-A~G) | 7 | D1 | R2b | 조건부 모듈 분류 |
| 기술/인프라 개념 | 15 | D1/R1 | X1 | 기술 기반 정의 |

**요약**: **D1(정합)** 중심 + **X1(횡단 전략)** 보조. 개념 노트는 설계 정합의 참조 자산.

---

### 11_WORKFLOWS — 워크플로우 (3개 노트)

| 노트 | 1차 셀 | 2차 셀 | 역할 |
|------|--------|--------|------|
| End-to-End-Request-Flow.md | R1 | R2a | S0→S8 전체 흐름 — 런타임 설계 |
| Gate-Rejection-Paths.md | R1 | X1 | Gate 거부 분기 — 안전 횡단 |
| Self-Check-Loop.md | R2a | D3 | Soft-loop — 코어 + 설계 대조 |

**요약**: **R1(런타임 설계)** + **R2a(코어)**. 실행 흐름 정의.

---

### 12_IMPLEMENTATION — 구현 (11개 노트)

| 노트 | 1차 셀 | 2차 셀 | 역할 |
|------|--------|--------|------|
| STEP7-Implementation-Bridge.md | B2a | D1 | A~P 16카테고리 매핑 — 하네스 + 정합 |
| Release-Track-Map.md | X1 | B2a | R1~R6 릴리스 트랙 |
| STEP6-Completed-Items.md | B2a | — | 1,556건 완료 기록 |
| v12-Additions.md | R2b | — | 웰니스/CBT/SM2 |
| v23-Extensions-87.md | R2b | — | 87개 확장 |
| Current-Phase.md | B2b | X1 | 현재 진행 상태 |
| V8~V13-Results (6개) | B3 | — | 버전별 구현 결과 평가 |

**요약**: **B2a(하네스)** + **B3(품질)** + **R2b(도메인)**. 구현 브릿지.

---

### 13_GUIDES — 가이드 (4개 노트)

| 노트 | 1차 셀 | 2차 셀 | 역할 |
|------|--------|--------|------|
| SESSION-GUIDES-MAP.md | B2b | — | 34개 세션 인덱스 — 컨텍스트 |
| Beginner-Guide.md | B1 | — | 초보자 환경 세팅 |
| Implementation-Part1.md | B2a | — | 구현가이드 Part1 |
| Implementation-Part2.md | B2a | — | 구현가이드 Part2 |

**요약**: **B2a/B2b/B1**. 구축 관련 가이드.

---

### 14_AUDIT — 감사 (3개 노���)

| 노트 | 1차 셀 | 2차 셀 | 역할 |
|------|--------|--------|------|
| SOT-Consistency-Audits.md | D1 | D3 | 26개 검증 리포트 — 정합 감사 |
| Phase11-Validation-Summary.md | D3 | B3 | Phase 11 검증 — 설계↔코드 + 품질 |
| Known-Issues-Registry.md | D1 | X3 | 45개 이슈 + 알려진 문제 — 정합 + 횡단 운영 |

**요약**: **D1(정합)** + **D3(설계↔코드)**. 감사/검증 자산.

---

### 15_RULES — 규칙 (4개 노트)

| 노트 | 1차 셀 | 2차 셀 | 역할 |
|------|--------|--------|------|
| BASE-1.3-Rules.md | D1 | X1 | R1~R11 + 비목표 — 절대 규��� |
| PLAN-3.0-Roadmap.md | D1 | X1 | DEC-001~017 — 아키텍처 결정 |
| Non-Goals.md | X1 | — | 7개 절대 금지 — 횡단 보안 |
| Part2-Master-Reference.md | D1 | B2a | 모든 도메인 근거 |

**요약**: **D1(정합)** 원천 + **X1(횡단 전략)** 근거. 최상위 규칙.

---

### 99_RAW — 원본 심링크 (3개 디렉토리)

| 디렉토리 | 1차 셀 | 역할 |
|----------|--------|------|
| sot/ → D:\VAMOS\docs\sot\ | D1 | SOT 정본 68개 직접 접근 |
| sot2/ → D:\VAMOS\docs\sot 2\ | D1 | SOT 2 2,654개 직접 접근 |
| guides/ → D:\VAMOS\docs\guides\ | B2a | 구현가이드 직접 접근 |

**요약**: 원본 참조 계층. 모든 노트의 최종 근거를 직접 확인하는 통로.

---

## 매트릭스 셀별 역매핑 — "이 셀에서 어떤 Obsidian 폴더를 참조하는가"

| 셀 | 1차 폴더 | 보조 폴더 |
|----|----------|----------|
| **D1** | 00_HUB, 01_GOV, 09_DESIGN, 10_CONCEPTS, 14_AUDIT, 15_RULES, 99_RAW | 02~03, 06, 08, 12 |
| **D2** | 00_HUB(DEPENDENCY-GRAPH) | 09_DESIGN |
| **D3** | 09_DESIGN, 14_AUDIT | 02_CORE, 10_CONCEPTS, 11_WORKFLOWS |
| **B1** | 13_GUIDES(Beginner) | 14_AUDIT |
| **B2a** | 12_IMPLEMENTATION, 13_GUIDES(Part1/2), 99_RAW(guides) | 05_INFRA(CICD) |
| **B2b** | 00_HUB, 06_QUALITY(File-Context), 12_IMPL(Current-Phase) | 13_GUIDES(SESSION) |
| **B2c** | 05_INFRA(Rust-Tauri, MCP) | 09_DESIGN(Schema) |
| **B3** | 06_QUALITY(Benchmark), 12_IMPL(V*-Results) | 05_INFRA(MLOps) |
| **R1** | 11_WORKFLOWS, 10_CONCEPTS(기술) | 04_FEATURES(Agent-Protocol) |
| **R2a** | 02_CORE, 07_SYSTEM(Memory/SDAR/Brain/Self-Evo) | 05_INFRA(MCP), 11_WORKFLOWS |
| **R2b** | 03_EXEC, 04_FEATURES(9개), 07_SYSTEM(Teams/RT/Cloud/EXP), 08_AI-INV | 12_IMPL(v12/v23) |
| **R2c** | 07_SYSTEM(UI-UX, Hologram) | 05_INFRA(Rust-Tauri) |
| **R3** | 07_SYSTEM(Operations, MLOps) | 07_SYSTEM(Cloud-Library) |
| **X1** | 07_SYSTEM(Security), 15_RULES, 01_GOV | 10_CONCEPTS, 12_IMPL(Release) |
| **X2** | 05_INFRA(CICD), 07_SYSTEM(Event-Logging, Security) | 06_QUALITY(Benchmark) |
| **X3** | 07_SYSTEM(Operations), 14_AUDIT(Known-Issues) | — |
| **DF/BF/RF/XF** | (피드백은 해당 행의 셀을 역방향 참조 — 별도 폴더 없음) | — |

---

## 커버리지 검증

| 매트릭스 셀 | Obsidian 폴더 존재 | 판정 |
|---|---|---|
| D1 | 00, 01, 09, 10, 14, 15, 99 | COVERED |
| D2 | 00(DEPENDENCY-GRAPH) | COVERED (변경 추적은 도구 기반) |
| D3 | 09, 14 | COVERED |
| B1 | 13 | COVERED |
| B2a | 05, 12, 13, 99 | COVERED |
| B2b | 00, 06, 12, 13 | COVERED |
| B2c | 05, 09 | COVERED |
| B3 | 06, 12 | COVERED |
| R1 | 10, 11 | COVERED |
| R2a | 02, 07 | COVERED |
| R2b | 03, 04, 07, 08, 12 | COVERED |
| R2c | 07 | COVERED |
| R3 | 05, 07 | COVERED |
| X1 | 01, 07, 15 | COVERED |
| X2 | 05, 07 | COVERED |
| X3 | 07, 14 | COVERED |
| F열 (DF/BF/RF/XF) | (역류 프로토콜 — 폴더 매핑 불필요) | N/A |

**판정**: 16개 실질 셀(F열 제외) 전부 1개 이상 Obsidian 폴더 매핑 완료. **누락 셀 없음.**
