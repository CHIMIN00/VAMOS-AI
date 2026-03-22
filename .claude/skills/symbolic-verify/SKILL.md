---
name: symbolic-verify
description: EA JSON의 수치 제약조건을 CSP(제약충족문제)로 변환하여 결정론적 검증. AI 판단 0%. DV-7의 확장판. Python 내장 로직으로 7가지 제약 유형 검증.
---

# A-9 Symbolic Verify — Neuro-Symbolic Verification (NSVIF)

> `/symbolic-verify [EA파일|all]` — EA JSON 수치 제약조건의 CSP 변환 결정론적 검증

## 개요

EA JSON의 수치 제약조건을 제약충족문제(CSP)로 변환하여 결정론적으로 검증합니다.
Python 내장 로직만 사용하며 AI 판단이 0%입니다. DV-7(COUNT↔LIST 교차검증)의 확장판입니다.

- **기반 기술**: Neuro-Symbolic Verification (NSVIF)
- **AI 판단 비율**: 0% (완전 결정론적)

---

## 기존 스킬과의 차이

| 스킬 | 검증 방식 | AI 판단 비율 |
|------|----------|:-----------:|
| `/validate` Layer A (DV-1~DV-9) | Python 스크립트 개별 규칙 | 0% |
| `/validate` Layer B (SV-1~SV-3) | AI 의미적 판단 | 100% |
| `/symbolic-verify` | **제약조건을 CSP로 변환 → 일괄 결정론적 검증** | 0% |

> `/validate` Layer A의 DV-7(COUNT↔LIST 교차검증)을 **7가지 제약 유형으로 확장**합니다.
> DV가 "개별 규칙"이라면, symbolic-verify는 "제약 체계"로서 항목 간 관계를 포괄 검증합니다.

---

## 검증 가능한 제약 유형 (7가지)

| # | 유형 | 제약 내용 |
|---|------|-----------|
| 1 | 산술 제약 | categories 합계 = total_items_extracted = items 길이 |
| 2 | 범위 제약 | 0 < source_line ≤ 파일 줄 수 |
| 3 | 타입 제약 | value_type = "number" → isinstance(value, (int, float)) |
| 4 | 교차 제약 | COUNT 키의 value = 관련 LIST 키의 len(value) |
| 5 | 유일성 제약 | item_id 중복 없음 |
| 6 | 포함 제약 | LOCK 값이 다른 EA에서도 동일 |
| 7 | 논리 제약 | severity=CRITICAL이면 confidence > 0.9 |

---

## 구현

Python 내장 로직 (기본, symbolic_verifier.py 훅)

---

## 실행 절차

```
1. EA JSON 로딩
   ↓
2. Python 훅 실행:
   python "D:/VAMOS/.claude/hooks/symbolic_verifier.py" "<EA파일>"
   ↓
3. 결과 해석 및 출력
```

---

## 출력

```json
{
  "symbolic_verify_metadata": {
    "target_file": "...",
    "total_constraints": 0,
    "satisfied": 0,
    "violated": 0,
    "verdict": "PASS|FAIL"
  },
  "constraints": [...]
}
```

저장: `v13_results/phase0/extraction/validation/{파일명}_symbolic_verify.json`

---

## 판정

- `violated ≥ 1` → **FAIL**
- 나머지 → **PASS**

---

## $ARGUMENTS 처리

- `$ARGUMENTS`가 파일 경로면 → 해당 파일만 검증
- `$ARGUMENTS`가 `all`이면 → extraction/ 디렉토리의 모든 v13_EA*.json 검증
- `$ARGUMENTS`가 `bias-check`이면 → 검증 도구 다양성/편향 점검
- `$ARGUMENTS`가 비어있으면 → 가장 최근 생성된 EA JSON 파일 검증

---

## CAT-28 확장: 검증 도구 다양성 / 공통 편향 점검

### `/symbolic-verify bias-check` — 검증 계층 공통 편향 탐지

DV/SV/AD 검증 도구들이 공통 편향(동일 방향으로 쏠림)을 가지는지 점검합니다.

```
1. 모든 검증 결과 수집 (DV-1~DV-10, SV-1~SV-3, AD-1~AD-3)
   ↓
2. 검증 도구별 PASS/FAIL 분포 분석:
   - 특정 카테고리(C1~C8)에 집중 검증/방치 여부
   - 짧은 값 vs 긴 값에 대한 편향
   - 후반부 항목 vs 전반부 항목 탐지율 차이
   ↓
3. 공통 편향 탐지:
   - 모든 도구가 동일 항목을 놓치면 → COMMON_BLIND_SPOT
   - 3개 이상 도구가 같은 방향 편향 → SYSTEMATIC_BIAS
   - 특정 카테고리의 검증 커버리지 < 50% → UNDER_COVERED
   ↓
4. 독립성 점수 산출:
   - 도구 간 FAIL 상관계수 계산
   - 상관계수 > 0.9 → 두 도구가 사실상 같은 것만 잡음
   - 상관계수 < 0.3 → 독립적 (좋음)
   ↓
5. 편향 리포트 생성
```

### 편향 점검 출력 형식

```json
{
  "bias_check_metadata": {
    "tools_analyzed": ["DV-1", "DV-2", "...", "SV-1", "AD-1"],
    "total_items_checked": 0,
    "timestamp": "2026-03-20T10:00:00"
  },
  "common_blind_spots": [
    {
      "category": "C5",
      "items_missed_by_all": 3,
      "example_item": "...",
      "severity": "CRITICAL"
    }
  ],
  "systematic_biases": [
    {
      "bias_type": "LENGTH_BIAS",
      "direction": "짧은 값(< 10자)에 대해 검증 관대",
      "affected_tools": ["DV-4", "SV-1"],
      "magnitude": 0.82
    }
  ],
  "independence_matrix": {
    "DV-4_vs_SV-1": 0.87,
    "DV-7_vs_AD-1": 0.21
  },
  "diversity_score": 0.0,
  "verdict": "DIVERSE|PARTIALLY_BIASED|SYSTEMATICALLY_BIASED"
}
```

### 판정 기준

| 판정 | 조건 |
|------|------|
| DIVERSE | 공통 맹점 0 + 체계적 편향 0 + 독립성 평균 < 0.5 |
| PARTIALLY_BIASED | 공통 맹점 1~2 또는 독립성 평균 0.5~0.7 |
| SYSTEMATICALLY_BIASED | 공통 맹점 3+ 또는 체계적 편향 감지 |

### 저장 위치
`v13_results/phase0/extraction/validation/bias_check_report.json`
