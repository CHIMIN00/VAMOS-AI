# VAMOS v13 적대적 감사 스킬 에이전트 (Devil's Advocate)

> **용도**: `/audit [파일경로]` — EA 산출물에 대한 적대적 리뷰: 환각, 오류, 누락, 약점 탐지
> **전략**: S4(적대적 리뷰) + W1(동일 모델 편향) 대응
> **원칙**: "이 산출물이 틀렸다고 가정하고 근거를 찾아라"

---

## 감사 대상

$ARGUMENTS 가 제공되면 해당 파일만 감사합니다.
$ARGUMENTS 가 비어있으면 `D:\VAMOS\04. 구현단계\v13_results\phase0\` 하위의 모든 JSON 산출물을 감사합니다.

---

## 적대적 감사 프로토콜 (5단계)

### AD-1: 환각 탐지 (Hallucination Detection)

"AI가 파일에 없는 값을 만들어냈을 가능성"을 집중 탐지합니다.

**방법**:
1. 산출물의 `source_text`를 SOT 원본 파일에서 직접 검색 (정확한 문자열 매칭)
2. 매칭 실패 시 → `source_line` 근처 ±5줄에서 유사 텍스트 검색
3. 유사 텍스트도 없으면 → **HALLUCINATION_SUSPECTED** 판정
4. `value`가 source_text에서 논리적으로 도출 불가능하면 → **VALUE_FABRICATION** 판정

**CRITICAL 기준**: R4에 따라 2개 이상의 SOT 근거 없이 CRITICAL 판정된 항목

### AD-2: 누락 탐지 (Omission Detection)

"추출해야 했는데 빠진 항목"을 탐지합니다.

**방법**:
1. SOT 원본 파일을 직접 읽기
2. C1~C8 카테고리에 해당하는 값이 원본에 있으나 산출물에 없는지 확인
3. 특히 아래 패턴을 집중 탐지:
   - 숫자가 포함된 문장 (C1 누락)
   - "N개", "목록:" 패턴 (C2 누락)
   - LOCK, FREEZE, 임계값 패턴 (C7 누락)
   - "참조", "§" 패턴 (C8 누락)
4. 누락 발견 시 → **OMISSION** + 해당 원문 인용

### AD-3: 값 변조 탐지 (Value Tampering)

W2(JSON 조작) 약점 대응 — "숫자를 맞추려고 값을 바꿨을 가능성"

**방법**:
1. C1(수치) 항목의 value를 source_text와 직접 비교
2. source_text에 "32개"라고 되어있는데 value가 31이면 → **VALUE_TAMPERED**
3. C2(카운트) 항목에서 count와 list 길이 불일치 → **COUNT_MISMATCH**
4. 동일 key로 여러 EA에서 추출된 값이 다르면 → **CROSS_EA_CONFLICT**

### AD-4: 의미적 오류 탐지 (Semantic Error)

W4(의미적 오류 누락) 약점 대응

**방법**:
1. source_text의 맥락과 추출된 key/context가 실제로 의미가 통하는지 확인
2. 예: "COND 모듈 10개"에서 추출한 key가 `EXP_MODULE_COUNT`이면 → **SEMANTIC_MISMATCH**
3. category 분류가 적절한지 확인 (숫자인데 C4로 분류 등)
4. value_type과 실제 value 형태 불일치 → **TYPE_MISMATCH**

### AD-5: 약점 패턴 종합 분석

v13_plan.md §3.2의 W1~W5에 해당하는 패턴을 종합 탐지:

| 약점 | 탐지 방법 |
|------|----------|
| W1(동일 모델 편향) | 여러 EA에서 동일한 틀린 패턴이 반복되는지 확인 |
| W2(JSON 조작) | AD-3에서 탐지 |
| W3(컨텍스트 한계) | 파일 후반부(2000줄 이후) 항목의 추출 품질이 전반부보다 낮은지 확인 |
| W4(의미적 오류) | AD-4에서 탐지 |
| W5(과잉 오탐) | 이전 /validate 결과에서 WARNING 비율이 30% 초과 시 경고 |

---

## 출력 형식

```json
{
  "audit_metadata": {
    "audited_at": "2026-03-XX",
    "target_file": "v13_EA01_claude_md.json",
    "auditor": "Devil's Advocate Agent",
    "total_items_audited": 200,
    "issues_found": 0,
    "verdict": "CLEAN|SUSPICIOUS|CONTAMINATED"
  },
  "findings": [
    {
      "finding_id": "AD1-001",
      "type": "HALLUCINATION_SUSPECTED|OMISSION|VALUE_TAMPERED|SEMANTIC_MISMATCH|...",
      "severity": "CRITICAL|WARNING|INFO",
      "item_id": "EA-01_045",
      "description": "source_text not found in CLAUDE.md near line 45",
      "evidence": {
        "expected": "원본 파일 해당 라인 텍스트",
        "actual": "산출물의 source_text"
      },
      "sot_references": ["CLAUDE.md:45", "CLAUDE.md:46"],
      "recommendation": "source_text를 원본에서 재확인 필요"
    }
  ],
  "weakness_analysis": {
    "W1_bias_detected": false,
    "W2_tampering_detected": false,
    "W3_context_degradation": false,
    "W4_semantic_errors": 0,
    "W5_false_positive_rate": "N/A"
  }
}
```

**저장 경로**: `D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\audit\{원본파일명}_audit.json`

---

## 판정 기준

| 판정 | 기준 |
|------|------|
| **CLEAN** | CRITICAL 0건, WARNING ≤ 3건 |
| **SUSPICIOUS** | CRITICAL 0건, WARNING > 3건 |
| **CONTAMINATED** | CRITICAL ≥ 1건 |

---

## 실행 우선순위

1. AD-1(환각) → 가장 위험. 최우선 실행
2. AD-3(값 변조) → 숫자 정확도 영향
3. AD-2(누락) → 완전성 영향
4. AD-4(의미적) → 품질 영향
5. AD-5(약점 종합) → 마지막에 패턴 분석

**⚠️ CRITICAL 판정 시 반드시 2개 이상의 SOT 근거를 제시하세요 (R4 준수)**
