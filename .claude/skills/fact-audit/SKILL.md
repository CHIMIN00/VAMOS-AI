---
name: fact-audit
description: 적응형 멀티에이전트 팩트 감사. 3개 역할(Auditor/Challenger/Judge)의 토론 구조로 EA 항목을 SOT에서 검증. ACL 2025 FACT-AUDIT 패턴.
---

# VAMOS v13 멀티에이전트 팩트 감사 스킬 (FACT-AUDIT) A-2

> `/fact-audit [EA파일경로]` — 3개 역할의 토론 구조로 EA 항목을 SOT에서 검증

## 기반 기술

**FACT-AUDIT 패턴 (ACL 2025 논문)**
3개 독립 에이전트가 역할별로 토론하여 편향을 감소시키는 구조.

---

## 기존 /audit과의 차이

| | /audit | /fact-audit |
|---|--------|-------------|
| 구조 | 하나의 AI가 "틀렸다고 가정하고 찾아라" | 3개 AI가 각자 역할로 토론 |
| 편향 | 단일 관점 (확증 편향 가능) | 역할 분리로 편향 감소 |
| 패턴 | Devil's Advocate | FACT-AUDIT (ACL 2025) |

---

## 3개 역할 (Agent tool로 분리)

### 1. Auditor (감사자)
EA 항목을 SOT에서 검증 시도. 각 항목에 대해 PASS/FAIL/UNCERTAIN 판정.

### 2. Challenger (반박자)
감사자의 "PASS" 판정을 반박 시도. "이 PASS가 틀렸을 수 있는 이유" 제시.

### 3. Judge (판정자)
감사자와 반박자의 근거를 비교하여 최종 CONFIRMED/OVERTURNED/NEEDS_REVIEW 판정.

---

## 선행 조건

**반드시 `/validate` Layer A가 PASS인 상태에서만 실행하세요.**
validation/ 디렉토리의 `_dv_result.json`에서 `result: "PASS"` 확인 후 진행.

---

## 실행 절차

```
1. EA JSON 로딩
   ↓
2. Agent tool로 Auditor 에이전트 실행:
   - 각 항목을 SOT에서 검증
   - PASS / FAIL / UNCERTAIN 판정
   ↓
3. Agent tool로 Challenger 에이전트 실행:
   - Auditor의 PASS 판정 항목을 받아 반박 시도
   - "이 PASS가 틀렸을 수 있는 이유" 제시
   ↓
4. Agent tool로 Judge 에이전트 실행:
   - Auditor의 PASS 근거 vs Challenger의 반박 근거를 비교
   - 최종 CONFIRMED / OVERTURNED / NEEDS_REVIEW 판정
   ↓
5. 결과 집계 및 저장
```

---

## 출력

```json
{
  "fact_audit_metadata": {
    "target_file": "...",
    "total_items_audited": 0,
    "auditor_pass": 0,
    "auditor_fail": 0,
    "challenger_overturns": 0,
    "judge_confirmed": 0,
    "judge_overturned": 0,
    "judge_needs_review": 0,
    "verdict": "CONFIRMED|DISPUTED|NEEDS_REVIEW"
  },
  "rounds": [...]
}
```

**저장**: `v13_results/phase0/extraction/validation/{파일명}_fact_audit.json`

**판정**: OVERTURNED >= 1 -> DISPUTED, NEEDS_REVIEW > 3 -> NEEDS_REVIEW, 나머지 -> CONFIRMED

---

## $ARGUMENTS 처리

- `$ARGUMENTS`가 파일 경로면 -> 해당 파일만 감사
- `$ARGUMENTS`가 비어있으면 -> 가장 최근 생성된 EA JSON 파일 감사
