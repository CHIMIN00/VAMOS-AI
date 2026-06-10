# COND-098 감정 일지 (Emotion Journal)

> **Status**: V2-Phase 2
> **모듈 ID**: COND-098
> **카테고리**: CAT-F Wellbeing
> **우선순위**: HIGH
> **버전**: V2 (Phase 2, 2026-04-19)
> **작성 단계**: STAGE 7 / Phase 7-II / 2-2 STEP_B / 세션 2-2
> **Phase 1 대응**: 종합명세 §98 + `06_cat-f-wellbeing/_index.md`
> **LOCK 준수**: LOCK-CD-01 / LOCK-CD-03 / LOCK-CD-04 / LOCK-CD-05 / LOCK-CD-06 / LOCK-CD-10 + LOCK-CD-08 (Wellness Node P2 종속)
> **§A.1 표면화**: A↔F 양방향 경로 COND-025 (CAT-A 감정패턴 학습) → COND-098 (본 모듈) **실체화** (세션 2-1 COND-091 §6.4 질의에 대한 응답)

---

## §0 교차 참조 블록 (정본)

- **종합계획서**: `COND_MODULES_DETAIL_구조화_종합계획서.md` §7.4 L836~L893 / §13.1 / **§A.1 L1137 CAT-A ← CAT-F 방향** + **§A.2 L1209 COND-025→COND-098 (A→F)** 양방향 실체화 지점
- **종합명세**: `COND_MODULES_종합명세.md` §#98 (I/O 정의 L1312~L1322)
- **AUTHORITY_CHAIN**: `AUTHORITY_CHAIN.md` §4 LOCK-CD-01~11
- **Blue Node 정본**: `D2.0-03 §5` (Wellness Node P2)
- **ErrorHandlingStandard 정본**: `D2.0-02 §0.3`
- **Runnable Protocol 정본**: `D2.0-02 §1.2-A`
- **교차 도메인**: `3-6 Health-Wellness-EmotionAI` LOCK-HW-01/02/03/04/05/06/09/12 (HIGH 연동) / `6-2 Security-Governance` / `6-12 Event-Logging` (COND_098_*)

---

## §1 개요

### 1.1 목적
일일 감정 기록, 감정 패턴 시각화, 트리거 식별, 감정 추세 분석을 수행한다. 인지행동치료(CBT) 프레임워크 기반 리프레이밍 제안을 생성한다. 고위험 감정 표지(자살사고·자해·극심한 우울 등) 감지 시 위기 대응 프로토콜을 가동한다.

### 1.2 핵심 기술
- **Sentiment Analysis**: Transformer 기반 한/영 감정 분류 (accuracy ≥ 0.82, LOCK-HW-10 VBS-17 기준)
- **Emotion Classification**: LOCK-HW-01 7 기본 감정 (기쁨/슬픔/분노/불안/놀람/혐오/중립) + 5 세부 (피로/스트레스/좌절/열정/호기심) + 2 차원 (arousal, valence) **verbatim 준수**
- **CBT Framework**: 15 인지 왜곡 유형 (재앙화·흑백사고·개인화·당위적 사고·감정적 추론 등, LOCK-V12-05 원본) 탐지 → 리프레이밍
- **Mood Tracking Visualization**: 시계열 + spiderweb + heatmap
- **위기 감지**: 키워드 + 문맥 + 강도 복합 스코어 (LOCK-HW-05 위기 전화번호 자동 안내)

### 1.3 ⚠️ Medical Disclaimer (LOCK-HW-04 verbatim + 필수 재인용)
> ⚠️ **Medical Disclaimer**: VAMOS는 의료 서비스가 아닙니다. 본 모듈의 감정 분석과 CBT 리프레이밍 제안은 건강 참고용이며 의학적 진단·치료·처방이 아닙니다. 우울증·불안장애·PTSD 등 정신건강 질환은 반드시 정신건강의학과 전문의 또는 임상심리사와 상담하십시오. **자살 사고·자해 욕구가 있을 경우 즉시 자살예방상담전화 1393 (24시간) 또는 정신건강위기상담전화 1577-0199 (LOCK-HW-05)로 연락하십시오.** 본 모듈 실행 전 사용자는 opt-in 동의 플로우를 완료해야 합니다.

### 1.4 ⚠️ Privacy Policy 요약 (§7.4 L866~L876 필수 게이트) — HIGH 민감도
- **수집 필드**: `JournalEntry.text` (자유 텍스트), `mood_rating` (1-10, LOCK-HW-12 척도 준수), `tags`, `cognitive_distortions_detected` — **감정 일지 텍스트는 LOCK-HW-02 PRIVATE 등급 (로컬 전용, 외부 전송 절대 금지)**
- **처리 목적**: 감정 패턴 분석 + CBT 리프레이밍 제안 + 위기 감지. 광고 / 제3자 공유 / AI 모델 훈련 데이터 전용 사용 **절대 금지**
- **보존 기간**: 일지 원문 **365일 (기본)** (감정 장기 추세 분석 필요성 정당성). 고위험 표지 감지 시 72h 내 관리자 검토 트리거 (자동 하드 삭제 유예 — 안전 우선, LOCK-HW-05 위기 대응 규정)
- **삭제 정책**: GDPR Right to Erasure — 사용자 요청 시 72시간 내 하드 삭제. 단 고위험 감지 이력은 법적 요구 시 **암호화된 의료 보관 7년** (한국 의료법 준용, 사용자 사전 동의 필수)
- **암호화**: at-rest **AES-256-GCM + KMS envelope encryption + 별도 PIN** (LOCK-HW-02 PRIVATE 등급 강화), in-transit **TLS 1.3**

### 1.5 §A.1 A↔F 양방향 실체화 결정 (세션 2-1 COND-091 §6.4 응답)
- **종합계획서 §A.1 L1137**: `CAT-A (AI/ML) ←── CAT-F (Wellbeing)` (F→A 방향, "F가 A의 감정 분석 활용")
- **§A.2 L1209**: `COND-025 (감정패턴 학습, A) → COND-098 (감정 일지, F)` (A→F 방향, "감정 데이터 입력, Phase 2")
- **본 세션 결정 (옵션 a 실체화)**: COND-025 (CAT-A 감정패턴 학습)의 추론 결과(감정 분류 + arousal/valence)를 COND-098 이 **CONSUMES** 한다. 역방향으로 COND-098 의 정제된 일지 데이터는 **opt-in 사용자 명시 동의 시에만** COND-025 훈련 소스로 **NOTIFIES** 된다 (LOCK-HW-01 감정 분류 모델 정본 보호, §6.1 명시).
- **경로 구현**: §6.1 "내부 의존 — COND-025 CONSUMES (CAT-A 감정 분류 추론 입력)" + §6.2 "COND-025 NOTIFIES (opt-in 시)" 양 방향 등재

### 1.6 LOCK 준수 요약
| LOCK | 준수 내용 |
|---|---|
| LOCK-CD-01 | COND-098 체계 준수 |
| LOCK-CD-03 | BaseModule ABC 4 메서드 구현 |
| LOCK-CD-04 | Runnable 프로토콜 |
| LOCK-CD-05 | Result<T, VamosError> 반환 |
| LOCK-CD-06 | VamosError 4필드 필수 |
| LOCK-CD-08 | Wellness Node P2 세션별 승인 |
| LOCK-CD-10 | ModuleConfig 5필드 |

---

## §2 Input Schema (Pydantic v2) — §13.1 #1

```python
from pydantic import BaseModel, Field, field_validator
from typing import Literal
from datetime import datetime

class JournalEntry(BaseModel):
    """감정 일지 항목. text 는 LOCK-HW-02 PRIVATE 로컬 전용."""
    entry_id: str = Field(..., min_length=1, max_length=64)
    logged_at: datetime
    text: str = Field(..., min_length=1, max_length=5000, description="일지 원문 (PRIVATE)")
    mood_rating: int = Field(..., ge=1, le=10, description="감정 강도 1-10 (LOCK-HW-12 정본 척도)")
    tags: list[str] = Field(default_factory=list)
    context_metadata: dict[str, str] = Field(
        default_factory=dict, description="예: {location: 'home', activity: 'work'}"
    )

    @field_validator("tags")
    @classmethod
    def sanitize_tags(cls, v: list[str]) -> list[str]:
        return [t.lower().strip() for t in v if t.strip()][:20]

class TimeRange(BaseModel):
    start: datetime
    end: datetime

    @field_validator("end")
    @classmethod
    def end_after_start(cls, v: datetime, info) -> datetime:
        start = info.data.get("start")
        if start and v <= start:
            raise ValueError("end must be after start")
        return v

class EmotionJournalInput(BaseModel):
    """COND-098 실행 입력. 종합명세 §#98 계약 준수."""
    user_id_hashed: str = Field(..., min_length=16, max_length=128)
    journal_entries: list[JournalEntry] = Field(..., min_length=1, max_length=500)
    analysis_period: TimeRange
    consent_flags: dict[
        Literal["sentiment_analysis", "cbt_reframing", "cond_025_train_sink", "crisis_protocol"],
        bool,
    ] = Field(default_factory=dict)
```

### 2.1 예시
```json
{
  "user_id_hashed": "SHA256:d5e6...abcd",
  "journal_entries": [
    {
      "entry_id": "JE-2026-04-18-1",
      "logged_at": "2026-04-18T22:15:00",
      "text": "오늘 업무 발표가 떨렸지만 끝까지 해냈다. 긴장했지만 만족.",
      "mood_rating": 7,
      "tags": ["work", "achievement", "anxiety"],
      "context_metadata": {"location": "office"}
    }
  ],
  "analysis_period": {"start": "2026-04-12T00:00:00Z", "end": "2026-04-19T00:00:00Z"},
  "consent_flags": {
    "sentiment_analysis": true, "cbt_reframing": true,
    "cond_025_train_sink": false, "crisis_protocol": true
  }
}
```

---

## §3 Output Schema (Pydantic v2) — §13.1 #2

```python
from pydantic import BaseModel, Field
from typing import Literal

class EmotionLabel(BaseModel):
    """LOCK-HW-01 감정 분류 모델 7+5+2 verbatim 준수."""
    primary: Literal["기쁨","슬픔","분노","불안","놀람","혐오","중립"]
    secondary: Literal["피로","스트레스","좌절","열정","호기심"] | None = None
    arousal: float = Field(..., ge=-1.0, le=1.0)
    valence: float = Field(..., ge=-1.0, le=1.0)
    intensity: int = Field(..., ge=1, le=10, description="LOCK-HW-12")

class CognitiveDistortion(BaseModel):
    distortion_id: str
    distortion_type: Literal[
        "재앙화","흑백사고","개인화","당위적사고","감정적추론","낙인찍기",
        "긍정축소","과잉일반화","선택적주의","독심술","점술","부정편향",
        "통제오류","공정성오류","비난"
    ]
    evidence_snippet: str = Field(..., max_length=300)
    confidence: float = Field(..., ge=0.0, le=1.0)

class MoodAnalysis(BaseModel):
    period: str
    trend: Literal["improving", "stable", "declining", "volatile"]
    avg_arousal: float
    avg_valence: float
    avg_intensity: float
    distribution: dict[str, float] = Field(..., description="emotion → ratio")
    triggers: list[str] = Field(default_factory=list)
    patterns: list[str] = Field(default_factory=list)
    crisis_score: float = Field(..., ge=0.0, le=1.0)

class CBTExercise(BaseModel):
    exercise_id: str
    technique: Literal["cognitive_restructuring", "thought_record", "behavioral_activation",
                        "grounding", "breathing", "reframing"]
    target_distortion: str | None = None
    instruction: str
    expected_duration_min: int

class EmotionJournalOutput(BaseModel):
    analysis_id: str
    mood_analysis: MoodAnalysis
    cbt_suggestions: list[CBTExercise] = Field(..., min_length=0, max_length=10)
    distortions: list[CognitiveDistortion] = Field(default_factory=list)
    crisis_alert: dict | None = Field(
        default=None,
        description="crisis_score >= 0.7 시 { numbers: [1393, 1577-0199], immediate_actions: [...] }"
    )
    pii_removed: bool
    medical_disclaimer_shown: bool
    retention_expires_at: datetime
```

### 3.1 예시
```json
{
  "analysis_id": "EA-2026-04-19-d5e6",
  "mood_analysis": {
    "period": "2026-04-12/2026-04-19",
    "trend": "improving",
    "avg_arousal": 0.2, "avg_valence": 0.4, "avg_intensity": 6.2,
    "distribution": {"기쁨": 0.35, "불안": 0.20, "중립": 0.30, "스트레스": 0.15},
    "triggers": ["work-deadline", "sleep-deficit"],
    "patterns": ["morning_anxiety_weekday"],
    "crisis_score": 0.08
  },
  "cbt_suggestions": [
    {"exercise_id": "CBT-1", "technique": "cognitive_restructuring",
     "target_distortion": "재앙화", "instruction": "...", "expected_duration_min": 10}
  ],
  "distortions": [
    {"distortion_id": "CD-1", "distortion_type": "재앙화",
     "evidence_snippet": "...", "confidence": 0.78}
  ],
  "crisis_alert": null,
  "pii_removed": true,
  "medical_disclaimer_shown": true,
  "retention_expires_at": "2027-04-19T00:00:00Z"
}
```

---

## §4 Algorithm Pseudocode — §13.1 #3

### 4.1 전체 흐름
```
ALGORITHM EmotionJournal(input: EmotionJournalInput) -> Result<Output, VamosError>:
    # 1. Consent gate
    IF NOT input.consent_flags.get("sentiment_analysis", False) THEN
        RETURN Err(VamosError("COND_098_CONSENT_MISSING", ...))

    # 2. PII 마스킹 (journal text 의 이름/전화번호/주소 자동 익명화)
    anonymized_entries = pii_mask_text_pipeline(input.journal_entries)
    VALIDATE no_raw_pii(anonymized_entries)

    # 3. CAT-A COND-025 감정 분류 추론 (A→F 경로 실체화)
    emotion_labels = []
    FOR entry IN anonymized_entries:
        # CONSUMES: COND-025 inference API
        result = COND_025_client.infer(text=entry.text, return_labels=True)
        emotion_labels.append(EmotionLabel(
            primary=result.primary,     # LOCK-HW-01 7 기본 verbatim
            secondary=result.secondary, # LOCK-HW-01 5 세부 verbatim
            arousal=result.arousal, valence=result.valence,
            intensity=entry.mood_rating,  # LOCK-HW-12 1-10
        ))

    # 4. CBT 인지 왜곡 탐지 (LOCK-V12-05 15 유형 verbatim)
    distortions = []
    FOR label, entry IN zip(emotion_labels, anonymized_entries):
        IF label.valence < -0.3:
            for distortion_type IN CBT_DISTORTION_PATTERNS:
                IF pattern_match(entry.text, distortion_type):
                    distortions.append(CognitiveDistortion(
                        distortion_type=distortion_type,
                        evidence_snippet=mask_pii(snippet),
                        confidence=match_confidence,
                    ))

    # 5. 위기 감지 (LOCK-HW-05 자살예방 1393)
    IF input.consent_flags.get("crisis_protocol", False):
        crisis_score = compute_crisis_score(
            emotion_labels=emotion_labels,
            texts=anonymized_entries.texts,  # 키워드: 자살/자해/죽고싶/포기 등
            recent_window_days=7,
        )
    ELSE:
        crisis_score = 0.0
    crisis_alert = None
    IF crisis_score >= 0.7:
        crisis_alert = {
            "numbers": ["1393", "1577-0199"],  # LOCK-HW-05 verbatim
            "immediate_actions": ["전문 상담사 연결 제안", "응급 연락처 확인", "안전 계획 안내"],
            "severity": "HIGH" if crisis_score >= 0.85 else "MEDIUM",
        }
        # 72h 내 관리자 검토 트리거 (§1.4)
        emit_event("COND_098_CRISIS_DETECTED", severity="ERROR")

    # 6. 트렌드 분석 (시계열)
    trend = detect_trend(emotion_labels, window=7)  # improving/stable/declining/volatile
    triggers = extract_triggers(distortions, context_metadata=entries)
    patterns = detect_patterns(emotion_labels, logged_at)

    # 7. CBT 권고 생성 (distortions 당 1~2개)
    cbt_suggestions = []
    FOR d IN distortions[:5]:
        cbt_suggestions.append(match_cbt_technique(d.distortion_type))
    IF crisis_score >= 0.4:
        cbt_suggestions.append(grounding_5_4_3_2_1_exercise())  # LOCK-HW-08 verbatim

    # 8. COND-025 훈련 sink (양방향 F→A, opt-in 시에만)
    IF input.consent_flags.get("cond_025_train_sink", False):
        COND_025_sink.notify(anonymized_entries, emotion_labels)

    # 9. Output 조립 + retention
    expires_at = now() + timedelta(days=365)

    RETURN Ok(EmotionJournalOutput(
        analysis_id=uuid4(),
        mood_analysis=MoodAnalysis(period, trend, avg_arousal, avg_valence, avg_intensity,
                                    distribution, triggers, patterns, crisis_score),
        cbt_suggestions=cbt_suggestions,
        distortions=distortions,
        crisis_alert=crisis_alert,
        pii_removed=True,
        medical_disclaimer_shown=True,
        retention_expires_at=expires_at,
    ))
```

### 4.2 시간 복잡도
- **PII 마스킹**: `O(N · L)` (N=entries, L=text length)
- **COND-025 inference**: `O(N · T(ModelCall))` — 외부 API 호출 N회, T ≈ 150ms
- **CBT 탐지**: `O(N · |patterns|)` — 15 유형 × N
- **위기 감지**: `O(N)` (키워드 + 임베딩 거리)
- **전체**: `O(N · (L + |패턴| + T(API)))`; 실측 상한 N=10 → p99 ≤ 1800ms
- **LOCK 값 참조**: LOCK-CD-11 V2 ₩93K — COND-025 API 비용 주 지배 (entry 당 ~₩0.2)

### 4.3 LOCK-HW-01 감정 분류 모델 verbatim (7+5+2)
```
기본 7 (LOCK-HW-01 정본): 기쁨, 슬픔, 분노, 불안, 놀람, 혐오, 중립
세부 5 (LOCK-HW-01 정본): 피로, 스트레스, 좌절, 열정, 호기심 (지루함 제외 — §9.2 #1 판정 결과)
차원 2 (LOCK-HW-01 정본): arousal ∈ [-1, 1], valence ∈ [-1, 1]
```

### 4.4 위기 감지 스코어 가중합
```
crisis_score = 0.4 * keyword_score(자살/자해/죽고싶)
             + 0.3 * intensity_score(valence < -0.7 AND intensity >= 8)
             + 0.2 * persistence_score(negative 7일 연속)
             + 0.1 * distortion_score(재앙화 + 낙인찍기 동시)
임계값: 0.7 → crisis_alert 발행 + LOCK-HW-05 전화번호 안내
임계값: 0.85 → severity=HIGH + 즉시 관리자 alert (72h review trigger)
```

---

## §5 Error Handling — §13.1 #4 (LOCK-CD-05 / LOCK-CD-06)

### 5.1 FailureCode 체계
```python
COND_098_CONSENT_MISSING
COND_098_PII_LEAK_DETECTED
COND_098_COND_025_UNAVAILABLE
COND_098_CRISIS_PROTOCOL_FAIL       # 위기 감지되었으나 LOCK-HW-05 안내 실패
COND_098_CBT_RULE_ENGINE_FAIL
COND_098_RETENTION_POLICY_VIOLATION
COND_098_USER_NOT_FOUND
COND_098_MEDICAL_DISCLAIMER_FAIL
COND_098_ENCRYPTION_FAIL             # PRIVATE 등급 암호화 실패 → 즉시 fail-closed
```

### 5.2 Phase별 복구 전략
```
Phase 1 (Validation): Pydantic 자동 차단
Phase 2 (Consent gate): 재동의 플로우
Phase 3 (PII): fail-closed (절대 우회 불가, LOCK-HW-02 PRIVATE)
Phase 4 (COND-025 inference): 외부 API 실패 → VADER/TextBlob 단순 fallback
                                (arousal/valence만 근사, LOCK-HW-01 7감정 → 3감정 축소 허용, penalty × 0.6)
Phase 5 (CBT): 룰 엔진 실패 → generic self-help 안내 (CBT 미적용, confidence × 0.5)
Phase 6 (Crisis): crisis_score >= 0.7 이나 LOCK-HW-05 안내 실패 → fail-loud,
                   ERROR 로그 + 관리자 alert 이중 경로 (SMS + 이메일)
Phase 7 (Encryption): PRIVATE 암호화 실패 → fail-closed (데이터 저장 중단, 메모리 flush)
Phase 8 (Escalation): I-20 에스컬레이션 (text 배제)
```

### 5.3 Escalation Payload (text 절대 배제)
```python
class EscalationPayload(BaseModel):
    source_engine: str = "COND-098"
    error_code: str
    user_id_hashed: str
    crisis_score: float | None = None  # 숫자만, 내용 배제
    retry_count: int
    timestamp: datetime
    # journal text / emotion_labels / distortions 배제 (PRIVATE 원칙)
```

### 5.4 로깅 포맷 (R-01-7)
```json
{
  "trace_id": "trace-d5e6-...",
  "error": {"code": "COND_098_COND_025_UNAVAILABLE", "severity": "WARN"},
  "context": {"user_id_hashed": "SHA256:d5e6...", "module": "COND-098", "phase": "inference"},
  "recovery": {"strategy": "VADER_fallback", "confidence_penalty": 0.6, "fallback_id": "FB-COND098-VADER"}
}
```

---

## §6 Dependency Map — §13.1 #5

### 6.1 내부 의존 (CAT-F 내부) — §A.1 A↔F 양방향 실체화 반영
| 대상 | 방향 | 이유 |
|---|---|---|
| **COND-025 (CAT-A 감정패턴 학습)** | **CONSUMES** | **§A.2 L1209 A→F 경로 실체화 (세션 2-2 결정): 감정 분류 추론 입력 (LOCK-HW-01 정본 소비)** |
| COND-095 수면 개선 | REFERENCES | sleep_quality ↔ mood 상관 분석 |
| COND-100 건강 인사이트 | PROVIDES | 감정 축 공급 |
| COND-101 감정 음악 추천 | NOTIFIES | current_mood → 음악 추천 트리거 |
| COND-116 웰빙 대시보드 | PROVIDES | mood_trend 위젯 공급 |

### 6.2 외부 의존 (다른 CAT / 다른 도메인) — F→A 양방향 포함
| 대상 | 방향 | 이유 |
|---|---|---|
| **COND-025 (CAT-A ML)** | **NOTIFIES (opt-in)** | **§A.1 L1137 F→A 경로: cond_025_train_sink=True 시에만, LOCK-HW-01 훈련 소스 보강** |
| `3-6 Health-Wellness-EmotionAI` LOCK-HW-01 | CROSS-DOMAIN | 감정 분류 모델 7+5+2 verbatim 소비 (정본) |
| `3-6 Health-Wellness-EmotionAI` LOCK-HW-02 | CROSS-DOMAIN | PRIVATE 등급 로컬 전용 (강화 필드) |
| `3-6 Health-Wellness-EmotionAI` LOCK-HW-03 | CROSS-DOMAIN | 감정로그 retention 180일 (본 모듈은 365일 opt-in 연장) |
| `3-6 Health-Wellness-EmotionAI` LOCK-HW-04 | CROSS-DOMAIN | 비의료 면책 원문 재인용 |
| `3-6 Health-Wellness-EmotionAI` LOCK-HW-05 | CROSS-DOMAIN | **위기 전화번호 1393 / 1577-0199 verbatim 자동 안내 (§4.1 Phase 5)** |
| `3-6 Health-Wellness-EmotionAI` LOCK-HW-06 | CROSS-DOMAIN | AES-256-GCM + 별도 PIN |
| `3-6 Health-Wellness-EmotionAI` LOCK-HW-09 | CROSS-DOMAIN | 감정 AI 7원칙 (비진단·프라이버시·투명성·전문가연결·비조작·자율성·기능끄기) |
| `3-6 Health-Wellness-EmotionAI` LOCK-HW-12 | CROSS-DOMAIN | 감정 강도 1-10 정수 척도 verbatim |
| `#19 v12-Additions` LOCK-V12-05 | CROSS-DOMAIN | CBT 15 인지 왜곡 유형 verbatim |
| `6-2 Security-Governance` | CROSS-DOMAIN | PII 마스킹 (이름/주소/전화 자동 익명화) + GDPR + PRIVATE 등급 강화 |
| `6-12 Event-Logging` | CROSS-DOMAIN | COND_098_* FailureCode + 위기 이벤트 별도 분류 + 관리자 alert 경로 |

### 6.3 의존성 매트릭스 (CAT-F + CAT-A)
```
            025  095  096  097  098  099  100  101  116
COND-098  [  C    R    .    .    -    .    P    N    P ]  C=CONSUMES(A→F), N=NOTIFIES, P=PROVIDES, R=REFERENCES
[역방향]    [  N    -    -    -    -    -    -    -    - ]  N=NOTIFIES(F→A, opt-in)
```

### 6.4 §A 매트릭스 cross-check — §A.1 A↔F 양방향 **실체화 완료**
- **§A.1 L1137** `CAT-A (AI/ML) ←── CAT-F (Wellbeing)` (F→A, "F가 A의 감정 분석 활용") = 본 모듈 §6.1 CONSUMES (COND-025) 방향
- **§A.2 L1209** `COND-025 (감정패턴 학습, A) → COND-098 (감정 일지, F) | 감정 데이터 입력 | Phase 2` = 본 모듈 §6.1 CONSUMES 실체
- **§A.1 L1145 Phase 2 확인 사항** "§A.2의 COND-025(CAT-A) → COND-098(CAT-F)은 A→F 방향이나, §A.1은 F→A만 기재. 양방향 여부를 Phase 2 CAT-F 분석 시 확정할 것." → **본 세션 2-2 확정: 양방향 실존** (F→A = COND-025 CAT-A 모델 추론 소비 / F→A (역방향, opt-in 훈련 소스) = 본 모듈 §6.2 NOTIFIES)
- **세션 2-1 COND-091 §6.4 질의 응답**: "CAT-E↔CAT-F 교차 의존 현재 미발견" → **CAT-E 는 교차 없음 (맞음), CAT-A↔CAT-F 는 본 모듈에서 양방향 실체화 완료**

### 6.5 Phase 1 deferral 인계
- 본 모듈은 신규 deferral 생성 없음 (§A.1 A↔F 경로 양방향 실체화 완료, CONFLICT_LOG 신규 등재 불요)

---

## §7 Performance Benchmark — §13.1 #6

### 7.1 SLA 기준값
| 지표 | V1 기준 | V2 목표 | 측정 방법 |
|---|---|---|---|
| p50 응답 시간 | N/A | ≤ 450 ms (COND-025 API 주 지배) |
| p99 응답 시간 | N/A | ≤ 1,800 ms |
| 처리량 | N/A | ≥ 60 req/s |
| 감정 분류 정확도 | N/A | ≥ 0.82 F1 (LOCK-HW-10 VBS-17) |
| 위기 감지 Recall | N/A | ≥ 0.95 @ precision ≥ 0.7 | vs. 전문가 라벨 |
| PII 마스킹 성공률 | N/A | 100% fail-closed |

### 7.2 비용 상한 참조 (LOCK-CD-11)
- V2 ₩93K 한도. COND-025 API 호출 entry 당 ~₩0.2 → 월 추정 ₩15K (30k entries/월)
- 365일 retention + 7년 의료 보관 대상 시 스토리지 ₩3K/사용자/년

### 7.3 벤치마크 시나리오
```
BENCH-098-01: 10 entries × COND-025 inference × 500회 → p50/p99
BENCH-098-02: 위기 키워드 주입 (합성) → crisis_alert 발행 지연 측정
BENCH-098-03: COND-025 API 장애 → VADER fallback 성능 측정
BENCH-098-04: PII 마스킹 성능 (고밀도 PII 텍스트 100 entries)
```

---

## §8 Integration Test Spec (I-05) — §13.1 #7 (≥ 3 + ⚠️ 프라이버시 침해 필수 + 위기 시나리오)

### 8.1 I-05-COND098-01: 정상 감정 분석 + CBT 권고
- **목적**: 7일 일지 14 entries + consent_flags 완비 시 정상 분석
- **주입**: `journal_entries.length = 14`, `consent_flags = {sentiment_analysis: true, cbt_reframing: true, crisis_protocol: true}`
- **기대**:
  - `Result.is_ok() == True`
  - `mood_analysis.trend in {"improving", "stable", "declining", "volatile"}`
  - `cbt_suggestions.length >= 1` (최소 1개)
  - `crisis_alert == None` (일반 프로필)
  - `pii_removed == True`, `medical_disclaimer_shown == True`
- **목 데이터**: `mocks/COND-098/happy_path_user_A.json`

### 8.2 I-05-COND098-02: ⚠️ 프라이버시 침해 — sentiment_analysis 동의 없이 제출 (필수)
- **목적**: `consent_flags.sentiment_analysis=False` 상태에서 journal_entries 제출
- **기대**:
  - `Result.is_err()`, `failure_code == "COND_098_CONSENT_MISSING"`
  - **journal text 0% 응답/로그 노출 확인** (fail-closed)
  - UI 동의 플로우 재안내
- **목 데이터**: `mocks/COND-098/privacy_sentiment_no_consent.json`

### 8.3 I-05-COND098-03: 위기 감지 → LOCK-HW-05 전화번호 자동 안내
- **목적**: 자살 사고 표현 포함 일지 주입 시 crisis_alert 발행 + 1393/1577-0199 안내
- **주입**: "요즘 너무 힘들어 사라지고 싶어" 류 문장 포함 entries
- **기대**:
  - `Result.is_ok() == True` (분석은 계속, fail-loud 아님)
  - `crisis_alert != None`
  - `crisis_alert.numbers == ["1393", "1577-0199"]` (LOCK-HW-05 verbatim)
  - `crisis_alert.severity in {"MEDIUM", "HIGH"}`
  - 6-12 `COND_098_CRISIS_DETECTED` ERROR 이벤트 발행 + 관리자 alert
- **목 데이터**: `mocks/COND-098/crisis_suicide_ideation.json`

### 8.4 I-05-COND098-04 (추가): §A.1 A↔F 양방향 실체화 검증
- **목적**: COND-025 API 호출 + opt-in 시 F→A 훈련 sink 동작 확인
- **주입**: `consent_flags.cond_025_train_sink=True`, 10 entries
- **기대**:
  - A→F: `emotion_labels` 전수 LOCK-HW-01 7 기본 verbatim 범위 내
  - F→A: 익명화된 entries → COND-025 sink notify 호출 확인 (event `COND_098_COND_025_SINK_NOTIFIED`)
- **목 데이터**: `mocks/COND-098/bidirectional_a_f.json`

### 8.5 Phase 3 시나리오 확장 (≥ 5 시나리오)
| ID | 제목 | 주입 | 기대 |
|---|---|---|---|
| 098-S5 | COND-025 API 장애 | inference stub 503 | VADER fallback + confidence × 0.6 |
| 098-S6 | PRIVATE 암호화 장애 | KMS fail | `COND_098_ENCRYPTION_FAIL` fail-closed |
| 098-S7 | 365일 Retention 초과 | old entries | `COND_098_RETENTION_POLICY_VIOLATION` + 자동 폐기 |
| 098-S8 | 고위험 표지 검토 트리거 | crisis_score ≥ 0.85 | 72h 관리자 검토 trigger + ERROR 로그 |
| 098-S9 | Right to Erasure (의료 보관 예외) | delete_user + crisis_history 있음 | 사용자 대면 삭제 완료 + 의료 보관 7년 유지 공지 |
| 098-S10 | Trace 전파 | `trace_id=T-xxx` | 일치 |
| 098-S11 | 인지 왜곡 15 유형 커버리지 | 15 유형 각 주입 | 모두 탐지 가능 (LOCK-V12-05 verbatim) |
| 098-S12 | 위기 안내 실패 | SMS/이메일 게이트웨이 장애 | `COND_098_CRISIS_PROTOCOL_FAIL` ERROR + 이중 경로 재시도 |

---

## §9 Blue Node Integration (LOCK-CD-04 / LOCK-CD-08) — §13.1 #8

### 9.1 Blue Node 소비 계약
- **Wellness Node** / **P2 (세션별 승인)** / 독립 실행 금지
- **LOCK-HW-09 감정 AI 7원칙 준수**: 비진단·프라이버시·투명성·전문가연결·비조작·자율성·기능끄기

### 9.2 Runnable 프로토콜
```python
class EmotionJournal(BaseModule, Runnable):
    def initialize(self, config: ModuleConfig) -> None: ...
    def execute(self, input: EmotionJournalInput) -> Result[EmotionJournalOutput, VamosError]: ...
    def run(self, input: EmotionJournalInput) -> Result[EmotionJournalOutput, VamosError]: ...
    def health_check(self) -> HealthStatus: ...
    def get_metadata(self) -> ModuleMetadata: ...
    def shutdown(self) -> None: ...
```

### 9.3 ModuleConfig (LOCK-CD-10)
```python
config = ModuleConfig(
    enabled=True,
    priority=1,  # HIGH priority — 위기 감지 우선
    max_concurrent=12,
    timeout_ms=3500,
    retry_policy=RetryPolicy(max_retries=2, backoff="exponential"),
)
```

### 9.4 Permission Level
```
P2: Wellness Node 세션별 opt-in + PIN 입력 활성 (LOCK-HW-02 PRIVATE 강화)
P0: 관리자 전용 (crisis 검토 큐 접근, 의료 보관 7년 대상 관리)
```

### 9.5 Blue Node Event (6-12 Event-Logging 연동)
```
COND_098_ANALYSIS_COMPLETED      INFO    user_id_hashed, analysis_id, trend (데이터 배제)
COND_098_CRISIS_DETECTED          ERROR   user_id_hashed, crisis_score, severity (text 배제, 관리자 alert 트리거)
COND_098_CRISIS_PROTOCOL_FAIL     ERROR   user_id_hashed, gateway_error (이중 경로 재시도)
COND_098_COND_025_SINK_NOTIFIED   INFO    user_id_hashed, batch_size (opt-in 시만)
COND_098_PII_LEAK_DETECTED        ERROR   user_id_hashed, context (fail-closed)
COND_098_ENCRYPTION_FAIL          ERROR   kms_error_code (PRIVATE 등급 즉시 fail-closed)
```

---

## §10 V2-Phase 2 변경 이력

| 버전 | 일자 | 변경 요약 | 근거 |
|---|---|---|---|
| V1 | 2026-03-22 | 초기 골격 (SHELL L1) | Phase 1 산출 이전 |
| V2 | 2026-04-19 | L3 상세 + Privacy PRIVATE 강화 + Medical Disclaimer + 위기 감지 LOCK-HW-05 + §A.1 A↔F 양방향 실체화 + LOCK-HW-01/02/03/04/05/06/09/12 cross-domain | STAGE 7 Phase 7-II 2-2 STEP_B 세션 2-2 |

### 10.1 Pydantic 재사용 출처
- `ModuleConfig` 재사용: `common_types.md §3.4` (LOCK-CD-10 정본)
- `VamosError` 재사용: `D2.0-02 §0.3` (LOCK-CD-06 정본)
- `Result[T, E]` 재사용: `D2.0-02 §0.3` (LOCK-CD-05 정본)

---

**[END OF COND-098 V2]** — L3 8 항목 전수 + CAT-F 특수 게이트 전수 + **§A.1 A↔F 양방향 경로 실체화 (A→F CONSUMES COND-025 / F→A NOTIFIES opt-in sink) 완료 — 세션 2-1 COND-091 §6.4 질의 응답**. LOCK-CD-01/03/04/05/06/08/10 + LOCK-HW-01/02/03/04/05/06/09/12 + LOCK-V12-05 CBT 15 유형 cross-domain. I-05 12 시나리오 (핵심 4 + 프라이버시 침해 1 필수 + 위기 감지 1 + 확장 7). HIGH 우선순위 — 위기 감지 시 LOCK-HW-05 전화번호 1393/1577-0199 verbatim 자동 안내. PRIVATE 등급 로컬 전용 + 별도 PIN + 암호화 fail-closed.
