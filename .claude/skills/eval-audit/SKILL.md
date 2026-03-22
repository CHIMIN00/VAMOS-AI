---
name: eval-audit
description: 평가 파이프라인 자체를 감사. golden-set 정답 오류, 평가 메트릭 편향, 검증 도구 거짓양성/음성률을 점검하여 "평가가 맞는지" 검증.
---

# VAMOS Eval-Audit 스킬 (평가의 평가)

> `/eval-audit [golden-set|metrics|tools|all]` — 평가 파이프라인 자체의 신뢰성 감사

## 이 스킬이 해결하는 문제

```
문제: golden-set 정답이 틀리면 → 정확한 추출을 FAIL로 판정 (역전)
문제: eval-ea 메트릭이 편향되면 → 특정 오류만 잡고 나머지 놓침
문제: validate DV 규칙에 버그 → 모든 검증 결과 신뢰 불가

해결: 평가 도구/데이터/메트릭 자체를 정기적으로 감사
```

---

## 기존 스킬과의 차이

| 스킬 | 대상 | 방향 |
|------|------|------|
| `/validate` | EA/CM 산출물 | 도구 → 산출물 검증 |
| `/eval-ea` | EA 추출 품질 | 메트릭으로 점수 산출 |
| `/eval-audit` | **도구/메트릭/정답 자체** | 평가 체계 → 평가 체계 검증 |

---

## 실행 절차

### `/eval-audit golden-set` — 정답 데이터 감사

```
1. golden-set JSON 로드
   ↓
2. 정답 항목 샘플링 (최소 10건 또는 전체의 20%)
   ↓
3. 각 정답을 SOT 원본에서 직접 재검증:
   - SOT에서 해당 값이 실제로 존재하는지 확인
   - 값이 변경되었는지 (SOT 업데이트 후 golden-set 미갱신)
   - 카테고리 분류가 올바른지
   ↓
4. 오류 발견 시:
   - STALE: SOT는 변경되었으나 golden-set은 구버전
   - WRONG: golden-set 정답 자체가 SOT와 불일치
   - AMBIGUOUS: SOT가 모호하여 정답이 하나로 확정 불가
   ↓
5. 감사 보고서 출력
```

### `/eval-audit metrics` — 평가 메트릭 편향 감사

```
1. 최근 eval-ea / ragas-eval 실행 결과 수집
   ↓
2. 메트릭별 분포 분석:
   - 모든 항목이 0.9+ → 메트릭이 너무 관대한가?
   - 특정 카테고리만 낮음 → 메트릭이 특정 유형에 편향?
   - faithfulness vs relevancy 괴리 → 메트릭 간 불일치?
   ↓
3. 알려진 오류 항목(audit에서 발견된)이 메트릭에서도 낮은 점수인지 확인
   - 오류인데 높은 점수 → 거짓 음성 (메트릭 실패)
   - 정확한데 낮은 점수 → 거짓 양성 (메트릭 과민)
   ↓
4. 메트릭 신뢰도 보고서 출력
```

### `/eval-audit tools` — 검증 도구 신뢰성 감사

```
1. validate DV-1~DV-9 규칙 목록 로드
   ↓
2. 각 규칙에 대해 테스트 케이스 자동 생성:
   - 통과해야 하는 정상 케이스 (true negative)
   - 실패해야 하는 오류 케이스 (true positive)
   ↓
3. 규칙 실행 → 기대 결과와 비교:
   - 정상인데 FAIL → 거짓 양성 (규칙 과민)
   - 오류인데 PASS → 거짓 음성 (규칙 누락)
   ↓
4. 규칙별 precision/recall 산출
5. 도구 신뢰성 보고서 출력
```

### `/eval-audit all` — 전체 감사

```
golden-set + metrics + tools 순차 실행 → 통합 보고서
```

---

## 출력 형식

```json
{
  "eval_audit_metadata": {
    "audit_type": "golden-set|metrics|tools|all",
    "timestamp": "2026-03-20T10:00:00",
    "scope": "전체|샘플"
  },
  "golden_set_audit": {
    "total_checked": 0,
    "stale": 0,
    "wrong": 0,
    "ambiguous": 0,
    "valid": 0,
    "reliability": "0%"
  },
  "metrics_audit": {
    "metrics_evaluated": ["faithfulness", "relevancy", "hallucination"],
    "false_negative_rate": "0%",
    "false_positive_rate": "0%",
    "bias_detected": []
  },
  "tools_audit": {
    "rules_tested": 0,
    "precision": 0.0,
    "recall": 0.0,
    "f1": 0.0,
    "buggy_rules": []
  },
  "verdict": "RELIABLE|NEEDS_UPDATE|UNRELIABLE"
}
```

## 저장 위치

`v13_results/phase0/extraction/validation/eval_audit_report.json`

---

## 판정 기준

| 판정 | 조건 |
|------|------|
| RELIABLE | golden-set 오류 0 + 메트릭 거짓률 < 5% + 도구 F1 > 0.9 |
| NEEDS_UPDATE | golden-set STALE > 0 또는 메트릭 거짓률 5~15% |
| UNRELIABLE | golden-set WRONG > 0 또는 메트릭 거짓률 > 15% 또는 도구 F1 < 0.7 |

---

## $ARGUMENTS 처리

- `$ARGUMENTS`가 `golden-set`이면 → 정답 데이터 감사
- `$ARGUMENTS`가 `metrics`이면 → 평가 메트릭 편향 감사
- `$ARGUMENTS`가 `tools`이면 → 검증 도구 신뢰성 감사
- `$ARGUMENTS`가 `all`이면 → 전체 감사
- `$ARGUMENTS`가 비어있으면 → `all` 실행
