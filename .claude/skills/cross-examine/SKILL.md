---
name: cross-examine
description: 에이전트 간 능동적 질문-답변 심문. /cross-match의 수동적 결과 비교를 넘어, "왜 이 값을 추출했는가?" 질문으로 추출 근거를 검증. MCF 기법 기반.
---

# VAMOS 교차심문(Cross-Examine) 스킬

> `/cross-examine [EA-01 EA-07]` — 에이전트 간 능동적 질문-답변 심문으로 추출 근거 검증

## 목적

단순 결과 비교(`/cross-match`)를 넘어, **"왜 이 값을 추출했는가?"** 질문을 통해
추출 근거 자체를 검증합니다. MCF(Multi-agent Collaborative Filtering) 기법 기반.

---

## /cross-match과의 차이

| 구분 | /cross-match | /cross-examine |
|------|-------------|----------------|
| 방식 | 두 EA의 **결과**만 비교 (수동적) | 한 에이전트가 다른 에이전트에게 **질문** (능동적) |
| 초점 | 값 일치/불일치 판정 | 추출 **근거**의 타당성 검증 |
| 출력 | CONSISTENT/INCONSISTENT | SUFFICIENT/INSUFFICIENT/CONTRADICTORY |

---

## 선행 조건

1. 비교 대상 EA JSON이 `/validate` Layer A PASS 상태
2. EA JSON이 `v13_results/phase0/extraction/`에 존재

---

## 실행 절차

```
1. 두 EA JSON 로딩
   ↓
2. 불일치 항목 또는 의심 항목 식별
   ↓
3. Agent tool로 Examiner 에이전트 실행: 불일치 항목에 대해 질문 목록 생성
   - "EA-01 item 5에서 MODULE_COUNT=81을 추출한 근거는?"
   - "source_text가 '모듈 수'인데 어떻게 81이라는 숫자를 도출했는가?"
   ↓
4. Agent tool로 Respondent 에이전트 실행: SOT 원본을 직접 읽고 각 질문에 답변
   ↓
5. Examiner가 답변 평가: SUFFICIENT / INSUFFICIENT / CONTRADICTORY
   ↓
6. INSUFFICIENT/CONTRADICTORY → 재추출 대상 목록에 추가
   ↓
7. 결과 저장
```

---

## $ARGUMENTS 처리

- `EA-01 EA-07` → 특정 EA 쌍 심문
- 비어있음 → 가장 최근 `/cross-match`에서 INCONSISTENT이 나온 쌍

---

## Output 스키마

```json
{
  "cross_examine_metadata": {
    "ea_pair": ["EA-01", "EA-07"],
    "total_questions": 0,
    "sufficient": 0,
    "insufficient": 0,
    "contradictory": 0,
    "re_extract_needed": []
  },
  "examinations": [...]
}
```

---

## 출력

**저장 위치**: `v13_results/phase0/cross_match/{EA쌍}_cross_examine.json`
