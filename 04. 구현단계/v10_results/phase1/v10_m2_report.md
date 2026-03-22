# VAMOS v10 Phase 1 — M-2 매핑 검증 보고서

> **에이전트**: M-2 (V1 기능 → PART2 §3 매핑 검증)
> **검증 범위**: Feature Registry의 `version_scope` contains "V1" 전체
> **PART2 대상**: §3 (V1 Phase 1~6), §6 (시스템별 상세) 교차확인
> **생성일**: 2026-03-09

---

## 1. 검증 대상 요약

| 구분 | 건수 |
|------|------|
| **V1 전체 기능** | **2,245** |
| Primary (V1이 첫 번째 버전) | 2,175 |
| Cross-check (V0,V1 등) | 70 |

### Version Scope 분포

| version_scope | 건수 | 매핑 역할 |
|--------------|------|----------|
| V1 | 1,759 | PRIMARY |
| V1,V2 | 215 | PRIMARY |
| V1,V2,V3 | 194 | PRIMARY |
| V1,V3 | 7 | PRIMARY |
| V0,V1 | 49 | CROSS_CHECK |
| V0,V1,V2,V3 | 17 | CROSS_CHECK |
| V0,V1,V2 | 4 | CROSS_CHECK |

---

## 2. 매핑 결과 통계

| 판정 | 건수 | 비율 |
|------|------|------|
| **MATCHED** | **703** | **31.3%** |
| **SPREAD** | **589** | **26.2%** |
| **PARTIAL** | **398** | **17.7%** |
| **MISSING** | **549** | **24.5%** |
| **NOT_APPLICABLE** | **6** | **0.3%** |
| **합계** | **2,245** | **100%** |

### 2.1 MATCHED Phase별 분포

| Phase | 건수 | 주요 내용 |
|-------|------|----------|
| V1_Phase1 | 184 | ORANGE CORE 17개 I-모듈 (I-1~I-20) |
| V1_Phase2 | 95 | Storage, Memory, RAG, Semantic Cache |
| V1_Phase3 | 217 | Workflow, Agent, Blue Node (E-1~E-6) |
| V1_Phase4 | 101 | UI/UX, React 컴포넌트, Zustand |
| V1_Phase5 | 29 | Integration, Test, CI/CD |
| V1_Phase6 | 77 | AI Investing, MCP, S-1 Self-check |

### 2.2 SPREAD (다중 Phase 분산)

- **589건**: 여러 Phase에서 구현 항목이 확인됨
- 주로 핵심 모듈(I-1, I-5 등)이 Phase 1 구현 + Phase 5 테스트 + Phase 3 Workflow 통합 등에 걸쳐 등장

### 2.3 PARTIAL (§6에만 존재, Phase 미배정)

| §6 섹션 | 건수 | 설명 |
|---------|------|------|
| §6.1 UI/UX | 65 | React 컴포넌트 세부, Hooks, Stores |
| §6.7 Agent Teams | 64 | 협업 패턴, LOCK 규칙 |
| §6.9 SDAR | 50 | 자가진단/복구 상세 |
| §6.5 보안 | 45 | 보안 항목 상세 |
| §6.2 Rust/Tauri | 42 | IPC 핸들러, Rust 모듈 |
| §6.8 AI Investing | 40 | 투자 상세 구현 |
| §6.10 Cloud Library | 35 | RT-BNP, DCL 상세 |
| §6.3 테스트 | 28 | 테스트 케이스 상세 |
| §6.4 CI/CD | 23 | 워크플로우 상세 |
| §6.6 MCP | 4 | MCP 상세 |
| §6.11 이벤트 | 2 | 이벤트/로깅 상세 |

> **해석**: §6에만 존재하는 398건은 시스템별 상세 구현 가이드에 기술되어 있으나, §3의 V1 Phase 테이블에 명시적 구현 항목으로 배정되지 않음. §6는 보조 참조 자료이므로 Phase 미배정 자체가 문제는 아니지만, 구현 시 §6 상세를 반드시 참조해야 함.

---

## 3. MISSING 항목 심각도별 분류

### 3.1 요약

| 심각도 | 건수 | 설명 |
|--------|------|------|
| **BLOCKER** | **0** | V1 필수 모듈 누락 없음 |
| **HIGH** | **237** | 중요 기능 누락 (FT-FUNC 199, FT-SEC 36, FT-API 2) |
| **MEDIUM** | **160** | 인프라/설정/스키마/모듈 누락 |
| **LOW** | **152** | 도메인/테스트/UI 세부 누락 |

### 3.2 HIGH 세부 (237건)

**[FT-FUNC] 199건**: 기능 구현 항목이 PART2에서 찾을 수 없음
- EVX-1~5 (검증 확장 기능): Code-as-Policy, Adversarial, Log-prob 등
- 대화 분류/검색/자동 요약 관련 세부 기능
- DomainScore 활용, 단계별 보호 체계
- IDEA 40개 인덱스 관련 기능
- 2단계 승인 로직, 자동 분류 등

**[FT-SEC] 36건**: 보안 관련 미등재 항목
- G3 EvidenceGate, G4 SelfCheckGate 구현
- STRIDE 위협 모델링, AI 특화 위협 트리
- 커뮤니티 스킬 검증 체계

**[FT-API] 2건**: API 관련
- SDK 자동 생성, OpenAPI 스펙

### 3.3 MEDIUM 세부 (160건)

| 카테고리 | 건수 |
|---------|------|
| FT-INFRA | 68 |
| FT-CFG | 40 |
| FT-SCHEMA | 31 |
| FT-MOD | 21 |

### 3.4 LOW 세부 (152건)

| 카테고리 | 건수 |
|---------|------|
| FT-DOMAIN | 75 |
| FT-TEST | 51 |
| FT-UI | 24 |
| FT-MIG | 2 |

---

## 4. 교차 버전 기능 분석 (W-28 방어)

| version_scope | 건수 | M-2 역할 | 비고 |
|--------------|------|----------|------|
| V1 only | 1,759 | PRIMARY | M-2 단독 매핑 |
| V1,V2 | 215 | PRIMARY | M-3 교차확인 |
| V1,V2,V3 | 194 | PRIMARY | M-3/M-4 교차확인 |
| V1,V3 | 7 | PRIMARY | M-4 교차확인 |
| V0,V1 | 49 | CROSS_CHECK | M-1 주 매핑 참조 |
| V0,V1,V2,V3 | 17 | CROSS_CHECK | M-1 주 매핑 참조 |
| V0,V1,V2 | 4 | CROSS_CHECK | M-1 주 매핑 참조 |

---

## 5. 핵심 발견 및 권고사항

### 5.1 긍정적 발견
1. **BLOCKER 0건**: V1 핵심 모듈(I-1~I-20) 전부 PART2 §3에 명시적으로 배정됨
2. **MATCHED+SPREAD 1,292건 (57.5%)**: 과반수 기능이 §3에서 직접 확인
3. **6개 Phase 균형 배치**: Phase 3(Workflow+Agent)이 217건으로 최대, Phase 5(Test)가 29건으로 최소

### 5.2 주의사항
1. **PARTIAL 398건**: §6에만 존재하는 기능들은 구현 시 §6 참조 필수
2. **HIGH MISSING 237건**: FT-FUNC 199건 중 상당수가 설계 문서(D2.0-xx) 원본에서 추출된 세부 기능으로, PART2 요약 수준에서 개별 등재되지 않은 것으로 판단
3. **SPREAD 589건**: 다중 Phase에 분산 구현되는 기능이 많아 구현 시 Phase 간 의존성 관리 필요

### 5.3 권고
1. **HIGH MISSING 237건 검토**: M-5b 통합 에이전트가 §6~§7 전체 검색으로 추가 매핑 가능성 확인 필요
2. **PARTIAL → §3 추가 배정 검토**: §6에만 있는 398건 중 핵심 기능은 §3 Phase 테이블에 명시적 추가 고려
3. **SPREAD 정리**: 589건의 주 구현 Phase를 확정하여 중복 구현 방지

---

## 6. 산출물 파일 목록

| 파일 | 설명 |
|------|------|
| `v10_m2_mapping_result_v2.json` | 전체 매핑 결과 (2,245건, feature별 판정/행번호/증거) |
| `v10_m2_missing_items.json` | MISSING 549건 심각도별/카테고리별 분류 |
| `v10_m2_report.md` | 본 보고서 |
| `m2_mapping_script.py` | 자동 매핑 스크립트 (1차) |
| `m2_refine.py` | 정제 스크립트 (2차, SPREAD→MATCHED 개선) |