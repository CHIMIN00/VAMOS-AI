# VAMOS v13 Pipeline — SOT 내부 정합성 검증 + v6~v12 전수 재검증 계획서

> **버전**: v13.2.0-PLAN (ABD 17건 + 2계층 검증 시스템 반영)
> **작성일**: 2026-03-16
> **목적**: SOT 68개 파일 내부 섹션 간 정합성 검증 + v6~v12 전체 검증 프로세스 전수 재실행
> **근거**: SOT 내부 불일치 3건 발견 → 오염된 SOT 기준으로 수행된 v6~v12 검증 결과 신뢰성 재확인 필요
> **원칙**: 하나도 빠짐없이 v6~v12의 모든 Phase, Step, Script, Agent, Check Item을 재실행

---

# 목차

1. [v13 포지션 및 필요성](#1-v13-포지션-및-필요성)
2. [SOT 내부 불일치 현황](#2-sot-내부-불일치-현황)
3. [AI 오류/환각 최소화 전략 + 약점 분석](#3-ai-오류환각-최소화-전략--약점-분석)
4. [v6~v12 전수 재검증 범위 매트릭스](#4-v6v12-전수-재검증-범위-매트릭스)
5. [Phase 0: SOT 내부 전수 정합성 검증 (신규)](#5-phase-0-sot-내부-전수-정합성-검증)
6. [Phase 1: v6 전수 재실행](#6-phase-1-v6-전수-재실행)
7. [Phase 2: v7 전수 재실행](#7-phase-2-v7-전수-재실행)
8. [Phase 3: v8 전수 재실행](#8-phase-3-v8-전수-재실행)
9. [Phase 4: v9 전수 재실행](#9-phase-4-v9-전수-재실행)
10. [Phase 5: v10 전수 재실행](#10-phase-5-v10-전수-재실행)
11. [Phase 6: v11 전수 재실행](#11-phase-6-v11-전수-재실행)
12. [Phase 7: v12 전수 재실행](#12-phase-7-v12-전수-재실행)
13. [Phase 8: 최종 종합 판정](#13-phase-8-최종-종합-판정)
14. [실행 가이드 및 세션 계획](#14-실행-가이드-및-세션-계획)
15. [완료 판정 (CHECKPOINT)](#15-완료-판정-checkpoint)

---

# 1. v13 포지션 및 필요성

```
v6  (완료)  구조 무결성          PART1+PART2+RPT ↔ 마크다운 규칙
v7  (완료)  SOT 교차 검증        PART1+PART2 ↔ SRC 41개 (189항목)
v8  (완료)  4-Dim 통합 검증      PART2 ↔ SRC 43개 (~791항목, 4차원)
v9  (완료)  구현 준비 완전성      PART2 ↔ SRC + 외부 의존성 (~663 checks)
v10 (완료)  Feature Coverage      SRC 43개→68개 기능 → PART2 매핑 (3,943 features)
v11 (완료)  내부 자기 정합성      PART2 ↔ PART2 자기 자신 (26 GAPs, 14 agents)
v12 (완료)  최종 완전성 검증      SOT 68개(89,363줄) → PART2 최종본 (12 success criteria)
───────────────────────────────────────────────────────────────────
v13 (본 계획)  SOT 정합성 + 전수 재검증 (2-Pass 전략)
  ├── Phase 0: SOT 68개 파일 내부 섹션 간 전수 정합성 검증 + 수정 (신규)
  ├── Pass 1: Phase 1~7 (v6~v12 전체 프로세스 재실행, 발견만 — 수정 없음)
  ├── Pass 2: 전체 발견사항 통합 수정 + 전 Phase 재검증
  └── Phase 8: 최종 종합 판정 + 초보자가이드 재검토
```

### 왜 v13이 필요한가?

1. **SOT 내부 불일치 발견**: v6~v12는 모두 SOT를 "절대 진실"로 간주했으나, SOT 자체에 3건의 내부 불일치 확인
2. **오염 전파 경로**: 불일치한 SOT 기준 → v6~v12 검증 결과에 오차/오류 전파 가능성
3. **v6~v12 공통 맹점**: 어떤 버전도 "SOT 파일 A의 §X ↔ SOT 파일 B의 §Y" 간 정합성을 검증하지 않음
4. **초보자가이드 품질 보장**: 33개 세션 산출물이 SOT 오류에 오염되었을 가능성 → 근본적 재검증 필수

---

# 2. SOT 내부 불일치 현황

> v6~v12에서 발견되지 않고 초보자가이드 검토 중 식별된 3건

## 불일치 A: 7개 불변구역 vs NEVER_AUTO 10개

| SOT 위치 | 내용 | 값 |
|----------|------|-----|
| CLAUDE.md §7.3 | 7개 불변 구역 | safety_rules, cost_ceiling, approval_flow, non_goals, audit_format, data_retention, user_consent |
| CLAUDE.md §17 SDAR | NEVER_AUTO | 위 7개 + escalate_own_privilege, guardrails, gate = **10개** |
| SDAR_DESIGN_SPEC | NEVER_AUTO 목록 | 10개 (동일) |

**분석**: 다른 범위(정책 수준 7 vs 시행 수준 10). 동일 문서 내 혼재 → 독자 혼동 가능. **범위 구분 명시 필요**.

## 불일치 B: COND 우선순위 카운트

| SOT 위치 | MEDIUM | LOW |
|----------|--------|-----|
| PART2 요약 테이블 | 9 | 3 |
| PART2 상세 목록 | **8** | **4** |

**분석**: 단순 카운팅 오류. PART2 상세 목록이 정본 → 요약 테이블 수정 필요.

## 불일치 C: 모듈 분류 체계

| SOT 위치 | 분류 | 합계 |
|----------|------|------|
| PART2 | 3-tier (CORE 32 + COND 10 + EXP 39) | 81 |
| CLAUDE.md | 4-tier (CORE 32 + COND 7 + EXP 32 + RE-ADD 10) | 81 |

**분석**: 분류 기준이 다름 (활성화 시점 vs 원본 출처). 두 분류 모두 유효하나 독자에게 혼동 → **분류 기준 명시 필요**.

---

# 3. AI 오류/환각 최소화 전략 + 약점 분석

## 3.0 2계층 검증 아키텍처 (v13.2.0 신규)

> **v6~v12의 근본 문제**: 전 과정이 100% AI 판단 — 프로그래밍적 팩트체크가 0%.
> 같은 AI가 추출하고 검증하면 동일 환각을 반복한다 (W1).
> **해결**: Layer A(결정론적 프로그램 검증)와 Layer B(AI 의미적 검증)를 분리.

```
┌───────────────────────────────────────────────────────────────┐
│ Layer A: 결정론적 검증 (Python 스크립트 — AI 판단 0%)          │
│ → DV-1: JSON 스키마 무결성 (필수 필드 존재)                    │
│ → DV-2: 메타데이터 카운트 정합성 (합계 = items 수)             │
│ → DV-3: source_line 범위 확인 (0 < line ≤ 파일 줄 수)         │
│ → DV-4: source_text 원본 매칭 (SOT 파일에서 직접 grep)        │
│ → DV-5: item_id 연속성                                       │
│ → DV-6: value_type vs value 실제 타입 일치                    │
│ → DV-7: COUNT key ↔ LIST key 길이 교차 검증                  │
│                                                               │
│ 판정: CRITICAL ≥ 1 → FAIL (저장 차단)                         │
│ 도구: D:\VAMOS\.claude\hooks\deterministic_validator.py       │
└──────────────────────────┬────────────────────────────────────┘
                           │ PASS 시에만
┌──────────────────────────▼────────────────────────────────────┐
│ Layer B: AI 의미적 검증 (스킬 에이전트)                        │
│ → SV-1: 의미적 정확성 (key/context가 맥락에 맞는지)            │
│ → SV-2: 추출 완전성 (SOT에 있는데 JSON에 없는 항목)           │
│ → SV-3: 표준 키 적절성                                       │
│ → AD-1: 환각 탐지 (무작위 20% 샘플링 SOT 대조)               │
│ → AD-2: 값 변조 탐지 (source_text 내 숫자 vs value)          │
│ → AD-3: 약점 패턴 분석 (W1~W5)                               │
│                                                               │
│ 도구: /validate, /audit, /sot-check, /quality-gate 스킬      │
└───────────────────────────────────────────────────────────────┘
```

### EA-1 테스트 결과 (실증)

```
결정론적 검증기(DV)가 EA-1 산출물(200항목)에서 즉시 발견:
  CRITICAL 14건 — source_text가 SOT 파일 전체에서 미발견 (환각 확정)
  WARNING 20건 — value_type "string"인데 실제 value가 dict
  INFO 1건    — source_line ±10줄 오차

v6~v12에서 못 잡은 이유: Claude가 "맞는지" Claude에게 물어봄 → 같은 환각 반복
v13 Layer A: Python이 파일에서 직접 grep → 거짓말 불가 → 환각 14건 확정
```

### 스킬 에이전트 + Hook 시스템

```
D:\VAMOS\.claude\
├── hooks\
│   ├── deterministic_validator.py    ← Layer A: AI 판단 0%, DV-1~DV-7
│   └── block_invalid_ea.sh           ← PreToolUse Hook: CRITICAL시 저장 차단
├── skills\
│   ├── validate\SKILL.md             ← /validate: Layer A+B 통합 검증
│   ├── audit\SKILL.md                ← /audit: 적대적 감사 (Devil's Advocate)
│   ├── sot-check\SKILL.md            ← /sot-check: SOT 원본 직접 대조
│   └── quality-gate\SKILL.md         ← /quality-gate: 전체 파이프라인
├── settings.json                      ← Hook 자동 실행 설정
└── CLAUDE.md                          ← 프로젝트 설정
```

### 자동 실행 흐름 (Hooks)

```
EA 추출 완료 → Write tool 호출
  → [PreToolUse Hook] block_invalid_ea.sh
    → deterministic_validator.py 실행
    → DV CRITICAL 있으면? → 저장 차단 (exit 2)
    → DV PASS? → 저장 허용
  → [PostToolUse Hook] 검증 결과 요약 출력 + /quality-gate 실행 권장
  → /quality-gate 실행
    → Step 1: Layer A (DV-1~DV-7)    ← 프로그램
    → Step 2: Layer B (SV-1~SV-3)    ← AI 의미 검증
    → Step 3: /audit (AD-1~AD-3)     ← AI 적대적 감사
    → Step 4: /sot-check             ← AI SOT 대조 (의심 항목만)
    → 판정: GOLD/SILVER/BRONZE/REJECT
  → GOLD/SILVER → 다음 Phase 진행 가능
  → REJECT → 수정 후 재추출
```

### 품질 게이트 판정 기준

| 판정 | 조건 |
|------|------|
| **GOLD** | Layer A PASS + Layer B PASS + Audit CLEAN + SOT 전체 MATCH |
| **SILVER** | Layer A PASS + Layer B PASS + Audit SUSPICIOUS + SHIFTED ≤ 5 |
| **BRONZE** | Layer A PASS + WARNING만 있음 |
| **REJECT** | Layer A FAIL 또는 Audit CONTAMINATED 또는 SOT NOT_FOUND ≥ 1 |

## 3.1 전략 9개 (S1~S7 + S8~S9 신규)

| # | 전략 | 설명 |
|---|------|------|
| S1 | **이중 검증** | 생성 에이전트 ≠ 검증 에이전트 (별도 프롬프트 맥락) |
| S2 | **정량 JSON 출력** | 모든 에이전트 산출물은 JSON 형태로 구조화 → 파싱 가능 |
| S3 | **SOT 값 프롬프트 주입** | 검증 대상 SOT 값을 프롬프트에 직접 포함 → 에이전트가 자체 기억 의존 방지 |
| S4 | **적대적 리뷰** | Devil's Advocate 에이전트가 모든 발견사항을 반박 시도 |
| S5 | **체크섬 검증** | 수치/카운트 항목은 산술적 체크섬으로 이중 확인 |
| S6 | **3단계 심각도** | CRITICAL/WARNING/INFO 분류 → CRITICAL만 필수 수정 (오탐 부담 감소) |
| S7 | **세션 간 산출물 체인** | 이전 세션 산출물을 다음 세션 입력으로 전달 → 맥락 단절 방지 |
| **S8** | **결정론적 검증 우선** | AI 판단 전에 프로그램(DV-1~DV-7)이 팩트체크. Layer A FAIL이면 Layer B 미진행 |
| **S9** | **Hook 기반 자동 차단** | PreToolUse Hook으로 CRITICAL 있는 JSON 저장 자동 차단. AI가 우회 불가 |

## 3.2 약점 분석 (5개) + 대응 변경

| # | 약점 | 원인 | 발생 확률 | v13.1 대응 | v13.2 대응 (신규) |
|---|------|------|-----------|-----------|------------------|
| W1 | **동일 모델 편향** | 같은 AI가 생성+검증 시 동일 환각 반복 | 중 | S4 + 원문 인용 강제 | **+S8: 프로그램이 먼저 팩트체크 → AI 환각을 프로그램이 잡음** |
| W2 | **JSON 조작** | 숫자를 맞추려고 AI가 값을 변조 | 저 | S3 + S5 교차 탐지 | **+DV-4/DV-7: 프로그램이 source_text↔value 직접 비교** |
| W3 | **컨텍스트 한계** | 68개 파일 89,363줄 → 단일 프롬프트 불가 | 고 | 파일별 분할 | **+DV-3: 프로그램이 줄 수 범위 자동 확인** |
| W4 | **의미적 오류 누락** | 숫자만 체크하면 축약/근사/혼동 놓침 | 중 | S1 + 정성 검증 | **+SV-1: AI 의미 검증은 Layer A 통과 후에만 → 팩트 확보 상태에서 의미 판단** |
| W5 | **적대적 과잉 오탐** | 엄격할수록 false positive 폭증 | 중 | S6 + CRITICAL 임계값 | **+GOLD/SILVER/BRONZE 4단계: 세분화된 판정으로 과잉 차단 방지** |

## 3.3 약점 대응 보강 규칙

```
R1: 모든 수치 비교 시 에이전트는 반드시 SOT 원문 라인번호를 인용한다
R2: JSON 출력에 source_file + source_line 필수 포함
R3: 파일 89,363줄은 68개 파일 × 파일별 개별 처리 → 크로스 참조만 별도
R4: 적대적 에이전트는 CRITICAL 판정 시 반드시 2개 이상의 SOT 근거를 제시
R5: 동일 항목이 3개 이상 SOT에서 서로 다른 값이면 SOURCE_CONFLICT로 에스컬레이션
R6: 세션 종료 시 미완료 항목 목록을 JSON으로 저장 → 다음 세션에서 자동 로드
R7: (신규) EA JSON 저장 전 반드시 DV-1~DV-7 통과 필수. Hook이 자동 차단.
R8: (신규) /quality-gate GOLD 또는 SILVER 판정 없이 다음 Phase 진행 금지.
```

---

# 4. v6~v12 전수 재검증 범위 매트릭스

> 아래는 v6~v12의 **모든** Phase, Script, Agent, Check Item을 빠짐없이 나열한 것이다.
> v13에서 이 모든 항목을 재실행한다.

## 4.1 v6 전수 목록

| Phase | 구성요소 | 항목 수 | v13 재실행 |
|-------|----------|---------|-----------|
| Phase 0 | 0-A~0-H 스크립트 8개 | 8 scripts | ✅ |
| Phase 1 STEP A | Agent 1~5 순방향 (PART → 원본) | 5 agents | ✅ |
| Phase 1 STEP B | Agent 1~5 역방향 (원본 → PART 누락) | 5 agents | ✅ |
| Phase 1.5 | 적대적 재검증 (층화 spot-check) | 1 adversarial | ✅ |
| Phase 2 | Ripple Map + 수정 + Phase 0 재실행 | fix + rerun | ✅ |
| CHECKPOINT | 7개 완료 조건 | 7 conditions | ✅ |
| **소계** | | **~19 실행 단위** | |

### v6 에이전트 범위 (정본: v6 §4~§5)

| Agent | 순방향 범위 | 역방향 범위 |
|-------|------------|------------|
| Agent 1 | §6.1~§6.4 ORANGE CORE | SRC → PART 누락 |
| Agent 2 | §6.5~§6.8 BLUE/Storage | SRC → PART 누락 |
| Agent 3 | §6.9~§6.10 Safety/Cost | SRC → PART 누락 |
| Agent 4 | §6.11~§6.13 UI/CI/Version + PART1 교차 | SRC → PART 누락 |
| Agent 5 | §3~§5 V1/V2/V3 Phase 구현 항목 | SRC → PART 누락 |

### v6 오류 패턴 카탈로그 (11개)

```
P1: 수치 불일치       P2: 필드/속성 누락     P3: 버전 범위 오류
P4: LOCK 값 위반      P5: 이름/명칭 변형     P6: 순서/계층 오류
P7: 중복 정의         P8: 참조 깨짐          P9: 범위 초과/축소
P10: 암묵적 가정      P11: 원본 간 충돌(SOURCE_CONFLICT)
```

## 4.2 v7 전수 목록

| Phase | 구성요소 | 항목 수 | v13 재실행 |
|-------|----------|---------|-----------|
| Phase 0 | 0-A~0-H 스크립트 8개 (v6 동일) | 8 scripts | ✅ |
| Phase 1 | Agent 1~10 주제별 검증 (순방향+역방향) | 10 agents × 2 | ✅ |
| Phase 1.5 | Agent 11 적대적 + 계층별 spot-check 50건+ | 1 adversarial | ✅ |
| Phase 2 | Ripple Map + 수정 + Phase 0 재실행 | fix + rerun | ✅ |
| CHECKPOINT | §7 완료 판정 (v7 기준) | conditions | ✅ |
| **소계** | | **~29 실행 단위** | |

### v7 에이전트 범위 (정본: v7 §4)

| Agent | 검증 범위 | Tier | 항목 수 |
|-------|----------|------|---------|
| Agent 1 | I-Series (I-1~I-25) 모듈 | T01~T03 | 25 |
| Agent 2 | E/S/A/B/C/D/EVX-Series 모듈 | T04~T06 | 56 |
| Agent 3 | 5-Gate + 9-State Machine | T07 | 14 |
| Agent 4 | API 계약 (88 endpoints) | T08 | 20 |
| Agent 5 | Storage/Memory/RAG | T09 | 18 |
| Agent 6 | Safety/Cost/RBAC | T10~T11 | 22 |
| Agent 7 | UI/UX | T12 | 12 |
| Agent 8 | Config (B4) | T13 | 8 |
| Agent 9 | Tech Stack/Version | T14~T15 | 6 |
| Agent 10 | V0~V3 GO/NO-GO + 이슈 | T16~T18 | 8 |
| **합계** | | **18 Tiers** | **189** |

## 4.3 v8 전수 목록

| Phase | 구성요소 | 항목 수 | v13 재실행 |
|-------|----------|---------|-----------|
| Phase 0 | 0-A~0-H + IMP-A~IMP-F = 14 스크립트 | 14 scripts | ✅ |
| Phase 1 | Agent 1~12 주제별 검증 (4-Dimension) | 12 agents | ✅ |
| Phase 1.5 | Agent 13 적대적 재검증 | 1 adversarial | ✅ |
| Phase 2 | Ripple Map + 수정 + Phase 0 재실행 | fix + rerun | ✅ |
| CHECKPOINT | 8개 완료 조건 | 8 conditions | ✅ |
| **소계** | | **~35 실행 단위** | |

### v8 검증 4-Dimension

| Dim | 명칭 | Phase 0 | Phase 1 |
|-----|------|---------|---------|
| A | 문서 구조 무결성 | 0-A~0-H (8개) | - |
| B | 내용 정합성 (SOT 교차) | - | Agent 1~10 (191항목) |
| C | 구현 실현가능성 | IMP-A~IMP-F (6개) | Agent 1~10 (200항목) |
| D | AI 프롬프트 완전성 | - | Agent 11 (프롬프트) + Agent 12 (D2.0-02) |

### v8 Phase 0 스크립트 14개

```
구조 (v6 계승):  0-A(테이블) 0-B(산술) 0-C(Heading) 0-D(LOCK) 0-E(숫자불일치) 0-F(ID유일성) 0-G(HTML주석) 0-H(헤더카운트)
구현 (v8 신규):  IMP-A(파일경로) IMP-B(의존성순서) IMP-C(단위/포맷) IMP-D(타임아웃/임계값) IMP-E(에러코드) IMP-F(테스트커버리지)
```

### v8 에이전트 12+1

| Agent | 검증 범위 | Dim |
|-------|----------|-----|
| Agent 1 | §2 V0 STEP 1~6 | B+C |
| Agent 2 | §3 V1 Phase 1~6 | B+C |
| Agent 3 | §4 V2 Phase 1~3 | B+C |
| Agent 4 | §5 V3 Phase 1~3 | B+C |
| Agent 5 | §6.1~§6.4 ORANGE CORE 상세 | B+C |
| Agent 6 | §6.5~§6.6 Storage/Memory 상세 | B+C |
| Agent 7 | §6.7~§6.8 Safety/Cost 상세 | B+C |
| Agent 8 | §6.9~§6.10 Config/Workflow 상세 | B+C |
| Agent 9 | §6.11~§6.12 UI/CI 상세 | B+C |
| Agent 10 | §6.13+§7 Version/GO-NOGO 상세 | B+C |
| Agent 11 | V0~V3 AI 프롬프트 전수 | D |
| Agent 12 | D2.0-01↔D2.0-02↔§7.x 트리플 매핑 | B |
| Agent 13 | 적대적 재검증 (전 Agent 발견사항) | All |

### v8 오류 패턴 카탈로그

```
v6 계승: P1~P11 (11개)
구현 추가: I1~I12 (12개) — 경로불일치/의존성순환/단위혼재/타임아웃누락/에러코드미정의 등
프롬프트: PR1~PR5 (5개) — LOCK위반/모호명세/참조깨짐/버전불일치/산출물미정의
```

## 4.4 v9 전수 목록

| Phase | 구성요소 | 항목 수 | v13 재실행 |
|-------|----------|---------|-----------|
| Phase -1 | 기반 정비 (PART2 무결성 + SRC 동기화) | 준비 | ✅ |
| Phase 0-Pre | Ground Truth 5개 구축 | 5 GTs | ✅ |
| Phase 0 | 프롬프트 작성 (6개 관점) | 6 prompts | ✅ |
| Phase 0-Validate | 시범 실행 | pilot | ✅ |
| Phase 1 | 전수 실행 (3-Wave × 에이전트) | ~663 checks | ✅ |
| Phase 2 | 수정 + 재검증 | fix + rerun | ✅ |
| CHECKPOINT | 8개 완료 조건 | 8 conditions | ✅ |
| **소계** | | **~40+ 실행 단위** | |

### v9 6개 관점

| 관점 | 명칭 | 핵심 질문 |
|------|------|----------|
| A | 의존성 순서 | STEP N이 STEP N+2 산출물을 전제하지 않는가? |
| B | 파일 경로 정합성 | 모든 경로가 PHASE_B2와 일치하는가? |
| C | 구현 가능성 | AI 프롬프트가 구현 가능할 만큼 구체적인가? |
| D | 누적 산출물 추적 | Stage 간 산출물 체인이 완전한가? |
| E | 수량 일관성 | 동일 수치가 모든 위치에서 일치하는가? |
| F | 외부 의존성 실현성 | 명시된 패키지/서비스가 실제 존재하는가? |

### v9 Ground Truth 5개

```
GT-1: 파일 경로 레지스트리 (PHASE_B2 기반)
GT-2: 산출물 체인 레지스트리 (Stage 간 입출력)
GT-3: 수량 인덱스 (모든 수치 + 위치)
GT-4: 외부 의존성 레지스트리 (패키지/서비스/API)
GT-5: 구현 가능성 체크리스트 (SOT 도출)
```

### v9 방어 규칙 14개

```
RULE 1~14: 마크다운 테이블 자동 파싱, 근거 인용 필수, 수치 허용오차 0,
           GT 기반만 판정, 3-Wave 구조, 충돌 시 정본 우선순위 적용 등
```

## 4.5 v10 전수 목록

| Phase | 구성요소 | 항목 수 | v13 재실행 |
|-------|----------|---------|-----------|
| Phase 0-A | 기능 항목 단위 정의 + 추출 템플릿 | template | ✅ |
| Phase 0-B | CLAUDE.md 기능 인덱스 추출 (Layer 1) | extraction | ✅ |
| Phase 0-C | 68개 SRC 전수 기능 추출 (Layer 2) | 15 agents | ✅ |
| Phase 0-D | CLAUDE.md ↔ SRC 교차 검증 (Delta) | delta | ✅ |
| Phase 0-E | V8/V9 산출물 1:1 재검증 | revalidation | ✅ |
| Phase 0-F | 최종 Feature Registry 확정 (GT) | registry | ✅ |
| Phase 1 | Feature → PART2 매핑 검증 | 6 agents | ✅ |
| Phase 1.5 | 적대적 재검증 | 1 adversarial | ✅ |
| Phase 2 | 누락 항목 반영 + 재검증 | fix + rerun | ✅ |
| CHECKPOINT | 완료 판정 | conditions | ✅ |
| **소계** | | **~25+ 실행 단위** | |

### v10 에이전트 구성

```
Phase 0-C: 15개 추출 에이전트 (68개 SRC 파일 분할 담당)
Phase 1:   6개 매핑 에이전트 (PART2 §2~§7 섹션별)
Phase 1.5: 1개 적대적 에이전트
합계:      22개 에이전트
```

### v10 핵심 수치

- SRC 파일: 68개 (v8의 43개에서 확장 — STEP7 15개 + 보조 4개 + 우선순위 R1-R6 6개)
- 추출 Feature: 3,943개
- MISSING 처리: 1,068건
- 대화: 33개 세션

## 4.6 v11 전수 목록

| Phase | 구성요소 | 항목 수 | v13 재실행 |
|-------|----------|---------|-----------|
| Phase 0 | 0-A~0-G 내부 인덱스 구축 7개 | 7 indexes | ✅ |
| Phase 1 Wave 1 | Agent 1~3 결정론적 자기 대조 | GAP-05,06,07,08,10 | ✅ |
| Phase 1 Wave 2 | Agent 4~6 구조/매핑 교차 | GAP-01,02,03,04,09 | ✅ |
| Phase 1 Wave 3 | Agent 7~9 프롬프트 전수 | GAP-11,12,13,14 | ✅ |
| Phase 1 Wave 4 | Agent 10~13 심화 검증 | GAP-15~22,25 | ✅ |
| Phase 1 Wave 5 | Agent 14 사용성 종합 | GAP-23,24 | ✅ |
| Phase 1.5 | Agent 15 적대적 재검증 | all findings | ✅ |
| Phase 2 | BP-1~15 원본 보호 + 수정 + 재검증 | fix + rerun | ✅ |
| CHECKPOINT | 14개 완료 조건 | 14 conditions | ✅ |
| **소계** | | **~30+ 실행 단위** | |

### v11 26개 GAP

```
GAP-01~04: 구조/매핑 (섹션-항목 정합, 구현항목 추적, AI프롬프트↔항목, §6↔Phase)
GAP-05~08: 수치/참조 (내부 수치 일관성, 참조 무결성, 용어 일관성, LOCK값 자기모순)
GAP-09~10: 버전/변경 (V0~V3 일관성, GO/NO-GO 자기 충족성)
GAP-11~14: 프롬프트 (산출물 추적, 입출력 명세, LOCK 준수, 구현 가능성)
GAP-15~22: 심화 (기술 실현성, 비용 산술, 보안 커버리지, 테스트 커버리지, 의존성 순서, 에러 처리, 성능 명세, 로깅 완전성)
GAP-23~24: 사용성 (초보자 실행가능성, 문서 탐색성)
GAP-25: §6.13 버전 관리 (변경이력 정합성)
GAP-26: ABD (Framework 자체 사전 검증)
```

### v11 원본 보호 프로토콜 (BP-1~15)

```
BP-1:  Phase 2 시작 전 PART2 전체 백업
BP-2:  SHA256 해시 기록
BP-3:  백업 무결성 확인
BP-4:  수정 전 영향범위 분석
BP-5:  수정 단위별 독립 적용
BP-6:  수정 후 즉시 검증
BP-7:  ripple 영향 추적
BP-8:  역패치 가능 보장
BP-9:  세션 중단 시 복구 절차
BP-10: 중단 지점 기록
BP-11: 수정 이력 전수 기록
BP-12: 6단계 수정 순서 (스냅샷→기록→수정→검증→감지→기록)
BP-13: Ripple Map 이중 검증
BP-14: 완료조건 14개 필수 PASS
BP-15: 최종 해시 비교
```

## 4.7 v12 전수 목록

| Phase | 구성요소 | 항목 수 | v13 재실행 |
|-------|----------|---------|-----------|
| Phase 0 | Feature Registry 재구축 (68개 SOT) | 15 agents | ✅ |
| Phase 1 | SOT→PART2 매핑 검증 | 7 agents | ✅ |
| Phase 1.5 | 적대적 재검증 | 1 adversarial | ✅ |
| Phase 2 | v10 교차 대사 | comparison | ✅ |
| Phase 3 | v7 역방향 교차 확인 | reverse check | ✅ |
| Phase 4 | §6 참조 57건 전수 해소 | 57 refs | ✅ |
| Phase 5 | v11 미해결 패턴 5건 | 5 patterns | ✅ |
| Phase 6 | PART2 반영 + 재검증 | fix + rerun | ✅ |
| CHECKPOINT | 12개 성공 기준 | 12 criteria | ✅ |
| **소계** | | **~50+ 실행 단위** | |

### v12 에이전트 구성

```
Phase 0:   15개 추출 에이전트 (SOT 68개 파일 기능 추출)
Phase 1:   7개 매핑 에이전트 (PART2 섹션별)
Phase 1.5: 1개 적대적 에이전트
합계:      23개 에이전트, 11개 대화 세션
```

### v12 성공 기준 12개

```
1. Feature Registry 완성 (읽기 완료율 90%+)
2. SOT→PART2 매핑 100%
3. MISSING BLOCKER 0건
4. 적대적 재검증 오판율 ≤10%
5. v10 교차 대사 완료
6. v7 역방향 교차 확인 추가 누락 0건
7. §6 참조 57건 전수 해소
8. v11 미해결 패턴 5건 해소
9. PART2 반영 완료
10. 18개 AI 프롬프트 재검증 PASS
11. 수치/참조 정합성 PASS
12. 원본 보호 (SHA256)
```

---

# 5. Phase 0: SOT 내부 전수 정합성 검증 (신규)

> **v13 독자적 Phase — v6~v12에서 한 번도 수행하지 않은 검증**
> **목적**: SOT 68개 파일 간 + 파일 내 섹션 간 정합성 전수 검증

## 5.1 검증 유형 (C1~C8)

| # | 유형 | 설명 | 예시 |
|---|------|------|------|
| C1 | **동일 값 불일치** | 같은 항목이 2개+ SOT에서 다른 값 | Guardrails 3-Layer vs 4-Layer |
| C2 | **카운트 불일치** | 요약 카운트 ≠ 상세 목록 수 | COND MEDIUM 9 vs 상세 8 |
| C3 | **분류 체계 충돌** | 동일 대상의 분류가 문서마다 다름 | 3-tier vs 4-tier 모듈 분류 |
| C4 | **명칭 불일치** | 같은 모듈/항목의 이름이 다름 | "Decision Engine" vs "Condition & Decision Engine" |
| C5 | **범위 불일치** | 같은 개념의 범위가 다름 | 불변구역 7 vs NEVER_AUTO 10 |
| C6 | **버전 범위 불일치** | 활성화 버전이 다름 | L4 "V2+" vs "V2/V3" |
| C7 | **수식/임계값 불일치** | 같은 파라미터의 값이 다름 | 타임아웃 5분 vs 15분 |
| C8 | **참조 무결성** | 참조하는 ID/섹션이 존재하지 않음 | 없는 §번호 참조 |

## 5.2 실행 구조 (v13.2.0 — 2계층 검증 반영)

```
Phase 0-A: SOT 68개 파일 전수 읽기 + 핵심 값 추출 (15 에이전트, 파일별 분할)
  └→ [자동] Hook: EA JSON 저장 시 DV-1~DV-7 결정론적 검증 → CRITICAL시 저장 차단
  └→ [수동] /quality-gate: Layer A(DV) + Layer B(SV) + Audit(AD) + SOT Check
  └→ 판정: GOLD/SILVER → Phase 0-B 진행 가능 / REJECT → 수정 후 재추출

Phase 0-B: 추출 값 크로스 매칭 (8 에이전트, C1~C8 유형별)
  └→ [선행조건] Phase 0-A 15개 산출물 전수 /quality-gate SILVER 이상
  └→ [자동] Hook: CM JSON 저장 시 스키마 검증

Phase 0-C: 불일치 목록 확정 + 심각도 분류 (1 종합 에이전트)
Phase 0-D: SOT 수정안 도출 + 영향 범위 분석 (1 에이전트)
Phase 0-E: 적대적 재검증 (1 에이전트 — /audit 스킬 사용)
Phase 0-F: SOT 수정 반영 (사용자 승인 후)
```

### Phase 0-A: 15 추출 에이전트 배정

| Agent | 담당 SOT 파일 | 추출 대상 |
|-------|--------------|----------|
| EA-1 | CLAUDE.md | 전체 LOCK값, 모듈 목록, 분류, 수치 |
| EA-2 | BASE-1.3, PLAN-3.0 | 규칙, 비용, 버전별 로드맵 |
| EA-3 | MASTER_SPECIFICATION | 통합 참조값 전수 |
| EA-4 | D2.0-01, D2.0-02 | Overview LOCK + ORANGE CORE 상세 |
| EA-5 | D2.0-03, D2.0-04 | BLUE NODES + INFRA CORE |
| EA-6 | D2.0-05, D2.0-06 | AGENT WORKFLOW + STORAGE MEMORY |
| EA-7 | D2.0-07, D2.0-08 | SAFETY/COST + UI/UX |
| EA-8 | D2.1-A1~D2.1-Q1 (10개) | 스키마/TECH STACK 전수 |
| EA-9 | PHASE_B1~B3 | API계약 + 모노레포 + 프론트엔드 |
| EA-10 | PHASE_B4~B7 | Config + Workflow + Safety + Backend |
| EA-11 | AI_INVESTING_SPEC, CLOUD_LIBRARY_SPEC | 투자/클라우드 도메인 |
| EA-12 | AGENT_TEAMS_SPEC, SDAR_DESIGN_SPEC | 에이전트/SDAR 도메인 |
| EA-13 | STEP7 작업가이드 15개 | STEP7 상세 전수 |
| EA-14 | STEP7 보조 4개 + 우선순위 R1-R6 | STEP7 보조 자료 |
| EA-15 | READINESS 3개 + BEGINNER_GUIDE | 준비도/온보딩 |

### Phase 0-B: 8 크로스 매칭 에이전트

| Agent | 유형 | 매칭 대상 |
|-------|------|----------|
| CM-1 | C1(동일값) | 모든 수치/파라미터 값 크로스 비교 |
| CM-2 | C2(카운트) | 요약 테이블 vs 상세 목록 수 전수 비교 |
| CM-3 | C3(분류) | 모듈/기능/항목 분류 체계 비교 |
| CM-4 | C4(명칭) | 모든 모듈/시스템/기능 명칭 일관성 |
| CM-5 | C5(범위) | 동일 개념의 범위/스코프 비교 |
| CM-6 | C6(버전범위) | V0/V1/V2/V3 활성화 정보 비교 |
| CM-7 | C7(수식/임계값) | 타임아웃/임계값/비용 수치 비교 |
| CM-8 | C8(참조무결성) | 모든 내부 참조(§번호, ID, 파일명) 존재 확인 |

## 5.3 기대 산출물

```
D:\VAMOS\04. 구현단계\v13_results\phase0\
├── sot_extraction_{EA-1~15}.json     — 68개 파일 값 추출 결과
├── cross_match_{CM-1~8}.json         — 크로스 매칭 결과
├── sot_inconsistency_list.json       — 불일치 확정 목록 (심각도 포함)
├── sot_fix_proposals.json            — 수정안 + 영향 범위
├── adversarial_review.json           — 적대적 재검증 결과
└── sot_corrections_applied.md        — 실제 수정 기록
```

## 5.4 완료 조건

```
PC-1: SOT 68개 파일 전수 읽기 완료 (100%)
PC-2: C1~C8 유형별 크로스 매칭 전수 완료
PC-3: 기존 3건 불일치 해소 확인
PC-4: 신규 불일치 CRITICAL 0건 잔여
PC-5: 적대적 재검증 오판율 ≤10%
PC-6: 사용자 승인 완료
```

---

# 6. Phase 1: v6 전수 재실행

> **대상**: PART1 + PART2 + RPT (3개 파일)
> **SRC**: SOT (Phase 0에서 정합성 확인 완료된 버전)
> **변경**: SOT 수정 반영분이 있으면 Phase 0 수정본 기준으로 재실행

## 6.1 Phase 0 (Scripts 8개)

Phase 0 스크립트의 SOT 기준 값이 Phase 0에서 수정되었을 수 있으므로:
- 0-D: LOCK/FREEZE 추출 시 수정된 SOT 반영
- 0-E: 동일 키워드 수치 비교 시 수정된 SOT 기준 적용
- 나머지 0-A, 0-B, 0-C, 0-F, 0-G, 0-H: 구조 검증이므로 SOT 수정 영향 없음

## 6.2 Phase 1 (5 에이전트 × 순방향+역방향)

- v6 원본 프롬프트의 Agent 1~5 범위 그대로 재실행
- **추가**: SOT Phase 0에서 수정된 값이 있으면 해당 값 기준으로 대조
- **추가**: R1~R6 규칙 적용 (원문 라인번호 인용 필수)

## 6.3 Phase 1.5 (적대적)

- v6 원본 적대적 프로토콜 그대로 재실행
- 층화 spot-check 포함

## 6.4 Phase 2 (수정 + 재실행)

- Ripple Map 생성 → 수정 반영 → Phase 0 재실행 → PASS 확인

---

# 7. Phase 2: v7 전수 재실행

> **대상**: PART1 + PART2 + RPT
> **SRC**: SOT 41개 + CLAUDE.md (Phase 0 수정본)

## 7.1~7.4: v7 Phase 0~2 + CHECKPOINT 전수 재실행

- Phase 0: 8 스크립트 (v6 동일)
- Phase 1: 10 에이전트 × 순방향+역방향, 189 항목 전수
- Phase 1.5: Agent 11 적대적 + 50건+ spot-check
- Phase 2: Ripple Map + 수정 + Phase 0 재실행
- CHECKPOINT: v7 §7 기준 완료 판정

---

# 8. Phase 3: v8 전수 재실행

> **대상**: PART2 단일 전수
> **SRC**: SOT 43개 + CLAUDE.md (Phase 0 수정본)

## 8.1~8.4: v8 Phase 0~2 + CHECKPOINT 전수 재실행

- Phase 0: 14 스크립트 (0-A~0-H + IMP-A~IMP-F)
- Phase 1: 12 에이전트 (4-Dimension: 구조+내용+구현+프롬프트), ~791 항목
- Phase 1.5: Agent 13 적대적
- Phase 2: Ripple Map + 수정 + Phase 0 재실행
- CHECKPOINT: 8개 완료 조건

---

# 9. Phase 4: v9 전수 재실행

> **대상**: PART2
> **SRC**: SOT + 외부 의존성 (Phase 0 수정본)

## 9.1~9.5: v9 Phase -1~2 + CHECKPOINT 전수 재실행

- Phase -1: 기반 정비 (PART2 무결성 + SRC 동기화)
- Phase 0-Pre: Ground Truth 5개 재구축
- Phase 0: 6개 관점 프롬프트 (재작성 또는 기존 활용)
- Phase 0-Validate: 시범 실행
- Phase 1: 3-Wave 전수 실행, ~663 checks
- Phase 2: 수정 + 재검증
- CHECKPOINT: 8개 완료 조건 + RULE 1~14 준수

---

# 10. Phase 5: v10 전수 재실행

> **대상**: PART2
> **SRC**: SOT 68개 파일 (Phase 0 수정본)

## 10.1~10.4: v10 Phase 0-A~2 + CHECKPOINT 전수 재실행

- Phase 0-A: 기능 항목 단위 정의
- Phase 0-B: CLAUDE.md 기능 인덱스 추출
- Phase 0-C: 68개 SRC 전수 기능 추출 (15 에이전트)
- Phase 0-D: CLAUDE.md ↔ SRC 교차 검증
- Phase 0-E: 이전 v13 Phase 1~4 산출물 재검증 (v8/v9 대신)
- Phase 0-F: 최종 Feature Registry 확정
- Phase 1: Feature → PART2 매핑 (6 에이전트)
- Phase 1.5: 적대적 재검증
- Phase 2: 누락 반영 + 재검증
- CHECKPOINT: v10 완료 조건

---

# 11. Phase 6: v11 전수 재실행

> **대상**: PART2 (내부 자기 정합성)
> **SRC**: 없음 (PART2 단독)

## 11.1~11.4: v11 Phase 0~2 + CHECKPOINT 전수 재실행

- Phase 0: 0-A~0-G 내부 인덱스 7개 재구축
- Phase 1: 5 Wave × 14 에이전트, 25개 GAP 전수 검증
  - Wave 1: Agent 1~3 (GAP-05,06,07,08,10)
  - Wave 2: Agent 4~6 (GAP-01,02,03,04,09)
  - Wave 3: Agent 7~9 (GAP-11,12,13,14)
  - Wave 4: Agent 10~13 (GAP-15~22,25)
  - Wave 5: Agent 14 (GAP-23,24)
- Phase 1.5: Agent 15 적대적 재검증
- Phase 2: BP-1~15 원본 보호 프로토콜 적용 + 수정 + 재검증
- CHECKPOINT: 14개 완료 조건

---

# 12. Phase 7: v12 전수 재실행

> **대상**: PART2
> **SRC**: SOT 68개 (Phase 0 수정본, 89,363줄+)

## 12.1~12.7: v12 전 Phase 전수 재실행

- Phase 0: Feature Registry 재구축 (15 에이전트, 68개 SOT)
- Phase 1: SOT→PART2 매핑 (7 에이전트)
- Phase 1.5: 적대적 재검증
- Phase 2: v10 교차 대사 (v13 Phase 5 산출물 기준)
- Phase 3: v7 역방향 교차 확인 (v13 Phase 2 산출물 기준)
- Phase 4: §6 참조 전수 해소
- Phase 5: v11 미해결 패턴 해소 (v13 Phase 6 산출물 기준)
- Phase 6: PART2 반영 + 재검증
- CHECKPOINT: 12개 성공 기준

---

# 13. Phase 8: 최종 종합 판정

> v13 전체의 최종 게이트

## 13.1 종합 판정 기준

| # | 조건 | 판정 |
|---|------|------|
| F1 | Phase 0 SOT 불일치 CRITICAL 0건 잔여 | PASS/FAIL |
| F2 | Phase 1 (v6) CHECKPOINT 전수 PASS | PASS/FAIL |
| F3 | Phase 2 (v7) CHECKPOINT 전수 PASS | PASS/FAIL |
| F4 | Phase 3 (v8) CHECKPOINT 전수 PASS | PASS/FAIL |
| F5 | Phase 4 (v9) CHECKPOINT 전수 PASS | PASS/FAIL |
| F6 | Phase 5 (v10) CHECKPOINT 전수 PASS | PASS/FAIL |
| F7 | Phase 6 (v11) CHECKPOINT 전수 PASS | PASS/FAIL |
| F8 | Phase 7 (v12) CHECKPOINT 전수 PASS | PASS/FAIL |
| F9 | v13 신규 발견 사항 0건 잔여 (CRITICAL 기준) | PASS/FAIL |
| F10 | 초보자가이드 33개 세션 SOT 정합성 확인 | PASS/FAIL |

**최종 판정**: F1~F10 전수 PASS → v13 COMPLETE → V0-STEP-1 착수 가능

## 13.2 초보자가이드 33개 세션 재검토

Phase 0~7에서 SOT 수정이 발생한 경우:
- 33개 세션 파일에서 수정된 SOT 값과 관련된 내용 전수 grep
- 영향 받는 세션 식별 → 해당 부분 수정
- 이전 v13 실행 전 수정한 59건 (Round 1: 50건 + Round 2: 9건) 재확인

---

# 14. 실행 가이드 및 세션 계획

## 14.1 예상 세션 수

| Phase | 예상 세션 | 에이전트 수 | 주요 작업 |
|-------|----------|------------|----------|
| Phase 0 (SOT) | 5~7 | 26 (15+8+1+1+1) | SOT 내부 정합성 + 수정 |
| Pass 1: Phase 1~7 | 15~20 | ~170 (v6~v12 전체) | 발견만, 수정 없음 |
| Pass 2: 통합 수정 | 5~8 | 재검증 에이전트 | 1회 수정 + 전 Phase 재검증 |
| Phase 8 (종합) | 2~3 | 10+ | 종합 판정 + 세션 재검토 |
| **총계** | **27~38** | **~170+ 에이전트** | **ABD-3 반영 (2-Pass)** |

## 14.2 세션별 실행 원칙

```
원칙 1: 매 세션 시작 시 이전 세션의 phase_summary.json만 로드 (5KB 이내) [ABD-14]
원칙 2: 매 에이전트 산출물은 JSON 형태로 디스크 저장, 컨텍스트에는 summary만 (S2) [ABD-14]
원칙 3: SOT 참조 시 반드시 Phase 0 수정본 사용 + Delta 목록 참조 (S3) [ABD-4]
원칙 4: 매 Phase 종료 시 사용자 승인 후 다음 Phase 진행
원칙 5: Pass 1에서는 수정하지 않음 — 발견만 수집 [ABD-3]
원칙 6: 적대적 에이전트는 별도 프롬프트 맥락에서 실행 + Phase별 초점 변경 (W1) [ABD-10]
원칙 7: 세션 중단 시 미완료 항목 목록 JSON 저장 (R6)
원칙 8: 전 Phase SRC 68개 통일 기준 [ABD-1]
원칙 9: PART2는 현재 최신 버전 단일 대상 [ABD-2]
원칙 10: Phase 0 스크립트(14개)는 1회 실행, 이후 Phase에서 결과 재활용 [ABD-7]
```

### 14.4 Phase 순서 의존성 (ABD-16 반영)

```
Phase 0 (SOT) → 필수 선행 (SOT 수정은 여기서만)
  ↓
Pass 1:
  Phase 1 (v6) → Phase 2 (v7) → Phase 3 (v8)   ← SRC 범위 확장 순서
  → Phase 4 (v9) → Phase 5 (v10)                 ← 구현준비→Feature Coverage 순서
  → Phase 6 (v11) → Phase 7 (v12)                ← 내부정합→최종완전성 순서
  ※ Phase 간 병렬 불가 (이전 Phase 산출물 참조)
  ↓
Pass 2:
  통합 발견사항 정리 → Ripple Map → 1회 수정 → 전 Phase CHECKPOINT 재검증
  ↓
Phase 8: 최종 종합 판정 + 초보자가이드 33개 세션 재검토 [ABD-17]
```

## 14.3 산출물 디렉토리 구조

```
D:\VAMOS\04. 구현단계\v13_results\
├── phase0\                — SOT 내부 정합성 검증
│   ├── extraction\        — 68개 파일 값 추출 (EA-1~15)
│   │   ├── validation\    — DV 결정론적 검증 결과
│   │   ├── audit\         — 적대적 감사 결과
│   │   └── sot_check\     — SOT 원본 대조 결과
│   ├── cross_match\       — 크로스 매칭 (CM-1~8)
│   └── fixes\             — SOT 수정 기록
├── phase1_v6\       — v6 재실행 결과
├── phase2_v7\       — v7 재실행 결과
├── phase3_v8\       — v8 재실행 결과
├── phase4_v9\       — v9 재실행 결과
├── phase5_v10\      — v10 재실행 결과
├── phase6_v11\      — v11 재실행 결과
├── phase7_v12\      — v12 재실행 결과
├── phase8_final\    — 최종 종합 판정
└── session_guide_recheck\ — 33개 세션 재검토
```

---

# 15. 완료 판정 (CHECKPOINT)

## 15.1 v13 전체 완료 조건

| # | 조건 | 필수 |
|---|------|------|
| 1 | Phase 0: SOT 68개 파일 내부 정합성 CRITICAL 0건 | ✅ |
| 2 | Phase 1: v6 7개 완료 조건 전수 PASS | ✅ |
| 3 | Phase 2: v7 완료 판정 전수 PASS | ✅ |
| 4 | Phase 3: v8 8개 완료 조건 전수 PASS | ✅ |
| 5 | Phase 4: v9 8개 완료 조건 전수 PASS | ✅ |
| 6 | Phase 5: v10 완료 조건 전수 PASS | ✅ |
| 7 | Phase 6: v11 14개 완료 조건 전수 PASS | ✅ |
| 8 | Phase 7: v12 12개 성공 기준 전수 PASS | ✅ |
| 9 | Phase 8: F1~F10 종합 판정 전수 PASS | ✅ |
| 10 | AI 오류 최소화: R1~R6 규칙 전 Phase 적용 확인 | ✅ |
| 11 | 초보자가이드 33개 세션 SOT 정합성 재확인 | ✅ |
| 12 | 전 에이전트 산출물 JSON 보존 | ✅ |

## 15.2 최종 판정

```
v13 전수 PASS → VAMOS 초보자가이드 최종본 확정 → Session 35 자동 조립 → V0-STEP-1 착수
v13 FAIL 항목 존재 → 해당 Phase 재실행 → PASS까지 반복
```

---

# 부록: v6~v12 전수 체크 항목 총계

| 버전 | Phase 0 스크립트 | Phase 1 에이전트 | 적대적 | 체크 항목 | 완료 조건 |
|------|----------------|----------------|--------|----------|----------|
| v6 | 8 | 5×2=10 | 1 | ~100+ | 7 |
| v7 | 8 | 10×2=20 | 1 | 189 | ~10 |
| v8 | 14 | 12 | 1 | ~791 | 8 |
| v9 | GT 5+6관점 | Wave 3 | 1 | ~663 | 8 |
| v10 | 추출 15 | 매핑 6 | 1 | 3,943 | ~8 |
| v11 | 인덱스 7 | 14 (5Wave) | 1 | 685~970 | 14 |
| v12 | 추출 15 | 매핑 7 | 1 | ~4,000+ | 12 |
| **v13 합계** | **~70+** | **~70+** | **8** | **~10,000+** | **~67+** |

> v13 = SOT 내부 정합성(Phase 0, 신규) + v6~v12 전 Phase 전수 재실행
> 에이전트 총 ~170+개, 체크 항목 ~10,000+개, 완료 조건 67+개
> **하나도 빠짐없이 재실행**

---

# 부록 B: v13 자체 약점 분석 (ABD — Adversarial Before Deployment)

> v13 계획서 자체의 약점, 오류 가능성, 실패 위험을 전수 식별하고 대응 방안을 확정한다.

## B.1 식별된 약점 17건 + 대응 방안

### BLOCKER (2건)

| # | 약점 | 대응 방안 |
|---|------|----------|
| **ABD-1** | **SRC 카운트 불일치**: v6=SRC 41개, v7=41개, v8=43개, v10/v12=68개. 각 Phase에서 SRC 몇 개 기준으로 재실행? | **결정**: Phase 0에서 SOT 68개 전수 정합성 확인 후, Phase 1~7 모두 **SOT 68개 기준**으로 통일. v6/v7의 원래 41개 범위는 68개로 확장 적용 (25개 누락 방지). v8의 43개도 68개로 확장. |
| **ABD-2** | **PART2 버전 미명시**: v8=v18, v9=v20.4, v11=v24, v12=v25.2 → v13은? | **결정**: v13은 **현재 최신 PART2 버전**(v12 완료 후 최종본)을 단일 대상으로 사용. 이전 버전별 재실행이 아니라, 최신 PART2에 대해 v6~v12 검증 로직을 재적용. |

### HIGH (5건)

| # | 약점 | 대응 방안 |
|---|------|----------|
| **ABD-3** | **Phase 간 수정 충돌**: Phase 1(v6)→2(v7)→3(v8)... 매번 PART2 수정 → 연쇄 충돌 | **결정**: 2-Pass 전략 채택. **Pass 1**(Phase 1~7): 수정하지 않고 발견만 수집. **Pass 2**: 전체 발견사항 통합 → Ripple Map → 1회 통합 수정 → 전 Phase 재검증. 이렇게 하면 Phase 간 수정 충돌 원천 차단. |
| **ABD-4** | **Phase 0 SOT 수정과 v6~v12 기대값 괴리**: SOT 수정 후 기준이 바뀌면 이전 v6~v12 프롬프트의 기대값과 불일치 | **결정**: Phase 0 SOT 수정 내역을 **Delta 목록**으로 관리. Phase 1~7 재실행 시 Delta에 해당하는 항목은 "수정된 SOT 기준" 적용을 명시. 프롬프트에 Delta 주입. |
| **ABD-5** | **RPT 파일 기준**: v6/v7은 RPT(검증_결과_리포트) 포함인데, RPT는 v6~v12 실행마다 변경됨 | **결정**: v13에서 RPT는 **v12 완료 후 최종 RPT**를 기준으로 사용. v6/v7의 Phase 0 스크립트가 RPT를 파싱할 때 최신 RPT 사용. |
| **ABD-6** | **38~53 세션 비현실적**: 산출물 체인 단절 위험 | **대응**: (1) 각 Phase 완료 시 **phase_summary.json** 생성 (다음 Phase 입력용, 핵심 데이터만 포함). (2) 세션 시작 시 summary만 로드 (전체 JSON 아님). (3) Phase 단위로 독립 실행 가능하도록 설계 — 이전 Phase summary만 있으면 됨. (4) 예상 세션 수 현실 조정: **Pass 1(발견)은 Phase 병합으로 20~25세션**, **Pass 2(수정+재검증)은 5~8세션**. |
| **ABD-11** | **GT 재구축 시점**: v9 GT-1~5를 Phase 4에서 재구축하지만, 이전 Phase에서 PART2 수정 가능 | **결정**: ABD-3의 2-Pass 전략으로 해소. Pass 1에서는 수정 없음 → GT 기반 변동 없음. Pass 2에서 통합 수정 후 GT 재구축. |
| **ABD-13** | **실패 시 재실행 범위**: Phase 3에서 FAIL 시 Phase 1~2도 재실행해야 하나? | **결정**: 2-Pass 전략에서 Pass 1은 발견만이므로 FAIL 없음. Pass 2에서 통합 수정 후 **전 Phase 재검증**(Pass 2의 핵심). 재검증에서 FAIL이면 해당 항목만 추가 수정 → 해당 Phase + 영향 Phase만 재실행. |

### MEDIUM (8건)

| # | 약점 | 대응 방안 |
|---|------|----------|
| **ABD-7** | **v6/v7 Phase 0 중복**: 동일 8 스크립트 2회 실행 | **결정**: Phase 0 스크립트는 **Phase 1(v6) 때 1회만 실행**, Phase 2(v7)에서는 결과 재활용. v7에서 추가 키워드가 있으면 그것만 추가 실행. |
| **ABD-8** | **v7이 v8의 부분집합**: v8 Agent 1~10이 v7 Agent 1~10 범위 포함 | **결정**: v7 189항목과 v8 191항목의 차이(2항목)를 사전 식별. v8 재실행 시 v7 결과를 참조하여 **중복 항목은 비교만, 차이 항목만 신규 검증**. 단, v7의 역방향 검증(SRC→PART)은 v8에 없으므로 v7 역방향은 독립 실행 유지. |
| **ABD-9** | **v10/v12 Feature Registry 중복** | **결정**: v12 Phase 0(Feature Registry)는 v10 Phase 0-C의 확장. v12 재실행 시 v10 산출물을 기반으로 **Delta만 검증** (v10 이후 추가된 25개 파일의 Feature). 단, v10 결과 자체의 정확성은 v10 Phase에서 별도 확인. |
| **ABD-10** | **적대적 에이전트 8회 동일 편향** | **대응**: (1) 적대적 프롬프트를 Phase마다 다르게 구성 (초점 변경). (2) Pass 1 종료 후 **1회 종합 적대적 리뷰** 추가 (전 Phase 발견사항 통합 검토). (3) R4 규칙(2개 이상 SOT 근거) 적용으로 편향 완화. |
| **ABD-14** | **산출물 JSON 수백 MB, 컨텍스트 초과** | **대응**: (1) phase_summary.json은 5KB 이내로 제한. (2) 상세 JSON은 디스크 보관만 (컨텍스트에 로드하지 않음). (3) 다음 세션에서 필요 시 특정 파일만 선택 로드. |
| **ABD-15** | **v6 에이전트 범위 정확성** | **대응**: Phase 1(v6) 실행 전 v6 원본 프롬프트를 다시 읽어 에이전트 범위 최종 확인. 현재 기재 내용은 이전 분석 기반이므로 실행 시점에 재확인. |
| **ABD-16** | **Phase 순서 의존성 미명시** | **결정**: Phase 순서 의존성 명시 추가. Phase 0→필수 선행. Phase 1~3(v6/v7/v8)→순차 (SRC 범위 확장). Phase 4(v9)→Phase 3 이후. Phase 5(v10)→Phase 4 이후. Phase 6(v11)→Phase 5 이후 (PART2 최신 상태 필요). Phase 7(v12)→Phase 6 이후. Pass 내 병렬 불가 (각 Phase가 이전 Phase 산출물 참조). |
| **ABD-17** | **초보자가이드 재검토 시점** | **결정**: Pass 2 통합 수정 완료 후 Phase 8에서 재검토. Phase 1~7은 Pass 1(발견만)이므로 수정 없음. Pass 2 통합 수정이 끝난 시점이 최적 재검토 시점. |

### LOW (2건)

| # | 약점 | 대응 방안 |
|---|------|----------|
| **ABD-12** | **v11 GAP-26 순환** | v11 GAP-26(ABD)은 v11 Framework 자체 검증. v13에서 재실행 시 v11 Framework에 대한 ABD 그대로 수행 (v13 자체 ABD와는 별개 대상). 순환 아님. |

## B.2 ABD 결과 반영 — 핵심 구조 변경 3건

### 변경 1: 2-Pass 전략 도입 (ABD-3, ABD-11, ABD-13 해소)

```
기존:  Phase 0 → Phase 1(v6, 발견+수정) → Phase 2(v7, 발견+수정) → ... → Phase 7(v12, 발견+수정) → Phase 8

변경:  Phase 0(SOT 정합성, 수정 포함)
       → Pass 1: Phase 1~7 (발견만, 수정 없음) — 전체 발견사항 수집
       → Pass 2: 통합 수정 (Ripple Map → 1회 수정 → 전 Phase 재검증)
       → Phase 8: 최종 판정 + 초보자가이드 재검토
```

**이유**:
- Phase마다 수정하면 다음 Phase의 기반이 변하여 연쇄 오류 발생
- 전체 발견사항을 모은 뒤 1회 통합 수정이 안전하고 효율적
- Pass 2 재검증 시 전 Phase CHECKPOINT를 한 번에 확인 가능

### 변경 2: SRC 통일 (ABD-1 해소)

```
기존:  v6=41개, v7=41개, v8=43개, v10/v12=68개 (각각 다른 SRC 범위)

변경:  전 Phase 통일 SOT 68개 기준
       - v6/v7 재실행 시에도 68개 SOT 사용 (원래 41개 범위 + 27개 확장)
       - 확장분은 "v6 원본에 없던 추가 검증"으로 표시
```

### 변경 3: Phase 0 스크립트 1회 실행 (ABD-7 해소)

```
기존:  Phase 1(v6)에서 8 scripts + Phase 2(v7)에서 8 scripts = 16회

변경:  Phase 1(v6)에서 14 scripts (v8 기준, 8+6 통합) 1회 실행
       - Phase 2(v7), Phase 3(v8)에서는 결과 재활용
       - 추가 키워드가 필요한 경우만 증분 실행
```

## B.3 수정 후 세션 예상치

| 구분 | 예상 세션 | 비고 |
|------|----------|------|
| Phase 0 (SOT 정합성) | 5~7 | SOT 수정 포함 |
| Pass 1 Phase 1~7 (발견만) | 15~20 | 수정 없이 발견만 → 더 빠름 |
| Pass 2 (통합 수정 + 재검증) | 5~8 | 1회 수정 + 전 Phase 재검증 |
| Phase 8 (종합 판정) | 2~3 | 초보자가이드 재검토 포함 |
| **총계** | **27~38** | 기존 38~53에서 감소 |

## B.4 잔여 위험 (수용 가능)

| # | 잔여 위험 | 수용 근거 |
|---|----------|----------|
| RR-1 | 동일 AI 모델 편향 | 적대적 프롬프트 다변화 + R1~R6 규칙 + 원문 인용 강제로 완화. 완전 제거는 불가 (다른 AI 모델 사용 시에만 가능). |
| RR-2 | 68개 SOT 파일 컨텍스트 한계 | 파일별 분할 + summary 체인으로 완화. 크로스 참조 시 일부 맥락 손실 가능성은 수용. |
| RR-3 | 27~38세션 간 산출물 체인 단절 | phase_summary.json(5KB 이내) + 디스크 보관으로 완화. 완전한 연속성은 불가능하나 핵심 데이터는 보존. |

---

*v13.2.0-PLAN — 2026-03-16 작성 (ABD 17건 + 2계층 검증 시스템 반영)*
