# VAMOS v13 SOT 원본 대조 검증 스킬 에이전트

> **용도**: `/sot-check [EA번호|key명]` — 추출 결과를 SOT 원본 파일에서 직접 대조 검증
> **전략**: S3(SOT 값 프롬프트 주입) + S5(체크섬 검증)
> **원칙**: "모든 추출값은 SOT 원본에서 직접 확인 가능해야 한다"

---

## 사용법

- `/sot-check EA-1` → EA-1 산출물의 모든 항목을 SOT 원본 대조
- `/sot-check TOTAL_MODULE_COUNT` → 특정 key가 등장하는 모든 EA에서 SOT 대조
- `/sot-check all` → 전체 EA 산출물 SOT 대조 (시간 소요 큼)

$ARGUMENTS 를 파싱하여 위 모드 중 하나로 실행합니다.

---

## 대조 검증 프로세스

### SC-1: 단일 EA 모드 (EA-N 지정 시)

1. 해당 EA JSON 파일 읽기
2. `metadata.source_files`에 나열된 SOT 파일들을 전부 Read tool로 읽기 (전체 읽기 필수)
3. 각 item에 대해:
   a. `source_file`의 `source_line` 행으로 이동
   b. 해당 행에서 `source_text`가 실제로 존재하는지 확인
   c. `value`가 해당 행(또는 근처 ±3줄)에서 도출 가능한지 확인
   d. 결과를 MATCH/MISMATCH/SHIFTED/NOT_FOUND 로 판정

### SC-2: 특정 Key 모드 (key명 지정 시)

1. 전체 EA JSON 파일(15개)에서 해당 key를 가진 items 수집
2. 각 item의 source_file/source_line에서 SOT 원본 대조
3. 동일 key의 값이 EA 간에 일치하는지 크로스 체크
4. 불일치 시 어느 SOT가 정본인지 판정 근거 제시

### SC-3: 전체 모드 (all 지정 시)

1. EA-1 ~ EA-15 순서대로 SC-1 실행
2. 각 EA 완료 후 중간 결과 저장
3. 전체 완료 후 종합 통계 생성

---

## 판정 기준

| 판정 | 의미 | 심각도 |
|------|------|--------|
| `MATCH` | source_text가 정확히 해당 행에 존재, value도 일치 | OK |
| `SHIFTED` | source_text가 ±10줄 이내에 존재 (행 번호만 틀림) | INFO |
| `PARTIAL` | source_text 일부만 매칭 (축약/변형 의심) | WARNING |
| `MISMATCH` | source_text는 있으나 value가 다름 | WARNING |
| `NOT_FOUND` | source_text가 해당 파일에서 전혀 발견되지 않음 | CRITICAL |

---

## 특수 검증: 3대 불일치 항목 집중 확인

v13_plan.md §2에 정의된 기존 불일치 3건을 특별히 추적합니다:

### 불일치 A: IMMUTABLE_ZONE_COUNT + NEVER_AUTO_COUNT
- CLAUDE.md §7.3 → 7개 불변구역
- CLAUDE.md §17 SDAR → NEVER_AUTO 10개
- 두 값이 다른 이유가 "범위 차이"임을 산출물이 올바르게 기록했는지 확인

### 불일치 B: COND_PRIORITY_MEDIUM + COND_PRIORITY_LOW
- PART2 요약 테이블 → MEDIUM=9, LOW=3
- PART2 상세 목록 → MEDIUM=8, LOW=4
- 상세 목록이 정본임을 산출물이 올바르게 반영했는지 확인

### 불일치 C: MODULE_TIER_SYSTEM
- PART2 → 3-tier (CORE 32 + COND 10 + EXP 39 = 81)
- CLAUDE.md → 4-tier (CORE 32 + COND 7 + EXP 32 + RE-ADD 10 = 81)
- 두 분류 기준의 차이가 산출물에 올바르게 기록되었는지 확인

---

## 출력 형식

```json
{
  "sot_check_metadata": {
    "checked_at": "2026-03-XX",
    "mode": "single_ea|single_key|full",
    "target": "EA-1|TOTAL_MODULE_COUNT|all",
    "total_items_checked": 200,
    "match": 190,
    "shifted": 5,
    "partial": 3,
    "mismatch": 1,
    "not_found": 1
  },
  "results": [
    {
      "item_id": "EA-01_045",
      "key": "CORE_MODULE_COUNT",
      "verdict": "MATCH|SHIFTED|PARTIAL|MISMATCH|NOT_FOUND",
      "source_file": "CLAUDE.md",
      "claimed_line": 123,
      "actual_line": 125,
      "claimed_text": "CORE 모듈 32개",
      "actual_text": "CORE 모듈: 32개",
      "value_match": true
    }
  ],
  "known_inconsistencies": {
    "inconsistency_A": {"tracked": true, "correctly_recorded": true},
    "inconsistency_B": {"tracked": true, "correctly_recorded": true},
    "inconsistency_C": {"tracked": true, "correctly_recorded": true}
  }
}
```

**저장 경로**: `D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\sot_check\{대상}_sot_check.json`

---

## 실행 규칙

1. **전체 읽기 강제**: SOT 파일은 반드시 전체 읽기. limit 사용 시 나머지 반드시 후속 읽기
2. **라인번호 직접 확인**: Read tool의 행 번호를 기준으로만 판정
3. **Agent tool 병렬 실행**: 각 EA의 SOT 대조는 독립적이므로 병렬 가능
4. **결과 즉시 저장**: 각 검증 완료 즉시 JSON 저장 (세션 종료 대비)
