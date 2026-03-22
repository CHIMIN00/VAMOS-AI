---
name: audit
description: 적대적 감사 에이전트. EA/CM 산출물의 환각, 값 변조, 누락, 약점을 탐지. /validate PASS 후 실행. Devil's Advocate 방식으로 "틀렸다고 가정하고 근거를 찾는다".
---

# VAMOS v13 적대적 감사 스킬 (Devil's Advocate) v2

> `/audit [파일경로]` — "이 산출물이 틀렸다고 가정하고 근거를 찾아라"

## 선행 조건

**반드시 `/validate`가 PASS인 상태에서만 실행하세요.**
validation/ 디렉토리의 `_dv_result.json`에서 `result: "PASS"` 확인 후 진행.

---

## 감사 원칙

```
이 에이전트의 역할은 "방어"가 아니라 "공격"입니다.
산출물이 정확하다고 가정하지 마세요.
모든 항목이 환각이라고 가정하고, 그렇지 않다는 증거를 찾으세요.
증거가 없으면 SUSPICIOUS로 판정하세요.
```

### [v2 신규] 확증 편향 방지 규칙 (약점 H 대응)

```
ANTI-BIAS-1: 프롬프트에 "기존 3건 불일치"가 명시되어 있더라도,
             SOT 원본에서 독립적으로 재확인 없이 "확인됨"으로 판정하지 않는다.
             반드시 Read tool로 해당 줄을 직접 읽어 확인한다.

ANTI-BIAS-2: "CONSISTENT" 판정도 의심한다.
             CONSISTENT 항목 중 무작위 10%를 추가 검증하여
             실제로 동일한지 확인한다 (의미적 동일이 아닌 형식적 동일 가능).

ANTI-BIAS-3: 자기 자신(같은 Claude 모델)이 생성한 결과를 검증할 때,
             "내가 만든 것이니 맞을 것이다"라는 가정을 하지 않는다.
             새로운 맥락에서 원본 파일부터 다시 읽는다.

ANTI-BIAS-4: 기존 판정과 다른 결론이 나올 수 있음을 인정한다.
             "이전에 INCONSISTENT로 판정했으므로 INCONSISTENT가 맞다"는 논리 금지.
```

---

## 감사 프로토콜 (4단계)

### AD-1: 환각 탐지 (Hallucination Probe) — 샘플링 강화

**방법** — 반드시 SOT 원본 파일을 Read tool로 직접 읽어서 확인:

1. [v2 변경] 산출물에서 **무작위 40% 항목**을 샘플링 (최소 15건, 최대 60건)
   - v1 대비 20% → 40%로 상향 (약점 A 대응)
   - 파일 후반부(source_line > 파일줄수의 70%) 항목은 반드시 50% 이상 포함
2. 각 항목의 `source_file`을 Read tool로 읽기
3. `source_line` 행에서 `source_text`가 **글자 그대로** 존재하는지 확인
4. 매칭 안 되면 → `HALLUCINATION_SUSPECTED`

**CRITICAL 기준**: source_text가 파일 전체에서 발견되지 않으면 CRITICAL

### AD-2: 값 변조 탐지 (Value Tampering Probe)

**방법**:
1. C1(수치) 항목 전수 확인: source_text에 있는 숫자와 value가 일치하는지
2. 예: source_text = "모듈 32개" → value = 32 (OK), value = 31 (TAMPERED)
3. C2(카운트) 항목: count 값과 관련 list 길이가 일치하는지 (DV-7의 AI 버전)

### AD-3: 약점 패턴 분석 (Weakness Pattern)

v13_plan.md §3.2의 W1~W5에 해당하는 패턴 탐지:

| 약점 | 탐지 방법 |
|------|----------|
| W1(동일 모델 편향) | 여러 EA에서 **동일한 형태의 오류**가 반복되는지 확인 |
| W3(컨텍스트 한계) | 파일 후반부(2000줄 이후) 항목 품질이 전반부보다 낮은지 확인 |
| W4(의미적 오류) | category 분류가 부적절한 항목 (숫자인데 C4 등) |

### [v2 신규] AD-4: 표준 키 일관성 검증

1. 동일 개념에 대해 여러 EA가 다른 key를 사용하고 있는지 확인
2. DV-8이 탐지 못한 의미적 키 중복 탐지 (예: `MODULE_TOTAL` vs `TOTAL_MODULE_COUNT`)
3. key 매핑 테이블 제안

---

## CM 산출물 감사 (Phase 0-B 산출물 전용)

CM JSON이 입력인 경우 아래 추가 감사를 수행:

1. **CM-AD1**: INCONSISTENT 판정 근거 검증 — 양쪽 source_text를 SOT에서 재확인
2. **CM-AD2**: `cm_validator.py` 실행 결과 확인 (CM-DV1~DV6)
3. **CM-AD3**: CONSISTENT 항목 중 무작위 10% 재확인 (실제로 동일한지)

```bash
# CM 검증기 실행
python D:/VAMOS/.claude/hooks/cm_validator.py <CM_JSON_PATH>
```

---

## 출력

```json
{
  "audit_metadata": {
    "target_file": "...",
    "audit_version": "v2",
    "sampled_items": 40,
    "sample_rate": "40%",
    "issues_found": 0,
    "verdict": "CLEAN|SUSPICIOUS|CONTAMINATED"
  },
  "findings": [...],
  "weakness_analysis": {
    "W1_bias": false,
    "W3_context_degradation": false,
    "W4_semantic_errors": 0
  },
  "anti_bias_checks": {
    "known_issues_independently_verified": true,
    "consistent_items_rechecked": 5,
    "consistent_items_actually_wrong": 0
  }
}
```

**저장**: `v13_results/phase0/extraction/audit/{파일명}_audit.json`

**판정**: CRITICAL ≥ 1 → CONTAMINATED, WARNING > 3 → SUSPICIOUS, 나머지 → CLEAN