---
name: consensus
description: 동일 SOT 반복 추출 후 다수결 투표로 환각 의심 항목 탐지. CISC(Confidence-Integrated Self-Consistency) 기법 적용. 가중 다수결로 신뢰도 판정.
---

# VAMOS A-5 Consensus 스킬 (Self-Consistency Voting / CISC)

> `/consensus [SOT파일|EA번호] --rounds 3` — 반복 추출 + 다수결 투표로 환각 탐지

## 기반 기술

- **Self-Consistency Voting**: 동일 입력에 대해 N회 독립 추출 후 다수결로 최종값 결정
- **CISC (Confidence-Integrated Self-Consistency)**: 각 추출에 confidence 가중치를 부여하여 가중 다수결 수행

---

## 기능

1. 동일 SOT를 3~5회 반복 추출 -> 각 항목별 다수결 투표
2. 다수결 일치 = 높은 신뢰도, 불일치 = 환각 의심 -> 수동 확인
3. CISC: 각 추출에 confidence 가중치 부여 -> 가중 다수결

---

## 핵심 로직 예시

```
SOT 파일 A를 3회 독립 추출:
  1회차: MODULE_COUNT = 81
  2회차: MODULE_COUNT = 81
  3회차: MODULE_COUNT = 82  <- 불일치!
다수결: 81 (2/3) -> 최종값 81
불일치 항목: MODULE_COUNT -> 수동 확인 필요
```

---

## 기존 스킬과의 차이

| 스킬 | 방식 | 검증 대상 |
|------|------|----------|
| `/audit` AD-1 | 단일 에이전트가 샘플링 검증 (1회) | 추출된 항목의 정확성 |
| `/hallucination-check` | 전 항목 claim 분해 (1회) | claim 단위 사실 여부 |
| `/consensus` | **동일 추출을 N회 반복 → 다수결** | 추출 재현성/안정성 |

> `/consensus`는 "정확성"이 아니라 **"재현성"**을 검증합니다.
> 같은 SOT를 여러 번 추출했을 때 결과가 흔들리면 환각 가능성이 높습니다.

---

## 실행 절차

```
1. 대상 SOT 파일 또는 EA 번호 결정
   ↓
2. Agent tool로 N회(기본 3) 독립 추출 에이전트 실행
   - 각 에이전트는 별도 컨텍스트에서 실행
   - 서로의 결과를 참조하지 않음 (독립성 보장)
   ↓
3. 각 추출 결과의 동일 key별 value 수집
   ↓
4. 다수결 투표:
   - 전원 일치 → CONSENSUS (높은 신뢰)
   - 다수결 일치 → MAJORITY (중간 신뢰, 소수 값 기록)
   - 균등 분할 → SPLIT (낮은 신뢰, 수동 확인 필수)
   ↓
5. CISC 가중치 적용:
   - confidence가 높은 추출의 투표에 더 큰 가중치 부여
   - 가중치 합산으로 최종 판정
   ↓
6. 결과 저장
```

---

## 투표 판정 기준

| 상태 | 조건 | 신뢰도 |
|------|------|--------|
| CONSENSUS | 전원 일치 (N/N) | 높음 |
| MAJORITY | 다수결 일치 (>50%) | 중간 |
| SPLIT | 균등 분할 또는 전원 불일치 | 낮음 |

---

## 출력 형식

```json
{
  "consensus_metadata": {
    "target": "...",
    "rounds": 3,
    "total_keys": 0,
    "consensus": 0,
    "majority": 0,
    "split": 0,
    "verdict": "HIGH_CONFIDENCE|MODERATE|LOW_CONFIDENCE"
  },
  "voting_results": [
    {
      "key": "MODULE_COUNT",
      "votes": [
        {"round": 1, "value": 81, "confidence": 0.95},
        {"round": 2, "value": 81, "confidence": 0.92},
        {"round": 3, "value": 82, "confidence": 0.70}
      ],
      "status": "MAJORITY",
      "final_value": 81,
      "weighted_score": 0.89,
      "minority_values": [{"value": 82, "round": 3}]
    }
  ]
}
```

## 저장 위치

`v13_results/phase0/extraction/validation/{파일명}_consensus.json`

## 최종 판정 (verdict)

| 판정 | 조건 |
|------|------|
| LOW_CONFIDENCE | SPLIT >= 1 |
| MODERATE | MAJORITY > 5 |
| HIGH_CONFIDENCE | 나머지 (대부분 CONSENSUS) |

---

## $ARGUMENTS 처리

- `$ARGUMENTS`가 SOT 파일 경로면 -> 해당 SOT 반복 추출
- `$ARGUMENTS`가 EA 번호면 -> 해당 EA의 SOT를 반복 추출
- `$ARGUMENTS`에 `--rounds N`이 포함되면 -> 반복 횟수를 N으로 설정 (기본 3)
- `$ARGUMENTS`가 비어있으면 -> 가장 최근 EA의 SOT를 대상으로 실행
