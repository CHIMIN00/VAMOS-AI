---
name: artifact-diff
description: llm-diff 기반 EA/CM 산출물 버전 간 시맨틱 diff + 이력 추적. /json-diff와 달리 버전 히스토리 저장 및 parent-child 관계 추적.
---

# VAMOS 산출물 버전 Diff + 이력 추적 스킬 (llm-diff)

> `/artifact-diff [파일A] [파일B]` — EA/CM 산출물의 버전 간 시맨틱 diff + 이력 추적

## 기존 스킬과의 차이

| 스킬 | 비교 방식 |
|------|----------|
| `/json-diff` | 두 파일의 "현재 상태" 비교 (1회성) |
| `/artifact-diff` | **버전 히스토리 저장 + 변화 추이 추적** (지속적) |

> `/json-diff`가 "스냅샷 비교"라면, `/artifact-diff`는 "변경 이력 관리"입니다.

---

## 선행 조건

```bash
pip install llm-diff
```

---

## 실행 절차

```
1. $ARGUMENTS 파싱 → 비교 모드 결정 (diff / history / regression)
   ↓
2. Python 훅 실행:
   python "D:/VAMOS/.claude/hooks/artifact_version_tracker.py" <모드> <인자...>
   ↓
3-A. diff 모드:
   - 두 파일 시맨틱 diff (llm-diff 엔진)
   - 변경 항목 구조적 분류
   - 버전 히스토리에 diff 결과 append
   ↓
3-B. history 모드:
   - 지정 EA의 전체 버전 히스토리 조회
   - parent-child 관계 시각화
   ↓
3-C. regression 모드:
   - Phase 전후 전체 EA에 대해 자동 diff
   - 악화된 항목 자동 식별
   ↓
4. 결과 저장 (append-only 이력)
```

---

## 출력

```json
{
  "artifact_diff_metadata": {
    "mode": "diff|history|regression",
    "file_a": "v13_EA01_v1.json",
    "file_b": "v13_EA01_v2.json",
    "total_changes": 5,
    "parent_version": "v1",
    "child_version": "v2"
  },
  "changes": {
    "added": [],
    "removed": [],
    "modified": [],
    "reordered": []
  },
  "version_history": [
    {
      "version": "v1",
      "timestamp": "2026-03-19T10:00:00",
      "parent": null,
      "changes_from_parent": 0
    }
  ]
}
```

**저장**: `v13_results/phase0/extraction/validation/{파일명}_artifact_diff.json`
**이력**: `v13_results/phase0/extraction/validation/artifact_history.json` (append-only)

---

## 판정 기준

| 판정 | 조건 |
|------|------|
| **IDENTICAL** | total_changes = 0 |
| **MINOR_DIFF** | total_changes ≤ 5 |
| **MAJOR_DIFF** | total_changes > 5 |
| **REGRESSION** | regression 모드에서 악화된 항목 존재 |

---

## $ARGUMENTS 처리

- `파일A 파일B` → 두 파일 시맨틱 diff + 이력 기록
- `history EA파일` → 해당 EA의 버전 이력 조회
- `regression phase번호` → Phase 전후 변화 분석
- 비어있음 → 에러 (인자 필수)
