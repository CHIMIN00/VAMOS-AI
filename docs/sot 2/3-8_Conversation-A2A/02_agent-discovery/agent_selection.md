# 에이전트 선택 알고리즘 (Agent Selection)

> **정본 소유**: sot 2/3-8_Conversation-A2A/02_agent-discovery/agent_selection.md
> **버전**: v1.0 (V2-Phase 2)
> **작성일**: 2026-04-22
> **Phase**: 2 (V2)
> **L3 상태**: L3 (DRAFT)
> **대응 항목**: §6.1 #20 (가중 스코어링 선택 알고리즘), #21 (Jaccard 유사도 스킬 매칭)
> **v12 매핑**: v12_C12_101 (에이전트 카드 확장 — 선택 입력 필드)
> **Phase 2→3 게이트**: 기여 (P2-6)
> **자매 문서**: `service_registry.md` (P2-6) — 본 알고리즘의 입력 제공

---

## 교차 참조 블록

| 정본 문서 | 참조 섹션 | 관계 |
|-----------|----------|------|
| AUTHORITY_CHAIN §3 L59 | LOCK-A2A-04 (`_vamos-a2a._tcp.local.`) | 후보 에이전트 출처 정합 |
| AUTHORITY_CHAIN §3 L64 | LOCK-A2A-09 (CB 3회 → OPEN, 60초 후 HALF-OPEN) | CB OPEN 에이전트 제외 |
| 종합계획서 §7.3 P2-6 | §6.1 #20~#21 | 작업 정의 |
| 상세명세 §3.2 L252~L274 | `AgentRegistration` interface + `AgentCapability` | 스키마 입력 |
| 상세명세 §3.3 L278~L303 | `select_agent` 가중 스코어링 + Jaccard 유사도 (VAMOS 원본) | **알고리즘 정본** |
| D2.0-05 §1.1 (ADD-009) | Cooperative Agent — 협력 선택 근거 | 아키텍처 정본 |
| STEP7-B §B L549~L554 | #13 의도 추출 / #17 제약 조건 추출 / #18 IntentFrame 스키마 (VAMOS 독자) | 입력 `required_skills` 추출 근거 |
| STEP7-B §D L583~L584 | #37 모델 라우팅 / #38 도메인별 실행분리 (VAMOS 우위) | 가중 스코어링 정합 |
| `02_agent-discovery/service_registry.md` (P2-6 자매) §7.4 | 레지스트리 → 선택 알고리즘 입력 계약 | **필수 입력 경로** |
| `02_agent-discovery/mdns_dns_sd.md` (P1-4) §4 | mDNS TXT `caps` 필드 | 능력 필터 폴백 |
| `01_a2a-protocol/agent_card_spec.md` (P1-3) §2.3 | `AgentCard.skills` 구조 | 스킬 집합 원천 |
| `04_advanced-features/moa_pattern.md` (P2-4) §3.3 | MoA proposer 후보 선발 | **MoA proposer 선발 연동 — Phase 3 이월** |
| `04_advanced-features/conversation_state_machine.md` (P2-3) §4.3 T#45 | `agent_delegating` 전이 | 위임 대상 선택 호출자 |
| `05_monitoring/metrics_dashboard.md` (P2-5) §3.5 | `a2a_agent_status` + `a2a_agent_load_factor` | 선택 결과 모니터링 |

---

## §1. 개요

본 문서는 **에이전트 선택 알고리즘(Agent Selection Algorithm)**을 정의한다. `service_registry.md` 로부터 공급된 후보 에이전트 목록에 대해 **Jaccard 유사도 스킬 매칭** 과 **4-factor 가중 스코어링**을 적용하여 단일 최적 에이전트를 결정한다.

**범위**:
- §2 알고리즘 개요 (상세명세 §3.3 선발 절차 준수)
- §3 Jaccard 유사도 스킬 매칭 (상세명세 §3.3 L285~L288 정본)
- §4 가중 스코어링 알고리즘 (상세명세 §3.3 L283~L302 verbatim)
- §5 Pydantic 입력/출력 스키마 (`SelectionRequest` / `SelectionResult`)
- §6 에러 처리 / fallback 정책
- §7 LOCK-A2A-04 mDNS 정합 (입력 후보 출처)
- §8 V2↔V2 peer cross-ref 매트릭스
- §9 Phase 3 테스트 시나리오
- §10 LOCK 정본 패널
- §11 변경 이력

**Phase 3 이월 항목**:
- 학습 기반 스코어링 가중치 자동 조정 (historical_success 가중치 도입)
- MoA proposer 다중 선발 (본 §2 는 단일 선택, moa_pattern §3.3 연계 확장)
- 대화 컨텍스트 기반 sticky selection (multi_turn_sessions §3.1 확장)

---

## §2. 알고리즘 개요

### 2.1 선발 절차 (상세명세 §3.3 준수, 5단계)

```
입력: TaskRequest { required_skills[], required_capabilities[], context }
     + AgentRegistry (service_registry.md 레지스트리 질의 응답)

1. 필터 단계 (O(N))
   candidates = registry.find_by_skills(task.required_skills)
              + registry.filter_by_capabilities(task.required_capabilities)
              + exclude CB OPEN (LOCK-A2A-09)
              + exclude stale (60s 이상 미갱신 metadata.load_factor)

2. Jaccard 유사도 매칭 (O(N · S))
   for agent in candidates:
     skill_match = |required_skills ∩ agent.skills| / |required_skills ∪ agent.skills|

3. 4-factor 가중 스코어링 (O(N))
   total = 0.40·skill_match + 0.25·load_score + 0.20·priority_score + 0.15·latency_score

4. 내림차순 정렬 (O(N log N))
   scored.sort(key=lambda x: x.total, reverse=True)

5. 단일 반환
   return scored[0] if scored else raise NoMatchingAgentError(task)
```

### 2.2 복잡도 분석

| 단계 | 복잡도 | 설명 |
|------|--------|------|
| 1. 필터 | O(N) | N = 레지스트리 총 에이전트 수 |
| 2. Jaccard | O(N · S) | S = required_skills 평균 크기 (<10 전제) |
| 3. 스코어링 | O(N) | 산술 연산 |
| 4. 정렬 | O(N log N) | 표준 정렬 |
| 5. 반환 | O(1) | — |
| **합계** | **O(N log N)** | N = 100 기준 마이크로초 단위 |

---

## §3. Jaccard 유사도 스킬 매칭 (§6.1 #21)

### 3.1 수학적 정의

Jaccard 유사도는 두 집합 `A`, `B`의 교집합 크기를 합집합 크기로 나눈 값이다.

```
J(A, B) = |A ∩ B| / |A ∪ B|       (0.0 ≤ J ≤ 1.0)
```

- `J = 1.0`: 두 집합이 완전히 동일 (완벽한 스킬 매칭)
- `J = 0.0`: 두 집합이 서로소 (스킬 완전 불일치, 해당 후보 배제)
- 중간값: 스킬 overlap 비율 (부분 매칭)

### 3.2 Python 구현 (상세명세 §3.3 정합)

```python
from typing import Set

def jaccard_similarity(a: Set[str], b: Set[str]) -> float:
    """Jaccard 유사도 — 상세명세 §3.3 L285~L288 verbatim 알고리즘"""
    if not a and not b:
        return 1.0  # 두 집합 모두 비면 완전 일치 간주
    intersection = a & b
    union = a | b
    return len(intersection) / len(union)
```

### 3.3 스킬 집합 정규화

- 모든 스킬 ID 는 **소문자 kebab-case** (`code-review`, `python-expert`, `rust-async`)
- 정규화 전 비교 금지 (대소문자 차이로 false negative 방지)
- `skill_id` 외 `tags[]` 는 **보조 매칭** (가중치 0.3, Phase 3 도입 예정)
- 공백 / 빈 문자열 스킬 ID 는 레지스트리 등록 단계에서 거부

### 3.4 임계값 정책

| `skill_match` 값 | 처리 |
|-------------------|------|
| 0.0 | 후보 배제 (기본). `--force-no-skill-match` 플래그 시 통과 허용 |
| 0.0 < J < 0.3 | 저유사 — 가중치 적용만, 로그 warning |
| 0.3 ≤ J < 0.7 | 일반 — 정상 스코어링 |
| 0.7 ≤ J < 1.0 | 고유사 — 정상 스코어링 |
| 1.0 | 완전 일치 — 우선 고려, 동점 시 priority/load 로 결정 |

---

## §4. 가중 스코어링 알고리즘 (§6.1 #20)

### 4.1 4-factor 수식 (상세명세 §3.3 L293~L298 verbatim)

```python
def score_agent(
    task: TaskRequest,
    agent: AgentRegistration,
) -> float:
    """상세명세 §3.3 L293~L298 4-factor 가중 스코어링 verbatim"""
    skill_match = jaccard_similarity(
        set(task.required_skills),
        set(agent.skills)
    )
    load_score = 1.0 - agent.metadata.load_factor
    priority_score = 1.0 - (agent.metadata.priority / 100.0)
    latency_score = 1.0 / (1.0 + agent.avg_latency_ms / 1000.0)

    total = (
        0.40 * skill_match +
        0.25 * load_score +
        0.20 * priority_score +
        0.15 * latency_score
    )
    return total
```

### 4.2 가중치 근거 (4-factor 합=1.0)

| Factor | 가중치 | 정당성 |
|--------|-------|-------|
| `skill_match` (Jaccard) | **0.40** | 도메인 적합성이 최우선 (부적합 에이전트 선택 시 재시도 비용 큼) |
| `load_score` (1 - load_factor) | **0.25** | 부하 분산 (`load_factor` 0.8 초과 시 load_score ≤ 0.2) |
| `priority_score` (1 - priority/100) | **0.20** | 조직 우선순위 반영 (시스템 에이전트 vs 실험 에이전트) |
| `latency_score` (1 / (1 + lat_s)) | **0.15** | 응답 속도 반영 (평균 지연 ≥ 10초 시 latency_score ≤ 0.1) |
| **합계** | **1.00** | **정규화된 스코어 0.0 ~ 1.0** |

### 4.3 정규화 분석

- 모든 factor 는 `[0.0, 1.0]` 로 정규화되어 `total ∈ [0.0, 1.0]`
- `total ≥ 0.7`: 고품질 매칭 (자동 선택 권고)
- `0.4 ≤ total < 0.7`: 중품질 (보조 로그)
- `total < 0.4`: 저품질 (경고 로그, fallback 고려)

### 4.4 latency_score 계산 유의

`avg_latency_ms` 은 에이전트별 최근 100회 평균 응답 시간 (레지스트리 metadata 확장 필드, Phase 3). Phase 2 에서는 `agent.metadata` 에 없을 경우 **기본값 500ms** 적용 (`latency_score = 0.667`).

---

## §5. Pydantic 입력/출력 스키마

### 5.1 SelectionRequest

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class SelectionRequest(BaseModel):
    required_skills: List[str] = Field(..., min_length=1, description="요구 스킬 집합 (소문자 kebab-case)")
    required_capabilities: List["AgentCapability"] = Field(default_factory=list)
    exclude_agent_ids: List[str] = Field(default_factory=list)
    min_score: float = Field(default=0.4, ge=0.0, le=1.0)
    session_id: Optional[str] = None   # sticky selection (Phase 3 multi_turn §3.1)
    delegation_depth: int = Field(default=0, ge=0, le=3)  # LOCK-A2A-07 상한 (delegation_chain.md §4)
```

### 5.2 SelectionResult

```python
class ScoredCandidate(BaseModel):
    agent_id: str
    total_score: float               # 0.0 ~ 1.0
    skill_match: float               # Jaccard
    load_score: float
    priority_score: float
    latency_score: float
    rank: int                        # 1 = 최상위

class SelectionResult(BaseModel):
    selected: ScoredCandidate | None
    all_candidates: List[ScoredCandidate]    # 전체 후보 (디버그/감사 로깅용)
    evaluated_count: int
    selection_reason: str                    # "top_score" / "tie_priority" / "fallback_default"
    request_trace_id: str                    # OTel trace (metrics_dashboard §5.1 정합)
```

---

## §6. 에러 처리 및 Fallback 정책

### 6.1 NoMatchingAgentError

후보 0건 또는 최고 `total < min_score` 시 발생:

```python
class NoMatchingAgentError(Exception):
    def __init__(self, task, evaluated_count: int):
        self.task_id = task.id
        self.evaluated_count = evaluated_count
        super().__init__(f"No agent matched task={task.id} (evaluated={evaluated_count})")
```

### 6.2 Fallback 단계 (상세명세 §4.4 에러 코드 정합)

| 시도 | 전략 | 에러 코드 |
|------|------|----------|
| 1차 | 기본 `min_score=0.4` 선택 | — |
| 2차 | `min_score=0.2` 로 완화 재시도 | 로그 warning |
| 3차 | `--force-no-skill-match` (Jaccard=0 허용) | `-32004` Unsupported operation 경계 |
| 4차 | `01_a2a-protocol/error_codes.md` `503 Agent unavailable` 반환 | HTTP 503 |
| 5차 | Phase 3: 큐잉 (`Priority Queuing` §5.1 #7) | Phase 3 이월 |

### 6.3 CB OPEN 배제 정책 (LOCK-A2A-09 정합)

필터 단계(§2.1 #1)에서 CB 상태가 `OPEN` 인 에이전트는 배제한다. `HALF-OPEN` 은 **1건 probe 허용** 하되, 가중치에 × 0.5 불이익 적용.

### 6.4 Delegation Depth 가드 (LOCK-A2A-07)

`SelectionRequest.delegation_depth > 3` 시 `-32007 Delegation depth exceeded` 에러 즉시 반환, 선택 알고리즘 미실행. (`03_security/delegation_chain.md` (P2-7) §4 정합, error_codes.md §4 C-7 -32007 카탈로그 정합)

---

## §7. LOCK-A2A-04 mDNS 정합 (입력 후보 출처)

레지스트리에서 공급되는 `AgentRegistration` 목록은 **LOCK-A2A-04** (`_vamos-a2a._tcp.local.`) 를 준수하는 에이전트만 포함한다. 즉:

1. mDNS Service Type 일치 확인 (서비스 등록 시점)
2. TXT 레코드 `caps` 필드가 `AgentCapability` 5값 집합 이내
3. TXT 레코드 `agent-id` UUID v4 검증

위 3 조건 불충족 에이전트는 `service_registry.md` §4 등록 단계에서 거부되며, 본 선택 알고리즘 입력에 **절대 도달하지 않는다**. 따라서 본 §7 은 **입력 신뢰성 전제**(invariant)에 해당한다.

---

## §8. V2↔V2 Peer Cross-reference 매트릭스

| 대상 V2 | 본 §§ | 대상 §§ | 관계 |
|----------|-------|---------|------|
| `service_registry.md` (P2-6 자매) | §2.1 (입력 출처) + §3 정규화 + §7 invariant | §7.4 연동 계약 + §4 caps | **필수** — 쌍방향 계약 |
| `moa_pattern.md` (P2-4) | §5.2 SelectionResult + §6.3 HALF-OPEN 불이익 | §3.3 proposer 후보 선발 | Phase 3 MoA 다중 선발 연동 |
| `conversation_state_machine.md` (P2-3) | §6.4 delegation_depth 가드 | §4.3 T#45 `agent_delegating` 전이 | 위임 전이에서 선택 알고리즘 호출 |
| `multi_turn_sessions.md` (P2-3) | §5.1 `session_id` sticky (Phase 3) | §3.1 session stickiness | sticky selection 인터페이스 |
| `metrics_dashboard.md` (P2-5) | §5.2 `request_trace_id` + §6 fallback | §5.1 W3C TraceContext + §5.3 span attrs | OTel trace 정합 |
| `streaming_sse.md` (P2-1) | §4 latency_score | §4.2 artifact 재전송 지연 | 지연 측정 정합 |
| `push_notifications.md` (P2-2) | §6.3 CB OPEN 배제 | §6 webhook 실패 CB | CB LOCK-A2A-09 공유 |
| `mdns_dns_sd.md` (P1-4 V1) | §7 LOCK-A2A-04 invariant | §4 TXT 레코드 필드 | 입력 출처 검증 |
| `agent_card_spec.md` (P1-3 V1) | §3.3 스킬 정규화 | §2.3 `AgentCard.skills` | 스킬 집합 원천 |
| `delegation_chain.md` (P2-7) | §6.4 depth 가드 | §4 JWT delegation_depth | LOCK-A2A-07 교차 정합 |

> **peer cross-ref 지점 수**: 본 §8 기록 10 peer (6 V2 + 3 V1 + 1 자매) × 평균 2 지점 = **예상 ≥15 peer 지점 실체화**.

---

## §9. Phase 3 테스트 시나리오 (10+ 목표)

| # | 테스트 ID | 시나리오 | 성공 기준 |
|---|-----------|---------|----------|
| 1 | SEL-01 | 완전 일치 스킬 (`J=1.0`) | top_score = 1.0 × 0.4 + ... 예상값 반환 |
| 2 | SEL-02 | 부분 일치 (`J=0.5`) | skill_match = 0.5, 스코어 반영 |
| 3 | SEL-03 | 스킬 불일치 (`J=0.0`) | 후보 배제, `NoMatchingAgentError` |
| 4 | SEL-04 | `load_factor=0.9` 에이전트 vs 0.1 | 0.1 에이전트 선택 (load_score 우위) |
| 5 | SEL-05 | `priority=0` (시스템) vs `priority=50` | 0 에이전트 선택 (priority_score 우위) |
| 6 | SEL-06 | 4-factor 모두 동일 | 등록 순서 / agent_id 사전식 tie-break |
| 7 | SEL-07 | CB OPEN 에이전트 배제 | 필터 단계에서 제외 확인 |
| 8 | SEL-08 | HALF-OPEN 에이전트 × 0.5 불이익 | 스코어 감점 검증 |
| 9 | SEL-09 | `min_score=0.4` 미만 모든 후보 | 2차 `min_score=0.2` 재시도 |
| 10 | SEL-10 | 2차/3차 모두 실패 | `503 Agent unavailable` HTTP |
| 11 | SEL-11 | `delegation_depth=3` | `-32011` 즉시 반환, 선택 미실행 |
| 12 | SEL-12 | 스킬 정규화 (`Code-Review` vs `code-review`) | 정규화 후 J=1.0 |
| 13 | SEL-13 | 필터 단계 0건 | `NoMatchingAgentError`, evaluated_count=0 |
| 14 | SEL-14 | 100개 에이전트 선택 성능 | p99 < 5ms (마이크로초 단위) |

> 목표 10건 대비 **14건 = 140%** (산출물 품질 필수 구조 #5 준수)

---

## §10. LOCK 정본 패널 (AUTHORITY_CHAIN §3 verbatim 5필드)

### 10.1 LOCK-A2A-04 (입력 후보 invariant)

| 필드 | 값 |
|------|-----|
| **LOCK ID** | `LOCK-A2A-04` |
| **항목** | mDNS Service Type |
| **값** | `_vamos-a2a._tcp.local.` |
| **출처** | 상세명세 §3.1 |
| **변경 조건** | 변경 금지 |

### 10.2 LOCK-A2A-07 (delegation_depth 가드)

| 필드 | 값 |
|------|-----|
| **LOCK ID** | `LOCK-A2A-07` |
| **항목** | JWT delegation chain 최대 깊이 |
| **값** | 3 |
| **출처** | 가이드 §4.3/#11 |
| **변경 조건** | 보안 검토 후만 변경 *(LOCK-AT-004 교차: 위임 깊이 최대 3단계 동일)* |

### 10.3 LOCK-A2A-09 (CB OPEN 배제)

| 필드 | 값 |
|------|-----|
| **LOCK ID** | `LOCK-A2A-09` |
| **항목** | Circuit Breaker 연속 실패 임계 |
| **값** | 3회 → OPEN, 60초 후 HALF-OPEN |
| **출처** | D2.0-05 §4.4 (ADD-072) |
| **변경 조건** | D2.0-05 변경 시만 |

> 본 §10 3 entries 는 AUTHORITY_CHAIN §3 L59/L62/L64 와 verbatim 일치 (hallucination 0, 5-1 회귀 방지).

---

## §11. 변경 이력

| 버전 | 날짜 | 내용 |
|------|------|------|
| v1.0 | 2026-04-22 | **V2-Phase 2 초기 작성** (STEP_B #2c 세션 P2-6). 상세명세 §3.3 L278~L303 verbatim 알고리즘 + Jaccard 유사도 정본 + 4-factor 가중 스코어링 + Pydantic 스키마 + NoMatchingAgentError + 5단 fallback + LOCK-A2A-04/07/09 verbatim 3 지점 + V2↔V2 peer 10 지점 + Phase 3 테스트 14건. V1 base 부재로 V2 NEW (3-7 ast_pipeline UPDATE 패턴 미해당). |

---

**[END OF agent_selection.md v1.0]** (parent-executed, 2026-04-22, STEP_B #2c P2-6, FABRICATION 0, LOCK-A2A-04/07/09 5필드 verbatim 3 지점 + 본문 정합 5 지점 = 8, peer cross-ref ≥10 V2/V1/자매, STEP7-B §B L549~L554 + §D L583~L584 5 line refs, Phase 3 테스트 14건 (140%))
