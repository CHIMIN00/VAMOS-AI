# text_emotion_analysis.md — KoBERT 기반 텍스트 감정 분석 파이프라인

> **P-ID**: P-001, P-001-a, P-001-b, P-001-c
> **V단계**: V1
> **상태**: P-001 EXTEND / P-001-a EXTEND / P-001-b EXTEND / P-001-c NEW
> **L3 완성**: 2026-04-10
> **정본 소유자**: sot 2/3-6_Health-Wellness-EmotionAI/01_emotion-recognition/

---

## 교차 참조 블록

| 참조 문서 | 위치 | 참조 내용 |
|----------|------|----------|
| 종합계획서 §3.4 | LOCK-HW-01/12 | 감정 분류 모델 7+5+2, 감정 강도 척도 1-10 |
| 종합계획서 §6.1 | 매핑 테이블 10항목 | P-001/P-001-a/P-001-b/P-001-c 배정 |
| 종합계획서 §4 | R-09-1~R-09-7 | 도메인 전용 거버넌스 규칙 |
| 상세명세 §2 | §2.1~§2.5 | 감정 인식 파이프라인 기존 명세 (레거시 참조) |
| STEP7-P | P-001 | 텍스트 감정 분석 원본 체크리스트 |
| AUTHORITY_CHAIN.md | §1~§5 | 정본 계층 및 충돌 해결 |
| 06_ethics-privacy/ethics_framework.md | §3 7원칙 | 비조작/비진단 원칙 적용 |
| 06_ethics-privacy/crisis_protocol.md | §3~§5 | 위기 감지 연동 인터페이스 |
| 02_adaptive-response/ | emotion_adaptive_response.md | 감정 분석 결과 → 적응 응답 인터페이스 |
| 05_emotion-journal/ | emotion_journal_trend.md | 감정 분석 결과 → 일지 기록 인터페이스 |

---

## 1. 개요

본 문서는 VAMOS 텍스트 감정 분석 파이프라인을 L3 구현 즉시 투입 가능 수준으로 정의한다. KoBERT 기반 한국어 텍스트 감정 분류 모델을 사용하여 7+5+2 감정 분류 체계(LOCK-HW-01)에 따라 사용자의 감정을 인식하고, 1-10 정수 강도 척도(LOCK-HW-12)로 감정의 세기를 정량화한다. 감정 상태 전환 추적(P-001-c)을 통해 시간에 따른 감정 변화를 모니터링한다.

**입력**: 사용자 텍스트 (최대 512 토큰)
**출력**: `TextEmotionResult { emotion, intensity, arousal, valence, transition }`

---

## 2. LOCK 인용

> LOCK (LOCK-HW-01, 기존 명세 §2/STEP7-P P-001): 기본7(기쁨,슬픔,분노,불안,놀람,혐오,중립)+세부5(피로,스트레스,좌절,열정,호기심)+차원2(arousal,valence)

> LOCK (LOCK-HW-12, 기존 명세 §2): 1-10 정수 척도

---

## 3. 감정 분류 모델 7+5+2 구조 (P-001-a)

### 3.1 기본 7감정 (Primary Emotions)

> LOCK-HW-01 적용

| # | 감정 | 영문 | arousal 범위 | valence 범위 | 설명 |
|---|------|------|-------------|-------------|------|
| 1 | 기쁨 | Joy | +0.3 ~ +0.8 | +0.5 ~ +1.0 | 긍정적 정서, 만족/행복 |
| 2 | 슬픔 | Sadness | -0.5 ~ +0.1 | -0.8 ~ -0.3 | 상실/실망에 따른 저각성 부정 정서 |
| 3 | 분노 | Anger | +0.5 ~ +1.0 | -0.8 ~ -0.2 | 좌절/불공정에 대한 고각성 부정 정서 |
| 4 | 불안 | Anxiety | +0.3 ~ +0.8 | -0.6 ~ -0.1 | 위협/불확실성에 대한 중~고각성 부정 정서 |
| 5 | 놀람 | Surprise | +0.5 ~ +1.0 | -0.2 ~ +0.5 | 예상치 못한 자극에 대한 고각성 중립 정서 |
| 6 | 혐오 | Disgust | +0.1 ~ +0.5 | -1.0 ~ -0.5 | 거부/회피 반응의 저~중각성 강부정 정서 |
| 7 | 중립 | Neutral | -0.1 ~ +0.1 | -0.1 ~ +0.1 | 뚜렷한 감정 없음 |

### 3.2 세부 5감정 (Secondary Emotions)

> LOCK-HW-01 적용

| # | 감정 | 영문 | arousal 범위 | valence 범위 | 설명 |
|---|------|------|-------------|-------------|------|
| 8 | 피로 | Fatigue | -0.7 ~ -0.2 | -0.5 ~ -0.1 | 에너지 고갈, 저각성 |
| 9 | 스트레스 | Stress | +0.4 ~ +0.9 | -0.7 ~ -0.2 | 과부하/압박에 의한 고각성 부정 |
| 10 | 좌절 | Frustration | +0.3 ~ +0.7 | -0.6 ~ -0.2 | 목표 차단에 의한 중각성 부정 |
| 11 | 열정 | Enthusiasm | +0.6 ~ +1.0 | +0.5 ~ +1.0 | 몰입/동기의 고각성 긍정 |
| 12 | 호기심 | Curiosity | +0.2 ~ +0.6 | +0.1 ~ +0.5 | 탐색 동기의 중각성 약긍정 |

### 3.3 차원 2 (Dimensional)

| 차원 | 범위 | 축 설명 | 산출 방법 |
|------|------|---------|----------|
| arousal | -1.0 ~ +1.0 | 차분(-)↔흥분(+) (Russell's Circumplex Y축) | 감정별 arousal 가중 평균 |
| valence | -1.0 ~ +1.0 | 불쾌(-)↔쾌(+) (Russell's Circumplex X축) | 감정별 valence 가중 평균 |

### 3.4 감정 분류 정합성 규칙

- 기본 7감정과 세부 5감정은 **동시 판정** 가능 (primary + secondary 형태)
- primary_emotion은 반드시 기본 7감정 중 하나
- secondary_emotion은 세부 5감정 중 하나 (없을 수 있음, Optional)
- arousal/valence는 각 감정의 범위 테이블과 일관성 검증 (±0.15 허용 오차)

---

## 4. KoBERT 텍스트 감정 분석 파이프라인 (P-001)

### 4.1 파이프라인 아키텍처

```
[사용자 텍스트 입력]
        │
        ▼
[1. 전처리 (Preprocessing)]
        │  텍스트 정규화 + 길이 제한
        ▼
[2. 토큰화 (KoBERT Tokenizer)]
        │  skt/kobert-base-v1 토크나이저
        ▼
[3. 모델 추론 (KoBERT Inference)]
        │  12-class softmax (7 primary + 5 secondary)
        ▼
[4. 후처리 (Post-processing)]
        │  확률 분포 → 감정 결정 + 차원 산출
        ▼
[5. 강도 산출 (Intensity Calculation)]
        │  LOCK-HW-12: 1-10 정수 척도
        ▼
[6. 전환 추적 (Transition Tracking)]
        │  이전 감정과 비교 + 전환 이벤트 생성
        ▼
[7. 출력: TextEmotionResult]
```

### 4.2 알고리즘 의사코드

```python
# text_emotion_analysis_pipeline.py
# ABC 매핑: P-001(KoBERT 텍스트 분석), P-001-a(7+5+2), P-001-b(강도), P-001-c(전환)

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import torch


# ── 공통 자료 구조 (Pydantic/dataclass 형태 선정의) ──

class PrimaryEmotion(str, Enum):
    """LOCK-HW-01 기본 7감정"""
    JOY = "기쁨"
    SADNESS = "슬픔"
    ANGER = "분노"
    ANXIETY = "불안"
    SURPRISE = "놀람"
    DISGUST = "혐오"
    NEUTRAL = "중립"


class SecondaryEmotion(str, Enum):
    """LOCK-HW-01 세부 5감정"""
    FATIGUE = "피로"
    STRESS = "스트레스"
    FRUSTRATION = "좌절"
    ENTHUSIASM = "열정"
    CURIOSITY = "호기심"


@dataclass
class EmotionScore:
    """개별 감정 확률 점수"""
    emotion: str
    probability: float  # 0.0 ~ 1.0


@dataclass
class TextEmotionResult:
    """
    텍스트 감정 분석 최종 출력.
    세션 간 인터페이스: 02_adaptive-response, 05_emotion-journal에서 참조.
    """
    primary_emotion: PrimaryEmotion
    primary_confidence: float            # 0.0 ~ 1.0
    secondary_emotion: Optional[SecondaryEmotion]  # None 가능
    secondary_confidence: float          # 0.0 ~ 1.0 (secondary 없으면 0.0)
    intensity: int                       # LOCK-HW-12: 1-10 정수
    arousal: float                       # -1.0 ~ +1.0
    valence: float                       # -1.0 ~ +1.0
    all_scores: list[EmotionScore] = field(default_factory=list)  # 12감정 전체 확률
    transition: Optional['EmotionTransition'] = None  # P-001-c


@dataclass
class EmotionTransition:
    """P-001-c: 감정 상태 전환 이벤트"""
    previous_emotion: PrimaryEmotion
    current_emotion: PrimaryEmotion
    previous_intensity: int
    current_intensity: int
    delta_arousal: float
    delta_valence: float
    transition_type: str  # "stable" | "shift" | "spike" | "drop"
    timestamp_ms: int


# ── 감정 분류 기준 상수 (LOCK-HW-01) ──

# arousal/valence 매핑 테이블 (§3.1, §3.2)
AROUSAL_VALENCE_MAP: dict[str, tuple[float, float]] = {
    # emotion: (arousal_center, valence_center)
    "기쁨":    (+0.55, +0.75),
    "슬픔":    (-0.20, -0.55),
    "분노":    (+0.75, -0.50),
    "불안":    (+0.55, -0.35),
    "놀람":    (+0.75, +0.15),
    "혐오":    (+0.30, -0.75),
    "중립":    ( 0.00,  0.00),
    "피로":    (-0.45, -0.30),
    "스트레스": (+0.65, -0.45),
    "좌절":    (+0.50, -0.40),
    "열정":    (+0.80, +0.75),
    "호기심":  (+0.40, +0.30),
}


class KoBERTEmotionPipeline:
    """
    KoBERT 기반 텍스트 감정 분석 파이프라인.

    시간복잡도:
        - 전처리: O(n) — n = 입력 텍스트 길이 (최대 512 토큰)
        - 토큰화: O(n)
        - 모델 추론: O(1) — 고정 크기 트랜스포머 forward pass
        - 후처리: O(k) — k = 감정 클래스 수 (12, 고정)
        - 강도 산출: O(1)
        - 전환 추적: O(1)
        총: O(n) (모델 추론은 n에 대해 상수)

    공간복잡도: O(n) — 토큰 텐서 + 12-class logits

    LOCK 참조:
        - LOCK-HW-01: 기본7 + 세부5 + 차원2
        - LOCK-HW-12: 1-10 정수 척도

    ABC 매핑:
        - P-001: analyze() 메서드 (KoBERT 추론)
        - P-001-a: _classify_emotion() (7+5+2 분류)
        - P-001-b: _calculate_intensity() (강도 산출)
        - P-001-c: _track_transition() (전환 추적)
    """

    MODEL_ID = "skt/kobert-base-v1"
    MAX_LENGTH = 512
    NUM_PRIMARY = 7
    NUM_SECONDARY = 5
    NUM_CLASSES = NUM_PRIMARY + NUM_SECONDARY  # 12

    # 강도 산출은 _calculate_intensity() 공식(raw=confidence*0.7+|arousal|*0.3, ceil(raw*10), clamp 1-10)을 정본으로 한다 (LOCK-HW-12).
    # (이전 INTENSITY_BOUNDARIES 상수는 미사용 dead code 로 제거 — 실제 알고리즘과 모순)

    # secondary 감정 판정 임계값
    SECONDARY_THRESHOLD = 0.15

    # 전환 판정 임계값
    TRANSITION_SPIKE_THRESHOLD = 3   # intensity 차이 >= 3이면 spike/drop
    TRANSITION_SHIFT_THRESHOLD = 1   # 감정 종류 변경이면 shift

    def __init__(self):
        self._model = None
        self._tokenizer = None
        self._previous_result: Optional[TextEmotionResult] = None

    async def initialize(self) -> None:
        """모델 및 토크나이저 로드. 앱 시작 시 1회 호출."""
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        self._tokenizer = AutoTokenizer.from_pretrained(self.MODEL_ID)
        self._model = AutoModelForSequenceClassification.from_pretrained(
            self.MODEL_ID, num_labels=self.NUM_CLASSES
        )
        self._model.eval()

    async def analyze(self, text: str) -> TextEmotionResult:
        """
        메인 분석 메서드.
        입력 텍스트 → TextEmotionResult 반환.

        P-001 ABC 매핑: KoBERT 텍스트 감정 분석 전체 파이프라인.

        Args:
            text: 사용자 입력 텍스트 (최대 512 토큰, 초과 시 truncation)

        Returns:
            TextEmotionResult: 감정 분류 + 강도 + 차원 + 전환 정보
        """
        # Step 1: 전처리
        cleaned = self._preprocess(text)

        # Step 2: 토큰화
        tokens = self._tokenizer(
            cleaned,
            return_tensors="pt",
            truncation=True,
            max_length=self.MAX_LENGTH,
            padding=True
        )

        # Step 3: 모델 추론
        with torch.no_grad():
            logits = self._model(**tokens).logits  # shape: (1, 12)

        # Step 4: 후처리 — 확률 분포 산출
        probs = torch.softmax(logits, dim=-1)[0]  # shape: (12,)

        # Step 5: 감정 분류 (P-001-a)
        primary, primary_conf, secondary, secondary_conf, all_scores = (
            self._classify_emotion(probs)
        )

        # Step 6: 차원 산출
        arousal, valence = self._calculate_dimensions(all_scores)

        # Step 7: 강도 산출 (P-001-b)
        intensity = self._calculate_intensity(primary_conf, arousal)

        # Step 8: 전환 추적 (P-001-c)
        transition = self._track_transition(primary, intensity, arousal, valence)

        result = TextEmotionResult(
            primary_emotion=primary,
            primary_confidence=primary_conf,
            secondary_emotion=secondary,
            secondary_confidence=secondary_conf,
            intensity=intensity,
            arousal=arousal,
            valence=valence,
            all_scores=all_scores,
            transition=transition,
        )

        self._previous_result = result
        return result

    # ── Step 1: 전처리 ──

    def _preprocess(self, text: str) -> str:
        """
        텍스트 정규화.
        - 연속 공백/개행 정리
        - 이모지 보존 (감정 신호)
        - HTML 태그 제거
        - 길이 제한 (MAX_LENGTH 토큰 이내)

        시간복잡도: O(n)
        """
        import re
        text = re.sub(r'<[^>]+>', '', text)       # HTML 태그 제거
        text = re.sub(r'\s+', ' ', text).strip()   # 연속 공백 정리
        return text

    # ── Step 5: 감정 분류 (P-001-a) ──

    def _classify_emotion(
        self, probs: torch.Tensor
    ) -> tuple[PrimaryEmotion, float, Optional[SecondaryEmotion], float, list[EmotionScore]]:
        """
        softmax 확률 분포로부터 primary/secondary 감정을 결정한다.

        LOCK-HW-01: 기본7(기쁨,슬픔,분노,불안,놀람,혐오,중립)
                    + 세부5(피로,스트레스,좌절,열정,호기심)

        알고리즘:
        1. 기본 7감정 중 최대 확률 → primary_emotion
        2. 세부 5감정 중 최대 확률이 SECONDARY_THRESHOLD 이상 → secondary_emotion
        3. 전체 12감정 확률 리스트 반환

        시간복잡도: O(k) — k=12 (고정)

        Args:
            probs: shape (12,) softmax 확률 텐서

        Returns:
            (primary, primary_conf, secondary, secondary_conf, all_scores)
        """
        PRIMARY_LABELS = list(PrimaryEmotion)
        SECONDARY_LABELS = list(SecondaryEmotion)

        all_scores = []
        for i, label in enumerate(PRIMARY_LABELS + SECONDARY_LABELS):
            all_scores.append(EmotionScore(emotion=label.value, probability=float(probs[i])))

        # Primary: 기본 7감정 중 최대
        primary_probs = probs[:self.NUM_PRIMARY]
        primary_idx = torch.argmax(primary_probs).item()
        primary = PRIMARY_LABELS[primary_idx]
        primary_conf = float(primary_probs[primary_idx])

        # Secondary: 세부 5감정 중 최대 (임계값 이상일 때만)
        secondary_probs = probs[self.NUM_PRIMARY:]
        secondary_idx = torch.argmax(secondary_probs).item()
        secondary_conf = float(secondary_probs[secondary_idx])

        if secondary_conf >= self.SECONDARY_THRESHOLD:
            secondary = SECONDARY_LABELS[secondary_idx]
        else:
            secondary = None
            secondary_conf = 0.0

        return primary, primary_conf, secondary, secondary_conf, all_scores

    # ── Step 6: 차원 산출 ──

    def _calculate_dimensions(
        self, all_scores: list[EmotionScore]
    ) -> tuple[float, float]:
        """
        확률 가중 평균으로 arousal/valence 산출.

        Russell's Circumplex Model 기반.
        arousal = Σ(p_i * arousal_center_i) / Σ(p_i)
        valence = Σ(p_i * valence_center_i) / Σ(p_i)

        시간복잡도: O(k) — k=12 (고정)

        Returns:
            (arousal, valence) 각각 -1.0 ~ +1.0
        """
        total_weight = 0.0
        arousal_sum = 0.0
        valence_sum = 0.0

        for score in all_scores:
            if score.emotion in AROUSAL_VALENCE_MAP:
                a_center, v_center = AROUSAL_VALENCE_MAP[score.emotion]
                arousal_sum += score.probability * a_center
                valence_sum += score.probability * v_center
                total_weight += score.probability

        if total_weight > 0:
            arousal = max(-1.0, min(1.0, arousal_sum / total_weight))
            valence = max(-1.0, min(1.0, valence_sum / total_weight))
        else:
            arousal = 0.0
            valence = 0.0

        return arousal, valence

    # ── Step 7: 강도 산출 (P-001-b) ──

    def _calculate_intensity(self, confidence: float, arousal: float) -> int:
        """
        감정 강도 산출. LOCK-HW-12: 1-10 정수 척도.

        공식:
            raw_intensity = confidence * 0.7 + abs(arousal) * 0.3
            intensity = clamp(ceil(raw_intensity * 10), 1, 10)

        근거:
        - confidence 70% 가중: 모델의 확신도가 주된 강도 지표
        - |arousal| 30% 가중: 각성 수준이 감정 체감 강도에 기여
        - 1-10 정수 변환: raw 0.0~1.0 → 1~10 (ceil로 올림, 최소 1)

        시간복잡도: O(1)

        Args:
            confidence: primary 감정 확률 (0.0~1.0)
            arousal: arousal 값 (-1.0~+1.0)

        Returns:
            int: 1~10 정수 강도
        """
        import math
        raw = confidence * 0.7 + abs(arousal) * 0.3
        intensity = max(1, min(10, math.ceil(raw * 10)))
        return intensity

    # ── Step 8: 전환 추적 (P-001-c) ──

    def _track_transition(
        self,
        current_emotion: PrimaryEmotion,
        current_intensity: int,
        current_arousal: float,
        current_valence: float,
    ) -> Optional[EmotionTransition]:
        """
        감정 상태 전환을 추적한다 (P-001-c).

        전환 유형 판정 규칙:
        - stable: 동일 감정 + intensity 차이 < TRANSITION_SHIFT_THRESHOLD
        - shift: 감정 종류 변경 (intensity 차이 < SPIKE_THRESHOLD)
        - spike: intensity 차이 >= SPIKE_THRESHOLD (상승 방향)
        - drop: intensity 차이 >= SPIKE_THRESHOLD (하강 방향)

        시간복잡도: O(1)

        Returns:
            EmotionTransition 또는 None (이전 결과 없을 때)
        """
        import time

        if self._previous_result is None:
            return None

        prev = self._previous_result
        delta_intensity = current_intensity - prev.intensity
        delta_arousal = current_arousal - prev.arousal
        delta_valence = current_valence - prev.valence

        # 전환 유형 결정
        if abs(delta_intensity) >= self.TRANSITION_SPIKE_THRESHOLD:
            transition_type = "spike" if delta_intensity > 0 else "drop"
        elif current_emotion != prev.primary_emotion:
            transition_type = "shift"
        else:
            transition_type = "stable"

        return EmotionTransition(
            previous_emotion=prev.primary_emotion,
            current_emotion=current_emotion,
            previous_intensity=prev.intensity,
            current_intensity=current_intensity,
            delta_arousal=round(delta_arousal, 4),
            delta_valence=round(delta_valence, 4),
            transition_type=transition_type,
            timestamp_ms=int(time.time() * 1000),
        )
```

---

## 5. 감정 강도 척도 상세 (P-001-b)

> LOCK (LOCK-HW-12, 기존 명세 §2): 1-10 정수 척도

### 5.1 강도 등급 정의

| 강도 | 등급 | 설명 | 대표 시나리오 |
|------|------|------|-------------|
| 1 | 미미 | 거의 감지되지 않는 미세 감정 | 무표정 중 약간의 관심 |
| 2 | 약함 | 본인도 인지하기 어려운 수준 | 가벼운 심심함 |
| 3 | 경미 | 인지 가능하나 행동에 영향 없음 | 약간 기분 좋음 |
| 4 | 보통-하 | 의식적으로 느끼는 수준 | 소소한 짜증 |
| 5 | 보통 | 행동에 약간 영향을 주는 수준 | 일상적 스트레스 |
| 6 | 보통-상 | 행동 변화가 나타나기 시작 | 업무 마감 압박 |
| 7 | 강함 | 명확한 행동 변화 동반 | 큰 기쁨/분노 |
| 8 | 매우 강함 | 정상적 판단에 영향을 줄 수 있음 | 강한 좌절/열정 |
| 9 | 극심 | 즉각적 개입이 도움이 되는 수준 | 극심한 불안/스트레스 |
| 10 | 위기 | 위기 감지 프로토콜 연동 대상 | 자해/극단적 감정 → crisis_protocol.md |

### 5.2 강도-행동 연결 매트릭스

| 강도 범위 | 시스템 반응 | 연동 모듈 |
|----------|-----------|----------|
| 1-3 | 일반 모니터링, 일지 기록만 | 05_emotion-journal |
| 4-6 | 적응 응답 톤 조정 활성화 | 02_adaptive-response |
| 7-8 | 스트레스 관리 도구 제안 | 04_stress-management |
| 9-10 | 위기 프로토콜 트리거 | 06_ethics-privacy/crisis_protocol |

---

## 6. 감정 상태 전환 추적 (P-001-c)

### 6.1 전환 유형

| 유형 | 조건 | 의미 | 후속 처리 |
|------|------|------|----------|
| stable | 동일 감정 + \|Δintensity\| < 1 | 감정 안정 | 일반 모니터링 |
| shift | 감정 종류 변경 + \|Δintensity\| < 3 | 자연스러운 감정 전환 | 전환 이력 일지 기록 |
| spike | \|Δintensity\| >= 3 (상승) | 급격한 감정 고조 | 적응 응답 즉시 조정 + 알림 |
| drop | \|Δintensity\| >= 3 (하강) | 급격한 감정 하강 | 원인 분석 트리거 + 일지 기록 |

### 6.2 전환 추적 윈도우

```
전환 추적 버퍼: 최근 N개 TextEmotionResult 유지 (기본 N=20)

[t-19] → [t-18] → ... → [t-1] → [t-0 (현재)]
                                    ↓
                          전환 이벤트 생성
                                    ↓
                     ┌──────────────┼──────────────┐
                     ↓              ↓              ↓
              stable → skip   shift → journal   spike/drop → alert
```

### 6.3 전환 통계 집계

```python
@dataclass
class EmotionTransitionStats:
    """세션 내 감정 전환 통계. 일지/트렌드 모듈에 전달."""
    total_transitions: int
    shift_count: int
    spike_count: int
    drop_count: int
    dominant_emotion: PrimaryEmotion      # 세션 내 최빈 감정
    average_intensity: float              # 세션 평균 강도
    arousal_trend: str                    # "increasing" | "stable" | "decreasing"
    valence_trend: str                    # "increasing" | "stable" | "decreasing"
    session_duration_ms: int
```

---

## 7. 세션 간 인터페이스

### 7.1 출력 인터페이스 (다른 모듈이 소비)

| 소비자 모듈 | 사용 데이터 | 인터페이스 |
|------------|-----------|-----------|
| 02_adaptive-response | primary_emotion, intensity, arousal, valence | `TextEmotionResult` 직접 참조 |
| 04_stress-management | primary_emotion == "스트레스" 또는 intensity >= 7 | 이벤트 기반 트리거 |
| 05_emotion-journal | TextEmotionResult 전체 + EmotionTransition | 일지 기록 API 호출 |
| 06_ethics-privacy/crisis_protocol | intensity >= 9 또는 위기 키워드 감지 | 위기 프로토콜 트리거 (우선순위 최고) |

### 7.2 입력 의존성

| 제공자 | 데이터 | 용도 |
|--------|--------|------|
| 사용자 입력 (텍스트) | str | analyze() 입력 |
| 06_ethics-privacy/ethics_framework | NonDiagnosticFilter | 출력 텍스트 필터링 |

---

## 8. 로깅 포맷 (R-01-7)

```json
{
  "log_type": "EMOTION_ANALYSIS",
  "timestamp": "2026-04-10T12:00:00.000Z",
  "session_id": "sess_abc123",
  "module": "01_emotion-recognition/text_emotion_analysis",
  "level": "INFO",
  "payload": {
    "input": {
      "text_length": 128,
      "text_hash": "sha256:abcd1234..."
    },
    "result": {
      "primary_emotion": "불안",
      "primary_confidence": 0.72,
      "secondary_emotion": "스트레스",
      "secondary_confidence": 0.18,
      "intensity": 6,
      "arousal": 0.55,
      "valence": -0.35,
      "transition": {
        "previous_emotion": "중립",
        "current_emotion": "불안",
        "transition_type": "shift",
        "delta_arousal": 0.55,
        "delta_valence": -0.35
      }
    },
    "performance": {
      "preprocessing_ms": 2,
      "tokenization_ms": 5,
      "inference_ms": 45,
      "postprocessing_ms": 1,
      "total_ms": 53
    }
  },
  "privacy": {
    "data_grade": "PRIVATE",
    "raw_text_logged": false,
    "retention_days": 180
  }
}
```

> **프라이버시 규칙**: 원시 텍스트는 로그에 기록하지 않는다 (R-09-3). text_hash만 기록하여 중복 분석 방지용으로 사용한다. 감정 데이터는 PRIVATE 등급(LOCK-HW-02)으로 로컬 전용 저장한다.

---

## 9. 예외 처리 정책 표

| 예외 상황 | 처리 방식 | 폴백 값 | 에스컬레이션 |
|----------|----------|---------|------------|
| 빈 텍스트 입력 | 즉시 반환 (분석 스킵) | primary=중립, intensity=1 | 없음 |
| 텍스트 512 토큰 초과 | truncation 적용 | 잘린 텍스트로 분석 | 경고 로그 |
| 모델 로드 실패 | 재시도 3회 (지수 백오프 1s/2s/4s) | 분석 불가 상태 반환 | [ESCALATION] 앱 시작 차단 |
| 추론 타임아웃 (>200ms) | 타임아웃 반환 | 이전 결과 유지 | 성능 경고 로그 |
| softmax 결과 전체 <0.1 | 저신뢰 플래그 | primary=중립, intensity=1, low_confidence=true | 없음 |
| 위기 강도 감지 (>=9) | crisis_protocol 즉시 호출 | N/A (분석은 정상 완료) | 위기 프로토콜 트리거 (R-09-2) |
| 토크나이저 인코딩 오류 | 유니코드 정규화 후 재시도 | 재시도 실패 시 중립 반환 | 경고 로그 |

---

## 10. Phase 2 테스트 시나리오

> 10건 이상 필수. 각 시나리오는 입력/기대 출력/검증 포인트를 포함한다.

| # | 시나리오 | 입력 (요약) | 기대 primary | 기대 intensity 범위 | 검증 포인트 |
|---|---------|-----------|-------------|-------------------|-----------|
| T1 | 기쁨 표현 | "오늘 승진했어! 너무 기뻐!" | 기쁨 | 7-9 | arousal > 0.3, valence > 0.5 |
| T2 | 슬픔 표현 | "친구가 이사가서 너무 슬퍼" | 슬픔 | 5-7 | valence < -0.3 |
| T3 | 분노 표현 | "또 약속 어겼어? 정말 화난다" | 분노 | 6-8 | arousal > 0.5 |
| T4 | 불안 표현 | "내일 면접인데 떨리고 걱정돼" | 불안 | 5-7 | arousal > 0.3, valence < -0.1 |
| T5 | 중립 표현 | "오늘 날씨가 흐리네요" | 중립 | 1-3 | \|arousal\| < 0.2, \|valence\| < 0.2 |
| T6 | 스트레스 (secondary) | "일이 너무 많아서 머리가 터질 것 같아" | 분노 또는 불안 | 7-9 | secondary=스트레스, conf >= 0.15 |
| T7 | 피로 (secondary) | "요즘 계속 피곤해서 아무것도 하기 싫어" | 슬픔 | 4-6 | secondary=피로, arousal < 0 |
| T8 | 위기 강도 | "모든 게 끝났어. 사라지고 싶어" | 슬픔 또는 불안 | 9-10 | crisis_protocol 트리거 확인 |
| T9 | 전환: shift | 기쁨→슬픔 연속 입력 | 슬픔 (2차) | - | transition_type="shift" |
| T10 | 전환: spike | 중립→분노(강) 연속 입력 | 분노 (2차) | 8-10 | transition_type="spike" |
| T11 | 빈 텍스트 | "" | 중립 | 1 | 폴백 동작 확인 |
| T12 | 장문 텍스트 | 512토큰 초과 텍스트 | 임의 | 임의 | truncation 정상 동작, 경고 로그 |
| T13 | 이모지 보존 | "😭😭😭 너무 슬퍼" | 슬픔 | 6-8 | 이모지가 감정 신호로 활용됨 |
| T14 | 혼합 감정 | "기쁘면서도 아쉬운 졸업식" | 기쁨 또는 슬픔 | 4-6 | secondary 존재, 두 감정 모두 >0.1 |
| T15 | 열정 (secondary) | "이 프로젝트 진짜 재밌어! 밤새 하고 싶다" | 기쁨 | 7-9 | secondary=열정, arousal > 0.6 |

---

## 11. 비의료 면책

> LOCK (LOCK-HW-04, STEP7-P 윤리원칙): "VAMOS는 의료 서비스가 아닙니다" 모든 건강 관련 응답에 포함

본 문서에서 정의하는 감정 분석은 심리 진단 도구가 아니며, 의학적/심리학적 판단을 대체하지 않는다. 모든 감정 분석 결과에는 비의료 면책 문구가 포함되어야 한다 (R-09-1). 진단 관련 용어 사용은 06_ethics-privacy/ethics_framework.md의 NonDiagnosticFilter에 의해 차단된다 (R-09-4).
