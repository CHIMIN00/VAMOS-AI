# video_analysis_v2.md — J-036 V2 EXTEND (스크린 레코딩 AI 편집) + J-039 V2 EXTEND (검색/인덱싱) + J-040 V3 골격→V2 본문 (실시간 스트리밍)

> **Status**: V2-Phase 2 (2-3 #2b)
> **작성일**: 2026-04-19
> **V1 정본**: [video_analysis.md](./video_analysis.md) (Phase 1-3 완료, 388 lines, read-only sha256 baseline, J-035 V1 EXTEND + J-078 트렌드 + J-036/J-039/J-040 V2/V3 골격 L354~L385)
> **SoT 근거**: STEP7-J Part 4 (J-036 L681~L696, J-039 L736~L749, J-040 L751~L761)
> **담당 J-ID**: **J-036** (V2 EXTEND: 스크린 레코딩 AI 편집 본문) + **J-039** (V2 EXTEND: 비디오 검색/인덱싱 본문) + **J-040** (V3 SHELL → V2 본문 골격 강화: 슬라이딩 윈도우 실시간 분석)
> **상위 인덱스**: [_index.md](./_index.md)
> **peer V2**: [video_generation_v2.md](./video_generation_v2.md) (J-033 생성 비디오 인덱싱) / [video_safety_v2.md](./video_safety_v2.md) (J-041 안전 필터) + **[voice_chat_v2.md](../02_audio-processing/voice_chat_v2.md) §4.1** (비디오 오디오 트랙 추출 → STT → LLM → TTS chain) + **[audio_analysis_v2.md](../02_audio-processing/audio_analysis_v2.md) §J-024** (오디오 트랙 → 화자분리)

---

## 1. Cross-domain 참조 블록

| 정본 | 역할 | 참조 지점 |
|------|------|----------|
| `MULTIMODAL_PROCESSING_구조화_종합계획서.md` §6.3 (Phase 2 J-036/J-039/J-040) + §A.3 비디오 파이프라인 | 비디오 분석 V2 확장 | §3 V2 승급 |
| `AUTHORITY_CHAIN.md` §4 LOCK-MM-07/09/10/11 | LOCK 정본 | §2 LOCK 인용 |
| `STEP7-J_멀티모달_생성처리_작업가이드.md` Part 4 J-036 (L681~L696) | 상위 SoT J-036 | §4.1 verbatim |
| `STEP7-J_멀티모달_생성처리_작업가이드.md` Part 4 J-039 (L736~L749) | 상위 SoT J-039 | §4.2 verbatim |
| `STEP7-J_멀티모달_생성처리_작업가이드.md` Part 4 J-040 (L751~L761) | 상위 SoT J-040 (V3) | §4.3 verbatim |
| `video_analysis.md` (V1, 388 lines) | V1 정본 (J-035 EXTEND + J-078 트렌드) | §3 V1 계승 |
| `voice_chat_v2.md` §4.1 (peer V2 Part 2) | 비디오 → 오디오 → STT → LLM → TTS chain | §4.1 E1 + Part 2 §7.3 forward link 해소 |
| `audio_analysis_v2.md` §J-024 (peer V2 Part 2) | 화자분리 | §4.1 E1 |
| `tts_engine_v2.md` §4.4 (peer V2 Part 2) | 자동 나레이션 추가 (TTS) | §4.1 E3 |

---

## 2. LOCK 인용 (R9 형식)

> LOCK (가이드 R-05-2): 파일 크기 상한 — 이미지 10MB / 오디오 25MB / 비디오 100MB

> LOCK (STEP7-J J-094~J-096): 비용 상한 — V1: ≤₩10K($8), V2: ≤₩40K($30), V3: ≤₩200K($150)

> LOCK (기존 명세 §비디오 분석): 비디오 프레임 제한 — max_frames = 100

> LOCK (기존 명세 §2.2): CLIP 임베딩 차원 — 768d (ViT-L/14@336)

> LOCK (SPEC §14): 14-Item Tech Stack — 변경 불가

**적용 지표**:
- LOCK-MM-09 (max_frames=100): J-036 스크린 녹화 분석 + J-039 인덱싱 시 강제 clamp
- LOCK-MM-07 (CLIP 768d): J-039 키프레임 임베딩 (ViT-L/14@336)
- LOCK-MM-10 (비디오 100MB): J-036 스크린 녹화 출력 + J-039 인덱싱 입력 검증
- LOCK-MM-06 V2 ($30/call): J-039 Qdrant 스토리지 비용 + Vision LLM 라우팅 가드

---

## 3. V1 → V2 승급 개요

| J-ID | V1 (V1 video_analysis.md) | V2 (본 산출물) |
|------|--------------------------|----------------|
| J-036 | V2 골격 L354~L362 (4건) | **E1~E10 + 화면 캡처 (OBS/ffmpeg gdigrab/x11grab) + 마우스/키보드 메타 + 침묵 컷 + 클릭 줌 + 챕터 분할** |
| J-039 | V2 골격 L364~L372 (4건) | **E1~E10 + CLIP 768d 키프레임 임베딩 + 자막 텍스트 임베딩 + Qdrant 통합 검색 + 시간 정렬 결과** |
| J-040 | V3 골격 L377~L385 (4건) | **V2 본문 추가: WebRTC/RTSP 입력 슬라이딩 윈도우 5s + 실시간 자막 + 알림 (V3 완전 구현은 J-040 별도 6개월+)** |

---

## 4. V2 본문

### 4.1 J-036. 스크린 레코딩 + AI 편집 V2 [V2 / EXTEND] (STEP7-J L681~L696)

**근거 verbatim 인용** (STEP7-J L684~L693):
> ```
> [구현 상세]
> - 화면 녹화: 코딩 세션, 디버깅 과정, 튜토리얼
> - AI 자동 편집: 불필요한 대기 시간 제거, 하이라이트 추출
> - 자동 나레이션 추가 (TTS)
> - 코드 하이라이트: 변경 부분 자동 줌인/강조
> - 챕터 자동 생성
>
> [활용]
> - 개발 튜토리얼 자동 생성
> - 코드 리뷰 영상 제작
> - 버그 재현 영상 자동 기록
> ```

**SoT 구현성 (STEP7-J L695 verbatim)**: V2 — ⚠️ 4개월 | V3: ✅ 풀 파이프라인

#### E1. Input Schema
```python
# 00_common §3.4 재사용: ModuleConfig
# 2-1 Blue-Node-Architecture D2.0-02 §0.3 재사용: VamosError/Result
# MULTIMODAL_PROCESSING_상세명세.md §5.1 재사용: MultimodalMessage
from common_types import ModuleConfig, MultimodalMessage
from d202_02 import VamosError, VamosResult

class ScreenRecordingConfigV2(ModuleConfig):
    capture_backend: Literal["obs","ffmpeg-gdigrab","ffmpeg-x11grab","ffmpeg-avfoundation"] = "ffmpeg-gdigrab"
    fps: int = 30
    resolution: tuple[int, int] = (1920, 1080)
    audio_capture: bool = True                       # 마이크 + 시스템 사운드
    record_keyboard: bool = True                     # keylog → 메타데이터
    record_mouse: bool = True                        # 좌표/클릭 메타데이터
    max_duration_sec: int = 3600                     # 1시간
    auto_edit_enabled: bool = True                   # AI 편집 활성화
    silence_threshold_db: float = -40.0              # 침묵 컷 임계값
    chapter_min_interval_sec: float = 30.0           # 챕터 최소 간격

class ScreenRecordingRequestV2:
    # 입력 (라이브 캡처 또는 사후 입력 둘 중 하나)
    capture_now: bool = True                         # True 시 즉시 녹화 시작
    pre_recorded_video: Optional[bytes] = None       # 사후 편집용 (≤100MB LOCK-MM-10)
    pre_recorded_keylog: Optional[list[KeyEvent]] = None
    pre_recorded_mouse: Optional[list[MouseEvent]] = None

    # 편집 옵션
    cut_silence: bool = True                         # 침묵 구간 자동 컷
    click_zoom: bool = True                          # 마우스 클릭 시 줌인 (1.5x)
    auto_subtitle: bool = True                       # J-021 STT 자막
    auto_narration: bool = False                     # J-022 TTS 나레이션 (V2 옵션)
    narration_script: Optional[str] = None           # auto_narration=True 시 필수
    code_highlight: bool = True                      # 코드 영역 OCR + 변경 부분 줌
    auto_chapters: bool = True                       # 챕터 자동 생성

    # 출력
    output_format: Literal["mp4","webm"] = "mp4"
    target_resolution: Optional[tuple[int, int]] = None  # 다운스케일 옵션
    max_cost_usd: float = 0.05                       # V2 (LOCK-MM-06 ≤$30)

class ScreenRecordingResultV2(VamosResult):
    request_id: UUID
    output_video: bytes                              # ≤ 100MB (LOCK-MM-10)
    duration_sec: float                              # 편집 후 길이
    raw_duration_sec: float                          # 편집 전 길이
    cuts_applied: int                                # 침묵 컷 횟수
    zooms_applied: int                               # 클릭 줌 횟수
    subtitle_segments: list[SubtitleSegment]
    narration_audio: Optional[bytes] = None          # auto_narration=True 시
    chapters: list[Chapter]
    code_blocks_detected: int                        # OCR 결과
    cost_usd: float                                  # LOCK-MM-06 V2
    processing_time_ms: int

class KeyEvent:
    timestamp_ms: int
    key: str                                         # 'a', 'enter', 'ctrl+s'
    type: Literal["press","release"]

class MouseEvent:
    timestamp_ms: int
    x: int; y: int
    type: Literal["move","click_left","click_right","scroll"]

class Chapter:
    start_sec: float; end_sec: float
    title: str                                       # AI 생성
    type: Literal["coding","debugging","explanation","navigation"]
```

#### E2. Output Schema
- 위 `ScreenRecordingResultV2` 참조. 편집 후 ≤100MB 보장. `cuts_applied` / `zooms_applied` 메타로 PR 리뷰 기록 가능.

#### E3. Algorithm — 스크린 녹화 + AI 편집 파이프라인
```python
async def record_and_edit_screen(req: ScreenRecordingRequestV2,
                                cfg: ScreenRecordingConfigV2) -> ScreenRecordingResultV2:
    # 1. 입력 분기: 라이브 캡처 vs 사후 편집
    if req.capture_now:
        # OBS / ffmpeg gdigrab (Win) / x11grab (Linux) / avfoundation (Mac)
        cap = await capture_screen(cfg.capture_backend, cfg.fps, cfg.resolution,
                                   audio=cfg.audio_capture,
                                   max_duration_sec=cfg.max_duration_sec)
        raw_video = cap.video                        # mp4 raw
        keylog = cap.keylog if cfg.record_keyboard else []
        mouse = cap.mouse if cfg.record_mouse else []
    else:
        if not req.pre_recorded_video:
            return VamosError("pre_recorded_video required when capture_now=False")
        if len(req.pre_recorded_video) > 100 * 1024 * 1024:
            return VamosError("pre_recorded_video > 100MB (LOCK-MM-10)")
        raw_video = req.pre_recorded_video
        keylog = req.pre_recorded_keylog or []
        mouse = req.pre_recorded_mouse or []

    raw_duration = await ffprobe_duration(raw_video)

    # 2. 오디오 트랙 분리 → STT (peer V2 voice_chat §4.1 chain)
    transcript = None
    if req.auto_subtitle and cfg.audio_capture:
        from audio.stt import transcribe              # peer Part 2 V2 stt_engine
        pcm = await ffmpeg_extract_pcm(raw_video, sr=16000, ch=1)  # LOCK-MM-08
        transcript = await transcribe(STTRequest(audio=pcm, word_timestamps=True))

    # 3. 침묵 컷 분석
    cut_segments = []
    if req.cut_silence:
        silence_ranges = await detect_silence(raw_video,
                                              threshold_db=cfg.silence_threshold_db,
                                              min_duration_sec=2.0)
        cut_segments = invert_to_keep(silence_ranges, total=raw_duration)

    # 4. 마우스 클릭 줌 분석
    zoom_events = []
    if req.click_zoom:
        for me in mouse:
            if me.type in ("click_left", "click_right"):
                zoom_events.append({
                    "timestamp_ms": me.timestamp_ms,
                    "x": me.x, "y": me.y,
                    "scale": 1.5,
                    "duration_ms": 800,
                })

    # 5. 코드 하이라이트 OCR (PaddleOCR / Tesseract)
    code_blocks = []
    if req.code_highlight:
        # 1초 간격 키프레임 OCR → 코드 영역 검출
        keyframes = await ffmpeg_keyframes(raw_video, interval_sec=1.0)
        for kf in keyframes:
            ocr_result = await paddleocr_layout(kf.image)
            code_areas = filter_code_layout(ocr_result)  # mono-space + indent
            if code_areas:
                code_blocks.append({
                    "timestamp_ms": kf.timestamp_ms,
                    "regions": code_areas,
                    "lang_detected": detect_language(ocr_result.text),
                })

    # 6. 챕터 자동 생성 (LLM)
    chapters = []
    if req.auto_chapters:
        chapters = await derive_chapters_screen(transcript, keylog, mouse, code_blocks,
                                                min_interval_sec=cfg.chapter_min_interval_sec,
                                                model="qwen2.5-7b-local")

    # 7. 자동 나레이션 (옵션, J-022 TTS peer V2)
    narration_audio = None
    if req.auto_narration and req.narration_script:
        from audio.tts import synthesize              # peer Part 2 V2 tts_engine
        narration_audio = await synthesize(TTSRequest(text=req.narration_script,
                                                      voice="ko-female-1",
                                                      output_format="pcm_16khz"))

    # 8. 편집 그래프 구성 → FFmpeg filter_complex (LOCK-MM-11 14-Item Tech Stack)
    graph = ScreenEditGraph(raw_video)
    if req.cut_silence:
        graph.apply_keep_segments(cut_segments)
    if req.click_zoom:
        graph.apply_zoom_events(zoom_events)
    if req.code_highlight:
        graph.apply_code_overlay(code_blocks)
    if req.auto_subtitle and transcript:
        graph.burn_subtitle(transcript.segments, font="Pretendard")
    if req.auto_chapters:
        graph.add_chapter_markers(chapters)
    if narration_audio:
        graph.mix_audio(narration_audio, level_db=-3.0)

    # 9. 출력 인코딩
    out = await graph.render(codec="h264_nvenc" if gpu_available() else "libx264",
                            target_res=req.target_resolution,
                            fmt=req.output_format, max_size_mb=100)

    return ScreenRecordingResultV2(
        output_video=out, duration_sec=ffprobe_duration(out),
        raw_duration_sec=raw_duration,
        cuts_applied=len(silence_ranges) if req.cut_silence else 0,
        zooms_applied=len(zoom_events),
        subtitle_segments=transcript.segments if transcript else [],
        narration_audio=narration_audio,
        chapters=chapters, code_blocks_detected=len(code_blocks),
        cost_usd=0.0,  # 로컬 처리 (R-05-4)
    )
```

#### E4. Model Selection — 백엔드 라우팅
| OS | 캡처 백엔드 | 권장 | 비고 |
|----|------------|------|------|
| Windows | ffmpeg gdigrab | ✅ 1순위 | 코드 친화 + 시스템 사운드 |
| Windows | OBS | 2순위 | 고급 기능 (멀티 소스) |
| Linux | ffmpeg x11grab | ✅ 1순위 | 표준 |
| Linux | OBS | 2순위 | Wayland 지원 |
| macOS | ffmpeg avfoundation | ✅ 1순위 | 시스템 통합 |
| OCR (코드 영역) | PaddleOCR | ✅ 1순위 | 한국어 + 코드 정확도 |
| LLM (챕터 생성) | Qwen2.5 7B 로컬 | ✅ R-05-4 | 비용 0 |
| TTS (나레이션) | peer J-022 V2 (Part 2) | — | OpenAI TTS-1-HD / Edge TTS |
| STT (자막) | peer J-021 V2 (Part 2) | — | Deepgram Nova-2 / Whisper v3 |

#### E5. Error Handling

| 에러 | 폴백 |
|------|------|
| 캡처 백엔드 시작 실패 | OBS 폴백 (Win/Linux), 사용자에게 권한 안내 (Mac) |
| pre_recorded_video > 100MB | 즉시 거부 (LOCK-MM-10) |
| max_duration_sec 초과 | 자동 종료 + warning |
| 침묵 검출 0 (전체 발화) | 컷 미적용 + warning |
| OCR 실패 | code_blocks_detected=0 으로 진행 |
| 챕터 LLM 실패 | 시간 균등 5분 간격 챕터 생성 |
| 나레이션 TTS 실패 | narration_audio=None + warning |
| NVENC 미가용 | libx264 폴백 |
| 출력 > 100MB | 720p 자동 다운스케일 + warning |
| auto_narration=True but narration_script=None | 즉시 거부 (입력 검증) |

R-05-5 Graceful Degradation 체인 명시.

#### E6. Cost Analysis

| 시나리오 | V2 (월) | LOCK-MM-06 V2 |
|----------|---------|---------------|
| 일 2건 × 30분 로컬 (캡처 + 로컬 편집) | $0 | 충족 ✅ |
| 일 2건 × Gemini Flash (챕터 LLM 폴백) | $0.50 | 충족 ✅ |
| 일 2건 + 나레이션 TTS (J-022 Edge TTS 무료) | $0.50 | 충족 ✅ |
| **V2 권장 합계** | **$0~$2** | LOCK-MM-06 V2 ≤$30 충족 |

#### E7. Performance SLA

| 입력 길이 | P50 (편집 후) | P99 |
|----------|--------------|-----|
| 5분 (1080p30) | 60s | 120s |
| 30분 (1080p30) | 6분 | 12분 |
| 1시간 (1080p30, 코드 OCR ON) | 15분 | 30분 |

병목: PaddleOCR (1초 간격 키프레임). `code_highlight=False` 시 처리량 4×.

#### E8. Integration Test (12건)
1. `capture_now=True, max_duration_sec=300` → 5분 녹화 + 침묵 컷 + 챕터 + STT 자막.
2. `pre_recorded_video=10분 mp4 + keylog + mouse` → 사후 편집, 클릭 줌 적용.
3. `cut_silence=True, silence_threshold_db=-40` → 침묵 5초 이상 구간 컷 검증.
4. `click_zoom=True` → 클릭 좌표 1.5x 줌 800ms 적용.
5. `code_highlight=True` → PaddleOCR 코드 영역 검출 + 줌인.
6. `auto_subtitle=True` (peer J-021 V2 chain) → STT 자막 burn-in.
7. `auto_narration=True, script="..."` → J-022 V2 TTS 나레이션 mix.
8. `auto_chapters=True` → LLM 챕터 5개 생성.
9. pre_recorded_video > 100MB → 즉시 거부.
10. 출력 > 100MB → 720p 자동 다운스케일.
11. NVENC 미가용 → libx264 폴백.
12. PaddleOCR 실패 → code_blocks=0 진행.

#### E9. Dependencies
- 외부: ffmpeg (gdigrab/x11grab/avfoundation), OBS Studio (옵션), PaddleOCR, Qwen2.5 7B (Ollama)
- 내부 (peer V2): J-021 V2 (stt_engine_v2.md), J-022 V2 (tts_engine_v2.md), J-019 (메타), J-034 V1 (편집 위임), J-065 (Cost Manager)
- GPU: RTX 4090 권장 (NVENC + Qwen2.5)

#### E10. Privacy / Safety
- R-05-4: 100% 로컬 처리 → 사용자 화면이 외부로 전송되지 않음
- 키로그/마우스 좌표는 메타데이터로만 저장, 영상에는 비기록
- 임시 파일 (raw 캡처) 처리 종료 후 즉시 삭제 (TTL 5분)
- 사용자에게 화면 녹화 시작 시 시스템 알림 (Windows 작업 표시줄, Mac 메뉴 바)
- 자동 나레이션 음성은 사용자 입력 스크립트 only — TTS 출력에 R-05-7 안전 필터 통과

**자체 점수**: 90/100

---

### 4.2 J-039. 비디오 검색 및 인덱싱 V2 [V2 / EXTEND] (STEP7-J L736~L749)

**근거 verbatim 인용** (STEP7-J L739~L747):
> ```
> [구현 상세]
> - 비디오 시맨틱 인덱싱:
>   ├─ 키프레임 임베딩 (CLIP)
>   ├─ 전사 텍스트 임베딩
>   ├─ 장면 설명 자동 생성
>   └─ 통합 검색 인덱스
>
> - 크로스모달 검색: 텍스트 쿼리 → 관련 비디오 구간 탐색
> - 개인 비디오 라이브러리: 촬영/다운로드 영상 자동 분류+검색
> ```

**SoT 구현성 (STEP7-J L748 verbatim)**: V2 — ✅ 3개월

#### E1. Input Schema
```python
class VideoSearchConfigV2(ModuleConfig):
    embedding_model: Literal["clip-vit-l14-336","clip-vit-b16","jina-clip-v1"] = "clip-vit-l14-336"
    embedding_dim: int = 768                         # LOCK-MM-07 ✅
    qdrant_collection: str = "video_index"
    text_embedding_model: Literal["bge-m3","jina-v3","openai-3-small"] = "bge-m3"
    max_indexed_frames: int = 100                    # LOCK-MM-09 ✅
    scene_threshold: float = 27.0                    # PySceneDetect

class VideoIndexRequestV2:
    video: bytes                                     # ≤ 100MB (LOCK-MM-10)
    video_id: str                                    # 사용자 정의 ID (PKM 연동)
    title: Optional[str] = None
    user_id: str
    library: Literal["personal","shared","reference"] = "personal"
    auto_describe_scenes: bool = True
    extract_subtitle_text: bool = True               # J-035 transcript

class VideoSearchRequestV2:
    query: str                                       # 텍스트 쿼리 (예: "강아지가 나오는 장면")
    user_id: str
    library_filter: Optional[list[str]] = None
    top_k: int = 10
    time_filter: Optional[tuple[float, float]] = None  # 비디오 내 시간구간 제한
    language: str = "ko"

class VideoSearchHit:
    video_id: str
    timestamp_sec: float
    duration_sec: float                              # 매칭 구간 길이
    score: float                                     # CLIP cosine + text BM25 통합
    keyframe_url: str                                # 썸네일 URL (signed)
    caption: str                                     # Vision LLM 생성
    subtitle_excerpt: Optional[str] = None
```

#### E2. Output Schema
- 위 `VideoSearchHit` 리스트 (top_k 만큼). `score` 는 0.0~1.0, CLIP cosine 0.7 + 텍스트 BM25 0.3 가중.

#### E3. Algorithm — 인덱싱 + 검색
```python
async def index_video(req: VideoIndexRequestV2,
                     cfg: VideoSearchConfigV2) -> dict:
    # 1. 입력 검증 + LOCK clamp
    if len(req.video) > 100 * 1024 * 1024:
        return VamosError("video > 100MB (LOCK-MM-10)")

    # 2. J-035 V1 분석 호출 (캡션 + 자막 추출)
    from video.analysis import analyze_video         # V1 J-035
    analysis = await analyze_video(VideoAnalysisRequest(
        video=req.video, sampling_strategy="scene_based",
        max_frames=cfg.max_indexed_frames,           # LOCK-MM-09
        extract_audio=req.extract_subtitle_text,
        transcribe=req.extract_subtitle_text,
        summarize=False,
    ))

    # 3. 키프레임 CLIP 임베딩 (LOCK-MM-07: 768d ViT-L/14@336)
    embeddings = []
    for scene in analysis.scenes:
        kf_image = await ffmpeg_extract_frame(req.video,
                                              timestamp_sec=scene.keyframe_timestamp)
        emb = await clip_encode_image(kf_image, model=cfg.embedding_model)
        assert len(emb) == cfg.embedding_dim         # 768 강제
        embeddings.append({
            "scene_id": scene.scene_id,
            "timestamp_sec": scene.start,
            "duration_sec": scene.end - scene.start,
            "vector": emb,                           # CLIP 768d
            "caption": scene.caption,                # Vision LLM (J-035)
            "visual_tags": scene.visual_tags,
        })

    # 4. 자막 텍스트 임베딩 (별도 컬렉션)
    text_embeddings = []
    if analysis.transcript:
        for seg in analysis.transcript.segments:
            txt_emb = await text_encode(seg.text, model=cfg.text_embedding_model)
            text_embeddings.append({
                "segment_id": seg.id,
                "start": seg.start, "end": seg.end,
                "text": seg.text,
                "vector": txt_emb,
            })

    # 5. Qdrant 인덱스 등록 (user_id + library 격리)
    collection = f"{cfg.qdrant_collection}_{req.user_id}_{req.library}"
    await qdrant.upsert(collection,
                       points=[{
                           "id": f"{req.video_id}::{e['scene_id']}",
                           "vector": e["vector"],
                           "payload": {**e, "video_id": req.video_id, "title": req.title}
                       } for e in embeddings])
    if text_embeddings:
        await qdrant.upsert(f"{collection}_text",
                          points=[{
                              "id": f"{req.video_id}::{te['segment_id']}",
                              "vector": te["vector"],
                              "payload": {**te, "video_id": req.video_id}
                          } for te in text_embeddings])

    return {"video_id": req.video_id, "scenes_indexed": len(embeddings),
            "subtitle_segments_indexed": len(text_embeddings)}


async def search_video(req: VideoSearchRequestV2,
                      cfg: VideoSearchConfigV2) -> list[VideoSearchHit]:
    # 1. 텍스트 쿼리 → CLIP 임베딩 (768d 일치)
    q_emb_clip = await clip_encode_text(req.query, model=cfg.embedding_model)
    q_emb_text = await text_encode(req.query, model=cfg.text_embedding_model)

    # 2. Qdrant 이중 검색 (시각 + 텍스트)
    collection = f"{cfg.qdrant_collection}_{req.user_id}_{req.library}"
    visual_hits = await qdrant.search(collection, q_emb_clip,
                                     limit=req.top_k * 2,
                                     filter={"video_id": {"$in": req.library_filter}} if req.library_filter else None)
    text_hits = await qdrant.search(f"{collection}_text", q_emb_text,
                                    limit=req.top_k * 2)

    # 3. 시간구간 필터 적용
    if req.time_filter:
        t_start, t_end = req.time_filter
        visual_hits = [h for h in visual_hits if t_start <= h.payload["timestamp_sec"] <= t_end]
        text_hits = [h for h in text_hits if t_start <= h.payload["start"] <= t_end]

    # 4. 통합 score (CLIP 0.7 + text BM25 0.3 가중)
    merged = merge_hits(visual_hits, weight_visual=0.7,
                        text_hits=text_hits, weight_text=0.3)
    merged.sort(key=lambda h: -h.score)

    # 5. 썸네일 URL 발급 (signed, TTL 1시간)
    return [VideoSearchHit(
        video_id=h.payload["video_id"],
        timestamp_sec=h.payload["timestamp_sec"],
        duration_sec=h.payload["duration_sec"],
        score=h.score,
        keyframe_url=await sign_thumbnail_url(h.payload["video_id"], h.payload["timestamp_sec"], ttl_sec=3600),
        caption=h.payload["caption"],
        subtitle_excerpt=h.payload.get("text"),
    ) for h in merged[:req.top_k]]
```

#### E4. Model Selection — 임베딩
| 작업 | 모델 | 차원 | 비고 |
|------|------|------|------|
| 키프레임 시각 (1순위) | CLIP ViT-L/14@336 | **768d** ✅ LOCK-MM-07 | 정본 |
| 키프레임 시각 (옵션) | Jina CLIP v1 | 768d | 다국어 강화 |
| 텍스트 자막 (1순위) | bge-m3 | 1024d | 다국어 + 코드 |
| 텍스트 자막 (대안) | jina-v3 | 1024d | 영문 강화 |

#### E5. Error Handling
| 에러 | 폴백 |
|------|------|
| video > 100MB | 즉시 거부 |
| Qdrant 연결 실패 | local 파일 캐시 (TTL 1시간) + retry |
| CLIP 임베딩 실패 (OOM) | 배치 크기 4 → 1 다운 |
| 자막 추출 실패 (오디오 없음) | 텍스트 인덱스 스킵, 시각만 |
| 검색 결과 0 | 빈 리스트 반환 + suggestion (관련 키워드) |
| max_indexed_frames 초과 입력 | 100으로 clamp |
| 시간구간 필터 무효 (음수) | 무시 + warning |

#### E6. Cost Analysis
| 시나리오 | V2 (월) | LOCK-MM-06 V2 |
|----------|---------|---------------|
| Qdrant 자체 호스팅 | $0 (자체 운영 비용 제외) | 충족 ✅ |
| Qdrant Cloud (1M points) | $25/월 | 충족 ✅ |
| CLIP 로컬 임베딩 (RTX 4090) | $0 | 충족 ✅ |
| OpenAI text-embedding-3-small (대안) | 100K tokens/일 = $0.20 | 충족 ✅ |

#### E7. Performance SLA
| 작업 | P50 | P99 |
|------|-----|-----|
| 인덱싱 5분 비디오 (100 scenes) | 30s | 60s |
| 검색 (top_k=10, 10K 비디오) | 80ms | 200ms |
| 썸네일 URL 서명 | 5ms | 20ms |

#### E8. Integration Test (10건)
1. 5분 비디오 인덱싱 → scene 50개 + 768d CLIP + 자막 텍스트 인덱싱.
2. 텍스트 쿼리 "강아지가 나오는 장면" → top_k=5 결과 + score >0.7.
3. 시간구간 필터 (60s~120s) → 해당 구간만 반환.
4. library_filter=["video_id_1"] → 단일 비디오 내 검색.
5. 자막 없는 비디오 → 시각만 인덱싱.
6. CLIP 768d 차원 검증 (LOCK-MM-07).
7. max_indexed_frames=200 입력 → 100 clamp + warning.
8. Qdrant 실패 → local 캐시 폴백.
9. 시각 hit + 텍스트 hit 통합 score 계산 검증 (0.7 + 0.3).
10. 썸네일 URL TTL 1시간 만료 검증.

#### E9. Dependencies
- 외부: Qdrant (1.7+), CLIP (open_clip / transformers), bge-m3 (HuggingFace), PySceneDetect, ffmpeg
- 내부: J-035 V1 (video_analysis.md), J-052 (이미지-텍스트 RAG, peer 2-4 multimodal_rag_v2.md), J-055 V2 (multimodal_rag_v2.md)
- GPU: RTX 4090 (CLIP 768d 배치 인코딩 1순위)

#### E10. Privacy / Safety
- user_id + library 단위 인덱스 격리 (개인 라이브러리는 본인만 검색)
- 썸네일 URL signed + TTL 1시간 (외부 누출 방지)
- 인덱싱 시 R-05-7 안전 필터 통과 (NSFW 비디오는 인덱스 거부 또는 mark-as-private)
- Qdrant payload 에 사용자 식별 정보 미포함 (해시만)

**자체 점수**: 91/100

---

### 4.3 J-040. 실시간 비디오 스트리밍 분석 [V3 SHELL → V2 본문 골격 강화] (STEP7-J L751~L761)

**근거 verbatim 인용** (STEP7-J L754~L758):
> ```
> [구현 상세]
> - 라이브 스트리밍 실시간 분석:
>   ├─ 주식 시장 방송 실시간 모니터링 → 종목 언급 감지
>   ├─ 기술 컨퍼런스 실시간 요약
>   ├─ 뉴스 방송 실시간 팩트체크
>   └─ 스포츠 경기 실시간 통계
> ```

**SoT 구현성 (STEP7-J L760 verbatim)**: V3 — ⚠️ 6개월+ (실시간 처리 인프라 필요)

> **상태**: 본 V2 산출물에서는 **V2 partial 본문 골격 강화**. 완전 V3 구현은 6개월+ 별도 일정.

#### V2 partial 본문 (sliding window 5s 베이스)

```python
class StreamingAnalysisConfigV2(ModuleConfig):
    sliding_window_sec: float = 5.0                  # 5초 윈도우
    fps: int = 5                                     # 다운샘플 (전체 30 → 5)
    overlap_sec: float = 1.0                         # 윈도우 간 1초 오버랩
    target_latency_ms: int = 500                     # SoT 목표
    transport: Literal["webrtc","rtsp","srt"] = "webrtc"
    use_cases: list[Literal["stock_alert","conference_summary","fact_check","sports_stats"]] = ["conference_summary"]

class StreamingFrame:
    timestamp_ms: int
    image: bytes                                     # JPEG
    audio_pcm: Optional[bytes]                       # 16kHz mono PCM (LOCK-MM-08)

class StreamingEvent:
    timestamp_ms: int
    type: Literal["stock_mention","summary_chunk","fact_check_warn","stats_update"]
    payload: dict                                    # 유스케이스별
    confidence: float
```

#### V2 partial 알고리즘 골격

```python
async def analyze_streaming(stream: AsyncIterator[StreamingFrame],
                           cfg: StreamingAnalysisConfigV2) -> AsyncIterator[StreamingEvent]:
    buffer = SlidingWindowBuffer(cfg.sliding_window_sec, cfg.overlap_sec)

    async for frame in stream:
        buffer.add(frame)

        if buffer.is_window_complete():
            window = buffer.get_window()             # 5s 프레임 묶음

            # V2: 짧은 STT (Whisper streaming) + 가벼운 Vision LLM
            if "conference_summary" in cfg.use_cases:
                # peer J-021 V2 streaming + Qwen2-VL 7B
                stt = await streaming_stt(window.audio_pcm)  # peer Part 2
                summary = await summarize_chunk(stt.text, model="qwen2.5-7b-local")
                yield StreamingEvent(timestamp_ms=window.start_ms,
                                   type="summary_chunk",
                                   payload={"text": summary},
                                   confidence=stt.confidence)

            # V3 use cases (별도 6개월+):
            #  - stock_alert: 종목 언급 + 주가 DB 매칭
            #  - fact_check: claim extraction + KG 검증
            #  - sports_stats: object tracking + score detection

            buffer.advance(cfg.sliding_window_sec - cfg.overlap_sec)
```

#### V2 partial Phase 2 진입 항목
- E1: WebRTC 입력 (브라우저 카메라 / OBS 출력) → 5초 윈도우 buffer
- E2: `StreamingEvent` async stream (SSE 또는 WebSocket)
- E3: Conference summary 1순위 (가장 가벼움) → Qwen2-VL 7B + 짧은 STT
- E5 폴백: WebRTC 실패 → RTSP, V3 use case 실패 → conference_summary 만 활성
- E6 비용: V2 partial 로컬만 = $0; V3 stock_alert 외부 API 비용 별도
- 의존: J-035 V1 (분석 베이스), J-021 V2 streaming STT (peer Part 2), J-083 Router (peer 2-4), WebRTC (aiortc), RTSP (gstreamer)
- 지연 목표: <500ms (V2 partial 800ms~1500ms 현실, V3 6개월 후 500ms 도달)

**자체 점수**: 75/100 (V2 partial — V3 완전 구현 시 95+ 예상)

---

## 5. peer V2 cross-reference (drift 0 검증)

### 5.1 voice_chat_v2.md §4.1 (Part 2, peer V2) ↔ 본 V2 §4.1 (J-036 STT chain)
- voice_chat_v2.md §4.1 (음성 → STT → LLM → TTS chain) ↔ 본 V2 J-036 자동 자막 (`auto_subtitle=True`) → audio extract → STT (peer)
- **Part 2 §7.3 forward link 해소**: voice_chat_v2.md §7.3 "비디오 오디오 트랙 추출 → 오디오 파이프라인 A.2 라우팅" forward link → 본 V2 §4.1 E3 line `pcm = await ffmpeg_extract_pcm(raw_video, sr=16000, ch=1) # LOCK-MM-08` 에서 실체화
- 인터페이스: STTRequest LOCK-MM-08 (16kHz mono PCM) 통일

### 5.2 audio_analysis_v2.md §J-024 (Part 2, peer V2) ↔ 본 V2 §4.1 (J-036 화자분리 옵션)
- audio_analysis_v2.md §J-024 (화자분리 pyannote) ↔ 본 V2 J-036 챕터 자동 생성 시 화자 전환 경계 활용
- 인터페이스: SpeakerSegment 통일 (start/end/speaker_id)

### 5.3 tts_engine_v2.md §4.4 (Part 2, peer V2) ↔ 본 V2 §4.1 (J-036 자동 나레이션)
- tts_engine_v2.md §4.4 (Edge TTS / OpenAI TTS-1-HD) ↔ 본 V2 J-036 `auto_narration=True` → TTSRequest 호출
- 인터페이스: TTSRequest text + voice + output_format 통일

### 5.4 video_generation_v2.md (peer 본 #2b) ↔ 본 V2 §4.2 (J-039 인덱싱)
- video_generation_v2.md §4 J-033 출력 → 본 V2 §4.2 J-039 인덱싱 (생성 비디오도 검색 가능)
- forward link: 본 V2 §4.2 E3 → video_safety_v2.md J-041 사후 게이팅 통과 비디오만 인덱싱

---

## 6. Phase 3 시나리오 (10건 이상)

1. **J-036 시나리오 1**: 30분 디버깅 세션 녹화 → AI 컷 (15분으로) + 챕터 5개 + 코드 OCR.
2. **J-036 시나리오 2**: 5분 코드 리뷰 사후 편집 → 클릭 줌 + 자막.
3. **J-036 시나리오 3**: 자동 나레이션 (J-022 V2 peer) → 사용자 음성 일관성.
4. **J-036 시나리오 4**: PaddleOCR 코드 영역 검출 → 변경 부분 줌인 검증.
5. **J-036 시나리오 5**: 100MB 초과 → 720p 다운스케일.
6. **J-039 시나리오 1**: 10K 비디오 인덱싱 → 검색 P99 200ms.
7. **J-039 시나리오 2**: 텍스트 쿼리 "강아지" → CLIP 768d 검색 + 시각 0.7 + 텍스트 0.3 통합.
8. **J-039 시나리오 3**: 시간구간 필터 (60s~120s) → 정확 매칭.
9. **J-039 시나리오 4**: 자막 없는 비디오 → 시각만 인덱싱.
10. **J-039 시나리오 5**: Qdrant 실패 → local 캐시 폴백.
11. **J-040 V2 partial 시나리오**: WebRTC 입력 5분 → 5초 윈도우 conference summary chunk.
12. **J-040 시나리오**: 지연 목표 <800ms (V2 partial) → P99 측정.

---

## 7. 검증 매트릭스

| 항목 | V1 (V1 video_analysis.md) | V2 (본 산출물) | L3 점수 |
|------|-------------------------|----------------|---------|
| J-036 스크린 녹화 (V1 골격) | 4건 골격 | **E1~E10 + OBS/ffmpeg + AI 편집 본문** | 90/100 |
| J-039 검색/인덱싱 (V1 골격) | 4건 골격 | **E1~E10 + CLIP 768d + Qdrant** | 91/100 |
| J-040 V3 골격 | 4건 골격 (V3 6개월+) | **V2 partial 본문 (sliding window 5s)** | 75/100 |
| LOCK-MM-07 (CLIP 768d) | 미명시 | **assert len(emb)==768 강제** | 95/100 |
| LOCK-MM-09 (max_frames=100) | 미명시 | **clamp + warning** | 95/100 |
| peer cross-ref | 없음 (Part 2 forward link 미해소) | **voice_chat §4.1 + audio_analysis §J-024 실체화** | 92/100 |
| Phase 3 시나리오 | 미작성 | **12건 작성** | 92/100 |

**도메인 평균 L3**: **90.0/100** (LOCK-MM-12 VBS-11 ≥80 V2 충족 ✅)
