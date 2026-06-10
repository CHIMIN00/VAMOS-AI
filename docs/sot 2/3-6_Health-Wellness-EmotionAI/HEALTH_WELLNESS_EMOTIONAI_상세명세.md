# HEALTH_WELLNESS_EMOTIONAI 상세명세

> **Tier**: 3 (Feature Domains) | **Part2 Status**: SHELL (CAT-F + UI 컴포넌트 일부) | **SOT**: STEP7-P (62 items)
> **Version**: 1.0.0 | **최종수정**: 2026-03-22
> **교차참조**: T2-CORE_AI → LLM 공감응답, T3-Multimodal → 음성감정인식, T3-Education → 학습스트레스

---

## 1. 개요

VAMOS Health/Wellness/EmotionAI 모듈은 사용자의 감정 상태를 인식하고,
적응적으로 응답하며, 건강 데이터 통합 및 스트레스 관리 도구를 제공한다.
프라이버시를 최우선으로 하며 전문 의료 조언을 대체하지 않는다.

### 1.1 모듈 구성

```
[감정 인식 파이프라인] ──→ [감정 적응 응답 시스템]
       ↕                          ↕
[건강 데이터 통합] ←──→ [스트레스 관리 백엔드]
       ↕                          ↕
       └──────→ [감정 일지/트렌드] ←──────┘
```

### 1.2 프라이버시 및 윤리 원칙

| 원칙 | 구현 |
|------|------|
| 데이터 최소 수집 | 필요한 데이터만 수집, 원시 데이터 즉시 삭제 |
| 로컬 우선 처리 | 감정 인식은 가능한 한 로컬(KoBERT)에서 처리 |
| 명시적 동의 | 건강 데이터 연동 전 명시적 동의 필요 |
| 암호화 저장 | 감정/건강 데이터는 AES-256 암호화 |
| 비의료 면책 | 모든 건강 관련 응답에 면책 조항 포함 |
| 위기 감지 | 자해/자살 관련 표현 감지 시 전문기관 안내 |

---

## 2. 감정 인식 파이프라인

### 2.1 멀티모달 감정 분석 아키텍처

```
[텍스트 입력] ──→ [KoBERT 감정 분류] ─────────────────────┐
[음성 입력] ───→ [음성 감정 인식 (SER)] ──────────────────┤
[얼굴/비디오] ─→ [표정 인식 (선택)] ──────────────────────┤
                                                           ↓
                                                  [멀티모달 감정 융합]
                                                           ↓
                                                  [감정 상태 결정]
                                                           ↓
                                          ┌────────────────┼───────────────┐
                                          ↓                ↓               ↓
                                  [감정 적응 응답]  [감정 일지 기록]  [위기 감지]
```

### 2.2 텍스트 감정 분석 (KoBERT)

```python
# text_emotion_analyzer.py
class KoBERTEmotionAnalyzer:
    """KoBERT 기반 한국어 텍스트 감정 분류"""

    MODEL_ID = "skt/kobert-base-v1"  # KoBERT 기반 감정 분류 fine-tuned 모델
    # LOCK-HW-01: 기본7 + 세부5 + 차원2(arousal, valence)
    PRIMARY_EMOTIONS = [
        "기쁨", "슬픔", "분노", "불안", "놀람", "혐오", "중립"
    ]
    SECONDARY_EMOTIONS = [
        "피로", "스트레스", "좌절", "열정", "호기심"
    ]
    EMOTION_LABELS = PRIMARY_EMOTIONS + SECONDARY_EMOTIONS

    SENTIMENT_MAP = {
        "positive": ["기쁨", "놀람", "열정", "호기심"],
        "negative": ["슬픔", "분노", "불안", "혐오", "피로", "스트레스", "좌절"],
        "neutral":  ["중립"],
    }

    async def analyze(self, text: str) -> TextEmotionResult:
        """
        1. 토큰화 (KoBERT tokenizer)
        2. 모델 추론
        3. softmax → 감정별 확률 분포
        4. 상위 감정 + 감성(sentiment) 반환
        """
        tokens = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        logits = self.model(**tokens).logits
        probs = torch.softmax(logits, dim=-1)[0]

        emotion_scores = {
            label: float(probs[i])
            for i, label in enumerate(self.EMOTION_LABELS)
        }

        # primary 는 기본 7감정으로 제한 (LOCK-HW-01 / §2.5 PrimaryEmotion). 세부 5감정이 최고여도 primary 승격 금지.
        primary = max(self.PRIMARY_EMOTIONS, key=lambda e: emotion_scores[e])
        sentiment = self._get_sentiment(primary)

        return TextEmotionResult(
            primary_emotion=primary,
            confidence=emotion_scores[primary],
            all_emotions=emotion_scores,
            sentiment=sentiment,
            arousal=self._estimate_arousal(emotion_scores),
            valence=self._estimate_valence(emotion_scores),
        )
```

### 2.3 음성 감정 인식 (SER)

```python
# speech_emotion_recognition.py
class SpeechEmotionRecognizer:
    """음성 신호에서 감정 추출"""

    FEATURES = [
        "mfcc",              # Mel-frequency cepstral coefficients (13차)
        "pitch",             # 기본 주파수 (F0)
        "energy",            # 에너지/볼륨
        "speech_rate",       # 발화 속도
        "pause_pattern",     # 침묵 패턴
        "jitter_shimmer",    # 음성 떨림
    ]

    MODELS = {
        "local": {
            "model": "wav2vec2-emotion-korean",
            "latency_ms": 200,
            "accuracy": 0.72,
            "cost": "GPU only",
        },
        "hume_ai": {
            "api": "https://api.hume.ai/v0/batch/jobs",
            "latency_ms": 1500,
            "accuracy": 0.85,
            "cost": "$0.01/request",
        },
    }

    async def recognize(self, audio: bytes, provider: str = "local") -> SpeechEmotionResult:
        if provider == "hume_ai":
            return await self._hume_ai_analyze(audio)
        else:
            features = self._extract_features(audio)
            return await self._local_model_predict(features)
```

### 2.4 Hume AI 통합

```python
# hume_ai_integration.py
class HumeAIClient:
    """Hume AI Expression Measurement API 통합"""

    BASE_URL = "https://api.hume.ai/v0"
    SUPPORTED_MODALITIES = ["face", "prosody", "language"]

    CONFIG = {
        "prosody": {
            "granularity": "utterance",     # "word" | "utterance" | "sentence"
            "identify_speakers": True,
        },
        "language": {
            "granularity": "sentence",
            "identify_speakers": False,
        },
    }

    # Hume AI 감정 분류 → VAMOS 감정 분류 매핑
    EMOTION_MAPPING = {
        "Joy": "기쁨",
        "Sadness": "슬픔",
        "Anger": "분노",
        "Fear": "불안",
        "Surprise (positive)": "놀람",
        "Disgust": "혐오",
        "Anxiety": "불안",
        "Boredom": "피로",
        "Contemplation": "중립",
        "Gratitude": "기쁨",
        "Guilt": "슬픔",
        "Loneliness": "슬픔",
    }

    async def analyze(self, data: bytes, modality: str) -> HumeEmotionResult:
        """Hume AI API 호출 + 결과 매핑"""
        response = await self._api_call(f"/batch/jobs", data, modality)
        return self._map_to_vamos_emotions(response)
```

### 2.5 감정 분류 체계

```typescript
// emotion_taxonomy.ts
interface EmotionState {
  // 기본 감정 (Ekman + 확장)
  primary_emotion: PrimaryEmotion;
  confidence: number;                 // 0.0 ~ 1.0

  // 차원 모델 (Russell's Circumplex)
  arousal: number;                    // -1.0 (차분) ~ 1.0 (흥분)
  valence: number;                    // -1.0 (불쾌) ~ 1.0 (쾌)

  // 강도
  intensity: number;                  // LOCK-HW-12: 1-10 정수 척도 (정수, 1<=intensity<=10)

  // 시간적 맥락
  duration: "momentary" | "persistent" | "chronic";
  trend: "improving" | "stable" | "declining";

  // 소스별 신뢰도
  sources: {
    text?: { emotion: string; confidence: number };
    speech?: { emotion: string; confidence: number };
    facial?: { emotion: string; confidence: number };
  };

  // 융합 방법
  fusion_method: "weighted_average" | "attention" | "majority_vote";
}

// LOCK-HW-01: 기본 7감정
type PrimaryEmotion =
  | "기쁨" | "슬픔" | "분노" | "불안" | "놀람" | "혐오" | "중립";

// LOCK-HW-01: 세부 5감정
type SecondaryEmotion =
  | "피로" | "스트레스" | "좌절" | "열정" | "호기심";

type AllEmotion = PrimaryEmotion | SecondaryEmotion;
```

---

## 3. 감정 적응 응답 시스템

### 3.1 감정 기반 응답 조절

```python
# emotion_adaptive_responder.py
class EmotionAdaptiveResponder:
    """감정 상태에 따른 응답 톤/스타일 자동 조절"""

    # LOCK-HW-01 기본 7감정 기반 프로파일 + 세부 5감정 추가
    RESPONSE_PROFILES = {
        # --- 기본 7감정 (LOCK-HW-01) ---
        "기쁨": {
            "tone": "밝고 에너지 넘치는",
            "style": "축하/격려, 긍정 에너지 증폭",
            "emoji_level": "moderate",
            "verbosity": "normal",
        },
        "슬픔": {
            "tone": "따뜻하고 공감적인",
            "style": "감정 인정, 경청, 위로",
            "emoji_level": "minimal",
            "verbosity": "concise",
            "avoid": ["긍정 강요", "비교", "조언 즉시 제공"],
        },
        "분노": {
            "tone": "차분하고 이해하는",
            "style": "감정 인정, 상황 정리 도움",
            "emoji_level": "none",
            "verbosity": "concise",
            "avoid": ["반박", "축소", "훈계"],
        },
        "불안": {
            "tone": "안정적이고 구조화된",
            "style": "사실 기반 정보, 단계별 안내, 안전감 제공",
            "emoji_level": "minimal",
            "verbosity": "structured",
        },
        "놀람": {
            "tone": "호기심을 존중하는",
            "style": "상황 파악 도움, 정보 제공",
            "emoji_level": "minimal",
            "verbosity": "normal",
        },
        "혐오": {
            "tone": "중립적이고 이해하는",
            "style": "감정 인정, 거리두기 도움",
            "emoji_level": "none",
            "verbosity": "concise",
            "avoid": ["판단", "축소"],
        },
        "중립": {
            "tone": "자연스럽고 전문적인",
            "style": "기본 대화 스타일",
            "emoji_level": "minimal",
            "verbosity": "normal",
        },
        # --- 세부 5감정 (LOCK-HW-01) ---
        "피로": {
            "tone": "부드럽고 배려하는",
            "style": "휴식 제안, 부담 줄이기, 간결한 응답",
            "emoji_level": "none",
            "verbosity": "concise",
        },
        "스트레스": {
            "tone": "차분하고 체계적인",
            "style": "우선순위 정리, 스트레스 관리 도구 제안",
            "emoji_level": "none",
            "verbosity": "structured",
        },
        "좌절": {
            "tone": "격려하고 공감하는",
            "style": "작은 성취 인정, 단계별 접근 제안",
            "emoji_level": "minimal",
            "verbosity": "concise",
            "avoid": ["긍정 강요", "비교"],
        },
        "열정": {
            "tone": "에너지 넘치고 지지하는",
            "style": "동기 부여, 실행 계획 도움, 목표 구체화",
            "emoji_level": "moderate",
            "verbosity": "normal",
        },
        "호기심": {
            "tone": "탐구적이고 정보 풍부한",
            "style": "상세 설명, 추가 자료 제공, 질문 유도",
            "emoji_level": "minimal",
            "verbosity": "detailed",
        },
    }

    async def adapt_response(
        self, base_response: str, emotion_state: EmotionState
    ) -> AdaptedResponse:
        profile = self.RESPONSE_PROFILES[emotion_state.primary_emotion]

        # 프롬프트에 감정 컨텍스트 주입
        system_prompt = f"""
        사용자의 현재 감정: {emotion_state.primary_emotion} (강도: {emotion_state.intensity})
        응답 톤: {profile['tone']}
        스타일: {profile['style']}
        {"피해야 할 것: " + ", ".join(profile.get('avoid', [])) if profile.get('avoid') else ""}

        위 감정 맥락에 맞게 응답을 조절하되, 자연스럽게.
        감정을 명시적으로 언급하지 말 것 (사용자가 감시당한다고 느끼지 않도록).
        """

        adapted = await self.llm.generate(
            system=system_prompt,
            user=f"원본 응답을 감정에 맞게 조절:\n{base_response}",
        )

        return AdaptedResponse(
            text=adapted,
            emotion_acknowledged=emotion_state.primary_emotion,
            tone_applied=profile["tone"],
        )
```

### 3.2 공감 프롬프트 라이브러리

```python
# empathy_prompts.py
EMPATHY_TEMPLATES = {
    "acknowledge": [
        "그런 마음이 드는 게 당연해요.",
        "그런 상황이라면 누구라도 그렇게 느낄 수 있어요.",
        "그 감정을 느끼고 계시는 것 자체가 의미 있는 거예요.",
    ],
    "validate": [
        "당신의 감정은 충분히 타당해요.",
        "그런 반응은 자연스러운 거예요.",
    ],
    "reflect": [
        "~라고 느끼고 계시는 것 같네요.",
        "지금 ~한 상황이 힘드시죠.",
    ],
    "support": [
        "제가 여기 있을게요.",
        "천천히 이야기해 주세요.",
        "원하시면 더 이야기 나눌 수 있어요.",
    ],
    "crisis_redirect": [
        "지금 많이 힘드시다면, 전문 상담을 받아보시는 건 어떨까요?",
        "한국자살예방상담전화: 1393 / 정신건강위기상담전화: 1577-0199",
    ],
}
```

---

## 4. 건강 데이터 통합

### 4.1 건강 데이터 모델

```typescript
// health_data_model.ts
interface HealthRecord {
  id: string;
  user_id: string;
  date: string;                      // ISO 8601 (일 단위)

  sleep: SleepData | null;
  exercise: ExerciseData | null;
  diet: DietData | null;
  vitals: VitalsData | null;
  mood_log: MoodEntry | null;        // 감정일지 연동
}

interface SleepData {
  total_hours: number;
  sleep_time: string;                // "23:30"
  wake_time: string;                 // "07:00"
  quality_score: number;             // 1~10
  deep_sleep_min: number;
  rem_sleep_min: number;
  light_sleep_min: number;
  awake_count: number;
  source: "manual" | "healthkit" | "fitbit" | "samsung_health";
}

interface ExerciseData {
  activities: ExerciseActivity[];
  total_minutes: number;
  total_calories: number;
  steps: number;
  active_minutes: number;
}

interface ExerciseActivity {
  type: string;                      // "running", "weight_training", "yoga"
  duration_min: number;
  calories: number;
  intensity: "light" | "moderate" | "vigorous";
  heart_rate_avg?: number;
}

interface DietData {
  meals: Meal[];
  total_calories: number;
  water_ml: number;
  caffeine_mg: number;
}

interface Meal {
  type: "breakfast" | "lunch" | "dinner" | "snack";
  time: string;
  description: string;
  calories_estimated: number;
  photo_url?: string;               // 음식 사진 (AI 칼로리 추정)
}
```

### 4.2 HealthKit 연동

```python
# healthkit_integration.py
class HealthKitSync:
    """Apple HealthKit 데이터 동기화 (iOS 앱 경유)"""

    SYNC_CATEGORIES = {
        "sleep_analysis": {
            "hk_type": "HKCategoryTypeIdentifierSleepAnalysis",
            "sync_interval_hours": 6,
        },
        "step_count": {
            "hk_type": "HKQuantityTypeIdentifierStepCount",
            "sync_interval_hours": 1,
        },
        "heart_rate": {
            "hk_type": "HKQuantityTypeIdentifierHeartRate",
            "sync_interval_hours": 1,
        },
        "active_energy": {
            "hk_type": "HKQuantityTypeIdentifierActiveEnergyBurned",
            "sync_interval_hours": 1,
        },
    }

    PRIVACY_CONFIG = {
        "data_retention_days": 90,        # 90일 후 자동 삭제
        "encryption": "AES-256-GCM",
        "server_storage": "encrypted_only",
        "raw_data_ttl_hours": 24,         # 원시 데이터 24시간 후 삭제 (집계만 보관)
        "export_format": "json",
        "user_delete_on_request": True,   # GDPR 준수
    }
```

---

## 5. 스트레스 관리 백엔드

### 5.1 호흡법 (4-7-8 Breathing)

```python
# breathing_exercise.py
class BreathingExercise:
    """구조화된 호흡 운동 세션"""

    TECHNIQUES = {
        "4-7-8": {
            "name": "4-7-8 이완 호흡법",
            "description": "앤드루 와일 박사의 이완 호흡법",
            "phases": [
                {"action": "inhale", "duration_sec": 4, "instruction": "코로 숨을 깊이 들이쉽니다"},
                {"action": "hold", "duration_sec": 7, "instruction": "숨을 참습니다"},
                {"action": "exhale", "duration_sec": 8, "instruction": "입으로 천천히 내쉽니다"},
            ],
            "recommended_cycles": 4,
            "total_duration_sec": 76,   # 4 cycles * 19sec
        },
        "box": {
            "name": "박스 브리딩",
            "phases": [
                {"action": "inhale", "duration_sec": 4},
                {"action": "hold", "duration_sec": 4},
                {"action": "exhale", "duration_sec": 4},
                {"action": "hold", "duration_sec": 4},
            ],
            "recommended_cycles": 4,
        },
        "diaphragmatic": {
            "name": "복식 호흡",
            "phases": [
                {"action": "inhale", "duration_sec": 4, "instruction": "배가 부풀어 오르도록"},
                {"action": "hold", "duration_sec": 2, "instruction": "잠시 유지"},
                {"action": "exhale", "duration_sec": 6, "instruction": "배가 들어가도록"},
            ],
            "recommended_cycles": 10,
            "total_duration_sec": 120,   # 10 cycles * 12sec (LOCK-HW-07: 4-2-6)
        },
    }
```

### 5.2 그라운딩 기법 (5-4-3-2-1)

```python
# grounding_technique.py
class GroundingTechnique:
    """5-4-3-2-1 감각 그라운딩 기법"""

    STEPS = [
        {
            "sense": "시각",
            "count": 5,
            "prompt": "주위를 둘러보세요. 눈에 보이는 것 5가지를 말해주세요.",
            "examples": "예: 창문, 책상, 식물, 컵, 시계",
        },
        {
            "sense": "촉각",
            "count": 4,
            "prompt": "만질 수 있는 것 4가지를 찾아서 느껴보세요.",
            "examples": "예: 책상의 차가운 느낌, 옷감의 부드러움",
        },
        {
            "sense": "청각",
            "count": 3,
            "prompt": "지금 들리는 소리 3가지에 집중해보세요.",
            "examples": "예: 에어컨 소리, 새소리, 키보드 소리",
        },
        {
            "sense": "후각",
            "count": 2,
            "prompt": "냄새를 맡을 수 있는 것 2가지를 찾아보세요.",
            "examples": "예: 커피 향, 핸드크림 향",
        },
        {
            "sense": "미각",
            "count": 1,
            "prompt": "맛볼 수 있는 것 1가지를 떠올리거나 맛보세요.",
            "examples": "예: 물 한 모금, 민트 사탕",
        },
    ]

    async def guide_session(self, user_id: str) -> GroundingSession:
        """단계별 대화형 그라운딩 세션 진행"""
        session = GroundingSession(user_id=user_id, started_at=datetime.now())
        for step in self.STEPS:
            response = await self._prompt_and_wait(step)
            session.responses.append(response)
        session.completed = True
        return session
```

### 5.3 명상 가이드

```python
# meditation_guide.py
MEDITATION_PROGRAMS = {
    "mindfulness_basic": {
        "name": "기초 마음챙김",
        "duration_min": [5, 10, 15, 20],
        "sessions": 30,                      # 30일 프로그램
        "description": "호흡에 집중하는 기초 마음챙김 명상",
    },
    "body_scan": {
        "name": "바디스캔",
        "duration_min": [10, 15, 20],
        "description": "몸의 각 부위에 주의를 기울이는 명상",
    },
    "loving_kindness": {
        "name": "자애 명상",
        "duration_min": [10, 15],
        "description": "자신과 타인에 대한 따뜻한 마음 키우기",
    },
    "sleep": {
        "name": "수면 명상",
        "duration_min": [15, 20, 30],
        "description": "편안한 잠자리를 위한 이완 명상",
    },
}
```

### 5.4 CBT 인지 왜곡 감지

```python
# cbt_cognitive_distortion.py
class CBTDistortionDetector:
    """인지행동치료(CBT) 기반 인지 왜곡 자동 감지"""

    DISTORTION_TYPES = {
        "all_or_nothing": {
            "name": "흑백 사고",
            "description": "극단적인 이분법적 사고",
            "keywords": ["항상", "절대", "완전히", "전혀", "100%"],
            "reframe": "중간 지대를 찾아봅시다. 부분적으로 성공한 것은 없을까요?",
        },
        "overgeneralization": {
            "name": "과잉 일반화",
            "description": "하나의 사건을 전체로 확대",
            "keywords": ["맨날", "늘", "또", "매번", "아무도"],
            "reframe": "이번 한 번의 경험이 모든 것을 대표하진 않아요.",
        },
        "catastrophizing": {
            "name": "파국화",
            "description": "최악의 시나리오를 예상",
            "keywords": ["끝났어", "망했어", "최악", "파멸", "절망"],
            "reframe": "실제로 일어날 가능성은 얼마나 될까요? 최악이 아닌 시나리오도 생각해봅시다.",
        },
        "mind_reading": {
            "name": "독심술",
            "description": "상대방의 생각을 단정",
            "keywords": ["분명히 ~라고 생각할 거야", "~게 보일 거야", "다 알아"],
            "reframe": "실제로 확인하지 않고 추측하고 있진 않나요?",
        },
        "should_statements": {
            "name": "당위적 사고",
            "description": "'~해야 한다'는 경직된 기준",
            "keywords": ["해야 해", "해야 하는데", "~어야지", "의무"],
            "reframe": "'~하면 좋겠다'로 바꿔 생각해볼까요?",
        },
        "emotional_reasoning": {
            "name": "감정적 추론",
            "description": "감정을 사실로 받아들임",
            "keywords": ["느낌이 그러니까", "불안하니까 위험한 거야"],
            "reframe": "감정은 사실과 다를 수 있어요. 객관적 근거를 살펴볼까요?",
        },
        "personalization": {
            "name": "개인화",
            "description": "모든 것을 자기 탓으로 돌림",
            "keywords": ["내 탓", "내가 그래서", "나 때문에"],
            "reframe": "여러 요인 중 내 영향은 일부일 수 있어요.",
        },
    }

    async def detect(self, text: str) -> list[DistortionDetection]:
        """
        2단계 감지:
        1. 키워드 기반 사전 필터링 (빠른 감지)
        2. LLM 기반 정밀 분류 (컨텍스트 이해)
        """
        # Stage 1: 키워드 필터
        candidates = self._keyword_filter(text)

        # Stage 2: LLM 정밀 분류
        if candidates:
            detections = await self._llm_classify(text, candidates)
            return [d for d in detections if d.confidence >= 0.7]

        return []
```

---

## 6. 감정 일지 및 트렌드

### 6.1 감정 일지 기록 스키마

```typescript
// emotion_journal.ts
interface EmotionJournalEntry {
  id: string;
  user_id: string;
  timestamp: string;                 // ISO 8601

  // 감정 데이터
  emotion: EmotionState;             // §2.5 감정 분류 체계
  trigger?: string;                  // 감정 유발 요인 (선택)
  context?: string;                  // 상황 설명 (선택)

  // 사용자 입력
  journal_text?: string;             // 자유 텍스트 일기
  rating: number;                    // 1~10 주관적 기분 점수

  // 자동 수집
  auto_detected: boolean;            // 자동 감지 vs 수동 입력
  detection_source: ("text" | "speech" | "facial")[];
  associated_conversation_id?: string;

  // 건강 데이터 연계
  sleep_quality_prev_night?: number;
  exercise_today?: boolean;
  caffeine_intake_mg?: number;

  // CBT 관련
  cognitive_distortions?: string[];  // 감지된 인지 왜곡
  reframe_suggestion?: string;       // AI 리프레이밍 제안

  // 암호화
  encrypted: boolean;                // 항상 true
}
```

### 6.2 트렌드 분석

```python
# emotion_trend_analyzer.py
class EmotionTrendAnalyzer:
    """감정 일지 데이터 기반 트렌드 분석"""

    async def analyze(self, user_id: str, period_days: int = 30) -> EmotionTrend:
        entries = await self._fetch_entries(user_id, period_days)

        return EmotionTrend(
            # 기본 통계
            dominant_emotion=self._most_frequent_emotion(entries),
            average_mood=self._average_mood(entries),
            mood_stability=self._mood_stability(entries),   # 표준편차 기반

            # 시계열 패턴
            daily_pattern=self._daily_pattern(entries),      # 시간대별 감정 분포
            weekly_pattern=self._weekly_pattern(entries),    # 요일별 패턴
            trend_direction=self._trend_direction(entries),  # 개선/악화/안정

            # 상관관계
            sleep_mood_correlation=self._correlate("sleep_quality", "mood", entries),
            exercise_mood_correlation=self._correlate("exercise", "mood", entries),
            caffeine_anxiety_correlation=self._correlate("caffeine", "anxiety", entries),

            # 트리거 분석
            common_triggers=self._analyze_triggers(entries),

            # 위험 신호
            risk_indicators=self._detect_risk_indicators(entries),
        )
```

### 6.3 예측적 지원

```python
# predictive_support.py
class PredictiveEmotionSupport:
    """감정 트렌드 기반 선제적 지원"""

    INTERVENTION_TRIGGERS = {
        "mood_decline_3day": {
            "condition": "3일 연속 기분 점수 하락",
            "action": "부드러운 체크인 메시지",
            "severity": "low",
        },
        "persistent_negative": {
            "condition": "7일 중 5일 이상 부정 감정",
            "action": "스트레스 관리 도구 제안",
            "severity": "medium",
        },
        "sleep_mood_pattern": {
            "condition": "수면 부족 + 기분 저하 패턴 감지",
            "action": "수면 개선 팁 제공",
            "severity": "low",
        },
        "crisis_indicator": {
            "condition": "극단적 부정 감정 + 위기 키워드",
            "action": "전문기관 안내 (즉시)",
            "severity": "critical",
        },
    }

    async def check_and_intervene(self, user_id: str) -> Optional[Intervention]:
        trend = await self.trend_analyzer.analyze(user_id, period_days=7)
        for trigger_name, config in self.INTERVENTION_TRIGGERS.items():
            if self._evaluate_condition(trigger_name, trend):
                return Intervention(
                    type=trigger_name,
                    severity=config["severity"],
                    message=await self._generate_intervention_message(config, trend),
                )
        return None
```

### 6.4 시각화

| 차트 | 데이터 | 설명 |
|------|------|------|
| 감정 캘린더 | 일별 주요 감정 | GitHub 히트맵 스타일, 색상=감정 |
| 무드 라인 차트 | 기분 점수 추이 | 30일 트렌드 + 7일 이동평균 |
| 감정 분포 파이 | 기간별 감정 비율 | 주/월 단위 |
| Arousal-Valence 산점도 | 각성도-쾌감 분포 | Russell's circumplex 모델 |
| 상관관계 히트맵 | 건강지표-감정 상관 | 수면/운동/카페인 vs 감정 |
| 트리거 워드 클라우드 | 감정 유발 요인 | 빈도 기반 |

---

## 8. 비기능 요구사항

### 8.1 성능 SLA

| 지표 | 목표값 | 측정 방법 |
|------|--------|----------|
| 감정 분석 지연 | < 200ms (p95) | KoBERT 추론 + 후처리 |
| 위기 키워드 감지 | < 50ms (p99) | 정규식 + 사전 매칭 |
| 호흡 가이드 렌더링 | < 16ms/frame (60fps) | 애니메이션 프레임 타이밍 |
| 일지 저장 | < 500ms | AES-256-GCM 암호화 포함 |
| 트렌드 분석 (30일) | < 2s | 집계 쿼리 + 시각화 |

### 8.2 확장성

- 동시 사용자: 최대 10,000명 (V3 목표)
- 감정 기록/초: 500 records/sec (배치 처리)
- 저장소: 사용자당 평균 50MB/년 (감정 기록 + 일지 + 암호화 오버헤드)

### 8.3 가용성

- 감정 분석 서비스: 99.9% uptime (SLA)
- 위기 감지 서비스: 99.99% uptime (생명 안전 관련) ※ 안전-핵심 수치 — 차기 거버넌스 사이클에서 LOCK 보호 권고
- 데이터 백업: RPO 1시간, RTO 4시간

### 8.4 보안 SLA

- OWASP LLM Top 10 (2025) 전 항목 대응
- 감정 데이터 암호화: AES-256-GCM (LOCK-HW-06)
- 프라이버시 3등급 체계 준수 (LOCK-HW-02): PRIVATE/PROTECTED/HIGHEST
- 외부 전송 차단: HIGHEST 등급 데이터 네트워크 ACL + iptables 규칙으로 물리적 차단
- 접근 감사 로그: 100% 기록, 90일 보존

---

## 9. 테스트 전략

### 9.1 단위 테스트

| 모듈 | 커버리지 목표 | 핵심 테스트 케이스 |
|------|-------------|-----------------|
| 감정 분류기 | ≥ 85% | 12감정 각 100+ 샘플, 경계값 (arousal/valence 0.0, 0.5, 1.0) |
| 위기 감지 | ≥ 95% | 위기 키워드 전수(§B.2), 오탐 시나리오 50건, 언어 변형 |
| 호흡 가이드 | ≥ 80% | 3패턴(4-7-8, Box, 횡격막) × 타이밍 정확도 ±100ms |
| 암호화 레이어 | ≥ 90% | AES-256-GCM 라운드트립, 키 로테이션, 무결성 검증 |

### 9.2 통합 테스트

- IT-1: 감정 인식 → 적응 응답 → 일지 기록 E2E 플로우
- IT-2: 위기 감지 → 안전 프로토콜 → 리소스 제공 → 로그 기록
- IT-3: 건강 데이터 동기화 → 프라이버시 등급 검증 → 접근 제어
- IT-4: CBT 인지 왜곡 감지 → 리프레이밍 → 사용자 피드백 루프
- IT-5: 교차도메인 Education(#8) → 감정 요약 전달 (opt-in 동의 검증)

### 9.3 성능 테스트

- 부하 테스트: 10,000 동시 감정 분석 요청, p95 < 200ms 검증
- 스트레스 테스트: 감정 기록 50,000건/분 배치 처리
- 내구성 테스트: 72시간 연속 운영, 메모리 누수 0건 확인

---

## 7. 교차참조

| 참조 모듈 | 연관 항목 | 참조 방향 |
|----------|---------|----------|
| T2-CORE_AI (2-2) | LLM 공감 응답, CBT 분석 | ← 사용 |
| T3-Multimodal (3-2) | 음성 감정 인식, TTS | ← 사용 |
| T3-Education (3-5) | 학습 스트레스 모니터링 | → 제공 |
| T3-PKM (3-3) | 감정 일지 지식화 | → 제공 |
| T4-Frontend (4-1) | 감정 대시보드, 호흡 UI, 명상 UI | → 제공 |
| T1-INFRA (1-x) | 암호화 저장, 프라이버시 인프라 | ← 사용 |

---

*끝 — HEALTH_WELLNESS_EMOTIONAI 상세명세 v1.0.0*
