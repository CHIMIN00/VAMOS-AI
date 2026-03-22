---
name: json-diff
description: 두 JSON 파일 간 시맨틱(의미적) diff. JSON 구조를 이해하는 비교로 키 순서 무시, 배열 재정렬 감지. EA/CM 전용 + 임의 JSON/텍스트 파일 범용 비교 지원.
---

# VAMOS JSON 시맨틱 Diff 스킬

> `/json-diff [파일A] [파일B]` — 두 EA/CM JSON 파일 간 시맨틱(의미적) 비교

## 목적

단순 텍스트 diff가 아닌 JSON 구조를 이해하는 시맨틱 비교를 수행합니다.
Phase 재실행 전후 결과를 비교하여 실질적 변경사항만 정확히 파악합니다.

---

## 기반 기술

- **기본 모드**: Python 내장 `json` + `difflib` (`json_semantic_diff.py` 훅 사용)
- **고급 모드**: `graphtage` 설치 시 Graphtage 시맨틱 Diff 엔진 활성화

---

## 기능

- 두 EA/CM JSON 파일 간 시맨틱 diff
- 단순 텍스트 diff가 아닌 JSON 구조 이해
- 키 순서 무시, 배열 요소 재정렬 감지
- 추가/삭제/변경된 항목을 구조적으로 표시
- Phase 재실행 전후 결과 비교

---

## 기존 스킬과의 차이

| 스킬 | 비교 방식 | 대상 |
|------|----------|------|
| `/cross-match` | EA 간 동일 key의 value 비교 | EA 쌍의 추출 결과 |
| `/json-diff` | **두 JSON/텍스트 파일의 구조적 전체 비교** | 임의의 파일 쌍 |

> `/cross-match`는 "같은 개념의 값이 일치하는가"를 판정하고,
> `/json-diff`는 "두 파일이 구조적으로 어떻게 다른가"를 보여줍니다.

---

## 실행 절차

### 1단계: 인자 파싱

`$ARGUMENTS`에서 두 JSON 파일 경로를 추출합니다.

| 인자 | 동작 |
|------|------|
| `파일A 파일B` | 두 파일 비교 |
| 비어있음 | 에러 — 두 파일 경로 필수 |

### 2단계: Python 훅 실행

```bash
python "D:/VAMOS/.claude/hooks/json_semantic_diff.py" "<파일A>" "<파일B>"
```

### 3단계: 결과 해석 및 요약 출력

훅이 생성하는 JSON 결과를 읽고 사용자에게 요약 표시합니다.

---

## 출력 형식

```json
{
  "diff_metadata": {
    "file_a": "...",
    "file_b": "...",
    "total_changes": 0,
    "added": 0,
    "removed": 0,
    "modified": 0,
    "reordered": 0
  },
  "changes": [...]
}
```

### 요약 표시 예시

```
=== JSON 시맨틱 Diff 결과 ===
파일A: v13_EA01_old.json
파일B: v13_EA01_new.json

총 변경: 5건
  추가(added):    2건
  삭제(removed):  1건
  변경(modified): 1건
  재정렬(reordered): 1건
```

---

## 사용 예시

```
/json-diff v13_EA01_old.json v13_EA01_new.json
/json-diff "D:/VAMOS/04. 구현단계/v13_results/phase0/v13_EA01.json" "D:/VAMOS/04. 구현단계/v13_results/phase1/v13_EA01.json"
```

---

## $ARGUMENTS 처리

- `파일A 파일B` → 두 파일 시맨틱 비교
- `파일A 파일B --text` → 강제 텍스트 diff 모드
- `파일A 파일B --output 경로` → 결과를 지정 경로에 저장
- 비어있음 → 에러 (두 파일 경로 필수)

---

## 판정 기준

| 판정 | 조건 |
|------|------|
| **IDENTICAL** | total_changes = 0 |
| **MINOR_DIFF** | total_changes ≤ 5 |
| **MAJOR_DIFF** | total_changes > 5 |

> 이 스킬은 PASS/FAIL이 아닌 **차이량 기반 판정**입니다.
> 변경이 "좋은지 나쁜지"는 사용자가 판단합니다.

---

## 저장 위치

- EA/CM 모드: `v13_results/phase0/extraction/validation/{파일A}_{파일B}_diff.json`
- 범용 모드: `--output`으로 지정하거나, stdout 출력

---

## 범용 모드 (일반 파일 비교)

> EA/CM JSON뿐 아니라 **임의의 JSON 파일 및 텍스트 파일**을 비교할 수 있습니다.

### 자동 모드 판별

```
두 파일 모두 .json → JSON 시맨틱 diff (훅 사용)
두 파일 중 하나라도 .json이 아님 → 텍스트 diff 모드
두 파일 모두 v13_EA/v13_CM 패턴 → EA/CM 모드 (기존, items_diff 포함)
```

### JSON 범용 모드

임의의 JSON 파일 쌍을 시맨틱 비교합니다. EA/CM 전용 `items_diff`는 `items` 배열이 있을 때만 자동 활성화됩니다.

```bash
# 임의 JSON 비교
python "D:/VAMOS/.claude/hooks/json_semantic_diff.py" "<파일A.json>" "<파일B.json>"

# settings.json 변경 전후 비교
/json-diff settings_old.json settings_new.json

# package.json 비교
/json-diff package_v1.json package_v2.json
```

### 텍스트 diff 모드

JSON이 아닌 파일(.md, .py, .yaml, .txt 등)은 **라인 기반 시맨틱 diff**를 수행합니다.

```bash
# Python 훅이 자동으로 텍스트 모드 전환
python "D:/VAMOS/.claude/hooks/json_semantic_diff.py" "<파일A>" "<파일B>" --text
```

텍스트 모드 비교 항목:
- 추가된 줄 (added lines)
- 삭제된 줄 (removed lines)
- 변경된 줄 (modified lines)
- 이동된 블록 (moved blocks) — 동일 내용이 다른 위치로 이동

### 범용 모드 출력

```json
{
  "diff_metadata": {
    "mode": "json_generic|text",
    "file_a": "...",
    "file_b": "...",
    "file_type": ".json|.md|.py|...",
    "total_changes": 0,
    "added": 0,
    "removed": 0,
    "modified": 0,
    "reordered": 0,
    "moved_blocks": 0
  },
  "changes": [...]
}
```

### 범용 사용 예시

```
/json-diff SKILL_v1.md SKILL_v2.md
/json-diff old_config.yaml new_config.yaml
/json-diff hook_v1.py hook_v2.py
/json-diff package.json package_updated.json
```
