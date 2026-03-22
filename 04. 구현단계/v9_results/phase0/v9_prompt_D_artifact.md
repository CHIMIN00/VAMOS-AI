# v9-D: 누적 산출물 추적 검증 프롬프트

> **Pipeline**: VAMOS v9.0.0
> **관점 ID**: v9-D (Cumulative Artifact)
> **작성일**: 2026-03-07
> **대상 문서**: `VAMOS_구현가이드_PART2_구현단계.md` v20.4.0 (3,807줄)

---

## [1] HEADER

```
v9 SCOPE HEADER — Phase -1I 산출물
> v9 SCOPE: 문서 정합성/완전성/구현 가능성/수량 일관성/경로 정합성/의존성 순서/외부 의존성
> BOUNDARY: §7.5 중 "문서 검증 가능" 태그 항목만 범위 내
> OUT OF SCOPE: 코드 동작 검증, 성능 벤치마크, 보안 침투 테스트, 런타임 행위
> RULE-14: §7.5 "구현 후 검증" 항목 검출 시 → OUT_OF_SCOPE (FN 아님)
```

**관점**: v9-D — 누적 산출물 추적 (Cumulative Artifact Tracking)
**핵심 질문**: 각 STEP 완료 후 존재해야 할 파일 목록이 다음 STEP의 전제와 일치하는가?
**검출 대상**: 산출물 미생성 후 참조, Stage Gate와 GO/NO-GO 간 중복/누락

---

## [2] SCOPE — 검증 대상 범위

**포함 범위**:
- §2 V0 (line 59~1375): 6 STEP의 산출물 → 다음 STEP 전제
- §3 V1 (line 1377~1711): 6 Phase의 산출물 → 다음 Phase 전제
- §4 V2 (line 1713~2099): 3 Phase의 산출물 → 다음 Phase 전제
- §5 V3 (line 2101~2697): 3 Phase의 산출물 → 다음 Phase 전제
- §7.1~§7.4 GO/NO-GO (line 3564~3700): 62항목

**제외 범위**:
- 변경 이력 (line 3777~3807)
- §6 (횡단 상세 — 관점 A에서 횡단 의존성 검증)
- §7.5~§7.6 (크로스컷 검토, 산출물 파일 인덱스)

---

## [3] GT REFERENCE — 참조 Ground Truth

| GT | 파일 경로 | 용도 |
|----|----------|------|
| **GT-2** | `D:\VAMOS\04. 구현단계\v9_results\phase0\gt2_artifact_chain.json` | 18 Stage별 inputs/outputs/gate_conditions/gate_count |

**추가 참조**:
- `D:\VAMOS\04. 구현단계\v9_results\phase-1\v9_gate_mapping.json` — GO/NO-GO 62항목 ↔ Stage Gate 매핑

---

## [4] RULES — 적용 방어 규칙

| RULE | 규칙 요약 | 적용 이유 |
|------|----------|----------|
| **RULE-1** | 정규화 전체 경로 사용, 부분 매칭 금지 | 산출물 이름 비교 시 정확 매칭 |
| **RULE-2** | V 범위 한정자 먼저 확인 | 버전 간 산출물 이동을 누락으로 오판 금지 |
| **RULE-7** | 병렬 패턴 별도 분류 | V1-P6 병렬 실행 시 산출물 타이밍 |
| **RULE-9** | HTML 주석 허용 목록 자동 PASS | 의도적 차이 보호 |
| **RULE-11** | §6 + §7 포함 필수 | §7 GO/NO-GO 검증 |
| **RULE-14** | 코드 동작 → SKIP | §7.5 구현 후 검증 항목 제외 |

---

## [5] ALLOWLIST — 허용 목록

| 항목 | 허용 사유 |
|------|----------|
| V1-Phase 6 산출물 타이밍 | 병렬 실행이므로 Phase 3~5 산출물과 동시 생성 가능 |
| V1 → V2 전환 시 산출물 이월 | V1 완료 산출물 전체가 V2 전제. 개별 미매핑은 오류 아님 |

---

## [6] CHECK ITEMS — 구체적 검증 항목

### [D-1] Stage N → Stage N+1 산출물 체인 검증
Stage N 완료 시 존재해야 할 파일 목록이 Stage N+1의 전제(`inputs`)와 일치하는지 확인.

**절차**:
1. GT-2의 `stages` 배열을 순서대로 순회
2. Stage N의 `outputs` 누적 합집합 계산:
   - `cumulative_outputs(N) = outputs(1) ∪ outputs(2) ∪ ... ∪ outputs(N)`
3. Stage N+1의 각 `input` 항목이 `cumulative_outputs(N)`에 포함되는지 확인
4. 포함되지 않는 input:
   - 외부 전제조건인가? (환경 설정, 도구 설치 등) → PASS
   - 이전 Stage 산출물인가? → `REAL_ERROR` (산출물 미생성)
5. **버전 전환 지점** 특별 처리:
   - V0-STEP-6 → V1-Phase 1: V0 전체 산출물이 V1 전제
   - V1-Phase 6 → V2-Phase 1: V1 전체 산출물이 V2 전제
   - V2-Phase 3 → V3-Phase 1: V2 전체 산출물이 V3 전제

**검증 수**: 17개 전환 (18 Stage - 1) × 평균 5개 inputs = ~85건

### [D-2] GO/NO-GO 산출물 포괄성 검증
GO/NO-GO 항목이 해당 버전의 **모든** Stage 산출물을 포괄하는지 확인.

**절차**:
1. 버전별 GO/NO-GO 항목 수 확인:
   - §7.1 V0: 16항목
   - §7.2 V1: 21항목
   - §7.3 V2: 14항목
   - §7.4 V3: 11항목
   합계: 62항목
2. 각 버전의 전체 Stage outputs를 합산
3. GO/NO-GO 항목이 해당 버전의 주요 산출물을 커버하는지 매핑:
   - GO/NO-GO가 Stage Gate의 SUBSET인 경우: 정상 (상위 요약)
   - GO/NO-GO가 Stage Gate의 SUPERSET인 경우: 추가 항목 확인
   - UNIQUE 항목 (GO/NO-GO에만 존재): 별도 기록
4. 주요 산출물이 GO/NO-GO에 미포함: `MEDIUM`
5. 산출물이 아닌 항목이 GO/NO-GO에 포함: 문서 작업 등 → PASS

**참조**: `v9_gate_mapping.json`의 매핑 유형 (SUBSET, SUPERSET, UNIQUE)

### [D-3] 전환 조건 항목 수 일관성 검증
전환 조건(Stage Gate) 항목 수가 §2-§5 본문과 §7 GO/NO-GO에서 동일하게 표기되는지 확인.

**절차**:
1. §2-§5에서 각 Stage의 Gate 항목 수 확인 (GT-2의 `gate_count`)
2. §7.1-§7.4에서 GO/NO-GO 항목 수 확인
3. 대조:
   - 버전별 합산이 일치하는가?
   - Stage Gate 총합 vs GO/NO-GO 총합의 관계 설명이 문서에 있는가?
4. 불일치 시: 어느 쪽이 정확한지 GT-2 기준으로 판정

**참고 수치** (GT-2에서 확인):
- V0 Stage Gate: STEP 1~6 합산
- V1 Stage Gate: Phase 1~6 합산 (10+12+11+12+11+10=66)
- V2 Stage Gate: Phase 1~3 합산
- V3 Stage Gate: Phase 1~3 합산

### [D-4] §6 횡단 정의의 참조 시점 명확성
§6 횡단 정의가 "어느 Stage까지 완료되면 참조 가능"한지 명확한지 확인.

**절차**:
1. GT-2의 `cross_section_dependencies` 항목 순회
2. 각 §6 정의에 대해:
   - "이 정의를 참조하려면 어떤 Stage가 완료되어야 하는가?"가 문서에 명시되어 있는가?
   - 명시적이면: PASS
   - 암시적이면: `MEDIUM` (추론 가능하나 명확하지 않음)
   - 완전 불명확이면: `HIGH`
3. 특히 확인할 §6 정의:
   - §6.1.6 UI State Machine → V1-Phase 4 이전에 참조 가능한가?
   - §6.9 SDAR → V2-Phase 2 이전에 참조 가능한가?
   - §6.8 AI Investing → V1-Phase 6 이전에 참조 가능한가?

---

## [7] OUTPUT FORMAT — 결과 JSON 스키마

```json
{
  "perspective": "v9-D",
  "perspective_name": "누적 산출물 추적",
  "timestamp": "2026-MM-DDTHH:mm:ssZ",
  "target_doc": "VAMOS_구현가이드_PART2_구현단계.md v20.4.0",
  "gt_version": "gt2_artifact_chain.json",
  "rules_applied": ["RULE-1", "RULE-2", "RULE-7", "RULE-9", "RULE-11", "RULE-14"],

  "summary": {
    "total_checks": 0,
    "pass": 0,
    "real_error": 0,
    "false_positive": 0,
    "style_concern": 0,
    "out_of_scope": 0,
    "blocker": 0,
    "high": 0,
    "medium": 0,
    "low": 0
  },

  "cumulative_artifact_chain": [
    {
      "stage": "V0-STEP-N",
      "cumulative_output_count": 0,
      "new_outputs": [],
      "next_stage_inputs_satisfied": true,
      "unsatisfied_inputs": []
    }
  ],

  "go_nogo_coverage": {
    "V0": {"go_nogo_count": 16, "stage_gate_total": 0, "coverage": ""},
    "V1": {"go_nogo_count": 21, "stage_gate_total": 66, "coverage": ""},
    "V2": {"go_nogo_count": 14, "stage_gate_total": 0, "coverage": ""},
    "V3": {"go_nogo_count": 11, "stage_gate_total": 0, "coverage": ""}
  },

  "findings": [
    {
      "id": "D-xxx-nnn",
      "check_item": "D-1 | D-2 | D-3 | D-4",
      "stage": "V0-STEP-N | V1-Phase-N | ...",
      "line": 0,
      "description": "발견 내용 상세 기술",
      "expected": "GT-2 기준",
      "actual": "PART2 실제 상태",
      "severity": "BLOCKER | HIGH | MEDIUM | LOW",
      "classification": "REAL_ERROR | FALSE_POSITIVE | STYLE_CONCERN | OUT_OF_SCOPE",
      "rule_applied": "RULE-N (해당 시)"
    }
  ]
}
```

---

## [8] SEVERITY — 판정 기준

| 등급 | 기준 | 이 관점의 예시 |
|------|------|--------------|
| **BLOCKER** | 산출물 미생성 후 참조 (구현 불가) | Stage N+1이 Stage N에서 미생성된 파일을 import |
| **HIGH** | GO/NO-GO에서 핵심 산출물 누락 | 버전 완료 판정에 핵심 산출물이 검증 항목에 없음 |
| **MEDIUM** | 전환 조건 수 불일치, §6 참조 시점 모호 | Gate 항목 수 §2 vs §7 불일치, §6 정의 참조 시점 암시적 |
| **LOW** | 산출물 표기 불통일, 중복 기재 | 동일 산출물이 다른 표현으로 기재 |

---

## 실행 지시

1. D-1을 최우선 실행: 18개 Stage의 누적 산출물 체인 순차 추적
2. D-2는 D-1 완료 후 실행 (Stage 산출물 목록 필요)
3. D-3은 수치 대조이므로 독립 실행 가능
4. D-4는 관점 A의 A-4와 유사하나, 여기서는 "명확성" 관점에서 판단 (A-4는 "참조 가능성")
5. RULE-7 주의: V1-Phase 6 병렬 패턴에서 산출물 타이밍 오판 방지
6. 버전 전환 지점(V0→V1, V1→V2, V2→V3)에서 누적 산출물 이월 확인