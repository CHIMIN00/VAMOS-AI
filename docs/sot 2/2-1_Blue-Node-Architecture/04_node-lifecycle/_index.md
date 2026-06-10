# 04. Node Lifecycle State Machine

> **버전**: v2.0
> **Status**: LOCKED (Phase 4 2026-05-31, was REVIEW — 18-file LOCKED inventory)
> **작성일**: 2026-03-30
> **Last-reviewed**: 2026-03-30 / Phase 4 LOCKED 2026-05-31
> **정본 소유 개념**: Node Lifecycle State Machine, 8-State FSM (MODULE-ARCH), P0/P1/P2 전이 규칙, Cap 관리 (ActiveNodeCap/CandidateNodeCap), Lazy Generation, 활성화 트리거/필수 조건, 종료 조건
> **기술스택 의존성**: SPEC §14 범위 내
> **SOT 근거**: D2.0-03 §3.2 (Node Lifecycle), §3.3 (P2 도메인 라이프사이클); D2.0-05 §7.3 고정 1 (07 Gate 선행); D2.0-07 §4.3.2/S7E-050 (승인 타임아웃); RULE 1.3 §2.6 (P2 자동 생성 금지), §3.3 (P2 활성화 조건)
> **GAP 해결**: GAP-BN-04 (CRITICAL)
> **L3 달성**: E1~E9 전항목 충족

---

## LOCK 인용

> LOCK (D2.0-03 §3.2~§3.3 — LOCK-BN-05): Node Lifecycle 규칙 — P0 기본 활성 / P1 승인 후 활성 / P2 세션 한정 + 자동 OFF

> LOCK (상세명세 §4, MODULE-ARCH — LOCK-BN-05a): Node Lifecycle States 8개 — CANDIDATE, LAZY, ACTIVATING, ACTIVE, BUSY, DRAINING, SUSPENDED, TERMINATED. ⚠️ D2.0-03에는 미정의, 상세명세 자체 설계. Phase 5 FINAL PASS 승인으로 사실상 동결.

> LOCK (RULE 1.3 §2.6 — LOCK-BN-06): P2 자동 생성 금지 — 사용자 승인 없이 시스템이 P2 도메인을 자동 활성화하는 것을 금지. 수동 등록은 명시적 승인 하 허용.

> LOCK (D2.0-03 §3.3.2 Option A — LOCK-BN-07): P2 세션 종료 시 자동 OFF — 세션 종료 → 즉시 OFF 전환.

> LOCK (D2.0-03 §3.2 + §3.2.1(C) — LOCK-BN-08): Node 활성화 = 승인 필수 — P1/P2 모두 07 Approval 경유 의무.

> LOCK (D2.0-05 §7.3 고정 1 — LOCK-BN-10): 07 Gate 경유 의무 — 어떤 실행 엔진을 쓰더라도 Execute 단계 전에 07 Gate 결과가 선행 입력으로 확정되어야 한다. 활성화 판정 포함.

> LOCK (D2.0-03 §3.2.1(B) — LOCK-BN-12): active_node_cap — V1=3 (Lead+2Sub), V2=10, V3=50.

> LOCK (D2.0-03 §3.2.1(B) — LOCK-BN-13): candidate_node_cap — V1=5, V2=20, V3=100.

> LOCK (D2.0-07 §4.3.2/S7E-050 — LOCK-BN-19): P2 승인 타임아웃 — 일반 10분 / P2(HITL) 5분 → Auto deny + 작업 취소 + 세션 P2 비활성화.

---

## 개요

Blue Node의 생성부터 종료까지 8개 상태와 전이 규칙을 정의한다. P0/P1/P2 도메인 우선순위별 차별화된 생명주기, Cap 관리, Lazy Generation 전략, 활성화 필수 조건 3가지, 종료 조건을 포함한다.

> ⚠️ **MODULE-ARCH 제안**: 8개 상태 정의(LOCK-BN-05a)는 D2.0-03에서 정의하지 않은 구체적 상태 머신이며, 상세명세 §4에서 MODULE-ARCH 수준으로 설계되었다. D2.0-03 §3.2/§3.3에서 정의된 것은 P0/P1/P2 분류 + 활성화/비활성화 규칙이다.

---

## 1. 8-State 정의 (E1)

> ⚠️ LOCK-BN-05a: MODULE-ARCH 제안. D2.0-03에서 정의하지 않은 구체적 상태 머신.

```python
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class NodeState(str, Enum):
    """Blue Node 8-State (LOCK-BN-05a, MODULE-ARCH)"""
    CANDIDATE   = "CANDIDATE"    # 후보 등록, 미활성
    LAZY        = "LAZY"         # 코드 로드, 리소스 미할당
    ACTIVATING  = "ACTIVATING"   # 리소스 할당 중 (MCP 연결, 메모리 초기화)
    ACTIVE      = "ACTIVE"       # 정상 운영, 태스크 수신 가능
    BUSY        = "BUSY"         # 태스크 실행 중, 신규 태스크 대기열
    DRAINING    = "DRAINING"     # 종료 준비, 기존 태스크 완료 대기
    SUSPENDED   = "SUSPENDED"    # 일시 정지, 리소스 유지/태스크 미수신
    TERMINATED  = "TERMINATED"   # 종료 완료, 리소스 해제

class DomainPriority(str, Enum):
    """도메인 우선순위 (LOCK-BN-05: D2.0-03 §3.2~§3.3)"""
    P0 = "P0"  # 기본 활성
    P1 = "P1"  # 승인 후 활성
    P2 = "P2"  # 세션 한정 + 자동 OFF
```

| 상태 | 코드 | 설명 | 리소스 상태 |
|------|------|------|------------|
| **Candidate** | `CANDIDATE` | candidate_node_cap에 의해 후보로 등록됨 | 없음 |
| **Lazy** | `LAZY` | 코드 로드 완료, 리소스 미할당 (lazy generation) | 코드만 |
| **Activating** | `ACTIVATING` | 리소스 할당 중 (MCP 연결, 메모리 초기화) | 할당 중 |
| **Active** | `ACTIVE` | 정상 운영 중, 작업 수신 가능 | 전체 할당 |
| **Busy** | `BUSY` | 작업 실행 중 (새 작업 큐잉) | 전체 할당 |
| **Draining** | `DRAINING` | 종료 준비 중 (진행 작업 완료 대기) | 유지 (해제 예정) |
| **Suspended** | `SUSPENDED` | 일시 중지 (리소스 유지, 작업 불가) | 유지 |
| **Terminated** | `TERMINATED` | 종료됨 (리소스 해제 완료) | 없음 |

---

## 2. 상태 전이표 (E1)

> LOCK-BN-05a (MODULE-ARCH 제안). 각 전이에 P0/P1/P2 분기 조건 포함.

| # | 출발 상태 | 도착 상태 | 트리거 이벤트 | 가드 조건 | P0 | P1 | P2 |
|---|-----------|-----------|--------------|-----------|:--:|:--:|:--:|
| T01 | CANDIDATE | LAZY | `register_complete` | candidate_node_cap 미초과 | ✅ | ✅ | ❌ (LOCK-BN-06: 자동 생성 금지) |
| T02 | CANDIDATE | LAZY | `manual_register` | 사용자 명시적 승인 + candidate_cap 미초과 | — | — | ✅ (수동만 허용) |
| T03 | LAZY | ACTIVATING | `activation_request` | 필수 조건 3가지 충족 (§4 참조) | ✅ (P0 자동) | ✅ (승인 후) | ✅ (세션 내 승인 후) |
| T04 | ACTIVATING | ACTIVE | `resources_ready` | MCP 연결 + 메모리 할당 + Template 프리로드 완료 | ✅ | ✅ | ✅ |
| T05 | ACTIVE | BUSY | `task_received` | 태스크 수신 | ✅ | ✅ | ✅ |
| T06 | BUSY | ACTIVE | `task_complete` | 태스크 완료, 대기열 비어있음 | ✅ | ✅ | ✅ |
| T07 | ACTIVE | SUSPENDED | `suspend_command` | 관리자 명령 또는 에러율 > 30% | ✅ | ✅ | ✅ |
| T08 | BUSY | SUSPENDED | `suspend_command` | 진행 태스크 완료 후 | ✅ | ✅ | ✅ |
| T09 | SUSPENDED | ACTIVE | `resume_command` | 관리자 재개 명령 + 필수 조건 재검증 | ✅ | ✅ | ✅ (세션 유효 시) |
| T10 | ACTIVE | DRAINING | `terminate_trigger` | idle_timeout / resource_pressure / cap_exceeded / manual_stop | ✅ | ✅ | ✅ |
| T11 | BUSY | DRAINING | `terminate_trigger` | 진행 태스크 완료 대기 후 전이 | ✅ | ✅ | ✅ |
| T12 | ACTIVE | DRAINING | `session_end` | P2 세션 종료 (LOCK-BN-07) | — | — | ✅ (즉시) |
| T13 | BUSY | DRAINING | `session_end` | P2 세션 종료 — 진행 태스크 강제 취소 후 즉시 전이 (LOCK-BN-07 즉시 OFF) | — | — | ✅ (즉시) |
| T14 | DRAINING | TERMINATED | `drain_complete` | 모든 진행 태스크 완료 | ✅ | ✅ | ✅ |
| T15 | SUSPENDED | TERMINATED | `force_terminate` | 관리자 강제 종료 명령 | ✅ | ✅ | ✅ |
| T16 | ACTIVATING | SUSPENDED | `activation_failed` | 리소스 할당 실패 (MCP 연결 실패 등) | ✅ | ✅ | ✅ |

### 상태 전이 다이어그램

```
                    ┌──────────────┐
                    │  CANDIDATE   │
                    └──────┬───────┘
                           │ T01/T02 (register)
                           ▼
                    ┌──────────────┐
                    │    LAZY      │
                    └──────┬───────┘
                           │ T03 (activation_request)
                           ▼
                    ┌──────────────┐     T16 (fail)     ┌──────────────┐
                    │  ACTIVATING  │───────────────────►│  SUSPENDED   │
                    └──────┬───────┘                    └──┬───────┬───┘
                           │ T04 (resources_ready)         │       │
                           ▼                    T09 (resume)│       │T15 (force)
              ┌───►┌──────────────┐◄────────────────────────┘       │
              │    │   ACTIVE     │──T07(suspend)──►SUSPENDED       │
              │    └──────┬───────┘                                 │
              │           │ T05 (task)      │ T10/T12 (terminate)   │
              │           ▼                 ▼                       ▼
              │    ┌──────────────┐  ┌──────────────┐       ┌──────────────┐
              │    │    BUSY      │  │  DRAINING    │──T14─►│ TERMINATED   │
              │    └──────┬───────┘  └──────────────┘       └──────────────┘
              │           │ T06 (complete)
              └───────────┘
```

---

## 3. P0/P1/P2 도메인별 전이 규칙 (LOCK-BN-05)

### 3.1 P0: 기본 활성

- **규칙**: 시스템 시작 시 자동으로 CANDIDATE → LAZY → ACTIVATING → ACTIVE
- **승인**: 불필요 (P0는 "기본 안전 범위" — D2.0-03 §3.1)
- **종료**: idle_timeout / resource_pressure / manual_stop 시만
- **인스턴스** (부록 §A.1):

| node_id | 도메인 | 역할 | risk_class | cost_class |
|---------|--------|------|-----------|-----------|
| `bn_web_research` | Research | 웹 검색, 소스 평가, 근거 수집 | low | v0 |
| `bn_code_engine` | Dev | 코드 생성, 리팩토링, 테스트 | med | v1 |
| `bn_content_gen` | Content | 콘텐츠 생성, 요약, 번역 | low | v0 |

### 3.2 P1: 승인 후 활성

- **규칙**: "도메인 확장" 범주, 사용자 승인 필수 (LOCK-BN-08)
- **승인 구조**: RULE 1.3 2단계 승인 — 1단계 계획 승인 + 2단계 실행 승인
- **후보 생성**: 채널 A (CORE 제안) / 채널 B (사용자 요청) — 프로필 생성 + 승인 요청까지만 허용
- **자동화 제한**: "후보 프로필 생성"까지만 허용, 활성화는 승인 후 (D2.0-03 §3.2)
- **종료**: idle_timeout / error_threshold / manual_stop
- **인스턴스** (부록 §A.2): `bn_quant_analyst`, `bn_pkm`, `bn_education`, `bn_health`, `bn_media`, `bn_cloud_collector_e15`

### 3.3 P2: 세션 한정 활성 (LOCK-BN-07)

- **규칙**: 세션 한정 + 자동 OFF (D2.0-03 §3.3)
- **자동 생성 금지**: LOCK-BN-06 — "사용자 승인 없이 시스템이 P2 자동 활성화" 금지 (RULE 1.3 §2.6). 수동 등록은 명시적 승인 하 허용
- **적용 범위**: P2가 승인으로 활성화되는 세션에서만 (D2.0-03 §3.3.1)
- **자동 비활성화**: Option A — 세션 종료 시 즉시 OFF (LOCK-BN-07, D2.0-03 §3.3.2)
- **활성화 조건**: 사용자 명시적 승인 요청 + 해당 세션에서만 활성 (D2.0-03 §3.3.3)
- **승인 타임아웃**: P2 HITL 5분 → Auto deny + 작업 취소 + 세션 P2 비활성화 (LOCK-BN-19, D2.0-07 §4.3.2/S7E-050)
- **이벤트**: `oc.p2.activated` / `oc.p2.deactivated` (D2.0-03 §3.3.5, 정본: 02 §6.1 LogEvent Registry)
- **인스턴스** (부록 §A.2): `bn_trading_exec`

> 참고: D2.0-03 §3.3.4는 §3.3.2 "자동 비활성화 규칙(LOCK)"을 따르며 별도 규칙 없음. §3.3.6은 향후 DEFER (24시간 운영 단계에서 재검토).

---

## 4. 활성화 필수 조건 + 트리거 (E1)

### 4.1 활성화 필수 조건 3가지 (D2.0-03 §3.2.1(C))

> 트리거 발생 → 필수 조건 3가지 검증 → **전부 충족 시만** ACTIVATING 진입.

| # | 필수 조건 | 출처 | 설명 |
|---|-----------|------|------|
| G1 | **07 Approval allow** | LOCK-BN-08 | P1/P2 모두 07 Approval 경유 의무. P0는 면제 |
| G2 | **02 Decision.gates.result allow/restrict** | D2.0-03 §3.2.1(C) | Decision 게이트가 범위 확정 |
| G3 | **04 ToolRegistry 실행 경로 확정** | D2.0-03 §3.2.1(C) | tool_id/adapter/runtime 경로 확정 |

```python
from typing import Literal

class ActivationGateResult(BaseModel):
    """활성화 필수 조건 검증 결과 (D2.0-03 §3.2.1(C) "활성 트리거(승인 후 ON)")"""
    approval_result: Literal["allow", "deny", "timeout"] = Field(
        ..., description="07 Approval 결과", example="allow"
    )
    decision_gates_result: Literal["allow", "restrict", "deny"] = Field(
        ..., description="02 Decision.gates.result", example="allow"
    )
    tool_registry_confirmed: bool = Field(
        ..., description="04 ToolRegistry 실행 경로 확정 여부", example=True
    )

    domain_priority: Literal["P0", "P1", "P2"] = Field(
        ..., description="노드 도메인 우선순위 (P0는 07 Approval 면제 — §4.1 G1)", example="P0"
    )

    def all_passed(self) -> bool:
        # G1: P0는 07 Approval 면제 — approval_result 미요구
        approval_ok = (self.domain_priority == "P0") or (self.approval_result == "allow")
        return (
            approval_ok
            and self.decision_gates_result in ("allow", "restrict")
            and self.tool_registry_confirmed
        )
```

### 4.2 활성화 트리거 (시도 사유)

> 트리거 = 활성화 시도 사유. 필수 조건 = 활성화 허용 게이트. 구분 필수.

| 트리거 | 설명 | 대상 도메인 |
|--------|------|------------|
| `first_request` | 해당 도메인 첫 요청 수신 | P0/P1 |
| `preload` | 시스템 시작 시 자주 사용 노드 사전 로드 | P0 |
| `scheduled` | 스케줄 기반 활성화 | P1 |
| `dependency` | 의존 노드 활성화 시 연쇄 활성 | P1 |
| `manual_request` | 사용자 명시적 활성화 요청 | P2 (수동만 허용) |

---

## 5. Cap 관리 (E1)

### 5.1 Cap 상한 값 (LOCK-BN-12/13)

```python
class ActiveNodeCap(BaseModel):
    """활성 노드 상한 (LOCK-BN-12: D2.0-03 §3.2.1(B))

    V1 "Lead+2Sub" 구조: Lead=주 실행 노드, Sub=보조 노드.
    ⚠️ 부록 §A.1의 3개 V1 인스턴스와 정합 — 3개 BN이 모두 P0이나
    Lead/Sub 역할 구분은 D2.0-03에 미명세 (INFO).
    """
    v1: int = Field(default=3, description="V1 상한: Lead+2Sub")
    v2: int = Field(default=10, description="V2 상한")
    v3: int = Field(default=50, description="V3 상한")

class CandidateNodeCap(BaseModel):
    """후보 노드 상한 (LOCK-BN-13: D2.0-03 §3.2.1(B))"""
    v1: int = Field(default=5, description="V1 상한")
    v2: int = Field(default=20, description="V2 상한")
    v3: int = Field(default=100, description="V3 상한")

class MaxPerDomain(BaseModel):
    """도메인별 최대 활성 노드 (MODULE-ARCH 자체 설계, D2.0-03 미정의)"""
    default: int = Field(default=2, description="도메인별 최대 활성 노드 수")
```

| 버전 | active_node_cap | candidate_node_cap | 비고 |
|------|:---------------:|:------------------:|------|
| V1 | **3** | **5** | Lead+2Sub, P0 3개 노드 |
| V2 | **10** | **20** | P1 확장 |
| V3 | **50** | **100** | P2 확장 + 커스텀 |

### 5.2 상한 도달 시 정책

> LOCK (D2.0-03 §3.2.1(B)): 상한 도달 시 동작 — 신규 후보 생성 금지 → 기존 NODE 재사용 또는 "범용 NODE + ToolRegistry"로 대체.

1. `candidate_node_cap` 초과 → 최장 미사용 CANDIDATE 퇴거 (LRU)
2. `active_node_cap` 초과 → 최장 미사용 ACTIVE → DRAINING → TERMINATED (LRU)
3. 재사용 불가 시 → 범용 NODE + ToolRegistry로 대체 실행

### 5.3 max_per_domain

> MODULE-ARCH 자체 설계 (D2.0-03 미정의). 기본값=2, 구현 시 조정 가능.

---

## 6. Lazy Generation 전략 (E2)

> LOCK-BN-06 (P2 자동 생성 금지, RULE 1.3 §2.6). P1 후보 생성은 "프로필 생성 + 승인 요청"까지만 허용 (D2.0-03 §3.2, §3.2.1(A)).

```python
class LazyNodeGenerator:
    """최초 요청 시점에 노드 리소스 할당 (Lazy Generation, A-5)

    흐름: LAZY → 필수 조건 검증 → MCP 연결 → 메모리 할당
          → Template 프리로드 → ACTIVATING → ACTIVE
    """

    async def activate_node(self, node_id: str, trigger: str,
                            gate_result: ActivationGateResult) -> NodeState:
        # Step 1: 필수 조건 검증
        if not gate_result.all_passed():
            raise ActivationDeniedError(
                node_id=node_id,
                failure_code="ACTIVATION_DENIED",
                detail=f"Gate check failed: {gate_result}"
            )

        # Step 2: Cap 잔여 확인
        if not await self.cap_manager.can_activate(node_id):
            raise CapExceededError(
                node_id=node_id,
                failure_code="CAP_EXCEEDED"
            )

        # Step 3: 상태 전이 LAZY → ACTIVATING
        await self.transition(node_id, NodeState.ACTIVATING)

        # Step 4: 리소스 할당
        try:
            mcp_handle = await self.connect_mcp(node_id)        # MCP 연결
            memory = await self.allocate_memory(node_id)         # 메모리 할당
            templates = await self.preload_templates(node_id)    # Template 프리로드
        except Exception as e:
            await self.transition(node_id, NodeState.SUSPENDED)
            raise ActivationTimeoutError(node_id=node_id, detail=str(e))

        # Step 5: 상태 전이 ACTIVATING → ACTIVE
        await self.transition(node_id, NodeState.ACTIVE)
        await self.emit_event("bn.lifecycle.state_changed", {
            "node_id": node_id, "from": "LAZY", "to": "ACTIVE", "trigger": trigger
        })

        return NodeState.ACTIVE
```

---

## 7. P2 라이프사이클 상세 (D2.0-03 §3.3)

> D2.0-03 §3.3 전체 반영: §3.3.1 적용 범위, §3.3.2 자동 비활성화 Option A, §3.3.3 활성화 조건, §3.3.5 이벤트.

### 7.1 적용 범위 (§3.3.1)

P2 라이프사이클 규칙은 **"P2가 승인으로 활성화되는 세션"**에서만 적용. 기본 정책 "P2 OFF" 상태에서는 미래 확장 대비 규칙으로만 유지.

### 7.2 자동 비활성화 (§3.3.2, LOCK-BN-07)

- **Option A (LOCK)**: 세션 종료 시 즉시 OFF
- UI/로그에 "세션 종료로 OFF" 기록 필수 (08 UI 규칙 참조)

### 7.3 활성화 조건 (§3.3.3)

1. 사용자 명시적 승인 요청
2. 승인 시 **해당 세션에서만** 활성

### 7.4 승인 타임아웃 (LOCK-BN-19)

> LOCK (D2.0-07 §4.3.2/S7E-050 — LOCK-BN-19): P2 HITL 5분 → Auto deny.

| 트리거 조건 | 임계값 | 타임아웃 | deny 시 fallback |
|------------|--------|----------|-----------------|
| P2 도메인 작업 실행 | P2 활성 상태 + 매 요청 | 5분 | 작업 취소 + 세션 P2 비활성화 |

### 7.5 이벤트 (§3.3.5)

- `oc.p2.activated`: P2 활성화 시 기록
- `oc.p2.deactivated`: P2 비활성화 시 기록
- 이벤트 정본: 02 §6.1 LogEvent Registry (REF-only, D2.1-D3 AC-D3-003 규칙)

---

## 8. 종료 조건

| 조건 | 임계값 | 동작 | 대상 | 출처 |
|------|--------|------|------|------|
| `idle_timeout` | 5분 무요청 | ACTIVE → DRAINING → TERMINATED | P0/P1 | MODULE-ARCH (D2.0-03 미정의) |
| `error_threshold` | 에러율 > 30% | ACTIVE → SUSPENDED | 전체 | MODULE-ARCH (D2.0-03 미정의) |
| `manual_stop` | 관리자 명령 | Any → DRAINING → TERMINATED | 전체 | — |
| `resource_pressure` | 시스템 리소스 부족 | LRU 노드 → DRAINING → TERMINATED | LRU 순서 | — |
| `cap_exceeded` | active_node_cap 초과 | LRU 노드 → DRAINING → TERMINATED | LRU 순서 | LOCK-BN-12 |
| `session_end` | P2 세션 종료 | ACTIVE/BUSY → DRAINING → TERMINATED (즉시) | P2만 | LOCK-BN-07 |

> ⚠️ idle_timeout=5분, error_threshold=30%는 D2.0-03에 미정의 — MODULE-ARCH 자체 설계. 구현 시 조정 가능.

---

## 9. LogEvent 이벤트 기록 명세

| 이벤트 | 발생 시점 | 정본 | 비고 |
|--------|----------|------|------|
| `oc.p2.activated` | P2 활성화 | D2.0-03 §3.3.5 / 02 §6.1 | 정본: ORANGE CORE LogEvent Registry |
| `oc.p2.deactivated` | P2 비활성화 | D2.0-03 §3.3.5 / 02 §6.1 | 동일 |
| `bn.lifecycle.state_changed` | 모든 상태 전이 시 | MODULE-ARCH (02 §6.1 REF) | payload: node_id, from, to, trigger |
| `bn.lifecycle.cap_exceeded` | Cap 초과 시 | MODULE-ARCH (02 §6.1 REF) | payload: node_id, cap_type, current, limit |
| `bn.lifecycle.activation_denied` | 활성화 거부 시 | MODULE-ARCH (02 §6.1 REF) | payload: node_id, gate_result, failure_code |
| `bn.lifecycle.activation_failed` | ACTIVATING→SUSPENDED 전이 시 (T16) | MODULE-ARCH (02 §6.1 REF) | payload: node_id, error_detail, mcp_status |

> 이벤트 정본: 02 §6.1 LogEvent Registry (REF-only, D2.1-D3 AC-D3-003 규칙).

---

## 10. 에러 코드 카탈로그 + 복구 전략 (E5)

> failure_code UPPER_SNAKE (정본: 02 §6.1~6.3).

| 에러 코드 | 설명 | 발생 조건 | 복구 전략 |
|-----------|------|----------|----------|
| `CAP_EXCEEDED` | 노드 상한 초과 | active_node_cap 또는 candidate_node_cap 초과 | 기존 NODE 재사용 또는 범용 NODE + ToolRegistry 대체 |
| `ACTIVATION_DENIED` | 활성화 필수 조건 미충족 | G1/G2/G3 중 하나 이상 미충족 | 미충족 조건별 안내 (승인 요청/Decision 재판정/ToolRegistry 확인) |
| `ACTIVATION_TIMEOUT` | 활성화 시간 초과 | ACTIVATING 상태에서 리소스 할당 시간 초과 | 재시도 또는 fallback (SUSPENDED 전이) |
| `STATE_INVALID` | 잘못된 상태 전이 시도 | 전이표에 없는 from→to 시도 | 현재 상태 안내, 유효 전이 목록 제공 |
| `P2_NOT_APPROVED` | P2 승인 미완료 | P2 활성화 시도 시 승인 미경유 | 사용자 승인 요청 안내 |
| `APPROVAL_TIMEOUT` | 승인 타임아웃 | LOCK-BN-19 타임아웃 (P2 HITL 5분 초과) | Auto deny + 작업 취소 + 세션 P2 비활성화, 재요청 안내 |
| `RESOURCE_EXHAUSTED` | 리소스 부족 | 시스템 메모리/CPU 부족으로 할당 실패 | 다른 노드로 위임 또는 대기열 배치 |
| `SUSPEND_FAILED` | 일시 중지 실패 | SUSPENDED 전이 중 오류 | 강제 DRAINING 전이 |

---

## 11. 알고리즘 상세 (E2)

### 11.1 상태 전이 알고리즘 (FSM 엔진)

```python
class LifecycleFSM:
    """상태 전이 알고리즘: current_state × trigger → guard_check → next_state 또는 reject"""

    TRANSITION_TABLE: dict[tuple[NodeState, str], tuple[NodeState, Callable]] = {
        (NodeState.CANDIDATE, "register_complete"): (NodeState.LAZY, guard_candidate_cap),
        (NodeState.CANDIDATE, "manual_register"):   (NodeState.LAZY, guard_manual_p2),
        (NodeState.LAZY, "activation_request"):      (NodeState.ACTIVATING, guard_activation_gates),
        (NodeState.ACTIVATING, "resources_ready"):   (NodeState.ACTIVE, guard_resources),
        (NodeState.ACTIVE, "task_received"):          (NodeState.BUSY, guard_none),
        (NodeState.BUSY, "task_complete"):             (NodeState.ACTIVE, guard_none),
        (NodeState.ACTIVE, "suspend_command"):         (NodeState.SUSPENDED, guard_none),
        (NodeState.SUSPENDED, "resume_command"):       (NodeState.ACTIVE, guard_activation_gates),
        (NodeState.ACTIVE, "terminate_trigger"):       (NodeState.DRAINING, guard_none),
        (NodeState.ACTIVE, "session_end"):             (NodeState.DRAINING, guard_p2_only),
        (NodeState.DRAINING, "drain_complete"):        (NodeState.TERMINATED, guard_none),
        (NodeState.BUSY, "suspend_command"):           (NodeState.SUSPENDED, guard_none),       # T08
        (NodeState.BUSY, "terminate_trigger"):         (NodeState.DRAINING, guard_none),         # T11
        (NodeState.BUSY, "session_end"):               (NodeState.DRAINING, guard_p2_only),      # T13
        (NodeState.SUSPENDED, "force_terminate"):      (NodeState.TERMINATED, guard_none),       # T15
        (NodeState.ACTIVATING, "activation_failed"):   (NodeState.SUSPENDED, guard_none),        # T16
    }

    async def transition(self, node_id: str, trigger: str) -> NodeState:
        current = await self.get_state(node_id)
        key = (current, trigger)

        if key not in self.TRANSITION_TABLE:
            raise StateInvalidError(node_id=node_id, current=current, trigger=trigger)

        next_state, guard_fn = self.TRANSITION_TABLE[key]

        if not await guard_fn(node_id):
            raise ActivationDeniedError(node_id=node_id, trigger=trigger)

        await self.set_state(node_id, next_state)
        await self.emit_event("bn.lifecycle.state_changed", {
            "node_id": node_id, "from": current, "to": next_state, "trigger": trigger
        })
        return next_state
```

### 11.2 활성화 판정 로직

```
1. Cap 잔여 확인 (active_node_cap)
2. 07 Approval 결과 확인 (P0 면제)
3. 02 Decision.gates.result 확인
4. 04 ToolRegistry 실행 경로 확정 확인
5. 전부 통과 → ACTIVATING 진입
6. 하나라도 실패 → ACTIVATION_DENIED
```

### 11.3 종료 판정 로직

```
1. idle_timeout 타이머 — 5분 무요청 감지
2. error_rate 모니터 — 에러율 30% 초과 감지 → SUSPENDED
3. Cap 초과 LRU 선택 — active_node_cap 초과 시 최장 미사용 노드 선택 → DRAINING
4. P2 세션 종료 감지 → 즉시 DRAINING (LOCK-BN-07)
```

---

## 12. 보안 요소 (E7)

### 12.1 승인 우회 방지

- 모든 P1/P2 활성화는 07 Approval 경유 필수 (LOCK-BN-08)
- Execute 단계 전 07 Gate 결과 선행 필수 (LOCK-BN-10, D2.0-05 §7.3 고정 1)
- P1: 후보 프로필 생성 + 승인 요청까지만 허용, 자동 활성화/실행 금지
- P2: 자동 생성 금지 (LOCK-BN-06) — "사용자 승인 없이 시스템이 P2 자동 활성화" 금지, 수동 등록은 명시적 승인 하 허용

### 12.2 감사 로그 스키마

```python
class LifecycleAuditLog(BaseModel):
    """상태 전이 감사 로그"""
    audit_log_id: str = Field(..., description="감사 로그 고유 ID")
    node_id: str = Field(..., description="노드 ID", example="bn_trading_exec")
    from_state: NodeState = Field(..., description="이전 상태")
    to_state: NodeState = Field(..., description="이후 상태")
    trigger: str = Field(..., description="트리거 이벤트", example="activation_request")
    guard_result: dict = Field(..., description="가드 조건 검증 결과")
    timestamp: datetime = Field(..., description="발생 시각")
    session_id: str = Field(..., description="세션 ID")
    approval_id: Optional[str] = Field(None, description="07 Approval ID (P1/P2)")
```

### 12.3 P2 Auto deny 시 필수 조치

- 감사 로그 기록 필수
- 사용자 알림 필수
- fallback: 작업 취소 + 세션 P2 비활성화 (D2.0-07 S7E-050)

---

## 13. 의존성 (E3)

### 상위 의존

| 대상 | 위치 | 관계 |
|------|------|------|
| ORANGE CORE | 02 Decision, I-5 routing | 활성화 트리거 발원, Decision.gates.result 제공 |
| 07 Gate | D2.0-05 §7.3 고정 1 (LOCK-BN-10) | Execute 단계 전 07 Gate 결과 선행 필수. 활성화 포함 |
| ApprovalManager | D2.0-07 §4.3.2/S7E-050 (LOCK-BN-19) | P1/P2 승인, P2 HITL 5분 타임아웃 |
| RULE 1.3 | §4.2~4.3 (P0/P1/P2 분류), §2.6 (P2 자동 생성 금지), §3.3 (P2 활성화 조건) | P2 세션 OFF 정본은 D2.0-03 §3.3.2 |

### 하위 의존

| 대상 | 관계 |
|------|------|
| 모든 BN 인스턴스 (부록 §A) | Lifecycle FSM이 모든 BN의 상태 관리 |

### 연관 의존

| 대상 | 위치 | 관계 |
|------|------|------|
| Permission Matrix | `01_permission-matrix/` | 활성화 시 권한 로드, 상태 전이 시 권한 재평가 |
| Interface Contract | `02_core-node-interface/` | Envelope 기반 요청 수신이 활성화 트리거 (ACTIVE 상태에서만) |
| MCP Bridge | `07_mcp-bridge/` | ACTIVATING 시 MCP 연결 수립 |
| Template Injection | `03_template-injection/` | ACTIVATING 시 Template 프리로드 |
| ToolRegistry | 04 (D2.0-03 §3.2.1(C)) | 활성 조건 G3: 실행 경로 확정 |

---

## 14. 단위 테스트 케이스 (E4)

### TC-LC-01: Cap 초과 시 활성화 거부

```python
def test_cap_exceeded_activation_denied():
    """active_node_cap V1=3 초과 시 CAP_EXCEEDED (LOCK-BN-12)"""
    # 3개 노드 이미 ACTIVE
    for i in range(3):
        await fsm.transition(f"node_{i}", "activation_request")

    # 4번째 활성화 시도 → 거부
    with pytest.raises(CapExceededError) as exc:
        await fsm.transition("node_3", "activation_request")
    assert exc.value.failure_code == "CAP_EXCEEDED"
```

### TC-LC-02: P2 세션 종료 시 자동 OFF

```python
def test_p2_session_end_auto_off():
    """LOCK-BN-07: ACTIVE→DRAINING→TERMINATED (세션 종료 즉시)"""
    node = create_p2_node("bn_trading_exec", state=NodeState.ACTIVE)
    result = await fsm.transition(node.id, "session_end")
    assert result == NodeState.DRAINING

    await fsm.transition(node.id, "drain_complete")
    assert await fsm.get_state(node.id) == NodeState.TERMINATED
    assert_event_emitted("oc.p2.deactivated", node_id=node.id)
```

### TC-LC-03: P2 자동 생성 금지

```python
def test_p2_auto_generation_blocked():
    """LOCK-BN-06: P2 자동 후보 등록 시도 → 거부. 수동 등록+승인은 허용."""
    # 자동 생성 시도 → 거부
    with pytest.raises(ActivationDeniedError):
        await generator.auto_register("bn_trading_exec", priority=DomainPriority.P2)

    # 수동 등록 + 명시적 승인 → 허용
    result = await generator.manual_register(
        "bn_trading_exec", priority=DomainPriority.P2, approval_id="APR-001"
    )
    assert result.state == NodeState.LAZY
```

### TC-LC-04: 승인 없이 활성화 시도 시 거부

```python
def test_activation_without_approval_denied():
    """LOCK-BN-08: 07 Approval 미경유 → ACTIVATION_DENIED"""
    gate = ActivationGateResult(
        approval_result="deny",
        decision_gates_result="allow",
        tool_registry_confirmed=True
    )
    with pytest.raises(ActivationDeniedError) as exc:
        await generator.activate_node("bn_quant_analyst", "first_request", gate)
    assert exc.value.failure_code == "ACTIVATION_DENIED"
```

### TC-LC-05: LOCK-BN-19 타임아웃 Auto deny

```python
def test_p2_approval_timeout():
    """P2 HITL 5분 초과 → APPROVAL_TIMEOUT + 작업 취소 + 세션 P2 비활성화"""
    node = create_p2_node("bn_trading_exec")
    # 5분 타임아웃 시뮬레이션
    result = await approval_manager.wait_approval(node.id, timeout_sec=300)
    assert result.status == "timeout"
    assert result.failure_code == "APPROVAL_TIMEOUT"
    assert result.fallback == "작업 취소 + 세션 P2 비활성화"
    assert_event_emitted("oc.p2.deactivated", node_id=node.id)
```

### TC-LC-06: 정상 상태 전이 시퀀스

```python
def test_normal_lifecycle_sequence():
    """정상 전이: CANDIDATE→LAZY→ACTIVATING→ACTIVE→BUSY→ACTIVE→DRAINING→TERMINATED"""
    node_id = "bn_web_research"
    assert await fsm.get_state(node_id) == NodeState.CANDIDATE

    await fsm.transition(node_id, "register_complete")
    assert await fsm.get_state(node_id) == NodeState.LAZY

    gate = ActivationGateResult(
        approval_result="allow", decision_gates_result="allow",
        tool_registry_confirmed=True
    )
    await generator.activate_node(node_id, "first_request", gate)
    assert await fsm.get_state(node_id) == NodeState.ACTIVE

    await fsm.transition(node_id, "task_received")
    assert await fsm.get_state(node_id) == NodeState.BUSY

    await fsm.transition(node_id, "task_complete")
    assert await fsm.get_state(node_id) == NodeState.ACTIVE

    await fsm.transition(node_id, "terminate_trigger")
    assert await fsm.get_state(node_id) == NodeState.DRAINING

    await fsm.transition(node_id, "drain_complete")
    assert await fsm.get_state(node_id) == NodeState.TERMINATED
```

---

## 15. 구체적 사용 시나리오 (E8)

### 시나리오 A: P0 BN-WebResearch 시스템 시작 시 자동 활성화

1. 시스템 시작 → `bn_web_research` CANDIDATE 등록
2. `preload` 트리거 발생 → CANDIDATE → LAZY
3. P0이므로 승인 불필요 → 필수 조건 G2(Decision), G3(ToolRegistry)만 검증
4. 리소스 할당 → LAZY → ACTIVATING → ACTIVE
5. 첫 요청 수신 → ACTIVE → BUSY → 작업 완료 → ACTIVE
6. 5분 무요청 → idle_timeout → ACTIVE → DRAINING → TERMINATED

### 시나리오 B: P1 BN-Quant 사용자 요청 → 승인 → 활성화

1. 사용자가 정량 분석 요청 → CORE가 `bn_quant_analyst` 후보 생성 (채널 A)
2. CANDIDATE 등록 → LAZY
3. 07 Approval 1단계 계획 승인 요청 → 사용자 승인
4. 필수 조건 3가지 검증 (G1 allow, G2 allow, G3 confirmed)
5. LAZY → ACTIVATING → ACTIVE
6. 작업 수행 → ACTIVE ↔ BUSY 반복
7. 5분 무요청 → idle_timeout → DRAINING → TERMINATED

### 시나리오 C: P2 BN-Trading 사용자 명시적 승인 → 세션 한정

1. 사용자가 거래 실행을 명시적으로 요청
2. 수동 등록 → CANDIDATE → LAZY (LOCK-BN-06: 자동 생성 금지이므로 수동만)
3. 07 Approval 요청 → P2 HITL 5분 타임아웃 시작
4. 사용자 승인 → 필수 조건 3가지 통과 → LAZY → ACTIVATING → ACTIVE
5. 이벤트: `oc.p2.activated` 기록
6. 해당 세션에서만 활성 → 매 요청마다 P2 확인
7. 세션 종료 → 즉시 ACTIVE → DRAINING → TERMINATED (LOCK-BN-07)
8. 이벤트: `oc.p2.deactivated` 기록

---

## 16. 성능 기준 (E6)

| 지표 | 기준값 | 측정 방식 |
|------|--------|----------|
| 상태 전이 latency (LAZY→ACTIVE) | < 500ms (ACTIVATING 포함) | first_request 수신 ~ ACTIVE 전이 완료 |
| SUSPENDED→ACTIVE 복구 시간 | < 200ms | resume_command ~ ACTIVE 전이 완료 |
| Cap 검사 오버헤드 | < 5ms | can_activate() 호출 ~ 반환 |
| 전체 활성화 판정 (트리거→ACTIVE) | < 1s (07 Approval 대기 제외) | 트리거 수신 ~ ACTIVE 전이 (승인 대기 시간 제외) |

---

## 17. V1/V2/V3 Phase 매핑 (E9)

> 구현 범위(scope) 정의만 기술. Phase 일정은 Part2 정본 (R6 준수).

| Phase | 노드 범위 | active_cap / candidate_cap | 주요 기능 |
|-------|----------|:-------------------------:|-----------|
| **V1** | P0 3개 노드 기본 활성 | 3 / 5 | 기본 FSM + idle_timeout 5분 + Cap 검사 |
| **V2** | P1 7개 노드 확장 | 10 / 20 | Dynamic Cap 조정 + Lazy Generation 고도화 + 2단계 승인 |
| **V3** | P2 확장 + 커스텀 노드 | 50 / 100 | 커스텀 노드 Lifecycle 정책 + 원격 실행(A-7) 활성화 |

---

## 18. 교차 참조

| 참조 대상 | 위치 | 관계 |
|----------|------|------|
| Permission Matrix | `01_permission-matrix/` | 상태 전이 시 권한 재평가, SUSPENDED → NODE_SUSPENDED |
| Interface Contract | `02_core-node-interface/` | ACTIVE 상태에서만 요청 수신 |
| Template Injection | `03_template-injection/` | ACTIVATING 시 Template 프리로드 |
| MCP Bridge | `07_mcp-bridge/` | ACTIVATING 시 MCP 연결 수립 |
| D2.0-05 §5.3.1 | SOT | Agent 3요소(Identity/Capability/Policy) — AgentMode↔Lifecycle 관계 추론 반영 |
| D2.0-05 §7.3 | SOT | 07 Gate 경유 의무 (고정 1) — Execute 단계 전 선행 필수 |

---

*정본 소유: 04_node-lifecycle/_index.md → Node Lifecycle State Machine, 8-State FSM, P0/P1/P2 전이 규칙, Cap 관리, Lazy Generation, 활성화 트리거/필수 조건, 종료 조건*
