# v13 Phase 0-C/D/E/F: 불일치 확정 + 수정안 + 적대적 검증 + 반영

> **버전**: v13.2.0 (2계층 검증 아키텍처 반영)
> **대화**: 대화 5~6 (2개 대화)
> **목표**: Phase 0-B 크로스 매칭 결과를 확정 → 수정안 도출 → 적대적 검증 → SOT 수정 반영
> **성격**: v13 Phase 0의 최종 단계. SOT 정합성 확보 후 Phase 1~7 진행 가능.
> **선행 조건**: Phase 0-B 완료 (CM-1~CM-8 산출물 8개 전수 존재) + **EA 15개 전수 quality-gate SILVER 이상**

---

## Pre-check Protocol

```
① 본 계획 파일 읽기: D:\VAMOS\04. 구현단계\v13_plan.md (§3.0 + §5 Phase 0 부분)
② 본 프롬프트 읽기: D:\VAMOS\04. 구현단계\v13\prompts\phase0_CDF_consolidate_fix_prompt.md
③ Phase 0-A 산출물 15개 존재 확인:
   D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA01_claude_md.json ~ v13_EA15_etc.json
④ [필수] EA 15개 전수 quality-gate 검증 결과 확인:
   D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\validation\
   → 15개 전수 SILVER 이상 확인 (BRONZE/REJECT 있으면 진행 불가)
⑤ Phase 0-B 산출물 8개 존재 확인:
   D:\VAMOS\04. 구현단계\v13_results\phase0\cross_match\v13_CM01_values.json ~ v13_CM08_references.json
⑥ PART2 최신본 확인:
   D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md (6,139줄, v26.0.0)
⑦ SOT 원본 디렉토리 확인:
   D:\VAMOS\docs\sot\ (68개 파일, 89,363줄)
⑧ 검증 스킬 확인: /validate, /audit, /sot-check, /quality-gate 사용 가능 여부
⑨ 확인 완료 후 작업 시작
```

---

## 핵심 원칙: 환각/오류 방지 규칙

```
R1: 불일치 확정 시 반드시 양쪽 SOT 원문(source_text + source_line)을 인용
R2: 수정안 도출 시 정본 우선순위 적용: RULE 1.3 > PLAN 3.0 > MASTER_SPEC > DESIGN 2.0 LOCK
R3: 수정안은 "어떤 파일의 몇 행을 어떻게 변경" 수준의 구체적 diff 형태
R4: 적대적 에이전트는 CRITICAL 판정 시 반드시 2개 이상의 SOT 근거를 제시
R5: 동일 항목이 3개 이상 SOT에서 서로 다른 값이면 SOURCE_CONFLICT로 에스컬레이션
R6: SOT 수정은 반드시 사용자 승인 후 실행. 자동 수정 금지.
R7: [신규] 모든 불일치 판정의 source_text는 SOT 원본에서 grep 재확인 (DV-4 수준)
R8: [신규] Phase 0-E 적대적 검증은 /audit 스킬과 연동하여 실행
```

---

# ═══ 대화 5: Phase 0-C + Phase 0-D ═══

---

## Phase 0-C: 불일치 목록 확정 + 심각도 분류

> **에이전트**: 1개 종합 에이전트 (CM-1~8 결과 통합)

### 작업

1. **CM-1~8 로드**: 8개 크로스 매칭 결과 전수 로드
2. **INCONSISTENT + SOURCE_CONFLICT 항목만 추출**: CONSISTENT와 SINGLE_SOURCE는 제외
3. **중복 제거**: 동일 불일치가 여러 CM에서 감지된 경우 통합
4. **심각도 재판정**: 아래 기준으로 최종 심각도 확정

#### 심각도 판정 기준

| 심각도 | 기준 | 예시 |
|--------|------|------|
| `CRITICAL` | LOCK/FREEZE 값 불일치 OR 구현 시 코드가 달라지는 수치 불일치 | 모듈 수 불일치, 비용 상한 불일치 |
| `WARNING` | 카운트/목록 불일치, 분류 체계 충돌 (구현에 간접 영향) | COND MEDIUM 9 vs 8, 3-tier vs 4-tier |
| `INFO` | 명칭 변형, 범위 표현 차이 (의미 동일 가능, 독자 혼동 수준) | 불변구역 7 vs NEVER_AUTO 10 (범위 다름) |

5. **기존 3건 확인**: v13_plan.md §2에 명시된 3건이 목록에 포함되는지 확인
   - 불일치 A: 7개 불변구역 vs NEVER_AUTO 10개 → 목록에 있어야 함
   - 불일치 B: COND MEDIUM 9 vs 8, LOW 3 vs 4 → 목록에 있어야 함
   - 불일치 C: 3-tier vs 4-tier 모듈 분류 → 목록에 있어야 함

### 산출물

**파일**: `D:\VAMOS\04. 구현단계\v13_results\phase0\v13_sot_inconsistency_list.json`

```json
{
  "metadata": {
    "version": "v13",
    "created": "2026-03-XX",
    "total_inconsistencies": 0,
    "severity": { "CRITICAL": 0, "WARNING": 0, "INFO": 0 },
    "known_issues_confirmed": {
      "issue_A_immutable_vs_never_auto": true,
      "issue_B_cond_count": true,
      "issue_C_module_tier": true
    }
  },
  "inconsistencies": [
    {
      "inconsistency_id": "INC-001",
      "severity": "WARNING",
      "type": "C2",
      "key": "COND_PRIORITY_MEDIUM",
      "description": "COND MEDIUM 우선순위 카운트 불일치",
      "sources": [
        {
          "source_file": "PART2 요약 테이블",
          "source_line": 0,
          "source_text": "MEDIUM: 9",
          "value": 9
        },
        {
          "source_file": "PART2 상세 목록",
          "source_line": 0,
          "source_text": "MEDIUM 항목 8개 나열",
          "value": 8
        }
      ],
      "analysis": "단순 카운팅 오류. 상세 목록이 정본.",
      "related_cm": ["CM-2"]
    }
  ]
}
```

---

## Phase 0-D: SOT 수정안 도출 + 영향 범위 분석

> **에이전트**: 1개 수정안 에이전트

### 작업

1. **불일치 목록 로드**: `v13_sot_inconsistency_list.json`
2. **CRITICAL/WARNING 항목에 대해 수정안 도출**:
   - 정본 우선순위에 따라 "어느 쪽이 정본인지" 결정
   - 정본이 아닌 쪽의 구체적 수정 내용 명시
3. **INFO 항목은 "명시 추가" 또는 "주석 추가" 수준 수정안**
4. **영향 범위 분석**: 각 수정이 다른 SOT/PART2에 미치는 ripple effect 확인

#### 정본 우선순위 (v12 기준 계승)

```
1순위: RULE 1.3 (BASE-1.3)
2순위: PLAN 3.0
3순위: MASTER_SPECIFICATION
4순위: DESIGN 2.0 LOCK (D2.0-01 ~ D2.0-08의 LOCK 값)
5순위: DESIGN 2.1 (D2.1-A1 ~ D2.1-Q1)
6순위: PHASE_B (B1~B7)
7순위: CLAUDE.md
8순위: 기타 (BEGINNER, READINESS, STEP7 등)
```

#### 수정안 유형

| 유형 | 설명 | 예시 |
|------|------|------|
| `FIX_VALUE` | 값을 정본 기준으로 수정 | COND MEDIUM 9 → 8 |
| `ADD_CLARIFICATION` | 범위/기준 구분 명시 추가 | "정책 수준 7개" vs "시행 수준 10개" 구분 문구 |
| `ADD_MAPPING` | 분류 체계 매핑 테이블 추가 | 3-tier ↔ 4-tier 매핑 |
| `NO_FIX` | 수정 불필요 (설계 의도) | 의도적으로 다른 범위를 사용하는 경우 |

### 산출물

**파일**: `D:\VAMOS\04. 구현단계\v13_results\phase0\v13_sot_fix_proposals.json`

```json
{
  "metadata": {
    "version": "v13",
    "created": "2026-03-XX",
    "total_proposals": 0,
    "by_type": { "FIX_VALUE": 0, "ADD_CLARIFICATION": 0, "ADD_MAPPING": 0, "NO_FIX": 0 }
  },
  "proposals": [
    {
      "proposal_id": "FIX-001",
      "inconsistency_id": "INC-001",
      "type": "FIX_VALUE",
      "target_file": "D:\\VAMOS\\docs\\guides\\VAMOS_구현가이드_PART2_구현단계.md",
      "target_line": 0,
      "current_text": "MEDIUM: 9",
      "proposed_text": "MEDIUM: 8",
      "authority": "PART2 상세 목록 (정본)",
      "authority_rule": "동일 문서 내 상세 > 요약",
      "ripple_effects": [
        {
          "file": "PART2",
          "line": 0,
          "description": "요약 테이블의 MEDIUM 카운트 수정"
        }
      ]
    }
  ]
}
```

---

ㄹ

---

## Phase 0-E: 적대적 재검증 (2계층 아키텍처 연동)

> **에이전트**: 1개 적대적 에이전트 (Devil's Advocate)
> **목적**: Phase 0-C/D의 불일치 판정과 수정안이 정당한지 반박 시도
> **스킬 연동**: `/audit` 스킬의 AD-1~AD-3 검증을 Phase 0 맥락에 적용

### 2단계 적대적 검증

#### Step 1: /audit 스킬 기반 자동 검증

각 EA 산출물에 대해 `/audit` 스킬을 실행하여 기계적으로 탐지 가능한 문제를 먼저 식별:

| /audit 검증 항목 | Phase 0-E 적용 |
|-----------------|----------------|
| AD-1: 환각 탐지 (랜덤 20% 샘플링) | 불일치 판정의 source_text가 실제 SOT에 존재하는지 확인 |
| AD-2: 값 변조 탐지 | 수정안의 current_text/proposed_text가 원본과 일치하는지 확인 |
| AD-3: 약점 패턴 분석 | W1(카운트↔목록), W3(값범위), W4(분류체계) 패턴 재점검 |

#### Step 2: AI 의미적 반박 (Devil's Advocate)

/audit 결과를 참고하면서 아래 반박을 시도:

### 작업

1. **입력 로드**:
   - `v13_sot_inconsistency_list.json` (불일치 목록)
   - `v13_sot_fix_proposals.json` (수정안)
   - 해당 SOT 원본 파일들 (직접 읽기)
   - `/audit` 실행 결과 (있는 경우)

2. **각 불일치 항목에 대해 반박 시도**:

| 반박 유형 | 설명 |
|----------|------|
| `FP_CHALLENGE` | "이것은 실제로는 불일치가 아니다" — 동일 의미를 다른 표현으로 쓴 것일 수 있음 |
| `SEVERITY_CHALLENGE` | "심각도가 과대평가되었다" — CRITICAL이 아니라 WARNING이어야 함 |
| `FIX_CHALLENGE` | "수정안이 잘못되었다" — 정본 우선순위 오적용, 또는 의도적 설계를 깨뜨림 |
| `MISS_CHALLENGE` | "놓친 불일치가 있다" — CM에서 탐지하지 못한 추가 불일치 제시 |
| `HALLUCINATION_CHALLENGE` | [신규] "불일치 판정 자체가 환각이다" — source_text가 SOT에 없거나 다름 |

3. **각 반박에 대해 2개 이상의 SOT 근거 제시** (R4)
4. **[신규] 반박 시 DV-4 수준 검증**: source_text를 SOT 원본에서 grep으로 직접 확인
5. **반박 성공 시**: 해당 항목의 심각도 변경 또는 수정안 철회 권고
6. **반박 실패 시**: 원래 판정 유지 확인

### 산출물

**파일**: `D:\VAMOS\04. 구현단계\v13_results\phase0\v13_adversarial_review.json`

```json
{
  "metadata": {
    "version": "v13",
    "created": "2026-03-XX",
    "total_challenges": 0,
    "results": {
      "challenge_sustained": 0,
      "challenge_rejected": 0
    },
    "error_rate": "N%",
    "verdict": "PASS|FAIL (오판율 ≤10%이면 PASS)"
  },
  "challenges": [
    {
      "challenge_id": "ADV-001",
      "target": "INC-001",
      "challenge_type": "FP_CHALLENGE",
      "argument": "COND MEDIUM 9 vs 8은 단순 오타가 아니라 ...",
      "evidence": [
        { "source_file": "...", "source_line": 0, "source_text": "..." },
        { "source_file": "...", "source_line": 0, "source_text": "..." }
      ],
      "result": "REJECTED",
      "reason": "상세 목록에서 실제 나열된 MEDIUM 항목이 8개이므로 요약의 9는 카운팅 오류가 맞음"
    }
  ]
}
```

---

## Phase 0-F: SOT 수정 반영 (2계층 검증 연동)

> **실행 조건**: Phase 0-E 적대적 검증 PASS + **사용자 승인**
> **자동 실행 금지**: 반드시 사용자에게 수정 목록을 제시하고 승인을 받은 후 실행

### 작업

1. **수정 전 준비**:
   - 수정 대상 SOT 파일 백업 (파일별 `_backup_v13` 접미사로 복사)
   - 백업 경로: `D:\VAMOS\04. 구현단계\v13_results\phase0\fixes\`

2. **사용자에게 수정 목록 제시**:
   ```
   [수정 목록]
   FIX-001: PART2 L{N} — COND MEDIUM 9 → 8
   FIX-002: CLAUDE.md L{N} — 불변구역 범위 구분 명시 추가
   FIX-003: ...

   승인하시겠습니까? (Y/N)
   ```

3. **승인 후 수정 실행**:
   - Edit tool로 각 수정 적용
   - 수정마다 즉시 검증 (수정된 행 재읽기)

4. **[신규] 수정 후 검증 파이프라인**:
   - 수정된 SOT 파일에 대해 `/sot-check` 실행 → 수정이 올바르게 반영되었는지 확인
   - 관련 EA가 있으면 해당 EA의 source_text/source_line이 여전히 유효한지 DV-4 재검증
   - 수정으로 인해 새로운 불일치가 발생하지 않는지 ripple effect 확인

5. **수정 기록 생성**:
   - 각 수정의 before/after diff 기록
   - Delta 목록 생성 (Phase 1~7에서 참조)

### 산출물

**파일 1**: `D:\VAMOS\04. 구현단계\v13_results\phase0\fixes\v13_sot_corrections_applied.md`

```markdown
# v13 Phase 0-F: SOT 수정 기록

| # | 파일 | 행 | before | after | 근거 |
|---|------|-----|--------|-------|------|
| 1 | PART2 | L{N} | MEDIUM: 9 | MEDIUM: 8 | INC-001, FIX-001 |
| 2 | ... | ... | ... | ... | ... |
```

**파일 2**: `D:\VAMOS\04. 구현단계\v13_results\phase0\v13_sot_delta.json`

> **중요**: 이 파일은 Phase 1~7에서 반드시 참조해야 합니다 (ABD-4).

```json
{
  "metadata": {
    "version": "v13",
    "created": "2026-03-XX",
    "total_corrections": 0,
    "affected_files": []
  },
  "deltas": [
    {
      "delta_id": "DELTA-001",
      "fix_id": "FIX-001",
      "file": "PART2",
      "file_path": "D:\\VAMOS\\docs\\guides\\VAMOS_구현가이드_PART2_구현단계.md",
      "line": 0,
      "before": "MEDIUM: 9",
      "after": "MEDIUM: 8",
      "affected_keys": ["COND_PRIORITY_MEDIUM"],
      "impact_on_phases": "Phase 1~7에서 COND MEDIUM 관련 검증 시 값 8 기준 적용"
    }
  ]
}
```

**파일 3 (백업들)**: `D:\VAMOS\04. 구현단계\v13_results\phase0\fixes\{원본파일명}_backup_v13.md`

---

## Phase 0 최종 판정

### 완료 조건 (PC-1 ~ PC-9)

| # | 조건 | 확인 방법 |
|---|------|----------|
| PC-1 | SOT 68개 파일 전수 읽기 완료 (100%) | EA-1~15 metadata.total_lines_read 합산 ≈ 89,363 |
| PC-2 | C1~C8 유형별 크로스 매칭 전수 완료 | CM-1~8 산출물 8개 존재 |
| PC-3 | 기존 3건 불일치 해소 확인 | inconsistency_list에서 3건 확인 + fix 적용 |
| PC-4 | 신규 불일치 CRITICAL 0건 잔여 | fix 후 CRITICAL 잔여 0 |
| PC-5 | 적대적 재검증 오판율 ≤10% | adversarial_review.error_rate |
| PC-6 | 사용자 승인 완료 | 수정 목록 승인 기록 |
| PC-7 | [신규] EA 15개 전수 quality-gate SILVER 이상 | validation/ 디렉토리 DV 결과 확인 |
| PC-8 | [신규] /audit 스킬 실행 완료 | audit/ 디렉토리 결과 존재 |
| PC-9 | [신규] 수정 후 /sot-check 확인 완료 | sot_check/ 디렉토리 결과 존재 |

### 판정 산출물

**파일**: `D:\VAMOS\04. 구현단계\v13_results\phase0\v13_phase0_verdict.md`

```markdown
# v13 Phase 0 판정서

## 결과: PASS / FAIL

| # | 조건 | 판정 |
|---|------|------|
| PC-1 | SOT 68개 전수 읽기 | PASS/FAIL |
| PC-2 | C1~C8 크로스 매칭 완료 | PASS/FAIL |
| PC-3 | 기존 3건 해소 | PASS/FAIL |
| PC-4 | 신규 CRITICAL 0건 | PASS/FAIL |
| PC-5 | 적대적 오판율 ≤10% | PASS/FAIL |
| PC-6 | 사용자 승인 | PASS/FAIL |

## 통계
- 추출 항목: {N}건 (EA-1~15)
- 크로스 비교: {N}건 (CM-1~8)
- 불일치: {N}건 (CRITICAL: {N}, WARNING: {N}, INFO: {N})
- 수정: {N}건
- 적대적 반박: {N}건 (채택: {N}, 기각: {N})

## Delta 요약
- 수정된 파일: {목록}
- Phase 1~7 영향: {요약}
```

---

## 전체 Phase 0 산출물 목록

| # | 파일 | 경로 | Phase |
|---|------|------|-------|
| 1~15 | EA-1~15 추출 JSON | `v13_results/phase0/extraction/v13_EA{01~15}_*.json` | 0-A |
| 16~23 | CM-1~8 매칭 JSON | `v13_results/phase0/cross_match/v13_CM{01~08}_*.json` | 0-B |
| 24 | 불일치 확정 목록 | `v13_results/phase0/v13_sot_inconsistency_list.json` | 0-C |
| 25 | 수정안 | `v13_results/phase0/v13_sot_fix_proposals.json` | 0-D |
| 26 | 적대적 검증 | `v13_results/phase0/v13_adversarial_review.json` | 0-E |
| 27 | 수정 기록 | `v13_results/phase0/fixes/v13_sot_corrections_applied.md` | 0-F |
| 28 | Delta 목록 | `v13_results/phase0/v13_sot_delta.json` | 0-F |
| 29 | 백업 파일들 | `v13_results/phase0/fixes/*_backup_v13.md` | 0-F |
| 30 | Phase 0 판정서 | `v13_results/phase0/v13_phase0_verdict.md` | 0-F |

---

## 2계층 검증 아키텍처 연동 (Phase 0-CDF 전체)

### Layer A (결정론적 검증) — 이미 완료 상태 확인

Phase 0-CDF 진입 시 EA 15개 전수가 DV-1~DV-7 통과 + quality-gate SILVER 이상이어야 합니다.
이 검증은 Phase 0-A에서 완료되었으므로 Pre-check에서 결과만 확인합니다.

### Layer B (AI 의미적 검증) — Phase 0-E에서 활용

| 단계 | 스킬 | 역할 |
|------|------|------|
| Phase 0-C (확정) | `/sot-check` | 불일치 항목의 SOT 원문 재확인 |
| Phase 0-D (수정안) | `/validate` | 수정안 JSON 스키마/정합성 검증 |
| Phase 0-E (적대적) | `/audit` | AD-1~AD-3 자동 검증 + Devil's Advocate 의미적 반박 |
| Phase 0-F (반영) | `/sot-check` | 수정 후 원본 대조 확인 |

### 검증 결과 저장 경로

```
v13_results/phase0/
├── extraction/validation/     # EA DV 검증 결과 (Phase 0-A에서 생성)
├── extraction/audit/          # EA /audit 결과
├── extraction/sot_check/      # EA /sot-check 결과
├── cross_match/               # CM-1~8 크로스 매칭 결과
└── fixes/                     # Phase 0-F 수정 기록 + 백업
```

---

## AI 오류 방지 규칙 (이 Phase에서 준수)

1. **환각 금지**: 불일치/수정안 모두 SOT 원문 인용으로 뒷받침
2. **정본 우선순위 엄수**: 수정안 도출 시 반드시 정본 우선순위 적용
3. **자동 수정 금지**: SOT 수정은 반드시 사용자 승인 후 실행
4. **백업 필수**: 수정 전 반드시 원본 백업
5. **Delta 기록 필수**: Phase 1~7에서 참조할 Delta 목록 반드시 생성
6. **적대적 독립성**: 적대적 에이전트는 Phase 0-C/D와 다른 프롬프트 맥락에서 실행
7. **CRITICAL 0건 목표**: Phase 0 완료 시 CRITICAL 잔여 0건이어야 Phase 1 진행 가능
8. **[신규] DV-4 수준 사실 확인**: 모든 source_text 인용은 SOT 원본에서 grep 재확인
9. **[신규] /audit 필수 실행**: Phase 0-E에서 /audit 스킬을 1회 이상 실행하여 AD-1~AD-4 검증
10. **[신규] 수정 후 /sot-check**: Phase 0-F에서 수정된 파일은 반드시 /sot-check로 원본 대조

---

## 🔍 사용자 확인 체크리스트 (Phase 0-CDF에서 2회 생성)

> **Claude는 대화 5 완료 시(0-C/D) + 대화 6 완료 시(0-E/F)에 각각 체크리스트를 제출합니다.**

### 대화 5 완료 시 (Phase 0-C/D: 불일치 확정 + 수정안)

```
═══════════════════════════════════════════════════
🔍 사용자 확인 체크리스트 (Phase 0-C/D 완료)
═══════════════════════════════════════════════════

■ 확인 항목 1: 불일치 판정 근거 직접 확인 (CRITICAL 전수 + WARNING 3건)
  [확인1-1] INC-{ID}: {불일치 설명}
            심각도: CRITICAL
            근거 A: 파일 {path_A}, 행 {line_A}
                    → 텍스트: "{source_text_A}"
                    → 사용자 확인: 해당 행에 텍스트 있음? ✅/❌
            근거 B: 파일 {path_B}, 행 {line_B}
                    → 텍스트: "{source_text_B}"
                    → 사용자 확인: 해당 행에 텍스트 있음? ✅/❌
            → 양쪽 값이 실제로 다름? ✅/❌

  ... (CRITICAL 전수 + WARNING 무작위 3건)

■ 확인 항목 2: 기존 3건 불일치 확정 확인
  [확인2-1] 불일치 A → INC-{ID}로 확정됨: ✅/❌
  [확인2-2] 불일치 B → INC-{ID}로 확정됨: ✅/❌
  [확인2-3] 불일치 C → INC-{ID}로 확정됨: ✅/❌

■ 확인 항목 3: 수정안 타당성 확인 (CRITICAL 수정안 전수)
  [확인3-1] FIX-{ID}: {수정 설명}
            대상: {파일명}, 행 {line}
            변경: "{before}" → "{after}"
            정본 근거: {authority}
            → 사용자 판단: 수정이 맞음? ✅/❌

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ 가 있으면 해당 항목 재검토 요청.
모두 ✅ 이면 Phase 0-E (적대적 검증)으로 진행.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 대화 6 완료 시 (Phase 0-E/F: 적대적 검증 + 수정 반영)

```
═══════════════════════════════════════════════════
🔍 사용자 확인 체크리스트 (Phase 0-E/F 완료 — Phase 0 최종)
═══════════════════════════════════════════════════

■ 확인 항목 1: 적대적 검증에서 채택된 반박 확인
  (채택된 반박이 있는 경우만)
  [확인1-1] ADV-{ID}: {반박 내용 요약}
            원래 판정: {INC-ID} → {severity}
            반박 후: {변경된 severity 또는 철회}
            → 사용자 판단: 반박이 타당함? ✅/❌

■ 확인 항목 2: SOT 수정 전/후 직접 확인 (전수)
  [확인2-1] FIX-{ID}: {파일명}, 행 {line}
            수정 전: "{before}" → 파일에서 직접 확인: ✅/❌
            수정 후: "{after}" → 수정이 올바르게 반영됨: ✅/❌

  ... (수정 건수만큼 반복)

■ 확인 항목 3: Phase 0 최종 판정 확인
  [확인3-1] PC-1: SOT 68개 전수 읽기 → ✅/❌
  [확인3-2] PC-2: CM-1~8 완료 → ✅/❌
  [확인3-3] PC-3: 기존 3건 해소 → ✅/❌
  [확인3-4] PC-4: CRITICAL 잔여 0건 → ✅/❌
  [확인3-5] PC-5: 적대적 오판율 ≤10% → ✅/❌ (실제: __%)
  [확인3-6] PC-6: 사용자 승인 → ✅/❌
  [확인3-7] PC-7: EA 15개 quality-gate SILVER+ → ✅/❌
  [확인3-8] PC-8: /audit 실행 완료 → ✅/❌
  [확인3-9] PC-9: /sot-check 확인 완료 → ✅/❌

■ 확인 항목 4: Delta 파일 확인
  [확인4-1] v13_sot_delta.json 존재: ✅/❌
  [확인4-2] 수정된 파일 목록이 실제 수정과 일치: ✅/❌

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
모든 PC가 ✅ 이면 Phase 0 완료 → Phase 1 진행 가능.
PC 하나라도 ❌ 이면 해당 항목 재작업 후 재확인.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 확인 항목 선택 기준

- **대화 5 확인1**: CRITICAL 전수 + WARNING 무작위 3건. 양쪽 SOT 파일 경로+행 번호 제시.
- **대화 5 확인3**: 수정안의 current_text가 실제 파일에 있는지 사용자가 확인.
- **대화 6 확인2**: 수정 전/후를 사용자가 파일을 열어 직접 확인. **이것이 가장 중요한 확인.**
- **대화 6 확인3**: PC-1~PC-9 전수. Claude가 판정값을 채우고 사용자가 최종 승인.
