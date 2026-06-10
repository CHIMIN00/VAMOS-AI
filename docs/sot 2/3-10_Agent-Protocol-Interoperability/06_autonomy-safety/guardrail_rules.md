# Guardrail Rules — K-042 / K-043 L3

> **정본 소유**: #13 Agent-Protocol-Interoperability / 06_autonomy-safety
> **레벨**: L3 (구현 상세)
> **버전**: v1.0 (2026-04-11, P1-2)
> **담당 K-ID**: K-042 (Human-in-the-Loop 프로토콜), K-043 (에이전트 샌드박싱)
> **LOCK 참조**: LOCK-AP-10 (Confidence < 50% HITL 트리거, **DEFINED-HERE**), LOCK-AP-02 (Permission Level 0~5), LOCK-AP-05 (Lead + max 2 Sub)
> **상태**: APPROVED — Phase 1 (V1)

---

## §0. 교차 참조 블록

| 정본 문서 | 섹션 | 참조 이유 |
|-----------|------|----------|
| `AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md` | §3.4 | LOCK-AP-02·AP-05·AP-10 (DEFINED-HERE) |
| `AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md` | §B.1~B.3 | 자율성 L0~L4 + 허용 작업 매트릭스 |
| `AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md` | §C.1~C.4 | 3-Phase 가드레일 아키텍처 + SG-001~SG-010 + HumanInterventionRequest 스키마 (정본) |
| `AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md` | §7.3.2 | Agent Teams V1 방식 C (Docker/E2B 샌드박싱) |
| `06_autonomy-safety/permission_matrix.md` | §3 공통 자료 구조 | ActionRequest, PermissionDecision, EscalationPayload 공유 |
| `06_autonomy-safety/permission_matrix.md` | §4 PermissionEnforcer | pre-action 가드레일 호출 지점 |
| `06_autonomy-safety/_index.md` | 가드레일 체계 | SG-001~SG-010 분류 참조 |
| `01_framework-adapters/langgraph_adapter.md` | §3 GatePolicy / §5.3 | G4 HITL → I-19 매핑 |
| `01_framework-adapters/autogen_adapter.md` | §10 EscalationPayload / §11 로그 | target_channel, 로그 nested 포맷 정합 |
| `01_framework-adapters/crewai_adapter.md` | code_execution_config / sandbox | K-043 샌드박싱 호출 지점 |
| `D:\VAMOS\docs\sot\STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md` | K-042, K-043 | 원본 요구사항 |
| `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` | I-19, CB, 자율성 | HITL I-19 채널 정의 |

---

## §1. Purpose & Scope

### 1.1 Purpose

본 문서는 VAMOS 에이전트의 **Human-in-the-Loop 승인 흐름 (K-042)** 과 **코드 실행 샌드박스 규격 (K-043)** 을 L3 수준에서 정의한다. 두 영역은 §C 안전 가드레일 규칙 엔진의 구체화 산출물이며, pre-action/runtime/post-action 3-Phase 가드 체계에 통합된다.

### 1.2 Scope

- **포함**: HITL 트리거 조건 / I-19 승인 흐름 / HumanInterventionRequest 처리 / Docker·E2B 샌드박스 구성 / 자원 제한 / 네트워크 정책 / 파일시스템 ACL / 샌드박스 이탈 감지 / Phase 2 통합 테스트 힌트
- **제외 (Phase 2 이후)**: K-047 자기진화 안전 가드레일 (V2, P2-6), K-044 비용 가드는 SG-001 만 참조 (본 문서 정본 아님), 프로덕션 Kubernetes PodSecurityPolicy 세부 (04_deployment-scaling 소유)

### 1.3 세션 간 인터페이스 cross-check

| 대상 산출물 | 확인 항목 | 결과 |
|-------------|----------|------|
| `permission_matrix.md` §3 `PermissionEnforcer.evaluate_pre_action_guards()` 호출 | 본 문서 §3 pre_action guard 체인과 시그니처 일치 | PASS |
| `permission_matrix.md` §3 `HumanInterventionRequest` | 본 문서 §4 사용 스키마 동일 (§C.4 정본) | PASS |
| `langgraph_adapter.md` §5.3 `router_fn == "hitl"` → G4 I-19 | 본 문서 §4 HITL 트리거와 일치 | PASS |
| `autogen_adapter.md` `AG-ADP-021` (sandbox 미구성) → I-19 | 본 문서 §5 샌드박스 부재 시 처리와 일치 | PASS |
| `permission_matrix.md` §8 로그 nested 포맷 | 본 문서 §7 로그 포맷 공통 | PASS |

---

## §2. 공통 자료 구조 참조

> `ActionRequest`, `PermissionDecision`, `HumanInterventionRequest`, `EscalationPayload` 는 `permission_matrix.md §3` 에서 정의된 것을 그대로 사용한다. 본 문서는 `GuardrailRule`, `GuardEvalResult`, `SandboxSpec`, `SandboxExecResult` 를 **추가 정의**한다.

```python
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field

GuardType = Literal["pre_action", "runtime", "post_action"]

class SafetyRule(BaseModel):
    """§C.2 정본 — 재정의 금지, 본 파일은 구현 바인딩만"""
    id: str                                          # "R-001" (§C.2 SafetyRule.id 형식)
    condition: str                                   # CEL 표현식
    action_on_violation: Literal["deny", "escalate", "modify", "log"]
    message: str
    cooldown_seconds: Optional[int] = None

class SafetyGuardrail(BaseModel):
    """§C.2 정본 — 재정의 금지"""
    id: str                                          # "SG-001"
    name: str
    type: GuardType
    autonomy_level_min: Literal[0, 1, 2, 3, 4]
    rules: list[SafetyRule]
    enforcement: Literal["block", "warn", "log"]

class GuardEvalResult(BaseModel):
    block: bool = False
    escalate: bool = False
    modify: bool = False
    warn: bool = False
    hits: list[str] = Field(default_factory=list)    # ["SG-003", "SG-005"]
    reasons: list[str] = Field(default_factory=list)
    code: Optional[str] = None                       # 최상위 위반 코드
    confidence_penalty: float = 0.0

class SandboxSpec(BaseModel):
    """K-043 샌드박스 실행 환경 규격"""
    engine: Literal["docker", "e2b"]                 # V1 지원 2종
    image: str                                       # e.g. "vamos/sandbox:python3.11-slim"
    cpu_limit: float = 1.0                           # cores
    mem_limit_mb: int = 2048
    disk_limit_mb: int = 1024
    timeout_ms: int = 30_000
    network_policy: Literal["deny", "egress_allowlist", "full"] = "egress_allowlist"
    allowed_egress_hosts: list[str] = Field(default_factory=list)
    readonly_rootfs: bool = True
    writable_paths: list[str] = Field(default_factory=lambda: ["/workspace"])
    allow_privileged: Literal[False] = False         # 고정
    user_ns_uid: int = 1000                          # non-root
    seccomp_profile: str = "default-deny-ptrace"
    capabilities_drop: list[str] = Field(default_factory=lambda: ["ALL"])
    env_whitelist: list[str] = Field(default_factory=list)
    trace_id: str

class SandboxExecResult(BaseModel):
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: int
    bytes_written: int
    bytes_network_out: int
    violations: list[str] = Field(default_factory=list)  # ["seccomp:ptrace", ...]
    error_code: Optional[str] = None
    trace_id: str
```

---

## §3. 3-Phase 가드레일 엔진 (§C.1 구현 바인딩)

### 3.1 전체 흐름

```
[ActionRequest]
      │
      ▼
┌──────────────────────────┐
│ Pre-Action Guard         │
│   SG-001 budget          │ ── deny → PE-005
│   SG-002 api_calls>100   │ ── escalate I-19
│   SG-003 PII             │ ── escalate I-19
│   SG-004 production      │ ── deny → PE-004
│   SG-005 autonomy        │ ── deny → PE-004
└──────────┬───────────────┘
           │ PASS
           ▼
┌──────────────────────────┐
│ Sandbox (K-043)          │ ← P2+ action
│   docker / e2b           │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Runtime Guard            │
│   SG-006 timeout×2       │ ── escalate I-19
│   SG-007 mem_over        │ ── deny + kill
│   SG-008 error_count>5   │ ── escalate I-19
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Post-Action Guard        │
│   SG-009 conf<0.5        │ ── escalate I-19 (LOCK-AP-10)
│   SG-010 irreversible    │ ── log+alert + HITL(L3)
└──────────┬───────────────┘
           │
           ▼
[결과 + ExplanationTrace(K-046) + TxLogEntry(K-045)]
```

### 3.2 Pre-action Guard 의사코드

```python
def evaluate_pre_action_guards(req: ActionRequest, agent) -> GuardEvalResult:
    """
    시간복잡도: O(R)  — R=활성 pre_action 규칙 수 (≤5, 상수)
    공간복잡도: O(R)
    LOCK 참조: AP-02 (Permission), AP-10 (Confidence 결과 평가는 post 에서)
    ABC 패턴: Interpreter (CEL 평가) + Chain of Responsibility
    """
    result = GuardEvalResult()
    for g in active_guards_for(agent.autonomy_level, phase="pre_action"):
        for rule in g.rules:
            if cel_eval(rule.condition, ctx=build_cel_ctx(req, agent)):
                result.hits.append(g.id)
                result.reasons.append(f"{g.id}: {rule.message}")
                # penalty 는 §6.2 표 기준으로 모든 위반 유형에 누적 (SG-009 는 hold=0)
                result.confidence_penalty += penalty_for(g.id)
                if rule.action_on_violation == "deny":
                    result.block = True
                    result.code = map_to_pe_code(g.id)
                elif rule.action_on_violation == "escalate":
                    result.escalate = True
                    result.code = map_to_pe_code(g.id)
                elif rule.action_on_violation == "modify":
                    result.modify = True
                elif rule.action_on_violation == "log":
                    result.warn = True
    return result
```

### 3.3 SG-001~SG-010 규칙 바인딩 표 (§C.3 정본)

> **정본**: §C.3 의 CEL 조건/위반시 액션/적용레벨 은 재정의 금지. 아래 표는 위 정본을 **구현 코드 매핑** 만 기록한다.

| ID | Type | CEL 조건 (§C.3 정본) | 위반 시 (§C.3) | 적용 | 매핑 PE 코드 | 채널 | confidence penalty |
|----|------|---------|--------|------|---------------|------|:-----------------:|
| SG-001 | pre | `action.estimated_cost_usd > agent.budget_remaining` | deny | L1+ | PE-005 | G5 hold | −0.10 |
| SG-002 | pre | `action.api_calls_count > 100` | escalate | L2+ | PE-006 | I-19 | −0.10 |
| SG-003 | pre | `action.data_scope contains 'PII'` | escalate | L0+ | PE-007 | I-19 | −0.15 |
| SG-004 | pre | `action.target_system in PRODUCTION_SYSTEMS` | deny | L0+ | PE-008 | - | −0.20 |
| SG-005 | pre | `action.autonomy_required > agent.current_level` | deny | L0+ | PE-004 | - | −0.15 |
| SG-006 | runtime | `execution.duration_ms > action.timeout_ms * 2` | escalate | L1+ | PE-041 | I-19 | −0.05 |
| SG-007 | runtime | `execution.memory_mb > agent.memory_limit_mb` | deny | L0+ | PE-042 | - | −0.10 |
| SG-008 | runtime | `execution.error_count > 5` | escalate | L2+ | PE-043 | I-19 | −0.10 |
| SG-009 | post | `result.confidence < 0.5` | escalate | L2+ **(LOCK-AP-10)** | **PE-010** | **I-19** | hold |
| SG-010 | post | `result.side_effects.count > 0 && !result.reversible` | log+alert | L3+ | PE-050 | I-19 (L3) | −0.30 |

### 3.4 예외 처리 정책 표

| error_code | 원인 | recoverable | 처리 |
|------------|------|:-----------:|------|
| `PE-004` | SG-005 autonomy 부족 | No | deny, downshift 제안 |
| `PE-005` | SG-001 budget 초과 | Yes (Gate G5) | deny, budget raise 요청 |
| `PE-006` | SG-002 api_calls>100 | Yes | escalate I-19 |
| `PE-007` | SG-003 PII | Yes | escalate I-19, K-046 Explanation 필수 |
| `PE-008` | SG-004 production | No | deny, audit log 영구 |
| `PE-010` | SG-009 conf<0.5 (LOCK-AP-10) | Yes | HITL I-19 |
| `PE-041` | SG-006 duration > ×2 | Yes | runtime kill, retry 1회 후 escalate |
| `PE-042` | SG-007 memory 초과 | No | sandbox kill, deny |
| `PE-043` | SG-008 error_count>5 | Yes | escalate I-19, retry 금지 |
| `PE-050` | SG-010 비가역 부작용 | L3+ only | log+alert + HITL (L3) |
| `PE-060` | 샌드박스 미구성 | No | deny (K-043) |
| `PE-061` | seccomp/cap 위반 | No | kill + I-20 |
| `PE-099` | 분류 불가 | No | I-20 post-mortem |

---

## §4. HITL 프로토콜 (K-042)

### 4.1 트리거 조건

| 조건 | 출처 | 채널 |
|------|------|------|
| `confidence < 0.5` | **LOCK-AP-10 (DEFINED-HERE)** / SG-009 | I-19 |
| L2 → L3 전환 | R-13-1 | I-19 |
| 비가역 작업 (L3+) | SG-010 | I-19 |
| 금융 트랜잭션 (P5) | `permission_matrix.md §2.1` | I-19 + 이중 승인 |
| SG-002 / SG-003 escalate | §C.3 | I-19 |
| `permission_matrix.md` PE-021 rollback 불가 | K-045 | I-19 |

### 4.2 HumanInterventionRequest 처리 흐름

```
[Guard 또는 Permission 위반]
        │
        ▼
[EscalationPayload 생성] target_channel="I-19"
        │
        ▼
[I-19 인터페이스]  ← D2.0-05 §HITL 정본
        │
        ├── notification_channels → ui / slack / email / sms
        │
        ▼
[HumanInterventionRequest] (§C.4 정본 스키마)
        │
        ├── urgency × autonomy_level 로 기본 timeout 결정
        │
        ▼
[사용자 응답] approve / deny / escalate
        │
        ├── approve → action 재개, confidence 복원
        ├── deny → rollback to last snapshot (K-045)
        └── escalate → I-20 post-mortem
        │
        ▼
[Post-resolution]  ← ExplanationTrace(K-046) + TxLogEntry(K-045) 업데이트
```

### 4.3 HITL Request 생성 의사코드

```python
def build_hitl_request(req: ActionRequest, dec: PermissionDecision,
                       guard_hits: list[str]) -> HumanInterventionRequest:
    """
    시간복잡도: O(1)
    LOCK 참조: AP-10 (트리거 조건)
    ABC 패턴: Factory Method
    """
    urgency = compute_urgency(
        guard_hits=guard_hits,
        required_permission=req.required_permission,
        autonomy=req.autonomy_required,
    )
    timeout = timeout_table(urgency)                 # low=300s, med=120s, high=60s, crit=30s
    return HumanInterventionRequest(
        request_id=new_uuid(),
        agent_id=req.agent_id,
        task_id=req.task_id,
        urgency=urgency,
        type=("approval" if req.required_permission >= 3 else "decision"),
        context={
            "action_description": req.action_name,
            "risk_assessment": assess_risk(req, guard_hits),
            "guardrail_violations": guard_hits,
            "suggested_options": suggest_options(req, dec),
            "autonomy_level": req.autonomy_required,
        },
        timeout_seconds=timeout,
        default_action=default_for(urgency),          # low="approve", high/crit="deny"
        notification_channels=route_channels(urgency),
    )
```

### 4.4 Timeout 기본 표 & default_action

| urgency | timeout | default_action | 비고 |
|---------|:-------:|:--------------:|------|
| low | 300s | approve | 낮은 리스크 |
| medium | 120s | deny | 기본 보수 |
| high | 60s | deny | SG-003 PII 등 |
| critical | 30s | deny | SG-004 production, PE-021 rollback 불가 |

### 4.5 Agent Teams V1 HITL 연동 (LOCK-AP-05 교차)

- Team (Lead + max 2 Sub) 의 HITL 은 **Lead 경유**로 1건만 생성. Sub 의 직접 HITL 생성 금지.
- `register_function` 에 P3+ 가 있으면 Lead level 로 승인 후 Sub 배포.

---

## §5. 샌드박스 규격 (K-043)

### 5.1 지원 엔진 (§7.3.2 방식 C 반영)

| 엔진 | 용도 | 허용 Permission | V1 디폴트 |
|------|------|----------------|:---------:|
| **Docker** | 일반 코드 실행 (Python/Node) | P2 이상 | Default |
| **E2B** | 격리가 더 강한 외부 실행 | P2 이상 (P4 권장) | alt |

> WebSocket 금지 (LOCK-AP-04 Streamable HTTP 만) — 샌드박스 통신도 HTTP/SSE 로 국한.

### 5.2 자원 제한 기본값 (SandboxSpec)

| 항목 | P2 기본 | P3 | P4 | 비고 |
|------|:-------:|:--:|:--:|------|
| cpu_limit | 1.0 | 2.0 | 2.0 | cores |
| mem_limit_mb | 2048 | 4096 | 4096 | |
| disk_limit_mb | 1024 | 2048 | 4096 | |
| timeout_ms | 30000 | 60000 | 120000 | |
| network_policy | `egress_allowlist` | `egress_allowlist` | `egress_allowlist` | deny / full 금지 |
| readonly_rootfs | True | True | True | 고정 |
| allow_privileged | False | False | False | **고정** |
| user_ns_uid | 1000 (non-root) | 1000 | 1000 | |
| capabilities_drop | ALL | ALL | ALL | |

### 5.3 네트워크 정책

- 기본: egress allowlist — approved-domains 만 허용.
- P3 이상: LLM provider / 결재 gateway / MCP server endpoint 만 허용 (origin별 per-host).
- P4 이상: allowlist 변경 시 HITL 승인.
- 금지: raw socket, ptrace, /proc 수정.

### 5.4 파일시스템 ACL

| 경로 | 권한 |
|------|------|
| `/workspace` | RW (writable_paths 기본) |
| `/tmp` | RW (ephemeral, 실행 종료 후 삭제) |
| `/etc/vamos/config` | RO |
| `/` (rootfs) | RO (readonly_rootfs=True) |
| `/var/run/docker.sock` | **절대 마운트 금지** |

### 5.5 샌드박스 실행 의사코드

```python
def run_in_sandbox(action: ActionRequest, spec: SandboxSpec) -> SandboxExecResult:
    """
    시간복잡도: O(N)  — N=표준출력 바이트
    LOCK 참조: AP-02 (Permission 기반 spec 선택), AP-04 (Streamable HTTP 만)
    ABC 패턴: Template Method (prepare → exec → collect → teardown)
    """
    assert spec.allow_privileged is False              # LOCK
    assert spec.readonly_rootfs is True
    assert "ALL" in spec.capabilities_drop

    container = provision_container(spec)              # docker-py / e2b sdk
    try:
        start_runtime_monitor(container, spec.timeout_ms)   # SG-006/SG-007
        result = container.exec_run(
            action.command,
            user=f"{spec.user_ns_uid}",
            environment=filter_env(spec.env_whitelist),
            read_only=True,
            network=spec.network_policy,
        )
        violations = collect_seccomp_violations(container)
        return SandboxExecResult(
            success=(result.exit_code == 0 and not violations),
            exit_code=result.exit_code,
            stdout=result.stdout[:MAX_LOG],
            stderr=result.stderr[:MAX_LOG],
            duration_ms=container.duration_ms,
            bytes_written=container.io_write,
            bytes_network_out=container.net_out,
            violations=violations,
            error_code=(None if not violations else "PE-061"),
            trace_id=action.trace_id,
        )
    except TimeoutError:
        container.kill()
        return _fail("PE-041", action, "timeout×2 (SG-006)")
    except MemoryError:
        container.kill()
        return _fail("PE-042", action, "memory over (SG-007)")
    except SandboxNotConfigured:
        return _fail("PE-060", action, "sandbox missing (K-043)")
    finally:
        teardown_container(container)                  # ephemeral
```

### 5.6 샌드박스 이탈 / 미구성 처리

- 감지: seccomp audit + AppArmor 로그.
- 위반 1건만으로 **즉시 kill** + `PE-061` I-20 post-mortem.
- 샌드박스 미구성 상태에서 P2+ action 시도 시 `PE-060` deny → I-19 제안 (autogen_adapter.md `AG-ADP-021` 과 정합).

---

## §6. Phase별 복구 흐름 + Confidence Penalty

### 6.1 Phase 흐름도

```
Phase 1 Intake ─→ Phase 2 Plan ─→ Phase 3 Execute ─→ Phase 4 Verify ─→ Phase 5 Deliver
     │                │                 │                   │                  │
     │                │                 │                   │                  └── SG-010 비가역 (L3+) → HITL I-19 + post log
     │                │                 │                   └── SG-009 conf<0.5 → HITL I-19 (LOCK-AP-10)
     │                │                 └── 샌드박스 위반 → PE-061 kill + I-20
     │                └── SG-005 autonomy_required > current → PE-004 deny + downshift
     └── SG-004 production → PE-008 deny (즉시)
```

### 6.2 다운그레이드 Confidence Penalty 표 (요약)

| SG ID | penalty | 채널 | 복구 |
|-------|:-------:|------|------|
| SG-001 | −0.10 | G5 hold | budget raise 요청 |
| SG-002 | −0.10 | I-19 | 승인 후 재시도 |
| SG-003 | −0.15 | I-19 | PII 필터 적용 후 재시도 |
| SG-004 | −0.20 | — | 영구 deny (production) |
| SG-005 | −0.15 | — | autonomy 승격 제안 |
| SG-006 | −0.05 | I-19 | retry 1회 후 escalate |
| SG-007 | −0.10 | — | 리소스 증설 또는 deny |
| SG-008 | −0.10 | I-19 | retry 금지 |
| SG-009 | hold (0) | I-19 | HITL 승인 대기 (LOCK-AP-10) |
| SG-010 | −0.30 | I-19 | 비가역 사후 감사 |
| PE-060 샌드박스 미구성 | −0.20 | — | 샌드박스 구성 요청 |
| PE-061 샌드박스 이탈 | −0.50 | I-20 | 강제 kill + post-mortem |

### 6.3 단계별 복구 전략

| Phase | 실패 유형 | 복구 | 에스컬레이션 |
|-------|----------|------|-------------|
| Intake | 입력 PII 감지 | 필터 + 재요청 | I-19 (SG-003) |
| Plan | autonomy 부족 | 계획 축소 | — (deny) |
| Execute | 샌드박스 이탈 | kill + snapshot rollback | **I-20 (PE-061)** |
| Execute | runtime timeout×2 | kill + retry×1 | I-19 (SG-006) |
| Verify | conf<0.5 | HITL 판정 | **I-19 (LOCK-AP-10)** |
| Deliver | 비가역 에러 | compensation → 불가 시 HITL | I-19 + I-20 |

---

## §7. 로깅 포맷 (R-01-7 structured JSON, 중첩)

```json
{
  "ts": "2026-04-11T11:05:22.004Z",
  "level": "ERROR",
  "logger": "guardrail_engine",
  "trace_id": "a8b1...7c",
  "event": "sandbox_escape_attempt",
  "error": {
    "code": "PE-061",
    "message": "seccomp violation: ptrace (K-043)",
    "class": "SandboxViolation",
    "stack_digest": "sha256:ab12..."
  },
  "context": {
    "agent_id": "agent-13",
    "task_id": "t-9912",
    "action_name": "exec_user_code",
    "sandbox_engine": "docker",
    "image": "vamos/sandbox:python3.11-slim",
    "permission_level": 2,
    "autonomy_level": 2,
    "vamos_phase": "execute"
  },
  "recovery": {
    "strategy": "kill_and_escalate_i20",
    "lock_violations": [],
    "last_snapshot_id": "snap-00742",
    "hitl_required": false,
    "confidence_after": 0.50
  }
}
```

> `permission_matrix.md §8` 과 **동일한 nested 3블록 + trace_id** 구조를 유지한다.

---

## §8. 에스컬레이션 페이로드

`permission_matrix.md §3` 의 `EscalationPayload` 를 재사용한다. `source_engine="permission_enforcer"` 대신 `"guardrail_engine"` 로 구분하는 것만 허용 (target_channel/lock_violations/trace_id 필드는 동일).

```python
class GuardrailEscalationPayload(BaseModel):
    source_engine: Literal["guardrail_engine"] = "guardrail_engine"
    target_channel: Literal["I-19", "I-20"]
    error_code: str                                   # "PE-061" 등
    original_request: "ActionRequest"
    partial_result: Optional[dict] = None
    retry_count: int = 0
    guard_hits: list[str] = Field(default_factory=list)  # ["SG-006", ...]
    lock_violations: list[str] = Field(default_factory=list)
    confidence_after_penalty: float
    trace_id: str
    timestamp: datetime
```

---

## §9. Phase 2 통합 테스트 시나리오 (10건 이상)

| # | 시나리오 | 주입 방법 | 기대 결과 |
|---|---------|----------|----------|
| GR-T01 | SG-001 budget 초과 | estimated_cost > remaining | `PE-005` deny, G5 hold |
| GR-T02 | SG-003 PII 감지 | data_scope=["PII"] | `PE-007` I-19 escalate, HITL high |
| GR-T03 | SG-004 production target | target_system=prod-db | `PE-008` deny, 영구 audit |
| GR-T04 | SG-005 autonomy 부족 | autonomy_required=3, current=1 | `PE-004` deny, downshift 제안 |
| GR-T05 | SG-009 confidence<0.5 | verify 후 0.42 | `PE-010` HITL I-19, LOCK-AP-10 준수 |
| GR-T06 | SG-010 비가역 부작용 | P4 email 발송 완료 | `PE-050` log+alert, L3 HITL |
| GR-T07 | 샌드박스 미구성 + P2 action | code_exec 요청 | `PE-060` deny, I-19 제안 |
| GR-T08 | 샌드박스 seccomp 이탈 | ptrace 시도 주입 | `PE-061` kill + I-20 post-mortem |
| GR-T09 | 샌드박스 timeout×2 | 60s 작업 + timeout 30s | `PE-041` runtime kill, I-19 |
| GR-T10 | 샌드박스 mem 초과 | 2.5GB alloc, limit 2GB | `PE-042` kill, deny |
| GR-T11 | HITL timeout default_action | urgency=high 60s 미응답 | default=deny, rollback snapshot |
| GR-T12 | LOCK-AP-05 team HITL 1건만 | Sub 3개 동시 HITL 시도 | Lead 경유 1건만 생성, 나머지 dedupe |
| GR-T13 | SG-002 api_calls>100 | 120회 호출 fixture | `PE-006` I-19 escalate |
| GR-T14 | 네트워크 allowlist 외 도메인 | 미등록 host | egress deny + `PE-061` I-20 |
| GR-T15 | 로그 nested 구조 검증 | 임의 guard hit 1건 | error/context/recovery 3블록 + trace_id 존재 |
| GR-T16 | HumanInterventionRequest 스키마 일치 | 생성 1건 | §C.4 정본 필드 전수 존재 |

---

## §10. ABC 패턴 매핑 요약

| 알고리즘 / 컴포넌트 | ABC 패턴 | 이유 |
|---------------------|---------|------|
| `evaluate_pre_action_guards` | Chain of Responsibility + Interpreter (CEL) | 규칙 순차 평가 |
| `SafetyGuardrail` 레지스트리 | Registry | id→규칙 조회 |
| `build_hitl_request` | Factory Method | urgency→timeout/default 선택 |
| `run_in_sandbox` | Template Method | prepare→exec→collect→teardown |
| SandboxEngine (docker/e2b) | Strategy | 동일 인터페이스, 엔진 교체 |
| GuardrailEscalationPayload routing | Adapter | I-19/I-20 채널 변환 |

---

## §11. LOCK-AP-10 DEFINED-HERE 정본 소유 선언

> **LOCK 참조 (출처: §3.4 LOCK-AP-10)**: `Confidence 임계값 — HITL 트리거 < 50%` — **DEFINED-HERE** (본 도메인 06_autonomy-safety 정본; MASTER_SPEC §5/§7.9 참조). 다른 도메인이 참조할 때는 반드시 본 파일 §4 / §3.3 SG-009 구현 규격을 따른다.

---

## §12. R6 준수 선언

본 문서는 **What+How** 만 기재한다. Phase/Week 일정 정보는 `AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md` §7 에만 존재한다.

---

## §13. 이슈/후속 작업

- K-047 자기진화 안전 가드레일은 V2 (P2-6 세션) 에서 본 파일 §3.3 에 SG-011+ 로 추가될 수 있음. 추가 시 LOCK-AP-10 재참조는 본 §11 정본 경유.
- Docker socket mount 금지는 §5.4 에 명시 — 04_deployment-scaling 의 배포 파이프라인은 별도 PodSecurityPolicy 로 이중 보장.
- `[CONFLICT_CANDIDATE: 없음]` — agent_mode_autonomy_mapping.md 와 정본 범위 충돌 0건 확인.

---

*정본 소유: #13 Agent-Protocol-Interoperability / 06_autonomy-safety*
*LOCK 참조: AP-02 (Level 0~5), AP-05 (Lead+2 Sub), AP-10 (HITL <50%, DEFINED-HERE)*

---

## §V2. V2-Phase 2 확장 (2026-04-22, STAGE 7 STEP_B #2c)

> **V2 태그**: V2-Phase 2 (append-only 확장, V1 §0~§13 + 상기 footer 본문 불변)
> **upstream baseline**: STEP7-K sha256 `150720a3496f557d359a421dcbf0922ebe5b1e4fbaa06611eff40e0865177539`
> **범위**: **K-047 에이전트 자기 진화 (Self-Evolution) 안전 가드레일** — STEP7-K L937~L955 원문 매핑 + Dream Mode 연동 (L947~L951) + **LOCK-AP-10 HITL<50% DEFINED-HERE 정본 cumulative 기준 확정** + max_strategy_drift 수치 확정 (4 P2-5 + 1 P2-4 참조자 정합 해제) + Permission L0~L4 자동 상한 + L5 금융 주문 절대 금지 + 자기진화 안전 가드레일 CEL SG-011~SG-015 + 에스컬레이션 payload.
> **LOCK 재확인**: LOCK-AP-02 (Permission Level 0~5) / LOCK-AP-05 (Lead + max 2 Sub-Agent) / LOCK-AP-09 (V1 ₩40K / V2 ₩93K / V3 ₩266K) / **LOCK-AP-10 (HITL 트리거 < 50%, DEFINED-HERE)** 본 §V2.2 정본 소유 확정.
> **경계**: K-048 에이전트 윤리 프레임워크 (STEP7-K L957~L975) 는 V3 범위이며 본 §V2 에서 **V2 EXTEND 없음** (§V2.1 매핑 대상 외). K-056 Kubernetes 오토스케일링 (L1101~L1111) / K-065~K-068 (L1254~L1318) 는 04_deployment-scaling + 05_self-evolution 의 V3 이관 항목으로 본 문서 범위 외.

### §V2.1 K-047 STEP7-K 원문 verbatim 매핑

STEP7-K `150720a3...` L937~L955 원문(19 lines)을 본 §V2 의 정본 입력으로 고정한다.

```
# STEP7-K L937~L955 verbatim (본 §V2 정본 입력)

### K-047. 에이전트 자기 진화 (Self-Evolution)
[VAMOS 독자 혁신]
- 에이전트 자동 개선 메커니즘:
  ├─ 성능 모니터링: 작업 성공률, 사용자 만족도 추적
  ├─ 프롬프트 자동 최적화: DSPy 기반 프롬프트 튜닝
  ├─ 도구 사용 패턴 학습: 효과적인 도구 조합 학습
  ├─ 실패 분석: 실패 원인 자동 분석 → 개선안 생성
  └─ A/B 테스트: 개선된 버전 vs 기존 버전 자동 비교

- Dream Mode 연동:                                   # L947~L951 — 05_self-evolution/dream_mode.md 소비자
  ├─ 비활성 시간에 과거 작업 복기
  ├─ 성능 병목점 식별
  ├─ 프롬프트/도구 최적화 실험
  └─ 다음 세션에 개선 사항 자동 적용

[구현성] V2: ⚠️ 4개월 | V3: ✅ 풀 자기진화
[참고 논문] "Self-Taught Reasoner (STaR)" (Zelikman et al., 2022)
```

**매핑 표**:

| 원문 블록 | STEP7-K line | 본 §V2 섹션 | 정본/참조자 |
|-----------|-------------:|-------------|------------|
| 성능 모니터링 (작업 성공률, 사용자 만족도) | L941 | §V2.4 Phase 1 (SG-011) | 정본 (본 문서) |
| 프롬프트 자동 최적화 (DSPy) | L942 | §V2.4 Phase 2 (SG-012) | 정본 (본 문서) |
| 도구 사용 패턴 학습 | L943 | §V2.4 Phase 3 (SG-013) | 정본 (본 문서) |
| 실패 분석 (원인 → 개선안) | L944 | §V2.4 Phase 4 (SG-014) | 정본 (본 문서) |
| A/B 테스트 (개선 vs 기존) | L945 | §V2.4 Phase 5 (SG-015) | 정본 (본 문서) |
| Dream Mode 비활성 시간 복기 | L948 | §V2.4 Phase 6 + §V2.3 | 05_self-evolution/dream_mode.md 소비자 |
| 성능 병목점 식별 | L949 | §V2.4 Phase 6 + Dream | 05_self-evolution/dream_mode.md 소비자 |
| 프롬프트/도구 최적화 실험 | L950 | §V2.3 drift 제한 | 05_self-evolution/dream_mode.md + predictive_agent.md 소비자 |
| 개선 사항 다음 세션 자동 적용 | L951 | §V2.5 Permission L2 상한 | 05_self-evolution/* 소비자 |
| [구현성] V2 4개월 / V3 풀 자기진화 | L953 | §V2.12 V 로드맵 | Part2 §6.7 + §7.4 P2-5/P2-6 |

### §V2.2 LOCK-AP-10 DEFINED-HERE 정본 확정 (cumulative 기준)

> **본 §V2.2 는 LOCK-AP-10 의 도메인 횡단 정본 소유처이다.** AUTHORITY_CHAIN.md §3 L51 (L50~L51) 에 `"LOCK-AP-10 | Confidence 임계값 | DEFINED-HERE (본 도메인 06_autonomy-safety 정본; MASTER_SPEC §5/§7.9 참조) | HITL 트리거 < 50% | 금지"` 5필드 verbatim 으로 등재되어 있으며, 9/9 V2 파일 (P2-4 container/healthcheck/logging/config/migration 5건 + P2-5 dream_mode/predictive_agent/ambient_agent/time_travel 4건) 은 본 §V2.2 를 참조자로 공식 정합 해제한다.

**LOCK-AP-10 verbatim 5필드 재인용**

| 필드 | 값 |
|------|-----|
| LOCK ID | `LOCK-AP-10` |
| 항목 | Confidence 임계값 |
| 원본 문서 | DEFINED-HERE (본 도메인 06_autonomy-safety 정본; MASTER_SPEC §5/§7.9 참조) |
| 값 | HITL 트리거 < 50% |
| 재정의 | 금지 |

**cumulative 계산식 (본 §V2.2 확정)**

LOCK-AP-10 "Confidence < 50% 시 HITL" 은 **단일 confidence 측정값**이 아니라, **시점 t 에서의 누적 confidence (cumulative_confidence)** 를 평가한다.

```
# V2-Phase 2 확정 계산식 (cumulative_confidence)
#   base_confidence:        당해 action 의 LLM + 게이트 체인 최종 confidence (0.0~1.0)
#   cumulative_penalty:     §V2.3 max_strategy_drift 위반 누계 (window=24h)
#   event_penalties:        §V2.3 표의 단일 이벤트 penalty 합 (window=24h)
#   adapter_drift:          prompt/tool_chain/strategy drift 3축 가중 합 (0.0~1.0)

cumulative_confidence(t) = base_confidence(t)
                           - sum(event_penalties_{24h})
                           - cumulative_penalty_{24h}
                           - w_strategy * adapter_drift(t)

# HITL 트리거 조건 (LOCK-AP-10 본 §V2.2 정본)
if cumulative_confidence(t) < 0.50:
    escalate_to_HITL(channel="I-19", reason="LOCK-AP-10 cumulative < 0.50")
```

**기본 가중치**

| 파라미터 | V2 값 | 근거 |
|----------|------:|------|
| `base_confidence` 하한 | 0.00 | GatePolicy 원본 입력 |
| `sum(event_penalties)` window | 24h rolling | 본 문서 §V2.3 표 |
| `cumulative_penalty` window | 24h rolling | 본 §V2.2 |
| `w_strategy` (adapter_drift 가중) | 0.25 | Phase 2 기본값 (Phase 3 튜닝 가능) |
| HITL 트리거 임계값 | < 0.50 | LOCK-AP-10 원본 값 (재정의 금지) |
| 초과 시 자동 동작 | pause + escalate I-19 | §V2.7 EscalationPayload |

**cumulative_confidence 하한**

| 구간 | 동작 |
|------|------|
| `cumulative_confidence ≥ 0.75` | 정상 실행 (가드레일 통과) |
| `0.50 ≤ cumulative_confidence < 0.75` | warn 로그 + 모니터링 강화 (SG-009 warn) |
| `cumulative_confidence < 0.50` | **HITL 트리거** (I-19) — LOCK-AP-10 본 §V2.2 정본 |
| `cumulative_confidence < 0.25` | **자기진화 실험 자동 중단** (pause Dream Mode + P0 알림) |

### §V2.3 `max_strategy_drift` 수치 확정 (참조자 정합 해제)

> **5 V2 소비자 참조**: `dream_mode.md §5.2 max_strategy_drift 표` + `predictive_agent.md §7.3 dispatch 게이팅` + `ambient_agent.md §9 penalty 표` + `time_travel.md §9 penalty 표` + `container_spec.md §9.2 penalty 표` — 전수 본 §V2.3 을 정본으로 참조.

**max_strategy_drift 정본 값** (24h rolling window, cumulative)

| 구간 | 임계값 | 동작 |
|------|:------:|------|
| `drift ≤ 0.10` | 허용 | 정상 실행 |
| `0.10 < drift ≤ 0.20` | warn | SG-011 warn 로그 + monitoring 강화 |
| `0.20 < drift ≤ 0.30` | escalate | HITL 승인 요청 (I-19) + Dream Mode 실험 지연 |
| `drift > 0.30` | **block** | **자기진화 실험 자동 중단 + P0 알림 + SG-014 post-action 로그** |

**drift 측정 3축** (가중 합계)

| 축 | 가중치 | 측정 방식 |
|----|:-----:|----------|
| `prompt_drift` | 0.40 | DSPy 최적화 이전/이후 프롬프트 embedding cosine distance |
| `tool_chain_drift` | 0.35 | 도구 호출 시퀀스 Levenshtein 비율 (1.0 = 완전 상이) |
| `strategy_drift` | 0.25 | 작업 분해 구조 (DAG) edit distance 정규화 |

```
adapter_drift(t) = 0.40 * prompt_drift(t)
                 + 0.35 * tool_chain_drift(t)
                 + 0.25 * strategy_drift(t)

# cumulative (window=24h)
cumulative_drift_{24h} = max(adapter_drift(t) for t in [now-24h, now])
```

**event_penalties 표 (5 V2 소비자 통합)**

| 이벤트 | penalty | 발생 소스 | 참조자 해제 |
|--------|:-------:|----------|------------|
| `max_strategy_drift > 0.30` | -0.20 | 본 §V2.3 정본 | dream_mode.md §5.2 (-0.20 정합) ✅ |
| `prompt DSPy 최적화 실패` | -0.15 | dream_mode.md §5.2 | ambient_agent.md §9 (-0.15 정합) ✅ |
| `도구 사용 실패 > 3회/24h` | -0.15 | dream_mode.md §5.2 | ambient_agent.md §9 (-0.15 정합) ✅ |
| `A/B 테스트 유의성 < 95%` | -0.10 | 본 §V2.3 정본 | dream_mode.md §5.2 (-0.10 정합) ✅ |
| `container digest drift (manifest vs runtime)` | -0.15 | container_spec.md §9.2 | container_spec.md §9.2 (-0.15 정합) ✅ |
| `healthcheck liveness 실패 > 3회/window` | -0.10 | healthcheck_spec.md §7.2 | healthcheck_spec.md §7.2 (-0.10 정합) ✅ |
| `Predictive dispatch confidence < 0.50` | -0.15 | predictive_agent.md §7.3 | predictive_agent.md §7.3 (-0.15 정합) ✅ |
| `Ambient P0 alert DND 위반` | -0.10 | ambient_agent.md §9 | ambient_agent.md §9 (-0.10 정합) ✅ |
| `Time-Travel replay divergence > ε` | -0.15 | time_travel.md §9 | time_travel.md §9 (-0.15 정합) ✅ |
| `config PATCH schema 위반` | -0.10 | config_spec.md §7.1 | config_spec.md §7.1 (-0.10 정합) ✅ |
| `migration rollback 발동` | -0.15 | migration_guide.md §6.3 | migration_guide.md §6.3 (-0.15 정합) ✅ |

**누적 임계**: `sum(event_penalties_{24h}) + cumulative_penalty_{24h} ≥ 0.30` 시 **무조건 HITL 트리거** (base_confidence/cumulative_confidence 값과 무관). 이 penalty-누적 HITL 은 §V2.2 cumulative_confidence < 0.50 HITL 과 독립적인 추가 게이트이며, 두 조건 중 하나라도 충족되면 HITL.

### §V2.4 자기진화 6 단계 가드레일 (SG-011 ~ SG-015 + Dream Mode)

K-047 원문 5 하위 메커니즘 + Dream Mode (1) = 6 단계 가드레일.

#### Phase 1 — SG-011 성능 모니터링 가드레일 (pre_action)

```python
SafetyGuardrail(
    id="SG-011",
    name="self_evolution_performance_monitoring",
    type="pre_action",
    autonomy_level_min=2,
    rules=[
        SafetyRule(
            id="R-13-7-1",
            condition=(
                "action.category == 'self_evolution' && "
                "metrics.success_rate_24h < 0.70"
            ),
            action_on_violation="escalate",
            message="자기진화 개선 직전 24h 성공률 70% 미만 — 실험 보류",
            cooldown_seconds=3600,
        ),
        SafetyRule(
            id="R-13-7-2",
            condition=(
                "action.category == 'self_evolution' && "
                "metrics.user_satisfaction_7d < 0.60"
            ),
            action_on_violation="escalate",
            message="사용자 만족도 60% 미만 — 실험 보류 + HITL 검토",
            cooldown_seconds=7200,
        ),
    ],
    enforcement="warn",
)
```

#### Phase 2 — SG-012 프롬프트 자동 최적화 가드레일 (runtime)

```python
SafetyGuardrail(
    id="SG-012",
    name="self_evolution_prompt_optimization",
    type="runtime",
    autonomy_level_min=2,
    rules=[
        SafetyRule(
            id="R-13-7-3",
            condition="action.tool == 'dspy.optimize' && context.prompt_drift > 0.20",
            action_on_violation="escalate",
            message="DSPy 프롬프트 drift 0.20 초과 — HITL 승인 필요",
        ),
        SafetyRule(
            id="R-13-7-4",
            condition="action.tool == 'dspy.optimize' && action.target_prompt.contains('LOCK-')",
            action_on_violation="deny",
            message="LOCK 참조 프롬프트는 자동 최적화 대상 외",
            cooldown_seconds=None,
        ),
    ],
    enforcement="block",
)
```

#### Phase 3 — SG-013 도구 사용 패턴 학습 가드레일 (runtime)

```python
SafetyGuardrail(
    id="SG-013",
    name="self_evolution_tool_pattern_learning",
    type="runtime",
    autonomy_level_min=1,
    rules=[
        SafetyRule(
            id="R-13-7-5",
            condition="action.category == 'tool_chain_update' && context.tool_chain_drift > 0.25",
            action_on_violation="escalate",
            message="tool_chain_drift 0.25 초과 — Phase 3 검토 필요",
        ),
        SafetyRule(
            id="R-13-7-6",
            condition="action.tool.permission_level > 3 && context.is_self_evolution == true",
            action_on_violation="deny",
            message="자기진화 경로에서 Permission L4+ 도구 사용 금지 (§V2.5)",
        ),
    ],
    enforcement="block",
)
```

#### Phase 4 — SG-014 실패 분석 가드레일 (post_action)

```python
SafetyGuardrail(
    id="SG-014",
    name="self_evolution_failure_analysis",
    type="post_action",
    autonomy_level_min=1,
    rules=[
        SafetyRule(
            id="R-13-7-7",
            condition="failure_analysis.generated_patch.touches_LOCK == true",
            action_on_violation="deny",
            message="실패 분석 자동 패치가 LOCK 영역 수정 — 전체 거부",
        ),
        SafetyRule(
            id="R-13-7-8",
            condition="failure_analysis.confidence < 0.50",
            action_on_violation="escalate",
            message="LOCK-AP-10 본 §V2.2 cumulative_confidence < 0.50 — HITL",
        ),
    ],
    enforcement="block",
)
```

#### Phase 5 — SG-015 A/B 테스트 가드레일 (runtime)

```python
SafetyGuardrail(
    id="SG-015",
    name="self_evolution_ab_test",
    type="runtime",
    autonomy_level_min=2,
    rules=[
        SafetyRule(
            id="R-13-7-9",
            condition="ab_test.traffic_share > 0.30 && context.is_production == true",
            action_on_violation="deny",
            message="자기진화 A/B 테스트 트래픽 30% 초과 금지 (Phase 2)",
        ),
        SafetyRule(
            id="R-13-7-10",
            condition="ab_test.significance < 0.95 && ab_test.arm == 'experiment'",
            action_on_violation="escalate",
            message="A/B 통계적 유의성 95% 미만 — 승인 후 정식 전환",
        ),
        SafetyRule(
            id="R-13-7-11",
            condition="ab_test.duration_hours < 24 && ab_test.arm == 'experiment'",
            action_on_violation="escalate",
            message="A/B 최소 24h 수행 전 조기 종결 금지",
        ),
    ],
    enforcement="block",
)
```

#### Phase 6 — Dream Mode 연동 가드레일 (pre_action + runtime)

Dream Mode (05_self-evolution/dream_mode.md) 는 본 §V2.4 Phase 1~5 의 6번째 단계로 통합된다. Dream Mode 실행은 아래 3 중 가드를 모두 통과해야 한다.

| 체크 | 조건 | 실패 시 |
|------|------|--------|
| D-1 | `active_time == false` (사용자 비활성 시간, idle ≥ 5min) | pause (Dream Mode 미진입) |
| D-2 | `autonomy_level ∈ {L0, L1, L2}` (§V2.5 상한) | deny (Permission 위반) |
| D-3 | `cumulative_drift_{24h} ≤ 0.20` (§V2.3) | escalate (HITL 승인 후 실행) |

> Dream Mode 내부 실험이 `max_strategy_drift > 0.30` 발생 시 **자동 중단 + HITL 알림** (SG-014 R-13-7-7 자동 발동).

### §V2.5 Permission L0~L4 자동 상한 + L5 금융 주문 절대 금지

> **LOCK-AP-02 (Permission Level 0~5) verbatim 5필드 재인용**: `LOCK-AP-02 | 에이전트 권한 레벨 | STEP7-K K-041 | Permission Level 0~5 (읽기→금융) | 금지`

**자기진화 × Permission 상한 표**

| Permission Level | 자기진화 허용 | 자동 적용 | 근거 |
|:---------------:|:------------:|:---------:|------|
| **L0 READ_ONLY** | ✅ | ✅ 자동 | 부작용 없음 |
| **L1 READ_WRITE_LOCAL** | ✅ | ✅ 자동 | 에이전트 로컬 스코프 |
| **L2 EXEC_SANDBOX** | ✅ | ✅ 자동 (K-043 샌드박스 내부) | 샌드박스 격리 보장 |
| **L3 EXTERNAL_API** | ⚠️ 조건부 | ❌ **HITL 필수** | 외부 영향 범위 확대 |
| **L4 IRREVERSIBLE_SIDE_EFFECTS** | ❌ | ❌ 금지 | 비가역 외부 상태 변경 |
| **L5 FINANCIAL_TX** | ❌ **절대 금지** | ❌ **LOCK-AP-02 + 본 §V2.5 이중 차단** | 금융 주문은 항상 사용자 확인 |

**V2 확정 규칙** (본 §V2.5 정본)

1. **L0~L2 자동**: 자기진화 경로에서 자동으로 실행 가능.
2. **L3 HITL**: 외부 API 호출을 자기진화 경로가 제안하려면 I-19 HITL 승인 필수 (R-13-7-6).
3. **L4~L5 금지**: 비가역/금융 작업은 자기진화 경로에서 **생성조차 금지**. permission_matrix.md §V2 참조.
4. **L5 이중 차단**: LOCK-AP-02 원본 "(항상 사용자 확인)" + 본 §V2.5 "자기진화 경로 절대 금지" 로 **이중 방어**. `is_self_evolution == true && action.permission_level == 5` 조합은 즉시 SG-013 R-13-7-6 deny.

### §V2.6 자기진화 안전 가드레일 CEL (§C 계획서 정본 보강)

계획서 §C 가드레일 CEL 에 본 §V2.6 가 SG-011~SG-015 CEL 표현식을 추가한다. 기존 §C.1~§C.4 CEL 본문 불변, §C.5 으로 확장된다.

**SG-011 ~ SG-015 CEL verbatim**

```
# SG-011 performance monitoring (pre_action)
R-13-7-1: action.category == "self_evolution" && metrics.success_rate_24h < 0.70
R-13-7-2: action.category == "self_evolution" && metrics.user_satisfaction_7d < 0.60

# SG-012 prompt optimization (runtime)
R-13-7-3: action.tool == "dspy.optimize" && context.prompt_drift > 0.20
R-13-7-4: action.tool == "dspy.optimize" && action.target_prompt.contains("LOCK-")

# SG-013 tool pattern learning (runtime)
R-13-7-5: action.category == "tool_chain_update" && context.tool_chain_drift > 0.25
R-13-7-6: action.tool.permission_level > 3 && context.is_self_evolution == true

# SG-014 failure analysis (post_action)
R-13-7-7: failure_analysis.generated_patch.touches_LOCK == true
R-13-7-8: failure_analysis.confidence < 0.50

# SG-015 A/B test (runtime)
R-13-7-9:  ab_test.traffic_share > 0.30 && context.is_production == true
R-13-7-10: ab_test.significance < 0.95 && ab_test.arm == "experiment"
R-13-7-11: ab_test.duration_hours < 24 && ab_test.arm == "experiment"
```

### §V2.7 에스컬레이션 Payload (Pydantic + structured JSON 3-block)

```python
from typing import Literal, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class SelfEvolutionEscalation(BaseModel):
    """§V2 에스컬레이션 전용 payload — EscalationPayload 상속 (permission_matrix.md §3)"""
    trigger_rule_id: str                                 # "R-13-7-1" ~ "R-13-7-11"
    guardrail_id: Literal["SG-011","SG-012","SG-013","SG-014","SG-015"]
    base_confidence: float = Field(ge=0.0, le=1.0)
    cumulative_confidence: float = Field(ge=0.0, le=1.0)
    cumulative_drift_24h: float = Field(ge=0.0, le=1.0)
    event_penalties: list[dict]                          # [{event, penalty, ts}, ...]
    phase: Literal[1,2,3,4,5,6]                          # §V2.4 Phase 1~6
    target_channel: Literal["I-19","I-20"]               # HITL
    trace_id: str
    escalated_at: datetime
    recommendation: Optional[str] = None                 # LLM 권고안 (optional)
```

**structured JSON 3-block** (autogen_adapter.md §11 nested `error/context/recovery` 정합)

```json
{
  "error": {
    "code": "SELF_EVO_GUARD_TRIGGERED",
    "rule_id": "R-13-7-7",
    "guardrail_id": "SG-014",
    "message": "failure_analysis.generated_patch.touches_LOCK == true"
  },
  "context": {
    "phase": 4,
    "base_confidence": 0.72,
    "cumulative_confidence": 0.38,
    "cumulative_drift_24h": 0.22,
    "event_penalties": [
      {"event": "max_strategy_drift > 0.30", "penalty": -0.20, "ts": "..."},
      {"event": "도구 사용 실패 > 3회/24h", "penalty": -0.15, "ts": "..."}
    ],
    "patch_summary": "<redacted>",
    "target_file": "<redacted>"
  },
  "recovery": {
    "action": "deny",
    "next_step": "escalate_to_HITL",
    "channel": "I-19",
    "cooldown_seconds": null,
    "recommendation": "LOCK 영역 자동 패치 금지 — 수동 설계 검토 필요"
  }
}
```

### §V2.8 Phase 3 통합 테스트 시나리오 (≥ 10건)

| # | ID | 시나리오 | 검증 기준 |
|---|-----|---------|----------|
| 1 | SE-01 | 성공률 < 70% 시 자기진화 실험 보류 | SG-011 R-13-7-1 escalate 발동 |
| 2 | SE-02 | 사용자 만족도 < 60% → HITL | SG-011 R-13-7-2 escalate 발동 |
| 3 | SE-03 | DSPy drift 0.25 → HITL | SG-012 R-13-7-3 escalate 발동 |
| 4 | SE-04 | LOCK 참조 프롬프트 자동 최적화 시도 → deny | SG-012 R-13-7-4 차단 |
| 5 | SE-05 | tool_chain_drift 0.28 → Phase 3 검토 | SG-013 R-13-7-5 escalate 발동 |
| 6 | SE-06 | 자기진화 경로에서 L4 외부 API 호출 시도 → deny | SG-013 R-13-7-6 차단 (L3+ HITL) |
| 7 | SE-07 | 실패 분석 자동 패치가 LOCK 영역 수정 시도 → deny | SG-014 R-13-7-7 차단 |
| 8 | SE-08 | failure_analysis.confidence 0.45 (cumulative < 0.50) → HITL | SG-014 R-13-7-8 LOCK-AP-10 발동 |
| 9 | SE-09 | A/B 트래픽 35% → deny (Phase 2 상한 30%) | SG-015 R-13-7-9 차단 |
| 10 | SE-10 | A/B 유의성 92% 조기 종결 시도 → HITL | SG-015 R-13-7-10 escalate |
| 11 | SE-11 | A/B 18h 수행 후 종결 시도 → HITL | SG-015 R-13-7-11 escalate (<24h) |
| 12 | SE-12 | Dream Mode 활성 시간(사용자 활동 중) 진입 시도 → pause | D-1 체크 실패 |
| 13 | SE-13 | Dream Mode cumulative_drift 0.25 → HITL | D-3 체크 escalate |
| 14 | SE-14 | 금융 L5 자기진화 경로 제안 → deny (이중 차단) | LOCK-AP-02 + §V2.5 R-13-7-6 |
| 15 | SE-15 | cumulative_confidence 0.22 → 자기진화 실험 자동 중단 + P0 | §V2.2 < 0.25 구간 |

> **≥10 충족**: 15건 (목표 ≥ 10건 1.5배 초과).

### §V2.9 세션 간 인터페이스 cross-check (5 V2 참조자 정합 해제)

| 참조자 V2 파일 | 참조 지점 | 본 §V2.x 정합 | 결과 |
|----------------|----------|---------------|------|
| `05_self-evolution/dream_mode.md` §5.2 max_strategy_drift 표 | `> 0.30 → -0.20` | §V2.3 event_penalties 표 -0.20 | **PASS** (정합) |
| `05_self-evolution/predictive_agent.md` §7.3 dispatch 게이팅 | `confidence < 0.50 → dispatch 차단` | §V2.2 LOCK-AP-10 cumulative < 0.50 | **PASS** (정합) |
| `05_self-evolution/ambient_agent.md` §9 penalty 표 | `-0.15 (DSPy 실패) / -0.10 (P0 DND 위반)` | §V2.3 event_penalties 표 동일 | **PASS** (정합) |
| `05_self-evolution/time_travel.md` §9 penalty 표 | `-0.15 (replay divergence)` | §V2.3 event_penalties 표 동일 | **PASS** (정합) |
| `04_deployment-scaling/container_spec.md` §9.2 penalty 표 | `-0.15 (digest drift), -0.10 (health liveness)` | §V2.3 event_penalties 표 동일 | **PASS** (정합) |

**자율 검증 grep 지점**

```
# 5 V2 참조자가 본 §V2.3 event_penalties 표와 정합하는지 실측
grep -n "max_strategy_drift\|cumulative_drift\|-0.20\|-0.15\|-0.10" \
  05_self-evolution/*.md \
  04_deployment-scaling/container_spec.md \
  04_deployment-scaling/healthcheck_spec.md
# 예상 매치: 본 §V2.3 event_penalties 표와 동일 수치 (재정의 0)
```

### §V2.10 자가 검증 체크리스트 (V1 EXTEND 원칙 + §V2 품질)

- [x] V1 §0~§13 + footer 본문 불변 (append-only 엄수)
- [x] V2-Phase 2 태그 + STAGE 7 STEP_B #2c 명시
- [x] upstream baseline STEP7-K sha256 `150720a3...` 명시 + 불변 엄수
- [x] K-047 원문 verbatim 매핑 (§V2.1, 19 lines) — Dream Mode 연동 L947~L951 포함
- [x] **LOCK-AP-10 DEFINED-HERE 정본 cumulative 기준 확정** (§V2.2, 5필드 + 계산식 + 구간 4단계)
- [x] max_strategy_drift 수치 확정 (§V2.3, event_penalties 11 rows)
- [x] 자기진화 6 Phase SG-011~SG-015 CEL (§V2.4, §V2.6)
- [x] Permission L0~L4 자동 상한 + L5 절대 금지 이중 차단 (§V2.5)
- [x] 에스컬레이션 Pydantic + 3-block JSON (§V2.7, autogen §11 nested 정합)
- [x] Phase 3 테스트 시나리오 ≥ 10건 (§V2.8, 15건)
- [x] 5 V2 참조자 정합 해제 cross-check (§V2.9)
- [x] LOCK-AP-02/AP-05/AP-09/AP-10 verbatim 5필드 분리 인용 (§V2.11)
- [x] FABRICATION 10종 census 0 hits (본 §V2 append 전체 scope)
- [x] K-048 에이전트 윤리 (L957~L975) V3 이관 명시 (§V2 경계 주석)
- [x] K-056 K8s / K-065~K-068 V3 이관 명시 (§V2 경계 주석)
- [x] parent-executed (Subagent 0회)
- [x] sandbox-only (production guardrail_rules.md SHA UNCHANGED 엄수)

### §V2.11 LOCK 5필드 매핑 (V2 재확인)

| LOCK ID | 항목 | 원본 문서 | 값 | 재정의 | V2 사용 지점 |
|---------|------|----------|-----|--------|--------------|
| LOCK-AP-02 | 에이전트 권한 레벨 | STEP7-K K-041 | Permission Level 0~5 (읽기→금융) | 금지 | §V2.5 자기진화 × Permission 표 + L5 절대 금지 |
| LOCK-AP-05 | Agent Teams V1 제한 | Part2 §6.7 LOCK-AT-014 (값 일치 확인: 6-3 LOCK-AT-014 참조) | Lead + max 2 Sub-Agent | 금지 | §V2.4 Phase 1~6 모두 `agents.length ≤ 2` 엄수 |
| LOCK-AP-09 | 비용 상한 | Part2 §비용 + 가이드 부록 D (STEP7-H 참조) | V1: ₩40K, V2: ₩93K, V3: ₩266K | 금지 | 자기진화 A/B 테스트 V2 ₩93K 예산 내 (§V2.8 SE-09) |
| **LOCK-AP-10** | Confidence 임계값 | **DEFINED-HERE (본 도메인 06_autonomy-safety 정본; MASTER_SPEC §5/§7.9 참조)** | HITL 트리거 < 50% | 금지 | **§V2.2 본 §V2 정본 소유** + §V2.3 cumulative + 5 V2 참조자 정합 해제 (§V2.9) |

### §V2.12 V 로드맵 + Phase 3 이월 항목 + FABRICATION 10종 census

**V 로드맵 (K-047 L953)**

| 버전 | 상태 | 범위 |
|:----:|:----:|------|
| V1 | — | K-047 자기진화는 V1 범위 외 (STEP7-K L953 "V2: ⚠️ 4개월") |
| **V2** | **본 §V2.1~§V2.11 정본** | 성능 모니터링 + DSPy + 도구 패턴 + 실패 분석 + A/B + Dream Mode 연동 (MVP) |
| V3 | Phase 3 이월 | 풀 자기진화 (K-065~K-068 멀티 페르소나 + 멀티유저 + 마켓플레이스) |

**Phase 3 이월 항목 (본 §V2 범위 외)**

1. K-048 에이전트 윤리 프레임워크 (STEP7-K L957~L975) — V3 Constitutional AI 연동
2. K-056 Kubernetes 오토스케일링 (L1101~L1111) — V3 04_deployment-scaling
3. K-065~K-068 멀티 페르소나/멀티유저/마켓플레이스/VBS-12+ (L1254~L1318) — V3 05_self-evolution
4. `w_strategy` 가중치 0.25 Phase 3 튜닝 (§V2.2)
5. A/B 트래픽 상한 30% → V3 50% 확장 검토 (§V2.8 SE-09)

**FABRICATION 10종 census** (본 §V2 전체 범위, append-only)

| Marker | hits |
|--------|:----:|
| `[FICTION]` | 0 |
| `[PLACEHOLDER]` | 0 |
| `[TBD]` | 0 |
| `[UNVERIFIED]` | 0 |
| `[GUESS]` | 0 |
| `[ASSUMED]` | 0 |
| `[HYPOTHETICAL]` | 0 |
| `[FAKE]` | 0 |
| `[STUB]` | 0 |
| `[MOCK_VALUE]` | 0 |

**TOTAL: 0/10 CLEAN** — parent-executed 100%, Subagent 0회 유지.

---

*V2-Phase 2 확장 작성: 2026-04-22 (STAGE 7 STEP_B #2c, 3-10 P2-6 세션, 도메인 마감 직전)*
*본 §V2.2 LOCK-AP-10 DEFINED-HERE cumulative 기준 본 문서 정본 소유 확정*
*5 V2 참조자 (dream_mode / predictive_agent / ambient_agent / time_travel / container_spec) 정합 해제 완료*

---

## §V3. Phase 4 추가 이월 통합 정밀화 (SE-09) — append-only, V2 영역 byte 무변경

> **Phase 4 태그**: V3-Phase 4 production-ready 정본 승급 (RECOVERY genuine write, P4-5)
> **Status**: APPROVED (DRAFT → APPROVED, 2026-06-03)
> **append-only 원칙**: 본 §V3 는 §V2 이하 영역을 일절 변경하지 않는다 (prefix EXACT). LOCK-AP-02/10 verbatim, DEFINED-HERE §V2.2 무변경.

### §V3.1 `w_strategy` 가중치 0.25 → A/B 기반 튜닝 (이월 #1)

Phase 2 §V2.2 cumulative 식의 `w_strategy = 0.25` (adapter_drift 가중) 는 Phase 2 기본값으로 확정되었다. Phase 3/4 운영 데이터 기반 A/B 튜닝을 다음 범위로 정밀화한다 — **기준값 ±0.05 범위 내 (0.20 ~ 0.30)**. §V2.2 정본 식 `cumulative_confidence = base - sum(event_penalties_{24h}) - cumulative_penalty_{24h} - w_strategy * adapter_drift(t)` 의 구조는 불변, `w_strategy` 만 운영 측정 기반 조정.

| 항목 | Phase 2 기본 (§V2.2) | V3 튜닝 범위 | 트리거 |
|------|:--------------------:|:-----------:|--------|
| `w_strategy` | 0.25 | 0.20 ~ 0.30 (±0.05) | A/B 측정 신뢰도 > 95% 시에만 조정 |
| 조정 단위 | — | ±0.01/회 | 회귀 알람 시 즉시 롤백 |

> ±0.05 초과 변경은 §V2.2 정본 변경으로 간주 → 금지 (LOCK-AP-10 DEFINED-HERE 보호).

### §V3.2 A/B 트래픽 상한 30% → V3 50% 확장 (이월 #2, SE-09)

Phase 2 SG-015 R-13-7-9 의 A/B 테스트 트래픽 상한 30% (SE-09: `A/B 트래픽 35% → deny`) 를 V3 에서 **50% 로 단계적 확장**한다. 단, 안전 가드 동반 필수.

```python
# §V3.2 A/B 트래픽 상한 V3 확장 (SE-09 정밀화)
def ab_traffic_guard_v3(traffic_ratio: float, error_delta_pp: float) -> str:
    if traffic_ratio > 0.50:                  # V3 상한 (Phase 2 는 0.30)
        return "deny"                          # SG-015 R-13-7-9 V3
    if error_delta_pp >= 0.5:                  # 에러율 +0.5%p
        return "rollback"                      # 즉시 롤백 (회귀 알람)
    return "allow"
```

| 단계 | 트래픽 상한 | 회귀 알람 | 비고 |
|------|:----------:|----------|------|
| Phase 2 (SE-09) | 30% | — | 기존 정본 |
| V3 단계 1 | 40% | 에러율 +0.5%p 즉시 롤백 | 안전성 입증 후 |
| V3 단계 2 | 50% | 에러율 +0.5%p 즉시 롤백 | 단계 1 PASS 후 |

### §V3.3 LOCK 재확인 + CFL 무손상

> **LOCK 재확인 (재정의 0)**: LOCK-AP-02 (Permission Level 0~5) / LOCK-AP-10 (HITL < 50%, DEFINED-HERE 본 §V2.2 정본 — §V3 는 참조자, byte 무변경). w_strategy ±0.05 / A/B 50% 는 운영 파라미터 정밀화이며 LOCK 값 변경 아님.
> **CFL-AP-001~007 무손상**: Phase 4 신규 충돌 발화 0건 strict (자동 RESOLVE 금지 원칙 엄수).

> 완전 무인 자동화(A/B 자동 승인 무인화)는 안전성 추가 입증 후 **Phase 4+ 이월** (본 §V3 는 50% 확장 + 안전 가드까지).

---

*V3-Phase 4 추가 이월 통합 정밀화: 2026-06-03 (RECOVERY genuine write, P4-5, append-only)*
*§V2 이하 영역 byte 무변경 (prefix EXACT) — DEFINED-HERE §V2.2 LOCK-AP-10 정본 무손상*
