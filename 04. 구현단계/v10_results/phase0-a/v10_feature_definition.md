# VAMOS v10 Feature Definition (Phase 0-A 산출물)

> **Phase**: 0-A | **생성일**: 2026-03-08
> **목적**: v10 Feature Coverage 검증의 기준 문서. Phase 0-B~C의 모든 에이전트가 본 문서를 참조한다.

---

## 1. 기능 항목(Feature Item) 정의

### 1.1 정의

```
하나의 Feature Item = PART2의 구현 Phase(V0 STEP 1~6, V1 Phase 1~6,
V2 Phase 1~3, V3 Phase 1~3)에 배정될 수 있는 최소 독립 구현 단위.
```

### 1.2 포함 대상

| 카테고리 | 설명 | 예시 |
|----------|------|------|
| **FT-MOD** | 모듈 구현 | I-1 Intent Detector 구현, E-7 STT 통합 |
| **FT-INFRA** | 인프라 구성 | Chroma→Qdrant 마이그레이션, K8s Helm |
| **FT-UI** | UI 화면/컴포넌트 | Builder View, 3-Panel, PWA 오프라인 |
| **FT-FUNC** | 기능 구현 | 5-Phase 파이프라인, RBAC 4역할 |
| **FT-CFG** | 설정/정책 | config.v1.toml 13섹션, LOCK 값 적용 |
| **FT-TEST** | 테스트/검증 | E2E Playwright, Python 80% 커버리지 |
| **FT-MIG** | 마이그레이션 | SQLite→PostgreSQL, NetworkX→Neo4j |
| **FT-API** | API 엔드포인트 | Tauri IPC 72개, JSON-RPC 13개 |
| **FT-SCHEMA** | 스키마 구현 | 25개 Pydantic 모델 코드 생성 |
| **FT-SEC** | 보안 구현 | Guardrails 4-Layer, PII 마스킹 |
| **FT-DOMAIN** | 도메인 기능 | AI Investing 51% Gate, SDAR 5-Layer |

### 1.3 제외 대상

- 설계 원칙, 철학, 방향성 서술 (예: "사용자 중심 설계를 지향")
- LOCK 값 자체 (값 정합성은 V8에서 검증 완료)
- 문서 간 용어 정의/약어 설명
- STEP7 TITLE_ONLY 항목 → `extractable=false` 태깅만
- PLAN-2.0 (SUPERSEDED) 내용

---

## 2. 추출 템플릿 (모든 에이전트 공통)

### 2.1 JSON 형식

```json
{
  "feature_id": "SRC약칭-NNN",
  "source_file": "D2.0-08",
  "source_line": 345,
  "source_section": "§7.3 모바일 UI",
  "feature_name": "React Native 네이티브 앱 (iOS/Android)",
  "version_scope": "V3",
  "category": "FT-UI",
  "implementation_type": "신규구현",
  "dependencies": ["IDEA-M05", "S7C-054"],
  "extractable": true,
  "confidence": "명시적",
  "notes": "D2.0-08 §7.3에 V3 RESERVED로 명시"
}
```

### 2.2 필드 명세

| 필드 | 필수 | 타입 | 설명 |
|------|------|------|------|
| `feature_id` | Y | string | `SRC약칭-순번` 형식. 예: `D208-015` |
| `source_file` | Y | string | SRC 파일 약칭. 예: `D2.0-08` |
| `source_line` | Y | int/string | 기능이 정의된 행번호. 범위일 경우 `시작-끝` |
| `source_section` | Y | string | SRC 파일 내 섹션 (§ 표기). 예: `§7.3 모바일 UI` |
| `feature_name` | Y | string | 기능 이름 (구현 관점에서 명확하게) |
| `version_scope` | Y | string | `V0` / `V1` / `V2` / `V3` (복수 가능: `"V1,V2,V3"`) |
| `category` | Y | string | 11개 카테고리 중 하나 (§1.2 참조) |
| `implementation_type` | Y | string | `신규구현` / `마이그레이션` / `설정` / `인프라` / `테스트` / `보강` |
| `dependencies` | N | string[] | 의존하는 다른 기능 ID 또는 모듈 ID |
| `extractable` | Y | bool | `true` / `false` (TITLE_ONLY 등은 `false`) |
| `confidence` | Y | string | `"명시적"` (SRC에 직접 기재) / `"추론"` (문맥에서 도출) |
| `notes` | N | string | 보충 설명 |

### 2.3 feature_id 네이밍 규칙

| SRC 파일 | 약칭 | feature_id 예시 |
|----------|------|-----------------|
| D2.0-01_OVERVIEW | D201 | D201-001 |
| D2.0-02_ORANGE_CORE | D202 | D202-001 |
| D2.0-03_BLUE_NODES | D203 | D203-001 |
| D2.0-04_INFRA_CORE | D204 | D204-001 |
| D2.0-05_AGENT_WORKFLOW | D205 | D205-001 |
| D2.0-06_STORAGE_MEMORY | D206 | D206-001 |
| D2.0-07_SAFETY_COST | D207 | D207-001 |
| D2.0-08_UI_UX | D208 | D208-001 |
| D2.1-A1_TECH_STACK | DA1 | DA1-001 |
| D2.1-D1~D8 (스키마) | DD1~DD8 | DD1-001 |
| D2.1-Q1_AUDIT | DQ1 | DQ1-001 |
| PHASE_B1~B7 | PB1~PB7 | PB1-001 |
| BASE-1.3 | BASE | BASE-001 |
| CLAUDE.md | CLAUDE | CLAUDE-001 |
| PLAN-3.0 | P30 | P30-001 |
| VAMOS_MASTER_SPEC | MSTR | MSTR-001 |
| VAMOS_STEP7_A-E | S7AE | S7AE-001 |
| VAMOS_STEP7_F-I | S7FI | S7FI-001 |
| VAMOS_STEP7_J-M | S7JM | S7JM-001 |
| VAMOS_STEP7_N-P | S7NP | S7NP-001 |
| VAMOS_STEP7_보강_통합 | S7BG | S7BG-001 |
| VAMOS_AGENT_TEAMS | TEAM | TEAM-001 |
| VAMOS_AI_INVESTING | AINV | AINV-001 |
| VAMOS_BEGINNER_GUIDE | BGNR | BGNR-001 |
| VAMOS_CLOUD_LIBRARY | CLIB | CLIB-001 |
| VAMOS_IMPL_READINESS_GUIDE | IRGD | IRGD-001 |
| VAMOS_IMPL_READINESS_REVIEW | IRRV | IRRV-001 |
| VAMOS_SDAR_DESIGN | SDAR | SDAR-001 |
| VAMOS_V0_READINESS | V0RD | V0RD-001 |

---

## 3. 에이전트 실행 규칙 (RULE-C1 ~ RULE-C9)

### RULE-C1: 전문 읽기 의무
할당된 SRC 파일을 **전문(全文)** 읽는다. 일부만 읽으면 반드시 보고.
- 읽은 줄 수 / 전체 줄 수, 미읽은 영역 명시
- **90% 미만** 읽은 파일 → 파일 분할 재실행 **필수**
- 마지막으로 읽은 줄의 내용 1줄을 그대로 인용 (거짓 완료 보고 방지)

### RULE-C2: 추출 템플릿 준수
위 §2 추출 템플릿에 따라 **모든 구현 기능 항목**을 추출한다.

### RULE-C3: version_scope 태깅 필수
- 명시적 태그가 있으면 → `confidence="명시적"`
- 문맥에서 추론하면 → `confidence="추론"` + 근거 기재
- 확정 불가능하면 → `version_scope="V_UNKNOWN"` + 근거 기재

### RULE-C4: TITLE_ONLY 처리
STEP7 항목 중 TITLE_ONLY는 `extractable=false`로 태깅한다.
- **TITLE_ONLY 판정 기준**: 제목만 있고 상세 설명/스펙이 없는 항목
- V2 CRITICAL + TITLE_ONLY → 제목 기반 PART2 키워드 매칭 시도
  - 매칭 불가 시 `"TITLE_ONLY_UNVERIFIABLE"` 태그

### RULE-C5: 경계 애매 항목 처리
기능인지 설명인지 판단이 애매하면 **일단 추출**하고 notes에 `"판단필요"` 표시.
- 추천(기능/제외) + 확신도(높음/중간/낮음) 함께 기재

### RULE-C6: 통계 보고 필수
추출 완료 후 아래 통계를 반드시 보고:
- 총 추출 건수 (`extractable=true` / `false` 구분)
- 카테고리별 분포
- `confidence="추론"` 건수
- `version_scope="V_UNKNOWN"` 건수
- `"판단필요"` 건수 (확신도별)
- 읽기 완료율

### RULE-C7: 중복 방지
하나의 SRC 파일 내에서 같은 기능이 여러 곳에 언급되면 **첫 출현만** 추출.
- 단, 버전별로 다른 내용이면 별도 항목으로 분리

### RULE-C8: SRC 경로 제한
SRC 경로는 반드시 `D:\VAMOS\docs\sot\` 만 사용한다.

### RULE-C9: 산출물 검증
산출물 JSON 저장 후 **파일 존재 확인**(Read 1줄) 수행.

---

## 4. 카테고리 정의 및 판단 예시

### 4.1 FT-MOD (모듈 구현)
> ORANGE CORE 또는 BLUE NODE의 내부 기능 모듈을 신규 구현하는 항목

| # | 예시 | 근거 |
|---|------|------|
| 1 | I-1 Intent Detector 모듈 구현 | D2.0-02 §7.1에서 I-1의 구현 직전 수준 설계를 명시. 독립 모듈로 구현 가능 |
| 2 | I-5 Runtime Brain Router 구현 | D2.0-02 §7.5에서 비용/품질/위험 기반 라우팅 모듈을 명시. 인터페이스+로직 구현 필요 |

### 4.2 FT-INFRA (인프라 구성)
> 실행 환경, 배포, 런타임 인프라를 구성하는 항목

| # | 예시 | 근거 |
|---|------|------|
| 1 | Docker Compose V2 스택 구성 | D2.0-04 §0.1에서 V2 Docker Compose 셋업 절차 명시 |
| 2 | HAL(Hardware Abstraction Layer) 구현 | D2.0-04 §4에서 하드웨어 독립 추상화 계층 명시 |

### 4.3 FT-UI (UI 화면/컴포넌트)
> 사용자 인터페이스 화면, 컴포넌트, 레이아웃을 구현하는 항목

| # | 예시 | 근거 |
|---|------|------|
| 1 | Builder View 5-탭 구현 (설정/정책/템플릿/레지스트리/디버그) | D2.0-08 §2.1에서 Builder View 구조 명시 |
| 2 | 3단 패널 레이아웃 구현 (좌/중/우) | D2.0-08 §3에서 좌(상태/정책/도메인), 중(대화/작업/그래프), 우(로그/근거/비용/승인/메모리) 구조 명시 |

### 4.4 FT-FUNC (기능 구현)
> 핵심 비즈니스 로직 또는 시스템 기능을 구현하는 항목

| # | 예시 | 근거 |
|---|------|------|
| 1 | 5-Phase 표준 파이프라인 (Perception→Reasoning→Action→Memory→Reflection) | D2.0-02 §0.4 체크리스트에서 표준 파이프라인 고정 명시 |
| 2 | Self-check 루프 (soft 1회 + hard 조건) | D2.0-02 §0.4에서 Self-check 조건 명시. P1-SCOPE NICE 항목 |

### 4.5 FT-CFG (설정/정책)
> 설정 파일, 정책 규칙, 레지스트리 등록 등 구성 항목

| # | 예시 | 근거 |
|---|------|------|
| 1 | ErrorHandlingStandard 적용 (Result<T, VamosError> 패턴) | D2.0-02 §0.3에서 에러 처리 인터페이스 통일 명시 |
| 2 | i18n 로케일 설정 (ko-KR 기본, en-US 보조, ja-JP V2 확장) | D2.0-08 §0 문서 메타에서 i18n 원칙 및 파일 구조 명시 |

### 4.6 FT-TEST (테스트/검증)
> 테스트 전략, 테스트 코드, 검증 도구를 구현하는 항목

| # | 예시 | 근거 |
|---|------|------|
| 1 | E2E Playwright 테스트 구현 | PHASE_B5에서 E2E 테스트 전략 명시 |
| 2 | Python 백엔드 80% 커버리지 달성 | PHASE_B5에서 커버리지 기준 명시 |

### 4.7 FT-MIG (마이그레이션)
> 기존 기술/데이터를 새로운 기술/구조로 이전하는 항목

| # | 예시 | 근거 |
|---|------|------|
| 1 | SQLite→PostgreSQL 마이그레이션 (V2) | D2.0-04 V2 Docker Compose에서 Postgres 마이그레이션 명시 |
| 2 | Chroma→Qdrant 벡터DB 마이그레이션 | PHASE_B7에서 마이그레이션 전략 명시 |

### 4.8 FT-API (API 엔드포인트)
> API 엔드포인트, IPC 커맨드, 프로토콜 인터페이스를 구현하는 항목

| # | 예시 | 근거 |
|---|------|------|
| 1 | Tauri IPC Core Commands (vamos:core:* 패턴) | PHASE_B1 §2에서 IPC command 네이밍 및 구조 명시 |
| 2 | JSON-RPC Python-Rust subprocess 통신 구현 | PHASE_B1 §1.3에서 V1 통신 프로토콜 명시 |

### 4.9 FT-SCHEMA (스키마 구현)
> Pydantic 모델, DB 스키마, 데이터 구조체를 코드로 구현하는 항목

| # | 예시 | 근거 |
|---|------|------|
| 1 | VamosError Pydantic 모델 구현 (failure_code, message, fallback_id, trace_id) | D2.0-02 §0.3에서 VamosError 필드 명시 |
| 2 | LogEvent 스키마 코드 생성 | D2.1-D2~D8에서 event_type 스키마 정의 |

### 4.10 FT-SEC (보안 구현)
> 보안 정책, 접근 제어, 데이터 보호를 구현하는 항목

| # | 예시 | 근거 |
|---|------|------|
| 1 | Guardrails 4-Layer 안전 필터 구현 | D2.0-07에서 Safety 정책 스키마 명시 |
| 2 | PII 마스킹 처리 구현 | D2.0-08 §8에서 민감정보 마스킹 표시 명시, D2.0-06/07 참조 |

### 4.11 FT-DOMAIN (도메인 기능)
> 특정 도메인(투자, 분석 등)에 특화된 비즈니스 기능을 구현하는 항목

| # | 예시 | 근거 |
|---|------|------|
| 1 | AI Investing 51% Gate 로직 구현 | VAMOS_AI_INVESTING_SPEC에서 51% 합의 게이트 명시 |
| 2 | SDAR 5-Layer 분석 파이프라인 구현 | VAMOS_SDAR_DESIGN_SPECIFICATION에서 5-Layer 구조 명시 |

---

## 5. "기능 vs 설명" 경계 판단 가이드라인

### 5.1 판단 원칙

| 구분 | 기능(Feature) | 설명(Description) |
|------|---------------|-------------------|
| 핵심 질문 | "구현해야 할 코드/설정이 있는가?" | "원칙/방향/정의를 서술하는가?" |
| 동사 패턴 | 구현, 생성, 마이그레이션, 통합, 배포 | 지향, 보장, 준수, 원칙 |
| 산출물 | 코드, 설정파일, 스키마, API, 화면 | 없음 (문서 내 서술에 그침) |
| PART2 매핑 | 특정 Phase/Step에 배정 가능 | 배정 불가 (크로스커팅 원칙) |

### 5.2 판단 예시 5건

#### 예시 1: ✅ 기능
> **"Front Mini LLM은 입력 1차 해석, 기초 안전 필터, 도메인 힌트를 수행한다"** (D2.0-02 §0.3)

- **판정**: **기능** (FT-MOD)
- **근거**: Front Mini LLM의 3가지 역할(해석/필터/힌트)은 각각 구현이 필요한 모듈 기능. 코드로 구현해야 하며 PART2에서 V0/V1에 배정 가능.

#### 예시 2: ❌ 설명
> **"CORE는 판단/제어에 집중하고, 실행 리소스는 INFRA 계층에서 추상화한다"** (D2.0-04 §1)

- **판정**: **설명** (제외 대상)
- **근거**: 아키텍처 원칙 서술. "집중한다", "추상화한다"는 설계 방향이지 구현 항목이 아님. 이 원칙을 실현하는 구체적 모듈(Brain Adapter, HAL 등)이 별도 기능으로 존재.

#### 예시 3: ✅ 기능
> **"모든 요청에 trace_id: string 포함"** (PHASE_B1 규칙)

- **판정**: **기능** (FT-API)
- **근거**: API 계약 규칙으로, 모든 엔드포인트에 trace_id 필드를 실제 구현해야 함. 코드 생성이 필요한 구현 항목.

#### 예시 4: ❌ 설명
> **"UI 구조/정책/이벤트 스키마 변경은 승인(Approval) 기반으로만 허용"** (D2.0-08 §0)

- **판정**: **설명** (제외 대상)
- **근거**: 변경 관리 정책 서술. 승인 기능 자체(FT-SEC/FT-FUNC)는 별도 항목이며, 이 문장은 변경 통제 원칙일 뿐.

#### 예시 5: ⚠️ 판단 필요 (경계)
> **"LogEvent payload의 message 필드는 영어 고정(로케일 무관 감사 추적 보장)"** (D2.0-08 §0)

- **판정**: **판단필요** → 추천: 기능, 확신도: 중간
- **근거**: 한편으로는 정책 서술이지만, LogEvent 스키마 구현 시 message 필드의 언어 고정 로직을 코드로 강제해야 함. 스키마 구현(FT-SCHEMA) 또는 설정(FT-CFG)의 일부로 포함 가능.

---

## 6. SRC 파일 목록 (43개)

| # | 파일명 | 약칭 |
|---|--------|------|
| 1 | BASE-1.3_VAMOS_RULE_1.3_BASE.md | BASE |
| 2 | CLAUDE.md | CLAUDE | ← Phase 0-B(Layer 1) + C-10(Layer 2) 이중 추출 대상 |
| 3 | D2.0-01_01. VAMOS_DESIGN_2_0_OVERVIEW.md | D201 |
| 4 | D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md | D202 |
| 5 | D2.0-03_03. VAMOS_DESIGN_2.0_BLUE_NODES.md | D203 |
| 6 | D2.0-04_04. VAMOS_DESIGN_2.0_INFRA_CORE.md | D204 |
| 7 | D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md | D205 |
| 8 | D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md | D206 |
| 9 | D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md | D207 |
| 10 | D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md | D208 |
| 11 | D2.1-A1_A1_TECH_STACK.md | DA1 |
| 12 | D2.1-D1_D1_SCHEMA_GLOSSARY.md | DD1 |
| 13 | D2.1-D2_D2_SCHEMA_ORANGE_CORE.md | DD2 |
| 14 | D2.1-D3_D3_SCHEMA_BLUE_NODES.md | DD3 |
| 15 | D2.1-D4_D4_SCHEMA_INFRA_CORE.md | DD4 |
| 16 | D2.1-D5_D5_SCHEMA_AGENT_WORKFLOW.md | DD5 |
| 17 | D2.1-D6_D6_SCHEMA_STORAGE_MEMORY.md | DD6 |
| 18 | D2.1-D7_D7_SCHEMA_SAFETY_COST_APPROVAL.md | DD7 |
| 19 | D2.1-D8_D8_SCHEMA_UI_UX.md | DD8 |
| 20 | D2.1-Q1_Q1_AUDIT_REPORT.md | DQ1 |
| 21 | PHASE_B1_API_CONTRACT.md | PB1 |
| 22 | PHASE_B2_PROJECT_STRUCTURE.md | PB2 |
| 23 | PHASE_B3_DEPENDENCIES.md | PB3 |
| 24 | PHASE_B4_CONFIG_SPEC.md | PB4 |
| 25 | PHASE_B5_TEST_STRATEGY.md | PB5 |
| 26 | PHASE_B6_CICD_PIPELINE.md | PB6 |
| 27 | PHASE_B7_MIGRATION_STRATEGY.md | PB7 |
| 28 | PLAN-2.0_VAMOS_PLAN_2.0_.md | P20 (SUPERSEDED — 추출 제외) |
| 29 | PLAN-3.0_VAMOS_PLAN_3_0_최종완성본.md | P30 |
| 30 | VAMOS_AGENT_TEAMS_SPEC.md | TEAM |
| 31 | VAMOS_AI_INVESTING_SPEC.md | AINV |
| 32 | VAMOS_BEGINNER_GUIDE.md | BGNR |
| 33 | VAMOS_CLOUD_LIBRARY_SPEC.md | CLIB |
| 34 | VAMOS_IMPLEMENTATION_READINESS_GUIDE.md | IRGD |
| 35 | VAMOS_IMPLEMENTATION_READINESS_REVIEW.md | IRRV |
| 36 | VAMOS_MASTER_SPECIFICATION.md | MSTR |
| 37 | VAMOS_SDAR_DESIGN_SPECIFICATION.md | SDAR |
| 38 | VAMOS_STEP7_A-E_상세명세서.md | S7AE |
| 39 | VAMOS_STEP7_F-I_상세명세서.md | S7FI |
| 40 | VAMOS_STEP7_J-M_상세명세서.md | S7JM |
| 41 | VAMOS_STEP7_N-P_보강_상세명세서.md | S7NP |
| 42 | VAMOS_STEP7_보강_통합명세서.md | S7BG |
| 43 | VAMOS_V0_READINESS_FINAL_REVIEW.md | V0RD |

> **참고**: PLAN-2.0은 SUPERSEDED 상태이므로 기능 추출 대상에서 제외 (C-10에서 스캔만 수행).
> CLAUDE.md는 Phase 0-B(Layer 1) + Phase 0-C C-10(Layer 2)에서 이중 추출 대상.
> 실질 추출 대상: **42개 파일** (PLAN-2.0만 제외)

---

## 7. Phase 0-B/C 에이전트 참조 요약

본 문서를 기준으로 Phase 0-B~C 에이전트는 다음을 준수한다:

1. **추출 대상**: §1.2 포함 대상 + §1.3 제외 대상 기준 적용
2. **추출 형식**: §2.1 JSON 템플릿 필수 준수
3. **ID 채번**: §2.3 네이밍 규칙에 따른 feature_id 부여
4. **실행 규칙**: §3 RULE-C1~C9 전체 준수
5. **카테고리 판단**: §4 정의 및 예시 참조
6. **경계 판단**: §5 가이드라인 적용, 애매한 경우 RULE-C5에 따라 처리
7. **SRC 파일**: §6 목록의 42개 파일 (PLAN-2.0만 제외)

---

> **문서 끝** | Phase 0-A 완료
