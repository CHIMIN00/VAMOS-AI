---
name: guardrails-validate
description: Guardrails AI 기반 EA JSON 검증 + 실패 시 자동 reask. DV-1~DV-9를 Validator 클래스로 래핑하여 검증 실패 시 AI에게 자동 재생성 요청.
---

# VAMOS Guardrails AI 검증 스킬

> `/guardrails-validate [EA파일|all]` — Guardrails AI로 EA JSON 검증 + 자동 재생성

## 기존 스킬과의 차이

| 스킬 | 검증 실패 시 |
|------|-------------|
| `/validate` | 오류 보고 → 사용자가 수동 수정 |
| `/guardrails-validate` | **AI에게 자동 재생성 요청 → 재검증** (reask 루프) |

> `/validate`가 "검사"라면, `/guardrails-validate`는 "검사 + 자동 수리"입니다.

---

## 선행 조건

```bash
pip install guardrails-ai
```

---

## 실행 절차

```
1. $ARGUMENTS 파싱 → 대상 EA JSON 결정
   ↓
2. Python 훅 실행:
   python "D:/VAMOS/.claude/hooks/guardrails_validator.py" "<EA_JSON_경로>"
   ↓
3. 훅이 Guardrails Guard 객체 생성:
   - Pydantic 모델로 EA JSON 스키마 정의
   - DV-1~DV-9 각각을 Validator 클래스로 등록
   ↓
4. Guard.validate() 실행:
   - PASS → 검증 완료
   - FAIL → reask 루프 (최대 3회):
     a. 실패 항목 + 오류 메시지를 프롬프트에 포함
     b. AI에게 해당 항목만 재생성 요청
     c. 재검증
   ↓
5. 최종 결과 저장
```

---

## 출력

```json
{
  "guardrails_metadata": {
    "target_file": "v13_EA01_claude_md.json",
    "initial_pass": false,
    "reask_count": 2,
    "final_pass": true,
    "validators_applied": ["DV-1", "DV-2", "DV-3", "DV-4", "DV-5", "DV-6", "DV-7", "DV-8", "DV-9"],
    "verdict": "PASS|FAIL"
  },
  "validation_details": [
    {
      "validator": "DV-1",
      "description": "JSON 스키마 필수 필드 존재",
      "status": "PASS|FAIL",
      "reask_applied": false
    }
  ],
  "reask_history": [
    {
      "attempt": 1,
      "failed_validators": ["DV-2"],
      "fixed": true
    }
  ]
}
```

**저장**: `v13_results/phase0/extraction/validation/{파일명}_guardrails_result.json`

---

## 판정 기준

| 판정 | 조건 |
|------|------|
| **PASS** | 모든 DV 검증 통과 (reask 후 포함) |
| **FAIL** | reask 3회 후에도 DV 검증 실패 |

---

## $ARGUMENTS 처리

- `$ARGUMENTS`가 파일 경로면 → 해당 파일만 검증
- `$ARGUMENTS`가 `all`이면 → extraction/ 디렉토리의 모든 v13_EA*.json 검증
- `$ARGUMENTS`가 비어있으면 → 가장 최근 생성된 EA JSON 파일 검증
