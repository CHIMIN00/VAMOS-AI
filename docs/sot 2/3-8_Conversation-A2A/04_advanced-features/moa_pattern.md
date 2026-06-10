# MoA (Mixture-of-Agents) 패턴 — 04_advanced-features/

> **문서 위치**: `sot 2/3-8_Conversation-A2A/04_advanced-features/moa_pattern.md`
> **정본 위계 Level 4 (구현 상세)** — 상위: D2.0-05 §4.4/§2 (아키텍처 + 비용 상한 Gate) + 상세명세 §5.3 (MoA Python 구현 정본) + 종합계획서 §C MoA 패턴 부록 (제약 표) + R-11-6 (proposer 2~5)
> **Phase**: Phase 2 V2-Phase 2 (P2-4 세션, STEP_B #2b)
> **작성일**: 2026-04-22
> **최종 갱신**: 2026-04-22
> **Status**: V2-Phase 2 DRAFT (L3)
> **버전**: v1.0
> **대응 Phase 2→3 게이트**: **"MoA 완성" 직접 충족** (종합계획서 §7 Phase 2→3 전환 게이트 2번 항목)
> **LOCK 직접 보호**: LOCK-A2A-09 Circuit Breaker (proposer 실패 fallback)
> **LOCK 간접 참조**: LOCK-A2A-01 JSON-RPC 2.0 / LOCK-A2A-02 Task 상태 / LOCK-A2A-05 컨텍스트 윈도우 (aggregator 단계 누적 토큰) / LOCK-A2A-08 Agent Mode (SEMI_AUTO 기본)

---

## 교차 참조

- **구조화 종합계획서**: `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_구조화_종합계획서.md`
  - §3.4 LOCK-A2A-09 (Circuit Breaker — proposer 실패 확산 차단)
  - §4.3 R-11-6 (proposer 최소 2, 최대 5) — 본 문서 비용/품질 균형 제약의 원본 규칙
  - §6.1 #49 MoA 병렬 제안 수집 (proposer) — 서브폴더 매핑 § §5.3
  - §6.1 #50 MoA 집계 에이전트 응답 합성 (aggregator) — 서브폴더 매핑 §5.3
  - §6.3 v12 확장 교차 매핑 (A2A 모니터링 메트릭 연동)
  - §7.3 P2-4 블록 (L1122~L1157, 산출물 본 파일 `moa_pattern.md`)
  - §8.2 W3 MoA 패턴 비용 폭발 리스크 MEDIUM + 대응책 "R-11-6 (최대 5 proposer), 비용 Gate 연동" (L1408)
  - §부록 §C MoA 패턴 (L1510~L1535, proposer 2/5/3, 타임아웃 5/120/30s, aggregator 1/1/1, 비용 = (proposer 수 + 1) × 단일 비용)
  - §부록 Part2 교차 참조 L1598~L1604 (PARL Decision Aggregator ↔ MoA 집계 모드 매핑: Majority Voting / Weighted Average / Consensus)
- **상세명세 (MoA Python 구현 정본)**: `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_상세명세.md` §5.3 L440~L469 `MixtureOfAgents` 클래스 + `asyncio.gather` 병렬 + `aggregation_task.metadata={"pattern":"moa", "proposal_count":len(proposals)}`
- **권한 체계**: `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\AUTHORITY_CHAIN.md` §3 LOCK-A2A-09 row (L64) + LOCK-A2A-05 row (L60) + LOCK-A2A-08 row (L63) verbatim 5필드
- **충돌 기록**: `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONFLICT_LOG.md` §CLF-A2A-004 (CB 3회 vs MCP 5회 의도적 차이, 5회 상향 금지)
- **상위 아키텍처 정본**: `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` §4.4 Circuit Breaker (ADD-072, LOCK-A2A-09 정본) + §2 비용 상한 Gate (MoA 비용 = (proposer 수 + 1) × 단일 비용 상한 연동) + §1.1 Cooperative Agent 구조 (ADD-009, LOCK-A2A-08 Agent Mode)
- **상위 SoT (벤치마크)**: `D:\VAMOS\docs\sot\STEP7-B_대화프로세스_작업가이드.md` — §E L599 #48 병렬 도구 호출 (proposer 병렬 근거) + §F L613 #57 Fallback Chain (proposer 실패 시 폴백) + §F L614 #58 비용 실시간 모니터링 (MoA 비용 매트릭스 05_monitoring 연계) + §5 Kimo/Kimi PARL Agent Swarm L373~L378 (MoA 선행 사례). **CLF-A2A-003 규칙 준수**: STEP7-B 는 시중 AI 벤치마크/갭 식별 참조, D2.0-05 가 아키텍처 정본.
- **peer V2**: `streaming_sse.md` §5 agent_streaming (proposer 병렬 스트림) + §6.1 LOCK-A2A-09 / `push_notifications.md` §8 aggregator 완료 Push 알림 / `multi_turn_sessions.md` §7.2 agent_delegating 재귀 ≤3 + 세션 공유 / `conversation_state_machine.md` §4.3 T#45 agent_delegating 분기 + LOCK-A2A-07 depth 3 / `05_monitoring/metrics_dashboard.md` MoA 비용 매트릭스

---

## 1. 개요

### 1.1 목적

MoA (Mixture-of-Agents) 패턴은 동일 Task 에 대해 **N 개 proposer 에이전트** 가 **병렬 독립 추론**을 수행한 뒤, **단일 aggregator 에이전트**가 제안들을 **합성/집계**하여 최종 응답을 반환하는 다중 에이전트 합의 프로토콜이다. 본 문서는 종합계획서 §C MoA 패턴 부록 + 상세명세 §5.3 Python 구현 정본을 근거로, VAMOS A2A 환경에서의 L3 구현 설계를 확정한다.

### 1.2 범위

- proposer 에이전트 병렬 호출 설계 (R-11-6: 최소 2, 최대 5, 기본 3)
- aggregator 응답 합성 알고리즘 (3 집계 모드: Majority Voting / Weighted Average / Consensus)
- 비용 매트릭스 (MoA 비용 = (proposer 수 + 1) × 단일 호출 비용, D2.0-05 §2 비용 상한 Gate 연동)
- 에러 처리 (proposer 부분 실패 / 전원 실패 / aggregator 실패 시 fallback chain)
- LOCK-A2A-09 Circuit Breaker 연동 (proposer 장애 연속 3 회 → OPEN)
- LOCK-A2A-05 컨텍스트 윈도우 한계 (aggregator 단계 누적 토큰 제어)
- peer cross-ref (streaming_sse / push_notifications / multi_turn_sessions / conversation_state_machine / metrics_dashboard)

### 1.3 범위 외 (Phase 3 이월)

- proposer 에이전트 동적 선발 알고리즘 상세 (02_agent-discovery/agent_selection.md — P2-6 범위, Phase 3 Jaccard 유사도 확장)
- aggregator 의 요약/합성 프롬프트 엔지니어링 (에이전트 내부 결정, 본 문서 scope 외)
- Safety-critical 작업 시 Consensus 모드 자동 전환 정책 (거버넌스 규정, 6-2 Security 소유)
- MoA 결과 캐싱 (Semantic Caching, STEP7-B L1003 #76 Semantic Caching VAMOS 설계만)
- 5 초과 proposer 확장 (R-11-6 상한 변경 시 거버넌스 재검토 필요 — 변경 금지)

---

## 2. 아키텍처 개요

### 2.1 MoA 실행 흐름 (종합계획서 §C.1 verbatim)

```
1. Orchestrator가 N개 proposer 에이전트에 동일 task 병렬 전송
2. 각 proposer가 독립적으로 응답 생성 (tasks/send)
3. 모든 응답 수집 후 aggregator 에이전트에 합성 요청
4. Aggregator가 N개 제안을 분석하여 최적 응답 생성
5. 최종 응답을 원래 요청자에게 반환
```

### 2.2 컴포넌트 다이어그램 (Mermaid)

```mermaid
flowchart TB
    subgraph Orchestrator["MoA Orchestrator (caller)"]
        O[MixtureOfAgents.execute]
    end

    subgraph Proposers["Proposer Pool (N=2~5, R-11-6)"]
        P1[Proposer #1]
        P2[Proposer #2]
        P3[Proposer #3 (optional)]
        P4[Proposer #4 (optional)]
        P5[Proposer #5 (optional)]
    end

    subgraph Aggregator["Aggregator (N=1, R-11-6)"]
        A[aggregation_task<br/>metadata.pattern=moa]
    end

    subgraph CB["LOCK-A2A-09 Circuit Breaker"]
        CBG[state ∈ CLOSED / OPEN / HALF-OPEN]
    end

    O -->|asyncio.gather 병렬| P1
    O -->|asyncio.gather 병렬| P2
    O -->|asyncio.gather 병렬| P3
    O -.optional.-> P4
    O -.optional.-> P5

    P1 -->|TaskResult| A
    P2 -->|TaskResult| A
    P3 -->|TaskResult| A

    A -->|최종 합성 응답| O

    P1 -.장애.-> CBG
    P2 -.장애.-> CBG
    CBG -.3회 실패.-> OpenState[-32030 Circuit breaker open]

    OpenState -->|60s 후 HALF-OPEN| P1
```

### 2.3 정본 Python 구현 (상세명세 §5.3 L440~L469 verbatim)

```python
class MixtureOfAgents:
    """다중 에이전트 합의 기반 응답 생성"""

    def __init__(self, proposer_agents: list[str], aggregator_agent: str):
        self.proposers = proposer_agents
        self.aggregator = aggregator_agent

    async def execute(self, task: TaskRequest) -> TaskResult:
        # Phase 1: 병렬 제안 수집
        proposals = await asyncio.gather(*[
            self.send_task(agent_id, task)
            for agent_id in self.proposers
        ])

        # Phase 2: 집계 에이전트가 최종 응답 합성
        aggregation_task = TaskRequest(
            message=Message(
                role="user",
                parts=[
                    TextPart(f"다음 {len(proposals)}개 제안을 분석하여 최적 응답을 합성하세요:"),
                    *[TextPart(f"[제안 {i+1}]: {p.result}") for i, p in enumerate(proposals)]
                ]
            ),
            metadata={"pattern": "moa", "proposal_count": len(proposals)}
        )
        return await self.send_task(self.aggregator, aggregation_task)
```

> **정본 소유**: 본 구현 코드는 `CONVERSATION_A2A_상세명세.md §5.3` (L440~L469) 의 수정 없는 재인용이다. 본 V2 문서에서는 코드 자체는 변경 금지 (append-only 원칙), 아래 §3~§8 에서 L3 설계 상세 (가드 / 타임아웃 / 집계 모드 / 비용 / 에러 처리) 를 추가 정의한다.

---

## 3. R-11-6 proposer 제약 (종합계획서 §4.3 + §C 부록 L1526~L1532 verbatim)

### 3.1 proposer 파라미터 표 (정본)

| 파라미터 | 최소 | 최대 | 기본값 | 근거 |
|---------|------|------|--------|------|
| **proposer 수** | **2** | **5** | **3** | R-11-6 (§4.3), §C.1 (L1530) |
| **응답 대기 타임아웃** | 5 초 | 120 초 | 30 초 | §C.1 (L1531) |
| **aggregator 수** | 1 | 1 | 1 | §C.1 (L1532) |

### 3.2 R-11-6 verbatim (§4.3 L198)

> `R-11-6 | MoA 패턴 사용 시 최소 2, 최대 5 proposer 에이전트 | 비용/품질 균형`

### 3.3 가드레일 구현 (생성자 단계 검증)

```python
class MixtureOfAgentsV2(MixtureOfAgents):
    """R-11-6 + 타임아웃 + 집계 모드 + CB 를 추가한 L3 확장"""

    MIN_PROPOSERS = 2   # R-11-6 하한 (1개 거절)
    MAX_PROPOSERS = 5   # R-11-6 상한 (6개 이상 거절, CLF-A2A-004 유사 의도적 차이: 상향 금지)
    DEFAULT_PROPOSERS = 3

    MIN_TIMEOUT_S = 5
    MAX_TIMEOUT_S = 120
    DEFAULT_TIMEOUT_S = 30

    def __init__(
        self,
        proposer_agents: list[str],
        aggregator_agent: str,
        *,
        timeout_s: int = DEFAULT_TIMEOUT_S,
        aggregation_mode: "AggregationMode" = "majority_voting",
    ):
        # R-11-6 가드 (O(1))
        n = len(proposer_agents)
        if n < self.MIN_PROPOSERS:
            raise ValueError(
                f"R-11-6 violation: proposer count {n} < {self.MIN_PROPOSERS} (minimum). "
                f"MoA 품질 보장을 위해 최소 2 개 proposer 필요."
            )
        if n > self.MAX_PROPOSERS:
            raise ValueError(
                f"R-11-6 violation: proposer count {n} > {self.MAX_PROPOSERS} (maximum). "
                f"MoA 비용 폭발 방지를 위해 최대 5 개 proposer 제한. 상향 금지."
            )
        # 타임아웃 가드
        if not (self.MIN_TIMEOUT_S <= timeout_s <= self.MAX_TIMEOUT_S):
            raise ValueError(f"timeout_s={timeout_s} out of range [5, 120]")
        # aggregator 단수 가드 (R-11-6 L1532)
        # (생성자 시그니처에서 단일 str 로만 받으므로 구조적 보장)

        super().__init__(proposer_agents, aggregator_agent)
        self.timeout_s = timeout_s
        self.aggregation_mode = aggregation_mode
```

### 3.4 Pydantic 공용 구조 (세션 간 공유)

```python
from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field, conlist

class AggregationMode(str, Enum):
    """MoA 집계 모드 (Part2 교차 참조 L1598~L1604)"""
    MAJORITY_VOTING = "majority_voting"     # 기본 (N 개 proposer 중 다수결)
    WEIGHTED_AVERAGE = "weighted_average"   # 에이전트 신뢰도 가중 평균 (advanced)
    CONSENSUS = "consensus"                  # 전원 동의 필요 (safety-critical)


class MoAConfig(BaseModel):
    """MoA 실행 설정 (R-11-6 제약 인라인 검증)"""
    proposer_agents: conlist(str, min_length=2, max_length=5)  # R-11-6
    aggregator_agent: str
    timeout_s: int = Field(30, ge=5, le=120)
    aggregation_mode: AggregationMode = AggregationMode.MAJORITY_VOTING
    cost_cap_usd: float | None = None  # D2.0-05 §2 비용 상한 Gate 연동


class Proposal(BaseModel):
    """proposer 단건 응답"""
    proposer_id: str
    result: str
    latency_ms: int
    confidence: float = Field(ge=0.0, le=1.0)  # 에이전트 self-assessed 신뢰도
    cost_usd: float


class AggregationResult(BaseModel):
    """aggregator 집계 결과"""
    final_answer: str
    aggregation_mode: AggregationMode
    proposal_count: int
    succeeded_count: int
    failed_count: int
    total_cost_usd: float
    metadata: dict  # {"pattern":"moa", "proposal_count":N, ...}
```

---

## 4. proposer 병렬 호출 설계

### 4.1 `asyncio.gather` 병렬 의미 (STEP7-B §E L599 #48 근거)

- **실행 모델**: `asyncio.gather(*coros, return_exceptions=True)` — N 개 proposer 코루틴을 **동시 스케줄링**, 결과를 **원래 호출 순서대로** 수집. 일부 proposer 가 예외를 반환해도 다른 proposer 는 계속 진행 (return_exceptions=True 필수).
- **동시성 상한**: N ≤ 5 이므로 세마포어 불필요 (`asyncio.Semaphore(5)` 암묵적). 외부 tasks/send 엔드포인트는 각 proposer 에이전트 고유 `agent_id` 로 분기.
- **타임아웃 래핑**: 각 proposer 호출을 `asyncio.wait_for(coro, timeout=self.timeout_s)` 로 감싸, 30 초 초과 시 `asyncio.TimeoutError` 발생 → `return_exceptions=True` 에 의해 `Proposal` 대신 `TimeoutError` 가 `proposals[i]` 에 반환.
- **취소 전파**: Orchestrator 가 취소되면 `gather` 는 하위 proposer 코루틴을 전부 `cancel()` 호출 (tasks/cancel 후속 전파는 Phase 3 이월, 현재는 로컬 취소만).

### 4.2 `send_task` 인터페이스 (상세명세 §2 + peer `conversation_state_machine.md`)

```python
async def send_task(
    self,
    agent_id: str,
    task: TaskRequest,
) -> TaskResult:
    """
    JSON-RPC 2.0 method=tasks/send (LOCK-A2A-01 verbatim)
    반환: TaskResult (LOCK-A2A-02 Task 상태 열거형에서 completed/failed/canceled 중 하나)
    """
```

- `tasks/send` 동기 완료 (SSE stream 미사용) — proposer 는 단건 요청-응답. streaming 필요 시 `streaming_sse.md` §5 agent_streaming 참조 (MoA 내부는 비-스트리밍 기본, proposer 병렬 스트림 시 `streaming_sse.md` §8 TS-14 MoA proposer 병렬 스트림 시나리오 참조).
- proposer 실패 분류 (LOCK-A2A-02 상태 머신 기준):
  - `completed` → 정상 `Proposal` 생성
  - `failed` → `FailedProposal` 마킹, `failure_code` 기록
  - `canceled` → `CanceledProposal` 마킹 (cost 집계 제외)

### 4.3 시간 복잡도

- **병렬 호출**: O(max(proposer latency)) — N 개 동시 실행이므로 **wall-clock 은 가장 느린 proposer 의 지연**에 지배됨 (`timeout_s` 상한).
- **집계 단계**: O(N) Majority Voting / O(N) Weighted Average / O(N) Consensus (단순 선형).
- **전체 MoA**: **O(max(proposer) + aggregator)** ≈ O(30 초 + aggregator 지연). 순차 호출 대비 약 (proposer 수) 배 단축.

---

## 5. aggregator 집계 모드 (3 모드)

### 5.1 Majority Voting (기본, §부록 L1601)

- **의미**: N 개 proposer 응답 중 **다수결**. 동점 시 `confidence` 최고 proposer 채택.
- **적용 범위**: 일반 질의응답, 코드 생성, 번역 등 "정답 1 개" 수렴 가능 과제.
- **알고리즘**:

```python
def majority_voting(proposals: list[Proposal]) -> str:
    # 응답 텍스트 정규화 (whitespace / punctuation) 후 buckets 카운트
    buckets: dict[str, list[Proposal]] = defaultdict(list)
    for p in proposals:
        key = normalize(p.result)
        buckets[key].append(p)
    # 최대 bucket → 동점 시 평균 confidence 최고 순
    best_key = max(
        buckets,
        key=lambda k: (len(buckets[k]), mean(p.confidence for p in buckets[k]))
    )
    return best_key  # 정규화 이전 대표 응답은 bucket 내 confidence 최고
```

- **시간 복잡도**: O(N) (N ≤ 5 이므로 사실상 상수)

### 5.2 Weighted Average (advanced, §부록 L1602)

- **의미**: 각 proposer `confidence` (self-assessed) + **에이전트 카드 상의 과거 성공률** 을 가중치로 한 평균. 수치 응답 (점수/확률/예측값) 에 적합.
- **적용 범위**: 정량 평가 과제 (순위 매기기, 확률 예측, 신뢰도 가중 추론).
- **알고리즘**:

```python
def weighted_average(proposals: list[Proposal], historical_success: dict[str, float]) -> float:
    # 수치 응답만 허용 (자연어 텍스트 합산 불가)
    values = []
    weights = []
    for p in proposals:
        w = p.confidence * historical_success.get(p.proposer_id, 1.0)
        values.append(parse_numeric(p.result))
        weights.append(w)
    return sum(v * w for v, w in zip(values, weights)) / sum(weights)
```

- **시간 복잡도**: O(N)
- **주의**: 자연어 응답에는 적용 불가 (parse_numeric 실패 → `TypeError`). aggregator 단계에서 응답 형식 사전 검증 필수.

### 5.3 Consensus (safety-critical, §부록 L1603)

- **의미**: **N 개 proposer 전원 동의** 필요. 1 개라도 불일치 시 `ESCALATE_TO_HUMAN` 결과 반환 (6-2 Security 거버넌스 연계).
- **적용 범위**: 의료 진단 보조, 법적 문서 생성, 금융 거래 권고 등 안전 임계 과제.
- **알고리즘**:

```python
def consensus(proposals: list[Proposal]) -> tuple[bool, str | None]:
    # 정규화 후 모두 동일한 응답인지 검사
    normalized = {normalize(p.result) for p in proposals}
    if len(normalized) == 1:
        return (True, next(iter(normalized)))
    return (False, None)  # 에스컬레이션 트리거
```

- **시간 복잡도**: O(N)
- **거버넌스 연동**: Consensus 실패 시 I-20 EscalationHandler 에 payload 전달 (§7.3 에스컬레이션 페이로드 참조).

### 5.4 모드 선택 매트릭스

| 과제 성격 | 권장 모드 | proposer 수 권장 | 비용 승수 |
|----------|----------|-----------------|-----------|
| 일반 질의응답 | MAJORITY_VOTING | 3 | ×4 (3 + 1) |
| 코드 생성 | MAJORITY_VOTING | 3 | ×4 |
| 정량 예측 | WEIGHTED_AVERAGE | 5 | ×6 (5 + 1) |
| 번역 | MAJORITY_VOTING | 2 | ×3 |
| 의료/법률/금융 | CONSENSUS | 3~5 | ×4~×6 |
| 비용 민감 | MAJORITY_VOTING | 2 | ×3 (최소) |

---

## 6. 비용 관리 (종합계획서 §C + §8.2 W3)

### 6.1 비용 공식 (§C verbatim L1534)

> **MoA 실행 시 비용 = (proposer 수 + 1) × 단일 호출 비용**.
> **D2.0-05 §2 의 비용 상한 Gate 와 연동하여 상한 초과 시 자동 차단**.

### 6.2 비용 매트릭스

| proposer 수 | aggregator 수 | 총 호출 수 | 승수 | 일반 과제 예산 | Safety-critical 예산 |
|------------|--------------|-----------|------|----------------|---------------------|
| 2 | 1 | 3 | ×3 | 허용 | 허용 |
| 3 (기본) | 1 | 4 | ×4 | 허용 | 허용 |
| 4 | 1 | 5 | ×5 | 관찰 | 허용 |
| 5 (상한) | 1 | 6 | ×6 | **비용 Gate 경고 필수** | 허용 |
| **≥6** | — | — | — | **R-11-6 위반, ValueError** | 동일 |

### 6.3 D2.0-05 §2 비용 상한 Gate 연동

- 실행 전: 예상 비용 = `len(proposers) * single_call_cost + aggregator_cost` 계산 → `MoAConfig.cost_cap_usd` 초과 시 생성자에서 `CostCapExceeded` 예외 발생.
- 실행 중: proposer 별 누적 cost 를 `Proposal.cost_usd` 로 집계. gather 완료 시점에 실측 비용 vs cap 비교, 초과 시 aggregator 단계 skip 하고 `PARTIAL_ABORT` 반환.
- 사후: `AggregationResult.total_cost_usd` 를 `05_monitoring/metrics_dashboard.md` 의 성능/비용 메트릭 게이지에 보고 (OTel span attribute `moa.total_cost_usd`).

### 6.4 W3 리스크 완화 (§8.2 L1408)

- **리스크**: "MoA 패턴 비용 폭발" MEDIUM.
- **대응**:
  1. R-11-6 상한 5 로 hard cap (본 문서 §3.3 `MAX_PROPOSERS = 5`, 위반 시 `ValueError`).
  2. 비용 Gate 선제 차단 (§6.3).
  3. Prompt Caching 활용 (STEP7-B L1002 #75, proposer 공통 prompt 부분 캐시 — Phase 3 이월).
  4. Semantic Caching (STEP7-B L1003 #76, 유사 질의 재사용 — VAMOS 설계만, Phase 3 이월).

---

## 7. 에러 처리 + Circuit Breaker 연동

### 7.1 LOCK-A2A-09 Circuit Breaker (연속 실패 3 회 → OPEN, 60 초 후 HALF-OPEN)

**LOCK-A2A-09 verbatim 5필드 분리 인용** (AUTHORITY_CHAIN.md §3 L64):

| 필드 | 값 |
|------|------|
| **LOCK ID** | `LOCK-A2A-09` |
| **항목** | Circuit Breaker 연속 실패 임계 |
| **값** | `3회 → OPEN, 60초 후 HALF-OPEN` |
| **출처** | `D2.0-05 §4.4 (ADD-072)` |
| **변경 조건** | `D2.0-05 변경 시만` |

**적용 규칙**:

1. proposer 별로 CB 상태를 독립 관리 (`cb_state[agent_id] ∈ {CLOSED, OPEN, HALF-OPEN}`).
2. 특정 proposer 로의 `tasks/send` 가 연속 3 회 실패(exception + timeout) 시 해당 proposer 의 CB → OPEN. 이후 60 초간 **해당 proposer 호출을 즉시 skip** (return_exceptions 에 `CircuitBreakerOpen` 주입).
3. 60 초 경과 후 HALF-OPEN: 다음 MoA 호출 시 1 건만 시험. 성공 시 CLOSED 복귀, 실패 시 다시 OPEN + 60 초 누적 대기.
4. **의도적 차이 (CLF-A2A-004 RESOLVED)**: A2A 3 회 임계와 MCP 5 회 임계는 의도적 차이. A2A 에이전트 간 통신은 실패 시 파급 범위가 크고(다중 에이전트 체인 연쇄 실패 가능), 신속한 차단이 필요하므로 보수적 임계값(3 회) 적용. **5 회로 상향 금지**.
5. MoA 의 CB 개방은 `streaming_sse.md` §6.1 의 단일 에이전트 CB 와 **독립 병렬**: proposer A 가 OPEN 이어도 proposer B/C 는 정상 진행 (부분 fallback, §7.2 참조).
6. CB 상태는 `05_monitoring/metrics_dashboard.md` 의 안정성 메트릭 (`cb_state_per_agent` 게이지) 로 노출.

### 7.2 proposer 부분 실패 fallback chain

```
proposer 실패 수 / 총 proposer 수 == 0     → 정상 집계 (§5)
proposer 실패 수 / 총 proposer 수 > 0, 성공 ≥ MIN_PROPOSERS (2)
                                           → 성공분만으로 집계 (Degraded, confidence -0.1 감산)
proposer 성공 < MIN_PROPOSERS (2)           → ESCALATE_TO_FALLBACK
                                             (단일 proposer fallback 또는 에이전트 재선택)
proposer 전원 실패                          → ABORT + -32030 (CB OPEN 전체 proposer)
                                             + I-20 에스컬레이션 payload
```

**STEP7-B §F L613 #57 Fallback Chain** 근거: VAMOS 독자 기능, proposer 실패 시 단일 에이전트 fallback 이 기본 경로. Phase 3 에서 대체 에이전트 재선택 (02_agent-discovery/agent_selection) 과 통합.

### 7.3 에스컬레이션 페이로드 (I-20 EscalationHandler 전달)

```python
from pydantic import BaseModel

class MoAEscalationPayload(BaseModel):
    """MoA 실패 시 I-20 에스컬레이션 전달 구조 (I-20 공용 필드 6 + MoA 추가 4)"""
    # 공용 6 필드
    source_engine: Literal["moa_pattern"] = "moa_pattern"
    error_code: str                       # "-32030" / "ABORT_ALL_FAILED" / "CONSENSUS_DISAGREEMENT"
    original_request: TaskRequest
    partial_result: AggregationResult | None  # Degraded 집계 시 성공분만
    retry_count: int                      # 재시도 누적 (CB HALF-OPEN 복구 시도 포함)
    timestamp: str                        # ISO 8601 UTC
    # MoA 추가 4 필드
    proposer_ids: list[str]
    proposer_failure_map: dict[str, str]  # {agent_id: error_code}
    aggregation_mode: AggregationMode
    cb_state_snapshot: dict[str, str]     # {agent_id: "CLOSED"|"OPEN"|"HALF-OPEN"}
```

### 7.4 에러 코드 매핑 (상세명세 §4.4 정합)

| 코드 | 상황 | MoA 복구 |
|------|------|----------|
| `-32001` | Task not found | proposer 개별 처리, 집계 대상 제외 |
| `-32004` | Unsupported operation | 해당 proposer skip, 대체 에이전트 재선택 (Phase 3) |
| `-32024` (비표준) | Session not found | MoA 전체 abort (세션 컨텍스트 손실) |
| `-32030` | Circuit breaker open (비표준 확장) | proposer 개별 skip, 성공분으로 집계 시도 |
| `CONSENSUS_DISAGREEMENT` | Consensus 모드 불일치 | I-20 에스컬레이션 + `ESCALATE_TO_HUMAN` |
| `COST_CAP_EXCEEDED` | D2.0-05 §2 상한 초과 | aggregator skip, PARTIAL_ABORT 반환 |
| `ABORT_ALL_FAILED` | 모든 proposer 실패 | I-20 에스컬레이션 + 단일 에이전트 fallback |

### 7.5 로깅 포맷 (R-01-7 structured JSON, 중첩 구조 필수)

```json
{
  "trace_id": "trace-uuid",
  "error": {
    "code": "-32030",
    "message": "Circuit breaker open for proposer agent:qa-001",
    "source": "moa_pattern.proposer_cb_guard"
  },
  "context": {
    "moa_session_id": "moa-uuid",
    "task_id": "task-uuid",
    "proposer_ids": ["agent:qa-001", "agent:qa-002", "agent:qa-003"],
    "aggregation_mode": "majority_voting",
    "cb_state_per_agent": {
      "agent:qa-001": "OPEN",
      "agent:qa-002": "CLOSED",
      "agent:qa-003": "CLOSED"
    },
    "cb_open_since": "2026-04-22T10:15:00Z"
  },
  "recovery": {
    "strategy": "partial_aggregation",
    "succeeded_count": 2,
    "failed_count": 1,
    "degraded_confidence_penalty": -0.1,
    "next_attempt_after_s": 60
  }
}
```

---

## 8. 컨텍스트 윈도우 (LOCK-A2A-05) — aggregator 단계

### 8.1 LOCK-A2A-05 verbatim 5필드 분리 인용 (AUTHORITY_CHAIN.md §3 L60)

| 필드 | 값 |
|------|------|
| **LOCK ID** | `LOCK-A2A-05` |
| **항목** | 컨텍스트 윈도우 한계 |
| **값** | `모델별 max_tokens 준수, 초과 시 압축` |
| **출처** | `D2.0-05 §12.13` |
| **변경 조건** | `모델 변경 시 갱신` |

### 8.2 aggregator 단계 토큰 누적 제어

- aggregator 입력 = 원본 task + N 개 proposer 응답 텍스트 (각 최대 4 K 토큰 가정 시 N=5 에서 약 20 K 토큰 누적).
- 누적 토큰이 aggregator 모델의 `max_tokens × 0.85` 초과 시 압축 트리거 (`streaming_sse.md` §7.2 동일 규칙).
- 압축 정책 위임: aggregator 에이전트 내부 (요약 체인 / 맵리듀스) — `multi_turn_sessions.md` §5 컨텍스트 관리 에 상세. 본 MoA 문서 scope 외.
- 위반 시 `-32005 Content type not supported` 폴백 (상세명세 §4.4).

---

## 9. Agent Mode 연동 (LOCK-A2A-08)

### 9.1 LOCK-A2A-08 verbatim 5필드 분리 인용 (AUTHORITY_CHAIN.md §3 L63)

| 필드 | 값 |
|------|------|
| **LOCK ID** | `LOCK-A2A-08` |
| **항목** | Agent Mode 열거형 |
| **값** | `MANUAL\|SEMI_AUTO\|SUPERVISED_AUTO` |
| **출처** | `D2.0-05 §1.1 (ADD-009)` |
| **변경 조건** | `D2.0-05 변경 시만` |

### 9.2 MoA 기본 모드 정책

- **기본**: `SEMI_AUTO` — proposer 병렬 호출은 자동, aggregator 결과 반환 직후 사용자 승인 여부는 호출자 결정.
- **Safety-critical (Consensus 모드)**: `SUPERVISED_AUTO` 필수 — 에스컬레이션 발생 시 인간 승인 포함.
- **MANUAL**: 각 proposer 별 사용자 개별 승인 (비용/속도 저하, Phase 3 UI 설계 이월).

---

## 10. Phase 3 테스트 시나리오 (12 건)

| # | 시나리오 | 주입 방법 | 기대 결과 |
|---|----------|----------|----------|
| MOA-01 | 정상 3-proposer + Majority Voting | 3 proposer 에 동일 질의, 2 개 동일 응답 + 1 개 상이 | 다수결 채택, `aggregation_mode="majority_voting"`, `succeeded_count=3` |
| MOA-02 | 2-proposer 최소 경계 | proposer 2 개 (하한), MAJORITY_VOTING | 정상 집계, 동점 시 confidence 최고 채택 |
| MOA-03 | 5-proposer 상한 경계 | proposer 5 개 (상한), MAJORITY_VOTING | 정상 집계, 비용 ×6 게이트 경고 |
| MOA-04 | R-11-6 위반 (1-proposer) | proposer 1 개로 생성자 호출 | `ValueError: R-11-6 violation: proposer count 1 < 2` |
| MOA-05 | R-11-6 위반 (6-proposer) | proposer 6 개로 생성자 호출 | `ValueError: R-11-6 violation: proposer count 6 > 5` |
| MOA-06 | proposer 1 실패, 2 성공 | 3 proposer 중 1 개 exception | Degraded 집계 (2 성공), confidence -0.1, `failed_count=1` |
| MOA-07 | proposer 전원 실패 | 3 proposer 전원 timeout | `ABORT_ALL_FAILED` + I-20 에스컬레이션 페이로드, `partial_result=None` |
| MOA-08 | Circuit Breaker 개방 | 특정 proposer 3 회 연속 실패 | 해당 proposer 의 CB OPEN, 다음 MoA 호출 시 즉시 skip, 60 초 후 HALF-OPEN |
| MOA-09 | Circuit Breaker 복구 | CB OPEN 후 60 초 + 에이전트 복구 | HALF-OPEN 1 건 성공 → CLOSED 복귀 |
| MOA-10 | Weighted Average 수치 집계 | 5 proposer 에 "1~10 점수" 질의, 상이 점수 반환 | 가중 평균 계산, confidence × historical_success 가중 |
| MOA-11 | Consensus 전원 동의 | 3 proposer 동일 응답 | Consensus 성공, `final_answer` 채택 |
| MOA-12 | Consensus 불일치 | 3 proposer 중 1 개 상이 | Consensus 실패, I-20 에스컬레이션 `CONSENSUS_DISAGREEMENT`, `ESCALATE_TO_HUMAN` |

---

## 11. LOCK 인용 표 (5필드 분리 강제 — 3-5/3-6/3-7/3-8 #2a 선례 계승)

| LOCK ID | 항목 | 값 | 출처 | 변경 조건 |
|---------|------|-----|------|----------|
| LOCK-A2A-01 | JSON-RPC 2.0 프로토콜 버전 | `"jsonrpc": "2.0"` | Google A2A Spec | 스펙 업데이트 시 검토 |
| LOCK-A2A-02 | Task 상태 열거형 | `submitted\|working\|input-required\|completed\|failed\|canceled` | Google A2A Spec | 스펙 업데이트 시 검토 |
| LOCK-A2A-05 | 컨텍스트 윈도우 한계 | 모델별 max_tokens 준수, 초과 시 압축 | D2.0-05 §12.13 | 모델 변경 시 갱신 |
| LOCK-A2A-08 | Agent Mode 열거형 | `MANUAL\|SEMI_AUTO\|SUPERVISED_AUTO` | D2.0-05 §1.1 (ADD-009) | D2.0-05 변경 시만 |
| LOCK-A2A-09 | Circuit Breaker 연속 실패 임계 | 3회 → OPEN, 60초 후 HALF-OPEN | D2.0-05 §4.4 (ADD-072) | D2.0-05 변경 시만 |

- LOCK-A2A-01 적용 위치: §4.2 `send_task` JSON-RPC 2.0 전제
- LOCK-A2A-02 적용 위치: §4.2 TaskResult 반환 상태, §7.2 proposer 실패 분류
- LOCK-A2A-05 적용 위치: §8 aggregator 단계 컨텍스트 윈도우 제어
- LOCK-A2A-08 적용 위치: §9 MoA 기본 모드 SEMI_AUTO / Consensus SUPERVISED_AUTO
- LOCK-A2A-09 적용 위치: §7.1 Circuit Breaker 연동 (proposer 별 독립 관리)

---

## 12. 세션 간 인터페이스 cross-check

| 항목 | 대상 산출물 | 일치 항목 |
|------|------------|----------|
| `MixtureOfAgents` 클래스 | 상세명세 §5.3 L440~L469 | `proposer_agents: list[str]` / `aggregator_agent: str` / `asyncio.gather` / `metadata={"pattern":"moa","proposal_count":N}` verbatim |
| `TaskRequest` / `TaskResult` / `Message` / `TextPart` | 상세명세 §2.2 | 공용 구조 재사용, 본 문서에서 재정의 금지 |
| `AgentSubState.agent_delegating` | `conversation_state_machine.md` §5.2 | proposer 병렬 호출 시 상태 식별자 verbatim |
| `StreamTransition` (proposer 스트리밍 시) | `streaming_sse.md` §5 agent_streaming T1~T6 | TS-14 MoA proposer 병렬 스트림 시나리오 연계 |
| `TransitionEvent` (MoA 완료 → `response_ready` 전이) | `conversation_state_machine.md` §4.3 T#45 | `trigger_type=MOA_COMPLETE`, delegation_depth ≤ 3 |
| `PushNotificationConfig` (aggregator 완료 Push) | `push_notifications.md` §8 | MoA 실행이 장시간인 경우 aggregator 완료 Push 알림 경로 |
| Circuit Breaker 임계값 | `streaming_sse.md` §6.1 + `push_notifications.md` §6.2 + `metrics_dashboard.md` | LOCK-A2A-09 3 회 / 60 초 verbatim 전역 일관 |
| MoA 비용 매트릭스 | `05_monitoring/metrics_dashboard.md` | `total_cost_usd` / `moa.proposal_count` / `moa.aggregation_mode` OTel span attributes |
| Session 컨텍스트 공유 | `multi_turn_sessions.md` §7.2 agent_delegating 재귀 ≤3 | MoA 호출이 중첩될 경우 `delegation_depth` 누적, LOCK-A2A-07 상한 3 |
| delegation_depth 상한 3 | `multi_turn_sessions.md` + `conversation_state_machine.md` | LOCK-A2A-07 JWT delegation chain 최대 깊이 3 교차 준수 |

---

## 13. 변경 이력

| 날짜 | 변경자 | 내용 |
|------|--------|------|
| 2026-04-22 | STAGE 7 3-8 STEP_B #2b (parent-executed) | V2-Phase 2 NEW 최초 작성 (P2-4 MoA 패턴 세션, exit gate "MoA 완성" 직접 충족). R-11-6 proposer 2/5/3 verbatim + §C.1 MoA 실행 흐름 5 단계 verbatim + 상세명세 §5.3 MixtureOfAgents Python 정본 재인용 + 3 집계 모드 (Majority Voting 기본 / Weighted Average advanced / Consensus safety-critical) + LOCK-A2A-09 CB proposer 별 독립 관리 + 비용 매트릭스 ×3~×6 + MoAEscalationPayload + 12 MOA-NN 테스트 시나리오 + peer cross-ref 10 지점 실체화 |
