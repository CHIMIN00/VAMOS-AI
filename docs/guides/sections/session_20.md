---
session: 20
sections: [23, 24]
status: complete
---

# §23. PARL Agent Swarm — V3 대규모 에이전트

> **비유**: 스타트업(V1)에서 3명이 일하던 팀이, 대기업(V3)이 되면 50명 이상의 전문가가 **그물망처럼 연결**되어 동시에 일합니다. 서로 직접 소통하면서도, 최종 결정은 여전히 팀장(ORANGE CORE)이 내립니다. 이것이 PARL Agent Swarm입니다.

[근거: VAMOS_AGENT_TEAMS_SPEC §9.3, D2.0-05 §5.2.4]

---

## §23.1 50+ 에이전트 Mesh 아키텍처

### 비유: 인터넷처럼 연결된 팀

V1에서는 팀장(Lead)을 중심으로 별(Star) 모양으로 연결됩니다 — 모든 대화가 팀장을 거쳐야 합니다. 하지만 V3에서는 **인터넷처럼** 모든 에이전트가 서로 직접 연결되는 **Mesh(그물망) 토폴로지 (topology, 연결 구조)**를 사용합니다.

### PARL = Parallel Agent Resource Layer (병렬 에이전트 자원 계층)

PARL은 V3에서 도입되는 **대규모 에이전트 병렬 실행 인프라**입니다.

| 항목 | 설명 |
|------|------|
| **정식 명칭** | Parallel Agent Resource Layer |
| **목적** | 50개 이상의 에이전트를 동시에 생성·실행·관리하는 인프라 계층 |
| **도입 버전** | V3 |
| **핵심 기술** | Redis MessageBus + P2P Mesh 네트워크 |

### Mesh 토폴로지 구조

```
V1 (Star 토폴로지):            V3 (Mesh 토폴로지):

     Agent A                    Agent A ◄──► Agent B
       ↑                          ↑  ╲        ╱  ↑
       │                          │    ╲      ╱   │
  ORANGE CORE                     │     ORANGE    │
       │                          │    ╱ CORE ╲   │
       ↓                          ↓  ╱        ╲  ↓
     Agent B                    Agent C ◄──► Agent D
```

- **V1 (Star)**: 모든 통신이 ORANGE CORE(팀장)를 경유 → 3개까지만 효율적
- **V3 (Mesh)**: 에이전트 간 **직접 통신** 가능 → 50+ 에이전트도 빠르게 협업

> **핵심 원칙**: Mesh에서도 **ORANGE CORE가 최종 결정권**을 유지합니다 (LOCK-AT-002: 단일결정 원칙 — 변경 불가). 직접 통신은 "작업 데이터 교환"에만 허용되고, "최종 결론 확정"은 반드시 ORANGE CORE가 수행합니다.

[근거: VAMOS_AGENT_TEAMS_SPEC §9.3, D2.0-05 §5.2.4 ADD-080]

### Mesh 아키텍처 상세도

```
    ┌───────┐     ┌───────┐     ┌───────┐
    │Agent A│◄───►│Agent B│◄───►│Agent C│
    └───┬───┘     └───┬───┘     └───┬───┘
        │             │             │
        └─────────────┼─────────────┘
                      │
              ┌───────▼───────┐
              │  ORANGE CORE  │  (여전히 최종 결정권)
              │  (Supervisor) │
              └───────────────┘
```

- 각 에이전트 노드는 **독립적 trace_id**(추적 번호)를 보유
- 상위 워크플로우 trace_id와 **계층적으로 연결** (부모-자식 관계)
- **Gate 선행 원칙**(§7.3 고정 1)은 Mesh 내 **모든 노드에 동일하게 적용** (변경 불가)

### 버전별 통신 방식 비교

| 항목 | V1 | V2 | V3 |
|------|-----|-----|-----|
| **토폴로지** | Star (중앙 집중) | Hierarchical (계층) | Mesh (그물망) |
| **MessageBus** | InMemoryDispatcher | Redis Pub/Sub | Redis + PARL Mesh |
| **에이전트 간 직접 통신** | ❌ 금지 | Lead 감사 하 HANDOFF | ✅ P2P 허용 |
| **최대 병렬 수** | 3 (LOCK-AT-014) | 10 | 50+ |
| **동적 생성/해체** | ❌ | ❌ | ✅ 작업에 따라 자동 |

[근거: VAMOS_AGENT_TEAMS_SPEC §2.3, §9.1~9.3]

### 핵심 요약 (3줄)
1. PARL(Parallel Agent Resource Layer)은 V3에서 50+ 에이전트를 병렬 관리하는 인프라 계층이다.
2. Mesh 토폴로지로 에이전트 간 직접 통신이 가능하지만, 최종 결정권은 ORANGE CORE가 유지한다 (LOCK-AT-002).
3. V1(Star, 3개) → V2(Hierarchical, 10개) → V3(Mesh, 50+개)로 통신 구조가 진화한다.

---

## §23.2 Agent Marketplace (에이전트 마켓플레이스)

### 비유: 앱스토어

스마트폰에 앱스토어가 있듯이, VAMOS에도 **Agent Marketplace**가 있습니다. 여기서 미리 만들어진 에이전트, 워크플로우 템플릿, 스킬 팩을 **검색·설치·공유**할 수 있습니다.

### Marketplace에서 거래되는 항목 3가지

| 항목 | 설명 | 포함 정보 |
|------|------|----------|
| **Agent 프로필** | 특정 작업 전문 에이전트 | agent_id, name, skills, success_rate, cost_per_use |
| **Workflow 템플릿** | 사전 정의된 워크플로우 | template_id, name, steps, required_tools, estimated_cost |
| **Skill Pack** | 능력 묶음 패키지 | skill_ids, description, compatibility |

### 마켓플레이스 운영 규칙

| 규칙 | 설명 |
|------|------|
| **설치/활성화** | 07 Gate 승인 후에만 허용 |
| **품질 보증** | 등록 시 자동 테스트 + QoD (Quality of Decision, 결정 품질) 기준 충족 필수 |
| **커뮤니티 공유** | V3에서 사용자가 만든 에이전트/워크플로우 공유 가능 |
| **등록/공유 기준** | DEFER-AT-003: V2에서 확정 예정 |

### 배포 파이프라인 (에이전트/워크플로우를 마켓에 올리는 과정)

```
1. 개발           → Skill + Prompt + Tool 정의
2. 테스트         → 자동 테스트 실행 (QoD, 안전성, 비용)
3. 스테이징       → 제한된 트래픽으로 A/B 테스트
4. 프로덕션       → 전체 트래픽 전환
5. 모니터링       → 성능/비용/에러율 추적
```

- **롤백**(되돌리기): 이전 버전 즉시 복원 (trace_id 기반)

### 버전별 Marketplace 지원

| 버전 | 범위 |
|------|------|
| V1 | 코드 기반 템플릿 (내장) |
| V2 | 비주얼 템플릿 + 등록/공유 기준 확정 |
| V3 | 풀 마켓플레이스 — 커뮤니티 공유, 검색, 설치 |

[근거: D2.0-05 §12.8.1~12.8.3, VAMOS_AGENT_TEAMS_SPEC §10.2 DEFER-AT-003]

### 핵심 요약 (3줄)
1. Agent Marketplace는 에이전트·워크플로우·스킬팩을 검색하고 설치하는 "앱스토어"이다.
2. 모든 설치는 07 Gate 승인 필수이며, 등록 시 자동 테스트와 QoD 기준 충족이 요구된다.
3. V1은 내장 템플릿, V2는 비주얼 템플릿, V3에서 커뮤니티 공유 마켓플레이스가 열린다.

---

## §23.3 Agent Specialization Protocol (에이전트 특화 규칙)

### 비유: 전문의 자격증 시스템

종합병원에서 내과, 외과, 피부과 등 전문의가 있듯이, VAMOS 에이전트도 **도메인별로 특화**됩니다. 각 에이전트는 자기 분야의 "자격증"(Identity + Capability + Policy)을 보유하고, 해당 분야의 작업만 수행합니다.

### Agent 3요소 기반 특화 (LOCK)

모든 VAMOS 에이전트는 3요소(Identity, Capability, Policy)를 필수 보유합니다 (ADD-024). 이 3요소가 에이전트의 **전문 분야**를 결정합니다.

```
AgentProfile (에이전트 프로필)
├── Identity (정체성 — "나는 누구인가")
│   ├── agent_id        ← 고유 식별자
│   ├── role            ← core / analysis / coding / research / trading
│   ├── domain          ← 담당 도메인 목록
│   └── allowed_tools   ← Allowlist 기반 허용 도구
├── Capability (능력 — "나는 무엇을 할 수 있는가")
│   ├── supported_tasks ← 수행 가능 작업 유형
│   ├── brain_preference← 선호 Brain 순서 (Failover 체인)
│   └── max_complexity  ← simple / moderate / complex
└── Policy (정책 — "나는 어떤 규칙을 따르는가")
    ├── approval_level  ← P0 / P1 / P2
    ├── cost_budget     ← 세션 내 비용 한도
    ├── selfcheck_threshold ← Self-check 임계값 (0~1)
    └── mode            ← MANUAL / SEMI_AUTO / SUPERVISED_AUTO
```

### Skill Loader 시스템 (스킬 로드 시스템)

에이전트의 특화된 능력(Skill)을 저장/로드/재사용하는 시스템입니다.

```yaml
skill:
  id: "stock_analysis_v2"
  name: "종목 심층 분석"
  prompt_template_ref: "prompt_lib://stock_analysis_v2"
  tools_required: [financial_data, chart_analysis, news_search]
  success_criteria:
    qod_min: 0.7               # 최소 품질 점수
    evidence_count_min: 3       # 최소 근거 3개
  version: "2.1.0"
```

- **Skill 카탈로그**: 중앙에서 관리 (프롬프트 라이브러리와 연동)
- **Skill 선택**: 에이전트가 태스크에 맞는 Skill을 **자동 선택** (유사도 기반)
- **Skill 업데이트**: 성공률/QoD 추적 → 개선 후보 생성 → 승인 후 새 버전 등록

### .vamosrules — 프로젝트 수준 커스텀 규칙

에이전트의 행동을 프로젝트/워크플로우 단위로 세부 제어하는 규칙 파일입니다.

```yaml
rules:
  - name: "투자_분석_규칙"
    scope: "trading_workflow"
    conditions:
      - "추천 시 반드시 3개 이상 근거 제시"
      - "레버리지 추천 금지"
      - "단일 종목 비중 30% 초과 경고"
    enforcement: strict          # 엄격 적용
    gate_integration: true       # 07 Gate와 연동
```

- 규칙 적용 위치: Plan 단계 (G1 정책 검사에 포함)
- 규칙 변경은 07 Gate 승인 후만 허용
- V2+에서는 대화 패턴 분석을 통해 **.vamosrules 개선 규칙을 자동 제안** (승인 후 적용)

[근거: D2.0-05 §5.3.1 ADD-024, §12.6.1~12.6.2]

### 핵심 요약 (3줄)
1. 모든 에이전트는 Identity(정체성)/Capability(능력)/Policy(정책) 3요소로 도메인 특화된다 (ADD-024).
2. Skill Loader 시스템으로 특화된 능력을 저장/로드/자동 선택하며, 성공률 기반으로 업데이트된다.
3. .vamosrules 파일로 프로젝트 수준의 커스텀 규칙을 정의하고, 07 Gate와 연동하여 적용한다.

---

## §23.4 A2A 프로토콜 (Agent-to-Agent)

### 비유: 국제 표준 통신 규약

각 나라가 서로 다른 언어를 쓰더라도, **국제 우편 규격**을 따르면 편지를 보낼 수 있습니다. A2A 프로토콜은 서로 다른 AI 시스템의 에이전트들이 **표준화된 메시지 형식**으로 소통하는 "국제 표준 통신 규약"입니다.

### A2A (Agent-to-Agent) 프로토콜 정의

| 항목 | 설명 |
|------|------|
| **정의** | 서로 다른 AI 시스템의 에이전트가 통신하는 표준 프로토콜 |
| **참조 표준** | Google A2A Protocol |
| **VAMOS 호환** | Google A2A + MCP 양방향 지원 |
| **도입 버전** | V3 (DEFER-AT-005) |
| **결정 시점** | V3 설계 시 구현 범위 확정 예정 |

### A2A + MCP 관계

```
┌─────────────────────────────────────────────────┐
│              VAMOS V3 통신 구조                    │
│                                                   │
│  ┌─────────────┐  A2A  ┌─────────────┐          │
│  │ VAMOS Agent │◄─────►│ 외부 Agent  │          │
│  │ (내부)       │  표준  │ (Google 등)  │          │
│  └──────┬──────┘  메시지 └─────────────┘          │
│         │                                         │
│    MCP  │  (Model Context Protocol)               │
│         │  도구 호출 표준                            │
│         ▼                                         │
│  ┌─────────────┐                                  │
│  │ MCP Server  │ (웹 검색, 코드 실행, API 등)       │
│  └─────────────┘                                  │
└─────────────────────────────────────────────────┘
```

- **A2A**: 에이전트 ↔ 에이전트 간 통신 표준 (수평적)
- **MCP**: 에이전트 → 도구/서비스 간 연결 표준 (수직적)
- V3에서 **양방향 호환**: VAMOS 에이전트가 외부 A2A 에이전트와 협업 가능

### Node 간 A2A 통신 메시지 형식

VAMOS 내부에서도 Blue Node 간 통신은 A2A 프로토콜 형식을 따릅니다.

| 필드 | 설명 |
|------|------|
| `sender` | 발신 에이전트 ID |
| `receiver` | 수신 에이전트 ID |
| `message_type` | 메시지 유형 (delegation / result / handoff 등) |
| `payload` | 메시지 본문 (작업 내용) |
| `timestamp` | 전송 시각 |
| `hmac_signature` | HMAC-SHA256 서명 (LOCK-AT-012 — 변경 불가) |

### Federated Agent (연합 에이전트) — V3 확장

외부 시스템/조직의 에이전트와 **연합(Federation)**하는 구조입니다.

| 규칙 | 설명 |
|------|------|
| **결과 검증** | 외부 에이전트 결과는 반드시 EvidenceBundle로 포장 → 07 Gate 검증 |
| **P2 위임** | 외부 에이전트에 대한 P2 위임은 별도 연합 승인 정책 적용 |
| **승인 정책** | DEFER-AT-004: V3 설계 시 확정 예정 |

[근거: VAMOS_AGENT_TEAMS_SPEC §9.3, §10.2 DEFER-AT-005, D2.0-05 §5.2.5 ADD-084, §14.2 P7-BNT]

### 버전별 상호 운용성

| 버전 | 내부 통신 | 외부 연동 |
|------|----------|----------|
| V1 | Lead 경유 단방향 위임만. Sub-agent 간 직접 A2A 금지 | ❌ |
| V2 | Redis MessageBus + Lead 감사 하 HANDOFF 허용 | ❌ |
| V3 | PARL Mesh P2P + A2A 프로토콜 | ✅ Google A2A + MCP 양방향 |

### 핵심 요약 (3줄)
1. A2A(Agent-to-Agent) 프로토콜은 서로 다른 AI 시스템의 에이전트가 표준 메시지로 소통하는 규약이다.
2. VAMOS V3에서 Google A2A + MCP 양방향 호환을 지원하여 외부 에이전트와의 상호 운용이 가능하다.
3. 외부 에이전트 결과는 반드시 EvidenceBundle + 07 Gate 검증을 거쳐야 한다 (안전 원칙 유지).

---

# §24. Workflow 자동화 시스템

> **비유**: 매일 아침 알람이 울리면(트리거) → 일어나서(액션1) → 커피를 내리고(액션2) → 뉴스를 확인(액션3)하는 "루틴"이 있듯이, VAMOS의 Workflow 자동화 시스템은 **반복되는 작업을 자동으로 실행하는 "디지털 루틴"**입니다.

[근거: D2.0-05 §3, §7, §12.7, §15~16]

---

## §24.1 DAG 기반 워크플로우

### 비유: 프로젝트 일정표

건설 현장에서 "기초 공사 → 골조 → 배관 → 인테리어" 순서가 정해져 있듯이, 워크플로우도 **작업 순서와 의존성**이 정해져 있습니다. 이것을 DAG(Directed Acyclic Graph, 방향 비순환 그래프)라고 합니다.

### DAG란 무엇인가?

| 용어 | 의미 | 비유 |
|------|------|------|
| **Directed (방향)** | 작업에 순서가 있다 (A→B) | 기초 공사 다음에 골조 |
| **Acyclic (비순환)** | 순서가 돌고 돌지 않는다 (A→B→A 금지) | 인테리어 끝나고 다시 기초 공사 하지 않음 |
| **Graph (그래프)** | 노드(작업)와 엣지(연결선)로 이루어진 구조 | 프로젝트 일정표 |

### DAG 구조 설명

```
노드(Node) = 작업
엣지(Edge) = 의존성 (화살표)

    ┌──────────┐     ┌──────────┐
    │ 뉴스 수집  │────►│          │
    └──────────┘     │ 종합     │     ┌──────────┐
                     │ 리포트   │────►│ 사용자에게 │
    ┌──────────┐     │ 생성     │     │ 전달      │
    │ 재무 분석  │────►│          │     └──────────┘
    └──────────┘     └──────────┘
                          ↑
    ┌──────────┐          │
    │ 차트 분석  │──────────┘
    └──────────┘
```

- **뉴스 수집**, **재무 분석**, **차트 분석**은 서로 독립 → **병렬 실행** 가능
- **종합 리포트 생성**은 위 3개가 모두 끝나야 시작 → **의존성**
- **사용자에게 전달**은 리포트가 끝나야 시작

### VAMOS 워크플로우 엔진 아키텍처

| 항목 | 설명 |
|------|------|
| **구현 방식** | DAG 기반 워크플로우 실행기 |
| **기술 스택** | Python asyncio, NetworkX (DAG 라이브러리), Pydantic v2 (스키마) |
| **실행 모드** | sequential (순차, 기본), parallel (병렬 fan-out/fan-in) |
| **상태 관리** | pending → running → paused → completed → failed |

### DAG 노드 유형 10가지

| 노드 유형 | 역할 | 비유 |
|-----------|------|------|
| **LLM Node** | AI 텍스트 처리 (요약, 분류, 생성) | AI 비서 |
| **Code Node** | Python/JS 코드 실행 | 프로그래머 |
| **API Node** | 외부 API 호출 | 전화 담당 |
| **Browser Node** | 웹 자동화 (Playwright) | 인터넷 서핑 담당 |
| **File Node** | 파일 읽기/쓰기/변환 | 서류 담당 |
| **Decision Node** | 조건 분기 | 갈림길 이정표 |
| **Loop Node** | 반복 처리 | 반복 작업자 |
| **Human Node** | 사용자 입력 대기 (HITL) | 결재 라인 |
| **Schedule Node** | 시간 기반 트리거 | 알람 시계 |
| **Notification Node** | 알림 발송 | 메신저 |

### Gate 선행 원칙 (LOCK)

> 어떤 실행 엔진을 쓰더라도 **Execute 단계 전에 07 Gate(PolicyCheck/Approval/Cost)를 반드시 통과**해야 합니다. Gate 결과를 내부 if문으로 대체하는 방식은 허용하지 않습니다 (우회 위험). [근거: D2.0-05 §7.3 고정1]

### 버전별 DAG 엔진 발전

| 버전 | 범위 |
|------|------|
| V1 | 기본 DAG 엔진 (즉시 구현) |
| V2 | 비주얼 에디터 — React Flow 기반 드래그 앤 드롭 (3개월) |
| V3 | 마켓플레이스 연동 + 자동 최적화 |

[근거: D2.0-05 §15.1 N-001]

### 핵심 요약 (3줄)
1. DAG(방향 비순환 그래프)는 작업(노드)과 의존성(엣지)으로 워크플로우의 실행 순서를 정의한다.
2. VAMOS 워크플로우 엔진은 10가지 노드 유형을 지원하며, Python asyncio + NetworkX로 구현된다.
3. 모든 실행은 07 Gate를 선행 통과해야 하며 (LOCK), V1은 기본 DAG, V2는 비주얼 에디터, V3는 마켓플레이스를 지원한다.

---

## §24.2 12가지 Workflow 패턴

### 비유: 요리 레시피 종류

요리에 볶음, 찜, 구이 등 다양한 조리법이 있듯이, 워크플로우에도 12가지 표준 패턴이 있습니다. 작업의 성격에 따라 가장 적합한 패턴을 선택합니다.

### 12가지 워크플로우 패턴 카탈로그

| # | 패턴명 | 구조 | 용도 | 비유 |
|---|--------|------|------|------|
| 1 | **Sequential** (순차) | A→B→C | 단순 분석 | 공장 조립 라인 |
| 2 | **Parallel Fan-out** (병렬 분산) | A→[B1,B2,B3]→C | 멀티소스 수집 | 여러 가게에서 동시 장보기 |
| 3 | **Map-Reduce** (분할-취합) | 데이터 분할→병렬 처리→통합 | 대량 데이터 분석 | 수능 채점 분담 |
| 4 | **Router** (라우터) | 조건별 분기 | 시나리오별 처리 | 고속도로 분기점 |
| 5 | **Retry-with-Backoff** (재시도) | 실패→대기→재시도 | 외부 API 호출 | 통화 중이면 잠시 후 재발신 |
| 6 | **Saga** (사가) | 분산 트랜잭션→보상 | 멀티 시스템 연동 | 항공+호텔 동시 예약 (하나 실패 시 전부 취소) |
| 7 | **Pipeline** (파이프라인) | 단계별 변환 | 데이터 정제 | 정수기 필터 단계 |
| 8 | **Observer** (관찰자) | 이벤트 감지→반응 | 모니터링 | CCTV 감시 |
| 9 | **Mediator** (중재자) | 중앙 조율 | 멀티에이전트 | 교통 경찰 |
| 10 | **Chain of Responsibility** (책임 연쇄) | 핸들러 체인 | 승인 단계 | 결재 라인 (팀장→부장→사장) |
| 11 | **State Machine** (상태 머신) | 상태 전이 | 복잡 워크플로우 | 자판기 (동전 투입→선택→배출) |
| 12 | **Event Sourcing** (이벤트 소싱) | 이벤트 로그 기반 | 감사/재현 | 은행 거래 장부 |

### 주요 패턴별 사용 시점

| 패턴 | 이런 상황에서 사용 |
|------|------------------|
| Sequential | 이전 결과가 다음 단계의 필수 입력인 경우 |
| Parallel Fan-out | 독립적인 작업을 동시에 수행해야 할 때 |
| Map-Reduce | 대량 데이터를 쪼개서 처리한 뒤 합칠 때 |
| Router | 조건에 따라 다른 처리가 필요할 때 |
| Saga | 여러 시스템에 걸친 작업이 "전부 성공 또는 전부 취소"일 때 |
| State Machine | 상태에 따라 다른 동작을 해야 하는 복잡한 흐름 |

[근거: D2.0-05 §12.7.3]

### 핵심 요약 (3줄)
1. VAMOS는 Sequential부터 Event Sourcing까지 12가지 표준 워크플로우 패턴을 지원한다.
2. 작업의 성격(순차/병렬/조건/분산)에 따라 가장 적합한 패턴을 선택하여 사용한다.
3. 모든 패턴은 §7.1 표준 5단계 Pipeline과 Gate 규칙을 준수한다.

---

## §24.3 SOP Pattern (절차 패턴)

### 비유: 매뉴얼대로 하는 프랜차이즈

프랜차이즈 매장에서 햄버거를 만들 때 **표준 운영 절차(SOP)**가 있듯이, VAMOS에서도 반복되는 작업의 **표준 절차를 정의**하여 자동으로 실행할 수 있습니다.

### SOP (Standard Operating Procedure) 정의

SOP는 반복 작업의 **표준 절차를 JSON/YAML 형식으로 정의**하여 워크플로우를 자동 생성하는 패턴입니다.

### SOP 예시: 종목분석 SOP

```yaml
sop:
  name: "종목분석_SOP"
  steps:
    - stage: intake
      action: "사용자 질문 파싱 + 종목코드 추출"
    - stage: plan
      action: "분석 항목 분해 (재무/기술/뉴스/감성)"
      gate: [policy_check, cost_check]
    - stage: execute
      action: "4개 서브에이전트 병렬 실행"
      tools: [financial_data, news_search, chart_analysis]
    - stage: verify
      action: "교차 검증 + QoD 점수 산출"
    - stage: deliver
      action: "종합 리포트 + 3단 출력"
```

### SOP와 표준 5단계 Pipeline의 관계

SOP의 각 step은 **표준 5단계 Pipeline(Intake → Plan → Execute → Verify → Deliver)**에 매핑됩니다.

| SOP step | Pipeline 단계 | 역할 |
|----------|-------------|------|
| intake | Intake | 요청/제약 수집 + G0 입력 검증 |
| plan | Plan | 분해/라우팅 + G1 정책 + G2 비용 |
| execute | Execute | 도구/노드 실행 + 07 Gate 필수 |
| verify | Verify | G3 품질 검사 + Self-check |
| deliver | Deliver | 출력/로그/저장 + 3단 출력 |

### 자연어 → SOP → DAG 자동 변환

```
사용자 입력 (자연어)
    │  "매일 아침 9시에 관심 종목 시세 확인하고
    │   변동이 3% 이상이면 알려줘"
    ▼
LLM 파싱
    │  트리거: Schedule 09:00
    │  노드: API → Code → Decision → Notification
    ▼
DAG JSON 자동 생성 + 미리보기
    │
    ▼
사용자 확인 후 등록/실행
```

- **수정도 대화로**: "알림을 이메일로도 보내줘" → 노드 자동 추가/변경
- SOP → 자연어 → DAG 변환 연계 가능

[근거: D2.0-05 §12.4.3, §15.2 N-002]

### 핵심 요약 (3줄)
1. SOP(Standard Operating Procedure)는 반복 작업의 표준 절차를 YAML/JSON으로 정의하는 패턴이다.
2. SOP의 각 단계는 표준 5단계 Pipeline(Intake→Plan→Execute→Verify→Deliver)에 매핑된다.
3. 자연어로 설명하면 LLM이 자동으로 SOP → DAG 워크플로우를 생성해준다.

---

## §24.4 Trigger/Action 시스템

### 비유: "~하면 ~한다" 자동 규칙

집에서 "해가 지면(트리거) → 조명이 켜진다(액션)"는 스마트홈 자동화와 같습니다. VAMOS의 Trigger/Action 시스템은 **특정 조건이 충족되면 자동으로 워크플로우를 실행**하는 시스템입니다.

### Trigger (트리거) 유형 5가지

| 유형 | 설명 | 예시 |
|------|------|------|
| **schedule** (시간) | 정해진 시간에 실행 | 매일 09:00 시장 리포트 |
| **event** (이벤트) | 특정 사건 발생 시 실행 | 종목 가격 ±5% 변동 |
| **webhook** (외부 호출) | 외부에서 API 호출 시 실행 | 외부 서비스 요청 |
| **manual** (수동) | 사용자가 직접 실행 | UI 버튼 클릭 |
| **chain** (체인) | 다른 워크플로우 완료 후 실행 | 분석 완료 → 리포트 생성 |

### Action (액션) 유형 4가지

| 유형 | 설명 |
|------|------|
| `execute_workflow` | 워크플로우 실행 |
| `send_notification` | 알림 발송 |
| `create_task` | 작업 생성 |
| `update_data` | 데이터 업데이트 |

### Trigger-Action 이벤트 스키마

```json
{
  "trigger_id": "trg_001",
  "trigger_type": "event",
  "condition": "stock_price_change > 5%",
  "action_type": "execute_workflow",
  "target_workflow": "stock_alert_wf",
  "priority_level": "high"
}
```

### 실제 예시: 파일 변경 → 자동 테스트 → 알림

```
[Trigger]                [Action 1]           [Action 2]          [Action 3]
파일 변경 감지  ────►  자동 테스트 실행  ────►  결과 분석  ────►  Slack 알림
(event 트리거)         (execute_workflow)      (LLM Node)        (send_notification)
```

### 트리거 조합

- **AND 로직**: 조건 A **그리고** 조건 B가 모두 충족되면 실행
- **OR 로직**: 조건 A **또는** 조건 B 중 하나라도 충족되면 실행
- Trigger-Action 매핑은 **07 Gate에 등록**하여 정책 검증 대상에 포함

### 버전별 트리거 지원

| 버전 | 지원 트리거 |
|------|-----------|
| V1 | 시간 기반(cron) + 수동 (즉시) |
| V2 | + 이벤트 기반 (파일 변경/이메일/웹훅) (2개월) |
| V3 | + 앰비언트 (ambient, 상황 인식 자동 실행) |

[근거: D2.0-05 §12.7.1, §16.1 N-003]

### 핵심 요약 (3줄)
1. Trigger/Action 시스템은 "조건 충족 시 자동 실행"하는 이벤트 기반 자동화 구조이다.
2. 5가지 트리거(시간/이벤트/웹훅/수동/체인)와 4가지 액션(실행/알림/작업 생성/데이터 업데이트)을 지원한다.
3. 모든 Trigger-Action 매핑은 07 Gate에 등록되어 정책 검증을 받는다.

---

## §24.5 Agentic Coding Pattern (코딩 자동화)

### 비유: AI 개발팀

개발자가 요구사항을 받아서 코드를 쓰고, 테스트하고, 코드 리뷰를 받는 과정을 **AI 에이전트가 자동으로 수행**하는 패턴입니다. 마치 "AI 개발팀"이 코딩을 대신 해주는 것과 같습니다.

### Agentic Coding 파이프라인 (ADD-026)

```
1. Spec 분석      → 사용자 요구사항을 IntentFrame으로 분류
       │
2. 코드 계획      → Plan 단계에서 코드 구조/파일 목록 설계
       │
3. 코드 생성      → Execute 단계에서 Coding Node가 코드 생성
       │
4. 샌드박스 실행   → Docker 샌드박스에서 코드 실행 및 테스트
       │
5. 검증           → Self-check + 코드 품질 게이트 (린팅/테스트 통과)
       │
6. 결과 전달      → Deliver 단계에서 코드 + 실행 결과 + 근거 출력
```

### 안전 규칙 (LOCK — 변경 불가)

| 규칙 | 설명 |
|------|------|
| **파일 시스템 격리** | 파일 쓰기는 Docker 샌드박스 내부에서만 허용 |
| **패키지 설치** | 외부 패키지 설치는 P1 승인 필요 (07 Gate) |
| **코드 덮어쓰기** | 기존 코드를 덮어쓰는 경우 P2 승인 필수 |
| **접근 제한** | `.env`, `credentials/` 폴더 접근 금지 |
| **쓰기 허용 범위** | `src/`, `tests/` 디렉터리만 쓰기 가능 |

### Coding Agent 상세

| 항목 | 내용 |
|------|------|
| **Blue Node** | Dev Node (Coding Node) |
| **P등급** | P0 (자동 실행 가능) |
| **모델** | Sonnet |
| **도구** | Docker 샌드박스, GitHub MCP, 파일 시스템, 린터, 테스트 실행기 |
| **스킬** | code_generation, code_review, debugging, refactoring, test_writing |

### 작업 완료 자동 검증 리포트

코딩 작업 완료 시 AI가 자동으로 검증 리포트를 생성합니다.

```yaml
verification_report:
  task_id: "{auto}"
  checklist:
    - rule_compliance: true/false     # .vamosrules 준수 여부
    - test_passed: true/false         # 테스트 통과 여부
    - no_regression: true/false       # 기존 기능 영향 없음
    - security_scan: true/false       # 보안 취약점 없음
    - cost_within_budget: true/false  # 비용 한도 내
  confidence: 0.0~1.0
```

| 버전 | 검증 리포트 범위 |
|------|---------------|
| V0 | 미생성 |
| V1 | 코드 변경 작업에만 (rule_compliance + test_passed) |
| V2 | 모든 작업 + QoD 점수 포함 |
| V3 | 실시간 검증 + 자동 회귀 테스트 |

[근거: D2.0-05 §5.3.3 ADD-026, VAMOS_AGENT_TEAMS_SPEC §4.2]

### 핵심 요약 (3줄)
1. Agentic Coding은 요구사항 분석 → 코드 생성 → 샌드박스 테스트 → 검증 → 전달의 6단계 자동화 파이프라인이다.
2. 모든 코드 실행은 Docker 샌드박스에서 격리 실행되며, 기존 코드 덮어쓰기는 P2 승인 필수이다 (LOCK).
3. 작업 완료 시 자동 검증 리포트가 생성되어 품질을 보증한다.

---

## §24.6 ★외부 Workflow 엔진 어댑터 규칙 — GAP-6

### 비유: 여행용 전원 어댑터

해외 여행 시 한국 플러그를 외국 콘센트에 바로 꽂을 수 없어서 **어댑터**를 씁니다. VAMOS도 외부 워크플로우 엔진(LangGraph 등)을 직접 가져오지 않고, **어댑터를 통해서만 연결**합니다.

### 핵심 원칙: LangGraph LOCK (변경 불가)

> **LOCK-AT-016**: **LangChain import 금지** (패턴 개념만 참조) — 변경 불가 [근거: DEC-002]

> **LOCK-AT-001**: VAMOS V1은 **자체 경량 프레임워크**를 기본으로 한다. 외부 엔진은 **어댑터로만 연결** — 변경 불가 [근거: D2.0-05 §5.1]

### 왜 외부 프레임워크를 직접 사용하지 않는가?

| 이유 | 설명 |
|------|------|
| **Gate 우회 위험** | 외부 엔진이 07 Gate를 건너뛸 수 있음 |
| **추적 불가** | VAMOS trace_id 체계 밖에서 실행되면 감사/재현 불가능 |
| **정책 불일치** | 외부 엔진의 승인/비용 체계가 VAMOS 규칙과 다를 수 있음 |
| **의존성 과다** | 외부 라이브러리에 과도하게 의존하면 유지보수 어려움 |

### 외부 엔진 어댑터 3대 고정 규칙 (LOCK — 변경 불가)

| 고정 규칙 | 내용 | 근거 |
|----------|------|------|
| **고정 1) Gate 선행** | 어떤 실행 엔진을 쓰더라도 Execute 전에 07 Gate 결과가 선행 확정되어야 함. Gate를 에이전트 내부 if문으로 대체 금지 (우회 위험) | D2.0-05 §7.3 고정1 |
| **고정 2) Checkpoint/Replay/Fork** | VAMOS trace_id 단위로만 허용. 재현 시 동일 trace_id의 Gate 판정도 함께 참조 필수 (감사/재현성 유지) | D2.0-05 §7.3 고정2 |
| **고정 3) 멀티 에이전트 제약** | 역할 분해는 가능하나, 에이전트끼리 자유 상호 호출/무한 루프 금지. 모든 Tool 호출은 Execute 단계에서만. 최종 결론은 단일결정 원칙 | D2.0-05 §7.3 고정3 |

### 참조 가능한 외부 프레임워크 패턴 (패턴만 참조, import 금지)

| 프레임워크 | 참조 패턴 수 | VAMOS 대응 예시 |
|-----------|------------|----------------|
| **LangGraph** | 7건 | StateGraph → 5단계 Pipeline, Conditional Edge → 조건 분기 |
| **LlamaIndex** | 5건 | Query Engine → RAG 파이프라인, Tool Spec → Allowlist |
| **AutoGen** | 6건 | GroupChat → V2 GroupChat, Code Executor → Coding Node |
| **Semantic Kernel** | 5건 | Plugin → MCP 서버, Planner → Plan 단계 |
| **CrewAI** | 5건 | Agent Role → V2 Crew, Process → 5단계 Pipeline |
| **LangChain** | 14건 | LCEL → Runnable 프로토콜, AgentExecutor → 5단계 Pipeline |

### 노코드 빌더 듀얼 구조 (LOCK-AT-017 — 변경 불가)

| 도구 | 역할 |
|------|------|
| **n8n** | 범용 워크플로우 자동화 (Trigger/Action, 스케줄링) |
| **Flowise** | AI/RAG 플로우 구성 (LLM 호출, 벡터 검색, 프롬프트 체인) |

- 두 도구 모두 동일한 §7.1 5단계 Pipeline과 §7.3 Gate 규칙을 준수
- 코드 모드(Python, 개발자용)와 노코드 모드(비주얼, 비개발자용) 듀얼 지원

[근거: D2.0-05 §7.3, §12.2~12.3, §12.10.2, LOCK-AT-001, LOCK-AT-016, LOCK-AT-017]

### 핵심 요약 (3줄)
1. VAMOS는 외부 프레임워크(LangGraph 등)를 직접 import하지 않고, 패턴 개념만 참조한다 (LOCK-AT-016).
2. 외부 엔진 연동 시 3대 고정 규칙(Gate 선행, trace_id 단위 Checkpoint, 무한 루프 금지)을 반드시 준수해야 한다.
3. 노코드 빌더는 n8n(범용 워크플로우) + Flowise(AI 플로우) 듀얼 구조로 확정되었다 (LOCK-AT-017).

---

## §23~24 전체 핵심 요약 (3줄)

1. **PARL Agent Swarm**(§23)은 V3에서 50+ 에이전트를 Mesh 토폴로지로 연결하고, A2A 프로토콜로 외부 에이전트와도 상호 운용하는 대규모 에이전트 시스템이다.
2. **Workflow 자동화**(§24)는 DAG 기반 워크플로우 엔진, 12가지 표준 패턴, SOP, Trigger/Action, Agentic Coding으로 반복 작업을 자동화한다.
3. 모든 시스템은 VAMOS의 핵심 원칙 — **Gate 선행(LOCK-AT-005)**, **단일결정(LOCK-AT-002)**, **자체 경량 프레임워크(LOCK-AT-001)** — 을 예외 없이 준수한다.
