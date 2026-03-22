# MULTIMODAL_PROCESSING 상세명세

> **Tier**: 3 (Feature Domains) | **Part2 Status**: SHELL | **SOT**: STEP7-J (98 items)
> **Version**: 1.0.0 | **최종수정**: 2026-03-22
> **교차참조**: T2-CORE_AI → LLM Router, T2-DATA_PIPELINE → Ingestion, T3-PKM → Knowledge Capture

---

## 1. 개요

VAMOS 멀티모달 처리 모듈은 텍스트 외 이미지, 오디오, 비디오 입력을 통합 처리하여
멀티모달 대화 경험을 제공한다. 각 모달리티별 전처리 → 특징추출 → 통합 → 응답생성
파이프라인을 정의한다.

### 1.1 버전 로드맵

| 기능 영역 | V1 (MVP) | V2 (Enhanced) | V3 (Full) |
|-----------|----------|---------------|-----------|
| 이미지 입력 | CLIP 임베딩 + 기본 OCR | Vision API 통합 | 실시간 스트리밍 |
| 오디오 처리 | Whisper STT 기본 | 화자분리 + 감정인식 | 실시간 TTS 대화 |
| 비디오 분석 | 프레임 추출만 | 장면분할 + 요약 | 실시간 비디오 분석 |
| 문서 생성 | Plotly 기본 차트 | D3.js 인터랙티브 | 풀 다이어그램 생성 |
| 크로스모달 검색 | 텍스트→이미지 | 양방향 검색 | 모든 모달리티 통합 |

---

## 2. 이미지 입력 파이프라인

### 2.1 처리 흐름

```
[이미지 업로드] → [포맷 검증] → [리사이즈/정규화] → [라우팅]
                                                        ├─→ [CLIP 임베딩] → 벡터 저장
                                                        ├─→ [OCR 처리] → 텍스트 추출
                                                        └─→ [Vision API] → 캡션/분석
                                                              ↓
                                                    [통합 MultimodalMessage 생성]
```

### 2.2 CLIP 임베딩 처리

```python
# clip_processor.py
class CLIPProcessor:
    MODEL_ID = "openai/clip-vit-large-patch14-336"
    EMBEDDING_DIM = 768
    MAX_IMAGE_SIZE = (336, 336)
    BATCH_SIZE = 16

    async def process(self, image: bytes, options: CLIPOptions) -> CLIPResult:
        """
        1. 이미지 디코딩 및 전처리 (RGB 변환, 리사이즈)
        2. CLIP 비전 인코더 추론
        3. L2 정규화된 임베딩 벡터 반환
        4. 벡터DB (Qdrant) 저장
        """
        preprocessed = self._preprocess(image)
        embedding = await self._encode(preprocessed)
        return CLIPResult(
            embedding=embedding,          # float32[768]
            confidence=float(logit),
            processing_time_ms=elapsed
        )
```

### 2.3 OCR 처리 모듈

| 엔진 | 용도 | 언어 지원 | 비용 |
|------|------|----------|------|
| Tesseract 5.x | 로컬 기본 OCR | 한/영/일/중 | 무료 |
| Google Vision API | 고품질 OCR | 200+ 언어 | $1.50/1K 요청 |
| Naver CLOVA OCR | 한국어 특화 | 한/영 | ₩3/요청 |

```typescript
// ocr_pipeline.ts
interface OCRConfig {
  engine: "tesseract" | "google_vision" | "clova";
  languages: string[];            // ["ko", "en"]
  outputFormat: "text" | "hocr" | "structured";
  confidenceThreshold: number;    // 0.0 ~ 1.0, default 0.7
  preprocessSteps: ("deskew" | "denoise" | "binarize")[];
}

interface OCRResult {
  text: string;
  blocks: OCRBlock[];             // 영역별 텍스트 블록
  confidence: number;
  language_detected: string;
  processing_time_ms: number;
}

interface OCRBlock {
  text: string;
  bbox: { x: number; y: number; w: number; h: number };
  confidence: number;
  type: "paragraph" | "heading" | "table" | "caption";
}
```

### 2.4 Vision API 통합

```python
# vision_api_router.py
VISION_PROVIDERS = {
    "openai": {
        "model": "gpt-4o",
        "max_image_size_mb": 20,
        "cost_per_image": 0.00765,   # 고해상도 기준
        "supported_formats": ["png", "jpg", "gif", "webp"],
    },
    "anthropic": {
        "model": "claude-sonnet-4-20250514",
        "max_image_size_mb": 20,
        "cost_per_image": 0.0048,
        "supported_formats": ["png", "jpg", "gif", "webp"],
    },
    "google": {
        "model": "gemini-2.0-flash",
        "max_image_size_mb": 20,
        "cost_per_image": 0.001,
        "supported_formats": ["png", "jpg", "gif", "webp", "pdf"],
    }
}
```

---

## 3. 오디오 처리

### 3.1 오디오 처리 파이프라인

```
[오디오 입력] → [포맷변환 ffmpeg] → [VAD 음성구간검출]
    ↓
[Whisper/Deepgram STT] → [텍스트]
    ↓                        ↓
[화자분리 pyannote] → [화자별 세그먼트] → [감정인식] → [MultimodalMessage]
    ↓
[TTS 응답생성] → [오디오 출력]
```

### 3.2 STT 엔진 비교

| 엔진 | 정확도(한국어) | 지연시간 | 비용 | 실시간 |
|------|-------------|---------|------|-------|
| Whisper large-v3 | 92% WER | 2~5초/분 | GPU 비용만 | 불가 (배치) |
| Whisper turbo | 88% WER | 0.5~1초/분 | GPU 비용만 | 준실시간 |
| Deepgram Nova-2 | 90% WER | <300ms | $0.0043/분 | 가능 |
| Google STT v2 | 91% WER | <500ms | $0.006/분 | 가능 |

### 3.3 화자 분리 (Speaker Diarization)

```python
# speaker_diarization.py
class SpeakerDiarizer:
    """pyannote/speaker-diarization-3.1 기반 화자 분리"""

    CONFIG = {
        "model": "pyannote/speaker-diarization-3.1",
        "min_speakers": 1,
        "max_speakers": 10,
        "embedding_model": "pyannote/wespeaker-voxceleb-resnet34",
        "clustering": "agglomerative",
        "min_cluster_size": 15,    # 초 단위 최소 발화 길이
    }

    async def diarize(self, audio_path: str) -> list[SpeakerSegment]:
        """
        Returns: [
            SpeakerSegment(speaker="SPEAKER_00", start=0.0, end=3.2, text="..."),
            SpeakerSegment(speaker="SPEAKER_01", start=3.5, end=7.1, text="..."),
        ]
        """
```

### 3.4 감정 인식 (Speech Emotion Recognition)

```python
# speech_emotion.py
EMOTION_TAXONOMY = {
    "primary": ["기쁨", "슬픔", "분노", "공포", "놀람", "혐오", "중립"],
    "secondary": ["흥분", "불안", "좌절", "만족", "지루함", "혼란"],
    "arousal_valence": {  # Russell's circumplex model
        "arousal": (-1.0, 1.0),   # 각성도
        "valence": (-1.0, 1.0),   # 쾌-불쾌
    }
}

class SpeechEmotionResult:
    primary_emotion: str           # "기쁨"
    confidence: float              # 0.87
    arousal: float                 # 0.6
    valence: float                 # 0.8
    secondary_emotions: dict       # {"흥분": 0.3, "만족": 0.2}
```

### 3.5 TTS (Text-to-Speech)

| 엔진 | 한국어 품질 | 지연시간 | 비용 |
|------|----------|---------|------|
| OpenAI TTS-1-HD | 우수 | ~1초 | $15/1M chars |
| ElevenLabs | 최상 | ~0.5초 | $0.18/1K chars |
| Google TTS | 양호 | ~0.3초 | $4/1M chars |
| Edge TTS (로컬) | 양호 | <0.1초 | 무료 |

---

## 4. 비디오 분석

### 4.1 비디오 처리 파이프라인

```
[비디오 업로드] → [FFmpeg 메타데이터 추출]
    ↓
[프레임 샘플링] ─────────────────→ [오디오 트랙 분리]
    ↓                                    ↓
[장면 분할 PySceneDetect]          [오디오 파이프라인 §3]
    ↓                                    ↓
[키프레임 선택] → [CLIP/Vision 분석]  [STT + 화자분리]
    ↓                                    ↓
[장면별 설명 생성] ←──── 통합 ────→ [시간정렬 자막]
    ↓
[비디오 요약 + 인덱싱]
```

### 4.2 프레임 샘플링 전략

```python
# frame_sampler.py
class FrameSamplingStrategy(Enum):
    UNIFORM = "uniform"               # 고정 간격 (예: 1fps)
    SCENE_BASED = "scene_based"       # 장면전환 기반
    CONTENT_ADAPTIVE = "adaptive"     # 콘텐츠 변화량 기반
    KEYFRAME_ONLY = "keyframe"        # I-frame만 추출

class FrameSamplerConfig:
    strategy: FrameSamplingStrategy = UNIFORM
    fps: float = 1.0                  # UNIFORM일 때 초당 프레임
    max_frames: int = 100             # 최대 추출 프레임 수
    scene_threshold: float = 27.0     # SCENE_BASED 민감도 (ContentDetector)
    min_scene_length_sec: float = 0.5
    output_format: str = "jpg"
    output_quality: int = 85
    resize_max_dim: int = 1024        # 장변 기준 리사이즈
```

### 4.3 FFmpeg 유틸리티

```python
# ffmpeg_utils.py
FFMPEG_PRESETS = {
    "extract_audio": "ffmpeg -i {input} -vn -acodec pcm_s16le -ar 16000 -ac 1 {output}",
    "extract_frames": "ffmpeg -i {input} -vf fps={fps} -q:v 2 {output_dir}/frame_%06d.jpg",
    "scene_detect": "ffmpeg -i {input} -vf select='gt(scene,{threshold})',showinfo -vsync vfr {output_dir}/scene_%04d.jpg",
    "thumbnail": "ffmpeg -i {input} -ss {timestamp} -vframes 1 -q:v 2 {output}",
    "video_info": "ffprobe -v quiet -print_format json -show_format -show_streams {input}",
}
```

---

## 5. 멀티모달 대화 데이터구조

### 5.1 MultimodalMessage 스키마

```typescript
// multimodal_message.ts
interface MultimodalMessage {
  id: string;                         // UUID v7
  conversation_id: string;
  role: "user" | "assistant" | "system";
  timestamp: string;                  // ISO 8601
  content: MultimodalContent[];       // 복수 모달리티 허용
  metadata: MessageMetadata;
}

interface MultimodalContent {
  type: "text" | "image" | "audio" | "video" | "file" | "chart" | "diagram";
  data: ContentData;
  processing_status: "pending" | "processing" | "completed" | "failed";
  processing_result?: ProcessingResult;
}

interface ContentData {
  // 텍스트
  text?: string;
  // 바이너리 (이미지/오디오/비디오)
  url?: string;                       // S3/R2 presigned URL
  mime_type?: string;                 // "image/png", "audio/wav"
  size_bytes?: number;
  // 파일 메타데이터
  filename?: string;
  thumbnail_url?: string;
}

interface ProcessingResult {
  modality: string;
  extracted_text?: string;            // OCR/STT 결과
  embedding?: number[];               // CLIP 등 벡터
  caption?: string;                   // Vision API 캡션
  emotions?: EmotionResult;           // 감정 분석
  speakers?: SpeakerSegment[];        // 화자 분리
  scenes?: SceneInfo[];               // 비디오 장면 정보
  confidence: number;
  processing_time_ms: number;
  cost_usd?: number;
}

interface MessageMetadata {
  model_used?: string;
  total_tokens?: number;
  modalities_processed: string[];     // ["image", "text"]
  total_processing_time_ms: number;
  total_cost_usd: number;
}
```

### 5.2 저장소 스키마 (PostgreSQL)

```sql
CREATE TABLE multimodal_messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id),
    role            VARCHAR(16) NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    metadata        JSONB NOT NULL DEFAULT '{}'
);

CREATE TABLE message_contents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id      UUID NOT NULL REFERENCES multimodal_messages(id),
    content_type    VARCHAR(32) NOT NULL,  -- 'text','image','audio','video'
    content_data    JSONB NOT NULL,
    processing_status VARCHAR(16) DEFAULT 'pending',
    processing_result JSONB,
    sort_order      SMALLINT DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_mc_message ON message_contents(message_id);
CREATE INDEX idx_mc_type ON message_contents(content_type);
```

---

## 6. 이미지/문서 생성

### 6.1 차트 생성 파이프라인

```
[사용자 요청] → [의도 파싱: 차트 유형 결정]
    ↓
[데이터 추출/변환] → [Plotly/D3.js 렌더링] → [SVG/PNG 출력]
    ↓
[MultimodalMessage에 chart 타입으로 첨부]
```

### 6.2 지원 차트 유형

| 카테고리 | 차트 유형 | 엔진 | V1 | V2 |
|---------|----------|------|----|----|
| 기본 | 바, 라인, 파이, 스캐터 | Plotly | O | O |
| 통계 | 히스토그램, 박스플롯, 히트맵 | Plotly | O | O |
| 금융 | 캔들스틱, OHLC | Plotly | O | O |
| 지리 | 코로플레스, 버블맵 | Plotly/D3 | - | O |
| 네트워크 | 노드-엣지 그래프 | D3.js | - | O |
| 다이어그램 | 플로우차트, 시퀀스, ER | Mermaid | O | O |

### 6.3 차트 생성 스키마

```typescript
interface ChartRequest {
  chart_type: string;
  data: Record<string, any>[];
  config: {
    title?: string;
    x_axis?: AxisConfig;
    y_axis?: AxisConfig;
    color_scheme?: string;        // "viridis", "plasma", "vamos_brand"
    width?: number;               // default 800
    height?: number;              // default 500
    interactive?: boolean;        // D3.js 인터랙티브 모드
    export_format: "svg" | "png" | "html";
  };
}
```

---

## 7. 멀티모달 검색 (크로스모달)

### 7.1 크로스모달 검색 아키텍처

```
[검색 쿼리 (텍스트/이미지)] → [쿼리 임베딩 생성]
    ↓
[벡터DB (Qdrant) 유사도 검색]
    ├─→ 텍스트 → 이미지 매칭 (CLIP text encoder)
    ├─→ 이미지 → 이미지 매칭 (CLIP vision encoder)
    ├─→ 이미지 → 텍스트 매칭 (OCR + semantic search)
    └─→ 오디오 → 텍스트 매칭 (STT + semantic search)
        ↓
[Re-ranking (Cross-Encoder)] → [결과 반환]
```

### 7.2 벡터 인덱스 설정

```python
# qdrant_multimodal_config.py
MULTIMODAL_COLLECTIONS = {
    "image_embeddings": {
        "vector_size": 768,          # CLIP ViT-L/14@336
        "distance": "Cosine",
        "on_disk": True,
        "quantization": "scalar",    # int8 양자화
        "payload_schema": {
            "conversation_id": "keyword",
            "created_at": "datetime",
            "caption": "text",
            "ocr_text": "text",
        }
    },
    "audio_embeddings": {
        "vector_size": 512,
        "distance": "Cosine",
    }
}
```

---

## 8. 비용/성능 관리

### 8.1 모달리티별 비용 추정 (월간 기준)

| 모달리티 | 일일 처리량 | 단가 | 월간 비용 (추정) |
|---------|-----------|------|---------------|
| 이미지 (Vision API) | 500건 | $0.005/건 | ~$75 |
| 이미지 (CLIP 임베딩) | 500건 | GPU $0.001/건 | ~$15 |
| OCR | 200건 | $0.0015/건 | ~$9 |
| STT (Whisper) | 60분 | GPU $0.002/분 | ~$3.6 |
| STT (Deepgram) | 60분 | $0.0043/분 | ~$7.7 |
| TTS | 30분 | $0.015/분 | ~$13.5 |
| 비디오 분석 | 10건 | $0.05/건 | ~$15 |
| **합계** | | | **~$140/월** |

### 8.2 성능 SLA

| 처리 유형 | 목표 지연시간 | P99 지연시간 | 최대 동시 처리 |
|----------|------------|------------|-------------|
| 이미지 CLIP 임베딩 | <500ms | <1s | 50 |
| OCR (단일 페이지) | <2s | <5s | 20 |
| STT (1분 오디오) | <3s | <8s | 10 |
| 비디오 프레임 추출 | <10s | <30s | 5 |
| 차트 생성 | <1s | <3s | 30 |
| 크로스모달 검색 | <200ms | <500ms | 100 |

### 8.3 비용 최적화 전략

```python
# cost_optimizer.py
class MultimodalCostPolicy:
    """계층적 비용 최적화"""
    rules = [
        # 1. 로컬 처리 우선
        Rule("OCR", prefer="tesseract", fallback="google_vision", threshold=0.7),
        # 2. 캐싱: 동일 이미지 재처리 방지
        Rule("CLIP", cache_ttl=86400, cache_key="sha256(image_bytes)"),
        # 3. 배치 처리: 비실시간 요청 묶기
        Rule("STT", batch_window_sec=30, max_batch_size=10),
        # 4. 해상도 자동 조절
        Rule("Vision", auto_resize=True, max_tokens_per_image=1024),
        # 5. 일일 예산 한도
        Rule("*", daily_budget_usd=10.0, alert_threshold=0.8),
    ]
```

---

## 9. 교차참조

| 참조 모듈 | 연관 항목 | 참조 방향 |
|----------|---------|----------|
| T2-CORE_AI (2-2) | LLM Router, 프롬프트 관리 | ← 사용 |
| T2-DATA_PIPELINE (2-3) | 데이터 인제스트, 벡터DB | ← 사용 |
| T3-PKM (3-3) | 멀티모달 지식 캡처 | → 제공 |
| T3-Education (3-5) | 교육 멀티미디어 콘텐츠 | → 제공 |
| T3-Health (3-6) | 감정 인식 (오디오/비주얼) | → 제공 |
| T4-Frontend (4-1) | 멀티모달 메시지 렌더링 | → 제공 |

---

*끝 — MULTIMODAL_PROCESSING 상세명세 v1.0.0*
