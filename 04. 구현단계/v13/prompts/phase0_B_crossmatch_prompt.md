# v13 Phase 0-B: 크로스 매칭 (8 에이전트, C1~C8 유형별)

> **버전**: v13.2.0 (2계층 검증 아키텍처 반영)
> **대화**: 대화 4 (1개 대화)
> **목표**: Phase 0-A에서 추출한 핵심 값을 C1~C8 유형별로 크로스 매칭하여 불일치 전수 탐지
> **성격**: 독립 추출(EA-1~15) 결과의 교차 비교. 불일치 후보 목록 생성.
> **선행 조건**: Phase 0-A 완료 + **quality-gate SILVER 이상** (EA-1~EA-15 전수)

---

## Pre-check Protocol

```
① 본 계획 파일 읽기: D:\VAMOS\04. 구현단계\v13_plan.md (§3.0 + §5 Phase 0 부분)
② 본 프롬프트 읽기: D:\VAMOS\04. 구현단계\v13\prompts\phase0_B_crossmatch_prompt.md
③ Phase 0-A 산출물 15개 전수 존재 확인:
   D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA01_claude_md.json
   D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA02_base_plan.json
   D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA03_master_spec.json
   D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA04_d20_01_02.json
   D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA05_d20_03_04.json
   D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA06_d20_05_06.json
   D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA07_d20_07_08.json
   D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA08_d21_schemas.json
   D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA09_phase_b1_b3.json
   D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA10_phase_b4_b7.json
   D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA11_spec_4.json
   D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA12_step7_spec.json
   D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA13_step7_guides.json
   D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA14_step7_rest.json
   D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA15_etc.json
④ [필수] 15개 EA 파일의 quality-gate 검증 결과 확인:
   D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\validation\
   → 15개 전수 SILVER 이상이어야 Phase 0-B 진입 가능
   → BRONZE/REJECT 파일이 있으면 Phase 0-A 재추출 필요
⑤ 15개 파일 전부 로드하여 전체 items 수 확인
⑥ 확인 완료 후 작업 시작
```

---

## 핵심 원칙: 환각/오류 방지 규칙

```
R1: 불일치 판정 시 반드시 양쪽 SOT 원문(source_text + source_line)을 인용한다
R2: 동일 key로 매칭한다. key가 다르지만 동일 개념이면 key 매핑 테이블 참조
R3: 불일치 판정 시 "의미적 동일" vs "형식적 차이" 구분 (예: "15분" vs "900초" = 의미적 동일)
R4: 값이 null인 항목은 "해당 SOT에서 미언급"으로 처리. 불일치로 판정하지 않음
R5: 동일 항목이 3개 이상 SOT에서 서로 다른 값이면 SOURCE_CONFLICT로 에스컬레이션
R7: [신규] EA 입력 데이터의 DV-1~DV-7 결정론적 검증이 통과된 상태여야 한다 (v13_plan §3.3)
R8: [신규] quality-gate GOLD/SILVER 필수 — BRONZE/REJECT EA는 크로스 매칭에 사용하지 않는다
```

---

## 스킬 에이전트 실행 규칙

> 8개 CM 에이전트는 **독립적이므로 전부 병렬 실행 가능**합니다.

1. **전체 병렬**: CM-1~CM-8을 Agent tool로 동시 투입
2. **입력 공유**: 15개 EA JSON을 각 CM 에이전트에 전달 (각 에이전트가 직접 파일 읽기)
3. **출력 분리**: 각 CM 에이전트가 개별 JSON 산출물 생성
4. **key 기반 매칭**: Phase 0-A의 표준 key로 동일 개념 매칭

---

## 크로스 매칭 방법론

### Step 1: key 기반 자동 매칭
- EA-1~15의 모든 items에서 동일 `key`를 가진 항목을 그룹핑
- 같은 key를 가진 항목이 2개 이상 → 값 비교

### Step 2: 값 비교 규칙
| 상황 | 판정 |
|------|------|
| 값이 완전 동일 | `CONSISTENT` |
| 값이 다르지만 의미적으로 동일 (단위 변환 등) | `CONSISTENT` + `note` |
| 값이 다르고 의미도 다름 | `INCONSISTENT` |
| 한쪽만 존재 (다른 SOT에서 미언급) | `SINGLE_SOURCE` (불일치 아님) |
| 3개 이상 SOT에서 서로 다른 값 | `SOURCE_CONFLICT` |

### Step 3: 심각도 분류
| 심각도 | 기준 |
|--------|------|
| `CRITICAL` | LOCK/FREEZE 값 불일치, 또는 구현에 직접 영향 |
| `WARNING` | 카운트/목록 불일치, 분류 체계 충돌 |
| `INFO` | 명칭 변형, 범위 표현 차이 (의미 동일 가능) |

---

## CM 에이전트 8개 상세

### CM-1: C1 동일 값 크로스 비교 (수치/파라미터)

**매칭 대상**: EA-1~15에서 `category: "C1"` 인 모든 items
**핵심 작업**:
1. 동일 key의 수치 값 비교 (예: `TOTAL_MODULE_COUNT` 가 여러 SOT에서 다른 값인지)
2. 수치 단위 통일 후 비교 (분→초, 원→만원 등)
3. 허용 오차: 0 (정확히 일치해야 CONSISTENT)

**기존 불일치 검증 포인트**:
- ⚠️ 불일치 A 관련: `IMMUTABLE_ZONE_COUNT`(EA-1) vs `NEVER_AUTO_COUNT`(EA-1, EA-11) 비교
- 7 vs 10 차이의 원인: 정책 수준 7 vs 시행 수준 10

**산출물**: `D:\VAMOS\04. 구현단계\v13_results\phase0\cross_match\v13_CM01_values.json`

---

### CM-2: C2 카운트 불일치 (요약 vs 상세)

**매칭 대상**: EA-1~15에서 `category: "C2"` 인 모든 items
**핵심 작업**:
1. COUNT 키 (예: `COND_MODULE_COUNT=10`) vs LIST 키 (예: `COND_MODULE_LIST=[...]`) → list.length == count 확인
2. 요약 테이블의 수 vs 상세 목록의 실제 수 비교
3. 동일 개념의 카운트가 여러 SOT에서 다른지 비교

**기존 불일치 검증 포인트**:
- ⚠️ 불일치 B 관련: `COND_PRIORITY_MEDIUM`(PART2 요약=9) vs (PART2 상세=8), `COND_PRIORITY_LOW`(요약=3 vs 상세=4)

**산출물**: `D:\VAMOS\04. 구현단계\v13_results\phase0\cross_match\v13_CM02_counts.json`

---

### CM-3: C3 분류 체계 충돌

**매칭 대상**: EA-1~15에서 `category: "C3"` 인 모든 items
**핵심 작업**:
1. 동일 대상(예: "모듈")의 분류 체계가 SOT마다 다른지 비교
2. tier 수, tier 명칭, tier 내 항목 수 비교
3. 분류 기준이 다른 경우(활성화 시점 vs 원본 출처) 명시

**기존 불일치 검증 포인트**:
- ⚠️ 불일치 C 관련: `MODULE_TIER_SYSTEM`이 3-tier(PART2) vs 4-tier(CLAUDE.md)

**산출물**: `D:\VAMOS\04. 구현단계\v13_results\phase0\cross_match\v13_CM03_taxonomy.json`

---

### CM-4: C4 명칭 불일치

**매칭 대상**: EA-1~15에서 `category: "C4"` 인 모든 items
**핵심 작업**:
1. 동일 모듈/시스템/기능의 이름이 SOT마다 다른지 비교
2. 약어 vs 정식 명칭 (예: "DE" vs "Decision Engine") = CONSISTENT
3. 완전히 다른 이름 (예: "Decision Engine" vs "Condition & Decision Engine") = INCONSISTENT

**매칭 규칙**:
- 문자열 유사도가 아닌 **맥락 기반 동일성** 판단
- 동일 섹션/위치에서 같은 역할을 하는 명칭이면 동일 대상

**산출물**: `D:\VAMOS\04. 구현단계\v13_results\phase0\cross_match\v13_CM04_names.json`

---

### CM-5: C5 범위 불일치

**매칭 대상**: EA-1~15에서 `category: "C5"` 인 모든 items
**핵심 작업**:
1. 동일 개념의 범위(포함하는 항목 집합)가 SOT마다 다른지 비교
2. 부분집합 관계 확인: A ⊂ B 이면 범위 차이 명시

**기존 불일치 검증 포인트**:
- ⚠️ 불일치 A 관련: 불변구역(7개) ⊂ NEVER_AUTO(10개) — 추가 3개: `escalate_own_privilege`, `guardrails`, `gate`

**산출물**: `D:\VAMOS\04. 구현단계\v13_results\phase0\cross_match\v13_CM05_scope.json`

---

### CM-6: C6 버전 범위 불일치

**매칭 대상**: EA-1~15에서 `category: "C6"` 인 모든 items
**핵심 작업**:
1. 동일 모듈/기능의 활성화 버전이 SOT마다 다른지 비교
2. "V2+" vs "V2/V3" = 의미적 동일 → CONSISTENT
3. "V1" vs "V2" = 명확한 차이 → INCONSISTENT

**산출물**: `D:\VAMOS\04. 구현단계\v13_results\phase0\cross_match\v13_CM06_versions.json`

---

### CM-7: C7 수식/임계값 불일치

**매칭 대상**: EA-1~15에서 `category: "C7"` 인 모든 items
**핵심 작업**:
1. 동일 파라미터의 LOCK/FREEZE 값이 SOT마다 다른지 비교
2. 타임아웃, 비용 상한, 임계값 등 구현에 직접 영향을 미치는 값 비교
3. LOCK 값 불일치 = 무조건 CRITICAL

**산출물**: `D:\VAMOS\04. 구현단계\v13_results\phase0\cross_match\v13_CM07_thresholds.json`

---

### CM-8: C8 참조 무결성

**매칭 대상**: EA-1~15에서 `category: "C8"` 인 모든 items
**핵심 작업**:
1. 참조하는 §번호, 파일명, ID가 실제 존재하는지 확인
2. EA-1~15 전체 items의 source_file 목록과 크로스 체크
3. 존재하지 않는 참조 = INCONSISTENT

**참조 확인용 파일**: PART2 v26.0.0
- 경로: `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` (6,139줄)

**산출물**: `D:\VAMOS\04. 구현단계\v13_results\phase0\cross_match\v13_CM08_references.json`

---

## CM 산출물 JSON 구조 (공통)

```json
{
  "metadata": {
    "agent": "CM-{N}",
    "category": "C{N}",
    "version": "v13",
    "created": "2026-03-XX",
    "total_comparisons": 0,
    "results": {
      "CONSISTENT": 0,
      "INCONSISTENT": 0,
      "SOURCE_CONFLICT": 0,
      "SINGLE_SOURCE": 0
    },
    "severity": {
      "CRITICAL": 0,
      "WARNING": 0,
      "INFO": 0
    }
  },
  "comparisons": [
    {
      "comparison_id": "CM-{N}_{seq:3자리}",
      "key": "IMMUTABLE_ZONE_COUNT",
      "result": "INCONSISTENT",
      "severity": "WARNING",
      "sources": [
        {
          "ea_agent": "EA-1",
          "item_id": "EA-01_003",
          "source_file": "CLAUDE.md",
          "source_line": 45,
          "source_text": "7개 불변 구역",
          "value": 7
        },
        {
          "ea_agent": "EA-1",
          "item_id": "EA-01_027",
          "source_file": "CLAUDE.md",
          "source_line": 312,
          "source_text": "NEVER_AUTO 10개",
          "value": 10
        }
      ],
      "analysis": "불변구역(7) ⊂ NEVER_AUTO(10). 정책 수준 vs 시행 수준 차이. 동일 문서 내 혼재.",
      "recommendation": "범위 구분 명시 필요"
    }
  ]
}
```

---

## 산출물 전수 목록

| # | 에이전트 | 유형 | 산출물 경로 |
|---|----------|------|------------|
| 1 | CM-1 | C1 동일 값 | `v13_results/phase0/cross_match/v13_CM01_values.json` |
| 2 | CM-2 | C2 카운트 | `v13_results/phase0/cross_match/v13_CM02_counts.json` |
| 3 | CM-3 | C3 분류 | `v13_results/phase0/cross_match/v13_CM03_taxonomy.json` |
| 4 | CM-4 | C4 명칭 | `v13_results/phase0/cross_match/v13_CM04_names.json` |
| 5 | CM-5 | C5 범위 | `v13_results/phase0/cross_match/v13_CM05_scope.json` |
| 6 | CM-6 | C6 버전 | `v13_results/phase0/cross_match/v13_CM06_versions.json` |
| 7 | CM-7 | C7 임계값 | `v13_results/phase0/cross_match/v13_CM07_thresholds.json` |
| 8 | CM-8 | C8 참조 | `v13_results/phase0/cross_match/v13_CM08_references.json` |

---

## 완료 시 수행

```
1. CM-1 ~ CM-8 산출물 8개 파일 전수 존재 확인
2. 유형별 불일치 요약 테이블 출력:
   | CM | CONSISTENT | INCONSISTENT | SOURCE_CONFLICT | CRITICAL | WARNING | INFO |
3. 기존 3건 불일치 재확인:
   - 불일치 A (불변구역 7 vs NEVER_AUTO 10): CM-1 또는 CM-5에서 탐지 확인
   - 불일치 B (COND MEDIUM 9 vs 8): CM-2에서 탐지 확인
   - 불일치 C (3-tier vs 4-tier): CM-3에서 탐지 확인
4. 신규 불일치 건수 집계
5. CRITICAL 건수가 0이면 INFO로, 1건 이상이면 다음 Phase로 전달
6. [신규] 불일치 항목의 source_text/source_line 원문 대조 (DV-4 수준 검증):
   - 각 INCONSISTENT 항목의 source_text가 실제 SOT 원문과 일치하는지 확인
   - 불일치 판정 근거가 환각이 아닌지 grep으로 재확인
7. [신규] /quality-gate 실행 권장: CM 산출물에 대해 /validate 실행하여 스키마 검증
```

---

## 2계층 검증 아키텍처 연동

### Layer A (결정론적 검증) — Phase 0-B 진입 전 완료 필수

Phase 0-B는 Phase 0-A의 EA 산출물을 입력으로 사용합니다. 따라서:

1. **진입 게이트**: 15개 EA 전수가 `deterministic_validator.py` (DV-1~DV-7) 통과 상태
2. **quality-gate 등급**: 15개 EA 전수가 GOLD 또는 SILVER
3. **미달 시 조치**: BRONZE/REJECT EA가 있으면 Phase 0-A 재추출 → quality-gate 재실행

### Layer B (AI 의미적 검증) — CM 산출물 검증

CM 산출물(비교 결과)은 EA와 다른 구조이지만, 아래 검증을 적용합니다:

1. **SV 수준 검증**: 각 INCONSISTENT 판정의 source_text가 실제 SOT 원문과 일치하는지 확인
2. **환각 탐지**: source_line으로 SOT 원본 행을 직접 읽어 source_text 대조
3. **/validate 실행 권장**: CM JSON 스키마 및 내부 정합성 검증

### 검증 스킬 활용

| 시점 | 스킬 | 용도 |
|------|------|------|
| Phase 0-B 진입 전 | `/quality-gate EA파일` | EA 입력 품질 확인 |
| CM 산출물 생성 후 | `/validate CM파일` | CM JSON 스키마 검증 |
| 불일치 항목 확인 시 | `/sot-check EA\|key` | SOT 원본 직접 대조 |

---

## AI 오류 방지 규칙 (이 Phase에서 준수)

1. **환각 금지**: 비교 결과는 반드시 양쪽 source_text 원문 인용으로 뒷받침
2. **의미적 동일 주의**: 단위 변환, 약어 확장 등 형식적 차이는 CONSISTENT로 판정
3. **null 처리**: 한쪽만 있는 값은 `SINGLE_SOURCE`로 처리. 불일치로 판정하지 않음
4. **SOURCE_CONFLICT 엄격 적용**: 3개 이상 SOT에서 서로 다른 값일 때만 적용
5. **CRITICAL 남발 금지**: LOCK/FREEZE 값 불일치 또는 구현 직접 영향일 때만 CRITICAL
6. **자동 매칭 한계 인식**: key가 다르지만 동일 개념인 경우를 놓칠 수 있음 → CM 에이전트는 key뿐 아니라 context 기반으로도 유사 항목 탐색
7. **[신규] DV-4 수준 사실 확인**: INCONSISTENT 판정 시 양쪽 source_text를 SOT 원본에서 grep으로 재확인 — AI 비교 결과도 검증 대상
8. **[신규] Layer A 통과 입력만 사용**: quality-gate BRONZE/REJECT EA는 크로스 매칭 입력에서 제외

---

## 🔍 사용자 확인 체크리스트 (Phase 0-B 완료 시 Claude가 생성)

> **Claude는 CM-1~CM-8 전수 완료 후 아래 형식의 체크리스트를 사용자에게 제출합니다.**

### Claude 작성 규칙

```
═══════════════════════════════════════════════════
🔍 사용자 확인 체크리스트 (Phase 0-B 완료)
═══════════════════════════════════════════════════

■ 확인 항목 1: INCONSISTENT 판정 근거 스팟 체크 (5건)
  [확인1-1] CM-{N} / key: {key명}
            판정: INCONSISTENT ({severity})
            근거 A: 파일 {source_file_A}, 행 {line_A}
                    → 텍스트: "{source_text_A 앞 40자}"
            근거 B: 파일 {source_file_B}, 행 {line_B}
                    → 텍스트: "{source_text_B 앞 40자}"
            → 각 파일을 열어 해당 행에 텍스트가 있는지 확인
            → 양쪽 다 있으면 ✅, 한쪽이라도 없으면 ❌ (환각)

  [확인1-2] ... (총 5건, CRITICAL 우선 선택)

■ 확인 항목 2: 기존 3건 불일치 탐지 확인
  [확인2-1] 불일치 A (불변구역 7 vs NEVER_AUTO 10)
            → CM-1 또는 CM-5에서 탐지됨: ✅/❌
            → 탐지된 comparison_id: ___
  [확인2-2] 불일치 B (COND MEDIUM 9 vs 8)
            → CM-2에서 탐지됨: ✅/❌
  [확인2-3] 불일치 C (3-tier vs 4-tier)
            → CM-3에서 탐지됨: ✅/❌

■ 확인 항목 3: CM 결정론적 검증 결과
  [확인3-1] CM-1: /validate 결과 → PASS/WARN/FAIL
  [확인3-2] CM-2: /validate 결과 → PASS/WARN/FAIL
  ... (8건 전수)

■ 확인 항목 4: 가장 의심스러운 INCONSISTENT 1건 직접 확인
  Claude가 "가장 확증 편향 위험이 높은" INCONSISTENT 1건을 선택하여 제시:
  [확인4-1] CM-{N} / key: {key}
            → 사용자가 직접 SOT 파일 2개를 열어서
            → 파일A {path}, 행 {line}에서 값 확인: ___
            → 파일B {path}, 행 {line}에서 값 확인: ___
            → 실제로 불일치가 맞으면 ✅, 같은 값이면 ❌ (오판)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ 가 하나라도 있으면 해당 CM 재실행 또는 수정 요청.
모두 ✅ 이면 Phase 0-CDF로 진행합니다.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 확인 항목 선택 기준

- **확인1**: CRITICAL 판정 우선, 없으면 WARNING에서 무작위 5건. 양쪽 source_text 모두 제시.
- **확인2**: 기존 3건은 반드시 포함. 탐지 안 됐으면 ❌ → 재검토 필요.
- **확인3**: `cm_validator.py` 결과를 그대로 인용.
- **확인4**: Claude가 "내가 가장 자신 없는 판정"을 솔직하게 1건 선택하여 제시.
