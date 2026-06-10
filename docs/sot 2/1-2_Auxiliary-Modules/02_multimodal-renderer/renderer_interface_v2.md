# I-13 Multimodal Renderer — 렌더러 인터페이스 V2 Enhanced (L3 보강)

> **V단계**: V2-Phase 2
> **Status**: APPROVED (Phase 4 ✅ 완료, 2026-05-23, V2 strict L3 PASS production-ready 정본 승급, Phase 3 V-17 PASS inheritance)
> **Last-reviewed**: 2026-05-23 (Phase 4 production promotion)
> **ReadOnly**: TRUE (production 승급 후 immutable, 변경 시 일시 해제→fix→복원 EXACT 패턴 + audit log)
> **작성일**: 2026-05-10
> **V1 정본**: `renderer_interface.md` (32 lines, Phase 1 완료, byte EXACT, read-only — E4 ABC 정본)
> **모듈**: I-13 Multimodal Output Renderer (CORE, Action 단계)
> **LOCK 참조**: LOCK-AX-01, LOCK-AX-11, LOCK-AX-12, LOCK-AX-13
> **L3 판정**: PASS (V-17 row content, 9/9 또는 8/9, 2026-05-14)
> **변경 이력 태그**: `V2-Phase 2` (2026-05-10, STAGE 9 1-2 STEP_B 세션 2-2, chain s9_36_a_2)
> **종합계획서 §**: §7 Phase 2 L1431~L1482 (2-2 I-13)
> **계약 cross-ref**: C-08 (I-5 → I-13: estimate_render_time/render/render_composite), C-09 (I-13 → I-20: RenderedOutput)
> **횡단**: 6-2 (렌더 결과 PII 마스킹 — L2 출력)

---

## 1. 교차 참조 블록

| 정본 | 역할 | 참조 지점 |
|------|------|----------|
| `AUXILIARY_MODULES_구조화_종합계획서.md` §7 Phase 2 (2-2 I-13) | V2 절차 | §3 |
| `AUTHORITY_CHAIN.md` §4 LOCK-AX-01/11/12/13 | LOCK 정본 | §2 |
| `renderer_interface.md` (V1, 32 lines, byte EXACT, **E4 ABC 정본**) | V1 정본 | §3 |
| `06_mapping/interface_contracts.md` v1.1 §4 C-08/C-09 | I-5→I-13, I-13→I-20 | §4.2 |
| `00_common/response_envelope.md` (LOCK-AX-11) | RenderedOutput → answer.details | §4.2 |
| `text_renderer_v2.md` ~ `composite_output_v2.md` ~ `quality_validation_v2.md` (자매 V2) | BaseRenderer 구현체 | §4.2 |
| `6-2/01_ai-code-security/pii_regex_masking.md` | L2 출력 PII | §4.3 |

---

## 2. LOCK 인용 (R9 형식)

> LOCK (D2.0-01 §5.6, LOCK-AX-01): I-13 = CORE, change_lock=false (V1:ON / V2:ON / V3:ON)

> LOCK (D2.0-02 §5.1.1, LOCK-AX-11): RenderedOutput → ResponseEnvelope `answer.details` 직렬화

> LOCK (D2.0-02 §2.1, LOCK-AX-12): I-13 = Action 단계 (Standard 5-stage)

> LOCK (D2.0-02 §2.2, LOCK-AX-13): S0~S8 운영 메타 채널 사용 (직접 매핑 없음)

---

## 3. V1 → V2 승급 개요

### 3.1 V1 정본 byte EXACT 보존
- V1: `renderer_interface.md` (32 lines, BaseRenderer ABC 정본)
- V1 §1 ABC 시그니처 (`render`, `supported_formats`, `estimate_render_time`) 보존 — **E4 정본**
- V1 변경 0

### 3.2 V2 보강 요소 (§13.1 L3 정의 + §7 Phase 2 2-2)

| 요소 | 보강 내용 | 위치 |
|------|----------|------|
| **E1** | BaseRenderer ABC의 목적 + 8 구현체 통일 인터페이스 | §4.1 |
| **E2** | render() 호출 흐름 의사코드 (timeout 적용, 에러 catch) | §4.2 |
| **E3** | Pydantic `RenderContent` / `RenderedOutput` 스키마 상세 | §4.2 |
| **E4** (보존) | V1 ABC 시그니처 byte EXACT | V1 §1 |
| **E5** | RenderTimeoutError, UnsupportedContentType, DAGCycleError | §4.3 |
| **E6** | render P95 / supported_formats(O(1)) / estimate(O(n)) | §4.4 |
| **E7** | 정상/timeout/미지원 포맷/PII 응답 5건 | §4.5 |
| **E9** | abc, pydantic, asyncio + composite_output 의존 | §4.6 |

---

## 4. V2 본문 (L3 보강)

### 4.1 E1 — 목적 및 역할

renderer_interface는 I-13 Multimodal Output Renderer의 **단일 진입 ABC**. 8개 구현체 (TextRenderer / ImageRenderer / AudioRenderer / ChartRenderer / DiagramRenderer / TableRenderer / CodeRenderer / CompositeOutput) 가 모두 `BaseRenderer` 를 상속하여 **통일된 호출 인터페이스** 를 제공한다.

해결 문제:
1. **호출자 단순화** — I-5 Decision Engine은 RenderType만 결정하고 구체 구현체는 모르고 호출.
2. **확장성** — 새 렌더러 (예: VideoRenderer V3) 추가 시 ABC 상속만으로 통합.
3. **사전 비용 추정** — `estimate_render_time()` 으로 I-5가 RenderPlan 결정 시 실행 시간/비용 사전 평가.

### 4.2 E2 + E3 — 의사코드 + Pydantic 스키마

**E3 입출력 모델**:
```python
class RenderContent(BaseModel):
    render_type: Literal["text", "image", "audio", "chart", "diagram", "table", "code", "composite"]
    payload: dict  # render_type별 페이로드 (각 v2 파일 §4.2 참조)
    locale: str = "ko-KR"
    accessibility: dict = {}  # alt_text, aria_label 등

class RenderedOutput(BaseModel):
    render_type: str
    artifact_url: Optional[str] = None  # CDN URL or null (inline 인 경우)
    artifact_inline: Optional[bytes] = None  # binary inline (≤1MB)
    mime_type: str
    bytes_size: int
    metadata: dict  # rendering_engine, duration_ms 등
    quality_check: dict  # quality_validation_v2.md §4.2 결과
```

**E2 호출 흐름**:
```python
class BaseRenderer(ABC):
    @abstractmethod
    async def render(self, content: RenderContent) -> RenderedOutput: ...

    @abstractmethod
    def supported_formats(self) -> list[str]: ...

    @abstractmethod
    def estimate_render_time(self, content: RenderContent) -> float:
        """Returns: estimated seconds (P95 기준)"""
        ...

# I-5 → I-13 호출 흐름 (C-08)
async def dispatch_render(plan: RenderPlan) -> RenderedOutput:
    renderer = registry[plan.render_type]
    estimated = renderer.estimate_render_time(plan.content)
    timeout_sec = _timeout_for(plan.render_type)  # timeout_policy §2 #11 (Rendering 단일/복합)
    if estimated > timeout_sec * 0.8:
        raise AuxError("AUX-E-RENDER-002", "estimate exceeds timeout budget")
    try:
        result = await asyncio.wait_for(renderer.render(plan.content), timeout=timeout_sec)
    except asyncio.TimeoutError:
        raise AuxError("AUX-E-RENDER-001", "render timeout")
    # 6-2 L2 출력 PII (text 채널)
    if plan.render_type == "text":
        masked, _ = pii_masker.apply_l2(result.artifact_inline.decode(), strategy="partial")
        result.artifact_inline = masked.encode()
    # quality_validation 호출 (quality_validation_v2.md §4.2)
    result.quality_check = await quality_validator.validate(result)
    return result
```

### 4.3 E5 — 에러 핸들링

| error_code | 설명 | recoverable | 처리 |
|-----------|------|:-----------:|------|
| `AUX-E-RENDER-001` | render timeout | YES | I-5 fallback render plan |
| `AUX-E-RENDER-002` | estimate exceeds timeout budget | YES | I-5에 downshift 요청 |
| `AUX-E-RENDER-003` | UnsupportedContentType | NO | I-5에 fallback render type 요청 |
| `AUX-E-RENDER-004` | DAGCycleError (composite) | NO | composite_output abort + 단일 fallback |
| `AUX-E-PII-002` | L2 출력 마스킹 실패 | NO | 차단 + 6-2 P1 |
| `AUX-E-QUAL-001` | quality_validation FAIL | YES | 재렌더 1회 또는 fallback |

### 4.4 E6 — 성능 벤치마크

| 메서드 | timeout_policy 호출 유형 | P95 | 비고 |
|--------|----------------------|:---:|------|
| `supported_formats()` | (인-프로세스) | 1 ms | static list |
| `estimate_render_time()` | (인-프로세스) | 5 ms | heuristic 계산 |
| `render()` (text) | Rendering 단일 (§2 #11) | 100 ms | CommonMark |
| `render()` (chart) | Rendering 단일 | 800 ms | Plotly + 데이터 |
| `render()` (composite) | Rendering 복합 (§2 #11) | 3000 ms | DAG 합성 |

### 4.5 E7 — 테스트 시나리오

| # | 시나리오 | 입력 | 예상 |
|---|---------|------|------|
| T-01 | 정상: text render | RenderContent(text, "# 헤딩") | RenderedOutput(text/html), quality_check=PASS |
| T-02 | 정상: composite | RenderContent(composite, [chart+table]) | DAG 병렬 → 레이아웃 합성 |
| T-03 | timeout | (인위 timeout) | AUX-E-RENDER-001 + I-5 fallback |
| T-04 | 미지원 포맷 | RenderContent(video) | AUX-E-RENDER-003 (V3 전까지) |
| T-05 | PII 응답 | text 본문에 이메일 포함 | L2 마스킹 적용 |
| T-06 | F-07 ABC 단위 테스트 | C-08/C-09 | ResponseEnvelope 5-key 정합 |
| T-07 | DAGCycleError | composite + 순환 의존 | AUX-E-RENDER-004 |

### 4.6 E9 — 의존성 명세

| 카테고리 | 의존성 | 용도 |
|---------|--------|------|
| 표준 라이브러리 | `abc`, `asyncio`, `typing` | ABC + 비동기 |
| 외부 라이브러리 | `pydantic` | 모델 검증 |
| 내부 모듈 | `00_common/response_envelope` (LOCK-AX-11), `00_common/error_taxonomy`, `00_common/timeout_policy` (§2 #11) | 공통 정본 |
| 내부 모듈 | `text/image/audio/chart/diagram/table/code/composite_output_v2` (구현체 8) | 구현체 |
| 내부 모듈 | `quality_validation_v2` | 품질 검증 |
| 횡단 도메인 | `6-2/01_ai-code-security/pii_regex_masking` | L2 출력 |

---

## 5. LOCK 교차 검증

| LOCK | AUTHORITY 값 | 본 V2 반영 | 일치 |
|------|------------|------------|:----:|
| LOCK-AX-01 | I-13 = CORE, change_lock=false | §2 + §4.1 | ✅ |
| LOCK-AX-11 (ResponseEnvelope) | answer.details 래핑 | §4.2 RenderedOutput → answer.details | ✅ |
| LOCK-AX-12 (Action) | I-13 ⊂ Action | §4.1 | ✅ |
| timeout_policy §2 #11 | Rendering 단일/복합 | §4.4 매핑 | ✅ |

---

## 6. V2 종결 marker

★ V2-Phase 2 작성 완료 (2026-05-10, 세션 2-2)
★ V1 byte EXACT (E4 ABC 정본 보존)
★ LOCK-AX-01/11/12/13 + timeout §2 #11 EXACT 인용
★ E1+E2+E3+E4(보존)+E5+E6+E7+E9 7요소 보강
★ interface_contracts C-08/C-09 baseline 인용
★ 6-2 PII (L2 출력) 명시
★ L3 판정: PENDING (2-7 일괄)
