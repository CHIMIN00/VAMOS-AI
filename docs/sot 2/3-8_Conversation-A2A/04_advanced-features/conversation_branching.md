# Conversation Branching — 대화 분기/병합 (다중 경로 탐색)

> **도메인**: #11 Conversation-A2A (TIER3-DOMAIN-08)
> **서브폴더**: `04_advanced-features/`
> **V3 산출물**: P4-1 (Phase 4 #1, P1) — P3-1 forward-defined 정본 승급
> **작성일**: 2026-06-03
> **Status**: V3-Phase 4 APPROVED (production-ready)
> **상세명세 근거**: §2.1 method enum, §2.2 TaskStatusEvent/TaskArtifactEvent, §6.1 #42 Conversation Branching
> **종합계획서 근거**: §6.1 구현 항목 #42, §7.3 P3-1 블록 (L1604~L1654), §7.4 P4-1 블록 (L2000~L2046)
> **STEP7-B 상위 SoT**: `#70 대화 분기 (Fork)` (L992, ❌ 미적용 — VAMOS 신규 구현), `S7B-023` (L1046), cost 표 (L1163)
> **LOCK 직접 보호**: LOCK-A2A-02 Task 상태 열거형 / LOCK-A2A-05 컨텍스트 윈도우 한계
> **LOCK 간접 참조**: LOCK-A2A-09 Circuit Breaker (분기 N>3 시 OPEN cascade)

---

## 교차 참조

- `_index.md` — 04_advanced-features/ 항목 #12 Conversation Branching (대화 분기/병합 P1, Phase 3→4 APPROVED)
- `multi_turn_sessions.md` — sessionId 기반 부모 세션에서 분기 시 새 session_id 발급, Redis 세션 캐시 정합
- `conversation_state_machine.md` — 분기 생성 시 부모 세션 상태 스냅샷 (9 상태 머신 §5.2), 분기 머지 시 상태 재구성
- `streaming_sse.md` — 분기별 독립 SSE 스트림 (§3.2 `artifact_chunk` last_chunk 분할), 분기 progress 이벤트 집약
- `moa_pattern.md` — MoA proposer 병렬 탐색을 분기 트리로 표현 (N proposer = N branch 매핑)
- `priority_queuing.md` — 분기 N개에 대한 작업 큐잉 시 우선순위 정책 (P4-2 cross-ref)
- `01_a2a-protocol/artifact_chunking.md` — 분기 트리 스냅샷 대용량 전송 시 청크 분할 (P4-3 cross-ref)
- `03_security/audit_logging.md` — 분기 생성/머지 권한 변경 감사 로그
- `05_monitoring/metrics_dashboard.md` — 분기 깊이/머지 충돌율 메트릭 소비
- `05_monitoring/vbs12_benchmark.md` — 시나리오 8 (분기·머지) 측정 대상 (P4-6 cross-ref)
- 상위 아키텍처 정본: `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` §12.13 컨텍스트 관리 (LOCK-A2A-05 정본), §4.4 Circuit Breaker (LOCK-A2A-09 정본)
- 상위 가이드 (벤치마크 참조 전용, CLF-A2A-003 RESOLVED): STEP7-B §H L992 #70 대화 분기 (Fork) (GPT only ✅, Claude/Gemini/Perplexity/Kimo/DeepSeek/Grok/Mistral/VAMOS ❌ → VAMOS 신규 구현 차별화)

---

## 1. 개요

### 1.1 목적

단일 대화 세션에서 임의의 메시지 지점을 분기점(fork point)으로 삼아 **독립적인 다중 대화 경로**를 동시에 탐색하고, 필요 시 분기를 부모 경로에 **병합(merge)**하는 기능을 정의한다. Git-like 대화 트리 모델을 채택하되, A2A Task 의 상태 무결성(LOCK-A2A-02)과 컨텍스트 윈도우 한계(LOCK-A2A-05)를 준수한다. STEP7-B #70 "대화 분기 (Fork)" 는 GPT 만 지원하고 VAMOS 미적용(❌)이던 항목으로, 본 V3 가 VAMOS 신규 구현으로 차별화한다.

### 1.2 범위

- 분기 트리 자료구조 정의 (`parent_id`, `branch_id`, `message_hash`)
- 분기 생성 API (`conversation/branch/create`) — 컨텍스트 inherit / fresh 선택
- 3-way merge 알고리즘 (common_ancestor + branch_a + branch_b → vector_clock 우선)
- 분기 비용 정책 (분기 N개에 대한 토큰 비용 합산 + LOCK-A2A-09 cascade)
- 분기 권한 RBAC (§14 W7 자율 레벨 오용 리스크 대응)
- 분기 트리 영속화 (SQLite 로컬 / PostgreSQL 분산)

### 1.3 범위 외 (Phase 5+ 이월)

- 분기 트리 GUI 시각화 — 6-1 UI-UX-System 또는 별도 Phase 5 V4 트랙
- 자동 분기 추천 (ML 기반 유망 경로 예측) — Phase 5 이월
- 분기 간 cherry-pick (부분 메시지 이식) — 3-way merge 안정화 후 검토

---

## 2. 분기 트리 자료구조 (D1)

### 2.1 핵심 식별자

| 필드 | 타입 | 설명 |
|------|------|------|
| `branch_id` | str (`branch-<uuid>`) | 분기 고유 식별자. 루트 분기는 `branch-root` |
| `parent_id` | str \| null | 부모 분기 `branch_id`. 루트는 null |
| `fork_point_message_id` | str | 분기가 시작된 부모 경로의 메시지 ID |
| `message_hash` | str (sha256) | 분기점까지의 메시지 시퀀스 누적 해시 (무결성 검증·중복 분기 탐지) |
| `session_id` | str | 분기에 발급된 새 sessionId (multi_turn_sessions 정합) |
| `vector_clock` | dict[str,int] | 분기별 논리 시계 (머지 시 인과 순서 결정) |

### 2.2 BranchRequest (Input Schema)

```python
from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field


class BranchRequest(BaseModel):
    """conversation/branch/create 요청. JSON-RPC 2.0 params (LOCK-A2A-01)."""

    parent_session_id: str = Field(..., description="분기 대상 부모 세션 sessionId")
    fork_point_message_id: str = Field(..., description="분기 시작 메시지 ID")
    fork_reason: str = Field(..., max_length=512, description="분기 사유 (감사 로그 기록)")
    inherit_context_window: bool = Field(
        default=True,
        description="True=부모 컨텍스트 상속, False=fresh 시작 (LOCK-A2A-05 압축 트리거 영향)",
    )
    branch_label: Optional[str] = Field(default=None, description="사람이 읽는 분기 이름")
```

### 2.3 메시지 트리 노드

분기 트리는 메시지를 노드로 하는 DAG 가 아닌 **순수 트리(tree)** 로 모델링한다. 머지는 트리를 변형하지 않고 별도의 merge-result 메시지를 부모 경로에 append 하는 방식으로 인과 순서를 단순화한다(순환 차단). 각 분기는 부모로부터 `fork_point_message_id` 까지의 메시지를 **공유(shallow reference)** 하고, 이후 메시지만 독립 보유한다.

---

## 3. BranchResponse (Output Schema, D2)

```python
class CostEstimate(BaseModel):
    inherited_tokens: int          # 상속된 컨텍스트 토큰
    projected_tokens_per_turn: int # 분기 턴당 예상 토큰
    branch_count_in_session: int   # 현재 세션 내 활성 분기 수
    cumulative_cost_usd: float     # 분기 N개 합산 비용


class BranchResponse(BaseModel):
    """conversation/branch/create 응답."""

    branch_id: str
    parent_id: str
    new_session_id: str
    message_tree_snapshot: str = Field(..., description="분기 직후 트리 스냅샷 (artifact_chunking 전송 가능)")
    cost_estimate: CostEstimate
    state: Literal["submitted", "working", "input-required", "completed", "failed", "canceled"]
    # state 는 LOCK-A2A-02 열거형만 허용 — 분기 직후 기본 submitted
```

- `state` 필드는 **LOCK-A2A-02 Task 상태 열거형** (`submitted|working|input-required|completed|failed|canceled`) 만 허용한다. 분기 생성 자체가 하나의 Task 로 추적되며 상태 머신 무결성을 따른다.
- `message_tree_snapshot` 이 64KB 를 초과하면 `01_a2a-protocol/artifact_chunking.md` 의 청크 분할 전송을 사용한다.

---

## 4. 분기 → 머지 알고리즘 (D3)

### 4.1 분기 생성 절차

1. `parent_session_id` + `fork_point_message_id` 검증 → 부모 경로 존재 + 해당 메시지 실존 확인.
2. 분기점까지 메시지 시퀀스의 누적 `message_hash` (sha256) 계산 → 동일 해시의 활성 분기가 있으면 중복 분기로 간주하고 기존 `branch_id` 반환 (idempotency).
3. 새 `session_id` 발급 (multi_turn_sessions API) + `vector_clock` 초기화 (`{branch_id: 0}`).
4. `inherit_context_window=True` 면 부모 컨텍스트를 shallow reference 로 상속, `False` 면 시스템 프롬프트만 유지하고 fresh 시작.
5. 상속 컨텍스트가 모델 `max_tokens × 0.85` 초과 시 **LOCK-A2A-05 압축** 트리거 (초과 시 압축).

### 4.2 3-way merge 알고리즘

분기 `branch_a` 를 부모(또는 `branch_b`)에 병합할 때 공통 조상(common ancestor)을 기준으로 3-way merge 를 수행한다.

```
def merge_branches(branch_a, branch_b):
    ancestor = lowest_common_ancestor(branch_a, branch_b)  # fork_point 기반
    delta_a = messages_since(branch_a, ancestor)
    delta_b = messages_since(branch_b, ancestor)

    # 충돌 판정: 동일 논리 슬롯에 양측 변경이 있고 vector_clock 이 비교 불가(concurrent)
    conflicts = detect_conflicts(delta_a, delta_b)
    if conflicts:
        if auto_resolvable(conflicts):       # 비중첩 변경 → 순차 append
            return auto_merge(ancestor, delta_a, delta_b)
        else:                                # 중첩 변경 → vector_clock 우선
            return clock_priority_merge(ancestor, delta_a, delta_b, conflicts)
    return fast_forward(ancestor, delta_a, delta_b)
```

- **vector_clock 우선 규칙**: 두 분기의 vector_clock 이 인과적으로 비교 가능하면(`vc_a ≤ vc_b` 또는 역) 후행 분기를 우선. 비교 불가(concurrent)면 분기 생성 timestamp 가 빠른 쪽을 base 로, 늦은 쪽을 `merge_conflict_note` 메시지로 부모 경로에 append.
- 머지 결과는 새 merge-result 메시지로 표현되어 트리를 순환시키지 않는다(LOCK-A2A-02 상태 머신 무결성 보장).

### 4.3 분기 비용 정책

- 한 세션 내 활성 분기 수가 증가하면 토큰 비용은 **분기 N개에 대해 합산**된다: `total ≈ inherited_tokens + Σ(projected_tokens_per_turn × turns_per_branch)`.
- 활성 분기 수가 **3 을 초과**하면 LOCK-A2A-09 Circuit Breaker 패턴을 비용 보호 용도로 차용하여, 신규 분기 생성을 `-32031 Branch limit exceeded` (비표준 확장 코드) 로 거절하고 운영 알림을 발생시킨다 (분기 머지 또는 abandon 후 재시도).

---

## 5. 에러 처리 (D4)

| 코드 | 상황 | 복구 |
|------|------|------|
| `-32602` | 분기 invalid (fork_point 없음 / 부모 세션 미존재) | 400 Invalid params, 클라이언트 재요청 |
| `-32006` | 컨텍스트 윈도우 초과 (상속 컨텍스트 max_tokens 초과) | LOCK-A2A-05 압축 후 재시도, 압축 불가 시 `inherit_context_window=False` 안내 |
| `-32600` | 권한 거부 (분기 생성 RBAC 미충족) | 403 Forbidden, audit_logging 기록 |
| `-32031` | Branch limit exceeded (활성 분기 > 3, 비표준 확장) | LOCK-A2A-09 cascade, 머지/abandon 후 재시도 |
| `-32032` | Merge conflict unresolvable (비표준 확장) | `merge_conflict_note` 반환 + 사용자 수동 해소 유도 |

```json
{
  "trace_id": "trace-uuid",
  "error": { "code": "-32031", "message": "Branch limit exceeded", "source": "conversation_branching.cost_guard" },
  "context": { "session_id": "sess-uuid", "active_branches": 4, "limit": 3 },
  "recovery": { "strategy": "merge_or_abandon", "next_attempt_after_s": 0 }
}
```

---

## 6. 의존성 (D5)

| 대상 | 방향 | 내용 |
|------|------|------|
| `multi_turn_sessions.md` | ← (소비) | 새 session_id 발급, Redis 세션 캐시 |
| `conversation_state_machine.md` | ← (소비) | 부모 세션 상태 스냅샷/재구성 |
| SQLite / PostgreSQL | → (영속화) | 분기 트리 저장 (§7.3 영속화 매트릭스) |
| Redis | → (캐시) | 활성 분기 세션 캐시 (TTL 1h) |
| `01_a2a-protocol/artifact_chunking.md` | ← (소비) | 트리 스냅샷 64KB 초과 시 청크 전송 |

### 6.1 분기 트리 영속화 매트릭스

| 백엔드 | 적합 환경 | 트레이드오프 |
|--------|----------|------------|
| SQLite | 로컬 단일 노드 / 데스크톱 | 무설정, 동시성 제한, 단일 파일 |
| PostgreSQL | 분산 멀티 노드 / 클라우드 | 동시성·복제 우수, 운영 비용 |

- 분기 트리는 `branches(branch_id PK, parent_id, session_id, message_hash, vector_clock JSONB, created_at, status)` 스키마로 영속화하며 `parent_id` 에 인덱스를 둔다.

---

## 7. 성능 SLA (D6)

| 메트릭 | 목표 | 측정 |
|--------|------|------|
| 분기 생성 P99 | < 50ms | vbs12_benchmark 시나리오 8 |
| 머지 P99 | < 100ms | vbs12_benchmark 시나리오 8 |
| 분기 깊이 상한 | ≤ 10 | 깊이 초과 시 `-32031` |
| 활성 분기 수 상한 | ≤ 3 (LOCK-A2A-09 cascade) | 비용 보호 |

- 분기 생성은 메시지 shallow reference + 메타 레코드 insert 만 수행하므로 컨텍스트 복제 없이 < 50ms 를 달성한다.
- 머지는 공통 조상 탐색(O(depth)) + delta diff 가 지배적이며 깊이 ≤ 10 제약 하에서 P99 < 100ms.

---

## 8. 테스트 시나리오 (D7, CB-T01~T14)

| # | 시나리오 | 주입 | 기대 결과 |
|---|----------|------|----------|
| CB-T01 | 정상 분기 생성 (inherit) | `branch/create` inherit=True | branch_id 발급, 부모 컨텍스트 상속, state=submitted |
| CB-T02 | 정상 분기 생성 (fresh) | inherit=False | 시스템 프롬프트만 유지, fresh 시작 |
| CB-T03 | 중복 분기 idempotency | 동일 fork_point 재요청 | 기존 branch_id 반환 (신규 생성 0) |
| CB-T04 | 분기 → 머지 (fast-forward) | branch_a 변경만 존재 | 충돌 0, 부모 경로 직접 append |
| CB-T05 | 분기 → 머지 (auto, 비중첩) | branch_a/b 비중첩 변경 | auto_merge 성공 |
| CB-T06 | 분기 → 머지 (vector_clock 우선) | concurrent 중첩 변경 | clock_priority_merge + merge_conflict_note |
| CB-T07 | 머지 충돌 해소 불가 | 의도적 중첩 충돌 | `-32032` + 수동 해소 유도 |
| CB-T08 | 컨텍스트 초과 | 상속 컨텍스트 max_tokens 초과 | LOCK-A2A-05 압축 트리거 → 성공 |
| CB-T09 | 권한 거부 | RBAC 미충족 user | `-32003` 403 + 감사 로그 |
| CB-T10 | 깊이 제한 초과 | 11단계 분기 | `-32031` Branch limit |
| CB-T11 | 활성 분기 4개 (CB cascade) | 동일 세션 4번째 분기 | `-32031` + 운영 알림 |
| CB-T12 | 트리 스냅샷 대용량 | snapshot > 64KB | artifact_chunking 청크 전송 |
| CB-T13 | 분기별 독립 SSE | 분기 3개 동시 스트림 | 3 스트림 독립 유지 (streaming_sse 연계) |
| CB-T14 | MoA proposer 분기 매핑 | proposer 3 = branch 3 | 분기 트리로 표현, aggregator 머지 |

---

## 9. 보안 / RBAC (D8)

- **분기 권한 RBAC 매트릭스** (§14 W7 자율 레벨 오용 리스크 대응):

| 역할 | 분기 생성 | 분기 머지 | 분기 abandon | 타인 분기 조회 |
|------|----------|----------|-------------|--------------|
| OWNER | ✅ | ✅ | ✅ | ✅ |
| EDITOR | ✅ | ✅ (자기 분기) | ✅ (자기 분기) | ✅ |
| VIEWER | ❌ | ❌ | ❌ | ✅ |
| AGENT (SEMI_AUTO/SUPERVISED_AUTO) | 위임 OWNER 권한 내 | ❌ (사람 승인 필요) | ❌ | ✅ |

- 분기 생성/머지/abandon 은 전부 `03_security/audit_logging.md` 에 감사 로그로 기록한다 (`fork_reason`, `branch_id`, actor, timestamp).
- 6-2 Security-Governance 의 RBAC 정책(LOCK-SG-* + R-62-1)과 정합하며, 자율 에이전트의 분기 권한은 위임받은 OWNER 권한 범위로 제한된다.

---

## 10. LOCK 인용 표 (5필드 분리 강제 — 3-5/3-6/3-7 선례 계승)

| LOCK ID | 항목 | 값 | 출처 | 변경 조건 |
|---------|------|-----|------|----------|
| LOCK-A2A-02 | Task 상태 열거형 | `submitted\|working\|input-required\|completed\|failed\|canceled` | Google A2A Spec | 스펙 업데이트 시 검토 |
| LOCK-A2A-05 | 컨텍스트 윈도우 한계 | 모델별 max_tokens 준수, 초과 시 압축 | D2.0-05 §12.13 | 모델 변경 시 갱신 |
| LOCK-A2A-09 | Circuit Breaker 연속 실패 임계 | 3회 → OPEN, 60초 후 HALF-OPEN | D2.0-05 §4.4 (ADD-072) | D2.0-05 변경 시만 |

- LOCK-A2A-02 적용 위치: §3 BranchResponse.state, §4.2 머지 트리 무결성
- LOCK-A2A-05 적용 위치: §4.1 분기 5단계 상속 컨텍스트 압축, §5 `-32005`
- LOCK-A2A-09 적용 위치: §4.3 분기 비용 보호 cascade (분기 N>3), §5 `-32031`

> **R2/R9 준수**: 위 LOCK 값은 AUTHORITY_CHAIN.md §3 정본을 verbatim 복사하며 재정의/축약하지 않는다. LOCK-A2A-09 의 비용 보호 차용은 임계값(3회) 변경이 아니라 동일 임계의 적용 확장이다.

---

## 11. 세션 간 인터페이스 cross-check

| 항목 | 대상 산출물 | 일치 항목 |
|------|------------|----------|
| `session_id` 발급 | `multi_turn_sessions.md` | sessionId 발급 API verbatim |
| 부모 상태 스냅샷 | `conversation_state_machine.md` §5.2 | 9 상태 머신 식별자 |
| 트리 스냅샷 청크 | `01_a2a-protocol/artifact_chunking.md` | `ArtifactChunk` 64KB 분할 |
| 분기 비용 큐잉 | `priority_queuing.md` | 분기 작업 우선순위 |
| Circuit Breaker 임계 | `streaming_sse.md` + `moa_pattern.md` | LOCK-A2A-09 3회/60초 verbatim |
| 분기·머지 측정 | `05_monitoring/vbs12_benchmark.md` | 시나리오 8 |

---

## 12. 변경 이력

| 날짜 | 변경자 | 내용 |
|------|--------|------|
| 2026-06-03 | Phase 4 RECOVERY (genuine write) | V3-Phase 4 NEW 최초 작성 (P4-1, P3-1 forward-defined 정본 승급). D1~D8 8섹션 + 분기 트리 자료구조 + 3-way merge + 비용 정책 + RBAC + 영속화 매트릭스. Status DRAFT→APPROVED. LOCK-A2A-02/05 verbatim, LOCK-A2A-09 cascade. SPEC Stage B verify-only 착시(phase4_v3_p4-1_promotion_report) genuine write 해소. |

---

**[END OF conversation_branching.md V3 — Phase 4 APPROVED, 2026-06-03]**
