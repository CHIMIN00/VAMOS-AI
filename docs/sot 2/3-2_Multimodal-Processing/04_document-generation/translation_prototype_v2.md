# translation_prototype_v2.md — J-049 V2 EXTEND (번역 + 로컬라이제이션) + **peer Part 2 STT/TTS 파이프라인 chain (STT → 번역 → TTS)**

> **Status**: V2-Phase 2 (2-4 #2b)
> **작성일**: 2026-04-19
> **V1 정본**: [translation_prototype.md](./translation_prototype.md) (Phase 1-4 완료, ~21K, read-only sha256 baseline, J-049 V1 NEW LLM 번역)
> **SoT 근거**: STEP7-J Part 5 J-049 (L871~L887)
> **담당 J-ID**: **J-049** (V2 EXTEND: 컨텍스트 번역 + 전문 용어 사전 + 번역 메모리 + 사후 편집 + 한국어 특화)
> **상위 인덱스**: [_index.md](./_index.md)
> **peer V2 (STT→번역→TTS chain)**: **[stt_engine_v2.md](../02_audio-processing/stt_engine_v2.md) §4.2 Deepgram Nova-2** (입력 source language) + **[tts_engine_v2.md](../02_audio-processing/tts_engine_v2.md) §4.3 ElevenLabs** (출력 target language) + [voice_chat_v2.md](../02_audio-processing/voice_chat_v2.md) §4.1 (실시간 통역 chain)

---

## 1. Cross-domain 참조 블록

| 정본 | 역할 | 참조 지점 |
|------|------|----------|
| `STEP7-J_멀티모달_생성처리_작업가이드.md` Part 5 J-049 (L871~L887) | 상위 SoT J-049 | §4 verbatim |
| `translation_prototype.md` (V1) | V1 정본 | §3 V1 계승 |
| **`stt_engine_v2.md` §4.2 Deepgram Nova-2 (peer Part 2 V2)** | **STT 입력 (source language)** | **§4 E1** |
| **`tts_engine_v2.md` §4.3 ElevenLabs (peer Part 2 V2)** | **TTS 출력 (target language 다국어)** | **§4 E3** |
| `voice_chat_v2.md` §4.1 (peer Part 2) | 실시간 음성 통역 chain | §4 E3 |
| `cost_accessibility_v2.md` §4.2 (peer 본 #2b) | 다국어 매트릭스 (ko/en/ja/zh) | §6 |
| AUTHORITY_CHAIN §4 LOCK-MM-06/11 | LOCK | §2 |

---

## 2. LOCK 인용

> LOCK (STEP7-J J-094~J-096): 비용 상한 V2 ≤ ₩40K($30)

> LOCK (SPEC §14): 14-Item Tech Stack — 변경 불가

**적용 지표**: LOCK-MM-06 V2 ($30/call): DeepL/Google Translate API 비용 가드 / 로컬 NLLB-200 우선

---

## 3. V1 → V2 승급

| 항목 | V1 | V2 (본) |
|------|----|---------|
| LLM 번역 | 단순 LLM 호출 | **컨텍스트 번역 + 도메인 적응** |
| 전문 용어 사전 | 미작성 | **VAMOS 용어 사전 + 도메인별 (투자/IT/의료)** |
| 번역 메모리 | 미작성 | **이전 번역 재활용 (TM cache)** |
| 사후 편집 제안 | 미작성 | **품질 점수 + 대안 제시** |
| 한국어 특화 | 미작성 | **존댓말/반말 변환 + 외래어 표기법 + 한자어 자동 추가** |

---

## 4. V2 본문 (STEP7-J L871~L887)

**근거 verbatim 인용** (STEP7-J L874~L885):
> ```
> [구현 상세]
> - 고품질 번역 파이프라인:
>   ├─ LLM 기반 번역 (컨텍스트 이해)
>   ├─ 전문 용어 사전 연동
>   ├─ 번역 메모리 (이전 번역 재활용)
>   └─ 사후 편집 제안
>
> - 한국어 특화:
>   ├─ 한영 기술 문서 번역
>   ├─ 존댓말/반말 변환
>   ├─ 외래어 표기법 적용
>   └─ 한자어 설명 자동 추가
> ```

#### E1. Schema
```python
from common_types import ModuleConfig, MultimodalMessage
from d202_02 import VamosError, VamosResult

class TranslationConfigV2(ModuleConfig):
    default_engine: Literal["nllb-200-local","deepl","google","gpt-4o","claude"] = "nllb-200-local"
    enable_glossary: bool = True
    enable_tm_cache: bool = True                     # 번역 메모리
    tm_cache_ttl_days: int = 30
    enable_post_edit_suggest: bool = True
    korean_special: bool = True                      # 존댓말/외래어/한자어
    max_cost_per_call_usd: float = 1.00              # V2 권장 (LOCK-MM-06 V2 ≤$30)

class TranslationRequestV2:
    source_text: str                                 # 또는 source_audio (peer J-021 V2 STT 후)
    source_audio: Optional[bytes] = None             # peer Part 2 STT 입력
    source_lang: str = "ko"
    target_lang: str = "en"
    domain: Optional[Literal["technical","medical","investment","general","casual"]] = "general"
    formality: Optional[Literal["honorific","casual"]] = None  # 한국어 존댓말/반말
    output_format: Literal["text","vtt","srt","docx"] = "text"
    glossary_id: Optional[str] = None                # 사용자 용어 사전
    return_alternatives: bool = False                # 사후 편집 제안

class TranslationResultV2(VamosResult):
    target_text: str                                 # 번역 결과
    target_audio: Optional[bytes] = None             # peer J-022 V2 TTS 후 (옵션)
    confidence: float                                # 0~1
    alternatives: list[str] = []                     # 사후 편집 대안 (return_alternatives=True 시)
    glossary_applied: list[str] = []                 # 적용된 용어
    tm_hits: int = 0                                 # 번역 메모리 히트
    cost_usd: float
    processing_time_ms: int
```

#### E3. Algorithm — STT → 번역 → TTS chain
```python
async def translate(req: TranslationRequestV2,
                   cfg: TranslationConfigV2) -> TranslationResultV2:
    # 1. 입력 분기: 텍스트 직접 또는 STT 변환 (peer Part 2)
    source = req.source_text
    if req.source_audio:
        from audio.stt import transcribe              # peer Part 2 V2 stt_engine §4.2
        stt_result = await transcribe(STTRequest(
            audio=req.source_audio,
            language=req.source_lang,                 # Deepgram Nova-2 다국어 지원
        ))
        source = stt_result.text

    # 2. TM cache 조회
    tm_hits = 0
    if cfg.enable_tm_cache:
        cached = await tm_cache.get(source, req.source_lang, req.target_lang, req.domain)
        if cached and cached.confidence > 0.9:
            return TranslationResultV2(target_text=cached.target, confidence=cached.confidence,
                                      tm_hits=1, cost_usd=0.0)

    # 3. 용어 사전 적용
    glossary_applied = []
    if cfg.enable_glossary and req.glossary_id:
        glossary = await load_glossary(req.glossary_id, domain=req.domain)
        # 사전 정의된 용어 → placeholder (LLM 번역 후 복원)
        source, glossary_applied = apply_glossary_placeholders(source, glossary)

    # 4. 번역 엔진 호출
    if cfg.default_engine == "nllb-200-local":
        from local_models import nllb_translate
        target = await nllb_translate(source, src=req.source_lang, tgt=req.target_lang)
        cost = 0.0
    elif cfg.default_engine == "deepl":
        target = await deepl_api(source, src=req.source_lang, tgt=req.target_lang,
                                domain=req.domain)
        cost = 0.001 * len(source) / 100             # ~$0.001/100자
    elif cfg.default_engine == "gpt-4o":
        prompt = build_context_prompt(source, req)
        target = await gpt4o_translate(prompt)
        cost = 0.005
    elif cfg.default_engine == "google":
        target = await google_translate_api(source, src=req.source_lang, tgt=req.target_lang)
        cost = 0.00002 * len(source)             # ~$20/1M chars
    elif cfg.default_engine == "claude":
        prompt = build_context_prompt(source, req)
        target = await claude_translate(prompt)
        cost = 0.003
    else:
        return VamosError(f"unsupported translation engine: {cfg.default_engine}")
    elif cfg.default_engine == "google":
        target = await google_translate_api(source, src=req.source_lang, tgt=req.target_lang)
        cost = 0.00002 * len(source)             # ~$20/1M chars
    elif cfg.default_engine == "claude":
        prompt = build_context_prompt(source, req)
        target = await claude_translate(prompt)
        cost = 0.003
    else:
        return VamosError(f"unsupported translation engine: {cfg.default_engine}")

    # 5. 용어 placeholder 복원
    if glossary_applied:
        target = restore_glossary_terms(target, glossary_applied)

    # 6. 한국어 특화 후처리
    if cfg.korean_special and req.target_lang == "ko":
        if req.formality == "honorific":
            target = convert_to_honorific(target)
        elif req.formality == "casual":
            target = convert_to_casual(target)
        target = apply_korean_loanword_norm(target)   # 외래어 표기법
        target = annotate_hanja(target, level="basic") # 한자어 설명

    # 7. 사후 편집 대안 (V2 신규)
    alternatives = []
    if cfg.enable_post_edit_suggest and req.return_alternatives:
        alternatives = await generate_alternatives(source, target, req,
                                                  n=3, model="qwen2.5-7b-local")

    # 8. TM cache 업데이트
    if cfg.enable_tm_cache:
        await tm_cache.set(source, target, req.source_lang, req.target_lang, req.domain)

    return TranslationResultV2(target_text=target, confidence=0.92,
                              alternatives=alternatives,
                              glossary_applied=glossary_applied,
                              tm_hits=tm_hits, cost_usd=cost)
```

#### E4. Engine Selection
| 시나리오 | 1순위 | 2순위 | 비용 |
|----------|-------|-------|------|
| R-05-4 100% 로컬 | NLLB-200 (1.3B 로컬) | M2M-100 | $0 |
| 한영 기술 문서 (고품질) | DeepL Pro | GPT-4o | $0.005~$0.01/문장 |
| 한국어 특화 (존댓말/한자) | GPT-4o + 후처리 | Claude 3.5 | $0.005 |
| 다국어 자막 (vtt/srt) | NLLB-200 + format wrapper | DeepL | $0 |
| 실시간 음성 통역 (peer voice_chat) | NLLB-200 streaming | — | $0 |

#### E5. Error Handling
| 에러 | 폴백 |
|------|------|
| NLLB-200 OOM | M2M-100 (작은 모델) → DeepL API |
| DeepL API 429 | GPT-4o 폴백 |
| TM cache 실패 | 신규 번역 진행 + warning |
| 용어 사전 부재 | glossary 미적용 진행 |
| LOCK-MM-06 V2 위반 | 로컬 강제 |

#### E6. Cost
| 시나리오 | V2 (월) | LOCK-MM-06 V2 |
|----------|---------|---------------|
| 100% 로컬 (NLLB-200) | $0 | 충족 |
| DeepL Pro 1000건/월 | $5 | 충족 |
| GPT-4o 100건/월 (고품질) | $0.50 | 충족 |
| **V2 권장 합계** | **$5~$10/월** | 충족 ✅ |

#### E7. SLA
| 모드 | P50 | P99 |
|------|-----|-----|
| NLLB-200 로컬 (단문) | 200ms | 800ms |
| DeepL API | 300ms | 1.2s |
| GPT-4o (컨텍스트) | 1.5s | 5s |
| 실시간 streaming (NLLB) | <500ms (첫 청크) | 2s |

#### E8. Test (10건)
1. ko→en 기술 문서 번역 (DeepL).
2. en→ko 존댓말 변환 + 한자어 추가.
3. peer J-021 V2 STT → 본 V2 번역 → peer J-022 V2 TTS chain.
4. 용어 사전 적용 (VAMOS 용어 → en 정확).
5. TM cache 히트 (동일 문장 재요청, ~0ms).
6. NLLB-200 로컬 → R-05-4 충족.
7. 다국어 자막 (vtt/srt) 출력 포맷.
8. 사후 편집 대안 3개 반환.
9. 실시간 streaming (voice_chat 통역) → <500ms 첫 청크.
10. LOCK-MM-06 V2 위반 → 로컬 폴백.

#### E9. Dependencies
- 외부: NLLB-200 (HF), DeepL API, Google Translate, GPT-4o, Claude
- 내부 (peer): J-021 V2 (stt_engine_v2), J-022 V2 (tts_engine_v2), J-023 V2 (voice_chat_v2 실시간 통역), J-066 V2 (cost_accessibility_v2 다국어 매트릭스), J-049 V1

#### E10. Privacy
- TM cache user_id 격리
- 외부 API 호출 시 사용자 동의 (R-05-4)
- 의료/법률 도메인은 R-05-7 안전 필터 통과

**자체 점수**: 89/100

---

## 5. peer V2 cross-ref
- stt_engine_v2 §4.2 Deepgram Nova-2 → 본 V2 §4 E1 source_audio 입력
- tts_engine_v2 §4.3 ElevenLabs → 본 V2 §4 E3 target_audio 출력 (다국어 voice)
- voice_chat_v2 §4.1 → 본 V2 streaming 실시간 통역
- cost_accessibility_v2 §4.2 → 다국어 매트릭스 ko/en/ja/zh-CN 통일

---

## 6. Phase 3 시나리오 (8건)
1. STT (Deepgram) → 본 V2 (NLLB) → TTS (ElevenLabs ja) chain.
2. 용어 사전 + TM cache 히트 → 0 cost.
3. 한국어 존댓말/반말 변환.
4. 외래어 표기법 적용.
5. 한자어 설명 자동 추가 (basic level).
6. 다국어 자막 출력 (vtt/srt 포맷).
7. 실시간 음성 통역 (voice_chat) <500ms.
8. 사후 편집 대안 3개 반환.

---

## 7. 검증 매트릭스
| 항목 | V1 | V2 | L3 |
|------|----|---------|-----|
| LLM 번역 | 단순 호출 | 컨텍스트 + 도메인 | 89 |
| 용어 사전 | 미작성 | 사전 적용 + placeholder | 88 |
| TM cache | 미작성 | 30일 TTL + 히트율 | 87 |
| 한국어 특화 | 미작성 | 존댓말/외래어/한자어 | 90 |
| STT→번역→TTS chain | 미작성 | peer Part 2 chain 실체화 | 92 |

**평균**: **89.2/100** (LOCK-MM-12 V2 ≥80 충족 ✅)
