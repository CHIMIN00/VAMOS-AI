# H16: Verbalized Confidence Calibration — 구현 명세

> **도메인**: 5-2_File-Context (DEFINED-HERE)  
> **파이프라인 위치**: Phase F — Layer 6 (최종 검증)  
> **버전**: V1 (CORE)  
> **난이도**: Easy-Medium  
> **핵심 도구**: 프롬프트 기반 (별도 라이브러리 불필요) (AUTHORITY_CHAIN §3.3)  
> **상위 문서**: `../FILE_CONTEXT_구조화_종합계획서.md` §6.4 H 상세표  
> **원본 참조**: `../../FILE CONTEXT/VAMOS_파일_컨텍스트_이해_최종_업데이트.md` §8 H16

---

## 1. 개요

### 1.1 문제 정의

LLM이 틀린 답을 높은 확신으로 제시하는 과신 편향(overconfidence bias)이 존재한다. 환각 응답이 자신감 있는 톤으로 전달되면 사용자가 오류를 인지하지 못한다.

### 1.2 해결 전략

LLM에게 답변과 함께 **수치 신뢰도 점수(0.0~1.0)**를 출력하게 하고, 이를 실제 정확도와 교정(calibration)한다. 저신뢰(< 0.7) 응답은 자동으로 W9 Self-Consistency를 트리거하여 다중 샘플 합의로 검증한다.

### 1.3 기대 효과

- **오류의 ~40%를 저신뢰로 플래그** (SOT §8 H16)
- **도메인 내 교정 +10.9%** (NAACL 교정 방법론)
- Phase G-4에서 신뢰도 이력 축적 → 교정 곡선 학습 (장기 자기 개선)

---

## 2. Phase F 8-Layer 배치

```
Phase F: 최종 검증 (공통) — 8 Layer
  Layer 1: QoD 5요소 ≥ 0.6 [L9]
  Layer 2: Pydantic Strict [G5] + R6 무생성
  Layer 3: [W11] Attributed QA (원문 발췌, 일치도 ≥ 0.8)
  Layer 4: NLI 환각 탐지 [A8]
  Layer 4.5: [H17] Chain-of-Verification (V2)
  Layer 5: Cross-Chunk 일관성 (SEAE)
  ──────────────────────────────────────
  Layer 6: [H16] Verbalized Confidence Calibration ◀── 본 기술
  ──────────────────────────────────────
  Layer 7: [W9] Self-Consistency 3x (< 0.7 트리거)
  Layer 8: [H5] FLARE 재검색 (V2)
```

### 2.1 실행 조건

| 조건 | 설명 |
|------|------|
| 활성화 트리거 | Layer 1~5 통과 후 항상 실행 (V1 기본 활성) |
| 선행 단계 | Layer 5 (Cross-Chunk 일관성) 완료 |
| 후속 단계 | Confidence < 0.7 → Layer 7 (W9 Self-Consistency) 자동 트리거 |
| V2 연동 | Layer 4.5 (H17 Chain-of-Verification)는 V2 항목. V1에서는 스킵 |

---

## 3. L9 QoD 체계와의 관계

> **L9 QoD**(CLAUDE.md LOCK)와 **H16 Confidence**는 **다른 계층의 품질 지표**이다.

| 구분 | L9 QoD 점수 | H16 Confidence Score |
|------|------------|---------------------|
| **대상** | 파이프라인 전체 응답 품질 | 개별 응답/주장의 생성 신뢰도 |
| **구성** | Accuracy(0.30)+Relevance(0.25)+Completeness(0.20)+Safety(0.15)+Efficiency(0.10) | 단일 수치 0.0~1.0 (LLM 자기 평가) |
| **기준** | **≥ 0.6** (Phase F Layer 1 게이트) | **< 0.7 → W9 트리거** |
| **위치** | Phase F Layer 1 (입구 게이트) | Phase F Layer 6 (출구 전 교정) |
| **소유** | CLAUDE.md LOCK (L9) | 5-2 DEFINED-HERE |

> QoD ≥ 0.6은 파이프라인 최소 품질 게이트. Confidence는 해당 게이트를 통과한 응답에 대한 추가 신뢰도 검증. 두 지표는 보완 관계이며 대체 관계가 아니다.

---

## 4. 구현 상세

### 4.1 신뢰도 산출 프롬프트

```python
# R1: Python 3.11+ 필수
# R2: Pydantic v2 스키마 검증

from pydantic import BaseModel, Field
from enum import Enum

class ConfidenceLevel(str, Enum):
    """신뢰도 수준"""
    HIGH = "HIGH"        # [0.7, 1.0] — 단일 응답 채택
    LOW = "LOW"          # [0.4, 0.7) — W9 Self-Consistency 트리거
    VERY_LOW = "VERY_LOW"  # [0.0, 0.4) — W9 + 원본 재검색

class ConfidenceResult(BaseModel):
    """신뢰도 평가 결과 (R2 Pydantic v2)"""
    score: float = Field(ge=0.0, le=1.0, description="수치 신뢰도 (0.0~1.0)")
    level: ConfidenceLevel
    reasoning: str = Field(description="신뢰도 판단 근거")
    uncertainty_factors: list[str] = Field(
        default_factory=list,
        description="불확실성 요인 목록 (예: 모호한 소스, 상충 정보)"
    )
    trigger_w9: bool = Field(description="W9 Self-Consistency 트리거 여부")

class ConfidenceConfig(BaseModel):
    """Confidence Calibration 설정 (R2 Pydantic v2)"""
    w9_trigger_threshold: float = Field(default=0.7, description="W9 트리거 임계값")
    very_low_threshold: float = Field(default=0.4, description="원본 재검색 임계값")
    calibration_enabled: bool = Field(default=True, description="교정 곡선 적용 여부 (G-4 학습 후)")
```

### 4.2 신뢰도 평가 프롬프트

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama  # [A8] 로컬 모델 (비용 0)

CONFIDENCE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a calibrated confidence assessor for VAMOS AI.
After the response has been generated and verified through Layers 1-5, 
evaluate how confident you are in the response's correctness.

Output a confidence score between 0.0 and 1.0 based on:

1. SOURCE STRENGTH (0.0~0.3):
   - Direct quote from source: +0.3
   - Paraphrase with citation: +0.2
   - Inferred from context: +0.1
   - No clear source: +0.0

2. CONSISTENCY (0.0~0.3):
   - Consistent across all retrieved chunks: +0.3
   - Minor inconsistencies resolved: +0.2
   - Some conflicting information: +0.1
   - Contradictory sources: +0.0

3. SPECIFICITY (0.0~0.2):
   - Specific facts/numbers with source: +0.2
   - General statements with context: +0.1
   - Vague or hedged claims: +0.0

4. QUERY MATCH (0.0~0.2):
   - Directly answers the question: +0.2
   - Partially answers: +0.1
   - Tangential answer: +0.0

Also list any uncertainty factors that lowered your confidence.

Respond with a JSON object."""),
    ("human", """Query: {query}

Generated Response:
---
{response}
---

Source Chunks Used:
---
{source_chunks}
---

Evaluate confidence.""")
])
```

### 4.3 W9 트리거 연동 로직

```python
async def evaluate_and_trigger(
    query: str,
    response: str,
    source_chunks: list[str],
    config: ConfidenceConfig = ConfidenceConfig(),
) -> ConfidenceResult:
    """
    신뢰도 평가 후 W9 트리거 판단.
    
    흐름:
    1. H16 신뢰도 산출 (Layer 6)
    2. score < 0.7 → W9 Self-Consistency 발동 (Layer 7)
       - N=3 응답 재생성 (R-52-7 DEFINED-HERE LOCK)
       - 합의 판정 (3/3 확정 / 2/3 다수결 / 불일치 재확인)
    3. score < 0.4 → W9 + 원본 소스 재검색
    """
    # 신뢰도 산출
    result = await _compute_confidence(query, response, source_chunks)
    
    # 트리거 판단
    if result.score < config.very_low_threshold:
        result.level = ConfidenceLevel.VERY_LOW
        result.trigger_w9 = True
        # W9 발동 + 원본 재검색
    elif result.score < config.w9_trigger_threshold:
        result.level = ConfidenceLevel.LOW
        result.trigger_w9 = True
        # W9 발동 (N=3 재생성)
    else:
        result.level = ConfidenceLevel.HIGH
        result.trigger_w9 = False
        # 단일 응답 채택 (비용 최적)
    
    return result
```

### 4.4 H16→W9 순차 시너지 흐름

```
Phase F Layer 1~5 검증 통과
    │
    ▼
Layer 6: H16 Confidence Score 산출
    │
    ├── Score ≥ 0.7 (HIGH)
    │   └── 단일 응답 채택 → Phase G 진입
    │
    ├── 0.4 ≤ Score < 0.7 (LOW)
    │   └── Layer 7: W9 Self-Consistency 발동
    │       ├── N=3 응답 재생성 (R-52-7 LOCK)
    │       ├── 합의 판정 (w09_self_consistency.md §3.1 규칙)
    │       └── 최종 응답 + Confidence 재산출
    │
    └── Score < 0.4 (VERY_LOW)
        └── 원본 소스 재검색 + W9 발동
            ├── Phase E 검색 재실행 (강화된 쿼리)
            ├── 새 컨텍스트로 N=3 재생성
            └── 재시도 후에도 < 0.4 → 사용자에게 불확실성 명시
```

---

## 5. LOCK 참조

| LOCK | 값 (SOT 원문 글자 그대로) | 연동 |
|------|--------------------------|------|
| **L9** | Accuracy(0.30)+Relevance(0.25)+Completeness(0.20)+Safety(0.15)+Efficiency(0.10) ≥ 0.6 | L9 QoD는 Layer 1 게이트, H16 Confidence는 Layer 6 교정. 보완 관계 (§3 참조) |

> **R-52-1 준수**: L9 값은 SOT 원본(CLAUDE.md L264-266)에서 글자 그대로 복사.

---

## 6. 거버넌스 준수

| 규칙 | 준수 내용 |
|------|----------|
| R1 | Python 3.11+ — asyncio 기반 비동기 신뢰도 산출 |
| R2 | `ConfidenceResult`, `ConfidenceConfig` Pydantic v2 BaseModel |
| R6 | 오류 40% 플래그, 교정 +10.9%는 SOT §8 H16에 근거 |
| R7 | V1 범위 — 프롬프트 기반. V2 항목(H17 CoV-RAG, H5 FLARE)에 의존하지 않음 |
| R9 | 신뢰도 점수, 불확실성 요인, 교정 내부 로그는 사용자 응답에 미노출 |
| R10 | [A8] 로컬 모델 기본 사용 (비용 0) |
| R-52-7 | W9 Self-Consistency N=3 DEFINED-HERE LOCK — H16이 트리거 조건만 제공, N 값 무변경 |

---

## 7. 벤치마크 연동 (§12)

| 메트릭 | 기준선 | H16 기여 |
|--------|--------|----------|
| Faithfulness | ≥ 0.85 | 저신뢰 응답 자동 검증(W9) → 환각 억제 → 충실도 향상 |
| Answer Relevancy | ≥ 0.80 | 불확실 응답 재생성 → 쿼리 매칭 향상 |
| Citation Accuracy | ≥ 0.85 | 저신뢰 인용 플래그 → W11 재검증 트리거 |

### 7.1 Phase G-4 교정 곡선 (장기)

| 항목 | 설명 |
|------|------|
| 데이터 수집 | H16 산출 신뢰도 + 실제 정확도 쌍(pair) 축적 |
| 교정 방법 | Platt Scaling / Temperature Scaling (NAACL 교정 방법론) |
| 효과 | 사용 횟수 증가 → 교정 정밀도 향상 → 오류 플래그 정확도 상승 |
| 반영 위치 | Phase G-4 Self-Improving Retrieval → H16 교정 곡선 학습 |

> §12.2: "RAGAS + H16 교정 곡선" — RAGAS 자동 평가와 H16 교정 곡선이 결합하여 자동 벤치마크 체계를 구성한다.

---

## 8. 시너지 관계

| 대상 | 관계 | 설명 |
|------|------|------|
| **W9 (Self-Consistency)** | **순차 — H16→W9 트리거** | H16 저신뢰(< 0.7) → W9 N=3 샘플 합의 자동 발동. _index.md 시너지 표 등재 |
| L9 (QoD) | 보완 | QoD=파이프라인 품질 게이트(Layer 1), Confidence=개별 응답 신뢰도(Layer 6) |
| W11 (Attributed QA) | 연동 | 저신뢰 인용 → W11 BERTScore ≥ 0.8 재검증 |
| Phase G-4 | 장기 시너지 | 신뢰도 이력 → 교정 곡선 학습 → 자기 개선 |

---

## 9. 성능 기대치

| 항목 | 값 |
|------|-----|
| 오류 플래그율 | ~40% (SOT §8 H16) |
| 교정 향상 | +10.9% (도메인 내) |
| 추가 지연 | ~100ms (프롬프트 기반, 로컬 7B) |
| 비용 | ₩0 (로컬 모델) |
| W9 트리거율 | 예상 15~25% (저신뢰 응답 비율) |

---

*작성일*: 2026-04-12  
*세션*: P1-6  
*검증*: W9 트리거 연동(< 0.7) 확인, L9 QoD 체계와 관계(보완) 명시
