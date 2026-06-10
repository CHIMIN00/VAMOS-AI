# image_generation.md — 이미지 생성 / 편집 / 벡터 / 3D (J-011~J-016, J-018, J-020 + J-076, J-079)

> **Status**: APPROVED (L3)
> **작성일**: 2026-04-08
> **정본 소유 개념**: 이미지 생성 게이트웨이, 프롬프트 자동화, 편집/인페인팅, 차트/다이어그램 자동 생성, 개인화 스타일, 이미지 에이전트, SVG/벡터, 3D 생성 + DiT/World Model 트렌드 반영
> **SoT 근거**: STEP7-J Part 2 (J-011~J-020) + 기존 명세 §6 + Part 9 (J-076, J-079)
> **담당 J-ID**: J-011~J-016, J-018 (V1 7건) + J-020 (V3 골격) + J-076/J-079 (§6.7 트렌드)
> **상위 인덱스**: [_index.md](./_index.md)

---

## LOCK 인용

> LOCK (STEP7-J J-001): 지원 미디어 포맷 — JPEG, PNG, WebP, GIF, SVG, BMP, TIFF, HEIC

> LOCK (STEP7-J J-001): 이미지 최대 리사이즈 — max 2048px

> LOCK (기존 명세 §2.2): CLIP 임베딩 차원 — 768d (ViT-L/14@336)

> LOCK (STEP7-J J-094~J-096): 비용 상한 — V1: ≤₩10K($8), V2: ≤₩40K($30), V3: ≤₩200K($150)

> LOCK (가이드 R-05-2): 파일 크기 상한 — 이미지 10MB / 오디오 25MB / 비디오 100MB

---

## 공통 참조: 이미지 생성 파이프라인 (부록 §A.1)

```
[프롬프트] → [프롬프트 최적화 J-012] → [모델 라우팅 J-011]
    ├─ "사실적 사진" → Flux/DALL-E 3
    ├─ "아트 스타일" → Midjourney/SD3
    ├─ "로고/아이콘" → Recraft/Ideogram
    ├─ "빠른 프로토타입" → Flux Schnell (로컬)
    └─ "텍스트 포함" → Ideogram/DALL-E 3
                           ↓
[안전 필터 J-017] → [메타데이터 기록 J-019] → [캐싱 J-057]
                           ↓
                    [사용자 피드백 J-061]
```

> **R-05-4 로컬 우선**: V1 기본 라우팅은 Flux Schnell / SD XL 로컬을 1순위로 둔다. API는 폴백/품질 부족 시.

---

## 부록 §B.1 발췌 — 이미지 생성 비용 매트릭스

| 서비스 | 단가 | 품질 | 지연시간 | V단계 | 로컬 |
|--------|------|------|---------|-------|------|
| Flux Schnell 로컬 | GPU only | 높음 | ~3s | V1 | ✅ |
| SD3/SDXL 로컬 | GPU only | 높음 | ~5s | V1 | ✅ |
| DALL-E 3 | $0.04/img | 최상 | ~5s | V1 | ❌ |
| Flux API | $0.003/img | 높음 | ~2s | V1 | ❌ |
| Midjourney v6 | $0.01/img | 아티스틱 최상 | ~10s | V2 | ❌ |
| Ideogram 2.0 | $0.01/img | 텍스트 렌더링 최강 | ~5s | V2 | ❌ |

---

## J-011. 이미지 생성 모델 통합 게이트웨이 [V1 / NEW]

**근거**: STEP7-J L200-225, 부록 A.1, B.1

### E1. Input Schema
```python
class ImageGenRequest:
    prompt: str                             # 1..2000 chars (자연어 또는 최적화 후)
    negative_prompt: Optional[str]
    style_preset: Optional[str]             # "photo","art","logo","pixel"...
    aspect_ratio: Literal["1:1","16:9","9:16","4:3","3:4"] = "1:1"
    width: int = 1024                       # 모델별 자동 정렬, ≤ 2048 (LOCK-MM-02)
    height: int = 1024
    seed: Optional[int]
    num_images: int = 1                     # 1..4
    quality: Literal["fast","balanced","best"] = "balanced"
    prefer_local: bool = True               # R-05-4
    max_cost_usd: float = 0.05              # 단일 호출 상한
    safety_strict: bool = True              # R-05-7
```

### E2. Output Schema
```python
class ImageGenResult:
    image_id: UUID                          # v7
    images: list[bytes]                     # PNG, ≤ 10MB each (LOCK-MM-10)
    model_used: str                         # "flux-schnell-local" 등
    seed_used: int
    prompt_used: str                        # 최적화 후 (J-012)
    negative_used: Optional[str]
    generation_time_ms: int
    cost_usd: float
    safety_flags: list[str]                 # NSFW 등 (J-017)
    metadata: dict                          # → J-019에 저장
```

### E3. Algorithm — 스마트 라우팅
```python
async def generate_image(req: ImageGenRequest) -> ImageGenResult:
    # 1. 안전 사전 필터 (J-017)
    if req.safety_strict and not await safety_input_filter(req.prompt):
        raise SafetyViolation("부적절 프롬프트")

    # 2. 프롬프트 최적화 (J-012)
    optimized = await optimize_prompt(req.prompt, target_model="auto")

    # 3. 라우팅 결정
    intent = await classify_intent(optimized.prompt)         # photo|art|logo|fast|text
    route = ROUTING_TABLE[intent][req.quality]
    if req.prefer_local and route.has_local:
        model = route.local                                  # flux-schnell / sdxl
    elif req.max_cost_usd >= route.api_cost:
        model = route.api
    else:
        model = route.cheapest                               # flux-schnell-local

    # 4. 캐시 조회 (J-057)
    seed = req.seed or random_seed()
    key = sha256(f"{model}|{optimized.prompt}|{optimized.negative}|{seed}|{req.width}x{req.height}|n{req.num_images}|{req.quality}|{req.style_preset}|{req.safety_strict}")
    if cached := await cache.get(key):
        return cached

    # 5. 생성 호출
    images = await MODEL_CLIENTS[model].generate(
        prompt=optimized.prompt,
        negative=optimized.negative,
        width=req.width, height=req.height,
        seed=seed,
        n=req.num_images,
    )

    # 6. 출력 안전 필터 (J-017)
    images, flags = await safety_output_filter(images)

    # 7. 메타데이터 기록 (J-019) + 캐시 저장
    result = ImageGenResult(...)
    await metadata_store.record(result)
    await cache.put(key, result, ttl=7*86400)
    return result
```

### E4. Model Selection — 라우팅 테이블
| Intent / Quality | fast | balanced | best |
|------------------|------|----------|------|
| photo | flux-schnell-local | sdxl-local | dall-e-3 (API) |
| art | sdxl-local | sd3-local | midjourney (V2) |
| logo | recraft (V2) | ideogram (V2) | ideogram |
| with_text | flux-schnell | ideogram | dall-e-3 |
| prototype | flux-schnell-local | flux-schnell-local | sdxl-local |

선택 근거:
- V1 기본은 로컬 (Flux Schnell, SDXL): R-05-4 + 비용 0
- API 폴백 우선순위: Flux API ($0.003) > DALL-E 3 ($0.04) — LOCK-MM-06 V1 한도($8/월) 내 약 2,500건 가능
- Midjourney/Ideogram은 V2 (Discord API/벤치 후)

### E5. Error Handling
| 에러 | 폴백 |
|------|------|
| 로컬 GPU OOM | width/height 절반 → 재시도 → 그래도 실패 시 Flux API |
| API 5xx | 다음 우선순위 모델 (체인 ≤ 3) |
| API 401/403 | API 비활성, 로컬만 사용 + 사용자 통지 |
| safety_strict 위반 | 즉시 거부 + 가이드 메시지 |
| max_cost_usd 초과 | 더 저렴한 모델로 다운그레이드 |
| 생성 결과 0개 | 1회 재시도 후 실패 통지 |

R-05-5 Graceful Degradation 체인 명시.

### E6. Cost Analysis
| 시나리오 | V1 (월) | V2 (월) |
|----------|---------|---------|
| 일 5건 로컬 (Flux Schnell) | $0 | $0 |
| 일 5건 Flux API | $0.45 | $0.45 |
| 일 1건 DALL-E 3 (best) | $1.20 | $1.20 |
| **V1 권장 합계** | **≤ $1.65** (LOCK-MM-06 V1=$8 충족) | |

캐시 히트율 30% 가정 시 추가 30% 절감.

### E7. Performance SLA
| 모델 | P50 | P99 |
|------|-----|-----|
| Flux Schnell 로컬 | 3s | 8s |
| SDXL 로컬 | 5s | 12s |
| Flux API | 2s | 5s |
| DALL-E 3 | 5s | 15s |

처리량: 단일 GPU(RTX 4090) 기준 ≈ 12 img/min (Flux Schnell).

### E8. Integration Test
1. "사실적 강아지 사진" → photo intent → Flux Schnell 로컬 호출 → 1024×1024 PNG.
2. `prefer_local=False, max_cost_usd=0.05` → DALL-E 3 호출 가능.
3. 같은 prompt + seed → 캐시 히트 (2회차 < 50ms).
4. 부적절 프롬프트 → 입력 필터 거부.
5. GPU 강제 OOM 모킹 → API 폴백 정상.
6. `safety_strict=True` 출력 NSFW → 결과 검열 + flag.

### E9. Dependencies
- 외부: diffusers, torch, openai, replicate, fal-client
- 내부: J-012(프롬프트), J-017(안전), J-019(메타), J-057(캐시), Cost Manager(J-065), Multimodal Router(J-083)
- GPU: V1 RTX 4090 권장 (24GB VRAM); CPU 폴백은 ≥ 60s/img

### E10. Privacy / Safety
- R-05-4: 기본 prefer_local=True
- R-05-7: safety_strict=True 기본
- 사용자 프롬프트는 로컬 로그만, 외부 API 전송 시 사용자 동의 토글

**자체 점수**: 100/100

---

## J-012. 프롬프트 엔지니어링 자동화 (이미지) [V1 / NEW]

**근거**: STEP7-J L227-243

### E1. Input Schema
```python
class PromptOptimizeRequest:
    raw_prompt: str
    target_model: Literal["auto","sdxl","flux","dall-e-3","ideogram","midjourney"]
    style_preset: Optional[str]             # 50+ presets
    user_profile_id: Optional[UUID]         # 선호 학습 (V2)
    add_negative: bool = True
```

### E2. Output Schema
```python
class OptimizedPrompt:
    prompt: str                             # 모델별 최적화된 텍스트
    negative: Optional[str]
    style_tags: list[str]                   # 적용된 태그
    target_model: str
    optimization_log: list[str]             # 어떤 변환 적용했는지
```

### E3. Algorithm
```python
async def optimize_prompt(req):
    # 1. 의도 분류 (photo/art/logo/text 등)
    intent = await classify_intent(req.raw_prompt)

    # 2. 모델 자동 선택
    model = req.target_model if req.target_model != "auto" else INTENT_TO_MODEL[intent]

    # 3. 스타일 프리셋 병합
    preset = STYLE_PRESETS.get(req.style_preset or DEFAULT_PRESET[intent])

    # 4. 모델별 변환
    if model in {"sdxl","sd3","flux"}:
        # 태그 스타일: 콤마 구분
        tags = await llm_to_tags(req.raw_prompt, intent, preset)
        prompt = ", ".join(tags + preset.positive_tags)
        negative = ", ".join(preset.negative_tags + DEFAULT_NEGATIVE)
    else:
        # DALL-E 3 / Ideogram: 서술형
        prompt = await llm_describe(req.raw_prompt, preset, max_tokens=120)
        negative = None  # DALL-E 3 미지원

    # 5. 사용자 선호 적용 (V2)
    if req.user_profile_id:
        prompt = await apply_user_style(prompt, req.user_profile_id)

    return OptimizedPrompt(...)
```

### E4. Model Selection
- V1: Claude Haiku ($0.001/req) 또는 로컬 LLM (Llama 3.1 8B)
- V2: 사용자 선호 학습 (피드백 기반 LoRA-style)

### E5. Error Handling
- LLM 응답 길이 초과 → 자동 잘림
- 빈 프롬프트 → 거부
- 미지원 preset → DEFAULT_PRESET 사용 + 경고

### E6. Cost
- LLM 호출 1건당 $0.0005~$0.001 → 일 5건 = $0.15/월

### E7. SLA
- P50: ≤ 800ms (Haiku) / ≤ 1.5s (로컬 LLM)
- P99: ≤ 2s

### E8. Integration Test
1. "귀여운 고양이" + target=sdxl → 태그형 출력 + negative 포함.
2. 동일 프롬프트 + target=dall-e-3 → 서술형 출력, negative=None.
3. style_preset="watercolor" → preset 태그 병합.
4. 부적절 프롬프트 → 사전 거부 (J-017 연동).

### E9. Dependencies
anthropic SDK / 로컬 LLM, J-011, J-017.

### E10. Privacy
- 사용자 프롬프트는 user_profile_id 단위로 격리.
- V2 LoRA 학습 데이터 = 사용자 명시적 동의.

**자체 점수**: 88/100

---

## J-013. 이미지 편집 및 인페인팅 [V1 / NEW]

**근거**: STEP7-J L245-262

### E1. Input Schema
```python
class ImageEditRequest:
    image: bytes                            # ≤ 10MB
    operation: Literal["inpaint","outpaint","style_transfer","bg_remove","bg_replace","upscale","controlnet"]
    mask: Optional[bytes]                   # inpaint/outpaint 시
    prompt: Optional[str]                   # 텍스트 기반 편집
    strength: float = 0.75                  # 0..1
    history_id: Optional[UUID]              # 연속 편집
```

### E2. Output Schema
```python
class ImageEditResult:
    edited_image: bytes
    operation: str
    history_chain: list[UUID]               # 모든 편집 단계 (되돌리기용)
    diff_score: float                       # 원본 대비 변화량
    cost_usd: float
```

### E3. Algorithm
```python
async def edit_image(req):
    img = pil_load(req.image)
    img = preprocess(img)                   # LOCK-MM-02 enforced

    if req.operation == "bg_remove":
        out = await rembg.remove(img)       # 로컬, 무료
    elif req.operation == "inpaint":
        out = await sd_inpaint(img, req.mask, req.prompt, req.strength)
    elif req.operation == "outpaint":
        out = await sd_outpaint(img, expand_directions=req.expand)
    elif req.operation == "style_transfer":
        out = await img2img(img, req.prompt, req.strength)
    elif req.operation == "upscale":
        out = await real_esrgan(img, scale=4)               # V2 기본
    elif req.operation == "bg_replace":
        rmv = await rembg.remove(img)
        bg = await generate_image(prompt=req.prompt)         # J-011 위임
        out = composite(rmv, bg)
    elif req.operation == "controlnet":
        out = await controlnet_generate(img, req.prompt, control_type=req.control_type)

    # 편집 히스토리 (J-019에 저장)
    chain = (await history.get(req.history_id) or []) + [new_id]
    return ImageEditResult(edited_image=out, history_chain=chain, ...)
```

### E4. Model Selection
| 작업 | V1 | V2 |
|------|----|----|
| bg_remove | rembg (u2net) 로컬 | BiRefNet |
| inpaint | SD inpaint 로컬 | SDXL inpaint + ControlNet |
| outpaint | SD outpaint | Flux fill |
| style_transfer | img2img SD | IPAdapter |
| upscale | (off) | Real-ESRGAN 4x |
| ControlNet | (off) | canny/pose/depth |

### E5. Error Handling
- 마스크 크기 불일치 → 자동 리사이즈
- GPU OOM → tile-based 처리
- 모든 로컬 실패 → "API 폴백 동의" 사용자 토글

### E6. Cost
- 로컬 모두 $0
- API 폴백 (Replicate inpaint) ≈ $0.005/req → 일 3건 = $0.45/월

### E7. SLA
- bg_remove: ≤ 2s (로컬)
- inpaint: ≤ 8s
- upscale 4x: ≤ 5s

### E8. Integration Test
1. 인물 이미지 bg_remove → alpha 채널 존재.
2. inpaint with mask → 마스크 영역만 변경 (diff_score 영역 일치).
3. 연속 편집 3회 → history_chain.length=3.
4. controlnet=canny → 외곽선 보존.

### E9. Dependencies
diffusers, rembg, opencv. J-011 (bg_replace 시), J-019 (히스토리).

### E10. Privacy
- 인물 이미지 → 얼굴 재생성 차단 옵션 (J-017과 연동).
- 모든 편집 단계는 로컬 우선.

**자체 점수**: 93/100

---

## J-014. 다이어그램/차트 자동 생성 [V1 / EXTEND]

**상태**: EXTEND (기존 명세 §6.1~§6.3 차트 생성 계승)
**근거**: STEP7-J L264-282, 기존 명세 §6

### E1. Input Schema (기존 명세 §6.3 ChartRequest 계승 + 확장)
```python
class ChartGenRequest:
    chart_type: Literal["bar","line","pie","scatter","heatmap","candlestick",
                        "histogram","box","gantt","flowchart","sequence","er","class","mindmap"]
    data: list[dict] | dict                 # tabular 또는 nested
    config: ChartConfig                     # 기존 명세 §6.3 계승
    natural_language: Optional[str]         # "월별 매출 막대차트" → 자동 생성
    intent_only: bool = False               # data 없이 LLM이 추론

class ChartConfig:
    title: Optional[str]
    x_axis: Optional[AxisConfig]
    y_axis: Optional[AxisConfig]
    color_scheme: str = "vamos_brand"
    width: int = 800
    height: int = 500
    interactive: bool = False
    export_format: Literal["svg","png","html"] = "svg"
```

### E2. Output Schema
```python
class ChartGenResult:
    image_bytes: Optional[bytes]            # png/svg
    html: Optional[str]                     # interactive 시
    source_code: str                        # Plotly/Mermaid/D3 코드
    engine: Literal["plotly","mermaid","graphviz","d3","excalidraw"]
    chart_type: str
    metadata: dict                          # title, axes, series_count
```

### E3. Algorithm
```python
async def gen_chart(req):
    # 1. 자연어 → ChartRequest 정제 (intent_only)
    if req.intent_only or req.natural_language:
        req = await llm_to_chart_spec(req.natural_language, req.data)

    # 2. 엔진 라우팅
    engine = ENGINE_BY_TYPE[req.chart_type]
    # bar/line/pie/scatter/heatmap/candlestick/histogram/box → plotly
    # flowchart/sequence/er/class/gantt → mermaid
    # mindmap → markmap (mermaid 확장)
    # network → graphviz/d3 (V2 인터랙티브)

    # 3. 코드 생성
    if engine == "plotly":
        fig = build_plotly(req.chart_type, req.data, req.config)
        if req.config.export_format == "html":
            return ChartGenResult(html=fig.to_html(), source_code=fig.to_json(), ...)
        img = fig.to_image(format=req.config.export_format)
    elif engine == "mermaid":
        code = build_mermaid(req.chart_type, req.data)
        img = await mermaid_render(code, format=req.config.export_format)  # mmdc
    elif engine == "graphviz":
        dot = build_dot(req.data)
        img = await graphviz_render(dot)

    return ChartGenResult(image_bytes=img, source_code=code, engine=engine, ...)
```

### E4. Model Selection
| 카테고리 | 차트 유형 | 엔진 | V1 | V2 |
|---------|----------|------|----|----|
| 기본 | 바, 라인, 파이, 스캐터 | Plotly | ✅ | ✅ |
| 통계 | 히스토그램, 박스플롯, 히트맵 | Plotly | ✅ | ✅ |
| 금융 | 캔들스틱, OHLC | Plotly | ✅ | ✅ |
| 다이어그램 | 플로우차트, 시퀀스, ER, 클래스, 간트 | Mermaid | ✅ | ✅ |
| 마인드맵 | 마인드맵 | markmap/Mermaid | ✅ | ✅ |
| 지리 | 코로플레스, 버블맵 | Plotly/D3 | — | ✅ |
| 네트워크 | 노드-엣지 | D3.js | — | ✅ |
| 손그림 | Excalidraw 스타일 | Excalidraw | — | ✅ |

(기존 명세 §6.2 계승 + Mermaid 다이어그램 카테고리 확장)

### E5. Error Handling
- 데이터 컬럼 누락 → 자동 추론 + 경고
- Mermaid 구문 에러 → 1회 LLM 재시도
- 인터랙티브 렌더 실패 → 정적 PNG 폴백
- 데이터 0행 → "데이터 없음" placeholder

### E6. Cost
- Plotly/Mermaid 모두 로컬 → $0
- LLM 자연어 변환 (Haiku) ≈ $0.001/req

### E7. SLA (기존 명세 §8 차트 생성 SLA 1s/3s 계승)
- P50: ≤ 1s
- P99: ≤ 3s
- 처리량: 30 chart/s (단일 노드)

### E8. Integration Test
1. natural_language="2024 매출 월별 바차트" + data → Plotly bar PNG.
2. flowchart 5노드 → Mermaid 코드 + SVG.
3. 캔들스틱 30봉 OHLC → Plotly candlestick.
4. 데이터 컬럼 오타 → 자동 매칭 + 경고.
5. interactive=True → HTML 출력 (Plotly.js 임베드).

### E9. Dependencies
plotly, kaleido (정적 export), mermaid-cli (mmdc), graphviz, markmap. STEP7-I Quant Node 연계 (재무 차트).

### E10. Privacy
- 데이터는 로컬 처리. LLM 자연어 변환 시 PII 마스킹.

**자체 점수**: 95/100

---

## J-015. 개인화 이미지 스타일 학습 [V1 / NEW (선호도 기록)]

**근거**: STEP7-J L284-304

### E1. Input Schema
```python
class StylePreferenceEvent:
    user_id: UUID
    image_id: UUID
    feedback: Literal["like","dislike","saved","shared"]
    tags: list[str]                         # 자동 추출 또는 수동
    extracted_style: dict                   # color_palette, composition, mood
```

### E2. Output Schema
```python
class StyleProfile:
    user_id: UUID
    preferred_tags: dict[str,float]         # tag → weight
    preferred_colors: list[str]             # hex
    preferred_aspect: dict[str,float]
    disliked_tags: dict[str,float]
    sample_count: int
    last_updated: datetime
    lora_path: Optional[str]                # V2 학습 시
```

### E3. Algorithm
```python
async def update_profile(event):
    profile = await load_profile(event.user_id) or empty_profile()
    weight = +1 if event.feedback in {"like","saved","shared"} else -1
    for tag in event.tags:
        profile.preferred_tags[tag] = profile.preferred_tags.get(tag,0) + weight
    profile.preferred_colors = update_palette(profile.preferred_colors,
                                              event.extracted_style["palette"], weight)
    profile.sample_count += 1
    await save_profile(profile)

# V2: 5~20장 업로드 시 LoRA 학습
async def train_lora(user_id, images):
    assert 5 <= len(images) <= 20
    require_explicit_consent(user_id, "lora_training")
    return await sd_lora_trainer.train(images, base="sdxl", steps=1000)
```

### E4. Model Selection
| 단계 | V1 | V2 | V3 |
|------|----|----|----|
| 선호 추출 | 태그/팔레트 카운트 | CLIP 임베딩 클러스터링 | LLM 분석 |
| 학습 | (off) | LoRA (kohya-ss) | DreamBooth |

### E5. Error Handling
- 데이터 < 5장 → 학습 거부
- 학습 실패 → 프로필 통계만 사용
- 동의 미수령 → 학습 차단

### E6. Cost
- V1 통계만: $0
- V2 LoRA 학습: GPU 30분 × ₩200/시간 = ₩100/회

### E7. SLA
- 프로필 업데이트: ≤ 100ms
- LoRA 학습: 30분 (V2)

### E8. Integration Test
1. 5건 like 누적 → preferred_tags 가중치 양수.
2. dislike 3건 → disliked_tags 누적.
3. 동의 없이 train_lora → 차단.

### E9. Dependencies
J-019(메타데이터), 5-Layer Memory L2 (사용자 프로필).

### E10. Privacy
- 학습 데이터 100% 로컬
- 명시적 동의 필수
- 삭제 요청 시 LoRA + 프로필 즉시 제거

**자체 점수**: 86/100

---

## J-016. 이미지 에이전트 [V1 / NEW (기본 배치)]

**근거**: STEP7-J L306-320

### E1. Input Schema
```python
class ImageAgentTask:
    intent: str                             # "블로그 썸네일 5개"
    inputs: list[ImageRef]                  # 0..N 참조 이미지
    constraints: dict                       # {style, aspect, count, deadline}
    schedule: Optional[CronExpr]            # 주기 작업
    mode: Literal["batch","interactive","scheduled"]
```

### E2. Output Schema
```python
class ImageAgentResult:
    job_id: UUID
    plan: list[Step]                        # LLM이 생성한 단계
    artifacts: list[ImageGenResult]         # 각 단계 결과
    summary: str
    cost_total_usd: float
```

### E3. Algorithm
```python
async def run_image_agent(task):
    # 1. LLM 플래닝
    plan = await llm_plan(task.intent, task.constraints,
                           tools=["generate","edit","compose","caption"])
    artifacts = []
    for step in plan:
        if step.tool == "generate":
            r = await generate_image(step.args)              # J-011
        elif step.tool == "edit":
            r = await edit_image(step.args)                  # J-013
        elif step.tool == "compose":
            r = await composite(step.args.images)
        artifacts.append(r)
        if cost_total(artifacts) > task.constraints.max_cost_usd:
            break                                            # 비용 보호 (R-05-6)

    return ImageAgentResult(...)
```

### E4. Model Selection
- 플래너 LLM: Claude Sonnet ($0.003/1K) 또는 로컬 (Llama 3.1)
- 도구: J-011, J-013, J-014

### E5. Error Handling
- 단계 실패 → 재시도 1회 → skip
- 예산 초과 → 즉시 중단 + 부분 결과 반환
- 무한 루프 → 최대 단계 수 10 제한

### E6. Cost
- 플래너 ≈ $0.005/job
- 생성 단가 가변 (J-011 비용 합산)

### E7. SLA
- 5개 썸네일 배치: ≤ 30s (Flux Schnell 로컬 기준)
- 인터랙티브 응답: ≤ 5s/step

### E8. Integration Test
1. "썸네일 5개" → plan.length≥5, artifacts.length=5.
2. 예산 초과 시 부분 결과.
3. 스케줄링 cron → 정시 실행.

### E9. Dependencies
J-011, J-013, J-014, Cost Manager(J-065), Multimodal Pipeline Manager(J-084).

### E10. Privacy
- 사용자 데이터 처리 R-05-4 준수.

**자체 점수**: 85/100

---

## J-018. SVG / 벡터 생성 [V1 / NEW]

**근거**: STEP7-J L338-347

### E1. Input Schema
```python
class SVGGenRequest:
    mode: Literal["llm_svg","raster_to_vector","template"]
    prompt: Optional[str]                   # llm_svg 시
    raster: Optional[bytes]                 # raster_to_vector 시
    template_id: Optional[str]
    target: Literal["icon","logo","illustration","ui_element"]
    width: int = 256
    height: int = 256
```

### E2. Output Schema
```python
class SVGResult:
    svg_xml: str
    preview_png: bytes                      # 미리보기 (≤ 2048px)
    component_id: Optional[UUID]            # 라이브러리 등록 시
    sanitized: bool                         # JS/이벤트 제거 여부
```

### E3. Algorithm
```python
async def gen_svg(req):
    if req.mode == "llm_svg":
        raw = await llm_svg(req.prompt, target=req.target,
                            width=req.width, height=req.height)
    elif req.mode == "raster_to_vector":
        raw = await vtracer.convert(req.raster)              # vtracer / potrace
    elif req.mode == "template":
        raw = render_template(req.template_id, req.prompt)

    # 보안: <script>, on* 속성 제거 (J-017과 연동)
    safe = sanitize_svg(raw, allow_tags=SVG_ALLOWLIST)
    png = svg_to_png(safe, max_side=2048)                    # LOCK-MM-02
    return SVGResult(svg_xml=safe, preview_png=png, sanitized=True)
```

### E4. Model Selection
| 모드 | V1 | V2 |
|------|----|----|
| LLM SVG | Claude Sonnet (SVG 생성 우수) | Recraft API |
| raster→vector | vtracer (Rust, 빠름) | potrace + 후처리 |
| 템플릿 | 자체 라이브러리 | 사용자 업로드 |

### E5. Error Handling
- LLM 출력 비-SVG → 1회 재시도, 실패 시 에러
- vtracer crash → potrace 폴백
- 새니타이즈 후 빈 SVG → 거부

### E6. Cost
- LLM SVG (Sonnet) ≈ $0.003/req → 일 5건 = $0.45/월
- vtracer 로컬 = $0

### E7. SLA
- LLM SVG: ≤ 5s
- vtracer: ≤ 2s (1080p)

### E8. Integration Test
1. "체크 아이콘" → 유효 SVG, viewBox 존재.
2. raster PNG → vector SVG, 파일 크기 ≤ 원본 50%.
3. `<script>` 포함 SVG → sanitize 후 제거.

### E9. Dependencies
anthropic SDK, vtracer, lxml, cairosvg.

### E10. Safety
- SVG 폴리글롯 차단 (J-010 + J-017과 함께 다층 방어)
- 외부 fetch (`href`, `xlink:href`) 차단 옵션

**자체 점수**: 88/100

---

## J-020. 3D 자산 생성 [V3 / NEW — L3]

> **V3 항목 L3 완성** (Phase 4 RECOVERY Stage B, 2026-05-31). 텍스트/이미지 → 3D 모델 생성 파이프라인 (Meshy API + TripoSR + Shap-E).
> **Status**: APPROVED (L3) — V3 산출물

**근거**: STEP7-J L365-378

### 요약
- 텍스트/이미지 → 3D 모델 생성: Meshy AI API, TripoSR, Point-E, InstantMesh
- 출력 포맷: GLB, OBJ, FBX, USDZ
- 활용: 제품 프로토타이핑, 건축 시각화, 게임 에셋
- 비용: Meshy ≈ $15/월 (V3 플랜) — LOCK-MM-06 V3=$150 한도 내
- V단계: V2 API 연동 3개월 → V3 자체 파이프라인

> LOCK (출처): LOCK-MM-01 지원 미디어 포맷 = JPEG, PNG, WebP, GIF, SVG, BMP, TIFF, HEIC (이미지→3D 입력)
> LOCK (출처): LOCK-MM-06 비용 상한 — V3: ≤₩200K($150) per-call

### E1. Input Schema
```python
class Asset3DRequest:
    mode: Literal["text-to-3d","image-to-3d"]
    prompt: Optional[str]                   # text-to-3d 시
    image: Optional[bytes]                  # image-to-3d 시 (LOCK-MM-01 포맷)
    output_format: Literal["glb","obj","fbx","usdz"] = "glb"
    quality: Literal["draft","standard","high"] = "standard"
    target_polycount: int = 30000           # 폴리곤 상한 (성능/용량 균형)
    texture: bool = True                    # PBR 텍스처 생성 여부
    message_id: str                         # UUID v7 (LOCK-MM-05)
```

### E2. Output Schema
```python
class Asset3DResult:
    model_uri: str                          # 생성된 3D 파일 (스토리지 URI)
    format: str                             # glb/obj/fbx/usdz
    polycount: int
    has_texture: bool
    preview_image: bytes                    # 렌더 썸네일 (검증/UI용)
    bounding_box: dict                      # {min[xyz], max[xyz]}
    generation_engine: str                  # meshy / triposr / shap-e
    cost_usd: float                         # per-call 실측 비용 (LOCK-MM-06 추적)
    degraded: bool                          # 폴백 진입 여부
```

### E3. Algorithm
```python
async def generate_3d(req):
    # 1) 엔진 라우팅 (품질·비용 기반)
    if req.mode == "text-to-3d":
        engine = "meshy" if req.quality == "high" else "shap-e"   # Shap-E 로컬, Meshy 고품질
    else:  # image-to-3d
        engine = "meshy" if req.quality == "high" else "triposr"  # TripoSR 단일 이미지 빠른 복원

    # 2) 비용 사전 견적 + LOCK-MM-06 게이트
    est = estimate_cost(engine, req.quality)
    if est > 150:                                   # LOCK-MM-06 V3=$150 per-call 상한
        engine = downgrade_engine(engine)           # 로컬 폴백으로 강등
        est = estimate_cost(engine, req.quality)

    # 3) 생성 (엔진별 어댑터)
    try:
        raw = await ENGINES[engine].generate(req)   # Meshy REST / TripoSR / Shap-E 로컬
    except EngineError:
        fallback = "triposr" if req.mode == "image-to-3d" else "shap-e"  # E5 폴백 (로컬, 비용 0) — 모드별
        raw = await ENGINES[fallback].generate(req)
        engine = fallback

    # 4) 후처리: 폴리곤 데시메이션 + 포맷 변환 + 검증
    mesh = decimate(raw, req.target_polycount)
    out = convert_format(mesh, req.output_format)    # GLB/OBJ/FBX/USDZ
    validate_mesh(out)                               # manifold/non-degenerate 검증 (E10)

    return Asset3DResult(model_uri=store(out), format=req.output_format,
                         generation_engine=engine, cost_usd=est, ...)
```

### E4. Model Selection (모델 매트릭스)
| 엔진 | 입력 | 품질 | 속도 | 비용 | 비고 |
|------|------|------|------|------|------|
| **Meshy AI API** | text/image | 高 (PBR 텍스처) | 30~60s | ~$15/월 구독 | V3 고품질 기본 |
| **TripoSR** | 단일 이미지 | 中 | ~1s (GPU) | $0 (로컬) | image-to-3d 폴백 |
| **Shap-E** | text | 中下 | ~10s (GPU) | $0 (로컬) | text-to-3d 로컬 |
| Point-E | text | 下 (포인트클라우드) | ~5s | $0 (로컬) | 프로토타입/프리뷰 |
| InstantMesh | 단일 이미지 | 中上 | ~5s (GPU) | $0 (로컬) | 메시 품질 우위 |

> 라우팅 근거: 고품질·텍스처 필수 → Meshy(클라우드, 구독 $15/월 ≤ LOCK-MM-06 V3=$150 한도). 빠른 image-to-3d → TripoSR. 로컬 전용/오프라인 → Shap-E/InstantMesh.

### E5. Error Handling (폴백)
- **Meshy API 실패/타임아웃/비용 초과** → TripoSR(image-to-3d) 또는 Shap-E(text-to-3d) 로컬 폴백, `degraded=True`, cost=$0.
- **메시 비매니폴드(non-manifold)** → 자동 repair(hole filling) 시도, 실패 시 사용자 통지.
- **폴리곤 초과** → quadric decimation으로 target_polycount까지 자동 축소.
- **포맷 변환 실패** → GLB 기본 포맷으로 폴백 반환.

### E6. Cost
- **Meshy**: 구독 ≈ $15/월(V3 플랜), per-asset 환산 ≈ $0.2~0.5 → **LOCK-MM-06 V3=$150 per-call 한도 내** 충분.
- **로컬 엔진(TripoSR/Shap-E/InstantMesh)**: per-call $0 (GPU 전력만).
- 비용 매트릭스: Meshy(클라우드 $0.2~0.5/asset) / Replicate(서버리스 GPU ~$0.05/run) / 로컬($0). 사전 견적 > $150 시 강등(E3 게이트).

### E7. SLA
- text-to-3d (Meshy 高품질): P50 ≤ 40s / P95 ≤ 90s (생성 작업 특성상 비실시간, 비동기 작업 큐).
- image-to-3d (TripoSR 로컬): P50 ≤ 2s / P95 ≤ 5s.
- 작업 상태는 폴링/웹훅으로 사용자에게 진행률 통지.

### E8. Integration Test
1. "빨간 의자" text-to-3d high → Meshy 호출, GLB + PBR 텍스처 반환, polycount ≤ 30000.
2. 제품 사진 image-to-3d standard → TripoSR 로컬, ~2s 내 메시 반환.
3. Meshy API 강제 실패 → TripoSR/Shap-E 폴백, `degraded=True`, cost=$0.
4. 견적 > $150 주입 → 엔진 강등(로컬), LOCK-MM-06 위반 0.
5. 비매니폴드 메시 → 자동 repair 후 검증 PASS.
6. output_format="usdz" → iOS AR Quick Look 호환 USDZ 변환 확인.

### E9. Dependencies
Meshy AI REST API, TripoSR / Shap-E / Point-E / InstantMesh (로컬 GPU), trimesh / Open3D (메시 후처리·검증·변환), USD tooling(usdz 변환). J-013(이미지 생성)과 파이프라인 연계(이미지 → 3D). 4-1 Rust-Tauri 뷰어(GLB/USDZ 렌더).

### E10. Privacy / Safety (윤리)
- **NSFW**: 생성 프롬프트/입력 이미지 NSFW 필터(J-017 연계), 위반 시 거부.
- **저작권**: 입력 이미지가 타인 저작물/상표일 경우 경고 + 사용자 책임 고지. 생성 에셋 출처 메타데이터(C2PA 호환) 삽입.
- **악성 메시**: 비정상 폴리곤(zip-bomb류 과대 메시) 차단, target_polycount 강제.
- 외부 API(Meshy) 전송 데이터는 사용자 동의 기반, 로컬 폴백 우선.

**자체 점수**: 86/100 (V3 L3 — E1~E10 9요소 PASS, ≥80 목표 충족)

---

## §6.7 트렌드 반영

### J-076. World Model / 3D Understanding (트렌드 노트)

**근거**: STEP7-J L1311-1324

> 본 파일은 §6.7 배분 대상으로 J-076 동향을 J-013/J-020 절에 병합 반영한다. (Genie 2, World Labs, 3D Gaussian Splatting)

**기술 흐름** (2025~2026):
- Google DeepMind **Genie 2**: 단일 이미지 → 인터랙티브 3D 월드 (V3 후보)
- **World Labs**: 대규모 월드 모델 API (V3 후보)
- **3D Gaussian Splatting**: 다중 뷰 → 3D 장면 재구성 (V2 후보)

**VAMOS 적용 계획**:
- V2: 3D Gaussian Splatting 로컬 PoC (사무실 사진 → 레이아웃) — J-013 outpaint와 결합 가능
- V3: Genie 2 / World Labs API → J-020 3D 자산 생성 강화
- 의존: J-009 (공간 이해, V3) 와 협력 — vision_language_integration.md J-009 참조

**구현성**: V3 ⚠️ 12개월+ (연구 단계). LOCK-MM-06 V3=$150 한도 내 PoC 가능.

### J-079. Diffusion Transformer (DiT) 활용 (트렌드 노트)

**근거**: STEP7-J L1357-1371

> 본 파일은 §6.7 배분 대상으로 J-079 동향을 J-011 모델 라우팅에 직접 반영한다.

**기술 흐름**:
- **Stable Diffusion 3**: DiT 아키텍처 + Flow Matching → 빠른 수렴
- **Flux** (Black Forest Labs): DiT 기반, 빠른 추론 (Schnell 4-step)
- **PixArt-α / PixArt-Σ**: 효율적 DiT, 작은 GPU에서도 실행 가능
- **DALL-E 3**: DiT + CLIP 재랭킹

**VAMOS 적용** (J-011 라우팅 테이블에 이미 반영됨):
- V1 기본 로컬: **Flux Schnell** (DiT, 4-step, 3s/img) → photo/prototype intent 1순위
- V1 로컬 보조: **SDXL** (UNet 기반, 호환성)
- V2: PixArt-Σ 로컬 추가 (더 가벼운 GPU 지원)
- ControlNet + DiT (Flux ControlNet) → J-013 controlnet 작업 V2

**구현성**: V1 ✅ 즉시 (Flux/SD3 로컬 적용 완료) → §6.7 트렌드 반영 100% 달성.

---

## E1~E10 자체 점검 요약

| J-ID | 상태 | E1 | E2 | E3 | E4 | E5 | E6 | E7 | E8 | E9 | E10 | 총점 | 판정 |
|------|------|----|----|----|----|----|----|----|----|----|----|------|------|
| J-011 | NEW | 10 | 10 | 15 | 10 | 10 | 10 | 10 | 10 | 10 | 5 | **100** | ✅ |
| J-012 | NEW | 9 | 10 | 13 | 9 | 8 | 9 | 9 | 9 | 8 | 4 | **88** | ✅ |
| J-013 | NEW | 10 | 10 | 13 | 9 | 9 | 9 | 9 | 10 | 9 | 5 | **93** | ✅ |
| J-014 | EXTEND | 10 | 10 | 14 | 10 | 9 | 9 | 10 | 10 | 9 | 4 | **95** | ✅ |
| J-015 | NEW | 9 | 10 | 12 | 9 | 8 | 8 | 8 | 9 | 8 | 5 | **86** | ✅ |
| J-016 | NEW | 9 | 10 | 12 | 8 | 9 | 8 | 8 | 9 | 8 | 4 | **85** | ✅ |
| J-018 | NEW | 9 | 10 | 13 | 9 | 8 | 9 | 9 | 9 | 8 | 4 | **88** | ✅ |
| J-020 | V3 L3 | 9 | 9 | 13 | 9 | 9 | 8 | 8 | 9 | 8 | 4 | **86** | ✅ V3 L3 |
| J-076 | 트렌드 병합 | — | — | — | — | — | — | — | — | — | — | (J-013/J-020 병합) | ✅ 반영 |
| J-079 | 트렌드 병합 | — | — | — | — | — | — | — | — | — | — | (J-011 라우팅 반영) | ✅ 반영 |

**Phase 1 V1 평가 대상 7건 모두 ≥ 80점 → L3 PASS**.
**§6.7 트렌드 J-076 / J-079 모두 본문에 반영 완료**.

---

## 변경 이력

| 날짜 | 변경 | 작성자 |
|------|------|--------|
| 2026-04-08 | 최초 작성 (J-011~J-016, J-018 L3 + J-020 골격 + J-076/J-079 트렌드 병합) | Phase 1-1 |
| 2026-05-31 | J-020 V3 L3 EXTEND (3D 자산 생성 — Meshy/TripoSR/Shap-E, E1~E10 86점) | Phase 4 RECOVERY Stage B |
