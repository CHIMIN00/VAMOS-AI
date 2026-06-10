# audio_analysis.md — 오디오 분석 / 생성 / 번역 / 검색 / 자막 (J-024, J-025, J-027, J-031, J-032 + V2 골격 J-029, J-030)

> **Status**: APPROVED (L3)
> **작성일**: 2026-04-08
> **정본 소유 개념**: 오디오 파일 분석(전사+화자분리+요약), 음악/효과음 생성, 음성 번역, 오디오 인덱싱/검색, 실시간 자막
> **SoT 근거**: STEP7-J Part 3 (J-024, J-025, J-027, J-029~J-032)
> **담당 J-ID**: J-024, J-025, J-027, J-031, J-032 (V1 5건) + J-029, J-030 (V2 골격)
> **상위 인덱스**: [_index.md](./_index.md)

---

## LOCK 인용

> LOCK (STEP7-J J-094~J-096): 비용 상한 — V1: ≤₩10K($8), V2: ≤₩40K($30), V3: ≤₩200K($150)

> LOCK (SPEC §14): 14-Item Tech Stack — 변경 불가

> LOCK (기존 명세 §오디오 파이프라인): 오디오 샘플링 레이트 — 16kHz mono PCM

> LOCK (가이드 R-05-2): 파일 크기 상한 — 이미지 10MB / 오디오 25MB / 비디오 100MB

---

## 공통 참조

본 파일의 모든 STT 호출은 J-021(`stt_engine.md`), TTS 호출은 J-022(`tts_engine.md`)에 위임한다. 검색·캐싱 인프라는 J-051/J-057(`05_cross-modal-search/multimodal_rag.md`, `caching_optimization.md`)을 공유 사용한다. 화자분리는 J-024가 1차 정본 소유.

---

## J-024. 오디오 파일 분석 [V1 / NEW]

**근거**: STEP7-J L465-486

> **충돌 해결**: 종합계획서 §6.2 우선 → J-024는 본 파일에 배치 (`audio_analysis.md`). `stt_engine.md` 아님.

### E1. Input Schema
```python
class AudioAnalysisRequest:
    audio: bytes                            # ≤ 25MB (LOCK-MM-10)
    audio_type: Literal["lecture","meeting","podcast","music","interview","other"] = "other"
    diarize: bool = True                    # 화자분리
    summarize: bool = True
    extract_action_items: bool = False      # 회의록 → TodoWrite 연동
    language: str = "ko"
    max_speakers: int = 10                  # pyannote 상한
    qa_questions: Optional[list[str]] = None  # "30분쯤에 뭐라고 했어?" 류
```

### E2. Output Schema
```python
class AudioAnalysisResult:
    transcript: str                         # 전체 전사
    segments: list[SpeakerSegment]          # 화자별 타임스탬프
    speakers: list[SpeakerProfile]          # SPEAKER_00.. 라벨 + 발언량
    summary: str                            # 요약 (LLM)
    key_points: list[KeyPoint]              # {timestamp, text, importance}
    action_items: list[ActionItem]          # {speaker, text, due?}
    qa_answers: list[QAAnswer]              # qa_questions 응답 + 타임스탬프
    topics: list[str]                       # 주요 토픽 키워드
    duration_sec: float
    cost_usd: float

class SpeakerSegment:
    speaker_id: str                         # "SPEAKER_00"
    start: float; end: float
    text: str
    confidence: float

class SpeakerProfile:
    speaker_id: str
    total_speech_sec: float
    turn_count: int
    avg_pitch_hz: Optional[float]           # 화자 식별 보조

class KeyPoint:
    timestamp: float
    text: str
    importance: float                       # 0..1
    source_segments: list[int]

class ActionItem:
    speaker_id: Optional[str]               # 발화자 (없으면 None)
    text: str                               # "다음 주까지 보고서 제출"
    due: Optional[str]                      # ISO date, 없으면 None
    confidence: float                       # 0..1

class QAAnswer:
    question: str
    answer: str
    timestamp: float                        # 답변 근거 구간 시작 (sec)
    source_segments: list[int]              # 인용 segment idx
```

### E3. Algorithm
```python
async def analyze_audio(req: AudioAnalysisRequest) -> AudioAnalysisResult:
    # 1. STT (J-021 위임) — word_timestamps + diarize
    stt = await transcribe(STTRequest(
        audio=req.audio, language=req.language,
        word_timestamps=True, diarize=req.diarize,
    ))

    # 2. 화자분리 결과 매핑 (이미 stt.segments에 speaker_id 할당됨)
    speakers = compute_speaker_profiles(stt.segments)

    # 3. 요약 (LLM, 청크 분할 → map-reduce)
    summary = ""
    key_points = []
    if req.summarize:
        chunks = chunk_by_topic(stt.segments, max_chars=4000)
        partials = await asyncio.gather(*[
            llm_summarize(c, audio_type=req.audio_type) for c in chunks
        ])
        summary = await llm_merge_summaries(partials)
        key_points = await llm_extract_keypoints(stt.segments)

    # 4. 액션 아이템 (회의록 모드)
    action_items = []
    if req.extract_action_items:
        action_items = await llm_extract_actions(stt.segments)
        # → TodoWrite/J-064 메모리 통합

    # 5. Q&A (시간 기반 검색 + LLM 답변)
    qa_answers = []
    if req.qa_questions:
        for q in req.qa_questions:
            ts_match = await semantic_search_segments(stt.segments, q)
            if not ts_match:                       # E5: qa_question 매칭 실패
                qa_answers.append(QAAnswer(question=q, answer="해당 내용을 찾을 수 없습니다", timestamp=None))
                continue
            ans = await llm_answer_with_context(q, ts_match)
            qa_answers.append(QAAnswer(question=q, answer=ans, timestamp=ts_match[0].start))

    # 6. 토픽 추출
    topics = await llm_extract_topics(stt.text)

    return AudioAnalysisResult(...)
```

### E4. Model Selection
| 작업 | V1 | V2 |
|------|-----|-----|
| STT | faster-whisper large-v3 (J-021) | + Deepgram Nova-2 |
| 화자분리 | pyannote/speaker-diarization-3.1 (로컬) | + 화자 인증 (성문) |
| 요약 | Claude Haiku ($0.001/청크) / 로컬 Llama 4 | Claude Sonnet 4.6 |
| 음악 분석 | (별도 — V2 essentia/librosa) | essentia BPM/key |

화자분리 설정 (기존 명세 §3.3 계승):
- model: `pyannote/speaker-diarization-3.1`
- min_speakers=1, max_speakers=10
- embedding: `pyannote/wespeaker-voxceleb-resnet34`
- clustering: agglomerative, min_cluster_size=15s

### E5. Error Handling

| 에러 | 폴백 |
|------|------|
| 25MB 초과 | 거부 (LOCK-MM-10) — 청크 업로드 안내 |
| pyannote 모델 미다운로드 | 자동 다운로드 1회 → 실패 시 diarize=False로 진행 |
| LLM 컨텍스트 초과 | 청크 분할 + map-reduce |
| 화자 0명 (음악 파일) | diarize 결과 없이 진행 |
| qa_question 매칭 실패 | "해당 내용을 찾을 수 없습니다" 응답 |

### E6. Cost Analysis

| 시나리오 | V1 (월) |
|----------|---------|
| 일 30분 회의 분석 (로컬 STT + Haiku 요약) | ~$0.45 |
| 일 60분 강의 분석 | ~$0.90 |
| **V1 권장 합계** | **≤ $1.35** (LOCK-MM-06 V1=$8 충족) |

### E7. Performance SLA

| 입력 길이 | P50 | P99 |
|----------|-----|-----|
| 5분 회의 | 15s | 30s |
| 30분 강의 | 90s | 180s |
| 60분 팟캐스트 | 180s | 360s |

(GPU RTX 4090 기준; STT가 지배적)

### E8. Integration Test

1. 5분 한국어 회의 → 화자 2명 분리 + 액션 아이템 3개 추출.
2. 30분 강의 → 요약 + 5개 key points + 토픽 ["통화정책","금리"] 추출.
3. `qa_questions=["KOSPI 전망?"]` → 해당 구간 timestamp + 답변.
4. 음악 파일 → diarize 결과 없이 메타데이터(BPM은 V2)만.
5. 25MB 초과 → 즉시 거부.
6. pyannote 모델 누락 → 자동 다운로드 후 재시도.

### E9. Dependencies

- 외부: pyannote-audio, faster-whisper, anthropic SDK / 로컬 LLM, librosa (V2 음악 분석)
- 내부: J-021 (STT), J-031 (인덱싱), J-064 (메모리 → 액션 아이템), J-057 (캐시)
- HuggingFace 토큰 (pyannote 모델 다운로드)

### E10. Privacy / Safety

- R-05-4: 로컬 STT/화자분리 → 음성 데이터 외부 전송 없음
- 화자 ID는 익명 라벨(SPEAKER_00..) — 사용자가 명시 매핑 시에만 실명 연결
- 회의 녹음 분석은 참가자 동의 의무 — 시스템은 동의 체크박스 강제

**자체 점수**: 88/100

---

## J-025. 음악/사운드 생성 [V1 / NEW]

**근거**: STEP7-J L488-510

### E1. Input Schema
```python
class MusicGenRequest:
    prompt: str                             # "신나는 lo-fi 코딩 BGM"
    type: Literal["song","instrumental","sfx","ambient"] = "instrumental"
    duration_sec: int = 30                  # 1..300
    style: Optional[str] = None             # "lo-fi","ambient","jazz",...
    lyrics: Optional[str] = None            # type=song 시
    bpm: Optional[int] = None               # 60..200
    key: Optional[str] = None               # "C major","A minor"
    prefer_local: bool = True               # R-05-4
    max_cost_usd: float = 0.10
```

### E2. Output Schema
```python
class MusicGenResult:
    audio: bytes                            # MP3, ≤ 25MB (LOCK-MM-10)
    duration_sec: float
    sample_rate_hz: int                     # 32000 (MusicGen) / 44100 (Suno)
    model_used: str
    style_tags: list[str]
    cost_usd: float
    license: str                            # "CC0-Local" / "Suno-Commercial"
```

### E3. Algorithm
```python
async def generate_music(req: MusicGenRequest) -> MusicGenResult:
    # 1. 라우팅
    if req.type == "song" and req.lyrics:
        route = "suno-api" if not req.prefer_local else None
        if route is None:
            raise NotSupported("V1 로컬은 가사 노래 생성 미지원 → V2 Suno")
    elif req.type == "sfx":
        route = "audiogen-local"            # Meta AudioGen
    else:
        route = "musicgen-local" if req.prefer_local else "suno-api"

    # 2. 비용 가드
    est = estimate_cost(route, req.duration_sec)
    if est > req.max_cost_usd:
        raise CostExceeded(f"{est} > {req.max_cost_usd}")

    # 3. 캐시 조회
    key = sha256(
        f"{route}|{req.prompt}|{req.duration_sec}|{req.style}|{req.bpm}|{req.key}|{req.lyrics}".encode()
    ).hexdigest()
    if cached := await cache.get(key):
        return cached

    # 4. 생성
    if route == "musicgen-local":
        audio = await musicgen.generate(
            prompt=build_musicgen_prompt(req),
            duration=req.duration_sec,
            model="facebook/musicgen-medium",
        )
    elif route == "audiogen-local":
        audio = await audiogen.generate(prompt=req.prompt, duration=req.duration_sec)
    elif route == "suno-api":
        audio = await suno_api.generate(prompt=req.prompt, lyrics=req.lyrics, style=req.style)

    # 5. 후처리 + 캐시
    audio_mp3 = to_mp3(audio)
    if len(audio_mp3) > 25*1024*1024:
        raise OutputTooLarge()
    result = MusicGenResult(audio=audio_mp3, ...)
    await cache.put(key, result, ttl=30*86400)
    return result
```

### E4. Model Selection

| 시나리오 | V1 | V2 |
|----------|-----|-----|
| BGM/lo-fi/ambient | MusicGen medium 로컬 | + Suno API ($10/mo) |
| 효과음 (UI/알림) | AudioGen 로컬 | + ElevenLabs Sound Effects |
| 가사 노래 | (불가) | Suno / Udio |
| 고품질 인스트루멘탈 | MusicGen large (GPU 16GB+) | Suno |

### E5. Error Handling

| 에러 | 폴백 |
|------|------|
| GPU OOM | medium → small 모델 다운스케일 |
| duration > 300s | 자동 분할 생성 → crossfade 결합 |
| Suno API 속도제한 | 큐잉 + 사용자 대기 안내 |
| 음악 저작권 의심 (lyrics) | 사용자 경고 + 동의 체크 |
| 출력 > 25MB | 비트레이트 다운스케일 (192k → 128k) |

### E6. Cost Analysis

| 시나리오 | V1 (월) |
|----------|---------|
| 일 1곡 30s MusicGen 로컬 | $0 |
| 월 5곡 Suno API | $10 (V2) |
| **V1 권장 합계** | **$0** (LOCK-MM-06 V1=$8 충족) |

### E7. Performance SLA

| 모델 | 30s 생성 P50 | P99 |
|------|------|-----|
| MusicGen medium 로컬 (GPU) | 20s | 60s |
| MusicGen small 로컬 | 8s | 20s |
| Suno API | 30s | 90s |

### E8. Integration Test

1. "신나는 lo-fi BGM 30초" → MusicGen 로컬 → MP3 출력.
2. `type="sfx", prompt="버튼 클릭음"` → AudioGen → 1초 효과음.
3. `type="song"+ lyrics, prefer_local=True` → NotSupported 에러 + V2 안내.
4. 동일 prompt 재요청 → 캐시 히트.
5. 300s 초과 → 거부.

### E9. Dependencies

- 외부: audiocraft (Meta MusicGen/AudioGen), torch, suno-api (V2)
- 내부: J-057 (캐시), Cost Manager (J-065)
- GPU: RTX 4090 권장 (medium 모델 8GB+)

### E10. Privacy / Safety

- 가사 입력은 저작권 책임 사용자 부담 — 시스템은 명시적 경고
- Suno API 사용 시 콘텐츠가 외부 전송됨 (사용자 동의 토글)
- 생성물 라이선스 명시 (CC0 로컬 / Suno 상업 라이선스)

**자체 점수**: 85/100

---

## J-027. 오디오 번역 (Speech Translation) [V1 / NEW]

**근거**: STEP7-J L536-548

### E1. Input Schema
```python
class SpeechTranslateRequest:
    audio: bytes                            # ≤ 25MB
    source_lang: Optional[str] = None       # 자동감지
    target_lang: str = "en"
    output_mode: Literal["text","audio","both"] = "both"
    voice: Optional[str] = None             # TTS voice
    preserve_timing: bool = False           # 자막 정렬용
```

### E2. Output Schema
```python
class SpeechTranslateResult:
    source_text: str
    source_lang: str
    target_text: str
    target_audio: Optional[bytes]           # output_mode in {"audio","both"}
    segments: list[TimedSegment]            # preserve_timing=True 시
    duration_sec: float
    cost_usd: float

class TimedSegment:
    start: float; end: float
    source_text: str
    target_text: str
```

### E3. Algorithm — STT → 번역 → TTS 파이프라인 (V1)
```python
async def translate_speech(req: SpeechTranslateRequest) -> SpeechTranslateResult:
    # 1. STT (J-021)
    stt = await transcribe(STTRequest(
        audio=req.audio, language=req.source_lang,
        word_timestamps=req.preserve_timing,
    ))

    # 2. 번역 (LLM 또는 NMT)
    if req.preserve_timing:
        translated_segs = []
        for seg in stt.segments:
            t = await llm_translate(seg.text, src=stt.language_detected, tgt=req.target_lang)
            translated_segs.append(TimedSegment(
                start=seg.start, end=seg.end,
                source_text=seg.text, target_text=t,
            ))
        target_text = " ".join(s.target_text for s in translated_segs)
    else:
        target_text = await llm_translate(stt.text, src=stt.language_detected, tgt=req.target_lang)
        translated_segs = []

    # 3. TTS (J-022)
    target_audio = None
    if req.output_mode in {"audio","both"}:
        tts_res = await synthesize(TTSRequest(
            text=target_text, language=req.target_lang, voice=req.voice,
        ))
        target_audio = tts_res.audio

    return SpeechTranslateResult(...)
```

### E4. Model Selection

| 컴포넌트 | V1 | V2 |
|---------|-----|-----|
| STT | faster-whisper large-v3 (다국어) | + Deepgram |
| 번역 | Claude Haiku (high-quality) | + DeepL API |
| TTS | Edge TTS (target lang voice) | + ElevenLabs |
| 음성↔음성 직접 | (V1 없음) | SeamlessM4T (Meta) |

V2: SeamlessM4T 통합 시 STT/번역/TTS 3단계 → 1단계로 단축 (음색 보존 가능).

### E5. Error Handling

| 에러 | 폴백 |
|------|------|
| 미지원 언어쌍 | en 경유 (pivot translation) |
| TTS voice 미지원 | 언어별 기본 voice 사용 |
| 번역 길이 폭증 (10x) | 청크 분할 + 병합 |

### E6. Cost Analysis

| 시나리오 | V1 (월) |
|----------|---------|
| 일 5분 한↔영 번역 (로컬 STT + Haiku + Edge TTS) | ~$0.15 |
| **V1 권장 합계** | **~$0.15** (LOCK-MM-06 V1=$8 충족) |

### E7. Performance SLA

| 입력 5분 | P50 | P99 |
|----------|-----|-----|
| 텍스트 전용 | 8s | 20s |
| 음성 포함 | 15s | 35s |

### E8. Integration Test

1. 한국어 1분 발화 → 영어 텍스트+음성 출력.
2. `preserve_timing=True` → 자막 정렬용 segments 출력 (.srt 변환 가능).
3. 미지원 언어쌍 (예: ko→sw) → en 경유 자동.
4. `output_mode="text"` → audio=None.

### E9. Dependencies

- 외부: faster-whisper, anthropic SDK, edge-tts
- 내부: J-021 (STT), J-022 (TTS), J-032 (자막 — preserve_timing 결과 소비)

### E10. Privacy / Safety

- R-05-4: 로컬 STT 우선 → 음성 외부 전송 없음
- 번역은 LLM API 호출 → 텍스트만 전송 (음성은 전송되지 않음)

**자체 점수**: 86/100

---

## J-031. 오디오 인덱싱 및 검색 [V1 / NEW]

**근거**: STEP7-J L591-600

### E1. Input Schema
```python
class AudioIndexRequest:
    audio: bytes
    audio_id: UUID                          # 클라이언트 지정 또는 자동
    metadata: dict                          # title, source, tags
    extract_chunks: bool = True             # 30s 청크 임베딩
    language: str = "ko"

class AudioSearchQuery:
    query: str | bytes                      # text or audio (V2 CLAP)
    query_type: Literal["text","audio"] = "text"
    top_k: int = 10
    filter: Optional[dict] = None           # metadata 필터
    return_timestamps: bool = True
```

### E2. Output Schema
```python
class AudioIndexResult:
    audio_id: UUID
    indexed_chunks: int
    transcript_chars: int
    embedding_dim: int                      # 768 (text) / 512 (CLAP, V2)

class AudioSearchHit:
    audio_id: UUID
    chunk_idx: int
    start: float; end: float
    text_excerpt: str
    score: float
    metadata: dict
```

### E3. Algorithm
```python
async def index_audio(req: AudioIndexRequest):
    # 1. STT (J-021)
    stt = await transcribe(STTRequest(audio=req.audio, language=req.language, word_timestamps=True))

    # 2. 30s 청크 분할 (overlap 5s)
    chunks = chunk_segments(stt.segments, window=30.0, overlap=5.0)

    # 3. 텍스트 임베딩 (V1: text-embedding 모델)
    texts = [c.text for c in chunks]
    embs = await embed_texts(texts, model="bge-m3")  # 768d, 한국어 우수

    # 4. Qdrant upsert (J-051/J-057 공유 인프라 — 05_cross-modal-search)
    points = [
        QdrantPoint(
            id=f"{req.audio_id}:{i}",
            vector=e,
            payload={
                "audio_id": str(req.audio_id),
                "chunk_idx": i,
                "start": c.start, "end": c.end,
                "text": c.text,
                **req.metadata,
            },
        ) for i, (c, e) in enumerate(zip(chunks, embs))
    ]
    await qdrant.upsert("audio_chunks", points)
    return AudioIndexResult(...)

async def search_audio(q: AudioSearchQuery) -> list[AudioSearchHit]:
    if q.query_type == "text":
        embs = await embed_texts([q.query], model="bge-m3")
        emb = embs[0]
    else:
        # V2: CLAP 오디오 임베딩
        raise NotImplementedV1("audio query → V2 (CLAP)")

    hits = await qdrant.search("audio_chunks", emb, top_k=q.top_k, filter=q.filter)
    return [AudioSearchHit(
        audio_id=UUID(h.payload["audio_id"]),
        chunk_idx=h.payload["chunk_idx"],
        start=h.payload["start"], end=h.payload["end"],
        text_excerpt=h.payload["text"],
        score=h.score,
        metadata={k: v for k, v in h.payload.items()
                  if k not in {"audio_id","chunk_idx","start","end","text"}},
    ) for h in hits]
```

### E4. Model Selection

| 컴포넌트 | V1 | V2 |
|---------|-----|-----|
| 텍스트 임베딩 | bge-m3 (768d, 한국어 우수, 로컬) | + Voyage AI |
| 오디오 임베딩 | (V1 없음) | CLAP (512d) |
| 벡터 DB | Qdrant (로컬) | Qdrant Cloud |

### E5. Error Handling

| 에러 | 폴백 |
|------|------|
| Qdrant 컬렉션 없음 | 자동 생성 (768d, Cosine, int8 양자화) |
| 빈 STT (음악) | 인덱싱 스킵 + 경고 |
| 임베딩 모델 OOM | 청크 batch_size 다운스케일 |
| audio query (V1) | NotImplemented + V2 안내 |

### E6. Cost Analysis

- 임베딩 로컬 (bge-m3): $0
- Qdrant 로컬: 디스크만 사용
- **V1 합계: $0** (LOCK-MM-06 V1=$8 충족)

### E7. Performance SLA

| 작업 | P50 | P99 |
|------|-----|-----|
| 30분 오디오 인덱싱 | 120s (STT 지배) | 240s |
| 검색 (top_k=10) | 50ms | 150ms |

### E8. Integration Test

1. 30분 강의 인덱싱 → ~50개 청크.
2. "API 설계에 대해 말한 부분" 검색 → 정확한 timestamp 반환.
3. metadata 필터 (`{"source":"meeting"}`) → 회의 녹음만 검색.
4. audio query → NotImplemented 에러 + V2 안내.

### E9. Dependencies

- 외부: bge-m3 (sentence-transformers), qdrant-client
- 내부: J-021 (STT), J-051 (멀티모달 청킹 패턴 공유 — `05_cross-modal-search/multimodal_rag.md`), J-057 (멀티모달 캐싱 — `05_cross-modal-search/caching_optimization.md`), J-024 (분석 결과 메타 통합)

### E10. Privacy / Safety

- 로컬 임베딩 + 로컬 Qdrant → 외부 전송 없음
- 인덱스는 user_id 단위 격리 (multi-tenant)
- 검색 결과는 사용자가 권한 가진 audio_id만

**자체 점수**: 87/100

---

## J-032. 실시간 자막 (Live Caption) [V1 / NEW]

**근거**: STEP7-J L602-611

### E1. Input Schema
```python
class LiveCaptionSession:
    session_id: UUID
    source: Literal["mic","system_audio","file"]  # V1: mic/file, V2: system_audio
    language: str = "ko"
    target_lang: Optional[str] = None       # 다국어 자막 (J-027 위임)
    overlay_mode: bool = False              # always-on-top UI 신호
    chunk_window_ms: int = 500              # STT 배치 윈도우
    save_srt: bool = False                  # 종료 후 .srt 저장
```

### E2. Output Schema
```python
class CaptionEvent:
    session_id: UUID
    seq: int
    type: Literal["partial","final","translation","error"]
    text: str
    start: float; end: float
    speaker_id: Optional[str]               # diarize 통합 시
    timestamp_ms: int
```

### E3. Algorithm
```python
async def run_live_caption(session: LiveCaptionSession,
                           frames: AsyncIterator[bytes]
                           ) -> AsyncIterator[CaptionEvent]:
    if session.source == "system_audio":
        raise NotImplementedV1("system audio capture → V2")

    stt = STTStream(language=session.language)  # J-021 streaming wrapper
    seq = 0
    buffer = bytearray()
    window = session.chunk_window_ms / 1000.0
    last_flush = time.time()

    async for chunk in frames:
        buffer += chunk
        if time.time() - last_flush >= window:
            partial = await stt.feed(bytes(buffer))
            if partial:
                yield CaptionEvent(seq=seq, type="partial", text=partial.text,
                                   start=partial.start, end=partial.end, ...)
                seq += 1
                if session.target_lang:
                    t = await llm_translate(partial.text, session.language, session.target_lang)
                    yield CaptionEvent(seq=seq, type="translation", text=t, ...)
                    seq += 1
            buffer.clear()
            last_flush = time.time()

    # 최종 flush
    final = await stt.finalize(bytes(buffer))
    yield CaptionEvent(seq=seq, type="final", text=final.text, ...)

    if session.save_srt:
        await save_srt(session.session_id, accumulated_segments)
```

### E4. Model Selection

| 시나리오 | V1 | V2 |
|----------|-----|-----|
| 마이크 → 자막 | faster-whisper turbo (배치 500ms) | Deepgram Nova-2 streaming |
| 파일 → .srt | faster-whisper large-v3 | + Google STT |
| 시스템 오디오 캡처 | (V1 미지원) | WASAPI (Windows) / BlackHole (mac) |
| 다국어 번역 자막 | Haiku 번역 (J-027) | + SeamlessM4T |

### E5. Error Handling

| 에러 | 폴백 |
|------|------|
| 마이크 권한 거부 | 세션 종료 + 안내 |
| STT 부분 결과 비어있음 | 다음 윈도우 대기 |
| 번역 실패 | 원문 자막만 표시 |
| system_audio (V1) | NotImplemented + V2 안내 |

### E6. Cost Analysis

| 시나리오 | V1 (월) |
|----------|---------|
| 일 30분 라이브 자막 (로컬 STT) | $0 |
| 다국어 번역 (Haiku) 추가 | ~$0.45 |
| **V1 권장 합계** | **~$0.45** (LOCK-MM-06 V1=$8 충족) |

### E7. Performance SLA

| 지표 | V1 P50 | V1 P99 | V2 P50 |
|------|--------|--------|--------|
| partial 지연 (발화 → 자막 표시) | 800ms | 2000ms | 300ms |
| 번역 추가 지연 | 400ms | 1500ms | 200ms |

### E8. Integration Test

1. 마이크 입력 → 500ms 윈도우 partial 자막 출력.
2. 한→영 번역 자막 동시 표시.
3. `save_srt=True` → 종료 후 .srt 파일 생성 (timestamp 정합).
4. `source="system_audio"` → NotImplemented + V2 안내.
5. 마이크 권한 거부 → error 이벤트.

### E9. Dependencies

- 외부: faster-whisper, sounddevice (마이크), pysrt (.srt 저장)
- 내부: J-021 (STT), J-027 (번역), J-022 (TTS — 시각장애인 모드 V2)

### E10. Privacy / Safety

- R-05-4: 로컬 STT → 음성 외부 전송 없음
- 자막 텍스트는 세션 종료 후 자동 폐기 (save_srt=True 시에만 보존)
- 회의 자막은 참가자 동의 의무

**자체 점수**: 86/100

---

## V2 골격 (Phase 2 진입 시 확장)

### J-029. 오디오 감정 분석 [V2 / EXTEND — 골격]

**근거**: STEP7-J L561-573, 기존 명세 §3.4

**EXTEND 출처**: 기존 명세 §3.4 Russell circumplex model (primary 7 + secondary 6 + arousal/valence)

```python
# Phase 2에서 E1~E10 작성
class SpeechEmotionRequest:
    audio: bytes
    return_arousal_valence: bool = True

class SpeechEmotionResult:
    primary_emotion: str         # "기쁨"
    confidence: float
    arousal: float               # -1..1
    valence: float               # -1..1
    secondary_emotions: dict
```

V2 모델: SpeechBrain emotion-recognition / Hume AI / 자체 fine-tune.
연동: J-024 (회의 감정 분석), J-070 (컨텍스트 톤 조절), STEP7-P 웰니스 (스트레스 추적).

### J-030. 팟캐스트/오디오 자동 생성 [V2 / NEW — 골격]

**근거**: STEP7-J L575-589

NotebookLM Audio Overview 스타일: 문서 → 2인 대화 팟캐스트 자동 생성.

파이프라인 (Phase 2 작성 예정):
```
[입력 문서] → [LLM 스크립트 생성 (대화 형식)]
    → [화자 1: ElevenLabs voice A, 화자 2: ElevenLabs voice B]
    → [TTS 청크 합성] → [BGM/효과음 (J-025)] → [최종 오디오]
```

연동: J-022 (TTS), J-025 (BGM), J-024 (소비자 — 생성 후 인덱싱).

---
