# Phase 4: 최종 검증 + CHECKPOINT

> **대화**: 대화 11
> **목표**: PART2 최종본(v26.0.0) 전수 재검증 → CHECKPOINT 12개 조건 판정 → v12 Pipeline 완료
> **성격**: 전체 파이프라인의 최종 관문. 여기서 PASS하면 V0-STEP-1 착수 가능.
> **선행 조건**: Phase 3 PASS

---

## Pre-check Protocol

```
① 본 계획 파일 읽기: D:\VAMOS\04. 구현단계\v12\v12_plan.md
② 본 프롬프트 읽기: D:\VAMOS\04. 구현단계\v12\prompts\phase4_prompt.md
③ 진행 상태 확인: D:\VAMOS\04. 구현단계\v12\v12_results\v12_phase_status.json
④ Phase 3 PASS 확인 (FAIL이면 Phase 4 진행 불가)
⑤ Phase 3 산출물 로드:
   - v12_phase3_verdict.md (수정 통계 + 구조 무결성)
   - v12_ripple_map.json (수정 건별 영향)
⑥ Phase 2 산출물 로드:
   - v12_final_missing_list.md (최종 누락 목록 — 전수 반영 확인용)
   - v12_s6_final_mapping.md (§6 57건 해소 확인용)
   - v12_pattern_resolution.md (패턴 해소 확인용)
⑦ Phase 0 산출물 로드:
   - v12_feature_registry_final.json (커버리지 판정용)
⑧ 확인 완료 후 작업 시작
```

---

## 스킬 에이전트 실행 규칙

> **필수**: 본 Phase의 작업은 **Agent tool(스킬 에이전트)**을 활용하여 일관된 결과를 도출합니다.

1. **독립 검증**: 작업 4-A~4-F는 Agent tool로 독립 병렬 실행 가능. 단, 4-G(CHECKPOINT)는 4-A~4-F 완료 후 순차 실행
2. **동일 템플릿**: 모든 산출물은 본 프롬프트에 정의된 출력 포맷 준수
3. **증거 기반**: 에이전트 결과에 evidence_source + evidence_line + evidence_text 필수
4. **재현성**: 동일 입력 → 동일 출력 보장을 위해 판정 기준을 명시적으로 적용

---

## 입력 파일

### PART2 최종본 (검증 대상)

| 파일 | 경로 |
|------|------|
| PART2 구현단계 v26.0.0 | `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` |

### v12 전 Phase 산출물

| # | 파일 | 경로 |
|---|------|------|
| 1 | Feature Registry | `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_feature_registry_final.json` |
| 2 | Section Map (Phase 0) | `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_section_map.json` |
| 3 | Numeric Registry | `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_numeric_registry.json` |
| 4 | Prompt Inventory | `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_prompt_inventory.json` |
| 5 | §6 예비 Mapping | `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_s6_mapping.json` |
| 6 | Phase 1 Report | `D:\VAMOS\04. 구현단계\v12\v12_results\phase1\v12_phase1_report.md` |
| 7 | Adversarial Report | `D:\VAMOS\04. 구현단계\v12\v12_results\phase15\v12_adversarial_report.md` |
| 8 | 최종 누락 목록 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase2\v12_final_missing_list.md` |
| 9 | §6 최종 매핑 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase2\v12_s6_final_mapping.md` |
| 10 | 패턴 해소 방안 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase2\v12_pattern_resolution.md` |
| 11 | 업데이트 계획 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase2\v12_update_plan.md` |
| 12 | Phase 3 판정 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase3\v12_phase3_verdict.md` |
| 13 | Ripple Map | `D:\VAMOS\04. 구현단계\v12\v12_results\phase3\v12_ripple_map.json` |
| 14 | 무결성 JSON | `D:\VAMOS\04. 구현단계\v12\v12_results\phase3\backup\v25_integrity.json` |
| 15 | v10 교차 대사 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase2\v12_v10_crosscheck.md` |
| 16 | v7 역방향 교차 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase2\v12_v7_crosscheck.md` |
| 17 | Reference Map | `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_reference_map.json` |
| 18 | Impl Skill Agent | `D:\VAMOS\04. 구현단계\v12\v12_impl_skill_agent.md` |
| 19 | Phase -1 Verdict | `D:\VAMOS\04. 구현단계\v12\v12_results\phase-1\v12_phase-1_verdict.md` |
| 20 | Phase 0 Verdict | `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_phase0_verdict.md` |
| 21 | Phase 2 Verdict | `D:\VAMOS\04. 구현단계\v12\v12_results\phase2\v12_phase2_verdict.md` |

### SOT (커버리지 판정용)

```
경로: D:\VAMOS\docs\sot\ (68개 파일)
```

---

## 스킬 에이전트 패턴

| 패턴 | 출처 | 적용 |
|------|------|------|
| 4-Dimension 검증 | v8 | 4-A~4-C |
| 프롬프트 검증 P1~P10 | v8 Agent 11 | 4-B |
| GT 기반 검증 | v9 GT-1~GT-5 | 4-C |
| 적대적 재검증 | v10/v11 | 4-F |
| 정본 우선순위 | v6 §4-A | 판정 시 |

---

## 작업 상세

### 작업 4-A: 인덱스 전수 재구축 (v26.0.0 기준)

**목적**: Phase 3 수정 후 인덱스를 v26.0.0 기준으로 재구축

**작업**:
1. PART2 v26.0.0 전체 읽기
2. 섹션 구조 재추출 (heading 전수)
3. Phase 0 Section Map과 비교 → 변경 사항 확인
4. 내부 참조 재매핑

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase4\v12_final_section_map.json`

---

### 작업 4-B: 18개 AI 프롬프트 재검증 (v8 P1~P10)

**목적**: PART2 v26.0.0의 18개 AI 프롬프트가 정확하고 완전한지 검증

**검증 항목 (v8 Agent 11 P1~P10 계승)**:

| # | 항목 | 검증 내용 |
|---|------|---------|
| P1 | 프롬프트 존재 | 18개 모두 존재 확인 (V0:6 + V1:6 + V2:3 + V3:3) |
| P2 | 입력 참조 유효성 | 프롬프트가 참조하는 파일/경로/§N이 존재하는지 |
| P3 | 출력 정의 | 각 프롬프트의 예상 출력물이 명확히 정의되었는지 |
| P4 | Stage Gate 연결 | 각 프롬프트가 올바른 Stage Gate에 연결되었는지 |
| P5 | 의존성 순서 | 프롬프트 간 의존성이 올바르게 순서화되었는지 |
| P6 | 커버리지 | 프롬프트가 해당 Phase의 작업을 충분히 커버하는지 |
| P7 | LOCK 값 일치 | 프롬프트 내 수치가 LOCK 값과 일치하는지 |
| P8 | 코드 블록 유효성 | 프롬프트 내 코드/스키마 예시가 현재 구조와 일치하는지 |
| P9 | 모호성 부재 | 프롬프트에 해석이 갈리는 모호한 지시가 없는지 |
| P10 | 자기완결성 | 프롬프트만으로 해당 작업을 수행할 수 있는지 (§6 의존도) |

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase4\v12_prompt_validation.md`

**포맷**:
```markdown
# v12 Phase 4-B: AI 프롬프트 재검증

## 요약
| 프롬프트 | 위치 | P1~P10 결과 | 종합 |
|---------|------|------------|------|
| V0-STEP-1 프롬프트 | §2.X L행 | P1✅ P2✅ ... | PASS/FAIL |
| ... | | | |

## P항목별 전체 통과율
| 항목 | PASS | FAIL | 통과율 |
|------|------|------|--------|
| P1 | 18 | 0 | 100% |
| ... | | | |

## FAIL 항목 상세
(있으면 건별 상세)
```

---

### 작업 4-C: 수치/참조/용어 정합성 재검증

**목적**: v26.0.0 전체의 수치/참조/용어 일관성 확인

**작업**:
1. **수치 정합성**: Numeric Registry(Phase 0) vs v26.0.0 실제 수치 대조
   - LOCK 값 40개 전수 확인
   - §6.13 작업량 테이블 산술 확인
   - 퍼센트 합산 확인 (100% 여부)
2. **참조 정합성**: 모든 "§N" 참조가 실제 해당 섹션을 가리키는지
   - 특히 §6 참조 57건이 모두 구체화되었는지
   - 새로 추가된 항목의 참조가 유효한지
3. **용어 일관성**: 동일 개념에 다른 용어 사용 여부
   - Stage Gate 명칭 통일 확인 (Pattern B 해소 확인)
   - 모듈 명칭 통일

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase4\v12_consistency_check.md`

---

### 작업 4-D: 18개 Stage Gate 전수 확인

**목적**: V0~V3 전체 18개 Stage Gate가 올바르게 정의되어 있는지

**작업**:
1. 18개 Stage Gate 위치 확인 (V0:6 + V1:6 + V2:3 + V3:3)
2. 각 Gate의 통과 조건 명시 확인
3. Gate 간 연결 (이전 Gate → 현재 Gate → 다음 Gate) 확인
4. Gate 명칭 일관성 확인

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase4\v12_stagegate_check.md`

---

### 작업 4-E: SOT 68개 → PART2 최종 커버리지 판정

**목적**: v12 파이프라인의 핵심 목표 — SOT 대비 PART2 완전성 최종 판정

**작업**:
1. v12 Feature Registry(extractable=true) 전체 로드
2. Phase 1 매핑 결과 + Phase 1.5 보정 + Phase 3 반영 후 최종 상태 (**5개만 허용**):
   - `MATCHED` — PART2에 존재
   - `RESOLVED` — Phase 3에서 추가됨
   - `UPPER_MODULE` — 상위 수준 커버
   - `RECLASSIFIED` — 범위 외
   - `REMAINING_MISSING` — 미해소 잔여
   > ❌ 금지: 위 5개 외 비표준 상태값 사용 금지 (예: `COVERED`, `DONE`, `N/A` 등)
3. 커버리지율 계산:
   ```
   커버리지 = (MATCHED + RESOLVED + UPPER_MODULE) / extractable_true × 100
   ```
4. REMAINING_MISSING 0건 확인

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase4\v12_coverage_final.md`

**포맷**:
```markdown
# v12 Phase 4-E: 최종 커버리지 판정

## Feature Registry 통계
| 항목 | 건수 |
|------|-----:|
| 총 Feature | X |
| extractable=true | X |
| extractable=false | X |

## 커버리지 결과
| 판정 | 건수 | 비율 |
|------|-----:|-----:|
| MATCHED | X | X% |
| RESOLVED (v26 신규) | X | X% |
| UPPER_MODULE | X | X% |
| RECLASSIFIED | X | X% |
| REMAINING_MISSING | X | X% |
| **합계** | **X** | **100%** |

## 커버리지율
= (MATCHED + RESOLVED + UPPER_MODULE) / extractable_true
= X / X = X%

## 판정: PASS (커버리지 ≥95% + REMAINING_MISSING 0건) / FAIL
```

---

### 작업 4-F: 적대적 재검증 (수정 후)

**목적**: Phase 3 수정 후 새로운 오류가 도입되지 않았는지 확인

**작업**:
1. Phase 3에서 추가/변경된 행만 대상
2. 각 수정 건에 대해:
   - 삽입된 내용이 SOT 원본과 일치하는지
   - 참조가 유효한지
   - LOCK 값이 보호되었는지
   - 기존 항목과 중복/충돌하지 않는지
3. 오류 발견 시 즉시 기록
4. **v12_impl_skill_agent.md 검증** (Phase 3 수정분):
   - §5.2 status가 Phase 3 결과에 따라 올바르게 업데이트되었는지 확인
   - impl_status.json 스키마와 v12_impl_skill_agent.md 내 스키마 정의가 일치하는지 확인
   - LOCK 40개 값이 보호(변경 없음)되었는지 확인

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase4\v12_final_adversarial.md`

---

### 작업 4-G: CHECKPOINT (§1.2 성공 기준 12개 전수 판정)

**목적**: v12_plan.md §1.2의 12개 성공 기준을 전수 판정

**판정 기준** (v12_plan.md §1.2에서):

| # | 조건 | 판정 기준 | 확인 방법 |
|---|------|---------|---------|
| 1 | v12 Feature Registry 완성 | SOT 68개 전수 추출, 읽기 완료율 90%+ | Phase 0 verdict |
| 2 | SOT→PART2 매핑 100% | extractable=true 전건 매핑 시도 | Phase 1 report |
| 3 | MISSING BLOCKER 0건 | BLOCKER 심각도 잔여 0건 | Phase 2 final_missing_list |
| 4 | 적대적 재검증 PASS | 오판율 ≤ 10% | Phase 1.5 adversarial_report |
| 5 | v10 교차 대사 완료 | v12 vs v10 차이 전건 분석 | Phase 2 v10_crosscheck |
| 6 | v7 역방향 교차 확인 | 추가 누락 0건 확인 | Phase 2 v7_crosscheck |
| 7 | §6 참조 57건 전수 해소 | 구체적 §6.X 매핑 또는 §6 내용 추가 | Phase 3 + 4-C |
| 8 | v11 미해결 패턴 5건 해소 | Pattern A/B, V1 고립, V3 과적재, V2-P2 | Phase 3 + 4-C |
| 9 | PART2 반영 완료 | 전수 패치 + 구조 무결성 PASS | Phase 3 verdict |
| 10 | 18개 AI 프롬프트 재검증 | P1~P10 전항목 PASS | 4-B |
| 11 | 수치/참조 정합성 | 재구축 인덱스 기준 PASS | 4-C |
| 12 | 원본 보호 | SHA256 백업 + 역패치 가능 | 4-F + Phase 3 backup |

**산출물**:
- `D:\VAMOS\04. 구현단계\v12\v12_results\v12_checkpoint.md`
- `D:\VAMOS\04. 구현단계\v12\v12_results\phase4\v12_final_validation.md` (CHECKPOINT 판정 + 최종 검증 보고서)

**포맷**:
```markdown
# v12 Pipeline 완료 판정 (CHECKPOINT)

> **작성일**: 2026-03-XX
> **PART2 최종 버전**: v26.0.0

---

## 12개 완료 조건 판정 결과

| # | 조건 | 판정 | 근거 (산출물 + 수치) |
|---|------|------|---------------------|
| 1 | Feature Registry 완성 | PASS/FAIL | ... |
| 2 | SOT→PART2 매핑 100% | PASS/FAIL | ... |
| 3 | MISSING BLOCKER 0건 | PASS/FAIL | ... |
| 4 | 적대적 재검증 PASS | PASS/FAIL | ... |
| 5 | v10 교차 대사 완료 | PASS/FAIL | ... |
| 6 | v7 역방향 교차 확인 | PASS/FAIL | ... |
| 7 | §6 참조 57건 해소 | PASS/FAIL | ... |
| 8 | v11 패턴 5건 해소 | PASS/FAIL | ... |
| 9 | PART2 반영 완료 | PASS/FAIL | ... |
| 10 | 18개 프롬프트 검증 | PASS/FAIL | ... |
| 11 | 수치/참조 정합성 | PASS/FAIL | ... |
| 12 | 원본 보호 | PASS/FAIL | ... |

---

## 최종 통계

- **v12 Feature Registry**: 총 X건 (extractable=true: X건)
- **커버리지율**: X%
- **MISSING 잔여**: X건 (BLOCKER: 0, HIGH: X, MEDIUM: X, LOW: X)
- **PART2 버전**: v25.2.0 → v26.0.0 (X행 → X행, +X행)
- **수정 건수**: 삽입 X건, 변경 X건, 삭제 0건

---

## v12 Pipeline 실행 요약

| Phase | 대화 | 상태 | 핵심 결과 |
|-------|------|------|---------|
| Phase -1 | 1 | PASS/FAIL | ... |
| Phase 0 | 2~5 | PASS/FAIL | ... |
| Phase 1 | 6~7 | PASS/FAIL | ... |
| Phase 1.5 | 8 | PASS/FAIL | ... |
| Phase 2 | 9 | PASS/FAIL | ... |
| Phase 3 | 10 | PASS/FAIL | ... |
| Phase 4 | 11 | PASS/FAIL | ... |

---

## 판정

**X/12 PASS → v12 Pipeline [완료/미완료]**

- 미달 조건: X건
- BLOCKER 잔여: X건
- PART2 최종 버전: vXX.X.X 확정 (X행)
- **다음 단계**: [V0-STEP-1 착수 가능 / 재검증 필요]
```

---

### 교차검증 ⑦: 전수 최종 PASS/FAIL

CHECKPOINT 내에 포함:
- 12개 조건 전수 판정
- 전 Phase 결과 종합
- 최종 커버리지

---

## 산출물 전수 목록

| # | 파일 | 경로 |
|---|------|------|
| 1 | 최종 Section Map | `D:\VAMOS\04. 구현단계\v12\v12_results\phase4\v12_final_section_map.json` |
| 2 | 프롬프트 검증 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase4\v12_prompt_validation.md` |
| 3 | 정합성 검증 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase4\v12_consistency_check.md` |
| 4 | Stage Gate 검증 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase4\v12_stagegate_check.md` |
| 5 | 최종 커버리지 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase4\v12_coverage_final.md` |
| 6 | 최종 적대적 검증 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase4\v12_final_adversarial.md` |
| 7 | CHECKPOINT | `D:\VAMOS\04. 구현단계\v12\v12_results\v12_checkpoint.md` |
| 8 | 최종 검증 보고서 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase4\v12_final_validation.md` |

---

## AI 오류 방지 규칙 (이 Phase에서 준수)

1. **전수 검증**: 샘플이 아닌 전수 검증. 18개 프롬프트 전수, 18개 Gate 전수, LOCK 값 전수
2. **v26.0.0 기준**: Phase 0~3의 이전 인덱스가 아닌 v26.0.0 실제 상태 기준
3. **환각 금지**: 모든 PASS 판정에 evidence 필수. "확인했다"만으로는 불충분
4. **CHECKPOINT 엄격**: 12개 중 1개라도 FAIL이면 전체 FAIL. 부분 PASS 없음
5. **최종 행 수 확인**: v26.0.0 실제 행 수를 직접 세어 확인 (wc -l 등)
6. **되돌리기 가능 확인**: Phase 3 백업 + diff로 v25.2.0 복구 가능한지 확인
7. **필드 값 enum 준수**: 4-E 커버리지 판정은 5개 상태(MATCHED/RESOLVED/UPPER_MODULE/RECLASSIFIED/REMAINING_MISSING)만 사용. Phase 0~3에서 사용된 priority/category/source_group/status/severity enum 값이 최종 산출물에서도 일관되게 유지되는지 확인

---

## 완료 시 수행

1. 위 8개 산출물 파일 전수 존재 확인
2. `v12_phase_status.json` 최종 업데이트:
   ```json
   {
     "current_phase": "completed",
     "phase4": {
       "status": "completed",
       "conversation": "대화 11",
       "pass": true/false,
       "started_at": "2026-03-XX",
       "completed_at": "2026-03-XX"
     }
   }
   ```
3. **12/12 PASS**: v12 Pipeline 완료. V0-STEP-1 착수 가능 선언.
4. **FAIL**: 미달 조건 목록 + 재실행 대상 Phase 지정
5. 최종 보고서 출력 (CHECKPOINT 전문)
