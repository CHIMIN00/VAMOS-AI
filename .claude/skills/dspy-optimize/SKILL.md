---
name: dspy-optimize
description: DSPy(Stanford NLP) 기반 프롬프트 자동 최적화. Golden Set 기준으로 BootstrapFewShot/MIPRO/BayesianSignatureOptimizer로 최적 프롬프트 탐색.
---

# VAMOS 프롬프트 자동 최적화 스킬 (DSPy)

> `/dspy-optimize [EA번호] --metric <메트릭>` — DSPy로 추출 프롬프트 자동 최적화

## 기존 스킬과의 차이

| 스킬 | 방식 |
|------|------|
| `/prompt-test` (B-12, Promptfoo) | 여러 프롬프트 변형을 **사람이 작성** → 자동 비교 (수동 최적화) |
| `/dspy-optimize` (B-39, DSPy) | 프롬프트를 **AI가 자동 탐색/최적화** (자동 최적화) |

> `/prompt-test`로 현재 성능 측정 → `/dspy-optimize`로 자동 개선 → `/prompt-test`로 개선 확인

---

## 선행 조건

```bash
pip install dspy
```

---

## 최적화 기법

| 기법 | 설명 | 적합한 경우 |
|------|------|------------|
| BootstrapFewShot | Few-shot 예시 자동 선별 | 소량 데이터, 빠른 최적화 |
| MIPRO | 프롬프트 지시문 자동 최적화 | 지시문 개선 필요 시 |
| BayesianSignatureOptimizer | 베이지안 기반 전역 탐색 | 최고 성능 추구 |

---

## 실행 절차

```
1. $ARGUMENTS 파싱 → 대상 EA + 최적화 메트릭 결정
   ↓
2. Python 훅 실행:
   python "D:/VAMOS/.claude/hooks/dspy_extraction_module.py" <EA번호> --metric <메트릭>
   ↓
3. 훅 동작:
   a. 추출 작업을 DSPy Module로 정의 (Signature + Predict)
   b. Golden Set (A-8) 로딩 → 학습/검증 데이터셋 분할
   c. 메트릭 함수 정의 (accuracy / coverage)
   d. DSPy Optimizer 실행:
      - 최적 프롬프트 탐색 (few-shot 예시 + 지시문)
      - 반복 평가 + 개선
   e. 최적화된 프롬프트 저장
   ↓
4. 최적화 전/후 비교 결과 저장
```

---

## 출력

```json
{
  "dspy_metadata": {
    "target_ea": "EA-01",
    "metric": "accuracy|coverage",
    "optimizer": "BootstrapFewShot|MIPRO|BayesianSignatureOptimizer",
    "iterations": 50,
    "verdict": "IMPROVED|NO_IMPROVEMENT"
  },
  "results": {
    "baseline_score": 0.85,
    "optimized_score": 0.93,
    "improvement": 0.08,
    "optimized_prompt_path": "D:/VAMOS/.claude/hooks/optimized_prompts/EA01_optimized.md"
  },
  "few_shot_examples": [
    {
      "input": "...",
      "output": "..."
    }
  ]
}
```

**저장**: `v13_results/phase0/extraction/validation/{EA번호}_dspy_result.json`
**최적화 프롬프트**: `D:/VAMOS/.claude/hooks/optimized_prompts/{EA번호}_optimized.md`

---

## 판정 기준

| 판정 | 조건 |
|------|------|
| **IMPROVED** | optimized_score > baseline_score |
| **NO_IMPROVEMENT** | optimized_score ≤ baseline_score |

---

## $ARGUMENTS 처리

- `EA번호 --metric accuracy` → 정확도 최적화
- `EA번호 --metric coverage` → 커버리지 최적화
- `compare` → 최적화 전/후 결과 비교
- 비어있음 → 에러 (EA 번호 필수)
