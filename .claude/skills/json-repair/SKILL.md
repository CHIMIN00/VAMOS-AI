---
name: json-repair
description: json-repair 라이브러리 기반 깨진/불완전한 JSON 자동 복구. 닫히지 않은 괄호, 후행 쉼표, 이스케이프 오류, 잘린 JSON 자동 수정 후 DV 재검증.
---

# VAMOS JSON 자동 복구 스킬 (json-repair)

> `/json-repair [EA파일]` — 깨진/불완전한 EA JSON 자동 복구 + DV 재검증

## 기존 도구와의 차이

| 상황 | 기존 방식 | json-repair |
|------|----------|-------------|
| JSON 파싱 실패 | 전체 재추출 (비용 높음) | **자동 복구 시도 → DV 검증만 재실행** |

---

## 선행 조건

```bash
pip install json-repair
```

---

## 복구 대상 오류

- 닫히지 않은 괄호/따옴표
- 후행 쉼표 (trailing comma)
- 이스케이프 안 된 특수문자
- 잘린 JSON (토큰 제한으로 중간에 끊김)
- 주석이 포함된 JSON
- 단일 따옴표 → 이중 따옴표 변환

---

## 실행 절차

```
1. $ARGUMENTS 파싱 → 대상 파일 결정
   ↓
2. Python 훅 실행:
   python "D:/VAMOS/.claude/hooks/json_auto_repair.py" "<깨진_JSON_경로>"
   ↓
3. 훅 동작:
   a. 원본 파일 읽기
   b. json.loads() 시도 → 성공 시 "이미 유효" 반환
   c. 실패 시 json_repair.repair_json() 실행
   d. 복구된 JSON을 json.loads()로 재검증
   e. 성공 시 복구된 JSON 저장
   f. deterministic_validator.py로 DV 재검증
   ↓
4. 결과 저장
```

---

## 출력

```json
{
  "repair_metadata": {
    "target_file": "v13_EA01_claude_md.json",
    "original_valid": false,
    "repair_attempted": true,
    "repair_success": true,
    "changes_made": 3,
    "dv_revalidation": "PASS|FAIL",
    "verdict": "REPAIRED|ALREADY_VALID|UNREPAIRABLE"
  },
  "repairs": [
    {
      "type": "unclosed_bracket",
      "position": 15234,
      "description": "닫히지 않은 } 추가"
    }
  ]
}
```

**저장**: `v13_results/phase0/extraction/validation/{파일명}_repair_result.json`
**복구된 파일**: 원본 경로에 덮어쓰기 (백업은 `{원본}.bak`)

---

## 판정 기준

| 판정 | 조건 |
|------|------|
| **ALREADY_VALID** | 원본 JSON이 이미 유효 |
| **REPAIRED** | 복구 성공 + DV 재검증 PASS |
| **UNREPAIRABLE** | 복구 불가 또는 DV 재검증 FAIL |

---

## $ARGUMENTS 처리

- `$ARGUMENTS`가 파일 경로면 → 해당 파일 복구 시도
- `$ARGUMENTS`가 비어있으면 → 가장 최근 파싱 실패한 JSON 파일 자동 탐지
