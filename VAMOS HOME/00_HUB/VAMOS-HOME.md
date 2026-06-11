---
tags: [type/hub, tier/all]
aliases: [HOME, VAMOS, 홈]
description: "VAMOS AI Knowledge Graph 진입점 — 전체 시스템 홈"
---

# VAMOS AI — Knowledge Graph Home

> 사용자의 지능적 결정을 돕는 개인 맞춤형 AI 보조 지능 (투자/생산성/분석), AGI 구조 지향

## 아키텍처 한눈에

```
Front Mini LLM (I-1 내부 서브컴포넌트)
  → ORANGE CORE (정책/룰/비용/라우팅/안전/Self-check)
    → BLUE NODE (도메인 전용 실행: Dev/Research/Productivity/Content/Quant/Trading)
      → OTHER BRAINS (검색/RAG/DB/API/코드실행/분석)
        → Main/Hologram LLM (최종 출력/시각화)
```

## 버전 로드맵

| 버전 | 비용 | 모듈 활성 | 에이전트 | 인프라 |
|------|------|----------|---------|--------|
| V0 | ₩40K/월 (V1 동일) | 스켈레톤 | - | 로컬 |
| V1 MVP | ₩40,000/월 | 26개 CORE | 3 | Ollama+Chroma+SQLite |
| V2 Pro | ₩93,000/월 | ~50개 | 10 (Redis) | Docker+Qdrant+Postgres |
| V3 Enterprise | ₩266,000/월 | 81+106 전체 | 50+ (K8s Mesh) | K8s+Neo4j+Loki |

## 기술 스택

`Tauri 2.0 + React 18` / `Rust (IPC)` / `Python 3.11+ (AI/ML)` / `LangGraph (LOCK)` / `BGE-M3 1024dim` / `Chroma→Qdrant` / `MCP Streamable HTTP (LOCK)`

## Vault 네비게이션

### 허브 (00_HUB)
- [[TIER-MAP]] — T0~T6 계층 전체 시각화
- [[DEPENDENCY-GRAPH]] — 112개 의존성 엣지 매핑
- [[LOCK-DECISION-REGISTRY]] — 469+ LOCK 항목 전체
- [[MODULE-MAP]] — 187개 모듈 (81 Named + 106 COND) 전체 맵
- [[39-FILE-MASTER-INDEX]] — SOT 39개 파일 계층
- [[SOT2-STRUCTURE-MAP]] — SOT 2 42개 폴더 구조

### 도메인 (Tier별)
- [[T0-Governance]] — 01_GOVERNANCE
- [[T1-Verifier-Engines]], [[T1-Auxiliary-Modules]] — 02_CORE-INTELLIGENCE
- [[T2-Blue-Node]], [[T2-COND-Modules]] — 03_EXECUTION
- [[T3-Multimodal]] ~ [[T3-Agent-Protocol]] (9개) — 04_FEATURES
- [[T4-Rust-Tauri]] ~ [[T4-MLOps]] (4개) — 05_INFRASTRUCTURE
- [[T5-Benchmark]] ~ [[T5-v23-Extensions]] (4개) — 06_QUALITY
- [[T6-UI-UX]] ~ [[T6-Operations]] (13개) — 07_SYSTEM-WIDE

### 특수 도메인
- [[AI-Investing-Overview]] — 08_AI-INVESTING (254파일, 28 하위도메인)

### 설계 문서
- [[D2.0-01-Overview]] ~ [[D2.0-08-UI-UX]] — 09_DESIGN-DOCS
- [[D2.1-Schema-Index]], [[SPEC-Agent-Teams]], [[SPEC-SDAR]], [[SPEC-Cloud-Library]]

### 횡단 개념 (10_CONCEPTS)
- 모듈 시리즈: [[A-Series-Architecture-Extensions]], [[B-Series-Memory-Assets]], [[C-Series-Verifiers]], [[D-Series-Brain-Extensions]], [[EVX-Verification-Chain]]
- COND: [[COND-CAT-A-AI-ML]] ~ [[COND-CAT-G-Integration]] (7개)
- 시스템: [[5-Gate-Decision-Framework]], [[Autonomy-Level-Framework]], [[Memory-Layers]], [[RAG-Pipeline]], [[Cost-Limits]], [[Decision-Lock]], [[LOCK-Mechanism]], [[Module-Classification]], [[Failover-Chain-Pattern]], [[VamosMessage-Schema]]
- 기술: [[Permission-Matrix-System]], [[LangGraph-DAG-Engine]], [[MCP-Bridge-Layer]], [[Hologram-Rendering-System]], [[VAMOS-Version-Strategy]], [[Event-Logging-Standard]], [[BGE-M3-Embedding-Pipeline]], [[VAMOS-Authority-Chain]], [[Data-Governance-Pipeline]], [[SLA-Performance-Targets]], [[VAMOS-Configuration-Framework]], [[SDAR-Emergency-Response]], [[Cross-Domain-Terminology]]

### 워크플로우 (11_WORKFLOWS)
- [[End-to-End-Request-Flow]] — S0→S8 전체 파이프라인
- [[Gate-Rejection-Paths]] — Gate 거부 시 분기
- [[Self-Check-Loop]] — Soft-loop 자가 검증

### 구현 (12_IMPLEMENTATION)
- [[STEP7-Implementation-Bridge]], [[Release-Track-Map]]
- [[V8-Results]] ~ [[V13-Results]], [[Current-Phase]]
- [[v12-Additions]], [[v23-Extensions-87]], [[STEP6-Completed-Items]]

### 가이드 (13_GUIDES)
- [[SESSION-GUIDES-MAP]], [[Beginner-Guide]], [[Implementation-Part1]], [[Implementation-Part2]]

### 감사 (14_AUDIT)
- [[SOT-Consistency-Audits]], [[Phase11-Validation-Summary]], [[Known-Issues-Registry]]

### 규칙 (15_RULES)
- [[BASE-1.3-Rules]], [[PLAN-3.0-Roadmap]], [[Non-Goals]], [[Part2-Master-Reference]]

## 원본 경로

| 영역 | 경로 | 파일 수 | 라인 수 |
|------|------|---------|---------|
| SOT | `D:\VAMOS\docs\sot\` | 68 | 89,413 |
| SOT 2 | `D:\VAMOS\docs\sot 2\` | 648 | 169,628 |
| Guides | `D:\VAMOS\docs\guides\` | 38 | 37,904 |
| 구현단계 | `D:\VAMOS\04. 구현단계\` | 696 | 98,795 |
| CLAUDE.md | `D:\VAMOS\CLAUDE.md` | 1 | 697 |
| **합계** | | **1,451** | **~396,000** |

## 6대 철학

1. 사용자 중심 & 개인화
2. 정확성/근거 기반 (환각 최소화)
3. 최신성 확보 (RAG + 외부 API)
4. 장기 맥락 유지 & 프로젝트 독립
5. 다중 의도 처리 & 메타인지
6. 구조적 모듈화 & 확장성
