# Multimodal Emotion Fusion — 멀티모달 감정 융합 (텍스트+음성+영상) (V3)

| 항목 | 값 |
|------|-----|
| **파일** | `01_emotion-recognition/multimodal_emotion_fusion.md` |
| **P-ID** | P-001-V3 (멀티모달 감정 융합) |
| **V단계** | **V3 (Phase 4 production-ready 정본)** |
| **Status** | **APPROVED** |
| **Level** | **L3 COMPLETE (E1~E10 9요소, 88점)** |
| **LOCK 참조** | LOCK-HW-01, LOCK-HW-02, LOCK-HW-12 (in-domain) + LOCK-MM-07, LOCK-MM-08 (3-2 cross) |
| **SOT 출처** | STEP7-P P-001 (L16~L22) + 종합계획서 §6.1 + §3.4 |
| **cross-domain** | 3-2 Multimodal (LOCK-MM-07 CLIP 768d / LOCK-MM-08 16kHz mono PCM, DEFINED-HERE 4번째 활성) / ★ 3-5 Education 감정 연동 (R-09-6 opt-in) |
| **태그** | V3-Phase 3 / Phase 4 production 승급 |
| **ReadOnly** | RW (Sub-B P4-7 도메인 종료 시 RO 정책 일괄 확정) |
| **최종 갱신** | 2026-06-01 (Phase 4 RECOVERY Sub-A genuine write, P4-1) |

---

## §1. 개요 (Purpose/Scope)

멀티모달 감정 융합 모듈은 **텍스트(KoBERT) + 음성(SER) + 영상(FER)** 3개 모달리티의 감정 인식 결과를 융합하여, 단일 모달리티 대비 견고하고 정확한 감정 분류를 산출한다. 출력은 LOCK-HW-01 12감정 분류 + arousal/valence 2차원 + LOCK-HW-12 1-10 강도 척도를 따른다. 모든 감정 데이터는 LOCK-HW-02 PRIVATE 등급으로 **로컬 전용**이며 외부 전송이 금지된다(R-09-3).

**V3 범위 (본 문서)**:
- §3 3-모달리티 입력 파이프라인 (텍스트/음성/영상) + LOCK-MM-07/08 정합
- §4 융합 전략 비교 (Late vs Early vs Hybrid fusion) + E4 모델 비교
- §5 LOCK-HW-01 12감정 + arousal/valence + LOCK-HW-12 1-10 출력 스키마
- §6 ★ 3-5 Education 감정 연동 (R-09-6 opt-in) + E5 Graceful Degradation 폴백 + E6 Privacy
- §7 E1~E10 L3 완전성 + 운영 baseline (멀티모달 ≥ 90%, p95 ≤ 500ms)

---

## §2. 교차 참조 (선행 Read 필수)

| 참조 대상 | 파일 | 관계 | 필수 섹션 |
|-----------|------|------|-----------|
| 텍스트 감정 분석 V2 | `text_emotion_analysis.md` | 텍스트 모달리티 base | 전체 |
| 음성 감정 인식 V2 (RO) | `speech_emotion_recognition.md` | 음성 모달리티 base | §2 |
| 감정 패턴 학습 (RO) | `emotion_pattern_learning.md` | 융합 결과 소비자 | §2 |
| LOCK 정본 | `../AUTHORITY_CHAIN.md` | LOCK-HW-01/02/12 §3 | §3.1~§3.3 |
| 3-2 멀티모달 정본 | `../../3-2_Multimodal-Processing/AUTHORITY_CHAIN.md` | LOCK-MM-07/08 (§3.4 L68-L69) | §3.4 |
| 3-5 감정 연동 인터페이스 | `../../3-5_Education-Learning/01_adaptive-learning/emotion_learning_interface.md` | CONSUMER (R-09-6) | §3~§7 |
| 상위 SoT | `D:/VAMOS/docs/sot/STEP7-P_건강_웰니스_감성AI_작업가이드.md` | P-001 V3 정본 (L16~L22) | Part 1 |

---

## §3. 3-모달리티 입력 파이프라인 (E1 Input / E3 Pipeline)

### §3.1 LOCK 인용 (정본 — 본 문서 재정의 0)

AUTHORITY_CHAIN §3 in-domain LOCK 정본 verbatim:
> LOCK (LOCK-HW-01): 기본7(기쁨,슬픔,분노,불안,놀람,혐오,중립)+세부5(피로,스트레스,좌절,열정,호기심)+차원2(arousal,valence)

> LOCK (LOCK-HW-02): 감정=PRIVATE(로컬전용), 건강=PROTECTED(AES-256+별도PIN), 의료=HIGHEST(외부전송절대금지)

> LOCK (LOCK-HW-12): 1-10 정수 척도

3-2 Multimodal AUTHORITY §3.4 cross-domain LOCK 정본 verbatim (DEFINED-HERE Phase 5 동결 — 본 문서 인용만):
> LOCK (LOCK-MM-07): 768d (ViT-L/14@336)

> LOCK (LOCK-MM-08): 16kHz mono PCM

### §3.2 모달리티별 입력 스키마 (E1)

| 모달리티 | 모델 | 입력 정규화 | LOCK 정합 | 출력 |
|----------|------|------------|-----------|------|
| 텍스트 | KoBERT (V1 base) + V3 한국어 미세조정 | UTF-8 토큰 (max 512) | LOCK-HW-01 12감정 logits | 12감정 분포 + arousal/valence |
| 음성 (SER) | Wav2Vec2 + Speech Emotion Diarization | **16kHz mono PCM** (LOCK-MM-08) | LOCK-MM-08 EXACT | 12감정 분포 + 발화 단위 |
| 영상 (FER) | FaceNet + OpenFace 2.x (Affectiva 대안) | 프레임 → **768d ViT-L/14@336** 임베딩 (LOCK-MM-07) | LOCK-MM-07 EXACT | 12감정 분포 + AU 강도 |

### §3.3 융합 파이프라인 (E3)

```
[멀티모달 융합 파이프라인]
텍스트 입력 ──→ KoBERT ──────┐
                              │
음성 입력 (16kHz) ─→ Wav2Vec2 ┼─→ [모달리티 정합성 검사] ─→ [융합 엔진]
                              │         (신뢰도 가중)        (§4 Late/Early/Hybrid)
영상 입력 (768d) ──→ FER ─────┘                                  │
                                                                  ▼
                          12감정 분포 + arousal/valence + intensity(1-10)
                                                                  │
                              ┌───────────────────────────────────┤
                              ▼                                    ▼
                    [PRIVATE 로컬 저장]              ★ [3-5 감정 연동 (R-09-6 opt-in)]
                    (LOCK-HW-02, R-09-3)              category+강도+a/v만 (원시 금지)
```

---

## §4. 융합 전략 비교 (E4 Model Comparison)

### §4.1 Late vs Early vs Hybrid fusion

| 전략 | 융합 위치 | 장점 | 단점 | 채택 |
|------|----------|------|------|------|
| **Late fusion** | 각 모달리티 분류 결과(12감정 분포)를 신뢰도 가중 평균 | 모달리티 독립, 단일 실패 견고, 폴백 용이 | 모달리티 간 상호작용 미반영 | ✅ 기본 (V3) |
| **Early fusion** | 멀티모달 임베딩을 통합 후 단일 분류기 | 모달리티 상호작용 포착 | 한 모달리티 결측 시 전체 영향, 정렬 비용 | △ 보조 |
| **Hybrid fusion** | Early(임베딩 attention) + Late(결정 가중) 결합 | 정확도 최상 | 계산 비용·복잡도 ↑ | ◎ Phase 5 목표 |

### §4.2 Late fusion 가중 산식 (V3 기본)

```python
from dataclasses import dataclass

@dataclass
class ModalityResult:
    distribution: dict[str, float]   # 12감정 → 확률 (LOCK-HW-01)
    arousal: float                   # -1.0 ~ 1.0
    valence: float                   # -1.0 ~ 1.0
    confidence: float                # 0.0 ~ 1.0 (모달리티 자체 신뢰도)
    available: bool                  # 모달리티 가용 여부 (E5 폴백)

def late_fusion(results: list[ModalityResult]) -> dict:
    """
    신뢰도 가중 Late fusion.
    가용 모달리티만 사용 (E5 Graceful Degradation).
    시간복잡도: O(m·k) — m=모달리티 수(≤3), k=12감정.
    """
    active = [r for r in results if r.available]
    if not active:
        raise FusionError("모든 모달리티 결측 — 폴백 불가")
    total_w = sum(r.confidence for r in active)
    fused = {emo: 0.0 for emo in EMOTIONS_12}   # LOCK-HW-01 12감정
    for r in active:
        for emo, p in r.distribution.items():
            fused[emo] += p * (r.confidence / total_w)
    arousal = sum(r.arousal * r.confidence for r in active) / total_w
    valence = sum(r.valence * r.confidence for r in active) / total_w
    return {"distribution": fused, "arousal": arousal, "valence": valence}
```

---

## §5. 출력 스키마 (E2 Output)

### §5.1 12감정 + arousal/valence + intensity(1-10)

```python
from pydantic import BaseModel, conint, confloat
from typing import Literal

EMOTIONS_12 = [
    "기쁨","슬픔","분노","불안","놀람","혐오","중립",   # PRIMARY 7 (LOCK-HW-01)
    "피로","스트레스","좌절","열정","호기심",             # SECONDARY 5 (LOCK-HW-01)
]

class FusedEmotion(BaseModel):
    """멀티모달 융합 감정 출력 — PRIVATE 등급 (LOCK-HW-02)"""
    primary: Literal["기쁨","슬픔","분노","불안","놀람","혐오","중립","피로","스트레스","좌절","열정","호기심"]    # 최고 확률 감정 (LOCK-HW-01 12감정)
    distribution: dict[str, confloat(ge=0, le=1)]
    arousal: confloat(ge=-1, le=1)          # 차원2 (LOCK-HW-01)
    valence: confloat(ge=-1, le=1)          # 차원2 (LOCK-HW-01)
    intensity: conint(ge=1, le=10)          # LOCK-HW-12 1-10 정수 척도
    fusion_strategy: Literal["late","early","hybrid"]
    modalities_used: list[Literal["text","speech","video"]]
    privacy_grade: Literal["PRIVATE"] = "PRIVATE"   # LOCK-HW-02 강제
```

> **LOCK-HW-12 정합**: arousal/valence는 연속값(-1~1)이나, 사용자 노출 강도(intensity)는 **1-10 정수 척도**로 양자화하여 표시한다(LOCK-HW-12 EXACT).

---

## §6. 3-5 감정 연동 + 폴백 + Privacy (E5/E6 / cross-domain)

### §6.1 ★ 3-5 Education 감정 연동 (R-09-6 opt-in)

종합계획서 §4 R-09-6 정본:
> R-09-6: #8 Education 감정 연동 시 opt-in 필수 / 기본 비활성

AUTHORITY_CHAIN §6 공유 규약 + emotion_learning_interface.md CONSUMER 계약:
- 본 도메인(#9 Health)은 감정 분류 모델 정본 소유(LOCK-HW-01). 3-5는 **CONSUMER** (학습 적응 입력으로만 활용).
- 공유 범위: **감정 카테고리(7분류) + 강도(1-10) + arousal/valence만** 허용. **원시 텍스트/음성/영상 데이터 공유 절대 금지(R-09-3)**.
- 연동 조건: 사용자 opt-in 필수, 기본 비활성(R-09-6).

```python
class EmotionShareDTO(BaseModel):
    """3-5 Education 공유 DTO (read-only, opt-in) — 원시 데이터 미포함"""
    category: Literal[tuple(EMOTIONS_12)]   # 12감정 카테고리만
    intensity: conint(ge=1, le=10)          # LOCK-HW-12
    arousal: confloat(ge=-1, le=1)
    valence: confloat(ge=-1, le=1)
    # raw_text / raw_audio / raw_video — 필드 자체 부재 (R-09-3 구조적 금지)
```

### §6.2 E5 Graceful Degradation 폴백 (R-05-5)

| 결측 모달리티 | 폴백 | confidence penalty |
|--------------|------|-------------------|
| 영상 결측 (카메라 OFF) | 텍스트+음성 Late fusion | -0.10 |
| 음성 결측 (마이크 OFF) | 텍스트+영상 Late fusion | -0.10 |
| 음성+영상 결측 | 텍스트 단독 | -0.25 |
| 전체 결측 | `FusionError` → 사용자 입력 요청 | N/A |

### §6.3 E6 Privacy/Security + E10 윤리

- **E6 Privacy**: 감정 데이터 PRIVATE 등급(LOCK-HW-02), 로컬 전용, 외부 전송 금지(R-09-3).
- **E10 윤리**: R-09-5 건강/감정 데이터 **AI 학습 파이프라인 제외 필수** + R-09-7 감정 조작 금지(구매/행동 유도 목적 사용 금지).

---

## §7. E1~E10 L3 완전성 + 운영 baseline

### §7.1 E1~E10 9요소 매트릭스

| 요소 | 항목 | 본 문서 충족 |
|------|------|-------------|
| E1 | Input Schema | §3.2 3-모달리티 입력 + 정규화 |
| E2 | Output Schema | §5.1 `FusedEmotion` 12감정+a/v+intensity |
| E3 | Algorithm/Pipeline | §3.3 융합 파이프라인 |
| E4 | Model Comparison | §4.1 Late/Early/Hybrid 비교 + 채택 근거 |
| E5 | Error Handling | §6.2 Graceful Degradation 폴백 4단계 |
| E6 | Privacy/Security | §6.3 LOCK-HW-02 PRIVATE + R-09-3 |
| E7 | Performance SLA | 융합 결과 p95 ≤ 500ms |
| E8 | Integration Test | §7.2 테스트 시나리오 8건 |
| E9 | Dependencies | §2 (text/speech/video base + 3-2 + 3-5) |
| E10 | Ethics/UX | §6.3 R-09-5 AI 학습 제외 + R-09-7 조작 금지 |

### §7.2 E8 Integration Test — Phase 5 테스트 시나리오 (8건)

| # | 시나리오 | 입력/조건 | 기대 결과 |
|---|----------|----------|-----------|
| S-1 | 3-모달리티 정합 | 텍스트+음성+영상 모두 "기쁨" | Late fusion "기쁨", confidence 높음 |
| S-2 | 모달리티 불일치 | 텍스트 "중립" vs 영상 "슬픔" | 신뢰도 가중 융합 + 강도 조정 |
| S-3 | 영상 결측 (E5) | 카메라 OFF | 텍스트+음성 폴백, penalty -0.10 |
| S-4 | 전체 결측 | 모든 입력 없음 | `FusionError` + 입력 요청 |
| S-5 | LOCK-MM-08 정합 | 44.1kHz 음성 입력 | 16kHz mono PCM 정규화 후 처리 |
| S-6 | intensity 양자화 | arousal 0.83 | intensity 1-10 정수 매핑 (LOCK-HW-12) |
| S-7 | ★ 3-5 연동 opt-in OFF | 감정 공유 요청 | 미수신 (기본 비활성, R-09-6) |
| S-8 | 원시 데이터 외부 전송 시도 | raw_audio 전송 요청 | [PRIVACY_BLOCK] R-09-3 거부 (구조적 부재) |

### §7.3 운영 baseline (VBS-17 V3 KPI)

> LOCK (LOCK-HW-10): 감정인식 >= 80%, 웰빙개선 >= 10%

- V3 강화 목표(KPI 표 §10.KPI): **멀티모달 융합 정확도 ≥ 90%** + 융합 p95 ≤ 500ms + arousal/valence MAE ≤ 0.15 (Phase 5 운영 실측).

---

## §8. L3 점수 (88/100)

| 평가 축 | 배점 | 획득 | 근거 |
|---------|-----:|-----:|------|
| E1~E10 9요소 완전성 | 50 | 45 | §7.1 전수 + Late fusion 산식 구체 |
| LOCK verbatim 정합 | 20 | 19 | LOCK-HW-01/02/12 + LOCK-MM-07/08 인용 (재정의 0) |
| cross-domain 계약 | 15 | 13 | 3-2 LOCK-MM + 3-5 R-09-6 opt-in (원시 데이터 구조적 금지) |
| SoT 출처 정합 | 15 | 11 | STEP7-P P-001 L16~L22 |
| **합계** | **100** | **88** | **APPROVED (≥ 80)** |

---

## §9. 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-06-01 | **V3-Phase 4 (genuine write)** | Phase 4 RECOVERY Sub-A P4-1 — multimodal_emotion_fusion.md V3 정본 신규 작성. 텍스트(KoBERT)+음성(SER Wav2Vec2 16kHz)+영상(FER 768d ViT-L/14@336) 3-모달리티 융합 + Late/Early/Hybrid fusion 비교(Late 채택) + LOCK-HW-01 12감정(PRIMARY 7+SECONDARY 5)+arousal/valence + LOCK-HW-12 1-10 강도 + LOCK-HW-02 PRIVATE 로컬 전용 + LOCK-MM-07 768d + LOCK-MM-08 16kHz mono PCM verbatim 인용(재정의 0, DEFINED-HERE 4번째 활성) + ★ 3-5 Education R-09-6 opt-in 감정 연동(category+강도+a/v만, 원시 데이터 구조적 금지 R-09-3) + R-09-5 AI 학습 제외 + R-09-7 조작 금지. E1~E10 9요소 L3 88점. Status DRAFT → APPROVED. |
