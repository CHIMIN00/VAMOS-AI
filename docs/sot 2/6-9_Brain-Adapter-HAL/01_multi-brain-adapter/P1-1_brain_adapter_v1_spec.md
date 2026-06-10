# P1-1 — Brain Adapter V1 구현 사양서 (Ollama + OpenAI + Anthropic)

> **도메인**: 6-9_Brain-Adapter-HAL
> **서브폴더**: 01_multi-brain-adapter
> **세션**: P1-1
> **작성일**: 2026-04-14
> **상태**: Phase 1 L2 (설계 완료, Phase 2 통합 테스트 힌트 포함)

---

## 0. Purpose & Scope

본 문서는 6-9 Brain Adapter 계층의 V1 구현 사양을 정의한다. 구현 대상은 Ollama(로컬), OpenAI, Anthropic 3개 프로바이더이다. 각 어댑터는 공통 `BaseBrainAdapter` ABC 를 상속하고 `ConnectorResponse`(LOCK-69-1) 을 반환한다. LangChain 직접 import 금지(LOCK-69-9), ToolRegistry 경유(LOCK-69-3), CORE 실행 금지(LOCK-69-5), 설정 우선순위(LOCK-69-6), 비용 상한 차단(LOCK-69-7), JSON 구조화 로깅(LOCK-69-10) 을 실구현에 반영한다.

**Phase 2 제외 항목**: Google/Groq/vLLM 어댑터(DeepSeek 는 V1 포함 대상 아님 — P1-4 폴백 체인에서만 호출 대상), HAL 환경 분기(P1-2), 동적 라우팅(P1-3), 폴백 체인(P1-4), MLOps 드리프트 연동(Phase 3).

## 1. 교차 참조 블록

| 참조 대상 | 섹션 | 용도 |
|-----------|------|------|
| `01_multi-brain-adapter/_index.md` | §2, §3 (ConnectorResponse), §4.1 (BaseBrainAdapter ABC), §4.2 (프로바이더별) | 정본 스키마/ABC |
| `AUTHORITY_CHAIN.md` | LOCK-69-1/3/5/6/7/9/10 | 규칙 근거 |
| `D:\VAMOS\docs\sot\D2.0-04_04. VAMOS_DESIGN_2.0_INFRA_CORE.md` | §2 (Brain Engine Modularization), §3 (Brain Adapter Layer), §4.0 (설정), §7.2 (ToolRegistry), §8.3 (로깅) | L1 정본 |
| `D:\VAMOS\docs\sot\D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md` | §1.2-A Runnable 프로토콜 | L2 정본 (run/invoke 위임) |
| `BRAIN_ADAPTER_HAL_구조화_종합계획서.md` | §7 P1-1, §6 P4 이슈 | 작업 절차/이슈 |
| `02_hal-interface/_index.md` | §3 HAL 인터페이스 | P1-2 와의 경계 (P1-1 어댑터는 HAL 하위 호출자) |
| `04_fallback-chain/_index.md` | §4 V-Phase 분기 | P1-4 와의 경계 (폴백 트리거 규칙) |

## 2. BrainRequest / BrainAdapter 공통 자료 구조 선정의

> 기존 `_index.md` §2/§3 는 `ConnectorResponse` 와 ABC 시그니처만 정의한다. 본 섹션은 P1-1 공통 자료구조 (BrainRequest, AdapterMetadata, HealthStatus) 를 정의하여 P1-2/P1-3/P1-4 가 동일 구조를 참조한다.

### 2.1 BrainRequest (Pydantic)

```python
from typing import Optional, List, Literal, Dict, Any
from pydantic import BaseModel, Field

class ToolCallRequest(BaseModel):
    tool_id: str                                   # LOCK-69-3: ToolRegistry 등록 ID 필수
    arguments: Dict[str, Any] = Field(default_factory=dict)
    class Config: extra = "forbid"

class BrainRequest(BaseModel):
    task_type: Literal["reasoning", "main_llm", "tool_call", "classification", "extraction"]
    prompt: str                                    # 사용자/엔진 입력 텍스트
    system_prompt: Optional[str] = None
    tier: Optional[Literal["main", "draft", "verify"]] = None   # 6-11 2-tier 라우팅 힌트
    max_tokens: int = Field(2048, ge=1, le=32768)
    temperature: float = Field(0.2, ge=0.0, le=2.0)
    cost_cap: float = Field(1.0, ge=0.0)           # LOCK-69-7: 비용 상한 (상대 단위), 기본값 = §5 global.cost_cap_default
    timeout_ms: int = Field(30000, ge=500, le=120000)  # LOCK-69-8 기본 30s
    tools: List[ToolCallRequest] = Field(default_factory=list)  # LOCK-69-3 경유
    metadata: Dict[str, Any] = Field(default_factory=dict)      # trace/caller 정보
    trace_id: str                                  # 상위 호출자가 전파한 추적 ID
    class Config: extra = "forbid"
```

### 2.2 AdapterMetadata / HealthStatus

```python
class AdapterMetadata(BaseModel):
    adapter_id: str            # ex: "llm_ollama_text"
    provider: Literal["ollama", "openai", "anthropic", "deepseek", "google", "groq", "vllm"]
    version: str               # semver (v1.0.0)
    capabilities: List[str]    # ex: ["text_gen", "tool_call", "streaming"]
    cost_unit_per_1k_tokens: float   # 정규화된 상대 비용 (LOCK-69-7 비교용)
    class Config: extra = "forbid"

class HealthStatus(BaseModel):
    healthy: bool
    latency_ms: Optional[int] = None
    last_check_ts: str          # ISO8601
    details: Optional[str] = None
    class Config: extra = "forbid"
```

### 2.3 ABC 시그니처 정본 (h)

`_index.md` §4.1 의 `BaseBrainAdapter` 를 그대로 따른다 — 임의 변경 금지.

```python
class BaseBrainAdapter(ABC):
    @abstractmethod
    async def invoke(self, request: BrainRequest) -> ConnectorResponse: ...
    @abstractmethod
    async def health_check(self) -> HealthStatus: ...
    @abstractmethod
    def get_metadata(self) -> AdapterMetadata: ...
```

Runnable 프로토콜 호환을 위해 `run(input) -> output` 은 `invoke` 에 위임하는 래퍼를 `BaseBrainAdapter` 에 기본 구현으로 제공한다 (`_index.md` §3.4 교차 확인 기준).

## 3. 프로바이더별 어댑터 설계

### 3.1 OllamaAdapter

| 항목 | 값 |
|------|-----|
| adapter_id | `llm_ollama_text` |
| SDK | `ollama` (공식 Python 클라이언트) — LangChain 우회 (LOCK-69-9) |
| 엔드포인트 | `OLLAMA_HOST` ENV > `config.yaml:ollama.host` > `http://localhost:11434` (LOCK-69-6) |
| 비용 산정 | 로컬 → `cost_unit_per_1k_tokens = 0.0`, `cost_used_estimate = 0.0` |
| 도구 호출 | Ollama tool-calling → `ToolRegistry.get(tool_id).invoke(args)` 로 변환 (LOCK-69-3) |
| 타임아웃 | `request.timeout_ms` (기본 30000) |

### 3.2 OpenAIAdapter

| 항목 | 값 |
|------|-----|
| adapter_id | `llm_openai_text` |
| SDK | `openai` (공식) — LangChain 금지 (LOCK-69-9) |
| 엔드포인트 | `OPENAI_API_BASE` ENV > `config.yaml:openai.base_url` > `https://api.openai.com/v1` (LOCK-69-6) |
| API 키 | `OPENAI_API_KEY` ENV only (코드/config 내 하드코딩 금지) |
| 기본 모델 | `config.yaml:openai.default_model` > `gpt-4o-mini` |
| 비용 산정 | `cost_used_estimate = (prompt_tokens + completion_tokens) / 1000 * cost_unit_per_1k_tokens` |
| 도구 호출 | `tools` 필드 → OpenAI function-calling 스키마 변환, 실행은 ToolRegistry |

### 3.3 AnthropicAdapter

| 항목 | 값 |
|------|-----|
| adapter_id | `llm_anthropic_text` |
| SDK | `anthropic` (공식) — LangChain 금지 (LOCK-69-9) |
| 엔드포인트 | `ANTHROPIC_API_BASE` ENV > `config.yaml:anthropic.base_url` > `https://api.anthropic.com` |
| API 키 | `ANTHROPIC_API_KEY` ENV only |
| 기본 모델 | `config.yaml:anthropic.default_model` > `claude-3-5-sonnet-20241022` |
| 비용 산정 | input/output 토큰별 단가 합산 |
| 도구 호출 | `tools` → Anthropic tool_use 블록 변환, 실행은 ToolRegistry |

## 4. invoke() 의사코드 (공통)

```python
async def invoke(self, request: BrainRequest) -> ConnectorResponse:
    # Step 1. 비용 사전 차단 (LOCK-69-7)
    estimated = self._estimate_cost(request)
    if estimated > request.cost_cap:
        self._log_blocked(request, estimated)
        raise CostCapExceededError(trace_id=request.trace_id, estimated=estimated, cap=request.cost_cap)

    # Step 2. 도구 요청 ToolRegistry 경유 변환 (LOCK-69-3)
    tool_schemas = [ToolRegistry.get_schema(t.tool_id) for t in request.tools]

    # Step 3. Provider SDK 직접 호출 (LangChain 금지, LOCK-69-9)
    t0 = time.monotonic()
    try:
        raw = await self._call_sdk(request, tool_schemas, timeout=request.timeout_ms/1000)
    except ProviderTimeout as e:
        self._log_error(request, "provider_timeout", e)
        raise
    except ProviderError as e:
        self._log_error(request, e.code, e)
        raise
    latency = int((time.monotonic() - t0) * 1000)

    # Step 4. Tool call → ToolRegistry 실행 (CORE 실행 금지, LOCK-69-5)
    tool_calls_result = None
    if raw.tool_calls:
        tool_calls_result = await asyncio.gather(*[
            ToolRegistry.invoke(tc.tool_id, tc.arguments, trace_id=request.trace_id)
            for tc in raw.tool_calls
        ])

    # Step 5. ConnectorResponse 생성 (LOCK-69-1)
    response = ConnectorResponse(
        output_text=raw.text,
        evidence_summary=raw.evidence,
        cost_used_estimate=self._actual_cost(raw),
        warnings=raw.warnings,
        tool_calls=tool_calls_result,
        trace_id=request.trace_id,
        qod_hint=raw.qod_hint,
    )
    self._log_success(request, response, latency)
    return response
```

### 4.1 시간복잡도 & 패턴 (f)

| 단계 | 복잡도 | 비고 |
|------|--------|------|
| 비용 사전 차단 | O(1) | 토큰 수 추정 — O(len(prompt)) 텍스트 길이 기준 |
| 도구 스키마 조회 | O(T) | T = request.tools 길이 |
| SDK 호출 | O(네트워크 레이턴시) | Provider 의존 |
| Tool 실행 | O(T·f(tool)) | 각 tool 실행 시간 `f` |
| 응답 포장 | O(1) | |
| **전체** | **O(T + 네트워크 + Σf(tool))** | LOCK-69-2 병렬 상한 3 은 라우터 계층 (P1-3) |

**ABC 패턴 매핑**: Template Method (`invoke` 공통 흐름) + Strategy (`_call_sdk` 프로바이더별) + Adapter (SDK → ConnectorResponse 변환).

## 5. 설정 우선순위 (LOCK-69-6) 적용 규칙

```
resolve(key) =
  ENV["VAMOS_BRAIN_" + key.upper()]              # 최우선
  ?? config.yaml:brain.<provider>.<key>          # 두 번째
  ?? CODE_DEFAULT[key]                           # 최후
```

| 설정 키 | ENV | config.yaml 경로 | 코드 기본값 |
|---------|-----|-----------------|-------------|
| ollama.host | `OLLAMA_HOST` | `brain.ollama.host` | `http://localhost:11434` |
| openai.base_url | `OPENAI_API_BASE` | `brain.openai.base_url` | `https://api.openai.com/v1` |
| openai.default_model | `VAMOS_BRAIN_OPENAI_DEFAULT_MODEL` | `brain.openai.default_model` | `gpt-4o-mini` |
| anthropic.base_url | `ANTHROPIC_API_BASE` | `brain.anthropic.base_url` | `https://api.anthropic.com` |
| anthropic.default_model | `VAMOS_BRAIN_ANTHROPIC_DEFAULT_MODEL` | `brain.anthropic.default_model` | `claude-3-5-sonnet-20241022` |
| global.timeout_ms | `VAMOS_BRAIN_TIMEOUT_MS` | `brain.global.timeout_ms` | `30000` |
| global.cost_cap_default | `VAMOS_BRAIN_COST_CAP` | `brain.global.cost_cap_default` | `1.0` |

API 키 (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) 는 **ENV 만 허용** — config.yaml 에 기록 금지. 미설정 시 `get_metadata()` 의 health 비활성 표시.

## 6. 로깅 포맷 (LOCK-69-10, R-01-7)

```json
{
  "ts": "2026-04-14T05:11:02.347Z",
  "level": "INFO",
  "module": "brain_adapter",
  "event": "brain_adapter.invoke",
  "trace_id": "0f8e...-uuid",
  "adapter_id": "llm_openai_text",
  "error": null,
  "context": {
    "task_type": "reasoning",
    "prompt_tokens": 1823,
    "completion_tokens": 412,
    "model": "gpt-4o-mini",
    "tier": "main",
    "tool_count": 2
  },
  "recovery": {
    "retried": 0,
    "fallback_used": false,
    "downgrade_penalty": 0.0
  }
}
```

에러 발생 시 `error{}` 블록 채움:

```json
"error": {
  "code": "cost_cap_exceeded",
  "message": "estimated 1.42 > cap 1.00",
  "recoverable": false,
  "source": "pre_check"
}
```

중첩 구조 `error{}` / `context{}` / `recovery{}` + `trace_id` 4 요소 필수 (R-01-7).

## 7. 예외 처리 정책 (g)

| error_code | 발생 원인 | recoverable | 처리 | 에스컬레이션 |
|------------|----------|-------------|------|-------------|
| `cost_cap_exceeded` | 사전 견적 > cost_cap | NO | 즉시 deny, 호출자에게 raise | I-20 경유 EscalationPayload (severity=medium) |
| `provider_timeout` | SDK 호출 > timeout_ms | YES | P1-4 폴백 체인으로 위임 | 2회 폴백 후 실패 시 I-20 (severity=high) |
| `provider_auth_error` | API 키 오류 | NO | 즉시 raise, health_check 갱신 | I-20 (severity=critical) |
| `provider_rate_limit` | 429 | YES | 지수 백오프 재시도 (최대 2회) 후 폴백 | 폴백 실패 시 I-20 |
| `tool_registry_miss` | tool_id 미등록 | NO | raise `PolicyViolationError` (LOCK-69-3) | I-20 (severity=high) |
| `langchain_import_detected` | import 감지 (사전 린트) | NO | 빌드 차단 | CI 단계 차단 |
| `schema_validation_error` | ConnectorResponse extra=forbid | NO | raise, trace 수집 | I-20 (severity=medium) |
| `provider_5xx` | 프로바이더 서버 오류 | YES | 1회 재시도 후 폴백 | 폴백 결과에 따름 |

### 7.1 Phase 별 복구 흐름도

```
[Phase 1: 사전 견적]
  cost_cap 초과 → deny (복구 없음)
  정상 → Phase 2
          │
[Phase 2: SDK 호출]
  timeout/5xx/429 → Phase 3 (재시도 1회)
  auth_error     → deny + I-20 (복구 없음)
  정상          → Phase 4
          │
[Phase 3: 재시도 (지수 백오프)]
  성공 → Phase 4
  실패 → P1-4 폴백 체인 호출 (다음 프로바이더, confidence penalty -0.10)
          │
[Phase 4: ToolRegistry 실행]
  tool_registry_miss → deny + I-20 (복구 없음)
  tool 실행 실패    → warnings 에 기록, output 반환 (graceful)
  정상             → Phase 5
          │
[Phase 5: ConnectorResponse 포장]
  schema_validation_error → I-20 + raise
  정상                    → 반환
```

### 7.2 다운그레이드 Confidence Penalty 표

| 다운그레이드 시나리오 | Penalty | 누적 한도 |
|-----------------------|---------|-----------|
| 재시도 1회 성공 | -0.05 | — |
| 폴백 1단계 전환 성공 (LOCK-69-8) | -0.10 | -0.30 |
| 폴백 2단계 전환 성공 | -0.20 | -0.30 |
| Ollama 로컬 폴백 도달 | -0.25 | -0.30 |
| tool 부분 실패 (warnings 기록) | -0.05 per tool | -0.15 |

`qod_hint` 가 존재할 경우 `qod_hint_final = max(0.0, qod_hint - Σpenalty)`.

## 8. 에스컬레이션 Payload 구조 (I-20 경유)

```python
class EscalationPayload(BaseModel):
    source_engine: str              # ex: "brain_adapter.openai"
    error_code: str                 # §7 표의 code
    severity: Literal["low", "medium", "high", "critical"]
    original_request: BrainRequest  # redacted (API 키/PII 제거)
    partial_result: Optional[ConnectorResponse] = None
    retry_count: int
    fallback_path: List[str] = []   # ex: ["openai", "anthropic"]
    timestamp: str                  # ISO8601
    trace_id: str
    notes: Optional[str] = None
    class Config: extra = "forbid"
```

전달 경로: `BrainAdapter → I-20 Escalation Router → 6-2 Security-Governance (로깅) + 0-0 Governance (정책 위반 시)`. I-20 호출 자체는 동기 (fire-and-forget 금지 — R-01-8).

## 9. 단위 테스트 케이스 정의 (P1-1 산출물 — 3 프로바이더)

> Phase 2 통합 테스트의 선행 단위 테스트. `test_brain_adapters.py` 에 각 프로바이더 × 케이스로 총 ≥ 21 케이스 작성.

| # | 케이스 | 대상 | 입력/주입 | 기대 결과 | LOCK 참조 |
|---|--------|------|-----------|-----------|-----------|
| U1 | 정상 응답 필드 완전성 | Ollama/OpenAI/Anthropic | 유효 BrainRequest, SDK mock 성공 | ConnectorResponse 5 필수 필드 모두 존재, extra=forbid 통과 | LOCK-69-1 |
| U2 | trace_id 전파 | 3 프로바이더 | request.trace_id="T-001" | response.trace_id == "T-001" | LOCK-69-1 |
| U3 | 비용 상한 초과 차단 | 3 프로바이더 | cost_cap=0.01, prompt 10k tokens | CostCapExceededError raise, SDK 호출 0회 | LOCK-69-7 |
| U4 | LangChain import 부재 | 3 모듈 | `importlib` 스캔 | `langchain*` import 0건 | LOCK-69-9 |
| U5 | ToolRegistry 경유 | 3 프로바이더 | tools=[ToolCallRequest(tool_id="web_search")], mock ToolRegistry.invoke | ToolRegistry.invoke 호출 1회, 직접 URL fetch 0회 | LOCK-69-3 |
| U6 | 미등록 tool_id | 3 프로바이더 | tool_id="not_registered" | PolicyViolationError raise | LOCK-69-3 |
| U7 | ENV 우선순위 | 3 프로바이더 | ENV/config/기본값 서로 다른 값 | resolve 결과 == ENV 값 | LOCK-69-6 |
| U8 | config 우선순위 | 3 프로바이더 | ENV 미설정, config/기본값 상이 | resolve == config 값 | LOCK-69-6 |
| U9 | 기본값 폴스루 | 3 프로바이더 | ENV/config 모두 미설정 | resolve == 코드 기본값 | LOCK-69-6 |
| U10 | JSON 로그 구조 | 3 프로바이더 | 정상 invoke | log line 은 JSON, `error/context/recovery/trace_id` 4 블록 존재 | LOCK-69-10 |
| U11 | 타임아웃 폴백 전파 | 3 프로바이더 | SDK mock timeout | provider_timeout raise, recovery.retried==0, fallback_used==false (P1-4 에서 폴백) | §7 |
| U12 | health_check 정상 | 3 프로바이더 | 엔드포인트 200 | HealthStatus(healthy=True, latency_ms>0) | — |
| U13 | health_check 실패 | 3 프로바이더 | 엔드포인트 5xx | HealthStatus(healthy=False, details!=None) | — |
| U14 | get_metadata capabilities | 3 프로바이더 | 호출 | `text_gen` 항상 존재, provider/adapter_id 일치 | — |
| U15 | CORE 실행 금지 | 3 프로바이더 | tool_calls mock — 어댑터가 직접 파일 IO 시도 | 탐지 시 PolicyViolationError | LOCK-69-5 |

## 10. Phase 2 통합 테스트 시나리오 힌트 (≥ 10 건)

| # | 시나리오 | 주입 방법 | 기대 결과 |
|---|----------|-----------|-----------|
| IT-1 | 1-1 C-1 추론 엔진 → Brain Adapter → Ollama → C-1 로 응답 반환 | C-1 테스트 러너에서 `llm_ollama_text` 지정 | ConnectorResponse 전달, evidence_summary 비어있지 않음 |
| IT-2 | OpenAI → tool_call → web_search → 결과 재통합 | `tools=[{tool_id:"web_search"}]`, ToolRegistry mock | tool_calls 배열 1건, output_text 에 결과 반영 |
| IT-3 | Anthropic 비용 상한 초과 시나리오 | prompt 100k tokens, cost_cap=0.05 | 차단 로그 1건, SDK 호출 0 |
| IT-4 | 3 프로바이더 병렬 호출 (LOCK-69-2 상한 3) | 3 동시 invoke | 모두 성공, 4번째 요청은 큐잉 |
| IT-5 | LangChain import 린트 | pre-commit hook `ast` 스캔 | PR 차단 |
| IT-6 | ENV override 런타임 반영 | `OPENAI_API_BASE` 변경 후 재호출 | 새 엔드포인트 사용 |
| IT-7 | ToolRegistry 미등록 tool 호출 | `tool_id="unknown"` 주입 | PolicyViolationError + I-20 payload 전송 확인 |
| IT-8 | 30초 타임아웃 실측 | SDK sleep(31s) mock | provider_timeout 29.5~30.5s 내 발생 |
| IT-9 | JSON 로그 중첩 구조 검증 | 10회 invoke 후 로그 수집 | `error/context/recovery/trace_id` 4 블록 모두 존재 |
| IT-10 | CORE 실행 금지 위반 탐지 | 어댑터 내부에서 `subprocess.run` 시도 mock | PolicyViolationError |
| IT-11 | 6-11 Main LLM tier="main" 호출 | `BrainRequest(task_type="main_llm", tier="main")` | Anthropic 어댑터로 라우팅 (P1-3 기본 규칙) |
| IT-12 | 4-4 MLOps 드리프트 메트릭 주입 | `RoutingWeightUpdate` 주입 | 라우팅 가중치 업데이트 반영 (Phase 3) |

## 11. 세션 간 인터페이스 cross-check (j)

| 상대 세션 | 공유 항목 | 본 P1-1 정의 | 일치 여부 |
|-----------|-----------|--------------|-----------|
| P1-2 HAL V1 | BrainAdapter → HAL 호출 방향 | `BaseBrainAdapter.invoke` 가 HAL.get_endpoint(provider) 로 엔드포인트 결정 | P1-2 `hal_v1.get_endpoint(provider: str) -> HalEndpoint`; 호출자는 `.base_url` 속성으로 URL 문자열 획득 (P1-2 §8 INTERFACE_DIFF_NOTE, 하위 호환) |
| P1-3 라우터 V1 | 라우터 → BrainAdapter 선택 | `BrainRequest.task_type + tier` 로 선택 | P1-3 Router.select(req) -> BaseBrainAdapter |
| P1-4 폴백 체인 | 에러 → 폴백 트리거 | §7 `recoverable=YES` 에러만 폴백 대상 | P1-4 에서 LOCK-69-8 순서 구현 |
| P1-5 통합 (1-1 연동) | ConnectorResponse 5 필수 필드 | `_index.md §3.1` 정본 따름 | 일치 |

[INTERFACE_MISMATCH: 없음] — 상위 정본 `_index.md` §2/§3/§4 ABC/스키마를 그대로 준수.

## 12. P4 이슈 해결 기록 (§6 P4 — 의존성 인터페이스 미매핑)

| 소비 도메인 | 요청 스키마 | 응답 스키마 | 에러 핸들링 | 본 문서 위치 |
|-------------|------------|-----------|-------------|--------------|
| 1-1 Verifier-Reasoning | `BrainRequest(task_type="reasoning")` | `ConnectorResponse` | §7 정책표 | §2.1, §9 U1/IT-1 |
| 4-4 MLOps-LLMOps | `RoutingWeightUpdate(model_id, quality_delta)` (Phase 3) | N/A (단방향) | I-20 경유 실패 시 로깅만 | Phase 3 (본 세션 제외) |
| 6-11 Hologram-Main-LLM | `BrainRequest(task_type="main_llm", tier="main")` | `ConnectorResponse` | §7 정책표 | §2.1, IT-11 |
| 4-3 MCP-Server-Client | `BrainRequest.tools=[ToolCallRequest]` | `ConnectorResponse.tool_calls` | tool_registry_miss → PolicyViolationError | §2.1, §9 U5/U6 |

`_index.md §5 의존성 매핑` 과 일관되며 P4 이슈의 "인터페이스 미매핑" 을 해소한다. (`_index.md` 자체의 §5 업데이트는 공통 산출물 보호 정책에 따라 step 5/7/8 에서 일괄 반영 — 본 세션에서는 본 사양서로 대체 기록.)

## 13. 산출물 파일 경로 (실코드 — 본 세션에서는 경로만 고정)

| 산출물 | 경로 | 세션 구현 여부 |
|--------|------|-----------------|
| Ollama 어댑터 | `vamos/adapters/brain/ollama_adapter.py` | 본 세션 사양 — 실파일은 구현 단계(`D:\VAMOS\04. 구현단계\[버전]\`)에서 작성 |
| OpenAI 어댑터 | `vamos/adapters/brain/openai_adapter.py` | 동상 |
| Anthropic 어댑터 | `vamos/adapters/brain/anthropic_adapter.py` | 동상 |
| 공통 Base | `vamos/adapters/brain/base.py` (`BaseBrainAdapter`, `BrainRequest`, `AdapterMetadata`, `HealthStatus`) | 동상 |
| 단위 테스트 | `tests/unit/adapters/test_brain_adapters.py` | 동상 — 케이스 §9 |

본 문서(`P1-1_brain_adapter_v1_spec.md`)는 위 코드의 정본 사양서이며, `_index.md §5 구현 상태` 갱신은 도메인 마감(step 5/7/8)에서 일괄 반영한다.

## 14. 검증 체크리스트 매핑 (종합계획서 §7 P1-1 검증란 1:1)

| 검증 항목 | 본 문서 대응 | 상태 |
|-----------|--------------|------|
| Ollama/OpenAI/Anthropic 단위 테스트 3개 PASS | §9 U1~U15 케이스 정의 | L2 (케이스 정의 완료, 실행은 구현 단계) |
| ConnectorResponse 5 필드 존재 | §2 Base 상속 + _index.md §3.1 참조 | L3 (사양 FROZEN) |
| LangChain import 부재 | §3 SDK 직접, §9 U4, §10 IT-5 | L2 |
| ToolRegistry 경유 | §4 Step 2/4, §9 U5/U6, §10 IT-2/IT-7 | L2 |
| 비용 상한 초과 차단 | §4 Step 1, §7 cost_cap_exceeded, §9 U3 | L2 |
| `_index.md §5` 갱신 | 도메인 마감 step 5/7/8 에서 일괄 | 보류 (본 세션 금지) |

---

## 부록 A. CONFLICT 후보 / LOCK 변경 필요 여부

- [LOCK_CHANGE_NEEDED] 없음 — 본 세션은 LOCK-69-1/3/5/6/7/9/10 을 그대로 준수한다.
- [CONFLICT_CANDIDATE] 없음 — `_index.md §3.3` 에서 이미 §3 텍스트 ↔ §3.1 Pydantic 불일치를 해결 기록했고, 본 사양은 §3.1 기준을 따른다.

## 부록 B. 갱신 이력

| 날짜 | 세션 | 변경 |
|------|------|------|
| 2026-04-14 | P1-1 step1 | 최초 작성 — V1 3 프로바이더 사양 L2 확정 |
