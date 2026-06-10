# FIM (Fill-in-the-Middle) 프로토콜

> **L-ID**: L-002
> **V 배정**: V1 (즉시 구현 가능)
> **Phase**: Phase 1 P1-2
> **수준**: L3 (D1~D8 전수 완성, P0 항목)
> **의존 LOCK**: LOCK-DT-04 (FIM 모델 fallback chain), LOCK-DT-07 (자동완성 디바운스 150ms)
> **S번호**: S-DT-002-FIM

---

## 교차 참조 블록

| 정본 문서 | 참조 내용 |
|----------|----------|
| STEP7-L L-002 | 인라인 코드 자동완성 구현 상세 — FIM, 다중 제안, 컨텍스트 인식, 학습 |
| 종합계획서 §2.1 | 폴더 트리 — 02_code-completion 매핑 |
| 종합계획서 §3.4 | LOCK-DT-04 (FIM fallback chain), LOCK-DT-07 (디바운스 150ms) |
| 종합계획서 §A | FIM 프로토콜 부록 — 요청/응답 스키마, fallback chain, 성능 최적화, 랭킹 알고리즘 |
| 종합계획서 §11.2 | FR-5 FIM 프로토콜 운영 상세 — 토큰 관리, 지연 예산, 신뢰도 스코어링 |
| 종합계획서 §13 | L3 전수 승급 기준 D1~D8 |
| ranking_algorithm.md | 제안 랭킹 알고리즘 (세션간 인터페이스) |
| local_model_setup.md | 로컬 모델 설정 (세션간 인터페이스) |
| 01_coding-engine/dev_node_architecture.md | 코딩 엔진 아키텍처 — FIM 호출 인터페이스 참조 |
| DEVELOPER_TOOLS_API_SDK_상세명세.md | 기술 아키텍처 참조 |

---

## D1. Input Schema

### 1.1 FIM 요청 (FIMRequest)

```typescript
interface FIMRequest {
  prefix: string;         // 커서 앞 코드 (최대 4096 토큰)
  suffix: string;         // 커서 뒤 코드 (최대 2048 토큰)
  language: string;       // 프로그래밍 언어 (ISO 639-1 또는 언어 ID)
  file_path: string;      // 파일 경로 (컨텍스트 힌트)
  max_tokens: number;     // 생성 최대 토큰 수, 기본값 128
  temperature: number;    // 기본값 0.0 (결정론적)
  stop_sequences: string[]; // 생성 중단 시퀀스
}
```

> **§A 정합성**: 종합계획서 부록 §A.2의 FIMRequest 스키마와 1:1 대응. 필드명, 타입, 기본값 모두 일치 확인 완료.

### 1.2 확장 FIM 요청 (FIMRequestExtended)

```python
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

class FIMMode(Enum):
    INLINE = "inline"          # 인라인 자동완성 (기본)
    BLOCK = "block"            # 블록 수준 완성
    MULTILINE = "multiline"    # 다중행 완성

@dataclass
class FIMRequestExtended:
    """확장 FIM 요청 — 운영 파라미터 포함"""
    # 핵심 FIM 파라미터 (§A.2 대응)
    prefix: str                             # 커서 앞 코드 (최대 4096 토큰)
    suffix: str                             # 커서 뒤 코드 (최대 2048 토큰)
    language: str                           # 프로그래밍 언어
    file_path: str                          # 파일 경로
    max_tokens: int = 128                   # 생성 최대 토큰
    temperature: float = 0.0                # 결정론적 생성
    stop_sequences: list[str] = field(default_factory=list)

    # 확장 파라미터
    mode: FIMMode = FIMMode.INLINE
    num_candidates: int = 3                 # 다중 제안 후보 수 (3~5개)
    debounce_ms: int = 150                  # LOCK-DT-07: 디바운스 150ms
    timeout_ms: int = 500                   # 지연 예산 (기본 500ms)
    model_override: Optional[str] = None    # None이면 fallback chain 적용
    stream: bool = True                     # 스트리밍 모드 활성화
    context_window: int = 8192              # 컨텍스트 윈도우 크기
    trace_id: Optional[str] = None          # 추적 ID
    user_style_profile: Optional[str] = None  # 사용자 코딩 스타일 프로필 ID
```

### 1.3 Prefix/Suffix 분할 규칙

```
┌──────────────────────────────────────────────────────┐
│                     소스 파일 전체                       │
├──────────────┬──────────┬────────────────────────────┤
│   prefix     │ [cursor] │          suffix             │
│ (≤ 4096 tok) │          │       (≤ 2048 tok)         │
├──────────────┴──────────┴────────────────────────────┤
│                                                        │
│  분할 알고리즘:                                          │
│  1. 커서 위치에서 좌측으로 4096 토큰까지 수집             │
│  2. 커서 위치에서 우측으로 2048 토큰까지 수집             │
│  3. 토큰 초과 시 구문 경계(AST 노드 경계)에서 절단        │
│  4. prefix가 불완전한 구문으로 끝나면 최근 완전 구문까지   │
│     백트래킹                                            │
│  5. suffix가 불완전한 구문으로 시작하면 다음 완전 구문까지 │
│     포워딩                                              │
└──────────────────────────────────────────────────────┘
```

**토큰 제한 정책** (FR-5 대응):

| 영역 | 최대 토큰 | 초과 시 전략 |
|------|----------|-------------|
| prefix | 4096 | AST 노드 경계에서 절단, 가장 오래된 코드부터 제거 |
| suffix | 2048 | AST 노드 경계에서 절단, 파일 끝 방향부터 제거 |
| 생성 | 128 (기본) | stop_sequences 또는 max_tokens에서 종료 |
| 전체 컨텍스트 | 8192 | prefix + suffix + 프롬프트 오버헤드 합계 제한 |

---

## D2. Output Schema

### 2.1 FIM 응답 (FIMResponse)

```typescript
interface FIMResponse {
  completion: string;     // 생성된 코드 텍스트
  confidence: number;     // 0.0 ~ 1.0 신뢰도 점수
  tokens_used: number;    // 사용된 토큰 수
  latency_ms: number;     // 응답 지연 (밀리초)
  alternatives: Array<{   // 대안 제안 목록
    text: string;
    score: number;        // 랭킹 점수
  }>;
}
```

> **§A 정합성**: 종합계획서 부록 §A.2의 FIMResponse 스키마와 1:1 대응. 필드명, 타입 모두 일치 확인 완료.

### 2.2 확장 응답 (FIMResponseExtended)

```python
@dataclass
class FIMCandidate:
    """개별 자동완성 후보"""
    text: str
    score: float                  # 랭킹 점수 (0.0 ~ 1.0)
    model_confidence: float       # 모델 신뢰도
    model_used: str               # 실제 사용된 모델명
    tokens_generated: int         # 생성된 토큰 수
    cache_hit: bool = False       # prefix cache 히트 여부

@dataclass
class FIMResponseExtended:
    """확장 FIM 응답"""
    completion: str               # 최고 점수 후보 텍스트
    confidence: float             # 최고 점수 후보 신뢰도
    tokens_used: int              # 전체 사용 토큰
    latency_ms: float             # 전체 지연 (밀리초)
    alternatives: list[FIMCandidate]  # 랭킹된 후보 목록
    model_used: str               # 최종 사용 모델
    fallback_triggered: bool      # fallback 발생 여부
    fallback_reason: Optional[str] = None  # fallback 사유
    cache_hit: bool = False       # KV-cache 재활용 여부
    stream_chunks: Optional[list[str]] = None  # 스트리밍 청크 (스트리밍 모드)
    trace_id: Optional[str] = None
```

### 2.3 스트리밍 응답

```python
@dataclass
class FIMStreamChunk:
    """스트리밍 모드 개별 청크"""
    delta: str                    # 증분 텍스트
    cumulative: str               # 누적 텍스트
    is_final: bool = False        # 최종 청크 여부
    confidence: Optional[float] = None  # 최종 청크에만 포함
    latency_ms: float = 0.0
```

---

## D3. Algorithm

### 3.1 FIM 코드 완성 파이프라인

```python
async def fim_complete(request: FIMRequestExtended) -> FIMResponseExtended:
    """
    FIM 코드 완성 메인 파이프라인
    Big-O: O(P + S + G) where P=prefix 토큰, S=suffix 토큰, G=생성 토큰
    """
    # 1. 디바운스 확인 — LOCK-DT-07: 150ms
    if not await debounce_check(request.trace_id, request.debounce_ms):
        raise CancelledError("debounce: 이전 요청 진행 중")

    # 2. Prefix/Suffix 분할 및 토큰화
    prefix_tokens = tokenize_with_boundary(request.prefix, max_tokens=4096)
    suffix_tokens = tokenize_with_boundary(request.suffix, max_tokens=2048)

    # 3. 컨텍스트 구성
    context = build_fim_context(prefix_tokens, suffix_tokens, request)

    # 4. 모델 선택 — LOCK-DT-04 fallback chain
    model = select_model(request, context)

    # 5. 추론 실행
    candidates = await run_inference(model, context, request.num_candidates)

    # 6. 랭킹 (→ ranking_algorithm.md 참조)
    ranked = rank_completions(candidates, context)

    # 7. 응답 구성
    return build_response(ranked, model)
```

### 3.2 모델 선택 알고리즘 (LOCK-DT-04 fallback chain)

```python
async def select_model(request: FIMRequestExtended, context: FIMContext) -> ModelEndpoint:
    """
    LOCK-DT-04: FIM 모델 fallback chain
    ┌─────────────────────────────────────────────────────────────┐
    │ 1차: Qwen 2.5 Coder 32B (fp16) — 복잡도 ≥ 0.7 또는 기본    │
    │ 2차: Qwen 2.5 Coder 7B (q4)   — 복잡도 < 0.3 & 지연 < 500ms│
    │ 3차: gpt-4o (API)              — 자체 모델 장애 시           │
    │ 4차: claude-sonnet (API)       — 전체 fallback              │
    └─────────────────────────────────────────────────────────────┘
    이 fallback chain 순서 변경 시 A/B 테스트 필수 (R-10-4).

    Big-O: O(1) — 모델 헬스 체크는 캐시된 상태 사용
    """
    complexity = estimate_complexity(context)

    FALLBACK_CHAIN = [
        ModelEndpoint("qwen-2.5-coder-32b-fp16", "local",
                      condition=lambda c: c >= 0.7 or True),  # 기본 선택
        ModelEndpoint("qwen-2.5-coder-7b-q4", "ollama",
                      condition=lambda c: c < 0.3),           # 경량 요청
        ModelEndpoint("gpt-4o", "api",
                      condition=lambda c: True),               # 장애 시 API
        ModelEndpoint("claude-sonnet", "api",
                      condition=lambda c: True),               # 전체 fallback
    ]

    if request.model_override:
        return resolve_model(request.model_override)

    # 우선순위: 복잡도 < 0.3이면 7B 먼저 시도, 그 외 32B 먼저
    if complexity < 0.3 and request.timeout_ms < 500:
        order = [FALLBACK_CHAIN[1], FALLBACK_CHAIN[0],
                 FALLBACK_CHAIN[2], FALLBACK_CHAIN[3]]
    else:
        order = FALLBACK_CHAIN

    for model in order:
        if model.condition(complexity) and await model.health_check():
            return model

    raise AllModelsUnavailableError("모든 FIM 모델 사용 불가")
```

### 3.3 디바운스 메커니즘 (LOCK-DT-07)

```python
class DebounceManager:
    """
    LOCK-DT-07: 자동완성 디바운스 150ms
    사용자 타이핑 중 연속 요청 억제.

    Big-O: O(1) per check
    """
    def __init__(self, default_ms: int = 150):
        self.default_ms = default_ms  # LOCK-DT-07: 150ms 고정
        self._pending: dict[str, asyncio.Task] = {}

    async def debounce(self, key: str, delay_ms: Optional[int] = None) -> bool:
        delay = delay_ms or self.default_ms
        # 기존 대기 중인 요청 취소
        if key in self._pending:
            self._pending[key].cancel()

        try:
            self._pending[key] = asyncio.current_task()
            await asyncio.sleep(delay / 1000.0)
            del self._pending[key]
            return True  # 디바운스 통과
        except asyncio.CancelledError:
            return False  # 새 요청에 의해 취소됨
```

### 3.4 Prefix/Suffix 토큰화 및 경계 절단

```python
def tokenize_with_boundary(text: str, max_tokens: int) -> list[Token]:
    """
    AST 노드 경계를 존중하는 토큰화.
    Big-O: O(T) where T = len(text)
    """
    tokens = tokenizer.encode(text)
    if len(tokens) <= max_tokens:
        return tokens

    # AST 파싱으로 구문 경계 탐색
    ast = tree_sitter_parse(text)
    boundaries = extract_statement_boundaries(ast)

    # max_tokens 이내의 가장 가까운 구문 경계에서 절단
    truncated = tokens[:max_tokens]
    for boundary in reversed(boundaries):
        if boundary.token_offset <= max_tokens:
            truncated = tokens[:boundary.token_offset]
            break

    return truncated
```

### 3.5 스트리밍 추론

```python
async def stream_fim_inference(
    model: ModelEndpoint,
    context: FIMContext,
    on_chunk: Callable[[FIMStreamChunk], None]
) -> FIMResponseExtended:
    """
    스트리밍 모드 FIM 추론.
    지연 예산: 첫 토큰 < 100ms (speculative decoding 활용).
    Big-O: O(G) where G = 생성 토큰 수
    """
    cumulative = ""
    start_time = time.monotonic_ns()

    async for token in model.stream_generate(context):
        cumulative += token
        chunk = FIMStreamChunk(
            delta=token,
            cumulative=cumulative,
            is_final=False,
            latency_ms=(time.monotonic_ns() - start_time) / 1e6
        )
        on_chunk(chunk)

    # 최종 청크
    final_chunk = FIMStreamChunk(
        delta="",
        cumulative=cumulative,
        is_final=True,
        confidence=compute_confidence(cumulative, context),
        latency_ms=(time.monotonic_ns() - start_time) / 1e6
    )
    on_chunk(final_chunk)

    return build_stream_response(cumulative, final_chunk)
```

---

## D4. Error Handling

### 4.1 에러 코드 체계

| 에러 코드 | 이름 | 설명 | 복구 전략 |
|-----------|------|------|----------|
| FIM-001 | MODEL_UNAVAILABLE | 선택된 모델 응답 없음 | fallback chain 다음 모델로 전환 |
| FIM-002 | TIMEOUT | 지연 예산 초과 | 현재 모델 취소, 다음 fallback 시도 |
| FIM-003 | TOKEN_LIMIT_EXCEEDED | prefix/suffix 토큰 초과 | AST 경계 기반 자동 절단 |
| FIM-004 | DEBOUNCE_CANCELLED | 디바운스에 의해 취소 | 무시 (정상 동작) |
| FIM-005 | CONTEXT_PARSE_FAILURE | AST 파싱 실패 | 순수 토큰 기반 절단으로 degradation |
| FIM-006 | RATE_LIMITED | API 레이트 리밋 도달 | 로컬 모델 전환 + 지수 백오프 |
| FIM-007 | STREAM_INTERRUPTED | 스트리밍 중 연결 끊김 | 부분 결과 반환 + 재시도 옵션 |
| FIM-008 | ALL_MODELS_DOWN | 전체 fallback chain 실패 | 사용자에게 오류 표시 + 에스컬레이션 |

### 4.2 Phase별 복구 전략

```
Phase 0 (초기화):
  - 모델 로드 실패 → 재시도 3회 → DEGRADED 모드(캐시된 제안만)

Phase 1 (요청 처리):
  - 디바운스 취소 → 정상 흐름 (무시)
  - 토큰 초과 → 자동 절단 → 경고 로그

Phase 2 (추론):
  - 모델 타임아웃 → fallback chain 다음 모델
  - 전체 모델 실패 → ALL_MODELS_DOWN 에스컬레이션

Phase 3 (후처리):
  - 랭킹 실패 → 모델 confidence 기반 정렬 fallback
  - 스트리밍 중단 → 부분 결과 반환
```

### 4.3 예외 처리 정책 표

| 계층 | 예외 유형 | 처리 방식 | 에스컬레이션 조건 |
|------|----------|----------|-----------------|
| Transport | 네트워크 타임아웃 | 재시도 2회 + fallback | 3회 연속 실패 |
| Model | 추론 오류 | fallback chain 전환 | 전체 chain 소진 |
| Parser | AST 파싱 실패 | graceful degradation | N/A |
| Ranking | 스코어링 오류 | confidence 기반 fallback | N/A |
| System | OOM / 디스크 부족 | 즉시 에스컬레이션 | 항상 |

### 4.4 EscalationPayload

```json
{
  "type": "FIM_ESCALATION",
  "severity": "CRITICAL",
  "source": "fim_protocol",
  "timestamp": "2026-04-10T09:54:00Z",
  "error_code": "FIM-008",
  "context": {
    "fallback_chain_exhausted": true,
    "models_attempted": ["qwen-2.5-coder-32b", "qwen-2.5-coder-7b", "gpt-4o", "claude-sonnet"],
    "last_error": "Connection refused on all endpoints",
    "request_trace_id": "tr-abc123",
    "user_impact": "자동완성 기능 전체 불가"
  },
  "recommended_action": "모델 서비스 상태 확인 및 수동 복구",
  "escalation_target": "ops-team"
}
```

---

## D5. Dependencies

### 5.1 외부 의존성

| 의존성 | 버전 | 용도 | 필수 여부 |
|--------|------|------|----------|
| tree-sitter | ≥ 0.20 | AST 기반 prefix/suffix 경계 탐색 | 권장 (없으면 토큰 기반 절단) |
| ollama | ≥ 0.1.7 | Qwen 2.5 Coder 로컬 추론 | 필수 (로컬 모드) |
| tiktoken | ≥ 0.5 | 토큰 카운팅 | 필수 |
| httpx | ≥ 0.24 | API 모델 호출 (gpt-4o, claude-sonnet) | 필수 (API 모드) |
| onnxruntime | ≥ 1.16 | 경량 모델 추론 가속 | 선택 |

### 5.2 내부 의존성 (세션간 인터페이스)

| 모듈 | 제공 인터페이스 | 소비 측 |
|------|---------------|--------|
| ranking_algorithm.md | `rank_completions(candidates, ctx)` | fim_protocol (D3.1 파이프라인 6단계) |
| local_model_setup.md | `OllamaModelManager.ensure_ready()` | fim_protocol (모델 헬스 체크) |
| 01_coding-engine/dev_node_architecture.md | `CodeGenerationRequest` | fim_protocol (컨텍스트 공유) |

### 5.3 의존성 그래프

```
fim_protocol.md
├── ranking_algorithm.md      (제안 랭킹)
├── local_model_setup.md      (Ollama 모델 관리)
├── 01_coding-engine/
│   └── dev_node_architecture.md  (코딩 엔진 코어)
├── [ext] ollama ≥ 0.1.7
├── [ext] tree-sitter ≥ 0.20
├── [ext] tiktoken ≥ 0.5
└── [ext] httpx ≥ 0.24
```

---

## D6. Performance

### 6.1 지연 예산 (FR-5 대응)

| 단계 | 목표 지연 | 최대 지연 | 비고 |
|------|----------|----------|------|
| 디바운스 대기 | 150ms | 150ms | LOCK-DT-07 고정 |
| 토큰화 + AST 파싱 | < 10ms | 20ms | Trie 기반 필터링 |
| Prefix cache 조회 | < 5ms | 10ms | KV-cache 재활용 |
| 모델 추론 (로컬) | < 80ms | 200ms | Speculative decoding |
| 모델 추론 (API) | < 300ms | 1000ms | 네트워크 지연 포함 |
| 랭킹 | < 5ms | 10ms | |
| **전체 (로컬)** | **< 100ms** | **250ms** | 디바운스 제외 |
| **전체 (API)** | **< 400ms** | **1200ms** | 디바운스 제외 |

### 6.2 성능 최적화 기법 (§A.4 대응)

| 기법 | 설명 | 목표 지연 | Big-O |
|------|------|----------|-------|
| Speculative decoding | Draft 모델 후보 생성 후 검증 | < 100ms | O(G) |
| Prefix caching | KV-cache 재활용으로 중복 연산 제거 | < 80ms | O(1) lookup |
| Trie-based filtering | 로컬 심볼 테이블 사전 필터링 | < 10ms | O(L) L=심볼길이 |
| Batched inference | 다중 요청 배치 처리 | < 200ms | O(B*G) B=배치크기 |
| ONNX Runtime | 경량 모델 로컬 추론 가속 | < 50ms | O(G) |

### 6.3 Big-O 요약

| 연산 | 시간 복잡도 | 공간 복잡도 |
|------|-----------|-----------|
| 토큰화 | O(T) T=텍스트 길이 | O(T) |
| AST 파싱 | O(T) | O(N) N=노드 수 |
| 모델 추론 | O(C+G) C=컨텍스트, G=생성 | O(C) KV-cache |
| 랭킹 | O(K log K) K=후보 수 | O(K) |
| 전체 파이프라인 | O(T + C + G + K log K) | O(C + K) |

---

## D7. Test Spec

### 7.1 단위 테스트

| TC-ID | 시나리오 | 입력 | 기대 결과 |
|-------|---------|------|----------|
| FIM-T01 | 기본 FIM 완성 | Python 함수 중간 코드 | 유효한 Python 코드 반환 |
| FIM-T02 | 빈 prefix | suffix만 제공 | 파일 시작부 코드 생성 |
| FIM-T03 | 빈 suffix | prefix만 제공 | 함수 끝까지 완성 |
| FIM-T04 | prefix 토큰 초과 | 5000 토큰 prefix | 4096 토큰으로 절단, AST 경계 존중 |
| FIM-T05 | 디바운스 취소 | 100ms 내 2회 요청 | 첫 번째 요청 취소, 두 번째만 처리 |
| FIM-T06 | fallback 전환 | 1차 모델 장애 | 2차 모델로 정상 응답 |
| FIM-T07 | 전체 fallback 소진 | 모든 모델 장애 | FIM-008 에러 + 에스컬레이션 |
| FIM-T08 | 스트리밍 모드 | stream=True | 청크 단위 응답, is_final 마킹 |
| FIM-T09 | 다중 언어 | TypeScript/Rust/Go | 언어별 올바른 구문 생성 |
| FIM-T10 | 레이트 리밋 | API 모델 60 req/min 초과 | 로컬 모델 전환 |
| FIM-T11 | prefix cache 히트 | 동일 파일 연속 요청 | cache_hit=True, 지연 감소 |
| FIM-T12 | 온도 0.0 (결정론적) | 동일 입력 3회 | 동일 출력 3회 |

### 7.2 통합 테스트

| TC-ID | 시나리오 | 검증 항목 |
|-------|---------|----------|
| FIM-IT01 | Ollama → FIM → 랭킹 → 응답 | 엔드투엔드 파이프라인 정상 동작 |
| FIM-IT02 | VS Code Extension → FIM API | InlineSuggestion 정상 렌더링 |
| FIM-IT03 | fallback chain 전체 순회 | 4단계 모델 순서 검증 |

### 7.3 Phase 2 테스트 케이스 (사전 정의)

| TC-ID | 시나리오 | 검증 항목 |
|-------|---------|----------|
| FIM-P2T01 | HumanEval+ 통과율 | ≥ 85% (Qwen 2.5 Coder 32B) |
| FIM-P2T02 | 수락률 A/B 테스트 | fallback chain 변경 시 수락률 비교 |
| FIM-P2T03 | 지연 P99 | 로컬 모델 < 200ms, API < 1200ms |
| FIM-P2T04 | 동시 요청 100건 | 배치 추론 안정성 |
| FIM-P2T05 | 사용자 스타일 학습 | 수락률 10% 향상 |
| FIM-P2T06 | 멀티바이트 문자 | 한국어/일본어/중국어 코멘트 포함 코드 |
| FIM-P2T07 | 대용량 파일 | 10,000행 파일 FIM 처리 |
| FIM-P2T08 | 오프라인 모드 | 네트워크 단절 시 로컬 전용 동작 |
| FIM-P2T09 | 메모리 사용량 | KV-cache + 모델 합산 ≤ 8GB |
| FIM-P2T10 | 보안: 프롬프트 인젝션 | 악의적 코드 주입 차단 |

---

## D8. Security

### 8.1 보안 고려사항

| 위협 | 설명 | 대응 |
|------|------|------|
| 프롬프트 인젝션 | prefix/suffix에 악의적 지시 삽입 | 입력 새니타이제이션 + 구조화된 FIM 포맷 사용 |
| 코드 유출 | 민감한 코드가 API 모델로 전송 | 로컬 모델 우선 정책 + 민감 파일 제외 규칙 |
| 시크릿 노출 | 생성 코드에 API 키/비밀번호 포함 | 생성 결과 시크릿 스캔 (정규식 + entropy 검사) |
| 모델 오남용 | 과도한 API 호출로 비용 폭증 | 레이트 리밋 (LOCK-DT-08: 분당 60 요청) |
| 캐시 오염 | 악의적 prefix cache 오염 | 캐시 키 해싱 + TTL 만료 + 무결성 검증 |

### 8.2 데이터 흐름 보안

```
사용자 코드 → [로컬 토큰화] → [AST 파싱] → [민감 정보 마스킹]
    │
    ├─ 로컬 모델: 데이터 외부 전송 없음 (Ollama)
    │
    └─ API 모델: TLS 1.3 암호화 전송
       ├─ 전송 전: .env, credentials 파일 자동 제외
       ├─ 전송 중: 종단 간 암호화
       └─ 전송 후: API 제공자 로그 보관 정책 확인 필수
```

---

## 로깅 중첩 JSON

```json
{
  "event": "fim_completion",
  "timestamp": "2026-04-10T09:54:00.000Z",
  "level": "INFO",
  "trace_id": "tr-abc123",
  "request": {
    "language": "python",
    "file_path": "src/main.py",
    "prefix_tokens": 2048,
    "suffix_tokens": 512,
    "max_tokens": 128,
    "mode": "inline",
    "debounce_ms": 150
  },
  "model_selection": {
    "complexity_score": 0.45,
    "selected_model": "qwen-2.5-coder-32b-fp16",
    "fallback_triggered": false,
    "health_check_ms": 2
  },
  "inference": {
    "model_used": "qwen-2.5-coder-32b-fp16",
    "tokens_generated": 42,
    "latency_ms": 67,
    "cache_hit": true,
    "candidates_count": 3
  },
  "ranking": {
    "top_score": 0.92,
    "algorithm": "weighted_multi_signal",
    "factors": {
      "model_confidence": 0.35,
      "type_match": 0.25,
      "recency": 0.20,
      "length_penalty": 0.10,
      "frequency": 0.10
    }
  },
  "response": {
    "completion_length": 42,
    "confidence": 0.92,
    "total_latency_ms": 85,
    "stream_mode": true
  }
}
```

---

## 통합 산출물 체크리스트

- [x] §A FIM 프로토콜 부록과 스키마 정합성 확인 (FIMRequest/FIMResponse 1:1 대응)
- [x] LOCK-DT-04 fallback chain 정확히 명시 (4단계: 32B → 7B → gpt-4o → claude-sonnet)
- [x] LOCK-DT-07 디바운스 150ms 명시 (D1.2, D3.3)
- [x] D1~D8 8차원 전수 작성 (P0 항목 L-002 기준)
- [x] FR-5 FIM 프로토콜 운영 상세 반영 (토큰 관리, 지연 예산, 신뢰도 스코어링)
- [x] 세션간 인터페이스: ranking_algorithm.md, local_model_setup.md 연동 명시
- [x] ABC 시그니처: S-DT-002-FIM

---

*Phase 1 P1-2 산출물 | L-002 FIM Protocol | ABC: S-DT-002-FIM*
