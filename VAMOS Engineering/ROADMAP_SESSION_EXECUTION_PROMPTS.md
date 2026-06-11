# VAMOS 로드맵 세션 실행 프롬프트

> **작성일**: 2026-04-04
> **목적**: 최종 로드맵 Phase 0~6의 각 세션을 실행할 때 복사/붙여넣기로 사용하는 프롬프트 모음
> **구조 참조**: SOT2_SESSION_EXECUTION_PROMPTS.md Phase 13~14 + 실제 사용 대본 8단계 흐름
> **사용법**: 해당 세션 착수 시 프롬프트를 복사 → Claude Code에 붙여넣기 → 실행

---

## 목차

1. [Phase 0: 자산 인벤토리 + 전체 그림 확정](#1-phase-0)
2. [Phase 1: SOT 2 완성 + D1 검증](#2-phase-1)
3. [Phase 2: 보강/생성 + 환경 세팅](#3-phase-2)
4. [Phase 3: 런타임 설계 + 횡단 전략](#4-phase-3)
5. [Phase 4: V0 구현](#5-phase-4)
6. [Phase 5: V0 검증 + GO/NO-GO](#6-phase-5)
7. [Phase 6: V1 구현](#7-phase-6)
8. [진행 상태 추적 테이블](#8-진행-상태-추적-테이블)

---

## 1. Phase 0

### 세션 P0-1: 자산 인벤토리 확정 + Git 확인 (0-0, 0-6)

**로드맵 작업 매핑:**

| # | 작업 | 상세 | 우선순위 | 병렬 | 산출물 |
|---|------|------|---------|------|--------|
| 0-0 | 자산 인벤토리 | 전체 폴더/파일 역할, 매트릭스 셀 매핑, 중복/미사용 식별 | **Must** | ✓ | STRATEGY_11 |
| 0-6 | Git + 리스크 | GitHub remote 확인 + 리스크 15건 검토 | **Must** | ✓ | 환경 확인 |

````
VAMOS 로드맵 Phase 0, 세션 P0-1 — 자산 인벤토리 확정 + Git 확인

■ 대상: 0-0(자산 인벤토리 확정, Must) + 0-6(Git remote + 리스크 검토, Must)

■ 참조 (반드시 먼저 읽기):
  D:\VAMOS\VAMOS Engineering\STRATEGY_11_ASSET_INVENTORY.md — 기존 인벤토리 확인
  D:\VAMOS\VAMOS Engineering\STRATEGY_01_FAILURE_AND_RISK.md §4.3 — 리스크 15건
  D:\VAMOS\VAMOS_최종_로드맵.md — Phase 0 섹션

■ STEP 1: 프롬프트 자체 검증 (실행 전 필수)
  a. 본 프롬프트의 작업이 로드맵 Phase 0의 0-0, 0-6 목표와 일치하는지 확인
  b. 본 프롬프트의 산출물이 로드맵 Phase 0 완료 조건과 일치하는지 확인
  c. 본 프롬프트의 참조 파일이 실제 존재하는지 Read로 확인
  d. 불일치/누락 발견 시 → 프롬프트 수정 → 재확인 → 반복
  e. "프롬프트 최종 확정" 선언 → PASS 후에만 STEP 2 진행

■ STEP 2: 작업 실행
  1. STRATEGY_11(자산 인벤토리) 최종 확인:
     - §1 전체 구조 맵: 현재 폴더 구조와 일치?
     - §2 폴더별 상세: 파일 수, 역할 정확?
     - §3 용도별 분류: D1/Phase4/Phase5 등 사용 파일 목록 정확?
     - §4 매트릭스 셀별 매핑: 20개 셀 전부 매핑?
     - §5 중복/미사용: 식별 결과 유효?
     - 불일치 → 즉시 수정
  2. Git remote 확인 (A2):
     - git remote -v → GitHub 연결 확인
     - 연결 안 됨 → git remote add origin {url}
     - git tag phase0-start → 시작 태그
  3. 리스크 15건 검토 (A15):
     - STRATEGY_01 §4.3 리스크 레지스터 15건 읽기
     - 현재 시점에 발생 가능한 위험 식별
  4. PROGRESS.md 초기 생성 (A5):
     - D:\VAMOS\VAMOS Engineering\PROGRESS.md 파일 생성
     - 현재: Phase 0-P0-1 시작 / 완료: 없음 / 다음: P0-2

■ STEP 3: 산출물 검증 (더 이상 수정 없을 때까지 반복)
  a. STRATEGY_11이 현재 폴더 구조와 100% 일치?
  b. Git remote 연결 확인?
  c. PROGRESS.md 생성 확인?
  d. 미세한 부분까지 확인 → 수정 필요 시 수정 → 재검증
  e. "산출물 최종 확정" 선언

■ STEP 4: 관련 문서 갱신
  - STRATEGY_11 갱신 (불일치 수정 시)
  - PROGRESS.md 갱신 (P0-1 완료 기록)

■ STEP 5: 갱신 결과 검증
  - 갱신된 STRATEGY_11이 다른 STRATEGY 파일과 모순 없는지 확인
  - PROGRESS.md 포맷이 STRATEGY_03 §2.2 규격과 일치하는지 확인

■ PASS 조건: 인벤토리 현행화 + Git 연결 + PROGRESS.md 존재 + 산출물 확정 + 갱신 검증 완료
````

---

### 세션 P0-2: CLAUDE.md + Obsidian 구조 확정 (0-1, 0-2)

**로드맵 작업 매핑:**

| # | 작업 | 상세 | 우선순위 | 병렬 | 산출물 |
|---|------|------|---------|------|--------|
| 0-1 | CLAUDE.md 구조 확정 | §1~§27 + §28 매트릭스 참조 | Should | ✓ | 구조 명세 |
| 0-2 | Obsidian 매트릭스 연결 | 120+ 노트가 매트릭스 어느 셀인지 | Should | ✓ | 매핑 문서 |

````
VAMOS 로드맵 Phase 0, 세션 P0-2 — CLAUDE.md + Obsidian 구조 확정

■ 대상: 0-1(CLAUDE.md 최종 구조, Should) + 0-2(Obsidian 매트릭스 연결, Should)

■ 참조 (반드시 먼저 읽기):
  D:\VAMOS\CLAUDE 보강전략 V1.0.md — §3 보강 대상, §5 신규 섹션
  D:\VAMOS\VAMOS HOME\OBSIDIAN-STRATEGY-v3.md — §2~§6 구조/템플릿
  D:\VAMOS\VAMOS Engineering\STRATEGY_08_ENGINEERING_MATRIX.md — 매트릭스 셀 정의

■ STEP 1: 프롬프트 자체 검증 (실행 전 필수)
  a. 본 프롬프트의 작업이 로드맵 Phase 0의 0-1, 0-2 목표와 일치하는지 확인
  b. 보강전략 §3, §5 구조가 본 프롬프트 작업과 일치하는지 확인
  c. Obsidian Strategy v3.0의 폴더 구조가 본 프롬프트의 매핑 대상과 일치하는지 확인
  d. 불일치/누락 발견 시 → 프롬프트 수정 → 재확인 → 반복
  e. "프롬프트 최종 확정" 선언 → PASS 후에만 STEP 2 진행

■ STEP 2: 작업 실행
  1. CLAUDE.md 최종 구조 확정:
     - 보강전략 §3에서 기존 §1~§20 수정 범위 확인
     - 보강전략 §5에서 신규 §21~§27 구조 확인
     - §28 "엔지니어링 프레임워크" 구조 정의:
       → 매트릭스 위치, PROGRESS.md 참조, Phase별 컨텍스트 테이블 (STRATEGY_03 §4.2)
     - 산출물: "CLAUDE.md 구조 명세" (§1~§28 목차 + 각 섹션 역할 + 줄 수 예상)
  2. Obsidian 전략과 매트릭스 연결:
     - Strategy v3.0 §3 (17개 폴더 구조) → 매트릭스 셀 매핑:
       00_HUB → 전체 참조 / 01_GOVERNANCE → D1(T0) / 12_IMPLEMENTATION → 매트릭스 노트 / 14_AUDIT → D1/D3 검증
     - 산출물: "Obsidian-매트릭스 매핑" (17개 폴더 × 해당 매트릭스 셀)
  3. 설계 자산 전체 맵 문서화:
     - [원본] SOT + SOT 2 → D행 / [요약] CLAUDE.md → B1, B2b / [KG] Obsidian → X1 / [엔지니어링] STRATEGY → 전체

■ STEP 3: 산출물 검증 (더 이상 수정 없을 때까지 반복)
  a. CLAUDE.md §1~§28 구조가 빠짐없는지?
  b. Obsidian 17개 폴더가 전부 매트릭스 셀에 매핑되었는지?
  c. 설계 자산 전체 맵에서 누락된 자산이 없는지?
  d. 미세한 부분까지 확인 → 수정 필요 시 수정 → 재검증
  e. "산출물 최종 확정" 선언

■ STEP 4: 관련 문서 갱신
  - PROGRESS.md 갱신 (P0-2 완료 기록)
  - STRATEGY_11 갱신 (신규 산출물 3개 파일 등록, 필요 시)

■ STEP 5: 갱신 결과 검증
  - 갱신된 문서가 P0-1 산출물과 모순 없는지 확인
  - 설계 자산 전체 맵이 STRATEGY_08 매트릭스 §1과 정합하는지 확인

■ PASS 조건: 3개 산출물 확정 + 갱신 검증 완료
````

---

### 세션 P0-3: 매트릭스 v1.1 갱신 (0-3)

**로드맵 작업 매핑:**

| # | 작업 | 상세 | 우선순위 | 병렬 | 산출물 |
|---|------|------|---------|------|--------|
| 0-3 | 매트릭스 v1.1 | 미연동 8건 해소 + 설계 자산 전체 맵 + 25건 관점 반영 | **Must** | ✓ | STRATEGY_08 v1.1 |

````
VAMOS 로드맵 Phase 0, 세션 P0-3 — 매트릭스 v1.1 갱신

■ 대상: 0-3(매트릭스 갱신 — 미연동 8건 해소 + 25건 관점 반영, Must)

■ 참조 (반드시 먼저 읽기):
  D:\VAMOS\VAMOS Engineering\STRATEGY_08_ENGINEERING_MATRIX.md — 현재 v1.0
  P0-2 산출물 — CLAUDE.md 구조 명세, Obsidian 매핑, 설계 자산 전체 맵

■ STEP 1: 프롬프트 자체 검증
  a. 미연동 8건 목록 확인: Obsidian, 로드맵, 검증 체계, GO/NO-GO, PART1, 보강전략, LOCK Registry, 5개 계획서
  b. 25건 관점(A1~A25) 중 매트릭스 셀에 반영해야 할 항목 확인: R2a(A21,A22,A25), X1(A16), B2b(A13)
  c. P0-2 산출물 3개가 존재하는지 확인
  d. 불일치 시 → 수정 → 재확인 → "프롬프트 최종 확정"

■ STEP 2: 작업 실행
  1. STRATEGY_08 갱신:
     - §1 "설계 자산 전체 맵" 추가 (P0-2 산출물)
     - D1 셀: CLAUDE.md 검증 + Obsidian 전략 정합 추가
     - B1 셀: CLAUDE.md 보강 상세 반영 (§28 포함)
     - B2b 셀: Phase별 컨텍스트 프로토콜(A13) 반영
     - R2a 셀: A21(Defense Layer), A22(reasoning_trace), A25(confidence_score) 반영
     - X1 셀: A16(책임 AI 체크리스트) 반영
     - 참조 문서 목록: 로드맵, 검증 체계, GO/NO-GO, PART1, STRATEGY 01~07 추가
  2. 미연동 8건 해소 확인: Grep으로 각 항목이 매트릭스에 참조되는지 1건씩 확인
  3. 버전 표기: v1.0 → v1.1

■ STEP 3: 산출물 검증 (반복)
  a. 미연동 8건 전부 매트릭스에 참조 확인
  b. A21/A22/A25가 R2a 셀에 반영 확인
  c. 로드맵, 검증 체계, PART1이 참조 문서에 포함 확인
  d. 미세한 부분 확인 → 수정 → 재검증 → "산출물 최종 확정"

■ STEP 4: 관련 문서 갱신
  - PROGRESS.md 갱신 (P0-3 완료)
  - STRATEGY_11(인벤토리) §2.7에 매트릭스 버전 갱신 반영

■ STEP 5: 갱신 결과 검증
  - 매트릭스 v1.1이 로드맵 참조 문서 맵과 일치하는지 확인
  - 매트릭스 v1.1이 STRATEGY_01~07에서 참조하는 셀과 정합하는지 확인

■ PASS 조건: 미연동 0건 + 25건 해당 셀 반영 + v1.1 확정 + 갱신 검증 완료
````

---

### 세션 P0-4: Phase 0 Gate + 나머지 작업 (0-4, 0-5)

**로드맵 작업 매핑:**

| # | 작업 | 상세 | 우선순위 | 병렬 | 산출물 |
|---|------|------|---------|------|--------|
| 0-4 | 5개 계획서 목차 | ②설계정합 ③런타임 ④다중스택 ⑤횡단 ⑥운영 | Could | ✓ | 목차 |
| 0-5 | 하네스 역참조 | STRATEGY_09 ↔ STRATEGY_08 양방향 | Could | ✓ | 갱신 |

````
VAMOS 로드맵 Phase 0, 세션 P0-4 — Phase 0 Gate

■ 대상: 0-4(5개 계획서 목차, Could) + 0-5(하네스 역참조, Could) + Phase 0 완료 검증

■ 참조:
  D:\VAMOS\VAMOS_최종_로드맵.md — Phase 0 검증 체크리스트
  D:\VAMOS\VAMOS Engineering\STRATEGY_09_HARNESS_ENGINEERING.md

■ STEP 1: 프롬프트 자체 검증
  a. Phase 0 완료 조건(0-V)이 로드맵과 일치하는지 확인
  b. "프롬프트 최종 확정"

■ STEP 2: 작업 실행
  1. 5개 계획서 범위/목차 (Could):
     - ②설계정합: D2, D3, DF / ③런타임: R1, R2a, R2b, RF / ④다중스택: B2c, R2c / ⑤횡단: X1~X3, XF / ⑥운영: R3
  2. 하네스 역참조 (Could):
     - STRATEGY_09 하단에 "본 계획서는 매트릭스 D1+B행에 해당" 명시
  3. Phase 0 완료 검증 (0-V — 로드맵과 1:1 일치):
     - □ 자산 인벤토리 완성 (STRATEGY_11)?
     - □ 매트릭스 v1.1 갱신 완료 (미연동 8건 해소)?
     - □ Git remote 연결 + git tag phase0-complete?
     - □ 리스크 15건 검토 완료?
     - □ PROGRESS.md 초기 생성?
     추가 확인 (로드맵 0-V 확장):
     - □ 매트릭스 20개 셀 전체 커버? □ CLAUDE.md/Obsidian 역할 명시?
     - □ 613건 거버넌스 Phase 매핑? □ Phase 순서 의존관계 일치?
  4. Phase 0 회고 (A11):
     - 잘된 것 3 / 안된 것 3 / 바꿀 것 1 → decisions/phase0_retro.md

■ STEP 3: 산출물 검증 (반복)
  a. 0-V 체크리스트 전항목 ☑?
  b. 회고 파일 존재?
  c. 미세한 부분 확인 → 수정 → "산출물 최종 확정"

■ STEP 4: 관련 문서 갱신
  - PROGRESS.md 갱신 (Phase 0 완료)
  - git tag phase0-complete
  - 로드맵 대조 (A12): Phase 1 내용이 현실과 맞는지 확인 → 3건+ 불일치 시 갱신

■ STEP 5: 갱신 결과 검증
  - git tag 존재 확인
  - PROGRESS.md가 Phase 0 완료 상태로 기록되었는지

■ 실패 시 (A1): 매트릭스 갱신 불가 → 모순 항목 PENDING 표시 + Phase 1 D1 결과로 해소

■ PASS 조건: 0-V 전항목 통과 + 회고 + git tag + 갱신 검증 → Phase 0 완료
````

---

## 2. Phase 1

### 세션 P1-0: 도구 사전 점검 + SOT 2 완성 확인

**로드맵 작업 매핑:**

| # | 작업 | 상세 | 우선순위 | 병렬 | 산출물 |
|---|------|------|---------|------|--------|
| 사전 | 도구 golden test | /sot-conflict, /sot2-cross-ref, /validate 동작 확인 (A7) | **Must** | - | 점검 결과 |
| 1-1 | SOT 2 완성 확인 | Must 5개 도메인 완성 여부 (A10) | **Must** | - | SOT 2 상태 |

````
VAMOS 로드맵 Phase 1, 세션 P1-0 — 도구 사전 점검 + SOT 2 완성 확인

■ 대상: 도구 golden test(A7, Must) + SOT 2 완성 여부(A10, Must)

■ 참조:
  D:\VAMOS\VAMOS Engineering\STRATEGY_04_TOOL_MAINTENANCE.md §3 — 스킬 의존맵
  D:\VAMOS\VAMOS Engineering\STRATEGY_02_SCOPE_AND_PRIORITY.md §3 — SOT 2 완성 정의

■ STEP 1: 프롬프트 자체 검증
  a. 도구 점검 대상(3개 스킬)이 STRATEGY_04 §2 점검 목록과 일치하는지
  b. SOT 2 완성 기준이 STRATEGY_02 §3.1 (14-섹션 + LOCK + Authority Chain)과 일치하는지
  c. "프롬프트 최종 확정"

■ STEP 2: 작업 실행
  1. 검증 스킬 golden test (A7):
     - /sot-conflict scan → 실행 가능? 알려진 7건 감지?
     - /sot2-cross-ref all → 실행 가능?
     - /validate → DV-1~9 동작?
  2. SOT 2 완성 확인 (A10):
     - Must: T0~T2 핵심 5개 도메인 완성 여부 (14-섹션 + LOCK + Authority Chain)
     - Must 5개 미완성 → SOT 2 작업 계속 (Phase 1 대기)
     - Must 5개 완성 → P1-1 진입 가능

■ STEP 3: 산출물 검증 (반복)
  a. 3개 스킬 golden test 결과가 예상과 일치?
  b. SOT 2 Must 5개 도메인 각각의 완성 조건(14-섹션, LOCK, AC) 충족?
  c. "산출물 최종 확정"

■ STEP 4: 관련 문서 갱신
  - PROGRESS.md 갱신 (P1-0 완료)

■ STEP 5: 갱신 결과 검증
  - PROGRESS.md가 도구 점검 PASS + SOT 2 상태 기록

■ PASS 조건: 스킬 3개 golden test PASS + SOT 2 Must 5개 완성 확인
````

---

### 세션 P1-1: D1 핵심 검증 (1-2 ~ 1-5)

**로드맵 작업 매핑:**

| # | 작업 | 상세 | 우선순위 | 산출물 |
|---|------|------|---------|--------|
| 1-2 | SOT 내부 정합 | /sot-conflict scan | **Must** | sot_conflict_report.json |
| 1-3 | SOT↔SOT2 교차 | /sot-conflict sot2-vs-sot | **Must** | sot2_crossref_report.json |
| 1-4 | SOT2 내부 교차 | /sot2-cross-ref all | **Must** | sot2_internal_report.json |
| 1-5 | 구조+LOCK | /validate sot2-all | **Must** | sot2_validate_report.json |

````
VAMOS 로드맵 Phase 1, 세션 P1-1 — D1 핵심 검증

■ 대상: 1-2(SOT 내부) + 1-3(SOT↔SOT2) + 1-4(SOT2 내부) + 1-5(구조+LOCK) — 전부 Must

■ 참조:
  D:\VAMOS\VAMOS Engineering\STRATEGY_09_HARNESS_ENGINEERING.md §4 — SOT 하네스 파이프라인
  D:\VAMOS\VAMOS Engineering\STRATEGY_10_VERIFICATION_SYSTEM.md §4 Phase 1 체크리스트

■ STEP 1: 프롬프트 자체 검증
  a. 실행할 스킬 4개가 하네스 §4 파이프라인 A/B와 일치하는지
  b. 산출물 파일명이 로드맵 Phase 1 산출물과 일치하는지
  c. PASS 조건이 로드맵 Phase 1 완료 조건과 일치하는지
  d. 불일치 시 → 수정 → "프롬프트 최종 확정"

■ STEP 2: 작업 실행
  1. /sot-conflict scan → SOT 68개 내부 모순 탐지 → sot_conflict_report.json
     CONFLICT 발견 시 → 정본 우선순위(RULE>PLAN>DESIGN LOCK)로 해소
  2. /sot-conflict sot2-vs-sot → SOT↔SOT2 교차 → sot2_crossref_report.json
     MISMATCH 발견 시 → SOT가 정본, SOT 2 수정
  3. /sot2-cross-ref all → SOT2 36개 도메인 교차 참조 → sot2_internal_report.json
  4. /validate sot2-all → SDV-1~7 + SDV-4 LOCK → sot2_validate_report.json
  5. 재현성 기록 (A17): 모든 결과에 timestamp + input_hash + skill_version

■ STEP 3: 산출물 검증 (더 이상 수정 없을 때까지 반복)
  a. CONFLICT 0건? (아니면 해소 후 재실행)
  b. MISMATCH 0건? (아니면 수정 후 재실행)
  c. 교차참조 무결?
  d. SDV PASS?
  e. 4개 리포트 JSON 파일 전부 존재 + 파싱 가능?
  f. 재현성 메타데이터(timestamp, hash) 기록 확인?
  g. 미세한 부분 확인 → 수정 → 재검증 → "산출물 최종 확정"

■ STEP 4: 관련 문서 갱신
  - PROGRESS.md 갱신 (P1-1 완료, CONFLICT/MISMATCH 수 기록)

■ STEP 5: 갱신 결과 검증
  - PROGRESS.md 기록이 실제 결과와 일치?

■ PASS 조건: CONFLICT 0건 + MISMATCH 0건 + 교차참조 무결 + SDV PASS + 산출물 확정
■ 실패 시 (A1): 핵심 5개 도메인 해소 불가 → 해당 도메인 제외 + V1 D1'에서 재검증
````

---

### 세션 P1-2: D1 보조 검증 + 기준선 + Gate (1-6 ~ 1-9)

**로드맵 작업 매핑:**

| # | 작업 | 상세 | 우선순위 | 산출물 |
|---|------|------|---------|--------|
| 1-6 | CLAUDE.md 검증 | /sot-check method-c → GAP 목록 | Should | claude_md_gap_report |
| 1-7 | Obsidian 정합 | 도메인 수/모듈 수 수동 대조 | Should | obsidian_gap_report |
| 1-8 | BLOCKER 재확인 | PART1 14건 변경 여부 | Should | blocker_log |
| 1-9 | 기준선 저장 | /integrity snapshot | **Must** | integrity_snapshot.json |

````
VAMOS 로드맵 Phase 1, 세션 P1-2 — D1 보조 검증 + 기준선 + Gate

■ 대상: 1-6~1-9 + Phase 1 완료 검증 + 인수인계

■ 참조:
  D:\VAMOS\CLAUDE.md — 현재 697줄
  D:\VAMOS\VAMOS HOME\OBSIDIAN-STRATEGY-v3.md
  D:\VAMOS\docs\guides\VAMOS_구현가이드_PART1_진입전.md — Section E.2

■ STEP 1: 프롬프트 자체 검증
  a. 1-6~1-9 작업이 로드맵과 일치하는지
  b. 인수인계 항목이 로드맵 "Phase 1→2 인수인계"와 일치하는지
  c. "프롬프트 최종 확정"

■ STEP 2: 작업 실행
  1. CLAUDE.md 검증 (1-6, Should):
     - /sot-check method-c → GAP 목록 → claude_md_gap_report
  2. Obsidian 전략 정합 (1-7, Should):
     - Strategy v3.0 도메인 수(36) vs SOT 2 최신 대조
     - 모듈 수(187) vs SOT 최신 대조 → obsidian_gap_report
  3. BLOCKER 재확인 (1-8, Should):
     - PART1 E.2 14건 → 2026-03-02 이후 변경으로 재발 여부
     - 재발 시 → 수정 → 1-8a(P1-1 해당 범위 재실행)
  4. 기준선 저장 (1-9, Must):
     - /integrity snapshot → integrity_snapshot.json

■ STEP 3: 산출물 검증 (반복)
  a. claude_md_gap_report 존재 + 내용 유효?
  b. obsidian_gap_report 존재 + 내용 유효?
  c. BLOCKER 14건 상태 확인 완료?
  d. integrity_snapshot.json 존재 + 해시값 유효?
  e. "산출물 최종 확정"

■ STEP 4: 관련 문서 갱신
  - PROGRESS.md 갱신 (Phase 1 완료)
  - Phase 1 회고 (A11) → decisions/phase1_retro.md
  - git tag phase1-d1-pass

■ STEP 5: 갱신 결과 검증
  - Phase 1→2 인수인계 확인:
    □ claude_md_gap_report → Phase 2-1 입력 존재?
    □ obsidian_gap_report → Phase 2-3 입력 존재?
    □ integrity_snapshot.json → D2 기준선 로드 가능?
    □ P1-1 산출물 4개 리포트 존재?
  - 로드맵 대조 (A12): Phase 2 내용이 현실과 맞는지

■ PASS 조건: 기준선 저장 + 인수인계 전부 확인 + 회고 + git tag → D1 PASS
````

---

## 3. Phase 2

### 세션 P2-0: 외부 의존성 재확인

**로드맵 작업 매핑:**

| # | 작업 | 상세 | 우선순위 | 산출물 |
|---|------|------|---------|--------|
| 2-0 | 외부 의존성 | PART1 E.1(9) + E.3(8) + B.1(9) 재확인 | **Must** | 환경 리포트 |

````
VAMOS 로드맵 Phase 2, 세션 P2-0 — 외부 의존성 재확인

■ 대상: 2-0(PART1 E.1+E.3+B.1 재확인, Must)

■ 참조:
  D:\VAMOS\docs\guides\VAMOS_구현가이드_PART1_진입전.md — Section E.1, E.3, B.1

■ STEP 1: 프롬프트 자체 검증
  a. 확인 대상 26건(E.1 9건 + E.3 8건 + B.1 9건)이 PART1과 일치하는지
  b. "프롬프트 최종 확정"

■ STEP 2: 작업 실행
  1. E.1 재확인 (9건): python/node/rust/ollama/git 버전 + pnpm/Poetry/CUDA 결정값
  2. E.3 재확인 (8건): pydantic v2/cargo/API Key/디스크/BGE-M3
  3. B.1 재확인 (9건): V0 준비 완료
  4. 변경 있으면 → 해당 항목 업데이트

■ STEP 3: 산출물 검증 (반복)
  a. 26건 전부 PASS/변경사항 기록?
  b. "산출물 최종 확정"

■ STEP 4: PROGRESS.md 갱신

■ STEP 5: 갱신 검증

■ PASS 조건: E.1(9) + E.3(8) + B.1(9) 전부 PASS
````

---

### 세션 P2-1: CLAUDE.md 보강

**로드맵 작업 매핑:**

| # | 작업 | 상세 | 우선순위 | 산출물 |
|---|------|------|---------|--------|
| 2-1 | CLAUDE.md 보강 | 보강전략 Phase A (5세션) → §21~§28 | **Must** | 보강된 CLAUDE.md |

````
VAMOS 로드맵 Phase 2, 세션 P2-1 — CLAUDE.md 보강

■ 대상: 2-1(CLAUDE.md 보강, Must)

■ 참조:
  D:\VAMOS\CLAUDE 보강전략 V1.0.md — §9 실행 순서
  P1-2 산출물: claude_md_gap_report

■ STEP 1: 프롬프트 자체 검증
  a. 보강 범위(§21~§28)가 보강전략 §5와 일치하는지
  b. GAP 목록 항목이 보강 범위에 포함되는지
  c. "프롬프트 최종 확정"

■ STEP 2: 작업 실행
  1. 보강전략 §9 5세션 진행:
     A-1: 기존 §1~§20 수정 (경로/줄수/갱신일)
     A-2: 모듈 보강 (EVX + COND 106개)
     A-3: 경로 보강 (특화 시스템 + 참조 경로)
     A-4: 신규 §21~§23 (SOT 2 라우팅 + COND + 교차 용어)
     A-5: 신규 §24~§27 (STEP7 + 의존성 + KG + .claude)
  2. §28 엔지니어링 프레임워크 추가 (A13):
     매트릭스 위치 + PROGRESS.md + Phase별 컨텍스트 테이블

■ STEP 3: 산출물 검증 (더 이상 수정 없을 때까지 반복)
  a. §1~§28 전부 존재?
  b. GAP 항목 전부 해소?
  c. 줄 수 ~953+?
  d. §28에 A13 컨텍스트 프로토콜 포함?
  e. 미세한 부분 확인 → 수정 → "산출물 최종 확정"

■ STEP 4: PROGRESS.md 갱신
■ STEP 5: 갱신 검증 — 보강된 CLAUDE.md가 SOT/SOT 2와 모순 없는지

■ PASS 조건: §1~§28 완성 + GAP 전부 해소 + 산출물 확정
````

---

### 세션 P2-2: CLAUDE.md 검증

**로드맵 작업 매핑:**

| # | 작업 | 상세 | 우선순위 | 산출물 |
|---|------|------|---------|--------|
| 2-2 | CLAUDE.md 검증 | 보강전략 Phase B (8스킬) → SILVER+ | Should | 검증 리포트 + 판정 |

````
VAMOS 로드맵 Phase 2, 세션 P2-2 — CLAUDE.md 검증

■ 대상: 2-2(CLAUDE.md 8스킬 검증, Should)

■ 참조: D:\VAMOS\CLAUDE 보강전략 V1.0.md — §6 검증 스킬 8개

■ STEP 1: 프롬프트 자체 검증
  a. 8스킬 목록이 보강전략 §6과 일치하는지
  b. "프롬프트 최종 확정"

■ STEP 2: 작업 실행
  1. 8스킬 순차 실행:
     /claude-md-sot-conflict, /claude-md-hallucination, /claude-md-fact-audit
     /claude-md-cross-examine, /claude-md-symbolic, /claude-md-consensus
     /claude-md-completeness, /claude-md-final-review → GOLD/SILVER/BRONZE/REJECT
  2. 회귀 확인: /sot-check 재실행 → D1 정합 안 깨뜨렸는지 (A15 R10)

■ STEP 3: 산출물 검증 (반복)
  a. 8스킬 결과 전부 기록?
  b. 최종 판정(SILVER+)?
  c. 회귀 확인 PASS?
  d. REJECT 시 (A1): 범위 축소(§21~§24만) → 재검증 → BRONZE 이상이면 진행
  e. "산출물 최종 확정"

■ STEP 4: PROGRESS.md 갱신
■ STEP 5: 갱신 검증

■ PASS 조건: SILVER+ 판정 + 회귀 확인 PASS + 산출물 확정
````

---

### 세션 P2-3: Obsidian 노트 생성

**로드맵 작업 매핑:**

| # | 작업 | 상세 | 우선순위 | 산출물 |
|---|------|------|---------|--------|
| 2-3 | Obsidian 생성 | Strategy v3.0 → 120+ 노트 + 매트릭스 노트 + A16 태깅 | Should | VAMOS HOME |

````
VAMOS 로드맵 Phase 2, 세션 P2-3 — Obsidian 노트 생성

■ 대상: 2-3(Obsidian 120+ 노트 생성, Should)

■ 참조:
  D:\VAMOS\VAMOS HOME\OBSIDIAN-STRATEGY-v3.md — §4~§6
  P1-2 산출물: obsidian_gap_report
  D:\VAMOS\docs\sot 2\ — 도메인 노트 내용 원본

■ STEP 1: 프롬프트 자체 검증
  a. 노트 생성 범위가 Strategy v3.0 §3과 일치하는지 (17개 폴더 + 120+ 노트)
  b. 태깅 규칙이 Strategy v3.0 §4와 일치하는지
  c. 템플릿이 Strategy v3.0 §5~§6과 일치하는지
  d. "프롬프트 최종 확정"

■ STEP 2: 작업 실행
  1. 120+ 노트 생성 (Strategy v3.0 §4~§6 실행)
  2. 매트릭스 노트: 12_IMPLEMENTATION/Engineering-Matrix.md
  3. 책임 AI 태깅 (A16): 7개 불변 관련 노트에 [responsible-ai] 태그

■ STEP 3: 산출물 검증 (반복)
  a. 120+ 노트 존재?
  b. 36개 도메인 전부 노트?
  c. [[wikilink]] 깨진 것 0건?
  d. LOCK 항목이 Registry와 일치?
  e. 매트릭스 노트 존재?
  f. 샘플 10% SOT 2 원본 대조 (A15 R12)?
  g. "산출물 최종 확정"

■ STEP 4: PROGRESS.md + STRATEGY_11 갱신 (노트 파일 등록)
■ STEP 5: 갱신 검증

■ PASS 조건: 120+ 노트 + 깨진 링크 0건 + 샘플 대조 + 산출물 확정
````

---

### 세션 P2-4: 린터/CI + 커스텀 린터

**로드맵 작업 매핑:**

| # | 작업 | 상세 | 우선순위 | 산출물 |
|---|------|------|---------|--------|
| 2-4 | 린터/CI | pyproject.toml + ruff + CI yaml + conftest.py | **Must** | 린터/CI 파일 |
| 2-5 | 커스텀 린터 | vamos_lint VL-001~005 + commitlint | **Must** | vamos_lint.py |
| 2-6 | CPS 템플릿 | Context/Problem/Solution 구조화 | Could | 템플릿 |

````
VAMOS 로드맵 Phase 2, 세션 P2-4 — 린터/CI 환경 세팅

■ 대상: 2-4(린터/CI, Must) + 2-5(커스텀 린터, Must) + 2-6(CPS, Could)

■ 참조:
  D:\VAMOS\VAMOS Engineering\STRATEGY_09_HARNESS_ENGINEERING.md §7~§8
  D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md — line 1410~1536

■ STEP 1: 프롬프트 자체 검증
  a. 생성할 파일 목록이 하네스 §7~§8과 일치하는지
  b. ruff 규칙이 PART2 line 1523~1536과 일치하는지
  c. VL-001~005가 CLAUDE.md §7 LOCK과 일치하는지
  d. "프롬프트 최종 확정"

■ STEP 2: 작업 실행
  1. 하네스 §7 (Layer 0): pyproject.toml, quality-python.yml, test-python.yml, conftest.py
  2. 하네스 §8 (Layer 1): ruff banned-api(DEC-002), vamos_lint.py(VL-001~005), commitlint
  3. CPS 템플릿 (Could)

■ STEP 3: 산출물 검증 (반복)
  a. poetry install 정상?
  b. ruff check . 실행 가능?
  c. pytest 실행 가능 (0 tests OK)?
  d. vamos_lint 5규칙 동작?
  e. ruff 13룰 ↔ PART2 일치?
  f. VL-001~005 ↔ CLAUDE.md §7 일치?
  g. "산출물 최종 확정"

■ STEP 4: PROGRESS.md + STRATEGY_11 갱신 (생성 파일 등록)
■ STEP 5: 갱신 검증

■ 실패 시 (A1): 린터 오탐(A15 R05) → 초기 warn 모드로 실행 → 안정화 후 error 전환

■ PASS 조건: ruff+pytest+vamos_lint 실행 가능 + CI yaml 존재 + 산출물 확정
````

---

### 세션 P2-5: Phase 2 Gate

**로드맵 작업 매핑:**

| # | 작업 | 상세 | 우선순위 | 산출물 |
|---|------|------|---------|--------|
| 2-7 | 로딩 전략 | 자산 인벤토리 §3 기반 로딩 맵 | Could | 로딩 맵 |
| 2-8 | 인벤토리 갱신 | Phase 2 생성 파일 반영 | Should | STRATEGY_11 갱신 |
| Gate | Phase 2 검증 | 체크리스트 + 인수인계 + 회고 | **Must** | PASS 판정 |

````
VAMOS 로드맵 Phase 2, 세션 P2-5 — Phase 2 Gate

■ 대상: 2-7(로딩 전략, Could) + 2-8(인벤토리 갱신, Should) + Phase 2 Gate(Must)

■ STEP 1: 프롬프트 자체 검증
  a. 2-V 체크리스트가 로드맵과 일치하는지
  b. 인수인계 항목이 로드맵 "Phase 2→3"과 일치하는지
  c. "프롬프트 최종 확정"

■ STEP 2: 작업 실행
  1. 로딩 전략 (Could): 자산 인벤토리 §3 기반 Phase별 SOT 2 로딩 맵
  2. 인벤토리 갱신 (2-8): STRATEGY_11에 Phase 2 생성 파일 반영
  3. Phase 2 검증 (2-V):
     □ CLAUDE.md SILVER+? □ Obsidian 120+ 노트? □ 린터 동작?
     □ CI yaml? □ 외부 의존성 PASS? □ 회귀 PASS?

■ STEP 3: 산출물 검증 (반복)
  a. 2-V 전항목 ☑?
  b. "산출물 최종 확정"

■ STEP 4: 관련 문서 갱신
  - Phase 2 회고 (A11) → decisions/phase2_retro.md
  - PROGRESS.md 갱신 (Phase 2 완료)
  - git tag phase2-b1-complete
  - 로드맵 대조 (A12)

■ STEP 5: 갱신 결과 검증
  - Phase 2→3 인수인계:
    □ 보강된 CLAUDE.md → Phase 3 AI 컨텍스트? □ Obsidian → 설계 참조?
    □ 린터/CI → Phase 4 자동 실행? □ 로딩 맵 → Phase 3~4 사용?
  - git tag 존재?

■ PASS 조건: 2-V 전항목 + 인수인계 + 회고 + git tag → Phase 2 완료
````

---

## 4. Phase 3

### 세션 P3-0: 미결정 게이트 (선행) ⟦2026-06-11 신설 — 로드맵 3-0 동기⟧

**로드맵 작업 매핑:**

| # | 작업 | 상세 | 우선순위 | 산출물 |
|---|------|------|---------|--------|
| 3-0 | 미결정 게이트 | D1 이연 대장 + 전수진단 결정 확인 + PART1 C.1 13건 + 분모·V1 귀속·STEP7 reconcile 확정 | **Must** (선행) | 결정 기록 |

````
VAMOS 로드맵 Phase 3, 세션 P3-0 — 미결정 게이트 (R1 착수 전 선행)

■ 대상: 3-0 (Must, 선행) — 로드맵 Phase 3 표 3-0 행의 게이트 스코프 ①~⑥ 전건

■ 참조:
  D:\VAMOS\VAMOS_최종_로드맵.md — Phase 3 표 3-0 행 (게이트 스코프 정의)
  D:\VAMOS\04. 구현단계\v13_results\phase0\D1_RESULTS_INDEX.md §3 — 이연 대장 D-1~D-4
  D:\VAMOS\_targets\DECISION_REGISTER.md — 기확정 17건 (D1~D7·D9~D11·D13~D19, D8·D12 결번)
  D:\VAMOS\docs\guides\VAMOS_구현가이드_PART1_진입전.md §C.1 — V0 시작 전 결정 13건
  D:\VAMOS\_targets\ROADMAP_정본화_검증보고서_2026-06-11.md — 분모·귀속 충돌 상세(F-03/F-11/F-12/F-18)

■ STEP 1: 프롬프트 자체 검증
  a. 3-0 행 스코프 ①~⑥과 본 세션 대상 일치 확인
  b. "프롬프트 최종 확정"

■ STEP 2: 작업 실행
  1. ① D1 이연 대장 D-2~D-4 처분 확인 (D-1은 RESOLVED 기록 확인만 — 2026-06-11 기해소)
  2. ② PART1 C.1 #1~3 기결정 확인, #4~13 확정 + 기록
  3. ③ 분모 확정: V0 모듈 "전 25 파일 선생성 여부"(기본 = PART2 V0-STEP-4 활성 5+stub 3) / V1 CORE 26 vs 32(기본 = PART2 §1.1 32)
  4. ④ V1 귀속 확정: SDAR §10.1 기반 · Cloud Library CB1(E-15/S-5) · RT-BNP V1 · 4-4 MLOps 본대 — SPEC↔PART2 충돌 해소(V1 추가 or V2 이연 명시)
  5. ⑤ STEP7 V1 라벨 ↔ PART2 V2/V3 배치 reconcile 방침 1건 (정본 우선순위: 본문 PART2 > STEP7)
  6. ⑥ READINESS §8 문서수정 잔여 확인 (다수 세션4~7 기집행 — 잔여만)
  7. 각 확정을 decisions/ ADR로 기록 (A6) — 기존 17건은 DECISION_REGISTER.md 정본 유지

■ STEP 3: 산출물 검증 (반복) — 미결정 잔여 0 확인 → "게이트 통과 선언"
■ STEP 4: PROGRESS.md 갱신
■ STEP 5: 갱신 검증 — 로드맵 3-0 행·DECISION_REGISTER와 모순 없는지

■ 실패 시 (A1): 확정 불가 항목 발생 → 보류 사유·기한 명기 후 R1 차단 여부 판단(차단 항목만 해소 후 진행)

■ PASS 조건: 스코프 ①~⑥ 전건 확정·기록 → P3-1(R1) 진입 허용
````

---

### 세션 P3-1: R1 런타임 설계 10개 LOCK

**로드맵 작업 매핑:**

| # | 작업 | 상세 | 우선순위 | 산출물 |
|---|------|------|---------|--------|
| 3-1~3-7 | R1 기존 7개 | Gate/메모리/Failover/DAG/Cost/IPC/MCP | **Must** | runtime_decisions.md |
| 3-7a | Defense Layer (A21) | 3계층 독립 확정 | **Must** | |
| 3-7b | 투명성 (A22) | reasoning_trace 스키마 + LOCK 관계 확정 | **Must** | |
| 3-7c | 신뢰도 (A25) | confidence_score + 임계값 LOCK | **Must** | |

````
VAMOS 로드맵 Phase 3, 세션 P3-1 — R1 런타임 설계 10개 LOCK

■ 대상: 3-1~3-7c (10개 결정, 전부 Must)

■ 참조:
  D:\VAMOS\docs\sot\D2.0-01~08 — 아키텍처 정본
  D:\VAMOS\VAMOS HOME\00_HUB\LOCK-DECISION-REGISTRY.md — 469건
  D:\VAMOS\VAMOS Engineering\STRATEGY_05_SAFETY_AND_ETHICS.md — A21, A22, A25
  D:\VAMOS\VAMOS Engineering\STRATEGY_06_INTEGRATION_AND_DEPLOY.md — A20

■ STEP 1: 프롬프트 자체 검증
  a. 10개 결정 목록이 로드맵 3-1~3-7c와 일치하는지
  b. 각 결정의 대조 SOT 정본이 정확한지 (D2.0-02, D2.0-05, D2.0-06, D2.0-07, PHASE_B1, PHASE_B4, DEC-017)
  c. A21 Defense Layer 3계층이 STRATEGY_05 §3과 일치하는지
  d. A22 ResponseEnvelope LOCK 관계가 STRATEGY_05 §4.2와 일치하는지 (D6 기확정: 선택지 A — metadata 내부 포함, 5필드 LOCK 보존)
  e. A25 confidence 임계값이 STRATEGY_05 §5.2와 일치하는지 (0.85/0.60/0.30)
  f. "프롬프트 최종 확정"

■ STEP 2: 작업 실행
  1. 10개 결정 각각 /sot-check로 정본 대조:
     3-1: 5-Gate 순서 → D2.0-07
     3-2: L0~L3 → D2.0-06
     3-3: Failover → D2.0-02 A-1
     3-4: DAG → D2.0-05 + D2.0-02 §2.2(9-State LOCK) ⟦2026-06-11 정정: 구 표기 PHASE_B5(테스트 전략)는 오참조⟧
     3-5: CostGate → D2.0-07 §4.2
     3-6: IPC + A20(Pydantic 정본) → PHASE_B1 §5.2(JSON-RPC 13) + D2.1 스키마 ⟦2026-06-11 정정: 구 표기 PHASE_B4(config)는 오참조⟧
     3-7: MCP → DEC-017
     3-7a: Defense Layer 3계층 → BASE-1.3 + SDAR §5.1
     3-7b: reasoning_trace → ResponseEnvelope LOCK 관계 — D6 기확정(선택지 A: metadata 내부, 5필드 LOCK 보존), 스키마 상세만 확정
     3-7c: confidence 임계값 → 0.85/0.60/0.30 LOCK
  2. 각 결정을 ADR 기록 (A6) → decisions/PHASE3-DEC-001~010
  3. LOCK Registry 일치 또는 신규 등록

■ STEP 3: 산출물 검증 (반복)
  a. 10개 결정 전부 SOT 정본과 일치?
  b. LOCK Registry 등록/일치?
  c. ADR 10건 존재?
  d. runtime_decisions.md 완성?
  e. 회귀: CLAUDE.md §5와 모순 없는지?
  f. "산출물 최종 확정"

■ STEP 4: PROGRESS.md 갱신
■ STEP 5: 갱신 검증 — ADR이 로드맵 참조와 정합

■ 실패 시 (A1): R1 결정이 SOT와 충돌 → SOT가 정본이므로 R1 수정. SOT 자체 모순 → DF 역류 → D1 부분 재실행

■ PASS 조건: 10개 LOCK + SOT 정합 + ADR + 산출물 확정
````

---

### 세션 P3-2: X1 횡단 전략 + 계획서 + Gate

**로드맵 작업 매핑:**

| # | 작업 | 상세 | 우선순위 | 산출물 |
|---|------|------|---------|--------|
| 3-8 | 보안 전략 | 7개 불변 + A16 + A21 검증 | **Must** | security_strategy.md |
| 3-9 | 테스트 전략 | 피라미드 + 80%+ | Should | test_strategy.md |
| 3-10 | 릴리스 전략 | 브랜치 + SemVer + A23 | Should | release_strategy.md |
| 3-11 | 문서화 전략 | 코드/설계 주체 + Obsidian 규칙 | Could | doc_strategy.md |
| 3-12 | 런타임 계획서 | R1 기반 R2a/R2b/RF | Should | runtime_eng_plan.md |
| 3-13 | 횡단 계획서 | X1 기반 X2/X3/XF | Should | cross_eng_plan.md |

````
VAMOS 로드맵 Phase 3, 세션 P3-2 — X1 횡단 전략 + 계획서 + Phase 3 Gate

■ 대상: 3-8~3-13 + Phase 3 Gate

■ 참조:
  D:\VAMOS\docs\sot\BASE-1.3_VAMOS_RULE_1.3_BASE.md — 보안 정본
  D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md §3.5 — 테스트
  D:\VAMOS\docs\sot\PLAN-3.0_최종완성본.md §2 — 릴리스
  D:\VAMOS\VAMOS Engineering\STRATEGY_05_SAFETY_AND_ETHICS.md — A16

■ STEP 1: 프롬프트 자체 검증
  a. 4개 전략 범위가 로드맵 3-8~3-11과 일치?
  b. 계획서 2개가 R1 결과(P3-1 산출물)를 반영하는지?
  c. "프롬프트 최종 확정"

■ STEP 2: 작업 실행
  1. 4개 전략 작성 (각각 SOT 정본 대조):
     3-8: security_strategy.md + A16 체크리스트 + A21 검증
     3-9: test_strategy.md
     3-10: release_strategy.md + Expand/Contract(A23)
     3-11: doc_strategy.md
  2. 계획서 2개: runtime_eng_plan.md(3-12), cross_eng_plan.md(3-13)

■ STEP 3: 산출물 검증 (반복)
  a. 4개 전략이 각각 SOT 정본과 일치?
  b. 계획서가 R1 10개 결정 + X1 4개 전략 전부 반영?
  c. 회귀: X1 전략이 Phase 2 린터 설정과 모순 없는지?
  d. "산출물 최종 확정"

■ STEP 4: 관련 문서 갱신
  - Phase 3→4 인수인계 확인:
    □ runtime_decisions.md → Phase 4 R2a? □ 전략 4개 → Phase 4 X2?
    □ IPC 사양 + A20 → Phase 4 B2c?
  - Phase 3 회고 (A11) → decisions/phase3_retro.md
  - PROGRESS.md 갱신 + git tag phase3-complete
  - 로드맵 대조 (A12)

■ STEP 5: 갱신 결과 검증 — 인수인계 항목 전부 존재 + git tag

■ PASS 조건: 10개 LOCK + 4개 전략 + 2개 계획서 + 인수인계 + 회고 + git tag
````

---

## 5. Phase 4

### 세션 P4-0: 스킬 점검 + 타입 동기화

**로드맵 작업 매핑:**

| # | 작업 | 상세 | 우선순위 | 산출물 |
|---|------|------|---------|--------|
| 사전 | 스킬/Hook 점검 | 11개 스킬 + 6개 Hook (A7) | **Must** | 점검 결과 |
| 4-1 | B2c 타입 동기화 | Pydantic→Schema→serde→TS + 왕복 (A20) | **Must** | shared_schemas/ |

````
VAMOS 로드맵 Phase 4, 세션 P4-0 — 스킬 점검 + 타입 동기화

■ 대상: 스킬/Hook 점검(A7, Must) + 4-1(타입 동기화, Must)

■ 참조:
  D:\VAMOS\VAMOS Engineering\STRATEGY_04_TOOL_MAINTENANCE.md §2~§3
  D:\VAMOS\VAMOS Engineering\STRATEGY_06_INTEGRATION_AND_DEPLOY.md §2 — A20

■ STEP 1: 프롬프트 자체 검증
  a. 점검 대상(11 스킬 + 6 Hook)이 STRATEGY_04 §2와 일치?
  b. 타입 동기화 규칙(Pydantic 정본)이 STRATEGY_06 §2.2와 일치?
  c. "프롬프트 최종 확정"

■ STEP 2: 작업 실행
  1. 스킬 11개 + Hook 6개 동작 확인 → PROGRESS.md 기록
  2. Pydantic 25개 모델 정의 (D2.1 + confidence_score A25)
  3. JSON Schema 추출 → serde(Rust) 생성 → TS interface 생성
  4. 왕복 테스트: Python→JSON→Rust→JSON→Python 일치?

■ STEP 3: 산출물 검증 (반복)
  a. 스킬 11개 전부 실행 가능?
  b. Hook 6개 settings.json 경로 일치?
  c. 왕복 테스트 PASS?
  d. 25개 모델에 confidence_score 포함?
  e. "산출물 최종 확정"

■ STEP 4: PROGRESS.md 갱신
■ STEP 5: 갱신 검증

■ PASS 조건: 스킬 PASS + Hook PASS + 왕복 PASS + 산출물 확정
````

---

### 세션 P4-1: ORANGE CORE + Registry + config

**로드맵 작업 매핑:**

| # | 작업 | 상세 | 우선순위 | 산출물 |
|---|------|------|---------|--------|
| 4-2 | ORANGE CORE | I-1~I-25 + Pipeline + Gate + A21/A22/A25 | **Must** | backend/orange_core/ |
| 4-4 | Registry | EventType/Failure/Fallback | **Must** | |
| 4-5 | config.v1.toml | LOCK + confidence + cost_limit | **Must** | |

````
VAMOS 로드맵 Phase 4, 세션 P4-1 — ORANGE CORE + Registry + config

■ 대상: 4-2 + 4-4 + 4-5 (전부 Must)

■ 참조:
  D:\VAMOS\VAMOS Engineering\STRATEGY_11_ASSET_INVENTORY.md §3.4
  D:\VAMOS\docs\sot\D2.0-02 — ORANGE CORE 정본
  P3-1 산출물: runtime_decisions.md

■ STEP 1: 프롬프트 자체 검증
  a. 구현 범위가 runtime_decisions.md의 10개 LOCK과 일치?
  b. config LOCK 값이 D2.0-07 §4.2 + STRATEGY_05 §5.2 임계값과 일치?
  c. "프롬프트 최종 확정"

■ STEP 2: 작업 실행 (매 파일마다: 코드→ruff→vamos_lint→pytest→PASS→커밋)
  1. I-1~I-25 스켈레톤 + 5-Phase Pipeline + 5-Gate + Defense Layer 3계층(A21) + reasoning_trace(A22) + confidence_score(A25)
  2. EventType/Failure/Fallback Registry (D2.1-D2 기반)
  3. config.v1.toml: 20개 LOCK + confidence 3개(A25) + cost_monthly_limit(A21)
  4. STEP별 체크포인트:
     □ V0-STEP-1 디렉토리 PHASE_B2 일치? □ V0-STEP-2 25개 D2.1 일치? □ V0-STEP-3 LOCK 일치?

■ STEP 3: 산출물 검증 (반복)
  a. 3개 STEP 통과?
  b. ruff+vamos_lint+pytest 전부 PASS?
  c. config LOCK 값이 SOT와 일치?
  d. "산출물 최종 확정"

■ STEP 4: PROGRESS.md + STRATEGY_11 갱신 (생성 코드 구조)
■ STEP 5: 갱신 검증

■ PASS 조건: STEP-1~3 + 하네스 PASS + 산출물 확정
````

---

### 세션 P4-2: IPC + BLUE NODE + 프론트엔드

**로드맵 작업 매핑:**

| # | 작업 | 상세 | 우선순위 | 산출물 |
|---|------|------|---------|--------|
| IPC | V0-STEP-4 | JSON-RPC 왕복 (A20) | **Must** | |
| Pipeline | V0-STEP-5 | 5-Phase 최소 동작 | **Must** | |
| 4-6 | BLUE NODE | Dev/Research/Productivity 3개 | **Must** | backend/blue_nodes/ |
| 4-3 | 프론트엔드 | Tauri+React + A22 + A25 + A16 | Should | frontend/ |
| 4-7 | X2 횡단 실행 | 보안 스캔 + 테스트 작성 + 커밋 린트 | Should | 보안/테스트 리포트 |

````
VAMOS 로드맵 Phase 4, 세션 P4-2 — IPC + BLUE NODE + 프론트엔드

■ 대상: V0-STEP-4(Must) + V0-STEP-5(Must) + 4-6(Must) + 4-3(Should) + 4-7(X2 횡단, Should)

■ STEP 1: 프롬프트 자체 검증
  a. IPC 사양이 runtime_decisions.md 3-6과 일치?
  b. A20 규칙(Pydantic 정본 + 자동 생성)이 적용되는지?
  c. "프롬프트 최종 확정"

■ STEP 2: 작업 실행 (매 파일마다 하네스)
  1. JSON-RPC IPC 구현 → 왕복 테스트 PASS (A20)
  2. 5-Phase Pipeline 최소 동작
  3. BLUE NODE 3개 스켈레톤
  4. 프론트엔드 (Should): Tauri + React + "왜?" 버튼(A22) + 신뢰도(A25) + 면책(A16)
  5. X2 횡단 실행 (Should): 보안 스캔 + 테스트 작성 + 커밋 린트 (commitlint)
  6. STEP 체크포인트: □ STEP-4 왕복 PASS? □ STEP-5 최소 동작?

■ STEP 3: 산출물 검증 (반복) → "산출물 최종 확정"
■ STEP 4: PROGRESS.md 갱신
■ STEP 5: 갱신 검증

■ PASS 조건: STEP-4,5 + BLUE NODE + 하네스 PASS + 산출물 확정
````

---

### 세션 P4-3: Phase 4 Gate

````
VAMOS 로드맵 Phase 4, 세션 P4-3 — Phase 4 Gate

■ STEP 1: 프롬프트 자체 검증 → "확정"

■ STEP 2: Phase 4 검증 (4-V):
  □ Must 11개 전부 통과(STRATEGY_02 표 라벨 기준 — 로드맵 4-V 분모 확정 2026-06-11)? □ B2c 왕복 PASS(A20)? □ 하네스 매 커밋 자동?
  □ Defense Layer 구현(A21)? □ reasoning_trace(A22)? □ confidence_score(A25)?

■ STEP 3: 산출물 검증 (반복) → "산출물 최종 확정"

■ STEP 4: 회고(A11) + PROGRESS.md + STRATEGY_11 갱신 + git tag + 로드맵 대조(A12)
■ STEP 5: 갱신 검증

■ 실패 시 (A1): Must 미통과 → 원인 분석(설계?코드?환경?) → 해당 영역 수정 → 재실행. 3언어 타입 불일치(R07) → A20: Pydantic에서 재생성

■ PASS 조건: 4-V 전항목 + 회고 + git tag
````

---

## 6. Phase 5

### 세션 P5-1: Eval + D3 + GO/NO-GO

**로드맵 작업 매핑:**

| # | 작업 | 상세 | 우선순위 | 산출물 |
|---|------|------|---------|--------|
| 5-1~5-2 | Eval | ragas+deepeval+promptfoo → QoD | Should | eval_results.json |
| 5-3~5-6 | D3 정합 | 모듈/스키마/Registry/LOCK 대조 | **Must** | alignment_report.json |
| 5-7+5-7a | 횡단+배포 | CI+commitlint + 배포 검증(A24) | **Must** | |
| 5-8 | GO/NO-GO | Phase 5 조건 + READINESS V0 ~15건 | **Must** | V0 릴리스 판정 |

````
VAMOS 로드맵 Phase 5, 세션 P5-1 — V0 검증 + GO/NO-GO

■ 대상: 5-1~5-8 (Must: 5-3~5-8, Should: 5-1~5-2)

■ 참조:
  D:\VAMOS\VAMOS Engineering\STRATEGY_11_ASSET_INVENTORY.md §3.5
  D:\VAMOS\docs\sot\VAMOS_IMPLEMENTATION_READINESS_GUIDE.md — V0 GO/NO-GO

■ STEP 1: 프롬프트 자체 검증
  a. D3 대조 항목이 로드맵 5-3~5-6과 일치?
  b. GO/NO-GO가 READINESS_GUIDE V0 섹션과 일치?
  c. 배포 검증(A24) 3단계가 STRATEGY_06 §4.2와 일치?
  d. "프롬프트 최종 확정"

■ STEP 2: 작업 실행 (3트랙 병렬)
  [A] Eval: ragas+deepeval+promptfoo+minicheck → QoD → 멱등성 seed=42 3회(A17)
  [B] D3: 모듈 수 + 스키마 필드(+confidence A25) + Registry + LOCK(+confidence 임계값)
  [C] X3: CI pytest + commitlint → 배포 검증(A24): 앱 기동 + config 대조 + E2E
  [통합] V0 GO/NO-GO: Phase 5 조건 + READINESS V0 ~15건

■ STEP 3: 산출물 검증 (반복)
  a. DRIFT 0건? b. 배포 검증 3단계 PASS? c. GO/NO-GO 전부 충족?
  d. 멱등성 3회 동일(A17)? e. "산출물 최종 확정"

■ STEP 4: 회고(A11) + STRATEGY_11 갱신 + PROGRESS.md + git tag v0-release + 로드맵 대조(A12)
■ STEP 5: 갱신 검증

■ 실패 시 (A1): DRIFT 발견 → 설계 정본 기준 코드 수정 → Phase 4 해당 STEP 재실행. GO/NO-GO 미충족 → 미충족 항목 수정 → 5-8 재확인

■ PASS 조건: DRIFT 0건 + 배포 PASS + GO/NO-GO + 멱등성 + 회고 + git tag → V0 완료
````

---

## 7. Phase 6

### 세션 P6-0: V1 준비

**로드맵 작업 매핑:**

| # | 작업 | 상세 | 우선순위 | 산출물 |
|---|------|------|---------|--------|
| 사전 | 스킬 재점검 | V0 구조 변경 영향 (A7) | **Must** | 점검 결과 |
| 사전 | B.2 확인 | PART1 V1 추가 12건 | **Must** | 준비 리포트 |
| 사전 | 마이그레이션 | Expand/Contract 확인 (A23) | **Must** | |

````
VAMOS 로드맵 Phase 6, 세션 P6-0 — V1 준비

■ 대상: 스킬 재점검 + PART1 B.2 + 마이그레이션 규칙 (전부 Must)

■ 참조:
  D:\VAMOS\docs\guides\VAMOS_구현가이드_PART1_진입전.md — Section B.2
  D:\VAMOS\VAMOS Engineering\STRATEGY_06_INTEGRATION_AND_DEPLOY.md §3 — A23

■ STEP 1: 프롬프트 자체 검증 → "확정"

■ STEP 2: 작업 실행
  1. 스킬 11개 + Hook 6개 재점검 (A7)
  2. PART1 B.2: API Key 6건 + SW 4건 + GitHub 2건 준비 확인
  3. 마이그레이션: Expand/Contract 규칙 + config 키 호환 + 데이터 호환

■ STEP 3: 산출물 검증 (반복) → "산출물 최종 확정"
■ STEP 4: PROGRESS.md 갱신
■ STEP 5: 갱신 검증

■ PASS 조건: 스킬 PASS + B.2 준비 + 마이그레이션 확인
````

---

### 세션 P6-1: D1' + B1' + V1 핵심 구현

**로드맵 작업 매핑:**

| # | 작업 | 상세 | 우선순위 |
|---|------|------|---------|
| 6-1 | D1' 재검증 | V0 D3 + COND 106개 | **Must** |
| 6-2 | B1' 확장 | vamos_lint Layer 2 | **Must** |
| 6-3 | R2a' CORE | 26개 실제 구현 | **Must** |
| 6-4 | R2b' 에이전트 | LangGraph 3 + RAG | **Must** |

````
VAMOS 로드맵 Phase 6, 세션 P6-1 — D1' + B1' + V1 핵심 구현

■ 대상: 6-1~6-4 (전부 Must)

■ STEP 1: 프롬프트 자체 검증
  a. D1' 범위가 V0 D3 결과 + COND 106개인지?
  b. B1' Layer 2가 187개 모듈 네이밍인지?
  c. "프롬프트 최종 확정"

■ STEP 2: 작업 실행
  1. D1': /sot-conflict + /sot2-cross-ref + /validate — COND 106개 범위 추가
     버전 간 역류: V0 결함 발견 시 수정 ≤50% → V1에서 흡수
  2. B1': vamos_lint Layer 2 (187개 모듈 네이밍 규칙)
  3. R2a': 26개 CORE 모듈 실제 구현 (매 파일마다 하네스)
  4. R2b': LangGraph 에이전트 3개 + BGE-M3→Chroma RAG

■ STEP 3: 산출물 검증 (반복) → "산출물 최종 확정"
■ STEP 4: PROGRESS.md 갱신
■ STEP 5: 갱신 검증

■ PASS 조건: D1' PASS + Layer 2 동작 + 26개 CORE + RAG 기본 동작
````

---

### 세션 P6-2: V1 UI + 운영 + Eval

**로드맵 작업 매핑:**

| # | 작업 | 상세 | 우선순위 |
|---|------|------|---------|
| 6-5 | R2c' E2E UI | reasoning_trace + confidence | Should |
| 6-6 | R3 운영 | 모니터링 + ₩40K/월 | Should |
| 6-7 | B3' Eval | QoD≥0.70 + 벤치마크 4개 | **Must** |

````
VAMOS 로드맵 Phase 6, 세션 P6-2 — V1 UI + 운영 + Eval

■ 대상: 6-5(Should) + 6-6(Should) + 6-7(Must)

■ STEP 1: 프롬프트 자체 검증 → "확정"

■ STEP 2: 작업 실행
  1. R2c': 입력→응답 E2E + reasoning_trace(A22) + confidence(A25) UI 표시
  2. R3: SQLite 모니터링 + 비용 추적(₩40K/월) + Alert 동작
  3. B3': QoD≥0.70 + MMLU/HumanEval/MBPP/LogicKor

■ STEP 3: 산출물 검증 (반복) → "산출물 최종 확정"
■ STEP 4: PROGRESS.md 갱신
■ STEP 5: 갱신 검증

■ PASS 조건: QoD≥0.70 + 벤치마크 4개 PASS + 산출물 확정
````

---

### 세션 P6-3: V1 Gate

**로드맵 작업 매핑:**

| # | 작업 | 상세 | 우선순위 |
|---|------|------|---------|
| 6-8 | D3' API | 88개 계약 vs 코드 | **Must** |
| 6-8a | 배포 검증 | /health + config + E2E (A24) | **Must** |
| 6-9 | V1 GO/NO-GO | READINESS V1 ~20건 + B.2(12건) | **Must** |

````
VAMOS 로드맵 Phase 6, 세션 P6-3 — V1 Gate

■ 대상: 6-8 + 6-8a + 6-9 (전부 Must)

■ 참조: D:\VAMOS\docs\sot\VAMOS_IMPLEMENTATION_READINESS_GUIDE.md — V1 GO/NO-GO

■ STEP 1: 프롬프트 자체 검증
  a. D3' 대조 범위(88개 API)가 PHASE_B1과 일치?
  b. 배포 검증 3단계가 STRATEGY_06 §4.2와 일치?
  c. GO/NO-GO가 READINESS V1 + PART1 B.2와 일치?
  d. "프롬프트 최종 확정"

■ STEP 2: 작업 실행
  1. D3': 88개 API 계약 vs 실제 코드 대조 → DRIFT 0건
  2. 배포 검증 (A24): /health + config LOCK 런타임 대조 + 핵심 E2E
  3. V1 GO/NO-GO: READINESS V1 ~20건 + PART1 B.2(12건)

■ STEP 3: 산출물 검증 (반복)
  a. DRIFT 0건? b. 배포 3단계 PASS? c. GO/NO-GO 전부 충족?
  d. "산출물 최종 확정"

■ STEP 4: Phase 6 회고(A11) + PROGRESS.md + git tag v1-release + 로드맵 대조(A12)
■ STEP 5: 갱신 검증

■ PASS 조건: QoD≥0.70 + 비용≤₩40K/월 + 배포 PASS + GO/NO-GO + 회고 + git tag → V1 완료
````

---

## 7.5 Phase 7~8 (V2·V3 사이클) — 세션 프롬프트는 PART2 위임 ⟦2026-06-11 로드맵 Phase 7/8 편입 동기⟧

로드맵 Phase 7(V2)·Phase 8(V3)의 작업별 AI 프롬프트는 본 파일에 별도 작성하지 않는다 — **PART2 §4 V2-Phase 1~3 · §5 V3-Phase 1~3의 각 "실행 가이드 + AI 프롬프트" 블록이 세션 프롬프트 정본**이다(로드맵 2층 구조 원칙).

- **P7-0·P8-0(진입 게이트)**: 로드맵 7-0/8-0 행 스코프 그대로 — 전환 조건 TC 판정(PART2 §7.2/§7.3 하단 측정 메커니즘 표 정본) + C.3 결정 정식화(D11: #1~3→P7-0, #4~5→P8-0) + (P7-0 한정) 한국어 LLM 결정(PART1 C.2 #1)·3-0 V2 귀속분 수용.
- **P7-1~P7-3 / P8-1~P8-3(구현)**: PART2 V2-Phase 1~3 / V3-Phase 1~3 프롬프트 블록 사용.
- **P7-4·P8-4(검증 게이트)**: PART2 §7.3(14항목)/§7.4(12항목) + READINESS §9.3/§9.4 체크리스트.
- 공통 5-STEP 흐름·A5/A6/A11·A2(git tag v2-release/v3-release) 동일 적용.

---

## 8. 진행 상태 추적 테이블

| Phase | 세션 | 작업 | 상태 |
|-------|------|------|------|
| **0** | P0-1 | 자산 인벤토리 + Git + 리스크 | ✅ (2026-04-04) |
| | P0-2 | CLAUDE.md 구조 + Obsidian 연결 | ✅ (2026-04-04) |
| | P0-3 | 매트릭스 v1.1 갱신 | ✅ (2026-04-04) |
| | P0-4 | Phase 0 Gate | ✅ (2026-04-04, tag phase0-complete — 산출물 소급 커밋 06-05) |
| **1** | P1-0 | 도구 점검 + SOT 2 완성 확인 | ✅ (2026-06-03, 30/30 도메인) |
| | P1-1 | D1 핵심 검증 (1-2~1-5) | ✅ (2026-06-04 D1 PASS) |
| | P1-2 | D1 보조 + 기준선 + Gate | ✅ (2026-06-04, 감사 정정 06-05, tag phase1-d1-pass) |
| **2** | P2-0 | 외부 의존성 재확인 | ⬜ |
| | P2-1 | CLAUDE.md 보강 | ⬜ |
| | P2-2 | CLAUDE.md 검증 | ⬜ |
| | P2-3 | Obsidian 노트 생성 | ⬜ |
| | P2-4 | 린터/CI + 커스텀 린터 | ⬜ |
| | P2-5 | Phase 2 Gate | ⬜ |
| **3** | P3-0 | 미결정 게이트 (선행, 2026-06-11 신설) | ⬜ |
| | P3-1 | R1 런타임 10개 LOCK | ⬜ |
| | P3-2 | X1 전략 + 계획서 + Gate | ⬜ |
| **4** | P4-0 | 스킬 점검 + 타입 동기화 | ⬜ |
| | P4-1 | ORANGE CORE + Registry + config | ⬜ |
| | P4-2 | IPC + BLUE NODE + 프론트엔드 | ⬜ |
| | P4-3 | Phase 4 Gate | ⬜ |
| **5** | P5-1 | Eval + D3 + GO/NO-GO | ⬜ |
| **6** | P6-0 | V1 준비 + 스킬 재점검 | ⬜ |
| | P6-1 | D1' + B1' + V1 핵심 | ⬜ |
| | P6-2 | V1 UI + 운영 + Eval | ⬜ |
| | P6-3 | V1 Gate | ⬜ |
| **7** | P7-0 | V2 진입 게이트 (전환 조건 6 + C.3 #1~3 + 한국어 LLM) | ⬜ |
| | P7-1~P7-3 | V2-Phase 1~3 구현 (PART2 §4 프롬프트 위임, 3세션) | ⬜ |
| | P7-4 | V2 검증 + GO/NO-GO (14항목) | ⬜ |
| **8** | P8-0 | V3 진입 게이트 (전환 조건 + C.3 #4~5) | ⬜ |
| | P8-1~P8-3 | V3-Phase 1~3 구현 (PART2 §5 프롬프트 위임, 3세션) | ⬜ |
| | P8-4 | V3 검증 + GO/NO-GO (12항목) | ⬜ |

**총 35세션** (P3-0 신설 + Phase 7~8 10세션 편입 2026-06-11 · Phase 0~1 = 7세션 완료, 잔여 28세션 — 표시상 P7-1~3/P8-1~3은 각 3세션 묶음 행)

---

> **모든 세션 공통 5-STEP 흐름:**
> STEP 1: 프롬프트 자체 검증 → 불일치 시 수정 반복 → "프롬프트 최종 확정"
> STEP 2: 작업 실행
> STEP 3: 산출물 검증 → 미세 부분까지 반복 → "산출물 최종 확정"
> STEP 4: 관련 문서 갱신 (PROGRESS.md + STRATEGY_11 + 회고 + git tag)
> STEP 5: 갱신 결과 검증 (다른 문서와 모순 없는지)
