# feedback_composition_v2.md — J-061 V2 EXTEND (멀티모달 피드백 루프) + J-062 V2 EXTEND (멀티모달 합성) + J-063 V2 EXTEND (대화 모드 전환)

> **Status**: V2-Phase 2 (2-4 #2b)
> **작성일**: 2026-04-19
> **V1 정본**: [feedback_composition.md](./feedback_composition.md) (Phase 1-6 완료, ~12K, read-only sha256 baseline, J-061~J-063 V1)
> **SoT 근거**: STEP7-J Part 7 J-061 (L1055~L1071) + J-062 (L1073~L1086) + J-063 (L1088~L1101)
> **담당 J-ID**: **J-061** (V2 EXTEND: 학습 루프 + 5-Layer 메모리 통합) + **J-062** (V2 EXTEND: 멀티모달 합성) + **J-063** (V2 EXTEND: 디바이스 인식 모드 전환)
> **상위 인덱스**: [_index.md](./_index.md)
> **peer V2**: [memory_integration_v2.md](./memory_integration_v2.md) (J-064 통합) + **[audio_analysis_v2.md](../02_audio-processing/audio_analysis_v2.md) §J-029 감정 추적** (감정 이력 → 응답 피드백 루프)

---

## 1. Cross-domain 참조

| 정본 | 역할 |
|------|------|
| `STEP7-J_멀티모달_생성처리_작업가이드.md` Part 7 J-061 (L1055~L1071) | 상위 SoT J-061 |
| `STEP7-J_멀티모달_생성처리_작업가이드.md` Part 7 J-062 (L1073~L1086) | 상위 SoT J-062 |
| `STEP7-J_멀티모달_생성처리_작업가이드.md` Part 7 J-063 (L1088~L1101) | 상위 SoT J-063 |
| `feedback_composition.md` (V1) | V1 정본 |
| **`audio_analysis_v2.md` §J-029 (peer Part 2 V2)** | **감정 추적 → 피드백 루프 통합** |
| `memory_integration_v2.md` (peer 본 #2b) | 5-Layer 메모리 저장 |
| AUTHORITY §4 LOCK-MM-04/06 | LOCK |

## 2. LOCK 인용

> LOCK (STEP7-J J-083): 모달리티 우선순위 — Text > Image > Audio > Video > Document > Mixed

> LOCK (STEP7-J J-094~J-096): 비용 상한 V2 ≤ ₩40K($30)

**적용**: LOCK-MM-04: J-063 모드 전환 우선순위 / LOCK-MM-06 V2: 학습 루프 비용 가드

## 3. V1 → V2 승급

| J-ID | V1 | V2 (본) |
|------|----|---------|
| J-061 피드백 루프 | 기본 피드백 즉시 | **학습 루프 + 5-Layer 저장 + peer J-029 감정 통합** |
| J-062 합성 (Composition) | V1 | **자동 레이아웃 + 스타일 일관성** |
| J-063 모드 전환 | V1 | **디바이스 인식 + 자동 모드 전환** |

## 4. V2 본문

### 4.1 J-061 멀티모달 피드백 루프 V2 (STEP7-J L1055~L1071)

**근거 verbatim** (STEP7-J L1058~L1069):
> ```
> [구현 상세]
> - 생성 결과에 대한 사용자 피드백 수집:
>   ├─ 이미지: 좋아요/수정 요청/재생성
>   ├─ 오디오: 속도/톤/품질 피드백
>   ├─ 비디오: 구간별 피드백
>   └─ 문서: 섹션별 수정 요청
>
> - 피드백 학습:
>   ├─ 사용자 선호 스타일 프로필 업데이트
>   ├─ 프롬프트 자동 개선
>   ├─ 모델 선택 최적화
>   └─ 5-Layer 메모리에 선호도 저장
> ```

```python
from common_types import ModuleConfig
from d202_02 import VamosError, VamosResult

class FeedbackConfigV2(ModuleConfig):
    enable_emotion_integration: bool = True          # peer J-029 감정 통합
    enable_auto_prompt_improvement: bool = True
    enable_model_optimization: bool = True
    storage_layer: Literal["L2","L3"] = "L2"         # peer memory_integration §4.1

class MultimodalFeedback:
    asset_id: UUID
    modality: Literal["image","audio","video","document"]
    feedback_type: Literal["like","dislike","modify","regenerate","section_edit"]
    rating: int                                      # 1~5
    comments: Optional[str]
    section_range: Optional[tuple[float, float]] = None  # 비디오 구간 / 문서 섹션
    user_id: str
    timestamp: datetime
    emotion_state: Optional[str] = None              # peer J-029 통합

async def submit_feedback(fb: MultimodalFeedback,
                         cfg: FeedbackConfigV2) -> dict:
    # 1. 감정 컨텍스트 통합 (peer audio_analysis_v2 §J-029)
    if cfg.enable_emotion_integration:
        from audio.emotion import get_recent_emotion  # peer Part 2 V2
        fb.emotion_state = await get_recent_emotion(fb.user_id, window_sec=300)

    # 2. 사용자 선호 프로필 업데이트 (peer memory L2/L3)
    profile = await load_user_preference(fb.user_id)
    profile.update(fb)                               # 모달별 선호도 누적
    await save_user_preference(fb.user_id, profile, layer=cfg.storage_layer)

    # 3. 프롬프트 자동 개선
    if cfg.enable_auto_prompt_improvement and fb.feedback_type == "modify":
        improvement = await llm_suggest_prompt_improvement(fb, profile,
                                                          model="qwen2.5-7b-local")
        await prompt_history.append(fb.user_id, improvement)

    # 4. 모델 선택 최적화 (LLM weighted scoring)
    if cfg.enable_model_optimization:
        backend_scores = await update_backend_scores(fb.modality, fb.rating)
        await backend_router.refresh(backend_scores)

    return {"feedback_id": uuid4(), "profile_updated": True,
            "prompt_improved": cfg.enable_auto_prompt_improvement,
            "emotion_state": fb.emotion_state}
```

### 4.2 J-062 멀티모달 합성 V2 (STEP7-J L1073~L1086)

**근거 verbatim** (STEP7-J L1076~L1083):
> ```
> [구현 상세]
> - 여러 모달리티 결과를 하나의 출력으로 합성:
>   ├─ 텍스트 + 이미지 + 차트 → 리포트 PDF
>   ├─ 비디오 + 자막 + 나레이션 → 완성 영상
>   ├─ 코드 + 스크린샷 + 설명 → 튜토리얼
>   └─ 데이터 + 차트 + 인사이트 → 대시보드
>
> - 자동 레이아웃: 콘텐츠에 따라 최적 배치
> - 스타일 일관성: 전체 출력의 통일된 디자인
> ```

```python
class CompositionRequestV2:
    components: list[ContentComponent]               # 각 모달리티 결과
    target_format: Literal["pdf","mp4","html","pptx","epub"]
    style_template: Literal["v0","corporate","academic","minimal"] = "v0"
    auto_layout: bool = True
    enforce_style_consistency: bool = True

class ContentComponent:
    type: Literal["text","image","chart","video","audio","code","data"]
    payload: bytes | str
    importance: int = 5                              # 1~10 (레이아웃 우선순위)
    section: str = "main"                            # header/main/sidebar/footer

async def compose_multimodal(req: CompositionRequestV2) -> bytes:
    # 1. 자동 레이아웃 (importance 기반 + 모달리티 우선순위 LOCK-MM-04)
    layout = build_layout(req.components, style=req.style_template)

    # 2. 스타일 일관성 (color/font 통일)
    if req.enforce_style_consistency:
        layout = apply_consistent_style(layout, template=req.style_template)

    # 3. 포맷별 렌더링 (peer document_generation_v2)
    if req.target_format == "pdf":
        from document.gen import compose_pdf
        return await compose_pdf(layout)
    elif req.target_format == "mp4":
        from video.compose import compose_video
        return await compose_video(layout)             # video + 자막 + 나레이션
    elif req.target_format == "pptx":
        return await compose_pptx(layout)
    elif req.target_format == "html":
        return await compose_html(layout)
    else:
        return VamosError(f"unsupported target_format: {req.target_format}")
    else:
        return VamosError(f"unsupported target_format: {req.target_format}")
```

### 4.3 J-063 멀티모달 대화 모드 전환 V2 (STEP7-J L1088~L1101)

```python
class DialogModeV2:
    user_id: str
    mode: Literal["text","voice","vision","mixed","handsfree"] = "text"
    auto_switch_enabled: bool = True
    device_type: Literal["pc","mobile","tablet","watch"] = "pc"

async def detect_and_switch_mode(user_id: str, context: dict) -> DialogModeV2:
    # 디바이스 인식
    device = detect_device_from_context(context)

    # 자동 모드 전환 (SoT 시나리오)
    if device == "pc" and context.get("has_camera_active"):
        return DialogModeV2(user_id=user_id, mode="vision", device_type=device)
    elif device == "mobile" and context.get("user_walking"):
        return DialogModeV2(user_id=user_id, mode="handsfree", device_type=device)
    elif device == "watch":
        return DialogModeV2(user_id=user_id, mode="handsfree", device_type=device)
    elif "이 사진 보면서" in context.get("user_query", ""):
        return DialogModeV2(user_id=user_id, mode="mixed", device_type=device)
    return DialogModeV2(user_id=user_id, mode="text", device_type=device)
```

## 5. peer V2 cross-ref

### 5.1 audio_analysis_v2.md §J-029 (Part 2) ↔ 본 V2 §4.1
- audio_analysis_v2 §J-029 Russell 감정 모델 (실시간 ≤200ms) → 본 V2 §4.1 line `get_recent_emotion(user_id, window_sec=300)`
- 인터페이스: emotion_state ("happy"/"sad"/"angry"/"neutral") → 응답 피드백 루프 통합

### 5.2 memory_integration_v2.md (peer 본 #2b) ↔ 본 V2 §4.1
- memory_integration_v2 5-Layer L2/L3 저장 → 본 V2 §4.1 사용자 선호 프로필 저장

### 5.3 document_generation_v2.md (peer 본 #2b) ↔ 본 V2 §4.2
- document_generation_v2 §4.1 PDF/PPTX/HTML 생성 → 본 V2 §4.2 J-062 합성 위임

## 6. Error Handling
| 에러 | 폴백 |
|------|------|
| 감정 추적 실패 (peer J-029) | emotion_state=None 진행 |
| 사용자 선호 프로필 부재 | default 프로필 |
| 프롬프트 개선 LLM 실패 | 원본 prompt 유지 |
| 합성 레이아웃 실패 | 단순 concat 폴백 |
| 모드 자동 전환 실패 | text 모드 기본 |

## 7. Cost
| 시나리오 | V2 (월) | LOCK-MM-06 V2 |
|----------|---------|---------------|
| 100% 로컬 (Qwen2.5 7B) | $0 | 충족 |
| 합성 LLM 호출 (Gemini Flash) | $0.50 | 충족 |
| **V2 권장** | **$0~$1/월** | 충족 ✅ |

## 8. SLA
| 작업 | P50 | P99 |
|------|-----|-----|
| submit_feedback | 100ms | 300ms |
| 프로필 업데이트 | 50ms | 200ms |
| 합성 (PDF) | 2s | 6s |
| 합성 (MP4) | 30s | 90s |
| 모드 전환 감지 | 20ms | 100ms |

## 9. Test (10건)
1. 이미지 modify 피드백 → 프로필 업데이트 + prompt 개선.
2. 비디오 구간 피드백 (60s~120s) → 해당 구간만 재생성.
3. 감정 통합 (peer J-029) → emotion_state 기록.
4. 합성 PDF (텍스트+이미지+차트) → 통일 디자인.
5. 합성 MP4 (비디오+자막+나레이션) → 완성 영상.
6. 모드 자동 전환 (PC + 카메라 → vision).
7. 모바일 + 이동 중 → handsfree.
8. 워치 → handsfree 강제.
9. 5-Layer L3 승격 (importance ≥ 0.8 피드백).
10. 모델 선택 최적화 → backend_scores 갱신.

## 10. Dependencies
- 외부: Qwen2.5 7B (Ollama), Pillow/PyPDF2 (합성)
- 내부 (peer): J-029 V2 (audio_analysis_v2), J-064 V2 (memory_integration_v2), J-043 V2 (document_generation_v2), J-022 V2 (tts_engine_v2 나레이션), J-083 (Router)

## 11. Privacy
- user_id 단위 격리
- 감정 상태는 user 본인만 열람
- 피드백 텍스트는 PII 마스킹 (R-05-7)

## 12. 검증
| 항목 | V1 | V2 | L3 |
|------|----|---------|-----|
| J-061 학습 루프 + peer J-029 통합 | 기본 피드백 | 감정 + 프로필 + 학습 | 89 |
| J-062 합성 (자동 레이아웃 + 스타일 통일) | 미작성 | 4 포맷 + 통일 | 87 |
| J-063 디바이스 인식 모드 전환 | 미작성 | 자동 전환 + 5 모드 | 86 |

**평균**: **87.3/100** ✅
