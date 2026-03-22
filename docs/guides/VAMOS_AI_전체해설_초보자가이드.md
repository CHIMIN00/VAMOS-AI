# VAMOS AI 전체 해설 — 초보자 완전 가이드

> **버전**: v1.1.0 | **작성일**: 2026-03-13
> **목적**: VAMOS AI의 모든 기능, 모듈, 스킬, 아키텍처를 초보자 관점에서 빠짐없이 설명
> **근거 문서**: `docs/sot/` 68개 SOT 문서 전수 크로스체크 기반
> **정본 우선순위**: RULE 1.3 > PLAN 3.0 > DESIGN 2.0 LOCK > DESIGN 본문 > 스키마/TECH_STACK
> **관련 문서**: PART2 구현가이드(v26.0.0)는 구현 정본, 본 문서는 이해/해설 정본
> **Gap 분석**: v1.0.0 대비 18개 누락 항목 보완 완료 (CRITICAL 7, HIGH 7, MEDIUM 3, LOW 1)

---

# 목차

## PART A: VAMOS AI 이해하기 (What & Why)

- [1. VAMOS AI란 무엇인가?](#1-vamos-ai란-무엇인가)
  - [1.1 정의와 정체성 — Virtual AI Mind Operating System](#11-정의와-정체성)
  - [1.2 핵심 철학 — 6대 원칙](#12-핵심-철학--6대-원칙)
  - [1.3 우선순위 체계 — 정확성 > 품질 > 안전 > 속도 > 비용](#13-우선순위-체계)
  - [1.4 14대 핵심 목표 (A/B/C/D 그룹)](#14-14대-핵심-목표)
  - [1.5 7대 절대 금지사항 (Non-Goals)](#15-7대-절대-금지사항)
  - [1.6 VAMOS vs 기존 AI 비교 (ChatGPT, Copilot 등)](#16-vamos-vs-기존-ai-비교)
  - [1.7 사용 시나리오 예시](#17-사용-시나리오-예시)

- [2. 전체 아키텍처 — 4계층 구조](#2-전체-아키텍처--4계층-구조)
  - [2.1 아키텍처 개요도](#21-아키텍처-개요도)
  - [2.2 1계층: Front Mini LLM (입구 경비원)](#22-1계층-front-mini-llm)
  - [2.3 2계층: ORANGE CORE (두뇌/지휘관)](#23-2계층-orange-core)
  - [2.4 3계층: BLUE NODES (실행팀/전문가)](#24-3계층-blue-nodes)
  - [2.5 4계층: OTHER BRAINS / INFRA-CORE (도구/자원)](#25-4계층-other-brains)
  - [2.6 Main/Hologram LLM (최종 출력)](#26-mainhologram-llm)
  - [2.7 계층 간 데이터 흐름 전체도](#27-계층-간-데이터-흐름-전체도)
  - [2.8 개발 환경 셋업 — V1/V2/V3 구성 ★GAP-2](#28-개발-환경-셋업)

---

## PART B: 핵심 시스템 동작 원리 (How)

- [3. 처리 파이프라인 — 요청부터 응답까지](#3-처리-파이프라인)
  - [3.1 9-State 상태 머신 (S0~S8)](#31-9-state-상태-머신)
  - [3.2 Standard 5-Phase 파이프라인](#32-standard-5-phase-파이프라인)
    - [3.2.1 Phase 1: Intake (접수)](#321-phase-1-intake)
    - [3.2.2 Phase 2: Plan (계획)](#322-phase-2-plan)
    - [3.2.3 Phase 3: Execute (실행)](#323-phase-3-execute)
    - [3.2.4 Phase 4: Verify (검증)](#324-phase-4-verify)
    - [3.2.5 Phase 5: Deliver (전달)](#325-phase-5-deliver)
  - [3.3 3-Part Output (사용자에게 전달되는 3가지)](#33-3-part-output)
  - [3.4 TEE Loop (Think-Execute-Evaluate 반복)](#34-tee-loop)
  - [3.5 Soft Loop / Hard Loop / Circuit Breaker](#35-soft-loop--hard-loop--circuit-breaker)
  - [3.6 에러 발생 시 흐름 (Failure → Fallback)](#36-에러-발생-시-흐름)
  - [3.7 에러 처리 표준 — Result&lt;T, VamosError&gt; 계약 ★GAP-1](#37-에러-처리-표준)

- [4. 5-Gate 검증 시스템 — 모든 판단의 관문](#4-5-gate-검증-시스템)
  - [4.1 Gate 시스템 개요](#41-gate-시스템-개요)
  - [4.2 Gate 1: PolicyGate (정책 검증)](#42-gate-1-policygate)
  - [4.3 Gate 2: CostGate (비용 검증)](#43-gate-2-costgate)
  - [4.4 Gate 3: ApprovalGate (승인 검증)](#44-gate-3-approvalgate)
  - [4.5 Gate 4: EvidenceGate (근거 검증)](#45-gate-4-evidencegate)
  - [4.6 Gate 5: SelfCheckGate (자체 품질 검증)](#46-gate-5-selfcheckgate)
  - [4.7 Gate 우선순위와 조합 규칙](#47-gate-우선순위와-조합-규칙)
  - [4.8 Gate 결과에 따른 행동 분기](#48-gate-결과에-따른-행동-분기)
  - [4.9 HITL 타이밍 & Gate Threshold Ledger ★GAP-9](#49-hitl-타이밍--gate-threshold-ledger)

- [5. Decision 객체 — 모든 판단의 핵심 데이터](#5-decision-객체)
  - [5.1 Decision이란?](#51-decision이란)
  - [5.2 IntentFrame (의도 프레임)](#52-intentframe)
  - [5.3 EvidencePack (근거 패키지)](#53-evidencepack)
  - [5.4 Decision Lock 원칙 (한번 결정되면 변경 불가)](#54-decision-lock-원칙)
  - [5.5 Decision 결론 4가지: ACCEPT / REJECT / HOLD / ESCALATE](#55-decision-결론-4가지)
  - [5.6 ResponseEnvelope (응답 봉투)](#56-responseenvelope)

---

## PART C: 모듈 시스템 전체 해설 (81개 모듈)

- [6. 모듈 시스템 개요](#6-모듈-시스템-개요)
  - [6.1 모듈이란? (비유: 레고 블록)](#61-모듈이란)
  - [6.2 모듈 분류 체계: CORE / COND / EXP](#62-모듈-분류-체계)
  - [6.3 버전별 활성 모듈 수 (V0:5 → V1:32 → V2:42 → V3:81)](#63-버전별-활성-모듈-수)
  - [6.4 모듈 네이밍 규칙](#64-모듈-네이밍-규칙)
  - [6.5 모듈 간 의존성 규칙 (CORE→COND 단방향)](#65-모듈-간-의존성-규칙)

- [7. I-Series — 내부 처리 모듈 (25개)](#7-i-series--내부-처리-모듈-25개)
  - [7.1 I-1 Intent Detector (의도 감지기)](#71-i-1-intent-detector)
  - [7.2 I-2 Context Builder / RAG (맥락 구성기)](#72-i-2-context-builder)
  - [7.3 I-3 Memory System (기억 관리자)](#73-i-3-memory-system)
  - [7.4 I-4 Multimodal Interpreter (다중 입력 해석기)](#74-i-4-multimodal-interpreter)
  - [7.5 I-5 Decision Engine (판단 엔진) — LOCK](#75-i-5-decision-engine)
  - [7.6 I-6 Self-check Engine (자기 검증기)](#76-i-6-self-check-engine)
  - [7.7 I-7 Project/Session Manager (프로젝트 관리자)](#77-i-7-projectsession-manager)
  - [7.8 I-8 Policy Engine (정책 엔진) — LOCK](#78-i-8-policy-engine)
  - [7.9 I-9 Cost Manager (비용 관리자) — LOCK](#79-i-9-cost-manager)
  - [7.10 I-10 Tool Registry/Router (도구 등록소)](#710-i-10-tool-registryrouter)
  - [7.11 I-11 Output Composer (출력 조합기)](#711-i-11-output-composer)
  - [7.12 I-12 Workflow Builder (작업흐름 설계기)](#712-i-12-workflow-builder)
  - [7.13 I-13 Multimodal Output Renderer (다중 출력 렌더러)](#713-i-13-multimodal-output-renderer)
  - [7.14 I-14 Summarizer & Memory Distiller (요약 & 기억 증류기)](#714-i-14-summarizer)
  - [7.15 I-15 Evidence & QoD Manager (근거 품질 관리자)](#715-i-15-evidence--qod-manager)
  - [7.16 I-16 Knowledge Search Engine (지식 검색 엔진)](#716-i-16-knowledge-search-engine)
  - [7.17 I-17 Blue Node Manager (실행팀 관리자)](#717-i-17-blue-node-manager)
  - [7.18 I-18 Self-evo Engine (자기 진화 엔진)](#718-i-18-self-evo-engine)
  - [7.19 I-19 Approval Manager (승인 관리자) — LOCK](#719-i-19-approval-manager)
  - [7.20 I-20 Failure/Fallback Manager (장애 대응 관리자)](#720-i-20-failurefallback-manager)
  - [7.21 I-21 Source Evolution (정보원 진화)](#721-i-21-source-evolution)
  - [7.22 I-22 Task/Project Manager (작업 관리자)](#722-i-22-taskproject-manager)
  - [7.23 I-23 Doc/Code Structuring (문서/코드 구조화)](#723-i-23-doccode-structuring)
  - [7.24 I-24 Knowledge Graph Engine (지식 그래프 엔진)](#724-i-24-knowledge-graph-engine)
  - [7.25 I-25 SDAR Engine (자가진단/자동수리 엔진)](#725-i-25-sdar-engine)

- [8. E-Series — 외부 도구 모듈 (16개)](#8-e-series--외부-도구-모듈-16개)
  - [8.1 E-1 Coding Helper (코딩 도우미)](#81-e-1-coding-helper)
  - [8.2 E-2 Web Search (웹 검색)](#82-e-2-web-search)
  - [8.3 E-3 Document Parser (문서 파서)](#83-e-3-document-parser)
  - [8.4 E-4 Code Executor (코드 실행기) — Docker Sandboxing 포함 ★GAP-2](#84-e-4-code-executor)
  - [8.5 E-5 Image Analyzer (이미지 분석기)](#85-e-5-image-analyzer)
  - [8.6 E-6 Z3 Solver (논리 풀이기)](#86-e-6-z3-solver)
  - [8.7 E-7 Speech-to-Text (음성→텍스트)](#87-e-7-speech-to-text)
  - [8.8 E-8 Text-to-Speech (텍스트→음성)](#88-e-8-text-to-speech)
  - [8.9 E-9 Video Analyzer (영상 분석기)](#89-e-9-video-analyzer)
  - [8.10 E-10 External API Gateway (외부 API 게이트웨이)](#810-e-10-external-api-gateway)
  - [8.11 E-11 Browser Automation (브라우저 자동화)](#811-e-11-browser-automation)
  - [8.12 E-12 DB Connector (데이터베이스 연결기)](#812-e-12-db-connector)
  - [8.13 E-13 Calendar/Task Sync (캘린더 연동)](#813-e-13-calendartask-sync)
  - [8.14 E-14 Email Handler (이메일 처리기)](#814-e-14-email-handler)
  - [8.15 E-15 Cloud Collector / File System (클라우드 수집기)](#815-e-15-cloud-collector)
  - [8.16 E-16 Cloud Storage Sync (클라우드 저장소 동기화)](#816-e-16-cloud-storage-sync)

- [9. S-Series — 자기 진화 모듈 (8개)](#9-s-series--자기-진화-모듈-8개)
  - [9.1 S-1 Self-check Engine (자기 검증 엔진)](#91-s-1-self-check-engine)
  - [9.2 S-2 Benchmark QA Suite (벤치마크 테스트)](#92-s-2-benchmark-qa-suite)
  - [9.3 S-3 Template Evolution (템플릿 진화)](#93-s-3-template-evolution)
  - [9.4 S-4 Error Pattern Miner (에러 패턴 분석기)](#94-s-4-error-pattern-miner)
  - [9.5 S-5 Router Evolution (라우터 진화)](#95-s-5-router-evolution)
  - [9.6 S-6 Search Evolution (검색 진화)](#96-s-6-search-evolution)
  - [9.7 S-7 User-Coop Designer (사용자 협업 설계기)](#97-s-7-user-coop-designer)
  - [9.8 S-8 Self-evo Governance (자기 진화 거버넌스)](#98-s-8-self-evo-governance)

- [10. A-Series — 아키텍처 확장 모듈 (7개)](#10-a-series--아키텍처-확장-모듈-7개)
  - [10.1 A-1 MultiBrain Adapter (멀티 AI 어댑터)](#101-a-1-multibrain-adapter)
  - [10.2 A-2 Preset Modularization (프리셋 모듈화)](#102-a-2-preset-modularization)
  - [10.3 A-3 Meta AI (메타 AI)](#103-a-3-meta-ai)
  - [10.4 A-4 Debate Mode (토론 모드)](#104-a-4-debate-mode)
  - [10.5 A-5 Lazy Generation (지연 생성)](#105-a-5-lazy-generation)
  - [10.6 A-6 Federated Module Network (연합 모듈 네트워크)](#106-a-6-federated-module-network)
  - [10.7 A-7 Remote Executor (원격 실행기)](#107-a-7-remote-executor)

- [11. B-Series — 기억/스킬 자산 모듈 (6개)](#11-b-series--기억스킬-자산-모듈-6개)
  - [11.1 B-1 Skill Library (스킬 라이브러리)](#111-b-1-skill-library)
  - [11.2 B-2 Procedural Memory (절차적 기억)](#112-b-2-procedural-memory)
  - [11.3 B-3 Memory Decay (기억 감쇠)](#113-b-3-memory-decay)
  - [11.4 B-4 Auto Curriculum Generator (자동 커리큘럼)](#114-b-4-auto-curriculum-generator)
  - [11.5 B-5 RL-like Self Trainer (강화학습형 자기 훈련)](#115-b-5-rl-like-self-trainer)
  - [11.6 B-6 DSPy Prompt Optimizer (프롬프트 최적화)](#116-b-6-dspy-prompt-optimizer)
  - [11.7 프롬프트 관리 & 템플릿 진화 시스템 ★GAP-5](#117-프롬프트-관리--템플릿-진화-시스템)

- [12. C-Series — 검증/추론 모듈 (7개)](#12-c-series--검증추론-모듈-7개)
  - [12.1 C-1 Logic Verifier (논리 검증기)](#121-c-1-logic-verifier)
  - [12.2 C-2 Math Verifier (수학 검증기)](#122-c-2-math-verifier)
  - [12.3 C-3 Code Verifier (코드 검증기)](#123-c-3-code-verifier)
  - [12.4 C-4 Domain Simulator (도메인 시뮬레이터)](#124-c-4-domain-simulator)
  - [12.5 C-5 Bayesian Belief Network (베이지안 추론)](#125-c-5-bayesian-belief-network)
  - [12.6 C-6 RL Advisor (강화학습 어드바이저)](#126-c-6-rl-advisor)
  - [12.7 C-7 GNN Score Model (그래프 신경망 스코어)](#127-c-7-gnn-score-model)

- [13. D-Series — 두뇌/플래너/RAG 확장 모듈 (6개)](#13-d-series--두뇌플래너rag-확장-모듈-6개)
  - [13.1 D-1 Think Engine (사고 엔진)](#131-d-1-think-engine)
  - [13.2 D-2 Multimodal Engine (멀티모달 엔진)](#132-d-2-multimodal-engine)
  - [13.3 D-3 Long Horizon Planner (장기 계획 수립기)](#133-d-3-long-horizon-planner)
  - [13.4 D-4 Personality/Tone Engine (성격/톤 엔진)](#134-d-4-personalitytone-engine)
  - [13.5 D-5 Parallel General Brain (병렬 범용 두뇌)](#135-d-5-parallel-general-brain)
  - [13.6 D-6 GraphRAG / Hybrid RAG (그래프 기반 RAG)](#136-d-6-graphrag--hybrid-rag)

- [14. EVX-Series — 검증 확장 모듈 (6개)](#14-evx-series--검증-확장-모듈-6개)
  - [14.1 EVX-1 Code-as-Policy (코드 기반 정책)](#141-evx-1-code-as-policy)
  - [14.2 EVX-2 Adversarial Verifier (적대적 검증기)](#142-evx-2-adversarial-verifier)
  - [14.3 EVX-3 Log-prob Confidence (확률 기반 신뢰도)](#143-evx-3-log-prob-confidence)
  - [14.4 EVX-4 Thought Buffer (사고 버퍼)](#144-evx-4-thought-buffer)
  - [14.5 EVX-5 Gen-Verify-Learn (생성-검증-학습 루프)](#145-evx-5-gen-verify-learn)
  - [14.6 EVX-6 Z3 Solver Routing (Z3 라우팅)](#146-evx-6-z3-solver-routing)

---

## PART D: 도메인 & 메모리 시스템

- [15. 도메인 시스템 — P0 / P1 / P2](#15-도메인-시스템)
  - [15.1 도메인이란? (비유: 전문 부서)](#151-도메인이란)
  - [15.2 P0 — 항상 활성 (Dev, Research, Productivity)](#152-p0)
    - [15.2.1 Dev/System (개발/시스템)](#1521-devsystem)
    - [15.2.2 Research (리서치/연구)](#1522-research)
    - [15.2.3 Productivity (생산성)](#1523-productivity)
  - [15.3 P1 — 1회 승인 후 활성 (Content, Data & Quant)](#153-p1)
    - [15.3.1 Content (콘텐츠)](#1531-content)
    - [15.3.2 Data & Quant (데이터/퀀트)](#1532-data--quant)
  - [15.4 P2 — 세션별 승인 필수 (Trading Strategy)](#154-p2)
    - [15.4.1 Trading Strategy Analysis (투자 전략 분석)](#1541-trading-strategy-analysis)
    - [15.4.2 P2 승인 흐름 상세](#1542-p2-승인-흐름-상세)
  - [15.5 Blue Node 생명주기 (활성화 → 비활성화)](#155-blue-node-생명주기)
  - [15.6 NodeCapabilityProfile (노드 역량 프로필)](#156-nodecapabilityprofile)

- [16. 메모리 시스템 — 4계층 기억 구조](#16-메모리-시스템)
  - [16.1 왜 기억이 필요한가?](#161-왜-기억이-필요한가)
  - [16.2 L0 Session Buffer (대화 기억)](#162-l0-session-buffer)
  - [16.3 L1 Project Memory (프로젝트 기억)](#163-l1-project-memory)
  - [16.4 L2 Global Knowledge (장기 지식)](#164-l2-global-knowledge)
  - [16.5 L3 Procedural Memory (절차 기억)](#165-l3-procedural-memory)
  - [16.6 기억 4유형: Working / Episodic / Semantic / Procedural](#166-기억-4유형)
  - [16.7 L0→L1→L2 승격 규칙 (3회 참조 시 L2 승격)](#167-승격-규칙)
  - [16.8 TTL (유효기간) 정책](#168-ttl-정책)
  - [16.9 PII 마스킹 & 데이터 보호](#169-pii-마스킹)
  - [16.10 데이터 프라이버시 경화 (S7E-031~040) ★GAP-8](#1610-데이터-프라이버시-경화)

- [17. RAG 시스템 — 지식 검색 & 활용](#17-rag-시스템)
  - [17.1 RAG란? (비유: 도서관에서 책 찾기)](#171-rag란)
  - [17.2 6-Stage RAG Pipeline](#172-6-stage-rag-pipeline)
    - [17.2.1 Intake (수집)](#1721-intake)
    - [17.2.2 Chunking (분할)](#1722-chunking)
    - [17.2.3 Embedding (벡터화)](#1723-embedding)
    - [17.2.4 Indexing (색인)](#1724-indexing)
    - [17.2.5 Retrieval (검색)](#1725-retrieval)
    - [17.2.6 Synthesis (합성)](#1726-synthesis)
  - [17.3 Hybrid Search (BM25 + Vector + Reranker)](#173-hybrid-search)
  - [17.4 Semantic Cache (의미 캐시)](#174-semantic-cache)
  - [17.5 QoD — Quality of Data (데이터 품질 점수)](#175-qod)
  - [17.6 Embedding 모델: BGE-M3 vs text-embedding-3-small](#176-embedding-모델)
  - [17.7 Vector DB: Chroma vs Qdrant](#177-vector-db)
  - [17.8 GraphRAG (지식 그래프 기반 RAG)](#178-graphrag)

---

## PART E: 안전 & 거버넌스

- [18. 보안 체계 — 4-Layer Guardrails](#18-보안-체계)
  - [18.1 왜 4겹 방어가 필요한가?](#181-왜-4겹-방어가-필요한가)
  - [18.2 L1: NeMo Guardrails (입력 방어)](#182-l1-nemo-guardrails)
  - [18.3 L2: Guardrails AI (처리 중 검증)](#183-l2-guardrails-ai)
  - [18.4 L3: LlamaGuard (출력 안전 분류)](#184-l3-llamaguard)
  - [18.5 L4: Post-Delivery Audit (사후 감사)](#185-l4-post-delivery-audit)
  - [18.6 Prompt Injection 방어](#186-prompt-injection-방어)
  - [18.7 OWASP LLM Top 10 대응](#187-owasp-llm-top-10)
  - [18.8 STRIDE 위협 모델 매핑](#188-stride-위협-모델)
  - [18.9 AI 코드 생성 보안 체크리스트](#189-ai-코드-생성-보안-체크리스트)
  - [18.10 HMAC 인증 & 타이밍 공격 방어](#1810-hmac-인증)
  - [18.11 제어 역전 방지 (Control Inversion Prevention) ★GAP-7](#1811-제어-역전-방지)
  - [18.12 커뮤니티 스킬 보안 & RSP 프레임워크 ★GAP-10](#1812-커뮤니티-스킬-보안)

- [19. RBAC — 역할 기반 접근 제어](#19-rbac)
  - [19.1 4가지 역할: OWNER / ADMIN / OPERATOR / VIEWER](#191-4가지-역할)
  - [19.2 역할별 권한 매트릭스](#192-역할별-권한-매트릭스)
  - [19.3 자율도 수준: L0 ~ L3](#193-자율도-수준)

- [20. 비용 관리 — Cost Control](#20-비용-관리)
  - [20.1 버전별 비용 상한 (ABSOLUTE LOCK)](#201-버전별-비용-상한)
  - [20.2 Downshift 메커니즘 (자동 모델 다운그레이드)](#202-downshift-메커니즘)
  - [20.3 비용 최적화 전략 (캐시, 배치, 프롬프트 캐싱)](#203-비용-최적화-전략)
  - [20.4 예산 초과 시 행동 흐름](#204-예산-초과-시-행동-흐름)
  - [20.5 규제 준수 & 컴플라이언스 ★GAP-16](#205-규제-준수--컴플라이언스)

- [21. 승인 시스템 — Approval Workflow](#21-승인-시스템)
  - [21.1 언제 승인이 필요한가?](#211-언제-승인이-필요한가)
  - [21.2 P0/P1/P2 도메인별 승인 매트릭스](#212-승인-매트릭스)
  - [21.3 승인 타임아웃 (10분 → 자동 거절)](#213-승인-타임아웃)
  - [21.4 자율 운영 4단계 (L0~L3)](#214-자율-운영-4단계)
  - [21.5 S-Module / E-Module 승인 규칙](#215-s-module--e-module-승인-규칙)

---

## PART F: 에이전트 & 팀 시스템

- [22. Agent Teams — 멀티 에이전트 아키텍처](#22-agent-teams)
  - [22.1 왜 여러 에이전트가 필요한가?](#221-왜-여러-에이전트가-필요한가)
  - [22.2 Lead Agent (리드 에이전트 = ORANGE CORE)](#222-lead-agent)
  - [22.3 Sub-Agent 8가지 타입](#223-sub-agent-8가지-타입)
  - [22.4 에이전트 3요소: Identity, Capability, Policy](#224-에이전트-3요소)
  - [22.5 에이전트 생명주기 (Created → Archived)](#225-에이전트-생명주기)
  - [22.6 6가지 협업 패턴](#226-6가지-협업-패턴)
    - [22.6.1 Sequential (순차)](#2261-sequential)
    - [22.6.2 Parallel (병렬)](#2262-parallel)
    - [22.6.3 Debate (토론)](#2263-debate)
    - [22.6.4 Supervisor (감독)](#2264-supervisor)
    - [22.6.5 Handoff (인계)](#2265-handoff)
    - [22.6.6 Map-Reduce (분산-취합)](#2266-map-reduce)
  - [22.7 MoA — Mixture of Agents 패턴 ★GAP-3](#227-moa-패턴)
  - [22.8 Agent Message 형식 & HMAC 서명](#228-agent-message-형식)
  - [22.9 Delegation 제약 (LOCK)](#229-delegation-제약)
  - [22.10 버전별 에이전트 규모 (V1:3 → V2:10 → V3:50+)](#2210-버전별-에이전트-규모)
  - [22.11 V1: InMemoryDispatcher / V2+: Redis MessageBus](#2211-메시지-버스)
  - [22.12 LOCK-AT 아키텍처 제약 17건](#2212-lock-at-아키텍처-제약)
  - [22.13 Agent Profiling & Capability Registry ★GAP-4](#2213-agent-profiling)

- [23. PARL Agent Swarm — V3 대규모 에이전트](#23-parl-agent-swarm)
  - [23.1 50+ 에이전트 Mesh 아키텍처](#231-50-에이전트-mesh)
  - [23.2 Agent Marketplace (에이전트 마켓플레이스)](#232-agent-marketplace)
  - [23.3 Agent Specialization Protocol](#233-agent-specialization-protocol)
  - [23.4 A2A 프로토콜 (Agent-to-Agent)](#234-a2a-프로토콜)

- [24. Workflow 자동화 시스템](#24-workflow-자동화-시스템)
  - [24.1 DAG 기반 워크플로우](#241-dag-기반-워크플로우)
  - [24.2 12가지 Workflow 패턴](#242-12가지-workflow-패턴)
  - [24.3 SOP Pattern (절차 패턴)](#243-sop-pattern)
  - [24.4 Trigger/Action 시스템](#244-triggeraction-시스템)
  - [24.5 Agentic Coding Pattern (코딩 자동화)](#245-agentic-coding-pattern)
  - [24.6 외부 Workflow 엔진 어댑터 규칙 ★GAP-6](#246-외부-workflow-엔진-어댑터-규칙)

---

## PART G: 특화 시스템

- [25. SDAR — 자가진단 & 자동수리 시스템](#25-sdar)
  - [25.1 SDAR이란?](#251-sdar이란)
  - [25.2 5-Layer Pipeline (모니터링→진단→계획→실행→검증)](#252-5-layer-pipeline)
  - [25.3 에러 분류 체계 (5가지 카테고리)](#253-에러-분류-체계)
  - [25.4 점진적 자율성 피라미드 (AR-L0 ~ AR-L4)](#254-점진적-자율성-피라미드)
  - [25.5 SDAR 7-State 상태 머신](#255-sdar-7-state-상태-머신)
  - [25.6 수리 액션 카탈로그](#256-수리-액션-카탈로그)
  - [25.7 5-Gate 통합 (SDAR와 Gate 연동)](#257-5-gate-통합)
  - [25.8 Emergency Kill Switch (긴급 중지)](#258-emergency-kill-switch)
  - [25.9 보안 오류 특별 규칙 (LOCK)](#259-보안-오류-특별-규칙)
  - [25.10 Self-evo 원칙 준수 (LOCK)](#2510-self-evo-원칙-준수)

- [26. Cloud Library — 정보 수집 & 관리 시스템](#26-cloud-library)
  - [26.1 10-Layer 아키텍처](#261-10-layer-아키텍처)
  - [26.2 G0~G4 5-Gate 검증 시스템](#262-g0g4-5-gate)
  - [26.3 평가 점수 & 소스 신뢰도 (LOCK)](#263-평가-점수)
  - [26.4 LOCK 결정사항 (CLOUD_LIBRARY_SPEC §16)](#264-lock-결정사항)

- [27. RT-BNP — 실시간 속보 파이프라인](#27-rt-bnp)
  - [27.1 RT-BNP란?](#271-rt-bnp란)
  - [27.2 뉴스 소스 Tier 분류](#272-뉴스-소스-tier-분류)
  - [27.3 Breaking Event 분류 체계](#273-breaking-event-분류-체계)
  - [27.4 Breaking Detector 엔진](#274-breaking-detector-엔진)
  - [27.5 Fast Gate (속보 전용 간소화 검증)](#275-fast-gate)
  - [27.6 버전별 RT-BNP 구현 범위 (V1/V2/V3)](#276-버전별-rt-bnp)

- [28. DCL — Domain Context Layer (도메인 컨텍스트)](#28-dcl)
  - [28.1 선택적 배경 인식 설계 원칙](#281-선택적-배경-인식)
  - [28.2 VAMOS AI 정보 환경 6계층](#282-정보-환경-6계층)
  - [28.3 3개 도메인 컨텍스트 채널](#283-3개-도메인-컨텍스트-채널)
  - [28.4 DCL → I-2 RAG 연동 흐름](#284-dcl-rag-연동-흐름)

- [29. AI Investing — 투자 분석 시스템](#29-ai-investing)
  - [29.1 시스템 개요 & 7-Layer 데이터 아키텍처](#291-시스템-개요)
  - [29.2 83개 데이터 소스 (P0/P1/TIER-0/TIER-1/KB)](#292-83개-데이터-소스)
  - [29.3 96개 투자 전략 (기술/퀀트/옵션/ML)](#293-96개-투자-전략)
  - [29.4 51% Gate & 백테스팅 엔진](#294-51-gate)
  - [29.5 Circuit Breaker (서킷 브레이커)](#295-circuit-breaker)
  - [29.6 법적 제약 (Wash Sale, PDT, Uptick)](#296-법적-제약)
  - [29.7 데이터 스키마 (VAMOS_OHLCV_PLUS, VAMOS_EVENT)](#297-데이터-스키마)
  - [29.8 Scraper Manager (17개 웹 스크래핑 대상)](#298-scraper-manager)
  - [29.9 ML/AI 스택 (FinBERT, LSTM, RL)](#299-mlai-스택)
  - [29.10 Real-Time News 연동 (RT-BNP ↔ Investing)](#2910-real-time-news-연동)
  - [29.11 VAMOS CORE 통합 (I-2, I-6, I-8, I-9, I-18)](#2911-vamos-core-통합)
  - [29.12 Walk-Forward Validation & Z-Session ★GAP-12](#2912-walk-forward-validation)
  - [29.13 참조 플랫폼 35개 & 알려진 결함 15개 ★GAP-12](#2913-참조-플랫폼--결함)

---

## PART H: UI/UX & 인프라

- [30. UI/UX — 사용자 인터페이스](#30-uiux)
  - [30.1 설계 철학 7원칙](#301-설계-철학-7원칙)
  - [30.2 Builder View (만드는 사람용)](#302-builder-view)
  - [30.3 Hologram View (사용하는 사람용)](#303-hologram-view)
  - [30.4 3-Panel Layout (좌/중/우 패널)](#304-3-panel-layout)
  - [30.5 UI 9-State 상태 머신 (S0_BOOT ~ S8_ARCHIVED)](#305-ui-9-state)
  - [30.6 Pipeline ↔ UI 상태 매핑](#306-pipeline-ui-상태-매핑)
  - [30.7 React 컴포넌트 목록 (~44개)](#307-react-컴포넌트-목록)
  - [30.8 Custom Hooks & Zustand Stores](#308-custom-hooks)
  - [30.9 멀티모달 입출력 UI](#309-멀티모달-입출력-ui)
  - [30.10 Failure/Fallback UI 규칙](#3010-failurefallback-ui)
  - [30.11 색상 팔레트 & 아이콘 시스템](#3011-색상-팔레트)
  - [30.12 CLI 인터페이스](#3012-cli-인터페이스)
  - [30.13 접근성 (WCAG 2.1 AA) & 다국어 (i18n)](#3013-접근성--다국어)
  - [30.14 STEP7 UI 강화 항목 (104개)](#3014-step7-ui-강화)
  - [30.15 대시보드 상세 (Log/P2/Document/Innovation) ★GAP-11](#3015-대시보드-상세)

- [31. MCP — Model Context Protocol](#31-mcp)
  - [31.1 MCP란?](#311-mcp란)
  - [31.2 Streamable HTTP Transport (LOCK)](#312-streamable-http-transport)
  - [31.3 MCP 서버/클라이언트 아키텍처](#313-mcp-서버클라이언트)
  - [31.4 MCP 외부 서버 카탈로그 (11개)](#314-mcp-외부-서버-카탈로그)
  - [31.5 Dynamic Tool Registration](#315-dynamic-tool-registration)
  - [31.6 MCP Resource System & Prompt Templates](#316-mcp-resource-system)
  - [31.7 MCP ↔ Blue Node Bridge](#317-mcp-blue-node-bridge)
  - [31.8 MCP Tool Use Optimization](#318-mcp-tool-use-optimization)

- [32. 기술 스택 — Tech Stack](#32-기술-스택)
  - [32.1 V1 Stack (Local MVP)](#321-v1-stack)
  - [32.2 V2 Stack (Pro Server)](#322-v2-stack)
  - [32.3 V3 Stack (Enterprise)](#323-v3-stack)
  - [32.4 LLM 서빙: Ollama / vLLM / API](#324-llm-서빙)
  - [32.5 Brain Adapter Layer (두뇌 어댑터)](#325-brain-adapter-layer)
  - [32.6 HAL — Hardware Abstraction Layer](#326-hal)
  - [32.7 프레임워크 결정: LangGraph (LOCK)](#327-프레임워크-결정)
  - [32.8 프롬프트 캐싱 (50~90% 절감)](#328-프롬프트-캐싱)
  - [32.9 양자화 관리 (Q4_K_M 권장)](#329-양자화-관리)
  - [32.10 Model Gateway (LiteLLM)](#3210-model-gateway)
  - [32.11 Batch Processing (50% 절감)](#3211-batch-processing)
  - [32.12 A/B Model Testing Framework](#3212-ab-model-testing)
  - [32.13 MoA — Mixture of Agents 실행 패턴 ★GAP-3](#3213-moa-실행-패턴)
  - [32.14 Docker Sandboxing & 코드 실행 격리 ★GAP-2](#3214-docker-sandboxing)
  - [32.15 프레임워크 패턴 참조 (Runnable Protocol) ★GAP-18](#3215-프레임워크-패턴-참조)

- [33. 프로젝트 구조 — Monorepo](#33-프로젝트-구조)
  - [33.1 전체 디렉토리 구조 (PHASE_B2 정본)](#331-전체-디렉토리-구조)
  - [33.2 Frontend (src/) — React 18 + TypeScript](#332-frontend)
  - [33.3 Rust Backend (src-tauri/) — Tauri 2.0](#333-rust-backend)
  - [33.4 Python Backend (backend/) — vamos_core](#334-python-backend)
  - [33.5 Shared Types (shared/)](#335-shared-types)
  - [33.6 Config (config/)](#336-config)

- [34. API & 통신 시스템 — 88개 엔드포인트](#34-api--통신-시스템)
  - [34.1 Tauri IPC 커맨드 (72개)](#341-tauri-ipc)
  - [34.2 Python-Rust JSON-RPC (13개)](#342-python-rust-json-rpc)
  - [34.3 MCP Tool Protocol (3개)](#343-mcp-tool-protocol)
  - [34.4 IPC Bridge (Rust ↔ Python)](#344-ipc-bridge)
  - [34.5 응답 형식 표준 (trace_id 필수)](#345-응답-형식-표준)

- [35. 이벤트 & 로깅 시스템](#35-이벤트--로깅-시스템)
  - [35.1 EventType Registry (134개 이벤트)](#351-eventtype-registry)
  - [35.2 FailureCode Registry (36개 에러코드)](#352-failurecode-registry)
  - [35.3 Fallback Registry (23개 대응전략)](#353-fallback-registry)
  - [35.4 FailureCode → Fallback 매핑 (36:23, 1:N)](#354-failurecode-fallback-매핑)
  - [35.5 NEVER_AUTO 에러 자동 탐지](#355-never_auto)
  - [35.6 로깅 스택 (V1:JSONL / V2:Loki-lite / V3:Loki+Grafana)](#356-로깅-스택)

- [36. Configuration 시스템](#36-configuration-시스템)
  - [36.1 설정 계층: .env → config.toml → DB Runtime](#361-설정-계층)
  - [36.2 config.toml 전체 섹션 (17개)](#362-configtoml-전체-섹션)
  - [36.3 LOCK / FREEZE 값 목록](#363-lock--freeze-값-목록)
  - [36.4 VAL-001~VAL-010 검증 규칙](#364-val-001val-010)
  - [36.5 schema_registry.toml (단일 참조점)](#365-schema_registrytoml)

---

## PART I: 테스트 & 배포 & 운영

- [37. 테스트 전략 (~128개 테스트)](#37-테스트-전략)
  - [37.1 테스트 피라미드 (Unit/Integration/E2E)](#371-테스트-피라미드)
  - [37.2 V0~V1 기본 테스트 (~85개)](#372-v0v1-기본-테스트)
  - [37.3 V2 COND 모듈 테스트 (~30개)](#373-v2-cond-모듈-테스트)
  - [37.4 V3 EXP 모듈 테스트 (~13개)](#374-v3-exp-모듈-테스트)
  - [37.5 AC 매핑 (50 AC → 79 테스트)](#375-ac-매핑)
  - [37.6 상세 테스트 케이스 (T-VAL, T-SDAR, T-HMAC, T-GUARD, T-GDPR, T-AC, T-ARCH)](#376-상세-테스트-케이스)

- [38. CI/CD 파이프라인](#38-cicd-파이프라인)
  - [38.1 GitHub Actions 워크플로우 (~14개)](#381-github-actions)
  - [38.2 브랜치 전략 (main/develop/feature/hotfix)](#382-브랜치-전략)
  - [38.3 8-Stage 파이프라인](#383-8-stage-파이프라인)
  - [38.4 보안 스캔 (SAST, Dependency Audit)](#384-보안-스캔)

- [39. 배포 전략](#39-배포-전략)
  - [39.1 V1: 로컬 (Windows/WSL)](#391-v1-로컬)
  - [39.2 V2: Docker Compose](#392-v2-docker-compose)
  - [39.3 V3: Kubernetes (Helm Chart)](#393-v3-kubernetes)
  - [39.4 Blue-Green 배포](#394-blue-green-배포)
  - [39.5 V3 인프라 대안: Hetzner + RunPod](#395-v3-인프라-대안)

- [40. 운영 가이드](#40-운영-가이드)
  - [40.1 모니터링 전략 (V1/V2/V3)](#401-모니터링-전략)
  - [40.2 백업 & 복구 (RPO/RTO)](#402-백업--복구)
  - [40.3 인시던트 대응 프로세스](#403-인시던트-대응-프로세스)
  - [40.4 알림 체계](#404-알림-체계)
  - [40.5 롤백 프로세스](#405-롤백-프로세스)
  - [40.6 헬스체크](#406-헬스체크)
  - [40.7 로그 보존 정책](#407-로그-보존-정책)
  - [40.8 비용 초과 대응](#408-비용-초과-대응)
  - [40.9 SDAR 수동 폴백](#409-sdar-수동-폴백)

---

## PART J: 자기 진화 & 버전 로드맵

- [41. Self-Evolution — 자기 진화 시스템](#41-self-evolution)
  - [41.1 자기 진화란?](#411-자기-진화란)
  - [41.2 변경 가능한 6가지 영역](#412-변경-가능한-6가지-영역)
  - [41.3 변경 불가 7가지 영역 (LOCK)](#413-변경-불가-7가지-영역)
  - [41.4 롤백 정책 (스냅샷, 이상 탐지, 재적용 잠금)](#414-롤백-정책)
  - [41.5 Constitutional AI + DPO (피드백 학습)](#415-constitutional-ai--dpo)
  - [41.6 Red Teaming / Bias Detection / Watermarking](#416-red-teaming--bias--watermarking)
  - [41.7 Hallucination Detection (NLI 기반)](#417-hallucination-detection)
  - [41.8 구현 운영 규칙 R1~R11 & 세션 관리 ★GAP-13](#418-구현-운영-규칙-r1r11)
  - [41.9 Adaptive Thinking — 난이도별 사고 깊이 (S7B-001)](#419-adaptive-thinking)

- [42. 버전 로드맵 — V0 → V1 → V2 → V3](#42-버전-로드맵)
  - [42.1 V0: Scaffold (1~2주)](#421-v0-scaffold)
  - [42.2 V1: Operational MVP (14~16주)](#422-v1-operational-mvp)
  - [42.3 V2: Pro Server (11~13주)](#423-v2-pro-server)
  - [42.4 V3: Enterprise (12~16주)](#424-v3-enterprise)
  - [42.5 버전 전환 GO/NO-GO 체크리스트](#425-gonogo-체크리스트)
  - [42.6 마이그레이션 전략 (V1→V2→V3)](#426-마이그레이션-전략)
  - [42.7 버전 진입 준비 체크리스트 & Readiness ★GAP-15](#427-버전-진입-준비)

- [43. V2 COND 확장 모듈 (106개)](#43-v2-cond-확장-모듈)
  - [43.1 CAT-A: AI/ML 엔진 (13개)](#431-cat-a)
  - [43.2 CAT-B: 지식관리 (13개)](#432-cat-b)
  - [43.3 CAT-C: 운영/인프라 (53개)](#433-cat-c)
  - [43.4 CAT-D: 미디어/생성 (8개)](#434-cat-d)
  - [43.5 CAT-E: 교육/학습 (7개)](#435-cat-e)
  - [43.6 CAT-F: 웰빙/건강 (8개)](#436-cat-f)
  - [43.7 CAT-G: 외부통합 확장 (4개)](#437-cat-g)

---

## PART K: 부록 & 참조

- [44. STEP7 — AI 기술 강화 16개 카테고리 (A~P)](#44-step7)
  - [44.1 Cat-A: 기초 강화](#441-cat-a)
  - [44.2 Cat-B: 대화/프로세스](#442-cat-b)
  - [44.3 Cat-C: UI/UX 전수 비교](#443-cat-c)
  - [44.4 Cat-D: 메모리/저장소 아키텍처](#444-cat-d)
  - [44.5 Cat-E: 보안/안전/거버넌스](#445-cat-e)
  - [44.6 Cat-F: 인프라/배포/MLOps](#446-cat-f)
  - [44.7 Cat-G: 벤치마크/평가/품질보증](#447-cat-g)
  - [44.8 Cat-H: 비즈니스모델/시장전략](#448-cat-h)
  - [44.9 Cat-I: AI Investing 보강](#449-cat-i)
  - [44.10 Cat-J: 멀티모달/생성처리](#4410-cat-j)
  - [44.11 Cat-K: 에이전트/프로토콜/상호운용](#4411-cat-k)
  - [44.12 Cat-L: 개발자도구/API/SDK](#4412-cat-l)
  - [44.13 Cat-M: PKM/지식관리](#4413-cat-m)
  - [44.14 Cat-N: 워크플로우/자동화/RPA](#4414-cat-n)
  - [44.15 Cat-O: 교육/학습/자기개발](#4415-cat-o)
  - [44.16 Cat-P: 건강/웰니스/감성AI](#4416-cat-p)

- [45. 스키마 정의 전체 목록 (D2.1-D1~D8)](#45-스키마-정의)
  - [45.1 D2.1-D2: ORANGE CORE 스키마](#451-orange-core-스키마)
  - [45.2 D2.1-D3: BLUE NODES 스키마](#452-blue-nodes-스키마)
  - [45.3 D2.1-D4: INFRA CORE 스키마](#453-infra-core-스키마)
  - [45.4 D2.1-D5: AGENT WORKFLOW 스키마](#454-agent-workflow-스키마)
  - [45.5 D2.1-D6: STORAGE & MEMORY 스키마](#455-storage-memory-스키마)
  - [45.6 D2.1-D7: SAFETY/COST/APPROVAL 스키마](#456-safety-스키마)
  - [45.7 D2.1-D8: UI/UX 스키마](#457-uiux-스키마)

- [46. 의존성 & 패키지 목록 (PHASE_B3)](#46-의존성--패키지-목록)
  - [46.1 Python 패키지 (pyproject.toml)](#461-python-패키지)
  - [46.2 Rust 크레이트 (Cargo.toml)](#462-rust-크레이트)
  - [46.3 Node 패키지 (package.json)](#463-node-패키지)

- [47. 정본 문서 맵 & 우선순위](#47-정본-문서-맵)
  - [47.1 SOT 68개 문서 전체 인덱스](#471-sot-68개-문서-인덱스)
  - [47.2 문서 권위 체계 (RULE > PLAN > DESIGN > 스키마)](#472-문서-권위-체계)
  - [47.3 SOURCE_CONFLICT 전수 인덱스](#473-source_conflict-전수-인덱스)
  - [47.4 LOCK / FREEZE 값 전체 레지스트리](#474-lock--freeze-값-레지스트리)
  - [47.5 DEC 결정사항 통합 인덱스 (DEC-001~DEC-017+) ★GAP-14](#475-dec-결정사항-통합-인덱스)
  - [47.6 ADD-xxx 항목 전수 인덱스 & 매핑 ★GAP-17](#476-add-xxx-항목-전수-인덱스)

- [48. 용어집 (Glossary)](#48-용어집)

- [49. 자주 묻는 질문 (FAQ)](#49-자주-묻는-질문)

---

## 크로스체크 커버리지 매핑 (v1.1.0 업데이트)

> 아래는 본 문서의 각 섹션이 어떤 SOT 문서를 근거로 하는지 추적 매핑입니다.
> ★ 표시 = v1.1.0에서 신규 추가된 Gap 보완 항목

| 본 문서 섹션 | 근거 SOT 문서 | 비고 |
|-------------|-------------|------|
| §1 정체성/철학/목표 | BASE-1.3, PLAN-3.0, BEGINNER_GUIDE | 14 Goals, 7 Non-Goals |
| §2 4계층 아키텍처 | D2.0-01, PLAN-3.0 §1.3A | 계층 구조도 |
| §2.8 ★개발 환경 셋업 | D2.0-04 | V1/V2/V3 구성 |
| §3 파이프라인/9-State | D2.0-02 §2.2, D2.0-05 §7 | 9-State LOCK |
| §3.7 ★에러 처리 표준 | D2.0-02 §0.3, §1.2 | Result&lt;T, VamosError&gt; |
| §4 5-Gate | D2.0-07, D2.0-02 §I-5 | Gate 우선순위 |
| §4.9 ★HITL/Threshold | D2.0-07 §2.1, §15.10 | SF-L01, Ledger |
| §5 Decision 객체 | D2.0-02 §2.4, D2.1-D2 | IntentFrame, EvidencePack |
| §6 모듈 개요 | D2.0-01 §1.4, CLAUDE.md | 81개 모듈 카탈로그 |
| §7 I-Series 25개 | D2.0-02 전체 | I-1~I-25 상세 |
| §8 E-Series 16개 | D2.0-04, CLAUDE.md | E-1~E-16, ★Docker Sandbox |
| §9 S-Series 8개 | D2.0-01, CLAUDE.md | S-1~S-8 |
| §10 A-Series 7개 | D2.0-01, D2.0-04 | A-1~A-7 |
| §11 B-Series 6개 | D2.0-01, D2.0-06 | B-1~B-6 |
| §11.7 ★프롬프트 관리 | D2.0-05 §7.5 | 템플릿 진화 시스템 |
| §12 C-Series 7개 | D2.0-01 | C-1~C-7 |
| §13 D-Series 6개 | D2.0-01 | D-1~D-6 |
| §14 EVX-Series 6개 | D2.0-01, D2.0-05 §7.4 | EVX-1~EVX-6 |
| §15 도메인 P0/P1/P2 | D2.0-03, BASE-1.3 | Blue Node 생명주기 |
| §16 메모리 L0~L3 | D2.0-06 | 4계층+4유형 |
| §16.10 ★데이터 프라이버시 | D2.0-07, STEP7-E | S7E-031~040 |
| §17 RAG 시스템 | D2.0-06 §1.1, D2.1-A1 | 6-Stage, Hybrid Search |
| §18 보안 4-Layer | D2.0-07, STEP7-E | Guardrails, HMAC |
| §18.11 ★제어 역전 방지 | D2.0-07 §15.12 | S09-B48, Kill Switch |
| §18.12 ★커뮤니티 보안 | D2.0-07, STEP7-E | RSP 프레임워크 |
| §19 RBAC | D2.0-07 §3.6 | 4역할 |
| §20 비용 관리 | D2.0-07 §4, BASE-1.3 | ABSOLUTE LOCK |
| §20.5 ★규제 준수 | D2.0-07, STEP7-H | GDPR, SOC2 |
| §21 승인 시스템 | D2.0-07 §3.3 | P0/P1/P2 매트릭스 |
| §22 Agent Teams | AGENT_TEAMS_SPEC | Lead+Sub, 6패턴 |
| §22.7 ★MoA 패턴 | D2.0-04 §4.9 | Multi-agent 오케스트레이션 |
| §22.13 ★Agent Profiling | D2.0-05 ADD-027 | Capability Registry |
| §23 PARL/Mesh | AGENT_TEAMS_SPEC, PLAN-3.0 | V3 확장 |
| §24 Workflow | D2.0-05 §12 | DAG, 12패턴, SOP |
| §24.6 ★외부 엔진 어댑터 | D2.0-05 §7.3 | LangGraph LOCK |
| §25 SDAR | SDAR_SPEC | 5-Layer, AR-L0~L4 |
| §26 Cloud Library | CLOUD_LIBRARY_SPEC | 10-Layer, G0~G4 |
| §27 RT-BNP | CLOUD_LIBRARY_SPEC §RT-BNP | 속보 파이프라인 |
| §28 DCL | CLOUD_LIBRARY_SPEC §DCL | 도메인 컨텍스트 |
| §29 AI Investing | AI_INVESTING_SPEC | 83소스, 96전략 |
| §29.12 ★Walk-Forward | AI_INVESTING_SPEC §17 | Z-Session |
| §29.13 ★참조 플랫폼 | AI_INVESTING_SPEC §19 | 35개+15 결함 |
| §30 UI/UX | D2.0-08 | Builder/Hologram, 104항목 |
| §30.15 ★대시보드 상세 | D2.0-08 §12, §14 | Log/P2/Document |
| §31 MCP | D2.0-03 §K, D2.0-04 | 11서버, Transport |
| §32 Tech Stack | D2.1-A1, D2.0-04 | V1/V2/V3 Combo |
| §32.13 ★MoA 실행 | D2.0-04 §4.9 | 멀티모델 병렬 |
| §32.14 ★Docker Sandbox | D2.0-02 §1.3-A | 코드 격리 |
| §32.15 ★Runnable Protocol | D2.0-04 §4.4 | 프레임워크 패턴 |
| §33 프로젝트 구조 | PHASE_B2 | Monorepo |
| §34 API 88개 | PHASE_B1 | IPC/RPC/MCP |
| §35 이벤트/로깅 | D2.1-D2, D2.0-01 | 134+36+23 Registry |
| §36 Configuration | PHASE_B4 | config.toml 17섹션 |
| §37 테스트 | PHASE_B5 | 128개, AC매핑 |
| §38 CI/CD | PHASE_B6 | GitHub Actions |
| §39 배포 | PHASE_B7, PLAN-3.0 | Docker/K8s |
| §40 운영 | PART2 §6.12 | 모니터링/백업/인시던트 |
| §41 Self-Evolution | D2.0-07, BASE-1.3 | 6변경/7불변 |
| §41.8 ★R1~R11 규칙 | PART2 §1.3 | 세션 관리 |
| §41.9 ★Adaptive Thinking | D2.0-02 S7B-001 | 난이도별 사고 |
| §42 버전 로드맵 | PLAN-3.0, PART2 §1-5 | V0~V3 |
| §42.7 ★Readiness | IMPL_READINESS 3개 문서 | GO/NO-GO |
| §43 v10 COND 확장 | PART2 §V2-Phase2 | 106개 CAT-A~G |
| §44 STEP7 | STEP7 A-P 5개 문서 | 16카테고리 |
| §45 스키마 | D2.1-D1~D8 | Pydantic v2 |
| §46 의존성 | PHASE_B3 | 패키지 목록 |
| §47 정본 맵 | MASTER_SPEC, 전체 SOT | 68개 인덱스 |
| §47.5 ★DEC 통합 | MASTER_SPEC §17 | DEC-001~017+ |
| §47.6 ★ADD 인덱스 | D2.0-01~08 전체 | ADD-xxx 100+항목 |
| §48 용어집 | BEGINNER_GUIDE, PART2 | 용어 통합 |
| §49 FAQ | BEGINNER_GUIDE | 초보자 질문 |

---

> **v1.1.0 변경사항**: 18개 Gap 보완으로 총 49개 섹션 내 서브섹션 추가. 섹션 번호 유지, 서브섹션으로 삽입.
> **다음 단계**: 작업 세션 운영 가이드(`VAMOS_초보자가이드_작업세션_운영가이드.md`) 참조하여 순차 작성 진행.
