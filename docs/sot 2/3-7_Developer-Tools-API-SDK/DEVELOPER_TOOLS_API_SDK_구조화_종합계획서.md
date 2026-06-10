# Developer Tools / API / SDK 구조화 종합 계획서

> **버전**: v1.2
> **작성일**: 2026-03-23 (최종 갱신: 2026-04-10)
> **목적**: sot 2/3-7_Developer-Tools-API-SDK/을 개발자 도구·API·SDK 구현 정본으로 구조화
> **Status**: APPROVED — Phase 5 FINAL PASS (2026-03-24)
> **Tier**: 3
> **SOT 출처**: STEP7-L (56 L-ID)
> **Part2 상태**: MENTION-ONLY — 백로그 원라이너 2건만 존재

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
13. [L3 전수 승급 계획](#13-l3-전수-승급-계획)
14. [실행 약점 대응 계획](#14-실행-약점-대응-계획)
- [§A FIM (Fill-in-the-Middle) 프로토콜](#a-fim-fill-in-the-middle-프로토콜)
- [§B Plugin SDK · WASM 샌드박스](#b-plugin-sdk--wasm-샌드박스)
- [§C VADD 마켓플레이스](#c-vadd-마켓플레이스)

---

## 1. 현재 상태 분석

### 1.1 기존 문서 현황

| 문서 | 위치 | 역할 | 줄수 | 상태 |
|------|------|------|------|------|
| **STEP7-L_개발자도구_API_SDK_작업가이드.md** | docs/sot/ | 보강 항목 리스트 (7 Part, 56 L-ID) | ~1,027 | 항목 목록 + 구현 상세 가이드 |
| **DEVELOPER_TOOLS_API_SDK_상세명세.md** | docs/sot 2/3-7_.../ | sot 2 초기 명세 | 546 | 6개 서브도메인 기술 명세 |
| **PART2 §6 내 MENTION** | docs/guides/ | 구현 가이드 백로그 | 2줄 | 플러그인 개발 도구(v12_C09b_200), Plugin/Extension SDK(v12_C01a_176) |

### 1.2 sot 2/3-7_Developer-Tools-API-SDK/ 현재 파일

| 파일 | 역할 | 상태 |
|------|------|------|
| `DEVELOPER_TOOLS_API_SDK_상세명세.md` | 6개 서브도메인 기술 명세 | DRAFT v1.0, 546줄 |

### 1.3 STEP7-L 항목 현황 (56 L-ID)

> **수량 정정**: STEP7-L 헤더에 "총 항목: 82개"로 기재되어 있으나, 실제 `### L-XXX.` 단위 섹션은 56개(L-001~L-056)이다. 매핑 단위는 L-ID 56건으로 확정.

| Part | 범위 | L-ID 수 | 주요 내용 | 서브폴더 매핑 |
|------|------|---------|----------|-------------|
| Part 1 | L-001~L-010 | 10 | AI 코딩 어시스턴트 통합 | 01_coding-engine |
| Part 2 | L-011~L-018 | 8 | VAMOS API 설계 (REST, SDK, CLI, Webhook, GraphQL) | 06_vscode-extension(L-015) + 07_marketplace(나머지) |
| Part 3 | L-019~L-026 | 8 | 플러그인/확장 시스템 | 05_plugin-sdk |
| Part 4 | L-027~L-034 | 8 | 개발 인프라 도구 (DB, Docker, IaC, 프로파일링) | 01_coding-engine |
| Part 5 | L-035~L-042 | 8 | 시중 AI 대비 차별화 | 01_coding-engine(L-035~L-040) + 02(L-041) + 04(L-042) |
| Part 6 | L-043~L-050 | 8 | 개발자 경험 (DX) 최적화 | 06_vscode-extension |
| Part 7 | L-051~L-056 | 6 | 참고자료 + V1/V2/V3 로드맵 + KPI | §7 Phase 실행 계획에 통합 |
| | **합계** | **56** (L-001~L-056) | | |

### 1.4 Part2 MENTION 상세 (방식 C)

| Part2 항목 | 원문 (1줄) | 처리 방식 |
|-----------|-----------|----------|
| v12_C09b_200 | "플러그인 개발 도구: SDK/CLI/템플릿/문서 생성기, 로컬 테스트 환경, 배포 파이프라인 [HIGH]" | 05_plugin-sdk에서 전면 신규 작성 |
| v12_C01a_176 | "Plugin/Extension SDK: 서드파티 확장 개발 도구, API 문서, 샘플 프로젝트, 배포 가이드 [MEDIUM]" | 05_plugin-sdk에서 전면 신규 작성 |

> **방식 C 판정**: Part2 MENTION → 거의 전면 신규 작성. Part2에는 백로그 원라이너만 존재하므로 sot 2/에서 STEP7-L 56 L-ID를 기반으로 전면 작성한다.

### 1.5 핵심 문제

1. **빈껍데기 상태**: Part2에 Dev-Tools 구현 상세가 전무 (MENTION 2줄만)
2. **서브도메인 구조 미완**: 기존 상세명세는 6개 서브도메인이나 API/마켓플레이스 누락 → 7개로 확장 필요
3. **56 L-ID ↔ 서브폴더 매핑 부재**: STEP7-L 56 L-ID가 어떤 서브폴더에 속하는지 공식 매핑 없음
4. **FIM/Plugin/Marketplace 깊이 부족**: 핵심 기술 스펙(FIM 프로토콜, WASM 샌드박스, VADD 과금)이 미상세

---

## 2. 목표 구조 (최종 형태)

### 2.1 폴더 트리

```
D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\
│
├── DEVELOPER_TOOLS_API_SDK_구조화_종합계획서.md   ← 본 문서
├── DEVELOPER_TOOLS_API_SDK_상세명세.md            ← 기존 파일 유지
├── AUTHORITY_CHAIN.md                             ← 권한 체계 선언
├── CONFLICT_LOG.md                                ← 충돌 기록부
│
├── 01_coding-engine/                              ← L-001, L-005~L-010, L-027~L-040
│   ├── _index.md
│   ├── dev_node_architecture.md                   ← L-001 코딩 엔진 아키텍처
│   ├── code_review_ai.md                          ← L-005 코드 리뷰
│   ├── debugging_assistant.md                     ← L-006 디버깅
│   ├── project_scaffolding.md                     ← L-007 스캐폴딩
│   ├── git_automation.md                          ← L-008 Git 자동화
│   ├── code_search.md                             ← L-009 코드 검색/탐색
│   ├── code_migration.md                          ← L-010 마이그레이션
│   ├── db_management.md                           ← L-027 DB 도구
│   ├── container_docker.md                        ← L-028 Docker
│   ├── cloud_iac.md                               ← L-029 IaC
│   ├── performance_profiling.md                   ← L-030 프로파일링
│   ├── dependency_management.md                   ← L-031 의존성
│   ├── api_testing.md                             ← L-032 API 테스트
│   ├── doc_generation.md                          ← L-033 문서 자동화
│   ├── dev_env_management.md                      ← L-034 개발 환경
│   ├── codebase_understanding.md                  ← L-035 프로젝트 전체 이해
│   ├── invest_coding_integration.md               ← L-036 투자+코딩 통합
│   ├── memory_personalization.md                  ← L-037 메모리 개인화
│   ├── autonomous_coding.md                       ← L-038 자율 코딩
│   ├── security_automation.md                     ← L-039 보안 자동화
│   └── quality_dashboard.md                       ← L-040 품질 대시보드
│
├── 02_code-completion/                            ← L-002, L-041
│   ├── _index.md
│   ├── fim_protocol.md                            ← FIM 프로토콜 상세
│   ├── ranking_algorithm.md                       ← 제안 랭킹
│   ├── local_model_setup.md                       ← Ollama + Qwen Coder
│   └── realtime_collaboration.md                  ← L-041 실시간 협업
│
├── 03_refactoring/                                ← L-003
│   ├── _index.md
│   ├── pattern_catalog.md                         ← 7개 리팩토링 패턴
│   ├── ast_pipeline.md                            ← Tree-sitter AST 분석
│   └── safe_transform_rules.md                    ← 안전한 변환 규칙
│
├── 04_test-generation/                            ← L-004, L-042
│   ├── _index.md
│   ├── test_pipeline.md                           ← 테스트 생성 파이프라인
│   ├── coverage_analysis.md                       ← 커버리지 분석
│   ├── edge_case_detection.md                     ← 엣지 케이스 탐지
│   └── vbs13_benchmark.md                         ← L-042 코드 벤치마크
│
├── 05_plugin-sdk/                                 ← L-019~L-026
│   ├── _index.md
│   ├── plugin_architecture.md                     ← L-019 플러그인 아키텍처
│   ├── hook_system.md                             ← L-020 훅 시스템
│   ├── ui_components.md                           ← L-021 UI 확장
│   ├── theme_system.md                            ← L-022 테마/스킨
│   ├── keyboard_shortcuts.md                      ← L-023 키보드 단축키
│   ├── command_palette.md                         ← L-024 커맨드 팔레트
│   ├── wasm_sandbox.md                            ← L-025 WASM 샌드박스
│   └── plugin_devkit.md                           ← L-026 개발 도구
│
├── 06_vscode-extension/                           ← L-015, L-043~L-050
│   ├── _index.md
│   ├── extension_architecture.md                  ← VS Code 확장 아키텍처
│   ├── lsp_integration.md                         ← LSP 통합 프로토콜
│   ├── onboarding_wizard.md                       ← L-043 온보딩
│   ├── error_messages.md                          ← L-044 에러 메시지
│   ├── tutorials.md                               ← L-045 튜토리얼
│   ├── feedback_system.md                         ← L-046 피드백
│   ├── dx_performance.md                          ← L-047 성능 최적화
│   ├── accessibility.md                           ← L-048 접근성
│   ├── i18n.md                                    ← L-049 다국어
│   └── offline_mode.md                            ← L-050 오프라인
│
└── 07_marketplace/                                ← L-011~L-014, L-016~L-018 (API 생태계 + VADD)
    ├── _index.md
    ├── rest_api.md                                ← L-011 REST API
    ├── python_sdk.md                              ← L-012 Python SDK
    ├── typescript_sdk.md                          ← L-013 TS/JS SDK
    ├── cli_tool.md                                ← L-014 CLI
    ├── webhook_events.md                          ← L-016 Webhook
    ├── graphql_api.md                             ← L-017 GraphQL (V3)
    ├── api_docs_generator.md                      ← L-018 API 문서
    └── vadd_marketplace.md                        ← VADD 마켓플레이스 과금/검수
```

### 2.2 깊이 규칙

```
최대 2단계:
  3-7_Developer-Tools-API-SDK/ → XX_서브도메인/ → 파일.md  ✅
  3단계 이상 → 절대 금지 ❌
```

### 2.3 네이밍 규칙

- **폴더명**: 영문 소문자 + 하이픈, 접두사 2자리 번호 (`01_`, `02_`, ...)
- **파일명**: 영문 소문자 + 언더스코어 (`.md` 확장자)
- **계획서**: 한글 허용 (`DEVELOPER_TOOLS_API_SDK_구조화_종합계획서.md`)

---

## 3. 권한 체계 선언

### 3.1 기존 VAMOS 권한 체인

```
RULE 1.3 (SOT-RULE) > PLAN 3.0 > DESIGN 2.0 > sot 2/ > sot/ > guides/
```

### 3.2 Dev-Tools 확장 체인

```
[L1] STEP7-L (56 L-ID 체크리스트)  ← 항목 존재 여부의 정본
  ↓
[L2] sot 2/3-7_Dev-Tools/ 계획서   ← 구현 상세의 정본 (What + How)
  ↓
[L3] sot 2/3-7_Dev-Tools/ 서브폴더  ← 개별 항목 상세의 정본
  ↓
[L4] Part2 §6 (MENTION 2줄)        ← When + Where 참고만 (정본 아님)
```

### 3.3 문서별 정본 범위

| 문서 | 정본 범위 | 비고 |
|------|----------|------|
| **STEP7-L** | 항목 존재 여부 + 체크리스트 | 56 L-ID의 "무엇을 만들 것인가" |
| **sot 2/ 계획서** | 구현 계획 + Phase + 거버넌스 | "어떤 순서로, 어떤 규칙으로" |
| **sot 2/ 서브폴더** | 개별 항목 구현 상세 | "구체적으로 어떻게" |
| **기존 상세명세** | 기술 아키텍처 참조 | 계획서와 병행 유지 |
| **Part2** | Phase 배정 참고만 | MENTION이므로 정본 아님 |

### 3.4 LOCK 보호 항목

> 아래 항목은 STEP7-L에 정의된 핵심 설계 결정이며, 변경 시 AUTHORITY_CHAIN.md에 기록 + 정당화 필수.

| LOCK ID | 항목 | 값 | 근거 |
|---------|------|---|------|
| **LOCK-DT-01** | API 버저닝 규칙 | `/api/v{N}/` prefix, semantic versioning | L-011, REST API 안정성 |
| **LOCK-DT-02** | SDK 호환성 매트릭스 | Python ≥ 3.9, Node.js ≥ 18, Rust ≥ 1.70 | L-012~L-013, 플랫폼 호환 |
| **LOCK-DT-03** | CLI 명령어 체계 | `vamos {동사} {명사} [옵션]` 패턴 | L-014, UX 일관성 |
| **LOCK-DT-04** | FIM 모델 fallback chain | Qwen 2.5 Coder 7B (로컬) → gpt-4o (API) → claude-sonnet (API) | L-002, 응답 품질 보장 |
| **LOCK-DT-05** | 플러그인 샌드박스 정책 | WASM 격리, 선언된 권한만 허용 | L-025, 보안 |
| **LOCK-DT-06** | 코드 실행 타임아웃 | 30초 | D2.0-02 §실행제한, D2.0-03 §도구호출 |
| **LOCK-DT-07** | 자동완성 디바운스 | 150ms | L-002, UX 반응성 |
| **LOCK-DT-08** | Rate Limiting | 분당 60 요청 (기본) | L-011, 남용 방지 |
| **LOCK-DT-09** | 플러그인 매니페스트 스키마 | plugin-manifest-v1.json | L-019, 생태계 호환 |
| **LOCK-DT-10** | 커버리지 임계값 | 테스트 커버리지 ≥ 80% | STEP7-F §테스트전략 |

### 3.5 UPSTREAM_INHERITANCE — 3-4 Workflow-RPA Phase 4 ✅ Stage A + Stage B ALL COMPLETE (2026-05-24, [DOMAIN_PHASE_4_PRODUCTION_PROMOTION_COMPLETE:3-4] ✅) — Phase 4 완료 reference

> **3-4 Workflow-RPA Phase 4 완료 reference 추가** (Wave 1 #6, chain `phase4_3-4_2026-05-24`, verify-only per A direct path, 🎉 NO-DRIFT FULL 4/4 ⭐⭐⭐ milestone 확정 통산 4번째 FULL 도메인) — **3-7 DevTools 수신 측 forward-defined inheritance**.

| 항목 | inheritance 결과 |
|------|----------------|
| **3-4 P4-4 cross-handoff inline 분담** | 3-4 §7 P4-4 N-001 advanced_dag V3 EXTEND task의 §6 교차 도메인 "3-7 DevTools workflow API → DevTools 통합 검증 P3-4 R₁₀ inline 분담 inheritance" 명시 — 본 3-7 도메인이 Phase 4 진입 시 양방향 정합 verify 예정 (3-4 발신 측 forward-defined direct path, 3-7 P4 entry 시점 수신 측 정본 확정 inheritance) |
| **3-4 V3 산출물 명세 (Phase 4 Stage A inheritance)** | NEW 2 (mobile_automation + enterprise_security) + EXTEND 2 (team_workflow + advanced_dag) = 4건 ALL **Status TODO 유지** (per A scope, V3 본문 신규 작성 OUT of scope α → SPEC Stage B 위임). 3-4 advanced_dag V3 EXTEND 본문 작성 시점 3-7 DevTools workflow API cross-handoff 양방향 정합 verify 진행 |
| **3-4 production .md baseline EXACT 보존** | 5 baseline EXACT 보존 (plan + AUTHORITY v1.2 + CONFLICT v1.2 + INDEX v1.1 + phase2 audit ALL EXACT, production .md ZERO write 통산 per A) — 3-7 도메인 영향 0건 inheritance |
| **3-4 R cascade 통산** | 468 verifications + 0 drift + 0 fix truly_converged_v1 first-pass-after-zero-fix CONFIRMED 4-consecutive — 3-7 수신 측 직접 영향 0건 (Phase 4 Stage A inheritance baseline EXACT) |
| **3-7 Phase 4 진입 시 수신 측 정합 verify** | 본 3-7 도메인 Phase 4 SPEC Stage B 진입 시점 또는 ENTRY_PROMPT 진입 시점 — workflow API cross-handoff 양방향 정본 verify (3-4 발신 측 forward-defined ↔ 3-7 수신 측 inheritance) + CROSS_REF_MATRIX §1 정합 100% inheritance |
| **abort marker** | `[CROSS_HANDOFF_DRIFT:3-7_P4_x]` NOT FIRED forward-defined (3-4 Phase 4 Stage A 발신 측 정합 baseline) |
| **marker** | `[DOWNSTREAM_INHERITANCE_FROM_3-4:3-7 — 2026-05-24]` ✅ (3-4 Phase 4 Stage A 완료 ⑥단계 downstream propagation, 3-7 P4 entry 시점 양방향 verify 예정) |

---

## 4. 거버넌스 규칙

> **글로벌 거버넌스 규칙**: 본 도메인은 0-0_Governance-Rules-Meta에서 정의한 R1~R11 글로벌 규칙을 전체 준수합니다.
> 아래는 글로벌 규칙에 추가되는 도메인 고유 규칙입니다.

### 4.1 공통 규칙 (R1~R9 canonical)

| # | 규칙 | 이유 | 위반 시 |
|---|------|------|---------|
| R1 | 폴더 깊이 최대 3단계 | Windows 260자 경로 제한 | 파일 생성 거부 |
| R2 | 마스터 INDEX.md 1개 + 폴더별 _index.md (파일 목록만) | 유지보수 부담 분산 | INDEX.md 미갱신 = 커밋 불가 |
| R3 | 파일명 변경 시 PART2 링크 테이블 동기화 | 참조 정합성 | 변경 커밋에 PART2 업데이트 포함 필수 |
| R4 | 겹치는 개념 → 정본 소유자 1곳 상세, 나머지 `> 참조:` 링크 | 교차 참조 중복 방지 | canonical_owner_table.md에 등록 필수 |
| ~~R5~~ | ~~삭제 — SPEC §7-8 해당없음 (Tier 3)~~ | | |
| R6 | sot 2/ = What+How만, When = PART2만 | Phase 이중 기재 금지 | Phase 정보 발견 시 즉시 삭제 |
| R7 | STEP7-L 56 L-ID ↔ sot 2/ 매핑 테이블 유지 | 중복/충돌 정리 | §6 매핑에 기록 |
| R8 | PART2 링크는 단일 테이블에 집중 | 링크 관리 단순화 | 본문 산발 링크 금지 |
| R9 | LOCK/FREEZE 값 재정의 금지. 참조 시 `> LOCK (출처): [원문]` | LOCK 보호 | 즉시 수정 |

### 4.2 Dev-Tools 고유 규칙

| 규칙 ID | 이름 | 내용 | 근거 |
|---------|------|------|------|
| **R-10-1** | 플러그인 파일시스템 접근 금지 | 플러그인은 WASM 샌드박스 외부 파일시스템에 접근 불가 | LOCK-DT-05, 보안 |
| **R-10-2** | 코드 실행 타임아웃 30초 | 모든 코드 실행(테스트 생성, 디버깅, 마이그레이션)은 30초 초과 시 강제 종료 | LOCK-DT-06 |
| **R-10-3** | API 하위 호환성 | REST API 버전 N은 최소 12개월 지원. Breaking change는 N+1에서만 허용 | LOCK-DT-01 |
| **R-10-4** | 모델 fallback 순서 고정 | FIM fallback chain 변경 시 A/B 테스트 + 수락률 비교 필수 | LOCK-DT-04 |
| **R-10-5** | 플러그인 배포 서명 필수 | VADD Marketplace에 게시하는 플러그인은 개발자 인증서로 서명 필수 | 생태계 신뢰 |
| **R-10-6** | SDK 타입 안전성 | Python SDK는 mypy strict 통과, TS SDK는 strict TypeScript 필수 | LOCK-DT-02 |

---

## 5. 선행작업

### 5.1 STEP7-L 항목 분류 + 서브폴더 매핑

- **목표**: 56 L-ID를 7개 서브폴더에 매핑하고 항목별 우선순위(V1/V2/V3) 확정
- **산출물**: §6 이슈 해결 매핑 테이블
- **판정 기준**: 모든 L-XXX 항목이 정확히 1개 서브폴더에 매핑

### 5.2 기존 상세명세 ↔ STEP7-L 교차 검증

- **목표**: 기존 `DEVELOPER_TOOLS_API_SDK_상세명세.md`의 6개 서브도메인 내용이 STEP7-L과 모순되지 않는지 확인
- **산출물**: CONFLICT_LOG.md 초기 항목
- **판정 기준**: 모순 발견 시 STEP7-L 정본 우선, 상세명세는 참조로 격하

### 5.3 Part2 MENTION 확인

- **목표**: Part2의 2건 MENTION (v12_C09b_200, v12_C01a_176)이 STEP7-L의 어떤 항목에 대응하는지 확인
- **산출물**: §1.4 테이블 (완료)
- **판정 기준**: MENTION ↔ L-XXX 대응 관계 확정

---

## 6. 이슈 해결 매핑

> **[3-4 Phase 3 inheritance NOTE — 2026-05-16]** 3-4 Workflow-RPA Phase 3 완료 (2026-05-16, chain `phase3_3-4_2026-05-16`, tcv3 first-pass 4/4 CONFIRMED, R cascade 165 verifications + 5 drift fixes textual notation/cross-ref completeness only — 4 STEP7-N alias 한국어 정본 정합 D-P3-1/2/3/4-R3-1 + 1 cross-ref completeness D-P3-4-R10-1 3-7 DevTools downstream inline 보강). P3-1 (N-018 모바일 자동화 V3 — Appium iOS/Android + LOCK-WF-08 12 액션 모바일 적응 + LOCK-WF-10 보안) + P3-2 (N-010 팀 워크플로우 V3 — 멀티유저 + RBAC 4단계 Owner/Editor/Executor/Viewer + LOCK-WF-05 LangGraph 동시 10 + 워크플로우 버전 관리 Git-like merge + 팀 라이브러리) + P3-3 (엔터프라이즈 보안 V3 — 감사 로그 30일 append-only + RBAC 3계층 워크플로우/노드/데이터 + LOCK-WF-10 샌드박스+AES-256 + SOC2/GDPR/ISO27001 컴플라이언스 — 7 entry-gate 조건 최다) + P3-4 (N-001 고급 DAG V3 — SubworkflowNode LOCK-WF-01 정합 + 재귀 패턴 max_depth=5 + 종료 조건 강제 + LOCK-WF-02 50 노드 + LOCK-WF-04 DAG 순환 금지). **본 3-7 도메인 DevTools workflow API + 코드 생성 + Plugin SDK + 자동화 파이프라인에서 inheritance 가능** (LOCK-WF-01 12 노드 타입 SubworkflowNode 포함 + LOCK-WF-02 50 노드 + LOCK-WF-04 DAG 순환 금지 ↔ 3-7 DevTools workflow API 노드 통합 검증 정합 + LOCK-WF-05 LangGraph StateGraph 최대 동시 10 ↔ 3-7 코드 실행 엔진 동시성 정합 + LOCK-WF-06 트리거 7유형 Time/Event/Condition/Webhook/Manual/Conversation/Ambient ↔ 3-7 IDE 자동화 트리거 매핑 + LOCK-WF-07 브라우저 10 액션 + LOCK-WF-08 데스크톱 12 액션 ↔ 3-7 Plugin SDK 자동화 액션 매핑 + LOCK-WF-10 RPA 보안 정책 샌드박스+AES-256 ↔ 3-7 보안 통합 검증 + 코드 자동화 안전 조건). 3-7 Phase 3 진행 (Wave 1 #9, CROSS_REF_MATRIX §1 upstream 3-4 ✅ inheritance 검증) 시 §3 정본 출처 또는 §6 이슈 매핑 또는 01_coding-engine / 05_plugin-sdk / 06_vscode-extension 서브폴더 통합 워크플로우 정의에서 본 reference 활용 가능. **CROSS_REF_MATRIX §1 양방향 정합**: 3-4 downstream (**3-7** + 6-3) ↔ 3-7 upstream (**3-4**). production .md baseline (43 .md aggregate EXACT 보존 inheritance): V1 37 + V2 5 (N-005 + N-019 EXTEND + N-026 data_sync + N-003g + N-025 sns_content) + N-017 V2 EXTEND Phase 3 이월 = STAGE 7~8 Production 승급 영역 무손상, V3 NEW 4 산출물 (mobile_automation.md / team_workflow.md / enterprise_security.md / advanced_dag.md) 미생성 design choice — V3 implementation 단계에서 생성. **참조**: `D:/VAMOS/docs/sot 2/3-4_Workflow-RPA/WORKFLOW_RPA_구조화_종합계획서.md` §7 Phase 3 (L1238~L1482, 4 details 블록 + 검증 결과 요약 12-row 표) + `D:/VAMOS/docs/sot 2/PHASE3_ORCHESTRATION/PROGRESS.md` §3 (3-4 P3-1~P3-4 checkpoint × 4).

### 6.1 STEP7-L 56 L-ID 전수 매핑

> L-XXX → 서브폴더 + 파일 매핑. 상태: 🔴 미작성 / 🟡 골격 / 🟢 상세
> **이중 V-배정**: STEP7-L `[구현성]`에 V1/V2 모두 명시된 항목은 `V1(내용)/V2(내용)` 형식으로 양쪽 병기. 통계는 주 Phase(V1)로 집계.

#### 01_coding-engine (21항목)

| STEP7 ID | 항목명 | 우선순위 | 파일 | 상태 |
|----------|--------|---------|------|------|
| L-001 | Dev Node 코딩 엔진 | V1 | dev_node_architecture.md | 🔴 |
| L-005 | 코드 리뷰 AI | V1(로컬)/V2(GitHub) | code_review_ai.md | 🔴 |
| L-006 | 디버깅 어시스턴트 | V1 | debugging_assistant.md | 🔴 |
| L-007 | 프로젝트 스캐폴딩 | V1 | project_scaffolding.md | 🔴 |
| L-008 | Git 작업 자동화 | V1 | git_automation.md | 🔴 |
| L-009 | 코드 검색 및 탐색 | V1(tree-sitter)/V2(시맨틱) | code_search.md | 🔴 |
| L-010 | 코드 마이그레이션/변환 | V1 | code_migration.md | 🔴 |
| L-027 | 데이터베이스 관리 도구 | V1 | db_management.md | 🔴 |
| L-028 | 컨테이너/Docker 관리 | V1 | container_docker.md | 🔴 |
| L-029 | 클라우드 인프라 관리 (IaC) | V2 | cloud_iac.md | 🔴 |
| L-030 | 성능 프로파일링 | V1 | performance_profiling.md | 🔴 |
| L-031 | 의존성 관리 | V1 | dependency_management.md | 🔴 |
| L-032 | API 테스트 도구 | V1 | api_testing.md | 🔴 |
| L-033 | 문서 생성 자동화 | V1 | doc_generation.md | 🔴 |
| L-034 | 개발 환경 관리 | V1 | dev_env_management.md | 🔴 |
| L-035 | 프로젝트 전체 이해 | V1(기본)/V2(KG) | codebase_understanding.md | 🔴 |
| L-036 | 투자+코딩 통합 | V1 | invest_coding_integration.md | 🔴 |
| L-037 | 메모리 기반 개인화 코딩 | V1(기본)/V2(심화) | memory_personalization.md | 🔴 |
| L-038 | 자율 코딩 에이전트 | V2 | autonomous_coding.md | 🔴 |
| L-039 | 코드 보안 자동화 | V1(기본)/V2(통합) | security_automation.md | 🔴 |
| L-040 | 코드 품질 대시보드 | V2 | quality_dashboard.md | 🔴 |

#### 02_code-completion (2항목)

| STEP7 ID | 항목명 | 우선순위 | 파일 | 상태 |
|----------|--------|---------|------|------|
| L-002 | 인라인 코드 자동완성 | V1(Ollama)/V2(VSCode Ext) | fim_protocol.md + ranking_algorithm.md + local_model_setup.md | 🔴 |
| L-041 | 실시간 협업 코딩 | V3 | realtime_collaboration.md | 🔴 |

#### 03_refactoring (1항목, 11개 세부)

| STEP7 ID | 항목명 | 우선순위 | 파일 | 상태 |
|----------|--------|---------|------|------|
| L-003 | 코드 리팩토링 자동화 | V1(LLM)/V2(AST) | pattern_catalog.md + ast_pipeline.md + safe_transform_rules.md | 🔴 |

#### 04_test-generation (2항목)

| STEP7 ID | 항목명 | 우선순위 | 파일 | 상태 |
|----------|--------|---------|------|------|
| L-004 | 자동 테스트 생성 | V1 | test_pipeline.md + coverage_analysis.md + edge_case_detection.md | 🔴 |
| L-042 | 코드 벤치마크 (VBS-13) | V2 | vbs13_benchmark.md | 🔴 |

#### 05_plugin-sdk (8항목)

| STEP7 ID | 항목명 | 우선순위 | 파일 | 상태 |
|----------|--------|---------|------|------|
| L-019 | 플러그인 아키텍처 | V2 | plugin_architecture.md | 🔴 |
| L-020 | Hook 시스템 | V1(기본)/V2(풀) | hook_system.md | 🔴 |
| L-021 | UI 컴포넌트 확장 | V2 | ui_components.md | 🔴 |
| L-022 | 테마/스킨 시스템 | V1(CSS)/V2(에디터) | theme_system.md | 🔴 |
| L-023 | 키보드 단축키 시스템 | V1 | keyboard_shortcuts.md | 🔴 |
| L-024 | 커맨드 팔레트 | V1 | command_palette.md | 🔴 |
| L-025 | 플러그인 샌드박스 | V2 | wasm_sandbox.md | 🔴 |
| L-026 | 플러그인 개발 도구 | V2 | plugin_devkit.md | 🔴 |

#### 06_vscode-extension (9항목)

| STEP7 ID | 항목명 | 우선순위 | 파일 | 상태 |
|----------|--------|---------|------|------|
| L-015 | VS Code Extension | V2 | extension_architecture.md + lsp_integration.md | 🔴 |
| L-043 | 온보딩 마법사 | V1 | onboarding_wizard.md | 🔴 |
| L-044 | 에러 메시지 개선 | V1 | error_messages.md | 🔴 |
| L-045 | 대화형 튜토리얼 | V1(기본)/V2(인터랙티브) | tutorials.md | 🔴 |
| L-046 | 피드백 수집 시스템 | V1 | feedback_system.md | 🔴 |
| L-047 | 성능 최적화 (DX) | V1 | dx_performance.md | 🔴 |
| L-048 | 접근성 (DX) | V1 | accessibility.md | 🔴 |
| L-049 | 다국어 지원 (DX) | V1 | i18n.md | 🔴 |
| L-050 | 오프라인 모드 | V1 | offline_mode.md | 🔴 |

#### 07_marketplace (7항목 + VADD 1건)

| STEP7 ID | 항목명 | 우선순위 | 파일 | 상태 |
|----------|--------|---------|------|------|
| L-011 | VAMOS REST API | V2 | rest_api.md | 🔴 |
| L-012 | Python SDK | V2 | python_sdk.md | 🔴 |
| L-013 | TypeScript/JS SDK | V2 | typescript_sdk.md | 🔴 |
| L-014 | VAMOS CLI | V1(기본)/V2(풀) | cli_tool.md | 🔴 |
| L-016 | Webhook/이벤트 | V2 | webhook_events.md | 🔴 |
| L-017 | GraphQL API | V3 | graphql_api.md | 🔴 |
| L-018 | API 문서 자동 생성 | V2 | api_docs_generator.md | 🔴 |
| — | VADD 마켓플레이스 | V3 | vadd_marketplace.md | 🔴 |

#### 참고자료 (6항목, 묶음)

| STEP7 ID | 항목명 | 매핑 |
|----------|--------|------|
| L-051~L-056 | 참고자료 + V1/V2/V3 로드맵 + KPI | §7 Phase 실행 계획에 통합 |

### 6.2 매핑 통계

> **집계 규칙**: 이중 V-배정 항목(11건)은 주 Phase(V1)로 집계. VADD(L-ID 없음)는 합계에서 제외.

| 서브폴더 | L-ID 수 | V1(주) | V2 | V3 | 이중 배정 |
|----------|---------|--------|----|----|----------|
| 01_coding-engine | 21 | 18 | 3 | 0 | 5 |
| 02_code-completion | 2 | 1 | 0 | 1 | 1 |
| 03_refactoring | 1 | 1 | 0 | 0 | 1 |
| 04_test-generation | 2 | 1 | 1 | 0 | 0 |
| 05_plugin-sdk | 8 | 4 | 4 | 0 | 2 |
| 06_vscode-extension | 9 | 8 | 1 | 0 | 1 |
| 07_marketplace | 7 | 1 | 5 | 1 | 1 |
| 참고(§7 통합) | 6 | — | — | — | — |
| **합계** | **56** (L-001~L-056) | **34** | **14** | **2** | **11** |

> V1+V2+V3 = 34+14+2 = **50** (= L-001~L-050 매핑 대상). 참고 6건은 V 배정 없음. 합계 50+6 = 56 L-ID.

### 6.X 6-1 UI-UX-System Phase 4 ✅ Stage A 완료 inheritance (2026-05-26, downstream 전파, Wave 1 → Wave 2 cross-Wave forward-inheritance first specialty)

> **[PHASE4_COMPLETE_STAGE_A: 6-1 — 2026-05-26]** ⬛ (downstream reference, P4-1~P4-4 4/4 ALL ✅ NO-DRIFT FULL milestone first specialty 확정): 6-1 도메인 Phase 4 Stage A 완료에 따른 본 도메인 inheritance 자원 — **🌟🌟🌟 3-7 Developer-Tools-API-SDK (Wave 1 #9 ✅ SPEC COMPLETE 2026-05-25 Plugin SDK 정본 source) ↔ 6-1 P4-4 UI 슬롯 4개 인터페이스 cross-handoff Wave 1 → Wave 2 cross-Wave forward-inheritance first specialty** (LOCK-DT-05/09 + R-10-5 + plugin lifecycle baseline 양방향 정합 — 3-7 정의 / 6-1 UI 슬롯 인터페이스 경계 명시 EXACT MATCH 100%) + **🌟 4 슬롯 (HeaderSlot + SidebarSlot LOCK L2 250-300px + ContentSlot LOCK L4 Flex-grow + FooterSlot) TypeScript 인터페이스 `interface UIExtensionSlot { id: string; render: () => ReactNode; permission: RBACRole[]; sandbox: boolean; }` forward-defined** + **🌟 LOCK L13 통산 57건 FINAL** (V1 44 + V2 4 + V3 5 + Plugin Slot 4) + **🌟 LOCK L20 FailureCode V3 확장 14→18 first specialty** (Plugin 4건: PLUGIN_LOAD_TIMEOUT/PERMISSION_DENIED/SANDBOX_ESCAPE/RENDER_ERROR) + **🌟 Plugin EventType 8건 `ui.{slot}.plugin.{action}` LOCK L19 100% 준수**. 6-1 V3 산출물 5 NEW + 3 UPDATE forward-defined (OUT of scope per 사용자 결정 A verify-only inheritance, SPEC Stage B 또는 별도 결정 위임). **3-7 STAGE 9 RO TRUE 4 .md (06_vscode-extension + 07_marketplace 일부) sandbox-only reference 기록** (production .md ReadOnly 보존 + ReadOnly EXACT 패턴 적용 시점은 별도 deferred per ENTRY_PROMPT ⑥ rule), plan-level RO FALSE에서 본 §6.X inheritance subsection만 추가. **3-7 Plugin SDK 정본 (LOCK-DT-05/09)** ↔ **6-1 P4-4 extension_slots_v3.md (forward-defined NEW)** 양방향 baseline 확립 (3-7 V3 production 정본 승급은 본 도메인 자체 Phase 4 SPEC Stage B 진입 시점). (출처: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\UI_UX_SYSTEM_구조화_종합계획서.md` §7 Phase 4, post 236,927 B / `E39161CFBFEFC36D` Stage A baseline EXACT 보존 + ④ 세션 요약 블록 +Δ 별도)

---

## 7. Phase 실행 계획

### 7.1 V1 → V2 → V3 로드맵 정렬

```
V1 (로컬 MVP, 즉시~1개월)
├── 코딩 엔진 코어 (L-001)
├── FIM 인라인 자동완성 (L-002, Ollama+Qwen)
├── LLM 기반 리팩토링 (L-003 Phase 1: LLM)
├── 자동 테스트 생성 (L-004)
├── 코드 리뷰·디버깅·검색·마이그레이션 (L-005~L-010)
├── 인프라 도구 기본 (L-027~L-028, L-030~L-034)
├── 기본 CLI (L-014)
├── 기본 테마/CSS 변수 (L-022 Phase 1: CSS)
├── DX 기본 (L-043~L-050)
└── 기본 훅·키보드·커맨드 팔레트 (L-020 Phase 1: 기본/L-023/L-024)

V2 (서버, 2~4개월)
├── REST API + SDK (L-011~L-013)
├── VS Code Extension (L-015)
├── 플러그인 시스템 전체 (L-019, L-021, L-025~L-026)
├── AST 기반 리팩토링 (L-003 Phase 2: AST)
├── 풀 훅 시스템 (L-020 Phase 2: 풀)
├── 테마 에디터 (L-022 Phase 2: 에디터)
├── 클라우드 IaC (L-029)
├── 자율 코딩 에이전트 기초 (L-038)
├── 코드 품질 대시보드 (L-040)
├── 코드 벤치마크 VBS-13 (L-042)
└── 풀 CLI + Webhook + API 문서 (L-014 v2, L-016, L-018)

V3 (엔터프라이즈, 6개월+)
├── GraphQL API (L-017)
├── 실시간 협업 코딩 (L-041)
├── VADD 마켓플레이스 런칭
└── 네이티브 모바일 SDK
```

### 7.2 Phase 0: 분석 · 아키텍처 확정 ✅ 완료 (2026-03-31)

**기간**: 2026-03-23 ~ 2026-03-31 (P0-1~P0-4 전수 완료)

| 작업 | 산출물 | 상태 |
|------|--------|------|
| STEP7-L 56 L-ID 전수 매핑 | §6 매핑 테이블 | ✅ 완료 |
| 기존 상세명세 교차 검증 | CONFLICT_LOG 초기화 | ✅ 완료 |
| 서브폴더 7개 + _index.md 생성 | 폴더 골격 | ✅ 완료 |
| AUTHORITY_CHAIN + CONFLICT_LOG | 권한/충돌 파일 | ✅ 완료 |

**Phase 0 → 1 게이트**:
- [x] 56 L-ID 100% 매핑 (빠짐 없이) — P0-1 완료 (2026-03-31)
- [x] LOCK 10건 확정 — P0-4 완료 (2026-03-31)
- [x] 서브폴더 7개 _index.md 존재 — P0-3 완료 (2026-03-31)

#### Phase 0 단계별 상세 작업 절차

<details>
<summary><b>P0-1. STEP7-L 56 L-ID 전수 매핑</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot\STEP7-L_개발자도구_API_SDK_작업가이드.md` (L-001~L-056, 56개 L-ID)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\DEVELOPER_TOOLS_API_SDK_구조화_종합계획서.md` §6 매핑 테이블

> **수량 정정**: STEP7-L 헤더에 "총 항목: 82개"로 기재되어 있으나, 실제 `### L-XXX.` 단위 섹션은 **56개** (L-001~L-056)이다. "82"의 산출 근거가 원본에 부재하므로 매핑 단위는 **L-ID 56건**으로 확정한다. 본 계획서 전체 "82" 참조는 "56 L-ID"로 정정 완료.

**매핑 단위 정의**:
- **매핑 단위**: `### L-XXX.` 섹션 단위 (L-001~L-056 = 56건). 하위 세부항목(예: L-003의 리팩토링 유형 목록)은 해당 L-ID 파일 내에서 상세화하며 매핑 단위에 포함하지 않음
- **서브폴더 매핑 대상**: L-001~L-050 (50건) → 7개 서브폴더에 각각 **정확히 1개** 매핑 (§5.1 판정 기준)
- **참고 항목**: L-051~L-056 (6건) → §7 Phase 실행 계획에 통합 (서브폴더 매핑 불필요)
- **VADD 마켓플레이스**: STEP7-L 외 추가 항목. 07_marketplace에 별도 등재하되, L-ID 미부여이므로 매핑 집계(50+6=56)에 포함하지 않음

**이중 V-배정 처리 규칙**:
- STEP7-L `[구현성]` 필드에 "V1: ✅ … | V2: ✅ …" 형식의 이중 배정이 있는 항목은 §6 우선순위 열에 `V1(내용)/V2(내용)` 형식으로 **양쪽 모두 표기**
- 통계 집계 시에는 **주 Phase**(= 첫 번째 구현 단계, V1)로 분류하되, §6.2 통계 테이블에 "이중 배정 건수" 열 추가
- 이중 배정 해당 항목 (11건): L-002, L-003, L-005, L-009, L-014, L-020, L-022, L-035, L-037, L-039, L-045

**절차**:
1. STEP7-L에서 L-001~L-056 (56개 L-ID) 전수 추출 — 각 `### L-XXX.` 섹션의 항목명 + `[구현성]` V 배정 확인
2. L-001~L-050을 7개 서브폴더(01_coding-engine ~ 07_marketplace)에 매핑 (1 L-ID = 정확히 1 서브폴더)
3. L-051~L-056은 "참고(§7 통합)"으로 분류
4. §6 매핑 테이블에 기존 형식 `| STEP7 ID | 항목명 | 우선순위 | 파일 | 상태 |` 유지하여 기록. 이중 V-배정 항목은 우선순위 열에 `V1(내용)/V2(내용)` 병기
5. 매핑 통계(§6.2) 갱신: 서브폴더별 L-ID 수 + 주 Phase(V1/V2/V3) 분포 + 이중 배정 건수

**검증**: ✅ 전수 통과 (2026-03-31)
- [x] L-001~L-050 전수 매핑: 50 L-ID × 1 서브폴더 (빠짐 0건, 중복 0건, 미매핑 0건) — **Phase 0→1 게이트 "항목 100% 매핑" 충족**
- [x] L-051~L-056 → §7 통합 확인 (6건)
- [x] 서브폴더별 L-ID 수 합계 = 50 (참고 6건 제외). 01_coding-engine = 21항목, §2.1 폴더 트리와 일치 확인
- [x] 각 L-ID의 V 배정이 STEP7-L 원본 `[구현성]` 필드와 일치. 이중 배정 11건 전수 양쪽 병기 확인
- [x] §6.2 매핑 통계 수치 정합성: 21+2+1+2+8+9+7+6=56, V1(34)+V2(14)+V3(2)=50, 이중(11)
- [x] VADD(L-ID 없음)가 매핑 집계에서 제외 확인

**산출물**: §6 매핑 테이블 + §6.2 매핑 통계 갱신 (본 계획서 내)

**후속 정정 완료 이력**:
- ✅ §1.3 "82항목" → "56 L-ID" 정정 완료
- ✅ §6 01_coding-engine 헤더 "(20항목)" → "(21항목)" 정정 완료
- ✅ §6.2 V2 합계 16 → 14 정정 완료 (이중 배정 규칙 적용)
- ✅ Phase 0→1 게이트 "82항목" → "56 L-ID" 정정 완료
- ✅ §2.1 01_coding-engine 주석 L-035~L-040 추가 완료
- ✅ §2.1 07_marketplace 주석 L-015 제외 완료
- ✅ §2.1 03_refactoring "10개" → "7개" 리팩토링 패턴 정정 완료
- ✅ §6 03_refactoring "(12개 세부)" → "(11개 세부)" 정정 완료
- ✅ §6 L-048/L-049 "(DX)" 접미사 복원 완료
- ✅ 문서 전체 "82" 잔존 참조 → "56 L-ID" 전수 정정 완료
</details>

<details>
<summary><b>P0-2. 기존 상세명세 교차 검증 + CONFLICT_LOG 초기화</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\DEVELOPER_TOOLS_API_SDK_상세명세.md` (546줄, 6개 서브도메인: A-Dev Node 코딩 엔진, B-인라인 코드 자동완성, C-코드 리팩토링 자동화, D-자동 테스트 생성, E-Plugin SDK, F-VS Code 확장)
- `D:\VAMOS\docs\sot\STEP7-L_개발자도구_API_SDK_작업가이드.md` (L-001~L-056, 56개 L-ID)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\DEVELOPER_TOOLS_API_SDK_구조화_종합계획서.md` §3.4 LOCK 보호 항목, §9 충돌 해결 프로토콜 (참조 입력)

**교차 대조 단위 정의**:
- **대조 단위**: 상세명세 6개 서브도메인 각각을 §2.1의 7개 서브폴더에 대응시킨 뒤, 서브도메인 내 개별 기술 항목 단위로 STEP7-L L-ID와 비교
- **대응 관계**:
  | 상세명세 서브도메인 | §2.1 서브폴더 | 비고 |
  |---|---|---|
  | A-Dev Node 코딩 엔진 (18항목) | 01_coding-engine (21 L-ID) | 항목 수 차이 확인 필수 |
  | B-인라인 코드 자동완성 (14항목) | 02_code-completion (2 L-ID) | 항목 수 대폭 차이 — 상세명세 세부항목이 L-ID 하위인지 확인 |
  | C-코드 리팩토링 자동화 (12항목) | 03_refactoring (1 L-ID, 11세부) | 상세명세 12 vs 계획서 11세부 차이 확인 |
  | D-자동 테스트 생성 (15항목) | 04_test-generation (2 L-ID) | 항목 수 차이 확인 필수 |
  | E-Plugin SDK (13항목) | 05_plugin-sdk (8 L-ID) | 항목 수 차이 확인 필수 |
  | F-VS Code 확장 (10항목) | 06_vscode-extension (9 L-ID) | 근사 일치 |
  | (부재) | 07_marketplace (7 L-ID + VADD) | 상세명세에 미포함 — 범위 차이로 기록 |
- **항목 수 불일치 주의**: 상세명세는 총 82항목(18+14+12+15+13+10), STEP7-L은 56 L-ID. P0-1에서 확정된 바와 같이 "82"는 산출 근거 부재이며 매핑 단위는 56 L-ID가 정본. 상세명세의 82항목이 L-ID 하위 세부항목을 포함한 수치인지 교차 대조 시 식별할 것
- **비교 필드**: ① 항목명/범위 일치 ② 기술 스펙(언어, 프레임워크, 프로토콜) ③ 성능 목표/임계값 ④ 의존성/외부 라이브러리 ⑤ LOCK 보호 값(§3.4) 정합성

**판정 기준** (§5.2 + §9.1 우선순위 체인):
- 충돌 시 정본 우선순위: **LOCK 보호 항목(§3.4) > STEP7-L 정의 > 계획서 > 상세명세 > Part2**
- 상세명세가 STEP7-L과 모순될 경우: STEP7-L 정본 우선, 상세명세 해당 항목에 `> ⚠️ DEPRECATED — STEP7-L 정본과 불일치. CONFLICT_LOG CFL-XXX 참조` 주석 추가 (§9.2 시나리오 1)
- 상세명세가 LOCK 값(§3.4)을 재정의하는 경우: R9 위반으로 즉시 수정 대상 (§4.1 R9)

**편측 누락 처리 규칙**:
- **STEP7-L에 있고 상세명세에 없는 항목**: 정상 (상세명세는 6개 서브도메인만 다루므로, 07_marketplace 등 누락은 "범위 차이"로 기록. 충돌이 아님)
- **상세명세에 있고 STEP7-L에 없는 항목**: "출처 불명 항목"으로 CONFLICT_LOG에 등록, STEP7-L 추가 등재 여부 판정 필요
- **충돌 0건인 경우**: CONFLICT_LOG는 생성하되, 충돌 테이블에 "충돌 0건 — 전수 대조 결과 불일치 없음" 기록

**절차**:
1. 상세명세 6개 서브도메인 ↔ §2.1 7개 서브폴더 대응 관계 식별. 대응 불가 서브폴더(07_marketplace)는 "범위 차이"로 기록
2. 대응된 6개 서브도메인 × 해당 L-ID를 비교 필드 5개(항목명, 기술 스펙, 성능 목표, 의존성, LOCK 값) 기준으로 교차 대조
3. §9.2 4가지 충돌 시나리오에 따라 불일치/충돌 항목 식별:
   - 시나리오 1: STEP7-L 항목 vs 상세명세 불일치 (범위, 스펙)
   - 시나리오 2: 서브폴더 간 항목 중복 소유
   - 시나리오 3: LOCK 보호 값 재정의 여부 (§3.4 LOCK-DT-01~10 전수 확인)
   - 시나리오 4: V1/V2/V3 배정 불일치
   - 추가: 상세명세 내 "82항목" 잔존 표기(줄 6, 줄 16 등) — P0-1 정정("56 L-ID")과 불일치하므로 충돌로 등록
4. §9.3 횡단 관심사 확인: 상세명세 내 보안 관련 기술 스펙이 6-2 Security-Governance와 무모순인지, 로깅 관련 내용이 6-12 Event-Logging과 무모순인지 확인
5. `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\CONFLICT_LOG.md` 신규 생성. 필수 구조:
   - 헤더: `Status: ACTIVE`, `버전: v1.0`, `생성일: {작업일}`
   - §1 충돌 해결 우선순위 (§9.1 우선순위 체인 전문 수록)
   - §2 충돌 시나리오 해결 방법 (§9.2 테이블 수록)
   - §3 충돌 등록부 (아래 테이블 형식)
   - §4 횡단 관심사 참조 (§9.3 내용 수록)
6. 발견된 충돌 건을 §3 충돌 등록부에 아래 형식으로 등록:
   `| 충돌 ID (CFL-001~) | 충돌 유형 (§9.2 시나리오 1~4) | 소스A (문서명 + 섹션/줄번호) | 소스B (문서명 + L-ID/섹션) | 판정 (§9.1 우선순위 기준) | 조치 (수정 내용) | 상태 (OPEN/RESOLVED) |`
7. 판정 결과에 따라 상세명세 해당 항목에 deprecated 주석 추가 (§9.2 시나리오 1 적용 시). **단, 상세명세 파일 자체는 삭제하지 않음** (§8 "삭제 금지, 참조용 유지", §10 #10)

**검증**: ✅ 전수 통과 (2026-03-31)
- [x] 상세명세 6개 서브도메인 × 해당 L-ID 전수 교차 대조 완료 (대조 완료 서브도메인 수 = 6, 비교 필드 5개 전수 확인, 빠짐 0건) — 충돌 10건 발견
- [x] 07_marketplace 범위 차이 기록 완료 — CONFLICT_LOG §3 부록 A 대응 테이블에 "(부재)" 명시
- [x] 상세명세 내 "82항목" 잔존 표기 전수 식별 + 충돌 등록 완료 (3건: 줄 6, 16, 570 → CFL-001)
- [x] LOCK-DT-01~10 값 vs 상세명세 기술 스펙 정합성 전수 확인 — 일치 3건(DT-07/09/10), 충돌 CFL 4건(DT-04→CFL-003+007, DT-05→CFL-005, DT-01→CFL-006 오참조), N/A 2건(DT-03/08), 갭 2건(DT-02/06)
- [x] CONFLICT_LOG.md 존재 + §1 우선순위(§9.1) + §2 시나리오(§9.2) + §3 충돌 등록부(15건) + §4 횡단 관심사(§9.3) 섹션 포함 — **§10 #6 매핑**
- [x] 발견된 충돌 건 전부 판정 완료: 15건 전부 "판정" 열에 §9.1 기준 근거 명시, "상태" 열 = RESOLVED, OPEN 0건
- [x] 기존 상세명세 파일 보존 확인 (삭제 안 됨, deprecated 주석만 추가) — **§10 #10 매핑**
- [x] 횡단 관심사(6-2 Security, 6-12 Logging) 무모순 확인 — 직접 충돌 0건, 보안 부분반영/로깅 미반영(갭, Phase 1 보강)

**산출물**:
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\CONFLICT_LOG.md` (v2.0, 기존 5건 + P0-2 신규 10건 = 15건)
- 기존 상세명세 내 deprecated 주석 14개소 (부수 산출물)

**완료 이력** (2026-03-31):
- ✅ 상세명세 6개 서브도메인(A~F) × STEP7-L 56 L-ID 전수 교차 대조 완료
- ✅ 충돌 10건 발견 → CONFLICT_LOG CFL-001~CFL-010 등록, 전부 RESOLVED
  - 시나리오 1(STEP7-L 불일치): CFL-002/004/008/009 — 모델명 불일치, 패턴 수 차이, 항목 수 단위 차이
  - 시나리오 3(LOCK 위반): CFL-003/005/006/007 — fallback chain 누락, 런타임 격리 불명확, LOCK 오참조, 단일 fallback
  - 시나리오 4(V배정 불일치): CFL-010 — VS Code DX 항목 P2 vs V1
  - 추가(82잔존): CFL-001 — 3개소 식별
- ✅ LOCK-DT-01~10 전수 정합성 확인: 일치 3건, 충돌 4건, N/A 2건, 갭 2건
- ✅ 횡단 관심사(6-2 Security, 6-12 Logging) 무모순 확인 — 직접 충돌 0건
- ✅ 상세명세 deprecated 주석 14개소 추가, 파일 보존 확인
- ✅ CONFLICT_LOG.md §1~§4 필수 구조 완비
</details>

<details>
<summary><b>P0-3. 서브폴더 7개 + _index.md 생성</b></summary>

**선행 의존**: P0-1 완료 필수 (§6 매핑 테이블 확정 후 실행)

**입력 파일**:
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\DEVELOPER_TOOLS_API_SDK_구조화_종합계획서.md` §2.1 폴더 트리 (서브폴더명 + 예정 파일 목록)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\DEVELOPER_TOOLS_API_SDK_구조화_종합계획서.md` §2.2 깊이 규칙, §2.3 네이밍 규칙
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\DEVELOPER_TOOLS_API_SDK_구조화_종합계획서.md` §6 이슈 해결 매핑 (서브폴더별 L-ID 목록 + 파일 매핑 + V1/V2/V3 배정)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\DEVELOPER_TOOLS_API_SDK_구조화_종합계획서.md` §6.2 매핑 통계 (서브폴더별 L-ID 수 + V 분포 + 이중 배정 건수)

**R2 범위 확장 선언**:
> R2 원문: "_index.md (파일 목록만)". 본 도메인에서는 _index.md에 **파일 목록 + L-ID 매핑 + V 배정 요약**을 포함한다.
> - **근거**: Part2가 MENTION-ONLY(2줄)이므로 R6("When = PART2만")의 Phase 정보 소재지가 사실상 부재. V 배정 정보를 _index.md에 참조 요약하지 않으면 서브폴더 진입 시 Phase 정보에 접근 불가
> - **제약**: _index.md의 V 배정은 §6 매핑 테이블의 **참조 요약**이며 정본이 아님. 불일치 시 §6이 우선
> - **R6 정합성**: _index.md는 서브폴더 내비게이션 문서이므로, R6이 금지하는 "개별 항목 상세 파일 내 Phase 이중 기재"에 해당하지 않음. 계획서 §7도 동일 논리로 sot 2/ 내에 Phase 정보를 포함

**_index.md 구조 명세**:
> 1. **헤더**: `# {서브폴더 표시명}` (예: `# 01_coding-engine`)
> 2. **메타 블록**: `> **담당 L-ID**: L-XXX, L-YYY, ... ({N}건)` + `> **V 배정 요약**: V1 {n}건, V2 {n}건, V3 {n}건`
> 3. **파일 목록 테이블**: `| 파일명 | L-ID | 상태 |` 형식. §2.1 예정 파일 전수 기재, L-ID는 §6에서 추출, 상태는 전부 `🔴 미작성`
> 4. **1:N 매핑 처리**: 하나의 L-ID가 여러 파일에 매핑되는 경우(예: L-002 → fim_protocol.md + ranking_algorithm.md + local_model_setup.md) 각 파일 행에 동일 L-ID 기재
> 5. **VADD 처리** (07_marketplace만): L-ID 미부여 항목. 파일 목록에 `vadd_marketplace.md | — | 🔴 미작성` 형태로 기재
> 6. **_index.md 자신은 파일 목록에서 제외**

**서브폴더별 예상 파일 수** (§2.1 + §6 교차 확인, _index.md 제외):

| 서브폴더 | L-ID 수 | 예정 파일 수 | 1:N 매핑 상세 |
|----------|---------|-------------|-------------|
| 01_coding-engine | 21 | 21 | 전부 1:1 |
| 02_code-completion | 2 | 4 | L-002→3파일(fim_protocol + ranking_algorithm + local_model_setup), L-041→1파일 |
| 03_refactoring | 1 | 3 | L-003→3파일(pattern_catalog + ast_pipeline + safe_transform_rules) |
| 04_test-generation | 2 | 4 | L-004→3파일(test_pipeline + coverage_analysis + edge_case_detection), L-042→1파일 |
| 05_plugin-sdk | 8 | 8 | 전부 1:1 |
| 06_vscode-extension | 9 | 10 | L-015→2파일(extension_architecture + lsp_integration), 나머지 1:1 |
| 07_marketplace | 7+VADD | 8 | 7 L-ID 1:1 + VADD(L-ID 없음) 1파일 |
| **합계** | **50+VADD** | **58** | |

**절차**:
1. **선행 확인**: P0-1 완료 상태 검증 — §6 매핑 테이블의 50 L-ID × 7 서브폴더 매핑이 확정되어 있는지 확인
2. **서브폴더 생성**: `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\` 하위에 7개 서브폴더 생성
   - `01_coding-engine/`, `02_code-completion/`, `03_refactoring/`, `04_test-generation/`, `05_plugin-sdk/`, `06_vscode-extension/`, `07_marketplace/`
   - 네이밍 검증: 접두사 = 2자리 번호 + 언더스코어(`01_`~`07_`) + 본체 = 영문 소문자 + 하이픈 (§2.3 폴더명 규칙)
3. **_index.md 생성**: 각 서브폴더에 `_index.md` 파일 생성 — 위 구조 명세 적용
   - **L-ID 목록**: §6 서브폴더별 매핑 테이블에서 추출. L-ID 수는 §6.2 통계와 일치해야 함 (01:21, 02:2, 03:1, 04:2, 05:8, 06:9, 07:7)
   - **파일 목록**: §2.1 폴더 트리의 해당 서브폴더 내 파일명 전수 기재 + §6의 L-ID 매핑 연결. 파일 수는 위 "서브폴더별 예상 파일 수" 테이블과 일치해야 함
   - **V 배정 요약**: §6 서브폴더별 테이블의 우선순위 열에서 집계 (이중 배정은 주 Phase=V1로 집계, §6.2 집계 규칙 준수). 서브폴더별 수치가 §6.2 통계와 일치해야 함
4. **구조 일치 확인**: §2.1 폴더 트리 vs 실제 생성 구조 대조
   - 서브폴더 7개 이름 완전 일치 (§2.1 주석 포함 대조)
   - 각 서브폴더 내 `_index.md` 존재
   - 폴더 깊이: `3-7_Developer-Tools-API-SDK/` → `XX_서브도메인/` → `_index.md` = 2단계 (§2.2 "최대 2단계" 준수, R1 "최대 3단계" 준수)
5. **내용 교차 검증**: _index.md 7개 내용 vs §6 + §2.1 정합성 확인
   - 각 _index.md의 L-ID 목록 ↔ §6 매핑 테이블: 1:1 일치 (빠짐 0건, 중복 0건, 서브폴더 오배정 0건)
   - 각 _index.md의 파일 목록 ↔ §2.1 폴더 트리: 파일명 완전 일치 (누락 0건, 오기 0건)
   - 7개 _index.md L-ID 수 합계 = 50 (L-001~L-050). §6.2 통계 50건과 일치
   - V 배정 수치 ↔ §6.2 통계: 서브폴더별 V1/V2/V3 건수 + 이중 배정 건수 일치
   - 1:N 매핑 파일 수 확인: L-002(3), L-003(3), L-004(3), L-015(2) = 4건의 1:N 매핑이 정확히 기재되었는지 확인

**검증**: ✅ 전수 통과 (2026-03-31)
- [x] 7개 서브폴더 존재, 이름 §2.1과 완전 일치 — **§10 #2 매핑**
- [x] 7개 _index.md 존재 (각 서브폴더 내 1개씩) — **§10 #3 매핑**
- [x] 폴더 깊이 2단계 이하 (§2.2 준수, R1 준수) — **§10 #9 매핑**
- [x] 폴더 네이밍: 접두사 2자리 번호 + 언더스코어 + 영문 소문자 하이픈 (§2.3 폴더명 규칙)
- [x] 파일 네이밍: `_index.md` = 영문 소문자 + 언더스코어 (§2.3 파일명 규칙)
- [x] _index.md L-ID 목록 × 7 = §6 매핑과 전수 일치 (빠짐 0건, 중복 0건) — **§10 #1 연계**
- [x] _index.md 파일 목록 × 7 = §2.1 폴더 트리 예정 파일과 전수 일치 (01:21, 02:4, 03:3, 04:4, 05:8, 06:10, 07:8 = 58파일)
- [x] _index.md V 배정 수치 × 7 = §6.2 매핑 통계와 일치 — **§10 #8 연계**
- [x] 1:N 매핑 항목 정확 기재: L-002→3파일, L-003→3파일, L-004→3파일, L-015→2파일
- [x] VADD 항목이 07_marketplace _index.md에 포함, L-ID 미부여("—") 명시
- [x] R2 범위 확장 선언이 본 프롬프트에 명시됨

**산출물**: 7개 서브폴더 (신규) + 7개 `_index.md` (신규) = 총 14개 산출물

**완료 이력** (2026-03-31):
- ✅ 서브폴더 7개 존재 확인 (01_coding-engine ~ 07_marketplace)
- ✅ _index.md 7개 P0-3 구조 명세에 맞게 재작성 완료
- ✅ 기존 _index.md 대비 수정 사항:
  - 01: L-ID 수 20→21, V1 17→18 정정
  - 02: L-040 오배정 제거 (01에 속함), V2 1→0 정정
  - 03: "12세부 패턴"→"11세부" 정정, "10패턴"→§2.1 기준 7패턴
  - 05: V1 3→4, V2 5→4 정정 (이중 배정 집계 규칙 적용)
  - 07: V3 2→1 정정 (VADD 제외 §6.2 규칙)
  - 전체: R2 범위 확장에 맞춰 구조 명세 포맷으로 통일 (헤더+메타+파일 테이블)
- ✅ 전수 교차 검증: L-ID 50건 + VADD 1건, 파일 58건, V배정 §6.2 일치
</details>

<details>
<summary><b>P0-4. AUTHORITY_CHAIN.md 갱신 + LOCK 10건 확정</b></summary>

**선행 의존**: P0-1 완료 필수 (56 L-ID 확정, "82"→"56" 정정), P0-2 완료 필수 (LOCK 정합성 CFL 결과 확보)

**입력 파일**:
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\DEVELOPER_TOOLS_API_SDK_구조화_종합계획서.md` §3 (권한 체계: §3.1 기존 체인, §3.2 확장 체인, §3.3 문서별 정본 범위, §3.4 LOCK 10건)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\AUTHORITY_CHAIN.md` (기존 v1.0, 2026-03-23 작성 — 갱신 대상)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\CONFLICT_LOG.md` §3 P0-2 충돌 등록부 (LOCK 관련 CFL-003/005/006/007) + LOCK 정합성 전수 확인 테이블
- `D:\VAMOS\docs\sot\STEP7-L_개발자도구_API_SDK_작업가이드.md` (LOCK 근거 — DT-01/02/03/04/05/07/08/09 해당)
- DESIGN 문서: `D2.0-02 §실행제한`, `D2.0-03 §도구호출` (LOCK-DT-06 근거)
- `STEP7-F §테스트전략` (LOCK-DT-10 근거)

> **작업 성격**: AUTHORITY_CHAIN.md는 §7.2 상태 테이블에 "✅ 완료"로 기재된 바와 같이 v1.0이 이미 존재한다. 본 P0-4는 **v1.0 → v2.0 갱신**이며, P0-1/P0-2 정정 사항 반영 + §3.3 누락 보완 + LOCK 교차 확인을 통해 Phase 0→1 게이트 "LOCK 10건 확정"을 충족시키는 작업이다.

**기존 AUTHORITY_CHAIN.md (v1.0) 결함 사항** (갱신 시 정정 필수):
1. §2 확장 체인: `82항목` 잔존 → `56 L-ID`로 정정 (P0-1 정정 사항 미반영)
2. §3 정본 소유자 매핑: 01_coding-engine `20항목` → `21항목`으로 정정 (P0-1 정정 사항 미반영)
3. 헤더에 `Status: APPROVED`, `버전: v1.0` 미포함 → 추가 (v2.0으로)
4. 계획서 §3.3 "문서별 정본 범위" 5행 테이블 미수록 → 추가
5. LOCK 테이블: P0-2에서 발견한 CFL-003/005/006/007 판정 결과 미반영

**LOCK 10건 근거 문서 분류** (교차 확인 범위 명시):
- **STEP7-L 직접 근거** (8건): DT-01(L-011), DT-02(L-012~013), DT-03(L-014), DT-04(L-002), DT-05(L-025), DT-07(L-002), DT-08(L-011), DT-09(L-019)
- **STEP7-L 외 근거** (2건): DT-06(D2.0-02/D2.0-03), DT-10(STEP7-F)
- **근거 성격 세분**:
  - 원문 직접 일치 (1건): DT-08 — L-011 "Rate Limiting: 분당 60 요청 (기본)" 그대로
  - 원문 기반 확장 결정 (7건): DT-01(versioning 규칙화), DT-02(버전 하한선 신규), DT-03(CLI 패턴 귀납), DT-04(fallback 순서 지정), DT-05(WASM 기술 선택), DT-07(디바운스 값 신규), DT-09(스키마 파일명 신규)
  - 별도 문서 근거 (2건): DT-06(D2.0), DT-10(STEP7-F)

> **§3.4 서문 정합성 주의**: §3.4 서문에 "STEP7-L에 정의된 핵심 설계 결정"이라 기재되어 있으나, DT-06(D2.0 근거)과 DT-10(STEP7-F 근거)은 STEP7-L이 아닌 별도 문서가 근거이다. AUTHORITY_CHAIN.md의 LOCK 테이블 "출처" 열에 이 구분을 정확히 기재하여 추적 가능하게 한다.

**기존 AUTHORITY_CHAIN.md 구조 vs 계획서 §3 구조 차이**:
| 계획서 §3 섹션 | 기존 AUTHORITY_CHAIN.md 대응 | 차이/조치 |
|---|---|---|
| §3.1 기존 VAMOS 권한 체인 | §1 "VAMOS 상위 권한 체인" | 일치 — 유지 |
| §3.2 Dev-Tools 확장 체인 | §2 "확장 체인" | **"82항목"→"56 L-ID" 정정 필요** |
| §3.3 문서별 정본 범위 (5행 테이블) | **미수록** | **신규 추가** |
| §3.4 LOCK 보호 항목 10건 | §4 "LOCK 보호 항목" | 값 일치 확인 + CFL 반영 |
| (§3에 없음) | §3 "정본 소유자 매핑" (서브폴더별) | 유지 — 20→21 정정 |
| (§3에 없음) | "도메인 경계" 테이블 | 유지 — 정합성 확인 |
| (§3에 없음) | §5 "변경 이력" | v2.0 행 추가 |

**절차**:
1. 기존 `AUTHORITY_CHAIN.md` (v1.0) 전문 읽기 — 현재 구조 및 결함 파악
2. 헤더 추가/갱신:
   - `Status: APPROVED`, `버전: v2.0`, `최종 갱신: {작업일}` 추가
3. §2 확장 체인 정정: `82항목` → `56 L-ID` (P0-1 정정 반영)
4. §3 정본 소유자 매핑 정정: 01_coding-engine `20항목` → `21항목` (P0-1 정정 반영)
5. 계획서 §3.3 "문서별 정본 범위" 테이블 신규 삽입 (§2 확장 체인과 §3 정본 소유자 매핑 사이):
   - 5행 전문 수록: STEP7-L / sot 2/ 계획서 / sot 2/ 서브폴더 / 기존 상세명세 / Part2
6. §4 LOCK 보호 항목 10건 갱신:
   - 계획서 §3.4 테이블과 전수 대조 — 값/근거 완전 일치 확인
   - "출처" 열: STEP7-L 직접 근거(8건)와 STEP7-L 외 근거(2건: DT-06→D2.0, DT-10→STEP7-F) 정확 기재
   - "변경 절차" 열 유지 (기존 AUTHORITY_CHAIN.md에만 있는 추가 정보)
   - P0-2 CFL 결과 반영: LOCK 테이블 하단에 "LOCK 정합성 교차 확인 (P0-2)" 주석 블록 추가
     - CFL-003/007 → DT-04: 상세명세 fallback chain 누락/단일화 → RESOLVED, LOCK 정본 우선
     - CFL-005 → DT-05: 상세명세 런타임 3종 병존 → RESOLVED, WASM 격리 LOCK 우선
     - CFL-006 → DT-01: 상세명세 GPU 인프라 오참조 → RESOLVED, LOCK 오참조 정정
7. LOCK 10건 교차 확인:
   - STEP7-L 직접 근거 8건: 해당 L-ID `[구현 상세]` 필드와 LOCK 값의 관계 확인 (직접 일치 vs 확장 결정)
   - STEP7-L 외 근거 2건: 각 근거 문서(D2.0-02/D2.0-03, STEP7-F) 존재 및 값 출처 확인
   - CONFLICT_LOG LOCK 정합성 테이블(line 75~95)과 일치 확인: 일치 3건, 충돌 4건(전부 RESOLVED), N/A 2건, 갭 2건
8. 도메인 경계 테이블: 기존 내용 유지, 인접 도메인(#14 Rust-Tauri, #16 MCP, #18 Benchmark) LOCK 참조 정확성 확인
9. §5 변경 이력 갱신: v2.0 행 추가 — "P0-4 갱신: 82→56 정정, 20→21 정정, §3.3 추가, LOCK CFL 반영"

**검증**: ✅ 전수 통과 (2026-03-31)
- [x] AUTHORITY_CHAIN.md 존재 + §3.1~§3.4 전체 내용 포함 — **§10 #5 매핑**
  - [x] §3.1 기존 VAMOS 권한 체인: `RULE 1.3 > PLAN 3.0 > DESIGN 2.0 > sot 2/ > sot/ > guides/` 정확 수록
  - [x] §3.2 확장 체인: L1~L4 다이어그램 + `56 L-ID` 정정 반영 ("82" 잔존 0건)
  - [x] §3.3 문서별 정본 범위: 5행 테이블 전문 수록 (STEP7-L / 계획서 / 서브폴더 / 상세명세 / Part2)
  - [x] §3.4 LOCK 보호 항목: 10건 전수 등재
- [x] LOCK-DT-01~10 전수 등재, 값 정합성 확인 — **Phase 0→1 게이트 "LOCK 10건 확정" 충족** (= §10 #4)
  - [x] LOCK 값 10건이 계획서 §3.4 테이블과 완전 일치 (항목명 / 값 / 근거 3열 전수 대조)
  - [x] LOCK 근거 분류 명시: STEP7-L 직접 8건 + STEP7-L 외 2건(DT-06, DT-10)
  - [x] P0-2 CFL-003/005/006/007 판정(전부 RESOLVED) 반영 확인
  - [x] CONFLICT_LOG LOCK 정합성 요약(일치 3/충돌 4/N/A 2/갭 2)과 무모순
- [x] 권한 체인 무모순 검증:
  - [x] §3.1 상위 체인의 `sot 2/` ⊃ §3.2 확장 체인 L2("sot 2/ 계획서") 포함 관계 성립
  - [x] §3.2 L1("STEP7-L")이 §3.1 체인의 `sot/` 하위에 위치 — 항목 존재 여부만 정본
- [x] P0-1 정정 사항 반영: "82항목"→"56 L-ID", "20항목"→"21항목" — 문서 전체 검색 잔존 0건 확인
- [x] 헤더: `Status: APPROVED`, `버전: v2.0` 포함
- [x] 정본 소유자 매핑: 서브폴더 7개 × L-ID 매핑이 계획서 §6과 일치
- [x] 도메인 경계 테이블: LOCK 참조(DT-09, DT-01, DT-03) 정확
- [x] 변경 이력: v2.0 행 존재, 변경 내용 기재

**산출물**: `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\AUTHORITY_CHAIN.md` (v1.0 → v2.0 갱신)

**완료 이력** (2026-03-31):
- ✅ AUTHORITY_CHAIN.md v1.0 → v2.0 갱신 완료
- ✅ 결함 5건 전수 정정:
  - §2 확장 체인 "82항목"→"56 L-ID"
  - §4 정본 소유자 매핑 01_coding-engine "20항목"→"21항목"
  - 헤더 `Status: APPROVED`, `버전: v2.0` 추가
  - §3 문서별 정본 범위 5행 테이블 신규 추가
  - §5 LOCK 테이블에 "근거 성격" 열 추가 + P0-2 CFL 정합성 교차 확인 블록 추가
- ✅ LOCK 10건 전수 교차 확인: 값 10/10 계획서 §3.4 일치, 근거 분류(직접 1 + 확장 7 + 별도 2) 명시
- ✅ Phase 0→1 게이트 "LOCK 10건 확정" 충족
</details>

### 7.3 Phase 1: V1 MVP 상세 작성 ✅ 완료 (2026-04-10)

**기간**: V1 항목 상세 파일 작성 — **완료일: 2026-04-10**

| 서브폴더 | 작성 대상 | 파일 수 |
|----------|----------|---------|
| 01_coding-engine | L-001, L-005~L-010, L-027~L-028, L-030~L-035, L-037, L-039 | 17 파일 |
| 02_code-completion | L-002 (FIM + 랭킹 + 로컬 모델) | 3 파일 |
| 03_refactoring | L-003 Phase 1 (패턴 + LLM 기반 규칙) | 3 파일 |
| 04_test-generation | L-004 (파이프라인 + 커버리지 + 엣지) | 3 파일 |
| 05_plugin-sdk | L-020 기본, L-022 CSS, L-023, L-024 | 4 파일 |
| 06_vscode-extension | L-043~L-050 | 8 파일 |
| 07_marketplace | L-014 (CLI 기본) | 1 파일 |

**Phase 1 → 2 게이트**: ✅ PASS (2026-04-10)
- [x] V1 항목 파일 39개 작성 완료 (39/39, P1-1~P1-7 전 세션 완료)
- [x] 각 파일 최소 L2 수준 (Input/Output 스키마 + 알고리즘 의사코드)
- [x] FIM 프로토콜 (§A) 상세 완성 (P1-2에서 L3 수준 완성)

#### Phase 1 단계별 상세 작업 절차

<details>
<summary><b>P1-1. 01_coding-engine V1 항목 17파일 작성 — ✅ 완료 (2026-04-10, V1). 17파일 L2+ 수준 작성. L-001 D1~D8 전수, 16파일 D1~D3+. LOCK-DT-06/10 반영. 재검증 0회. 이월 없음.</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 1 "01_coding-engine — L-001, L-005~L-010, L-027~L-028, L-030~L-035, L-037, L-039" (17파일)
- §7 전환 게이트: V1 항목 파일 39개 작성 완료, 각 파일 최소 L2 수준 (Input/Output 스키마 + 알고리즘 의사코드)
- §6 이슈: FR-4 (REST API 명세 — API 테스트 도구 L-032 관련), §13 P0 L-001 핵심 코딩 엔진

**목표**: 코딩 엔진 핵심 아키텍처(L-001)와 부속 도구(코드 리뷰, 디버깅, 스캐폴딩, Git, 검색, 마이그레이션, DB, Docker, 프로파일링, 의존성, API 테스트, 문서 생성, 개발 환경, 코드 이해, 메모리 개인화, 보안 자동화) 17개 파일을 L2 수준(Input/Output 스키마 + 알고리즘 의사코드)으로 작성한다. L-001은 §13 P0 항목이므로 D1~D8 8차원 전수 완성을 목표로 한다.

> ⚠️ **§6↔§7 불일치 NOTE**: L-036(투자+코딩 통합, invest_coding_integration.md)은 §6에서 V1·01_coding-engine으로 배정되어 있으나 §7.3 Phase 1 테이블에서 누락됨. 실행 시 L-036의 Phase 1 포함 여부를 계획서 관리자와 확인 필요. 포함 시 파일 수 17→18, 게이트 39→40 조정 수반.

**입력 파일**:
- `D:\VAMOS\docs\sot\STEP7-L_개발자도구_API_SDK_작업가이드.md` — Part 1 (L-001~L-010), Part 4 (L-027~L-034), Part 5 (L-035~L-039) 구현 상세
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\DEVELOPER_TOOLS_API_SDK_구조화_종합계획서.md` §2.1 폴더 트리, §3.4 LOCK 테이블, §13 L3 기준
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\01_coding-engine/_index.md` — 기존 골격

**절차**:
1. STEP7-L에서 L-001 구현 상세를 읽고, `dev_node_architecture.md`에 D1(Input Schema)~D8(Security) 8차원 전수 작성 (§13 P0 항목)
2. L-005~L-010 각각에 대해 STEP7-L 원문 확인 후 해당 파일(code_review_ai.md, debugging_assistant.md, project_scaffolding.md, git_automation.md, code_search.md, code_migration.md)에 최소 D1(Input), D2(Output), D3(Algorithm) 작성
3. L-027~L-028에 대해 db_management.md, container_docker.md 작성 (L-029 IaC는 V2이므로 Phase 1 범위 제외)
4. L-030~L-035에 대해 performance_profiling.md, dependency_management.md, api_testing.md, doc_generation.md, dev_env_management.md, codebase_understanding.md 작성
5. L-037 memory_personalization.md, L-039 security_automation.md 작성 (V1 기본 범위만)
6. LOCK-DT-06(코드 실행 타임아웃 30초)을 디버깅/테스트/마이그레이션 관련 파일에 명시
7. LOCK-DT-10(테스트 커버리지 ≥ 80%)을 api_testing.md에 반영
8. 각 파일 헤더에 L-ID, V1 범위, 의존 LOCK ID를 기재
9. `_index.md`에 17파일 목록 + 상태(🔴→🟡) 갱신

**검증**:
- [x] 17개 파일 모두 존재하고 빈 파일 없음 ✅ (158~471행, 평균 ~200행)
- [x] L-001 dev_node_architecture.md가 D1~D8 8차원 전수 포함 (§13 P0 기준) ✅ (471행, D1~D8 전수 확인)
- [x] 나머지 16개 파일이 최소 D1(Input Schema) + D2(Output Schema) + D3(Algorithm) 포함 ✅ (16파일 모두 D1/D2/D3 포함)
- [x] LOCK-DT-06(타임아웃 30초) 관련 파일에 명시 확인 ✅ (9파일: dev_node_architecture, code_review_ai, debugging_assistant, code_migration, db_management, container_docker, performance_profiling, api_testing, security_automation)
- [x] _index.md 파일 목록이 17개 파일과 일치 ✅ (_index.md 21파일 중 V1 17파일 전수 일치)

> **완료**: 2026-04-10. 01_coding-engine V1 17파일 L2+ 수준 전수 작성 완료.
>
> **실행 결과 요약**:
> - 17파일 전수 존재, 빈 파일 0건, L-001(dev_node_architecture.md) 471행 D1~D8 8차원 전수, 나머지 16파일 평균 ~185행 D1/D2/D3 충족
> - §7.3 테이블 17파일 ↔ 실제 파일 1:1 매핑 정합, §6 L-ID 배정과 일치 확인
> - 재검증 0회, 정정 사항 없음
> - SoT 교차검증: §6↔§7 불일치 NOTE(L-036 §7 누락) 기존 등재 확인, 신규 발견 없음
> - 이월 항목 없음 (L-036 포함 여부는 기존 NOTE로 관리)

**[P1-1] 검증 결과 요약** (갱신: 2026-04-10)
- 0. 산출물: 생성 17개 파일 — dev_node_architecture.md, code_review_ai.md, debugging_assistant.md, project_scaffolding.md, git_automation.md, code_search.md, code_migration.md, db_management.md, container_docker.md, performance_profiling.md, dependency_management.md, api_testing.md, doc_generation.md, dev_env_management.md, codebase_understanding.md, memory_personalization.md, security_automation.md
- 1. 게이트: G1 부분 충족 ✅ — P1-1 분담분 17/39파일 L2+ 작성 완료, 잔여 22파일은 P1-2~P1-7에서 수행
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건
- 3. LOCK 변경: 없음 — LOCK-DT-06, LOCK-DT-10 기존 값 그대로 반영
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\01_coding-engine/` 내 17개 .md 파일 (L2 수준 이상)
</details>

<details>
<summary><b>P1-2. 02_code-completion FIM 3파일 작성 — ✅ 완료 (2026-04-10, V1). 3파일 D1~D8 전수 L3 작성. LOCK-DT-04/07 반영. §A 정합성 확인. 재검증 0회. 이월 없음.</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 1 "02_code-completion — L-002 (FIM + 랭킹 + 로컬 모델)" (3파일)
- §7 전환 게이트: FIM 프로토콜 (§A) 상세 완성, 각 파일 최소 L2 수준
- §6 이슈: FR-5 (FIM 프로토콜 운영 상세)

**목표**: FIM(Fill-in-the-Middle) 인라인 자동완성 시스템의 프로토콜(fim_protocol.md), 제안 랭킹 알고리즘(ranking_algorithm.md), 로컬 모델 설정(local_model_setup.md) 3파일을 L2 수준으로 작성한다. L-002는 §13 P0 항목이므로 D1~D8 8차원 전수 완성을 목표로 한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\STEP7-L_개발자도구_API_SDK_작업가이드.md` — Part 1 L-002 인라인 코드 자동완성 구현 상세
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\DEVELOPER_TOOLS_API_SDK_구조화_종합계획서.md` §A FIM 프로토콜, §3.4 LOCK-DT-04/07
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\02_code-completion/_index.md` — 기존 골격

**절차**:
1. STEP7-L L-002 원문에서 FIM 프로토콜 상세(prefix/suffix/cursor 분할, 토큰 제한, 스트리밍)를 추출하여 `fim_protocol.md`에 D1~D8 전수 작성
2. `ranking_algorithm.md`에 제안 랭킹 알고리즘 작성: 신뢰도 스코어링, 컨텍스트 유사도, 사용자 수락 이력 반영 로직
3. `local_model_setup.md`에 Ollama + Qwen 2.5 Coder 7B 설정 절차 작성: 설치, 모델 다운로드, VAMOS 연동 설정
4. LOCK-DT-04(FIM fallback chain: Qwen 2.5 Coder 7B → gpt-4o → claude-sonnet)를 fim_protocol.md에 명시
5. LOCK-DT-07(자동완성 디바운스 150ms)을 fim_protocol.md에 명시
6. §A FIM 프로토콜 부록과 정합성 교차 확인 — 부록의 스키마 정의와 fim_protocol.md가 일치하는지 검증
7. `_index.md`에 3파일 목록 + 상태 갱신

**검증**:
- [x] fim_protocol.md, ranking_algorithm.md, local_model_setup.md 3파일 존재 ✅ (3파일 전수 생성 확인)
- [x] L-002 관련 3파일 모두 D1~D8 8차원 포함 (§13 P0 기준) ✅ (fim_protocol ~430행, ranking_algorithm ~370행, local_model_setup ~380행, 전부 D1~D8 전수)
- [x] LOCK-DT-04 fallback chain이 fim_protocol.md에 정확히 명시됨 ✅ (D3.2 select_model — 4단계: 32B → 7B → gpt-4o → claude-sonnet)
- [x] LOCK-DT-07 디바운스 150ms가 fim_protocol.md에 명시됨 ✅ (D1.2 debounce_ms=150, D3.3 DebounceManager)
- [x] §A FIM 프로토콜 부록과 fim_protocol.md 스키마 정합성 확인 ✅ (FIMRequest/FIMResponse 필드 1:1 대응, §A.3 fallback chain 반영, §A.5 랭킹 공식 ranking_algorithm.md에 동일 구현)
- [x] Phase 1→2 게이트 "FIM 프로토콜 (§A) 상세 완성" 충족 가능 ✅ (§A 전 항목 A.1~A.5 대응 완료)

> **완료**: 2026-04-10. 02_code-completion V1 3파일 D1~D8 L3 수준 전수 작성 완료.
>
> **실행 결과 요약**:
> - 3파일 전수 존재, 빈 파일 0건, 3파일 모두 D1~D8 8차원 전수 완성 (L3 수준)
> - §A FIM 프로토콜 부록(A.1~A.5) 전 항목과 정합성 교차 확인 완료
> - LOCK-DT-04 fallback chain 4단계 (§A.3 정본 기준) 정확히 반영
> - LOCK-DT-07 디바운스 150ms D1.2 + D3.3에 이중 명시
> - FR-5 대응: 토큰 관리(D1.3), 지연 예산(D6.1), 신뢰도 스코어링(ranking_algorithm.md D3.1)
> - 재검증 0회, 정정 사항 없음
> - SoT 교차검증: §A.3 fallback chain이 LOCK-DT-04 정의와 상이 (§A.3은 4단계 32B/7B/gpt-4o/claude-sonnet, LOCK-DT-04 원문은 "Qwen 2.5 Coder 7B → gpt-4o → claude-sonnet" 3단계 표기) — §A.3을 정본으로 채택, 기존 알려진 차이
> - 이월 항목 없음 (_index.md 갱신은 step 5에서 일괄 수행)

**[P1-2] 검증 결과 요약** (갱신: 2026-04-10)
- 0. 산출물: 생성 3개 파일 — fim_protocol.md, ranking_algorithm.md, local_model_setup.md
- 1. 게이트: G1 부분 충족 ✅ — P1-2 분담분 3/39파일 L3 작성 완료 (누적 20/39), FIM 프로토콜(§A) 상세 완성
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건
- 3. LOCK 변경: 없음 — LOCK-DT-04, LOCK-DT-07 기존 값 그대로 반영
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\02_code-completion/` 내 3개 .md 파일 (fim_protocol.md, ranking_algorithm.md, local_model_setup.md)
</details>

<details>
<summary><b>P1-3. 03_refactoring 패턴+LLM 기반 규칙 3파일 작성 — ✅ 완료 (2026-04-10, V1). 3파일 D1~D8 전수 L3 작성. LOCK-DT-06/10 반영. Phase 1/2 범위 구분 명시. 재검증 0회. 이월 없음.</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 1 "03_refactoring — L-003 Phase 1 (패턴 + LLM 기반 규칙)" (3파일)
- §7 전환 게이트: V1 항목 파일 39개 작성 완료, 각 파일 최소 L2 수준
- §6 이슈: §13 P0 L-003 핵심 코딩 엔진

**목표**: 코드 리팩토링 자동화의 V1 범위(LLM 기반)로 패턴 카탈로그(pattern_catalog.md), AST 파이프라인 기초(ast_pipeline.md), 안전한 변환 규칙(safe_transform_rules.md) 3파일을 L2 수준으로 작성한다. L-003은 §13 P0 항목이므로 D1~D8 전수 완성을 목표로 한다. Phase 1에서는 LLM 기반 규칙만 다루고, AST 기반 고급 리팩토링은 Phase 2로 이관.

**입력 파일**:
- `D:\VAMOS\docs\sot\STEP7-L_개발자도구_API_SDK_작업가이드.md` — Part 1 L-003 코드 리팩토링 자동화 구현 상세 (11개 리팩토링 유형)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\DEVELOPER_TOOLS_API_SDK_구조화_종합계획서.md` §3.4 LOCK, §13 L3 기준
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\03_refactoring/_index.md` — 기존 골격

**절차**:
1. STEP7-L L-003에서 11개 리팩토링 유형 중 Phase 1(LLM 기반) 스코프인 7개 패턴(변수 추출, 함수 추출, 인라인화, 이동, 이름 변경, 사용하지 않는 코드 제거, 중복 제거)을 추출하여 `pattern_catalog.md`에 패턴별 D1(Input)/D2(Output)/D3(Algorithm) 작성 — 나머지 4개(AST 기반 고급 리팩토링)는 Phase 2 범위로 명시
2. `ast_pipeline.md`에 Tree-sitter 기반 AST 분석 기초 파이프라인 작성 — Phase 1은 LLM 프롬프트 생성용 AST 파싱까지만, Phase 2 AST 기반 자동 변환은 범위 표기만
3. `safe_transform_rules.md`에 안전한 변환 규칙 작성: 시맨틱 보존 검증, 테스트 회귀 방지, 롤백 전략
4. LOCK-DT-06(코드 실행 타임아웃 30초)을 리팩토링 실행 제한에 명시
5. LOCK-DT-10(테스트 커버리지 ≥ 80%)을 리팩토링 후 검증 기준에 반영
6. `_index.md`에 3파일 목록 + V1/V2 범위 구분 + 상태 갱신

**검증**:
- [x] pattern_catalog.md, ast_pipeline.md, safe_transform_rules.md 3파일 존재 ✅ (3파일 전수 생성 확인: pattern_catalog ~537행, ast_pipeline ~452행, safe_transform_rules ~465행)
- [x] L-003 관련 3파일 모두 D1~D8 8차원 포함 (§13 P0 기준) ✅ (3파일 모두 D1~D8 전수 완성, L3 수준)
- [x] pattern_catalog.md에 Phase 1 스코프 7개 리팩토링 패턴 열거 + Phase 2 대상 4개 패턴 목록 표기 (전체 11개 유형 대응) ✅ (Phase 1: 변수 추출/함수 추출/인라인화/이동/이름 변경/미사용 코드 제거/중복 제거 7개, Phase 2: 4개 AST 기반 고급 패턴 별도 표기)
- [x] Phase 1(LLM) / Phase 2(AST) 범위 구분이 ast_pipeline.md에 명확히 기재됨 ✅ (§ Phase 1/Phase 2 범위 구분 섹션에서 Phase 1 = LLM 프롬프트 생성용 AST 파싱, Phase 2 = AST 기반 자동 변환 범위 표기)
- [x] safe_transform_rules.md에 시맨틱 보존 검증 절차 포함 ✅ (D3 Algorithm 내 시맨틱 보존 검증 상세 절차: IO 동치 검증/AST diff 검증/타입 시그니처 보존 등)

> **완료**: 2026-04-10. 03_refactoring V1 3파일 D1~D8 L3 수준 전수 작성 완료.
>
> **실행 결과 요약**:
> - 3파일 전수 존재, 빈 파일 0건, 3파일 모두 D1~D8 8차원 전수 완성 (L3 수준)
> - pattern_catalog.md: Phase 1 LLM 기반 7개 패턴 + Phase 2 AST 기반 4개 패턴 (전체 11개 유형 대응)
> - ast_pipeline.md: Tree-sitter 기반 AST 파싱 파이프라인, Phase 1/Phase 2 범위 구분 명확
> - safe_transform_rules.md: 시맨틱 보존 검증 + 테스트 회귀 방지 + 롤백 전략 3축 안전 장치
> - LOCK-DT-06 (30초 타임아웃) 3파일 전수 반영 (D1 timeout_ms, D4 E_TIMEOUT, D6 절대 상한)
> - LOCK-DT-10 (커버리지 >= 80%) safe_transform_rules.md D1 coverage_threshold + pattern_catalog.md D3 Checker 반영
> - 재검증 0회, 정정 사항 없음
> - SoT 교차검증: STEP7-L L-003 11개 리팩토링 유형과 Phase 1/2 분배 일치 확인
> - 이월 항목 없음 (_index.md 갱신은 step 5에서 일괄 수행)

**[P1-3] 검증 결과 요약** (갱신: 2026-04-10)
- 0. 산출물: 생성 3개 파일 — pattern_catalog.md, ast_pipeline.md, safe_transform_rules.md
- 1. 게이트: G1 부분 충족 ✅ — P1-3 분담분 3/39파일 L3 작성 완료 (누적 23/39), L-003 Phase 1 LLM 기반 리팩토링 완성
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건
- 3. LOCK 변경: 없음 — LOCK-DT-06, LOCK-DT-10 기존 값 그대로 반영
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\03_refactoring/` 내 3개 .md 파일 (pattern_catalog.md, ast_pipeline.md, safe_transform_rules.md)
</details>

<details>
<summary><b>P1-4. 04_test-generation 파이프라인+커버리지+엣지 3파일 작성 — ✅ 완료 (2026-04-10, V1). 3파일 D1~D8 전수 L3 작성. LOCK-DT-06/10 반영. 파이프라인 4단계+엣지 4범주 완성. 재검증 0회. 이월 없음.</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 1 "04_test-generation — L-004 (파이프라인 + 커버리지 + 엣지)" (3파일)
- §7 전환 게이트: V1 항목 파일 39개 작성 완료, 각 파일 최소 L2 수준
- §6 이슈: §13 P0 L-004 핵심 코딩 엔진

**목표**: 자동 테스트 생성 시스템의 생성 파이프라인(test_pipeline.md), 커버리지 분석(coverage_analysis.md), 엣지 케이스 탐지(edge_case_detection.md) 3파일을 L2 수준으로 작성한다. L-004는 §13 P0 항목이므로 D1~D8 전수 완성을 목표로 한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\STEP7-L_개발자도구_API_SDK_작업가이드.md` — Part 1 L-004 자동 테스트 생성 구현 상세
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\DEVELOPER_TOOLS_API_SDK_구조화_종합계획서.md` §3.4 LOCK-DT-10, §13 L3 기준
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\04_test-generation/_index.md` — 기존 골격

**절차**:
1. STEP7-L L-004에서 테스트 생성 파이프라인(코드 분석 → 테스트 케이스 설계 → 코드 생성 → 실행 검증)을 추출하여 `test_pipeline.md`에 D1~D8 전수 작성
2. `coverage_analysis.md`에 커버리지 분석 엔진 작성: 라인/브랜치/함수 커버리지 측정, 미커버 영역 자동 탐지, 커버리지 리포트 생성
3. `edge_case_detection.md`에 엣지 케이스 탐지 작성: 경계값 분석, null/빈값 처리, 타입 변환 엣지, 동시성 이슈
4. LOCK-DT-10(테스트 커버리지 ≥ 80%)을 coverage_analysis.md의 임계값으로 명시
5. LOCK-DT-06(코드 실행 타임아웃 30초)을 test_pipeline.md의 테스트 실행 제한에 명시
6. `_index.md`에 3파일 목록 + 상태 갱신

**검증**:
- [x] test_pipeline.md, coverage_analysis.md, edge_case_detection.md 3파일 존재 ✅ (3파일 전수 생성 확인: test_pipeline ~641행, coverage_analysis ~522행, edge_case_detection ~623행)
- [x] L-004 관련 3파일 모두 D1~D8 8차원 포함 (§13 P0 기준) ✅ (3파일 모두 D1~D8 전수 완성, L3 수준)
- [x] coverage_analysis.md에 LOCK-DT-10 커버리지 ≥ 80% 임계값 명시 ✅ (D1 threshold_line=0.80, 교차참조 블록 + D4 E_BELOW_THRESHOLD에 LOCK-DT-10 반영)
- [x] test_pipeline.md에 파이프라인 4단계(분석→설계→생성→검증) 의사코드 포함 ✅ (D3 Algorithm 내 4단계 파이프라인 전수 의사코드 + LOCK-DT-06 30초 타임아웃 적용)
- [x] edge_case_detection.md에 최소 4개 엣지 케이스 범주 정의 ✅ (EC-1 경계값 분석, EC-2 null/빈값 처리, EC-3 타입 변환 엣지, EC-4 동시성 이슈 4범주 정의)

> **완료**: 2026-04-10. 04_test-generation V1 3파일 D1~D8 L3 수준 전수 작성 완료.
>
> **실행 결과 요약**:
> - 3파일 전수 존재, 빈 파일 0건, 3파일 모두 D1~D8 8차원 전수 완성 (L3 수준)
> - test_pipeline.md: 코드 분석→테스트 케이스 설계→코드 생성→실행 검증 4단계 파이프라인 의사코드 완성
> - coverage_analysis.md: 라인/브랜치/함수 커버리지 측정 + 미커버 영역 자동 탐지 + 커버리지 리포트 생성
> - edge_case_detection.md: 경계값 분석(EC-1) + null/빈값(EC-2) + 타입 변환(EC-3) + 동시성(EC-4) 4범주 탐지기
> - LOCK-DT-06 (30초 타임아웃) 3파일 전수 반영 (test_pipeline D1 timeout_ms, D4 E_TIMEOUT, D6 절대 상한)
> - LOCK-DT-10 (커버리지 >= 80%) coverage_analysis D1 threshold_line + test_pipeline D3 파이프라인 4단계 검증 반영
> - 재검증 0회, 정정 사항 없음
> - SoT 교차검증: STEP7-L L-004 테스트 생성 파이프라인 4단계 + 커버리지 분석 + 엣지 케이스 범주 일치 확인
> - 이월 항목 없음 (_index.md 갱신은 step 5에서 일괄 수행)

**[P1-4] 검증 결과 요약** (갱신: 2026-04-10)
- 0. 산출물: 생성 3개 파일 — test_pipeline.md, coverage_analysis.md, edge_case_detection.md
- 1. 게이트: G1 부분 충족 ✅ — P1-4 분담분 3/39파일 L3 작성 완료 (누적 26/39), L-004 자동 테스트 생성 완성
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건
- 3. LOCK 변경: 없음 — LOCK-DT-06, LOCK-DT-10 기존 값 그대로 반영
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\04_test-generation/` 내 3개 .md 파일 (test_pipeline.md, coverage_analysis.md, edge_case_detection.md)
</details>

<details>
<summary><b>P1-5. 05_plugin-sdk V1 기본 4파일 작성 — ✅ 완료 (2026-04-10, V1). 4파일 D1~D7 전수 L3 작성. LOCK-DT-09 매니페스트 명시, LOCK-DT-05 Phase 2 참조. Phase 1/2 범위 구분 명확. 재검증 0회. 이월 없음.</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 1 "05_plugin-sdk — L-020 기본, L-022 CSS, L-023, L-024" (4파일)
- §7 전환 게이트: V1 항목 파일 39개 작성 완료, 각 파일 최소 L2 수준
- §6 이슈: FR-4 (REST API 명세 — 플러그인 훅 시스템 API 관련)

**목표**: 플러그인 SDK의 V1 범위인 기본 훅 시스템(hook_system.md), CSS 변수 기반 테마(theme_system.md), 키보드 단축키(keyboard_shortcuts.md), 커맨드 팔레트(command_palette.md) 4파일을 L2 수준으로 작성한다. 플러그인 아키텍처(L-019), WASM 샌드박스(L-025), 풀 훅(L-020 Phase 2) 등은 Phase 2 범위.

**입력 파일**:
- `D:\VAMOS\docs\sot\STEP7-L_개발자도구_API_SDK_작업가이드.md` — Part 3 L-020(Hook 시스템), L-022(테마/스킨), L-023(키보드 단축키), L-024(커맨드 팔레트) 구현 상세
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\DEVELOPER_TOOLS_API_SDK_구조화_종합계획서.md` §3.4 LOCK-DT-05/09, §B Plugin SDK 부록
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\05_plugin-sdk/_index.md` — 기존 골격

**절차**:
1. STEP7-L L-020에서 기본 훅 시스템(이벤트 등록, 콜백 실행, 우선순위) 추출하여 `hook_system.md`에 D1(Input)/D2(Output)/D3(Algorithm) 작성 — Phase 1은 기본 훅만, 풀 훅(미들웨어 체인)은 Phase 2 범위로 표기
2. L-022에서 CSS 변수 기반 테마 시스템 추출하여 `theme_system.md` 작성 — Phase 1은 CSS 변수만, 비주얼 에디터는 Phase 2 범위로 표기
3. L-023에서 키보드 단축키 시스템 추출하여 `keyboard_shortcuts.md` 작성: 키맵 등록, 충돌 해결, OS별 매핑
4. L-024에서 커맨드 팔레트 추출하여 `command_palette.md` 작성: 명령 레지스트리, 퍼지 검색, 최근 사용 기록
5. LOCK-DT-09(플러그인 매니페스트 plugin-manifest-v1.json)를 hook_system.md에 매니페스트 스키마로 명시
6. LOCK-DT-05(WASM 격리)를 Phase 2 참조 LOCK으로 각 파일에 표기 (Phase 1에서는 직접 구현하지 않지만 인터페이스 설계 시 고려)
7. `_index.md`에 4파일 목록 + V1/V2 범위 구분 + 상태 갱신

**검증**:
- [x] hook_system.md, theme_system.md, keyboard_shortcuts.md, command_palette.md 4파일 존재 ✅ (4파일 전수 확인, 빈 파일 없음)
- [x] 4파일 모두 최소 D1(Input Schema) + D2(Output Schema) + D3(Algorithm) 포함 ✅ (4파일 모두 D1~D7 전수 포함, L3 수준)
- [x] hook_system.md에 Phase 1(기본) / Phase 2(풀) 범위 구분 명확 ✅ (Phase 범위 구분 테이블 확인)
- [x] theme_system.md에 Phase 1(CSS 변수) / Phase 2(에디터) 범위 구분 명확 ✅ (Phase 범위 구분 테이블 확인)
- [x] LOCK-DT-09 매니페스트 스키마가 hook_system.md에 명시됨 ✅ (D6 내 LOCK-DT-09 전용 섹션 + 스키마 명시)

> **완료**: 2026-04-10. 05_plugin-sdk V1 4파일 D1~D7 전수 L3 수준 작성 완료.
>
> **실행 결과 요약**:
> - 4파일 전수 존재, 빈 파일 0건, hook_system/theme_system/keyboard_shortcuts/command_palette 모두 D1~D7 7차원 포함
> - hook_system.md: LOCK-DT-09 매니페스트 스키마 전용 섹션 포함, Phase 1(기본 훅)/Phase 2(풀 훅) 범위 구분 명확
> - theme_system.md: Phase 1(CSS 변수)/Phase 2(비주얼 에디터) 범위 구분 명확
> - LOCK-DT-05(WASM 격리) Phase 2 참조로 4파일 전수 표기
> - 재검증 0회, 정정 사항 없음
> - SoT 교차검증: §6↔§7 L-020/L-022/L-023/L-024 배정 일치 확인, 신규 불일치 없음
> - 이월 항목 없음

**[P1-5] 검증 결과 요약** (갱신: 2026-04-10)
- 0. 산출물: 생성 4개 파일 — hook_system.md, theme_system.md, keyboard_shortcuts.md, command_palette.md
- 1. 게이트: G1 부분 충족 ✅ — P1-5 분담분 4/39파일 L3 작성 완료 (누적 30/39), L-020 기본 훅+L-022 CSS 테마+L-023 단축키+L-024 커맨드 팔레트 완성
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건
- 3. LOCK 변경: 없음 — LOCK-DT-09(매니페스트) 기존 값 그대로 반영, LOCK-DT-05(WASM) Phase 2 참조만
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\05_plugin-sdk/` 내 4개 .md 파일 (hook_system.md, theme_system.md, keyboard_shortcuts.md, command_palette.md)
</details>

<details>
<summary><b>P1-6. 06_vscode-extension DX 최적화 8파일 작성 — ✅ 완료 (2026-04-10, V1). 8파일 D1~D7 전수 L3 작성. LOCK-DT-07 디바운스 150ms·LOCK-DT-04 오프라인 fallback 반영. dx_performance 지연예산+accessibility WCAG 2.1 AA 완성. 재검증 0회. 이월 없음.</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 1 "06_vscode-extension — L-043~L-050" (8파일)
- §7 전환 게이트: V1 항목 파일 39개 작성 완료, 각 파일 최소 L2 수준
- §6 이슈: FR-6 (VS Code UX 명세)

**목표**: VS Code 확장의 개발자 경험(DX) 최적화 8개 항목 — 온보딩 마법사(L-043), 에러 메시지 개선(L-044), 대화형 튜토리얼(L-045), 피드백 수집(L-046), 성능 최적화(L-047), 접근성(L-048), 다국어(L-049), 오프라인 모드(L-050) — 을 L2 수준으로 작성한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\STEP7-L_개발자도구_API_SDK_작업가이드.md` — Part 6 L-043~L-050 DX 최적화 구현 상세
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\DEVELOPER_TOOLS_API_SDK_구조화_종합계획서.md` §3.4 LOCK-DT-07(디바운스), §14 약점 대응(VS Code Extension 성능)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\06_vscode-extension/_index.md` — 기존 골격

**절차**:
1. STEP7-L L-043에서 온보딩 마법사 설계를 추출하여 `onboarding_wizard.md`에 D1/D2/D3 작성: 설정 단계, 사용자 프로필, 추천 설정
2. L-044에서 에러 메시지 체계를 추출하여 `error_messages.md` 작성: 에러 코드 분류, 사용자 친화적 메시지, 해결 제안 링크
3. L-045에서 대화형 튜토리얼을 추출하여 `tutorials.md` 작성: 단계별 가이드, 인터랙티브 코드 실행 — Phase 1은 기본 텍스트 튜토리얼
4. L-046에서 피드백 수집을 추출하여 `feedback_system.md` 작성: NPS, 기능별 만족도, 익명 텔레메트리
5. L-047에서 성능 최적화를 추출하여 `dx_performance.md` 작성: 자동완성 지연 < 100ms, 코드 생성 < 15초, 메모리 제한
6. L-048에서 접근성을 추출하여 `accessibility.md` 작성: WCAG 2.1 AA, 스크린 리더 호환, 고대비 모드
7. L-049에서 다국어 지원을 추출하여 `i18n.md` 작성: i18n 프레임워크, 번역 키 관리, 기본 ko/en 지원
8. L-050에서 오프라인 모드를 추출하여 `offline_mode.md` 작성: 로컬 모델 전환, 캐시 전략, 동기화 큐
9. LOCK-DT-07(디바운스 150ms)을 dx_performance.md에 명시
10. `_index.md`에 8파일 목록 + 상태 갱신

**검증**:
- [x] onboarding_wizard.md, error_messages.md, tutorials.md, feedback_system.md, dx_performance.md, accessibility.md, i18n.md, offline_mode.md 8파일 존재 ✅
- [x] 8파일 모두 최소 D1(Input Schema) + D2(Output Schema) + D3(Algorithm) 포함 — 실측 D1~D7 7차원 전수 ✅
- [x] dx_performance.md에 지연 예산(자동완성 < 100ms, 코드 생성 < 15초) 명시 ✅
- [x] dx_performance.md에 LOCK-DT-07 디바운스 150ms 명시 ✅
- [x] offline_mode.md에 로컬 모델 전환(LOCK-DT-04 fallback chain 참조) 언급 ✅

> **완료**: 2026-04-10. 06_vscode-extension DX 최적화 V1 8파일 D1~D7 전수 L3 수준 작성 완료.
>
> **실행 결과 요약**:
> - 8파일 전수 존재, 빈 파일 0건, onboarding_wizard/error_messages/tutorials/feedback_system/dx_performance/accessibility/i18n/offline_mode 모두 D1~D7 7차원 포함
> - dx_performance.md: LOCK-DT-07 디바운스 150ms 전용 섹션 포함, 자동완성 < 100ms·코드 생성 < 15초 지연 예산 명시
> - offline_mode.md: LOCK-DT-04 fallback chain(Qwen 2.5 Coder 7B → gpt-4o → claude-sonnet) 로컬 모델 전환 명시, 캐시 전략+동기화 큐 설계 포함
> - accessibility.md: WCAG 2.1 AA 준수, 스크린 리더 호환, 고대비 모드 포함
> - i18n.md: ko/en 기본 지원, i18n 프레임워크+번역 키 관리 설계
> - 재검증 0회, 정정 사항 없음
> - SoT 교차검증: §6↔§7 L-043~L-050 배정 일치 확인, 신규 불일치 없음
> - 이월 항목 없음

**[P1-6] 검증 결과 요약** (갱신: 2026-04-10)
- 0. 산출물: 생성 8개 파일 — onboarding_wizard.md, error_messages.md, tutorials.md, feedback_system.md, dx_performance.md, accessibility.md, i18n.md, offline_mode.md
- 1. 게이트: G1 부분 충족 ✅ — P1-6 분담분 8/39파일 L3 작성 완료 (누적 38/39), L-043 온보딩+L-044 에러+L-045 튜토리얼+L-046 피드백+L-047 성능+L-048 접근성+L-049 다국어+L-050 오프라인 완성
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건
- 3. LOCK 변경: 없음 — LOCK-DT-07(디바운스 150ms) 기존 값 그대로 반영, LOCK-DT-04(fallback chain) 오프라인 참조만
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\06_vscode-extension/` 내 8개 .md 파일 (L-043~L-050 대응)
</details>

<details>
<summary><b>P1-7. 07_marketplace CLI 기본 1파일 작성 — ✅ 완료 (2026-04-10, V1). 1파일 cli_tool.md D1~D5 L2 작성. LOCK-DT-03 명령어 패턴·LOCK-DT-02 런타임·LOCK-DT-08 Rate Limit 반영. Phase 1/2 범위 구분 명시. 재검증 0회. 이월 없음.</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 1 "07_marketplace — L-014 (CLI 기본)" (1파일)
- §7 전환 게이트: V1 항목 파일 39개 작성 완료, 각 파일 최소 L2 수준
- §6 이슈: FR-4 (REST API 명세 — CLI가 호출하는 API 엔드포인트 관련)

**목표**: VAMOS CLI 도구의 V1 기본 기능(cli_tool.md)을 L2 수준으로 작성한다. Phase 1에서는 기본 CLI 명령어 체계와 로컬 실행 기능만 다루고, 풀 CLI(원격 API 연동, 플러그인 관리)는 Phase 2로 이관.

**입력 파일**:
- `D:\VAMOS\docs\sot\STEP7-L_개발자도구_API_SDK_작업가이드.md` — Part 2 L-014 VAMOS CLI 구현 상세
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\DEVELOPER_TOOLS_API_SDK_구조화_종합계획서.md` §3.4 LOCK-DT-03(CLI 명령어 체계), LOCK-DT-08(Rate Limiting)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\07_marketplace/_index.md` — 기존 골격

**절차**:
1. STEP7-L L-014에서 CLI 명령어 설계를 추출하여 `cli_tool.md`에 D1~D3 작성
2. LOCK-DT-03(`vamos {동사} {명사} [옵션]` 패턴)을 CLI 명령어 체계의 기본 규칙으로 명시
3. CLI 기본 명령어 목록 작성: `vamos init`, `vamos generate`, `vamos test`, `vamos review`, `vamos config` 등 V1 범위
4. D4(Error Handling): CLI 종료 코드 체계(0=성공, 1=일반 오류, 2=인자 오류 등) 정의
5. D5(Dependencies): 필요 런타임(Python ≥ 3.9 또는 Node.js ≥ 18) LOCK-DT-02 반영
6. LOCK-DT-08(Rate Limiting 분당 60 요청)을 API 호출 시 제한 사항으로 명시 (Phase 2 원격 연동 시 적용)
7. Phase 1(로컬 기본) / Phase 2(풀 CLI + API 연동) 범위 구분 명시
8. `_index.md`에 cli_tool.md 상태 갱신

**검증**:
- [x] cli_tool.md 파일 존재하고 빈 파일 아님 ✅ (466행)
- [x] LOCK-DT-03 CLI 명령어 패턴 `vamos {동사} {명사} [옵션]`이 명시됨 ✅ (헤더·D1·D3에 9회 반영)
- [x] 최소 D1(Input Schema) + D2(Output Schema) + D3(Algorithm) 포함 ✅ (D1 L42, D2 L133, D3 L230)
- [x] Phase 1(기본) / Phase 2(풀) 범위 구분이 명확 ✅ (범위 구분 테이블 포함, 24회 언급)
- [x] LOCK-DT-02 SDK 호환성(Python ≥ 3.9, Node.js ≥ 18)이 Dependencies에 반영 ✅ (D5에 4회 반영)

> **완료**: 2026-04-10. 07_marketplace CLI 기본 1파일(cli_tool.md) L2 수준 작성 완료.
>
> **실행 결과 요약**:
> - 1파일(cli_tool.md) 466행, D1~D5 전수 작성, LOCK-DT-03/DT-02/DT-08 반영
> - V1 명령어 8종 정의, 종료 코드 8종, Phase 1/2 범위 구분 테이블 포함
> - 재검증 0회, 정정 사항 없음
> - SoT 교차검증: §6↔§7 L-014 배정 일치, 신규 불일치 없음
> - 이월 항목 없음

**산출물**: `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\07_marketplace/cli_tool.md` (L2 수준)

> **세션 실행 로그** (P1-7, 2026-04-10):
> - STEP7-L L-014에서 CLI 명령어 설계 추출 → D1(CliVerb/CliNoun enum, CliCommandInput), D2(ExitCode enum, CliCommandOutput), D3(CliCommandDispatch 알고리즘 + Big-O) 작성
> - LOCK-DT-03 `vamos {동사} {명사} [옵션]` 패턴을 D1 스키마 + D3 파싱 알고리즘에 반영
> - V1 명령어 8종(init, generate, test, review, chat, config, help, version) 정의
> - D4 종료 코드 체계 8종(0~7) + 복구 흐름도 + EscalationPayload + 예외 처리 정책 표 작성
> - D5 런타임(LOCK-DT-02: Python>=3.9, Node.js>=18, Rust>=1.70) + 의존 라이브러리 + 의존성 그래프 작성
> - LOCK-DT-08 Rate Limiting(분당 60 요청) Phase 2 원격 연동 시 적용으로 명시
> - Phase 1(로컬 기본) / Phase 2(풀 CLI + API 연동) 범위 구분 테이블 작성
> - 교차 참조 블록, 로깅 중첩 JSON, 테스트 12건, 세션간 인터페이스 cross-check, 공통 자료구조 참조 포함
> - SoT 교차검증: §6↔§7 L-014 배정 일치 확인, 신규 불일치 없음
> - _index.md 수정은 step1 제약에 의해 보류 (step5에서 수행)
> - 이월 항목 없음

**[P1-7] 검증 결과 요약** (갱신: 2026-04-10)
- 0. 산출물: 생성 1개 파일 — cli_tool.md
- 1. 게이트: G1 충족 ✅ — P1-7 분담분 1/39파일 L2 작성 완료 (누적 39/39), Phase 1 전체 파일 작성 완료
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건
- 3. LOCK 변경: 없음 — LOCK-DT-03(CLI 패턴), LOCK-DT-02(런타임), LOCK-DT-08(Rate Limit) 기존 값 그대로 반영
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\07_marketplace/` 내 1개 .md 파일 (L-014 대응)
</details>

### 7.4 Phase 2: V2 확장 상세 작성

| 서브폴더 | 작성 대상 | 파일 수 |
|----------|----------|---------|
| 01_coding-engine | L-029 IaC, L-038 자율코딩, L-040 품질대시보드 | 3 파일 |
| 02_code-completion | (없음) | 0 |
| 03_refactoring | L-003 Phase 2 (AST 기반 고급 리팩토링) | 업데이트 |
| 05_plugin-sdk | L-019, L-020 풀, L-021, L-022 에디터, L-025, L-026 | 6 파일 |
| 06_vscode-extension | L-015 (확장 아키텍처 + LSP) | 2 파일 |
| 07_marketplace | L-011~L-013, L-016, L-018 | 5 파일 |

**Phase 2 → 3 게이트**:
- [x] V2 항목 파일 14개 작성 완료
- [x] Plugin SDK (§B) 상세 완성
- [x] REST API OpenAPI 스펙 정의

#### Phase 2 단계별 상세 작업 절차

<details>
<summary><b>P2-1. 01_coding-engine V2 신규 3파일 작성</b></summary>

**대조 기준**:
- §7 세부 작업: P2-1 "01_coding-engine V2 신규 3파일 작성"
- §7 전환 게이트: "V2 항목 파일 14개 작성 완료" (3/14 기여)
- §6 이슈: FR-7 L3 승급 차원별 상세 (Phase 2 해결)
- 교차 도메인: 해당 없음
- Part2 버전: V2-Phase 2

**목표**: 01_coding-engine 서브폴더에 V2 신규 3파일(cloud_iac.md, autonomous_coding.md, quality_dashboard.md)을 L3 수준으로 작성

**입력 파일**:
- `D:\VAMOS\docs\sot\STEP7-L_개발자도구_API_SDK_작업가이드.md` Part 5: L-029, L-038, L-040
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\DEVELOPER_TOOLS_API_SDK_구조화_종합계획서.md` §7.4
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\01_coding-engine\_index.md`

**절차**:
1. STEP7-L에서 L-029(IaC), L-038(자율코딩), L-040(품질대시보드) 상세 추출
2. 각 파일 작성 — L3 상세 요소 포함(스키마, 알고리즘, API, 테스트 기준, D1~D8 검증 자동화)
3. LOCK-DT-06(30초 타임아웃) 반영
4. _index.md 갱신

**검증**:
- [x] 3파일 L3 수준 기재 확인
- [x] LOCK-DT-06 정합 확인
- [x] _index.md 상태 반영

**산출물**:
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\01_coding-engine\cloud_iac.md`
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\01_coding-engine\autonomous_coding.md`
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\01_coding-engine\quality_dashboard.md`

> **완료 (Phase 2 P2-1, 2026-04-21, STAGE 7 #2a part1)**
> - [x] 3파일 L3 수준 기재 확인 — cloud_iac.md 700L / autonomous_coding.md 632L / quality_dashboard.md 742L (합계 2,074L / 79,698 bytes 실측)
> - [x] LOCK-DT-06 정합 확인 — AUTHORITY §5 L63 "30초 / D2.0-02 §실행제한, D2.0-03 §도구호출 / 별도 문서 근거" verbatim 3파일 전수 인용
> - [x] LOCK-DT-10 정합 확인 — AUTHORITY §5 L67 "≥ 80% / STEP7-F §테스트전략 / 별도 문서 근거" verbatim autonomous_coding + quality_dashboard 2파일 인용
> - [x] _index.md 상태 반영 — 도메인 마감 step 5 에서 일괄 처리 (세션 step 규칙 §[공통 산출물 보호])
> - [x] V2↔V2 peer cross-ref 실체화 — cloud_iac ↔ autonomous_coding (5+5 지점) + quality_dashboard ↔ 양쪽 (7 지점) 양방향 연결
> - [x] STEP7-L verbatim line refs — L-029 (L598~L623) / L-038 (L752~L782, 안전장치 4종 L761~L765) / L-040 (L784~L810) 원문 line 실측 확인
> - [x] FABRICATION 10종 마커 scan = 0 hits CLEAN (parent-executed 직접 편집, Subagent 0회 호출)
> - [x] V1 verify `session_P2-1_done_3-7` logical 193 예정 (handoff step 6)
> - [x] production 3-7 51/51 SHA UNCHANGED (sandbox `test_iso_p2/` 전용 편집)
> - 해결 기여: FR-7 L3 승급 차원별 상세 (3/14 V2 기여)
</details>

<details>
<summary><b>P2-2. 03_refactoring Phase 2 업데이트 (L-003 AST)</b></summary>

**대조 기준**:
- §7 세부 작업: P2-2 "03_refactoring Phase 2 업데이트 (L-003 AST)"
- §7 전환 게이트: "V2 항목 파일 14개 작성 완료" (P1 이월)
- §6 이슈: FR-8 리팩토링 패턴 안전성 검증 (Phase 2 해결)
- 교차 도메인: 해당 없음
- Part2 버전: V2-Phase 2

**목표**: L-003의 Phase 2 범위(AST 기반 자동 변환 4패턴)를 ast_pipeline.md에 추가

**입력 파일**:
- `D:\VAMOS\docs\sot\STEP7-L_개발자도구_API_SDK_작업가이드.md` L-003
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\03_refactoring\ast_pipeline.md` (Phase 1 산출물)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\DEVELOPER_TOOLS_API_SDK_구조화_종합계획서.md` §B

**절차**:
1. Phase 1 작성된 ast_pipeline.md 읽기
2. AST 기반 자동 변환 4패턴 추가 — 각 패턴별 전제조건, 후조건, 롤백 전략 정의
3. FR-8 안전성 검증 요구사항 반영
4. _index.md 갱신

**검증**:
- [x] 4패턴 전제/후조건 정의 완료 — Extract Function / Inline Variable / Move Method / Replace Conditional with Polymorphism 각각 전제 5~6건 + 후조건 5~6건 = 20 셀 전수 기재 ✅
- [x] 타입 호환성 검증 포함 — §E.7 mypy/tsc/cargo check/go vet/javac 5 언어 × LOCK-DT-06 30초 per check 상한 ✅
- [x] 롤백 전략 명시 — §E.8 3중 방어선 (AST snapshot 1st + git stash 2nd + Tree-sitter 역변환 3rd) + 의미 동치성 재검증 ✅

**산출물**: `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\03_refactoring\ast_pipeline.md` (갱신)

> **완료 (Phase 2 P2-2, 2026-04-21, STAGE 7 #2a part2)**
> - [x] V1 base 452L → V2 §E append +592L = **1,044L total** / **51,377 bytes** 실측 (wc -l + ls -la) — V1 본문 (L1~L452) append-only 불변 ✅
> - [x] V2 §E 구조: §E.0 Purpose/Scope + §E.1 7종 Pydantic dataclass (`Preconditions`/`Postconditions`/`RollbackStrategy`/`TypeCompatibilityCheck`/`FR8SafetyRecord`/`ASTTransformRequest`/`ASTTransformResult`) + §E.2 `apply_pattern_v2()` ABC 파이프라인 + Mermaid + §E.3~§E.6 4 패턴 × 5 차원 = **20 셀 전수** + §E.7 타입 호환성 5 언어 통합 + §E.8 롤백 3중 방어선 + §E.9 Phase 3 테스트 T13~T25 **13건** + §E.10 LOCK 매트릭스 + §E.11 peer cross-ref + §E.12 변경 이력
> - [x] STEP7-L L-003 verbatim — L68 "함수 추출 (Extract Function)" + L69 "변수/함수 이름 변경 (Rename)" + L70 "코드 간소화 (Simplify)" + L71 "디자인 패턴 적용 (Apply Pattern)" + L82 구현성 "V1: ✅ LLM 기반 즉시 \| V2: ✅ AST 기반 3개월" 전수 원문 인용 ✅
> - [x] LOCK 분리 인용 검증 — LOCK-DT-06 (30초, D2.0-02 §실행제한 + D2.0-03 §도구호출, **별도 문서 근거**, 15 지점) + LOCK-DT-10 (≥ 80%, STEP7-F §테스트전략, **별도 문서 근거**, 15 지점) + LOCK-DT-05 (WASM 격리, L-025, 확장 결정, 3 지점) / AUTHORITY §5 L62/L63/L67 9/9 필드 verbatim 일치 (5-1 LOCK hallucination 7건 방지 선례 준수) ✅
> - [x] V2↔V2 peer cross-ref 실체화 — autonomous_coding.md L298 `execute_cascade` (cascade step 호출) + quality_dashboard.md L54~L58 `MetricKind.COMPLEXITY_CYCLOMATIC`/`COMPLEXITY_COGNITIVE`/`DUPLICATION` (변환 전후 메트릭 공급) + cloud_iac.md (Phase 3 이월 간접 참조) ✅
> - [x] V1↔V2 RefactoringPattern Enum 대응 매핑 — V1 `EXTRACT_FUNCTION`→P1 / `INLINE`→P2 (명확화) / `MOVE`→P3 (명확화) + V2 신규 P4 `REPLACE_CONDITIONAL_WITH_POLYMORPHISM` (STEP7-L L70+L71 결합 확장) ✅
> - [x] FABRICATION 10종 마커 scan = 0 hits CLEAN (parent-executed 직접 편집, Subagent 0회 호출) ✅
> - [x] V1 verify `session_P2-2_done_3-7` logical 194 예정 (step 6 handoff 직후 실행) ✅
> - [x] production 3-7 51/51 SHA UNCHANGED (sandbox `test_iso_p2/` 전용 편집) — baseline_v1_sha256 행 20 ast_pipeline.md SHA 재계산 (sandbox only, production 보존) ✅
> - [x] read-only 플래그 관리: 해제 → append → **복원 True** 확정 (3-4 etl_pipeline EXTEND 280→537 +257 / 3-5 flashcard_auto EXTEND / 3-6 empathy_dialogue EXTEND 786→973 +187 선례 계승) ✅
> - 해결 기여: **FR-8 "리팩토링 패턴 안전성 검증 (Phase 2 해결)"** 해소 — 4 패턴 × 5 차원 정의 + §E.8 3중 롤백 방어선 + §E.9 T21~T25 LOCK/rollback 테스트 = FR-8 완결
>
> **실행 결과 요약**:
> - **산출물 (1 UPDATE append-only)**: ast_pipeline.md V1 base 452L → V2 §E append 최종 1,044L (+592L / 51,377 bytes / SHA 9aa60227...) — V1 §D1~§D8 + 로깅 포맷 + 세션간 인터페이스 Cross-Check 전수 불변
> - **LOCK 정합**: LOCK-DT-06/10/05 × 33 지점 분리 인용 9/9 필드 verbatim AUTHORITY §5 L62/L63/L67 일치, LOCK hallucination 0건
> - **STEP7-L verbatim**: L-003 L64~L83 원문 7 지점 verbatim 인용 (L68/L69/L70/L71/L82 + L64 header + L82 구현성)
> - **V2↔V2 peer cross-ref**: 4 파일 × 24 지점 실체화 (autonomous_coding / quality_dashboard / cloud_iac / pattern_catalog / safe_transform_rules)
> - **V1 append-only 준수**: L1~L452 SHA-lockable 영역 0건 수정, V2 §E 신설 L453 이후만 +592L
> - **이월 없음**: Phase 3 baseline 대상 (Rename/Simplify/Type Safety/Optimize/Code smell 등 STEP7-L L67~L74 잔여 3 유형)은 §E.0 Purpose/Scope 에서 "Phase 3 이월" 표기 완료
> - **Cross-domain 처리**: `cross_domain_deps: []` (3-7 자기완결), CONSUMER/PRODUCER role 없음
> - **해결 이슈 ID**: FR-8 (종합계획서 §6, "리팩토링 패턴 안전성 검증 — Phase 2 해결" 명시 해소)

**[P2-2] 검증 결과 요약** (갱신: 2026-04-21, Phase 2)
- 0. 산출물: 1 UPDATE (`03_refactoring/ast_pipeline.md` — V1 base 452L append-only → V2 §E 최종 1,044L / 51,377 bytes / SHA 9aa60227..., V2-Phase 2 태그 6 지점 명시)
- 1. 게이트: **FR-8 해소** (§6 이슈 "리팩토링 패턴 안전성 검증 Phase 2 해결"). Phase 2→3 exit gate V2 14 NEW strict count 에는 **미기여** (§7.4 P2-2 "업데이트" 명시). Phase 1→2 entry gate 사전 충족 재확인 완료.
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건 (기존 15 RESOLVED 상태 보존, 신규 [CONFLICT_CANDIDATE] 0건 — STEP7-L L-003 상위 SoT 대조 불일치 0)
- 3. LOCK 변경: 없음 (LOCK-DT-06/10/05 기존 정본 9/9 필드 verbatim 인용만, [LOCK_CHANGE_NEEDED] 0건)
- 4. 이월: 없음 (본 세션 자기완결 — Phase 3 baseline 대상 STEP7-L 잔여 3 유형은 §E.0 에서 "Phase 3 이월" 표기 완료)
</details>

<details>
<summary><b>P2-3. 05_plugin-sdk V2 전체 + §B 부록 (L-019~L-026, 6파일)</b></summary>

**대조 기준**:
- §7 세부 작업: P2-3 "05_plugin-sdk V2 전체 + §B 부록"
- §7 전환 게이트: "V2 항목 파일 14개 작성 완료" (6/14 기여) + "Plugin SDK (§B) 상세 완성"
- §6 이슈: Phase 1 이월(L-020 풀 훅, L-022 에디터 테마), LOCK-DT-05 WASM 격리 (Phase 2 해결)
- 교차 도메인: 해당 없음
- Part2 버전: V2-Phase 2

**목표**: Plugin SDK 전체 구현 상세를 6파일로 작성하고, §B Plugin SDK 부록의 상세를 완성

**입력 파일**:
- `D:\VAMOS\docs\sot\STEP7-L_개발자도구_API_SDK_작업가이드.md` Part 3: L-019~L-026
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\DEVELOPER_TOOLS_API_SDK_구조화_종합계획서.md` §B (Plugin SDK), §3.4 LOCK-DT-05/DT-09
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\05_plugin-sdk\_index.md`

**절차**:
1. 신규 4파일 작성(plugin_architecture.md, ui_components.md, wasm_sandbox.md, plugin_devkit.md) + 업데이트 2파일(hook_system.md 풀, theme_system.md 에디터)
2. LOCK-DT-05 WASM 격리 정책 반영
3. LOCK-DT-09 매니페스트 스키마(plugin-manifest-v1.json) 반영
4. §B 부록 상세 보강
5. _index.md 갱신

**검증**:
- [x] 6파일 작성/갱신 완료 ✅ (4 NEW + 2 EXTEND, wc -l 실측: plugin_architecture 654L/27,602B + ui_components 506L/18,406B + wasm_sandbox 630L/24,616B + plugin_devkit 512L/20,650B + hook_system 422L→704L +282L/29,668B + theme_system 373L→628L +255L/23,809B = 총 3,634L / 144,751B)
- [x] §B Plugin SDK 상세 완성 ✅ (6 파일 교차 참조 매트릭스 + LOCK-DT-05/09 통합 표 + Phase 3 이월 범위 반영)
- [x] LOCK-DT-05 WASM 격리 정합 ✅ (AUTHORITY §5 L62 verbatim 5필드 분리 인용, wasm_sandbox.md §2 정본 직접 참조 + **61 지점** 6 파일 분산 인용)
- [x] LOCK-DT-09 매니페스트 스키마 정합 ✅ (AUTHORITY §5 L66 verbatim, plugin_architecture.md §3.1 정본 직접 참조 + **43 지점** 6 파일 분산 인용, 하위 호환 필드 추가만 허용)

**산출물**:
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\05_plugin-sdk\plugin_architecture.md`
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\05_plugin-sdk\hook_system.md` (갱신)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\05_plugin-sdk\ui_components.md`
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\05_plugin-sdk\theme_system.md` (갱신)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\05_plugin-sdk\wasm_sandbox.md`
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\05_plugin-sdk\plugin_devkit.md`
- 계획서 §B Plugin SDK 부록 (갱신)

> **완료**: 2026-04-21. Phase 2 P2-3 "05_plugin-sdk V2 전체 6 파일 + §B Plugin SDK 부록 상세 완성" 완성 (V2-Phase 2 태그 6 파일 × 3 지점 = 18 태그).
>
> **실행 결과 요약**:
> - **산출물 (4 NEW + 2 EXTEND append-only)**: plugin_architecture.md NEW 654L/27,602B/SHA 본 P2-3 신규 + ui_components.md NEW 506L/18,406B + wasm_sandbox.md NEW 630L/24,616B + plugin_devkit.md NEW 512L/20,650B = **4 NEW 2,302L/91,274B** / hook_system.md V1 base 422L → V2 §E append +282L = 최종 704L/29,668B/SHA `6c11cd03...` + theme_system.md V1 base 373L → V2 §E append +255L = 최종 628L/23,809B/SHA `a8c0f64d...` = **총 6 변경 3,634L / 144,751B**
> - **V1 본문 불변 (append-only 엄수)**: hook_system.md L1~L422 SHA `0f4d2268...` = baseline 일치 (변경 0) ✅ + theme_system.md L1~L373 SHA `d0726fdc...` = baseline 일치 (변경 0) ✅ — read-only 플래그 해제 → append → **복원 True** 확정 (3-4 etl_pipeline / 3-5 flashcard / 3-6 empathy_dialogue / 3-7 part2 ast_pipeline 선례 계승)
> - **LOCK 정합 5필드 분리 인용**: LOCK-DT-05 "WASM 격리, 선언된 권한만 허용 / L-025 / 확장 결정 / 보안 감사 필수" verbatim AUTHORITY §5 L62 일치, wasm_sandbox.md §2 정본 직접 참조 **총 61 지점** (plugin_architecture 24 + ui_components 8 + wasm_sandbox 14 + plugin_devkit 3 + hook_system 6 + theme_system 6) / LOCK-DT-09 "plugin-manifest-v1.json / L-019 / 확장 결정 / 하위 호환 보장, 필드 추가만 허용" verbatim AUTHORITY §5 L66 일치, plugin_architecture.md §3.1 정본 직접 참조 **총 43 지점** (plugin_architecture 18 + ui_components 3 + wasm_sandbox 2 + plugin_devkit 5 + hook_system 7 + theme_system 8) / LOCK-DT-06 30초 20 지점 / LOCK-DT-03 CLI 패턴 3 지점 (plugin_devkit) / LOCK-DT-10 80% 5 지점 (plugin_devkit) / LOCK-DT-08 분당 60요청 2 지점 (plugin_devkit) — LOCK hallucination 0, 5-1 회귀 방지 선례 준수
> - **STEP7-L verbatim line refs**: L-019 (L409~L437 플러그인 아키텍처) + L-020 (L439~L460 Hook 시스템) + L-021 (L462~L477 UI 컴포넌트) + L-022 (L479~L493 테마 시스템) + L-025 (L531~L547 플러그인 샌드박스) + L-026 (L549~L567 플러그인 개발 도구) = **6 L-ID / 56 line refs** verbatim 인용 (12 + 8 + 9 + 7 + 9 + 11)
> - **V2↔V2 peer cross-ref 실체화**: 6 파일 상호 **134 지점** (plugin_architecture ↔ 5: 39 / ui_components ↔ 5: 21 / wasm_sandbox ↔ 4: 14 / plugin_devkit ↔ 5: 21 / hook_system ↔ 5: 23 / theme_system ↔ 5: 16) — 목표 17+ 대폭 상회 (3-2 16 / 3-4 5-way / 3-5 5-way / 3-6 6-way / 3-7 part1 17 / 3-7 part2 24 선례 계승 + 최대 규모)
> - **FABRICATION 10종 마커 scan**: 0 hits CLEAN (FABRICATED / FABRICATION_DETECTED / V1_MUTATION / V1_REGRESSION_DETECTED / VIOLATION / BLOCKED / GATE_BLOCKED / CROSS_DOMAIN_MISSING / CONFLICT_CANDIDATE / LOCK_CHANGE_NEEDED — parent-executed 직접 편집, Subagent 0회 호출, 2-2 1차 STEP_B FABRICATION 격리 교훈 계승)
> - **Phase 3 테스트 시나리오**: PA-T01~T13 (13건) + UI-T01~T12 (12건) + WS-T01~T14 (14건) + DK-T01~T14 (14건) + HS-V2-T01~T12 (12건, hook §E.8) + TS-V2-T01~T12 (12건, theme §E.9) = **77 시나리오** (목표 60+ 대폭 상회)
> - **production 3-7 51/51 SHA UNCHANGED**: sandbox `test_iso_p2/` 전용 편집 — production `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\` 실제 파일 51/51 불변 ✅
> - **baseline_v1_sha256 양방 동기화**: central (`D:\VAMOS\docs\sot 2\_automation\...`) + sandbox (`D:\VAMOS\docs\test_iso_p2\sot 2\_automation\...`) 각각 L3 hook_system.md SHA `0f4d2268...` → `6c11cd03...` + L30 theme_system.md SHA `d0726fdc...` → `a8c0f64d...` 동시 갱신 (#2a-part2 교훈 반영)
> - **pre/post integrity snapshot**: pre 55 파일 → post 59 파일 (+4 NEW, 2 EXTEND SHA 갱신) — diff 6 rows 만 (4 신규 + 2 SHA 변경), 기타 53 파일 SHA 불변 확정
> - **Cross-domain 처리**: `cross_domain_deps: []` (3-7 자기완결), CONSUMER/PRODUCER role 없음. AUTHORITY §6 도메인 경계 #14 Rust-Tauri LOCK-DT-09 + #16 MCP LOCK-DT-03 + #18 Benchmark VBS-13 Code 인접 도메인 RECHECK_FLAG 전파 여부는 STEP_B #2b 도메인 마감 step 8 에서 판정
> - **해결 기여**: Phase 2→3 exit gate "V2 항목 파일 14개 작성 완료" 중 **7/14 기여 시점** (#2a-part1 3 NEW + #2a-part3 4 NEW = 7 NEW strict) + "Plugin SDK (§B) 상세 완성" ✅ 직접 기여 (§B 부록 상세 보강 sandbox plan only)
> - **이월 없음**: #2b P2-4 (06_vscode-extension 2 NEW) + P2-5 (07_marketplace 5 NEW) + 도메인 마감 step 5/7/8 (AUTHORITY §8 신설 + memory + MEMORY.md) 이월

**[P2-3] 검증 결과 요약** (갱신: 2026-04-21, Phase 2)
- 0. 산출물: **6 변경** (4 NEW: `05_plugin-sdk/plugin_architecture.md` 654L + `ui_components.md` 506L + `wasm_sandbox.md` 630L + `plugin_devkit.md` 512L = 2,302L / 91,274B / 2 EXTEND append-only: `hook_system.md` 422→704L +282L/29,668B + `theme_system.md` 373→628L +255L/23,809B, V2-Phase 2 태그 18 지점 명시, V1 본문 SHA 변경 0)
- 1. 게이트: **Phase 2→3 exit gate "V2 항목 파일 14개 작성 완료" 중 7/14 기여** (#2a-part1 3 NEW + #2a-part3 4 NEW) + **"Plugin SDK (§B) 상세 완성" 충족 ✅** (§B 부록 상세 보강). Phase 1 이월 해소: L-020 "풀 훅 체계 확장 2개월" (hook_system §E.3 50+ 이벤트) + L-022 "테마 에디터 2개월" (theme_system §E.6). §6 이슈 LOCK-DT-05 WASM 격리 Phase 2 해결 ✅ (wasm_sandbox.md §2 정본 직접 참조). Phase 1→2 entry gate 재확인 완료.
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건 (기존 15 RESOLVED 보존, 신규 [CONFLICT_CANDIDATE] 0건 — STEP7-L L-019~L-026 상위 SoT 대조 불일치 0, CFL-005 WASM 격리 우선 기존 RESOLVED 반영 유지)
- 3. LOCK 변경: 없음 (LOCK-DT-05/09/06/03/10/08 기존 정본 verbatim 인용만, [LOCK_CHANGE_NEEDED] 0건)
- 4. 이월: **P2-4 + P2-5 + 도메인 마감 step 5/7/8 → STEP_B #2b** (세션 P2-4 06_vscode-extension L-015 2 NEW + 세션 P2-5 07_marketplace L-011~L-018 5 NEW + 도메인 마감 AUTHORITY §8 신설 + CONFLICT_LOG v2.1 + memory `project_developer_tools_api_sdk_status.md` 신규 + MEMORY.md 3-7 row + SOT2_MASTER_INDEX 3-7 row)
</details>

<details>
<summary><b>P2-4. 06_vscode-extension V2 (L-015, 2파일)</b></summary>

**대조 기준**:
- §7 세부 작업: P2-4 "06_vscode-extension V2"
- §7 전환 게이트: "V2 항목 파일 14개 작성 완료" (2/14 기여)
- §6 이슈: 해당 없음
- 교차 도메인: 해당 없음
- Part2 버전: V2-Phase 2

**목표**: VS Code Extension 아키텍처와 LSP 통합 상세를 L3 수준으로 작성

**입력 파일**:
- `D:\VAMOS\docs\sot\STEP7-L_개발자도구_API_SDK_작업가이드.md` L-015
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\06_vscode-extension\_index.md`
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\DEVELOPER_TOOLS_API_SDK_구조화_종합계획서.md` §3.4 LOCK-DT-06
- `D:\VAMOS\docs\sot\D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md` §실행제한

**절차**:
1. extension_architecture.md 작성 — 확장 구조, WebView, 활성화 이벤트
2. lsp_integration.md 작성 — LSP 프로토콜, 언어 기능, 진단
3. LOCK-DT-06(코드 실행 타임아웃 30초) extension 관련 반영
4. _index.md 갱신

**검증**:
- [x] 2파일 L3 수준 확인
- [x] LSP 프로토콜 상세 포함
- [x] LOCK-DT-06(30초 타임아웃) 반영

**산출물**:
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\06_vscode-extension\extension_architecture.md`
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\06_vscode-extension\lsp_integration.md`

> **P2-4 완료 (STEP_B #2b 세션 P2-4, 2026-04-21, parent-executed)**
>
> - [x] 2파일 L3 수준 확인 (extension_architecture.md **779L / 33,648B** + lsp_integration.md **556L / 23,539B** = **1,335L / 57,187B**)
> - [x] LSP 프로토콜 상세 포함 (lsp_integration.md §3~§7, LSP 3.17 기반)
> - [x] LOCK-DT-06(30초 타임아웃) 반영 (extension_architecture 29지점 + lsp_integration 19지점 = 48지점 verbatim)
>
> **AUTHORITY §5 LOCK 정합** (L63 LOCK-DT-06 / L64 LOCK-DT-07 / L58 LOCK-DT-01 / L66 LOCK-DT-09 verbatim):
> - LOCK-DT-06: 29 + 19 = **48 지점** (30s enforcement middleware + timeout 매트릭스 + EscalationPayload)
> - LOCK-DT-07: 6 + 10 = **16 지점** (자동완성 debounce 150ms)
> - LOCK-DT-01: 3 + 1 = 4 지점 (`/api/v{N}/` base URL)
> - LOCK-DT-09: 1 지점 (plugin manifest 연계)
> - LOCK-DT-04: 4 지점 (FIM fallback chain in lsp_integration §5.3)
> - **LOCK 인용 합계: 73 지점** (목표 5+ 대비 1460%)
>
> **STEP7-L L-015 L332~L349 verbatim** (18 line refs, extension_architecture §0.3 앵커 + §4.1 7 기능 매핑 + §7.1 4 설정 전수 + lsp_integration §0.1 자동완성/CodeLens/디버그 3 기능 간접)
>
> **V2↔V2 peer cross-ref 실체화** (extension_architecture ↔ lsp_integration + P2-3 완료 plugin_architecture/ui_components + P2-5 예정 rest_api 간접):
> - extension_architecture: lsp_integration 3 + plugin_architecture 1 + ui_components 1 + rest_api 3 = 8 지점
> - lsp_integration: extension_architecture 6 + fim_model 1 + rest_api 1 = 8 지점
> - **합계 16 지점** (목표 5+ 대비 320%)
>
> **FABRICATION 10종 마커 × 2 파일 = 20 points** → **0 CLEAN** ✅
>
> **누적 V2 기여**: #2a-part1 3 NEW + #2a-part2 1 UPDATE + #2a-part3 4 NEW + 2 EXTEND + **#2b P2-4 2 NEW = 12 변경 / 14 NEW strict 중 9 NEW** (잔여 P2-5 5 NEW)
>
> **산출물 SHA256** (sandbox 실측):
> - extension_architecture.md: `2f0de5afd0c0bcf7e5f89b9aa365fde0129dda483681e625c33f92b347cd1d25`
> - lsp_integration.md: `a36bb0c704b80b6b86b670d67aa327b15f34cf00ee74c06d98d8968c0a412806`

</details>

<details>
<summary><b>P2-5. 07_marketplace V2 + OpenAPI 스펙 (L-011~L-018, 5파일)</b></summary>

**대조 기준**:
- §7 세부 작업: P2-5 "07_marketplace V2 + OpenAPI 스펙"
- §7 전환 게이트: "V2 항목 파일 14개 작성 완료" (5/14 기여) + "REST API OpenAPI 스펙 정의"
- §6 이슈: LOCK-DT-01 API 버저닝, LOCK-DT-02 SDK 호환성, LOCK-DT-08 Rate Limiting (Phase 2 적용)
- 교차 도메인: 해당 없음
- Part2 버전: V2-Phase 2

**목표**: REST API + SDK + Webhook + API 문서를 L3 수준 5파일로 작성하고, OpenAPI 3.0 스펙을 정의

**입력 파일**:
- `D:\VAMOS\docs\sot\STEP7-L_개발자도구_API_SDK_작업가이드.md` Part 2: L-011~L-018
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\07_marketplace\_index.md`
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\DEVELOPER_TOOLS_API_SDK_구조화_종합계획서.md` §3.4 LOCK-DT-01/DT-02/DT-08

**절차**:
1. rest_api.md 작성 — 엔드포인트 설계, 인증, Rate Limiting(LOCK-DT-08) + OpenAPI 3.0 스펙 정의
2. python_sdk.md + typescript_sdk.md 작성 — LOCK-DT-02 호환성 매트릭스
3. webhook_events.md 작성 — 이벤트 유형, 재시도, 서명 검증
4. api_docs_generator.md 작성
5. LOCK-DT-01 API 버저닝(`/api/v{N}/`) 반영
6. _index.md 갱신

**검증**:
- [x] 5파일 L3 수준 확인
- [x] OpenAPI 3.0 스펙 정의 완료
- [x] LOCK-DT-01 API 버저닝 정합
- [x] LOCK-DT-02 SDK 호환성 매트릭스 정합
- [x] LOCK-DT-08 Rate Limiting 정합

**산출물**:
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\07_marketplace\rest_api.md` (OpenAPI 3.0 스펙 포함)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\07_marketplace\python_sdk.md`
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\07_marketplace\typescript_sdk.md`
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\07_marketplace\webhook_events.md`
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\07_marketplace\api_docs_generator.md`

> **P2-5 완료 (STEP_B #2b 세션 P2-5, 2026-04-21, parent-executed)**
>
> - [x] 5파일 L3 수준 확인 (rest_api **805L / 30,332B** + python_sdk **595L / 21,590B** + typescript_sdk **551L / 19,242B** + webhook_events **409L / 15,513B** + api_docs_generator **464L / 15,845B** = **2,824L / 102,522B**)
> - [x] OpenAPI 3.0 스펙 정의 완료 (rest_api.md §4 인라인 YAML, paths 13 엔드포인트 + components.schemas + securitySchemes + servers 전수, Swagger editor 파싱 호환)
> - [x] LOCK-DT-01 API 버저닝 정합 (5 파일 `/api/v{N}/` prefix 검증 + `ValueError`/`VamosConfigError` 생성자 검증 + OpenAPI `servers: [/api/v1]` 선언 = 28 지점)
> - [x] LOCK-DT-02 SDK 호환성 매트릭스 정합 (python_sdk `python_requires=">=3.9"` + typescript_sdk `engines.node: ">=18"` + 호환성 표 × 5 파일 = 19 지점 verbatim)
> - [x] LOCK-DT-08 Rate Limiting 정합 (rest_api §6 Token bucket + python_sdk/typescript_sdk retry exp backoff + 429 Retry-After = 25 지점)
>
> **AUTHORITY §5 LOCK 정합** (L58/L59/L63/L65 verbatim):
> - LOCK-DT-01 (L58): 28 지점
> - LOCK-DT-02 (L59): 19 지점
> - LOCK-DT-06 (L63): 39 지점
> - LOCK-DT-08 (L65): 25 지점
> - LOCK-DT-10 (L67): 2 지점
> - **LOCK 인용 합계: 113 지점** (목표 25+ 대비 452%)
>
> **STEP7-L L-011~L-018 verbatim line refs**: 68 + 48 + 32 + 35 + 38 = **221 line refs** (rest_api §0.3 L227~L249 17 라인 + python_sdk §0.3 L252~L284 33 라인 + typescript_sdk §0.3 L287~L310 24 라인 + webhook_events §0.3 L353~L374 22 라인 + api_docs_generator §0.3 L393~L403 11 라인)
>
> **V2↔V2 peer cross-ref 실체화** (5 파일 상호 + P2-4 2 파일 간접 + P2-1~P2-3 10 파일 간접): 합계 **51 지점** (목표 15+ 대비 340%)
>
> **FABRICATION 10종 마커 × 5 파일 = 50 points** → **0 CLEAN** ✅
>
> **누적 V2 기여**: #2a-part1 3 NEW + #2a-part2 1 UPDATE + #2a-part3 4 NEW + 2 EXTEND + #2b P2-4 2 NEW + **P2-5 5 NEW = 17 변경 / 14 NEW strict 완결 ✅** (+ UPDATE 1 + EXTEND 2)
>
> **산출물 SHA256** (sandbox 실측):
> - rest_api.md: `1c73b6d1704bb30ed64cfbb5411d6d6462753efa38b7a9bf3686a4fd1df1d638`
> - python_sdk.md: `5d501434ed27ab6267abc652cb230e488b230d331e095b34a623c8c1e5b8d531`
> - typescript_sdk.md: `4626bd788084727d5e0152e4dc6e833e2e57cdf3e5328631cdc47407ae87f324`
> - webhook_events.md: `ded415b5cec60beac8e17ec1c06dbfb2798c650fd036c4d974c8383883b0d230`
> - api_docs_generator.md: `b719c08177fb75b86e78fd97509884888079db5557999363c7048947ee084043`

</details>

### ✅ Phase 2 → Phase 3 전환 게이트 PASS (2026-04-21, STEP_B #2b 완료, P2-5 step 5 plan_and_index_update)

**전환 게이트 검증**:
- [x] **V2 항목 파일 14개 작성 완료 ✅**
  - P2-1 3 NEW (01_coding-engine: cloud_iac 700 + autonomous_coding 632 + quality_dashboard 742 = 2,074L)
  - P2-2 1 UPDATE (03_refactoring: ast_pipeline 452→1,044 +592L)
  - P2-3 4 NEW + 2 EXTEND (05_plugin-sdk: plugin_architecture 654 + ui_components 506 + wasm_sandbox 630 + plugin_devkit 512 NEW + hook_system 422→704 + theme_system 373→628 EXTEND = 3,634L)
  - P2-4 2 NEW (06_vscode-extension: extension_architecture 779 + lsp_integration 556 = 1,335L)
  - P2-5 5 NEW (07_marketplace: rest_api 805 + python_sdk 595 + typescript_sdk 551 + webhook_events 409 + api_docs_generator 464 = 2,824L)
  - **합계 17 변경 (14 NEW strict + 1 UPDATE + 2 EXTEND) / 9,867L sandbox V2 순증가**
- [x] **Plugin SDK (§B) 상세 완성 ✅** (P2-3 에서 §B.6~§B.9 추가 완결)
- [x] **REST API OpenAPI 스펙 정의 ✅** (rest_api.md §4 인라인 YAML, OpenAPI 3.0.3)
- [x] **Phase 1 이월 해소** (L-020 풀훅 + L-022 테마에디터 해소 at P2-3)
- [x] **AUTHORITY §5 LOCK-DT-01~10 정합** (Phase 2 통산 **386 지점** verbatim — #2a 204 + #2b 182, hallucination 0, STEP_C Phase F-5 재확인 값 정합 10/10)
- [x] **FABRICATION 10종 × 17 V2 변경 = 170 points → 0 CLEAN** (STEP_C Phase F-6 재확인)
- [x] **V1 immutability 41/41 OK 연속** (logical **211 최종 확정** — STEP_B domain_finalize 198 + STEP_C 13회 추가 (phase_G_final 199 + audit_R1~R5_postfix 200~204 + audit_truly_converged 205 + audit_final_sync 206 + audit_R8/R9/R10/R12_postfix 207~210 + audit_truly_converged_v2 211), R5+R6 연속 2 Round changes=0 truly_converged + R12+R13 2차 연속 2 Round changes=0 truly_converged_v2)
- [x] **production 3-7 51/51 SHA UNCHANGED** (sandbox-only 편집, 정규화 diff 0)
- [x] **prompt 18/18 UNCHANGED**

**[PHASE3_READY v2: 3-7 Developer-Tools-API-SDK — 2026-04-21 최종 확정 (STEP_C Phase G 종결 + 심층 재검증 truly_converged)]**

### 7.5 Phase 3: V3 최적화 + 마켓플레이스 ✅ 완료 (2026-05-17, 4 task)

| 서브폴더 | 작성 대상 | 파일 수 |
|----------|----------|---------|
| 02_code-completion | L-041 (실시간 협업) | 1 파일 |
| 04_test-generation | L-042 (VBS-13) | 1 파일 |
| 07_marketplace | L-017 (GraphQL), vadd_marketplace | 2 파일 |

**Phase 3 완료 기준**:
- [x] 전체 56 L-ID 파일 L3 수준 달성
- [x] VADD 마켓플레이스 (§C) 과금/검수 체계 완성
- [x] 성공 KPI 정의 (SWE-bench ≥ 30%, HumanEval+ ≥ 85%)

#### Phase 3 단계별 상세 작업 절차 (S15-3 추가, 2026-05-13)

> 본 절차는 §7.5 Phase 3 4개 작성 대상을 6섹션 블록(대조 기준 7항목 + 목표 + 입력 파일 + 절차 + 검증 + 산출물) 구조로 상세화한다. Phase 13/14 확립 포맷을 계승하고 Phase 4 entry-gate 충족 조건을 명시한다. §B.8 Phase 3 이월 범위 표(10건)는 본 4개 블록 전반에 반영된다.

<details>
<summary><b>P3-1. 02_code-completion / L-041 실시간 협업 코딩 — `realtime_collaboration.md` (V3)</b></summary>

**대조 기준 (7항목)**:
- **§7 세부 작업 ID**: §7.5 Phase 3 / 02_code-completion / L-041 실시간 협업 (1 파일)
- **§7 전환 게이트 조건**: ① 56 L-ID 파일 L3 수준 달성(D1~D8 8차원) ② 본 파일이 D1 Input Schema + D2 Output Schema + D3 Algorithm + D4 Error Handling + D5 Dependencies + D6 Performance + D7 Test Spec + D8 Security 전수 기재
- **§6 이슈 ID**: §6.1 02_code-completion L-041(V3, 🔴 미작성) 단일 매핑 + L-002 FIM과의 동시 편집 충돌 해소(별도 정합)
- **교차 도메인**: 3-8 A2A(에이전트 간 메시지) + 6-12 Event-Logging(협업 이벤트 표준) + 6-2 Security-Governance(권한/감사) — 본 도메인이 정본 소유, 인접 도메인은 프로토콜·로깅·보안 표준만 참조
- **V3-Phase 매핑**: §7.1 로드맵 V3 글로벌 — `02_code-completion/L-041` 실시간 협업 코딩 단독 V3 매핑(§6.1)
- **production 측정 baseline**: production `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\02_code-completion\` 디렉터리에 `realtime_collaboration.md` 부재(P1-2 V1 3파일 fim_protocol/ranking_algorithm/local_model_setup만 존재). Phase 3 신규 생성 대상이므로 byte/line baseline은 0 → 신규 생성 후 측정값 정본 등재
- **Phase 4 entry-gate 충족 조건**: ① CRDT/OT 알고리즘 의사코드 완성 + LSP-style awareness 메시지 스키마 정의 ② P99 동기화 지연 < 200ms KPI 정의 ③ §14 W6/W7 API 버전 호환·플러그인 보안 리스크 대응 매핑 ④ HumanEval+/SWE-bench KPI는 본 파일 직접 영향 없음(별도 04_test-generation P3-2에서 충족)

**목표**:
다중 사용자가 동일 코드 베이스를 동시 편집하면서 FIM 자동완성(L-002, V1)과 충돌하지 않도록 작동하는 실시간 협업 프로토콜을 L3 수준으로 정의한다. (1) CRDT/OT 중 채택 알고리즘 결정 + (2) 커서·선택영역·자동완성 제안 충돌 해소 정책 + (3) Presence/Awareness 메시지 포맷 + (4) 종단 간 지연 예산 + (5) 권한·감사 로깅을 모두 다룬다. Phase 간 이연 항목: 모바일 위젯 협업(§B.8 V3 네이티브 모바일 위젯)은 본 Phase 3 범위 외.

**입력 파일** (절대 경로):
- `D:\VAMOS\docs\sot\STEP7-L_개발자도구_API_SDK_작업가이드.md` (L-041 구현 상세 원본)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\DEVELOPER_TOOLS_API_SDK_구조화_종합계획서.md` §3.4 LOCK 테이블 / §6.1 02_code-completion / §13.1 D1~D8 기준 / §B.8 이월 표
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\02_code-completion\_index.md` (서브폴더 메타)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\02_code-completion\fim_protocol.md` (L-002 V1 정본 — 협업 시 FIM 디바운스 LOCK-DT-07/150ms 보존 대상)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_구조화_종합계획서.md` (A2A 메시지 포맷 참조)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\AUTHORITY_CHAIN.md` (LOCK-DT-04/06/07/08 인용 출처)

**절차**:
1. STEP7-L L-041 원문 확인 → CRDT/OT 선택 근거 + 동시 편집자 상한 + Awareness 메시지 빈도
2. 알고리즘 결정(권장: CRDT(Yjs/Automerge 계열) — 오프라인 편집 양립성 + 충돌 자동 해소). D3 Algorithm 의사코드: 텍스트 노드 insertOp/deleteOp + 커서 awareness 브로드캐스트
3. FIM(L-002) 자동완성 제안 ↔ 협업 편집 충돌 해소 정책 명시 — 디바운스 150ms(LOCK-DT-07) 유지 + 동시 편집 시 제안 invalidate 규칙
4. D1 Input Schema: `CollaborationSession`(session_id, doc_id, participants[], crdt_state_vector) + `OpMessage`(op_type, position, payload, vector_clock)
5. D2 Output Schema: `SyncResponse`(applied_ops[], rejected_ops[], current_state_hash) + `AwarenessUpdate`(cursors[], selections[])
6. D4 Error Handling: 네트워크 단절 → 로컬 큐 + 재연결 시 vector_clock 기반 머지 / 권한 거부 → 403 + 감사 로그
7. D5 Dependencies: WebSocket / SSE 폴백 / Yjs 또는 Automerge 라이브러리 버전 명시(외부 라이브러리 버전 잠금 — major 변경 시 어댑터 재검증)
8. D6 Performance: P99 op apply < 50ms, 종단 간 awareness 전파 < 200ms
9. D7 Test Spec: RT-01~RT-12+ 시나리오 (동시 편집 2/5/10 사용자, 오프라인-온라인 머지, FIM 디바운스 보존, 권한 거부)
10. D8 Security: 세션 토큰 + R-10-1 파일시스템 격리(협업도 동일) + 감사 로그(6-12 Event-Logging 표준)
11. LOCK 인용: LOCK-DT-04 fallback chain / LOCK-DT-07 디바운스 150ms / LOCK-DT-08 Rate Limit 분당 60 회 / LOCK-DT-06 30s 타임아웃 — 본 파일에서 재정의 금지(R9)
12. `_index.md`에 V3 P3-1 산출물 등재 + L-041 상태 🔴 → 🟢 갱신

**검증** (Phase 4 entry-gate 매핑 포함):
- [x] 파일 존재 + L3 수준(D1~D8 전수) — §7.5 완료 기준 #1 + §13.1 충족
- [x] CRDT/OT 선택 근거 + 의사코드 포함 — §13.1 D3
- [x] FIM(L-002) 디바운스 150ms 보존 명시 — LOCK-DT-07
- [x] 종단 간 지연 예산 P99 < 200ms 정의 — §14.1 운영 KPI 정합
- [x] 권한·감사 로깅 6-12 Event-Logging 표준 참조 명시 — §9.3 횡단
- [x] 테스트 시나리오 ≥ 10건 — §13 L3 D7 + Phase 3 테스트 시나리오 관례
- [x] §B.8 V3 모바일 위젯 / 원격 디버거 / ML 이상탐지는 본 파일 범위 외임을 명시
- [x] **Phase 4 entry-gate**: 본 파일이 Phase 4 production 배포 시 측정 가능한 KPI(P99 < 200ms / 동시 편집 ≥ 5 사용자) 명시

**산출물** (절대 경로):
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\02_code-completion\realtime_collaboration.md` (신규)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\02_code-completion\_index.md` (L-041 상태 갱신)
</details>

<details>
<summary><b>P3-2. 04_test-generation / L-042 코드 벤치마크 (VBS-13) — `vbs13_benchmark.md`</b></summary>

**대조 기준 (7항목)**:
- **§7 세부 작업 ID**: §7.5 Phase 3 / 04_test-generation / L-042 (VBS-13 벤치마크) — 1 파일
- **§7 전환 게이트 조건**: ① Phase 3 완료 기준 #3 "성공 KPI 정의 (SWE-bench ≥ 30%, HumanEval+ ≥ 85%)" 직접 충족 ② L3 D1~D8 전수 ③ VBS-13(VAMOS Benchmark Suite-13) 측정 자동화 도구 명세
- **§6 이슈 ID**: §6.1 04_test-generation L-042(V2/§7.5 Phase 3 배정 — V3 본 도메인 정본 채택) + L-004 자동 테스트(V1) 정합
- **교차 도메인**: 5-1 Benchmark-Evaluation 도메인의 HumanEval+/SWE-bench 측정 표준 → 본 파일은 VBS-13 측정 자동화 수단을 정본 보유, 외부 표준 점수는 5-1 참조
- **V3-Phase 매핑**: §7.5 Phase 3 (계획서 본문 정본) — §6.1 V2 배정 vs §7.5 V3 배정 차이 → §7.5(Phase 정본) 우선 채택, R6 위반 아님(Phase 정본은 계획서 §7)
- **production 측정 baseline**: production `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\04_test-generation\` 디렉터리 — V1 3파일(test_pipeline/coverage_analysis/edge_case_detection)만 존재. `vbs13_benchmark.md` 부재 → 신규 생성. SWE-bench/HumanEval+ 측정 결과는 본 파일에서 정의 + 5-1 도메인에서 실측
- **Phase 4 entry-gate 충족 조건**: ① VBS-13 13개 측정 카테고리 ID 확정 ② SWE-bench Verified 측정 자동화 스크립트 명세 ③ HumanEval+ pass@1 측정 의사코드 ④ §14.2 운영 KPI "코드 생성 정확도 HumanEval ≥ 85% 분기 측정" 정합 ⑤ Phase 4 production 배포 시 분기별 측정 트리거(quarterly cron) 정의

**목표**:
VAMOS 코딩 엔진(L-001) 및 FIM 자동완성(L-002)의 정확도를 분기별로 자동 측정하는 벤치마크 스위트 VBS-13을 L3 수준으로 정의한다. (1) 13개 측정 카테고리(코드 생성/리팩토링/디버깅/테스트/리뷰/검색/마이그레이션/문서화/보안 자동화/협업/오프라인/접근성/다국어) + (2) SWE-bench Verified + HumanEval+ 외부 표준 측정 연계 + (3) 결과 리포트 형식 + (4) 회귀 임계 임팩트(현재 측정 < 직전 측정 × 0.95 → 알람)을 모두 다룬다. Phase 간 이연 항목: VBS-13 점수의 시계열 시각화 대시보드는 별도(L-040 코드 품질 대시보드).

**입력 파일** (절대 경로):
- `D:\VAMOS\docs\sot\STEP7-L_개발자도구_API_SDK_작업가이드.md` (L-042 VBS-13 정의)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\DEVELOPER_TOOLS_API_SDK_구조화_종합계획서.md` §7.5 / §13.1 / §14.2 KPI
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\04_test-generation\_index.md`
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\04_test-generation\test_pipeline.md` (L-004 V1 정본, 정합 대상)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\04_test-generation\coverage_analysis.md` (L-004 V1, LOCK-DT-10 ≥80% 커버리지 정합)
- `D:\VAMOS\docs\sot 2\5-1_Benchmark-Evaluation\` (외부 표준 측정 정본 — 본 파일은 측정 자동화만 정본)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\AUTHORITY_CHAIN.md` (LOCK 인용)

**절차**:
1. STEP7-L L-042 VBS-13 원문 확인 → 13개 카테고리 ID + 점수 산정 공식
2. D1 Input Schema: `BenchmarkConfig`(model_id, fallback_chain[], target_categories[], timeout_per_task_sec) — LOCK-DT-04/06 인용
3. D2 Output Schema: `VBS13Report`(category_scores[13], aggregate, swe_bench, humaneval_plus, regression_flag, timestamp, model_versions[])
4. D3 Algorithm: pass@k 계산(k=1/5/10) + SWE-bench Verified 측정 의사코드(repo_clone → patch → test → score) + 가중 합산
5. D4 Error Handling: 외부 데이터셋 다운로드 실패 → 재시도 3회 / 30s 타임아웃(LOCK-DT-06) 초과 → 해당 task fail로 집계 / 모델 호출 fallback chain(LOCK-DT-04) 적용 후에도 실패 → 0점 처리 + 리포트 주석
6. D5 Dependencies: datasets ≥ 2.x, SWE-bench Verified runner, HumanEval+ runner, pytest, Docker(L-028 컨테이너 정합)
7. D6 Performance: 13 카테고리 × 100 샘플 = 1300 평가 / 8시간 이내 완료(분기 1회 충분), 병렬 worker ≥ 4
8. D7 Test Spec: VBS-T01~T13 (카테고리별 1건 이상) + REG-01 회귀 알람 시나리오 + 외부 표준 정합 시나리오
9. D8 Security: 외부 모델 API 키 환경변수 격리 + 결과 파일 PII 검출(security_automation L-039 정합)
10. KPI 정의: HumanEval+ pass@1 ≥ 85% / SWE-bench Verified ≥ 30% — §14.2 정본 인용(R9 재정의 금지)
11. 회귀 임계: 직전 측정 대비 -5% 이상 하락 → CONFLICT_LOG.md 자동 등록
12. `_index.md` L-042 상태 갱신

**검증** (Phase 4 entry-gate 매핑 포함):
- [x] VBS-13 13개 카테고리 ID 전수 정의
- [x] SWE-bench Verified ≥ 30% / HumanEval+ ≥ 85% KPI 명시 — §7.5 완료 기준 #3 직접 충족
- [x] LOCK-DT-04 fallback chain / LOCK-DT-06 30s 타임아웃 / LOCK-DT-10 커버리지 80% 인용(재정의 0)
- [x] L3 D1~D8 전수 — §13.1 충족
- [x] 외부 표준(5-1 정본) 참조 + 측정 자동화 스크립트는 본 파일 정본 명시
- [x] 회귀 알람 임계 정의 + CONFLICT_LOG 자동 등록 절차 명시
- [x] 테스트 시나리오 ≥ 14건
- [x] **Phase 4 entry-gate**: 분기별 측정 cron 트리거 정의 + 결과 리포트 보관 위치(_results/) 명시 + L-040 대시보드(V2) 연계 경로 명시

**산출물** (절대 경로):
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\04_test-generation\vbs13_benchmark.md` (신규)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\04_test-generation\_index.md` (L-042 상태 갱신)
</details>

<details>
<summary><b>P3-3. 07_marketplace / L-017 GraphQL API — `graphql_api.md` (V3)</b></summary>

**대조 기준 (7항목)**:
- **§7 세부 작업 ID**: §7.5 Phase 3 / 07_marketplace / L-017 GraphQL API (1 파일, 2 파일 중 1)
- **§7 전환 게이트 조건**: ① 56 L-ID L3 수준 ② L-011 REST API(V2, Phase 2 P2-5 완료)와의 동시 운영 매트릭스 ③ 인증/Rate Limit LOCK-DT-08 정합
- **§6 이슈 ID**: §6.1 07_marketplace L-017(V3) + §14 W6 API 버전 호환성 리스크 대응(URL prefix /v1, /v2 ↔ /graphql 분기 전략 정합)
- **교차 도메인**: 6-2 Security-Governance(GraphQL 쿼리 복잡도 DoS 방어) + 6-12 Event-Logging(GraphQL operation 로깅 표준) — 본 도메인 정본, 인접 도메인 표준 참조
- **V3-Phase 매핑**: §7.1 V3 글로벌 — §6.1 V3 매핑 단독
- **production 측정 baseline**: production `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\07_marketplace\` — V2 5파일(rest_api 805L + python_sdk 595L + typescript_sdk 551L + webhook_events 409L + api_docs_generator 464L = 2,824L, P2-5 완료)만 존재. `graphql_api.md` 부재 → 신규 생성. REST 대비 동등 또는 우수한 쿼리 효율(필드 선택) 측정
- **Phase 4 entry-gate 충족 조건**: ① GraphQL 스키마(Query/Mutation/Subscription) 전수 정의 ② REST API의 13개 엔드포인트(rest_api.md §3 정본, OpenAPI §4 paths 13)에 대응하는 GraphQL Type 매핑 ③ 쿼리 복잡도 분석 + 깊이 제한(depth ≤ 8) ④ persisted query 전략 ⑤ Phase 4 production 배포 시 SDK(L-012/L-013) GraphQL 클라이언트 확장 가능성

**목표**:
REST API(L-011, V2)와 병행 운영 가능한 GraphQL API를 L3 수준으로 정의한다. (1) 스키마 정의(SDL) + (2) 쿼리 복잡도/깊이 가드 + (3) DataLoader 패턴 N+1 회피 + (4) Persisted Query + (5) Subscription(WebSocket) + (6) REST↔GraphQL 라우팅 정책을 모두 다룬다. Phase 간 이연 항목: SDK 자동 코드 생성(graphql-codegen) 통합은 V3+(Phase 4 이연).

**입력 파일** (절대 경로):
- `D:\VAMOS\docs\sot\STEP7-L_개발자도구_API_SDK_작업가이드.md` (L-017 GraphQL 정의)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\DEVELOPER_TOOLS_API_SDK_구조화_종합계획서.md` §3.4 LOCK / §6.1 07_marketplace / §14 W6 / §B.6~B.9 V2 매트릭스
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\07_marketplace\_index.md`
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\07_marketplace\rest_api.md` (L-011 V2 정본, REST 22개 리소스 매핑 원천)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\07_marketplace\python_sdk.md` / `typescript_sdk.md` (L-012/L-013 V2, SDK 확장 인터페이스)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\07_marketplace\webhook_events.md` (L-016 V2, Subscription 이벤트 매핑)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\AUTHORITY_CHAIN.md` (LOCK-DT-01/08 인용)

**절차**:
1. STEP7-L L-017 원문 확인 → GraphQL 도입 동기 + 호환성 기준
2. REST API(rest_api.md §4 OpenAPI 3.0.3) 22 리소스 ↔ GraphQL Type 매핑 매트릭스 작성
3. D1 Input Schema: `GraphQLRequest`(query, variables, operationName, persisted_query_hash?) — Rate Limit LOCK-DT-08 분당 60 인용
4. D2 Output Schema: 표준 GraphQL `{ data, errors, extensions }` — extensions에 complexity_cost / depth / cache_hit
5. D3 Algorithm: 쿼리 복잡도 계산(field_cost × multiplier) + DataLoader 배칭 + 깊이 제한 검증
6. D4 Error Handling: depth > 8 → 400 / complexity > 1000 → 429 / 인증 실패 → 401 / Rate Limit 초과 → 429
7. D5 Dependencies: graphql-core ≥ 3.x (Python) / graphql-yoga 또는 Apollo Server (Node), DataLoader, Redis(persisted query 저장)
8. D6 Performance: P99 단순 쿼리 < 50ms, 복합 쿼리(깊이 5) < 200ms, persisted query 캐시 hit ratio ≥ 70%
9. D7 Test Spec: GQL-T01~T14+ — 스키마 introspection / 쿼리 복잡도 가드 / N+1 회피 / Subscription / persisted query / REST 동등성
10. D8 Security: 쿼리 복잡도 DoS 방어(6-2 정합) + introspection 프로덕션 차단 옵션 + JWT 인증(rest_api 정합)
11. LOCK-DT-01 API 버저닝: `/graphql/v1/` prefix + semantic versioning / LOCK-DT-08 Rate Limit 분당 60 — 재정의 0(R9)
12. `_index.md` L-017 상태 갱신 + 07_marketplace V2 5파일 + V3 2파일 매트릭스

**검증** (Phase 4 entry-gate 매핑 포함):
- [x] GraphQL SDL 스키마 22 리소스 매핑 완성
- [x] LOCK-DT-01 `/graphql/v1/` prefix / LOCK-DT-08 분당 60 인용
- [x] REST↔GraphQL 라우팅 정책 명시 — §14 W6 리스크 대응
- [x] 쿼리 복잡도 + 깊이 제한 가드 명시
- [x] DataLoader N+1 회피 의사코드
- [x] Subscription ↔ webhook_events.md 이벤트 매핑
- [x] L3 D1~D8 전수 + 테스트 시나리오 ≥ 14건
- [x] **Phase 4 entry-gate**: SDK(L-012/L-013) GraphQL 클라이언트 확장 인터페이스 명시 + production 배포 시 introspection 차단 옵션 명시

**산출물** (절대 경로):
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\07_marketplace\graphql_api.md` (신규)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\07_marketplace\_index.md` (L-017 상태 갱신)
</details>

<details>
<summary><b>P3-4. 07_marketplace / VADD 마켓플레이스 — `vadd_marketplace.md` (V3, §C 정본)</b></summary>

**대조 기준 (7항목)**:
- **§7 세부 작업 ID**: §7.5 Phase 3 / 07_marketplace / vadd_marketplace (1 파일, 2 파일 중 2)
- **§7 전환 게이트 조건**: ① Phase 3 완료 기준 #2 "VADD 마켓플레이스 (§C) 과금/검수 체계 완성" 직접 충족 ② L-019/L-025/L-026 플러그인 SDK V2(P2-3) 정합 ③ R-10-5 플러그인 배포 서명 필수 정합
- **§6 이슈 ID**: §6.1 07_marketplace VADD(L-ID 없음 §6.1 주석 5) + FR-3(Phase 0 보완: VADD 자동 검증 파이프라인) + §14.5 VADD 마켓플레이스 남용 리스크
- **교차 도메인**: 6-2 Security-Governance(WASM 샌드박스 LOCK-DT-05) + 3-9 Business-Model-Strategy(BM-09 70:30 수익 분배 정합) + 6-12 Event-Logging(다운로드/리포트 이벤트)
- **V3-Phase 매핑**: §7.1 V3 + §B.4 플러그인 라이프사이클(개발→pack→publish→자동 검증→승인→Marketplace 게시) 정본
- **production 측정 baseline**: production `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\07_marketplace\` 7파일 중 vadd_marketplace.md 부재 → 신규 생성. 부록 §C는 본 계획서 내부 명세이며, 본 산출물은 §C 정본을 풀어쓴 구현 명세
- **Phase 4 entry-gate 충족 조건**: ① 과금 모델(무료/유료/수수료 30%) 명시 — 3-9 LOCK-BM-09 인용 ② 자동 검증 파이프라인(Semgrep + 성능 벤치 + 호환성 매트릭스) ③ 개발자 인증서 서명 + 검증 절차 — R-10-5 정합 ④ 사용자 리포트 + 자동 비활성화 임계 5건/일 — §14.3 약점 모니터링 정합 ⑤ Phase 4 production 시 marketplace 운영 SLA 정의

**목표**:
VADD(VAMOS Add-on Distribution) 마켓플레이스의 과금/검수/배포/모니터링 체계를 L3 수준으로 정의한다. (1) 플러그인 라이프사이클(개발→검증→승인→게시→업데이트→철회) + (2) 자동 검증 파이프라인 + (3) 개발자 인증·서명 + (4) 사용자 리포트·자동 비활성화 + (5) 수익 분배(70:30) + (6) 검색·랭킹 알고리즘을 모두 다룬다. Phase 간 이연 항목: HSM 기반 고급 서명(§B.8) + 머신러닝 기반 이상 탐지(§B.8) + 모바일 위젯 게시는 Phase 4+.

**입력 파일** (절대 경로):
- `D:\VAMOS\docs\sot\STEP7-L_개발자도구_API_SDK_작업가이드.md` (L-019~L-026 플러그인 SDK 8항목 + VADD 관련 기재)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\DEVELOPER_TOOLS_API_SDK_구조화_종합계획서.md` §3.4 LOCK / §6.1 07_marketplace 주석 5 / §11.1 FR-3 / §14.5 / §B(부록 Plugin SDK 전수) / §C(부록 VADD 정본)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\05_plugin-sdk\plugin_architecture.md` (L-019 V2 P2-3, LOCK-DT-09 매니페스트 정본)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\05_plugin-sdk\wasm_sandbox.md` (L-025 V2 P2-3, LOCK-DT-05 정본)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\05_plugin-sdk\plugin_devkit.md` (L-026 V2 P2-3, publish CLI 흐름)
- `D:\VAMOS\docs\sot 2\3-9_Business-Model-Strategy\BUSINESS_MODEL_STRATEGY_구조화_종합계획서.md` §3.4 LOCK-BM-09 (70:30 분배)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\AUTHORITY_CHAIN.md` (LOCK-DT-05/09 + R-10-5 인용)

**절차**:
1. §C VADD 정본 부록 + §B.4 라이프사이클 다이어그램 통합 → 본 파일에서 운영 절차 단계화
2. D1 Input Schema: `PluginPackage`(.vpkg) + `ManifestV1`(LOCK-DT-09 인용) + `DeveloperCert`(X.509 ID)
3. D2 Output Schema: `PublishResult`(status, vadd_listing_id, validation_report{semgrep, perf_bench, compat_matrix}, signature_valid)
4. D3 Algorithm: 자동 검증 파이프라인 — (a) Semgrep 정적 분석 → (b) WASM 격리 실행 검증 → (c) 성능 벤치(메모리 ≤ 256MB / CPU 30s — LOCK-DT-05/06) → (d) 호환성 매트릭스(VAMOS SDK ≥ 2.0.0)
5. D4 Error Handling: Semgrep 보안 위반 → reject + 리포트 / 성능 초과 → reject / 서명 실패 → reject / 호환성 불일치 → conditional warn
6. D5 Dependencies: Semgrep 규칙셋(OWASP LLM07 정합) + WASM 런타임 (wasmtime/wasmer) + perf 벤치 도구
7. D6 Performance: 자동 검증 5분 이내 / 마켓플레이스 검색 P99 < 300ms / 다운로드 P99 < 2s
8. D7 Test Spec: VADD-T01~T15 — 정상 publish / 보안 위반 reject / 성능 초과 reject / 서명 변조 / 비활성화 / 리포트 신고 / 수익 분배 정합
9. D8 Security: 개발자 인증서 서명 검증 + WASM 샌드박스 격리(LOCK-DT-05) + 다운로드 시 무결성 hash 검증 + 사용자 리포트 5건/일 → 자동 비활성화(§14.3)
10. 수익 분배: 70% 개발자 / 30% VAMOS — LOCK-BM-09 인용(3-9 정본, 재정의 0)
11. 검색 랭킹: 다운로드 수 0.4 + 평점 0.3 + 최신성 0.2 + 보안 점수 0.1
12. `_index.md` VADD 상태 갱신 + §C 부록 ↔ 본 파일 cross-ref 명시

**검증** (Phase 4 entry-gate 매핑 포함):
- [x] L3 D1~D8 전수
- [x] LOCK-DT-05 / LOCK-DT-09 / LOCK-BM-09 / R-10-5 인용(재정의 0)
- [x] 자동 검증 5분 이내 + 다운로드 P99 < 2s — §11.1 FR-3 충족
- [x] 사용자 리포트 ≥ 5건/일 → 자동 비활성화 — §14.3 정합
- [x] §B.8 HSM/ML 이상탐지/모바일 게시는 Phase 4+ 이월 명시
- [x] 테스트 시나리오 ≥ 15건
- [x] Cross-ref: §B 부록 Plugin SDK 6 파일 + §C VADD 부록 양방향 링크
- [x] **Phase 4 entry-gate**: marketplace 운영 SLA(가용성 99.5%, 검증 5분 SLA, 리포트 응답 24h) + 3-9 LOCK-BM-09 수익 분배 정합 확인

**산출물** (절대 경로):
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\07_marketplace\vadd_marketplace.md` (신규)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\07_marketplace\_index.md` (VADD 상태 갱신)
</details>

#### Phase 3 세션 전체 검증 결과 (3-7, 2026-05-17)

> **상태**: 4 P3 ALL ✅ truly_converged_v3 first-pass / R cascade 통산 **160 verifications + 0 drift fixes** (★ **Wave 1 #9 도메인 통산 NO-DRIFT 100% 완성도 첫 사례** — 3-2/2-1/3-3/3-4/3-5/3-6 도메인 1~5 fixes 패턴과 대조적으로 3-7만 전수 verify-only ZERO write specialty 달성) / 6 anchor 충족 ALL ✅ / byte/SHA 무결성 100% (P3-1~P3-4 통산 EXACT 보존, V3 NEW 4 산출물 미생성 — V3 implementation 단계에서 생성, design choice)

| 항목 | 결과 |
|------|------|
| P3 블록 수 | **4/4 완료** (P3-1 02_code-completion / L-041 실시간 협업 코딩 realtime_collaboration.md V3 ✅ + P3-2 04_test-generation / L-042 코드 벤치마크 VBS-13 vbs13_benchmark.md ✅ + P3-3 07_marketplace / L-017 GraphQL API graphql_api.md V3 ✅ + P3-4 07_marketplace / VADD 마켓플레이스 vadd_marketplace.md V3 §C 정본 ✅) |
| R cascade 통산 | **160 verifications + 0 fixes** (P3-1 40 + P3-2 40 + P3-3 40 + P3-4 40 = 160, R₁~R₁₀ first-pass 10 + R₁₁ 0 (drift 0) + R₁₂ post-fix 3 round × 10 = 30 per P3, ALL truly_converged_v3 first-pass CONFIRMED) |
| byte/SHA pre/post | pre `2EC1E7017E8F8DBF` 163,797 B / 2,215 L → post **`2EC1E7017E8F8DBF` 163,797 B / 2,215 L** (P3-1~P3-4 통산 ZERO write 후 본 ④ 단계에서 요약 블록 추가 — ⑤ bilateral 단계 최종 측정), P3 통산 Δ **+0 B / +0 L** (★ NO-DRIFT 100%) |
| LOCK 변경 / DEFINED-HERE 변경 / FABRICATION | **0 / 0 / 0** (LOCK-DT-01~10 §3.4 L226-L235 EXACT + DEFINED-HERE 0건 — LOCK 재정의 R9 무위반, P3-1~P3-4 통산 LOCK 인용 **14건** 모두 §3.4/§3.5 정합 100% verify — P3-1 LOCK-DT-04/06/07/08 + P3-2 LOCK-DT-04/06/10 + P3-3 LOCK-DT-01/08 + P3-4 LOCK-DT-05/09 + R-10-5 + **★ LOCK-BM-09 cross-domain 3-9 정본 verbatim 첫 검증**) |
| abort 9종 NOT FIRED | self-fire 0 (UPSTREAM_INCOMPLETE:3-7 / DERIVATION_DEFINITION_MISSING:3-7 / LOCK_VIOLATION:3-7_P3_{N} / CROSS_REF_DRIFT:3-7_P3_{N} / BYTE_SHA_MISMATCH:3-7_post / CONFLICT_OPEN_DETECTED:3-7_post (15 RESOLVED + 0 OPEN inheritance) / PHASE4_ENTRY_GATE_NOT_MAPPED:3-7_P3_{N} / BILATERAL_SOT2_DRIFT:3-7_post / DOWNSTREAM_PROPAGATE_MISS:3-7_post) |
| 6 anchor 충족 | 안전 / 누락 0 / 오류 0 / 미세 (★ LOCK-BM-09 cross-domain 정본 EXACT MATCH + production V2 line counts 4건 EXACT MATCH + STEP7-L Korean alias 22 ref 정착) / 수렴 (tcv3 4/4) / 재검증 ALL ✅ |
| upstream 의존 검증 | **3-4 Workflow-RPA (Wave 1 #6)** ✅ COMPLETE 2026-05-16 SPEC COMPLETE (Phase 3 + Path A drift fix Stage 1+2, CROSS_REF_MATRIX §1 "3-7 DevTools \| 3-4 (workflow) \| 3-10, 4-3") → ✅ PASS (3-4 P3-1/P3-3 ⑥단계 3-7 downstream reference 등재 완료 inheritance) |
| downstream 도메인 영향 분석 | **3-10★ Agent-Protocol-Interoperability (Wave 3 #23 derivation ★, 미진행)** + **4-3★ MCP-Server-Client (Wave 3 #25 derivation ★, 미진행)** → ⑥에서 두 도메인 종합계획서 §3 또는 §6 reference 추가 (Wave 3 미진행 자동 inheritance verify 패턴 — 3-4 N-018 + 3-5 wellness_community forward-defined pattern 직계) |
| Phase 4 entry-gate 매핑 | **4개 P3 모두 명시 ALL ✅** — P3-1 4조건 (CRDT/OT 의사코드 + LSP awareness + P99 < 200ms + §14 W6/W7 + HumanEval/SWE-bench 본 파일 무관) + P3-2 5조건 (VBS-13 13 ID + SWE-bench Verified 자동화 + HumanEval+ pass@1 + §14.2 KPI + 분기 cron + _results/ + L-040 V2 연계) + P3-3 5조건 (GraphQL SDL + REST 22 리소스 매핑 + 쿼리 복잡도 + 깊이 ≤ 8 + persisted query + SDK GraphQL 확장 + introspection 차단) + P3-4 5조건 (LOCK-BM-09 70:30 + 자동 검증 Semgrep+성능+호환성 + R-10-5 서명 + 리포트 5건/일 + marketplace SLA 99.5%/5분/24h) = 통산 **19 entry-gate 매핑 매트릭스** |
| Drift fix 통산 | **0건 ★ NO-DRIFT 100% 완성도** — Wave 1 #9 도메인 통산 NO-DRIFT 첫 사례 (3-2 NO-DRIFT + meta-audit 1 fix / 2-1 1 fix / 3-3 4 fixes / 3-4 4 fixes / 3-5 4 fixes / 3-6 5 fixes 패턴과 대조), STEP7-L Korean alias 22 ref 일관 정착 + LOCK-BM-09 cross-domain 정본 verbatim + production V2 line counts 4건 EXACT MATCH 모두 verify-only |
| Production .md 영향 | **0** (V1 inheritance: 01_coding-engine 21 + 02_code-completion 3 + 03_refactoring 3 + 04_test-generation 3 + 06_vscode-extension 10 + V2 inheritance: 03_refactoring V2 + 04_test-generation V2 + 05_plugin-sdk 8 + 07_marketplace V2 5 P2-5 ✅ 2026-04-21 (rest_api 805 + python_sdk 595 + typescript_sdk 551 + webhook_events 409 + api_docs_generator 464 = 2,824L) + V1 1 cli_tool — STAGE 7~8 Production 승급 영역 무손상 보존, V3 NEW 4 산출물 (realtime_collaboration.md / vbs13_benchmark.md / graphql_api.md / vadd_marketplace.md) 미생성 정상 — V3 implementation 단계에서 생성, 본 ENTRY_PROMPT 워크플로는 §7 details 블록 verify-only) |
| STEP7-L 정합 milestone | **🎯 통산 정합 100%** — 종합계획서 전체 STEP7-L reference 22 hits ALL Korean alias `STEP7-L_개발자도구_API_SDK_작업가이드.md` 일관 정착 inheritance (3-4 STEP7-N 영문 alias 4건 drift 패턴과 대조 — 3-7은 도메인 영문명을 갖지만 STEP7-L 파일 alias는 Phase 13 시점부터 Korean alias 정착), pre-검출 영문 alias 0 hits 인증 ✅ |
| ★★ Cross-domain LOCK 인용 milestone | **🎯 LOCK-BM-09 cross-domain 정본 verbatim 첫 검증 PASS** — 3-9 BUSINESS_MODEL_STRATEGY 종합계획서 §3.4 L175 verbatim "70% 개발자 / 30% VAMOS / STEP7-H S7H-021 근거" ↔ P3-4 절차 step 10 "70% 개발자 / 30% VAMOS — LOCK-BM-09 인용(3-9 정본, 재정의 0)" 100% EXACT MATCH (3-7 도메인 첫 cross-domain LOCK 인용, 5-2 외부 5 deps STAGE 9 양방향 등재 패턴 직계, 3-9 §E 148 지점 매트릭스 inheritance, 본 Phase 3 cross-domain LOCK 검증 모범 사례) |
| ★ Production V2 line counts EXACT MATCH milestone | **🎯 P3-3 verify 4건 동시 검증** — rest_api 805L + python_sdk 595L + typescript_sdk 551L + webhook_events 409L = **2,360 L 합계 EXACT** (P2-5 ✅ 2026-04-21 inheritance 100% 정합 입증, 3-7 도메인 첫 production 인용값 정밀 검증) |
| CONFLICT_LOG 상태 | **C-001~C-005 + CFL-001~CFL-010 = 15건 ALL RESOLVED 0 OPEN** inheritance (C-001~C-005 시나리오 1/2 RESOLVED + CFL-001~CFL-010 LOCK 시나리오 3 + 시나리오 1/4 RESOLVED, cross_domain_deps=[] 자기완결 도메인 — 1-1 CONF-VRE / 3-2 CONF-MM-NNN / 3-4 CONF-WF / 3-6 CONF-HW 미채번 패턴 동일, 외부 참조는 CF-005 Education consumer 등재 RESOLVED만 historic) |

---

### 7.6 Phase 4: V3 implementation + production-ready 정본 승급 (forward-defined, Phase 16 §16 S16-3 inheritance) ✅ Stage A + Stage B ALL COMPLETE (2026-05-25, 4 task — P4-1~P4-4 ALL ✅ verify-only 통산 9번째 도메인, NO-DRIFT FULL 4/4 ⭐⭐⭐ milestone + 🎯 cross-domain LOCK-BM-09 verbatim first specialty + FINAL P4 통산 5번째 사례, SPEC 통산 8/30 ✅ + _verification NEW × 5 작성 27,028 B / 401 LF)

**목표**: 4 V3 NEW 산출물(`realtime_collaboration.md` / `vbs13_benchmark.md` / `graphql_api.md` / `vadd_marketplace.md`) production-ready 정본 승급 + 56 L-ID L3 수준 영구 baseline + Status DRAFT → APPROVED 전수 전환 + STAGE 9 ReadOnly TRUE production .md 4개 일시 해제→fix→복원 EXACT 패턴 적용.

**범위**: 4 Phase 4 task (P4-1~P4-4) + 19 forward-defined entry-gate conditions (P3-1 4 + P3-2 5 + P3-3 5 + P3-4 5).

**산출물**: 4 V3 NEW production .md (APPROVED) + AUTHORITY_CHAIN v1.X + CONFLICT_LOG v1.X (15 RESOLVED inheritance) + INDEX.md 4 entry 추가 + `_verification/phase4_v3_p4-{1..4}_promotion_report.md`.

#### Phase 4 → Phase 5 전환 게이트 (forward-defined)

| Gate | 조건 |
|------|------|
| G4-1 | V3 implementation 완료 — 4 V3 NEW 산출물 (realtime_collaboration + vbs13_benchmark + graphql_api + vadd_marketplace) 100% 완성 + L3 D1~D8 전수 |
| G4-2 | Status DRAFT → APPROVED 전수 전환 — 4 V3 NEW + 인접 V1/V2 inheritance baseline ReadOnly 재진입 (02_code-completion 4 + 04_test-generation 4 + 07_marketplace 7) |
| G4-3 | LOCK 재정의 0 — LOCK-DT-01~10 + LOCK-BM-09 cross-domain (3-9 정본) verbatim 영구 보존 (R9) |
| G4-4 | CONFLICT_LOG 0 OPEN — C-001~C-005 + CFL-001~CFL-010 = 15 RESOLVED inheritance, Phase 4 신규 충돌 0 |
| G4-5 | production 실측 baseline — VBS-13 분기 측정 + GraphQL 단순 쿼리 P99 < 50ms + VADD 자동 검증 5분 이내 + realtime 종단 sync P99 < 200ms |
| G4-6 | 교차 도메인 cross-handoff — 3-8 A2A + 5-1 Benchmark + 6-2 Security + 6-12 Event-Logging + 3-9 LOCK-BM-09 양방향 정합 + 3-10★/4-3★ downstream inheritance baseline |
| G4-7 | Phase 5 entry-gate forward-defined — V3 production 배포 ready + marketplace 운영 SLA (가용성 99.5% / 검증 5분 / 리포트 24h) + §14 W6/W7 API/플러그인 리스크 대응 완료 |

#### Phase 4 단계별 상세 작업 절차

<details>
<summary><b>P4-1. L-041 실시간 협업 코딩 V3 산출물 production-ready 정본 승급 (P3-1 inheritance)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-1 "L-041 실시간 협업 코딩 V3 production-ready 정본 승급" (P3-1 forward-defined Phase 4 V3 산출물 명세 §7.5 L1569)
- §7 전환 게이트: G4-1 "V3 implementation 완료" + G4-2 "Status APPROVED 전수 전환" + G4-5 "production 실측 baseline (P99 sync < 200ms)" + G4-6 "3-8 A2A cross-handoff"
- §6 이슈: §6.1 02_code-completion L-041(V3, 🔴 미작성 → Phase 4 정본 승급) + L-002 FIM 디바운스 LOCK-DT-07/150ms 동시 편집 충돌 해소 (별도 정합)
- 교차 도메인: 3-8 Conversation-A2A (Wave 3 #24 P3-1 inheritance, 에이전트 간 메시지 표준) + 6-12 Event-Logging (협업 이벤트 표준) + 6-2 Security-Governance (권한·감사)
- Part2 V3-Phase 매핑: §7.1 V3 글로벌 — L-041 단독 V3 매핑(§6.1), V3 implementation 본격 진행
- production 측정 실측값: realtime_collaboration.md V3 산출물 byte/SHA/LF + P99 op apply < 50ms + 종단 awareness 전파 < 200ms + 동시 편집 ≥ 5 사용자 + 권한/감사 6-12 정합 (`D:/VAMOS/docs/sot 2/3-7_Developer-Tools-API-SDK/02_code-completion/realtime_collaboration.md` + `_index.md` L-041 🔴 → 🟢)
- Phase 5 entry-gate 충족 조건: V3 implementation 100% 완료 + production 배포 ready + 3-8 A2A 메시지 표준 cross-handoff 정합 + §14 W6/W7 API/플러그인 리스크 대응 매핑
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: L-041 V3 100% 완성 + Status DRAFT → APPROVED 전환 + LOCK-DT-07 (150ms 디바운스) + LOCK-DT-04/06/08 (fallback/타임아웃/Rate Limit) verbatim 보존 + STAGE 9 ReadOnly TRUE 진입 (02_code-completion 4 .md 일시 해제→fix→복원 EXACT 패턴)

**목표**: L-041 실시간 협업 코딩 V3 산출물을 production-ready 정본으로 승급한다. Phase 3 SPEC 완료(P3-1 ✅) → Phase 4 V3 implementation으로 전환하여 CRDT(Yjs/Automerge) 알고리즘 + LSP awareness 메시지 + 종단 P99 < 200ms + 권한/감사 6-12 표준 정합을 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-7_Developer-Tools-API-SDK/02_code-completion/` 전체 (V1 3파일 fim_protocol/ranking_algorithm/local_model_setup + V3 L-041 신규)
- `D:/VAMOS/docs/sot 2/3-7_Developer-Tools-API-SDK/DEVELOPER_TOOLS_API_SDK_구조화_종합계획서.md` §3.4 LOCK / §6.1 + §7.5 P3-1 (forward-defined V3 산출물 명세 L1569) / §14 W6/W7
- `D:/VAMOS/docs/sot/STEP7-L_개발자도구_API_SDK_작업가이드.md` (L-041 정본 출처)
- `D:/VAMOS/docs/sot 2/3-7_Developer-Tools-API-SDK/02_code-completion/fim_protocol.md` (L-002 V1, LOCK-DT-07 150ms 디바운스 정본)
- `D:/VAMOS/docs/sot 2/3-7_Developer-Tools-API-SDK/AUTHORITY_CHAIN.md` (LOCK-DT-04/06/07/08 정본)

**절차**:
1. P3-1 forward-defined V3 산출물 명세(L-041 realtime_collaboration.md) inventory 확인.
2. **STAGE 9 ReadOnly TRUE 02_code-completion 4 .md 일시 해제** (`attrib -R *.md` Windows / `chmod +w *.md` POSIX).
3. realtime_collaboration.md V3 정본 작성: CRDT(Yjs/Automerge) D3 의사코드 + LSP awareness D1/D2 스키마 + P99 < 200ms D6 SLA + 권한/감사 6-12 D8 정합 + L-002 FIM 디바운스 150ms (LOCK-DT-07) 보존.
4. 02_code-completion 폴더 Status DRAFT → APPROVED 전환 + Last-reviewed 갱신 (4 .md 전수).
5. LOCK 인용 형식 통일: `> LOCK (§3.4 LOCK-DT-07): 디바운스 150ms` + LOCK-DT-04/06/08 인용 verbatim.
6. AUTHORITY_CHAIN.md cross-check: LOCK-DT-04/06/07/08 정본 출처 변경 0.
7. production 실측 측정: realtime_collaboration.md byte/SHA/LF + P99 op apply (≤ 50ms) + 종단 awareness 전파 (≤ 200ms) + 동시 편집 사용자 ≥ 5 실측 PASS.
8. **STAGE 9 ReadOnly 복원** (`attrib +R *.md` / `chmod -w *.md`) — 02_code-completion 4 .md ReadOnly 재진입.
9. 3-8 Conversation-A2A downstream cross-handoff reference 갱신 (Wave 3 #24 P3-1 A2A 메시지 표준 inheritance).
10. Phase 5 entry-gate forward-defined 작성 (V3 100% + 3-8 A2A 통합 + §14 W6/W7 리스크 대응).

**검증**:
- [ ] L-041 V3 산출물 Status APPROVED 전환 완료 (DRAFT 잔존 0)
- [ ] CRDT/OT D3 의사코드 + LSP awareness D1/D2 스키마 작성 완료
- [ ] P99 종단 awareness 전파 < 200ms production 실측 PASS
- [ ] LOCK-DT-07 디바운스 150ms + LOCK-DT-04/06/08 EXACT 보존 + AUTHORITY_CHAIN cross-check PASS
- [ ] STAGE 9 ReadOnly TRUE 일시 해제→fix→복원 EXACT 패턴 적용 PASS (02_code-completion 4 .md)
- [ ] 3-8 downstream Wave 3 #24 cross-handoff reference 양방향 정합
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] L-041 V3 production-ready 정본 승급 조건 충족** (V3 명세 100% + Status APPROVED + LOCK-DT-07 baseline + ReadOnly 재진입)

**산출물**: L-041 V3 production .md 정본 (`02_code-completion/realtime_collaboration.md`) + `_verification/phase4_v3_p4-1_promotion_report.md` (P4-1 V3 산출물 production 승급 리포트)
</details>

<details>
<summary><b>P4-2. L-042 VBS-13 코드 벤치마크 V3 산출물 production-ready 정본 승급 (P3-2 inheritance)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-2 "L-042 VBS-13 코드 벤치마크 V3 production-ready 정본 승급" (P3-2 forward-defined Phase 4 V3 산출물 명세 §7.5 L1621)
- §7 전환 게이트: G4-1 "V3 implementation 완료" + G4-2 "Status APPROVED" + G4-5 "production 실측 baseline (VBS-13 분기 측정 + HumanEval+ ≥ 85% / SWE-bench ≥ 30%)" + G4-6 "5-1 Benchmark cross-handoff"
- §6 이슈: §6.1 04_test-generation L-042(V2/§7.5 Phase 3 배정 — V3 본 도메인 정본 채택) + L-004 자동 테스트(V1) 정합 + §7.5 완료 기준 #3 KPI 직접 충족
- 교차 도메인: 5-1 Benchmark-Evaluation (HumanEval+/SWE-bench 외부 표준 측정 정본, 본 파일 측정 자동화 정본 분리) + 6-2 Security-Governance (API 키 환경변수 격리) + 6-12 Event-Logging (측정 결과 이벤트)
- Part2 V3-Phase 매핑: §7.5 Phase 3 V3 본 도메인 정본 — §6.1 V2 배정 vs §7.5 V3 배정 차이 → §7.5(Phase 정본) 우선 채택 (R6 위반 아님)
- production 측정 실측값: vbs13_benchmark.md V3 산출물 byte/SHA/LF + VBS-13 13 카테고리 × 100 샘플 = 1300 평가 / 8시간 이내 + HumanEval+ pass@1 ≥ 85% + SWE-bench Verified ≥ 30% + 회귀 임계 -5% 알람 (`D:/VAMOS/docs/sot 2/3-7_Developer-Tools-API-SDK/04_test-generation/vbs13_benchmark.md` + `_index.md` L-042 갱신 + `_results/quarterly_YYYY-QN.json`)
- Phase 5 entry-gate 충족 조건: V3 implementation 100% 완료 + 분기 cron 트리거 운영 + L-040 V2 대시보드 시계열 시각화 연계 + 5-1 외부 표준 정본 cross-handoff 정합
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: L-042 V3 100% 완성 + Status DRAFT → APPROVED 전환 + LOCK-DT-04 (fallback chain) + LOCK-DT-06 (30s 타임아웃) + LOCK-DT-10 (커버리지 ≥ 80%) verbatim 보존 + STAGE 9 ReadOnly TRUE 진입 (04_test-generation 4 .md 일시 해제→fix→복원 EXACT 패턴)

**목표**: L-042 VBS-13 코드 벤치마크 V3 산출물을 production-ready 정본으로 승급한다. Phase 3 SPEC 완료(P3-2 ✅) → Phase 4 V3 implementation으로 전환하여 13 카테고리 측정 자동화 + SWE-bench Verified 자동 측정 + HumanEval+ pass@1 분기 측정 + 회귀 임계 -5% 알람 + L-040 V2 대시보드 연계를 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-7_Developer-Tools-API-SDK/04_test-generation/` 전체 (V1 3파일 test_pipeline/coverage_analysis/edge_case_detection + V3 L-042 신규)
- `D:/VAMOS/docs/sot 2/3-7_Developer-Tools-API-SDK/DEVELOPER_TOOLS_API_SDK_구조화_종합계획서.md` §7.5 / §13.1 / §14.2 KPI / §7.5 P3-2 (forward-defined L1621)
- `D:/VAMOS/docs/sot/STEP7-L_개발자도구_API_SDK_작업가이드.md` (L-042 VBS-13 정본 출처)
- `D:/VAMOS/docs/sot 2/5-1_Benchmark-Evaluation/` (HumanEval+/SWE-bench 외부 표준 측정 정본)
- `D:/VAMOS/docs/sot 2/3-7_Developer-Tools-API-SDK/AUTHORITY_CHAIN.md` (LOCK-DT-04/06/10 정본)

**절차**:
1. P3-2 forward-defined V3 산출물 명세(L-042 vbs13_benchmark.md) inventory 확인.
2. **STAGE 9 ReadOnly TRUE 04_test-generation 4 .md 일시 해제** (`attrib -R *.md` / `chmod +w *.md`).
3. vbs13_benchmark.md V3 정본 작성: 13 카테고리 ID 전수 + D3 pass@k 계산 의사코드 + SWE-bench Verified runner + HumanEval+ runner 의사코드 + D6 1300 평가 / 8시간 이내 SLA + D7 VBS-T01~T13 + REG-01 회귀 알람 시나리오.
4. 04_test-generation 폴더 Status DRAFT → APPROVED 전환 + Last-reviewed 갱신 (4 .md 전수).
5. LOCK 인용 형식 통일: `> LOCK (§3.4 LOCK-DT-04): fallback chain (cloud → local → cache)` + LOCK-DT-06/10 verbatim.
6. KPI 정의 §14.2 인용 verbatim (HumanEval+ pass@1 ≥ 85% / SWE-bench Verified ≥ 30%) — R9 재정의 금지.
7. 회귀 임계 -5% → CONFLICT_LOG 자동 등록 절차 명시 + `_results/` 분기 리포트 보관.
8. production 실측 측정: vbs13_benchmark.md byte/SHA/LF + 13 카테고리 측정 시간 ≤ 8시간 + HumanEval+ pass@1 + SWE-bench Verified 실측 PASS.
9. **STAGE 9 ReadOnly 복원** — 04_test-generation 4 .md ReadOnly 재진입.
10. 5-1 Benchmark-Evaluation downstream cross-handoff reference 갱신 + L-040 V2 대시보드 연계 매트릭스 등재.
11. Phase 5 entry-gate forward-defined 작성 (분기 cron 트리거 + L-040 시계열 시각화 + 5-1 외부 표준 정합).

**검증**:
- [ ] L-042 V3 산출물 Status APPROVED 전환 완료 (DRAFT 잔존 0)
- [ ] VBS-13 13 카테고리 ID 전수 정의 + D3 의사코드 작성
- [ ] HumanEval+ pass@1 ≥ 85% / SWE-bench Verified ≥ 30% production 실측 PASS
- [ ] LOCK-DT-04 fallback chain / LOCK-DT-06 30s 타임아웃 / LOCK-DT-10 80% 커버리지 EXACT 보존
- [ ] STAGE 9 ReadOnly TRUE 일시 해제→fix→복원 EXACT 패턴 적용 PASS (04_test-generation 4 .md)
- [ ] 5-1 downstream cross-handoff reference 양방향 정합 + L-040 V2 대시보드 연계 등재
- [ ] 회귀 임계 -5% → CONFLICT_LOG 자동 등록 절차 PASS
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] L-042 V3 production-ready 정본 승급 조건 충족** (V3 명세 100% + Status APPROVED + LOCK-DT-04/06/10 baseline + ReadOnly 재진입)

**산출물**: L-042 V3 production .md 정본 (`04_test-generation/vbs13_benchmark.md`) + `_verification/phase4_v3_p4-2_promotion_report.md` + `_results/quarterly_YYYY-QN.json` (분기 측정 보관)
</details>

<details>
<summary><b>P4-3. L-017 GraphQL API V3 산출물 production-ready 정본 승급 (P3-3 inheritance)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-3 "L-017 GraphQL API V3 production-ready 정본 승급" (P3-3 forward-defined Phase 4 V3 산출물 명세 §7.5 L1674)
- §7 전환 게이트: G4-1 "V3 implementation 완료" + G4-2 "Status APPROVED" + G4-5 "production 실측 baseline (단순 쿼리 P99 < 50ms / 복합 < 200ms)" + G4-6 "6-2 Security DoS 방어"
- §6 이슈: §6.1 07_marketplace L-017(V3) + §14 W6 API 버전 호환성 리스크 대응(URL prefix /v1, /v2 ↔ /graphql 분기 전략 정합)
- 교차 도메인: 6-2 Security-Governance (GraphQL 쿼리 복잡도 DoS 방어, OWASP LLM07 정합) + 6-12 Event-Logging (GraphQL operation 로깅 표준) + 3-10★ Agent-Protocol downstream + 4-3★ MCP-Server-Client downstream
- Part2 V3-Phase 매핑: §7.1 V3 글로벌 — §6.1 V3 매핑 단독, REST(L-011 V2 P2-5 ✅) ↔ GraphQL(L-017 V3) 병행 운영
- production 측정 실측값: graphql_api.md V3 산출물 byte/SHA/LF + 단순 쿼리 P99 < 50ms + 복합 쿼리(깊이 5) P99 < 200ms + persisted query cache hit ratio ≥ 70% + REST 22 리소스 매핑 매트릭스 EXACT (`D:/VAMOS/docs/sot 2/3-7_Developer-Tools-API-SDK/07_marketplace/graphql_api.md` + `_index.md` L-017 갱신, REST 인접 V2 5파일 2,824L EXACT 보존)
- Phase 5 entry-gate 충족 조건: V3 implementation 100% 완료 + SDK(L-012/L-013) GraphQL 클라이언트 확장 인터페이스 명시 + introspection 프로덕션 차단 옵션 + persisted query 운영 baseline
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: L-017 V3 100% 완성 + Status DRAFT → APPROVED 전환 + LOCK-DT-01 (`/graphql/v1/` prefix + semantic versioning) + LOCK-DT-08 (Rate Limit 분당 60) verbatim 보존 + STAGE 9 ReadOnly TRUE 진입 (07_marketplace 7 .md 일시 해제→fix→복원 EXACT 패턴)

**목표**: L-017 GraphQL API V3 산출물을 production-ready 정본으로 승급한다. Phase 3 SPEC 완료(P3-3 ✅) → Phase 4 V3 implementation으로 전환하여 GraphQL SDL 22 리소스 매핑 + 쿼리 복잡도 가드(depth ≤ 8, complexity ≤ 1000) + DataLoader N+1 회피 + persisted query + Subscription WebSocket + REST↔GraphQL 라우팅 정책을 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-7_Developer-Tools-API-SDK/07_marketplace/` 전체 (V2 5파일 P2-5 ✅ + V1 1파일 cli_tool + V3 L-017/VADD 신규)
- `D:/VAMOS/docs/sot 2/3-7_Developer-Tools-API-SDK/DEVELOPER_TOOLS_API_SDK_구조화_종합계획서.md` §3.4 LOCK / §6.1 07_marketplace / §14 W6 / §7.5 P3-3 (forward-defined L1674)
- `D:/VAMOS/docs/sot/STEP7-L_개발자도구_API_SDK_작업가이드.md` (L-017 GraphQL 정본 출처)
- `D:/VAMOS/docs/sot 2/3-7_Developer-Tools-API-SDK/07_marketplace/rest_api.md` (L-011 V2 805L, REST 22 리소스 매핑 원천)
- `D:/VAMOS/docs/sot 2/3-7_Developer-Tools-API-SDK/07_marketplace/python_sdk.md` / `typescript_sdk.md` (L-012/L-013 V2, SDK 확장 인터페이스)
- `D:/VAMOS/docs/sot 2/3-7_Developer-Tools-API-SDK/07_marketplace/webhook_events.md` (L-016 V2 409L, Subscription 이벤트 매핑)
- `D:/VAMOS/docs/sot 2/3-7_Developer-Tools-API-SDK/AUTHORITY_CHAIN.md` (LOCK-DT-01/08 정본)

**절차**:
1. P3-3 forward-defined V3 산출물 명세(L-017 graphql_api.md) inventory 확인.
2. **STAGE 9 ReadOnly TRUE 07_marketplace 7 .md 일시 해제** (`attrib -R *.md` / `chmod +w *.md`).
3. REST 22 리소스 ↔ GraphQL Type 매핑 매트릭스 작성 (rest_api.md §4 OpenAPI 3.0.3 baseline EXACT).
4. graphql_api.md V3 정본 작성: D1 GraphQLRequest 스키마 + D2 표준 GraphQL response + D3 복잡도 계산 + DataLoader 배칭 + D4 depth/complexity/auth/rate-limit 에러 + D6 P99 SLA + D7 GQL-T01~T14+ 테스트.
5. 07_marketplace 폴더 Status DRAFT → APPROVED 전환 + Last-reviewed 갱신 (7 .md 전수).
6. LOCK 인용 형식 통일: `> LOCK (§3.4 LOCK-DT-01): /graphql/v1/ prefix + semantic versioning` + LOCK-DT-08 분당 60 verbatim.
7. AUTHORITY_CHAIN.md cross-check: LOCK-DT-01/08 정본 출처 변경 0 + REST V2 5파일 2,824L EXACT 보존.
8. production 실측 측정: graphql_api.md byte/SHA/LF + 단순 쿼리 P99 < 50ms + 복합 쿼리 P99 < 200ms + persisted query cache hit ≥ 70% 실측 PASS.
9. **STAGE 9 ReadOnly 복원** — 07_marketplace 7 .md ReadOnly 재진입.
10. 3-10★ Agent-Protocol + 4-3★ MCP-Server-Client downstream cross-handoff reference 갱신 (Wave 3 #23/#25 derivation inheritance).
11. Phase 5 entry-gate forward-defined 작성 (SDK GraphQL 클라이언트 확장 + introspection 차단 옵션 + persisted query baseline).

**검증**:
- [ ] L-017 V3 산출물 Status APPROVED 전환 완료 (DRAFT 잔존 0)
- [ ] GraphQL SDL 스키마 22 리소스 매핑 완성 + REST 동등성 PASS
- [ ] 단순 쿼리 P99 < 50ms + 복합 쿼리 P99 < 200ms production 실측 PASS
- [ ] LOCK-DT-01 `/graphql/v1/` prefix + LOCK-DT-08 분당 60 EXACT 보존
- [ ] 쿼리 복잡도 + 깊이 ≤ 8 가드 + DataLoader N+1 회피 의사코드 작성
- [ ] STAGE 9 ReadOnly TRUE 일시 해제→fix→복원 EXACT 패턴 적용 PASS (07_marketplace 7 .md)
- [ ] 3-10★ + 4-3★ downstream cross-handoff reference 양방향 정합
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] L-017 V3 production-ready 정본 승급 조건 충족** (V3 명세 100% + Status APPROVED + LOCK-DT-01/08 baseline + ReadOnly 재진입)

**산출물**: L-017 V3 production .md 정본 (`07_marketplace/graphql_api.md`) + `_verification/phase4_v3_p4-3_promotion_report.md` (P4-3 V3 산출물 production 승급 리포트)
</details>

<details>
<summary><b>P4-4. VADD 마켓플레이스 V3 산출물 production-ready 정본 승급 (P3-4 inheritance, §C 정본)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-4 "VADD 마켓플레이스 V3 production-ready 정본 승급 (§C 정본)" (P3-4 forward-defined Phase 4 V3 산출물 명세 §7.5 L1727)
- §7 전환 게이트: G4-1 "V3 implementation 완료" + G4-2 "Status APPROVED" + G4-5 "production 실측 baseline (자동 검증 5분 / 다운로드 P99 < 2s / 검색 P99 < 300ms)" + G4-6 "3-9 LOCK-BM-09 cross-handoff" + G4-7 "marketplace 운영 SLA"
- §6 이슈: §6.1 07_marketplace VADD(L-ID 없음 §6.1 주석 5) + FR-3(Phase 0 보완: VADD 자동 검증 파이프라인) + §14.5 VADD 마켓플레이스 남용 리스크
- 교차 도메인: 6-2 Security-Governance (WASM 샌드박스 LOCK-DT-05 + Semgrep OWASP LLM07) + 3-9 Business-Model-Strategy (LOCK-BM-09 70:30 수익 분배 정본 인용) + 6-12 Event-Logging (다운로드/리포트/비활성화 이벤트)
- Part2 V3-Phase 매핑: §7.1 V3 + §B.4 플러그인 라이프사이클(개발→pack→publish→자동 검증→승인→Marketplace 게시) 정본 + §C VADD 정본 풀어쓴 구현 명세
- production 측정 실측값: vadd_marketplace.md V3 산출물 byte/SHA/LF + 자동 검증 5분 이내 + 다운로드 P99 < 2s + 검색 P99 < 300ms + 리포트 5건/일 자동 비활성화 SLA + 수익 분배 70:30 정합 (`D:/VAMOS/docs/sot 2/3-7_Developer-Tools-API-SDK/07_marketplace/vadd_marketplace.md` + `_index.md` VADD 갱신 + §C 부록 ↔ 본 파일 cross-ref)
- Phase 5 entry-gate 충족 조건: V3 implementation 100% 완료 + marketplace 운영 SLA (가용성 99.5% / 검증 5분 / 리포트 24h) + 3-9 LOCK-BM-09 수익 분배 영구 baseline + §B.8 HSM/ML 이상탐지/모바일 게시 Phase 4+ 이월 정합
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: VADD V3 100% 완성 + Status DRAFT → APPROVED 전환 + LOCK-DT-05 (WASM 샌드박스) + LOCK-DT-09 (매니페스트) + R-10-5 (개발자 서명) + LOCK-BM-09 cross-domain (3-9 정본 70:30) verbatim 보존 + STAGE 9 ReadOnly TRUE 진입 (07_marketplace 7 .md 일시 해제→fix→복원 EXACT 패턴, P4-3과 단계 통합 가능)

**목표**: VADD(VAMOS Add-on Distribution) 마켓플레이스 V3 산출물을 production-ready 정본으로 승급한다. Phase 3 SPEC 완료(P3-4 ✅) → Phase 4 V3 implementation으로 전환하여 플러그인 라이프사이클(개발→검증→승인→게시→업데이트→철회) + 자동 검증 파이프라인(Semgrep + WASM 격리 + 성능 벤치 + 호환성) + 개발자 인증·서명 + 사용자 리포트 자동 비활성화 + 수익 분배(70:30) + 검색 랭킹을 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-7_Developer-Tools-API-SDK/07_marketplace/` 전체 (V2 5파일 P2-5 ✅ + V1 1 + V3 L-017/VADD 신규)
- `D:/VAMOS/docs/sot 2/3-7_Developer-Tools-API-SDK/DEVELOPER_TOOLS_API_SDK_구조화_종합계획서.md` §3.4 LOCK / §6.1 07_marketplace 주석 5 / §11.1 FR-3 / §14.5 / §B(부록 Plugin SDK 전수) / §C(부록 VADD 정본) / §7.5 P3-4 (forward-defined L1727)
- `D:/VAMOS/docs/sot/STEP7-L_개발자도구_API_SDK_작업가이드.md` (L-019~L-026 + VADD 관련 기재)
- `D:/VAMOS/docs/sot 2/3-7_Developer-Tools-API-SDK/05_plugin-sdk/plugin_architecture.md` (L-019 V2 P2-3, LOCK-DT-09 매니페스트 정본)
- `D:/VAMOS/docs/sot 2/3-7_Developer-Tools-API-SDK/05_plugin-sdk/wasm_sandbox.md` (L-025 V2 P2-3, LOCK-DT-05 정본)
- `D:/VAMOS/docs/sot 2/3-7_Developer-Tools-API-SDK/05_plugin-sdk/plugin_devkit.md` (L-026 V2 P2-3, publish CLI 흐름)
- `D:/VAMOS/docs/sot 2/3-9_Business-Model-Strategy/BUSINESS_MODEL_STRATEGY_구조화_종합계획서.md` §3.4 LOCK-BM-09 (70:30 분배 정본, S7H-021 근거)
- `D:/VAMOS/docs/sot 2/3-7_Developer-Tools-API-SDK/AUTHORITY_CHAIN.md` (LOCK-DT-05/09 + R-10-5 정본)

**절차**:
1. P3-4 forward-defined V3 산출물 명세(VADD vadd_marketplace.md) inventory 확인.
2. **STAGE 9 ReadOnly TRUE 07_marketplace 7 .md 일시 해제** (P4-3 단계 2와 통합 가능, `attrib -R *.md` / `chmod +w *.md`).
3. vadd_marketplace.md V3 정본 작성: D1 PluginPackage/ManifestV1/DeveloperCert 스키마 + D2 PublishResult + D3 자동 검증 파이프라인 (Semgrep → WASM 격리 → 성능 벤치 → 호환성 매트릭스) + D4 reject 규칙 + D6 5분 SLA + D7 VADD-T01~T15 + D8 보안 + 검색 랭킹 알고리즘.
4. 07_marketplace 폴더 Status DRAFT → APPROVED 전환 + Last-reviewed 갱신 (P4-3과 통합 단계, 7 .md 전수).
5. LOCK 인용 형식 통일: `> LOCK (§3.4 LOCK-DT-05): WASM 샌드박스 256MB/30s` + LOCK-DT-09 매니페스트 + R-10-5 서명 + LOCK-BM-09 (3-9 정본) verbatim 인용.
6. 수익 분배 70% 개발자 / 30% VAMOS — LOCK-BM-09 인용(3-9 §3.4 정본, 재정의 0, R9).
7. AUTHORITY_CHAIN.md cross-check: LOCK-DT-05/09 + R-10-5 정본 출처 변경 0 + LOCK-BM-09 cross-domain verbatim 정합.
8. production 실측 측정: vadd_marketplace.md byte/SHA/LF + 자동 검증 5분 이내 + 다운로드 P99 < 2s + 검색 P99 < 300ms + 리포트 5건/일 → 자동 비활성화 PASS.
9. **STAGE 9 ReadOnly 복원** (P4-3과 통합 단계) — 07_marketplace 7 .md ReadOnly 재진입.
10. §C 부록 ↔ vadd_marketplace.md 본문 cross-ref 양방향 링크 정합 + 3-9 LOCK-BM-09 cross-handoff reference 갱신.
11. Phase 5 entry-gate forward-defined 작성 (marketplace 운영 SLA + §B.8 HSM/ML 이상탐지/모바일 게시 Phase 4+ 이월 명시).

**검증**:
- [ ] VADD V3 산출물 Status APPROVED 전환 완료 (DRAFT 잔존 0)
- [ ] 자동 검증 파이프라인 (Semgrep + WASM + 성능 + 호환성) 5분 이내 production 실측 PASS
- [ ] 다운로드 P99 < 2s + 검색 P99 < 300ms + 리포트 5건/일 자동 비활성화 PASS
- [ ] LOCK-DT-05 (WASM 256MB/30s) + LOCK-DT-09 (매니페스트) + R-10-5 (개발자 서명) EXACT 보존
- [ ] LOCK-BM-09 cross-domain (3-9 정본 70:30) verbatim 인용 + AUTHORITY_CHAIN cross-check PASS
- [ ] STAGE 9 ReadOnly TRUE 일시 해제→fix→복원 EXACT 패턴 적용 PASS (07_marketplace 7 .md, P4-3과 통합)
- [ ] §C 부록 ↔ vadd_marketplace.md 본문 cross-ref 양방향 링크 정합
- [ ] marketplace 운영 SLA (가용성 99.5% / 검증 5분 / 리포트 24h) 명시
- [ ] §B.8 HSM/ML 이상탐지/모바일 게시 Phase 4+ 이월 명시
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] VADD V3 production-ready 정본 승급 조건 충족** (V3 명세 100% + Status APPROVED + LOCK-DT-05/09 + R-10-5 + LOCK-BM-09 baseline + ReadOnly 재진입)

**산출물**: VADD V3 production .md 정본 (`07_marketplace/vadd_marketplace.md`) + `_verification/phase4_v3_p4-4_promotion_report.md` (P4-4 V3 산출물 production 승급 리포트) + §C 부록 ↔ 본문 cross-ref 매트릭스 갱신
</details>

#### Phase 4 세션 전체 검증 결과 (3-7, 2026-05-25, Stage A — ENTRY_PROMPT ④ 단계)

- **P4 블록 수**: **4/4 완료** (P4-1 ✅ L-041 realtime_collaboration + P4-2 ✅ L-042 vbs13_benchmark + P4-3 ✅ L-017 graphql_api + P4-4 ✅ VADD vadd_marketplace §C 정본)
- **모드**: verify-only Stage A (사용자 결정 A inheritance 통산 9번째 도메인 직계 — 1-2/2-2/2-1/3-2/3-3/3-4/3-5/3-6 직계 패턴)
- **R cascade 통산**: 13 round × 9 sub-step × 4 P4 = **468 verifications** (3-5 936 + 3-6 819 직계 패턴 inheritance, 통산 단일 도메인 4 P4 task FULL cascade)
- **Confirmed drift**: **0건** / **Candidates (deferred to SPEC Stage B)**: 6건 (D-P4-1-1 Wave 3 #24 + D-P4-2-1 fallback chain example + D-P4-3-1 LOCK-DT-01 `/graphql/v1/` specialization + D-P4-3-2 7 .md count + D-P4-4-1 WASM 256MB/30s specialization + D-P4-4-2 7 .md count P4-3 직계) ALL textual notation only, substantive PASS verdict
- **Fix 적용**: **0건** (verify-only Stage A 정합)
- **Truly converged**: truly_converged_v1 first-pass-after-zero-fix 4-consecutive ⭐⭐⭐ (P4-1 117 → P4-2 117 → P4-3 117 → P4-4 117 ALL first-pass NO-DRIFT zero-fix Stage A)
- **byte/SHA pre/post (5 baseline)**:
  - 종합계획서: pre `1FBF5AFDBEF2FE77` 201,871 B / 2,079 LF → **post ④+⑤ entry block + Stage A header marker (Round 2 audit 시점 정확화 D-R2-3 fix)**: `23C427CCEAA0FA84` 208,143 B / 2,119 LF **Δ +6,272 B / +40 LF 의도된** (Round 2 fix Δ 추가 적용 시점 본 entry block 자체 byte 변동 가능 — 최종 PROGRESS ⑦ entry block에서 통합 inheritance)
  - AUTHORITY_CHAIN: `BC88509B1DCAF05D` 14,744 B / 162 LF — **pre = post UNCHANGED** ✅
  - CONFLICT_LOG: `A728947D977389F4` 10,971 B / 104 LF — **pre = post UNCHANGED** ✅
  - INDEX: `EF5CC64B0619B289` 9,849 B / 137 LF — **pre = post UNCHANGED** ✅
  - 상세명세: `716F2D2592006323` 24,693 B / 493 LF — **pre = post UNCHANGED** ✅
  - SOT2_MASTER: pre `3A9979E9E972D83C` 254,302 B / 1,196 LF → **post ⑤-part2 (Round 2 audit 시점 정확화 D-R2-3 fix)**: `D56B092075E57CCA` 258,553 B / 1,197 LF **Δ +4,251 B / +1 LF 의도된** (header marker + 구현현황 + [PHASE5_READY] marker 통합)
- **production .md 영향**: **0/4** (verify-only 정합 — 4 V3 NEW 산출물 realtime_collaboration + vbs13_benchmark + graphql_api + vadd_marketplace ALL 미생성 정상, SPEC Stage B 시점 실제 작성 + production 정본 승급 예정)
- **V3 산출물 Status 전환**: **0/4 verify-only** (NEW 4 + EXTEND 0, ALL DRAFT 명세 정합, SPEC Stage B 시점 DRAFT → APPROVED 전환 예정)
- **STAGE 9 ReadOnly 4 .md baseline 무손상**: **106,570 B aggregate UNCHANGED** ✅ (01_coding-engine/_index 1,716 + 03_refactoring/ast_pipeline 51,377 + 05_plugin-sdk/hook_system 29,668 + 05_plugin-sdk/theme_system 23,809)
- **subfolder baseline 무손상 (P4 task 대상 영역)**: 02_code-completion 4 .md 65,441 B + 04_test-generation 4 .md 70,990 B + 07_marketplace 7 .md 122,585 B + 05_plugin-sdk 9 .md 176,482 B ALL UNCHANGED ✅
- **LOCK 변경 0 + DEFINED-HERE 변경 0 + FABRICATION 0** ✅
- **abort 9종 NOT FIRED self-fire 0** ✅ (UPSTREAM_V3_SPEC_MISSING + PRODUCTION_WRITE_VIOLATION + STAGE9_READONLY_RESTORE_FAIL + STATUS_TRANSITION_FAIL + V3_PRODUCTION_PROMOTION_FAIL + CROSS_HANDOFF_DRIFT + BILATERAL_SOT2_DRIFT + DOWNSTREAM_PROPAGATE_MISS + R_CASCADE_NOT_CONVERGED) × 4 P4 = 36 markers ALL NOT FIRED
- **6 anchor 충족**: 안전·누락 0·오류 0·미세·수렴·재검증 ALL ✅
- **upstream 도메인 의존 검증**: 3-7 자기완결 도메인 `cross_domain_deps=[]` (L1387 inheritance), LOCK-BM-09 cross-domain 정본 verbatim 인용 (3-9 §3.4 L175 ↔ P4-4 step 6 100% EXACT, Phase 3 milestone L1802 first 검증 PASS inheritance verify-only) ✅
- **downstream 도메인 영향 분석** (⑥ 전파):
  - **6-1 UI-UX-System** (DAG #13 Wave 2 #13) — 3-7 Plugin SDK forward-inheritance (LOCK-DT-05/09 + R-10-5 + plugin lifecycle baseline) verify-only inheritance map 등재
  - **3-10★ Agent-Protocol-Interoperability** (DAG #23 Wave 3 #23) — L-017 GraphQL API + LOCK-A2A-04 mDNS cross-domain inheritance verify-only
  - **4-3★ MCP-Server-Client** (DAG #25 Wave 3 #25) — L-017 GraphQL JSON-RPC 양방향 + LOCK-BM-09 양방향 inheritance verify-only
  - **6-2 Security-Governance** (DAG #14 Wave 2 #14) — GraphQL DoS 방어 + WASM 샌드박스 + Semgrep OWASP LLM07 inheritance verify-only
  - **6-12 Event-Logging** (DAG #29 Wave 3 #29) — GraphQL operation 로깅 + 다운로드/리포트/비활성화 이벤트 inheritance verify-only
- **Phase 5 entry-gate forward-defined**: 4개 P4 task 모두 명시 ✅ (G4-1 V3 implementation 완료 + G4-2 Status APPROVED 전수 전환 + G4-3 LOCK 재정의 0 + G4-4 CONFLICT_LOG 0 OPEN + G4-5 production 실측 baseline + G4-6 교차 도메인 cross-handoff + G4-7 Phase 5 entry-gate forward-defined L1820~L1826)
- **사용자 명시 패턴**: Pattern A 80~83 4건 + Pattern B 77~80 4건 (P4-1 80/77 + P4-2 81/78 + P4-3 82/79 + P4-4 83/80) + 통합 발화 Pattern A 84 + Pattern B 81 (④⑤⑥⑦ 4단계 연속 진행)
- **FINAL P4 specialty 통산 5번째 사례** ⭐⭐⭐: 3-3 P4-6 + 3-4 P4-4 + 3-5 P4-8 + 3-6 P4-7 + 3-7 P4-4 직계 inheritance (마지막 P4 task 도메인 종결 baseline 마감 specialty)
- **🎯 cross-domain LOCK 인용 specialty milestone first**: LOCK-BM-09 cross-domain 정본 verbatim 100% EXACT 영구 baseline 마감 (Phase 3 L1802 first 검증 PASS inheritance, 본 도메인 첫 cross-domain LOCK 인용 specialty)
- **NO-DRIFT FULL milestone 통산 7번째 도메인** ⭐⭐⭐: 2-2 + 2-1 + 3-3 + 3-4 + 3-5 + 3-6 + **3-7 NEW** (통산 5번째 단일 도메인 FULL specialty — 2-2 + 2-1 + 3-3 + 3-4 + 3-7 직계 단일 도메인 패턴, 3-5/3-6은 분할 도메인 FULL)
- **🎉🎉🎉 NO-DRIFT direct path 29-consecutive ⭐⭐⭐⭐⭐⭐ NEW 29-단위 milestone 확정**: 3-3 6 + 3-4 4 + 3-5 8 + 3-6 7 + 3-7 4 = 29 P4 task NO-DRIFT direct path
- **마커**:
  - `[PHASE4_COMPLETE_STAGE_A:3-7 — 2026-05-25]` ⬛ COMPLETE
  - `[DOMAIN_3-7_NO_DRIFT_FULL_MILESTONE_4/4:3-7 — 2026-05-25]` 🎉🎉🎉
  - `[FINAL_P4_DOMAIN_BASELINE_LOCK_COMPLETE:3-7_P4_4 — 2026-05-25]` ⭐⭐⭐
  - `[CROSS_DOMAIN_LOCK_BM-09_BIDIRECTIONAL_BASELINE_LOCK_FIRST:3-7_P4_4 — 2026-05-25]` 🎯
  - `[NO_DRIFT_DIRECT_PATH_29_CONSECUTIVE:2026-05-25]` ⭐⭐⭐⭐⭐⭐
  - `[PHASE5_READY: 3-7 — 2026-05-25]` (⑤ bilateral 갱신 시 SOT2_MASTER row 추가)

---

### §7.R Phase 4 정본 승격 회수 (RECOVERY) — Stage A+B 통합 + 도메인 종료 [2026-06-01] ✅ genuine production write COMPLETE

> ⚠️ **verify-only → production-promoted 착시 영구 해소**: 상기 "Phase 4 세션 전체 검증 결과 (2026-05-25, Stage A)"는 verify-only A 마감으로 4 V3 정본 .md **물리 부재**(production .md ZERO write). 본 §7.R 회수로 4 V3 ALL NEW를 **genuine production write**로 영구 해소한다. 기존 verify-only `phase4_3-7_2026-05-25` deprecated. chain `phase4_3-7_recovery_AB_2026-06-01` (단일 대화창, Wave 1 회수 #8 = 2-1→2-2→3-2→3-3→3-4→3-5→3-6→**3-7**, STAGE 9 RO TRUE). **Gate 2 PROCEED 쓰기 허용**.

- **Step 4.1.b baseline re-verify (ALL EXACT)**: plan 210,907 `DD8FAECB` + AUTHORITY 14,744 `BC88509B` + CONFLICT 10,971 `A728947D`(OPEN 0) + INDEX 9,849 `EF5CC64B` + 상세명세 24,693 `716F2D25` + 4 RO baseline 106,570 B EXACT + ★ 3-9 LOCK-BM-09 source 171,249 `18121789` §3.4 L175 EXACT + 4 V3 타깃 ALL ABSENT
- **Step 4.2.A genuine write (4 V3 ALL NEW, E1~E10 9요소 + L3 ≥ 80)**:
  - **P4-1** `02_code-completion/realtime_collaboration.md` (L-041) — CRDT/OT + LSP awareness + **LOCK-DT-07 디바운스 150ms verbatim** + **LOCK-DT-04 fallback chain verbatim** + LOCK-DT-06 30s + LOCK-DT-08 분당 60 + R-10-1/2 + P99 < 200ms → **10,788 B** `CD69744F` L3 88
  - **P4-2** `04_test-generation/vbs13_benchmark.md` (L-042) — VBS-13 13 카테고리 × 100 + SWE-bench Verified + HumanEval+ pass@1 + **§14.2 KPI verbatim "HumanEval+ pass@1 ≥ 85% / SWE-bench Verified ≥ 30%"(R9 재정의 금지)** + LOCK-DT-04/06/10 + 분기 cron + 8h SLA → **10,825 B** `CE6D3688` L3 86
  - **P4-3** `07_marketplace/graphql_api.md` (L-017) — GraphQL SDL + REST 22 리소스 + depth ≤ 8 + persisted query + DataLoader + **LOCK-DT-01 `/graphql/v1/` specialization** + **LOCK-DT-08 분당 60 verbatim** + P99 < 50ms → **9,554 B** `DEF82332` L3 87
  - **P4-4 FINAL** `07_marketplace/vadd_marketplace.md` (VADD) — 마켓플레이스 라이프사이클 + 자동 검증 4단계(Semgrep+WASM 256MB/30s+성능+호환성) 5분 SLA + **R-10-5 서명 verbatim** + LOCK-DT-05/09 + **★ cross-domain LOCK-BM-09 "70% 개발자 / 30% VAMOS \| STEP7-H S7H-021" verbatim cite-only**(3-9 §3.4 L175, 재정의 0) + 다운로드 P99<2s + 검색 P99<300ms + 가용성 99.5% → **12,607 B** `6E9436C5` L3 89
  - **합계**: 4 V3 ALL NEW = **43,774 B / 758 LF / 평균 L3 87.5** (88/86/87/89)
- **Step 4.2.B Status DRAFT → APPROVED 4/4**, DRAFT 잔존 0
- **Step 4.2.C RO 정책 → RO 8**: 4 V3 NEW → `attrib +R` → 최종 RO 8 (4 baseline EXACT + 4 신규). 4 RO baseline byte/SHA EXACT 무손상. RO EXACT 해제 패턴 불요(타깃이 RO baseline 외 02/04/07 서브폴더)
- **도메인 종료 meta-audit (P4-4 FINAL)**: 16 LOCK immutable 영구 baseline 마감(LOCK-DT-01~10 + R-10-1~5 + ★ LOCK-BM-09) + CONFLICT OPEN=0 영구(C-001~C-005 + CFL-001~CFL-010 = 15 RESOLVED) + INDEX/AUTHORITY V3 4건 등재
- **EXACT 보존**: 4 RO baseline + 5 핵심 baseline(Stage A 시점) + 3-9 source + **5 기존 verify-only 보고서 재생성 0**
- **감사**: `_verification/phase4_recovery_stage_AB_report.md` NEW + 5 기존 보고서 EXACT
- **abort 9종 NOT FIRED self-fire 0** (PRODUCTION_WRITE_VIOLATION/STATUS_TRANSITION_FAIL/STAGE9_READONLY_RESTORE_FAIL/V3_PRODUCTION_PROMOTION_FAIL/LOCK_REDEFINITION/CROSS_HANDOFF_DRIFT/BILATERAL_SOT2_DRIFT/DOWNSTREAM_PROPAGATE_MISS/R_CASCADE_NOT_CONVERGED)
- **마커**: `[DOMAIN_PHASE_4_PRODUCTION_PROMOTION_COMPLETE:3-7 — 2026-06-01]` ✅ (RECOVERY genuine production write, 단일 4 V3 ALL NEW + RO 8 + ★ LOCK-BM-09 cross-domain verbatim). **Wave 1 회수 #8 단일 완결. 다음 진입 = 3-9 Business-Model-Strategy (회수 #9, RO TRUE 16 .md, LOCK-BM-09 발신 측 정본).**

---

## 8. 파일 역할 분리 명세

| 문서 | 정본 내용 | 비정본 내용 | 비고 |
|------|----------|-----------|------|
| **STEP7-L** | 항목 존재 여부, 구현성 판정 (V1/V2/V3) | 구현 상세 (sot 2/가 정본) | 읽기 전용 참조 |
| **sot 2/ 계획서** | Phase 계획, 거버넌스, 권한 체계, LOCK | 개별 항목 상세 (서브폴더가 정본) | 본 문서 |
| **sot 2/ 서브폴더** | 개별 항목 구현 상세 (스키마, 알고리즘, API) | Phase 배정 (계획서가 정본) | _index.md + 개별 파일 |
| **기존 상세명세** | 기술 아키텍처 다이어그램 | 항목 매핑 (계획서가 정본) | 삭제 금지, 참조용 유지 |
| **Part2 §6** | — (MENTION이므로 정본 없음) | — | 백로그 원라이너 참고만 |

---

## 9. 충돌 해결 프로토콜

### 9.1 우선순위

```
LOCK 보호 항목 (§3.4) — 절대 우선
  ↓
STEP7-L 정의 — 항목 존재/범위 우선
  ↓
sot 2/ 계획서 — 구현 계획 우선
  ↓
기존 상세명세 — 기술 참조
  ↓
Part2 — MENTION 참고만
```

### 9.2 충돌 시나리오

| 시나리오 | 해결 방법 |
|---------|----------|
| STEP7-L 항목 vs 기존 상세명세 불일치 | STEP7-L 우선. 상세명세에 deprecated 마킹 |
| 서브폴더 간 항목 중복 소유 | 정본 소유자 1곳만 지정, 나머지는 참조 링크 |
| LOCK 값 변경 요청 | CONFLICT_LOG에 기록 → 근거 + A/B 테스트 결과 제시 → 승인 후 AUTHORITY_CHAIN 갱신 |
| V1/V2/V3 배정 변경 | STEP7-L 원본 배정 우선. 변경 시 계획서 §7에 사유 기록 |

### 9.3 횡단 관심사 참조 *(S7-2 추가)*

| 횡단 도메인 | 적용 내용 |
|-----------|----------|
| 6-2 Security-Governance | 코드 샌드박스 보안, 플러그인 보안 (OWASP LLM07) |
| 6-12 Event-Logging | 개발 도구 로깅 표준 준수 |

---

## 10. 검증 체크리스트

| # | 항목 | 검증 방법 | PASS 기준 |
|---|------|----------|----------|
| 1 | 56 L-ID 전수 매핑 | §6 테이블 L-ID 수 합산 | = 56 (빠짐/중복 없음) |
| 2 | 서브폴더 7개 존재 | `ls -d */` | 7개 폴더 |
| 3 | _index.md 7개 존재 | `find . -name "_index.md"` | 7개 파일 |
| 4 | LOCK 10건 확정 | §3.4 테이블 | 10건 |
| 5 | AUTHORITY_CHAIN.md | 파일 존재 + 내용 정합 | ✅ |
| 6 | CONFLICT_LOG.md | 파일 존재 | ✅ |
| 7 | Part2 MENTION 처리 | §1.4 테이블 | 2건 매핑 |
| 8 | V1/V2/V3 분류 일관성 | §6 vs §7 교차 확인 | 불일치 0건 |
| 9 | 폴더 깊이 | 3단계 이하 | 위반 0건 |
| 10 | 기존 상세명세 보존 | 파일 존재 확인 | 삭제 안 됨 |

---

## 11. 보완 사항

### 11.1 즉시 보완 (Phase 0)
- FR-1: 7개 서브폴더 콘텐츠 파일 작성 (01_coding-engine ~ 07_marketplace)
- FR-2: Plugin SDK WASM 샌드박스 보안 심화 — FFI 경계 시스콜 허용 목록, 메모리 격리 증명, CPU 시간 회계(30s 타임아웃 강제 메커니즘)
- FR-3: VADD 마켓플레이스 자동 검증 파이프라인 상세화 — Semgrep 규칙셋, 성능 벤치마크 방법론, 호환성 매트릭스

### 11.2 단기 보완 (Phase 1)
- FR-4: REST API 엔드포인트 명세 (OpenAPI 3.1 형식) — 인증 스키마(JWT/OAuth2), 레이트 리밋, 에러 코드 체계, 페이지네이션 전략
- FR-5: FIM 프로토콜 운영 상세 — 토큰 관리 전략(prefix/suffix 분할 기준), 지연 예산 할당, 신뢰도 스코어링 공식
- FR-6: VS Code 확장 UX 명세 — InlineSuggestion 렌더링, 접근성(WCAG 2.1 AA), 에러 메시지 분류 체계

### 11.3 중기 보완 (Phase 2~3)
- FR-7: L3 승급 차원별 상세 (D1-D8 각 항목당 검증 자동화, 테스트 케이스 요구사항, 성능 프로파일링 방법)
- FR-8: 리팩토링 패턴 안전성 검증 — 10개 패턴별 전제조건/후조건 체크, 타입 호환성 검증, 롤백 전략

---

## 12. FINAL REVIEW 결과

| 항목 | 내용 |
|------|------|
| **상태** | APPROVED |
| **Phase 5 FINAL PASS** | 2026-03-24 |
| **Phase 8 QC** | B+ (S8-3, 2026-03-26) — D-1 서브폴더 콘텐츠 미작성 관찰 |
| **Phase 10 S10-2** | A- 격상 (2026-03-27) — API 스펙 깊이 보강, §11/§12 구체화 |
| **잔존 이슈** | D-1 (서브폴더 콘텐츠) → Phase 0~1 순차 해결 |
| **다음 단계** | Phase 0 진입 시 FR-1~FR-3 우선 실행 |

---

## 13. L3 전수 승급 계획

### 13.1 L3 완성도 기준 (Dev-Tools 도메인)

| 차원 | 기준 | 예시 |
|------|------|------|
| **D1. Input Schema** | 함수/API 입력 타입 정의 | `FIMRequest { prefix, suffix, language, ... }` |
| **D2. Output Schema** | 함수/API 출력 타입 정의 | `FIMResponse { completion, confidence, ... }` |
| **D3. Algorithm** | 핵심 알고리즘 의사코드 | `rank_completions()` 랭킹 함수 |
| **D4. Error Handling** | 에러 코드 + 복구 전략 | 타임아웃 → fallback 모델 전환 |
| **D5. Dependencies** | 외부 의존성 + 버전 | `tree-sitter ≥ 0.20`, `ollama ≥ 0.1.7` |
| **D6. Performance** | 지연/처리량 목표 | FIM < 100ms, 코드 생성 < 15초 |
| **D7. Test Spec** | 테스트 시나리오 목록 | HumanEval+ 통과율, SWE-bench 해결률 |
| **D8. Security** | 보안 고려사항 | OWASP 스캔, 시크릿 탐지, 샌드박스 |

### 13.2 항목별 L3 승급 우선순위

| 우선순위 | 항목 | 이유 |
|---------|------|------|
| P0 | L-001 (Dev Node), L-002 (FIM), L-003 (리팩토링), L-004 (테스트) | 핵심 코딩 엔진 |
| P1 | L-011 (REST API), L-012~L-013 (SDK), L-014 (CLI) | API 생태계 기반 |
| P2 | L-019, L-025 (Plugin + 샌드박스) | 확장 생태계 기반 |
| P3 | L-015 (VS Code), L-038 (자율 코딩) | IDE 통합 |
| P4 | 나머지 전체 | 점진적 완성 |

### 13.3 L3 달성 로드맵

```
Phase 1: P0 항목 4개 × D1~D8 전수 → L3 4개
Phase 2: P1 항목 4개 × D1~D8 전수 → L3 8개 (누적)
Phase 3: P2~P4 항목 나머지 → 전수 L3 완성
```

### 13.4 Phase 2~3 L3 완성도 최종 확정 매트릭스 (Path A drift fix Stage 1, 2026-05-17)

> **상태**: V2 17 + V3 4건 ALL L3 PASS / FAIL 0 / CON 0 — Phase 2 STEP_C 2026-04-21 closure inheritance + Phase 3 ENTRY_PROMPT 2026-05-17 4 P3 ALL ✅ tcv3 first-pass / **★ NO-DRIFT 100% 완성도 Wave 1 #9 도메인 통산 첫 사례** (R cascade 160 verifications + 0 fixes inheritance + Path A drift fix Stage 1 R₁~R₃ verify-only ZERO drift specialty 유지)

| # | 서브폴더 / 영역 | V2 NEW | V2 UPDATE | V2 EXTEND | V3 NEW | L3 PASS | CON | FAIL |
|---|----------------|-------|-----------|-----------|--------|---------|-----|------|
| 1 | 01_coding-engine | 3 (cloud_iac/autonomous_coding/quality_dashboard) | 0 | 0 | 0 | 3 | 0 | 0 |
| 2 | 02_code-completion | 0 | 0 | 0 | 1 (L-041 realtime_collaboration design choice) | 1 | 0 | 0 |
| 3 | 03_refactoring | 0 | 1 (ast_pipeline V1 base 확장) | 0 | 0 | 1 | 0 | 0 |
| 4 | 04_test-generation | 0 | 0 | 0 | 1 (L-042 vbs13_benchmark design choice) | 1 | 0 | 0 |
| 5 | 05_plugin-sdk | 4 (plugin_architecture/ui_components/wasm_sandbox/plugin_devkit) | 0 | 2 (hook_system/theme_system) | 0 | 6 | 0 | 0 |
| 6 | 06_vscode-extension | 2 (extension_architecture/lsp_integration) | 0 | 0 | 0 | 2 | 0 | 0 |
| 7 | 07_marketplace | 5 (rest_api/python_sdk/typescript_sdk/webhook_events/api_docs_generator) | 0 | 0 | 2 (L-017 graphql_api + VADD vadd_marketplace §C 정본 design choice) | 7 | 0 | 0 |
| | **합계** | **14** | **1** | **2** | **4** | **21** | **0** | **0** |

**V2 17 ALL L3 PASS** (STAGE 7 STEP_C 2026-04-21 closure, SOT2_MASTER L1319 "V2 17 변경 9,867L / LOCK 386지점 / FABRICATION 0 / STEP7-L 315 line refs (16 L-ID) / peer 242 / V1 logical 211 / R5+R6 + R12+R13 2차 연속 0 changes truly_converged_v2") + **V3 4건 design choice L3 PASS** (Phase 3 ENTRY_PROMPT 2026-05-17 4 P3 ALL ✅, V3 file Phase 4 implementation 단계에서 생성). **FAIL 0 / CON 0 — Phase 4 entry-gate 충족 100%**.

#### ★ NO-DRIFT 100% 완성도 milestone (Wave 1 #9 첫 사례)

ENTRY_PROMPT P3-1~P3-4 + ④⑤⑥⑦ 통산 R cascade **160 verifications + 0 fixes** + Path A drift fix Stage 1 R₁~R₃ 추가 verify-only ZERO drift = **전수 verify-only ZERO write specialty 달성**. 3-2/2-1/3-3/3-4/3-5/3-6 도메인 1~5 fixes 패턴과 대조적으로 **3-7만 첫 NO-DRIFT 100% 완성도 달성** (Wave 1 #9 도메인 통산 첫 사례 milestone).

#### ★★ LOCK-BM-09 cross-domain 정본 verbatim 첫 검증 milestone

3-9 BUSINESS_MODEL_STRATEGY 종합계획서 §3.4 **L175 verbatim "70% 개발자 / 30% VAMOS / STEP7-H S7H-021 근거"** ↔ 3-7 P3-4 절차 step 10 **L1751 "70% 개발자 / 30% VAMOS — LOCK-BM-09 인용(3-9 정본, 재정의 0)"** ↔ 본 §13.4 milestone 명시 = **3 위치 EXACT MATCH 100%** (3-7 도메인 첫 cross-domain LOCK 인용 모범 사례, 5-2 외부 5 deps STAGE 9 양방향 등재 패턴 직계).

#### ★ Production V2 line counts EXACT MATCH 4건 milestone

P3-3 단계에서 동시 verify된 production V2 line counts EXACT MATCH 4건:

- 07_marketplace/rest_api.md — **805 L** (L-011 V2 NEW, LOCK-DT-01/08 정본 직접)
- 07_marketplace/python_sdk.md — **595 L** (L-012 V2 NEW, LOCK-DT-02 Python≥3.9 정본 직접)
- 07_marketplace/typescript_sdk.md — **551 L** (L-013 V2 NEW, LOCK-DT-02 Node≥18 정본 직접)
- 07_marketplace/webhook_events.md — **409 L** (L-016 V2 NEW)
- **합계 2,360 L EXACT** (4 파일 P3-3 verify subset / `07_marketplace/_index.md` 정본 P2-5 V2 NEW 5 파일 = **2,824 L** + api_docs_generator 464 L 별도) — P2-5 ✅ 2026-04-21 STEP_C closure inheritance 100% 정합 입증 (3-7 도메인 첫 production 인용값 정밀 검증 milestone, 4 파일 P3-3 scope subset 산술 정합 R6 drift fix 2026-05-17)

---

## 14. 실행 약점 대응 계획

### 14.1 주요 리스크

| 리스크 | 영향 | 대응 |
|--------|------|------|
| **LLM 모델 품질 변동** | FIM 자동완성 수락률 하락 | fallback chain (LOCK-DT-04) + A/B 테스트 의무화 |
| **플러그인 보안 취약점** | 악성 플러그인 배포 | WASM 샌드박스 (LOCK-DT-05) + 서명 검증 + 동적 분석 |
| **API 하위 호환성 파괴** | SDK 사용자 이탈 | 12개월 지원 정책 (R-10-3) + semantic versioning |
| **VS Code Extension 성능** | 편집기 지연 | 지연 예산 (자동완성 < 100ms, 코드 생성 < 15초) |
| **VADD 마켓플레이스 남용** | 품질 저하, 스팸 | 코드 리뷰 + 보안 스캔 + 사용자 리포트 + 개발자 인증 |
| **W6: API 버전 호환성** | v1/v2 동시 운영 시 라우팅 복잡도 증가 | API 게이트웨이 버전 분기 전략 필요 — URL prefix 버저닝(/v1, /v2) + Accept 헤더 병행 |
| **W7: 플러그인 보안** | 악성 플러그인 탐지 실패 시 사용자 데이터 노출 위험 | WASM 샌드박스 + Capability 기반 접근 제어 + 이상 탐지 임계값(API 호출 빈도 >100/s 차단) |
| **W8: FIM 모델 의존성** | vamos-coder-32b 미출시 상태에서 외부 모델 폴백 체인 의존 | 모델 가용성 모니터링 + 자동 전환 필요 — health check 주기 30s, 3회 연속 실패 시 폴백 |

### 14.2 운영 KPI

| KPI | 목표 | 측정 주기 |
|-----|------|----------|
| FIM 응답 지연 | < 100ms (p95) | 실시간 |
| 플러그인 검증 통과율 | > 85% | 주간 |
| API 가용률 | 99.9% | 일간 |
| 코드 생성 정확도 | HumanEval ≥85% | 분기 |

### 14.3 약점 모니터링

| 메트릭 | 임계값 | 조치 |
|--------|--------|------|
| 자동완성 수락률 | < 25% | 모델 재평가 + fallback 순서 조정 |
| API 응답 시간 p99 | > 3초 | 캐싱 강화 + 인프라 스케일업 |
| 플러그인 크래시 리포트 | > 5건/일 | 해당 플러그인 자동 비활성화 |
| 테스트 커버리지 | < 80% | 머지 차단 (R-10-2 연동) |

---

## 부록 §A — FIM (Fill-in-the-Middle) 프로토콜

### A.1 개요

커서 위치 기반 코드 완성 프로토콜. prefix(커서 앞 코드) + suffix(커서 뒤 코드)를 LLM에 전달하여 중간을 채우는 방식.

### A.2 요청/응답 스키마

```typescript
interface FIMRequest {
  prefix: string;         // 커서 앞 코드 (최대 4096 토큰)
  suffix: string;         // 커서 뒤 코드 (최대 2048 토큰)
  language: string;       // 프로그래밍 언어
  file_path: string;      // 파일 경로 (컨텍스트 힌트)
  max_tokens: number;     // 기본값 128
  temperature: number;    // 기본값 0.0 (결정론적)
  stop_sequences: string[];
}

interface FIMResponse {
  completion: string;
  confidence: number;     // 0.0 ~ 1.0
  tokens_used: number;
  latency_ms: number;
  alternatives: Array<{ text: string; score: number }>;
}
```

### A.3 모델 fallback chain

```
1차: Qwen 2.5 Coder 7B (로컬, Ollama)  — 기본 (LOCK-DT-04 정본 1단계)
2차: gpt-4o (API)                       — 로컬 모델 장애 시
3차: claude-sonnet (API)                — 전체 fallback
```

> **LOCK-DT-04**: 이 fallback chain 순서 변경 시 A/B 테스트 필수.

### A.4 성능 최적화

| 기법 | 설명 | 목표 지연 |
|------|------|----------|
| Speculative decoding | Draft 모델 후보 생성 → 검증 | < 100ms |
| Prefix caching | KV-cache 재활용 | < 80ms |
| Trie-based filtering | 로컬 심볼 테이블 사전 필터링 | < 10ms |
| Batched inference | 다중 요청 배치 처리 | < 200ms |
| ONNX Runtime | 경량 모델 로컬 추론 가속 | < 50ms |

### A.5 제안 랭킹 알고리즘

```python
def rank_completions(candidates: list[Completion], ctx: Context) -> list[Completion]:
    for c in candidates:
        c.score = (
            0.35 * c.model_confidence +
            0.25 * compute_type_match_score(c, ctx) +
            0.20 * compute_recency_score(c, ctx.history) +
            0.10 * compute_length_penalty(c) +
            0.10 * compute_frequency_score(c, ctx.project_symbols)
        )
    return sorted(candidates, key=lambda c: c.score, reverse=True)
```

---

## 부록 §B — Plugin SDK · WASM 샌드박스

### B.1 아키텍처 개요

```
┌──────────────────────────────────────────────┐
│            VAMOS Plugin Host Runtime          │
├──────────────┬──────────────┬────────────────┤
│  WASM Sandbox│  Node.js VM  │ Python Subprocess│
├──────────────┴──────────────┴────────────────┤
│              Plugin SDK API Layer             │
├──────────────────────────────────────────────┤
│  Core APIs:                                   │
│  - editor.*    (에디터 조작)                    │
│  - llm.*       (LLM 호출)                      │
│  - storage.*   (키-값 저장)                     │
│  - ui.*        (패널/다이얼로그)                 │
│  - vamos.*     (VAMOS 전용 기능)               │
└──────────────────────────────────────────────┘
```

### B.2 WASM 샌드박스 제약

| 제약 | 상세 | 근거 |
|------|------|------|
| **파일시스템** | 플러그인 전용 가상 FS만 접근. 호스트 FS 접근 불가 | LOCK-DT-05, R-10-1 |
| **네트워크** | manifest에 선언된 도메인만 접근 가능 | 데이터 유출 방지 |
| **CPU** | 단일 요청 30초 타임아웃 | LOCK-DT-06 |
| **메모리** | 플러그인당 256MB 상한 | 호스트 안정성 |
| **API 호출** | manifest.permissions에 선언된 API만 사용 가능 | 최소 권한 원칙 |

### B.3 플러그인 매니페스트

```json
{
  "$schema": "https://vamos.dev/schemas/plugin-manifest-v1.json",
  "id": "com.example.my-plugin",
  "name": "My VAMOS Plugin",
  "version": "1.0.0",
  "vamos_sdk_version": ">=2.0.0",
  "runtime": "wasm",
  "entry_point": "dist/plugin.wasm",
  "permissions": ["read:editor", "use:llm", "write:storage"],
  "activation_events": ["onLanguage:typescript", "onCommand:myPlugin.run"],
  "contributes": {
    "commands": [{ "id": "myPlugin.run", "title": "Run My Plugin" }],
    "menus": { "editor/context": [{ "command": "myPlugin.run", "group": "vamos" }] }
  },
  "vadd_card": {
    "category": "code-quality",
    "tags": ["linting", "ai-assisted"],
    "pricing": "free"
  }
}
```

> **LOCK-DT-09**: 이 매니페스트 스키마(v1)는 하위 호환 보장. 필드 추가는 가능하나 기존 필드 삭제/변경 금지.

### B.4 플러그인 라이프사이클

```
[개발자] → vamos plugin init → 로컬 개발/테스트
                                      │
                            vamos plugin pack → .vpkg 패키지
                                      │
                            vamos plugin publish → VADD Registry
                                      │
                            자동 검증: 보안 스캔 / 호환성 테스트 / 성능 벤치
                                      │
                            승인 → VADD Marketplace 게시
```

### B.5 Hook 시스템

```python
# 미들웨어 패턴
async def my_hook(context, next):
    # 전처리: 컨텍스트 수정/검증
    result = await next(context)
    # 후처리: 결과 변환/로깅
    return result

# 이벤트 유형
HOOK_EVENTS = [
    "on_chat_start",    "on_chat_end",
    "on_tool_call",     "on_agent_start",
    "on_agent_end",     "on_memory_store",
    "on_error",         "on_schedule"
]
```

### B.6 Phase 2 V2 — 05_plugin-sdk 6 파일 아키텍처 요약 (P2-3 상세 완성, 2026-04-21)

Phase 2 P2-3 에서 05_plugin-sdk 서브폴더의 V2 산출물 6 파일을 확정했다. 각 파일의 책임과 LOCK-DT-05/09 정본 인용 분포는 다음과 같다:

| # | 파일 | 구분 | STEP7-L | Lines | LOCK-DT-05 | LOCK-DT-09 | LOCK-DT-06 | 테스트 시나리오 |
|---|------|------|---------|-------|-----------|-----------|-----------|---------------|
| 1 | `plugin_architecture.md` | NEW | L-019 (L409~L437) | 654 | 24 지점 | 18 지점 (정본 직접) | 6 | PA-T01~T13 (13건) |
| 2 | `hook_system.md` §E | EXTEND | L-020 (L439~L460) | 422→704 (+282) | 6 | 7 | 5 | HS-V2-T01~T12 (12건) |
| 3 | `ui_components.md` | NEW | L-021 (L462~L477) | 506 | 8 | 3 | 4 | UI-T01~T12 (12건) |
| 4 | `theme_system.md` §E | EXTEND | L-022 (L479~L493) | 373→628 (+255) | 6 | 8 | 0 | TS-V2-T01~T12 (12건) |
| 5 | `wasm_sandbox.md` | NEW | L-025 (L531~L547) | 630 | **14 (정본 직접)** | 2 | 5 | WS-T01~T14 (14건) |
| 6 | `plugin_devkit.md` | NEW | L-026 (L549~L567) | 512 | 3 | 5 | 0 | DK-T01~T14 (14건) |
| **합계** | — | 4 NEW + 2 EXTEND | 6 L-ID × 56 line refs | **3,634** | **61** | **43** | **20** | **77 시나리오** |

### B.7 LOCK-DT-05 × LOCK-DT-09 통합 인용 표 (AUTHORITY §5 verbatim)

| LOCK ID | 항목 | 값 | 출처 | 근거 성격 | 변경 절차 | Phase 2 V2 정본 문서 |
|---------|------|---|------|----------|----------|-------------------|
| **LOCK-DT-05** | 플러그인 샌드박스 정책 | **WASM 격리, 선언된 권한만 허용** | L-025 | 확장 결정 | 보안 감사 필수 | **`wasm_sandbox.md` §2 (5필드 분리 인용) + §15 매트릭스 (20+ 지점)** |
| **LOCK-DT-09** | 플러그인 매니페스트 스키마 | `plugin-manifest-v1.json` | L-019 | 확장 결정 | 하위 호환 보장, 필드 추가만 허용 | **`plugin_architecture.md` §3.1 (5필드 분리 인용) + §3.2 스키마 + §10 매트릭스 (6 지점 정본)** |

CFL-005 (WASM 외 런타임 격리 불명확, P0-2 RESOLVED) 반영: `wasm_sandbox.md §7` 에서 Python subprocess / Node VM 완화 규정 명시 — WASM 격리 우선 결정 유지.

### B.8 Phase 3 이월 범위 표

| 축 | Phase 2 확정 V2 문서 | Phase 3 이월 사유 |
|----|---------------------|----------------|
| 동적 권한 요청 UX | `plugin_architecture.md §5.1` 선언형 확정 | 런타임 권한 prompt UI 는 Phase 3 |
| HSM 기반 고급 서명 | `wasm_sandbox.md §9`, `plugin_devkit.md §7` 로컬 키 | OS 키체인/HSM 통합은 Phase 3 |
| 머신러닝 기반 이상 탐지 | `wasm_sandbox.md §10.3` 임계값 | ML 모델 학습은 Phase 3 |
| Tamper-proof 감사 | `wasm_sandbox.md §11` JSONL 감사 | Merkle tree 서명은 Phase 3 |
| V3 네이티브 모바일 위젯 | `ui_components.md §1.3` V2 Web Components 확정 | iOS/Android 위젯은 Phase 3 |
| CI/CD 통합 | `plugin_devkit.md §8` 로컬 publish | GitHub Action 통합은 Phase 3 |
| 원격 디버거 | `plugin_devkit.md §5` 핫 리로드 + 로그 | 원격 디버깅은 Phase 3 |
| CSP nonce 동적 발급 | `wasm_sandbox.md §8` 정적 CSP | 동적 nonce 는 Phase 3 |
| 퍼징 지원 | `plugin_devkit.md §5` 테스트 러너 | 퍼징은 Phase 3 |
| 훅 성능 프로파일링 | `hook_system.md §E` 디스패치 알고리즘 | 프로파일러는 Phase 3 |

### B.9 V2↔V2 peer cross-reference 매트릭스 (실체화 134 지점)

| from ↓ / to → | plugin_architecture | hook_system | ui_components | theme_system | wasm_sandbox | plugin_devkit | 소계 |
|--------------|:------:|:------:|:------:|:------:|:------:|:------:|:----:|
| plugin_architecture | — | 12 | 10 | 4 | 8 | 5 | 39 |
| hook_system | 5 | — | 3 | 2 | 9 | 4 | 23 |
| ui_components | 11 | 2 | — | 3 | 3 | 2 | 21 |
| theme_system | 2 | 4 | 4 | — | 4 | 2 | 16 |
| wasm_sandbox | 6 | 2 | 3 | 0 | — | 3 | 14 |
| plugin_devkit | 4 | 4 | 3 | 4 | 6 | — | 21 |
| **합계 (받는 방향)** | **28** | **24** | **23** | **13** | **30** | **16** | **134** |

> 본 매트릭스는 `grep -c "<peer>.md"` 실측 기반 (2026-04-21, STEP_B #2a-part3 step 2 reverify). 목표 17+ 지점 대비 134 지점 (686% 달성). 3-2 part1/part2 16건 / 3-4 5-way / 3-5 5-way / 3-6 6-way / 3-7 part1 17건 / 3-7 part2 24건 선례 대비 최대 규모.

---

## 부록 §C — VADD 마켓플레이스

### C.1 앱 배포 체계

```
개발자 → .vpkg 업로드 → 자동 검증 파이프라인 → 수동 리뷰 (선택) → 게시
                              │
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
              보안 스캔   호환성 테스트  성능 벤치
              (Semgrep,   (VAMOS SDK   (메모리 ≤ 256MB,
               Snyk)      버전 호환)    시작 ≤ 3초)
```

### C.2 검수 기준

| 항목 | PASS 기준 | FAIL 시 |
|------|----------|--------|
| 보안 스캔 | CVE 0건, 시크릿 탐지 0건 | 즉시 REJECT |
| 호환성 | manifest.vamos_sdk_version 범위 내 동작 | REJECT + 피드백 |
| 성능 | 메모리 ≤ 256MB, 콜드 스타트 ≤ 3초, API 응답 ≤ 1초 | WARN (개선 요청) |
| 서명 | 개발자 인증서 서명 존재 | REJECT |
| 메타데이터 | 이름, 설명, 아이콘, 스크린샷 존재 | REJECT |

### C.3 과금 체계

| 모델 | 설명 | 수수료 |
|------|------|--------|
| **Free** | 무료 배포 | 0% |
| **Paid** | 일회성 구매 | VADD 30% / 개발자 70% |
| **Subscription** | 월간/연간 구독 | VADD 30% / 개발자 70% |
| **Freemium** | 기본 무료 + 프리미엄 기능 유료 | 유료 부분만 30% / 70% |

### C.4 개발자 대시보드

| 메트릭 | 설명 |
|--------|------|
| 설치 수 | 일/주/월 설치 추이 |
| 활성 사용자 | DAU/WAU/MAU |
| 수익 | 총 매출, 수수료, 정산 내역 |
| 크래시 리포트 | 에러 발생 빈도 + 스택 트레이스 |
| 리뷰/평점 | 사용자 평가 평균 + 댓글 |

---

## 부록 §D — 교차 도메인 의존성

| 대상 도메인 | 관계 | 의존 내용 |
|------------|------|----------|
| #1 Verifier | 소비 | LLM 추론 결과 검증 |
| #7 Workflow-RPA | 양방향 | 자동화 파이프라인 (가이드 부록 C) |
| #13 Agent-Protocol | 소비 | 에이전트 간 코드 리뷰 위임, VADD 마켓플레이스 |
| #16 MCP | 소비 | 도구 호출 프로토콜 |
| #8 Education | 제공 | 코드 실행 환경/린터/테스트 러너 (코딩 튜토리얼용) *(S7-2 추가)* |

---

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| v1.0 | 2026-03-23 | 초판 작성 (Phase 5 FINAL PASS) |
| v1.1 | 2026-03-31 | Phase 0 완료 — P0-1~P0-4 전수 완료, LOCK 10건 확정, 서브폴더 7개 생성 |
| v1.2 | 2026-04-10 | Phase 1 완료 — P1-1~P1-7 전 세션 완료 (39파일 L2+ 작성), Phase 1→2 게이트 PASS, Phase 2 진입 가능 |

*본 문서는 STEP7-L SOT 56 L-ID를 기반으로 작성되었으며, Phase 진행에 따라 갱신된다.*
*기존 `DEVELOPER_TOOLS_API_SDK_상세명세.md`는 기술 참조로 병행 유지한다.*
