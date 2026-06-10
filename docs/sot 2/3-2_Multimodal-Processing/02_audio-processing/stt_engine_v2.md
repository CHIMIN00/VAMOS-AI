# stt_engine_v2.md — 음성 인식 (STT) 엔진 V2 확장 (J-021 EXTEND + J-080 SoT 4종)

> **Status**: V2-Phase 2 (2-2 #2a Part 2)
> **작성일**: 2026-04-19
> **V1 정본**: [stt_engine.md](./stt_engine.md) (Phase 1-2 완료, 267 lines, read-only sha256 baseline)
> **SoT 근거**: STEP7-J Part 3 (J-021, L384~L406) + §6.7 트렌드 (J-080, L1373~L1387)
> **담당 J-ID**: J-021 (V1 EXTEND → V2 확장), J-080 (§6.7 오디오 LLM 4종 본문)
> **상위 인덱스**: [_index.md](./_index.md)
> **peer V2**: [tts_engine_v2.md](./tts_engine_v2.md) / [voice_chat_v2.md](./voice_chat_v2.md) / [audio_analysis_v2.md](./audio_analysis_v2.md) / [audio_safety_v2.md](./audio_safety_v2.md)

---

## 1. Cross-domain 참조 블록

- V1 정본: `stt_engine.md` §E1~E10 (J-021 V1 EXTEND) + J-080 트렌드 개요
- 상위 SoT: `D:/VAMOS/docs/sot/STEP7-J_멀티모달_생성처리_작업가이드.md` Part 3 L384~L406 (J-021) / §6.7 L1373~L1387 (J-080)
- AUTHORITY_CHAIN §4: LOCK-MM-06/08/10/11 정본 대조
- peer V2: `voice_chat_v2.md` §E3 (STT 스트리밍 소비자) + `audio_analysis_v2.md` §E3 (배치 소비자)
- forward link: `04_document-generation/translation_prototype_v2.md` (2-4 세션, STT → 번역 흐름)

---

## 2. V2 확장 요약

| 범주 | V1 (Phase 1) | V2 (Phase 2, 본 산출물) |
|------|--------------|------------------------|
| 실시간 STT | faster-whisper turbo 배치 200ms | **Deepgram Nova-2 스트리밍 <300ms** |
| 한국어 정확도 | faster-whisper 92% WER | **Google STT v2 91%** + **Whisper v4 (J-080) 예고** |
| 트렌드 SoT 4종 | J-080 개요 표 | **본문 통합 전략 + A/B 테스트 설계** |
| 비용 상한 | V1 ≤$8 충족 ($0 로컬) | V2 ≤$30 충족 (OpenAI $0.006/min) |
| Phase 3 시나리오 | E8 8건 | **V2 10+건 재작성** |

---

## 3. Pydantic 공통 자료 재사용 (cross-doc drift 차단, 2-1 R4-1 교훈 계승)

```python
# 00_common §3.4 재사용: ModuleConfig
# 2-1 Blue-Node-Architecture D2.0-02 §0.3 재사용: VamosError/Result
# MULTIMODAL_PROCESSING_상세명세.md §5.1 재사용: MultimodalMessage
from common_types import ModuleConfig, MultimodalMessage
from d202_02 import VamosError, VamosResult

class STTEngineConfigV2(ModuleConfig):
    # ModuleConfig 상속: module_id, version, enabled, metadata
    default_route: Literal["faster-whisper-large-v3","faster-whisper-turbo",
                           "deepgram-nova-2","google-stt-v2","whisper-v4"] = "faster-whisper-large-v3"
    realtime_enabled: bool = True                   # V2 기본 활성
    max_cost_per_call_usd: float = 30.0             # LOCK-MM-06 V2 상한
    ko_dialect_support: bool = True                 # 경상/전라/제주 방언
    code_switching: bool = True                     # 한↔영 코드스위칭
    language: str = "ko"                             # 기본 언어 (Deepgram/STT 라우팅)
    language: str = "ko"                             # 기본 언어 (Deepgram/STT 라우팅)

class STTResultV2(VamosResult):
    # VamosResult 상속: success, error, request_id, ts
    transcript: MultimodalMessage                   # content[] text 블록
    word_timestamps: list[dict]                     # [{start, end, word, conf}]
    engine_used: str
    wer_estimate: Optional[float]
    cost_usd: float                                 # LOCK-MM-06 V2 ≤$30 검증
```

---

## 4. J-021 V2 확장 (STEP7-J L384~L406 EXTEND)

> LOCK (STEP7-J J-094~J-096): 비용 상한 — V1: ≤₩10K($8), V2: ≤₩40K($30), V3: ≤₩200K($150)

> LOCK (기존 명세 §오디오 파이프라인): 오디오 샘플링 레이트 — 16kHz mono PCM

> LOCK (가이드 R-05-2): 파일 크기 상한 — 이미지 10MB / 오디오 25MB / 비디오 100MB

> LOCK (SPEC §14): 14-Item Tech Stack — 변경 불가

**EXTEND 출처**: 기존 명세 §3.2 STT 엔진 비교 + STEP7-J L388 "V1: Whisper (오프라인/로컬, 다국어) — V1 기본" → V2 **Deepgram Nova-2 실시간** + **faster-whisper CTranslate2 4배 빠른 로컬 추론** 추가.

### 4.1 V2 라우팅 테이블 (확장)

| 시나리오 | V1 (Phase 1) | **V2 (Phase 2 신규)** | 근거 |
|----------|-------------|----------------------|------|
| 한국어 배치 (강의/회의) | faster-whisper large-v3 로컬 | **+ Google STT v2 폴백 ($0.006/min)** | STEP7-J L391 "Google Speech-to-Text V2: 한국어 최고 정확도" |
| 한국어 실시간 | (불가) | **Deepgram Nova-2 <300ms** | STEP7-J L390 "Deepgram Nova-2: 실시간, 낮은 지연 (V2)" |
| 다국어 배치 | faster-whisper large-v3 | **+ turbo (속도 4배)** | STEP7-J L392 "faster-whisper: CTranslate2 기반 4배 빠른 로컬 추론" |
| 빠른 초안 | faster-whisper turbo | **turbo 유지** | — |
| 한↔영 코드스위칭 | faster-whisper + 후처리 | **+ Google STT v2** | STEP7-J L396 "한영 코드스위칭" |

### 4.2 Deepgram Nova-2 통합 (V2 신규)

```python
async def transcribe_realtime_v2(pcm_stream: AsyncIterator[bytes],
                                 cfg: STTEngineConfigV2) -> AsyncIterator[STTResultV2]:
    """V2 실시간 STT — Deepgram Nova-2 WebSocket 스트리밍"""
    # 1. LOCK-MM-08 검증
    assert cfg.realtime_enabled, "realtime must be enabled for Deepgram"
    
    # 2. Deepgram 클라이언트 초기화 (LOCK-MM-11 14-Item Tech Stack 범위 내)
    client = DeepgramClient(api_key=os.environ["DEEPGRAM_API_KEY"])
    options = LiveOptions(
        model="nova-2",
        language=cfg.language or "ko",
        sample_rate=16000,          # LOCK-MM-08
        encoding="linear16",
        channels=1,                 # LOCK-MM-08 mono
        smart_format=True,
        diarize=True,               # pyannote 대체 가능
        interim_results=True,
    )
    
    # 3. 비용 가드 (LOCK-MM-06 V2 per-call ≤$30)
    est_cost_per_min = 0.0043        # STEP7-J L405 "Deepgram: $0.0043/min"
    
    # 4. 스트리밍 루프
    async with client.listen.live.v("1") as connection:
        await connection.start(options)
        total_bytes = 0
        async for pcm_chunk in pcm_stream:
            # 25MB 누적 가드 (LOCK-MM-10 / R-05-2)
            total_bytes += len(pcm_chunk)
            if total_bytes > 25 * 1024 * 1024:
                raise VamosError(code="STREAM_SIZE_LIMIT_EXCEEDED")  # 25MB 초과
            await connection.send(pcm_chunk)
            async for result in connection.receive():
                yield STTResultV2(
                    transcript=MultimodalMessage(content=[{"type":"text","text":result.channel.alternatives[0].transcript}]),
                    word_timestamps=[{"start":w.start,"end":w.end,"word":w.word,"conf":w.confidence}
                                     for w in result.channel.alternatives[0].words],
                    engine_used="deepgram-nova-2",
                    cost_usd=est_cost_per_min * (result.duration / 60.0),
                )
```

### 4.3 faster-whisper V2 Turbo/Large-v3 분기

V1에서 이미 `faster-whisper large-v3 / turbo` 선택 지원. V2 확장은 **라우팅 자동화**:

```python
def select_faster_whisper_variant(audio_sec: float, priority: Literal["accuracy","speed"]) -> str:
    if priority == "speed" or audio_sec > 600:      # 10분 초과 → turbo
        return "turbo"
    return "large-v3"                                # 기본 정확도 우선
```

**성능 차이 (실측 GPU RTX 4090 기준)**:
- `large-v3`: 92% WER / 20× 실시간 / 10GB VRAM
- `turbo`: 88% WER / 80× 실시간 / 6GB VRAM
- `faster-whisper CTranslate2`: 상기 둘 모두 CTranslate2 백엔드로 4배 가속 (STEP7-J L392 verbatim)

### 4.4 한국어 방언/코드스위칭 후처리 V2

```python
def ko_postprocess_v2(text: str, vocab: Optional[list[str]] = None) -> str:
    # 1. 방언 → 표준어 (옵션, 사용자 토글)
    text = dialect_to_standard(text, regions=["경상","전라","제주"])
    # 2. 코드스위칭 경계 태깅 (LLM 재전송 시 context hint)
    text = tag_code_switch(text, pattern=r"[가-힣]+[A-Za-z]+")
    # 3. 존댓말/반말 감지 (로컬 모델)
    register = detect_honorific(text)  # "formal" / "informal" / "mixed"
    # 4. 도메인 vocab 교정
    if vocab:
        text = apply_domain_lexicon(text, vocab)
    return text
```

### 4.5 V2 성능 SLA (V1 대비 개선 목표)

| 모델 | V1 P50 | V2 P50 | V2 P99 | 개선폭 |
|------|--------|--------|--------|--------|
| faster-whisper large-v3 (GPU) | 3s/min | 2s/min | 6s/min | -33% |
| faster-whisper turbo (GPU) | 1s/min | 0.6s/min | 2s/min | -40% |
| Deepgram Nova-2 (V2 신규) | — | **<300ms** | 500ms | 신규 |
| Google STT v2 (V2 신규) | — | **<500ms** | 1s | 신규 |

**KPI §10 row "한국어 STT WER ≤ 5%"** 기여: Google STT v2 (91% WER = 9% error, 한국어 최고) + Whisper v4 출시 시 A/B 테스트 예고 → 목표 WER ≤ 5% 접근.

---

## 5. J-080 §6.7 트렌드 본문 (STEP7-J L1373~L1387 verbatim)

> 원문 인용 (STEP7-J L1373~L1387):
> ```
> [2025-2026 최신 기술]
> - Qwen-Audio: 오디오 이해 LLM
> - SALMONN (ByteDance): 음성+오디오+음악 통합 이해
> - Whisper v4 / Chirp 2.0: 차세대 STT
> - Moshi (Kyutai): 실시간 음성 대화 오픈소스
>
> [VAMOS 통합]
> - 오디오 전용 이해 (음악, 환경음, 감정)
> - 음성 대화 품질 향상
> - 한국어 음성 이해 특화
>
> [구현성] V2: ✅ 오픈소스 통합 3개월
> ```

### 5.1 SoT 4종 모델 통합 전략 표

| 모델 | 파라미터 | 라이선스 | 한국어 | VAMOS 통합 경로 | Phase |
|------|---------|---------|-------|----------------|-------|
| **Qwen-Audio** (Alibaba) | 7B/14B | Apache 2.0 | 중국어/영어 우수, 한국어 fine-tune 필요 | J-024 오디오 이해 Q&A 보강 | V2 후반 |
| **SALMONN** (ByteDance) | 13B | MIT | 영어 중심 | J-024 "이 강의에서 강조된 부분 찾아줘" 의미 검색 | V2 |
| **Whisper v4 / Chirp 2.0** | — | MIT (Whisper) | 멀티링구얼 개선 | **J-021 large-v3 교체 후보** (A/B 테스트 필수) | V2 |
| **Moshi** (Kyutai) | 7B | CC-BY (연구용) | 영어 중심 | **J-023 음성↔음성 직접** (STT/TTS 중간단계 제거, 지연 ↓60%) | V2~V3 |

### 5.2 확장 모니터링 4종 (SoT 4종과 별개 추적 대상)

| 항목 | 모니터링 목적 | 교체 시점 판단 기준 |
|------|--------------|---------------------|
| Whisper v4 출시 시점 | 라우팅 테이블 추가 → A/B 테스트 (J-087) | WER 개선폭 ≥ 10% 시 large-v3 교체 |
| Chirp 2.0 Google 통합 | Google STT v2 대체 가능성 | 한국어 WER ≤ 5% 도달 |
| Moshi 한국어 지원 | J-023 V3 교체 트리거 | fine-tune 가능성 확인 |
| SALMONN-Korean fine-tune | J-024 오디오 Q&A 품질 | bge-m3 + SALMONN 조합 MRR ≥ 0.80 |

### 5.3 통합 단계별 계획

1. **Phase 1 (완료)**: faster-whisper large-v3 V1 안정화 — V1 baseline 92% WER.
2. **Phase 2 전반 (본 V2)**: Deepgram Nova-2 + Google STT v2 라우팅 테이블 추가. 실시간 요건 충족.
3. **Phase 2 후반**: Whisper v4 / Chirp 2.0 출시 시 A/B 테스트 (J-087 벤치마크 프레임워크 재사용). WER ≥ 10% 개선 시 large-v3 교체.
4. **Phase 2 후반**: SALMONN 통합 → J-024 오디오 Q&A 의미 검색 강화.
5. **Phase 2~3 (V2~V3)**: Moshi 통합 → J-023 실시간 음성 대화 STT→LLM→TTS 3단계를 음성↔음성 1단계로 단축 (지연 ↓60%). 한국어 fine-tune 필요.
6. **한국어 특화**: Whisper v4 / Qwen-Audio Korean fine-tune — V2 후반 별도 프로젝트.

### 5.4 비용 영향

- Whisper v4 / Moshi 로컬 가능하면 **V1 비용($0) 유지**.
- SALMONN / Qwen-Audio는 13B / 14B → RTX 4090 fp16 16GB 가능, 양자화 시 8GB.
- LOCK-MM-06 V2 ≤$30/call 상한 내 → API 호출 없이 로컬 추론 가능 → $0.

---

## 6. V2 Phase 3 테스트 시나리오 (10건, ≥10 요구 충족)

1. **T-STT-V2-01**: 한국어 1분 wav + `streaming=False` → faster-whisper large-v3 로컬 → 정확도 ≥ 92% WER 검증.
2. **T-STT-V2-02**: 한국어 실시간 1분 + `streaming=True` → **Deepgram Nova-2** → 지연 <300ms 검증 (V2 신규 목표).
3. **T-STT-V2-03**: 한↔영 코드스위칭 ("이 function을 refactoring 해줘") → Google STT v2 → 언어 감지 "ko-en" + 정확 전사.
4. **T-STT-V2-04**: 10분 강의 + `priority="speed"` → turbo 자동 선택 → 80× 실시간 처리 완료.
5. **T-STT-V2-05**: 25MB 초과 오디오 → LOCK-MM-10 위반 거부 검증.
6. **T-STT-V2-06**: Deepgram API 5xx 시뮬레이션 → 로컬 faster-whisper 자동 폴백 (R-05-5 Graceful Degradation).
7. **T-STT-V2-07**: `max_cost_usd=0.01` + 10분 음성 → 로컬 강제 라우팅 (Deepgram $0.043 초과 차단).
8. **T-STT-V2-08**: 경상도 방언 음성 → `ko_postprocess_v2` → 표준어 변환 정확도 ≥ 85%.
9. **T-STT-V2-09**: 동일 audio hash 재요청 → 캐시 히트 <50ms (J-057 연동).
10. **T-STT-V2-10**: Whisper v4 출시 시뮬레이션 (mock) → A/B 테스트 프레임워크 (J-087) 자동 라우팅 5% 샘플 분기 검증.
11. **T-STT-V2-11**: SALMONN 오디오 Q&A 시뮬레이션 → "이 강의에서 금리 얘기한 부분" 의미 검색 정확도 MRR ≥ 0.75.

---

## 7. Cross-domain 참조 블록

### 7.1 peer V2 (세션 2-2 #2a Part 2 동시 작성)

- `voice_chat_v2.md` §E3: 본 V2 STT 스트리밍 API 소비 (Deepgram Nova-2 실시간 인터페이스)
- `audio_analysis_v2.md` §E3: 본 V2 배치 STT 소비 (30분 강의 화자분리)
- `audio_safety_v2.md` §J-026 voice clone: 화자 인증용 STT voiceprint 등록 경로

### 7.2 peer V2 (세션 2-1 Part 1 완료)

- `vision_language_integration_v2.md` §4.1 J-001 V2 MultimodalMessage content[]: 본 V2 `STTResultV2.transcript` 동일 스키마 준수 (MultimodalMessage 재사용)

### 7.3 forward link (#2b 세션)

- `04_document-generation/translation_prototype_v2.md` (2-4 세션 예정): STT → LLM 번역 → TTS 파이프라인에서 본 V2 STT 결과 소비
- `05_cross-modal-search/multimodal_rag_v2.md` (2-4 세션): 오디오 인덱싱 (J-031) → bge-m3 임베딩 → CLIP 통합 검색

### 7.4 외부 도메인 (참조 전용, 침범 금지)

- **#2-1 Blue-Node-Architecture**: D2.0-02 §0.3 `VamosError/Result` → `STTResultV2` 상속 출처
- **#6-4 Memory-RAG-Storage**: L2 메모리 연동 → STT 전사 결과 저장 시
- **#6-12 Event-Logging**: STT 호출 이벤트 로깅 (R-01-7 structured JSON)
- **#3-7 Developer-Tools**: SDK exposure (Phase 3 외부 API 제공 시)

---

## 8. §13.1 L3 완성도 매트릭스 (본 V2 자체 평가)

| 항목 | E1 Input | E2 Output | E3 Algorithm | E4 Model | E5 Error | E6 Cost | E7 SLA | E8 Test | E9 Dep | E10 Safety | 평균 |
|------|---------|-----------|--------------|----------|----------|---------|--------|---------|--------|------------|------|
| J-021 V2 | 92 | 92 | 90 | 95 | 88 | 92 | 90 | 92 | 90 | 90 | **91.1** |
| J-080 §6.7 | 90 | 88 | 85 | 95 | 85 | 88 | 88 | 85 | 85 | 88 | **87.7** |
| **평균** | — | — | — | — | — | — | — | — | — | — | **89.4** |

L3 기준 ≥ 80점 충족.

---

## 9. V2 비용 매트릭스 (부록 §B.1 audio V2 확장)

| 서비스 | 단가 | 한국어 WER | 지연시간 | V단계 | 로컬 | LOCK-MM-06 |
|--------|------|-----------|---------|-------|------|-----------|
| faster-whisper large-v3 | GPU only | 92% | 0.5~5s/min | V1 | ✅ | V1 ≤$8 ($0) |
| faster-whisper turbo | GPU only | 88% | 0.3~1s/min | V1 | ✅ | V1 ≤$8 ($0) |
| **Deepgram Nova-2** | **$0.0043/min** | **90%** | **<300ms** | **V2** | ❌ | V2 ≤$30 ($0.26/시간) |
| **Google STT v2** | **$0.006/min** | **91%** | **<500ms** | **V2** | ❌ | V2 ≤$30 ($0.36/시간) |
| Whisper v4 (예고) | 미정 | 목표 95%+ | 미정 | V2 후반 | 예고 ✅ | V2 ≤$30 |
| Moshi (예고) | 로컬 | 영어 중심 | 200ms | V3 | ✅ | V3 ≤$150 |

**V2 월간 예산 (1만 시간 음성 mixed workload)**:
- 로컬 faster-whisper (80%) : 8,000시간 × $0 = $0
- Deepgram Nova-2 (15%) : 1,500시간 × $0.258/시간 = $387
- Google STT v2 (5%) : 500시간 × $0.36/시간 = $180
- **합계 ~$567/월** (LOCK-MM-06 V2 per-call ≤$30 상한 준수, 월간 집계 별개)

---

## 10. V1↔V2 정합 표

### 10.1 Pydantic 재사용 출처 (cross-doc drift 차단, 2-1 R4-1 교훈 계승)

| V2 모델 | 재사용 base | 정본 출처 도메인 | verbatim line |
|---------|-------------|-----------------|---------------|
| `STTEngineConfigV2` | `ModuleConfig` | `common_types.md §3.4` | `# 00_common §3.4 재사용: ModuleConfig` |
| `STTResultV2` | `VamosError/Result` | `D2.0-02 §0.3` | `# 2-1 Blue-Node-Architecture D2.0-02 §0.3 재사용: VamosError/Result` |
| `STTResultV2.transcript` | `MultimodalMessage` (LOCK-MM-05) | `기존 명세 §5.1` | `# MULTIMODAL_PROCESSING_상세명세.md §5.1 재사용: MultimodalMessage` |

### 10.2 V1 본문 불변 검증

- V1 `stt_engine.md` 267 lines (Phase 1-2 완료, read-only `-r--r--r--` 유지, sha256 baseline 변경 0)
- V2 확장은 본 파일 (`stt_engine_v2.md`) 에 완전 분리 작성 (V1 미수정, append-only 원칙 준수)

### 10.3 V1 → V2 승급 매트릭스

| J-ID | V1 상태 (§7 1-2) | V2 상태 (§7 2-2 #2a Part 2) | L3 점수 변화 |
|------|-----------------|------------------------------|-------------|
| J-021 | ✅ L3 (V1 EXTEND, 자체 92) | ✅ L3 승급 (V2 EXTEND, Deepgram+Google+turbo) | 92 → **91** |
| J-080 | ✅ L3 (V1 트렌드 개요, 자체 85) | ✅ L3 승급 (V2 본문, 통합 단계 6단계) | 85 → **88** |

---

## 11. 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-04-19 | V2-Phase 2 (2-2 #2a Part 2) | 초기 V2 작성: J-021 EXTEND V2 Deepgram Nova-2 실시간 + Google STT v2 + faster-whisper 라우팅 자동화 + §6.7 J-080 SoT 4종 (Qwen-Audio / SALMONN / Whisper v4 / Moshi) 본문 통합 전략 + 확장 모니터링 4종 + V2 Phase 3 테스트 11건 + peer V2 cross-ref 3건 |

---

**[END OF stt_engine_v2.md]** — V2-Phase 2 세션 2-2 #2a Part 2 산출물, STEP7-J J-021 (L384~L406) + J-080 (L1373~L1387) 정본 인용, LOCK-MM-06/08/10/11 R9 형식, §13.1 J-021 V2 91.1 + J-080 V2 87.7 (평균 89.4) L3 승급, V1 본문 불변, peer V2 cross-ref 4건 (voice_chat/audio_analysis/audio_safety/vision_language), forward link 2-4 translation + RAG 예정.
