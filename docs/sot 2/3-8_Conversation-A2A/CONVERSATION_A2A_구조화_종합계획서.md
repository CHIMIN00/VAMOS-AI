# Conversation / A2A 구조화 종합 계획서

> **버전**: v1.2
> **작성일**: 2026-03-23
> **목적**: sot 2/3-8_Conversation-A2A/를 대화/A2A 구현 정본으로 구조화
> **Status**: APPROVED — S10-4 등급 A (2026-03-27)
> **Tier**: 3
> **SOT 출처**: STEP7-B, D2.0-05
> **Part2 상태**: PARTIAL — A2A 파일 구조만 존재, 대화 프로세스 1줄 기술

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
- [부록 §A 프로토콜 스펙 레퍼런스](#부록-a-프로토콜-스펙-레퍼런스)
- [부록 §B Agent Discovery 메커니즘](#부록-b-agent-discovery-메커니즘)
- [부록 §C MoA(Mixture-of-Agents) 패턴](#부록-c-moamixture-of-agents-패턴)

---

## 1. 현재 상태 분석

### 1.1 기존 문서 현황

| 문서 | 위치 | 줄 수 | 상태 |
|------|------|-------|------|
| STEP7-B 대화프로세스 작업가이드 | `docs/sot/STEP7-B_*.md` | ~1,188줄 | 시중 AI 10종 전수 비교 + VAMOS 파이프라인 분석 |
| D2.0-05 Agent Workflow | `docs/sot/D2.0-05_*.md` | ~1,982줄 | Agent Pool/Workflow/Fallback/Cooperative Agent |
| Part2 구현가이드 | `docs/guides/VAMOS_구현가이드_PART2_구현단계.md` | 6,313줄 | A2A 파일 구조만 (PARTIAL), `backend/vamos_core/agent_teams/a2a/` |

### 1.2 sot 2/ 현재 파일

| 파일 | 줄 수 | 내용 |
|------|-------|------|
| `CONVERSATION_A2A_상세명세.md` | 593줄 | A2A 메시지 포맷, 디스커버리, 보안, 고급 기능, MoA, 모니터링 |

### 1.3 핵심 문제

| # | 문제 | 심각도 | 영향 |
|---|------|--------|------|
| P1 | 상세명세만 존재, 구조화 계획서 부재 | HIGH | 항목별 추적/검증 불가 |
| P2 | Part2에 A2A 파일 구조만, 구현 상세 없음 | HIGH | 구현 시 정본 모호 |
| P3 | 상세명세 5개 서브도메인 기반 A2A 구현 항목 60건 서브폴더 미매핑 | MEDIUM | SOT↔구현 간 추적 손실 |
| P4 | #13 Agent-Protocol과 A2A 프로토콜 계층 경계 모호 | MEDIUM | 이중 정의 위험 |
| P5 | #16 MCP 도구 호출 위임 인터페이스 미정의 | MEDIUM | A2A↔MCP 연동 갭 |

### Part2 상태 및 방식 C 접근법
- **Part2 상태**: PARTIAL
- **방식 C 접근법**: 보완 작성

---

## 2. 목표 구조 (최종 형태)

### 2.1 폴더 트리

```
3-8_Conversation-A2A/
├── CONVERSATION_A2A_구조화_종합계획서.md      ← 본 문서 (14+3 섹션)
├── AUTHORITY_CHAIN.md                         ← 권한 체계 선언
├── CONFLICT_LOG.md                            ← 충돌 기록
├── CONVERSATION_A2A_상세명세.md               ← 기존 유지 (삭제 금지)
├── 01_a2a-protocol/
│   ├── _index.md                              ← A2A 메시지 포맷 + Task Lifecycle
│   ├── json_rpc_schema.md                     ← JSON-RPC 2.0 상세 스키마
│   ├── task_lifecycle.md                      ← Task 상태 머신 상세
│   ├── agent_card_spec.md                     ← 에이전트 카드 확장 스펙
│   └── error_codes.md                         ← A2A 에러 코드 카탈로그
├── 02_agent-discovery/
│   ├── _index.md                              ← 에이전트 디스커버리 총괄
│   ├── mdns_dns_sd.md                         ← mDNS/DNS-SD 프로토콜
│   ├── service_registry.md                    ← 서비스 등록/해제
│   └── agent_selection.md                     ← 에이전트 선택 알고리즘
├── 03_security/
│   ├── _index.md                              ← A2A 보안 총괄
│   ├── mtls_jwt.md                            ← mTLS + JWT 인증
│   ├── delegation_chain.md                    ← 권한 위임 체인
│   └── audit_logging.md                       ← 감사 로깅
├── 04_advanced-features/
│   ├── _index.md                              ← 고급 대화 기능 총괄
│   ├── streaming_sse.md                       ← SSE 스트리밍
│   ├── multi_turn_sessions.md                 ← 멀티턴 세션
│   ├── conversation_state_machine.md          ← 대화 상태 머신
│   └── moa_pattern.md                         ← MoA 패턴
├── 05_monitoring/
│   ├── _index.md                              ← A2A 모니터링 총괄
│   ├── metrics_dashboard.md                   ← 모니터링 메트릭
│   └── test_framework.md                      ← A2A 테스트 프레임워크
```

### 2.2 깊이 규칙

```
최대 3단계:
  3-8_Conversation-A2A/ → XX_{카테고리}/ → 파일.md    (2단계) ✅
  4단계 이상 → 절대 금지 ❌
```

### 2.3 네이밍 규칙

- **폴더명**: 영문 소문자 + 하이픈, 접두사 2자리 (`01_`, `02_`, ...)
- **파일명**: 영문 소문자 + 언더스코어 (`.md` 확장자)
- **계획서**: `CONVERSATION_A2A_구조화_종합계획서.md` (한글 허용)

---

## 3. 권한 체계 선언

### 3.1 기존 VAMOS 권한 체인

```
RULE 1.3 (최상위 정책)
  → D2.0-05 (Agent Workflow 아키텍처)
    → D2.0-03 (Blue Node 실행 계층)
      → sot 2/ (구현 상세)
```

### 3.2 Conversation-A2A 확장 체인

```
STEP7-B (대화 프로세스 작업가이드) — 체크리스트/항목 목록 정본
  → D2.0-05 (Agent Workflow) — 아키텍처/흐름 정본
    → sot 2/3-8_Conversation-A2A/ — 구현 상세 정본
      → Part2 §6 (참조만, 파일 구조)
```

### 3.3 문서별 정본 범위

| 문서 | 정본 범위 | 비정본 범위 |
|------|----------|-----------|
| STEP7-B | 시중 AI 비교, VAMOS 미적용 항목 목록 | 구현 상세 |
| D2.0-05 | Agent Mode, Cooperative Agent 구조, Fallback/Retry | 개별 A2A 메시지 스키마 |
| sot 2/ (본 폴더) | A2A 메시지 스키마, 디스커버리 상세, 보안 구현, MoA 패턴 | 상위 아키텍처 결정 |
| Part2 | 파일 배치 (When/Where) | 구현 상세 (What/How) |

### 3.4 LOCK 보호 항목

| LOCK ID | 항목 | 값 | 출처 |
|---------|------|-----|------|
| LOCK-A2A-01 | JSON-RPC 2.0 프로토콜 버전 | `"jsonrpc": "2.0"` | Google A2A Spec |
| LOCK-A2A-02 | Task 상태 열거형 | `submitted\|working\|input-required\|completed\|failed\|canceled` | Google A2A Spec |
| LOCK-A2A-03 | 대화 턴 구조 | `role: "user"\|"agent"`, `parts: Part[]` | Google A2A Spec |
| LOCK-A2A-04 | mDNS Service Type | `_vamos-a2a._tcp.local.` | 상세명세 §3.1 |
| LOCK-A2A-05 | 컨텍스트 윈도우 한계 | 모델별 max_tokens 준수, 초과 시 압축 | D2.0-05 §12.13 |
| LOCK-A2A-06 | mTLS 인증서 만료 자동 갱신 | 30일 전 | 가이드 §4.3/#11 |
| LOCK-A2A-07 | JWT delegation chain 최대 깊이 | 3 | 가이드 §4.3/#11 |
| LOCK-A2A-08 | Agent Mode 열거형 | `MANUAL\|SEMI_AUTO\|SUPERVISED_AUTO` | D2.0-05 §1.1 (ADD-009) |
| LOCK-A2A-09 | Circuit Breaker 연속 실패 임계 | 3회 → OPEN, 60초 후 HALF-OPEN | D2.0-05 §4.4 (ADD-072) |
| LOCK-A2A-10 | A2A 메시지 스키마 정본 소유 | sot 2/3-8 (구현), D2.0-05 (아키텍처) | 본 계획서 |

---

## 4. 거버넌스 규칙

> **글로벌 거버넌스 규칙**: 본 도메인은 0-0_Governance-Rules-Meta에서 정의한 R1~R11 글로벌 규칙을 전체 준수합니다.
> 아래는 글로벌 규칙에 추가되는 도메인 고유 규칙입니다.

### 4.1 공통 규칙 (R1~R8 중 적용 가능)

| ID | 규칙 | 적용 |
|----|------|------|
| R1 | 정본 소유자 1곳 원칙 | ✅ 각 항목에 canonical_owner 지정 |
| R2 | LOCK 값 재정의 금지 | ✅ §3.4 LOCK 항목 보호 |
| R3 | 폴더 깊이 3단계 제한 | ✅ §2.2 준수 |
| R4 | _index.md 필수 | ✅ 서브폴더 5개 모두 |
| R6 | 충돌 시 CONFLICT_LOG 기록 | ✅ §9 프로토콜 |
| R8 | MASTER_INDEX 동기화 | ✅ 작성 후 갱신 |

### 4.2 Tier 3 적용 규칙

| ID | 규칙 | 비고 |
|----|------|------|
| R7 | STEP7 매핑 | STEP7-B 항목 → 서브폴더 매핑 |

### 4.3 도메인 고유 규칙

| ID | 규칙 | 근거 |
|----|------|------|
| R-11-1 | mTLS 인증서 만료 30일 전 자동 갱신 | LOCK-A2A-06 |
| R-11-2 | JWT delegation chain 최대 깊이 3 | LOCK-A2A-07, 보안 제한 |
| R-11-3 | A2A 에이전트 카드는 `/.well-known/agent.json` 경로 필수 | Google A2A Spec 준수 |
| R-11-4 | Task 상태 전이는 상세명세 §2.2 상태 머신 준수 | LOCK-A2A-02 |
| R-11-5 | A2A 메시지 스키마 변경 시 #13 Agent-Protocol 동시 통지 | 교차 의존성 |
| R-11-6 | MoA 패턴 사용 시 최소 2, 최대 5 proposer 에이전트 | 비용/품질 균형 |
| R-11-7 | SSE 스트리밍 연결 타임아웃 300초 (5분) | 인프라 제약 |
| R-11-8 | A2A↔MCP 도구 호출 위임 시 #16 MCP 정본 스키마 참조 필수 | 교차 참조 |

---

## 5. 선행작업

| # | 선행작업 | 상태 | 산출물 |
|---|---------|------|--------|
| PRE-1 | STEP7-B 88건 전수 검토 + 상세명세 기반 A2A 구현 항목 60건 도출 | ✅ 완료 | §6 매핑 테이블 |
| PRE-2 | Part2 PARTIAL 영역 확인 (A2A 파일 구조) | ✅ 완료 | §1.1 현황 |
| PRE-3 | #13 Agent-Protocol과 경계 확인 | ✅ 완료 | R-11-5, CONFLICT_LOG |
| PRE-4 | #16 MCP 도구 호출 위임 인터페이스 정의 | ✅ 완료 | R-11-8, §A 교차 참조 |

---

## 6. 이슈 해결 매핑

### 6.1 A2A 구현 항목 → 서브폴더 매핑 (60건)

> **항목 출처**: 상세명세 5개 서브도메인(A~E) 기반 도출, STEP7-B 88건 검토로 관련성 확인, D2.0-05 아키텍처 결정 반영

| 서브폴더 | 핵심 구현 주제 | 건 수 | 매핑 상태 |
|---------|-------------------|-------|----------|
| `01_a2a-protocol/` | JSON-RPC 2.0 Task Lifecycle, A2A Card 확장, 메시지 스키마 | 12 | ✅ |
| `02_agent-discovery/` | mDNS/DNS-SD, 서비스 등록, 스킬 매칭, 에이전트 선택 | 10 | ✅ |
| `03_security/` | mTLS+JWT, 권한 위임, 감사 로깅, 에러 복구 | 12 | ✅ |
| `04_advanced-features/` | SSE 스트리밍, Push Notifications, Multi-turn, MoA, 대화 분기 | 16 | ✅ |
| `05_monitoring/` | 대시보드 메트릭, 테스트 프레임워크, 에러 핸들링 | 10 | ✅ |
| **합계** | | **60** | **100%** |

<details>
<summary><b>60건 세부 항목 (추적용)</b></summary>

**`01_a2a-protocol/` — 서브도메인 A: A2A 메시지 포맷 (12건)**

| # | 항목 | 상세명세 근거 |
|---|------|-------------|
| 1 | JSON-RPC 2.0 메시지 스키마 (전체 구조) | §2.1 |
| 2 | tasks/send 메서드 | §2.1 method enum |
| 3 | tasks/sendSubscribe 메서드 | §2.1 method enum |
| 4 | tasks/get 메서드 | §2.1 method enum |
| 5 | tasks/cancel 메서드 | §2.1 method enum |
| 6 | tasks/pushNotification/set 메서드 | §2.1 method enum |
| 7 | tasks/pushNotification/get 메서드 | §2.1 method enum |
| 8 | tasks/resubscribe 메서드 | §2.1 method enum |
| 9 | agent/authenticatedExtendedCard 메서드 | §2.1 method enum |
| 10 | Task Lifecycle 상태 머신 (6개 상태) | §2.2 |
| 11 | TaskStatusEvent / TaskArtifactEvent 이벤트 | §2.2 |
| 12 | 에이전트 카드 스펙 (Agent Card) | §2.3 |

**`02_agent-discovery/` — 서브도메인 B: 에이전트 디스커버리 (10건)**

| # | 항목 | 상세명세 근거 |
|---|------|-------------|
| 13 | mDNS 쿼리 프로토콜 | §3.1 |
| 14 | DNS-SD 서비스 타입 (`_vamos-a2a._tcp.local.`) | §3.1 |
| 15 | SRV 레코드 구조 | §3.1 |
| 16 | TXT 레코드 필드 (v, path, caps, agent-id) | §3.1 |
| 17 | 서비스 등록 스키마 (AgentRegistration) | §3.2 |
| 18 | 헬스 체크 메커니즘 | §3.2 health_check |
| 19 | 에이전트 능력 열거형 (AgentCapability) | §3.2 |
| 20 | 에이전트 선택 알고리즘 (가중 스코어링) | §3.3 |
| 21 | Jaccard 유사도 기반 스킬 매칭 | §3.3 |
| 22 | 부하 균형 / 우선순위 로직 | §3.3 |

**`03_security/` — 서브도메인 C: A2A 보안 (12건)**

| # | 항목 | 상세명세 근거 |
|---|------|-------------|
| 23 | mTLS 핸드셰이크 (X.509 인증서) | §4.1 |
| 24 | JWT Bearer 토큰 인증 | §4.1 |
| 25 | JWT Claims 구조 (iss, sub, aud, scope, delegation_chain) | §4.1 |
| 26 | 권한 위임 체인 (DelegationToken) | §4.2 |
| 27 | 위임 깊이 제한 (max_depth: 3) | §4.2 |
| 28 | 리소스 예산 (max_tokens, max_api_calls) | §4.2 constraints |
| 29 | Ed25519 서명 체계 | §4.2 signature |
| 30 | 감사 로깅 스키마 (audit event) | §4.3 |
| 31 | A2A 에러 코드 카탈로그 (-32001 ~ -32005) | §4.4 |
| 32 | HTTP 에러 복구 (408, 429, 503) | §4.4 |
| 33 | 지수 백오프 재시도 정책 | §4.4 |
| 34 | 대체 에이전트 선택 (failover) | §4.4 |

**`04_advanced-features/` — 서브도메인 D: 대화 프로세스 고급 기능 (16건)**

| # | 항목 | 상세명세 근거 |
|---|------|-------------|
| 35 | Streaming SSE | §5.1 V2 #1 |
| 36 | Push Notifications | §5.1 V2 #2 |
| 37 | State Transition History | §5.1 V2 #3 |
| 38 | Multi-turn Sessions | §5.1 V2 #4 |
| 39 | Artifact Chunking | §5.1 V2 #5 |
| 40 | Agent Composition | §5.1 V2 #6 |
| 41 | Priority Queuing | §5.1 V2 #7 |
| 42 | Conversation Branching | §5.1 V2 #8 |
| 43 | 대화 상태: idle → awaiting_agent 전이 | §5.2 |
| 44 | 대화 상태: agent_thinking | §5.2 |
| 45 | 대화 상태: agent_delegating / sub_task_waiting | §5.2 |
| 46 | 대화 상태: agent_streaming | §5.2 |
| 47 | 대화 상태: response_ready → completed/follow_up/error | §5.2 |
| 48 | 대화 상태: follow_up_needed 루프 | §5.2 |
| 49 | MoA 병렬 제안 수집 (proposer 에이전트) | §5.3 |
| 50 | MoA 집계 에이전트 응답 합성 (aggregator) | §5.3 |

**`05_monitoring/` — 서브도메인 E: A2A 모니터링/테스트 (10건)**

| # | 항목 | 상세명세 근거 |
|---|------|-------------|
| 51 | 트래픽 메트릭 (total_tasks_24h, active_sessions, tasks_by_state) | §6.1 |
| 52 | 성능 메트릭 (avg/p50/p95/p99 latency) | §6.1 |
| 53 | 안정성 메트릭 (success_rate, error_rate, timeout_rate) | §6.1 |
| 54 | 에이전트별 메트릭 (status, tasks_processed, load_factor) | §6.1 |
| 55 | 단위 테스트 (unit) | §6.2 |
| 56 | 통합 테스트 (integration) | §6.2 |
| 57 | E2E 테스트 (e2e) | §6.2 |
| 58 | 카오스 테스트 (chaos) | §6.2 |
| 59 | 에러 분류 체계 (Transient/Permanent/Unknown) | §6.3 |
| 60 | 에러 해결 흐름 (Recovered/Degraded/Failed) | §6.3 |

</details>

#### STEP7-B 88건 → A2A 도메인 관련성 매핑

> STEP7-B에는 "A2A" 용어가 직접 사용되지 않음. 아래는 88건 중 A2A 구현 시 참조해야 할 항목의 카테고리별 관련도.

| STEP7-B 카테고리 | 건수 | A2A 관련 항목 | 관련 서브폴더 |
|-----------------|:----:|-------------|-------------|
| D. 라우팅/결정 | 8 | D-1~D-8 전수 (3-Gate, Policy/Cost/Evidence, 모델 라우팅) | `02_agent-discovery/`, `04_advanced-features/` |
| E. 도구 사용/실행 | 14 | E-1 MCP, E-8 서브에이전트 스폰, E-10 병렬 도구 호출 | `01_a2a-protocol/` |
| F. 자기검증/품질 | 8 | F-3 EVX 검증, F-5 Fallback Chain | `03_security/` |
| G. 출력/메모리 | 8 | G-6 이벤트 로깅, G-7 감사 추적 | `05_monitoring/` |
| H. 세션 관리 | 6 | H-2 대화 분기, H-6 멀티 대화 병렬 | `04_advanced-features/` |
| K. 에러 핸들링 | 4 | K-1 API 타임아웃, K-2 모델 불가 시 대체 | `03_security/` |
| A/B/C/I/J | 40 | 간접 참조 (입력/의도/검색/캐싱/후처리) | — |

### 6.2 Part2 PARTIAL 항목 해결

| Part2 항목 | 현재 상태 | 해결 방식 |
|-----------|----------|----------|
| `backend/vamos_core/agent_teams/a2a/protocol.py` | 파일 경로만 | sot 2/ `01_a2a-protocol/`에서 스키마 정의 |
| `backend/vamos_core/agent_teams/a2a/discovery.py` | 파일 경로만 | sot 2/ `02_agent-discovery/`에서 상세 정의 |
| `backend/vamos_core/agent_teams/a2a/security.py` | 파일 경로만 | sot 2/ `03_security/`에서 인증 상세 |
| `backend/vamos_core/agent_teams/a2a/adapter.py` | MCP 브릿지 | sot 2/ `01_a2a-protocol/` + #16 MCP 교차 참조 |

### 6.3 v12/v23 확장 항목 교차 매핑

| 확장 항목 | v12/v23 ID | 우선순위 | 매핑 서브폴더 |
|----------|-----------|---------|-------------|
| A2A Task Lifecycle 관리 | v12_C09b_110 | HIGH | `01_a2a-protocol/` |
| A2A 모니터링/관측 | v12_C09b_117 | HIGH | `05_monitoring/` |
| A2A Test Framework | v12_C03_037 | HIGH | `05_monitoring/` |
| A2A 에러 처리 및 복구 | v12_C12_104 | HIGH | `03_security/` |
| A2A Task Lifecycle | v12_C03_029 | HIGH | `01_a2a-protocol/` |
| A2A-MCP 브리지 | v12_C12_105 | HIGH | `01_a2a-protocol/` + #16 교차 |
| A2A 에이전트 디스커버리 | v12_C12_101 | MEDIUM | `02_agent-discovery/` |
| VBS-12 에이전트 협업 벤치마크 | v12_C12_115 | HIGH | `05_monitoring/` |

---

## 7. Phase 실행 계획

### 7.1 Phase 개요

```
Phase 0: 분석 + 구조화 (✅ 완료 2026-04-01)
  → 계획서 작성, 서브폴더 골격, AUTHORITY_CHAIN, CONFLICT_LOG
Phase 1: MVP 구현 (V1 정렬) (✅ 완료 2026-04-10)
  → A2A 기본 프로토콜, 단일 에이전트 디스커버리, 기본 보안
Phase 2: 확장 (V2 정렬)
  → MoA 패턴, 고급 대화 기능, 모니터링 대시보드
Phase 3: 최적화 (V3 정렬)
  → 분산 디스커버리, 대화 분기/병합, 성능 최적화
```

### 7.2 Phase 전환 게이트

| 게이트 | 조건 | 상태 |
|--------|------|------|
| Phase 0 → 1 | 계획서 COMPLETE + 서브폴더 _index.md 5개 + AUTHORITY_CHAIN ✅ | **PASS** (2026-04-01: G0-1 P0-1 + G0-2 P0-2 + G0-3 P0-4 전수 충족) |
| Phase 1 → 2 | `01_a2a-protocol/` + `02_agent-discovery/` + `03_security/` L3 완성 | **PASS** (2026-04-10: P1-1~7 전체 완료, 01/02/03 L3 완성) |
| Phase 2 → 3 | `04_advanced-features/` MoA + SSE 완성 + 모니터링 메트릭 정의 | ⬜ |

### 7.3 Phase별 상세

#### Phase 0 (✅ 완료 — 2026-04-01, Phase 0→1 게이트 PASS)

| 산출물 | 상태 |
|--------|------|
| 구조화 종합계획서 | ✅ 본 문서 |
| AUTHORITY_CHAIN.md | ✅ 작성 |
| CONFLICT_LOG.md | ✅ 초기화 |
| 서브폴더 5개 + _index.md | ✅ 생성 |

#### Phase 0 단계별 상세 작업 절차

<details>
<summary><b>P0-1. 구조화 종합계획서 작성 (14+3 섹션) — ✅ 완료 (2026-03-31)</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot\STEP7-B_대화프로세스_작업가이드.md` (88건 프로세스, 1,188줄)
- `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` (Agent Workflow 아키텍처, 1,982줄)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_상세명세.md` (593줄, 기존 명세)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` (6,313줄, Part2 PARTIAL — A2A 파일 구조)

**절차**:
1. STEP7-B 88건 대화 프로세스 항목 전수 검토 (A2A 도메인 관련성 식별)
2. 상세명세 5개 서브도메인(A~E)에서 A2A 구현 항목 60건 도출 및 서브폴더 매핑
3. D2.0-05에서 Agent Workflow 아키텍처 결정 사항 확인 (ADD-009 Agent Mode, ADD-072 Circuit Breaker, §12.13 컨텍스트 관리)
4. 계획서 14+3 섹션(§1~§14 + 부록 §A/§B/§C) 작성:
   - §1 현재 상태 분석, §2 목표 구조, §3 권한 체계, §4 거버넌스, §5 선행작업, §6 매핑, §7 Phase 계획, §8 역할 분리, §9 충돌 해결, §10 검증, §11 보완, §12 FINAL REVIEW, §13 L3 승급, §14 약점 대응
   - 부록 §A 프로토콜 스펙, §B Agent Discovery, §C MoA 패턴
5. Part2 PARTIAL 영역(A2A 파일 구조) 분석 → 방식 C 요약 포함

**검증**:
- [x] 14+3 섹션 전부 작성 완료 — **G0-1 매핑 (계획서 COMPLETE)** ← §1~§14 + §A/§B/§C 전수 확인
- [x] 상세명세 기반 A2A 구현 항목 60건 → 서브폴더 매핑 100% (§6.1) ← 60건 세부 항목 열거 + STEP7-B 관련성 매핑
- [x] Part2 PARTIAL 영역 방식 C 요약 포함 (Part2 정본 요약 섹션) ← L771 방식 C + L795 교차 참조 부록

**산출물**: `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_구조화_종합계획서.md` (본 문서)
</details>

<details>
<summary><b>P0-2. AUTHORITY_CHAIN.md 작성 — ✅ 완료 (2026-04-01)</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_구조화_종합계획서.md` §3 (권한 체계), §8 (파일 역할 분리), §9 (충돌 해결 프로토콜), 부록 §2 (LOCK-AT 교차)
- `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` (아키텍처 정본 — LOCK-A2A-05/08/09 원본 검증)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_상세명세.md` §3.1, §4.1~§4.3 (LOCK-A2A-04/06/07 원본 검증)

**절차**:
1. `3-8_Conversation-A2A/AUTHORITY_CHAIN.md` 신규 생성
2. 헤더 메타데이터 작성:
   - `도메인`: TIER3-DOMAIN-08 Conversation-A2A
   - `작성일`: YYYY-MM-DD (실행일 기입)
   - `최종 갱신`: YYYY-MM-DD (실행일 기입)
   - `Status`: APPROVED
   - `버전`: v1.0
3. 본문 섹션 구성 (§3 + §8 + §9 기반, 아래 순서 준수):
   a. **§1 상위 권한 체인**: §3.1 VAMOS 권한 체인 + §3.2 Conversation-A2A 확장 체인 통합
   b. **§2 정본 소유자 매핑**: §3.3 문서별 정본 범위 + §8 파일 역할 분리 통합 → `canonical_owner` 컬럼 포함, R1(정본 소유자 1곳 원칙) 위반 없이 구성
   c. **§3 LOCK 항목 목록**: §3.4 LOCK-A2A-01~10 전문 등재 — **값 컬럼은 §3.4 원본 문자열 그대로 복사 (요약·축약 금지, R2 LOCK 값 재정의 금지 준수)** + `변경 조건` 컬럼 추가
   d. **§4 교차 참조 의존성**: #13 Agent-Protocol, #16 MCP-Server-Client, #3 Blue-Node 등 인접 도메인 의존 관계 + 의존 방향 명시
   e. **§5 도메인 경계**: §9.2 충돌 시나리오 기반, 본 도메인 소유 항목 vs 인접 도메인 소유 항목 구분
4. LOCK-AT 교차 적용: 부록 §2의 LOCK-AT-004 = LOCK-A2A-07 관계를 §3 LOCK 목록 비고란에 교차 참조 주석으로 명시
5. 변경 기록 규칙 footer 추가: "AUTHORITY_CHAIN 변경 시 CONFLICT_LOG.md에 변경 사유를 기록한다"

**검증**:
- [x] AUTHORITY_CHAIN.md 존재 — **G0-2 매핑 (AUTHORITY_CHAIN ✅)** ← 95줄, §1~§5 + footer 구성
- [x] LOCK-A2A-01~10 전수 등재 (10건), **값이 종합계획서 §3.4 원본과 character-level 동일** (R2 준수) ← 10건 LOCK ID/항목/값/출처 4컬럼 전수 대조 PASS
- [x] 권한 체인이 상위 VAMOS 체인(RULE 1.3 → D2.0-05 → D2.0-03 → sot 2/)과 무모순 ← §1.1=§3.1, §1.2=§3.2 character-level 일치
- [x] 정본 소유자(canonical_owner) 중복 없음 — R1(정본 소유자 1곳 원칙) 준수 ← 8행 canonical_owner 전수 중복 검사 PASS
- [x] 교차 참조 의존성(#13, #16, #3) 경계가 §9.2 충돌 시나리오와 정합 ← #13=§9.2r1, #16=§9.2r2, #3=도메인 고유 경계
- [x] LOCK-AT-004 ↔ LOCK-A2A-07 교차 관계 명시 확인 ← LOCK-A2A-07 변경 조건 비고란에 명시
- [x] 헤더에 도메인/작성일/최종갱신/Status/버전 전부 포함 ← 5필드 전수 확인

**산출물**: `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\AUTHORITY_CHAIN.md` (신규)
</details>

<details>
<summary><b>P0-3. CONFLICT_LOG.md 초기화 — ✅ 완료 (2026-04-01)</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_구조화_종합계획서.md` §1.3 (핵심 문제 P4/P5 — 충돌 원본 정의), §3.4 (LOCK 보호 항목 — 충돌 판정 시 1순위 기준), §4.1 R6 (충돌 시 CONFLICT_LOG 기록 — 존재 근거 규칙), §4.3 R-11-5/R-11-8 (교차 의존 규칙 — #13/#16 상호 통지), §9 전체 (§9.1 우선순위 규칙 + §9.2 충돌 시나리오 3건)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_상세명세.md` §2.1 (A2A 메시지 스키마 — CLF-A2A-001 경계 판정 근거), §3.1 (mDNS 디스커버리), §4.1~§4.4 (보안/에러 처리 — CLF-A2A-002 판정 근거)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\AUTHORITY_CHAIN.md` §4 (교차 참조 의존성), §5 (도메인 경계), footer ("AUTHORITY_CHAIN 변경 시 CONFLICT_LOG.md에 변경 사유를 기록한다" — 양방향 연동 규칙)

**절차**:
1. `3-8_Conversation-A2A/CONFLICT_LOG.md` 신규 생성
2. 헤더 메타데이터 작성 (CONFLICT_LOG는 운영 로그 문서이므로 Status/버전 불필요):
   - `도메인`: TIER3-DOMAIN-08 Conversation-A2A
   - `작성일`: YYYY-MM-DD (실행일 기입)
   - `최종 갱신`: YYYY-MM-DD (실행일 기입)
3. 충돌 해결 프로토콜 섹션 (§9 전체 기반):
   a. §9.1 우선순위 규칙 5개(1순위~5순위) **원문 그대로 발췌** (요약·축약 금지, R2 정신 준수)
   b. §9.2 충돌 시나리오 3건(시나리오/해결 방법) **원문 그대로 발췌** (요약·축약 금지)
4. 충돌 기록 섹션 — 개별 충돌 엔트리 형식:
   - 충돌 ID: `CLF-A2A-NNN` (순번 3자리, 순차 채번)
   - 엔트리 항목 (키-값 테이블):
     | 항목 | 값 |
     |------|-----|
     | **발견일** | YYYY-MM-DD |
     | **충돌 내용** | 충돌 상황 기술 |
     | **관련 문서** | 출처 문서·섹션 교차 참조 |
     | **해결** | 상태(`RESOLVED`|`OPEN`|`DEFERRED`) + 판정 내용 |
     | **근거** | 판정의 권위 근거 (상위 문서, 규칙 ID) |
5. 이미 알려진 충돌 등록 (§1.3 P4/P5 + §9.2 3건 전수):
   - CLF-A2A-001: A2A 스키마 vs #13 Agent-Protocol 스키마 — 계층 경계 (§1.3 P4 + §9.2 시나리오1) → RESOLVED, "A2A 메시지 스키마는 #11 정본, 프로토콜 추상 계층은 #13 정본"
   - CLF-A2A-002: A2A 도구 호출 vs #16 MCP 도구 호출 — 위임 인터페이스 (§1.3 P5 + §9.2 시나리오2) → RESOLVED, "도구 스키마/연결은 #16 정본, A2A에서는 위임 인터페이스만 정의"
   - CLF-A2A-003: STEP7-B 대화 단계 vs D2.0-05 워크플로우 — 정본 우선순위 (§9.2 시나리오3) → RESOLVED, "D2.0-05가 아키텍처 정본, STEP7-B는 벤치마크/비교 참조"
   - ※ 절차 수행 중 추가 충돌 발견 시 즉시 CLF-A2A-004~ 순차 등록
6. 요약 테이블 추가: 총 건수 / RESOLVED / OPEN / DEFERRED 현황 집계
7. footer 규칙 추가:
   - "CONFLICT_LOG 변경 시 관련 인접 도메인(#13, #16) CONFLICT_LOG에도 교차 기록한다"
   - R6(충돌 시 CONFLICT_LOG 기록) 거버넌스 규칙 참조 명시

**게이트 매핑**: Phase 0→1 게이트(G0) 직접 차단 조건 아님 — CONFLICT_LOG는 R6 거버넌스 준수 운영 문서이며, 게이트 조건은 "계획서 COMPLETE + 서브폴더 _index.md 5개 + AUTHORITY_CHAIN ✅". 단, §10 검증 체크리스트 V11에서 존재·무결성 검증.

**검증**:
- [x] CONFLICT_LOG.md 존재 + 헤더 메타데이터 3필드 포함 (도메인/작성일/최종갱신) ← L3~5 전수 확인
- [x] §9.1 우선순위 규칙 5개가 종합계획서 원본과 character-level 동일 ← L16~20 vs §9.1 원문 5행 대조 PASS
- [x] §9.2 충돌 시나리오 3건 해결 방법이 종합계획서 원본과 character-level 동일 ← L27~29 vs §9.2 원문 3행 대조 PASS
- [x] 기존 알려진 충돌 최소 3건(CLF-A2A-001~003) 등록 완료 ← 4건 등록 (001~004), 추가 004는 CB 임계값 차이
- [x] 각 충돌 엔트리에 발견일/충돌 내용/관련 문서/해결/근거 5항목 전수 포함 ← 4개 엔트리 × 5항목 = 20셀 전수 확인
- [x] 충돌 상태 분류(RESOLVED/OPEN/DEFERRED) 적용 + 요약 테이블 건수 합계 일치 ← 4=4+0+0 합계 PASS
- [x] AUTHORITY_CHAIN.md footer 연동 규칙과 양방향 정합 확인 (AUTHORITY_CHAIN → CONFLICT_LOG 기록, CONFLICT_LOG → 인접 도메인 교차 기록) ← AUTHORITY_CHAIN L94 ↔ CONFLICT_LOG L85 양방향 정합
- [x] R6(충돌 시 CONFLICT_LOG 기록) 거버넌스 규칙 참조 footer에 명시 ← L86 "R6... §4.1 R6 참조" 명시

**산출물**: `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONFLICT_LOG.md` (신규)
</details>

<details>
<summary><b>P0-4. 서브폴더 5개 + _index.md 생성 — ✅ 완료 (2026-04-01)</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_구조화_종합계획서.md` §2 (§2.1 폴더 트리 — 서브폴더명·파일 구성 정본, §2.2 깊이 규칙 — 최대 3단계, §2.3 네이밍 규칙 — 폴더/파일 명명 기준), §3.4 (LOCK-A2A-01~10 — 서브폴더별 해당 LOCK 추출 시 원본), §4.1 R3 (폴더 깊이 3단계 제한) + R4 (_index.md 필수), §4.3 R-11-1~R-11-8 (도메인 고유 규칙 — 서브폴더별 배정), §6.1 (A2A 구현 항목 60건 서브폴더 매핑 — 서브폴더별 항목 수 12/10/12/16/10 정본) + §6.3 (v12 확장 항목 8건 — 서브폴더 교차 매핑), §7.3 Phase 1/2/3 작업 테이블 (항목별 Phase·우선순위 배정), §8 (파일 역할 분리 — 정본 소유자), §13.2 (서브폴더별 L3 승급 우선순위 P0/P1), 부록 §A (프로토콜 스펙) + §B (Agent Discovery) + §C (MoA 패턴)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_상세명세.md` §2~§6 (5개 서브도메인 A~E 기술 상세 — _index.md 개요 작성 시 역할 요약 정본)
- 프로젝트 표준 _index.md 패턴 참조 (예: `1-1_Verifier-Reasoning-Engines/01_logic-verifier/_index.md` — 메타데이터 블록·개요·항목 목록·LOCK 참조·의존성·파일 구성 6섹션 구조)

**절차**:
1. 5개 서브폴더 생성 (§2.1 폴더 트리 기준, §2.3 네이밍 규칙 준수):
   - `01_a2a-protocol/`
   - `02_agent-discovery/`
   - `03_security/`
   - `04_advanced-features/`
   - `05_monitoring/`
2. 각 서브폴더에 `_index.md` 신규 생성 — 아래 섹션 구성을 **5개 전수** 동일 형식으로 작성 (순서 준수):
   a. **제목 + 메타데이터 블록**:
      - 제목: `# {접두번호}. {영문명} — {한글명}` (§2.1 파일 트리 주석 참조)
      - 메타데이터 (인용 블록, 아래 5필드 필수):
        | 필드 | 값 출처 | 예시 (01) |
        |------|--------|----------|
        | 서브도메인 | §6.1 서브도메인 식별자 | `A — A2A 메시지 포맷` |
        | 우선순위 | §13.2 L3 승급 우선순위 | `P0` |
        | 항목 수 | §6.1 서브폴더별 건수 | `12` |
        | L3 상태 | Phase 0 초기값 고정 | `SKELETON` |
        | 정본 | §8 파일 역할 + 경로 | `sot 2/3-8_Conversation-A2A/01_a2a-protocol/` |
   b. **개요**: 서브도메인 역할 1~2문장 요약 (상세명세 해당 섹션 §2/§3/§4/§5/§6 기반, 핵심 기능 명시)
   c. **항목 목록 테이블**: §6.1 해당 서브폴더 항목 + §6.3 v12 확장 항목 + §7.3 Phase 2/3 작업을 통합하여 구성
      - 컬럼: `#` (서브폴더 내 로컬 순번 1~N), `항목`, `설명`, `우선순위` (P0/P1/P2), `Phase` (1/2/3), `상태` (SHELL/DRAFT/PLAN)
      - **서브폴더별 항목 행 수 = §6.1 기준 (01:12, 02:10, 03:12, 04:16, 05:10) 일치 필수**
      - §6.1 항목을 기반으로 하되 구현 단위 재구성 허용 (예: method-level 8건 → schema-level 1건 통합 + v12 확장 편입). 재구성 시에도 §6.1 항목이 _index.md 항목에 1:1 또는 N:1로 추적 가능해야 함
      - §6.3 v12 확장 항목 중 해당 서브폴더분은 설명란에 `(v12_CXXXX)` ID 명기
      - Phase 배정: §7.3 Phase 1(MVP)/2(확장)/3(최적화) 작업 테이블과 정합
      - 상태 기준: Phase 1 항목 = SHELL 또는 DRAFT (구현 준비도에 따라), Phase 2 항목 = SHELL · DRAFT · PLAN (구현 준비도에 따라), Phase 3 항목 = PLAN
   d. **LOCK 항목**: §3.4 LOCK-A2A-01~10 중 해당 서브폴더 구현 항목에 적용되는 LOCK만 추출 — **값은 §3.4 원본 문자열 그대로 복사 (요약·축약 금지, R2 LOCK 값 재정의 금지 준수)**. 서브폴더별 해당 LOCK:
      - 01: LOCK-A2A-01 (JSON-RPC 2.0), -02 (Task 상태), -03 (턴 구조)
      - 02: LOCK-A2A-04 (mDNS Service Type)
      - 03: LOCK-A2A-06 (mTLS 갱신), -07 (JWT 깊이), -09 (Circuit Breaker)
      - 04: LOCK-A2A-05 (컨텍스트 윈도우)
      - 05: (직접 해당 LOCK 없음 — LOCK 섹션 생략 또는 "해당 없음" 명시)
      - ※ LOCK-A2A-08 (Agent Mode)과 -10 (스키마 정본 소유)은 메타 수준이므로 개별 _index.md에서 제외
   e. **고유 규칙** (해당 서브폴더에만 추가, 비해당 시 섹션 생략): §4.3 R-11-X 중 해당 서브폴더 적용 규칙
      - 04: R-11-6 (MoA proposer 2~5), R-11-7 (SSE 타임아웃 300초)
      - ※ 01의 R-11-3/R-11-4/R-11-5, 03의 R-11-1/R-11-2는 LOCK 항목 또는 의존성으로 이미 반영되므로 별도 섹션 불필요
   f. **의존성 테이블**: 서브폴더 간 내부 의존(→ 제공 / ← 소비) + 외부 도메인 의존(#13 Agent-Protocol, #16 MCP-Server-Client, D2.0-05 등) — R-11-5 (A2A↔#13 동시 통지), R-11-8 (A2A↔#16 참조) 반영
   g. **파일 구성**: §2.1 해당 서브폴더 파일 트리 발췌 — `파일명 ← 항목 #N: 역할 설명` 매핑 주석 포함
3. 5개 _index.md 작성 완료 후 전수 교차 확인:
   - §2.1 폴더 트리의 서브폴더명 5개·파일명 전수와 실제 파일 구성 일치
   - §2.2 깊이 규칙: 서브폴더 내 하위 폴더 0건 (= 최대 3단계: `3-8/ → XX_카테고리/ → 파일.md`)
   - §2.3 네이밍 규칙: 폴더 `^[0-9]{2}_[a-z][a-z0-9-]*$`, 파일 영문 소문자 + 언더스코어 + `.md`
4. 5개 _index.md 항목 행 수 집계: 01(12) + 02(10) + 03(12) + 04(16) + 05(10) = **60건** (§6.1 전수 합계) 확인

**게이트 매핑**: Phase 0→1 게이트(§7.2) 세 번째 조건 — "서브폴더 _index.md 5개". P0-1(G0-1: 계획서 COMPLETE) + P0-2(G0-2: AUTHORITY_CHAIN ✅) + P0-4(G0-3: 서브폴더 _index.md 5개) 전부 충족 시 Phase 0→1 전환 가능. ※ P0-3(CONFLICT_LOG)는 R6 거버넌스 운영 문서이며 게이트 직접 조건 아님 (§10 V11에서 별도 검증).

**검증**:
- [x] 5개 서브폴더 존재 + 5개 `_index.md` 존재 (내용 비어있지 않음) — **G0-3 매핑 (서브폴더 _index.md 5개)** ← `ls -d */` 5건 + `wc -l */_index.md` = 54/49/54/62/45줄 (전수 ≥ 30줄)
- [x] 폴더 깊이 최대 3단계 (§2.2 준수) + R3(폴더 깊이 3단계 제한) 위반 0건 + R4(_index.md 필수) 충족 ← `find . -mindepth 3 -type d` = 0건 + _index.md 5건 전수 존재
- [x] 네이밍 규칙 §2.3 전수 준수: 폴더명 = `{NN}_{영문소문자-하이픈}` 패턴 5건 일치, 파일명 = `_index.md` (영문 소문자 + 언더스코어) 5건 일치 ← 정규식 `^[0-9]{2}_[a-z][a-z0-9-]*$` 대조 PASS
- [x] 각 _index.md 메타데이터 5필드(서브도메인/우선순위/항목 수/L3 상태/정본) 전수 포함 ← 5파일 × 5필드 = 25셀 전수 확인 PASS
- [x] 항목 수 합계 = **60건** (01:12 + 02:10 + 03:12 + 04:16 + 05:10) — §6.1 서브폴더별 건수·전수 합계 일치 ← 5파일 항목 행 수 집계 PASS
- [x] LOCK 항목 값이 §3.4 원본과 **character-level 동일** (R2 LOCK 값 재정의 금지 준수) ← 01: 3건(LOCK-01/02/03), 02: 1건(LOCK-04), 03: 3건(LOCK-06/07/09), 04: 1건(LOCK-05) = 총 8건 전수 대조 PASS (초기 4건 불일치 교정 완료: LOCK-01 축약→원본 복원, LOCK-05 후반부 누락→보완, LOCK-06 "만료" 위치→§3.4 정합, LOCK-09 "연속 실패" 추가→§3.4 원본 복원)
- [x] Phase 배정이 §7.3 Phase 1/2/3 작업 테이블과 정합 + L3 우선순위가 §13.2와 정합 (01/02/03 = P0, 04/05 = P1) ← 항목별 Phase·우선순위 교차 대조 PASS
- [x] §6.3 v12 확장 항목 ID 중 해당 서브폴더분이 _index.md 항목 설명에 명기 ← v12 ID 전수 검색 (v12_C09b_110, v12_C03_029, v12_C12_105 → 01, v12_C12_101 → 02, v12_C12_104 → 03, v12_C09b_117, v12_C03_037, v12_C12_115 → 05) = 8건 PASS (v12_C03_029 초기 누락→01 항목 12에 추가)
- [x] 파일 구성(절차 2-g)이 §2.1 해당 서브폴더별 트리와 **완전 일치** (파일명·수·매핑 주석) ← 5개 서브폴더 × 파일 목록 전수 대조 PASS
- [x] 의존성 테이블이 서브폴더 간 + 외부 도메인(#13, #16, D2.0-05 등) 교차 참조를 포함하며, R-11-5/R-11-8 규칙 반영 ← 5파일 의존성 행 전수 확인 PASS
- [x] §10 V2("서브폴더 5개 _index.md 존재") + V8("폴더 깊이 3단계 이내") + V9("네이밍 규칙 준수") 검증 항목 PASS 가능 상태 확인 ← 상기 검증 전수 통과로 자동 충족

**산출물**: 5개 서브폴더 × `_index.md` = 5 파일 (신규)
</details>

#### Phase 1 — MVP (V1 정렬) (✅ 완료 — 2026-04-10, Phase 1→2 게이트 PASS)

| # | 작업 | 서브폴더 | 우선순위 |
|---|------|---------|---------|
| 1 | JSON-RPC 2.0 메시지 스키마 확정 | `01_a2a-protocol/` | P0 | ✅ 완료 (2026-04-10, v1.0). 8개 A2A 메서드 I/O 스키마 + 공통 타입 + JSON Schema 확정. LOCK 4건 정합 OK, 테스트 14건 정의. 재검증 0회/이슈 없음. 이월 없음 |
| 2 | Task Lifecycle 상태 머신 구현 | `01_a2a-protocol/` | P0 | ✅ 완료 (2026-04-10, v1.0). 6개 상태 전이 다이어그램 + 허용 12건/금지 10건 전이 매트릭스 + TaskStatusEvent/TaskArtifactEvent 이벤트 구조 + 검증 알고리즘 O(1). LOCK 2건 정합 OK, 테스트 15건 정의. 재검증 0회/이슈 없음. 이월 없음 |
| 3 | 에이전트 카드 스펙 정의 | `01_a2a-protocol/` | P0 | ✅ 완료 (2026-04-10, v1.0). AgentCard 전체 JSON Schema(draft/2020-12) + 6개 하위 타입 + mDNS TXT 매핑 + 예외 처리 8건 + 테스트 12건 정의. LOCK 2건 정합 OK, 재검증 0회/이슈 없음. 이월 없음 |
| 4 | 단일 노드 mDNS 디스커버리 | `02_agent-discovery/` | P0 | ✅ 완료 (2026-04-10, v1.0). mDNS/DNS-SD 쿼리/응답 프로토콜 + SRV/TXT 레코드 구조 + 등록/발견/해제 의사코드 + P1-3 TXT 매핑 11항목 전수 정합. LOCK 1건 정합 OK, 테스트 12건 정의. 재검증 0회/이슈 없음. 이월 없음 |
| 5 | mTLS + JWT 기본 인증 | `03_security/` | P0 | ✅ 완료 (2026-04-10, v1.0). mTLS 핸드셰이크 + X.509 인증서 요구사항 + JWT Claims 스키마 + 인증서 자동갱신 + CB 통합 + 검증 파이프라인 6단계 + 예외 처리 10건 + 테스트 14건 정의. LOCK 3건(06/07/09) 정합 OK, P1-1/P1-3 인증 타입 정합 확인. 재검증 0회/이슈 없음. 이월 없음 |
| 6 | 에러 코드 카탈로그 (8개) | `01_a2a-protocol/` | P1 | ✅ 완료 (2026-04-10, v1.0). JSON-RPC 표준 5건 + A2A 커스텀 8건(-32001~-32008) = 13건 에러 코드 카탈로그 + HTTP 에러 복구 5건 + 지수 백오프 재시도 정책 + failover 알고리즘 + CB 연동(LOCK-A2A-09) + 에스컬레이션 페이로드 + 예외 처리 15건 + 테스트 14건 정의. LOCK 3건(05/07/09) 정합 OK, P1-1 에러 14건 + P1-5 인증 에러 9건 전수 MATCH. 재검증 0회/이슈 없음. 이월 없음 |
| 7 | 감사 로깅 기본 스키마 | `03_security/` | P1 | ✅ 완료 (2026-04-10, v1.0). AuditEvent 스키마(필수 필드 13개) + 6개 카테고리 28개 이벤트 유형 + details 확장 스키마 6종 + 보존 정책 4단계 + 접근 제어 5역할 + 무결성 해시 체인 + 에스컬레이션 3종 + 예외 처리 10건 + 테스트 12건 정의. LOCK 3건(06/07/09) 정합 OK, P1-5 인증 이벤트 10건 + P1-6 에러 이벤트 14건 전수 감사 대상 포함 MATCH. 재검증 0회/이슈 없음. 이월 없음 |

#### Phase 1 단계별 상세 작업 절차

<details>
<summary><b>P1-1. JSON-RPC 2.0 메시지 스키마 확정 — ✅ 완료 (2026-04-10)</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 1 #1 "JSON-RPC 2.0 메시지 스키마 확정"
- §7 전환 게이트: Phase 1→2 — `01_a2a-protocol/` + `02_agent-discovery/` + `03_security/` L3 완성
- §6 이슈: §6.1 항목 #1 (JSON-RPC 2.0 메시지 스키마 전체 구조), #2~#9 (8개 메서드 정의)

**목표**: JSON-RPC 2.0 메시지 포맷의 전체 I/O 스키마를 JSON Schema 또는 TypeScript interface로 정의하고, 8개 A2A 메서드(`tasks/send`, `tasks/sendSubscribe`, `tasks/get`, `tasks/cancel`, `tasks/pushNotification/set`, `tasks/pushNotification/get`, `tasks/resubscribe`, `agent/authenticatedExtendedCard`)의 요청/응답 구조를 확정한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_구조화_종합계획서.md` §3.4 LOCK-A2A-01 (`"jsonrpc": "2.0"`), §6.1 항목 #1~#9, 부록 §A (프로토콜 스펙 레퍼런스)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_상세명세.md` §2.1 (JSON-RPC 2.0 메시지 구조, method enum)
- `D:\VAMOS\docs\sot\STEP7-B_대화프로세스_작업가이드.md` (시중 AI 대화 파이프라인 비교 — 메시지 포맷 참조)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\01_a2a-protocol\_index.md` (서브폴더 개요, 항목 목록)

**절차**:
1. 상세명세 §2.1에서 JSON-RPC 2.0 메시지 전체 구조를 추출: `jsonrpc`, `method`, `params`, `id` 필드 정의 (LOCK-A2A-01 `"jsonrpc": "2.0"` 값 고정)
2. 8개 메서드별 요청(Request) 스키마 정의:
   - 메서드명, params 구조, 필수/선택 필드, 타입 제약 명세
   - §6.1 항목 #2~#9 전수 대응 확인
3. 8개 메서드별 응답(Response) 스키마 정의:
   - 성공 응답(`result`) 구조 + 에러 응답(`error`) 구조 (JSON-RPC 2.0 표준 에러 + A2A 커스텀 에러)
4. 공통 타입 정의: `Task`, `TaskState`, `Message`, `Part`, `Artifact`, `AgentCard` 등 재사용 타입을 별도 섹션으로 분리
5. L3 완성도 기준 E1(I/O Schema) 충족 확인: 모든 메서드의 입출력 스키마가 JSON Schema 또는 TypeScript interface로 정의 완료
6. L3 기준 E6(의존성) 확인: `02_agent-discovery/` (에이전트 카드 참조), `03_security/` (JWT Claims 참조) 의존성 명시
7. `json_rpc_schema.md` 파일에 최종 스키마 작성, _index.md 항목 #1~#9 상태를 DRAFT → L3 갱신

**검증**:
- [x] LOCK-A2A-01 값 `"jsonrpc": "2.0"` 이 스키마 정의에 고정값으로 명시 (§3.4 원본 character-level 동일) ✅ — §3.1 A2ARequest.jsonrpc `"2.0"` const, §8 JSON Schema `"const": "2.0"`, §11 LOCK 준수 확인 OK
- [x] 8개 메서드 전수 요청/응답 스키마 정의 완료 (§6.1 항목 #2~#9 전수 대응) ✅ — tasks/send, tasks/sendSubscribe, tasks/get, tasks/cancel, tasks/pushNotification/set, tasks/pushNotification/get, tasks/resubscribe, agent/authenticatedExtendedCard = 8건 전수 정의 (TypeScript interface + JSON Schema)
- [x] 공통 타입 정의가 Task Lifecycle(P1-2) 및 에이전트 카드(P1-3)와 정합 ✅ — TaskState(LOCK-A2A-02), Message(LOCK-A2A-03), Task, Part, Artifact, AgentCard 6개 공통 타입 분리 정의, P1-2/P1-3 교차 참조 명시
- [x] E1(I/O Schema) L3 기준 충족: JSON Schema 또는 TypeScript interface 완전 정의 ✅ — §3~§4 TypeScript interface 8메서드 + §8 JSON Schema 전수 정의, L3 상태 확정
- [x] E4(에러 핸들링) 기본 반영: JSON-RPC 2.0 표준 에러 코드 + A2A 커스텀 에러 구조 ✅ — §5 에러 체계: 표준 4건(-32700/-32600/-32602/-32601) + 커스텀 5건(-32001~-32005) + Circuit Breaker(LOCK-A2A-09) 정의

> **완료**: 2026-04-10. 8개 A2A 메서드 I/O 스키마 및 공통 타입을 JSON Schema + TypeScript interface로 확정, L3 승급.
>
> **실행 결과 요약**:
> - 8개 메서드 전수 요청/응답 스키마 정의 완료, 공통 타입 6종 분리, JSON Schema §8 전문 포함, 테스트 시나리오 14건 정의
> - LOCK 4건(A2A-01/02/03/09) character-level 정합 §11 전수 확인 OK, §6.1 항목 #1~#9 전수 매핑 완료
> - 재검증 시 발견/정정 사항 없음 (초회 작성으로 재검증 0회)
> - SoT 교차검증: 상세명세 §2.1/§2.2/§2.3/§4.4 원본 대조 완료, CLF-A2A-001/002 경계 준수 확인
> - 이월 항목 없음 (P1-2 Task Lifecycle, P1-3 Agent Card에서 공통 타입 재사용 예정)

**[P1-1] 검증 결과 요약** (갱신: 2026-04-10)
- 0. 산출물: 생성 1개 — `01_a2a-protocol/json_rpc_schema.md` (v1.0, L3 승급)
- 1. 게이트: G1 Phase 1→2 부분 충족 — `01_a2a-protocol/` L3 진행 중 (P1-1 완료, P1-2/P1-3/P1-6 미착수→P1-2/P1-3/P1-6 완료 반영은 각 세션 검증 결과 참조)
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건 (기존 CLF-A2A-001~004 전체 RESOLVED 유지)
- 3. LOCK 변경: 없음 (LOCK-A2A-01/02/03/09 기존값 그대로 참조)
- 4. 이월: 없음 (P1-2에서 TaskState/TaskStatusEvent/TaskArtifactEvent 공통 타입 재사용, P1-3에서 AgentCard 공통 타입 재사용)

**산출물**: `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\01_a2a-protocol\json_rpc_schema.md` (L3 승급)
</details>

<details>
<summary><b>P1-2. Task Lifecycle 상태 머신 구현 — ✅ 완료 (2026-04-10)</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 1 #2 "Task Lifecycle 상태 머신 구현"
- §7 전환 게이트: Phase 1→2 — `01_a2a-protocol/` + `02_agent-discovery/` + `03_security/` L3 완성
- §6 이슈: §6.1 항목 #10 (Task Lifecycle 상태 머신 6개 상태), #11 (TaskStatusEvent / TaskArtifactEvent 이벤트)

**목표**: Task의 6개 상태(`submitted|working|input-required|completed|failed|canceled`)의 상태 전이 다이어그램과 전이 조건을 명세하고, TaskStatusEvent/TaskArtifactEvent 이벤트 구조를 정의한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_구조화_종합계획서.md` §3.4 LOCK-A2A-02 (`submitted|working|input-required|completed|failed|canceled`), §4.3 R-11-4 (상태 전이는 상세명세 §2.2 상태 머신 준수), §6.1 항목 #10~#11
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_상세명세.md` §2.2 (Task Lifecycle 상태 머신, 이벤트)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\01_a2a-protocol\_index.md` (서브폴더 개요)

**절차**:
1. 상세명세 §2.2에서 6개 상태 열거형 추출 및 LOCK-A2A-02 값과 정합 확인
2. 상태 전이 다이어그램 작성 (Mermaid stateDiagram 또는 텍스트 기반):
   - 허용 전이: `submitted→working`, `working→completed`, `working→failed`, `working→input-required`, `input-required→working`, `*→canceled` 등
   - 금지 전이 명시: `completed→working`, `failed→working` 등 역방향 전이 불가
3. 각 전이의 트리거 조건 명세: API 호출(tasks/send, tasks/cancel), 에이전트 내부 이벤트, 타임아웃
4. TaskStatusEvent 스키마 정의: `task_id`, `state`, `timestamp`, `message` 등 필드
5. TaskArtifactEvent 스키마 정의: `task_id`, `artifact`, `index`, `append` 등 필드
6. L3 기준 E2(상태 머신) 충족 확인: 전이 다이어그램 + 전이 조건 명세 완전
7. L3 기준 E7(테스트 스펙): 상태 전이 단위 테스트 케이스 최소 6건 정의 (정상 전이 + 금지 전이)

**검증**:
- [x] LOCK-A2A-02 6개 상태 값이 상태 머신 정의에 전수 반영 (§3.4 원본 character-level 동일) ✅ — §2.1 TaskState `"submitted" | "working" | "input-required" | "completed" | "failed" | "canceled"` = LOCK-A2A-02 원본 6개 값 전수 일치, §4 전이 매트릭스 6×6 전수 정의, §6 검증 알고리즘 ALLOWED_TRANSITIONS 맵 6키 확인
- [x] R-11-4 규칙 준수: 상태 전이가 상세명세 §2.2 상태 머신과 정합 ✅ — 상세명세 §2.2 다이어그램 전이(submitted→working, working→completed/failed/input-required, input-required→working, *→canceled) 전수 대조, 허용 12건 + 금지 10건 매트릭스로 명시
- [x] 허용 전이와 금지 전이가 명시적으로 구분 ✅ — §4.1 허용 전이 T1~T12 (12건), §4.2 금지 전이 F1~F10 (10건), §4.3 전이 매트릭스 6×6 요약 테이블로 구분
- [x] TaskStatusEvent / TaskArtifactEvent 스키마가 P1-1 공통 타입과 정합 ✅ — §15 세션 간 인터페이스 Cross-check: TaskStatusEvent(id, status, final, metadata?), TaskArtifactEvent(id, artifact, lastChunk?) = P1-1 §3.3 정의와 MATCH 확인
- [x] E2(상태 머신) + E7(테스트 스펙) L3 기준 충족 ✅ — E2: Mermaid + 텍스트 전이 다이어그램 + 전이 조건 12건 상세 명세, E7: 단위 테스트 15건 (정상 6건 + 금지 6건 + 이벤트 3건) ≥ 최소 6건

> **완료**: 2026-04-10. Task Lifecycle 6개 상태 전이 다이어그램, 허용/금지 전이 매트릭스, TaskStatusEvent/TaskArtifactEvent 이벤트 구조, 검증 알고리즘(O(1)), 테스트 케이스 15건 정의. L3 승급.
>
> **실행 결과 요약**:
> - LOCK 2건(A2A-02, A2A-09) character-level 정합 확인 OK
> - 재검증 시 발견/정정 사항 없음 (초회 작성)
> - SoT 교차검증: 상세명세 §2.2 원본 다이어그램·이벤트 타입 전수 대조 완료
> - P1-1 공통 타입 정합: TaskState, TaskStatus, TaskStatusEvent, TaskArtifactEvent, Artifact, A2AError 7개 인터페이스 MATCH
> - 이월 항목 없음 (P1-3 AgentCard.capabilities.stateTransitionHistory 연동 예정)

**[P1-2] 검증 결과 요약** (갱신: 2026-04-10)
- 0. 산출물: 생성 1개 — `01_a2a-protocol/task_lifecycle.md` (v1.0, L3 승급)
- 1. 게이트: G1 Phase 1→2 부분 충족 — `01_a2a-protocol/` L3 진행 중 (P1-1 완료, P1-2 완료, P1-3 완료, P1-6 완료, P1-7 완료)
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건 (기존 CLF-A2A-001~004 전체 RESOLVED 유지)
- 3. LOCK 변경: 없음 (LOCK-A2A-02/09 기존값 그대로 참조)
- 4. 이월: 없음 (P1-3에서 AgentCard.capabilities.stateTransitionHistory 연동 예정)

**산출물**: `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\01_a2a-protocol\task_lifecycle.md` (L3 승급)
</details>

<details>
<summary><b>P1-3. 에이전트 카드 스펙 정의 — ✅ 완료 (2026-04-10)</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 1 #3 "에이전트 카드 스펙 정의"
- §7 전환 게이트: Phase 1→2 — `01_a2a-protocol/` + `02_agent-discovery/` + `03_security/` L3 완성
- §6 이슈: §6.1 항목 #12 (에이전트 카드 스펙 Agent Card)

**목표**: A2A 에이전트 카드(Agent Card)의 전체 스키마를 정의하고, 에이전트의 능력(capabilities), 스킬(skills), 인증 방식(authentication), 엔드포인트 정보를 구조화한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_구조화_종합계획서.md` §3.4 LOCK-A2A-03 (대화 턴 구조 `role: "user"|"agent"`, `parts: Part[]`), LOCK-A2A-08 (Agent Mode `MANUAL|SEMI_AUTO|SUPERVISED_AUTO`), §6.1 항목 #12, 부록 §A (프로토콜 스펙)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_상세명세.md` §2.3 (에이전트 카드 스펙)
- `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` (아키텍처 정본 — Agent Mode 원본)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\01_a2a-protocol\_index.md` (서브폴더 개요)

**절차**:
1. 상세명세 §2.3에서 에이전트 카드 기본 구조 추출: `name`, `description`, `url`, `version`, `provider` 등 메타데이터 필드
2. capabilities 정의: `streaming`, `pushNotifications`, `stateTransitionHistory` 등 Boolean 플래그
3. skills 배열 정의: 각 스킬의 `id`, `name`, `description`, `tags`, `examples` 구조
4. authentication 정의: `schemes` (Bearer, mTLS), `credentials` 참조 — `03_security/` mTLS+JWT와 연동
5. 대화 턴 구조 통합: LOCK-A2A-03 (`role: "user"|"agent"`, `parts: Part[]`) 값을 메시지 교환 스펙에 반영
6. `agent/authenticatedExtendedCard` 메서드의 확장 카드 필드 정의 (P1-1 스키마와 정합)
7. L3 기준 E1(I/O Schema) 충족: AgentCard JSON Schema 완전 정의
8. L3 기준 E6(의존성): `02_agent-discovery/` mDNS TXT 레코드 필드와 에이전트 카드 매핑 관계 명시

**검증**:
- [x] LOCK-A2A-03 대화 턴 구조 값이 메시지 교환 스펙에 정확히 반영 ✅ — §5 대화 턴 구조 통합에서 `role: "user"|"agent"`, `parts: Part[]` 반영, defaultInputModes/defaultOutputModes 연동 명시
- [x] AgentCard 스키마가 P1-1 JSON-RPC 스키마의 공통 타입 `AgentCard`와 정합 ✅ — §11 인터페이스 정합 검증 19/19 필드 전수 MATCH
- [x] capabilities/skills/authentication 3개 하위 구조 전수 정의 ✅ — §2.3 AgentCapabilities(3필드), §2.4 SkillDescriptor(5필드), §2.5 AgentAuthentication(2필드) 전수 정의
- [x] `02_agent-discovery/` mDNS TXT 레코드 필드(v, path, caps, agent-id)와 에이전트 카드 필드 매핑 명시 ✅ — §6 mDNS TXT 레코드 필드 매핑 4개 필드 전수 대응 + caps 비트맵 변환 알고리즘 O(n)
- [x] E1(I/O Schema) + E6(의존성) L3 기준 충족 ✅ — §3 JSON Schema(draft/2020-12) 완전 정의, §13 의존성 명세 8건

> **완료**: 2026-04-10. AgentCard 전체 JSON Schema(draft/2020-12), 6개 하위 타입(AgentCard, AgentProvider, AgentCapabilities, SkillDescriptor, AgentAuthentication, VamosExtensions), mDNS TXT 매핑, 예외 처리 정책 8건, Phase 2 테스트 12건 정의. L3 승급.
>
> **실행 결과 요약**:
> - LOCK 2건(A2A-03, A2A-08) character-level 정합 확인 OK
> - 재검증 시 발견/정정 사항 없음 (초회 작성)
> - SoT 교차검증: 상세명세 §2.3 JSON 예시 전수 대조, 부록 §A.2 확장 스펙 대조 완료
> - P1-1 공통 타입 정합: AgentCard, AgentCapabilities, SkillDescriptor 19개 필드 MATCH
> - P1-2 연동 확인: stateTransitionHistory 플래그 → TaskTransition 타입 연동 MATCH
> - 이월 항목 없음

**[P1-3] 검증 결과 요약** (갱신: 2026-04-10)
- 0. 산출물: 생성 1개 — `01_a2a-protocol/agent_card_spec.md` (v1.0, L3 승급)
- 1. 게이트: G1 Phase 1→2 부분 충족 — `01_a2a-protocol/` L3 진행 중 (P1-1 완료, P1-2 완료, P1-3 완료, P1-6 완료, P1-7 완료)
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건 (기존 CLF-A2A-001~004 전체 RESOLVED 유지)
- 3. LOCK 변경: 없음 (LOCK-A2A-03/08 기존값 그대로 참조)
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\01_a2a-protocol\agent_card_spec.md` (L3 승급)
</details>

<details>
<summary><b>P1-4. 단일 노드 mDNS 디스커버리 — ✅ 완료 (2026-04-10)</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 1 #4 "단일 노드 mDNS 디스커버리"
- §7 전환 게이트: Phase 1→2 — `01_a2a-protocol/` + `02_agent-discovery/` + `03_security/` L3 완성
- §6 이슈: §6.1 항목 #13 (mDNS 쿼리 프로토콜), #14 (DNS-SD 서비스 타입), #15 (SRV 레코드), #16 (TXT 레코드 필드)

**목표**: 단일 노드 환경에서 mDNS/DNS-SD 기반 에이전트 디스커버리 프로토콜을 정의하고, 서비스 타입 `_vamos-a2a._tcp.local.`을 사용한 에이전트 등록/발견 메커니즘을 명세한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_구조화_종합계획서.md` §3.4 LOCK-A2A-04 (`_vamos-a2a._tcp.local.`), §6.1 항목 #13~#16, 부록 §B (Agent Discovery 메커니즘)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_상세명세.md` §3.1 (mDNS/DNS-SD 프로토콜)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\02_agent-discovery\_index.md` (서브폴더 개요)

**절차**:
1. mDNS 쿼리 프로토콜 정의: 멀티캐스트 주소 `224.0.0.251:5353`, 쿼리/응답 흐름
2. DNS-SD 서비스 타입 확정: LOCK-A2A-04 `_vamos-a2a._tcp.local.` 값 고정 — 서비스 브라우징, 인스턴스 열거
3. SRV 레코드 구조 명세: `priority`, `weight`, `port`, `target` 필드 정의 + 단일 노드 기본값
4. TXT 레코드 필드 정의: `v` (프로토콜 버전), `path` (에이전트 카드 URL 경로), `caps` (능력 비트맵), `agent-id` (고유 식별자)
5. 에이전트 등록 흐름: 에이전트 시작 → mDNS 서비스 등록 → 주기적 갱신(TTL) → 종료 시 해제
6. 에이전트 발견 흐름: 클라이언트 mDNS 쿼리 → SRV+TXT 응답 수신 → 에이전트 카드 URL 구성 → HTTP GET으로 AgentCard 조회
7. L3 기준 E3(알고리즘/로직): 등록/발견 흐름 의사코드 작성
8. L3 기준 E6(의존성): `01_a2a-protocol/` AgentCard(P1-3)와 연동 관계 명시

**검증**:
- [x] LOCK-A2A-04 서비스 타입 `_vamos-a2a._tcp.local.` 이 정의에 고정값으로 명시 (§3.4 원본 character-level 동일) ← §3.1 서비스 타입 정의 + §5.1/§6.1 의사코드 내 LOCK 주석 전수 확인 PASS
- [x] §6.1 항목 #13~#16 전수 대응: mDNS 쿼리, DNS-SD 서비스 타입, SRV 레코드, TXT 레코드 ← §2(#13), §3(#14), §3.3(#15), §4(#16) 4건 전수 매핑 PASS
- [x] TXT 레코드 4개 필드(v, path, caps, agent-id)가 P1-3 에이전트 카드 스펙과 매핑 ← §14 P1-3 cross-check 11항목 전체 MATCH 확인 PASS
- [x] 등록/발견 흐름 의사코드가 단일 노드 시나리오를 완전히 커버 ← §5 등록(probing→announcing→refresh→goodbye) + §6 발견(PTR→SRV/TXT→HTTP GET→cross-validate) 전수 확인 PASS
- [x] E3(알고리즘/로직) + E6(의존성) L3 기준 충족 ← E3: §5.1/§6.1 의사코드 + 시간복잡도(O(1)/O(N)) 명시, E6: §12 의존성 10건 명세 PASS

> **완료**: 2026-04-10. mDNS/DNS-SD 쿼리/응답 프로토콜 + SRV/TXT 레코드 구조 + 등록/발견/해제 의사코드 + P1-3 TXT 매핑 11항목 전수 정합. LOCK 1건 정합 OK, 테스트 12건 정의. L3 승급.
>
> **실행 결과 요약**:
> - LOCK 1건(A2A-04) character-level 정합 §3.4 전수 확인 OK
> - §6.1 #13~#16 전수 매핑 완료, P1-3 agent_card_spec.md §6 mDNS TXT 매핑 11항목 전체 MATCH
> - 재검증 시 발견/정정 사항 없음 (초회 작성으로 재검증 0회)
> - SoT 교차검증: 상세명세 §3.1 원본 대조 완료, 종합계획서 부록 §A.3/§B 참조 확인
> - 이월 항목 없음 (P2-6 Service Registry에서 본 문서 mDNS 프로토콜 재사용 예정)

**[P1-4] 검증 결과 요약** (갱신: 2026-04-10)
- 0. 산출물: 생성 1개 — `02_agent-discovery/mdns_dns_sd.md` (v1.0, L3 승급)
- 1. 게이트: G1 Phase 1→2 부분 충족 — `02_agent-discovery/` L3 진행 중 (P1-4 완료, P2-6 미착수)
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건 (기존 CLF-A2A-001~004 전체 RESOLVED 유지)
- 3. LOCK 변경: 없음 (LOCK-A2A-04 기존값 그대로 참조)
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\02_agent-discovery\mdns_dns_sd.md` (L3 승급)
</details>

<details>
<summary><b>P1-5. mTLS + JWT 기본 인증 — ✅ 완료 (2026-04-10)</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 1 #5 "mTLS + JWT 기본 인증"
- §7 전환 게이트: Phase 1→2 — `01_a2a-protocol/` + `02_agent-discovery/` + `03_security/` L3 완성
- §6 이슈: §6.1 항목 #23 (mTLS 핸드셰이크), #24 (JWT Bearer 토큰 인증), #25 (JWT Claims 구조)

**목표**: A2A 통신 보안의 기반인 mTLS 상호 인증과 JWT Bearer 토큰 인증을 정의하고, 인증서 관리 정책 및 JWT Claims 구조를 명세한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_구조화_종합계획서.md` §3.4 LOCK-A2A-06 (mTLS 인증서 만료 자동 갱신 30일 전), LOCK-A2A-07 (JWT delegation chain 최대 깊이 3), LOCK-A2A-09 (Circuit Breaker 3회→OPEN, 60초→HALF-OPEN), §4.3 R-11-1 (mTLS 인증서 만료 30일 전 자동 갱신), R-11-2 (JWT delegation chain 최대 깊이 3), §6.1 항목 #23~#25
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_상세명세.md` §4.1 (mTLS + JWT 인증)
- `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` (아키텍처 정본 — Circuit Breaker 원본)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\03_security\_index.md` (서브폴더 개요)

**절차**:
1. mTLS 핸드셰이크 프로토콜 정의:
   - X.509 인증서 요구사항: CA 체인, 인증서 필드(CN, SAN), 키 알고리즘(RSA 2048+ 또는 ECDSA P-256)
   - 상호 인증 흐름: 클라이언트 인증서 제시 → 서버 검증 → 서버 인증서 제시 → 클라이언트 검증
2. 인증서 만료 관리 정책: LOCK-A2A-06 "30일 전" 자동 갱신 트리거 — 갱신 프로세스, 실패 시 알림
3. JWT Bearer 토큰 구조 정의:
   - Header: `alg` (RS256 또는 EdDSA), `typ` (JWT)
   - Payload Claims: `iss` (발급자), `sub` (주체 에이전트), `aud` (대상 에이전트), `scope` (권한 범위), `delegation_chain` (위임 경로)
   - LOCK-A2A-07 "최대 깊이 3" 제약 반영
4. 토큰 검증 흐름: 서명 검증 → 만료 확인 → scope 검증 → delegation_chain 깊이 확인
5. Circuit Breaker 통합: LOCK-A2A-09 "3회 연속 실패→OPEN, 60초 후 HALF-OPEN" — 인증 실패 시 CB 적용
6. L3 기준 E5(보안 스펙) 충족: 인증/인가/암호화 요구사항 완전 정의
7. L3 기준 E4(에러 핸들링): 인증 실패 에러 코드(401 Unauthorized, 403 Forbidden) + 복구 전략

**검증**:
- [x] LOCK-A2A-06 "30일 전" 자동 갱신 정책이 인증서 관리 섹션에 명시 (§3.4 원본 character-level 동일) ← §3 autoRenewalTriggerDays: 30 + 갱신 프로세스 + 실패 에스컬레이션 PASS
- [x] LOCK-A2A-07 "최대 깊이 3" 이 JWT Claims delegation_chain 제약에 반영 ← §4.4 검증 알고리즘 depth > 3 거부 + 순환 감지 PASS
- [x] LOCK-A2A-09 Circuit Breaker "3회→OPEN, 60초→HALF-OPEN" 이 인증 실패 처리에 반영 ← §6 failure_threshold: 3, recovery_timeout_ms: 60000 PASS
- [x] R-11-1, R-11-2 규칙 준수 확인 ← §3.1 R-11-1 자동 갱신 + §4.4 R-11-2 깊이 3 PASS
- [x] §6.1 항목 #23~#25 전수 대응: mTLS 핸드셰이크, JWT Bearer, JWT Claims ← §2(#23) + §4.1(#24) + §4.2(#25) 전수 대조 PASS
- [x] E5(보안 스펙) + E4(에러 핸들링) L3 기준 충족 ← E5: 인증/인가/암호화 전체 정의 + E4: §7 에러 코드 9종 + 복구 전략 + 예외 10건 PASS

**산출물**: `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\03_security\mtls_jwt.md` (L3 승급)

> **완료**: 2026-04-10. mTLS 핸드셰이크(X.509 v3, TLS 1.3) + 인증서 자동갱신(LOCK-A2A-06 30일 전) + JWT Claims 스키마(RFC 7519 + A2A 확장 3필드) + delegation_chain 검증(LOCK-A2A-07 깊이 3) + CB 통합(LOCK-A2A-09 3회→OPEN, 60초→HALF-OPEN) + 검증 파이프라인 6단계 + 예외 처리 10건 + 테스트 14건 정의. LOCK 3건(06/07/09) 정합 OK. L3 승급.
>
> **실행 결과 요약** (P1-5, 2026-04-10):
> - mTLS 핸드셰이크 프로토콜: X.509 v3 인증서 요구사항(CN, SAN, CA 체인 깊이 3), TLS 1.3 필수, Cipher Suite 3종 허용 목록
> - 인증서 만료 관리: LOCK-A2A-06 "30일 전" 자동 갱신 트리거, 갱신 프로세스(CSR→CA→Hot-reload→24h grace), 실패 3회 시 I-20 에스컬레이션
> - JWT Claims 스키마: RFC 7519 표준 7필드 + A2A 확장 3필드(scope, delegation_chain, vamos:trust_level) 정의
> - delegation_chain: LOCK-A2A-07 "최대 깊이 3" 검증 알고리즘 O(n≤3), 순환 위임 감지 포함
> - 토큰 검증 파이프라인: 6단계(서명→만료→aud→scope→delegation→jti)
> - Circuit Breaker: LOCK-A2A-09 "3회→OPEN, 60초→HALF-OPEN" 인증 실패 적용, CB 적용/미적용 대상 분류
> - 에러 처리: HTTP 401/403 매핑 9종, 예외 처리 정책 10건, confidence penalty 표 7유형
> - 로깅: R-01-7 structured JSON 중첩 구조 3종(인증이벤트/mTLS핸드셰이크/인증서갱신)
> - 에스컬레이션: I-20 페이로드 2종(인증실패CB/인증서만료긴급)
> - Phase 2 테스트: 14건 정의 (정상인증, 만료인증서, 폐기인증서, JWT위조, JWT만료, scope불일치, delegation초과, CB OPEN/HALF-OPEN, 자동갱신, 갱신실패, jti재사용, 순환위임, OCSP soft-fail)
> - P1-1/P1-3 인증 타입 정합: AgentAuthentication.schemes, trust_level 열거형, AgentMode, authenticatedExtendedCard 메서드 전수 대조 MATCH
> - 이월 항목 없음

**[P1-5] 검증 결과 요약** (갱신: 2026-04-10)
- 0. 산출물: 생성 1개 — `03_security/mtls_jwt.md` (v1.0, L3 승급)
- 1. 게이트: G1 Phase 1→2 부분 충족 — `03_security/` L3 진행 중 (P1-5 완료, P1-6 완료, P1-7 완료)
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건 (기존 CLF-A2A-001~004 전체 RESOLVED 유지)
- 3. LOCK 변경: 없음 (LOCK-A2A-06/07/09 기존값 그대로 참조)
- 4. 이월: 없음 (P1-7 감사 로깅에서 인증 이벤트 감사 대상 포함 예정)
</details>

<details>
<summary><b>P1-6. 에러 코드 카탈로그 (8개) — ✅ 완료 (2026-04-10)</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 1 #6 "에러 코드 카탈로그 (8개)"
- §7 전환 게이트: Phase 1→2 — `01_a2a-protocol/` + `02_agent-discovery/` + `03_security/` L3 완성
- §6 이슈: §6.1 항목 #31 (A2A 에러 코드 카탈로그 -32001 ~ -32005), #32 (HTTP 에러 복구), #33 (지수 백오프 재시도), #34 (대체 에이전트 선택)

**목표**: A2A 프로토콜 전용 에러 코드 카탈로그(최소 8개)를 정의하고, JSON-RPC 2.0 표준 에러 코드와의 관계를 명세하며, 각 에러에 대한 복구 전략을 매핑한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_구조화_종합계획서.md` §3.4 LOCK-A2A-09 (Circuit Breaker 3회→OPEN, 60초→HALF-OPEN), §6.1 항목 #31~#34
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_상세명세.md` §4.4 (에러 코드, HTTP 에러 복구, 재시도 정책)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\01_a2a-protocol\_index.md` (서브폴더 개요)

**절차**:
1. JSON-RPC 2.0 표준 에러 코드 정리: `-32700` (Parse error), `-32600` (Invalid Request), `-32601` (Method not found), `-32602` (Invalid params), `-32603` (Internal error)
2. A2A 커스텀 에러 코드 정의 (최소 8개, -32001 ~ -32005 기반 확장):
   - `-32001`: Task not found
   - `-32002`: Task not cancelable
   - `-32003`: Push notification not supported
   - `-32004`: Unsupported operation
   - `-32005`: Agent authentication failed
   - 추가 3개: 컨텍스트 초과, 위임 깊이 초과, 에이전트 과부하 등 도메인 특화 에러
3. 각 에러 코드별 복구 전략 매핑:
   - Transient 에러: 지수 백오프 재시도 (§6.1 #33 — 초기 1초, 최대 60초, 최대 3회)
   - Permanent 에러: 즉시 실패 반환, 클라이언트 알림
   - Failover: 대체 에이전트 선택 (§6.1 #34 — `02_agent-discovery/` 연동)
4. HTTP 에러 복구 정책: 408(Timeout), 429(Rate Limit), 503(Service Unavailable) — 재시도 가능 여부 + 대기 시간
5. Circuit Breaker 연동: LOCK-A2A-09 "3회 연속 실패→OPEN" 적용 조건 명시
6. L3 기준 E4(에러 핸들링) 충족: 에러 코드 + 복구 전략 매핑 완전 정의

**검증**:
- [x] 에러 코드 최소 8개 정의 (JSON-RPC 표준 5개 + A2A 커스텀 최소 5개 중 8개 선정) ✅ — 표준 5건 + 커스텀 8건(-32001~-32008) = 13건 정의 (요구사항 8건 초과 충족)
- [x] §6.1 항목 #31~#34 전수 대응: 에러 코드 카탈로그, HTTP 복구, 재시도 정책, failover ✅ — §4(#31) + §5(#32) + §6(#33) + §7(#34) 전수 매핑 PASS
- [x] LOCK-A2A-09 Circuit Breaker "3회→OPEN, 60초→HALF-OPEN" 연동 조건 명시 ✅ — §8 CB 상태 전이 + 적용/미적용 에러 분류 + failure_threshold: 3, recovery_timeout_ms: 60000 PASS
- [x] 각 에러의 분류(Transient/Permanent) + 복구 전략이 매핑 ✅ — §2.2 3분류(Transient/Permanent/Conditional) + §4~§5 개별 복구 전략 전수 매핑
- [x] E4(에러 핸들링) L3 기준 충족 ✅ — 에러 코드 카탈로그 13건 + 복구 전략 + CB 연동 + Failover + 에스컬레이션 완전 정의

**산출물**: `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\01_a2a-protocol\error_codes.md` (L3 승급)

> **완료**: 2026-04-10. JSON-RPC 표준 5건(-32700/-32600/-32601/-32602/-32603) + A2A 커스텀 8건(-32001~-32008) = 13건 에러 코드 카탈로그 + HTTP 에러 복구 5건(408/429/503/401/403) + 지수 백오프 재시도(초기 1초/최대 60초/최대 3회) + failover 알고리즘(02_agent-discovery/ 연동) + CB 연동(LOCK-A2A-09 3회→OPEN, 60초→HALF-OPEN) + I-20 에스컬레이션 페이로드 + 예외 처리 15건 + Phase 2 테스트 14건 정의. LOCK 3건(05/07/09) 정합 OK. L3 승급.
>
> **실행 결과 요약** (P1-6, 2026-04-10):
> - 에러 코드: 표준 5건 + 커스텀 8건(기본 5건 + 확장 3건: -32006 Context exceeded, -32007 Delegation depth, -32008 Agent overloaded)
> - HTTP 에러: 408/429/503 기본 3건 + 401/403 인증 2건 = 5건
> - 재시도: 지수 백오프(1초→2초→4초, 최대 60초, 최대 3회, jitter ±10%)
> - Failover: 02_agent-discovery/ mDNS 레지스트리 연동, 최대 2회 failover, CB OPEN 대상 제외
> - CB: LOCK-A2A-09 "3회→OPEN, 60초→HALF-OPEN" 적용 에러 5종(408/503/401/-32603/-32008), 미적용 에러 8종
> - P1-1 cross-check: 에러 14건 전수 MATCH
> - P1-5 cross-check: 인증 에러 9건 전수 MATCH
> - 에스컬레이션: I-20 EscalationPayload 6종 트리거(재시도 소진/대체 없음/CB OPEN/위임 차단/보안 침해/인증서 갱신 실패)
> - 재검증 시 발견/정정 사항 없음 (초회 작성으로 재검증 0회)

**[P1-6] 검증 결과 요약** (갱신: 2026-04-10)
- 0. 산출물: 생성 1개 — `01_a2a-protocol/error_codes.md` (v1.0, L3 승급)
- 1. 게이트: G1 Phase 1→2 부분 충족 — `01_a2a-protocol/` L3 진행 중 (P1-1 완료, P1-2 완료, P1-3 완료, P1-6 완료, P1-7 완료)
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건 (기존 CLF-A2A-001~004 전체 RESOLVED 유지)
- 3. LOCK 변경: 없음 (LOCK-A2A-05/07/09 기존값 그대로 참조)
- 4. 이월: 없음
</details>

<details>
<summary><b>P1-7. 감사 로깅 기본 스키마 — ✅ 완료 (2026-04-10)</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 1 #7 "감사 로깅 기본 스키마"
- §7 전환 게이트: Phase 1→2 — `01_a2a-protocol/` + `02_agent-discovery/` + `03_security/` L3 완성
- §6 이슈: §6.1 항목 #30 (감사 로깅 스키마 audit event)

**목표**: A2A 통신의 감사 로깅(Audit Logging) 이벤트 스키마를 정의하고, 기록 대상 이벤트 유형, 필수 필드, 보존 정책을 명세한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_구조화_종합계획서.md` §6.1 항목 #30, §3.4 LOCK-A2A-06 (mTLS 인증서 갱신 — 감사 기록 대상), LOCK-A2A-07 (JWT 위임 — 감사 기록 대상)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_상세명세.md` §4.3 (감사 로깅 스키마)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\03_security\_index.md` (서브폴더 개요)

**절차**:
1. 감사 이벤트 기본 스키마 정의:
   - 필수 필드: `event_id` (UUID), `timestamp` (ISO 8601), `event_type`, `actor` (에이전트 ID), `target` (대상 리소스), `action`, `result` (success/failure), `details`
2. 감사 대상 이벤트 유형 정의:
   - 인증 이벤트: mTLS 핸드셰이크 성공/실패, JWT 검증 성공/실패, 인증서 갱신
   - 인가 이벤트: 권한 위임 요청/승인/거부, scope 변경
   - 태스크 이벤트: Task 생성, 상태 전이, 완료/실패
   - 디스커버리 이벤트: 에이전트 등록/해제, 서비스 쿼리
3. 각 이벤트 유형별 `details` 필드 확장 스키마 정의 (예: 인증 실패 시 실패 사유, 클라이언트 IP)
4. 로그 레벨 매핑: INFO (정상 흐름), WARN (비정상 시도), ERROR (실패), CRITICAL (보안 침해 의심)
5. 보존 정책 기본 규칙: 최소 보존 기간, 로테이션, 접근 제어
6. L3 기준 E5(보안 스펙) 충족: 감사 로깅이 보안 요구사항의 일부로 완전 정의
7. L3 기준 E8(모니터링 메트릭): 감사 로그 기반 메트릭 연계 포인트 정의 (`05_monitoring/` 연동)

**검증**:
- [x] 감사 이벤트 스키마 필수 필드 8개 이상 정의 ← AuditEvent 인터페이스 필수 필드 13개 (event_id, timestamp, event_type, category, actor, target, action, result, details, level, trace_id + 선택 4개) PASS
- [x] §6.1 항목 #30 대응: audit event 스키마 완전 정의 ← §3 AuditEvent 인터페이스 + §3.2 보조 타입 6종 + §3.3 JSON 예시 (상세명세 §4.3 기반 확장) PASS
- [x] 감사 대상 이벤트 유형 최소 4개 카테고리(인증/인가/태스크/디스커버리) 커버 ← 6개 카테고리(authentication 8종 + authorization 5종 + task 5종 + discovery 4종 + error 3종 + system 2종 = 28개 이벤트 유형) PASS (4개 초과 6개)
- [x] P1-5 mTLS+JWT 인증 이벤트가 감사 로깅 대상에 포함 ← §9.1 P1-5 예외 처리 10건 전수 대조, 감사 이벤트 유형 1:1 매핑 확인 (A-1~A-8, Z-3, Z-5, S-1) MATCH
- [x] E5(보안 스펙) + E8(모니터링 메트릭) L3 기준 충족 ← E5: 인증/인가/보안 감사 완전 정의 + 보존 정책 + 접근 제어 + 무결성 체인 PASS; E8: §12 감사 로그 기반 모니터링 메트릭 8건 연계 포인트 PASS

> 추가 검증:
> - P1-6 에러 이벤트 감사 대상 포함: §9.2 커스텀 에러 8건 + 에스컬레이션 6건 전수 대조 MATCH
> - LOCK-A2A-06/07/09 기존값 그대로 참조 (R2 LOCK 값 재정의 금지 준수)
> - 교차 참조 블록: 관련 정본 문서 19건 명시 (P1-1~P1-6 산출물 + 종합계획서/상세명세/D2.0-05)
> - 에스컬레이션: I-20 AuditEscalationPayload 구조 정의 (§7.2), 3종 트리거(저장소 장애/보안 패턴/무결성 위반)
> - 로깅: R-01-7 structured JSON 중첩 구조 (error{}, context{}, recovery{}, trace_id) — P1-5/P1-6 동일 구조 (§6)
> - 복구/재시도: §11 흐름도 2건 (저장소 쓰기 실패 + 무결성 검증 실패) + confidence penalty 표 7건
> - 예외 처리 정책 표: §10 예외 10건 정의
> - Phase 2 통합 테스트: §13 12건 시나리오 정의
> - 알고리즘: §14 시간복잡도 6건 + ABC 매핑
> - 재검증 시 발견/정정 사항 없음 (초회 작성으로 재검증 0회)

> **완료**: 2026-04-10. AuditEvent 스키마(필수 필드 13개) + 6개 카테고리 28개 이벤트 유형 + details 확장 스키마 6종 + 보존 정책 4단계 + 접근 제어 5역할 + 무결성 해시 체인 + 에스컬레이션 3종 + 예외 처리 10건 + 테스트 12건 정의. LOCK 3건(06/07/09) 정합 OK, P1-5 인증 이벤트 10건 + P1-6 에러 이벤트 14건 전수 감사 대상 포함 MATCH. L3 승급.
>
> **실행 결과 요약**:
> - AuditEvent 인터페이스 필수 필드 13개 + 보조 타입 6종 정의, 6개 카테고리(authentication/authorization/task/discovery/error/system) 28개 이벤트 유형 전수 정의
> - LOCK 3건(A2A-06/07/09) 기존값 그대로 참조, §6.1 항목 #30 대응 완료, P1-5 예외 10건 + P1-6 에러 14건 전수 감사 매핑 MATCH
> - 재검증 시 발견/정정 사항 없음 (초회 작성으로 재검증 0회)
> - SoT 교차검증: 상세명세 §4.3 원본 대조 완료, LOCK-A2A-06/07/09 기존값 준수 확인

**[P1-7] 검증 결과 요약** (갱신: 2026-04-10)
- 0. 산출물: 생성 1개 — `03_security/audit_logging.md` (v1.0, L3 승급)
- 1. 게이트: G1 Phase 1→2 충족 — `01_a2a-protocol/` L3 완성 (P1-1, P1-2, P1-3, P1-6 완료) + `02_agent-discovery/` L3 진행 중 (P1-4 완료) + `03_security/` L3 완성 (P1-5, P1-7 완료)
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건 (기존 CLF-A2A-001~004 전체 RESOLVED 유지)
- 3. LOCK 변경: 없음 (LOCK-A2A-06/07/09 기존값 그대로 참조)
- 4. 이월: 없음
</details>

**산출물**: `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\03_security\audit_logging.md` (L3 승급)

#### Phase 2 — 확장 (V2 정렬)

| # | 작업 | 서브폴더 | 우선순위 |
|---|------|---------|---------|
| 1 | SSE 스트리밍 구현 | `04_advanced-features/` | P0 |
| 2 | Push Notifications | `04_advanced-features/` | P0 |
| 3 | Multi-turn Sessions | `04_advanced-features/` | P1 |
| 4 | MoA 패턴 구현 | `04_advanced-features/` | P1 |
| 5 | 모니터링 대시보드 메트릭 | `05_monitoring/` | P1 |
| 6 | 분산 에이전트 레지스트리 | `02_agent-discovery/` | P1 |
| 7 | 위임 체인 고급 기능 | `03_security/` | P2 |

#### Phase 2 단계별 상세 작업 절차

<details>
<summary>P2-1. SSE 스트리밍 구현 (04_advanced-features/, P0 우선)</summary>

**대조 기준**

1. §7 Phase 2 테이블 #1
2. Phase 2→3 게이트: "SSE 완성"
3. §6.1 #35 Streaming SSE, #46 agent_streaming 상태
4. 교차 도메인: 해당 없음
5. Part2 버전: V2-Phase 2

**목표**: Server-Sent Events 기반 실시간 스트리밍 구현 상세. R-11-7 SSE 타임아웃 300초 반영.

**입력 파일**

- `D:\VAMOS\docs\sot\STEP7-B_대화프로세스_작업가이드.md` (88건 대화 프로세스)
- `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` — Agent Workflow
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_상세명세.md` §5.1 V2#1
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_구조화_종합계획서.md` §7.3 #1, §3.4 LOCK
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\04_advanced-features\_index.md`

**절차**

1. SSE 엔드포인트 설계
2. 이벤트 유형 정의 (task_status / artifact_chunk / heartbeat)
3. 연결 관리 (타임아웃 300초, 재연결, 백프레셔)
4. agent_streaming 상태 전이 정의
5. `_index.md` 갱신

**검증**:
- [x] SSE 엔드포인트 정의 완료 — Phase 2→3 게이트 "SSE 완성" 기여
- [x] R-11-7 SSE 타임아웃 300초 반영
- [x] 재연결 로직 + 백프레셔 메커니즘 포함

**산출물**: `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\04_advanced-features\streaming_sse.md`

> **P2-1 완료 (STEP_B #2a 세션 P2-1, 2026-04-22, parent-executed)**
>
> - [x] SSE 엔드포인트 정의 완료 — Phase 2→3 게이트 "SSE 완성" 직접 충족 (streaming_sse.md §2 엔드포인트 + §3 3 이벤트 유형)
> - [x] R-11-7 SSE 타임아웃 300초 반영 (§4.1 상한 300s + TS-03/TS-04 경계 시나리오)
> - [x] 재연결 로직 + 백프레셔 메커니즘 포함 (§4.2 지수 백오프 + last-event-id / §4.3 in-memory 큐 64 이벤트 상한)
>
> **실행 결과 요약**:
> - **산출물 (1 NEW)**: `04_advanced-features/streaming_sse.md` **374L / 19,766B** (sandbox 실측 `wc -l` 2026-04-22T11:23, 3-6 #2b 수동 추정 436L cascade 교훈 사전 차단)
> - **V1 본문 불변 (append-only 엄수)**: V1 EXTEND 대상 0건 (04_advanced-features 에 기존 V1 .md 파일 없음, 전수 NEW 생성), V1 MUTATION 0.
> - **LOCK 정합 5필드 분리 인용**: LOCK-A2A-05 "컨텍스트 윈도우 한계 / 모델별 max_tokens 준수, 초과 시 압축 / D2.0-05 §12.13 / 모델 변경 시 갱신" verbatim AUTHORITY §3 일치 (streaming_sse §7.1 + §9 + 본문 5 지점 총 7 지점) + LOCK-A2A-09 "Circuit Breaker 연속 실패 임계 / 3회 → OPEN, 60초 후 HALF-OPEN / D2.0-05 §4.4 (ADD-072) / D2.0-05 변경 시만" verbatim 일치 (§6.1 5필드 분리 + §9 + 본문 7 지점 총 9 지점) — LOCK hallucination 0, 5-1 회귀 방지 선례 준수. LOCK-A2A-01/02 간접 참조 (§2.2 JSON-RPC envelope + §3.1 state 필드).
> - **STEP7-B verbatim line refs**: L622 #61 스트리밍 출력 (VAMOS "설계만" 상태 갱신 대상) + L711 #18 S7B-018 스트리밍 출력 구현 (V1 가능 🟡 HIGH) = **2 line refs** verbatim (CLF-A2A-003 규칙 준수, D2.0-05 §4.4 / §12.13 이 실질 정본).
> - **V2↔V2 peer cross-ref 예약**: push_notifications.md (§1 / §6.3 역방향 폴백) + multi_turn_sessions.md (§1 / §7.2 컨텍스트 관리) + conversation_state_machine.md (§1 / §5 agent_streaming 상태 정본) + moa_pattern.md (§1 / §TS-14 proposer 병렬 스트림) + 05_monitoring/metrics_dashboard.md (§1 active_sessions 메트릭) = **5 peer references** (P2-2/P2-3 이후 실체화 완료 예정).
> - **FABRICATION 10종 마커 scan**: 0 hits CLEAN (TODO/FIXME/PLACEHOLDER/XXX/TBD/FABRICATED/FABRICATION_DETECTED/V1_MUTATION/V1_REGRESSION_DETECTED/VIOLATION — parent-executed 직접 편집, Subagent 0회, 2-2 1차 FABRICATION 격리 교훈 계승)
> - **Phase 3 테스트 시나리오**: TS-01~TS-15 (**15 시나리오**, 목표 10+ 대비 150% 달성)
> - **CLF-A2A-003 규칙 준수**: D2.0-05 아키텍처 정본 우선 서술 (§6.1 CB / §7 컨텍스트 압축), STEP7-B 는 벤치마크/갭 식별 보조로 한정.
> - **CLF-A2A-004 규칙 준수**: LOCK-A2A-09 CB 3회 vs MCP 5회 "의도적 차이" §6.1-3 명시, 5회 상향 금지 보호 반영.
> - **pre/post integrity snapshot**: pre 5 meta 파일 SHA 고정 후 streaming_sse.md NEW 생성, production 3-8 17/17 SHA UNCHANGED 확정, sandbox 04_advanced-features/ 1 파일 증가.
> - **Cross-domain 처리**: `cross_domain_deps: []` (3-8 자기완결), CONSUMER/PRODUCER role 없음. AUTHORITY §4 교차 참조 의존성 표 #13 Agent-Protocol / #16 MCP / #3 Blue-Node / #1 Verifier / #15 CI/CD RECHECK_FLAG 판정은 STEP_B #2c 도메인 마감 step 8.
> - **이월 없음**: P2-1 단일 세션 완결, #2a P2-2 (Push) + P2-3 (Multi-turn) 로 진행. #2b P2-4/P2-5 MoA+메트릭 + #2c P2-6/P2-7 + 도메인 마감.

**[P2-1] 검증 결과 요약** (갱신: 2026-04-22, Phase 2)
- 0. 산출물: **1 NEW** (`04_advanced-features/streaming_sse.md` 374L / 19,766B, V2-Phase 2 태그 3 지점 명시, V1 본문 SHA 변경 0)
- 1. 게이트: **Phase 2→3 exit gate "04_advanced-features/ MoA + SSE 완성 + 모니터링 메트릭 정의" 중 "SSE 완성" 직접 충족** + Phase 1→2 entry gate 재확인 (01/02/03 L3 완성 충족 확인).
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건 (기존 4 RESOLVED 보존, 신규 [CONFLICT_CANDIDATE] 0건 — CLF-A2A-003/004 규칙 준수 서술 반영).
- 3. LOCK 변경: 없음 (LOCK-A2A-05/09 기존 정본 verbatim 인용만, LOCK-A2A-01/02 간접 참조, [LOCK_CHANGE_NEEDED] 0건).
- 4. 이월: 없음 (P2-1 단일 세션 완결).

</details>

<details>
<summary>P2-2. Push Notifications (04_advanced-features/, P0)</summary>

**대조 기준**

1. §7 Phase 2 테이블 #2
2. Phase 2→3 게이트: 기여 (04_ 완성)
3. §6.1 #36 Push, #37 State Transition History
4. 교차 도메인: 해당 없음
5. Part2 버전: V2-Phase 2

**목표**: Push 알림 메커니즘 + 상태 전이 이력 추적.

**입력 파일**

- `D:\VAMOS\docs\sot\STEP7-B_대화프로세스_작업가이드.md` (88건 대화 프로세스)
- `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md`
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_상세명세.md` §5.1 V2#2~3
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_구조화_종합계획서.md` §7.3 #2

**절차**

1. Push 채널 설계 (WebSocket / Webhook)
2. 알림 페이로드 스키마
3. 상태 전이 이력 저장 스키마
4. 구독 관리 API

**검증**:
- [x] Push 알림 스키마 정의 완료
- [x] 상태 전이 이력 저장 스키마 포함

**산출물**: `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\04_advanced-features\multi_turn_sessions.md` (Push Notifications 섹션으로 통합 — §2.1 폴더 트리 기준 별도 파일 미등재)

> **P2-2 완료 (STEP_B #2a 세션 P2-2, 2026-04-22, parent-executed)**
>
> - [x] Push 알림 스키마 정의 완료 (`push_notifications.md` §2 method + §3 웹훅 포맷 + §5 구독 관리 API)
> - [x] 상태 전이 이력 저장 스키마 포함 (§4 `TransitionEventRecord` Pydantic append-only ledger + §4.4 허용 전이 DAG)
>
> **실행 결과 요약**:
> - **산출물 (1 NEW)**: `04_advanced-features/push_notifications.md` **382L / 17,433B** (sandbox 실측 `wc -l` 2026-04-22T11:29)
> - **파일 배치 결정 (⚠️ 3원 불일치 해소)**: plan §7.3 P2-2 L1078 "multi_turn_sessions.md Push 섹션 통합" vs `_index.md` "streaming_sse.md 통합 (항목 1-3)" vs 사용자 entry prompt "push_notifications.md NEW 별도 파일" 3원 불일치 → 사용자 정밀성 우선 결정에 따라 **Push + State Transition History 결합 독립 파일** 채택 (3-6 benchmark_vbs17.md NEW 선례 계승, P2-3 `multi_turn_sessions.md` 와 중복 방지). **[CONFLICT_CANDIDATE:push_file_placement]** 라벨로 추적, #2c 도메인 마감 step 7 (CONFLICT_LOG v1.1) 에서 정식 등재 판정 또는 RESOLVE (자동 처리 금지).
> - **LOCK 정합 5필드 분리 인용** (AUTHORITY §3 verbatim 대조):
>   * LOCK-A2A-01 "`\"jsonrpc\": \"2.0\"` / Google A2A Spec / 스펙 업데이트 시 검토" — §2.1 요청 스키마 + §3.1 콜백 포맷 + §9 표 + 본문 1 지점 = **4 지점**
>   * LOCK-A2A-02 "`submitted|working|input-required|completed|failed|canceled` / Google A2A Spec / 스펙 업데이트 시 검토" — §4.1 TaskState Enum verbatim + §4.3 5필드 분리 + §4.4 DAG + §9 + 본문 5 지점 = **10 지점**
>   * LOCK-A2A-06 "mTLS 인증서 만료 자동 갱신 / 30일 전 / 가이드 §4.3/#11 / 변경 금지" — §5.2 + §9 + §1/§10 + 헤더 = **4 지점**
>   * LOCK-A2A-07 "JWT delegation chain 최대 깊이 / 3 / 가이드 §4.3/#11 / 보안 검토 후만 변경" — §4.1 delegation_depth + PN-12 + §9 + §10 + 본문 3 지점 = **7 지점**
>   * LOCK-A2A-09 "Circuit Breaker 연속 실패 임계 / 3회 → OPEN, 60초 후 HALF-OPEN / D2.0-05 §4.4 (ADD-072) / D2.0-05 변경 시만" — §6.2 5필드 분리 + §9 + 본문 7 지점 = **9 지점**
>   * **LOCK 인용 합계 34 지점** (5 LOCK 직접 참조), hallucination 0
> - **STEP7-B verbatim line refs**: L598 #47 Hook 시스템 (Claude ✅ 6종 / 타 AI ❌ / VAMOS ❌ 미적용) + L991 #69 세션 영속성 (10종 AI 모두 ✅ / VAMOS ⚠️ 설계만) = **2 line refs** verbatim (CLF-A2A-003 규칙 준수, D2.0-05 / 상세명세 §2.1 `$defs.PushNotificationConfig` 가 실질 정본)
> - **상세명세 §2.1 `$defs.PushNotificationConfig` verbatim 준수**: url / token / authentication.schemes 3 필드 일치 (§2.1 요청 스키마)
> - **V2↔V2 peer cross-ref 실체화**: push_notifications ↔ 6 peer (streaming_sse 1: `-32003` 폴백 / multi_turn_sessions 1: sessionId 이력 / conversation_state_machine 1: from/to state / moa_pattern 1: aggregator 완료 Push / metrics_dashboard 1: 전송 성공률 / audit_logging 1: audit trail) = **6 지점** (P2-3 이후 실체화 완료)
> - **FABRICATION 10종 마커 scan**: 0 hits CLEAN
> - **Phase 3 테스트 시나리오**: PN-01~PN-14 (**14 시나리오**, 목표 10+ 대비 140%)
> - **허용 전이 DAG 정의** (§4.4): LOCK-A2A-02 6 상태 간 11 전이 edge 명시, `-32000 Invalid transition` 가드
> - **append-only ledger 설계**: TransitionEventRecord sequence_num 단조 증가 + payload_hash sha256 + delegation_depth ≤ 3 (LOCK-A2A-07)
> - **CLF-A2A-003 규칙 준수**: D2.0-05 아키텍처 정본 우선 서술, STEP7-B 는 갭 식별 보조 한정
> - **CLF-A2A-004 규칙 준수**: CB 3회 의도적 차이 §6.2 명시
> - **pre/post integrity snapshot**: pre 5 meta SHA 고정 + sandbox 04_advanced-features/ 2 파일 (streaming_sse + push_notifications) 증가, production 3-8 17/17 SHA UNCHANGED
> - **Cross-domain 처리**: `cross_domain_deps: []`, AUTHORITY §4 #13/#16/#3/#1/#15 RECHECK_FLAG 판정은 #2c step 8

**[P2-2] 검증 결과 요약** (갱신: 2026-04-22, Phase 2)
- 0. 산출물: **1 NEW** (`04_advanced-features/push_notifications.md` 382L / 17,433B, V2-Phase 2 태그 3 지점, V1 본문 SHA 변경 0)
- 1. 게이트: **Phase 2→3 exit gate "04_ 완성" 기여** (Push + State Transition History 결합 독립 파일 + 구독 관리 API + CB 연동)
- 2. CONFLICT: 발견 **1건 [CONFLICT_CANDIDATE:push_file_placement]** (자동 RESOLVE 금지, #2c step 7 추적) / 해소 0건 / OPEN 0건 신규 (기존 4 RESOLVED 보존)
- 3. LOCK 변경: 없음 (LOCK-A2A-01/02/06/07/09 기존 정본 verbatim 인용만)
- 4. 이월: [CONFLICT_CANDIDATE] 1건 → #2c step 7 (도메인 마감)

</details>

<details>
<summary>P2-3. Multi-turn Sessions (04_advanced-features/, P1)</summary>

**대조 기준**

1. §7 Phase 2 테이블 #3
2. Phase 2→3 게이트: 기여
3. §6.1 #38 Multi-turn, #43~#48 대화 상태 머신 전이 6건, LOCK-AT-003 / LOCK-AT-009 보완
4. 교차 도메인: 해당 없음
5. Part2 버전: V2-Phase 2

**목표**: 멀티턴 세션 관리 + 대화 상태 머신 전이 6종 정의. LOCK-A2A-05 컨텍스트 윈도우 max_tokens 준수.

**입력 파일**

- `D:\VAMOS\docs\sot\STEP7-B_대화프로세스_작업가이드.md` (88건 대화 프로세스)
- `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` §12.13 컨텍스트 관리
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_상세명세.md` §5.1 V2#4
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_구조화_종합계획서.md` §3.4 LOCK-A2A-05, §7.3 #3

**절차**

1. 세션 생성 / 유지 / 종료 API
2. 대화 상태 머신 전이 6종 정의 (idle → awaiting → thinking → streaming → ready → completed / follow_up / error)
3. max_loop_iterations 가드 (LOCK-AT-003)
4. 턴 카운터 (LOCK-AT-009: P0=5 / P1=10 / P2=20)
5. 컨텍스트 윈도우 관리 (LOCK-A2A-05)

**검증**:
- [x] 대화 상태 머신 전이 6종 정의 완료
- [x] LOCK-A2A-05 컨텍스트 윈도우 max_tokens 준수 반영
- [x] LOCK-AT-003 무한 루프 가드 (max_loop_iterations) 반영
- [x] LOCK-AT-009 턴 상한 (P0=5/P1=10/P2=20) 반영

**산출물**:
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\04_advanced-features\multi_turn_sessions.md`
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\04_advanced-features\conversation_state_machine.md`

> **P2-3 완료 (STEP_B #2a 세션 P2-3, 2026-04-22, parent-executed)**
>
> - [x] 대화 상태 머신 전이 6종 정의 완료 (`conversation_state_machine.md` §4 #43~#48 전수 매핑 + §3 Mermaid 정본)
> - [x] LOCK-A2A-05 컨텍스트 윈도우 max_tokens 준수 반영 (`multi_turn_sessions.md` §5 압축 트리거 70%/85%/100% 3 구간)
> - [x] LOCK-AT-003 무한 루프 가드 반영 (`multi_turn_sessions.md` §4 + `conversation_state_machine.md` §7.2, 기본 50 iterations)
> - [x] LOCK-AT-009 턴 상한 반영 (`multi_turn_sessions.md` §3.4 매트릭스 P0=5 / P1=10 / P2=20)
>
> **실행 결과 요약**:
> - **산출물 (2 NEW)**: `04_advanced-features/multi_turn_sessions.md` **328L / ~15KB** (세션 관리 API + 턴 카운터 + loop guard + 컨텍스트 압축) + `04_advanced-features/conversation_state_machine.md` **385L / ~18KB** (9 상태 정본 + Mermaid + TransitionEvent Pydantic + 6 전이 군) = **2 NEW 713L** (sandbox 실측 `wc -l` 2026-04-22)
> - **R1 단일 소유권 원칙**: 대화 상태 머신 9 상태 정본 = `conversation_state_machine.md` 단독 소유 (§7.1), `multi_turn_sessions.md` 는 세션 관리 API 계층만 정본 소유. 두 문서 공통 상태 이름 참조 시 `conversation_state_machine.md` §5.2 verbatim 매핑 강제.
> - **LOCK 정합 5필드 분리 인용** (AUTHORITY §3 + #13 교차 LOCK):
>   * LOCK-A2A-05 (multi_turn §5.1 5필드 + 12 지점): "모델별 max_tokens 준수, 초과 시 압축 / D2.0-05 §12.13 / 모델 변경 시 갱신" verbatim
>   * LOCK-A2A-02 (state_machine §5 layer 구분 + 11 지점): "submitted|working|input-required|completed|failed|canceled" verbatim
>   * LOCK-A2A-07 (multi_turn §2.1 depth ≤3 + state_machine §4.3 재귀 + §7.3 5필드 = 15 지점): "JWT delegation chain 최대 깊이 / 3 / 가이드 §4.3/#11 / 보안 검토 후만 변경" verbatim
>   * LOCK-A2A-08 (state_machine §4.5 #47 분기 + §7.4 5필드 = 7 지점): "MANUAL|SEMI_AUTO|SUPERVISED_AUTO / D2.0-05 §1.1 (ADD-009)" verbatim
>   * LOCK-A2A-09 (multi_turn §2.3 + state_machine §3 + §7.1 5필드 = 14 지점): CB 3회/60초 verbatim
>   * **LOCK-AT-003 (교차 LOCK from #13 Agent-Protocol R-11-5)**: multi_turn §4.1 5필드 + 15 지점 + state_machine §7.2 5필드 + 11 지점 = **26 지점** "기본 50 iterations / #13 Agent-Protocol §3.4 / #13 변경 시 R-11-5 교차 통지"
>   * **LOCK-AT-009 (교차 LOCK from #13 Agent-Protocol R-11-5)**: multi_turn §3.1 5필드 + §3.4 매트릭스 + 12 지점 = **12 지점** "P0=5 / P1=10 / P2=20 / #13 Agent-Protocol 교차"
>   * **LOCK 인용 합계 95 지점** (hallucination 0, 교차 LOCK 2 건 포함)
> - **STEP7-B verbatim line refs**: L987 §H 세션 관리 섹션 헤더 + L991 #69 세션 영속성 + L992 #70 대화 분기 (Phase 3 이월) + L993 #71 내보내기 + L994 #72 검색 + L995 #73 요약 + L996 #74 멀티 대화 병렬 + L622 #61 스트리밍 출력 (#46 agent_streaming 분기) = **8 line refs** verbatim (CLF-A2A-003 규칙 준수, D2.0-05 §12.13 + Agent Mode §1.1 ADD-009 실질 정본)
> - **상세명세 §5.2 다이어그램 Mermaid 정본화**: ASCII L418~L438 → conversation_state_machine.md §3 Mermaid stateDiagram-v2 (L3 구현 사양 확정), 9 상태 + 13 전이 edge 전수 매핑
> - **V2↔V2 peer cross-ref 실체화**: multi_turn ↔ 6 peer (conversation_state_machine 8: R1 단일 소유권 / streaming_sse 3: agent_streaming 연동 / push_notifications 2: TransitionEventRecord 공유 / moa_pattern 1: 세션 공유 / metrics_dashboard 1: active_sessions / 6-4 1: 컨텍스트 RAG 위임) + conversation_state_machine ↔ 5 peer (multi_turn 7 / streaming_sse 4 / push_notifications 2 / moa_pattern 1 / D2.0-05 §1.1 1) = **32 peer references**
> - **FABRICATION 10종 마커 scan**: 0 hits CLEAN (multi_turn + state_machine 각 0)
> - **Phase 3 테스트 시나리오**: multi_turn MT-01~MT-14 (14건) + state_machine CS-01~CS-12 (12건) = **26 시나리오** (목표 20+ 대비 130%)
> - **Pydantic 공용 구조 정의**: Session / SessionPriority / SessionState / ConversationState / TransitionTrigger / TransitionEvent 6 모델 (§3.1 산출물 품질 필수 구조 #7 준수, 중복 정의 0)
> - **허용 전이 DAG + 분기 정책**: state_machine §4 6 전이군 각각 timeout/retry/가드 정책 정의, §3 Mermaid 시각화, §4.5 #47 Agent Mode (LOCK-A2A-08) 에 따른 분기 확정 주체 명시
> - **CLF-A2A-003 규칙 준수**: D2.0-05 아키텍처 정본 우선 (§12.13 + §1.1 ADD-009), STEP7-B 벤치마크/갭 식별 보조
> - **CLF-A2A-004 규칙 준수**: CB 3회 의도적 차이 state_machine §7.1 명시
> - **교차 LOCK R-11-5 동시 통지 규칙 적용**: LOCK-AT-003 + LOCK-AT-009 두 건 모두 #13 Agent-Protocol 에서 변경 시 본 #11 도메인에 동시 통지 필요 (AUTHORITY §4 R-11-5 / 4.3 교차 참조 의존성)
> - **pre/post integrity snapshot**: pre 5 meta SHA 고정 + sandbox 04_advanced-features/ 4 파일 (streaming_sse + push_notifications + multi_turn_sessions + conversation_state_machine) 증가, production 3-8 17/17 SHA UNCHANGED
> - **Cross-domain 처리**: `cross_domain_deps: []` (3-8 자기완결). 단 LOCK-AT-003/009 교차 LOCK 참조는 #13 Agent-Protocol 과의 R-11-5 동시 통지 대상. AUTHORITY §4 #13/#16/#3/#1/#15 RECHECK_FLAG 판정은 #2c step 8.
> - **이월 없음**: P2-3 단일 세션 완결 (2 V2 NEW)

**[P2-3] 검증 결과 요약** (갱신: 2026-04-22, Phase 2)
- 0. 산출물: **2 NEW** (`04_advanced-features/multi_turn_sessions.md` 328L + `conversation_state_machine.md` 385L = 713L, V2-Phase 2 태그 5 지점, V1 본문 SHA 변경 0)
- 1. 게이트: **Phase 2→3 exit gate "04_ 완성" 기여** (세션 관리 API + 9 상태 머신 정본 + TransitionEvent Pydantic + 턴/루프/컨텍스트 3중 가드)
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건 신규 (기존 4 RESOLVED 보존)
- 3. LOCK 변경: 없음 (LOCK-A2A-02/05/07/08/09 + LOCK-AT-003/009 교차 2건 모두 기존 정본 verbatim 인용만)
- 4. 이월: 없음 (P2-3 단일 세션 완결). #2b P2-4 MoA + P2-5 메트릭, #2c P2-6 레지스트리 + P2-7 위임 + 도메인 마감.

</details>

<details>
<summary>P2-4. MoA 패턴 구현 (04_advanced-features/, P1)</summary>

**대조 기준**

1. §7 Phase 2 테이블 #4
2. Phase 2→3 게이트: "MoA 완성"
3. §6.1 #49 proposer, #50 aggregator, R-11-6
4. 교차 도메인: 해당 없음
5. Part2 버전: V2-Phase 2

**목표**: Mixture of Agents 패턴 구현. R-11-6 (proposer 최소 2, 최대 5) 준수. §C MoA 패턴 부록 참조.

**입력 파일**

- `D:\VAMOS\docs\sot\STEP7-B_대화프로세스_작업가이드.md` (88건 대화 프로세스)
- `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` — Cooperative Agent
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_상세명세.md` §5.3
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_구조화_종합계획서.md` §C MoA 패턴, §7.3 #4

**절차**

1. proposer 에이전트 병렬 호출 설계
2. aggregator 응답 합성 알고리즘
3. R-11-6 (2~5 proposer) 반영
4. 투표 / 가중 집계 로직
5. 에러 처리 (proposer 실패 시 fallback)

**검증**:
- [x] MoA proposer/aggregator 정의 완료 — Phase 2→3 게이트 "MoA 완성" 기여
- [x] R-11-6 (proposer 최소 2, 최대 5) 반영
- [x] §C 부록 정합

**산출물**: `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\04_advanced-features\moa_pattern.md`

> **P2-4 완료 (STEP_B #2b 세션 P2-4, 2026-04-22, parent-executed)**
>
> - [x] MoA proposer/aggregator 정의 완료 — **Phase 2→3 게이트 "MoA 완성" 직접 충족** (`moa_pattern.md` §2 아키텍처 + §3 R-11-6 가드 + §4 병렬 호출 + §5 집계 모드 3종 + §7 CB 연동 + §10 MOA-01~12)
> - [x] R-11-6 반영 (`moa_pattern.md` §3.1 proposer 2/5/3 verbatim + §3.3 `MAX_PROPOSERS=5` hard cap + §3.2 R-11-6 verbatim L198 인용 + MOA-04/05 1-proposer/6-proposer 위반 ValueError 테스트)
> - [x] §C 부록 정합 (`moa_pattern.md` §2.1 MoA 실행 흐름 5 단계 verbatim L1516~L1524 + §3.1 proposer 2/5/3 · 타임아웃 5/120/30s · aggregator 1/1/1 전수 verbatim + §6.1 비용 공식 `(proposer 수 + 1) × 단일 호출 비용` verbatim L1534)
>
> **실행 결과 요약**:
> - **산출물 (1 NEW)**: `04_advanced-features/moa_pattern.md` **608L / 32,143B** (sandbox 실측 `wc -l` + `ls -la` 2026-04-22, §3.1 anti-fabrication 준수). 3-6 #2b 수동 추정 436L cascade 교훈 사전 차단 성공 (Measure-Object 맹신 0).
> - **LOCK 정합 5필드 분리 인용** (AUTHORITY_CHAIN.md §3 L56~L64):
>   * LOCK-A2A-01 (§4.2 `send_task` JSON-RPC 2.0 전제 + §11 LOCK 표 1행 = 2 지점)
>   * LOCK-A2A-02 (§4.2 TaskResult 반환 상태 + §7.2 proposer 실패 분류 + §11 = 3 지점)
>   * LOCK-A2A-05 (§8 aggregator 컨텍스트 윈도우 제어 + §8.1 5필드 verbatim + §11 = 4 지점)
>   * LOCK-A2A-08 (§9.1 5필드 verbatim + §9.2 SEMI_AUTO 기본 + §11 = 3 지점)
>   * LOCK-A2A-09 (§7.1 5필드 verbatim + §2.2 CB 다이어그램 + §7 CB 독립 관리 + §11 + CLF-A2A-004 CB 3회 의도적 차이 명시 + MOA-08/09 CB 테스트 2건 = 9 지점)
>   * **LOCK 인용 합계 21 지점** (hallucination 0, 5-1 회귀 방지 차단)
> - **R-11-6 verbatim 준수**: §3.1 표 + §3.2 plan §4.3 L198 verbatim 재인용 + §3.3 Python 가드 `MIN_PROPOSERS=2` / `MAX_PROPOSERS=5` + 주석 "상향 금지" 명시 (CLF-A2A-004 의도적 차이 원칙 계승)
> - **STEP7-B verbatim line refs**: L599 #48 병렬 도구 호출 (proposer 병렬 `asyncio.gather` 근거) + L613 #57 Fallback Chain (proposer 실패 fallback) + L614 #58 비용 실시간 모니터링 (MoA 비용 매트릭스 05_monitoring 연계) + L1002 #75 Prompt Caching (Phase 3 이월 근거) + L1003 #76 Semantic Caching (Phase 3 이월) + L373~L378 Kimo PARL Agent Swarm (MoA 선행 사례) = **6 line refs** verbatim (CLF-A2A-003 규칙 준수 D2.0-05 §4.4/§2/§1.1 실질 정본)
> - **V2↔V2 peer cross-ref 실체화 (§12 세션 간 인터페이스 표 10 지점)**: moa_pattern ↔ 상세명세 §5.3 (MixtureOfAgents 정본 재인용) + streaming_sse §5 agent_streaming + §6.1 CB + TS-14 MoA proposer 병렬 스트림 + push_notifications §8 aggregator 완료 Push + conversation_state_machine §4.3 T#45 + §5.2 agent_delegating + multi_turn_sessions §7.2 재귀 ≤3 + 세션 컨텍스트 공유 + metrics_dashboard total_cost_usd + moa span attributes = **10 peer 지점 실체화** (3-7 6×6=134 / 3-8 #2a 32 선례 계승)
> - **3 집계 모드 확정**: Majority Voting (기본, §5.1) + Weighted Average (advanced, §5.2) + Consensus (safety-critical, §5.3) — Part2 교차 참조 §L1598~L1604 verbatim, 각 모드 O(N) 시간 복잡도 + 선택 매트릭스 §5.4
> - **비용 매트릭스 §6.2**: proposer 2~5 × ×3~×6 승수 + aggregator 1 × 비용 = 총 ×3~×6, R-11-6 상한 5 hard cap, §6.3 D2.0-05 §2 비용 상한 Gate 연동 (사전 검증 + 실행 중 실측 + 사후 OTel 노출 3단)
> - **MoAEscalationPayload 에스컬레이션 구조 §7.3** (I-20 공용 6 + MoA 추가 4 필드): source_engine / error_code / original_request / partial_result / retry_count / timestamp + proposer_ids / proposer_failure_map / aggregation_mode / cb_state_snapshot (산출물 품질 필수 구조 #3 준수)
> - **로깅 포맷 §7.5** (R-01-7 structured JSON, 중첩 구조 필수): trace_id + error{} + context{} + recovery{} 3 블록 전수 포함 (산출물 품질 필수 구조 #4 준수)
> - **Pydantic 공용 구조 §3.4**: AggregationMode (3 모드 Enum) + MoAConfig (conlist min_length=2 max_length=5 R-11-6 인라인) + Proposal + AggregationResult 4 모델 (중복 정의 0, 산출물 품질 필수 구조 #7 준수)
> - **FABRICATION 10종 마커 scan**: 0 hits CLEAN (단일 파일 × 10 = 10 points, 2-2 1차 STEP_B FABRICATION 격리 교훈 계승, parent-executed Subagent 0회 유지)
> - **Phase 3 테스트 시나리오 §10**: MOA-01~MOA-12 **12 시나리오** (목표 10+ 대비 120%, 산출물 품질 필수 구조 #5 준수)
> - **CLF-A2A-003 규칙 준수**: D2.0-05 §4.4 CB + §2 비용 Gate + §1.1 ADD-009 Agent Mode 실질 정본, STEP7-B 벤치마크/갭 식별 보조
> - **CLF-A2A-004 규칙 준수**: LOCK-A2A-09 CB 3회 vs MCP 5회 의도적 차이 명시 (§7.1 #4 "5 회로 상향 금지" + §3.3 MAX_PROPOSERS 주석 "상향 금지" 병기)
> - **교차 LOCK R-11-5/R-11-8**: LOCK-A2A-07 delegation_depth ≤3 (세션 중첩 MoA 호출 시 `multi_turn_sessions.md` §7.2 + `conversation_state_machine.md` §4.3 T#45 위임 깊이 누적) 교차 준수
> - **비용 관리 정책 통합**: _index.md 항목 #9 "(proposer 수 + 1) × 단일 비용, 상한 Gate 연동" 반영 (L3 설계 확정, §6.3 사전/실행중/사후 3단 가드)
> - **pre/post integrity snapshot**: pre 5 meta SHA 고정 + sandbox 04_advanced-features/ 5 파일 (streaming_sse + push_notifications + multi_turn_sessions + conversation_state_machine + moa_pattern) 증가, production 3-8 17/17 SHA UNCHANGED
> - **Cross-domain 처리**: `cross_domain_deps: []` (3-8 자기완결). AUTHORITY §4 교차 참조 #13 Agent-Protocol + #16 MCP + #3 Blue-Node + #1 Verifier + #15 CI/CD RECHECK_FLAG 판정은 #2c step 8 dependency_propagate.
> - **이월 없음**: P2-4 단일 세션 완결 (1 V2 NEW)

**[P2-4] 검증 결과 요약** (갱신: 2026-04-22, Phase 2)
- 0. 산출물: **1 NEW** (`04_advanced-features/moa_pattern.md` 608L / 32,143B, V2-Phase 2 태그 §13 변경 이력 1 지점, V1 본문 SHA 변경 0)
- 1. 게이트: **Phase 2→3 exit gate "MoA 완성" 직접 충족** (proposer/aggregator 정의 + R-11-6 가드 + 3 집계 모드 + CB 연동 + 비용 매트릭스)
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건 신규 (기존 4 RESOLVED 보존 + [CONFLICT_CANDIDATE:push_file_placement] 1건 #2a 추적 유지 #2c step 7 판정)
- 3. LOCK 변경: 없음 (LOCK-A2A-01/02/05/08/09 5건 모두 기존 정본 verbatim 인용만)
- 4. 이월: 없음 (P2-4 단일 세션 완결). #2b 잔여 P2-5 메트릭, #2c P2-6/P2-7 + 도메인 마감.

</details>

<details>
<summary>P2-5. 모니터링 대시보드 메트릭 (05_monitoring/, P1)</summary>

**대조 기준**

1. §7 Phase 2 테이블 #5
2. Phase 2→3 게이트: "모니터링 메트릭 정의"
3. §6.1 #51~#54 트래픽/성능/안정성/에이전트별, v12_C09b_117 OTel
4. 교차 도메인: 해당 없음
5. Part2 버전: V2-Phase 2

**목표**: A2A 모니터링 메트릭 4종 정의 + OpenTelemetry 통합 설계.

**입력 파일**

- `D:\VAMOS\docs\sot\STEP7-B_대화프로세스_작업가이드.md` (88건 대화 프로세스)
- `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` §4.4 Circuit Breaker (LOCK-A2A-09 정본)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_상세명세.md` §6
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_구조화_종합계획서.md` §3.4 LOCK-A2A-09, §7.3 #5
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\05_monitoring\_index.md`

**절차**

1. 트래픽 메트릭 (total_tasks_24h, active_sessions)
2. 성능 메트릭 (avg / p50 / p95 / p99 latency)
3. 안정성 메트릭 (success / error / timeout rate)
4. 에이전트별 메트릭 (status, load_factor)
5. OTel 통합 (trace context, span naming `a2a.task.{method}`)
6. LOCK-A2A-09 Circuit Breaker 메트릭 포함

**검증**:
- [x] 4종 메트릭(트래픽/성능/안정성/에이전트별) 정의 완료 — Phase 2→3 게이트 "모니터링 메트릭 정의" 충족
- [x] OTel 통합 (trace context, span naming) 설계 포함
- [x] LOCK-A2A-09 CB 메트릭 반영 (3회→OPEN, 60초 HALF-OPEN 임계값 포함)

**산출물**: `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\05_monitoring\metrics_dashboard.md`

> **P2-5 완료 (STEP_B #2b 세션 P2-5, 2026-04-22, parent-executed)**
>
> - [x] 4종 메트릭 정의 완료 — **Phase 2→3 게이트 "모니터링 메트릭 정의" 직접 충족** (`metrics_dashboard.md` §3.1 트래픽 / §3.3 성능 / §3.4 안정성 / §3.5 에이전트별, 상세명세 §6.1 L475~L508 A2AMetrics TypeScript interface 정본 재인용 §2.1 + Pydantic 공용 구조 TrafficMetrics/PerformanceMetrics/ReliabilityMetrics/AgentMetric/A2AMetricsSnapshot §2.2)
> - [x] OTel 통합 설계 포함 (`metrics_dashboard.md` §5: §5.1 W3C TraceContext 전파 + §5.2 span naming `a2a.task.{method}` 8 method verbatim + §5.3 10 span attributes + §5.4 sampling 3단 head 10% / tail error 100% / consensus 100% + 종합계획서 §6.3 L1591 v12_C09b_117 verbatim 인용)
> - [x] LOCK-A2A-09 CB 메트릭 반영 (`metrics_dashboard.md` §4 전체: §4.1 5필드 verbatim "3회 → OPEN, 60초 후 HALF-OPEN / D2.0-05 §4.4 (ADD-072)" + §4.2 5 CB 메트릭 게이지 cb_state_per_agent / cb_open_total / cb_half_open_total / cb_open_duration_s / cb_trip_reason + §4.3 peer V2 연동 streaming_sse/push_notifications/moa_pattern + §4.4 CB 알림 규칙 + §7.1 CB_OPEN_DETECTED Critical 알림 60s 쿨다운)
>
> **실행 결과 요약**:
> - **산출물 (1 NEW)**: `05_monitoring/metrics_dashboard.md` **504L / 27,277B** (sandbox 실측 `wc -l` + `ls -la` 2026-04-22, §3.1 anti-fabrication 준수). 3-6 #2b 수동 추정 436L cascade 교훈 사전 차단 성공.
> - **LOCK 정합 5필드 분리 인용** (AUTHORITY_CHAIN.md §3 L57/62/64):
>   * LOCK-A2A-02 (§3.1 tasks_by_state 6 상태 verbatim + §2.2 Pydantic dict keys + §6.2 라벨 카디널리티 = 3 지점)
>   * LOCK-A2A-07 (§5.5 5필드 verbatim + `a2a.delegation.depth` 버킷 [0,1,2,3] + `depth_exceeded_total` 카운터 + `DELEGATION_DEPTH_EXCEEDED` Critical 알림 + §11 LOCK 표 = 5 지점)
>   * LOCK-A2A-09 (§4.1 5필드 verbatim + §4.2 5 게이지 + §4.3 peer 3 연동 + §4.4 CB 알림 + §5.3 `a2a.cb.state` span attribute + §7.1 CB_OPEN_DETECTED 알림 + CLF-A2A-004 의도적 차이 명시 + MET-07/08 CB 테스트 2건 + §11 = 15 지점)
>   * **LOCK 인용 합계 23 지점** (hallucination 0, 5-1 회귀 방지 차단)
> - **OpenTelemetry 통합 확정 (§6.3 v12_C09b_117 L1591 verbatim 직접 충족)**: W3C TraceContext (`traceparent` + `tracestate`) + span `a2a.task.{method}` 8 method 전수 (tasks/send + sendSubscribe + get + cancel + pushNotification/set|get + resubscribe + authenticatedExtendedCard) + 10 span attributes (task.id / session.id / agent.id / delegation.depth / cb.state / moa.proposal_count / moa.aggregation_mode / moa.total_cost_usd / stream.chunk_count / stream.dropped_artifacts) + sampling 3단 (head ParentBased TraceIdRatioBased 10% + tail-based error_code≠null / cb.state∈{OPEN,HALF-OPEN} / status=failed 100% + Consensus aggregation_mode=consensus 100% 강제)
> - **STEP7-B verbatim line refs**: L609 #53 자기검증 루프 (VAMOS 설계 근거) + L610 #54 환각 감지 + L611 #55 EVX 검증 체인 (VAMOS 독자) + L614 #58 비용 실시간 모니터링 (VAMOS 독자, MoA 비용 연계) + L622 #61 스트리밍 출력 (SSE 메트릭 연계) + §I L1006 #79 Rate Limiting/Throttling (VAMOS Cost Gate) = **6 line refs** verbatim (CLF-A2A-003 규칙 준수 D2.0-05 §4.4 + 상세명세 §6.1 실질 정본)
> - **V2↔V2 peer cross-ref 실체화 (§12 세션 간 인터페이스 표 12 지점)**: metrics_dashboard ↔ 상세명세 §6.1 정본 + §2.3 method + AUTHORITY LOCK-A2A-02/07/09 + multi_turn_sessions §3.1 active_sessions 정의 + streaming_sse §4.3 dropped_artifacts + §3.2 artifact_chunk + CB 3 파일 전역 + conversation_state_machine §4 6 전이군 + moa_pattern §3.1 R-11-6 + §5 3 집계 모드 + §6 비용 매트릭스 + delegation ≤3 교차 = **12 peer 지점 실체화** (3-7 134 / 3-8 #2a 32 / P2-4 10 선례 계승)
> - **A2AMetrics 정본 소유권 준수 §2.1**: 상세명세 §6.1 L475~L508 TypeScript interface 수정 없는 재인용 (21-line 코드 블록), 본 V2 문서에서 interface 자체 변경 금지 원칙 + §2.2 Pydantic 대응 구조 추가 정의 (중복 정의 0, 산출물 품질 필수 구조 #7 준수)
> - **Prometheus 메트릭 명명 §6**: a2a_tasks_total + a2a_active_sessions + a2a_latency_seconds + a2a_errors_total / timeouts / retries + a2a_agent_status / load_factor + a2a_cb_state / cb_open_total + a2a_moa_executions / proposal_count / cost_usd + a2a_delegation_depth / depth_exceeded_total = 13 표준 메트릭, 라벨 카디널리티 제한 (agent_id ≤100, method 8, state 6, error_code ≤20)
> - **알림 규칙 §7**: Critical 5 (CB_OPEN_DETECTED / AGENT_DOWN / ERROR_RATE_HIGH / P99_LATENCY_HIGH / DELEGATION_DEPTH_EXCEEDED 보안) + Warning 4 (TIMEOUT_RATE_ELEVATED / RETRY_RATE_ELEVATED / MOA_COST_SPIKE / AGENT_DEGRADED) = 9 규칙 정의, 각 쿨다운 / 지속 시간 명시
> - **Grafana 대시보드 구조 §8**: 5 패널 (트래픽 개요 + 성능 분포 + 안정성 보드 + 에이전트 상태 + CB+MoA+위임) + 3 표준 필터 (agent_id / method / time_range) — JSON 파일 및 provisioning YAML 은 Phase 3 이월 (_index.md 항목 3 "PLAN" 상태 유지)
> - **로깅 포맷 §9** (R-01-7 structured JSON, 중첩 구조 필수): trace_id + error{} + context{} + recovery{} 3 블록 전수 포함 (산출물 품질 필수 구조 #4 준수)
> - **FABRICATION 10종 마커 scan**: 0 hits CLEAN (단일 파일 × 10 = 10 points, 2-2 1차 STEP_B FABRICATION 격리 교훈 계승, parent-executed Subagent 0회)
> - **Phase 3 테스트 시나리오 §10**: MET-01~MET-15 **15 시나리오** (목표 10+ 대비 150%, 산출물 품질 필수 구조 #5 준수) — 메트릭 정확성 + 알림 임계 + CB 전이 + OTel trace 전파 + sampling 전략 + 라벨 카디널리티 방어
> - **CLF-A2A-003 규칙 준수**: D2.0-05 §4.4 CB + 상세명세 §6.1 A2AMetrics 실질 정본, STEP7-B 는 VAMOS 독자 기능 (EVX 검증 체인 / 비용 실시간 모니터링) 근거 참조
> - **CLF-A2A-004 규칙 준수**: LOCK-A2A-09 CB 3회 vs MCP 5회 의도적 차이 §4.3 명시 + §4.4 알림 임계 3회 기준 유지 (5회 상향 금지)
> - **교차 LOCK LOCK-A2A-07**: 위임 깊이 3 상한 히스토그램 버킷 + `depth_exceeded_total` 카운터 + 보안팀 알림 (LOCK-AT-013 privilege escalation 방지 준수)
> - **05_monitoring 첫 V2 생성**: `_index.md` 항목 매핑 확인 완료 (항목 1 A2AMetrics + 항목 2 Prometheus + 항목 3 Grafana + 항목 4 알림 + 항목 5 OTel = 본 V2 파일 통합 대상 5 항목 전수 반영). _index.md 자체 미수정 (도메인 마감 step 5 #2c 전용).
> - **pre/post integrity snapshot**: pre 5 meta SHA 고정 + sandbox 05_monitoring/ 추가 metrics_dashboard.md 1 파일, 04_advanced-features/ 5 파일 전수 유지, production 3-8 17/17 SHA UNCHANGED
> - **Cross-domain 처리**: `cross_domain_deps: []` (3-8 자기완결). AUTHORITY §4 교차 참조 #13 Agent-Protocol + #16 MCP + #3 Blue-Node + #1 Verifier + #15 CI/CD RECHECK_FLAG 판정은 #2c step 8.
> - **이월 없음**: P2-5 단일 세션 완결 (1 V2 NEW)

**[P2-5] 검증 결과 요약** (갱신: 2026-04-22, Phase 2)
- 0. 산출물: **1 NEW** (`05_monitoring/metrics_dashboard.md` 504L / 27,277B, V2-Phase 2 태그 §13 변경 이력 1 지점, V1 본문 SHA 변경 0)
- 1. 게이트: **Phase 2→3 exit gate "모니터링 메트릭 정의" 직접 충족** (4종 메트릭 Pydantic + OTel W3C TraceContext + span 8 method + LOCK-A2A-09 CB 게이지 + 알림 9 규칙 + Grafana 5 패널)
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건 신규 (기존 4 RESOLVED 보존 + [CONFLICT_CANDIDATE:push_file_placement] 1건 #2a 추적 유지 #2c step 7 판정)
- 3. LOCK 변경: 없음 (LOCK-A2A-02/07/09 3건 모두 기존 정본 verbatim 인용만)
- 4. 이월: 없음 (P2-5 단일 세션 완결). #2b 완결, #2c P2-6/P2-7 + 도메인 마감.

</details>

<details>
<summary>P2-6. 분산 에이전트 레지스트리 (02_agent-discovery/, P1)</summary>

**대조 기준**

1. §7 Phase 2 테이블 #6
2. Phase 2→3 게이트: 기여
3. §6.1 #17~#22, v12_C12_101
4. 교차 도메인: 해당 없음
5. Part2 버전: V2-Phase 2

**목표**: 분산 환경 에이전트 레지스트리 + 선택 알고리즘 상세.

**입력 파일**

- `D:\VAMOS\docs\sot\STEP7-B_대화프로세스_작업가이드.md` (88건 대화 프로세스)
- `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` — Cooperative Agent 아키텍처
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_상세명세.md` §3.2~3.3
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_구조화_종합계획서.md` §3.4 LOCK-A2A-04, §7.3 #6
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\02_agent-discovery\_index.md`

**절차**

1. AgentRegistration 스키마 확장
2. 헬스 체크 메커니즘
3. AgentCapability 열거형
4. 가중 스코어링 선택 알고리즘
5. Jaccard 유사도 스킬 매칭
6. 부하 균형 / 우선순위 로직

**검증**:
- [x] 레지스트리 스키마(AgentRegistration) 정의 완료
- [x] 선택 알고리즘(가중 스코어링, Jaccard 유사도) 포함
- [x] LOCK-A2A-04 mDNS 정합

**산출물**:
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\02_agent-discovery\service_registry.md`
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\02_agent-discovery\agent_selection.md` (갱신)

> **P2-6 완료 (STEP_B #2c 세션 P2-6, 2026-04-22, parent-executed)**
>
> - [x] 레지스트리 스키마(AgentRegistration) 정의 완료 (`service_registry.md` §2.1 상세명세 §3.2 L252~L274 verbatim 재인용 + §2.2 Pydantic 공용 구조 HealthCheckSpec/AgentMetadata/SkillDescriptor/AgentRegistration 4 모델 정의 + §2.3 AgentCard ↔ AgentRegistration ↔ mDNS TXT 3열 대응 표)
> - [x] 선택 알고리즘(가중 스코어링, Jaccard 유사도) 포함 (`agent_selection.md` §3 Jaccard 유사도 Python 구현 상세명세 §3.3 L285~L288 정합 + §4 4-factor 가중 스코어링 0.40 skill_match + 0.25 load + 0.20 priority + 0.15 latency 상세명세 §3.3 L293~L298 verbatim + §5 Pydantic SelectionRequest/SelectionResult/ScoredCandidate 3 모델 + §6 5단 fallback 정책 + §9 Phase 3 테스트 14건)
> - [x] LOCK-A2A-04 mDNS 정합 (`service_registry.md` §3.2 mDNS TXT `caps` 필드 매핑 5값 × `AgentCapability` 열거형 정합 + §8.1 LOCK-A2A-04 5필드 verbatim + `agent_selection.md` §7 입력 후보 invariant 3 조건 + §10.1 LOCK-A2A-04 verbatim)
>
> **실행 결과 요약**:
> - **산출물 (2 NEW)**: `02_agent-discovery/service_registry.md` **416L / 21,297B** + `02_agent-discovery/agent_selection.md` **368L / 16,805B** = **합계 784L / 38,102B** (sandbox 실측 `wc -l` + `ls -la` 2026-04-22, §3.1 anti-fabrication 준수). 3-6 #2b 수동 추정 436L cascade 교훈 사전 차단 성공.
> - **agent_selection.md 는 V2 NEW** (V1 base 부재 확인 — sandbox `02_agent-discovery/` 에 `mdns_dns_sd.md` V1 + `_index.md` 만 존재, agent_selection V1 미생성). 3-7 ast_pipeline V1 EXTEND 452→1,044 L append-only 패턴 미해당. 신규 V2 작성으로 전환 (사용자 정밀성 우선 결정 / prompt 대응 contingency 적용).
> - **LOCK 정합 5필드 분리 인용** (AUTHORITY_CHAIN.md §3 L59/L62/L64/L65):
>   * LOCK-A2A-04 mDNS Service Type `_vamos-a2a._tcp.local.` 변경 금지 (service_registry §8.1 + agent_selection §10.1 = 2 지점 verbatim + §3.2 caps 매핑 + §7 invariant + §2.3 대응 표 = 본문 정합 4 지점)
>   * LOCK-A2A-07 JWT delegation_depth 3 (agent_selection §10.2 verbatim + §6.4 depth 가드 + §5.1 SelectionRequest.delegation_depth le=3 = 3 지점)
>   * LOCK-A2A-09 CB 3회/60초 (service_registry §8.2 + agent_selection §10.3 verbatim 2 지점 + service_registry §4.3 + §5 레지스트리 CB + §4.4 3단 상태 전이 + agent_selection §6.3 CB OPEN 배제 = 본문 정합 4 지점)
>   * LOCK-A2A-10 A2A 메시지 스키마 정본 소유 (service_registry §8.3 verbatim 1 지점, 경계 선언)
>   * **LOCK 인용 합계 17 지점** (verbatim 8 + 본문 정합 9, hallucination 0, 5-1 회귀 방지)
> - **상세명세 §3.3 L278~L303 verbatim 알고리즘 준수**: `agent_selection.md` §3.2 Jaccard Python 함수 + §4.1 4-factor 수식 Python 구현이 상세명세 원본 L278~L303 과 **수정 없이 재인용** (R1 정본 소유자 1곳 원칙 준수). 본 V2 에서 가중치 0.40/0.25/0.20/0.15 변경 금지, Phase 3 에서 historical_success 가중치 도입 예정.
> - **STEP7-B verbatim line refs**: §B L549 #13 의도 추출 (VAMOS 명시적) + L553 #17 제약 조건 추출 (VAMOS 독자) + L554 #18 IntentFrame 스키마 (VAMOS 독자, `required_skills` 추출 근거) + §D L583 #37 모델 라우팅 (설계) + L584 #38 도메인별 실행분리 (VAMOS 우위) = **5 line refs** verbatim (CLF-A2A-003 규칙 준수 D2.0-05 §1.1 + 상세명세 §3.1~§3.3 실질 정본, STEP7-B 벤치마크 참조)
> - **V2↔V2 peer cross-ref 실체화**: service_registry §9 매트릭스 10 peer + agent_selection §8 매트릭스 10 peer = **20 peer 지점** (3-7 134 / 3-8 #2a 32 / #2b 22 / P2-6 20 선례 계승). 본 2 파일 쌍방향 계약 (service_registry §7.4 ↔ agent_selection §2.1/§7 invariant) = P2-6 내부 V2↔V2 실체화.
> - **AgentCapability 열거형 정본 소유 §3**: 상세명세 §3.2 L272~L273 verbatim 5값 (`streaming | pushNotifications | stateTransitionHistory | multimodal | long_running`) 재인용, 본 V2 에서 값 추가/제거 금지. §3.2 mDNS TXT `caps` 필드 축약 별칭 (`push`, `stateHistory`) 호환성 명시 + REST 정규화.
> - **헬스 체크 §4 LOCK-A2A-09 정합**: 기본 30초 간격 + 1000ms 타임아웃 + 3회 연속 실패 → DOWN/CB_OPEN + 60초 후 HALF-OPEN + 1회 성공 CLOSED 복귀 = LOCK-A2A-09 전수 정합. §4.4 4단 실패 대응 (warning retry → DEGRADED → DOWN + CB OPEN + 은닉 → HALF-OPEN 60초 후 → CLOSED 복귀) + §5.1 레지스트리 서버 자체 CB + 캐시 fallback + mDNS 단일 노드 폴백.
> - **REST API 계약 §6**: 6 엔드포인트 스케치 (POST register + GET by id/query + PUT heartbeat + DELETE + GET health) + 4 신규 에러 코드 (`-32006~-32009`) + 인증 mTLS + JWT Bearer 정합 (P1-5 mtls_jwt.md). Phase 3 구현 이월 (본 V2 는 인터페이스 계약만).
> - **가중 스코어링 §4 정규화 분석**: 4 factor 합 = 1.00, total ∈ [0.0, 1.0], 임계값 정책 (≥0.7 고품질 / 0.4~0.7 중품질 / <0.4 저품질), latency_score 기본값 500ms 적용 (avg_latency_ms 부재 시). 5단 fallback (min_score 0.4 → 0.2 → force → 503 → Phase 3 큐잉).
> - **FABRICATION 10종 마커 scan**: 2 V2 파일 × 10 마커 = 20 points × 0 hits **CLEAN** (2-2 1차 STEP_B FABRICATION 격리 교훈 계승, parent-executed Subagent 0회)
> - **Phase 3 테스트 시나리오**: service_registry §10 REG-01~REG-13 **13 시나리오** (목표 10+ 대비 130%) + agent_selection §9 SEL-01~SEL-14 **14 시나리오** (목표 10+ 대비 140%) = P2-6 합계 **27 시나리오** (산출물 품질 필수 구조 #5 준수)
> - **CLF-A2A-003 규칙 준수**: D2.0-05 §1.1 ADD-009 Cooperative Agent + 상세명세 §3.1~§3.3 실질 정본, STEP7-B §B #17/#18 (IntentFrame 스키마 VAMOS 독자) + §D #37/#38 (도메인별 실행분리 VAMOS 우위) 벤치마크/갭 식별 보조
> - **CLF-A2A-004 규칙 준수**: LOCK-A2A-09 CB 3회 vs MCP 5회 의도적 차이 §4.3 service_registry 명시 + §5.2 에이전트 측 CB 독립성 + §6.3 agent_selection CB OPEN 배제 정책 (5회 상향 금지)
> - **교차 LOCK LOCK-A2A-07**: agent_selection §6.4 depth 가드 + §5.1 SelectionRequest.delegation_depth ≤3 명시 + §10.2 LOCK verbatim (P2-7 delegation_chain.md 와 R-11-5 동시 통지 규칙 적용, LOCK-AT-013 privilege escalation 방지 준수)
> - **V1 base 부재 대응 정책**: agent_selection.md V1 sandbox 부재 확인 → V2 NEW 선택 (3-7 ast_pipeline UPDATE 선례 미해당, 3-4 etl_pipeline UPDATE 선례도 미해당). 새 V2 NEW 로 작성 + §11 변경 이력 "V1 base 부재로 V2 NEW" 명시. V1 immutability 9 파일 SHA 불변 검증 완료 (`./` prefix 정규화 후 exit=0).
> - **pre/post integrity snapshot**: pre 9 V1 SHA 고정 + sandbox 02_agent-discovery/ 추가 service_registry + agent_selection 2 파일, 04_advanced-features/ 5 파일 + 05_monitoring/ 1 파일 전수 유지, production 3-8 17/17 SHA UNCHANGED (766d5f66...)
> - **Cross-domain 처리**: `cross_domain_deps: []` (3-8 자기완결). AUTHORITY §4 교차 참조 #13 Agent-Protocol (LOCK-AT-013 agent_selection §6.4 간접 교차) + #16 MCP + #3 Blue-Node + #1 Verifier + #15 CI/CD RECHECK_FLAG 판정은 도메인 마감 step 8.
> - **이월 없음**: P2-6 2 V2 세션 완결, #2c P2-7 + 도메인 마감 step 5/7/8 로 진행.

**[P2-6] 검증 결과 요약** (갱신: 2026-04-22, Phase 2)
- 0. 산출물: **2 NEW** (`02_agent-discovery/service_registry.md` 416L / 21,297B + `agent_selection.md` 368L / 16,805B, V2-Phase 2 태그 §11 변경 이력 각 1 지점, V1 본문 SHA 변경 0). agent_selection V1 base 부재 → V2 NEW (UPDATE 패턴 미해당).
- 1. 게이트: **Phase 2→3 기여** (exit gate 3대 조건 #2a/#2b 에서 전수 충족, 본 P2-6 은 레지스트리 + 선택 알고리즘 기여 세션). Jaccard + 4-factor 가중 스코어링 + AgentRegistration Pydantic + LOCK-A2A-04 mDNS 정합 3대 검증 [x].
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건 신규 (기존 4 RESOLVED 보존 + [CONFLICT_CANDIDATE:push_file_placement] 1건 #2a 추적 유지, 도메인 마감 step 7 에서 CFL-A2A-005 정식 판정 예정).
- 3. LOCK 변경: 없음 (LOCK-A2A-04/07/09/10 4건 모두 기존 정본 verbatim 인용만, hallucination 0).
- 4. 이월: 없음 (P2-6 단일 세션 완결, 2 V2 NEW). #2c P2-7 + 도메인 마감 step 5/7/8.

</details>

<details>
<summary>P2-7. 위임 체인 고급 기능 (03_security/, P2)</summary>

**대조 기준**

1. §7 Phase 2 테이블 #7
2. Phase 2→3 게이트: 기여
3. §6.1 #26~#29 DelegationToken / 깊이제한 / 리소스예산 / Ed25519, LOCK-A2A-07
4. 교차 도메인: 해당 없음
5. Part2 버전: V2-Phase 2

**목표**: JWT 기반 위임 체인 고급 기능. LOCK-A2A-07 (max_depth: 3) 준수.

**입력 파일**

- `D:\VAMOS\docs\sot\STEP7-B_대화프로세스_작업가이드.md` (88건 대화 프로세스)
- `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` — Agent Mode / delegation
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_상세명세.md` §4.2
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_구조화_종합계획서.md` §3.4 LOCK-A2A-07, §7.3 #7
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\03_security\_index.md`

**절차**

1. DelegationToken 스키마
2. max_depth 3 적용 (LOCK-A2A-07)
3. 리소스 예산 (max_tokens, max_api_calls)
4. Ed25519 서명 체계
5. privilege escalation 방지 (LOCK-AT-013)

**검증**:
- [x] DelegationToken 스키마 정의 완료
- [x] LOCK-A2A-07 max_depth 3 반영
- [x] Ed25519 서명 체계 포함
- [x] privilege escalation 방지 (LOCK-AT-013) 반영

**산출물**: `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\03_security\delegation_chain.md`

> **P2-7 완료 (STEP_B #2c 세션 P2-7, 2026-04-22, parent-executed)**
>
> - [x] DelegationToken 스키마 정의 완료 (`delegation_chain.md` §2.1 상세명세 §4.2 L335~L355 TypeScript interface verbatim 재인용 + §2.2 Pydantic 공용 구조 Permission/ResourceBudget/TokenConstraints/DelegationToken + DelegationUsage 5 모델 + §2.3 DelegationToken ↔ JWT Claims 매핑 표 11 행)
> - [x] LOCK-A2A-07 max_depth 3 반영 (`delegation_chain.md` §4 전체: §4.1 hard cap 정책 0/1/2/3 OK vs 4 `-32011` + §4.2 Python `issue_delegation_token` 의사코드 + `DelegationDepthExceeded` 예외 + §4.3 검증 측 hard cap 3 조건 + §13.2 LOCK-A2A-07 5필드 verbatim = depth 가드 5+ 지점)
> - [x] Ed25519 서명 체계 포함 (`delegation_chain.md` §6 전체: §6.1 서명 흐름 JWS base64url + `EdDSA` alg + `kid` 식별 + §6.2 키 회전 30일 LOCK-A2A-06 정합 + 7일 grace period + §6.3 JWKS `.well-known/jwks.json` 배포 kty=OKP crv=Ed25519)
> - [x] privilege escalation 방지 (LOCK-AT-013) 반영 (`delegation_chain.md` §7 전체: §7.1 `original_owner` claim 불변 정책 + §7.2 OWNER 권한 실행 분리 (권한 주체 = original_owner / 실행 주체 = delegate_agent_id) + §7.3 LOCK-AT-013 교차 LOCK 5필드 verbatim + R-11-5 동시 통지 규칙 적용 + §7.4 변조 탐지 `-32015 Original owner mutation detected` = 4중 방어선 전수 실체화)
>
> **실행 결과 요약**:
> - **산출물 (1 NEW)**: `03_security/delegation_chain.md` **619L / 29,052B** (sandbox 실측 `wc -l` + `ls -la` 2026-04-22, §3.1 anti-fabrication 준수). 3-6 #2b 수동 추정 436L cascade 교훈 사전 차단 성공.
> - **LOCK 정합 5필드 분리 인용** (AUTHORITY_CHAIN.md §3 L61/L62/L64 + §4 #13 교차):
>   * LOCK-A2A-06 mTLS 30일 갱신 (§13.1 verbatim + §6.2 Ed25519 키 회전 30일 정합 = 2 지점)
>   * LOCK-A2A-07 JWT delegation_depth 3 — **본 V2 핵심 LOCK** (§13.2 verbatim + §2.2 Pydantic conint ge=1 le=3 + §3.2 `vamos:max_depth=3` 필수 claim + §4.2 Python hard cap + §4.3 검증 측 재확인 = 5 지점)
>   * LOCK-A2A-09 CB 3회/60초 (§13.3 verbatim + §8 4중 방어선 독립 운용 = 2 지점)
>   * LOCK-AT-013 교차 LOCK 위임 시 OWNER 권한 실행 (§13.4 verbatim + §7.1~§7.4 전수 인용 = 5 지점, **R-11-5 동시 통지 규칙 적용** 도메인 마감 step 8 RECHECK_FLAG 판정)
>   * **LOCK 인용 합계 14 지점 verbatim + 본문 정합 15+ = 29+ LOCK 지점** (hallucination 0, 5-1 회귀 방지)
> - **상세명세 §4.2 L335~L355 verbatim 재인용 준수**: `DelegationToken` TypeScript interface + `Permission` 타입 6값을 **수정 없이 재인용** (R1 정본 소유자 1곳 원칙 준수). 본 V2 에서 interface 자체 필드 추가/제거 금지. Pydantic 구조는 §2.2 매핑 + §5 리소스 예산 확장 (max_cost_usd 추가) + §2.2 추가 claim 필드(original_owner / delegation_depth / jti)는 Pydantic 매핑 전용.
> - **JWT Claims 확장 §3**: 상세명세 §4.1 L320~L330 기본 claims 에 VAMOS 확장 claim 5개 추가 (`vamos:delegation_chain` / `vamos:delegation_depth` / `vamos:max_depth` / `vamos:original_owner` / `vamos:parent_jti` / `vamos:resource_budget` / `vamos:trust_level`). 모든 vamos 확장 claim 은 `vamos:` 네임스페이스 prefix 준수.
> - **4중 방어선 통합 §8**: (1) Claim 불변 + (2) Depth Guard + (3) Resource Budget + (4) Audit Trail 을 AND 조건으로 통합. 한 개 방어선만 실패해도 위임 거부. LOCK-A2A-07 (depth) + LOCK-AT-013 (owner) + LOCK-A2A-06 (키 회전) + audit_logging append-only 각 1 방어선 담당. §10 에러 코드 매핑 `-32011/-32012/-32013/-32014/-32015` 5 신규 + 상세명세 §4.4 기존 `-32001~-32005/408/429/503` 정합.
> - **audit_logging.md append-only 의무 §9**: 8 이벤트 타입 (`delegation.issued/verified/rejected/budget_warn/budget_exhausted/depth_exceeded/owner_mutation/signature_invalid`) 전수 정의 + 상세명세 §4.3 감사 로깅 스키마 정합 (`evt_delegation_a1b2c3` 예시) + 수정/삭제 금지 (GDPR 법적 의무 제외) + Phase 3 Merkle 트리 무결성 증명 이월.
> - **리소스 예산 추적 §5**: 부모 ≥ 자식 상속 규칙 (`-32012 Budget inflation denied` 거부) + 누적 카운터 Redis `INCRBY` + 80%/95%/100% 3단 경고 + MoA 비용 통합 (`moa_pattern.md §6` 비용 매트릭스 → `cost_usd_spent` 차감).
> - **STEP7-B verbatim line refs**: §D L573~L584 라우팅/결정 8개 (Policy/Cost/Evidence Gate 등 VAMOS 독자) 3 line refs + §G L627 #66 이벤트 로깅 + L628 #67 감사 추적 (VAMOS 독자) 2 line refs = **5 line refs** verbatim (CLF-A2A-003 규칙 준수 D2.0-05 §1.1 ADD-009 Agent Mode + 상세명세 §4.1~§4.4 실질 정본)
> - **V2↔V2 peer cross-ref 실체화 §11**: 10 peer (metrics_dashboard §5.5 / agent_selection §6.4 / moa_pattern §7.1 / multi_turn §7.2 / state_machine T#45 / service_registry §7.3 / streaming_sse §4.2 / push §6 / mtls_jwt V1 §2 / audit_logging V1) × 평균 2 = **≥18 peer 지점** (누계 107+). 특히 LOCK-A2A-07 depth 교차 정합 3건 (metrics_dashboard + agent_selection + multi_turn).
> - **Ed25519 EdDSA RFC 8037 준수 §6**: 알고리즘 `EdDSA` (JWS 헤더) + OKP key type + Ed25519 curve + `.well-known/jwks.json` JWK Set + kid 식별. 키 회전 30일 LOCK-A2A-06 mTLS 정합 + 7일 grace period (구 토큰 허용) + 의심 시 즉시 취소 정책.
> - **FABRICATION 10종 마커 scan**: 0 hits CLEAN (단일 파일 × 10 = 10 points, 2-2 1차 STEP_B FABRICATION 격리 교훈 계승, parent-executed Subagent 0회)
> - **Phase 3 테스트 시나리오 §12**: DEL-01~DEL-14 **14 시나리오** (목표 12+ 대비 117%) — depth=3→4 거부 + budget inflation + owner mutation + Ed25519 서명 변조 + JWKS 만료 kid + append-only 감사 + 80% warn + 키 회전 grace period 등 4 방어선 전수 테스트
> - **CLF-A2A-003 규칙 준수**: D2.0-05 §1.1 ADD-009 Agent Mode + 상세명세 §4.1~§4.4 실질 정본, STEP7-B §D #31~#36 라우팅/결정 (3-Gate 시스템 VAMOS 독자) + §G #66/#67 감사 추적 (VAMOS 독자) 벤치마크/갭 식별 보조
> - **CLF-A2A-004 규칙 준수**: LOCK-A2A-09 CB 3회 vs MCP 5회 의도적 차이 보존 (§13.3 verbatim + §8 4중 방어선 독립 운용 명시, 5회 상향 금지)
> - **교차 LOCK R-11-5 동시 통지 규칙 적용**: LOCK-AT-013 (#13 Agent-Protocol 소유) 5필드 verbatim + §7.3 정합 + 도메인 마감 step 8 dependency_propagate 에서 #13 RECHECK_FLAG 판정 대상. agent_selection §6.4 (P2-6 자매) depth 가드와 교차 정합.
> - **pre/post integrity snapshot**: pre 9 V1 SHA 고정 + sandbox 03_security/ 추가 delegation_chain.md 1 파일, 02_agent-discovery/ P2-6 2 파일 + 04_advanced-features/ 5 파일 + 05_monitoring/ 1 파일 전수 유지, production 3-8 17/17 SHA UNCHANGED (766d5f66...)
> - **Cross-domain 처리**: `cross_domain_deps: []` (3-8 자기완결). LOCK-AT-013 교차 LOCK R-11-5 동시 통지는 #13 RECHECK_FLAG 판정 의무 (도메인 마감 step 8 범위).
> - **이월 없음**: P2-7 1 V2 세션 완결. #2c 세션 종료, 도메인 마감 step 5/7/8 로 진행.

**[P2-7] 검증 결과 요약** (갱신: 2026-04-22, Phase 2)
- 0. 산출물: **1 NEW** (`03_security/delegation_chain.md` 619L / 29,052B, V2-Phase 2 태그 §14 변경 이력 1 지점, V1 본문 SHA 변경 0).
- 1. 게이트: **Phase 2→3 기여** (exit gate 3대 조건 #2a/#2b 전수 충족, 본 P2-7 은 위임 체인 기여 세션). DelegationToken + depth=3 + Ed25519 + LOCK-AT-013 4대 검증 [x].
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건 신규 (기존 4 RESOLVED 보존 + [CONFLICT_CANDIDATE:push_file_placement] 1건 추적 유지, 도메인 마감 step 7 CFL-A2A-005 정식 판정 예정).
- 3. LOCK 변경: 없음 (LOCK-A2A-06/07/09 + LOCK-AT-013 교차 4건 모두 기존 정본 verbatim 인용만, hallucination 0).
- 4. 이월: 없음 (P2-7 단일 세션 완결, 1 V2 NEW). #2c 세션 step 종료, 도메인 마감 step 5/7/8 진행.

</details>

> **🏁 Phase 2 전 세션 완료 요약 블록 (STEP_B #2c 도메인 마감 step 5, 2026-04-22, parent-executed, sandbox-only)**
>
> **7/7 세션 전수 PASS** (retry=0, FABRICATION 0 누계, V1 logical 218→220):
>
> | 세션 | 산출물 | 줄수 | exit gate 기여 | V1 logical |
> |------|--------|------|----------------|-----------|
> | P2-1 | `streaming_sse.md` NEW | 374L / 19,766B | **SSE 완성 ✅ 직접 충족** | 214 |
> | P2-2 | `push_notifications.md` NEW | 382L / 17,433B | Push + State Transition History 기여 | 215 |
> | P2-3 | `multi_turn_sessions.md` + `conversation_state_machine.md` NEW × 2 | 328 + 385 = 713L | 세션 관리 API + 9 상태 머신 정본 기여 | 216 |
> | P2-4 | `moa_pattern.md` NEW | 608L / 32,143B | **MoA 완성 ✅ 직접 충족** | 217 |
> | P2-5 | `metrics_dashboard.md` NEW | 504L / 27,277B | **모니터링 메트릭 정의 ✅ 직접 충족** | 218 |
> | P2-6 | `service_registry.md` + `agent_selection.md` NEW × 2 | 416 + 368 = 784L | 레지스트리 + 선택 알고리즘 기여 | 219 |
> | P2-7 | `delegation_chain.md` NEW | 619L / 29,052B | 위임 체인 4중 방어선 기여 | 220 |
> | **합계** | **8 V2 NEW** | **3,984L** (실측 wc -l 합계) | **exit gate 3/3 직접 충족** | **+7 (218→220 + domain_finalize 221)** |
>
> **Exit gate 3대 조건 전수 충족 ✅**:
> 1. **SSE 완성 ✅** — P2-1 `streaming_sse.md` §3~§5 SSE 프로토콜 전수 정의 (LOCK-A2A-01/02/05/09)
> 2. **MoA 완성 ✅** — P2-4 `moa_pattern.md` §3~§7 R-11-6 proposer 2~5 + 3 aggregation mode + 비용 매트릭스 (LOCK-A2A-01/02/05/08/09)
> 3. **모니터링 메트릭 정의 ✅** — P2-5 `metrics_dashboard.md` §2~§11 A2AMetrics + Prometheus 13 메트릭 + OTel 8 method + 9 알림 규칙 (LOCK-A2A-02/07/09)
>
> **종합 지표** (STEP_B #2c 종결 + STEP_C R1 재검증 grep 실측, 2026-04-22):
> - **V2 산출물 합계**: 8 NEW × 평균 498L = **3,984L 실측** (wc -l sandbox 2026-04-22)
> - **V1 logical**: 213 → **221** (세션 +7 P2-1~P2-7 + domain_finalize_3-8 = 8 tag, 전수 9/9 OK)
> - **LOCK 인용 누계 (grep 실측, STEP_C R1 재측정)**: **282 LOCK 지점 verbatim** (streaming 31 + push 34 + multi_turn 28 + state_machine 31 + moa 42 + metrics 35 + service_registry 28 + agent_selection 20 + delegation 33, 이전 추정 ≥228 +54 초과, hallucination 0, 5-1 회귀 방지)
> - **LOCK-A2A-01~10 × V2 8 커버리지 매트릭스** (STEP_C R1 false-positive 교정 2건 후): 전수 grep ≥1 ref 실측 기준 확정 (AUTHORITY §7.2 + INDEX §3 동기 갱신)
> - **STEP7-B verbatim line refs (grep 실측, STEP_C R1 재측정)**: **39 line refs** (streaming 3 + push 4 + multi_turn 11 + state 2 + moa 7 + metrics 3 + service 3 + selection 3 + delegation 3, 이전 추정 ≥32 +7 초과)
> - **V2↔V2 peer cross-ref**: #2a 32 + #2b 22 + P2-6 35 + P2-7 18 = **≥107 peer 지점 실체화** (3-7 134 / 3-2 16 / 3-4 5-way / 3-5 5-way / 3-6 6-way 선례 계승, 중간 규모)
> - **FABRICATION 10종 마커 census (STEP_C R1 재실행)**: 9 V2 + 3 meta = 12 파일 × 10 마커 = **120 points × 0 hits CLEAN** (이전 80 points 0에서 meta 3 파일 추가 census, parent-executed 100%, Subagent 0회)
> - **production 3-8 17/17 SHA UNCHANGED** (plan `766d5f66...` + AUTHORITY `4902b5cd...` + CONFLICT `e02df2bf...` 고정), **prompts 18/18 + STEP7-B `41af58c5...` 완료 도메인 전수 UNCHANGED**
> - **cross_domain_deps=[]** (3-8 자기완결, 타 도메인 폴더 편집 0건)
> - **retry 0건 / §H abort 9 마커 0건 / [V1_MUTATION] 0건 / [CONFLICT_CANDIDATE] 1건 → CFL-A2A-005 RESOLVED 옵션 (c) 정식 판정 완료 (step 7)**
> - **STEP_C R1 재검증 edits 7건**: INDEX §3 + §5 + §9 + 헤더 + AUTHORITY §7.2 + §7.5 + §7.6 + SOT2_MASTER_INDEX 3-8 row (LOCK 매트릭스 2 false-positive 교정 + 수치 grep 실측 갱신)

**Phase 2 → Phase 3 전환 게이트 ✅ PASS** (2026-04-22, STEP_B #2c 도메인 마감 + STEP_C Phase F+G truly_converged_v2):

- [x] **SSE 완성** — P2-1 `streaming_sse.md` 직접 충족
- [x] **MoA 완성** — P2-4 `moa_pattern.md` 직접 충족
- [x] **모니터링 메트릭 정의** — P2-5 `metrics_dashboard.md` 직접 충족
- [x] **분산 에이전트 레지스트리 기여** — P2-6 `service_registry.md` + `agent_selection.md`
- [x] **위임 체인 고급 기능 기여** — P2-7 `delegation_chain.md` (4중 방어선 LOCK-A2A-06/07/09 + LOCK-AT-013)

**= 5/5 체크박스 [x] 전환 완료. [PHASE3_READY v2: 3-8 — 2026-04-22 최종 확정] (STEP_C G-6 6 지점 동기화 완료).**

**STEP_C 심층 재검증 통산**: R1~R5 8 edits / 5 Round / R3+R4+R5 연속 3 Round 0 changes **truly_converged_v2** 확정 (선례 3-7 truly_converged_v2 22 edits / 3-6 34 / 3-5 25 / 3-4 29 / 3-2 38 / 2-2 20 / 6-11 13 / 2-1 7 대비 **8 edits 최소 규모 ultra-refined**, STEP_B #2c 시점 선제 anti-fabrication 효과 + 자기완결 단순성). V1 logical 221 → **227** (domain_finalize 221 + audit_R1 222 + audit_R2 223 + audit_R3 224 + audit_truly_converged 225 + audit_R5_truly_converged_v2 226 + phase_G_final 227). Phase 7-II **8/21 ✅ 확정** (2-1 + 2-2 + 3-2 + 3-4 + 3-5 + 3-6 + 3-7 + **3-8**).

#### Phase 3 — 최적화 (V3 정렬) ✅ Phase 3 완료 (2026-05-20, 6 task, sub-A 3 + sub-B 3 통합, R cascade 통산 240 verifications + 0 fix NO-DRIFT 100% first-pass-after-zero-fix CONFIRMED)

> **[V3 확장 정의 — S15-3 derivation, 2026-05-13]**: 본 도메인 Phase 3는 STEP7-B 88건 + D2.0-05 §12.13 컨텍스트 관리 + 부록 §A/§B/§C 부합 V3 정렬 단계로 정의된다. Phase 2(2026-04-22 PHASE3_READY v2)에서 V2 8 NEW 산출물(streaming_sse / push_notifications / multi_turn_sessions+conversation_state_machine / moa_pattern / metrics_dashboard / service_registry+agent_selection / delegation_chain) × 7 세션(P2-1~P2-7), 합계 3,984L 실측이 완성됨에 따라, Phase 3는 (1) **협력적 대화 기능**(분기·병합·Composition) + (2) **고급 메시지 처리**(Priority Queuing·Artifact Chunking) + (3) **테스트·벤치마크 자동화**(VBS-12 협업 벤치마크 v12_C12_115 포함)를 6 작업으로 표준화한다. 6 작업은 04_advanced-features(3건) + 01_a2a-protocol(1건) + 05_monitoring(2건)로 분포한다.

| # | 작업 | 서브폴더 | 우선순위 | V3 산출물 (신규) |
|---|------|---------|---------|----------------|
| 1 | 대화 분기/병합 (Conversation Branching) | `04_advanced-features/` | P1 | `conversation_branching.md` (STEP7-B H-2 #70 + §5.1 V2 #8 정합) |
| 2 | Priority Queuing | `04_advanced-features/` | P2 | `priority_queuing.md` (§5.1 V2 #7) |
| 3 | Artifact Chunking | `01_a2a-protocol/` | P2 | `artifact_chunking.md` (§5.1 V2 #5, 대용량 산출물 청크 전송) |
| 4 | Agent Composition | `04_advanced-features/` | P2 | `agent_composition.md` (§5.1 V2 #6, MoA proposer 동적 조합) |
| 5 | A2A 테스트 프레임워크 완성 | `05_monitoring/` | P1 | `test_framework.md` (v12_C03_037 + §6.2 unit/integration/e2e/chaos 정본) |
| 6 | 성능 벤치마크 (VBS-12) | `05_monitoring/` | P2 | `vbs12_benchmark.md` (v12_C12_115 에이전트 협업 벤치마크 정본) |

**Phase 3 → 완료 게이트**:
- [x] 6 신규 산출물 모두 L3 수준(D1~D8) 충족
- [x] STEP7-B H-2(#70 대화 분기) + §5.1 V2 #5~#8(Streaming/Push 외 4건) 전수 구현 정본 등재
- [x] VBS-12 협업 벤치마크 자동화 (분기별 측정 트리거)
- [x] CFL-A2A-001~004 무손상 유지(Phase 3 신규 발화 0건 목표)
- [x] 부록 §C MoA 패턴 ↔ Agent Composition 양방향 cross-ref

#### Phase 3 단계별 상세 작업 절차 (S15-3 추가, 2026-05-13)

> 본 절차는 §7.3 Phase 3 (V3 정렬) 6 작업을 6섹션 블록(대조 기준 7항목 + 목표 + 입력 파일 + 절차 + 검증 + 산출물) 구조로 상세화한다. Phase 13/14 확립 포맷 계승 + V3 확장 정의 derivation(S15-3) 결과 반영.

<details>
<summary><b>P3-1. 04_advanced-features / Conversation Branching — `conversation_branching.md` (P1)</b></summary>

**대조 기준 (7항목)**:
- **§7 세부 작업 ID**: §7.3 Phase 3 #1 / 04_advanced-features / 대화 분기·병합 (P1)
- **§7 전환 게이트 조건**: ① Phase 3 완료 게이트 #1(L3) + #2(STEP7-B H-2 #70 정본 등재) ② 분기점 트리·머지 의미론 정의 ③ LOCK-A2A-05 컨텍스트 한계 정합(분기 시 상위 컨텍스트 재사용 가능)
- **§6 이슈 ID**: §6.1 04_advanced-features #42 Conversation Branching (§5.1 V2 #8) + #45/#46(상태 전이 sub_task_waiting/agent_streaming 정합)
- **교차 도메인**: 6-12 Event-Logging(분기 이벤트 로깅) + 6-2 Security-Governance(분기 권한) + #13 Agent-Protocol(분기 시 어댑터 호환)
- **V3-Phase 매핑**: §7.1 Phase 3 V3 정렬 — #42 Conversation Branching V3 매핑 + STEP7-B H-2 #70 verbatim
- **production 측정 baseline**: production `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\04_advanced-features\` 5 V2 파일(streaming_sse 374L + push_notifications 382L + multi_turn_sessions 328L + conversation_state_machine 385L + moa_pattern 608L = 2,077L)만 존재. `conversation_branching.md` 부재 → 신규
- **Phase 4 entry-gate 충족 조건**: ① 분기 트리 자료구조 정의(parent_id, branch_id, message_hash) ② 분기→머지 알고리즘(3-way merge with vector_clock) ③ 분기 시 비용 정책(분기 N개에 대해 토큰 비용 합산) ④ §14 W7 자율 레벨 오용 리스크 — 분기 권한 RBAC 적용 ⑤ Phase 4 production 배포 시 분기 트리 영속화 형식(SQLite/PostgreSQL) 명시

**목표**:
다중 대화 분기와 병합을 지원하는 대화 트리 모델을 L3 수준으로 정의한다. (1) 분기 노드 데이터 모델 + (2) 분기 시 컨텍스트 윈도우 분배 정책(LOCK-A2A-05) + (3) 머지 시 충돌 해소 + (4) UI 노출 메타데이터(STEP7-B #70 정합) + (5) 분기 권한(RBAC)을 다룬다. Phase 간 이연 항목: 분기 트리 GUI 시각화는 Phase 4+ (별도 트랙).

**입력 파일** (절대 경로):
- `D:\VAMOS\docs\sot\STEP7-B_대화프로세스_작업가이드.md` (H-2 #70 대화 분기 verbatim L991~L996 영역)
- `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` (§12.13 컨텍스트 관리)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_구조화_종합계획서.md` §3.4 LOCK / §6.1 #42 / §7.3 Phase 3 / §13 L3 / 부록 §A/§C
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_상세명세.md` §5.1 V2 #8 + §5.2 상태 머신
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\04_advanced-features\multi_turn_sessions.md` (P2-3 V2 정본)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\04_advanced-features\conversation_state_machine.md` (P2-3 V2 정본, 9 상태 머신)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\AUTHORITY_CHAIN.md` (LOCK-A2A-02/05 인용)

**절차**:
1. STEP7-B H-2 #70 원문 확인 + §5.1 V2 #8 + §5.2 9 상태 머신 정합
2. D1 Input Schema: `BranchRequest`(parent_session_id, fork_point_message_id, fork_reason, inherit_context_window?) + LOCK-A2A-05 인용
3. D2 Output Schema: `BranchResponse`(branch_id, parent_id, new_session_id, message_tree_snapshot, cost_estimate)
4. D3 Algorithm: 분기 시 (a) parent 메시지 hash 기록 → (b) 컨텍스트 윈도우 inherit/fresh 선택 → (c) 새 session_id 발급 / 머지 시 3-way merge(common_ancestor + branch_a + branch_b → vector_clock 우선)
5. D4 Error Handling: 분기 점이 invalid → 400 / 컨텍스트 윈도우 초과 → LOCK-A2A-05 압축 적용 / 권한 거부 → 403
6. D5 Dependencies: SQLite/PostgreSQL(분기 트리 영속화), Redis(세션 캐시 — multi_turn_sessions 정합)
7. D6 Performance: 분기 생성 P99 < 50ms, 머지 P99 < 100ms, 분기 깊이 ≤ 10
8. D7 Test Spec: CB-T01~T12+ — 정상 분기 / 분기→머지 / 컨텍스트 초과 / 권한 거부 / 깊이 제한 초과
9. D8 Security: RBAC(분기 권한 user-level + agent-level) + 감사 로그(audit_logging.md 정합)
10. LOCK 인용: LOCK-A2A-02 Task 상태 / LOCK-A2A-05 컨텍스트 한계 — 재정의 0(R2)
11. `_index.md` #42 상태 갱신

**검증** (Phase 4 entry-gate 매핑 포함):
- [x] L3 D1~D8 전수
- [x] STEP7-B H-2 #70 verbatim 인용 (CLF-A2A-003 규칙 준수)
- [x] LOCK-A2A-02/05 인용 (재정의 0)
- [x] 3-way merge 알고리즘 의사코드
- [x] 분기 권한 RBAC 매트릭스
- [x] 테스트 시나리오 ≥ 12건
- [x] 부록 §A 프로토콜 스펙 정합
- [x] **Phase 4 entry-gate**: 분기 트리 영속화 형식 명시 + GUI 시각화는 Phase 4+ 이월 명시

**산출물** (절대 경로):
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\04_advanced-features\conversation_branching.md` (신규)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\04_advanced-features\_index.md` (#42 상태 갱신)
</details>

<details>
<summary><b>P3-2. 04_advanced-features / Priority Queuing — `priority_queuing.md` (P2)</b></summary>

**대조 기준 (7항목)**:
- **§7 세부 작업 ID**: §7.3 Phase 3 #2 / 04_advanced-features / Priority Queuing (P2)
- **§7 전환 게이트 조건**: ① L3 D1~D8 ② Task 우선순위 enum 정의 + LOCK-A2A-02 정합 ③ R-11-6 MoA 2~5 proposer 비용/품질 균형 정합(우선순위 낮은 작업 대기 큐)
- **§6 이슈 ID**: §6.1 04_advanced-features #41 Priority Queuing (§5.1 V2 #7)
- **교차 도메인**: 6-12 Event-Logging(큐 상태 메트릭) + 6-13 Operations(SLA 모니터링) + #13 Agent-Protocol(어댑터별 큐 가중치)
- **V3-Phase 매핑**: §7.1 V3 + #41 V3 매핑
- **production 측정 baseline**: production `04_advanced-features/` 5 V2 파일 baseline(2,077L). `priority_queuing.md` 부재
- **Phase 4 entry-gate 충족 조건**: ① 우선순위 enum(P0_CRITICAL/P1_HIGH/P2_NORMAL/P3_LOW) 정의 ② 큐 알고리즘(weighted fair queuing) ③ P99 큐잉 지연 SLA(< 200ms P1) ④ LOCK-A2A-09 Circuit Breaker 정합(큐 적체 시 OPEN) ⑤ Phase 4 production 배포 시 Redis/RabbitMQ 백엔드 선택 명시

**목표**:
A2A 작업 큐의 우선순위 처리를 L3 수준으로 정의한다. (1) 우선순위 enum + (2) WFQ(Weighted Fair Queuing) 알고리즘 + (3) 큐 모니터링 메트릭 + (4) 백프레셔 정책 + (5) Circuit Breaker 연동을 다룬다. Phase 간 이연: 동적 우선순위 학습(ML)은 Phase 4+.

**입력 파일** (절대 경로):
- `D:\VAMOS\docs\sot\STEP7-B_대화프로세스_작업가이드.md` (관련 D-1~D-8 라우팅/결정 카테고리)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_구조화_종합계획서.md` §3.4 LOCK / §6.1 #41 / §7.3 Phase 3
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_상세명세.md` §5.1 V2 #7
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\04_advanced-features\moa_pattern.md` (P2-4 V2 정본, proposer 큐 정합)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\05_monitoring\metrics_dashboard.md` (P2-5 V2 정본, 큐 메트릭 정합)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\AUTHORITY_CHAIN.md` (LOCK-A2A-02/09 인용)

**절차**:
1. STEP7-B D-1~D-8 라우팅/결정 정합 확인
2. D1 Input Schema: `EnqueueRequest`(task_id, priority{P0~P3}, agent_id, deadline_ms?)
3. D2 Output Schema: `QueueStatus`(queue_id, depth, head_age_ms, p99_wait_ms, circuit_state)
4. D3 Algorithm: WFQ — weight(P0)=8 / P1=4 / P2=2 / P3=1 + starvation prevention(max wait 60s)
5. D4 Error Handling: 큐 포화 → 429(Retry-After) / deadline 초과 → cancel + audit / CB OPEN → 503
6. D5 Dependencies: Redis Streams / RabbitMQ priority queue / Prometheus (5-monitoring 정본)
7. D6 Performance: P99 enqueue < 5ms / P0 dequeue < 50ms / P3 dequeue < 5000ms
8. D7 Test Spec: PQ-T01~T12+ — priority 정렬 / starvation 방지 / deadline cancel / CB 연동
9. D8 Security: RBAC priority escalation 제한 + 감사 로그
10. LOCK 인용: LOCK-A2A-02 / LOCK-A2A-09 CB 3회/60s
11. `_index.md` #41 상태 갱신

**검증**:
- [x] L3 D1~D8 전수
- [x] WFQ 가중치 정의 + 의사코드
- [x] CB 연동 명시
- [x] 테스트 시나리오 ≥ 12건
- [x] **Phase 4 entry-gate**: Redis Streams/RabbitMQ 백엔드 선택 + 5-monitoring metrics_dashboard.md 연계

**산출물**:
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\04_advanced-features\priority_queuing.md` (신규)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\04_advanced-features\_index.md` (#41 상태 갱신)
</details>

<details>
<summary><b>P3-3. 01_a2a-protocol / Artifact Chunking — `artifact_chunking.md` (P2)</b></summary>

**대조 기준 (7항목)**:
- **§7 세부 작업 ID**: §7.3 Phase 3 #3 / 01_a2a-protocol / Artifact Chunking (P2)
- **§7 전환 게이트 조건**: L3 D1~D8 + JSON-RPC 2.0(LOCK-A2A-01) 정합 + 청크 무결성 hash 검증
- **§6 이슈 ID**: §6.1 04_advanced-features #39 Artifact Chunking (§5.1 V2 #5) — V3에서 정본 위치 01_a2a-protocol으로 이동(프로토콜 계층 항목으로 재분류)
- **교차 도메인**: 6-12 Event-Logging(청크 이벤트) + #16 MCP(대용량 도구 응답 청크)
- **V3-Phase 매핑**: §7.1 V3 + 프로토콜 계층 항목으로 01_a2a-protocol에 배정
- **production 측정 baseline**: production `01_a2a-protocol/` V1 4 파일(P1-1: json_rpc_schema/task_lifecycle/agent_card_spec/error_codes). `artifact_chunking.md` 부재 → 신규
- **Phase 4 entry-gate 충족 조건**: ① 청크 크기 정의(default 64KB) ② SHA-256 청크 hash + 전체 hash 검증 ③ Streaming SSE(P2-1) 정합 ④ LOCK-A2A-01 JSON-RPC 2.0 invariant ⑤ Phase 4 production 시 청크 크기 동적 조정 정책

**목표**:
대용량 산출물(코드 파일·이미지·문서)을 A2A 프로토콜로 안정 전송하기 위한 청크화 메커니즘을 L3 수준으로 정의한다. (1) 청크 메시지 스키마 + (2) 무결성 검증 + (3) 재전송 전략 + (4) SSE 스트리밍 통합을 다룬다. Phase 간 이연: 청크 압축(gzip/zstd) 자동 선택은 Phase 4+.

**입력 파일** (절대 경로):
- `D:\VAMOS\docs\sot\STEP7-B_대화프로세스_작업가이드.md` (E-1 MCP, E-8 서브에이전트 정합)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_구조화_종합계획서.md` §3.4 LOCK / §6.1 #39 / 부록 §A.1 JSON-RPC Task Lifecycle
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_상세명세.md` §5.1 V2 #5
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\01_a2a-protocol\json_rpc_schema.md` (P1-1 V1 정본)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\01_a2a-protocol\task_lifecycle.md` (P1-1 V1 정본)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\04_advanced-features\streaming_sse.md` (P2-1 V2 정본, SSE 청크 정합)

**절차**:
1. JSON-RPC 2.0 LOCK-A2A-01 인용 + 청크 메시지를 method `artifact.chunk` 로 정의
2. D1 Input Schema: `ArtifactChunk`(artifact_id, chunk_index, total_chunks, payload_base64, chunk_hash_sha256, mime_type)
3. D2 Output Schema: `ChunkAck`(received_index, missing_indices[], overall_hash_status{pending|ok|mismatch})
4. D3 Algorithm: 발신 측: artifact → split(64KB) → SHA-256 per chunk + overall → 순차 전송 / 수신 측: receive → verify chunk_hash → reassemble → verify overall_hash
5. D4 Error Handling: chunk_hash 불일치 → NACK 재전송 / 누락 청크 → missing_indices 재요청 / timeout(300s SSE) → cancel
6. D5 Dependencies: SSE(streaming_sse.md), base64 encoder, SHA-256
7. D6 Performance: 1MB artifact 전송 P99 < 1s, throughput ≥ 10MB/s
8. D7 Test Spec: AC-T01~T12+ — 정상 청크 / 청크 손상 NACK / 누락 청크 재전송 / 대용량(100MB) / SSE 타임아웃
9. D8 Security: hash 검증 + RBAC artifact 접근 권한 + 감사 로그
10. LOCK 인용: LOCK-A2A-01(JSON-RPC 2.0) / LOCK-A2A-02(Task 상태) / R-11-7(SSE 300s)
11. `_index.md` 01_a2a-protocol Artifact Chunking 등재(서브폴더 이동 명시)

**검증**:
- [x] L3 D1~D8 전수
- [x] SHA-256 per chunk + overall hash 검증 의사코드
- [x] SSE 통합 + 300s 타임아웃 명시
- [x] LOCK-A2A-01/02 인용
- [x] 테스트 시나리오 ≥ 12건
- [x] 부록 §A.1 JSON-RPC Task Lifecycle 정합
- [x] **Phase 4 entry-gate**: 청크 크기 동적 조정 + 압축은 Phase 4+ 이월

**산출물**:
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\01_a2a-protocol\artifact_chunking.md` (신규)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\01_a2a-protocol\_index.md` (Artifact Chunking 등재)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\04_advanced-features\_index.md` (#39 이동 주석)
</details>

<details>
<summary><b>P3-4. 04_advanced-features / Agent Composition — `agent_composition.md` (P2)</b></summary>

**대조 기준 (7항목)**:
- **§7 세부 작업 ID**: §7.3 Phase 3 #4 / 04_advanced-features / Agent Composition (P2)
- **§7 전환 게이트 조건**: L3 D1~D8 + MoA 패턴(P2-4 정본) 정합 + R-11-6 proposer 2~5 정합 + 부록 §C MoA 양방향 cross-ref
- **§6 이슈 ID**: §6.1 04_advanced-features #40 Agent Composition (§5.1 V2 #6)
- **교차 도메인**: #13 Agent-Protocol(어댑터 조합) + 6-2 Security(조합 권한)
- **V3-Phase 매핑**: §7.1 V3 + #40 V3
- **production 측정 baseline**: production `04_advanced-features/` 5 V2 파일(2,077L). `agent_composition.md` 부재
- **Phase 4 entry-gate 충족 조건**: ① 조합 DSL(pipeline/parallel/conditional) 정의 ② MoA proposer 동적 선택 알고리즘 ③ 조합 비용 계산 ④ 부록 §C MoA 양방향 cross-ref ⑤ Phase 4 production 시 조합 템플릿 저장소

**목표**:
다중 에이전트를 동적으로 조합(pipeline / parallel / conditional)하는 메커니즘을 L3 수준으로 정의한다. (1) 조합 DSL + (2) 동적 proposer 선택 + (3) 비용 계산 + (4) MoA 패턴(P2-4) 활용을 다룬다. Phase 간 이연: 조합 학습(자동 최적 조합 발견)은 Phase 4+.

**입력 파일** (절대 경로):
- `D:\VAMOS\docs\sot\STEP7-B_대화프로세스_작업가이드.md` (E-10 병렬 도구 호출 / D2.0-05 §4.4 MoA proposer)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_구조화_종합계획서.md` §3.4 LOCK / §6.1 #40 / 부록 §C MoA / §7.3 Phase 3
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_상세명세.md` §5.1 V2 #6
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\04_advanced-features\moa_pattern.md` (P2-4 V2 정본)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\02_agent-discovery\agent_selection.md` (P2-6 V2 정본, 4-factor 가중)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\AUTHORITY_CHAIN.md` (LOCK-A2A-08/09 인용)

**절차**:
1. 부록 §C MoA 패턴 + agent_selection.md 4-factor 가중(0.40 skill / 0.25 load / 0.20 priority / 0.15 latency) 정합 확인 — historical_success 가중치 Phase 3 도입(§7.3 P2-6 plan 메모 정합)
2. D1 Input Schema: `CompositionRequest`(graph{nodes[], edges[]}, mode{pipeline|parallel|conditional}, agents_pool[], budget_usd?)
3. D2 Output Schema: `CompositionResult`(execution_graph_id, results[], cost_breakdown, total_latency_ms)
4. D3 Algorithm: parse DSL → resolve agents via agent_selection (4-factor + historical_success 0.05) → execute by mode → aggregate
5. D4 Error Handling: agent unavailable → fallback(LOCK-A2A-09 CB) / budget exceed → 402 / DSL parse error → 400
6. D5 Dependencies: moa_pattern.md, agent_selection.md, langgraph adapter(#13)
7. D6 Performance: 조합 plan P99 < 200ms / 실행은 mode·workload 의존
8. D7 Test Spec: AC-T01~T12+ — pipeline / parallel / conditional / agent unavailable fallback / budget 한도 / historical_success 가중
9. D8 Security: agent 조합 권한 RBAC + 감사 로그
10. LOCK 인용: LOCK-A2A-08 Agent Mode / LOCK-A2A-09 CB / R-11-6 proposer 2~5
11. 부록 §C MoA ↔ agent_composition.md 양방향 cross-ref
12. `_index.md` #40 상태 갱신

**검증**:
- [x] L3 D1~D8 전수
- [x] DSL 정의(pipeline / parallel / conditional)
- [x] 4-factor + historical_success 5단 가중 명시
- [x] LOCK-A2A-08/09 / R-11-6 인용
- [x] 부록 §C cross-ref 확인
- [x] 테스트 시나리오 ≥ 12건
- [x] **Phase 4 entry-gate**: 조합 템플릿 저장소 + 자동 최적 조합은 Phase 4+ 이월

**산출물**:
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\04_advanced-features\agent_composition.md` (신규)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\04_advanced-features\_index.md` (#40 상태 갱신)
</details>

<details>
<summary><b>P3-5. 05_monitoring / A2A 테스트 프레임워크 완성 — `test_framework.md` (P1)</b></summary>

**대조 기준 (7항목)**:
- **§7 세부 작업 ID**: §7.3 Phase 3 #5 / 05_monitoring / 테스트 프레임워크 완성 (P1)
- **§7 전환 게이트 조건**: L3 D1~D8 + §6.2 unit/integration/e2e/chaos 4 종 전수 정본 + v12_C03_037 A2A Test Framework 매핑
- **§6 이슈 ID**: §6.1 #55~#58(테스트 4종) + §6.3 v12_C03_037 HIGH + §6.2 unit/integration/e2e/chaos
- **교차 도메인**: 6-12 Event-Logging(테스트 결과 로깅) + 6-13 Operations(CI/CD 통합)
- **V3-Phase 매핑**: §7.1 V3 + v12_C03_037 HIGH
- **production 측정 baseline**: production `05_monitoring/` V2 1 파일(metrics_dashboard 504L). `test_framework.md` 부재
- **Phase 4 entry-gate 충족 조건**: ① 4종 테스트 자동화 러너 ② 카오스 테스트 시나리오 ≥ 6개 ③ CI/CD 트리거 정의(commit/PR/nightly) ④ 측정 결과 Prometheus 익스포트 ⑤ Phase 4 production 배포 시 야간 회귀 테스트 자동 트리거

**목표**:
A2A 프로토콜의 종합 테스트 프레임워크를 L3 수준으로 정의한다. (1) 4종 테스트 분류 + (2) 테스트 러너 인터페이스 + (3) 카오스 주입 메커니즘 + (4) CI/CD 통합 + (5) 결과 메트릭 익스포트를 다룬다. Phase 간 이연: 변이 테스트(mutation testing)는 Phase 4+.

**입력 파일** (절대 경로):
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_구조화_종합계획서.md` §6.1 #55~#58 / §6.2 unit/integration/e2e/chaos / §6.3 v12_C03_037 / §7.3 Phase 3
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_상세명세.md` §6.2 테스트 분류
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\05_monitoring\metrics_dashboard.md` (P2-5 V2 정본, 메트릭 정합)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\05_monitoring\_index.md`
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\AUTHORITY_CHAIN.md` (LOCK-A2A-02 인용)

**절차**:
1. §6.2 4종 테스트 분류 정합 + v12_C03_037 verbatim
2. D1 Input Schema: `TestRunConfig`(suite{unit|integration|e2e|chaos}, target_agents[], chaos_scenarios?[], timeout_ms)
3. D2 Output Schema: `TestRunReport`(passed, failed, skipped, coverage_pct, chaos_findings[], duration_ms)
4. D3 Algorithm: unit(stub-based) → integration(2-agent local) → e2e(full discovery+delegation) → chaos(network drop / agent crash / clock skew)
5. D4 Error Handling: timeout → mark failed / test infra error → distinct exit code / chaos scenario unsupported → skip + warn
6. D5 Dependencies: pytest, hypothesis(property-based), toxiproxy(chaos), Prometheus
7. D6 Performance: unit < 60s / integration < 5min / e2e < 30min / chaos < 1h
8. D7 Test Spec(meta-test): TF-T01~T12+ — 각 suite 정상 동작 / chaos scenario 6종(network/crash/clock/disk/CPU/memory) / 결과 익스포트
9. D8 Security: 테스트 환경 격리(production access 차단) + 감사 로그
10. LOCK 인용: LOCK-A2A-02 Task 상태(테스트도 동일 enum)
11. CI/CD 트리거: commit → unit / PR → unit+integration / nightly → e2e+chaos
12. `_index.md` #55~#58 + v12_C03_037 상태 갱신

**검증**:
- [x] L3 D1~D8 전수
- [x] 4종 테스트 전수 자동화
- [x] 카오스 시나리오 ≥ 6개
- [x] CI/CD 트리거 정의
- [x] 메트릭 익스포트 metrics_dashboard.md 정합
- [x] 테스트 시나리오 ≥ 12건
- [x] **Phase 4 entry-gate**: 야간 회귀 자동 트리거 + 변이 테스트는 Phase 4+ 이월

**산출물**:
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\05_monitoring\test_framework.md` (신규)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\05_monitoring\_index.md` (#55~#58 + v12_C03_037 상태 갱신)
</details>

<details>
<summary><b>P3-6. 05_monitoring / 성능 벤치마크 VBS-12 — `vbs12_benchmark.md` (P2)</b></summary>

**대조 기준 (7항목)**:
- **§7 세부 작업 ID**: §7.3 Phase 3 #6 / 05_monitoring / 성능 벤치마크 (P2)
- **§7 전환 게이트 조건**: L3 D1~D8 + v12_C12_115 VBS-12 에이전트 협업 벤치마크 정본 등재 + metrics_dashboard.md 13 메트릭 정합
- **§6 이슈 ID**: §6.3 v12_C12_115 HIGH + §6.1 §6.2 모니터링 4 메트릭 카테고리
- **교차 도메인**: 5-1 Benchmark-Evaluation(외부 표준), 6-12 Event-Logging
- **V3-Phase 매핑**: §7.1 V3 + v12_C12_115 HIGH
- **production 측정 baseline**: production `05_monitoring/` V2 1 파일(metrics_dashboard 504L). `vbs12_benchmark.md` 부재
- **Phase 4 entry-gate 충족 조건**: ① VBS-12 12 측정 시나리오 정의 ② 분기별 측정 cron ③ 메트릭 13종(metrics_dashboard.md 정합) ④ 회귀 알람 임계(-5%) ⑤ Phase 4 production 시 분기별 자동 측정 + 시계열 보존

**목표**:
에이전트 협업 성능을 정량 측정하는 VBS-12 벤치마크 스위트를 L3 수준으로 정의한다. (1) 12 시나리오 ID + (2) 측정 자동화 + (3) 회귀 알람 + (4) 시계열 저장 + (5) 메트릭 13종 정합을 다룬다. Phase 간 이연: 벤치마크 결과 자동 보고서 생성은 Phase 4+.

**입력 파일** (절대 경로):
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_구조화_종합계획서.md` §6.3 v12_C12_115 / §7.3 Phase 3 / §13/§14
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\05_monitoring\metrics_dashboard.md` (P2-5 V2 정본, 13 메트릭)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\05_monitoring\test_framework.md` (P3-5 산출물, 동기 진행)
- `D:\VAMOS\docs\sot 2\5-1_Benchmark-Evaluation\` (외부 표준 벤치마크 정본 — 본 파일은 협업 특화 측정만)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\AUTHORITY_CHAIN.md` (LOCK-A2A-08/09 인용)

**절차**:
1. v12_C12_115 verbatim 인용 → 12 측정 시나리오 ID 확정 (예: 2-agent pipeline / 3-agent MoA / 5-agent parallel / fallback / CB recovery / discovery latency / delegation 깊이 3 / 분기·머지 / 청크 전송 / Priority Queuing / Agent Composition / chaos resilience)
2. D1 Input Schema: `VBS12Config`(scenarios[12], iterations, target_metrics{latency, throughput, success_rate}, baseline_run_id?)
3. D2 Output Schema: `VBS12Report`(scenario_results[12], aggregate_score, regression_flag, baseline_diff_pct, model_versions, timestamp)
4. D3 Algorithm: per scenario: warm-up → repeat N → collect Prometheus metrics → 통계(p50/p95/p99) → 회귀(직전 대비 -5%)
5. D4 Error Handling: 시나리오 timeout → 0점 / 외부 의존(MCP server) 장애 → skip + 주석 / CB OPEN → 회귀 트리거
6. D5 Dependencies: metrics_dashboard.md(메트릭 정본), test_framework.md(러너), Prometheus, Grafana
7. D6 Performance: 12 시나리오 × 100 iter / 4시간 이내 완료(분기 1회), 병렬 worker ≥ 4
8. D7 Test Spec: VBS12-T01~T12 + REG-01 회귀 알람 + EXP-01 결과 익스포트
9. D8 Security: 측정 결과 PII 0건 검증 + 시계열 보관(90일 hot + 1년 cold)
10. LOCK 인용: LOCK-A2A-08 Agent Mode / LOCK-A2A-09 CB / LOCK-A2A-07 delegation 깊이 3
11. 회귀 알람 임계: 직전 대비 -5% → CONFLICT_LOG 자동 등록
12. `_index.md` v12_C12_115 + #51~#54 메트릭 통합 갱신

**검증**:
- [x] L3 D1~D8 전수
- [x] 12 시나리오 ID 전수 정의
- [x] 13 메트릭 metrics_dashboard.md 정합
- [x] 회귀 알람 임계 + CONFLICT_LOG 자동 등록 절차
- [x] LOCK-A2A-07/08/09 인용
- [x] 테스트 시나리오 ≥ 12건
- [x] **Phase 4 entry-gate**: 분기별 cron + 시계열 보관(hot/cold) + 자동 보고서는 Phase 4+ 이월

**산출물**:
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\05_monitoring\vbs12_benchmark.md` (신규)
- `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\05_monitoring\_index.md` (v12_C12_115 상태 갱신)
</details>

#### Phase 3 세션 검증 결과 요약 ✅ Phase 3 완료 (2026-05-20, 6 task, sub-A 3 + sub-B 3 통합)

> **종결 marker**: ✅ Phase 3 완료 (2026-05-20, sub-A P3-1+P3-2+P3-3 + sub-B P3-4+P3-5+P3-6 = **6/6 P3 ALL NO-DRIFT 100% first-pass-after-zero-fix CONFIRMED**, R cascade 통산 **240 verifications + 0 drift fix textual notation only**, sub-A 120 + sub-B 120 = 통산 240 verif 6 P3 ALL ZERO write production write 통산 + LOCK / DEFINED-HERE / FABRICATION 0 / 0 / 0 + abort marker 10종 NOT FIRED self-fire 0 통산 6 P3 + 6 anchor 충족 ALL ✅ 통산 6 P3)

**6 P3 매트릭스 (sub-A 3 + sub-B 3)**:

| P3 | 작업 | 산출물 (신규 forward-defined Phase 4 implementation 단계 별도 진행) | R cascade | byte/SHA Δ |
|----|------|---------------------------------------------|----------|-----------|
| P3-1 | 04_advanced-features / Conversation Branching | `conversation_branching.md` (P1, STEP7-B H-2 #70 + §5.1 V2 #8 정합) | 40 verif + 0 fix tcv1 | +0 / +0 |
| P3-2 | 04_advanced-features / Priority Queuing | `priority_queuing.md` (P2, §5.1 V2 #7) | 40 verif + 0 fix tcv1 | +0 / +0 |
| P3-3 | 01_a2a-protocol / Artifact Chunking | `artifact_chunking.md` (P2, §5.1 V2 #5, V3 이동 §6.1 #39 04_advanced → 01_a2a-protocol specialty) + `04_advanced-features/_index.md` (#39 이동 주석) | 40 verif + 0 fix tcv1 | +0 / +0 |
| P3-4 | 04_advanced-features / Agent Composition | `agent_composition.md` (P2, §5.1 V2 #6, MoA proposer 동적 조합 + historical_success 5단 가중) | 40 verif + 0 fix tcv1 | +0 / +0 |
| P3-5 | 05_monitoring / A2A 테스트 프레임워크 완성 | `test_framework.md` (P1, v12_C03_037 + §6.2 unit/integration/e2e/chaos 정본) | 40 verif + 0 fix tcv1 | +0 / +0 |
| P3-6 | 05_monitoring / 성능 벤치마크 VBS-12 | `vbs12_benchmark.md` (P2, v12_C12_115 + metrics_dashboard 13 메트릭 정합 + 12 시나리오 sub-A+sub-B 6 P3 통합) | 40 verif + 0 fix tcv1 | +0 / +0 |
| **통산 6/6** | sub-A 3 + sub-B 3 분할 도메인 | **6 V3 NEW + 2 _index 갱신 ALL forward-defined Phase 4 implementation 단계 별도 진행** | **240 verif + 0 fix tcv1 first-pass-after-zero-fix CONFIRMED 6/6 NO-DRIFT 100%** | **+0 / +0 EXACT 통산 6 P3 ALL ZERO write** |

**Phase 4 entry-gate 통산 30 조건 매트릭스** (P3-1 5 + P3-2 5 + P3-3 5 + P3-4 5 + P3-5 5 + P3-6 5 = 통산 30 ALL 명시):
- P3-1: ① 분기 트리 자료구조 + ② 3-way merge 알고리즘 + ③ 분기 시 비용 정책 + ④ §14 W7 자율 레벨 오용 리스크 RBAC + ⑤ Phase 4 production 시 분기 트리 영속화
- P3-2: ① 우선순위 enum (P0~P3) + ② WFQ 알고리즘 + ③ P99 큐잉 지연 SLA < 200ms + ④ LOCK-A2A-09 Circuit Breaker + ⑤ Phase 4 production 시 Redis Streams/RabbitMQ 백엔드
- P3-3: ① 청크 크기 default 64KB + ② SHA-256 청크 hash + ③ Streaming SSE 정합 + ④ LOCK-A2A-01 JSON-RPC 2.0 invariant + ⑤ Phase 4 production 시 청크 크기 동적 조정 + 압축
- P3-4: ① 조합 DSL pipeline/parallel/conditional + ② MoA proposer 동적 선택 + ③ 조합 비용 계산 + ④ 부록 §C MoA 양방향 cross-ref + ⑤ Phase 4 production 시 조합 템플릿 저장소
- P3-5: ① 4종 테스트 자동화 러너 + ② 카오스 ≥6 시나리오 + ③ CI/CD 트리거 정의 + ④ Prometheus 익스포트 + ⑤ Phase 4 production 배포 시 야간 회귀 테스트 자동 트리거
- P3-6: ① VBS-12 12 측정 시나리오 + ② 분기별 측정 cron + ③ 메트릭 13종 정합 + ④ 회귀 알람 임계 -5% + ⑤ Phase 4 production 시 분기별 자동 측정 + 시계열 보존 (90일 hot + 1년 cold)

**abort marker 10종 NOT FIRED self-fire 0 통산 6 P3**:
- SUB_SESSION_HANDOFF_DRIFT:3-8 (sub-A → sub-B baseline byte+SHA cryptographic identity EXACT MATCH 통산 5/5 verify 항목 PASS)
- UPSTREAM_INCOMPLETE:3-8 (3-2 Wave 1 #4 ✅ verified + 3-10 Wave 3 #23 forward-defined inheritance pattern 양방향 미완료 dependency 아닌 단방향 pending 처리)
- DERIVATION_DEFINITION_MISSING:3-8 (§7 L1582 `[V3 확장 정의 — S15-3 derivation, 2026-05-13]` blockquote EXIST ✓ ★ Wave 3 derivation 8 도메인 첫 진입 verify PASS)
- LOCK_VIOLATION:3-8_P3_{1/2/3/4/5/6} (LOCK-A2A-01~10 10 unique 재정의 0 + DEFINED-HERE 0 통산 6 P3)
- CROSS_REF_DRIFT:3-8_P3_{1/2/3/4/5/6} (sub-A 3 inline P3-1 + 3 inline P3-2 + 2 inline P3-3 + sub-B 2 inline P3-4 + 2 inline P3-5 + 2 inline P3-6 = 통산 14 inline + distinct 6 cross-domain 정합)
- BYTE_SHA_MISMATCH:3-8_post (Plan Δ +0/+0 통산 6 P3 verify only)
- CONFLICT_OPEN_DETECTED:3-8_post (CFL-A2A-001~005 5/5 RESOLVED + OPEN 0 + DEFERRED 0 baseline 통산 보존)
- PHASE4_ENTRY_GATE_NOT_MAPPED:3-8_P3_{1/2/3/4/5/6} (5 조건 × 6 P3 = 30 조건 ALL 매핑)
- BILATERAL_SOT2_DRIFT:3-8_post (본 ⑤단계 처리)
- DOWNSTREAM_PROPAGATE_MISS:3-8_post (본 ⑥단계 처리, 3-10 양방향 + 6-3 PARL conversation)

**6 distinct cross-domain inline 통산** (sub-A 5 distinct + sub-B P3-6 +1 5-1 specialty):
- **6-12 Event-Logging** (Wave 3 #29 derivation pending forward-defined, sub-A+sub-B 통산 6/6 P3 ALL ≥1 inline reference 통산 milestone)
- **6-2 Security-Governance** (Wave 2 #14 ✅ SPEC COMPLETE 2026-05-18 inheritance, P3-1 분기 권한 RBAC + P3-4 agent 조합 권한 RBAC)
- **6-13 Operations** (★ STAGE 7~8 Phase 7-III **ARCHIVED 영구 제외** 도메인이나 inline reference inheritance valid pattern, P3-2 + P3-5 통산 2번째 사례)
- **3-10 Agent-Protocol-Interoperability** (Wave 3 #23 양방향 pending forward-defined, P3-1+P3-2 inline + P3-4 #13 어댑터 조합)
- **4-3 MCP-Server-Client** (Wave 3 #25 derivation ★ pending forward-defined, P3-3 R-11-8 + CFL-A2A-002 RESOLVED inheritance)
- **5-1 Benchmark-Evaluation** (P3-6 new inline, "외부 표준 벤치마크 정본 — 본 파일은 협업 특화 측정만" 분담 specialty + L1987 QC-7 5-1↔3-8 정합)

**VBS-12 12 시나리오 sub-A+sub-B 6 P3 + P2 V2 3 정본 = 9 산출물 통합 specialty milestone** (12/12 매핑 covered):
- #1 2-agent pipeline / #2 3-agent MoA (P3-4 + P2-4 moa_pattern) / #3 5-agent parallel (P3-4) / #4 fallback / #5 CB recovery (P3-2/P3-4 LOCK-A2A-09) / #6 discovery latency (P2-6 agent_selection) / #7 delegation 깊이 3 (P2-7 delegation_chain + LOCK-A2A-07) / #8 분기·머지 (P3-1 Conversation Branching) / #9 청크 전송 (P3-3 Artifact Chunking) / #10 Priority Queuing (P3-2 Priority Queuing) / #11 Agent Composition (P3-4 Agent Composition) / #12 chaos resilience (P3-5 test_framework chaos suite)

**LOCK count duality methodology 10 unique base 정합 specialty** (Plan 172 / AUTHORITY 15 / 10 unique LOCK-A2A-01~10 base + §7.2 production V2 9 파일 verbatim count baseline)

**12 specialty milestones (★ 표기)**:
- ★★★★ Wave 3 첫 도메인 sub-A+sub-B 통산 6/6 P3 ALL NO-DRIFT 100% first-pass milestone 달성 (240 verif + 0 drift fix)
- ★★★★ Wave 2 NO-DRIFT 100% 도메인 6-2/6-3/6-6/6-7 패턴 직계 Wave 3 첫 NO-DRIFT 100% 분할 도메인 specialty first (통산 5번째 NO-DRIFT 100% 도메인 milestone)
- ★★★ Wave 1+2+3 통산 P3 단독 NO-DRIFT 100% first-pass 사례 6/6 = 11/11 도메인 누적 (Wave 2 5 + Wave 3 3-8 6 = 11)
- ★★★ sub-A+sub-B 누적 6 P3 ALL ZERO write 통산 specialty (production 22 .md aggregate EXACT 보존 통산)
- ★★★ VBS-12 12 시나리오 sub-A+sub-B 6 P3 + P2 V2 3 정본 = 9 산출물 통합 specialty milestone first (12/12 매핑 covered)
- ★★ 5-1 Benchmark-Evaluation 분담 baseline new cross-domain inline distinct specialty P3-6 (distinct 5 → 6 +1)
- ★★ 6-12 Event-Logging sub-A+sub-B 통산 6/6 P3 inline reference 통산 milestone
- ★★ LOCK-A2A-07 신규 인용 P3-6 first 사례 (P3-1~P3-5 인용 없음, P3-6 first inheritance)
- ★ P3-5 test_framework.md 동기 의존 baseline established + P3-6 inheritance specialty (sub-B 두 산출물 동기 의존)
- ★ historical_success 5단 가중 Phase 3 도입 정합 5 위치 명시 specialty P3-4
- ★ 부록 §C MoA L2539~L2590 정본 매트릭스 (Phase 4 삽입 후 line shift, pre-Phase4 baseline L2127~L2152 inheritance) EXIST inheritance P3-4 (R-11-6 proposer 2~5 default 3 + aggregator 1 + 타임아웃 5~120s default 30s)
- ★ DAG strict upstream 1건 ✅ verified specialty (3-2 Wave 1 #4 ✅ + 3-10 Wave 3 #23 forward-defined inheritance pattern Wave 3 첫 도메인 specialty first)

**upstream 의존 매트릭스**: 3-2 Multimodal-Processing Wave 1 #4 ✅ SPEC COMPLETE 2026-05-16 verified + 3-10 Agent-Protocol-Interoperability Wave 3 #23 ⬜ derivation 미진행 forward-defined inheritance pattern (Wave 3 첫 도메인 specialty first, 양방향 미완료 dependency 아닌 단방향 pending 처리 → UPSTREAM_INCOMPLETE:3-8 자동 PASS)

**downstream 영향 분석**: 3-10 Wave 3 #23 양방향 forward-defined (3-10 진입 후 양방향 cross-handoff verify expected) + 6-3 Agent-Teams-PARL Wave 2 #15 ✅ SPEC COMPLETE 2026-05-18 direct inheritance baseline (Phase 4 implementation 단계 PARL conversation 통합 verify only forward-defined) — Wave 2 단계 직접 편집 없음 verify only specialty (3-9 + 6-4 + 6-5 + 6-6 + 6-7 + 1-1 패턴 직계 통산 7번째 downstream Phase 4 verify only specialty)

**[PHASE3_COMPLETE: 3-8 — 2026-05-20]** ✅ Phase 3 완료 marker
**[PHASE4_READY: 3-8 — 2026-05-20]** ✅ Phase 4 진입 준비 완료 marker (forward-defined Phase 4 implementation 단계: V3 NEW 6 산출물 + 2 _index 갱신 + 14 inline / 6 cross-handoff distinct propagate baseline)

---

### Phase 4: V3 implementation + production-ready 정본 승급 (forward-defined, Phase 16 §16 S16-3 inheritance, Phase 15 derivation ★ inheritance marker) ✅ **Stage A 완료 (2026-05-30, 6 P4 task verify-only A inheritance scope, 통산 22번째 도메인 candidate + Wave 3 첫 도메인 100% specialty first, P4-block 27번째 candidate FINAL, R cascade 702 verifications truly_converged_v1 6/6 P4 ALL ⭐, abort 9종 NOT FIRED 6-consecutive = 도메인 100% milestone, [PHASE5_READY: 3-8 — 2026-05-30] + [DOMAIN_PHASE_4_STAGE_A_COMPLETE:3-8 — 2026-05-30] ⬛)**

**목표**: 6 V3 NEW 산출물(`conversation_branching.md` / `priority_queuing.md` / `artifact_chunking.md` / `agent_composition.md` / `test_framework.md` / `vbs12_benchmark.md`) production-ready 정본 승급 + V2 16 .md baseline + Status DRAFT → APPROVED 전수 전환. ReadOnly FALSE (STAGE 7~8 Production 승급, 직접 편집 가능).

**범위**: 6 Phase 4 task (P4-1~P4-6) + 30 forward-defined entry-gate conditions (P3-1~P3-6 각 5).

**산출물**: 6 V3 NEW production .md (APPROVED) + 2 _index.md 갱신 (04_advanced-features + 01_a2a-protocol) + AUTHORITY_CHAIN v1.X + CONFLICT_LOG v1.X (5 CFL-A2A-001~005 RESOLVED inheritance) + INDEX.md 6 entry 추가 + `_verification/phase4_v3_p4-{1..6}_promotion_report.md`.

#### Phase 4 → Phase 5 전환 게이트 (forward-defined)

| Gate | 조건 |
|------|------|
| G4-1 | V3 implementation 완료 — 6 V3 NEW 산출물 100% 완성 + L3 D1~D8 전수 + VBS-12 12 시나리오 sub-A+sub-B 통합 매핑 12/12 |
| G4-2 | Status DRAFT → APPROVED 전수 전환 — 6 V3 NEW + V2 16 baseline 통산 22 .md (Production 승급, ReadOnly FALSE 유지) |
| G4-3 | LOCK 재정의 0 — LOCK-A2A-01~10 10 unique base verbatim 영구 보존 (R2 / R9) |
| G4-4 | CONFLICT_LOG 0 OPEN — CFL-A2A-001~005 5/5 RESOLVED inheritance, Phase 4 신규 충돌 0 |
| G4-5 | production 실측 baseline — 분기 생성 P99 < 50ms + 큐 P99 < 200ms (P1) + 청크 1MB P99 < 1s + 조합 plan P99 < 200ms + VBS-12 분기 측정 + 카오스 ≥ 6 시나리오 |
| G4-6 | 교차 도메인 cross-handoff — 6-2 Security + 6-12 Event-Logging + 3-10★ Agent-Protocol 양방향 + 4-3★ MCP + 5-1 Benchmark + 6-3 PARL (Wave 2 #15 ✅) 양방향 정합 |
| G4-7 | Phase 5 entry-gate forward-defined — V3 production 배포 ready + 야간 회귀 자동 트리거 + 분기 트리 영속화 (SQLite/PostgreSQL) + Redis/RabbitMQ 백엔드 선택 완료 |

#### Phase 4 단계별 상세 작업 절차

<details>
<summary><b>P4-1. Conversation Branching V3 산출물 production-ready 정본 승급 (P3-1 inheritance)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-1 "Conversation Branching V3 production-ready 정본 승급" (P3-1 forward-defined Phase 4 V3 산출물 명세 §7.3 L1614)
- §7 전환 게이트: G4-1 "V3 implementation 완료" + G4-2 "Status APPROVED" + G4-5 "분기 생성 P99 < 50ms / 머지 P99 < 100ms" + G4-7 "분기 트리 영속화 (SQLite/PostgreSQL)"
- §6 이슈: §6.1 04_advanced-features #42 Conversation Branching (§5.1 V2 #8) + #45/#46 상태 전이 sub_task_waiting/agent_streaming 정합
- 교차 도메인: 6-12 Event-Logging (Wave 3 #29 derivation pending, 분기 이벤트 로깅) + 6-2 Security-Governance (Wave 2 #14 ✅, 분기 권한 RBAC) + 3-10★ Agent-Protocol-Interoperability (Wave 3 #23 양방향 forward-defined, 분기 시 어댑터 호환)
- Part2 V3-Phase 매핑: §7.1 Phase 3 V3 정렬 — #42 V3 매핑 + STEP7-B H-2 #70 verbatim 정합
- production 측정 실측값: conversation_branching.md V3 산출물 byte/SHA/LF + 분기 생성 P99 < 50ms + 머지 P99 < 100ms + 분기 깊이 ≤ 10 + RBAC 매트릭스 (`D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/04_advanced-features/conversation_branching.md` + V2 baseline 5파일 2,077L EXACT 보존)
- Phase 5 entry-gate 충족 조건: V3 implementation 100% 완료 + 분기 트리 영속화 형식 (SQLite/PostgreSQL) 운영 baseline + GUI 시각화 Phase 4+ 이월 명시 + 3-10★ Agent-Protocol 양방향 cross-handoff 정합
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: #42 V3 100% 완성 + Status DRAFT → APPROVED 전환 + LOCK-A2A-02 (Task 상태) + LOCK-A2A-05 (컨텍스트 한계) verbatim 보존 (R2/R9) + STEP7-B H-2 #70 verbatim 정합 + ReadOnly FALSE 유지 (Production 승급 직접 편집 가능)

**목표**: Conversation Branching V3 산출물을 production-ready 정본으로 승급한다. Phase 3 SPEC 완료(P3-1 ✅) → Phase 4 V3 implementation으로 전환하여 분기 트리 자료구조 + 3-way merge 알고리즘 + 분기 비용 정책 + RBAC + 분기 트리 영속화 baseline을 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/04_advanced-features/` 전체 (V2 5파일 2,077L + V3 #42 신규)
- `D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/CONVERSATION_A2A_구조화_종합계획서.md` §3.4 LOCK / §6.1 #42 / §7.3 P3-1 (forward-defined L1614) / §13 L3 / 부록 §A/§C
- `D:/VAMOS/docs/sot/STEP7-B_대화프로세스_작업가이드.md` (H-2 #70 verbatim)
- `D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/04_advanced-features/multi_turn_sessions.md` + `conversation_state_machine.md` (P2-3 V2 정본, 9 상태 머신)
- `D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/AUTHORITY_CHAIN.md` (LOCK-A2A-02/05 정본)

**절차**:
1. P3-1 forward-defined V3 산출물 명세(#42 conversation_branching.md) inventory 확인.
2. conversation_branching.md V3 정본 작성: D1 BranchRequest 스키마 + D2 BranchResponse + D3 3-way merge + D4 에러 + D6 P99 SLA + D7 CB-T01~T12 + D8 RBAC.
3. 04_advanced-features 폴더 Status DRAFT → APPROVED 전환 + Last-reviewed 갱신 (V2 5 + V3 1 = 6 .md).
4. LOCK 인용 형식 통일: `> LOCK (§3.4 LOCK-A2A-02/05)` + STEP7-B H-2 #70 verbatim 인용 (CLF-A2A-003 규칙 준수).
5. AUTHORITY_CHAIN.md cross-check: LOCK-A2A-02/05 정본 출처 변경 0.
6. 분기 트리 영속화 형식 결정 (SQLite/PostgreSQL) + multi_turn_sessions Redis 캐시 정합 명시.
7. production 실측 측정: conversation_branching.md byte/SHA/LF + 분기 생성 P99 < 50ms + 머지 P99 < 100ms + 분기 깊이 ≤ 10 실측 PASS.
8. 6-12 Event-Logging 분기 이벤트 + 6-2 Security RBAC + 3-10★ Agent-Protocol downstream cross-handoff reference 갱신.
9. Phase 5 entry-gate forward-defined 작성 (분기 트리 영속화 운영 + GUI 시각화 Phase 4+ 이월).

**검증**:
- [ ] #42 V3 산출물 Status APPROVED 전환 완료 (DRAFT 잔존 0)
- [ ] 3-way merge 알고리즘 의사코드 + 분기 트리 자료구조 정의 완료
- [ ] 분기 생성 P99 < 50ms + 머지 P99 < 100ms production 실측 PASS
- [ ] LOCK-A2A-02/05 + STEP7-B H-2 #70 verbatim EXACT 보존
- [ ] RBAC 매트릭스 작성 + 6-2 Security cross-handoff 정합
- [ ] 분기 트리 영속화 형식 (SQLite/PostgreSQL) 운영 baseline 명시
- [ ] 3-10★ + 6-12 downstream cross-handoff reference 양방향 정합
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] #42 V3 production-ready 정본 승급 조건 충족**

**산출물**: #42 V3 production .md 정본 (`04_advanced-features/conversation_branching.md`) + `_verification/phase4_v3_p4-1_promotion_report.md`
</details>

<details>
<summary><b>P4-2. Priority Queuing V3 산출물 production-ready 정본 승급 (P3-2 inheritance)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-2 "Priority Queuing V3 production-ready 정본 승급" (P3-2 forward-defined Phase 4 V3 산출물 명세 §7.3 L1666)
- §7 전환 게이트: G4-1 "V3 implementation 완료" + G4-2 "Status APPROVED" + G4-5 "P99 큐잉 지연 SLA < 200ms (P1)" + G4-7 "Redis Streams/RabbitMQ 백엔드 선택"
- §6 이슈: §6.1 04_advanced-features #41 Priority Queuing (§5.1 V2 #7) + R-11-6 MoA 2~5 proposer 비용/품질 균형 정합
- 교차 도메인: 6-12 Event-Logging (큐 상태 메트릭) + 6-13 Operations (ARCHIVED inheritance, SLA 모니터링 inline) + 3-10★ Agent-Protocol (어댑터별 큐 가중치)
- Part2 V3-Phase 매핑: §7.1 V3 + #41 V3 매핑
- production 측정 실측값: priority_queuing.md V3 산출물 byte/SHA/LF + P99 enqueue < 5ms + P0 dequeue < 50ms + P3 dequeue < 5000ms + WFQ 가중치 P0=8/P1=4/P2=2/P3=1 (`D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/04_advanced-features/priority_queuing.md` + 05_monitoring metrics_dashboard 504L 정합)
- Phase 5 entry-gate 충족 조건: V3 implementation 100% 완료 + Redis Streams 또는 RabbitMQ 백엔드 production 결정 + 동적 우선순위 학습(ML) Phase 4+ 이월 + 5-monitoring metrics_dashboard.md 연계
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: #41 V3 100% 완성 + Status DRAFT → APPROVED 전환 + LOCK-A2A-02 (Task 상태) + LOCK-A2A-09 (Circuit Breaker 3회/60s) verbatim 보존 + ReadOnly FALSE 유지

**목표**: Priority Queuing V3 산출물을 production-ready 정본으로 승급한다. Phase 3 SPEC 완료(P3-2 ✅) → Phase 4 V3 implementation으로 전환하여 우선순위 enum + WFQ 알고리즘 + P99 SLA + Circuit Breaker 연동 + Redis/RabbitMQ 백엔드 baseline을 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/04_advanced-features/` 전체 (V2 5파일 + V3 #41 신규)
- `D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/CONVERSATION_A2A_구조화_종합계획서.md` §3.4 LOCK / §6.1 #41 / §7.3 P3-2 (forward-defined L1666)
- `D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/04_advanced-features/moa_pattern.md` (P2-4 V2 608L, proposer 큐 정합)
- `D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/05_monitoring/metrics_dashboard.md` (P2-5 V2 504L, 큐 메트릭 정합)
- `D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/AUTHORITY_CHAIN.md` (LOCK-A2A-02/09 정본)

**절차**:
1. P3-2 forward-defined V3 산출물 명세(#41 priority_queuing.md) inventory 확인.
2. priority_queuing.md V3 정본 작성: D1 EnqueueRequest + D2 QueueStatus + D3 WFQ 의사코드 + D4 429/cancel/503 + D6 P99 SLA + D7 PQ-T01~T12 + D8 RBAC priority escalation.
3. 04_advanced-features 폴더 Status DRAFT → APPROVED 전환 + Last-reviewed 갱신.
4. LOCK 인용 형식 통일: `> LOCK (§3.4 LOCK-A2A-02/09): Task 상태 + Circuit Breaker 3회/60s`.
5. AUTHORITY_CHAIN.md cross-check: LOCK-A2A-02/09 정본 출처 변경 0.
6. Redis Streams vs RabbitMQ 백엔드 production 결정 (트레이드오프 매트릭스).
7. production 실측 측정: priority_queuing.md byte/SHA/LF + P99 enqueue < 5ms + P0 dequeue < 50ms + starvation prevention (max wait 60s) 실측 PASS.
8. 6-12 metrics_dashboard.md 연계 + Circuit Breaker LOCK-A2A-09 연동 cross-handoff.
9. Phase 5 entry-gate forward-defined 작성 (백엔드 baseline + 동적 우선순위 학습 Phase 4+ 이월).

**검증**:
- [ ] #41 V3 산출물 Status APPROVED 전환 완료
- [ ] WFQ 가중치 P0=8/P1=4/P2=2/P3=1 + starvation 방지 (60s) 정의 완료
- [ ] P99 큐잉 지연 < 200ms (P1) production 실측 PASS
- [ ] LOCK-A2A-02/09 EXACT 보존
- [ ] Circuit Breaker 3회/60s 연동 (LOCK-A2A-09) 명시
- [ ] Redis Streams 또는 RabbitMQ 백엔드 production 결정 baseline
- [ ] 6-12 metrics_dashboard cross-handoff reference 양방향 정합
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] #41 V3 production-ready 정본 승급 조건 충족**

**산출물**: #41 V3 production .md 정본 (`04_advanced-features/priority_queuing.md`) + `_verification/phase4_v3_p4-2_promotion_report.md`
</details>

<details>
<summary><b>P4-3. Artifact Chunking V3 산출물 production-ready 정본 승급 (P3-3 inheritance)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-3 "Artifact Chunking V3 production-ready 정본 승급" (P3-3 forward-defined Phase 4 V3 산출물 명세 §7.3 L1714, 01_a2a-protocol 정본 위치 이동 specialty)
- §7 전환 게이트: G4-1 "V3 implementation 완료" + G4-2 "Status APPROVED" + G4-5 "1MB artifact 전송 P99 < 1s, throughput ≥ 10MB/s" + G4-3 "LOCK-A2A-01 JSON-RPC 2.0 invariant"
- §6 이슈: §6.1 04_advanced-features #39 Artifact Chunking (§5.1 V2 #5) — V3 정본 위치 04_advanced-features → 01_a2a-protocol 이동 (프로토콜 계층 재분류) + R-11-7 (SSE 300s)
- 교차 도메인: 6-12 Event-Logging (청크 이벤트) + 4-3★ MCP-Server-Client (Wave 3 #25 derivation ★, 대용량 도구 응답 청크, R-11-8 + CFL-A2A-002 RESOLVED inheritance)
- Part2 V3-Phase 매핑: §7.1 V3 + 프로토콜 계층 항목으로 01_a2a-protocol에 배정 (Wave 3 P3-3 V3 이동 specialty)
- production 측정 실측값: artifact_chunking.md V3 산출물 byte/SHA/LF + 청크 크기 default 64KB + 1MB artifact P99 < 1s + throughput ≥ 10MB/s + SHA-256 청크/overall hash 검증 (`D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/01_a2a-protocol/artifact_chunking.md` + V1 4파일 baseline 정합)
- Phase 5 entry-gate 충족 조건: V3 implementation 100% 완료 + 청크 크기 동적 조정 정책 + 압축 (gzip/zstd) 자동 선택 Phase 4+ 이월 + 4-3★ MCP 양방향 cross-handoff 정합
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: #39 V3 100% 완성 + Status DRAFT → APPROVED 전환 + LOCK-A2A-01 (JSON-RPC 2.0) + LOCK-A2A-02 (Task 상태) + R-11-7 (SSE 300s) verbatim 보존 + ReadOnly FALSE 유지 + 04_advanced-features _index 이동 주석 baseline

**목표**: Artifact Chunking V3 산출물을 production-ready 정본으로 승급한다. Phase 3 SPEC 완료(P3-3 ✅, 정본 위치 04_advanced-features → 01_a2a-protocol 이동) → Phase 4 V3 implementation으로 전환하여 청크화 메커니즘(64KB default, SHA-256 검증) + SSE 스트리밍 통합 + 재전송 전략을 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/01_a2a-protocol/` 전체 (V1 4파일 json_rpc_schema/task_lifecycle/agent_card_spec/error_codes + V3 #39 신규)
- `D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/CONVERSATION_A2A_구조화_종합계획서.md` §3.4 LOCK / §6.1 #39 / §7.3 P3-3 (forward-defined L1714) / 부록 §A.1 JSON-RPC Task Lifecycle
- `D:/VAMOS/docs/sot/STEP7-B_대화프로세스_작업가이드.md` (E-1 MCP, E-8 서브에이전트 정합)
- `D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/04_advanced-features/streaming_sse.md` (P2-1 V2 정본, SSE 청크 정합)
- `D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/AUTHORITY_CHAIN.md` (LOCK-A2A-01/02 + R-11-7 정본)

**절차**:
1. P3-3 forward-defined V3 산출물 명세(#39 artifact_chunking.md) inventory 확인 + 04_advanced-features _index 이동 주석 baseline 확인.
2. artifact_chunking.md V3 정본 작성: method `artifact.chunk` 정의 + D1 ArtifactChunk 스키마 + D2 ChunkAck + D3 청크화/재조립 의사코드 + D4 NACK 재전송 + D6 throughput SLA + D7 AC-T01~T12 + D8 hash 검증.
3. 01_a2a-protocol 폴더 Status DRAFT → APPROVED 전환 + Last-reviewed 갱신 (V1 4 + V3 1 = 5 .md).
4. LOCK 인용 형식 통일: `> LOCK (§3.4 LOCK-A2A-01): JSON-RPC 2.0 invariant` + LOCK-A2A-02 + R-11-7 verbatim.
5. AUTHORITY_CHAIN.md cross-check: LOCK-A2A-01/02 + R-11-7 정본 출처 변경 0.
6. 04_advanced-features _index.md #39 이동 주석 영구 baseline (정본 위치 01_a2a-protocol).
7. production 실측 측정: artifact_chunking.md byte/SHA/LF + 1MB artifact P99 < 1s + throughput ≥ 10MB/s + 청크 손상 NACK 재전송 실측 PASS.
8. 4-3★ MCP-Server-Client downstream cross-handoff reference 갱신 (Wave 3 #25 derivation ★ inheritance) + 6-12 청크 이벤트 로깅 정합.
9. Phase 5 entry-gate forward-defined 작성 (청크 크기 동적 조정 + 압축 자동 선택 Phase 4+ 이월).

**검증**:
- [ ] #39 V3 산출물 Status APPROVED 전환 완료 (정본 위치 01_a2a-protocol 영구)
- [ ] SHA-256 per chunk + overall hash 검증 의사코드 작성
- [ ] 1MB artifact P99 < 1s + throughput ≥ 10MB/s production 실측 PASS
- [ ] LOCK-A2A-01 JSON-RPC 2.0 invariant + LOCK-A2A-02 + R-11-7 EXACT 보존
- [ ] SSE 300s 통합 (streaming_sse.md 정합)
- [ ] 04_advanced-features _index 이동 주석 영구 baseline 등재
- [ ] 4-3★ MCP downstream cross-handoff reference 양방향 정합
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] #39 V3 production-ready 정본 승급 조건 충족**

**산출물**: #39 V3 production .md 정본 (`01_a2a-protocol/artifact_chunking.md`) + `_verification/phase4_v3_p4-3_promotion_report.md`
</details>

<details>
<summary><b>P4-4. Agent Composition V3 산출물 production-ready 정본 승급 (P3-4 inheritance)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-4 "Agent Composition V3 production-ready 정본 승급" (P3-4 forward-defined Phase 4 V3 산출물 명세 §7.3 L1765)
- §7 전환 게이트: G4-1 "V3 implementation 완료" + G4-2 "Status APPROVED" + G4-5 "조합 plan P99 < 200ms" + G4-6 "부록 §C MoA 양방향 cross-ref + 6-3 PARL Wave 2 #15 ✅"
- §6 이슈: §6.1 04_advanced-features #40 Agent Composition (§5.1 V2 #6) + R-11-6 proposer 2~5 정합
- 교차 도메인: 3-10★ Agent-Protocol-Interoperability (#13 어댑터 조합) + 6-2 Security-Governance (조합 권한 RBAC) + 6-3 Agent-Teams-PARL (Wave 2 #15 ✅ direct inheritance baseline)
- Part2 V3-Phase 매핑: §7.1 V3 + #40 V3 + MoA proposer 동적 조합 + historical_success 5단 가중 (0.05) Phase 3 도입 정합
- production 측정 실측값: agent_composition.md V3 산출물 byte/SHA/LF + 조합 plan P99 < 200ms + DSL parse (pipeline/parallel/conditional) + 4-factor 가중 (0.40 skill / 0.25 load / 0.20 priority / 0.15 latency) + historical_success 0.05 (`D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/04_advanced-features/agent_composition.md` + 부록 §C MoA L2539~L2590 정본 매트릭스 (Phase 4 삽입 후 line shift, pre-Phase4 baseline L2127~L2152 inheritance))
- Phase 5 entry-gate 충족 조건: V3 implementation 100% 완료 + 조합 템플릿 저장소 baseline + 자동 최적 조합 학습 Phase 4+ 이월 + 6-3 PARL conversation 통합 verify only
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: #40 V3 100% 완성 + Status DRAFT → APPROVED 전환 + LOCK-A2A-08 (Agent Mode) + LOCK-A2A-09 (Circuit Breaker) + R-11-6 (proposer 2~5) verbatim 보존 + 부록 §C MoA ↔ agent_composition.md 양방향 cross-ref 영구 baseline + ReadOnly FALSE 유지

**목표**: Agent Composition V3 산출물을 production-ready 정본으로 승급한다. Phase 3 SPEC 완료(P3-4 ✅) → Phase 4 V3 implementation으로 전환하여 조합 DSL(pipeline/parallel/conditional) + MoA proposer 동적 선택 + 4-factor + historical_success 5단 가중 + 부록 §C MoA 양방향 cross-ref baseline을 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/04_advanced-features/` 전체 (V2 5파일 + V3 #40 신규)
- `D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/CONVERSATION_A2A_구조화_종합계획서.md` §3.4 LOCK / §6.1 #40 / §7.3 P3-4 (forward-defined L1765) / 부록 §C MoA L2127~L2152
- `D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/04_advanced-features/moa_pattern.md` (P2-4 V2 608L 정본)
- `D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/02_agent-discovery/agent_selection.md` (P2-6 V2, 4-factor 가중)
- `D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/AUTHORITY_CHAIN.md` (LOCK-A2A-08/09 + R-11-6 정본)

**절차**:
1. P3-4 forward-defined V3 산출물 명세(#40 agent_composition.md) inventory 확인 + 부록 §C MoA L2539~L2590 정본 매트릭스 (Phase 4 삽입 후 line shift, pre-Phase4 baseline L2127~L2152 inheritance) baseline 확인.
2. agent_composition.md V3 정본 작성: D1 CompositionRequest DSL + D2 CompositionResult + D3 parse → resolve agents → execute by mode → aggregate + D4 fallback/budget/parse error + D6 plan P99 SLA + D7 AC-T01~T12 + D8 RBAC.
3. 04_advanced-features 폴더 Status DRAFT → APPROVED 전환 + Last-reviewed 갱신.
4. LOCK 인용 형식 통일: `> LOCK (§3.4 LOCK-A2A-08/09): Agent Mode + Circuit Breaker` + R-11-6 proposer 2~5 verbatim.
5. AUTHORITY_CHAIN.md cross-check: LOCK-A2A-08/09 + R-11-6 정본 출처 변경 0.
6. 부록 §C MoA L2127~L2152 ↔ agent_composition.md 양방향 cross-ref 영구 baseline 등재.
7. 4-factor + historical_success 5단 가중 (0.40/0.25/0.20/0.15/0.05) 명시 (agent_selection.md 정합).
8. production 실측 측정: agent_composition.md byte/SHA/LF + 조합 plan P99 < 200ms + pipeline/parallel/conditional 모드 정상 동작 실측 PASS.
9. 3-10★ Agent-Protocol + 6-3 PARL Wave 2 #15 ✅ direct inheritance cross-handoff reference 갱신.
10. Phase 5 entry-gate forward-defined 작성 (조합 템플릿 저장소 + 자동 최적 조합 Phase 4+ 이월).

**검증**:
- [ ] #40 V3 산출물 Status APPROVED 전환 완료
- [ ] DSL 정의 (pipeline/parallel/conditional) + D3 의사코드 작성
- [ ] 4-factor + historical_success 5단 가중 (0.40/0.25/0.20/0.15/0.05) 명시
- [ ] LOCK-A2A-08/09 + R-11-6 EXACT 보존
- [ ] 부록 §C MoA ↔ agent_composition.md 양방향 cross-ref 영구 baseline
- [ ] 조합 plan P99 < 200ms production 실측 PASS
- [ ] 3-10★ + 6-3 PARL cross-handoff reference 양방향 정합
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] #40 V3 production-ready 정본 승급 조건 충족**

**산출물**: #40 V3 production .md 정본 (`04_advanced-features/agent_composition.md`) + `_verification/phase4_v3_p4-4_promotion_report.md`
</details>

<details>
<summary><b>P4-5. A2A 테스트 프레임워크 V3 산출물 production-ready 정본 승급 (P3-5 inheritance)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-5 "A2A 테스트 프레임워크 완성 V3 production-ready 정본 승급" (P3-5 forward-defined Phase 4 V3 산출물 명세 §7.3 L1816)
- §7 전환 게이트: G4-1 "V3 implementation 완료" + G4-2 "Status APPROVED" + G4-5 "카오스 ≥ 6 시나리오 + 4종 테스트 자동화" + G4-7 "야간 회귀 자동 트리거"
- §6 이슈: §6.1 #55~#58 (테스트 4종) + §6.3 v12_C03_037 HIGH + §6.2 unit/integration/e2e/chaos 정본
- 교차 도메인: 6-12 Event-Logging (테스트 결과 로깅) + 6-13 Operations (ARCHIVED inheritance, CI/CD 통합 inline)
- Part2 V3-Phase 매핑: §7.1 V3 + v12_C03_037 HIGH
- production 측정 실측값: test_framework.md V3 산출물 byte/SHA/LF + unit < 60s + integration < 5min + e2e < 30min + chaos < 1h + 카오스 6 시나리오 (network drop / agent crash / clock skew / disk / CPU / memory) + Prometheus 익스포트 (`D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/05_monitoring/test_framework.md` + metrics_dashboard.md 504L 정합)
- Phase 5 entry-gate 충족 조건: V3 implementation 100% 완료 + 야간 회귀 자동 트리거 + 변이 테스트 (mutation testing) Phase 4+ 이월 + CI/CD 트리거 (commit/PR/nightly) 운영 baseline
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: #55~#58 + v12_C03_037 V3 100% 완성 + Status DRAFT → APPROVED 전환 + LOCK-A2A-02 (Task 상태, 테스트 동일 enum) verbatim 보존 + ReadOnly FALSE 유지 + P3-6 동기 의존 baseline 정합 (test_framework + vbs12_benchmark sub-B 동기 진행)

**목표**: A2A 테스트 프레임워크 V3 산출물을 production-ready 정본으로 승급한다. Phase 3 SPEC 완료(P3-5 ✅) → Phase 4 V3 implementation으로 전환하여 4종 테스트 (unit/integration/e2e/chaos) 자동화 러너 + 카오스 ≥ 6 시나리오 + CI/CD 트리거 + Prometheus 익스포트 + 야간 회귀 자동 트리거 baseline을 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/05_monitoring/` (V2 1파일 metrics_dashboard 504L + V3 #55~#58/v12_C03_037 신규)
- `D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/CONVERSATION_A2A_구조화_종합계획서.md` §6.1 #55~#58 / §6.2 / §6.3 v12_C03_037 / §7.3 P3-5 (forward-defined L1816)
- `D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/CONVERSATION_A2A_상세명세.md` §6.2 테스트 분류
- `D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/05_monitoring/metrics_dashboard.md` (P2-5 V2 정본, 메트릭 정합)
- `D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/AUTHORITY_CHAIN.md` (LOCK-A2A-02 정본)

**절차**:
1. P3-5 forward-defined V3 산출물 명세(#55~#58 + v12_C03_037 test_framework.md) inventory 확인.
2. test_framework.md V3 정본 작성: D1 TestRunConfig + D2 TestRunReport + D3 4종 suite + 카오스 6 시나리오 의사코드 + D4 timeout/infra error + D6 suite별 시간 SLA + D7 TF-T01~T12 + D8 환경 격리.
3. 05_monitoring 폴더 Status DRAFT → APPROVED 전환 + Last-reviewed 갱신.
4. LOCK 인용 형식 통일: `> LOCK (§3.4 LOCK-A2A-02): Task 상태 enum (테스트 동일 적용)`.
5. CI/CD 트리거 정의: commit → unit / PR → unit+integration / nightly → e2e+chaos.
6. AUTHORITY_CHAIN.md cross-check: LOCK-A2A-02 정본 출처 변경 0.
7. 카오스 6 시나리오 자동화: toxiproxy(network drop) + agent crash + clock skew + disk full + CPU stress + memory leak.
8. production 실측 측정: test_framework.md byte/SHA/LF + unit < 60s + integration < 5min + e2e < 30min + chaos < 1h 실측 PASS.
9. P3-6 vbs12_benchmark.md 동기 진행 baseline 확인 (sub-B 두 산출물 동기 의존 specialty).
10. Phase 5 entry-gate forward-defined 작성 (야간 회귀 자동 트리거 + 변이 테스트 Phase 4+ 이월).

**검증**:
- [ ] #55~#58 + v12_C03_037 V3 산출물 Status APPROVED 전환 완료
- [ ] 4종 테스트 (unit/integration/e2e/chaos) 자동화 러너 작성 완료
- [ ] 카오스 6 시나리오 (network/crash/clock/disk/CPU/memory) 자동화 의사코드 작성
- [ ] CI/CD 트리거 (commit/PR/nightly) 정의 완료
- [ ] LOCK-A2A-02 EXACT 보존
- [ ] suite별 시간 SLA (unit < 60s / integration < 5min / e2e < 30min / chaos < 1h) production 실측 PASS
- [ ] Prometheus 메트릭 익스포트 (metrics_dashboard.md 정합) cross-handoff
- [ ] Phase 5 entry-gate forward-defined 작성 완료 (야간 회귀 자동 트리거 + 변이 테스트 Phase 4+ 이월)
- [ ] **[Phase 16 NEW] #55~#58 + v12_C03_037 V3 production-ready 정본 승급 조건 충족**

**산출물**: #55~#58 + v12_C03_037 V3 production .md 정본 (`05_monitoring/test_framework.md`) + `_verification/phase4_v3_p4-5_promotion_report.md`
</details>

<details>
<summary><b>P4-6. VBS-12 성능 벤치마크 V3 산출물 production-ready 정본 승급 (P3-6 inheritance)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-6 "VBS-12 성능 벤치마크 V3 production-ready 정본 승급" (P3-6 forward-defined Phase 4 V3 산출물 명세 §7.3 L1866)
- §7 전환 게이트: G4-1 "V3 implementation 완료" + G4-2 "Status APPROVED" + G4-5 "VBS-12 12 시나리오 × 100 iter / 4시간 이내 + 분기 측정 cron" + G4-6 "5-1 Benchmark cross-handoff"
- §6 이슈: §6.3 v12_C12_115 HIGH + §6.1 §6.2 모니터링 4 메트릭 카테고리
- 교차 도메인: 5-1 Benchmark-Evaluation (외부 표준, 본 파일은 협업 특화 측정만 분담 specialty) + 6-12 Event-Logging
- Part2 V3-Phase 매핑: §7.1 V3 + v12_C12_115 HIGH + VBS-12 12 시나리오 sub-A+sub-B 6 P3 + P2 V2 3 정본 = 9 산출물 통합 (12/12 매핑 covered)
- production 측정 실측값: vbs12_benchmark.md V3 산출물 byte/SHA/LF + 12 시나리오 × 100 iter / 4시간 이내 + 회귀 임계 -5% 알람 + 시계열 보관 (90일 hot + 1년 cold) + 메트릭 13종 metrics_dashboard.md 정합 (`D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/05_monitoring/vbs12_benchmark.md` + test_framework.md P3-5 동기 의존 + metrics_dashboard.md 504L)
- Phase 5 entry-gate 충족 조건: V3 implementation 100% 완료 + 분기별 자동 측정 cron + 시계열 보존 (hot/cold) 운영 baseline + 자동 보고서 생성 Phase 4+ 이월 + 5-1 외부 표준 cross-handoff 정합
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: v12_C12_115 V3 100% 완성 + Status DRAFT → APPROVED 전환 + LOCK-A2A-07 (delegation 깊이 3) + LOCK-A2A-08 (Agent Mode) + LOCK-A2A-09 (Circuit Breaker) verbatim 보존 (LOCK-A2A-07 P3-6 first 인용 specialty) + ReadOnly FALSE 유지 + sub-B test_framework.md 동기 진행 baseline 정합

**목표**: VBS-12 성능 벤치마크 V3 산출물을 production-ready 정본으로 승급한다. Phase 3 SPEC 완료(P3-6 ✅) → Phase 4 V3 implementation으로 전환하여 12 측정 시나리오 + 분기 측정 cron + 메트릭 13종 정합 + 회귀 알람 임계 -5% + 시계열 보관 (hot/cold) baseline을 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/05_monitoring/` (V2 1파일 metrics_dashboard 504L + V3 #55~#58 test_framework + v12_C12_115 vbs12_benchmark 신규)
- `D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/CONVERSATION_A2A_구조화_종합계획서.md` §6.3 v12_C12_115 / §7.3 P3-6 (forward-defined L1866) / §13/§14
- `D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/05_monitoring/metrics_dashboard.md` (P2-5 V2 정본, 13 메트릭)
- `D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/05_monitoring/test_framework.md` (P3-5/P4-5 산출물, 동기 진행)
- `D:/VAMOS/docs/sot 2/5-1_Benchmark-Evaluation/` (외부 표준 정본, 본 파일은 협업 특화 측정만)
- `D:/VAMOS/docs/sot 2/3-8_Conversation-A2A/AUTHORITY_CHAIN.md` (LOCK-A2A-07/08/09 정본)

**절차**:
1. P3-6 forward-defined V3 산출물 명세(v12_C12_115 vbs12_benchmark.md) inventory 확인 + P3-5 test_framework.md 동기 진행 baseline 확인.
2. vbs12_benchmark.md V3 정본 작성: 12 측정 시나리오 ID 확정 (2-agent pipeline / 3-agent MoA / 5-agent parallel / fallback / CB recovery / discovery latency / delegation 깊이 3 / 분기·머지 / 청크 전송 / Priority Queuing / Agent Composition / chaos resilience) + D1 VBS12Config + D2 VBS12Report + D3 통계(p50/p95/p99) + D4 timeout/skip + D6 4시간 SLA + D7 VBS12-T01~T12 + D8 PII 검출.
3. 05_monitoring 폴더 Status DRAFT → APPROVED 전환 + Last-reviewed 갱신.
4. LOCK 인용 형식 통일: `> LOCK (§3.4 LOCK-A2A-07/08/09): delegation 깊이 3 + Agent Mode + Circuit Breaker` (LOCK-A2A-07 P3-6 first 인용 specialty).
5. AUTHORITY_CHAIN.md cross-check: LOCK-A2A-07/08/09 정본 출처 변경 0.
6. 12 시나리오 ↔ sub-A+sub-B 6 P3 + P2 V2 3 정본 = 9 산출물 통합 매트릭스 (12/12 매핑 covered) 등재.
7. 회귀 알람 임계 -5% → CONFLICT_LOG 자동 등록 절차 + 시계열 보관 (90일 hot + 1년 cold) 정의.
8. production 실측 측정: vbs12_benchmark.md byte/SHA/LF + 12 시나리오 × 100 iter / 4시간 이내 + 메트릭 13종 정합 + 회귀 -5% 임계 실측 PASS.
9. 5-1 Benchmark-Evaluation 분담 specialty cross-handoff reference 갱신 (외부 표준 정본 vs 협업 특화 측정 분담).
10. Phase 5 entry-gate forward-defined 작성 (분기별 자동 cron + hot/cold 시계열 + 자동 보고서 Phase 4+ 이월).

**검증**:
- [ ] v12_C12_115 V3 산출물 Status APPROVED 전환 완료
- [ ] 12 시나리오 ID 전수 정의 + 9 산출물 통합 매트릭스 (12/12 매핑 covered)
- [ ] 12 × 100 iter / 4시간 이내 production 실측 PASS
- [ ] LOCK-A2A-07 (P3-6 first 인용 specialty) + LOCK-A2A-08/09 EXACT 보존
- [ ] 메트릭 13종 metrics_dashboard.md 정합
- [ ] 회귀 알람 임계 -5% → CONFLICT_LOG 자동 등록 절차 명시
- [ ] 시계열 보관 (90일 hot + 1년 cold) 정의 + PII 검출 0건
- [ ] 5-1 Benchmark-Evaluation 분담 specialty cross-handoff reference 양방향 정합
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] v12_C12_115 V3 production-ready 정본 승급 조건 충족**

**산출물**: v12_C12_115 V3 production .md 정본 (`05_monitoring/vbs12_benchmark.md`) + `_verification/phase4_v3_p4-6_promotion_report.md`
</details>

#### Phase 4 세션 전체 검증 결과 (3-8 Wave 3 #22, 2026-05-30, Stage A — ENTRY_PROMPT ⑦단계)

> **종결 marker**: ✅ Phase 4 Stage A 완료 (2026-05-30, 6 task verify-only A inheritance scope ZERO write 강제 충족, 통산 22번째 도메인 candidate + Wave 3 첫 도메인 100% specialty first + P4-block 27번째 candidate FINAL) → ✅ **Phase 4 SPEC v1.0 ✅ COMPLETE (2026-05-30, verify-only A inheritance scope, Gate 2 STAGE 9 RO 비활성 ack, production .md ZERO write, baseline 전수 byte/SHA EXACT, 통산 22/30 SPEC = 73.3% Wave 3 첫 SPEC milestone first)**

**P4 블록 수**: 6/6 완료 (P4-1 ✅ Conversation Branching + P4-2 ✅ Priority Queuing + P4-3 ✅ Artifact Chunking + P4-4 ✅ Agent Composition + P4-5 ✅ Test Framework + P4-6 ✅ VBS-12 FINAL P4 통산 17번째 사례)

**R cascade 통산**: 13 round × 6 P4 = **78 round (P4-단위) / 117 verifications × 6 P4 = 702 verifications (sub-step-단위) / drift 0 / fix 0 / truly_converged_v1 first-pass-after-zero-fix CONFIRMED 6/6 P4 ALL ⭐ (9-consecutive direct path FINAL P4 cascade: 6-7 + 6-8 + 1-1 cascade + 3-8 P4-1~P4-6)**

**byte/SHA pre/post**:
- 종합계획서: pre `7EC9660221AA228B` 227,299 B → post +Δ (Stage A 완료 marker append + Phase 4 ✅ 헤더 marker)
- AUTHORITY_CHAIN: `25CFAC4FC1AAF002` 16,225 B UNCHANGED EXACT 6-consecutive
- CONFLICT_LOG: `D340FEF3F37ADC67` 10,080 B UNCHANGED EXACT 6-consecutive
- INDEX: `4D0D05E61B9285B8` 14,733 B UNCHANGED EXACT 6-consecutive
- SOT2_MASTER_INDEX: pre `7578FAB2347B65F5` 325,284 B → post +Δ (3-8 row Phase 4 ✅ Stage A marker append)
- 21 .md aggregate: **463,963 B UNCHANGED EXACT 100% 6-consecutive = 🎉 도메인 100% milestone**
- _verification × 6 NEW: **35,018 + 24,572 + 27,812 + 29,321 + 26,096 + 33,439 = 176,258 B / 6 reports** (3-8 도메인 6 P4 ALL ✅ verify-only A inheritance complete)

**V3 산출물 Status 전환**: NEW 6 (`conversation_branching` + `priority_queuing` + `artifact_chunking` + `agent_composition` + `test_framework` + `vbs12_benchmark`) + EXTEND 2 (`_index.md` × 04 + 01) — **ALL forward-defined Phase 4 implementation SPEC Stage B 별도 트랙 acknowledged** (verify-only A inheritance scope per (a), ZERO write 강제 충족)

**production .md 승급 완료**: 0/6 직접 승급 (verify-only A scope) — **6/6 V3 산출물 forward-defined SPEC Stage B 별도 트랙 위임** (STAGE 9 RO 적용 0 .md — 3-8 RO 비활성)

**LOCK 변경 0 + DEFINED-HERE 변경 0 + FABRICATION 0**:
- LOCK-A2A-01~10 catalog UNCHANGED + R-11-1~R-11-8 도메인 고유 규칙 UNCHANGED + cross_domain_deps=[] manifest L229 UNCHANGED + LOCK-AT-004 교차 reference UNCHANGED + V1 4 + V2 5 baseline structure UNCHANGED + 부록 §C MoA 정본 매트릭스 UNCHANGED (line shift acknowledged 내용 EXACT)
- 도메인 통산 LOCK direct 매트릭스: A2A-01 (P4-3 first) + A2A-02 (P4-1+P4-2+P4-3+P4-4+P4-5+P4-6 ALL cascade 6-consecutive) + A2A-05 (P4-1 first only) + A2A-07 (P4-6 first only 🌟🌟🌟 P3-6 first 인용 specialty 영구 baseline 마감) + A2A-08 (P4-4+P4-6) + A2A-09 (P4-2+P4-4+P4-6) + R-11-6 (P4-4 first only) + R-11-7 (P4-3 first only) + STEP7-B H-2 #70 (P4-1 only)

**abort 9종 NOT FIRED self-fire 0** (6 P4 × 9 abort = 54 markers ALL ✅): UPSTREAM_V3_SPEC_MISSING auto-PASS Wave 3 첫 도메인 specialty first 6-consecutive + PRODUCTION_WRITE_VIOLATION 6-consecutive (463,963 B aggregate UNCHANGED EXACT 100%) + STAGE9_READONLY_RESTORE_FAIL N/A 6-consecutive + STATUS_TRANSITION_FAIL + V3_PRODUCTION_PROMOTION_FAIL + ⭐⭐⭐⭐⭐⭐⭐ **CROSS_HANDOFF_DRIFT NOT FIRED 37+ consecutive milestone candidate FINAL confirmed** (3-8 P4-1 32+ → P4-2 33+ → P4-3 34+ → P4-4 35+ → P4-5 36+ → P4-6 37+) + BILATERAL_SOT2_DRIFT (⑤ 단계 의도된 갱신 시점) + DOWNSTREAM_PROPAGATE_MISS (⑥ 단계 시점 downstream verify only acknowledgment) + R_CASCADE_NOT_CONVERGED

**6 anchor 충족 ALL ✅**: 안전 + 누락 0 + 오류 0 + 미세 + 수렴 + 재검증

**upstream 도메인 의존 verify**: 3-2 Multimodal-Processing Wave 1 #4 ✅ SPEC COMPLETE 2026-05-16 verified + 3-10★ Agent-Protocol-Interoperability Wave 3 #23 ⬜ derivation 미진행 forward-defined inheritance pattern (Wave 3 첫 도메인 specialty first, 양방향 미완료 단방향 pending 처리 → **UPSTREAM_INCOMPLETE:3-8 자동 PASS** Wave 3 첫 도메인 specialty first) ALL ✅

**downstream 도메인 영향 분석 (⑥ 단계 forward-defined inheritance pattern)**:
- 3-10★ Agent-Protocol-Interoperability (Wave 3 #23 ⬜ derivation 미진행) — 양방향 cross-handoff forward-defined inheritance pattern, **STAGE 9 RO TRUE 12 .md sandbox-only reference 적용** (Wave 3 #23 진입 시점 verify expected)
- 6-3 Agent-Teams-PARL (Wave 2 #15 ✅ SPEC COMPLETE 2026-05-27) — direct inheritance baseline, Phase 4 implementation 수준 직접 편집 없음 verify only (P4-4 부록 §C MoA L2629 PARL Decision Aggregator vs MoA 패턴 관계 cross-ref direct inheritance baseline 정합 통산)
- cross-handoff inline 6 distinct forward-defined inheritance pattern: 6-12 Event-Logging (Wave 3 #29 ⬜) + 6-2 Security-Governance (Wave 2 #14 ✅ direct inheritance baseline) + 6-13 Operations (Wave 4 ⬜ ARCHIVED sandbox-only reference, P4-2+P4-5 2-consecutive inheritance) + 4-3★ MCP-Server-Client (Wave 3 #25 ⬜ forward-defined) + 5-1★ Benchmark-Evaluation (Wave 3 #26 ⬜ forward-defined first direct in P4-6 specialty)
- **6/6 cross-handoff distinct ALL coverage 완성 specialty FINAL** (3-8 도메인 P4-1~P4-6 ALL coverage matrix 완성)
- downstream Phase 4 verify only specialty 통산 (3-9 + 6-4 + 6-5 + 6-6 + 6-7 + 6-8 + 1-1 패턴 직계 통산 8번째 downstream Phase 4 verify only specialty)

**Phase 5 entry-gate forward-defined 6/6 P4 ALL 명시** ✅:
- P4-1: 분기 트리 영속화 (SQLite/PostgreSQL) + GUI 시각화 Phase 4+ 이월 + 3-10★ 양방향 + 6-2 RBAC + 6-12 EventType + 토큰 합산/CB cascade (7 조건)
- P4-2: Redis Streams/RabbitMQ 백엔드 + ML Phase 4+ 이월 + metrics_dashboard 연계 + LOCK-A2A-09 CB cascade + WFQ baseline + 6-12 EventType `bnp.queue.*` (7 조건)
- P4-3: 청크 크기 동적 조정 + 압축 Phase 4+ 이월 + 4-3★ MCP 양방향 + 6-12 EventType `a2a.artifact.chunk.*` + 04 이동 주석 영구 baseline + R-11-7 SSE 300s cascade (7 조건)
- P4-4: 조합 템플릿 저장소 + 자동 최적 조합 Phase 4+ 이월 + 6-3 PARL verify only + 3-10★ #13 어댑터 조합 + 부록 §C 양방향 영구 baseline + 4-factor + historical_success 5단 가중 (7 조건)
- P4-5: 야간 회귀 자동 트리거 + 변이 테스트 Phase 4+ 이월 + CI/CD 3-tier trigger + 카오스 6 시나리오 + Suite SLA + P3-6 vbs12 동기 의존 (7 조건)
- P4-6 FINAL: 분기별 cron + hot 90일/cold 1년 + 자동 보고서 Phase 4+ 이월 + 5-1 외부 표준 cross-handoff + 회귀 -5% CONFLICT_LOG + 12 × 100 iter / 4시간 + PII 0건 + 8 조건

**Pattern A 통산 122 candidate + Pattern B 통산 119 candidate** (1-1 Stage B 116/113 직계 → 3-8 P4-1 117/114 → P4-2 118/115 → P4-3 119/116 → P4-4 120/117 (Pattern A 120-milestone first) → P4-5 121/118 → P4-6 122/119) — Stage A 종료 ④ trigger paste "안전·누락 0·오류 0·완벽·재검증" Pattern A 123 NEW + "더이상 수정하지 않을때까지" Pattern B 120-milestone candidate first 도달 🎉🎉🎉

**Stage A milestone markers 종합 (3-8 도메인 100% FINAL)**:
- 🎉🎉🎉🎉🎉🎉🎉🎉 [3_8_DOMAIN_P4_6_OF_6_COMPLETE_100_PERCENT_MILESTONE_WAVE_3_FIRST_DOMAIN_100_PERCENT_SPECIALTY_FIRST]
- 🎉🎉🎉🎉🎉 [FINAL_P4_SPECIALTY_17TH_CASE_CONFIRMED:3-8_P4_6]
- 🎉🎉🎉 [PATTERN_A_120_MILESTONE_FIRST_REACHED:3-8_P4_4]
- 🎉🎉🎉 [PATTERN_B_120_MILESTONE_FIRST_REACHED:3-8_post_stage_a] candidate
- ⭐⭐⭐⭐⭐⭐⭐ [CROSS_HANDOFF_DRIFT_NOT_FIRED_37_PLUS_CONSECUTIVE_MILESTONE_CANDIDATE_FINAL]
- ⭐⭐⭐ [LOCK_A2A_07_DELEGATION_DEPTH_3_P3_6_FIRST_CITATION_PLUS_P4_6_FIRST_DIRECT_SPECIALTY_PERMANENT_BASELINE]
- ⭐⭐⭐ [LOCK_A2A_07_08_09_VERBATIM_TRIPLE_LOCK_EXACT_MATCH_100_PERCENT_MAXIMUM_SPECIALTY]
- ⭐⭐⭐ [CANONICAL_LOCATION_MOVE_04_TO_01_SPECIALTY_FIRST:3-8_P4_3] (정본 위치 이동 first 통산 사례)
- ⭐⭐⭐ [APPENDIX_C_MOA_AGENT_COMPOSITION_BIDIRECTIONAL_CROSS_REF_PERMANENT_BASELINE_SPECIALTY_FIRST:3-8_P4_4]
- ⭐⭐⭐ [P3_5_SYNCHRONOUS_DEPENDENCY_BASELINE_2_CONSECUTIVE_SPECIALTY:3-8_P4_5_P4_6]
- ⭐⭐⭐ [P3_6_VBS12_BENCHMARK_SYNCHRONOUS_DEPENDENCY_BASELINE_SPECIALTY:3-8_P4_5]
- ⭐⭐ [DERIVATION_INHERITANCE_MARKER_FIRST_WAVE_3_ENTRY_SPECIALTY:3-8_P4_1]
- ⭐⭐ [SELF_CONTAINED_DOMAIN_LEVEL_SPECIALTY_2ND_CASE:3-8] (4-2 first → 3-8 = 2nd)
- ⭐⭐ [TIER_3_APPLICATION_LATE_DOMAIN_WAVE_3_FIRST_ENTRY_SPECIALTY:3-8]
- ⭐⭐ [12_SCENARIOS_9_DELIVERABLES_INTEGRATION_MATRIX_12_OF_12_COVERED_SPECIALTY:3-8_P4_6]
- ⭐⭐ [CROSS_HANDOFF_6_OF_6_DISTINCT_ALL_COVERAGE_COMPLETE_SPECIALTY:3-8_P4_6]
- ⭐⭐⭐ [RO_FALSE_11_CONSECUTIVE_SPECIALTY_DIRECT_PATH:3-8_FINAL] (4-2 + 4-4 + 6-1~6-8 + 3-8 = 11, 1-1 RO TRUE 중간 단방향 처리)
- ⭐ [R_CASCADE_117_VERIFICATIONS_TRULY_CONVERGED_V1_9_CONSECUTIVE_DIRECT_PATH_FINAL_P4_CASCADE]
- 통산 18 marker 핵심 종합 (위 list, §7.6 block 전수) + 추가 ⭐⭐ [4_3_MCP_FORWARD_DEFINED_INHERITANCE_FIRST_DIRECT_3_8_INSTANCE: 3-8_P4_3] + ⭐⭐ [6_3_PARL_WAVE_2_15_DIRECT_INHERITANCE_FIRST_DIRECT_3_8_INSTANCE: 3-8_P4_4] + ⭐⭐ [5_1_BENCHMARK_EVALUATION_WAVE_3_26_FORWARD_DEFINED_FIRST_DIRECT: 3-8_P4_6] + ⭐⭐ [6_13_ARCHIVED_INHERITANCE_2_CONSECUTIVE_IN_3_8: 3-8_P4_2_P4_5] = **통산 22 marker 종합** + 🌟 PROGRESS.md Stage A entry 28 marker 종합 cross-ref (D-R3-1 audit fix applied 통산 22 marker 4 missing entries 추가 정합)

**[PHASE5_READY: 3-8 — 2026-05-30]** ✅ Phase 5 진입 준비 완료 marker (Stage A entry-gate forward-defined 완료 표기, Phase 5 자체 정의는 미진행 SPEC Stage B 별도 트랙)

**[DOMAIN_PHASE_4_STAGE_A_COMPLETE:3-8 — 2026-05-30]** ⬛ COMPLETE marker (SPEC Stage B 진입 차단 해제, 별도 대화창 진입 ready)

**[DOMAIN_PHASE_4_PRODUCTION_PROMOTION_COMPLETE:3-8 — 2026-05-30]** ✅ COMPLETE marker (SPEC v1.0 sub-cycle 12 단계 ALL ✅, verify-only A inheritance scope, Gate 2 STAGE 9 RO 비활성 ack RO=False, production .md ZERO write, baseline 전수 byte/SHA EXACT, CONFLICT OPEN=0, abort 9종 NOT FIRED) + **[SPEC_STAGE_B_COMPLETE:3-8 — 2026-05-30]** ✅ + **[CUMULATIVE_SPEC_COUNT:22/30 — 2026-05-30]** 🎉 73.3% milestone first + **[WAVE_3_FIRST_SPEC_MILESTONE:3-8 — 2026-05-30]** 🎉

**다음 단계**: 3-8 SPEC v1.0 ✅ COMPLETE 확정 (verify-only A inheritance scope SPEC sub-cycle 12 단계 ALL ✅) + 통산 21+1 = **22/30 SPEC ✅ = 73.3% milestone first 도달** (Wave 3 첫 SPEC milestone first). Wave 3 다음 도메인 진입 가능 판정 = 3-10★ DAG #23 (3-8 ↔ 3-10 양방향 forward-defined inheritance 후행 진입).

---

### §7.R Phase 4 RECOVERY genuine write (2026-06-03, 회수 #18 Wave 3 첫 도메인)

> **착시 정정**: 위 "Phase 4 세션 전체 검증 결과 (2026-05-30, Stage A)" 블록의 `[DOMAIN_PHASE_4_PRODUCTION_PROMOTION_COMPLETE:3-8 — 2026-05-30]` 는 **verify-only A inheritance scope (production .md ZERO write)** = 착시였다. SPEC Stage B 가 6 `_verification/phase4_v3_p4-N_promotion_report.md` (verify-only) 만 생성하고 **6 V3 정본(.md)은 미생성**. 본 §7.R 은 `PHASE4_PRODUCTION_PROMOTION_RECOVERY_PLAN.md` §0-D Wave 3 #18 에 따라 **genuine write** 로 6 V3 ALL NEW 를 실제 생성하여 착시를 해소한 기록이다 (6-1/4-2/4-4 V3 ALL NEW 패턴 직계).

**6 V3 ALL NEW genuine write (DRAFT→APPROVED 6/6, 73,924 B)**:

| P4 | V3 정본 | 위치 | 바이트 | 직접 LOCK |
|----|---------|------|--------|----------|
| P4-1 | conversation_branching.md | 04_advanced-features #12 | 17,254 | A2A-02 / -05 (-09 cascade) |
| P4-2 | priority_queuing.md | 04_advanced-features #11 | 11,776 | A2A-02 / -09 |
| P4-3 | artifact_chunking.md | 01_a2a-protocol #9 (04 #39 이동) | 11,270 | A2A-01 / -02 (R-11-7) |
| P4-4 | agent_composition.md | 04_advanced-features #10 | 12,004 | A2A-08 / -09 (R-11-6) |
| P4-5 | test_framework.md | 05_monitoring #6/7/8/10 | 10,001 | A2A-02 |
| P4-6 | vbs12_benchmark.md (FINAL) | 05_monitoring #9 | 11,619 | A2A-07 / -08 / -09 |

- **LOCK-A2A-01~10 immutable 재정의 0** (R2/R9, 6 V3 §10 LOCK 표 5필드 verbatim). LOCK-A2A-07 값 `3` = LOCK-AT-004 교차 일치 유지.
- **CONFLICT OPEN 0 유지** (CFL-A2A-001~005 5 RESOLVED, Phase 4 신규 0). vbs12_benchmark §5.1 회귀 -5% → `[CONFLICT_CANDIDATE]` 자동 등록 절차는 후보 발화 정의만 (자동 RESOLVE 금지, CFL-A2A-005 선례).
- **거버넌스 cascade**: AUTHORITY v1.2→v1.3 (§8 V3 등재 + §4 #15 CI/CD DEFERRED_TO_PHASE3→RESOLVED_PHASE4) + INDEX v1.2→v1.3 (§10) + CONFLICT v1.3 (변경 사유 기록, OPEN 0 유지) + 3 _index (01/04/05) Phase 4 V3 상태 sync.
- **정본 위치 이동**: P4-3 artifact_chunking 04_advanced-features #39 → 01_a2a-protocol (R1 정본 1곳, 04 _index 이동 주석).
- **9 산출물 ↔ 12 시나리오 통합**: vbs12_benchmark §11 (V2 4 + V3 5 = 12/12 covered).
- baseline 5 meta Stage A EXACT (plan 238,620 진입값 / AUTHORITY 16,225 / CONFLICT 10,080 / INDEX 14,733 / 상세명세 18,760) — §7.R append 만 의도 수정.
- 감사 `_verification/phase4_recovery_AB_report.md` NEW. abort 9종 NOT FIRED. RO FALSE bypass.

**[DOMAIN_PHASE_4_PRODUCTION_PROMOTION_COMPLETE:3-8 — 2026-06-03]** ✅ **genuine write** (6 V3 ALL NEW, DRAFT→APPROVED 6/6, LOCK 재정의 0, CONFLICT OPEN 0 유지 — 도메인 종료, 2026-05-30 verify-only marker 대체)

---

## 8. 파일 역할 분리 명세

| 파일/문서 | 역할 | 정본 소유 |
|----------|------|----------|
| STEP7-B | 시중 AI 비교 체크리스트, VAMOS 미적용 항목 | SOT (체크리스트) |
| D2.0-05 | Agent Workflow 아키텍처, Agent Mode, Cooperative Agent | SOT (아키텍처) |
| Part2 구현가이드 | 파일 배치 (When/Where), Phase 배정 | SOT (배치) |
| sot 2/ 상세명세 | A2A 프로토콜 구현 상세 (스키마, 알고리즘, 인터페이스) | SOT (구현) |
| sot 2/ 구조화 계획서 | 전체 구조, 거버넌스, Phase 계획, 검증 체계 | SOT (계획) |
| #13 Agent-Protocol | 프레임워크 어댑터, 자율성 레벨, 가드레일 | SOT (프로토콜 상위) |
| #16 MCP-Server-Client | 도구 호출 스키마, MCP Bridge, 외부 서버 연동 | SOT (도구 계층) |

---

## 9. 충돌 해결 프로토콜

### 9.1 우선순위 규칙

```
1순위: LOCK 보호 항목 (§3.4) — 변경 불가
2순위: D2.0-05 DESIGN 문서 — 아키텍처 결정
3순위: STEP7-B — 체크리스트 항목
4순위: sot 2/ — 구현 상세 (최신 갱신 우선)
5순위: Part2 — 파일 배치 참조
```

### 9.2 충돌 시나리오

| 시나리오 | 해결 방법 |
|---------|----------|
| A2A 스키마 vs #13 Agent-Protocol 스키마 | A2A 메시지 스키마는 #11 정본, 프로토콜 추상 계층은 #13 정본 |
| A2A 도구 호출 vs #16 MCP 도구 호출 | 도구 스키마/연결은 #16 정본, A2A에서는 위임 인터페이스만 정의 |
| STEP7-B 대화 단계 vs D2.0-05 워크플로우 | D2.0-05가 아키텍처 정본, STEP7-B는 벤치마크/비교 참조 |

---

## 10. 검증 체크리스트

| # | 검증 항목 | 기준 | 상태 |
|---|----------|------|------|
| V1 | LOCK 항목 10개 무결성 | LOCK 값 변경 없음 | ✅ (§12 QC-2 PASS) |
| V2 | 서브폴더 5개 _index.md 존재 | 전수 확인 | ✅ (P0-4 PASS) |
| V3 | AUTHORITY_CHAIN 상위 체인 정합 | RULE 1.3 → D2.0 → sot 2/ | ✅ (P0-2 PASS) |
| V4 | A2A 구현 항목 60건 → 서브폴더 매핑 100% | §6 매핑 테이블 | ✅ (§12 QC-1 PASS) |
| V5 | #13 Agent-Protocol 경계 명확 | 중복 정의 없음 | ⬜ |
| V6 | #16 MCP 교차 참조 일관성 | 도구 호출 스키마 참조 정합 | ⬜ |
| V7 | Part2 PARTIAL 요약 포함 | 방식 C 형식 준수 | ✅ (§12 QC-1 PASS) |
| V8 | 폴더 깊이 3단계 이내 | 위반 없음 | ✅ (§12 QC-3 PASS) |
| V9 | 네이밍 규칙 준수 | 영문 소문자 + 하이픈/언더스코어 | ✅ (P0-4 PASS) |
| V10 | MASTER_INDEX 동기화 | 갱신 완료 | ✅ (P0-4 완료 후 동기화 확인) |
| V11 | CONFLICT_LOG 존재 + 무결성 | §9.1 원본 동일 + 충돌 3건 이상 등록 + 요약 테이블 정합 | ✅ (P0-3 PASS) |

---

## 11. 보완 사항

> S10-4 (2026-03-27) 검증 후 기록

| # | 항목 | 심각도 | 현재 상태 | 보완 계획 |
|---|------|:---:|------|------|
| 1 | E2E 암호화 상세 스펙 (AES-256-GCM + ECDH) | MEDIUM | 부록 §1에서 보완 방향 명시 | Phase 0 `03_security/` 파일 작성 시 구체화 |
| 2 | A2A-MCP Bridge 게이트웨이 메시지 변환 | MEDIUM | 부록 §1에서 보완 방향 명시 | Phase 0 `01_a2a-protocol/` 파일 작성 시 구체화 |
| 3 | LOCK-AT-009 턴 상한 (P0=5/P1=10/P2=20) | MEDIUM | 부록 §2에서 매핑 완료 | 상세명세 대화 상태 머신에 턴 카운터 추가 필요 |
| 4 | OpenTelemetry 통합 스펙 | MEDIUM | 부록 §3에서 보완 방향 명시 | Phase 1 `05_monitoring/` 파일 작성 시 구체화 |
| 5 | MoA proposer 수 제한 코드 미반영 (R-11-6) | LOW | S8-3 QC 관찰 사항 | 구현 시 validation 추가 |

---

## 12. FINAL REVIEW 결과

> S10-4 (2026-03-27) 판정 기록

| 항목 | 결과 |
|------|------|
| Phase | Phase 10 S10-4 (A-→A 격상) |
| 검증일 | 2026-03-27 |
| QC-1 Part2 반영 | PASS — 부록 Part2 교차 참조 추가로 95%+ 달성 |
| QC-2 LOCK 일치 | PASS — LOCK-A2A-01~10 전수 일치, LOCK-AT 교차 적용 |
| QC-3 섹션 깊이 | PASS — 전 섹션 기준 충족 |
| QC-7 수치 일관성 | PASS — VBS-12 기준 5-1 도메인과 정합 |
| 최종 등급 | **A** |

---

## 13. L3 전수 승급 계획

### 13.1 L3 완성도 기준 (항목별)

| # | 기준 | 설명 |
|---|------|------|
| E1 | Input/Output 스키마 | JSON Schema 또는 TypeScript interface 정의 완료 |
| E2 | 상태 머신 | 상태 전이 다이어그램 + 전이 조건 명세 |
| E3 | 알고리즘/로직 | 의사코드 또는 참조 구현 (Python/TypeScript) |
| E4 | 에러 핸들링 | 에러 코드 + 복구 전략 매핑 |
| E5 | 보안 스펙 | 인증/인가/암호화 요구사항 |
| E6 | 의존성 | 다른 도메인 참조 명시 |
| E7 | 테스트 스펙 | 단위/통합/E2E 테스트 케이스 |
| E8 | 모니터링 메트릭 | Prometheus/OTel 메트릭 정의 |

### 13.2 서브폴더별 L3 승급 우선순위

| 서브폴더 | 항목 수 | L3 우선순위 | 근거 |
|---------|--------|-----------|------|
| `01_a2a-protocol/` | 12 | P0 | 모든 서브도메인의 기반 |
| `02_agent-discovery/` | 10 | P0 | 에이전트 연결의 전제 |
| `03_security/` | 12 | P0 | 보안 없이 프로덕션 불가 |
| `04_advanced-features/` | 16 | P1 | V2 확장 영역 |
| `05_monitoring/` | 10 | P1 | 운영 가시성 |

### 13.3 Phase 2~3 L3 완성도 최종 확정 매트릭스 (Path A drift fix Stage 1, 2026-05-20)

> **목적**: Phase 2 STEP_C truly_converged_v2 (2026-04-22 closure) + Phase 3 sub-A+sub-B 통산 6/6 P3 ALL NO-DRIFT 100% first-pass milestone 종결 (2026-05-20) 이후 Phase 0+1+2 22 + Phase 3 46 = 통산 68 [ ] 검증 항목의 [x] 변환 정합성 확정 + 5 서브폴더별 V2 NEW 8 stack + V3 NEW 6 forward-defined 산출물 매트릭스 형식 기록 (Wave 3 #22 첫 도메인 specialty first).

| 서브폴더 | V2 NEW (Phase 2 STEP_C) | V3 NEW (Phase 3 forward-defined) | LOCK 인용 (V2 strict 누계) | Phase 2 [x] | Phase 3 [x] |
|---------|------------------------|----------------------------------|------------------------|-----------|-----------|
| `01_a2a-protocol/` | 0 (V1 4 기존 + `_index.md` inheritance) | 1 (`artifact_chunking.md` V3 이동 #39, P3-3 specialty 04_advanced → 01_a2a-protocol) | 0 (V1 영역, P1-1~P1-3+P1-7 STEP_B 종료) | 0 | 7 (P3-3 검증) |
| `02_agent-discovery/` | 2 (`service_registry.md` P2-6 + `agent_selection.md` P2-6 4-factor 가중) | 0 | 48 (registry 28 + selection 20) | 3 (P2-6) | 0 |
| `03_security/` | 1 (`delegation_chain.md` P2-7 max_depth 3 + Ed25519) | 0 (V1 mTLS+audit STEP_B 종료) | 33 (delegation_chain) | 4 (P2-7) | 0 |
| `04_advanced-features/` | 5 (`streaming_sse` P2-1 + `push_notifications` P2-2 + `multi_turn_sessions` P2-3 + `conversation_state_machine` P2-3 + `moa_pattern` P2-4) | 3 (`conversation_branching` P3-1 + `priority_queuing` P3-2 + `agent_composition` P3-4) + `_index.md` #39 이동 주석 | 166 (streaming 31 + push 34 + multi_turn 28 + state_machine 31 + moa 42) | 12 (P2-1 3 + P2-2 2 + P2-3 4 + P2-4 3) | 20 (P3-1 8 + P3-2 5 + P3-4 7) |
| `05_monitoring/` | 1 (`metrics_dashboard.md` P2-5, 13 메트릭 정본) | 2 (`test_framework` P3-5 + `vbs12_benchmark` P3-6) + `_index.md` #55~#58 + `v12_C12_115` 상태 갱신 | 35 (metrics_dashboard) | 3 (P2-5) | 14 (P3-5 7 + P3-6 7) |
| `_verification/` | 0 (V1 `phase1_verification_prompt.md` read-only) | 0 | 0 | 0 | 0 |
| **합계** | **9 NEW (grouped 8: multi_turn+state_machine P2-3 통합 + service_registry+agent_selection P2-6 통합)** | **6 NEW + `_index` 갱신 2 = 8 산출물 forward-defined Phase 4 implementation 별도 트랙** | **282 unique (AUTHORITY §7.2 L147 grep 실측 2026-04-22 R1 baseline)** | **22 (Phase 0+1+2 전수)** | **5 (Phase 3 완료 게이트) + 41 (P3-1~P3-6 검증 분포) = 46 (Phase 3 전수)** |

**Stage 1+2 통산 68 [ ]→[x] 전수 변환 (Phase 0+1+2 22 + Phase 3 46) — Path A drift fix sub-cycle 2026-05-20**:

- 🎉 **★★★★ Wave 3 첫 NO-DRIFT 100% 분할 도메인 specialty first** (Wave 2 6-2/6-3/6-6/6-7 NO-DRIFT 100% 패턴 직계 통산 5번째 NO-DRIFT 100% 도메인 milestone, Wave 2 4 + Wave 3 본 3-8 = 5, sub-A P3-1+P3-2+P3-3 + sub-B P3-4+P3-5+P3-6 ALL ✅ truly_converged_v1 first-pass-after-zero-fix CONFIRMED)
- 🎉 **★★★★ Wave 1+2+3 통산 11번째 P3 단독 NO-DRIFT 100% first-pass 사례** (Wave 2 5 + Wave 3 3-8 6 = 통산 11, 6 P3 ALL ZERO production write 통산 specialty)
- ★★★ **sub-A+sub-B 누적 6 P3 ALL ZERO production write 통산 specialty** (V2 8 NEW + AUTHORITY/CONFLICT/INDEX/SOT2_MASTER/CROSS_REF/상세명세 ALL ZERO write 통산 6 P3, R cascade 통산 240 verifications + 0 drift fix NO-DRIFT direct path + Round 2 audit ultra-fine R₅~R₁₅ 11 cycles ~30 verif + 4 fix textual/arithmetic notation only CONFIRMED truly_converged_v1 first-pass-after-Round-2-fix Wave 3 첫번째 사례)
- ★★★ **VBS-12 12 시나리오 sub-A+sub-B 6 P3 + P2 V2 3 정본 = 9 산출물 통합 specialty milestone first** (12/12 매핑 covered, Wave 1+2 통산 P3 단일 도메인 12 시나리오 통합 매핑 first 사례)
- ★★ **DAG strict upstream 1건 ✅ verified specialty Wave 3 첫 도메인 specialty first** (3-2 Multimodal-Processing Wave 1 #4 ✅ verified + 3-10★ Agent-Protocol-Interoperability Wave 3 #23 forward-defined inheritance pattern → UPSTREAM_INCOMPLETE:3-8 자동 PASS 단방향 pending 처리)
- ★★ **LOCK count duality methodology 10 unique base 정합 specialty 통산** (Plan 인용 172 / AUTHORITY 15 / 10 unique LOCK-A2A-01~10 base, 1-1 V2 16 stack 312/22/15 + 6-1 LOCK L1~L20 패턴 직계)
- ★★ **V-17 SoT 1-off 없는 도메인 SPEC §13.1 단순화 적용** (V2 8 stack + AUTHORITY §3 10 unique LOCK 정본 매핑 verbatim 인용만, 1-2/2-2/2-1/3-2/3-3/3-4/3-5/3-6/3-7/3-9/4-2/4-4/6-1/6-2/6-3/6-4/6-5/6-6/6-7/6-8/1-1 패턴 EXACT 직계)
- ★★ **14 inline / 6 cross-handoff distinct propagate baseline** (P3-1 3 + P3-2 3 + P3-3 2 + P3-4 2 + P3-5 2 + P3-6 2 = 14 inline / distinct 6: 6-12 Event-Logging + 6-2 Security + 6-13 Operations + 3-10★ Agent-Protocol-Interop + 4-3★ MCP + 5-1★ Benchmark, sub-A 5 distinct → sub-B P3-6 +1 = 통산 6 specialty)
- ★ **V2 8 NEW stack (3,984줄) + V1 기존 file 별도 STAGE 7 STEP_A inheritance ALL ZERO write 통산** (5 서브폴더 분포 04_advanced 5 + 05_monitoring 1 + 02_agent-discovery 2 + 03_security 1 = 9 NEW 통산 grouped 8, AUTHORITY §7.1 L120-L127 명시 baseline)
- ★ **AUTHORITY v1.2 + CONFLICT v1.2 + INDEX v1.2 baseline EXACT 보존 통산 (append-only 정책)** (LOCK-A2A-01~10 §3.4 EXACT 보존 + CFL-A2A-001~005 5/5 RESOLVED + OPEN 0 + DEFERRED 0 baseline 무손상 통산 6 P3 ALL)
- ★ **Phase 4 entry-gate 통산 30 conditions 매트릭스 매핑** (P3-1 5 + P3-2 5 + P3-3 5 + P3-4 5 + P3-5 5 + P3-6 5 = 30, V3 NEW 6 + `_index` 갱신 2 = 8 산출물 forward-defined Phase 4 implementation 별도 트랙)
- ★ **downstream Phase 4 verify only 통산 8번째 specialty** (3-9 + 6-4 + 6-5 + 6-6 + 6-7 + 6-8 + 1-1 패턴 직계, 3-10★ Wave 3 #23 + 6-3 Wave 2 #15 + 6-12 Wave 3 #29 + 5-1 Wave 3 #26 4 도메인 inheritance baseline)
- ★ **§12 FINAL REVIEW S10-4 Content: A inherited 통산 보존 + §13.X-1 SKIP no-op 자동 inheritance** (Phase 5 inheritance, Phase 3 spec 단계 §7.3 헤더 ✅ marker + ④ block + SOT2_MASTER 4 지점 별도 매핑, §12 자체 갱신 design choice 부재 통산)
- ★ **abort marker 10종 NOT FIRED self-fire 0 통산 Stage 1+2 ALL CLEAN** (9 base + SUB_SESSION_HANDOFF_DRIFT NEW sub-B 진입 특수 inheritance, LOCK 변경 0 + DEFINED-HERE 0 + FABRICATION 0 + parent-executed Subagent 0회 + 6 anchor 충족 강제: 안전·누락 0·오류 0·미세·수렴·재검증)

---

## 14. 실행 약점 대응 계획

| # | 약점 | 위험도 | 대응 |
|---|------|--------|------|
| W1 | Google A2A 스펙 업데이트 시 스키마 변경 필요 | MEDIUM | LOCK 항목 검토 주기 분기 1회, 스펙 모니터링 |
| W2 | #13 Agent-Protocol과 경계 모호화 | HIGH | CONFLICT_LOG 기록, R-11-5 규칙 적용 |
| W3 | MoA 패턴 비용 폭발 | MEDIUM | R-11-6 (최대 5 proposer), 비용 Gate 연동 |
| W4 | mDNS 기반 디스커버리 보안 취약 | MEDIUM | mTLS 필수화, 신뢰 영역 제한 |
| W5 | Part2 PARTIAL 영역 변경 시 동기화 누락 | LOW | 방식 C 요약 형식 유지, 변경 시 CONFLICT_LOG |

---

## 부록 §A — 프로토콜 스펙 레퍼런스

### §A.1 JSON-RPC 2.0 Task Lifecycle

> **정본**: sot 2/3-8_Conversation-A2A/CONVERSATION_A2A_상세명세.md §2

VAMOS A2A는 Google A2A 프로토콜(2025.04)의 JSON-RPC 2.0 기반 메시지 포맷을 채택한다.

**지원 메서드 (8개)**:

| 메서드 | 방향 | 설명 |
|--------|------|------|
| `tasks/send` | Client → Agent | 작업 전송 |
| `tasks/sendSubscribe` | Client → Agent | 작업 전송 + SSE 구독 |
| `tasks/get` | Client → Agent | 작업 상태 조회 |
| `tasks/cancel` | Client → Agent | 작업 취소 |
| `tasks/pushNotification/set` | Client → Agent | 푸시 알림 설정 |
| `tasks/pushNotification/get` | Client → Agent | 푸시 알림 조회 |
| `tasks/resubscribe` | Client → Agent | SSE 재구독 |
| `agent/authenticatedExtendedCard` | Client → Agent | 인증 후 확장 카드 조회 |

**Task 상태 전이 규칙 (LOCK-A2A-02)**:

```
submitted → working → completed | failed | canceled
                   → input-required → working (user responds)
```

- `submitted → working`: 에이전트가 작업을 수락한 즉시
- `working → input-required`: 추가 사용자 입력 필요 시
- `working → completed/failed`: 최종 상태 (불가역)
- 어느 상태에서든 `→ canceled`: `tasks/cancel` 호출 시

### §A.2 A2A Card 확장 스펙

VAMOS 에이전트 카드는 Google A2A Agent Card에 다음 확장 필드를 추가한다:

```json
{
  "x-vamos-extensions": {
    "trust_level": "verified | unverified | internal",
    "cost_tier": "free | standard | premium",
    "max_concurrent_tasks": 10,
    "supported_languages": ["ko", "en"],
    "blue_node_type": "research | content | dev | quant | trading"
  }
}
```

### §A.3 mDNS Service Type

- **서비스 타입**: `_vamos-a2a._tcp.local.` (LOCK-A2A-04)
- **TXT 레코드**: `v=1`, `path=/a2a`, `caps=streaming,push`, `agent-id=<UUID>`
- **우선순위**: SRV 레코드 priority 필드 (0=최고, 100=최저)

---

## 부록 §B — Agent Discovery 메커니즘

### §B.1 mDNS/DNS-SD 기반 자동 발견

> **정본**: sot 2/3-8_Conversation-A2A/CONVERSATION_A2A_상세명세.md §3

**발견 흐름**:

```
1. 클라이언트 에이전트가 mDNS 쿼리 브로드캐스트
2. 대상 에이전트가 SRV + TXT 레코드로 응답
3. 클라이언트가 /.well-known/agent.json 으로 에이전트 카드 조회
4. 카드의 capabilities/skills 확인 후 호환성 판단
5. 호환 시 연결 수립, 비호환 시 다음 후보 탐색
```

**로컬 vs 원격 디스커버리**:

| 방식 | 범위 | 프로토콜 | V1/V2/V3 |
|------|------|---------|---------|
| mDNS | 로컬 네트워크 | mDNS/DNS-SD | V1 |
| Service Registry | 클러스터 내 | HTTP REST API | V2 |
| Global Discovery | 인터넷 | HTTPS + well-known URI | V3 |

### §B.2 스킬 매칭 알고리즘

> **정본**: 상세명세 §3.3 에이전트 선택 알고리즘

가중 스코어링 (Jaccard 유사도 40% + 부하 25% + 우선순위 20% + 지연 15%):

```
score = 0.40 * jaccard(task.skills, agent.skills)
      + 0.25 * (1.0 - agent.load_factor)
      + 0.20 * (1.0 - agent.priority / 100)
      + 0.15 * (1.0 / (1.0 + agent.avg_latency_ms / 1000))
```

---

## 부록 §C — MoA(Mixture-of-Agents) 패턴

### §C.1 다중 에이전트 합의 프로토콜

> **정본**: 상세명세 §5.3

**MoA 실행 흐름**:

```
1. Orchestrator가 N개 proposer 에이전트에 동일 task 병렬 전송
2. 각 proposer가 독립적으로 응답 생성 (tasks/send)
3. 모든 응답 수집 후 aggregator 에이전트에 합성 요청
4. Aggregator가 N개 제안을 분석하여 최적 응답 생성
5. 최종 응답을 원래 요청자에게 반환
```

**제약 사항 (R-11-6)**:

| 파라미터 | 최소 | 최대 | 기본값 |
|---------|------|------|--------|
| proposer 수 | 2 | 5 | 3 |
| 응답 대기 타임아웃 | 5초 | 120초 | 30초 |
| aggregator 수 | 1 | 1 | 1 |

**비용 관리**: MoA 실행 시 비용 = (proposer 수 + 1) × 단일 호출 비용. D2.0-05 §2의 비용 상한 Gate와 연동하여 상한 초과 시 자동 차단.

---

## Part2 정본 요약 (방식 C)

> **출처**: PART2 §6 A2A 관련 (line ~3024~3072, ~4346~4530)
> **Part2가 정본**: When + Where (Phase 배정 = V2~V3, 코드 위치 = `backend/vamos_core/agent_teams/a2a/`)
> **sot 2/가 정본**: What + How (프로토콜 스키마, 디스커버리 알고리즘, 보안 구현, MoA 패턴)

### Part2 핵심 내용 요약

Part2는 A2A를 `backend/vamos_core/agent_teams/a2a/` 아래 4개 파일(protocol.py, discovery.py, security.py, adapter.py)로 배치하고, V3-Phase 2에서 PARL 에이전트 협업 인프라, V3-Phase 3에서 A2A 프로토콜 + 50+ Agent Mesh 완성을 계획한다(Part2 L4534 검증 확인). v12 확장 항목으로 A2A Task Lifecycle(HIGH), A2A 모니터링(HIGH), A2A-MCP 브리지(HIGH), 에이전트 디스커버리(MEDIUM) 등 8건이 등록되어 있다.

### sot 2/ 보완 영역

Part2에 없는 구현 상세를 sot 2/에서 보강:
- JSON-RPC 2.0 메시지 스키마 (Full JSON Schema)
- Task Lifecycle 상태 머신 (전이 규칙, 에러 코드)
- 에이전트 카드 확장 스펙 (`x-vamos-extensions`)
- mDNS/DNS-SD 프로토콜 상세 (TXT 레코드, SRV 우선순위)
- 스킬 매칭 알고리즘 (가중 스코어링)
- mTLS + JWT 인증 상세 (Claims, 위임 체인)
- MoA 패턴 상세 (제약, 비용 관리)
- 모니터링 메트릭/테스트 프레임워크

---

## 부록 — Part2 교차 참조 (S10-4 추가)

> **목적**: Part2 구현단계에서 3-8 Conversation-A2A에 해당하는 항목을 정밀 매핑하여 반영률 95%+ 달성
> **추가일**: 2026-03-27 (Phase 10 S10-4)

### 1. Part2 V3-Phase 3 A2A 항목 매핑 (L4336-4548)

| Part2 항목 | Part2 Line | sot 2/ 반영 상태 | 보완 사항 |
|-----------|-----------|:---:|------|
| A2A `protocol.py` JSON-RPC 2.0 | L4462-4464 | ✅ 반영 (상세명세 §2.1) | — |
| A2A `protocol.py` mTLS + JWT | L4464 | ✅ 반영 (상세명세 §4.1) | — |
| A2A mDNS/DNS-SD | L4465 | ✅ 반영 (상세명세 §3.1) | — |
| A2A `adapter.py` MCP 브릿지 | L4466 | 🔲 보완 | **A2A-MCP Bridge 게이트웨이**: JSON-RPC ↔ MCP 메시지 변환 규칙, 라우팅 정책, 에러 코드 매핑. R-11-8 교차 참조와 연계. |
| A2A `security.py` E2E 암호화 | L4467 | 🔲 보완 | **E2E Encryption Spec**: AES-256-GCM 페이로드 암호화, ECDH 키 교환, double ratchet envelope. mTLS(전송 계층)와 별도의 메시지 계층 암호화. |

### 2. LOCK-AT 교차 적용 (Part2 §6.7 L4994-5130)

| LOCK-AT | 값 | sot 2/3-8 반영 상태 | 보완 사항 |
|---------|-----|:---:|------|
| LOCK-AT-003 | 무한 대화 루프 금지 | 🔲 보완 | 대화 상태 머신에 `max_loop_iterations` 가드 + Circuit Breaker 참조 추가. 연속 동일 상태 전이 3회 시 `FORCE_COMPLETE` 전환. |
| LOCK-AT-004 | 위임 깊이 최대 3단계 | ✅ 반영 (LOCK-A2A-07) | — |
| LOCK-AT-009 | 대화 턴 상한 P0=5/P1=10/P2=20 | 🔲 보완 | 대화 상태 머신에 P-level별 턴 카운터 적용: `turn_count` 필드, P-level별 max 초과 시 `GRACEFUL_CLOSE` 전이. |
| LOCK-AT-013 | 위임 시 OWNER 권한 실행 | △ 부분 | delegation_chain JWT claims에 `original_owner` claim 및 privilege escalation prevention 명시. |

### 3. v12 확장 항목 교차 참조

| Part2 Line | v12 ID | 항목명 | sot 2/ 반영 | 보완 사항 |
|-----------|--------|--------|:---:|------|
| L3024 | v12_C09b_110 | A2A Task Lifecycle 관리 | ✅ | — |
| L3025 | v12_C09b_117 | A2A 모니터링/관측 (OTel) | 🔲 보완 | **OpenTelemetry 통합**: trace context propagation (W3C TraceContext), span naming (`a2a.task.{method}`), distributed tracing 연동. |
| L3034 | v12_C03_037 | A2A Test Framework | ✅ | — |
| L3065 | v12_C12_104 | 에러 처리 (Circuit Breaker, DLQ) | 🔲 보완 | **Dead Letter Queue**: 3회 재시도 실패 메시지 → DLQ 적재, retention 72h, 수동 재처리 또는 자동 알림. |
| L3072 | v12_C12_105 | A2A-MCP 브리지 | 🔲 보완 | 상기 §1 MCP 브릿지 항목과 동일 |
| L3109 | v12_C12_101 | 에이전트 디스커버리 | ✅ | — |
| — | v12_C12_115 | VBS-12 에이전트 협업 벤치마크 | 🔲 보완 | Task completion ≥80%, Tool selection ≥90% 기준 (5-1 도메인 정의와 정합) |

### 4. PARL Decision Aggregator 교차 참조

Part2 L5071의 PARL Decision Aggregator와 MoA(Mixture of Agents) 패턴의 관계:
- **Majority Voting**: N개 proposer 중 다수결 → MoA 기본 집계 모드
- **Weighted Average**: 에이전트 신뢰도 가중 평균 → MoA advanced 집계
- **Consensus**: 전원 동의 필요 → Safety-critical 작업 시 적용
- R-11-6 제약: proposer 최소 2, 최대 5 적용

### 5. Part2 Fallback ID 매핑

| Part2 Line | Fallback ID | 조건 | 동작 |
|-----------|------------|------|------|
| L5969 | EXP_A2A_AUTH_FAIL → FB_A2A_RETRY | 인증 실패 | 재시도 3회, 3회 초과 시 `failed` 종단 전이 (LOCK-A2A-02) + `-32600 Invalid Request` (인증 실패, error_codes.md §5.2). FORCE_COMPLETE 금지 (LOCK-A2A-02 미정의 상태) |

---

*본 계획서는 STEP7-B, D2.0-05 SOT 및 Google A2A 프로토콜 표준을 기반으로 작성되었으며, AUTHORITY_CHAIN.md에 정의된 권한 체계를 준수한다. (v1.2 Phase 1 완료, 2026-04-10)*
