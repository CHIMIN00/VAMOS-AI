# VAMOS v9 Pipeline — 완전 계획서

> **버전**: v9.0.0-PLAN
> **작성일**: 2026-03-06
> **대상 문서**: `VAMOS_구현가이드_PART2_구현단계.md` v20.4.0 (3,807줄)
> **목적**: "문서 정합성" 이외의 6개 관점에서 PART2를 검증하여 "완벽하게 구현 가능한 가이드"로 확정
> **전제**: v8 파이프라인 완료 (Phase 2-C Checkpoint 8/8 PASS, 문서 정합성 확인 완료)

---

## 목차

1. [v8 vs v9 포지션](#1-v8-vs-v9-포지션)
2. [v9 6개 관점 정의](#2-v9-6개-관점-정의)
3. [27개 약점과 해결 매핑](#3-27개-약점과-해결-매핑)
4. [RULE 1~14 방어 규칙](#4-rule-1-14-방어-규칙)
5. [Phase -1: 기반 정비](#5-phase--1-기반-정비)
6. [Phase 0-Pre: Ground Truth 구축](#6-phase-0-pre-ground-truth-구축)
7. [Phase 0: 프롬프트 작성](#7-phase-0-프롬프트-작성)
8. [Phase 0-Validate: 시범 실행](#8-phase-0-validate-시범-실행)
9. [Phase 1: 전수 실행 (Wave 구조)](#9-phase-1-전수-실행)
10. [Phase 2: 수정 + 재검증](#10-phase-2-수정--재검증)
11. [판정 기준](#11-판정-기준)
12. [입출력 파일 인덱스](#12-입출력-파일-인덱스)

---

# 1. v8 vs v9 포지션

```
v8 (완료)                              v9 (본 계획)
─────────────────────────────          ─────────────────────────────
축: 문서 정합성                        축: 구현 준비 완전성
├── SOT ↔ PART2 수치/필드/파라미터     ├── A. 의존성 순서
├── Stage Gate ↔ 구현 항목 정합성      ├── B. 파일 경로 정합성
├── LOCK/FREEZE 값 정확성              ├── C. 구현 가능성
└── 변경이력/번호 일관성               ├── D. 누적 산출물 추적
                                       ├── E. 수량 일관성
                                       └── F. 외부 의존성 실현성

v8 검증 범위: PART2 본문 ↔ SOT 문서 간 "값"의 일치
v9 검증 범위: PART2 내부의 "구조/순서/완전성/실현성"
```

---

# 2. v9 6개 관점 정의

## 관점 A: 의존성 순서 (Dependency Order)

| 항목 | 내용 |
|------|------|
| **핵심 질문** | STEP N이 STEP N+2의 산출물을 전제하고 있지 않은가? |
| **검증 범위** | §2-§5 (18 Stage 간 종적 의존성) + §6 (횡단 의존성) + §7 (GO/NO-GO) |
| **입력 GT** | GT-2 (산출물 체인 레지스트리) |
| **검출 대상** | 순환 의존성, 전제 산출물 미생성, 병렬 vs 순차 모순 |
| **예시** | V0-STEP-4에서 Gate를 구현하는데, Gate가 참조하는 Registry가 STEP-2에서 정의되었는가? |

## 관점 B: 파일 경로 정합성 (Path Consistency)

| 항목 | 내용 |
|------|------|
| **핵심 질문** | PART2의 모든 파일경로가 PHASE_B2 모노레포 구조와 일치하는가? |
| **검증 범위** | §2-§5 (AI 프롬프트 내 경로) + §6 (CI/CD yml, SDAR 파일 등) |
| **입력 GT** | GT-1 (파일 경로 레지스트리) |
| **검출 대상** | PHASE_B2 미존재 경로, 동일 파일의 경로 불일치, 상대/절대 혼재 |
| **예시** | `backend/vamos_core/orange_core/i01_intent.py` — PHASE_B2에 이 경로가 존재하는가? |

## 관점 C: 구현 가능성 (Implementability)

| 항목 | 내용 |
|------|------|
| **핵심 질문** | AI 프롬프트를 받은 개발자/AI가 실제로 구현할 수 있을 만큼 구체적인가? |
| **검증 범위** | §2 (V0 AI 프롬프트 6개) + §4-§5 (V2/V3 AI 프롬프트 6개) + §3 (V1 테이블 77행) + §6 (시스템별 상세) |
| **입력 GT** | GT-5 (구현 가능성 체크리스트, SOT에서 도출) |
| **검출 대상** | 모호한 명세, 누락된 파라미터, 참조만 있고 값 없음, 실행 가이드 부재 |
| **예시** | "LangGraph 5-Phase 구현" — 노드 이름, 엣지 조건, StateGraph 키가 명시되어 있는가? |
| **특이사항** | V1 Phase 1~6에는 AI 프롬프트 블록이 없음 (테이블만). 별도 체크리스트 적용 |

## 관점 D: 누적 산출물 추적 (Cumulative Artifact)

| 항목 | 내용 |
|------|------|
| **핵심 질문** | 각 STEP 완료 후 존재해야 할 파일 목록이 다음 STEP의 전제와 일치하는가? |
| **검증 범위** | §2-§5 (18 Stage의 산출물 → 다음 Stage 전제) + §7 (GO/NO-GO) |
| **입력 GT** | GT-2 (산출물 체인 레지스트리) |
| **검출 대상** | 산출물 미생성 후 참조, Stage Gate와 GO/NO-GO 간 중복/누락 |
| **예시** | V0-STEP-3 완료 시 `python_manager.rs`가 생겨야 STEP-4에서 import 가능 |

## 관점 E: 수량 일관성 (Quantity Consistency)

| 항목 | 내용 |
|------|------|
| **핵심 질문** | "17개 모듈", "44개 컴포넌트", "88개 API" 등 수치가 파일 내 모든 위치에서 동일한가? |
| **검증 범위** | §1-§7.6 전체 (변경 이력 §3777-3807 제외) |
| **입력 GT** | GT-3 (수량 인덱스) |
| **검출 대상** | 동일 수치의 위치별 불일치, LOCK 수치 vs ~근사치 구분 위반, §6.13 산술 오류 |
| **예시** | V1-Phase 1에서 "17개"라고 했는데 V1 완료 체크리스트에서도 "17개"인가? |

## 관점 F: 외부 의존성 실현성 (Feasibility)

| 항목 | 내용 |
|------|------|
| **핵심 질문** | 지정된 라이브러리/도구가 실제로 존재하고 호환되며, 비용 범위 내인가? |
| **검증 범위** | §2-§5 (기술 스택) + §6.8 (AI Investing) + §6.10 (Cloud Library) + SOT (PHASE_B3) |
| **입력 GT** | GT-4 (외부 의존성 레지스트리) |
| **검출 대상** | 미존재 라이브러리, 버전 비호환, 라이선스 충돌, V버전 범위 오류 |
| **예시** | FlagEmbedding Matryoshka 256dim이 실제로 BGE-M3에서 지원되는가? |

---

# 3. 27개 약점과 해결 매핑

## 3.1 구조적 약점 (S등급 — 8건)

| # | 약점 | 위험 | 해결 Phase | 해결 방법 |
|---|------|------|-----------|----------|
| 1 | GT 2개 누락 (관점 C, F에 Ground Truth 없음) | 관점 C/F 검증 불가 | Phase 0-Pre | GT-4 (외부 의존성 94개), GT-5 (구현 가능성 체크리스트) 추가 |
| 2 | V1 형식 차이 (AI 프롬프트 0개, 테이블만 존재) | V1 구현 가능성 검증 불가 | Phase 0-Pre | GT-5에 V1 전용 체크리스트 설계 ("모듈명/파일경로/SOT참조/구현수준" 4항목 필수) |
| 7 | SOT 파일명 ↔ PART2 참조명 매핑 미확보 | SOT 교차 검증 실패 | Phase -1A | 43개 산출물 파일의 PART2 참조명(D2.0-04) ↔ 실제 파일명(D2.0-04_INFRA_CORE.md) 매핑 테이블 |
| 8 | config "13 vs 17" 미해결 | GT-3 오염 | Phase -1B | PHASE_B4 실물 기준 확정: TOML 섹션=13개, V1+=4개 추가=17개 (또는 ENV 포함 여부 확인) |
| 9 | §6-§7 (1,108줄, 28%) 미커버 | PART2의 28% 검증 누락 | Phase -1D + RULE-11 | §6(13개 하위섹션)+§7(6개 하위섹션) 교차 인덱스 구축 + 6개 관점 모두 §6/§7 포함 |
| 15 | §6.1 "~85" vs §6.13 UI/UX "~135" 수치 불일치 | GT-3 구축 시 어느 값이 정답인지 불명 | Phase -1D + RULE-13 | §6 헤더 수치 ↔ §6.13 매트릭스 행 합계 교차 검증 규칙 |
| 16 | V1 Phase 2~6 파일 경로 전무 | GT-1에 빈 영역 발생 | Phase 0-Pre GT-1 | §6 파일 경로 + PHASE_B2 정본 경로를 V1 Phase에 역매핑하는 보조 인덱스 |
| 17 | V1 Phase 1 칼럼 비일관성 (6열 vs 5열) | 문서 구조 오류 미감지 | Phase -1H | v8 Phase 0 (0-A Table Structure) v20.4.0 재실행으로 선제 확인 |

## 3.2 논리적 약점 (L등급 — 14건)

| # | 약점 | 위험 | 해결 Phase | 해결 방법 |
|---|------|------|-----------|----------|
| 3 | Phase 0-Validate V0만 시범 실행 | V2/V3/§6 패턴 미검증 | Phase 0-Val | 4샘플: V0-STEP-1 + V1-Phase 1 + V2-Phase 1 + §6.1 |
| 4 | ~근사치 vs LOCK 정확 수치 미구분 | 근사치를 오류로 오판 | RULE-8 | ~접두사 → ±20% 허용, LOCK/FREEZE → 정확 매칭만 |
| 5 | 의도적 추가 경로 3건 FP | rpc/, data/, logs/ 오탐 | Phase -1C | PART2 HTML 주석(NOTE/XREF) 전수 수집 → 허용 목록 |
| 6 | v9 고유 FP 유형 미대비 | 새 유형 FP 발생 | RULE-7~10 | 병렬 의존성, 근사치, 주석, 버전 범위 4개 규칙 |
| 10 | §2-5 ↔ §6 교차 일관성 미검증 | 동일 항목의 수치 불일치 미감지 | RULE-12 | §2-5 수치와 §6 상세 수치 교차 일치 검증 |
| 11 | GO/NO-GO 62항목 ↔ Stage Gate ~190항목 관계 미정의 | GT-2 불완전 | Phase -1E | 62항목 각각이 190항목 중 어디에 매핑되는지 + 고유 항목 식별 |
| 12 | GT-5 순환 검증 (PART2에서 추출 → PART2 검증) | 누락 감지 불가 | Phase 0-Pre GT-5 | GT-5를 SOT 문서(D2.0-02, D2.0-05 등)에서 도출 |
| 13 | 음성 대조군(Negative Test) 부재 | FN(위음성) 미검증 | Phase 0-Val-N | 의도적 오류 삽입 문서로 프롬프트 감지력 테스트 |
| 18 | §6.13 3차원 정합성 미검증 | 영역별/버전별/Stage별 합계 불일치 | GT-3 | §6.13 행 합계 + 열 합계 + §2-5 항목 합산 교차 확인 |
| 19 | V1 Phase 6 병렬 ↔ 순차 게이트 모순 | 의존성 순서 판정 불가 | Phase -1E + RULE-7 | "병렬 실행 + 순차 검증" 패턴 정의 → RULE-7에 허용 패턴 등록 |
| 20 | changelog 수치 진동 (테스트 수, V2 모듈 수) | GT-3 구축 시 과거 값 혼입 | GT-3 원칙 | "수량 추출은 본문(§1-§7.6)에서만, 변경 이력 절대 참조 금지" |
| 21 | changelog v17.0.0 순서 이상 | 문서 구조 오류 잔존 | Phase -1H | v8 0-C (Heading Hierarchy) v20.4.0 재실행 |
| 22 | §7.5 "코드 검증" 항목이 v9 범위에 혼입 | 검증 불가 항목에서 FN 오분류 | Phase -1I + RULE-14 | v9 범위 = 문서 정합성/완전성. 코드 동작 검증은 범위 외 |
| 23 | GT-2에 §6 횡단 의존성 미포함 | Stage 전제조건 미감지 | GT-2 | §6 정의(UI SM, LOCK-AT, SDAR 등)가 어떤 Stage의 전제인지 매핑 |

## 3.3 운영적 약점 (O등급 — 5건)

| # | 약점 | 위험 | 해결 Phase | 해결 방법 |
|---|------|------|-----------|----------|
| 14 | changelog 제외 범위 미특정 | 프롬프트가 과거 수치를 현재로 오인 | Phase -1F | line 3777-3807 명시적 제외 |
| 24 | SOT 문서 경로 안정화 | 파일 삭제 시 GT 무효화 | Phase -1G | 정본(OneDrive) → D:\VAMOS\docs\sot\ 안정 경로로 복사 |
| 25 | v9 Phase 2 수정 후 GT 업데이트 미계획 | 재검증 시 GT-본문 불일치 | Phase 2 설계 | Phase 2 Ripple Fix → GT 재구축 → Phase 1 재실행 |
| 26 | GT-1 상대경로 vs 절대경로 혼재 | 동일 파일 미인식 | GT-1 구축 원칙 | 모든 경로를 PHASE_B2 기준 정규화 절대경로로 통일 |
| 27 | v8 Phase 0 v20.4.0 미재실행 | v20.x 변경으로 잔존 구조 이슈 | Phase -1H | v8 14개 스크립트 v20.4.0 재실행 |

---

# 4. RULE 1~14 방어 규칙

## v8 FP 방어 (RULE 1~6)

v8에서 발생한 FALSE_POSITIVE 16건의 원인 6개 유형에서 도출.

| RULE | 규칙 | 원인 유형 | v8 FP 건수 |
|------|------|----------|-----------|
| **RULE-1** | 비교 시 `section.key` 정규화 전체 경로 사용. 부분 문자열 매칭 금지 | 부분 키 매칭 | 3건 |
| **RULE-2** | V0/V1/V2/V3 범위 한정자를 먼저 확인. V2 전용 항목을 V1 누락으로 판정 금지 | 버전 스코프 미구분 | 3건 |
| **RULE-3** | changelog(line 3777-3807), STEP7 보강(K-xxx), 인라인 주석 `# V2=...` 는 현행 구현과 별도 컨텍스트. 불일치 검출 대상에서 제외하거나 별도 분류 | 컨텍스트 차이 | 3건 |
| **RULE-4** | MISSING 판정 전 상위 LOCK/FREEZE 계층에서 간접 커버 여부 확인 필수. 개념적 커버와 완전 부재를 구분 | 간접 커버 미인식 | 3건 |
| **RULE-5** | 요약 테이블 vs 전체 열거, 약칭 vs 풀네임은 구조적 표현 차이이지 데이터 오류가 아님 | 구조적 차이 | 2건 |
| **RULE-6** | 코드 주석(`#`) 내 기술명은 현재 사용이 아닌 참고/예고로 분류. 상태 코드(S3 등)와 서비스명(S3) 구분 | 인라인 주석 오인식 | 1건 |

## v9 고유 방어 (RULE 7~14)

v9 관점에서 새로 발생할 FP/FN 유형에서 도출.

| RULE | 규칙 | 대응 약점 |
|------|------|----------|
| **RULE-7** | 비선형 의존성(병렬, 조건부) 별도 분류. "V1-Phase 6: Phase 3-5와 병렬"처럼 병렬 실행 + 순차 검증 패턴은 허용 패턴으로 등록. 병렬 관계를 순환 의존성으로 오판 금지 | #6, #19 |
| **RULE-8** | `~` 접두사 근사치는 ±20% 허용. LOCK/FREEZE/ABSOLUTE 태그가 붙은 수치만 정확 매칭 요구. 예: `~44`는 35~53 허용, `18 (FREEZE)`는 정확히 18만 허용 | #4 |
| **RULE-9** | PART2 내 HTML 주석(`<!-- NOTE -->`, `<!-- SOURCE_CONFLICT -->`, `<!-- XREF -->`)은 의도적 기록이므로 오류 판정 대상에서 제외. 허용 목록(Phase -1C)에 등록된 항목은 자동 PASS | #5 |
| **RULE-10** | 라이브러리 존재/호환성은 버전 범위 표기(`>=x,<y`) 기준으로 판정. 범위 내 최소 1개 버전이 존재하면 PASS. 정확한 단일 버전이 아니어도 오류 아님 | #6 |
| **RULE-11** | 검증 범위에 §6(13개 하위 섹션: §6.1~§6.13) + §7(6개 하위 섹션: §7.1~§7.6) 포함 필수. "18 Stage" 뿐 아니라 시스템별 상세 + 최종 검토사항까지 전수 검증 | #9 |
| **RULE-12** | §2-5의 수치와 §6의 상세 수치를 교차 검증. 예: V1-Phase 4 "React ~44개" ↔ §6.1.2 "~44개" 상세 테이블의 그룹별 합산 = 44인지 확인 | #10 |
| **RULE-13** | §6 각 섹션 헤더의 수치와 §6.13 매트릭스의 해당 행 합계를 교차 검증. 예: §6.1 "~85" vs §6.13 UI/UX 합계 "~135" → 정의 차이인지 실제 오류인지 판정 | #15 |
| **RULE-14** | v9 범위 = PART2 문서 내부의 정합성, 완전성, 구현 가능성. §7.5의 "코드 동작 검증" 항목(PII 마스킹 동작, Gate 우회 불가 등)은 v9 범위 외 → SKIP 처리 | #22 |

---

# 5. Phase -1: 기반 정비

> **목적**: GT 구축 전에 "GT의 정확성을 보증하는 메타 검증" 수행
> **예상 소요**: Phase -1 전체 1~2세션

## [-1A] SOT 파일명 ↔ PART2 참조명 매핑 테이블

**입력**: §7.6 산출물 파일 인덱스 43개 + 정본 경로(`C:\Users\dkscl\OneDrive\바탕 화면\VAMOS\00. 통합\02. TECH\00. FINAL SUMMARY\STEP6_pipeline\output\updated\`) 실제 파일 목록
**작업**:
1. PART2에서 사용되는 참조명 전수 수집 (예: `D2.0-04`, `D2.0-04 §5`, `PHASE_B2 §3.1`)
2. 실제 파일명과 1:1 매핑 (예: `D2.0-04` → `D2.0-04_INFRA_CORE.md`)
3. 미발견 파일 식별 (특히 D2.1-D1~D8 개별 파일)
4. §7.6의 43개가 실제 파일 43개와 일치하는지 검증 (이미 확인: 정확히 43개)

**산출물**: `v9_sot_mapping.json`
```json
{
  "D2.0-04": {
    "filename": "D2.0-04_INFRA_CORE.md",
    "path": "D:/VAMOS/docs/sot/D2.0-04_INFRA_CORE.md",
    "lines": 1584,
    "part2_references": ["line 864", "line 1428", ...]
  },
  ...
}
```

## [-1B] config "13 vs 17" 확정 판정

**입력**: PART2 line 117 (`B4 정본은 17섹션. V0에서 4개 생략`), PHASE_B4 실물
**작업**:
1. PHASE_B_EXHAUSTIVE_ANALYSIS.md에서 config 섹션 전수 확인
2. 이미 확인된 사실: TOML 내 `[section]` 기준 = 13개
3. V1+ 추가 4개 = `[rate_limit]`, `[blue_nodes]`, `[ui]`, `[guardrails]`
4. 13+4 = 17의 근거 확인 또는 반박

**산출물**: 확정 판정문 (GT-3에 반영)

## [-1C] 의도적 추가/SOURCE_CONFLICT 허용 목록

**입력**: PART2 전문에서 HTML 주석 추출
**작업**:
1. `<!-- NOTE -->`, `<!-- SOURCE_CONFLICT -->`, `<!-- XREF -->`, `<!-- RESOLVED -->` 전수 수집
2. 각 주석이 어떤 "의도적 차이"를 기록하는지 분류
3. 알려진 3건: rpc/ (XREF-V0-12), data/ (NOTE), logs/ (NOTE)
4. §7.5.5의 SC-01~SC-12와 대조

**산출물**: `v9_allowlist.json`
```json
{
  "path_additions": ["rpc/", "data/", "logs/"],
  "source_conflicts": ["SC-01", "SC-02", ..., "SC-12"],
  "xref_notes": ["XREF-V0-10", "XREF-V0-12", ...]
}
```

## [-1D] §6-§7 ↔ §2-§5 교차 인덱스

**입력**: PART2 §6(line 2699-3562), §7(line 3564-3775)
**작업**:
1. §6의 13개 하위 섹션 목록 확정
   - §6.1 UI/UX (~85항목), §6.2 Rust/Tauri (~108항목), §6.3 테스트 (~84항목)
   - §6.4 CI/CD (~14항목), §6.5 보안 (15항목), §6.6 MCP (~7항목)
   - §6.7 Agent Teams, §6.8 AI Investing, §6.8.1 RT-BNP 연동
   - §6.9 SDAR, §6.10 Cloud Library, §6.10.1 RT-BNP, §6.10.2 DCL
   - §6.11 이벤트/로깅, §6.12 운영 결정 (2건), §6.13 작업량 요약
2. 각 §6 섹션이 §2-§5의 어떤 Stage에 대응하는지 매핑
3. §7의 6개 하위 섹션 인덱스
4. §6 헤더 수치 vs §6.13 매트릭스 대조표 작성:
   - §6.1: ~85 vs UI/UX합계 ~135 → 차이 원인 규명
   - §6.2: ~108 vs 인프라합계 ~108 → 일치 확인
   - §6.3: ~84 vs 테스트합계 ~84 → 일치 확인
   - (나머지 동일)

**산출물**: `v9_cross_section_index.json`

## [-1E] GO/NO-GO 62항목 ↔ Stage Gate ~190항목 관계 + 병렬 패턴 정의

**입력**: §7.1-§7.4 (GO/NO-GO 62항목), §2-§5 내 "단계 완료 검증" 섹션 (~190항목)
**작업**:
1. GO/NO-GO 62항목 각각을 Stage Gate 항목에 매핑
   - 매핑 유형: SUBSET(Stage Gate의 부분집합), SUPERSET(상위 요약), UNIQUE(GO/NO-GO에만 있음)
   - 예: GO/NO-GO V0 #7 "PLAN-2.0 (대체됨) 표기" (CC-010) → Stage Gate에 없음 = UNIQUE (문서 작업)
2. 병렬 실행 패턴 정의:
   - V1-Phase 6: "Phase 3-5와 병렬"
   - 정의: 작업은 Phase 3 시작 후 병행 가능, 검증/완료 선언은 Phase 5 완료 후
   - GT-2에 `parallel_with: ["Phase 3", "Phase 4", "Phase 5"]` + `validate_after: "Phase 5"` 속성 추가
3. Stage Gate 검증 항목 수 합산:
   - V0: STEP 1~6 각각의 검증 항목 수 합산
   - V1: Phase 1~6 각각의 검증 항목 수 합산 (이미 확인: 10+12+11+12+11+10 = 66)
   - V2, V3 동일

**산출물**: `v9_gate_mapping.json`

## [-1F] changelog 제외 줄 범위 확정

**입력**: PART2 변경 이력 (line 3777~3807)
**작업**:
1. 정확한 줄 범위 확인: `## 변경 이력` 시작 ~ 파일 끝
2. v20.4.0 기준 줄 범위 확정
3. v17.0.0 순서 이상 확인 (line 3807, 날짜 2026-03-03인데 v20.4.0 뒤에 배치)
4. 모든 v9 프롬프트에 `exclude_lines: [3777, 3807]` 지시 삽입

**산출물**: 프롬프트 지시문에 반영

## [-1G] SOT 문서 안정 경로 이동

**입력**: 정본 경로(`C:\Users\dkscl\OneDrive\바탕 화면\VAMOS\00. 통합\02. TECH\00. FINAL SUMMARY\STEP6_pipeline\output\updated\`) 내 43개 SOT 문서
**작업**:
1. `D:\VAMOS\docs\sot\` 디렉토리 생성 (완료)
2. 정본 경로에서 43개 SOT 문서 전체 복사:
   - CLAUDE.md (697줄)
   - VAMOS_AI_INVESTING_SPEC.md (1,379줄)
   - D2.0-04_INFRA_CORE.md (1,584줄)
   - D2.0-07_SAFETY_COST_APPROVAL.md (2,580줄)
   - D2.0-08_UI_UX.md (2,776줄)
   - 외 38개 SOT 문서
3. [-1A]의 매핑 테이블에서 모든 경로를 안정 경로로 갱신 (완료)

**산출물**: `D:\VAMOS\docs\sot\` 디렉토리 + 파일

## [-1H] v8 Phase 0 재실행 (v20.4.0 기준)

**입력**: `D:\VAMOS\04. 구현단계\v8_results\phase0\phase0_part1.py`, `phase0_part2.py`
**작업**:
1. v8 14개 스크립트를 PART2 v20.4.0에 대해 재실행
   - 0-A (Table Structure): v20.0.0에서 Stage Gate 테이블 18개 추가 → 칼럼 일관성
   - 0-B (Arithmetic Sum): V0=5, V1=32, V2=42, V3=81
   - 0-C (Heading Hierarchy): v17.0.0 순서 이상 감지 여부
   - 0-D~0-H, IMP-A~IMP-F: v19.1.0 이후 변경사항 반영
2. 결과 분류: REAL_ERROR → Phase -1에서 즉시 수정, FALSE_POSITIVE → RULE 확인
3. V1 Phase 1 칼럼 비일관성(6열 vs 5열) 감지 여부 확인

**산출물**: `v9_phase-1h_v8_rerun_report.md`

## [-1I] v9 검증 범위 명시 정의

**입력**: §7.5 크로스컷 검토 항목 전수
**작업**:
1. §7.5 각 항목에 "문서 검증 가능" vs "구현 후 검증" 태그 부여:
   - 문서 검증 가능: I-모듈 번호 일관성, LOCK 값 반영, RBAC 역할 통일, 비용 임계값 단일화, 스키마 버전 통일
   - 구현 후 검증: PII 마스킹 동작, Non-goal 차단, P2 자동 OFF, Gate 우회 불가, Docker 샌드박스, 성능 목표
2. v9 범위 선언문 작성:

```
v9 SCOPE DEFINITION:
- IN SCOPE: PART2 문서 내부의 정합성, 완전성, 구현 가능성, 수량 일관성,
            파일 경로 정합성, 의존성 순서, 외부 의존성 실현성
- OUT OF SCOPE: 코드 레벨 동작 검증, 성능 벤치마크, 보안 침투 테스트
- BOUNDARY: §7.5 항목 중 "문서 검증 가능" 태그만 v9 범위 내
```

**산출물**: v9 범위 정의문 (모든 프롬프트 헤더에 삽입)

---

# 6. Phase 0-Pre: Ground Truth 구축

> **목적**: 6개 관점의 프롬프트가 참조할 "정답 데이터" 구축
> **전제**: Phase -1 완료 (매핑, 확정, 허용목록, 인덱스 확보)
> **예상 소요**: 1~2세션

## [GT-1] 파일 경로 레지스트리 (관점 B용)

**추출 원본**: PART2 전문 + PHASE_B2 정본
**구축 절차**:

1. **PART2 경로 추출** (§1-§7.6, changelog 제외)
   - AI 프롬프트 내 디렉토리 트리: ~30개 고유 디렉토리
   - 테이블/본문 내 파일 경로: ~40개 고유 파일
   - §6 CI/CD yml 14개, SDAR 파일 3개 등
   - 총 예상: ~60-80개 고유 경로

2. **PHASE_B2 정본 경로 추출**
   - Category B (886줄) 내 모든 디렉토리/파일
   - 각 경로에 V(V0/V1/V2/V3) 태그

3. **매칭**
   - PART2 경로 ↔ PHASE_B2 경로 대조
   - 상대경로(`i01_intent_detector.py`) → 절대경로(`backend/vamos_core/orange_core/i01_intent_detector.py`) 정규화
   - [-1C] 허용 목록 적용 (rpc/, data/, logs/ → 의도적 추가)

4. **V1 Phase 2~6 역매핑**
   - V1 Phase 2~6에 파일 경로가 없는 구현 항목 식별
   - §6의 파일 경로와 PHASE_B2를 기반으로 "이 구현 항목의 예상 파일 위치" 추론
   - 관점 C(구현 가능성)에서 "파일 경로 미명시"를 결함으로 플래그할지 판단 기준 수립

**산출물 스키마**:
```json
{
  "entries": [
    {
      "normalized_path": "backend/vamos_core/orange_core/i01_intent_detector.py",
      "part2_references": [
        {"line": 887, "format": "absolute", "section": "V0-STEP-4"},
        {"line": 1387, "format": "relative", "section": "V1-Phase 1", "raw": "i01_intent_detector.py"}
      ],
      "phase_b2_exists": true,
      "phase_b2_section": "§5.1",
      "v_scope": "V0+",
      "allowlist": false
    },
    {
      "normalized_path": "backend/vamos_core/rpc/server.py",
      "part2_references": [{"line": 657}, {"line": 709}],
      "phase_b2_exists": false,
      "allowlist": true,
      "allowlist_reason": "XREF-V0-12: 기능적 필요로 추가"
    }
  ],
  "stats": {
    "total_unique_paths": 0,
    "matched": 0,
    "allowlisted": 0,
    "unmatched": 0
  }
}
```

## [GT-2] 산출물 체인 레지스트리 (관점 A, D용)

**추출 원본**: PART2 §2-§5 전환 조건 + §6 횡단 의존성 + §7 GO/NO-GO
**구축 절차**:

1. **18 Stage별 입출력 추출**
   각 Stage에 대해:
   - `inputs`: 이 Stage가 시작하려면 존재해야 하는 산출물
   - `outputs`: 이 Stage가 완료되면 생성되는 산출물
   - `gate_conditions`: 전환 조건 전수 (항목 수 + 내용)
   - `gate_count`: 전환 조건 항목 수

2. **종적 의존성 체인**
   ```
   PART1 완료 → V0-STEP-1 → STEP-2 → ... → STEP-6
   → V1-P1 → V1-P2 → V1-P3 → V1-P4 → V1-P5 → V1-P6
   → V2-P1 → V2-P2 → V2-P3
   → V3-P1 → V3-P2 → V3-P3
   ```

3. **병렬 관계**
   - V1-Phase 6: `parallel_with: ["V1-P3", "V1-P4", "V1-P5"]`, `validate_after: "V1-P5"`
   - 다른 병렬 관계가 있는지 확인

4. **횡단 의존성 (§6 → Stage)**
   | §6 정의 | 의존하는 Stage | 의존 유형 |
   |---------|--------------|----------|
   | §6.1.6 UI State Machine 9-state | V1-Phase 4 | Phase 4가 이 정의를 구현 전제로 참조 |
   | §6.7 LOCK-AT 17건 | V1-Phase 3, V2-Phase 3 | Agent 구현이 이 제약을 준수 |
   | §6.9 SDAR 5-Layer/7-State/5-Gate | V2-Phase 2~3 | SDAR 구현의 아키텍처 전제 |
   | §6.10 Cloud Library 10-Layer/5-Gate | V2-Phase 3 | Cloud Library 구현 전제 |
   | §6.8 AI Investing 51% Gate/Circuit Breaker | V1-Phase 6 | AI Investing 구현 전제 |
   | §6.11 EventTypeRegistry 123항목 | V1-Phase 1+ | 이벤트 등록의 전제 |

5. **GO/NO-GO ↔ Stage Gate 매핑** ([-1E] 결과 반영)

**산출물**: `gt2_artifact_chain.json`

## [GT-3] 수량 인덱스 (관점 E용)

**추출 원본**: PART2 §1-§7.6 (line 1-3775, changelog 제외)
**구축 절차**:

1. **수량 추출** — 본문에서만 (변경 이력 line 3777-3807 절대 참조 금지)
   - 추출 패턴: `N개`, `N건`, `N항목`, `N줄`, `~N`, `N (LOCK)`, `N (FREEZE)` 등
   - 예상 항목 수: 200+건

2. **LOCK/FREEZE 태깅**
   각 수치에 정밀도 태그 부여:
   - `EXACT_LOCK`: LOCK/FREEZE/ABSOLUTE 태그 → 정확 매칭 필수
   - `EXACT_COUNT`: 명시적 카운트 (예: "16항목", "62항목") → 정확 매칭
   - `APPROX`: `~` 접두사 (예: "~44개", "~85개") → ±20% 허용
   - `DERIVED`: 다른 수치의 합산/계산 (예: 5+6+3+...=44) → 산술 검증

3. **교차 인덱스**
   동일 개념의 수치가 등장하는 모든 위치 매핑:
   ```
   "V1_active_modules": {
     "value": 32,
     "precision": "EXACT_COUNT",
     "locations": [
       {"line": 42, "section": "§1.1", "text": "V1 ... **32**"},
       {"line": 1377, "section": "§3 header", "text": "활성 모듈: CORE 32개"}
     ]
   }
   ```

4. **§6.13 산술 검증**
   - 행 합계: UI(~135)+인프라(~108)+테스트(~84)+CI(~14)+도구(~19)+보안(~15)+MCP(~7)+기타(~72) = ~454
   - 열 합계: V0(~41)+V1(~273)+V2(~92)+V3(~48) = ~454
   - 교차: 행 합계 = 열 합계 = ~454

5. **§6 헤더 ↔ §6.13 교차** ([-1D] 결과 반영)
   - §6.1 "~85" vs §6.13 UI/UX 합계 "~135" → 차이 원인 기록
   - 나머지 일치 확인

6. **[-1B] 확정 판정 반영**: config "13 vs 17" 해결값 GT-3에 등재

**산출물**: `gt3_quantity_index.json`

## [GT-4] 외부 의존성 레지스트리 (관점 F용)

**추출 원본**: PHASE_B_EXHAUSTIVE_ANALYSIS.md + PART2 + CLAUDE.md
**구축 절차**:

1. **라이브러리 전수 수집** (이미 확인: 94개)
   - npm: 28개 (react, zustand, recharts, ...)
   - Cargo: 17개 (tauri, serde, tokio, ...)
   - Python V1: 40개 (pydantic, langgraph, chromadb, ...)
   - Python V2 추가: 7개 (qdrant-client, neo4j, ...)
   - Python V3 추가: 5개 (vllm, prometheus-client, ...)

2. **각 라이브러리 속성 기록**
   ```json
   {
     "name": "chromadb",
     "version_spec": ">=0.5.23,<1.0",
     "v_scope": "V1_ONLY",
     "lock": true,
     "lock_note": "LOCK (V1), V2=qdrant",
     "license": "Apache-2.0",
     "part2_lines": [139, 1461, ...],
     "phase_b3_listed": true
   }
   ```

3. **§6 고유 의존성 추가 확인**
   - §6.8 AI Investing: yfinance, vectorbt, backtrader, TimescaleDB
   - §6.10 Cloud Library: 크롤러 라이브러리 (명시적 이름 없음 → 관점 C 이슈)
   - §6.9 SDAR: 추가 의존성 없음 (기존 모듈 재사용)

4. **인프라/서비스 도구 포함**
   - Ollama, Docker, K8s/Helm, GitHub Actions, Playwright 등

**산출물**: `v9_dependency_registry.json`

## [GT-5] 구현 가능성 체크리스트 (관점 C용)

**추출 원본**: SOT 문서 (D2.0-02, D2.0-05 등) — PART2에서 추출하면 순환 검증
**구축 절차**:

1. **"구현 가능한 프롬프트"의 외부 기준 정의**

   AI 프롬프트가 구현 가능하려면 최소한 다음이 명시되어야 함:

   | # | 필수 항목 | 설명 |
   |---|----------|------|
   | C-1 | 파일 경로 | 생성/수정할 파일의 절대 경로 |
   | C-2 | 입출력 스키마 | 함수/클래스의 입력과 출력 타입 |
   | C-3 | 의존성 | import할 모듈/패키지 목록 |
   | C-4 | 설정값 | config에서 읽어야 할 키와 기본값 |
   | C-5 | SOT 참조 | 구현 근거가 되는 SOT 문서와 섹션 |
   | C-6 | 성공 기준 | 테스트/검증 방법 (Stage Gate 항목과 연결) |
   | C-7 | LOCK 제약 | 해당 구현에 적용되는 LOCK/FREEZE 값 |

2. **V0 STEP 1~6 (AI 프롬프트 있음)**
   - 6개 AI 프롬프트 블록 각각에 C-1~C-7 체크 (STEP당 1개, "사용자 직접 작업"은 수동 체크리스트이므로 제외)
   - SOT 문서에서 해당 STEP의 "구현에 필요한 최소 명세 항목" 추출
   - 프롬프트에 누락된 항목 식별

3. **V1 Phase 1~6 (AI 프롬프트 없음, 테이블만)**
   - 별도 체크리스트:

   | # | V1 필수 항목 | 설명 |
   |---|-------------|------|
   | V1-1 | 모듈 ID + 파일명 | 테이블에 파일명 칼럼 존재 여부 (Phase 1만 있음, Phase 2~6 없음) |
   | V1-2 | 구현 내용 구체성 | 1줄 설명만으로 구현 가능한가, 모호하지 않은가 |
   | V1-3 | SOT 참조 | 산출물 참조 칼럼에 구체적 문서+섹션 |
   | V1-4 | LOCK 제약 명시 | 해당 모듈에 적용되는 LOCK 값이 테이블 내에 기술 |

   - Phase 1: 6열 테이블 (6행) + 5열 테이블 (11행) → V1-1~V1-4 체크
   - Phase 2~6: 4열 테이블 → V1-1(파일명 없음 = FAIL), V1-2~V1-4 체크

4. **V2/V3 Phase (AI 프롬프트 있음)**
   - 6개 AI 프롬프트 블록에 C-1~C-7 체크

**산출물**: `v9_implementability_checklist.json`

---

# 7. Phase 0: 프롬프트 작성

> **목적**: 6개 관점별 검증 프롬프트를 GT와 RULE을 기반으로 작성
> **전제**: Phase -1 + Phase 0-Pre 완료

## 프롬프트 공통 구조

각 프롬프트는 다음 구조를 따름:

```
[1] HEADER — v9 버전, 관점 ID, 대상 문서, 범위 정의 (RULE-14)
[2] SCOPE — 검증 대상 줄 범위 (changelog 제외: RULE-3, Phase -1F)
[3] GT REFERENCE — 참조할 GT 파일 경로
[4] RULES — 해당 관점에 적용되는 RULE 목록
[5] ALLOWLIST — Phase -1C 허용 목록
[6] CHECK ITEMS — 구체적 검증 항목 (GT에서 도출)
[7] OUTPUT FORMAT — 결과 JSON 스키마
[8] SEVERITY — BLOCKER/HIGH/MEDIUM/LOW 판정 기준
```

## 관점별 프롬프트 설계

### v9-A: 의존성 순서

```
적용 RULE: 1, 2, 3, 7, 9, 11, 14
입력 GT: GT-2 (산출물 체인)
검증 항목:
  [A-1] 각 Stage의 inputs가 이전 Stage의 outputs에 포함되는가
  [A-2] 순환 의존성이 없는가 (방향 그래프 순환 검출)
  [A-3] 전환 조건의 항목이 해당 Stage에서 실제로 구현되는가
  [A-4] §6 횡단 의존성: §6 정의가 해당 Stage 이전에 참조 가능한가
  [A-5] V1-Phase 6 병렬 패턴이 RULE-7 허용 패턴과 일치하는가
  [A-6] GO/NO-GO 항목 중 UNIQUE 유형이 실제로 해당 버전 내에서 수행 가능한가
검증 범위: §2-§5 (18 Stage) + §6 (횡단) + §7.1-§7.4 (GO/NO-GO)
```

### v9-B: 파일 경로 정합성

```
적용 RULE: 1, 2, 5, 6, 9, 11, 14
입력 GT: GT-1 (파일 경로 레지스트리)
검증 항목:
  [B-1] GT-1의 unmatched 경로 0건 확인 (allowlist 제외)
  [B-2] 동일 파일의 경로가 모든 위치에서 일관적인가
  [B-3] 상대경로 참조가 절대경로와 동일 파일을 가리키는가
  [B-4] §6의 파일 경로 (CI yml 14개, SDAR 3개 등)가 PHASE_B2와 일치하는가
  [B-5] V1 Phase 2~6의 파일 경로 부재를 보고 (정보 항목, ERROR는 아님)
검증 범위: §2-§6 (경로가 등장하는 모든 위치)
```

### v9-C: 구현 가능성

```
적용 RULE: 2, 4, 5, 8, 9, 11, 14
입력 GT: GT-5 (구현 가능성 체크리스트)
검증 항목:
  [C-1] V0 AI 프롬프트 6개: C-1~C-7 체크리스트 전수 적용
  [C-2] V1 테이블 77행: V1-1~V1-4 체크리스트 전수 적용
  [C-3] V2/V3 AI 프롬프트 6개: C-1~C-7 체크리스트 전수 적용
  [C-4] §6 고유 정의 (UI SM, LOCK-AT 등)의 구현 충분성
  [C-5] V1 Phase 2~6 "파일 경로 미명시" 플래그
  [C-6] V1 "실행 가이드/AI 프롬프트 부재" 플래그 (V0, V2/V3와의 형식 차이)
검증 범위: §2-§6 전체
SEVERITY 기준:
  - BLOCKER: 핵심 파라미터 누락으로 구현 불가
  - HIGH: SOT 참조 없이 모호한 명세
  - MEDIUM: 파일 경로 미명시 (§6/PHASE_B2에서 추론 가능)
  - LOW: 실행 가이드 부재 (V1 구조적 한계)
```

### v9-D: 누적 산출물 추적

```
적용 RULE: 1, 2, 7, 9, 11, 14
입력 GT: GT-2 (산출물 체인)
검증 항목:
  [D-1] Stage N 완료 시 존재해야 할 파일 목록이 Stage N+1의 전제와 일치하는가
  [D-2] GO/NO-GO 항목이 해당 버전의 모든 Stage 산출물을 포괄하는가
  [D-3] 전환 조건 항목 수가 §2-§5와 §7에서 동일하게 표기되는가
  [D-4] §6 횡단 정의가 "어느 Stage까지 완료되면 참조 가능"한지 명확한가
검증 범위: §2-§5 + §7.1-§7.4
```

### v9-E: 수량 일관성

```
적용 RULE: 2, 3, 5, 8, 11, 12, 13, 14
입력 GT: GT-3 (수량 인덱스)
검증 항목:
  [E-1] EXACT_LOCK 수치: 모든 출현 위치에서 동일 값
  [E-2] EXACT_COUNT 수치: 모든 출현 위치에서 동일 값
  [E-3] APPROX 수치: 동일 개념의 근사치가 ±20% 내
  [E-4] DERIVED 수치: 산술 합산/계산이 정확한가
  [E-5] §6.13 매트릭스: 행 합계 = 열 합계 = ~454
  [E-6] §6 헤더 수치 ↔ §6.13 교차 (RULE-13)
  [E-7] §2-5 수치 ↔ §6 상세 수치 교차 (RULE-12)
  [E-8] §7 GO/NO-GO 항목 수 (16+21+14+11=62) 정확성
  [E-9] §7.6 산출물 파일 수 (43개) 정확성
검증 범위: §1-§7.6 (line 1-3775)
제외 범위: 변경 이력 (line 3777-3807)
```

### v9-F: 외부 의존성 실현성

```
적용 RULE: 2, 6, 10, 11, 14
입력 GT: GT-4 (외부 의존성 레지스트리)
검증 항목:
  [F-1] 모든 라이브러리가 실재하는가 (PyPI/npm/crates.io 기준)
  [F-2] 지정 버전 범위 내에 실제 릴리스가 존재하는가
  [F-3] 상호 호환성: 동일 런타임의 라이브러리 간 충돌 없는가
  [F-4] V 범위 정확성: V1-ONLY 라이브러리가 V2에서 사용되지 않는가
  [F-5] 라이선스 충돌: GPL-3.0 (neo4j) 등 주의 항목
  [F-6] PART2에서 라이브러리를 언급하는 위치와 GT-4의 V 범위가 일치하는가
  [F-7] §6.8 AI Investing 전용 라이브러리 (yfinance, vectorbt 등)의 실현성
검증 범위: §2-§6 + SOT (PHASE_B3)
```

---

# 8. Phase 0-Validate: 시범 실행

> **목적**: 프롬프트의 FP(위양성) 0건 + FN(위음성) 0건 확인
> **전제**: Phase 0 프롬프트 작성 완료

## [Val-1] V0-STEP-1 (line 65-436, 372줄)

- **이유**: V0는 가장 상세한 AI 프롬프트가 있어 6개 관점 모두 테스트 가능
- **방법**: 6개 관점 프롬프트 모두 V0-STEP-1 범위로 한정 실행
- **검증**: 결과 전수 수동 확인. FP가 발견되면 해당 프롬프트 교정

## [Val-2] V1-Phase 1 (line 1381-1451, 71줄)

- **이유**: V1은 AI 프롬프트가 없는 유일한 형식. 관점 C의 V1 체크리스트 작동 확인
- **방법**: 관점 B, C, E 프롬프트 실행
- **검증**: V1-1~V1-4 체크리스트가 정상 적용되는지, 칼럼 비일관(6열 vs 5열) 감지 여부

## [Val-3] V2-Phase 1 (line 1717-1878, 162줄)

- **이유**: V0에 없는 패턴 (마이그레이션 스크립트, COND 모듈, Docker 배포) 검증
- **방법**: 관점 A, B, C, F 프롬프트 실행
- **검증**: V2 전용 패턴에서 FP 발생 여부

## [Val-4] §6.1 UI/UX (line 2705-2807, 103줄)

- **이유**: §6은 18 Stage 밖의 영역. RULE-11 작동 확인 + §6.1 "~85" vs §6.13 "~135" 감지 여부
- **방법**: 관점 C, E 프롬프트 실행
- **검증**: §6 고유 정의(UI SM 9-state, React ~44 상세)가 관점 C에서 올바르게 평가되는지

## [Val-N] 음성 대조군 (Negative Test)

- **이유**: FP 0건만으로는 프롬프트가 "맹목"인지 "정확"인지 구분 불가
- **방법**:
  1. PART2 v20.4.0의 **복사본** 생성
  2. 의도적 오류 6건 삽입 (관점당 1건):
     - A: STEP-4가 STEP-6의 산출물을 전제하는 문구 삽입
     - B: 존재하지 않는 경로 `backend/vamos_core/phantom/module.py` 삽입
     - C: AI 프롬프트에서 핵심 파라미터(StateGraph 키) 삭제
     - D: STEP-3 산출물 목록에서 `python_manager.rs` 삭제
     - E: V1 활성 모듈 수를 32 → 35로 변경
     - F: 존재하지 않는 라이브러리 `phantom-ml>=1.0` 삽입
  3. 6개 프롬프트를 오류 삽입 문서에 실행
  4. 6건 모두 감지되면 PASS. 미감지 건이 있으면 해당 프롬프트 교정

**Val 전체 통과 기준**: Val-1~4 FP 0건 + Val-N 6/6 감지 = Phase 1 진입 가능

---

# 9. Phase 1: 전수 실행

> **목적**: PART2 전문에 대해 6개 관점 전수 검증
> **전제**: Phase 0-Validate 통과
> **구조**: 3-Wave (의존성 기반)

## Wave 1: v9-B (파일 경로) + v9-E (수량 일관성)

**이유**: 기계적 비교, 팩트 기반. 결과가 Wave 2의 입력이 됨
**실행 방법**:
- v9-B: GT-1 기준으로 PART2 전문 경로 검증
- v9-E: GT-3 기준으로 PART2 전문 수량 검증
- 병렬 실행 가능 (상호 독립)

**예상 검증 항목 수**: B ~80건, E ~200건 = ~280건
**Wave 1 Checkpoint**: REAL_ERROR 전수 식별 + FP 판별

## Wave 2: v9-A (의존성 순서) + v9-D (누적 산출물)

**이유**: Wave 1 결과(경로/수량 확인)가 A/D의 입력이 됨
**실행 방법**:
- v9-A: GT-2 기준으로 18 Stage + §6 횡단 + §7 GO/NO-GO 의존성 검증
- v9-D: GT-2 기준으로 산출물 체인 추적
- Wave 1에서 경로 오류가 발견되었다면 A/D에서 해당 경로의 의존성도 재확인
- 병렬 실행 가능 (A와 D는 같은 GT-2를 사용하지만 검증 관점이 다름)

**예상 검증 항목 수**: A ~86건, D ~50건 = ~136건
**Wave 2 Checkpoint**: REAL_ERROR 전수 식별 + FP 판별

## Wave 3: v9-F (외부 의존성) + v9-C (구현 가능성)

**이유**: 가장 판단이 필요한 영역. Wave 1-2가 깨끗해야 의미 있음
**실행 방법**:
- v9-F: GT-4 기준으로 94개 라이브러리 실현성 검증
- v9-C: GT-5 기준으로 12개 AI 프롬프트 + 77개 V1 테이블 행 + §6 상세 검증
- v9-C는 범위가 넓으므로 분할 실행:
  - C-1: V0 (6 STEP)
  - C-2: V1 (6 Phase)
  - C-3: V2 (3 Phase)
  - C-4: V3 (3 Phase)
  - C-5: §6 (13개 하위 섹션)

**예상 검증 항목 수**: F ~97건, C ~150건 = ~247건
**Wave 3 Checkpoint**: REAL_ERROR 전수 식별 + FP 판별

## 각 Wave Checkpoint 판정 기준

| 항목 | 기준 |
|------|------|
| REAL_ERROR 전수 식별 | 모든 발견 항목에 REAL_ERROR / FALSE_POSITIVE / STYLE_CONCERN 판정 |
| FP 오판율 | ≤ 10% (Val-N에서 프롬프트 교정 완료 전제) |
| Severity 분류 | 각 REAL_ERROR에 BLOCKER / HIGH / MEDIUM / LOW 부여 |
| 다음 Wave 진입 조건 | Checkpoint 판정 완료 (수정은 Phase 2에서 일괄) |

---

# 10. Phase 2: 수정 + 재검증

> **목적**: Phase 1에서 발견된 REAL_ERROR 전수 수정 + 재검증
> **전제**: Phase 1 Wave 1~3 Checkpoint 완료

## Phase 2-A: Ripple Map + PART2 수정

v8과 동일한 패턴:

1. **Ripple Map 작성**
   - 각 REAL_ERROR의 수정 대상 값(old/new) 전수 식별
   - PART2 전문에서 해당 값의 모든 변형을 grep
   - 영향 위치(줄 번호) 전수 매핑

2. **PART2 수정 실행**
   - 수정 ID (FIX-01, FIX-02, ...) 부여
   - Severity별 우선순위: BLOCKER → HIGH → MEDIUM → LOW
   - 각 수정에 정본 근거(SOT 문서+섹션) 명기
   - PART2 버전 v20.4.0 → v21.0.0으로 갱신

3. **SOURCE_CONFLICT 처리**
   - 정본 간 충돌이 발견된 경우 HTML 주석으로 기록
   - §7.5.5 SOURCE_CONFLICT 인덱스에 추가 (SC-13~)

## Phase 2-B: GT 재구축 (약점 #25 대응)

**PART2 수정 후 반드시 수행**:
1. GT-1: 수정된 경로가 있으면 재추출
2. GT-2: 수정된 의존성/전환조건이 있으면 재구축
3. GT-3: 수정된 수량이 있으면 재인덱싱
4. GT-4/GT-5: 수정된 기술 스택/프롬프트가 있으면 재구축

## Phase 2-C: Phase 1 재실행

1. 수정된 PART2 v21.0.0 + 재구축된 GT로 Phase 1 (Wave 1~3) 재실행
2. REAL_ERROR 0건 확인
3. 잔존 FP 확인 (v8 Phase 2-B와 동일)

## Phase 2-D: Final Checkpoint

| # | 조건 | 기준 |
|---|------|------|
| 1 | Wave 1 (B+E) | REAL_ERROR 0건 |
| 2 | Wave 2 (A+D) | REAL_ERROR 0건 |
| 3 | Wave 3 (F+C) | REAL_ERROR 0건, BLOCKER 0건 |
| 4 | FP 오판율 | ≤ 10% |
| 5 | Ripple 완전성 | 전수 수정 + 재실행 PASS |
| 6 | GT 재구축 | 수정 반영 완료 |
| 7 | v8 호환성 | v8 Phase 0 재실행 PASS (Phase -1H 이후 잔존 0건) |
| 8 | 보고서 | 최종 검증 보고서 작성 완료 |

**8/8 PASS → v9 Pipeline 완료 → PART2 구현 착수 가능**

---

# 11. 판정 기준

## 발견 항목 분류

| 분류 | 코드 | 의미 | 조치 |
|------|------|------|------|
| 실제 오류 | **RE** (REAL_ERROR) | PART2 수정 필요 | Phase 2에서 수정 |
| 오탐 | **FP** (FALSE_POSITIVE) | 프롬프트/GT의 한계로 인한 오판 | 무시, 프롬프트 교정 |
| 스타일 우려 | **SC** (STYLE_CONCERN) | 오류는 아니지만 개선 권장 | 선택적 수정 |

## Severity 등급

| 등급 | 기준 | 예시 |
|------|------|------|
| **BLOCKER** | 구현 불가 또는 런타임 오류 | 순환 의존성, 필수 파라미터 누락, 존재하지 않는 라이브러리 |
| **HIGH** | 구현은 가능하나 결과가 SOT와 불일치 | 파일 경로 불일치, LOCK 수치 불일치, V 범위 오류 |
| **MEDIUM** | 구현에 영향은 적으나 혼란 유발 | 근사치 범위 초과, 칼럼 비일관, 구현 가이드 모호 |
| **LOW** | 미관/일관성 문제 | 표기 불통일, 순서 이상, 불필요한 중복 |

---

# 12. 입출력 파일 인덱스

## 입력 파일

| 파일 | 위치 | 용도 |
|------|------|------|
| PART2 v20.4.0 | `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` | 검증 대상 문서 |
| PHASE_B_EXHAUSTIVE_ANALYSIS.md | `D:\VAMOS\docs\sot\` (이동 후) | SOT 기준: 구조, 의존성, 기술 스택 |
| CLAUDE.md | `D:\VAMOS\docs\sot\` (이동 후) | SOT 기준: 아키텍처, LOCK 값 |
| D2.0-04_INFRA_CORE.md | `D:\VAMOS\docs\sot\` | SOT 기준: 인프라, I-Series |
| D2.0-07_SAFETY_COST_APPROVAL.md | `D:\VAMOS\docs\sot\` | SOT 기준: 안전, 비용, 승인 |
| D2.0-08_UI_UX.md | `D:\VAMOS\docs\sot\` | SOT 기준: UI/UX |
| v8 Phase 0 스크립트 | `D:\VAMOS\04. 구현단계\v8_results\phase0\` | Phase -1H 재실행용 |
| v8 Phase 0 결과 | `D:\VAMOS\04. 구현단계\v8_results\phase0\*.json` | 기존 검증 결과 참조 |

## 산출물 파일 — Phase별 상세 저장 경로

> **기본 경로**: `D:\VAMOS\04. 구현단계\v9_results\`

### Phase -1: 기반 정비 (`v9_results\phase-1\`)

| # | 작업 | 산출물 파일명 | 전체 경로 |
|---|------|-------------|----------|
| -1A | SOT 파일명 매핑 | `v9_sot_mapping.json` | `D:\VAMOS\04. 구현단계\v9_results\phase-1\v9_sot_mapping.json` |
| -1B | config 13/17 확정 | `v9_config_13vs17_verdict.md` | `D:\VAMOS\04. 구현단계\v9_results\phase-1\v9_config_13vs17_verdict.md` |
| -1C | 허용 목록 | `v9_allowlist.json` | `D:\VAMOS\04. 구현단계\v9_results\phase-1\v9_allowlist.json` |
| -1D | §6-§7 교차 인덱스 | `v9_cross_section_index.json` | `D:\VAMOS\04. 구현단계\v9_results\phase-1\v9_cross_section_index.json` |
| -1E | GO/NO-GO ↔ Gate 매핑 | `v9_gate_mapping.json` | `D:\VAMOS\04. 구현단계\v9_results\phase-1\v9_gate_mapping.json` |
| -1F | changelog 제외 범위 | `v9_changelog_exclude_range.md` | `D:\VAMOS\04. 구현단계\v9_results\phase-1\v9_changelog_exclude_range.md` |
| -1G | SOT 안정 경로 이동 | `v9_phase-1g_sot_copy_report.md` | `D:\VAMOS\04. 구현단계\v9_results\phase-1\v9_phase-1g_sot_copy_report.md` |
| -1H | v8 Phase 0 재실행 | `v9_phase-1h_v8_rerun_report.md` | `D:\VAMOS\04. 구현단계\v9_results\phase-1\v9_phase-1h_v8_rerun_report.md` |
| -1I | v9 범위 정의 | `v9_scope_definition.md` | `D:\VAMOS\04. 구현단계\v9_results\phase-1\v9_scope_definition.md` |

> Phase -1 산출물 합계: **8개 파일** + SOT 복사 12개

### Phase 0-Pre: Ground Truth 구축 (`v9_results\phase0\`)

| # | GT | 산출물 파일명 | 전체 경로 |
|---|-----|-------------|----------|
| GT-1 | 파일 경로 레지스트리 | `gt1_file_path_registry.json` | `D:\VAMOS\04. 구현단계\v9_results\phase0\gt1_file_path_registry.json` |
| GT-2 | 산출물 체인 레지스트리 | `gt2_artifact_chain.json` | `D:\VAMOS\04. 구현단계\v9_results\phase0\gt2_artifact_chain.json` |
| GT-3 | 수량 인덱스 | `gt3_quantity_index.json` | `D:\VAMOS\04. 구현단계\v9_results\phase0\gt3_quantity_index.json` |
| GT-4 | 외부 의존성 레지스트리 | `v9_dependency_registry.json` | `D:\VAMOS\04. 구현단계\v9_results\phase0\v9_dependency_registry.json` |
| GT-5 | 구현 가능성 체크리스트 | `v9_implementability_checklist.json` | `D:\VAMOS\04. 구현단계\v9_results\phase0\v9_implementability_checklist.json` |

> Phase 0-Pre 산출물 합계: **5개 파일** (GT-1~GT-5)

### Phase 0: 프롬프트 작성 (`v9_results\phase0\`)

| # | 관점 | 산출물 파일명 | 전체 경로 |
|---|------|-------------|----------|
| P-A | 의존성 순서 | `v9_prompt_A_dependency.md` | `D:\VAMOS\04. 구현단계\v9_results\phase0\v9_prompt_A_dependency.md` |
| P-B | 파일 경로 정합성 | `v9_prompt_B_path.md` | `D:\VAMOS\04. 구현단계\v9_results\phase0\v9_prompt_B_path.md` |
| P-C | 구현 가능성 | `v9_prompt_C_implementability.md` | `D:\VAMOS\04. 구현단계\v9_results\phase0\v9_prompt_C_implementability.md` |
| P-D | 누적 산출물 추적 | `v9_prompt_D_artifact.md` | `D:\VAMOS\04. 구현단계\v9_results\phase0\v9_prompt_D_artifact.md` |
| P-E | 수량 일관성 | `v9_prompt_E_quantity.md` | `D:\VAMOS\04. 구현단계\v9_results\phase0\v9_prompt_E_quantity.md` |
| P-F | 외부 의존성 실현성 | `v9_prompt_F_feasibility.md` | `D:\VAMOS\04. 구현단계\v9_results\phase0\v9_prompt_F_feasibility.md` |

> Phase 0 산출물 합계: **6개 파일** (프롬프트 A~F)

### Phase 0-Validate: 시범 실행 (`v9_results\phase0-val\`)

| # | 테스트 | 산출물 파일명 | 전체 경로 |
|---|--------|-------------|----------|
| Val-1 | V0-STEP-1 시범 | `val1_v0_step1_results.json` | `D:\VAMOS\04. 구현단계\v9_results\phase0-val\val1_v0_step1_results.json` |
| Val-2 | V1-Phase 1 시범 | `val2_v1_phase1_results.json` | `D:\VAMOS\04. 구현단계\v9_results\phase0-val\val2_v1_phase1_results.json` |
| Val-3 | V2-Phase 1 시범 | `val3_v2_phase1_results.json` | `D:\VAMOS\04. 구현단계\v9_results\phase0-val\val3_v2_phase1_results.json` |
| Val-4 | §6.1 시범 | `val4_s6_1_uiux_results.json` | `D:\VAMOS\04. 구현단계\v9_results\phase0-val\val4_s6_1_uiux_results.json` |
| Val-N | 음성 대조군 | `valN_negative_test_results.json` | `D:\VAMOS\04. 구현단계\v9_results\phase0-val\valN_negative_test_results.json` |
| — | Val 종합 판정 | `phase0_validate_report.md` | `D:\VAMOS\04. 구현단계\v9_results\phase0-val\phase0_validate_report.md` |

> Phase 0-Val 산출물 합계: **6개 파일** (Val-1~4 + Val-N + 종합 보고서)

### Phase 1: 전수 실행 (`v9_results\phase1\`)

| # | Wave | 산출물 파일명 | 전체 경로 |
|---|------|-------------|----------|
| W1-B | Wave 1 파일 경로 | `wave1_v9B_path_results.json` | `D:\VAMOS\04. 구현단계\v9_results\phase1\wave1_v9B_path_results.json` |
| W1-E | Wave 1 수량 일관성 | `wave1_v9E_quantity_results.json` | `D:\VAMOS\04. 구현단계\v9_results\phase1\wave1_v9E_quantity_results.json` |
| W1-CP | Wave 1 체크포인트 | `wave1_checkpoint_report.md` | `D:\VAMOS\04. 구현단계\v9_results\phase1\wave1_checkpoint_report.md` |
| W2-A | Wave 2 의존성 순서 | `wave2_v9A_dependency_results.json` | `D:\VAMOS\04. 구현단계\v9_results\phase1\wave2_v9A_dependency_results.json` |
| W2-D | Wave 2 누적 산출물 | `wave2_v9D_artifact_results.json` | `D:\VAMOS\04. 구현단계\v9_results\phase1\wave2_v9D_artifact_results.json` |
| W2-CP | Wave 2 체크포인트 | `wave2_checkpoint_report.md` | `D:\VAMOS\04. 구현단계\v9_results\phase1\wave2_checkpoint_report.md` |
| W3-F | Wave 3 외부 의존성 | `wave3_v9F_feasibility_results.json` | `D:\VAMOS\04. 구현단계\v9_results\phase1\wave3_v9F_feasibility_results.json` |
| W3-C | Wave 3 구현가능성 (통합) | `wave3_v9C_implementability_results.json` | `D:\VAMOS\04. 구현단계\v9_results\phase1\wave3_v9C_implementability_results.json` |
| W3-CP | Wave 3 체크포인트 | `wave3_checkpoint_report.md` | `D:\VAMOS\04. 구현단계\v9_results\phase1\wave3_checkpoint_report.md` |
| — | 최종 보고서 | `phase1_final_report.md` | `D:\VAMOS\04. 구현단계\v9_results\phase1\phase1_final_report.md` |

> Phase 1 산출물 합계: **10개 파일** (관점별 결과 6개 + 체크포인트 3개 + 최종 보고서 1개)
> **참고**: §9 v9-C 분할(C1~C5) 대신 단일 통합 파일로 실행 (내부 V0/V1/V2/V3/§6 분할 포함)

### Phase 2: 수정 + 재검증 (`v9_results\phase2\`)

| # | 단계 | 산출물 파일명 | 전체 경로 |
|---|------|-------------|----------|
| 2-A | Ripple Map + FIX 기록 | `v9_phase2_ripple_map.md` | `D:\VAMOS\04. 구현단계\v9_results\phase2\v9_phase2_ripple_map.md` |
| 2-B~D | 최종 보고서 (GT 재구축 + 재실행 + 8/8 체크포인트) | `v9_phase2_final_report.md` | `D:\VAMOS\04. 구현단계\v9_results\phase2\v9_phase2_final_report.md` |

> Phase 2 산출물 합계: **2개 파일** (Ripple Map+FIX 1개 + 최종 보고서 1개)
> **참고**: §10 설계 5개 파일 대신 2개로 통합 실행 (Ripple Map에 FIX 기록 포함, 최종 보고서에 GT 재구축·재실행·체크포인트 포함)

### 산출물 총계

| Phase | 파일 수 | 저장 디렉토리 |
|-------|--------|-------------|
| Phase -1 | 8 (+SOT 12) | `v9_results\phase-1\` + `docs\sot\` |
| Phase 0-Pre | 5 | `v9_results\phase0\` |
| Phase 0 | 6 | `v9_results\phase0\` |
| Phase 0-Val | 6 | `v9_results\phase0-val\` |
| Phase 1 | 10 | `v9_results\phase1\` |
| Phase 2 | 2 | `v9_results\phase2\` |
| **합계** | **37개** (+SOT 12) | — |

## 전체 파이프라인 흐름도

```
Phase -1 (기반 정비, 9개 작업)
  │
  ├── [-1A] SOT 매핑 ──────────────────────┐
  ├── [-1B] config 13/17 확정 ─────────────┤
  ├── [-1C] 허용 목록 ─────────────────────┤
  ├── [-1D] §6-§7 교차 인덱스 ─────────────┤
  ├── [-1E] GO/NO-GO ↔ Stage Gate 매핑 ────┤
  ├── [-1F] changelog 제외 범위 ───────────┤
  ├── [-1G] SOT 안정 경로 이동 ────────────┤
  ├── [-1H] v8 Phase 0 재실행 ─────────────┤
  └── [-1I] v9 범위 정의 ─────────────────┤
                                            │
                                            ▼
Phase 0-Pre (GT 구축, 5개 파일)
  │
  ├── [GT-1] 파일 경로 레지스트리 ──────────┤ ← [-1C] 허용목록
  ├── [GT-2] 산출물 체인 + 횡단 의존성 ────┤ ← [-1E] 매핑
  ├── [GT-3] 수량 인덱스 ──────────────────┤ ← [-1B] 확정, [-1D] 교차
  ├── [GT-4] 외부 의존성 94개 ─────────────┤ ← [-1A] SOT 매핑
  └── [GT-5] 구현 가능성 체크리스트 ────────┤ ← SOT 문서 (순환 방지)
                                            │
                                            ▼
Phase 0 (프롬프트 작성, 6개)
  │
  ├── v9-A (의존성 순서) ← GT-2 + RULE-1,2,3,7,9,11,14
  ├── v9-B (파일 경로) ← GT-1 + RULE-1,2,5,6,9,11,14
  ├── v9-C (구현 가능성) ← GT-5 + RULE-2,4,5,8,9,11,14
  ├── v9-D (누적 산출물) ← GT-2 + RULE-1,2,7,9,11,14
  ├── v9-E (수량 일관성) ← GT-3 + RULE-2,3,5,8,11,12,13,14
  └── v9-F (외부 의존성) ← GT-4 + RULE-2,6,10,11,14
                                            │
                                            ▼
Phase 0-Validate (시범 실행, 5개 테스트)
  │
  ├── [Val-1] V0-STEP-1 (372줄) — 정상 FP 검증
  ├── [Val-2] V1-Phase 1 (71줄) — 테이블 형식
  ├── [Val-3] V2-Phase 1 (162줄) — 마이그레이션 패턴
  ├── [Val-4] §6.1 (103줄) — §6 검증
  └── [Val-N] 음성 대조군 (6건 오류 삽입) — FN 검증
                                            │
                    Val 통과 (FP=0 + FN=0)  │
                                            ▼
Phase 1 (전수 실행, 3-Wave)
  │
  ├── Wave 1: v9-B + v9-E (~280건) ─── Checkpoint ─┐
  ├── Wave 2: v9-A + v9-D (~136건) ─── Checkpoint ─┤
  └── Wave 3: v9-F + v9-C (~247건) ─── Checkpoint ─┤
                                                     │
                                                     ▼
Phase 2 (수정 + 재검증)
  │
  ├── [2-A] Ripple Map + PART2 수정 (v20.4.0 → v21.0.0)
  ├── [2-B] GT 재구축 (수정 반영)
  ├── [2-C] Phase 1 재실행 (RE 0건 확인)
  └── [2-D] Final Checkpoint (8/8 PASS)
                    │
                    ▼
        PART2 v21.0.0 구현 착수 가능
```

---

> **END OF v9 PIPELINE PLAN**