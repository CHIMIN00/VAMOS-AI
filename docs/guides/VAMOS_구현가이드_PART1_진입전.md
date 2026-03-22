# VAMOS AI 구현 가이드 — PART 1: 구현단계 진입전

> **버전**: v12.2.0 | **작성일**: 2026-02-24 | **최종갱신**: 2026-03-02
> **목적**: VAMOS AI 구현 착수 전 모든 오류 해결, 사용자 준비사항, 미결정사항, AI 코딩 방법론 총정리
> **정본 근거**: `STEP6_pipeline/output/updated/` 43개 산출물 전수 분석 기반 (3차 정밀 스캔 반영) (4차 검증 반영)
> **정본 우선순위**: RULE 1.3 > PLAN 3.0 > DESIGN 2.0 LOCK > DESIGN 본문 > 스키마/TECH_STACK

---

# 목차

- [A. 산출물 오류 총정리 — 수정/제거/대체/추가](#a-산출물-오류-총정리)
- [B. 사용자 직접 준비사항](#b-사용자-직접-준비사항)
- [C. 미결정사항 + 최종 결정 필요 항목](#c-미결정사항--최종-결정-필요-항목)
- [D. AI와 함께 VAMOS를 코딩하는 방법론](#d-ai와-함께-vamos를-코딩하는-방법론)
- [E. 진입전 최종 체크리스트](#e-진입전-최종-체크리스트)

---

# A. 산출물 오류 총정리

> 43개 산출물 파일에서 발견된 모든 오류를 **수정(FIX)**, **제거(DEL)**, **대체(REP)**, **추가(ADD)** 4가지 액션으로 분류합니다.

---

## A.1 BLOCKER — 구현 진입 불가 (14건)

> 아래 14건을 해결하지 않으면 V0 스캐폴딩조차 시작할 수 없습니다.

### BLOCKER-1: PLAN 3.0 I-모듈 번호 완전 불일치
- **액션**: FIX
- **파일**: `PLAN-3.0_VAMOS_PLAN_3_0_최종완성본.md` §2.3
- **문제**: PLAN은 I-1~I-21(구 번호 체계)을 사용하지만 정본(DESIGN 2.0 / D2.0-01 §5.6)은 I-1~I-25(신 번호 체계). I-7~I-10 역할 매핑이 완전히 다름. I-11, I-12, I-13, I-17, I-20 누락. I-22~I-25 미언급.
- **정본 기준**: D2.0-01 §5.6 I-Series 정본 인덱스 (25개)
- **수정 내용**:
  1. PLAN-3.0 §2.3에 경고 배너 추가: `⚠️ 본 번호는 PLAN 2.0 기준. DESIGN 2.0 §5.6이 정본`
  2. I-모듈 목록을 정본 25개로 교체
  3. P7-MOD 구현 우선순위도 25개 기준으로 재계산

### BLOCKER-2: P0 활성 도메인 리스트 순환 참조
- **액션**: ADD
- **파일**: `PLAN-3.0_VAMOS_PLAN_3_0_최종완성본.md` + `D2.0-03` §7
- **문제**: D2.0-03 §7에서 "P0 구체 리스트는 PLAN 3.0 근거로만" → PLAN 3.0은 P0/P1/P2를 정식 정의하지 않음 → 교착 상태
- **정본 기준**: D2.0-03 §3.1 원칙 (Wide P0 + Gate Control) + RULE 1.3
- **수정 내용**:
  1. PLAN-3.0에 공식 P0/P1/P2 분류 섹션 추가:
     - P0 (기본 활성): Dev, Research, Productivity
     - P1 (1회 승인): Content, Quant
     - P2 (세션별 승인 + 자동 OFF): Trading, Investing
  2. D2.0-03 §7 잠금 보류 해제 → PLAN 3.0 근거 확보 처리

### BLOCKER-3: Storage 이벤트 코드 미등록
- **액션**: ADD
- **파일**: `D2.1-D2_D2_SCHEMA_ORANGE_CORE.md` EventTypeRegistry
- **문제**: D2.0-06 §8에서 정의한 storage.* 이벤트 5개가 D2.1-D2 중앙 레지스트리에 없음
- **수정 내용**: D2.1-D2 EventTypeRegistry에 추가:
  ```
  storage.policy.checked
  storage.memory.write.requested
  storage.memory.write.completed
  storage.vector.insert.denied
  storage.pii.longterm.denied
  ```
  FailureCodeRegistry 추가: `PII_LONGTERM_DENIED`
  FallbackRegistry 추가: `FB_DENY_STORAGE`

### BLOCKER-4: 다운시프트 임계값 자기 모순
- **액션**: FIX
- **파일**: `D2.0-07` §9 (1144줄)
- **문제**: §4.2에서 "80%/100% LOCK"이라 하면서 §9에서 "80%는 예시일 뿐"이라 함
- **수정 내용**: §9 문구를 "80%/100%는 §4.2에서 LOCK 확정. 운영 조정은 Approval Gate 승인 필수"로 통일

### BLOCKER-5: Node.js vs Python 아키텍처 충돌
- **액션**: FIX
- **파일**: `VAMOS_STEP7_F-I_상세명세서.md` S7F-012
- **문제**: STEP7이 "Node.js + LangGraph.js" 아키텍처를 제시하지만, 정본(PLAN 3.0)은 "Python + LangGraph(Python)"
- **정본 기준**: CLAUDE.md §1 통신 계층 (React ↔ Tauri IPC ↔ Rust ↔ JSON-RPC ↔ Python)
- **수정 내용**: STEP7 S7F-012에 오버라이드 배너 추가: `⚠️ PLAN-3.0 정본: Python backend. 본 항목은 대안 참조로 강등`

### BLOCKER-6: 디렉토리 구조 충돌
- **액션**: FIX
- **파일**: `VAMOS_STEP7_F-I_상세명세서.md`
- **문제**: STEP7은 `~/vamos/config/settings.yaml`(홈 기반), PHASE_B2 정본은 monorepo + `config.v1.toml`
- **정본 기준**: PHASE_B2 monorepo 구조
- **수정 내용**: STEP7에 주석 추가: `⚠️ 정본: PHASE_B2 monorepo 구조. 본 경로는 참조용`

### BLOCKER-7: Config 파일 포맷 (YAML vs TOML)
- **액션**: FIX
- **파일**: `VAMOS_STEP7_F-I_상세명세서.md`
- **문제**: STEP7에서 `.yaml` 4곳 이상 사용 → 정본은 `config.toml` (Pydantic v2 + tomli LOCK)
- **수정 내용**: STEP7 전체에서 `.yaml` 참조에 `⚠️ 정본: .toml (PHASE_B4 LOCK)` 배너 추가

### BLOCKER-8: 스키마 버전 불일치
- **액션**: FIX
- **파일**: D2.1-D1 ~ D2.1-D8 전체 (8개 파일)
- **문제**: 8개 스키마 문서가 v2.2.0~v2.4.0까지 제각각. V0 GO/NO-GO에 "v3.0.0 통일" 필수
- **수정 내용**: 전체 D1~D8을 v3.0.0으로 일괄 승격 + 내부 REF 크로스레퍼런스 버전 업데이트

### BLOCKER-9: CLAUDE.md 모듈 카탈로그 대규모 오류
- **액션**: FIX
- **파일**: `CLAUDE.md` §6 모듈 시스템
- **문제**:
  1. 총 모듈 수 "80개"로 표기 → 정본은 **81개**
  2. **C-Series (C-1~C-7)** 7개 모듈 완전 누락 (Logic/Math/Code Verifier + Domain Sim/Bayesian/RL/GNN)
  3. **D-Series (D-1~D-6)** 6개 모듈 완전 누락 (Think Engine/Multimodal/LongHorizon/Personality/Parallel/GraphRAG)
  4. **B-Series** B-1~B-4 명칭 완전 불일치 (메모리 계층과 혼동), B-5/B-6 누락
- **정본 기준**: D2.0-01 §5.10~5.13 (B/C/D/EVX 시리즈 정본 카탈로그)
- **수정 내용**:
  1. CLAUDE.md §6에 C-Series(7개), D-Series(6개) 테이블 추가
  2. B-Series를 정본 기준으로 교체: B-1 Skill Library, B-2 Procedural Memory, B-3 Memory Decay, B-4 Auto Curriculum, B-5 RL Self Trainer, B-6 DSPy Prompt Optimizer
  3. 총 모듈 수 "81개"로 정정

### BLOCKER-10: D2.0-07 RBAC 역할 3중 충돌
- **액션**: FIX
- **파일**: `D2.0-07` §3.6.1, S7E-023, CLAUDE.md §7.3
- **문제**: 3개 위치에서 완전히 다른 RBAC 4-역할 정의
  - §3.6.1: OWNER / OPERATOR / AGENT / AUDITOR
  - S7E-023: Owner / Admin / User / Guest
  - CLAUDE.md: OWNER / ADMIN / OPERATOR / VIEWER
- **정본 기준**: CLAUDE.md §7.3 LOCK
- **수정 내용**:
  1. D2.0-07 §3.6.1, S7E-023을 CLAUDE.md LOCK 기준으로 통일: **OWNER / ADMIN / OPERATOR / VIEWER**
  2. AGENT는 "시스템 주체(system principal)"로 재분류, RBAC 역할에서 제외
  3. config.v1.toml에 RBAC 기본 역할 명시

### BLOCKER-11: D2.0-07 비용 경고 임계값 문서 내 6중 모순
- **액션**: FIX
- **파일**: `D2.0-07` §4.2, §15.6.2, §17.6, S7E-008, S7E-062 + `D2.0-08` §23.1 + `D2.0-04` §R1
- **문제**: 동일 문서 내에서 비용 경고 임계값이 6가지로 상충 + 추가 2곳 발견
  1. §4.2 (LOCK): **80% / 100%** (2단계)
  2. S7E-008: 80% / 90% / 100% (3단계)
  3. §15.6.2: 50% / 80% / 95% / 100% (4단계)
  4. §17.6: 60% / 80% / 95% (3단계)
  5. S7E-062: 70% / 85% / 95% (3단계)
  6. D2.0-08 §23.1: 70% / 85% / 100% (3단계) — 이벤트명 `ui.gate.cost.warning_70/85` 포함
  7. D2.0-04 §R1: 70% / 85% / 95% (모니터링 경고)
- **정본 기준**: D2.0-07 §4.2 LOCK (80%/100% 2단계)
- **수정 내용**:
  1. §4.2 LOCK (80% warn+force_mini / 100% block)을 유일한 Gate 임계값 SOT로 확정
  2. §15.6.2의 50%/95%는 "UI 정보성 알림(non-gate)"으로 재분류 및 라벨링
  3. §17.6, S7E-008, S7E-062 문구를 §4.2 LOCK 기준으로 통일
  4. D2.0-08 §23.1 UI 이벤트도 80%/100% 기준으로 정정 (이벤트명 `warning_80/ceiling_100`으로 통일, v12.2.0)
  5. D2.0-04 §R1 모니터링 경고도 80%/100%로 정정 (v12.2.0)

### BLOCKER-12: CLAUDE.md I-4~I-21 모듈 역할명 D2.0-02와 체계적 불일치
- **액션**: FIX
- **파일**: `CLAUDE.md` §6 I-Series 전체
- **문제**: CLAUDE.md가 D2.0-01 §5.6 명명을 사용하지만, 정본(D2.0-02)은 완전히 다른 역할명을 정의. I-4부터 I-21까지 14개 모듈의 이름과 역할이 모두 불일치.
  - 예) CLAUDE.md I-8="Policy Engine" vs D2.0-02 I-8="비용/리소스 관리 엔진"
  - 예) CLAUDE.md I-19="Approval Manager" vs D2.0-02 I-19="데이터 품질(QoD) 평가 엔진"
- **정본 기준**: 문서 우선순위 (DESIGN 2.0 LOCK > PLAN 3.0)에 따라 D2.0-02 §4 정본 인덱스가 최종 권위
- **수정 내용**:
  1. **결정 필요**: D2.0-02 정본 명칭 vs CLAUDE.md/PLAN-3.0 명칭 중 구현시 사용할 "운영 명칭" 확정
  2. 확정 후 CLAUDE.md I-Series 테이블을 정본 기준으로 전면 교체
  3. V1-001 이슈와 연계하여 정본 단일화 처리

### BLOCKER-13: D2.0-01 ↔ D2.0-02 I-모듈명 체계적 불일치 (D2.0-01 vs D2.0-02)
- **액션**: FIX
- **파일**: `D2.0-01` §5.6 vs `D2.0-02` §4
- **문제**: D2.0-01 Overview의 정본 인덱스(I-1~I-25)와 D2.0-02 ORANGE CORE의 내부 인덱스(I-1~I-24)에서 I-6~I-21까지 **16개 모듈명이 체계적으로 불일치**. D2.0-02는 I-25 SDAR 자체가 미정의.
  - 예) D2.0-01 I-6="Self-Check Engine" vs D2.0-02 I-6="워크플로우 오케스트레이션"
  - 예) D2.0-01 I-8="비용/리소스 관리" vs D2.0-02 I-8="템플릿/프롬프트 관리"
- **정본 기준**: D2.0-01 §5.6이 전체 카탈로그 SOT. D2.0-02 §4는 상세 설계 SOT.
- **수정 내용**:
  1. D2.0-01과 D2.0-02 간 매핑 테이블 작성
  2. **결정 필요**: 번호 기준(D2.0-01)을 유지하되 상세 설계(D2.0-02)의 내용을 재매핑, 또는 D2.0-02 번호를 D2.0-01에 정렬
  3. BLOCKER-12(CLAUDE.md↔D2.0-02)와 함께 일괄 해결 필수

### BLOCKER-14: STEP7 전문서 + D2.0-07 3-Gate 체계 (정본 5-Gate 위반)
- **액션**: FIX
- **파일**: `VAMOS_STEP7_*` 전체 5개 파일 (30+ 위치) + `D2.0-07` (3곳)
- **문제**: STEP7 전문서에서 일관되게 **"3-Gate"** (PolicyGate/CostGate/EvidenceGate)만 언급. 정본 5-Gate(+ApprovalGate, +SelfCheckGate)에서 2개 누락. V1 MVP 정의, UI 위젯, 벤치마크, 보안 통합, 공식 용어집 등 30+ 위치에 걸쳐 확산.
  - 5-Gate 언급 시에도 5번째를 "Quality Gate"로 오기 (정본: SelfCheckGate)
  - D2.0-07에서도 3-Gate 잔존 3건 발견 (§2.2 OWASP 매핑, S7E-079 Tool Gate, S7E-085 보안 항목)
- **정본 기준**: D2.0-02 §2.3 + CLAUDE.md §5 (5-Gate LOCK: Policy/Approval/Cost/Evidence/SelfCheck)
- **수정 내용**:
  1. STEP7 전체에서 "3-Gate" → "5-Gate" 교정
  2. ApprovalGate(P1/P2 HITL 승인), SelfCheckGate(P0>=70/P1>=75/P2>=80) 정의 추가
  3. "Quality Gate" → "SelfCheckGate" 명칭 통일
  4. D2.0-07 3-Gate 잔존 3건 → 5-Gate로 교정 완료 (v12.2.0)

---

## A.2 HIGH — 해결 없이 V1 출시 불가 (70건)

| # | ID | 파일 | 문제 | 액션 | 수정 내용 |
|---|-----|------|------|------|----------|
| 1 | V1-001 | PLAN-3.0 | I-Series 21개 vs 25개 | FIX | 25개 정본 확정 (BLOCKER-1과 동일) |
| 2 | V1-016 | PLAN-3.0 | I-21~I-25 정의 누락 | ADD | 5개 모듈 상세 정의 추가 |
| 3 | V1-002 | D2.0-03 | E-15 명칭 충돌 (File System / Cloud Collector) | FIX | 이중명 공식화: "E-15 File System (+ Cloud Collector V2+)" |
| 4 | V1-003 | D2.0-03 | S-5 명칭 충돌 (Router Evolution / Cloud Evolver) | FIX | 이중명 공식화: "S-5 Router Evolution (+ Cloud Evolver V2+)" |
| 5 | V1-008 | 전체 | 38개 DEFER/TBD 미분류 | FIX | 전수 태깅 완료 확인 (V1 blocking=0) |
| 6 | V1-015 | PHASE_B2 | Python backend 진입점 미정 | ADD | `backend/main.py` 진입점 확정 |
| 7 | OC-2 | D2.0-02 | QoD 임계값 수치 미잠금 | FIX | 운영 기본값 0.4/0.7 채택 |
| 8 | OC-5 | D2.0-02 | 한국어 로컬 LLM 미확정 | DEF | DEFER V1.1 / GPT-4o 임시 사용 |
| 9 | BN-12 | D2.0-03 | 이벤트 네이밍 최종 잠금 미완 | FIX | D2.0-02 §6 표준을 V1 정본으로 확정 |
| 10 | CC-006 | D2.1-D2 | EventTypeRegistry agent.*/sdar.* 미등록 | ADD | 두 네임스페이스 레지스트리 등록 |
| 11 | CC-007 | 전체 | Python/TypeScript 스키마 동기화 없음 | ADD | Pydantic→Zod 변환기 V1 구축 |
| 12 | IF-21 | D2.0-07 | 강등 규칙(use_mini_only) 근거 미확보 | FIX | D2.0-07 §4 LOCK 근거 채택 |
| 13 | A-2 | PLAN-3.0 | PLAN 내 RULE 참조가 1.0 기준 (1.3이 정본) | FIX | PLAN-3.0 전체에서 "RULE 1.0" → "RULE 1.3" 교체 |
| 14 | A-8 | PLAN-3.0/CLAUDE.md | E-Series 모듈 역할 매핑 불일치 | FIX | DESIGN 2.0 정본 기준으로 통일 |
| 15 | CM-01 | CLAUDE.md §17 | SDAR NEVER_AUTO 6항목 → 정본 10항목 | FIX | 누락 4개 추가: audit_format, data_retention, user_consent, escalate_own_privilege. CLAUDE.md의 'guardrails/gate' 2항목은 SDAR RA_NEVER_09(disable_guardrails)/RA_NEVER_10(bypass_gate)에 대응하므로 약칭 보존 가능 |
| 16 | CM-02 | CLAUDE.md §12 | Decision policy_gate enum 3값(deny\|restrict\|allow) vs I-5 상세 4값(block\|require_approval\|mask\|allow) | FIX | I-5 상세 설계 4값 enum으로 통일 |
| 17 | D1-01 | D2.1-D1 §3.3 | Cloud Library 스키마 7개 소유권 매핑 누락 (D3 v2.4.0 반영 안 됨) | ADD | D1 §3.3에 CloudLibrary 7개 스키마 등록 |
| 18 | D2-01 | D2.1-D2 | DecisionSchema에 s_module_hints 필드 누락 (FREEZE 스펙 vs 실제 불일치) | ADD | s_module_hints{} 옵셔널 필드 추가 |
| 19 | D2-02 | D2.1-D1~D8 전체 | ResponseEnvelope 스키마 어디에도 정의 안 됨 (CLAUDE.md에서 LOCK 참조) | ADD | D2 또는 D5에 ResponseEnvelope 스키마 정의 + D1 소유권 등록 |
| 20 | D6-01 | D2.1-D6 | KBEmbeddingRecord.vector_dim 예시값 1536 → V1 LOCK(BGE-M3)은 1024 | FIX | 예시값 1024로 변경 또는 "V2 cloud 전용" 주석 추가 |
| 21 | PL-01 | PLAN-3.0 | E-Series(E-1~E-16) 모듈명 D2.0-01과 완전 불일치 (user-facing vs technical tool adapter) | FIX | PLAN-3.0에 오버라이드 배너: "⚠️ E-Series 정본은 D2.0-01/03 기준" |
| 22 | ST-01 | STEP7 J-M | 메모리 L1/L2 의미 역전: STEP7(L1=7d, L2=프로젝트) vs 정본(L1=프로젝트 90d, L2=장기) | FIX | STEP7에 오버라이드 배너: "⚠️ 정본: D2.0-06 L1=Project(90d), L2=Long-term" |
| 23 | ST-02 | STEP7 J-M/보강 | 5계층 메모리(L4 Archive) 정의 — 정본은 4계층(L0~L3) | FIX | STEP7에 배너: "⚠️ 정본: 4계층(L0~L3). L4 Archive는 참조용" |
| 24 | AI-01 | AI Investing | S0/S1 스크래퍼 우선순위 명칭, 메인 상태머신(S0_RECEIVED/S1_INTENT_PARSED)과 충돌 | FIX | 스크래퍼 우선순위를 "TIER-0/TIER-1" 등으로 리네이밍 |
| 25 | AI-02 | AI Investing §14 | 14-Item 기술스택(Kafka/TimescaleDB/Airflow/S3) V1 LOCK 위반 | FIX | V1용으로는 LOCK 기술스택 사용, Kafka/TimescaleDB는 V2+ 전용으로 명시 |
| 26 | SF-01 | D2.0-07 §4.3.2/S7E-050 | 승인 타임아웃 이중화: 일반 10분 vs HITL 5분 (교차참조 없음) | FIX | §4.3.2에 "예외: S7E-050 HITL 고위험은 5분" 명시 |
| 27 | SF-02 | D2.0-07 S7E 전체 | V1 CRITICAL 보안항목 15개 확정 (READINESS_REVIEW §9 기준: CRITICAL 10 + HIGH 4 + DEC-003 Allowlist) | FIX | 전체 문서에서 보안항목 수를 15개로 통일. READINESS_REVIEW §9 + PART2 v8.4.0 DEC-003 반영 |
| 28 | ST-03 | STEP7 F-I | React 19 참조 — 정본 React 18.3 LOCK (V1-014, PHASE_B3 정본) | FIX | STEP7에 배너: "⚠️ 정본: React 18.3 (LOCK)" |
| 29 | PH-01 | CLAUDE.md §7.3 | V2 daily_limit=₩3,300 → PHASE_B4 정본 ₩3,100 (₩93K/30=₩3,100) | FIX | CLAUDE.md §7.3 및 B.5 일 비용 ₩3,100으로 정정 |
| 30 | PH-02 | CLAUDE.md §7.3 | V3 daily_limit=₩9,300 → PHASE_B4 정본 ₩8,900 (₩266K/30≈₩8,900) | FIX | CLAUDE.md §7.3 및 B.5 일 비용 ₩8,900으로 정정 |
| 31 | PH-03 | PHASE_B6 §2.3 | React 경로 `src/frontend/` → B2 정본 `src/`(root) 충돌 | FIX | B6 전체에서 `src/frontend/` → 프로젝트 루트로 정정 |
| 32 | UI-01 | D2.0-08 §4.1 vs §4.4 | UI 상태머신 이중 정의: 9-state(UI_S0~S8) vs 6-state(UIS1~6) 매핑 없음 | FIX | 두 세트 간 양방향 매핑 테이블 추가 또는 정본 단일화 |
| 33 | UI-02 | D2.0-08 §7 vs D2.1-D2 §5.2/5.3 | 에러코드 10개(FM/TL/MC_ERR_*) + 폴백 9개 D2 SOT 미등록 | ADD | D2.1-D2 FailureCode/FallbackRegistry에 19개 등록 |
| 34 | UI-03 | D2.0-08 §2.2/5.3~5.7 vs D2.1-D2 §5.1 | UI 이벤트 54+(hologram/frontmini/core/gate/node/tool/memory) EventTypeRegistry 미등록 | ADD | D2.1-D2 EventTypeRegistry에 등록 (count 53→107+) |
| 35 | BN-01 | D2.0-04 §3 vs §3.1 | `qod_hint` 타입 모순: 본문 `Literal["high","medium","low"]` vs Pydantic `float(0-1)` | FIX | DEC-010 LOCK(0.0~1.0 연속)에 따라 본문을 float로 통일 |
| 36 | BN-02 | D2.0-04 §10.6.2 vs D2.0-05 §4.4 | Circuit Breaker 기본값 충돌: 5회/30s(04) vs 3회/60s(05 LOCK) | FIX | D2.0-05 §4.4 LOCK(3회/60s) 기준으로 D2.0-04 정정 |
| 37 | BN-03 | D2.0-05 §7.1 vs §10 | 파이프라인 명명 자기모순: Intake/Plan/Execute/Verify/Deliver(LOCK) vs Perception/Reasoning/Action/Memory/Reflection | FIX | §10을 §7.1 LOCK 명칭으로 통일 |
| 38 | BN-04 | D2.0-03 K-001 vs §4.4 | SSE를 V2 MCP 옵션으로 기재하면서 동시에 deprecated 선언 | FIX | K-001/K-054에서 SSE 제거, DEC-017(Streamable HTTP LOCK) 통일 |
| 39 | CM-05 | CLAUDE.md §6 I-22/I-23 | status=OFF/V2=ON → 정본 D2.0-01: status=COND/V2=COND (OFF는 유효하지 않은 enum) | FIX | D2.0-01 §5.6 정본 기준으로 교체 |
| 40 | CM-06 | CLAUDE.md §5 Pipeline | Phase 4(Memory/S7) vs Phase 5(Reflection/S6): 상태머신 S6→S7 실행순서와 역전 | FIX | Phase 4=Reflection/Verify(S6), Phase 5=Memory/Store(S7)로 교환 또는 순서 비의존 주석 추가 |
| 41 | PL-04 | PLAN-3.0/BASE-1.3/MASTER | 다운시프트 임계값 3문서 3중 불일치: 70/85/95(PLAN) vs 60/80/95(BASE) vs 80/100(MASTER LOCK) | FIX | MASTER §9.7 LOCK(80%/100%) 기준으로 PLAN/BASE 정정 |
| 42 | PL-02 | PLAN-3.0 §0.6(D) | LangChain을 V1 기술소스로 기재 → DEC-002 LOCK "LangChain import 금지" 위반 | FIX | "LangChain" → "LangGraph" 교체 + DEC-002 배너 추가 |
| 43 | PL-03 | MASTER_SPEC §9.1/§17.3 | "3-Layer Guardrails" 타이틀 ↔ 본문 테이블은 4-Layer(L1~L4) 자기모순 | FIX | 타이틀 "4-Layer" + §17.3 LOCK 요약 정정 |
| 44 | OC-06 | D2.0-02 §8 | Gate 3개만 정의(Policy/Cost/Evidence). ApprovalGate, SelfCheckGate 누락 | ADD | D2.0-02 §8에 ApprovalGate + SelfCheckGate 상세 정의 추가 |
| 45 | SM-01 | D2.0-06 §2/§3 | 내부 5계층(L0~L4 Archive) 기술 ↔ 정본 4계층(L0~L3) 충돌. "3-layer memory" 라벨도 잔존 | FIX | 4계층(L0~L3) 정본 통일, L4 Archive는 V2+ 참조용 명시 |
| 46 | MG-01 | READINESS_REVIEW §1/§V0 | "80모듈" 2곳 → 정본 **81모듈** | FIX | "80" → "81" 정정 (2곳) |
| 47 | MG-02 | BEGINNER_GUIDE §2.3 | I-Series "I-1~I-24" (정본 I-25) + I-21/22/23 테이블 누락 + "4개 시리즈"(정본 8개) | FIX | "I-1~I-25" + 누락 3개 모듈 추가 + "8개 시리즈" 정정 |
| 48 | SP-01 | AGENT_TEAMS §2.1 | LeadAgent가 MessageBus.send_and_wait() 사용 → V1에 MessageBus 미구현(V2 전용) | FIX | V1용 direct dispatcher 대체 또는 in-memory stub 가드 추가 |
| 49 | OV-01 | D2.0-02 §0.6-A + §3.4 | DEC-001 "외부 프레임워크 import 금지" 선언이 LangGraph LOCK(DEC-002)과 충돌 + §3.4에서 LangGraph를 "후보"로 표기 | FIX | DEC-001에 LangGraph 예외 명시 + §3.4 "LOCK 확정" 교체 |
| 50 | MEM-01 | D2.0-01/03/04/08 + MASTER + PLAN-3.0 | 메모리 "3계층" 표기 추가 6개 파일 20+위치 잔존 (SM-01/CM-11 외). D2.0-01 §2.1.1, D2.0-03 2곳, D2.0-04 1곳, MASTER §4/§2.3, PLAN-3.0 10곳+, D2.0-08 5곳 | FIX | 전체 "3계층"→"4계층(L0~L3)" 교체. L3 Procedural 추가 |
| 51 | GATE-01 | D2.0-01/03/08 | Gate 수 오류 추가 3파일 7+위치. D2.0-01 §1.4.2(4-Gate), D2.0-03(3-Gate 2곳), D2.0-08(3-Gate 4곳) | FIX | "3-Gate"/"4-Gate"→"5-Gate" 교체 + ApprovalGate/SelfCheckGate 추가 |
| 52 | D8-H01 | D2.0-08 §6 | 4-Layer 아키텍처와 5-Phase Pipeline 혼합 "5단계 파이프라인(Front→ORANGE→BLUE→Main→Tool)" 기술 | FIX | 4계층+5-Phase 분리 기술 |
| 53 | D8-H03 | D2.0-08 §6.4.7 | "5-Layer 메모리(L0~L4 Archive)" 자체 발명. J-064/J-061/J-097/S7C-072/S7C-090 등 5곳 확산 | FIX | "5-Layer"→"4-Layer(L0~L3)" + L4 삭제 |
| 54 | D8-H04 | D2.0-08 §11-A.11 | 기술스택 Svelte/SvelteKit/Electron(V3)/Node.js CLI 4건 LOCK 위반 | FIX | Tauri 2.0+React 18 LOCK 통일 |
| 55 | D8-H10 | D2.0-08 §4.4 | I-10="UI Orchestration Layer"로 오기 → 정본 I-10=Tool Registry/Router | FIX | 정본 역할명 교정 |
| 56 | D8-H05 | D2.0-08 §6.4.1 J-007 | CLIP 768d와 BGE-M3 1024dim 미구분. 텍스트 임베딩 LOCK 불명확 | FIX | BGE-M3 1024dim LOCK 명시 |
| 57 | SM-06 | D2.0-06 DEC-005 3곳 | text-embedding-3-small/1536dim 잔존 → 정본 BGE-M3/1024dim (D6-01 스키마와 별개 설계문서) | FIX | BGE-M3/1024dim 교체 |
| 58 | WF-01 | D2.0-05 | P2 OPEN→HALF-OPEN CB 전이 충돌 + 에이전트 생명주기 9-State(S0~S8) 불일치 | FIX | §4.4 LOCK CB 통일 + S0~S8 매핑 |
| 59 | WF-02 | D2.0-05 | P2 HITL 무제한 타임아웃 허용 → 정본(일반 10분/HITL 5분) 위반 | FIX | 5분 HITL 타임아웃 적용 명시 |
| 60 | SF-04 | D2.0-07 | SelfCheckGate 전문서 부재 + SDAR 교차참조 전무 + L4 Guardrails 매핑 오류 | FIX | SelfCheckGate 섹션+SDAR 교차참조+L4 정합성 수정 |
| 61 | PL-11 | PLAN-3.0 §0.6 기술소스표 | Weaviate/Pinecone(비정규), LangChain(DEC-002 금지), text-embedding-3 co-primary(BGE-M3 LOCK) 혼재 | FIX | 정규 기술만 열거 |
| 62 | PL-12 | PLAN-3.0 §14.3/§15 | E/S-Series 명칭 정본과 전면 불일치. E-1="전략·기획"(정본:Coding), S-2="자기진화·스케줄러"(정본:Benchmark QA) 등 | FIX | 정본 명칭 병기/교체 |
| 63 | MS-01 | MASTER §4.4 | Decision target_layer Literal["L0","L1","L2"] → L3 누락 | FIX | Literal["L0","L1","L2","L3"] 확장 |
| 64 | OV-02 | D2.0-01 §5.10 | B-Series 6개(Skill Library~DSPy)가 정본 4개 메모리유형(Episodic~Working)과 동일 B-ID 혼재 | FIX | 자산 모듈 vs 메모리유형 구분 주석 또는 네이밍 분리 |
| 65 | D8-H09 | D2.0-08 §S7C-038 | SSE(EventSource) 스트리밍 지정 → DEC-017 Streamable HTTP LOCK 위반 | FIX | Streamable HTTP 교체 |
| 66 | ST-06 | STEP7 | Claude 3.5 Sonnet 명칭 잔존 + V3 Electron 참조(Tauri LOCK) | FIX | 모델명 업데이트 + Tauri LOCK 배너 |
| 67 | SC-01 | D2.1-D1~D4 | Pydantic v1 `class Config:` 잔존(B7 PH-06과 별개 스키마 문서) | FIX | v2 `model_config=ConfigDict(...)` 교체 |
| 68 | PB-01 | PHASE_B1~B4 | config 경로 충돌: B4 정본 `config/config.v1.toml` vs B1 루트 참조 불일치 | FIX | B4 정본 경로 통일 |
| 69 | OV-03 | D2.0-01 §5.10-5.12 vs §8.4 | B/C/D Series 내부 자기모순: §5.10 B-3="Memory Decay" vs §8.4 B-3="Deep Reflection"; §5.10 B-5="RL Self Trainer" vs §8.4 B-5="Memory Decay"; D-4="Personality/Tone" vs §8.4 D-4="HTN Planning" | FIX | §5.10~5.12를 정본으로 확정, §8.4는 별칭 참조용 주석 추가 |
| 70 | B3-01 | PHASE_B3 | `requires-python` 미명시 → 3.10 이하 환경에서 BGE-M3/Pydantic v2 설치 실패 | ADD | pyproject.toml에 `requires-python = ">=3.11"` 추가 |

---

## A.3 MEDIUM — V1 출시 가능하지만 개선 필요 (87건)

| # | ID | 파일 | 문제 | 액션 | 수정 내용 |
|---|-----|------|------|------|----------|
| 1 | V1-004 | D2.1-D7 | approval_status enum 2값 vs 4값 | FIX | D7 정본 2값(approved/denied). CLAUDE.md 4값 참조는 ApprovalSchema.status와 구분 |
| 2 | V1-006 | PLAN-3.0 | QoD 가중치 4요소 vs 5요소 | FIX | PLAN-3.0 5요소 채택 (Accuracy/Relevance/Completeness/Safety/Efficiency) |
| 3 | V1-010 | 전체 | Guardrails 3Layer vs 4Layer | FIX | 4Layer 정본 (L4=post-audit V2+) |
| 4 | V1-013 | 전체 | 비용 ₩40K vs $8 혼동 | FIX | BASE-1.3 ₩40K/월이 정본 |
| 5 | V2-003 | AGENT_TEAMS | Agent Teams vs FREEZE 충돌 | FIX | V1=Lead unidirectional delegation, V2=MessageBus |
| 6 | V2-008 | STEP7 | STEP7 TITLE_ONLY 44% 상세화 필요 | ADD | 미상세 항목 점진적 보강 |
| 7 | V2-001 | CLOUD_LIBRARY | 10-Layer 명칭 충돌 (Cloud Library) | FIX | CL-Layer 접두사 사용 |
| 8 | V2-002 | SDAR | SDAR 활성화 조건 미확정 | ADD | AR-L2→AR-L3 전환 조건 명시 |
| 9 | V2-004 | PHASE_B7 | JSONL→PostgreSQL 마이그레이션 스크립트 미작성 | ADD | V2 마이그레이션 스크립트 개발 |
| 10 | V2-005 | PHASE_B7 | Chroma→Qdrant 벡터 재임베딩 | ADD | V2 임베딩 전환 스크립트 개발 |
| 11 | V2-006 | PHASE_B7 | NetworkX→Neo4j 그래프 변환 | ADD | V2 그래프 변환 스크립트 개발 |
| 12 | CC-004 | CLOUD_LIBRARY | Gate G0-G4 이중 사용 | FIX | Cloud Library: CL-G0~CL-G4 접두사 |
| 13 | CC-012 | AGENT_TEAMS | HMAC 서명 키 관리 미상세 | ADD | V2 MessageBus HMAC 프로토콜 설계 |
| 14 | DEFER-AT-001 | AGENT_TEAMS | MessageBus: Redis vs In-Memory | DEF | V1=In-Memory, V2=Redis 확정 |
| 15 | DEFER-AT-002 | AGENT_TEAMS | GroupChat 순서 알고리즘 | DEF | V2에서 설계 |
| 16 | CC-003 | D2.0-02/CL | QoD 가중치 이중 시스템 | FIX | RAG QoD vs Cloud Library QoD 별도 목적 명시 |
| 17 | E.4 | D2.0-08 | D8 UI 에러 코드 미등록 | ADD | FM_ERR_*/TL_ERR_*/MC_ERR_* → D2 FailureCodeRegistry 등록 |
| 18 | E.6 | D2.1-D1 | D1 스키마 소유권 매핑 누락 | ADD | CloudLibrary 7개 스키마 D1 §3.3에 추가 |
| 19 | B1-ERR | PHASE_B1 | B1 IPC 커맨드 수 표기 오류 (47 vs 72) | FIX | 섹션 헤더 72로 정정 |
| 20 | B7-ERR | PHASE_B7 | datetime.utcnow() deprecated | FIX | datetime.now(timezone.utc) 교체 |
| 21 | SF-54 | D2.0-07 | GDPR 기능 미구현 | ADD | V2 열람/이동/제한 기능 |
| 22 | CM-03 | CLAUDE.md | CLAUDE.md §12 Decision 필드 수 "16" 표기 → 정본 18필드 | FIX | D2.1-D2 §4.1 정본: required 14 + optional 4 = 18 |
| 23 | CM-04 | CLAUDE.md | CLAUDE.md §7.1 DEC-002 LangChain 예외 범위 확대 | FIX | D2.0-02 "Adapter 계층만 + Architecture Review" 조건 추가 |
| 24 | D2-03 | D2.1-D2 | EventTypeRegistry `workflow.report.created` → `wf.` 접두사 미사용 | FIX | `wf.report.created`로 통일 |
| 25 | D2-04 | D2.1-D3/D4 | Gate 배열 필드명 `gates_required` vs `required_gates` | FIX | `required_gates`(D4 컨벤션)로 통일 |
| 26 | D5-01 | D2.1-D5 | CircuitBreaker recovery_time_sec=300s (5분) — 다른 곳 60s/30s | FIX | D2.0-05 §4.4 LOCK(60s) 기준 통일 |
| 27 | B4-01 | PHASE_B4 | config.toml에 self_check 임계값 미포함 (P0=70, P1=75, P2=80 LOCK) | ADD | `[self_check]` 섹션 추가 |
| 28 | B4-02 | PHASE_B4 | config.toml에 approval_timeout_s 미포함 (LOCK: 600초=10분) | ADD | `approval_timeout_s = 600` 추가 |
| 29 | SF-03 | D2.0-07 S7E-031 | PII regex 4패턴만 정의 (주민/전화/이메일/카드) → 여권/운전면허/계좌/사업자등록번호 누락 | ADD | 최소 8패턴으로 확장 |
| 30 | CL-01 | CLOUD_LIBRARY | S1~S5 진화 단계 명칭, 메인 S-Series(S-1~S-8) 모듈 ID와 충돌 | FIX | CL-S1~CL-S5 접두사 사용 |
| 31 | AI-03 | AI Investing §20.2 | Self-evo I-12 매핑 오류 (I-12=Workflow Builder, 정본 I-18=Self-evo Engine) | FIX | 모듈 ID 매핑 정정 |
| 32 | AI-04 | AI Investing §18.6 | V2/V3 비용 수치($79/$189) 메인 LOCK($70/$200)과 불일치 | FIX | 서브셋 vs 추가 비용 명시 |
| 33 | AT-01 | Agent Teams §V1 | V1 위임깊이 "최대 2단계" vs LOCK-AT-004 "최대 3단계" 내부 불일치 | FIX | LOCK-AT-004(3단계) 우선, V1 실무 제한(2단계)은 config로 분리 |
| 34 | CM-07 | CLAUDE.md §5 | Pipeline Phase 4 Memory 출력 "L0/L1/L2" → L3 Procedural 누락 (§15에서 4계층 정의) | FIX | "L0/L1/L2/L3 저장"으로 정정 |
| 35 | CM-08 | CLAUDE.md §11 Tech Stack | V3 Guardrails "4층" → §7.3은 "L4=V2+"로 V2부터 활성 | FIX | V2 Guardrails에 "4층(+사후감사)" 반영 |
| 36 | CM-09 | CLAUDE.md §6 EVX | EVX-3 "Uncertainty" → 정본 D2.0-01 "Log-prob Confidence" | FIX | 정본 명칭으로 교체 |
| 37 | CM-10 | CLAUDE.md §6 I-21 | activation(COND/COND/ON) → 정본 D2.0-01(EXP/OFF/OFF/ON) | FIX | D2.0-01 카탈로그 기준 정정 |
| 38 | PL-13 | MASTER_SPEC §6.9/§17.4 | `config.yaml` 2곳 → 정본 `config.toml` (PHASE_B4 LOCK) | FIX | "config.yaml" → "config.toml" |
| 39 | PL-05 | BASE-1.3 P7-APR vs MASTER §9.5 | 승인 타임아웃: BASE P1=30분/P2=15분 vs MASTER/CLAUDE 10분 | FIX | LOCK 통일 필요 (10분 또는 레벨별 차등) |
| 40 | PL-06 | PLAN-3.0 §0.2 + 17곳 | "RULE 1.0 BASE" 18개 위치 잔존 → 현재 정본 "RULE 1.3" | FIX | 전체 "RULE 1.0" → "RULE 1.3" 교체 |
| 41 | PL-07 | BASE-1.3 P7-NGO | "Non-Goal 10개" → 실제 §2에 7개만 정의 | FIX | "10개" → "7개" 정정 |
| 42 | PL-08 | PLAN-3.0 §2~12 vs §13 | 본문 "I-1~I-21" → §13에서 I-22/23/24 정의. 내부 자기모순 | FIX | 본문을 "I-1~I-24" (또는 I-25)로 업데이트 |
| 43 | PH-04 | PHASE_B6 §2.1 | Python 경로 `src/python/` → B2 정본 `backend/vamos_core/` | FIX | CI 린트 경로 정정 |
| 44 | PH-05 | B5 §7.1 vs B6 §3.4 | Rust 커버리지 목표: B5=80%+ vs B6=60% min/75% target | FIX | B6 target을 B5 기준 80%로 통일 |
| 45 | PH-06 | B7 §2.1 | Pydantic v1 `class Config:` → v2 `model_config = ConfigDict(...)` | FIX | deprecated 패턴 교체 |
| 46 | PH-07 | B6 §2.2/3.2/4.1 | Rust `nightly` toolchain → 정본/CLAUDE.md `stable` | FIX | `dtolnay/rust-toolchain@stable` 통일 |
| 47 | PH-08 | B5 §6.4 | Python `3.12` → B3/B6 정본 `3.11` | FIX | CI 예시 `python-version: "3.11"` |
| 48 | PH-09 | B7 §5.2/§6.3 | `datetime.utcnow()` 추가 3곳 (§2.1 외 별도) | FIX | `datetime.now(timezone.utc)` 교체 |
| 49 | BN-05 | D2.0-05 §7.4.1 vs §7.1 | EVX 5-zone "Plan/Execute/Verify/Memory/Reflection" ≠ 5-Phase LOCK naming | FIX | "Deliver:Memory/Deliver:Reflection" 표기 또는 EVX 전용 명시 |
| 50 | BN-06 | D2.0-03 전체 | E-Series(E-1~E-16) 열거 테이블 부재. E-15만 언급 | ADD | E-Series 정본 참조 크로스레퍼런스 추가 |
| 51 | BN-07 | D2.0-05 §7.2 | OutputEnvelope 스키마 소유권 "또는" 모호 → D2.1-D5에서 이미 해결됨 | FIX | "D5 WorkflowOutputEnvelopeSchema (SOT)"로 명확화 |
| 52 | SP-02 | AGENT_TEAMS §1.3 + §6.4 | I-8/I-9/I-11 모듈 ID 오기: I-8="Cost"(→Policy), I-9="Logger"(→Cost), I-11="Tool"(→I-10) | FIX | 정본 모듈 ID 매핑으로 교체 |
| 53 | SP-03 | AI_INVESTING §20.2 | I-7/I-8/I-9 모듈 ID 체계적 1칸 밀림 (Policy↔Cost↔Logger) | FIX | CLAUDE.md §6 정본 기준 정정 |
| 54 | SP-04 | AI_INVESTING §4.3 | ChromaDB "1536차원" → LOCK BGE-M3 1024dim | FIX | 1024dim으로 정정 |
| 55 | SP-05 | AI_INVESTING §4.2 vs §23.4 | impact_level 범위: §4.2(1~5) vs §23.4(0~10) 내부 모순 | FIX | §4.2 SOT(1~5) 기준 §23.4 정정 |
| 56 | SP-06 | AGENT_TEAMS §9.3 vs LOCK-AT-014 | V3 병렬 수 "최대 100" → LOCK "50+" | FIX | LOCK-AT-014(50+) 기준 정정 |
| 57 | MG-03 | READINESS_GUIDE §3.2.1 | V1 활성 S-Series "S-1~S-5(5개)" → 정본 S-1만(1개). A-Series "A-1~A-3(3개)" → A-1,A-2(2개) | FIX | 정본 activation_default 기준 정정 |
| 58 | MG-04 | READINESS_REVIEW §1 vs §3.1 | 이슈 수 "45건" vs 상세 테이블 합계 55건 내부 모순 | FIX | 일관된 수치로 통일 |
| 59 | OV-M01 | D2.0-01 | §0.7 A1 TECH_STACK 버전 테이블 행 중복 (2회, 다른 버전) | FIX | 중복 행 제거, 단일화 |
| 60 | OV-M02 | D2.0-01 | §2.3.3 vs §8.2.5 "DECISION" vs "DECISION_LOCK" 내부 표기 불일치 | FIX | §8.2.5 정본 기준 통일 |
| 61 | OV-M03 | D2.0-01 | §8.4.2 체크리스트 항목 동일 문구 2회 중복 | FIX | 중복 행 삭제 |
| 62 | OV-M04 | D2.0-01 | §9~11 섹션 번호 역전 (§11이 §10 앞에 배치) | FIX | 번호순 정렬 |
| 63 | OV-M05 | D2.0-02 | §6.3 FB_RESTRICT_GENERAL_INFO 2회 중복 정의 (unique 원칙 위반) | FIX | 중복 정의 삭제/통합 |
| 64 | OV-M06 | D2.0-01 | §1.2 파이프라인 Perception/Reflection 표기에 정본 Intake/Deliver 매핑 설명 없음 | FIX | 매핑 주석 추가 |
| 65 | RG-M01 | READINESS_GUIDE | §3.2.1 I-Series V1 활성 수 "18" → 실제 열거 17개 (산술 오류) | FIX | 18→17 정정 |
| 66 | BG-M01 | BEGINNER_GUIDE | §3.2 QoD 4요소만 제시 → 정본 PLAN-3.0 5요소 (V1-006 연동 별개 파일) | FIX | 5요소 공식 교체 또는 RAG 전용 표기 |
| 67 | BN-D3-M01 | D2.0-03 | SSE deprecated 3곳 + YAML→TOML 2곳 (BN-04/BLOCKER-7과 별개 파일) | FIX | Streamable HTTP + .toml 교체 |
| 68 | SM-06-M01 | D2.0-06 | V2 Chroma→Qdrant 벡터 차원 1536→1024 전환 정합성 미검증 | FIX | 차원 매핑 명시 |
| 69 | WF-M01 | D2.0-04 | evidence_summary 필드 required/optional 모호 (§ 간 상충) | FIX | SOT 확정 |
| 70 | WF-M02 | D2.0-05 | 파이프라인 Retry 최대 횟수 미정의 (무한 루프 가능성) | FIX | max_retry 추가 |
| 71 | SF-M01 | D2.0-07 | 자율성 등급 L0~L3 역전 + 95% use_mini_only 비정규 동작 | FIX | 등급 방향 통일 + 80%/100% LOCK |
| 72 | SC-M01 | D2.1-D1~D4 | ref_legacy 필드 잔존 + gates 필드명 불일치 (required_gates vs gates_required) | FIX | 레거시 정리 + 필드명 통일 |
| 73 | PB-M01 | PHASE_B5~B7 | import 경로 혼재(vamos_core vs backend.schemas) + MCP "SSE" 잔존 | FIX | 경로 통일 + DEC-017 교체 |
| 74 | D8-M02 | D2.0-08 | §2.2.2 Runtime Pipeline 라벨이 정본 S0~S8 명칭과 불일치 (INTENT≠S1_INTENT_PARSED) | FIX | 정본 매핑 주석 추가 |
| 75 | D8-M03 | D2.0-08 | §6.4.7 L1 TTL "7일"(정본 90d) + L2 "프로젝트"(정본 Long-term) 의미 역전 | FIX | 정본 L1=Project/90d, L2=Long-term 통일 |
| 76 | D8-M07 | D2.0-08 | §9.4 E-17=CLib 모듈 추가 시 81→82 영향 (E-Series 16개 초과) | FIX | 기존 모듈 내 재분류 또는 정식 확장 |
| 77 | D8-M09 | D2.0-08 | §1.6 LangGraph를 AutoGen/CrewAI와 동등 옵션 표기 (LOCK 위반) | FIX | "LangGraph LOCK" 명시 |
| 78 | D8-M10 | D2.0-08 | §6.4.11 멀티모달 비용 예산이 버전별 ABSOLUTE LOCK 상한 초과 가능성 | FIX | "전체 상한 내 서브예산" 명시 |
| 79 | D8-M11 | D2.0-08 | §4 UI State Machine 이름이 정본 S0~S8 매핑 없음 | FIX | 크로스 매핑 테이블 추가 |
| 80 | PL-M01 | PLAN-3.0 | §9.1.1 LLM "3단 라우팅" vs 4계층 아키텍처 표현 혼용 | FIX | 4계층 관계 주석 추가 |
| 81 | PL-M02 | PLAN-3.0 | §15+§14.3 S/E-Series 명칭 상세 불일치 (S-2~S-7, E-1~E-11 순서/역할 혼재) | FIX | "DESIGN 2.0 SOT" 주석 |
| 82 | PL-M03 | PLAN-3.0 | §2.X 의존성 매트릭스 L3 누락 + §6.2.2 개인정보 정책 L3 누락 | FIX | L3 행/정책 추가 |
| 83 | PL-M04 | PLAN-3.0 | §13.3.3/§4.5 "I-1~I-24" 참조 잔존 (I-25 SDAR 누락) 다수 위치 | FIX | "I-1~I-25" 전수 교체 |
| 84 | OV-L02 | D2.0-02 | §3.2/[C3] policy_gate enum 이중 정의(deny/restrict/allow vs allow/mask/require_approval/block) — V1 PolicyGate 구현 시 혼란 | FIX | DEC 정본 기준 통일 + 비정본 버전 주석 |
| 85 | DX-05 | D2.1-D3 | §5.2 decision_id optional ↔ AC-D3-006 "필수" 모호 — Pipeline 추적 키 | FIX | D2.1-D3 SOT 기준 required 확정 |
| 86 | DX-06 | D2.1-D4 | §4.2 trace_id description "권장" ↔ required:true 모순 — ABSOLUTE LOCK 위반 | FIX | required:true 유지, description "필수" 정정 |
| 87 | CM-13 | CLAUDE.md §17 | SDAR AR-Level "L0~L4" → "AR-L0~AR-L4" 접두사로 메모리 Layer 혼동 방지 | FIX | AR- 접두사 추가 |

---

## A.4 LOW — V1.1 이후 해결 가능 (33건)

> **v10.1.0 변경**: 기존 46건 중 5건 심각도 상향(→HIGH 1, →MEDIUM 4) + 8건 PART2 이동(V2/V3 로드맵). 이동 내역은 A.5 참조.

| # | ID | 문제 | 액션 |
|---|-----|------|------|
| 1 | V1-005 | datetime.utcnow() deprecated | FIX (V1.1) |
| 2 | V1-009 | LangChain 허용 범위 명시 | ADD (V1.1) |
| 3 | V1-014 | React 18 vs 19 | FIX (V1 = React 18, V2 검토) |
| 4 | CC-002 | 레거시 §10.2 삭제 필요 | DEL (V1.1) |
| 5 | CC-005 | E-15/S-5 내부 참조 혼선 | FIX (V1.1) |
| 6 | B4-03 | PHASE_B4 Guardrails config 3계층만 (L4 사후감사 미포함) | ADD (V2) |
| 7 | D1-02 | D2.1-D1 Template _meta anchor v2.2.0 → 문서 v2.3.0 불일치 | FIX (V1.1) |
| 8 | D8-01 | D2.0-08 React 컴포넌트 레지스트리 미작성 (~44개 매핑 필요) | ADD (V1.1) |
| 9 | CM-11 | CLAUDE.md §6 I-3 "(3계층)" → 정본 4계층(L0~L3) | FIX (V1.1) |
| 10 | CM-12 | CLAUDE.md §6 I-25 D2.0-02 미수록 주석 누락 | ADD (V1.1) |
| 11 | PL-09 | MASTER_SPEC §4.4 approval_status 3값 → D7 정본 2값(approved/denied) | FIX (V1.1) |
| 12 | PL-10 | PLAN-3.0 §12.1 V0 "I-1~I-21 스켈레톤" → GO/NO-GO "I-1~I-5+I-19"만 | FIX (V1.1) |
| 13 | PH-10 | B6 §1.1 `nightly.yml` 워크플로우 참조만 있고 YAML 정의 없음 | ADD (V3) |
| 14 | PH-11 | B5 §7.1 vs B6 §3.3 React vitest threshold 70 → B5 목표 80%+ 불일치 | FIX (V1.1) |
| 15 | DX-04 | D2.1-D2 PII_LONGTERM_DENIED failure code 미등록 | ADD (V1.1) |
| 16 | DX-07 | D2.1-D1 §3.3 Cloud Library 스키마 7개 매핑 (D3 v2.4.0) 누락 | ADD (V1.1) |
| 17 | UI-04 | D2.0-08 §0 CLI 네임스페이스 i18n 파일 미지정 | ADD (V1.1) |
| 18 | UI-05 | D2.0-08 §0 vs S7C-101: 일본어(ja-JP) i18n 미선언 | ADD (V2) |
| 19 | BN-08 | D2.0-03 K-054 SSE V1 스트리밍 로드맵 — deprecated 모순 | FIX (V1.1) |
| 20 | SP-07 | AGENT_TEAMS §2.3.1 `datetime.utcnow` default — V1-005 추가 위치 | FIX (V1.1) |
| 21 | OV-L01 | D2.0-01 §5.9/§5.6 change_lock/activation_default 컬럼 우측정렬(---:) 포맷 오류 | FIX (V1.1) |
| 22 | OV-L03 | D2.0-02 §2.2 S6 FAIL soft loop 1회 LOCK 조건 미명시 | FIX (V1.1) |
| 23 | OV-L04 | D2.0-01 §3.2 V0~V3 설명에 L3 Procedural 진입 시점 미명시 | ADD (V1.1) |
| 24 | BN-D3-L01 | D2.0-03 Dream Mode 자동 적용 범위 + 메모리 scoping 경계 모호 | FIX (V1.1) |
| 25 | SM-06-L01 | D2.0-06 L3 Procedural 정의 상세 부재 + 벡터 검색 결과 수 기본값 미명시 | ADD (V1.1) |
| 26 | SC-L01 | D2.1-D1~D4 문서 버전 추적 주석 누락 + CLib 예시 코드 블록 미포함 | ADD (V1.1) |
| 27 | SF-L01 | D2.0-07 TOC 번호 불일치 + HITL 트리거 미세 정의 미흡 | FIX (V1.1) |
| 28 | D8-L01 | D2.0-08 §5.6-A CLI 이벤트 섹션 빈 스텁 (정의 없음) | ADD (V1.1) |
| 29 | D8-L02 | D2.0-08 §10.3 Alert P0/P1/P2가 도메인 P0/P1/P2와 네이밍 충돌 | FIX (V1.1) |
| 30 | D8-L05 | D2.0-08 §12.3 V2 로그 "5초 폴링" → 이벤트 기반 원칙(§4.4) 위반 | FIX (V2) |
| 31 | D8-L06 | D2.0-08 §16.2 워터마크 배지 이벤트 재사용 → 감사추적 모호 | FIX (V1.1) |
| 32 | PL-L01 | PLAN-3.0 §[INFRA-CORE-6] brain.yaml 참조(config.toml LOCK) + §5.9.1 gpt-5.1 비존재 모델명 | FIX (V1.1) |
| 33 | PL-L02 | PLAN-3.0 §20 STEP7 비용 표기(₩6K/₩20K/₩100K)가 LOCK 상한(₩40K/₩93K/₩266K)과 혼동 가능 | FIX (V1.1) |

---

## A.5 오류 총 요약

| 심각도 | 건수 | V0 차단 | V1 차단 | 액션 분포 |
|--------|------|---------|---------|----------|
| **BLOCKER** | 14 | 14 | 14 | FIX 12, ADD 2 |
| **HIGH** | 70 | 0 | 70 | FIX 58, ADD 11, DEF 1 |
| **MEDIUM** | 87 | 0 | 0 | FIX 72, ADD 13, DEF 2 |
| **LOW** | 33 | 0 | 0 | FIX 19, ADD 13, DEL 1 |
| **PART1 소계** | **204** | **14** | **84** | FIX 161, ADD 39, DEF 3, DEL 1 |
| *PART2 이동* | *8* | *0* | *0* | *ADD 4, DEF 3, 모니터링 1* |
| **전체 합계** | **212** | **14** | **84** | — |

> **v3.0.0 변경**: 2차 심층 스캔으로 62건 신규 추가 (BLOCKER +2, HIGH +20, MEDIUM +25, LOW +15)
> **v4.0.0 변경**: 3차 정밀 스캔으로 60건 신규 추가 (HIGH +20, MEDIUM +25, LOW +15) — 총 211건
> **v5.0.0 변경**: 4차 검증으로 HIGH 1건 추가(OV-03) — 총 212건
> **v10.1.0 변경**: A.4 재배치 — 심각도 상향 5건(→HIGH 1, →MEDIUM 4) + PART2 이동 8건(V2/V3 로드맵)

---

# B. 사용자 직접 준비사항

> VAMOS AI 구현을 위해 사용자가 직접 준비해야 하는 모든 항목입니다.

---

## B.1 V0 시작 전 — 즉시 준비 (필수)

### B.1.1 API Key / 계정 (1건)

| 항목 | 가입 URL | 비용 | 용도 |
|------|---------|------|------|
| **OpenAI API Key** | https://platform.openai.com | 종량제 (~$0.15/1M tokens, gpt-4o-mini) | V0 테스트 + V1 Main LLM |

> **V0에서는 이 키 1개만 있으면 됩니다.** 나머지는 전부 로컬입니다.

### B.1.2 소프트웨어 설치 (7건)

| # | 소프트웨어 | 버전 | 설치 방법 | 용도 |
|---|-----------|------|----------|------|
| 1 | **Python** | 3.11+ | python.org 또는 pyenv-win | AI/ML 백엔드 (venv 필수) |
| 2 | **Node.js** | 18+ LTS | nodejs.org 또는 nvm-windows | React 프론트엔드 빌드 |
| 3 | **Rust** | 1.70+ stable | rustup.rs | Tauri IPC 백엔드 |
<!-- SOURCE_CONFLICT: B6=nightly vs CLAUDE.md/B5/DESIGN 2.0=stable. stable 정본 채택. PH-07에서 B6 nightly→stable 교정 기추적 -->
| 4 | **Ollama** | 최신 | ollama.ai | 로컬 LLM 실행 |
| 5 | **Git** | 최신 | git-scm.com | 버전 관리 |
| 6 | **Ollama 모델 A** | llama3.2:3b | `ollama pull llama3.2:3b` | Mini LLM (~2GB) |
| 7 | **Ollama 모델 B** | llama3.1:8b | `ollama pull llama3.1:8b` | Main LLM (~5GB) |

### B.1.3 하드웨어 확인

| 항목 | 최소 | 권장 | 현재 환경 |
|------|------|------|----------|
| RAM | 8GB | 16GB+ | **64GB DDR4** ✓ (권장 4배 초과) |
| 저장공간 | 20GB 여유 | 50GB+ | **~500GB 여유** ✓ (1.36TB 중) |
| GPU | 없어도 됨 (CPU 모드) | NVIDIA GPU → 추론 속도↑ | **RTX 3070 Ti 8GB (CUDA 12.6)** ✓ |
| CPU | 4코어 | 8코어+ | **i9-12900KF (16코어/24스레드)** ✓ |
| OS | Windows 10+ | Windows 11 | **Windows 11 Pro** ✓ |

### B.1.4 결정 필요 사항 (3건)

| # | 결정 사항 | 선택지 | 권장 | 이유 |
|---|----------|--------|------|------|
| 1 | **프론트엔드 패키지 매니저** | npm / pnpm / yarn | **pnpm** ✅ 결정완료 | 빠르고 디스크 절약, Tauri 호환 (C.1 #1) |
| 2 | **Python 의존성 관리** | Poetry / pip+pip-tools / uv | **Poetry** ✅ 결정완료 | lock 파일 관리, venv 자동 (C.1 #2) |
| 3 | **PyTorch CPU vs GPU** | CPU / CUDA | **CUDA** ✅ 결정완료 | RTX 3070 Ti 확인, CUDA 12.6 (C.1 #3) |

**B.1.5 추가 준비 (권장)**
- `.vamosrules` 파일 작성 (BASE-1.3 lines 249-253 참조, 프로젝트 규칙 정의)
- BGE-M3 Embedding 모델 다운로드 (Hugging Face에서 `BAAI/bge-m3` 다운로드, ~2GB)

---

## B.2 V1 MVP 전 — 추가 준비

### B.2.1 추가 API Key (6건)

| # | 서비스 | 가입 URL | 비용 | 용도 | 모듈 |
|---|--------|---------|------|------|------|
| 1 | **Tavily** | tavily.com | Free 1000회/월 | 웹 검색 | E-2 |
| 2 | **SerpAPI** | serpapi.com | Free 100회/월 | 검색엔진 보조 | E-2 |
| 3 | **E2B** | e2b.dev | Free tier 가능 | 코드 샌드박스 | E-4 |
| 4 | **Unstructured.io** | unstructured.io | Free tier 가능 | 문서 파싱 | E-3 |
| 5 | **NewsAPI** (선택) | newsapi.org | Free 100회/일 | V2 RT-BNP T2 폴링 | E-15 RT-BNP |
| 6 | **Finnhub** (선택) | finnhub.io | Free 60회/분 | V2+ 금융 뉴스 + WebSocket | E-15 RT-BNP |

### B.2.2 추가 소프트웨어 (4건)

| # | 소프트웨어 | 용도 | 비용 |
|---|-----------|------|------|
| 1 | **Docker Desktop** | 코드 실행 샌드박스 (보안 LOCK) | 무료 (개인) |
| 2 | **Tauri Signing Key** | 앱 서명 (릴리스) | 무료 (자체 생성) |
| 3 | **Playwright** | E2E 테스트 | 무료 |
| 4 | **SQLCipher** | 데이터 암호화 | 무료 (오픈소스) |

### B.2.3 GitHub 설정 (2건)

| # | Secret 이름 | 용도 |
|---|------------|------|
| 1 | `TAURI_SIGNING_PRIVATE_KEY` | 앱 코드 서명 |
| 2 | `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` | 서명 키 비밀번호 |

---

## B.3 V2 Pro 전 — 서버/인프라 (비용 발생)

### B.3.1 서버 인프라

| # | 항목 | 용도 | 예상 월 비용 |
|---|------|------|-------------|
| 1 | **VPS 서버** (Vultr/DigitalOcean) | Docker Compose 배포 | ~₩20,000 |
| 2 | **PostgreSQL 16** (Neon/Supabase) | 메인 DB | ~₩10,000 |
| 3 | **Qdrant** (셀프호스팅 or Cloud) | 벡터 DB | Free~₩15,000 |
| 4 | **Neo4j Community** | 그래프 DB | 무료 (GPL 주의) |
| 5 | **Redis 7** | 캐시 + MessageBus | 무료 (로컬) |
| **합계** | | | **~₩45,000/월** |

### B.3.2 추가 API Key (2건)

| # | 서비스 | 용도 | 비용 |
|---|--------|------|------|
| 1 | **Anthropic (Claude)** | V2 메인 LLM | 종량제 |
| 2 | **Slack Webhook** | 배포 알림 | 무료 |

### B.3.3 GitHub Secrets (11건 추가)

```
DEPLOY_SSH_KEY, DEPLOY_HOST, POSTGRES_USER, POSTGRES_PASSWORD,
QDRANT_API_KEY, NEO4J_AUTH, OPENAI_API_KEY (CI용),
SLACK_WEBHOOK_URL, ANTHROPIC_API_KEY,
TAURI_SIGNING_PRIVATE_KEY (V1에서 이관), TAURI_SIGNING_PRIVATE_KEY_PASSWORD (V1에서 이관)
```

> **참고**: V1에서 설정한 2개 Tauri 서명 키 + V2 신규 9개 = 총 11개

---

## B.4 V3 Enterprise 전 — 고급 인프라

| # | 항목 | 예상 월 비용 |
|---|------|-------------|
| 1 | **Kubernetes 클러스터** | 변동 |
| 2 | **GPU 서버** (A10G for vLLM) | ~$144 (~₩190,000) |
| 3 | **Qdrant Cloud** (관리형) | 유료 |
| 4 | **Neo4j Aura** (관리형) | 유료 |
| **합계** | | **₩266,000 이내 (비용 상한 LOCK)** |

---

## B.5 전체 비용 요약

| 버전 | 월 비용 상한 (LOCK) | 일 비용 상한 | 외부 API Key | 서버 |
|------|-------------------|-------------|-------------|------|
| V0 | 테스트용 (~₩5,000) | - | OpenAI 1개 | 없음 (로컬) |
| V1 | **₩40,000** | ₩1,300 | OpenAI + Tavily + SerpAPI + E2B + Unstructured (5개) | 없음 (로컬) |
| V2 | **₩93,000** | ₩3,100 | +Anthropic + Slack (7개) | VPS + Postgres + Qdrant (~₩45K) |
| V3 | **₩266,000** | ₩8,900 | 동일 | +K8s + GPU (~₩190K) |

---

# C. 미결정사항 + 최종 결정 필요 항목

> 산출물 전체에서 아직 결정되지 않은(TBD/DEFER) 항목과 사용자가 결정해야 할 사항입니다.

---

## C.1 V0 시작 전 결정 필요 (13건)

| # | 결정 사항 | 선택지 | 권장안 | 영향 범위 |
|---|----------|--------|--------|----------|
| 1 | 패키지 매니저 | npm / pnpm | **pnpm** | package.json, CI/CD |
| 2 | Python 의존성 관리 | Poetry / pip | **Poetry** | pyproject.toml, CI |
| 3 | PyTorch CPU/GPU | CPU / CUDA | **CUDA** (RTX 3070 Ti 8GB + RAM 64GB 확인) | 로컬 추론 속도 |
| 4 | **RBAC 역할 확정** | CLAUDE.md 4역할 / D2.0-07 §3.6.1 4역할 / S7E-023 4역할 | **CLAUDE.md: OWNER/ADMIN/OPERATOR/VIEWER** | 보안 전체, config.v1.toml |
| 5 | **I-모듈 운영 명칭** | D2.0-02 정본명 / CLAUDE.md/PLAN-3.0 명칭 | **D2.0-02 정본** (DESIGN LOCK > PLAN) | CLAUDE.md, 전체 코드, 문서 |
| 6 | **반응형 breakpoint** | 데스크톱 전용 / 반응형 지원 | **데스크톱 전용** (Tauri 앱) | UI 전체, CSS |
| 7 | **아이콘 라이브러리** | Lucide / Heroicons / Material Icons | **Lucide** (경량, React 호환) | 컴포넌트 전체 |
| 8 | **폰트 설정** | 시스템 폰트 / 웹폰트 번들링 | **시스템 폰트** (번들 크기 절감) | UI 전체, 빌드 |
| 9 | **파일 업로드 크기 제한** | 10MB / 25MB / 50MB | **25MB** (PDF 크기 LOCK과 동일) | LLM context, 스토리지 |
| 10 | **API 재시도 정책** | 1회 / 3회 / 5회 | **3회 + exponential backoff** | 비용, UX |
| 11 | **LLM API 호출 단가 기준** | GPT-4o-mini / Claude Haiku / Ollama 로컬 | **V1=Ollama 무료 + GPT-4o-mini $0.15/1M** | 비용 상한 역산 |
| 12 | **월간 예상 호출 수** | ₩40,000 기준 역산 | **~267,000회/월** (GPT-4o-mini 기준) | UX 설계, 캐싱 전략 |
| 13 | **벡터DB 비용 방향** | 로컬(Chroma 무료) / 클라우드(Pinecone) | **V1=Chroma 무료** (이미 LOCK) | 비용 상한 |

### C.1 각 항목 상세 설명

> **#1 패키지 매니저 — 왜 pnpm인가?**
> npm은 Node.js를 설치하면 자동으로 딸려오는 기본 패키지 매니저입니다. 하지만 npm은 프로젝트마다 같은 패키지를 중복 저장해서 디스크를 많이 차지합니다. pnpm은 "하드 링크"라는 방식으로 한 번 다운로드한 패키지를 여러 프로젝트에서 공유하기 때문에 디스크를 크게 절약합니다. VAMOS는 프론트엔드(Tauri/React)와 백엔드(Python)가 한 저장소(monorepo)에 공존하는 구조인데, pnpm의 workspace 기능이 이런 monorepo 관리에 특히 강합니다. 설치는 `npm install -g pnpm` 한 줄이면 끝이고, 명령어도 npm과 거의 같아서(`pnpm install`, `pnpm add`) 추가 학습이 거의 필요 없습니다.

> **#2 Python 의존성 관리 — 왜 Poetry인가?**
> pip는 Python 기본 패키지 관리자이지만, 의존성 버전 충돌을 자동으로 해결해 주지 못합니다. "A 패키지는 numpy 1.24가 필요한데, B 패키지는 numpy 1.26이 필요하다" 같은 상황에서 pip는 그냥 마지막 걸 설치하고 넘어가 버립니다. Poetry는 이런 충돌을 미리 감지하고 최적의 버전 조합을 자동으로 찾아줍니다. 또한 `pyproject.toml` 하나로 프로젝트 설정/의존성/빌드를 통합 관리할 수 있어서, VAMOS처럼 패키지가 많은 프로젝트에서 깔끔한 관리가 가능합니다. `pip install poetry`로 설치하고, `poetry add 패키지명`으로 사용합니다.

> **#3 PyTorch CPU/GPU — CUDA 확정 (현재 PC 사양 기준)**
> PyTorch는 AI/ML 연산에 사용되는 라이브러리입니다. 현재 PC에 NVIDIA RTX 3070 Ti(8GB VRAM, CUDA 12.6, Compute 8.6 Ampere)가 장착되어 있으므로 **CUDA 버전을 설치**합니다.
>
> **현재 PC 사양과 VAMOS 활용 분석:**
> - CPU: i9-12900KF (16코어/24스레드) — 멀티스레드 처리 우수
> - RAM: 64GB DDR4 — Ollama GPU+CPU 분산(offloading) 시 13B~30B 모델까지 실행 가능
> - GPU: RTX 3070 Ti 8GB — 7B 모델 GPU 전용 실행, 13B 모델 GPU+RAM 분산 실행
> - Storage: 1.36TB (여유 ~500GB) — 모델 저장 충분
>
> **V1 최적 구성:**
> - BGE-M3 임베딩: GPU 가속 (~1.5GB VRAM) → CPU 대비 10~20배 빠름
> - Ollama 로컬 LLM 13B(Q4 양자화): GPU+RAM 분산 (~20 tok/s) → 일반 질문을 무료로 처리
> - 동시 실행(임베딩+LLM): VRAM 8GB + RAM 64GB로 충분한 여유
>
> **V2 전환 시:**
> - 64GB RAM 덕분에 에이전트 10개 동시 실행, Redis MessageBus, Qdrant 서버 등을 외부 서버 없이 로컬에서 상당 부분 운용 가능
> - 30B 모델 GPU+RAM 분산 실행도 가능하여 한국어 고품질 로컬 LLM 활용 여지 큼
>
> 설치: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`

> **#4 RBAC 역할 확정 — 왜 CLAUDE.md의 4역할인가?**
> RBAC(Role-Based Access Control)은 "누가 무엇을 할 수 있는가"를 역할별로 정하는 보안 체계입니다. VAMOS 문서 3곳에서 각각 다른 역할 이름을 사용하고 있었는데, CLAUDE.md의 OWNER/ADMIN/OPERATOR/VIEWER가 가장 직관적입니다. OWNER는 시스템 전체를 관리하는 최고 권한자, ADMIN은 설정을 변경할 수 있는 관리자, OPERATOR는 일상 작업을 수행하는 운영자, VIEWER는 결과만 볼 수 있는 읽기 전용 사용자입니다. 개인 사용자라면 처음에는 OWNER 하나만 쓰게 되지만, 나중에 다른 사람과 함께 쓸 때 역할 분리가 필요해집니다.

> **#5 I-모듈 운영 명칭 — 왜 D2.0-02 정본인가?**
> VAMOS에는 81개 모듈이 있고, 각 모듈에 "I-1 Orchestrator", "I-2 RAG Engine" 같은 이름이 붙어 있습니다. 그런데 설계 문서(D2.0-02)와 운영 문서(CLAUDE.md/PLAN-3.0)에서 같은 모듈을 다른 이름으로 부르는 경우가 있었습니다. VAMOS의 정본 우선순위는 "RULE 1.3 > PLAN 3.0 > DESIGN 2.0 LOCK > DESIGN 본문 > 스키마/TECH_STACK" 순서입니다. 이 우선순위만 보면 PLAN-3.0이 더 상위이지만, PART1 검증 과정(BLOCKER-12/13)에서 모듈별 인터페이스·이벤트·실패코드까지 완전하게 정의된 D2.0-02의 명칭을 운영 기준으로 통일하기로 결정했습니다. 실제 코딩할 때 모듈을 import하거나 참조할 때 이 이름이 쓰이므로, 하나로 통일하는 것이 혼란을 방지합니다.

> **#6 반응형 breakpoint — 왜 데스크톱 전용인가?**
> 반응형 디자인은 화면 크기에 따라 레이아웃이 자동으로 바뀌는 것입니다(예: 스마트폰에서는 1열, PC에서는 3열). VAMOS는 Tauri 데스크톱 앱으로 만들어지므로, 모바일 화면을 지원할 필요가 없습니다. 반응형을 넣으면 CSS 코드가 2~3배 늘어나고 테스트 케이스도 크게 증가합니다. V1은 데스크톱 전용으로 빠르게 출시하고, 만약 V2에서 웹 버전이 필요해지면 그때 반응형을 추가해도 됩니다. 데스크톱 전용이면 최소 너비 1280px 기준으로 개발하면 충분합니다.

> **#7 아이콘 라이브러리 — 왜 Lucide인가?**
> 아이콘 라이브러리는 버튼, 메뉴, 상태 표시 등에 쓰이는 작은 그림(아이콘)을 모아놓은 것입니다. Lucide는 Feather Icons에서 파생된 오픈소스 아이콘 세트로, 1,400+ 아이콘을 제공하면서도 매우 가볍습니다. React와의 호환성이 뛰어나고(`lucide-react` 패키지), 트리 쉐이킹이 잘 되어 사용하지 않는 아이콘은 빌드에서 자동 제외됩니다. Heroicons(Tailwind 팀)도 좋지만 아이콘 수가 300개 정도로 적고, Material Icons는 구글 디자인 언어에 종속되어 VAMOS의 자체 UI와 어울리지 않을 수 있습니다.

> **#8 폰트 설정 — 왜 시스템 폰트인가?**
> 웹폰트를 번들링하면 예쁜 커스텀 폰트를 쓸 수 있지만, 폰트 파일이 500KB~2MB 정도 추가됩니다. VAMOS는 데스크톱 앱이므로 사용자의 OS에 이미 설치된 시스템 폰트(Windows: Segoe UI/맑은 고딕, macOS: SF Pro/Apple SD Gothic Neo)를 쓰면 추가 용량 없이 깔끔한 화면을 만들 수 있습니다. CSS에서 `font-family: system-ui, sans-serif;` 한 줄이면 끝입니다. 나중에 브랜딩이 필요해지면 V2에서 웹폰트를 추가해도 코드 변경이 거의 없습니다.

> **#9 파일 업로드 크기 제한 — 왜 25MB인가?**
> 사용자가 VAMOS에 파일을 업로드할 때의 최대 크기입니다. 10MB는 일반 PDF 한 권도 못 올릴 수 있어 너무 작고, 50MB는 LLM이 처리하기에 토큰이 너무 많아져서 비용이 급증합니다. 25MB는 VAMOS의 PDF 크기 LOCK(C.4.4: "PDF 크기 최대 25MB")과 일치하는 값으로, 대부분의 보고서/논문 PDF를 커버하면서도 비용을 통제할 수 있는 균형점입니다. 이미지는 별도로 15MB LOCK이 걸려 있으므로, 파일 종류에 따라 자동 분류됩니다.

> **#10 API 재시도 정책 — 왜 3회 + exponential backoff인가?**
> 외부 API(LLM, 검색 등)를 호출할 때 네트워크 오류나 서버 과부하로 실패할 수 있습니다. 1회만 시도하면 일시적 오류에도 바로 실패하고, 5회는 불필요한 대기 시간과 비용이 듭니다. 3회가 "웬만한 일시적 오류는 복구되는" 적정선입니다. exponential backoff는 재시도 간격을 점점 늘리는 방식(예: 1초 → 2초 → 4초)으로, 서버가 과부하일 때 더 많은 요청을 보내서 상황을 악화시키는 것을 방지합니다. 대부분의 클라우드 서비스(AWS, GCP)가 이 방식을 표준으로 권장합니다.

> **#11 LLM API 호출 단가 기준 — 왜 Ollama + GPT-4o-mini인가?**
> VAMOS V1은 월 ₩40,000 비용 상한이 LOCK입니다. 현재 PC(RTX 3070 Ti + 64GB RAM)에서는 Ollama로 **13B 모델(Mistral, Llama 3 등)을 로컬에서 무료로** 돌릴 수 있어서, GPT-4o-mini급 성능의 작업 대부분을 비용 없이 처리할 수 있습니다. 13B 로컬 모델로 커버하기 어려운 고난도 작업(긴 문서 분석, 복잡한 추론 등)만 GPT-4o-mini($0.15/1M 입력 토큰)를 쓰면, 월 예산의 대부분을 남길 수 있습니다. 이 PC 사양이라면 로컬 처리 비중이 90% 이상 가능하여, 유료 API 비용은 월 ₩5,000 이하로 통제할 수 있을 것으로 예상됩니다. V2부터는 GPT-4o나 Claude Sonnet 같은 고성능 모델을 추가할 수 있습니다.

> **#12 월간 예상 호출 수 — 왜 ~267,000회인가?**
> 월 ₩40,000 ÷ GPT-4o-mini 호출 단가로 역산한 수치입니다. 실제로는 Ollama 로컬 호출(무료)이 80% 이상을 차지하고, 유료 API는 20% 정도만 쓰게 되므로, 체감 호출 수는 이보다 훨씬 많습니다. 이 수치는 "비용만으로 유료 API를 쓸 경우의 최대치"입니다. 하루로 나누면 약 8,900회이고, 일반 사용 패턴(하루 20~50건 질문)에서는 예산의 10%도 안 쓸 가능성이 높습니다. 시맨틱 캐시(cosine ≥ 0.95 LOCK)가 중복 질문을 자동 차단하므로 실제 API 호출은 더 줄어듭니다.

> **#13 벡터DB 비용 방향 — 왜 Chroma 무료인가?**
> 벡터DB는 텍스트를 숫자 벡터로 변환해서 "의미가 비슷한 문서"를 빠르게 찾아주는 데이터베이스입니다. Pinecone은 클라우드 서비스로 성능이 좋지만 월 $70+ 비용이 듭니다. Chroma는 내 PC에서 로컬로 동작하는 무료 벡터DB로, V1 규모(수만 건 문서)에서는 성능 차이가 거의 없습니다. 이미 기술스택 LOCK(C.4.2)에서 "V1=Chroma(embedded)"로 확정되어 있으므로 사실상 결정이 끝난 항목입니다. V2에서 Qdrant로, V3에서 Qdrant Cloud로 자연스럽게 스케일업하는 로드맵이 이미 잡혀 있습니다.

---

## C.2 V1 구현 중 결정 필요 (13건)

| # | 결정 사항 | 현재 상태 | 권장안 | 근거 |
|---|----------|----------|--------|------|
| 1 | 한국어 기본 로컬 LLM | DEFER V1.1 | GPT-4o-mini 임시 사용 | SOLAR/Polyglot-Ko 벤치마크 미완 |
| 2 | active_node_cap 수치 | TBD (01/04/07 협의) | V1=3, V2=10, V3=50 | Agent Teams LOCK-AT-014와 정렬 |
| 3 | candidate_node_cap 수치 | TBD | V1=5, V2=20, V3=100 | 리소스 제약 고려 |
| 4 | QoD 임계값 기본값 | 발명 금지 → 운영 설정 | 0.4 (최소) / 0.7 (권장) | OC-2 해결안 |
| 5 | P2 비활성 타임아웃 | DEFER V2+ | V1=없음 (세션 종료만) | D2.0-03 §3.3 Option A LOCK |
| 6 | Blue Node 간 A2A 통신 | 미정의 (V1+) | V1=Lead 경유만, V2=MessageBus | Agent Teams 로드맵 |
| 7 | React 버전 | 18 vs 19 | V1=React 18 | 생태계 안정성 |
| 8 | contracts.py 12개 불일치 | ACTION-REQUIRED | Phase A에서 정렬 | AI Investing P0 blocker |
| 9 | **메모리 저장 용량 한계** | 미정의 (TTL만 정의됨) | 실측 후 결정 | L0~L3 각 계층별 용량 상한 미정의. 구현 시 디스크 사용량 측정 필요 |
| 10 | **RT-BNP RSS 소스 목록** | 미정의 | V1에서 구독할 RSS 피드 URL 리스트 확정 | CLOUD_LIBRARY_SPEC §7 확장 |
| 11 | **RT-BNP Breaking 키워드 사전** | 미정의 | 속보 감지 트리거 키워드 목록 확정 | 도메인별 정의 필요 (금융/지정학/기술) |
| 12 | **DCL-TECH RSS 소스 목록** | 미정의 | AI/기술 동향 수집 RSS 피드 URL 확정 | §6.10.2 |
| 13 | **DCL 배경 요약 프롬프트** | 미정의 | I-3 L0에 주입할 "세상 상황 요약" 생성 프롬프트 확정 | §6.10.2 |

### C.2 각 항목 상세 설명

> **#1 한국어 기본 로컬 LLM — 왜 GPT-4o-mini를 임시로 쓰는가?**
> VAMOS는 한국어 AI 투자 비서이므로 한국어를 잘 이해하는 LLM이 필요합니다. 로컬에서 무료로 돌릴 수 있는 한국어 LLM 후보로 SOLAR 10.7B(업스테이지), Polyglot-Ko(EleutherAI) 등이 있지만, 아직 VAMOS 기준의 벤치마크(QoD 0.7 이상)를 통과한 모델이 확정되지 않았습니다. 그래서 V1 초기에는 GPT-4o-mini를 임시 LLM으로 사용하고, V1.1에서 한국어 로컬 LLM 벤치마크를 완료한 뒤 교체합니다. **현재 PC(RTX 3070 Ti 8GB + RAM 64GB)에서는 SOLAR 10.7B(Q4)를 GPU+RAM 분산으로 로컬 실행할 수 있으므로**, V1 초기부터 병행 테스트가 가능합니다. Ollama에서 `ollama pull solar:10.7b-instruct-v1.0-q4_K_M` 한 줄로 설치하고, VAMOS config에서 로컬/API를 쉽게 전환할 수 있습니다. GPT-4o-mini는 한국어 성능이 준수하고 가격($0.15/1M 토큰)이 저렴해서 V1 예산(₩40,000/월) 안에서 폴백 용도로 충분합니다.

> **#2 active_node_cap 수치 — 왜 V1=3개인가?**
> active_node_cap은 "동시에 활성화할 수 있는 Blue Node(AI 에이전트) 최대 수"입니다. Blue Node 하나가 활성화되면 LLM 호출, 메모리 접근, 도구 실행 등 리소스를 소비합니다. V1 환경(개인 PC, 제한된 API 예산)에서 3개 이상 동시 실행하면 응답이 느려지고 비용이 급증합니다. 3개면 "리더 에이전트 1 + 서브 에이전트 2"로 기본 팀 구성이 가능합니다. Agent Teams LOCK-AT-014에서 V1 팀 구성이 "Lead+2Sub"로 정해져 있으므로, active_node_cap=3이 정확히 맞습니다.

> **#3 candidate_node_cap 수치 — 왜 V1=5개인가?**
> candidate_node_cap은 "대기 상태로 준비해 둘 수 있는 Blue Node 후보 최대 수"입니다. 활성 노드(3개)가 작업을 마치면 대기 후보 중에서 다음 노드가 투입됩니다. V1에서 5개면 활성 3 + 대기 2로, 작업 전환 시 지연 없이 바로 다음 노드를 투입할 수 있습니다. 너무 많이 잡으면 메모리에 불필요한 노드 상태를 유지하느라 리소스가 낭비됩니다. V2(20개)와 V3(100개)는 서버 환경에서 대규모 병렬 처리를 위한 수치입니다.

> **#4 QoD 임계값 기본값 — 왜 0.4/0.7인가?**
> QoD(Quality of Data)는 AI가 생성한 데이터의 품질을 0.0~1.0 점수로 측정하는 지표입니다. 정확성(accuracy), 관련성(relevance), 완전성(completeness), 안전성(safety), 효율성(efficiency) 5개 항목의 가중 평균으로 계산됩니다. 0.7은 "이 이상이면 장기 메모리(L2/L3)에 저장할 만큼 신뢰할 수 있다"는 권장 기준이고, 0.4는 최소 기준선입니다. QoD < 0.7이면 출력이 보류되어 추가 검증을 거치고, QoD < 0.4이면 장기 메모리(L2/L3) 저장이 금지되어 임시 메모리(L0/L1)에만 보관 후 재평가됩니다. 참고로, 응답 자체의 자동 재생성(Soft Loop 1회)은 QoD가 아닌 Self-check Gate 점수(P0≥70, P1≥75, P2≥80) 미달 시 발동하는 별개 메커니즘입니다. 이 값은 config.toml에서 운영 중에도 바꿀 수 있으므로, 처음에는 권장값으로 시작하고 실사용 경험에 따라 조정하면 됩니다.

> **#5 P2 비활성 타임아웃 — 왜 V1에서는 없는가?**
> VAMOS는 작업 도메인을 3단계 위험 등급으로 나눕니다. P0(Dev/Research/Productivity)는 기본 활성, P1(Content/Quant)은 1회 승인 필요, P2(Trading/Investing)는 세션마다 승인이 필요하고 자동 OFF되는 가장 엄격한 등급입니다. P2는 실제 돈이 관련된 투자/트레이딩 도메인이므로, 실수로 켜놓은 채 방치하면 위험합니다. 타임아웃은 "P2를 켜놓고 자리를 비워도 자동으로 꺼지는 시간"인데, V1은 개인 데스크톱 앱이므로 세션을 닫으면(앱 종료) P2가 즉시 해제됩니다(Option A LOCK). 별도 타임아웃 로직을 만들 필요가 없습니다. V2부터는 서버에서 여러 사용자가 접속하므로, 유휴 세션 자동 종료 타임아웃이 필요해집니다.

> **#6 Blue Node 간 A2A 통신 — 왜 V1은 Lead 경유만인가?**
> A2A(Agent-to-Agent)는 AI 에이전트끼리 직접 대화하는 것입니다. V1에서 에이전트 3개(Lead+2Sub)가 동시에 서로 직접 대화하면, 메시지 순서 보장이 어렵고 디버깅이 매우 복잡해집니다. "모든 통신은 Lead 에이전트를 경유한다"는 단순한 규칙을 적용하면, Lead가 중앙 허브 역할을 해서 메시지 흐름을 쉽게 추적할 수 있습니다. 쉽게 말해 "팀장을 통해서만 소통"하는 방식입니다. V2에서는 에이전트가 10개로 늘어나므로 MessageBus(Redis)를 통한 직접 통신이 필요해집니다.

> **#7 React 버전 — 왜 18인가?**
> React 19는 2024년 말에 출시되었지만, Tauri 2.0과의 호환성, 서드파티 라이브러리 지원, 커뮤니티 레퍼런스 등이 아직 React 18 중심입니다. VAMOS가 사용하는 주요 라이브러리들(React Router, Zustand, TanStack Query 등)이 React 18에서 안정적으로 동작하는 것이 검증되어 있습니다. 새 프레임워크 버전의 초기 버그에 시간을 빼앗기는 것보다, 검증된 버전으로 V1을 빠르게 출시하는 것이 낫습니다. 이미 기술스택 LOCK(C.4.2)에서 "V1=React 18"로 확정되어 있습니다.

> **#8 contracts.py 12개 불일치 — 왜 Phase A에서 정렬인가?**
> contracts.py는 AI Investing 모듈의 데이터 계약(스키마)을 정의하는 파일입니다. 현재 12개 필드가 설계 문서와 불일치하는 상태인데, 이것은 "문서 수정"이 아니라 "실제 코드 작성"에 해당합니다. PART1은 문서 정합성 작업이고, 실제 코딩은 Phase A(V0 스캐폴딩)에서 시작됩니다. Phase A에서 스키마 파일을 처음 생성할 때 D2.1 스키마 정본에 맞춰서 12개 필드를 올바르게 정의하면 자연스럽게 해결됩니다. 지금 문서만 고치면 나중에 코드와 또 어긋날 수 있습니다.

> **#9 메모리 저장 용량 한계 — 왜 실측 후 결정인가?**
> VAMOS의 4계층 메모리(L0 Session ~ L3 Procedural)는 각각 다른 수명(7일, 90일, 무기한, 무기한)을 가지지만, "최대 몇 GB까지 저장할 수 있는가"는 아직 정해지지 않았습니다. 이유는 간단합니다. 실제로 돌려보기 전에는 "L0에 하루 평균 몇 MB가 쌓이는지" 알 수 없기 때문입니다. V1을 2~4주 운영하면서 각 계층별 디스크 사용량을 측정한 뒤, 그 데이터를 기반으로 상한을 정하는 것이 합리적입니다. 임의로 "L0=500MB"라고 정해봤자 실제 사용 패턴과 맞지 않을 가능성이 높습니다.

> **#10 RT-BNP RSS 소스 목록 — 왜 미정의인가?**
> RT-BNP(Real-Time Breaking News Pipeline)는 실시간 뉴스를 수집하는 모듈입니다. RSS 피드는 뉴스 사이트가 제공하는 자동 업데이트 채널인데, 어떤 뉴스 소스를 구독할지는 사용자의 투자 관심 분야에 따라 달라집니다. 예를 들어 한국 주식 투자자라면 한경/매경/연합뉴스, 미국 주식이라면 Reuters/Bloomberg/CNBC 등의 RSS를 구독하게 됩니다. V1 구현 시점에 사용자가 관심 분야를 확정하면 그에 맞는 RSS URL 리스트를 config.toml에 등록합니다. CLOUD_LIBRARY_SPEC §7에 등록 형식이 정의되어 있습니다.

> **#11 RT-BNP Breaking 키워드 사전 — 왜 미정의인가?**
> "속보"를 자동 감지하려면 트리거 키워드가 필요합니다. 예: 금융 도메인이면 "금리인상", "긴급", "서킷브레이커", 지정학이면 "전쟁", "제재", "미사일" 등. 이 키워드 목록은 투자 전략에 따라 완전히 달라지므로, VAMOS 설계 단계에서 미리 고정할 수 없습니다. V1에서는 기본 키워드 세트(공통 금융 용어 50개 정도)를 제공하고, 사용자가 자기 도메인에 맞게 추가/삭제할 수 있는 UI를 만드는 것이 현실적입니다. config.toml의 `[rt_bnp.keywords]` 섹션에서 관리됩니다.

> **#12 DCL-TECH RSS 소스 목록 — 왜 미정의인가?**
> DCL(Dynamic Context Layer)의 TECH 모드는 AI/기술 동향을 수집해서 VAMOS가 "세상 돌아가는 상황"을 파악하는 기능입니다. #10 RT-BNP와 마찬가지로, 어떤 기술 블로그/뉴스를 구독할지는 사용자 관심에 따라 다릅니다. 추천 소스 예시: Hacker News RSS, TechCrunch, The Verge, AI 분야라면 Papers With Code, Hugging Face Blog 등. V1 구현 시 기본 추천 목록 10개를 제공하고, 사용자가 커스터마이즈할 수 있게 만드는 것이 좋습니다.

> **#13 DCL 배경 요약 프롬프트 — 왜 미정의인가?**
> DCL이 수집한 뉴스/기술 동향을 "오늘의 세상 요약" 형태로 압축해서 메모리 L0(Session)에 주입하는데, 이 요약을 생성하는 LLM 프롬프트가 아직 없습니다. 프롬프트는 "아래 뉴스 기사들을 읽고, 투자에 영향을 줄 수 있는 핵심 정보를 5줄 이내로 요약하세요. 긍정/부정/중립 레이블을 붙이세요"와 같은 형태가 됩니다. 이것은 실제로 뉴스 데이터를 넣어보면서 출력 품질을 반복 조정(프롬프트 엔지니어링)해야 하므로, V1 구현 후 실데이터로 테스트하면서 확정하는 것이 올바른 순서입니다.

---

## C.3 V2 이후 결정 필요 (5건)

| # | 결정 사항 | 대상 버전 | 현재 상태 | 권장안 |
|---|----------|----------|----------|--------|
| 1 | MessageBus 구현 (In-Memory vs Redis) | V2 | DEFER-AT-001 → Redis 확정 | **Redis (이미 확정)** |
| 2 | GroupChat 순서 알고리즘 | V2 | DEFER-AT-002 | **Round-Robin + Priority Queue** |
| 3 | Agent Marketplace 등록 기준 | V2 | DEFER-AT-003 | **QoD ≥ 0.7 + 테스트 10회 통과 + OWNER 승인** |
| 4 | Federated Agent 승인 정책 | V3 | DEFER-AT-004 | **OWNER 수동승인 + 샌드박스 72시간 검증** |
| 5 | A2A 프로토콜 설계 | V3 | DEFER-AT-005 | **JSON-RPC over Streamable HTTP (MCP LOCK 통일)** |

### C.3 각 항목 상세 설명

> **#1 MessageBus 구현 — 왜 Redis인가?**
> V1에서는 에이전트가 3개뿐이라 메모리 안에서 직접 메시지를 주고받으면(InMemoryDispatcher) 충분합니다. 하지만 V2에서 에이전트가 10개로 늘어나면, 한 프로세스 안에서 모든 메시지를 처리하기가 버거워집니다. Redis는 초고속 인메모리 데이터 저장소로, Pub/Sub(발행/구독) 기능을 기본 제공합니다. 에이전트 A가 "분석 완료"라는 메시지를 Redis에 발행하면, 그 메시지를 구독한 에이전트 B, C가 동시에 받아볼 수 있습니다. Redis는 설치가 쉽고(`docker run redis`), 초당 수십만 건의 메시지를 처리할 수 있어서 V2~V3 규모에서도 병목이 되지 않습니다. AGENT_TEAMS_SPEC에서 이미 "DEFER-AT-001 → Redis 확정"으로 결론이 난 상태입니다.

> **#2 GroupChat 순서 알고리즘 — 왜 Round-Robin + Priority Queue인가?**
> GroupChat은 여러 에이전트가 하나의 주제에 대해 토론하는 기능입니다. "누가 먼저 발언할 것인가"를 정하는 알고리즘이 필요합니다. Round-Robin은 "돌아가면서 한 번씩"이라는 가장 단순하고 공평한 방식입니다. 하지만 긴급한 정보(예: 속보 감지, 비용 초과 경고)를 가진 에이전트는 순서를 기다릴 수 없으므로, Priority Queue를 결합합니다. Priority 0(긴급)은 즉시 발언, Priority 1(일반)은 Round-Robin 순서를 따르는 방식입니다. 이 조합은 구현이 단순하면서도 실시간 반응성을 보장합니다. 더 복잡한 알고리즘(동적 우선순위, 발언 빈도 제한 등)은 V3에서 실사용 데이터를 보고 개선해도 늦지 않습니다.

> **#3 Agent Marketplace 등록 기준 — 왜 QoD ≥ 0.7 + 테스트 10회 통과 + OWNER 승인인가?**
> Agent Marketplace는 V2에서 추가되는 기능으로, 커뮤니티가 만든 커스텀 에이전트를 설치할 수 있는 "앱스토어" 같은 것입니다. 아무 에이전트나 등록하면 품질이 낮거나 악의적인 에이전트가 시스템에 들어올 수 있습니다. 3중 기준을 두는 이유는: (1) **QoD ≥ 0.7**: 자동 품질 검증으로 기준 미달 에이전트를 걸러냅니다. (2) **테스트 10회 통과**: 한 번 잘 돌아가는 것이 아니라 반복적으로 안정적인지 확인합니다. (3) **OWNER 승인**: 최종적으로 사람이 확인하여 의도치 않은 동작을 방지합니다. 이 기준은 config.toml에서 조정할 수 있으므로, 엄격하게 시작하고 경험이 쌓이면 완화할 수 있습니다.

> **#4 Federated Agent 승인 정책 — 왜 OWNER 수동승인 + 샌드박스 72시간인가?**
> Federated Agent는 V3에서 추가되는 기능으로, 외부 서버에서 동작하는 에이전트를 내 VAMOS에 연결하는 것입니다. 예를 들어 금융 전문 에이전트가 외부 클라우드에서 동작하고, 내 VAMOS가 그 에이전트에게 분석을 요청하는 방식입니다. 외부 에이전트는 내 데이터에 접근할 수 있으므로 보안이 매우 중요합니다. (1) **OWNER 수동승인**: 시스템 최고 권한자만 외부 에이전트 연결을 허가합니다. ADMIN이나 OPERATOR는 이 권한이 없습니다. (2) **샌드박스 72시간**: 승인 후에도 바로 실전 투입하지 않고, 격리된 환경(샌드박스)에서 72시간 동안 행동을 모니터링합니다. 비정상 행동(과도한 데이터 접근, 예상 외 API 호출 등)이 감지되면 자동 차단됩니다. 72시간은 주말을 포함한 관찰 기간으로, 다양한 시장 상황에서의 행동을 확인할 수 있는 최소 기간입니다.

> **#5 A2A 프로토콜 설계 — 왜 JSON-RPC over Streamable HTTP인가?**
> A2A(Agent-to-Agent) 프로토콜은 V3에서 다른 VAMOS 인스턴스나 외부 AI 시스템과 에이전트끼리 직접 통신하는 규격입니다. 새로운 프로토콜을 만들 수도 있지만, VAMOS에 이미 MCP(Model Context Protocol) 전송 규격이 "Streamable HTTP LOCK (DEC-017)"으로 확정되어 있습니다. A2A도 같은 전송 규격을 쓰면: (1) 이미 구현된 인프라(HTTP 서버, 인증, 로깅)를 재사용할 수 있고, (2) 개발자가 새로운 프로토콜을 배울 필요가 없으며, (3) MCP 도구 호출과 A2A 메시지를 같은 채널로 처리할 수 있습니다. JSON-RPC는 "메서드명 + 파라미터 → 결과" 형태의 단순한 호출 규격으로, 디버깅이 쉽고 언어 중립적입니다. Google의 A2A 프로토콜 초안도 HTTP + JSON 기반이므로, 향후 표준과의 호환성도 기대할 수 있습니다.

---

## C.4 LOCK 확정 사항 — 변경 불가 (핵심 57항목)

> 아래 항목들은 이미 LOCK/FREEZE로 확정되어 구현 시 반드시 준수해야 합니다.

### C.4.1 아키텍처 LOCK

| 항목 | 확정 내용 | 근거 |
|------|----------|------|
| 4계층 구조 | Front Mini → ORANGE CORE → BLUE NODES/OTHER BRAINS → Main LLM | PLAN 3.0 |
| 5-Phase Pipeline | **Intake → Plan → Execute → Verify → Deliver** (LOCK, D2.0-05 §7.1) | DESIGN 2.0 LOCK |
| 9-State Machine | S0~S8 (RECEIVED → DONE) | DESIGN 2.0 LOCK |
| 5-Gate System | Policy → Approval → Cost → Evidence → SelfCheck (우회 불가) | DESIGN 2.0 LOCK |
| 단일 결정 원칙 | 한 시점/한 컨텍스트/한 결론 → locked=true | I-5 FREEZE |
| Decision 18필드 | FREEZE (추가만 가능, 삭제/수정 불가) | D2.1-D2 §4.1 |
<!-- RESOLVED: CLAUDE.md §12 및 체크리스트 모두 18필드로 정정 완료. D2.1-D2 §4.1 SOT=18필드(required 14 + optional 4) -->
| 3-Output 표준 | 사용자 응답 + 근거 요약 + 로그/리포트 | D2.0-05 LOCK |
| 9-State 전이 규칙 | S0~S8 상태 전이: 5-Phase 내 9단계 순차 진행 (LOCK) | D2.0-05 §7.1 |
| 5-Gate 검증 체계 | Policy→Approval→Cost→Evidence→SelfCheck 우회 불가 (LOCK) | D2.0-07 §4 |
| 모듈 카탈로그 | 81개: I:25+E:16+S:8+A:7+B:6+C:7+D:6+EVX:6 | D2.0-01 §5.6~5.13 |
| Agent Teams 구성 | V1=3(Lead+2Sub), V2=10, V3=50+ | AGENT_TEAMS_SPEC LOCK |
| API 엔드포인트 총수 | 88개: Tauri IPC 72 + JSON-RPC 13 + MCP Tool Protocol 3 | CLAUDE.md §13 |

> ⚠️ 초기 표현 "Perception/Reasoning/Action/Memory/Reflection"은 LOCK 이전 명칭. CLAUDE.md에서 병기(/)형태로 사용하나, 구현 시에는 반드시 LOCK 명칭 사용.

### C.4.2 기술 스택 LOCK

| 항목 | V1 | V2 | V3 |
|------|----|----|-----|
| UI | Tauri 2.0 + React 18 | 동일 + PWA (Next.js) | 동일 |
<!-- RESOLVED: CLAUDE.md §11 정본 기준 V2 PWA = Next.js 확정. Next.js는 React 18 기반 메타프레임워크로 React LOCK과 양립. Phase 1 검증에서 확정 (2026-03-02) -->
| Backend | Rust (IPC) + Python 3.11+ (AI/ML) | 동일 | 동일 |
| Agent Framework | LangGraph (Python) LOCK | 동일 | 동일 |
| LLM | Ollama + GPT-4o-mini | +GPT-4o/Claude | +vLLM 셀프호스팅 |
| Embedding | BGE-M3 로컬 (1024dim) | +text-embedding-3-small | +text-embedding-3-large |
| Vector DB | Chroma (embedded) | Qdrant (server) | Qdrant Cloud |
| Graph DB | JSON 파일 기반 | Neo4j Community | Neo4j Aura |
| Storage | SQLite + JSONL | PostgreSQL | Managed Postgres |
| MCP Transport | Streamable HTTP LOCK (DEC-017) | 동일 | 동일 |
| Token Counting | tiktoken cl100k_base LOCK | 동일 | 동일 |
| Schema Validation | Pydantic v2 LOCK | 동일 | 동일 |
| Code Sandbox | Docker LOCK | 동일 | 동일 |
| Semantic Cache | cosine >= 0.95 LOCK | 동일 | 동일 |

### C.4.3 비용/안전 LOCK

| 항목 | 확정 내용 |
|------|----------|
| 비용 상한 | V1=₩40,000/월, V2=₩93,000/월, V3=₩266,000/월 (ABSOLUTE LOCK) |
| 다운시프트 | 80% 경고+force_mini, 100% 차단 (LOCK) |
| Self-check 임계값 | P0>=70, P1>=75, P2>=80 (LOCK) |
| Soft Loop | 자동 1회만 허용, 이후 승인 필요 (LOCK) |
| P2 자동 OFF | 세션 종료 시 즉시 비활성 (LOCK) |
| 승인 타임아웃 | 일반: 10분 미응답 → 자동 거부 (LOCK). 예외: HITL 고위험(S7E-050)은 5분 |
| RBAC | OWNER/ADMIN/OPERATOR/VIEWER 4레벨 (LOCK) — BLOCKER-10 통일 후 확정 |
| Autonomy | L0~L3 자율성 게이팅 (LOCK) |
| 4-Layer Guardrails | L1=NeMo(입력) + L2=Guardrails AI(출력) + L3=LlamaGuard(안전분류) + L4=사후감사. V1=L1+L2 활성, V2=3층(+LlamaGuard), V3=4층(+사후감사) |
| LangChain | import 금지 (패턴 참조만) (FREEZE) |
| SDAR 불변 영역 | **10개 NEVER_AUTO**: 7개 불변구역(safety_rules, cost_ceiling, approval_flow, non_goals, audit_format, data_retention, user_consent) + 3개 운영금지(escalate_own_privilege, disable_guardrails, bypass_gate) |

### C.4.4 운영 한계 LOCK

| 항목 | 확정 값 |
|------|--------|
| 동시 처리 | 최대 3개 병렬 태스크 |
| RAG 검색 | 최대 15문서 / 30청크 |
| API 호출 | 외부 10/분, 고가 모델 3/분 |
| Blue Node 동시 실행 | MAX_CONCURRENT_BLUE_NODES=3 |
| Tool 동시 실행 | MAX_CONCURRENT_TOOLS=5 |
| 위임 깊이 | 최대 3단계 (LOCK-AT-004) |
| MCP 동시 세션 | 최대 10개, TTL 300초 |
| Agent 턴 제한 | P0=5, P1=10, P2=20 |
| TEE 반복 제한 | P0=3, P1=5, P2=10 |
| SDAR 동시 수리 | MAX_CONCURRENT_REPAIRS=1, 인스턴스=3 |
| 입력 토큰 | 최대 30,000 tokens |
| 출력 토큰 | 최대 20,000 tokens |
| 이미지 크기 | 최대 15MB |
| PDF 크기 | 최대 25MB |
| RT-BNP 전파 지연 | BREAKING-P0: 최대 30초, P1: 최대 5분 |
| RT-BNP 사후 검증 | 30분 이내 정규 CL-G0~G4 재검증 |
| RT-BNP 중복 억제 | 5분 윈도우 내 동일 주제 병합 |
| RT-BNP 동시 연결 | V2=10개, V3=30개 |
| DCL 비용 상한 | V1: +₩0, V2: +₩5,000/월, V3: +₩15,000/월 |
| DCL 배경 요약 갱신 | 최대 1시간마다 (V2+), 수동 요청 (V1) |
| DCL QoD 임계값 | >= 0.5 → RAG 삽입, < 0.5 → 폐기 |

---

# D. AI와 함께 VAMOS를 코딩하는 방법론

> VAMOS AI는 규모가 크므로 AI 코딩 어시스턴트(Claude Code)의 도움을 최대한 활용해야 합니다. 아래는 효율적으로 진행하는 방법입니다.

---

## D.0 CLAUDE.md 수정 필수사항 (구현 전 반드시 해결)

> **경고**: 현재 CLAUDE.md에 BLOCKER급 오류 **5건** (BLOCKER 2건 + HIGH 3건)이 있습니다. 수정 없이 사용하면 AI가 잘못된 모듈 구조와 역할로 코드를 생성합니다.

### D.0.1 CLAUDE.md 필수 수정 목록

| # | BLOCKER | 수정 내용 | 영향 |
|---|---------|----------|------|
| 1 | **BLOCKER-9** | C-Series(7개) + D-Series(6개) 테이블 추가, B-Series 명칭 교체(B-1~B-6), 총수 81개로 정정 | 모듈 카탈로그 |
| 2 | **BLOCKER-12** | I-4~I-21 모듈 역할명을 D2.0-02 정본 기준으로 교체 (또는 운영 명칭 결정 후 교체) | 전체 I-모듈 구현 |
| 3 | **HIGH CM-01** | SDAR NEVER_AUTO를 10항목으로 확장 (4개 누락 추가) | 안전 시스템 |
| 4 | **HIGH CM-02** | Decision policy_gate enum을 4값(block\|require_approval\|mask\|allow)으로 통일 | Decision 스키마 |
| 5 | **HIGH SF-02** | V1 CRITICAL 보안항목 15개 확정 (READINESS_REVIEW §9 + DEC-003 Allowlist) | V1 GO/NO-GO |

### D.0.2 CLAUDE.md 검증 체크리스트

```
수정 후 반드시 확인:
☐ §6 모듈 총수 = 81개 (I:25 + E:16 + S:8 + A:7 + B:6 + C:7 + D:6 + EVX:6)
☐ §6 B-Series = D2.0-01 §5.10 정본 (Skill Library ~ DSPy)
☐ §6 C-Series 테이블 존재 (C-1 Logic Verifier ~ C-7 GNN)
☐ §6 D-Series 테이블 존재 (D-1 Think Engine ~ D-6 GraphRAG)
☐ §12 Decision policy_gate = block|require_approval|mask|allow (4값)
☐ §17 SDAR NEVER_AUTO = 10항목
☐ V1 보안항목 = 15개 (READINESS_REVIEW §9: CRITICAL 10 + HIGH 4 + DEC-003 Allowlist)
```

---

## D.1 CLAUDE.md 파일 활용

VAMOS 산출물에 이미 `CLAUDE.md`(672줄)가 포함되어 있습니다. **위 D.0 수정사항을 적용한 후** 이 파일은 3계층 접근 구조로 설계되었습니다:

### 계층 구조
```
1계층 — CLAUDE.md (프로젝트 루트)
├── 전체 아키텍처 요약 (4계층, 5Phase, 9State, 5Gate)
├── 모듈 카탈로그 요약 (81개)
├── 기술 스택 LOCK 목록
├── 비용/안전 LOCK 목록
├── 오픈 이슈 목록 (45건)
└── 문서 참조 인덱스

2계층 — .vamos/instructions.md (상세 지침)
├── 코딩 컨벤션 (Python/Rust/TypeScript)
├── 파일 구조 규칙
├── 테스트 작성 규칙
├── 커밋 메시지 포맷
└── PR 리뷰 체크리스트

3계층 — 개별 산출물 문서 (43개)
└── 필요시 직접 참조
```

### 사용 방법
1. 프로젝트 루트에 `CLAUDE.md`를 배치
2. AI에게 "CLAUDE.md를 읽고 작업해줘"라고 지시
3. AI가 자동으로 아키텍처, LOCK 규칙, 모듈 정보를 이해
4. 특정 모듈 구현 시 "D2.0-02 I-1 섹션 참조해서 구현해줘"처럼 2계층/3계층 참조

---

## D.2 세션별 컨텍스트 관리

### 원칙: 1세션 = 1모듈/1기능

```
[세션 시작]
├── CLAUDE.md 읽기 (자동)
├── 작업 대상 모듈 명시
│   예: "I-1 Intent Detector 구현해줘"
├── 관련 산출물 참조 지시
│   예: "D2.0-02 §7.1 IntentFrame 스키마 기반으로"
├── 구현 → 테스트 → 커밋
└── [세션 종료]
```

### 컨텍스트 과부하 방지
- 한 세션에 여러 모듈을 동시에 구현하지 않음
- 스키마 정의 → 모듈 구현 → 테스트 순서로 진행
- 이전 세션 결과물이 다음 세션의 입력이 되도록 연쇄 설계

---

## D.3 코딩 워크플로우

### STEP 1: 스키마 우선 (Schema-First)
```
1. D2.1 스키마 문서를 읽고 Pydantic v2 모델 생성
   → backend/schemas/contracts.py
2. Pydantic → Zod 변환 (TypeScript 타입)
   → frontend/src/types/generated.ts
3. Pydantic → serde 변환 (Rust 구조체)
   → src-tauri/src/models/
```

### STEP 2: 인터페이스 정의
```
1. 각 모듈의 공개 인터페이스 정의
   → parse_intent(), build_queries(), lock_decision() 등
2. IPC 커맨드 핸들러 스텁 생성
   → src-tauri/src/commands/
3. JSON-RPC 메서드 스텁 생성
   → backend/rpc/
```

### STEP 3: 핵심 로직 구현
```
1. 모듈별 비즈니스 로직 구현
2. Gate 통합 (각 모듈에서 Gate 호출)
3. EventType emit 로직 추가
4. FailureCode → Fallback 연결
```

### STEP 4: 테스트
```
1. Unit Test: pytest (Python) / cargo test (Rust) / vitest (React)
2. Integration Test: IPC 브릿지, 파이프라인 E2E
3. Coverage 확인: Python 75%+, Rust 80%+, React 80%+
   <!-- RESOLVED: B6 v1.0.2 PH-11 기준 적용. Rust 60%→80%, React 70%→80%. Python만 B6 min 75% 유지. Phase 1 검증에서 stale 값 발견→수정 완료 (2026-03-02) -->
```

### STEP 5: 다음 모듈로 이동
```
1. 구현 완료 모듈 체크
2. 의존성 확인 후 다음 모듈 선택
3. 반복
```

---

## D.4 AI에게 지시하는 팁

### 효과적인 프롬프트 예시

```
# 나쁜 예
"VAMOS AI 만들어줘"

# 좋은 예
"CLAUDE.md를 참조해서 I-1 Intent Detector를 구현해줘.
- D2.0-02 §7.1 IntentFrame 스키마 기반
- 입력: user_input.text (string), session_context (optional)
- 출력: IntentFrame (intent_id, trace_id, user_goal, task_type, domain_hint, constraints, risk_flags)
- 내부 상태: I1_S0_RAW → I1_S1_PARSING → I1_S3_READY → I1_S4_EMITTED
- EventType: oc.i1.parse.started, oc.i1.intent.parsed, oc.i1.parse.failed
- FailureCode: OC_I1_PARSE_FAIL → FB_INTENT_HEURISTIC_PARSE
- 테스트 파일도 같이 만들어줘"
```

### 핵심 규칙
1. **한 번에 하나의 모듈만** 지시
2. **스키마 참조를 명시** (어떤 문서의 어떤 섹션)
3. **LOCK 규칙 상기** (필요시 "Gate 우회 불가 LOCK 준수해줘")
4. **테스트를 항상 같이** 요청
5. **기존 코드를 먼저 읽게** 한 후 수정 지시
6. **정본 우선순위 상기**: "RULE 1.3 > PLAN 3.0 > DESIGN 2.0 LOCK > DESIGN 본문 > 스키마" 순서 준수 지시
7. **STEP7 참조 시 주의**: STEP7은 참조용(Node.js/yaml/홈디렉토리 등 정본과 충돌 다수). 반드시 "STEP7은 참조만, 정본은 DESIGN 2.0" 명시

---

## D.5 파일 단위 작업 순서

### V0 스캐폴딩 시 AI에게 요청할 파일 순서

```
Session 1: 프로젝트 초기화
  → monorepo 구조 생성 (PHASE_B2 기준)
  → pyproject.toml + Cargo.toml + package.json
  → config.v1.toml 기본 설정

Session 2: 스키마 정의
  → backend/schemas/contracts.py (24개 Pydantic 모델)
  → backend/schemas/registries.py (EventType/FailureCode/Fallback)
  → 공유 타입 생성 스크립트

Session 3: IPC 통신 레이어
  → src-tauri/src/ipc/protocol.rs
  → src-tauri/src/ipc/python_manager.rs
  → backend/rpc/server.py (JSON-RPC stdin/stdout)

Session 4: I-1 Intent Detector
Session 5: I-2 Context Builder (RAG)
Session 6: I-5 Condition & Decision Engine + Gates
Session 7: I-8 Policy Engine + I-9 Cost Manager
Session 8: I-19 Approval Manager + I-20 Failure/Fallback
Session 9: LangGraph StateGraph 통합
Session 10: 기본 UI 셸 + CLI
```

---

## D.6 버전 관리 전략

### Git 브랜치 전략
```
main ─── 안정 릴리스
├── develop ─── 개발 통합
│   ├── feature/v0-scaffold
│   ├── feature/v0-schemas
│   ├── feature/v0-ipc
│   ├── feature/v1-orange-core
│   ├── feature/v1-storage
│   ├── feature/v1-workflow
│   ├── feature/v1-ui
│   └── feature/v1-integration
├── release/v0.1.0
├── release/v1.0.0
└── hotfix/*
```

### 커밋 메시지 컨벤션
```
feat(I-1): implement Intent Detector with IntentFrame schema
fix(I-5): correct Gate evaluation order (Policy > Approval > Cost > Evidence)
test(I-2): add unit tests for EvidencePack builder
docs(schemas): update contracts.py to match D2.1-D2 v3.0.0
refactor(ipc): simplify Python-Rust JSON-RPC bridge
```

---

# E. 진입전 최종 체크리스트

> 아래 모든 항목이 완료되어야 구현단계(PART 2)로 진입할 수 있습니다.

---

## E.1 즉시 액션 (사용자)

- [x] OpenAI API Key 발급 완료
- [x] Python 3.11+ 설치 확인 (`python --version`)
- [x] Node.js 18+ LTS 설치 확인 (`node --version`)
- [x] Rust 1.70+ 설치 확인 (`rustc --version`)
- [x] Ollama 설치 + `ollama pull llama3.2:3b` + `ollama pull llama3.1:8b`
- [x] Git 설치 확인 (`git --version`)
- [x] **결정**: 패키지 매니저 (npm / pnpm)
- [x] **결정**: Python 의존성 관리 (Poetry / pip)
- [x] **결정**: PyTorch CPU vs GPU

### E.1 검증 결과 (2026-03-02)

**소프트웨어 설치 확인:**

| 항목 | 요구사항 | 실제 버전 | 결과 |
|------|---------|----------|------|
| Python | 3.11+ | 3.11.8 | PASS |
| Node.js | 18+ LTS | v23.1.0 | PASS |
| Rust | 1.70+ | 1.93.1 | PASS |
| Cargo | 1.70+ | 1.93.1 | PASS |
| Git | 설치 확인 | 2.52.0 | PASS |
| Ollama | llama3.2:3b + llama3.1:8b | 둘 다 확인 | PASS |

**결정사항 확인 (C.1 섹션 확정값 참조):**

| 결정 사항 | 확정값 | 근거 |
|----------|-------|------|
| 패키지 매니저 | **pnpm** | C.1 #1 권장안 채택 |
| Python 의존성 관리 | **Poetry** | C.1 #2 권장안 채택 |
| PyTorch | **CUDA** | C.1 #3 RTX 3070 Ti 8GB 확인 |

**API Key:** OpenAI API Key 발급 완료 (사용자 확인)

> **E.1 전체 9개 항목 PASS — 완료**

---

## E.2 문서 수정 (BLOCKER 14건 해결)

- [x] BLOCKER-1: PLAN-3.0 I-모듈 목록 25개로 교정
- [x] BLOCKER-2: PLAN-3.0에 P0/P1/P2 도메인 분류 추가
- [x] BLOCKER-3: D2.1-D2 레지스트리에 storage.* 코드 등록
- [x] BLOCKER-4: D2.0-07 §9 다운시프트 정본 통일
- [x] BLOCKER-5: STEP7 F-I Python backend 오버라이드
- [x] BLOCKER-6: STEP7 F-I 디렉토리 구조 정본 주석
- [x] BLOCKER-7: STEP7 F-I config.toml 통일
- [x] BLOCKER-8: D1~D8 스키마 v3.0.0 일괄 승격
- [x] **BLOCKER-9: CLAUDE.md C/D-Series 추가 + B-Series 교체 + 총수 81로 정정** ← PASS (수정 완료)
- [x] **BLOCKER-10: D2.0-07 RBAC 역할 OWNER/ADMIN/OPERATOR/VIEWER로 통일**
- [x] **BLOCKER-11: D2.0-07 비용 경고 임계값 §4.2 LOCK(80%/100%) SOT 통일**
- [x] **BLOCKER-12: CLAUDE.md I-4~I-21 모듈명 정본 확정 후 교체** ← PASS (수정 완료)
- [x] **BLOCKER-13: D2.0-01 ↔ D2.0-02 I-모듈명 체계적 불일치 해결 (16개 모듈)** ← PASS (듀얼 레이어 + 극고② 전건 완료 — E.2.6 참조)
- [x] **BLOCKER-14: STEP7 전문서 3-Gate → 5-Gate 교정 (30+ 위치)**

### E.2 검증 결과 (2026-03-02)

**14건 전건 PASS / 0건 FAIL — 극고 2건 포함 전부 해결 완료 (E.2.6 참조)**

| # | BLOCKER | 대상 파일 | 결과 | 상세 |
|---|---------|----------|------|------|
| 1 | B-1 | PLAN-3.0 §2.3 | **PASS** | I-1~I-25 (25개) 교정 완료 + 경고 배너 추가 |
| 2 | B-2 | PLAN-3.0 §4.0 | **PASS** | P0/P1/P2 도메인 분류 SOT 섹션 완비 |
| 3 | B-3 | D2.1-D2 | **PASS** | storage.* 5개 + PII_LONGTERM_DENIED + FB_DENY_STORAGE 전수 등록 |
| 4 | B-4 | D2.0-07 §9 | **PASS** | "§4.2에서 LOCK 확정"으로 통일, "예시일 뿐" 문구 제거 |
| 5 | B-5 | STEP7 F-I S7F-012 | **PASS** | Python backend 오버라이드 배너 확인 |
| 6 | B-6 | STEP7 F-I S7F-013 | **PASS** | "PHASE_B2 monorepo 정본" 주석 확인 |
| 7 | B-7 | STEP7 F-I | **PASS** | .yaml 5곳 전부에 ".toml LOCK" 배너 부착 |
| 8 | B-8 | D2.1-D1~D8 | **PASS** | 8개 파일 전부 v3.0.0 승격 완료 |
| 9 | B-9 | CLAUDE.md §6 | **PASS** | 총수 81개 반영, C-1~C-7 + D-1~D-6 테이블 추가, B-1~B-6 정본 교체 완료 |
| 10 | B-10 | D2.0-07 §3.6.1 | **PASS** | OWNER/ADMIN/OPERATOR/VIEWER 통일 완료 (AUDITOR 잔존 3건은 비-RBAC 맥락) |
| 11 | B-11 | D2.0-07 + D2.0-08 + D2.0-04 | **PASS** | §15.6.2, §17.6, S7E-008, S7E-062 전부 80%/100%로 통일 + D2.0-08 §23.1 이벤트명 정정 + D2.0-04 §R1 정정 (v12.2.0) |
| 12 | B-12 | CLAUDE.md §6 | **PASS** | I-1~I-25 전 25개 모듈명 D2.0-01 §5.6 정본으로 교체 완료 |
| 13 | B-13 | D2.0-01 vs D2.0-02 | **PASS** | 듀얼 레이어 완료: §4.0 7열 매핑 테이블, §4.1 타입 주석, §7 헤더 14건(A*/A+/B/D), §10.4.2 타입 열, PLAN-3.0 §13.1 주석. 극고②: I-22/23 신규 + I-24/25 참조 — **E.2.6 참조** |
| 14 | B-14 | STEP7 전5개 + D2.0-07 | **PASS** | STEP7 3-Gate 잔존 0건, 5-Gate 29건 확인, Quality Gate 잔존 0건 + D2.0-07 3-Gate 3건→5-Gate 교정 (v12.2.0) |

**수정 완료 내역**: BLOCKER-9(CLAUDE.md §6 B/C/D-Series + 81개), BLOCKER-12(CLAUDE.md I-Series 25개 정본 교체), BLOCKER-13(듀얼 레이어 6-타입 매핑 + 극고② I-22~25) 전건 완전 해결. 상세는 E.2.6 참조.

---

## E.2.5 CLAUDE.md 수정 검증 (D.0 참조)

- [x] CLAUDE.md §6 모듈 총수 = 81개 확인 ← PASS (81개로 수정 완료)
- [x] CLAUDE.md C-Series(7개) + D-Series(6개) 테이블 존재 확인 ← PASS (C-1~C-7, D-1~D-6 테이블 추가 완료)
- [x] CLAUDE.md B-Series = D2.0-01 정본 (B-1 Skill Library ~ B-6 DSPy) ← PASS (B-1~B-6 정본 교체 완료)
- [x] CLAUDE.md §12 Decision policy_gate = 4값 enum ← PASS (block|require_approval|mask|allow 반영)
- [x] CLAUDE.md §17 SDAR NEVER_AUTO = 10항목 ← PASS (10항목 반영 완료)
- [x] CLAUDE.md V1 보안항목 = 15개 (READINESS_REVIEW §9 + DEC-003 Allowlist) ← PASS (15개 반영 완료)

### E.2.5 검증 결과 (2026-03-02)

**6개 항목 모두 PASS — CLAUDE.md 수정 전건 반영 완료**

| # | 항목 | 요구값 | 현재값 | 결과 |
|---|------|-------|-------|------|
| 1 | §6 모듈 총수 | 81개 | 81개 | **PASS** |
| 2 | C-Series + D-Series 테이블 | C-1~C-7, D-1~D-6 | C-1~C-7, D-1~D-6 추가 완료 | **PASS** |
| 3 | B-Series 정본 | B-1 Skill Library ~ B-6 DSPy (6개) | B-1~B-6 정본 교체 완료 | **PASS** |
| 4 | §12 policy_gate | 4값 enum | block\|require_approval\|mask\|allow | **PASS** |
| 5 | §17 NEVER_AUTO | 10항목 | 10항목 반영 완료 | **PASS** |
| 6 | V1 보안항목 | 15개 | 15개 반영 완료 | **PASS** |

> ~~BLOCKER-9, 12 해결 시 항목 1~3은 자동 해소. 항목 4~6은 CLAUDE.md 별도 수정 필요.~~ → **전건 수정 완료 (2026-03-02)**

---

## E.2.6 극고(極高) 위험 2건 — 해결 완료

> **배경**: BLOCKER-13 완전 해결을 위해 필요했으나, 동일 I-번호에 다른 기능이 매핑된 "의미적 불일치"가 발견되어 단순 명칭 교체가 불가능했음.
> **최종 상태**: ✅ **듀얼 레이어 방식(Option C)**으로 양쪽 모두 해결 완료.

---

### 극고① D2.0-02 본문 명칭 혼동 해소 — ✅ 완료

**핵심 발견**: D2.0-02의 21개 모듈 중 **12개가 MISMATCH** — 같은 I-번호에 D2.0-01 정본과 다른 기능이 설계되어 있음. 단순 명칭 교체(find-replace)는 설계 의미를 파괴하므로 불가.

**해결 방식 — 듀얼 레이어 (기능 기준 매핑)**:
- 본문 레거시 명칭은 유지 (설계 내용과 일치하므로)
- 위에 기능 매핑 정보를 덧씌워 정본과의 관계를 명확히 표시

**6-타입 분류 체계**:

| 타입 | 정의 | 해당 모듈 | 수 |
|------|------|----------|---|
| A | 번호=기능 완전 일치 | I-1,2,3,6,7,18,21 | 7 |
| A* | 번호 일치, 해석 차이 | I-4, I-10 | 2 |
| A+ | MATCH + 1:N 확장 | I-5 → {I-5, I-8} | 1 |
| B | 번호≠기능, 1:1 매핑 | I-8→I-9, I-11→I-10, I-12→I-12, I-15→I-20, I-19→I-15, I-20→I-24 | 6 |
| D | D2.0-01 미대응 orphan | I-9, I-13, I-14, I-16, I-17 | 5 |
| 합계 | | | **21** |

**실행 내역 (4개 결정사항)**:

| 결정 | 대상 | 실행 내용 | 상태 |
|------|------|----------|------|
| Decision 2 | D2.0-02 §4.0 | 7열 기능 매핑 테이블 재구축 + 0:1 GAP 테이블 추가 | ✅ |
| Decision 3 | D2.0-02 §7 | 14개 모듈 타입별 헤더 재수정 (A*/A+/B/D 경고문) | ✅ |
| Decision 4 | PLAN-3.0 §13.1 | 매핑 주석 테이블 추가 (PLAN-3.0 고유 명칭 3건 포함) | ✅ |
| §10.4.2 동기화 | D2.0-02 §10.4.2 | 연결 테이블에 "타입" 열 추가, 기능 매핑 기준으로 갱신 | ✅ |

---

### 극고② I-22~I-25 상세 설계 — ✅ 완료

| I-번호 | 정본 명칭 | 처리 방식 | 설계 위치 | 상태 |
|--------|----------|----------|----------|------|
| I-22 | Task/Project Manager | PLAN-3.0 §13.1.22 기반 신규 작성 | D2.0-02 §7.99~7.101 | ✅ |
| I-23 | Doc/Code Structuring | PLAN-3.0 §13.1.23 기반 신규 작성 | D2.0-02 §7.102~7.104 | ✅ |
| I-24 | Knowledge Graph Engine | D2.0-02 I-20에서 커버(Type B) → 참조 연결 | D2.0-02 §7.105 (참조) | ✅ |
| I-25 | SDAR Engine | 별도 SDAR 사양서 존재 → 참조 연결 | D2.0-02 §7.106 (참조) | ✅ |

**추가 수정**:
- D2.0-01 §2.2.1: "I-1 ~ I-24" → "I-1 ~ I-25" 수정 완료
- D2.0-02 §7 헤더: "I-1 ~ I-24 상세 설계" → "I-1 ~ I-25 상세 설계" 수정 완료

---

### 극고 2건 최종 판정

| 항목 | 해결 방식 | 결과 |
|------|---------|------|
| 극고① 명칭 혼동 | 듀얼 레이어 (§4.0 + §7 헤더 + §10.4.2 + PLAN-3.0 주석) | **PASS** |
| 극고② 설계 부재 | 신규작성 2건 + 참조 연결 2건 | **PASS** |

> **결론**: 극고 2건 모두 해결 완료. D2.0-02에서 레거시 명칭을 만나면 §4.0 기능 매핑 테이블 또는 각 모듈 §7 헤더의 타입별 경고문을 참조.

---

## E.3 환경 검증

- [x] `python -c "import pydantic; print(pydantic.__version__)"` → v2.x 확인
- [x] `cargo --version` → 1.70+ 확인
- [x] `ollama list` → llama3.2:3b, llama3.1:8b 확인
- [x] OpenAI API Key 테스트: `curl https://api.openai.com/v1/models -H "Authorization: Bearer $KEY"`
- [x] 디스크 여유 공간 20GB+ 확인
- [x] `node --version` → 18+ 확인
- [x] `python --version` → 3.11+ 확인
- [x] BGE-M3 모델 다운로드 확인 (또는 V0 진입 후 첫 세션에서 자동 다운로드 설정)

### E.3 검증 결과 (2026-03-02)

**8건 전건 PASS / 0건 FAIL / 0건 COND**

| # | 항목 | 요구 | 현재값 | 결과 | 비고 |
|---|------|------|-------|------|------|
| 1 | pydantic | v2.x | **2.11.5** | **PASS** | |
| 2 | cargo | 1.70+ | **1.93.1** | **PASS** | |
| 3 | ollama 모델 | llama3.2:3b, llama3.1:8b | **둘 다 존재** | **PASS** | llama3.1:8b(4.9GB), llama3.2:3b(2.0GB) |
| 4 | OpenAI API Key | $OPENAI_API_KEY 설정 | **sk-proj-...(164자) + gpt-4o-mini 응답 확인** | **PASS** | setx 등록 완료, API 호출 테스트 성공 |
| 5 | 디스크 여유 | 20GB+ | **490GB** (D: 932GB 중 443GB 사용) | **PASS** | 작업 드라이브 D:\VAMOS 로 변경 |
| 6 | node | 18+ | **v23.1.0** | **PASS** | |
| 7 | python | 3.11+ | **3.11.8** | **PASS** | |
| 8 | BGE-M3 | FlagEmbedding 패키지 | **v1.3.5 설치 완료** | **PASS** | transformers 4.57.6으로 호환 조정, import 확인 완료. 모델 가중치는 V0 첫 실행 시 자동 다운로드 |

> **E.3 완료**: 8건 전건 PASS. 작업 드라이브 D:\VAMOS, 전 파일 경로 D: 기준으로 변경 완료.

## E.4 문서 이해도 확인

- [x] CLAUDE.md 전체 읽기 완료 (**D.0 수정 적용 후**)
- [x] VAMOS_MASTER_SPECIFICATION.md §0 파일 인덱스 확인
- [x] D2.0-01 §5.6~5.13 전체 시리즈 정본 카탈로그 확인 (I/E/S/A/B/C/D/EVX)
- [x] D2.1-D2 §4.1 Decision 18필드 FREEZE 확인
- [x] D2.0-07 §4.2 비용 LOCK (80%/100%) + §4.3.2 승인 타임아웃 (10분) 확인
- [x] PHASE_B2 monorepo 구조 확인
- [x] PHASE_B4 config.v1.toml LOCK 값 확인
- [x] 정본 우선순위 이해: RULE 1.3 > PLAN 3.0 > DESIGN 2.0 LOCK > DESIGN 본문 > 스키마/TECH_STACK
- [x] SDAR DESIGN SPECIFICATION §5.1 NEVER_AUTO 10개 항목 확인

### E.4 검증 결과 (2026-03-02)

**9건 전건 PASS / 0건 FAIL**

| # | 항목 | 확인 내용 | 결과 |
|---|------|----------|------|
| 1 | CLAUDE.md | 697줄, 20개 섹션, **81개 모듈** 선언. D.0 수정(B/C/D-Series 추가, I-Series 정본 교체) 반영 확인 | **PASS** |
| 2 | MASTER_SPEC §0 | **39개 파일** 인덱스 완비 (RULE 1 + PLAN 2 + DESIGN 8 + SCHEMA 10 + PHASE 7 + STEP7 5 + SPEC 5 + GUIDE 1) | **PASS** |
| 3 | D2.0-01 §5.6~5.13 | 8개 시리즈 전수 확인: I(25)+S(8)+E(16)+A(7)+B(6)+C(7)+D(6)+EVX(6) = **81개** | **PASS** |
| 4 | D2.1-D2 §4.1 Decision | DecisionSchema SOT 확인. **18개 top-level 필드** (required 14 + optional 4). FREEZE 정상 | **PASS** |
| 5 | D2.0-07 비용/승인 | §4.2 LOCK: **80% warning / 100% block** 확인. §4.3.2 승인 타임아웃: **10분** (자동 deny) 확인 | **PASS** |
| 6 | PHASE_B2 monorepo | Monorepo **(LOCK)** 확인. `vamos/` 단일 Git root — src(React) + src-tauri(Rust) + backend(Python) + shared + tests + config | **PASS** |
| 7 | PHASE_B4 config LOCK | **20개** LOCK 항목 확인 (core 12 + self_check 4 + approval 2 + blue_nodes 1 + ui 1) | **PASS** |
| 8 | 정본 우선순위 | CLAUDE.md §3/§18 + MASTER_SPEC §3.1/§17.1 일치: **RULE 1.3 > PLAN 3.0 > DESIGN 2.0 LOCK > DESIGN 본문 > 스키마/TECH_STACK** | **PASS** |
| 9 | SDAR NEVER_AUTO | §5.1 정확히 **10항목** (RA_NEVER_01~10) 확인. §9.1 frozenset과 일치. 불변구역 7 + SDAR 안전 3 | **PASS** |

> **RESOLVED (E.4-4)**: D2.1-D2 §4.1 SOT = 18 top-level 필드. CLAUDE.md §12 및 체크리스트 모두 18필드로 정정 완료.

## E.5 기타 준비사항

- [x] GitHub 저장소 생성 (private 권장)
- [x] `.gitignore` 준비 (Python/Rust/Node.js/Tauri 통합)
- [x] `.env.example` 템플릿 준비
- [x] IDE 설정 (VS Code + Rust Analyzer + Python + TypeScript)
- [x] 이 문서(PART1)와 PART2 문서를 프로젝트에 포함

### E.5 검증 결과 (2026-03-02)

**5건 전건 PASS / 0건 FAIL**

| # | 항목 | 확인 내용 | 결과 |
|---|------|----------|------|
| 1 | Git 저장소 | `D:\VAMOS` — `git init` + `main` 브랜치 생성 완료. GitHub remote는 gh CLI 설치 후 연결 예정 | **PASS** |
| 2 | .gitignore | Python/Rust/Node.js/Tauri 통합 패턴 (`.env`, `__pycache__/`, `target/`, `node_modules/`, `data/`, `logs/`) | **PASS** |
| 3 | .env.example | 11개 환경변수 템플릿 (API keys, Ollama, Storage, Cost LOCK, MCP) | **PASS** |
| 4 | IDE 설정 | `.vscode/settings.json` (Python/TS/Rust formatOnSave) + `extensions.json` (9개 권장 확장) | **PASS** |
| 5 | 문서 포함 | `docs/guides/VAMOS_구현가이드_PART1_진입전.md` + `PART2_구현단계.md` 복사 완료 | **PASS** |

> **NOTE**: GitHub remote 연결은 `gh` CLI 설치 후 `gh repo create vamos --private` → `git remote add origin` 순서로 진행. 로컬 Git 초기화는 완료 상태.

---

> **다음 단계**: 위 체크리스트를 모두 완료하면 `VAMOS_구현가이드_PART2_구현단계.md`로 이동하여 V0부터 실제 구현을 시작합니다.

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| v4.0.0 | 2026-02-24 | 3차 정밀 스캔 반영, 60건 추가 (총 211건) |
| v5.0.0 | 2026-02-25 | 4차 검증 반영: C.4.1 Pipeline LOCK 명칭 수정, HIGH 1건 추가(OV-03), CM-01 명칭 정정, B/C/E 섹션 보완, 총 212건 |
| v6.0.0 | 2026-02-25 | 5차 검증 반영: A.5 액션 분포 재계산(HIGH FIX 58/ADD 10, LOW 재산정), SF-02 보안항목 14개 확정(READINESS_REVIEW §9 근거), D.1 산출물 수 43개 정정, PL-01 중복 ID→PL-04 분리 |
| v7.0.0 | 2026-02-25 | 6차 최종 검증: 43개 산출물 전수 크로스체크 완료, PART 1 추가 오류 0건 확인 |
| v8.0.0 | 2026-02-25 | 80건 미검증 항목 분류 반영: C.1 결정필요 5→13건(+8 신규), C.2 +1건(메모리 용량 한계), C.4.1 +5건(9-State 전이 규칙, 5-Gate 검증 체계, 모듈 카탈로그, Agent Teams 구성, API 88 엔드포인트), C.4.3 +1건(4-Layer Guardrails 상세) |
| v8.1.0 | 2026-02-25 | 3단계 독립 검증(Adversarial) 반영: Fix 1 C.4.1 창작 스키마명 3건→산출물 기반 명칭 교체, Fix 2 READINESS_REVIEW §6.1→§9 참조 수정(PART1+PART2+리포트), Fix 3 storage.* 이벤트 7→5개 건수 정정, Fix 4 GDPR SF-54 출처 명확화, Fix 5 Rust 커버리지 B5/B6 충돌 주석 추가 |
| v8.2.0 | 2026-02-25 | 2차 3단계 독립 검증 반영: CM-01 phantom→약칭 대응 표현 정정, 커버리지 B5/B6 SOURCE_CONFLICT 주석 보강(D.3). FALSE_POSITIVE 검증: 24개 Pydantic(V0 서브셋 정당), V2 +10모듈(정확) 확인 |
| v8.3.0 | 2026-02-25 | 4종 교차 검증 반영: A.3 테이블 구조 복구(헤더 5→6열 통일, 26행 파일열 추가), React 18→18.3 LOCK(PHASE_B3 정본), D5-01 Circuit Breaker 60s LOCK 확정. PART2 교차 정합성 5건: V2 +10→+8 모듈 정정, Circuit Breaker 300→60s(D2.0-05 LOCK), 보안 ~13→~14, 위임깊이 LOCK 주석, I-21 정본명 명확화 |
| v8.4.0 | 2026-02-25 | PART2 Check B 역방향 누락 17건 반영과 동기화 버전업 (PART1 자체 변경 없음, PART2 §6.7 LOCK-AT 17건 + §6.9 SDAR LOCK 확장 + §6.5 DEC-003 추가) |
| v9.0.0 | 2026-02-26 | Phase 1 AI 의미검증 반영: (1) A.3 D8-01 React 컴포넌트 ~39→~44개(PART2 §6.1.2 상세 분해 44개와 통일) (2) C.4.1 Decision 16→17필드(D2.1-D2 §4.1 정본: 14 required+3 optional) (3) E.2 체크리스트 Decision 필드 수 동기화 |
| v10.0.0 | 2026-02-26 | Phase 2 수정: Phase 1.5 적대적 재검증 REAL_ERROR 5건 수정 — (1) BLOCKER-5 출처 PLAN-3.0→CLAUDE.md §1 (2) BLOCKER-12 출처 PLAN 3.0→D2.0-01 §5.6 (3) BLOCKER-14 출처 D2.0-02 §8→§2.3+CLAUDE.md §5 (4) Guardrails V2+=전체→V2=3층/V3=4층 + SOURCE_CONFLICT 13건 HTML 주석 처리 + PWA Next.js/React 주석 |
| v11.0.0 | 2026-02-28 | Phase 2 최종 수정 (Phase 1.5 통합 55 REAL_ERROR + 20 SOURCE_CONFLICT): (1) PL-09 approval_status 4값→2값(D7 SOT) (2) B.5 일 비용 V2=₩3,300→₩3,100, V3=₩9,300→₩8,900 (PHASE_B4 산술) (3) PH-01/PH-02 방향 역전(CLAUDE.md→B4 정본) (4) SF-02 보안항목 14→15개(DEC-003) 전 4위치 (5) Decision 17필드 SC 주석 (6) Rust stable SC 주석. Phase 0 전수 재실행 |
| v12.0.0 | 2026-03-01 | RT-BNP (Real-Time Breaking News Pipeline) 설계 추가: C.4.4 운영 한계 LOCK 4건 추가(전파 지연/사후 검증/중복 억제/동시 연결), C.2 결정항목 9→11건(+RSS 소스 목록, Breaking 키워드 사전), B.2.1 API Key 4→6건(+NewsAPI, Finnhub) |
| v12.1.0 | 2026-03-01 | Domain Context Layer(DCL) 선택적 배경 인식 설계: C.4.4 LOCK 3건 추가(비용 상한/갱신 주기/QoD 임계값), C.2 결정항목 11→13건(+DCL-TECH RSS/배경 요약 프롬프트) |
| v12.2.0 | 2026-03-02 | 전수조사 리포트 신규 2건 반영: (1) BLOCKER-14 범위 확장 — D2.0-07 3-Gate 잔존 3건(§2.2 OWASP/S7E-079/S7E-085) → 5-Gate 교정 완료 (2) BLOCKER-11 근거 위치 확장 — D2.0-08 §23.1 이벤트명 `warning_70/85` → `warning_80/ceiling_100` 정정 + D2.0-04 §R1 비용 경고 80%/100%로 정정 |
