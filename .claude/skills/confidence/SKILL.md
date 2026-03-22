---
name: confidence
description: EA 항목별 신뢰도 점수를 반복 추출 또는 교차 모델로 보정
triggers:
  - /confidence
args:
  - name: target
    description: EA 파일 경로
  - name: --method
    description: "self (자체 반복) 또는 cross (교차 모델)"
    optional: true
    default: self
  - name: --recalibrate
    description: 기존 confidence 값 재보정
    optional: true
---

# `/confidence` — 신뢰도 보정

## 목적
EA JSON의 confidence 값을 **통계적으로 보정**한다. AI 자체 판단 confidence가 아닌 실측 기반 신뢰도.

## 방법

### 방법 A: `--method self` (비용 $0, 기본값)
1. 동일 SOT에서 **3회 독립 추출** (temperature 변경)
2. 항목별 일치율 = 보정된 confidence
   - 3/3 일치 → confidence 1.0
   - 2/3 일치 → confidence 0.67
   - 전부 다름 → confidence 0.33

### 방법 B: `--method cross` (C-17 필요)
1. Claude EA + GPT EA 비교 결과 활용
2. MATCH → confidence 1.0
3. PARTIAL → confidence 0.7
4. MISMATCH → confidence 0.3

## 실행 절차

### Step 1: 대상 EA 로드
```
EA JSON 파일을 로드하고 각 항목의 기존 confidence 확인
```

### Step 2-A: 자체 반복 추출 (method=self)
```
Agent tool로 3개 독립 추출 에이전트 실행:
  - Agent 1: temperature=0.0으로 추출
  - Agent 2: temperature=0.3으로 추출
  - Agent 3: temperature=0.7로 추출

각 에이전트는 동일 SOT에서 동일 필드를 추출
```

### Step 2-B: 교차 모델 (method=cross)
```
/cross-model 결과 파일을 로드하여 비교 결과 활용
결과 파일이 없으면 /cross-model을 먼저 실행하라고 안내
```

### Step 3: Python 스크립트로 보정 계산
```bash
python D:\VAMOS\.claude\hooks\confidence_calibrator.py \
  --ea <EA파일> \
  --extractions <추출결과들.json> \
  --method self|cross \
  --output <보정된_EA.json>
```

### Step 4: 보고서 출력
```
## 신뢰도 보정 결과

| # | EA항목 | 필드 | 기존 conf | 보정 conf | 변화 | 조치 |
|---|--------|------|-----------|-----------|------|------|
| 1 | EA-001 | name | 0.95 | 1.00 | +0.05 | - |
| 2 | EA-003 | ver  | 0.90 | 0.33 | -0.57 | 재추출 필요 |

### 요약
- 보정 대상: N 항목
- 상향 조정: X건
- 하향 조정: Y건 (과신 탐지)
- 재추출 권장 (conf < 0.7): Z건
```

### Step 5: `--recalibrate` 옵션
기존 EA JSON의 confidence를 보정된 값으로 **직접 업데이트**.
원본은 `_backup` 접미사로 백업 후 덮어쓰기.

## 판정 기준
- **PASS**: 재추출 권장 항목(conf < 0.7) 비율 < 10%
- **WARN**: 재추출 권장 10~25%
- **FAIL**: 재추출 권장 > 25% → 해당 항목 일괄 재추출 필요

## 저장 위치
- 보정된 EA: `{원본EA경로}` (원본은 `{원본EA}_backup.json`으로 백업)
- 보정 보고서: `D:\VAMOS\04. 구현단계\{version}_results\{phase}\confidence_calibration.json`
