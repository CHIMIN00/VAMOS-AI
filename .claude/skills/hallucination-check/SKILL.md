---
name: hallucination-check
description: EA JSON의 각 항목을 atomic claim 단위로 분해하여 SOT 원본에서 개별 검증. /audit AD-1의 학술적 강화판.
---

# VAMOS v13 환각 검증 스킬 (Atomic Claim Verification) v1

> `/hallucination-check [EA파일경로|all]` — EA 항목을 atomic claim으로 분해하여 SOT 원본에서 개별 fact 검증

## 선행 조건

**반드시 `/validate` Layer A가 PASS인 상태에서만 실행하세요.**
validation/ 디렉토리의 `_dv_result.json`에서 `result: "PASS"` 확인 후 진행.

---

## 핵심 원칙

```
기반 기술: LLM Hallucination Detection Script
기능: EA JSON의 각 항목을 atomic claim(원자적 주장) 단위로 분해,
      각 claim을 SOT 원본 파일에서 개별 검증,
      claim별 VERIFIED / UNVERIFIED / PARTIAL 판정.

/audit AD-1과의 차이:
  /audit AD-1  → 무작위 40% 샘플링 → source_text 존재 확인
  /hallucination-check → 전 항목을 claim 단위로 분해 → 개별 fact 검증

/audit AD-1이 "표본 검사"라면, /hallucination-check은 "전수 정밀 검사"입니다.
```

---

## 검증 프로토콜 (5단계)

### HC-1: EA JSON 로딩 및 전 항목 순회

1. 대상 EA JSON 파일을 Read tool로 읽기
2. `items` 배열의 **전체 항목**을 순회 대상으로 확보
3. 각 항목의 `source_file`, `source_line`, `source_text`, `key`, `value` 추출

### HC-2: Atomic Claim 분해

각 항목을 아래 atomic claim으로 분해:

| Claim ID | Claim 내용 | 검증 대상 |
|----------|-----------|----------|
| C-key | `key`가 source_text 맥락에서 적절한가 | 의미적 검증 |
| C-value | `value`가 source_text에서 도출 가능한가 | 의미적 검증 |
| C-src-exist | `source_text`가 SOT 원본 파일에 존재하는가 | 글자 대조 |
| C-src-line | `source_text`가 `source_line` 행에 존재하는가 | 위치 대조 |

→ 항목 1개당 최대 4개 claim 생성

### HC-3: SOT 원본 파일 읽기

1. 항목의 `source_file` 경로로 SOT 원본 파일을 Read tool로 읽기
2. 동일 파일을 참조하는 항목은 한 번만 읽고 캐시하여 재사용

### HC-4: Claim별 개별 검증

각 claim을 SOT 원본에서 검증하여 판정:

```
C-src-exist + C-src-line 판정 기준:
  - source_text가 source_line 행(±3줄)에 존재 → VERIFIED
  - source_text가 source_line이 아닌 다른 줄에 존재 → PARTIAL (위치 불일치)
  - source_text가 파일 전체에 없음 → UNVERIFIED (환각 의심)

C-value 판정 기준:
  - value가 source_text 맥락과 의미적으로 일치 → VERIFIED
  - value가 source_text에서 부분적으로만 도출 가능 → PARTIAL
  - value가 source_text와 무관하거나 모순 → UNVERIFIED

C-key 판정 기준:
  - key가 source_text의 개념을 정확히 반영 → VERIFIED
  - key가 source_text의 개념과 부분적으로 관련 → PARTIAL
  - key가 source_text의 개념과 무관 → UNVERIFIED
```

### HC-5: 결과 집계 및 저장

1. 전체 claim 수, VERIFIED/PARTIAL/UNVERIFIED 수 집계
2. 판정 기준 적용
3. 결과 JSON 저장

---

## 출력

```json
{
  "hallucination_check_metadata": {
    "target_file": "...",
    "total_items": 0,
    "total_claims": 0,
    "verified": 0,
    "partial": 0,
    "unverified": 0,
    "verdict": "CLEAN|SUSPICIOUS|CONTAMINATED"
  },
  "claims": [
    {
      "item_id": 1,
      "claim_type": "C-src-exist",
      "claim_description": "source_text가 SOT 원본에 존재하는가",
      "result": "VERIFIED|PARTIAL|UNVERIFIED",
      "evidence": "해당 줄 내용 또는 불일치 설명"
    }
  ]
}
```

**저장**: `v13_results/phase0/extraction/validation/{파일명}_hallucination_check.json`

**판정**:
- UNVERIFIED >= 1 → **CONTAMINATED**
- PARTIAL > 5 → **SUSPICIOUS**
- 나머지 → **CLEAN**

---

## $ARGUMENTS 처리

- `$ARGUMENTS`가 파일 경로면 → 해당 파일만 검증
- `$ARGUMENTS`가 `all`이면 → extraction/ 디렉토리의 모든 v13_EA*.json 검증
- `$ARGUMENTS`가 비어있으면 → 가장 최근 생성된 EA JSON 파일 검증
