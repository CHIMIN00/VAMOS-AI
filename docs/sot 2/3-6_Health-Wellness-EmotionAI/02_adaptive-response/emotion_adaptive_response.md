# emotion_adaptive_response.md — 감정 적응 응답 시스템

> **P-ID**: P-002, P-002-a, P-002-b
> **V단계**: V1
> **상태**: P-002 EXTEND / P-002-a EXTEND / P-002-b NEW
> **L3 완성**: 2026-04-10
> **정본 소유자**: sot 2/3-6_Health-Wellness-EmotionAI/02_adaptive-response/

---

## 교차 참조 블록

| 참조 문서 | 위치 | 참조 내용 |
|----------|------|----------|
| 종합계획서 §3.4 | LOCK-HW-01/09 | 감정 분류 모델 7+5+2, 감정 AI 7원칙 |
| 종합계획서 §6.2 | 매핑 테이블 8항목 | P-002/P-002-a/P-002-b 배정 |
| 종합계획서 §4 | R-09-1~R-09-7 | 도메인 전용 거버넌스 규칙 |
| 상세명세 §3.1 | EmotionAdaptiveResponder | 감정 기반 응답 조절 기존 명세 (레거시 참조) |
| STEP7-P | P-002 | 감정 적응형 응답 원본 체크리스트 |
| AUTHORITY_CHAIN.md | §1~§5 | 정본 계층 및 충돌 해결 |
| 01_emotion-recognition/text_emotion_analysis.md | §7 인터페이스 | TextEmotionResult 입력 소스 |
| 06_ethics-privacy/ethics_framework.md | §3 7원칙 | 비조작 원칙 적용 |
| 05_emotion-journal/ | emotion_journal_trend.md | 적응 응답 이력 → 일지 기록 |

---

## 1. 개요

본 문서는 VAMOS 감정 적응 응답 시스템을 L3 구현 즉시 투입 가능 수준으로 정의한다. 01_emotion-recognition의 TextEmotionResult를 입력으로 받아, 감정 분류 모델(LOCK-HW-01: 7+5+2)에 따른 톤/스타일 자동 전환 매트릭스를 적용하고, LLM 프롬프트를 동적으로 조정하여 사용자 감정에 공감하는 응답을 생성한다. 모든 응답 생성 과정에서 7원칙(LOCK-HW-09) 중 "비조작" 원칙을 필수 준수한다.

**입력**: `TextEmotionResult` (01_emotion-recognition 출력)
**출력**: `AdaptedResponse { text, tone_applied, style_applied, manipulation_check_passed }`

---

## 2. LOCK 인용

> LOCK (LOCK-HW-01, 기존 명세 §2/STEP7-P P-001): 기본7(기쁨,슬픔,분노,불안,놀람,혐오,중립)+세부5(피로,스트레스,좌절,열정,호기심)+차원2(arousal,valence)

> LOCK (LOCK-HW-09, STEP7-P P-010): 비진단/프라이버시/투명성/전문가연결/비조작/자율성/기능끄기

---

## 3. 톤/스타일 전환 매트릭스 (P-002-a)

### 3.1 기본 7감정 톤/스타일 매핑

> LOCK-HW-01 적용 — PRIMARY 7감정 × 톤 파라미터

| # | 감정 | tone | style | emoji_level | verbosity | avoid |
|---|------|------|-------|-------------|-----------|-------|
| 1 | 기쁨 | 밝고 에너지 넘치는 | 축하/격려, 긍정 에너지 증폭 | moderate | normal | - |
| 2 | 슬픔 | 따뜻하고 공감적인 | 감정 인정, 경청, 위로 | minimal | concise | 긍정 강요, 비교, 조언 즉시 제공 |
| 3 | 분노 | 차분하고 이해하는 | 감정 인정, 상황 정리 도움 | none | concise | 반박, 축소, 훈계 |
| 4 | 불안 | 안정적이고 구조화된 | 사실 기반 정보, 단계별 안내, 안전감 제공 | minimal | structured | - |
| 5 | 놀람 | 호기심을 존중하는 | 상황 파악 도움, 정보 제공 | minimal | normal | - |
| 6 | 혐오 | 중립적이고 이해하는 | 감정 인정, 거리두기 도움 | none | concise | 판단, 축소 |
| 7 | 중립 | 자연스럽고 전문적인 | 기본 대화 스타일 | minimal | normal | - |

### 3.2 세부 5감정 톤/스타일 매핑

> LOCK-HW-01 적용 — SECONDARY 5감정 × 톤 파라미터

| # | 감정 | tone | style | emoji_level | verbosity | avoid |
|---|------|------|-------|-------------|-----------|-------|
| 8 | 피로 | 부드럽고 배려하는 | 휴식 제안, 부담 줄이기, 간결한 응답 | none | concise | 활동 강요 |
| 9 | 스트레스 | 차분하고 체계적인 | 우선순위 정리, 스트레스 관리 도구 제안 | none | structured | 더 많은 할 일 제안 |
| 10 | 좌절 | 격려하고 공감하는 | 작은 성취 인정, 단계별 접근 제안 | minimal | concise | 긍정 강요, 비교 |
| 11 | 열정 | 에너지 넘치고 지지하는 | 동기 부여, 실행 계획 도움, 목표 구체화 | moderate | normal | 열정 꺾기 |
| 12 | 호기심 | 탐구적이고 정보 풍부한 | 상세 설명, 추가 자료 제공, 질문 유도 | minimal | detailed | 단답 |

### 3.3 강도 기반 톤 가중 조정

| intensity 범위 | 톤 강도 조정 | verbosity 오버라이드 | 추가 행동 |
|---------------|-------------|-------------------|----------|
| 1-3 | 기본 프로파일 그대로 | 변경 없음 | 일반 모니터링 |
| 4-6 | 톤 파라미터 강화 (공감 +20%) | 변경 없음 | 적응 응답 활성화 |
| 7-8 | 톤 파라미터 최대 (공감 +40%) | concise 강제 | 스트레스 관리 도구 제안 (04_stress-management) |
| 9-10 | 위기 모드 전환 | crisis 전용 | 위기 프로토콜 우선 (06_ethics-privacy) |

### 3.4 복합 감정 톤 결합 규칙

```
복합 감정 시 (primary + secondary 동시 존재):
1. primary 톤을 기본(base)으로 설정
2. secondary 톤의 style을 보조(supplement)로 추가
3. avoid 목록은 합집합(union) 적용
4. verbosity: primary 우선, 단 secondary가 concise이면 concise 채택
5. emoji_level: none이 하나라도 있으면 none

예시: primary=불안(structured), secondary=스트레스(structured)
  → tone: "안정적이고 체계적인", verbosity: structured, avoid: ["더 많은 할 일 제안"]
```

---

## 4. LLM 프롬프트 동적 조정 알고리즘 (P-002)

### 4.1 아키텍처

```
[TextEmotionResult 입력]
        │
        ▼
[1. 프로파일 조회 (Profile Lookup)]
        │  RESPONSE_PROFILES에서 primary/secondary 매칭
        ▼
[2. 톤 파라미터 구성 (Tone Composition)]
        │  강도 가중 + 복합 감정 결합
        ▼
[3. 비조작 검증 (Manipulation Check)]    ← LOCK-HW-09 "비조작"
        │  ManipulationGuard 통과 필수
        ▼
[4. 시스템 프롬프트 생성 (System Prompt)]
        │  감정 컨텍스트 + 톤 + 제약 조건
        ▼
[5. LLM 생성 (Adapted Response)]
        │  원본 응답 → 감정 적응 응답
        ▼
[6. 후처리 검증 (Post Validation)]
        │  비진단 필터 + 면책 검증
        ▼
[7. 출력: AdaptedResponse]
```

### 4.2 알고리즘 의사코드

```python
# emotion_adaptive_response_pipeline.py
# ABC 매핑: P-002(적응 응답), P-002-a(톤/스타일 매트릭스), P-002-b(응답 템플릿)

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


# ── 공통 자료 구조 (Pydantic/dataclass 형태 선정의) ──

class ToneLevel(str, Enum):
    """톤 강도 수준"""
    BASE = "base"           # intensity 1-3
    ENHANCED = "enhanced"   # intensity 4-6
    MAXIMUM = "maximum"     # intensity 7-8
    CRISIS = "crisis"       # intensity 9-10


class VerbosityLevel(str, Enum):
    """응답 상세도"""
    CONCISE = "concise"
    NORMAL = "normal"
    STRUCTURED = "structured"
    DETAILED = "detailed"
    CRISIS = "crisis"


class EmojiLevel(str, Enum):
    """이모지 사용 수준"""
    NONE = "none"
    MINIMAL = "minimal"
    MODERATE = "moderate"


@dataclass
class ToneProfile:
    """
    감정별 톤/스타일 프로파일.
    §3.1/§3.2 매핑 테이블의 데이터 구조.
    """
    emotion: str
    tone: str
    style: str
    emoji_level: EmojiLevel
    verbosity: VerbosityLevel
    avoid: list[str] = field(default_factory=list)


@dataclass
class ComposedTone:
    """
    복합 감정 결합 후 최종 톤 설정.
    """
    base_tone: str
    supplement_style: Optional[str]
    emoji_level: EmojiLevel
    verbosity: VerbosityLevel
    avoid: list[str]
    tone_level: ToneLevel
    empathy_boost: float  # 0.0 ~ 0.4


@dataclass
class ManipulationCheckResult:
    """
    비조작 원칙 검증 결과 (LOCK-HW-09).
    """
    passed: bool
    violations: list[str] = field(default_factory=list)
    confidence: float = 1.0  # 검증 신뢰도


@dataclass
class AdaptedResponse:
    """
    감정 적응 응답 최종 출력.
    세션 간 인터페이스: 05_emotion-journal에서 이력 기록 참조.
    """
    text: str
    tone_applied: str
    style_applied: str
    emotion_acknowledged: str
    intensity_at_generation: int
    manipulation_check_passed: bool
    disclaimer_included: bool        # LOCK-HW-04 비의료 면책


# ── LOCK-HW-01 기반 RESPONSE_PROFILES (상세명세 §3.1 EXTEND) ──

RESPONSE_PROFILES: dict[str, ToneProfile] = {
    # --- PRIMARY 7감정 ---
    "기쁨": ToneProfile(
        emotion="기쁨", tone="밝고 에너지 넘치는",
        style="축하/격려, 긍정 에너지 증폭",
        emoji_level=EmojiLevel.MODERATE, verbosity=VerbosityLevel.NORMAL
    ),
    "슬픔": ToneProfile(
        emotion="슬픔", tone="따뜻하고 공감적인",
        style="감정 인정, 경청, 위로",
        emoji_level=EmojiLevel.MINIMAL, verbosity=VerbosityLevel.CONCISE,
        avoid=["긍정 강요", "비교", "조언 즉시 제공"]
    ),
    "분노": ToneProfile(
        emotion="분노", tone="차분하고 이해하는",
        style="감정 인정, 상황 정리 도움",
        emoji_level=EmojiLevel.NONE, verbosity=VerbosityLevel.CONCISE,
        avoid=["반박", "축소", "훈계"]
    ),
    "불안": ToneProfile(
        emotion="불안", tone="안정적이고 구조화된",
        style="사실 기반 정보, 단계별 안내, 안전감 제공",
        emoji_level=EmojiLevel.MINIMAL, verbosity=VerbosityLevel.STRUCTURED
    ),
    "놀람": ToneProfile(
        emotion="놀람", tone="호기심을 존중하는",
        style="상황 파악 도움, 정보 제공",
        emoji_level=EmojiLevel.MINIMAL, verbosity=VerbosityLevel.NORMAL
    ),
    "혐오": ToneProfile(
        emotion="혐오", tone="중립적이고 이해하는",
        style="감정 인정, 거리두기 도움",
        emoji_level=EmojiLevel.NONE, verbosity=VerbosityLevel.CONCISE,
        avoid=["판단", "축소"]
    ),
    "중립": ToneProfile(
        emotion="중립", tone="자연스럽고 전문적인",
        style="기본 대화 스타일",
        emoji_level=EmojiLevel.MINIMAL, verbosity=VerbosityLevel.NORMAL
    ),
    # --- SECONDARY 5감정 ---
    "피로": ToneProfile(
        emotion="피로", tone="부드럽고 배려하는",
        style="휴식 제안, 부담 줄이기, 간결한 응답",
        emoji_level=EmojiLevel.NONE, verbosity=VerbosityLevel.CONCISE,
        avoid=["활동 강요"]
    ),
    "스트레스": ToneProfile(
        emotion="스트레스", tone="차분하고 체계적인",
        style="우선순위 정리, 스트레스 관리 도구 제안",
        emoji_level=EmojiLevel.NONE, verbosity=VerbosityLevel.STRUCTURED,
        avoid=["더 많은 할 일 제안"]
    ),
    "좌절": ToneProfile(
        emotion="좌절", tone="격려하고 공감하는",
        style="작은 성취 인정, 단계별 접근 제안",
        emoji_level=EmojiLevel.MINIMAL, verbosity=VerbosityLevel.CONCISE,
        avoid=["긍정 강요", "비교"]
    ),
    "열정": ToneProfile(
        emotion="열정", tone="에너지 넘치고 지지하는",
        style="동기 부여, 실행 계획 도움, 목표 구체화",
        emoji_level=EmojiLevel.MODERATE, verbosity=VerbosityLevel.NORMAL,
        avoid=["열정 꺾기"]
    ),
    "호기심": ToneProfile(
        emotion="호기심", tone="탐구적이고 정보 풍부한",
        style="상세 설명, 추가 자료 제공, 질문 유도",
        emoji_level=EmojiLevel.MINIMAL, verbosity=VerbosityLevel.DETAILED,
        avoid=["단답"]
    ),
}


# ── 비조작 원칙 검증 (LOCK-HW-09) ──

# 조작 의도 감지 키워드/패턴 (R-09-7)
MANIPULATION_PATTERNS: list[str] = [
    "구매를 유도",
    "결제를 권유",
    "행동을 강요",
    "감정을 이용",
    "불안을 조장",
    "두려움을 자극",
    "FOMO 유발",
    "즉시 결정하세요",
    "지금 아니면 늦습니다",
]


class ManipulationGuard:
    """
    LOCK-HW-09 "비조작" 원칙 준수 검증기.

    모든 적응 응답 생성 전후에 검증을 수행한다.
    감정 상태를 이용한 구매/행동 유도를 차단한다 (R-09-7).

    시간복잡도: O(m * p) — m = 응답 텍스트 길이, p = 패턴 수 (고정 ~10)
    공간복잡도: O(1)

    ABC 매핑: P-002 (비조작 검증 서브 컴포넌트)
    """

    def check_pre_generation(
        self,
        system_prompt: str,
        emotion: str,
        intensity: int
    ) -> ManipulationCheckResult:
        """
        LLM 생성 전 시스템 프롬프트 검증.
        - 감정을 이용한 행동 유도 프롬프트 패턴 차단
        - 고강도 감정(>=7) 시 추가 제약 적용

        Returns:
            ManipulationCheckResult: 검증 통과 여부 + 위반 목록
        """
        violations: list[str] = []

        # 패턴 매칭 검사
        for pattern in MANIPULATION_PATTERNS:
            if pattern in system_prompt:
                violations.append(f"조작 패턴 감지: '{pattern}'")

        # 고강도 감정 시 추가 제약
        if intensity >= 7:
            if "추천" in system_prompt and "구매" in system_prompt:
                violations.append("고강도 감정 상태에서 구매 추천 시도")

        return ManipulationCheckResult(
            passed=len(violations) == 0,
            violations=violations
        )

    def check_post_generation(
        self,
        response_text: str,
        emotion: str,
        intensity: int
    ) -> ManipulationCheckResult:
        """
        LLM 생성 후 응답 텍스트 검증.
        - 생성된 응답에 조작 의도 패턴이 포함되었는지 확인
        - 감정 명시적 언급 여부 확인 (사용자가 감시당한다고 느끼지 않도록)

        Returns:
            ManipulationCheckResult: 검증 통과 여부 + 위반 목록
        """
        violations: list[str] = []

        # 패턴 매칭 검사
        for pattern in MANIPULATION_PATTERNS:
            if pattern in response_text:
                violations.append(f"응답에 조작 패턴 포함: '{pattern}'")

        # 감정 명시적 언급 검사 (비투명성이 아닌 자연스러움 목적)
        explicit_emotion_phrases = [
            f"지금 {emotion}이시",
            f"지금 {emotion}하시",
            f"{emotion} 상태이시",
            f"당신의 {emotion}",
        ]
        for phrase in explicit_emotion_phrases:
            if phrase in response_text:
                violations.append(
                    f"감정 명시적 언급: '{phrase}' — 자연스러운 응답 권장"
                )

        return ManipulationCheckResult(
            passed=len(violations) == 0,
            violations=violations,
            confidence=0.85 if intensity >= 7 else 1.0
        )


class EmotionAdaptiveResponsePipeline:
    """
    감정 적응 응답 생성 파이프라인.

    TextEmotionResult를 입력으로 받아, 톤/스타일을 조정한 응답을 생성한다.
    모든 생성 과정에서 LOCK-HW-09 비조작 원칙을 검증한다.

    시간복잡도:
        - 프로파일 조회: O(1) — dict 조회
        - 톤 구성: O(a) — a = avoid 목록 길이 (최대 ~5)
        - 비조작 검증: O(m * p) — m = 텍스트 길이, p = 패턴 수
        - LLM 생성: O(LLM) — 외부 의존
        - 후처리: O(m * p)
        총: O(LLM) 지배적

    공간복잡도: O(m) — 응답 텍스트

    LOCK 참조:
        - LOCK-HW-01: 12감정 프로파일 키 매칭
        - LOCK-HW-09: 비조작 원칙 검증 (7원칙 중 5번째)

    ABC 매핑:
        - P-002: adapt_response() (LLM 프롬프트 동적 조정)
        - P-002-a: _compose_tone() (톤/스타일 매트릭스 적용)
        - P-002-b: _build_system_prompt() (감정별 응답 템플릿)
    """

    def __init__(self):
        self._llm = None  # LLM 클라이언트 (외부 주입)
        self._manipulation_guard = ManipulationGuard()

    async def adapt_response(
        self,
        base_response: str,
        emotion_result: "TextEmotionResult"
    ) -> AdaptedResponse:
        """
        메인 적응 응답 생성 메서드.

        P-002 ABC 매핑: 감정 적응 응답 전체 파이프라인.

        Args:
            base_response: LLM이 생성한 원본 응답
            emotion_result: 01_emotion-recognition의 TextEmotionResult

        Returns:
            AdaptedResponse: 감정 적응 응답 결과

        Raises:
            ManipulationViolationError: 비조작 검증 실패 시 (재생성 트리거)
        """
        # Step 1: 프로파일 조회
        primary_profile = RESPONSE_PROFILES[emotion_result.primary_emotion.value]
        secondary_profile = (
            RESPONSE_PROFILES.get(emotion_result.secondary_emotion.value)
            if emotion_result.secondary_emotion else None
        )

        # Step 2: 톤 구성 (P-002-a)
        composed = self._compose_tone(
            primary_profile, secondary_profile, emotion_result.intensity
        )

        # Step 3: 시스템 프롬프트 생성 (P-002-b)
        system_prompt = self._build_system_prompt(
            emotion_result, composed
        )

        # Step 4: 비조작 사전 검증 (LOCK-HW-09)
        pre_check = self._manipulation_guard.check_pre_generation(
            system_prompt,
            emotion_result.primary_emotion.value,
            emotion_result.intensity
        )
        if not pre_check.passed:
            # 위반 패턴 제거 후 재구성
            system_prompt = self._sanitize_prompt(system_prompt, pre_check.violations)

        # Step 5: LLM 생성
        adapted_text = await self._llm.generate(
            system=system_prompt,
            user=f"원본 응답을 감정에 맞게 조절:\n{base_response}",
        )

        # Step 6: 비조작 사후 검증 (LOCK-HW-09)
        post_check = self._manipulation_guard.check_post_generation(
            adapted_text,
            emotion_result.primary_emotion.value,
            emotion_result.intensity
        )

        # 사후 검증 실패 시 최대 2회 재생성
        retry_count = 0
        while not post_check.passed and retry_count < 2:
            adapted_text = await self._llm.generate(
                system=system_prompt + "\n\n[재생성 제약] 다음을 반드시 피하세요: "
                       + ", ".join(post_check.violations),
                user=f"원본 응답을 감정에 맞게 조절:\n{base_response}",
            )
            post_check = self._manipulation_guard.check_post_generation(
                adapted_text,
                emotion_result.primary_emotion.value,
                emotion_result.intensity
            )
            retry_count += 1

        # §9 L817: 비조작 사후 검증 3회 실패 → 원본 응답(base_response) 반환 (조작 가능성 텍스트 차단)
        return AdaptedResponse(
            text=base_response if not post_check.passed else adapted_text,
            tone_applied=composed.base_tone,
            style_applied=primary_profile.style,
            emotion_acknowledged=emotion_result.primary_emotion.value,
            intensity_at_generation=emotion_result.intensity,
            manipulation_check_passed=post_check.passed,
            disclaimer_included=True,  # _build_system_prompt에서 면책 포함
        )

    def _compose_tone(
        self,
        primary: ToneProfile,
        secondary: Optional[ToneProfile],
        intensity: int
    ) -> ComposedTone:
        """
        복합 감정 톤 결합 (P-002-a).

        §3.4 결합 규칙:
        1. primary 톤 = base
        2. secondary style = supplement
        3. avoid = union
        4. verbosity: primary 우선, secondary concise이면 concise
        5. emoji: none 하나라도 있으면 none

        시간복잡도: O(a) — a = avoid 합집합 크기
        """
        # 강도 기반 톤 수준 결정
        if intensity >= 9:
            tone_level = ToneLevel.CRISIS
            empathy_boost = 0.0  # 위기 시 감정 증폭 아닌 안정 우선
        elif intensity >= 7:
            tone_level = ToneLevel.MAXIMUM
            empathy_boost = 0.4
        elif intensity >= 4:
            tone_level = ToneLevel.ENHANCED
            empathy_boost = 0.2
        else:
            tone_level = ToneLevel.BASE
            empathy_boost = 0.0

        # 복합 감정 처리
        avoid_union = list(set(primary.avoid))
        supplement_style = None
        emoji = primary.emoji_level
        verbosity = primary.verbosity

        if secondary:
            supplement_style = secondary.style
            avoid_union = list(set(primary.avoid + secondary.avoid))
            if secondary.emoji_level == EmojiLevel.NONE or primary.emoji_level == EmojiLevel.NONE:
                emoji = EmojiLevel.NONE
            if secondary.verbosity == VerbosityLevel.CONCISE:
                verbosity = VerbosityLevel.CONCISE

        # 위기 시 verbosity 오버라이드 (§3.3: intensity 9-10 → crisis 전용)
        if tone_level == ToneLevel.CRISIS:
            verbosity = VerbosityLevel.CRISIS

        # 고강도 시 verbosity 오버라이드
        if tone_level == ToneLevel.MAXIMUM and verbosity != VerbosityLevel.CONCISE:
            verbosity = VerbosityLevel.CONCISE

        return ComposedTone(
            base_tone=primary.tone,
            supplement_style=supplement_style,
            emoji_level=emoji,
            verbosity=verbosity,
            avoid=avoid_union,
            tone_level=tone_level,
            empathy_boost=empathy_boost,
        )

    def _build_system_prompt(
        self,
        emotion_result: "TextEmotionResult",
        composed: ComposedTone
    ) -> str:
        """
        LLM 시스템 프롬프트 동적 생성 (P-002-b).

        감정 컨텍스트, 톤 설정, 비조작 제약을 포함하는 시스템 프롬프트를 생성한다.
        감정을 명시적으로 언급하지 않아야 한다 (사용자가 감시당한다고 느끼지 않도록).

        시간복잡도: O(1)
        """
        # 위기 모드 시 프롬프트
        if composed.tone_level == ToneLevel.CRISIS:
            return (
                "사용자가 극도로 힘든 상태입니다. "
                "안정적이고 따뜻한 톤으로 응답하세요. "
                "전문 상담 안내를 자연스럽게 포함하세요 "
                "(한국자살예방상담전화: 1393 / 정신건강위기상담전화: 1577-0199). "
                "감정을 명시적으로 언급하지 마세요. "
                "VAMOS는 의료 서비스가 아닙니다."
            )

        avoid_text = ""
        if composed.avoid:
            avoid_text = f"피해야 할 것: {', '.join(composed.avoid)}\n"

        supplement_text = ""
        if composed.supplement_style:
            supplement_text = f"보조 스타일: {composed.supplement_style}\n"

        prompt = (
            f"사용자의 현재 감정 맥락에 맞게 응답을 조절하세요.\n"
            f"응답 톤: {composed.base_tone}\n"
            f"스타일: {RESPONSE_PROFILES[emotion_result.primary_emotion.value].style}\n"
            f"{supplement_text}"
            f"상세도: {composed.verbosity.value}\n"
            f"이모지 수준: {composed.emoji_level.value}\n"
            f"{avoid_text}"
            f"\n"
            f"[필수 제약 — LOCK-HW-09 비조작 원칙]\n"
            f"- 감정을 이용하여 구매/결정/행동을 유도하지 마세요 (R-09-7)\n"
            f"- 감정 상태를 명시적으로 언급하지 마세요\n"
            f"- 자연스럽고 진심 어린 응답을 생성하세요\n"
            f"- VAMOS는 의료 서비스가 아닙니다 (LOCK-HW-04)\n"
        )

        return prompt

    def _sanitize_prompt(self, prompt: str, violations: list[str]) -> str:
        """
        비조작 검증 실패 시 프롬프트 정화.
        위반 패턴을 제거하고 비조작 제약을 강화한다.

        시간복잡도: O(v * m) — v = 위반 수, m = 프롬프트 길이
        """
        sanitized = prompt
        for pattern in MANIPULATION_PATTERNS:
            sanitized = sanitized.replace(pattern, "")

        sanitized += "\n[강화 제약] 비조작 원칙을 반드시 준수하세요."
        return sanitized
```

---

## 5. 감정별 응답 템플릿 (P-002-b)

### 5.1 감정별 시작 문구 템플릿

> LOCK-HW-01 12감정 전수 대응

| # | 감정 | 시작 문구 예시 (자연스러운 표현) | 비고 |
|---|------|-------------------------------|------|
| 1 | 기쁨 | "좋은 소식이네요!", "축하드려요!" | 감정 명시 지양 |
| 2 | 슬픔 | "그런 일이 있으셨군요.", "마음이 많이 무거우시겠어요." | avoid: 긍정 강요 |
| 3 | 분노 | "충분히 그러실 만해요.", "답답하셨겠어요." | avoid: 반박/훈계 |
| 4 | 불안 | "하나씩 정리해 볼까요?", "천천히 살펴봅시다." | 구조화된 안내 |
| 5 | 놀람 | "예상치 못한 일이었겠어요.", "같이 한번 살펴볼까요?" | 정보 제공 |
| 6 | 혐오 | "불편하셨을 거예요.", "거리를 두는 것도 방법이에요." | avoid: 판단 |
| 7 | 중립 | (기본 대화 스타일, 특별 시작 문구 없음) | - |
| 8 | 피로 | "무리하지 마세요.", "잠깐 쉬어가는 건 어떨까요?" | 간결 응답 |
| 9 | 스트레스 | "하나씩 풀어봅시다.", "가장 급한 것부터 볼까요?" | 우선순위 정리 |
| 10 | 좌절 | "여기까지 오신 것 자체가 대단해요.", "한 걸음씩 가봅시다." | 작은 성취 인정 |
| 11 | 열정 | "멋진 에너지네요!", "같이 구체적인 계획을 세워볼까요?" | 동기 부여 |
| 12 | 호기심 | "좋은 질문이에요!", "더 자세히 알아볼까요?" | 상세 설명 |

### 5.2 위기 감정 전용 템플릿 (intensity >= 9)

```
[위기 대응 응답 템플릿]
- 기본: "지금 많이 힘드시죠. 혼자 감당하지 않으셔도 돼요."
- 전문가 안내: "전문 상담을 받아보시는 건 어떨까요?"
- 연락처: "한국자살예방상담전화: 1393 / 정신건강위기상담전화: 1577-0199"
- 면책: "VAMOS는 의료 서비스가 아닙니다."

※ 위기 시에는 반드시 crisis_protocol.md (06_ethics-privacy) 트리거.
※ LOCK-HW-05 (1393/1577-0199) 고정 — 변경 금지.
```

---

## 6. 비조작 원칙 준수 로직 상세 (LOCK-HW-09)

### 6.1 비조작 원칙 정의

> LOCK (LOCK-HW-09, STEP7-P P-010): 비진단/프라이버시/투명성/전문가연결/**비조작**/자율성/기능끄기

"비조작" 원칙: 감정 상태를 이용하여 사용자의 구매, 행동, 결정을 유도하는 모든 행위를 금지한다 (R-09-7).

### 6.2 검증 3단계

```
[사전 검증 (Pre-generation)]
  ├─ 시스템 프롬프트에 조작 패턴 포함 여부
  ├─ 고강도 감정(>=7) 시 추가 제약 적용
  └─ 실패 시: 프롬프트 정화 후 재구성

[생성 중 제약 (In-generation)]
  ├─ 시스템 프롬프트에 비조작 명시적 제약 포함
  └─ "감정을 명시적으로 언급하지 마세요" 지시

[사후 검증 (Post-generation)]
  ├─ 생성된 응답에 조작 패턴 포함 여부
  ├─ 감정 명시적 언급 여부
  └─ 실패 시: 최대 2회 재생성 → 3회 실패 시 원본 응답 반환
```

### 6.3 위반 시 처리 흐름

```
비조작 검증 실패
        │
        ▼
   재생성 시도 (최대 2회)
        │
   ┌────┼────┐
   ↓         ↓
 성공      3회 실패
   │         │
   ▼         ▼
 정상 반환   원본 응답 반환 + 경고 로그
              │
              ▼
         MANIPULATION_VIOLATION 이벤트 기록
              │
              ▼
         에스컬레이션 (I-20):
         severity=HIGH, module=02_adaptive-response
```

---

## 7. 세션 간 인터페이스

### 7.1 입력 의존성

| 제공자 | 데이터 | 용도 |
|--------|--------|------|
| 01_emotion-recognition | TextEmotionResult | 감정 분석 결과 입력 |
| 06_ethics-privacy/ethics_framework | NonDiagnosticFilter | 응답 텍스트 비진단 필터링 |
| LLM 서비스 | 원본 응답 텍스트 | 적응 대상 응답 |

### 7.2 출력 인터페이스 (다른 모듈이 소비)

| 소비자 모듈 | 사용 데이터 | 인터페이스 |
|------------|-----------|-----------|
| 05_emotion-journal | AdaptedResponse 이력 | 적응 응답 로그 기록 |
| 04_stress-management | manipulation_check_passed=false 이벤트 | 조작 시도 모니터링 |

### 7.3 LOCK-HW-01 정합성 검증 (FR-4 연동)

```
RESPONSE_PROFILES 키 = LOCK-HW-01 12감정 라벨 (PRIMARY 7 + SECONDARY 5)
검증: len(RESPONSE_PROFILES) == 12
각 키 ∈ {기쁨, 슬픔, 분노, 불안, 놀람, 혐오, 중립, 피로, 스트레스, 좌절, 열정, 호기심}

위반 시: CI 빌드 실패 (FR-4 자동 검증 스크립트)
```

---

## 8. 로깅 포맷 (R-01-7)

```json
{
  "log_type": "ADAPTIVE_RESPONSE",
  "timestamp": "2026-04-10T12:00:00.000Z",
  "session_id": "sess_abc123",
  "module": "02_adaptive-response/emotion_adaptive_response",
  "level": "INFO",
  "payload": {
    "input": {
      "primary_emotion": "슬픔",
      "secondary_emotion": "피로",
      "intensity": 6,
      "base_response_length": 256
    },
    "tone_composition": {
      "base_tone": "따뜻하고 공감적인",
      "supplement_style": "휴식 제안, 부담 줄이기, 간결한 응답",
      "tone_level": "enhanced",
      "empathy_boost": 0.2,
      "verbosity": "concise",
      "emoji_level": "none"
    },
    "manipulation_check": {
      "pre_generation": {"passed": true, "violations": []},
      "post_generation": {"passed": true, "violations": []},
      "retry_count": 0
    },
    "result": {
      "adapted_response_length": 180,
      "tone_applied": "따뜻하고 공감적인",
      "disclaimer_included": true
    },
    "performance": {
      "profile_lookup_ms": 1,
      "tone_composition_ms": 1,
      "pre_check_ms": 2,
      "llm_generation_ms": 350,
      "post_check_ms": 3,
      "total_ms": 357
    }
  },
  "privacy": {
    "data_grade": "PRIVATE",
    "emotion_data_logged": true,
    "response_text_logged": false,
    "retention_days": 180
  }
}
```

---

## 9. 예외 처리 정책 표

| 예외 상황 | 처리 방식 | 폴백 값 | 에스컬레이션 |
|----------|----------|---------|------------|
| TextEmotionResult 미수신 | 중립 프로파일 적용 | tone="자연스럽고 전문적인" | 경고 로그 |
| 프로파일 키 불일치 | 중립 폴백 + 경고 | RESPONSE_PROFILES["중립"] | [ESCALATION] LOCK-HW-01 정합성 위반 |
| 비조작 사전 검증 실패 | 프롬프트 정화 후 재구성 | 정화된 프롬프트 | 정화 이벤트 로그 |
| 비조작 사후 검증 3회 실패 | 원본 응답 반환 | base_response 그대로 | [ESCALATION] MANIPULATION_VIOLATION |
| LLM 생성 타임아웃 (>500ms) | 원본 응답 반환 | base_response 그대로 | 성능 경고 로그 |
| LLM 서비스 불가 | 원본 응답 반환 + 면책 추가 | base_response + 면책 | [ESCALATION] 서비스 장애 |
| 위기 강도 (>=9) | crisis 모드 전환 | crisis 전용 프롬프트 | 위기 프로토콜 트리거 (R-09-2) |
| 복합 감정 결합 오류 | primary만 적용 | secondary=None 처리 | 경고 로그 |

---

## 10. Phase 2 테스트 시나리오

> 15건. 각 시나리오는 입력/기대 출력/검증 포인트를 포함한다.

| # | 시나리오 | 입력 감정 | intensity | 기대 톤 | 검증 포인트 |
|---|---------|----------|-----------|---------|-----------|
| T1 | 기쁨 기본 응답 | primary=기쁨 | 5 | 밝고 에너지 넘치는 | emoji_level=moderate, verbosity=normal |
| T2 | 슬픔 공감 응답 | primary=슬픔 | 6 | 따뜻하고 공감적인 | "긍정 강요" 미포함, verbosity=concise |
| T3 | 분노 차분 응답 | primary=분노 | 7 | 차분하고 이해하는 | "반박/훈계" 미포함, tone_level=MAXIMUM |
| T4 | 불안 구조화 응답 | primary=불안 | 5 | 안정적이고 구조화된 | verbosity=structured, 단계별 안내 포함 |
| T5 | 중립 기본 응답 | primary=중립 | 2 | 자연스럽고 전문적인 | tone_level=BASE, empathy_boost=0.0 |
| T6 | 복합: 슬픔+피로 | primary=슬픔, secondary=피로 | 5 | 따뜻하고 공감적인 | supplement="휴식 제안", emoji=none |
| T7 | 복합: 불안+스트레스 | primary=불안, secondary=스트레스 | 7 | 안정적이고 구조화된 | verbosity=concise (고강도 오버라이드) |
| T8 | 위기 모드 전환 | primary=슬픔 | 9 | crisis 전용 | 1393/1577-0199 포함, 면책 포함 |
| T9 | 비조작 사전 검증 | 조작 패턴 포함 프롬프트 | 5 | - | pre_check.passed=false, 정화 트리거 |
| T10 | 비조작 사후 검증 | LLM 응답에 "구매를 유도" 포함 | 6 | - | 재생성 트리거, retry_count >= 1 |
| T11 | 감정 명시 언급 차단 | LLM 응답에 "지금 슬픔이시" 포함 | 5 | - | post_check 위반 감지 |
| T12 | 프로파일 키 불일치 | unknown 감정 | 3 | 자연스럽고 전문적인 | 중립 폴백, 경고 로그 |
| T13 | LLM 타임아웃 | primary=기쁨 | 4 | - | 원본 반환, 성능 경고 |
| T14 | 고강도 피로 | primary=슬픔, secondary=피로 | 8 | 따뜻하고 공감적인 | empathy_boost=0.4, concise 강제 |
| T15 | 호기심 상세 응답 | primary=중립, secondary=호기심 | 3 | 자연스럽고 전문적인 | supplement="상세 설명", verbosity=normal |

---

## 11. 비의료 면책

> LOCK (LOCK-HW-04, STEP7-P 윤리원칙): "VAMOS는 의료 서비스가 아닙니다" 모든 건강 관련 응답에 포함

본 문서에서 정의하는 감정 적응 응답은 심리 치료 도구가 아니며, 전문 상담을 대체하지 않는다. 모든 적응 응답에는 비의료 면책이 시스템 프롬프트에 포함된다 (R-09-1). 특히 위기 모드(intensity >= 9)에서는 전문 상담 안내가 필수적으로 포함된다 (LOCK-HW-05).
