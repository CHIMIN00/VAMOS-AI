# VAMOS AI 초보자 가이드 — 작업 세션 운영 가이드

> **버전**: v2.0.0 | **작성일**: 2026-03-13
> **목적**: 대화창(세션)별로 정확히 무엇을 입력하고, 결과물을 어디에 저장하고, 어떻게 자동 조립하는지 안내
> **총 세션 수**: 35개 (작성 30 + 검토 4 + 자동 조립 1)
> **예상 소요**: 세션당 15~30분 (SOT 첨부 + 프롬프트 입력 + 결과 확인)
> **원칙**: 각 세션은 독립적. 새 대화창에서 시작. 이전 세션 의존 없음.

---

## 사전 준비

### 1. 필요한 SOT 문서 위치
```
D:\VAMOS\docs\sot\          ← 모든 SOT 문서 (68개)
D:\VAMOS\docs\guides\       ← 가이드 문서 (본 가이드 + 전체해설 초보자가이드)
```

### 2. 결과물 저장 경로
```
D:\VAMOS\docs\guides\sections\   ← 각 세션 결과물 저장 폴더
```
각 세션의 결과물은 아래 파일명 규칙으로 저장:
```
session_XX.md    (예: session_01.md, session_02.md, ...)
```

### 3. 세션 운영 규칙
- 각 세션마다 **새 대화창** 사용 (컨텍스트 오염 방지)
- SOT 문서 첨부는 **3~5개 이내** (컨텍스트 다이어트 원칙)
- 결과물은 **지정된 경로에 파일로 저장** (수동 복사-붙여넣기 불필요)
- 작성 완료 후 **체크리스트 확인** 후 다음 세션 진행
- 모든 세션 완료 후 **SESSION 35 (자동 조립)** 실행하면 전체해설 초보자가이드에 자동 반영

### 4. 공통 스킬 에이전트 프롬프트 (모든 세션 앞에 붙이기)

아래 내용을 **모든 세션의 첫 번째 입력**으로 사용하세요:

```
[시스템 지시]
당신은 VAMOS AI 초보자 가이드 작성 전문가입니다.
아래 규칙을 반드시 준수하세요:

1. 대상 독자: 프로그래밍/AI 초보자 (기술 용어 사용 시 반드시 괄호 안에 쉬운 설명 추가)
2. 설명 방식: 비유 → 정의 → 구조도/표 → 상세 설명 → 실제 예시 순서
3. 모든 내용은 첨부된 SOT 문서 기반. SOT에 없는 내용 창작 금지.
4. LOCK/FREEZE 값은 반드시 명시하고 "변경 불가" 표시
5. 버전별 차이 (V0/V1/V2/V3) 반드시 표로 정리
6. 모듈 설명 시 포함 항목: 목적, 비유, 입력/출력, 상태, 이벤트, 에러코드, 폴백, 관련 모듈, 버전별 활성 여부
7. 마크다운 형식: # = 대제목, ## = 중제목, ### = 소제목
8. 각 섹션 끝에 "핵심 요약 (3줄)" 추가
9. 한글 기반, 영문 용어는 병기 (예: 의도 감지기 (Intent Detector))
10. 근거 SOT 문서 참조 표기 필수 (예: [근거: D2.0-02 §2.3])
11. 결과물 맨 위에 아래 헤더를 반드시 포함:
    ---
    session: XX
    sections: [해당 섹션 번호들]
    status: complete
    ---
```

---

## SESSION 01 — §1. VAMOS AI란 무엇인가?

### 첨부할 SOT 문서 (3개)
1. `BASE-1.3_VAMOS_RULE_1.3_BASE.md`
2. `PLAN-3.0_최종완성본.md` (§1~§3만 발췌)
3. `VAMOS_BEGINNER_GUIDE.md` (§1~§3만 발췌)

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_01.md
```

### 프롬프트
```
[위의 시스템 지시를 먼저 입력]

첨부된 SOT 문서를 기반으로 아래 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_01.md 에 저장해주세요.

## 작성 대상: §1. VAMOS AI란 무엇인가?

### 포함해야 할 하위 섹션:
- §1.1 정의와 정체성 — Virtual AI Mind Operating System
  - VAMOS 이름의 의미, AGI 지향 구조, 사용자 중심 개인 AI 어시스턴트
- §1.2 핵심 철학 — 6대 원칙
  - 사용자 중심, 정확성/근거 기반, 최신성, 장기 맥락 유지, 멀티 인텐트 대화, 구조적 모듈화
- §1.3 우선순위 체계
  - 정확성 > 품질 > 안전 > 속도 > 비용 (왜 이 순서인지 설명)
- §1.4 14대 핵심 목표 (A/B/C/D 그룹)
  - A그룹(지능 5개), B그룹(아키텍처 4개), C그룹(생산성 3개), D그룹(진화 2개)
- §1.5 7대 절대 금지사항 (Non-Goals)
  - 실거래 연결 금지, 불법 활동 금지, 의료/법률 확정 판단 금지, PII 장기 저장 금지, 저작권 위반 금지, P2 자동 생성 금지, 무승인 자동화 금지
- §1.6 VAMOS vs 기존 AI 비교
  - ChatGPT, GitHub Copilot, Perplexity 등과의 차이점 표
- §1.7 사용 시나리오 예시
  - 개발자, 연구자, 투자 분석, 일반 사용자 각 1개씩

### 검증 체크리스트:
- [ ] 6대 원칙 모두 포함?
- [ ] 14대 목표 모두 나열?
- [ ] 7대 금지사항 모두 명시?
- [ ] LOCK 값 표시?
- [ ] 비유 설명 포함?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 200~300줄

---

## SESSION 02 — §2. 전체 아키텍처 — 4계층 구조

### 첨부할 SOT 문서 (3개)
1. `D2.0-01_VAMOS_DESIGN_2_0_OVERVIEW.md`
2. `PLAN-3.0_최종완성본.md` (§1.3A 아키텍처 부분)
3. `VAMOS_BEGINNER_GUIDE.md` (아키텍처 관련 부분)

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_02.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_02.md 에 저장해주세요.

## 작성 대상: §2. 전체 아키텍처 — 4계층 구조

### 포함해야 할 하위 섹션:
- §2.1 아키텍처 개요도 (ASCII 다이어그램)
- §2.2 1계층: Front Mini LLM — 역할, 비유(입구 경비원), 하는 일 3가지
- §2.3 2계층: ORANGE CORE — 역할, 비유(두뇌/지휘관), I-Series 모듈 25개 관장
- §2.4 3계층: BLUE NODES — 역할, 비유(실행팀), P0/P1/P2 도메인 실행
- §2.5 4계층: OTHER BRAINS / INFRA-CORE — 역할, 비유(도구/자원), Brain Adapter
- §2.6 Main/Hologram LLM — 최종 출력 생성, 3-Part Output
- §2.7 계층 간 데이터 흐름 전체도 (ASCII 흐름도)
- §2.8 개발 환경 셋업 — V1(로컬), V2(Docker), V3(K8s) 각각의 셋업 절차 ★GAP-2

### 검증 체크리스트:
- [ ] 4계층 모두 설명?
- [ ] 각 계층의 비유 포함?
- [ ] 데이터 흐름도 포함?
- [ ] V1/V2/V3 환경 셋업 포함?
- [ ] Front Mini LLM → Main LLM 전체 흐름?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 200~250줄

---

## SESSION 03 — §3. 처리 파이프라인

### 첨부할 SOT 문서 (3개)
1. `D2.0-02_VAMOS_DESIGN_2_0_ORANGE_CORE.md`
2. `D2.0-05_VAMOS_DESIGN_2_0_AGENT_WORKFLOW.md`
3. `VAMOS_BEGINNER_GUIDE.md` (파이프라인 관련 부분)

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_03.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_03.md 에 저장해주세요.

## 작성 대상: §3. 처리 파이프라인 — 요청부터 응답까지

### 포함해야 할 하위 섹션:
- §3.1 9-State 상태 머신 (S0~S8) — 각 상태 설명 + 전이 조건 + 상태 다이어그램
- §3.2 Standard 5-Phase 파이프라인
  - §3.2.1~3.2.5 각 Phase 상세 (Intake/Plan/Execute/Verify/Deliver)
  - 각 Phase에서 어떤 Gate가 적용되는지
- §3.3 3-Part Output (user_response, evidence_summary, log_report)
- §3.4 TEE Loop (Think-Execute-Evaluate) — 반복 조건, 최대 횟수 (P0=3, P1=5, P2=10)
- §3.5 Soft Loop / Hard Loop / Circuit Breaker — 각각의 차이와 발동 조건
- §3.6 에러 발생 시 흐름 (Failure → Fallback → Deny) — 흐름도
- §3.7 ★에러 처리 표준 — Result<T, VamosError> 계약
  - VamosError 필드: failure_code, message, fallback_id, trace_id
  - 모듈 경계에서 예외 금지 원칙

### 검증 체크리스트:
- [ ] S0~S8 9개 상태 모두 설명?
- [ ] 5 Phase 모두 상세?
- [ ] TEE Loop 반복 조건?
- [ ] Circuit Breaker 3상태 (CLOSED/OPEN/HALF-OPEN)?
- [ ] VamosError 계약 포함?
- [ ] 9-State LOCK 표시?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 300~400줄

---

## SESSION 04 — §4. 5-Gate 시스템 + §5. Decision 객체

### 첨부할 SOT 문서 (3개)
1. `D2.0-07_VAMOS_DESIGN_2_0_SAFETY_COST_APPROVAL.md`
2. `D2.0-02_VAMOS_DESIGN_2_0_ORANGE_CORE.md` (I-5 Decision Engine 부분)
3. `D2.1-D2_VAMOS_SCHEMA_2_1_ORANGE_CORE.md` 또는 `D2.1-D7_VAMOS_SCHEMA_2_1_SAFETY_COST_APPROVAL.md`

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_04.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 두 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_04.md 에 저장해주세요.

## 작성 대상 A: §4. 5-Gate 검증 시스템

### 포함 항목:
- §4.1 Gate 시스템 개요 — 비유(공항 보안 검색대 5단계)
- §4.2 Gate 1: PolicyGate (정책 검증) — 역할, 판정값, 트리거 조건, 실패 시 행동
- §4.3 Gate 2: CostGate (비용 검증) — 역할, 판정값, 트리거 조건, 실패 시 행동
- §4.4 Gate 3: ApprovalGate (승인 검증) — 역할, 판정값, 트리거 조건, 실패 시 행동
- §4.5 Gate 4: EvidenceGate (근거 검증) — 역할, 판정값, 트리거 조건, 실패 시 행동
- §4.6 Gate 5: SelfCheckGate (자체 품질 검증) — 역할, 판정값, 트리거 조건, 실패 시 행동
- §4.7 Gate 우선순위: Policy > Cost > Approval > Evidence > SelfCheck
- §4.8 Gate 결과 조합 행동 분기표
- §4.9 ★HITL 타이밍 & Gate Threshold Ledger
  - SF-L01 HITL 트리거 목록
  - Gate 임계값 변경 규칙 (분기별 감사)
  - PolicyCheck Self-Check (정책 자기 검증)

## 작성 대상 B: §5. Decision 객체

### 포함 항목:
- §5.1 Decision이란? (비유: 재판 판결문)
- §5.2 IntentFrame — 필드 10개 상세
- §5.3 EvidencePack — 필드 6개 상세
- §5.4 Decision Lock 원칙 — locked=true 후 변경 불가
- §5.5 Decision 결론 4가지: ACCEPT/REJECT/HOLD/ESCALATE (각각 언제 발생하는지)
- §5.6 ResponseEnvelope — 5필드

### 검증 체크리스트:
- [ ] 5 Gate 모두 설명?
- [ ] Gate 우선순위 명시?
- [ ] HITL 트리거 목록?
- [ ] IntentFrame 10필드?
- [ ] EvidencePack 6필드?
- [ ] Decision Lock LOCK 표시?
- [ ] 4가지 결론 설명?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 350~450줄

---

## SESSION 05 — §6. 모듈 시스템 개요

### 첨부할 SOT 문서 (2개)
1. `D2.0-01_VAMOS_DESIGN_2_0_OVERVIEW.md` (§1.4 Module Catalog)
2. `CLAUDE.md`

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_05.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_05.md 에 저장해주세요.

## 작성 대상: §6. 모듈 시스템 개요

### 포함 항목:
- §6.1 모듈이란? — 레고 블록 비유, Runnable 인터페이스
- §6.2 분류 체계: CORE(필수)/COND(조건부)/EXP(실험) — 각각의 의미
- §6.3 버전별 활성 모듈 수 표: V0(5) → V1(32) → V2(42) → V3(81)
  - 시리즈별 (I/E/S/A/B/C/D/EVX) 상세 수량 표
- §6.4 네이밍 규칙: I-#(Internal), E-#(External), S-#(Self-evo), A-#(Advanced), B-#(Memory), C-#(Reasoning), D-#(Generation), EVX-#(Verify Extension)
- §6.5 모듈 간 의존성 규칙: CORE→COND 단방향, 역방향 금지 (R7)
- 81개 모듈 전체 목록 표 (ID, 이름, 분류, LOCK여부, 활성 버전)

### 검증 체크리스트:
- [ ] 81개 모듈 전체 목록 표?
- [ ] CORE/COND/EXP 분류 설명?
- [ ] 버전별 수량 표?
- [ ] 네이밍 규칙 설명?
- [ ] 의존성 규칙 R7?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 200~250줄

---

## SESSION 06 — §7 Part 1: I-Series I-1 ~ I-8

### 첨부할 SOT 문서 (2개)
1. `D2.0-02_VAMOS_DESIGN_2_0_ORANGE_CORE.md`
2. `CLAUDE.md`

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_06.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_06.md 에 저장해주세요.

## 작성 대상: §7 I-Series — I-1부터 I-8까지 (8개 모듈)

각 모듈에 대해 아래 형식으로 작성:
1. 모듈 이름 (한글 + 영문)
2. 비유 (초보자가 이해하기 쉬운 한 줄)
3. 목적 (2~3문장)
4. 입력 (Input)
5. 출력 (Output)
6. 내부 상태 (States)
7. 관련 이벤트 (Events) — oc.i#.* 네임스페이스
8. 에러 코드 (FailureCodes) — OC_I#_*
9. 폴백 전략 (Fallbacks) — FB_*
10. Policy Hook 목록
11. 관련 모듈 (Cross-reference)
12. 버전별 활성 여부 (V0/V1/V2/V3)
13. LOCK 여부 (change_lock)

### 대상 모듈:
- §7.1 I-1 Intent Detector
- §7.2 I-2 Context Builder / RAG
- §7.3 I-3 Memory System
- §7.4 I-4 Multimodal Interpreter
- §7.5 I-5 Decision Engine (LOCK, change_lock=true)
- §7.6 I-6 Self-check Engine
- §7.7 I-7 Project/Session Manager
- §7.8 I-8 Policy Engine (LOCK, change_lock=true)

### 검증 체크리스트:
- [ ] 8개 모듈 모두 작성?
- [ ] 각 모듈 13가지 항목 모두 포함?
- [ ] I-5, I-8의 LOCK 표시?
- [ ] 비유 설명 포함?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 400~500줄

---

## SESSION 07 — §7 Part 2: I-Series I-9 ~ I-17

### 첨부할 SOT 문서 (2개)
1. `D2.0-02_VAMOS_DESIGN_2_0_ORANGE_CORE.md`
2. `CLAUDE.md`

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_07.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_07.md 에 저장해주세요.

## 작성 대상: §7 I-Series — I-9부터 I-17까지 (9개 모듈)

각 모듈에 대해 아래 형식으로 작성:
1. 모듈 이름 (한글 + 영문)
2. 비유 (초보자가 이해하기 쉬운 한 줄)
3. 목적 (2~3문장)
4. 입력 (Input)
5. 출력 (Output)
6. 내부 상태 (States)
7. 관련 이벤트 (Events) — oc.i#.* 네임스페이스
8. 에러 코드 (FailureCodes) — OC_I#_*
9. 폴백 전략 (Fallbacks) — FB_*
10. Policy Hook 목록
11. 관련 모듈 (Cross-reference)
12. 버전별 활성 여부 (V0/V1/V2/V3)
13. LOCK 여부 (change_lock)

### 대상 모듈:
- §7.9 I-9 Cost Manager (비용 관리자) — LOCK, change_lock=true
  - 비용 상한: V1 ₩40K/mo, V2 ₩93K/mo, V3 ₩266K/mo (ABSOLUTE LOCK)
  - Downshift 메커니즘, 예산 소진 시 자동 모델 다운그레이드
- §7.10 I-10 Tool Registry/Router (도구 등록소)
  - MCP 도구 등록, 라우팅, capability 매칭
- §7.11 I-11 Output Composer (출력 조합기)
  - 3-Part Output 생성, ResponseEnvelope 조립
- §7.12 I-12 Workflow Builder (작업흐름 설계기)
  - DAG 기반 워크플로우 생성, 12패턴 지원
- §7.13 I-13 Multimodal Output Renderer (다중 출력 렌더러)
  - 텍스트/이미지/차트/코드 출력 렌더링
- §7.14 I-14 Summarizer & Memory Distiller (요약 & 기억 증류기)
  - 대화 요약, L0→L1 승격 판단, 기억 압축
- §7.15 I-15 Evidence & QoD Manager (근거 품질 관리자)
  - QoD 점수 산출, 근거 부족 시 재검색 트리거
- §7.16 I-16 Knowledge Search Engine (지식 검색 엔진)
  - Hybrid Search (BM25 + Vector), Semantic Cache
- §7.17 I-17 Blue Node Manager (실행팀 관리자)
  - Blue Node 생명주기 관리, NodeCapabilityProfile

### 검증 체크리스트:
- [ ] 9개 모듈 모두 작성?
- [ ] 각 모듈 13가지 항목 모두 포함?
- [ ] I-9의 LOCK 표시 및 비용 상한 ABSOLUTE LOCK?
- [ ] 비유 설명 포함?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 450~550줄

---

## SESSION 08 — §7 Part 3: I-Series I-18 ~ I-25

### 첨부할 SOT 문서 (3개)
1. `D2.0-02_VAMOS_DESIGN_2_0_ORANGE_CORE.md`
2. `CLAUDE.md`
3. `VAMOS_SDAR_DESIGN_SPECIFICATION.md` (I-25 SDAR Engine 참조용)

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_08.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_08.md 에 저장해주세요.

## 작성 대상: §7 I-Series — I-18부터 I-25까지 (8개 모듈)

각 모듈에 대해 아래 형식으로 작성:
1. 모듈 이름 (한글 + 영문)
2. 비유 (초보자가 이해하기 쉬운 한 줄)
3. 목적 (2~3문장)
4. 입력 (Input)
5. 출력 (Output)
6. 내부 상태 (States)
7. 관련 이벤트 (Events) — oc.i#.* 네임스페이스
8. 에러 코드 (FailureCodes) — OC_I#_*
9. 폴백 전략 (Fallbacks) — FB_*
10. Policy Hook 목록
11. 관련 모듈 (Cross-reference)
12. 버전별 활성 여부 (V0/V1/V2/V3)
13. LOCK 여부 (change_lock)

### 대상 모듈:
- §7.18 I-18 Self-evo Engine (자기 진화 엔진)
  - 6가지 변경 가능 영역, 7가지 변경 불가 영역 (LOCK)
  - 롤백 정책: 스냅샷, 이상 탐지, 재적용 잠금
- §7.19 I-19 Approval Manager (승인 관리자) — LOCK, change_lock=true
  - P0/P1/P2 승인 매트릭스, 타임아웃 10분→자동 거절
  - NEVER_AUTO 규칙
- §7.20 I-20 Failure/Fallback Manager (장애 대응 관리자)
  - 36 FailureCode → 23 Fallback 매핑
  - Circuit Breaker 3상태 (CLOSED/OPEN/HALF-OPEN)
- §7.21 I-21 Source Evolution (정보원 진화)
  - 소스 신뢰도 관리, 신뢰도 하락 시 자동 비활성화
- §7.22 I-22 Task/Project Manager (작업 관리자)
  - 프로젝트 ↔ 세션 매핑, 장기 작업 추적
- §7.23 I-23 Doc/Code Structuring (문서/코드 구조화)
  - 코드 생성 시 구조화 규칙, 문서 템플릿 관리
- §7.24 I-24 Knowledge Graph Engine (지식 그래프 엔진)
  - Neo4j/NetworkX 기반, GraphRAG 연동
- §7.25 I-25 SDAR Engine (자가진단/자동수리 엔진)
  - 5-Layer Pipeline, AR-L0~L4, Kill Switch
  - SDAR_SPEC 참조, 보안 오류 특별 규칙 (LOCK)

### 검증 체크리스트:
- [ ] 8개 모듈 모두 작성?
- [ ] 각 모듈 13가지 항목 모두 포함?
- [ ] I-19의 LOCK 표시?
- [ ] I-25 SDAR 5-Layer 설명?
- [ ] 비유 설명 포함?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 400~500줄

---

## SESSION 09 — §8. E-Series 외부 도구 모듈 (16개)

### 첨부할 SOT 문서 (3개)
1. `D2.0-04_VAMOS_DESIGN_2_0_INFRA_CORE.md`
2. `CLAUDE.md`
3. `D2.0-03_VAMOS_DESIGN_2_0_BLUE_NODES.md` (E-모듈 연동 부분)

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_09.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_09.md 에 저장해주세요.

## 작성 대상: §8. E-Series — 외부 도구 모듈 (E-1 ~ E-16, 총 16개)

각 모듈에 대해 아래 형식으로 작성:
1. 모듈 이름 (한글 + 영문)
2. 비유 (초보자가 이해하기 쉬운 한 줄)
3. 목적 (2~3문장)
4. 입력/출력 (Input/Output)
5. 분류 (CORE/COND/EXP)
6. 버전별 활성 여부 (V0/V1/V2/V3)
7. 특별 보안 규칙 (있는 경우)

### 대상 모듈 (16개 전부):
- §8.1 E-1 Coding Helper (코딩 도우미) — 코드 생성/리팩터/디버그
- §8.2 E-2 Web Search (웹 검색) — Tavily/SerpAPI, 최신 정보 수집
- §8.3 E-3 Document Parser (문서 파서) — PDF/DOCX/XLSX 파싱
- §8.4 E-4 Code Executor (코드 실행기) — ★Docker Sandboxing 상세 포함
  - 네트워크 차단 (--network=none)
  - 파일시스템 읽기전용 (readonly rootfs)
  - 타임아웃 30초 (LOCK)
  - 메모리 제한 256MB
  - SANDBOX_* 에러코드 (SANDBOX_TIMEOUT, SANDBOX_OOM, SANDBOX_NETWORK_VIOLATION)
- §8.5 E-5 Image Analyzer (이미지 분석기) — GPT-4V/LLaVA
- §8.6 E-6 Z3 Solver (논리 풀이기) — 논리 검증, SAT
- §8.7 E-7 Speech-to-Text (음성→텍스트) — Whisper
- §8.8 E-8 Text-to-Speech (텍스트→음성) — TTS 엔진
- §8.9 E-9 Video Analyzer (영상 분석기) — 프레임 추출 + 분석
- §8.10 E-10 External API Gateway (외부 API 게이트웨이) — rate limiting, HMAC
- §8.11 E-11 Browser Automation (브라우저 자동화) — Playwright
- §8.12 E-12 DB Connector (데이터베이스 연결기) — SQLite/PostgreSQL
- §8.13 E-13 Calendar/Task Sync (캘린더 연동) — Google Calendar API
- §8.14 E-14 Email Handler (이메일 처리기) — IMAP/SMTP
- §8.15 E-15 Cloud Collector / File System (클라우드 수집기)
- §8.16 E-16 Cloud Storage Sync (클라우드 저장소 동기화) — S3/GCS

### 검증 체크리스트:
- [ ] 16개 모듈 모두 작성?
- [ ] E-4 Docker Sandboxing 상세 (네트워크, 파일시스템, 타임아웃, 메모리)?
- [ ] SANDBOX_* 에러코드 포함?
- [ ] 버전별 활성 여부?
- [ ] 비유 설명 포함?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 400~500줄

---

## SESSION 10 — §9. S-Series (8개) + §10. A-Series (7개)

### 첨부할 SOT 문서 (3개)
1. `D2.0-01_VAMOS_DESIGN_2_0_OVERVIEW.md` (Module Catalog)
2. `CLAUDE.md`
3. `D2.0-04_VAMOS_DESIGN_2_0_INFRA_CORE.md` (A-Series 관련)

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_10.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 두 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_10.md 에 저장해주세요.

## 작성 대상 A: §9. S-Series — 자기 진화 모듈 (8개)

각 모듈에 대해 아래 형식으로 작성:
1. 모듈 이름 (한글 + 영문)
2. 비유 (초보자가 이해하기 쉬운 한 줄)
3. 목적 (2~3문장)
4. 입력/출력
5. 분류 (CORE/COND/EXP)
6. 버전별 활성 여부 (V0/V1/V2/V3)
7. LOCK 여부

### 대상 모듈:
- §9.1 S-1 Self-check Engine (자기 검증 엔진) — 출력 품질 자동 검증
- §9.2 S-2 Benchmark QA Suite (벤치마크 테스트) — 성능 기준 평가
- §9.3 S-3 Template Evolution (템플릿 진화) — 프롬프트/응답 템플릿 진화
- §9.4 S-4 Error Pattern Miner (에러 패턴 분석기) — 반복 에러 패턴 학습
- §9.5 S-5 Router Evolution (라우터 진화) — 라우팅 규칙 자동 최적화
- §9.6 S-6 Search Evolution (검색 진화) — RAG 파라미터 자동 튜닝
- §9.7 S-7 User-Coop Designer (사용자 협업 설계기) — 사용자 선호도 학습
- §9.8 S-8 Self-evo Governance (자기 진화 거버넌스) — 진화 규칙 감독

## 작성 대상 B: §10. A-Series — 아키텍처 확장 모듈 (7개)

### 대상 모듈:
- §10.1 A-1 MultiBrain Adapter (멀티 AI 어댑터) — 여러 LLM 연결/전환
- §10.2 A-2 Preset Modularization (프리셋 모듈화) — 사용자 커스텀 프리셋
- §10.3 A-3 Meta AI (메타 AI) — AI가 AI를 관리
- §10.4 A-4 Debate Mode (토론 모드) — 다중 에이전트 토론
- §10.5 A-5 Lazy Generation (지연 생성) — 필요 시까지 생성 지연
- §10.6 A-6 Federated Module Network (연합 모듈 네트워크) — V3 분산 모듈
- §10.7 A-7 Remote Executor (원격 실행기) — 원격 GPU/서버 실행

### 검증 체크리스트:
- [ ] S-Series 8개 모듈 모두 작성?
- [ ] A-Series 7개 모듈 모두 작성?
- [ ] 총 15개 모듈 각각 비유 포함?
- [ ] 버전별 활성 여부 표?
- [ ] LOCK 여부 표시?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 300~400줄

---

## SESSION 11 — §11. B-Series (6개) + §12. C-Series (7개) + §11.7 프롬프트 관리

### 첨부할 SOT 문서 (3개)
1. `D2.0-01_VAMOS_DESIGN_2_0_OVERVIEW.md` (Module Catalog)
2. `D2.0-06_VAMOS_DESIGN_2_0_STORAGE_MEMORY.md` (B-Series 메모리 관련)
3. `CLAUDE.md`

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_11.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 세 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_11.md 에 저장해주세요.

## 작성 대상 A: §11. B-Series — 기억/스킬 자산 모듈 (6개)

각 모듈에 대해 아래 형식으로 작성:
1. 모듈 이름 (한글 + 영문)
2. 비유 (초보자가 이해하기 쉬운 한 줄)
3. 목적 (2~3문장)
4. 입력/출력
5. 분류 (CORE/COND/EXP)
6. 버전별 활성 여부 (V0/V1/V2/V3)
7. LOCK 여부

### 대상 모듈:
- §11.1 B-1 Skill Library (스킬 라이브러리) — 재사용 가능한 스킬 저장소
- §11.2 B-2 Procedural Memory (절차적 기억) — 작업 절차 기억, L3 레벨
- §11.3 B-3 Memory Decay (기억 감쇠) — TTL 기반 자동 삭제/감쇠
- §11.4 B-4 Auto Curriculum Generator (자동 커리큘럼) — 학습 경로 자동 생성
- §11.5 B-5 RL-like Self Trainer (강화학습형 자기 훈련) — 보상 기반 자기 개선
- §11.6 B-6 DSPy Prompt Optimizer (프롬프트 최적화) — DSPy 기반 프롬프트 최적화

## 작성 대상 B: §11.7 ★프롬프트 관리 & 템플릿 진화 시스템 (GAP-5)

### 포함 항목:
- 프롬프트 버전 관리 체계
- 템플릿 진화 규칙 (S-3 연동)
- DSPy 통합 파이프라인
- 프롬프트 A/B 테스트 프레임워크
- [근거: D2.0-05 §7.5]

## 작성 대상 C: §12. C-Series — 검증/추론 모듈 (7개)

### 대상 모듈:
- §12.1 C-1 Logic Verifier (논리 검증기) — 논리적 일관성 검증
- §12.2 C-2 Math Verifier (수학 검증기) — 수학 계산 검증 (SymPy)
- §12.3 C-3 Code Verifier (코드 검증기) — 코드 정확성 검증 (AST, lint)
- §12.4 C-4 Domain Simulator (도메인 시뮬레이터) — 시나리오 시뮬레이션
- §12.5 C-5 Bayesian Belief Network (베이지안 추론) — 확률적 추론
- §12.6 C-6 RL Advisor (강화학습 어드바이저) — 행동 최적화 조언
- §12.7 C-7 GNN Score Model (그래프 신경망 스코어) — 지식 그래프 기반 점수

### 검증 체크리스트:
- [ ] B-Series 6개 모듈 모두 작성?
- [ ] C-Series 7개 모듈 모두 작성?
- [ ] §11.7 프롬프트 관리 시스템 GAP-5 포함?
- [ ] 총 13개 모듈 + 1개 시스템 각각 비유 포함?
- [ ] 버전별 활성 여부 표?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 300~350줄

---

## SESSION 12 — §13. D-Series (6개) + §14. EVX-Series (6개)

### 첨부할 SOT 문서 (3개)
1. `D2.0-01_VAMOS_DESIGN_2_0_OVERVIEW.md` (Module Catalog)
2. `D2.0-05_VAMOS_DESIGN_2_0_AGENT_WORKFLOW.md` (EVX-Series §7.4)
3. `CLAUDE.md`

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_12.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 두 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_12.md 에 저장해주세요.

## 작성 대상 A: §13. D-Series — 두뇌/플래너/RAG 확장 모듈 (6개)

각 모듈에 대해 아래 형식으로 작성:
1. 모듈 이름 (한글 + 영문)
2. 비유 (초보자가 이해하기 쉬운 한 줄)
3. 목적 (2~3문장)
4. 입력/출력
5. 분류 (CORE/COND/EXP)
6. 버전별 활성 여부 (V0/V1/V2/V3)
7. LOCK 여부

### 대상 모듈:
- §13.1 D-1 Think Engine (사고 엔진) — Chain-of-Thought, Tree-of-Thought
- §13.2 D-2 Multimodal Engine (멀티모달 엔진) — 이미지/음성/영상 통합 처리
- §13.3 D-3 Long Horizon Planner (장기 계획 수립기) — 다단계 작업 계획
- §13.4 D-4 Personality/Tone Engine (성격/톤 엔진) — 사용자 맞춤 톤/스타일
- §13.5 D-5 Parallel General Brain (병렬 범용 두뇌) — 병렬 LLM 실행
- §13.6 D-6 GraphRAG / Hybrid RAG (그래프 기반 RAG) — 지식 그래프 + 벡터 검색 결합

## 작성 대상 B: §14. EVX-Series — 검증 확장 모듈 (6개)

### 대상 모듈:
- §14.1 EVX-1 Code-as-Policy (코드 기반 정책) — 정책을 코드로 표현/실행
- §14.2 EVX-2 Adversarial Verifier (적대적 검증기) — 적대적 공격 시뮬레이션
- §14.3 EVX-3 Log-prob Confidence (확률 기반 신뢰도) — LLM 출력 확률 분석
- §14.4 EVX-4 Thought Buffer (사고 버퍼) — 중간 사고 과정 저장/재활용
- §14.5 EVX-5 Gen-Verify-Learn (생성-검증-학습 루프) — 자동 개선 루프
- §14.6 EVX-6 Z3 Solver Routing (Z3 라우팅) — Z3 검증 필요 판단/라우팅

### 검증 체크리스트:
- [ ] D-Series 6개 모듈 모두 작성?
- [ ] EVX-Series 6개 모듈 모두 작성?
- [ ] 총 12개 모듈 각각 비유 포함?
- [ ] 버전별 활성 여부 표?
- [ ] LOCK 여부 표시?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 250~300줄

---

## SESSION 13 — §15. 도메인 시스템 P0/P1/P2

### 첨부할 SOT 문서 (3개)
1. `D2.0-03_VAMOS_DESIGN_2_0_BLUE_NODES.md`
2. `BASE-1.3_VAMOS_RULE_1.3_BASE.md` (Non-Goal, P2 규칙)
3. `VAMOS_BEGINNER_GUIDE.md` (도메인 설명)

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_13.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_13.md 에 저장해주세요.

## 작성 대상: §15. 도메인 시스템 — P0/P1/P2

### 포함해야 할 하위 섹션:
- §15.1 도메인이란? (비유: 전문 부서 — 회사에서 영업부/기술부/인사부처럼 역할별로 나뉜 조직)
- §15.2 P0 — 항상 활성 (승인 없이 사용 가능)
  - §15.2.1 Dev/System (개발/시스템) — 코딩, 디버깅, 시스템 관리
  - §15.2.2 Research (리서치/연구) — 정보 검색, 논문 분석
  - §15.2.3 Productivity (생산성) — 문서 작성, 일정 관리, 이메일
- §15.3 P1 — 1회 승인 후 활성 (처음 한 번만 승인하면 이후 자유)
  - §15.3.1 Content (콘텐츠) — 블로그, SNS, 미디어 생성
  - §15.3.2 Data & Quant (데이터/퀀트) — 데이터 분석, 퀀트 모델
- §15.4 P2 — 세션별 승인 필수 (매번 새로 승인 필요, 가장 엄격)
  - §15.4.1 Trading Strategy Analysis (투자 전략 분석)
  - §15.4.2 P2 승인 흐름 상세 — 요청→사유입력→승인→실행→세션 종료 시 자동 비활성화
  - P2 자동 생성 금지 (Non-Goal §1.5)
- §15.5 Blue Node 생명주기 (Created→Initializing→Ready→Running→Paused→Terminated→Archived)
  - 상태 전이도 (ASCII 다이어그램)
- §15.6 NodeCapabilityProfile — 필드 설명 (node_id, domain, tools, llm_config, max_concurrent)

### 검증 체크리스트:
- [ ] P0 3개 도메인 모두 설명?
- [ ] P1 2개 도메인 모두 설명?
- [ ] P2 승인 흐름 상세?
- [ ] 세션 종료 시 자동 비활성화 명시?
- [ ] Blue Node 생명주기 7상태?
- [ ] NodeCapabilityProfile 필드?
- [ ] 비유 설명 포함?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 250~300줄

---

## SESSION 14 — §16. 메모리 시스템

### 첨부할 SOT 문서 (3개)
1. `D2.0-06_VAMOS_DESIGN_2_0_STORAGE_MEMORY.md`
2. `D2.0-07_VAMOS_DESIGN_2_0_SAFETY_COST_APPROVAL.md` (프라이버시 부분)
3. `STEP7_PART_E_S7E_001_050_보안_안전_거버넌스.md` (S7E-031~040 데이터 프라이버시)

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_14.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_14.md 에 저장해주세요.

## 작성 대상: §16. 메모리 시스템 — 4계층 기억 구조

### 포함해야 할 하위 섹션:
- §16.1 왜 기억이 필요한가? (비유: 사람의 단기기억/장기기억)
- §16.2 L0 Session Buffer (대화 기억)
  - 현재 대화 내용 저장, 세션 종료 시 삭제
  - 최대 크기, 슬라이딩 윈도우 방식
- §16.3 L1 Project Memory (프로젝트 기억)
  - 프로젝트별 장기 저장, 명시적 저장
- §16.4 L2 Global Knowledge (장기 지식)
  - 사용자 전체 지식 베이스, 3회 참조 시 자동 승격
- §16.5 L3 Procedural Memory (절차 기억)
  - 작업 절차/패턴 저장, 스킬 라이브러리 연동
- §16.6 기억 4유형: Working / Episodic / Semantic / Procedural
  - 각 유형의 정의와 예시
- §16.7 L0→L1→L2 승격 규칙
  - 3회 참조 시 L2 승격, 승격 조건 표
- §16.8 TTL (유효기간) 정책
  - L0: 세션, L1: 90일, L2: 영구(decay 적용)
- §16.9 PII 마스킹 & 데이터 보호
  - PII 필드 자동 감지, 마스킹 규칙, 저장 금지 항목
- §16.10 ★데이터 프라이버시 경화 (S7E-031~040) — GAP-8
  - GDPR 준수 설계
  - 데이터 암호화 (at-rest, in-transit)
  - 사용자 데이터 삭제 요청 처리 (Right to be Forgotten)
  - 감사 로그 (who accessed what, when)
  - 데이터 보존 정책 (retention policy)

### 검증 체크리스트:
- [ ] L0~L3 4계층 모두 설명?
- [ ] 4유형 (Working/Episodic/Semantic/Procedural) 모두?
- [ ] 승격 규칙 (3회 참조)?
- [ ] TTL 정책 표?
- [ ] PII 마스킹 규칙?
- [ ] ★데이터 프라이버시 경화 GAP-8 포함?
- [ ] 비유 설명 포함?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 300~350줄

---

## SESSION 15 — §17. RAG 시스템

### 첨부할 SOT 문서 (2개)
1. `D2.0-06_VAMOS_DESIGN_2_0_STORAGE_MEMORY.md` (§1.1 RAG Pipeline)
2. `D2.1-A1_VAMOS_TECH_STACK_SPEC.md` (Embedding, Vector DB)

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_15.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_15.md 에 저장해주세요.

## 작성 대상: §17. RAG 시스템 — 지식 검색 & 활용

### 포함해야 할 하위 섹션:
- §17.1 RAG란? (비유: 도서관에서 책 찾기 — 질문 → 관련 책 검색 → 답변 작성)
  - Retrieval-Augmented Generation의 뜻, 왜 LLM만으로는 부족한지
- §17.2 6-Stage RAG Pipeline
  - §17.2.1 Intake (수집) — 문서 입력, 소스 등록
  - §17.2.2 Chunking (분할) — 문서를 적절한 크기로 분할, chunk_size 설정
  - §17.2.3 Embedding (벡터화) — 텍스트를 숫자 벡터로 변환
  - §17.2.4 Indexing (색인) — 벡터 DB에 저장
  - §17.2.5 Retrieval (검색) — 유사 벡터 검색 + BM25 키워드 검색
  - §17.2.6 Synthesis (합성) — 검색 결과 + LLM으로 최종 답변 생성
- §17.3 Hybrid Search (BM25 + Vector + Reranker)
  - 3가지 검색 방법 비교 표
  - Reranker로 최종 순위 결정
- §17.4 Semantic Cache (의미 캐시)
  - 유사 질문 캐시 히트, 비용 절감 효과
- §17.5 QoD — Quality of Data (데이터 품질 점수)
  - 0.0~1.0 점수 산출 기준, 최소 임계값
- §17.6 Embedding 모델: BGE-M3 vs text-embedding-3-small
  - 비교 표 (차원, 다국어, 비용, 성능)
- §17.7 Vector DB: Chroma vs Qdrant
  - V1(Chroma 로컬) vs V2+(Qdrant 서버) 비교 표
- §17.8 GraphRAG (지식 그래프 기반 RAG)
  - 벡터 검색 + 그래프 관계 탐색 결합

### 검증 체크리스트:
- [ ] 6-Stage Pipeline 모두 설명?
- [ ] Hybrid Search 3방법 비교?
- [ ] Semantic Cache 설명?
- [ ] QoD 점수 기준?
- [ ] Embedding 모델 비교 표?
- [ ] Vector DB 비교 표?
- [ ] GraphRAG 설명?
- [ ] 비유 설명 포함?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 300~350줄

---

## SESSION 16 — §18. 보안 체계

### 첨부할 SOT 문서 (2개)
1. `D2.0-07_VAMOS_DESIGN_2_0_SAFETY_COST_APPROVAL.md`
2. `STEP7_PART_E_S7E_001_050_보안_안전_거버넌스.md`

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_16.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_16.md 에 저장해주세요.

## 작성 대상: §18. 보안 체계 — 4-Layer Guardrails

### 포함해야 할 하위 섹션:
- §18.1 왜 4겹 방어가 필요한가? (비유: 공항 보안 — 입구검색 → 탑승게이트 → 기내검사 → 사후감사)
- §18.2 L1: NeMo Guardrails (입력 방어)
  - 위험 입력 차단, 프롬프트 인젝션 필터링
- §18.3 L2: Guardrails AI (처리 중 검증)
  - 처리 과정에서의 정책 위반 감지
- §18.4 L3: LlamaGuard (출력 안전 분류)
  - 출력물의 안전성 분류 (safe/unsafe)
- §18.5 L4: Post-Delivery Audit (사후 감사)
  - 전달 후 비동기 감사, 이상 패턴 탐지
- §18.6 Prompt Injection 방어
  - Direct/Indirect Injection 구분
  - 방어 전략: 입력 분리, 레이어 격리, 탈출 감지
- §18.7 OWASP LLM Top 10 대응
  - 10가지 위협 각각에 대한 VAMOS 대응 전략 표
- §18.8 STRIDE 위협 모델 매핑
  - Spoofing, Tampering, Repudiation, Info Disclosure, DoS, EoP 각각 매핑
- §18.9 AI 코드 생성 보안 체크리스트
  - 자동 생성 코드의 보안 검증 항목
- §18.10 HMAC 인증 & 타이밍 공격 방어
  - HMAC-SHA256, constant-time 비교, nonce, replay 방지
- §18.11 ★제어 역전 방지 (Control Inversion Prevention) — GAP-7
  - S09-B48: AI가 사용자 의도 무시하고 자체 판단하는 것 방지
  - Kill Switch 규칙
  - Constitutional AI 기반 자기 제한
- §18.12 ★커뮤니티 스킬 보안 & RSP 프레임워크 — GAP-10
  - 외부 스킬 설치 시 보안 검증 절차
  - RSP (Responsible Scaling Policy) 적용
  - 스킬 서명 검증, 샌드박스 격리

### 검증 체크리스트:
- [ ] 4-Layer 모두 설명?
- [ ] Prompt Injection 방어 전략?
- [ ] OWASP Top 10 대응 표?
- [ ] STRIDE 매핑?
- [ ] HMAC 인증 상세?
- [ ] ★제어 역전 방지 GAP-7 포함?
- [ ] ★커뮤니티 스킬 보안 GAP-10 포함?
- [ ] 비유 설명 포함?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 400~500줄

---

## SESSION 17 — §19. RBAC + §20. 비용 관리

### 첨부할 SOT 문서 (2개)
1. `D2.0-07_VAMOS_DESIGN_2_0_SAFETY_COST_APPROVAL.md` (§3.6 RBAC, §4 Cost)
2. `BASE-1.3_VAMOS_RULE_1.3_BASE.md` (비용 상한 LOCK)

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_17.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 두 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_17.md 에 저장해주세요.

## 작성 대상 A: §19. RBAC — 역할 기반 접근 제어

### 포함 항목:
- §19.1 4가지 역할 (비유: 회사 직급)
  - OWNER (소유자) — 모든 권한, 시스템 설정 변경
  - ADMIN (관리자) — 모듈 관리, 정책 수정
  - OPERATOR (운영자) — 일상 작업, 제한된 설정
  - VIEWER (열람자) — 읽기 전용
- §19.2 역할별 권한 매트릭스
  - 각 역할이 할 수 있는/없는 것 상세 표
  - P2 승인: OWNER만 가능
  - Self-evo 실행: OWNER/ADMIN만 가능
- §19.3 자율도 수준: L0 ~ L3
  - L0 (완전 수동): 모든 작업에 승인 필요
  - L1 (반자동): P0만 자동, P1/P2 승인
  - L2 (자동): P0/P1 자동, P2 승인
  - L3 (완전 자동): 모든 도메인 자동 (OWNER만 설정 가능)

## 작성 대상 B: §20. 비용 관리 — Cost Control

### 포함 항목:
- §20.1 버전별 비용 상한 (ABSOLUTE LOCK — 절대 변경 불가)
  - V1: ₩40,000/월 (약 $30)
  - V2: ₩93,000/월 (약 $70)
  - V3: ₩266,000/월 (약 $200)
  - 이 값들은 코드에서도 하드코딩 (LOCK)
- §20.2 Downshift 메커니즘 (자동 모델 다운그레이드)
  - 예산 80% 도달 → 경고
  - 예산 90% 도달 → 자동으로 저렴한 모델로 전환
  - 예산 100% 도달 → 서비스 중단 (LOCK)
- §20.3 비용 최적화 전략
  - 프롬프트 캐싱 (50~90% 절감)
  - Batch Processing (50% 절감)
  - Semantic Cache (유사 질문 재사용)
- §20.4 예산 초과 시 행동 흐름 (ASCII 흐름도)
- §20.5 ★규제 준수 & 컴플라이언스 — GAP-16
  - GDPR 준수 항목
  - SOC2 Type II 준비 사항
  - 데이터 주권 (Data Sovereignty) 정책
  - 감사 로그 보존 기간

### 검증 체크리스트:
- [ ] 4가지 역할 모두 설명?
- [ ] 권한 매트릭스 표?
- [ ] 자율도 L0~L3?
- [ ] 비용 상한 ABSOLUTE LOCK?
- [ ] Downshift 3단계?
- [ ] 비용 최적화 3전략?
- [ ] ★규제 준수 GAP-16 포함?
- [ ] 비유 설명 포함?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 300~400줄

---

## SESSION 18 — §21. 승인 시스템

### 첨부할 SOT 문서 (2개)
1. `D2.0-07_VAMOS_DESIGN_2_0_SAFETY_COST_APPROVAL.md` (§3.3 Approval)
2. `D2.0-02_VAMOS_DESIGN_2_0_ORANGE_CORE.md` (I-19 Approval Manager)

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_18.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_18.md 에 저장해주세요.

## 작성 대상: §21. 승인 시스템 — Approval Workflow

### 포함해야 할 하위 섹션:
- §21.1 언제 승인이 필요한가? (비유: 결재 시스템)
  - 자동 승인 가능한 경우 vs 수동 승인 필요한 경우
  - NEVER_AUTO 목록: 절대 자동 승인 불가 항목
- §21.2 P0/P1/P2 도메인별 승인 매트릭스
  - P0: 승인 불필요 (항상 허용)
  - P1: 최초 1회 승인 → 이후 자동
  - P2: 매 세션 승인 필요
  - 각 도메인 × 역할(OWNER/ADMIN/OPERATOR/VIEWER) 매트릭스 표
- §21.3 승인 타임아웃
  - 10분 내 미응답 → 자동 거절 (LOCK)
  - 거절 사유: APPROVAL_TIMEOUT
- §21.4 자율 운영 4단계 (L0~L3)
  - 각 단계에서 어떤 승인이 자동/수동인지 상세 표
- §21.5 S-Module / E-Module 승인 규칙
  - S-Module (Self-evo): 항상 OWNER 승인 필요
  - E-Module (External): 최초 도구 등록 시 승인, 이후 자동
  - 위험 E-Module (E-4 Code Executor, E-11 Browser): 항상 승인

### 검증 체크리스트:
- [ ] 승인 매트릭스 (도메인 × 역할) 표?
- [ ] NEVER_AUTO 목록?
- [ ] 타임아웃 10분 LOCK?
- [ ] 자율 운영 L0~L3 상세?
- [ ] S-Module/E-Module 승인 규칙?
- [ ] 비유 설명 포함?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 200~250줄

---

## SESSION 19 — §22. Agent Teams

### 첨부할 SOT 문서 (2개)
1. `VAMOS_AGENT_TEAMS_SPEC.md`
2. `D2.0-05_VAMOS_DESIGN_2_0_AGENT_WORKFLOW.md` (ADD-027 Agent Profiling)

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_19.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_19.md 에 저장해주세요.

## 작성 대상: §22. Agent Teams — 멀티 에이전트 아키텍처

### 포함해야 할 하위 섹션:
- §22.1 왜 여러 에이전트가 필요한가? (비유: 프로젝트 팀 — 팀장 1명 + 전문가 여러 명)
- §22.2 Lead Agent (리드 에이전트 = ORANGE CORE)
  - 역할: 작업 분배, 결과 취합, 최종 판단
- §22.3 Sub-Agent 8가지 타입
  - Researcher, Coder, Analyst, Writer, Reviewer, Planner, Executor, Specialist
  - 각 타입의 역할과 사용 시점
- §22.4 에이전트 3요소: Identity, Capability, Policy
  - Identity: 이름, 역할, 전문 분야
  - Capability: 사용 가능 도구, LLM 모델
  - Policy: 행동 규칙, 제한사항
- §22.5 에이전트 생명주기 (Created → Initialized → Running → Completed → Archived)
  - 상태 전이도 (ASCII 다이어그램)
- §22.6 6가지 협업 패턴
  - §22.6.1 Sequential (순차) — A→B→C 순서대로
  - §22.6.2 Parallel (병렬) — A,B,C 동시 실행 후 취합
  - §22.6.3 Debate (토론) — 에이전트 간 의견 대립 → 최선안 선택
  - §22.6.4 Supervisor (감독) — 상위 에이전트가 하위 감독
  - §22.6.5 Handoff (인계) — 한 에이전트가 다른 에이전트에게 작업 전달
  - §22.6.6 Map-Reduce (분산-취합) — 작업 분할 → 병렬 실행 → 결과 병합
- §22.7 ★MoA — Mixture of Agents 패턴 — GAP-3
  - 여러 LLM을 동시에 실행하여 최선 결과 선택
  - 오케스트레이션 규칙
  - [근거: D2.0-04 §4.9]
- §22.8 Agent Message 형식 & HMAC 서명
  - 메시지 필드: sender, receiver, content, timestamp, hmac_sig
  - HMAC-SHA256 서명으로 위변조 방지
- §22.9 Delegation 제약 (LOCK)
  - 최대 위임 깊이, 위임 불가 작업 목록
- §22.10 버전별 에이전트 규모
  - V1: 최대 3개 (InMemoryDispatcher)
  - V2: 최대 10개 (Redis MessageBus)
  - V3: 최대 50+ (PARL Mesh)
- §22.11 V1: InMemoryDispatcher / V2+: Redis MessageBus
  - 메시지 버스 아키텍처 비교
- §22.12 LOCK-AT 아키텍처 제약 17건
  - 17개 LOCK 항목 전체 목록 + 각각의 의미
- §22.13 ★Agent Profiling & Capability Registry — GAP-4
  - 에이전트 능력치 프로파일링
  - 자동 에이전트 선택 알고리즘
  - [근거: D2.0-05 ADD-027]

### 검증 체크리스트:
- [ ] Sub-Agent 8타입 모두?
- [ ] 3요소 (Identity/Capability/Policy)?
- [ ] 6가지 협업 패턴 모두?
- [ ] ★MoA 패턴 GAP-3?
- [ ] HMAC 서명?
- [ ] Delegation LOCK?
- [ ] LOCK-AT 17건?
- [ ] ★Agent Profiling GAP-4?
- [ ] 비유 설명 포함?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 500~600줄

---

## SESSION 20 — §23. PARL Agent Swarm + §24. Workflow 자동화

### 첨부할 SOT 문서 (2개)
1. `VAMOS_AGENT_TEAMS_SPEC.md` (PARL 부분)
2. `D2.0-05_VAMOS_DESIGN_2_0_AGENT_WORKFLOW.md` (§12 Workflow, DAG, SOP)

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_20.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 두 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_20.md 에 저장해주세요.

## 작성 대상 A: §23. PARL Agent Swarm — V3 대규모 에이전트

### 포함 항목:
- §23.1 50+ 에이전트 Mesh 아키텍처
  - PARL = Parallel Agent Resource Layer
  - Mesh 토폴로지: 에이전트 간 직접 통신
- §23.2 Agent Marketplace (에이전트 마켓플레이스)
  - 스킬 기반 에이전트 검색/배포
  - 커뮤니티 에이전트 등록/검증
- §23.3 Agent Specialization Protocol
  - 에이전트 특화 규칙, 도메인 전문화
- §23.4 A2A 프로토콜 (Agent-to-Agent)
  - Google A2A 호환, 표준 메시지 형식, 상호 운용성

## 작성 대상 B: §24. Workflow 자동화 시스템

### 포함 항목:
- §24.1 DAG 기반 워크플로우
  - DAG (Directed Acyclic Graph) 설명 (비유: 프로젝트 일정표)
  - 노드 = 작업, 엣지 = 의존성
- §24.2 12가지 Workflow 패턴
  - 각 패턴의 이름, 설명, 사용 시점 표
- §24.3 SOP Pattern (절차 패턴)
  - 반복 작업의 표준 운영 절차 정의
- §24.4 Trigger/Action 시스템
  - 이벤트 트리거 → 자동 액션 실행
  - 예시: 파일 변경 → 자동 테스트 → 알림
- §24.5 Agentic Coding Pattern (코딩 자동화)
  - 요구사항 → 코드 생성 → 테스트 → 리뷰 자동화 흐름
- §24.6 ★외부 Workflow 엔진 어댑터 규칙 — GAP-6
  - LangGraph LOCK (다른 프레임워크 사용 금지)
  - 외부 워크플로우 엔진 연동 시 어댑터 패턴
  - [근거: D2.0-05 §7.3]

### 검증 체크리스트:
- [ ] PARL Mesh 아키텍처?
- [ ] Agent Marketplace?
- [ ] A2A 프로토콜?
- [ ] DAG 기반 워크플로우?
- [ ] 12가지 패턴 목록?
- [ ] SOP Pattern?
- [ ] Trigger/Action?
- [ ] Agentic Coding?
- [ ] ★외부 엔진 어댑터 GAP-6?
- [ ] 비유 설명 포함?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 350~400줄

---

## SESSION 21 — §25. SDAR 자가진단 & 자동수리

### 첨부할 SOT 문서 (1개)
1. `VAMOS_SDAR_DESIGN_SPECIFICATION.md`

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_21.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_21.md 에 저장해주세요.

## 작성 대상: §25. SDAR — 자가진단 & 자동수리 시스템

### 포함해야 할 하위 섹션:
- §25.1 SDAR이란? (비유: 자동차 자가진단 시스템 — 엔진 경고등이 켜지면 원인 파악하고 간단한 것은 자동 수리)
  - Self-Directed Adaptive Reasoning
  - I-25 모듈로 구현
- §25.2 5-Layer Pipeline
  - Layer 1: Monitoring (모니터링) — 이상 감지
  - Layer 2: Diagnosis (진단) — 원인 분석
  - Layer 3: Planning (계획) — 수리 계획 수립
  - Layer 4: Execution (실행) — 수리 액션 실행
  - Layer 5: Verification (검증) — 수리 결과 확인
- §25.3 에러 분류 체계 (5가지 카테고리)
  - 성능 저하, 데이터 오류, 모듈 장애, 보안 이상, 비용 이상
- §25.4 점진적 자율성 피라미드 (AR-L0 ~ AR-L4)
  - AR-L0: 알림만 (수동)
  - AR-L1: 진단 + 제안 (반자동)
  - AR-L2: 안전한 수리 자동 실행
  - AR-L3: 복잡한 수리 자동 실행 (승인 필요)
  - AR-L4: 완전 자율 (V3 전용)
- §25.5 SDAR 7-State 상태 머신
  - IDLE→MONITORING→DIAGNOSING→PLANNING→EXECUTING→VERIFYING→RESOLVED
- §25.6 수리 액션 카탈로그
  - 재시작, 캐시 클리어, 모델 전환, 파라미터 조정, 롤백 등
- §25.7 5-Gate 통합 (SDAR와 Gate 연동)
  - SDAR 수리 액션도 5-Gate 검증 통과 필요
- §25.8 Emergency Kill Switch (긴급 중지)
  - 즉시 모든 SDAR 작업 중단
  - 트리거 조건, 복구 절차
- §25.9 보안 오류 특별 규칙 (LOCK)
  - 보안 관련 오류는 AR-L0 고정 (자동 수리 금지)
- §25.10 Self-evo 원칙 준수 (LOCK)
  - SDAR도 Self-evo 7대 불변 규칙 준수

### 검증 체크리스트:
- [ ] 5-Layer Pipeline 모두 설명?
- [ ] AR-L0~L4 자율성 피라미드?
- [ ] 7-State 상태 머신?
- [ ] 수리 액션 카탈로그?
- [ ] Kill Switch?
- [ ] 보안 오류 LOCK 규칙?
- [ ] 비유 설명 포함?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 350~400줄

---

## SESSION 22 — §26. Cloud Library + §27. RT-BNP + §28. DCL

### 첨부할 SOT 문서 (1개)
1. `VAMOS_CLOUD_LIBRARY_SPEC.md` (Cloud Library, RT-BNP, DCL 모두 포함)

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_22.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 세 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_22.md 에 저장해주세요.

## 작성 대상 A: §26. Cloud Library — 정보 수집 & 관리 시스템

### 포함 항목:
- §26.1 10-Layer 아키텍처
  - 각 레이어 이름, 역할, 입력/출력 표
- §26.2 G0~G4 5-Gate 검증 시스템
  - G0: 중복 체크, G1: 포맷 검증, G2: 신뢰도 점수, G3: 충돌 감지, G4: 최종 승인
- §26.3 평가 점수 & 소스 신뢰도 (LOCK)
  - 신뢰도 점수 산출 공식, 0.0~1.0 범위, 최소 임계값
- §26.4 LOCK 결정사항 (CLOUD_LIBRARY_SPEC §16)

## 작성 대상 B: §27. RT-BNP — 실시간 속보 파이프라인

### 포함 항목:
- §27.1 RT-BNP란? (비유: 뉴스 속보 알림 시스템)
- §27.2 뉴스 소스 Tier 분류 (TIER-0/1/2)
- §27.3 Breaking Event 분류 체계 (Level 1~5)
- §27.4 Breaking Detector 엔진
- §27.5 Fast Gate (속보 전용 간소화 검증)
- §27.6 버전별 RT-BNP 구현 범위 (V1/V2/V3)

## 작성 대상 C: §28. DCL — Domain Context Layer

### 포함 항목:
- §28.1 선택적 배경 인식 설계 원칙
- §28.2 VAMOS AI 정보 환경 6계층
- §28.3 3개 도메인 컨텍스트 채널 (Market, Tech, Academic)
- §28.4 DCL → I-2 RAG 연동 흐름

### 검증 체크리스트:
- [ ] 10-Layer 아키텍처?
- [ ] G0~G4 Gate?
- [ ] 소스 신뢰도 LOCK?
- [ ] RT-BNP Tier 분류?
- [ ] Breaking Detector?
- [ ] Fast Gate?
- [ ] DCL 6계층?
- [ ] 3채널?
- [ ] 비유 설명 포함?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 400~500줄

---

## SESSION 23 — §29. AI Investing

### 첨부할 SOT 문서 (1개)
1. `VAMOS_AI_INVESTING_SPEC.md` (핵심 섹션 발췌 — 전체 1,380줄이므로 §1~§10, §14~§17, §19 위주)

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_23.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_23.md 에 저장해주세요.

## 작성 대상: §29. AI Investing — 투자 분석 시스템

### 포함해야 할 하위 섹션:
- §29.1 시스템 개요 & 7-Layer 데이터 아키텍처 (비유: 투자 분석 회사의 부서 구조)
- §29.2 83개 데이터 소스 (P0/P1/TIER-0/TIER-1/KB) — 카테고리별 주요 소스 표
- §29.3 96개 투자 전략 (기술/퀀트/옵션/ML) — 4개 카테고리별 전략 수 및 주요 예시
- §29.4 51% Gate & 백테스팅 엔진 — 전략 신뢰도 51% 미만 → 자동 거부 (LOCK)
- §29.5 Circuit Breaker (서킷 브레이커) — 시장 급변 시 자동 분석 중단
- §29.6 법적 제약 (Wash Sale, PDT, Uptick) — 각 규제의 의미
- §29.7 데이터 스키마 (VAMOS_OHLCV_PLUS, VAMOS_EVENT) — 핵심 필드
- §29.8 Scraper Manager (17개 웹 스크래핑 대상) — rate limiting, robots.txt 준수
- §29.9 ML/AI 스택 (FinBERT, LSTM, RL) — 각 모델의 역할
- §29.10 Real-Time News 연동 (RT-BNP ↔ Investing)
- §29.11 VAMOS CORE 통합 (I-2, I-6, I-8, I-9, I-18) — 각 모듈과의 연동
- §29.12 ★Walk-Forward Validation & Z-Session — GAP-12
  - Walk-Forward 검증 방법론, Z-Session: 제로 리스크 시뮬레이션
  - [근거: AI_INVESTING_SPEC §17]
- §29.13 ★참조 플랫폼 35개 & 알려진 결함 15개 — GAP-12
  - [근거: AI_INVESTING_SPEC §19]

### 검증 체크리스트:
- [ ] 7-Layer 아키텍처?
- [ ] 83개 소스 카테고리별?
- [ ] 96개 전략 카테고리별?
- [ ] 51% Gate LOCK?
- [ ] Circuit Breaker?
- [ ] 법적 제약 3가지?
- [ ] ML 스택?
- [ ] ★Walk-Forward GAP-12?
- [ ] ★참조 플랫폼 35개 GAP-12?
- [ ] 비유 설명 포함?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 500~600줄

---

## SESSION 24 — §30. UI/UX

### 첨부할 SOT 문서 (1개)
1. `D2.0-08_VAMOS_DESIGN_2_0_UI_UX.md`

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_24.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_24.md 에 저장해주세요.

## 작성 대상: §30. UI/UX — 사용자 인터페이스

### 포함해야 할 하위 섹션:
- §30.1 설계 철학 7원칙 — 7가지 원칙 각각 설명
- §30.2 Builder View (만드는 사람용) — 개발자/관리자를 위한 상세 뷰
- §30.3 Hologram View (사용하는 사람용) — 일반 사용자를 위한 간결 뷰
- §30.4 3-Panel Layout (좌/중/우 패널) — 좌:네비게이션, 중:대화, 우:컨텍스트
- §30.5 UI 9-State 상태 머신 (S0_BOOT ~ S8_ARCHIVED) — 각 상태와 UI 표현
- §30.6 Pipeline ↔ UI 상태 매핑 — 백엔드 9-State와 UI 상태 연결 표
- §30.7 React 컴포넌트 목록 (~44개) — 카테고리별 목록
- §30.8 Custom Hooks & Zustand Stores — 주요 Hook/Store 목록
- §30.9 멀티모달 입출력 UI — 텍스트/이미지/음성/코드/차트 UI 패턴
- §30.10 Failure/Fallback UI 규칙 — 에러 시 사용자 UI 패턴
- §30.11 색상 팔레트 & 아이콘 시스템 — Primary/Secondary/Error/Warning/Success
- §30.12 CLI 인터페이스 — 커맨드라인 사용, 주요 명령어
- §30.13 접근성 (WCAG 2.1 AA) & 다국어 (i18n)
- §30.14 STEP7 UI 강화 항목 (104개) — 카테고리별 항목 수 요약
- §30.15 ★대시보드 상세 (Log/P2/Document/Innovation) — GAP-11
  - Log/P2/Document/Innovation Dashboard 각각 설명
  - [근거: D2.0-08 §12, §14]

### 검증 체크리스트:
- [ ] 7원칙?
- [ ] Builder/Hologram View?
- [ ] 3-Panel Layout?
- [ ] UI 9-State?
- [ ] React 컴포넌트 ~44개?
- [ ] 색상 팔레트?
- [ ] 접근성 WCAG?
- [ ] ★대시보드 상세 GAP-11?
- [ ] 비유 설명 포함?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 400~500줄

---

## SESSION 25 — §31. MCP + §32. 기술 스택

### 첨부할 SOT 문서 (3개)
1. `D2.0-03_VAMOS_DESIGN_2_0_BLUE_NODES.md` (MCP 부분)
2. `D2.0-04_VAMOS_DESIGN_2_0_INFRA_CORE.md`
3. `D2.1-A1_VAMOS_TECH_STACK_SPEC.md`

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_25.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 두 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_25.md 에 저장해주세요.

## 작성 대상 A: §31. MCP — Model Context Protocol

### 포함 항목:
- §31.1 MCP란? (비유: USB 포트 — 어떤 도구든 표준 규격으로 연결)
  - Anthropic이 만든 표준 프로토콜, 도구 연결 표준화
- §31.2 Streamable HTTP Transport (LOCK)
  - WebSocket 대신 HTTP 스트리밍 선택 이유
  - 이 결정은 변경 불가 (LOCK)
- §31.3 MCP 서버/클라이언트 아키텍처
  - VAMOS = MCP 클라이언트, 외부 서비스 = MCP 서버
- §31.4 MCP 외부 서버 카탈로그 (11개)
  - 각 서버 이름, 기능, V1/V2/V3 지원 여부 표
- §31.5 Dynamic Tool Registration
  - 런타임에 새로운 도구 등록/제거
- §31.6 MCP Resource System & Prompt Templates
  - Resource: 파일, DB 등 외부 리소스 접근
  - Prompt Templates: 표준 프롬프트 템플릿
- §31.7 MCP ↔ Blue Node Bridge
  - MCP 도구와 Blue Node 연결 방식
- §31.8 MCP Tool Use Optimization
  - 도구 호출 최적화 (병렬, 캐싱)

## 작성 대상 B: §32. 기술 스택 — Tech Stack

### 포함 항목:
- §32.1 V1 Stack (Local MVP)
  - Tauri 2.0 + React 18 + Python 3.11+ + SQLite + Ollama
- §32.2 V2 Stack (Pro Server)
  - + Docker + PostgreSQL + Redis + Qdrant + vLLM
- §32.3 V3 Stack (Enterprise)
  - + Kubernetes + Helm + Grafana + Loki + Prometheus
- §32.4 LLM 서빙: Ollama / vLLM / API
  - 각 서빙 방식 비교 표 (비용, 성능, 설정 난이도)
- §32.5 Brain Adapter Layer (두뇌 어댑터)
  - 다양한 LLM을 통일 인터페이스로 사용
- §32.6 HAL — Hardware Abstraction Layer
  - 하드웨어 차이를 추상화 (GPU/CPU 자동 전환)
- §32.7 프레임워크 결정: LangGraph (LOCK)
  - 왜 LangGraph인지, 대안 비교, LOCK 이유
- §32.8 프롬프트 캐싱 (50~90% 절감)
  - Anthropic/OpenAI 프롬프트 캐싱 활용
- §32.9 양자화 관리 (Q4_K_M 권장)
  - 양자화란?, Q4_K_M 선택 이유
- §32.10 Model Gateway (LiteLLM)
  - 여러 LLM API를 하나의 게이트웨이로 통합
- §32.11 Batch Processing (50% 절감)
  - 비실시간 요청 배치 처리
- §32.12 A/B Model Testing Framework
  - 모델 비교 테스트 프레임워크
- §32.13 ★MoA — Mixture of Agents 실행 패턴 — GAP-3
  - 멀티모델 병렬 실행 아키텍처
  - [근거: D2.0-04 §4.9]
- §32.14 ★Docker Sandboxing & 코드 실행 격리 — GAP-2
  - E-4와 연동, 격리 아키텍처 상세
- §32.15 ★프레임워크 패턴 참조 (Runnable Protocol) — GAP-18
  - LangChain Runnable 인터페이스 패턴
  - [근거: D2.0-04 §4.4]

### 검증 체크리스트:
- [ ] V1/V2/V3 스택 모두?
- [ ] LLM 서빙 비교?
- [ ] Brain Adapter?
- [ ] LangGraph LOCK?
- [ ] 프롬프트 캐싱/Batch 절감?
- [ ] MCP 11개 서버 카탈로그?
- [ ] Streamable HTTP LOCK?
- [ ] ★MoA 실행 GAP-3?
- [ ] ★Docker Sandbox GAP-2?
- [ ] ★Runnable Protocol GAP-18?
- [ ] 비유 설명 포함?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 500~600줄

---

## SESSION 26 — §33. 프로젝트 구조 + §34. API

### 첨부할 SOT 문서 (2개)
1. `PHASE_B1_API_IPC_SPEC.md`
2. `PHASE_B2_PROJECT_STRUCTURE.md`

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_26.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 두 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_26.md 에 저장해주세요.

## 작성 대상 A: §33. 프로젝트 구조 — Monorepo

### 포함 항목:
- §33.1 전체 디렉토리 구조 (PHASE_B2 정본)
  - 트리 형식으로 전체 구조 표시
  - 각 주요 디렉토리의 역할 설명
- §33.2 Frontend (src/) — React 18 + TypeScript
  - 주요 하위 폴더: components, hooks, stores, pages, utils
- §33.3 Rust Backend (src-tauri/) — Tauri 2.0
  - 주요 하위 폴더: commands, ipc, config
- §33.4 Python Backend (backend/) — vamos_core
  - 주요 하위 폴더: modules, agents, pipeline, memory, tools
- §33.5 Shared Types (shared/)
  - TypeScript/Python 공유 타입 정의
- §33.6 Config (config/)
  - config.toml, schema_registry.toml 위치

## 작성 대상 B: §34. API & 통신 시스템 — 88개 엔드포인트

### 포함 항목:
- §34.1 Tauri IPC 커맨드 (72개)
  - 주요 커맨드 카테고리별 목록 (대화, 프로젝트, 설정, 모듈 등)
- §34.2 Python-Rust JSON-RPC (13개)
  - Rust → Python 호출 인터페이스
- §34.3 MCP Tool Protocol (3개)
  - MCP 표준 도구 프로토콜
- §34.4 IPC Bridge (Rust ↔ Python)
  - 통신 방식: subprocess + JSON-RPC
  - 비유: 통역사 (두 언어 사이에서 번역)
- §34.5 응답 형식 표준 (trace_id 필수)
  - 모든 응답에 trace_id 포함 (추적 가능성)
  - 표준 응답 JSON 구조

### 검증 체크리스트:
- [ ] 전체 디렉토리 트리?
- [ ] Frontend/Rust/Python 각각 설명?
- [ ] 88개 엔드포인트 분류?
- [ ] Tauri IPC 72개?
- [ ] JSON-RPC 13개?
- [ ] IPC Bridge 설명?
- [ ] trace_id 표준?
- [ ] 비유 설명 포함?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 300~400줄

---

## SESSION 27 — §35. 이벤트/로깅 + §36. Configuration

### 첨부할 SOT 문서 (2개)
1. `D2.1-D2_VAMOS_SCHEMA_2_1_ORANGE_CORE.md` (EventType, FailureCode Registry)
2. `PHASE_B4_CONFIG_SCHEMA_VALIDATION.md`

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_27.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 두 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_27.md 에 저장해주세요.

## 작성 대상 A: §35. 이벤트 & 로깅 시스템

### 포함 항목:
- §35.1 EventType Registry (134개 이벤트)
  - 이벤트 네임스페이스 구조: oc.i#.*, bn.*, infra.* 등
  - 주요 이벤트 카테고리별 예시 (10개 정도)
  - 전체 134개를 나열하되, 카테고리별로 그룹화
- §35.2 FailureCode Registry (36개 에러코드)
  - 에러코드 네이밍 규칙: OC_I#_*, BN_*, SANDBOX_* 등
  - 주요 에러코드 카테고리별 목록
- §35.3 Fallback Registry (23개 대응전략)
  - 폴백 네이밍 규칙: FB_*
  - 주요 폴백 전략 목록
- §35.4 FailureCode → Fallback 매핑 (36:23, 1:N)
  - 하나의 에러코드가 여러 폴백 옵션을 가질 수 있음
  - 매핑 표 (주요 10개)
- §35.5 NEVER_AUTO 에러 자동 탐지
  - 절대 자동 처리하면 안 되는 에러 목록
  - 반드시 사용자에게 에스컬레이션
- §35.6 로깅 스택 (V1:JSONL / V2:Loki-lite / V3:Loki+Grafana)
  - 버전별 로깅 방식 비교 표

## 작성 대상 B: §36. Configuration 시스템

### 포함 항목:
- §36.1 설정 계층: .env → config.toml → DB Runtime
  - 우선순위: DB Runtime > config.toml > .env
- §36.2 config.toml 전체 섹션 (17개)
  - 각 섹션 이름과 역할 표
- §36.3 LOCK / FREEZE 값 목록
  - 변경 불가 설정값 전체 목록
- §36.4 VAL-001~VAL-010 검증 규칙
  - 설정값 유효성 검증 규칙 10개
- §36.5 schema_registry.toml (단일 참조점)
  - 모든 스키마의 단일 등록점

### 검증 체크리스트:
- [ ] 134개 이벤트 카테고리별?
- [ ] 36개 에러코드?
- [ ] 23개 폴백?
- [ ] FailureCode→Fallback 매핑?
- [ ] NEVER_AUTO 목록?
- [ ] 로깅 스택 V1/V2/V3?
- [ ] config.toml 17섹션?
- [ ] LOCK/FREEZE 목록?
- [ ] VAL-001~010?
- [ ] 비유 설명 포함?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 400~500줄

---

## SESSION 28 — §37. 테스트 + §38. CI/CD

### 첨부할 SOT 문서 (2개)
1. `PHASE_B5_TEST_STRATEGY.md`
2. `PHASE_B6_CI_CD_PIPELINE.md`

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_28.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 두 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_28.md 에 저장해주세요.

## 작성 대상 A: §37. 테스트 전략 (~128개 테스트)

### 포함 항목:
- §37.1 테스트 피라미드 (Unit/Integration/E2E)
  - 비유: 건물 검사 (기초→구조→완성 순서)
  - 각 레벨의 역할, 비율 (70/20/10)
- §37.2 V0~V1 기본 테스트 (~85개)
  - CORE 모듈 테스트, 통합 테스트
- §37.3 V2 COND 모듈 테스트 (~30개)
  - 조건부 모듈 활성화 테스트
- §37.4 V3 EXP 모듈 테스트 (~13개)
  - 실험 모듈 테스트
- §37.5 AC 매핑 (50 AC → 79 테스트)
  - Acceptance Criteria와 테스트 케이스 매핑 표
- §37.6 상세 테스트 케이스
  - T-VAL: 설정 검증 테스트
  - T-SDAR: SDAR 자동수리 테스트
  - T-HMAC: HMAC 인증 테스트
  - T-GUARD: Guardrails 테스트
  - T-GDPR: 개인정보보호 테스트
  - T-AC: 접근제어 테스트
  - T-ARCH: 아키텍처 테스트

## 작성 대상 B: §38. CI/CD 파이프라인

### 포함 항목:
- §38.1 GitHub Actions 워크플로우 (~14개)
  - 각 워크플로우 이름, 트리거, 역할 표
- §38.2 브랜치 전략 (main/develop/feature/hotfix)
  - Git Flow 기반 전략 설명
- §38.3 8-Stage 파이프라인
  - Stage 1~8 각각의 이름, 역할, 실패 시 행동
- §38.4 보안 스캔 (SAST, Dependency Audit)
  - SAST: 정적 코드 분석 도구
  - Dependency Audit: 의존성 취약점 검사

### 검증 체크리스트:
- [ ] 테스트 피라미드 (Unit/Integration/E2E)?
- [ ] 128개 테스트 카테고리별?
- [ ] AC 매핑 (50 AC → 79 테스트)?
- [ ] 상세 케이스 (T-VAL~T-ARCH)?
- [ ] GitHub Actions ~14개?
- [ ] 브랜치 전략?
- [ ] 8-Stage 파이프라인?
- [ ] 보안 스캔?
- [ ] 비유 설명 포함?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 350~450줄

---

## SESSION 29 — §39. 배포 + §40. 운영

### 첨부할 SOT 문서 (2개)
1. `PHASE_B7_DEPLOYMENT_STRATEGY.md`
2. `VAMOS_구현가이드_PART2_구현단계.md` (§6.12 운영 부분 발췌)

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_29.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 두 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_29.md 에 저장해주세요.

## 작성 대상 A: §39. 배포 전략

### 포함 항목:
- §39.1 V1: 로컬 (Windows/WSL)
  - 설치 방법, 필요 사양, 시작 명령어
- §39.2 V2: Docker Compose
  - docker-compose.yml 구성, 서비스 목록
  - 시작/중지 명령어
- §39.3 V3: Kubernetes (Helm Chart)
  - Helm chart 구성, values.yaml 주요 설정
- §39.4 Blue-Green 배포
  - Blue-Green 방식 설명 (비유: 무대 교체)
  - 다운타임 제로 배포 절차
- §39.5 V3 인프라 대안: Hetzner + RunPod
  - 비용 효율적인 GPU 서버 선택지
  - Hetzner (CPU/Storage) + RunPod (GPU) 조합

## 작성 대상 B: §40. 운영 가이드

### 포함 항목:
- §40.1 모니터링 전략 (V1/V2/V3)
  - V1: 로컬 로그 + JSONL
  - V2: Loki-lite + 기본 대시보드
  - V3: Prometheus + Grafana + Loki + AlertManager
- §40.2 백업 & 복구 (RPO/RTO)
  - RPO (Recovery Point Objective): 최대 데이터 손실 허용량
  - RTO (Recovery Time Objective): 최대 복구 시간
- §40.3 인시던트 대응 프로세스
  - 감지 → 분류 → 대응 → 복구 → 사후분석 (5단계)
- §40.4 알림 체계
  - 심각도별 알림 채널 (Critical→SMS, Warning→Slack, Info→Dashboard)
- §40.5 롤백 프로세스
  - 즉시 롤백 vs 점진적 롤백
- §40.6 헬스체크
  - /health 엔드포인트, 각 서비스 상태 확인
- §40.7 로그 보존 정책
  - V1: 7일, V2: 30일, V3: 90일 (LOCK)
- §40.8 비용 초과 대응
  - 경고 → Downshift → 서비스 중단 흐름
- §40.9 SDAR 수동 폴백
  - 자동 수리 실패 시 수동 개입 절차

### 검증 체크리스트:
- [ ] V1/V2/V3 배포 모두?
- [ ] Blue-Green 배포?
- [ ] Hetzner + RunPod?
- [ ] 모니터링 V1/V2/V3?
- [ ] RPO/RTO?
- [ ] 인시던트 5단계?
- [ ] 알림 체계?
- [ ] 롤백 프로세스?
- [ ] 헬스체크?
- [ ] 로그 보존 LOCK?
- [ ] 비유 설명 포함?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 350~450줄

---

## SESSION 30 — §41. Self-Evolution + §42. 버전 로드맵

### 첨부할 SOT 문서 (4개)
1. `D2.0-07_VAMOS_DESIGN_2_0_SAFETY_COST_APPROVAL.md` (Self-evo 부분)
2. `BASE-1.3_VAMOS_RULE_1.3_BASE.md`
3. `PLAN-3.0_최종완성본.md` (V0~V3 로드맵)
4. `VAMOS_구현가이드_PART2_구현단계.md` (§1.3 R1~R11 발췌)

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_30.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 두 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_30.md 에 저장해주세요.

## 작성 대상 A: §41. Self-Evolution — 자기 진화 시스템

### 포함 항목:
- §41.1 자기 진화란? (비유: 스스로 업그레이드하는 소프트웨어)
  - AI가 자기 자신을 개선하는 시스템
- §41.2 변경 가능한 6가지 영역
  - 프롬프트 템플릿, 라우팅 가중치, 캐시 정책, 도구 파라미터, 검색 파라미터, 스킬 라이브러리
- §41.3 변경 불가 7가지 영역 (LOCK)
  - 비용 상한, 승인 규칙, 보안 정책, RBAC, Gate 우선순위, 9-State, Decision Lock
- §41.4 롤백 정책
  - 스냅샷 기반 롤백, 이상 탐지 시 자동 롤백, 재적용 잠금
- §41.5 Constitutional AI + DPO (피드백 학습)
  - Constitutional AI: 헌법 기반 자기 제한
  - DPO (Direct Preference Optimization): 사용자 선호 학습
- §41.6 Red Teaming / Bias Detection / Watermarking
  - Red Teaming: 적대적 테스트
  - Bias Detection: 편향 감지
  - Watermarking: AI 출력물 워터마크
- §41.7 Hallucination Detection (NLI 기반)
  - Natural Language Inference로 환각 탐지
- §41.8 ★구현 운영 규칙 R1~R11 & 세션 관리 — GAP-13
  - R1~R11 각 규칙 상세 설명
  - 세션 관리 규칙
  - [근거: PART2 §1.3]
- §41.9 ★Adaptive Thinking — 난이도별 사고 깊이 — GAP-13
  - 쉬운 질문 → 빠른 응답 (S7B-001)
  - 어려운 질문 → 깊은 사고 (Chain-of-Thought)
  - 난이도 판별 기준

## 작성 대상 B: §42. 버전 로드맵 — V0 → V1 → V2 → V3

### 포함 항목:
- §42.1 V0: Scaffold (1~2주)
  - 프로젝트 구조 생성, 기본 설정, 5개 CORE 모듈 스텁
- §42.2 V1: Operational MVP (14~16주)
  - 32개 모듈 활성, 로컬 실행, 기본 기능 완성
- §42.3 V2: Pro Server (11~13주)
  - 42개 모듈, Docker 배포, 서버 기능 추가
- §42.4 V3: Enterprise (12~16주)
  - 81개 모듈, K8s 배포, 완전체
- §42.5 버전 전환 GO/NO-GO 체크리스트
  - V0→V1, V1→V2, V2→V3 각 전환 조건 표
- §42.6 마이그레이션 전략 (V1→V2→V3)
  - 데이터 마이그레이션, 설정 마이그레이션
- §42.7 ★버전 진입 준비 체크리스트 & Readiness — GAP-15
  - IMPL_READINESS 가이드 참조
  - 각 버전 진입 전 체크 항목
  - [근거: IMPL_READINESS 3개 문서]

### 검증 체크리스트:
- [ ] 6가지 변경 가능 영역?
- [ ] 7가지 변경 불가 LOCK?
- [ ] 롤백 정책?
- [ ] Constitutional AI + DPO?
- [ ] ★R1~R11 규칙 GAP-13?
- [ ] ★Adaptive Thinking GAP-13?
- [ ] V0~V3 로드맵 모두?
- [ ] GO/NO-GO 체크리스트?
- [ ] ★Readiness GAP-15?
- [ ] 비유 설명 포함?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 450~550줄

---

## SESSION 31 — §43. V2 COND 확장 모듈 106개

### 첨부할 SOT 문서 (1개)
1. `VAMOS_구현가이드_PART2_구현단계.md` (§V2-Phase2 COND 확장 부분 발췌)

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_31.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_31.md 에 저장해주세요.

## 작성 대상: §43. V2 COND 확장 모듈 (106개)

### 포함해야 할 하위 섹션:
- §43.1 CAT-A: AI/ML 엔진 (13개)
  - 각 모듈 이름, 한줄 설명, 활성 조건
- §43.2 CAT-B: 지식관리 (13개)
  - 각 모듈 이름, 한줄 설명, 활성 조건
- §43.3 CAT-C: 운영/인프라 (53개)
  - 각 모듈 이름, 한줄 설명, 활성 조건
  - 가장 많은 카테고리 — 주요 모듈 10개 상세 + 나머지 표
- §43.4 CAT-D: 미디어/생성 (8개)
  - 각 모듈 이름, 한줄 설명, 활성 조건
- §43.5 CAT-E: 교육/학습 (7개)
  - 각 모듈 이름, 한줄 설명, 활성 조건
- §43.6 CAT-F: 웰빙/건강 (8개)
  - 각 모듈 이름, 한줄 설명, 활성 조건
- §43.7 CAT-G: 외부통합 확장 (4개)
  - 각 모듈 이름, 한줄 설명, 활성 조건

### 공통 규칙:
- COND 모듈 활성화 조건: config.toml에서 enable=true
- 비활성 시 메모리/CPU 사용 제로
- 공통 Runnable 인터페이스 준수

### 검증 체크리스트:
- [ ] 7개 카테고리 모두?
- [ ] 총 106개 모듈 전부 목록?
- [ ] 각 모듈 이름 + 한줄 설명?
- [ ] 활성화 조건?
- [ ] config 키 설명?
- [ ] 비유 설명 포함?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 300~400줄

---

## SESSION 32 — §44. STEP7 AI 기술 강화 16개 카테고리

### 첨부할 SOT 문서 (5개, 분할 첨부)
> ⚠️ STEP7 파일이 크므로 3회로 분할 가능:
> - 1차: STEP7_PART_A~B (Cat-A~B)
> - 2차: STEP7_PART_C~E + STEP7_PART_F~J (Cat-C~J)
> - 3차: STEP7_PART_K~P (Cat-K~P)
> 또는 핵심만 발췌하여 1회로 진행

1. `STEP7_PART_A_B_S7A_S7B_001_020_기초강화_대화프로세스.md`
2. `STEP7_PART_C_S7C_001_060_UI_UX_전수비교.md`
3. `STEP7_PART_D_S7D_001_015_메모리_저장소_아키텍처.md`
4. `STEP7_PART_E_S7E_001_050_보안_안전_거버넌스.md`
5. `STEP7_PART_F_to_P_S7F_to_S7P_인프라_벤치마크_비즈니스_기타.md`

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_32.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_32.md 에 저장해주세요.

## 작성 대상: §44. STEP7 — AI 기술 강화 16개 카테고리 (A~P)

각 카테고리에 대해 아래 형식으로 작성:
1. 카테고리 이름 (영문 + 한글)
2. 항목 수 (예: S7A-001~010 = 10개)
3. 핵심 내용 요약 (5~10줄)
4. 주요 항목 3~5개 상세 설명
5. VAMOS 모듈/시스템과의 연동 관계

### 대상 카테고리 (16개 전부):
- §44.1 Cat-A: 기초 강화 (S7A-001~010)
  - 기본 대화 품질, 컨텍스트 이해, 응답 정확도
- §44.2 Cat-B: 대화/프로세스 (S7B-001~010)
  - Adaptive Thinking, 멀티턴 대화, 프로세스 최적화
- §44.3 Cat-C: UI/UX 전수 비교 (S7C-001~060)
  - 60개 UI 항목 경쟁사 비교, 개선 방안
- §44.4 Cat-D: 메모리/저장소 아키텍처 (S7D-001~015)
  - 메모리 계층 최적화, 저장소 설계
- §44.5 Cat-E: 보안/안전/거버넌스 (S7E-001~050)
  - 보안 강화, 프라이버시, 감사, 컴플라이언스
- §44.6 Cat-F: 인프라/배포/MLOps (S7F-001~020)
  - 인프라 최적화, MLOps 파이프라인
- §44.7 Cat-G: 벤치마크/평가/품질보증 (S7G-001~015)
  - 성능 벤치마크, 품질 메트릭
- §44.8 Cat-H: 비즈니스모델/시장전략 (S7H-001~010)
  - 수익 모델, 시장 진입 전략
- §44.9 Cat-I: AI Investing 보강 (S7I-001~020)
  - 투자 분석 기능 강화
- §44.10 Cat-J: 멀티모달/생성처리 (S7J-001~015)
  - 이미지/음성/영상 처리 강화
- §44.11 Cat-K: 에이전트/프로토콜/상호운용 (S7K-001~015)
  - MCP, A2A, 에이전트 프로토콜
- §44.12 Cat-L: 개발자도구/API/SDK (S7L-001~010)
  - 개발자 경험 개선, API 확장
- §44.13 Cat-M: PKM/지식관리 (S7M-001~010)
  - Personal Knowledge Management
- §44.14 Cat-N: 워크플로우/자동화/RPA (S7N-001~010)
  - 업무 자동화, RPA 연동
- §44.15 Cat-O: 교육/학습/자기개발 (S7O-001~010)
  - 학습 도우미, 자기개발 지원
- §44.16 Cat-P: 건강/웰니스/감성AI (S7P-001~010)
  - 건강 관리, 감성 인식

### 검증 체크리스트:
- [ ] 16개 카테고리 모두?
- [ ] 각 카테고리 항목 수?
- [ ] 핵심 내용 요약?
- [ ] 주요 항목 3~5개 상세?
- [ ] VAMOS 모듈 연동 관계?
- [ ] 비유 설명 포함?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 500~600줄

---

## SESSION 33 — §45~49. 부록 (스키마/의존성/정본맵/용어/FAQ)

### 첨부할 SOT 문서 (4개)
1. `D2.1-D1_VAMOS_SCHEMA_INDEX.md` (또는 D2.1 시리즈 요약)
2. `PHASE_B3_DEPENDENCY_PACKAGES.md`
3. `MASTER_SPEC.md` (정본 맵, DEC 인덱스)
4. `VAMOS_BEGINNER_GUIDE.md` (용어집, FAQ)

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_33.md
```

### 프롬프트
```
[시스템 지시]

첨부된 SOT 문서를 기반으로 아래 다섯 섹션의 내용을 작성해주세요.
결과물은 D:\VAMOS\docs\guides\sections\session_33.md 에 저장해주세요.

## 작성 대상 A: §45. 스키마 정의 전체 목록 (D2.1-D1~D8)

### 포함 항목:
- §45.1 D2.1-D2: ORANGE CORE 스키마 — 주요 Pydantic 모델 목록
- §45.2 D2.1-D3: BLUE NODES 스키마 — NodeCapabilityProfile 등
- §45.3 D2.1-D4: INFRA CORE 스키마 — ToolSpec, BrainConfig 등
- §45.4 D2.1-D5: AGENT WORKFLOW 스키마 — AgentMessage, DAGNode 등
- §45.5 D2.1-D6: STORAGE & MEMORY 스키마 — MemoryEntry, ChunkMetadata 등
- §45.6 D2.1-D7: SAFETY/COST/APPROVAL 스키마 — GateResult, CostRecord 등
- §45.7 D2.1-D8: UI/UX 스키마 — UIState, ComponentSpec 등
- 각 그룹별 주요 스키마 5개씩 (필드, 타입, 설명) 표

## 작성 대상 B: §46. 의존성 & 패키지 목록 (PHASE_B3)

### 포함 항목:
- §46.1 Python 패키지 (pyproject.toml) — 주요 패키지 + 버전 제약
- §46.2 Rust 크레이트 (Cargo.toml) — 주요 크레이트 + 버전
- §46.3 Node 패키지 (package.json) — 주요 패키지 + 버전

## 작성 대상 C: §47. 정본 문서 맵 & 우선순위

### 포함 항목:
- §47.1 SOT 68개 문서 전체 인덱스 — 파일명, 역할, 정본 범위
- §47.2 문서 권위 체계 (RULE > PLAN > DESIGN > 스키마)
- §47.3 SOURCE_CONFLICT 전수 인덱스 — 문서 간 충돌 목록
- §47.4 LOCK / FREEZE 값 전체 레지스트리
- §47.5 ★DEC 결정사항 통합 인덱스 (DEC-001~DEC-017+) — GAP-14
  - 모든 DEC 결정사항 목록 + 관련 SOT
  - [근거: MASTER_SPEC §17]
- §47.6 ★ADD-xxx 항목 전수 인덱스 & 매핑 — GAP-17
  - D2.0-01~08에 산재한 ADD-xxx 항목 통합 인덱스
  - 각 ADD 항목의 상태 (구현/미구현)

## 작성 대상 D: §48. 용어집 (Glossary)

### 포함 항목:
- VAMOS 핵심 용어 50개 이상
- 각 용어: 영문, 한글 설명, 관련 섹션 번호

## 작성 대상 E: §49. 자주 묻는 질문 (FAQ)

### 포함 항목:
- 초보자가 자주 묻는 질문 20개
- Q&A 형식, 관련 섹션 링크 포함
- 예: "VAMOS AI를 사용하려면 GPU가 필요한가요?", "V1부터 시작해도 되나요?" 등

### 검증 체크리스트:
- [ ] 스키마 7그룹 모두?
- [ ] 패키지 목록 (Python/Rust/Node)?
- [ ] SOT 68개 인덱스?
- [ ] LOCK/FREEZE 레지스트리?
- [ ] ★DEC 통합 인덱스 GAP-14?
- [ ] ★ADD 인덱스 GAP-17?
- [ ] 용어집 50개+?
- [ ] FAQ 20개?
- [ ] 근거 SOT 참조 표기?
```

### 예상 결과 분량: 약 500~600줄

---

## SESSION 34 — 최종 검토 (검토 에이전트)

### 첨부할 문서 (1개)
1. 완성된 `VAMOS_AI_전체해설_초보자가이드.md` 전체

### 출력 저장 경로
```
D:\VAMOS\docs\guides\sections\session_34_review.md
```

### 프롬프트
```
[최종 검토 에이전트]

당신은 VAMOS AI 문서 품질 검토 전문가입니다.
첨부된 "VAMOS AI 전체 해설 초보자 가이드" 문서에 대해 아래 5가지 차원의 검토를 수행하세요.
결과물은 D:\VAMOS\docs\guides\sections\session_34_review.md 에 저장해주세요.

## 검토 1: 완전성 (Completeness)
- 목차의 모든 섹션(49개)이 실제 내용으로 채워져 있는가?
- SOT 68개 문서의 핵심 내용이 빠짐없이 반영되었는가?
- 81개 모듈 전체가 설명되어 있는가?
- 18개 Gap 보완 항목(★표시) 모두 작성되었는가?
- 106개 COND 확장 모듈 전부 목록되었는가?

## 검토 2: 정확성 (Accuracy)
- SOT 문서의 원본과 일치하는가?
- LOCK/FREEZE 값이 정확한가?
- 숫자 (모듈 수, 이벤트 수, 엔드포인트 수 등)가 정확한가?
- 버전별 (V0/V1/V2/V3) 정보가 올바른가?
- 비용 상한 (V1:₩40K, V2:₩93K, V3:₩266K) 정확한가?

## 검토 3: 초보자 적합성 (Beginner-friendliness)
- 기술 용어에 괄호 설명이 있는가?
- 비유가 적절한가?
- 설명 순서가 논리적인가 (기초 → 심화)?
- 핵심 요약(3줄)이 각 섹션에 있는가?

## 검토 4: 일관성 (Consistency)
- 용어 사용이 전체적으로 통일되어 있는가?
- 형식 (표, 코드블록, 제목 수준)이 일관되는가?
- 크로스 참조가 올바른가?
- 섹션 번호가 목차와 일치하는가?

## 검토 5: SOT 크로스체크
- 크로스체크 매핑 테이블의 모든 SOT 문서가 실제 참조되었는가?
- SOURCE_CONFLICT 항목이 올바르게 처리되었는가?
- 정본 우선순위 (RULE > PLAN > DESIGN > 스키마)가 준수되었는가?

## 출력 형식:
각 차원별로:
- PASS / FAIL 판정
- 발견된 문제 목록 (있으면)
- 수정 제안
- 심각도 (CRITICAL / HIGH / MEDIUM / LOW)

마지막에 전체 종합 점수 (100점 만점) 및 종합 판정 제공.
```

### 예상 결과 분량: 약 200~300줄

---

## SESSION 35 — 자동 조립 (Auto-Assembly)

### 설명
모든 세션(01~33) 결과물을 `VAMOS_AI_전체해설_초보자가이드.md`에 자동으로 조립합니다.

### 출력 저장 경로
```
D:\VAMOS\docs\guides\VAMOS_AI_전체해설_초보자가이드.md (덮어쓰기)
```

### 프롬프트
```
[자동 조립 에이전트]

당신은 문서 조립 전문가입니다.
아래 규칙에 따라 모든 세션 결과물을 하나의 완성 문서로 조립하세요.

## 입력 파일들
D:\VAMOS\docs\guides\sections\ 폴더의 모든 session_XX.md 파일들:
- session_01.md ~ session_33.md (총 33개)

## 출력 파일
D:\VAMOS\docs\guides\VAMOS_AI_전체해설_초보자가이드.md

## 조립 규칙:
1. 기존 전체해설 초보자가이드의 **헤더 (1~8줄)** 유지
2. 기존 **목차 (12~549줄)** 유지
3. 목차 아래에 "---" 구분선 추가
4. session_01.md ~ session_33.md 내용을 **섹션 번호 순서대로** 삽입
   - 각 session 파일의 frontmatter (---session:XX--- 블록) 제거
   - 각 session 파일의 내용만 추출하여 순서대로 배치
5. 각 섹션 사이에 "---" 구분선 추가
6. 마지막에 기존 **크로스체크 커버리지 매핑 테이블** 유지
7. 문서 버전을 v2.0.0으로 업데이트
8. 작성일을 조립 실행일로 업데이트

## 조립 순서 (session → section 매핑):
| Session | Section(s) |
|---------|-----------|
| 01 | §1 |
| 02 | §2 |
| 03 | §3 |
| 04 | §4, §5 |
| 05 | §6 |
| 06 | §7 (I-1~I-8) |
| 07 | §7 (I-9~I-17) |
| 08 | §7 (I-18~I-25) |
| 09 | §8 |
| 10 | §9, §10 |
| 11 | §11, §12 |
| 12 | §13, §14 |
| 13 | §15 |
| 14 | §16 |
| 15 | §17 |
| 16 | §18 |
| 17 | §19, §20 |
| 18 | §21 |
| 19 | §22 |
| 20 | §23, §24 |
| 21 | §25 |
| 22 | §26, §27, §28 |
| 23 | §29 |
| 24 | §30 |
| 25 | §31, §32 |
| 26 | §33, §34 |
| 27 | §35, §36 |
| 28 | §37, §38 |
| 29 | §39, §40 |
| 30 | §41, §42 |
| 31 | §43 |
| 32 | §44 |
| 33 | §45~§49 |

## 검증:
조립 완료 후 아래 확인:
- [ ] 49개 섹션 모두 내용 존재?
- [ ] 목차의 앵커 링크가 본문과 일치?
- [ ] 섹션 번호 순서 올바름?
- [ ] 중복 내용 없음?
- [ ] 크로스체크 매핑 테이블 유지?
```

### 예상 결과 분량: 전체 문서 약 8,000~12,000줄

---

## 진행 추적표

| 세션 | 섹션 | 출력 파일 | 상태 | 완료일 |
|------|------|----------|------|--------|
| 01 | §1 VAMOS AI란 | `session_01.md` | ⬜ 미시작 | |
| 02 | §2 아키텍처 | `session_02.md` | ⬜ 미시작 | |
| 03 | §3 파이프라인 | `session_03.md` | ⬜ 미시작 | |
| 04 | §4-5 Gate+Decision | `session_04.md` | ⬜ 미시작 | |
| 05 | §6 모듈 개요 | `session_05.md` | ⬜ 미시작 | |
| 06 | §7 I-1~I-8 | `session_06.md` | ⬜ 미시작 | |
| 07 | §7 I-9~I-17 | `session_07.md` | ⬜ 미시작 | |
| 08 | §7 I-18~I-25 | `session_08.md` | ⬜ 미시작 | |
| 09 | §8 E-Series | `session_09.md` | ⬜ 미시작 | |
| 10 | §9-10 S/A-Series | `session_10.md` | ⬜ 미시작 | |
| 11 | §11-12 B/C-Series | `session_11.md` | ⬜ 미시작 | |
| 12 | §13-14 D/EVX-Series | `session_12.md` | ⬜ 미시작 | |
| 13 | §15 도메인 | `session_13.md` | ⬜ 미시작 | |
| 14 | §16 메모리 | `session_14.md` | ⬜ 미시작 | |
| 15 | §17 RAG | `session_15.md` | ⬜ 미시작 | |
| 16 | §18 보안 | `session_16.md` | ⬜ 미시작 | |
| 17 | §19-20 RBAC/비용 | `session_17.md` | ⬜ 미시작 | |
| 18 | §21 승인 | `session_18.md` | ⬜ 미시작 | |
| 19 | §22 Agent Teams | `session_19.md` | ⬜ 미시작 | |
| 20 | §23-24 PARL/Workflow | `session_20.md` | ⬜ 미시작 | |
| 21 | §25 SDAR | `session_21.md` | ⬜ 미시작 | |
| 22 | §26-28 Cloud/RT-BNP/DCL | `session_22.md` | ⬜ 미시작 | |
| 23 | §29 AI Investing | `session_23.md` | ⬜ 미시작 | |
| 24 | §30 UI/UX | `session_24.md` | ⬜ 미시작 | |
| 25 | §31-32 MCP/Tech Stack | `session_25.md` | ⬜ 미시작 | |
| 26 | §33-34 구조/API | `session_26.md` | ⬜ 미시작 | |
| 27 | §35-36 이벤트/Config | `session_27.md` | ⬜ 미시작 | |
| 28 | §37-38 테스트/CI-CD | `session_28.md` | ⬜ 미시작 | |
| 29 | §39-40 배포/운영 | `session_29.md` | ⬜ 미시작 | |
| 30 | §41-42 진화/로드맵 | `session_30.md` | ⬜ 미시작 | |
| 31 | §43 COND 확장 106개 | `session_31.md` | ⬜ 미시작 | |
| 32 | §44 STEP7 | `session_32.md` | ⬜ 미시작 | |
| 33 | §45-49 부록 | `session_33.md` | ⬜ 미시작 | |
| 34 | 최종 검토 | `session_34_review.md` | ⬜ 미시작 | |
| 35 | 자동 조립 | 전체해설가이드 덮어쓰기 | ⬜ 미시작 | |

---

## 주의사항

1. **세션 32 (STEP7)**은 SOT 문서가 크므로 3회로 분할 가능 (A-B / C-E / F-P)
2. **세션 23 (AI Investing)**은 AI_INVESTING_SPEC이 1,380줄이므로 핵심만 발췌 첨부
3. 각 세션 결과물은 반드시 **지정된 출력 경로**에 저장
4. SESSION 35 (자동 조립)을 실행하면 모든 결과물이 전체해설 가이드에 **자동 반영**
5. SESSION 34 (최종 검토) 후 발견된 문제는 해당 세션을 다시 실행하여 수정
6. 수동 복사-붙여넣기 불필요 — 자동 조립으로 대체
7. 모든 세션에 **스킬 에이전트 프롬프트**(사전 준비 §4)를 반드시 먼저 입력
8. 세션 완료 시 **진행 추적표** 상태를 ✅ 완료로 업데이트
