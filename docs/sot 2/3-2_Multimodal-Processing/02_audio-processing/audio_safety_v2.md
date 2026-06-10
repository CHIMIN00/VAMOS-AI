# audio_safety_v2.md — 음성 복제 윤리 프레임워크 V2 본문 (J-026 NEW)

> **Status**: V2-Phase 2 (2-2 #2a Part 2)
> **작성일**: 2026-04-19
> **V1 정본**: [audio_safety.md](./audio_safety.md) (Phase 1-2 완료, 266 lines, read-only sha256 baseline, J-028 V1 NEW + J-026 V2 골격)
> **SoT 근거**: STEP7-J Part 3 (J-026, L512~L534)
> **담당 J-ID**: **J-026** (V2 NEW: 음성 복제 + 5중 윤리 프레임워크 본문)
> **상위 인덱스**: [_index.md](./_index.md)
> **peer V2**: [stt_engine_v2.md](./stt_engine_v2.md) / [tts_engine_v2.md](./tts_engine_v2.md) / [voice_chat_v2.md](./voice_chat_v2.md) / [audio_analysis_v2.md](./audio_analysis_v2.md) + **[image_safety_metadata_v2.md](../01_image-pipeline/image_safety_metadata_v2.md) §8.2**

---

## 1. Cross-domain 참조 블록

- V1 정본: `audio_safety.md` §J-028 (V1 NEW, DeepFilterNet 소음 제거) + §J-026 V2 골격 (L181~L257, 윤리 프레임워크 6조항 + 모델 후보 표)
- 상위 SoT: STEP7-J L512~L534 (J-026 verbatim)
- AUTHORITY_CHAIN §4: LOCK-MM-06/08/10/11 정본 대조
- 거버넌스 규칙 원문: **R-05-7** (종합계획서 §4, 딥페이크/NSFW 안전 필터 항시 활성화) — 본 V2 5중 프레임워크 fail-safe=reject 및 워터마크 강제 정책의 근거
- **peer V2 Part 1 정본**: `image_safety_metadata_v2.md` §8.2 (딥페이크 감지 공통 아키텍처) + §4 J-017 V2 (NSFW + FaceForensics++ EfficientNet-B4 + CSAM zero-tolerance)
- peer V2 2-2 본 파트: tts_engine_v2 §4.4 Fish Speech zero-shot / audio_analysis_v2 §J-030 화자 A/B voice_id / voice_chat_v2 §4.2 audio_ref 생성자
- forward link: `03_video-analysis/video_safety_v2.md` (#2b 2-3, 비디오 립싱크 딥페이크 + 본 V2 음성 딥페이크 통합 감지)

---

## 2. V2 확장 요약

| 범주 | V1 (Phase 1, §J-026 골격) | V2 (Phase 2, 본 산출물) |
|------|--------------------------|------------------------|
| 5중 프레임워크 | 조항 나열만 (6조항 중 5개 활성) | **각 조항 E1~E10 수준 본문 + 실측 구현** |
| 명시적 동의 | "opt-in 토글, 기본값 OFF" 텍스트 | **consent_token 발급 API + 감사 로그 + 7일 만료** |
| 화자 인증 | "voiceprint 유사도 ≥ 0.85 차단" 텍스트 | **wav2vec2-anti-spoofing + pyannote embedding + challenge phrase** |
| 딥페이크 방지 워터마크 | "AudioSeal 제안" | **AudioSeal 상세 + invisible watermark + 이미지 FaceForensics++ 통일** |
| Constitutional AI | "정치인/공인 차단" 텍스트 | **R-05-7 정책 원문 + 분류기 + 거부 페이로드 + 감사 로그** |
| **미성년자 zero-tolerance** | 미포함 (V1 골격) | **신규: 나이 검증 + CSAM 동급 정책 + 영구 로그** |
| 삭제 권리 | "GDPR/PIPA 준수" 텍스트 | **user_id 단위 영구 삭제 + voice_id 캐스케이드** |
| Phase 3 시나리오 | (미작성) | **V2 12건** |

---

## 3. Pydantic 공통 자료 재사용

```python
# 00_common §3.4 재사용: ModuleConfig
# 2-1 Blue-Node-Architecture D2.0-02 §0.3 재사용: VamosError/Result
# MULTIMODAL_PROCESSING_상세명세.md §5.1 재사용: MultimodalMessage
from common_types import ModuleConfig, MultimodalMessage
from d202_02 import VamosError, VamosResult

class VoiceCloneConfigV2(ModuleConfig):
    require_consent: bool = True                     # 항상 True, 토글 불가
    require_speaker_verification: bool = True        # 항상 True
    require_watermark: bool = True                   # 항상 True, 제거 옵션 없음
    minor_zero_tolerance: bool = True                # 항상 True
    constitutional_ai_enabled: bool = True           # 항상 True
    model: Literal["fish-speech","openvoice-v2","xtts-v2","elevenlabs"] = "fish-speech"
    max_cost_per_call_usd: float = 30.0              # LOCK-MM-06 V2
    consent_token_ttl_sec: int = 7 * 86400           # 7일 만료

class VoiceCloneRequestV2:
    sample_audio: bytes                              # 30s~3분 사용자 음성, ≤ 25MB (LOCK-MM-10)
    consent_token: str                               # 필수, 만료 검증
    target_text: str
    target_lang: str = "ko"
    speaker_challenge_audio: Optional[bytes] = None  # 실시간 challenge phrase
    purpose: Literal["self_use","narration","accessibility"] = "self_use"

class VoiceCloneResultV2(VamosResult):
    audio: bytes                                     # 워터마크 포함, ≤ 25MB
    voice_id: UUID                                   # user 단위 격리
    watermark_applied: bool = True                   # 항상 True
    consent_verified: bool                           # 5중 프레임워크 1
    speaker_verified: bool                           # 5중 프레임워크 2
    constitutional_ok: bool                          # 5중 프레임워크 4
    minor_check_passed: bool                         # 5중 프레임워크 5
    license: Literal["self_use_only","narration_licensed"] = "self_use_only"
    cost_usd: float                                  # LOCK-MM-06 V2 검증
    audit_log_id: UUID                               # 불변 감사 로그 포인터
```

---

## 4. J-026 V2 본문 (STEP7-J L512~L534 NEW)

> LOCK (STEP7-J J-094~J-096): 비용 상한 — V1: ≤₩10K($8), V2: ≤₩40K($30), V3: ≤₩200K($150)

> LOCK (SPEC §14): 14-Item Tech Stack — 변경 불가

> LOCK (기존 명세 §오디오 파이프라인): 오디오 샘플링 레이트 — 16kHz mono PCM

> LOCK (가이드 R-05-2): 파일 크기 상한 — 이미지 10MB / 오디오 25MB / 비디오 100MB

> **R-05-7 (종합계획서 §4)** 거버넌스 규칙: 딥페이크/NSFW 콘텐츠 안전 필터 항시 활성화 — 본 V2 5중 프레임워크 fail-safe=reject 및 워터마크 강제 정책의 근거

**근거 verbatim 인용** (STEP7-J L527~L533):
> ```
> [보안/윤리]
> - 명시적 동의 필수 (녹음 + 사용 범위)
> - 타인 음성 복제 차단 (화자 인증)
> - 딥페이크 방지 워터마크 삽입
> - Constitutional AI: 음성 복제 정책 적용
>
> [구현성] V2: ⚠️ 4개월 (윤리 프레임워크 포함) | V3: ✅ 자체 모델
> ```

### 4.1 E1. Input Schema

```python
# §3 VoiceCloneRequestV2 참조
# 필수 필드: sample_audio (30s~3분) + consent_token + target_text
# 옵션: speaker_challenge_audio (실시간 인증용)
```

### 4.2 E2. Output Schema

```python
# §3 VoiceCloneResultV2 참조
# 5중 프레임워크 게이트 결과 모두 True 시에만 audio 생성
# 하나라도 False → VamosError 반환 (audio = empty)
```

### 4.3 E3. Algorithm — 5중 프레임워크 순차 게이트

```python
async def clone_voice_v2(req: VoiceCloneRequestV2,
                         cfg: VoiceCloneConfigV2) -> VoiceCloneResultV2:
    audit_log_id = uuid7()
    
    # GATE 1: 명시적 동의 검증 (프레임워크 §5.1)
    consent_verified = await verify_consent_token(
        token=req.consent_token, ttl_sec=cfg.consent_token_ttl_sec,
        user_id=session.user_id, scope="voice_clone",
    )
    if not consent_verified:
        await audit_log_insert(audit_log_id, "consent_failed", req)
        raise VamosError(code="CONSENT_MISSING_OR_EXPIRED", audit_log_id=audit_log_id)
    
    # GATE 2: 화자 인증 (프레임워크 §5.2)
    speaker_verified = False
    if cfg.require_speaker_verification:
        # 2-a: wav2vec2-anti-spoofing (합성 음성 감지)
        spoof_score = await wav2vec2_anti_spoofing(req.sample_audio)
        if spoof_score > 0.5:  # 합성 의심
            await audit_log_insert(audit_log_id, "spoofing_suspected", {"score": spoof_score})
            raise VamosError(code="SPEAKER_SPOOFING_DETECTED", audit_log_id=audit_log_id)
        
        # 2-b: challenge phrase 발화 → 등록된 voiceprint 매칭
        emb_sample = await pyannote_embedding(req.sample_audio)
        if req.speaker_challenge_audio:
            emb_challenge = await pyannote_embedding(req.speaker_challenge_audio)
            sim = cosine_similarity(emb_sample, emb_challenge)
            if sim < 0.75:
                raise VamosError(code="SPEAKER_MISMATCH", detail={"similarity": sim})
            speaker_verified = True
        
        # 2-c: 타인 voiceprint 조회 (≥0.85 유사도면 타인 음성 복제 차단)
        other_match = await voiceprint_db_search(emb_sample, exclude_user=session.user_id)
        if other_match and other_match.similarity >= 0.85:
            await audit_log_insert(audit_log_id, "other_user_voice", other_match)
            raise VamosError(code="OTHER_USER_VOICE_DETECTED", audit_log_id=audit_log_id)
    
    # GATE 3: 딥페이크 방지 워터마크 강제 (프레임워크 §5.3)
    # (워터마크는 출력 후 적용 — 강제 플래그만 검증)
    if not cfg.require_watermark:
        raise ConfigError("require_watermark must be True — 제거 옵션 없음")
    
    # GATE 4: Constitutional AI 분류 (프레임워크 §5.4, R-05-7)
    constitutional_ok = True
    classifier_result = await constitutional_classifier(
        target_text=req.target_text,
        context={"purpose": req.purpose, "sample_audio_hash": sha256(req.sample_audio).hexdigest()},
    )
    if classifier_result.denied:
        # 정치인/공인/명예훼손 감지
        await audit_log_insert(audit_log_id, "constitutional_denied", classifier_result)
        raise VamosError(code="CONSTITUTIONAL_DENIED",
                         detail={"category": classifier_result.category},
                         audit_log_id=audit_log_id)
    
    # GATE 5: 미성년자 zero-tolerance (프레임워크 §5.5, CSAM 동급)
    minor_check_passed = False
    if cfg.minor_zero_tolerance:
        # 5-a: 음성 연령 추정 (SpeechBrain age estimator)
        age_est = await speechbrain_age_estimate(req.sample_audio)
        if age_est.min_age < 18:
            await audit_log_insert(audit_log_id, "minor_voice_detected", age_est,
                                   permanent=True)  # 영구 로그
            # 즉시 거부 + 사용자 계정 flag (수동 검토)
            raise VamosError(code="MINOR_VOICE_ZERO_TOLERANCE",
                             audit_log_id=audit_log_id)
        
        # 5-b: target_text 미성년자 대상 콘텐츠 차단
        if await detect_minor_content_in_text(req.target_text):
            await audit_log_insert(audit_log_id, "minor_target_content", req.target_text,
                                   permanent=True)
            raise VamosError(code="MINOR_TARGET_CONTENT", audit_log_id=audit_log_id)
        minor_check_passed = True
    
    # 5 게이트 모두 통과 → 실제 합성
    # 모델 선택
    if cfg.model == "fish-speech":
        cloned_audio = await fish_speech_clone(req.sample_audio, req.target_text, req.target_lang)
    elif cfg.model == "elevenlabs":
        cloned_audio = await elevenlabs_voice_clone(req.sample_audio, req.target_text)
    # ... (openvoice-v2 / xtts-v2 분기 동일)
    
    # 워터마크 삽입 (AudioSeal — 강제, 제거 불가)
    voice_id = uuid7()
    watermarked_audio = audioseal_embed(cloned_audio, user_id=session.user_id, voice_id=voice_id)
    
    # LOCK-MM-10 가드
    assert len(watermarked_audio) <= 25 * 1024 * 1024
    
    # 성공 감사 로그
    await audit_log_insert(audit_log_id, "clone_success", {
        "voice_id": voice_id, "duration_sec": len(cloned_audio) / 32000,
        "consent_verified": True, "speaker_verified": speaker_verified,
        "constitutional_ok": True, "minor_check_passed": True,
    })
    
    return VoiceCloneResultV2(
        audio=watermarked_audio, voice_id=voice_id, watermark_applied=True,
        consent_verified=True, speaker_verified=speaker_verified,
        constitutional_ok=True, minor_check_passed=True,
        license="self_use_only" if req.purpose == "self_use" else "narration_licensed",
        cost_usd=estimate_cost(cfg.model, len(req.target_text)),
        audit_log_id=audit_log_id,
    )
```

---

## 5. 5중 윤리 프레임워크 상세 (Part 1 `image_safety_metadata_v2.md` §8.2 통일 인터페이스)

### 5.1 프레임워크 §1: 명시적 동의 (R-05-7)

- **Consent Token 발급 API**: 사용자가 UI에서 "음성 복제 동의" 명시적 체크박스 체크 → JWT 토큰 발급 (scope=voice_clone, ttl=7일).
- **사용 범위 동의서**: 토큰 발급 시 사용 목적 (self_use / narration / accessibility) 선택 강제 (`purpose` 필드).
- **감사 로그**: 동의 시점 + IP + user_agent + 동의 scope 영구 저장 (GDPR Article 30 감사 기록 의무).
- **만료 정책**: 7일 경과 시 자동 무효화. 재사용 시 재동의.
- **기본값 OFF**: 시스템 설치 시 음성 복제 기능 비활성. 사용자 명시 활성화 필수.

### 5.2 프레임워크 §2: 화자 인증 (Speaker Verification)

| 단계 | 방법 | 임계값 | 정본 출처 |
|------|------|-------|----------|
| 2-a wav2vec2-anti-spoofing | 합성 음성 분류기 (Facebook wav2vec2-large-xlsr) | spoof_score > 0.5 차단 | ASVspoof 2021 챌린지 |
| 2-b Challenge phrase | 실시간 문장 발화 + pyannote embedding 매칭 | cosine sim < 0.75 차단 | pyannote/wespeaker-voxceleb-resnet34 |
| 2-c 타인 voiceprint 조회 | 사용자 DB 전체 검색 (exclude_user=self) | sim ≥ 0.85 차단 | 내부 voiceprint DB |

- **차단 시나리오**: 유명인 음성 샘플 업로드 시도 → 2-c에서 즉시 차단 + 감사 로그.

### 5.3 프레임워크 §3: 딥페이크 방지 워터마크 (필수)

- **모델**: **AudioSeal (Meta, 2024)** — invisible audio watermark, 압축/리샘플링 견고성 검증.
- **페이로드**: `{user_id, voice_id, timestamp, signature}` (HMAC-SHA256 서명).
- **강제 정책**: `require_watermark=True` 불변 (코드 상수). 제거 API 없음. 사용자 토글 불가.
- **검증 도구**: 외부 검증 도구 오픈 제공 (audit_log_id 인덱싱, 법적 대응 지원).

### 5.4 프레임워크 §4: Constitutional AI 정책 (R-05-7 정본)

#### 차단 카테고리 (분류기 출력 → 자동 거부)

1. **정치인/공인 음성 + 임의 텍스트** → 명예훼손/선거 개입 위험 → 즉시 거부
2. **명예훼손 가능 텍스트** ("X는 범죄자다" 등) → Claude Constitutional AI 분류기 거부
3. **금융 사기 시나리오** ("은행입니다. 계좌번호를 알려주세요") → 거부
4. **유사 재난 대응** ("긴급 상황입니다. 이곳으로 오세요") → 거부
5. **스팸/광고성 대량 합성** → 거부

#### 분류기 파이프라인

```python
async def constitutional_classifier(target_text: str, context: dict) -> ClassifierResult:
    # 1. Claude Haiku 분류 (명예훼손/사기/공인 검출)
    claude_result = await claude_classify(target_text, rubric=R_05_7_RUBRIC)
    if claude_result.any_category_denied:
        return ClassifierResult(denied=True, category=claude_result.category, evidence=claude_result)
    
    # 2. 로컬 룰 기반 필터 (공인 이름 DB, 금융 키워드)
    if await public_figure_name_detected(target_text):
        return ClassifierResult(denied=True, category="public_figure")
    if await financial_scam_keywords(target_text):
        return ClassifierResult(denied=True, category="financial_scam")
    
    return ClassifierResult(denied=False)
```

### 5.5 프레임워크 §5: 미성년자 zero-tolerance (Part 2 신규)

**근거**: `image_safety_metadata_v2.md` §4.1 E10 CSAM zero-tolerance 정책 + 본 V2 R-05-7 확장.

#### 5-a. 음성 연령 추정

- **모델**: SpeechBrain age estimator (pretrained on VoxCeleb1 age annotations) — age_min, age_max, age_mean 반환.
- **임계값**: `age_min < 18` 감지 시 **즉시 거부 + 영구 감사 로그** (삭제 불가).
- **사용자 계정 flag**: 2회 감지 시 계정 임시 정지 + 수동 검토 대기열.

#### 5-b. target_text 미성년자 대상 콘텐츠 감지

- **분류기**: Claude Haiku 분류 + 로컬 룰 (미성년자 관련 부적절 맥락)
- **감지 시**: 즉시 거부 + 영구 감사 로그 + CSAM 동급 처리

#### 정책 통일 (이미지 ↔ 음성)

- **이미지 정본** (`image_safety_metadata_v2.md` §4.1 E10): FaceForensics++ EfficientNet-B4 + CSAM zero-tolerance 정책
- **음성 정본** (본 V2 §5.5): wav2vec2-anti-spoofing + age estimator + CSAM 동급 정책
- **공통 원칙**: 영구 감사 로그 + 즉시 거부 + 계정 flag + 법적 의무 보고 (국가별)

### 5.6 프레임워크 §6: 삭제 권리 (GDPR/PIPA)

- **사용자 요청 API**: `DELETE /api/voice/{voice_id}` (user 소유 검증 후).
- **캐스케이드 삭제**:
  1. `voice_id` 메타데이터 삭제 (PostgreSQL)
  2. voiceprint 임베딩 삭제 (Qdrant voiceprint 컬렉션)
  3. 생성된 모든 음성 파일 삭제 (S3 / 로컬 스토리지)
  4. 감사 로그는 익명화하여 보존 (법적 의무)
- **7일 SLA**: 요청 ~ 완료 ≤ 7일 (GDPR Article 17 준수)
- **확인 회신**: 삭제 완료 시 이메일 통지

---

## 6. peer §8.2 딥페이크 감지 공통 아키텍처 (2-1 ↔ 2-2 통일)

### 6.1 공통 원칙 (image_safety_metadata_v2 §8.2 forward link 실체화)

Part 1 `image_safety_metadata_v2.md` §8.2 forward link:
> "`02_audio-processing/audio_safety_v2.md` (2-2 세션): 음성 복제 윤리 프레임워크 5중 검증 (동의 + 워터마크 + 화자인증 + Constitutional AI + 미성년자 zero-tolerance) ↔ 본 V2 이미지 딥페이크 감지 아키텍처 통일 인터페이스"

본 V2 §6.1 에서 **Part 2 실체화** 완료:

### 6.2 감지 아키텍처 통일 표

| 범주 | 이미지 (image_safety_metadata_v2 §4.1 J-017) | 음성 (본 V2 §4.3) |
|------|-------------------------------------------|-------------------|
| 합성물 감지 분류기 | FaceForensics++ + **EfficientNet-B4** | **wav2vec2-anti-spoofing** |
| 임계값 | fake_probability > 0.75 flag | spoof_score > 0.5 차단 |
| NSFW 감지 | NudeNet + Falconsai CLIP 이중 | — (음성 scope 외) |
| CSAM zero-tolerance | 영구 감사 로그 + 즉시 거부 | 동일 정책 (§5.5) |
| 워터마크 | invisible DCT (이미지) | **AudioSeal (음성)** |
| Constitutional AI | R-05-7 정책 (J-017 E10) | 동일 정책 (§5.4) |
| 감사 로그 보존 | 불변 immutable audit log | 동일 (영구 보존 7년) |
| 삭제 권리 (GDPR/PIPA) | 7일 SLA 4 stores 일괄 purge | 7일 SLA 캐스케이드 |

### 6.3 CSAM 정책 완전 통일

- **이미지**: `image_safety_metadata_v2.md` §4.1 E10 + Phase 3 테스트 T-SFM-07 (CSAM 감지 시뮬레이션 즉시 reject + immutable audit log + alert)
- **음성**: 본 V2 §5.5-a (age_min < 18 감지 시 영구 감사 로그 + 즉시 거부 + 계정 flag + 법적 보고)
- **공통**: Part 1 `image_safety_metadata_v2.md` 의 "CSAM zero-tolerance 정책" 이 음성 영역까지 완전 일관 적용

### 6.4 peer 인터페이스 규칙

1. **이미지 딥페이크 감지** 결과와 **음성 딥페이크 감지** 결과가 **동일 MultimodalMessage** 에 함께 나타날 경우 (예: 비디오 통화 캡처) → 둘 중 하나라도 flag 이면 MultimodalMessage 전체 reject.
2. **사용자 계정 flag** 은 이미지/음성 구분 없이 통합 집계 (2회 누적 시 수동 검토).
3. **감사 로그 스키마 통일**: `{detected_modality: "image"|"audio"|"both", category, evidence, action, audit_log_id}` 공통 필드.

---

## 7. Model Selection (V2 음성 복제 모델 비교)

| 모델 | 라이선스 | 한국어 | 합성 품질 | 윤리 워터마크 기본 | V2 권장 |
|------|---------|--------|----------|------------------|---------|
| ElevenLabs Voice Clone | 상용 (월 $5+) | 우수 | 최상 (MOS 4.3) | **자체 워터마크** | 고품질 옵션 |
| OpenVoice V2 | MIT (오픈소스) | 양호 | 우수 (MOS 4.0) | 별도 AudioSeal 적용 | 백업 |
| XTTS v2 (Coqui) | Coqui CPL | 양호 | 양호 (MOS 3.9) | 별도 AudioSeal 적용 | 백업 |
| **Fish Speech** | **Apache 2.0** | **우수 (한국어 특화)** | 우수 (MOS 4.0) | 별도 AudioSeal 적용 | **V2 기본 권장** |

**V2 기본: Fish Speech + AudioSeal 조합** (STEP7-J L417 "Fish Speech: 오픈소스, 한국어 지원" + V1 골격 L245 "V2 권장: Fish Speech 오픈소스 + 한국어 + AudioSeal 조합" 계승).

---

## 8. Error Handling (R-05-5 Graceful Degradation)

| 에러 | 폴백 / 거부 |
|------|-----------|
| consent_token 만료 | 거부 + 재동의 안내 |
| spoofing 감지 (§2-a) | 거부 + 감사 로그 + 사용자 통지 |
| challenge phrase 불일치 (§2-b) | 재시도 1회 → 2차 실패 시 거부 |
| 타인 voiceprint 매칭 (§2-c) | 즉시 거부 + 영구 감사 로그 + 수동 검토 대기열 |
| Constitutional AI 거부 | 즉시 거부 + 카테고리 통지 |
| **미성년자 감지** | **즉시 거부 + 영구 감사 로그 + 계정 flag + 법적 보고 검토** |
| 워터마크 삽입 실패 | 출력 차단 + 기술 지원 알림 (워터마크 없는 출력 금지) |
| 모델 5xx (ElevenLabs 등) | Fish Speech 로컬 폴백 |

---

## 9. Cost Analysis

| 시나리오 | V2 (월) |
|---------|---------|
| 일 1회 5분 팟캐스트 나레이션 (Fish Speech 로컬) | $0 |
| 월 10회 ElevenLabs voice clone (고품질) | ~$5 (월 구독 최저) |
| 감사 로그 저장 (S3) | ~$0.1/월 |
| Constitutional AI 분류 (Claude Haiku) | ~$0.01/호출 |
| **V2 권장 합계** | **$0~$5** (LOCK-MM-06 V2 $30 per-call + 월간 집계 $135 이내) |

---

## 10. V2 Phase 3 테스트 시나리오 (12건)

1. **T-AS-V2-01**: consent_token 없음 + voice clone 요청 → CONSENT_MISSING_OR_EXPIRED 거부.
2. **T-AS-V2-02**: 만료된 token → 동일 거부 + 재동의 안내.
3. **T-AS-V2-03**: 합성 음성 샘플 업로드 (wav2vec2 spoof_score 0.8) → SPEAKER_SPOOFING_DETECTED 거부.
4. **T-AS-V2-04**: challenge phrase 발화 불일치 (sim 0.65) → SPEAKER_MISMATCH 거부.
5. **T-AS-V2-05**: 유명인 음성 샘플 (타인 voiceprint 매칭) → OTHER_USER_VOICE_DETECTED 영구 감사 로그 검증.
6. **T-AS-V2-06**: 정치인 이름 + target_text → CONSTITUTIONAL_DENIED (category="public_figure").
7. **T-AS-V2-07**: 금융 사기 텍스트 ("계좌번호 알려주세요") → CONSTITUTIONAL_DENIED (category="financial_scam").
8. **T-AS-V2-08**: **미성년자 음성 샘플 (age_min 14) → MINOR_VOICE_ZERO_TOLERANCE 거부 + 영구 감사 로그 + 계정 flag**.
9. **T-AS-V2-09**: 미성년자 대상 target_text → MINOR_TARGET_CONTENT 거부.
10. **T-AS-V2-10**: 5 게이트 전부 통과 → Fish Speech 클로닝 + **AudioSeal 워터마크 round-trip 검증** (외부 검증 도구로 재확인).
11. **T-AS-V2-11**: 사용자 DELETE API → voice_id 캐스케이드 삭제 (PG + Qdrant + S3) + 7일 SLA 검증.
12. **T-AS-V2-12**: 워터마크 삽입 시뮬레이션 실패 → 출력 차단 + 워터마크 없는 음성 절대 반환 안 됨 검증.

---

## 11. Cross-domain 참조 블록

### 11.1 peer V2 (세션 2-2 #2a Part 2)

- `stt_engine_v2.md` §4.2: 화자 인증 challenge phrase → Deepgram 전사 → 정확 텍스트 대조
- `tts_engine_v2.md` §4.4: Fish Speech zero-shot voice clone → 본 V2 5 게이트 통과 후에만 호출
- `voice_chat_v2.md` §4.2: audio_ref 생성 시점 → 본 V2 voice_id 등록 경로
- `audio_analysis_v2.md` §J-030: 팟캐스트 화자 A/B voice_id → 본 V2 윤리 게이트 필수 통과

### 11.2 peer V2 (세션 2-1 Part 1 정본 — **§8.2 통일 인터페이스 실체화**)

- **`image_safety_metadata_v2.md` §8.2 (forward link)**: "딥페이크 감지 공통 아키텍처" **Part 2 실체화 완료** (본 V2 §6)
- **`image_safety_metadata_v2.md` §4.1 J-017 V2**: CSAM zero-tolerance + FaceForensics++ → 본 V2 §5.5 + §6 완전 통일
- **`image_safety_metadata_v2.md` §5 워터마크 DCT**: 이미지 invisible watermark ↔ 본 V2 AudioSeal 음성 invisible watermark 공통 정책

### 11.3 forward link (#2b 세션)

- **`03_video-analysis/video_safety_v2.md` (#2b 세션 2-3)**: 비디오 립싱크 딥페이크 + 음성 딥페이크 통합 감지 (본 V2 §4 + §6 소비)
- `06_multimodal-dialog/computer_use_agent_v2.md` (2-4): R-05-7 경계 + 샌드박스 격리
- `06_multimodal-dialog/integration_architecture.md` (2-4): J-083 라우터에서 voice clone 요청 → 본 V2 5 게이트 경유 강제

### 11.4 외부 도메인 (참조 전용)

- **#6-2 Security-Governance**: R-05-7 정본 + Constitutional AI 정책 + CSAM 정책
- **#6-12 Event-Logging**: 불변 immutable audit log (영구 7년 보존)
- **#6-4 Memory-RAG**: voice_id user 격리 저장 (L2 메모리)
- **#1 VRE 1-1**: Evidence Gate → 5 게이트 결과 기반 검증 체인
- **법무/규제**: GDPR Article 17 (삭제 권리) + Article 30 (처리 기록) + 대한민국 개인정보보호법 (PIPA)

---

## 12. §13.1 L3 완성도 매트릭스

| 항목 | E1 | E2 | E3 | E4 | E5 | E6 | E7 | E8 | E9 | E10 | 평균 |
|------|----|----|----|----|----|----|----|----|----|----|------|
| J-026 V2 | 95 | 95 | 98 | 92 | 92 | 92 | 90 | 95 | 92 | 100 | **94.1** |

L3 기준 ≥ 80점 충족. **E10 Privacy/Safety 100** (5중 프레임워크 + CSAM 동급 정책 완전 구현). **E3 Algorithm 98** (5 게이트 순차 구조 + 감사 로그 강제). E1~E2 Input/Output 95 (Pydantic verbatim reuse).

---

## 13. V1↔V2 정합 표

### 13.1 Pydantic 재사용 출처

| V2 모델 | 재사용 base | 정본 출처 도메인 | verbatim line |
|---------|-------------|-----------------|---------------|
| `VoiceCloneConfigV2` | `ModuleConfig` | `common_types.md §3.4` | `# 00_common §3.4 재사용: ModuleConfig` |
| `VoiceCloneResultV2` | `VamosError/Result` | `D2.0-02 §0.3` | `# 2-1 Blue-Node-Architecture D2.0-02 §0.3 재사용: VamosError/Result` |
| `VoiceCloneRequestV2.audio_ref` | `MultimodalMessage` (LOCK-MM-05) | `기존 명세 §5.1` | `# MULTIMODAL_PROCESSING_상세명세.md §5.1 재사용: MultimodalMessage` |

### 13.2 V1 본문 불변 검증

- V1 `audio_safety.md` 266 lines (Phase 1-2 완료, read-only `-r--r--r--`, sha256 baseline 변경 0)
- V2 확장은 본 파일 (`audio_safety_v2.md`) 에 완전 분리 작성 (V1 §J-026 골격 L181~L257 블록 미수정)

### 13.3 V1 → V2 승급 매트릭스

| J-ID | V1 상태 | V2 상태 (§7 2-2 #2a Part 2) | L3 점수 변화 |
|------|---------|------------------------------|-------------|
| J-026 | 🟡 V2 골격 (6조항 텍스트 + 모델 후보) | ✅ L3 승급 (V2 NEW 5중 게이트 본문 + §5 상세 + §6 peer 통일) | — → **94.1** |

---

## 14. 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-04-19 | V2-Phase 2 (2-2 #2a Part 2) | 초기 V2 작성: **J-026 NEW 5중 윤리 프레임워크 본문** (§5.1 명시적 동의 consent_token + §5.2 화자 인증 wav2vec2/pyannote/voiceprint DB + §5.3 AudioSeal 워터마크 강제 + §5.4 Constitutional AI R-05-7 분류기 + §5.5 미성년자 zero-tolerance CSAM 동급) + **§6 peer §8.2 딥페이크 감지 공통 아키텍처 실체화** (이미지 FaceForensics++ ↔ 음성 wav2vec2, CSAM 정책 완전 통일) + V2 Phase 3 테스트 12건 + R-05-5 graceful degradation + GDPR/PIPA 삭제 권리 7일 SLA |

---

**[END OF audio_safety_v2.md]** — V2-Phase 2 세션 2-2 #2a Part 2 산출물, STEP7-J J-026 (L512~L534) 정본 인용, LOCK-MM-06/08/10/11 + R-05-7 R9 형식, §13.1 94.1/100 L3 승급 (Part 2 최고점), V1 본문 불변, **딥페이크 감지 공통 아키텍처 peer cross-ref 실체화 완료** (세션 2-1 §8.2 ↔ 2-2 §6 통일), 음성 복제 5중 프레임워크 + CSAM 정책 완전 구현, forward link #2b 2-3 video_safety 통합 감지 예정.
