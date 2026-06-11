# v12 Additions Detail 구조화 종합 계획서

> **버전**: v1.0
> **작성일**: 2026-03-24
> **목적**: sot 2/5-3_v12-Additions-Detail/을 v12 추가사항 허브 정본(Single Source of Truth)으로 구조화하고, ~40건의 v12 추가 항목을 각 도메인 정본 폴더로 연결하는 인덱스 허브 체계를 확립하며, 도메인 횡단 충돌을 해결하는 종합 실행 계획
> **Status**: APPROVED — Phase 8 QC B+ (2026-03-26), Phase 10 QC A- (2026-03-27)
> **Tier**: 5 — Quality/Cross-cutting (횡단 허브)
> **SOT 출처**: Part2 §6.1, §6.7, §6.8, §6.10, V2-Phase 3, V3-Phase 2/3
> **Part2 상태**: PARTIAL (1줄 설명만 산재)
> **구현 Phase 상태**: 영구 제외 — `permanently_excluded_design_decision` (메타 허브; 정본 기록: SOT2_SESSION_EXECUTION_PROMPTS.md "제외 도메인 (5개)" + SOT2_MASTER_INDEX.md "범위 외(Phase 4 비대상) 11폴더" — 2026-06-11 폴더 내 명기)

---

## 목차

1. [현재 상태 분석](#1-현재-상태-분석)
2. [목표 구조 (최종 형태)](#2-목표-구조-최종-형태)
3. [권한 체계 선언](#3-권한-체계-선언)
4. [거버넌스 규칙](#4-거버넌스-규칙)
5. [선행작업](#5-선행작업)
6. [이슈 해결 매핑](#6-이슈-해결-매핑)
7. [Phase 실행 계획](#7-phase-실행-계획)
8. [파일 역할 분리 명세](#8-파일-역할-분리-명세)
9. [충돌 해결 프로토콜](#9-충돌-해결-프로토콜)
10. [검증 체크리스트](#10-검증-체크리스트)
11. [보완 사항](#11-보완-사항)
12. [FINAL REVIEW 결과](#12-final-review-결과)
13. [L3 전수 승급 계획 (간소화)](#13-l3-전수-승급-계획-간소화)
14. [실행 약점 대응 계획 (간소화)](#14-실행-약점-대응-계획-간소화)
- [부록 §A: 도메인별 정본 연결](#부록-a-도메인별-정본-연결)

---

## 1. 현재 상태 분석

### 1.1 기존 문서 현황

| 문서 | 위치 | 역할 | 줄수 | 상태 |
|------|------|------|------|------|
| **V12_ADDITIONS_상세명세.md** | docs/sot 2/5-3_.../ | v12 추가 기능 기술 명세 (7개 섹션, A~G) | 535 | 기술 명세 완비, 인덱스/도메인 매핑 부재 |
| **Part2 §6.1** | docs/guides/ | UI/UX v12 추가 컴포넌트 | ~4줄 | 1줄 설명 수준 (PARTIAL) |
| **Part2 §6.7** | docs/guides/ | Agent Teams v12 추가 | ~3줄 | 1줄 설명 수준 (PARTIAL) |
| **Part2 §6.8** | docs/guides/ | AI Investing v12 추가 | ~3줄 | 1줄 설명 수준 (PARTIAL) |
| **Part2 §6.10** | docs/guides/ | Cloud Library v12 추가 | ~5줄 | 1줄 설명 수준 (PARTIAL) |
| **Part2 V2-Phase 3** | docs/guides/ | V2 고급 확장 항목 | ~10줄 | 항목 이름만 나열 |
| **Part2 V3-Phase 2/3** | docs/guides/ | V3 미래 확장 항목 | ~10줄 | 항목 이름만 나열 |

### 1.2 sot 2/5-3_v12-Additions-Detail/ 현재 파일

| # | 파일/폴더명 | 상태 |
|---|------------|------|
| 1 | `V12_ADDITIONS_상세명세.md` | 기존 유지 (535줄, 7개 섹션 기술 명세) |
| 2 | `01_wellness-ui/` | 빈 서브폴더 (항목 파일 미생성) |
| 3 | `02_learning-tools/` | 빈 서브폴더 |
| 4 | `03_agent-teams/` | 빈 서브폴더 |
| 5 | `04_investing-additions/` | 빈 서브폴더 |
| 6 | `05_cloud-library/` | 빈 서브폴더 |
| 7 | `06_v2-v3-advanced/` | 빈 서브폴더 |

### 1.3 상세명세 7개 섹션 항목 전수 목록 (~40건)

| 섹션 | 범위 | 항목수 | 주요 내용 | 서브폴더 매핑 |
|------|------|--------|----------|-------------|
| **A: §6.1 UI/UX v12 추가** | A-1~A-4 | 4건 (10 컴포넌트) | 웰니스 UI 3종, CBT 도구 2종, 번아웃 예방 2종, 학습 도구 3종 | `01_wellness-ui/`, `02_learning-tools/` |
| **B: §6.7 Agent Teams v12 추가** | B-1~B-2 | 2건 (4 항목) | Prompt Registry API, TemplateSets 3종 | `03_agent-teams/` |
| **C: §6.8 AI Investing v12 추가** | C-1~C-2 | 2건 | Black-Litterman 모델, Factor Investing (6 팩터) | `04_investing-additions/` |
| **D: §6.10 Cloud Library v12 추가** | D-1~D-10 | 10건 | Evolution Control ~ Zettelkasten Extension | `05_cloud-library/` |
| **E: V2-Phase 3 HIGH/MEDIUM** | E-1~E-15 | ~15건 | Enhanced Context Window, Multi-turn Reasoning, Adaptive Prompt 등 | `06_v2-v3-advanced/` |
| **F: V3-Phase 2 MEDIUM** | F-1~F-6 | 6건 | Federated Learning, KG Auto-builder, Multi-agent Debate 등 | `06_v2-v3-advanced/` |
| **G: V3-Phase 3 LOW** | G-1~G-6 | 6건 | Neuromorphic Attention, Quantum-inspired, Self-evolving Agent 등 | `06_v2-v3-advanced/` |
| **합계** | | **~45건** | 7개 섹션 전체 | 6개 서브폴더 |

### 1.4 Part2 산재 상태 분석

Part2에서 v12 추가 관련 실질 내용 분포:

| Part2 섹션 | 실질 내용 | 비고 |
|-----------|----------|------|
| §6.1 | 컴포넌트 이름 4줄 | 스키마, 알고리즘 상세 없음 |
| §6.7 | Prompt Registry 1줄 + TS 3종 이름 | API 상세 없음 |
| §6.8 | Black-Litterman/Factor 이름만 | 수학 공식 없음 |
| §6.10 | 10개 서비스 이름 나열 | 기능 상세 없음 |
| V2-Phase 3 | ~15개 항목 이름 | 구현 상세 없음 |
| V3-Phase 2/3 | ~12개 항목 이름 | 구현 상세 없음 |

**결론**: Part2는 항목 이름만 산재하여 PARTIAL 상태. 실질 기술 명세는 상세명세(535줄)에 모두 집중되어 있음.

### 1.5 핵심 문제

1. **도메인 소유권 미확정**: ~45건의 v12 항목이 5개 이상 도메인에 걸쳐 있으나, 각 항목의 정본 소유 도메인이 명시적으로 선언되지 않음. 특히 횡단 기능(A-전략 도구, B-포트폴리오 최적화)이 다수 도메인에 중복 참조되어 단일 소유 도메인 확정이 지연됨.
2. **LOCK 상속 미정의**: 상세명세 내 LOCK-worthy 값(SM-2 파라미터, Black-Litterman τ 등)이 해당 도메인 LOCK과 어떻게 연결되는지 정의 부재. S8-4 검증 결과 8건의 LOCK이 확인되었으나, 상속 체인이 명시적으로 문서화되지 않아 갱신 시 불일치 위험이 있었음 (본 S10-3에서 해결).
3. **Part2 산재**: 6개 이상의 Part2 섹션(§6.1, §6.7, §6.8, §6.10, V2-Phase 3, V3-Phase 2/3)에 각 1줄씩만 흩어져 있어 전체상 파악 불가. 인덱스 허브 없이는 v12 전체 범위를 파악하려면 6개 섹션을 개별 탐색해야 하는 비효율 존재.
4. **인덱스 부재**: 서브폴더는 존재하나 `_index.md` 및 개별 항목 파일이 미생성. 도메인별 정본 연결(부록 §A)이 미완으로, 각 항목의 구현 상태 추적이 수동에 의존.
5. **V2/V3 항목 도메인 귀속 미정**: 섹션 E/F/G의 ~27건이 어느 도메인에 속하는지 미매핑. Phase 2 진입 시 확정 예정이나, 잠정 매핑(부록 §A)으로 추적 가능성은 확보됨.

### Part2 상태 및 방식 C 접근법
- **Part2 상태**: PARTIAL
- **방식 C 접근법**: 보완 작성

---

## 2. 목표 구조 (최종 형태)

### 2.1 폴더 트리

```
D:\VAMOS\docs\sot 2\5-3_v12-Additions-Detail\
│
├── V12_ADDITIONS_DETAIL_구조화_종합계획서.md  ← 본 문서
├── V12_ADDITIONS_상세명세.md                  ← 기존 파일 유지 (삭제 금지)
├── AUTHORITY_CHAIN.md                         ← 권한 체계 선언
├── CONFLICT_LOG.md                            ← 충돌 기록부
│
├── 01_wellness-ui\                            ← 웰니스 UI v12 추가
│   ├── _index.md                              ← 섹션 A-1~A-3 인덱스
│   ├── breathing_guide.md                     ← A-1 → #9 Health-Wellness 정본 참조
│   ├── grounding_exercise.md                  ← A-1 → #9 정본 참조
│   ├── meditation_timer.md                    ← A-1 → #9 정본 참조
│   ├── thought_record.md                      ← A-2 → #9 정본 참조
│   ├── cognitive_distortion_detector.md       ← A-2 → #9 정본 참조
│   ├── workload_monitor.md                    ← A-3 → #9 정본 참조
│   └── forced_break_overlay.md                ← A-3 → #9 정본 참조
│
├── 02_learning-tools\                         ← 학습 도구 v12 추가
│   ├── _index.md                              ← 섹션 A-4 인덱스
│   ├── flashcard_editor.md                    ← A-4 → #8 Education 정본 참조
│   ├── sm2_review_engine.md                   ← A-4 → #6 PKM + #8 Education 공유
│   └── review_dashboard.md                    ← A-4 → #8 Education 정본 참조
│
├── 03_agent-teams\                            ← Agent Teams v12 추가
│   ├── _index.md                              ← 섹션 B-1~B-2 인덱스
│   ├── prompt_registry_api.md                 ← B-1 → #17 MLOps 정본 참조
│   └── template_sets.md                       ← B-2 → #11 Conversation-A2A 정본 참조
│
├── 04_investing-additions\                    ← AI Investing v12 추가
│   ├── _index.md                              ← 섹션 C-1~C-2 인덱스
│   ├── black_litterman_model.md               ← C-1 → Ai-investing-detail 정본 참조
│   └── factor_investing.md                    ← C-2 → Ai-investing-detail 정본 참조
│
├── 05_cloud-library\                          ← Cloud Library v12 추가
│   ├── _index.md                              ← 섹션 D-1~D-10 인덱스
│   ├── evolution_control.md                   ← D-1 → #6 PKM 정본 참조
│   ├── korean_stopwords.md                    ← D-2 → #6 PKM 정본 참조
│   ├── code_snippets.md                       ← D-3 → #10 Dev-Tools 정본 참조
│   ├── idea_capture.md                        ← D-4 → #6 PKM 정본 참조
│   ├── swot_analysis.md                       ← D-5 → #12 Business 정본 참조
│   ├── writing_support.md                     ← D-6 → #6 PKM 정본 참조
│   ├── zettelkasten.md                        ← D-7 → #6 PKM 정본 참조
│   ├── knowledge_maturity.md                  ← D-8 → #6 PKM 정본 참조
│   ├── task_checkpoint.md                     ← D-9 → #7 Workflow 정본 참조
│   └── zettelkasten_extension.md              ← D-10 → #6 PKM 정본 참조
│
└── 06_v2-v3-advanced\                         ← V2/V3 고급 확장 v12 항목
    └── _index.md                              ← 섹션 E/F/G 인덱스 (E/F/G 27건은 §2.2 규칙에 따라 _index.md 내부 섹션으로 처리)
```

### 2.2 폴더 깊이 규칙

```
최대 3단계:
  sot 2/ → 5-3_v12-Additions-Detail/ → XX_{카테고리}/ → 파일.md  (3단계) OK
  4단계 이상 → 불필요 (V2/V3 항목도 _index.md 내부 섹션으로 처리)
```

### 2.3 네이밍 규칙

- **폴더명**: 영문 소문자 + 하이픈, 접두사 2자리 번호 (`01_`, `02_`, ...)
- **파일명**: 영문 소문자 + 언더스코어 (`.md` 확장자)
- **계획서 파일명**: `V12_ADDITIONS_DETAIL_구조화_종합계획서.md` (한글 허용)

### 2.4 허브 역할 정의

> **핵심 원칙**: 이 도메인은 **인덱스 허브**이다. 각 v12 항목의 구현 상세(L3)는 해당 도메인 정본 폴더에 존재하며, 여기에는 (1) 인덱스 매핑 (2) 도메인 횡단 추적 (3) 충돌 해결 기록만 유지한다.

| 역할 | 설명 | 이 폴더에서 하는 것 | 이 폴더에서 하지 않는 것 |
|------|------|-------------------|----------------------|
| **인덱스 허브** | ~45건 v12 항목의 소속 도메인 매핑 | 항목별 1-page 요약 + 정본 링크 | 구현 상세 (스키마, 알고리즘 등) |
| **횡단 추적** | 다중 도메인에 걸친 진행 상태 추적 | 월 1회 상태 갱신 | 독립적 Phase 실행 |
| **충돌 중재** | 도메인 간 소유권 분쟁 해결 | CONFLICT_LOG 기록 | 도메인 내부 기술 판정 |
| **상세명세 보존** | 535줄 기존 명세 유지 | 참조 링크 제공 | 명세 내용 중복 작성 |

---

## 3. 권한 체계 선언

### 3.1 기존 VAMOS 권한 체인

```
RULE 1.3 > PLAN 3.0 > DESIGN 2.0 LOCK > DESIGN body > Schema/TECH_STACK
```

### 3.2 v12 Additions Detail 확장 권한 체인

```
RULE 1.3
  > PLAN 3.0
    > DESIGN 2.0
      └─ Part2 (§6.1, §6.7, §6.8, §6.10, V2/V3 Phase)
        > 각 도메인 sot 2/ 정본 폴더                    ← 구현 상세 정본 (What + How)
          > sot 2/5-3_v12-Additions-Detail/상세명세    ← 통합 기술 명세 참조
            > sot 2/5-3_v12-Additions-Detail/인덱스     ← 인덱스 허브 (When + Where + Who)
```

> **핵심**: 각 v12 항목의 LOCK은 해당 항목이 속하는 도메인의 LOCK을 상속한다. 이 폴더는 LOCK을 신규 정의하지 않으며, 기존 LOCK을 참조·인용만 한다.

### 3.3 각 문서의 권한 범위

| 문서 | 권한 레벨 | 결정할 수 있는 것 | 결정할 수 없는 것 |
|------|----------|------------------|------------------|
| **Part2 §6.x / V2-V3** | IMPL-GUIDE | 항목 존재 선언, Phase 배정 | 구현 상세, 알고리즘, 스키마 |
| **각 도메인 sot 2/ 정본** | IMPL-DETAIL | What + How (스키마, 알고리즘, 파이프라인) | 항목 존재 자체, Phase |
| **상세명세 (535줄)** | 레거시 참조 | 기술 명세 통합 뷰 (유지, 삭제 금지) | 정본 역할 아님 (도메인 폴더가 정본) |
| **본 계획서 + 인덱스** | HUB-INDEX | 도메인 매핑, 횡단 추적, 충돌 중재 | 구현 상세, LOCK 값 정의 |

### 3.4 LOCK 보호 선언 — 상속 방식

> **절대 규칙**: sot 2/5-3_v12-Additions-Detail/ 내 파일은 **자체 LOCK을 LOCK-V12-01(귀속 원칙)·LOCK-V12-10(매핑 테이블) 2건에 한해서만 정의한다**(AUTHORITY_CHAIN 정합). 그 외 모든 LOCK-worthy 값은 해당 도메인 정본 폴더의 LOCK을 참조한다.

| # | LOCK 항목 | 상속 출처 (도메인 LOCK) | 값 | 비고 |
|---|-----------|----------------------|-----|------|
| LOCK-V12-01 | v12 항목 도메인 귀속 원칙 | R-19-1 (본 계획서) | "v12 항목은 해당 도메인 LOCK 상속" | 유일한 자체 규칙 |
| LOCK-V12-02 | SM-2 알고리즘 공식 | #6 PKM LOCK + #8 Education LOCK | ease_factor 업데이트, interval 계산 | 공유 LOCK |
| LOCK-V12-03 | Black-Litterman tau | Ai-investing-detail LOCK | tau = 0.025 | 상세명세 C-1 참조 |
| LOCK-V12-04 | Factor 6종 정의 | Ai-investing-detail LOCK | Value/Momentum/Quality/Size/Volatility/Dividend | 상세명세 C-2 참조 |
| LOCK-V12-05 | CBT 15가지 인지 왜곡 유형 | #9 Health-Wellness LOCK | 전부 아니면 전무, 과잉일반화, 파국화 등 15종 | 상세명세 A-2 참조 |
| LOCK-V12-06 | BreathingPattern 4-7-8 기본 패턴 | #9 Health-Wellness LOCK-HW-07 | 흡4초-지7초-호8초 | 상세명세 A-1 참조 |
| LOCK-V12-07 | TS_CORE/TS_WEB_RESEARCH/TS_CODE 3종 | D2.0-03 §4.2 LOCK + 2-1 LOCK-BN-18 | 3개 TemplateSet 구성 | 상세명세 B-2 참조. C-07 판정(2026-06-11): #11/#17은 참조만 |
| LOCK-V12-08 | PortfolioConstraints max 비중 | Ai-investing-detail LOCK | 단일 종목 max 10%, 단일 섹터 max 30% | 상세명세 C-2 참조 |
| LOCK-V12-09 | Zettelkasten 원자적 노트 원칙 | #6 PKM LOCK | Luhmann-style 원자적 노트, 5종 링크 타입 (related/supports/contradicts/continues/branches) | 상세명세 D-7 참조 |
| LOCK-V12-10 | 도메인 정본 연결 매핑 | 본 계획서 부록 §A | 부록 §A 전체 매핑 테이블 | 자체 정의 |

---

## 4. 거버넌스 규칙

> **글로벌 거버넌스 규칙**: 본 도메인은 0-0_Governance-Rules-Meta에서 정의한 R1~R11 글로벌 규칙을 전체 준수합니다.
> 아래는 글로벌 규칙에 추가되는 도메인 고유 규칙입니다.

### 공통 규칙

| # | 규칙 | 이유 | 위반 시 |
|---|------|------|---------|
| R1 | 폴더 깊이 최대 3단계 | Windows 260자 경로 제한 | 파일 생성 거부 |
| R2 | 마스터 INDEX.md 1개 + 폴더별 _index.md (파일 목록만) | 유지보수 부담 분산 | INDEX.md 미갱신 = 커밋 불가 |
| R3 | 파일명 변경 시 PART2 링크 테이블 동기화 | 참조 정합성 | 변경 커밋에 PART2 업데이트 포함 필수 |
| R4 | 상세명세 삭제 금지 | 기존 기술 명세 보존 | 삭제 시도 시 REJECT |
| R6 | 커밋 시 CONFLICT_LOG 확인 | 충돌 미해결 방지 | 경로/링크 영향이 있는 OPEN 충돌 존재 시 머지 차단. LOCK 값 불일치 건(C-04~C-08)은 경로 영향 없는 비차단 이월 충돌로 명시 분류(해당 도메인 조치 대기) |
| R8 | 분기별 전체 도메인 매핑 정합성 검사 | 링크 부패 방지 | 검사 미실시 = 다음 Phase 진입 차단 |

### Tier 5 횡단 규칙

| # | 규칙 | 이유 | 위반 시 |
|---|------|------|---------|
| R-T5-1 | 도메인 횡단 항목은 정본 소유자 명시 필수 | 소유권 분쟁 예방 | 소유자 미명시 항목 = OPEN 상태 유지, 실행 불가 |
| R-T5-2 | 추적 인덱스는 월 1회 갱신 | 상태 추적 적시성 | 미갱신 월 발생 시 다음 갱신 시 전수 점검 |

### 도메인 #19 고유 규칙

| # | 규칙 | 이유 | 위반 시 |
|---|------|------|---------|
| R-19-1 | v12 항목은 해당 도메인 sot 2/ 폴더에 원본 유지, 여기는 인덱스만 | 단일 정본 원칙 (SSoT) | 이 폴더에 구현 상세 작성 시 REJECT, 해당 도메인 폴더로 이동 |
| R-19-2 | 항목 추가 시 도메인 정본 폴더에도 동시 갱신 | 양방향 정합성 | 인덱스만 갱신하고 도메인 폴더 미갱신 시 커밋 차단 |
| R-19-3 | v12 항목 삭제 시 해당 도메인 폴더에서도 제거 확인 | 고아 항목 방지 | 삭제 커밋에 도메인 폴더 확인 증적 포함 필수 |
| R-19-4 | V2/V3 항목(섹션 E/F/G)은 도메인 귀속 확정 전까지 `06_v2-v3-advanced/`에 잠정 보관 | 미귀속 항목 관리 | 도메인 확정 시 즉시 이동 + 인덱스 갱신 |
| R-19-5 | 도메인 간 공유 항목(SM-2 등)은 주 소유 도메인 + 참조 도메인 명시 | 공유 LOCK 관리 | 주 소유 도메인 미지정 시 CONFLICT_LOG에 OPEN 등록 |

---

## 5. 선행작업

### 5.1 선행작업 목록

| # | 작업 | 설명 | 완료 기준 | 상태 |
|---|------|------|----------|------|
| PRE-01 | 도메인별 정본 폴더 존재 확인 | v12 항목이 연결될 대상 도메인 sot 2/ 폴더가 모두 존재하는지 확인 | 8개 대상 도메인 폴더 존재 확인 | DONE (2026-04-02) — 9/9 전수 존재 확인 |
| PRE-02 | 각 도메인 계획서 상태 확인 | 대상 도메인(#6, #7, #8, #9, #10, #11, #12, #17, AI-Investing)의 계획서가 작성 완료 상태인지 확인 | 최소 DRAFT 이상 | DONE (2026-04-02) — 9/9 구조화_종합계획서 존재 |
| PRE-03 | 상세명세 ~45건 전수 목록 확정 | 상세명세 535줄에서 개별 항목을 정확히 분리하여 전수 목록 작성 | 항목 ID + 이름 + 섹션 매핑 완료 | DONE (2026-04-02) — A~G 7개 섹션 45건 확인 |
| PRE-04 | V2/V3 항목 도메인 귀속 초안 작성 | 섹션 E/F/G ~27건의 잠정 도메인 귀속 매핑 | 각 항목에 후보 도메인 1~2개 지정 | DONE (2026-04-02) — 부록 §A.2에 27건 잠정 매핑 완료 |

### 5.2 대상 도메인 존재 확인 체크리스트

| 대상 도메인 | sot 2/ 폴더 | 계획서 존재 | v12 항목 수 |
|-----------|-----------|-----------|-----------|
| #6 PKM Knowledge Management | `3-3_PKM-Knowledge-Management/` | ✅ 존재 확인 | D-1,2,4,6,7,8,10 (7건) |
| #7 Workflow-RPA | `3-4_Workflow-RPA/` | ✅ 존재 확인 | D-9 (1건) |
| #8 Education-Learning | `3-5_Education-Learning/` | ✅ 존재 확인 | A-4 일부 (3건) |
| #9 Health-Wellness-EmotionAI | `3-6_Health-Wellness-EmotionAI/` | ✅ 존재 확인 | A-1,2,3 (7건) |
| #10 Developer-Tools | `3-7_Developer-Tools-API-SDK/` | ✅ 존재 확인 | D-3 (1건) |
| #11 Conversation-A2A | `3-8_Conversation-A2A/` | ✅ 존재 확인 | B-2 일부 |
| #12 Business-Strategy | `3-9_Business-Model-Strategy/` | ✅ 존재 확인 | D-5 (1건) |
| #17 MLOps-LLMOps | `4-4_MLOps-LLMOps/` | ✅ 존재 확인 | B-1 (1건) |
| AI Investing | `Ai-investing-detail/` | ✅ 완성 참조 모델 | C-1,2 (2건) |

---

## 6. 이슈 해결 매핑

### 6.1 섹션 A: §6.1 UI/UX v12 추가 (4건, 11 컴포넌트)

| 항목 ID | 항목명 | 소속 도메인 | 해결 방식 | 인덱스 파일 |
|---------|--------|-----------|----------|-----------|
| A-1a | BreathingGuide | #9 Health-Wellness | 정본 → `3-6_Health.../04_stress-management/breathing_exercises.md` | `01_wellness-ui/breathing_guide.md` |
| A-1b | GroundingExercise | #9 Health-Wellness | 정본 → `3-6_Health.../04_stress-management/grounding_technique.md` | `01_wellness-ui/grounding_exercise.md` |
| A-1c | MeditationTimer | #9 Health-Wellness | 정본 → `3-6_Health.../04_stress-management/mindfulness_meditation.md` | `01_wellness-ui/meditation_timer.md` |
| A-2a | ThoughtRecord | #9 Health-Wellness | 정본 → `3-6_Health.../04_stress-management/cbt_self_care.md` | `01_wellness-ui/thought_record.md` |
| A-2b | CognitiveDistortionDetector | #9 Health-Wellness | 정본 → `3-6_Health.../06_ethics-privacy/cbt_distortion_taxonomy.md` | `01_wellness-ui/cognitive_distortion_detector.md` |
| A-3a | WorkloadMonitor | #9 Health-Wellness | 정본 → `3-6_Health.../04_stress-management/burnout_prevention.md` | `01_wellness-ui/workload_monitor.md` |
| A-3b | ForcedBreakOverlay | #9 Health-Wellness | 정본 → `3-6_Health.../04_stress-management/burnout_prevention.md` | `01_wellness-ui/forced_break_overlay.md` |
| A-4a | FlashcardEditor | #8 Education | 정본 → `3-5_Education.../02_spaced-repetition/` | `02_learning-tools/flashcard_editor.md` |
| A-4b | SM2ReviewEngine | #6 PKM (주) + #8 Education (참조) | 정본 → `3-3_PKM.../03_spaced-repetition/`, 참조 → Education | `02_learning-tools/sm2_review_engine.md` |
| A-4c | ReviewDashboard | #8 Education | 정본 → `3-5_Education.../05_learning-analytics/` | `02_learning-tools/review_dashboard.md` |

### 6.2 섹션 B: §6.7 Agent Teams v12 추가 (2건)

| 항목 ID | 항목명 | 소속 도메인 | 해결 방식 | 인덱스 파일 |
|---------|--------|-----------|----------|-----------|
| B-1 | Prompt Registry API (CRUD + 버전관리 + A/B 테스트) | #17 MLOps (주) | 정본 → `4-4_MLOps.../01_prompt-versioning/`. 프롬프트 관리 정본은 MLOps, Agent Teams는 "에이전트 전용 인터페이스"로 한정 | `03_agent-teams/prompt_registry_api.md` |
| B-2 | 3 TemplateSets (TS_CORE / TS_WEB_RESEARCH / TS_CODE) | #11 Conversation-A2A (주) + #17 MLOps (참조) | 정본 → `3-8_Conversation.../`. 에이전트 대화 패턴 정본은 A2A | `03_agent-teams/template_sets.md` |

### 6.3 섹션 C: §6.8 AI Investing v12 추가 (2건)

| 항목 ID | 항목명 | 소속 도메인 | 해결 방식 | 인덱스 파일 |
|---------|--------|-----------|----------|-----------|
| C-1 | Black-Litterman 모델 (수학 공식 + 입출력 스키마) | AI Investing | 정본 → `Ai-investing-detail/`. 이미 완성된 참조 모델에 포함 | `04_investing-additions/black_litterman_model.md` |
| C-2 | Factor Investing (6 팩터 + 백테스팅) | AI Investing | 정본 → `Ai-investing-detail/`. 이미 완성된 참조 모델에 포함 | `04_investing-additions/factor_investing.md` |

### 6.4 섹션 D: §6.10 Cloud Library v12 추가 (10건)

| 항목 ID | 항목명 | 소속 도메인 | 해결 방식 | 인덱스 파일 |
|---------|--------|-----------|----------|-----------|
| D-1 | Evolution Control | #6 PKM | 정본 → `3-3_PKM.../01_knowledge-capture/` | `05_cloud-library/evolution_control.md` |
| D-2 | Korean Stopwords | #6 PKM | 정본 → `3-3_PKM.../01_knowledge-capture/` | `05_cloud-library/korean_stopwords.md` |
| D-3 | Code Snippets | #10 Dev-Tools | 정본 → `3-7_Developer.../01_coding-engine/` | `05_cloud-library/code_snippets.md` |
| D-4 | Idea Capture | #6 PKM | 정본 → `3-3_PKM.../01_knowledge-capture/` | `05_cloud-library/idea_capture.md` |
| D-5 | SWOT Analysis | #12 Business | 정본 → `3-9_Business.../02_market-analysis/` | `05_cloud-library/swot_analysis.md` |
| D-6 | Writing Support | #6 PKM | 정본 → `3-3_PKM.../01_knowledge-capture/` | `05_cloud-library/writing_support.md` |
| D-7 | Zettelkasten | #6 PKM | 정본 → `3-3_PKM.../06_zettelkasten/` | `05_cloud-library/zettelkasten.md` |
| D-8 | Knowledge Maturity | #6 PKM | 정본 → `3-3_PKM.../02_knowledge-graph/` | `05_cloud-library/knowledge_maturity.md` |
| D-9 | Task Checkpoint | #7 Workflow | 정본 → `3-4_Workflow.../01_dag-engine/` | `05_cloud-library/task_checkpoint.md` |
| D-10 | Zettelkasten Extension | #6 PKM | 정본 → `3-3_PKM.../06_zettelkasten/` | `05_cloud-library/zettelkasten_extension.md` |

### 6.5 섹션 E: V2-Phase 3 HIGH/MEDIUM (~15건)

| 항목 ID | 항목명 | 잠정 소속 도메인 | 해결 방식 | 비고 |
|---------|--------|----------------|----------|------|
| E-1 | Enhanced Context Window | #1 Verifier-Reasoning | 도메인 확정 시 이동 | HIGH |
| E-2 | Multi-turn Reasoning | #1 Verifier-Reasoning | 도메인 확정 시 이동 | HIGH |
| E-3 | Adaptive Prompt Optimization | #17 MLOps | 도메인 확정 시 이동 | HIGH |
| E-4 | Cross-session Memory | #6 PKM | 도메인 확정 시 이동 | HIGH |
| E-5 | Hybrid RAG v2 | #2 Auxiliary-Modules | 도메인 확정 시 이동 | HIGH |
| E-6 | Advanced Code Generation | #10 Dev-Tools | 도메인 확정 시 이동 | HIGH |
| E-7 | Multimodal Reasoning | #5 Multimodal | 도메인 확정 시 이동 | HIGH |
| E-8 | Agent Collaboration Protocol | #13 Agent-Protocol | 도메인 확정 시 이동 | HIGH |
| E-9 | Personalized Learning Path | #8 Education | 도메인 확정 시 이동 | MEDIUM |
| E-10 | Emotion-aware Dialogue | #9 Health-Wellness | 도메인 확정 시 이동 | MEDIUM |
| E-11 | Financial Report Generator | AI Investing | 도메인 확정 시 이동 | MEDIUM |
| E-12 | Workflow Template Marketplace | #7 Workflow | 도메인 확정 시 이동 | MEDIUM |
| E-13 | Privacy-preserving Analytics | #14 Rust-Tauri | 도메인 확정 시 이동 | MEDIUM |
| E-14 | Model Ensemble Framework | #17 MLOps | 도메인 확정 시 이동 | MEDIUM |
| E-15 | Cross-platform Sync | #14 Rust-Tauri | 도메인 확정 시 이동 | MEDIUM |

### 6.6 섹션 F: V3-Phase 2 MEDIUM (6건)

| 항목 ID | 항목명 | 잠정 소속 도메인 | 해결 방식 | 비고 |
|---------|--------|----------------|----------|------|
| F-1 | Federated Learning | #17 MLOps | 도메인 확정 시 이동 | MEDIUM |
| F-2 | KG Auto-builder | #6 PKM | 도메인 확정 시 이동 | MEDIUM |
| F-3 | Multi-agent Debate | #13 Agent-Protocol | 도메인 확정 시 이동 | MEDIUM |
| F-4 | Continuous Learning Pipeline | #17 MLOps | 도메인 확정 시 이동 | MEDIUM |
| F-5 | Cross-modal Transfer | #5 Multimodal | 도메인 확정 시 이동 | MEDIUM |
| F-6 | Autonomous Code Review | #10 Dev-Tools | 도메인 확정 시 이동 | MEDIUM |

### 6.7 섹션 G: V3-Phase 3 LOW (6건)

| 항목 ID | 항목명 | 잠정 소속 도메인 | 해결 방식 | 비고 |
|---------|--------|----------------|----------|------|
| G-1 | Neuromorphic Attention | #1 Verifier-Reasoning | 도메인 확정 시 이동 | LOW |
| G-2 | Quantum-inspired Optimization | #2 Auxiliary-Modules | 도메인 확정 시 이동 | LOW |
| G-3 | Self-evolving Agent | #13 Agent-Protocol | 도메인 확정 시 이동 | LOW |
| G-4 | Bio-inspired Memory Architecture | #6 PKM | 도메인 확정 시 이동 | LOW |
| G-5 | Swarm Intelligence Framework | #13 Agent-Protocol | 도메인 확정 시 이동 | LOW |
| G-6 | AGI Safety Framework | #13 Agent-Protocol | 도메인 확정 시 이동 | LOW |

### 6.8 이슈 해결 요약

| 카테고리 | 총 항목 | 도메인 확정 | 도메인 미확정(잠정) | 도메인 공유 |
|---------|--------|-----------|-----------------|-----------|
| 섹션 A (UI/UX) | 10건 | 10건 | 0건 | 1건 (SM2) |
| 섹션 B (Agent) | 2건 | 2건 | 0건 | 1건 (TS) |
| 섹션 C (Investing) | 2건 | 2건 | 0건 | 0건 |
| 섹션 D (Cloud) | 10건 | 10건 | 0건 | 0건 |
| 섹션 E (V2-P3) | 15건 | 0건 | 15건 | 0건 |
| 섹션 F (V3-P2) | 6건 | 0건 | 6건 | 0건 |
| 섹션 G (V3-P3) | 6건 | 0건 | 6건 | 0건 |
| **합계** | **~45건** | **24건** | **27건** | **2건** |

---

## 7. Phase 실행 계획

> **Tier 5 특성**: 독립적 Phase 불가. 각 v12 항목의 실행은 해당 도메인의 Phase에 종속된다. 본 도메인은 인덱스 갱신 + 추적만 수행한다.

### 7.1 Phase 정의

| Phase | 목표 | 종속 조건 | 산출물 |
|-------|------|----------|--------|
| **Phase 0: 인덱스 구축** | 6개 서브폴더 _index.md 생성 + 24건 확정 항목 인덱스 파일 작성 | PRE-01~04 완료 | _index.md 6개 + 항목 인덱스 ~30파일 |
| **Phase 1: 도메인 연결 확인** | ✅ 완료 (2026-04-12, P1-1). 24건 파일 수준 전수 검증 완료 — VALID 23건 + CONDITIONAL 1건(B-2), 95.8% 게이트 통과. C-1/C-2 경로 확정, §A.1 갱신. 재검증 0건. 이월: B-2 TemplateSet 전용 파일 미존재(Phase 2 귀속 확정 시 처리) | 대상 도메인 Phase 0 이상 완료 | 정합성 체크 리포트 |
| **Phase 2: V2/V3 항목 귀속 확정** | 27건 잠정 항목의 도메인 귀속 최종 확정 + 인덱스 이동 | 대상 도메인 계획서 완료 | 27건 도메인 매핑 확정 |
| **Phase 3: 횡단 추적 정례화** | 월 1회 인덱스 갱신 체계 확립 + 상태 대시보드 | 전체 도메인 Phase 1 이상 | 갱신 프로세스 문서 |

### 7.2 Phase 전환 게이트

| 전환 | 게이트 조건 |
|------|-----------|
| Phase 0 → 1 | 6개 _index.md 생성 + 24건 인덱스 파일 작성 완료 |
| Phase 1 → 2 | 24건 중 90% 이상 도메인 정본 파일 링크 유효 확인 |
| Phase 2 → 3 | 27건 잠정 항목 중 70% 이상 도메인 귀속 확정 |

#### Phase 0 단계별 상세 작업 절차

<details>
<summary><b>P0-1. 6개 서브폴더 _index.md 생성</b></summary>

**전제 조건**:
- PRE-01~04 완료 확인 필수 (특히 PRE-03: 전수 목록 확정)
- PRE 미완료 시 본 작업 진입 불가

**입력 파일**:
- 본 계획서 §2.1 (목표 폴더 트리 — 6개 서브폴더 구조)
- 본 계획서 §6 (이슈 해결 매핑 — 항목별 소속 도메인 + 정본 경로)
- 본 계획서 §3.4 (LOCK 보호 선언 — LOCK-V12-01~10 상속 매핑)
- 본 계획서 부록 §A (도메인별 정본 연결 마스터 테이블 — 51건 전수)
- `D:\VAMOS\docs\sot 2\5-3_v12-Additions-Detail\V12_ADDITIONS_상세명세.md` §A~§G (7개 섹션, 기술 명세 참조)

**등록 단위**: 컴포넌트 단위 (§A.1 기준: A-1a, A-1b, ... 각 행 = 1항목)

**적용 거버넌스 규칙**:
- R2: _index.md는 파일 목록만 (구현 상세 불가)
- R-19-1: 인덱스만 작성, 구현 상세 작성 시 REJECT
- R-T5-1: 도메인 횡단 항목은 정본 소유자 명시 필수
- R-19-5: 공유 항목(SM-2, TemplateSets 등)은 주 소유 도메인 + 참조 도메인 명시

**절차**:
1. PRE-01~04 완료 상태 확인 (§5.1 참조):
   - PRE-01: 9개 대상 도메인 폴더 존재 확인 완료 여부
   - PRE-02: 대상 도메인 계획서 최소 DRAFT 이상 여부
   - PRE-03: 상세명세 전수 목록 확정 여부 (항목 ID + 이름 + 섹션 매핑)
   - PRE-04: V2/V3 27건 잠정 도메인 귀속 초안 여부
2. 6개 서브폴더에 `_index.md` 생성 (§2.1 폴더 트리 준수):
   - `01_wellness-ui/_index.md`: 섹션 A-1~A-3 → **7건** (A-1a~A-1c, A-2a~A-2b, A-3a~A-3b)
   - `02_learning-tools/_index.md`: 섹션 A-4 → **3건** (A-4a~A-4c)
   - `03_agent-teams/_index.md`: 섹션 B-1~B-2 → **2건** (B-1, B-2)
   - `04_investing-additions/_index.md`: 섹션 C-1~C-2 → **2건** (C-1, C-2)
   - `05_cloud-library/_index.md`: 섹션 D-1~D-10 → **10건** (D-1~D-10)
   - `06_v2-v3-advanced/_index.md`: 섹션 E/F/G → **27건** (E-1~E-15, F-1~F-6, G-1~G-6)
3. 각 _index.md 포맷 (테이블 형식):
   ```markdown
   # {서브폴더명} — v12 항목 인덱스
   > 출처: 본 계획서 §6.X + 부록 §A

   | # | 항목 ID | 항목명 | 상세명세 섹션 | 소속 도메인 | 정본 경로 | LOCK 상속 | 상태 |
   |---|---------|--------|-------------|-----------|----------|----------|------|
   ```
   - 컬럼 값은 부록 §A.1 (확정 항목) 또는 §A.2 (잠정 항목)에서 직접 인용
   - `06_v2-v3-advanced/_index.md`만 "우선순위" 칼럼 추가 (HIGH/MEDIUM/LOW — §A.2 기준)
   - 공유 항목은 "주 소유 도메인 (주) + 참조 도메인 (참조)" 형식 (R-19-5)
4. LOCK 상속 참조 기입 (§3.4 + §A.4 기준):
   - `01_wellness-ui/_index.md`: LOCK-V12-05 (CBT 15유형), LOCK-V12-06 (4-7-8 호흡)
   - `02_learning-tools/_index.md`: LOCK-V12-02 (SM-2 알고리즘)
   - `03_agent-teams/_index.md`: LOCK-V12-07 (TS 3종)
   - `04_investing-additions/_index.md`: LOCK-V12-03 (tau), LOCK-V12-04 (Factor 6종), LOCK-V12-08 (max 비중)
   - `05_cloud-library/_index.md`: LOCK-V12-09 (Zettelkasten)
   - `06_v2-v3-advanced/_index.md`: 해당 없음 (잠정 항목 — 도메인 귀속 확정 후 LOCK 배정)

**검증** (→ §10.1 V-01 대응):
- [x] 6개 _index.md 파일 존재 (6/6) ✅
- [x] 각 _index.md 항목 전수 등록 — 기대 수량: 01=7, 02=3, 03=2, 04=2, 05=10, 06=27 (총 51건) ✅
- [x] 각 항목에 소속 도메인 + 정본 경로 포함 (§6 + 부록 §A와 일치) ✅
- [x] 공유 항목(A-4b SM2, B-2 TS)에 주/참조 도메인 명시 (R-19-5) ✅
- [x] LOCK 상속 참조 기입 완료: 01=2건, 02=1건, 03=1건, 04=3건, 05=1건, 06=0건 ✅
- [x] R-19-1 준수: 구현 상세(스키마, 알고리즘 등) 미포함 확인 ✅

**산출물**: 6개 `_index.md` 파일 — **완료 (2026-04-02)**
</details>

<details>
<summary><b>P0-2. 24건 확정 항목 인덱스 파일 작성</b></summary>

**전제 조건**:
- P0-1 완료 필수 (6개 _index.md 생성 완료 확인)
- P0-1 미완료 시 본 작업 진입 불가

**입력 파일**:
- `D:\VAMOS\docs\sot 2\5-3_v12-Additions-Detail\V12_ADDITIONS_상세명세.md` §A~§D (24건 확정 — 항목별 기술 명세 참조)
- 본 계획서 §2.1 (목표 폴더 트리 — 24개 파일의 폴더 배치 정본)
- 본 계획서 §6.1~§6.4 (이슈 해결 매핑 — 항목별 정본 경로 확정값)
- 본 계획서 §3.4 + §A.4 (LOCK 보호 선언 — LOCK 상속 참조 매트릭스)
- 본 계획서 부록 §A.1 (도메인별 정본 연결 마스터 테이블 — 24건 전수)

**등록 단위**: 컴포넌트 단위 (§A.1 기준: 각 행 = 1파일 = 1인덱스)

**적용 거버넌스 규칙**:
- R-19-1: 인덱스만 작성, 구현 상세(스키마, 알고리즘, API 정의 등) 작성 시 REJECT
- R-19-5: 공유 항목은 "주 소유 도메인 (주) + 참조 도메인 (참조)" 형식 필수
- R-T5-1: 도메인 횡단 항목은 정본 소유자 명시 필수
- R2: 파일 목록만 (구현 상세 불가)

**절차**:
1. `01_wellness-ui/`에 **7건** 인덱스 파일 작성 (섹션 A-1~A-3 → 전원 #9 Health-Wellness):
   - `breathing_guide.md` (A-1a BreathingGuide → 정본: `3-6_Health.../04_stress-management/breathing_exercises.md`, LOCK-HW-07)
   - `grounding_exercise.md` (A-1b GroundingExercise → 정본: `3-6_Health.../04_stress-management/grounding_technique.md`, LOCK-HW-08)
   - `meditation_timer.md` (A-1c MeditationTimer → 정본: `3-6_Health.../04_stress-management/mindfulness_meditation.md`)
   - `thought_record.md` (A-2a ThoughtRecord → 정본: `3-6_Health.../04_stress-management/cbt_self_care.md`, LOCK-HW-09)
   - `cognitive_distortion_detector.md` (A-2b CognitiveDistortionDetector → 정본: `3-6_Health.../06_ethics-privacy/cbt_distortion_taxonomy.md`, LOCK-HW-09)
   - `workload_monitor.md` (A-3a WorkloadMonitor → 정본: `3-6_Health.../04_stress-management/burnout_prevention.md`)
   - `forced_break_overlay.md` (A-3b ForcedBreakOverlay → 정본: `3-6_Health.../04_stress-management/burnout_prevention.md`)
2. `02_learning-tools/`에 **3건** 인덱스 파일 작성 (섹션 A-4):
   - `flashcard_editor.md` (A-4a FlashcardEditor → #8 Education, 정본: `3-5_Education.../02_spaced-repetition/`)
   - `sm2_review_engine.md` (A-4b SM2ReviewEngine → **#6 PKM (주) + #8 Education (참조)**, 정본: `3-3_PKM.../03_spaced-repetition/`, #6 PKM SM-2 LOCK) ← R-19-5 적용
   - `review_dashboard.md` (A-4c ReviewDashboard → #8 Education, 정본: `3-5_Education.../05_learning-analytics/`)
3. `03_agent-teams/`에 **2건** 인덱스 파일 작성 (섹션 B):
   - `prompt_registry_api.md` (B-1 Prompt Registry API → **#17 MLOps (주)**, 정본: `4-4_MLOps.../01_prompt-versioning/`, LOCK-ML-02/03) ← R-T5-1 적용
   - `template_sets.md` (B-2 TemplateSets 3종 → **#11 Conversation-A2A (주) + #17 MLOps (참조)**, 정본: `3-8_Conversation.../`, LOCK-V12-07) ← R-19-5 적용
4. `04_investing-additions/`에 **2건** 인덱스 파일 작성 (섹션 C):
   - `black_litterman_model.md` (C-1 Black-Litterman → AI Investing, 정본: `Ai-investing-detail/`, AI-Invest tau=0.025 LOCK)
   - `factor_investing.md` (C-2 Factor Investing → AI Investing, 정본: `Ai-investing-detail/`, AI-Invest Factor 6종 LOCK + AI-Invest max 비중 LOCK)
5. `05_cloud-library/`에 **10건** 인덱스 파일 작성 (섹션 D — 4개 도메인 분산):
   - `evolution_control.md` (D-1 Evolution Control → #6 PKM, 정본: `3-3_PKM.../01_knowledge-capture/`)
   - `korean_stopwords.md` (D-2 Korean Stopwords → #6 PKM, 정본: `3-3_PKM.../01_knowledge-capture/`)
   - `code_snippets.md` (D-3 Code Snippets → **#10 Dev-Tools**, 정본: `3-7_Developer.../01_coding-engine/`)
   - `idea_capture.md` (D-4 Idea Capture → #6 PKM, 정본: `3-3_PKM.../01_knowledge-capture/`)
   - `swot_analysis.md` (D-5 SWOT Analysis → **#12 Business**, 정본: `3-9_Business.../02_market-analysis/`)
   - `writing_support.md` (D-6 Writing Support → #6 PKM, 정본: `3-3_PKM.../01_knowledge-capture/`)
   - `zettelkasten.md` (D-7 Zettelkasten → #6 PKM, 정본: `3-3_PKM.../06_zettelkasten/`, #6 PKM Zettelkasten LOCK)
   - `knowledge_maturity.md` (D-8 Knowledge Maturity → #6 PKM, 정본: `3-3_PKM.../02_knowledge-graph/`)
   - `task_checkpoint.md` (D-9 Task Checkpoint → **#7 Workflow**, 정본: `3-4_Workflow.../01_dag-engine/`)
   - `zettelkasten_extension.md` (D-10 Zettelkasten Extension → #6 PKM, 정본: `3-3_PKM.../06_zettelkasten/`, #6 PKM Zettelkasten LOCK)
6. 각 파일 포맷 (§8 "1-page 요약 + 도메인 정본 링크" 준수):
   ```markdown
   # {항목명}
   > 항목 ID: {A-1a} | 상세명세 섹션: {A-1} | 소속 도메인: {#9 Health-Wellness}

   ## 요약
   {상세명세에서 발췌한 1~3문장 기능 설명 — 구현 상세(스키마, 알고리즘) 제외}

   ## 도메인 정본 연결
   | 항목 | 값 |
   |------|-----|
   | 정본 폴더 | `{sot 2/ 정본 폴더 경로}` |
   | 정본 파일 | `{정본 파일 추정 경로}` |
   | LOCK 상속 | {LOCK ID + 값 요약} 또는 "해당 없음" |
   | 주 소유 도메인 | {도메인명} |
   | 참조 도메인 | {도메인명} 또는 "해당 없음" |

   ## 출처
   - 상세명세: `V12_ADDITIONS_상세명세.md` §{섹션}
   - 계획서: 본 계획서 §6.X #{행번호} + 부록 §A.1 #{행번호}
   ```
   - 공유 항목 2건(A-4b, B-2)은 "주 소유 도메인" + "참조 도메인" 반드시 분리 기입 (R-19-5). B-1은 공유가 아닌 횡단 항목(R-T5-1) — §9.3 C-02 판정 참조
   - LOCK 해당 항목(11건: A-1a, A-1b, A-2a, A-2b, A-4b, B-1, B-2, C-1, C-2, D-7, D-10)은 LOCK ID + 값 요약 기입 (§A.4 참조)
   - LOCK 미해당 항목(13건)은 "해당 없음" 명시
   - V12 교차참조: §A.4에 V12 대응이 있는 LOCK(9건: A-1a→V12-06, A-2a/b→V12-05, A-4b→V12-02, B-2=V12-07, C-1→V12-03, C-2→V12-04/08, D-7/D-10→V12-09)은 `(→ LOCK-V12-XX)` 형식으로 _index.md와 동일 패턴 기입. V12 대응 없는 LOCK(A-1b LOCK-HW-08, B-1 LOCK-ML-02/03)은 도메인 LOCK만 기재
   - 동일 LOCK 상속 항목(예: A-2a, A-2b = LOCK-HW-09)은 값 설명을 §A.4 정본값으로 통일

**검증** (→ §10.1 V-02, V-03, V-11 대응):
- [x] 24건 인덱스 파일 존재 — 서브폴더별 기대 수량: 01=7, 02=3, 03=2, 04=2, 05=10 (총 24건) ✅
- [x] 각 파일의 소속 도메인 + 정본 경로가 §6.1~§6.4 및 부록 §A.1과 일치 ✅
- [x] 공유 항목 2건(A-4b, B-2)에 주/참조 도메인 분리 명시 (R-19-5), 횡단 항목 1건(B-1)에 정본 소유자 명시 (R-T5-1) ✅
- [x] LOCK 해당 항목 11건(A-1a, A-1b, A-2a, A-2b, A-4b, B-1, B-2, C-1, C-2, D-7, D-10)에 LOCK ID + 값 기입 ✅
- [x] V12 교차참조 9건에 `(→ LOCK-V12-XX)` 기입, _index.md 패턴 일치 ✅
- [x] 동일 LOCK(HW-09) 상속 항목(A-2a, A-2b) 값 설명 §A.4 정본값("15가지 인지 왜곡 유형")으로 통일 ✅
- [x] R-19-1 준수: 각 파일 18줄 (< 50줄), 구현 상세(인터페이스 정의, 알고리즘 수식, API 엔드포인트 등) 미포함 ✅
- [x] 네이밍 규칙 준수 (§2.3): 영문 소문자 + 언더스코어 + `.md` ✅
- [x] P0-1 _index.md와 정합성: 각 인덱스 파일이 해당 서브폴더 _index.md에 등록된 항목과 1:1 대응 ✅

**산출물**: 24개 항목별 인덱스 파일 (5개 서브폴더에 분산: 01=7, 02=3, 03=2, 04=2, 05=10) — **완료 (2026-04-02)**
</details>

<details>
<summary><b>P0-3. LOCK 상속 검증</b></summary>

**전제 조건**:
- P0-2 완료 필수 (24건 인덱스 파일 LOCK 기입 완료 확인)
- P0-2 미완료 시 본 작업 진입 불가

**입력 파일**:
- 본 계획서 §3.4 (LOCK 보호 선언 — LOCK-V12-01~10 정의, 상속 출처, 값, 비고)
- 본 계획서 부록 §A.4 (LOCK 상속 참조 매트릭스 — 상속 원본 도메인 + 상속 원본 LOCK ID + 값 요약)
- P0-1 산출물 (6개 _index.md의 LOCK 상속 참조 기입 — 01=2건, 02=1건, 03=1건, 04=3건, 05=1건, 06=0건)
- P0-2 산출물 (24개 인덱스 파일의 LOCK 기입 — 11건 해당 + 13건 "해당 없음")
- 해당 도메인 구조화_종합계획서 LOCK 섹션 (6개 도메인):
  - `3-3_PKM-Knowledge-Management/` 계획서 LOCK 섹션 — PKM SM-2 LOCK (V12-02), PKM Zettelkasten LOCK (V12-09)
  - `3-5_Education-Learning/` 계획서 LOCK 섹션 — SM-2 공유 LOCK 참조 확인 (V12-02 R-19-5)
  - `3-6_Health-Wellness-EmotionAI/` 계획서 LOCK 섹션 — LOCK-HW-07 (V12-06), LOCK-HW-09 (V12-05)
  - `3-8_Conversation-A2A/` 계획서 LOCK 섹션 — TS 3종 LOCK 주 소유 (V12-07)
  - `4-4_MLOps-LLMOps/` 계획서 LOCK 섹션 — TS 3종 LOCK 참조 확인 (V12-07 R-19-5)
  - `Ai-investing-detail/` 계획서 LOCK 섹션 — AI-Invest tau LOCK (V12-03), Factor LOCK (V12-04), Constraints LOCK (V12-08)

**적용 거버넌스 규칙**:
- R-19-1: v12 항목은 해당 도메인 LOCK 상속, 자체 LOCK 정의 금지 — LOCK-V12-01 원칙과 일치 확인
- R-19-5: 공유 항목(SM-2, TemplateSets)은 주 소유 도메인 + 참조 도메인의 LOCK 양쪽 확인 필수
- §9.2 충돌 해결 우선순위: 불일치 발견 시 "1. LOCK 보호 값 → 해당 도메인 LOCK 값 우선" 원칙 적용

**대조 방법**: 글자 그대로 대조 — §A.4 "값 요약" 컬럼의 텍스트와 도메인 정본 LOCK의 해당 값을 문자열 수준에서 일치 확인 (§12 S8-4 QC 기준 동일)

**절차**:
1. LOCK-V12-01, LOCK-V12-10 자체 정의 확인 (도메인 대조 불요 — 자체 규칙):
   - LOCK-V12-01: §4 R-19-1 규칙 "v12 항목은 해당 도메인 sot 2/ 폴더에 원본 유지, 여기는 인덱스만"이 §3.4 LOCK-V12-01 값 "v12 항목은 해당 도메인 LOCK 상속"과 의미 일치하는지 확인
   - LOCK-V12-10: 부록 §A 매핑 테이블 존재 + 51건(§A.1 확정 24건 + §A.2 잠정 27건) 전수 등록 확인
2. LOCK-V12-02~09 (8건) 도메인 LOCK 값 글자 그대로 대조:
   - LOCK-V12-02 (SM-2 알고리즘 공식):
     - §A.4 값: "ease_factor, interval 공식" / §3.4 값: "ease_factor 업데이트, interval 계산"
     - 주 대조: #6 PKM 계획서 LOCK (PKM SM-2 LOCK) ← 주 소유 도메인 (§A.4 상속 원본)
     - 부 대조: #8 Education 계획서 LOCK에 SM-2 참조 존재 여부 확인 (R-19-5 공유 LOCK, §3.4 비고 "공유 LOCK")
     - 참고: §3.4는 "#6 PKM LOCK + #8 Education LOCK" 양쪽 기재, §A.4는 "#6 PKM"만 기재 — §A.4가 주 소유 도메인 기준이므로 의도적 차이로 판정 (불일치 아님)
   - LOCK-V12-03 (Black-Litterman tau):
     - §A.4 값: "tau = 0.025"
     - 대조: Ai-investing-detail 계획서 LOCK (AI-Invest tau LOCK)
   - LOCK-V12-04 (Factor 6종 정의):
     - §A.4 값: "6종: Value/Momentum/Quality/Size/Volatility/Dividend"
     - 대조: Ai-investing-detail 계획서 LOCK (AI-Invest Factor LOCK)
   - LOCK-V12-05 (CBT 15가지 인지 왜곡 유형):
     - §A.4 값: "15가지 인지 왜곡 유형" / §3.4 값: "전부 아니면 전무, 과잉일반화, 파국화 등 15종"
     - 대조: #9 Health-Wellness 계획서 LOCK-HW-09 (§A.4 상속 원본 LOCK ID "LOCK-HW-09")
     - 참고: §3.4는 "#9 Health-Wellness LOCK" (구체 ID 미기재), §A.4는 "LOCK-HW-09" 명시 — 대조 시 §A.4 LOCK ID 기준
   - LOCK-V12-06 (BreathingPattern 4-7-8):
     - §A.4 값: "4-7-8 호흡법 (흡4초-지7초-호8초)"
     - 대조: #9 Health-Wellness 계획서 LOCK-HW-07 (§3.4, §A.4 모두 LOCK-HW-07 명시 — 일치)
   - LOCK-V12-07 (TS_CORE/TS_WEB_RESEARCH/TS_CODE 3종):
     - §A.4 값: "TS_CORE, TS_WEB_RESEARCH, TS_CODE"
     - 주 대조: #11 Conversation-A2A 계획서 LOCK ← 주 소유 도메인 (§6.2 B-2 "에이전트 대화 패턴 정본은 A2A")
     - 부 대조: #17 MLOps 계획서 LOCK에 TS 참조 존재 여부 확인 (R-19-5 공유 LOCK)
     - 참고: §3.4는 "#17 MLOps / #11 A2A LOCK" 순서 기재, §A.4는 "#11 A2A + #17 MLOps" 기재 — 주/참 관계는 §6.2 B-2 판정 기준
   - LOCK-V12-08 (PortfolioConstraints max 비중):
     - §A.4 값: "단일 종목 max 10%, 단일 섹터 max 30%"
     - 대조: Ai-investing-detail 계획서 LOCK (AI-Invest Constraints LOCK)
   - LOCK-V12-09 (Zettelkasten 원자적 노트 원칙):
     - §A.4 값: "원자적 노트, 5종 링크 타입"
     - 대조: #6 PKM 계획서 LOCK (PKM Zettelkasten LOCK)
3. P0-1/P0-2 산출물 LOCK 기입 정합성 교차 확인:
   - P0-1 _index.md 6개의 LOCK 상속 참조 기입값이 §A.4 + 절차 2 도메인 대조 결과와 일치하는지 확인:
     - `01_wellness-ui/_index.md`: LOCK-V12-05 (CBT 15유형), LOCK-V12-06 (4-7-8 호흡) 기입값
     - `02_learning-tools/_index.md`: LOCK-V12-02 (SM-2 알고리즘) 기입값
     - `03_agent-teams/_index.md`: LOCK-V12-07 (TS 3종) 기입값
     - `04_investing-additions/_index.md`: LOCK-V12-03 (tau), LOCK-V12-04 (Factor 6종), LOCK-V12-08 (max 비중) 기입값
     - `05_cloud-library/_index.md`: LOCK-V12-09 (Zettelkasten) 기입값
     - `06_v2-v3-advanced/_index.md`: LOCK 상속 "해당 없음" 확인 (잠정 항목 — 도메인 귀속 미확정)
   - P0-2 인덱스 파일 LOCK 기입 교차 확인:
     - V12 대응 9건: A-1a (LOCK-HW-07 → V12-06), A-2a/A-2b (LOCK-HW-09 → V12-05), A-4b (PKM SM-2 → V12-02), B-2 (V12-07), C-1 (V12-03), C-2 (V12-04 + V12-08), D-7/D-10 (V12-09) — `(→ LOCK-V12-XX)` 형식 기입 확인
     - V12 미대응 2건: A-1b (LOCK-HW-08), B-1 (LOCK-ML-02/03) — 도메인 LOCK만 기재, LOCK-V12 매핑 없음이 정당한지 확인 (§3.4에 해당 LOCK-V12 미등록 = 정상)
     - LOCK 미해당 13건: "해당 없음" 명시 확인
4. §3.4 ↔ §A.4 내부 정합성 확인 (10건 전수):
   - 각 LOCK-V12의 §3.4 "상속 출처" 컬럼과 §A.4 "상속 원본 도메인" 컬럼 대조
   - 각 LOCK-V12의 §3.4 "값" 컬럼과 §A.4 "값 요약" 컬럼 대조
   - 공유 LOCK(V12-02, V12-07): §3.4가 복수 도메인, §A.4가 주 소유 도메인 기준 — 의도적 차이로 판정 (§A.4는 상속 원본만 기재하는 구조)
   - 그 외 불일치 발견 시 CONFLICT_LOG 등록
5. 불일치 발견 시 처리:
   - 값 불일치: §9.2 우선순위 1 "도메인 LOCK 값 우선" 적용 → §3.4/§A.4 값을 도메인 값에 맞춰 정정 → CONFLICT_LOG 등록
   - P0-1/P0-2 기입 오류: 해당 _index.md 또는 인덱스 파일 정정 후 재검증
   - §3.4 ↔ §A.4 불일치: §A.4가 상세 매트릭스이므로 §A.4 기준으로 §3.4 정정 → CONFLICT_LOG 등록

**검증** (→ §10.1 V-04 대응, §10.2 V-07 선행):
- [x] LOCK-V12-01 자체 규칙: R-19-1과 의미 일치 확인 ✅
- [x] LOCK-V12-10 자체 정의: 부록 §A 매핑 테이블 51건 존재 확인 ✅
- [x] LOCK-V12-02~09 (8건) 도메인 LOCK 글자 그대로 대조 완료 ✅ — 3건 PASS(V12-02,04,06), 3건 CONDITIONAL(V12-03,07,08), 2건 FAIL(V12-05,09)
- [x] 공유 LOCK 2건(V12-02 SM-2, V12-07 TS) 주 소유 + 참조 도메인 양쪽 확인 (R-19-5) ✅ — V12-02: Education LOCK-ED-04 PKM 참조 확인. V12-07: W-05 정본=A2A 확인 (C-07 전용 LOCK 부재 참고)
- [x] P0-1 _index.md LOCK 기입값 8건 정합성 확인 ✅
- [x] P0-2 인덱스 파일: V12 대응 9건 + V12 미대응 2건 + 미해당 13건 정합성 확인 ✅ — 24/24 전수 PASS
- [x] §3.4 ↔ §A.4 내부 정합성 10건 대조 완료 ✅ — 의도적 차이 4건, 실질 불일치 0건
- [ ] 불일치 0건 (또는 전건 CONFLICT_LOG 등록 + 정정 완료) — ❌ 5건 CONFLICT_LOG 등록 (C-04~C-08 OPEN). C-04(V12-05 CBT↔HW-09 매핑), C-05(V12-09 링크타입 4종→5종), C-06(V12-08 현금비중), C-07(V12-07 TS LOCK 부재), C-08(V12-03 tau 도메인내부)

**산출물**:
- LOCK 상속 검증 결과 리포트 (10건 전수: 자체 2건 + 도메인 대조 8건 + P0-1/P0-2 교차 확인 + §3.4↔§A.4 정합성) — **완료 (2026-04-03)**
- AUTHORITY_CHAIN.md 갱신: 검증 이력 기록 (대조일 2026-04-03, 5건 PASS / 3건 CONDITIONAL / 2건 FAIL, 불일치 5건) → §10.1 V-04 기등록 확인 — **완료 (2026-04-03)**
- CONFLICT_LOG.md: C-04~C-08 신규 5건 OPEN 등록 (§9 프로토콜 적용) — **완료 (2026-04-03)**
</details>

<details>
<summary><b>P0-4. 도메인 정본 파일 경로 검증</b></summary>

**전제 조건**:
- P0-2 완료 필수 (24건 인덱스 파일의 도메인 정본 링크 기입 완료 확인)
- P0-2 미완료 시 본 작업 진입 불가
- P0-3 완료 권장 (LOCK 상속 검증 결과 반영). P0-3 미완료 시에도 경로 검증 자체는 진행 가능하나, P0-3 CONFLICT_LOG(C-04~C-08)의 경로 영향 여부를 사후 교차 확인해야 함
- **Phase 위치**: 본 작업은 Phase 0→1 전환 게이트(§7.2 "6개 _index.md 생성 + 24건 인덱스 파일 작성 완료")의 필수 조건이 아닌, Phase 0 품질 보증 단계. Phase 1(V-06 "24건 정본 파일 실제 존재 확인 90% 이상") 원활 진행을 위한 사전 검증 데이터를 제공함

**입력 파일**:
- P0-2 산출물 (24개 인덱스 파일의 도메인 정본 링크 — 각 파일의 "정본 폴더" + "정본 파일" 값)
- 본 계획서 §6.1~§6.4 (이슈 해결 매핑 — 항목별 정본 경로 **정본값**. P0-2 인덱스 파일과 교차 대조용)
- 본 계획서 부록 §A.1 (도메인별 정본 연결 마스터 테이블 — 24건 전수 "정본 파일 (추정 경로)" 칼럼)
- 본 계획서 §5.2 (대상 도메인 존재 확인 체크리스트 — PRE-01 결과, 9개 도메인 최상위 폴더 존재 기확인)

**적용 거버넌스 규칙**:
- R-19-1: 검증 결과 리포트에 구현 상세 기술 금지 — 경로 존재/부존재 사실만 기록
- R-19-2: 미존재 경로 발견 시, 해당 도메인 정본 폴더에 생성 요청 또는 인덱스 파일 경로 정정 필요 (양방향 정합성)
- §9.2: 경로 불일치(P0-2 기입값 ≠ §6/§A.1 정본값) 발견 시 "3순위: 도메인 정본 → 해당 도메인 sot 2/ 계획서 정의 우선" 적용
- R6: OPEN 충돌 존재 시 주의 — 경로 미존재 건은 CONFLICT_LOG 등록 대상

**대조 방법**:
- **3단계 검증**: ① 도메인 최상위 폴더 존재 (PRE-01 기확인값 재확인) → ② 서브폴더 존재 (§A.1 "정본 파일 (추정 경로)" 칼럼의 폴더 부분) → ③ 정본 파일 존재 (§6.1~§6.4 해결 방식 칼럼의 파일명, 파일명 특정 가능한 항목만)
- **교차 대조**: P0-2 인덱스 파일의 "정본 폴더"/"정본 파일" 값이 §6 + §A.1 정본값과 일치하는지 확인. 불일치 시 §A.1 기준으로 P0-2 인덱스 파일 정정
- **PRE-01 차별화**: PRE-01은 9개 도메인 **최상위 폴더** 존재만 확인 (§5.2 DONE). P0-4는 최상위 폴더 하위의 **서브폴더 + 파일** 수준까지 검증
- **경로 정밀도 3등급**: §A.1 기준으로 24건을 정밀도별 분류 —
  - 파일 수준 (7건): §6.1에 파일명까지 특정된 항목 (A-1a~c, A-2a~b, A-3a~b)
  - 서브폴더 수준 (14건): §A.1에 서브폴더까지만 기재된 항목 (A-4a~c, B-1, D-1~D-10)
  - 기술적 설명만 (3건): §A.1에 괄호 설명만 기재된 항목 (B-2, C-1, C-2)

**절차**:
1. P0-2 인덱스 파일 24건의 "정본 폴더"/"정본 파일" 값을 §6.1~§6.4 + §A.1과 교차 대조하여, 검증 대상 경로 목록 확정:
   - 불일치 항목 발견 시: §A.1 기준으로 검증 대상 경로 확정 + P0-2 인덱스 파일 정정 필요 건 별도 기록

2. 24건을 **정본 도메인 기준**으로 분류하여 서브폴더 + 파일 존재 확인 (Read/Glob으로 확인):

   **#9 Health-Wellness — 7건** (A-1a~c, A-2a~b, A-3a~b):
   - 서브폴더 `3-6_Health-Wellness-EmotionAI/04_stress-management/` 존재 확인 (6건 공통: A-1a~c, A-2a, A-3a~b)
   - 서브폴더 `3-6_Health-Wellness-EmotionAI/06_ethics-privacy/` 존재 확인 (A-2b)
   - 파일 수준 확인 (§6.1 정본 경로 기준, 6개 고유 파일):
     - A-1a: `04_stress-management/breathing_exercises.md`
     - A-1b: `04_stress-management/grounding_technique.md`
     - A-1c: `04_stress-management/mindfulness_meditation.md`
     - A-2a: `04_stress-management/cbt_self_care.md`
     - A-2b: `06_ethics-privacy/cbt_distortion_taxonomy.md`
     - A-3a/A-3b: `04_stress-management/burnout_prevention.md` ← 2건이 동일 파일 공유 (§6.1 의도적)

   **#6 PKM — 8건** (A-4b, D-1, D-2, D-4, D-6, D-7, D-8, D-10):
   - 서브폴더 `3-3_PKM-Knowledge-Management/03_spaced-repetition/` 존재 확인 (A-4b — SM2ReviewEngine, 주 소유 도메인=PKM)
   - 서브폴더 `3-3_PKM-Knowledge-Management/01_knowledge-capture/` 존재 확인 (D-1, D-2, D-4, D-6 — 4건 공통 폴더)
   - 서브폴더 `3-3_PKM-Knowledge-Management/06_zettelkasten/` 존재 확인 (D-7, D-10 — 2건 공통 폴더)
   - 서브폴더 `3-3_PKM-Knowledge-Management/02_knowledge-graph/` 존재 확인 (D-8)
   - 파일 수준: §A.1에 서브폴더까지만 기재 (파일명 미특정) → 서브폴더 존재 확인으로 판정. 파일 특정은 Phase 1(V-06)에서 수행

   **#8 Education — 2건** (A-4a, A-4c):
   - 서브폴더 `3-5_Education-Learning/02_spaced-repetition/` 존재 확인 (A-4a FlashcardEditor)
   - 서브폴더 `3-5_Education-Learning/05_learning-analytics/` 존재 확인 (A-4c ReviewDashboard)
   - 참고: A-4b(SM2ReviewEngine)는 정본 도메인이 #6 PKM이므로 PKM에서 검증 (§6.1, §A.1 #9행 근거)

   **#17 MLOps — 1건** (B-1):
   - 서브폴더 `4-4_MLOps-LLMOps/01_prompt-versioning/` 존재 확인

   **#11 A2A — 1건** (B-2):
   - 최상위 폴더 `3-8_Conversation-A2A/` 존재 확인 (PRE-01 기확인)
   - 서브폴더: §6.2/§A.1에 "(에이전트 대화 패턴 폴더)"로만 기재, 구체적 서브폴더 미특정 → 최상위 폴더 존재로 CONDITIONAL PASS 판정 + Phase 1에서 서브폴더 특정 필요 건으로 기록

   **Ai-investing-detail — 2건** (C-1, C-2):
   - 최상위 폴더 `Ai-investing-detail/` 존재 확인 (PRE-01 기확인, §5.2 "완성 참조 모델")
   - 서브폴더: §A.1에 "(포트폴리오 최적화 폴더)", "(팩터 투자 폴더)"로만 기재, 구체적 서브폴더 미특정 → 최상위 폴더 존재로 CONDITIONAL PASS 판정 + Phase 1에서 서브폴더 특정 필요 건으로 기록

   **#10 Dev-Tools — 1건** (D-3):
   - 서브폴더 `3-7_Developer-Tools-API-SDK/01_coding-engine/` 존재 확인

   **#12 Business — 1건** (D-5):
   - 서브폴더 `3-9_Business-Model-Strategy/02_market-analysis/` 존재 확인

   **#7 Workflow — 1건** (D-9):
   - 서브폴더 `3-4_Workflow-RPA/01_dag-engine/` 존재 확인

3. 검증 결과 분류 (24건 전수):
   - **PASS**: 서브폴더 존재 + 파일 존재 (파일명 특정 항목) 또는 서브폴더 존재 (파일명 미특정 항목)
   - **CONDITIONAL PASS**: 최상위 폴더 존재하나 서브폴더 미특정 (§A.1 괄호 설명만 있는 3건: B-2, C-1, C-2) → Phase 1에서 경로 특정 필요
   - **FAIL**: 서브폴더 또는 파일 미존재

4. 미존재 경로 발견 시 처리:
   - 서브폴더 미존재: 해당 도메인 계획서의 폴더 구조 확인 → 실제 서브폴더명과 §A.1 추정 경로 대조 → 경로명 차이(오타, 네이밍 변경)인 경우 §A.1 + P0-2 인덱스 파일 정정
   - 파일 미존재 (파일명 특정 7건 대상): 해당 서브폴더 내 유사 파일명 검색(Glob) → 파일명 차이인 경우 §6.1 + §A.1 + P0-2 인덱스 파일 정정
   - 서브폴더·파일 모두 미존재 (도메인에 해당 구조 자체 없음): CONFLICT_LOG에 OPEN 등록 (§9.2 3순위 "도메인 정본 우선" 적용) + 해당 도메인에 정본 파일 생성 요청 또는 P0-2 인덱스 파일에 "(미생성 — Phase 1 대기)" 표기

5. P0-3 CONFLICT_LOG OPEN 건(C-04~C-08) 경로 영향 교차 확인:
   - C-04 (V12-05 CBT↔HW-09 매핑): A-2a/A-2b 정본 **경로**에 영향 없음 (LOCK 매핑 문제이지 경로 문제 아님) → 확인
   - C-05 (V12-09 링크타입 4종↔5종): D-7/D-10 정본 **경로**에 영향 없음 (값 불일치이지 경로 문제 아님) → 확인
   - C-06 (V12-08 현금비중): C-2 정본 **경로**에 영향 없음 → 확인
   - C-07 (V12-07 TS LOCK 부재): B-2 정본 **경로**에 영향 없음 → 확인
   - C-08 (V12-03 tau 도메인내부): C-1 정본 **경로**에 영향 없음 → 확인
   - 영향 있는 건 발견 시: CONFLICT_LOG 갱신 + 해당 경로 재검증

**검증** (→ §10.2 V-06 선행 데이터 제공, §10.4 V-12 관련):
- [x] 24건 정본 경로 전수 검증 완료 (PASS / CONDITIONAL PASS / FAIL 분류) ✅ — 14 PASS(서브폴더 수준) + 3 CONDITIONAL PASS(최상위 폴더 수준) + 7 FAIL(파일 수준 미존재)
- [x] P0-2 인덱스 파일 "정본 폴더"/"정본 파일" 값과 §6.1~§6.4 + §A.1 교차 대조 24/24 완료 ✅ — 24/24 전수 일치, 불일치 0건, 정정 불요
- [ ] 미존재 경로 0건 (또는 전건 처리 완료: 경로 정정 또는 CONFLICT_LOG 등록) — ❌ 7건 미해소(Phase 1 대기): #9 Health-Wellness 정본 파일 6개 고유 파일(7건: A-1a~c, A-2a~b, A-3a/b — A-3a/b는 `burnout_prevention.md` 공유) 미생성. 서브폴더(`04_stress-management/`, `06_ethics-privacy/`) 존재하나 개별 정본 파일 미생성. Glob으로 유사 파일명 검색 결과 0건. CONFLICT_LOG 미등록 사유: §9.1 충돌 유형(소유권/값/매핑 충돌) 비해당 — 경로 매핑 자체는 유효하며 도메인이 해당 콘텐츠를 아직 생성하지 않은 상태. Phase 1(V-06) 진입 시 #9 도메인 파일 생성 확인이 선행 조건
- [x] CONDITIONAL PASS 건 목록 확정 (Phase 1 서브폴더/파일 특정 필요 건 — 3건: B-2, C-1, C-2) ✅ — B-2: A2A 서브폴더 미특정(§A.1 "(에이전트 대화 패턴 폴더)"), C-1/C-2: Ai-investing 서브폴더 미특정(§A.1 "(포트폴리오 최적화 폴더)", "(팩터 투자 폴더)"). 단, 도메인 내 관련 콘텐츠 존재 확인: C-1→`15_portfolio-advanced/portfolio_optimization.md`, C-2→`20_strategy-detail/quant/factor.md`
- [x] P0-3 CONFLICT_LOG OPEN 5건(C-04~C-08) 경로 영향 교차 확인 완료 ✅ — 5건 전부 경로 영향 없음 (LOCK 매핑/값 불일치 문제이지 경로 문제 아님). C-04: A-2a/A-2b 경로 무관, C-05: D-7/D-10 경로 무관, C-06: C-2 경로 무관, C-07: B-2 경로 무관, C-08: C-1 경로 무관

**산출물**:
- 경로 검증 결과 리포트 — **완료 (2026-04-03)**:
  - **PASS 14건** (서브폴더 수준 확인 — §A.1에 파일명 미특정된 항목): #6 PKM 8건(서브폴더 4개 전수 존재: `03_spaced-repetition/`, `01_knowledge-capture/`, `06_zettelkasten/`, `02_knowledge-graph/`) + #8 Education 2건(`02_spaced-repetition/`, `05_learning-analytics/`) + #17 MLOps 1건(`01_prompt-versioning/`) + #10 Dev-Tools 1건(`01_coding-engine/`) + #12 Business 1건(`02_market-analysis/`) + #7 Workflow 1건(`01_dag-engine/`). 참고: 14건 전부 서브폴더 내 `_index.md`만 존재, 개별 콘텐츠 파일은 미생성 상태 — V-06 파일 수준 확인 시 추가 검증 필요
  - **CONDITIONAL PASS 3건** (최상위 폴더 존재, 서브폴더 미특정): #11 A2A 1건(B-2: `3-8_Conversation-A2A/` 존재, 서브폴더 5개 확인되나 §A.1 매핑 미특정) + Ai-investing 2건(C-1/C-2: `Ai-investing-detail/` 존재, 관련 콘텐츠 파일 확인됨 — C-1→`portfolio_optimization.md`, C-2→`factor.md`)
  - **FAIL 7건** (파일 수준 미존재 — §6.1에 파일명 특정된 항목): #9 Health-Wellness 7건(A-1a~c, A-2a~b, A-3a/b). 서브폴더 `04_stress-management/`(6건), `06_ethics-privacy/`(1건) 존재하나 개별 정본 파일 6개 고유 파일 미생성: `breathing_exercises.md`(A-1a), `grounding_technique.md`(A-1b), `mindfulness_meditation.md`(A-1c), `cbt_self_care.md`(A-2a), `cbt_distortion_taxonomy.md`(A-2b), `burnout_prevention.md`(A-3a+A-3b 공유). Glob 유사 파일명 검색 0건 — 도메인이 서브폴더 구조만 생성한 상태
  - P0-2 교차 대조: 24/24 전수 일치, 정정 0건
  - CONFLICT_LOG 경로 영향: C-04~C-08 5건 전부 경로 영향 없음
  - **V-06 게이트 영향 분석** (Phase 1→2 전환 게이트 "24건 중 90% 이상 도메인 정본 파일 링크 유효 확인" 사전 평가):
    - 현재 확정 PASS율: 14/24 = 58.3% (V-06 기준 미달)
    - #9 FAIL 7건 해소 시: 21/24 = 87.5% (여전히 90% 미달)
    - CONDITIONAL 3건 중 1건 이상 추가 해소 시: 22/24 = 91.7% (**V-06 게이트 통과 최소 조건**)
    - 전건 해소 시: 24/24 = 100%
    - **Phase 1 진입 최소 요건**: #9 Health-Wellness 도메인 정본 파일 6개 생성 + CONDITIONAL 3건(B-2, C-1, C-2) 중 최소 1건 서브폴더 특정·확인
    - 참고: PASS 14건은 서브폴더 수준 확인이며 V-06 파일 수준 확인 시 추가 FAIL 가능성 있음 — Phase 1에서 24건 전수 파일 수준 재확인 권장
- P0-2 인덱스 파일 정정 건 — 해당 없음 (교차 대조 불일치 0건)
- CONFLICT_LOG 갱신 건 — 해당 없음. 사유: FAIL 7건은 §9.1 충돌 유형(소유권 충돌/값 충돌/매핑 충돌) 어디에도 해당하지 않음 — v12 인덱스의 경로 매핑(§6.1, §A.1)은 유효하나 대상 도메인(#9)이 해당 정본 파일을 아직 생성하지 않은 상태. CONDITIONAL 3건도 §A.1 "추정 경로"의 서브폴더 미특정이지 충돌이 아님. Phase 1 진행 시 #9 도메인 파일 생성 확인 및 CONDITIONAL 3건 서브폴더 특정이 선행 조건
</details>

#### Phase 1 단계별 상세 작업 절차

<details>
<summary><b>P1-1. 24건 확정 항목 도메인 정본 파일 링크 유효 확인</b></summary>

**대조 기준**: §7.2 Phase 1→2 게이트 "24건 중 90% 이상 도메인 정본 파일 링크 유효 확인" + §10.2 V-06 + §6.1~§6.4 이슈 해결 매핑 정본 경로

**목표**: P0-4에서 서브폴더/최상위 수준으로 검증된 24건을 **파일 수준**으로 전수 재확인하여, 90% 이상(22건 이상) 유효 링크를 확보하고 Phase 1→2 전환 게이트를 통과한다.

**전제 조건**:
- Phase 0 완료 필수 (P0-1~P0-4 전수 완료, §7.2 Phase 0→1 게이트 "6개 _index.md 생성 + 24건 인덱스 파일 작성 완료" 통과)
- P0-4 산출물 활용: 14 PASS + 3 CONDITIONAL PASS + 7 FAIL 분류 결과를 기초 데이터로 사용
- P0-3 CONFLICT_LOG C-04~C-08 OPEN 5건: 경로 영향 없음 기확인 (P0-4 절차 5). LOCK 값 불일치 건이며 링크 유효성과 무관

**입력 파일**:
- P0-4 산출물 (경로 검증 결과 리포트 — 24건 PASS/CONDITIONAL/FAIL 분류 + V-06 게이트 영향 분석)
- P0-2 산출물 (24개 인덱스 파일의 "정본 폴더"/"정본 파일" 기입값)
- 본 계획서 §6.1~§6.4 (이슈 해결 매핑 — 항목별 정본 경로 정본값)
- 본 계획서 부록 §A.1 (도메인별 정본 연결 마스터 테이블 — 24건 "정본 파일 (추정 경로)" 칼럼)
- 본 계획서 §3.4 + §A.4 (LOCK 보호 선언 — LOCK-V12-01~10 상속 매핑, 경로 변경 시 LOCK 영향 교차 확인용)
- 각 도메인 sot 2/ 정본 폴더 실제 파일 시스템 (Glob/Read로 직접 확인)

**적용 거버넌스 규칙**:
- R-19-1: 검증 결과에 구현 상세 기술 금지 — 경로 존재/부존재 사실 + 유효/무효 판정만 기록
- R-19-2: 경로 불일치 발견 시 양방향 정합성 유지 — 인덱스 파일 정정 + 도메인 폴더 확인 동시 수행
- R8: 분기별 정합성 검사의 첫 실행 인스턴스로서, 향후 검사의 베이스라인 제공
- §9.2 충돌 해결 우선순위: 경로 불일치 시 "3순위: 도메인 정본 → 해당 도메인 sot 2/ 계획서 정의 우선" 적용

**절차**:
1. P0-4 결과를 기초로 24건을 3개 그룹으로 분류하여 **파일 수준** 검증 수행:

   **그룹 A — P0-4 FAIL 7건 (우선 처리: #9 Health-Wellness)**:
   - 대상: A-1a(`breathing_exercises.md`), A-1b(`grounding_technique.md`), A-1c(`mindfulness_meditation.md`), A-2a(`cbt_self_care.md`), A-2b(`cbt_distortion_taxonomy.md`), A-3a/A-3b(`burnout_prevention.md` 공유)
   - 확인 방법:
     a. `D:\VAMOS\docs\sot 2\3-6_Health-Wellness-EmotionAI\04_stress-management\` 내 파일 Glob 전수 확인
     b. `D:\VAMOS\docs\sot 2\3-6_Health-Wellness-EmotionAI\06_ethics-privacy\` 내 파일 Glob 전수 확인
     c. §6.1 정본 경로 파일명과 실제 파일명 대조 (정확히 일치 / 유사 파일명 존재 / 완전 부재 3단계 분류)
   - 미존재 시: #9 Health-Wellness 도메인 Phase 진행 상태 확인 → 정본 파일 생성 시점 확인 → 미생성 건은 "(미생성 — #9 Phase 진행 대기)" 표기
   - 판정: 파일 존재 = VALID, 유사 파일명 = VALID(정정 필요), 완전 부재 = INVALID

   **그룹 B — P0-4 CONDITIONAL PASS 3건 (서브폴더 특정 필요)**:
   - B-2 (TemplateSets → #11 A2A): `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\` 하위 전수 Glob → TemplateSet 관련 파일/폴더 식별 → §A.1 "에이전트 대화 패턴 폴더" 매핑 특정
   - C-1 (Black-Litterman → Ai-investing): P0-4에서 `15_portfolio-advanced/portfolio_optimization.md` 확인됨 → 파일 Read로 Black-Litterman 관련 내용 포함 확인 → 유효 시 §A.1 추정 경로를 실제 경로로 확정·정정
   - C-2 (Factor Investing → Ai-investing): P0-4에서 `20_strategy-detail/quant/factor.md` 확인됨 → 파일 Read로 Factor Investing 관련 내용 포함 확인 → 유효 시 §A.1 추정 경로를 실제 경로로 확정·정정
   - 판정: 관련 파일 존재 + 내용 확인 = VALID, 파일 존재하나 내용 무관 = INVALID, 파일 미존재 = INVALID

   **그룹 C — P0-4 PASS 14건 (파일 수준 재확인)**:
   - P0-4에서 서브폴더 존재만 확인된 14건을 파일 수준으로 승격 검증
   - 대상 도메인별 서브폴더 Glob으로 실제 파일 목록 확인:
     - #6 PKM 8건: `03_spaced-repetition/`(A-4b), `01_knowledge-capture/`(D-1,2,4,6), `06_zettelkasten/`(D-7,10), `02_knowledge-graph/`(D-8)
     - #8 Education 2건: `02_spaced-repetition/`(A-4a), `05_learning-analytics/`(A-4c)
     - #17 MLOps 1건: `01_prompt-versioning/`(B-1)
     - #10 Dev-Tools 1건: `01_coding-engine/`(D-3)
     - #12 Business 1건: `02_market-analysis/`(D-5)
     - #7 Workflow 1건: `01_dag-engine/`(D-9)
   - §A.1 "정본 파일 (추정 경로)"에 파일명이 기재된 항목: 해당 파일 존재 확인
   - §A.1에 서브폴더까지만 기재된 항목: 서브폴더 내 관련 파일 존재 + _index.md 등록 여부 확인 → 존재 시 VALID(구체 경로 확정), 서브폴더 비어 있으면 CONDITIONAL(콘텐츠 미생성)
   - 판정: 파일 존재 = VALID, 서브폴더만 존재(파일 미생성) = CONDITIONAL, 서브폴더 미존재 = INVALID

2. 24건 전수 판정 결과 집계 및 게이트 평가:
   - VALID 건수 / 24건 산출 → 90% (22건) 이상 여부 확인
   - CONDITIONAL 건은 게이트 산정 시 제외 (VALID만 산정) 또는 건별 판정 근거 명시
   - 90% 미달 시: 미달 원인 분석 + 해소 방안(도메인 파일 생성 요청, 경로 정정 등) 기록 → Phase 1→2 전환 보류

3. 인덱스 파일 정정 (경로 변경 발견 건):
   - CONDITIONAL→VALID 전환 건(B-2, C-1, C-2 등): P0-2 인덱스 파일의 "정본 폴더"/"정본 파일" 값을 실제 확인된 경로로 정정
   - 유사 파일명 건: §6 + §A.1 + P0-2 인덱스 파일 3곳 동시 정정 (R-19-2)
   - 정정 시 LOCK 상속에 영향 없음 확인 (§A.4 교차 확인 — 경로 변경이 LOCK 값 변경을 수반하지 않는지)

4. 부록 §A.1 마스터 테이블 갱신:
   - 검증 결과 반영: "상태" 칼럼에 VALID/CONDITIONAL/INVALID 기입
   - CONDITIONAL→VALID 전환 건: "정본 파일 (추정 경로)" 칼럼을 실제 확정 경로로 갱신
   - §7.3 종속 도메인 Phase 현황 추적 테이블 갱신: 각 도메인의 현재 Phase 상태 반영

5. CONFLICT_LOG 갱신 (필요 시):
   - 경로 불일치(§6/§A.1 정본값 ≠ 실제 파일 시스템): CONFLICT_LOG에 OPEN 등록 (§9.1 "매핑 충돌" 유형)
   - P0-3 C-04~C-08 OPEN 건: 경로 영향 재확인 (P0-4에서 영향 없음 확인되었으나, 파일 수준 검증에서 추가 발견 시 갱신)

**검증**:
- [x] 24건 전수 **파일 수준** 링크 유효성 판정 완료 (VALID / CONDITIONAL / INVALID 분류) ✅ — VALID 23건 + CONDITIONAL 1건 (B-2)
- [x] VALID 건수 ≥ 22건 (90% 이상) — Phase 1→2 전환 게이트 조건 충족 (§7.2) ✅ — 23/24 = 95.8%
- [x] 그룹 A (#9 Health-Wellness 7건): 파일 존재 여부 확인 ✅ — 7/7 전수 VALID. breathing_exercises.md, grounding_technique.md, mindfulness_meditation.md, cbt_self_care.md, cbt_distortion_taxonomy.md, burnout_prevention.md(A-3a/A-3b 공유) 전부 존재
- [x] 그룹 B (CONDITIONAL 3건: B-2, C-1, C-2): 서브폴더 특정 + 파일 수준 확인 ✅ — C-1→VALID(`15_portfolio-advanced/portfolio_optimization.md` Black-Litterman 포함 확인), C-2→VALID(`20_strategy-detail/quant/factor.md` Factor Investing 포함 확인), B-2→CONDITIONAL(A2A 내 TemplateSet 전용 파일 미존재, 도메인 관련 콘텐츠 간접 참조만)
- [x] 그룹 C (PASS 14건): 서브폴더→파일 수준 승격 검증 완료 ✅ — 14/14 전수 VALID. 각 서브폴더에 _index.md + 관련 콘텐츠 파일 다수 존재 확인
- [x] 경로 정정 건: P0-2 인덱스 파일 + §A.1 동시 정정 (R-19-2) + LOCK 영향 없음 확인 ✅ — C-1: §A.1 "(포트폴리오 최적화 폴더)"→`15_portfolio-advanced/portfolio_optimization.md`, C-2: §A.1 "(팩터 투자 폴더)"→`20_strategy-detail/quant/factor.md`. LOCK 값 변경 없음 (경로만 특정)
- [x] 부록 §A.1 마스터 테이블 정본 파일 경로 갱신 완료 ✅ — C-1, C-2 실제 경로 확정 반영
- [x] §7.3 종속 도메인 Phase 현황 추적 테이블 갱신 완료 ✅ — 7개 도메인 Phase 상태 갱신 (2026-04-12)

> **완료**: 2026-04-12. 24건 확정 항목 파일 수준 전수 검증 완료 — VALID 23건(95.8%), Phase 1→2 게이트 통과.
>
> **실행 결과 요약**:
> - 24건 전수 파일 수준 판정 완료: VALID 23건 + CONDITIONAL 1건(B-2 TemplateSets)
> - 그룹 A(#9 Health-Wellness 7건) 전수 VALID, 그룹 B C-1/C-2 VALID 전환 + B-2 CONDITIONAL 유지, 그룹 C 14/14 VALID
> - C-1/C-2 경로 확정: §A.1 추정 경로 → 실제 경로 정정 (`portfolio_optimization.md`, `factor.md`), LOCK 영향 없음
> - §A.1 마스터 테이블 + §7.3 종속 도메인 Phase 현황 테이블 갱신 완료
> - 이월: B-2 TemplateSets (#11 A2A) 전용 파일 미존재 — Phase 2 귀속 확정 시 처리

**[P1-1] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: Phase 1 정합성 체크 리포트 1건 (24건 전수 파일 수준 VALID/CONDITIONAL/INVALID 분류 + 게이트 평가 + 정정 이력), §A.1 경로 정정 2건(C-1, C-2), §7.3 테이블 갱신
- 1. 게이트: G1→2 ✅ — 23/24 = 95.8% ≥ 90% (§7.2 Phase 1→2 전환 게이트 통과)
- 2. CONFLICT: 신규 발견 0건 / 신규 해소 0건 / 누적 OPEN 5건 (C-04~C-08 지속). 해당 5건은 LOCK 값 불일치 건으로 경로 영향 없음 재확인
- 3. LOCK 변경: 없음. LOCK-V12-01~10 변경 0건, C-1/C-2 경로 확정은 LOCK 값 변경 미수반
- 4. 이월: B-2 TemplateSets CONDITIONAL 1건 → Phase 2(P2-1) 27건 잠정 항목 귀속 확정 시 함께 처리

**산출물**: Phase 1 정합성 체크 리포트 (24건 전수 파일 수준 VALID/CONDITIONAL/INVALID 분류 + 게이트 평가 + 정정 이력) — **완료 (2026-04-12)**
</details>

#### Phase 2 단계별 상세 작업 절차

<details>
<summary><b>P2-1. V2/V3 27건 잠정 항목 도메인 귀속 확정</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 2 "V2/V3 항목 귀속 확정" (27건 잠정 항목 도메인 귀속 최종 확정 + 인덱스 이동)
- §7 전환 게이트: Phase 2→3 = 27건 잠정 항목 중 70% 이상 도메인 귀속 확정
- §6 이슈: P-3 (의존성 미정의 — Phase 2 해결)
- 교차 도메인: 해당 없음 (단, 18개 대상 도메인 계획서 완성 상태 종속)
- Part2 버전: V2-Phase 2~3 + V3-Phase 2~3 (§6.5~6.7 항목 전체)

**목표**: 27건 잠정(§6.5 E-1~E-15, §6.6 F-1~F-6, §6.7 G-1~G-6) 항목의 도메인 귀속을 최종 확정하고, 확정된 항목의 인덱스 파일을 해당 서브폴더로 이동. 70% 이상(19건+) 귀속 확정 달성.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\5-3_v12-Additions-Detail\V12_ADDITIONS_DETAIL_구조화_종합계획서.md` §6.5~6.7 (27건 잠정 항목 목록 + 도메인 매핑)
- `D:\VAMOS\docs\sot 2\5-3_v12-Additions-Detail\V12_ADDITIONS_상세명세.md` §A~§G (기술 명세 참조)
- 본 계획서 부록 §A (도메인별 정본 연결 마스터 테이블)
- 각 대상 도메인 계획서 (18개 도메인 sot 2/ 종합계획서)

**절차**:
1. §6.5~6.7 27건 잠정 항목 전수 목록 확인 (E-1~E-15, F-1~F-6, G-1~G-6)
2. 각 항목의 매핑 대상 도메인 계획서 Phase 상태 확인 (계획서 완성 여부)
3. 도메인 계획서가 완성된 항목: 해당 도메인 정본 폴더에 항목 존재/생성 가능 여부 판정
4. 귀속 확정 판정:
   a. CONFIRMED: 도메인 계획서 완성 + 정본 폴더 내 매핑 파일/섹션 명확
   b. CONDITIONAL: 도메인 계획서 완성 + 정본 폴더 내 위치 결정 필요
   c. DEFERRED: 도메인 계획서 미완성 → Part2 로드맵 대기
5. CONFIRMED 항목: 06_v2-v3-advanced/_index.md에서 해당 도메인 참조 경로 확정 기재
6. §A 부록에 의존성 그래프 작성 (P-3 이슈 해결): 항목 간 선후 관계 + 도메인 종속성
7. §7.3 종속 도메인 Phase 현황 추적 테이블 갱신
8. LOCK-V12-10 (도메인 정본 연결 매핑) 부록 §A 반영 갱신

**검증**:
- [ ] 27건 전수 판정 완료 (CONFIRMED + CONDITIONAL + DEFERRED = 27)
- [ ] CONFIRMED ≥ 19건 (70% 이상) — CONDITIONAL은 별도 2차 지표로 추적(게이트 산정 제외)
- [ ] 06_v2-v3-advanced/_index.md에 확정 항목 전수 경로 기재
- [ ] §A 부록 의존성 그래프 작성 완료 (P-3 해결)
- [ ] §7.3 테이블 갱신 완료
- [ ] LOCK-V12-10 부록 §A 정합 확인

**산출물**:
- `D:\VAMOS\docs\sot 2\5-3_v12-Additions-Detail\06_v2-v3-advanced\_index.md` (27건 귀속 판정 결과 + 확정 경로)
- 본 계획서 §A 부록 (의존성 그래프 추가)
- 본 계획서 §7.3 (종속 도메인 현황 갱신)
</details>

### 7.3 종속 도메인 Phase 현황 추적

| 대상 도메인 | 현재 Phase | v12 항목 실행 가능 여부 | 비고 |
|-----------|-----------|---------------------|------|
| #6 PKM | Phase 1 완료 (Phase 2 진입 가능) | 항목 8건 실행 가능 | A-4b, D-1,2,4,6,7,8,10 |
| #7 Workflow | 확인 필요 | 항목 1건 대기 | D-9 |
| #8 Education | 확인 필요 | 항목 2건 대기 | A-4a, A-4c |
| #9 Health-Wellness | Phase 1 완료 (Phase 2 진입 가능) | 항목 7건 실행 가능 | A-1,2,3 |
| #10 Dev-Tools | Phase 1 완료 (Phase 2 진입 가능) | 항목 1건 실행 가능 | D-3 |
| #11 Conversation-A2A | Phase 1 완료 (Phase 2 진입 가능) | 항목 1건 대기 (CONDITIONAL — B-2 전용 파일 미존재, Phase 2 귀속 확정 시 처리) | B-2 |
| #12 Business | Phase 1 완료 (Phase 2 진입 가능) | 항목 1건 실행 가능 | D-5 |
| #17 MLOps | Phase 1 완료 (Phase 2 진입 가능) | 항목 1건 실행 가능 | B-1 |
| AI Investing | 완성 | 항목 2건 즉시 가능 | C-1,2 |

---

## 8. 파일 역할 분리 명세

| 파일/폴더 | 역할 | 내용 범위 | 갱신 주기 | 삭제 가능 |
|----------|------|----------|----------|----------|
| **V12_ADDITIONS_DETAIL_구조화_종합계획서.md** | 마스터 플랜 | 14+1섹션 구조화 계획 | 주요 변경 시 | 불가 |
| **V12_ADDITIONS_상세명세.md** | 레거시 기술 명세 | 7개 섹션, 535줄 기술 상세 | 갱신 없음 (참조 전용) | 불가 (삭제 금지) |
| **AUTHORITY_CHAIN.md** | 권한 체계 선언 | LOCK 10건 + 변경 이력 | LOCK 변경 시 | 불가 |
| **CONFLICT_LOG.md** | 충돌 기록 | 도메인 간 충돌 해결 기록 | 충돌 발견 시 | 불가 |
| **XX_*/_index.md** (6개) | 서브폴더 인덱스 | 항목 목록 + 상태 + 도메인 링크 | 월 1회 | 가능 (폴더 재구성 시) |
| **개별 항목 인덱스 파일** (~30개) | 항목별 인덱스 | 1-page 요약 + 도메인 정본 링크 | 도메인 변경 시 | 가능 (항목 삭제 시) |

### 역할 경계 명확화

| 질문 | 답변 | 근거 |
|------|------|------|
| SM-2 알고리즘 상세는 어디에? | `3-3_PKM.../03_spaced-repetition/` (정본) | R-19-1 |
| Black-Litterman 수학 공식은? | `Ai-investing-detail/` (정본) | R-19-1 |
| CBT 인지 왜곡 15유형 목록은? | `3-6_Health.../06_ethics-privacy/cbt_distortion_taxonomy.md` (정본) | R-19-1 |
| v12 전체 진행 현황은? | 본 폴더 `_index.md` 6개 (인덱스 허브) | 허브 역할 |
| 도메인 간 충돌은? | 본 폴더 `CONFLICT_LOG.md` | 중재 역할 |

---

## 9. 충돌 해결 프로토콜

### 9.1 충돌 유형

| 유형 | 설명 | 해결 원칙 |
|------|------|----------|
| **소유권 충돌** | 동일 v12 항목을 2개 이상 도메인이 정본 주장 | 기능의 핵심 속성(알고리즘/데이터/UI) 기준 판정 |
| **값 충돌** | 동일 파라미터가 상세명세와 도메인 정본에서 다른 값 | 도메인 LOCK 우선 (상세명세는 레거시 참조) |
| **매핑 충돌** | 동일 항목이 2개 서브폴더에 중복 등록 | 주 소유 도메인 기준 1개 서브폴더만 유지 |

### 9.2 충돌 해결 우선순위

```
1. LOCK 보호 값 → 해당 도메인 LOCK 값 우선 (변경 불가)
2. DESIGN 문서 → Part2/D2.0 정의 우선
3. 도메인 정본 → 해당 도메인 sot 2/ 계획서 정의 우선
4. 상세명세 → 레거시 참조 (가장 낮은 우선순위)
5. 시간순 → 최신 결정 우선 (동일 레벨 충돌 시)
```

### 9.3 현재 충돌 기록 요약

> 상세: CONFLICT_LOG.md 참조

| # | 충돌 내용 | 상태 | 판정 요약 |
|---|----------|------|----------|
| C-01 | SM2ReviewEngine: #6 PKM vs #8 Education | RESOLVED | PKM이 알고리즘 정본, Education은 UI 참조 |
| C-02 | Prompt Registry: #17 MLOps vs Agent Teams | RESOLVED | MLOps가 프롬프트 관리 정본, Agent Teams는 에이전트 전용 인터페이스 |
| C-03 | Zettelkasten D-7/D-10: #6 PKM vs Cloud Library | RESOLVED | PKM이 정본, Cloud Library/v12는 UI 확장만 |

### 9.4 횡단 관심사 참조 *(S7-2 추가)*

| 횡단 도메인 | 적용 내용 |
|-----------|----------|
| 0-0 Governance-Rules-Meta | R1~R11 공통 규칙 준수 (R-19-1: v12 항목 도메인 LOCK 상속) |

---

## 10. 검증 체크리스트

### 10.1 Phase 0 완료 검증

| # | 검증 항목 | 기준 | 상태 |
|---|----------|------|------|
| V-01 | 6개 서브폴더 _index.md 존재 | 6/6 존재 | DONE (2026-04-02) — 6/6 ✅, 51건 전수 등록, §A 대조 완료 |
| V-02 | 24건 확정 항목 인덱스 파일 존재 | 24/24 존재 | DONE (2026-04-02) — 24/24 ✅, 서브폴더별 01=7, 02=3, 03=2, 04=2, 05=10 |
| V-03 | 각 인덱스 파일에 도메인 정본 링크 포함 | 24/24 링크 유효 | DONE (2026-04-02) — §6+§A.1 대조 완료, LOCK 11건 기입, 공유 2건+횡단 1건 명시 |
| V-04 | AUTHORITY_CHAIN.md 10개 LOCK 등록 | 10/10 등록 | DONE (2026-04-03) — 10/10 기등록 확인 + P0-3 검증 이력 추가. 5건 CONFLICT_LOG(C-04~C-08) OPEN |
| V-05 | CONFLICT_LOG.md 기존 3건 RESOLVED | 3/3 RESOLVED | DONE (2026-04-03) — C-01~C-03 3/3 RESOLVED 확인. P0-3에서 C-04~C-08 OPEN 5건 신규 추가 (→ §10.4 V-13 대응) |
| V-05b | 24건 도메인 정본 경로 검증 (P0-4) | 24건 서브폴더 이상 존재 | DONE (2026-04-03) — 14 PASS(서브폴더 수준) + 3 CONDITIONAL PASS(최상위 폴더, 서브폴더 미특정: B-2,C-1,C-2) + 7 FAIL(파일 수준 미존재: #9 Health-Wellness A-1a~c,A-2a~b,A-3a/b). P0-2 교차 대조 24/24 일치. V-06 사전 데이터: 현재 58.3% → #9+COND 1건 해소 시 91.7% |

### 10.2 Phase 1 완료 검증

| # | 검증 항목 | 기준 | 상태 |
|---|----------|------|------|
| V-06 | 24건 정본 파일 실제 존재 확인 | 90% 이상 존재 | ✅ DONE (2026-04-12) — 23/24 VALID + 1 CONDITIONAL(B-2) = 95.8% ≥ 90%. Phase 1→2 게이트 통과 |
| V-07 | LOCK 상속 값 정합성 (상세명세 vs 도메인 LOCK) | 10/10 일치 | ✅ DONE (2026-04-12) — LOCK-V12-01~10 변경 0건. C-04~C-08 OPEN 5건은 LOCK 값 불일치 건으로 경로 영향 없음 재확인 |
| V-08 | Part2 산재 항목 전수 커버리지 | §6.1 + §6.7 + §6.8 + §6.10 100% 매핑 | ✅ DONE (2026-04-12) — 24건 전수 파일 수준 검증 완료, §A.1 마스터 테이블 경로 정정 2건(C-1, C-2) 반영 |

### 10.3 Phase 2 완료 검증

| # | 검증 항목 | 기준 | 상태 |
|---|----------|------|------|
| V-09 | V2/V3 27건 도메인 귀속 확정률 | 70% 이상 | TODO |
| V-10 | 확정된 항목의 도메인 폴더 동시 등록 확인 (R-19-2) | 100% 동시 등록 | TODO |

### 10.4 전체 검증

| # | 검증 항목 | 기준 | 상태 |
|---|----------|------|------|
| V-11 | R-19-1 준수: 구현 상세가 인덱스 파일에 없음 | 인덱스 파일 각각 < 50줄 | TODO |
| V-12 | R-19-3 준수: 삭제 항목 = 0건 (초기) | 고아 항목 0건 | TODO |
| V-13 | CONFLICT_LOG OPEN 건수 | 0건 | TODO |

---

## 11. 보완 사항

> S8-4 및 S10-3 QC 과정에서 발견된 보완 사항 기록. P0-3 검증(2026-04-03)에서 추가 발견 사항 반영.

| # | 발견 사항 | 심각도 | 조치 | 상태 |
|---|----------|--------|------|------|
| S-1 | 51건 확정 항목 전수 도메인 귀속 검증 완료 — 각 항목이 정확한 SOT 2 도메인 폴더에 매핑되었는지 전수 확인 | LOW | S8-4 검증 | DONE |
| S-2 | 8건 LOCK 상속 전수 일치 확인 — 상세명세 내 LOCK 값이 해당 도메인 정본의 LOCK 값과 글자 그대로 일치하는지 전수 대조 | LOW | S8-4 검증 | **SUPERSEDED** — P0-3에서 도메인 정본 LOCK과 직접 대조 시 2건 FAIL(V12-05, V12-09), 3건 CONDITIONAL(V12-03, V12-07, V12-08) 발견. S8-4는 상세명세 기준 대조였으나 P0-3은 도메인 계획서 LOCK 기준 대조. CONFLICT_LOG C-04~C-08 참조 |
| S-3 | V2/V3 27건 잠정 항목 도메인 귀속 미확정 — 섹션 E/F/G의 27건이 잠정 매핑 상태로 Phase 2 진입 시 최종 확정 필요 | MEDIUM | Phase 2 진입 시 확정 | OPEN |
| S-4 | §1.5 핵심 문제 기술 깊이 보강 — 각 문제 항목에 구체적 영향 범위와 해결 경과를 추가 기술 | LOW | S10-3 보강 | DONE |
| S-5 | LOCK-V12-05 상속 매핑 부정확 — §A.4에서 LOCK-HW-09(감정 AI 7원칙)를 상속 원본으로 매핑하나, LOCK-HW-09는 CBT 15유형이 아닌 윤리 원칙. CBT 15유형 전용 LOCK이 #9 Health-Wellness에 부재 | HIGH | #9 도메인에 CBT 전용 LOCK 신규 부여 요청 후 §3.4/§A.4/AUTHORITY_CHAIN 정정 | ✅ RESOLVED (2026-06-11, D1) — 상속 출처 '부록 §C(LOCK 미부여)' 정정 + 정본 15종 전사 완료, LOCK-HW-13 신설안 기각 (C-04) |
| S-6 | LOCK-V12-09 Zettelkasten 링크 타입 불일치 — V12 "4종(RELATED_TO, SUPPORTS, CONTRADICTS, SUPERSEDES)" vs PKM 부록 §A.3 "5종(related, supports, contradicts, continues, branches)". 개수·명칭 모두 불일치 | HIGH | #6 PKM 도메인에서 링크 타입 LOCK 여부 확인 후 §3.4/§A.4/AUTHORITY_CHAIN 정정 | ✅ RESOLVED (2026-06-11, D2) — C-05: PKM 정본 5종 채택, §3.4/§A.4/AUTHORITY_CHAIN 정정 완료 |
| S-7 | LOCK-V12-08 AUTHORITY_CHAIN 현금 비중 초과 기재 — §3.4/§A.4에 없는 "현금 비중 최소 5%"가 AUTHORITY_CHAIN에 기재, 도메인 값(20%)과도 불일치 | MEDIUM | AUTHORITY_CHAIN에서 현금 비중 삭제 또는 도메인 값(20%)으로 정정 | ✅ RESOLVED (2026-06-11) — C-06: 현행 AUTHORITY_CHAIN에 현금 비중 기재 부재(권고 기이행) + 5%/20% 맥락 구분(20%=SPEC §10.2 LOCK 안전장치, 5%=cash_allocation.md 운영 목표, LOCK-V12-08 범위 밖 유지) |
| S-8 | LOCK-V12-07 TS 3종 도메인 전용 LOCK 부재 — A2A/MLOps 양쪽 도메인 모두 TS_CORE/TS_WEB_RESEARCH/TS_CODE 전용 LOCK 미등록 | MEDIUM | A2A 또는 MLOps 도메인에서 TS 전용 LOCK 생성 권장 | ✅ RESOLVED (2026-06-11, D4) — 전용 LOCK은 D2.0-03 §4.2 + 2-1 LOCK-BN-18로 기존재, 신설 불요. LOCK-V12-07 상속 출처 정정으로 해결 — C-07 RESOLVED |
| S-9 | P0-4 경로 검증: #9 Health-Wellness 정본 파일 7건(6개 고유 파일) 미생성 — 서브폴더(`04_stress-management/`, `06_ethics-privacy/`) 존재하나 `breathing_exercises.md` 등 6개 정본 파일 미생성. V-06 게이트(90%) 충족을 위해 #9 도메인 파일 생성 필수 | MEDIUM | Phase 1 진입 시 #9 도메인 파일 생성 확인 선행. CONFLICT_LOG 불요(§9.1 충돌 비해당) | ✅ RESOLVED (2026-04-12) — P1-1 검증에서 7/7 전수 VALID 확인 |
| S-10 | P0-4 경로 검증: CONDITIONAL PASS 3건(B-2, C-1, C-2) 서브폴더 미특정 — §A.1에 괄호 설명만 기재, 구체적 서브폴더 미매핑. Ai-investing 내 관련 파일(`portfolio_optimization.md`, `factor.md`) 존재 확인됨 | LOW | Phase 1에서 정확한 서브폴더 경로 특정 후 §A.1 갱신 | ✅ RESOLVED (2026-04-12) — C-1→VALID, C-2→VALID, B-2→CONDITIONAL 유지(Phase 2 귀속 확정 시 처리) |

---

## 12. FINAL REVIEW 결과

> **상태**: APPROVED — Phase 8 QC B+ (2026-03-26), Phase 10 QC A- (2026-03-27), P0-3 LOCK 검증 (2026-04-03), P0-4 경로 검증 (2026-04-03), Phase 1 완료 (2026-04-12)

| 항목 | 결과 | 비고 |
|------|------|------|
| **전체 판정** | **CONDITIONAL PASS** | V2/V3 잠정 항목 Phase 2 확정 대기 (S-3) + LOCK 불일치 5건 OPEN (S-5~S-8). 정본 경로 S-9/S-10 RESOLVED (2026-04-12, P1-1 23/24 VALID) |
| **51건 확정 매핑** | PASS | 전수 도메인 귀속 검증 완료 (S8-4) |
| **LOCK 상속 8건** | **CONDITIONAL** | P0-3 도메인 정본 직접 대조 결과: 3건 PASS(V12-02,04,06), 3건 CONDITIONAL(V12-03,07,08), 2건 FAIL(V12-05,09). S8-4 "전수 일치" 판정을 SUPERSEDE. CONFLICT_LOG C-04~C-08 OPEN |
| **정본 경로 24건** | **PASS** | P1-1 검증 완료 (2026-04-12): 23 VALID + 1 CONDITIONAL(B-2) = 95.8%. C-1/C-2 경로 확정. S-9 RESOLVED(#9 7건 VALID), S-10 RESOLVED(C-1→VALID, C-2→VALID, B-2→CONDITIONAL 유지) |
| **도메인 귀속 원칙** | PASS | LOCK-V12-01 작동 확인 — v12 항목의 LOCK 값은 해당 도메인 정본에서만 변경 가능 |
| **부록 §A 매핑 테이블** | PASS | 24건 확정 + 27건 잠정 = 51건 전수 추적 가능 |
| **Gate 판정** | **CONDITIONAL PASS** | Phase 0/1 완료 (P0-1~P0-4 + P1-1 DONE). Phase 1→2 게이트 PASS (23/24=95.8%). V2/V3 27건 Phase 2 확정 대기. LOCK 불일치 5건 해당 도메인 조치 대기. |
| **리뷰 이력** | S8-4 → S10-3 → P0-3 → P0-4 → P1-1 | B+ → A- → P0-3 LOCK 검증 → P0-4 경로 검증 → P1-1 파일 수준 전수 검증 (§11 S-9/S-10 RESOLVED) |
| **리뷰일** | 2026-04-12 | P1-1 24건 파일 수준 전수 검증 완료 (Phase 1→2 게이트 PASS) |

---

## 13. L3 전수 승급 계획 (간소화)

> **Tier 5 간소화 적용**: 이 도메인은 인덱스 허브이므로, L3 개별 승급을 수행하지 않는다. 각 v12 항목의 L3 상태는 해당 도메인 정본 폴더의 L3 상태를 참조한다.

### 13.1 L3 상태 참조 체계

| 서브폴더 | 항목 수 | L3 참조 도메인 | 참조 방법 |
|---------|--------|--------------|----------|
| `01_wellness-ui/` | 7건 | #9 Health-Wellness §13 | 해당 계획서 L3 매트릭스 참조 |
| `02_learning-tools/` | 3건 | #8 Education §13 + #6 PKM §13 | 각 도메인 계획서 L3 참조 |
| `03_agent-teams/` | 2건 | #17 MLOps §13 + #11 A2A §13 | 각 도메인 계획서 L3 참조 |
| `04_investing-additions/` | 2건 | AI Investing (완성 모델) | 이미 L3 완료 추정 |
| `05_cloud-library/` | 10건 | #6 PKM §13 (7건) + #10/#12/#7 §13 (3건) | 각 도메인 계획서 L3 참조 |
| `06_v2-v3-advanced/` | ~27건 | 도메인 미확정 | 귀속 확정 후 참조 |

### 13.2 L3 상태 갱신 주기

- **월 1회**: 각 도메인의 L3 상태를 확인하여 인덱스 _index.md에 반영
- **갱신 담당**: Phase 3 정례화 프로세스의 일부로 실행
- **갱신 범위**: 인덱스 파일 내 `status` 필드만 갱신 (구현 상세 작성 금지)

---

## 14. 실행 약점 대응 계획 (간소화)

> **Tier 5 간소화 적용**: 주요 리스크만 식별하고 대응 방안을 기술한다.

### 14.1 주요 리스크

| # | 리스크 | 영향도 | 발생 가능성 | 대응 방안 |
|---|--------|--------|-----------|----------|
| RISK-01 | 대상 도메인 계획서 미완성으로 정본 연결 불가 | HIGH | MEDIUM | Phase 1 게이트에서 차단. 해당 도메인 완성 후 재시도 |
| RISK-02 | V2/V3 27건 도메인 귀속 장기 미확정 | MEDIUM | HIGH | R-19-4 적용하여 `06_v2-v3-advanced/`에 잠정 보관. 분기별 귀속 검토 회의 |
| RISK-03 | 인덱스 링크 부패 (도메인 폴더 구조 변경 시) | MEDIUM | MEDIUM | R8 분기별 정합성 검사 + R-19-2 동시 갱신 규칙 강제 |
| RISK-04 | 도메인 간 소유권 분쟁 재발 | LOW | LOW | CONFLICT_LOG 즉시 등록 + §9 프로토콜 적용 |
| RISK-05 | 상세명세(535줄)와 도메인 정본 간 값 불일치 발견 | MEDIUM | MEDIUM | 도메인 LOCK 우선 원칙(§9.2) 적용. 상세명세는 레거시 참조로 고정 |

### 14.2 비상 절차

| 상황 | 절차 |
|------|------|
| 도메인 폴더 삭제/이동 발생 | 즉시 인덱스 전수 점검 → 링크 갱신 → CONFLICT_LOG 기록 |
| 새로운 v12 항목 발견 | 상세명세 확인 → 도메인 귀속 판정 → 인덱스 추가 → 도메인 폴더 동시 등록 (R-19-2) |
| LOCK 값 변경 요청 | 해당 도메인 AUTHORITY_CHAIN 먼저 변경 → 본 AUTHORITY_CHAIN 상속 값 갱신 |

---

## 부록 §A — 도메인별 정본 연결

> **목적**: ~45건 전체 v12 항목의 도메인 매핑을 한 눈에 파악할 수 있는 마스터 테이블. 이 테이블이 이 도메인의 핵심 산출물이다.

### §A.1 섹션 A~D 확정 항목 (24건)

| # | 항목 ID | 항목명 | 상세명세 섹션 | 소속 도메인 | sot 2/ 정본 폴더 | 정본 파일 (추정 경로) | LOCK 상속 |
|---|---------|--------|-------------|-----------|----------------|---------------------|----------|
| 1 | A-1a | BreathingGuide | A-1 | #9 Health-Wellness | `3-6_Health-Wellness-EmotionAI/` | `04_stress-management/breathing_exercises.md` | LOCK-HW-07 |
| 2 | A-1b | GroundingExercise | A-1 | #9 Health-Wellness | `3-6_Health-Wellness-EmotionAI/` | `04_stress-management/grounding_technique.md` | LOCK-HW-08 |
| 3 | A-1c | MeditationTimer | A-1 | #9 Health-Wellness | `3-6_Health-Wellness-EmotionAI/` | `04_stress-management/mindfulness_meditation.md` | — |
| 4 | A-2a | ThoughtRecord | A-2 | #9 Health-Wellness | `3-6_Health-Wellness-EmotionAI/` | `04_stress-management/cbt_self_care.md` | LOCK-HW-09 |
| 5 | A-2b | CognitiveDistortionDetector | A-2 | #9 Health-Wellness | `3-6_Health-Wellness-EmotionAI/` | `06_ethics-privacy/cbt_distortion_taxonomy.md` | LOCK-HW-09 |
| 6 | A-3a | WorkloadMonitor | A-3 | #9 Health-Wellness | `3-6_Health-Wellness-EmotionAI/` | `04_stress-management/burnout_prevention.md` | — |
| 7 | A-3b | ForcedBreakOverlay | A-3 | #9 Health-Wellness | `3-6_Health-Wellness-EmotionAI/` | `04_stress-management/burnout_prevention.md` | — |
| 8 | A-4a | FlashcardEditor | A-4 | #8 Education | `3-5_Education-Learning/` | `02_spaced-repetition/` | — |
| 9 | A-4b | SM2ReviewEngine | A-4 | #6 PKM (주) + #8 Education (참조) | `3-3_PKM-Knowledge-Management/` | `03_spaced-repetition/` | #6 PKM SM-2 LOCK |
| 10 | A-4c | ReviewDashboard | A-4 | #8 Education | `3-5_Education-Learning/` | `05_learning-analytics/` | — |
| 11 | B-1 | Prompt Registry API | B-1 | #17 MLOps (주) | `4-4_MLOps-LLMOps/` | `01_prompt-versioning/` | LOCK-ML-02, 03 |
| 12 | B-2 | TemplateSets (3종) | B-2 | #11 Conversation-A2A (주) | `3-8_Conversation-A2A/` | (에이전트 대화 패턴 폴더) | — |
| 13 | C-1 | Black-Litterman Model | C-1 | AI Investing | `Ai-investing-detail/` | `15_portfolio-advanced/portfolio_optimization.md` | AI-Invest tau=0.025 LOCK |
| 14 | C-2 | Factor Investing | C-2 | AI Investing | `Ai-investing-detail/` | `20_strategy-detail/quant/factor.md` | AI-Invest Factor 6종 LOCK |
| 15 | D-1 | Evolution Control | D-1 | #6 PKM | `3-3_PKM-Knowledge-Management/` | `01_knowledge-capture/` | — |
| 16 | D-2 | Korean Stopwords | D-2 | #6 PKM | `3-3_PKM-Knowledge-Management/` | `01_knowledge-capture/` | — |
| 17 | D-3 | Code Snippets | D-3 | #10 Dev-Tools | `3-7_Developer-Tools-API-SDK/` | `01_coding-engine/` | — |
| 18 | D-4 | Idea Capture | D-4 | #6 PKM | `3-3_PKM-Knowledge-Management/` | `01_knowledge-capture/` | — |
| 19 | D-5 | SWOT Analysis | D-5 | #12 Business | `3-9_Business-Model-Strategy/` | `02_market-analysis/` | — |
| 20 | D-6 | Writing Support | D-6 | #6 PKM | `3-3_PKM-Knowledge-Management/` | `01_knowledge-capture/` | — |
| 21 | D-7 | Zettelkasten | D-7 | #6 PKM | `3-3_PKM-Knowledge-Management/` | `06_zettelkasten/` | #6 PKM Zettelkasten LOCK |
| 22 | D-8 | Knowledge Maturity | D-8 | #6 PKM | `3-3_PKM-Knowledge-Management/` | `02_knowledge-graph/` | — |
| 23 | D-9 | Task Checkpoint | D-9 | #7 Workflow | `3-4_Workflow-RPA/` | `01_dag-engine/` | — |
| 24 | D-10 | Zettelkasten Extension | D-10 | #6 PKM | `3-3_PKM-Knowledge-Management/` | `06_zettelkasten/` | #6 PKM Zettelkasten LOCK |

### §A.2 섹션 E~G 잠정 항목 (27건)

| # | 항목 ID | 항목명 | 상세명세 섹션 | 우선순위 | 잠정 소속 도메인 | 귀속 상태 |
|---|---------|--------|-------------|---------|----------------|----------|
| 25 | E-1 | Enhanced Context Window | E | HIGH | #1 Verifier-Reasoning | 잠정 |
| 26 | E-2 | Multi-turn Reasoning | E | HIGH | #1 Verifier-Reasoning | 잠정 |
| 27 | E-3 | Adaptive Prompt Optimization | E | HIGH | #17 MLOps | 잠정 |
| 28 | E-4 | Cross-session Memory | E | HIGH | #6 PKM | 잠정 |
| 29 | E-5 | Hybrid RAG v2 | E | HIGH | #2 Auxiliary-Modules | 잠정 |
| 30 | E-6 | Advanced Code Generation | E | HIGH | #10 Dev-Tools | 잠정 |
| 31 | E-7 | Multimodal Reasoning | E | HIGH | #5 Multimodal | 잠정 |
| 32 | E-8 | Agent Collaboration Protocol | E | HIGH | #13 Agent-Protocol | 잠정 |
| 33 | E-9 | Personalized Learning Path | E | MEDIUM | #8 Education | 잠정 |
| 34 | E-10 | Emotion-aware Dialogue | E | MEDIUM | #9 Health-Wellness | 잠정 |
| 35 | E-11 | Financial Report Generator | E | MEDIUM | AI Investing | 잠정 |
| 36 | E-12 | Workflow Template Marketplace | E | MEDIUM | #7 Workflow | 잠정 |
| 37 | E-13 | Privacy-preserving Analytics | E | MEDIUM | #14 Rust-Tauri | 잠정 |
| 38 | E-14 | Model Ensemble Framework | E | MEDIUM | #17 MLOps | 잠정 |
| 39 | E-15 | Cross-platform Sync | E | MEDIUM | #14 Rust-Tauri | 잠정 |
| 40 | F-1 | Federated Learning | F | MEDIUM | #17 MLOps | 잠정 |
| 41 | F-2 | KG Auto-builder | F | MEDIUM | #6 PKM | 잠정 |
| 42 | F-3 | Multi-agent Debate | F | MEDIUM | #13 Agent-Protocol | 잠정 |
| 43 | F-4 | Continuous Learning Pipeline | F | MEDIUM | #17 MLOps | 잠정 |
| 44 | F-5 | Cross-modal Transfer | F | MEDIUM | #5 Multimodal | 잠정 |
| 45 | F-6 | Autonomous Code Review | F | MEDIUM | #10 Dev-Tools | 잠정 |
| 46 | G-1 | Neuromorphic Attention | G | LOW | #1 Verifier-Reasoning | 잠정 |
| 47 | G-2 | Quantum-inspired Optimization | G | LOW | #2 Auxiliary-Modules | 잠정 |
| 48 | G-3 | Self-evolving Agent | G | LOW | #13 Agent-Protocol | 잠정 |
| 49 | G-4 | Bio-inspired Memory Architecture | G | LOW | #6 PKM | 잠정 |
| 50 | G-5 | Swarm Intelligence Framework | G | LOW | #13 Agent-Protocol | 잠정 |
| 51 | G-6 | AGI Safety Framework | G | LOW | #13 Agent-Protocol | 잠정 |

### §A.3 도메인별 항목 수 요약

| 도메인 | 확정 항목 | 잠정 항목 | 합계 | 주요 서브폴더 |
|--------|---------|---------|------|-------------|
| #1 Verifier-Reasoning | 0 | 3 (E-1,2 / G-1) | 3 | `06_v2-v3-advanced/` |
| #2 Auxiliary-Modules | 0 | 2 (E-5 / G-2) | 2 | `06_v2-v3-advanced/` |
| #5 Multimodal | 0 | 2 (E-7 / F-5) | 2 | `06_v2-v3-advanced/` |
| #6 PKM | 8 (A-4b, D-1,2,4,6,7,8,10) | 3 (E-4 / F-2 / G-4) | 11 | `02_learning-tools/`, `05_cloud-library/`, `06_v2-v3-advanced/` |
| #7 Workflow | 1 (D-9) | 1 (E-12) | 2 | `05_cloud-library/`, `06_v2-v3-advanced/` |
| #8 Education | 2 (A-4a,c) | 1 (E-9) | 3 | `02_learning-tools/`, `06_v2-v3-advanced/` |
| #9 Health-Wellness | 7 (A-1~A-3) | 1 (E-10) | 8 | `01_wellness-ui/`, `06_v2-v3-advanced/` |
| #10 Dev-Tools | 1 (D-3) | 2 (E-6 / F-6) | 3 | `05_cloud-library/`, `06_v2-v3-advanced/` |
| #11 Conversation-A2A | 1 (B-2) | 0 | 1 | `03_agent-teams/` |
| #12 Business | 1 (D-5) | 0 | 1 | `05_cloud-library/` |
| #13 Agent-Protocol | 0 | 5 (E-8 / F-3 / G-3,5,6) | 5 | `06_v2-v3-advanced/` |
| #14 Rust-Tauri | 0 | 2 (E-13,15) | 2 | `06_v2-v3-advanced/` |
| #17 MLOps | 1 (B-1) | 4 (E-3,14 / F-1,4) | 5 | `03_agent-teams/`, `06_v2-v3-advanced/` |
| AI Investing | 2 (C-1,2) | 1 (E-11) | 3 | `04_investing-additions/`, `06_v2-v3-advanced/` |
| **합계** | **24** | **27** | **51** | — |

### §A.4 LOCK 상속 참조 매트릭스

| LOCK-V12 ID | 상세명세 참조 | 상속 원본 도메인 | 상속 원본 LOCK ID | 값 요약 |
|-------------|-------------|----------------|------------------|---------|
| LOCK-V12-01 | — | 본 계획서 R-19-1 | (자체) | 도메인 LOCK 상속 원칙 |
| LOCK-V12-02 | A-4 (SM2) | #6 PKM | (PKM SM-2 LOCK) | ease_factor, interval 공식 |
| LOCK-V12-03 | C-1 (BL) | AI Investing | (AI-Invest tau LOCK) | tau = 0.025 |
| LOCK-V12-04 | C-2 (Factor) | AI Investing | (AI-Invest Factor LOCK) | 6종: Value/Momentum/Quality/Size/Volatility/Dividend |
| LOCK-V12-05 | A-2 (CBT) | #9 Health-Wellness | 부록 §C — cbt_distortion_taxonomy.md §4.1 (LOCK 미부여; LOCK-HW-09는 감정 AI 7원칙 거버넌스 관련) | 15가지 인지 왜곡 유형 |
| LOCK-V12-06 | A-1 (Breathing) | #9 Health-Wellness | LOCK-HW-07 | 4-7-8 호흡법 (흡4초-지7초-호8초) |
| LOCK-V12-07 | B-2 (TS) | 2-1 Blue-Node-Architecture (D2.0-03 §4.2) | LOCK-BN-18 + D2.0-03 §4.2 (LOCK) TemplateSet = 3종 | TS_CORE, TS_WEB_RESEARCH, TS_CODE |
| LOCK-V12-08 | C-2 (Portfolio) | AI Investing | (AI-Invest Constraints LOCK) | 단일 종목 max 10%, 단일 섹터 max 30% |
| LOCK-V12-09 | D-7 (Zettel) | #6 PKM | (PKM Zettelkasten LOCK) | 원자적 노트, 5종 링크 타입 (related/supports/contradicts/continues/branches) |
| LOCK-V12-10 | — | 본 계획서 부록 §A | (자체) | 전체 매핑 테이블 |

---

> **문서 끝** — v12 Additions Detail 구조화 종합 계획서 v1.0
> 총 ~45건 항목, 24건 확정 + 27건 잠정, 6개 서브폴더, 10개 LOCK, 3건 RESOLVED 충돌
