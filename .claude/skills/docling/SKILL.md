---
name: docling
description: Docling(IBM Research) 기반 문서 구조 인식 파싱. SOT 마크다운의 표/중첩 리스트/코드 블록 정확한 파싱. AI 읽기 전 사전 구조화로 후반부 누락 감소.
---

# VAMOS 문서 구조 파싱 스킬 (Docling)

> `/docling <서브커맨드> [SOT파일]` — SOT 문서의 구조 인식 파싱 (표, 리스트, 코드 블록)

## 기존 스킬과의 차이

| 스킬 | 문서 파싱 |
|------|----------|
| `/validate` SV-2 | AI가 SOT를 직접 Read tool로 읽기 (구조 오해석 가능) |
| `/docling` | **Docling 엔진으로 표/리스트/코드블록을 사전 구조화 → AI에게 전달** |

> AI가 SOT를 읽기 전에 Docling으로 사전 파싱하여 구조 인식 정확도를 높입니다.

---

## VAMOS 특화 가치

```
SOT 마크다운에는 복잡한 표, 중첩 리스트, 코드 블록이 혼재
→ AI가 직접 읽으면 구조를 잘못 해석하는 경우 있음
→ Docling 사전 파싱 → 구조화된 데이터로 AI에게 전달
→ 후반부 누락(DV-10) 감소 기대
```

---

## 선행 조건

```bash
pip install docling
```

---

## 서브커맨드

| 커맨드 | 기능 |
|--------|------|
| `parse [SOT파일\|all]` | SOT 구조 파싱 (표 + 리스트 + 코드 블록) |
| `tables [SOT파일]` | 표(table) 자동 추출 → 구조화된 데이터 |
| `structure [SOT파일]` | 문서 구조 트리 출력 (헤딩/섹션 계층) |

---

## 실행 절차

```
1. $ARGUMENTS 파싱 → 서브커맨드 + 대상 결정
   ↓
2. Python 훅 실행:
   python "D:/VAMOS/.claude/hooks/docling_parser.py" <서브커맨드> <SOT_파일>
   ↓
3-A. parse 모드:
   - SOT 마크다운 → Docling DocumentConverter 로딩
   - 표, 중첩 리스트, 코드 블록, 머리말/꼬리말 구분
   - 각 요소를 구조화된 JSON으로 변환
   ↓
3-B. tables 모드:
   - 문서에서 표(table)만 추출
   - 각 표를 rows/columns 구조로 변환
   - 셀 병합, 다중 행/열 처리
   ↓
3-C. structure 모드:
   - 문서 구조 트리 생성
   - 헤딩 계층 (H1~H6) 기반 섹션 분리
   - 각 섹션의 요소 수 표시
   ↓
4. 결과 저장
```

---

## 출력

### parse 모드
```json
{
  "docling_metadata": {
    "target_file": "D2.0-01_Overview.md",
    "mode": "parse",
    "total_elements": 250,
    "tables": 5,
    "lists": 12,
    "code_blocks": 3,
    "verdict": "COMPLETE"
  },
  "elements": [
    {
      "type": "table",
      "location": {"start_line": 45, "end_line": 62},
      "content": {"rows": 15, "columns": 4, "data": []}
    }
  ]
}
```

### tables 모드
```json
{
  "docling_metadata": {
    "target_file": "D2.0-01_Overview.md",
    "mode": "tables",
    "tables_found": 5,
    "verdict": "COMPLETE"
  },
  "tables": [
    {
      "table_id": 1,
      "location": {"start_line": 45},
      "headers": ["모듈명", "유형", "상태", "비고"],
      "rows": []
    }
  ]
}
```

**저장**: `v13_results/phase0/extraction/validation/{파일명}_docling_parsed.json`

---

## 판정 기준

| 판정 | 조건 |
|------|------|
| **COMPLETE** | 파싱 정상 완료 |
| **PARTIAL** | 일부 요소 파싱 실패 |
| **ERROR** | 파일 읽기 또는 파싱 전체 실패 |

---

## $ARGUMENTS 처리

- `parse SOT파일` → 해당 SOT 전체 구조 파싱
- `parse all` → SOT 디렉토리 전체 파싱
- `tables SOT파일` → 표만 추출
- `structure SOT파일` → 문서 구조 트리 출력
- 비어있음 → 에러 (서브커맨드 필수)
