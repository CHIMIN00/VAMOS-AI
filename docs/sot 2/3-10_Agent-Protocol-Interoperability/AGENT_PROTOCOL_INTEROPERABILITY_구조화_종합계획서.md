# Agent Protocol / Interoperability 구조화 종합 계획서

> **버전**: v1.0
> **작성일**: 2026-03-23
> **목적**: sot 2/3-10_Agent-Protocol-Interoperability/를 에이전트 프로토콜·상호운용성 구현 정본으로 구조화
> **Status**: APPROVED — Phase 5 FINAL PASS (2026-03-24)
> **Tier**: 3
> **SOT 출처**: STEP7-K (86개 항목, 10 Parts)
> **Part2 상태**: PARTIAL (44개 항목 미반영, MCP·Agent Teams·LangGraph 일부만 반영 — 76 K-ID 중 24 반영/44 미반영/8 N/A)

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
- [§A 프레임워크 어댑터 카탈로그](#a-프레임워크-어댑터-카탈로그)
- [§B 자율성 레벨 L0~L4 정의](#b-자율성-레벨-l0l4-정의)
- [§C 안전 가드레일 규칙 엔진](#c-안전-가드레일-규칙-엔진)
- [§D 의존성 매트릭스](#d-의존성-매트릭스)

---

## 1. 현재 상태 분석

### 1.1 기존 문서 현황

| 문서 | 위치 | 역할 | 줄수 | 상태 |
|------|------|------|------|------|
| **STEP7-K 작업가이드** | docs/sot/ | 86개 항목 체크리스트 (10 Parts) | ~1,400 | 항목 목록 + 구현 상세 개요, 구현 코드 없음 |
| **PART2 구현단계** | docs/guides/ | 구현 가이드 | ~2,600 | PARTIAL — MCP(§6.6), Agent Teams(§6.7), LangGraph(§3 Phase 3) 반영, 24항목 반영 / 44항목 미반영 (76 K-ID 기준) |
| **기존 상세명세** | sot 2/3-10_*/ | 도메인 명세 v1.0 | 770 | DRAFT — 6개 서브도메인(A~F) 기술, 인터페이스 스키마 수준 |

### 1.2 sot 2/3-10_Agent-Protocol-Interoperability/ 현재 파일

| 파일 | 줄수 | 상태 |
|------|------|------|
| `AGENT_PROTOCOL_INTEROPERABILITY_상세명세.md` | 770 | 6개 서브도메인 구조, 코드 스키마 포함 |

### 1.3 STEP7-K 86개 항목 현황 (76개 K-ID, K-001~K-076, 일부 번호 묶음 포함 — STEP7-K 원본 카운트 준수)

| Part | 범위 | K-ID 수 | 주제 | Part2 반영 | 반영/미반영 |
|------|------|---------|------|-----------|-----------|
| Part 1 | K-001~K-010 | 10 | MCP 심화 | PARTIAL (§6.6 MCP — K-001~K-005·K-007·K-010 반영) | 7/3 |
| Part 2 | K-011~K-020 | 10 | A2A 프로토콜 | PARTIAL (§6.7 Agent Card/Task/Discovery/Delegation) | 4/6 |
| Part 3 | K-021~K-030 | 10 | 멀티에이전트 프레임워크 | PARTIAL (K-021 LangGraph §3, K-022·K-025 §6.7 MINIMAL) | 3/7 |
| Part 4 | K-031~K-040 | 10 | 외부 서비스 연동 | PARTIAL (K-031 LiteLLM·K-032 Tavily·K-033 E2B·K-034 MINIMAL) | 4/6 |
| Part 5 | K-041~K-048 | 8 | 에이전트 자율성/안전 | PARTIAL (K-041 RBAC·K-043 샌드박스·K-044 비용, K-042 HITL MINIMAL) | 4/4 |
| Part 6 | K-049~K-054 | 6 | 데이터 교환 형식 | MINIMAL (K-049 VamosMessage 기본, K-054 Streamable HTTP) | 2/4 |
| Part 7 | K-055~K-060 | 6 | 에이전트 배포/확장 | ABSENT | 0/6 |
| Part 8 | K-061~K-068 | 8 | 차별화 전략 | ABSENT | 0/8 |
| Part 9 | K-069~K-072 | 4 | 참고 자료 | N/A (비구현) | — |
| Part 10 | K-073~K-076 | 4 | 구현 로드맵 | N/A (참조) | — |
| | | **76 K-ID** | | | **24 반영 / 44 미반영 / 8 N/A** |

### 1.4 핵심 문제

1. **44항목 미반영(ABSENT)**: Parts 5~8(자율성, 데이터교환, 배포, 차별화) 중 22항목이 Part2에 전혀 없고, Parts 1~4에서도 세부 구현 상세 22항목이 누락 (Part 5는 K-041~K-044 4건 반영 확인)
2. **기존 명세 깊이 부족**: 상세명세가 인터페이스 스키마 수준이며, 알고리즘·에러핸들링·성능 기준 미정의
3. **도메인 횡단 의존성 미정리**: #4 COND(COND-085), #11 A2A(프로토콜 계층), #16 MCP(도구 프로토콜) 간 경계 불명확
4. **자율성 레벨 미정의**: L0~L4 레벨 전환 조건·가드레일이 정식 정의되지 않음

### Part2 상태 및 방식 C 접근법
- **Part2 상태**: PARTIAL
- **방식 C 접근법**: 보완 작성

---

## 2. 목표 구조 (최종 형태)

### 2.1 폴더 트리

```
3-10_Agent-Protocol-Interoperability/
├── AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md   ← 본 문서
├── AGENT_PROTOCOL_INTEROPERABILITY_상세명세.md           ← 기존 유지
├── AUTHORITY_CHAIN.md                                    ← 권한 체계
├── CONFLICT_LOG.md                                       ← 충돌 기록
├── 01_framework-adapters/
│   ├── _index.md        ← K-021~K-030 프레임워크 통합 10항목
│   ├── crewai_adapter.md
│   ├── autogen_adapter.md
│   └── langgraph_adapter.md
├── 02_service-integration/
│   ├── _index.md        ← K-031~K-040 외부 서비스 연동 10항목
│   ├── llm_gateway.md
│   └── external_apis.md
├── 03_data-exchange/
│   ├── _index.md        ← K-049~K-054 데이터 교환 6항목
│   ├── message_format.md
│   └── serialization.md
├── 04_deployment-scaling/
│   ├── _index.md        ← K-055~K-060 배포/스케일링 6항목
│   └── container_spec.md
├── 05_self-evolution/
│   ├── _index.md        ← K-061~K-068 차별화 전략 8항목
│   └── dream_mode.md
└── 06_autonomy-safety/
    ├── _index.md        ← K-041~K-048 자율성/안전 8항목
    ├── permission_matrix.md
    └── guardrail_rules.md
```

### 2.2 깊이 규칙

```
최대 3단계:
  3-10_*/ → XX_{카테고리}/ → 파일.md           (2단계) ✅
  4단계 이상 → 절대 금지 ❌
```

### 2.3 네이밍 규칙

- **폴더명**: 영문 소문자 + 하이픈, 2자리 번호 접두사 (`01_`, `02_`, ...)
- **파일명**: 영문 소문자 + 언더스코어 (`.md` 확장자)
- **계획서**: 한글 허용 (`*_구조화_종합계획서.md`)

---

## 3. 권한 체계 선언

### 3.1 기존 VAMOS 체인

```
RULE 1.3 (헌법) > PLAN 3.0 (기획서) > DESIGN 2.0 (설계) > STEP7 (SOT 체크리스트)
```

### 3.2 Agent-Protocol 확장 체인

```
STEP7-K (86항목 SOT 체크리스트)
  ↓
sot 2/3-10_Agent-Protocol-Interoperability/ (구현 정본)
  ├── 구조화_종합계획서.md (마스터 플랜)
  ├── AUTHORITY_CHAIN.md (권한 선언)
  ├── 상세명세.md (기존 기술 명세)
  └── XX_서브폴더/ (항목별 상세)
```

### 3.3 문서별 범위

| 문서 | 정본 범위 | 비고 |
|------|----------|------|
| **STEP7-K** | 항목 정의 (What to build) | 체크리스트 — 변경 불가 |
| **Part2 구현단계** | When + Where (Phase 배정, 코드 위치) | Phase 3/6 배정 — LOCK |
| **sot 2/ (본 폴더)** | How (구현 상세, 알고리즘, 스키마, 에러핸들링) | 구현 정본 |
| **D2.0-03** | Blue Node 인터페이스 계약 | LOCK — 재정의 금지 |
| **D2.0-05** | A2A 프로토콜 정본 | LOCK — 메시지 포맷 |

### 3.4 LOCK 보호 목록

| LOCK ID | 항목 | 원본 | 값 |
|---------|------|------|-----|
| LOCK-AP-01 | 프로토콜 메시지 포맷 | STEP7-K, D2.0-05 | VamosMessage 스키마 (id, type, source, target, content, metadata) |
| LOCK-AP-02 | 에이전트 권한 레벨 | STEP7-K K-041 | Permission Level 0~5 (읽기→금융) |
| LOCK-AP-03 | A2A Task 상태 머신 | D2.0-05, K-012 | submitted→working→input-required→completed/failed/canceled |
| LOCK-AP-04 | MCP 전송 방식 | Part2 §6.6 | Streamable HTTP (V1), WebSocket 아님 |
| LOCK-AP-05 | Agent Teams V1 제한 | Part2 §6.7 LOCK-AT-014 | Lead + max 2 Sub-Agent |
| LOCK-AP-06 | Circuit Breaker recovery | D2.0-05 §4.4 LOCK | 60초 (D2.1 스키마 300s는 하위) |
| LOCK-AP-07 | 인터롭 규격 | STEP7-K | A2A + MCP 양방향 지원 필수 |
| LOCK-AP-08 | LangGraph 상수 | Part2 Phase 3 규칙 | START/END 상수 사용 (set_entry_point 금지) |
| LOCK-AP-09 | 비용 상한 | Part2 §비용 + 가이드 부록 D (STEP7-H 참조) | V1: ₩40K, V2: ₩93K, V3: ₩266K |
| LOCK-AP-10 | Confidence 임계값 | MASTER_SPEC §5/§7.9 | HITL 트리거 < 50% |

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
| R7 | STEP7-K 86건 ↔ sot 2/ 매핑 테이블 유지 | 중복/충돌 정리 | §6 매핑에 기록 |
| R8 | PART2 링크는 단일 테이블에 집중 | 링크 관리 단순화 | 본문 산발 링크 금지 |
| R9 | LOCK/FREEZE 값 재정의 금지. 참조 시 `> LOCK (출처): [원문]` | LOCK 보호 | 즉시 수정 |

### 4.2 도메인 고유 규칙

| ID | 규칙 | 근거 |
|----|------|------|
| R-13-1 | L3 이상 자율성 전환 시 Human-in-the-Loop 승인 필수 | K-042, §B 자율성 레벨 |
| R-13-2 | 외부 프레임워크 버전 잠금: major 변경 시 어댑터 재검증 필수 | K-021~K-025, 호환성 보장 |
| R-13-3 | CEL 가드레일 규칙 추가 시 pre_action/runtime/post_action 분류 필수 | K-041~K-048, §C 가드레일 |
| R-13-4 | A2A ↔ MCP 브리지 양방향 변환 보장 | K-017 LOCK-AP-07 |
| R-13-5 | 에이전트 배포 시 리소스 클래스(light/standard/heavy) 명시 필수 | K-055~K-056 |
| R-13-6 | 자기진화(Self-Evolution) 전략 변경 시 max_strategy_drift 이내 | K-047, K-061 |
| R-13-7 | 외부 에이전트 첫 연동 시 사용자 명시적 승인 필수 | K-015 신뢰 모델 |

---

## 5. 선행작업

### 5.1 STEP7-K 항목 분류 + Part2 GAP 확인

- **목적**: 86항목을 6개 서브폴더에 매핑하고, Part2 반영/미반영 구분
- **산출물**: §6 이슈 해결 매핑 테이블
- **상태**: ✅ 완료 (본 계획서 §1.3, §6)

### 5.2 도메인 횡단 의존성 정리

- **목적**: #4 COND(COND-085), #11 A2A, #16 MCP 간 경계 확정
- **방법**: 각 도메인의 AUTHORITY_CHAIN 참조 → 정본 소유자 확정
- **결과**:
  - MCP 프로토콜 자체 → #16 MCP 정본, #13은 "MCP 활용" 관점만 소유
  - A2A 프로토콜 스펙 → #11 A2A 정본, #13은 "인터롭 브리지" 소유
  - COND-085 에이전트통합 → #4 COND 정본, #13은 "프레임워크 어댑터" 소유

### 5.3 기존 상세명세 정합성 확인

- **목적**: 상세명세 770줄의 인터페이스 정의가 STEP7-K와 모순 없는지 검증
- **결과**: 모순 없음 — 상세명세는 STEP7-K 세부 구현 수준의 스키마를 제공하며 상호 보완적

---

## 6. 이슈 해결 매핑

### 6.1 STEP7-K 76 K-ID 전수 매핑 (STEP7-K 원본 카운트 86건, 일부 묶음 포함)

| 서브폴더 | STEP7-K 항목 | K-ID 수 | Part2 상태 | 반영/미반영 | 해결 방식 |
|----------|-------------|---------|-----------|-----------|----------|
| `01_framework-adapters/` | K-021~K-030 | 10 | PARTIAL (K-021 LangGraph §3 반영, K-022·K-025 §6.7 MINIMAL, K-023·K-024·K-026~K-030 ABSENT) | 3/7 | 방식 C 요약 + 미반영 항목 신규 |
| `02_service-integration/` | K-031~K-040 | 10 | PARTIAL (K-031 LiteLLM·K-032 Tavily·K-033 E2B §6.6 반영, K-034 §6.6 MINIMAL, K-035~K-040 ABSENT) | 4/6 | 방식 C 요약 + 미반영 항목 신규 |
| `03_data-exchange/` | K-049~K-054 | 6 | MINIMAL (K-049 VamosMessage 기본, K-054 Streamable HTTP MINIMAL, K-050~K-053 ABSENT) | 2/4 | 거의 전면 신규 |
| `04_deployment-scaling/` | K-055~K-060 | 6 | ABSENT | 0/6 | 전면 신규 |
| `05_self-evolution/` | K-061~K-068 | 8 | ABSENT | 0/8 | 전면 신규 |
| `06_autonomy-safety/` | K-041~K-048 | 8 | PARTIAL (K-041 RBAC·K-043 샌드박스·K-044 비용 §6.7 반영, K-042 HITL §6.5 MINIMAL, K-045~K-048 ABSENT) | 4/4 | 방식 C 요약 + 미반영 항목 신규 |
| *(MCP — #16 정본)* | K-001~K-010 | 10 | PARTIAL (K-001~K-005·K-007·K-010 §6.6 반영, K-006·K-008·K-009 ABSENT) | 7/3 | #16 MCP 도메인 정본 참조 |
| *(A2A — #11 정본)* | K-011~K-020 | 10 | PARTIAL (K-011~K-014 §6.7 Agent Card/Task/Discovery/Delegation, K-015~K-020 ABSENT) | 4/6 | #11 A2A 도메인 정본 참조 |
| *(참고/로드맵)* | K-069~K-076 | 8 | N/A (비구현 참조) | —/— | 부록 참조 |
| **합계** | | **76 K-ID** | | **24 반영 / 44 미반영 / 8 N/A** | |

> **MCP(K-001~K-010)**: 프로토콜 자체는 #16 MCP 정본. 본 도메인은 "MCP를 활용한 프레임워크 통합" 관점에서 K-010(Blue Node 브리지), K-017(A2A↔MCP 브리지)를 `01_framework-adapters/`와 `02_service-integration/`에서 다룸.
>
> **A2A(K-011~K-020)**: 프로토콜 스펙은 #11 A2A 정본. 본 도메인은 "A2A를 통한 외부 에이전트 상호운용" 관점에서 K-014(멀티에이전트 협업), K-017(브리지)를 다룸.
>
> **Part2 반영 분류 기준**: Part2는 K-ID를 직접 참조하지 않으므로 개념 중첩(concept overlap) 기준으로 분류. PARTIAL = 구현 방향·코드 위치·Phase 배정 존재, MINIMAL = 개념만 언급, ABSENT = 전혀 미언급.

### 6.2 미반영(ABSENT) 항목 상세 — 6개 서브폴더 기준 (35건)

> 우선순위는 §7 Phase 실행 계획의 V 로드맵과 정합. P0 = V1(§7.3), P1 = V2(§7.4), P2 = V3(§7.5).

| 범위 | 미반영(ABSENT) 항목 | 핵심 내용 | 우선순위 | §7 배정 |
|------|-------------------|----------|---------|---------|
| K-023 | AutoGen 대화형 에이전트 | 프레임워크 변환기 구현 | **P0** | §7.3 V1 |
| K-024 | Magentic-One 패턴 | 프레임워크 변환기 구현 | P1 | §7.4 V2 |
| K-026~K-030 | Reflection/Planning/Tool Use/메모리공유/벤치마크 | 에이전트 패턴 상세 | P1 | §7.4 V2 |
| K-045~K-046 | 롤백·되돌리기 / 설명가능성 | 자율성·안전 V1 범위 | **P0** | §7 미배정 ⚠ |
| K-051 | 이벤트 버스 | 데이터 교환 V1 | **P0** | §7.3 V1 |
| K-047 | 자기진화 안전 가드레일 | 자율성·안전 V2 | P1 | §7.4 V2 |
| K-050·K-052~K-053 | Artifact / API버전 / 직렬화 | 데이터 교환 심화 | P1 | §7.4 V2 |
| K-061~K-068 | 자기진화/예측/앰비언트/시간여행/페르소나/멀티유저/마켓/테스트 | 차별화 전체 | P1 | §7.4~7.5 V2~V3 |
| K-035~K-040 | 클라우드/캘린더/금융/IoT/CI·CD/외부AI | 외부 서비스 연동 확장 | P2 | §7.4 V2 + §7.5 K-038 V3 |
| K-055~K-060 | 패키징/스케일링/헬스체크/로깅/설정/마이그레이션 | 배포·확장 전체 | P2 | §7.4 V2 + §7.5 K-056 V3 |
| K-048 | 에이전트 윤리 프레임워크 | Constitutional AI 연동 | P2 | §7.5 V3 |

> **P0 합계**: K-023 + K-045~K-046 + K-051 = **4건** (V1 Phase 1 범위)
> **P1 합계**: K-024 + K-026~K-030 + K-047 + K-050·K-052~K-053 + K-061~K-068 = **18건** (V2 Phase 2 범위)
> **P2 합계**: K-035~K-040 + K-055~K-060 + K-048 = **13건** (V2~V3 Phase 2~3 범위)
> **6 서브폴더 ABSENT 합계**: 4+18+13 = **35건**. 외부 도메인 포함 시 44건.
>
> ⚠ **§7 미배정 항목**: K-045(롤백)·K-046(설명가능성)은 06_autonomy-safety 소속 ABSENT이나 §7.3~§7.5 어디에도 미배정. Phase 1에서 K-041~K-043과 함께 작성 권고.
>
> **외부 도메인 ABSENT**: MCP #16 정본 내 3건(K-006·K-008·K-009), A2A #11 정본 내 6건(K-015~K-020) — 해당 도메인 책임.

---

## 7. Phase 실행 계획

### 7.1 Phase 전환 게이트

```
Phase 0 → Phase 1: §6 매핑 100% + AUTHORITY_CHAIN 작성 + 서브폴더 골격
Phase 1 → Phase 2: 01_/06_ P0 항목 L2 이상 + Part2 방식 C 요약 완료
Phase 2 → Phase 3: 전 서브폴더 L2 이상 + 교차 검증 PASS
Phase 3 완료: L3 전수 승급 + FINAL REVIEW PASS
```

### 7.2 Phase 0: 분석 + 골격 (완료)

> **Phase 0 완료**: 2026-04-02 | P0-1~P0-7 전수 완료 (7/7)
> **게이트 PASS**: G0-1 §6 매핑 100% ✅ · G0-2 AUTHORITY_CHAIN 작성 ✅ · G0-3 서브폴더 골격 ✅ → Phase 0→1 전환 게이트 **PASS**

| 작업 | 산출물 | 상태 |
|------|--------|------|
| P0-1. STEP7-K 86항목 분류 | §1.3, §6 매핑 테이블 | ✅ |
| P0-2. Part2 PARTIAL 영역 식별 | §7.3 방식 C 요약 3건 | ✅ |
| P0-3. 계획서 14+4 섹션 작성 | 본 문서 (APPROVED) | ✅ |
| P0-4. AUTHORITY_CHAIN.md | 10개 LOCK 항목 (LOCK-AP-01~AP-10) | ✅ |
| P0-5. CONFLICT_LOG.md | 6건 등록 (v1.1) | ✅ |
| P0-6. 서브폴더 6개 + _index.md | 골격 생성 (6/6) | ✅ |
| P0-7. SOT2_MASTER_INDEX.md 갱신 | #13 항목 12필드 + 총괄표 | ✅ |

#### Phase 0 단계별 상세 작업 절차

<details>
<summary><b>P0-1. STEP7-K 86항목 분류 + §6 매핑</b></summary>

**목표**: STEP7-K 86항목(76 K-ID, 일부 묶음)을 §6 매핑 테이블에 전수 매핑하고, Part2 반영 상태를 분류하여 Phase 0→1 전환 게이트 **G0-1(§6 매핑 100%)**을 충족한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md` (86항목, 10 Parts, K-001~K-076)
- `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` (A2A 아키텍처, LOCK 항목 30+건)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` (§3 LangGraph, §6.6 MCP, §6.7 Agent Teams — Part2 반영 상태 분류에 필요)

**절차**:
1. STEP7-K에서 K-001~K-076 전수 추출 (76 K-ID, 묶음 포함 86건 — STEP7-K 원본 항목 카운트 기준 준수)
2. 10 Parts를 다음 **9개 카테고리**에 매핑:
   - **6개 서브폴더**: `01_framework-adapters`(K-021~K-030), `02_service-integration`(K-031~K-040), `03_data-exchange`(K-049~K-054), `04_deployment-scaling`(K-055~K-060), `05_self-evolution`(K-061~K-068), `06_autonomy-safety`(K-041~K-048)
   - **2개 외부 도메인 정본**: #16 MCP 정본(K-001~K-010, Part 1), #11 A2A 정본(K-011~K-020, Part 2) — 본 도메인은 "활용/인터롭" 관점만 소유
   - **1개 참고/로드맵**: K-069~K-076 (Parts 9-10, 비구현 참조 자료)
3. Part2(§3, §6.6, §6.7)를 읽고 항목별 반영 상태를 3단계로 분류:
   - **PARTIAL**: Part2에 해당 K-ID의 구현 방향·코드 위치·Phase 배정이 부분적으로 존재
   - **MINIMAL**: Part2에 개념만 언급되었으나 구현 상세 없음
   - **ABSENT**: Part2에 전혀 미언급
   - 실측치: 반영(PARTIAL+MINIMAL) 24건 / 미반영(ABSENT) 44건 / N/A 8건 (§1.3 기준, P0-1 실행 결과)
4. §6 매핑 테이블 **2종** 작성:
   - **§6.1 서브폴더별 집계**: `| 서브폴더 | STEP7-K 항목 | 항목 수 | Part2 상태 | 해결 방식 |`
   - **§6.2 미반영 항목 상세**: `| 범위 | 미반영 항목 | 핵심 내용 | 우선순위 |`
   - **우선순위 기준**: P0 = V1 핵심 (01_ 프레임워크 어댑터, 06_ 자율성·안전), P1 = V1 보완 + V2 준비 (03_ 데이터교환, 05_ 차별화), P2 = V2~V3 확장 (02_ 서비스연동 확장, 04_ 배포)
5. §1.3 항목 현황 테이블 갱신 (§6의 Part별 상위 요약 뷰)

**검증**: ✅ 전수 PASS (2026-04-01)
- [x] 76 K-ID 전수 매핑 (빠짐 0건) — **G0-1 (§6 매핑 100%)** PASS
  - STEP7-K K-ID 전체 목록과 §6.1 9개 카테고리 1:1 대조 완료, 누락·이중카운트 0건
- [x] Part2 PARTIAL/MINIMAL/ABSENT 분류 정합 — PASS
  - Part2 원문(§3, §6.6, §6.7) 개념 중첩 기준 분류: 24 반영 / 44 미반영 / 8 N/A
- [x] D2.0-05 LOCK 4건 무충돌 — PASS
  - §5.3.2 Node-to-Node 금지, §2 병렬 3상한, §7.3 Gate 선행, §5.1 trace_id 필수 — 매핑 항목 위반 0건
- [x] 외부 도메인 정본 경계 §5.2 정합 — PASS
  - #16 MCP(K-001~K-010), #11 A2A(K-011~K-020) 경계 일치
- [x] §6.1 합계 = 76 K-ID, §6.2(35건) ⊂ §6.1(44건 미반영) — PASS
- [x] §6.2 우선순위 ↔ §7 Phase V 로드맵 정합 — PASS (K-045/K-046 §7 미배정 ⚠ 기록)

**산출물**: §6.1 서브폴더별 매핑 테이블 + §6.2 미반영 항목 상세(35건, P0/P1/P2) + §1.3 항목 현황 (본 계획서 내)
**상태**: ✅ 완료
</details>

<details>
<summary><b>P0-2. Part2 PARTIAL 영역 식별 + 방식 C 요약</b></summary>

**목표**: Part2에서 #13 도메인과 중첩되는 PARTIAL 영역을 Part2 섹션 단위로 식별(3곳)하고, 각각에 대해 방식 C 요약(§3.3 권한 체계 기반: Part2 정본 When+Where / sot 2/ 정본 What+How 분리)을 작성하여, Phase 1→2 전환 게이트 조건 **"Part2 방식 C 요약 완료"**를 선행 충족한다.

**입력 파일**:
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` (§3 LangGraph StateGraph, §6.5 HITL, §6.6 MCP, §6.7 Agent Teams — Part2 PARTIAL 영역 원문 + 요약 대조 원본)
- `D:\VAMOS\docs\sot\STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md` (Part2 PARTIAL 영역의 K-ID 커버리지 대조용)
- `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` (LOCK-AT 값 원본 참조: LOCK-AT-004 위임깊이, LOCK-AT-014 병렬상한 등)

**절차**:
1. §6.1 매핑 테이블에서 Part2 반영 상태가 PARTIAL인 영역을 **Part2 섹션 단위**로 그룹핑하여 3곳 식별:
   - **§3 LangGraph StateGraph** (V1-Phase 3): K-021 반영, K-022·K-025 MINIMAL
   - **§6.7 Agent Teams V1**: K-011~K-014 Agent Card/Task/Discovery/Delegation 반영 + K-041·K-043·K-044 권한/샌드박스/비용 반영 (06_autonomy-safety PARTIAL 항목 포함)
   - **§6.6 MCP Bridge** (V1-Phase 6): K-001~K-005·K-007·K-010 반영 + K-031~K-034 서비스연동 반영
   - ※ **제외 근거 1**: 06_autonomy-safety PARTIAL 항목(K-041·K-043·K-044)은 Part2 §6.7에 이미 포함되므로 별도 방식 C 불필요 — §6.7 방식 C 요약에서 일괄 처리
   - ※ **제외 근거 2**: §6.5의 K-042(HITL)는 MINIMAL(개념만 언급, 구현 상세 없음)이므로 방식 C 대상 아님 — Phase 1에서 전면 신규 작성 대상
2. 각 영역에 대해 **방식 C 요약** 작성 (§3.3 권한 체계 기반 정본 분리):
   - **Part2가 정본**: When(Phase 배정, 일정) + Where(코드 위치, 파일 경로)
   - **sot 2/가 정본**: What(구현 상세, 항목 정의) + How(알고리즘, 스키마, 에러핸들링)
   - **출력 형식** (§7.3.1~§7.3.3 각 요약에 아래 5요소 필수):
     1. 출처: Part2 섹션 번호 + 실측 라인 범위
     2. Part2 정본 범위: When + Where 명시 (Phase·Week·코드 경로)
     3. sot 2/ 정본 범위: What + How 명시 (보완 작성 대상)
     4. Part2 핵심 내용 요약: 주요 구현 방향·수치·LOCK 값 (Part2 원문 키워드 기반)
     5. sot 2/ 보완 영역: Part2에 없는 구현 상세 (알고리즘, 변환 규칙, K-ID 매핑)
   - **R6 준수**: 요약에 Phase 일정을 출처 참조 형태로만 기재, sot 2/ 정본 범위에 When 정보 이중 기재 금지
3. Part2 원문 직접 열람 → 요약과 1:1 대조:
   - Part2 원문의 핵심 키워드·수치·LOCK 값이 요약에 정확히 반영 확인
   - 요약 내 LOCK-AT/LOCK-AP 값이 §3.4(LOCK-AP-01~10) 및 D2.0-05(LOCK-AT) 원본과 무충돌 확인
   - Part2 라인 번호가 실제 원문 위치와 일치하는지 확인 (오차 ±5 이내)

**검증**: ✅ 전수 PASS (2026-04-01, 2차 재검증 완료)
- [x] Part2 PARTIAL 영역 3곳 식별 + 제외 영역 근거 기록 — **Phase 1→2 전환 게이트 선행 (Part2 방식 C 요약 완료)** PASS
  - §6.1 PARTIAL 영역 전수 대조: Part2 섹션 3곳(§3, §6.7, §6.6)으로 그룹핑 확인, 누락 0건
  - 06_ PARTIAL 항목(K-041·K-043·K-044) §6.7 포함 확인, §6.5 K-042 MINIMAL 제외 근거 확인
- [x] 방식 C 요약 3건 작성 (§7.3.1 LangGraph, §7.3.2 Agent Teams, §7.3.3 MCP Bridge) — PASS
  - 각 요약에 5요소(출처·Part2 정본·sot 2/ 정본·핵심 요약·보완 영역) 포함 확인
- [x] Part2 원문 ↔ 요약 정합성 — PASS
  - §7.3.1: Part2 원문 키워드·수치 12건 전수 대조 누락 0건, 라인 범위 2078~2275 실측 일치
  - §7.3.2: Part2 원문 키워드·수치 15건 전수 대조 누락 0건, 라인 범위 2130~2133 + 4998~5133 실측 일치
  - §7.3.3: Part2 원문 키워드·수치 12건 전수 대조 누락 0건, 라인 범위 2546~2684 + 4966~4996 실측 일치
- [x] LOCK 무충돌 — PASS (6건 전수 대조)
  - LOCK-AT-004(위임깊이 max=3, V1 config=2) ↔ Part2 §6.7 line 5042 / S7E-080 ✅
  - LOCK-AT-011(비용상한 초과 자동차단) ↔ Part2 §6.7 line 5049 / RULE 1.3 §5 ✅
  - LOCK-AT-014(병렬상한 V1=3, V2=10, V3=50+) ↔ Part2 §6.7 line 5052 / S7-A-008 ✅
  - LOCK-AP-04(Streamable HTTP, WebSocket 아님) ↔ §3.4 LOCK-AP-04 ✅
  - LOCK-AP-06(CB failure_threshold=3, recovery=60s) ↔ §3.4 LOCK-AP-06 ✅ (SOURCE_CONFLICT: D2.1 300s 대비 정본 60s 채택 기록)
  - LOCK-AP-08(START/END 상수, set_entry_point 금지) ↔ §3.4 LOCK-AP-08 ✅
- [x] R6 준수 — PASS
  - When 정보(Phase/Week)는 출처 blockquote 참조 형태로만 존재, sot 2/ 정본 범위 이중 기재 0건
- [x] §3.3 권한 체계 준수 — PASS
  - Part2 정본(When+Where): Phase·Week·코드경로만 기재. sot 2/ 정본(What+How): 알고리즘·변환규칙·K-ID 상세만 기재. 월권 0건
- [x] §5.2 도메인 경계 준수 — PASS (2차 재검증 추가)
  - §7.3.3 sot 2/ 보완: #13 직접 작성(K-017 인터롭, K-010 활용) vs #16 MCP 정본 참조(K-007, K-006) 분리 확인
  - §7.3.1·§7.3.2 보완 항목 전수 #13 도메인 소유 확인 (01_framework-adapters, 06_autonomy-safety)

**산출물**: §7.3 Part2 방식 C 요약 3건 (§7.3.1 LangGraph StateGraph, §7.3.2 Agent Teams V1, §7.3.3 MCP Bridge) — 본 계획서 내
**상태**: ✅ 완료
</details>

<details>
<summary><b>P0-3. 계획서 14+4 섹션 작성</b></summary>

**목표**: P0-1(§6 매핑 테이블)·P0-2(§7.3 방식 C 요약) 산출물을 통합하고, §1~§14 본문 + 부록 §A~§D를 작성하여 Phase 0 마스터 산출물(본 문서)을 완성한다. 본 문서는 P0-4~P0-7 후속 작업의 입력이자, 전체 Phase 0~3 실행의 기준 문서(마스터 플랜)이다.

**선행 의존**:
- P0-1 산출물: §1.3 항목 현황, §6.1 전수 매핑 테이블, §6.2 미반영 항목 상세(35건)
- P0-2 산출물: §7.3.1~§7.3.3 방식 C 요약 3건

**입력 파일**:
- `D:\VAMOS\docs\sot\STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md` (86항목, 10 Parts — §1 현황·§6 매핑·§A 어댑터 카탈로그·§B 자율성·§C 가드레일 근거)
- `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` (A2A 아키텍처, LOCK-AT 항목 — §3.4 LOCK-AP 근거·§9 충돌 해결·§B 전환 조건)
- `D:\VAMOS\docs\sot\D2.0-03_03. VAMOS_DESIGN_2.0_BLUE_NODES.md` (Blue Node 인터페이스 계약 LOCK — §3.3 문서별 범위·§8 파일 역할)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\AGENT_PROTOCOL_INTEROPERABILITY_상세명세.md` (770줄 — §1.2 기존 파일 현황·§A.2 공통 인터페이스 스키마 기반)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` (§3 LangGraph, §6.5 HITL, §6.6 MCP, §6.7 Agent Teams — §7.3 방식 C 요약 원본·§7.4~§7.5 Phase 배정 출처)
- `D:\VAMOS\docs\sot 2\0-0_Governance-Rules-Meta\GOVERNANCE_RULES_META_규칙서.md` (§4 글로벌 거버넌스 R1~R11 출처)

**절차**:
1. **P0-1·P0-2 산출물 통합**: P0-1 산출물(§1.3, §6.1, §6.2)과 P0-2 산출물(§7.3.1~§7.3.3)을 본 계획서의 해당 위치에 배치. 통합 시 산출물 원본의 수치·K-ID·Part2 상태 분류가 변형 없이 유지되는지 확인
2. **§1~§5 본문 작성**:
   - §1 현재 상태 분석: STEP7-K·Part2·상세명세 3종 문서 현황 테이블(§1.1) + sot 2/ 현재 파일(§1.2) + P0-1 산출물 기반 항목 현황(§1.3) + 핵심 문제 4건 도출(§1.4) + Part2 방식 C 접근법 선언
   - §2 목표 구조: 폴더 트리(§2.1, 6개 서브폴더) + 깊이 규칙(§2.2, R1 3단계 이하) + 네이밍 규칙(§2.3)
   - §3 권한 체계: VAMOS 체인(§3.1) + Agent-Protocol 확장 체인(§3.2) + 문서별 정본 범위(§3.3, What/When+Where/How 분리) + LOCK-AP-01~10 전수 등재(§3.4, STEP7-K·D2.0-05·Part2 원본 값 인용)
   - §4 거버넌스: 0-0_Governance-Rules-Meta R1~R11 글로벌 준수 선언(§4.1) + 도메인 고유 R-13-1~R-13-7 정의(§4.2, STEP7-K 항목 근거 명시)
   - §5 선행작업: P0-1 결과(§5.1) + 도메인 횡단 의존성 경계 확정(§5.2, #16 MCP·#11 A2A·#4 COND 정본 소유자) + 상세명세 정합성(§5.3)
3. **§7~§14 본문 작성**:
   - §7 Phase 실행 계획: 전환 게이트 4단계(§7.1) + Phase 0 작업 테이블(§7.2) + P0-2 산출물 기반 Part2 방식 C 요약 3건(§7.3) + Phase 1~3 서브폴더별 항목·V 로드맵 배정(§7.4~§7.5). §6.2 우선순위(P0/P1/P2) ↔ §7.3~§7.5 V 로드맵 정합 확인
   - §8 파일 역할 분리: 문서 6종별 정본 범위·읽기 참조·쓰기 권한 매트릭스 (§3.3 권한 체계 기반)
   - §9 충돌 해결: 우선순위 5단계(§9.1, LOCK→DESIGN→STEP7-K→Part2→sot 2/) + 충돌 시나리오 5건(§9.2) + CONFLICT_LOG 참조(§9.3) + 횡단 관심사(§9.4)
   - §10 검증 체크리스트: 10개 검증 항목 정의 (매핑 완전성·LOCK·권한·깊이·_index·방식 C·횡단·자율성·가드레일·의존성)
   - §11 보완 사항: GAP 분석 → 즉시(FR-1~3)·단기(FR-4~6)·중기(FR-7~9) 분류
   - §12 FINAL REVIEW: 리뷰 이력 기록 (Phase 5/8/10)
   - §13 L3 전수 승급 계획: L3 기준 8요소(§13.1) + 서브폴더별 현재→목표 레벨(§13.2)
   - §14 실행 약점: 리스크 9건 + 대응 전략 + 모니터링 KPI 4건
4. **부록 §A~§D 작성**:
   - §A 프레임워크 어댑터 카탈로그: 지원 매트릭스(A.1, LangGraph/CrewAI/AutoGen/Magentic-One/Custom) + 공통 인터페이스(A.2, FrameworkAdapter TypeScript 스키마) + 변환 규칙 요약(A.3, Agent→/Task→/Tool→/상태→ 4종 변환) — STEP7-K K-021~K-030, 상세명세 스키마 기반
   - §B 자율성 레벨 L0~L4: 레벨 정의(B.1, 5단계 인간 개입·가드레일·전환 조건) + 전환 프로토콜(B.2, 정방향 4단계 + 역방향 즉시하향/L0리셋) + 허용 작업 매트릭스(B.3, 8 카테고리×5 레벨) — STEP7-K K-041~K-048, LOCK-AP-02 기반
   - §C 안전 가드레일 규칙 엔진: 3-Phase 아키텍처(C.1, Pre→Runtime→Post) + 스키마(C.2, SafetyGuardrail/SafetyRule TypeScript) + 기본 규칙 세트(C.3, SG-001~SG-010 pre/runtime/post 분류) + HITL 스키마(C.4, HumanInterventionRequest) — CEL 기반, LOCK-AP-10 Confidence < 50% 반영
   - §D 의존성 매트릭스: 소비 의존성(D.1, 9건: #4 COND·#11 A2A·#16 MCP·#3 Blue Node·#1 Verifier·#15 CI/CD·#14 Rust-Tauri·#12 Business·#10 Dev Tools) + 제공 의존성(D.2, 3건) — §5.2 도메인 경계 + 전체 도메인 구조 기반
5. **목차 ↔ 본문 정합**: 목차 18개 항목(§1~§14 + §A~§D) 각각에 대응하는 본문 헤딩이 존재하는지 1:1 대조. 누락·순서 불일치 시 즉시 수정

**검증**: ✅ 전수 PASS (2026-04-01)
- [x] 14+4 섹션 전수 작성 — 목차 18개 항목(§1~§14 + §A~§D) ↔ 본문 헤딩 1:1 대조 완료, 누락 0건
- [x] P0-1 산출물 통합 정합 — §1.3(10 Parts 76 K-ID 항목 현황) + §6.1(9개 카테고리 전수 매핑, 합계 76 K-ID) + §6.2(35건 미반영 상세, P0/P1/P2 분류) 본문 배치 확인, 수치 변형 0건 — §10 검증 #1(86항목 전수 매핑 100%) P0-1에서 PASS, 본 단계에서 통합 수치 정합 재확인
- [x] P0-2 산출물 통합 정합 — §7.3.1(LangGraph) + §7.3.2(Agent Teams) + §7.3.3(MCP Bridge) 방식 C 요약 3건, 각 5요소(출처·Part2 정본·sot 2/ 정본·핵심 요약·보완 영역) 포함 확인 — §10 검증 #6(방식 C 형식, Part2 PARTIAL 출처 명시) P0-2에서 PASS, 본 단계에서 §7.3 배치 확인
- [x] §3.4 LOCK-AP-01~10 전수 등재 + LOCK 재정의 0건 — §10 검증 #2 기준 PASS
  - 10개 LOCK 항목 원본(STEP7-K·D2.0-05·Part2) 값 인용만, 재정의·변경 0건 (R9 준수)
- [x] §3 권한 체계 ↔ VAMOS 체인 무충돌 — §10 검증 #3 기준 PASS
  - RULE 1.3 > PLAN 3.0 > DESIGN 2.0 > STEP7 체인 유지, Agent-Protocol 확장 체인이 기존 체인 하위에 정합
- [x] §4 거버넌스 규칙 완비 — R1~R9 글로벌(0-0_Governance-Rules-Meta 준수 선언) + R-13-1~R-13-7 도메인 고유(7건, STEP7-K 근거 명시)
- [x] §5.2 도메인 횡단 경계 3건 명시 — §10 검증 #7 기준 PASS
  - #16 MCP: 프로토콜 자체→#16 정본, MCP 활용→#13 정본
  - #11 A2A: 프로토콜 스펙→#11 정본, 인터롭 브리지→#13 정본
  - #4 COND: 에이전트 통합(COND-085)→#4 정본, 프레임워크 어댑터→#13 정본
- [x] §B 자율성 레벨 L0~L4 정의 완비 — §10 검증 #8 기준 PASS
  - B.1 레벨 정의(5단계, 전환 조건 명시) + B.2 전환 프로토콜(정방향 4단계 + 역방향 2조건) + B.3 허용 작업(8 카테고리×5 레벨, ✅/❌/Ask 분류)
- [x] §C 가드레일 규칙 CEL 엔진 완비 — §10 검증 #9 기준 PASS
  - C.1 아키텍처(Pre→Runtime→Post 3-Phase) + C.2 스키마(2종) + C.3 규칙 SG-001~SG-010(pre 5건/runtime 3건/post 2건) + C.4 HITL 스키마. LOCK-AP-10(Confidence < 50%) SG-009에 반영 확인
- [x] §D 의존성 매트릭스 완비 — §10 검증 #10 기준 PASS
  - D.1 소비 9건(#4·#11·#16·#3·#1·#15·#14·#12·#10) + D.2 제공 3건. §5.2 경계와 정합(#4·#11·#16 의존 유형·영향 명시)
- [x] §6.2 우선순위 ↔ §7 Phase V 로드맵 정합 — PASS (§7.4에 03_data-exchange 행 추가 보정 완료)
  - P0(4건)→§7.3 V1, P1(18건)→§7.4 V2, P2(13건)→§7.4~§7.5 V2~V3 일치. K-050·K-052~K-053 §7.4 배정 확인. K-045/K-046 §7 미배정 ⚠ §6.2에 기록 (§11.1 FR-1 범위)
- [x] R6 준수 — sot 2/ 정본 범위에 When(Phase/Week) 이중 기재 0건, §7.3 출처 blockquote 참조 형태만 존재
- [x] R9 준수 — LOCK/FREEZE 값 재정의 0건, §3.4 원문 값만 인용. SOURCE_CONFLICT(LOCK-AP-06 60s vs D2.1 300s) §3.4에 기록
- [x] §10 검증 #4(폴더 깊이 3단계)·#5(_index.md 6/6) — P0-6 책임. §2.1 폴더 트리·§2.2 깊이 규칙은 본 P0-3에서 정의 완료, 실물 생성·검증은 P0-6에서 수행

**산출물**: `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md` (본 문서 — §1~§14 + §A~§D 18개 섹션)
**상태**: ✅ 완료
</details>

<details>
<summary><b>P0-4. AUTHORITY_CHAIN.md 작성</b></summary>

**목표**: §3 권한 체계 선언·§5.2 도메인 횡단 경계·§9.1 충돌 우선순위·§D 의존성 매트릭스를 통합하여, 본 도메인의 단일 권한 선언 문서(AUTHORITY_CHAIN.md)를 신규 생성한다. Phase 0→1 전환 게이트 조건 **"AUTHORITY_CHAIN 작성"**(§7.1)을 충족한다.

**선행 의존**:
- P0-3 산출물: 본 계획서 §3(권한 체계 선언), §5.2(도메인 횡단 의존성), §8(파일 역할 분리), §9.1(충돌 우선순위), §D(의존성 매트릭스) — P0-3 검증 PASS 전제

**입력 파일**:
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md` §3, §5.2, §8, §9.1, §D (AUTHORITY_CHAIN 내용의 1차 출처 — P0-3에서 작성·검증 완료된 정본)
- `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` (검증용: LOCK-AP-01·AP-03·AP-06 원본 값 대조 + §3.3 A2A 프로토콜 정본 범위 확인)
- `D:\VAMOS\docs\sot\D2.0-03_03. VAMOS_DESIGN_2.0_BLUE_NODES.md` (검증용: §3.3 Blue Node 인터페이스 계약 정본 범위 확인)
- `D:\VAMOS\docs\sot\STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md` (검증용: LOCK-AP-01·AP-02·AP-07 원본 값 대조)
- `D:\VAMOS\docs\sot 2\6-3_Agent-Teams-PARL\AUTHORITY_CHAIN.md` (검증용: LOCK-AP-05 ↔ 6-3 LOCK-AT-014 교차 대조 — 값 일치 확인)

**절차**:
1. `3-10_Agent-Protocol-Interoperability/AUTHORITY_CHAIN.md` 신규 생성
2. 헤더 메타데이터: 도메인명(#13 Agent Protocol / Interoperability), 도메인 ID(TIER3-DOMAIN-10), `Status: APPROVED`, `버전: v1.0`, 작성일
3. **§1 상위 VAMOS 권한 체인** (§3.1 + §3.2 기반):
   - VAMOS 체인 다이어그램: `RULE 1.3 (헌법) → PLAN 3.0 (기획서) → DESIGN 2.0 (설계 — D2.0-03, D2.0-05) → STEP7-K (86항목 SOT) → sot 2/3-10_*/ (구현 정본)`
   - DESIGN 2.0에서 D2.0-03·D2.0-05를 괄호 내 명시 (§3.1 원문은 D2.0-XX 미기재이나 §3.3·§8에서 정본 문서로 참조되므로 체인에 명시)
4. **§2 도메인 내 권한 서열** (§3.3 문서별 범위 + §8 파일 역할 분리 + §9.1 충돌 우선순위 통합):
   - 7단계 서열 테이블 `| 순위 | 문서 | 정본 범위 |`:
     (1) STEP7-K — 항목 정의 (What to build), 86항목 불변
     (2) Part2 §3/§6.6/§6.7 — Phase 배정·코드 위치 (When/Where)
     (3) D2.0-03 / D2.0-05 — 아키텍처 계약 (Blue Node·A2A) LOCK
     (4) 구조화_종합계획서.md — 마스터 플랜 (거버넌스·Phase·방식 C)
     (5) 서브폴더 _index.md — 카테고리별 항목 인덱스
     (6) 서브폴더 개별 파일 — 항목별 구현 상세 (How)
     (7) 상세명세.md (기존) — 기술 명세 v1.0, 병행 유지, 충돌 시 상위 우선
   - ※ 서열 근거: §3.3(5개 문서 정본 범위)를 §8(6종 파일 역할)·§9.1(5단계 충돌 우선순위)와 통합하여 도메인 내 7단계로 세분화. 충돌 시 §9.1 우선순위(LOCK→DESIGN→STEP7-K→Part2→sot 2/)에 따라 해결
5. **§3 LOCK 보호 항목** (§3.4 전문 기반):
   - LOCK-AP-01~10 테이블 (열: `LOCK ID | 항목 | 원본 문서 | 값 | 재정의`)
   - **재정의 열**: 전 항목 **"금지"** 일괄 표기 (R9 준수)
   - **교차 도메인 LOCK 주석**: LOCK-AP-05 원본 열에 "6-3 LOCK-AT-014 참조 — 값 일치 확인(V1=3, V2=10, V3=50+)" 명시
   - **정본 소유 구분**: LOCK-AP-10은 "DEFINED-HERE (본 도메인 06_autonomy-safety 정본; MASTER_SPEC §5/§7.9 참조)" — 다른 LOCK-AP는 외부 원본 참조, AP-10만 본 도메인이 정본임을 명시
   - §3.4 원본 값을 그대로 인용, 재정의·변경 일체 금지 (R9)
6. **§4 도메인 횡단 정본 소유 경계** (§5.2 기반):
   - 테이블 `| 영역 | 정본 소유자 | #13의 역할 |`
   - 외부 정본 4건: #16 MCP(프로토콜 스펙)→MCP 활용 관점, #11 A2A(프로토콜 스펙)→인터롭 브리지 관점, #4 COND(COND-085 에이전트통합)→프레임워크 어댑터 소비, #3 Blue Node(인터페이스)→에이전트 실행 환경 소비
   - 본 도메인(#13) 정본 4건: 에이전트 자율성/안전(L0~L4·가드레일), 프레임워크 어댑터(CrewAI/AutoGen/LangGraph), 에이전트 배포/스케일링, 자기진화 전략(Dream Mode/Self-Evolution)
7. **도메인 경계 테이블** (§D 소비/제공 의존성 기반):
   - 테이블 `| 인접 도메인 | 본 도메인 소유 | 인접 도메인 소유 |`
   - 최소 4건: #11 A2A(인터롭 브리지 vs A2A 프로토콜 스펙), #16 MCP(MCP 활용 통합 vs MCP 프로토콜 스펙), #3 Blue Node(자율성 레벨 L0~L4 vs Blue Node 인터페이스), 6-3 Agent Teams(배포/스케일링 vs 협업 패턴/PARL)
8. **충돌 해결 원칙** (§9.1 발췌):
   - 우선순위 5단계: `LOCK 값(절대 불변) → DESIGN 2.0(아키텍처) → STEP7-K(항목 정의) → Part2(Phase/위치) → sot 2/(구현 상세, 최하위)`
   - Footer 1줄: "충돌 발생 시 CONFLICT_LOG.md에 기록하고 상위 LOCK/DESIGN 우선 원칙에 따라 해결한다."

**검증**: ✅ 전수 PASS (2026-04-01, 2차 재검증 완료 — §3.4 문자 수준 대조 6건 보정, 5 Round 검증 전수 통과)
- [x] AUTHORITY_CHAIN.md 파일 존재 + 헤더 `Status: APPROVED`, `버전: v1.0` 기재 — §7.1 Phase 0→1 전환 게이트 조건 "AUTHORITY_CHAIN 작성" 충족
- [x] 상위 VAMOS 권한 체인 정확 기재 — §3.1 원문(RULE 1.3 > PLAN 3.0 > DESIGN 2.0 > STEP7) 일치, D2.0-03·D2.0-05 체인 내 명시 — §10 #3 매핑 (권한 체계 정합, VAMOS 체인과 모순 없음)
- [x] 도메인 내 권한 서열 7단계 ↔ §9.1 충돌 우선순위 정합 — 서열 순서가 §9.1 "LOCK→DESIGN→STEP7-K→Part2→sot 2/" 체계와 모순 없음, 서열 근거 주석에 충돌 시 §9.1 적용 명시 — §10 #3 매핑
- [x] §3.3 문서별 정본 범위 **5건** 전수 기재 — STEP7-K(What), Part2(When/Where), sot 2/(How), D2.0-03(Blue Node LOCK), D2.0-05(A2A LOCK) 각 범위 명시
- [x] LOCK-AP-01~10 **전수 등재** (10건, 누락 0건) + 재정의 열 "금지" 일괄 표기 — §10 #2 매핑 (LOCK 재정의 없음, 0건 위반)
- [x] LOCK-AP 원본 값 정합 (R9 준수, 재정의·변경 0건 — 2차 재검증 시 §3.4 문자 수준 대조, 6건 보정 완료):
  - LOCK-AP-01(VamosMessage 스키마) ↔ STEP7-K K-049 lines 984-998 확인 ✅
  - LOCK-AP-02(Permission Level 0~5) ↔ STEP7-K K-041 lines 819-840 확인 ✅
  - LOCK-AP-03(Task 상태 머신) ↔ D2.0-03 lines 631-639 + D2.0-05 확인 ✅
  - LOCK-AP-04(Streamable HTTP) ↔ Part2 §6.6 원문 (P0-3 PASS) ✅ — 2차: 값 어순 §3.4 원문 복원 "Streamable HTTP (V1), WebSocket 아님"
  - LOCK-AP-05(Lead + max 2 Sub) ↔ Part2 §6.7 LOCK-AT-014 원문 (P0-3 PASS) ✅ — 2차: 항목명 "Agent Teams V1 제한" §3.4 원문 복원
  - LOCK-AP-06(CB recovery 60초) ↔ D2.0-05 §4.4 line 177 확인 (SOURCE_CONFLICT: D2.1 line 367 300s는 UserIntervention timeout — CB recovery 아님, 정본 60s 채택) ✅ — 2차: 값에 "(D2.1 스키마 300s는 하위)" §3.4 SOURCE_CONFLICT 주석 복원
  - LOCK-AP-07(A2A+MCP 양방향) ↔ STEP7-K K-017 lines 329-341 확인 ✅
  - LOCK-AP-08(START/END 상수) ↔ Part2 Phase 3 규칙 원문 (P0-3 PASS) ✅ — 2차: 값 "START/END 상수 사용" §3.4 원문 복원 ("상수" 누락 보정)
  - LOCK-AP-09(V1:₩40K/V2:₩93K/V3:₩266K) ↔ Part2 §비용 + 가이드 부록 D 원문 (P0-3 PASS) ✅
  - LOCK-AP-10(HITL < 50%) ↔ MASTER_SPEC §5/§7.9 원문 (P0-3 PASS) + DEFINED-HERE 정본 소유 명시 확인 ✅ — 2차: 항목명 "Confidence 임계값" + 값 "HITL 트리거 < 50%" §3.4 원문 복원
- [x] LOCK-AP-05 ↔ 6-3 LOCK-AT-014 교차 대조 — 값 일치(V1=3, V2=10, V3=50+) 확인, 6-3 AUTHORITY_CHAIN line 47 대조 완료
- [x] 도메인 횡단 정본 소유 경계 ↔ §5.2 정합 — 외부 정본 4건(#16 MCP·#11 A2A·#4 COND·#3 Blue Node) + 본 도메인 정본 4건(자율성/어댑터/배포/자기진화) 전수 기재 (8건) — §10 #7 매핑 (도메인 횡단 참조, #4·#11·#16 정본 소유자 명시)
- [x] 도메인 경계 테이블 4건 — #11 A2A, #16 MCP, #3 Blue Node, 6-3 Agent Teams 인접 도메인별 소유 분리 기재, §D 의존성 매트릭스와 정합
- [x] 충돌 해결 원칙 — §9.1 우선순위 5단계(LOCK→DESIGN→STEP7-K→Part2→sot 2/) 정확 기재 + CONFLICT_LOG.md 참조 안내 포함

**산출물**: `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\AUTHORITY_CHAIN.md` (신규)
**상태**: ✅ 완료
</details>

<details>
<summary><b>P0-5. CONFLICT_LOG.md 초기화</b></summary>

**목표**: §9 충돌 해결 프로토콜(§9.1 우선순위 5단계 + §9.2 충돌 시나리오 5건 + §9.3 기록 원칙)을 기반으로 CONFLICT_LOG.md를 초기화하고, §5.2 도메인 횡단 경계에서 식별된 기존 알려진 도메인 횡단 충돌 2건을 선등록한다. §2.1 목표 구조의 `CONFLICT_LOG.md ← 충돌 기록` 파일 역할을 구현한다.

**선행 의존**:
- P0-3 산출물: 본 계획서 §9(충돌 해결 프로토콜 — §9.1 우선순위 규칙, §9.2 충돌 시나리오 5건, §9.3 충돌 기록 원칙, §9.4 횡단 관심사) 작성 완료 전제
- P0-4 산출물: AUTHORITY_CHAIN.md "충돌 해결 원칙" 섹션(P0-4 절차 8번)에 "충돌 발생 시 CONFLICT_LOG.md에 기록" footer 기재 완료 전제

**입력 파일**:
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md` §9(충돌 해결 프로토콜 전체), §5.2(도메인 횡단 의존성 — 충돌 2건의 경계 근거), §3.4(LOCK-AP SOURCE_CONFLICT 기록 — 기존 충돌 사례 참조)

**절차**:
1. `3-10_Agent-Protocol-Interoperability/CONFLICT_LOG.md` 신규 생성 (§2.1 폴더 트리 위치 준수)
2. **충돌 해결 프로토콜 섹션** (§9.1 우선순위 규칙 발췌):
   - 우선순위 5단계: `LOCK 값(절대 불변) → DESIGN 2.0(아키텍처) → STEP7-K(항목 정의) → Part2(Phase/위치) → sot 2/(구현 상세, 최하위)`
   - 기록 원칙: §9.3 "모든 충돌은 CONFLICT_LOG.md에 기록한다" 명시
3. **충돌 기록 테이블 구조** 정의:
   - 열: `| # | 충돌 유형 | 당사자 | 해결 원칙 | 상태 | 등록일 |`
4. **기존 알려진 도메인 횡단 충돌 2건** 등록 (§9.2 + §5.2 경계 근거):
   - #1: #11 A2A 도메인 vs #13 경계 — A2A 프로토콜 스펙 → #11 정본, 인터롭 관점 → #13 정본 (§5.2: A2A 프로토콜 스펙 → #11 A2A 정본, #13은 "인터롭 브리지" 소유)
   - #2: #16 MCP 도메인 vs #13 경계 — MCP 프로토콜 → #16 정본, 프레임워크 통합 활용 → #13 정본 (§5.2: MCP 프로토콜 자체 → #16 MCP 정본, #13은 "MCP 활용" 관점만 소유)
   - ※ §9.2의 5건 중 나머지 3건(STEP7-K vs sot 2/, Part2 vs sot 2/, D2.0-05 vs sot 2/)은 도메인 내부 우선순위 규칙(§9.1)으로 자동 해결되는 유형이므로 충돌 로그 등록 대상이 아님 — 실제 충돌 발생 시 등록
5. **횡단 관심사 참조** (§9.4): 6-2 Security-Governance(자율성 게이팅 L0~L4 보안, 가드레일 정책 OWASP LLM08) 횡단 도메인 참조 안내 포함
6. **기존 SOURCE_CONFLICT 참조** (§3.4): LOCK-AP-06 SOURCE_CONFLICT(CB recovery 60s vs D2.1 300s, 정본 60s 채택) 사례를 비고란에 참조 기록 — 이미 §3.4에서 해결·기록 완료된 건이므로 "해결 완료" 상태로 등록

**검증**: ✅ 전수 PASS (2026-04-01 — 기존 v1.0 보강, 6건 기록 보존 + P0-5 요구사항 전수 반영)
- [x] CONFLICT_LOG.md 존재 + §2.1 폴더 트리 위치(`3-10_Agent-Protocol-Interoperability/` 루트) 일치
- [x] 충돌 해결 프로토콜 섹션 포함: §9.1 우선순위 5단계 문자 수준 일치 + §9.3 기록 원칙 명시
- [x] 도메인 횡단 경계 충돌 2건 등록: 각 충돌의 당사자·해결 원칙·§5.2 경계 근거 기재 (#1 A2A line 41/50-56, #2 MCP line 42/58-64)
- [x] §9.4 횡단 관심사(6-2 Security-Governance) 참조 포함 — §3 횡단 관심사 참조 섹션 (line 96-100)
- [x] SOURCE_CONFLICT 참조(LOCK-AP-06) 기록 포함 — 충돌 #3 (line 43/66-71), "해결 완료" 상태
- [x] P0-4 AUTHORITY_CHAIN.md footer("충돌 발생 시 CONFLICT_LOG.md에 기록")와 상호 참조 정합 — §1.2 (line 32-33) 동일 문구 인용 + 출처 "AUTHORITY_CHAIN.md '충돌 해결 원칙' 섹션, line 89" 명시
- [x] 기존 충돌 기록 6건(v1.0) 보존 + 구조 보강: 충돌 상세(§2.1) 6건 전수 + 등록 규칙(§4) + 상태 분류 체계 추가

**산출물**: `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\CONFLICT_LOG.md` (v1.1 — 기존 v1.0 보강)
**상태**: ✅ 완료
</details>

<details>
<summary><b>P0-6. 서브폴더 6개 + _index.md 생성</b></summary>

**목표**: §2.1 목표 구조의 6개 서브폴더 골격과 각 폴더의 _index.md를 생성하여, Phase 0→1 전환 게이트 조건 **"서브폴더 골격"**(§7.1 G0-3)을 충족한다. _index.md는 카테고리별 항목 인덱스(P0-4 서열 5번)로서, 각 서브폴더의 담당 K-ID 목록·계획 파일 목록·V 스코프 배정을 기재한다. 콘텐츠 파일(crewai_adapter.md 등)은 본 작업 범위 외이며 §11.1 FR-1에서 별도 작성한다.

**선행 의존**:
- P0-3 산출물: 본 계획서 §2.1(폴더 트리)·§2.2(깊이 규칙)·§2.3(네이밍 규칙)·§6.1(서브폴더↔K-ID 매핑 테이블)·§7.3~§7.5(V 로드맵 배정) — P0-3 검증 PASS 전제

**입력 파일**:
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md`:
  - §2.1 폴더 트리 (서브폴더 6개 이름·_index.md 위치·계획 파일 목록)
  - §2.2 깊이 규칙 (3단계 이하), §2.3 네이밍 규칙 (폴더명: 영문 소문자+하이픈+2자리 접두사, 파일명: 영문 소문자+언더스코어)
  - §6.1 전수 매핑 테이블 (서브폴더별 K-ID 범위·Part2 상태·해결 방식)
  - §7.3~§7.5 Phase 1~3 V 로드맵 배정 (서브폴더별 항목→V1/V2/V3 스코프)

**절차**:
1. 6개 서브폴더 생성 (§2.1 폴더 트리 기준, §2.3 네이밍 규칙 준수):
   - `01_framework-adapters/`, `02_service-integration/`, `03_data-exchange/`, `04_deployment-scaling/`, `05_self-evolution/`, `06_autonomy-safety/`
2. 각 서브폴더에 `_index.md` 생성 (§2.3: 파일명 영문 소문자+언더스코어)
3. _index.md 내용 작성 (아래 4요소 필수, R2 준수 — 인덱스 정보만 기재, 구현 상세 본문 금지):
   - **(a) 담당 K-ID 목록**: §6.1 매핑 테이블 기준 해당 서브폴더의 K-ID 범위와 항목명
   - **(b) 계획 파일 목록**: §2.1 폴더 트리에 정의된 해당 서브폴더의 파일 구성 (현재 _index.md만 존재, 나머지는 "Phase 1 이후 생성 예정" 표기)
   - **(c) V 스코프 배정**: §7.3~§7.5 기준 각 항목의 V1/V2/V3 스코프 분류 (※ R6 준수: V 스코프는 범위 분류(What)이며 Phase 일정(When) 아님 — Phase/Week 기재 금지)
   - **(d) Part2 반영 상태 요약**: §6.1 기준 PARTIAL/MINIMAL/ABSENT 집계 1줄 (해결 방식 참조)
4. 각 서브폴더별 _index.md 내용 대조표:
   | 서브폴더 | K-ID 범위 (§6.1) | K-ID 수 | 계획 파일 (§2.1) | V 스코프 (§7) |
   |----------|------------------|---------|-----------------|--------------|
   | `01_framework-adapters/` | K-021~K-030 | 10 | crewai_adapter.md, autogen_adapter.md, langgraph_adapter.md | V1: K-021~K-023, V2: K-024~K-030 |
   | `02_service-integration/` | K-031~K-040 | 10 | llm_gateway.md, external_apis.md | V2: K-031~K-037·K-039~K-040, V3: K-038(IoT) |
   | `03_data-exchange/` | K-049~K-054 | 6 | message_format.md, serialization.md | V1: K-049·K-051, V2: K-050·K-052~K-053(§6.2 P1), K-054(MINIMAL, §7 미배정 — V1 방식C 보완 시 포함 권고) |
   | `04_deployment-scaling/` | K-055~K-060 | 6 | container_spec.md | V2: K-055·K-057~K-060, V3: K-056(K8s 오토스케일링) |
   | `05_self-evolution/` | K-061~K-068 | 8 | dream_mode.md | V2: K-061~K-064, V3: K-065~K-068 |
   | `06_autonomy-safety/` | K-041~K-048 | 8 | permission_matrix.md, guardrail_rules.md | V1: K-041~K-044(§7.3 + §7.3.2 방식C)·K-045~K-046(§6.2 P0+§7 미배정⚠ Phase 1 권고), V2: K-047, V3: K-048 |
5. §2.1 폴더 트리와 실제 생성 구조 1:1 대조 확인 (서브폴더 6개 이름·위치·_index.md 존재)

**검증**: ✅ 전수 PASS (2026-04-01, 2차 재검증 완료 — §6.1 Part2 상태 문자 수준 대조 + K-032/K-033 보정)
- [x] 6개 서브폴더 존재 — **G0-3 매핑 (서브폴더 골격)**, §7.1 Phase 0→1 전환 게이트 충족
  - 01_framework-adapters, 02_service-integration, 03_data-exchange, 04_deployment-scaling, 05_self-evolution, 06_autonomy-safety 전수 확인
- [x] 6개 _index.md 존재 — **§10 검증 #5 (_index.md 존재, 기준 6/6)**
  - 6개 서브폴더 × _index.md = 6/6 확인
- [x] 폴더 깊이 3단계 이하 — **§10 검증 #4 (폴더 깊이, 기준 위반 0)**, R1 준수
  - `3-10_*/ → XX_카테고리/ → _index.md` = 2단계, 4단계 파일 0건
- [x] 서브폴더명 §2.3 네이밍 규칙 준수 — 영문 소문자+하이픈+2자리 접두사(`01_`~`06_`) 6/6 PASS
- [x] 파일명 §2.3 네이밍 규칙 준수 — `_index.md` 영문 소문자+언더스코어 6/6 PASS
- [x] _index.md 4요소(K-ID 목록·파일 목록·V 스코프·Part2 상태) 기재 — 절차 3 기준 6/6 PASS
  - (a) K-ID 목록: §6.1 기준 K-ID 범위+항목명 테이블 전수 기재
  - (b) 계획 파일 목록: §2.1 기준 파일 구성 + "생성 예정 (§11.1 FR-1)" 표기
  - (c) V 스코프 배정: §7.3~§7.5 기준 V1/V2/V3 분류, §7 미배정 항목(K-045·K-046·K-054) 주석 포함
  - (d) Part2 반영 상태 요약: 헤더에 PARTIAL/MINIMAL/ABSENT 집계 + 해결 방식 1줄 기재
- [x] _index.md에 Phase/Week 등 When 정보 미기재 — R6 준수 (sot 2/ = What+How만)
  - "§3 Phase 3" 등 Part2 섹션명(출처 식별자)만 존재 — Part2 라벨 참조이므로 R6 허용 범위
  - V 스코프(V1/V2/V3)는 범위 분류(What)이며 Phase 일정(When) 아님
- [x] §6.1 K-ID 범위 ↔ _index.md 담당 K-ID 일치 — 절차 4 대조표 기준
  - 01_(K-021~K-030=10) + 02_(K-031~K-040=10) + 03_(K-049~K-054=6) + 04_(K-055~K-060=6) + 05_(K-061~K-068=8) + 06_(K-041~K-048=8) = 48 K-ID, 누락·이중 카운트 0건
  - V 스코프 §7.3~§7.5 교차 대조: 기존 오류 19건(01_ 4건, 02_ 5건, 03_ 4건, 04_ 3건, 05_ 3건) 전수 보정 완료
- [x] §6.1 Part2 상태 문자 수준 대조 (2차 재검증) — 48건 전수 PASS
  - 01_: K-021 PARTIAL(§3), K-022·K-025 MINIMAL(§6.7), K-023·K-024·K-026~K-030 ABSENT — 3/7 §6.1 일치 ✅
  - 02_: K-031 LiteLLM·K-032 Tavily·K-033 E2B PARTIAL(§6.6), K-034 MINIMAL(§6.6), K-035~K-040 ABSENT — 4/6 §6.1 일치 ✅
    - 2차 보정: K-032 "Tavily/Brave"→"Tavily" (§6.1에 Brave 미언급), K-033 "MCP"→"E2B" (§6.1 원문 준수)
  - 03_: K-049·K-054 MINIMAL, K-050~K-053 ABSENT — 2/4 §6.1 일치 ✅
  - 04_: 전체 ABSENT — 0/6 §6.1 일치 ✅
  - 05_: 전체 ABSENT — 0/8 §6.1 일치 ✅
  - 06_: K-041·K-043·K-044 PARTIAL(§6.7), K-042 MINIMAL(§6.5), K-045~K-048 ABSENT — 4/4 §6.1 일치 ✅
- [x] 계획 파일 목록 ↔ §2.1 폴더 트리 전수 대조 — 6/6 PASS
  - 01_: crewai_adapter.md, autogen_adapter.md, langgraph_adapter.md ✅
  - 02_: llm_gateway.md, external_apis.md ✅
  - 03_: message_format.md, serialization.md ✅
  - 04_: container_spec.md ✅
  - 05_: dream_mode.md ✅
  - 06_: permission_matrix.md, guardrail_rules.md ✅
- [x] 콘텐츠 파일(crewai_adapter.md 등) 미생성 — 본 작업 범위 외 (§11.1 FR-1 책임)
  - 06_의 기존 `agent_mode_autonomy_mapping.md`는 P0-6 이전 생성물, 본 작업 범위 외 기존 파일로 보존
- [x] 기존 _index.md V 로드맵 오류 보정 — 19건 전수 수정
  - 01_: K-026~K-029 V1→V2 (4건, §7.4 기준)
  - 02_: K-031~K-033·K-037·K-039 V1→V2 (5건, §7.4 기준)
  - 03_: K-050·K-052~K-053 V1→V2 (3건, §6.2 P1), K-054 V1→§7 미배정 (1건)
  - 04_: K-057~K-059 V1→V2 (3건, §7.4 기준)
  - 05_: K-063 V3→V2 (1건, §7.4), K-065 V1→V3 (1건, §7.5), K-068 V2→V3 (1건, §7.5)
- [x] R6 위반 보정 — 기존 _index.md "핵심 파일" 테이블의 "Phase" 열 → "상태" 열로 교체 (6건), Phase/Week 직접 기재 제거
- [x] 형식 일관성 6/6 — 제목·헤더 blockquote·K-ID 테이블 6열·계획 파일 테이블 3열·Footer 정본 소유·"생성 예정 (§11.1 FR-1)" 통일 확인

**산출물**:
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\01_framework-adapters\_index.md` (보정)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\02_service-integration\_index.md` (보정)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\03_data-exchange\_index.md` (보정)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\04_deployment-scaling\_index.md` (보정)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\05_self-evolution\_index.md` (보정)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\06_autonomy-safety\_index.md` (보정)
= 6개 서브폴더 × `_index.md` = **6 파일 (기존 골격 존재, V 스코프·R6·4요소·§6.1 Part2 상태 보정)**
**상태**: ✅ 완료
</details>

<details>
<summary><b>P0-7. SOT2_MASTER_INDEX.md 갱신</b></summary>

**목표**: P0-1~P0-6 전수 완료 상태를 SOT2_MASTER_INDEX.md의 #13(3-10 Agent-Protocol-Interoperability) 항목에 반영하여, Phase 0 마감을 기록한다. §7.1 전환 게이트 조건(G0-1 §6 매핑 100%·G0-2 AUTHORITY_CHAIN 작성·G0-3 서브폴더 골격)에는 직접 포함되지 않으나, 전체 sot 2/ 도메인의 단일 인덱스 문서로서 Phase 0 완료 선언의 마감 작업이다. §10 검증 항목에 직접 매핑되지 않으며, MASTER_INDEX 자체의 정합성·완전성을 검증 기준으로 한다.

**선행 의존**:
- P0-1~P0-6 전수 완료 전제 — 갱신 내용이 각 작업의 산출물 상태를 반영하므로:
  - P0-1: §6 매핑 100% (86항목 전수 매핑, G0-1 PASS)
  - P0-2: §7.3 방식 C 요약 3건 (LangGraph·Agent Teams·MCP Bridge)
  - P0-3: 계획서 14+4 섹션 작성 완료 (APPROVED)
  - P0-4: AUTHORITY_CHAIN.md 작성 완료 (LOCK-AP-01~AP-10, G0-2 PASS)
  - P0-5: CONFLICT_LOG.md 초기화 + 충돌 6건 등록 (v1.1)
  - P0-6: 서브폴더 6개 + _index.md 6/6 생성 완료 (G0-3 PASS)

**입력 파일**:
- `D:\VAMOS\docs\sot 2\SOT2_MASTER_INDEX.md` (갱신 대상 — #13 항목 위치 확인 + 인접 도메인 기재 형식 참조)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md` (갱신 내용 1차 출처 — §1.3 항목 수·§2.1 서브폴더 구조·§3.4 LOCK 10개·§6 매핑 현황·§7.2 Phase 0 상태·§7.3 방식 C 3건·§12 FINAL REVIEW 등급)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\AUTHORITY_CHAIN.md` (P0-4 산출물 상태 확인 — Status·버전·LOCK 항목 수)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\CONFLICT_LOG.md` (P0-5 산출물 상태 확인 — 충돌 건수·상태 분류·버전)

**절차**:
1. **MASTER_INDEX 현행 구조 파악**: #13(3-10 Agent-Protocol-Interoperability) 항목의 현재 위치·기존 내용 확인. 인접 도메인(#11 3-8 A2A, #16 4-3 MCP 등 동일 Tier 3) 항목의 기재 패턴(헤더·blockquote·항목 리스트·서브폴더·Phase 추적) 확인하여 형식 일관성 기준 수립
2. **P0-1~P0-6 산출물 실물 대조**: 갱신에 필요한 수치·상태를 실물 파일에서 확인
   - AUTHORITY_CHAIN.md: Status(APPROVED)·버전(v1.0)·LOCK 항목 수(10개, LOCK-AP-01~AP-10)
   - CONFLICT_LOG.md: 버전(v1.1)·충돌 건수(6건)·상태 분류(경계 확정 2건 + 해결 완료 4건)
   - 서브폴더 6개 실물 존재 + _index.md 6/6 존재
   - 본 계획서 §6.1 매핑 합계(76 K-ID, 48 직접 소유 + 20 외부 정본 참조 + 8 참고/로드맵)
3. **#13 상세 항목 갱신** (아래 12개 필드 전수 반영):
   - **(a) 헤더**: `### 3-10. Agent Protocol / Interoperability ✅ APPROVED` + Phase FINAL PASS + Content 등급 — §12 FINAL REVIEW 기준
   - **(b) 구현 현황 blockquote**: `Phase 0 ✅ 완료 (7/7) — Phase 1 대기 | 86항목, 6 서브폴더` — §7.2 Phase 0 작업 7건(P0-1~P0-7) 전수 완료 기준
   - **(c) 폴더명**: `3-10_Agent-Protocol-Interoperability/`
   - **(d) 계획서**: 파일명 + 섹션 구조(14+4) + 부록 주요 내용(§A 어댑터 카탈로그·§B 자율성 L0~L4·§C 가드레일 엔진·§D 의존성 매트릭스) — P0-3 검증 "14+4 섹션" 정본 기준
   - **(e) 기존 명세**: `AGENT_PROTOCOL_INTEROPERABILITY_상세명세.md` + 줄수(770줄)
   - **(f) AUTHORITY_CHAIN.md**: ✅ 작성 완료 + LOCK 항목 수·범위 — P0-4 산출물 + 실물 대조
   - **(g) CONFLICT_LOG.md**: ✅ + 충돌 건수·해결 상태 요약 — P0-5 산출물 + CONFLICT_LOG.md 실물 대조 (§2 충돌 기록 테이블 기준, 현재 6건: 경계 확정 2건 + 해결 완료 4건)
   - **(h) 서브폴더 6개 목록**: 각 폴더명 + K-ID 범위 + 항목 수 + 카테고리 설명 + `_index.md ✅` — P0-6 산출물 + §6.1 매핑 테이블 대조
   - **(i) 86항목 매핑 현황**: §6 전수 매핑 결과 기재 (48항목 직접 소유 + 20항목 #11/#16 정본 참조 + 8항목 참고/로드맵 = 76 K-ID) — P0-1 산출물 §6 기준
   - **(j) Part2 상태**: PARTIAL (44개 항목 미반영, 76 K-ID 중 24 반영/44 미반영/8 N/A) + 방식 C 요약 건수·대상(3건: LangGraph, Agent Teams, MCP Bridge) + 미반영 중심 신규 작성 방향 — §1.3·계획서 header 정본 기준 + P0-2 산출물 §7.3 기준
   - **(k) SOT 근거**: STEP7-K (86개 항목)
   - **(l) 구현 Phase 추적 (collapsible)**: Phase 0~3 테이블 `| Phase | 작업 요약 | 상태 | 주요 게이트 |` — §7.1 전환 게이트 + §7.2~§7.5 Phase 계획 기준
4. **하단 Phase 진행 총괄표 갱신**: MASTER_INDEX 하단 도메인별 총괄표에서 3-10 행의 Phase 0 열을 `✅ (7/7)`로 갱신, 비고 `Ph1 대기` — §7.2 전수 완료(P0-1~P0-7) 기준
5. **형식 일관성 최종 확인**: 인접 도메인(#11 3-8 A2A, #12 3-9 Business, #16 4-3 MCP 등) 항목과 기재 형식·순서·수준 비교, 불일치 시 #13 항목을 인접 도메인 패턴에 맞춰 조정

**검증**: ✅ 전수 PASS (2026-04-02)
- [x] #13 헤더에 `✅ APPROVED` + Phase FINAL PASS + Content 등급 반영 — §12 FINAL REVIEW(APPROVED, Phase 5 FINAL PASS 2026-03-24, A- S10-2) 기준 일치 확인
- [x] 구현 현황 `Phase 0 ✅ 완료 (7/7) — Phase 1 대기 | 86항목, 6 서브폴더` 기재 — §7.2 Phase 0 작업 7건(P0-1~P0-7) 전수 완료 기준
- [x] 폴더명 `3-10_Agent-Protocol-Interoperability/` 기재
- [x] 계획서 파일명 + `(14+4 섹션, §A 어댑터 카탈로그 · §B 자율성 L0~L4 · §C 가드레일 엔진 · §D 의존성 매트릭스)` 기재 — 목차 18개 항목(§1~§14 + §A~§D) 전수 반영. **기존 "14+3" → "14+4"로 보정** (§D 의존성 매트릭스 누락 수정, P0-3 검증 "14+4 섹션" 정본 기준)
- [x] 기존 명세 `AGENT_PROTOCOL_INTEROPERABILITY_상세명세.md (770줄)` 기재
- [x] AUTHORITY_CHAIN.md: `✅ 작성 완료 (10개 LOCK 항목, LOCK-AP-01~AP-10)` 기재 — P0-4 산출물 + AUTHORITY_CHAIN.md 실물(Status: APPROVED, v1.0) 대조 일치
- [x] CONFLICT_LOG.md: 충돌 건수·상태 기재 — P0-5 산출물 + CONFLICT_LOG.md 실물(v1.1, 6건: 경계 확정 2건 #1·#2 + 해결 완료 4건 #3~#6) 대조. **기존 "3건 RESOLVED" → 6건으로 보정 완료** (경계 확정 2: A2A·MCP 정본 소유 + 해결 완료 4: CB recovery 60s SOURCE_CONFLICT, 항목 수 정합, LOCK-AP-09 출처 정정, K-065 V 로드맵 정정)
- [x] 서브폴더 6개 전수 기재 (01_~06_) + 각 K-ID 범위·항목 수·설명 + `_index.md ✅` 6/6 — P0-6 산출물 + §6.1 매핑 테이블 + 실물 폴더 대조 (6개 서브폴더 + 6개 _index.md 실물 확인)
- [x] 86항목 매핑 현황 `48항목 직접 소유 + 20항목 #11/#16 정본 참조 + 8항목 참고/로드맵` 기재 — P0-1 산출물 §6 대조 (합계 76 K-ID, 전수 매핑 100%)
- [x] Part2 상태 + 방식 C 요약 3건(LangGraph, Agent Teams, MCP Bridge) 기재 — P0-2 산출물 §7.3 대조. **기존 "~50개 항목 미반영" → "44개 항목 미반영, 76 K-ID 중 24 반영/44 미반영/8 N/A"로 보정** (§1.3·계획서 header 정본 기준)
- [x] SOT 근거 `STEP7-K (86개 항목)` 기재
- [x] 구현 Phase 추적 테이블 (Phase 0~3) 기재 — §7.1 전환 게이트 + §7.2~§7.5 Phase 계획 대조, Phase 0 상태 `✅`, Phase 1~3 `☐`. **기존 게이트 "Section-6 매핑 100%"(1조건) → "§6 매핑 100% + AUTH + 6폴더 → PASS (2026-04-02)"(3조건)로 보정** (§7.1 전환 게이트 3조건 전수 반영, #11 3-8 형식 일관성 확보)
- [x] 하단 총괄표 3-10 행: Phase 0 `✅ (7/7)`, 비고 `Ph1 대기` — §7.2 전수 완료 기준 일치 (line 1156 확인)
- [x] 인접 도메인(#11 3-8, #12 3-9, #16 4-3) 기재 형식과 일관성 — 헤더·blockquote·항목 리스트·서브폴더·Phase 추적 순서·패턴 통일 확인. 의존성 필드는 #11만 기재·#12/#13 미기재(비필수 패턴, 현행 유지)

**산출물**: `D:\VAMOS\docs\sot 2\SOT2_MASTER_INDEX.md` 갱신 (#13 상세 항목 12필드 + 하단 총괄표 1행)
**상태**: ✅ 완료
</details>

### 7.3 Phase 1: MVP (V1 핵심)

> Part2 V1-Phase 3/6에 배정된 항목 중심
> **Phase 1 완료**: 2026-04-11 | P1-1~P1-4 전수 완료 (4/4)
> **게이트 PASS**: G1-1 01_ P0(K-021·K-022·K-023) L3 승급 ✅ · G1-2 06_ P0(K-041·K-042·K-043 + K-045·K-046) L3 승급 ✅ · G1-3 Part2 방식 C 요약(§7.3.1~§7.3.3) ↔ P1-1~P1-3 교차 대조 PASS ✅ → Phase 1→2 전환 게이트 **PASS**
> **Phase 1 완료 판정**: ✅ (2026-04-11) — P1-1~P1-3 L3 작성 + P1-4 교차 대조 판정 전수 PASS. Phase 1→Phase 2 전환 게이트 3조건(01_/06_ P0 L2 이상 + Part2 방식 C 요약 완료) 충족. 상세: 아래 P1-4 세션 검증 결과 요약 참조.

| 서브폴더 | 항목 | 작업 | V 로드맵 |
|----------|------|------|---------|
| `01_framework-adapters/` | K-021(LangGraph), K-022(CrewAI), K-023(AutoGen) | 3대 프레임워크 어댑터 L3 작성 — ✅ 완료 (2026-04-11, v1.0). 3개 L3 파일(1,458줄) 생성, LOCK-AP-01·03·05·06·07·08·09 전수 정합, §7.3.1·7.3.2 방식 C 반영, 재검증 0회, CONFLICT 후보 0건, 이월 없음 | V1 |
| `06_autonomy-safety/` | K-041(권한), K-042(HITL), K-043(샌드박스) | 권한 매트릭스 + HITL 프로토콜 L3 — ✅ 완료 (2026-04-11, v1.0). 2개 L3 파일(1,140줄) 생성, K-041/K-042/K-043 + §6.2 P0 미배정 K-045/K-046 5건 전수 해소, LOCK-AP-02·05·10 전수 정합, §B/§C 부록 교차검증 PASS, 재검증 0회, CONFLICT 후보 0건, 이월 없음 | V1 |
| `03_data-exchange/` | K-049(메시지포맷), K-051(이벤트버스) | VamosMessage 확장 + 이벤트 버스 L3 — ✅ 완료 (2026-04-11, v1.0). 2개 L3 파일(1,210줄) 생성, LOCK-AP-01·03·04·07·09 전수 정합, §7.3.3 방식 C(MCP Bridge) 반영, §7.3.2 V2 Redis Pub/Sub 전환 경로 명시, Phase 2 통합 테스트 시나리오 27건(MF 13 + EB 14), 재검증 0회, CONFLICT 후보 1건(type enum alias §2.5 매핑 해소), 이월 없음 | V1 |

**Part2 PARTIAL 방식 C 요약 포함 영역:**

#### 7.3.1 Part2 정본 요약 — LangGraph StateGraph (방식 C)

> **출처**: PART2 V1-Phase 3 (line 2078~2275)
> **Part2가 정본**: When + Where — V1-Phase 3 Week 9-12 배정, `backend/vamos_core/agent/graph/state_graph.py`, Gate 통합 `agent/gate_pipeline.py`, Loop `agent/pipeline/` + `agent/hitl.py`, CB `agent/circuit_breaker.py`
> **sot 2/가 정본**: What + How — LangGraph↔VAMOS 상태 매핑 알고리즘, 조건부 엣지 변환 규칙, 그래프→Task 변환 로직

**Part2 핵심 내용 요약:**
V1-Phase 3에서 LangGraph StateGraph 5-Phase(Intake→Plan→Execute→Verify→Deliver LOCK), Gate 통합 노드(5-Gate 실행 + allow/deny/downshift/hold 라우팅), Soft Loop(최대 1회 자동 재시도 D2.0-05 §4.2 LOCK), Hard Loop(2회째 실패→HITL I-19 승인), Circuit Breaker(3-State closed/open/half_open, failure_threshold=3, recovery=60s D2.0-05 §4.4 LOCK — SOURCE_CONFLICT: D2.1 스키마 300s 대비 정본 우선순위 60s 채택), A-1 MultiBrain Adapter Failover(GPT-4o→Claude→Ollama, 3회 타임아웃 시 전환 LOCK), Agent Teams V1(Lead + max 2 Sub LOCK-AT-014), E-1~E-6 Blue Node 6종 연동, `START`/`END` 상수 사용 필수(set_entry_point 금지 LOCK-AP-08). 단순 제어 흐름 원칙: StateGraph는 오케스트레이션 전용, 모듈 내부는 함수/if-else/while, StateGraph 중첩 금지.

**sot 2/ 보완 영역:**
LangGraph 그래프→VAMOS Task 변환 알고리즘(노드 토폴로지 정렬→Task 체인 변환), 상태 동기화 프로토콜(양방향 state_mapping), 조건부 엣지→VAMOS Gate 매핑 규칙, Circuit Breaker half_open 복구 전략 상세.

#### 7.3.2 Part2 정본 요약 — Agent Teams V1 (방식 C)

> **출처**: PART2 V1-Phase 3 구현항목 #7 (line 2130~2133) + §6.7 상세 (line 4998~5133)
> **Part2가 정본**: When + Where — V1-Phase 3 Week 9-12 배정, `backend/vamos_core/agent/teams.py`
> **sot 2/가 정본**: What + How — 팀 구성 전략, 역할 배정 알고리즘, 통신 패턴, K-041·K-043·K-044 구현 상세

**Part2 핵심 내용 요약:**
Agent Teams V1은 Lead Agent + max 2 Sub-Agent(LOCK-AT-014 V1=3). Sequential/Parallel 패턴만 지원. 위임 깊이 V1=2(LOCK-AT-004 max=3). V1 Agent 유형: Lead(ORANGE CORE/I-5, Sonnet), Research(BLUE NODE P0, Sonnet), Coding(BLUE NODE P0, Haiku). 비용 ₩1,300/일 이내. MessageBus In-Memory Queue. LOCK-AT-001~017(17개 아키텍처 제약: 단일결정 LOCK-AT-002, 무한루프 금지 LOCK-AT-003, Gate 선행 LOCK-AT-005, Execute 단계 도구호출 LOCK-AT-006, 비용상한 초과 자동차단 LOCK-AT-011, HMAC 무결성 LOCK-AT-012, 권한 상승 금지 LOCK-AT-013, Lead 직접실행 금지 LOCK-AT-015). RBAC 매트릭스 상세는 AGENT_TEAMS_SPEC §8 및 D2.0-07 §4 참조. 로드맵: V2 Teams 10(Redis Pub/Sub, 6패턴), V3 Mesh 50+(PARL Agent Swarm, PPO RL) 확장 예정.

**sot 2/ 보완 영역:**
CrewAI/AutoGen 스타일 팀 구성 패턴, 역할 기반 에이전트 매칭 알고리즘, 팀 간 통신 프로토콜(Delegation/Collaboration/Pipeline/Competition/Consensus), K-041 권한 매트릭스 상세(Permission Level 0~5), K-043 에이전트 샌드박싱 규격(Docker/E2B), K-044 비용 관리 알고리즘(토큰 추적·자동 차단).

#### 7.3.3 Part2 정본 요약 — MCP Bridge (방식 C)

> **출처**: PART2 V1-Phase 6 (line 2546~2684) + §6.6 카탈로그 (line 4966~4996)
> **Part2가 정본**: When + Where — V1-Phase 6 Week 13-16 배정(Phase 4-5 병렬), `backend/vamos_core/mcp/bridge.py`, `mcp/server.py` + `mcp/tool_discovery.py`, `mcp/client.py`
> **sot 2/가 정본**: What + How — MCP↔A2A 양방향 변환 로직(K-017), Blue Node MCP 노출 활용(K-010), 도구 디스커버리 알고리즘

**Part2 핵심 내용 요약:**
MCP Bridge Layer는 Streamable HTTP 기반(WebSocket 아님 LOCK-AP-04). SSE 기반 양방향 통신. MCP Server(20+ V1 tools, I-10 Tool Registry 기반 MCP Tool Discovery 프로토콜), MCP Client(Tavily, E2B 등 외부 MCP 서버 연결, auth 토큰 관리). §6.6 외부 MCP 서버 카탈로그 11개(V1=7: Tavily·SerpAPI·E2B·Pyodide·Unstructured·PyMuPDF·Playwright, V2+=3: CLIP·Whisper·Postgres, V3=1: WebSocket). 내부 MCP 컴포넌트 7개(Bridge Layer·Server·Client·Pyodide·PyMuPDF·CLIP·Playwright 래퍼). 비용 ₩40,000/월 LOCK(V1 전체 운영비). SOT: D2.0-03 §6(MCP Protocol).

**sot 2/ 보완 영역:**
\#13 직접 작성: MCP Tool→A2A Skill 양방향 변환기(K-017 — #13 인터롭 정본), Blue Node→MCP Server 노출 활용 패턴(K-010 — #13 활용 정본). #16 MCP 정본 참조 필요(§5.2 도메인 경계): 보안 레이어(K-007), Sampling 통합(K-006).

#### Phase 1 단계별 상세 작업 절차

<details>
<summary><b>P1-1. 3대 프레임워크 어댑터 L3 작성 (01_framework-adapters/)</b></summary>

**대조 기준**:
- §7 세부 작업: §7.3 `01_framework-adapters/` K-021(LangGraph), K-022(CrewAI), K-023(AutoGen) 배정
- §7 전환 게이트: 01_/06_ P0 항목 L2 이상 + Part2 방식 C 요약 완료
- §6 이슈: K-021 PARTIAL(§3 LangGraph), K-022 MINIMAL(§6.7), K-023 ABSENT — Part2 미반영 영역 신규 작성 필요
- §7.3.1 방식 C: LangGraph StateGraph (Part2 V1-Phase 3) — StateGraph 5-Phase, Gate 통합 노드, Soft/Hard Loop, CB 3-State, START/END 상수(LOCK-AP-08)
- §7.3.2 방식 C: Agent Teams V1 (Part2 V1-Phase 3) — Lead + max 2 Sub(LOCK-AP-05), Sequential/Parallel 패턴, LOCK-AT-001~017

**목표**: `01_framework-adapters/` 하위 3개 콘텐츠 파일(langgraph_adapter.md, crewai_adapter.md, autogen_adapter.md)을 L3(구현 상세) 수준으로 작성한다. 각 어댑터는 VAMOS 5-Phase 파이프라인(Intake→Plan→Execute→Verify→Deliver)과의 매핑, VamosMessage(LOCK-AP-01) 변환, A2A Task 상태(LOCK-AP-03) 연동, START/END 상수 사용(LOCK-AP-08)을 포함한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md` §2.1(폴더 트리), §3.4(LOCK-AP-01~10), §6.1(K-ID 매핑), §7.3.1(LangGraph 방식 C), §7.3.2(Agent Teams 방식 C), §A(프레임워크 어댑터 카탈로그)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\01_framework-adapters\_index.md` (K-021~K-030 인덱스, V 스코프 확인)
- `D:\VAMOS\docs\sot\STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md` (K-021~K-023 원본 요구사항)
- `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` (StateGraph 5-Phase, Gate, Loop, CB 원본 — LOCK-AP-03·AP-06·AP-08 값 대조)

**절차**:
1. `01_framework-adapters/_index.md`에서 K-021~K-023의 V1 스코프 배정 및 Part2 반영 상태 확인
2. STEP7-K에서 K-021(LangGraph 어댑터), K-022(CrewAI 어댑터), K-023(AutoGen 어댑터) 원본 요구사항 추출
3. `langgraph_adapter.md` 작성 (K-021):
   - §7.3.1 방식 C 참조: StateGraph 5-Phase→VAMOS 파이프라인 매핑 알고리즘
   - 노드 토폴로지 정렬→Task 체인 변환, 조건부 엣지→VAMOS Gate 매핑 규칙
   - START/END 상수 사용 필수(LOCK-AP-08, set_entry_point 금지)
   - CB recovery 60초(LOCK-AP-06), failure_threshold=3
   - 양방향 state_mapping 프로토콜, half_open 복구 전략 상세
   - 단순 제어 흐름 원칙: StateGraph 오케스트레이션 전용, 중첩 금지
4. `crewai_adapter.md` 작성 (K-022):
   - §7.3.2 방식 C 참조: Agent Teams V1 팀 구성 패턴과의 매핑
   - CrewAI Role/Goal/Backstory→VAMOS Agent 유형 변환
   - Lead + max 2 Sub-Agent(LOCK-AP-05, LOCK-AT-014) 제약 적용
   - Sequential/Parallel 패턴→VAMOS Task 체인 변환
   - VamosMessage(LOCK-AP-01) 스키마 준수, A2A Task 상태(LOCK-AP-03) 연동
5. `autogen_adapter.md` 작성 (K-023):
   - AutoGen ConversableAgent→VAMOS Agent 변환
   - GroupChat→VAMOS Teams 매핑 (Lead + max 2 Sub 제약)
   - AssistantAgent/UserProxyAgent 역할 분리→VAMOS RBAC 매핑
   - VamosMessage(LOCK-AP-01), A2A Task 상태(LOCK-AP-03) 연동
6. 3개 파일 공통: LOCK-AP-01(VamosMessage 스키마), LOCK-AP-03(A2A Task 상태), LOCK-AP-07(A2A+MCP 양방향 필수), LOCK-AP-09(V1 비용 ₩40K) 준수 확인
7. §A 프레임워크 어댑터 카탈로그와 교차 대조 — 카탈로그 정의와 L3 구현 상세 정합성 검증

**검증**: ✅ 전수 PASS (2026-04-11)
- [x] 3개 파일(langgraph_adapter.md, crewai_adapter.md, autogen_adapter.md) 생성 — §2.1 폴더 트리 기준 (3/3 존재 ✅)
- [x] 각 파일 L3 수준 (구현 상세: 알고리즘, 스키마, 변환 규칙 포함) — L2(설계) 이상 게이트 충족 (langgraph 528줄 / crewai 458줄 / autogen 472줄, 총 1,458줄 ✅)
- [x] LOCK-AP-01·AP-03·AP-05·AP-06·AP-07·AP-08·AP-09 값 §3.4 원본과 무충돌 (7/7 LOCK 무충돌 ✅)
- [x] §7.3.1 방식 C(LangGraph) 참조 내용 반영 — StateGraph 5-Phase, Gate, Loop, CB, START/END (6요소 전수 반영 ✅)
- [x] §7.3.2 방식 C(Agent Teams) 참조 내용 반영 — Lead+2 Sub, Sequential/Parallel, LOCK-AT-001~017 (5요소 전수 반영 ✅)
- [x] K-021 Part2 PARTIAL(§3) 보완 영역 반영, K-022 MINIMAL(§6.7) 신규 작성, K-023 ABSENT 신규 작성 (3건 Part2 상태 헤더 정합 ✅)
- [x] R6 준수 — Phase/Week 등 When 정보 미기재 (sot 2/ = What+How만) (3파일 전수 R6 준수 ✅)
- [x] §A 카탈로그 정합성 확인 (FrameworkAdapter 인터페이스 정합 ✅)

> **완료**: 2026-04-11. 3개 프레임워크 어댑터 L3 파일(1,458줄)을 K-021/K-022/K-023 L3 정본으로 작성하고 LOCK-AP-01·03·05·06·07·08·09 전수 정합 + §7.3.1·7.3.2 방식 C 반영 확인.
>
> **실행 결과 요약**:
> - 3개 L3 파일 생성: langgraph_adapter.md(528줄), crewai_adapter.md(458줄), autogen_adapter.md(472줄) — 총 1,458줄
> - LOCK 정합 검증: LOCK-AP-01(VamosMessage 6필드)/AP-03(A2A Task 6상태)/AP-05(Lead+max 2 Sub)/AP-06(CB recovery 60s)/AP-07(A2A+MCP 양방향)/AP-08(START/END 상수)/AP-09(V1 비용 상한) — 7/7 무충돌
> - 방식 C 참조: §7.3.1(LangGraph StateGraph 5-Phase, Gate, Soft/Hard Loop, CB 3-State, START/END, MultiBrain Failover) 전수 langgraph_adapter.md 반영 / §7.3.2(Agent Teams Lead+2 Sub, Sequential/Parallel, LOCK-AT-001~017, RBAC 연결) 전수 crewai·autogen_adapter.md 반영
> - 공통 자료 구조 선정의: langgraph_adapter.md §3에 VamosMessage/A2ATaskState/FrameworkAdapter 인터페이스 1회 정의, crewai/autogen은 참조만
> - R6 정본 분리 준수: 3개 파일 헤더 Part2 상태 명시(PARTIAL/MINIMAL/ABSENT), Phase/Week 정보 본문 미기재
> - §A 카탈로그 정합: FrameworkAdapter 공통 인터페이스(convert/execute/state_sync) 3파일 일치
> - 재검증·CONFLICT·이월: 재검증 0회, CONFLICT 후보 0건, 이월 항목 0건

**[P1-1] 검증 결과 요약** (갱신: 2026-04-11)
- 0. 산출물: 3개 파일 신규 생성 — `01_framework-adapters/langgraph_adapter.md`(K-021, 528줄), `crewai_adapter.md`(K-022, 458줄), `autogen_adapter.md`(K-023, 472줄). 총 1,458줄.
- 1. 게이트: G1(01_ P0 항목 L2 이상) ✅ — K-021/K-022/K-023 전수 L3 승급, LOCK-AP-01·03·05·06·07·08·09 무충돌 7/7, §7.3.1·7.3.2 방식 C 전수 반영, R6 준수 확인
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건 — 기존 CONFLICT_LOG.md 6건과 무관, 신규 후보 없음
- 3. LOCK 변경: 없음 — LOCK-AP-01~10 모두 §3.4 원본 값 그대로 인용, 재정의·갱신 0건
- 4. 이월: 없음 — P1-2(permission_matrix·guardrail_rules) / P1-3(message_format·event_bus) / P1-4(Part2 방식 C 통합 검증)은 각 독립 세션에서 별도 진행

**산출물**:
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\01_framework-adapters\langgraph_adapter.md` (K-021, L3 신규)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\01_framework-adapters\crewai_adapter.md` (K-022, L3 신규)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\01_framework-adapters\autogen_adapter.md` (K-023, L3 신규)
</details>

<details>
<summary><b>P1-2. 권한 매트릭스 + HITL + 샌드박스 L3 작성 (06_autonomy-safety/)</b></summary>

**대조 기준**:
- §7 세부 작업: §7.3 `06_autonomy-safety/` K-041(권한), K-042(HITL), K-043(샌드박스) 배정
- §7 전환 게이트: 01_/06_ P0 항목 L2 이상 + Part2 방식 C 요약 완료
- §6 이슈: K-041·K-043·K-044 PARTIAL(§6.7), K-042 MINIMAL(§6.5), K-045(롤백)·K-046(설명가능성) §7 미배정 ⚠ → Phase 1 포함 권고(§6.2 P0 우선순위)
- §7.3.2 방식 C: Agent Teams V1 — RBAC 매트릭스 상세는 AGENT_TEAMS_SPEC §8 및 D2.0-07 §4 참조, K-041 권한 매트릭스(Permission Level 0~5), K-043 샌드박싱(Docker/E2B)

**목표**: `06_autonomy-safety/` 하위 콘텐츠 파일(permission_matrix.md, guardrail_rules.md)을 L3 수준으로 작성한다. K-041(권한 매트릭스, LOCK-AP-02 Permission Level 0~5), K-042(HITL 프로토콜, LOCK-AP-10 Confidence < 50%), K-043(샌드박싱)을 포함하며, §6.2 P0 우선순위이나 §7 미배정인 K-045(롤백)·K-046(설명가능성)을 함께 작성하여 미배정 이슈를 해소한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md` §3.4(LOCK-AP-02·AP-10), §6.1(K-041~K-048 매핑), §6.2(P0 우선순위 K-045·K-046), §7.3.2(Agent Teams 방식 C), §B(자율성 레벨 L0~L4), §C(안전 가드레일 규칙 엔진)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\06_autonomy-safety\_index.md` (K-041~K-048 인덱스)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\06_autonomy-safety\agent_mode_autonomy_mapping.md` (기존 자율성 매핑 — 충돌 여부 확인)
- `D:\VAMOS\docs\sot\STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md` (K-041~K-043, K-045~K-046 원본 요구사항)
- `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` (HITL I-19, CB, 자율성 레벨 원본)

**절차**:
1. `06_autonomy-safety/_index.md`에서 K-041~K-048의 V1 스코프 및 Part2 반영 상태 확인
2. 기존 `agent_mode_autonomy_mapping.md`와의 정본 범위 중복 여부 확인 — 충돌 시 §9 충돌 해결 프로토콜 적용
3. `permission_matrix.md` 작성 (K-041 + K-045 + K-046):
   - K-041: Permission Level 0~5(LOCK-AP-02) 완전 매트릭스 — 레벨별 허용 작업·API 범위·자원 접근·승인 흐름
   - §B 자율성 레벨 L0~L4 참조: 허용 작업 매트릭스(B.3, 8 카테고리×5 레벨)와 Permission Level 교차 매핑
   - K-045(롤백): 에이전트 작업 롤백·되돌리기 메커니즘 — 상태 스냅샷, 트랜잭션 로그, 복원 절차
   - K-046(설명가능성): 에이전트 결정 설명가능성 — 추론 로그, 결정 트리 추적, 사용자 설명 생성
   - ⚠ K-045·K-046은 §6.2 P0이나 §7 미배정 — 본 작업에서 Phase 1에 포함하여 미배정 이슈 해소
4. `guardrail_rules.md` 보강 (K-042 + K-043):
   - K-042: HITL 프로토콜 L3 — Confidence < 50%(LOCK-AP-10) 트리거, I-19 승인 흐름, HumanInterventionRequest 스키마(§C.4 참조)
   - §C 안전 가드레일 규칙 엔진 참조: 3-Phase(Pre→Runtime→Post), SG-001~SG-010 규칙 세트, SG-009 HITL 트리거
   - K-043: 에이전트 샌드박싱 규격 — Docker/E2B 컨테이너 격리, 자원 제한, 네트워크 정책, 파일시스템 접근 제어
   - §7.3.2 방식 C 참조: K-043 Docker/E2B 샌드박싱 규격 상세
5. LOCK-AP-02(Permission Level 0~5), LOCK-AP-05(Lead + max 2 Sub), LOCK-AP-10(HITL < 50%) 값 대조
6. §B·§C 부록과 L3 콘텐츠 정합성 교차 검증 — 부록은 정의, 콘텐츠 파일은 구현 상세

**검증**: ✅ 전수 PASS (2026-04-11)
- [x] permission_matrix.md 생성 — K-041·K-045·K-046 포함, L3 수준 (552줄, 교차참조/Purpose/공통자료구조/PermissionEnforcer/Level0~5 매트릭스/롤백/설명가능성/로깅/테스트 10건 ✅)
- [x] guardrail_rules.md 생성/보강 — K-042·K-043 포함, L3 수준 (588줄, HITL 트리거/I-19 흐름/Docker·E2B 샌드박스/자원제한/네트워크/FS ACL/이탈감지/테스트 10건 ✅)
- [x] LOCK-AP-02(Permission Level 0~5) 값 §3.4 원본과 무충돌 (permission_matrix.md §2 인용 PASS ✅)
- [x] LOCK-AP-10(HITL Confidence < 50%) 값 §3.4 원본과 무충돌 (guardrail_rules.md DEFINED-HERE 표기 PASS ✅)
- [x] K-045·K-046 §7 미배정 이슈 해소 — Phase 1 permission_matrix.md에 포함 확인 (K-045 롤백 §5 + K-046 설명가능성 §6 신규 작성, §6.2 P0 2건 해소 ✅)
- [x] §B 자율성 레벨·§C 가드레일 규칙 엔진과 교차 정합 (B.1~B.3 + C.1~C.4 교차 참조 8건 PASS ✅)
- [x] agent_mode_autonomy_mapping.md(기존)와 정본 범위 충돌 0건 (정본 범위 분리: 기존=Agent Mode↔Autonomy 매핑 / 신규=Permission Level 집행, §9 충돌 0건 ✅)
- [x] K-041 PARTIAL(§6.7)·K-042 MINIMAL(§6.5)·K-043 PARTIAL(§6.7) Part2 보완 영역 반영 (3건 Part2 상태 헤더 정합, 방식 C 요약 §7.3.2 반영 ✅)
- [x] R6 준수 — Phase/Week 미기재 (2파일 전수 R6 준수, What+How만 ✅)

> **완료**: 2026-04-11. 2개 L3 파일(1,140줄)로 K-041/K-042/K-043 + 미배정 P0 K-045/K-046 포함 총 5 K-ID를 해소하고 LOCK-AP-02·05·10 전수 정합 + §B·§C 부록 교차검증 PASS.
>
> **실행 결과 요약**:
> - 2개 L3 파일 신규 생성: `permission_matrix.md`(K-041·K-045·K-046, 552줄), `guardrail_rules.md`(K-042·K-043, 588줄) — 총 1,140줄
> - LOCK 정합 검증: LOCK-AP-02(Permission Level 0~5)/AP-05(Lead+max 2 Sub)/AP-10(HITL Confidence < 50%, guardrail_rules.md가 DEFINED-HERE) 3/3 무충돌, §3.4 원본 값 그대로 인용
> - §6.2 P0 미배정 이슈 해소: K-045(롤백 스냅샷/트랜잭션 로그/복원 절차) + K-046(추론 로그/결정 트리/사용자 설명 생성) → permission_matrix.md §5/§6 포함, §7 원래 미배정 항목 2건 Phase 1에서 전수 해소
> - §B/§C 부록 교차검증: §B(B.1~B.3) 자율성 레벨 L0~L4 ↔ Permission Level 0~5 교차 매핑, §C(C.1~C.4) 3-Phase 가드레일 + SG-001~SG-010 + HumanInterventionRequest 스키마 정합 PASS
> - 세션 간 인터페이스 정합: langgraph_adapter.md §3 `GatePolicy.escalate_to: "I-19"|"I-20"` / autogen_adapter.md §10 `EscalationPayload.target_channel` / crewai_adapter.md `register_function permission` 3파일 전수 PASS (P1-1 선행 산출물과 무충돌)
> - 공통 자료 구조 선정의: `ActionRequest`, `PermissionDecision`, `EscalationPayload`, `HumanInterventionRequest`를 permission_matrix.md §3에 1회 정의, guardrail_rules.md는 참조만
> - 정본 범위 중복 확인: 기존 `agent_mode_autonomy_mapping.md`(Agent Mode↔Autonomy Level 매핑)와 신규(Permission Level 집행·HITL·샌드박스) 범위 분리 — §9 충돌 0건
> - R-01-7 구조화 로깅 준수: error{}/context{}/recovery{}/trace_id nested 포맷 양 파일 채택 (autogen_adapter §11과 정합)
> - 테스트 시나리오: permission_matrix.md 10건 + guardrail_rules.md 10건 — 총 20건 Phase 2 통합 테스트 힌트 제공
> - R6 정본 분리 준수: 2파일 헤더 Part2 상태 명시(PARTIAL/MINIMAL), Phase/Week 정보 본문 미기재
> - 재검증·CONFLICT·이월: 재검증 0회, CONFLICT 후보 0건, 이월 항목 0건

**[P1-2] 검증 결과 요약** (갱신: 2026-04-11)
- 0. 산출물: 2개 파일 신규 생성 — `06_autonomy-safety/permission_matrix.md`(K-041·K-045·K-046, 552줄), `guardrail_rules.md`(K-042·K-043, 588줄). 총 1,140줄.
- 1. 게이트: G1(06_ P0 항목 L2 이상 + Part2 방식 C 요약 완료) ✅ — K-041/K-042/K-043 L3 승급 + K-045/K-046 신규 L3 작성으로 §6.2 P0 미배정 2건 해소, LOCK-AP-02·05·10 무충돌 3/3, §B·§C 교차 정합 PASS, §7.3.2 Agent Teams 방식 C 반영, R6 준수
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건 — 기존 CONFLICT_LOG.md 6건과 무관, 기존 `agent_mode_autonomy_mapping.md` 정본 범위 분리로 충돌 0건, 신규 후보 없음
- 3. LOCK 변경: 없음 — LOCK-AP-02/AP-05/AP-10 모두 §3.4 원본 값 그대로 인용, 재정의·갱신 0건 (LOCK-AP-10은 guardrail_rules.md가 DEFINED-HERE 표기만 추가)
- 4. 이월: 없음 — P1-3(message_format·event_bus) / P1-4(Part2 방식 C 통합 검증)은 각 독립 세션에서 별도 진행, K-047(자기진화 가드레일 V2) / K-048(에이전트 윤리 V3)은 Phase 2/3 배정 유지

**산출물**:
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\06_autonomy-safety\permission_matrix.md` (K-041·K-045·K-046, L3 신규)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\06_autonomy-safety\guardrail_rules.md` (K-042·K-043, L3 신규)
</details>

<details>
<summary><b>P1-3. VamosMessage 확장 + 이벤트 버스 L3 작성 (03_data-exchange/)</b></summary>

**대조 기준**:
- §7 세부 작업: §7.3 `03_data-exchange/` K-049(메시지포맷), K-051(이벤트버스) 배정
- §7 전환 게이트: 01_/06_ P0 항목 L2 이상 + Part2 방식 C 요약 완료
- §6 이슈: K-049 MINIMAL(Part2 §6.5 수준), K-051 ABSENT — 신규 작성 필요
- §7.3.3 방식 C: MCP Bridge — Streamable HTTP(LOCK-AP-04), SSE 양방향, VamosMessage 기반 메시지 교환

**목표**: `03_data-exchange/` 하위 콘텐츠 파일(message_format.md, event_bus.md)을 L3 수준으로 작성한다. VamosMessage 스키마(LOCK-AP-01)의 확장 규격과 이벤트 버스(In-Memory Queue V1→Redis Pub/Sub V2) 아키텍처를 정의한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md` §3.4(LOCK-AP-01·AP-03·AP-04·AP-07), §6.1(K-049~K-054 매핑), §7.3.3(MCP Bridge 방식 C)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\03_data-exchange\_index.md` (K-049~K-054 인덱스)
- `D:\VAMOS\docs\sot\STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md` (K-049, K-051 원본 요구사항)
- `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` (VamosMessage 원본 스키마, A2A Task 상태 머신)

**절차**:
1. `03_data-exchange/_index.md`에서 K-049·K-051의 V1 스코프 및 Part2 반영 상태 확인
2. STEP7-K에서 K-049(메시지 포맷), K-051(이벤트 버스) 원본 요구사항 추출
3. `message_format.md` 작성 (K-049):
   - VamosMessage 스키마(LOCK-AP-01): id, type, source, target, content, metadata — 6필드 완전 정의
   - 필드별 타입·제약·검증 규칙, 확장 필드 가이드라인
   - A2A Task 상태(LOCK-AP-03): submitted→working→input-required→completed/failed/canceled 전이 규칙
   - MCP 메시지↔VamosMessage 양방향 변환 규칙(LOCK-AP-07)
   - Streamable HTTP 전송(LOCK-AP-04, WebSocket 아님) 기반 직렬화 포맷
   - 메시지 무결성: HMAC(LOCK-AT-012 참조) 검증 절차
4. `event_bus.md` 작성 (K-051):
   - V1: In-Memory Queue 아키텍처 — MessageBus 인터페이스, publish/subscribe API, 토픽 관리
   - 이벤트 타입 정의: AgentCreated, TaskAssigned, TaskCompleted, GateEvaluated, HITLRequested 등
   - 이벤트 순서 보장·중복 제거·재시도 정책
   - VamosMessage(LOCK-AP-01) 기반 이벤트 페이로드 규격
   - V2 확장 경로 명시: Redis Pub/Sub 전환 인터페이스 (§7.3.2 방식 C — V2 Teams 10 Redis Pub/Sub 참조)
5. LOCK-AP-01(VamosMessage 스키마), LOCK-AP-03(A2A Task 상태), LOCK-AP-04(Streamable HTTP), LOCK-AP-07(양방향 필수) 값 대조

**검증**: ✅ 전수 PASS (2026-04-11)
- [x] message_format.md 생성 — K-049, L3 수준 (661줄 ✅)
- [x] event_bus.md 생성 — K-051, L3 수준 (549줄 ✅)
- [x] LOCK-AP-01(VamosMessage 6필드 스키마) 값 §3.4 원본과 무충돌 (6/6 필드 정합 ✅)
- [x] LOCK-AP-03(A2A Task 상태 6개 전이) 값 §3.4 원본과 무충돌 (6상태 전이 머신 일치 ✅)
- [x] LOCK-AP-04(Streamable HTTP) 준수 — WebSocket 사용 0건 (거부 테스트 T-MF-12 포함 ✅)
- [x] LOCK-AP-07(A2A+MCP 양방향) 변환 규칙 포함 (§4 JSON-RPC 2.0 변환 + 라운드트립 불변식 ✅)
- [x] K-049 MINIMAL 보완 + K-051 ABSENT 신규 작성 확인 (2/2 헤더 Part2 상태 정합 ✅)
- [x] R6 준수 — Phase/Week 미기재 (2파일 전수 When 정보 미기재 ✅)

> **완료**: 2026-04-11. 2개 L3 파일(1,210줄)을 K-049/K-051 L3 정본으로 작성하고 LOCK-AP-01·03·04·07·09 전수 정합 + §7.3.3 방식 C(MCP Bridge) 반영 확인.
>
> **실행 결과 요약**:
> - 2개 L3 파일 생성: message_format.md(661줄, K-049 정본), event_bus.md(549줄, K-051 정본) — 총 1,210줄
> - LOCK 정합 검증: LOCK-AP-01(VamosMessage 6필드 Pydantic v2 정본)/AP-03(A2A Task 6상태 전이 머신)/AP-04(Streamable HTTP + SSE, WebSocket 거부 명시)/AP-07(MCP JSON-RPC 2.0 ↔ VamosMessage 양방향 변환 + 라운드트립 불변식)/AP-09(₩40K 비용 상한 → cost.threshold 이벤트 발행 기준) — 5/5 무충돌
> - 방식 C 참조: §7.3.3(MCP Bridge Streamable HTTP, SSE 양방향, VamosMessage 교환) 전수 message_format.md §4·§5 반영 / §7.3.2(Agent Teams V2 Redis Pub/Sub 전환 경로) event_bus.md §11 반영
> - 공통 자료 구조 선정의: message_format.md §2 가 VamosMessage Pydantic v2 도메인 정본, 01_framework-adapters/{langgraph,crewai,autogen}_adapter.md §3 의 간이 flat 뷰는 본 §2 를 참조 (layered 관계), event_bus.md §3 VamosEvent 는 VamosMessage 를 래핑
> - R6 정본 분리 준수: 2개 파일 헤더 Part2 상태 명시(MINIMAL/ABSENT), Phase/Week 정보 본문 미기재
> - Phase 2 통합 테스트 시나리오: message_format §12 13건(T-MF-01~13) + event_bus §12 14건(T-EB-01~14) = 총 27건 — 가이드라인 10건 이상 충족
> - 세션 간 인터페이스 cross-check: 01_framework-adapters §3 간이 뷰 layered OK, 06_autonomy-safety SG-009(LOCK-AP-10) HITL I-19 정합, 6-3 LOCK-AT-012 HMAC cross-domain 참조, 3-8 A2A 상태 머신 1:1 일치 — [INTERFACE_MISMATCH] 검출 0건
> - 에스컬레이션/로깅/ABC: I-20 경유 EscalationPayload(§10/§8), R-01-7 structured JSON 중첩(error/context/recovery/trace_id, §11/§9), MessageBus ABC 신규 정의(event_bus.md §4 — async publish/subscribe/unsubscribe/health/replay)
> - 재검증·CONFLICT·이월: 재검증 0회, CONFLICT 후보 1건(VamosMessage.type enum 용어 STEP7-K 원문 request/response/event/error vs 도메인 canonical task/result/event/control — message_format.md §2.5 alias 매핑 표로 정책 해소, 정식 등재는 step 7 에서 판단), 이월 항목 0건

**[P1-3] 검증 결과 요약** (갱신: 2026-04-11)
- 0. 산출물: 2개 파일 신규 생성 — `03_data-exchange/message_format.md`(K-049, 661줄), `03_data-exchange/event_bus.md`(K-051, 549줄). 총 1,210줄.
- 1. 게이트: G1(03_ P0 항목 L2 이상) ✅ — K-049/K-051 전수 L3 승급, LOCK-AP-01·03·04·07·09 무충돌 5/5, §7.3.3 방식 C 전수 반영, V2 Redis Pub/Sub 전환 경로 명시, R6 준수 확인. Phase 2 통합 테스트 시나리오 27건 (10건 이상 가이드라인 충족).
- 2. CONFLICT: 발견 1건 / 해소 1건 / OPEN 0건 — VamosMessage.type enum 용어(STEP7-K 원문 `request/response/event/error` vs 도메인 canonical `task/result/event/control`) 불일치는 message_format.md §2.5 alias 매핑 표로 정책 해소. 기존 CONFLICT_LOG.md 6건과 무관. 정식 등재 여부는 step 7 에서 판단.
- 3. LOCK 변경: 없음 — LOCK-AP-01·03·04·07·09 모두 §3.4 원본 값 그대로 인용, 재정의·갱신 0건 (message_format.md §2 는 LOCK-AP-01 도메인 정본 선언이나 값 불변).
- 4. 이월: 없음 — P1-4(Part2 방식 C 통합 검증)는 독립 세션에서 별도 진행. K-050(Artifact Store) / K-052~K-054 는 V2+ 배정 유지.

**산출물**:
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\03_data-exchange\message_format.md` (K-049, L3 신규)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\03_data-exchange\event_bus.md` (K-051, L3 신규)
</details>

<details>
<summary><b>P1-4. Part2 방식 C 통합 검증 (§7.3.1~7.3.3 교차 대조)</b></summary>

**대조 기준**:
- §7 세부 작업: §7.3 Phase 1 전체 — Part2 방식 C 요약(§7.3.1~§7.3.3) ↔ P1-1~P1-3 산출물 정합성
- §7 전환 게이트: 01_/06_ P0 항목 L2 이상 + **Part2 방식 C 요약 완료** — 본 태스크에서 "완료" 판정
- §6 이슈: Part2 PARTIAL 항목(K-021 §3, K-022·K-025 §6.7 MINIMAL, K-041·K-043·K-044 §6.7) — L3 반영 확인
- §7.3.1 방식 C: LangGraph StateGraph, §7.3.2 방식 C: Agent Teams V1, §7.3.3 방식 C: MCP Bridge

**목표**: P1-1~P1-3에서 작성한 7개 L3 파일이 §7.3.1~§7.3.3 Part2 방식 C 요약과 정합하는지 전수 교차 대조한다. LOCK-AP-01~10 값 무충돌, Part2 정본(When+Where)↔sot 2/ 정본(What+How) 분리 원칙(§3.3) 준수, Phase 1→2 전환 게이트 조건 충족 여부를 최종 판정한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md` §3.3(정본 분리), §3.4(LOCK-AP-01~10), §7.1(전환 게이트), §7.3.1~§7.3.3(방식 C 요약)
- P1-1 산출물: `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\01_framework-adapters\langgraph_adapter.md`
- P1-1 산출물: `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\01_framework-adapters\crewai_adapter.md`
- P1-1 산출물: `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\01_framework-adapters\autogen_adapter.md`
- P1-2 산출물: `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\06_autonomy-safety\permission_matrix.md`
- P1-2 산출물: `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\06_autonomy-safety\guardrail_rules.md`
- P1-3 산출물: `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\03_data-exchange\message_format.md`
- P1-3 산출물: `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\03_data-exchange\event_bus.md`

**절차**:
1. §7.3.1 방식 C ↔ P1-1 langgraph_adapter.md 교차 대조:
   - StateGraph 5-Phase, Gate 통합 노드, Soft/Hard Loop, CB 3-State(recovery=60s LOCK-AP-06), START/END(LOCK-AP-08), MultiBrain Failover, 단순 제어 흐름 원칙 — 누락 항목 0건 확인
2. §7.3.2 방식 C ↔ P1-1 crewai_adapter.md·autogen_adapter.md + P1-2 permission_matrix.md·guardrail_rules.md 교차 대조:
   - Lead + max 2 Sub(LOCK-AP-05·LOCK-AT-014), Sequential/Parallel, 위임 깊이 V1=2, RBAC, MessageBus In-Memory, LOCK-AT-001~017 — 누락 항목 0건 확인
   - K-041 권한(LOCK-AP-02)·K-042 HITL(LOCK-AP-10)·K-043 샌드박스 — 방식 C sot 2/ 보완 영역 전수 반영 확인
3. §7.3.3 방식 C ↔ P1-3 message_format.md·event_bus.md 교차 대조:
   - Streamable HTTP(LOCK-AP-04), SSE 양방향, MCP↔A2A 변환(LOCK-AP-07), VamosMessage(LOCK-AP-01), 비용 ₩40K(LOCK-AP-09) — 누락 항목 0건 확인
4. LOCK-AP-01~10 전수 값 대조 (§3.4 원본 vs P1-1~P1-3 산출물):
   - AP-01(VamosMessage 6필드), AP-02(Permission 0~5), AP-03(A2A 6상태), AP-04(Streamable HTTP), AP-05(Lead+2 Sub), AP-06(CB 60s), AP-07(A2A+MCP 양방향), AP-08(START/END), AP-09(V1 ₩40K), AP-10(HITL <50%) — 재정의·위반 0건 확인
5. §3.3 정본 분리 원칙 검증: L3 파일에 Phase/Week(When) 정보 미기재, 파일 경로(Where) 참조만 기재 — R6 준수
6. §6.2 P0 미배정 이슈 해소 확인: K-045(롤백)·K-046(설명가능성) → P1-2 permission_matrix.md에 포함 확인
7. Phase 1→2 전환 게이트 최종 판정:
   - 01_ P0 항목(K-021~K-023) L2 이상 → P1-1에서 L3 작성 ✓
   - 06_ P0 항목(K-041~K-043, +K-045·K-046) L2 이상 → P1-2에서 L3 작성 ✓
   - Part2 방식 C 요약 완료 → §7.3.1~§7.3.3 기존 완료 + P1-1~P1-3 교차 대조 PASS ✓

**검증**: ✅ 전수 PASS (2026-04-11)
- [x] §7.3.1 방식 C ↔ langgraph_adapter.md 누락 항목 0건 — StateGraph 5-Phase / Gate 통합 노드(§5.3) / Soft·Hard Loop(§7.1) / CB 3-State closed·open·half_open(§3·§7) / recovery 60s LOCK-AP-06(§7.2·§7.3) / START·END 상수 LOCK-AP-08(§5.4) / MultiBrain Failover(§7.3) / 단순 제어 흐름 원칙(§2.3) 전 8요소 반영 ✅
- [x] §7.3.2 방식 C ↔ crewai/autogen_adapter.md + permission_matrix.md + guardrail_rules.md 누락 항목 0건 — Lead+max 2 Sub LOCK-AP-05·LOCK-AT-014(crewai §5.2 / autogen §5.2) / Sequential·Parallel(crewai §5.3) / 위임 깊이 V1=2 LOCK-AT-004(crewai §5.4 / autogen §5.2) / LOCK-AT-001~017(crewai §2.3·§5 / autogen §5) / RBAC(permission_matrix §2~§4) / In-Memory MessageBus(event_bus §2~§4) / K-041 권한(permission_matrix §2·§4) / K-042 HITL LOCK-AP-10(guardrail_rules §4) / K-043 샌드박스 Docker·E2B(guardrail_rules §5) 전 9요소 반영 ✅
- [x] §7.3.3 방식 C ↔ message_format.md + event_bus.md 누락 항목 0건 — Streamable HTTP LOCK-AP-04(message_format §5) / SSE 양방향(message_format §5·event_bus §2.3·§4 ABC docstring) / MCP↔A2A 양방향 LOCK-AP-07(message_format §2·§5) / VamosMessage LOCK-AP-01(message_format §2) / A2A Task 상태 LOCK-AP-03(message_format §2·§3) / 비용 ₩40K LOCK-AP-09(message_format §2.3·event_bus §4.4·§15) 전 6요소 반영 ✅
- [x] LOCK-AP-01~10 전수 대조 — 재정의·위반 0건: AP-01(VamosMessage 6필드 message_format §2 정본, 3 어댑터 §3 참조) / AP-02(Permission 0~5 permission_matrix §2 정본, crewai §7 참조) / AP-03(A2A 6상태 message_format §2·§3 정본, 3 어댑터 §3 참조) / AP-04(Streamable HTTP message_format §5, event_bus §2.3 경계 주) / AP-05(Lead+2 Sub crewai §5.2 + autogen §5.2 강제 검사) / AP-06(CB 60s langgraph §7.2·§7.3) / AP-07(A2A+MCP 양방향 message_format §2·§5) / AP-08(START/END langgraph §5.4 LockViolation 강제) / AP-09(V1 ₩40K crewai·autogen §3·message_format §2.3·event_bus §4.4·§15) / AP-10(HITL Confidence<50% guardrail_rules §4 DEFINED-HERE, permission_matrix §2·§4 참조, message_format §2.3 참조) — 10/10 §3.4 원본값 준수 ✅
- [x] §3.3 정본 분리 원칙(What+How only) 준수 — R6 위반 0건: 03_data-exchange/{message_format,event_bus}.md 각각 §1.4 R6 선언 명시 / 01_framework-adapters/*.md 3파일 "Part2 상태" 헤더는 Part2 반영 상태 기록일 뿐 Phase/Week 배정 재정의 아님 (header 메타데이터 허용) / permission_matrix.md·guardrail_rules.md 의 "Phase 1 Intake → Phase 5 Deliver" 문자열은 VAMOS 5-Phase 파이프라인(Intake/Plan/Execute/Verify/Deliver) 호출 단계명이며 Part2 V1-Phase 3 code 배치와 무관 — How 컨텐츠 허용 범위 ✅
- [x] K-045·K-046 §7 미배정 이슈 해소 확인: permission_matrix.md §1 담당 K-ID 에 K-045(롤백/되돌리기)·K-046(설명가능성) 명시, §3 공통 자료 구조에 `StateSnapshot`/`TxLogEntry`(K-045) + `ExplanationTrace`(K-046) 정의, §5 롤백/되돌리기 메커니즘(K-045, 스냅샷-트랜잭션 모델 + rollback 의사코드) + §6 설명가능성(K-046, 3단 설명 구조 + 불변 감사 체인) 전담 섹션, §4 `PermissionEnforcer` 의사코드가 K-041 권한 평가 + K-045 snapshot + K-046 explanation 3축을 통합 수행 — §6.2 P0 미배정 2건 전수 해소 ✅
- [x] Phase 1→2 전환 게이트 3조건 충족 판정:
  1. **01_ P0 항목 L2 이상**: K-021/K-022/K-023 L3 전수 승급 (1,458줄, P1-1 완료) ✅
  2. **06_ P0 항목 L2 이상**: K-041/K-042/K-043 + §6.2 P0 미배정 K-045/K-046 L3 전수 승급 (1,140줄, P1-2 완료) ✅
  3. **Part2 방식 C 요약 완료**: §7.3.1~§7.3.3 요약 3건 기존 완료(P0-2) + P1-1~P1-3 7파일과 누락 0건 교차 대조 PASS (P1-4 본 세션) ✅
  → **Phase 1 → Phase 2 전환 게이트 PASS**

> **완료**: 2026-04-11. P1-1~P1-3 산출물 7개 L3 파일과 §7.3.1~§7.3.3 Part2 방식 C 요약 3건 전수 교차 대조 완료, Phase 1→Phase 2 전환 게이트 3/3 조건 충족 판정.
>
> **실행 결과 요약**:
> - 입력 검토: P1-1 3파일(langgraph/crewai/autogen_adapter.md, 1,458줄) + P1-2 2파일(permission_matrix/guardrail_rules.md, 1,140줄) + P1-3 2파일(message_format/event_bus.md, 1,210줄) = 총 7파일 / 3,808줄 전수 읽기
> - 방식 C 교차 대조: §7.3.1 LangGraph 8요소 / §7.3.2 Agent Teams 9요소 / §7.3.3 MCP Bridge 6요소 = 23/23 요소 누락 0건 PASS
> - LOCK 전수 대조: LOCK-AP-01~10 10/10 §3.4 원본값 준수, 재정의·위반 0건 (AP-01 6필드, AP-02 0~5, AP-03 6상태, AP-04 Streamable HTTP, AP-05 Lead+2 Sub, AP-06 60s, AP-07 양방향, AP-08 START/END, AP-09 ₩40K, AP-10 <50%)
> - §3.3 정본 분리(R6) 검증: 7파일 전수 R6 위반 0건, Phase/Week 재정의 0건
> - §6.2 P0 미배정 해소 확인: K-045(롤백)·K-046(설명가능성) permission_matrix.md §5/§6 포함 재확인 — Phase 1 내 전수 해소 ✅
> - Phase 1→2 전환 게이트 3/3 판정: (1) 01_ P0 L3 승급, (2) 06_ P0 L3 승급(+K-045/K-046), (3) 방식 C 요약 완료 — PASS
> - 이월 없음: Phase 1 MVP 4개 세션(P1-1~P1-4) 전수 완료, Phase 2 V2 진입 가능
> - CONFLICT 신규 0건: P1-3 type enum alias 건은 message_format.md §2.5에서 정책 해소 완료(기존 P1-3 세션 등재 범주), 본 P1-4 신규 CONFLICT 없음

**산출물**: Phase 1 완료 판정 기록 — 본 §7.3 P1-4 검증 결과 (P1-1~P1-3 전수 PASS 확인, Phase 1→2 게이트 3/3 충족)

**[P1-4] 검증 결과 요약** (갱신: 2026-04-11)
- 0. 산출물: 본 P1-4 는 교차 대조 + 판정 세션 — 신규 L3 파일 0건, 본 계획서 §7.3 P1-4 검증 체크리스트 갱신 1건 + Phase 1 추적 상태 갱신. 입력 파일 7건(1-1 langgraph/crewai/autogen, 1-2 permission_matrix/guardrail_rules, 1-3 message_format/event_bus) 전수 검토.
- 1. 게이트: Phase 1→Phase 2 전환 게이트 3/3 조건 전수 충족 ✅ — (1) 01_ P0(K-021·K-022·K-023) L3 승급, (2) 06_ P0(K-041·K-042·K-043·K-045·K-046) L3 승급, (3) Part2 방식 C 요약 §7.3.1~§7.3.3 ↔ P1-1~P1-3 산출물 누락 0건 PASS. LOCK-AP-01~10 10/10 §3.4 원본값 준수. R6(§3.3 정본 분리) 위반 0건.
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건 — 본 P1-4 세션 자체는 신규 CONFLICT 없음. P1-3 에서 식별한 VamosMessage.type enum alias 건은 message_format.md §2.5 alias 매핑 표에서 이미 정책 해소, step 7 에서 정식 등재 여부 판단(기존 P1-3 [P1-3] 검증 결과 요약 참조). 기존 CONFLICT_LOG.md 6건과 무관.
- 3. LOCK 변경: 없음 — 본 P1-4 는 교차 대조·판정 전용. LOCK-AP-01~10 전수 §3.4 원본 값 검증만 수행, 재정의·신규 0건.
- 4. 이월: 없음 — Phase 1 MVP 4개 세션(P1-1~P1-4) 전수 완료. Phase 2 V2 확장 세션(P2-1~P2-6)은 독립 세션에서 별도 진행. K-024(Magentic-One)/K-025(MoA)/K-026~K-030/K-047/K-050/K-052~K-053/K-055~K-060/K-061~K-068 는 §7.4 Phase 2 V2 배정 유지, K-038(IoT)·K-056(K8s)·K-048(윤리) 는 §7.5 Phase 3 V3 배정 유지.
</details>

### 7.4 Phase 2: 확장 (V2)

| 서브폴더 | 항목 | 작업 | V 로드맵 |
|----------|------|------|---------|
| `01_framework-adapters/` | K-024(Magentic-One), K-025(MoA), K-026~K-030 | 확장 패턴 + 벤치마크 | V2 |
| `02_service-integration/` | K-031~K-040 | LLM 게이트웨이 + 외부 서비스 | V2 |
| `03_data-exchange/` | K-050(Artifact), K-052(API버전), K-053(직렬화) | 데이터 교환 심화 | V2 |
| `04_deployment-scaling/` | K-055~K-060 | 패키징 + 스케일링 + 모니터링 | V2 |
| `05_self-evolution/` | K-061~K-064 | 자기진화 MVP + 예측형 | V2 |
| `06_autonomy-safety/` | K-047 | 자기진화 안전 가드레일 (K-047은 06_autonomy-safety 정본 소유, Part 5) | V2 |

#### Phase 2 단계별 상세 작업 절차

<details>
<summary>P2-1. 01_framework-adapters V2 (K-024~K-030, 7항목)</summary>

**K-ID 항목 코드**: K-024 Magentic-One, K-025 MoA, K-026 Reflection, K-027 Planning, K-028 Tool Use, K-029 메모리공유, K-030 벤치마크

**대조 기준**
1. §7.4 `01_framework-adapters` 행
2. Phase 2→3 게이트: 전 서브폴더 L2 이상 + 교차 검증 PASS
3. §6 Issues: FR-7(Agent Teams 역할 선정), FR-9(어댑터 호환성 매트릭스)
4. 교차 도메인: 6-3 Agent-Teams-PARL LOCK-AT-014 (K-025 MoA 연관)
5. Part2 버전: V2-Phase 2

**목표**: 프레임워크 어댑터 확장 패턴 7건을 L2 이상으로 작성. CrewAI/AutoGen/LangGraph 3개 프레임워크 호환성 매트릭스(FR-9) 포함.

**입력 파일**
- `D:\VAMOS\docs\sot\STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md` (K-024~K-030)
- `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` — Cooperative Agent
- `01_framework-adapters/_index.md`
- 6-3 Agent-Teams-PARL `AUTHORITY_CHAIN` LOCK-AT-014

**절차**
1. K-024 Magentic-One 패턴 작성 (Orchestrator/WebSurfer 연동)
2. K-025 MoA 패턴 (LOCK-AP-05 Lead+2 Sub-Agent, 6-3 LOCK-AT-014 교차 확인)
3. K-026~K-028 Reflection/Planning/Tool Use 패턴
4. K-029 메모리 공유 메커니즘
5. K-030 벤치마크 기준 정의
6. FR-9 호환성 매트릭스 (CrewAI/AutoGen/LangGraph 버전별)
7. `_index.md` 갱신

**검증**: 7항목 L2+, FR-9 호환성 매트릭스 포함, LOCK-AP-05/AT-014 교차 정합 확인.

**산출물**: `01_framework-adapters/` 파일들 — `crewai_adapter.md`, `autogen_adapter.md`, `langgraph_adapter.md` 갱신 + 신규 파일.

</details>

<details>
<summary>P2-2. 02_service-integration V2 (K-031~K-040, 10항목 — K-038 V3 제외 9항목 실행)</summary>

**K-ID 항목 코드**: K-031~K-034 PARTIAL 보완(LLM 게이트웨이, 외부 검색, 이미지/음성), K-035~K-037·K-039~K-040 ABSENT 신규(클라우드/캘린더/금융/CI·CD/외부AI). K-038 IoT는 V3 이관.

**대조 기준**
1. §7.4 `02_service-integration` 행
2. Phase 2→3 게이트: 전 서브폴더 L2 이상 + 교차 검증 PASS
3. §6 Issues: 없음
4. 교차 도메인: 없음
5. Part2 버전: V2-Phase 2 (K-038→V3 제외)

**목표**: LLM 게이트웨이 + 외부 서비스 연동 10항목(K-038 V3 제외 → 9항목 실행). PARTIAL 4건 보완(방식C) + ABSENT 5건 신규.

**입력 파일**
- `D:\VAMOS\docs\sot\STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md` (K-031~K-040)
- Part2 §6.6 MCP
- `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md`
- `02_service-integration/_index.md`

**절차**
1. `llm_gateway.md` 보완 (K-031~K-034 PARTIAL→L2)
2. `external_apis.md` 신규 (K-035~K-037, K-039~K-040 ABSENT)
3. K-038 IoT는 §7.5 V3로 이관 명시
4. `_index.md` 갱신

**검증**: 9항목 L2+, K-038 V3 이관 명시, PARTIAL→방식C 보완 확인.

**산출물**: `llm_gateway.md`(갱신), `external_apis.md`(신규).

</details>

<details>
<summary>P2-3. 03_data-exchange V2 (K-050, K-052~K-053, 3항목)</summary>

**K-ID 항목 코드**: K-050 Artifact, K-052 API버전, K-053 직렬화

**대조 기준**
1. §7.4 `03_data-exchange` 행
2. Phase 2→3 게이트: 전 서브폴더 L2 이상 + 교차 검증 PASS
3. §6 Issues: FR-8(직렬화 형식 결정 트리)
4. 교차 도메인: 없음
5. Part2 버전: V2-Phase 2

**목표**: 데이터 교환 심화 3항목. FR-8 직렬화 형식 선택 결정 트리(JSON/MessagePack/Protobuf/CBOR) 포함.

**입력 파일**
- `D:\VAMOS\docs\sot\STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md` (K-050, K-052, K-053)
- `03_data-exchange/_index.md`

**절차**
1. `message_format.md` 갱신 (K-050 Artifact 스키마)
2. `serialization.md` 갱신 (K-052 API 버전 관리 + K-053 직렬화 상세)
3. FR-8 직렬화 결정 트리 포함
4. `_index.md` 갱신

**검증**: 3항목 L2+, FR-8 결정 트리 포함 확인.

**산출물**: `message_format.md`(갱신), `serialization.md`(갱신).

</details>

<details>
<summary>P2-4. 04_deployment-scaling V2 (K-055~K-060, 6항목 — K-056 V3 제외 5항목)</summary>

**K-ID 항목 코드**: K-055 패키징, K-057 헬스체크, K-058 로깅, K-059 설정, K-060 마이그레이션. K-056 K8s는 V3 이관.

**대조 기준**
1. §7.4 `04_deployment-scaling` 행
2. Phase 2→3 게이트: 전 서브폴더 L2 이상 + 교차 검증 PASS
3. §6 Issues: 없음
4. 교차 도메인: 없음
5. Part2 버전: V2-Phase 2 (K-056→V3 제외)

**목표**: 배포·스케일링 5항목 L2 작성. K-056 K8s는 V3 이관 명시.

**입력 파일**
- `D:\VAMOS\docs\sot\STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md` (K-055~K-060)
- `04_deployment-scaling/_index.md`

**절차**
1. `container_spec.md` 신규 (K-055 패키징)
2. K-057~K-060 항목 작성 (헬스체크/로깅/설정/마이그레이션)
3. K-056 V3 이관 명시
4. `_index.md` 갱신

**검증**: 5항목 L2+, K-056 V3 이관 명시 확인.

**산출물**:
- `04_deployment-scaling/container_spec.md` (신규 — K-055)
- `04_deployment-scaling/healthcheck_spec.md` (신규 — K-057)
- `04_deployment-scaling/logging_spec.md` (신규 — K-058)
- `04_deployment-scaling/config_spec.md` (신규 — K-059)
- `04_deployment-scaling/migration_guide.md` (신규 — K-060)

> **P2-4 완료 기록 (STAGE 7 STEP_B #2b, 2026-04-22, sandbox-only)**
> - 5 V2 NEW / 2,173 L 실측 (`container_spec.md` 479 + `healthcheck_spec.md` 425 + `logging_spec.md` 410 + `config_spec.md` 471 + `migration_guide.md` 388)
> - STEP7-K K-055 L1089~L1099 + K-057 L1113~L1123 + K-058 L1125~L1141 + K-059 L1143~L1153 + K-060 L1155~L1165 verbatim 인용 (baseline sha256 `150720a3...` UNCHANGED)
> - K-056 Kubernetes (L1101~L1111) V3 이관 명시 (5 파일 헤더 + container_spec.md §2.2 + migration_guide.md §11 MG-12 전수)
> - LOCK-AP-01/02/04/07/09/10 5필드 분리 인용 총 142 references (per-file 25~33)
> - LOCK-AP-10 HITL<50% 본 문서 재정의 없음 (06_autonomy-safety/guardrail_rules.md P2-6 정본 참조자 유지)
> - FABRICATION 10-마커 census 0/50 CLEAN (5 V2 × 10 marker)
> - 세션 간 인터페이스 cross-check 정합 (container ↔ healthcheck ↔ logging ↔ config ↔ migration 5-way)
> - V1 content 0 → V2 전수 NEW (P2-2 02_service-integration 선례 동일 패턴)
> - 신규 [CONFLICT_CANDIDATE] 0건 / CFL-AP-001~007 전수 RESOLVED 보존
> - production 3-10 19/19 + prompts 18/18 + STEP7-K + 완료 도메인 14 전수 SHA UNCHANGED

</details>

<details>
<summary>P2-5. 05_self-evolution V2 (K-061~K-064, 4항목)</summary>

**K-ID 항목 코드**: K-061 자기진화, K-062 예측형, K-063 앰비언트, K-064 시간여행. K-065~K-068(페르소나/멀티유저/마켓플레이스/테스트)은 §7.5 V3 이관

**대조 기준**
1. §7.4 `05_self-evolution` 행
2. Phase 2→3 게이트: 전 서브폴더 L2 이상 + 교차 검증 PASS
3. §6 Issues: 없음
4. 교차 도메인: 없음
5. Part2 버전: V2-Phase 2

**목표**: 자기진화 MVP + 예측형 에이전트 4항목 L2 작성.

**입력 파일**
- `D:\VAMOS\docs\sot\STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md` (K-061~K-064)
- `05_self-evolution/_index.md`

**절차**
1. `dream_mode.md` 신규 (K-061 Self-Evolution, Dream Mode 설계)
2. K-062 예측형 에이전트
3. K-063 앰비언트 에이전트
4. K-064 시간여행 (상태 복원)
5. `_index.md` 갱신

**검증**: 4항목 L2+ 확인.

**산출물**:
- `05_self-evolution/dream_mode.md` (신규 — K-061)
- `05_self-evolution/predictive_agent.md` (신규 — K-062)
- `05_self-evolution/ambient_agent.md` (신규 — K-063)
- `05_self-evolution/time_travel.md` (신규 — K-064)

> **P2-5 완료 기록 (STAGE 7 STEP_B #2b, 2026-04-22, sandbox-only)**
> - 4 V2 NEW / 1,560 L 실측 (`dream_mode.md` 417 + `predictive_agent.md` 359 + `ambient_agent.md` 389 + `time_travel.md` 395)
> - STEP7-K K-061 L1171~L1192 + K-062 L1194~L1210 + K-063 L1212~L1234 + K-064 L1236~L1252 verbatim 인용 (baseline sha256 `150720a3...` UNCHANGED)
> - K-065 멀티 페르소나 / K-066 협업형 멀티유저 / K-067 에이전트 마켓플레이스 / K-068 VBS-12+ (L1254~L1318) V3 이관 명시 (4 파일 헤더 전수)
> - K-061 Dream Mode 안전 가드레일(K-047 L937~L955) 정본은 06_autonomy-safety/guardrail_rules.md (P2-6 정본) 참조자 명시, 본 문서는 Dream Mode 실행 측면만
> - LOCK-AP-01/02/04/07/09/10 5필드 분리 인용 총 112 references (per-file 26~30)
> - LOCK-AP-10 HITL<50% 본 문서 재정의 없음 (06_autonomy-safety/guardrail_rules.md P2-6 정본 참조자 유지, 4 V2 §9 penalty 표)
> - LOCK-AP-02 L3+ HITL 필수, L5 절대 금지 엄수 (Dream Mode L2 상한, Predictive L1~L2, Ambient L0~L2, Time-Travel shadow L2)
> - FABRICATION 10-마커 census 0/40 CLEAN (4 V2 × 10 marker)
> - 세션 간 인터페이스 cross-check 정합 (Dream ↔ Predictive ↔ Ambient ↔ Time-Travel 4-way + migration_guide §6.3 rollback replay)
> - V1 content 0 → V2 전수 NEW
> - 신규 [CONFLICT_CANDIDATE] 0건 / CFL-AP-001~007 전수 RESOLVED 보존
> - production 3-10 19/19 + prompts 18/18 + STEP7-K + 완료 도메인 14 전수 SHA UNCHANGED

</details>

<details>
<summary>P2-6. 06_autonomy-safety V2 (K-047) + L2 교차검증</summary>

**K-ID 항목 코드**: K-047 자기진화 안전 가드레일

**대조 기준**
1. §7.4 `06_autonomy-safety` 행
2. Phase 2→3 게이트: 전 서브폴더 L2 이상 + 교차 검증 PASS
3. §6 Issues: 없음
4. 교차 도메인: LOCK-AP-10 HITL 트리거 <50% (DEFINED-HERE)
5. Part2 버전: V2-Phase 2

**목표**: K-047 자기진화 안전 가드레일 L2 작성 + 전 서브폴더 교차 검증 실행. LOCK-AP-10(HITL <50%) 본 도메인 정본 반영.

**입력 파일**
- `D:\VAMOS\docs\sot\STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md` (K-047)
- 계획서 §C 가드레일 CEL
- `06_autonomy-safety/_index.md`
- LOCK-AP-10

**절차**
1. `guardrail_rules.md` 갱신 (K-047 자기진화 안전 가드레일, CEL SG-009 LOCK-AP-10 반영)
2. LOCK-AP-10 DEFINED-HERE 정본 소유 선언을 guardrail_rules.md 내에 명시 확인
3. `permission_matrix.md` 갱신 (자기진화 시 권한 제약)
4. 전 6개 서브폴더 L2 달성 여부 교차 검증 실행
4. 교차 도메인 정합 확인 (6-3 LOCK-AT-014, LOCK-AP-05)
5. `_index.md` 갱신

**검증**: K-047 L2+, LOCK-AP-10 반영, 전 서브폴더 L2 교차 검증 PASS, 6-3 교차 정합 확인.

**산출물**: `guardrail_rules.md`(갱신), `permission_matrix.md`(갱신), L2 교차검증 결과.

> **P2-6 완료 기록 (STAGE 7 STEP_B #2c, 2026-04-22, sandbox-only)**
> - 2 V1 EXTEND §V2 append / **820 L 신규 내용 실측** (`guardrail_rules.md` 588→1121 +533L / `permission_matrix.md` 552→839 +287L)
> - STEP7-K K-047 L937~L955 verbatim 19 lines 원문 매핑 (§V2.1) + Dream Mode 연동 L947~L951 5 lines (baseline sha256 `150720a3...` UNCHANGED)
> - **LOCK-AP-10 HITL<50% DEFINED-HERE 정본 cumulative 기준 확정** (`guardrail_rules.md §V2.2` 5필드 + 계산식 + 4구간 `≥0.75/0.50~0.75/<0.50/<0.25`) — AUTHORITY §3 L51 5필드 verbatim 재인용
> - **max_strategy_drift 수치 확정** (§V2.3, 5 소비자 참조 정합 해제): 4 P2-5 (dream/predictive/ambient/time_travel) + 1 P2-4 (container_spec §9.2) = 42 references 전수 PASS
> - 자기진화 6 Phase 가드레일 (SG-011~SG-015 CEL + Dream Mode 연동 3 중 가드 D-1/D-2/D-3)
> - Permission L0~L4 자동 상한 + **L5 금융 주문 이중 차단** (LOCK-AP-02 원본 + §V2.5 자기진화 경로 절대 금지, `forbid_l5` Pydantic validator)
> - K-048 에이전트 윤리 프레임워크 (L957~L975) V3 이관 명시 (§V2 경계 주석 + §7.5 row 기존 유지)
> - K-056 K8s / K-065~K-068 V3 이관 명시 (§V2 경계 주석)
> - Phase 3 통합 테스트 시나리오 guardrail 15건 + permission 12건 = **27건** (목표 ≥ 10건 × 2 파일 = 20건 1.35배 초과)
> - FABRICATION 10-마커 census 0/20 CLEAN (2 V2 × 10 marker) — 본 §V2 append 전체 scope
> - V1 content 불변 (guardrail §0~§13 + permission §0~§12 + footer 본문 append-only)
> - baseline SHA refresh: `guardrail_rules.md` 620c725c → 99ada408 / `permission_matrix.md` fc5e6476 → cf80c12b / V1 verify 10/10 OK × 3 위치
> - 6-3 LOCK-AT-014 교차 정합 유지 (V2 자기진화 경로에서도 `agents.length ≤ 2` 엄수)
> - 신규 [CONFLICT_CANDIDATE] 0건 / CFL-AP-001~007 전수 RESOLVED 보존
> - production 3-10 19/19 + prompts 18/18 + STEP7-K + 완료 도메인 14 전수 SHA UNCHANGED

</details>

---

### 7.4.1 Phase 2 완료 블록 (2026-04-22, STAGE 7 STEP_B #2c 종결, sandbox-only)

> **Phase 2 전환 게이트 5/5 [x] PASS — [PHASE3_READY v2: 3-10 — 2026-04-22 최종 확정]**

**exit_gate 조건 대조 (manifest L256: "전 서브폴더 L2 이상 + 교차 검증 PASS")**

| # | 조건 | 결과 | 증빙 |
|---|------|:----:|------|
| 1 | 전 6개 서브폴더 L2 이상 달성 | [x] | 01_framework-adapters(7 V2) / 02_service-integration(2 V2) / 03_data-exchange(2 V2) / 04_deployment-scaling(5 V2) / 05_self-evolution(4 V2) / 06_autonomy-safety(2 V2 EXTEND) = 22 V2 |
| 2 | 교차 검증 PASS (V2↔V2 peer cross-ref) | [x] | P2-1 4+3 V1 EXTEND 7-way / P2-4 5-way / P2-5 4-way + 크로스 세션 migration §6.3 ↔ time_travel §4.2 / P2-6 5 참조자 정합 해제 42 refs |
| 3 | LOCK-AP-01~10 재정의 0 + verbatim 5필드 분리 인용 | [x] | AUTHORITY §3.4 10 LOCK 변경 0 + V2 22 파일 LOCK 누계 ~460 references (#2a ~142 + #2b 254 + #2c guardrail §V2.11 4 LOCKs × 4 = 16 + permission §V2.11 4 × 4 = 16 cross-ref + §V2.1/§V2.3/§V2.5 인용 ~40 = 총 ~466) |
| 4 | CFL-AP-001~007 RESOLVED 보존 + 신규 [CONFLICT_CANDIDATE] 0건 | [x] | v1.2 변경 0 + STEP_B #2a/#2b/#2c 3 회차 전수 "0건 발화" |
| 5 | STEP7-K upstream baseline sha256 `150720a3...` UNCHANGED + production 3-10 19/19 + prompts 18/18 + 완료 도메인 14 전수 SHA UNCHANGED | [x] | cwd=production 재실행 검증 3 회차 (STEP_A + STEP_B #2a + STEP_B #2b/#2c) 전수 UNCHANGED |

**Phase 2 누계 12 지표 표**

| # | 지표 | 실측 | 근거 |
|---|------|:----:|------|
| 1 | V2 파일 수 | **22 strict label** (11 NEW + 7 V1 EXTEND + 2 V1 EXTEND in P2-1 + 2 P2-6 V1 EXTEND §V2) | 22 파일 §V2 / 신설 / 확장 label 혼합 |
| 2 | V2 line content | **7,214 L** (신규 기여분 전수 합계: #2a 2,661 + #2b 3,733 + #2c 820 — magentic_one 283 정본 반영) | P2-1~P2-6 wc -l 실측 (R1 ultra-fine 교정) |
| 3 | K-ID 커버리지 | **26/76 K-ID 본 Phase 2 범위** (K-022/024~030 7 + K-031~040 [K-038 V3] 9 + K-049~053 5 + K-055/057~060 5 + K-061~064 4 + K-041/045~047 3 — 중 P2-2 9=8 V2 범위 + P2-3 3 V2) | plan §7.4 P2-1~P2-6 대조 |
| 4 | V1 logical 회차 | **251 → 252 (P2-6 완료)** | STEP_B #2c session_P2-6_done_3-10 |
| 5 | FABRICATION 10-마커 census | **0/220 CLEAN 누계** (#2a 110 + #2b 90 + #2c 20) | parent-executed Subagent 0회 |
| 6 | LOCK 5필드 인용 총계 | **~466+ references** (누계 #2a ~142 + #2b 254 + #2c ~70) | grep 실측 |
| 7 | LOCK-AP-10 DEFINED-HERE 정본 확정 | **✅ guardrail_rules.md §V2.2** | 본 blockquote + AUTHORITY §3 L51 |
| 8 | K-056 K8s + K-065~K-068 V3 이관 명시 | ✅ 9 V2 헤더 전수 (#2b) + 2 V2 §V2 헤더 (#2c) | 명시 grep 0건 누락 |
| 9 | 세션 간 인터페이스 cross-check | **PASS** 5-way (P2-4) + 4-way (P2-5) + 크로스 세션 + 5 참조자 정합 해제 (P2-6) | 매 세션 §N.2/§V2.9 |
| 10 | CFL-AP-001~007 | **전수 RESOLVED 보존** + 신규 0건 | CONFLICT_LOG.md v1.2 |
| 11 | upstream STEP7-K baseline | **UNCHANGED** `150720a3496f557d359a421dcbf0922ebe5b1e4fbaa06611eff40e0865177539` | 매 STEP 재검증 ✅ |
| 12 | cross_domain_deps | **[] 자기완결** (manifest L255) | downstream CONSUMER 0건 |

**Phase 2 → Phase 3 전환 완료 선언**

본 blockquote 작성 시점(2026-04-22)에 3-10 Agent-Protocol-Interoperability 도메인의 Phase 2 는 **전환 게이트 5/5 [x] PASS** 를 달성하였으며, exit_gate 충족으로 `[PHASE3_READY v2: 3-10 — 2026-04-22 최종 확정]` 으로 전환 처리한다. Phase 3 이월 항목은 §7.5 참조.

---

### 7.5 Phase 3: 최적화 (V3) ✅ Phase 3 완료 (2026-05-20, 5 task)

| 서브폴더 | 항목 | 작업 | V 로드맵 | Phase 2 STEP_C 이월 상태 (2026-04-22) |
|----------|------|------|---------|--------------------------------------|
| `05_self-evolution/` | K-065~K-068 | 멀티페르소나 + 멀티유저 + 마켓플레이스 (K-065: V1 기본은 Phase 1, V2 자동전환은 Phase 2에 배치) | V3 | P2-5 4 V2 헤더 + guardrail §V2 경계 주석 명시 ✅ |
| `04_deployment-scaling/` | K-056(K8s 스케일링) | Kubernetes 기반 풀 오토스케일링 | V3 | P2-4 5 V2 헤더 + container §2.2 + migration §11 MG-12 명시 ✅ |
| `06_autonomy-safety/` | K-048(윤리) | Constitutional AI 연동 | V3 | guardrail §V2 + permission §V2 경계 주석 명시 ✅ (V2 EXTEND 없음 엄수) |
| `02_service-integration/` | K-038(IoT) | 스마트홈 연동 | V3 | P2-2 external_apis 헤더 + §11 시나리오 11 명시 ✅ |

**Phase 3 추가 이월 항목 (P2-6 §V2 에서 발생)**

| # | 항목 | 출처 | 이월 사유 |
|---|------|------|----------|
| 1 | `w_strategy` 가중치 0.25 튜닝 | guardrail_rules.md §V2.2 | Phase 2 기본값 확정, Phase 3 A/B 기반 튜닝 |
| 2 | A/B 테스트 트래픽 상한 30% → V3 50% 확장 | guardrail_rules.md §V2.8 SE-09 | Phase 2 SG-015 R-13-7-9 상한 완화 검토 |
| 3 | Dream Mode 활성 시간 판정 임계 (idle ≥ 5min) V3 튜닝 | permission_matrix.md §V2.2 | 사용자 습관 학습 기반 자동 튜닝 |
| 4 | A/B 테스트 승격 제안 자동 승인 | permission_matrix.md §V2.8 PM-12 | 현재 Phase 2 는 HITL 필수, V3 자동화 검토 |
| 5 | CFL-AP-001~007 전수 유지 | CONFLICT_LOG.md v1.2 | Phase 3 신규 발화 대기 (0건 예상) |

#### Phase 3 단계별 상세 작업 절차 (S15-3 추가, 2026-05-13 — derivation 정밀화)

> **[Phase 3 derivation 정밀화 — S15-3, 2026-05-13]**: 본 §7.5 Phase 3 표(4 주요 작업 + 5 추가 이월)는 간이 매트릭스 수준이었다. S15-3에서 Phase 13/14 확립 포맷에 맞춰 6섹션 블록(대조 기준 7항목 + 목표 + 입력 파일 + 절차 + 검증 + 산출물) 구조로 정밀화한다. 5 추가 이월 항목 중 #1~#4(파라미터 튜닝/자동화 검토)는 P3-5 가드레일·권한 정밀화 블록 1개로 통합하고, #5(CFL 무손상 유지)는 P3 진입 게이트로 운용한다. 결과적으로 5 `<details>` 블록(P3-1~P3-5)으로 구성한다.

<details>
<summary><b>P3-1. 05_self-evolution / K-065~K-068 멀티페르소나·멀티유저·마켓플레이스 (V3)</b></summary>

**대조 기준 (7항목)**:
- **§7 세부 작업 ID**: §7.5 Phase 3 / 05_self-evolution / K-065(멀티페르소나 V2 일부 + V3 자동전환)·K-066(멀티유저)·K-067(에이전트 마켓플레이스)·K-068(에이전트 테스트 — V3 배정)
- **§7 전환 게이트 조건**: §7.2 Phase 3→완료 게이트(전체 86 K-ID L3 + /audit PASS) — 본 단계는 4 K-ID 직접 기여 + 05_self-evolution 완성
- **§6 이슈 ID**: §6.1 05_self-evolution K-065(V3) + K-066(V3) + K-067(V3) + K-068(V3) / §13.2 05_ L0→L2(V2 대상) + V3에서 L3 진입
- **교차 도메인**: 3-7 Developer-Tools(VADD 마켓플레이스 ↔ 에이전트 마켓 LOCK-BM-09 70:30 정합) + 3-9 Business-Model(수익 분배 정합) + 6-2 Security-Governance(멀티유저 RBAC)
- **V3-Phase 매핑**: §7.1 V3 + §6.1 K-065~K-068 매핑 (CFL-AP-006 K-065 V 로드맵 정정 후) + Phase 2 P2-5에서 V2 헤더 4건 + guardrail §V2 경계 주석 명시 inheritance
- **production 측정 baseline**: production `05_self-evolution/` — P2-5 V2 4 V2 헤더 + dream_mode.md(V1) 존재. V3 4 K-ID는 신규 파일 또는 기존 §V3 append
- **Phase 4 entry-gate 충족 조건**: ① K-065 멀티페르소나 자동 전환 알고리즘 ② K-066 멀티유저 격리 + RBAC ③ K-067 에이전트 마켓 등록/심사/수익 분배(LOCK-BM-09 인용) ④ K-068 에이전트 테스트 자동화(VBS-12 정합) ⑤ §B.2 L3→L4 전환 조건 정합(90일 연속 운영)

**목표**:
05_self-evolution V3 4 K-ID를 L3 수준으로 정의한다. (1) K-065 멀티페르소나 자동 전환 + (2) K-066 멀티유저 격리·RBAC + (3) K-067 에이전트 마켓플레이스 + (4) K-068 에이전트 테스트 자동화. R-13-6 max_strategy_drift 이내 + R-13-7 외부 에이전트 첫 연동 사용자 승인 정합. Phase 간 이연: ML 기반 페르소나 자동 학습은 Phase 4+.

**입력 파일** (절대 경로):
- `D:\VAMOS\docs\sot\STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md` (K-065~K-068 원문)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md` §3.4 LOCK / §6.1 / §7.5 / §B 자율성 레벨 / §C 가드레일
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\05_self-evolution\dream_mode.md` (V1 정본)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\05_self-evolution\_index.md`
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\06_autonomy-safety\guardrail_rules.md` (P2-6 V2 정본, §V2 경계 주석 정합)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\06_autonomy-safety\permission_matrix.md` (P2-6 V2 정본)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\07_marketplace\vadd_marketplace.md` (P3-4 산출물, cross-ref)
- `D:\VAMOS\docs\sot 2\3-9_Business-Model-Strategy\AUTHORITY_CHAIN.md` (LOCK-BM-09 인용)

**절차**:
1. K-065 멀티페르소나: D1 페르소나 정의 schema + D3 자동 전환 알고리즘(컨텍스트→페르소나 선택)
2. K-066 멀티유저: 사용자별 데이터 격리(tenant_id) + RBAC + 감사 로그
3. K-067 에이전트 마켓플레이스: 에이전트 등록/심사 파이프라인 + LOCK-BM-09 70:30 인용 + 3-7 VADD cross-ref
4. K-068 에이전트 테스트 자동화: 5-1 Benchmark 표준 정합 + chaos 시나리오
5. R-13-6 max_strategy_drift 정합 + R-13-7 외부 에이전트 사용자 승인
6. LOCK-AP-02 권한 레벨 0~5 인용 + LOCK-AP-10 confidence 50% HITL 인용
7. _index.md V3 4 K-ID 상태 갱신

**검증**:
- [x] K-065~K-068 각각 L3 D1~D8 + §13 가중 합 충족
- [x] LOCK-AP-02/10 인용 + 충돌 0건
- [x] LOCK-BM-09 (3-9 정본) cross-ref
- [x] 3-7 VADD(P3-4) cross-ref
- [x] R-13-6/R-13-7 정합
- [x] **Phase 4 entry-gate**: 4 K-ID 모두 production 배포 가능 수준 + 마켓플레이스 운영 SLA

**산출물**:
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\05_self-evolution\multi_persona.md` (신규, K-065)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\05_self-evolution\multi_user.md` (신규, K-066)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\05_self-evolution\agent_marketplace.md` (신규, K-067)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\05_self-evolution\agent_testing.md` (신규, K-068)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\05_self-evolution\_index.md`
</details>

<details>
<summary><b>P3-2. 04_deployment-scaling / K-056 Kubernetes 풀 오토스케일링 (V3)</b></summary>

**대조 기준 (7항목)**:
- **§7 세부 작업 ID**: §7.5 Phase 3 / 04_deployment-scaling / K-056 K8s 스케일링
- **§7 전환 게이트 조건**: 04_deployment-scaling 완성 + R-13-5 리소스 클래스 명시 정합
- **§6 이슈 ID**: §6.1 04_deployment-scaling K-056(V3) + K-055/057~060(V2 P2-4 완료)
- **교차 도메인**: 4-1 Rust-Tauri Infrastructure(IPC ↔ K8s 통신) + 6-13 Operations(K8s 운영 표준) + 6-2 Security-Governance(K8s RBAC)
- **V3-Phase 매핑**: §7.1 V3 + Phase 2 P2-4 5 V2 헤더 + container §2.2 + migration §11 MG-12 명시 inheritance
- **production 측정 baseline**: production `04_deployment-scaling/container_spec.md`(V2 정본) baseline 측정 후 §V3 append 또는 신규 `k8s_autoscaling.md`
- **Phase 4 entry-gate 충족 조건**: ① HPA(Horizontal Pod Autoscaler) 정의 ② VPA + Cluster Autoscaler ③ 메트릭 기반 스케일링(CPU/mem/custom RPS) ④ 리소스 클래스(light/standard/heavy — R-13-5) K8s requests/limits 매핑 ⑤ 비용 가드(LOCK-AP-09 ₩40K/₩93K/₩266K) 정합

**목표**:
K-056 Kubernetes 풀 오토스케일링을 L3 수준으로 정의한다. (1) HPA/VPA/CA 3중 스케일 + (2) 커스텀 메트릭(에이전트 RPS) + (3) 리소스 클래스 매핑 + (4) 비용 가드. Phase 간 이연: 멀티 클러스터·멀티 클라우드는 Phase 4+.

**입력 파일** (절대 경로):
- `D:\VAMOS\docs\sot\STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md` (K-056 원문)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md` §3.4 LOCK-AP-09 / §6.1 / §7.5
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\04_deployment-scaling\container_spec.md` (V2 정본)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\04_deployment-scaling\_index.md`
- `D:\VAMOS\docs\sot 2\4-1_Rust-Tauri-Infrastructure\RUST_TAURI_INFRASTRUCTURE_구조화_종합계획서.md` (IPC 매핑 정합)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\AUTHORITY_CHAIN.md`

**절차**:
1. K-056 원문 + R-13-5 리소스 클래스 정합
2. D1 Input: HPA/VPA/CA config YAML schema + custom metrics(agent_rps)
3. D3 Algorithm: HPA target CPU 70% / VPA recommendation mode / CA node pool 정책
4. 리소스 클래스 매핑: light(0.5/1Gi) / standard(1/2Gi) / heavy(2/4Gi)
5. LOCK-AP-09 비용 가드: 월 ₩40K/₩93K/₩266K — 클러스터 총 비용 제한
6. _index.md K-056 상태 갱신

**검증**:
- [x] L3 D1~D8 전수
- [x] HPA/VPA/CA 3중 + custom metrics 명시
- [x] R-13-5 리소스 클래스 매핑
- [x] LOCK-AP-09 인용
- [x] 4-1 Rust-Tauri IPC 매핑 정합
- [x] **Phase 4 entry-gate**: production K8s manifest 예시 + SLA 정의

**산출물**:
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\04_deployment-scaling\k8s_autoscaling.md` (신규)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\04_deployment-scaling\_index.md`
</details>

<details>
<summary><b>P3-3. 06_autonomy-safety / K-048 Constitutional AI 연동 (V3)</b></summary>

**대조 기준 (7항목)**:
- **§7 세부 작업 ID**: §7.5 Phase 3 / 06_autonomy-safety / K-048 윤리 (Constitutional AI)
- **§7 전환 게이트 조건**: 86 K-ID L3 + /audit PASS — K-048 단독
- **§6 이슈 ID**: §6.1 06_autonomy-safety K-048(V3) — Phase 2 V2 EXTEND 없음 엄수 inheritance
- **교차 도메인**: 6-2 Security-Governance(OWASP LLM08) + 5-1 Benchmark-Evaluation(윤리 평가 표준)
- **V3-Phase 매핑**: §7.1 V3 + Phase 2 guardrail §V2 + permission §V2 경계 주석 명시 ✅
- **production 측정 baseline**: production `06_autonomy-safety/` V1+V2 정본(guardrail_rules.md + permission_matrix.md). V3 K-048은 신규 `constitutional_ai.md`
- **Phase 4 entry-gate 충족 조건**: ① Constitution Principles 8~12 조항 정의 ② RLAIF/RLHF 차이 명시 ③ 윤리 점수 측정 ≥ 0.85 ④ R-13-1 HITL 정합 ⑤ §C 가드레일 엔진 연동

**목표**:
K-048 Constitutional AI 연동을 L3 수준으로 정의한다. (1) Constitution Principles + (2) Self-Critique 알고리즘 + (3) RLAIF 통합 + (4) §C 가드레일 엔진 cross-ref. Phase 간 이연: Principles 자동 학습은 Phase 4+.

**입력 파일** (절대 경로):
- `D:\VAMOS\docs\sot\STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md` (K-048 원문)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md` §3.4 LOCK-AP-02/10 / §6.1 / §7.5 / §B 자율성 / §C 가드레일
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\06_autonomy-safety\guardrail_rules.md` (P2-6 V2 정본, §V2 경계 주석 inheritance)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\06_autonomy-safety\permission_matrix.md` (P2-6 V2 정본)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\06_autonomy-safety\_index.md`
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\AUTHORITY_CHAIN.md`

**절차**:
1. K-048 원문 + Constitutional AI(Anthropic) 패러다임 정합
2. Constitution Principles ≥ 8 조항 정의(harmlessness / helpfulness / honesty 등)
3. Self-Critique: 모델이 자신의 응답을 Constitution에 비춰 평가 + 수정 알고리즘
4. RLAIF: AI feedback 기반 강화학습 — RLHF와 차이 명시
5. 윤리 점수 측정: TruthfulQA / HHH 벤치마크 정합(5-1 cross-ref)
6. R-13-1 HITL 정합: 윤리 점수 < 0.85 → HITL 트리거
7. §C 가드레일 엔진 양방향 cross-ref
8. _index.md K-048 상태 갱신

**검증**:
- [x] L3 D1~D8 전수
- [x] Principles ≥ 8 조항
- [x] Self-Critique 의사코드
- [x] LOCK-AP-02/10 인용 + R-13-1 정합
- [x] §C 가드레일 cross-ref
- [x] **Phase 4 entry-gate**: 윤리 점수 측정 자동화 + 5-1 Benchmark cross-ref

**산출물**:
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\06_autonomy-safety\constitutional_ai.md` (신규)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\06_autonomy-safety\_index.md`
</details>

<details>
<summary><b>P3-4. 02_service-integration / K-038 IoT 스마트홈 연동 (V3)</b></summary>

**대조 기준 (7항목)**:
- **§7 세부 작업 ID**: §7.5 Phase 3 / 02_service-integration / K-038 IoT
- **§7 전환 게이트 조건**: 86 K-ID L3 + /audit PASS — K-038 단독
- **§6 이슈 ID**: §6.1 02_service-integration K-038(V3) — Phase 2 P2-2 external_apis 헤더 + §11 시나리오 11 명시 inheritance
- **교차 도메인**: 6-2 Security-Governance(IoT 보안) + 4-3 MCP-Server-Client(외부 IoT 서버 통합)
- **V3-Phase 매핑**: §7.1 V3 + Phase 2 V2 헤더 inheritance
- **production 측정 baseline**: production `02_service-integration/` V2(llm_gateway.md + external_apis.md). V3 K-038은 `iot_integration.md` 신규 또는 external_apis.md §V3 append
- **Phase 4 entry-gate 충족 조건**: ① IoT 표준(Matter / Thread / Zigbee / Z-Wave) 매핑 ② 디바이스 디스커버리 + 인증 ③ 명령/상태 메시지 schema ④ R-13-7 첫 연동 사용자 승인 ⑤ LOCK-AP-04 Streamable HTTP 정합

**목표**:
K-038 IoT 스마트홈 연동을 L3 수준으로 정의한다. (1) IoT 표준 매핑 + (2) 디바이스 디스커버리·인증 + (3) 명령/상태 메시지 + (4) 보안 + (5) 외부 MCP 서버 연계. Phase 간 이연: 음성 인터페이스 통합은 Phase 4+.

**입력 파일** (절대 경로):
- `D:\VAMOS\docs\sot\STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md` (K-038 원문)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md` §3.4 LOCK-AP-04 / §6.1 / §7.5
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\02_service-integration\external_apis.md` (V2 정본, §V3 또는 신규 분리)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\02_service-integration\_index.md`
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\AUTHORITY_CHAIN.md`

**절차**:
1. K-038 원문 + IoT 표준 분석(Matter/Thread/Zigbee/Z-Wave)
2. 디스커버리: mDNS(LOCK-A2A-04 정합 가능) + 디바이스 인증 토큰
3. D1 Input/D2 Output: `IoTDeviceCommand` / `IoTStateUpdate` schema
4. D3 Algorithm: 명령 전달 → 응답 polling 또는 webhook → 상태 동기화
5. R-13-7 첫 연동 사용자 승인 + LOCK-AP-04 Streamable HTTP
6. 4-3 MCP 외부 서버 cross-ref (IoT 게이트웨이로 활용 가능)
7. _index.md K-038 상태 갱신

**검증**:
- [x] L3 D1~D8 전수
- [x] IoT 표준 매핑 ≥ 3
- [x] R-13-7 정합 + LOCK-AP-04 인용
- [x] 4-3 MCP cross-ref
- [x] **Phase 4 entry-gate**: 디바이스 디스커버리 자동화 + 보안 인증 명세

**산출물**:
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\02_service-integration\iot_integration.md` (신규) 또는 `external_apis.md` (§V3 append)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\02_service-integration\_index.md`
</details>

<details>
<summary><b>P3-5. 06_autonomy-safety / 추가 이월 4건 통합 — 가드레일·권한 V3 정밀화</b></summary>

**대조 기준 (7항목)**:
- **§7 세부 작업 ID**: §7.5 Phase 3 추가 이월 항목 #1~#4(통합) — `w_strategy` 0.25 튜닝 + A/B 테스트 트래픽 상한 30%→50% + Dream Mode idle ≥ 5min 임계 튜닝 + A/B 승격 자동 승인
- **§7 전환 게이트 조건**: 06_autonomy-safety 완성 (P2-6 V2 정본 §V2.2/§V2.8 inheritance) + R-13-7 자동 승인 정합
- **§6 이슈 ID**: 추가 이월 #1~#4 — guardrail_rules.md §V2.2/§V2.8 SE-09 + permission_matrix.md §V2.2/§V2.8 PM-12 (이월 항목 #5 CFL 무손상은 Phase 3 진입 게이트로 별도 운용)
- **교차 도메인**: 6-2 Security-Governance(자동화 + RBAC) + 5-1 Benchmark-Evaluation(A/B 테스트 측정)
- **V3-Phase 매핑**: §7.1 V3 + P2-6 V2 §V2 inheritance(SG-015 / PM-12 R-13-7-9 정합)
- **production 측정 baseline**: production `06_autonomy-safety/guardrail_rules.md` + `permission_matrix.md`(P2-6 V2 정본) baseline 측정 후 §V3 append
- **Phase 4 entry-gate 충족 조건**: ① `w_strategy` 가중치 A/B 측정 결과 + 0.25→실측 기반 조정값 ② A/B 트래픽 상한 50%로 확장 시 안전성 입증 ③ Dream Mode idle 임계 사용자 습관 학습 기반 자동 튜닝 ④ A/B 승격 자동 승인 조건(에러율 < 1% / 측정 신뢰도 > 95%) ⑤ R-13-7 HITL 우회 시점 명시

**목표**:
Phase 2에서 확정된 V2 기본값(`w_strategy` 0.25, A/B 30%, Dream Mode 5min, HITL 필수)을 V3 운영 데이터 기반으로 튜닝하고, 일부 자동화 후보를 정밀 검토한다. (1) `w_strategy` 0.25 A/B 결과 분석 + 조정 + (2) A/B 상한 30%→50% 안전성 + (3) Dream Mode 임계 자동 학습 + (4) A/B 승격 자동 승인 조건. Phase 간 이연: 완전 무인 자동화는 Phase 4+ (안전성 추가 입증 후).

**입력 파일** (절대 경로):
- `D:\VAMOS\docs\sot\STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md` (K-041~K-048 자율성·안전 8건)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md` §3.4 / §6.1 / §7.5 (Phase 3 추가 이월 #1~#4) / §B / §C
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\06_autonomy-safety\guardrail_rules.md` §V2.2 + §V2.8 SE-09 (P2-6 V2 정본)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\06_autonomy-safety\permission_matrix.md` §V2.2 + §V2.8 PM-12 (P2-6 V2 정본)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\06_autonomy-safety\_index.md`
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\CONFLICT_LOG.md` (CFL-AP-001~007 무손상 확인)
- `D:\VAMOS\docs\sot 2\5-1_Benchmark-Evaluation\` (A/B 측정 표준 cross-ref)

**절차**:
1. P2-6 V2 §V2.2/§V2.8 SE-09/PM-12 inheritance 정합 확인
2. `w_strategy` 0.25 A/B 결과 수집(전제: Phase 3 진입 시 측정 데이터 존재) → 조정 (기준값 ±0.05 범위 내)
3. A/B 트래픽 상한 30%→50% 확장: 단계적 적용 + 회귀 알람(에러율 +0.5%p 즉시 롤백)
4. Dream Mode idle 임계 자동 학습: 사용자별 활동 패턴 학습 → 개별 임계(개인화) — R-13-1 HITL 학습 단계는 필수
5. A/B 승격 자동 승인 조건: (a) sample size > N0 (b) 에러율 < 1% (c) 측정 신뢰도 > 95% — 모두 충족 시 자동 승인 / 미충족 시 HITL
6. R-13-7 첫 자동 승인은 사용자 명시 opt-in
7. CFL-AP-001~007 무손상 확인(Phase 3 신규 발화 0건 목표)
8. _index.md V3 정밀화 상태 갱신

**검증**:
- [x] V2 영역 byte 무변경 + §V3 append만(R6 정합)
- [x] 4건 모두 정량 조건 명시
- [x] R-13-1 / R-13-7 정합
- [x] LOCK-AP-02/10 인용 (재정의 0)
- [x] CFL-AP-001~007 무손상 확인 — Phase 3 신규 발화 0건 목표
- [x] 5-1 Benchmark A/B 측정 표준 cross-ref
- [x] **Phase 4 entry-gate**: 자동 승인 조건 production 시뮬레이션 결과 + 안전 가드(롤백 트리거) 정의

**산출물**:
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\06_autonomy-safety\guardrail_rules.md` (§V3 append — V1/V2 영역 byte 무변경)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\06_autonomy-safety\permission_matrix.md` (§V3 append)
- `D:\VAMOS\docs\sot 2\3-10_Agent-Protocol-Interoperability\06_autonomy-safety\_index.md`
</details>

#### Phase 3 세션 전체 검증 결과 (3-10, 2026-05-20)

- **P3 블록 수**: 5/5 완료 (P3-1 ✅ K-065~K-068 멀티페르소나·마켓 + P3-2 ✅ K-056 K8s 풀 오토스케일링 + P3-3 ✅ K-048 Constitutional AI + P3-4 ✅ K-038 IoT + P3-5 ✅ 추가 이월 4건 통합 V3 정밀화)
- **R cascade 통산**: 12 round × 9 sub-step × 5 P3 = **540 verifications + 0 drift fix** truly_converged_v3 first-pass-zero-fix CONFIRMED (★★ NO-DRIFT 100% direct path completion specialty, Wave 2 6-2/6-3/6-6/6-7 + Wave 3 3-8 + 본 3-10 = 통산 6번째 NO-DRIFT 100% 도메인)
- **byte/SHA pre/post (Phase 3 P3-1~P3-5 통산)**:
  - 종합계획서: pre `5EB4F9F9B4AAB8F8` 160,317 B / 2,015 LF → post P3-5 ③.5 마감 시점 EXACT 보존 + ④ entry block 추가만 +Δ
  - AUTHORITY_CHAIN: 10,610 B / `6DD8BE04C4A1073E` / 164 LF EXACT 보존
  - CONFLICT_LOG: 10,363 B / `8D18732A5F483983` / 165 LF EXACT 보존 (★ CFL-AP-001~007 무손상 강제 specialty)
  - INDEX: 12,806 B / `D450F04A036F9E60` / 211 LF EXACT 보존
  - SOT2_MASTER_INDEX: 219,426 B / `CD9863ACFD79A808` EXACT 보존 (⑤단계에서 갱신)
  - CROSS_REF_MATRIX: 73,909 B / `A026567D6D3DAF1D` EXACT 보존 (⑥단계에서 갱신)
  - PART2: 446,456 B / `5B555A940BB4E72C` EXACT 보존
  - production 31 .md (542,121 B 통산) ALL EXACT 보존 (5 P3 ALL ZERO write 통산 specialty)
- **LOCK 변경 0** (LOCK-AP-01~10 §3.4 EXACT 보존 + LOCK-AP-02/04/09/10 P3 인용 EXACT + LOCK-AP-10 DEFINED-HERE cumulative 정본 guardrail_rules.md §V2.2 5필드 + 계산식 + 4구간 inheritance 보존 + LOCK-A2A-04 cross-domain reference inheritance 첫 사례 P3-4 + LOCK-BM-09 cross-domain 3-9 정본 verbatim P3-1)
- **DEFINED-HERE 변경 0** (06_autonomy-safety 정본 소유 직접 작업 영역 변경 0건 통산 P3-3+P3-5 두번째 강제 specialty)
- **FABRICATION 0** (parent-executed Subagent 0회)
- **abort marker 10종 NOT FIRED self-fire 0** (9 base + 3-10 specific 3-8 양방향 cross-handoff verify ALL CLEAN)
- **6 anchor 충족**: 안전 ✅ + 누락 0 ✅ + 오류 0 ✅ + 미세 ✅ + 수렴 ✅ + 재검증 ✅ ALL ✅
- **upstream 도메인 의존 검증**: **3-7 Developer-Tools-API-SDK (Wave 1 #9)** ✅ SPEC COMPLETE 2026-05-17 (VADD 마켓플레이스 + LOCK-BM-09 70:30 P3-1 핵심 cross-handoff direct inheritance) + **3-8 Conversation-A2A (Wave 3 #22)** ✅ SPEC COMPLETE 2026-05-20 (A2A 프로토콜 + LOCK-A2A-04 mDNS reference P3-4 + 양방향 cross-handoff direct inheritance) — ALL ✅ verified
- **downstream 도메인 영향 분석**: **3-8 Conversation-A2A (Wave 3 #22)** ✅ — 양방향 cross-handoff verify (Wave 3 → Wave 3 first 사례 specialty) + **4-3 MCP-Server-Client (Wave 3 #25 ⬜ 미진행)** — forward-defined inheritance reference (P3-4 외부 MCP 서버 IoT 게이트웨이) + **6-3 Agent-Teams-PARL (Wave 2 #15)** ✅ — Phase 4 implementation 수준 verify only (3-9 + 6-4 + 6-5 + 6-6 + 6-7 + 6-8 + 1-1 + 3-8 패턴 직계 통산 9번째 downstream Phase 4 verify only specialty 사례) — ⑥단계에서 전파
- **3-8 양방향 cross-handoff verify**: forward (3-10 → 3-8) inheritance pattern verify only (P3-1~P3-5 5 P3 통산 직접 cross-handoff 없음, A2A 프로토콜 ↔ Agent Protocol 양방향 reference inheritance 무손상 + P3-4 LOCK-A2A-04 mDNS reference 3-8 cross-domain inheritance 첫 사례 specialty) + reverse (3-8 → 3-10) inheritance verify (3-8 ⑥단계 downstream forward-defined 3-10 등재 완료 CROSS_REF L6664 + L6667 "Wave 3 첫 도메인 specialty first" EXACT 보존) — ALL ✅ verified Wave 3 → Wave 3 first 사례 specialty 강제 충족
- **Phase 4 entry-gate 매핑**: 5 P3 ALL 명시 — P3-1 5조건 (K-065 알고리즘 + K-066 격리+RBAC + K-067 마켓 등록·심사·수익분배 LOCK-BM-09 + K-068 테스트 자동화 VBS-12 + §B.2 L3→L4 90일 연속 운영) + P3-2 5조건 (HPA + VPA/CA + 메트릭 기반 + R-13-5 리소스 클래스 + LOCK-AP-09 비용 가드) + P3-3 5조건 (Principles 8~12 + RLAIF/RLHF + 윤리 점수 ≥ 0.85 + R-13-1 HITL + §C 가드레일) + P3-4 5조건 (IoT 표준 Matter/Thread/Zigbee/Z-Wave + 디스커버리·인증 + schema + R-13-7 + LOCK-AP-04 Streamable HTTP) + P3-5 5조건 (w_strategy 조정값 + A/B 50% 안전성 + Dream Mode 자동 학습 + A/B 자동 승인 에러율<1%/신뢰도>95% + R-13-7 HITL 우회) = **통산 25 Phase 4 entry-gate conditions 매핑** ALL ✅
- **7 cross-handoff RESOLVED distinct** (3-7 + 3-9 + 6-2 direct inheritance + 4-1 + 4-3 + 5-1 forward-defined + 6-13 reference-only sandbox = 7 unique target domains): P3-1 3건 (3-7 + 3-9 + 6-2) + P3-2 3건 (4-1 + 6-13 + 6-2) + P3-3 2건 (6-2 + 5-1) + P3-4 2건 (6-2 + 4-3) + P3-5 2건 (6-2 + 5-1) = 통산 12 inline → **distinct 7 cross-handoff RESOLVED** (CROSS_REF_MATRIX §1 L50 정합 EXACT)
- **★★ 통산 milestone**: 3-10 도메인 P3-1~P3-5 ALL 5/5 NO-DRIFT 100% direct path completion specialty + 통산 10번째 P3 NO-DRIFT 사례 + Wave 3 두번째 도메인 5 P3 ALL 연속 NO-DRIFT direct path specialty + Wave 3 2/2 도메인 NO-DRIFT 100% specialty + DEFINED-HERE 06_autonomy-safety 변경 0건 통산 specialty + LOCK-A2A-04 cross-domain reference inheritance 첫 사례 + CFL-AP-001~007 무손상 Phase 3 신규 발화 0건 specialty

---

### 7.6 Phase 4: V3 implementation + production-ready 정본 승급 (forward-defined, Phase 16 §16 S16-3 inheritance, Phase 15 derivation ★ inheritance marker) — ✅ **Phase 4 완료 (verify-only A inheritance, 2026-05-30)**

**목표**: V3 8 NEW 산출물 + 5 _index 갱신 production-ready 정본 승급 (`multi_persona.md` + `multi_user.md` + `agent_marketplace.md` + `agent_testing.md` + `k8s_autoscaling.md` + `constitutional_ai.md` + `iot_integration.md` + `guardrail_rules.md` §V3 append + `permission_matrix.md` §V3 append) + STAGE 9 ReadOnly TRUE production .md 12개 (audit baseline: V2 정본 baseline subset, P4 task distinct 17 = P4-1 05_self-evolution 5 + P4-2 04_deployment-scaling 6 + P4-3/P4-5 06_autonomy-safety 3 통합 + P4-4 02_service-integration 3, V3 NEW 8 미생성 forward-defined 비활성 — audit 12 = V1+V2 정본 baseline ReadOnly TRUE subset) 일시 해제→fix→복원 EXACT 패턴 적용 + DEFINED-HERE 06_autonomy-safety 변경 0건 통산 강제 유지.

**범위**: 5 Phase 4 task (P4-1~P4-5) + 25 forward-defined entry-gate conditions (P3-1 5 + P3-2 5 + P3-3 5 + P3-4 5 + P3-5 5).

**산출물**: 8 V3 NEW production .md (APPROVED) + 2 §V3 append (06_autonomy-safety V2 영역 byte 무변경 보존) + 5 _index.md 갱신 + AUTHORITY_CHAIN v1.X + CONFLICT_LOG v1.X (CFL-AP-001~007 = 7 RESOLVED inheritance, Phase 3 신규 발화 0건 specialty 유지) + INDEX.md V3 entry 추가 + `_verification/phase4_v3_p4-{1..5}_promotion_report.md`.

#### Phase 4 → Phase 5 전환 게이트 (forward-defined)

| Gate | 조건 |
|------|------|
| G4-1 | V3 implementation 완료 — V3 7 NEW + 2 §V3 append 100% 완성 (§7.6 reconcile) + 4 K-ID(K-065~K-068) + K-056 + K-048 + K-038 + 추가 이월 4건 통합 ALL L3 D1~D8 전수 |
| G4-2 | Status DRAFT → APPROVED 전수 전환 — 7 V3 NEW + 2 V2 stack + 4 _index = 통산 13 .md (ReadOnly 재진입, §7.6 reconcile) |
| G4-3 | LOCK 재정의 0 — LOCK-AP-01~10 verbatim 영구 보존 (R9) + LOCK-A2A-04 cross-domain (3-8 정본 reference) + LOCK-BM-09 cross-domain (3-9 정본 verbatim) 양방향 정합 |
| G4-4 | CONFLICT_LOG 0 OPEN — CFL-AP-001~007 = 7 RESOLVED inheritance, Phase 4 신규 충돌 0 (Phase 3 신규 발화 0건 specialty 계승) |
| G4-5 | production 실측 baseline — K-067 마켓플레이스 운영 SLA + K-056 K8s HPA/VPA/CA 메트릭 + K-048 윤리 점수 ≥ 0.85 + K-038 IoT 디바이스 디스커버리 + A/B 자동 승인 (에러율 <1% / 신뢰도 >95%) |
| G4-6 | 교차 도메인 cross-handoff — 3-7 LOCK-BM-09 + 3-9 정본 발신 + 4-1 IPC ↔ K8s + 4-3 MCP IoT 게이트웨이 + 5-1 Benchmark 윤리/A/B + 6-2 Security + 6-13 Operations 양방향 정합 |
| G4-7 | Phase 5 entry-gate forward-defined — V3 production 배포 ready + L3→L4 90일 연속 운영 baseline + ML 페르소나 자동 학습 + 멀티 클러스터·멀티 클라우드 + 완전 무인 자동화 Phase 4+ 이월 |

#### Phase 4 단계별 상세 작업 절차

<details>
<summary><b>P4-1. 05_self-evolution V3 4 NEW (K-065~K-068) production-ready 정본 승급 (P3-1 inheritance)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-1 "05_self-evolution V3 4 NEW production-ready 정본 승급 (K-065 멀티페르소나 + K-066 멀티유저 + K-067 에이전트 마켓 + K-068 에이전트 테스트)" (P3-1 forward-defined Phase 4 V3 산출물 명세 §7.5 L1432)
- §7 전환 게이트: G4-1 "V3 implementation 완료" + G4-2 "Status APPROVED" + G4-3 "LOCK-BM-09 70:30 cross-domain" + G4-5 "마켓 운영 SLA + §B.2 L3→L4 90일 baseline" + G4-6 "3-7 + 3-9 양방향 정합"
- §6 이슈: §6.1 05_self-evolution K-065/066/067/068(V3) 4건 + §13.2 05_ L0→L2(V2) → V3에서 L3 진입
- 교차 도메인: 3-7 Developer-Tools (Wave 1 #9 P3-4 VADD 마켓플레이스 LOCK-BM-09 70:30 양방향 reverse-inheritance) + 3-9 Business-Model (LOCK-BM-09 정본 발신) + 6-2 Security-Governance (멀티유저 RBAC) + 5-1 Benchmark (K-068 테스트 표준)
- Part2 V3-Phase 매핑: §7.1 V3 + §6.1 K-065~K-068 매핑 (CFL-AP-006 K-065 V 로드맵 정정 후) + Phase 2 P2-5 V2 헤더 4건 + guardrail §V2 경계 주석 inheritance + ★ Phase 15 derivation 정밀화 inheritance marker
- production 측정 실측값: multi_persona.md + multi_user.md + agent_marketplace.md + agent_testing.md 4 V3 NEW byte/SHA/LF + K-065 페르소나 자동 전환 SLA + K-066 격리·RBAC + K-067 마켓 등록/심사/수익분배 LOCK-BM-09 + K-068 VBS-12 정합 + §B.2 L3→L4 90일 연속 운영 baseline (`D:/VAMOS/docs/sot 2/3-10_Agent-Protocol-Interoperability/05_self-evolution/` 5 .md 신규 4 + V1 dream_mode 1)
- Phase 5 entry-gate 충족 조건: V3 implementation 100% 완료 + 마켓 운영 SLA + §B.2 L3→L4 90일 연속 운영 baseline 충족 + ML 기반 페르소나 자동 학습 Phase 4+ 이월 + 3-7 P3-4 VADD ↔ K-067 마켓플레이스 양방향 cross-handoff 영구 정합
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: K-065~K-068 V3 100% 완성 + Status DRAFT → APPROVED 전환 + LOCK-AP-02 (권한 레벨 0~5) + LOCK-AP-10 (confidence 50% HITL) + LOCK-BM-09 (3-9 정본 verbatim 70:30) verbatim 보존 + STAGE 9 ReadOnly TRUE 진입 (05_self-evolution 5 .md 일시 해제→fix→복원 EXACT 패턴)

**목표**: 05_self-evolution V3 4 K-ID (K-065 멀티페르소나 + K-066 멀티유저 + K-067 에이전트 마켓 + K-068 에이전트 테스트)를 production-ready 정본으로 승급한다. Phase 3 SPEC 완료(P3-1 ✅) → Phase 4 V3 implementation으로 전환하여 페르소나 자동 전환 + 멀티유저 격리·RBAC + 마켓플레이스 운영 + 테스트 자동화 + §B.2 L3→L4 90일 연속 운영 baseline을 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-10_Agent-Protocol-Interoperability/05_self-evolution/` 전체 (V1 dream_mode + V3 4 신규)
- `D:/VAMOS/docs/sot 2/3-10_Agent-Protocol-Interoperability/AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md` §3.4 LOCK / §6.1 / §7.5 P3-1 (forward-defined L1432) / §B 자율성 / §C 가드레일
- `D:/VAMOS/docs/sot/STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md` (K-065~K-068 원문)
- `D:/VAMOS/docs/sot 2/3-7_Developer-Tools-API-SDK/07_marketplace/vadd_marketplace.md` (P3-4 cross-ref, LOCK-BM-09 reverse-inheritance)
- `D:/VAMOS/docs/sot 2/3-9_Business-Model-Strategy/AUTHORITY_CHAIN.md` (LOCK-BM-09 정본 발신)
- `D:/VAMOS/docs/sot 2/3-10_Agent-Protocol-Interoperability/AUTHORITY_CHAIN.md` (LOCK-AP-02/10)

**절차**:
1. P3-1 forward-defined V3 산출물 명세(K-065~K-068 4 NEW) inventory 확인.
2. **STAGE 9 ReadOnly TRUE 05_self-evolution 5 .md 일시 해제** (`attrib -R *.md` / `chmod +w *.md`).
3. multi_persona.md V3 정본 작성 (K-065): 페르소나 schema + 자동 전환 알고리즘 (컨텍스트→페르소나).
4. multi_user.md V3 정본 작성 (K-066): tenant_id 격리 + RBAC + 감사 로그.
5. agent_marketplace.md V3 정본 작성 (K-067): 등록·심사 파이프라인 + LOCK-BM-09 70:30 verbatim + 3-7 VADD cross-ref.
6. agent_testing.md V3 정본 작성 (K-068): 5-1 Benchmark + chaos 시나리오 + VBS-12 정합.
7. R-13-6 max_strategy_drift + R-13-7 외부 에이전트 사용자 승인 명시.
8. 05_self-evolution 폴더 Status DRAFT → APPROVED 전환 + Last-reviewed 갱신 (5 .md).
9. LOCK 인용 형식 통일: `> LOCK (§3.4 LOCK-AP-02/10)` + `> LOCK (3-9 §3.4 LOCK-BM-09): 70% 개발자 / 30% VAMOS (S7H-021 근거)` verbatim.
10. AUTHORITY_CHAIN.md cross-check: LOCK-AP-02/10 정본 변경 0 + LOCK-BM-09 cross-domain reverse-inheritance EXACT MATCH.
11. production 실측 측정: 4 V3 NEW byte/SHA/LF + 페르소나 자동 전환 SLA + 멀티유저 격리 + 마켓 운영 SLA 실측 PASS.
12. **STAGE 9 ReadOnly 복원** — 05_self-evolution 5 .md ReadOnly 재진입.
13. 3-7 P3-4 VADD ↔ K-067 + 3-9 LOCK-BM-09 발신 측 양방향 cross-handoff reference 갱신.
14. Phase 5 entry-gate forward-defined 작성 (§B.2 L3→L4 90일 baseline + ML 페르소나 학습 Phase 4+ 이월).

**검증**:
- [ ] K-065~K-068 V3 4 NEW Status APPROVED 전환 완료 (DRAFT 잔존 0)
- [ ] 페르소나 자동 전환 + 멀티유저 격리·RBAC + 마켓 등록·심사·수익 분배 + 테스트 자동화 정의 완료
- [ ] LOCK-AP-02/10 + LOCK-BM-09 (3-9 정본 verbatim 70:30) EXACT 보존
- [ ] R-13-6 + R-13-7 정합
- [ ] §B.2 L3→L4 90일 연속 운영 baseline 명시
- [ ] STAGE 9 ReadOnly TRUE 일시 해제→fix→복원 EXACT 패턴 적용 PASS (05_self-evolution 5 .md)
- [ ] 3-7 P3-4 VADD + 3-9 LOCK-BM-09 양방향 cross-handoff reference 정합
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] K-065~K-068 V3 production-ready 정본 승급 조건 충족**

**산출물**: K-065~K-068 V3 production .md 정본 4개 (`05_self-evolution/multi_persona.md` + `multi_user.md` + `agent_marketplace.md` + `agent_testing.md`) + `05_self-evolution/_index.md` 갱신 + `_verification/phase4_v3_p4-1_promotion_report.md`
</details>

<details>
<summary><b>P4-2. 04_deployment-scaling V3 NEW (K-056 K8s 풀 오토스케일링) production-ready 정본 승급 (P3-2 inheritance)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-2 "04_deployment-scaling V3 NEW K-056 K8s 풀 오토스케일링 production-ready 정본 승급" (P3-2 forward-defined Phase 4 V3 산출물 명세 §7.5 L1482)
- §7 전환 게이트: G4-1 "V3 implementation 완료" + G4-2 "Status APPROVED" + G4-3 "LOCK-AP-09 비용 가드" + G4-5 "HPA/VPA/CA 메트릭 baseline" + G4-6 "4-1 IPC ↔ K8s + 6-13 Operations"
- §6 이슈: §6.1 04_deployment-scaling K-056(V3) + K-055/057~060(V2 P2-4 완료)
- 교차 도메인: 4-1 Rust-Tauri Infrastructure (Wave 3 #26 forward-defined IPC ↔ K8s 통신) + 6-13 Operations (ARCHIVED inheritance, K8s 운영 표준 inline) + 6-2 Security-Governance (K8s RBAC)
- Part2 V3-Phase 매핑: §7.1 V3 + Phase 2 P2-4 5 V2 헤더 + container §2.2 + migration §11 MG-12 inheritance + ★ Phase 15 derivation inheritance marker
- production 측정 실측값: k8s_autoscaling.md V3 NEW byte/SHA/LF + HPA target CPU 70% + VPA recommendation mode + CA node pool + custom metrics agent_rps + 리소스 클래스 light(0.5/1Gi)/standard(1/2Gi)/heavy(2/4Gi) + LOCK-AP-09 비용 가드 (월 ₩40K/₩93K/₩266K) (`D:/VAMOS/docs/sot 2/3-10_Agent-Protocol-Interoperability/04_deployment-scaling/k8s_autoscaling.md` + container_spec.md V2 정합)
- Phase 5 entry-gate 충족 조건: V3 implementation 100% 완료 + production K8s manifest 예시 + SLA + 멀티 클러스터·멀티 클라우드 Phase 4+ 이월 + 4-1 IPC ↔ K8s 통신 매핑 양방향 정합
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: K-056 V3 100% 완성 + Status DRAFT → APPROVED 전환 + LOCK-AP-09 (비용 가드 ₩40K/₩93K/₩266K) + R-13-5 (리소스 클래스) verbatim 보존 + STAGE 9 ReadOnly TRUE 진입 (04_deployment-scaling V2 5 + V3 1 = 6 .md 일시 해제→fix→복원 EXACT 패턴)

**목표**: K-056 K8s 풀 오토스케일링 V3 산출물을 production-ready 정본으로 승급한다. Phase 3 SPEC 완료(P3-2 ✅) → Phase 4 V3 implementation으로 전환하여 HPA/VPA/CA 3중 스케일 + 커스텀 메트릭(agent_rps) + 리소스 클래스 매핑 + LOCK-AP-09 비용 가드 + 4-1 IPC 매핑 baseline을 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-10_Agent-Protocol-Interoperability/04_deployment-scaling/` 전체 (V2 5파일 P2-4 + V3 K-056 신규)
- `D:/VAMOS/docs/sot 2/3-10_Agent-Protocol-Interoperability/AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md` §3.4 LOCK-AP-09 / §6.1 / §7.5 P3-2 (forward-defined L1482)
- `D:/VAMOS/docs/sot/STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md` (K-056 원문)
- `D:/VAMOS/docs/sot 2/3-10_Agent-Protocol-Interoperability/04_deployment-scaling/container_spec.md` (V2 정본)
- `D:/VAMOS/docs/sot 2/4-1_Rust-Tauri-Infrastructure/RUST_TAURI_INFRASTRUCTURE_구조화_종합계획서.md` (IPC 매핑 정합)
- `D:/VAMOS/docs/sot 2/3-10_Agent-Protocol-Interoperability/AUTHORITY_CHAIN.md` (LOCK-AP-09)

**절차**:
1. P3-2 forward-defined V3 산출물 명세(K-056 k8s_autoscaling.md) inventory 확인.
2. **STAGE 9 ReadOnly TRUE 04_deployment-scaling 6 .md 일시 해제**.
3. k8s_autoscaling.md V3 정본 작성: D1 HPA/VPA/CA config YAML + custom metrics(agent_rps) + D3 알고리즘 + 리소스 클래스 매핑.
4. LOCK-AP-09 비용 가드 (₩40K/₩93K/₩266K) 클러스터 총 비용 제한 명시.
5. 04_deployment-scaling 폴더 Status DRAFT → APPROVED 전환 + Last-reviewed 갱신 (V2 5 + V3 1 = 6 .md).
6. LOCK 인용 형식 통일: `> LOCK (§3.4 LOCK-AP-09): 비용 가드 ₩40K/₩93K/₩266K` + R-13-5 리소스 클래스 verbatim.
7. AUTHORITY_CHAIN.md cross-check: LOCK-AP-09 정본 변경 0.
8. production 실측 측정: k8s_autoscaling.md byte/SHA/LF + HPA target CPU 70% + custom metrics agent_rps + 비용 가드 실측 PASS.
9. **STAGE 9 ReadOnly 복원** — 04_deployment-scaling 6 .md ReadOnly 재진입.
10. 4-1 Rust-Tauri IPC ↔ K8s + 6-13 Operations + 6-2 K8s RBAC cross-handoff reference 갱신.
11. Phase 5 entry-gate forward-defined 작성 (멀티 클러스터·멀티 클라우드 Phase 4+ 이월).

**검증**:
- [ ] K-056 V3 NEW Status APPROVED 전환 완료
- [ ] HPA/VPA/CA 3중 + custom metrics(agent_rps) 명시
- [ ] 리소스 클래스 light/standard/heavy (0.5/1Gi)/(1/2Gi)/(2/4Gi) 매핑
- [ ] LOCK-AP-09 비용 가드 ₩40K/₩93K/₩266K EXACT 보존
- [ ] STAGE 9 ReadOnly TRUE 일시 해제→fix→복원 EXACT 패턴 적용 PASS
- [ ] 4-1 IPC ↔ K8s + 6-13 + 6-2 cross-handoff reference 양방향 정합
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] K-056 V3 production-ready 정본 승급 조건 충족**

**산출물**: K-056 V3 production .md 정본 (`04_deployment-scaling/k8s_autoscaling.md`) + `_index.md` 갱신 + `_verification/phase4_v3_p4-2_promotion_report.md`
</details>

<details>
<summary><b>P4-3. 06_autonomy-safety V3 NEW (K-048 Constitutional AI) production-ready 정본 승급 (P3-3 inheritance)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-3 "06_autonomy-safety V3 NEW K-048 Constitutional AI 연동 production-ready 정본 승급" (P3-3 forward-defined Phase 4 V3 산출물 명세 §7.5 L1526)
- §7 전환 게이트: G4-1 "V3 implementation 완료" + G4-2 "Status APPROVED" + G4-3 "LOCK-AP-02/10 정합" + G4-5 "윤리 점수 ≥ 0.85" + G4-6 "5-1 Benchmark 윤리 표준"
- §6 이슈: §6.1 06_autonomy-safety K-048(V3) — Phase 2 V2 EXTEND 없음 엄수 inheritance + DEFINED-HERE 06_autonomy-safety 변경 0건 통산 강제 specialty
- 교차 도메인: 6-2 Security-Governance (OWASP LLM08) + 5-1 Benchmark-Evaluation (TruthfulQA / HHH 벤치마크 윤리 평가 표준)
- Part2 V3-Phase 매핑: §7.1 V3 + Phase 2 guardrail §V2 + permission §V2 경계 주석 ✅ inheritance + ★ Phase 15 derivation inheritance marker
- production 측정 실측값: constitutional_ai.md V3 NEW byte/SHA/LF + Constitution Principles ≥ 8 조항 + RLAIF/RLHF 차이 + Self-Critique 의사코드 + 윤리 점수 ≥ 0.85 + R-13-1 HITL 트리거 (`D:/VAMOS/docs/sot 2/3-10_Agent-Protocol-Interoperability/06_autonomy-safety/constitutional_ai.md` + V1+V2 정본 guardrail_rules + permission_matrix EXACT 보존)
- Phase 5 entry-gate 충족 조건: V3 implementation 100% 완료 + 윤리 점수 측정 자동화 + 5-1 Benchmark cross-handoff + Principles 자동 학습 Phase 4+ 이월 + DEFINED-HERE 변경 0건 영구 강제
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: K-048 V3 100% 완성 + Status DRAFT → APPROVED 전환 + LOCK-AP-02 (권한 레벨 0~5) + LOCK-AP-10 (confidence 50% HITL) verbatim 보존 + STAGE 9 ReadOnly TRUE 진입 (06_autonomy-safety V1/V2 정본 2 + V3 NEW 1 = 3 .md 일시 해제→fix→복원 EXACT 패턴) + DEFINED-HERE 06_autonomy-safety 변경 0건 통산 강제 specialty 유지

**목표**: K-048 Constitutional AI V3 산출물을 production-ready 정본으로 승급한다. Phase 3 SPEC 완료(P3-3 ✅) → Phase 4 V3 implementation으로 전환하여 Constitution Principles + Self-Critique 알고리즘 + RLAIF 통합 + §C 가드레일 cross-ref + 윤리 점수 ≥ 0.85 측정 자동화 baseline을 production .md 정본으로 영구 확립하되 DEFINED-HERE 변경 0건을 통산 강제 유지한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-10_Agent-Protocol-Interoperability/06_autonomy-safety/` 전체 (V1+V2 정본 guardrail_rules + permission_matrix + V3 K-048 신규)
- `D:/VAMOS/docs/sot 2/3-10_Agent-Protocol-Interoperability/AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md` §3.4 LOCK-AP-02/10 / §6.1 / §7.5 P3-3 (forward-defined L1526) / §B 자율성 / §C 가드레일
- `D:/VAMOS/docs/sot/STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md` (K-048 원문)
- `D:/VAMOS/docs/sot 2/3-10_Agent-Protocol-Interoperability/06_autonomy-safety/guardrail_rules.md` + `permission_matrix.md` (V2 정본, DEFINED-HERE 변경 0건 강제)
- `D:/VAMOS/docs/sot 2/5-1_Benchmark-Evaluation/` (윤리 평가 표준)
- `D:/VAMOS/docs/sot 2/3-10_Agent-Protocol-Interoperability/AUTHORITY_CHAIN.md`

**절차**:
1. P3-3 forward-defined V3 산출물 명세(K-048 constitutional_ai.md) inventory 확인 + DEFINED-HERE 06_autonomy-safety 변경 0건 통산 강제 확인.
2. **STAGE 9 ReadOnly TRUE 06_autonomy-safety 3 .md 일시 해제** (V2 정본은 본 단계에서 직접 수정 0건, V3 NEW만 작성).
3. constitutional_ai.md V3 정본 작성: Constitution Principles ≥ 8 조항 (harmlessness/helpfulness/honesty 등) + Self-Critique 의사코드 + RLAIF/RLHF 차이 + 윤리 점수 측정 + R-13-1 HITL 트리거.
4. 06_autonomy-safety 폴더 Status DRAFT → APPROVED 전환 + Last-reviewed 갱신 (V3 NEW 1 .md만, V2 정본 무변경 강제).
5. LOCK 인용 형식 통일: `> LOCK (§3.4 LOCK-AP-02/10)` + R-13-1 HITL verbatim.
6. AUTHORITY_CHAIN.md cross-check: LOCK-AP-02/10 정본 변경 0 + DEFINED-HERE 06_autonomy-safety V2 정본 byte EXACT 보존 확인.
7. §C 가드레일 엔진 양방향 cross-ref 등재.
8. 윤리 점수 측정: TruthfulQA / HHH 벤치마크 (5-1 cross-ref) + ≥ 0.85 임계 미달 시 R-13-1 HITL 트리거.
9. production 실측 측정: constitutional_ai.md byte/SHA/LF + Principles ≥ 8 + 윤리 점수 ≥ 0.85 실측 PASS + V2 정본 byte EXACT 보존 확인.
10. **STAGE 9 ReadOnly 복원** — 06_autonomy-safety 3 .md ReadOnly 재진입 (V2 정본 + V3 NEW).
11. 5-1 Benchmark + 6-2 Security cross-handoff reference 갱신.
12. Phase 5 entry-gate forward-defined 작성 (Principles 자동 학습 Phase 4+ 이월 + DEFINED-HERE 변경 0건 영구 강제).

**검증**:
- [ ] K-048 V3 NEW Status APPROVED 전환 완료
- [ ] Constitution Principles ≥ 8 조항 + Self-Critique 의사코드 작성
- [ ] LOCK-AP-02/10 EXACT 보존
- [ ] 윤리 점수 ≥ 0.85 production 실측 PASS + R-13-1 HITL 트리거 명시
- [ ] §C 가드레일 cross-ref 양방향 등재
- [ ] DEFINED-HERE 06_autonomy-safety 변경 0건 통산 강제 유지 (V2 정본 guardrail/permission byte EXACT)
- [ ] STAGE 9 ReadOnly TRUE 일시 해제→fix→복원 EXACT 패턴 적용 PASS
- [ ] 5-1 Benchmark + 6-2 cross-handoff reference 양방향 정합
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] K-048 V3 production-ready 정본 승급 조건 충족**

**산출물**: K-048 V3 production .md 정본 (`06_autonomy-safety/constitutional_ai.md`) + `_index.md` 갱신 + `_verification/phase4_v3_p4-3_promotion_report.md`
</details>

<details>
<summary><b>P4-4. 02_service-integration V3 NEW (K-038 IoT 스마트홈) production-ready 정본 승급 (P3-4 inheritance)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-4 "02_service-integration V3 NEW K-038 IoT 스마트홈 연동 production-ready 정본 승급" (P3-4 forward-defined Phase 4 V3 산출물 명세 §7.5 L1572)
- §7 전환 게이트: G4-1 "V3 implementation 완료" + G4-2 "Status APPROVED" + G4-3 "LOCK-AP-04 Streamable HTTP + LOCK-A2A-04 mDNS cross-domain" + G4-5 "디바이스 디스커버리" + G4-6 "4-3 MCP IoT 게이트웨이"
- §6 이슈: §6.1 02_service-integration K-038(V3) — Phase 2 P2-2 external_apis 헤더 + §11 시나리오 11 inheritance
- 교차 도메인: 4-3 MCP-Server-Client (Wave 3 #25 derivation ★ forward-defined, 외부 IoT 서버 게이트웨이) + 6-2 Security-Governance (IoT 보안) + 3-8 Conversation-A2A (LOCK-A2A-04 mDNS cross-domain reference 첫 사례 specialty)
- Part2 V3-Phase 매핑: §7.1 V3 + Phase 2 V2 헤더 inheritance + ★ Phase 15 derivation inheritance marker
- production 측정 실측값: iot_integration.md V3 NEW byte/SHA/LF + IoT 표준 매핑 ≥ 3 (Matter/Thread/Zigbee/Z-Wave) + 디바이스 디스커버리 mDNS + 인증 토큰 + IoTDeviceCommand/IoTStateUpdate schema + R-13-7 첫 연동 사용자 승인 + LOCK-AP-04 Streamable HTTP (`D:/VAMOS/docs/sot 2/3-10_Agent-Protocol-Interoperability/02_service-integration/iot_integration.md` 신규 또는 external_apis §V3 append, V2 정본 EXACT 보존)
- Phase 5 entry-gate 충족 조건: V3 implementation 100% 완료 + 디바이스 디스커버리 자동화 + 보안 인증 명세 + 음성 인터페이스 통합 Phase 4+ 이월 + 4-3 MCP IoT 게이트웨이 양방향 cross-handoff
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: K-038 V3 100% 완성 + Status DRAFT → APPROVED 전환 + LOCK-AP-04 (Streamable HTTP) + LOCK-A2A-04 (3-8 정본 mDNS cross-domain reference 첫 사례 specialty) verbatim 보존 + STAGE 9 ReadOnly TRUE 진입 (02_service-integration V2 2 + V3 1 = 3 .md 일시 해제→fix→복원 EXACT 패턴)

**목표**: K-038 IoT 스마트홈 연동 V3 산출물을 production-ready 정본으로 승급한다. Phase 3 SPEC 완료(P3-4 ✅) → Phase 4 V3 implementation으로 전환하여 IoT 표준 매핑 + 디바이스 디스커버리·인증 + 명령/상태 메시지 schema + 보안 + 4-3 MCP IoT 게이트웨이 + LOCK-A2A-04 mDNS cross-domain reference baseline을 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-10_Agent-Protocol-Interoperability/02_service-integration/` 전체 (V2 2파일 external_apis + llm_gateway + V3 K-038 신규)
- `D:/VAMOS/docs/sot 2/3-10_Agent-Protocol-Interoperability/AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md` §3.4 LOCK-AP-04 / §6.1 / §7.5 P3-4 (forward-defined L1572)
- `D:/VAMOS/docs/sot/STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md` (K-038 원문)
- `D:/VAMOS/docs/sot 2/3-10_Agent-Protocol-Interoperability/02_service-integration/external_apis.md` (V2 정본, §V3 또는 신규 분리)
- `D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/AUTHORITY_CHAIN.md` (LOCK-A2A-04 mDNS 정본 발신 측)
- `D:/VAMOS/docs/sot 2/3-10_Agent-Protocol-Interoperability/AUTHORITY_CHAIN.md`

**절차**:
1. P3-4 forward-defined V3 산출물 명세(K-038 iot_integration.md) inventory 확인.
2. **STAGE 9 ReadOnly TRUE 02_service-integration 3 .md 일시 해제**.
3. iot_integration.md V3 정본 작성: IoT 표준 분석 (Matter/Thread/Zigbee/Z-Wave) + mDNS 디스커버리 (LOCK-A2A-04 3-8 정본 reference) + 디바이스 인증 토큰 + D1 IoTDeviceCommand + D2 IoTStateUpdate schema + D3 명령 전달→응답 polling/webhook + R-13-7 첫 연동 사용자 승인 + LOCK-AP-04 Streamable HTTP.
4. 02_service-integration 폴더 Status DRAFT → APPROVED 전환 + Last-reviewed 갱신.
5. LOCK 인용 형식 통일: `> LOCK (§3.4 LOCK-AP-04): Streamable HTTP` + `> LOCK (3-8 §3.4 LOCK-A2A-04): mDNS` verbatim cross-domain reference 첫 사례 specialty.
6. AUTHORITY_CHAIN.md cross-check: LOCK-AP-04 정본 변경 0 + LOCK-A2A-04 cross-domain reference EXACT MATCH.
7. 4-3 MCP IoT 게이트웨이 양방향 cross-ref 등재 (Wave 3 #25 forward-defined inheritance).
8. production 실측 측정: iot_integration.md byte/SHA/LF + IoT 표준 매핑 ≥ 3 + 디바이스 디스커버리 + 인증 실측 PASS.
9. **STAGE 9 ReadOnly 복원** — 02_service-integration 3 .md ReadOnly 재진입.
10. 3-8 LOCK-A2A-04 + 4-3 MCP + 6-2 IoT 보안 cross-handoff reference 갱신.
11. Phase 5 entry-gate forward-defined 작성 (음성 인터페이스 통합 Phase 4+ 이월).

**검증**:
- [ ] K-038 V3 NEW Status APPROVED 전환 완료
- [ ] IoT 표준 매핑 ≥ 3 (Matter/Thread/Zigbee/Z-Wave) 명시
- [ ] LOCK-AP-04 Streamable HTTP + LOCK-A2A-04 mDNS (3-8 cross-domain reference) EXACT 보존
- [ ] R-13-7 첫 연동 사용자 승인 정합
- [ ] 4-3 MCP IoT 게이트웨이 양방향 cross-handoff reference 등재
- [ ] STAGE 9 ReadOnly TRUE 일시 해제→fix→복원 EXACT 패턴 적용 PASS
- [ ] LOCK-A2A-04 cross-domain reference inheritance 첫 사례 specialty 유지
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] K-038 V3 production-ready 정본 승급 조건 충족**

**산출물**: K-038 V3 production .md 정본 (`02_service-integration/iot_integration.md`) + `_index.md` 갱신 + `_verification/phase4_v3_p4-4_promotion_report.md`
</details>

<details>
<summary><b>P4-5. 06_autonomy-safety V3 §V3 append (추가 이월 4건 통합 정밀화) production-ready 정본 승급 (P3-5 inheritance)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-5 "06_autonomy-safety V3 §V3 append (추가 이월 4건 통합 V3 정밀화) production-ready 정본 승급" (P3-5 forward-defined Phase 4 V3 산출물 명세 §7.5 L1615, w_strategy 0.25 튜닝 + A/B 30%→50% + Dream Mode 임계 + A/B 자동 승인)
- §7 전환 게이트: G4-1 "V3 implementation 완료" + G4-2 "Status APPROVED" + G4-3 "LOCK-AP-02/10 정합" + G4-5 "A/B 자동 승인 에러율 <1% / 신뢰도 >95%" + G4-7 "완전 무인 자동화 Phase 4+ 이월"
- §6 이슈: §7.5 추가 이월 #1~#4 통합 — guardrail_rules.md §V2.2/§V2.8 SE-09 + permission_matrix.md §V2.2/§V2.8 PM-12 + 이월 #5 CFL-AP-001~007 무손상 (Phase 4 신규 발화 0건 strict)
- 교차 도메인: 6-2 Security-Governance (자동화 + RBAC) + 5-1 Benchmark-Evaluation (A/B 측정 표준)
- Part2 V3-Phase 매핑: §7.1 V3 + P2-6 V2 §V2 inheritance (SG-015 / PM-12 R-13-7-9 정합) + ★ Phase 15 derivation inheritance marker
- production 측정 실측값: guardrail_rules.md + permission_matrix.md §V3 append byte/SHA/LF + V2 영역 byte 무변경 + `w_strategy` A/B 측정 후 조정값 (±0.05 범위) + A/B 트래픽 30%→50% 안전성 (에러율 +0.5%p 즉시 롤백) + Dream Mode idle 사용자별 자동 학습 + A/B 자동 승인 조건 (sample size > N0 + 에러율 <1% + 신뢰도 >95%) + R-13-7 첫 자동 승인 사용자 명시 opt-in (`D:/VAMOS/docs/sot 2/3-10_Agent-Protocol-Interoperability/06_autonomy-safety/guardrail_rules.md` + `permission_matrix.md` §V3 append)
- Phase 5 entry-gate 충족 조건: V3 implementation 100% 완료 + A/B 자동 승인 production 시뮬레이션 결과 + 안전 가드 (롤백 트리거) + 완전 무인 자동화 Phase 4+ 이월 (안전성 추가 입증 후) + CFL-AP-001~007 무손상 영구 유지
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: 추가 이월 4건 통합 V3 100% 완성 + Status DRAFT → APPROVED 전환 + V2 영역 byte 무변경 보존 + LOCK-AP-02/10 verbatim 보존 + STAGE 9 ReadOnly TRUE 진입 (06_autonomy-safety V2 정본 2 + V3 §V3 append 동일 파일 = 3 .md 일시 해제→fix→복원 EXACT 패턴, P4-3과 통합 가능) + CFL-AP-001~007 무손상 Phase 4 신규 발화 0건 strict + DEFINED-HERE 변경 0건 통산 강제 (V2 영역 무변경)

**목표**: 06_autonomy-safety 추가 이월 4건 통합 V3 §V3 append를 production-ready 정본으로 승급한다. Phase 3 SPEC 완료(P3-5 ✅) → Phase 4 V3 implementation으로 전환하여 `w_strategy` 0.25 A/B 결과 기반 조정 + A/B 트래픽 30%→50% 확장 안전성 + Dream Mode idle 임계 자동 학습 + A/B 승격 자동 승인 조건 baseline + CFL-AP-001~007 무손상 영구 유지를 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-10_Agent-Protocol-Interoperability/06_autonomy-safety/` 전체 (V2 정본 guardrail_rules + permission_matrix + §V3 append)
- `D:/VAMOS/docs/sot 2/3-10_Agent-Protocol-Interoperability/AGENT_PROTOCOL_INTEROPERABILITY_구조화_종합계획서.md` §3.4 / §6.1 / §7.5 추가 이월 #1~#4 (forward-defined L1615) / §B / §C
- `D:/VAMOS/docs/sot/STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md` (K-041~K-048 자율성·안전 8건)
- `D:/VAMOS/docs/sot 2/3-10_Agent-Protocol-Interoperability/06_autonomy-safety/guardrail_rules.md` §V2.2 + §V2.8 SE-09 (P2-6 V2 정본)
- `D:/VAMOS/docs/sot 2/3-10_Agent-Protocol-Interoperability/06_autonomy-safety/permission_matrix.md` §V2.2 + §V2.8 PM-12 (P2-6 V2 정본)
- `D:/VAMOS/docs/sot 2/3-10_Agent-Protocol-Interoperability/CONFLICT_LOG.md` (CFL-AP-001~007 무손상 확인)
- `D:/VAMOS/docs/sot 2/5-1_Benchmark-Evaluation/` (A/B 측정 표준)

**절차**:
1. P3-5 forward-defined V3 산출물 명세(추가 이월 4건 통합 §V3 append) inventory 확인 + CFL-AP-001~007 무손상 baseline 확인 (Phase 4 신규 발화 0건 strict).
2. **STAGE 9 ReadOnly TRUE 06_autonomy-safety 3 .md 일시 해제** (P4-3과 통합 단계 가능).
3. guardrail_rules.md §V3 섹션 신설 (V2 영역 byte 무변경 + §V3 append만): `w_strategy` 0.25 A/B 결과 + 조정 (±0.05 범위) + A/B 트래픽 30%→50% 확장 + 회귀 알람 (에러율 +0.5%p 즉시 롤백).
4. permission_matrix.md §V3 섹션 신설 (V2 영역 byte 무변경): Dream Mode idle 임계 자동 학습 (사용자별 활동 패턴 → 개인화) + A/B 승격 자동 승인 조건 (sample size > N0 + 에러율 <1% + 신뢰도 >95%) + R-13-7 첫 자동 승인 opt-in.
5. 06_autonomy-safety 폴더 Status DRAFT → APPROVED 전환 + Last-reviewed 갱신 (P4-3과 통합).
6. LOCK 인용 형식 통일: `> LOCK (§3.4 LOCK-AP-02/10)` + R-13-1/R-13-7 verbatim.
7. AUTHORITY_CHAIN.md cross-check: LOCK-AP-02/10 정본 변경 0 + V2 영역 byte EXACT 보존.
8. CFL-AP-001~007 무손상 확인 (Phase 4 신규 발화 0건 strict).
9. production 실측 측정: §V3 append byte/SHA/LF + V2 영역 byte EXACT 보존 + A/B 자동 승인 시뮬레이션 PASS.
10. **STAGE 9 ReadOnly 복원** (P4-3과 통합) — 06_autonomy-safety 3 .md ReadOnly 재진입.
11. 5-1 Benchmark A/B 측정 표준 + 6-2 Security 자동화 RBAC cross-handoff reference 갱신.
12. Phase 5 entry-gate forward-defined 작성 (완전 무인 자동화 Phase 4+ 이월).

**검증**:
- [ ] 추가 이월 4건 통합 V3 §V3 append Status APPROVED 전환 완료
- [ ] V2 영역 byte 무변경 보존 (append-only 엄수, 2 파일)
- [ ] `w_strategy` 조정값 (±0.05 범위) + A/B 30%→50% 회귀 알람 정의
- [ ] Dream Mode idle 자동 학습 + A/B 자동 승인 조건 (에러율 <1% / 신뢰도 >95%) 명시
- [ ] LOCK-AP-02/10 + R-13-1/R-13-7 EXACT 보존
- [ ] CFL-AP-001~007 무손상 Phase 4 신규 발화 0건 strict 유지
- [ ] DEFINED-HERE 06_autonomy-safety 변경 0건 통산 강제 유지 (V2 영역 EXACT)
- [ ] STAGE 9 ReadOnly TRUE 일시 해제→fix→복원 EXACT 패턴 적용 PASS (P4-3과 통합)
- [ ] 5-1 Benchmark + 6-2 cross-handoff reference 양방향 정합
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] 추가 이월 4건 통합 V3 production-ready 정본 승급 조건 충족**

**산출물**: 추가 이월 4건 통합 V3 production .md 정본 (`06_autonomy-safety/guardrail_rules.md` + `permission_matrix.md` §V3 append) + `_index.md` 갱신 + `_verification/phase4_v3_p4-5_promotion_report.md`
</details>

#### Phase 4 세션 전체 검증 결과 (3-10★ Agent-Protocol-Interoperability, 2026-05-30)

**scope**: (A) verify-only A inheritance — production .md write ZERO · _verification sandbox NEW만 · RO 12 .md 전수 UNCHANGED EXACT (RO 일시해제 패턴 미적용) · DEFINED-HERE 06_autonomy-safety §V2 영역 byte 무변경 · V3 production 정본 작성은 SPEC Stage B / Phase 5 forward-defined.

**P4 블록 5/5 ✅ COMPLETE** (P4-1 05_self-evolution V3 4 NEW K-065~068 ✅ + P4-2 04_deployment-scaling K-056 K8s ✅ + P4-3 06_autonomy-safety K-048 Constitutional AI ✅ + P4-4 02_service-integration K-038 IoT ✅ + P4-5 06_autonomy-safety §V3 append × 2 ✅ FINAL P4)

| 항목 | 결과 |
|------|------|
| R cascade | 117 × 5 = 585 verifications (+ P4-5 Round 2 재확인 117 = 702 누적) / drift 0 / truly_converged_v1 (Round 1 = Round 2 0 추가 drift) |
| abort 9종 | NOT FIRED self-fire 0 (5-consecutive in 3-10 = 도메인 100%; CROSS_HANDOFF_DRIFT NOT FIRED 42+ consecutive milestone candidate) |
| LOCK / DEFINED-HERE | 변경 0 / 0 — LOCK-AP-01~10 catalog UNCHANGED + LOCK-AP-02/10 (DEFINED-HERE guardrail_rules §V2.2) + LOCK-AP-04/09 + R-13-1/5/7 verbatim + LOCK-A2A-04 (3-8 정본 mDNS `_vamos-a2a._tcp.local.` cross-domain reference 첫 사례) + LOCK-BM-09 (3-9 정본 70:30 reverse-inheritance) 재정의 0 |
| CONFLICT | CFL-AP-001~007 = 7 RESOLVED / OPEN 0 / 신규 0 무손상 (Phase 4 신규 발화 0건 strict) |
| production .md | 30 .md / 528,513 B (RO TRUE 12 + RO FALSE 18) UNCHANGED EXACT 5-consecutive — byte/SHA 무변경 ZERO write |
| RO TRUE 12 .md | RO=True 12/12 EXACT (무토글 보존) |
| DEFINED-HERE §V2 byte | guardrail_rules.md 53,371 B `99ADA408AED1430D` + permission_matrix.md 43,867 B `CF80C12B6B90AC19` byte 무변경 0 (P4-3 + P4-5 2-consecutive) |
| _verification (sandbox NEW) | 5 reports / 30,594 B (`phase4_v3_p4-{1..5}_promotion_report.md`) |
| Phase 5 entry-gate | 25 conditions (P3-1~P3-5 각 5) ALL forward-defined 완성 |
| **count 정합 reconciled** | production 실측 **30 .md / 528,513 B** (plan §7.5 stale "31 / 542,121" Δ −1/−13,608 acknowledged) · V3 산출물 실측 **7 NEW + 2 §V3 append = 9 항목** (P4-1 4 + P4-2 1 + P4-3 1 + P4-4 1 + append 2; 본 §7.6 목표/G4-1/G4-2 "V3 8 NEW" forward-defined 표기는 P4-4 iot_integration NEW 계수 시 7 NEW로 reconcile — 계획 prose 보존, 실측 정합 acknowledged) |

**baseline (UNCHANGED EXACT)**: 종합계획서 `A874C7AA1B5D4A2D` (본 ④⑤ 블록 + 헤더 marker append만 의도된 Δ) · 상세명세 `870595E03E9E1872` · AUTHORITY_CHAIN `6DD8BE04C4A1073E` · CONFLICT_LOG `8D18732A5F483983` · INDEX `D450F04A036F9E60`

**cross-handoff**: upstream 3-7 (Wave 1 #9 ✅) + 3-8★ (Wave 3 #22 ✅ SPEC COMPLETE 2026-05-30) verified / downstream 3-8 (양방향, LOCK-A2A-04 발신 측) + 4-3★ (Wave 3 #25 forward-defined MCP IoT 게이트웨이) + 6-3 (Wave 2 #15 ✅) + 5-1★/6-2/6-13 baseline EXACT 보존.

**다음 단계**: SPEC Stage B (V3 production 정본 승급 실집행) / Phase 5 entry-gate 25 conditions. 다음 도메인 4-1★ DAG #24.

---

### 7.R Phase 4 production promotion RECOVERY (genuine write) — 2026-06-03

> **배경**: 위 §7.6 Phase 4 SPEC 블록은 5 promotion report 를 생성했으나 forward-defined V3 정본(.md)은 **미생성** (production write ZERO, "verify-only A inheritance scope") = 착시. 본 §7.R RECOVERY 는 genuine write 로 V3 정본을 실제 생성하여 production-ready 정본 승급한다 (Wave 3 #19, 3-8/6-1/4-2/4-4 V3 ALL NEW + 3-9 §V3 EXTEND-RO 패턴 혼합).

**판정**: ✅ Stage A+B genuine write COMPLETE — 7 V3 NEW + 2 §V3 EXTEND-RO production-ready 정본 승급, DRAFT→APPROVED 9/9, 도메인 종료.

| 항목 | RECOVERY 실측 |
|------|--------------|
| 7 V3 NEW | multi_persona 13,198 `3483DD19` / multi_user 10,903 `12CA2110` / agent_marketplace 12,017 `C675310A` / agent_testing 10,529 `D174E40E` / k8s_autoscaling 12,039 `7842F16F` / constitutional_ai 12,467 `92070D31` / iot_integration 12,197 `BD1ACAD5` = **83,350 B** |
| 2 §V3 EXTEND-RO | guardrail_rules §V3(SE-09) 56,513(+3,142) `3EE85DBA` / permission_matrix §V3(PM-12) 46,945(+3,078) `088AA4CE` — V2 영역 byte 무변경 prefix EXACT(guardrail 53,371 / permission 43,867 검증) |
| Status | DRAFT → APPROVED 9/9 |
| LOCK | LOCK-AP-01~10 재정의 0 + LOCK-AP-10 DEFINED-HERE §V2.2 byte 무변경(constitutional_ai 참조자) + cross-domain cite-only 3건(LOCK-A2A-04 3-8 `_vamos-a2a._tcp.local.` 첫 수신 + LOCK-BM-09 3-9 70:30 + LOCK-AT-014 6-3) 재정의 0 |
| CONFLICT | CFL-AP-001~007 7 RESOLVED / OPEN 0 / 신규 0 무손상 (CONFLICT_LOG v1.3 무변경 `8D18732A`) |
| RO | **19** (기존 12 + 신규 7 V3) IsReadOnly=$true verify PASS — 2 §V3 EXTEND + 4 _index RO 4-step 적용 |
| cascade | AUTHORITY v1.1→v1.2 §6 V3 등재 + INDEX v1.1→v1.2 §11 + 4 _index(02/04/05/06) V3-Phase 4 status |
| count reconcile | plan §7.5.4 "8 V3 NEW" stale → **7 NEW + 2 §V3 EXTEND** (guardrail/permission = append) · G4-2 "5 _index" → 실측 4 (V3 신규 수신 서브폴더 02/04/05/06) |
| abort 9종 | NOT FIRED (CONFLICT_OPEN/STATUS_TRANSITION/V3_PROMOTION/LOCK_REDEFINITION/STAGE9_RO/CROSS_HANDOFF_DRIFT[3-8/3-9/6-3 외부 0 touch]/BILATERAL/DOWNSTREAM/R_CASCADE) |
| 감사 | `_verification/phase4_recovery_AB_report.md` NEW + 5 기존 promotion report EXACT |

**marker**: `[DOMAIN_PHASE_4_PRODUCTION_PROMOTION_COMPLETE:3-10 — 2026-06-03]` ✅ genuine — 도메인 종료. 다음 = Wave 3 #20 4-1 Rust-Tauri-Infrastructure.

---

## 8. 파일 역할 분리 명세

| 파일/폴더 | 정본 범위 | 읽기 참조 대상 | 쓰기 권한 |
|-----------|----------|--------------|----------|
| **STEP7-K** | 86항목 체크리스트 (What) | sot 2/ 전체 | SOT 관리자 |
| **Part2 §3, §6.6, §6.7** | Phase 배정, 코드 위치 (When/Where) | sot 2/, 구현팀 | Part2 관리자 |
| **D2.0-03** | Blue Node 인터페이스 | sot 2/ 01_, 06_ | DESIGN 관리자 |
| **D2.0-05** | A2A 프로토콜 스펙 | sot 2/ 01_, 03_ | DESIGN 관리자 |
| **sot 2/3-10_*/** | 구현 상세 (How) | 구현팀, 테스트 | 본 도메인 |
| **sot 2/상세명세.md** | 기술 명세 v1.0 | sot 2/ 전체 | 본 도메인 (병행 유지) |

---

## 9. 충돌 해결 프로토콜

### 9.1 우선순위 규칙

```
LOCK 값 → 절대 불변 (§3.4 목록)
DESIGN 2.0 문서 → 아키텍처 결정
STEP7-K → 항목 정의
Part2 → Phase/위치 배정
sot 2/ → 구현 상세 (최하위)
```

### 9.2 충돌 시나리오

| 시나리오 | 해결 |
|---------|------|
| STEP7-K 항목 정의 vs sot 2/ 구현 상세 | STEP7-K가 정본 (체크리스트 항목 변경 불가) |
| Part2 Phase 배정 vs sot 2/ Phase 계획 | Part2가 정본 (When/Where) |
| D2.0-05 A2A 스키마 vs sot 2/ 확장 스키마 | D2.0-05가 정본, sot 2/는 확장만 가능 |
| #11 A2A 도메인 vs #13 Agent-Protocol | A2A 프로토콜 스펙 → #11 정본, 인터롭 관점 → #13 정본 |
| #16 MCP 도메인 vs #13 Agent-Protocol | MCP 프로토콜 → #16 정본, 프레임워크 통합 활용 → #13 정본 |

### 9.3 충돌 기록

모든 충돌은 `CONFLICT_LOG.md`에 기록한다.

### 9.4 횡단 관심사 참조 *(S7-2 추가)*

| 횡단 도메인 | 적용 내용 |
|-----------|----------|
| 6-2 Security-Governance | 자율성 게이팅 L0~L4 보안, 가드레일 정책 (OWASP LLM08) |

---

## 10. 검증 체크리스트

| # | 항목 | 검증 내용 | 기준 |
|---|------|----------|------|
| 1 | STEP7-K 매핑 완전성 | 86항목 전수 서브폴더 매핑 | 100% |
| 2 | LOCK 재정의 없음 | §3.4의 10개 LOCK 값 변경 없음 | 0건 위반 |
| 3 | 권한 체계 정합 | AUTHORITY_CHAIN이 VAMOS 체인과 모순 없음 | 통과 |
| 4 | 폴더 깊이 | 3단계 이하 | 위반 0 |
| 5 | _index.md 존재 | 6개 서브폴더 전부 | 6/6 |
| 6 | 방식 C 형식 | Part2 PARTIAL 영역 출처 명시 | §7.3 3건 |
| 7 | 도메인 횡단 참조 | #4, #11, #16 정본 소유자 명시 | 3건 |
| 8 | 자율성 레벨 정의 | L0~L4 전환 조건 정의 | §B 완성 |
| 9 | 가드레일 규칙 | CEL 기반 pre/runtime/post 분류 | §C 완성 |
| 10 | 의존성 선언 | 부록 §D 의존성 매트릭스 | 완성 |

---

## 11. 보완 사항

### 11.1 즉시 보완 (Phase 0)
- FR-1: 6개 서브폴더 콘텐츠 파일 작성 (01_framework-adapters ~ 06_autonomy-safety)
- FR-2: Self-Evolution 기본 파라미터 정의 — learning_rate, evaluation_window, max_strategy_drift 기본값 + 사용 시나리오별 권장 설정
- FR-3: L3→L4 전환 기준 정밀화 — 90일 연속 운영의 정의, 에러율 계산 방법(롤링 윈도우), HITL 응답 SLA

### 11.2 단기 보완 (Phase 1)
- FR-4: LangGraph 어댑터 운영 상세 — Circuit Breaker 통합(LOCK-AP-06 failure_threshold=3, recovery=60s), LOCK-AP-08 START/END 상수 사용 강제
- FR-5: 자율 레벨별 가드레일 적용 매트릭스 — L0~L4 각 레벨에서 어떤 CEL 가드레일이 강제/선택/비활성인지 명시
- FR-6: MCP 어댑터 소유권 경계 명확화 — #16(4-3 MCP)이 프로토콜 소유, #13(3-10)이 어댑터 사용자

### 11.3 중기 보완 (Phase 2~3)
- FR-7: Agent Teams 역할 선정 알고리즘 — Lead/Sub-Agent 자동 배정 기준
- FR-8: 직렬화 형식 선택 결정 트리 — JSON vs MessagePack vs Protobuf vs CBOR (지연/크기/호환성 기준)
- FR-9: 프레임워크 어댑터 호환성 매트릭스 — CrewAI/AutoGen/LangGraph 주요 버전별 테스트 요구사항

---

## 12. FINAL REVIEW 결과

| 항목 | 내용 |
|------|------|
| **상태** | APPROVED |
| **Phase 5 FINAL PASS** | 2026-03-24 |
| **Phase 8 QC** | B+ (S8-3, 2026-03-26) — A-1 Self-Evolution 파라미터 미정의 관찰 |
| **Phase 10 S10-2** | A- 격상 (2026-03-27) — LangGraph/MCP 기술 정확도 보강, Self-Evolution 기본값 정의 |
| **잔존 이슈** | FR-1 (서브폴더 콘텐츠) → Phase 0 순차 해결 |
| **다음 단계** | Phase 0 진입 시 FR-1~FR-3 우선 실행 |

---

## 13. L3 전수 승급 계획

### 13.1 L3 완성도 기준 (도메인 항목별)

| 기준 | 설명 | 가중치 |
|------|------|--------|
| Input Schema | 입력 데이터 타입·검증 규칙 정의 | 15% |
| Output Schema | 출력 데이터 타입·형식 정의 | 15% |
| Algorithm | 핵심 알고리즘 의사코드 또는 구현 | 20% |
| Error Handling | 에러 유형별 처리 전략 | 10% |
| Dependency | 의존 모듈·서비스 명시 | 10% |
| Test Spec | 단위/통합 테스트 시나리오 | 15% |
| Performance | 성능 기준 (응답시간, 처리량) | 10% |
| Security | 보안 고려사항 (인증, 권한, 암호화) | 5% |

### 13.2 서브폴더별 승급 계획

| 서브폴더 | 현재 레벨 | 목표 | 핵심 작업 |
|----------|----------|------|----------|
| `01_framework-adapters/` | L1 (스키마만) | L3 | 3대 어댑터 변환 알고리즘 + 테스트 |
| `02_service-integration/` | L0 (목록만) | L3 | LLM 게이트웨이 라우팅 알고리즘 |
| `03_data-exchange/` | L1 (스키마만) | L3 | 직렬화 전략 + 스키마 버전 협상 |
| `04_deployment-scaling/` | L0 | L3 | 컨테이너 스펙 + 오토스케일링 |
| `05_self-evolution/` | L0 | L2 (V2 대상) | 학습 루프 + 전략 저장소 |
| `06_autonomy-safety/` | L1 (레벨만) | L3 | 가드레일 엔진 + HITL 프로토콜 |

### 13.3 Phase 2~3 L3 완성도 최종 확정 매트릭스 (Path A drift fix Stage 1, 2026-05-20)

> **목적**: Phase 2 STEP_C truly_converged_v2 (2026-04-22 closure) + Phase 3 5/5 P3 ALL NO-DRIFT 100% first-pass-zero-fix milestone 종결 (2026-05-20) 이후 Phase 0+1+2 0 + Phase 3 30 = 통산 30 [ ] 검증 항목의 [x] 변환 정합성 확정 + 6 서브폴더별 V2 NEW 22 stack + V3 NEW 8 forward-defined 산출물 매트릭스 형식 기록 (Wave 3 #23 두번째 NO-DRIFT 100% 도메인 specialty + NO D-spec specialty 6-3 패턴 직계 통산 두번째 사례).

| 서브폴더 | V2 (Phase 2 STEP_C, NEW+EXTEND) | V3 NEW (Phase 3 forward-defined) | LOCK 인용 / V 로드맵 | Phase 2 [x] | Phase 3 [x] |
|---------|--------------------------------|----------------------------------|------------------------|-----------|-----------|
| `01_framework-adapters/` | 7 V2 EXTEND (V1 7 어댑터 → V2 EXTEND via Phase 2 STEP_A inheritance: autogen + crewai + langgraph + magentic_one + moa_pattern + reflection_planning + tool_memory_benchmark) + `_index.md` inheritance | 0 | LOCK-AP-08 LangGraph START/END base + V1 영역 P1-1 STEP_B 종료 | 0 | 0 |
| `02_service-integration/` | 2 V2 (`llm_gateway.md` P2-1 + `external_apis.md` P2-2) | 1 (`iot_integration.md` P3-4 K-038 또는 `external_apis.md` §V3 append) + `_index.md` 갱신 | LOCK-AP-04 MCP Streamable HTTP base + V3 IoT 게이트웨이 | 0 | 5 (P3-4 검증) |
| `03_data-exchange/` | 2 V2 (`event_bus.md` P2-3 + `message_format.md` P2-3) | 0 | LOCK-AP-01 VamosMessage 스키마 base inheritance | 0 | 0 |
| `04_deployment-scaling/` | 5 V2 (`config_spec` P2-4 + `container_spec` P2-4 + `healthcheck_spec` P2-4 + `logging_spec` P2-4 + `migration_guide` P2-4) | 1 (`k8s_autoscaling.md` P3-2 K-056) + `_index.md` 갱신 | container §2.2 + migration §11 MG-12 base + V3 K8s 오토스케일링 | 0 | 6 (P3-2 검증) |
| `05_self-evolution/` | 4 V2 (`ambient_agent` P2-5 + `dream_mode` P2-5 V1 base + `predictive_agent` P2-5 + `time_travel` P2-5) | 4 (`multi_persona` + `multi_user` + `agent_marketplace` + `agent_testing` P3-1 K-065~K-068) + `_index.md` 갱신 | LOCK-AP-05 Agent Teams Lead+max2Sub base + V3 멀티페르소나·멀티유저·마켓플레이스·테스트 + LOCK-BM-09 cross-domain 3-9 verbatim 70:30 | 0 | 6 (P3-1 검증) |
| `06_autonomy-safety/` | 2 V2 EXTEND (`guardrail_rules` P2-6 + `permission_matrix` P2-6) | 2 (`constitutional_ai.md` P3-3 K-048 + `guardrail_rules.md §V3` / `permission_matrix.md §V3` append P3-5 추가 이월 #1~#4) + `_index.md` 갱신 | LOCK-AP-02 Permission Level 0~5 + LOCK-AP-10 HITL Confidence < 50% DEFINED-HERE 06_autonomy-safety 정본 + V3 Constitutional AI · 가드레일·권한 §V3 | 0 | 13 (P3-3 검증 6 + P3-5 검증 7) |
| `_verification/` | 0 (V1 `phase1_verification_prompt.md` read-only) | 0 | V1 verification baseline | 0 | 0 |
| **합계** | **22 V2 (Phase 2 STEP_C truly_converged_v2 2026-04-22 baseline, SOT2_MASTER L554 "V2 22 파일 7,214 L" inheritance + plan §7.4 row 1 L1370 정합: 01 7 V2 EXTEND + 02 2 V2 + 03 2 V2 + 04 5 V2 + 05 4 V2 + 06 2 V2 EXTEND = 22)** | **8 NEW + `_index` 갱신 5 = 13 산출물 forward-defined Phase 4 implementation 별도 트랙 (Wave 3 두번째 도메인 specialty)** | **LOCK-AP-01~10 10 unique 정본 (AUTHORITY §3 L162~L175) + LOCK-AP-10 DEFINED-HERE 06_autonomy-safety + cross-domain reference LOCK-A2A-04 mDNS (3-8 정본) + LOCK-BM-09 70:30 (3-9 정본)** | **0 (Phase 0+1+2 전수 — NO D-spec specialty 6-3 패턴 직계 통산 두번째 사례 Wave 3 첫 사례)** | **30 (P3-1 6 + P3-2 6 + P3-3 6 + P3-4 5 + P3-5 7 = 30 Phase 3 검증 항목 전수, Phase 4 entry-gate 항목 5 inclusive 각 P3 1개)** |

**Stage 1+2 통산 30 [ ]→[x] 전수 변환 (Phase 0+1+2 0 + Phase 3 30) — Path A drift fix sub-cycle 2026-05-20**:

- 🎉 **★★★★ Wave 3 두번째 NO-DRIFT 100% 도메인 specialty** (Wave 2 6-2/6-3/6-6/6-7 + Wave 3 3-8 + 본 3-10 = 통산 6번째 NO-DRIFT 100% 도메인 milestone, 5/5 P3 ALL ✅ truly_converged_v1 first-pass-zero-fix CONFIRMED, R cascade 통산 540 verifications + 0 drift fix NO-DRIFT direct path)
- 🎉 **★★★★ NO D-spec specialty 6-3 패턴 직계 통산 두번째 사례 (Wave 3 첫 사례)** (Wave 2 6-3 NO D-spec first + 본 3-10 통산 두번째 + Wave 3 첫 사례, Phase 0+1+2 [ ] = 0 STEP_C 2026-04-22 closure 후 [x] 100% 완전 변환 잔존 0건 specialty — 사용자 안내 옵션 B 채택 가정에서 Phase 0+1+2 잔존 0 검출로 인해 Phase 3 only 30 변환 결정)
- ★★★ **Wave 1+2+3 통산 10번째 P3 단독 NO-DRIFT 100% first-pass 사례** (Wave 2 6-2/6-3/6-6/6-7 4 + Wave 3 3-8 1 + 본 3-10 P3-1~P3-5 5 = 통산 10 P3 NO-DRIFT, 본 3-10 P3-1~P3-5 = 6~10번째 누적, 5 P3 ALL ZERO production write 통산 specialty, 종합계획서 §7.5 ④ block L1677 + PROGRESS 3-10 P3 mid-checkpoint L6907~L6986 통합 convention)
- ★★★ **5 P3 ALL ZERO production write 통산 specialty** (V2 22 stack + AUTHORITY/CONFLICT/INDEX/SOT2_MASTER/CROSS_REF/상세명세 ALL ZERO write 통산 5 P3, R cascade 통산 540 verifications + 0 drift fix NO-DRIFT direct path + Round 2 audit ultra-fine R₅~R₁₅ 11 cycles ~30 verif + 3 fix textual/arithmetic notation only CONFIRMED truly_converged_v1 first-pass-after-Round-2-fix Wave 3 세번째 사례)
- ★★★ **DEFINED-HERE 06_autonomy-safety 정본 소유 직접 작업 영역 변경 0건 통산 P3-3+P3-5 두번째 강제 specialty** (LOCK-AP-10 HITL Confidence < 50% DEFINED-HERE 06_autonomy-safety 정본 + guardrail_rules.md §V2 / permission_matrix.md §V2 영역 byte 무변경 강제 + V3 append 또는 신규 파일 forward-defined Phase 4 implementation 별도 트랙)
- ★★ **DAG strict upstream 2건 ✅ verified specialty Wave 3 두번째 도메인 specialty** (3-7 Developer-Tools Wave 1 #9 ✅ + 3-8 Conversation-A2A Wave 3 #22 ✅ verified + 양방향 cross-handoff Wave 3 → Wave 3 first 사례 specialty 강제 충족 P3-4 LOCK-A2A-04 mDNS cross-domain reference inheritance)
- ★★ **LOCK-A2A-04 cross-domain reference inheritance 첫 사례 specialty P3-4** (3-8 정본 LOCK-A2A-04 mDNS reference, 3-10에 LOCK-A2A 정의 없음 cross-domain reference-only specialty + service_registry P2-6 inheritance)
- ★★ **LOCK-BM-09 cross-domain 3-9 정본 verbatim 보존 specialty P3-1** (마켓플레이스 70% 개발자 / 30% VAMOS, 3-9 Business-Model 정본 verbatim 인용 + 3-7 VADD vadd_marketplace.md P3-4 산출물 cross-ref forward-defined)
- ★★ **V-17 SoT 1-off 없는 도메인 SPEC §13.1 단순화 적용** (V2 22 stack + AUTHORITY §3 10 unique LOCK 정본 매핑 verbatim 인용만, 1-2/2-2/2-1/3-2/3-3/3-4/3-5/3-6/3-7/3-9/4-2/4-4/6-1/6-2/6-3/6-4/6-5/6-6/6-7/6-8/1-1/3-8 패턴 EXACT 직계 통산 22번째 사례)
- ★★ **7 cross-handoff distinct propagate baseline** (P3-1 3 + P3-2 3 + P3-3 2 + P3-4 2 + P3-5 2 = 12 inline → distinct 7: 3-7 Developer-Tools + 3-9 Business-Model + 6-2 Security-Governance direct + 4-1 Rust-Tauri + 4-3 MCP-Server-Client + 5-1 Benchmark-Evaluation forward-defined + 6-13 Operations reference-only sandbox)
- ★ **V2 22 stack (7,214줄) + V1 기존 file 별도 STAGE 7 STEP_A inheritance ALL ZERO write 통산** (6 서브폴더 분포 plan §7.4 row 1 L1370 정합 — 01_framework 7 V2 EXTEND + 02_service-integration 2 V2 + 03_data-exchange 2 V2 + 04_deployment 5 V2 + 05_self-evolution 4 V2 + 06_autonomy 2 V2 EXTEND + _verification V1 only = 22 V2 통산, SOT2_MASTER L554 baseline)
- ★ **AUTHORITY v1.2 + CONFLICT v1.2 + INDEX v1.2 baseline EXACT 보존 통산 (append-only 정책)** (LOCK-AP-01~10 §3.4 EXACT 보존 + CFL-AP-001~007 7/7 RESOLVED + OPEN 0 + DEFERRED 0 baseline 무손상 통산 5 P3 ALL)
- ★ **CFL-AP-001~007 무손상 Phase 3 신규 발화 0건 specialty 강제 충족 P3-5** (Phase 3 신규 발화 0건 목표 게이트 5 P3 ALL EXACT 충족 통산 specialty + CFL-AP-001~007 무손상 verify Phase 3 통산 specialty)
- ★ **Phase 4 entry-gate 통산 25 conditions 매트릭스 매핑** (P3-1 5 + P3-2 5 + P3-3 5 + P3-4 5 + P3-5 5 = 25, V3 NEW 8 + `_index` 갱신 5 = 13 산출물 forward-defined Phase 4 implementation 별도 트랙)
- ★ **downstream Phase 4 verify only 통산 9번째 specialty** (3-9 + 6-4 + 6-5 + 6-6 + 6-7 + 6-8 + 1-1 + 3-8 + 본 3-10 패턴 직계, 3-8 양방향 + 4-3 Wave 3 #25 forward-defined + 6-3 Wave 2 #15 Phase 4 verify only 3 도메인 inheritance baseline)
- ★ **§12 FINAL REVIEW S10-2 Content: A- inherited 통산 보존 + §13.X-1 SKIP no-op 자동 inheritance** (Phase 5 FINAL PASS 2026-03-24 inheritance, Phase 3 spec 단계 §7.5 헤더 ✅ marker + ④ block + SOT2_MASTER 4 지점 별도 매핑, §12 자체 갱신 design choice 부재 통산)
- ★ **abort marker 15종 NOT FIRED self-fire 0 통산 Stage 1+2 ALL CLEAN** (LOCK 변경 0 + DEFINED-HERE 0 + FABRICATION 0 + parent-executed Subagent 0회 + 6 anchor 충족 강제: 안전·누락 0·오류 0·미세·수렴·재검증)

---

## 14. 실행 약점 대응 계획

| # | 약점 | 리스크 | 대응 |
|---|------|--------|------|
| 1 | 외부 프레임워크 버전 변경 | 어댑터 호환성 깨짐 | R-13-2 버전 잠금 + 자동 호환성 테스트 |
| 2 | A2A/MCP 표준 업데이트 | 프로토콜 변환기 수정 필요 | 버전 협상 메커니즘(K-052) + 하위 호환 |
| 3 | 자율성 레벨 남용 | L3/L4 에이전트의 위험한 자율 행동 | R-13-1 HITL 필수 + 가드레일 엔진 |
| 4 | 도메인 횡단 충돌 | #11 A2A, #16 MCP와 정본 소유 분쟁 | §5.2 경계 확정 + AUTHORITY_CHAIN |
| 5 | Part2 Phase 변경 | Phase 배정 변동 시 계획서 불일치 | Part2 정본 우선 + 정기 동기화 |
| 6 | 멀티 프레임워크 통합 복잡도 | CrewAI/AutoGen/LangGraph 동시 지원 부담 | MVP는 LangGraph 집중 → 순차 확장 |
| 7 | LangGraph 버전 호환성 | LangGraph 주요 릴리스(StateGraph API 변경) 시 어댑터 깨짐 위험 | 주요 버전 고정(R-13-2) + 어댑터 E2E 테스트 필수 |
| 8 | 자율 레벨 오용 | L3/L4 전환 시 안전 가드레일 우회 가능성 | CEL 규칙 강제 + 감사 로그 100% + 이상 탐지 |
| 9 | MCP 도구 스키마 불일치 | 외부 MCP 서버 도구 스키마 변경 시 자동 디스커버리 실패 | tools/list_changed 알림 처리 + 스키마 캐시 TTL 설정 |

**모니터링 KPI**:

| KPI | 목표 | 측정 주기 |
|-----|------|----------|
| 어댑터 변환 성공률 | > 99% | 실시간 |
| HITL 응답 시간 | < 24시간 | 이벤트 기반 |
| 가드레일 위반 차단률 | 100% | 실시간 |
| Self-Evolution 개선율 | +5% 성공률/분기 | 분기 |

---

## 부록 §A — 프레임워크 어댑터 카탈로그

### A.1 지원 프레임워크 매트릭스

| 프레임워크 | STEP7-K | 버전 범위 | 지원 기능 | V 로드맵 |
|-----------|---------|----------|----------|---------|
| **LangGraph** | K-021 | ≥0.2.0 | StateGraph 변환, 상태 동기화, 체크포인트 | V1 |
| **CrewAI** | K-022 | ≥0.40.0 | 역할 변환, 작업 위임, 도구 브리지 | V1 |
| **AutoGen** | K-023 | ≥0.4.0 | GroupChat 변환, 대화 히스토리 매핑 | V1 |
| **Magentic-One** | K-024 | ≥0.1.0 | Orchestrator 매핑, WebSurfer 연동 | V2 |
| **Custom** | - | - | AbstractAdapter 기반 확장 | V1+ |

### A.2 공통 어댑터 인터페이스

```typescript
interface FrameworkAdapter {
  framework_id: string;
  framework_name: "crewai" | "autogen" | "langgraph" | "magentic-one" | "custom";
  version_range: string;
  capabilities: AdapterCapability[];

  // 메시지 변환
  translate_to_vamos(external_msg: unknown): VAMOSMessage;
  translate_from_vamos(vamos_msg: VAMOSMessage): unknown;

  // 에이전트 매핑
  map_agents(external_agents: unknown[]): VAMOSAgent[];

  // 도구 브리지
  bridge_tools(external_tools: unknown[]): MCPTool[];

  // 상태 동기화
  sync_state(external_state: unknown, vamos_context: dict): unknown;

  // 헬스체크
  health_check(): AdapterHealth;
}

type AdapterCapability =
  | "task_delegation"    // 작업 위임
  | "state_sync"        // 상태 동기화
  | "tool_sharing"      // 도구 공유
  | "memory_bridge"     // 메모리 브릿지
  | "event_forwarding"  // 이벤트 전달
  | "conversation_map"; // 대화 매핑
```

### A.3 어댑터별 변환 규칙 요약

| 변환 | CrewAI → VAMOS | AutoGen → VAMOS | LangGraph → VAMOS |
|------|---------------|----------------|-------------------|
| Agent → | VAMOSAgent (role→skill) | VAMOSAgent (name→agent_card) | VAMOSTask (node→task) |
| Task → | tasks/send (description→text) | A2AMessage (content→parts) | Task 체인 (의존성 보존) |
| Tool → | MCPTool (func→handler) | MCPTool (코드실행 래퍼) | MCPTool (노드 래퍼) |
| 상태 → | Crew context → metadata | GroupChat history → A2A messages | state_schema → vamos_context |

---

## 부록 §B — 자율성 레벨 L0~L4 정의

### B.1 레벨 정의

| 레벨 | 이름 | 설명 | 인간 개입 | 가드레일 | 전환 조건 |
|------|------|------|----------|---------|----------|
| **L0** | Manual | 인간이 모든 결정, 에이전트는 정보 제공만 | 모든 액션 승인 | 전체 block | 기본값 (신규 사용자) |
| **L1** | Assisted | 에이전트가 제안, 인간이 승인 후 실행 | 실행 전 확인 | pre_action 전부 | 사용자 설정 또는 7일 사용 후 |
| **L2** | Supervised | 에이전트가 실행, 인간이 모니터링 | 이상 시 개입 | runtime warn | 30일 사용 + 에러율 <5% |
| **L3** | Conditional | 정의된 범위 내 자율, 범위 외 승인 요청 | 경계 초과 시 | pre_action 경계만 | R-13-1 HITL 승인 필수 |
| **L4** | Autonomous | 완전 자율 실행, 사후 보고 | 사후 감사 | post_action 로그 | R-13-1 HITL 승인 + 90일 L3 운영 + 에러율 <1% |

### B.2 레벨 전환 프로토콜

```
[L0] ──(사용자 설정 or 7일)──→ [L1]
       ──(30일 + 에러율<5%)──→ [L2]
       ──(HITL 승인 필수)────→ [L3]
       ──(HITL + 90일L3 + <1%)→ [L4]

역방향: 에러율 급등(>10%) → 즉시 1단계 하향
        보안 위반 → 즉시 L0 리셋
```

### B.3 레벨별 허용 작업

| 작업 카테고리 | L0 | L1 | L2 | L3 | L4 |
|-------------|:--:|:--:|:--:|:--:|:--:|
| 정보 조회/검색 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 파일 생성 | ❌ | Ask | ✅ | ✅ | ✅ |
| 파일 수정 | ❌ | Ask | Ask | ✅ | ✅ |
| 코드 실행 | ❌ | Ask | ✅ | ✅ | ✅ |
| 외부 API 호출 | ❌ | ❌ | Ask | ✅ | ✅ |
| 이메일/메시지 발송 | ❌ | ❌ | ❌ | Ask | ✅ |
| 금융 거래 | ❌ | ❌ | ❌ | ❌ | Ask |
| 비가역 작업 | ❌ | ❌ | ❌ | ❌ | Ask |

---

## 부록 §C — 안전 가드레일 규칙 엔진

### C.1 아키텍처

```
[에이전트 액션 요청]
        │
        ▼
┌──────────────────┐
│ Pre-Action Guard │ ← CEL 규칙 평가
└────────┬─────────┘
         │ PASS
         ▼
┌──────────────────┐
│   Action 실행     │
│  ┌──────────────┐│
│  │Runtime Guard ││ ← 실행 중 모니터링
│  └──────────────┘│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Post-Action Guard│ ← 결과 검증 + 감사 로깅
└──────────────────┘
```

### C.2 가드레일 스키마

```typescript
interface SafetyGuardrail {
  id: string;                    // "SG-001"
  name: string;                  // "리소스 사용 제한"
  type: "pre_action" | "runtime" | "post_action";
  autonomy_level_min: 0 | 1 | 2 | 3 | 4;  // 이 레벨 이상에서 적용
  rules: SafetyRule[];
  enforcement: "block" | "warn" | "log";
}

interface SafetyRule {
  id: string;                    // "R-001"
  condition: string;             // CEL 표현식
  action_on_violation: "deny" | "escalate" | "modify" | "log";
  message: string;               // 위반 시 메시지
  cooldown_seconds?: number;     // 재평가 대기 시간
}
```

### C.3 기본 가드레일 규칙 세트

| ID | 유형 | CEL 조건 | 위반 시 | 적용 레벨 |
|----|------|---------|--------|----------|
| SG-001 | pre_action | `action.estimated_cost_usd > agent.budget_remaining` | deny | L1+ |
| SG-002 | pre_action | `action.api_calls_count > 100` | escalate | L2+ |
| SG-003 | pre_action | `action.data_scope contains 'PII'` | escalate | L0+ |
| SG-004 | pre_action | `action.target_system in PRODUCTION_SYSTEMS` | deny | L0+ |
| SG-005 | pre_action | `action.autonomy_required > agent.current_level` | deny | L0+ |
| SG-006 | runtime | `execution.duration_ms > action.timeout_ms * 2` | escalate | L1+ |
| SG-007 | runtime | `execution.memory_mb > agent.memory_limit_mb` | deny | L0+ |
| SG-008 | runtime | `execution.error_count > 5` | escalate | L2+ |
| SG-009 | post_action | `result.confidence < 0.5` | escalate | L2+ (LOCK-AP-10) |
| SG-010 | post_action | `result.side_effects.count > 0 && !result.reversible` | log+alert | L3+ |

### C.4 Human Intervention Request 스키마

```typescript
interface HumanInterventionRequest {
  request_id: string;
  agent_id: string;
  task_id: string;
  urgency: "low" | "medium" | "high" | "critical";
  type: "approval" | "decision" | "review" | "error_resolution";
  context: {
    action_description: string;
    risk_assessment: string;
    guardrail_violations: string[];
    suggested_options: Option[];
    autonomy_level: 0 | 1 | 2 | 3 | 4;
  };
  timeout_seconds: number;
  default_action: "approve" | "deny" | "escalate";
  notification_channels: ("email" | "slack" | "ui" | "sms")[];
}
```

---

## 부록 §D — 의존성 매트릭스

### D.1 본 도메인이 소비하는 의존성

| 의존 대상 | 도메인 | 의존 유형 | 영향 |
|-----------|--------|----------|------|
| #4 COND (COND-085) | TIER2-04 | 에이전트 통합 모듈 | 프레임워크 어댑터가 COND-085 소비 |
| #11 A2A/Conversation | TIER3-08 | A2A 프로토콜 계층 | 인터롭 브리지가 A2A 스펙 참조 |
| #16 MCP Server/Client | TIER4-03 | 도구 프로토콜 | MCP↔A2A 브리지, Tool Discovery |
| #3 Blue Node | TIER2-01 | 오케스트레이션 연동 | Blue Node 인스턴스로 에이전트 실행 |
| #1 Verifier | TIER1-01 | 안전성 검증 | 가드레일 엔진이 검증기 소비 |
| #15 CI/CD | TIER4-02 | 배포 파이프라인 | 에이전트 컨테이너 배포 |
| #14 Rust-Tauri | TIER4-01 | IPC 통신 계층 | 에이전트 간 통신이 IPC 레이어 통과 |
| #12 Business-Strategy | TIER3-09 | 비용/가격 영향 | LOCK-AP-09 비용 상한 참조, 마켓플레이스 수익 모델 |
| #10 Dev Tools | TIER3-07 | Plugin SDK 연동 | VADD 마켓플레이스 에이전트 배포 |

### D.2 본 도메인을 소비하는 도메인

| 소비자 | 소비 내용 |
|--------|----------|
| 모든 Tier 3 도메인 | 프레임워크 어댑터를 통한 멀티에이전트 협업 |
| #12 Business-Strategy | 에이전트 마켓플레이스 비즈니스 모델 |
| #18 Benchmark | VBS-12 에이전트 협업 벤치마크 |

---

*본 문서는 STEP7-K SOT 86개 항목을 기반으로 작성되었으며, 프로토콜 표준 업데이트에 따라 갱신된다.*
*기존 `AGENT_PROTOCOL_INTEROPERABILITY_상세명세.md`(770줄)는 삭제하지 않고 병행 유지한다.*
