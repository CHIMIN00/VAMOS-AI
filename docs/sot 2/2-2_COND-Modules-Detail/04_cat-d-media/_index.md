# CAT-D: Media — 카테고리 인덱스

> **카테고리**: CAT-D (Media)
> **모듈 수**: 8개
> **Phase**: Phase 1 (작업 1-3, 2026-04-08 완료)
> **L-Level**: 8/8 = **L3** (구현 즉시 투입 가능)
> **Mixin**: `MediaMixin` (미디어 인코딩/디코딩, FFmpeg 래퍼, 이미지 처리 파이프라인)
> **Config Group**: `media_config` (ffmpeg_path, max_file_size_mb, supported_formats, gpu_acceleration)
> **의존성**: FFmpeg, Pillow, OpenCV, Whisper, Stable Diffusion, CLIP, pyannote, Tree-sitter
> **코드 디렉토리**: `vamos/modules/cat_d_media/`
> **LOCK 준수**: LOCK-CD-03 (BaseModule ABC), LOCK-CD-04 (Runnable), LOCK-CD-05/06 (ErrorHandlingStandard + VamosError 4필드), LOCK-CD-08 (NODE 독립 실행 불가), LOCK-CD-10 (ModuleConfig 5필드)
> **상위 인덱스**: [../COND_MODULES_종합명세.md](../COND_MODULES_종합명세.md) ⟦D-2 보수 2026-06-11: 구 `../_index.md`는 부재 파일(도메인 루트 _index 미운용 — 형제 7개 카테고리 인덱스 동일 컨벤션). 실존 마스터 명세로 교정⟧

---

## 모듈 목록

| # | 모듈 ID | 이름 | 우선순위 | L-Level | GPU | 핵심 백엔드 | 상세 파일 |
|---|---------|------|---------|---------|:---:|------------|----------|
| 1 | COND-016 | 멀티미디어 라이브러리 | HIGH | **L3** | 선택 | Pillow / OpenCV / FFmpeg | [cond_016_multimedia_library.md](cond_016_multimedia_library.md) |
| 2 | COND-080 | 스타일 트랜스퍼 | LOW | **L3** | **필수** | AdaIN / Gatys / CLIP-guided | [cond_080_style_transfer.md](cond_080_style_transfer.md) |
| 3 | COND-081 | 로고/아이콘 생성 | LOW | **L3** | **필수** | Stable Diffusion + potrace | [cond_081_logo_icon_gen.md](cond_081_logo_icon_gen.md) |
| 4 | COND-082 | 화자분리 (Diarization) | MEDIUM | **L3** | 권장 | pyannote + Whisper + ECAPA | [cond_082_speaker_diarization.md](cond_082_speaker_diarization.md) |
| 5 | COND-083 | 양식 자동생성 | MEDIUM | **L3** | 불필요 | Jinja2 + WeasyPrint + docxtpl | [cond_083_form_generation.md](cond_083_form_generation.md) |
| 6 | COND-084 | 크로스모달 검색 | MEDIUM | **L3** | 권장 | CLIP / BLIP-2 / ImageBind | [cond_084_cross_modal_search.md](cond_084_cross_modal_search.md) |
| 7 | COND-086 | 코드 변환 | MEDIUM | **L3** | 선택 | Tree-sitter + LLM polish | [cond_086_code_conversion.md](cond_086_code_conversion.md) |
| 8 | COND-109 | 인포그래픽 생성 | LOW | **L3** | 선택 | Vega-Lite + CairoSVG + LLM | [cond_109_infographic_gen.md](cond_109_infographic_gen.md) |

> **L-Level 기준** (§13): L0=이름만 / L1=I/O 스키마 / L2=알고리즘+에러 / L2+=L2+테스트골격 / **L3=구현 즉시 투입 가능 (8개 항목 모두 충족)**
> 8개 전수 §13.1 8개 항목(Input/Output Schema, Algorithm, Error Handling, Dependency Map, BaseModule ABC, Performance Benchmark(I-04), Integration Test Spec, Blue Node Integration) 작성 완료.

---

## 카테고리 특성

### 핵심 역할
CAT-D는 VAMOS의 미디어 처리 파이프라인을 담당한다. 이미지/오디오/비디오/문서의 기본 처리(COND-016), 생성형/스타일 변환(COND-080/081/109), 오디오 처리(COND-082), 문서 생성(COND-083), 크로스모달 검색(COND-084), 코드 변환(COND-086)을 포함한다. CAT-A(ML 추론)·CAT-B(VectorStore)·CAT-C(인프라)를 소비하며 모든 Blue Node에 미디어 능력을 제공한다.

### Blue Node 연동
- **주요 소비 Node**: Content Node, Creative Node (일부 Developer Node)
- **Permission Level**: P0~P1 혼합 (등록 자산은 P0, 사용자 입력/외부 모델 호출은 P1)
- **호출 패턴**: ORANGE CORE → Blue Node → `MediaMixin` → COND-D 모듈

### 의존 관계
- **CAT-D가 제공**: 미디어 전처리/변환/생성 결과 → CAT-A(ML 입력), Content/Creative Node
- **CAT-D가 소비**: CAT-A(ML 모델 추론 — CLIP, Whisper, SD), CAT-B(VectorStore), CAT-C(인프라)

### 교차 참조
- COND-084 (크로스모달 검색) → 3-2_Multimodal-Processing 통합 임베딩 공간
- COND-082 (화자분리) → 3-2_Multimodal-Processing 오디오 파이프라인 (ECAPA 공유)
- COND-086 (코드 변환) → 3-7_Developer-Tools-API-SDK 코딩 엔진 (Tree-sitter grammar 공유)
- COND-016 (멀티미디어 라이브러리) → 모든 미디어 모듈의 기반 IO 레이어

---

## 미디어 파이프라인 (입력 → 변환 → 출력)

```
                      ┌────────────────────────────────────────────────┐
                      │              Storage / Temp FS                 │
                      └──────────┬─────────────────────────┬───────────┘
                                 │ load                     │ save
                                 ▼                          ▲
   ┌─────────────────────────────────────────────────────────────────┐
   │                COND-016 멀티미디어 라이브러리 (HUB)              │
   │         Pillow · OpenCV · FFmpeg · librosa · python-magic       │
   │   (load / decode / resize / convert / extract metadata / save)  │
   └──┬─────┬────────┬──────────┬──────────┬──────────┬─────────┬───┘
      │     │        │          │          │          │         │
      ▼     ▼        ▼          ▼          ▼          ▼         ▼
  ┌──────┐ ┌──────┐ ┌──────┐ ┌─────────┐ ┌────────┐ ┌──────┐ ┌────────┐
  │ 080  │ │ 081  │ │ 082  │ │   083   │ │  084   │ │ 086  │ │  109   │
  │style │ │logo  │ │speakr│ │ form    │ │cross   │ │code  │ │info-   │
  │trans.│ │gen   │ │diariz│ │ gen     │ │modal   │ │conv. │ │graphic │
  │(GPU) │ │(GPU) │ │(GPU±)│ │ (CPU)   │ │(GPU±)  │ │(CPU±)│ │(CPU±)  │
  └──────┘ └──────┘ └──────┘ └─────────┘ └────┬───┘ └──────┘ └────────┘
                                              │
                                              ▼
                                    ┌──────────────────┐
                                    │  CAT-B Vector    │
                                    │     Store        │
                                    │ (Qdrant/pgvector)│
                                    └──────────────────┘
```

- **입력 포맷**: image (jpg/png/webp/svg/...), audio (wav/mp3/flac/...), video (mp4/mkv/...), document (pdf/docx/html/md), text/code
- **변환 체인**: COND-016이 모든 모듈의 IO 레이어로 동작 (디코딩·표준화·메타데이터 추출)
- **출력 포맷**: 모듈별 자체 정의, 모두 `MediaFile` 스키마로 통일하여 Blue Node에 반환
- **스트리밍 지원**: COND-016만 부분 지원 (FFmpeg `-ss/-t` stream copy). 080/081/082/084는 파일 단위 처리.

---

## GPU 활용 패턴 (Phase 1 신규)

| 모듈 | GPU 필수/선택 | 백엔드 | VRAM 권장 | CPU fallback |
|------|--------------|--------|----------|--------------|
| COND-016 | **선택** (옵션) | OpenCV CUDA 가속 | 1 GB | ✅ 기본값 |
| COND-080 | **필수** (권장) | torch + AdaIN/Gatys | 4~6 GB | ⚠️ 가능 (config로 활성화, 매우 느림) |
| COND-081 | **필수** | torch + diffusers | 6~8 GB | ❌ 외부 API 모드만 가능 |
| COND-082 | **권장** | torch + pyannote/Whisper | 4 GB | ✅ spectral + Whisper-small |
| COND-083 | **불필요** | WeasyPrint/Jinja2 (CPU 바운드) | — | — |
| COND-084 | **권장** | torch + CLIP/ImageBind | 2~4 GB | ✅ small-CLIP |
| COND-086 | **선택** (LLM 후보정 시 간접) | LLMOrchestrator 위임 | LLM 인스턴스 측 | ✅ AST 단독 모드 |
| COND-109 | **선택** (AI 레이아웃 시 간접) | LLMOrchestrator 위임 | LLM 인스턴스 측 | ✅ Static 레이아웃 |

### Fallback 전략 공통
- 모든 GPU 사용 모듈은 `gpu_device_id`, `require_gpu`, `allow_cpu_fallback`, `max_vram_mb` 4개 설정 필드 보유 (LOCK-CD-10 보완)
- `require_gpu=True` AND GPU 사용 불가 → 즉시 `COND_*_GPU_UNAVAILABLE` 반환 (LOCK-CD-05 결과 패턴)
- VRAM OOM 시 `COND_*_VRAM_OOM` 반환 — 사용자에게 해상도/길이 축소 fallback 메시지 제공

---

## LOCK 준수 매트릭스 (검증)

| 모듈 | LOCK-CD-03 (BaseModule ABC) | LOCK-CD-04 (Runnable) | LOCK-CD-05/06 (Result/VamosError) | LOCK-CD-10 (ModuleConfig 5필드) | LOCK-CD-08 (Independent X) |
|------|:---:|:---:|:---:|:---:|:---:|
| 016 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 080 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 081 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 082 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 083 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 084 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 086 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 109 | ✅ | ✅ | ✅ | ✅ | ✅ |
| **합계** | **8/8** | **8/8** | **8/8** | **8/8** | **8/8** |

> **예외 throw 0건**: 8개 모듈 전수 `Result<T, VamosError>` 적용. 모든 실패 경로에서 4필드(`failure_code, message, fallback_id, trace_id`) 채움 (LOCK-CD-06).
> **I-03 해결**: 8개 모듈 전체 VamosError 매핑 + 미디어 특화 FailureCode 등록 — 정식 등재는 §B.7.2 FailureCode Registry로 승격 예정.
> **FB_ID 네이밍 정합성**: 8개 모듈 전수 §B.7.2 표준 적용 — `FB_COND_REJECT` (입력/정책 거부), `FB_COND_SKIP` (외부/일시적 실패) 두 가지 일반 ID만 사용. 모듈명 누출 0건 (1-1/1-2 재검증 학습사항 사전 적용).
> **LOCK-CD-10 강제 검사**: 8개 모듈 전수 알고리즘 진입부에 `max_concurrent` 검사 + 종료부에 `timeout_ms` 검사 전수 적용 (`COND_*_QUOTA_EXCEEDED` / `COND_*_EXECUTE_TIMEOUT` 표준 코드).

### 미디어 특화 FailureCode 카테고리 (I-03)
| 카테고리 | 모듈 적용 | 대표 코드 |
|---------|----------|----------|
| 코덱/포맷 미지원 | 016, 080, 081, 082 | `COND_*_UNSUPPORTED_FORMAT`, `COND_016_CODEC_MISSING` |
| GPU 미사용 가능 | 080, 081, 082, 084 | `COND_*_GPU_UNAVAILABLE` |
| VRAM OOM | 080, 081, 082, 084 | `COND_*_VRAM_OOM` |
| 처리 시간 초과 | 8/8 | `COND_*_EXECUTE_TIMEOUT` |
| 동시 처리 한도 초과 | 8/8 | `COND_*_QUOTA_EXCEEDED` |
| 입력 크기 초과 | 016, 082, 086, 109 | `COND_*_TOO_LARGE`, `COND_*_TOO_LONG` |
| 모델 로드 실패 | 080, 081, 082, 084 | `COND_*_MODEL_LOAD_FAILED`, `COND_*_MODEL_NOT_AVAILABLE` |
| 정책/검열 차단 | 081 | `COND_081_PROMPT_BLOCKED` |

---

## 의존성 구조 (§A 참조)

### COND 내부 의존
- **HUB 모듈**: COND-016이 7개 모듈 모두의 IO 레이어로 작동 (필수 의존)
- **재사용 케이스**:
  - COND-080 → COND-016 (이미지 IO)
  - COND-081 → COND-016 (이미지 IO), COND-080 (스타일 후처리, 선택)
  - COND-082 → COND-016 (오디오 표준화)
  - COND-083 → COND-016 (출력 IO), COND-027 (i18n, 선택)
  - COND-084 → COND-016, **CAT-B VectorStore** (필수)
  - COND-086 → LLMOrchestrator (선택)
  - COND-109 → COND-016, COND-083 (PDF 위임), COND-081 (로고 합성), LLMOrchestrator (AI 레이아웃)
- §A.2(P0-1 매트릭스)는 CAT-A/B 범위라 미수록 → Phase 2 P2-1에서 CAT-D 내부 의존 매트릭스 정식 등록 권장. CONFLICT_LOG 추적 항목으로 기재 권장.

### I-Series 소비 (공통 4종)
8개 모듈 전수 **공통 4종 소비**: I-1 (Intent), I-5 (Decision), I-6 (Self-check), I-9 (Logging)
+ COND-082/084: I-19 (QoD) 선택 소비 (전사 신뢰도, 검색 품질)

---

## CAT-D 성능 벤치마크 기준 테이블 (I-04 해결)

> §6.2 I-04 (Phase 1: CAT별 성능 기준 테이블 작성) 충족.
> 모듈별 처리 시간 · GPU/VRAM · 해상도/포맷별 SLA 종합표.

### 모듈 단위 SLA 종합

| 모듈 | 핵심 SLA (p99) | VRAM peak | 처리량 | 가용성 |
|------|---------------|-----------|--------|--------|
| COND-016 | resize 4K→HD ≤ 200 ms / 인코딩 1 min 1080p ≤ 30 s | (CPU) | ≥ 5 동시 | 99.95 % |
| COND-080 | AdaIN 1024px ≤ 800 ms (GPU) / Gatys ≤ 15 s | ≤ 6 GB | 2/GPU | 99.5 % |
| COND-081 | PNG 4 variants 512px ≤ 8 s / SVG 1 variant ≤ 6 s | ≤ 8 GB | 1/GPU | 99.0 % |
| COND-082 | RTF ≤ 0.1 (pyannote+Whisper-medium GPU) | ≤ 6 GB | 2/GPU | 99.5 % |
| COND-083 | PDF 10p ≤ 800 ms / DOCX 10p ≤ 500 ms | (CPU) | ≥ 50 doc/s | 99.9 % |
| COND-084 | text→image ≤ 80 ms (CLIP GPU) / +rerank ≤ 100 ms | ≤ 4 GB | ≥ 200 q/s | 99.9 % |
| COND-086 | AST 200 LOC ≤ 200 ms / +LLM polish ≤ 4 s | (간접) | 8 / 2 (LLM) | 99.5 % |
| COND-109 | 1080×1920 PNG 5 sections ≤ 2.5 s / +AI layout ≤ 6 s | (간접) | 4 동시 | 99.5 % |

### 해상도/포맷별 처리 시간 기준

#### 이미지 처리 (COND-016, 080, 081)
| 작업 | 256px | 512px | 1024px | 2048px (4K은 016만) |
|------|:-----:|:-----:|:------:|:------:|
| 016 resize (CPU) | 30 ms | 60 ms | 120 ms | 200 ms (4K→HD) |
| 016 format convert (CPU) | 50 ms | 100 ms | 200 ms | 300 ms |
| 080 AdaIN (GPU) | 100 ms | 250 ms | 800 ms | 2.5 s |
| 080 Gatys (GPU) | 2 s | 5 s | 15 s | 60 s |
| 081 SD-turbo (GPU, 1 variant) | — | 2 s | 4 s | 12 s |

#### 오디오 처리 (COND-016, 082)
| 작업 | 1 min | 5 min | 30 min | 120 min |
|------|:----:|:-----:|:------:|:-------:|
| 016 WAV→MP3 (CPU) | 600 ms | 3 s | 18 s | 70 s |
| 082 pyannote (GPU) | 6 s | 30 s | 3 min | 12 min |
| 082 spectral (CPU) | 18 s | 90 s | 9 min | 36 min |
| 082 + Whisper-medium STT | +4 s | +20 s | +120 s | +480 s |

#### 비디오 처리 (COND-016)
| 작업 | 1 min 720p | 1 min 1080p | 5 min 1080p |
|------|:----------:|:-----------:|:-----------:|
| trim (stream copy) | 2 s | 2 s | 4 s |
| transcode H.264 CRF=23 | 12 s | 30 s | 150 s |
| metadata extract (FFprobe) | 50 ms | 50 ms | 50 ms |

#### 문서 처리 (COND-083, 109)
| 출력 | 5p A4 | 10p A4 | 50p A4 | 100p A4 |
|------|:-----:|:------:|:------:|:-------:|
| 083 PDF (WeasyPrint) | 400 ms | 800 ms | 3 s | 6 s |
| 083 DOCX (docxtpl) | 250 ms | 500 ms | 2 s | 4 s |
| 109 1080×1920 PNG (5 sec) | — | 2.5 s | — | — |
| 109 +AI layout | — | 6 s | — | — |

### 측정 표준
- **방법**: Prometheus histogram(`_bucket`, `_sum`, `_count`), 부하 시험은 k6/locust 기반
- **GPU 측정**: `torch.cuda.max_memory_allocated()`로 VRAM peak 기록 (각 모듈 E6 표 참조)
- **하드웨어 기준**: 측정 기준선은 NVIDIA RTX A4000 (16 GB) / Intel Xeon 16C / SSD NVMe
- **알람 임계**: 각 모듈 E4 FailureCode 표의 `*_EXECUTE_TIMEOUT`, `*_VRAM_OOM`, `*_QUOTA_EXCEEDED` 코드 트리거 시 발화
- **Retention**: 메트릭 30 d / 트레이스 7 d / 로그 30 d (운영 정책)
- **계측 공통 라벨**: `module_id`, `category=d`, `tenant`, `region`, `gpu_used`

---

## Blue Node 연동 (§B.6.1 패턴 적용)

> §B.6.1은 CAT-A 13개에 대한 P0-2 산출물. CAT-D는 동일 패턴(Permission, Gate, lower.dot 이벤트, LOCK-CD-08 독립 실행 불가)을 적용한다.

### 공통 사항
- **연동 Blue Node**: Content Node, Creative Node (일부 Developer Node — 086)
- **Permission Level**: P0~P1 혼합 — 등록 자산/시스템 호출은 P0, 사용자 입력/외부 모델/생성형은 P1
- **호출 패턴**: Blue Node 내부에서 `MediaMixin` 경유 자동 호출 — 직접 import 금지(LOCK-CD-08)
- **이벤트 매핑**: 8개 모듈 전수 6종 lifecycle 이벤트 발행 (`cond.d.{id}.{initialized|execute_start|execute_done|execute_fail|health|shutdown}`)
- **Decision 연계**: 각 모듈 실행 결과는 `Decision.optional_signals`에 `{cond_module_id, op, gpu_used, execution_time_ms, ...}` 기록 (§B.8)

### 모듈별 게이트 요구

| 모듈 | Permission | 추가 게이트 | 사유 |
|------|:---------:|------------|------|
| 016 | P1 | policy + cost (파일 크기) | 사용자 파일 처리 |
| 080 | P1 | policy + cost (GPU 시간) + approval(>4K) | 저작권/유해 스타일 차단 |
| 081 | P1 | policy + cost (GPU 시간/외부 API) + approval(>4 variants) | 브랜드/유해 검열 + 비용 발생 |
| 082 | P1 | policy + cost (오디오 길이) + approval(>30 min) + evidence | 개인 음성 데이터/녹취 동의 |
| 083 | P0/P1 | policy + evidence + approval(인라인 템플릿) | PII 출력 검열 |
| 084 | P0/P1 | policy + evidence + approval(개인 인덱스) | NSFW 필터 + 출처 추적 |
| 086 | P0/P1 | policy + evidence + approval(LLM 사용) + cost | 라이선스/저작권 + LLM 비용 |
| 109 | P1 | policy + evidence + approval(AI 레이아웃) + cost | 데이터 출처 + LLM 비용 |

### 이벤트 명명 일관성
- 8개 모듈 전수 `cond.d.{module_id}.{lifecycle}` lower.dot 규칙 준수 (§B.4)
- 016/080/081/082/083/084/086/109 = 6 lifecycle × 8 modules = **48개 이벤트 인스턴스**

---

## 검증 체크리스트 (§7.3 작업 1-3)

- [x] `04_cat-d-media/` 하위 8개 .md 파일 존재 (016, 080, 081, 082, 083, 084, 086, 109)
- [x] 8개 모듈 전수 BaseModule ABC(LOCK-CD-03) 4개 메서드 구조 준수 (`initialize / execute / health_check / shutdown`)
- [x] 8개 모듈 전수 Runnable Protocol(LOCK-CD-04) 위임 명시 (`execute → run`)
- [x] 8개 모듈 전수 ErrorHandlingStandard(LOCK-CD-05/06) 적용 — `Result<T, VamosError>`, 예외 throw 0건, 4필드 전수 — **미디어 특화 에러 경로(코덱/GPU/VRAM/타임아웃) 포함**
- [x] 8개 모듈 전수 ModuleConfig(LOCK-CD-10) 5개 필드 포함 (`enabled, priority, max_concurrent, timeout_ms, retry_policy`) + GPU 4필드 보완(`gpu_device_id, require_gpu, allow_cpu_fallback, max_vram_mb`)
- [x] **미디어 파이프라인 정합성 검증** — 모듈 간 입출력 포맷 일치 (COND-016 HUB 표준, `MediaFile` 스키마 통일)
- [x] **GPU 활용 기준 정의 완료** (필수/선택, fallback 전략) — 위 GPU 활용 패턴 표 참조
- [x] `04_cat-d-media/_index.md` 완성 (본 문서)
- [x] **성능 벤치마크 기준 테이블 포함 (I-04)**: 모듈 단위 SLA + 해상도별/포맷별 처리 시간 종합표
- [x] **§6.2 I-03 해결** — 8개 모듈 전체 VamosError 매핑 + 미디어 특화 failure_code 모듈별 등록 (§B.7.2 FailureCode Registry 승격 예정)
- [x] **§6.2 I-04 해결** — CAT-D 성능 벤치마크 종합표 작성 (해상도별·포맷별 목표값)
- [x] §7 Phase 1 전환 게이트 (CAT-C/D 전체 _index.md 완성 + 성능 벤치마크 테이블 완성) 충족

---

## 후속 작업 연결

- **1-1** (CAT-C Core 14개) ✅ 완료 (2026-04-07)
- **1-2** (CAT-C E-series 39개) ✅ 완료 (2026-04-08)
- **1-3** (CAT-D Media 8개) ✅ **본 작업 (2026-04-08)**
- **Phase 1 전환 게이트** (§7): CAT-C/D _index 완성 + 성능 벤치마크 테이블 완성 → **충족**
- **Phase 2** P2-1: CAT-D 내부 의존성 매트릭스 정식 등록 — COND-016 HUB 관계 + COND-109 ↔ 083/081 합성 의존
- **종합계획서 §7 갱신**: 1-3 작업 결과는 §7.3 (Phase 1) 표 상태 컬럼 갱신 필요 (별도 세션 — `feedback_session_summary_update` 양식)
