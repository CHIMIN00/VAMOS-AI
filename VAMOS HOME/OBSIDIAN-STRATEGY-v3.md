---
tags: [type/hub, strategy]
aliases: [전략, Obsidian Strategy, 옵시디언 전략]
description: "VAMOS AI Obsidian Knowledge Graph 전략 v3.0 — 누락 없는 최종본"
created: 2026-03-30
---

# VAMOS AI Obsidian Knowledge Graph 전략 v3.0

> **목표**: VAMOS AI의 모든 내용(396,000줄, 1,451개 파일)을 Obsidian으로 구조화하여,
> 질문/검색 시 누락 없이 파악 가능하고, 모든 시스템 간 연결을 추적 가능하게 한다.

---

## 1. 전략 수립 배경

### 1.1 문제 정의

| 문제 | 상세 |
|------|------|
| **대용량** | 396,000줄 — Claude 1M 컨텍스트로도 한번에 불가 (약 16배 초과) |
| **현재 참조** | 매 대화에서 CLAUDE.md 697줄만 자동 로드 — 전체의 0.2% |
| **폴더 구조 한계** | 계층적 트리 구조라 횡단 연결이 보이지 않음 |
| **모듈 복잡성** | 187개 모듈 (8 시리즈 81개 + COND 106개) 간 교차 참조 추적 불가 |

### 1.2 VAMOS 전체 문서 규모

| 영역 | 파일 수 | 라인 수 | 경로 |
|------|---------|---------|------|
| SOT (정본) | 68 | 89,413 | `D:\VAMOS\docs\sot\` |
| SOT 2 (확장) | 648 | 169,628 | `D:\VAMOS\docs\sot 2\` |
| Guides | 38 | 37,904 | `D:\VAMOS\docs\guides\` |
| 구현단계 | 696 | 98,795 | `D:\VAMOS\04. 구현단계\` |
| CLAUDE.md | 1 | 697 | `D:\VAMOS\CLAUDE.md` |
| **합계** | **1,451** | **~396,000** | |

### 1.3 전략 진화 과정

| 버전 | 노트 수 | 커버리지 | 주요 변경 |
|------|---------|---------|----------|
| v1.0 | 66 | ~40% | 초기 설계 — 도메인+개념 기본 |
| v2.0 | 107 | ~80% | GAP 10개 보완, 워크플로우/감사/규칙 추가 |
| **v3.0** | **120+** | **~90%** | COND CAT-A~G, A-Series, v12/v23, 용어충돌, Part2 추가 |

---

## 2. VAMOS 전체 구성 요소 (빠짐없이)

### 2.1 모듈 시스템 — 187개 전체

| 시리즈 | 개수 | 풀네임 | 분류 | 버전 |
|--------|------|--------|------|------|
| I-Series | 25 | Internal Core Modules | CORE 17, COND 5, EXP 3 | V1~V3 |
| E-Series | 16 | External Tool Modules | CORE 12, COND 4 | V1~V3 |
| S-Series | 8 | Self-Evolution Modules | CORE 1, EXP 7 | V3 중심 |
| A-Series | 7 | Architecture Extension | CORE 2, EXP 5 | V1(2), V3(5) |
| B-Series | 6 | Memory/Skill Assets | CORE 1, EXP 5 | V3 중심 |
| C-Series | 7 | Verifier/Reasoning | CORE 3, EXP 4 | V1(3), V3(4) |
| D-Series | 6 | Brain/Planner/RAG | CORE 2, EXP 4 | V1(2), V3(4) |
| EVX-Series | 6 | Verification Chain | CORE 5, EXP 1 | V3-only |
| **Named 소계** | **81** | | | |
| COND CAT-A | 13 | AI/ML Engine | Conditional | Mixed |
| COND CAT-B | 13 | Knowledge Management | Conditional | Mixed |
| COND CAT-C | 53 | Ops/Infrastructure (+E-Ops 39) | Conditional | Mixed |
| COND CAT-D | 8 | Media Processing | Conditional | Mixed |
| COND CAT-E | 7 | Education | Conditional | Mixed |
| COND CAT-F | 8 | Wellbeing/Health | Conditional | Mixed |
| COND CAT-G | 4 | Integration | Conditional | Mixed |
| **COND 소계** | **106** | | | |
| **총계** | **187** | | | |

### 2.2 도메인 시스템 — 36개 + 특수 2개

| Tier | 도메인 | 수 |
|------|--------|---|
| T0 | 0-0 Governance | 1 |
| T1 | 1-1 Verifier, 1-2 Auxiliary | 2 |
| T2 | 2-1 Blue-Node, 2-2 COND | 2 |
| T3 | 3-2~3-10 (3-1 결번) | 9 |
| T4 | 4-1~4-4 | 4 |
| T5 | 5-1~5-4 | 4 |
| T6 | 6-1~6-13 | 13 |
| 특수 | Ai-investing-detail | 1 |
| 메타 | _cross-ref, FILE CONTEXT | 2 |
| **합계** | | **38** |

### 2.3 설계 문서 — 39개 (5그룹)

- A그룹 설계 21개: RULE(1) + PLAN(1) + DESIGN D2.0(8) + SCHEMA D2.1(11)
- B그룹 구현가이드 7개: PHASE_B1~B7
- C그룹 특화 SPEC 5개: MASTER + INVESTING + CLOUD + TEAMS + SDAR
- D그룹 STEP7 명세 5개: A-E / F-I / J-M / N-P / 통합
- E그룹 기타 1개: BEGINNER_GUIDE

### 2.4 의존성 구조 — 112개 엣지

- 90개 단방향 + 27개 양방향 쌍
- 순환 의존성: 0개
- 교차 Tier 양방향: 6개 (정당화됨)

### 2.5 LOCK 항목 — 469+개

- 28개 네임스페이스
- DEC-001~017 아키텍처 결정
- 도메인별 LOCK (LOCK-AT, LOCK-BN, LOCK-MR 등)
- 7개 절대 불변 구역 (safety, cost, approval, non-goals, audit, data_retention, consent)

### 2.6 비목표 (Non-goal) — 7개

1. 실거래/주문/계좌/API 연동
2. 불법 행위/해킹/권한 상승
3. 의료/법률 단정적 판단
4. 민감 개인정보 장기 저장
5. 저작권/약관 위반
6. P2 도메인 자동 생성
7. 위험 기능 자동 실행

### 2.7 미해소 이슈 — 45개

- HIGH 10건, MEDIUM 21건, LOW 9건, INFO 5건
- 버전별: V0 5건, V1 16건, V2 14건, V3 5건, CC 5건

### 2.8 GO/NO-GO 체크리스트

- V0 진입: 16항목
- V1 진입: 21항목
- V2 진입: 14항목
- V3 진입: 11항목

### 2.9 STEP7 기술 보강 — 3,101건

- 16개 카테고리 (A~P)
- STEP6 완료: 1,556건
- STEP7 보강: 1,545건
- TITLE_ONLY ~44% (~675건): V2에서 상세 보강 필요

### 2.10 교차 도메인 용어 충돌 — 15개

| 용어 | 충돌 도메인 |
|------|-----------|
| QoD | 1-2 vs 4-4 (검색품질 vs LLM출력) |
| Gate | 4-4 vs quant vs 1-2 (QA vs EVAL vs PHASE) |
| Pipeline | 4-2 vs 3-2 vs 4-4 (CI vs IO vs MODEL) |
| Agent | 6-3 vs 3-8 (팀 vs 서비스) |
| Score | quant vs universe vs 5-1 vs 4-4 |
| 5-Gate | 0-0 vs 6-5 vs 6-8 (VAMOS vs SDAR vs CL) |
| Autonomy | 3-10 vs 6-2 vs 6-5 (L0~L4 범위 차이) |
| ... | (15개 전체는 GLOSSARY_CROSS_DOMAIN.md 참조) |

### 2.11 v12 추가사항

- BreathingGuide, GroundingExercise, MeditationTimer (웰니스 UI)
- ThoughtRecord, CognitiveDistortionDetector (CBT 도구)
- WorkloadMonitor, ForcedBreakOverlay (피로 감지)
- FlashcardEditor, SM2ReviewEngine, ReviewDashboard (간격 반복)
- Prompt Registry API + 3 TemplateSets

### 2.12 v23 확장 항목 — 87개

- V2-P2: 51건 (Self-RAG, CRAG, ColBERT v3, Multi-agent Orchestrator 등)
- V2-P3: 14건 (Sparse Attention, MoE Routing, Continual Learning 등)
- V3-P2: 6건 (Neuro-symbolic, Causal Inference, World Model 등)
- V3-P3: 16건 (AGI Safety, Emergent Behavior Monitor, DID 등)

### 2.13 가이드 문서 — 38개

- 초보자 가이드 1개
- 구현 가이드 PART 1, PART 2
- 세션 운영 가이드 1개
- 세션 가이드 34개 (session_01 ~ session_34_review)

### 2.14 구현 단계 — v8~v13

| 버전 | 파일 수 | 목적 |
|------|---------|------|
| v8 | 35 | 초기 단계 |
| v9 | 38 | Phase 1 |
| v10 | 149 | Phase 0/2 종합 |
| v11 | 80 | Phase 0/1/5 |
| v12 | 88 | v12 구현 |
| v13 | 299 | Phase 0~5 종합 (현재) |

### 2.15 검증 체계

- Phase 11 검증: 56 sessions (S1-1 ~ S11-8)
- 26개 검증 스킬 실행
- RAGAS 평가: 4개 메트릭 전부 PASS
- Patronus 체크: 37/37 plans FAITHFUL
- 최종: ALL-A VERIFIED

---

## 3. Obsidian Vault 구조 (최종)

```
D:\VAMOS\VAMOS HOME\
│
├── 00_HUB/                              (7개 — 진입점)
│   ├── VAMOS-HOME.md                    ← 전체 시스템 홈
│   ├── TIER-MAP.md                      ← T0~T6 계층 시각화
│   ├── DEPENDENCY-GRAPH.md              ← 112개 엣지 매핑
│   ├── LOCK-DECISION-REGISTRY.md        ← 469+ LOCK 전체
│   ├── MODULE-MAP.md                    ← 187개 모듈 전체
│   ├── 39-FILE-MASTER-INDEX.md          ← SOT 39파일 계층
│   └── SOT2-STRUCTURE-MAP.md            ← SOT 2 42폴더 구조
│
├── 01_GOVERNANCE/                       (1개)
│   └── T0-Governance.md
│
├── 02_CORE-INTELLIGENCE/                (2개)
│   ├── T1-Verifier-Engines.md
│   └── T1-Auxiliary-Modules.md
│
├── 03_EXECUTION/                        (2개)
│   ├── T2-Blue-Node.md
│   └── T2-COND-Modules.md
│
├── 04_FEATURES/                         (9개)
│   ├── T3-Multimodal.md
│   ├── T3-PKM.md
│   ├── T3-Workflow-RPA.md
│   ├── T3-Education.md
│   ├── T3-Health-EmotionAI.md
│   ├── T3-Dev-Tools.md
│   ├── T3-A2A-Protocol.md
│   ├── T3-Business-Model.md
│   └── T3-Agent-Protocol.md
│
├── 05_INFRASTRUCTURE/                   (4개)
│   ├── T4-Rust-Tauri.md
│   ├── T4-CICD.md
│   ├── T4-MCP.md
│   └── T4-MLOps.md
│
├── 06_QUALITY/                          (4개)
│   ├── T5-Benchmark.md
│   ├── T5-File-Context.md
│   ├── T5-v12-Additions.md
│   └── T5-v23-Extensions.md
│
├── 07_SYSTEM-WIDE/                      (13개)
│   ├── T6-UI-UX.md
│   ├── T6-Security.md
│   ├── T6-Agent-Teams.md
│   ├── T6-Memory-RAG.md
│   ├── T6-SDAR.md
│   ├── T6-Self-Evolution.md
│   ├── T6-RT-BNP-DCL.md
│   ├── T6-Cloud-Library.md
│   ├── T6-Brain-Adapter.md
│   ├── T6-EXP-Modules.md
│   ├── T6-Hologram.md
│   ├── T6-Event-Logging.md
│   └── T6-Operations.md
│
├── 08_AI-INVESTING/                     (4개)
│   ├── AI-Investing-Overview.md         ← 28 하위도메인 맵
│   ├── AI-Investing-Core.md             ← 00_core~07
│   ├── AI-Investing-Advanced.md         ← 08~15
│   └── AI-Investing-Infrastructure.md   ← 16~21
│
├── 09_DESIGN-DOCS/                      (12개)
│   ├── D2.0-01-Overview.md
│   ├── D2.0-02-Orange-Core.md
│   ├── D2.0-03-Blue-Nodes.md
│   ├── D2.0-04-Infra.md
│   ├── D2.0-05-Agent-Workflow.md
│   ├── D2.0-06-Storage-Memory.md
│   ├── D2.0-07-Safety-Cost.md
│   ├── D2.0-08-UI-UX.md
│   ├── D2.1-Schema-Index.md
│   ├── SPEC-Agent-Teams.md
│   ├── SPEC-SDAR.md
│   └── SPEC-Cloud-Library.md
│
├── 10_CONCEPTS/                         (37개)
│   │
│   │  ── 시스템 개념 (10개) ──
│   ├── 5-Gate-Decision-Framework.md
│   ├── LOCK-Mechanism.md
│   ├── Autonomy-Level-Framework.md      ← L0~L4 + NEVER
│   ├── Memory-Layers.md                 ← L0~L3 + B↔L 매핑
│   ├── RAG-Pipeline.md                  ← 6-stage + hybrid
│   ├── Cost-Limits.md                   ← V1/V2/V3 절대한도
│   ├── Module-Classification.md         ← CORE/COND/EXP
│   ├── Decision-Lock.md                 ← S3 이후 변경불가
│   ├── Failover-Chain-Pattern.md        ← 멀티도메인 fallback
│   ├── VamosMessage-Schema.md           ← envelope + 스키마
│   │
│   │  ── 모듈 시리즈 (5개) ──
│   ├── A-Series-Architecture-Extensions.md ← A1~A7
│   ├── B-Series-Memory-Assets.md        ← B1~B6 + B↔L
│   ├── C-Series-Verifiers.md            ← C1~C7
│   ├── D-Series-Brain-Extensions.md     ← D1~D6
│   ├── EVX-Verification-Chain.md        ← EVX1~6
│   │
│   │  ── COND 카테고리 (7개) ──
│   ├── COND-CAT-A-AI-ML.md
│   ├── COND-CAT-B-Knowledge.md
│   ├── COND-CAT-C-Ops-Infra.md
│   ├── COND-CAT-D-Media.md
│   ├── COND-CAT-E-Education.md
│   ├── COND-CAT-F-Wellbeing.md
│   ├── COND-CAT-G-Integration.md
│   │
│   │  ── 기술/인프라 개념 (15개) ──
│   ├── Permission-Matrix-System.md      ← L0~L5 6단계
│   ├── LangGraph-DAG-Engine.md
│   ├── MCP-Bridge-Layer.md              ← Streamable HTTP
│   ├── Hologram-Rendering-System.md
│   ├── VAMOS-Version-Strategy.md        ← V0→V1→V2→V3
│   ├── Event-Logging-Standard.md        ← trace_id, JSON
│   ├── BGE-M3-Embedding-Pipeline.md     ← 1024dim, hybrid
│   ├── VAMOS-Authority-Chain.md         ← RULE>PLAN>DESIGN
│   ├── Data-Governance-Pipeline.md      ← QoD, PII
│   ├── SLA-Performance-Targets.md
│   ├── VAMOS-Configuration-Framework.md ← TOML + ENV
│   ├── SDAR-Emergency-Response.md       ← Kill switch
│   ├── Cross-Domain-Terminology.md      ← 15개 용어 충돌
│   ├── Benchmark-Evaluation-Framework.md
│   └── VAMOS-Authority-Chain.md
│
├── 11_WORKFLOWS/                        (3개)
│   ├── End-to-End-Request-Flow.md       ← S0→S8 전체
│   ├── Gate-Rejection-Paths.md          ← Gate 거부 분기
│   └── Self-Check-Loop.md              ← Soft-loop
│
├── 12_IMPLEMENTATION/                   (11개)
│   ├── STEP7-Implementation-Bridge.md   ← A~P 16카테고리 매핑
│   ├── Release-Track-Map.md             ← R1~R6 → V1/V2/V3
│   ├── STEP6-Completed-Items.md         ← 1,556건
│   ├── v12-Additions.md                 ← 웰니스/CBT/SM2
│   ├── v23-Extensions-87.md             ← 87개 확장
│   ├── Current-Phase.md                 ← 현재 진행
│   ├── V8-Results.md
│   ├── V9-Results.md
│   ├── V10-Results.md
│   ├── V11-Results.md
│   ├── V12-Results.md
│   └── V13-Results.md
│
├── 13_GUIDES/                           (4개)
│   ├── SESSION-GUIDES-MAP.md            ← 34개 세션 인덱스
│   ├── Beginner-Guide.md
│   ├── Implementation-Part1.md
│   └── Implementation-Part2.md
│
├── 14_AUDIT/                            (3개)
│   ├── SOT-Consistency-Audits.md        ← 26개 검증 리포트
│   ├── Phase11-Validation-Summary.md
│   └── Known-Issues-Registry.md         ← 45개 이슈 + 알려진 문제
│
├── 15_RULES/                            (4개)
│   ├── BASE-1.3-Rules.md                ← R1~R11 + 비목표
│   ├── PLAN-3.0-Roadmap.md              ← DEC-001~017
│   ├── Non-Goals.md                     ← 7개 절대 금지
│   └── Part2-Master-Reference.md        ← 모든 도메인 근거
│
├── 99_RAW/                              (심링크/참조)
│   ├── sot/ → D:\VAMOS\docs\sot\
│   ├── sot2/ → D:\VAMOS\docs\sot 2\
│   └── guides/ → D:\VAMOS\docs\guides\
│
└── OBSIDIAN-STRATEGY-v3.md              ← 이 문서
```

**총 노트 수: 120+ 개**

---

## 4. 태깅 시스템 (6차원)

모든 노트의 frontmatter에 적용:

```yaml
tags:
  # 1. Tier (계층)
  - tier/T0 ~ tier/T6

  # 2. 모듈 시리즈
  - module/I-series
  - module/E-series
  - module/S-series
  - module/A-series
  - module/B-series
  - module/C-series
  - module/D-series
  - module/EVX-series
  - module/COND

  # 3. 상태
  - status/CORE
  - status/COND
  - status/EXP

  # 4. 버전
  - version/V0 ~ version/V3

  # 5. 노트 분류
  - type/domain
  - type/concept
  - type/design
  - type/workflow
  - type/hub
  - type/guide
  - type/audit
  - type/rule
  - type/implementation

  # 6. LOCK 분류
  - lock/ABSOLUTE
  - lock/FREEZE
  - lock/DEFINED-HERE
```

---

## 5. 도메인 노트 Template

```markdown
---
tags: [tier/T#, module/X-series, status/CORE, version/V1, type/domain]
aliases: [번호, 한글명, 영문명]
tier: T#
domain: "#-# Domain-Name"
sot_source: "D:\\VAMOS\\docs\\sot 2\\#-#_Domain\\"
design_doc: "[[D2.0-##-Name]]"
quality_gate: GOLD/SILVER/BRONZE
step7_category: "[[STEP7-Implementation-Bridge#카테고리]]"
version_gate: "V1: 내용 | V2: 내용 | V3: 내용"
---

# #-# Domain-Name

## 한줄 요약
(도메인의 핵심 역할 1문장)

## 핵심 정의
(주요 컴포넌트, 패턴, 수치)

## LOCK 항목
(LOCK-XX-001 ~ 전체 나열)

## 의존성 (Depends On)
- [[도메인]] — 이유

## 제공 (Provides To)
- [[도메인]] — 이유

## 횡단 개념 연결
- [[개념노트]] — 이 도메인에서의 역할

## 관련 모듈 시리즈
- [[MODULE-MAP#시리즈|모듈ID]] — 역할

## STEP7 매핑
- 출처: STEP7-X (N개 항목)

## 버전별 범위
- V1: 내용
- V2: 내용
- V3: 내용

## 검증 상태
- Quality Gate: 등급
- Phase 11: Grade
- LOCK 검증: N/N 일치

## 원본 문서
- SOT 2: 경로
- Authority: AUTHORITY_CHAIN.md 경로
- Design: D2.0 파일명
```

---

## 6. 횡단 개념 노트 Template

```markdown
---
tags: [type/concept, tier/all]
aliases: [약어, 한글명]
---

# Concept Name

## 정의
(개념의 핵심 정의)

## 이 개념이 등장하는 모든 도메인
- [[도메인]] — 역할/맥락

## LOCK 항목
(관련 LOCK 나열)

## 버전별 차이
- V1: 내용
- V2: 내용
- V3: 내용

## 원본 참조
(정본 문서 경로)
```

---

## 7. Claude 연동 방법

### 7.1 Obsidian MCP Server

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "npx",
      "args": ["-y", "obsidian-mcp"],
      "env": {
        "OBSIDIAN_VAULT_PATH": "D:/VAMOS/VAMOS HOME"
      }
    }
  }
}
```

### 7.2 CLAUDE.md 보강 (스마트 라우터)

CLAUDE.md에 추가할 내용:
- Obsidian Vault 경로
- 질문 시 관련 노트 검색 워크플로우
- 도메인 → 파일 경로 라우팅 테이블

### 7.3 검색 워크플로우

```
사용자 질문
  → CLAUDE.md 읽기 (자동)
  → 관련 도메인 판단
  → Obsidian MCP: 도메인 노트 읽기
  → "Depends On" / "Provides To" 링크 따라가기
  → 관련 횡단 개념 확인
  → 필요 시 원본 문서(99_RAW) 참조
  → 누락 없는 응답 생성
```

---

## 8. 구축 순서

### Phase 1: HUB + 규칙 (완료/진행중)
- [x] 디렉토리 구조 생성
- [x] 00_HUB 7개 파일
- [ ] 15_RULES 4개 파일

### Phase 2: 횡단 개념 + 워크플로우 (1일)
- [ ] 10_CONCEPTS 37개 노트
- [ ] 11_WORKFLOWS 3개 노트

### Phase 3: 도메인 노트 (2일)
- [ ] 01~07 Tier별 36개 노트
- [ ] 08_AI-INVESTING 4개 노트

### Phase 4: 보조 레이어 (1일)
- [ ] 09_DESIGN-DOCS 12개 노트
- [ ] 12_IMPLEMENTATION 11개 노트
- [ ] 13_GUIDES 4개 노트
- [ ] 14_AUDIT 3개 노트

### Phase 5: 연동 + 검증 (지속)
- [ ] Obsidian MCP 연결
- [ ] CLAUDE.md 보강
- [ ] Graph View 검증 (고립 노드 없는지)
- [ ] 실사용 피드백 반영

---

## 9. 커버리지 분석

### 포함된 것 (90%)
- 187개 모듈 전체 (8 시리즈 + COND 7카테고리)
- 36개 도메인 전체 (T0~T6 + AI-Investing)
- 39개 SOT 파일 계층
- 112개 의존성 엣지
- 469+ LOCK 항목
- 15개 교차 용어 충돌
- 45개 미해소 이슈
- GO/NO-GO 체크리스트 (V0~V3)
- 3,101건 STEP7 + 1,556건 STEP6
- 87개 v23 확장 항목
- v12 추가사항
- 34개 세션 가이드
- Phase 11 검증 결과
- 7개 비목표

### 포함되지 않은 것 (10%) — 대응 방법
| 미포함 | 이유 | 대응 |
|--------|------|------|
| AI-Investing 254개 파일 전체 상세 | 4개 요약 노트로 인덱싱 | 원본 참조 |
| 177개 하위폴더 내 세부 _index.md | 도메인 노트에서 경로 명시 | Claude 직접 읽기 |
| 구현단계 696개 파일 상세 | 버전별 요약 노트 | 필요 시 원본 참조 |
| 코드 레벨 상세 (API 88개) | 설계 문서 요약에 포함 | PHASE_B1 직접 참조 |

---

## 10. 최종 체크리스트

- [x] 모듈 8개 시리즈 전체 (I/E/S/A/B/C/D/EVX) 포함 확인
- [x] COND 106개 (CAT-A~G 7카테고리) 포함 확인
- [x] 36개 도메인 전체 포함 확인
- [x] 3-1 결번 사유 기록
- [x] 39개 SOT 파일 계층 매핑
- [x] 112개 의존성 엣지 (27 양방향) 매핑
- [x] 469+ LOCK 항목 인덱싱
- [x] 7개 비목표 독립 노드
- [x] 15개 교차 용어 충돌 노드
- [x] 45개 미해소 이슈 추적
- [x] GO/NO-GO 체크리스트 포함
- [x] STEP6(1,556) + STEP7(1,545) 브릿지
- [x] v12 추가사항 노드
- [x] v23 확장 87개 노드
- [x] 34개 세션 가이드 인덱스
- [x] Phase 11 검증 결과 노드
- [x] Part2 마스터 참조 노드
- [x] 6차원 태깅 시스템 설계
- [x] Claude MCP 연동 방법
- [x] 도메인/개념 노트 Template
