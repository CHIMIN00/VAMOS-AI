---
name: prompt-test
description: Promptfoo 기반 추출 프롬프트 자동 테스트. 여러 프롬프트 변형 비교, 회귀 테스트, YAML 설정으로 테스트 케이스 정의.
---

# VAMOS 프롬프트 테스트 스킬 (Promptfoo)

> `/prompt-test [프롬프트파일|all]` — 추출 프롬프트의 품질 자동 테스트 및 비교

## 기존 스킬과의 차이

| 스킬 | 대상 |
|------|------|
| `/validate` | EA JSON 산출물의 정확성 검증 |
| `/eval-ea` | EA 추출 결과의 정량적 점수 |
| `/prompt-test` | **추출 프롬프트 자체**의 품질 비교 + 회귀 테스트 |

> `/eval-ea`가 "결과 채점"이라면, `/prompt-test`는 "프롬프트 비교 실험"입니다.

---

## 선행 조건

```bash
npm install -g promptfoo
```

---

## 실행 절차

```
1. $ARGUMENTS 파싱 → 테스트 대상 프롬프트 결정
   ↓
2. promptfoo_config.yaml 로딩 또는 자동 생성:
   - 프롬프트 파일 목록
   - 테스트 케이스 (SOT + 기대 결과)
   - 검증 로직 (promptfoo_assertions.js)
   ↓
3. Promptfoo 실행:
   npx promptfoo eval --config "D:/VAMOS/.claude/hooks/promptfoo_config.yaml"
   ↓
4. 결과 파싱 및 요약:
   - 각 프롬프트 변형별 성공률
   - 회귀 감지 (이전보다 나빠진 항목)
   - 최적 프롬프트 추천
   ↓
5. 결과 저장
```

---

## 설정 파일

### promptfoo_config.yaml (테스트 설정)
```yaml
prompts:
  - phase0_A_extraction_prompt_v1.md
  - phase0_A_extraction_prompt_v2.md

tests:
  - description: "LOCK 값 추출 정확도"
    vars:
      sot_file: "D2.0-07_Safety_Cost_Approval.md"
    assert:
      - type: contains
        value: "NEVER_AUTO"
      - type: javascript
        value: "output.items.length >= 40"
```

### promptfoo_assertions.js (커스텀 검증)
- EA JSON 스키마 검증
- 카테고리 분포 검증
- 커버리지 검증

---

## 출력

```json
{
  "prompt_test_metadata": {
    "prompts_tested": 2,
    "test_cases": 10,
    "verdict": "PASS|REGRESSION|FAIL"
  },
  "results": [
    {
      "prompt": "phase0_A_extraction_prompt_v1.md",
      "pass_rate": 0.90,
      "failed_tests": ["수치 카테고리 완전성"]
    }
  ],
  "recommendation": "v2 프롬프트 추천 (pass_rate 0.95 vs 0.90)",
  "regression_detected": false
}
```

**저장**: `v13_results/phase0/extraction/validation/prompt_test_result.json`

---

## 판정 기준

| 판정 | 조건 |
|------|------|
| **PASS** | 모든 테스트 통과 |
| **REGRESSION** | 이전 결과 대비 pass_rate 하락 |
| **FAIL** | pass_rate < 0.80 |

---

## $ARGUMENTS 처리

- `$ARGUMENTS`가 프롬프트 파일 경로면 → 해당 프롬프트만 테스트
- `$ARGUMENTS`가 `all`이면 → 등록된 모든 프롬프트 변형 테스트
- `$ARGUMENTS`가 `regression`이면 → 이전 결과와 비교 (회귀 테스트)
- `$ARGUMENTS`가 비어있으면 → 현재 사용 중인 프롬프트 테스트
