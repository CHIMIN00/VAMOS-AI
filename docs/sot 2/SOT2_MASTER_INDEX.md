# SOT 2 마스터 인덱스

> **목적**: VAMOS AI의 모든 기능에 대한 상세내용을 Part2 구현단계의 빈껍데기/미완성 부분을 채우기 위한 Second Source of Truth
> **기준 소스**: Part2 구현단계 (6,313줄) + SOT 원본 (68파일) + 기존 SOT 2
> **생성일**: 2026-03-22
> **구조**: 5 Tier / 19개 대분류 / 107건 하위항목 + COND 106개 모듈

---

## Part2에서 FULL이라 SOT 2 불필요 확인된 영역 (7건)

| 영역 | Part2 섹션 | 상태 |
|------|-----------|------|
| SDAR (자가진단/수리) | 6.9 | FULL |
| Cloud Library | 6.10 | FULL |
| Agent Teams | 6.7 | FULL (대부분) |
| 보안/거버넌스 | 6.5 | FULL |
| 메모리/저장소/RAG | V1-Phase 2 | FULL |
| UI/UX | 6.1 | FULL |
| Brain Adapter/HAL | D2.0-04 | FULL (아키텍처) |

---

## Tier 1: Core Intelligence (ORANGE CORE 내부)

### 1-1. Verifier / Reasoning Engines
- **폴더**: `1-1_Verifier-Reasoning-Engines/`
- **파일**: `VERIFIER_REASONING_ENGINES_상세명세.md` (321줄)
- **내용**: C-1 Logic Verifier, C-2 Math Verifier, C-3 Code Verifier, D-1 Think Engine, D-2 Multimodal Engine
- **Part2 상태**: SHELL (이름 + 1줄만)
- **SOT 근거**: D2.0-01 S5.10~5.11, D2.0-02 S7

### 1-2. Auxiliary I-Series Modules
- **폴더**: `1-2_Auxiliary-Modules/`
- **파일**: `AUXILIARY_MODULES_상세명세.md` (336줄)
- **내용**: I-4 Multimodal Interpreter, I-13 Multimodal Renderer, I-14 Summarizer, I-16 Knowledge Search Engine, S-1 Self-check Engine
- **Part2 상태**: PARTIAL (2~3줄 + SOT 포인터)
- **SOT 근거**: D2.0-01 S5.6, D2.0-02 S7, D2.0-06

---

## Tier 2: Domain Execution (BLUE NODE 실행 계층)

### 2-1. Blue Node Architecture
- **폴더**: `2-1_Blue-Node-Architecture/`
- **파일**: `BLUE_NODE_ARCHITECTURE_상세명세.md` (1,027줄)
- **내용**: Permission Matrix (K-041), CORE-NODE Interface Contract (SS5.2), Template Set Injection (SS4.2), Node Lifecycle State Machine, Memory Sharing Protocol (K-029), Domain-specific Policy Overrides, MCP-Blue Node Bridge (K-010)
- **Part2 상태**: GAP (SOT에 정의되어 있으나 Part2에 없음)
- **SOT 근거**: D2.0-03 SS4~SS6

### 2-2. COND Modules Detail (V2 106개 모듈)
- **폴더**: `2-2_COND-Modules-Detail/`
- **마스터 파일**: `COND_MODULES_종합명세.md` (1,464줄)
- **하위 폴더**: CAT-A ~ CAT-G (7개)
  - `CAT-A_AI-ML-Engine/` -- 13개 모듈
  - `CAT-B_Knowledge/` -- 13개 모듈
  - `CAT-C_Ops-Infra/` -- 53개 모듈 (E-0XX 39개 포함)
  - `CAT-D_Media/` -- 8개 모듈
  - `CAT-E_Education/` -- 7개 모듈
  - `CAT-F_Wellbeing/` -- 8개 모듈
  - `CAT-G_Integration/` -- 4개 모듈
- **Part2 상태**: SHELL (이름=설명, 39개 "E-0XX 운영"만)
- **SOT 근거**: D2.0-01~03, STEP7 A-P 전체

---

## Tier 3: Feature Domains (기능 도메인별)

### 3-1. AI Investing Detail ✅ 진행중
- **폴더**: `Ai-investing-detail/`
- **파일**: 21개 (19개 관점 + 종합계획서 + 검증도구)
- **상태**: L3 품질 업그레이드 진행중
- **SOT 근거**: VAMOS_AI_INVESTING_SPEC, STEP7-I

### 3-2. Multimodal Processing
- **폴더**: `3-2_Multimodal-Processing/`
- **파일**: `MULTIMODAL_PROCESSING_상세명세.md` (493줄)
- **내용**: 이미지(CLIP/OCR/Vision), 오디오(Whisper/Deepgram/TTS), 비디오(FFmpeg), 멀티모달 대화 구조, 차트/다이어그램 생성, 크로스모달 검색, 비용관리
- **Part2 상태**: SHELL (파일명 + 백로그 1줄만)
- **SOT 근거**: STEP7-J (98개 항목)

### 3-3. PKM / Knowledge Management
- **폴더**: `3-3_PKM-Knowledge-Management/`
- **파일**: `PKM_KNOWLEDGE_MANAGEMENT_상세명세.md` (579줄)
- **내용**: 지식 캡처 파이프라인, 대화 지식 추출, Neo4j 지식 그래프, SM-2 간격 반복, 지식 신선도/충돌, Notion/Obsidian 통합, Zettelkasten
- **Part2 상태**: SHELL (CAT-B 카탈로그만)
- **SOT 근거**: STEP7-M (78개 항목)

### 3-4. Workflow / RPA
- **폴더**: `3-4_Workflow-RPA/`
- **파일**: `WORKFLOW_RPA_상세명세.md` (581줄)
- **내용**: DAG 워크플로우 엔진, NL→워크플로우 생성, 트리거 시스템, 템플릿 라이브러리, 브라우저 자동화(Playwright), RPA 데스크톱 자동화
- **Part2 상태**: SHELL (I-12 4줄만)
- **SOT 근거**: STEP7-N (72개 항목)

### 3-5. Education / Learning
- **폴더**: `3-5_Education-Learning/`
- **파일**: `EDUCATION_LEARNING_상세명세.md` (690줄)
- **내용**: 적응형 학습 엔진(Khanmigo/Socratic), SM-2 간격 반복, 코딩 튜토리얼(LeetCode-style), 교육 컨텐츠 생성, 학습 분석 대시보드
- **Part2 상태**: SHELL (CAT-E + UI 1개)
- **SOT 근거**: STEP7-O (68개 항목)

### 3-6. Health / Wellness / Emotion AI
- **폴더**: `3-6_Health-Wellness-EmotionAI/`
- **파일**: `HEALTH_WELLNESS_EMOTIONAI_상세명세.md` (767줄)
- **내용**: 감정 인식 파이프라인(KoBERT/Hume AI), 감정 적응 응답, 건강 데이터 통합(HealthKit), 스트레스 관리(호흡법/CBT), 감정 일지/트렌드
- **Part2 상태**: SHELL (CAT-F + UI 일부)
- **SOT 근거**: STEP7-P (62개 항목)

### 3-7. Developer Tools / API / SDK
- **폴더**: `3-7_Developer-Tools-API-SDK/`
- **파일**: `DEVELOPER_TOOLS_API_SDK_상세명세.md` (546줄)
- **내용**: Dev Node 코딩 엔진, FIM 자동완성, 코드 리팩토링, 자동 테스트 생성, Plugin SDK, VS Code 확장
- **Part2 상태**: MENTION-ONLY (백로그 1줄 2건)
- **SOT 근거**: STEP7-L (82개 항목)

### 3-8. Conversation / A2A Protocol
- **폴더**: `3-8_Conversation-A2A/`
- **파일**: `CONVERSATION_A2A_상세명세.md` (593줄)
- **내용**: A2A 메시지 포맷(JSON-RPC 2.0), 에이전트 디스커버리(mDNS), A2A 보안(mTLS+JWT), 대화 프로세스 고급 기능, MoA 패턴
- **Part2 상태**: PARTIAL (파일 구조만)
- **SOT 근거**: STEP7-B, D2.0-05

### 3-9. Business Model / Strategy
- **폴더**: `3-9_Business-Model-Strategy/`
- **파일**: `BUSINESS_MODEL_STRATEGY_상세명세.md` (576줄)
- **내용**: 가격 전략/수익 모델, 타겟 페르소나/시장 분석, GTM/성장 전략, 리스크 분석/재무 모델링
- **Part2 상태**: ABSENT (구현 가이드에 없음)
- **SOT 근거**: STEP7-H (78개 항목)

### 3-10. Agent Protocol / Interoperability
- **폴더**: `3-10_Agent-Protocol-Interoperability/`
- **파일**: `AGENT_PROTOCOL_INTEROPERABILITY_상세명세.md` (770줄)
- **내용**: 멀티 에이전트 프레임워크(CrewAI/AutoGen/LangGraph), 외부 서비스 통합, 데이터 교환 포맷, 에이전트 배포/스케일링, VAMOS 차별화, 에이전트 자율성/안전성
- **Part2 상태**: PARTIAL (~50개 항목 미반영)
- **SOT 근거**: STEP7-K (86개 항목)

---

## Tier 4: Infrastructure & Platform (인프라/플랫폼)

### 4-1. Rust / Tauri Infrastructure
- **폴더**: `4-1_Rust-Tauri-Infrastructure/`
- **파일**: `RUST_TAURI_INFRASTRUCTURE_상세명세.md` (379줄)
- **내용**: 72개 IPC 커맨드 핸들러, 25개 Serde 모델, 13개 Python-Rust JSON-RPC, Python 프로세스 관리
- **Part2 상태**: PARTIAL (108개 항목 ~20줄만)
- **SOT 근거**: PHASE_B1, PHASE_B2, D2.1-D2~D4

### 4-2. CI/CD Pipeline
- **폴더**: `4-2_CICD-Pipeline/`
- **파일**: `CICD_PIPELINE_상세명세.md` (401줄)
- **내용**: 14개 GitHub Actions 워크플로우, job 의존성, 트리거/환경, 시크릿, 캐싱, 병렬화
- **Part2 상태**: PARTIAL (14개 파일명만)
- **SOT 근거**: PHASE_B6

### 4-3. MCP Server / Client
- **폴더**: `4-3_MCP-Server-Client/`
- **파일**: `MCP_SERVER_CLIENT_상세명세.md` (463줄)
- **내용**: 20+ 내부 MCP 도구(스키마 포함), MCP Bridge, 도구 디스커버리, 11개 외부 MCP 서버 연동
- **Part2 상태**: PARTIAL (도구 스키마 없음)
- **SOT 근거**: PHASE_B1, D2.0-04

### 4-4. MLOps / LLMOps
- **폴더**: `4-4_MLOps-LLMOps/`
- **파일**: `MLOPS_LLMOPS_상세명세.md` (377줄)
- **내용**: 프롬프트 버전 관리, 모델 평가 파이프라인, 드리프트 감지, Canary 배포, 피드백 루프
- **Part2 상태**: NOT COVERED
- **SOT 근거**: STEP7-F Part 9

---

## Tier 5: Quality & Cross-cutting (품질/횡단 관심사)

### 5-1. Benchmark / Evaluation
- **폴더**: `5-1_Benchmark-Evaluation/`
- **파일**: `BENCHMARK_EVALUATION_상세명세.md` (281줄)
- **내용**: MMLU/HumanEval/MBPP/LogicKor/ARC-AGI 루브릭, 테스트 데이터셋, VBS-12~17, 인간 평가, +190개 테스트 커버리지
- **Part2 상태**: PARTIAL (러너 + 2개만 구체적)
- **SOT 근거**: STEP7-G, PHASE_B5

### 5-2. File Context (대용량 컨텍스트) ✅ 진행중
- **폴더**: `FILE CONTEXT/`
- **파일**: `VAMOS_파일_컨텍스트_이해_최종_업데이트.md` (1,618줄)
- **내용**: Lost-in-the-Middle, Context Rot, G1~G8 갭, W1~W12 보강, H1~H17 고구현성
- **상태**: 진행중

### 5-3. v12 Additions Detail (횡단)
- **폴더**: `5-3_v12-Additions-Detail/`
- **파일**: `V12_ADDITIONS_상세명세.md` (535줄)
- **내용**: Part2 전체에 걸친 v12 추가항목 총정리 (UI/UX 4건, Agent Teams 2건, AI Investing 2건, Cloud Library 10건, V2-P3 15건, V3-P2 6건, V3-P3 6건)
- **Part2 상태**: PARTIAL (1줄 설명만)

### 5-4. v23 Extension Items (횡단 인덱스)
- **폴더**: `5-4_v23-Extension-Items/`
- **파일**: `V23_EXTENSION_ITEMS_인덱스.md` (218줄)
- **내용**: 87개 v23 SHELL 확장항목 추적 인덱스 (V2-P2 51건, V2-P3 14건, V3-P2 6건, V3-P3 16건) → 도메인별 SOT 2 폴더 교차 참조
- **Part2 상태**: SHELL (이름=설명)

---

## 통계

| 항목 | 수치 |
|------|------|
| **총 대분류 폴더** | 19개 (+ 기존 2개 = 21개) |
| **신규 생성 파일** | 18개 상세명세 |
| **신규 총 라인수** | ~10,000줄 |
| **기존 파일 (AI Investing)** | 21개 (~2,800줄) |
| **기존 파일 (FILE CONTEXT)** | 1개 (1,618줄) |
| **전체 SOT 2 파일** | 40+ 개 |
| **전체 SOT 2 라인수** | ~14,400줄 |
| **커버리지: VAMOS 모듈** | 107건 하위항목 + COND 106개 |
| **진행중** | 3개 (AI Investing, File Context) |
| **미착수** | 16개 대분류 |
