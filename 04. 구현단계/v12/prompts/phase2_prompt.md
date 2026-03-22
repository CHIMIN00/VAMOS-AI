# Phase 2: v10 교차 대사 + 최종 누락 확정 + 업데이트 계획

> **대화**: 대화 9
> **목표**: v12 독립 결과 + v10/v7 기존 결과 교차 대사 → 최종 수정 목록 확정 + Patch Plan 수립
> **성격**: 독립 검증(v12) + 기존 검증(v10/v7) 합류점. 모든 누락을 최종 확정.
> **선행 조건**: Phase 1.5 PASS

---

## Pre-check Protocol

```
① 본 계획 파일 읽기: D:\VAMOS\04. 구현단계\v12\v12_plan.md
② 본 프롬프트 읽기: D:\VAMOS\04. 구현단계\v12\prompts\phase2_prompt.md
③ 진행 상태 확인: D:\VAMOS\04. 구현단계\v12\v12_results\v12_phase_status.json
④ Phase 1.5 PASS 확인 (FAIL이면 Phase 2 진행 불가)
⑤ Phase 1.5 산출물 로드:
   - v12_adversarial_report.md (REAL_MISSING 확정 목록)
⑥ Phase 1 산출물 로드:
   - v12_phase1_report.md
   - v12_mapping_M01~M06.json (M05a/M05b 포함, 7개)
⑦ Phase 0 산출물 로드:
   - v12_feature_registry_final.json
   - v12_section_map.json
   - v12_s6_mapping.json
   - v12_reference_map.json
   - v12_v10_delta.json
⑧ 확인 완료 후 작업 시작
```

---

## 스킬 에이전트 실행 규칙

> **필수**: 본 Phase의 작업은 **Agent tool(스킬 에이전트)**을 활용하여 일관된 결과를 도출합니다.

1. **독립 검증**: 각 작업(2-A~2-F)은 가능한 Agent tool로 독립 실행하여 교차 오염 방지
2. **동일 템플릿**: 모든 산출물은 본 프롬프트에 정의된 출력 포맷 준수
3. **증거 기반**: 에이전트 결과에 evidence_source + evidence_line + evidence_text 필수
4. **재현성**: 동일 입력 → 동일 출력 보장을 위해 판정 기준을 명시적으로 적용

---

## 입력 파일

### v12 산출물 (Phase 0/1/1.5)

| # | 파일 | 경로 |
|---|------|------|
| 1 | Feature Registry | `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_feature_registry_final.json` |
| 2 | Section Map | `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_section_map.json` |
| 3 | §6 예비 Mapping | `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_s6_mapping.json` |
| 4 | Reference Map | `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_reference_map.json` |
| 5 | v10 대비 Feature 변동 내역 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_v10_delta.json` |
| 6 | Phase 1 Report | `D:\VAMOS\04. 구현단계\v12\v12_results\phase1\v12_phase1_report.md` |
| 7 | M-1~M-6 매핑 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase1\v12_mapping_M01_v0.json` ~ `v12_mapping_M06.json` |
| 8 | Adversarial Report | `D:\VAMOS\04. 구현단계\v12\v12_results\phase15\v12_adversarial_report.md` |

### v10 기존 산출물 (교차확인용)

| # | 파일 | 경로 |
|---|------|------|
| 9 | v10 Feature Registry | `D:\VAMOS\04. 구현단계\v10_results\phase0-f\v10_feature_registry_final.json` |
| 10 | v10 Consolidated Missing | `D:\VAMOS\04. 구현단계\v10_results\phase2\consolidated_missing.json` |
| 11 | v10 Integrated Result | `D:\VAMOS\04. 구현단계\v10_results\phase2\v10_step2_integrated_result.json` |
| 12 | v10 Phase 2 Report | `D:\VAMOS\04. 구현단계\v10_results\phase2\v10_phase2_final_report.md` |
| 13 | v10 Checkpoint | `D:\VAMOS\04. 구현단계\v10_results\v10_checkpoint.md` |

### v11 기존 산출물 (교차확인용)

| # | 파일 | 경로 |
|---|------|------|
| 14 | v11 Adversarial Report | `D:\VAMOS\04. 구현단계\v11_results\phase15\v11_adversarial_report.md` |
| 15 | v11 Checkpoint | `D:\VAMOS\04. 구현단계\v11_results\v11_checkpoint.md` |

### v7 교차확인용

| # | 파일 | 경로 |
|---|------|------|
| 16 | v7 프롬프트 | `C:\Users\dkscl\OneDrive\바탕 화면\VAMOS\04. 구현단계\VAMOS_검증_프롬프트_v7.md` |

### PART2 원본

| 파일 | 경로 |
|------|------|
| PART2 구현단계 v25.2.0 | `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` |

### Phase -1 산출물 (v11 패턴 참조)

| # | 파일 | 경로 |
|---|------|------|
| 17 | 패턴 점검 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase-1\v12_pattern_check.md` |
| 18 | v25 편집 충돌 검사 결과 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase-1\v12_v25_conflict.md` |

---

## 스킬 에이전트 패턴

| 패턴 | 출처 | 적용 |
|------|------|------|
| 심각도 분류 (BLOCKER/H/M/L) | v6 §4-C | 2-E 최종 분류 |
| 4-Phase 분류 (EXACT/UPPER/RECLASS/TRUE_MISSING) | v10 Phase 2 | 2-A 교차 대사 |
| 도메인별 SOT 역방향 MISSING 탐지 | v7 Agent 1~10 | 2-B 역방향 확인 |
| 정본 우선순위 | v6 §4-A | 충돌 해결 |

---

## 작업 상세

### 작업 2-A: v12 MISSING vs v10 consolidated_missing 교차 대사

**목적**: v12 독립 검증의 REAL_MISSING과 v10의 1,068건 교차 비교

**작업**:
1. v12 REAL_MISSING 목록 로드 (Phase 1.5 확정)
2. v10 consolidated_missing (1,068건) 로드
3. 교차 비교:

| 조합 | 의미 | 처리 |
|------|------|------|
| v12 MISSING + v10 MISSING | 양쪽 모두 누락 판정 → 확정 MISSING | 최종 목록에 포함 |
| v12 MISSING + v10 MATCHED | v12에서만 누락 → v10 매핑 위치 재확인 | v25.2.0에서 해당 위치 확인. 존재하면 v12 FP |
| v12 MATCHED + v10 MISSING | v10에서만 누락 → v25.2.0에서 추가됐을 수 있음 | v25.2.0에서 확인. 없으면 v12 FN |
| v12 MISSING + v10 없음(신규) | v10이 분석 안 한 25개 SOT에서 발견 → 신규 MISSING | 최종 목록에 포함 |

4. v10 TRUE_MISSING 200건의 v25.2.0 반영 상태 확인 (v23 마커 존재 확인)

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase2\v12_v10_crosscheck.md`

**포맷**:
```markdown
# v12 Phase 2-A: v10 교차 대사

## 교차 비교 요약
| 조합 | 건수 |
|------|-----:|
| v12 MISSING + v10 MISSING (확정) | X |
| v12 MISSING + v10 MATCHED (v12 재확인) | X |
| v12 MATCHED + v10 MISSING (v10 해소 확인) | X |
| v12 MISSING + v10 없음 (신규) | X |
| v12 MATCHED + v10 MATCHED (일치) | X |

## v10 TRUE_MISSING 200건 반영 상태
| 상태 | 건수 |
|------|-----:|
| v25.2.0에 반영 확인 | X |
| 반영 미확인 | X |

## 상세 목록
(건별 — 불일치 건만)
```

---

### 작업 2-B: v7 역방향 MISSING 교차 확인

**목적**: v7의 역방향(PART2→SOT) 접근으로 발견한 누락이 v12에서도 확인되는지

**작업**:
1. v7 프롬프트 읽기 → v7 Agent 1~10의 도메인별 MISSING 패턴 확인
2. v7에서 보고된 주요 MISSING 항목 추출
3. v12 결과와 교차 → 추가 누락 여부 확인

**주의**: v7은 라인 참조 기반이므로 v25.2.0에서 무효. 내용 기반으로만 대조.

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase2\v12_v7_crosscheck.md`

---

### 작업 2-C: v11 미해결 패턴 5건 해소 방안

**목적**: Phase -1A에서 확인한 5건 패턴의 구체적 해소 방안 수립

**입력**: `v12_results/phase-1/v12_pattern_check.md`

**작업**:
1. 각 패턴의 현재 상태 (RESOLVED/OPEN) 확인
2. OPEN 패턴별 구체적 수정 방안:

| 패턴 | OPEN일 때 해소 방안 |
|------|-----------------|
| Pattern A (연쇄 미갱신) | §6.13 + §7.4 수치 갱신 |
| Pattern B (Gate 명칭) | Stage Gate 명칭 통일 |
| V1 구조 고립 | §3 Phase 테이블 포맷 통일 |
| V3 과적재 | §5에 §6 내용 직접 추가 또는 §6.X 참조 구체화 |
| V2-P2 저커버리지 | §4.2 AI 프롬프트 커버 범위 확장 |

3. 각 해소 방안의 PART2 영향 범위 분석

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase2\v12_pattern_resolution.md`

---

### 작업 2-D: §6 참조 57건 최종 매핑 확정

**목적**: Phase 0에서 예비 매핑한 §6 참조 57건의 최종 매핑 확정

**입력**: `v12_results/phase0/v12_s6_mapping.json`

**작업**:
1. 예비 매핑 결과 로드
2. 각 건별 PART2 §6.X 실제 확인:
   - §6.X에 충분한 내용 있음 → "§6 참조" → "§6.X 참조"로 구체화 (Phase 3에서 수정)
   - §6.X에 불충분 → §6에 내용 추가 필요 (Phase 3에서 수정)
   - §6.X 해당 없음 → 해당 Feature를 §2~§5 Phase 테이블에 직접 기재 (Phase 3에서 수정)
3. 57건 전수 분류

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase2\v12_s6_final_mapping.md`

**포맷**:
```markdown
# v12 Phase 2-D: §6 참조 57건 최종 매핑

## 분류 요약
| 분류 | 건수 |
|------|-----:|
| §6.X 구체화 가능 (참조만 변경) | X |
| §6에 내용 추가 필요 | X |
| §2~§5에 직접 기재 | X |
| **합계** | **57** |

## 건별 상세
| # | v25 행번호 | 현재 텍스트 | §6.X 매핑 | 분류 | 해소 방안 |
|---|----------|-----------|---------|------|---------|
```

---

### 작업 2-E: 심각도 분류

**목적**: 최종 누락 항목(REAL_MISSING + 교차대사 추가분 + §6 미해소분)에 대한 심각도 분류

**분류 기준** (v6 §4-C 계승):

| 심각도 | 기준 |
|--------|------|
| **BLOCKER** | 이것 없으면 V0~V3 구현 착수 불가. LOCK 값 미기재, 핵심 아키텍처 결정 미기재 |
| **HIGH** | 구현 시 모호함 발생. AI 프롬프트 커버리지 부족, Phase 간 의존성 미기재 |
| **MEDIUM** | 구현 가능하나 최적이 아님. 세부 스펙 부족, 예외 처리 미기재 |
| **LOW** | 사소한 누락. 부가 설명, UI 세부, 문서화 세부 |

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase2\v12_final_missing_list.md`

**포맷**:
```markdown
# v12 Phase 2-E: 최종 누락 목록 (확정)

## 통계
| 심각도 | 건수 | 비율 |
|--------|-----:|-----:|
| BLOCKER | X | X% |
| HIGH | X | X% |
| MEDIUM | X | X% |
| LOW | X | X% |
| **합계** | **X** | **100%** |

## 출처별
| 출처 | 건수 |
|------|-----:|
| v12 독립 MISSING | X |
| v10 교차 추가 | X |
| v7 역방향 추가 | X |
| §6 미해소 | X |
| v11 패턴 해소 | X |
| **합계** | **X** |

## 건별 상세
| # | feature_id | feature_name | severity | source | target_section | action |
|---|-----------|-------------|---------|--------|---------------|--------|
```

---

### 작업 2-F: Patch Plan 수립

**목적**: Phase 3에서 실행할 PART2 수정 계획

**작업**:
1. 수정 건별 분류:
   - **신규 삽입**: Phase 테이블에 행 추가
   - **참조 구체화**: "§6 참조" → "§6.X 참조" 변경
   - **내용 추가**: §6에 새 항목 추가
   - **구조 수정**: 포맷/명칭 통일 등
   - **수치 갱신**: §6.13 작업량, §7.4 체크리스트 등
2. 수정 순서 결정 (의존성 분석):
   - 먼저: 구조 수정 (포맷 통일)
   - 다음: 신규 삽입 (Phase 테이블)
   - 다음: 참조 구체화 (§6 참조)
   - 다음: 내용 추가 (§6 새 항목)
   - 마지막: 수치 갱신 (행 수 변동 반영)
3. 영향 분석 (Ripple Map 예비):
   - 각 수정이 영향을 미치는 다른 섹션 식별
4. 예상 행 수 변화

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase2\v12_update_plan.md`

**포맷**:
```markdown
# v12 Phase 2-F: PART2 업데이트 계획

## 수정 유형별 요약
| 유형 | 건수 | 예상 추가 행 |
|------|-----:|----------:|
| 신규 삽입 | X | +X |
| 참조 구체화 | X | 0 |
| 내용 추가 | X | +X |
| 구조 수정 | X | ±X |
| 수치 갱신 | X | 0 |

## 수정 순서
1. ...
2. ...

## 예상 버전
- 현재: v25.2.0 (5,858행)
- 목표: v26.0.0 (예상 ~X행)

## 수정 건별 상세
| # | 유형 | 대상 섹션 | 수정 내용 | 영향 범위 | 순서 |
|---|------|---------|---------|---------|------|
```

---

### 교차검증 ⑤: 최종 목록 + 계획 정합성

**작업**:
1. 최종 누락 목록 건수 = 2-A~2-D에서 확정한 건수 합산 일치 확인
2. Patch Plan 건수 = 최종 누락 목록 건수 + §6 구체화 건수 + 패턴 해소 건수 일치 확인
3. BLOCKER 잔여 여부 확인 (0건이어야 Phase 3 진행 가능)
4. 수정 순서 의존성 교차 확인

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase2\v12_phase2_verdict.md`

---

## 산출물 전수 목록

| # | 파일 | 경로 |
|---|------|------|
| 1 | v10 교차 대사 | `v12_results/phase2/v12_v10_crosscheck.md` |
| 2 | v7 역방향 교차 | `v12_results/phase2/v12_v7_crosscheck.md` |
| 3 | 패턴 해소 방안 | `v12_results/phase2/v12_pattern_resolution.md` |
| 4 | §6 최종 매핑 | `v12_results/phase2/v12_s6_final_mapping.md` |
| 5 | 최종 누락 목록 | `v12_results/phase2/v12_final_missing_list.md` |
| 6 | 업데이트 계획 | `v12_results/phase2/v12_update_plan.md` |
| 7 | Phase 2 판정 | `v12_results/phase2/v12_phase2_verdict.md` |

---

## AI 오류 방지 규칙 (이 Phase에서 준수)

1. **독립 결과 우선**: v12 독립 결과가 v10과 다를 때, v25.2.0 현재 상태로 최종 판정
2. **v10 라인 참조 사용 금지**: v10 결과의 라인 번호는 v21~v23 기준. v25.2.0에서 직접 확인
3. **과잉 수정 방지**: PART2에 이미 있는 내용을 중복 추가하지 않도록 주의
4. **환각 금지**: 교차 대사 시 v10/v7 결과를 직접 파일에서 읽고 확인
5. **Patch Plan 실행 가능성**: 각 수정 건이 구체적이고 실행 가능한 수준으로 기술
6. **필드 값 enum 준수**: 심각도는 `BLOCKER`/`HIGH`/`MEDIUM`/`LOW`(4개)만 허용. `CRITICAL`, `P0/P1/P2`, `H/M/L` 축약 사용 금지. Phase 0~1에서 확정된 priority/category/source_group 값 변경 금지

---

## 완료 시 수행

1. 위 7개 산출물 파일 전수 존재 확인
2. `v12_phase_status.json` 업데이트:
   ```json
   {
     "phase2": {
       "status": "completed",
       "conversation": "대화 9",
       "pass": true/false,
       "started_at": "2026-03-XX",
       "completed_at": "2026-03-XX"
     }
   }
   ```
3. 최종 누락 건수 + 심각도 요약 출력
4. BLOCKER > 0이면 해소 방안 즉시 포함 (Phase 3에서 최우선 처리)
