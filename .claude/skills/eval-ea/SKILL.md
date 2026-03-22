---
name: eval-ea
description: DeepEval 기반 EA 추출 결과 정량적 평가. HallucinationMetric, FaithfulnessMetric, AnswerRelevancyMetric + 커스텀 메트릭(DV PASS율, 카테고리 분포, 커버리지).
---

# VAMOS EA 정량적 평가 스킬 (DeepEval)

> `/eval-ea [EA파일|all]` — EA 추출 결과에 대한 정량적 메트릭 자동 계산

## 기존 스킬과의 차이

| 스킬 | 평가 방식 |
|------|----------|
| `/validate` | 결정론적 PASS/FAIL (DV-1~DV-9) |
| `/audit` | 적대적 감사 (정성적 탐지) |
| `/eval-ea` | **정량적 점수** (0~1 스케일, 임계값 기반 판정) |

> `/validate`가 "합격/불합격"이라면, `/eval-ea`는 "몇 점인지 채점"입니다.

---

## 선행 조건

```bash
pip install deepeval
```

---

## 메트릭 종류

### 표준 메트릭 (DeepEval 내장)
| 메트릭 | 설명 | 임계값 |
|--------|------|--------|
| HallucinationMetric | source_text vs SOT 원본 비교 | ≤ 0.05 |
| FaithfulnessMetric | value가 source_text에서 도출 가능한지 | ≥ 0.90 |
| AnswerRelevancyMetric | 추출된 key가 context와 관련 있는지 | ≥ 0.85 |

### 커스텀 메트릭 (VAMOS 전용)
| 메트릭 | 설명 | 임계값 |
|--------|------|--------|
| dv_pass_rate | DV-1~DV-9 통과율 | = 1.0 |
| category_balance | C1~C8 카테고리 분포 균형 | ≥ 0.80 |
| coverage_rate | SOT 대비 추출 커버리지 | ≥ 0.85 |

---

## 실행 절차

```
1. $ARGUMENTS 파싱 → 대상 EA JSON 결정
   ↓
2. Python 훅 실행:
   python "D:/VAMOS/.claude/hooks/deepeval_metrics.py" "<EA_JSON_경로>"
   ↓
3. 훅이 수행하는 작업:
   a. EA JSON 로딩 + SOT 원본 파일 읽기
   b. 각 항목을 DeepEval test case로 변환
   c. 6개 메트릭 계산
   d. 임계값 기반 판정
   ↓
4. 결과 JSON 저장
```

---

## 출력

```json
{
  "eval_metadata": {
    "target_file": "v13_EA01_claude_md.json",
    "total_items_evaluated": 85,
    "metrics_computed": 6,
    "verdict": "PASS|FAIL"
  },
  "metrics": {
    "hallucination_score": 0.02,
    "faithfulness_score": 0.95,
    "relevancy_score": 0.91,
    "dv_pass_rate": 1.0,
    "category_balance": 0.87,
    "coverage_rate": 0.93
  },
  "failed_metrics": [],
  "per_item_scores": []
}
```

**저장**: `v13_results/phase0/extraction/validation/{파일명}_eval_result.json`

---

## 판정 기준

| 판정 | 조건 |
|------|------|
| **PASS** | 모든 메트릭이 임계값 이상 |
| **FAIL** | 하나 이상의 메트릭이 임계값 미만 |

---

## $ARGUMENTS 처리

- `$ARGUMENTS`가 파일 경로면 → 해당 파일만 평가
- `$ARGUMENTS`가 `all`이면 → extraction/ 디렉토리의 모든 v13_EA*.json 평가
- `$ARGUMENTS`가 `all --compare-with v12`이면 → v12 결과와 메트릭 비교
- `$ARGUMENTS`가 비어있으면 → 가장 최근 생성된 EA JSON 파일 평가
