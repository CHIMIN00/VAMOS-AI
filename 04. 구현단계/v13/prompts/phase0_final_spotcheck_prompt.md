# v13 Phase 0 최종 스팟체크 + 구현 진입 사전 점검

> **버전**: v13.2.0
> **대화**: 대화 7 (Phase 0 마무리 + PART2 구현 진입 게이트)
> **목표**: Phase 0-F에서 적용한 SOT 수정 18건의 PART2 전파 여부 확인 + 보류 2건 처리 + 구현 착수 최종 판정
> **선행 조건**: 대화 5~6에서 Phase 0-A~F 완료, SOT 18건 수정 적용 완료

---

## Pre-check Protocol

```
① 본 프롬프트 읽기: D:\VAMOS\04. 구현단계\v13\prompts\phase0_final_spotcheck_prompt.md
② v13 계획서 읽기: D:\VAMOS\04. 구현단계\v13_plan.md (§2 불일치 현황, §3 전략)
③ Phase 0 판정서 읽기: D:\VAMOS\04. 구현단계\v13_results\phase0\v13_phase0_verdict.md
④ Delta 목록 읽기: D:\VAMOS\04. 구현단계\v13_results\phase0\v13_sot_delta.json (18건 전수)
⑤ 적대적 검증 읽기: D:\VAMOS\04. 구현단계\v13_results\phase0\v13_adversarial_review.json
⑥ 수정 기록 읽기: D:\VAMOS\04. 구현단계\v13_results\phase0\fixes\v13_sot_corrections_applied.md
⑦ PART2 최신본 확인: D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md (6,139줄)
⑧ SOT 디렉토리 확인: D:\VAMOS\docs\sot\ (68개 파일)
⑨ 확인 완료 후 작업 시작
```

---

## 핵심 원칙

```
R1: 모든 grep 결과는 원본 파일의 실제 행 번호와 텍스트를 인용
R2: 수정 필요 시 반드시 사용자 승인 후 실행
R3: 판정은 근거와 함께 제시 (PASS/FAIL + 근거 행 번호)
R4: FIX-008/010은 정확한 삽입 위치를 SOT 원본에서 직접 확인 후 결정
```

---

## 현재 상태 요약 (대화 5~6에서 완료된 내용)

### Phase 0 전체 완료 현황
- **Phase 0-A**: EA-1~15 추출 완료 (68개 SOT, ~89,363줄 전수 읽기)
- **Phase 0-B**: CM-1~8 크로스 매칭 완료 (8개 유형별)
- **Phase 0-C**: 불일치 31건 확정 (CRITICAL 5 → 적대적 검증 후 2, WARNING 18→15, INFO 8→14)
- **Phase 0-D**: 수정안 22건 도출
- **Phase 0-E**: 적대적 검증 PASS (15건 반박 중 11채택/4기각, 오판율 ~10%)
- **Phase 0-F**: SOT 수정 18건 적용 완료 + 검증 18/18 PASS

### 적용 완료된 SOT 수정 18건 (Delta 요약)
| # | 파일 | 행 | 수정 내용 |
|---|------|-----|----------|
| 1 | CLAUDE.md | L92 | `(81개)` → `(81개: I25+E16+S8+A7+B6+C7+D6+EVX6)` |
| 2 | D2.0-03 BLUE_NODES | L766 | `Confidence < 70%` → `< 50% (MASTER_SPEC 정본)` |
| 3 | STEP7-K | L848 | `Confidence < 70%` → `< 50%` |
| 4 | STEP7 J-M | L881 | `Confidence<70%` → `<50%` |
| 5 | MASTER_SPEC | L1726 | NEVER_AUTO 6개 → 10개 (4개 누락 보완) |
| 6 | MASTER_SPEC | L1729 | `7개 불변구역` → `7개 불변구역 + 3개 운영금지(총 10개)` |
| 7 | PART2 | L3199 | `MEDIUM(9개) → LOW(3개)` → `MEDIUM(8개) → LOW(4개)` |
| 8 | PART2 | L3290 | 동일 수정 |
| 9 | MASTER_SPEC | L729 | `10계층 아키텍처` → `10계층 보안 아키텍처 (4-Layer와 별개)` |
| 10 | MASTER_SPEC | L1008 | `4-Layer Guardrails` → `4-Layer LLM Guardrails (10계층과 별개)` |
| 11 | D2.0-06 | L177 | top_k=10에 `API 레이어 B1은 top_k=5 기본` 주석 추가 |
| 12 | B2 | L334 | `Intent Parser` → `Intent Detector` |
| 13 | B2 | L353 | `Gate Evaluator` → `Condition & Decision Engine` |
| 14 | D2.0-01 | L1011 | `Intent Parser` → `Intent Detector` (Mermaid) |
| 15 | B5 | L127 | `Intent Parser` → `Intent Detector` |
| 16 | AGENT_TEAMS | L505 | `Intent Parser` → `Intent Detector` |
| 17 | PLAN-3.0 | L806 | `#FF4D4D` → `#EF4444` |
| 18 | PLAN-3.0 | L808 | `#FACC15` → `#FBBF24` |

### 적대적 검증으로 철회된 수정 3건
| FIX | INC | 사유 |
|-----|-----|------|
| FIX-002 | INC-002 | FP — Series/Priority/Layer는 직교 분류 체계 |
| FIX-003 | INC-003 | FP — QoD 0.7 출력보류는 양쪽 일치, 0.4는 별개 기능 |
| FIX-005 | INC-005 | 문서가 이미 갭 인정, 인덱스 수 변경은 추적성 상실 |

### 보류 2건 (이번 대화에서 처리)
| FIX | INC | 보류 사유 |
|-----|-----|----------|
| FIX-008 | INC-008 | MASTER_SPEC에서 CORE 모듈 26개 범위 명시 — 정확한 삽입 위치 미확정 |
| FIX-010 | INC-010 | MASTER_SPEC에서 COND 모듈 4→5개 — 정확한 삽입 위치 미확정 |

---

## ═══ TASK 1: PART2 스팟체크 (M-1 ~ M-6) ═══

> **목적**: Phase 0에서 수정한 18건의 SOT 변경이 PART2 구현가이드에 잘못된 값으로 잔류하는지 확인
> **대상 파일**: D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md (6,139줄)
> **방법**: 병렬 에이전트 4개로 동시 실행

### M-1: HITL 임계값 잔류 확인

```
대상: PART2에서 "70%" grep
목적: Confidence < 70% (구 HITL 임계값)가 PART2에 잔류하는지 확인
판정 기준:
  - HITL/Confidence 관련 맥락에서 "70%"가 있으면 → FAIL (수정 필요)
  - 비용 관련(Cost 70% 경고 등) "70%"는 → PASS (다른 의미)
작업:
  1. PART2에서 "70%" grep (output_mode: content, -C 3)
  2. 각 매치의 맥락 확인 → HITL/Confidence 관련인지 판별
  3. 관련 있으면 해당 행 + 수정안 제시
```

### M-2: NEVER_AUTO 카운트 확인

```
대상: PART2에서 "NEVER_AUTO" grep
목적: NEVER_AUTO가 10개로 올바르게 기술되어 있는지 확인
판정 기준:
  - "NEVER_AUTO" 관련 행에서 카운트가 6 또는 7이면 → FAIL
  - 10으로 올바르면 → PASS
작업:
  1. PART2에서 "NEVER_AUTO" grep (output_mode: content, -C 3)
  2. 각 매치에서 항목 수/목록 확인
  3. 불일치 있으면 해당 행 + 수정안 제시
```

### M-3: 모듈명 잔류 확인

```
대상: PART2에서 "Intent Parser" + "Gate Evaluator" grep
목적: 구 모듈명이 PART2에 잔류하는지 확인
판정 기준:
  - "Intent Parser" 또는 "Gate Evaluator" 발견 시 → FAIL
  - 미발견 시 → PASS
작업:
  1. PART2에서 "Intent Parser" grep
  2. PART2에서 "Gate Evaluator" grep
  3. 발견 시 해당 행 + 수정안 제시
참고: 이전 대화에서 PART2에 해당 용어 없음을 확인했으나 재확인 필요
```

### M-4: STEP-1 스캐폴드 모듈명 확인

```
대상: PART2 §2 V0-STEP-1 섹션
목적: 스캐폴드 생성 시 참조하는 모듈명/구조가 수정된 SOT와 일치하는지 확인
판정 기준:
  - I-1이 "Intent Detector"로 기술 → PASS
  - I-5가 "Condition & Decision Engine"으로 기술 → PASS
  - 구 명칭 사용 시 → FAIL
작업:
  1. PART2에서 "V0" 또는 "STEP-1" 또는 "스캐폴드" grep하여 섹션 위치 찾기
  2. 해당 섹션 읽기 (300~500줄 예상)
  3. I-1, I-5 모듈 참조 확인
  4. B2 PROJECT_STRUCTURE (D:\VAMOS\docs\sot\PHASE_B2_PROJECT_STRUCTURE.md) 참조와 대조
```

### M-5: UI 색상코드 잔류 확인

```
대상: PART2에서 "#FF4D4D" + "#FACC15" grep
목적: 구 색상코드가 PART2에 잔류하는지 확인
판정 기준:
  - 구 색상코드 발견 시 → FAIL
  - 미발견 시 → PASS
작업:
  1. PART2에서 "#FF4D4D" grep
  2. PART2에서 "#FACC15" grep
  3. 발견 시 해당 행 + 수정안 제시
참고: 이전 대화에서 PART2에 해당 색상 없음을 확인했으나 재확인 필요
```

### M-6: COND 우선순위 카운트 정합성 확인

```
대상: PART2 전체에서 COND MEDIUM/LOW 카운트 관련 행
목적: L3199/L3290 외에 MEDIUM(9개) 또는 LOW(3개)가 잔류하는지 확인
판정 기준:
  - L3199/L3290 이외 위치에서 "MEDIUM(9" 또는 "LOW(3" 발견 시 → FAIL
  - 모든 위치에서 MEDIUM=8, LOW=4 → PASS
작업:
  1. PART2에서 "MEDIUM" grep (COND 우선순위 맥락)
  2. PART2에서 "LOW(3" grep
  3. 각 매치의 맥락 확인 → v10 COND 배치 관련인지 판별
  4. 불일치 있으면 해당 행 + 수정안 제시
```

### 스팟체크 실행 방법

```
Agent 활용 전략:
  - Agent 1 (Explore): M-1 + M-2 (PART2 grep 2건 — 병렬)
  - Agent 2 (Explore): M-3 + M-5 (PART2 grep 4건 — 병렬, 이미 PASS 예상)
  - Agent 3 (Explore): M-4 (PART2 §2 STEP-1 섹션 읽기)
  - Agent 4 (Explore): M-6 (PART2 COND 카운트 전수 확인)
  → 4개 병렬 에이전트로 동시 실행 권장
```

---

## ═══ TASK 2: 보류 수정 2건 처리 (FIX-008, FIX-010) ═══

### FIX-008: MASTER_SPEC CORE 모듈 범위 명시

```
배경:
  - INC-008: CORE 모듈 수 불일치
    MASTER_SPEC: "I(17)+E(6)+S(1)+A(2)=26" (CORE status 모듈)
    AGENT_TEAMS: "P0 (Critical) -- 16개"
    서로 다른 범위를 '핵심 모듈'로 칭함
  - FIX-008 목표: MASTER_SPEC에 범위 명시 추가

작업:
  1. MASTER_SPEC에서 "CORE" grep하여 관련 위치 전수 파악
  2. 모듈 테이블 (I-Series, E-Series, S-Series, A-Series) 읽기
  3. CORE status 모듈을 직접 카운트하여 26개 확인
  4. 범위 명시 텍스트 삽입 위치 결정
  5. 수정안 제시 → 사용자 승인 후 적용

대상 파일: D:\VAMOS\docs\sot\VAMOS_MASTER_SPECIFICATION.md
참조: CLAUDE.md L92~210 (모듈 시스템 섹션)
```

### FIX-010: MASTER_SPEC COND 모듈 수 정정

```
배경:
  - INC-010: COND 모듈 수 불일치
    MASTER_SPEC: 4개 (I+E+S+A 중 COND status)
    CLAUDE.md: 5개 (I-7, I-12, I-22, I-23, I-25)
  - FIX-010 목표: MASTER_SPEC COND 모듈 수를 5개로 정정

작업:
  1. MASTER_SPEC 모듈 테이블에서 "COND" grep
  2. COND status 모듈 목록 직접 확인 (I-7, I-12 등이 있는지)
  3. CLAUDE.md의 COND 목록과 대조
  4. 정확한 수정 위치 결정
  5. 수정안 제시 → 사용자 승인 후 적용

대상 파일: D:\VAMOS\docs\sot\VAMOS_MASTER_SPECIFICATION.md
참조: D:\VAMOS\docs\sot\CLAUDE.md L94~120 (I-Series 모듈 목록)
```

### 보류 수정 실행 방법

```
Agent 활용 전략:
  - Agent 5 (Explore): FIX-008 위치 탐색 (MASTER_SPEC CORE grep + 테이블 분석)
  - Agent 6 (Explore): FIX-010 위치 탐색 (MASTER_SPEC COND grep + CLAUDE.md 대조)
  → 2개 병렬 에이전트로 동시 실행 권장
  → 탐색 결과 확인 후 Edit으로 수정 (사용자 승인 후)
```

---

## ═══ TASK 3: 구현 진입 최종 게이트 판정 ═══

### TASK 1~2 완료 후 최종 판정 기준

| # | 조건 | 판정 방법 |
|---|------|----------|
| G-1 | M-1~M-6 전수 PASS | 6건 스팟체크 결과 |
| G-2 | FIX-008, FIX-010 처리 완료 | 수정 적용 + 검증 |
| G-3 | PART2에서 수정 필요한 추가 행 없음 | TASK 1 결과 |
| G-4 | CRITICAL 잔여 0건 유지 | adversarial_review 확인 |
| G-5 | v13_sot_delta.json 최종 갱신 | FIX-008/010 반영 |

### 판정 산출물

TASK 1~2 완료 후 아래 파일 갱신:
1. `v13_sot_delta.json` — FIX-008/010 + M-1~6 추가 수정 반영
2. `v13_phase0_verdict.md` — 최종 판정 갱신
3. `v13_sot_corrections_applied.md` — 추가 수정 기록

### 최종 체크리스트 (사용자 확인용)

```
═══════════════════════════════════════════════════
 구현 진입 최종 게이트 체크리스트
═══════════════════════════════════════════════════

■ 스팟체크 결과
  [G-1] M-1 HITL 70% 잔류 없음: ✅/❌
  [G-2] M-2 NEVER_AUTO 10개 정확: ✅/❌
  [G-3] M-3 Intent Parser/Gate Evaluator 잔류 없음: ✅/❌
  [G-4] M-4 STEP-1 스캐폴드 모듈명 정확: ✅/❌
  [G-5] M-5 구 색상코드 잔류 없음: ✅/❌
  [G-6] M-6 COND MEDIUM/LOW 카운트 정합: ✅/❌

■ 보류 수정 처리
  [G-7] FIX-008 CORE 범위 명시 완료: ✅/❌
  [G-8] FIX-010 COND 모듈 수 정정 완료: ✅/❌

■ 최종 상태
  [G-9] CRITICAL 잔여 0건: ✅/❌
  [G-10] v13_sot_delta.json 최종 갱신: ✅/❌
  [G-11] v13_phase0_verdict.md 최종 갱신: ✅/❌

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
G-1~G-11 전수 ✅ 이면 → PART2 구현단계 착수 가능
하나라도 ❌ 이면 → 해당 항목 재작업 후 재확인
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## AI 오류 방지 규칙

1. **grep 결과 전수 인용**: 매치된 행 번호 + 텍스트 반드시 제시
2. **맥락 판별**: "70%" grep 시 Cost 70%와 HITL 70%를 반드시 구분
3. **수정 전 승인**: 추가 수정 발견 시 목록 제시 후 사용자 승인 대기
4. **Delta 갱신**: 추가 수정 시 v13_sot_delta.json에 DELTA-019+ 추가
5. **백업 필수**: 추가 수정 대상 파일은 fixes/ 디렉토리에 백업

---

## 참조 파일 목록 (이 대화에서 읽어야 하는 파일)

### 필수 읽기 (Pre-check)
| # | 파일 | 경로 |
|---|------|------|
| 1 | v13 계획서 | `D:\VAMOS\04. 구현단계\v13_plan.md` |
| 2 | Phase 0 판정서 | `D:\VAMOS\04. 구현단계\v13_results\phase0\v13_phase0_verdict.md` |
| 3 | Delta 목록 | `D:\VAMOS\04. 구현단계\v13_results\phase0\v13_sot_delta.json` |
| 4 | 적대적 검증 | `D:\VAMOS\04. 구현단계\v13_results\phase0\v13_adversarial_review.json` |
| 5 | 수정 기록 | `D:\VAMOS\04. 구현단계\v13_results\phase0\fixes\v13_sot_corrections_applied.md` |

### 스팟체크 대상
| # | 파일 | 경로 |
|---|------|------|
| 6 | PART2 구현가이드 | `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` |

### 보류 수정 대상
| # | 파일 | 경로 |
|---|------|------|
| 7 | MASTER_SPEC | `D:\VAMOS\docs\sot\VAMOS_MASTER_SPECIFICATION.md` |
| 8 | CLAUDE.md | `D:\VAMOS\docs\sot\CLAUDE.md` |
