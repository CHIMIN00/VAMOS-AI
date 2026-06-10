# vision_language_integration.md — 비전-언어 모델 통합 (J-001~J-010)

> **Status**: APPROVED (L3)
> **작성일**: 2026-04-08
> **정본 소유 개념**: 이미지 입력 → 검증 → 전처리 → 라우팅(CLIP/OCR/Vision API) → MultimodalMessage 통합. 입력 단계의 비전-언어 모델 호출 전반을 정본으로 소유한다.
> **SoT 근거**: STEP7-J Part 1 (J-001~J-010) + 기존 명세 §2 (이미지 입력 파이프라인)
> **담당 J-ID**: J-001~J-010 (V1 9건 + V3 1건)
> **상위 인덱스**: [_index.md](./_index.md)

---

## LOCK 인용

> LOCK (STEP7-J J-001): 지원 미디어 포맷 — JPEG, PNG, WebP, GIF, SVG, BMP, TIFF, HEIC

> LOCK (STEP7-J J-001): 이미지 최대 리사이즈 — max 2048px

> LOCK (기존 명세 §2.2): CLIP 임베딩 차원 — 768d (ViT-L/14@336)

> LOCK (STEP7-J / 기존 명세): 처리 파이프라인 순서 — 입력→검증→전처리→라우팅→처리→통합

> LOCK (가이드 R-05-2): 파일 크기 상한 — 이미지 10MB / 오디오 25MB / 비디오 100MB

> LOCK (STEP7-J J-094~J-096): 비용 상한 — V1: ≤₩10K($8), V2: ≤₩40K($30), V3: ≤₩200K($150)

---

## 공통 참조: 이미지 입력 파이프라인 (부록 §A.1)

```
[이미지 입력] → [포맷 검증 (8포맷)] → [전처리]
    │                                       ├─ EXIF 회전 보정
    │                                       ├─ 색공간 정규화 (RGB)
    │                                       └─ 리사이즈 (max 2048px)
    ↓
[라우팅 (Multimodal Router J-083)]
    ├─→ [CLIP 임베딩] ──→ Qdrant (768d) → 유사도 검색
    ├─→ [OCR] ──→ 텍스트 추출 (Tesseract V1 / PaddleOCR V2)
    ├─→ [Vision API] ──→ 캡션/분석 (GPT-4o / Claude 4.6 / Gemini 2.0 Flash)
    └─→ [품질 평가 J-010] → 저품질 시 Real-ESRGAN 업스케일링
                                       ↓
                            [MultimodalMessage 생성]
```

> 파이프라인 순서는 LOCK-MM-03 준수. 모든 라우팅 결과는 단일 `MultimodalMessage`(LOCK-MM-05) 로 합쳐진다.

---

## J-001. 이미지 입력 처리 파이프라인 [V1 / EXTEND]

**상태**: EXTEND (기존 명세 §2.1, §2.2 계승)
**근거**: STEP7-J L11-28, 기존 명세 §2.1, 부록 §A.1

### E1. Input Schema
| 필드 | 타입 | 제약 |
|------|------|------|
| `image_bytes` | bytes | 필수, ≤ 10MB (LOCK-MM-10) |
| `mime_type` | enum | `image/{jpeg,png,webp,gif,svg+xml,bmp,tiff,heic}` (LOCK-MM-01) |
| `source_uri` | str? | URL/경로/clipboard, 선택 |
| `user_intent` | enum | `embed | ocr | vision | quality_only | full` |
| `processing_hint` | dict? | `{prefer_local: bool, max_cost_usd: float}` |

검증: 매직바이트 헤더 확인 → MIME 일치 확인 → 파일 크기 ≤ 10MB → 멀웨어 사전 차단 (J-010과 공유).

### E2. Output Schema
```python
class ImageIngestResult:
    image_id: UUID                          # UUID v7
    normalized_bytes: bytes                 # 전처리 후 (RGB, ≤2048px)
    width: int                              # ≤ 2048
    height: int                             # ≤ 2048
    embedding: Optional[list[float]]        # CLIP 768d (요청 시)
    ocr_text: Optional[str]                 # OCR 결과 (요청 시)
    caption: Optional[str]                  # Vision API 캡션 (요청 시)
    quality: QualityScore                   # J-010 결과
    processing_time_ms: int
    cost_usd: float
    provenance: dict                        # {model, version, prompt_hash}
```

### E3. Algorithm / Pipeline (의사코드)
```python
async def ingest_image(req: ImageIngestRequest) -> ImageIngestResult:
    # 1. 검증
    assert len(req.image_bytes) <= 10 * 1024 * 1024              # LOCK-MM-10
    fmt = sniff_format(req.image_bytes)
    assert fmt in {"JPEG","PNG","WEBP","GIF","SVG","BMP","TIFF","HEIC"}  # LOCK-MM-01

    # 2. 전처리
    img = pil_load(req.image_bytes)
    img = exif_autorotate(img)
    img = img.convert("RGB")
    img = resize_keep_aspect(img, max_side=2048)                  # LOCK-MM-02

    # 3. 품질 평가 (J-010 위임)
    quality = await assess_quality(img)
    if quality.score < 0.4 and (req.processing_hint or {}).get("allow_upscale", False):
        img = await real_esrgan_upscale(img)                      # V2

    # 4. 라우팅 (Multimodal Router J-083)
    tasks = []
    if req.user_intent in {"embed","full"}:
        tasks.append(clip_encode(img))                            # J-001 + J-007
    if req.user_intent in {"ocr","full"}:
        tasks.append(ocr_pipeline(img))                           # J-003
    if req.user_intent in {"vision","full"}:
        tasks.append(vision_api_call(img, req.processing_hint))   # J-001 + J-008

    embed, ocr_text, vision_caption = await gather_with_fallback(tasks)

    # 5. MultimodalMessage 통합 (J-002)
    return ImageIngestResult(...)
```

### E4. Model Selection
| 단계 | V1 (즉시) | V2 (3개월) | V3 (6개월+) |
|------|-----------|-----------|-------------|
| 임베딩 | CLIP ViT-L/14@336 로컬 (768d) | SigLIP, ImageBind 1024d 추가 | 커스텀 fine-tune |
| OCR | Tesseract 5.x | PaddleOCR | 자체 모델 |
| Vision API | Gemini 2.0 Flash 우선 | GPT-4o / Claude 4.6 | 멀티모델 합의 |
| 업스케일 | (off) | Real-ESRGAN 4x | 자체 SR |

선택 근거: V1은 LOCK-MM-06 (월 $8) 준수를 위해 로컬 CLIP + Gemini Flash($0.001/img) 우선. R-05-4 (로컬 우선).

### E5. Error Handling
| 에러 | 폴백 | 사용자 통지 |
|------|------|-------------|
| 미지원 포맷 | 변환 시도(HEIC→JPEG) 후 재시도 | "이 포맷은 변환 후 처리되었습니다" |
| ≥10MB | 거부 (R-05-2) | "이미지가 10MB를 초과합니다" |
| CLIP GPU OOM | CPU 백엔드 fallback | (silent) |
| Vision API 5xx | Gemini → Claude → GPT-4o 체인 | (silent) |
| 모든 API 실패 | 임베딩+OCR만 반환, `caption=None` | "비전 캡션 일시 불가" |
| EXIF 손상 | 원본 그대로 진행 | (silent) |

R-05-5 Graceful Degradation 체인 명시.

### E6. Cost Analysis (부록 §B.1)
| 처리 | 단가 | V1 일일 30건 월간 |
|------|------|-------------------|
| CLIP 로컬 | $0 (GPU 상각) | $0 |
| Tesseract | $0 | $0 |
| Gemini 2.0 Flash | $0.001/img | $0.9 |
| GPT-4o (옵션) | $0.00765/img | $6.9 |

V1 권장: Gemini Flash 단독 → 월 $0.9 (LOCK-MM-06 V1 한도 내). 캐싱 키 = SHA256(normalized_bytes).

### E7. Performance SLA
| 메트릭 | V1 목표 | V2 목표 |
|--------|---------|---------|
| P50 전처리 | ≤ 200ms | ≤ 100ms |
| P50 CLIP 인코딩 | ≤ 500ms | ≤ 300ms |
| P50 OCR (Tesseract) | ≤ 2s | ≤ 1s |
| P50 Vision API | ≤ 2s | ≤ 1.5s |
| P99 end-to-end | ≤ 5s | ≤ 3s |
| 처리량 | 5 img/s (단일 GPU) | 20 img/s |

### E8. Integration Test Spec
1. **happy path**: PNG 1024×768 → embedding(768d) + ocr_text + caption 반환, 2초 이내.
2. **HEIC 변환**: iPhone HEIC → 내부 JPEG 변환 → 정상 처리.
3. **10MB 거부**: 12MB JPEG → `FileTooLargeError`.
4. **EXIF 회전**: orientation=6 이미지 → 정방향 정규화 확인.
5. **API 폴백**: Gemini 강제 5xx → Claude로 자동 전환, 응답 동일 스키마.
6. **저품질 업스케일**: 240×180 블러 이미지 → quality<0.4 → V2에서 Real-ESRGAN 통해 통과.

### E9. Dependencies
- **외부**: Pillow ≥10, transformers (CLIP), pytesseract, openai/anthropic/google-generativeai SDK, Qdrant client
- **내부**: ORANGE CORE → Multimodal Router(J-083), 5-Layer Memory(J-064), Cost Manager(J-065), Quality Module(J-010)
- **저장**: Qdrant 컬렉션 `image_embeddings` (768d, Cosine, int8 양자화)

### E10. Privacy / Safety
- R-05-4: API 전송 전 사용자 동의 또는 `prefer_local=true` 우선.
- PII 마스킹: OCR 결과에 대해 J-017 전 단계에서 정규식 기반 1차 마스킹(이메일/주민번호/카드번호) 후 외부 API 전송.
- 메타데이터 EXIF GPS 자동 제거 (J-019에서 옵션 노출).

**E1~E10 자체 점수**: 10/10/15/10/10/10/10/10/10/5 = **100/100**

---

## J-002. 멀티모달 대화 컨텍스트 관리 [V1 / EXTEND]

**상태**: EXTEND (기존 명세 §5.1 MultimodalMessage 계승)
**근거**: STEP7-J L30-51

### E1. Input Schema
```python
class TurnInput:
    text: Optional[str]
    images: list[ImageRef]                  # 0..N (LOCK-MM-04 우선순위)
    audio: Optional[AudioRef]
    references: list[str]                   # 이전 image_id 회상 ("이전 그래프")
    session_id: UUID
    parent_turn_id: Optional[UUID]
```

### E2. Output Schema (LOCK-MM-05)
```python
class MultimodalMessage:
    id: UUID                                # v7
    role: Literal["user","assistant","system"]
    content: list[ContentPart]              # text|image|audio|tool_use
    metadata: dict                          # {turn_id, ts, model, cost, parent_id}
    refs: list[UUID]                        # 회상된 이전 image_id 목록
```

### E3. Algorithm
```python
async def build_turn(inp: TurnInput) -> MultimodalMessage:
    # 1. 모달리티 우선순위 정렬 (LOCK-MM-04: Text > Image > Audio > Video)
    parts = []
    if inp.text:
        parts.append(TextPart(inp.text))
    for img in inp.images:
        parts.append(ImagePart(image_id=img.id, embedding=img.embedding,
                               desc=img.caption))

    # 2. 회상 ("이전 그래프") → L1/L2 메모리에서 image_id 해석
    if inp.text and any(kw in inp.text for kw in REFERENCE_KEYWORDS):
        recalled = await recall_images(inp.text, inp.session_id, top_k=3)
        parts.extend(recalled)

    # 3. 컨텍스트 윈도우 압축 (J-085 위임)
    parts = await context_window_manager.fit(parts, model_limit)

    # 4. 5-Layer Memory(J-064)에 저장
    msg = MultimodalMessage(...)
    await memory.persist(msg, layer="L0_session")
    return msg
```

### E4. Model Selection
- 회상 검색: CLIP text→image (J-007 공유)
- 멀티턴 프롬프트 빌더: 모델별 어댑터 (Claude `image` block, GPT-4o `image_url`, Gemini `inline_data`)

### E5. Error Handling
| 에러 | 폴백 |
|------|------|
| 회상 0건 | 텍스트만 사용 + "이전 이미지 검색 실패" 로그 |
| 컨텍스트 초과 | 오래된 이미지 → thumbnail/desc로 강등 (J-085) |
| image_id dangling | 메타데이터(`desc`)만 인용 |

### E6. Cost
- 메모리 IO만 발생 (≈$0). 회상 1건당 Qdrant 검색 ≈ 5ms, 비용 0.

### E7. SLA
| | V1 |
|--|----|
| 회상 검색 | ≤ 50ms (Qdrant top_k=5) |
| 컨텍스트 빌드 | ≤ 100ms |
| 멀티턴 누적 이미지 | ≤ 32장 / 세션 (V1) |

### E8. Integration Test
1. 3턴 대화에서 1턴의 차트를 3턴에서 "그 그래프" → 동일 image_id 회상 확인.
2. 컨텍스트 200K 토큰 초과 시 가장 오래된 이미지 강등.
3. 세션 간 회상은 L2 (프로젝트 메모리)에서만 허용.

### E9. Dependencies
ORANGE CORE 5-Layer Memory(J-064), J-085 Context Window Manager, J-007 임베딩 검색, Qdrant.

### E10. Privacy
- 회상 검색은 같은 사용자/세션 권한 범위 내. 크로스세션 회상은 `project_id` 일치 필수.
- 이미지 caption에 PII 포함 시 마스킹 후 저장.

**자체 점수**: 95/100

---

## J-003. OCR + 문서 이해 [V1 / EXTEND]

**상태**: EXTEND (기존 명세 §2.3 계승)
**근거**: STEP7-J L53-72

### E1. Input Schema
```python
class OCRRequest:
    image: bytes | PIL.Image                # ≤ 10MB
    languages: list[str] = ["ko","en"]
    output_format: Literal["text","hocr","structured"]
    confidence_threshold: float = 0.7
    preprocess: list[str] = ["deskew","denoise"]
    document_type: Optional[Literal["pdf","scan","receipt","code","math"]]
```

### E2. Output Schema
```python
class OCRResult:
    text: str
    blocks: list[OCRBlock]                  # paragraph|heading|table|caption
    tables: list[Table]                     # img2table 결과
    language_detected: str
    confidence: float
    latex: Optional[str]                    # 수식 시
    processing_time_ms: int

class OCRBlock:
    text: str
    bbox: BBox
    confidence: float
    type: str
```

### E3. Algorithm
```python
async def ocr(req: OCRRequest) -> OCRResult:
    img = preprocess(req.image, req.preprocess)         # deskew, denoise, binarize
    if req.document_type == "pdf":
        return await pymupdf_layout(req.image)
    if req.document_type == "math":
        return await mathpix_latex(req.image)           # V2

    # V1 기본: Tesseract
    raw = pytesseract.image_to_data(img, lang="+".join(req.languages),
                                    output_type=Output.DICT)
    blocks = group_to_blocks(raw, req.confidence_threshold)
    if req.document_type in {"receipt","scan"}:
        tables = img2table.extract(img)
    return OCRResult(text=join(blocks), blocks=blocks, tables=tables, ...)
```

### E4. Model Selection
| 엔진 | 용도 | 언어 | 비용 | V단계 |
|------|------|------|------|-------|
| Tesseract 5.x | 로컬 기본 | 한/영/일/중 | 무료 | V1 |
| PaddleOCR | 정확도↑ | 80+ | GPU 상각 | V2 |
| Google Vision OCR | 고품질 | 200+ | $1.50/1K | V2 (고객 동의 시) |
| Naver CLOVA | 한국어 특화 | 한/영 | ₩3/req | V2 |
| Mathpix | 수식 | LaTeX | $0.004/img | V2 |

근거: V1은 R-05-4 (로컬 우선) + 비용 0.

### E5. Error Handling
| 에러 | 폴백 |
|------|------|
| 신뢰도 < 0.4 | 사용자에게 "OCR 정확도 낮음" 경고 + Vision API(GPT-4o) 보조 호출 |
| 비라틴 외 언어 미감지 | 자동 언어감지(langdetect) 재시도 |
| 표 추출 실패 | 텍스트만 반환 |
| Tesseract crash | PaddleOCR(V2) 또는 Vision API 폴백 |

### E6. Cost
| 시나리오 | V1 |
|----------|-----|
| 일일 20건 Tesseract | $0 |
| 보조 Vision 호출 5% | ≈ $0.07/월 |

### E7. SLA
- P50: ≤ 2s/page (Tesseract)
- P99: ≤ 5s/page
- 처리량: 10 page/s (단일 코어 4개)

### E8. Integration Test
1. 한국어 영수증 → tables.length ≥ 1, 합계 셀 추출.
2. 코드 스크린샷 → 들여쓰기 보존, 라인 80%+ 정확도.
3. 회전된 PDF 페이지 → deskew 후 정상 추출.
4. 신뢰도 < 0.4 시 자동 보조 Vision 트리거.
5. 영문/한글 혼합 → `language_detected="mixed"`, 두 언어 모두 추출.

### E9. Dependencies
pytesseract, PyMuPDF, img2table, langdetect, Pillow. ORANGE CORE → Knowledge Graph (문서→노드, J-003 §6의 차별화 포인트), 3-Gate Evidence Gate 연동(숫자 검증).

### E10. Privacy / Safety
- 영수증/명함의 카드번호/주민번호 정규식 마스킹 → 저장 전 적용.
- 로컬 처리 우선(R-05-4). Vision 보조 호출은 사용자 토글 필요.

**자체 점수**: 98/100

---

## J-004. 스크린 캡처 + 화면 이해 [V1 / NEW]

**근거**: STEP7-J L74-93

### E1. Input Schema
```python
class CaptureRequest:
    mode: Literal["full","window","region","periodic"]
    region: Optional[BBox]                  # mode=region 시 필수
    interval_sec: Optional[int]             # periodic
    monitor_index: int = 0
    consent_token: str                      # opt-in 필수
```

### E2. Output Schema
```python
class CaptureResult:
    capture_id: UUID
    image_path: Path                        # AES-256 암호화 로컬 저장
    timestamp: datetime
    masked_regions: list[BBox]              # PII 자동 마스킹
    ui_elements: list[UIElement]            # V2: 버튼/입력필드/메뉴
    semantic_tags: list[str]                # V1: CLIP zero-shot 분류
```

### E3. Algorithm
```python
async def capture(req: CaptureRequest) -> CaptureResult:
    if not consent.verify(req.consent_token):
        raise PermissionDenied("스크린 캡처 opt-in 필요")
    img = mss.grab(region or full_screen)               # mss > pyautogui (성능)
    img = pil_from_mss(img)

    # PII 자동 감지/마스킹
    pii_boxes = await pii_detector.find(img)            # OCR + regex
    img = mask_regions(img, pii_boxes)

    # 임베딩 + 시맨틱 태그
    embed = await clip_encode(img)
    tags = await zero_shot_classify(embed,
              labels=["코드","문서","브라우저","터미널","채팅","차트"])

    # 암호화 저장 → L1 메모리
    enc_path = aes256_save(img, key=user_key)
    await memory.persist_capture(...)
    return CaptureResult(...)
```

### E4. Model Selection
| 단계 | V1 | V2 | V3 |
|------|----|----|----|
| 캡처 백엔드 | mss (cross-platform) | mss + macOS ScreenCaptureKit | OS 네이티브 + GPU 직접 |
| UI 인식 | (off) | Ferret-UI / OmniParser (J-077) | 자체 모델 |
| 시맨틱 분류 | CLIP zero-shot | 학습된 분류기 | 사용자 fine-tune |

### E5. Error Handling
- 권한 없음 → opt-in UI 호출
- 디스크 가득 → 가장 오래된 캡처 자동 삭제 (FIFO, 7일 정책)
- 멀티모니터 인덱스 오류 → monitor_index=0 fallback

### E6. Cost
- 100% 로컬 → $0
- 디스크: 1080p PNG ≈ 500KB → 일 100장 = 50MB → 7일 350MB

### E7. SLA
- P50 캡처+마스킹: ≤ 300ms (1080p)
- 주기 캡처 최소 간격: 5초 (배터리/IO 보호)

### E8. Integration Test
1. opt-in 없이 호출 → `PermissionDenied`.
2. 신용카드 노출된 스크린 → 마스킹 박스 ≥ 1.
3. 7일 후 자동 삭제 트리거.
4. mode=region에서 좌표 음수 → 자동 클리핑.

### E9. Dependencies
mss, Pillow, cryptography (AES-256), CLIP. 5-Layer Memory L1 (7일 캐시).

### E10. Privacy / Safety
- 명시적 opt-in (consent_token), 클라우드 전송 0건
- AES-256 로컬 암호화, 사용자 키 OS keyring 보관
- 마스킹: 카드번호/주민번호/이메일/패스워드 필드 자동 박스 처리
- "일시정지", "범위 제한", "전체 삭제" UI 노출 (R-05-4 강화)

**자체 점수**: 92/100

---

## J-005. 차트/그래프/다이어그램 자동 분석 [V1 / NEW]

**근거**: STEP7-J L95-110

### E1. Input Schema
```python
class ChartAnalysisRequest:
    image: bytes
    chart_type_hint: Optional[Literal["bar","line","pie","scatter","heatmap","candlestick","unknown"]]
    extract_data: bool = True
    domain: Optional[Literal["finance","scientific","general"]]
```

### E2. Output Schema
```python
class ChartAnalysis:
    chart_type: str
    title: Optional[str]
    axes: dict                              # {x_label, y_label, x_unit, y_unit}
    series: list[Series]                    # [{name, points: [(x,y), ...]}]
    data_table: pd.DataFrame                # 추출된 수치
    insights: list[str]                     # 자연어 트렌드 요약
    confidence: float
```

### E3. Algorithm
```python
async def analyze_chart(req):
    # 1. 유형 감지: zero-shot CLIP 분류
    chart_type = req.chart_type_hint or await classify_chart_type(req.image)

    # 2. V1: Vision API에 구조화 출력 요청
    schema = CHART_SCHEMA[chart_type]
    raw = await vision_api(req.image,
            system="Extract chart data as JSON matching schema",
            json_schema=schema, model="gemini-2.0-flash")

    # 3. 도메인 특화 후처리
    if req.domain == "finance" and chart_type == "candlestick":
        raw = candlestick_pattern_detect(raw)           # 망치형/도지/엔걸핑

    # 4. 인사이트 LLM 생성 (트렌드/이상치)
    insights = await llm_summarize(raw["series"])

    return ChartAnalysis(...)
```

### E4. Model Selection
| 단계 | V1 | V2 |
|------|----|----|
| 유형 분류 | CLIP zero-shot | ChartOCR fine-tune |
| 데이터 추출 | Gemini 2.0 Flash JSON 모드 | DePlot (Google Research) |
| 패턴 인식 | LLM 추론 | 전용 모델 |

선택 근거: V1 단가 $0.001/img (Gemini Flash) → LOCK-MM-06 V1 한도 충족.

### E5. Error Handling
- chart_type=unknown → general caption만 반환, `data_table=None`
- JSON 파싱 실패 → 1회 재시도, 실패 시 raw text + 경고
- 축 단위 누락 → "단위 추정 불가" 노트

### E6. Cost
- Gemini Flash $0.001/img × 일 10건 = $0.30/월
- LLM 인사이트 (Claude Haiku) ≈ $0.05/월

### E7. SLA
- P50: ≤ 3s
- P99: ≤ 6s
- 데이터 추출 정확도 (V1): MAE ≤ 5% (단순 막대/선차트)

### E8. Integration Test
1. matplotlib 막대 차트 4개 막대 → 4개 (label, value) 정확 추출.
2. 캔들스틱 30봉 → OHLC 추출 + 패턴 1개 이상 식별.
3. 다중 시리즈 선차트 → series.length 일치.
4. 손글씨 차트 → confidence < 0.5 + 경고.

### E9. Dependencies
Pillow, google-generativeai, pandas, anthropic SDK. STEP7-I Quant Node 연계 (재무 차트→정량 분석).

### E10. Privacy
- 차트는 일반적으로 공개 데이터지만, 내부 자료 가능성 → R-05-4 준수, 사용자 동의 확인.

**자체 점수**: 89/100

---

## J-006. 실시간 비디오/카메라 입력 처리 [V1 / NEW (기본 캡처만)]

**근거**: STEP7-J L112-128. V1은 ⚠️ 기본 프레임 캡처 한정. 본격 실시간은 V2/V3.

### E1. Input Schema
```python
class VideoStreamRequest:
    source: Literal["webcam","screen","file","rtsp"]
    fps_sample: float = 1.0                 # V1: 1~5 fps
    duration_sec: Optional[int]
    analysis_mode: Literal["frame_only","captioning","tracking"]
    consent_token: str
```

### E2. Output Schema
```python
class VideoFrameEvent:
    frame_id: int
    timestamp_sec: float
    image: bytes                            # JPEG
    embedding: Optional[list[float]]        # CLIP 768d
    caption: Optional[str]
    detected_objects: list[Detection]       # V2
```

### E3. Algorithm
```python
async def stream_video(req):
    cap = open_source(req.source)                       # opencv-python
    interval = 1.0 / req.fps_sample
    last = 0
    while not done:
        ok, frame = cap.read()
        if not ok: break
        if time.time() - last < interval: continue
        last = time.time()

        img = bgr2rgb(frame)
        img = resize_keep_aspect(img, max_side=2048)    # LOCK-MM-02

        if req.analysis_mode != "frame_only":
            embed = await clip_encode(img)
            cap_text = await vision_api(img, model="gemini-flash")  # 비용 주의
            yield VideoFrameEvent(...)
        else:
            yield VideoFrameEvent(image=jpeg(img), embedding=None)
```

### E4. Model Selection
| 모드 | V1 | V2 |
|------|----|----|
| 캡처 | OpenCV (cv2.VideoCapture) | + DeepStream / FFmpeg HW |
| 임베딩 | CLIP 로컬 | SigLIP, ImageBind |
| 캡션 | Gemini Flash (선택적) | GPT-4o Vision Live |
| 추적 | (off) | YOLOv9 + ByteTrack |

### E5. Error Handling
- 카메라 권한 거부 → `PermissionDenied`
- RTSP 끊김 → exponential backoff 재연결 (최대 3회)
- API 비용 한도 도달 (R-05-6) → caption 비활성, frame_only 자동 전환
- 처리 지연 > interval × 2 → fps_sample 동적 하향

### E6. Cost
- frame_only: $0
- captioning 모드 (Gemini Flash, 1fps × 60s): $0.06
- V1 일일 5분 캡션: ≈ $9/월 → R-05-6 한도 근접 → 기본은 OFF

### E7. SLA
- P50 frame 캡처+리사이즈: ≤ 50ms (1080p)
- 1 fps 안정 지원
- captioning 모드 P50: ≤ 1.5s/frame

### E8. Integration Test
1. 웹캠 10초 캡처 → 10 frames (1fps).
2. 권한 없는 화면 캡처 → `PermissionDenied`.
3. RTSP 끊김 → 재연결 1회 성공.
4. 비용 한도 도달 시 frame_only 전환 로그.

### E9. Dependencies
opencv-python, cv2, mss, CLIP. ORANGE CORE Cost Manager(J-065)와 R-05-6 연동.

### E10. Privacy / Safety
- 명시적 opt-in. 실시간 카메라는 LED/UI 표시 의무.
- 캡처 프레임 로컬 우선, API 전송 시 사용자 확인.
- 얼굴 인식 OFF (V1).

**자체 점수**: 90/100

---

## J-007. 멀티모달 임베딩 통합 검색 [V1 / EXTEND]

**상태**: EXTEND (기존 명세 §2.2 CLIP + Qdrant 컬렉션 계승)
**근거**: STEP7-J L130-147

### E1. Input Schema
```python
class CrossModalQuery:
    query_type: Literal["text","image","audio"]
    text: Optional[str]
    image_bytes: Optional[bytes]
    audio_bytes: Optional[bytes]
    top_k: int = 10
    filters: dict                           # {project_id, date_range, tag}
    target_collections: list[str] = ["image_embeddings"]
```

### E2. Output Schema
```python
class SearchHit:
    asset_id: UUID
    score: float                            # cosine [0..1]
    modality: str
    metadata: dict                          # {caption, project, ts, ...}
    snippet: Optional[str]                  # 텍스트/캡션 조각
```

### E3. Algorithm
```python
async def cross_modal_search(q: CrossModalQuery) -> list[SearchHit]:
    # 1. 쿼리 임베딩
    if q.query_type == "text":
        vec = await clip_text_encode(q.text)            # 768d (LOCK-MM-07)
    elif q.query_type == "image":
        vec = await clip_image_encode(q.image_bytes)    # 768d
    elif q.query_type == "audio":
        vec = await clap_audio_encode(q.audio_bytes)    # 512d (별도 컬렉션)

    # 2. Qdrant 검색
    results = await qdrant.search(
        collection_name=q.target_collections[0],
        query_vector=vec,
        limit=q.top_k * 3,                              # over-fetch for re-rank
        query_filter=build_filter(q.filters),
    )

    # 3. Re-rank (V2: cross-encoder; V1: score 그대로)
    return [SearchHit(...) for r in results[:q.top_k]]
```

### E4. Model Selection
| 모달리티 | 모델 | 차원 | 컬렉션 |
|----------|------|------|--------|
| 텍스트/이미지 | CLIP ViT-L/14@336 | 768d (LOCK-MM-07) | `image_embeddings` |
| 오디오 | CLAP | 512d | `audio_embeddings` |
| 통합(V2) | ImageBind | 1024d | `multimodal_index` |

> 차원 불일치 처리: CLIP 768d ↔ ImageBind 1024d는 별도 컬렉션 (W4 대응).

### E5. Error Handling
- 쿼리 임베딩 실패 → 텍스트라면 BM25 fallback
- Qdrant timeout → in-memory FAISS 캐시 (최근 1만 벡터)
- top_k=0 → 빈 리스트 반환
- 차원 불일치 collection → 명시적 에러

### E6. Cost
- CLIP 인코딩 로컬 → $0
- Qdrant 자체 호스팅 → $0 (서버 상각)
- V2에서 ImageBind 추가 시 GPU VRAM +4GB 예상

### E7. SLA
- P50 쿼리 임베딩: ≤ 200ms
- P50 Qdrant 검색 (10K 벡터): ≤ 30ms
- end-to-end P99: ≤ 500ms

### E8. Integration Test
1. 텍스트 "빨간 자동차" → image_embeddings에서 빨간 차 이미지 top1.
2. 이미지 → 동일 이미지 self-retrieval score > 0.99.
3. 오디오 쿼리 → audio_embeddings 컬렉션 자동 라우팅.
4. 필터 `project_id=X` → 해당 프로젝트 결과만.

### E9. Dependencies
qdrant-client, transformers (CLIP), laion-clap (CLAP). ORANGE CORE → 5-Layer Memory L2/L3 (영구 임베딩 저장).

### E10. Privacy
- 검색 결과는 사용자 권한 범위 내 (project_id, owner_id 필터 강제).
- 임베딩은 원본 복원 불가하지만, 메타데이터에 PII 포함 시 마스킹.

**자체 점수**: 96/100

---

## J-008. 비전 기반 코드 이해 [V1 / NEW]

**근거**: STEP7-J L149-165

### E1. Input Schema
```python
class CodeVisionRequest:
    image: bytes                            # 코드 스크린샷/UI 이미지/에러 캡처
    task: Literal["extract_code","wireframe_to_code","error_analysis","ui_to_react"]
    target_language: Optional[str]          # python|typescript|...
    framework: Optional[str]                # react|vue|svelte
```

### E2. Output Schema
```python
class CodeVisionResult:
    extracted_code: Optional[str]           # 원본 코드 텍스트
    generated_code: Optional[str]           # 변환된 코드
    language: str
    diagnostics: list[Diagnostic]           # 에러 분석 시
    confidence: float
    suggestions: list[str]
```

### E3. Algorithm
```python
async def code_vision(req):
    if req.task == "extract_code":
        # OCR (J-003) + 구문 검증
        ocr = await ocr_pipeline(req.image, document_type="code")
        lang = detect_language(ocr.text)                # pygments
        # AST 파싱으로 검증
        try:
            ast.parse(ocr.text) if lang == "python" else ts.parse(ocr.text)
        except SyntaxError as e:
            ocr = await vision_api_correct(req.image, ocr.text)
        return CodeVisionResult(extracted_code=ocr.text, language=lang, ...)

    if req.task == "ui_to_react":
        # Vision API → React 컴포넌트 직접 생성
        return await vision_api(req.image,
            system=PROMPT_UI_TO_REACT, model="claude-sonnet-4-6")

    if req.task == "error_analysis":
        ocr = await ocr_pipeline(req.image, document_type="code")
        diagnostics = await llm_diagnose(ocr.text)
        return CodeVisionResult(diagnostics=diagnostics, ...)
```

### E4. Model Selection
| 작업 | V1 | V2 |
|------|----|----|
| 코드 OCR | Tesseract + AST 검증 | TrOCR-code fine-tune |
| UI→React | Claude 4.6 Vision (가장 우수) | v0-style 학습 모델 |
| 에러 분석 | Claude/GPT-4o + LSP | Code-LLaMA 로컬 |

### E5. Error Handling
- AST 파싱 실패 3회 → "수동 확인 필요" + raw OCR 텍스트 반환
- 지원 언어 미감지 → `language="unknown"` + 추측 제시
- 워터마크/모자이크 → confidence 하향 + 경고

### E6. Cost
- Tesseract OCR: $0
- Claude Vision (UI→React): $0.0048/img × 일 5건 = $0.72/월
- 에러 분석 (Haiku): $0.001/req

### E7. SLA
- P50 코드 추출: ≤ 3s
- P50 UI→React 변환: ≤ 8s (긴 LLM 응답)
- P99: ≤ 15s

### E8. Integration Test
1. Python 함수 스크린샷 → AST 파싱 성공, 100% 라인 일치.
2. 간단한 와이어프레임 → React 컴포넌트 (lint 통과).
3. 스택트레이스 캡처 → diagnostics ≥ 1, 해결책 제시.
4. 손글씨 코드 → confidence < 0.5 경고.

### E9. Dependencies
pytesseract, pygments, ast/ts-morph, anthropic SDK. Dev Node (코드 실행/테스트) 연계 → "분석→생성→실행" 자동 파이프라인.

### E10. Privacy
- 사내 코드일 가능성 → R-05-4 강제 (로컬 우선, API 전송 동의)
- API 키/시크릿 정규식 마스킹 후 외부 호출.

**자체 점수**: 93/100

---

## J-009. 공간 이해 및 AR 연동 [V3 / NEW — L3]

> **V3 항목 L3 완성** (Phase 4 RECOVERY Stage B, 2026-05-31). 3D 공간 이해(depth estimation) + ARKit/ARCore 좌표계 정렬 + 공간 메시 생성.
> **Status**: APPROVED (L3) — V3 산출물

**근거**: STEP7-J L167-182

### 요약
- 3D 공간 이해 (depth estimation), 물체 인식 + 위치 추정, AR 오버레이, 매장/사무실 레이아웃 분석.
- 시중 비교: Apple Vision Pro / Google Lens. VAMOS 차별화: 개인화 공간 컨텍스트 + 메모리 연동.
- 의존: ARKit/ARCore (V3 모바일 앱), depth-anything 모델군, 5-Layer Memory L2.
- 예상 V단계: V3 (12개월+, 하드웨어 의존).

> LOCK (출처): LOCK-MM-01 지원 미디어 포맷 = JPEG, PNG, WebP, GIF, SVG, BMP, TIFF, HEIC
> LOCK (출처): LOCK-MM-02 이미지 최대 리사이즈 = max 2048px
> LOCK (출처): LOCK-MM-05 MultimodalMessage 스키마 = UUID v7, content[], metadata 구조 (DEFINED-HERE, Phase 5 동결)

### E1. Input Schema
```python
class SpatialUnderstandingRequest:
    frame: bytes                            # 단일 프레임 (포맷: LOCK-MM-01, ≤2048px LOCK-MM-02)
    camera_intrinsics: Optional[dict]       # {fx, fy, cx, cy} — 없으면 추정
    device_pose: Optional[dict]             # ARKit/ARCore world transform 4x4 (있으면 좌표 정렬)
    platform: Literal["arkit","arcore","none"] = "none"
    enable_mesh: bool = True                # 공간 메시 생성 여부
    target_objects: list[str] = []          # 위치 추정 대상 (빈 리스트 = 전체 검출)
    message_id: str                         # UUID v7 (LOCK-MM-05)
```

### E2. Output Schema
```python
class SpatialScene:
    depth_map: np.ndarray                   # H×W float32, 미터 단위 (metric depth)
    point_cloud: Optional[np.ndarray]       # N×3 (camera or world 좌표계)
    coordinate_frame: Literal["camera","world"]   # device_pose 제공 시 world
    objects: list[DetectedObject]           # {label, bbox_2d, position_3d(x,y,z), confidence}
    spatial_mesh: Optional[SpatialMesh]     # vertices, faces, normals (enable_mesh=True)
    layout: Optional[dict]                  # {floor_plane, walls[], free_space_m2}
    degraded: bool                          # depth 폴백 진입 시 True (2D-only)
```

### E3. Algorithm
```python
async def understand_space(req):
    img = decode_validate(req.frame)                 # LOCK-MM-01 포맷 검증 + ≤2048px clamp (LOCK-MM-02)

    # 1) Metric depth 추정
    try:
        depth = await depth_model.infer(img)         # DPT-Large / Depth-Anything-V2
        depth = to_metric(depth, req.camera_intrinsics)
    except DepthModelError:
        return degrade_to_2d(img)                     # E5 폴백 → 2D bbox only

    # 2) 물체 검출 + 3D 위치 역투영 (back-projection)
    dets = await detector.infer(img)                  # Grounding-DINO / YOLO-World (open-vocab)
    objects = [back_project(d, depth, req.camera_intrinsics) for d in dets
               if not req.target_objects or d.label in req.target_objects]

    # 3) ARKit/ARCore 좌표계 정렬
    frame = "camera"
    if req.device_pose is not None:                   # world transform 적용
        depth, objects = align_to_world(depth, objects, req.device_pose)
        frame = "world"

    # 4) 공간 메시 + 레이아웃
    mesh = build_mesh(depth, req.camera_intrinsics) if req.enable_mesh else None  # TSDF/Poisson
    layout = estimate_layout(depth)                   # RANSAC 평면 분할 (바닥/벽)

    return SpatialScene(depth_map=depth, coordinate_frame=frame,
                        objects=objects, spatial_mesh=mesh, layout=layout, degraded=False)
```

### E4. Model Selection
| 기능 | V1 | V2 | V3 (본 항목) |
|------|----|----|----|
| Depth 추정 | (off) | MiDaS v3.1 (relative) | **DPT-Large / Depth-Anything-V2 (metric)** |
| 물체 검출 | — | YOLOv8 (closed-set) | **Grounding-DINO / YOLO-World (open-vocab)** |
| 좌표계 정렬 | — | — | **ARKit (iOS) / ARCore (Android) world transform** |
| 메시 생성 | — | — | **TSDF fusion / Poisson 재구성** |
| 레이아웃 | — | 2D bbox | RANSAC 평면 분할 (floor/wall) |

> 모델 비교 근거: DPT-Large는 metric depth 정확도 우위(절대 거리), Depth-Anything-V2는 추론 속도(SLA ≤ 300ms/frame 충족) 우위. 디바이스 GPU 가용 시 DPT-Large, 모바일/저사양은 Depth-Anything-V2-Small.

### E5. Error Handling (폴백)
- **Depth 모델 실패/타임아웃** → `degrade_to_2d()`: depth 없이 2D bbox + label만 반환, `degraded=True`, position_3d=null. AR 오버레이는 2D 앵커로 폴백.
- **camera_intrinsics 부재** → 디바이스 기본 FoV로 추정(정확도 경고 플래그).
- **device_pose 부재** → camera 좌표계 유지(`coordinate_frame="camera"`), world 정렬 생략.
- **메시 생성 실패** → point_cloud만 반환(`spatial_mesh=null`), 비치명적.

### E6. Cost
- 100% 온디바이스/로컬 GPU 추론 → per-call $0 (외부 API 미사용).
- 클라우드 폴백(저사양 디바이스, DPT-Large 원격 추론) 시 GPU 초당 과금 ≈ $0.02/frame.
- **부록 §B.2 V3 시나리오**: 실시간 30fps AR 세션 10분 = 18,000 frame 중 키프레임 샘플링(2fps) → 1,200 추론 → 클라우드 폴백 최악 ≈ $24/세션 ≤ **LOCK-MM-06 V3=$150** 한도 내. 온디바이스 우선 정책으로 실측 대부분 $0.

> LOCK (출처): LOCK-MM-06 비용 상한 — V3: ≤₩200K($150) per-call (per-call 미디어 처리 비용 상한)

### E7. SLA
- **목표: ≤ 300ms/frame** (depth + 검출 + 역투영, 온디바이스 GPU).
- P50: ≤ 180ms (Depth-Anything-V2-Small) / P95: ≤ 300ms / P99: ≤ 500ms (DPT-Large 클라우드 폴백 포함).
- 메시 재구성은 비동기 백그라운드(SLA 외), 키프레임마다 증분 업데이트.

### E8. Integration Test
1. 실내 거실 프레임 + ARKit pose → `coordinate_frame="world"`, 바닥 평면 검출 + 소파/테이블 3D 위치 반환.
2. depth 모델 강제 실패 주입 → `degraded=True`, 2D bbox만 반환, AR 2D 앵커 폴백 동작.
3. camera_intrinsics 누락 → 기본 FoV 추정 + 경고 플래그, 처리 계속.
4. 2048px 초과 입력 → LOCK-MM-02 clamp 후 처리(원본 비율 보존).
5. target_objects=["chair"] → 의자만 위치 추정, 그 외 검출 제외.
6. 30fps 라이브 피드 키프레임 2fps 샘플링 → 평균 latency ≤ 300ms 충족.

### E9. Dependencies
DPT-Large / Depth-Anything-V2 (depth), Grounding-DINO / YOLO-World (open-vocab 검출), Open3D (TSDF/Poisson 메시), ARKit (iOS) / ARCore (Android) SDK. 5-Layer Memory L2 연동(개인화 공간 컨텍스트 저장). 4-1 Rust-Tauri 네이티브 브리지(V3 모바일 앱).

### E10. Privacy / Safety
- 공간 스캔 데이터(메시/포인트클라우드)는 사용자 명시 동의 후에만 클라우드 전송, 기본 온디바이스 처리.
- 실내 레이아웃은 민감 정보 → 5-Layer Memory L2 암호화 저장 + 사용자 삭제 권한(GDPR Right to Erasure).
- 타인 얼굴/신체 검출 시 익명화 옵션(개인정보 보호).

**자체 점수**: 88/100 (V3 L3 — E1~E10 9요소 PASS, ≥80 목표 충족)

---

## J-010. 멀티모달 입력 품질 관리 [V1 / NEW]

**근거**: STEP7-J L184-194

### E1. Input Schema
```python
class QualityCheckRequest:
    image: bytes
    auto_fix: bool = False                  # True면 개선 시도
    target_min_score: float = 0.6
```

### E2. Output Schema
```python
class QualityScore:
    score: float                            # 0..1
    resolution: tuple[int,int]
    blur_score: float                       # Laplacian variance 정규화
    noise_score: float
    brightness: float                       # 0..1
    is_safe_format: bool
    is_malicious: bool
    fixed_image: Optional[bytes]            # auto_fix=True 시
    recommendations: list[str]
```

### E3. Algorithm
```python
async def assess_quality(req):
    # 멀웨어/포맷 검증 — 파싱(pil_load) 이전에 선행 (parse-time exploit 차단, E1 §검증 순서)
    safe = sniff_format(req.image) in SUPPORTED          # LOCK-MM-01
    malicious = await scan_polyglot(req.image)           # SVG/EXIF 폴리글롯 차단
    if not safe or malicious:
        raise SafetyViolation("unsupported or malicious image (polyglot/format)")
    img = pil_load(req.image)
    w, h = img.size

    # 블러: Laplacian variance
    gray = img.convert("L")
    lap_var = cv2.Laplacian(np.array(gray), cv2.CV_64F).var()
    blur = sigmoid_normalize(lap_var, k=100)

    # 노이즈: 표준편차 기반
    noise = 1 - normalize(np.std(np.array(gray)))

    # 밝기 분포
    brightness = np.mean(np.array(gray)) / 255

    # 멀웨어/포맷 검증
    safe = sniff_format(req.image) in SUPPORTED          # LOCK-MM-01
    malicious = await scan_polyglot(req.image)           # SVG/EXIF 폴리글롯 차단

    score = weighted_avg(blur, 1-noise, balance(brightness),
                         resolution_score(w,h))

    fixed = None
    if req.auto_fix and score < req.target_min_score:
        if blur < 0.4:
            fixed = await real_esrgan_upscale(img)       # V2
        if brightness < 0.2 or brightness > 0.85:
            fixed = auto_levels(fixed or img)

    return QualityScore(score=score, blur_score=blur, ...)
```

### E4. Model Selection
| 측정 | V1 | V2 | V3 |
|------|----|----|----|
| 블러 | Laplacian var | NIQE/BRISQUE 학습 모델 | LIQE 멀티스케일 |
| 노이즈 | std 기반 | DnCNN | Restormer |
| 업스케일 | (off) | Real-ESRGAN 4x | SwinIR |
| 멀웨어 | magic-bytes + polyglot 검사 | ClamAV 통합 | sandbox |

### E5. Error Handling
- 멀웨어 의심 → 즉시 거부 + 격리 로그
- 업스케일 실패 → 원본 반환 + 경고
- 모든 측정 실패 → score=0 + "분석 불가" 사용자 통지

### E6. Cost
- 100% 로컬 → $0
- Real-ESRGAN(V2) GPU 부하 ≈ 3s/img

### E7. SLA
- P50 평가: ≤ 100ms (1080p)
- P99: ≤ 300ms
- 멀웨어 스캔 추가 시 +50ms

### E8. Integration Test
1. 1080p 선명한 사진 → score ≥ 0.85.
2. 블러 처리된 사진 → score < 0.4, recommendations에 "업스케일 권장".
3. SVG 폴리글롯 (JS 포함) → is_malicious=True, 거부.
4. 240×180 → resolution_score 패널티.
5. 과노출 사진 → brightness > 0.9, auto_fix 시 정상화.

### E9. Dependencies
opencv-python, numpy, Pillow, python-magic, real-esrgan(V2). 모든 J-001~J-008 진입점에서 본 모듈을 호출.

### E10. Safety
- 멀웨어 차단 = 1차 안전 게이트 (J-017과 별개로 입력 단계에서 작동).
- 자동 개선은 사용자 동의 옵션 (`auto_fix`).

**자체 점수**: 95/100

---

## §6.7 트렌드 반영 노트

본 파일은 §6.7 항목 직접 배분 대상이 아님. (J-076/J-079는 `image_generation.md`로 배분.) 다만 J-007에서 ImageBind/CLAP 등 최신 통합 임베딩 기술 동향을 V2 로드맵에 명시했다.

---

## E1~E10 자체 점검 요약

| J-ID | E1 | E2 | E3 | E4 | E5 | E6 | E7 | E8 | E9 | E10 | 총점 | 판정 |
|------|----|----|----|----|----|----|----|----|----|----|------|------|
| J-001 | 10 | 10 | 15 | 10 | 10 | 10 | 10 | 10 | 10 | 5 | **100** | ✅ L3 |
| J-002 | 10 | 10 | 14 | 9 | 9 | 8 | 10 | 10 | 10 | 5 | **95** | ✅ L3 |
| J-003 | 10 | 10 | 14 | 10 | 10 | 9 | 10 | 10 | 10 | 5 | **98** | ✅ L3 |
| J-004 | 10 | 10 | 13 | 9 | 8 | 9 | 9 | 10 | 9 | 5 | **92** | ✅ L3 |
| J-005 | 9 | 10 | 13 | 9 | 8 | 9 | 8 | 10 | 9 | 4 | **89** | ✅ L3 |
| J-006 | 9 | 10 | 13 | 9 | 9 | 8 | 8 | 10 | 9 | 5 | **90** | ✅ L3 |
| J-007 | 10 | 10 | 14 | 10 | 9 | 9 | 10 | 10 | 10 | 4 | **96** | ✅ L3 |
| J-008 | 10 | 10 | 13 | 9 | 9 | 9 | 9 | 10 | 9 | 5 | **93** | ✅ L3 |
| J-009 | 9 | 9 | 13 | 9 | 9 | 9 | 8 | 9 | 9 | 4 | **88** | ✅ V3 L3 |
| J-010 | 10 | 10 | 14 | 10 | 9 | 9 | 9 | 10 | 9 | 5 | **95** | ✅ L3 |

**Phase 1 V1 평가 대상 9건 모두 ≥ 80점 → L3 PASS**.

---

## 변경 이력

| 날짜 | 변경 | 작성자 |
|------|------|--------|
| 2026-04-08 | 최초 작성 (J-001~J-010 L3, J-009 골격) | Phase 1-1 |
| 2026-05-31 | J-009 V3 L3 EXTEND (공간 이해/AR — Depth + ARKit/ARCore + 공간 메시, E1~E10 88점) | Phase 4 RECOVERY Stage B |
