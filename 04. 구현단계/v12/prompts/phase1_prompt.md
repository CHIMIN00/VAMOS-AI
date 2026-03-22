# Phase 1: SOT Feature → PART2 전수 매핑

> **대화**: 대화 6~7 (2개 대화에 분산)
> **목표**: v12 Feature Registry의 모든 extractable=true 항목을 PART2 v25.2.0에 매핑 → MATCHED/MISSING 판정
> **성격**: 누락 탐지의 핵심 단계. 매핑 정확도가 전체 파이프라인 품질을 결정.
> **선행 조건**: Phase 0 PASS (Feature Registry Final + 인덱스 구축 완료)

---

## Pre-check Protocol

**매 대화(대화 6/7) 시작 시 반드시 수행:**

```
① 본 계획 파일 읽기: D:\VAMOS\04. 구현단계\v12\v12_plan.md
② 본 프롬프트 읽기: D:\VAMOS\04. 구현단계\v12\prompts\phase1_prompt.md
③ 진행 상태 확인: D:\VAMOS\04. 구현단계\v12\v12_results\v12_phase_status.json
④ Phase 0 PASS 확인 (FAIL이면 Phase 1 진행 불가)
⑤ Phase 0 핵심 산출물 로드:
   - v12_feature_registry_final.json (Feature Registry)
   - v12_section_map.json (섹션 인덱스)
   - v12_reference_map.json (참조 인덱스)
   - v12_numeric_registry.json (수치 인덱스)
   - v12_prompt_inventory.json (프롬프트 인덱스)
   - v12_s6_mapping.json (§6 예비 매핑)
⑥ 대화 6: 전체 Feature 통계 확인 (총 건수, extractable=true 건수)
   대화 7: 대화 6 산출물 (M-1~M-3) 존재 확인 + 통계 대조
⑦ 확인 완료 후 작업 시작
```

---

## 스킬 에이전트 실행 규칙

> **필수**: 본 Phase의 작업 단위는 반드시 **Agent tool(스킬 에이전트)**을 사용하여 병렬 실행합니다.

1. **병렬 실행**: 독립적인 작업 단위(M-에이전트)는 Agent tool로 동시 투입
2. **동일 템플릿**: 모든 에이전트는 본 프롬프트에 정의된 출력 템플릿을 준수
3. **결과 통합**: 개별 에이전트 결과를 취합하여 교차검증 수행
4. **재현성**: 동일 입력 → 동일 출력 보장을 위해 에이전트별 명확한 범위 지정

---

## 입력 파일

### Phase 0 산출물 (필수)

| # | 파일 | 경로 |
|---|------|------|
| 1 | Feature Registry Final | `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_feature_registry_final.json` |
| 2 | Section Map | `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_section_map.json` |
| 3 | Reference Map | `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_reference_map.json` |
| 4 | Prompt Inventory | `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_prompt_inventory.json` |
| 5 | §6 예비 Mapping | `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_s6_mapping.json` |
| 6 | Numeric Registry | `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_numeric_registry.json` |

### PART2 대상

| 파일 | 경로 |
|------|------|
| PART2 구현단계 v25.2.0 | `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` |

---

## 스킬 에이전트 패턴

| 패턴 | 출처 | 적용 |
|------|------|------|
| 6개 매핑 에이전트 | v10 Phase 1 M-1~M-5b | M-1~M-5b (구조 계승, 범위 확장) |
| 신규 M-6 | v12 신규 | §1 + §7(변경이력) + 프롬프트 내부 참조 |
| 정본 우선순위 | v6 §4-A | 충돌 시 SOT 우선 판정 |

### 오류 주의사항

| 오류 | 대응 |
|------|------|
| v10은 v21~v23 기준 매핑 | v12는 v25.2.0 기준. v10 매핑 결과 참조 금지 (Phase 2에서만 교차확인) |
| v10 M-에이전트 라인 참조 무효 | Phase 0에서 재구축한 v12 인덱스만 사용 |
| PARTIAL 과다 판정 | "§6 참조"만 있는 경우 → PARTIAL로 판정, §6.X 구체 매핑은 0-I-E 결과 참조 |

---

## 매핑 판정 기준

| 판정 | 정의 | 필수 필드 |
|------|------|---------|
| **MATCHED** | PART2에 명시적 존재. 해당 Feature의 구현 지침이 충분함 | part2_section, part2_line, part2_text |
| **PARTIAL** | 관련 내용 있으나 불충분. "§6 참조"만 있거나 상위 모듈만 언급 | part2_section, part2_line, partial_reason |
| **MISSING** | PART2 어디에도 없음. SOT에는 있지만 구현 가이드에 누락 | severity(BLOCKER/HIGH/MEDIUM/LOW), missing_reason |
| **SPREAD** | 여러 Phase/섹션에 분산 배치. 주 위치 + 부 위치 기재 | primary_section, secondary_sections[] |
| **NOT_APPLICABLE** | PART2 반영 불필요. 설계 원칙/배경/이력 등 | na_reason |

---

## 대화별 작업 상세

### ═══ 대화 6: M-1 ~ M-3 (V0/V1/V2 매핑) ═══

#### M-1: PART2 §2 (V0 STEP 1~6) 매핑

**범위**: Feature Registry에서 version_scope에 "V0" 포함된 전체
**대상 섹션**: PART2 §2 (V0 구현 가이드)

**작업**:
1. Feature Registry에서 V0 Features 필터링
2. PART2 §2 전체 읽기
3. 각 Feature → PART2 §2 매핑 시도
4. 매핑 불가 시 §6(공통 구현 상세)에서 추가 검색
5. 판정 기재

**매핑 결과 JSON 템플릿**:
```json
{
  "agent": "M-1",
  "scope": "V0",
  "part2_sections": ["§2"],
  "total_features": 0,
  "results": [
    {
      "feature_id": "v12_C01a_001",
      "feature_name": "...",
      "status": "MATCHED|PARTIAL|MISSING|SPREAD|NOT_APPLICABLE",
      "part2_section": "§2.3.2",
      "part2_line": 456,
      "part2_text": "매칭된 텍스트 (50자)",
      "evidence_source": "SOT 파일명",
      "evidence_line": 123,
      "evidence_text": "SOT 원본 (50자)",
      "severity": null,
      "notes": ""
    }
  ],
  "statistics": {
    "MATCHED": 0,
    "PARTIAL": 0,
    "MISSING": 0,
    "SPREAD": 0,
    "NOT_APPLICABLE": 0
  }
}
```

> **⚠️ 필드 값 제약 (M-에이전트 공통)**:
> - `status`: `MATCHED`, `PARTIAL`, `MISSING`, `SPREAD`, `NOT_APPLICABLE` (5개만 허용)
> - `severity` (MISSING/PARTIAL일 때): `BLOCKER`, `HIGH`, `MEDIUM`, `LOW` (4개만 허용). `P0/P1/P2`, `CRITICAL` 등 비표준 금지
> - Phase 0에서 정규화된 `priority`, `category`, `source_group` 값을 그대로 유지. M-에이전트가 임의로 변경 금지

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase1\v12_mapping_M01_v0.json`

---

#### M-2: PART2 §3 (V1 Phase 1~6) 매핑

**범위**: Feature Registry에서 version_scope에 "V1" 포함된 전체
**대상 섹션**: PART2 §3 (V1 구현 가이드)

**특별 주의**:
- V1은 Feature 건수가 최대 (v10 기준 1,759건). v12에서도 최대일 것으로 예상
- §3 Phase 테이블 + §6 공통 상세 양쪽에서 매핑 시도
- v10에서 V1_P3에 44건 TRUE_MISSING 패치됨 → v25.2.0에서 확인 필요
- v11 "V1 구조 고립" 패턴 관련 — 균일성 확인

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase1\v12_mapping_M02_v1.json`

---

#### M-3: PART2 §4 (V2 Phase 1~3) 매핑

**범위**: Feature Registry에서 version_scope에 "V2" 포함된 전체
**대상 섹션**: PART2 §4 (V2 구현 가이드)

**특별 주의**:
- v10에서 V2_P2에 106건 TRUE_MISSING 패치됨 (최대 집중)
- v11 "V2-P2 저커버리지" 패턴 관련 — 116건 중 프롬프트 10건만
- §4.2(V2 Phase 2) AI 프롬프트 커버 범위 특별 점검

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase1\v12_mapping_M03_v2.json`

---

### ═══ 대화 7: M-4 ~ M-6 (V3/§6/프롬프트 매핑) ═══

#### M-4: PART2 §5 (V3 Phase 1~3) 매핑

**범위**: Feature Registry에서 version_scope에 "V3" 포함된 전체
**대상 섹션**: PART2 §5 (V3 구현 가이드)

**특별 주의**:
- v11 "V3 과적재" 패턴 관련 — 자기완결성 2.5/5
- §5에서 "§6 참조" 비율이 과도한지 확인
- V3 Feature가 V1/V2 대비 적절한 세부 수준인지

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase1\v12_mapping_M04_v3.json`

---

#### M-5a: PART2 §6.1~§6.7 매핑

**범위**: Feature Registry 전체 중 §6 관련 Feature + PARTIAL 판정된 항목
**대상 섹션**: PART2 §6.1~§6.7

**작업**:
1. §6.1~§6.7 전체 읽기
2. Feature Registry에서 category 기반 매핑 (orange_core → §6.X, storage → §6.X 등)
3. M-1~M-4에서 PARTIAL("§6 참조") 판정된 항목의 §6.X 매핑 시도
4. §6에만 있고 §2~§5에 매핑이 없는 Feature 식별

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase1\v12_mapping_M05a.json`

---

#### M-5b: PART2 §6.8~§6.13 + §7 매핑

**범위**: Feature Registry 전체 중 §6.8~§6.13 및 §7 관련 Feature
**대상 섹션**: PART2 §6.8~§6.13 + §7

**특별 주의**:
- §6.12.6 번호 중복 오류 발견됨 (이전 대화에서 확인) — 확인 필요
- §7은 부록/변경이력/Gate 정의 등 — NOT_APPLICABLE 다수 예상

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase1\v12_mapping_M05b.json`

---

#### M-6: PART2 §1 + §7(변경이력) + 18개 AI 프롬프트 내부 참조 매핑 (신규)

**범위**: Feature Registry 중 §1(개요)/§7(변경이력) 관련 + 18개 AI 프롬프트 커버리지
**대상 섹션**: PART2 §1, §7(변경이력), 18개 AI 프롬프트 내부

**작업**:
1. §1(프로젝트 개요, 기술 스택, 아키텍처) 읽기 → Feature 매핑
2. §7 후반부(변경이력 영역) 읽기 → Feature 매핑
3. 18개 AI 프롬프트(Phase 0 프롬프트 인벤토리 참조) 각각의 커버 범위 분석
4. 프롬프트가 참조하는 §N, Feature, 데이터 등이 실제 존재하는지 확인
5. 프롬프트 내부 참조 누락 식별

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase1\v12_mapping_M06.json`

---

### 교차검증 ③: 에이전트 간 중복/충돌 + 통계 검증

**작업** (대화 7 마지막):
1. M-1~M-6 통계 합산 → 총 건수 = Feature Registry extractable=true 건수와 일치 확인
2. 에이전트 간 중복 매핑 (동일 Feature를 다른 에이전트가 매핑) 식별
3. MISSING 판정 전수 수집 → 심각도별 분류
4. PARTIAL 판정 전수 수집 → §6 참조 건수 확인
5. 종합 보고서 작성

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase1\v12_phase1_report.md`

**보고서 포맷**:
```markdown
# v12 Phase 1 매핑 보고서

## 통계 요약
| 판정 | 건수 | 비율 |
|------|-----:|-----:|
| MATCHED | X | X% |
| PARTIAL | X | X% |
| MISSING | X | X% |
| SPREAD | X | X% |
| NOT_APPLICABLE | X | X% |
| **합계** | **X** | **100%** |

## MISSING 심각도별
| 심각도 | 건수 |
|--------|-----:|
| BLOCKER | X |
| HIGH | X |
| MEDIUM | X |
| LOW | X |

## 에이전트별 통계
(M-1~M-6 각각)

## 중복/충돌 사항
(있으면 상세)

## Phase 1 판정: PASS/FAIL
```

---

## 산출물 전수 목록

| # | 파일 | 경로 | 대화 |
|---|------|------|------|
| 1 | M-1 V0 매핑 | `v12_results/phase1/v12_mapping_M01_v0.json` | 6 |
| 2 | M-2 V1 매핑 | `v12_results/phase1/v12_mapping_M02_v1.json` | 6 |
| 3 | M-3 V2 매핑 | `v12_results/phase1/v12_mapping_M03_v2.json` | 6 |
| 4 | M-4 V3 매핑 | `v12_results/phase1/v12_mapping_M04_v3.json` | 7 |
| 5 | M-5a §6.1~6.7 매핑 | `v12_results/phase1/v12_mapping_M05a.json` | 7 |
| 6 | M-5b §6.8~6.13+§7 매핑 | `v12_results/phase1/v12_mapping_M05b.json` | 7 |
| 7 | M-6 §1+§7(변경이력)+프롬프트 매핑 | `v12_results/phase1/v12_mapping_M06.json` | 7 |
| 8 | Phase 1 보고서 | `v12_results/phase1/v12_phase1_report.md` | 7 |

---

## AI 오류 방지 규칙 (이 Phase에서 준수)

1. **환각 금지**: 매핑 판정에 part2_line + part2_text + evidence_source + evidence_line + evidence_text 5개 필드 필수
2. **독립 매핑**: v10 매핑 결과 참조 금지. v12 독립 매핑만 수행. v10은 Phase 2에서 교차확인
3. **PARTIAL 남용 금지**: "§6 참조"만 있다고 무조건 PARTIAL이 아님. §6.X에서 실제 구현 상세가 충분하면 MATCHED (+ SPREAD)
4. **MISSING 과잉 주의**: extractable=false 항목은 매핑 대상 아님. extractable=true만 매핑
5. **부분 읽기 금지**: PART2 §N 읽기 시 해당 섹션 전체 읽기
6. **v12 인덱스 활용**: section_map, reference_map 등 Phase 0 인덱스를 적극 활용하여 정확한 위치 지정
7. **대화 간 상태**: 대화 6의 M-1~M-3 결과는 JSON으로 저장. 대화 7에서 M-4~M-6 수행 후 전체 교차검증
8. **필드 값 enum 준수**: `status`는 5개(MATCHED/PARTIAL/MISSING/SPREAD/NOT_APPLICABLE), `severity`는 4개(BLOCKER/HIGH/MEDIUM/LOW)만 허용. Phase 0 Feature Registry의 `priority`/`category`/`source_group` 값을 M-에이전트가 변경하지 말 것

---

## 완료 시 수행 (대화 7 마지막)

1. 위 8개 산출물 파일 전수 존재 확인
2. `v12_phase_status.json` 업데이트:
   ```json
   {
     "phase1": {
       "status": "completed",
       "conversation": "대화 6~7",
       "pass": true/false,
       "started_at": "2026-03-XX",
       "completed_at": "2026-03-XX"
     }
   }
   ```
3. MISSING 건수 + 심각도 요약 출력
4. BLOCKER > 0이면 해당 항목 즉시 보고
