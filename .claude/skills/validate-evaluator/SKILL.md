---
name: validate-evaluator
description: LLM Judge/평가자의 신뢰도를 golden-set 대비 검증. 인간 라벨과의 일치율(Cohen's Kappa), 평가 편향, 보정(calibration) 점검.
---

# VAMOS Validate-Evaluator 스킬 (평가자 검증)

> `/validate-evaluator [judge-prompt|eval-ea|all]` — 평가자 자체의 신뢰도 검증

## 이 스킬이 해결하는 문제

```
문제: write-judge-prompt로 Judge를 만들었는데, 그 Judge가 정확한지 모름
문제: eval-ea 메트릭 점수가 높은데, 실제 품질과 괴리
문제: 평가자가 특정 유형에 편향 (예: 짧은 항목에 항상 높은 점수)

해결: 평가자를 golden-set(인간 라벨)과 대조하여 신뢰도 정량화
```

---

## 기존 스킬과의 관계

```
write-judge-prompt → Judge 프롬프트 설계
validate-evaluator → Judge가 맞는지 검증 (이 스킬)
eval-audit         → 전체 평가 파이프라인 감사 (상위 레벨)

순서: write-judge-prompt → validate-evaluator → (문제 있으면) → write-judge-prompt 재설계
```

---

## 실행 절차

### `/validate-evaluator judge-prompt` — Judge 프롬프트 검증

```
1. golden-set에서 인간 라벨(정답 판정) 로드
   ↓
2. 동일 항목에 대해 Judge 프롬프트 실행 → AI 판정 수집
   ↓
3. 인간 라벨 vs AI 판정 비교:

   일치 매트릭스:
                    AI: PASS    AI: FAIL
   인간: PASS    |  TP (진양성)  |  FP (거짓양성)  |
   인간: FAIL    |  FN (거짓음성) |  TN (진음성)   |

   ↓
4. 지표 산출:
   - Accuracy: (TP + TN) / 전체
   - Cohen's Kappa: 우연 일치 보정한 일치율
   - 거짓 양성률: FP / (FP + TN)
   - 거짓 음성률: FN / (TP + FN)
   ↓
5. 편향 분석:
   - 카테고리별 정확도 (C1~C8 어디서 약한지)
   - 값 길이별 정확도 (짧은/긴 항목 편향)
   - confidence별 정확도 (고신뢰/저신뢰 편향)
   ↓
6. 신뢰도 보고서 출력
```

### `/validate-evaluator eval-ea` — eval-ea 메트릭 검증

```
1. golden-set 항목 중 "확실한 오류"와 "확실한 정답" 선별
   ↓
2. eval-ea 메트릭으로 해당 항목 평가
   ↓
3. 메트릭이 오류를 낮은 점수로, 정답을 높은 점수로 판정하는지 확인:
   - 오류인데 높은 점수 → 메트릭 거짓 음성
   - 정답인데 낮은 점수 → 메트릭 거짓 양성
   ↓
4. 메트릭별 ROC/AUC 산출 (가능한 경우)
5. 보정 곡선: 메트릭 점수 구간별 실제 정확도 매핑
```

### `/validate-evaluator all` — 전체 검증

```
judge-prompt + eval-ea 순차 실행 → 통합 보고서
```

---

## 출력 형식

```json
{
  "evaluator_validation_metadata": {
    "evaluator_type": "judge-prompt|eval-ea",
    "golden_set_size": 0,
    "tested_items": 0,
    "timestamp": "2026-03-20T10:00:00"
  },
  "agreement_metrics": {
    "accuracy": 0.0,
    "cohens_kappa": 0.0,
    "false_positive_rate": "0%",
    "false_negative_rate": "0%"
  },
  "bias_analysis": {
    "by_category": {
      "C1": 0.0, "C2": 0.0, "C3": 0.0
    },
    "by_value_length": {
      "short": 0.0, "medium": 0.0, "long": 0.0
    },
    "by_confidence": {
      "high": 0.0, "low": 0.0
    }
  },
  "calibration": {
    "score_range_0.9_1.0": {"actual_accuracy": 0.0},
    "score_range_0.7_0.9": {"actual_accuracy": 0.0},
    "score_range_0.5_0.7": {"actual_accuracy": 0.0}
  },
  "verdict": "TRUSTED|NEEDS_CALIBRATION|UNRELIABLE"
}
```

## 저장 위치

`v13_results/phase0/extraction/validation/evaluator_validation_report.json`

---

## 판정 기준

| 판정 | 조건 |
|------|------|
| TRUSTED | Cohen's Kappa ≥ 0.8 + 거짓 음성률 < 5% |
| NEEDS_CALIBRATION | Cohen's Kappa 0.6~0.8 또는 카테고리별 편향 감지 |
| UNRELIABLE | Cohen's Kappa < 0.6 또는 거짓 음성률 > 15% |

---

## $ARGUMENTS 처리

- `$ARGUMENTS`가 `judge-prompt`이면 → Judge 프롬프트 검증
- `$ARGUMENTS`가 `eval-ea`이면 → eval-ea 메트릭 검증
- `$ARGUMENTS`가 `all`이면 → 전체 검증
- `$ARGUMENTS`가 비어있으면 → `all` 실행
