---
name: golden-set
description: 검증 완료 산출물에서 정답 데이터셋(Golden Set) 자동 구축. GOLD 판정 + CLEAN 감사 항목 기반. Precision/Recall/F1로 추출 정확도 자동 측정.
---

# A-8 Golden Set 자동 구축

> `/golden-set [build|eval|status]` — 정답 데이터셋 구축 및 추출 정확도 측정

## 기반 기술

Golden Dataset 자동 구축

## 기능

- v8~v13의 검증 완료 산출물에서 "정답 데이터셋" 자동 구축
- 정답 기준: quality-gate **GOLD** 판정 + 적대적 감사 **CLEAN**인 항목
- 이 정답 데이터셋으로 이후 추출 결과의 정확도를 자동 측정

## 기존 스킬과의 차이

| 스킬 | 검증 방식 | 정답 기준 |
|------|----------|----------|
| `/validate` | 결정론적 스크립트 + AI 의미적 검증 | 스키마/구조 기준 |
| `/audit` | 적대적 감사 (Devil's Advocate) | "틀렸다고 가정" |
| `/golden-set` | **검증 완료 정답 데이터셋 대비 정량 비교** | GOLD+CLEAN 확정 항목 |

> `/validate`와 `/audit`는 "이 산출물이 맞는가"를 판단하고,
> `/golden-set`은 "이전에 확정된 정답과 얼마나 일치하는가"를 **수치(P/R/F1)**로 측정합니다.

---

## 핵심 로직

```
1. v13 EA 중 GOLD 판정 받은 항목 수집
2. 각 항목의 {key, value, source_file, source_line, source_text} 추출
3. SOT 원본에서 source_text 존재 확인 (결정론적 검증)
4. 확인된 항목 → golden_set.json 저장
5. 이후 /extract 결과를 golden_set과 비교:
   - Precision: 추출된 것 중 정답과 일치하는 비율
   - Recall: 정답 중 추출된 비율
   - F1: 종합 점수
```

## 서브커맨드

### build — 정답 데이터셋 구축

Python 훅으로 정답 데이터셋을 구축한다.

```bash
python "D:/VAMOS/.claude/hooks/build_golden_set.py" build
```

### eval [EA파일] — 추출 결과 평가

추출 결과를 정답과 비교하여 Precision/Recall/F1을 산출한다.

```bash
python "D:/VAMOS/.claude/hooks/build_golden_set.py" eval "$ARGUMENTS"
```

### status — 현재 정답 데이터셋 통계

```bash
python "D:/VAMOS/.claude/hooks/build_golden_set.py" status
```

## 실행 방법

### $ARGUMENTS 가 `build`인 경우:

1. Bash tool로 build 명령 실행
2. v13 EA 중 GOLD + CLEAN 항목 수집
3. SOT 원본에서 source_text 존재 확인
4. golden_set.json 저장

### $ARGUMENTS 가 `eval [EA파일]`인 경우:

1. 대상 EA 파일 경로를 추출
2. Bash tool로 eval 명령 실행
3. golden_set.json과 비교하여 Precision/Recall/F1 산출
4. 평가 결과 JSON 저장

### $ARGUMENTS 가 `status`인 경우:

1. Bash tool로 status 명령 실행
2. 현재 golden_set.json 통계 출력

### $ARGUMENTS 가 비어있는 경우:

- `status`와 동일하게 동작

## 산출물

**빌드 결과**: `v13_results/golden_set.json`

```json
{
  "golden_set_metadata": {
    "total_golden_items": 0,
    "source_eas": [],
    "build_date": "...",
    "sot_verified": true
  },
  "items": [...]
}
```

**평가 결과**: `v13_results/phase0/extraction/validation/{파일명}_golden_eval.json`

---

## 판정 기준 (eval 서브커맨드)

| 판정 | 조건 |
|------|------|
| **EXCELLENT** | F1 ≥ 0.95 |
| **GOOD** | F1 ≥ 0.85 |
| **ACCEPTABLE** | F1 ≥ 0.70 |
| **POOR** | F1 < 0.70 |

> build/status는 판정 없음. eval 시에만 F1 기반 판정이 적용됩니다.

---

## CAT-33 확장: 정답 데이터 재검증 (레거시 오류 탐지)

### `/golden-set reverify` — golden-set 정답의 SOT 대비 재검증

golden-set이 구축된 이후 SOT가 업데이트되었거나, 초기 검증이 불완전했을 때
기존 정답 데이터가 여전히 유효한지 재검증합니다.

```
1. golden_set.json 로딩
   ↓
2. 각 정답 항목에 대해 SOT 원본 재대조:
   a. source_file이 존재하는지 확인
   b. source_line이 유효한지 확인 (파일 줄 수 이내)
   c. source_text가 SOT에 실제 존재하는지 확인
   d. value가 SOT 원문과 여전히 일치하는지 확인
   ↓
3. 불일치 유형 분류:
   - STALE: SOT가 변경되어 golden-set과 불일치
     (예: SOT에서 "81개 모듈" → "83개 모듈"로 변경)
   - SHIFTED: source_line이 이동됨 (내용은 일치하나 위치 변경)
   - MISSING: source_text가 SOT에서 삭제됨
   - WRONG: golden-set 정답 자체가 처음부터 오류였음
     (GOLD+CLEAN 판정에도 불구하고 실제 SOT와 불일치)
   ↓
4. 정답 신뢰도 산출:
   - valid_ratio = 유효 항목 / 전체 항목
   - stale_ratio = STALE 항목 / 전체 항목
   ↓
5. 재검증 리포트 생성 + 자동 수정 옵션 제공
```

### 실행 방법

```bash
python "D:/VAMOS/.claude/hooks/build_golden_set.py" reverify
```

### 재검증 출력 형식

```json
{
  "reverify_metadata": {
    "golden_set_size": 0,
    "items_checked": 0,
    "timestamp": "2026-03-20T10:00:00",
    "sot_last_modified": "2026-03-19T10:00:00"
  },
  "results": {
    "valid": 0,
    "stale": 0,
    "shifted": 0,
    "missing": 0,
    "wrong": 0
  },
  "stale_items": [
    {
      "item_id": "golden_042",
      "key": "MODULE_COUNT",
      "golden_value": "81개 모듈",
      "current_sot_value": "83개 모듈",
      "source_file": "D2.0-01.md",
      "type": "STALE"
    }
  ],
  "reliability": "0%",
  "verdict": "VALID|NEEDS_UPDATE|UNRELIABLE"
}
```

### 판정 기준

| 판정 | 조건 |
|------|------|
| VALID | 유효 비율 ≥ 95% + WRONG 0건 |
| NEEDS_UPDATE | STALE/SHIFTED > 0 but WRONG = 0 |
| UNRELIABLE | WRONG > 0 또는 유효 비율 < 80% |

### 저장 위치
`v13_results/phase0/extraction/validation/golden_set_reverify.json`

### $ARGUMENTS 추가
- `reverify` → golden-set 정답 데이터 SOT 대비 재검증
