# python_sdk.md — VAMOS Python SDK (V2-Phase 2)

> **Status**: DRAFT — Phase 2 V2-Phase 2
> **버전**: v2.0 (2026-04-21)
> **도메인**: #10 Developer-Tools-API-SDK, 서브폴더 `07_marketplace/`
> **대응 STEP7-L**: **L-012 "VAMOS Python SDK"** (STEP7-L L252~L284 전수 verbatim 반영)
> **LOCK**: LOCK-DT-02 (SDK 호환성 Python ≥ 3.9, 직접 참조), LOCK-DT-01 (API 버저닝, base_url), LOCK-DT-06 (타임아웃 30s), LOCK-DT-08 (Rate Limiting)
> **관련 V2**: `rest_api.md` (본 세션 P2-5 peer — REST API 계약), `typescript_sdk.md` (peer), `webhook_events.md` (peer), `api_docs_generator.md` (peer)

---

## §0. Purpose / Scope

### §0.1 목적

VAMOS Python SDK (PyPI `vamos-sdk`) 의 **최상위 API 정본** 을 Phase 2 범위에서 확정한다. 본 문서는 다음 5개의 근간 축을 정의한다:

1. **호환성 매트릭스** (LOCK-DT-02 — Python ≥ 3.9, OS 전수)
2. **VamosClient / AsyncVamosClient 시그니처 정본** (STEP7-L L255~L281 verbatim)
3. **네임스페이스 구조** (chat/memory/agent/image/audio/investment/kg/code)
4. **에러 처리 + 재시도 + Rate Limit** (LOCK-DT-06/08)
5. **타입 힌트 + mypy 호환** (STEP7-L L281 "타입 힌트 완전 지원 (mypy 호환)")

### §0.2 Phase 2 범위 vs Phase 3 이월

| 축 | Phase 2 확정 | Phase 3 이월 |
|----|------------|--------------|
| sync/async 클라이언트 | ✅ 본 문서 §3 | WebSocket 클라이언트 (V3) |
| 8 네임스페이스 | ✅ 본 문서 §4 | GraphQL 클라이언트 (V3) |
| Pydantic 모델 자동 생성 | ✅ 본 문서 §5 | IDE 플러그인 (JetBrains, PyCharm) |
| 재시도 + RL 핸들링 | ✅ 본 문서 §6 | 분산 환경 토큰 공유 |
| 타입 스텁 + mypy | ✅ 본 문서 §7 | Literal overloads 확장 |
| 배포 + 버전 정책 | ✅ 본 문서 §8 | conda-forge 동시 배포 |

### §0.3 STEP7-L L-012 원문 앵커 (verbatim)

```
[STEP7-L L252] ### L-012. VAMOS Python SDK
[STEP7-L L255] from vamos import VamosClient
[STEP7-L L257] client = VamosClient(api_key="...", base_url="http://localhost:8000")
[STEP7-L L259] # 대화
[STEP7-L L260] response = client.chat("오늘 삼성전자 분석해줘")
[STEP7-L L262] # 스트리밍
[STEP7-L L263] for chunk in client.chat_stream("코드 리뷰 해줘"):
[STEP7-L L264]     print(chunk.text, end="")
[STEP7-L L266] # 메모리
[STEP7-L L267] results = client.memory.search("지난주 분석한 종목")
[STEP7-L L268] client.memory.store("AAPL 분석 결과: ...", level="L2")
[STEP7-L L270] # 에이전트
[STEP7-L L271] task = client.agent.run(
[STEP7-L L272]     node="quant",
[STEP7-L L273]     task="삼성전자 DCF 밸류에이션",
[STEP7-L L274]     tools=["yfinance", "dart"]
[STEP7-L L275] )
[STEP7-L L277] # 이미지
[STEP7-L L278] image = client.image.generate("VAMOS 로고 디자인")
[STEP7-L L280] - PyPI 배포: pip install vamos-sdk
[STEP7-L L281] - 타입 힌트 완전 지원 (mypy 호환)
[STEP7-L L282] - 비동기 지원: AsyncVamosClient
[STEP7-L L284] [구현성] V2: ✅ 2개월
```

---

## §1. 교차 참조 블록

| 참조 문서 | 위치 | 본 문서 사용 목적 |
|----------|------|-----------------|
| `D:\VAMOS\docs\sot\STEP7-L_개발자도구_API_SDK_작업가이드.md` | L252~L284 (L-012) | Phase 2 원문 정본 (verbatim) |
| `AUTHORITY_CHAIN.md` §5 | L59 LOCK-DT-02 | Python ≥ 3.9 verbatim |
| `rest_api.md` §3 / §8 (peer V2) | 세션 P2-5 | REST 엔드포인트 + Pydantic 공유 구조 |
| `webhook_events.md` (peer V2) | 세션 P2-5 | `client.webhooks.register()` 소비 |

---

## §2. 호환성 매트릭스 (LOCK-DT-02 "Python ≥ 3.9" verbatim)

### §2.1 Python 런타임

| Python 버전 | 상태 | 비고 |
|------------|------|------|
| **3.9** | ✅ minimum (LOCK-DT-02) | `python_requires=">=3.9"` |
| 3.10 | ✅ 권장 | pattern matching 활용 |
| 3.11 | ✅ 권장 | 예외 그룹 활용 |
| 3.12 | ✅ 권장 | PEP 695 generic |
| 3.13 | ✅ 권장 | JIT 실험 지원 |
| < 3.9 | ❌ 미지원 | 설치 거부 |

### §2.2 OS / 아키텍처

| OS | x86_64 | arm64 | 비고 |
|----|--------|-------|------|
| macOS ≥ 12 | ✅ | ✅ (Apple Silicon) | wheel 제공 |
| Linux (glibc ≥ 2.28) | ✅ | ✅ | manylinux_2_28 wheel |
| Windows 10+ | ✅ | ❌ (실험) | msvc wheel |

### §2.3 런타임 의존성 (최소)

| 패키지 | 버전 | 용도 |
|-------|-----|------|
| `httpx` | `≥ 0.26,<1.0` | sync/async HTTP |
| `pydantic` | `≥ 2.5,<3.0` | 모델 검증 |
| `typing-extensions` | `≥ 4.8` | Python 3.9~3.10 호환 |
| `anyio` | `≥ 4.0` | AsyncClient 백엔드 추상 |

---

## §3. VamosClient / AsyncVamosClient 정본

### §3.1 sync 클라이언트 (STEP7-L L255~L278)

```python
# vamos/client.py
from typing import Iterator, Optional
import httpx
import uuid
from .models import ChatResponse, ChatChunk, MemorySearchResponse
from .namespaces import MemoryNamespace, AgentNamespace, ImageNamespace, AudioNamespace, \
                        InvestmentNamespace, KgNamespace, CodeNamespace, WebhookNamespace

class VamosClient:
    """VAMOS Python SDK (sync).

    Example (STEP7-L L255~L260):
        >>> from vamos import VamosClient
        >>> client = VamosClient(api_key="...", base_url="http://localhost:8000")
        >>> response = client.chat("오늘 삼성전자 분석해줘")
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.vamos.local/api/v1",  # LOCK-DT-01
        timeout: float = 30.0,                              # LOCK-DT-06 상한
        max_retries: int = 3,
        *,
        user_agent: Optional[str] = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        # LOCK-DT-01 검증: /api/v{N}/ prefix
        if "/api/v" not in self.base_url:
            raise ValueError(f"base_url must include /api/v{{N}}/ prefix (LOCK-DT-01): got {base_url!r}")
        if timeout > 30.0:
            logger.warning("timeout %.1fs exceeds LOCK-DT-06 30s cap; clamping to 30.0", timeout)
        if timeout > 30.0:
            logger.warning("timeout %.1fs exceeds LOCK-DT-06 30s cap; clamping to 30.0", timeout)
        self._http = httpx.Client(
            timeout=min(timeout, 30.0),                     # LOCK-DT-06
            headers={
                "Authorization": f"ApiKey {api_key}",
                "X-Client-Version": user_agent or f"python-sdk/{__version__}",
            },
        )
        self.max_retries = max_retries
        # 네임스페이스
        self.memory     = MemoryNamespace(self)
        self.agent      = AgentNamespace(self)
        self.image      = ImageNamespace(self)
        self.audio      = AudioNamespace(self)
        self.investment = InvestmentNamespace(self)
        self.kg         = KgNamespace(self)
        self.code       = CodeNamespace(self)
        self.webhooks   = WebhookNamespace(self)

    def chat(self, prompt: str, *, model: str = "claude-sonnet-4-6",
             max_tokens: int = 4096, temperature: float = 0.7) -> ChatResponse:
        """단일 턴 대화 (STEP7-L L260)."""
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        return self._request_model(
            "POST", "/chat", json=payload, model=ChatResponse,
        )

    def chat_stream(self, prompt: str, *, model: str = "claude-sonnet-4-6") -> Iterator[ChatChunk]:
        """스트리밍 대화 (STEP7-L L263~L264, SSE)."""
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}
        with self._http.stream("POST", f"{self.base_url}/chat/stream", json=payload) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if line.startswith("data: "):
                    yield ChatChunk.model_validate_json(line[6:])

    def _request_model(self, method: str, path: str, **kwargs) -> "ChatResponse":
        """내부: 재시도 + Rate Limit 핸들링 (§6 참조)."""
        ...

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "VamosClient": return self
    def __exit__(self, *exc) -> None: self.close()
```

### §3.2 async 클라이언트 (STEP7-L L282)

```python
# vamos/async_client.py
from typing import AsyncIterator

class AsyncVamosClient:
    """VAMOS Python SDK (async).

    Example:
        >>> async with AsyncVamosClient(api_key="...") as client:
        ...     response = await client.chat("질문")
        ...     async for chunk in client.chat_stream("스트림"):
        ...         print(chunk.text, end="")
    """

    def __init__(self, api_key: str, base_url: str = "https://api.vamos.local/api/v1",
                 timeout: float = 30.0, max_retries: int = 3) -> None:
        self._http = httpx.AsyncClient(
            timeout=min(timeout, 30.0),  # LOCK-DT-06
            headers={"Authorization": f"ApiKey {api_key}"},
        )
        self.base_url = base_url.rstrip("/")
        # 동일 네임스페이스 (async variant)
        self.memory = AsyncMemoryNamespace(self)
        # ...

    async def chat(self, prompt: str, *, model: str = "claude-sonnet-4-6") -> ChatResponse: ...

    async def chat_stream(self, prompt: str, *, model: str = "claude-sonnet-4-6") -> AsyncIterator[ChatChunk]:
        async with self._http.stream("POST", f"{self.base_url}/chat/stream",
                                     json={"model": model, "messages": [{"role": "user", "content": prompt}]}) as r:
            async for line in r.aiter_lines():
                if line.startswith("data: "):
                    yield ChatChunk.model_validate_json(line[6:])

    async def aclose(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> "AsyncVamosClient": return self
    async def __aexit__(self, *exc) -> None: await self.aclose()
```

---

## §4. 네임스페이스 상세

### §4.1 `client.memory` (L267~L268)

```python
class MemoryNamespace:
    def search(self, query: str, *, level: Optional[str] = None, limit: int = 10) -> MemorySearchResponse:
        """STEP7-L L267: client.memory.search('지난주 분석한 종목')"""
        params = {"q": query, "limit": limit}
        if level: params["level"] = level
        return self._client._request_model("GET", "/memory/search", params=params, model=MemorySearchResponse)

    def store(self, content: str, *, level: str = "L2", tags: Optional[list[str]] = None,
              ttl_seconds: Optional[int] = None) -> "MemoryStoreResponse":
        """STEP7-L L268: client.memory.store('...', level='L2')"""
        return self._client._request_model("POST", "/memory/store",
                                           json={"content": content, "level": level,
                                                 "tags": tags or [], "ttl_seconds": ttl_seconds},
                                           model=MemoryStoreResponse)
```

### §4.2 `client.agent` (L271~L275)

```python
class AgentNamespace:
    def run(self, *, node: str, task: str, tools: Optional[list[str]] = None,
            max_steps: int = 15) -> AgentRunResponse:
        """STEP7-L L271~L275: client.agent.run(node=..., task=..., tools=[...])"""
        return self._client._request_model("POST", "/agent/run",
                                           json={"node": node, "task": task,
                                                 "tools": tools or [], "max_steps": max_steps},
                                           model=AgentRunResponse)
```

### §4.3 `client.image` (L278)

```python
class ImageNamespace:
    def generate(self, prompt: str, *, size: str = "1024x1024",
                 style: Optional[str] = None) -> ImageGenerateResponse:
        """STEP7-L L278: client.image.generate('VAMOS 로고 디자인')"""
        return self._client._request_model("POST", "/image/generate",
                                           json={"prompt": prompt, "size": size, "style": style},
                                           model=ImageGenerateResponse)

    def analyze(self, image: bytes | str, instruction: str) -> ImageAnalyzeResponse:
        """이미지 분석 (L-011 엔드포인트 /image/analyze)."""
        files = {"image": image if isinstance(image, bytes) else open(image, "rb")}
        return self._client._request_model("POST", "/image/analyze",
                                           data={"instruction": instruction}, files=files,
                                           model=ImageAnalyzeResponse)
```

### §4.4 `client.audio`

```python
class AudioNamespace:
    def stt(self, audio: bytes | str, *, language: str = "ko") -> SttResponse: ...
    def tts(self, text: str, *, voice: str = "ko-female-01") -> bytes: ...
```

### §4.5 `client.investment`, `client.kg`, `client.code`, `client.webhooks`

각각 `/investment/*`, `/kg/query`, `/code/execute`, `/webhooks` 엔드포인트에 대응 (`rest_api.md §3` 참조).

---

## §5. Pydantic 모델 (shared with rest_api.md §8)

```python
# vamos/models.py
from pydantic import BaseModel, Field
from typing import Literal, Optional

class ChatChoice(BaseModel):
    index: int
    message: "ChatMessage"
    finish_reason: Literal["stop", "length", "tool_calls", "content_filter"]

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str

class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatResponse(BaseModel):
    id: str
    trace_id: str
    choices: list[ChatChoice]
    usage: Usage
    latency_ms: int

class ChatChunk(BaseModel):
    type: Literal["chunk", "done", "error"]
    delta: Optional[str] = None
    text: Optional[str] = None   # 편의 필드 (STEP7-L L264 호환: chunk.text)
    trace_id: Optional[str] = None
    usage: Optional[Usage] = None

    def __init_subclass__(cls, **kwargs): super().__init_subclass__(**kwargs)

    # STEP7-L L264 "chunk.text" 사용 예시 호환
    @property
    def _text(self) -> str: return self.text or self.delta or ""

class MemorySearchResponse(BaseModel):
    trace_id: str
    results: list[dict]
    total: int

class MemoryStoreResponse(BaseModel):
    id: str
    trace_id: str
    stored_at: str

class AgentRunResponse(BaseModel):
    trace_id: str
    job_id: Optional[str] = None
    result: dict
    steps: list[dict]
    elapsed_seconds: float

class ImageGenerateResponse(BaseModel):
    trace_id: str
    image_url: str
    job_id: Optional[str] = None

class ImageAnalyzeResponse(BaseModel):
    trace_id: str
    description: str
    objects: list[dict] = Field(default_factory=list)

class SttResponse(BaseModel):
    trace_id: str
    text: str
    language: str
    segments: list[dict] = Field(default_factory=list)

class ProblemDetails(BaseModel):
    type: str
    title: str
    status: int
    detail: Optional[str] = None
    trace_id: str
```

---

## §6. 에러 + 재시도 + Rate Limit

### §6.1 예외 계층

```python
class VamosError(Exception): ...
class VamosAuthError(VamosError): ...           # 401/403
class VamosRateLimitError(VamosError):          # 429
    retry_after: int
class VamosTimeoutError(VamosError): ...        # LOCK-DT-06 초과
class VamosServerError(VamosError): ...         # 5xx
class VamosValidationError(VamosError): ...     # Pydantic 검증 실패
```

### §6.2 재시도 정책 (exponential backoff with jitter)

```python
def _request_with_retry(self, method, path, **kwargs):
    for attempt in range(self.max_retries + 1):
        try:
            r = self._http.request(method, f"{self.base_url}{path}", **kwargs)
            if r.status_code == 429:
                retry_after = int(r.headers.get("Retry-After", "5"))
                if attempt < self.max_retries:
                    time.sleep(retry_after + random.uniform(0, 0.5))   # jitter
                    continue
                raise VamosRateLimitError(r.text, retry_after=retry_after)
            if r.status_code in (502, 503, 504) and attempt < self.max_retries:
                time.sleep((2 ** attempt) + random.uniform(0, 0.5))
                continue
            r.raise_for_status()
            return r
        except httpx.TimeoutException as e:
            if attempt < self.max_retries:
                time.sleep((2 ** attempt))
                continue
            raise VamosTimeoutError(str(e)) from e
```

### §6.3 LOCK 준수 매트릭스

| 동작 | LOCK | 준수 방법 |
|-----|------|----------|
| `timeout=31` 설정 | LOCK-DT-06 | 생성자 `min(timeout, 30.0)` → 경고 로그 |
| base_url "/api/v1/" 누락 | LOCK-DT-01 | 생성자 `ValueError` |
| Rate Limit 초과 | LOCK-DT-08 | `VamosRateLimitError` + `retry_after` 자동 wait |
| Python 3.8 이하 | LOCK-DT-02 | setup.py `python_requires=">=3.9"` |

### §6.4 구조화 로깅 (R-01-7)

```python
import logging
logger = logging.getLogger("vamos")

def _log(self, *, endpoint, status, trace_id, latency_ms, error=None):
    logger.info(json.dumps({
        "error": {"code": error.__class__.__name__, "message": str(error)} if error else None,
        "context": {"endpoint": endpoint, "status": status, "sdk": f"python-sdk/{__version__}"},
        "recovery": "retry_with_backoff" if isinstance(error, (VamosRateLimitError, VamosTimeoutError)) else None,
        "trace_id": trace_id, "latency_ms": latency_ms,
    }))
```

---

## §7. 타입 힌트 + mypy (STEP7-L L281)

### §7.1 PEP 561 마커

```
vamos/
  __init__.py
  py.typed           # PEP 561 marker (빈 파일)
  client.py
  async_client.py
  models.py
  namespaces/
    __init__.py
    memory.py
    agent.py
    ...
```

### §7.2 mypy 설정 (strict 호환)

```toml
# pyproject.toml 발췌
[tool.mypy]
python_version = "3.9"
strict = true
warn_return_any = true
disallow_untyped_defs = true
no_implicit_optional = true
plugins = ["pydantic.mypy"]
```

### §7.3 Overloads (예시)

```python
from typing import overload, Literal

class VamosClient:
    @overload
    def chat(self, prompt: str, *, stream: Literal[False] = False, model: str = ...) -> ChatResponse: ...
    @overload
    def chat(self, prompt: str, *, stream: Literal[True], model: str = ...) -> Iterator[ChatChunk]: ...

    def chat(self, prompt, *, stream=False, model="claude-sonnet-4-6"):
        if stream: return self.chat_stream(prompt, model=model)
        return self._do_chat(prompt, model=model)
```

---

## §8. 배포 + 버전 정책 (STEP7-L L280)

### §8.1 pyproject.toml 발췌

```toml
[project]
name = "vamos-sdk"
version = "1.0.0"
requires-python = ">=3.9"    # LOCK-DT-02
dependencies = [
    "httpx>=0.26,<1.0",
    "pydantic>=2.5,<3.0",
    "typing-extensions>=4.8",
    "anyio>=4.0",
]

[project.optional-dependencies]
test = ["pytest>=8.0", "pytest-asyncio>=0.23", "respx>=0.21"]

[project.urls]
Homepage = "https://docs.vamos.local/python-sdk"
Source   = "https://github.com/vamos-ai/vamos-sdk-python"
```

### §8.2 버전 정책 (semver)

| 변경 | 예시 | SDK 버전 |
|-----|------|---------|
| REST API MAJOR (`/api/v1/` → `/api/v2/`) | breaking change | SDK MAJOR bump |
| REST API MINOR (새 엔드포인트) | 추가 | SDK MINOR bump |
| REST API PATCH (버그픽스) | 호환 | SDK PATCH bump |
| SDK 내부 리팩토링 (공개 API 불변) | - | PATCH bump |

---

## §9. 품질 지표

| 지표 | 임계값 | 측정 |
|-----|-------|------|
| mypy strict 통과 | 100% | CI |
| 타입 힌트 커버리지 | ≥ 95% | `mypy --strict` |
| 테스트 커버리지 | ≥ 80% (LOCK-DT-10 간접) | pytest-cov |
| `pip install vamos-sdk` 성공 | 3 OS × 5 Python = 15 CI 매트릭스 | GitHub Actions |
| Pydantic 응답 검증 실패 | = 0 (스키마 sync) | CI |
| LOCK-DT-06 30s 초과 실패 | 0 | unit test |

---

## §10. V1 ↔ V2 정합 매트릭스

| V1/V2 파일 | 관계 | 정합 처리 |
|-----------|------|----------|
| `rest_api.md §3` | REST 엔드포인트 정본 | §4 네임스페이스가 1:1 매핑 |
| `rest_api.md §8` | Pydantic 공통 구조 | §5 가 subset 소비 |
| `07_marketplace/cli_tool.md` (V1, L-014) | CLI 가 본 SDK 를 import 가능 | 참조 |

---

## §11. FABRICATION 방지 주석

- STEP7-L L252~L284 L-012 verbatim 전수
- LOCK-DT-02 L59 "Python ≥ 3.9" verbatim (§2.1)
- `httpx` / `pydantic v2` 공식 API 만 사용 (초과 필드 0)
- 가상의 `vamos_internal`, `vamos_secret` 등 모듈명 발명 0건

---

## §12. Phase 3 테스트 시나리오 (≥ 10건)

| # | ID | 시나리오 | 입력 | 기대 결과 |
|---|-----|---------|------|----------|
| 1 | PS-T01 | 기본 chat | `client.chat("안녕")` | `ChatResponse` 정상 |
| 2 | PS-T02 | 스트리밍 | `for chunk in client.chat_stream(...)` | ChatChunk iter 정상 |
| 3 | PS-T03 | async chat | `await aclient.chat(...)` | 정상 |
| 4 | PS-T04 | base_url 검증 | `base_url="http://x"` | `ValueError` (LOCK-DT-01) |
| 5 | PS-T05 | timeout > 30 | `timeout=60` | 내부 30 으로 절단 + 경고 |
| 6 | PS-T06 | 429 자동 재시도 | 4xx 2회 + OK | 최종 정상 |
| 7 | PS-T07 | Python 3.8 설치 | `pip install` on 3.8 | setup 에서 거부 |
| 8 | PS-T08 | mypy strict | 샘플 코드 | 0 errors |
| 9 | PS-T09 | Pydantic 검증 실패 | 서버 응답 스키마 변경 | `VamosValidationError` |
| 10 | PS-T10 | 컨텍스트 매니저 | `with VamosClient(...) as c:` | close 자동 호출 |
| 11 | PS-T11 | 메모리 저장/검색 roundtrip | store → search | 동일 내용 반환 |
| 12 | PS-T12 | 에이전트 run | node="quant" | 정상 결과 |

---

## §13. 변경 이력

| 날짜 | 버전 | 변경 내용 | 변경자 |
|------|------|----------|--------|
| 2026-04-21 | v2.0 | Phase 2 P2-5 최초 작성 — STEP7-L L-012 verbatim + LOCK-DT-02 Python≥3.9 + sync/async + 8 네임스페이스 + mypy strict + PyPI 배포 정본 | P2-5 세션 |
