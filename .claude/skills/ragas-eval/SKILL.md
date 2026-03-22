---
name: ragas-eval
description: RAGAS 기반 RAG 파이프라인 정량적 품질 평가. Faithfulness, Answer Relevancy, Context Precision, Context Recall 4대 메트릭. EA 추출의 SOT 충실도 평가.
---

# VAMOS RAG 파이프라인 평가 스킬 (RAGAS)

> `/ragas-eval [EA파일|all]` — RAGAS 4대 메트릭으로 EA 추출 품질 정량 평가

## 기존 스킬과의 차이

| 스킬 | 초점 |
|------|------|
| `/eval-ea` (B-11, DeepEval) | 환각/충실성/관련성 (추출 결과 중심) |
| `/ragas-eval` (B-35, RAGAS) | **RAG 4대 메트릭** (검색+생성 전체 파이프라인 중심) |

> `/eval-ea`가 "추출 결과 채점"이라면, `/ragas-eval`은 "검색→생성 전체 파이프라인 채점"입니다.
> 상호 보완적이므로 동시 사용 가능.

---

## 선행 조건

```bash
pip install ragas
```

---

## 메트릭 (RAGAS 4대 메트릭)

| 메트릭 | 설명 | 범위 | 임계값 |
|--------|------|------|--------|
| Faithfulness | 생성된 답변이 컨텍스트에 충실한지 | 0~1 | ≥ 0.85 |
| Answer Relevancy | 답변이 질문과 관련 있는지 | 0~1 | ≥ 0.80 |
| Context Precision | 검색된 컨텍스트가 정확한지 | 0~1 | ≥ 0.80 |
| Context Recall | 필요한 컨텍스트가 모두 검색되었는지 | 0~1 | ≥ 0.75 |

---

## 실행 절차

```
1. $ARGUMENTS 파싱 → 평가 모드 결정 (EA / pipeline)
   ↓
2. Python 훅 실행:
   python "D:/VAMOS/.claude/hooks/ragas_evaluator.py" "<EA_JSON_경로>"
   ↓
3. 훅 동작:
   a. EA JSON 로딩
   b. 각 항목을 RAGAS 데이터셋으로 변환:
      - question: key + context 정보
      - answer: value
      - contexts: [source_text, SOT 원문 ±5줄]
      - ground_truths: [SOT 원본에서 직접 추출한 값]
   c. RAGAS evaluate() 실행
   d. 4대 메트릭 계산
   ↓
4. 결과 저장
```

---

## 출력

```json
{
  "ragas_metadata": {
    "target_file": "v13_EA01_claude_md.json",
    "total_items_evaluated": 85,
    "verdict": "PASS|FAIL"
  },
  "metrics": {
    "faithfulness": 0.92,
    "answer_relevancy": 0.88,
    "context_precision": 0.85,
    "context_recall": 0.80
  },
  "failed_metrics": [],
  "per_item_scores": []
}
```

**저장**: `v13_results/phase0/extraction/validation/{파일명}_ragas_result.json`

---

## 판정 기준

| 판정 | 조건 |
|------|------|
| **PASS** | 4대 메트릭 모두 임계값 이상 |
| **FAIL** | 하나 이상의 메트릭이 임계값 미만 |

---

## $ARGUMENTS 처리

- `$ARGUMENTS`가 파일 경로면 → 해당 EA만 평가
- `$ARGUMENTS`가 `all`이면 → 전체 EA 평가
- `$ARGUMENTS`가 `pipeline`이면 → 전체 RAG 파이프라인 평가
- `$ARGUMENTS`가 비어있으면 → 가장 최근 EA 파일 평가
