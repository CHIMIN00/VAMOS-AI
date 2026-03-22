# Phase 0-E: V8/V9 산출물 1:1 재검증 종합 보고서

> **Pipeline**: VAMOS v10.0.0
> **단계**: Phase 0-E (대화 17~18)
> **실행일**: 2026-03-09
> **원칙**: V8/V9 산출물은 참고용. v10_merged_features.json(3943개) 독립 추출 결과와 1:1 대조

---

## 1. 종합 판정

| 구분 | 대상 수 | CONFIRMED | CONFIRMED_WITH_NOTE | GAP_FOUND | 총 GAP 수 |
|:----:|:-------:|:---------:|:-------------------:|:---------:|:---------:|
| **V8 재검증** (대화 17) | 5 | 0 | 0 | 5 | 17 |
| **V9 재검증** (대화 18) | 4 | 0 | 1 | 3 | 10 |
| **합계** | **9** | **0** | **1** | **8** | **27** |

### 핵심 결론

**V8/V9 어느 쪽도 "기능 목록 완전성(Feature Coverage)"을 검증하지 않았음.**

- V8: 수량/구조 매칭 (모듈 수, API 수, 스키마 필드 수, Config 키)
- V9: PART2 내부 정합성 (경로, 수량, 의존성, 산출물, 구현가능성, 외부의존성)
- **V10이 최초로 "기능 완전성" 관점을 도입** — 3943개 기능의 Phase 배정 및 커버리지 검증

---

## 2. V8 재검증 결과 요약 (대화 17)

### 2.1 GAP 목록 (17건)

| ID | 대상 | 내용 | 심각도 |
|----|------|------|--------|
| GAP-E1 | IMP-E 모듈 매트릭스 | module_id 미매핑 — FT-MOD 244개에 module_id 비어있음 | HIGH |
| GAP-E2 | IMP-E | phase_assignment 필드 전역 부재 (3943개 전체) | HIGH |
| GAP-E3 | IMP-E | V3-only 모듈 수 불일치 (IMP-E 39 vs V10 41, 2개 차이) | MEDIUM |
| GAP-C1 | IMP-C API | V8 '88개 매칭 완료' 주장 vs IMP-C verdict=FAIL 모순 | HIGH |
| GAP-C2 | IMP-C | API 수 차이 (IMP-C 83개 vs V10 FT-API 135개, +52) | HIGH |
| GAP-C3 | IMP-C | 135개 API Phase 배정 미수행 | HIGH |
| GAP-C4 | IMP-C | IPC src_only 67개, part2_only 8개 대규모 불일치 미해결 | MEDIUM |
| GAP-B1 | IMP-B 스키마 | 25개 스키마 Phase 배정 미수행 | MEDIUM |
| GAP-B2 | IMP-B | src_schemas_found=0 (SRC에서 스키마 0개 발견) | LOW |
| GAP-B3 | IMP-B | LOCK 스키마 4개 구현 우선순위/Phase 미정 | MEDIUM |
| GAP-D1 | IMP-D Config | 291개 FT-CFG Phase 배정 없음 | MEDIUM |
| GAP-D2 | IMP-D | 섹션 불일치 (B4=13 vs PART2=17 vs SRC=18) 미해결 | MEDIUM |
| GAP-D3 | IMP-D | Value mismatch 15건 미해결 | HIGH |
| GAP-D4 | IMP-D | IMP-D verdict=FAIL 상태 유지 | HIGH |
| GAP-A7-1 | Agent 7 UI/UX | D2.0-08 모바일/PWA/위젯/AR 14건 중 3건만 검증 | MEDIUM |
| GAP-A7-2 | Agent 7 | HIGH 5건 미해결 (i18n, Hooks명, 페이지 목록 등) | MEDIUM |
| GAP-A7-3 | Agent 7 | D2.1-D8 파일 부재 문제 미해결 | LOW |

### 2.2 Cross-Cutting GAPs (V8)

| ID | 제목 | 심각도 |
|----|------|--------|
| CCG-1 | phase_assignment 필드 전역 부재 (3943개) | HIGH |
| CCG-2 | V8 상위 보고와 실제 verdict 불일치 (IMP-C, IMP-D) | HIGH |
| CCG-3 | module_id 매핑 부재 (FT-MOD 244개) | MEDIUM |

---

## 3. V9 재검증 결과 요약 (대화 18)

### 3.1 GAP 목록 (12건)

| ID | 대상 | 내용 | 심각도 |
|----|------|------|--------|
| GAP-SOT-1 | SOT 매핑 | part2_references 수 불일치 (_meta=488, unique=490, sum=526) | LOW |
| GAP-SOT-2 | SOT 매핑 | 8개 SOT 파일 PART2 미참조 (STEP7 5개=1544기능, BEGINNER=30기능 등) | HIGH |
| GAP-SOT-3 | SOT 매핑 | SOT→PART2 역방향 검증 미수행 | HIGH |
| GAP-GT1-1 | GT-1 레지스트리 | SD-01/SD-03 구조적 모호성이 Phase 배정에 간접 영향 | MEDIUM |
| GAP-PH1-1 | Phase 1 보고 | Feature Coverage 관점 전면 부재 (877 checks 중 0건) | HIGH |
| GAP-PH1-2 | Phase 1 보고 | V9 REAL_ERROR 4건이 V10 기능 추출 정확도에 잠재 영향 | MEDIUM |
| GAP-PH1-3 | Phase 1 보고 | V9 검증 범위 한계 — 내부 정합성 6관점만 검증 | MEDIUM |
| GAP-VER-1 | PART2 버전 | v21.0.0 changelog 미존재 | MEDIUM |
| GAP-VER-2 | PART2 버전 | V8(v18) 이후 Stage Gate 190개 등 대규모 추가, V8 결과 직접 비교 불가 | HIGH |
| GAP-VER-3 | PART2 버전 | V8 IMP-C/D FAIL이 v19~v20 수정으로 해소되었는지 미확인 | MEDIUM |

### 3.2 Cross-Cutting GAPs (V9)

| ID | 제목 | 심각도 |
|----|------|--------|
| V9-CCG-1 | Feature Coverage 검증 전면 부재 | HIGH |
| V9-CCG-2 | SOT→PART2 역방향 검증 미수행 (STEP7 1544개 미추적) | HIGH |
| V9-CCG-3 | V9 REAL_ERROR 미해결 항목의 V10 영향 | MEDIUM |
| V9-CCG-4 | PART2 v21.0.0 changelog 미존재 | MEDIUM |

---

## 4. v18→v21 Changelog 분석

| 버전 | 날짜 | 주요 변경 | 구현 항목 영향 |
|------|------|----------|--------------|
| v17.0.0 | 03-03 | Track A 잔여 이슈 19건 (BLOCKER 2, MED 16) | config_loader 3단계, LogEventSchema 7필드, MCP 도구 수 등 |
| **v18.0.0** | 03-03 | **V2/V3 실행 가이드 전면 추가** | 6 AI프롬프트 + 6 사용자가이드 + 6 산출물참조 (대규모 컨텐츠 추가) |
| v19.0.0 | 03-06 | Ripple Fix 11건 (CRITICAL 3) | 9-State 상태기계, VamosState 필드, Failover 체인 추가 |
| v19.1.0 | 03-06 | 재검증 1건 수정 | RT-BNP 칼럼 수정 |
| **v20.0.0** | 03-06 | **Stage Gate 18개 (~190 검증 항목) 추가** | V0~V3 전 Stage에 완료 검증 섹션 신설 |
| v20.1.0~v20.4.0 | 03-06 | Stage Gate SOT 정합성 15건 수정 | alpha값, SDAR 액션명, 페이지 누락, Gate 순서 등 |
| **v21.0.0** | **미기재** | **changelog 항목 없음** | V9 Phase 2 수정 내용 미문서화 |

### V8(v18) → V10(v21) 간 핵심 변화

1. **Stage Gate 시스템 전면 도입** (v20.0.0) — V8 시점에 미존재
2. **9-State 상태기계 인라인** (v19.0.0) — V8이 검증하지 못한 항목
3. **15건 세부 수정** (v20.1~v20.4) — V8 IMP-D value mismatch 일부 해소 가능성
4. **v21.0.0 불명** — changelog 부재로 V9의 정확한 수정 내역 미파악

---

## 5. V10 Phase 1 진입 전 권고사항

### 5.1 필수 선행 (HIGH)

| # | 항목 | 근거 |
|---|------|------|
| 1 | **Phase 배정 수행** | CCG-1: 3943개 기능에 phase_assignment 필드 부재. PART2 Phase(V0-STEP1~V3-Phase3)에 기능 매핑 필요 |
| 2 | **Feature Coverage 산출** | V9-CCG-1: V8/V9 모두 미수행. 3943개 기능 중 PART2에 명시적 구현 지침이 있는 비율 산출 |
| 3 | **STEP7→PART2 역방향 추적** | V9-CCG-2/GAP-SOT-2: STEP7 유래 1544개 기능이 PART2에 어떻게 반영되어 있는지 매핑 |

### 5.2 권고 (MEDIUM)

| # | 항목 | 근거 |
|---|------|------|
| 4 | module_id 매핑 생성 | CCG-3: FT-MOD 244개에 IMP-E 81개 모듈과의 매핑 필요 |
| 5 | V8 verdict 신뢰도 재평가 | CCG-2: IMP-C/D FAIL을 PASS로 보고한 이력 감안, V8 결과는 원본 JSON 직접 확인 필수 |
| 6 | PART2 v21 changelog 보강 | V9-CCG-4: V9 Phase 2 수정 내역 문서화 |
| 7 | SD-01/SD-03 구조 결정 | GAP-GT1-1: 단일 파일 vs 서브디렉토리, modules/ 위치 결정 |
| 8 | LOCK 전수 재확인 | V9-CCG-3: V1 테이블 형식 LOCK 미기재 가능성 감안, 25개 이상일 수 있음 |

---

## 6. 산출물 파일 인덱스

| 파일 | 대화 | 내용 |
|------|------|------|
| `v10_v8_revalidation.json` | 17 | V8 산출물 1:1 재검증 상세 (5 targets, 17 gaps) |
| `v10_v9_revalidation.json` | 18 | V9 산출물 1:1 재검증 상세 (4 targets, 10 gaps) |
| `v10_revalidation_report.md` | 17+18 | 본 종합 보고서 |
