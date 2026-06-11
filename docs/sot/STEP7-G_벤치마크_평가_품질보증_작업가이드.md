# STEP7-G: 벤치마크 / 평가 / 품질보증 심화 작업가이드

> **최종 업데이트**: 2026-02-22
> **목적**: VAMOS AI의 품질을 정량적으로 측정·평가·보증하는 체계를 수립. 표준 벤치마크, Agent 평가, RAG 평가, 사용자 경험 평가, VAMOS 고유 벤치마크까지 전수 정리
> **대상 비교**: ChatGPT, Claude, Gemini, Perplexity, Grok, Mistral, DeepSeek, Meta AI, Open-source 모델
> **총 항목**: 88건 (Part 1~11)

---

## 통계 요약

| 구분 | 항목 수 | 우선도 분포 |
|------|---------|------------|
| Part 1: 표준 LLM 벤치마크 | 10 | HIGH 6 / MED 4 |
| Part 2: 한국어 특화 벤치마크 | 8 | CRITICAL 2 / HIGH 4 / MED 2 |
| Part 3: 코딩 벤치마크 | 8 | HIGH 5 / MED 3 |
| Part 4: Agent/Tool Use 벤치마크 | 8 | CRITICAL 2 / HIGH 4 / MED 2 |
| Part 5: RAG 품질 평가 | 10 | CRITICAL 2 / HIGH 5 / MED 3 |
| Part 6: 안전성 벤치마크 | 8 | CRITICAL 2 / HIGH 4 / MED 2 |
| Part 7: 사용자 경험(UX) 평가 | 8 | HIGH 4 / MED 4 |
| Part 8: VAMOS 고유 벤치마크 | 10 | CRITICAL 3 / HIGH 5 / MED 2 |
| Part 9: 자동 평가 파이프라인 | 8 | HIGH 5 / MED 3 |
| Part 10: 인간 평가 프로세스 | 6 | HIGH 3 / MED 3 |
| Part 11: 품질 보증 프로세스 | 4 | HIGH 2 / MED 2 |
| **합계** | **88** | **CRITICAL 11 / HIGH 47 / MED 30** |

---

## Part 1: 표준 LLM 벤치마크 (10건)

### 주요 벤치마크 전수비교표

| 벤치마크 | 카테고리 | 측정 대상 | GPT-4o | Claude 3.5 Sonnet | Gemini 2.0 | Llama 3.3 70B | DeepSeek V3 | VAMOS 활용 |
|---------|---------|----------|--------|-------------------|-----------|--------------|-------------|-----------|
| MMLU | 지식 | 57개 과목 | 88.7 | 88.7 | 87.5 | 86.0 | 88.5 | 모델 선택 기준 |
| MMLU-Pro | 지식(강화) | 난이도↑ | 72.6 | 78.0 | 75.2 | 66.4 | 75.9 | 추론 모델 선택 |
| GPQA | 전문 지식 | 대학원 수준 | 53.6 | 65.0 | 59.1 | 46.7 | 59.1 | 전문가 작업 라우팅 |
| HumanEval | 코딩 | Python 생성 | 90.2 | 92.0 | 87.6 | 88.4 | 89.0 | 코딩 Agent 모델 |
| MATH | 수학 | 경시대회 수준 | 76.6 | 78.3 | 83.9 | 77.0 | 84.3 | 수학 능력 |
| GSM8K | 수학(기초) | 초중등 수학 | 95.8 | 96.4 | 95.2 | 93.8 | 96.7 | 기본 추론 |
| MT-Bench | 대화 | 다턴 대화 | 9.32 | 9.12 | 9.20 | 8.95 | 9.05 | 대화 품질 |
| IFEval | 지시따르기 | 지시 준수 | 84.3 | 88.4 | 85.7 | 82.1 | 86.2 | 명령 수행력 |
| ARC-C | 추론 | 과학 추론 | 96.4 | 96.7 | 95.8 | 94.5 | 96.3 | 기본 추론력 |
| HellaSwag | 상식 | 상식 추론 | 95.3 | 94.8 | 95.0 | 93.2 | 95.1 | 상식 수준 |

**S7G-001** | HIGH | V1 | MMLU/MMLU-Pro — 범용 지식 벤치마크
- 내용: 모델의 전반적 지식 수준 평가 기준
- VAMOS 활용:
  - 새 모델 도입 시 MMLU 최소 85+ 필수
  - MMLU-Pro 65+ 이상 모델만 추론 작업에 라우팅
  - 모델 카탈로그에 MMLU 점수 기록
- 자체 테스트: 한국어 번역 MMLU 서브셋 (100문항) 자동 실행

**S7G-002** | HIGH | V1 | HumanEval / MBPP — 코딩 능력 평가
- 내용: 코드 생성 능력 평가 표준 벤치마크
- VAMOS 활용:
  - Dev Node 모델 선택 기준: HumanEval 85+
  - pass@1 (단일 시도 통과율) 기준 적용
  - HumanEval+ (강화판): 엣지 케이스 포함 테스트
- 자체 확장: VAMOS 코딩 작업 유형별 커스텀 테스트 (Python, JS, Rust)

**S7G-003** | HIGH | V1 | MT-Bench — 다턴 대화 품질 평가
- 내용: 멀티턴 대화에서의 응답 품질 평가 (GPT-4 Judge)
- VAMOS 활용:
  - 대화 모델 품질 기준: MT-Bench 8.5+
  - 카테고리별 점수 분석: writing, reasoning, math, coding, extraction, stem, humanities, roleplay
  - VAMOS 커스텀 카테고리 추가: 한국어, 투자, 개인비서

**S7G-004** | HIGH | V1 | IFEval — 지시 따르기 평가
- 내용: 복잡한 지시를 얼마나 정확히 따르는지 평가
- VAMOS 활용:
  - Agent 작업의 핵심: 복잡한 지시 정확 수행
  - 지시 유형: 포맷 제한, 길이 제한, 내용 제한, 조건부 응답
  - 목표: IFEval 점수 85+ 모델만 Agent 작업 배정
- Constitution 준수 테스트와 연계

**S7G-005** | HIGH | V1 | GPQA / ARC-C — 전문 지식 + 추론 평가
- 내용: 고난이도 전문 지식 및 과학적 추론 능력 평가
- VAMOS 활용:
  - Research Node 모델 기준: GPQA 50+
  - 투자 분석 작업에서 추론력 중요
  - Quant Node: 수학적 추론 능력 필수

**S7G-006** | HIGH | V1 | MATH / GSM8K — 수학적 추론 평가
- 내용: 수학 문제 풀이 능력 평가 (초등~경시대회 수준)
- VAMOS 활용:
  - Quant/Trading Node 모델 기준: MATH 70+, GSM8K 95+
  - 투자 계산, 포트폴리오 분석, 리스크 계산에 필수
  - Chain-of-Thought + Tool Use (계산기) 병행 테스트

**S7G-007** | MED | V2 | AlpacaEval 2.0 — 지시따르기 자동 평가
- 내용: 오픈 엔드 지시의 품질을 GPT-4 Judge로 자동 평가
- VAMOS 활용: 월간 모델 비교, Length-Controlled (LC) 점수로 길이 편향 보정

**S7G-008** | MED | V2 | Chatbot Arena ELO — 인간 선호도 기반 평가
- 내용: 실제 인간 평가자의 선호도 기반 ELO 레이팅 참조
- VAMOS 활용:
  - LMSYS Chatbot Arena 순위 모니터링 (월간)
  - 새 모델 평가 시 Arena 순위 참고
  - VAMOS 내부에서도 A/B 비교 → ELO 산출

**S7G-009** | MED | V2 | WildBench — 실제 사용 시나리오 벤치마크
- 내용: 실제 사용자 질문 기반 현실적 벤치마크
- VAMOS 활용: 학술 벤치마크와 실사용 간 갭 측정, 분기별 실행

**S7G-010** | MED | V2 | LiveBench — 지속 갱신 벤치마크
- 내용: 데이터 오염 방지를 위해 매월 새 문제로 갱신되는 벤치마크
- VAMOS 활용: 모델의 진짜 실력 측정 (학습 데이터에 포함 불가)

---

## Part 2: 한국어 특화 벤치마크 (8건)

### 한국어 벤치마크 전수비교표

| 벤치마크 | 측정 대상 | 작업 수 | GPT-4o | Claude 3.5 | Gemini 2.0 | 비고 |
|---------|----------|--------|--------|-----------|-----------|------|
| KoBEST | 한국어 NLU 5종 | 5 | ~92 | ~91 | ~90 | 기본 한국어 |
| KLUE | 한국어 NLU 8종 | 8 | ~88 | ~87 | ~86 | NLU 표준 |
| KorMedMCQA | 의학 지식 | 1 | ~75 | ~78 | ~73 | 의료 한국어 |
| CLIcK | 한국 문화 지식 | 1 | ~65 | ~62 | ~60 | 문화 이해 |
| HAE-RAE | 한국어 종합 | 6 | ~85 | ~84 | ~82 | 종합 한국어 |
| Ko-MMLU | MMLU 한국어 | 45 | ~82 | ~80 | ~78 | MMLU 번역 |
| LogicKor | 한국어 논리 | 5 | ~87 | ~88 | ~85 | 추론 + 한국어 |
| Ko-HellaSwag | 한국어 상식 | 1 | ~88 | ~87 | ~85 | 상식 한국어 |

**S7G-011** | CRITICAL | V1 | KoBEST — 한국어 기본 NLU 평가
- 내용: 한국어 자연어 이해 5가지 작업 평가
- 작업: BoolQ(참거짓), COPA(인과추론), WiC(단어의미), HellaSwag(상식), SentiNeg(감성)
- VAMOS 활용:
  - 한국어 서비스의 최소 품질 기준
  - 모델 선택 시 KoBEST 평균 88+ 필수
  - V1 출시 전 모든 후보 모델 KoBEST 테스트 필수

**S7G-012** | CRITICAL | V1 | KLUE — 한국어 NLU 표준 벤치마크
- 내용: 한국어 언어 이해 8가지 작업 (KAIST)
- 작업: TC(주제분류), STS(문장유사), NLI(자연어추론), NER(개체명), RE(관계추출), DP(의존파싱), MRC(기계독해), DST(대화상태)
- VAMOS 활용:
  - NER: 메모리에서 인물/장소/날짜 자동 추출
  - STS: 시맨틱 검색 품질 평가
  - MRC: RAG 문서 이해 능력
  - 목표: KLUE 평균 85+ (한국어 지원 모델 기준)

**S7G-013** | HIGH | V1 | LogicKor — 한국어 논리 추론 평가
- 내용: 한국어 환경에서의 논리적 추론 능력 평가
- 작업: 수학추론, 논리퍼즐, 작문, 코딩, 이해력
- VAMOS 활용:
  - Research/Quant Node의 한국어 추론 품질 기준
  - 투자 분석 보고서 작성 품질 연관
  - 목표: LogicKor 85+ 모델 우선 사용

**S7G-014** | HIGH | V1 | CLIcK — 한국 문화 지식 평가
- 내용: 한국 문화·역사·사회에 대한 지식 평가
- VAMOS 활용:
  - 한국 사용자 대상 개인 비서로서 필수
  - 한국 공휴일, 문화 관습, 사회 규범 이해
  - 한국식 감정 표현 이해 (STEP7-B 감정 분석과 연계)
  - 목표: CLIcK 60+ (외국 모델의 한국 문화 이해 한계 인식)

**S7G-015** | HIGH | V1 | 한국어 환각 테스트 — 한국어 Hallucination 측정
- 내용: 한국어 답변에서의 환각(거짓 정보) 빈도 측정
- 구현:
  - 한국 팩트체크 데이터셋 기반 (서울대 SNU FactCheck)
  - 한국 인물/지역/사건에 대한 사실 확인
  - 100개 질문 → 정확 응답률 측정
  - 환각 유형 분류: 완전 허위 / 부분 부정확 / 최신성 오류
- 목표: 환각률 <5% (한국어 사실 질문 기준)

**S7G-016** | HIGH | V1 | 한국어 존댓말/비속어 테스트 — 어투 적절성
- 내용: 한국어 응답의 어투 적절성 평가
- 평가 항목:
  - 존댓말 일관성 (설정에 따른 유지)
  - 비속어/불쾌어 미생성
  - 호칭 적절성
  - 한국어 자연스러움 (번역투 최소화)
- 목표: 번역투 탐지율 <10%, 존댓말 일관성 >98%

**S7G-017** | MED | V2 | Ko-MMLU — MMLU 한국어 버전
- 내용: MMLU 벤치마크를 한국어로 번역한 평가
- VAMOS 활용: MMLU 영어 점수와 한국어 점수 갭 분석
- 갭이 큰 모델은 한국어 작업에서 제외 또는 번역 파이프라인 추가

**S7G-018** | MED | V2 | 한국어 생성 품질 — 작문/요약/번역 평가
- 내용: 한국어 텍스트 생성의 전반적 품질 평가
- 평가: 요약 정확성(ROUGE-L), 번역 품질(BLEU/COMET), 작문 자연스러움(인간 평가)

---

## Part 3: 코딩 벤치마크 (8건)

### 코딩 벤치마크 전수비교표

| 벤치마크 | 언어 | 난이도 | GPT-4o | Claude 3.5 Sonnet | DeepSeek V3 | VAMOS Dev Node |
|---------|------|--------|--------|-------------------|-------------|---------------|
| HumanEval | Python | 중 | 90.2 | 92.0 | 89.0 | 목표: 90+ |
| HumanEval+ | Python | 고 | 81.0 | 84.0 | 82.0 | 목표: 82+ |
| MBPP | Python | 쉬움~중 | 86.8 | 90.0 | 88.5 | 목표: 88+ |
| SWE-bench | GitHub Issues | 실전 | 33.2 | 49.0 | 42.0 | 목표: 40+ |
| BFCL | 함수 호출 | 중~고 | 88.5 | 90.5 | 86.0 | 핵심 지표 |
| MultiPL-E | 다국어 | 중 | 다양 | 다양 | 다양 | JS, Python, Rust |
| Aider Polyglot | 실전 코딩 | 고 | 70.0 | 72.8 | 68.0 | 목표: 70+ |
| CodeContests | 경시대회 | 최고 | 43.0 | 48.0 | 52.0 | 참조용 |

**S7G-019** | HIGH | V1 | HumanEval / HumanEval+ — Python 코드 생성
- 내용: 함수 docstring으로부터 Python 코드 생성 및 테스트 통과율
- VAMOS 활용:
  - Dev Node 모델 선택 1차 기준
  - HumanEval+ (엣지 케이스 강화) 필수 테스트
  - pass@1 기준 85+ 모델만 코딩 작업에 배정

**S7G-020** | HIGH | V1 | SWE-bench (Verified) — 실전 소프트웨어 엔지니어링
- 내용: 실제 GitHub 이슈를 해결하는 능력 평가 (가장 현실적)
- VAMOS 활용:
  - Agent 기반 코딩 능력의 핵심 지표
  - Claude 3.5 Sonnet이 49%로 1위 → VAMOS Dev Node 핵심 모델
  - SWE-bench Lite (300문제)로 빠른 테스트
  - 목표: VAMOS Agent가 SWE-bench 40%+ 달성

**S7G-021** | HIGH | V1 | BFCL — Berkeley Function Calling Leaderboard
- 내용: LLM의 함수/Tool 호출 정확도 평가 (VAMOS 핵심)
- 카테고리:
  - Simple Function: 단일 함수 호출
  - Multiple Function: 복수 함수 선택
  - Parallel Function: 병렬 함수 호출
  - Relevance Detection: 관련 함수 없을 때 거부
  - AST Summary: 구조 정확도
- VAMOS 활용:
  - MCP Tool 호출 정확도 직결
  - 모델 선택 시 BFCL 88+ 필수
  - VAMOS 커스텀 Tool 호출 테스트 추가 (30건)

**S7G-022** | HIGH | V1 | Aider Polyglot — 실전 코드 편집 평가
- 내용: 기존 코드베이스에서 코드 편집 능력 평가 (Aider)
- 측정: Python, JavaScript, TypeScript, Rust 등 다국어 코드 수정
- VAMOS 활용:
  - Dev Node의 실전 코드 편집 능력 평가
  - 단순 생성이 아닌 "기존 코드 수정" 능력 → Agent 핵심 역량
  - 목표: 전체 편집 성공률 70+

**S7G-023** | HIGH | V1 | MultiPL-E — 다언어 코딩 평가
- 내용: Python 외 JavaScript, TypeScript, Rust 등 다양한 언어 코딩 능력
- VAMOS 활용:
  - VAMOS 핵심 언어: TypeScript (프론트엔드), Rust (Tauri), Python (Agent)
  - 언어별 모델 라우팅 최적화
  - Python 강한 모델 / JS 강한 모델 분리 가능

**S7G-024** | MED | V2 | 코드 보안 평가 — CWE/SAST 기반
- 내용: LLM이 생성한 코드의 보안 취약점 평가
- 측정:
  - CWE Top 25 취약점 생성 빈도
  - SQL Injection, XSS, Buffer Overflow 등
  - Semgrep/CodeQL로 자동 스캔
- 목표: 보안 취약 코드 생성률 <2%

**S7G-025** | MED | V2 | 코드 리뷰 품질 — PR 리뷰 정확도
- 내용: LLM의 코드 리뷰 제안 품질 평가
- 측정: 버그 발견률, 제안 정확성, false positive 비율
- VAMOS 활용: Dev Node의 코드 리뷰 기능 품질 기준

**S7G-026** | MED | V2 | 디버깅 능력 — 버그 찾기·고치기 평가
- 내용: 주어진 버그 코드에서 버그를 찾고 수정하는 능력
- 측정: 버그 식별률, 수정 정확률, 설명 품질
- 데이터셋: BugsInPy, Defects4J (Java)

---

## Part 4: Agent / Tool Use 벤치마크 (8건)

### Agent 벤치마크 전수비교표

| 벤치마크 | 유형 | 측정 대상 | Claude | GPT | Gemini | VAMOS 관련도 |
|---------|------|----------|--------|-----|--------|-------------|
| BFCL v3 | Tool Use | 함수 호출 정확도 | 90.5 | 88.5 | 86.0 | ★★★★★ |
| τ-bench | Agent | 대화형 Tool 사용 | — | — | — | ★★★★★ |
| AgentBench | Agent | 8종 환경 Agent 능력 | 높음 | 높음 | 보통 | ★★★★☆ |
| ToolBench | Tool | 16K API 활용 | 보통 | 높음 | 보통 | ★★★★☆ |
| WebArena | Web Agent | 웹 탐색 작업 | — | 보통 | — | ★★★☆☆ |
| OSWorld | OS Agent | OS 조작 작업 | — | — | — | ★★★☆☆ |
| GAIA | General | 범용 Agent 능력 | 높음 | 높음 | 보통 | ★★★★☆ |
| MLE-bench | ML Agent | ML 파이프라인 | — | 보통 | — | ★★★☆☆ |

**S7G-027** | CRITICAL | V1 | BFCL v3 — Tool/Function Calling 평가
- 내용: VAMOS의 MCP Tool 호출 정확도를 직접 평가하는 핵심 벤치마크
- 평가 항목:
  - 단일 Tool 호출 정확도
  - 복수 Tool 선택 정확도
  - 병렬 Tool 호출
  - Tool 불필요 시 거부
  - 복합 시나리오 (순차 + 병렬)
- VAMOS 커스텀 확장:
  ```
  BFCL + VAMOS Custom Tests (30건):
  1. MCP Tool 호출 (10건): 파일 읽기, 검색, 코드 실행
  2. 3-Gate 판단 (10건): Policy/Cost/Evidence 게이트 통과
  3. Multi-Agent 위임 (10건): 적절한 Agent 선택
  ```

**S7G-028** | CRITICAL | V1 | τ-bench (Tau-bench) — 대화형 Agent 평가
- 내용: 실제 대화 속에서 Tool을 적절히 사용하는 능력 평가
- 시나리오: 항공사 예약, 쇼핑 주문 등 실제 비즈니스 프로세스
- VAMOS 활용:
  - ORANGE CORE의 대화형 작업 수행 능력 핵심 지표
  - 사용자 의도 파악 → 적절한 Tool 선택 → 실행 → 결과 통합
  - 커스텀 시나리오: 투자 분석 요청, 문서 작성 지시, 일정 관리

**S7G-029** | HIGH | V1 | GAIA — General AI Assistants 벤치마크
- 내용: 범용 AI 비서의 종합적 능력 평가
- 레벨:
  - Level 1: 단순 도구 사용 (계산기, 검색)
  - Level 2: 다단계 추론 + 도구 활용
  - Level 3: 복합 문제 해결 (여러 도구 + 긴 추론)
- VAMOS 활용: VAMOS의 전반적 비서 능력 평가, 분기별 테스트

**S7G-030** | HIGH | V1 | AgentBench — 다환경 Agent 종합 평가
- 내용: 8가지 환경에서 Agent 능력 평가
- 환경: OS 조작, DB 쿼리, 지식 그래프, 웹 탐색, 게임, 코딩, 웹쇼핑, 가정환경
- VAMOS 활용:
  - 특히 OS 조작, DB 쿼리, 지식 그래프 결과 중요
  - Dev Node: 코딩 환경 점수
  - Research Node: 지식 그래프, 웹 탐색 점수

**S7G-031** | HIGH | V2 | ToolBench — 대규모 API 활용 평가
- 내용: 16,000+ API를 활용하는 능력 평가
- VAMOS 활용:
  - MCP Tool 확장 시 새 Tool 활용 능력 평가
  - Zero-shot Tool 학습: 처음 보는 Tool을 얼마나 잘 사용하는지
  - API 설명(description)만으로 정확한 파라미터 추론

**S7G-032** | HIGH | V2 | WebArena / VisualWebArena — 웹 자동화 평가
- 내용: 웹 브라우저를 통한 작업 수행 능력 평가
- VAMOS 활용:
  - Computer Use / GUI Agent 기능 (STEP7 Part L) 품질 평가
  - 웹 리서치 자동화 품질 측정
  - V3: 웹 기반 작업 자동화 기능의 핵심 벤치마크

**S7G-033** | MED | V2 | OSWorld — OS 조작 Agent 평가
- 내용: 운영체제 수준 작업 (파일 관리, 앱 설치, 설정 변경 등) 수행 능력
- VAMOS 활용: V3 데스크톱 자동화 기능 평가

**S7G-034** | MED | V2 | MLE-bench — ML 엔지니어링 Agent 평가
- 내용: Kaggle 대회 수준의 ML 파이프라인 구축 능력
- VAMOS 활용: Quant Node의 ML 모델 구축 능력 기준

---

## Part 5: RAG 품질 평가 (10건)

### RAG 평가 프레임워크

```
RAG Evaluation Dimensions:
┌──────────────────────────────────────────────────────┐
│  1. Retrieval Quality (검색 품질)                     │
│     ├── Precision: 검색된 문서 중 관련 비율          │
│     ├── Recall: 전체 관련 문서 중 검색된 비율        │
│     ├── MRR: 첫 관련 문서의 순위                     │
│     └── NDCG: 순위 가중 관련성 점수                  │
│                                                       │
│  2. Generation Quality (생성 품질)                    │
│     ├── Faithfulness: 검색 문서에 충실한 답변        │
│     ├── Answer Relevancy: 질문에 관련된 답변         │
│     ├── Context Precision: 컨텍스트 활용 정확도      │
│     └── Context Recall: 필요 컨텍스트 포함률         │
│                                                       │
│  3. End-to-End Quality (종합 품질)                    │
│     ├── Correctness: 최종 답변 정확성                │
│     ├── Completeness: 답변 완전성                    │
│     ├── Harmfulness: 유해 답변 여부                   │
│     └── Latency: 응답 시간                           │
└──────────────────────────────────────────────────────┘
```

**S7G-035** | CRITICAL | V1 | RAGAS 프레임워크 — RAG 자동 평가
- 내용: RAGAS(Retrieval Augmented Generation Assessment) 프레임워크로 RAG 품질 자동 평가
- 평가 지표:
  ```python
  from ragas import evaluate
  from ragas.metrics import (
      faithfulness,        # 검색 문서에 충실한가
      answer_relevancy,    # 질문에 관련된 답변인가
      context_precision,   # 관련 컨텍스트가 상위에 있는가
      context_recall,      # 필요한 모든 컨텍스트를 검색했는가
  )

  result = evaluate(
      dataset=eval_dataset,
      metrics=[faithfulness, answer_relevancy, context_precision, context_recall]
  )
  ```
- 비용: RAGAS 무료 오픈소스
- 목표: Faithfulness 0.9+, Answer Relevancy 0.85+, Context Precision 0.8+

**S7G-036** | CRITICAL | V1 | 검색 정확도 평가 — Retrieval Metrics
- 내용: 벡터 검색 + 키워드 검색 + 그래프 검색의 정확도 개별 및 종합 평가
- 구현:
  ```
  평가 데이터셋:
  - VAMOS 커스텀: 100개 질문-정답 문서 쌍
  - 카테고리: 사실 질문(30), 분석 질문(30), 개인 정보(20), 코딩(20)

  측정 지표:
  - Precision@K (K=1,3,5,10)
  - Recall@K
  - MRR (Mean Reciprocal Rank)
  - NDCG@10

  검색 방식별 비교:
  1. 벡터 검색만 (Chroma/Qdrant)
  2. 키워드 검색만 (BM25)
  3. 그래프 검색만 (NetworkX/Neo4j)
  4. 하이브리드 (1+2 Reciprocal Rank Fusion)
  5. 4-Index Fusion (1+2+3+메모리)
  ```
- 목표: 4-Index Fusion이 단일 방식 대비 15%+ 개선

**S7G-037** | HIGH | V1 | Faithfulness 테스트 — 환각 방지 평가
- 내용: RAG 응답이 검색된 문서에 근거한 답변인지 평가
- 구현:
  - RAGAS faithfulness 점수
  - 인용 정확성: 인용한 출처와 답변 내용 일치 여부
  - 없는 정보 생성 탐지: 문서에 없는 내용을 생성했는지
- 목표: Faithfulness 0.90+ (V1), 0.95+ (V2)

**S7G-038** | HIGH | V1 | Chunking 품질 평가 — 문서 분할 최적화
- 내용: 문서 분할(chunking) 전략별 RAG 품질 비교
- 비교:
  | 전략 | Chunk Size | Overlap | 장점 | 단점 |
  |------|-----------|---------|------|------|
  | Fixed (512) | 512 tok | 50 | 간단 | 의미 절단 |
  | Fixed (1024) | 1024 tok | 100 | 더 많은 컨텍스트 | 검색 정밀도↓ |
  | Semantic | 가변 | 자동 | 의미 보존 | 느림 |
  | Recursive | 가변 | 설정 | 구조 보존 | 복잡 |
  | Document | 문서 단위 | 없음 | 전체 맥락 | 긴 컨텍스트 필요 |
- VAMOS 추천: Semantic Chunking + Contextual Retrieval (Anthropic 방식)

**S7G-039** | HIGH | V1 | Embedding 모델 비교 평가 — 한국어 특화
- 내용: 임베딩 모델별 한국어 검색 정확도 비교
- 비교:
  | 모델 | 차원 | 한국어 성능 | 비용 | 속도 | VAMOS 선택 |
  |------|------|-----------|------|------|-----------|
  | BGE-M3 | 1024 | ★★★★★ | 무료(로컬) | 보통 | ✅ V1 |
  | multilingual-e5-large | 1024 | ★★★★☆ | 무료(로컬) | 보통 | 대안 |
  | text-embedding-3-small | 1536 | ★★★★☆ | $0.02/1M | 빠름 | V2 |
  | Jina-embeddings-v3 | 1024 | ★★★★☆ | 무료/API | 빠름 | 대안 |
  | Cohere embed-v3 | 1024 | ★★★★☆ | $0.10/1M | 빠름 | 대안 |
  | Nomic-embed | 768 | ★★★☆☆ | 무료 | 매우빠름 | 경량용 |
- 평가: MTEB 한국어 서브셋 + VAMOS 커스텀 한국어 검색 테스트

**S7G-040** | HIGH | V1 | 컨텍스트 윈도우 활용 평가 — Long Context
- 내용: 긴 컨텍스트 윈도우에서의 정보 검색 능력 평가
- 테스트:
  - Needle-in-a-Haystack: 긴 문서에서 특정 정보 찾기
  - Multi-Needle: 여러 정보를 동시에 찾기
  - 위치별 정확도: 시작/중간/끝 위치에 따른 정확도 변화
- Claude 200K / GPT 128K / Gemini 2M 비교
- VAMOS 활용: RAG vs Long Context 전략 결정의 기준

**S7G-041** | HIGH | V2 | RAG vs Long Context — 전략 비교 테스트
- 내용: 동일 질문에 대해 RAG 방식 vs 전체 문서 직접 입력 비교
- 측정: 정확도, 비용, 속도 3축 비교
- 결론: 문서 크기별 최적 전략 결정 규칙 도출

**S7G-042** | MED | V2 | Self-RAG / CRAG 품질 평가 — 고급 RAG 패턴
- 내용: Self-RAG (자기 성찰 RAG), CRAG (Corrective RAG)의 품질 개선 효과 측정
- 비교: 기본 RAG vs Self-RAG vs CRAG vs RAPTOR
- 목표: 기본 RAG 대비 정확도 10%+ 개선

**S7G-043** | MED | V2 | 다국어 RAG 평가 — 한국어/영어 혼합 검색
- 내용: 한국어 질문으로 영어 문서 검색, 또는 그 반대의 정확도 평가
- BGE-M3의 다국어 성능이 핵심

**S7G-044** | MED | V2 | Knowledge Graph RAG 평가 — 그래프 기반 검색 품질
- 내용: Knowledge Graph 검색이 벡터 검색 대비 얼마나 개선하는지 평가
- 테스트: 관계 추론 질문 (예: "X와 Y의 관계는?")에서 KG 검색의 정확도 이점

---

## Part 6: 안전성 벤치마크 (8건)

**S7G-045** | CRITICAL | V1 | TruthfulQA — 진실성 평가
- 내용: LLM이 일반적 오해에 빠지지 않고 진실된 답변을 하는지 평가
- VAMOS 활용:
  - 전체 모델의 진실성 최소 기준
  - "모르겠습니다" 응답 허용 → 거짓보다 나음
  - 목표: TruthfulQA MC1 55+

**S7G-046** | CRITICAL | V1 | Prompt Injection 저항성 — 보안 테스트 스위트
- 내용: Prompt Injection 공격에 대한 저항성 정량 평가
- 구현:
  ```
  테스트 스위트 (100건):
  - Direct Injection: 20건 (system prompt 무시 지시)
  - Indirect Injection: 20건 (외부 문서 내 숨긴 지시)
  - Prompt Leaking: 20건 (시스템 프롬프트 추출 시도)
  - Jailbreak: 20건 (가드레일 우회 시도)
  - Multi-turn: 20건 (점진적 공격)

  평가:
  - 방어 성공률 목표: 95%+ (V1), 99%+ (V2)
  - False Positive: 정상 요청 거부율 <2%
  ```
- 도구: garak (무료), PyRIT (Microsoft, 무료)

**S7G-047** | HIGH | V1 | ToxiGen — 유해 콘텐츠 생성 평가
- 내용: LLM이 유해한 콘텐츠를 생성하는 빈도 평가
- 목표: 유해 콘텐츠 생성률 <0.5%

**S7G-048** | HIGH | V1 | BBQ (Bias Benchmark) — 편향 평가
- 내용: 사회적 편향 (성별, 인종, 나이, 종교 등) 평가
- VAMOS 활용: 편향 점수가 높은 모델의 민감 주제 라우팅 제한

**S7G-049** | HIGH | V1 | AdvBench — 적대적 공격 저항성
- 내용: 유해 요청에 대한 거부 능력 평가
- 목표: 유해 요청 거부율 99%+

**S7G-050** | HIGH | V2 | 한국어 안전성 테스트 — 한국 맥락 안전성
- 내용: 한국어 환경 특화 안전성 평가
- 테스트:
  - 한국 법률 위반 콘텐츠 생성 거부
  - 한국 사회 민감 주제 (정치, 남북, 역사) 균형 잡힌 응답
  - 한국 혐오 표현 탐지
  - 투자 관련 불법 조언 방지 (자본시장법)

**S7G-051** | MED | V2 | AI Deception 테스트 — 기만 행동 탐지
- 내용: AI가 사용자를 의도적으로 속이는 행동 탐지
- 시나리오: 에러 숨김, 능력 과장, 확신 없는 단정, 출처 날조

**S7G-052** | MED | V2 | 긴급 상황 대응 — 자해/위기 상황 대응 품질
- 내용: 사용자가 위기 상황(자해 암시 등)을 표현했을 때 적절한 대응 평가
- 목표: 적절한 위기 자원(상담전화 등) 안내 + 공감적 응답

---

## Part 7: 사용자 경험(UX) 평가 (8건)

**S7G-053** | HIGH | V1 | 작업 완수율 — Task Completion Rate
- 내용: 사용자가 요청한 작업을 성공적으로 완수하는 비율
- 측정:
  - 단순 질문 답변: 목표 95%
  - 코딩 작업: 목표 85%
  - 분석 작업: 목표 80%
  - Agent 복합 작업: 목표 70%
- 실패 분석: 실패 원인 분류 (모델 한계, 도구 오류, 이해 오류, 비용 제한)

**S7G-054** | HIGH | V1 | 응답 시간 체감 — Perceived Latency
- 내용: 사용자가 체감하는 응답 속도 만족도
- 측정:
  - TTFT (Time To First Token): 목표 <1s
  - 전체 응답 시간: 작업 유형별 SLO 기준
  - 스트리밍 유무에 따른 체감 차이
  - 진행 상태 표시의 효과

**S7G-055** | HIGH | V1 | 사용자 만족도 — User Satisfaction Score
- 내용: 응답별 사용자 만족도 수집 및 분석
- 구현:
  - 👍/👎 간편 평가 (모든 응답)
  - 1-5점 상세 평가 (선택적)
  - NPS (Net Promoter Score): 분기별 서베이
  - 차원별 만족도: 정확성, 유용성, 속도, 안전성, 비용 대비

**S7G-056** | HIGH | V1 | 대화 효율성 — Conversation Efficiency
- 내용: 원하는 결과에 도달하기까지의 대화 턴 수
- 측정:
  - 평균 턴 수 (작업 유형별)
  - 명확화 질문 빈도 (적을수록 의도 파악 우수)
  - 재시도 요청 빈도 (적을수록 품질 우수)
- 목표: 경쟁 AI 대비 평균 턴 수 20% 감소

**S7G-057** | MED | V1 | 온보딩 효과 — First-Time User Experience
- 내용: 최초 사용자의 온보딩 경험 평가
- 측정: 설정 완료율, 설정 소요 시간, 첫 대화 성공률, 7일 리텐션

**S7G-058** | MED | V2 | 개인화 효과 — Personalization Impact
- 내용: 메모리/KG 기반 개인화가 응답 품질에 미치는 영향 측정
- A/B 테스트: 개인화 ON vs OFF → 만족도/정확도/효율성 비교

**S7G-059** | MED | V2 | 접근성 평가 — WCAG 준수
- 내용: 웹 접근성 가이드라인 준수 평가
- 기준: WCAG 2.1 AA 수준, 키보드 네비게이션, 스크린리더 호환

**S7G-060** | MED | V2 | 다국어 UX — 한국어/영어 전환 경험
- 내용: 한국어-영어 혼합 사용 시 UX 품질 평가
- 측정: 언어 전환 정확도, 혼합 입력 처리, 번역 품질

---

## Part 8: VAMOS 고유 벤치마크 (10건)

### VAMOS Custom Benchmark Suite

```
┌──────────────────────────────────────────────────────┐
│           VAMOS Custom Benchmark Suite (VBS)          │
├──────────────────────────────────────────────────────┤
│                                                       │
│  VBS-1: 3-Gate Accuracy          (3-Gate 정확도)     │
│  VBS-2: Model Routing Efficiency (모델 라우팅 효율)  │
│  VBS-3: Memory Recall Quality    (메모리 회상 품질)  │
│  VBS-4: KG Navigation Quality    (KG 탐색 품질)     │
│  VBS-5: Self-Evolution Score     (자기진화 점수)     │
│  VBS-6: Cost Efficiency Ratio    (비용 효율 비율)    │
│  VBS-7: Constitution Compliance  (헌법 준수율)       │
│  VBS-8: Agent Collaboration      (Agent 협업 품질)   │
│  VBS-9: Personal Assistant Score (비서 종합 점수)    │
│  VBS-10: Investment Analysis     (투자 분석 품질)    │
│                                                       │
│  실행 주기: VBS-1~7 (주간), VBS-8~10 (월간)         │
│  목표: 각 지표 80+ (100점 만점)                      │
└──────────────────────────────────────────────────────┘
```

**S7G-061** | CRITICAL | V1 | VBS-1: 3-Gate 정확도 — Gate 판단 품질
- 내용: 3-Gate System (Policy/Cost/Evidence)의 판단 정확도 측정
- 테스트:
  ```
  테스트 케이스 (60건):
  - Policy Gate (20건):
    ✅ 통과해야 할 안전한 요청 10건
    ❌ 차단해야 할 위험한 요청 10건
  - Cost Gate (20건):
    ✅ 예산 내 요청 10건
    ❌ 예산 초과 요청 10건
  - Evidence Gate (20건):
    ✅ 충분한 근거가 있는 응답 10건
    ❌ 근거 부족한 응답 10건

  점수 = (정확 판단 수 / 60) × 100
  목표: 85/100 (V1), 95/100 (V2)
  ```

**S7G-062** | CRITICAL | V1 | VBS-2: 모델 라우팅 효율 — 최적 모델 선택
- 내용: 작업에 대해 최적 모델을 선택하는 정확도와 비용 효율
- 테스트:
  ```
  테스트 (50건, 각 카테고리 10건):
  1. 간단한 질문 → 로컬 Ollama가 최적
  2. 코딩 작업 → Claude Sonnet이 최적
  3. 빠른 분류 → GPT-4o-mini가 최적
  4. 검색 필요 → Gemini+Search가 최적
  5. 깊은 추론 → Claude Opus가 최적

  점수:
  - 모델 선택 정확도 (정답률)
  - 비용 효율 (실제 비용 / 최적 비용)
  - 목표: 선택 정확도 80%, 비용 효율 1.2x 이하
  ```

**S7G-063** | CRITICAL | V1 | VBS-3: 메모리 회상 품질 — 개인화 메모리
- 내용: 사용자 과거 정보를 정확히 기억하고 활용하는 능력
- 테스트:
  ```
  테스트 (30건):
  - 사실 기억 (10건): "내 이름/생일/직업 뭐야?"
  - 선호 기억 (10건): "내가 좋아하는 음식/코딩 스타일?"
  - 맥락 기억 (10건): "어제 논의했던 프로젝트 진행 상황?"

  점수:
  - 정확 회상률 (정확/전체)
  - 선택적 망각: 삭제 요청한 정보 미회상 확인
  - 목표: 회상 정확도 90%, 망각 정확도 100%
  ```

**S7G-064** | HIGH | V1 | VBS-6: 비용 효율 비율 — Cost Efficiency Ratio
- 내용: 동일 품질 대비 VAMOS가 얼마나 비용 효율적인지 측정
- 계산:
  ```
  CER = (VAMOS 품질 점수 / VAMOS 비용) / (ChatGPT 품질 점수 / ChatGPT 비용)

  예시:
  VAMOS: 품질 85점, 월 $8 → 10.6점/$
  ChatGPT Plus: 품질 90점, 월 $20 → 4.5점/$
  CER = 10.6 / 4.5 = 2.36x (VAMOS가 2.36배 비용 효율적)
  ```
- 목표: CER ≥ 2.0x (ChatGPT Plus 대비)

**S7G-065** | HIGH | V1 | VBS-7: Constitution 준수율 — 개인 헌법 이행
- 내용: Personal Constitution에 정의된 규칙을 얼마나 잘 따르는지 측정
- 테스트:
  - 톤/어투 규칙 준수 (20건)
  - 경계(boundary) 규칙 준수 (20건)
  - 우선순위 규칙 준수 (10건)
- 목표: 95%+ 준수율

**S7G-066** | HIGH | V1 | VBS-4: KG 탐색 품질 — Knowledge Graph 활용
- 내용: Knowledge Graph의 관계 탐색이 답변 품질에 기여하는 정도
- 테스트: 관계 추론 질문 (20건) — KG 있을 때 vs 없을 때 정확도 비교
- 목표: KG 사용 시 관계 질문 정확도 20%+ 향상

**S7G-067** | HIGH | V2 | VBS-5: 자기진화 점수 — Self-Evolution
- 내용: 시간이 지남에 따라 VAMOS의 성능이 개선되는 정도 측정
- 측정:
  - 주간: 동일 테스트셋 반복 → 점수 추이
  - 학습 곡선: 사용 1주/1개월/3개월 후 성능 비교
  - 개인화 효과: 사용 기간에 따른 만족도 변화

**S7G-068** | HIGH | V2 | VBS-8: Agent 협업 품질 — Multi-Agent 성능
- 내용: 여러 BLUE NODE Agent가 협업하는 작업의 품질 평가
- 테스트:
  - 리서치 → 코딩: Research Node 결과를 Dev Node가 활용
  - 분석 → 리포트: Quant Node 분석 → Content Node 리포트
  - 복합 작업: 3개+ Agent 순차/병렬 협업
- 목표: 단일 Agent 대비 복합 작업 품질 30%+ 향상

**S7G-069** | MED | V2 | VBS-9: 개인 비서 종합 점수
- 내용: 일상적 비서 작업의 종합 수행 능력 평가
- 작업: 일정 관리, 이메일 초안, 요약, 번역, 리마인더, 추천
- 목표: Google Assistant/Siri 수준 이상의 종합 비서 품질

**S7G-070** | MED | V2 | VBS-10: 투자 분석 품질 — AI Investing
- 내용: 투자 관련 분석의 품질 평가 (STEP7-I 연계)
- 테스트:
  - 기업 분석 리포트 품질 (10건)
  - 시장 트렌드 분석 정확도 (10건)
  - 포트폴리오 분석 합리성 (10건)
  - 리스크 경고 적절성 (10건)
- 주의: 실제 수익률 예측이 아닌, 분석의 논리적 품질 평가

---

## Part 9: 자동 평가 파이프라인 (8건)

**S7G-071** | HIGH | V1 | LLM-as-Judge — LLM 자동 평가기
- 내용: GPT-4o를 Judge로 활용하여 응답 품질 자동 평가
- 구현:
  ```python
  judge_prompt = """
  다음 질문과 답변을 평가해주세요.

  질문: {question}
  답변: {answer}

  평가 기준:
  1. 정확성 (1-5)
  2. 유용성 (1-5)
  3. 완전성 (1-5)
  4. 안전성 (1-5)
  5. 한국어 자연스러움 (1-5)

  JSON 형식으로 점수와 이유를 제공하세요.
  """
  ```
- 비용: GPT-4o-mini Judge → 요청당 ~$0.001
- 주의: Judge 편향 존재 (자기 모델 선호), 다중 Judge로 완화

**S7G-072** | HIGH | V1 | promptfoo 통합 — 프롬프트 자동 테스트
- 내용: 프롬프트 변경 시 자동 회귀 테스트
- 구현: STEP7-F S7F-070 상세 참조
- CI/CD 통합: PR마다 promptfoo 자동 실행, 품질 저하 시 머지 차단

**S7G-073** | HIGH | V1 | 회귀 테스트 자동화 — 품질 저하 방지
- 내용: 시스템 변경 시 기존 품질이 저하되지 않는지 자동 검증
- 구현:
  ```
  Regression Test Suite:
  - Core 응답 품질: 50건 고정 테스트 세트
  - Tool 호출 정확도: 30건 고정 테스트 세트
  - 안전성: 20건 고정 테스트 세트
  - 한국어: 20건 고정 테스트 세트

  실행: 주간 자동 + PR마다 Core 50건
  임계값: 이전 대비 3% 이상 하락 시 알림
  ```

**S7G-074** | HIGH | V1 | 자동 벤치마크 스케줄러 — 정기 평가 실행
- 내용: 벤치마크를 정기적으로 자동 실행하는 스케줄러
- 스케줄:
  | 빈도 | 벤치마크 | 비용 |
  |------|---------|------|
  | 일간 | VBS Core (1-3,6-7) | ~$0.50 |
  | 주간 | VBS 전체 + 안전성 | ~$2.00 |
  | 월간 | 전체 표준 벤치마크 | ~$10.00 |
  | 분기 | 전체 + 인간 평가 | ~$50.00 |

**S7G-075** | HIGH | V2 | 평가 대시보드 — 벤치마크 결과 시각화
- 내용: 모든 벤치마크 결과를 대시보드로 시각화
- 패널:
  - 종합 점수 추이 (시간축 그래프)
  - 카테고리별 레이더 차트
  - 모델별 비교 바 차트
  - 비용 효율 산점도
  - 회귀 테스트 합격/불합격 이력

**S7G-076** | MED | V2 | 자동 리포트 생성 — 평가 보고서
- 내용: 벤치마크 결과를 마크다운 리포트로 자동 생성
- 포함: 점수 요약, 추이 분석, 개선 권고, 모델 교체 제안

**S7G-077** | MED | V2 | 경쟁사 추적 — 경쟁 AI 성능 모니터링
- 내용: ChatGPT, Claude, Gemini 등 경쟁 서비스 성능 변화 추적
- 구현: Chatbot Arena, LMSYS, 공식 벤치마크 모니터링 (RSS/API)

**S7G-078** | MED | V2 | 평가 데이터셋 관리 — 골든 데이터셋
- 내용: VAMOS 평가용 골든 데이터셋 구축 및 관리
- 구성: 질문-정답 쌍 500건 (카테고리별), 정기 갱신, 버전 관리

---

## Part 10: 인간 평가 프로세스 (6건)

**S7G-079** | HIGH | V1 | 자기 평가 — 개발자 정기 품질 체크
- 내용: 개발자가 직접 VAMOS를 사용하며 품질 평가
- 주기: 주 1회, 30분 체크리스트 기반
- 체크: 대화 품질, 도구 사용, 속도, 안전성, 개인화 효과

**S7G-080** | HIGH | V2 | 베타 테스터 피드백 — 외부 사용자 평가
- 내용: 선정된 베타 테스터의 실사용 피드백 수집
- 규모: V2 출시 전 10-20명 베타 테스트
- 방법: 2주 사용 → 설문 + 인터뷰 + 로그 분석

**S7G-081** | HIGH | V2 | A/B 인간 비교 — VAMOS vs 경쟁 AI
- 내용: 동일 질문에 대한 VAMOS vs ChatGPT/Claude 응답 비교 평가
- 방법: 블라인드 비교 (어떤 AI인지 모르는 상태)
- 규모: 100건 비교, 5명 평가자

**S7G-082** | MED | V2 | 시나리오 기반 테스트 — 실제 사용 시나리오
- 내용: 실제 사용 시나리오 기반 종합 테스트
- 시나리오: 일일 업무 비서, 코딩 프로젝트 지원, 투자 분석, 학습 도우미

**S7G-083** | MED | V2 | 전문가 리뷰 — 도메인 전문가 평가
- 내용: 투자/코딩/보안 등 도메인 전문가의 품질 평가
- 평가: 전문 분야 답변의 정확성과 깊이

**S7G-084** | MED | V3 | 장기 사용성 연구 — Longitudinal Study
- 내용: 3-6개월 장기 사용에서의 품질 변화 추적
- 측정: 개인화 효과, 자기진화, 사용자 만족도 추이

---

## Part 11: 품질 보증 프로세스 (4건)

**S7G-085** | HIGH | V1 | QA 체크리스트 — 릴리즈 전 품질 게이트
- 내용: 모든 릴리즈 전 통과해야 할 품질 체크리스트
- 체크리스트:
  ```
  Release Quality Gate:
  □ Unit Test Coverage ≥80%
  □ Integration Test Pass
  □ E2E Core Flow Pass
  □ VBS Core Score ≥80
  □ Prompt Regression Test Pass
  □ Security Test (Injection) Pass
  □ 한국어 품질 테스트 Pass
  □ Performance SLO 달성
  □ 비용 예산 내 확인
  □ 접근성 기본 테스트 Pass
  ```

**S7G-086** | HIGH | V1 | 버그 트래킹 — 이슈 관리 프로세스
- 내용: 버그 발견·보고·수정·검증 프로세스
- 도구: GitHub Issues + Labels (bug/enhancement/security)
- 프로세스: 발견 → 재현 → 원인 분석 → 수정 → 테스트 → 릴리즈

**S7G-087** | MED | V2 | 품질 지표 (KPI) — 핵심 품질 목표
- KPI:
  | 지표 | V1 목표 | V2 목표 |
  |------|---------|---------|
  | 작업 완수율 | 80% | 90% |
  | 사용자 만족도 | 4.0/5 | 4.3/5 |
  | 환각률 | <8% | <3% |
  | Injection 방어율 | 95% | 99% |
  | 비용 효율 (CER) | 2.0x | 2.5x |
  | 한국어 자연스러움 | 85% | 92% |

**S7G-088** | MED | V2 | 지속적 개선 — Continuous Improvement
- 내용: 품질 데이터 기반 지속적 개선 사이클
- 사이클: 측정 → 분석 → 개선 → 검증 → 배포 (월간 반복)

---

## 구현 우선순위 로드맵

### V1 (MVP) — 필수 구현: 38건
- 표준 벤치마크: S7G-001~006 (6건)
- 한국어: S7G-011~016 (6건)
- 코딩: S7G-019~023 (5건)
- Agent: S7G-027~030 (4건)
- RAG: S7G-035~040 (6건)
- 안전성: S7G-045~049 (5건)
- UX: S7G-053~056 (4건)
- VAMOS 고유: S7G-061~066 (6건)
- 자동 파이프라인: S7G-071~074 (4건)
- QA: S7G-079, 085, 086 (3건)

### V2 (Server) — 확장 구현: 40건
- 나머지 전체 항목

### V3 (Enterprise) — 고급 구현: 10건
- 장기 사용성 연구, 전문가 리뷰 확대 등

---

> **다음 단계**: STEP7-H (비즈니스 모델/시장 전략)로 이동
