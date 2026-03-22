---
session: 19
sections: [22]
status: complete
---

# §22. Agent Teams — 멀티 에이전트 아키텍처

> **비유**: 대형 프로젝트를 혼자서 하면 시간이 너무 오래 걸립니다. 그래서 팀을 꾸립니다 — **팀장 1명 + 전문가 여러 명**. 팀장은 전체 계획을 세우고 일을 나눠주며, 각 전문가는 자기 분야의 일을 수행합니다. VAMOS의 Agent Teams도 정확히 이 방식입니다.

[근거: VAMOS_AGENT_TEAMS_SPEC §1]

---

## §22.1 왜 여러 에이전트가 필요한가?

### 비유: 프로젝트 팀

회사에서 "NVIDIA 종합 투자 분석 리포트"를 만들라는 요청이 들어왔다고 상상해보세요.

- 한 사람이 모든 걸 다 하려면? → 뉴스 검색, 재무 분석, 차트 분석, 리포트 작성을 순서대로 해야 해서 시간이 매우 오래 걸림
- 팀으로 하면? → 리서치 담당, 데이터 분석 담당, 글쓰기 담당이 **동시에** 작업 → 훨씬 빠르고 전문적

VAMOS Agent Teams는 이런 "팀 협업" 구조를 AI 에이전트로 구현한 것입니다.

### 멀티 에이전트 vs 싱글 에이전트 — 언제 뭘 써야 할까?

| 판단 기준 | 멀티 에이전트 적합 | 싱글 에이전트 적합 |
|-----------|-------------------|-------------------|
| 맥락 연속성 (Context) | 낮음 (독립적 작업) | 높음 (연속 추론 필요) |
| 대표 예시 | 여행 계획 (항공+호텔+일정 병렬) | 소설 집필 (일관된 맥락 유지) |
| 정보 공유 | 결과만 공유하면 충분 | 중간 과정 전체 공유 필요 |
| VAMOS 적용 | BLUE NODE 병렬 실행 | ORANGE CORE 단일 체인 |

[근거: D2.0-05 §5 멀티 에이전트 vs 싱글 에이전트 판단 기준]

### 핵심 요약 (3줄)
1. 복잡한 작업은 여러 전문 에이전트가 나눠서 처리하면 빠르고 정확하다.
2. 독립적 하위 작업이 있으면 멀티 에이전트, 연속 추론이 필요하면 싱글 에이전트를 쓴다.
3. VAMOS는 ORANGE CORE(팀장) + BLUE NODE(전문가) 구조로 멀티 에이전트를 구현한다.

---

## §22.2 Lead Agent (리드 에이전트 = ORANGE CORE)

### 비유: 프로젝트 팀장

Lead Agent는 프로젝트 팀장과 같습니다. 팀장은 **직접 코딩하거나 리서치하지 않습니다**. 대신:
- 전체 계획을 세우고 (Planning)
- 적합한 팀원에게 일을 나눠주고 (Assignment)
- 진행 상황을 감독하고 (Monitoring)
- 결과를 모아서 최종 결론을 내립니다 (Merging + Decision)

### Lead Agent의 6가지 역할 (LOCK — 변경 불가)

| 역할 | 설명 | 제약 |
|------|------|------|
| **계획 수립 (Planning)** | 사용자 요청을 분석하고 실행 계획 수립 | TEE Think 단계에서 수행 |
| **작업 분배 (Assignment)** | 하위 작업으로 분해 → 적합한 Sub-agent에 할당 | 할당 전 G1(정책)/G2(비용) 통과 필수 |
| **진행 감독 (Monitoring)** | Sub-agent 진행 상황을 실시간 추적 | LogEvent 기록, 타임아웃 감시 |
| **결과 병합 (Merging)** | Sub-agent 결과를 수집하여 최종 응답 구성 | 충돌 해결은 Lead만 수행 |
| **품질 검증 (Verification)** | Self-check + EVX 체인으로 품질 검증 | QoD 미달 시 Soft loop |
| **최종 결론 확정 (Decision Lock)** | S3_DECISION_LOCKED 상태로 결론 잠금 | **단일결정 원칙** 적용 |

> **LOCK-AT-015**: Lead Agent는 직접 코드 작성, 데이터 분석, 웹 검색 등 **실행 작업을 수행하지 않는다**. 모든 실행은 Sub-agent에 위임한다. [근거: S7-A-001]

### Lead Agent 상태 머신 (작동 흐름)

```
IDLE → PLANNING → ASSIGNING → MONITORING → MERGING → VERIFYING → DELIVERING → IDLE
  │                                 │            │
  │                                 ▼            ▼
  │                            ESCALATING   SOFT_LOOPING
  │                            (사용자에게   (재실행 요청)
  │                             승인 요청)
  └────────────────── ABORTED (Gate deny 또는 비용 초과)
```

[근거: VAMOS_AGENT_TEAMS_SPEC §2.1]

### 핵심 요약 (3줄)
1. Lead Agent = ORANGE CORE = 프로젝트 팀장. 직접 실행하지 않고 계획·분배·검증만 수행한다.
2. 최종 결론은 반드시 Lead Agent만 확정한다 (단일결정 원칙, LOCK-AT-002).
3. 모든 작업 위임 전에 G1(정책) + G2(비용) Gate를 반드시 통과해야 한다.

---

## §22.3 Sub-Agent 8가지 타입

### 비유: 전문 팀원들

회사 프로젝트 팀에 다양한 전문가가 있듯이, VAMOS에도 8가지 타입의 Sub-Agent가 있습니다. 각 Sub-Agent는 BLUE NODE (실행 모듈)에 매핑됩니다.

### Sub-Agent 유형 종합표

| # | Sub-Agent 유형 | 비유 | BLUE NODE | P등급 | 모델 | 주요 역할 | 사용 시점 |
|---|---------------|------|-----------|-------|------|----------|----------|
| 1 | **Research Agent** (리서처) | 정보 수집 담당 | Research Node | P0 | Sonnet | 웹 검색, RAG, 사실 확인, 감성 분석 | 정보를 찾아야 할 때 |
| 2 | **Coding Agent** (코더) | 개발자 | Dev Node | P0 | Sonnet | 코드 생성, 디버깅, 리팩토링, 테스트 | 코드 작업이 필요할 때 |
| 3 | **Quant Agent** (분석가) | 데이터 분석가 | Data & Quant Node | P1 | Sonnet | 데이터 분석, 백테스팅, 차트 분석 | 숫자/통계 분석이 필요할 때 |
| 4 | **Content Agent** (작가) | 글쓰기 담당 | Content Node | P1 | Haiku | 문서 작성, 번역, 요약 | 리포트/문서를 만들 때 |
| 5 | **Trading Analysis Agent** (투자 분석가) | 투자 전문가 | Trading Node | **P2** | Opus | 투자 분석, 포트폴리오 최적화 | 투자 관련 분석 시 (승인 필수) |
| 6 | **SDAR Agent** (시스템 의사) | 시스템 관리자 | SDAR Module (I-25) | P0 | Haiku | 자가진단, 자동복구, 건강 점검 | 시스템 오류 발생 시 |
| 7 | **Critic Agent** (검증자) | 품질 감사관 | (내부 검증용) | P0 | Sonnet | 결과 검증, 적대적 검사, 사실 확인 | 결과의 정확성을 확인할 때 |
| 8 | **Productivity Agent** (비서) | 개인 비서 | Productivity Node | P0 | Haiku | 일정 관리, 알림, 메모 | 생산성 관련 작업 시 |

> **비용 절감 포인트**: 팀장(Lead)은 비싼 모델(Opus급)을 쓰고, 단순 작업 팀원(Content, SDAR, Productivity)은 저렴한 모델(Haiku)을 써서 비용을 절감합니다. [근거: S7-A-013]

### 각 Sub-Agent 상세

#### 1. Research Agent (리서처)
- **도구**: Brave Search, Exa AI Search, arXiv 논문 검색, 뉴스 API, RAG 파이프라인
- **스킬**: web_search, rag_retrieval, document_analysis, fact_check, news_aggregation, sentiment_analysis

#### 2. Coding Agent (코더)
- **도구**: Docker 샌드박스 코드 실행, GitHub MCP, 파일 시스템, 린터, 테스트 실행기
- **스킬**: code_generation, code_review, debugging, refactoring, test_writing
- **특이사항**: 파일 소유권 제한 — `src/`, `tests/`만 쓰기 가능, `.env`, `credentials/`는 접근 금지

#### 3. Quant Agent (분석가)
- **도구**: yfinance, DART 공시 API, backtrader, vectorbt, matplotlib
- **스킬**: data_analysis, statistical_modeling, chart_analysis, backtesting, portfolio_optimization

#### 4. Content Agent (작가)
- **도구**: Markdown 렌더러, PDF 생성기, 차트 삽입기, 문서 템플릿
- **스킬**: document_writing, summarization, translation, formatting, proofreading

#### 5. Trading Analysis Agent (투자 분석가) — ⚠️ P2 등급
- **도구**: Paper Trading API (실전 X), 포트폴리오 최적화, 리스크 계산기
- **스킬**: investment_analysis, strategy_evaluation, portfolio_review, risk_assessment
- **제약**: 항상 명시적 승인 필요, 세션 종료 시 자동 OFF (LOCK-AT-008)

#### 6. SDAR Agent (시스템 의사)
- **도구**: 시스템 모니터
- **스킬**: health_monitoring, error_detection, root_cause_analysis, auto_repair
- **자율 수준**: AR-L0(알림만) ~ AR-L4(고위험: 코드 패치)까지 단계적

#### 7. Critic Agent (검증자)
- **도구**: 내부 검증 전용
- **스킬**: verify, adversarial_check, fact_check

#### 8. Productivity Agent (비서)
- **도구**: Calendar, Todo
- **스킬**: scheduling, reminders, note_taking

[근거: VAMOS_AGENT_TEAMS_SPEC §2.2, §4.1~4.6]

### 핵심 요약 (3줄)
1. Sub-Agent는 8가지 전문 타입이 있으며, 각각 BLUE NODE에 매핑된다.
2. P등급에 따라 자동 실행 가능(P0) / 일반(P1) / 승인 필수(P2)로 구분된다.
3. 모델 비용을 절감하기 위해 역할별로 Opus/Sonnet/Haiku를 차등 배정한다.

---

## §22.4 에이전트 3요소: Identity, Capability, Policy

### 비유: 직원 프로필 카드

회사에 입사하면 직원 프로필이 만들어집니다: 이름·직무(Identity), 보유 스킬(Capability), 규정·권한(Policy). VAMOS 에이전트도 마찬가지로 3가지 필수 요소를 반드시 보유합니다.

### 3요소 상세

| 요소 | 의미 | 포함 항목 | 비유 |
|------|------|----------|------|
| **Identity (정체성)** | "나는 누구인가" | 고유 ID, 역할(Role), 도메인, 허용 도구 목록 | 직원증 (이름, 부서, 직급) |
| **Capability (능력)** | "나는 무엇을 할 수 있는가" | 수행 가능 작업, 사용 가능 Brain/Tool, 최대 복잡도 등급 | 스킬 목록 (자격증, 경력) |
| **Policy (정책)** | "나는 어떤 규칙을 따르는가" | 승인 수준(P0/P1/P2), 비용 한도, Self-check 임계값, 자율 수준 | 사규 (보안 등급, 예산 한도) |

### 3요소 코드 구조

```
AgentProfile (에이전트 프로필)
├── Identity
│   ├── agent_id        ← 고유 식별자
│   ├── role            ← core / analysis / coding / research / trading
│   ├── domain          ← 담당 도메인 목록
│   └── allowed_tools   ← Allowlist 기반 허용 도구
├── Capability
│   ├── supported_tasks ← 수행 가능 작업 유형
│   ├── brain_preference← 선호 Brain 순서 (Failover 체인)
│   └── max_complexity  ← simple / moderate / complex
└── Policy
    ├── approval_level  ← P0 / P1 / P2
    ├── cost_budget     ← 세션 내 비용 한도
    ├── selfcheck_threshold ← Self-check 임계값 (0~1)
    └── mode            ← MANUAL / SEMI_AUTO / SUPERVISED_AUTO
```

[근거: D2.0-05 §5.3.1 ADD-024]

### 핵심 요약 (3줄)
1. 모든 VAMOS 에이전트는 Identity(정체성), Capability(능력), Policy(정책)를 필수 보유한다.
2. Identity는 "누구인지", Capability는 "뭘 할 수 있는지", Policy는 "어떤 규칙을 따르는지"를 정의한다.
3. 이 3요소는 에이전트 생성 시 반드시 설정되며, 작업 매칭과 권한 검사의 기준이 된다.

---

## §22.5 에이전트 생명주기 (Lifecycle)

### 비유: 직원의 입사부터 퇴사까지

에이전트의 생명주기는 직원의 회사 생활과 같습니다:
- **Created** = 입사 서류 제출
- **Initialized** = 교육 수료 + 장비 지급
- **Active** = 업무 수행 중
- **Suspended** = 휴직 (리소스 부족/정책 위반)
- **Terminated** = 업무 완료 또는 퇴사
- **Archived** = 인사 기록 보관

### 상태 전이도

```
created ──→ initialized ──→ active ──→ terminated ──→ archived
                              │                          ↑
                              ├── suspended ─────────────┘
                              │   (리소스 부족/정책 위반)
                              │
                              └── terminated (에러 발생)
```

### 각 단계 상세 (LOCK — 변경 불가)

| 단계 | 상태 | 수행 동작 | 기록 이벤트 |
|------|------|----------|------------|
| **생성 (Created)** | `created` | AgentProfile 생성, 모델 등급 할당, 기본 권한 설정 | `agent.spawned` |
| **초기화 (Initialized)** | `initialized` | MCP 도구 연결, Skill 로드, ToolRegistry 등록, Gate 등록 | `agent.initialized` |
| **활성 (Active)** | `active` | 태스크 수신 대기 → 수신 시 TEE 루프 진입 → 결과 반환 | `agent.active` |
| **일시정지 (Suspended)** | `suspended` | 리소스 부족/비용 초과/정책 위반 시 자동 전환. 체크포인트 저장 | `agent.suspended` |
| **종료 (Terminated)** | `terminated` | 태스크 완료 또는 에러. 결과 반환 후 리소스 해제 | `agent.terminated` |
| **보관 (Archived)** | `archived` | 실행 이력/결과를 06(STORAGE) L2 프로젝트 메모리에 보존 | `agent.archived` |

[근거: VAMOS_AGENT_TEAMS_SPEC §2.4]

### 핵심 요약 (3줄)
1. 에이전트는 Created → Initialized → Active → Terminated → Archived 순서로 생명주기를 거친다.
2. 리소스 부족이나 정책 위반 시 Suspended(일시정지)로 전환되며, 복구 후 다시 Active가 될 수 있다.
3. 모든 상태 전이는 LogEvent에 기록되어 추적 가능하다.

---

## §22.6 6가지 협업 패턴

VAMOS Agent Teams는 6가지 협업 패턴을 지원합니다. 어떤 패턴을 쓸지는 작업의 성격에 따라 Lead Agent가 결정합니다.

### §22.6.1 Sequential (순차) — A→B→C 순서대로

```
Agent A ──→ Agent B ──→ Agent C ──→ Lead (결과 병합)
  결과 A ─────→ 입력 B ─────→ 입력 C
```

- **비유**: 공장 조립 라인 — 한 단계가 끝나야 다음 단계 시작
- **사용 시점**: 이전 단계 결과가 다음 단계의 필수 입력인 경우
- **예시**: 코드 작성 → 코드 리뷰 → 테스트 작성 → 테스트 실행

### §22.6.2 Parallel (병렬) — A,B,C 동시 실행 후 취합

```
         ┌──→ Agent A ──┐
Lead ────┼──→ Agent B ──┼──→ Lead (결과 병합)
         └──→ Agent C ──┘
```

- **비유**: 요리사 3명이 전채·메인·디저트를 동시에 준비
- **사용 시점**: 서로 독립적인 하위 작업을 동시에 수행할 때
- **예시**: 뉴스 수집 ‖ 재무 분석 ‖ 기술 차트 분석 → 종합 리포트
- **병렬 수 제한**: V1=최대 3개, V2=10개, V3=50+ (LOCK-AT-014)

### §22.6.3 Debate (토론) — 에이전트 간 의견 대립 → 최선안 선택

```
Lead Agent (사회자)
    │
    ├──→ Bull Agent: "매수 추천" (근거 A, B, C)
    │
    ├──→ Bear Agent: "매도 추천" (근거 D, E, F)
    │
    ├──→ [토론 라운드 1~N]
    │       Bull 반론 → Bear 반론 → ...
    │
    └──→ Lead: 양측 근거 종합 → 최종 결론 확정 (단일결정 원칙)
```

- **비유**: 법정 토론 — 검사 vs 변호사, 판사(Lead)가 최종 판결
- **사용 시점**: 상반된 관점이 필요한 분석 (투자 분석, 전략 평가)
- **토론 라운드 제한**: P0=2라운드, P1=3라운드, P2=5라운드 (LOCK)
- **무한 루프 금지**: LOCK-AT-003
- **버전별 활성**: V1=OFF, V2=조건부(COND), V3=ON

### §22.6.4 Supervisor (감독) — 상위 에이전트가 하위 감독

```
Lead Agent (감독관)
    │ [실시간 모니터링]
    │
    ├──→ Agent A: 실행 중... 진행률 40%
    │       │ ← [Lead: 방향 수정 지시]
    │       └──→ 수정 후 계속 실행
    │
    ├──→ Agent B: 실행 중... 진행률 80%
    │       │ ← [Lead: OK, 계속]
    │
    └──→ Agent C: 오류 발생!
            │ ← [Lead: 중단 + Agent D로 교체]
            └──→ Agent D: 대체 실행
```

- **비유**: 현장 감독관 — 작업자들을 실시간으로 감시하며 필요 시 개입
- **사용 시점**: 복잡한 작업에서 중간 결과를 확인하며 방향을 조정해야 할 때
- **특징**: 실패한 에이전트를 자동으로 대체 에이전트로 교체 가능

### §22.6.5 Handoff (인계) — 한 에이전트가 다른 에이전트에게 작업 전달

- **비유**: 릴레이 경주 — 바톤(컨텍스트)을 넘기며 이어달리기
- **사용 시점**: 한 에이전트의 작업 결과를 다른 에이전트가 이어서 처리할 때
- **인계 패킷 내용**: 작업 ID, 공유 컨텍스트, 부분 결과, 인계 사유, 남은 작업 지시

**인계 프로토콜 (5단계)**:
1. 인계 에이전트가 `handoff_packet` 생성 → Lead Agent에게 전송
2. Lead Agent가 인계 대상 에이전트의 가용성/적합성 확인
3. Lead Agent가 인계 승인 → MessageBus 통해 인수 에이전트에 전달
4. 인수 에이전트가 context 검증 후 실행 시작
5. 인계 이벤트 LogEvent 기록 (`agent.handoff.completed`)

> **V1 제약**: V1에서는 Sub-agent 간 직접 Handoff 금지. 모든 인계는 Lead Agent를 경유해야 함. V2+에서 MessageBus(Redis) 경유 HANDOFF 허용. [근거: VAMOS_AGENT_TEAMS_SPEC §2.3.0]

### §22.6.6 Map-Reduce (분산-취합) — 작업 분할 → 병렬 실행 → 결과 병합

- **비유**: 수능 채점 — 1번~10번은 A 선생님, 11번~20번은 B 선생님이 채점 → 결과 합산
- **사용 시점**: 대량 데이터를 분할하여 병렬 처리한 뒤 결과를 합치는 경우
- **구조**: 데이터 분할(Map) → 각 조각 병렬 처리 → 결과 통합(Reduce)

[근거: VAMOS_AGENT_TEAMS_SPEC §5, D2.0-05 §12.7.3]

### 6가지 패턴 종합 비교

| 패턴 | 구조 | 장점 | V1 | V2 | V3 |
|------|------|------|-----|-----|-----|
| Sequential (순차) | A→B→C | 의존성 처리 용이 | ✅ | ✅ | ✅ |
| Parallel (병렬) | A‖B‖C | 속도 극대화 | ✅ | ✅ | ✅ |
| Debate (토론) | A↔B | 다각도 분석 | ❌ | 조건부 | ✅ |
| Supervisor (감독) | Lead→{A,B,C} | 품질 제어 | ✅ | ✅ | ✅ |
| Handoff (인계) | A→B 인계 | 유연한 전환 | Lead경유 | ✅ | ✅ |
| Map-Reduce (분산) | 분할→병렬→합산 | 대량 처리 | ✅ | ✅ | ✅ |

### 핵심 요약 (3줄)
1. VAMOS는 Sequential, Parallel, Debate, Supervisor, Handoff, Map-Reduce 6가지 협업 패턴을 지원한다.
2. Lead Agent가 작업 성격에 따라 최적의 패턴을 자동 선택한다.
3. V1에서는 Sequential/Parallel이 기본이고, Debate은 V2+에서 활성화된다.

---

## §22.7 ★MoA — Mixture of Agents 패턴 — GAP-3

### 비유: 여러 의사에게 동시에 진료받기

중요한 진단을 할 때, 한 의사의 의견만 듣는 것보다 **여러 의사에게 동시에** 물어보고, 각 의견의 장점을 합쳐서 최종 결론을 내리는 것이 더 정확합니다. MoA도 같은 원리입니다.

### MoA (Mixture of Agents) 정의

MoA는 **여러 LLM 모델을 동시에 실행**하여, 각 모델의 답변 중 **최선의 결과를 선택하거나 통합**하는 패턴입니다.

### MoA 3계층 아키텍처

```
Layer 1 (Proposers — 제안자들):
    ┌──→ Ollama (로컬 Llama 4)  ──→ 답변 A
    ├──→ Claude API              ──→ 답변 B
    ├──→ GPT-4o API              ──→ 답변 C
    └──→ Gemini API              ──→ 답변 D

Layer 2 (Aggregator — 통합자):
    ← 답변 A, B, C, D 수신
    → 각 답변의 강점 추출
    → 모순점 식별 + 해결
    → 통합 답변 생성

Layer 3 (Final — 최종):
    → 가장 강력한 LLM이 최종 정리
```

### 오케스트레이션 규칙

| 규칙 | 설명 |
|------|------|
| 활성화 조건 | 일반 질문 = 단일 모델 / **중요 질문 = MoA 활성화** |
| 비용 | MoA 활성화 시 비용 3~4배 증가 (품질 향상과 트레이드오프) |
| Gate 연동 | G2(비용) Gate에서 MoA 비용 예측 후 예산 내 여부 확인 |
| 단일결정 원칙 | MoA 결과도 최종적으로 ORANGE CORE(Lead)가 확정 |

### 버전별 MoA 지원

| 버전 | 범위 |
|------|------|
| V1 | 2-모델 MoA (즉시 구현 가능) |
| V2 | 풀 MoA — 4개 모델 병렬 (2개월 구현) |
| V3 | 자동 최적 모델 조합 선택 |

[근거: D2.0-03 K-025 Mixture of Agents 구현]

### 핵심 요약 (3줄)
1. MoA는 여러 LLM을 동시에 실행하여 각 답변의 장점을 합치는 "집단 지성" 패턴이다.
2. 3계층 구조: Proposers(제안) → Aggregator(통합) → Final(최종 정리).
3. 비용이 3~4배 증가하므로 중요한 질문에만 선택적으로 활성화한다.

---

## §22.8 Agent Message 형식 & HMAC 서명

### 비유: 보안 우편 시스템

에이전트 간 메시지는 일반 편지가 아니라 **등기우편 + 봉인 도장**과 같습니다. 누가 보냈는지(sender), 누가 받는지(receiver), 내용이 뭔지(content), 언제 보냈는지(timestamp), 그리고 **위변조 방지 도장**(HMAC 서명)이 반드시 포함됩니다.

### 메시지 필드 구조

| 필드 | 설명 | 예시 |
|------|------|------|
| `message_id` | 메시지 고유 ID | `msg_01HZ0001ABCDEF` |
| `trace_id` | 워크플로우 추적 ID | `tr_01HZXXABCDEF` |
| `sender_id` | 발신 에이전트 ID | `lead_001` |
| `receiver_id` | 수신 에이전트 ID | `research_agent_001` |
| `message_type` | 메시지 유형 | delegation / result / progress / handoff / help_request / abort |
| `priority` | 우선순위 | critical / high / normal / low |
| `payload` | 메시지 본문 (작업 내용) | `{"task_id": "task_001", "instruction": "NVIDIA 실적 분석"}` |
| `timestamp` | 전송 시각 (UTC) | `2026-02-23T14:00:00Z` |
| `hmac_signature` | HMAC-SHA256 서명 | `sha256:abc123...` |

### HMAC-SHA256 서명 — 왜 필요한가?

> **LOCK-AT-012**: Agent 메시지에 HMAC 무결성 서명 필수 (변경 불가) [근거: S7E-078]

- **문제**: 에이전트 간 메시지가 중간에 변조되면 엉뚱한 작업을 실행할 위험
- **해결**: HMAC-SHA256으로 메시지에 디지털 서명 → 수신 에이전트가 서명 검증 → 변조 감지

### 통신 보안 규칙 4가지 (S7E-078)

| 규칙 | 설명 |
|------|------|
| HMAC 무결성 서명 | 모든 메시지에 HMAC-SHA256 서명 필수 |
| Agent ID 인증 | 허위 Agent 방지 (Agent ID 검증) |
| 전송 암호화 | TLS 1.3 기반 전송 암호화 |
| 민감 정보 마스킹 | 비밀번호, API 키 등 자동 마스킹 |

[근거: VAMOS_AGENT_TEAMS_SPEC §2.3.1, S7E-078]

### 핵심 요약 (3줄)
1. 에이전트 간 메시지에는 sender, receiver, content, timestamp, hmac_sig가 필수 포함된다.
2. HMAC-SHA256 서명으로 메시지 위변조를 방지한다 (LOCK-AT-012).
3. 추가로 Agent ID 인증, TLS 1.3 암호화, 민감 정보 마스킹이 적용된다.

---

## §22.9 Delegation 제약 (LOCK — 변경 불가)

### 비유: 위임 체인 = 명령 하달 구조

군대에서 장군 → 대령 → 소령으로 명령이 내려가듯이, 에이전트도 위임 체인이 있습니다. 하지만 **무한히 내려갈 수 없고**, 반드시 제한이 있습니다.

### 위임 체인 구조

```
Level 0: Lead Agent (ORANGE CORE)
    │
    ├── Level 1: Research Agent ──── 직접 실행 (MCP 도구 호출)
    │
    ├── Level 1: Coding Agent
    │       │
    │       └── Level 2: Test Runner Sub-agent ──── 테스트 실행
    │
    └── Level 1: Quant Agent
            │
            └── Level 2: Backtesting Sub-agent ──── 백테스팅 실행
                    │
                    └── Level 3: ❌ 금지 (최대 깊이 초과)
```

### 위임 제약 목록 (LOCK — 전체 변경 불가)

| 제약 항목 | 값 | 근거 |
|----------|------|------|
| **최대 위임 깊이** | 3단계 (Lead → Sub → Sub-sub) | S7E-080 |
| **최대 병렬 에이전트** | V1=3, V2=10, V3=50+ | S7-A-008 |
| **위임 시 권한** | 원래 요청자(OWNER) 권한으로 실행 | 권한 상승 방지 |
| **위임 감사** | ORANGE CORE가 모든 위임 요청 감사 기록 | S7E-080 |
| **위임 타임아웃** | P0=30초, P1=120초, P2=300초 | 비용 제어 |
| **대화 턴 상한** | P0=5턴, P1=10턴, P2=20턴 | LOCK-AT-009 |
| **TEE 루프 최대** | P0=3회, P1=5회, P2=10회 | LOCK-AT-010 |
| **예산 배분** | Lead 20% + Sub-agents 80% | 비용 구조 |
| **예비비** | 전체의 10%를 Soft loop/재시도용 예약 | 안전 마진 |

### 위임 불가 작업 목록

- 권한 상승이 필요한 작업 (하위 에이전트가 상위 권한 시도 → 즉시 차단)
- 순환 위임 (A → B → A → ... 무한 루프 → 자동 감지/차단)
- P2 작업의 무승인 위임 (반드시 OWNER 승인 필요)

[근거: VAMOS_AGENT_TEAMS_SPEC §3.3, §3.4]

### 핵심 요약 (3줄)
1. 위임 체인은 최대 3단계까지만 허용되며 초과 시 즉시 차단된다 (LOCK-AT-004).
2. 위임 시 원래 요청자(OWNER)의 권한으로 실행되어 권한 상승이 불가능하다 (LOCK-AT-013).
3. 모든 위임은 ORANGE CORE가 감사 기록하며, 순환 참조/무한 루프도 자동 감지된다.

---

## §22.10 버전별 에이전트 규모

### 비유: 팀 성장 과정

스타트업(V1)일 때는 3명, 중견기업(V2)이 되면 10명, 대기업(V3)이 되면 50명+으로 팀이 성장하는 것처럼, VAMOS의 에이전트 규모도 버전에 따라 확장됩니다.

### 버전별 비교표

| 항목 | V1 (스타트업) | V2 (중견기업) | V3 (대기업) |
|------|-------------|-------------|-------------|
| **에이전트 수** | Lead + 최대 2 Sub (총 3) | Lead + 최대 9 Sub (총 10) | 최대 50+ (동적 생성/해체) |
| **협업 패턴** | Sequential, Parallel | + Debate, Supervisor, Handoff | + Multi-Agent Mesh, Federated |
| **위임 깊이** | 최대 2단계 | 최대 3단계 | 최대 3단계 (안전 유지) |
| **병렬 수** | 최대 3 | 최대 10 | 최대 50+ |
| **Lead 모델** | Sonnet (비용 절감) | Opus | Opus |
| **Sub 모델** | Haiku | Sonnet/Haiku 차등 | 자동 최적 선택 |
| **오케스트레이션** | Centralized (중앙 집중) | + Hierarchical (계층) | + Market-based, Stigmergic |
| **Debate Mode** | OFF | 조건부 ON | 항상 ON |
| **MessageBus** | InMemoryDispatcher | Redis 기반 | Redis + PARL Mesh |
| **일일 비용 한도** | ₩1,300 ($1) | ₩3,100 ($2.3) | ₩8,900 ($6.7) |
| **월 비용 한도** | ₩40,000 ($30) | ₩93,000 ($70) | ₩266,000 ($200) |

[근거: VAMOS_AGENT_TEAMS_SPEC §9.1~9.3]

### 핵심 요약 (3줄)
1. V1은 3개(Lead+2Sub), V2는 10개, V3는 50+개 에이전트를 지원한다.
2. 에이전트 수 확장에 맞춰 통신 방식도 InMemory → Redis → PARL Mesh로 발전한다.
3. 비용 한도도 버전별로 단계적으로 확대된다 (일일 ₩1,300 → ₩3,100 → ₩8,900).

---

## §22.11 V1: InMemoryDispatcher / V2+: Redis MessageBus

### 비유: 사내 메신저 발전 과정

- **V1 (InMemoryDispatcher)**: 3명밖에 없으니 **직접 말로 전달** — 빠르고 단순하지만 기록이 남지 않음
- **V2+ (Redis MessageBus)**: 10명 이상이 되니 **사내 메신저(Slack 같은)** 도입 — 모든 메시지 기록, 다대다 통신 가능

### 아키텍처 비교

| 항목 | V1: InMemoryDispatcher | V2+: Redis MessageBus |
|------|----------------------|---------------------|
| **구현** | 메모리 내 직접 호출 | Redis Pub/Sub 기반 메시지 큐 |
| **통신 방식** | Lead 경유 단방향 위임만 | Pub/Sub 다대다 통신 |
| **Sub-agent 간 직접 통신** | ❌ 금지 (Lead 경유만) | ✅ HANDOFF 허용 (Lead 감사 하에) |
| **메시지 지속성** | 메모리 소실 시 유실 | Redis에 지속 저장 |
| **감사 로그** | 기본 LogEvent | ORANGE CORE Auditor 내장 |
| **확장성** | 3개까지 | 10~50+개까지 |

### MessageBus 아키텍처 (V2+)

```
┌──────────────┐     ┌─────────────────────────────┐     ┌──────────────┐
│  Lead Agent  │────>│       MessageBus (Redis)      │────>│ Sub-Agent A  │
│              │<────│                               │<────│              │
└──────────────┘     │  ┌───────────────────────┐   │     └──────────────┘
                     │  │  ORANGE CORE Auditor   │   │
                     │  │  - 메시지 감사          │   │     ┌──────────────┐
                     │  │  - HMAC 검증           │   │────>│ Sub-Agent B  │
                     │  │  - 정책 필터링          │   │<────│              │
                     │  │  - 비용 모니터링        │   │     └──────────────┘
                     │  └───────────────────────┘   │
                     └─────────────────────────────┘
```

> **V1에서 직접 통신 금지 이유**: 에이전트 3개 환경에서 메시지 순서 보장과 디버깅 단순화를 위해 Lead 허브 패턴을 적용한다. [근거: VAMOS_AGENT_TEAMS_SPEC §2.3.0]

[근거: VAMOS_AGENT_TEAMS_SPEC §2.3]

### 핵심 요약 (3줄)
1. V1은 InMemoryDispatcher(메모리 내 직접 호출)로 3개 에이전트를 간단히 연결한다.
2. V2+는 Redis MessageBus(Pub/Sub)로 다대다 통신을 지원하며 모든 메시지를 감사한다.
3. V1에서 Sub-agent 간 직접 통신은 금지되고, V2+에서 Lead 감사 하에 HANDOFF가 허용된다.

---

## §22.12 LOCK-AT 아키텍처 제약 17건

> LOCK = **변경 불가**. 이 17개 제약은 VAMOS Agent Teams 전체 아키텍처에서 절대 변경할 수 없는 핵심 규칙입니다.

### LOCK-AT 전체 목록

| LOCK ID | 제약 내용 | 근거 |
|---------|----------|------|
| **LOCK-AT-001** | V1은 자체 경량 프레임워크 기본. 외부 엔진은 어댑터로만 연결 | D2.0-05 §5.1 |
| **LOCK-AT-002** | **단일결정 원칙**: 최종 결론은 ORANGE CORE(Lead Agent)만 확정 | D2.0-02 §2.2 S3 |
| **LOCK-AT-003** | 에이전트 간 자유 상호 호출/무한 대화 루프 **금지** | D2.0-03 §1.4, D2.0-05 §7.3 |
| **LOCK-AT-004** | 위임 체인 최대 깊이 **3단계** | S7E-080 |
| **LOCK-AT-005** | 모든 에이전트 실행은 **07 Gate 선행 통과 필수** | D2.0-05 §7.3 고정1 |
| **LOCK-AT-006** | **Execute 단계에서만** 도구 호출 수행 | D2.0-05 §7.3 고정2 |
| **LOCK-AT-007** | Checkpoint/Replay/Fork는 **trace_id 단위로만** 허용 | D2.0-05 §7.3 고정2 |
| **LOCK-AT-008** | P2 에이전트(Trading)는 기본 OFF, 세션별 승인, 세션 종료 시 자동 OFF | RULE 1.3 §3.3 |
| **LOCK-AT-009** | 대화 턴 상한: P0=5턴, P1=10턴, P2=20턴 | D2.0-05 §12.4.4 |
| **LOCK-AT-010** | TEE 최대 반복: P0=3회, P1=5회, P2=10회 | D2.0-05 §12.5.1 |
| **LOCK-AT-011** | 비용 상한 초과 호출은 **승인 없이 자동 차단** | RULE 1.3 §5 |
| **LOCK-AT-012** | Agent 메시지에 **HMAC 무결성 서명 필수** | S7E-078 |
| **LOCK-AT-013** | 위임 시 원래 요청자(OWNER) 권한으로 실행 (**권한 상승 방지**) | S7E-080 |
| **LOCK-AT-014** | V1 병렬 상한=3, V2=10, V3=50+ | S7-A-008 |
| **LOCK-AT-015** | Lead Agent는 **직접 실행 금지** (계획/분배/검증만 수행) | S7-A-001 |
| **LOCK-AT-016** | **LangChain import 금지** (패턴 개념만 참조) | DEC-002 |
| **LOCK-AT-017** | 노코드 빌더는 **n8n + Flowise 듀얼 구조** | D2.0-05 §12.10.2 |

### LOCK-AT 분류별 정리

**안전 관련 (6건)**:
- LOCK-AT-003 (무한 루프 금지), LOCK-AT-004 (깊이 3단계), LOCK-AT-005 (Gate 필수), LOCK-AT-008 (P2 제어), LOCK-AT-012 (HMAC 서명), LOCK-AT-013 (권한 상승 방지)

**아키텍처 관련 (5건)**:
- LOCK-AT-001 (자체 프레임워크), LOCK-AT-002 (단일결정), LOCK-AT-006 (Execute만 도구 호출), LOCK-AT-016 (LangChain 금지), LOCK-AT-017 (노코드 구조)

**자원 제한 관련 (4건)**:
- LOCK-AT-009 (대화 턴), LOCK-AT-010 (TEE 반복), LOCK-AT-011 (비용 차단), LOCK-AT-014 (병렬 상한)

**역할 관련 (2건)**:
- LOCK-AT-007 (trace_id 단위 체크포인트), LOCK-AT-015 (Lead 직접 실행 금지)

[근거: VAMOS_AGENT_TEAMS_SPEC §10.1]

### 핵심 요약 (3줄)
1. LOCK-AT 17건은 Agent Teams의 절대 불변 규칙으로, 안전·아키텍처·자원·역할 4개 범주로 분류된다.
2. 가장 핵심적인 3대 원칙: 단일결정(002), Gate 필수(005), 위임 3단계(004).
3. 모든 LOCK은 RULE 1.3, D2.0 시리즈, S7E 보안 규격에 근거한다.

---

## §22.13 ★Agent Profiling & Capability Registry — GAP-4

### 비유: 직원 역량 평가 시스템

회사에서 매 분기마다 직원 역량 평가를 하듯이, VAMOS는 각 에이전트의 성능을 **지속적으로 프로파일링**합니다. 이 데이터를 바탕으로 "이 작업에는 어떤 에이전트가 가장 적합한지"를 **자동으로 선택**합니다.

### Agent Profiling — 무엇을 측정하는가?

| 지표 | 측정 방식 | 저장 위치 | 활용 |
|------|----------|----------|------|
| **응답 지연 (latency)** | 단계별 시간 측정 | trace_spans | 병목 분석 |
| **작업 성공률** | 완료/실패 비율 | decision_log | 에이전트 신뢰도 산출 |
| **비용 효율** | 비용 대비 QoD 점수 | cost_log | 라우팅 최적화 |
| **도구 호출 효율** | 호출 횟수 대비 유용성 | tool_call_log | Allowlist 개선 |
| **Self-check 통과율** | 1차 통과 vs 재시도 비율 | selfcheck_log | 프롬프트 최적화 |

### 자동 에이전트 선택 알고리즘

Lead Agent가 작업을 받으면, **AgentMatcher**가 아래 5가지 기준으로 점수를 매겨 최적의 에이전트를 선택합니다:

| 기준 | 가중치 | 설명 |
|------|--------|------|
| **스킬 적합도** | 40% | 작업에 필요한 스킬과 에이전트가 보유한 스킬의 일치도 |
| **도구 가용성** | 20% | 필요한 도구를 에이전트가 보유하고 있는지 |
| **비용 효율** | 20% | 예상 비용 대비 예산 여유 |
| **현재 부하** | 10% | 에이전트가 현재 다른 작업을 처리 중인지 |
| **과거 성공률** | 10% | 해당 도메인에서의 역사적 성공률 |

**총점 계산**: 각 기준 점수(0.0~1.0) × 가중치 → 합산 → 점수 내림차순으로 최적 에이전트 선택

### Capability Registry (능력 레지스트리)

- 모든 에이전트의 능력(Capability)을 중앙에서 등록/관리하는 시스템
- 에이전트 스폰 시 자동 등록, 종료 시 자동 해제
- V2+에서 프로파일 데이터를 기반으로 **자동 Brain 라우팅 최적화** 적용 (I-5 피드백 루프)

### 프로파일 데이터 활용 흐름

```
에이전트 실행 완료
    │
    ▼
프로파일 데이터 수집 (latency, 성공률, 비용, QoD)
    │
    ▼
06(STORAGE)에 저장
    │
    ▼
04(INFRA) Observability Dashboard에서 시각화
    │
    ▼
V2+: 자동 Brain 라우팅 최적화 (I-5 피드백 루프)
```

[근거: D2.0-05 §5.3.4 ADD-027]

### 핵심 요약 (3줄)
1. Agent Profiling은 에이전트의 응답 지연, 성공률, 비용 효율, 도구 효율, Self-check 통과율을 지속 측정한다.
2. AgentMatcher가 5가지 기준(스킬 40%, 도구 20%, 비용 20%, 부하 10%, 성공률 10%)으로 최적 에이전트를 자동 선택한다.
3. V2+에서는 프로파일 데이터를 기반으로 Brain 라우팅을 자동 최적화한다.

---

## 종합 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────────────┐
│                        VAMOS AGENT TEAMS                            │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    ORANGE CORE (Lead Agent)                    │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐│  │
│  │  │ I-1      │ │ I-5      │ │ I-6      │ │ I-8              ││  │
│  │  │ Intent   │ │ Decision │ │ Self-    │ │ Policy           ││  │
│  │  │ Parser   │ │ Engine   │ │ Check    │ │ Engine           ││  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘│  │
│  │  ┌──────────────────────────────────────────────────────────┐│  │
│  │  │            Task Decomposer + Delegation Engine           ││  │
│  │  │  plan() → decompose() → assign() → monitor() → merge()  ││  │
│  │  └──────────────────────────────────────────────────────────┘│  │
│  └───────────────┬───────────────┬───────────────┬──────────────┘  │
│                  │               │               │                  │
│         ┌────────▼──────┐ ┌─────▼───────┐ ┌─────▼───────┐         │
│         │  MessageBus   │ │  TaskBoard  │ │  EventBus   │         │
│         └───┬───┬───┬───┘ └─────────────┘ └─────────────┘         │
│             │   │   │                                               │
│  ┌──────────▼┐ ┌▼────────┐ ┌▼──────────┐ ┌───────────┐            │
│  │ Research  │ │ Coding   │ │ Quant     │ │ Content   │  ...       │
│  │ Agent     │ │ Agent    │ │ Agent     │ │ Agent     │            │
│  └─────┬─────┘ └────┬────┘ └─────┬─────┘ └─────┬─────┘            │
│        │            │            │              │                   │
│  ┌─────▼────────────▼────────────▼──────────────▼──────────┐       │
│  │              OTHER BRAINS + MCP Servers                  │       │
│  └──────────────────────────────────────────────────────────┘       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                 07 SAFETY / COST / APPROVAL                  │   │
│  │  [G0 Input] [G1 Policy] [G2 Cost] [G3 Quality] [G4 Final]  │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

[근거: VAMOS_AGENT_TEAMS_SPEC §1.3]

---

## §22 전체 핵심 요약 (3줄)

1. VAMOS Agent Teams는 **Lead Agent(ORANGE CORE) + Sub-Agent(BLUE NODE)** 구조로, 팀장이 계획하고 전문가가 실행하는 멀티 에이전트 아키텍처이다.
2. 6가지 협업 패턴(순차/병렬/토론/감독/인계/분산), MoA(멀티 LLM 통합), Agent Profiling(자동 에이전트 선택)으로 다양한 작업을 효율적으로 처리한다.
3. 17개 LOCK-AT 제약(단일결정, Gate 필수, 위임 3단계, HMAC 서명 등)으로 안전성과 비용 통제를 보장한다.
