---
name: deterministic
description: LLM 재현성 제어. 동일 입력에 대해 동일 출력을 최대한 재현. 캐시된 이전 결과와 현재 결과 비교로 drift 감지.
---

# VAMOS E-32 Deterministic 스킬 (LLM Output Reproducibility)

> `/deterministic [on|off|compare]` — LLM 추출 재현성 제어 및 drift 감지

## 기반 기술

- **LLM Reproducibility Control**: temperature=0 고정 + seed 고정으로 출력 재현성 극대화
- **Drift Detection**: 캐시된 이전 결과와 현재 결과를 비교하여 변동 감지

---

## 기능

1. temperature=0 고정으로 동일 입력 → 동일 출력 최대한 보장
2. 이전 추출 결과를 캐시에 저장
3. 동일 SOT 재추출 시 이전 결과와 비교 → drift 항목 탐지
4. "어제와 오늘 같은 작업인데 결과가 다르다" → 원인 분석

---

## E-46 gpt-cache와의 차이

| 스킬 | 목적 | 방식 |
|------|------|------|
| `/deterministic` | **품질/재현성** | 동일 입력 → 동일 출력 보장, drift 감지 |
| `/gpt-cache` | **비용/속도** | 유사 입력 → 이전 출력 반환 (캐싱) |

---

## 실행 절차

### `/deterministic on` — 재현성 모드 활성화

```
1. 현재 설정 백업
2. temperature=0 고정
3. 이후 모든 추출 작업에서:
   - 입력(SOT 경로 + 프롬프트 해시)을 키로 사용
   - 추출 결과를 캐시에 저장
   - 타임스탬프 기록
```

### `/deterministic off` — 비활성화

```
1. 재현성 모드 해제
2. 캐시는 유지 (compare에서 사용 가능)
```

### `/deterministic compare` — drift 분석

```
1. 캐시에서 가장 최근 2개 결과 로드
   ↓
2. key별 value 비교:
   - STABLE: 동일한 값 → 재현성 확인
   - DRIFTED: 다른 값 → drift 발생
   - NEW: 이전에 없던 key → 신규 추가
   - MISSING: 이전에 있었으나 현재 없음 → 누락
   ↓
3. drift 원인 분석:
   - SOT 파일 변경 여부 확인
   - 프롬프트 변경 여부 확인
   - 모델 버전 변경 여부 확인
   ↓
4. drift 보고서 출력
```

---

## 출력 형식

```json
{
  "deterministic_metadata": {
    "target": "SOT 파일 경로",
    "previous_run": "2026-03-19T14:30:00",
    "current_run": "2026-03-20T10:00:00",
    "total_keys": 0,
    "stable": 0,
    "drifted": 0,
    "new": 0,
    "missing": 0,
    "drift_rate": "0%"
  },
  "drift_details": [
    {
      "key": "MODULE_COUNT",
      "status": "DRIFTED",
      "previous_value": 81,
      "current_value": 82,
      "possible_cause": "SOT_UNCHANGED | 모델 비결정성"
    }
  ]
}
```

## 저장 위치

### 캐시
`v13_results/phase0/extraction/deterministic_cache/{SOT해시}_{타임스탬프}.json`

### drift 보고서
`v13_results/phase0/extraction/validation/{파일명}_drift_report.json`

---

## $ARGUMENTS 처리

- `$ARGUMENTS`가 `on`이면 → 재현성 모드 활성화
- `$ARGUMENTS`가 `off`이면 → 재현성 모드 비활성화
- `$ARGUMENTS`가 `compare`이면 → 가장 최근 2개 결과 drift 분석
- `$ARGUMENTS`가 `compare [SOT파일]`이면 → 해당 SOT의 drift 분석
- `$ARGUMENTS`가 비어있으면 → 현재 상태 표시
