# Security-Governance 구조화 종합 계획서

> **버전**: v1.0
> **작성일**: 2026-03-24
> **목적**: sot 2/6-2_Security-Governance/를 보안·거버넌스 구현 정본으로 구조화하고, Part2 §6.5 FULL 영역 + D2.0-07 정본 + STEP7-E 체크리스트와의 역할 분리·참조 체계를 확립
> **Status**: APPROVED
> **Tier**: 6 (System-wide Components)
> **SOT 출처**: D2.0-07 (Safety/Cost/Approval 정본), STEP7-E (보안/안전/거버넌스 전수비교 92건)
> **Part2 상태**: FULL (§6.5 L4861-4961)
> **세션**: S6-3

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
- [부록 A: 소비 도메인 매트릭스](#부록-a-소비-도메인-매트릭스)
- [부록 B: STEP7-E 92건 매핑 요약](#부록-b-step7-e-92건-매핑-요약)
- [부록 C: Guardrails 3-Layer × Part2 §6.5 15항목 교차 참조](#부록-c-guardrails-3-layer--part2-65-15항목-교차-참조)
- [부록 D: HMAC 키 운영 절차 매트릭스](#부록-d-hmac-키-운영-절차-매트릭스)

---

## 1. 현재 상태 분석

### 1.1 기존 문서 현황

| 문서 | 위치 | 역할 | 상태 |
|------|------|------|------|
| **D2.0-07** | docs/sot/ | Safety/Cost/Approval 설계 정본 | LOCK — 16섹션, §0~§15 + Guardrails 3-Layer |
| **STEP7-E** | docs/sot/ | 보안/안전/거버넌스 전수비교 작업가이드 | 10 Part, 92건 항목 (CRITICAL 27 / HIGH 41 / MED 24) |
| **Part2 §6.5** | docs/guides/PART2 L4861-4961 | 보안 상세 구현 (15개 항목) | FULL — 4개 하위 섹션 (6.5.1~6.5.4) |
| **Part2 V2-P2/P3** | docs/guides/PART2 L2878-3688 | 보안 Phase (V2 COND + Agent Teams) | PARTIAL — 보안 관련 항목 분산 |

### 1.2 sot 2/6-2_Security-Governance/ 현재 파일

| 항목 | 상태 |
|------|------|
| 종합계획서 | 본 문서 (신규 작성) |
| AUTHORITY_CHAIN.md | 신규 작성 |
| CONFLICT_LOG.md | 신규 작성 |
| 서브폴더 4개 | 신규 생성 (01~04) |
| 기존 명세 파일 | 없음 (Tier 6 신규 도메인) |

### 1.3 핵심 문제

1. **횡단 보안 정책 분산**: Part2 §6.5에 보안 체크리스트가 있으나, 이를 소비하는 12개 도메인과의 참조 체계 부재
2. **D2.0-07 ↔ Part2 §6.5 역할 혼재**: D2.0-07의 Safety/Approval 설계와 Part2 §6.5의 구현 가이드가 중첩되어 단일 참조점 부재
3. **STEP7-E 92건 미매핑**: 92건 보안 보강 항목이 Part2/D2.0-07과 체계적으로 매핑되지 않음
4. **OWASP LLM Top 10 / STRIDE 갱신 추적 구조 없음**: 외부 표준 변경 시 VAMOS 매핑 업데이트 프로세스 미정의

### 1.4 Part2 §6.5 FULL 영역 요약 (방식 C)

> **출처**: PART2 §6.5 (L4861-4961)
> **Part2가 정본**: When + Where (각 보안 항목의 V1/V2/V3 배정, 코드 위치)
> **sot 2/가 정본**: What + How (보안 체크리스트 상세, HMAC 구현 패턴, STRIDE/OWASP 매핑 로직)

#### Part2 핵심 내용 요약

Part2 §6.5는 15개 보안 항목과 4개 하위 섹션으로 구성:
- **보안 항목 15건**: NeMo Guardrails, Guardrails AI, LlamaGuard, PII 마스킹, RBAC, Autonomy 레벨, P2 세션 승인, Docker 샌드박스, 승인 타임아웃, SQLCipher, API Key 관리, 입력 검증, HMAC-SHA256, GDPR, DEC-003 Allowlist
- **6.5.1** AI 코드 생성 보안 체크리스트 (7개 검증 항목): 입력 검증, SQL 바인딩, trace_id 위조 방지, Docker 네트워크 차단, API 키 노출 방지, 권한 체크, 에러 정보 유출
- **6.5.2** HMAC 타이밍 공격 방어 (5개 방어 항목): 상수 시간 비교, 키 길이 검증, 키 순환(90일), 리플레이 방지, 에러 응답 균일화 + Python 참조 코드
- **6.5.3** STRIDE 위협 모델 매핑 (6개 위협): Spoofing→JWT+RBAC, Tampering→HMAC, Repudiation→audit_log, Information Disclosure→Docker 격리, DoS→Cost Gate, Elevation→NEVER_AUTO
- **6.5.4** OWASP LLM Top 10 (2025) 매핑 (10개 위험): 각 LLM01~LLM10에 대한 VAMOS 완화 전략 + 적용 상태

---

## 2. 목표 구조 (최종 형태)

### 2.1 폴더 트리

```
D:\VAMOS\docs\sot 2\6-2_Security-Governance\
│
├── SECURITY_GOVERNANCE_구조화_종합계획서.md   ← 본 문서
├── AUTHORITY_CHAIN.md                        ← 권한 체계 선언
├── CONFLICT_LOG.md                           ← 충돌 기록부
│
├── 01_ai-code-security/                      ← AI 코드 생성 보안 체크리스트
│   └── _index.md
│
├── 02_hmac-timing-defense/                   ← HMAC 타이밍 공격 방어
│   └── _index.md
│
├── 03_stride-threat-model/                   ← STRIDE 위협 모델 매핑
│   └── _index.md
│
└── 04_owasp-llm-top10/                       ← OWASP LLM Top 10 (2025) 매핑
    └── _index.md
```

### 2.2 깊이 규칙

```
최대 3단계:
  6-2_Security-Governance/ → XX_{카테고리}/ → 파일.md           (2단계) ✅
  6-2_Security-Governance/ → XX_{카테고리}/ → {하위}/ → 파일.md  (3단계) ✅
  4단계 이상 → 절대 금지 ❌
```

### 2.3 네이밍 규칙

- **폴더명**: 영문 소문자 + 하이픈, 접두사 2자리 번호 (`01_`, `02_`, ...)
- **파일명**: 영문 소문자 + 언더스코어 (`.md` 확장자)
- **계획서 파일명**: `SECURITY_GOVERNANCE_구조화_종합계획서.md`

---

## 3. 권한 체계 선언

### 3.1 기존 VAMOS 권한 체인

```
RULE 1.3 > PLAN 3.0 > DESIGN 2.0 LOCK > DESIGN body > Schema/TECH_STACK
```

### 3.2 Security-Governance 확장 권한 체인

```
RULE 1.3
  > PLAN 3.0
    > DESIGN 2.0
      ├─ D2.0-07 전체 (Safety/Cost/Approval 정본)
      │   ├─ §1 Non-goal/금지 항목 (절대 금지 리스트 LOCK)
      │   ├─ §2 위험 등급/분류 (P0/P1/P2 LOCK)
      │   ├─ §3 승인 정책 (5-Gate System LOCK)
      │   ├─ §4 비용 상한/다운시프트 (LOCK)
      │   ├─ §10 Guardrails 3-Layer (LOCK)
      │   ├─ §13 RBAC 접근 제어 (LOCK)
      │   └─ §14 자율 운영 수준 (L0~L3 LOCK)
      └─ D2.0-07 §2.2A (STRIDE/Attack Tree/OWASP 통합)
        > Part2 §6.5 (구현 가이드: When + Where)
          > sot 2/6-2_Security-Governance/ (구현 상세: What + How) ← 본 도메인
            > STEP7-E (보강 항목 92건 = 체크리스트)
```

### 3.3 각 문서의 권한 범위

| 문서 | 권한 레벨 | 결정할 수 있는 것 | 결정할 수 없는 것 |
|------|----------|------------------|------------------|
| **D2.0-07** | DESIGN (LOCK) | Safety 정책, 승인 게이트, 비용 상한, Guardrails 아키텍처, RBAC, 자율 운영 수준 | 구현 일정, 코드 위치 |
| **Part2 §6.5** | IMPL-GUIDE | When(V1/V2별 보안 항목 배정), Where(보안 모듈 위치), 15개 보안 항목 목록 | 체크리스트 구현 상세, STRIDE/OWASP 매핑 로직 |
| **sot 2/6-2** | IMPL-DETAIL | What(보안 체크리스트 상세) + How(HMAC 패턴, STRIDE 대응, OWASP 완화) | When(Phase), LOCK 값 재정의 |
| **STEP7-E** | CHECKLIST | 보강 필요 항목 92건 ID + 우선순위 (CRITICAL/HIGH/MED) | 구현 방법 (→ sot 2/) |

### 3.4 도메인 경계 명시

| 인접 도메인 | 경계 |
|-----------|------|
| **0-0 Governance** | 6-2 = 보안 실행 정책 (STRIDE, OWASP, HMAC, 코드 보안). 0-0 = 전체 거버넌스 규칙(R1~R11), LOCK/FREEZE 레지스트리. 경계 = 보안 **규칙 정의**(0-0) vs 보안 **실행 상세**(6-2) |
| **4-2 CI/CD** | 6-2 = 보안 정책 정의 (SAST/DAST/의존성 스캔 기준). 4-2 = CI/CD 파이프라인에서 보안 스캔 **실행**. 경계 = 정책(6-2) vs 실행(4-2) |
| **4-3 MCP** | 6-2 = MCP Tool 보안 정책 (화이트리스트, 서명 검증). 4-3 = MCP 서버/클라이언트 구현. 경계 = 보안 요구사항(6-2) vs 기능 구현(4-3) |
| **6-3 Agent-Teams** | 6-2 = Agent 보안 정책 (자율성 게이팅, NEVER_AUTO). 6-3 = PARL 패턴, 팀 구성. 경계 = 보안 제약(6-2) vs 에이전트 아키텍처(6-3) |
| **6-5 SDAR** | 6-2 = 보안 위협 모델 (STRIDE). 6-5 = 자가진단/수리 파이프라인. 경계 = 위협 분류(6-2) vs 런타임 자가복구(6-5) |
| **6-12 Event-Logging** | 6-2 = 보안 이벤트 정의 (audit_log, 보안 위반 로깅). 6-12 = 이벤트 수집/저장 시스템. 경계 = 보안 이벤트 발행(6-2) vs 수집(6-12) |

### 3.5 LOCK 보호 선언

> **절대 규칙**: sot 2/6-2_Security-Governance/ 내 모든 파일은 아래 LOCK 값을 **재정의할 수 없다**.
> 참조 시 반드시 `> LOCK (출처): [원문 그대로]` 형식을 사용한다.

| # | LOCK 항목 | 정본 출처 | 값 |
|---|-----------|----------|-----|
| L1 | **OWASP LLM Top 10 목록** | Part2 §6.5.4 | LLM01~LLM10 (2025 버전, 10개 위험 고정) |
| L2 | **STRIDE 6대 위협 분류** | Part2 §6.5.3 | Spoofing/Tampering/Repudiation/Info Disclosure/DoS/Elevation |
| L3 | **HMAC 알고리즘** | Part2 §6.5.2 | HMAC-SHA256 (상수 시간 비교 필수) |
| L4 | **HMAC 키 최소 길이** | Part2 §6.5.2 | 32바이트 |
| L5 | **HMAC 키 순환 주기** | Part2 §6.5.2 | 90일 |
| L6 | **리플레이 방지 윈도우** | Part2 §6.5.2 | 5분(300초) |
| L7 | **Guardrails 3-Layer** | D2.0-07 §10 | L1 NeMo(입력) → L2 Guardrails AI(처리) → L3 LlamaGuard(출력) |
| L8 | **RBAC 4단계** | D2.0-07 §13 / Part2 §6.5 | OWNER/ADMIN/OPERATOR/VIEWER |
| L9 | **P2 승인 타임아웃** | D2.0-07 | 일반 10분 / HITL(P2) 5분 → Auto deny |
| L10 | **비용 상한** | D2.0-07 §4 | V1: ₩40,000 / V2: ₩93,000 / V3: ₩266,000 |
| L11 | **5-Gate System** | D2.0-07 §5 | Policy→Approval→Cost→Evidence→SelfCheck |
| L12 | **Docker 샌드박스 타임아웃** | Part2 §6.5.1 | 30초 + `--network=none` |
| L13 | **SQLCipher 암호화** | Part2 §6.5 | AES-256-CBC |
| L14 | **자율 운영 수준** | D2.0-07 §14 | L0~L3 (V1: L0~L1, V2: L2, V3: L3) |
| L15 | **Non-goal 절대 금지** | D2.0-07 §1 | 실거래/해킹/의료법률판단/개인정보장기저장/저작권위반/P2자동생성/위험자동실행 |
| L16 | **Rate Limiting** | Part2 §6.5 | 10 req/min 기본 |
| L17 | **Cost Gate 일일 한도** | D2.0-07 §4 / Part2 §6.5.3 | V2: ₩93,000 |
| L18 | **trace_id 생성** | Part2 §6.5.1 | 서버 측 UUID v4 전용 (클라이언트 신뢰 금지) |
| L19 | **DEC-003 도구 승인** | Part2 §6.5 | 읽기전용=자동, 외부API/쓰기/코드실행=확인 필요 |
| L20 | **NEVER_AUTO 정책** | D2.0-07 §3 / Part2 §6.5.3 | P1 이상 자동승인 금지, Gate 순서 강제 |

### 3.6 UPSTREAM_INHERITANCE — 3-4 Workflow-RPA Phase 4 ✅ Stage A + Stage B ALL COMPLETE (2026-05-24, implicit reference, [DOMAIN_PHASE_4_PRODUCTION_PROMOTION_COMPLETE:3-4] ✅) — Phase 4 완료 reference

> **3-4 Workflow-RPA Phase 4 완료 reference 추가** (Wave 1 #6, chain `phase4_3-4_2026-05-24`, verify-only per A direct path, 🎉 NO-DRIFT FULL 4/4 ⭐⭐⭐ milestone 확정 통산 4번째 FULL 도메인) — **6-2 Security-Governance 수신 측 implicit forward-defined inheritance** (Wave 2 #14 진입 대기). 본 도메인은 3-4 P4-3 enterprise_security V3 NEW의 보안 정책 inheritance reference 측 (implicit, P3-3 §1362 6-2 implicit + 1-1 VRE + 6-13 Operations).

| 항목 | inheritance 결과 |
|------|----------------|
| **3-4 P4-3 cross-handoff implicit inheritance** | 3-4 §7 P4-3 enterprise_security V3 NEW task의 §6 교차 도메인 "6-2 Security-Governance (implicit, 보안 정책 inheritance) + phase2_security_audit_report.md PHASE3_READY v2 baseline + 6-13 Operations + 1-1 VRE" 명시 — 본 6-2 도메인이 Phase 4 진입 시 양방향 정합 verify 예정 (3-4 발신 측 forward-defined direct path implicit, 6-2 P4 entry 시점 수신 측 LOCK-WF-10 + R-07-4/5/6 + RBAC 3계층 + SOC2/GDPR/ISO27001 정본 확정 inheritance) |
| **3-4 enterprise_security V3 산출물 명세** | enterprise_security V3 NEW + phase4_security_audit_report.md 신규 작성 = 2건 ALL **Status TODO 유지** (per A scope, V3 본문 + 보안 감사 보고서 OUT of scope α + β → SPEC Stage B 위임). LOCK-WF-10 verbatim + R-07-4/5/6 verbatim + phase2 §3.1 8항목 baseline inheritance ✅ verify |
| **3-4 RBAC 3계층 차원 차이 α-2 stale 명시** | 3-4 P3-3 §1379 "RBAC 3계층 (워크플로우/노드/데이터)" 보호 대상 차원 vs P4-3 §1652 "RBAC 3계층 (Admin/Operator/Auditor)" 권한 역할 차원 — design 의도 difference, V3 본문 작성 시 두 차원 조합 9 cells RBAC matrix 가능 (Stage B 위임). 6-2 도메인 보안 정책 inheritance 시점 정본 확정 |
| **3-4 SOC2/GDPR/ISO27001 컴플라이언스 매핑 inheritance** | 3-4 P4-3 §1652 "SOC2 Type II + GDPR Article 32 + ISO 27001" forward-defined — 6-2 보안 정책 도메인 implicit 보안 거버넌스 inheritance baseline |
| **3-4 production .md baseline EXACT 보존** | 5 baseline EXACT 보존 (plan + AUTHORITY v1.2 LOCK-WF-10 verbatim + CONFLICT v1.2 OPEN=0 + INDEX v1.1 42/42 + phase2 audit PHASE3_READY v2 ALL EXACT, production .md ZERO write 통산 per A) + 06_desktop-rpa _index.md EXACT — 6-2 도메인 영향 0건 inheritance |
| **3-4 R cascade 통산** | 468 verifications + 0 drift + 0 fix truly_converged_v1 first-pass-after-zero-fix CONFIRMED 4-consecutive — 6-2 수신 측 직접 영향 0건 (Phase 4 Stage A inheritance baseline EXACT) |
| **6-2 Phase 4 진입 시 수신 측 정합 verify** | 본 6-2 도메인 Wave 2 #14 ENTRY_PROMPT 진입 또는 Phase 4 SPEC Stage B 진입 시점 — LOCK-WF-10 8항목 + R-07-4/5/6 + RBAC matrix + 규제 준수 매핑 양방향 정본 verify (3-4 발신 측 forward-defined ↔ 6-2 수신 측 보안 거버넌스 inheritance) + phase2 §3.1 8항목 baseline 정합 verify |
| **abort marker** | `[CROSS_HANDOFF_DRIFT:6-2_P4_x]` NOT FIRED forward-defined (3-4 Phase 4 Stage A 발신 측 implicit 정합 baseline) |
| **marker** | `[DOWNSTREAM_INHERITANCE_FROM_3-4:6-2 — 2026-05-24]` ✅ implicit (3-4 Phase 4 Stage A 완료 ⑥단계 downstream propagation, 6-2 P4 entry 시점 양방향 verify 예정) |

---

## 4. 거버넌스 규칙

### 4.1 공통 규칙 (R1~R11)

> **글로벌 거버넌스 규칙**: 본 도메인은 0-0_Governance-Rules-Meta에서 정의한 R1~R11 글로벌 규칙을 전체 준수합니다.
>
> 상세: `0-0_Governance-Rules-Meta/01_common-rules/_index.md` 참조.

### 4.2 Tier 6 공통 규칙

| 규칙 ID | 규칙 | 근거 |
|---------|------|------|
| **R-T6-1** | Part2 §6.x 원문과 SOT2 상세가 충돌 시 **Part2 원문 우선** | GUIDE §4.6 |
| **R-T6-2** | 횡단 관심사 도메인(6-2, 6-12, 6-13)은 소비 도메인 목록 유지 필수 | GUIDE §4.6 |
| **R-T6-3** | Part2 업데이트 시 해당 Tier 6 도메인 STALE 체크 필수 | INTEGRATION_PLAN §9 |

### 4.3 Security-Governance 전용 규칙

| 규칙 ID | 규칙 | 근거 |
|---------|------|------|
| **R-62-1** | 보안 체크리스트 갱신 시 **전 도메인 통보** — 소비 도메인 12개에 변경 사항 전파 필수 | INTEGRATION_PLAN §7.5 횡단 매트릭스 |
| **R-62-2** | OWASP LLM Top 10 매핑 변경 시 Part2 §6.5.4 동기 갱신 필수 | Part2 §6.5.4 LOCK |
| **R-62-3** | STRIDE 위협 모델에 새 위협 시나리오 추가 시 CONFLICT_LOG 기록 + D2.0-07 §2.2A 참조 확인 | D2.0-07 §2.2A |
| **R-62-4** | HMAC 구현 패턴 변경 금지 — `hmac.compare_digest()` / `crypto.timingSafeEqual()` 외 비교 방법 사용 불가 | Part2 §6.5.2 LOCK |
| **R-62-5** | 보안 항목 15건 목록 삭제 금지 — 추가만 허용 | Part2 §6.5 |
| **R-62-6** | AI 코드 생성 보안 체크리스트 7개 항목은 모든 코드 생성 세션에서 의무 적용 | Part2 §6.5.1 |
| **R-62-7** | Guardrails 3-Layer 순서 변경 금지 (L1 입력 → L2 처리 → L3 출력) | D2.0-07 §10 |
| **R-62-8** | 보안 감사 이벤트는 `security.*` 네임스페이스로 6-12(Event-Logging)에 발행 | 6-12 연동 |
| **R-62-9** | 연 1회 이상 OWASP LLM Top 10 최신판 대비 VAMOS 매핑 재검토 | STEP7-E S7E-003 |
| **R-62-10** | 외부 보안 표준(STRIDE, OWASP) 변경 시 본 도메인 STALE 플래그 발행 + 30일 이내 갱신 | STEP7-E S7E-001 |

---

## 5. 선행작업

### 5.1 Part2 §6.5 완전 읽기 + D2.0-07 대조 (완료)

- **목적**: Part2 FULL 영역과 D2.0-07 정본 간 불일치 확인
- **결과**: Part2 §6.5는 D2.0-07에서 파생. 15개 보안 항목, STRIDE 6대 위협, OWASP LLM 10개 위험 일치 확인. Guardrails 3-Layer 구조 동일.
- **상태**: ✅ 완료

### 5.2 기존 관련 도메인과 중복 범위 확인 (완료)

- **0-0 Governance**: R1~R11, LOCK/FREEZE 레지스트리 → 6-2는 보안 실행 정책만 관할
- **4-2 CI/CD**: 보안 스캔 실행 → 6-2는 스캔 정책/기준 정의만
- **4-3 MCP**: MCP 구현 → 6-2는 MCP 보안 요구사항만
- **경계**: 6-2 = 보안 정책 정의 + 체크리스트 + 위협 모델 / 소비 도메인 = 정책에 따른 구현
- **상태**: ✅ 완료

### 5.3 STEP7-E 92건 항목 분류 (완료)

- **목적**: 92건 보안 보강 항목을 4개 서브폴더로 매핑
- **결과**: Part 1~10 × 항목별로 01~04 서브폴더 + 소비 도메인 배정 완료
- **상태**: ✅ 완료

---

## 6. 이슈 해결 매핑

> **[1-2 Auxiliary-Modules Phase 3 완료 — 2026-05-14]** (downstream reference, P3-1~P3-6 6/6 ALL ✅ tcv3): 1-2 도메인 Phase 3 완료에 따른 본 도메인 inheritance 가능 자원 — P3-3 V-14 ResponseEnvelope (`00_common/response_envelope.md` v2, LOCK-AX-11) + PII 마스킹 정합 verify 결과 + ResponseEnvelope 표준 필드 (`audit.failure_codes` / `fallback_ids` / `event_ids`) + AUX-Exxx 에러 분류 체계 (`00_common/error_taxonomy.md`). 본 도메인 PII 마스킹 정책 적용 시 보조 모듈 응답 envelope 정합 보장. Wave 2 #14 진입 시 본 reference inheritance 처리 예정. (출처: `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\AUXILIARY_MODULES_구조화_종합계획서.md` §7 Phase 3, post 192,270 B / 293E2A16CFB5BE74)

| # | 이슈 | 현재 상태 | 해결 방안 | 대상 서브폴더 |
|---|------|----------|----------|------------|
| 1 | D2.0-07 §10 Guardrails 3-Layer와 Part2 §6.5 15개 항목 간 매핑 | ✅ 완료 | 부록 §C에 Guardrails 3×15 교차 참조 매트릭스 등록 완료 | 01_ai-code-security |
| 2 | STEP7-E 92건 중 Part2 §6.5 미반영 항목 | 미매핑 | 서브폴더별 매핑 + 우선순위 배정 | 01~04 전체 |
| 3 | OWASP LLM Top 10 (2025) 버전 고정 vs 향후 업데이트 | 고정 | L1 LOCK으로 2025 버전 고정 + 연 1회 재검토 규칙(R-62-9) | 04_owasp-llm-top10 |
| 4 | STRIDE 매핑이 9-State 파이프라인에만 한정 | 한정적 | MCP, Agent 통신, RAG 파이프라인까지 확장 매핑 | 03_stride-threat-model |
| 5 | HMAC 키 순환 grace period(24h) 운영 절차 미문서화 | ✅ 완료 | 부록 §D에 HMAC 키 운영 절차 매트릭스 등록 완료, 02_hmac-timing-defense 서브폴더 반영 예정 | 02_hmac-timing-defense |
| 6 | 소비 도메인 12개의 §9에서 본 보안 체크리스트 참조 체계 | 미구축 | 부록 A 소비 도메인 매트릭스 작성 + 각 도메인 §9에 참조 포인터 | 전체 |
| 7 | AI 코드 생성 체크리스트 7항목과 CI/CD(4-2) 자동화 연결 | 미연결 | 4-2 CI/CD 도메인의 03_security-scanning 서브폴더와 교차 참조 | 01_ai-code-security |

### 6.X 1-2 Auxiliary-Modules Phase 4 ✅ 완료 inheritance (2026-05-23, downstream 전파)

> **1-2 Phase 4 ✅ 완료 (2026-05-23, 6/6 P4 task ALL ✅)** — 본 도메인 Wave 2 #14 진입 시 inheritance 활용 가능 산출물:
> - **V-14 ResponseEnvelope + 6-2 PII 마스킹 정합 영구 baseline**: 1-2 V2 13 CONDITIONAL → PASS 승급 결과 (P4-2 inheritance), 모든 V2 module에 E7 Security 영구 보강 section 추가 (PII 마스킹 정책 cross-ref to `6-2/01_ai-code-security/pii_regex_masking.md` + RBAC 3-tier + audit log via 6-12 Event-Logging LOCK-EL-01~10)
> - **6-2 cross-handoff**: 1-2 V2 13 파일 (00_common 3 + I-4 7 + I-16 2 + S-1 1)에 E7 Security 영구 baseline section 영구 추가 → 본 도메인 §7 Phase 4 진입 시 PII regex 패턴 cross-validation + RBAC 권한 매트릭스 detail + audit log 6-12 cross-handoff verify 필요 (~2026-06-09 closure tracking)
> - **STAGE 9 STEP_C inheritance**: 1-2 PII 31 V2 / 244 raw refs 광범위 sync inheritance (변경 0)
> - **Phase 4 P4-2 chain**: `phase4_1-2_p4-2_2026-05-23` → 본 도메인 §7 Phase 4 V-14 cross-handoff inheritance ✅
> - **1-2 산출물**: `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\_verification\phase4_conditional_closure_report.md` (E7 Security 영구 baseline 매트릭스 §4.2)
> - **상위 SoT**: `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\AUXILIARY_MODULES_구조화_종합계획서.md` §7 Phase 4 P4-2 + SOT2_MASTER_INDEX 1-2 row [PHASE5_READY: 1-2 — 2026-05-23]

### 6.Y 6-1 UI-UX-System Phase 4 ✅ Stage A 완료 inheritance (2026-05-26, downstream 전파)

> **[PHASE4_COMPLETE_STAGE_A: 6-1 — 2026-05-26]** ⬛ (downstream reference, P4-1~P4-4 4/4 ALL ✅ NO-DRIFT FULL milestone first specialty 확정): 6-1 도메인 Phase 4 Stage A 완료에 따른 본 도메인 inheritance 자원 — **🌟 6-2 Security-Governance (Wave 2 #14 forward-defined) ↔ 6-1 P4-1+P4-3+P4-4 RBAC + PII + Docker 샌드박스 cross-handoff** (3 P4 task distinct coverage forward-defined: P4-1 모바일 RBAC L10 4단계 OWNER/ADMIN/OPERATOR/VIEWER + Part2 §6.5 보안 체크리스트 + P4-3 아바타 RBAC 4 × 5 = 20 cell + 디지털 휴먼 대화 PII 마스킹 + P4-4 Plugin Slot RBAC 4 × 4 = 16 cell + 화이트리스트 + Docker 샌드박스 LOCK L12 Part2 §6.5.1 D8-L03 패턴 직계 inheritance) + **🌟 4 슬롯 (HeaderSlot + SidebarSlot + ContentSlot + FooterSlot) Plugin SDK 통합 시 Plugin 화이트리스트 + Docker 샌드박스 격리 정책 forward-defined** + **🌟 통산 RBAC 매트릭스 36 cell coverage** (20 + 16 = 36 cell, 4 역할 × 9 컴포넌트/슬롯/UI). 6-1 V3 산출물 5 NEW + 3 UPDATE forward-defined (OUT of scope per 사용자 결정 A verify-only inheritance, SPEC Stage B 또는 별도 결정 위임). **Wave 2 #14 본 도메인 Phase 4 진입 시 본 inheritance reference 처리 예정** — 6-1 P4-1 모바일 RBAC L10 + P4-3 아바타 PII 마스킹 + P4-4 Plugin 화이트리스트/Docker 샌드박스 LOCK L12 양방향 baseline 확립 + 6-2 자체 §3.4 LOCK matrix에 본 inheritance reference 통합 + V3 RBAC 매트릭스 36 cell SPEC Stage B 위임 + 6-1 V3 production .md 정본 승급 시 6-2 보안 체크리스트 cross-validation. (출처: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\UI_UX_SYSTEM_구조화_종합계획서.md` §7 Phase 4, post 236,927 B / `E39161CFBFEFC36D` Stage A baseline EXACT 보존 + ④ 세션 요약 블록 +Δ 별도)

---

## 7. Phase 실행 계획

### 7.1 V-Phase 정렬

| SOT2 Phase | Part2 대응 | 내용 | 산출물 |
|-----------|-----------|------|--------|
| **Phase 0** | — | 분석 + 구조화 (본 계획서) | 계획서, AUTHORITY_CHAIN, 서브폴더 |
| **Phase 1** ✅ | V1 (15개 보안 항목 중 V1 해당 12건) | 핵심 보안 구현: 코드 보안 체크리스트, 입력 검증, RBAC, API Key 관리, Docker 샌드박스, 승인 타임아웃 — **완료 (12/12, 2026-04-12)** | 서브폴더별 L3 상세 파일 |
| **Phase 2** ✅ | V2 (HMAC, LlamaGuard, GDPR, Zero-Trust) | 보안 확장: HMAC-SHA256 Agent 인증, LlamaGuard 통합, GDPR 준수, Zero-Trust 아키텍처 — **완료 (5/5, 2026-04-26, STAGE 7 STEP_B)** | L3 업그레이드 (V2 NEW 5 / 1,752 L) |
| **Phase 3** | V3 (자체 학습 탐지, Model Theft 방어) | 고급 보안: ML 기반 이상탐지, Red Team 자동화, 자체 보안 테스트 파이프라인 | 최종 L3 완성 |

### 7.2 Phase 전환 게이트

| 전환 | 게이트 조건 |
|------|-----------|
| P0→P1 | 본 계획서 APPROVED + AUTHORITY_CHAIN 작성 + CONFLICT_LOG 초기화 + 4개 서브폴더 _index.md 완료 |
| P1→P2 | V1 보안 항목 12건 구현 완료 + AI 코드 보안 체크리스트 CI/CD 통합 + STRIDE 기본 매핑 검증 |
| P2→P3 ✅ | HMAC 운영 절차 확정 ✅ + LlamaGuard 통합 ✅ + GDPR 대응 완료 ✅ + OWASP 매핑 재검토 ✅ — **전체 PASS (2026-04-26)** |

#### Phase 0 세부 태스크

<details>
<summary><b>P0-1. AUTHORITY_CHAIN.md 작성</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` (LOCK 6건 단독 출처 + 3건 복합 출처)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.5 (LOCK 11건 단독 출처 + 3건 복합 출처)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\SECURITY_GOVERNANCE_구조화_종합계획서.md` §3.1~§3.5

**절차**:
1. 본 계획서 §3.1~§3.5 권한 체계 전체 읽기 (§3.1 기존 체인 → §3.2 확장 체인 → §3.3 권한 범위 → §3.4 도메인 경계 → §3.5 LOCK 선언)
2. 본 계획서 §3.5 LOCK 테이블(L1~L20) 기반으로, 각 항목의 정본 출처(D2.0-07 또는 Part2 §6.5)에서 원문 값 추출
3. AUTHORITY_CHAIN.md 신규 생성:
   - 권한 체인 계층 (§3.1 기존 + §3.2 확장)
   - 각 문서의 권한 범위 테이블 (§3.3)
   - 도메인 경계 명시 6건 (§3.4)
   - LOCK 20건 레지스트리: 항목명, 정본 출처 섹션, LOCK 값 — §3.5 형식 준수 (`> LOCK (출처): [원문 그대로]`)
4. D2.0-07 원본과 LOCK 값 교차 검증 (단독: L7, L9, L10, L11, L14, L15 / 복합의 D2.0-07 측: L8, L17, L20)
5. Part2 §6.5 원본과 LOCK 값 교차 검증 (단독: L1~L6, L12, L13, L16, L18, L19 / 복합의 Part2 측: L8, L17, L20)

**검증**:
- [x] G0-2: AUTHORITY_CHAIN.md에 LOCK 20건(L1~L20) 전체 포함 ✅ (2026-04-03)
- [x] 각 LOCK 값이 정본 출처(D2.0-07 또는 Part2 §6.5) 원본과 일치 ✅ (2026-04-03)
- [x] 각 LOCK 항목에 정본 출처 섹션 번호가 명시됨 (§10 #2 충족) ✅ (2026-04-03)
- [x] §3.3 권한 범위 테이블(4개 문서) 포함 ✅ (2026-04-03)
- [x] §3.4 도메인 경계(6건) 포함 ✅ (2026-04-03)
- [x] LOCK 참조 형식이 §3.5 절대 규칙(`> LOCK (출처): [원문 그대로]`) 준수 ✅ (2026-04-03)

**산출물**: `D:\VAMOS\docs\sot 2\6-2_Security-Governance\AUTHORITY_CHAIN.md` — **v1.1 완료**

**완료 이력**:
- v1.0 (2026-03-24 S6-3): 초기 작성 — §1~§4 + Tier 6 규칙
- v1.1 (2026-04-03): §5 LOCK 상세 원문 레지스트리 추가, D2.0-07 9건 + Part2 §6.5 14건 교차 검증 완료, L9 "Auto reject"→"Auto deny" 원문 반영, §2 "← 본 도메인" 마커 추가
</details>

<details>
<summary><b>P0-2. CONFLICT_LOG.md 초기화</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\SECURITY_GOVERNANCE_구조화_종합계획서.md` §9.1 (Tier 6 공통 프로토콜: 충돌 유형 4건 + 해결 방법) + §9.2 (Security-Governance 고유 시나리오 4건)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\SECURITY_GOVERNANCE_구조화_종합계획서.md` §4.3 R-62-3 (STRIDE 변경 시 CONFLICT_LOG 기록 규칙)

**절차**:
1. 본 계획서 §9.1 공통 프로토콜(충돌 유형 4건 + 해결 방법) + §9.2 고유 시나리오(4건 + 해결) 전체 읽기
2. 본 계획서 §4.3 R-62-3 확인: STRIDE 위협 시나리오 추가 시 CONFLICT_LOG 기록 의무
3. CONFLICT_LOG.md 신규 생성:
   - **충돌 해결 프로토콜 발췌**: §9.1 공통 4유형 + §9.2 고유 4시나리오 + 해결 우선순위 원칙(Part2 원문 우선 / 6-2 보안 체크리스트 우선 / D2.0-07 LOCK 우선 등) 포함
   - **로그 테이블 템플릿**: ID, 발견일, 충돌 유형(§9.1 분류 기준: Part2↔SOT2 / Tier6 중복 / 횡단 관심사 / 기존 도메인), 출처A↔출처B, 충돌 내용, 적용 해결 원칙(§9.1 해결 방법 참조), 해결 결과, 상태
   - **소비 도메인 예외 기록 섹션**: 부록 A 기반, 소비 도메인의 보안 체크리스트 예외 요청 시 기록 용도 (§9.1 횡단 관심사 충돌 + §9.2 예외 요청 시나리오 연동)
4. 초기 항목 없이 빈 로그로 초기화

**검증**:
- [x] G0-4: CONFLICT_LOG.md 파일 존재 ✅ (2026-04-03)
- [x] 로그 테이블에 §9.1 충돌 유형 4건 분류 체계가 컬럼으로 반영됨 ✅ (2026-04-03)
- [x] §9.1/§9.2 해결 우선순위 원칙(Part2 원문 우선, 6-2 보안 체크리스트 우선, D2.0-07 LOCK 우선) 발췌 포함 ✅ (2026-04-03)
- [x] R-62-3 STRIDE 변경 기록 + 소비 도메인 예외 기록을 수용 가능한 구조 ✅ (2026-04-03)

**산출물**: `D:\VAMOS\docs\sot 2\6-2_Security-Governance\CONFLICT_LOG.md` — **v2.0 완료**

**완료 이력**:
- v1.0 (2026-03-24 S6-3): 초기 작성 — 기본 충돌 기록 테이블 + 프로토콜 요약 5줄 + 잠재 충돌 W-1~W-3
- v2.0 (2026-04-03): P0-2 프롬프트 기준 전면 보강 — §1 프로토콜 발췌(§9.1 공통 4유형 테이블 + §9.2 고유 4시나리오 테이블 + 우선순위 원칙 4단계 + 기록 트리거 7건(R-62-3 §2.2A 포함)), §2 충돌 로그(8컬럼 + 4분류 체계), §3 소비 도메인 예외 기록(R-62-1 통보 + 12개 도메인), §4 잠재 모니터링(W-1~W-3 보존)
</details>

<details>
<summary><b>P0-3. 01_ai-code-security/_index.md 작성</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` §10.1(NeMo Guardrails L1), §10.2(Guardrails AI L2), §10.3(LlamaGuard L3), §15.4(컴플라이언스/감사 로깅 — §15.4.2 GDPR 데이터 보호 포함)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.5.1(AI 코드 생성 보안 체크리스트 7항목) + §6.5 15개 보안 항목 중 #1(NeMo), #2(Guardrails AI), #4(PII), #8(Docker), #12(입력 검증)
- `D:\VAMOS\docs\sot\STEP7-E_보안_안전_거버넌스_작업가이드.md` Part 2(S7E-011~020 Prompt Injection), Part 4(S7E-031~040 데이터 프라이버시), Part 9(S7E-077~084 Agent 보안) — 총 28건
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\SECURITY_GOVERNANCE_구조화_종합계획서.md` §7.3(Phase 1 세부 항목 #1~#5, #7), 부록 §B(STEP7-E 92건 매핑 요약), 부록 §C(Guardrails 3-Layer × 15항목 교차 참조)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\AUTHORITY_CHAIN.md` §5 LOCK 레지스트리(L7, L12, L18 교차 검증용)

**절차**:
1. D2.0-07 §10.1(NeMo Guardrails L1 입력 검사), §10.2(Guardrails AI L2 처리 중 검사), §10.3(LlamaGuard L3 출력 검사), §15.4.2(GDPR 데이터 보호 — PII 처리 근거) 읽기
2. Part2 §6.5.1 AI 코드 생성 보안 체크리스트 7항목 전체 읽기 + §6.5 15개 보안 항목 목록에서 01_ai-code-security 해당 항목(#1 NeMo, #2 Guardrails AI, #4 PII, #8 Docker, #12 입력 검증) 추출
3. 본 계획서 부록 §B에서 01_ai-code-security 매핑 항목 확인: Part 2(S7E-011~020), Part 4(S7E-031~040), Part 9(S7E-077~084) — 총 28건
4. STEP7-E 원본에서 28건 개별 항목의 ID, 제목, 우선순위(CRITICAL/HIGH/MED) 직접 추출
5. 본 계획서 부록 §C Guardrails 3-Layer × 15항목 교차 참조 매트릭스에서 01_ai-code-security 관련 행 추출 (L1/L2/L3 커버리지 확인)
6. 본 계획서 §7.3에서 01_ai-code-security 배정 항목 확인: #1(체크리스트 7항목), #2(입력 검증), #3(NeMo L1), #4(Guardrails AI L2), #5(PII), #7(Docker)
7. _index.md 신규 생성:
   - **A.** AI 코드 생성 보안 체크리스트 7개 검증 항목 (Part2 §6.5.1 기반, 적용 시점 + STEP7-E 참조)
   - **B.** 보안 항목 15건 전체 목록 (Part2 §6.5 기반, 서브폴더 매핑 명시: 본 폴더/02_hmac/03_stride/04_owasp)
   - **C.** Guardrails 3-Layer 매핑 (부록 §C 기반, L7 LOCK 원문 인용, Layer별 역할·체크리스트 연결)
   - **D.** STEP7-E 매핑 현황 28건 (ID, 제목, 우선순위, 버전, 상태)
   - **E.** LOCK 참조 테이블: L7(Guardrails 3-Layer), L12(Docker 30초 + --network=none), L18(trace_id UUID v4) — `> LOCK (출처): [원문 그대로]` 형식
   - **F.** Phase 배정 (§7.3 기준 V1/V2/V3)
   - **G.** L3 작성 현황 (미작성 항목 + Phase 대상 표기)
   - **H.** 소비 도메인 참조 (R-62-6 의무 적용 대상 도메인 목록)
8. LOCK 교차 검증: L7, L12, L18 값을 AUTHORITY_CHAIN.md §5 + D2.0-07 원본과 대조
9. §6 이슈 반영 확인: #1(Guardrails 3×15 교차 참조 — 부록 §C 연동 상태), #7(CI/CD 4-2 교차 참조 포인터 포함 여부)

**검증**:
- [x] G0-3: 01_ai-code-security/_index.md 존재 + 비어있지 않음 ✅ (2026-04-04)
- [x] LOCK 참조 값(L7, L12, L18)이 D2.0-07 원본 및 AUTHORITY_CHAIN.md와 일치 ✅ (2026-04-04)
- [x] LOCK 참조 형식이 §3.5 절대 규칙(`> LOCK (출처): [원문 그대로]`) 준수 ✅ (2026-04-04)
- [x] Part2 §6.5.1 체크리스트 7항목 전부 포함 ✅ (2026-04-04)
- [x] STEP7-E 28건(Part 2/4/9) 매핑이 ID·제목·우선순위와 함께 반영 ✅ (2026-04-04)
- [x] Phase 배정(V1/V2/V3)이 §7.3 및 §6.5 버전과 일치 ✅ (2026-04-04)
- [x] R-62-6(체크리스트 7항목 의무 적용), R-62-7(Guardrails 3-Layer 순서 불변) 규칙 반영 확인 ✅ (2026-04-04)

**산출물**: `D:\VAMOS\docs\sot 2\6-2_Security-Governance\01_ai-code-security\_index.md` — **v2.0 완료**

**완료 이력**:
- v1.0 (2026-03-24 S6-3): 초기 작성 — A~D 섹션 + 15건 목록 + STEP7-E 그룹 매핑
- v2.0 (2026-04-04): P0-3 프롬프트 기준 전면 보강 — §A R-62-6 규칙 ID 명시, §B #14 D2.0-07 §15.4.2 출처 추가, §C R-62-7 순서 불변 명시, §D STEP7-E 28건 개별 분리(Part 2: 10건 + Part 4: 10건 + Part 9: 8건 + 교차 참조 3건), §E LOCK 참조 테이블 신설(L7/L12/L18 정식 `> LOCK` 형식), §F Phase 배정 신설(§7.3 기준), §G L3 작성 현황 Phase 대상 추가, §H 소비 도메인 R-62-6 명시 + 이슈 #7 교차 참조
</details>

<details>
<summary><b>P0-4. 02_hmac-timing-defense/_index.md 작성</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.5.2(HMAC 타이밍 공격 방어 — 상수 시간 비교, 키 길이, 순환, 리플레이 방지, 에러 응답 균일화) + §6.5 15개 보안 항목 중 #10(SQLCipher), #11(API Key), #13(HMAC-SHA256)
- `D:\VAMOS\docs\sot\D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` S7E-032(SQLCipher AES-256-CBC), S7E-078(Agent HMAC 무결성 검증) — LOCK 교차 검증 보조
- `D:\VAMOS\docs\sot\STEP7-E_보안_안전_거버넌스_작업가이드.md` Part 8(S7E-069~076 인시던트 대응) — 8건 (HIGH 4건, MED 4건)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\SECURITY_GOVERNANCE_구조화_종합계획서.md` §7.3(Phase 1 세부 항목 #9, #10), 부록 §B(STEP7-E 매핑 요약), 부록 §D(HMAC 키 운영 절차 매트릭스 — D.1 라이프사이클 7단계, D.2 Grace Period 상세, D.3 실패 시나리오)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\AUTHORITY_CHAIN.md` §5 LOCK 레지스트리(L3~L6, L13 교차 검증용)

**절차**:
1. Part2 §6.5.2 HMAC 타이밍 공격 방어 전체 읽기 (상수 시간 비교, 키 최소 길이 32바이트, 순환 주기 90일, 리플레이 방지 5분, 에러 응답 균일화) + §6.5 #10(SQLCipher AES-256-CBC), #11(API Key .env+dotenv), #13(HMAC-SHA256 Agent 인증) 추출
2. 본 계획서 부록 §B에서 02_hmac-timing-defense 매핑 항목 확인: Part 8(S7E-069~076 인시던트 대응) — 8건
3. STEP7-E 원본에서 8건(S7E-069~076) 개별 항목의 ID, 제목, 우선순위(HIGH/MED), 버전(V1/V2) 직접 추출
4. 본 계획서 부록 §D HMAC 키 운영 절차 매트릭스 읽기: D.1(라이프사이클 7단계), D.2(Grace Period 24h 상세), D.3(실패 시나리오 및 롤백) — 참고: D.1 4단계 "R-62-6" 참조는 §4.3 R-62-6(AI 코드 보안 체크리스트)과 불일치, 키 순환 근거는 L5(90일) 기준 적용
5. 본 계획서 §7.3에서 02_hmac-timing-defense 배정 항목 확인: #9(SQLCipher AES-256), #10(API Key 관리) — §6.5 #13(HMAC-SHA256)은 V2/Phase 2 대상이므로 참조만 포함
6. _index.md 신규 생성:
   - **A.** HMAC 타이밍 공격 방어 항목 (Part2 §6.5.2 기반, 5개 방어 항목 + 구현 패턴)
   - **B.** 참조 구현 패턴 (Python: `hmac.compare_digest()`, Node.js: `crypto.timingSafeEqual()` — R-62-4 필수)
   - **C.** 키 관리 라이프사이클 (부록 §D 기반, 7단계 + Grace Period 24h)
   - **D.** 암호화 인프라 (SQLCipher AES-256-CBC, API Key 관리)
   - **E.** STEP7-E 매핑 현황 (Part 8: 8건 + §7.3 위임 항목)
   - **F.** LOCK 참조 테이블: L3(HMAC-SHA256), L4(키 32바이트), L5(순환 90일), L6(리플레이 5분), L13(SQLCipher AES-256-CBC) — `> LOCK (출처): [원문 그대로]` 형식
   - **G.** Phase 배정 (§7.3 기준: #9·#10 → V1/Phase 1, §6.5 #13 HMAC-SHA256 → V2/Phase 2 예고)
   - **H.** L3 작성 현황 (미작성 항목 + Phase 대상 표기)
7. LOCK 교차 검증: L3~L6 값을 Part2 §6.5.2 원본, L13 값을 Part2 §6.5 원본, 전체를 AUTHORITY_CHAIN.md §5와 대조 + D2.0-07 S7E-032(SQLCipher)/S7E-078(HMAC) 보조 대조
8. §6 이슈 반영 확인: #5(HMAC 키 순환 grace period — 부록 §D 연동 상태)

**검증**:
- [x] G0-3: 02_hmac-timing-defense/_index.md 존재 + 비어있지 않음 ✅ (2026-04-04)
- [x] LOCK 참조 값(L3~L6, L13)이 Part2 §6.5.2/§6.5 원본 및 AUTHORITY_CHAIN.md와 일치 ✅ (2026-04-04)
- [x] LOCK 참조 형식이 §3.5 절대 규칙(`> LOCK (출처): [원문 그대로]`) 준수 ✅ (2026-04-04)
- [x] Part2 §6.5.2 HMAC 방어 항목 전부 포함 (상수 시간 비교, 키 길이, 순환, 리플레이, 에러 균일화) ✅ (2026-04-04)
- [x] STEP7-E 8건(Part 8) 매핑이 ID·제목·우선순위·버전과 함께 반영 ✅ (2026-04-04)
- [x] 부록 §D 키 운영 절차(라이프사이클 7단계 + Grace Period + 실패 시나리오) 반영 ✅ (2026-04-04)
- [x] R-62-4(HMAC 구현 패턴 변경 금지 — compare_digest/timingSafeEqual 전용) 규칙 반영 확인 ✅ (2026-04-04)
- [x] Phase 배정에서 §7.3 #9·#10이 V1/Phase 1, §6.5 #13(HMAC-SHA256)이 V2/Phase 2로 정확히 분류 ✅ (2026-04-04)
- [x] D2.0-07 S7E-032(SQLCipher)/S7E-078(HMAC) 보조 교차 검증 완료 ✅ (2026-04-04)

**산출물**: `D:\VAMOS\docs\sot 2\6-2_Security-Governance\02_hmac-timing-defense\_index.md` — **v2.0 완료**

**완료 이력**:
- v1.0 (2026-03-24 S6-3): 초기 작성 — A~C 섹션 + STEP7-E 그룹 매핑 + L3 작성 현황
- v2.0 (2026-04-04): P0-4 프롬프트 기준 전면 보강 — §A Part2 §6.5.2 5개 방어 항목 LOCK 매핑(L3~L6), §B R-62-4 규칙 명시 + Python/Node.js 정본 패턴, §C 부록 §D 기반 7단계 라이프사이클(Grace Period 24h + 실패 시나리오 4건 + R-62-6 참조 오류 경고), §D TLS 1.3 제거 + SQLCipher L13 + API Key S7E-005, §E STEP7-E Part 8 8건 개별 분리(ID·제목·우선순위·버전) + §7.3 위임 항목(#9·#10), §F LOCK 참조 테이블 신설(L3~L6·L13 정식 `> LOCK` 형식, AUTHORITY_CHAIN §5 원문 대조), §G Phase 배정 명확화(#9·#10→V1, #13→V2 예고), §H L3 작성 현황 Phase 대상 추가, D2.0-07 S7E-032/S7E-078 보조 교차 검증 완료
</details>

<details>
<summary><b>P0-5. 03_stride-threat-model/_index.md 작성</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` §2.2A(STRIDE/Attack Tree/OWASP 통합), §3(승인 정책 — §3.1 타임아웃 + NEVER_AUTO), §5(5-Gate System), §13(RBAC 접근 제어), §14(자율 운영 수준 L0~L3)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.5.3(STRIDE 위협 모델 매핑) + §6.5 15개 보안 항목 중 #5(RBAC), #6(Autonomy — L14 참조), #7(P2 세션 승인 — L9 참조), #9(승인 타임아웃), #15(DEC-003)
- `D:\VAMOS\docs\sot\STEP7-E_보안_안전_거버넌스_작업가이드.md` Part 1(S7E-001~010 위협 모델링), Part 3(S7E-021~030 인증/권한/접근제어), Part 7(S7E-061~068 모니터링/감사/로깅) — 총 28건
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\SECURITY_GOVERNANCE_구조화_종합계획서.md` §7.3(Phase 1 세부 항목 #6, #8, #11, #12), 부록 §A(소비 도메인 매트릭스), 부록 §B(STEP7-E 매핑 요약)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\AUTHORITY_CHAIN.md` §5 LOCK 레지스트리(L2, L8, L9, L11, L14, L19, L20 교차 검증용)

**절차**:
1. D2.0-07 §2.2A(STRIDE/Attack Tree/OWASP 통합 매핑), §3(승인 정책 — §3.1 타임아웃 + NEVER_AUTO), §5(5-Gate System), §13(RBAC 4레벨 접근 제어), §14(자율 운영 수준 L0~L3) 읽기
2. Part2 §6.5.3 STRIDE 위협 모델 매핑 전체 읽기 + §6.5 15개 보안 항목 중 03_stride-threat-model 해당 항목(#5 RBAC, #6 Autonomy(L14 참조), #7 P2 세션 승인(L9 참조), #9 승인 타임아웃, #15 DEC-003) 추출 — 참고: #6·#7은 §7.3 Phase 1 미배정이나, 섹션 C(인증/인가/접근제어) 콘텐츠 + L9·L14 LOCK 참조에 필요
3. 본 계획서 부록 §B에서 03_stride-threat-model 매핑 항목 확인: Part 1(S7E-001~010), Part 3(S7E-021~030), Part 7(S7E-061~068) — 총 28건
4. STEP7-E 원본에서 28건 개별 항목의 ID, 제목, 우선순위(CRITICAL/HIGH/MED), 버전(V1/V2/V3) 직접 추출
5. 본 계획서 §7.3에서 03_stride-threat-model 배정 항목 확인: #6(RBAC 4레벨), #8(승인 타임아웃), #11(DEC-003), #12(STRIDE 기본 매핑)
6. _index.md 신규 생성:
   - **A.** STRIDE 6대 위협 매핑 (Part2 §6.5.3 기반, 위협별 대응 통제 명시)
   - **B.** 확장 공격 표면 (LLM API, 로컬 저장소, MCP 도구, Agent 간 통신, 프롬프트 인젝션, RAG 파이프라인, 외부 데이터)
   - **C.** 인증/인가/접근제어 (RBAC 4레벨, 로컬 인증, OAuth2, 도구 실행 권한, 세션 관리, Zero-Trust, 감사 추적)
   - **D.** Attack Tree (D2.0-07 §2.2A 기반)
   - **E.** STEP7-E 매핑 현황 28건 (ID, 제목, 우선순위, 버전, 상태)
   - **F.** LOCK 참조 테이블: L2(STRIDE 6대 위협), L8(RBAC 4단계), L9(P2 승인 타임아웃), L11(5-Gate System), L14(자율 운영 수준 L0~L3), L19(DEC-003), L20(NEVER_AUTO) — `> LOCK (출처): [원문 그대로]` 형식
   - **G.** Phase 배정 (§7.3 기준 V1/V2/V3)
   - **H.** L3 작성 현황 (미작성 항목 + Phase 대상 표기)
   - **I.** 소비 도메인 참조 (부록 §A 기반, STRIDE 위협 모델 소비 도메인 목록 — R-62-3 변경 시 CONFLICT_LOG 기록 + 통보 대상)
7. LOCK 교차 검증: L2, L8, L9, L11, L14, L19, L20 값을 AUTHORITY_CHAIN.md §5 + D2.0-07/Part2 원본과 대조 — 특히 L11(§5), L14(§14), L20(§3) 원문 대조 시 입력 파일에 명시된 D2.0-07 섹션 직접 참조
8. §6 이슈 반영 확인: #4(STRIDE 매핑 확장 — MCP, Agent 통신, RAG 파이프라인 포함 여부)

**검증**:
- [x] G0-3: 03_stride-threat-model/_index.md 존재 + 비어있지 않음 ✅ (2026-04-04)
- [x] LOCK 참조 값(L2, L8, L9, L11, L14, L19, L20)이 D2.0-07/Part2 원본 및 AUTHORITY_CHAIN.md와 일치 ✅ (2026-04-04)
- [x] LOCK 참조 형식이 §3.5 절대 규칙(`> LOCK (출처): [원문 그대로]`) 준수 ✅ (2026-04-04)
- [x] STRIDE 6대 위협 전부 대응 통제 명시 (§10 검증 #6 충족) ✅ (2026-04-04)
- [x] STEP7-E 28건(Part 1/3/7) 매핑이 ID·제목·우선순위·버전과 함께 반영 ✅ (2026-04-04)
- [x] Phase 배정(V1/V2/V3)이 §7.3과 일치 ✅ (2026-04-04)
- [x] R-62-3(STRIDE 변경 시 CONFLICT_LOG 기록 + §2.2A 참조 확인) 규칙 반영 확인 ✅ (2026-04-04)
- [x] R-62-10(외부 보안 표준 STRIDE 변경 시 STALE 플래그 + 30일 갱신) 규칙 반영 확인 ✅ (2026-04-04)

**산출물**: `D:\VAMOS\docs\sot 2\6-2_Security-Governance\03_stride-threat-model\_index.md` — **v2.0 완료**

**완료 이력**:
- v1.0 (2026-03-24 S6-3): 초기 작성 — A~E 섹션 + STEP7-E 그룹 매핑 + L3 작성 현황
- v2.0 (2026-04-04): P0-5 프롬프트 기준 전면 보강 — §A LOCK L2 정식 원문 인용(6대 위협별 대응 통제), §B 확장 공격 표면 RAG 파이프라인 추가(이슈 #4), §C 인증/인가/접근제어 13항목(RBAC L8 + Autonomy L14 + 5-Gate L11 + NEVER_AUTO L20 + Session L9 + DEC-003 L19 + 감사 추적 S7E-028 V1→V2 수정), §D Attack Tree 유지, §E STEP7-E 28건 개별 분리(Part 1: 10건 + Part 3: 10건 + Part 7: 8건, ID·제목·우선순위·버전·상태), §F LOCK 참조 테이블 신설(L2/L8/L9/L11/L14/L19/L20 정식 `> LOCK` 형식 9블록, AUTHORITY_CHAIN §5 원문 전수 대조), §G Phase 배정 신설(§7.3 #6/#8/#11/#12), §H L3 작성 현황 Phase 대상 추가, §I 소비 도메인 참조 신설(부록 §A 기반 6개 도메인 + R-62-3 변경 통보), R-62-3 + R-62-10 규칙 반영
</details>

<details>
<summary><b>P0-6. 04_owasp-llm-top10/_index.md 작성</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` §2.2A(STRIDE/Attack Tree/OWASP 통합 — OWASP LLM Top 10 매핑 근거), §5(5-Gate System — LLM08 Excessive Agency 완화 근거)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.5.4(OWASP LLM Top 10 (2025) 매핑 — LLM01~LLM10 완화 전략)
- `D:\VAMOS\docs\sot\STEP7-E_보안_안전_거버넌스_작업가이드.md` Part 1(S7E-003 OWASP Top 10 전체 대응 — 교차참조), Part 5(S7E-041~050 AI Safety/Alignment), Part 6(S7E-051~060 규제/컴플라이언스), Part 10(S7E-085~092 VAMOS 고유 보안) — 총 28건 + 교차참조 1건
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\SECURITY_GOVERNANCE_구조화_종합계획서.md` §4.3(R-62-2, R-62-9, R-62-10 규칙 원본), §7.3(Phase 1 세부 항목 — 04 직접 배정 없음, Phase 2+ 대상 확인), §9.2(OWASP LOCK 충돌 시나리오), 부록 §A(소비 도메인 매트릭스), 부록 §B(STEP7-E 매핑 요약)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\AUTHORITY_CHAIN.md` §5 LOCK 레지스트리(L1, L7, L11, L14 교차 검증용)

**절차**:
1. D2.0-07 §2.2A(STRIDE/Attack Tree/OWASP 통합 — OWASP LLM Top 10 매핑 근거) + §5(5-Gate System — LLM08 Excessive Agency 완화) 읽기
2. Part2 §6.5.4 OWASP LLM Top 10 (2025) 매핑 전체 읽기 (LLM01~LLM10 위험 + 완화 전략)
3. STEP7-E Part 1에서 S7E-003(OWASP Top 10 for LLM 전체 대응 매핑) 교차참조 확인 — R-62-9 참조 근거, LLM01~LLM10 대응 전략 원천
4. 본 계획서 부록 §B에서 04_owasp-llm-top10 매핑 항목 확인: Part 5(S7E-041~050), Part 6(S7E-051~060), Part 10(S7E-085~092) — 총 28건
5. STEP7-E 원본에서 28건 개별 항목의 ID, 제목, 우선순위(CRITICAL/HIGH/MED) 직접 추출
6. 본 계획서 §7.3 확인: 04_owasp-llm-top10에 Phase 1 직접 배정 항목 없음 → Phase 2+ 대상 확인
7. 본 계획서 §4.3에서 R-62-2(OWASP 매핑 변경 → Part2 §6.5.4 동기화 필수), R-62-9(연 1회 OWASP 최신 버전 재검토, 참조: S7E-003), R-62-10(외부 보안 표준 변경 → STALE 플래그 + 30일 필수 갱신) 규칙 원문 확인
8. 본 계획서 §9.2에서 OWASP LOCK 충돌 시나리오 확인: 현재 LOCK = 2025 버전 → 외부 변경 → R-62-9 연 1회 재검토 → LOCK 갱신 제안 → 0-0 Governance 승인 필요
9. _index.md 신규 생성:
   - **A.** OWASP LLM Top 10 (2025) 매핑 (Part2 §6.5.4 기반, LLM01~LLM10 위험별 완화 전략 + S7E-003 교차참조)
   - **B.** AI Safety/Alignment (S7E-041~050 기반)
   - **C.** 규제/컴플라이언스 (S7E-051~060 기반)
   - **D.** VAMOS 고유 보안 차별화 (S7E-085~092 기반)
   - **E.** 외부 표준 재검토 프로세스 (R-62-2 Part2 §6.5.4 동기화 의무 + R-62-9 연 1회 재검토 + R-62-10 STALE 30일 필수 갱신 + §9.2 LOCK 충돌 해결 경로: 재검토 → 갱신 제안 → 0-0 거버넌스 승인)
   - **F.** LOCK 참조 테이블: L1(OWASP LLM Top 10 — 2025 버전 10개 위험 고정), L7(Guardrails 3-Layer), L11(5-Gate System — LLM08 Excessive Agency 완화), L14(자율 운영 수준 L0~L3) — `> LOCK (출처): [원문 그대로]` 형식
   - **G.** Phase 배정 (Phase 2+ 대상)
   - **H.** L3 작성 현황 (미작성 항목 + Phase 대상 표기)
   - **I.** 소비 도메인 참조 (부록 §A 기반, OWASP 매핑 소비 도메인 목록 — R-62-1 변경 시 12개 도메인 통보 대상)
10. LOCK 교차 검증: L1, L7, L11, L14 값을 AUTHORITY_CHAIN.md §5 + Part2/D2.0-07 원본과 대조 — 특히 L11(§5 5-Gate System) 원문 대조 시 D2.0-07 §5 직접 참조
11. §6 이슈 반영 확인: #2(STEP7-E Part2 미반영 — 28건 중 Part2 §6.5.4 직접 매핑 불가 항목 식별), #3(OWASP LLM Top 10 버전 고정 — L1 LOCK + R-62-9 연 1회 재검토 반영)

**검증**:
- [x] G0-3: 04_owasp-llm-top10/_index.md 존재 + 비어있지 않음 ✅ (2026-04-04)
- [x] LOCK 참조 값(L1, L7, L11, L14)이 Part2/D2.0-07 원본 및 AUTHORITY_CHAIN.md와 일치 ✅ (2026-04-04)
- [x] LOCK 참조 형식이 §3.5 절대 규칙(`> LOCK (출처): [원문 그대로]`) 준수 ✅ (2026-04-04)
- [x] OWASP LLM Top 10 위험 10건(LLM01~LLM10) 전부 완화 전략 명시 (§10 검증 #7 충족) ✅ (2026-04-04)
- [x] STEP7-E 28건(Part 5/6/10) 매핑이 ID·제목·우선순위와 함께 반영 ✅ (2026-04-04)
- [x] S7E-003(Part 1) 교차참조 포함 — R-62-9 참조 근거 명시 ✅ (2026-04-04)
- [x] R-62-2(OWASP 매핑 변경 → Part2 §6.5.4 동기화), R-62-9(연 1회 재검토), R-62-10(외부 표준 STALE 30일) 규칙 반영 확인 ✅ (2026-04-04)
- [x] §9.2 OWASP LOCK 충돌 해결 경로(재검토 → 갱신 제안 → 0-0 승인) 반영 확인 ✅ (2026-04-04)
- [x] 소비 도메인 참조 포함 (R-62-1 변경 시 12개 도메인 통보 대상 명시) ✅ (2026-04-04)

**산출물**: `D:\VAMOS\docs\sot 2\6-2_Security-Governance\04_owasp-llm-top10\_index.md` — **v2.0 완료**

**완료 이력**:
- v1.0 (2026-03-24 S6-3): 초기 작성 — A~E 섹션 + STEP7-E 그룹 매핑 + L3 작성 현황
- v2.0 (2026-04-04): P0-6 프롬프트 기준 전면 보강 — §A Part2 §6.5.4 기반 LLM01~LLM10 완화 전략 + S7E-003 교차참조(R-62-9 근거), §B STEP7-E Part 5 10건 개별 분리(ID·제목·우선순위·버전, STEP7-E 원본 직접 추출로 v1.0 오류 전수 수정), §C STEP7-E Part 6 10건 개별 분리(동일 수정), §D STEP7-E Part 10 8건 개별 분리(동일 수정), §E 외부 표준 재검토 프로세스 전면 보강(R-62-2 Part2 동기화 + R-62-9 연 1회 재검토 7단계 절차 + R-62-10 STALE 30일 긴급 절차 + §9.2 LOCK 충돌 해결 경로), §F LOCK 참조 테이블 신설(L1/L7/L11/L14 정식 `> LOCK` 형식, AUTHORITY_CHAIN §5 원문 전수 대조), §G Phase 배정 신설(§7.3 기준 + §6 이슈 #2 Part2 미반영 분석), §H L3 작성 현황 Phase 대상 추가, §I 소비 도메인 참조 신설(부록 §A 기반 12개 도메인 + OWASP 직접 매핑 + R-62-1 통보 의무)
</details>

**Phase 0→Phase 1 게이트 (G0)**:
- [x] **G0-1**: 본 계획서 APPROVED ✅ (2026-04-04)
- [x] **G0-2**: AUTHORITY_CHAIN.md에 LOCK 20건(L1~L20) 전체 포함 ✅ (2026-04-03)
- [x] **G0-3**: 4개 서브폴더 _index.md 존재 + 비어있지 않음 ✅ (2026-04-04)
- [x] **G0-4**: CONFLICT_LOG.md 존재 + §9.1 충돌 유형 분류 체계 반영 + 해결 우선순위 원칙 발췌 포함 ✅ (2026-04-03)

### 7.3 Phase 1 세부 항목 (V1 보안 정렬)

| # | 항목 | Part2 출처 | D2.0-07 출처 | 서브폴더 |
|---|------|-----------|------------|---------|
| 1 | AI 코드 생성 보안 체크리스트 7항목 | §6.5.1 | — | 01_ai-code-security |
| 2 | 입력 검증 (Zod + regex) | §6.5 #12 | S7E-006 | 01_ai-code-security |
| 3 | NeMo Guardrails (L1 입력 방어) | §6.5 #1 | §10.1 | 01_ai-code-security |
| 4 | Guardrails AI (L2 출력 검증) | §6.5 #2 | §10.2 | 01_ai-code-security |
| 5 | PII Regex 마스킹 | §6.5 #4 | §15.4 | 01_ai-code-security |
| 6 | RBAC 4레벨 | §6.5 #5 | §13 | 03_stride-threat-model |
| 7 | Docker 샌드박스 | §6.5 #8 | S7E-019 | 01_ai-code-security |
| 8 | 승인 타임아웃 (10분) | §6.5 #9 | §3.1 | 03_stride-threat-model |
| 9 | SQLCipher AES-256 | §6.5 #10 | — | 02_hmac-timing-defense |
| 10 | API Key 관리 | §6.5 #11 | S7E-005 | 02_hmac-timing-defense |
| 11 | DEC-003 도구 승인 Allowlist | §6.5 #15 | — | 03_stride-threat-model |
| 12 | STRIDE 기본 매핑 (6대 위협) | §6.5.3 | §2.2A | 03_stride-threat-model |

---

#### Phase 1 단계별 상세 작업 절차

<!-- ═══════════════════════════════════════════════ -->
<!-- 01_ai-code-security (#1, #2, #3, #4, #5, #7)  -->
<!-- ═══════════════════════════════════════════════ -->

<details>
<summary><b>#1. AI 코드 생성 보안 체크리스트 7항목</b></summary>

**대조 기준**:
- §7 세부 작업: #1 "AI 코드 생성 보안 체크리스트 7항목"
- §7 전환 게이트: P1→P2 (V1 보안 항목 12건 구현 완료 + AI 코드 보안 체크리스트 CI/CD 통합 + STRIDE 기본 매핑 검증)
- §6 이슈: #7 (AI 코드 체크리스트-CI/CD 연결 → 4-2 교차 참조)

**목표**: Part2 §6.5.1 기반 AI 코드 생성 보안 체크리스트 7항목을 실행 가능한 검증 스크립트·규칙 셋으로 구체화하고, CI/CD(4-2) 통합 포인터를 확보한다.

**입력 파일**:
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.5.1 (7개 검증 항목: 입력 검증, SQL 바인딩, trace_id 위조 방지, Docker 네트워크 차단, API 키 노출 방지, 권한 체크, 에러 정보 유출)
- `D:\VAMOS\docs\sot\D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` §10 (Guardrails 3-Layer)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\01_ai-code-security\_index.md`

**절차**:
1. Part2 §6.5.1 AI 코드 생성 보안 체크리스트 7항목 전문 추출 — 항목별 ID(CK-01~CK-07), 검증 대상, 통과 조건 정리
2. 각 항목에 대해 자동화 검증 방법 설계: ESLint custom rule, regex 패턴, AST 분석, Semgrep rule 등 매핑
3. 01_ai-code-security/_index.md 기존 §A 섹션과 정합성 확인 — 7항목이 _index.md 내용과 1:1 대응하는지 검증
4. 체크리스트 상세 명세 파일 작성: 항목별 (검증 대상, 위반 예시, 자동 검증 규칙, 수동 검증 절차, 심각도)
5. CI/CD 통합 포인터 작성: `sot 2/4-2_CI-CD-Pipeline/03_security-scanning/` 참조 경로 + hook 트리거 조건 명시 (ISS-7 해결)
6. 부록 §C Guardrails 3×15 교차 참조 매트릭스와 대조 — 7항목이 L1/L2/L3 어느 계층에서 검증되는지 명시

**검증**:
- [x] CK-01~CK-07 전체 7항목이 상세 명세에 포함 ✅
- [x] 각 항목에 자동화 검증 규칙(ESLint/Semgrep 등) 또는 수동 절차 명시 ✅
- [x] CI/CD(4-2) 교차 참조 포인터 포함 (ISS-7) ✅
- [x] _index.md §A 섹션과 항목 정합성 확인 ✅

> **완료**: 2026-04-12. AI 코드 생성 보안 체크리스트 CK-01~CK-07 전체 7항목을 자동화 검증 규칙 및 CI/CD 통합 포인터와 함께 구체화.
>
> **실행 결과 요약**:
> - CK-01~CK-07 7항목 전수 상세 명세 완료(ESLint/Semgrep 규칙 매핑 포함)
> - CI/CD(4-2) 교차 참조 포인터 확보, _index.md §A 1:1 정합성 확인
> - 부록 §C Guardrails 3×15 매트릭스 대조 완료, L1/L2/L3 계층 명시
> - 이월 항목 없음

**[P1-1 #1] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: ai_code_checklist_7items.md
- 1. 게이트: G1-1 충족 (12건 중 1건), G1-2 CI/CD 통합 포인터 확보
- 2. CONFLICT: 발견 0건
- 3. LOCK 변경: 없음
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\6-2_Security-Governance\01_ai-code-security\ai_code_checklist_7items.md`
</details>

<details>
<summary><b>#2. 입력 검증 Zod+regex</b></summary>

**대조 기준**:
- §7 세부 작업: #2 "입력 검증 (Zod + regex)"
- §7 전환 게이트: P1→P2 (V1 보안 항목 12건 구현 완료 + AI 코드 보안 체크리스트 CI/CD 통합 + STRIDE 기본 매핑 검증)
- §6 이슈: #2 (STEP7-E 92건 중 미반영 → 서브폴더별 매핑; S7E-006)

**목표**: 모든 외부 입력(사용자 프롬프트, MCP 도구 파라미터, API 요청)에 대해 Zod 스키마 + regex 패턴 기반 입력 검증 계층을 정의하고, STEP7-E S7E-006 요구사항을 충족한다.

**입력 파일**:
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.5 #12 (입력 검증)
- `D:\VAMOS\docs\sot\STEP7-E_보안_안전_거버넌스_작업가이드.md` S7E-006 (입력 검증 요구사항)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\01_ai-code-security\_index.md`

**절차**:
1. Part2 §6.5 #12 입력 검증 항목 전문 추출 — Zod 스키마 적용 대상(프롬프트 길이, 도구 파라미터 타입, API 페이로드 구조) 식별
2. STEP7-E S7E-006 원본 요구사항 추출 — 우선순위, 버전(V1), 구체적 검증 대상 확인
3. 입력 유형별 Zod 스키마 설계: (a) 프롬프트 입력 — 최대 길이, 금지 패턴(인젝션 시그니처), (b) MCP 도구 파라미터 — 타입·범위 강제, (c) API 요청 본문 — JSON 스키마 검증
4. regex 패턴 라이브러리 정의: SQL 인젝션 패턴, XSS 패턴, 경로 탈출 패턴, 프롬프트 인젝션 시그니처
5. 검증 실패 시 에러 처리 정책: 균일한 에러 응답 형식(정보 유출 방지), 로깅(trace_id 포함), 재시도 허용 조건
6. _index.md 기존 콘텐츠와 정합성 확인 + CK-01(입력 검증) 항목과 상호 참조

**검증**:
- [x] Zod 스키마가 3가지 입력 유형(프롬프트, MCP 파라미터, API 요청) 모두 커버 ✅
- [x] regex 패턴이 SQL 인젝션, XSS, 경로 탈출, 프롬프트 인젝션 4가지 공격 벡터 포함 ✅
- [x] S7E-006 요구사항 반영 확인 ✅
- [x] 에러 처리 정책에 정보 유출 방지 조항 포함 ✅

> **완료**: 2026-04-12. Zod 스키마 + regex 패턴 기반 입력 검증 계층을 3가지 입력 유형·4가지 공격 벡터에 대해 정의.
>
> **실행 결과 요약**:
> - Zod 스키마 3유형(프롬프트/MCP 파라미터/API 요청) 전수 커버
> - regex 패턴 4벡터(SQL 인젝션/XSS/경로 탈출/프롬프트 인젝션) 라이브러리 정의
> - S7E-006 요구사항 반영 확인, 에러 처리 정책 정보 유출 방지 포함
> - 이월 항목 없음

**[P1-1 #2] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: input_validation_zod_regex.md
- 1. 게이트: G1-1 충족 (12건 중 1건)
- 2. CONFLICT: 발견 0건
- 3. LOCK 변경: 없음
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\6-2_Security-Governance\01_ai-code-security\input_validation_zod_regex.md`
</details>

<details>
<summary><b>#3. NeMo Guardrails L1 입력 방어</b></summary>

**대조 기준**:
- §7 세부 작업: #3 "NeMo Guardrails (L1 입력 방어)"
- §7 전환 게이트: P1→P2 (V1 보안 항목 12건 구현 완료 + AI 코드 보안 체크리스트 CI/CD 통합 + STRIDE 기본 매핑 검증)
- §6 이슈: #1 (Guardrails 3×15 교차 참조 — 부록 §C 연동)

**목표**: Guardrails 3-Layer 중 L1(입력 계층)을 NeMo Guardrails로 구현하여 프롬프트 인젝션, 탈옥 시도, 유해 입력을 사전 차단한다. LOCK L7 준수.

**입력 파일**:
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.5 #1 (NeMo Guardrails)
- `D:\VAMOS\docs\sot\D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` §10.1 (L1 입력 방어 정책)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\AUTHORITY_CHAIN.md` §5 LOCK L7 (Guardrails 3-Layer)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\01_ai-code-security\_index.md`

**절차**:
1. D2.0-07 §10.1 L1 입력 방어 정책 전문 추출 — 차단 대상(인젝션, 탈옥, 유해 콘텐츠), 응답 정책, 로깅 요구사항
2. Part2 §6.5 #1 NeMo Guardrails 구현 지침 추출 — 설정 파일 구조, 규칙 정의 방식, V1 범위
3. NeMo Guardrails 구성 설계: (a) Colang 규칙 파일 — 금지 패턴, 탈옥 감지, (b) config.yml — 모델 연결, 임계값 설정, (c) 커스텀 액션 — 로깅, 알림
4. L1 입력 필터 규칙 정의: 프롬프트 인젝션 패턴 10종 이상, 탈옥 시도 패턴 5종, 유해 콘텐츠 분류 기준
5. 부록 §C Guardrails 3×15 교차 참조 매트릭스와 대조 — L1 계층이 커버하는 §6.5 항목 전체 확인
6. LOCK L7 교차 검증: AUTHORITY_CHAIN.md §5 L7 값과 구현 범위 일치 여부 확인
7. 차단 시 사용자 응답 형식 정의 + trace_id(L18) 포함 감사 로그 구조 설계

**검증**:
- [x] NeMo Guardrails Colang 규칙 파일 구조 명세 포함 ✅
- [x] L1 차단 대상(인젝션, 탈옥, 유해 콘텐츠) 3가지 카테고리 전체 정의 ✅
- [x] LOCK L7 교차 검증 완료 (AUTHORITY_CHAIN §5 대조) ✅
- [x] 부록 §C L1 행과 정합성 확인 ✅
- [x] 감사 로그 구조에 trace_id(L18) 포함 ✅

> **완료**: 2026-04-12. NeMo Guardrails L1 입력 방어 Colang 규칙 구조 및 3카테고리 차단 정책 정의, LOCK L7 교차 검증 완료.
>
> **실행 결과 요약**:
> - Colang 규칙 파일 구조, config.yml, 커스텀 액션 명세 포함
> - L1 차단 3카테고리(인젝션 10종/탈옥 5종/유해 콘텐츠) 정의
> - LOCK L7 AUTHORITY_CHAIN §5 대조 완료, 부록 §C L1 행 정합성 확인
> - 이월 항목 없음

**[P1-1 #3] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: nemo_guardrails_l1_input.md
- 1. 게이트: G1-1 충족 (12건 중 1건), G1-4 LOCK L7 대조 완료
- 2. CONFLICT: 발견 0건
- 3. LOCK 변경: 없음
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\6-2_Security-Governance\01_ai-code-security\nemo_guardrails_l1_input.md`
</details>

<details>
<summary><b>#4. Guardrails AI L2 출력 검증</b></summary>

**대조 기준**:
- §7 세부 작업: #4 "Guardrails AI (L2 출력 검증)"
- §7 전환 게이트: P1→P2 (V1 보안 항목 12건 구현 완료 + AI 코드 보안 체크리스트 CI/CD 통합 + STRIDE 기본 매핑 검증)
- §6 이슈: #1 (Guardrails 3×15 교차 참조 — 부록 §C 연동)

**목표**: Guardrails 3-Layer 중 L2(처리/출력 계층)를 Guardrails AI 프레임워크로 구현하여 LLM 출력의 구조 준수, 유해 콘텐츠 필터링, 할루시네이션 감지를 수행한다. LOCK L7 준수.

**입력 파일**:
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.5 #2 (Guardrails AI)
- `D:\VAMOS\docs\sot\D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` §10.2 (L2 출력 검증 정책)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\AUTHORITY_CHAIN.md` §5 LOCK L7 (Guardrails 3-Layer)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\01_ai-code-security\_index.md`

**절차**:
1. D2.0-07 §10.2 L2 출력 검증 정책 전문 추출 — 검증 대상(구조, 유해성, 할루시네이션), 실패 시 처리(재생성/차단/경고)
2. Part2 §6.5 #2 Guardrails AI 구현 지침 추출 — Guard 정의, Validator 구성, Rail 스펙 형식
3. Guardrails AI 구성 설계: (a) Guard 정의 — 출력 스키마, 검증 규칙, (b) Validator 체인 — 유해 콘텐츠 필터, JSON 구조 검증, 길이 제한, (c) 실패 처리 전략 — retry(최대 3회), fallback 응답
4. 출력 검증 규칙 정의: 코드 생성 출력(위험 함수 감지, 하드코딩 시크릿 감지), 자연어 출력(유해 표현, PII 유출), 구조화 출력(JSON 스키마 준수)
5. 부록 §C Guardrails 3×15 교차 참조 매트릭스와 대조 — L2 계층이 커버하는 §6.5 항목 전체 확인
6. LOCK L7 교차 검증: AUTHORITY_CHAIN.md §5 L7 값과 구현 범위 일치 여부 확인
7. L1(NeMo)→L2(Guardrails AI) 파이프라인 연결 인터페이스 정의 + 실패 시 L1 재진입 조건

**검증**:
- [x] Guardrails AI Guard/Validator/Rail 구성 명세 포함 ✅
- [x] 출력 검증 3가지 카테고리(코드/자연어/구조화) 전체 정의 ✅
- [x] 실패 처리 전략(retry/fallback) 명시 ✅
- [x] LOCK L7 교차 검증 완료 (AUTHORITY_CHAIN §5 대조) ✅
- [x] 부록 §C L2 행과 정합성 확인 ✅

> **완료**: 2026-04-12. Guardrails AI L2 출력 검증 Guard/Validator/Rail 구성 및 3카테고리 출력 검증 규칙 정의, 실패 처리 전략 포함.
>
> **실행 결과 요약**:
> - Guard/Validator/Rail 구성 명세, 코드/자연어/구조화 출력 3카테고리 전체 정의
> - 실패 처리 전략(retry 최대 3회/fallback 응답) 명시
> - LOCK L7 AUTHORITY_CHAIN §5 대조 완료, 부록 §C L2 행 정합성 확인
> - 이월 항목 없음

**[P1-1 #4] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: guardrails_ai_l2_output.md
- 1. 게이트: G1-1 충족 (12건 중 1건), G1-4 LOCK L7 대조 완료
- 2. CONFLICT: 발견 0건
- 3. LOCK 변경: 없음
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\6-2_Security-Governance\01_ai-code-security\guardrails_ai_l2_output.md`
</details>

<details>
<summary><b>#5. PII Regex 마스킹</b></summary>

**대조 기준**:
- §7 세부 작업: #5 "PII Regex 마스킹"
- §7 전환 게이트: P1→P2 (V1 보안 항목 12건 구현 완료 + AI 코드 보안 체크리스트 CI/CD 통합 + STRIDE 기본 매핑 검증)
- §6 이슈: 해당 없음

**목표**: LLM 입출력에서 PII(개인식별정보)를 regex 기반으로 탐지·마스킹하여 민감 정보 유출을 방지한다. D2.0-07 §15.4 GDPR 사전 대응.

**입력 파일**:
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.5 #4 (PII 마스킹)
- `D:\VAMOS\docs\sot\D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` §15.4 (GDPR 데이터 보호)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\01_ai-code-security\_index.md`

**절차**:
1. Part2 §6.5 #4 PII 마스킹 구현 지침 추출 — 대상 PII 유형, 마스킹 방식, 적용 지점
2. D2.0-07 §15.4 GDPR 데이터 보호 요구사항 추출 — PII 정의, 처리 원칙, 최소 수집
3. PII 유형별 regex 패턴 라이브러리 설계: (a) 이메일 — RFC 5322 패턴, (b) 전화번호 — 국가 코드 포함, (c) 주민등록번호/SSN — 한국·미국 형식, (d) 신용카드 — Luhn 사전 검증 + 패턴, (e) IP 주소 — IPv4/IPv6, (f) 이름 — NER 보조 필요 표기
4. 마스킹 전략 정의: 부분 마스킹(이메일: u***@d.com), 전체 마스킹([PII_REDACTED]), 복원 가능 토큰화(보안 감사용)
5. 적용 지점 명시: L1 입력 전처리(NeMo 연동), L2 출력 후처리(Guardrails AI 연동), 로그 기록 시
6. 오탐·미탐 대응: 허용 목록(비 PII 이메일 형식), 정기 패턴 업데이트 주기(분기 1회)

**검증**:
- [x] PII 유형 6가지 이상 regex 패턴 정의 ✅
- [x] 마스킹 전략(부분/전체/토큰화) 3가지 명시 ✅
- [x] 적용 지점이 L1 입력·L2 출력·로그 3곳 포함 ✅
- [x] D2.0-07 §15.4 GDPR 요구사항 반영 확인 ✅

> **완료**: 2026-04-12. PII 6유형 이상 regex 패턴 라이브러리 및 3가지 마스킹 전략 정의, L1/L2/로그 3지점 적용.
>
> **실행 결과 요약**:
> - PII 6유형(이메일/전화번호/주민등록번호/신용카드/IP주소/이름) regex 패턴 정의
> - 마스킹 전략 3가지(부분/전체/토큰화) 명시, 적용 지점 3곳 포함
> - D2.0-07 §15.4 GDPR 요구사항 반영 확인, 오탐·미탐 대응 정책 포함
> - 이월 항목 없음

**[P1-1 #5] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: pii_regex_masking.md
- 1. 게이트: G1-1 충족 (12건 중 1건)
- 2. CONFLICT: 발견 0건
- 3. LOCK 변경: 없음
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\6-2_Security-Governance\01_ai-code-security\pii_regex_masking.md`
</details>

<details>
<summary><b>#7. Docker 샌드박스</b></summary>

**대조 기준**:
- §7 세부 작업: #7 "Docker 샌드박스"
- §7 전환 게이트: P1→P2 (V1 보안 항목 12건 구현 완료 + AI 코드 보안 체크리스트 CI/CD 통합 + STRIDE 기본 매핑 검증)
- §6 이슈: #2 (STEP7-E 92건 중 미반영 → S7E-019)

**목표**: AI 생성 코드 실행을 Docker 컨테이너로 격리하여 호스트 시스템 보호. 30초 타임아웃 + --network=none 네트워크 차단 필수. LOCK L12 준수.

**입력 파일**:
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.5 #8 (Docker 샌드박스)
- `D:\VAMOS\docs\sot\STEP7-E_보안_안전_거버넌스_작업가이드.md` S7E-019 (코드 실행 격리)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\AUTHORITY_CHAIN.md` §5 LOCK L12 (Docker 30초 --network=none)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\01_ai-code-security\_index.md`

**절차**:
1. Part2 §6.5 #8 Docker 샌드박스 구현 지침 추출 — 컨테이너 구성, 리소스 제한, 네트워크 정책
2. STEP7-E S7E-019 코드 실행 격리 요구사항 추출 — 격리 수준, 파일시스템 접근 제한, 프로세스 제한
3. Docker 실행 환경 설계: (a) 베이스 이미지 — 최소 Alpine 기반, (b) --network=none 강제(L12), (c) --read-only 루트 파일시스템, (d) --memory=256m --cpus=0.5 리소스 제한
4. 타임아웃 메커니즘 설계: 30초 하드 타임아웃(L12), 컨테이너 자동 종료 + 결과 회수, 타임아웃 초과 시 강제 kill + 경고 로그
5. 입출력 인터페이스 설계: stdin으로 코드 전달, stdout/stderr 캡처, 결과물 임시 볼륨 마운트(/tmp/sandbox:ro)
6. 보안 강화: seccomp 프로파일 적용, capabilities 최소화(--cap-drop=ALL), PID namespace 격리
7. LOCK L12 교차 검증: AUTHORITY_CHAIN.md §5 L12 값("Docker 30초 --network=none")과 설계 일치 확인

**검증**:
- [x] --network=none 네트워크 차단 명시 (L12) ✅
- [x] 30초 타임아웃 하드 리밋 명시 (L12) ✅
- [x] 리소스 제한(메모리, CPU) 정의 ✅
- [x] seccomp/capabilities 보안 강화 포함 ✅
- [x] S7E-019 요구사항 반영 확인 ✅
- [x] LOCK L12 교차 검증 완료 ✅

> **완료**: 2026-04-12. Docker 샌드박스 실행 환경 설계 완료 — --network=none + 30초 타임아웃 + seccomp 보안 강화.
>
> **실행 결과 요약**:
> - --network=none 네트워크 차단, 30초 하드 타임아웃, 리소스 제한(256m/0.5 CPU) 명시
> - seccomp 프로파일, --cap-drop=ALL, PID namespace 격리 보안 강화 포함
> - S7E-019 요구사항 반영, LOCK L12 AUTHORITY_CHAIN §5 대조 완료
> - 이월 항목 없음

**[P1-1 #7] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: docker_sandbox.md
- 1. 게이트: G1-1 충족 (12건 중 1건), G1-4 LOCK L12 대조 완료
- 2. CONFLICT: 발견 0건
- 3. LOCK 변경: 없음
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\6-2_Security-Governance\01_ai-code-security\docker_sandbox.md`
</details>

<!-- ═══════════════════════════════════════════════ -->
<!-- 02_hmac-timing-defense (#9, #10)               -->
<!-- ═══════════════════════════════════════════════ -->

<details>
<summary><b>#9. SQLCipher AES-256</b></summary>

**대조 기준**:
- §7 세부 작업: #9 "SQLCipher AES-256"
- §7 전환 게이트: P1→P2 (V1 보안 항목 12건 구현 완료 + AI 코드 보안 체크리스트 CI/CD 통합 + STRIDE 기본 매핑 검증)
- §6 이슈: 해당 없음

**목표**: 로컬 SQLite 데이터베이스를 SQLCipher AES-256-CBC로 암호화하여 저장 데이터(data-at-rest) 보호. LOCK L13 준수.

**입력 파일**:
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.5 #10 (SQLCipher AES-256)
- `D:\VAMOS\docs\sot\D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` S7E-032 (SQLCipher 요구사항)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\AUTHORITY_CHAIN.md` §5 LOCK L13 (SQLCipher AES-256-CBC)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\02_hmac-timing-defense\_index.md`

**절차**:
1. Part2 §6.5 #10 SQLCipher 구현 지침 추출 — 암호화 알고리즘, 키 파생, 페이지 크기, 호환성
2. D2.0-07 S7E-032 SQLCipher 요구사항 추출 — 암호화 강도, 적용 대상 DB, 성능 영향 허용 범위
3. SQLCipher 설정 설계: (a) 암호화 — AES-256-CBC(L13), (b) 키 파생 — PBKDF2-HMAC-SHA512, 256000 iterations, (c) 페이지 크기 — 4096, (d) PRAGMA 설정 — cipher_compatibility=4
4. 키 관리: 마스터 키 생성(32바이트 CSPRNG), 키 저장(.env 환경 변수 또는 OS 키체인), 키 순환 시 `PRAGMA rekey` 절차
5. 대상 DB 식별: 사용자 설정 DB, 대화 이력 DB, 감사 로그 DB — 각 DB별 암호화 적용 여부 및 성능 영향 평가
6. 마이그레이션 절차: 기존 평문 DB → SQLCipher 암호화 DB 변환 스크립트, 무결성 검증(SHA-256 체크섬)
7. LOCK L13 교차 검증: AUTHORITY_CHAIN.md §5 L13 값과 설계 일치 확인

**검증**:
- [x] AES-256-CBC 암호화 명시 (L13) ✅
- [x] 키 파생 함수(PBKDF2) 및 iterations 명시 ✅
- [x] 대상 DB 목록 및 마이그레이션 절차 포함 ✅
- [x] 키 관리(생성, 저장, 순환) 절차 정의 ✅
- [x] S7E-032 요구사항 반영 확인 ✅
- [x] LOCK L13 교차 검증 완료 ✅

> **완료**: 2026-04-12. SQLCipher AES-256-CBC 암호화 설계 — PBKDF2 키 파생, 대상 DB 식별, 마이그레이션 절차 포함.
>
> **실행 결과 요약**:
> - AES-256-CBC 암호화, PBKDF2-HMAC-SHA512 256000 iterations 명시
> - 대상 DB 3종(설정/대화이력/감사로그) 식별, 마이그레이션 절차 정의
> - 키 관리(생성/저장/순환) 절차 포함, S7E-032 반영 확인
> - 이월 항목 없음

**[P1-1 #9] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: sqlcipher_aes256.md
- 1. 게이트: G1-1 충족 (12건 중 1건), G1-4 LOCK L13 대조 완료
- 2. CONFLICT: 발견 0건
- 3. LOCK 변경: 없음
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\6-2_Security-Governance\02_hmac-timing-defense\sqlcipher_aes256.md`
</details>

<details>
<summary><b>#10. API Key 관리</b></summary>

**대조 기준**:
- §7 세부 작업: #10 "API Key 관리"
- §7 전환 게이트: P1→P2 (V1 보안 항목 12건 구현 완료 + AI 코드 보안 체크리스트 CI/CD 통합 + STRIDE 기본 매핑 검증)
- §6 이슈: #2 (STEP7-E 92건 중 미반영 → S7E-005)

**목표**: LLM API 키를 안전하게 관리하여 키 유출·남용을 방지. .env + dotenv 패턴 + 소스 코드 노출 방지. STEP7-E S7E-005 충족.

**입력 파일**:
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.5 #11 (API Key 관리)
- `D:\VAMOS\docs\sot\STEP7-E_보안_안전_거버넌스_작업가이드.md` S7E-005 (API Key 보안 관리)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\02_hmac-timing-defense\_index.md`

**절차**:
1. Part2 §6.5 #11 API Key 관리 지침 추출 — 저장 방식(.env), 접근 패턴(dotenv), 로테이션 정책
2. STEP7-E S7E-005 API Key 보안 요구사항 추출 — 키 노출 방지, 접근 로깅, 비상 폐기 절차
3. 키 저장 아키텍처 설계: (a) .env 파일 — .gitignore 필수 등록, 0600 퍼미션, (b) dotenv 로딩 — 프로세스 환경 변수로만 참조, (c) 소스 코드 노출 방지 — pre-commit hook(detect-secrets)
4. 키 로테이션 정책: 90일 주기(LOCK L5 HMAC 키 순환 주기를 API 키에 유추 적용 — API 키 전용 LOCK 미정의), 로테이션 자동화 스크립트, Grace Period(24h 이전 키 병행 유효)
5. 비상 폐기 절차: 키 유출 감지 시 즉시 폐기 → 새 키 발급 → .env 교체 → 서비스 재시작 → 감사 로그 기록
6. 접근 로깅: API Key 사용 시마다 trace_id(L18) + 타임스탬프 + 호출 엔드포인트 기록
7. 비용 제어 연동: 일일 비용 상한(L17) 초과 시 API Key 자동 비활성화 트리거

**검증**:
- [x] .env + dotenv 패턴 명시 ✅
- [x] .gitignore 및 pre-commit hook(detect-secrets) 포함 ✅
- [x] 키 로테이션 정책(90일) 및 Grace Period 명시 ✅
- [x] 비상 폐기 절차 정의 ✅
- [x] S7E-005 요구사항 반영 확인 ✅
- [x] 비용 제어(L17) 연동 포함 ✅

> **완료**: 2026-04-12. API Key 관리 아키텍처 설계 — .env+dotenv 패턴, 90일 로테이션, 비상 폐기 절차, 비용 제어 연동.
>
> **실행 결과 요약**:
> - .env+dotenv 패턴, .gitignore, pre-commit hook(detect-secrets) 포함
> - 키 로테이션 90일 주기 + Grace Period 24h, 비상 폐기 절차 정의
> - S7E-005 반영 확인, 비용 제어(L17) 초과 시 자동 비활성화 연동
> - 이월 항목 없음

**[P1-1 #10] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: api_key_management.md
- 1. 게이트: G1-1 충족 (12건 중 1건)
- 2. CONFLICT: 발견 0건
- 3. LOCK 변경: 없음
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\6-2_Security-Governance\02_hmac-timing-defense\api_key_management.md`
</details>

<!-- ═══════════════════════════════════════════════ -->
<!-- 03_stride-threat-model (#6, #8, #11, #12)      -->
<!-- ═══════════════════════════════════════════════ -->

<details>
<summary><b>#6. RBAC 4레벨</b></summary>

**대조 기준**:
- §7 세부 작업: #6 "RBAC 4레벨"
- §7 전환 게이트: P1→P2 (V1 보안 항목 12건 구현 완료 + AI 코드 보안 체크리스트 CI/CD 통합 + STRIDE 기본 매핑 검증)
- §6 이슈: 해당 없음

**목표**: D2.0-07 §13 기반 RBAC 4레벨 접근 제어를 구현하여 사용자·Agent·도구 간 권한 분리를 수행한다. LOCK L8 준수.

**입력 파일**:
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.5 #5 (RBAC)
- `D:\VAMOS\docs\sot\D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` §13 (RBAC 접근 제어)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\AUTHORITY_CHAIN.md` §5 LOCK L8 (RBAC 4단계)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\03_stride-threat-model\_index.md`

**절차**:
1. D2.0-07 §13 RBAC 4레벨 접근 제어 정책 전문 추출 — 레벨 정의, 권한 매트릭스, 상승 조건
2. Part2 §6.5 #5 RBAC 구현 지침 추출 — V1 범위, 코드 위치, 적용 대상
3. 4레벨 권한 모델 상세 설계: (a) L0 Viewer — 읽기 전용, (b) L1 Operator — 기본 실행 + 승인 요청, (c) L2 Admin — 도구 승인 + 설정 변경, (d) L3 Owner — LOCK 변경 제안 + 거버넌스 접근
4. 권한 매트릭스 작성: 각 레벨 × 리소스(대화, 도구, 설정, 감사로그, LOCK) 접근 허용/거부 표
5. 권한 상승 프로토콜: 상승 요청 → 인증 확인 → 타임아웃(L9 연동) → 감사 기록
6. Agent 권한 제어: Agent별 기본 레벨 할당, DEC-003(L19) 연동으로 도구 실행 권한 분리
7. LOCK L8 교차 검증: AUTHORITY_CHAIN.md §5 L8 값과 4레벨 정의 일치 확인

**검증**:
- [x] 4레벨(L0~L3) 정의 및 권한 범위 명시 ✅
- [x] 권한 매트릭스(레벨×리소스) 포함 ✅
- [x] 권한 상승 프로토콜 정의 ✅
- [x] Agent 권한 제어 및 DEC-003(L19) 연동 명시 ✅
- [x] D2.0-07 §13 요구사항 반영 확인 ✅
- [x] LOCK L8 교차 검증 완료 ✅

> **완료**: 2026-04-12. RBAC 4레벨(L0~L3) 접근 제어 설계 — 권한 매트릭스, 상승 프로토콜, Agent 권한 제어 포함.
>
> **실행 결과 요약**:
> - 4레벨(L0 Viewer/L1 Operator/L2 Admin/L3 Owner) 정의 및 권한 매트릭스 작성
> - 권한 상승 프로토콜(요청→인증→타임아웃→감사) 정의, DEC-003(L19) 연동
> - D2.0-07 §13 요구사항 반영, LOCK L8 AUTHORITY_CHAIN §5 대조 완료
> - 이월 항목 없음

**[P1-1 #6] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: rbac_4level.md
- 1. 게이트: G1-1 충족 (12건 중 1건), G1-4 LOCK L8 대조 완료
- 2. CONFLICT: 발견 0건
- 3. LOCK 변경: 없음
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\6-2_Security-Governance\03_stride-threat-model\rbac_4level.md`
</details>

<details>
<summary><b>#8. 승인 타임아웃 10분</b></summary>

**대조 기준**:
- §7 세부 작업: #8 "승인 타임아웃 (10분)"
- §7 전환 게이트: P1→P2 (V1 보안 항목 12건 구현 완료 + AI 코드 보안 체크리스트 CI/CD 통합 + STRIDE 기본 매핑 검증)
- §6 이슈: 해당 없음

**목표**: D2.0-07 §3.1 기반 승인 요청에 LOCK L9 타임아웃(일반 P1 10분=600초 / HITL P2 5분=300초 → Auto deny)을 적용하여 무한 대기·무단 승인을 방지한다. LOCK L9 준수.

**입력 파일**:
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.5 #9 (승인 타임아웃)
- `D:\VAMOS\docs\sot\D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` §3.1 (승인 정책 타임아웃 + NEVER_AUTO)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\AUTHORITY_CHAIN.md` §5 LOCK L9 (P2 타임아웃), L20 (NEVER_AUTO)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\03_stride-threat-model\_index.md`

**절차**:
1. D2.0-07 §3.1 승인 정책 전문 추출 — P2 위험 작업 정의, 타임아웃 값, 타임아웃 초과 시 행동, NEVER_AUTO 규칙
2. Part2 §6.5 #9 승인 타임아웃 구현 지침 추출 — 타이머 구현 방식, UI 표시, 알림 채널
3. 승인 흐름 설계: 위험 작업 감지 → 승인 요청 생성(trace_id L18 포함) → 사용자 알림 → 타이머 시작(600초) → 응답 대기
4. 타임아웃 처리: 600초 초과 → 자동 거부 → 작업 취소 → 감사 로그("TIMEOUT_REJECTED") 기록 → 사용자 알림
5. NEVER_AUTO(L20) 강제: 자동 승인 로직 완전 차단, 코드 레벨에서 auto_approve 파라미터 제거/무효화
6. 재요청 정책: 타임아웃 후 동일 작업 재요청 허용 여부, 연속 타임아웃 3회 시 세션 레벨 경고
7. LOCK L9·L20 교차 검증: AUTHORITY_CHAIN.md §5 L9(타임아웃)·L20(NEVER_AUTO) 값과 설계 일치 확인

**검증**:
- [x] 10분(600초) 타임아웃 명시 (L9) ✅
- [x] 타임아웃 초과 시 자동 거부 + 감사 로그 기록 정의 ✅
- [x] NEVER_AUTO 강제 메커니즘 명시 (L20) ✅
- [x] 승인 흐름 전체(요청→대기→응답/타임아웃) 다이어그램 또는 절차 포함 ✅
- [x] D2.0-07 §3.1 요구사항 반영 확인 ✅
- [x] LOCK L9·L20 교차 검증 완료 ✅

> **완료**: 2026-04-12. P2 위험 작업 승인 10분 타임아웃 설계 — NEVER_AUTO 강제, 자동 거부, 감사 로그 포함.
>
> **실행 결과 요약**:
> - 10분(600초) 하드 타임아웃, 초과 시 자동 거부 + TIMEOUT_REJECTED 감사 로그
> - NEVER_AUTO(L20) 강제 메커니즘 명시, auto_approve 파라미터 무효화
> - 승인 흐름 전체 절차(요청→대기→응답/타임아웃) 정의, D2.0-07 §3.1 반영
> - 이월 항목 없음

**[P1-1 #8] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: approval_timeout_10min.md
- 1. 게이트: G1-1 충족 (12건 중 1건), G1-4 LOCK L9·L20 대조 완료
- 2. CONFLICT: 발견 0건
- 3. LOCK 변경: 없음
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\6-2_Security-Governance\03_stride-threat-model\approval_timeout_10min.md`
</details>

<details>
<summary><b>#11. DEC-003 도구 승인 Allowlist</b></summary>

**대조 기준**:
- §7 세부 작업: #11 "DEC-003 도구 승인 Allowlist"
- §7 전환 게이트: P1→P2 (V1 보안 항목 12건 구현 완료 + AI 코드 보안 체크리스트 CI/CD 통합 + STRIDE 기본 매핑 검증)
- §6 이슈: 해당 없음

**목표**: Agent가 실행할 수 있는 도구를 사전 승인 목록(Allowlist)으로 제한하여 무단 도구 실행을 차단한다. LOCK L19 준수.

**입력 파일**:
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.5 #15 (DEC-003 Allowlist)
- `D:\VAMOS\docs\sot\D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` (DEC-003 도구 승인 정책)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\AUTHORITY_CHAIN.md` §5 LOCK L19 (DEC-003 도구 승인)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\03_stride-threat-model\_index.md`

**절차**:
1. Part2 §6.5 #15 DEC-003 Allowlist 구현 지침 추출 — 도구 등록 절차, Allowlist 형식, 실행 시 검증 흐름
2. D2.0-07 DEC-003 도구 승인 정책 추출 — 승인 권한 주체, 도구 분류(안전/위험/금지), 예외 처리
3. Allowlist 구조 설계: (a) JSON 스키마 — tool_id, name, risk_level, allowed_roles, max_calls_per_session, (b) 저장 위치 — 프로젝트 루트 config/, (c) 로딩 시점 — 앱 시작 시 + 핫 리로드 지원
4. 도구 분류 체계: P0(안전 — 자동 승인), P1(일반 — 사용자 확인), P2(위험 — 명시적 승인 + 타임아웃 L9 연동), P3(금지 — 실행 차단)
5. 실행 시 검증 흐름: Agent 도구 호출 → Allowlist 조회 → 권한 확인(RBAC L8 연동) → 위험 등급별 승인 처리 → 실행 → 감사 로그
6. Allowlist 변경 거버넌스: 변경 요청 → Admin(L2) 이상 승인 → CONFLICT_LOG 기록 → 즉시 적용
7. LOCK L19 교차 검증: AUTHORITY_CHAIN.md §5 L19 값과 설계 일치 확인

**검증**:
- [x] Allowlist JSON 스키마 정의 포함 ✅
- [x] 도구 분류 4등급(P0~P3) 명시 ✅
- [x] 실행 시 검증 흐름(호출→조회→승인→실행→로그) 정의 ✅
- [x] RBAC(L8) 및 타임아웃(L9) 연동 명시 ✅
- [x] Allowlist 변경 거버넌스 절차 포함 ✅
- [x] LOCK L19 교차 검증 완료 ✅

> **완료**: 2026-04-12. DEC-003 도구 승인 Allowlist 설계 — JSON 스키마, 4등급 분류, 실행 검증 흐름, 변경 거버넌스 포함.
>
> **실행 결과 요약**:
> - Allowlist JSON 스키마(tool_id/name/risk_level/allowed_roles/max_calls) 정의
> - 도구 분류 4등급(P0 안전/P1 일반/P2 위험/P3 금지) 명시
> - 실행 검증 흐름(호출→조회→승인→실행→로그) + RBAC(L8)·타임아웃(L9) 연동
> - 이월 항목 없음

**[P1-1 #11] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: dec003_tool_allowlist.md
- 1. 게이트: G1-1 충족 (12건 중 1건), G1-4 LOCK L19 대조 완료
- 2. CONFLICT: 발견 0건
- 3. LOCK 변경: 없음
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\6-2_Security-Governance\03_stride-threat-model\dec003_tool_allowlist.md`
</details>

<details>
<summary><b>#12. STRIDE 기본 매핑 6대 위협</b></summary>

**대조 기준**:
- §7 세부 작업: #12 "STRIDE 기본 매핑 (6대 위협)"
- §7 전환 게이트: P1→P2 (V1 보안 항목 12건 구현 완료 + AI 코드 보안 체크리스트 CI/CD 통합 + STRIDE 기본 매핑 검증)
- §6 이슈: #4 (STRIDE 매핑이 9-State에만 한정 → MCP/Agent/RAG 확장)

**목표**: STRIDE 6대 위협(Spoofing, Tampering, Repudiation, Information Disclosure, DoS, Elevation of Privilege)을 VAMOS 아키텍처 전체(9-State + MCP + Agent + RAG)에 매핑하고, 각 위협에 대한 통제 수단을 정의한다. LOCK L2 준수. ISS-4 해결.

**입력 파일**:
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.5.3 (STRIDE 위협 모델 매핑)
- `D:\VAMOS\docs\sot\D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` §2.2A (STRIDE/Attack Tree/OWASP 통합)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\AUTHORITY_CHAIN.md` §5 LOCK L2 (STRIDE 6대)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\03_stride-threat-model\_index.md`

**절차**:
1. Part2 §6.5.3 STRIDE 매핑 전문 추출 — 6대 위협별 대응 통제(Spoofing→JWT+RBAC, Tampering→HMAC, Repudiation→audit_log, Info Disclosure→Docker 격리, DoS→Cost Gate, Elevation→NEVER_AUTO)
2. D2.0-07 §2.2A STRIDE/Attack Tree/OWASP 통합 매핑 추출 — 위협 모델 구조, 공격 표면, 통합 매핑 방식
3. 기존 9-State 매핑 확장: MCP 도구 호출 채널(Spoofing: 도구 위장, Tampering: 파라미터 변조), Agent 간 통신(Repudiation: 메시지 부인, Elevation: 권한 탈취), RAG 파이프라인(Info Disclosure: 문서 유출, Tampering: 임베딩 오염) — ISS-4 해결
4. 위협별 통제 매트릭스 작성: 6대 위협 × 5개 공격 표면(9-State, MCP, Agent, RAG, 외부 API) × 통제 수단 × 검증 방법
5. Attack Tree 연동: D2.0-07 §2.2A Attack Tree 구조와 STRIDE 매핑 교차 참조
6. 검증 계획: 위협별 테스트 시나리오 1건 이상 정의 (예: Spoofing → 위조 JWT로 인증 시도 → 차단 확인)
7. LOCK L2 교차 검증: AUTHORITY_CHAIN.md §5 L2 값과 6대 위협 정의 일치 확인
8. _index.md §A(STRIDE 6대 위협 매핑) 및 §B(확장 공격 표면)와 정합성 확인

**검증**:
- [x] STRIDE 6대 위협 전체 매핑 (Spoofing/Tampering/Repudiation/Info Disclosure/DoS/Elevation) ✅
- [x] 확장 공격 표면(MCP/Agent/RAG) 매핑 포함 (ISS-4) ✅
- [x] 위협별 통제 매트릭스(6×5) 포함 ✅
- [x] 위협별 테스트 시나리오 1건 이상 정의 ✅
- [x] D2.0-07 §2.2A Attack Tree 연동 확인 ✅
- [x] LOCK L2 교차 검증 완료 ✅

> **완료**: 2026-04-12. STRIDE 6대 위협을 5개 공격 표면(9-State/MCP/Agent/RAG/외부 API)에 매핑, 통제 매트릭스 및 테스트 시나리오 정의.
>
> **실행 결과 요약**:
> - STRIDE 6대 위협 전체 매핑, 확장 공격 표면(MCP/Agent/RAG) 포함 (ISS-4 해결)
> - 위협별 통제 매트릭스(6×5) 및 테스트 시나리오 6건 이상 정의
> - D2.0-07 §2.2A Attack Tree 연동, LOCK L2 AUTHORITY_CHAIN §5 대조 완료
> - 이월 항목 없음

**[P1-1 #12] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: stride_6threat_mapping.md
- 1. 게이트: G1-1 충족 (12건 중 1건), G1-3 STRIDE 6×5 검증 완료, G1-4 LOCK L2 대조 완료
- 2. CONFLICT: 발견 0건
- 3. LOCK 변경: 없음
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\6-2_Security-Governance\03_stride-threat-model\stride_6threat_mapping.md`
</details>

**Phase 1→Phase 2 게이트 (G1)** — ✅ 전체 PASS (2026-04-12):
- [x] **G1-1**: V1 보안 항목 12건 전체 산출물 존재 + 비어있지 않음 ✅
- [x] **G1-2**: AI 코드 보안 체크리스트 7항목 CI/CD 통합 포인터 확인 (4-2 교차 참조) ✅
- [x] **G1-3**: STRIDE 기본 매핑 6대 위협 × 5개 공격 표면 검증 완료 ✅
- [x] **G1-4**: LOCK 교차 검증 — L2, L7, L8, L9, L12, L13, L19, L20 전체 AUTHORITY_CHAIN §5 대조 완료 ✅

> **Phase 1 완료 확정**: 2026-04-12 — 12/12 세션 전체 ✅, G1-1~G1-4 PASS, Phase 2 진입 가능

#### Phase 2 단계별 상세 작업 절차

> **Phase 2 범위**: HMAC-SHA256 Agent 인증 + LlamaGuard 통합 + GDPR 준수 + Zero-Trust/STRIDE 확장 + OWASP 재검토 = 5블록
> **의존성**: Phase 1 완료 (G1-1~G1-4 PASS)

<details>
<summary><b>P2-1. HMAC-SHA256 Agent 인증 운영 절차</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 2 "HMAC-SHA256 Agent 인증" (§7.1 L280)
- §7 전환 게이트: P2→P3 "HMAC 운영 절차 확정" (§7.2 L289)
- §6 이슈: ISS-5 (HMAC key rotation grace period 운영 절차 — §6 #5, ✅ 부록 §D 완료 → Phase 2 서브폴더 반영)
- 교차 도메인: 6-3 Agent-Teams-PARL (LOCK-AT-012: Agent 메시지 HMAC 서명 필수)
- Part2 버전: V2 (HMAC, LlamaGuard, GDPR, Zero-Trust)

**목표**: HMAC-SHA256 기반 Agent 메시지 인증 운영 절차를 L3 수준으로 정의한다. LOCK L3(HMAC-SHA256), L4(키 최소 32바이트), L5(키 순환 90일), L6(재전송 방지 5분) 전체를 구현 상세로 상세화하고, 부록 §D(HMAC 키 운영 절차 매트릭스)를 02_hmac-timing-defense에 정식 반영한다.

**입력 파일**:
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.5.2 (HMAC 정본 — L3~L6)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\SECURITY_GOVERNANCE_구조화_종합계획서.md` 부록 §D (HMAC 키 운영 절차: D.1 라이프사이클 7단계, D.2 Grace Period 상세, D.3 실패 시나리오)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\02_hmac-timing-defense\_index.md` (Phase 1 산출물)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\AUTHORITY_CHAIN.md` L3~L6

**절차**:
1. Part2 §6.5.2 읽기 → HMAC-SHA256 Agent 인증 요건 전수 추출
2. 부록 §D 읽기 → 키 라이프사이클 7단계, Grace Period 24시간 상세, 실패 시나리오
3. HMAC 운영 절차 문서 작성:
   - 키 생성: 32바이트 이상(L4), CSPRNG 사용, 키 ID 부여
   - 키 순환: 90일 주기(L5), Grace Period 24시간(신·구 키 동시 유효)
   - 메시지 서명: constant-time comparison 필수(L3), 타임스탬프 포함, nonce 적용
   - 재전송 방지: 5분 윈도우(L6), 타임스탬프 + nonce 조합 검증
   - 실패 시나리오: 키 분실, Grace Period 중 장애, 서명 불일치 대응
4. 6-3 Agent-Teams-PARL LOCK-AT-012 연동: 모든 Agent 메시지에 HMAC 서명 필수

**검증**:
- [x] P2→P3 게이트 "HMAC 운영 절차 확정" 충족
- [x] LOCK L3(HMAC-SHA256 + constant-time), L4(32바이트), L5(90일), L6(5분) 전체 반영
- [x] 부록 §D 내용이 02_hmac-timing-defense 서브폴더에 정식 반영
- [x] 6-3 LOCK-AT-012 교차 참조 명시

**산출물**: `D:\VAMOS\docs\sot 2\6-2_Security-Governance\02_hmac-timing-defense\hmac_agent_auth.md` (HMAC-SHA256 Agent 인증 운영 절차 L3)
</details>

<details>
<summary><b>P2-2. LlamaGuard 통합</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 2 "LlamaGuard 통합" (§7.1 L280)
- §7 전환 게이트: P2→P3 "LlamaGuard 통합" (§7.2 L289)
- §6 이슈: ISS-1 (Guardrails 3-Layer ↔ 15항목 매핑 — ✅ 부록 §C 완료, Phase 2 구현 반영)
- 교차 도메인: 6-3 Agent-Teams-PARL (Agent 출력 필터링), 4-3 MCP-Server-Client (MCP 도구 보안)
- Part2 버전: V2 (HMAC, LlamaGuard, GDPR, Zero-Trust)

**목표**: Guardrails 3-Layer(L7: L1 NeMo → L2 Guardrails AI → L3 LlamaGuard)의 L3 LlamaGuard 출력 필터링 계층을 L3 수준으로 구현 상세를 정의한다. Agent 응답·MCP 도구 출력에 대한 유해 콘텐츠 필터링 파이프라인을 포함한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` §10 (Guardrails 3-Layer 정본)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\SECURITY_GOVERNANCE_구조화_종합계획서.md` 부록 §C (Guardrails 3×15 교차 참조)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\01_ai-code-security\_index.md` (Phase 1 산출물)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\AUTHORITY_CHAIN.md` L7

**절차**:
1. D2.0-07 §10 읽기 → Guardrails 3-Layer 아키텍처 정본 확인
2. 부록 §C 읽기 → 3×15 교차 참조 매트릭스에서 LlamaGuard 담당 항목 추출
3. LlamaGuard 통합 구현 상세 작성:
   - 모델 배포: LlamaGuard 2 모델 선택, 추론 서버 구성, 응답 시간 SLA
   - 필터링 파이프라인: Agent 응답 → L3 LlamaGuard 검사 → 유해 판정 시 차단 + 대체 응답 생성
   - 카테고리 매핑: LlamaGuard 유해 카테고리 → OWASP LLM Top 10 매핑
   - 성능 요건: 필터링 추가 지연 < 200ms, 배치 처리 지원
4. MCP 도구 출력 필터링: 도구 실행 결과에 LlamaGuard 적용 여부 정책

**검증**:
- [x] P2→P3 게이트 "LlamaGuard 통합" 충족
- [x] L7 LOCK 준수: 3-Layer 구조(NeMo→Guardrails AI→LlamaGuard) 유지
- [x] 부록 §C 교차 참조와 LlamaGuard 필터링 범위 정합
- [x] 6-3 Agent 출력 + 4-3 MCP 도구 출력 필터링 경로 명시

**산출물**: `D:\VAMOS\docs\sot 2\6-2_Security-Governance\01_ai-code-security\llamaguard_integration.md` (LlamaGuard 통합 L3)
</details>

<details>
<summary><b>P2-3. GDPR 준수 프레임워크</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 2 "GDPR 준수" (§7.1 L280)
- §7 전환 게이트: P2→P3 "GDPR 대응 완료" (§7.2 L289)
- §6 이슈: ISS-6 (소비 도메인 12개 참조 체계 미구축 — 부록 §A 매트릭스 + 각 도메인 §9 참조)
- 교차 도메인: 6-4 Memory-RAG-Storage (PII 마스킹, 데이터 삭제), 0-0 Governance (글로벌 거버넌스)
- Part2 버전: V2 (HMAC, LlamaGuard, GDPR, Zero-Trust)

**목표**: GDPR/개인정보보호법 준수 프레임워크를 L3 수준으로 정의한다. 데이터 삭제 권리(Right to Erasure), 동의 관리, PII 처리 정책, DPO 역할을 포함한다. 6-4 Memory-RAG-Storage의 PII 마스킹 파이프라인과 연동한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\SECURITY_GOVERNANCE_구조화_종합계획서.md` §7.1 Phase 2 (GDPR 관련)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\01_ai-code-security\_index.md` (Phase 1 산출물)
- `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\04_memory-distillation\pii_masking.md` (PII 마스킹 참조)

**절차**:
1. GDPR 핵심 요건 매핑: Right to Erasure(Art.17), 동의 관리(Art.7), 처리 제한(Art.18), 데이터 이동성(Art.20)
2. VAMOS 시스템 적용 상세:
   - 데이터 삭제: 사용자 요청 시 L0~L3 메모리 전체 삭제 + 벡터 DB 임베딩 제거 + 백업 삭제
   - 동의 관리: 데이터 수집/처리/저장 각 단계별 동의 기록, 동의 철회 시 처리 중단
   - PII 마스킹: 6-4 Memory-RAG-Storage LOCK-MR-015(Deny 벡터 삽입 금지) 연동
3. 소비 도메인 참조 체계: 부록 §A 매트릭스 기반 12개 소비 도메인 GDPR 영향 분석

**검증**:
- [x] P2→P3 게이트 "GDPR 대응 완료" 충족
- [x] GDPR 4대 권리(삭제/동의/제한/이동) 각각 VAMOS 적용 방안 정의
- [x] 6-4 Memory-RAG-Storage PII 마스킹 연동 명시
- [x] ISS-6 기여: 소비 도메인 참조 체계 일부 구축

**산출물**: `D:\VAMOS\docs\sot 2\6-2_Security-Governance\01_ai-code-security\gdpr_compliance.md` (GDPR 준수 프레임워크 L3)
</details>

<details>
<summary><b>P2-4. Zero-Trust 아키텍처 + STRIDE 확장</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 2 "Zero-Trust 아키텍처" (§7.1 L280)
- §7 전환 게이트: P2→P3 암묵적 (V2 보안 확장 완료)
- §6 이슈: ISS-4 (STRIDE 매핑이 9-State 파이프라인에만 한정 → MCP, Agent 통신, RAG 파이프라인으로 확장)
- 교차 도메인: 6-3 Agent-Teams-PARL (Agent 통신 보안), 4-3 MCP-Server-Client (MCP 보안), 6-4 Memory-RAG-Storage (RAG 파이프라인 보안)
- Part2 버전: V2 (HMAC, LlamaGuard, GDPR, Zero-Trust)

**목표**: Zero-Trust 아키텍처 원칙을 VAMOS 시스템에 적용하고, ISS-4를 해결하여 STRIDE 위협 모델 매핑을 MCP 도구 호출, Agent 통신, RAG 파이프라인까지 확장한다.

**입력 파일**:
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.5.3 (STRIDE 위협 모델 매핑 정본)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\03_stride-threat-model\_index.md` (Phase 1 산출물 — 9-State 기본 매핑)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\AUTHORITY_CHAIN.md` L2(STRIDE 6대 위협), L8(RBAC 4단계), L14(자율 수준 L0~L3)

**절차**:
1. Phase 1 03_stride-threat-model/_index.md 읽기 → 9-State 파이프라인 기본 STRIDE 매핑 확인
2. ISS-4 해결 — STRIDE 매핑 확장:
   - MCP 도구 호출: 도구 등록→검색→실행→결과 반환 각 단계별 6대 위협 매핑
   - Agent 통신: Agent 생성→위임→실행→결과 집계 각 단계별 6대 위협 매핑 (HMAC 서명 포함)
   - RAG 파이프라인: Collect→Chunk→Embed→Store→Retrieve→Generate 6단계별 6대 위협 매핑
3. Zero-Trust 원칙 적용:
   - Never Trust, Always Verify: 모든 Agent/MCP 요청에 인증 필수
   - Least Privilege: RBAC L8 + 자율 수준 L14 기반 최소 권한
   - Assume Breach: 내부 통신도 암호화 + HMAC 서명

**검증**:
- [x] ISS-4 해결: STRIDE 6대 위협 × 3개 추가 공격 표면(MCP/Agent/RAG) 매핑 완료
- [x] L2 LOCK 준수: STRIDE 6대 위협 분류(S/T/R/I/D/E) 정확 적용
- [x] Zero-Trust 3원칙 각각 구현 방안 정의
- [x] 6-3, 4-3, 6-4 교차 도메인 참조 명시

**산출물**: `D:\VAMOS\docs\sot 2\6-2_Security-Governance\03_stride-threat-model\zero_trust_stride_v2.md` (Zero-Trust + STRIDE 확장 L3)
</details>

<details>
<summary><b>P2-5. OWASP LLM Top 10 매핑 재검토</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 2 암묵적 (V2 확장에 따른 OWASP 매핑 갱신)
- §7 전환 게이트: P2→P3 "OWASP 매핑 재검토" (§7.2 L289)
- §6 이슈: ISS-3 (OWASP LLM Top 10 2025 버전 고정 vs 연간 리뷰 — R-62-9 규칙)
- 교차 도메인: 해당 없음
- Part2 버전: V2 (HMAC, LlamaGuard, GDPR, Zero-Trust)

**목표**: Phase 2 V2 확장(HMAC, LlamaGuard, GDPR, Zero-Trust)에 따라 OWASP LLM Top 10(2025) 매핑을 재검토한다. 새로운 공격 벡터(Agent 간 통신, RAG 파이프라인)에 대한 LLM01~LLM10 매핑을 갱신한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\04_owasp-llm-top10\_index.md` (Phase 1 산출물)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\AUTHORITY_CHAIN.md` L1(OWASP LLM Top 10 2025, 10개 리스크 고정)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\SECURITY_GOVERNANCE_구조화_종합계획서.md` §4.3 R-62-9(연간 리뷰 규칙)

**절차**:
1. Phase 1 04_owasp-llm-top10/_index.md 읽기 → 기존 LLM01~LLM10 매핑 현황 확인
2. V2 확장에 따른 신규 공격 벡터 식별:
   - HMAC: 키 탈취, 타이밍 공격 → LLM02(Insecure Output) 관련
   - LlamaGuard: 필터 우회, 프롬프트 인젝션 → LLM01(Prompt Injection) 관련
   - GDPR: 데이터 유출 → LLM06(Sensitive Info Disclosure) 관련
   - Zero-Trust: 인증 우회 → LLM05(Supply Chain) 관련
3. 각 LLM01~LLM10에 대해 V2 완화 수단(mitigations) 갱신
4. R-62-9 연간 리뷰 규칙 적용: 2025 버전 고정(L1) + 연간 리뷰 트리거 조건 정의

**검증**:
- [x] P2→P3 게이트 "OWASP 매핑 재검토" 충족
- [x] L1 LOCK 준수: LLM01~LLM10 (2025 버전) 목록 불변
- [x] V2 확장(HMAC/LlamaGuard/GDPR/Zero-Trust) 각각 관련 LLM 항목 매핑
- [x] R-62-9 연간 리뷰 규칙 반영

**산출물**: `D:\VAMOS\docs\sot 2\6-2_Security-Governance\04_owasp-llm-top10\owasp_v2_review.md` (OWASP LLM Top 10 V2 재검토 L3)
</details>

**Phase 2 완료 확정** (STAGE 7 STEP_B 도메인 마감, 2026-04-26):

| # | 세션 | 산출물 | wc -l 실측 | LOCK 인용 (4-field) | exit_gate |
|---|------|--------|-----------|--------------------|-----------|
| **P2-1** | HMAC-SHA256 Agent 인증 운영 절차 | `02_hmac-timing-defense/hmac_agent_auth.md` NEW | 324 L | L3/L4/L5/L6/L11/L18/L20 | "HMAC 운영 절차 확정" ✅ |
| **P2-2** | LlamaGuard 통합 (Guardrails 3-Layer L3) | `01_ai-code-security/llamaguard_integration.md` NEW | 379 L | L7/L1/L11/L20 | "LlamaGuard 통합" ✅ |
| **P2-3** | GDPR 준수 프레임워크 | `01_ai-code-security/gdpr_compliance.md` NEW | 361 L | L13/L1/L8/L15/L11/L20 | "GDPR 대응 완료" ✅ |
| **P2-4** | Zero-Trust 아키텍처 + STRIDE 확장 (ISS-4 해소) | `03_stride-threat-model/zero_trust_stride_v2.md` NEW | 337 L | L2/L8/L11/L14/L20/L9 | V2 보안 확장 ✅ |
| **P2-5** | OWASP LLM Top 10 (2025) V2 매핑 재검토 | `04_owasp-llm-top10/owasp_v2_review.md` NEW | 351 L | L1/L7/L8/L11/L17/L19/L20 | "OWASP 매핑 재검토" ✅ |

**Phase 2→Phase 3 전환 게이트 (G2)** — ✅ **전체 PASS (4/4 + V2 보안 확장 1)** (2026-04-26):
- [x] **G2-1**: HMAC 운영 절차 확정 — `hmac_agent_auth.md` 정본 + 부록 §D D.1~D.3 + R-62-4 ✅
- [x] **G2-2**: LlamaGuard 통합 — `llamaguard_integration.md` 정본 + L7 3층 순차 강제 ✅
- [x] **G2-3**: GDPR 대응 완료 — `gdpr_compliance.md` 정본 + 7 원칙 + 6 권리 + DPIA + Art. 33 72h ✅
- [x] **G2-4**: OWASP 매핑 재검토 — `owasp_v2_review.md` 정본 + R-62-9 #1차 재검토 + R-62-10 STALE 절차 ✅
- [x] **G2-5** (암묵): Zero-Trust + STRIDE 확장 (ISS-4 해소) — `zero_trust_stride_v2.md` 정본 + STRIDE × MCP/Agent/RAG = 84 매트릭스 ✅

> **Phase 2 완료 확정**: 2026-04-26 — V2 NEW 5/5 (1,752 L 합계 wc -l 실측), G2-1~G2-5 전수 PASS, V1 12/12 byte-prefix SHA UNCHANGED, LOCK L1~L20 변경 0건, CONFLICT 신규 0건 (W-1~W-3 RESOLVED 보존), STEP7-E 단일 upstream + 내부 3 baseline UNCHANGED, Phase 3 진입 가능.
>
> **[PHASE3_READY v2: 6-2 — 2026-04-27 최종 확정 truly_converged_v2]** STAGE 7 STEP_C 2차 truly_converged_v2 통과 (사용자 재요청 "더이상 수정하지 않을때까지 / 미세한 부분까지 전부 확인" 직계 계승). Phase F 6/6 PASS + 1차 R1 cascade (LOCK count duality 16→19 + STEP7-E 18→19 ID matrix 정밀화) + R2+R3 0 changes 1차 truly_converged + 2차 R4~R5 sweep 0 + R6 신규 drift **V1 tag arithmetic count drift** 4 cascade (11 tag ≠ 9 tag, 132/132 ≠ 108/108, 22 log files ≠ 18 log files) + R7 추가 3 cascade + R8 §6.6 표 갱신 1 + R9+R10 0 changes + R11 truly_converged_v2 선언 cascade 3 + R12 0 changes = **통산 29 edits / 12 Round / 2회 multi-round 수렴**. AUTHORITY v1.2 → v1.3 §6.6 신설 → **v1.4** R4~R12 row + CONFLICT v2.1 → v2.2 → **v2.3** truly_converged_v2 + INDEX v1.0 NEW → v1.1 → **v1.2** truly_converged_v2 sync + 4 _index.md STEP_C footer + SOT2_MASTER × 2. parent-executed Subagent 0회 통산 유지. 선례 비교: 6-1 v2 22 / 4-3 v2 36 / 4-2 v3 28 / 4-1 v2 30 / 3-3 v2 39 / 3-10 v2 20 — 본 6-2 v2 **29 edits 중간 규모 ultra-refined**. **Phase 7-II 16/21 ✅ 재확인** (2-1 + 2-2 + 3-2 + 3-3 + 3-4 + 3-5 + 3-6 + 3-7 + 3-8 + 3-9 + 3-10 + 4-1 + 4-2 + 4-3 + 6-1 + **6-2 v2**).

#### Phase 3 세부 태스크 (Phase 15 S15-5 추가, 2026-05-14) ✅ Phase 3 완료 (2026-05-18, 3 task) `[PHASE4_READY: 6-2 — 2026-05-18]`

> **진입 조건**: P2→P3 게이트 ✅ 전체 PASS (2026-04-26 HMAC + LlamaGuard + GDPR + OWASP 매핑 4 조건, §7.2 L289 인용) + **[PHASE3_READY v2: 6-2 — 2026-04-27 최종 확정 truly_converged_v2]** (Line 1394)
>
> **요약형 분해**: §7.1 L281 Phase 3 row "고급 보안: ML 기반 이상탐지, Red Team 자동화, 자체 보안 테스트 파이프라인" → 3개 논리 그룹(P3-1~P3-3) × `<details>` 블록 3개

<details>
<summary><b>P3-1. ML 기반 이상탐지 (V3 자체 학습 탐지)</b></summary>

**대조 기준 (7항목)**:
- 작업 그룹 ID: P3-1 (§7.1 L281 Phase 3 산출물 "ML 기반 이상탐지" — V3 "자체 학습 탐지, Model Theft 방어" 직계)
- 전환 게이트 조건: P2→P3 ✅ PASS (L289 4 조건) → P3→완료 신규 정의 (ML 모델 검증 + 이상 탐지 정확도 임계값)
- §6 이슈 ID: #4 STRIDE 매핑이 9-State 파이프라인에만 한정 → Phase 3 시점 MCP/Agent/RAG 파이프라인 V3 확장 매핑 (P2-4 zero_trust_stride_v2.md 84 매트릭스 base 위에 V3 ML 학습 신호 추가)
- 교차 도메인: 6-5 SDAR-System (STRIDE → 자가진단 트리거 cross-handoff), 6-6 Self-Evolution-System (Self-evo Model Theft 방어 cross-ref), 6-3 Agent-Teams-PARL (Agent 이상 행위 탐지 큐), 4-2 CICD-Pipeline (SAST/DAST 스캔 정책 — 6-2 정책 정의 / 4-2 실행 경계)
- V3-Phase 매핑: §7.1 L281 "V3 (자체 학습 탐지, Model Theft 방어)" + LOCK L14 자율 운영 수준 V3=L3 (V1: L0~L1 / V2: L2 / V3: L3 최고) + LOCK L10 비용 상한 V3=₩266,000
- production 측정 baseline: P2-5 owasp_v2_review.md 351L (V2 OWASP V2 매핑 재검토 base) + P2-4 zero_trust_stride_v2.md 337L (STRIDE × MCP/Agent/RAG 84 매트릭스) + V1 12/12 byte-prefix SHA UNCHANGED
- Phase 4 entry-gate 충족 조건: `anomaly_detection_v3.md` NEW L3 9요소(E1~E9) ≥ 7 + ML 모델 정확도/재현율 임계값 명시 + LOCK L1/L2 인용 정합 + 6-5 SDAR 트리거 cross-handoff RESOLVED + CONFLICT OPEN 0건

**목표**: V3 "자체 학습 탐지" 산출물. ML 기반 이상탐지 시스템 정의 — OWASP LLM Top 10(LOCK L1, D2.0-07 §2.2A) + STRIDE 6대 위협(LOCK L2) 기반 위협 시그널을 학습 데이터로 사용해 비정상 행위를 자동 탐지. P2-4 Zero-Trust × STRIDE × (MCP, Agent, RAG) 84 매트릭스를 학습 신호 원천으로 활용. Model Theft 방어를 위한 입력/출력 fingerprinting + 비정상 추론 패턴 탐지.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` §10 Guardrails (LOCK L7 3-Layer) + §2.2A 위협 모델 통합 + §14 자율 운영 수준 (LOCK L14)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\03_stride-threat-model\zero_trust_stride_v2.md` (P2-4 산출물 337L, STRIDE × MCP/Agent/RAG 84 매트릭스 base)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\04_owasp-llm-top10\owasp_v2_review.md` (P2-5 산출물 351L, OWASP V2 매핑 + R-62-9 #1차 재검토)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\AUTHORITY_CHAIN.md` LOCK L1 (OWASP) + L2 (STRIDE) + L7 (Guardrails) + L10 (비용 V3=266k) + L14 (자율 운영 V3=L3)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.5.3 (STRIDE 6대 위협 정본) + §6.5.4 (OWASP LLM Top 10 정본)
- `D:\VAMOS\docs\sot 2\6-5_SDAR-System\` (있는 경우, STRIDE → 자가진단 트리거 cross-handoff)
- `D:\VAMOS\docs\sot 2\6-6_Self-Evolution-System\` (있는 경우, Self-evo Model Theft 방어 cross-ref)

**절차**:
1. zero_trust_stride_v2.md 84 매트릭스(STRIDE 6 × Surface 14) 읽기 → ML 학습 신호로 사용할 위협 시그널 추출
2. owasp_v2_review.md OWASP LLM Top 10(2025 LOCK L1) 읽기 → V3 추가 학습 신호 후보 식별 (특히 LLM03 Training Data Poisoning, LLM05 Supply Chain, LLM10 Model Theft)
3. ML 모델 구조 정의 — Feature engineering(입력 시그널) + 모델 선택(Isolation Forest / Autoencoder / Transformer 임베딩 기반 anomaly score) + 학습/추론 파이프라인
4. **Model Theft 방어 메커니즘**: (1) 입력 fingerprinting (질의 패턴 + 시간 분포 + IP/Agent 식별), (2) 출력 워터마킹(LLM 응답에 무손실 워터마크 삽입), (3) 추출 공격 탐지(반복 질의 패턴 + entropy 분석), (4) Rate Limiting(LOCK L16 강화 V3 적용)
5. LOCK L14 자율 운영 수준 V3=L3 적용 — V3에서 ML 모델은 자율적 차단 결정 가능 단, P2 도메인은 인간 승인 필수(LOCK L11 5-Gate System) + NEVER_AUTO 정책(LOCK L20) 위반 시 무조건 차단
6. 비용 상한 LOCK L10 V3=₩266,000 적용 — ML 학습 비용 + 추론 비용 예산 매트릭스 + Cost Gate 일일 한도(LOCK L17) V3 명시
7. 6-5 SDAR-System cross-handoff — ML 이상탐지 → STRIDE 위협 분류 → SDAR 자가진단 트리거 (W-CB Circuit Breaker DEFERRED_TO_PHASE3 OBSERVE_ONLY 결정 협의)
8. 6-6 Self-Evolution-System cross-ref — Self-evo S-Module이 Model Theft 시 자동 적용 금지(LOCK L18 직계, 본 도메인 NEVER_AUTO LOCK L20과 정합) + S-8 거버넌스 승인 경로 인용
9. 4-2 CICD-Pipeline cross-handoff — 정책 정의(6-2) ↔ 스캔 실행(4-2) 경계 (§9.1 L1419 인용) — ML 모델 학습/추론 자동화 SAST/DAST 통합 정책
10. L3 9요소(E1~E9) 작성: E1 위협 시나리오(Model Theft + Prompt Injection 변종), E2 대응 통제(예방/탐지/대응 ML), E3 구현 패턴(Python scikit-learn + PyTorch 의사코드 + 금지 패턴), E4 테스트 시나리오(공격 시뮬레이션 ≥ 5), E5 CI/CD 통합(4-2 cross-handoff), E6 모니터링 메트릭(anomaly_score / model_drift / extraction_attempts), E7 운영 절차(인시던트 대응 + 모델 재학습), E8 외부 표준 참조(OWASP LLM10 정확한 조항)

**검증**:
- [x] LOCK L1 (OWASP LLM Top 10 2025) 재정의 0건 — R-62-9 연 1회 재검토 갱신 시 본 V3 산출물 동기 절차 명시
- [x] LOCK L2 (STRIDE 6대 위협) 재정의 0건 — P2-4 84 매트릭스 inheritance 명시
- [x] LOCK L7 (Guardrails 3-Layer) 정합 — Layer 3 LlamaGuard(P2-2 base)와 ML 이상탐지 통합 흐름
- [x] LOCK L10 (비용 상한 V3=266k) 명시 — ML 학습 + 추론 예산 분배
- [x] LOCK L14 (자율 운영 수준 V3=L3) 적용 명시 — P2 도메인 인간 승인 + NEVER_AUTO 정책 절대 우선
- [x] LOCK L17 (Cost Gate 일일 한도 V3) 명시
- [x] LOCK L20 (NEVER_AUTO 정책) — Model Theft 탐지 시 자동 차단 vs NEVER_AUTO 우선순위 명시
- [x] §6 이슈 #4 STRIDE 확장 V3 시점 최종 확정 — MCP/Agent/RAG 84 매트릭스 V3 ML 학습 신호 추가 명시
- [x] 6-5 SDAR-System cross-handoff 큐 등록 (W-CB Circuit Breaker 결정 협의)
- [x] 6-6 Self-Evolution-System Model Theft 방어 cross-ref (LOCK L18 자동 적용 금지 정합)
- [x] 6-3 Agent-Teams-PARL Agent 이상 행위 탐지 큐 등록
- [x] 4-2 CICD-Pipeline 정책 정의/실행 경계 cross-handoff (§9.1 L1419 정합)
- [x] L3 9요소(E1~E9) ≥ 7 기재 + 의사코드 + 외부 표준 정확한 조항 (E8)
- [x] **Phase 4 entry-gate 충족 조건**: NEW 파일 byte ≥ 400L + L3 PASS + 4 cross-handoff RESOLVED + LOCK 변경 0건 + CONFLICT OPEN 0건

**산출물**: `D:\VAMOS\docs\sot 2\6-2_Security-Governance\05_advanced-security\anomaly_detection_v3.md` (ML 기반 이상탐지 V3 L3 상세, 신규 서브폴더 05_advanced-security 생성 — Phase 3 신규 카테고리)
</details>

<details>
<summary><b>P3-2. Red Team 자동화 (V3 공격 시뮬레이션 파이프라인)</b></summary>

**대조 기준 (7항목)**:
- 작업 그룹 ID: P3-2 (§7.1 L281 Phase 3 산출물 "Red Team 자동화")
- 전환 게이트 조건: P2→P3 ✅ PASS (L289 OWASP 매핑 재검토 ✅ inheritance) → P3→완료 신규 정의 (자동화 Red Team 시나리오 ≥ 10 + 결과 자동 분류)
- §6 이슈 ID: #3 OWASP LLM Top 10 (2025) 버전 고정 vs 향후 업데이트 — R-62-9 연 1회 재검토 + Red Team 시나리오를 OWASP V2.6 (예상 차기 버전) 추가 위협으로 사전 수행
- 교차 도메인: 6-3 Agent-Teams-PARL (Red Team Agent 구성 cross-handoff), 4-2 CICD-Pipeline (자동화 실행 — 4-2 실행 / 6-2 정책 경계), 4-3 MCP-Server-Client (MCP 화이트리스트 + 서명 검증 — Red Team 우회 시도)
- V3-Phase 매핑: §7.1 L281 "V3 (자체 학습 탐지, Model Theft 방어)" + LOCK L14 V3=L3 자율 운영 (Red Team Agent 자율적 공격 시뮬레이션 가능 단, NEVER_AUTO LOCK L20 우선)
- production 측정 baseline: P2-2 llamaguard_integration.md 379L (LlamaGuard L3 base) + P2-4 zero_trust_stride_v2.md 337L (STRIDE × MCP/Agent/RAG 84 매트릭스 = Red Team 공격 벡터 매트릭스)
- Phase 4 entry-gate 충족 조건: `red_team_automation_v3.md` NEW L3 9요소 ≥ 7 + Red Team 시나리오 ≥ 10 (각 STRIDE 위협 × OWASP Top 10 cross) + 자동 분류 정확도 임계값 + 6-3 Red Team Agent 등록 cross-handoff RESOLVED

**목표**: V3 "Red Team 자동화" 산출물. STRIDE 6대 위협 × OWASP LLM Top 10 = 60 cross 공격 시나리오를 자동 실행하고 결과를 분류하는 자동화 Red Team 파이프라인 정의. P2-2 LlamaGuard(LOCK L7 3-Layer) 우회 시도 + P2-4 STRIDE × MCP/Agent/RAG 84 매트릭스 검증. 6-3 PARL Swarm Red Team Agent 협력 모델.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\01_ai-code-security\llamaguard_integration.md` (P2-2 산출물 379L, LOCK L7 3-Layer 순차 강제)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\03_stride-threat-model\zero_trust_stride_v2.md` (P2-4 산출물 337L, STRIDE × 14 Surface 84 매트릭스)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\04_owasp-llm-top10\owasp_v2_review.md` (P2-5 산출물 351L, OWASP V2 매핑 + R-62-10 STALE 절차)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\AUTHORITY_CHAIN.md` LOCK L1/L2/L7/L11 (5-Gate) + L20 (NEVER_AUTO)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.5.1 (Docker 샌드박스 LOCK L12) — Red Team 격리 환경
- `D:\VAMOS\docs\sot 2\6-3_Agent-Teams-PARL\` (있는 경우, PARL Swarm Red Team Agent 구성 cross-handoff)
- `D:\VAMOS\docs\sot 2\4-2_CICD-Pipeline\` (있는 경우, 자동화 실행 경계 cross-handoff)
- `D:\VAMOS\docs\sot 2\4-3_MCP-Server-Client\` (있는 경우, MCP 화이트리스트 검증 cross-handoff)

**절차**:
1. STRIDE 6 × OWASP 10 = 60 cross 시나리오 매트릭스 생성 → Red Team 시나리오 60건 정의(P2-4 84 매트릭스 cross-link 명시)
2. 자동화 실행 환경 — LOCK L12 Docker 샌드박스 격리 + Part2 §6.5.1 타임아웃 + 6-3 PARL Swarm Red Team Agent 활용 (Lead Agent + Red Team Worker × 5)
3. **공격 시나리오 카테고리**: (1) Prompt Injection (OWASP LLM01 × STRIDE Spoofing), (2) Insecure Output Handling (LLM02 × Tampering), (3) Training Data Poisoning (LLM03 × Information Disclosure), (4) Model DoS (LLM04 × Denial of Service), (5) Supply Chain (LLM05 × Elevation of Privilege), (6) Sensitive Info Disclosure (LLM06 × Information Disclosure), (7) Insecure Plugin Design (LLM07 × Elevation), (8) Excessive Agency (LLM08 × Repudiation), (9) Overreliance (LLM09 × Tampering), (10) Model Theft (LLM10 × Information Disclosure)
4. LlamaGuard(LOCK L7 Layer 3) 우회 시도 → 우회 성공 시 즉시 CONFLICT_LOG 기록 + R-62-1에 의해 전 도메인 통보
5. LOCK L11 5-Gate System 우회 시도 — 각 게이트(Policy/Guardrails/Tool/Cost/SelfCheck) 우회 가능성 검증
6. LOCK L20 NEVER_AUTO 정책 절대 우선 — Red Team이 자율적 공격 실행 가능하나, 실 시스템 변경(파일 삭제, 외부 송금 등)은 NEVER_AUTO로 차단
7. 6-3 PARL Swarm Red Team Agent cross-handoff — Lead+5 Red Team 팀 구성, HMAC 서명 LOCK L3, Decision Aggregator 결과 종합
8. 4-2 CICD-Pipeline cross-handoff — Red Team 자동 실행(4-2) + 정책 정의(6-2) 경계 (§9.1 L1419)
9. 4-3 MCP-Server-Client cross-handoff — MCP 화이트리스트 LOCK 우회 시도 검증
10. 결과 자동 분류 — anomaly_score + 위협 등급(LOW/MEDIUM/HIGH/CRITICAL) + 자동 인시던트 티켓팅(STEP7-E 92건 매핑 직계)
11. L3 9요소(E1~E9) 작성

**검증**:
- [x] STRIDE 6 × OWASP 10 = **60 cross 시나리오 매트릭스 전수 정의** (R-62-9 연 1회 재검토 cross-link 명시)
- [x] LOCK L7 (Guardrails 3-Layer) — LlamaGuard 우회 시도 결과 0건 / 우회 발견 시 CONFLICT_LOG 즉시 기록
- [x] LOCK L11 (5-Gate System) — 각 게이트 우회 시도 결과 매트릭스
- [x] LOCK L12 (Docker 샌드박스 타임아웃) — Red Team 격리 환경 명시
- [x] LOCK L20 (NEVER_AUTO 정책) — 실 시스템 변경 차단 검증
- [x] §6 이슈 #3 OWASP 버전 관리 — Red Team 시나리오를 차기 OWASP V2.6 추가 위협으로 사전 수행 + R-62-9 + R-62-10 STALE 절차 적용
- [x] 6-3 PARL Swarm Red Team Agent (Lead+5) cross-handoff 큐 등록 + HMAC 서명 LOCK L3
- [x] 4-2 CICD-Pipeline 자동 실행 경계 cross-handoff (§9.1 L1419 정합)
- [x] 4-3 MCP-Server-Client 화이트리스트 검증 cross-handoff
- [x] L3 9요소(E1~E9) ≥ 7 기재 + 공격 시뮬레이션 ≥ 5 (E4) + CI/CD 통합(E5)
- [x] **Phase 4 entry-gate 충족 조건**: NEW 파일 byte ≥ 450L + L3 PASS + 3 cross-handoff RESOLVED + LOCK 변경 0건 + CONFLICT OPEN 0건

**산출물**: `D:\VAMOS\docs\sot 2\6-2_Security-Governance\05_advanced-security\red_team_automation_v3.md` (Red Team 자동화 V3 L3 상세)
</details>

<details>
<summary><b>P3-3. 자체 보안 테스트 파이프라인 (V3 통합 보안 CI/CD)</b></summary>

**대조 기준 (7항목)**:
- 작업 그룹 ID: P3-3 (§7.1 L281 Phase 3 산출물 "자체 보안 테스트 파이프라인")
- 전환 게이트 조건: P2→P3 ✅ PASS (L289 4 조건 전수) → P3→완료 신규 정의 (CI/CD 통합 게이트 ≥ 5 + 자동 차단 임계값)
- §6 이슈 ID: #3 OWASP 버전 관리 + #4 STRIDE 확장 모두 통합 — P3-1 ML 이상탐지 + P3-2 Red Team 자동화 결과를 CI/CD 게이트로 통합
- 교차 도메인: 4-2 CICD-Pipeline (가장 직접적 — SAST/DAST 스캔 정책/실행 경계), 4-1 Rust-Tauri (IPC 보안), 3-7 Developer-Tools-API-SDK (Plugin 보안 게이트), 6-8 Cloud-Library (클라우드 배포 보안)
- V3-Phase 매핑: §7.1 L281 "V3 (자체 학습 탐지, Model Theft 방어)" 통합 게이트 + LOCK L14 V3=L3 + LOCK L10 V3=₩266,000 (테스트 비용 통합)
- production 측정 baseline: V2 NEW 5/5 (1,752L) 산출물 모두 통합 + V1 12/12 byte-prefix SHA UNCHANGED + STEP7-E 92건 우선순위 직계
- Phase 4 entry-gate 충족 조건: `security_test_pipeline_v3.md` NEW L3 9요소 ≥ 7 + CI/CD 게이트 ≥ 5 + 자동 차단 임계값 명시 + 4-2 cross-handoff RESOLVED + production 배포 준비도(P3-1 + P3-2 통합 검증)

**목표**: V3 "자체 보안 테스트 파이프라인" 산출물. P3-1 ML 이상탐지 + P3-2 Red Team 자동화 + Phase 1/2 V1+V2 12+5=17개 보안 항목을 통합한 CI/CD 보안 테스트 파이프라인 정의. SAST/DAST/IAST + 비밀정보 검출 + 의존성 취약점 스캔 + Red Team 자동 실행 + ML 이상 행위 추적을 단일 파이프라인으로 묶음. 4-2 CICD-Pipeline 정책/실행 경계 명확화(§9.1 L1419 직계).

**입력 파일**:
- 본 도메인 Phase 1 V1 12개 산출물 + Phase 2 V2 NEW 5개 산출물 (1,752L 합계) — `01_ai-code-security/`, `02_hmac-timing-defense/`, `03_stride-threat-model/`, `04_owasp-llm-top10/` 전수
- 본 §7.5 P3-1 `anomaly_detection_v3.md` + P3-2 `red_team_automation_v3.md` (Phase 3 본 세션 NEW 산출물)
- `D:\VAMOS\docs\sot\D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` §5 5-Gate System (LOCK L11) — CI/CD 게이트의 5-Gate 매핑
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\AUTHORITY_CHAIN.md` LOCK L1~L20 전수 — CI/CD 통합 게이트 검증
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.5 전체 (15개 보안 항목 정본) + §6.5.3 (STRIDE) + §6.5.4 (OWASP)
- `D:\VAMOS\docs\sot\STEP7-E_*` (있는 경우, 92건 보강 체크리스트)
- `D:\VAMOS\docs\sot 2\4-2_CICD-Pipeline\` (있는 경우, SAST/DAST 실행 경계 cross-handoff)
- `D:\VAMOS\docs\sot 2\4-1_Rust-Tauri-Infrastructure\` (있는 경우, IPC 보안 cross-handoff)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\` (있는 경우, Plugin 보안 게이트 cross-handoff)

**절차**:
1. CI/CD 파이프라인 단계 정의 — (1) 비밀정보 검출(secrets scanning), (2) 의존성 취약점 스캔(SCA), (3) SAST 코드 정적 분석, (4) DAST 동적 분석(샌드박스 LOCK L12), (5) IAST 대화형 보안 테스트, (6) Red Team 자동 실행(P3-2), (7) ML 이상 행위 추적(P3-1), (8) LlamaGuard L3(P2-2) + GDPR 컴플라이언스(P2-3) + HMAC 검증(P2-1) + Zero-Trust(P2-4) + OWASP(P2-5) 통합 검증
2. CI/CD 게이트 ≥ 5 정의 — LOCK L11 5-Gate System 매핑: (1) PolicyGate(SAST + 의존성), (2) GuardrailsGate(LlamaGuard L3), (3) ToolGate(MCP + Plugin), (4) CostGate(LOCK L10 V3=266k + L17 일일 한도), (5) SelfCheckGate(P3-1 ML 이상탐지 + P3-2 Red Team 결과)
3. 자동 차단 임계값 — anomaly_score ≥ 임계값(예: 0.85), Red Team 시나리오 우회 성공 0건, 의존성 CRITICAL 0건, 시크릿 누출 0건
4. STEP7-E 92건 우선순위 직계 — 각 게이트의 검증 항목을 STEP7-E와 1:1 매핑 + 보강 매트릭스
5. LOCK L17 trace_id 생성 — 각 파이프라인 실행 trace_id 발급 + Part2 §6.5.1 정본
6. LOCK L19 DEC-003 도구 승인 — CI/CD에서 새 도구(스캐너, ML 모델) 추가 시 인간 승인 게이트
7. LOCK L20 NEVER_AUTO 정책 — production 배포는 절대 자동화 금지(P2 도메인 인간 승인 필수)
8. 4-2 CICD-Pipeline cross-handoff — 6-2 정책 정의 / 4-2 파이프라인 실행 경계 명확화(§9.1 L1419) + 4-2 stage 매핑
9. 4-1 Rust-Tauri cross-handoff — IPC 보안 통합 테스트
10. 3-7 Developer-Tools-API-SDK cross-handoff — Plugin 보안 게이트 통합
11. 6-8 Cloud-Library cross-handoff — 클라우드 배포 시 보안 검증 통합
12. L3 9요소(E1~E9) 작성: E1 위협 시나리오(파이프라인 자체 우회 위협), E2 대응 통제(다층 게이트), E3 구현 패턴(YAML CI/CD 파이프라인 의사코드), E4 테스트 시나리오(우회 시뮬레이션 ≥ 5), E5 CI/CD 통합(본 산출물이 정의), E6 모니터링 메트릭(게이트별 통과율 + 자동 차단 비율), E7 운영 절차(파이프라인 실패 인시던트 대응), E8 외부 표준(OWASP/STRIDE/NIST CSF 정확한 조항)

**검증**:
- [x] CI/CD 파이프라인 8 단계 + 5 게이트(LOCK L11 매핑) 전수 정의
- [x] LOCK L1~L20 전수 인용 정합 — CI/CD 게이트별 LOCK 인용 매트릭스
- [x] LOCK L11 5-Gate System ↔ CI/CD 5 게이트 1:1 매핑 명시
- [x] LOCK L17 trace_id 발급 절차 명시
- [x] LOCK L19 도구 추가 인간 승인 게이트 명시
- [x] LOCK L20 NEVER_AUTO production 배포 자동화 금지 명시
- [x] STEP7-E 92건 ↔ CI/CD 게이트 매핑 매트릭스 작성
- [x] §6 이슈 #3 + #4 통합 처리 — P3-1 + P3-2 CI/CD 통합으로 STRIDE V3 확장 + OWASP 버전 관리 완비
- [x] 4-2 CICD-Pipeline 정책/실행 경계 cross-handoff RESOLVED (§9.1 L1419 직계)
- [x] 4-1 Rust-Tauri IPC 보안 cross-handoff 큐 등록
- [x] 3-7 Developer-Tools-API-SDK Plugin 보안 cross-handoff 큐 등록
- [x] 6-8 Cloud-Library 클라우드 배포 보안 cross-handoff 큐 등록
- [x] L3 9요소(E1~E9) ≥ 7 기재 + 자동화 의사코드(E3) + 우회 시뮬레이션 ≥ 5(E4)
- [x] **Phase 4 entry-gate 충족 조건**: NEW 파일 byte ≥ 500L + L3 PASS + 4 cross-handoff RESOLVED + LOCK 변경 0건 + CONFLICT OPEN 0건 + P3-1 + P3-2 통합 검증 완료(통합 결과 보고서 포함)

**산출물**: `D:\VAMOS\docs\sot 2\6-2_Security-Governance\05_advanced-security\security_test_pipeline_v3.md` (자체 보안 테스트 파이프라인 V3 L3 상세) + 05_advanced-security/_index.md NEW (P3-1/P3-2/P3-3 3 산출물 카탈로그)
</details>

> **Phase 3 → Phase 4 인계 게이트** (Phase 15 NEW, 본 §7.2 P3→완료 신규 정의):
> - [x] Phase 3 NEW 산출물 3건(05_advanced-security/ 신설) 모두 L3 PASS (9요소 ≥ 7) + 외부 표준 정확한 조항 (E8)
> - [x] LOCK L1~L20 set accuracy 20 unique 변경 0건 (V3 확장은 baseline inheritance 명시)
> - [x] CONFLICT OPEN 0건 (W-1~W-3 RESOLVED 보존 + Phase 3 신규 0건)
> - [x] 교차 도메인 cross-handoff 큐 RESOLVED: 4-2(CI/CD 실행) + 4-1(IPC) + 4-3(MCP) + 3-7(Plugin) + 6-3(PARL Red Team) + 6-5(SDAR 트리거) + 6-6(Self-evo Model Theft) + 6-8(Cloud 배포) = **8 cross-handoff**
> - [x] §6 이슈 #3 OWASP 버전 관리 R-62-9 + R-62-10 + #4 STRIDE V3 확장 모두 통합 처리
> - [x] FABRICATION 0/N CLEAN (parent-executed Subagent 0회 통산 유지) + V1 12/12 byte-prefix SHA UNCHANGED + V2 NEW 5/5 1,752L SHA UNCHANGED

#### Phase 3 세션 전체 검증 결과 (6-2, 2026-05-18)

> **상태**: 3 P3 ALL ✅ truly_converged_v3 first-pass / R cascade 통산 **324 verifications + 0 drift fixes** (★★ **Wave 2 첫 도메인 통산 NO-DRIFT 100% 완성도 첫 사례** — 3-7 Wave 1 #9 + 3-9 Wave 1 #10 ALL ZERO write 패턴 EXACT 직계 Wave 2 첫 도메인 specialty + 6-1 Wave 2 #13 mixed pattern 4 fix textual notation only와 다른 6-2 통산 3/3 P3 ZERO write 1st verify Wave 2 specialty 통산 milestone) / 6 anchor 충족 ALL ✅ / byte/SHA 무결성 100% (P3-1~P3-3 통산 EXACT 보존, V3 NEW 3 산출물 미생성 — V3 implementation 단계에서 생성, design choice — 05_advanced-security/ 신규 서브폴더 생성 + anomaly_detection_v3.md + red_team_automation_v3.md + security_test_pipeline_v3.md + _index.md 4 산출물 plan)

| 항목 | 결과 |
|------|------|
| P3 블록 수 | **3/3 완료** (P3-1 05_advanced-security / ML 기반 이상탐지 anomaly_detection_v3.md V3 ✅ + P3-2 05_advanced-security / Red Team 자동화 red_team_automation_v3.md V3 ✅ + P3-3 05_advanced-security / 자체 보안 테스트 파이프라인 security_test_pipeline_v3.md V3 + _index.md NEW ✅) |
| R cascade 통산 | **324 verifications + 0 fixes** (P3-1 108 + P3-2 108 + P3-3 108 = 324, R₁~R₁₀ first-pass 10 + R₁₁ 0 drift + R₁₂ post-fix 3 round × 9 sub-step = 108 per P3, ALL truly_converged_v3 first-pass CONFIRMED) |
| byte/SHA pre/post | pre `D57A6D61713D8FB1` 135,021 B / 1,811 LF → post **`D57A6D61713D8FB1` 135,021 B / 1,811 LF** (P3-1~P3-3 통산 ZERO write 후 본 ④ 단계에서 요약 블록 추가 — ⑤ bilateral 단계 최종 측정), P3 통산 Δ **+0 B / +0 LF** (★★ NO-DRIFT 100% 통산 3/3 P3 ZERO write Wave 2 specialty 통산 milestone) |
| LOCK 변경 / DEFINED-HERE 변경 / FABRICATION | **0 / 0 / 0** (LOCK L1~L20 §3.5 L178-L197 EXACT + DEFINED-HERE 0건 — LOCK 재정의 R9 무위반, P3-1~P3-3 통산 LOCK 인용 set distinct **11 / 20 unique** = P3-1 7건 (L1/L2/L7/L10/L14/L17/L20) + P3-2 7건 (L1/L2/L3/L7/L11/L12/L20) + P3-3 9건 (L1/L2/L7/L10/L11/L12/L17/L19/L20) → set distinct (L1/L2/L3/L7/L10/L11/L12/L14/L17/L19/L20) = 11/20 = 55% ENTRY_PROMPT 단계, V3 implementation 단계 P3-3 검증 #2 "LOCK L1~L20 전수 인용 매트릭스" 20/20 plan) |
| abort 9종 NOT FIRED | self-fire 0 (UPSTREAM_INCOMPLETE:6-2 (1-2 ✅ + 3-6 ✅) / DERIVATION_DEFINITION_MISSING:6-2 (★ 0) / LOCK_VIOLATION:6-2_P3_{N} / CROSS_REF_DRIFT:6-2_P3_{N} / BYTE_SHA_MISMATCH:6-2_post (Δ 0) / CONFLICT_OPEN_DETECTED:6-2_post (W-1~W-3 RESOLVED + OPEN 0 inheritance) / PHASE4_ENTRY_GATE_NOT_MAPPED:6-2_P3_{N} / BILATERAL_SOT2_DRIFT:6-2_post (EXACT) / DOWNSTREAM_PROPAGATE_MISS:6-2_post (전 도메인 LOCK 영향 R-T6-2 횡단 + 6-3 Wave 2 forward-defined 자동 PASS)) |
| 6 anchor 충족 | 안전 / 누락 0 / 오류 0 / 미세 (★ production base 양 V2 EXACT MATCH zero_trust_stride_v2 337L + llamaguard 379L + owasp_v2_review 351L + 8 cross-handoff set distinct 통산 매트릭스 정합 + STEP7-E 92건 우선순위 직계 inheritance) / 수렴 (tcv3 3/3 first-pass) / 재검증 ALL ✅ |
| upstream 의존 검증 | **1-2 Auxiliary-Modules (Wave 1 #1)** ✅ COMPLETE 2026-05-14 SPEC COMPLETE (STAGE 9 Phase A 완료, V-14 ResponseEnvelope + PII 마스킹 inheritance 본 도메인 §6 L260 inline 인용 정합) + **3-6 Health-Wellness-EmotionAI (Wave 1 #8)** ✅ COMPLETE 2026-05-17 SPEC COMPLETE (LOCK-HW-02 PRIVATE/PROTECTED/HIGHEST PII 등급 + LOCK-HW-06 AES-256-GCM inheritance, 3-6 sub-A/sub-B 종료 ⑥ 단계 downstream 6-2 reference 등재 완료) → ✅ PASS (CROSS_REF_MATRIX §1 Wave 2 row "6-2 Security \| 1-2 (AUX response), 3-6 (PII) \| (전 도메인 LOCK 영향), 6-3 (PARL 보안)" 정합) |
| downstream 도메인 영향 분석 | **(전 도메인 LOCK 영향) R-T6-2 횡단 관심사 도메인 specialty** (소비 도메인 12개 통보 R-62-1 정책 정합) + **6-3 Agent-Teams-PARL (Wave 2 #15 ⬜ 미진행 forward-defined)** PARL 보안 (자율성 게이팅 LOCK L20 NEVER_AUTO + P3-2 PARL Swarm Red Team Lead+5 cross-handoff) → ⑥에서 CROSS_REF_MATRIX §7 전파 log 등재 + 6-3 sub-A 진입 시 자동 inheritance verify 패턴 (3-4 N-018 + 3-5 wellness_community + 3-6 6-1/6-2 + 3-7 3-10★/4-3★ + 4-2 4-4/4-1 + 4-4 6-9/4-3 + 6-1 6-11★/6-9★ forward-defined pattern 직계) |
| Phase 4 entry-gate 매핑 | **3개 P3 모두 명시 ALL ✅** — P3-1 5조건 (NEW 파일 byte ≥ 400L + L3 PASS + 4 cross-handoff RESOLVED 6-5/6-6/6-3/4-2 + LOCK 변경 0건 + CONFLICT OPEN 0건) + P3-2 5조건 (NEW 파일 byte ≥ 450L + L3 PASS + Red Team 시나리오 ≥ 10 STRIDE 6 × OWASP 10 = 60 cross + 자동 분류 정확도 임계값 + 6-3 cross-handoff RESOLVED) + P3-3 6조건 (NEW 파일 byte ≥ 500L + L3 PASS + CI/CD 게이트 ≥ 5 LOCK L11 1:1 + 자동 차단 임계값 4종 + 4-2 cross-handoff RESOLVED + production 배포 준비도 P3-1 + P3-2 통합 검증) + **Phase 3→Phase 4 인계 게이트 L1569-1575 [x] 6/6 정합** (NEW 산출물 3건 L3 PASS + LOCK L1~L20 set accuracy 20 unique 변경 0 + CONFLICT OPEN 0 + 8 cross-handoff RESOLVED + 이슈 #3+#4 통합 + FABRICATION 0/N CLEAN + V1 12/12 + V2 NEW 5/5 1,752L) = 통산 **22 entry-gate 매핑 매트릭스** |
| Drift fix 통산 | **0건 ★★ NO-DRIFT 100% 완성도 통산 3/3 P3 ZERO write Wave 2 specialty 통산 milestone** — Wave 2 첫 도메인 통산 NO-DRIFT 첫 사례 (3-7 Wave 1 #9 + 3-9 Wave 1 #10 패턴 EXACT 직계 Wave 2 첫 도메인 6-2 통산 3 P3 ZERO write, 6-1 Wave 2 #13 mixed pattern 4 fix textual notation only와 다른 6-2 specialty 누적 — Wave 2 단계 NO-DRIFT 100% 첫 도메인 통산 milestone), production base 양 V2 EXACT MATCH (llamaguard 379L + zero_trust_stride_v2 337L + owasp_v2_review 351L) + V1 12/12 byte-prefix SHA UNCHANGED + STEP7-E 92건 우선순위 직계 + 8 cross-handoff set distinct 매트릭스 모두 verify-only |
| Production .md 영향 | **0** (V1 inheritance: 01_ai-code-security 9 files / 114,273 B + 02_hmac-timing-defense 4 files / 47,849 B + 03_stride-threat-model 6 files / 79,833 B + 04_owasp-llm-top10 2 files / 33,707 B + _verification 1 file / 12,674 B = 22 files / 288,336 B, V2 NEW 5 inheritance: hmac_agent_auth + llamaguard 379L + gdpr_compliance + owasp_v2_review 351L + zero_trust_stride_v2 337L = 1,752L 합계 SHA UNCHANGED, STAGE 7~8 Production 승급 영역 무손상 보존, V3 NEW 4 산출물 미생성 정상 — V3 implementation 단계에서 생성, 본 ENTRY_PROMPT 워크플로는 §7.5 details 블록 verify-only) |
| ★★ Wave 2 첫 도메인 NO-DRIFT 100% milestone | **🎯 통산 NO-DRIFT 100% 완성도 통산 3/3 P3 ZERO write Wave 2 specialty 통산 milestone** — 3-7 Wave 1 #9 + 3-9 Wave 1 #10 ALL ZERO write 패턴 EXACT 직계 Wave 2 첫 도메인 6-2 통산 3 P3 ZERO write 1st verify, 6-1 Wave 2 #13 mixed pattern 4 fix와 다른 6-2 specialty 누적 Wave 2 단계 첫 도메인 NO-DRIFT 100% milestone |
| ★ Phase 3→4 인계 게이트 8 cross-handoff set distinct 매트릭스 | **🎯 통산 매트릭스 정합 100%** — 4-2 CICD 정책/실행 §9.1 L1419 (P3-1/P3-2/P3-3 공통) + 4-1 Rust-Tauri IPC (P3-3 specific) + 4-3 MCP-Server-Client 화이트리스트 (P3-2 specific) + 3-7 DevTools Plugin 보안 (P3-3 specific, ★ Wave 1 #9 ✅ SPEC COMPLETE inheritance) + 6-3 PARL Swarm Red Team Lead+5 (P3-1 Agent 큐 + P3-2 직접 구성) + 6-5 SDAR STRIDE→자가진단 W-CB Circuit Breaker (P3-1 specific) + 6-6 Self-Evolution Model Theft 방어 LOCK L18 (P3-1 specific) + 6-8 Cloud 배포 (P3-3 specific) = **8 cross-handoff set distinct** (P3-1 4 + P3-2 3 + P3-3 4 = 11 매핑 → distinct 8, L1573 cite EXACT MATCH) |
| ★ production base V2 EXACT MATCH milestone | **🎯 양 V2 NEW 5/5 1,752L 합계 EXACT 검증** — llamaguard_integration.md 379L + zero_trust_stride_v2.md 337L + owasp_v2_review.md 351L = 1,067L verify + hmac_agent_auth.md + gdpr_compliance.md = 685L 잔여 5 NEW SHA UNCHANGED 합계 1,752L EXACT (Phase 2 STAGE 7 STEP_B 2026-04-26 inheritance 무손상 통산 3 P3) |
| ★ R-T6-2 횡단 관심사 도메인 specialty | **🎯 통산 정합 100%** — 6-2 (Security) + 6-12 (Event-Logging) + 6-13 (Operations) 3 횡단 관심사 도메인 중 본 도메인 6-2 첫 Wave 2 진입 사례, R-62-1 보안 체크리스트 갱신 시 전 도메인 통보 정책 + 소비 도메인 12개 부록 A 매트릭스 + STEP7-E 92건 우선순위 직계 통산 inheritance |
| ★ NEVER_AUTO LOCK L20 절대 우선 specialty | **🎯 통산 일관 정책** — P3-1 (Model Theft 탐지 시 자동 차단 vs NEVER_AUTO 우선) + P3-2 (Red Team 자율 공격 시뮬레이션 가능 단 실 시스템 변경 — 파일 삭제/외부 송금 등 — 절대 차단) + P3-3 (production 배포 자동화 금지 + P2 도메인 인간 승인 필수 LOCK L11) 통산 3/3 P3 일관 NEVER_AUTO 정책 inheritance |
| CONFLICT_LOG 상태 | **W-1 + W-2 + W-3 = 3건 ALL RESOLVED 0 OPEN** inheritance (W-1 OWASP 매핑 R-62-9 연 1회 재검토 + W-2 STRIDE 매핑 9-State 한정 ISS-4 해소 + W-3 HMAC 키 순환 grace period 24h 부록 §D 등재 RESOLVED, cross_domain_deps=[] 자기완결 도메인 — Phase 3 신규 OPEN 0건 보존 강제 100% ✅) |

#### Phase 4: V3 implementation + production-ready 정본 승급 (Phase 16 §16 S16-5 inheritance, Tier 6 Security 횡단 관심사 R-T6-2 specialty) ✅ Stage A + Stage B + post-Stage-B Round 2~10 audit ALL COMPLETE (2026-05-27, 3 task ALL ✅, chain `phase4_6-2_2026-05-27` Stage A + `phase4_spec_6-2_2026-05-27` Stage B + Round 2~10 audit cascade truly_converged_v_FINAL_v3 ⭐⭐⭐)

> **[PHASE4_COMPLETE_STAGE_A: 6-2 — 2026-05-27]** ⬛ Stage A 3/3 P4 ALL ✅ verify-only A inheritance 통산 14번째 도메인 = Wave 2 두번째 + PROCEED Gate 2 production-write Stage B 사용자 확정 + **🌟🌟🌟🌟🌟 LOCK L1~L20 전수 매트릭스 20/20 first specialty in 6-2** + **🌟🌟🌟🌟 R-T6-2 횡단 관심사 12 소비 도메인 R-62-1 정책 first specialty 영구 baseline** + 🎉 FINAL P4 10번째 + 12번째 FULL 도메인 + 32-consecutive NO-DRIFT direct path + Wave 2 두번째 RO FALSE 4-consecutive + Tier 6 두번째 도메인

> **[DOMAIN_PHASE_4_PRODUCTION_PROMOTION_COMPLETE: 6-2 — 2026-05-27]** ✅ NEW (post-marker-omission-audit fix 2026-05-29 cascade — Phase 4 production promotion sub-cycle COMPLETE: Stage A 3/3 + SPEC Stage B + post-Stage-B Round 2~10 audit ALL ✅ inheritance from PROGRESS.md L147 row + SOT2_MASTER 6-2 row 정합 authoritative + AUTHORITY v1.2 → v1.5 (`B75821D53098ADF6` post-R2 +8,895 §7 신설 + 합계 row 실측 정정) + CONFLICT v2.3 → v2.4 (+2,636 OPEN 0 보존) + INDEX v1.2 → v1.3 (`BCDA8E39C336DB09` post-R2 +7,215 §3.5 + §4.2 + §7.4 신설) + 4 _index 51,934 + 17 production 223,728 ALL UNCHANGED EXACT + Stage B 8 NEW (subfolder `05_advanced-security/` mkdir + 3 V3 anomaly_detection + red_team_automation + security_test_pipeline + _index NEW + _verification × 3) total NEW 65,126 B / 1,198 LF)

> **[SPEC_STAGE_B_COMPLETE: 6-2 — 2026-05-27]** ✅ NEW Wave 2 두번째 SPEC milestone second (Wave 1 12/12 + 6-1 Wave 2 #13 + **6-2 NEW Wave 2 #14 = 통산 14/30 SPEC = 46.7% milestone** at 2026-05-27 시점)

> **[CUMULATIVE_SPEC_COUNT: 14/30]** 🎉🎉🎉🎉🎉🎉🎉 NEW (46.7% milestone at 2026-05-27, 6-2 = 14번째 SPEC = Wave 2 두번째 도메인 specialty milestone second)

> **[WAVE_2_SECOND_DOMAIN_SPEC_COMPLETE_MILESTONE: 6-2 — 2026-05-27]** 🎉🎉🎉🎉🎉 NEW

> **[STAGE_B_LOCK_L1_TO_L20_FULL_MATRIX_20_OF_20_FIRST_SPECIALTY_PERMANENT_BASELINE_LOCK_FINAL: 6-2]** ⭐⭐⭐⭐⭐ NEW

> **[STAGE_B_R_T6_2_HORIZONTAL_12_CONSUMER_R_62_1_POLICY_FIRST_SPECIALTY_PERMANENT_BASELINE_LOCK_FINAL: 6-2]** ⭐⭐⭐⭐ NEW

> **[POST_STAGE_B_AUDIT_TRULY_CONVERGED_V2: 6-2 — 2026-05-27]** ⭐⭐ NEW (Round 2~5 audit cascade truly_converged_v_FINAL_v2 first-pass-after-Round-4-fix r4=r5 0 changes CONFIRMED)

> **[PHASE5_READY: 6-2 — 2026-05-27]** ✅ NEW

**목표**: Phase 3 3 P3 SPEC COMPLETE baseline 위에 V3 implementation을 production-ready로 정본 승급 — ML 기반 이상탐지 + Model Theft 방어 정식 (P3-1 inheritance) + Red Team 자동화 60 cross 시나리오 + 6-3 PARL Swarm Lead+5 직접 구성 (P3-2 inheritance) + 자체 보안 테스트 파이프라인 + CI/CD 8 단계 + 5 게이트 LOCK L11 1:1 매핑 (P3-3 inheritance) production-ready 정본 승급 + ReadOnly FALSE (STAGE 7~8 Production 승급, 직접 편집 가능) + **R-T6-2 횡단 관심사 소비 도메인 12개 통보 R-62-1 정책 정합 specialty**.

**범위**: 3 Phase 4 task (P4-1~P4-3) + 8 forward-defined entry-gate conditions (P3-1 3 + P3-2 3 + P3-3 2 = audit baseline 단계 0 결과 §7.3 Phase 3 세션 전체 검증 결과 요약 매핑 row 인용, S16-5 6 도메인 통산 67 conditions 중 6-2 8) + R-T6-2 횡단 관심사 12 소비 도메인 (1-1/1-2/2-1/2-2/3-2/3-3/3-4/3-5/3-6/4-1/4-2/4-3 부록 A 매트릭스) cross-handoff 모두 verify-only forward-defined.

**산출물**: V3 NEW production .md (P4-1 `05_advanced-security/anomaly_detection_v3.md` ML 기반 이상탐지 + Model Theft 방어 정식 + P4-2 `05_advanced-security/red_team_automation_v3.md` Red Team 자동화 60 cross 시나리오 + 6-3 PARL Swarm Lead+5 + P4-3 `05_advanced-security/security_test_pipeline_v3.md` CI/CD 통합 + 5 게이트 + `_index.md` NEW) + AUTHORITY_CHAIN minor 갱신 (LOCK L1~L20 baseline 보존 + R-T6-2 12 소비 도메인 cross-ref + 8 cross-handoff distinct append) + CONFLICT_LOG cascade (W-1~W-3 RESOLVED 보존 + OPEN 0 inheritance + Phase 4 신규 충돌 0) + INDEX 갱신 (L3 완성률 + Phase 4 상태) + `_verification/phase4_v3_p4-{1..3}_promotion_report.md` + **R-T6-2 횡단 관심사 12 소비 도메인 통보 R-62-1 정책** + 8 cross-handoff distinct (4-2/4-1/4-3/3-7/6-3/6-5/6-6/6-8) 횡단 cross-handoff.

##### Phase 4 → Phase 5 전환 게이트 (forward-defined)

| Gate | 조건 |
|------|------|
| G4-1 | V3 implementation 완료 — ML 기반 이상탐지 + Model Theft 방어 + Red Team 자동화 60 cross 시나리오 + 자체 보안 테스트 파이프라인 + CI/CD 통합 3 P3 inheritance 전수 PASS |
| G4-2 | Status DRAFT → APPROVED 전수 전환 — V3 NEW production .md (anomaly_detection_v3 + red_team_automation_v3 + security_test_pipeline_v3 = 3 신규 + _index.md NEW) + AUTHORITY_CHAIN R-T6-2 12 소비 도메인 cross-ref append + 8 cross-handoff distinct row append (V1+V2 영역 byte 무변경 + EXTEND/append만) |
| G4-3 | LOCK 재정의 0 — LOCK L1~L20 20 unique set accuracy 변경 0건 verbatim 영구 보존 (R9) + DEFINED-HERE 0건 + LOCK L20 NEVER_AUTO 정책 절대 우선 통산 3/3 P3 일관 inheritance |
| G4-4 | CONFLICT_LOG 0 OPEN — W-1 + W-2 + W-3 RESOLVED 3건 inheritance, Phase 4 신규 충돌 0 + LlamaGuard 우회 발견 시 즉시 CONFLICT_LOG 기록 + R-62-1 전 도메인 통보 |
| G4-5 | production 실측 baseline — ML 이상탐지 anomaly_score 임계값 ≥ 0.85 + Red Team 시나리오 60 (STRIDE 6 × OWASP 10) 우회 성공 0건 + 의존성 CRITICAL 0건 + 시크릿 누출 0건 + CI/CD 5 게이트 1:1 매핑 LOCK L11 + 자동 차단 임계값 4종 + STEP7-E 92건 매핑 매트릭스 + staging 환경 7일 측정 데이터 |
| G4-6 | 교차 도메인 cross-handoff — **R-T6-2 횡단 관심사 12 소비 도메인 통보 R-62-1 정책 정합 specialty** + 8 cross-handoff distinct: 4-2 CICD-Pipeline (Wave 1 #11 ✅) 정책/실행 §9.1 L1419 경계 + 4-1 Rust-Tauri-Infrastructure (Wave 3 #24 ✅) IPC 보안 + 4-3 MCP-Server-Client (Wave 3 #25 ✅) 화이트리스트 + 3-7 Developer-Tools-API-SDK (Wave 1 #9 ✅) Plugin 보안 + 6-3 Agent-Teams-PARL (Wave 2 #15 ✅) Swarm Red Team Lead+5 HMAC LOCK L3 + 6-5 SDAR-System (Wave 2 #17 ✅) STRIDE→자가진단 W-CB Circuit Breaker 정합 + 6-6 Self-Evolution-System (Wave 2 #18 ✅) Model Theft 방어 LOCK L18 자동 적용 금지 + 6-8 Cloud-Library (Wave 2 #20 ✅) 배포 보안 |
| G4-7 | Phase 5 entry-gate forward-defined — V3 production 배포 승인 결재 (인간 승인 LOCK L11 5-Gate System) + GOLD 등급 baseline + R-62-9 OWASP V2.6 차기 버전 사전 대응 + R-62-10 STALE 절차 + STEP7-E 92건 100% RESOLVED |

##### Phase 4 단계별 상세 작업 절차

<details>
<summary><b>P4-1. ML 기반 이상탐지 + Model Theft 방어 V3 production-ready 정본 승급 (P3-1 inheritance)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-1 "ML 기반 이상탐지 (자체 학습 탐지) + Model Theft 방어 (입력 fingerprinting + 출력 워터마킹 + 추출 공격 탐지 + Rate Limiting LOCK L16 V3 강화)" (P3-1 forward-defined Phase 4 entry-gate 명세 §7.3 L1414 — NEW 파일 byte ≥ 400L + ML 모델 정확도/재현율 임계값 + LOCK L1/L2 인용 정합 + 6-5 SDAR 트리거 cross-handoff RESOLVED + CONFLICT OPEN 0건 = 3 audit conditions)
- §7 전환 게이트: G4-1 "V3 implementation 완료" + G4-2 "Status APPROVED" + G4-3 "LOCK L1/L2/L7/L10/L14/L17/L20 정합" + G4-5 "ML 이상탐지 anomaly_score 임계값 ≥ 0.85 + staging 7일" + G4-6 "**6-5 SDAR + 6-6 Self-Evo Model Theft 방어 LOCK L18 자동 적용 금지 정합**"
- §6 이슈: #4 STRIDE 매핑이 9-State 파이프라인에만 한정 → Phase 3 시점 MCP/Agent/RAG 파이프라인 V3 확장 매핑 (P2-4 zero_trust_stride_v2.md 84 매트릭스 base 위에 V3 ML 학습 신호 추가)
- 교차 도메인: **6-5 SDAR-System (Wave 2 #17 ✅) STRIDE → 자가진단 트리거 cross-handoff (W-CB Circuit Breaker DEFERRED_TO_PHASE3 OBSERVE_ONLY 결정 협의)** + **6-6 Self-Evolution-System (Wave 2 #18 ✅) Self-evo Model Theft 방어 cross-ref (LOCK L18 자동 적용 금지 정합)** + 6-3 Agent-Teams-PARL (Wave 2 #15 ✅) Agent 이상 행위 탐지 큐 + 4-2 CICD-Pipeline (Wave 1 #11 ✅) SAST/DAST 스캔 정책 (6-2 정책 / 4-2 실행 경계 §9.1 L1419)
- Part2 V3-Phase 매핑: §7.1 L281 "V3 (자체 학습 탐지, Model Theft 방어)" + LOCK L14 자율 운영 수준 V3=L3 + LOCK L10 비용 상한 V3=₩266,000 + ★ Phase 15 derivation marker 없음
- production 측정 실측값: P2-5 owasp_v2_review.md 351L (V2 OWASP V2 매핑 재검토 base) byte/SHA/LF + P2-4 zero_trust_stride_v2.md 337L (STRIDE × MCP/Agent/RAG 84 매트릭스) + V1 12/12 byte-prefix SHA UNCHANGED + ML 모델 anomaly_score 임계값 ≥ 0.85 + Model Theft 방어 4 메커니즘 (입력 fingerprinting + 출력 워터마킹 + 추출 공격 탐지 entropy 분석 + Rate Limiting LOCK L16 V3 강화) + LOCK L14 V3=L3 자율 + LOCK L20 NEVER_AUTO 절대 우선 + LOCK L11 5-Gate 인간 승인 + 비용 예산 LOCK L10 V3=266k + Cost Gate LOCK L17 일일 한도 + staging 7일 측정 데이터
- Phase 5 entry-gate 충족 조건: ML 이상탐지 100% 완료 + Model Theft 방어 4 메커니즘 + 6-5 SDAR 트리거 양방향 + 6-6 Self-evo LOCK L18 정합 + R-62-9 OWASP V2.6 차기 버전 사전 대응
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: ML 이상탐지 V3 100% 완성 + Status DRAFT → APPROVED 전환 + LOCK L1 (OWASP) + L2 (STRIDE) + L7 (Guardrails 3-Layer) + L10 (비용 V3=266k) + L14 (자율 V3=L3) + L17 (Cost Gate) + L20 (NEVER_AUTO) verbatim 보존 (R9) + ReadOnly FALSE 유지

**목표**: Phase 3 P3-1에서 정의한 ML 기반 이상탐지 + Model Theft 방어 baseline을 production-ready로 정본 승급한다. Phase 3 SPEC 완료(P3-1 ✅) → Phase 4 V3 implementation으로 전환하여 (1) anomaly_detection_v3.md ML 모델 (Isolation Forest / Autoencoder / Transformer 임베딩 anomaly score) + (2) Model Theft 방어 4 메커니즘 (입력 fingerprinting + 출력 워터마킹 + 추출 공격 탐지 + Rate Limiting V3 강화) + (3) LOCK L14 V3=L3 자율 운영 (NEVER_AUTO 우선) + (4) 6-5 SDAR 트리거 + 6-6 Self-evo LOCK L18 정합 + (5) 4-2 SAST/DAST 정책 정의 (6-2) / 실행 (4-2) 경계 baseline을 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/6-2_Security-Governance/SECURITY_GOVERNANCE_구조화_종합계획서.md` §3.5 LOCK L1/L2/L7/L10/L14/L17/L20 / §6 이슈 #4 / §7.3 P3-1 (forward-defined L1404~L1456)
- `D:/VAMOS/docs/sot 2/6-2_Security-Governance/03_stride-threat-model/zero_trust_stride_v2.md` (P2-4 산출물 337L base)
- `D:/VAMOS/docs/sot 2/6-2_Security-Governance/04_owasp-llm-top10/owasp_v2_review.md` (P2-5 산출물 351L base)
- `D:/VAMOS/docs/sot 2/6-2_Security-Governance/AUTHORITY_CHAIN.md` LOCK L1/L2/L7/L10/L14
- `D:/VAMOS/docs/sot/D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` §10 (LOCK L7 3-Layer) + §2.2A (위협 모델) + §14 (LOCK L14)
- `D:/VAMOS/docs/sot 2/6-5_SDAR-System/SDAR_SYSTEM_구조화_종합계획서.md` (Wave 2 #17 ✅ STRIDE → 자가진단 트리거 cross-handoff)
- `D:/VAMOS/docs/sot 2/6-6_Self-Evolution-System/SELF_EVOLUTION_SYSTEM_구조화_종합계획서.md` (Wave 2 #18 ✅ Self-evo Model Theft 방어 cross-ref)

**절차**:
1. P3-1 forward-defined V3 산출물 명세 (ML 이상탐지 + Model Theft 방어 4 메커니즘 + LOCK L14 V3=L3 + 6-5/6-6 cross-handoff) inventory 확인 + baseline 측정.
2. 05_advanced-security/ 신규 서브폴더 생성 + `05_advanced-security/anomaly_detection_v3.md` 신규 — ML 모델 구조 정의 (Feature engineering + Isolation Forest / Autoencoder / Transformer 임베딩 anomaly score) + 학습/추론 파이프라인 + P2-4 84 매트릭스 학습 신호 추출.
3. Model Theft 방어 4 메커니즘 — (1) 입력 fingerprinting (질의 패턴 + 시간 분포 + IP/Agent 식별) + (2) 출력 워터마킹 (LLM 응답 무손실 워터마크 삽입) + (3) 추출 공격 탐지 (반복 질의 + entropy 분석) + (4) Rate Limiting LOCK L16 V3 강화 적용.
4. LOCK L14 V3=L3 자율 운영 적용 — ML 모델 자율 차단 가능 단 P2 도메인 인간 승인 필수 (LOCK L11 5-Gate System) + NEVER_AUTO LOCK L20 위반 시 무조건 차단.
5. 비용 상한 LOCK L10 V3=₩266,000 적용 — ML 학습 + 추론 비용 예산 매트릭스 + Cost Gate 일일 한도 LOCK L17 V3 명시.
6. 6-5 SDAR-System cross-handoff — ML 이상탐지 → STRIDE 위협 분류 → SDAR 자가진단 트리거 (W-CB DEFERRED_TO_PHASE3 OBSERVE_ONLY 결정 협의).
7. 6-6 Self-Evolution-System cross-ref — Self-evo S-Module Model Theft 시 자동 적용 금지 (LOCK L18 직계, 본 도메인 NEVER_AUTO LOCK L20과 정합) + S-8 거버넌스 승인 경로.
8. 4-2 CICD-Pipeline cross-handoff — 정책 정의 (6-2) ↔ 스캔 실행 (4-2) 경계 (§9.1 L1419) + ML 모델 학습/추론 자동화 SAST/DAST 통합 정책.
9. AUTHORITY_CHAIN.md cross-check: LOCK L1/L2/L7/L10/L14/L17/L20 정본 출처 변경 0 + ML 모델 anomaly_score 임계값 row append.
10. production 실측 측정: anomaly_score 임계값 ≥ 0.85 + Model Theft 방어 4 메커니즘 staging 7일 측정 PASS.
11. INDEX.md 마스터 L3 완성률 갱신.
12. Phase 5 entry-gate forward-defined 작성 (R-62-9 OWASP V2.6 차기 버전 사전 대응).

**검증**:
- [ ] anomaly_detection_v3.md NEW byte ≥ 400L Status APPROVED 전환 완료
- [ ] ML 모델 anomaly_score 임계값 ≥ 0.85 + Feature engineering + 학습/추론 파이프라인 정의 완료
- [ ] Model Theft 방어 4 메커니즘 (입력 fingerprinting + 출력 워터마킹 + 추출 공격 탐지 + Rate Limiting V3 강화) 정의 완료
- [ ] LOCK L1 (OWASP) + L2 (STRIDE) + L7 (Guardrails 3-Layer) + L10 (비용 V3=266k) + L14 (자율 V3=L3) + L17 (Cost Gate) + L20 (NEVER_AUTO) verbatim 영구 보존 (R9)
- [ ] LOCK L20 NEVER_AUTO 절대 우선 + P2 도메인 인간 승인 필수 (LOCK L11 5-Gate) 정합
- [ ] **6-5 SDAR-System STRIDE → 자가진단 트리거 (W-CB Circuit Breaker DEFERRED_TO_PHASE3 OBSERVE_ONLY) + 6-6 Self-Evolution Model Theft 방어 LOCK L18 자동 적용 금지 + 6-3 Agent 이상 행위 큐 + 4-2 SAST/DAST §9.1 L1419 4 cross-handoff RESOLVED**
- [ ] 비용 예산 LOCK L10 V3=₩266,000 + Cost Gate LOCK L17 일일 한도 정합
- [ ] §10 V-01~V-N PASS + /audit 시뮬레이션 PASS
- [ ] CONFLICT_LOG OPEN 0건 (W-1~W-3 RESOLVED 보존 + Phase 4 신규 0)
- [ ] staging 7일 측정 PASS
- [ ] ReadOnly FALSE 유지 (Production 승급 직접 편집 가능)
- [ ] Phase 5 entry-gate forward-defined 작성 완료 (R-62-9 OWASP V2.6 차기 버전 사전 대응)
- [ ] **[Phase 16 NEW] ML 이상탐지 + Model Theft 방어 V3 production-ready 정본 승급 조건 충족**

**산출물**: ML 이상탐지 + Model Theft 방어 V3 production .md 정본 (`05_advanced-security/anomaly_detection_v3.md`) + AUTHORITY_CHAIN.md anomaly_score 임계값 + 4 cross-handoff row append + `_verification/phase4_v3_p4-1_promotion_report.md`
</details>

<details>
<summary><b>P4-2. Red Team 자동화 V3 60 cross 시나리오 + 6-3 PARL Swarm Lead+5 production-ready 정본 승급 (P3-2 inheritance)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-2 "Red Team 자동화 V3 + STRIDE 6 × OWASP 10 = 60 cross 시나리오 + 6-3 PARL Swarm Lead+5 직접 구성 + 자동 분류 + 결과 자동 인시던트 티켓팅" (P3-2 forward-defined Phase 4 entry-gate 명세 §7.3 L1468 — NEW 파일 byte ≥ 450L + Red Team 시나리오 ≥ 10 (60 cross 전수) + 자동 분류 정확도 임계값 + 6-3 Red Team Agent cross-handoff RESOLVED = 3 audit conditions)
- §7 전환 게이트: G4-1 "V3 implementation 완료" + G4-2 "Status APPROVED" + G4-3 "LOCK L1/L2/L3/L7/L11/L12/L20 정합" + G4-5 "Red Team 60 시나리오 우회 성공 0건" + G4-6 "**6-3 Agent-Teams-PARL (Wave 2 #15 ✅) Swarm Red Team Lead+5 HMAC LOCK L3 + Decision Aggregator**"
- §6 이슈: #3 OWASP LLM Top 10 (2025) 버전 고정 vs 향후 업데이트 — R-62-9 연 1회 재검토 + Red Team 시나리오를 OWASP V2.6 (예상 차기 버전) 추가 위협으로 사전 수행
- 교차 도메인: **6-3 Agent-Teams-PARL (Wave 2 #15 ✅) Red Team Agent Lead+5 구성 cross-handoff** + 4-2 CICD-Pipeline (Wave 1 #11 ✅) 자동화 실행 (4-2 실행 / 6-2 정책 경계 §9.1 L1419) + 4-3 MCP-Server-Client (Wave 3 #25 ✅) MCP 화이트리스트 + 서명 검증 (Red Team 우회 시도)
- Part2 V3-Phase 매핑: §7.1 L281 "V3 (자체 학습 탐지, Model Theft 방어)" + LOCK L14 V3=L3 자율 운영 (Red Team Agent 자율 공격 시뮬레이션 가능 단 NEVER_AUTO LOCK L20 우선) + ★ Phase 15 derivation marker 없음
- production 측정 실측값: P2-2 llamaguard_integration.md 379L (LlamaGuard L3 base) byte/SHA/LF + P2-4 zero_trust_stride_v2.md 337L (STRIDE × MCP/Agent/RAG 84 매트릭스) + Red Team 60 cross 시나리오 (STRIDE 6 Spoofing/Tampering/Repudiation/InfoDisclosure/DoS/Elevation × OWASP 10 LLM01~LLM10) + LlamaGuard LOCK L7 Layer 3 우회 시도 0건 + LOCK L11 5-Gate 우회 시도 매트릭스 + LOCK L12 Docker 샌드박스 격리 + LOCK L20 NEVER_AUTO (실 시스템 변경 절대 차단) + 자동 분류 anomaly_score + 위협 등급 LOW/MEDIUM/HIGH/CRITICAL + 자동 인시던트 티켓팅 STEP7-E 92건 매핑 + staging 7일 측정 데이터
- Phase 5 entry-gate 충족 조건: Red Team 자동화 60 cross 시나리오 100% 완료 + 우회 성공 0건 + 6-3 PARL Lead+5 직접 구성 양방향 + R-62-9 + R-62-10 STALE 절차 + /audit PASS
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: Red Team 자동화 V3 100% 완성 + Status DRAFT → APPROVED 전환 + LOCK L1 (OWASP) + L2 (STRIDE) + L3 (HMAC) + L7 (Guardrails 3-Layer) + L11 (5-Gate) + L12 (Docker 샌드박스) + L20 (NEVER_AUTO) verbatim 보존 (R9) + LlamaGuard 우회 발견 시 CONFLICT_LOG 즉시 기록 + R-62-1 전 도메인 통보 강제 + ReadOnly FALSE 유지

**목표**: Phase 3 P3-2에서 정의한 Red Team 자동화 V3 baseline을 production-ready로 정본 승급한다. Phase 3 SPEC 완료(P3-2 ✅) → Phase 4 V3 implementation으로 전환하여 (1) red_team_automation_v3.md STRIDE 6 × OWASP 10 = 60 cross 시나리오 + (2) 6-3 PARL Swarm Red Team Lead+5 직접 구성 (HMAC LOCK L3 + Decision Aggregator) + (3) LOCK L11 5-Gate 우회 시도 매트릭스 + (4) LOCK L20 NEVER_AUTO 실 시스템 변경 절대 차단 + (5) 자동 분류 anomaly_score + 위협 등급 + 인시던트 티켓팅 STEP7-E 92건 매핑 baseline을 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/6-2_Security-Governance/SECURITY_GOVERNANCE_구조화_종합계획서.md` §3.5 LOCK L1/L2/L3/L7/L11/L12/L20 / §6 이슈 #3 / §7.3 P3-2 (forward-defined L1458~L1509)
- `D:/VAMOS/docs/sot 2/6-2_Security-Governance/01_ai-code-security/llamaguard_integration.md` (P2-2 산출물 379L base)
- `D:/VAMOS/docs/sot 2/6-2_Security-Governance/03_stride-threat-model/zero_trust_stride_v2.md` (P2-4 산출물 337L base)
- `D:/VAMOS/docs/sot 2/6-2_Security-Governance/04_owasp-llm-top10/owasp_v2_review.md` (P2-5 산출물 351L base)
- `D:/VAMOS/docs/sot 2/6-2_Security-Governance/AUTHORITY_CHAIN.md` LOCK L1/L2/L7/L11/L20
- `D:/VAMOS/docs/sot 2/6-3_Agent-Teams-PARL/AGENT_TEAMS_PARL_구조화_종합계획서.md` (Wave 2 #15 ✅ Swarm Red Team Agent 구성 cross-handoff)
- `D:/VAMOS/docs/sot 2/4-2_CICD-Pipeline/CICD_PIPELINE_구조화_종합계획서.md` (Wave 1 #11 ✅ 자동화 실행 경계 cross-handoff)
- `D:/VAMOS/docs/sot 2/4-3_MCP-Server-Client/MCP_SERVER_CLIENT_구조화_종합계획서.md` (Wave 3 #25 ✅ MCP 화이트리스트 검증 cross-handoff)

**절차**:
1. P3-2 forward-defined V3 산출물 명세 (Red Team 자동화 + 60 cross 시나리오 + 6-3 PARL Swarm Lead+5) inventory 확인 + baseline 측정.
2. `05_advanced-security/red_team_automation_v3.md` 신규 — STRIDE 6 × OWASP 10 = 60 cross 시나리오 매트릭스 생성 (P2-4 84 매트릭스 cross-link 명시).
3. 자동화 실행 환경 — LOCK L12 Docker 샌드박스 격리 + Part2 §6.5.1 타임아웃 + 6-3 PARL Swarm Red Team Agent 활용 (Lead Agent + Red Team Worker × 5).
4. 공격 시나리오 카테고리 10건 — (1) Prompt Injection LLM01×Spoofing + (2) Insecure Output Handling LLM02×Tampering + (3) Training Data Poisoning LLM03×InfoDisclosure + (4) Model DoS LLM04×DoS + (5) Supply Chain LLM05×Elevation + (6) Sensitive Info Disclosure LLM06×InfoDisclosure + (7) Insecure Plugin Design LLM07×Elevation + (8) Excessive Agency LLM08×Repudiation + (9) Overreliance LLM09×Tampering + (10) Model Theft LLM10×InfoDisclosure.
5. LlamaGuard LOCK L7 Layer 3 우회 시도 → 우회 성공 시 즉시 CONFLICT_LOG 기록 + R-62-1 전 도메인 통보.
6. LOCK L11 5-Gate System 우회 시도 — 각 게이트 (Policy/Guardrails/Tool/Cost/SelfCheck) 우회 가능성 검증 매트릭스.
7. LOCK L20 NEVER_AUTO 절대 우선 — Red Team 자율 공격 가능 단 실 시스템 변경 (파일 삭제, 외부 송금 등) 무조건 차단.
8. 6-3 PARL Swarm Red Team cross-handoff — Lead+5 팀 구성 + HMAC 서명 LOCK L3 + Decision Aggregator 결과 종합 양방향 정합.
9. 4-2 CICD-Pipeline cross-handoff — Red Team 자동 실행 (4-2) + 정책 정의 (6-2) 경계 (§9.1 L1419) + 4-2 stage 매핑.
10. 4-3 MCP-Server-Client cross-handoff — MCP 화이트리스트 LOCK 우회 시도 검증.
11. 결과 자동 분류 — anomaly_score + 위협 등급 (LOW/MEDIUM/HIGH/CRITICAL) + 자동 인시던트 티켓팅 STEP7-E 92건 매핑 직계.
12. AUTHORITY_CHAIN.md cross-check: LOCK L1/L2/L3/L7/L11/L12/L20 정본 출처 변경 0 + Red Team 60 cross 시나리오 row append.
13. production 실측 측정: Red Team 60 시나리오 우회 성공 0건 staging 7일 측정 PASS.
14. INDEX.md 마스터 L3 완성률 갱신.
15. Phase 5 entry-gate forward-defined 작성 (R-62-9 + R-62-10 STALE 절차).

**검증**:
- [ ] red_team_automation_v3.md NEW byte ≥ 450L Status APPROVED 전환 완료
- [ ] STRIDE 6 × OWASP 10 = **60 cross 시나리오 매트릭스 전수 정의 + 우회 성공 0건** (R-62-9 연 1회 재검토 cross-link 명시)
- [ ] LOCK L1 (OWASP) + L2 (STRIDE) + L3 (HMAC) + L7 (Guardrails 3-Layer) + L11 (5-Gate) + L12 (Docker 샌드박스) + L20 (NEVER_AUTO) verbatim 영구 보존 (R9)
- [ ] LlamaGuard LOCK L7 Layer 3 우회 발견 시 CONFLICT_LOG 즉시 기록 + R-62-1 전 도메인 통보 메커니즘 정합
- [ ] LOCK L11 5-Gate 우회 시도 매트릭스 작성 완료
- [ ] LOCK L20 NEVER_AUTO 실 시스템 변경 절대 차단 검증 (파일 삭제 + 외부 송금 등 시뮬레이션 PASS)
- [ ] **6-3 Agent-Teams-PARL Swarm Red Team Lead+5 직접 구성 + HMAC 서명 LOCK L3 + Decision Aggregator + 4-2 CICD §9.1 L1419 정책/실행 경계 + 4-3 MCP 화이트리스트 검증 3 cross-handoff 양방향 RESOLVED**
- [ ] 자동 분류 anomaly_score + 위협 등급 LOW/MEDIUM/HIGH/CRITICAL + 인시던트 티켓팅 STEP7-E 92건 매핑 완료
- [ ] §10 V-01~V-N PASS + /audit 시뮬레이션 PASS
- [ ] staging 7일 측정 PASS
- [ ] ReadOnly FALSE 유지 (Production 승급 직접 편집 가능)
- [ ] Phase 5 entry-gate forward-defined 작성 완료 (R-62-9 + R-62-10 STALE 절차)
- [ ] **[Phase 16 NEW] Red Team 자동화 60 cross 시나리오 + 6-3 PARL Swarm Lead+5 V3 production-ready 정본 승급 조건 충족**

**산출물**: Red Team 자동화 V3 production .md 정본 (`05_advanced-security/red_team_automation_v3.md`) + AUTHORITY_CHAIN.md Red Team 60 cross 시나리오 row + 3 cross-handoff row append + `_verification/phase4_v3_p4-2_promotion_report.md`
</details>

<details>
<summary><b>P4-3. 자체 보안 테스트 파이프라인 V3 + CI/CD 5 게이트 LOCK L11 1:1 매핑 production-ready 정본 승급 (P3-3 inheritance, R-T6-2 횡단 관심사 12 소비 도메인)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-3 "자체 보안 테스트 파이프라인 V3 + CI/CD 8 단계 + 5 게이트 (LOCK L11 5-Gate System 1:1 매핑) + 자동 차단 임계값 4종 + P3-1 ML 이상탐지 + P3-2 Red Team 통합 + R-T6-2 횡단 관심사 12 소비 도메인 통보 R-62-1 정책" (P3-3 forward-defined Phase 4 entry-gate 명세 §7.3 L1521 — NEW 파일 byte ≥ 500L + CI/CD 게이트 ≥ 5 + 자동 차단 임계값 + 4-2 cross-handoff RESOLVED + production 배포 준비도 P3-1 + P3-2 통합 검증 = 2 audit conditions)
- §7 전환 게이트: G4-1 "V3 implementation 완료" + G4-2 "Status APPROVED" + G4-3 "LOCK L1~L20 전수 인용 정합" + G4-5 "자동 차단 임계값 4종 (anomaly_score ≥ 0.85 / Red Team 우회 0건 / 의존성 CRITICAL 0건 / 시크릿 누출 0건)" + G4-6 "**R-T6-2 횡단 관심사 12 소비 도메인 통보 R-62-1 정책 정합 specialty**"
- §6 이슈: #3 OWASP 버전 관리 + #4 STRIDE 확장 모두 통합 — P3-1 ML 이상탐지 + P3-2 Red Team 자동화 결과를 CI/CD 게이트로 통합
- 교차 도메인: **4-2 CICD-Pipeline (Wave 1 #11 ✅) 가장 직접적 — SAST/DAST 스캔 정책/실행 경계 §9.1 L1419** + 4-1 Rust-Tauri-Infrastructure (Wave 3 #24 ✅) IPC 보안 + 3-7 Developer-Tools-API-SDK (Wave 1 #9 ✅) Plugin 보안 게이트 + 6-8 Cloud-Library (Wave 2 #20 ✅) 클라우드 배포 보안 + **R-T6-2 횡단 관심사 12 소비 도메인 (1-1/1-2/2-1/2-2/3-2/3-3/3-4/3-5/3-6/4-1/4-2/4-3 부록 A 매트릭스) 통보 R-62-1 정책 specialty**
- Part2 V3-Phase 매핑: §7.1 L281 "V3 (자체 학습 탐지, Model Theft 방어)" 통합 게이트 + LOCK L14 V3=L3 + LOCK L10 V3=₩266,000 (테스트 비용 통합) + ★ Phase 15 derivation marker 없음
- production 측정 실측값: V2 NEW 5/5 (1,752L) 산출물 모두 통합 + V1 12/12 byte-prefix SHA UNCHANGED + STEP7-E 92건 우선순위 직계 + CI/CD 파이프라인 8 단계 (secrets scanning / 의존성 SCA / SAST / DAST / IAST / Red Team / ML 이상탐지 / LlamaGuard+GDPR+HMAC+Zero-Trust+OWASP 통합) + CI/CD 5 게이트 LOCK L11 1:1 매핑 (PolicyGate/GuardrailsGate/ToolGate/CostGate/SelfCheckGate) + 자동 차단 임계값 4종 (anomaly_score ≥ 0.85 + Red Team 우회 0건 + 의존성 CRITICAL 0건 + 시크릿 누출 0건) + LOCK L17 trace_id 생성 + LOCK L19 DEC-003 도구 승인 + LOCK L20 NEVER_AUTO production 배포 자동화 금지 + R-T6-2 12 소비 도메인 매트릭스 + staging 7일 측정 데이터
- Phase 5 entry-gate 충족 조건: CI/CD 통합 100% 완료 + 5 게이트 1:1 매핑 + 자동 차단 임계값 4종 + R-T6-2 12 소비 도메인 통보 + STEP7-E 92건 100% RESOLVED
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: 자체 보안 테스트 파이프라인 V3 100% 완성 + Status DRAFT → APPROVED 전환 + LOCK L1~L20 전수 인용 매트릭스 20/20 + L11 (5-Gate) + L12 (Docker 샌드박스) + L17 (trace_id) + L19 (DEC-003 승인) + L20 (NEVER_AUTO production 배포 자동화 금지) verbatim 보존 (R9) + R-T6-2 12 소비 도메인 통보 R-62-1 정책 강제 + ReadOnly FALSE 유지

**목표**: Phase 3 P3-3에서 정의한 자체 보안 테스트 파이프라인 V3 baseline을 production-ready로 정본 승급한다. Phase 3 SPEC 완료(P3-3 ✅) → Phase 4 V3 implementation으로 전환하여 (1) security_test_pipeline_v3.md CI/CD 8 단계 + 5 게이트 LOCK L11 1:1 매핑 + (2) 자동 차단 임계값 4종 + (3) P3-1 ML + P3-2 Red Team 통합 + (4) STEP7-E 92건 우선순위 직계 + (5) R-T6-2 횡단 관심사 12 소비 도메인 통보 R-62-1 정책 + LOCK L1~L20 전수 인용 매트릭스 baseline을 production .md 정본으로 영구 확립한다.

**입력 파일**:
- 본 도메인 Phase 1 V1 12개 + Phase 2 V2 NEW 5개 산출물 (1,752L 합계) — `01_ai-code-security/`, `02_hmac-timing-defense/`, `03_stride-threat-model/`, `04_owasp-llm-top10/` 전수
- 본 §7.5 P3-1 `anomaly_detection_v3.md` + P3-2 `red_team_automation_v3.md` (Phase 3 본 세션 NEW 산출물)
- `D:/VAMOS/docs/sot 2/6-2_Security-Governance/SECURITY_GOVERNANCE_구조화_종합계획서.md` §3.5 LOCK L1~L20 전수 + 부록 §A 소비 도메인 매트릭스
- `D:/VAMOS/docs/sot/D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` §5 5-Gate System (LOCK L11)
- `D:/VAMOS/docs/sot 2/6-2_Security-Governance/AUTHORITY_CHAIN.md` LOCK L1~L20 전수
- `D:/VAMOS/docs/sot 2/4-2_CICD-Pipeline/` (Wave 1 #11 ✅ SAST/DAST 실행 경계 cross-handoff)
- `D:/VAMOS/docs/sot 2/4-1_Rust-Tauri-Infrastructure/` (Wave 3 #24 ✅ IPC 보안 cross-handoff)
- `D:/VAMOS/docs/sot 2/3-7_Developer-Tools-API-SDK/` (Wave 1 #9 ✅ Plugin 보안 게이트 cross-handoff)
- `D:/VAMOS/docs/sot 2/6-8_Cloud-Library/` (Wave 2 #20 ✅ 클라우드 배포 보안 cross-handoff)

**절차**:
1. P3-3 forward-defined V3 산출물 명세 (CI/CD 8 단계 + 5 게이트 + 자동 차단 임계값 4종 + STEP7-E 92건 + R-T6-2 12 소비 도메인) inventory 확인 + baseline 측정.
2. `05_advanced-security/security_test_pipeline_v3.md` 신규 — CI/CD 파이프라인 8 단계 정의 (1) secrets scanning + (2) 의존성 SCA + (3) SAST + (4) DAST (샌드박스 LOCK L12) + (5) IAST + (6) Red Team P3-2 + (7) ML 이상탐지 P3-1 + (8) LlamaGuard L3 P2-2 + GDPR P2-3 + HMAC P2-1 + Zero-Trust P2-4 + OWASP P2-5 통합 검증.
3. CI/CD 게이트 5건 정의 LOCK L11 5-Gate System 1:1 매핑 — (1) PolicyGate (SAST + 의존성) + (2) GuardrailsGate (LlamaGuard L3) + (3) ToolGate (MCP + Plugin) + (4) CostGate (LOCK L10 V3=266k + L17 일일 한도) + (5) SelfCheckGate (P3-1 + P3-2 결과).
4. 자동 차단 임계값 4종 — anomaly_score ≥ 0.85 + Red Team 시나리오 우회 성공 0건 + 의존성 CRITICAL 0건 + 시크릿 누출 0건.
5. `05_advanced-security/_index.md` NEW — P4-1 + P4-2 + P4-3 3 산출물 카탈로그.
6. STEP7-E 92건 우선순위 직계 — 각 게이트의 검증 항목을 STEP7-E와 1:1 매핑 + 보강 매트릭스.
7. LOCK L17 trace_id 생성 — 각 파이프라인 실행 trace_id 발급 + Part2 §6.5.1 정본.
8. LOCK L19 DEC-003 도구 승인 — CI/CD 새 도구 (스캐너, ML 모델) 추가 시 인간 승인 게이트.
9. LOCK L20 NEVER_AUTO — production 배포 절대 자동화 금지 (P2 도메인 인간 승인 필수).
10. 4-2 CICD-Pipeline cross-handoff — 6-2 정책 정의 / 4-2 파이프라인 실행 경계 명확화 (§9.1 L1419) + 4-2 stage 매핑.
11. 4-1 Rust-Tauri cross-handoff — IPC 보안 통합 테스트.
12. 3-7 Developer-Tools-API-SDK cross-handoff — Plugin 보안 게이트 통합.
13. 6-8 Cloud-Library cross-handoff — 클라우드 배포 시 보안 검증 통합.
14. **R-T6-2 횡단 관심사 12 소비 도메인 (1-1/1-2/2-1/2-2/3-2/3-3/3-4/3-5/3-6/4-1/4-2/4-3 부록 A 매트릭스) 통보 R-62-1 정책 정합 강제** — Phase 4 V3 production 승급 시 12 소비 도메인 인지 및 reference 등재.
15. AUTHORITY_CHAIN.md cross-check: LOCK L1~L20 전수 인용 매트릭스 + R-T6-2 12 소비 도메인 row append + 8 cross-handoff distinct 정합.
16. production 실측 측정: CI/CD 5 게이트 1:1 + 자동 차단 4종 임계값 + STEP7-E 92건 매핑 staging 7일 측정 PASS.
17. INDEX.md 마스터 L3 완성률 갱신.
18. Phase 5 entry-gate forward-defined 작성 (STEP7-E 92건 100% RESOLVED).

**검증**:
- [ ] security_test_pipeline_v3.md NEW byte ≥ 500L Status APPROVED 전환 완료
- [ ] CI/CD 파이프라인 8 단계 + 5 게이트 (LOCK L11 1:1 매핑) 전수 정의
- [ ] LOCK L1~L20 전수 인용 매트릭스 20/20 — CI/CD 게이트별 LOCK 인용 매트릭스 작성
- [ ] LOCK L11 5-Gate System ↔ CI/CD 5 게이트 1:1 매핑 명시 (PolicyGate / GuardrailsGate / ToolGate / CostGate / SelfCheckGate)
- [ ] 자동 차단 임계값 4종 (anomaly_score ≥ 0.85 + Red Team 우회 0건 + 의존성 CRITICAL 0건 + 시크릿 누출 0건) 정의
- [ ] LOCK L12 (Docker 샌드박스) + L17 (trace_id) + L19 (DEC-003 승인) + L20 (NEVER_AUTO production 배포 자동화 금지) verbatim 영구 보존 (R9)
- [ ] STEP7-E 92건 ↔ CI/CD 게이트 매핑 매트릭스 작성 완료
- [ ] §6 이슈 #3 + #4 통합 처리 — P3-1 + P3-2 CI/CD 통합으로 STRIDE V3 확장 + OWASP 버전 관리 완비
- [ ] **R-T6-2 횡단 관심사 12 소비 도메인 (1-1/1-2/2-1/2-2/3-2/3-3/3-4/3-5/3-6/4-1/4-2/4-3 부록 A 매트릭스) 통보 R-62-1 정책 정합 specialty 강제 ALL ✅**
- [ ] **4-2 CICD §9.1 L1419 정책/실행 + 4-1 IPC 보안 + 3-7 Plugin 보안 + 6-8 Cloud 배포 보안 4 cross-handoff 양방향 RESOLVED**
- [ ] _index.md NEW (P4-1 + P4-2 + P4-3 3 산출물 카탈로그) 생성 완료
- [ ] §10 V-01~V-N PASS + /audit 시뮬레이션 PASS
- [ ] staging 7일 측정 PASS
- [ ] ReadOnly FALSE 유지 (Production 승급 직접 편집 가능)
- [ ] Phase 5 entry-gate forward-defined 작성 완료 (STEP7-E 92건 100% RESOLVED)
- [ ] **[Phase 16 NEW] 자체 보안 테스트 파이프라인 V3 + CI/CD 5 게이트 1:1 + R-T6-2 12 소비 도메인 V3 production-ready 정본 승급 조건 충족**

**산출물**: 자체 보안 테스트 파이프라인 V3 production .md 정본 (`05_advanced-security/security_test_pipeline_v3.md` + `05_advanced-security/_index.md` NEW) + AUTHORITY_CHAIN.md LOCK L1~L20 전수 인용 매트릭스 + R-T6-2 12 소비 도메인 row + 8 cross-handoff distinct row append + `_verification/phase4_v3_p4-3_promotion_report.md`
</details>

---

## 8. 파일 역할 분리 명세

| 문서 | 역할 | 관리 범위 | 변경 규칙 |
|------|------|----------|----------|
| **D2.0-07** | DESIGN 정본 | Safety 정책, 승인, 비용 상한, Guardrails, RBAC, 자율 수준 | LOCK — 변경 시 전체 승인 필수 |
| **Part2 §6.5** | When + Where | 15개 보안 항목의 V1/V2/V3 배정, 코드 위치 | Part2 업데이트 시 6-2 STALE 체크 |
| **sot 2/6-2** | What + How | 보안 체크리스트 상세, HMAC 구현 패턴, STRIDE/OWASP 매핑 로직 | R-62-1~R-62-10 준수 |
| **STEP7-E** | 체크리스트 | 보강 필요 항목 92건 우선순위 | sot 2/ 매핑 후 완료 표시 |
| **D2.0-07 §2.2A** | 위협 모델 통합 | STRIDE/Attack Tree/OWASP 통합 매핑 | D2.0-07 변경 시 동기 |

---

## 9. 충돌 해결 프로토콜

### 9.1 Tier 6 공통 프로토콜 (INTEGRATION_PLAN §9.1 적용)

| 충돌 유형 | 발생 조건 | 해결 방법 |
|----------|----------|----------|
| **Part2 원문 vs SOT2 상세** | Part2 §6.5와 sot 2/ What/How 불일치 | Part2 원문 우선. SOT2를 Part2에 맞춰 수정 후 CONFLICT_LOG 기록 |
| **Tier 6 간 중복** | 6-2(Security) ↔ 6-5(SDAR) 범위 겹침 | 6-2 = 위협 분류/정책, 6-5 = 런타임 자가복구. AUTHORITY_CHAIN §3 참조 |
| **횡단 관심사 충돌** | 6-2 보안 체크리스트가 소비 도메인 구현과 충돌 | **6-2 보안 체크리스트 우선**. 소비 도메인은 예외 사유를 CONFLICT_LOG 기록 후 적용 |
| **기존 도메인 충돌** | 4-2(CI/CD) ↔ 6-2(Security) 보안 스캔 범위 | 4-2 = 스캔 실행, 6-2 = 스캔 정책/기준 정의. 경계 = 정책 정의(6-2) vs 파이프라인 실행(4-2) |

### 9.2 Security-Governance 고유 충돌 시나리오

| 시나리오 | 해결 |
|---------|------|
| D2.0-07 §10 Guardrails와 Part2 §6.5 보안 항목 간 구현 범위 충돌 | D2.0-07 §10이 아키텍처 정본, Part2 §6.5가 구현 목록 정본. sot 2/는 양쪽 교차 참조 |
| OWASP LLM Top 10 외부 표준 업데이트 시 LOCK과 충돌 | 현재 LOCK = 2025 버전. 외부 표준 변경 시 R-62-9에 의해 연 1회 재검토 → LOCK 갱신 제안 → 0-0 Governance 승인 필요 |
| STEP7-E 신규 항목이 D2.0-07 LOCK과 충돌 | D2.0-07 LOCK 우선. STEP7 항목은 LOCK 범위 내에서만 구현 |
| 소비 도메인에서 보안 체크리스트 예외 요청 | 예외 사유를 본 도메인 CONFLICT_LOG에 기록 + R-62-1에 의해 전 도메인 통보 |

---

## 10. 검증 체크리스트

| # | 검증 항목 | 확인 방법 | 필수 |
|---|----------|----------|:---:|
| 1 | 계획서 14+α 섹션 완결성 | 모든 섹션 존재 + 빈 섹션 없음 (§11/§12 제외) | ✅ |
| 2 | AUTHORITY_CHAIN 20개 LOCK | LOCK 항목 20건 + Part2/D2.0-07 출처 명시 | ✅ |
| 3 | 서브폴더 4개 × _index.md | 각 서브폴더에 `_index.md` 존재 + 내용 비어있지 않음 | ✅ |
| 4 | Part2 §6.5 라인 대조 | `/sot-check sot2 6-2` MATCH 판정 | ✅ |
| 5 | D2.0-07 LOCK 항목 20건 불변 확인 | AUTHORITY_CHAIN과 D2.0-07 원문 대조 | ✅ |
| 6 | STRIDE 6대 위협 매핑 완결 | 03_stride-threat-model에 6개 위협 전부 대응 통제 명시 | ✅ |
| 7 | OWASP LLM Top 10 매핑 완결 | 04_owasp-llm-top10에 10개 위험 전부 완화 전략 명시 | ✅ |
| 8 | 소비 도메인 매트릭스 | 부록 A에 12개 소비 도메인 목록 + 연동 방식 명시 | ✅ |
| 9 | 기존 도메인 무변경 | `git diff`로 기존 폴더 변경 없음 | ✅ |
| 10 | MASTER_INDEX 갱신 | 6-2 상태 ✅ Phase 6 완료 기록 | ✅ |
| 11 | CONFLICT_LOG 구조 정합성 | §9.1 충돌 유형 4건 분류 체계 반영 + 해결 우선순위 원칙 발췌 + R-62-3 STRIDE 변경/소비 도메인 예외 기록 수용 | ✅ |

---

## 11. 보완 사항

| # | 발견 사항 | 심각도 | 대응 | 상태 |
|---|----------|--------|------|------|
| S-1 | §9에 CONFLICT_LOG 충돌 이력 요약 테이블(§9.3) 없음 | LOW | CONFLICT_LOG에 OPEN 충돌 0건이므로 즉시 조치 불필요. S8-7 일괄 보강 시 추가 | 🔄 OPEN |
| S-2 | §11 보완 사항 미작성 | LOW | S8-5에서 본 테이블 작성 완료 | ✅ DONE |
| S-3 | Guardrails 3-Layer × §6.5 15항목 교차 참조 테이블 미완 | MEDIUM | S10-5에서 부록 §C 추가 — 3×15 매트릭스 전수 커버리지 확인 | ✅ DONE |
| S-4 | HMAC 키 운영 절차 미문서화 | MEDIUM | S10-5에서 부록 §D 추가 — 7단계 라이프사이클 + Grace Period 상세 + 실패 시나리오 | ✅ DONE |

---

## 12. FINAL REVIEW 결과

> 첫 작성 시점. Phase 0 완료 후 판정.

| 항목 | 결과 |
|------|------|
| 검증 체크리스트 10항목 | ⬜ 미검증 |
| Gate 판정 | ⬜ 미판정 |

---

## 13. L3 전수 승급 계획

### 13.1 L3 완성도 매트릭스 (Security-Governance 도메인)

| # | 기준 | 설명 |
|---|------|------|
| E1 | **위협 시나리오** | 위협 유형 + 공격 경로 + 영향도 + 발생 가능성 |
| E2 | **대응 통제** | 예방/탐지/대응 통제 각각의 구현 상세 |
| E3 | **구현 패턴** | 언어별(Python/Node.js/Rust) 코드 패턴 + 금지 패턴 |
| E4 | **테스트 시나리오** | 보안 테스트 케이스 (공격 시뮬레이션, 경계값, fuzzing) |
| E5 | **CI/CD 통합** | 자동 검증 스크립트 + 파이프라인 통합 방법 |
| E6 | **모니터링 메트릭** | 보안 이벤트 수집 항목 + 알림 임계값 |
| E7 | **운영 절차** | 인시던트 대응, 키 순환, 보안 패치 적용 절차 |
| E8 | **외부 표준 참조** | OWASP/STRIDE/NIST 등 외부 표준 정확한 조항 참조 |

### 13.2 현재 L3 상태

| 서브폴더 | 대상 수 | L3 완료 | 비율 |
|---------|---------|---------|------|
| 01_ai-code-security | 7 체크리스트 + 15 보안 항목 | 0 | 0% |
| 02_hmac-timing-defense | 5 방어 항목 + 키 관리 | 0 | 0% |
| 03_stride-threat-model | 6 위협 + 대응 통제 | 0 | 0% |
| 04_owasp-llm-top10 | 10 위험 + 완화 전략 | 0 | 0% |

> Phase 1에서 L3 작성 시작, Phase 2에서 완성 목표.

### 13.3 Phase 2~3 L3 완성도 최종 확정 매트릭스 (Path A drift fix Stage 1, 2026-05-18)

> **목적**: Phase 2 V2 5 NEW + Phase 3 P3-1~P3-3 3건 L3 완성도 최종 확정 + ★★ NO-DRIFT 100% Wave 2 첫 도메인 specialty milestone 통산 (3-7 Wave 1 #9 + 3-9 Wave 1 #10 ZERO write 패턴 EXACT 직계 Wave 2 첫 도메인 + R-T6-2 횡단 관심사 도메인 specialty + 8 cross-handoff set distinct + NEVER_AUTO LOCK L20 절대 우선 통산 일관).

| 서브폴더 | V2 NEW | V3 forward-defined | V-17 PASS | CON | FAIL |
|---------|--------|-------------------|-----------|-----|------|
| 01_ai-code-security | 2 (llamaguard_integration 379L + gdpr_compliance 361L) | 1 (security_test_pipeline_v3 NEW SAST/DAST/IAST + LlamaGuard L3 통합) | 2 | 0 | 0 |
| 02_hmac-timing-defense | 1 (hmac_agent_auth 324L) | 0 (P3-2 Red Team HMAC LOCK L3 6-3 PARL Lead+5 cross-handoff inline) | 1 | 0 | 0 |
| 03_stride-threat-model | 1 (zero_trust_stride_v2 337L) | 2 (anomaly_detection_v3 + red_team_automation_v3 STRIDE 84 매트릭스 + 60 cross 시나리오 base) | 1 | 0 | 0 |
| 04_owasp-llm-top10 | 1 (owasp_v2_review 351L) | 1 (P3-2 OWASP V2.6 사전 수행 + P3-3 OWASP 통합 검증 inline 분담) | 1 | 0 | 0 |
| 05_advanced-security (NEW 서브폴더) | 0 (P3 V3 forward-defined 신규 생성) | 4 (anomaly_detection_v3 + red_team_automation_v3 + security_test_pipeline_v3 + _index.md NEW) | 0 | 0 | 0 |
| **합계** | **5 NEW / 1,752 L** | **8 forward-defined (4 NEW V3 산출물 [05 폴더] + 4 base usage references [01/03×2/04])** | **5** | **0** | **0** |

**6 sub-section milestone**:
1. **★★ NO-DRIFT 100% Wave 2 첫 specialty 통산 3/3 P3 ZERO write**: P3-1 tcv3 first-pass + P3-2 tcv3 first-pass + P3-3 tcv3 first-pass ALL ZERO write = 0 drift fix, byte Δ P3 단계 +0 B / +0 LF (3-7 Wave 1 #9 + 3-9 Wave 1 #10 ZERO write 패턴 EXACT 직계 Wave 2 첫 도메인 6-2 specialty 누적)
2. **★ LOCK L1~L20 set accuracy 20 unique 변경 0 통산 Phase 0/1/2/3** + LOCK 인용 set distinct 11/20 = 55% ENTRY_PROMPT 단계 (P3-1 7 + P3-2 7 + P3-3 9 specific = set distinct L1/L2/L3/L7/L10/L11/L12/L14/L17/L19/L20 = 11, V3 implementation 단계 P3-3 검증 #2 "LOCK L1~L20 전수 인용 매트릭스" 20/20 plan ALL §3.5 AUTHORITY §4 정본 EXACT 정합)
3. **★ LOCK count duality**: V2 5 NEW grep "LOCK L" 누계 ~89 refs + V2 §2 4-field 정의 row + LOCK set unique 20 (변경 0 통산) + LOCK 신규 추가 0 통산 V3 범위 이월 (4-2 V2-only 129 / 4-4 시나리오 88 / 6-1 V2 4 NEW 77 패턴과 다른 specialty 6-2 V2 5 NEW LOCK 인용 누계 매트릭스 specialty + R-T6-2 횡단 관심사 도메인 LOCK count duality V2 + 전체 specialty)
4. **★ AUTHORITY STEP_C 2026-04-27 truly_converged_v2 수렴 통산 R1~R12 29 edits / 12 Round / 2회 multi-round 수렴** (1차 LOCK count duality 16→19 + STEP7-E 18→19 ID matrix 정밀화 + 2차 V1 tag arithmetic count drift 11 tag/132/22 cascade) — LOCK 4-field verbatim 100% 준수 + V2 정본 분리 R9 핵심 기여
5. **⚠️ CONFLICT_LOG 3 entries inheritance 보존**: W-1 OWASP 매핑 R-62-9 연 1회 재검토 RESOLVED + W-2 STRIDE 매핑 9-State 한정 ISS-4 해소 RESOLVED + W-3 HMAC 키 순환 grace period 24h 부록 §D 등재 RESOLVED + Phase 3 신규 OPEN 0 통산 (Phase 0/1/2/3 변경 0)
6. **★ Phase 4 entry-gate 3 P3 매핑 + Phase 3→Phase 4 인계 게이트 [x] 6/6** (P3-1 anomaly_detection_v3 ≥ 400L + ML 정확도/재현율 임계값 + LOCK L1/L2 인용 정합 + 6-5 SDAR cross-handoff + CONFLICT 0 / P3-2 red_team_automation_v3 ≥ 450L + Red Team 시나리오 ≥ 10 (60 cross) + 자동 분류 정확도 임계값 + 6-3 cross-handoff + 0 / P3-3 security_test_pipeline_v3 ≥ 500L + CI/CD 게이트 ≥ 5 (LOCK L11 1:1) + 자동 차단 임계값 4종 + 4-2 cross-handoff + P3-1+P3-2 통합 검증 + 0 / Phase 3→4 인계 [x] 6/6: NEW 3건 L3 PASS + LOCK 20 unique 변경 0 + CONFLICT OPEN 0 + 8 cross-handoff RESOLVED + 이슈 #3+#4 통합 + FABRICATION 0 + V1 12/12 + V2 5/5 1,752L SHA UNCHANGED)

**★★ NO-DRIFT 100% Wave 2 첫 specialty 통산 3/3 P3 ZERO write Wave 2 specialty milestone 첫 사례**: P3-1 + P3-2 + P3-3 ALL tcv3 first-pass = 통산 324 verifications + 0 drift fixes (3-7 Wave 1 #9 + 3-9 Wave 1 #10 ZERO write 패턴 EXACT 직계 Wave 2 첫 도메인 6-2 통산 3 P3 ZERO write 1st verify, 6-1 Wave 2 #13 mixed pattern 4 fix textual notation only와 다른 6-2 specialty 누적 Wave 2 단계 첫 NO-DRIFT 100% 도메인 milestone)

**★ R-T6-2 횡단 관심사 도메인 specialty milestone**: 소비 도메인 12개 R-62-1 정책 통보 (Part2 §6.5 L4861-4961 정본 명시: 1-1/1-2/2-1/2-2/3-7/3-10/4-1/4-2/4-3/6-3/6-5/6-8) + 부록 A 매트릭스 + STEP7-E 92건 우선순위 직계 통산 inheritance + STAGE 9 Production read-only 1-2 Auxiliary §5 read-only sandbox 전용 reference 처리 specialty (6-2 + 6-12 + 6-13 3 횡단 관심사 도메인 중 본 6-2 첫 Wave 2 진입 사례)

**★ Phase 3→Phase 4 인계 게이트 8 cross-handoff set distinct 매트릭스 정합 milestone**: 4-2 CICD §9.1 L1419 + 4-1 Rust-Tauri IPC + 4-3 MCP 화이트리스트 + 3-7 Plugin 보안 + 6-3 PARL Swarm + 6-5 SDAR W-CB + 6-6 Self-Evolution L18 + 6-8 Cloud 배포 = 8 set distinct (P3-1 4 + P3-2 3 + P3-3 4 = 11 매핑 → distinct 8, L1573 cite EXACT MATCH)

**★ downstream (전 도메인 LOCK 영향) R-T6-2 횡단 + 6-3 PARL Wave 2 #15 forward-defined inheritance pattern** (3-4 N-018 + 3-5 wellness_community + 3-6 6-1/6-2 + 3-7 3-10★/4-3★ + 4-2 4-4/4-1 + 4-4 6-9/4-3 + 6-1 6-11★/6-9★ 패턴 직계, 본 도메인 Phase 3 단계 6-3 + 12 소비 도메인 종합계획서 미직접 편집 verify only, STAGE 9 RO 1-2 sandbox 전용 reference 처리 specialty)

**§12 ⬜ PENDING SKIP no-op 자동 inheritance** (§13.X-1 처리, 3-9 ⬜ PENDING 패턴 직계 + 3-7 ✅ APPROVED + 4-2 ✅ APPROVED + 4-4 ✅ APPROVED + 6-1 CONDITIONAL APPROVED 패턴과 다름 — 6-2는 ⬜ PENDING 인지 유지 specialty, Phase 3 완료 후 별도 /validate → /audit → /final-review 트랙)

**★ NEVER_AUTO LOCK L20 절대 우선 통산 일관 정책 milestone**: P3-1 Model Theft 자율 차단 vs NEVER_AUTO 우선 + P3-2 Red Team 자율 공격 가능 단 실 시스템 변경 — 파일 삭제/외부 송금 등 — 절대 차단 + P3-3 production 배포 자동화 금지 통산 3/3 P3 일관 NEVER_AUTO 정책 inheritance

---

## 14. 실행 약점 대응 계획

| # | 약점 | 위험도 | 대응 |
|---|------|--------|------|
| 1 | D2.0-07 16섹션 + STEP7-E 92건 분량이 커서 참조 누락 가능 | HIGH | 서브폴더별로 D2.0-07/STEP7-E 섹션 매핑 테이블 유지 |
| 2 | 소비 도메인 12개에 보안 체크리스트 변경 전파 누락 가능 | HIGH | R-62-1 강제 + 부록 A 매트릭스 유지 |
| 3 | OWASP LLM Top 10 외부 표준 업데이트 추적 필요 | MEDIUM | R-62-9 연 1회 재검토 + R-62-10 STALE 플래그 |
| 4 | HMAC 키 순환 운영 절차 실행 경험 부족 | MEDIUM | Phase 2에서 운영 절차 시뮬레이션 + 문서화 |
| 5 | Guardrails 3-Layer 통합 테스트 환경 필요 | LOW | Phase 2에서 테스트 환경 구축 (V2 LlamaGuard 의존) |

---

## 부록 §A — 소비 도메인 매트릭스

> **횡단 관심사**: 6-2 Security-Governance는 다음 12개 도메인에서 보안 체크리스트를 소비합니다.
> 출처: INTEGRATION_PLAN §7.5 횡단 매트릭스

| # | 소비 도메인 | 참조 위치 | 연동 방식 |
|---|-----------|----------|----------|
| 1 | **1-1** Verifier-Reasoning-Engines | §9 충돌해결 | 추론 엔진 입출력 보안 검증 (OWASP LLM01, LLM02) |
| 2 | **1-2** Auxiliary-Modules | §9 충돌해결 | 보조 모듈 보안 검증 (PII 마스킹, 출력 sanitize) |
| 3 | **2-1** Blue-Node-Architecture | §9 충돌해결 | Node 간 통신 HMAC 인증 (STRIDE Tampering) |
| 4 | **2-2** COND-Modules-Detail | §9 충돌해결 | 106개 모듈 보안 체크리스트 적용 |
| 5 | **3-7** Developer-Tools-API-SDK | §9 충돌해결 | 코드 실행 샌드박스, Plugin 보안 (OWASP LLM07) |
| 6 | **3-10** Agent-Protocol-Interoperability | §9 충돌해결 | 자율성 게이팅 L0~L4, 안전 가드레일 (OWASP LLM08) |
| 7 | **4-1** Rust-Tauri-Infrastructure | §9 충돌해결 | IPC 보안, Python Bridge 인증 |
| 8 | **4-2** CICD-Pipeline | §9 충돌해결 | SAST/DAST 보안 스캔 정책, 의존성 스캔 기준 |
| 9 | **4-3** MCP-Server-Client | §9 충돌해결 | MCP Tool 화이트리스트, 서명 검증 (OWASP LLM05, LLM07) |
| 10 | **6-3** Agent-Teams-PARL | §9 충돌해결 | Agent 보안 정책, NEVER_AUTO, PARL 패턴 보안 |
| 11 | **6-5** SDAR-System | §9 충돌해결 | STRIDE 위협 → SDAR 자가진단 트리거 매핑 |
| 12 | **6-8** Cloud-Library | §9 충돌해결 | 클라우드 배포 보안, 네트워크 세그먼테이션 |

### 소비 도메인의 §9 참조 방법

각 소비 도메인의 §9 충돌 해결 프로토콜에서 다음과 같이 참조:

```markdown
### 9.x 횡단 관심사 — 보안 체크리스트 참조

> 6-2_Security-Governance 보안 체크리스트가 본 도메인에 우선 적용.
> 예외 시 6-2/CONFLICT_LOG.md에 기록 필수.
> 참조: sot 2/6-2_Security-Governance/SECURITY_GOVERNANCE_구조화_종합계획서.md §4.3 R-62-1
```

---

## 부록 §B — STEP7-E 92건 매핑 요약

| STEP7-E Part | 항목 수 | 주요 매핑 서브폴더 | 비고 |
|-------------|---------|-----------------|------|
| Part 1: Threat Modeling | 10 | 03_stride-threat-model | S7E-001~010, STRIDE/Attack Tree |
| Part 2: Prompt Injection 방어 | 10 | 01_ai-code-security | S7E-011~020, 다층 방어 |
| Part 3: 인증/권한/접근제어 | 10 | 03_stride-threat-model | S7E-021~030, RBAC/Zero-Trust |
| Part 4: 데이터 프라이버시 | 10 | 01_ai-code-security | S7E-031~040, PII/GDPR |
| Part 5: AI Safety/Alignment | 10 | 04_owasp-llm-top10 | S7E-041~050, Constitutional AI |
| Part 6: 규제/컴플라이언스 | 10 | 04_owasp-llm-top10 | S7E-051~060, EU AI Act |
| Part 7: 모니터링/감사/로깅 | 8 | 03_stride-threat-model | S7E-061~068, 6-12 Event-Logging 연동 |
| Part 8: 인시던트 대응 | 8 | 02_hmac-timing-defense | S7E-069~076, 키 순환/복구 |
| Part 9: Agent 보안 심화 | 8 | 01_ai-code-security | S7E-077~084, 에이전트 샌드박스 |
| Part 10: VAMOS 고유 보안 차별화 | 8 | 04_owasp-llm-top10 | S7E-085~092, 100% 로컬 옵션 |
| **합계** | **92** | — | CRITICAL 27 / HIGH 41 / MED 24 |

---

## 부록 §C — Guardrails 3-Layer × Part2 §6.5 15항목 교차 참조 매트릭스

> **목적**: D2.0-07 §10 Guardrails 3-Layer가 Part2 §6.5 15개 보안 항목을 어떻게 커버하는지 전수 매핑
> **S10-5 추가**: S8-5 이슈 #1 (Guardrails 교차참조 테이블 미완) 해결

| # | Part2 §6.5 보안 항목 | L1 입력 (NeMo Guardrails) | L2 처리 (Guardrails AI) | L3 출력 (LlamaGuard) | STEP7-E 매핑 | 버전 |
|---|---------------------|:---:|:---:|:---:|---------|:---:|
| 1 | 입력 검증/살균 | **✅ 1차 방어** | ⬜ 보조 | ⬜ — | S7E-011~016 | V1 |
| 2 | 프롬프트 인젝션 방어 | **✅ Instruction Hierarchy** | ✅ 재검증 | ⬜ — | S7E-011~013 | V1 |
| 3 | 시스템/사용자 프롬프트 분리 | **✅ 분리 강제** | ⬜ — | ⬜ — | S7E-014 | V1 |
| 4 | 출력 길이 제한 (10KB) | ⬜ — | **✅ 크기 검증** | ✅ 최종 필터 | S7E-007 | V1 |
| 5 | HTML/JS 이스케이프 | ⬜ — | **✅ sanitize** | ✅ 최종 검증 | S7E-007 | V1 |
| 6 | RBAC 권한 체크 | ✅ 입력 시 | **✅ 세션 검증** | ⬜ — | S7E-025~027 | V1 |
| 7 | 에러 정보 유출 방지 (R9) | ⬜ — | ✅ 스택트레이스 차단 | **✅ 최종 필터** | S7E-042 | V1 |
| 8 | API Key 관리/마스킹 | ✅ 키 검증 | **✅ 마스킹** | ⬜ — | S7E-031~034 | V1 |
| 9 | Docker 샌드박스 코드 실행 | ⬜ — | **✅ 격리 실행** | ⬜ — | S7E-077~078 | V1 |
| 10 | HMAC-SHA256 Agent 인증 | ⬜ — | **✅ 서명 검증** | ⬜ — | S7E-004~005 | V2 |
| 11 | PII 필터링 | ✅ 입력 감지 | **✅ 마스킹 적용** | ✅ 출력 재검증 | S7E-035~037 | V1 |
| 12 | MCP Tool 화이트리스트 | **✅ 호출 전 검증** | ⬜ — | ⬜ — | S7E-004 | V1 |
| 13 | 승인 타임아웃 (600초) | **✅ 시간 제한** | ✅ 상태 추적 | ⬜ — | S7E-028 | V1 |
| 14 | NEVER_AUTO 정책 | **✅ 정책 강제** | ✅ 재확인 | ⬜ — | S7E-029~030 | V1 |
| 15 | 비용 상한 차단 (R10) | **✅ 사전 차단** | ✅ 비용 추적 | ⬜ — | S7E-008 | V1 |

**커버리지 요약**:
- **L1 입력 (NeMo Guardrails)**: 15항목 중 **10항목** 1차 방어 제공
- **L2 처리 (Guardrails AI)**: 15항목 중 **13항목** 처리/검증 (핵심 레이어)
- **L3 출력 (LlamaGuard)**: 15항목 중 **5항목** 최종 필터
- **전수 커버리지**: 15/15 항목 최소 1개 Layer 이상 커버 ✅

---

## 부록 §D — HMAC 키 운영 절차 매트릭스

> **목적**: HMAC 키 순환 grace period(24h) 운영 절차를 포함한 전체 키 라이프사이클 운영 매트릭스
> **S10-5 추가**: S8-5 이슈 #5 (HMAC 운영절차 미문서화) 해결

### D.1 키 라이프사이클 운영 절차

| 단계 | 절차 | 담당 | 자동화 | 검증 방법 | 관련 LOCK |
|------|------|------|:---:|----------|----------|
| **1. 생성** | `crypto.randomBytes(32)` → 최소 32바이트 | 시스템 (자동) | ✅ | 키 길이 ≥ 32 확인 | LOCK-SEC-05 |
| **2. 저장** | V1: `.env` + dotenv / V2: HashiCorp Vault | DevOps | V2 ✅ | gitleaks hook으로 소스 내 유출 탐지 | LOCK-SEC-06 |
| **3. 배포** | 환경변수 주입 (Docker secrets / K8s secrets) | CI/CD | ✅ | 키 해시값 비교로 배포 확인 | — |
| **4. 순환** | 90일 자동 순환 (R-62-6) | 시스템 (cron) | ✅ | 순환 이벤트 로그 확인 (6-12 연동) | LOCK-SEC-07 |
| **5. Grace Period** | 구 키 24시간 병행 유지 (듀얼 키 검증) | 시스템 (자동) | ✅ | 양쪽 키 모두 HMAC 검증 통과 확인 | LOCK-SEC-07 |
| **6. 폐기** | Grace 만료 후 구 키 완전 삭제 + 감사 로그 | 시스템 (자동) | ✅ | 구 키 HMAC 검증 실패 확인 | — |
| **7. 긴급 교체** | 키 유출 시: 즉시 폐기 → 신규 생성 → Grace 없이 즉시 적용 | DevOps + Oncall | ⬜ 수동 | S7E-005 인시던트 절차 따름 | LOCK-SEC-08 |

### D.2 Grace Period 운영 상세

```
[순환 시작]
  → 신규 키 생성 (crypto.randomBytes(32))
  → 환경변수에 NEW_KEY + OLD_KEY 모두 등록
  → Agent HMAC 검증: NEW_KEY 우선 → 실패 시 OLD_KEY 검증
  → 24시간 경과 후 OLD_KEY 삭제
  → 감사 로그: oc.security.key_rotation.{started|completed}
```

### D.3 실패 시나리오 및 롤백

| 시나리오 | 탐지 방법 | 대응 | 에스컬레이션 |
|---------|----------|------|-------------|
| 신규 키 배포 실패 | 키 해시 미일치 알림 | 구 키로 롤백 (자동) | P2 oncall 통보 |
| Grace 기간 내 인증 실패 급증 | 6-12 이벤트 모니터링 | 듀얼 키 검증 로직 확인 | P1 oncall 통보 |
| 키 유출 감지 | gitleaks/보안 스캔 알림 | 긴급 교체 절차 즉시 발동 | **P0 즉시 대응** |
| Vault 접근 불가 (V2) | 헬스체크 실패 | 로컬 캐시 키 사용 (최대 1시간) | P1 인프라 팀 |
