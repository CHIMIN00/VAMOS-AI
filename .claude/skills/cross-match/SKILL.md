---
name: cross-match
description: EA JSON 간 교차매칭(CM) 자동화. C1~C8 유형별 비교 패턴 적용, CONSISTENT/INCONSISTENT/SOURCE_CONFLICT 판정, 이전 CM 결과와 diff 비교.
---

# VAMOS 교차매칭(CM) 스킬

> `/cross-match [EA쌍|C유형|all]` — EA 간 교차 비교 및 일관성 검증

## 목적

2개 이상의 EA JSON에서 동일 개념을 다른 SOT에서 추출한 항목을 비교하여
일관성(CONSISTENT) 또는 불일치(INCONSISTENT)를 판정합니다.

---

## 선행 조건

1. 비교 대상 EA JSON이 `/validate` Layer A PASS 상태
2. EA JSON이 `v13_results/phase0/extraction/`에 존재

---

## 비교 패턴 (C1~C8)

| 유형 | 비교 방법 | 판정 기준 |
|------|----------|----------|
| C1 (수치) | 동일 개념의 숫자값 비교 | 값 불일치 → INCONSISTENT |
| C2 (카운트) | COUNT vs LIST 길이 교차 | 불일치 → INCONSISTENT |
| C3 (목록) | 목록 항목 집합 비교 | 부분집합/차집합 분석 |
| C4 (상태) | 상태 전이 경로 비교 | 경로 불일치 → INCONSISTENT |
| C5 (설정) | 동일 키의 값 비교 | 값 불일치 → INCONSISTENT |
| C6 (제약) | 제약조건 범위 비교 | 범위 충돌 → INCONSISTENT |
| C7 (잠금) | LOCK/FREEZE 대상 비교 | 대상/값 불일치 → CRITICAL |
| C8 (참조) | 참조 대상 존재 확인 | 참조 미존재 → WARNING |

---

## CM JSON 스키마

```json
{
  "metadata": {
    "cm_id": "CM-C{N}",
    "comparison_type": "C1",
    "source_eas": ["EA-01", "EA-07"],
    "total_comparisons": 0,
    "consistent": 0,
    "inconsistent": 0,
    "source_conflict": 0
  },
  "comparisons": [
    {
      "comp_id": 1,
      "key": "TOTAL_MODULE_COUNT",
      "ea_a": {"ea_id": "EA-01", "item_id": 5, "value": 81, "source_text": "..."},
      "ea_b": {"ea_id": "EA-07", "item_id": 12, "value": 81, "source_text": "..."},
      "result": "CONSISTENT|INCONSISTENT|SOURCE_CONFLICT",
      "severity": "CRITICAL|WARNING|INFO",
      "note": "판정 근거"
    }
  ]
}
```

---

## 실행 절차

```
1. $ARGUMENTS 파싱 → 비교 대상 결정
   ↓
2. 대상 EA JSON 로딩
   ↓
3. 동일 key 또는 관련 key 쌍 추출
   - 표준 키 기준 매칭
   - 유사 키 탐지 (예: MODULE_TOTAL ↔ TOTAL_MODULE_COUNT)
   ↓
4. C유형별 비교 로직 적용
   ↓
5. 판정: CONSISTENT / INCONSISTENT / SOURCE_CONFLICT
   - SOURCE_CONFLICT: 2개 이상의 SOT가 서로 다른 값을 명시
   ↓
6. 이전 CM 결과와 diff (있는 경우)
   - 새로 발견된 불일치
   - 해소된 불일치 (delta 적용 후)
   ↓
7. CM JSON 저장
   ↓
8. cm_validator.py 실행 (Layer A 검증)
   python "D:/VAMOS/.claude/hooks/cm_validator.py" "<CM_JSON_PATH>"
```

---

## $ARGUMENTS 처리

- `EA-01 EA-07` → 특정 EA 쌍 비교
- `C1` → C1 유형 항목만 전체 EA에서 교차 비교
- `all` → 8개 CM 유형 전체 실행 (Agent tool로 병렬)
- 비어있음 → 가장 최근 수정된 EA의 관련 CM만 실행

## 출력

**저장 위치**: `v13_results/phase0/cross_match/v13_CM_C{N}_{설명}.json`

## 이전 버전 CM 참조

비교 시 이전 CM 결과를 참조하여 변화 추적:
- `v13_results/phase0/cross_match/` (기존 v13 CM)
- `v13_results/phase0/v13_sot_inconsistency_list.json` (31개 불일치 목록)
