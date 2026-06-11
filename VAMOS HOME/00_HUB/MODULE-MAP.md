---
tags: [type/hub, tier/all]
aliases: [Module Map, 모듈맵, 모듈 전체]
description: "VAMOS 187개 모듈 전체 맵 (81 Named + 106 COND)"
---

# VAMOS Module Map — 187개 전체

## 모듈 시리즈 총괄

| 시리즈 | 개수 | 분류 | 정의 문서 |
|--------|------|------|----------|
| [[A-Series-Architecture-Extensions\|A-Series]] | 7 | Architecture Extension | D2.0-01 §5.9 |
| [[B-Series-Memory-Assets\|B-Series]] | 6 | Memory/Skill/Self-evo | D2.0-01 §5.10 |
| [[C-Series-Verifiers\|C-Series]] | 7 | Verifier/Reasoning | D2.0-01 §5.11 |
| [[D-Series-Brain-Extensions\|D-Series]] | 6 | Brain/Planner/RAG | D2.0-01 §5.12 |
| E-Series | 16 | External Tools | D2.0-01 §5.7 |
| [[EVX-Verification-Chain\|EVX-Series]] | 6 | Verification Chain | D2.0-01 §5.13 |
| I-Series | 25 | Internal Core | D2.0-01 §5.6, D2.0-02 |
| S-Series | 8 | Self-Evolution | D2.0-01 §5.8 |
| **Named 소계** | **81** | | |
| [[COND-CAT-A-AI-ML\|COND CAT-A~G]] | 106 | Domain Conditional | SOT 2 / 2-2 |
| **총계** | **187** | | |

---

## I-Series (I-1 ~ I-25) — Internal Core

| ID | 명칭 | status | V1 | V2 | V3 |
|---|---|---|---|---|---|
| I-1 | Intent Detector | CORE | ON | ON | ON |
| I-2 | Context Builder | CORE | ON | ON | ON |
| I-3 | Memory System (L0~L3) | CORE | ON | ON | ON |
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
| I-25 | SDAR Engine | COND | OFF | COND | ON |

**연결**: [[T1-Auxiliary-Modules]], [[D2.0-02-Orange-Core]]

---

## E-Series (E-1 ~ E-16) — External Tools

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
| E-15 | File System (V1) → Cloud Collector (V2+) | OFF | COND | ON |
| E-16 | Cloud Storage Sync | OFF | COND | ON |

**주의**: E-15, E-16은 V1에서 OFF, V2에서 COND 활성화
**연결**: [[T2-Blue-Node]], [[D2.0-01-Overview]] §5.7

---

## S-Series (S-1 ~ S-8) — Self-Evolution

| ID | 명칭 | V1 | V2 | V3 | I-연결 |
|---|---|---|---|---|---|
| S-1 | Self-check Engine | ON | ON | ON | I-6, I-15 |
| S-2 | Benchmark QA Suite | OFF | OFF | ON | I-24 |
| S-3 | Template Evolution | OFF | OFF | ON | I-12, I-18 |
| S-4 | Error Pattern Miner | OFF | OFF | ON | I-20, I-18 |
| S-5 | Router Evolution / Cloud Evolver (이중역할) | OFF | OFF | ON | I-10, I-18 |
| S-6 | Search Evolution | OFF | OFF | ON | I-16, I-18 |
| S-7 | User-Coop Designer | OFF | OFF | ON | I-19, I-18 |
| S-8 | Self-evo Governance (LOCK) | OFF | OFF | ON | I-19, I-8, I-9, I-24 |

**연결**: [[T6-Self-Evolution]], [[D2.0-01-Overview]] §5.8

---

## A-Series (A-1 ~ A-7) — Architecture Extension

| ID | 명칭 | V1 | V2 | V3 |
|---|---|---|---|---|
| A-1 | MultiBrain Adapter | ON | ON | ON |
| A-2 | Preset Modularization | ON | ON | ON |
| A-3 | Meta AI | OFF | OFF | ON |
| A-4 | Debate Mode | OFF | COND | ON |
| A-5 | Lazy Generation | OFF | OFF | ON |
| A-6 | Federated Module Network (LOCK) | OFF | OFF | ON |
| A-7 | Remote Executor (LOCK) | OFF | OFF | ON |

**연결**: [[A-Series-Architecture-Extensions]], [[T6-Brain-Adapter]]

---

## B-Series (B-1 ~ B-6) — Memory/Skill/Self-evo Assets

| ID | 명칭 | status | V1 | V2 | V3 | L-매핑 |
|---|---|---|---|---|---|---|
| B-1 | Skill Library | EXP | OFF | OFF | ON | → L1 Episodic |
| B-2 | Procedural Memory | EXP | OFF | OFF | ON | → L3 Procedural |
| B-3 | Memory Decay | CORE | ON | ON | ON | → L2 Semantic |
| B-4 | Auto Curriculum Generator | EXP | OFF | OFF | ON | → L0 Working |
| B-5 | RL-like Self Trainer | EXP | OFF | OFF | ON | - |
| B-6 | DSPy Prompt Optimizer | EXP | OFF | OFF | ON | - |

**LOCK**: B↔L 매핑 변경 불가 (B-4→L0, B-1→L1, B-3→L2, B-2→L3)
**연결**: [[B-Series-Memory-Assets]], [[Memory-Layers]], [[T6-Memory-RAG]]

---

## C-Series (C-1 ~ C-7) — Verifier/Reasoning

| ID | 명칭 | status | V1 | V2 | V3 |
|---|---|---|---|---|---|
| C-1 | Logic Verifier | CORE | ON | ON | ON |
| C-2 | Math Verifier | CORE | ON | ON | ON |
| C-3 | Code Verifier | CORE | ON | ON | ON |
| C-4 | Domain Simulator | EXP | OFF | OFF | ON |
| C-5 | Bayesian Belief Engine | EXP | OFF | OFF | ON |
| C-6 | RL Advisor | EXP | OFF | OFF | ON |
| C-7 | GNN Score Model | EXP | OFF | OFF | ON |

**연결**: [[C-Series-Verifiers]], [[T1-Verifier-Engines]]

---

## D-Series (D-1 ~ D-6) — Brain/Planner/RAG

| ID | 명칭 | status | V1 | V2 | V3 |
|---|---|---|---|---|---|
| D-1 | Think Engine (CoT/ToT/GoT) | CORE | ON | ON | ON |
| D-2 | Multimodal Engine | CORE | ON | ON | ON |
| D-3 | Long Horizon Planner | EXP | OFF | OFF | ON |
| D-4 | Personality/Tone Engine | EXP | OFF | OFF | ON |
| D-5 | General Brain (Parallel) | EXP | OFF | OFF | ON |
| D-6 | GraphRAG / Hybrid RAG | EXP | OFF | OFF | ON |

**연결**: [[D-Series-Brain-Extensions]], [[T6-Brain-Adapter]]

---

## EVX-Series (EVX-1 ~ EVX-6) — Verification Chain

| ID | 명칭 | LOCK | V1 | V2 | V3 |
|---|---|---|---|---|---|
| EVX-1 | Code-as-Policy | false | OFF | OFF | ON |
| EVX-2 | Adversarial Verifier | **true (LOCK)** | OFF | OFF | ON |
| EVX-3 | Log-prob Confidence | EXP | OFF | OFF | ON |
| EVX-4 | Thought Buffer | false | OFF | OFF | ON |
| EVX-5 | Gen-Verify-Learn | false | OFF | OFF | ON |
| EVX-6 | Z3 Solver Routing | false | OFF | OFF | ON |

**모두 V3-only**. EVX-7+ 미정의 (V2+ Self-evo 확장 시 정의)
**연결**: [[EVX-Verification-Chain]], [[T6-EXP-Modules]]

---

## COND 모듈 (106개) — CAT-A ~ CAT-G

| 카테고리 | 모듈 수 | 범위 | 대상 도메인 |
|---------|--------|------|-----------|
| [[COND-CAT-A-AI-ML]] | 13 | COND-011~106 (산재) | AI/ML 엔진 |
| [[COND-CAT-B-Knowledge]] | 13 | COND-017~108 | 지식 관리 |
| [[COND-CAT-C-Ops-Infra]] | 53 | COND-027~079 + E-Ops 39개 | 운영/인프라 (최대) |
| [[COND-CAT-D-Media]] | 8 | COND-016, 080~109 | 미디어 처리 |
| [[COND-CAT-E-Education]] | 7 | COND-091~115 | 교육 |
| [[COND-CAT-F-Wellbeing]] | 8 | COND-095~116 | 건강/웰니스 |
| [[COND-CAT-G-Integration]] | 4 | COND-090~112 | 통합 |

**정의**: SOT 2 `2-2_COND-Modules-Detail/`
**연결**: [[T2-COND-Modules]]

---

## 버전별 활성 모듈 수

| 버전 | I | E | S | A | B | C | D | EVX | COND | 합계 |
|------|---|---|---|---|---|---|---|-----|------|------|
| V1 | 17 | 6 | 1 | 2 | 1 | 3 | 2 | 0 | 일부 | ~32+ |
| V2 | 20 | 10 | 1 | 3 | 1 | 3 | 2 | 0 | 추가 | ~50+ |
| V3 | 25 | 16 | 8 | 7 | 6 | 7 | 6 | 6 | 전체 | 187 |

## 모듈 상태 분류 (CORE / COND / EXP)

- **CORE**: 변경 불가 핵심 — V1부터 ON
- **COND**: 조건부 활성화 — 특정 도메인/버전에서만 ON
- **EXP**: 실험적 — 주로 V3에서 활성화
