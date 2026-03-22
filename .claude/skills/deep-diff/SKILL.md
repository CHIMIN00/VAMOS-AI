---
name: deep-diff
description: DeepDiff 라이브러리 기반 Python 객체/JSON 깊은 구조적 비교. 타입 변경 감지, 리스트 순서 변경 vs 내용 변경 구분, 부동소수점 근사 비교.
---

# VAMOS 깊은 구조적 Diff 스킬 (DeepDiff)

> `/deep-diff [파일A] [파일B]` — DeepDiff 기반 객체 레벨 정밀 비교

## 기존 스킬과의 차이

| 스킬 | 비교 엔진 | 수준 |
|------|----------|------|
| `/json-diff` (A-7) | Python difflib | 텍스트 레벨 |
| `/deep-diff` (B-34) | **DeepDiff 라이브러리** | **객체 레벨, 타입 인식** |

> `/json-diff`가 "텍스트 비교"라면, `/deep-diff`는 "구조 + 타입 정밀 비교"입니다.

---

## 선행 조건

```bash
pip install deepdiff
```

---

## 기능

- 타입 변경 감지 (string → number)
- 딕셔너리 키 추가/삭제/변경
- 리스트 요소 순서 변경 vs 내용 변경 구분
- 부동소수점 근사 비교 (significant_digits)
- 깊이 제한 없는 재귀적 비교
- EA 버전 간 정밀 차이 분석

---

## 실행 절차

```
1. $ARGUMENTS 파싱 → 두 JSON 파일 경로 추출
   ↓
2. Python 훅 실행:
   python "D:/VAMOS/.claude/hooks/deep_diff_compare.py" "<파일A>" "<파일B>" [--ignore-order]
   ↓
3. 훅 동작:
   a. 두 JSON 파일 로딩
   b. DeepDiff(obj_a, obj_b, ...) 실행
   c. 결과를 구조화된 JSON으로 변환
   ↓
4. 결과 저장 및 요약 출력
```

---

## 출력

```json
{
  "deep_diff_metadata": {
    "file_a": "v13_EA01_v1.json",
    "file_b": "v13_EA01_v2.json",
    "ignore_order": false,
    "total_changes": 8,
    "verdict": "IDENTICAL|MINOR_DIFF|MAJOR_DIFF"
  },
  "changes": {
    "type_changes": [],
    "values_changed": [],
    "dictionary_item_added": [],
    "dictionary_item_removed": [],
    "iterable_item_added": [],
    "iterable_item_removed": [],
    "repetition_change": []
  },
  "summary": {
    "type_changes": 0,
    "values_changed": 3,
    "items_added": 2,
    "items_removed": 1,
    "order_changes": 2
  }
}
```

**저장**: `v13_results/phase0/extraction/validation/{파일A}_{파일B}_deep_diff.json`

---

## 판정 기준

| 판정 | 조건 |
|------|------|
| **IDENTICAL** | total_changes = 0 |
| **MINOR_DIFF** | total_changes ≤ 5 |
| **MAJOR_DIFF** | total_changes > 5 |

---

## $ARGUMENTS 처리

- `파일A 파일B` → 두 파일 깊은 비교
- `파일A 파일B --ignore-order` → 리스트 순서 무시
- `파일A 파일B --significant-digits N` → 소수점 N자리까지만 비교
- 비어있음 → 에러 (두 파일 경로 필수)
