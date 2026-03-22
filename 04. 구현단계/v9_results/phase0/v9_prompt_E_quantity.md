# v9-E: 수량 일관성 검증 프롬프트

> **Pipeline**: VAMOS v9.0.0
> **관점 ID**: v9-E (Quantity Consistency)
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

**관점**: v9-E — 수량 일관성 (Quantity Consistency)
**핵심 질문**: "17개 모듈", "44개 컴포넌트", "88개 API" 등 수치가 파일 내 모든 위치에서 동일한가?
**검출 대상**: 동일 수치의 위치별 불일치, LOCK 수치 vs ~근사치 구분 위반, §6.13 산술 오류

---

## [2] SCOPE — 검증 대상 범위

**포함 범위**:
- §1 개요 (line 1~57): 버전별 모듈 수 요약
- §2 V0 (line 59~1375): V0 관련 수량
- §3 V1 (line 1377~1711): V1 관련 수량
- §4 V2 (line 1713~2099): V2 관련 수량
- §5 V3 (line 2101~2697): V3 관련 수량
- §6 횡단 상세 (line 2699~3562): §6.1~§6.13 수량
- §7.1~§7.6 (line 3564~3775): GO/NO-GO 항목 수, 산출물 파일 수

**제외 범위**:
- 변경 이력 (line 3777~3807) — **절대 참조 금지** (과거 수치 혼입 방지, RULE-3)
- changelog 내 수치는 과거 버전 기준이므로 현행 값과 불일치해도 오류 아님

---

## [3] GT REFERENCE — 참조 Ground Truth

| GT | 파일 경로 | 용도 |
|----|----------|------|
| **GT-3** | `D:\VAMOS\04. 구현단계\v9_results\phase0\gt3_quantity_index.json` | 248개 수량 항목의 교차 인덱스 |

**GT-3 핵심 구조**:
- `_metadata.precision_summary`: EXACT_LOCK(89), EXACT_COUNT(112), APPROX(41), DERIVED(6)
- `cross_index`: 각 수치의 `value`, `precision`, `locations[]` (line, section, text)
- 정밀도 태그:
  - `EXACT_LOCK`: LOCK/FREEZE/ABSOLUTE → 정확 매칭 필수 (오차 0)
  - `EXACT_COUNT`: 명시적 카운트 → 정확 매칭 (오차 0)
  - `APPROX`: `~` 접두사 → ±20% 허용 범위
  - `DERIVED`: 합산/계산 → 산술 정확성 검증

**추가 참조**:
- `D:\VAMOS\04. 구현단계\v9_results\phase-1\v9_cross_section_index.json` — §6 헤더 수치 ↔ §6.13 교차표
- `D:\VAMOS\04. 구현단계\v9_results\phase-1\v9_config_13vs17_verdict.md` — config 13/17 확정 판정

---

## [4] RULES — 적용 방어 규칙

| RULE | 규칙 요약 | 적용 이유 |
|------|----------|----------|
| **RULE-2** | V0/V1/V2/V3 범위 한정자 먼저 확인 | V0 수치를 V1 수치와 직접 비교 금지 |
| **RULE-3** | changelog 제외. 인라인 주석 별도 컨텍스트 | line 3777-3807 절대 참조 금지. 과거 수치 혼입 차단 |
| **RULE-5** | 요약 vs 상세 구조적 차이 | §1 요약 수치 vs §3 상세 수치의 표현 차이 허용 |
| **RULE-8** | `~` 근사치 ±20% 허용. LOCK/FREEZE만 정확 매칭 | ~44는 35~53 허용, 18(FREEZE)는 정확히 18 |
| **RULE-11** | §6 + §7 포함 필수 | §6.13 매트릭스, §7 항목 수 검증 |
| **RULE-12** | §2-5 수치 ↔ §6 상세 수치 교차 검증 | 동일 항목의 두 영역 간 수치 일치 |
| **RULE-13** | §6 헤더 수치 ↔ §6.13 매트릭스 교차 검증 | §6.1 "~85" vs §6.13 UI/UX "~135" 차이 규명 |
| **RULE-14** | v9 범위 = 문서 정합성 | 코드 수준 카운트 제외 |

---

## [5] ALLOWLIST — 허용 목록

| 항목 | 허용 사유 |
|------|----------|
| §6.1 "~85" vs §6.13 UI/UX "~135" | 정의 범위 차이 (§6.1=V1 신규, §6.13=전체 누적). 차이 원인이 규명되면 PASS |
| config "13 vs 17" | Phase -1B 확정: TOML 섹션=13개, V1+=4개 추가=17개. 두 수치 모두 정확 |
| SC-01 (V0 활성 모듈 5 vs 6) | 5개 채택 확정. §2.8=6개는 과거 표기 |
| SC-10 (IPC 핸들러 47 vs 72) | 72개 채택 (CLAUDE.md 정본). §6.2.1=72 |
| APPROX 수치 전반 | ~접두사 수치는 ±20% 범위 내이면 PASS |

---

## [6] CHECK ITEMS — 구체적 검증 항목

### [E-1] EXACT_LOCK 수치 전수 검증
GT-3에서 `precision: "EXACT_LOCK"` 인 89개 항목의 모든 출현 위치에서 동일 값인지 확인.

**절차**:
1. GT-3의 `cross_index`에서 `precision == "EXACT_LOCK"` 항목 필터 (89건)
2. 각 항목의 `locations[]`에 명시된 모든 줄(line)에서:
   - PART2에서 해당 줄의 수치를 추출
   - GT-3의 `value`와 정확 일치 여부 확인
3. 불일치 발견 시: `HIGH` (LOCK 수치 불일치)
4. 모든 위치에서 일치 시: `PASS`

**예시**: `V1_active_modules: 32` — line 42, 1377, 2404에서 모두 32인지

### [E-2] EXACT_COUNT 수치 전수 검증
GT-3에서 `precision: "EXACT_COUNT"` 인 112개 항목의 모든 출현 위치에서 동일 값인지 확인.

**절차**: E-1과 동일하되, 대상은 112건
- 차이: EXACT_COUNT는 LOCK 태그 없으나 정확 매칭 요구
- 불일치 시: `HIGH`

### [E-3] APPROX 수치 범위 검증
GT-3에서 `precision: "APPROX"` 인 41개 항목에 대해, 동일 개념의 근사치가 ±20% 이내인지 확인.

**절차**:
1. GT-3에서 `precision == "APPROX"` 항목 필터 (41건)
2. 각 항목의 `locations[]` 수치들 간 비교:
   - 기준값: GT-3의 `value` (또는 최초 출현 값)
   - 각 위치 값이 기준값의 80%~120% 범위 내인가?
3. 범위 초과 시: `MEDIUM` (근사치 범위 위반)
4. 범위 내: `PASS`

**예시**: `~44`는 35~53 허용. line 1590에서 ~44, §6.1에서 ~44 → PASS

### [E-4] DERIVED 수치 산술 검증
GT-3에서 `precision: "DERIVED"` 인 6개 항목의 산술 합산/계산이 정확한지 확인.

**절차**:
1. GT-3에서 `precision == "DERIVED"` 항목 필터 (6건)
2. 각 항목의 산술식 검증:
   - 합산: A + B + C = D인지 확인
   - 곱셈/나눗셈: 산술 결과 일치 확인
3. 산술 오류 시: `HIGH`

**예시**: V3 활성 모듈 = V1(32) + V2(10) + V3(39) = 81 → line 2404에서 81인지

### [E-5] §6.13 매트릭스 산술 검증
§6.13 작업량 요약 매트릭스의 행 합계, 열 합계, 교차 합계 검증.

**절차**:
1. §6.13 매트릭스 위치 식별 (PART2 내)
2. **행 합계** 검증:
   - UI(~135) + 인프라(~108) + 테스트(~84) + CI(~14) + 도구(~19) + 보안(~15) + MCP(~7) + 기타(~72) = ~454
3. **열 합계** 검증:
   - V0(~41) + V1(~273) + V2(~92) + V3(~48) = ~454
4. **교차 검증**: 행 합계 = 열 합계 = ~454
5. 모든 합산은 APPROX이므로 ±20% 허용 (RULE-8)
6. 합산 불일치 시: `MEDIUM` (APPROX 수치의 산술 오류)

### [E-6] §6 헤더 수치 ↔ §6.13 교차 검증 (RULE-13)
§6 각 섹션 헤더의 수치와 §6.13 매트릭스 해당 행 합계가 일치하는지 확인.

**절차**:
1. [-1D] 교차 인덱스(`v9_cross_section_index.json`) 참조
2. 대조표:
   | §6 섹션 | 헤더 수치 | §6.13 행 합계 | 판정 |
   |---------|----------|--------------|------|
   | §6.1 UI/UX | ~85 | ~135 | **차이 존재** — 원인 규명 필요 |
   | §6.2 Rust/Tauri | ~108 | ~108 | 일치 예상 |
   | §6.3 테스트 | ~84 | ~84 | 일치 예상 |
   | §6.4 CI/CD | ~14 | ~14 | 일치 예상 |
   | §6.5 보안 | 15 | ~15 | 일치 예상 |
   | §6.6 MCP | ~7 | ~7 | 일치 예상 |
3. §6.1 "~85" vs §6.13 "~135" 차이 원인:
   - ~85 = V1 신규 항목만?
   - ~135 = V0+V1+V2+V3 누적?
   - 원인이 규명되면: `PASS` (allowlist), 규명 불가면: `HIGH`
4. 나머지 불일치 발견 시: `HIGH`

### [E-7] §2-5 수치 ↔ §6 상세 수치 교차 검증 (RULE-12)
§2-5에서 언급된 수치와 §6 상세 섹션의 수치가 동일 개념에 대해 일치하는지 확인.

**절차**:
1. GT-3에서 동일 개념이 §2-5와 §6 양쪽에 출현하는 항목 필터
2. 양쪽 수치 비교:
   - EXACT: 정확 일치
   - APPROX: ±20% 범위
3. 교차 불일치 시: `HIGH`

**예시**: V1-Phase 4 "React ~44개" ↔ §6.1.2 "~44개" → 일치 확인

### [E-8] §7 GO/NO-GO 항목 수 정확성 검증
§7.1-§7.4의 GO/NO-GO 항목 수가 정확한지 확인.

**절차**:
1. §7.1 V0 GO/NO-GO 항목을 직접 카운트
2. §7.2 V1 GO/NO-GO 항목을 직접 카운트
3. §7.3 V2 GO/NO-GO 항목을 직접 카운트
4. §7.4 V3 GO/NO-GO 항목을 직접 카운트
5. 기대값: 16 + 21 + 14 + 11 = 62
6. 실제 카운트와 비교:
   - 일치: PASS
   - 불일치: `HIGH` (문서 내 항목 수 표기 오류)

### [E-9] §7.6 산출물 파일 수 정확성 검증
§7.6 산출물 파일 인덱스의 파일 수가 43개인지 확인.

**절차**:
1. §7.6에서 산출물 파일 목록을 직접 카운트
2. 기대값: 43개
3. 실제 카운트와 비교:
   - 일치: PASS
   - 불일치: `MEDIUM`

---

## [7] OUTPUT FORMAT — 결과 JSON 스키마

```json
{
  "perspective": "v9-E",
  "perspective_name": "수량 일관성",
  "timestamp": "2026-MM-DDTHH:mm:ssZ",
  "target_doc": "VAMOS_구현가이드_PART2_구현단계.md v20.4.0",
  "gt_version": "gt3_quantity_index.json",
  "rules_applied": ["RULE-2", "RULE-3", "RULE-5", "RULE-8", "RULE-11", "RULE-12", "RULE-13", "RULE-14"],

  "summary": {
    "total_checks": 248,
    "by_precision": {
      "EXACT_LOCK": {"total": 89, "pass": 0, "fail": 0},
      "EXACT_COUNT": {"total": 112, "pass": 0, "fail": 0},
      "APPROX": {"total": 41, "pass": 0, "fail": 0},
      "DERIVED": {"total": 6, "pass": 0, "fail": 0}
    },
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

  "section_6_13_matrix": {
    "row_totals": {},
    "column_totals": {},
    "row_sum": 0,
    "column_sum": 0,
    "cross_check": "PASS | FAIL"
  },

  "section_6_header_vs_6_13": [
    {
      "section": "§6.N",
      "header_value": 0,
      "matrix_value": 0,
      "match": "MATCH | DIFF",
      "explanation": ""
    }
  ],

  "findings": [
    {
      "id": "E-xxx-nnn",
      "check_item": "E-1 ~ E-9",
      "quantity_id": "GT-3 cross_index key",
      "precision": "EXACT_LOCK | EXACT_COUNT | APPROX | DERIVED",
      "line": 0,
      "section": "§N.N",
      "description": "발견 내용 상세 기술",
      "expected": "GT-3 기준 값",
      "actual": "PART2 실제 값",
      "tolerance": "정확 | ±20%",
      "severity": "BLOCKER | HIGH | MEDIUM | LOW",
      "classification": "REAL_ERROR | FALSE_POSITIVE | STYLE_CONCERN",
      "rule_applied": "RULE-N (해당 시)"
    }
  ]
}
```

---

## [8] SEVERITY — 판정 기준

| 등급 | 기준 | 이 관점의 예시 |
|------|------|--------------|
| **BLOCKER** | LOCK 수치 불일치로 구현 불가 | FREEZE 스키마 필드 수 불일치 (구현 시 다른 스키마 생성) |
| **HIGH** | 정확 수치(LOCK/COUNT) 불일치 | V1 활성 모듈 32 vs 35, IPC 핸들러 47 vs 72 (SC-10 미적용 시) |
| **MEDIUM** | 근사치 범위 초과 또는 산술 오류 | ~44의 실제 출현값이 60 (±20% 초과), §6.13 행 합계 ≠ 열 합계 |
| **LOW** | 표기 불통일 (수치 자체는 동일) | "17개" vs "17 modules" 표현 차이, 단위 불통일 |

---

## 실행 지시

1. **GT-3 로드**: gt3_quantity_index.json을 전체 로드 후 248개 항목 목록화
2. **정밀도별 분류 실행**: E-1(LOCK) → E-2(COUNT) → E-3(APPROX) → E-4(DERIVED) 순서
3. **§6.13 독립 검증**: E-5는 PART2 §6.13을 직접 읽어 산술 검증 (GT-3과 무관하게)
4. **교차 검증**: E-6, E-7은 [-1D] 교차 인덱스 참조하여 실행
5. **카운트 검증**: E-8, E-9는 §7 영역을 직접 읽어 수동 카운트
6. RULE-3 주의: **changelog (line 3777-3807)의 수치를 현행 값으로 사용하지 않을 것**
7. RULE-8 주의: `~` 접두사 수치의 ±20% 허용 범위 준수
8. RULE-12/13 주의: §2-5 ↔ §6, §6 헤더 ↔ §6.13 교차 검증 필수
