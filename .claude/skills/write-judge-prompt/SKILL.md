---
name: write-judge-prompt
description: EA 추출 품질을 판단하는 LLM-as-Judge 프롬프트를 체계적으로 설계. 평가 기준 정의, 루브릭 생성, 판정 일관성 보장.
---

# VAMOS Write-Judge-Prompt 스킬 (LLM-as-Judge 설계)

> `/write-judge-prompt [평가대상] --criteria [기준]` — 평가용 Judge 프롬프트 생성

## 이 스킬이 해결하는 문제

```
문제: eval-ea의 메트릭은 범용적 → VAMOS 특화 평가 기준 부재
문제: "이 EA가 좋은가?"의 "좋은"이 주관적 → 판정 흔들림
문제: 사람마다/실행마다 다른 기준으로 평가 → 비일관적

해결: VAMOS 맥락에 맞는 Judge 프롬프트를 구조적으로 설계
```

---

## 기존 스킬과의 차이

| 스킬 | 역할 |
|------|------|
| `/eval-ea` | DeepEval 범용 메트릭으로 점수 산출 |
| `/audit` | 적대적 감사 (오류 탐지) |
| `/write-judge-prompt` | **VAMOS 특화 평가 기준 + 루브릭을 Judge 프롬프트로 생성** |

> `/write-judge-prompt`는 평가 자체를 하지 않고, **평가하는 방법을 설계**합니다.

---

## 실행 절차

### Step 1: 평가 차원 정의

```
사용자가 평가할 대상에 따라 차원을 자동 선정:

[EA 추출 품질 평가 시]
  D1. SOT 충실도: 추출된 값이 SOT 원본과 일치하는가?
  D2. 필드 완전성: 필수 필드가 모두 채워져 있는가?
  D3. 값 정확도: 숫자/단위/범위가 정확한가?
  D4. 카테고리 적합성: C1~C8 분류가 올바른가?
  D5. source_text 품질: 인용 근거가 정확하고 충분한가?

[CM 교차매칭 품질 평가 시]
  D1. 일관성 판정 정확도
  D2. SOURCE_CONFLICT 탐지율
  D3. 비교 쌍 완전성

[프롬프트 품질 평가 시]
  D1. 추출 정확도 향상 기여
  D2. 환각 유발 가능성
  D3. 범용성 (다양한 SOT에 적용 가능)
```

### Step 2: 루브릭 생성 (5점 척도)

```
각 차원에 대해 구체적 루브릭 생성:

예시 — D1. SOT 충실도:
  5점: 값이 SOT 원문과 완전 일치, source_text가 정확
  4점: 값이 SOT와 일치하나 표현이 약간 다름 (동의어 사용)
  3점: 값의 핵심은 맞으나 세부사항 누락/변형
  2점: 값이 SOT와 부분적으로만 일치
  1점: 값이 SOT에 없음 (환각) 또는 완전 불일치
```

### Step 3: Judge 프롬프트 조립

```
시스템 프롬프트:
  "당신은 VAMOS EA 추출 품질을 평가하는 전문 심사관입니다.
   아래 루브릭에 따라 각 차원을 1~5점으로 채점하세요.
   반드시 근거를 함께 제시하세요."

입력 형식:
  - SOT 원문 (관련 구절)
  - EA 추출 결과 (평가 대상)
  - 루브릭 (채점 기준)

출력 형식:
  - 차원별 점수 (1~5)
  - 차원별 근거
  - 종합 점수
  - 판정: EXCELLENT / GOOD / ACCEPTABLE / POOR / REJECT
```

### Step 4: 일관성 검증

```
동일 입력에 대해 Judge를 3회 실행:
  - 3회 모두 동일 판정 → 일관성 HIGH
  - 2/3 일치 → 일관성 MODERATE → 루브릭 모호한 부분 보완
  - 전부 다름 → 일관성 LOW → 루브릭 재설계 필요
```

---

## 출력 형식

```json
{
  "judge_prompt_metadata": {
    "target_type": "EA|CM|prompt",
    "dimensions": 5,
    "rubric_scale": "1-5",
    "timestamp": "2026-03-20T10:00:00"
  },
  "judge_prompt": {
    "system": "시스템 프롬프트 전문...",
    "input_template": "입력 템플릿...",
    "output_schema": {
      "dimensions": [
        {"name": "SOT 충실도", "score": "1-5", "evidence": "string"}
      ],
      "overall_score": "1-5",
      "verdict": "EXCELLENT|GOOD|ACCEPTABLE|POOR|REJECT"
    }
  },
  "consistency_test": {
    "runs": 3,
    "agreement_rate": "0%",
    "consistency": "HIGH|MODERATE|LOW"
  }
}
```

## 저장 위치

`D:\VAMOS\.claude\skills\write-judge-prompt\generated\{대상}_judge_prompt.json`

---

## $ARGUMENTS 처리

- `$ARGUMENTS`가 `EA`이면 → EA 추출 품질 Judge 프롬프트 생성
- `$ARGUMENTS`가 `CM`이면 → CM 교차매칭 Judge 프롬프트 생성
- `$ARGUMENTS`가 `prompt`이면 → 프롬프트 품질 Judge 프롬프트 생성
- `$ARGUMENTS`에 `--criteria [기준]`이 포함되면 → 사용자 정의 기준 사용
- `$ARGUMENTS`가 비어있으면 → EA 기본 Judge 프롬프트 생성
