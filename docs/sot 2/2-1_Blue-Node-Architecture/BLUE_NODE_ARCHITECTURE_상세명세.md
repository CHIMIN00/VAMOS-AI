# 2-1. Blue Node Architecture 상세명세

> **Tier**: 2 - Domain Execution (Blue Node 계층)
> **Part2 상태**: GAP (SOT D2.0-03 §1~§6에 정의되어 있으나 Part2에 미구현)
> **SOT 근거**: D2.0-03 §3.2~§3.3, §4.1~§4.2, §5.2, §6; D2.0-01 S4; STEP7 K-010, K-029, K-041, K-049
> **Part2 위치**: V2-Phase 1~2 (Blue Node 관련 섹션)

---

## 개요

Blue Node는 VAMOS의 도메인 실행 계층으로, ORANGE CORE로부터 위임받은 작업을 도메인 특화 방식으로 처리한다. Part2에는 Blue Node의 기본 구조(이름, 역할)만 존재하며, 권한 매트릭스·인터페이스 계약·템플릿 주입·라이프사이클·메모리 공유·정책 오버라이드·MCP 브리지 등 7개 핵심 아키텍처 요소가 누락되어 있다.

본 문서는 SOT D2.0-03 §1~§6에 정의된 Blue Node 아키텍처의 상세 명세를 제공한다.

---

## 1. Permission Matrix (K-041): Level 0~5 권한 매트릭스

### SOT 근거
- STEP7 K-041: Blue Node별 레벨 기반 권한 제어
- D2.0-03 §6.1: Event Registry (⚠️ 원문은 이벤트 레지스트리, "보안 및 접근 제어 정책" 직접 해당 아님 — 접근 제어는 D2.0-03 §1 P0/P1/P2 제약 + D2.0-07 참조)

### 1.1 권한 레벨 정의

| Level | 이름 | 설명 | 허용 범위 |
|-------|------|------|-----------|
| 0 | `READ` (읽기전용) | 정보 조회·검색만 허용 | 데이터 열람, 검색 쿼리 |
| 1 | `CREATE` (생성) | 새 리소스 생성 허용 | 파일 생성, 코드 생성 |
| 2 | `MODIFY` (수정) | 기존 리소스 변경 허용 | 파일 수정, 설정 변경 |
| 3 | `EXECUTE` (실행) | 코드·API 실행 허용 | 코드 실행, API 호출 |
| 4 | `EXTERNAL` (외부통신) | 외부 시스템 통신 허용 | 이메일 발송, PR 생성 (노드별 Ask) |
| 5 | `FINANCIAL` (금융) | 금융 거래 허용 (항상 사용자 확인 필수) | 주문 실행, 결제 |

> **LOCK-BN-02 정본**: Level 정의는 01_permission-matrix/_index.md §1 (D2.0-03 §4 K-041) 정본을 따른다. 본 표는 정본을 참조하며 재정의하지 않는다.

### 1.2 입출력 스키마

```python
class PermissionEntry(BaseModel):
    node_id: str                    # Blue Node 식별자
    resource_type: str              # 리소스 유형 (memory, tool, api, file)
    level: int                      # 0~5
    granted_by: str                 # 권한 부여자 (ORANGE CORE 또는 상위 노드)
    expires_at: Optional[datetime]  # 만료 시간 (None=영구)
    conditions: dict[str, Any]      # 동적 조건 (시간대, 사용량 등)

class PermissionMatrix(BaseModel):
    node_id: str
    entries: list[PermissionEntry]
    default_level: int = 1          # 미지정 리소스에 대한 기본 레벨
    escalation_policy: str          # "ask_user" | "deny" | "escalate_core"

class PermissionCheckRequest(BaseModel):
    requester_node_id: str
    target_resource: str
    action: Literal["read", "write", "execute", "admin"]
    context: dict[str, Any]         # 런타임 컨텍스트 (부하, 시간대 등)

class PermissionCheckResult(BaseModel):
    allowed: bool
    effective_level: int
    reason: str
    audit_log_id: str               # 감사 로그 ID
```

### 1.3 동적 권한 조정 알고리즘

```python
class DynamicPermissionAdjuster:
    """런타임 조건에 따라 권한 레벨을 동적으로 조정"""

    async def adjust(self, node_id: str, context: RuntimeContext) -> int:
        base_level = await self.get_base_level(node_id)

        # 조건별 조정 — 하향만 허용 (LOCK-BN-17 "Only Stricter"). 상향은 절대 불가;
        # 권한 상향은 ORANGE CORE 매트릭스 재설정(07 Gate 승인)으로만 가능 (01 §5.2/§8.2).
        adjustments = []
        if context.error_rate > 0.1:
            adjustments.append(-1)          # 에러율 높으면 레벨 하향
        if context.is_peak_hours:
            adjustments.append(-1)          # 피크 시간 보수적 운영

        # 하향만 반영: 양수 합산은 무시 (min(0, ...))
        effective = max(0, base_level + min(0, sum(adjustments)))

        await self.audit_log(node_id, base_level, effective, adjustments)
        return effective
```

### 1.4 Blue Node별 기본 권한 매트릭스 (예시)

| Blue Node | memory | tool | api | file | cross_domain |
|-----------|--------|------|-----|------|--------------|
| BN-WebResearch | 2 | 3 | 3 | 1 | 2 |
| BN-CodeEngine | 3 | 4 | 2 | 3 | 2 |
| BN-PKM | 3 | 2 | 1 | 4 | 3 |
| BN-Education | 2 | 2 | 2 | 2 | 1 |
| BN-Health | 2 | 2 | 3 | 2 | 1 |

### 1.5 의존성
- **상위**: ORANGE CORE 정책 엔진 (D2.0-07 §4.3.2/S7E-050 ApprovalManager)
- **하위**: 모든 Blue Node 실행 시 권한 체크 선행
- **연관**: K-029 Memory Sharing Protocol (메모리 접근 권한)

---

## 2. CORE-NODE Interface Contract (SS5.2): VamosMessage 표준 포맷

### SOT 근거
- D2.0-03 SS5.2: CORE-NODE 간 통신 계약
- STEP7 K-049: VamosMessage 표준 메시지 포맷

### 2.1 VamosMessage 표준 포맷

> **LOCK-BN-16 정본**: VamosMessage 구조는 02_core-node-interface/_index.md §1 (D2.0-03 K-049 — id, type, source, target, content, metadata 6개 top-level 필수) 정본을 따른다. 아래 스키마는 MODULE-ARCH 확장 초안으로 정본과 충돌 시 정본이 우선하며, auth_token/permission_level/signature 는 메시지 필드가 아닌 AuthGateway/Policy/Gate 계층 소관이다 (종합계획서 '선행 교정: 상세명세 §2 ↔ SoT 불일치 해소' 참조).

```python
class VamosMessage(BaseModel):
    """모든 CORE-NODE 간 통신의 기본 메시지 포맷 (K-049)"""

    # 헤더
    message_id: str = Field(default_factory=lambda: str(uuid4()))
    correlation_id: str             # 요청-응답 추적용
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"         # 메시지 포맷 버전

    # 라우팅
    source: str                     # 발신자 노드 ID
    destination: str                # 수신자 노드 ID
    message_type: Literal[
        "request", "response", "event", "heartbeat", "error"
    ]

    # 페이로드
    payload: dict[str, Any]         # 실제 데이터
    metadata: MessageMetadata       # 부가 정보

    # 보안
    auth_token: str                 # 인증 토큰
    permission_level: int           # 요구 권한 레벨
    signature: Optional[str]        # 메시지 무결성 서명

class MessageMetadata(BaseModel):
    priority: Literal["low", "normal", "high", "critical"] = "normal"
    ttl_seconds: int = 300          # Time-to-Live
    retry_count: int = 0
    max_retries: int = 3
    trace_id: str                   # 분산 트레이싱 ID
    span_id: str
    tags: dict[str, str] = {}
```

### 2.2 NodeRequestEnvelope

> **LOCK-BN-03/04 정본**: §2.2~§2.3 봉투 구조는 02_core-node-interface/_index.md §2~§3 정본을 따른다 (LOCK-BN-03 7필수: request_id, project_id, session_id, node_id, intent_summary, constraints, trace_id / LOCK-BN-04 7필수: trace_id, node_id, domain, inputs.summary, outputs.result, outputs.evidence_refs, status[success|fail]). 아래 스키마의 비-LOCK 필드는 MODULE-ARCH 확장 또는 constraints 내부 재분류 대상이며 정본과 충돌 시 정본이 우선한다 (종합계획서 '선행 교정: 상세명세 §2 ↔ SoT 불일치 해소' 참조).

```python
class NodeRequestEnvelope(BaseModel):
    """ORANGE CORE → Blue Node 요청 봉투"""

    # 요청 식별
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str                 # 세션 ID
    conversation_turn: int          # 대화 턴 번호

    # 작업 정의
    task_type: str                  # 작업 유형 (e.g., "web_research", "code_gen")
    task_description: str           # 사람이 읽을 수 있는 작업 설명
    task_params: dict[str, Any]     # 작업별 파라미터

    # 컨텍스트
    user_intent: str                # 사용자 의도 요약
    relevant_memory: list[MemoryRef]  # 관련 메모리 참조
    template_set_id: str            # 사용할 템플릿 셋 ID

    # 제약 조건
    deadline_ms: int = 30000        # 응답 제한 시간
    max_tokens: int = 4096          # 최대 출력 토큰
    quality_threshold: float = 0.7  # 최소 품질 기준
    permission_scope: list[str]     # 허용된 리소스 범위

    # 메시지 래핑
    message: VamosMessage           # 표준 메시지

class MemoryRef(BaseModel):
    memory_id: str
    memory_type: Literal["shared", "private", "broadcast"]
    relevance_score: float
```

### 2.3 NodeResponseEnvelope

```python
class NodeResponseEnvelope(BaseModel):
    """Blue Node → ORANGE CORE 응답 봉투"""

    # 응답 식별
    response_id: str = Field(default_factory=lambda: str(uuid4()))
    request_id: str                 # 대응하는 요청 ID

    # 결과
    status: Literal["success", "partial", "error", "timeout"]
    result: dict[str, Any]          # 작업 결과 데이터
    confidence: float               # 결과 신뢰도 (0.0~1.0)

    # 실행 정보
    execution_time_ms: int          # 실행 소요 시간
    tokens_used: int                # 사용된 토큰 수
    tools_invoked: list[str]        # 호출된 도구 목록
    memory_updates: list[MemoryUpdate]  # 메모리 업데이트 요청

    # 에러 정보 (status != "success" 시)
    error_code: Optional[str]
    error_message: Optional[str]
    fallback_suggestion: Optional[str]  # 대안 제안

    # 메시지 래핑
    message: VamosMessage

class MemoryUpdate(BaseModel):
    operation: Literal["create", "update", "delete"]
    memory_type: Literal["shared", "private"]
    key: str
    value: Any
    ttl_seconds: Optional[int]
```

### 2.4 메시지 흐름 시퀀스

```
User Request
    │
    ▼
ORANGE CORE (라우팅 결정)
    │
    ├─ NodeRequestEnvelope 생성
    │   ├─ task_type 결정
    │   ├─ template_set_id 선택
    │   ├─ relevant_memory 조회
    │   └─ permission_scope 설정
    │
    ▼
Blue Node (도메인 실행)
    │
    ├─ 권한 검증 (Permission Matrix)
    ├─ 템플릿 로드 (Template Set)
    ├─ 작업 실행
    └─ NodeResponseEnvelope 반환
    │
    ▼
ORANGE CORE (결과 통합)
    │
    ├─ confidence 검증
    ├─ memory_updates 반영
    └─ 사용자 응답 생성
```

### 2.5 의존성
- **상위**: ORANGE CORE 라우터 (I-18 ClarityEngine)
- **하위**: 모든 Blue Node의 요청/응답 처리
- **연관**: K-041 Permission Matrix, K-029 Memory Sharing

---

## 3. Template Set Injection (SS4.2): 템플릿 셋 주입

### SOT 근거
- D2.0-03 SS4.2: 템플릿 셋 정의 및 주입 메커니즘
- D2.0-01 S4: 프롬프트 엔지니어링 전략

### 3.1 3대 템플릿 셋 정의

| Template Set ID | 이름 | 대상 노드 | 설명 |
|-----------------|------|-----------|------|
| `TS_CORE` | 코어 템플릿 | 모든 Blue Node | 기본 시스템 프롬프트, 안전 가드레일, 출력 포맷 |
| `TS_WEB_RESEARCH` | 웹 리서치 템플릿 | BN-WebResearch | 검색 쿼리 생성, 소스 평가, 요약 전략 |
| `TS_CODE` | 코드 템플릿 | BN-CodeEngine | 코드 생성 규칙, 리뷰 체크리스트, 테스트 전략 |

### 3.2 템플릿 셋 구조

```python
class TemplateSet(BaseModel):
    """템플릿 셋 정의"""
    set_id: str                     # e.g., "TS_CORE"
    version: str                    # SemVer (e.g., "1.2.0")
    name: str
    description: str

    # 템플릿 구성
    system_prompt: str              # 시스템 프롬프트 기본 텍스트
    role_instruction: str           # 역할 지시문
    output_format: OutputFormat     # 출력 포맷 규칙
    guardrails: list[Guardrail]     # 안전 가드레일
    examples: list[FewShotExample]  # Few-shot 예시

    # 도메인 특화
    domain_rules: list[str]         # 도메인별 규칙
    tool_usage_hints: dict[str, str]  # 도구 사용 힌트
    quality_criteria: dict[str, float]  # 품질 기준

    # 메타
    parent_set_id: Optional[str]    # 상속 원본 (None = 루트)
    created_at: datetime
    deprecated: bool = False

class OutputFormat(BaseModel):
    format_type: Literal["json", "markdown", "plain", "structured"]
    schema: Optional[dict]          # JSON 스키마 (format_type=json 시)
    max_length: Optional[int]
    required_sections: list[str]    # 필수 포함 섹션

class Guardrail(BaseModel):
    rule_id: str
    description: str
    check_type: Literal["regex", "llm_judge", "rule_based"]
    check_config: dict[str, Any]
    action_on_violation: Literal["block", "warn", "rewrite"]
```

### 3.3 주입 메커니즘

```python
class TemplateInjector:
    """Blue Node 실행 시 템플릿 셋 주입"""

    def __init__(self, registry: TemplateRegistry):
        self.registry = registry

    async def inject(
        self,
        node_id: str,
        request: NodeRequestEnvelope
    ) -> InjectedContext:
        # 1. 기본 TS_CORE 로드
        core = await self.registry.get("TS_CORE", latest=True)

        # 2. 도메인 템플릿 로드
        domain_ts = await self.registry.get(request.template_set_id)

        # 3. 병합 (도메인이 코어를 오버라이드, guardrails는 합집합)
        merged = self._merge(core, domain_ts)

        # 4. 변수 바인딩
        bound = self._bind_variables(merged, {
            "user_intent": request.user_intent,
            "task_type": request.task_type,
            "session_context": request.relevant_memory,
        })

        # 5. 가드레일 적용
        validated = await self._validate_guardrails(bound)

        return InjectedContext(
            system_prompt=validated.system_prompt,
            role_instruction=validated.role_instruction,
            output_format=validated.output_format,
            active_guardrails=validated.guardrails,
        )

    def _merge(self, base: TemplateSet, override: TemplateSet) -> TemplateSet:
        """병합 규칙: override가 base를 덮되, guardrails는 합집합"""
        merged = base.model_copy()
        merged.system_prompt = override.system_prompt or base.system_prompt
        merged.role_instruction = override.role_instruction
        merged.output_format = override.output_format or base.output_format
        merged.guardrails = list(set(base.guardrails + override.guardrails))
        merged.domain_rules = override.domain_rules
        merged.tool_usage_hints = {**base.tool_usage_hints, **override.tool_usage_hints}
        return merged
```

### 3.4 버전 확장 전략

> ⚠️ 아래는 구현 범위(scope) 정의만 기술. Phase 일정은 Part2 정본 참조 (R6 준수).

| 단계 | 범위 | 추가 템플릿 셋 | 설명 |
|------|------|----------------|------|
| V1 | MVP | TS_CORE, TS_WEB_RESEARCH, TS_CODE | 3대 핵심 셋 |
| V2 | P1 확장 | TS_PKM, TS_EDUCATION, TS_HEALTH, TS_MEDIA, TS_FINANCE, TS_INTEGRATION | 도메인 확장 |
| V3 | P2 확장 | TS_CUSTOM (사용자 정의) | 사용자가 직접 생성 |

### 3.5 의존성
- **상위**: K-049 VamosMessage (template_set_id 전달)
- **하위**: Blue Node 실행 컨텍스트 구성
- **연관**: SS4.1 정책 오버라이드 (guardrails 상속)

---

## 4. Node Lifecycle State Machine (SS3.2): 노드 라이프사이클 상태 머신

### SOT 근거
- D2.0-03 SS3.2: Blue Node 생명주기 관리
- D2.0-01 S4.3: 노드 활성화/비활성화 전략

### 4.1 상태 정의

| 상태 | 코드 | 설명 |
|------|------|------|
| **Candidate** | `CANDIDATE` | candidate_node_cap에 의해 후보로 등록됨 |
| **Lazy** | `LAZY` | 코드 로드 완료, 리소스 미할당 (lazy generation) |
| **Activating** | `ACTIVATING` | 리소스 할당 중 (MCP 연결, 메모리 초기화) |
| **Active** | `ACTIVE` | 정상 운영 중, 작업 수신 가능 |
| **Busy** | `BUSY` | 작업 실행 중 (새 작업 큐잉) |
| **Draining** | `DRAINING` | 종료 준비 중 (진행 작업 완료 대기) |
| **Suspended** | `SUSPENDED` | 일시 중지 (리소스 유지, 작업 불가) |
| **Terminated** | `TERMINATED` | 종료됨 (리소스 해제 완료) |

### 4.2 상태 전이 다이어그램

```
                    ┌──────────────┐
                    │  CANDIDATE   │
                    └──────┬───────┘
                           │ activation_trigger
                           ▼
                    ┌──────────────┐
                    │    LAZY      │◄─────────────────────┐
                    └──────┬───────┘                      │
                           │ first_request / preload      │ cooldown_expired
                           ▼                              │
                    ┌──────────────┐                      │
                    │  ACTIVATING  │                      │
                    └──────┬───────┘                      │
                           │ resources_ready              │
                           ▼                              │
              ┌───►┌──────────────┐                      │
              │    │   ACTIVE     │──── suspend ────►┌────┴─────┐
              │    └──────┬───────┘                  │SUSPENDED │
              │           │ task_received            └────┬─────┘
              │           ▼                               │ resume
              │    ┌──────────────┐                      │
              │    │    BUSY      │──────────────────────┘
              │    └──────┬───────┘
              │           │ task_complete
              └───────────┘
                           │ terminate_signal / idle_timeout
                           ▼
                    ┌──────────────┐
                    │  DRAINING    │
                    └──────┬───────┘
                           │ all_tasks_complete
                           ▼
                    ┌──────────────┐
                    │ TERMINATED   │
                    └──────────────┘
```

### 4.3 candidate_node_cap 메커니즘

```python
class CandidateNodeCap(BaseModel):
    """Blue Node 후보 등록 제한"""
    max_candidates: int = 5          # 최대 후보 수 (LOCK-BN-13 V1=5; V2=20, V3=100)
    max_active: int = 3              # 동시 활성 노드 수 (LOCK-BN-12 V1=3; V2=10, V3=50)
    max_per_domain: int = 2          # 도메인별 최대 활성 노드

class NodeCapManager:
    async def register_candidate(self, node_spec: NodeSpec) -> bool:
        """후보 등록 (cap 초과 시 거부)"""
        current = await self.count_candidates()
        if current >= self.cap.max_candidates:
            await self.evict_least_used()
        return await self.store.register(node_spec)

    async def can_activate(self, node_id: str) -> bool:
        """활성화 가능 여부 확인"""
        active_count = await self.count_active()
        domain = await self.get_domain(node_id)
        domain_count = await self.count_active_in_domain(domain)
        return (
            active_count < self.cap.max_active
            and domain_count < self.cap.max_per_domain
        )
```

### 4.4 Lazy Generation 전략

```python
class LazyNodeGenerator:
    """최초 요청 시점에 노드 리소스 할당 (lazy generation)"""

    async def ensure_ready(self, node_id: str) -> NodeHandle:
        state = await self.get_state(node_id)

        if state == NodeState.LAZY:
            # 1. MCP 서버 연결
            mcp_handle = await self.connect_mcp(node_id)
            # 2. 메모리 공간 할당
            memory = await self.allocate_memory(node_id)
            # 3. 템플릿 셋 프리로드
            templates = await self.preload_templates(node_id)
            # 4. 상태 전이
            await self.transition(node_id, NodeState.ACTIVATING)
            await self.transition(node_id, NodeState.ACTIVE)

        return await self.get_handle(node_id)
```

### 4.5 활성화 트리거

| 트리거 | 조건 | 동작 |
|--------|------|------|
| `first_request` | 해당 도메인 첫 요청 수신 | LAZY → ACTIVATING → ACTIVE |
| `preload` | 시스템 시작 시 자주 사용 노드 | LAZY → ACTIVATING → ACTIVE |
| `scheduled` | 스케줄 기반 활성화 | LAZY → ACTIVATING → ACTIVE |
| `dependency` | 의존 노드 활성화 시 함께 활성화 | LAZY → ACTIVATING → ACTIVE |

### 4.6 종료 조건

| 조건 | 타임아웃 | 동작 |
|------|----------|------|
| `idle_timeout` | 5분 무요청 | ACTIVE → DRAINING → TERMINATED |
| `error_threshold` | 에러율 > 30% | ACTIVE → SUSPENDED |
| `manual_stop` | 관리자 명령 | Any → DRAINING → TERMINATED |
| `resource_pressure` | 시스템 리소스 부족 | LRU 노드 → DRAINING → TERMINATED |
| `cap_exceeded` | max_active 초과 | LRU 노드 → DRAINING → TERMINATED |

### 4.7 의존성
- **상위**: ORANGE CORE 스케줄러
- **하위**: 모든 Blue Node 인스턴스
- **연관**: K-041 Permission Matrix (활성화 시 권한 로드), K-010 MCP Bridge (MCP 연결)

---

## 5. Memory Sharing Protocol (K-029): 메모리 공유 프로토콜

### SOT 근거
- STEP7 K-029: 노드 간 메모리 공유 프로토콜
- D2.0-03 SS5.3: 메모리 계층 및 접근 제어

### 5.1 메모리 유형

| 유형 | 코드 | 범위 | 수명 | 접근 제어 |
|------|------|------|------|-----------|
| **Shared** | `SHARED` | 모든 Blue Node 접근 가능 | 세션 수명 | Permission Level 2+ |
| **Private** | `PRIVATE` | 해당 Blue Node 전용 | 노드 수명 | 소유 노드만 |
| **Broadcast** | `BROADCAST` | 전체 노드에 읽기 전파 | TTL 기반 | 모든 노드 읽기, 발행자만 쓰기 |

### 5.2 입출력 스키마

```python
class MemorySlot(BaseModel):
    slot_id: str = Field(default_factory=lambda: str(uuid4()))
    memory_type: Literal["shared", "private", "broadcast"]
    owner_node_id: str              # 소유 노드
    key: str                        # 메모리 키
    value: Any                      # 저장 데이터
    value_type: str                 # 데이터 타입 힌트
    version: int = 1                # 낙관적 동시성 제어용
    created_at: datetime
    updated_at: datetime
    ttl_seconds: Optional[int]      # None = 영구
    access_log: list[AccessRecord]  # 접근 이력

class MemoryReadRequest(BaseModel):
    requester_node_id: str
    key: str
    memory_type: Literal["shared", "private", "broadcast"]
    required_version: Optional[int]  # 특정 버전 요구 시

class MemoryWriteRequest(BaseModel):
    requester_node_id: str
    key: str
    memory_type: Literal["shared", "private", "broadcast"]
    value: Any
    expected_version: Optional[int]  # 낙관적 잠금 (CAS)
    ttl_seconds: Optional[int]

class MemoryReadResult(BaseModel):
    found: bool
    slot: Optional[MemorySlot]
    access_denied: bool = False
    denial_reason: Optional[str]

class MemoryWriteResult(BaseModel):
    success: bool
    new_version: int
    conflict: bool = False          # CAS 충돌 시 True
    broadcast_count: int = 0        # broadcast 전파된 노드 수
```

### 5.3 접근 제어 규칙

```python
class MemoryAccessControl:
    """메모리 접근 제어 (Permission Matrix 연동)"""

    async def check_read(self, request: MemoryReadRequest) -> bool:
        perm = await self.permission_matrix.check(
            requester=request.requester_node_id,
            resource=f"memory:{request.memory_type}:{request.key}",
            action="read"
        )

        if request.memory_type == "private":
            # private: 소유 노드만 읽기 가능
            slot = await self.store.get(request.key)
            return slot.owner_node_id == request.requester_node_id

        if request.memory_type == "broadcast":
            # broadcast: 모든 노드 읽기 가능
            return True

        # shared: Permission Level 2+ 필요
        return perm.effective_level >= 2

    async def check_write(self, request: MemoryWriteRequest) -> bool:
        if request.memory_type == "private":
            slot = await self.store.get(request.key)
            return slot is None or slot.owner_node_id == request.requester_node_id

        if request.memory_type == "broadcast":
            # broadcast: 발행자만 쓰기 가능
            slot = await self.store.get(request.key)
            return slot is None or slot.owner_node_id == request.requester_node_id

        # shared: Permission Level 3+ 필요
        perm = await self.permission_matrix.check(
            requester=request.requester_node_id,
            resource=f"memory:shared:{request.key}",
            action="write"
        )
        return perm.effective_level >= 3
```

### 5.4 동기화 메커니즘

```python
class MemorySynchronizer:
    """노드 간 메모리 동기화"""

    async def sync_shared(self, key: str, write_result: MemoryWriteResult):
        """shared 메모리 변경 시 관련 노드에 invalidation 전파"""
        subscribers = await self.get_subscribers(key)
        for node_id in subscribers:
            await self.send_invalidation(node_id, key, write_result.new_version)

    async def broadcast(self, key: str, value: Any, sender_id: str):
        """broadcast 메모리: 모든 활성 노드에 전파"""
        active_nodes = await self.node_registry.get_active_nodes()
        results = await asyncio.gather(*[
            self.send_broadcast(node_id, key, value, sender_id)
            for node_id in active_nodes
            if node_id != sender_id
        ])
        return sum(1 for r in results if r.success)

    async def resolve_conflict(self, key: str, versions: list[MemorySlot]) -> MemorySlot:
        """CAS 충돌 해결: Last-Writer-Wins + 사용자 확인"""
        if len(set(v.value for v in versions)) == 1:
            return versions[0]  # 동일 값이면 아무거나

        # 타임스탬프 기반 LWW
        latest = max(versions, key=lambda v: v.updated_at)

        # 중요 데이터는 사용자 확인 요청
        if await self.is_critical(key):
            return await self.request_user_resolution(key, versions)

        return latest
```

### 5.5 의존성
- **상위**: K-041 Permission Matrix (접근 권한 확인)
- **하위**: 모든 Blue Node의 메모리 읽기/쓰기
- **연관**: NodeResponseEnvelope.memory_updates, Node Lifecycle (메모리 할당/해제)

---

## 6. Domain-specific Policy Overrides (SS4.1): 도메인별 정책 오버라이드

### SOT 근거
- D2.0-03 SS4.1: 정책 상속 및 오버라이드 규칙
- D2.0-01 S4.1: "only stricter direction" 원칙

### 6.1 "Only Stricter Direction" 원칙

> 하위 노드는 상위 정책을 **더 엄격한 방향으로만** 오버라이드할 수 있다.
> 느슨한 방향의 오버라이드는 무시되며 감사 로그에 기록된다.

### 6.2 정책 구조

```python
class Policy(BaseModel):
    policy_id: str
    scope: Literal["global", "domain", "node"]  # 적용 범위
    source: str                     # 정책 출처 (ORANGE CORE / Blue Node ID)
    rules: list[PolicyRule]
    priority: int                   # 높을수록 우선 (동일 scope 내)

class PolicyRule(BaseModel):
    rule_id: str
    category: Literal[
        "safety", "quality", "performance",
        "resource", "privacy", "content"
    ]
    parameter: str                  # 규칙 대상 파라미터
    operator: Literal["max", "min", "exact", "range", "enum"]
    value: Any                      # 제한 값
    direction: Literal["stricter", "looser"]  # 엄격/느슨 방향

    def is_stricter_than(self, other: "PolicyRule") -> bool:
        """현재 규칙이 other보다 엄격한지 판단"""
        if self.operator == "max":
            return self.value <= other.value  # max는 낮을수록 엄격
        if self.operator == "min":
            return self.value >= other.value  # min은 높을수록 엄격
        if self.operator == "enum":
            return set(self.value).issubset(set(other.value))  # 허용 범위 축소
        return False
```

### 6.3 정책 상속/오버라이드 알고리즘

```python
class PolicyResolver:
    """정책 상속 체인 해석"""

    async def resolve(self, node_id: str) -> ResolvedPolicy:
        # 1. 전역 정책 로드 (ORANGE CORE)
        global_policies = await self.load_policies(scope="global")

        # 2. 도메인 정책 로드
        domain = await self.get_domain(node_id)
        domain_policies = await self.load_policies(scope="domain", domain=domain)

        # 3. 노드 정책 로드
        node_policies = await self.load_policies(scope="node", node_id=node_id)

        # 4. 병합 (only stricter direction)
        resolved = {}
        for rule in global_policies.rules:
            resolved[rule.parameter] = rule

        for rule in domain_policies.rules + node_policies.rules:
            existing = resolved.get(rule.parameter)
            if existing is None:
                resolved[rule.parameter] = rule
            elif rule.is_stricter_than(existing):
                resolved[rule.parameter] = rule
                await self.audit_log("override_accepted", rule, existing)
            else:
                # 느슨한 방향 → 무시
                await self.audit_log("override_rejected", rule, existing)

        return ResolvedPolicy(rules=list(resolved.values()))
```

### 6.4 정책 카테고리별 기본값

| 카테고리 | 파라미터 | 전역 기본값 | 방향 | 설명 |
|----------|----------|-------------|------|------|
| safety | `max_risk_score` | 0.7 | max (↓=엄격) | 최대 허용 위험 점수 |
| safety | `content_filter_level` | 2 | min (↑=엄격) | 컨텐츠 필터 레벨 (1~5) |
| quality | `min_confidence` | 0.6 | min (↑=엄격) | 최소 신뢰도 |
| quality | `max_hallucination_rate` | 0.1 | max (↓=엄격) | 최대 환각률 |
| performance | `max_response_time_ms` | 30000 | max (↓=엄격) | 최대 응답 시간 |
| resource | `max_tokens_per_request` | 4096 | max (↓=엄격) | 요청당 최대 토큰 |
| privacy | `data_retention_days` | 90 | max (↓=엄격) | 데이터 보관 기간 |
| content | `allowed_languages` | ["ko","en"] | enum (⊂=엄격) | 허용 언어 |

### 6.5 도메인별 오버라이드 예시

```yaml
# BN-Health 도메인 정책 (전역보다 엄격)
domain: health
overrides:
  - parameter: max_risk_score
    value: 0.3              # 전역 0.7 → 0.3 (의료 정보는 더 엄격)
  - parameter: min_confidence
    value: 0.8              # 전역 0.6 → 0.8 (높은 신뢰도 요구)
  - parameter: content_filter_level
    value: 4                # 전역 2 → 4 (의료 컨텐츠 필터 강화)

# BN-CodeEngine 도메인 정책
domain: code
overrides:
  - parameter: max_tokens_per_request
    value: 8192             # 전역 4096 → 8192 → 거부됨 (느슨한 방향)
  - parameter: min_confidence
    value: 0.7              # 전역 0.6 → 0.7 (수용됨, 엄격한 방향)
```

### 6.6 의존성
- **상위**: ORANGE CORE 정책 엔진
- **하위**: 모든 Blue Node 실행 시 정책 적용
- **연관**: K-041 Permission Matrix (권한 정책), Template Set (guardrails 정책)

---

## 7. MCP-Blue Node Bridge (K-010): MCP 서버로 Blue Node 노출

### SOT 근거
- STEP7 K-010: MCP(Model Context Protocol) 통합
- D2.0-03 §6.4~§6.7: MCP 표준 채택/서버 카탈로그/Claude Tool Use/SDK 통합 (⚠️ 기존 "SS6.2" 참조는 §6.2 Failure/Fallback Registry와 불일치 — 실제 MCP 관련 근거는 §6.4~§6.7)

### 7.1 아키텍처 개요

```
┌─────────────────────────────────────────────┐
│              External MCP Client            │
│  (Claude Desktop, Cursor, 3rd-party apps)   │
└──────────────────┬──────────────────────────┘
                   │ MCP Protocol (JSON-RPC 2.0)
                   ▼
┌─────────────────────────────────────────────┐
│           MCP-Blue Node Bridge              │
│  ┌─────────────┐  ┌──────────────────────┐  │
│  │ Auth Gateway │  │ Tool Registry        │  │
│  │ (K-041 연동) │  │ (자동 등록/발견)      │  │
│  └─────────────┘  └──────────────────────┘  │
│  ┌─────────────┐  ┌──────────────────────┐  │
│  │ Rate Limiter│  │ Request Translator   │  │
│  │             │  │ (MCP↔VamosMessage)   │  │
│  └─────────────┘  └──────────────────────┘  │
└──────────────────┬──────────────────────────┘
                   │ VamosMessage (K-049)
                   ▼
┌─────────────────────────────────────────────┐
│              Blue Node Pool                 │
│  BN-WebResearch │ BN-Code │ BN-PKM │ ...   │
└─────────────────────────────────────────────┘
```

### 7.2 Blue Node를 MCP 서버로 노출

```python
class MCPBlueNodeServer:
    """Blue Node를 MCP 서버로 노출하는 브리지"""

    def __init__(self, node_id: str, node_handle: NodeHandle):
        self.node_id = node_id
        self.node_handle = node_handle
        self.mcp_server = MCPServer(name=f"vamos-{node_id}")

    async def start(self):
        # 1. 노드의 capabilities를 MCP tools로 등록
        capabilities = await self.node_handle.get_capabilities()
        for cap in capabilities:
            tool = self._capability_to_mcp_tool(cap)
            self.mcp_server.register_tool(tool)

        # 2. 노드의 메모리를 MCP resources로 등록
        memory_keys = await self.node_handle.list_shared_memory_keys()
        for key in memory_keys:
            resource = self._memory_to_mcp_resource(key)
            self.mcp_server.register_resource(resource)

        # 3. MCP 서버 시작
        await self.mcp_server.start()

    def _capability_to_mcp_tool(self, cap: NodeCapability) -> MCPTool:
        return MCPTool(
            name=f"{self.node_id}.{cap.name}",
            description=cap.description,
            input_schema=cap.input_schema,
            handler=self._create_handler(cap),
        )

    def _create_handler(self, cap: NodeCapability):
        async def handler(params: dict) -> dict:
            # MCP 요청 → VamosMessage 변환
            request = NodeRequestEnvelope(
                task_type=cap.name,
                task_params=params,
                template_set_id=cap.default_template_set,
                session_id=str(uuid4()),
                conversation_turn=0,
                user_intent=f"MCP external call: {cap.name}",
                relevant_memory=[],
                message=VamosMessage(
                    source="mcp-bridge",
                    destination=self.node_id,
                    message_type="request",
                    payload=params,
                    metadata=MessageMetadata(
                        priority="normal",
                        trace_id=str(uuid4()),
                        span_id=str(uuid4()),
                    ),
                    auth_token="",  # Auth Gateway에서 주입
                    permission_level=2,
                ),
            )

            # Blue Node 실행
            response = await self.node_handle.execute(request)

            # VamosMessage → MCP 응답 변환
            return response.result

        return handler
```

### 7.3 도구 자동 등록/발견 (Tool Registry)

```python
class MCPToolRegistry:
    """Blue Node capabilities를 MCP tools로 자동 등록/발견"""

    def __init__(self):
        self.tools: dict[str, MCPTool] = {}
        self.node_tool_map: dict[str, list[str]] = {}  # node_id → tool names

    async def on_node_activated(self, node_id: str, handle: NodeHandle):
        """노드 활성화 시 자동으로 MCP tools 등록"""
        capabilities = await handle.get_capabilities()
        for cap in capabilities:
            tool_name = f"{node_id}.{cap.name}"
            self.tools[tool_name] = MCPTool(
                name=tool_name,
                description=cap.description,
                input_schema=cap.input_schema,
            )
            self.node_tool_map.setdefault(node_id, []).append(tool_name)

        await self.notify_clients_tools_changed()

    async def on_node_terminated(self, node_id: str):
        """노드 종료 시 MCP tools 자동 해제"""
        tool_names = self.node_tool_map.pop(node_id, [])
        for name in tool_names:
            del self.tools[name]
        await self.notify_clients_tools_changed()

    async def discover(self, query: str) -> list[MCPTool]:
        """도구 검색 (이름, 설명 기반 퍼지 매칭)"""
        results = []
        for tool in self.tools.values():
            score = self._fuzzy_match(query, tool.name, tool.description)
            if score > 0.5:
                results.append((score, tool))
        return [t for _, t in sorted(results, reverse=True)]
```

### 7.4 인증 게이트웨이

```python
class MCPAuthGateway:
    """MCP 클라이언트 인증 및 권한 매핑"""

    async def authenticate(self, request: MCPRequest) -> AuthResult:
        # 1. API 키 검증
        api_key = request.headers.get("x-api-key")
        if not api_key:
            return AuthResult(authenticated=False, reason="Missing API key")

        client = await self.client_store.get_by_api_key(api_key)
        if not client:
            return AuthResult(authenticated=False, reason="Invalid API key")

        # 2. 클라이언트 → Permission Level 매핑
        permission_level = self._map_client_to_permission(client)

        # 3. Rate Limit 확인
        if await self.rate_limiter.is_exceeded(client.client_id):
            return AuthResult(
                authenticated=True,
                authorized=False,
                reason="Rate limit exceeded"
            )

        # 4. 도구별 접근 권한 확인
        tool_name = request.method_params.get("name", "")
        if not await self.check_tool_access(client, tool_name):
            return AuthResult(
                authenticated=True,
                authorized=False,
                reason=f"No access to tool: {tool_name}"
            )

        return AuthResult(
            authenticated=True,
            authorized=True,
            permission_level=permission_level,
            client_id=client.client_id,
        )

    def _map_client_to_permission(self, client: MCPClient) -> int:
        """클라이언트 tier → VAMOS permission level 매핑"""
        tier_map = {
            "free": 1,       # READ_ONLY
            "basic": 2,      # EXECUTE
            "premium": 3,    # WRITE
            "enterprise": 4, # CROSS_DOMAIN
        }
        return tier_map.get(client.tier, 1)
```

### 7.5 지원 MCP 프로토콜 기능

| MCP 기능 | 지원 | 매핑 대상 |
|----------|------|-----------|
| `tools/list` | O | Blue Node capabilities |
| `tools/call` | O | NodeRequestEnvelope → 실행 → NodeResponseEnvelope |
| `resources/list` | O | Shared Memory 키 목록 |
| `resources/read` | O | MemoryReadRequest |
| `prompts/list` | O | Template Set 목록 |
| `prompts/get` | O | Template Set 내용 (가드레일 적용) |
| `sampling` | X | 보안상 비활성 (내부 전용) |

### 7.6 의존성
- **상위**: K-041 Permission Matrix (인증/권한), K-049 VamosMessage (프로토콜 변환)
- **하위**: 외부 MCP 클라이언트 (Claude Desktop, Cursor 등)
- **연관**: Node Lifecycle (노드 활성화/종료 시 도구 등록/해제), Template Set (prompts 노출)

---

## 교차 참조 요약

| 항목 | 관련 키워드 | SOT 참조 | 의존 관계 |
|------|-------------|----------|-----------|
| Permission Matrix | K-041 | D2.0-03 §1 (P0/P1/P2 제약) + §6.1 (Event Registry) | → Memory, Lifecycle, MCP Bridge |
| Interface Contract | K-049 | D2.0-03 §5.2 | → Template, Permission |
| Template Set | — | D2.0-03 §4.2 | → Interface Contract, Policy |
| Lifecycle State Machine | — | D2.0-03 §3.2, §3.3 | → Permission, MCP Bridge |
| Memory Sharing | K-029 | D2.0-03 §5.3 | → Permission Matrix |
| Policy Overrides | — | D2.0-03 §4.1 | → Template Set, Permission |
| MCP Bridge | K-010 | D2.0-03 §6.4~§6.7 | → Permission, Lifecycle, Interface Contract |

---

## 구현 우선순위

| 순서 | 항목 | 이유 |
|------|------|------|
| 1 | Permission Matrix (K-041) | 모든 다른 항목의 보안 기반 |
| 2 | Interface Contract (K-049) | 통신 표준이 없으면 나머지 구현 불가 |
| 3 | Node Lifecycle (SS3.2) | 노드 관리의 기본 골격 |
| 4 | Memory Sharing (K-029) | 노드 간 데이터 공유 필수 |
| 5 | Template Set (SS4.2) | 도메인 실행 품질 향상 |
| 6 | Policy Overrides (SS4.1) | 안전성 강화 |
| 7 | MCP Bridge (K-010) | 외부 연동 (MVP 이후 가능) |
