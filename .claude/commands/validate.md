# VAMOS v13 EA 산출물 검증 스킬 에이전트

> **용도**: `/validate [파일경로]` — EA 추출 JSON 산출물이 R1~R6 규칙을 준수하는지 자동 검증
> **적용 대상**: `v13_results/phase0/extraction/v13_EA*.json`

---

## 검증 대상

$ARGUMENTS 가 제공되면 해당 파일만 검증합니다.
$ARGUMENTS 가 비어있으면 `D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\` 디렉토리의 모든 `v13_EA*.json` 파일을 검증합니다.

---

## 검증 규칙 체크리스트

각 EA JSON 파일에 대해 아래 검증을 수행하세요:

### VR-1: 구조 무결성 (Schema Validation)
- [ ] `metadata` 필드 존재: agent, version, created, source_files, total_lines_read, total_items_extracted, categories
- [ ] `items` 배열 존재 및 비어있지 않음
- [ ] 각 item에 필수 필드 8개 전수 존재: item_id, category, source_file, source_line, source_text, key, value, value_type
- [ ] `category`가 C1~C8 중 하나
- [ ] `value_type`이 number|string|list|boolean 중 하나
- [ ] `metadata.categories`의 C1~C8 합계 = `metadata.total_items_extracted` = `items` 배열 길이

### VR-2: 라인번호 실제 확인 (R1, R2 준수)
- [ ] 각 item의 `source_file` 경로를 실제로 읽어서 `source_line` 행이 존재하는지 확인
- [ ] 해당 행 근처(±3줄)에 `source_text`의 핵심 키워드가 포함되어 있는지 확인
- [ ] source_line이 0이거나 파일 총 줄 수를 초과하면 **CRITICAL**

### VR-3: 환각 탐지 (R3 준수)
- [ ] `source_text`가 100자 이내인지 확인
- [ ] `source_text`가 SOT 원본 파일의 해당 라인에 실제로 존재하는지 확인 (부분 문자열 매칭)
- [ ] `value`가 `source_text`에서 도출 가능한 값인지 확인
- [ ] value가 null이면 반드시 item에 note 필드가 있어야 함

### VR-4: 표준 키 준수
- [ ] 표준 키 목록에 있는 개념은 반드시 표준 키 사용 확인
- [ ] 자유 생성 키는 `{카테고리}_{대상}_{속성}` 형식 준수 확인
- [ ] 동일 key가 같은 파일 내에서 중복 사용되지 않는지 확인 (같은 값이면 OK, 다른 값이면 WARNING)

### VR-5: 카운트 정합성 (S5 체크섬)
- [ ] category별 항목 수가 metadata.categories와 일치하는지 확인
- [ ] C2(카운트) 항목에서 count 값과 해당 list 항목의 배열 길이가 일치하는지 확인
  - 예: `CORE_MODULE_COUNT=32` ↔ `CORE_MODULE_LIST`의 배열 길이 = 32

### VR-6: item_id 연속성
- [ ] item_id가 `EA-{N}_{seq}` 형식이고 seq가 001부터 연속적인지 확인
- [ ] 건너뛴 번호가 있으면 WARNING

---

## 출력 형식

검증 결과를 아래 JSON 형식으로 저장하세요:

```json
{
  "validation_metadata": {
    "validated_at": "2026-03-XX",
    "target_file": "v13_EA01_claude_md.json",
    "total_items_checked": 200,
    "pass_count": 195,
    "fail_count": 5,
    "result": "PASS|FAIL|WARN"
  },
  "checks": [
    {
      "rule": "VR-2",
      "item_id": "EA-01_045",
      "severity": "CRITICAL|WARNING|INFO",
      "message": "source_line 999 exceeds file length 697",
      "expected": "line <= 697",
      "actual": "line = 999"
    }
  ],
  "summary": {
    "CRITICAL": 0,
    "WARNING": 3,
    "INFO": 2
  }
}
```

**저장 경로**: `D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\validation\{원본파일명}_validation.json`

---

## 실행 방법

1. 대상 EA JSON 파일을 Read tool로 전체 읽기
2. 해당 EA의 source_files에 해당하는 SOT 원본 파일도 Read tool로 읽기
3. VR-1 ~ VR-6 순서대로 검증 수행
4. 검증 결과를 JSON으로 저장
5. CRITICAL이 1건이라도 있으면 결과를 **FAIL**로 판정
6. WARNING만 있으면 **WARN**, 전부 통과면 **PASS**

**⚠️ 검증 시 반드시 Agent tool로 병렬 실행하세요** — 각 EA 파일 검증은 독립적이므로 동시 수행 가능합니다.
