# Phase -1: 기초 검증 (스킬 에이전트 오류 점검)

> **대화**: 대화 1
> **목표**: v6~v11 스킬 에이전트 재사용 전 오류 점검 + 기반 환경 확인
> **성격**: v12 파이프라인 진입 전 안전 점검. 여기서 FAIL이면 후속 Phase 진행 불가.

---

## Pre-check Protocol

**매 대화 시작 시 반드시 수행:**

```
① 본 계획 파일 읽기: D:\VAMOS\04. 구현단계\v12\v12_plan.md
② 본 프롬프트 읽기: D:\VAMOS\04. 구현단계\v12\prompts\phase-1_prompt.md
③ 진행 상태 확인: D:\VAMOS\04. 구현단계\v12\v12_results\v12_phase_status.json
④ Phase -1이 "pending" 상태인지 확인
⑤ 확인 완료 후 작업 시작
```

---

## 스킬 에이전트 실행 규칙

> **필수**: 본 Phase의 작업은 **Agent tool(스킬 에이전트)**을 활용하여 일관된 결과를 도출합니다.

1. **독립 검증**: 각 작업(-1A~-1E)은 가능한 Agent tool로 독립 실행하여 교차 오염 방지
2. **동일 템플릿**: 모든 산출물은 본 프롬프트에 정의된 출력 포맷 준수
3. **증거 기반**: 에이전트 결과에 evidence_source + evidence_line + evidence_text 필수
4. **재현성**: 동일 입력 → 동일 출력 보장을 위해 판정 기준을 명시적으로 적용

---

## 입력 파일 (전수 목록)

### 필수 입력

| # | 파일 | 경로 | 용도 |
|---|------|------|------|
| 1 | PART2 구현단계 | `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` | v25.2.0 현재 상태 확인 |
| 2 | v11 Adversarial Report | `D:\VAMOS\04. 구현단계\v11_results\phase15\v11_adversarial_report.md` | 미해결 패턴 5건 원본 |
| 3 | v11 Checkpoint | `D:\VAMOS\04. 구현단계\v11_results\v11_checkpoint.md` | v11 완료 상태 |
| 4 | v11 Phase Status | `D:\VAMOS\04. 구현단계\v11_results\v11_phase_status.json` | v11 Phase 2 결과 |
| 5 | v10 Feature Registry | `D:\VAMOS\04. 구현단계\v10_results\phase0-f\v10_feature_registry_final.json` | 샘플 검증용 |
| 6 | v10 Checkpoint | `D:\VAMOS\04. 구현단계\v10_results\v10_checkpoint.md` | v10 완료 상태 |

### 스킬 에이전트 프롬프트 (감사용)

| # | 파일 | 경로 |
|---|------|------|
| 7 | v6 프롬프트 | `C:\Users\dkscl\OneDrive\바탕 화면\VAMOS\04. 구현단계\VAMOS_검증_프롬프트_v6.md` |
| 8 | v7 프롬프트 | `C:\Users\dkscl\OneDrive\바탕 화면\VAMOS\04. 구현단계\VAMOS_검증_프롬프트_v7.md` |
| 9 | v8 프롬프트 | `C:\Users\dkscl\OneDrive\바탕 화면\VAMOS\04. 구현단계\VAMOS_검증_프롬프트_v8.md` |
| 10 | v9 프롬프트 | `D:\VAMOS\04. 구현단계\v9_pipeline_plan.md` |
| 11 | v10 프롬프트 | `D:\VAMOS\04. 구현단계\v10_pipeline_plan.md` |
| 12 | v11 프롬프트 | `D:\VAMOS\04. 구현단계\v11_pipeline_framework_skill.md` |

> ※ #7~#9 경로는 OneDrive 사용자 경로입니다. 경로 접근 불가 시 `D:\VAMOS\04. 구현단계\` 하위에 동일 파일명이 있는지 확인하거나, 대체 경로를 사용하세요.

### SOT 68개 파일 (수정일 확인용)

```
D:\VAMOS\docs\sot\
(68개 파일 전수 — v12_plan.md §2.1 참조)
```

---

## 작업 상세

### 작업 -1A: v11 미해결 패턴 5건 현재 상태 확인

**목적**: v11 적대적 재검증에서 발견된 5개 미해결 패턴이 v25.2.0에서 이미 해소되었는지, 아직 남아있는지 확인

**확인할 패턴 5건**:

| # | 패턴 | v11 원본 위치 | 확인 방법 |
|---|------|-------------|---------|
| 1 | **Pattern A: v10 연쇄 미갱신** | v10 대량 추가(+201행) 후 §6.13 작업량 테이블, §7.4 GO/NO-GO 체크리스트 등 연쇄 수정 대상이 모두 갱신되었는지 | PART2에서 §6.13, §7.4 검색 → 수치가 v25.2.0 현재 총 행수/항목수와 일치하는지 |
| 2 | **Pattern B: FIX-09 Gate 명칭 미전파** | v11에서 L3875, L3876, L3927, L3928 지적 | PART2에서 Stage Gate 명칭 일관성 확인. **주의**: v25.2.0에서 라인 번호 시프트되었으므로 라인 번호가 아닌 내용 기반 검색 |
| 3 | **V1 구조 고립** | 균일성 5/7 항목 ✗ | PART2 §3(V1)의 Phase 테이블 구조가 §4(V2)/§5(V3)와 동일 포맷인지 비교 |
| 4 | **V3 과적재** | 자기완결성 2.5/5 | PART2 §5(V3) Phase 테이블에서 "§6 참조" 비율 확인. V3가 다른 섹션 대비 과도하게 §6에 의존하는지 |
| 5 | **V2-P2 저커버리지** | 116건 중 프롬프트 10건만 | PART2 §4.2(V2 Phase 2) AI 프롬프트의 커버 범위 확인 |

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase-1\v12_pattern_check.md`

**포맷**:
```markdown
# v12 Phase -1A: v11 미해결 패턴 점검

| # | 패턴 | v11 원본 | v25.2.0 현재 상태 | 판정 | evidence_line | evidence_text |
|---|------|---------|-----------------|------|-------------|-------------|
| 1 | Pattern A | ... | ... | RESOLVED/OPEN | L번호 | 실제 텍스트 |
...

## 상세 분석
(패턴별 상세 — 각각 evidence 포함)
```

---

### 작업 -1B: v25.1.0/v25.2.0 편집 vs v11 Fix 충돌 점검

**목적**: v25.1.0과 v25.2.0에서 수행된 편집이 v11에서 적용한 Fix와 충돌하거나 되돌리지 않았는지 확인

**방법**:
1. PART2 v25.2.0의 changelog 섹션 읽기 (문서 상단 또는 하단)
2. v25.1.0과 v25.2.0에서 변경된 영역 식별
3. v11 Phase 2에서 적용한 수정 사항과 영역 비교
4. 충돌 여부 판정

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase-1\v12_v25_conflict.md`

**포맷**:
```markdown
# v12 Phase -1B: v25 편집 충돌 점검

## v25.1.0 변경 요약
(changelog 기반)

## v25.2.0 변경 요약
(changelog 기반)

## v11 Fix 목록
(v11 결과 기반)

## 충돌 분석
| # | v11 Fix | v25 편집 | 충돌 여부 | 상세 |
|---|---------|---------|---------|------|

## 판정: CONFLICT / NO_CONFLICT
```

---

### 작업 -1C: SOT 68개 파일 수정일 확인

**목적**: v10 실행 시점(2026-03-08~03-11) 이후 SOT 파일이 수정되었는지 확인. 수정된 파일이 있으면 v10 결과와 차이가 있을 수 있음.

**방법**:
1. SOT 68개 파일 경로: `D:\VAMOS\docs\sot\`
2. 각 파일의 수정일(last modified) 확인
3. 2026-03-11 이후 수정된 파일 식별
4. 수정된 파일의 v10 분석 영향도 판정

**실행 명령** (참고):
```bash
ls -la --time-style=full-iso "D:/VAMOS/docs/sot/" | sort -k6,7
```

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase-1\v12_sot_currency.md`

**포맷**:
```markdown
# v12 Phase -1C: SOT 68개 파일 수정일 점검

## 기준일: 2026-03-11 (v10 Pipeline 완료일)

| # | 파일명 | 수정일 | v10 분석 | v10 이후 수정 | 영향도 |
|---|--------|------|---------|-------------|--------|
| 1 | BASE-1.3_... | 2026-03-XX | ✅/❌ | YES/NO | HIGH/LOW/NONE |
...

## v10 이후 수정 파일 (상세)
(수정된 파일만 — 변경 내용 추정)

## 판정: CURRENCY_OK / CURRENCY_DRIFT
```

---

### 작업 -1D: v10 Feature Registry 샘플 30건 유효성 검증

**목적**: v10 Feature Registry(3,940건)의 품질 샘플 검증. SOT 원본과 대조하여 추출 정확도 확인.

**방법**:
1. `v10_feature_registry_final.json` 로드
2. 층화 샘플링: V0 5건 + V1 10건 + V2 10건 + V3 5건 = 30건
3. 각 Feature의 `source_file` + `source_line` → SOT 원본 파일에서 실제 확인
4. Feature 설명, version_scope, extractable 판정의 정확도 검증

**주의**: v10은 SRC 43개 기준. SOT 68개 중 25개는 v10에 없음. 샘플은 v10이 분석한 43개 범위 내에서 추출.

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase-1\v12_registry_validity.md`

**포맷**:
```markdown
# v12 Phase -1D: v10 Feature Registry 샘플 검증

## 샘플링 방법
- 층화 샘플링: V0(5) + V1(10) + V2(10) + V3(5) = 30건

## 샘플 검증 결과
| # | feature_id | version | source_file | 원본 확인 | 정확도 | 비고 |
|---|-----------|---------|------------|---------|--------|------|
| 1 | ... | V0 | ... | ✅/❌ | EXACT/PARTIAL/WRONG | ... |
...

## 통계
- 정확: X/30 (X%)
- 부분: X/30 (X%)
- 오류: X/30 (X%)

## 판정: VALID (≥80% 정확) / INVALID
```

---

### 작업 -1E: 스킬 에이전트 재사용 패턴 확정 + 오류 목록 정리

**목적**: v6~v11 스킬 에이전트 프롬프트를 읽고, 재사용 가능한 패턴과 알려진 오류를 정리

**방법**:
1. v6~v11 프롬프트 파일 6개 읽기 (§2 입력 파일 목록 참조)
2. 각 프롬프트에서 핵심 패턴 식별 (v12_plan.md §3.2 대조)
3. 알려진 오류 목록 갱신 (v12_plan.md §3.1 대조 + 추가 발견)
4. v12 Phase별 적용 계획 확정

**확인할 알려진 오류** (v12_plan.md §3.1):

| 출처 | 오류 | v12 대응 |
|------|------|---------|
| v7~v8 | 라인 번호 기반 참조 (v25.2.0 시프트 → 무효) | Phase 0 인덱스 재구축 |
| v10 | SRC 43개만 분석 (25개 미분석) | Phase 0 SOT 68개 전수 |
| v10 | Feature Registry v21~v23 기준 | Phase 0 독립 구축 |
| v11 | Pattern A~B + V1/V3/V2-P2 미해결 | Phase -1A에서 확인 완료 |
| v11 | 적대적 FP율 19.7% | v12 FP 기준 강화 |

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase-1\v12_agent_pattern_audit.md`

**포맷**:
```markdown
# v12 Phase -1E: 스킬 에이전트 감사

## 1. 재사용 패턴 (확정)
| # | 패턴 | 출처 | v12 적용 위치 | 오류 유무 | 대응 |
|---|------|------|-------------|---------|------|

## 2. 알려진 오류 (최종)
| # | 출처 | 오류 | 심각도 | v12 대응 |
|---|------|------|--------|---------|

## 3. 추가 발견 오류
(이번 감사에서 새로 발견한 문제)

## 4. v12 Phase별 에이전트 적용 매트릭스
| Phase | 사용 패턴 | 오류 주의사항 |
|-------|---------|-------------|
```

---

### 교차검증 ①: Phase -1 전체 PASS/FAIL

**방법**: 위 5개 작업 완료 후 종합 판정

**판정 기준**:
- -1A: 5건 패턴 전수 확인 완료 (OPEN이면 Phase 2-C에서 해소 필요, Phase -1 자체는 PASS)
- -1B: CONFLICT가 있으면 해소 방안 명시 필요 (해소 방안 없으면 FAIL)
- -1C: CURRENCY_DRIFT가 있으면 영향도 분석 필요 (HIGH 영향 파일 있으면 주의)
- -1D: INVALID이면 v10 Registry 재구축 필요 (Phase 0에서 독립 구축하므로 PASS 가능)
- -1E: 오류 목록 확정 필수

**전체 PASS 조건**: 위 5개 작업 모두 완료 + 해소 불가능한 BLOCKER 없음

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase-1\v12_phase-1_verdict.md`

---

## 산출물 전수 목록

| # | 파일 | 경로 |
|---|------|------|
| 1 | 패턴 점검 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase-1\v12_pattern_check.md` |
| 2 | v25 충돌 점검 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase-1\v12_v25_conflict.md` |
| 3 | SOT 수정일 점검 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase-1\v12_sot_currency.md` |
| 4 | Registry 유효성 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase-1\v12_registry_validity.md` |
| 5 | 에이전트 감사 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase-1\v12_agent_pattern_audit.md` |
| 6 | Phase -1 판정 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase-1\v12_phase-1_verdict.md` |

---

## AI 오류 방지 규칙 (이 대화에서 준수)

1. **환각 금지**: 모든 판정에 `evidence_source` + `evidence_line` + `evidence_text` 3개 필드 필수
2. **라인 번호 주의**: v10/v11의 라인 참조를 그대로 사용하지 말 것. v25.2.0에서 시프트되었으므로 내용 기반 검색
3. **부분 읽기 금지**: 파일 전체를 읽을 것. `limit` 사용 시 나머지도 반드시 후속 읽기
4. **추측 금지**: 파일을 직접 열어 확인하지 않은 내용은 판정에 사용하지 말 것
5. **결과 저장 필수**: 모든 작업 결과를 위 산출물 경로에 파일로 저장할 것

---

## 완료 시 수행

1. 위 6개 산출물 파일 전수 생성 확인
2. `v12_phase_status.json` 업데이트:
   ```json
   {
     "phase-1": {
       "status": "completed",
       "conversation": "대화 1",
       "pass": true/false,
       "started_at": "2026-03-XX",
       "completed_at": "2026-03-XX"
     }
   }
   ```
3. FAIL이면 사유 기재 + 다음 Phase 진행 불가 명시
