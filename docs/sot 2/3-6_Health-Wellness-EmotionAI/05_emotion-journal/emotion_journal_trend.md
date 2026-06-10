# emotion_journal_trend.md — 감정 일지 기록 및 트렌드 분석

> **P-ID**: P-003, P-003-a (V2 골격), P-003-b (V2 골격)
> **V단계**: V1
> **상태**: P-003 EXTEND / P-003-a NEW (V2 골격) / P-003-b NEW (V2 골격)
> **L3 완성**: 2026-04-10
> **정본 소유자**: sot 2/3-6_Health-Wellness-EmotionAI/05_emotion-journal/

---

## 교차 참조 블록

| 참조 문서 | 위치 | 참조 내용 |
|----------|------|----------|
| 종합계획서 §3.4 | LOCK-HW-12 | 감정 강도 척도 1-10 정수 |
| 종합계획서 §3.4 | LOCK-HW-01 | 감정 분류 모델 7+5+2 |
| 종합계획서 §3.4 | LOCK-HW-04 | 비의료 면책 문구 |
| 종합계획서 §6.5 | 매핑 테이블 13항목 | P-003/P-003-a/P-003-b 배정 |
| 종합계획서 §4 | R-09-1~R-09-7 | 도메인 전용 거버넌스 규칙 |
| 상세명세 §6 | §6.1~§6.4 | 감정 일지 기존 명세 (레거시 참조) |
| STEP7-P | P-003 | 감정 기록 및 트렌드 원본 체크리스트 |
| AUTHORITY_CHAIN.md | §1~§5 | 정본 계층 및 충돌 해결 |
| 01_emotion-recognition/text_emotion_analysis.md | §4~§7 | 감정 분석 결과 입력 인터페이스 |
| 06_ethics-privacy/ethics_framework.md | §3 7원칙 | 비조작/비진단/프라이버시 원칙 적용 |
| 06_ethics-privacy/crisis_protocol.md | §3~§5 | 위기 감지 연동 (crisis_indicator) |
| 05_emotion-journal/wellness_score.md | VWS 연동 | 감정 차원 → VWS 감정 점수 전달 |

---

## 1. 개요

본 문서는 VAMOS 감정 일지 기록 및 트렌드 분석 모듈을 L3 구현 즉시 투입 가능 수준으로 정의한다. 사용자의 일별 감정을 7+5+2 감정 분류 체계(LOCK-HW-01)에 따라 기록하고, 1-10 정수 강도 척도(LOCK-HW-12)로 감정의 세기를 정량화한다. 기록된 감정 데이터를 기반으로 주간/월간 트렌드를 분석하여 감정-행동 상관관계를 도출한다.

**입력**: 사용자 감정 기록 (자동 태깅 + 수동 입력)
**출력**: `EmotionJournalEntry`, `EmotionTrendReport`

---

## 2. LOCK 인용

> LOCK (LOCK-HW-12, 기존 명세 §2): 1-10 정수 척도

> LOCK (LOCK-HW-01, 기존 명세 §2/STEP7-P P-001): 기본7(기쁨,슬픔,분노,불안,놀람,혐오,중립)+세부5(피로,스트레스,좌절,열정,호기심)+차원2(arousal,valence)

> LOCK (LOCK-HW-04, STEP7-P 윤리원칙): "VAMOS는 의료 서비스가 아닙니다" 모든 건강 관련 응답에 포함

---

## 3. 감정 일지 데이터 모델 (P-003)

### 3.1 Input Schema

```python
from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum
from datetime import datetime

class PrimaryEmotion(Enum):
    """LOCK-HW-01 기본 7감정"""
    JOY = "기쁨"
    SADNESS = "슬픔"
    ANGER = "분노"
    ANXIETY = "불안"
    SURPRISE = "놀람"
    DISGUST = "혐오"
    NEUTRAL = "중립"

class SecondaryEmotion(Enum):
    """LOCK-HW-01 세부 5감정"""
    FATIGUE = "피로"
    STRESS = "스트레스"
    FRUSTRATION = "좌절"
    ENTHUSIASM = "열정"
    CURIOSITY = "호기심"

@dataclass
class EmotionJournalInput:
    """감정 일지 기록 입력"""
    user_id: str                                      # 사용자 식별자
    primary_emotion: PrimaryEmotion                    # LOCK-HW-01 기본 7감정 중 1
    intensity: int                                     # LOCK-HW-12: 1-10 정수 척도
    secondary_emotion: Optional[SecondaryEmotion] = None  # 세부 5감정 (선택)
    trigger: Optional[str] = None                      # 감정 유발 요인 (최대 200자)
    context: Optional[str] = None                      # 상황 설명 (최대 500자)
    journal_text: Optional[str] = None                 # 자유 텍스트 일기 (최대 2000자)
    auto_detected: bool = False                        # True=자동감지, False=수동입력
    detection_source: List[str] = field(default_factory=list)  # ["text", "speech", "facial"]
    associated_conversation_id: Optional[str] = None   # 관련 대화 ID

    def __post_init__(self):
        if not (1 <= self.intensity <= 10):
            raise ValueError(f"intensity must be 1-10 (LOCK-HW-12), got {self.intensity}")
        if self.trigger and len(self.trigger) > 200:
            raise ValueError("trigger max 200 chars")
        if self.context and len(self.context) > 500:
            raise ValueError("context max 500 chars")
        if self.journal_text and len(self.journal_text) > 2000:
            raise ValueError("journal_text max 2000 chars")
```

**제약조건**:
- `intensity`: 1-10 정수만 허용 (LOCK-HW-12 준수)
- `primary_emotion`: LOCK-HW-01 기본 7감정 enum 값만 허용
- `secondary_emotion`: LOCK-HW-01 세부 5감정 enum 값만 허용 (Optional)
- `journal_text`: 프라이버시 등급 PRIVATE (LOCK-HW-02), 로컬 저장 전용

### 3.2 Output Schema

```python
@dataclass
class EmotionJournalEntry:
    """감정 일지 기록 결과 (저장 단위)"""
    id: str                                    # UUID v4
    user_id: str
    timestamp: datetime                        # ISO 8601 (UTC)
    
    # 감정 데이터 (LOCK-HW-01)
    primary_emotion: PrimaryEmotion
    secondary_emotion: Optional[SecondaryEmotion]
    intensity: int                             # LOCK-HW-12: 1-10
    arousal: float                             # -1.0 ~ +1.0 (Russell's Circumplex Y축)
    valence: float                             # -1.0 ~ +1.0 (Russell's Circumplex X축)
    
    # 사용자 입력
    trigger: Optional[str]
    context: Optional[str]
    journal_text: Optional[str]
    
    # 메타데이터
    auto_detected: bool
    detection_source: List[str]
    associated_conversation_id: Optional[str]
    
    # 건강 데이터 연계 (03_health-data 참조)
    sleep_quality_prev_night: Optional[float]  # 0-100 수면 점수
    exercise_today: Optional[bool]
    
    # CBT 관련 (06_ethics-privacy 참조)
    cognitive_distortions: List[str] = field(default_factory=list)
    reframe_suggestion: Optional[str] = None
    
    # 보안
    encrypted: bool = True                     # 항상 True (LOCK-HW-06: AES-256-GCM)
    privacy_level: str = "PRIVATE"             # LOCK-HW-02: 감정=PRIVATE
```

### 3.3 arousal/valence 산출 공식

감정별 중심값 테이블 기반으로 arousal/valence를 자동 산출한다:

| 감정 | arousal 중심 | valence 중심 |
|------|-------------|-------------|
| 기쁨 | +0.55 | +0.75 |
| 슬픔 | -0.20 | -0.55 |
| 분노 | +0.75 | -0.50 |
| 불안 | +0.55 | -0.35 |
| 놀람 | +0.75 | +0.15 |
| 혐오 | +0.30 | -0.75 |
| 중립 | 0.00 | 0.00 |
| 피로 | -0.45 | -0.30 |
| 스트레스 | +0.65 | -0.45 |
| 좌절 | +0.50 | -0.40 |
| 열정 | +0.80 | +0.75 |
| 호기심 | +0.40 | +0.30 |

**산출**:
```
arousal_base = PRIMARY_CENTER[primary_emotion].arousal
valence_base = PRIMARY_CENTER[primary_emotion].valence

if secondary_emotion:
    arousal = 0.7 * arousal_base + 0.3 * SECONDARY_CENTER[secondary_emotion].arousal
    valence = 0.7 * valence_base + 0.3 * SECONDARY_CENTER[secondary_emotion].valence
else:
    arousal = arousal_base
    valence = valence_base

# intensity 가중 (고강도 → 극단값 방향 확대)
intensity_factor = (intensity - 5) / 10  # -0.4 ~ +0.5
arousal = clamp(arousal + intensity_factor * 0.2, -1.0, 1.0)
valence = clamp(valence + intensity_factor * sign(valence) * 0.15, -1.0, 1.0)
```

---

## 4. 감정 일지 기록 파이프라인

### 4.1 파이프라인 아키텍처

```
[감정 기록 요청]
        │
        ▼
[1. 입력 검증 (Validation)]
        │  intensity 1-10 범위, emotion enum 유효성
        ▼
[2. 자동 감정 보강 (Auto-Enrichment)]
        │  대화 기반 자동 태깅 결과 병합 (auto_detected=True 시)
        ▼
[3. arousal/valence 산출]
        │  §3.3 공식 적용
        ▼
[4. 건강 데이터 연계]
        │  03_health-data: 전날 수면/당일 운동 조회 (Optional)
        ▼
[5. CBT 인지왜곡 감지]
        │  06_ethics-privacy: journal_text 분석 (Optional)
        ▼
[6. 위기 신호 점검]
        │  crisis_protocol 연동: intensity>=9 + 부정 감정 → 위기 평가
        ▼
[7. 암호화 + 저장]
        │  AES-256-GCM (LOCK-HW-06), 프라이버시 PRIVATE (LOCK-HW-02)
        ▼
[8. VWS 갱신 알림]
        │  wellness_score 모듈에 감정 점수 변경 이벤트 발행
        ▼
[9. 출력: EmotionJournalEntry]
```

### 4.2 알고리즘 의사코드

```python
class EmotionJournalService:
    """감정 일지 기록 서비스"""
    
    DISCLAIMER = "⚠️ VAMOS는 의료 서비스가 아닙니다. (LOCK-HW-04)"
    
    async def record_entry(self, input: EmotionJournalInput) -> EmotionJournalEntry:
        """
        감정 일지 기록 메인 함수
        Time Complexity: O(1) 기본 기록 + O(n) CBT 분석 (n=journal_text 토큰 수)
        Space Complexity: O(1) 기본 + O(n) 텍스트 저장
        SLA: p95 < 150ms (CBT 분석 제외), p95 < 500ms (CBT 분석 포함)
        """
        # 1. 입력 검증
        self._validate_input(input)
        
        # 2. 자동 감정 보강 (text_emotion_analysis 결과 존재 시 병합)
        if input.auto_detected and input.associated_conversation_id:
            auto_result = await self.emotion_analyzer.get_latest(
                input.user_id, input.associated_conversation_id
            )
            if auto_result and not input.secondary_emotion:
                input.secondary_emotion = auto_result.secondary_emotion
        
        # 3. arousal/valence 산출 (§3.3)
        arousal, valence = self._compute_arousal_valence(
            input.primary_emotion, input.secondary_emotion, input.intensity
        )
        
        # 4. 건강 데이터 연계 (Optional, 실패 시 None)
        sleep_quality = await self._safe_fetch_sleep(input.user_id)
        exercise_today = await self._safe_fetch_exercise(input.user_id)
        
        # 5. CBT 인지왜곡 감지 (journal_text 존재 시)
        distortions = []
        reframe = None
        if input.journal_text:
            distortions, reframe = await self._detect_cognitive_distortions(
                input.journal_text
            )
        
        # 6. 위기 신호 점검
        if input.intensity >= 9 and input.primary_emotion in (
            PrimaryEmotion.SADNESS, PrimaryEmotion.ANXIETY, PrimaryEmotion.ANGER
        ):
            await self.crisis_checker.evaluate(
                user_id=input.user_id,
                emotion=input.primary_emotion,
                intensity=input.intensity,
                text=input.journal_text
            )
        
        # 7. 엔트리 생성 + 암호화 저장
        entry = EmotionJournalEntry(
            id=generate_uuid_v4(),
            user_id=input.user_id,
            timestamp=datetime.utcnow(),
            primary_emotion=input.primary_emotion,
            secondary_emotion=input.secondary_emotion,
            intensity=input.intensity,
            arousal=arousal,
            valence=valence,
            trigger=input.trigger,
            context=input.context,
            journal_text=input.journal_text,
            auto_detected=input.auto_detected,
            detection_source=input.detection_source,
            associated_conversation_id=input.associated_conversation_id,
            sleep_quality_prev_night=sleep_quality,
            exercise_today=exercise_today,
            cognitive_distortions=distortions,
            reframe_suggestion=reframe,
            encrypted=True,
            privacy_level="PRIVATE"
        )
        
        await self.store.save_encrypted(entry)  # AES-256-GCM (LOCK-HW-06)
        
        # 8. VWS 갱신 이벤트 발행
        await self.event_bus.publish("emotion.journal.recorded", {
            "user_id": input.user_id,
            "primary_emotion": input.primary_emotion.value,
            "intensity": input.intensity,
            "arousal": arousal,
            "valence": valence,
            "timestamp": entry.timestamp.isoformat()
        })
        
        return entry
    
    def _validate_input(self, input: EmotionJournalInput):
        if not (1 <= input.intensity <= 10):
            raise ValidationError("LOCK-HW-12: intensity must be 1-10")
        if input.primary_emotion not in PrimaryEmotion:
            raise ValidationError("LOCK-HW-01: invalid primary emotion")
    
    def _compute_arousal_valence(
        self, primary: PrimaryEmotion, secondary: Optional[SecondaryEmotion], intensity: int
    ) -> tuple[float, float]:
        """§3.3 arousal/valence 산출"""
        arousal_base = AROUSAL_CENTER[primary]
        valence_base = VALENCE_CENTER[primary]
        
        if secondary:
            arousal = 0.7 * arousal_base + 0.3 * AROUSAL_CENTER[secondary]
            valence = 0.7 * valence_base + 0.3 * VALENCE_CENTER[secondary]
        else:
            arousal = arousal_base
            valence = valence_base
        
        intensity_factor = (intensity - 5) / 10
        arousal = max(-1.0, min(1.0, arousal + intensity_factor * 0.2))
        valence = max(-1.0, min(1.0, valence + intensity_factor * (1 if valence >= 0 else -1) * 0.15))
        
        return round(arousal, 3), round(valence, 3)
```

**Big-O 분석**:
| 연산 | Time | Space | 비고 |
|------|------|-------|------|
| 기록 (기본) | O(1) | O(1) | 검증 + arousal/valence + 저장 |
| CBT 분석 | O(n) | O(n) | n = journal_text 토큰 수, max 2000자 |
| 건강 데이터 조회 | O(1) | O(1) | 캐시 hit 시 / API 호출 시 네트워크 의존 |
| 위기 점검 | O(k) | O(1) | k = 위기 키워드 수 (고정, ~100개) |

---

## 5. 트렌드 분석 (P-003)

### 5.1 트렌드 분석 Output Schema

```python
@dataclass
class EmotionTrendReport:
    """감정 트렌드 분석 보고서"""
    user_id: str
    period_start: datetime
    period_end: datetime
    total_entries: int
    
    # 기본 통계
    dominant_emotion: PrimaryEmotion           # 최빈 감정
    average_intensity: float                   # 평균 강도 (1.0-10.0)
    mood_stability: float                      # 안정도 (표준편차 역수, 0-1)
    
    # 시계열 패턴
    daily_pattern: dict[int, PrimaryEmotion]   # hour(0-23) → 주요 감정
    weekly_pattern: dict[str, PrimaryEmotion]  # weekday → 주요 감정
    trend_direction: str                       # "improving" | "declining" | "stable"
    
    # 상관관계
    sleep_mood_correlation: float              # -1.0 ~ +1.0 (Pearson)
    exercise_mood_correlation: float           # -1.0 ~ +1.0 (Pearson)
    
    # 트리거 분석
    common_triggers: List[tuple[str, int]]     # [(trigger, count), ...]
    
    # 위험 신호
    risk_indicators: List[str]                 # 위험 지표 목록
    
    # 비의료 면책
    disclaimer: str = "⚠️ VAMOS는 의료 서비스가 아닙니다. 본 분석은 참고용이며, 전문 의료 상담을 대체하지 않습니다. (LOCK-HW-04)"
```

### 5.2 트렌드 분석 알고리즘

```python
class EmotionTrendAnalyzer:
    """감정 트렌드 분석 엔진"""
    
    async def analyze(
        self, user_id: str, period_days: int = 30
    ) -> EmotionTrendReport:
        """
        주기적 감정 트렌드 분석
        Time Complexity: O(n log n) — n=기간 내 엔트리 수, 정렬 + 통계
        Space Complexity: O(n) — 엔트리 로드
        SLA: p95 < 2000ms (30일 기준, 최대 ~90 엔트리)
        """
        entries = await self.store.fetch_entries(
            user_id, period_days, decrypt=True
        )
        # 시간순 정렬 강제 — period_start/end, trend_direction, 연속일 risk_indicators 정확성 보장
        entries = sorted(entries, key=lambda e: e.timestamp)
        
        if len(entries) < 3:
            raise InsufficientDataError("최소 3건 이상 기록 필요")
        
        return EmotionTrendReport(
            user_id=user_id,
            period_start=entries[0].timestamp,
            period_end=entries[-1].timestamp,
            total_entries=len(entries),
            dominant_emotion=self._most_frequent_emotion(entries),
            average_intensity=self._average_intensity(entries),
            mood_stability=self._mood_stability(entries),
            daily_pattern=self._daily_pattern(entries),
            weekly_pattern=self._weekly_pattern(entries),
            trend_direction=self._trend_direction(entries),
            sleep_mood_correlation=self._correlate("sleep_quality_prev_night", "intensity", entries),
            exercise_mood_correlation=self._correlate_exercise("exercise_today", "valence", entries),
            common_triggers=self._analyze_triggers(entries),
            risk_indicators=self._detect_risk_indicators(entries),
        )
    
    def _most_frequent_emotion(self, entries: List[EmotionJournalEntry]) -> PrimaryEmotion:
        """최빈 감정 산출 — O(n)"""
        counter = {}
        for e in entries:
            counter[e.primary_emotion] = counter.get(e.primary_emotion, 0) + 1
        return max(counter, key=counter.get)
    
    def _average_intensity(self, entries: List[EmotionJournalEntry]) -> float:
        """평균 강도 — O(n)"""
        return round(sum(e.intensity for e in entries) / len(entries), 2)
    
    def _mood_stability(self, entries: List[EmotionJournalEntry]) -> float:
        """
        감정 안정도 = 1 / (1 + std(intensity))
        범위: 0(불안정) ~ 1(완전 안정)
        O(n)
        """
        intensities = [e.intensity for e in entries]
        mean = sum(intensities) / len(intensities)
        variance = sum((x - mean) ** 2 for x in intensities) / len(intensities)
        std = variance ** 0.5
        return round(1 / (1 + std), 3)
    
    def _trend_direction(self, entries: List[EmotionJournalEntry]) -> str:
        """
        최근 7일 평균 valence vs 이전 기간 평균 valence 비교
        차이 > +0.1 → improving, < -0.1 → declining, else → stable
        O(n)
        """
        if len(entries) < 7:
            return "stable"
        recent = entries[-7:]
        earlier = entries[:-7]
        recent_avg = sum(e.valence for e in recent) / len(recent)
        earlier_avg = sum(e.valence for e in earlier) / len(earlier)
        diff = recent_avg - earlier_avg
        if diff > 0.1:
            return "improving"
        elif diff < -0.1:
            return "declining"
        return "stable"
    
    def _detect_risk_indicators(self, entries: List[EmotionJournalEntry]) -> List[str]:
        """
        위험 신호 감지 — 위기 프로토콜(crisis_protocol.md) 연동 트리거
        O(n)
        """
        indicators = []
        
        # 3일 연속 기분 하락
        if len(entries) >= 3:
            last_3 = entries[-3:]
            if all(e.intensity <= 3 and e.valence < -0.3 for e in last_3):
                indicators.append("mood_decline_3day")
        
        # 7일 중 5일 이상 부정 감정
        if len(entries) >= 7:
            last_7 = entries[-7:]
            negative_count = sum(
                1 for e in last_7
                if e.primary_emotion in (
                    PrimaryEmotion.SADNESS, PrimaryEmotion.ANGER,
                    PrimaryEmotion.ANXIETY, PrimaryEmotion.DISGUST
                )
            )
            if negative_count >= 5:
                indicators.append("persistent_negative_7day")
        
        # 극단적 강도 (intensity >= 9 + 부정 감정)
        extreme = [
            e for e in entries[-7:]
            if e.intensity >= 9 and e.valence < -0.5
        ]
        if extreme:
            indicators.append("extreme_negative_intensity")
        
        return indicators
```

### 5.3 감정-행동 상관 분석

| 상관쌍 | 데이터 소스 | 방법 | 해석 |
|--------|-----------|------|------|
| 수면↔기분 | sleep_quality_prev_night ↔ intensity | Pearson r | r>0.3: 수면이 기분에 유의미한 영향 |
| 운동↔기분 | exercise_today ↔ valence | Point-biserial | rpb>0.2: 운동일에 긍정 감정 유의미 증가 |
| 카페인↔불안 | caffeine_intake ↔ anxiety_intensity | Pearson r | r>0.3: 카페인이 불안 수준에 영향 |
| 트리거↔감정 | trigger_category ↔ primary_emotion | Chi-squared | p<0.05: 특정 트리거와 감정 간 유의미 연관 |

---

## 6. 에러 처리 및 Graceful Degradation

### 6.1 에러 유형별 처리

| 에러 유형 | 원인 | 처리 | 폴백 |
|----------|------|------|------|
| `ValidationError` | intensity 범위 초과, 무효 emotion | 400 반환 + 사용자 안내 | 없음 (입력 교정 필요) |
| `InsufficientDataError` | 트렌드 분석 최소 기록 수 미달 | 기록 수 안내 + 목표 제시 | 단순 통계만 반환 |
| `EncryptionError` | AES-256-GCM 암호화 실패 | 재시도 1회 → 실패 시 기록 거부 | **기록 거부** (보안 우선) |
| `HealthDataFetchError` | 건강 데이터 API 호출 실패 | sleep/exercise = None 처리 | 감정 데이터만으로 기록 완성 |
| `CrisisCheckError` | 위기 평가 서비스 장애 | **즉시 기본 위기 안내 표시** (R-09-2) | 전화번호 직접 표시 |
| `StorageError` | 저장소 쓰기 실패 | 재시도 3회 (지수 백오프) | 로컬 큐에 임시 저장 → 복구 후 flush |

### 6.2 위기 신호 폴백 (R-09-2 필수)

위기 평가 서비스 장애 시에도 **반드시** 전문기관 안내를 표시한다:

```python
CRISIS_FALLBACK_MESSAGE = """
긴급 도움이 필요하시면 아래 번호로 연락해 주세요:
- 자살예방상담전화: 1393 (24시간)
- 정신건강위기상담전화: 1577-0199 (24시간)
⚠️ VAMOS는 의료 서비스가 아닙니다. (LOCK-HW-04)
"""
# LOCK-HW-05: 자살예방 1393, 정신건강위기 1577-0199
```

---

## 7. 윤리/프라이버시 준수 (E6)

### 7.1 프라이버시 적용

| 데이터 | 프라이버시 등급 (LOCK-HW-02) | 저장 위치 | 보존 기간 (LOCK-HW-03) |
|--------|---------------------------|----------|----------------------|
| 감정 기록 (일지) | **PRIVATE** (로컬전용) | 로컬 암호화 DB | 사용자 설정 (기본 180일) |
| journal_text | **PRIVATE** | 로컬 암호화 DB | 사용자 설정 (기본 180일) |
| 트렌드 통계 (집계) | PRIVATE | 로컬 | 90일 |
| arousal/valence | PRIVATE | 로컬 | 사용자 설정 (기본 180일) |

### 7.2 윤리 원칙 적용 (LOCK-HW-09)

| 원칙 | 적용 방법 |
|------|----------|
| 비진단 | 트렌드 분석 결과에 "진단"/"치료" 단어 사용 금지 (R-09-4) |
| 프라이버시 | 감정 데이터 외부 전송 절대 금지 (R-09-3) |
| 투명성 | 자동 태깅 시 사용자에게 수정 기회 제공 |
| 전문가연결 | risk_indicators 감지 시 전문기관 안내 (R-09-2) |
| 비조작 | 감정 일지 분석을 구매/행동 유도에 사용 금지 (R-09-7) |
| 자율성 | 기록은 항상 사용자 선택, 자동 태깅 비활성 가능 |
| 기능끄기 | 감정 일지 기능 전체 비활성 옵션 제공 |

### 7.3 비의료 면책 (LOCK-HW-04)

모든 트렌드 분석 결과에 아래 면책 문구를 포함한다:

- **한국어**: "⚠️ VAMOS는 의료 서비스가 아닙니다. 본 분석은 참고용이며, 전문 의료 상담을 대체하지 않습니다."
- **영어**: "⚠️ VAMOS is not a medical service. This analysis is for reference only and does not replace professional medical consultation."

---

## 8. Performance SLA (E7)

| 연산 | p50 | p95 | p99 | 비고 |
|------|-----|-----|-----|------|
| 감정 일지 기록 (기본) | 30ms | 100ms | 150ms | 저장 포함 |
| 감정 일지 기록 (CBT 포함) | 150ms | 400ms | 500ms | CBT 분석 포함 |
| 트렌드 분석 (30일) | 500ms | 1500ms | 2000ms | 최대 ~90 엔트리 |
| 트렌드 분석 (7일) | 100ms | 300ms | 500ms | 최대 ~21 엔트리 |

---

## 9. 통합 테스트 시나리오 (E8)

| # | 시나리오 | 입력 | 기대 출력 | 검증 포인트 |
|---|---------|------|----------|-----------|
| T1 | 기본 기록 — 기쁨 | primary=JOY, intensity=7 | entry.arousal>0, entry.valence>0 | LOCK-HW-01/12 준수 |
| T2 | 최소 강도 | primary=NEUTRAL, intensity=1 | arousal≈0, valence≈0 | 경계값 1 |
| T3 | 최대 강도 | primary=ANGER, intensity=10 | arousal>0.8, valence<-0.5 | 경계값 10 |
| T4 | 복합 감정 | primary=ANXIETY, secondary=STRESS, intensity=8 | 양쪽 반영 | 7:3 가중 |
| T5 | 자동 태깅 병합 | auto_detected=True, conv_id 존재 | secondary 보강됨 | 자동 보강 로직 |
| T6 | 건강 데이터 연계 실패 | health API 장애 | sleep=None, entry 정상 저장 | Graceful Degradation |
| T7 | 위기 신호 감지 | primary=SADNESS, intensity=9 | crisis_checker 호출됨 | R-09-2 준수 |
| T8 | 트렌드 — 개선 | 최근 7일 valence 상승 | trend_direction="improving" | 방향 판정 |
| T9 | 트렌드 — 위험 | 3일 연속 intensity<=3, valence<-0.3 | risk_indicators에 "mood_decline_3day" | 위험 감지 |
| T10 | 프라이버시 — 외부 전송 금지 | 외부 API 호출 시도 | 차단됨, 로컬만 저장 | R-09-3/LOCK-HW-02 |
| T11 | 암호화 실패 시 | AES-256-GCM 장애 | 기록 거부, 에러 반환 | 보안 우선 (LOCK-HW-06) |
| T12 | 비의료 면책 포함 | 트렌드 보고서 생성 | disclaimer 필드 존재 | LOCK-HW-04/R-09-1 |

---

## 10. 의존성 (E9)

| 의존 대상 | 유형 | 인터페이스 | 방향 |
|----------|------|-----------|------|
| 01_emotion-recognition/text_emotion_analysis.md | 내부 | TextEmotionResult → auto_detected 보강 | ← 수신 |
| 03_health-data/sleep_management.md | 내부 | GET /api/health/sleep/latest → sleep_quality | ← 수신 |
| 03_health-data/activity_exercise.md | 내부 | GET /api/health/exercise/today → exercise_today | ← 수신 |
| 06_ethics-privacy/crisis_protocol.md | 내부 | crisis_checker.evaluate() → 위기 대응 | ← 수신 |
| 06_ethics-privacy/cbt_distortion_taxonomy.md | 내부 | detect_distortions() → cognitive_distortions | ← 수신 |
| 05_emotion-journal/wellness_score.md | 내부 | event: emotion.journal.recorded → VWS 갱신 | → 발신 |
| 05_emotion-journal/investment_emotion_guard.md | 내부 | 감정 상태 조회 → 투자 가드 판단 | → 발신 |
| ORANGE CORE | 외부 | EmotionState 인터페이스 | ↔ 양방향 |

---

## 11. 위기 프로토콜 준수 (E10)

- risk_indicators 감지 시 crisis_protocol.md §3 3단계 감지 파이프라인 연동
- `extreme_negative_intensity` → HIGH 위험도 평가 요청
- `persistent_negative_7day` → MEDIUM 위험도 평가 요청
- `mood_decline_3day` → LOW 위험도: 부드러운 체크인 메시지 + 전문기관 안내 옵션
- 위기 평가 서비스 장애 시 §6.2 폴백 (LOCK-HW-05: 1393, 1577-0199 직접 표시)

---

## V2 골격: P-003-a 감정 시계열 시각화

> **상태**: V2 골격 — Phase 2에서 L3 완성 예정

### 시각화 컴포넌트 목록 (Phase 2 구현)

| 차트 | 데이터 | 설명 |
|------|--------|------|
| 감정 캘린더 | 일별 주요 감정 | GitHub 히트맵 스타일, 색상=감정 |
| 무드 라인 차트 | 기분 점수 추이 | 30일 트렌드 + 7일 이동평균 |
| 감정 분포 파이 | 기간별 감정 비율 | 주/월 단위 |
| Arousal-Valence 산점도 | 각성도-쾌감 분포 | Russell's Circumplex 모델 |
| 상관관계 히트맵 | 건강지표-감정 상관 | 수면/운동/카페인 vs 감정 |
| 트리거 워드 클라우드 | 감정 유발 요인 | 빈도 기반 |

---

## V2 골격: P-003-b 감정 트리거 자동 분석

> **상태**: V2 골격 — Phase 2에서 L3 완성 예정

### 트리거 자동 분류 개요 (Phase 2 구현)

- 감정 트리거 텍스트 NLP 분석 → 자동 카테고리 분류
- 카테고리: 업무/대인관계/건강/재정/기타
- "투자 손실 후 스트레스 패턴" 등 패턴 자동 감지 (STEP7-P P-003 요구사항)
- 트리거-감정 상관관계 학습 → 선제적 지원 트리거

---

## ABC 시그니처

```
ABC-3-6-05-EJT-V1 = {
  doc: "emotion_journal_trend.md",
  version: "V1-L3",
  lock_refs: ["HW-01", "HW-04", "HW-12"],
  p_ids: ["P-003", "P-003-a(skeleton)", "P-003-b(skeleton)"],
  dependencies: ["text_emotion_analysis", "crisis_protocol", "wellness_score"],
  created: "2026-04-10",
  session: "P1-6"
}
```
