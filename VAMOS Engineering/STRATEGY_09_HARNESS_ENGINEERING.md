# VAMOS AI 하네스 엔지니어링 실행 계획

> **작성일**: 2026-04-03 | **최종갱신**: 2026-04-04
> **목적**: VAMOS AI 프로젝트에 하네스 엔지니어링을 적용하여 AI 생성 코드의 일관성과 멱등성을 확보
> **범위**: SOT(68개) + SOT 2(648개) + CLAUDE.md + PART2 구현가이드 + 코드 생성 — 전체 파이프라인
> **근거**: "상위 1% AI 네이티브들은 프롬프트 안쓰고 하네스 깎기에 수백시간 투자합니다" (빌더 조쉬 — DIO FDE 김지운님)
> **상태**: VAMOS 설계 하네스 90점 / 실행 하네스 10점 → 실행 하네스 구축이 최우선

---

## 목차

1. [배경: 왜 하네스 엔지니어링인가](#1-배경-왜-하네스-엔지니어링인가)
2. [현재 상태 진단](#2-현재-상태-진단)
3. [하네스 엔지니어링 6대 원칙 vs VAMOS 갭 분석](#3-하네스-엔지니어링-6대-원칙-vs-vamos-갭-분석)
4. [SOT/SOT 2 하네스 계층 — 원본 정합성 보장](#4-sotsot-2-하네스-계층--원본-정합성-보장)
5. [전체 하네스 아키텍처 — 5계층 구조](#5-전체-하네스-아키텍처--5계층-구조)
6. [최종 실행 계획: 5단계](#6-최종-실행-계획-5단계)
7. [1단계 상세: Layer 0 — PART2 기본 설정 파일 생성](#7-1단계-상세-layer-0--part2-기본-설정-파일-생성)
8. [2단계 상세: Layer 1 — VAMOS 고유 규칙 린터 추가](#8-2단계-상세-layer-1--vamos-고유-규칙-린터-추가)
9. [3단계 상세: CLAUDE.md 보강전략 V1.0 적용](#9-3단계-상세-claudemd-보강전략-v10-적용)
10. [4단계 상세: V0 구현 재개 — 하네스 위에서](#10-4단계-상세-v0-구현-재개--하네스-위에서)
11. [5단계 상세: Eval + 모니터링](#11-5단계-상세-eval--모니터링)
12. [하네스 용어 → VAMOS 적용 매핑표](#12-하네스-용어--vamos-적용-매핑표)
13. [위험 요소 및 대응](#13-위험-요소-및-대응)
14. [성공 기준](#14-성공-기준)

---

# 1. 배경: 왜 하네스 엔지니어링인가

## 1.1 영상 핵심 요약

**출처**: "상위 1% AI 네이티브들은 프롬프트 안쓰고 '하네스 깎기'에 수백시간 투자합니다"
**채널**: 빌더 조쉬 (Builder Josh) — DIO FDE 김지운님 인터뷰
**URL**: http://www.youtube.com/watch?v=A8PMyC7W_vg

### 하네스 엔지니어링이란

어떤 AI 모델(Claude, Gemini, Codex 등)을 갈아끼워도 **동일한 결과물(Output)이 나오도록 시스템적으로 강제**하는 기법. 단순 프롬프트 잘 쓰기를 넘어, AI를 **틀(Harness) 안에 가두어** 규칙을 따르게 만드는 것이 핵심이다.

### 하네스의 3대 구성요소

| 구성요소 | 역할 | 영상 설명 |
|---------|------|---------|
| **린터(Linter)** | 코드/문서의 형식 규칙 강제 | "파일명, 임포트 순서, 클래스 명명 규칙까지 린터로 강제" |
| **구조화 문서(CPS)** | Context→Problem→Solution 프레임워크 | "맥락→문제→해결책 순서로 정리하면 AI가 제멋대로 하지 않는다" |
| **평가(Eval)** | 지속적 품질 측정 및 모니터링 | "Datadog처럼 에이전트 품질을 실시간 모니터링" |

### 멱등성 (Idempotency) — 핵심 원리

- 같은 입력 → 항상 같은 출력
- 12번 시켜도 12번 동일한 결과가 나와야 함
- 프롬프트(자연어)가 아니라 **코드화된 규칙(Linter, Gate, Schema)**으로 달성
- "포맷하고 Reset to Zero 해도 같은 결과가 나오는 시스템" (김지운)

### 하네스 엔지니어링 6단계 프로세스

```
1. 요구사항 분석   — "고객의 말을 제한하지 않는다. 모든 것이 데이터."
2. 플랜(Plan) 수립 — CPS 프레임워크 (Context/Problem/Solution)
3. 아키텍처 설계   — PRD는 살아있는 산출물, 프로젝트 내내 업데이트
4. 코드 레벨 디자인 — DDD + 린터(Linter)로 엄격한 규칙 강제
5. 멱등성 검증     — 어떤 모델에 시켜도 동일 결과 확인
6. 최종 리뷰       — 배포 전 조직 맞춤형 평가
```

### 엔터프라이즈 AI 평가(Eval) 전략

- **평가 지표**: 문맥 적합성(Context Relevance), 근거 확실성(Groundedness) 등
- **조직 맞춤형**: 100번 중 10번 틀리면 차라리 답 안 하는 조직 vs. 틀려도 답하는 조직
- **Agent Dog**: Datadog처럼 에이전트 품질을 실시간 모니터링하는 체계

### 유지보수와 지속 가능성

- FDE가 떠난 후에도 내부 인원이 직접 유지보수 가능해야 함
- 문서와 규칙을 코드화하여 자산으로 고객사에 전달
- AI 시스템의 불확정성을 잡는 핵심 수단

---

## 1.2 VAMOS에 적용하는 이유

현재 VAMOS는 AI(Claude Code)로 SOT 상세화 및 코드 구현을 진행 중이나, **하네스 없이 프롬프트만으로 작업하면 일관성 있는 결과가 나오지 않는 문제**를 체감했다.

```
문제 상황:
  프롬프트 → AI 코드 생성 → 눈으로 확인 → 다음 작업
  결과: 매번 다른 코드 스타일, 네이밍 불일치, 누적 불일치

목표 상황:
  프롬프트 → AI 코드 생성 → Ruff 자동검사 → pytest → CI 통과 → 다음 작업
  결과: 틀린 코드는 린터가 잡고, 회귀는 테스트가 잡음
```

---

# 2. 현재 상태 진단

## 2.1 설계 vs 실제 구현 갭

| 구분 | 설계 (문서) | 실제 구현 (파일) |
|------|-----------|---------------|
| **SOT 설계 문서** | 68개 + SOT 2 648개 = 716개 | 존재 |
| **구현 가이드** | PART2 ~4,700줄 | 존재 |
| **검증 프레임워크** | deterministic_validator.py (713줄) | EA/CM JSON 검증용만 존재 |
| **평가 도구** | ragas, deepeval, promptfoo, giskard, minicheck | 개별 스크립트 존재, 파이프라인 미연결 |
| **모니터링** | langfuse, phoenix, lineage tracker | 스크립트 존재, 외부 서비스 미연동 |
| **스킬** | 55개 디렉토리 | ~30%만 실구현체, 나머지 스캐폴드 |
| **린터 설정** | PART2에 ruff/pytest 정의 있음 | **실제 파일 0개** |
| **CI/CD** | PART2에 GitHub Actions yaml 있음 | **실제 파일 0개** |
| **테스트** | PART2에 80%+ 커버리지 목표 | **실제 파일 0개** |
| **패키지 관리** | PART2에 poetry/pnpm 정의 있음 | **실제 파일 0개** |

## 2.2 하네스 점수 (영상 6대 원칙 기준)

| 하네스 원칙 | VAMOS 설계 | VAMOS 실제 구현 | 점수 |
|-----------|-----------|---------------|------|
| 1. 린터(코드 강제) | 네이밍 LOCK, DEC-002, R1~R11 | 린터 설정 파일 0개 | **10/100** |
| 2. CPS 프레임워크 | 5-Phase Pipeline, IntentFrame | 스킬 ~30% 구현 | **40/100** |
| 3. 멱등성 검증 | SDAR 내부 3회 재시도, Decision Lock | 시스템 전체 멱등성 미구현 | **15/100** |
| 4. Eval (지속 평가) | 88개 벤치마크, QoD 5요소 | 4개만 V1 실행 가능, 파이프라인 미연결 | **20/100** |
| 5. Agent Dog (모니터링) | 134개 이벤트 로깅 설계 | 메트릭 집계 0건, 알림 0건 | **15/100** |
| 6. 유지보수 자산화 | CLAUDE.md + SOT 716개 | CI/CD 0건, 테스트 0건, 패키지관리 0건 | **30/100** |

**종합: 설계 하네스 90점 / 실행 하네스 ~22점**

## 2.3 PART2 구현가이드에 설계되어 있지만 실행되지 않은 것

| 항목 | PART2 위치 | 내용 | 상태 |
|------|-----------|------|------|
| pyproject.toml | line 1490~1536 | poetry 의존성 + ruff + mypy | 미생성 |
| quality-python.yml | line 1410~1430 | GitHub Actions ruff + mypy CI | 미생성 |
| test-python.yml | line 1432~1450 | GitHub Actions pytest + coverage CI | 미생성 |
| ruff 설정 | line 1523~1536 | 13개 린트 룰셋 | 미생성 |
| conftest.py | line 1541~1545 | pytest fixture, async 지원, Ollama 스킵 | 미생성 |
| V0 완료 체크리스트 | line 1569~1584 | 13개 검증 항목 | 미실행 |

---

# 3. 하네스 엔지니어링 6대 원칙 vs VAMOS 갭 분석

## GAP-1. 린터 (코드 레벨 강제) — CRITICAL

### 영상 원칙
> "파일 이름 하나까지도 규칙(린터)에 맞게 짜도록 설정하여 유지보수가 쉬운 코드를 만든다"

### VAMOS 현재 상태

**설계에 있는 것:**
- 네이밍 LOCK: event=lower.dot, failure=UPPER_SNAKE, fallback=FB_UPPER_SNAKE, state=S#_, module=S-#
- DEC-002: LangChain import 금지 (Allowlist만 허용)
- R1~R11: 공통 규칙 레지스트리 (PART2 §1.3)
- PART2 ruff 설정: 13개 린트 룰셋 (E, F, W, I, N, UP, S, B, A, C4, DTZ, T20, ICN)

**실제로 있는 것:**
- deterministic_validator.py (713줄): EA/CM JSON 검증 전용
- .claude Hook: EA/CM 파일 Write/Edit에만 트리거

**완전히 없는 것:**

| 필요한 린터 | 용도 | 파일명 | 현황 |
|-----------|------|--------|------|
| Ruff | Python 백엔드 코드 규칙 | `backend/pyproject.toml [tool.ruff]` | 미생성 |
| ESLint / Biome | React 프론트엔드 코드 규칙 | `.eslintrc.js` or `biome.json` | 미생성 |
| Clippy | Rust/Tauri 백엔드 린트 | `clippy.toml` | 미생성 |
| Prettier | 코드 포맷 통일 | `.prettierrc` | 미생성 |
| commitlint | 커밋 메시지 규칙 강제 | `commitlint.config.js` | 미생성 |
| VAMOS 커스텀 린트 | VAMOS 고유 규칙 (네이밍, import 금지 등) | `scripts/vamos_lint.py` | 미생성 |

### PART2 ruff vs VAMOS 전체 규칙 — 갭

PART2의 ruff 설정은 **범용 Python 린트**이며, VAMOS 고유 규칙을 잡지 못한다:

| VAMOS 규칙 | 출처 | ruff 기본으로 잡히나? | 별도 처리 |
|-----------|------|-------------------|---------|
| R1: Python ≥ 3.11 | PART2 R1 | `target-version = "py311"` | 커버됨 |
| R2: `class Config:` 금지, Pydantic v2만 | PART2 R2 | 안 잡힘 | 커스텀 룰 필요 |
| R3: 새 파일 생성 제한 | PART2 R3 | 린터 범위 밖 | Claude Hook |
| R5: LOCK/FREEZE 런타임 변경 금지 | PART2 R5 | 안 잡힘 | 커스텀 검사 |
| R6: SOT 없는 내용 창작 금지 | PART2 R6 | 린터 범위 밖 | Claude Hook |
| DEC-002: `import langchain` 금지 | CLAUDE.md §7.1 | `flake8-tidy-imports` 가능 | ruff 설정 추가 |
| 네이밍 LOCK: lower.dot/UPPER_SNAKE | CLAUDE.md §7.4 | 파일명은 안 잡힘 | 커스텀 스크립트 |
| S-#/S#_ 구분 | CLAUDE.md §7.1 | 안 잡힘 | 변수명 패턴 검사 |
| datetime.utcnow() 금지 | V1-005 | DTZ 룰 이미 포함 | 커버됨 |
| R7: CORE→COND 단방향 의존성 | PART2 R7 | 안 잡힘 | import 구조 검사 |
| R11: schema_registry.toml 단일 참조 | PART2 R11 | 안 잡힘 | 커스텀 검사 |

---

## GAP-2. CPS 프레임워크 (구조화된 입력) — HIGH

### 영상 원칙
> "Context → Problem → Solution 순서로 정리하면 AI가 제멋대로 하지 않는다"

### VAMOS 현재 상태

- **설계**: 5-Phase Pipeline (Perception→Reasoning→Action→Reflection→Memory)은 CPS의 확장판
- **I-1 IntentFrame 스키마**: intent_id, user_goal, task_type, domain_hint, constraints, risk_flags 정의됨
- **문제**: IntentFrame은 AI 내부 처리용이지, 사용자 입력을 CPS로 구조화하는 템플릿이 아님
- CPS 3단계가 암묵적으로만 존재하고 명시적 로깅이 없음

### 필요 작업

- 사용자 입력 CPS 템플릿 정의 (Context=I-2, Problem=I-1, Solution=I-5 매핑)
- ResponseEnvelope에 CPS 로그 추가 검토
- V1 L0 Session Memory에 CPS 태그 추가

---

## GAP-3. 멱등성 (Idempotency) — CRITICAL

### 영상 원칙
> "어떤 모델에 시켜도 12개의 결과물이 동일하게 나와야 한다"

### VAMOS 현재 상태

| 멱등성 요소 | 설계 | 구현 |
|-----------|------|------|
| Decision Lock (S3 이후 불변) | 스키마 정의됨 | 미구현 |
| Multi-Brain Failover (GPT→Claude→Ollama) | 설계됨 | 미구현 |
| SDAR 3회 재시도 후 롤백 | 설계됨 (V2+) | V1 없음 |
| Snapshot Integrity 검증 | 언급만 | 알고리즘 미정의 |
| **Request-level Idempotency (idempotency_key)** | **미설계** | **미구현** |
| **Event Deduplication** | **미설계** | **미구현** |
| **Partial Failure Recovery (Phase별 재개)** | **미설계** | **미구현** |
| **Multi-Brain 출력 동등성 판단 기준** | **미설계** | **미구현** |

### 필요 작업

- 모든 API에 idempotency_key (trace_id + request_hash) 추가
- 동일 IntentFrame → 동일 Decision → 동일 ResponseEnvelope 검증 테스트
- 5-Phase 중간 실패 시 이전 Phase 결과부터 재개 메커니즘
- seed 고정 (벤치마크에만 있고 일반 파이프라인에 없음)

---

## GAP-4. Evaluation (지속 평가) — CRITICAL

### 영상 원칙
> "Context Relevance, Groundedness 등을 조직 기준에 맞춰 지속 측정"

### VAMOS 현재 상태

| 평가 요소 | 설계 | V1 실행 가능 |
|----------|------|------------|
| 표준 벤치마크 88개 | 정의됨 | **4개만** (MMLU, HumanEval, MBPP, LogicKor) |
| QoD 5요소 (Accuracy/Relevance/Completeness/Safety/Efficiency) | 가중치 정의됨 | **측정 코드 없음** |
| LLM-as-Judge (S7G-071) | 정의됨 | V2 예정 |
| 회귀 테스트 자동화 (S7G-073) | 정의됨 | V2 예정 |
| 벤치마크 스케줄러 (S7G-074) | 정의됨 | V2 예정 |
| 평가 대시보드 (S7G-075) | 정의됨 | V2 예정 |

**구현체는 있으나 연결이 안 된 것:**

| 파일 | 내용 | 문제 |
|------|------|------|
| ragas_evaluator.py | RAGAS 4개 메트릭 (faithfulness, relevancy, precision, recall) | 파이프라인 미연결 |
| deepeval_metrics.py | HallucinationMetric, FaithfulnessMetric | 파이프라인 미연결 |
| promptfoo_config.yaml | 10개 테스트 케이스 | 파이프라인 미연결 |
| minicheck_verifier.py | NLI 기반 검증 | 파이프라인 미연결 |
| giskard_scanner.py | 취약점 스캔 | 파이프라인 미연결 |

**없는 것:**
- 위 도구를 하나로 엮는 Eval Pipeline Orchestrator
- 실행 결과를 저장/비교하는 Result Store
- 자동 실행 스케줄 (CI/CD 연동)
- 기준선(baseline) 대비 회귀 감지

---

## GAP-5. Agent Dog (실시간 모니터링) — CRITICAL

### 영상 원칙
> "Datadog처럼 에이전트 품질을 실시간 모니터링하는 체계"

### VAMOS 현재 상태

**있는 것:**
- Event Logging 134개 이벤트 타입 (설계)
- langfuse_logger.py — LLM 호출 추적
- phoenix_tracer.py — OTLP 트레이스
- lineage_tracker.py — 데이터 계보

**없는 것:**
- 메트릭 집계 파이프라인 (Prometheus 등)
- 이상 탐지 알고리즘 (statistical baseline)
- Alert 라우팅 (Slack/Email/PagerDuty)
- SLO 추적 (P99 latency, error rate)
- 모델 성능 Drift 감지
- 실시간 대시보드 (Grafana 등)

---

## GAP-6. 유지보수 자산화 — HIGH

### 영상 원칙
> "FDE가 떠난 후에도 내부 인원이 직접 유지보수 가능하도록 문서와 규칙을 코드화"

### VAMOS 현재 상태

| 자산 유형 | 설계 | 구현 |
|----------|------|------|
| 설계 문서 (SOT) | 68 + 648개 | 존재 |
| CLAUDE.md (컨텍스트) | 보강 후 ~953줄 예정 | 보강 전 697줄 |
| 스킬 55개 | SKILL.md 존재 | ~30% 실구현 |
| CI/CD | GitHub Actions 8-stage 설계 | **0건** |
| 테스트 | 80%+ 커버리지 목표 | **0건** |
| 패키지 관리 | requirements.txt, package.json 설계 | **0건** |
| Docker | V2 Docker Compose 설계 | **0건** |

---

# 4. SOT/SOT 2 하네스 계층 ��� 원본 정합성 보장

> **핵심 인식**: 린터/CI/테스트는 "코드 형식"을 잡지만, "코드 내용의 정확성"은 SOT/SOT 2가 결정한다.
> SOT/SOT 2가 부정확하면 → PART2가 잘못된 근거로 코드 지시 → 린터가 아무리 좋아도 "형식은 맞지만 내용이 틀린 코드"가 생산된다.

## 4.1 왜 SOT/SOT 2 하네스가 필요한가

### 문서 흐름과 의존 관계

```
SOT (68개 정본)                   ← "무엇을 만들지" 정의
  │
  ├──→ SOT 2 (648개 상세)         ← SOT를 도메인별로 상세화 (현재 진행 중)
  │       │
  │       └──→ CLAUDE.md          ← AI가 읽는 요약 (SOT+SOT 2 기반)
  │
  ���──→ PART2 (구현가이드)          ← "어떻게 코딩하지" (SOT 참조해서 지시)
          │
          └──→ AI 코드 생성        ← PART2 프롬프트 + SOT 참조로 코드 작성
```

### 불일치가 전파되는 경로

```
SOT 내부 불일치:
  MASTER_SPEC: "모듈 25개"  ←→  DESIGN 2.0: "모듈 24개"
  → PART2가 어느 쪽 기준으로 코드 지시할지 모호
  → AI가 매번 다른 쪽을 참조 → 일관성 붕괴

SOT ↔ SOT 2 불일치:
  SOT: "I-1 Intent Detector는 5개 서브컴포넌트"
  SOT 2 (1-2_Auxiliary-Modules): "I-1은 7개 서브컴포넌트로 확장"
  → PART2는 SOT 기준 5개 구현 → SOT 2 기준 2개 누락

SOT → PART2 참조 낙후:
  SOT D2.0-02가 업데이트됨 (4,230줄 → 4,474줄)
  PART2의 "참조: D2.0-02" 는 구버전 기준
  → AI가 PART2 프롬프트대로 코드를 짜도 현재 SOT와 불일치

SOT 2 → SOT 2 내부 불일치:
  SOT 2 (6-3_Agent-Teams): "Lead Agent가 3개 Sub Agent 관리"
  SOT 2 (2-1_Blue-Node): "Lead Agent가 5개 Sub Agent 관리"
  → 648개 파일 간 교차 모순은 수작업으로 발견 불가
```

## 4.2 기존 검증 스킬 현황 — 이미 있는 도구

VAMOS `.claude/skills/` 에 SOT 검증용 스킬이 이미 존재한다. 새로 만들 필요 없이 **하네스 파이프라인에 편입**시킨다.

### SOT 직접 검증 스킬 (3개)

| 스킬 | 역할 | SOT↔SOT 2 | 핵��� 기능 |
|------|------|-----------|---------|
| **`/sot-conflict`** | SOT 파일 간 모순 탐지 | **직접 가능** | `sot2-vs-sot` 명령으로 SOT 2와 SOT 원본 68개 간 불일치 탐지. 온톨로지 매핑(동의어/이의어 자동 그룹핑). `sot2-numbers`, `sot2-terms` 세부 검증 |
| **`/sot-check`** | SOT 원본 직접 대조 | **직접 가능** | `sot2 {항목}` 명령으로 SOT 2 파일 직접 검증. `sot2-lock` 으로 LOCK 값 일관성. `method-c` 로 요약↔Part2 정본 대조. MATCH/SHIFTED/PARTIAL/MISMATCH/NOT_FOUND 판정 |
| **`/sot2-cross-ref`** | SOT 2 교차참조 검�� | **직접 가능** | SOT 2 폴더 간 + Part2 참조 무결성 검증. `all` 명령으로 전체 교차검증 |

### SOT 간접 검증 스킬 (4개)

| 스킬 | 역할 | SOT↔SOT 2 | 핵심 기능 |
|------|------|-----------|---------|
| **`/cross-match`** | EA 간 교차매칭 | **간접** | C1(수치)~C8(참조) 8가지 비교 유형. EA가 SOT에서 추출되었으므로 결과적으로 SOT 불일치 탐지 |
| **`/cross-examine`** | 에이전트 간 능동적 심문 | **간접** | Examiner/Respondent 역할로 추출 근거 타당성 질문. SUFFICIENT/INSUFFICIENT/CONTRADICTORY 판정 |
| **`/validate`** | 2계층 검증 (결정론+AI) | **직접 가능** | `sot2 {파일}` 명령으로 SDV-1~SDV-7 검증. SDV-4: LOCK 값 Part2 정본 일치 확인. SSV-1~SSV-3 AI 의미 검증 |
| **`/fact-audit`** | 멀티에이전트 팩트 감사 | **간접** | Auditor/Challenger/Judge 3역할 토론. CONFIRMED/DISPUTED/NEEDS_REVIEW 판정 |

### 지원 도구 스킬 (5개)

| 스킬 | 역할 | 용도 |
|------|------|------|
| **`/completeness-map`** | 오류 유형별 커버리지 행렬 | `sot2` 명령으로 SOT 2 전용 8개 에러 유형 커버리지 확인 |
| **`/hallucination-check`** | atomic claim 검증 | EA를 원자적 주장으로 분해 후 SOT에서 개별 fact 검증 |
| **`/integrity`** | SOT 무결성 모니터 | SOT 변경 감지 + 영향 범위 분석 |
| **`/sot-graph`** | 관계 그래프 시각화 | 문서 간 의존성 분석 |
| **`/audit`** | 적대적 감사 | EA 환각/변조/누락 탐지 |

## 4.3 SOT 하���스 파이프라인 설계

### 파이프라인 A: SOT 내부 정합성 (SOT 68개 자체)

**실행 시점**: V0 진입 전 + SOT 문서 수정 시마다

```
Step A-1: /sot-conflict scan
  → SOT 68개 파일 간 수치/정의/LOCK 값 모순 탐지
  → 보강전략 §2에서 발견된 7건 불일치 포함

Step A-2: /sot-check all
  → 핵심 파일 8개 (CLAUDE.md §4)의 줄 수, 필드 수, LOCK 값 직접 대조

Step A-3: /integrity snapshot
  → 현재 SOT 상태 스냅샷 저장 (이후 변경 감지 기준선)

산출물: sot_conflict_report.json + sot_check_all.json + integrity_snapshot.json
판정: CONFLICT 0건 → PASS / 1건 이상 → 수정 후 재검증
```

### 파이프라인 B: SOT ↔ SOT 2 교차 검증

**실행 시점**: SOT 2 상세화 작업 완료 시마다

```
Step B-1: /sot-conflict sot2-vs-sot
  → SOT 2 (648개) vs SOT 원본 (68개) 모순 탐지
  → 수치 모순, 용어 불일치, LOCK 값 분산 확인

Step B-2: /sot2-cross-ref all
  → SOT 2 내부 36개 도메인 간 교차 참조 무결성
  → SOT 2 → Part2 참조 유효성

Step B-3: /sot-check sot2-lock
  → SOT 2에 기재된 모든 LOCK 값이 SOT 원본과 일치하는지

Step B-4: /validate sot2-all
  → SOT 2 파일 구조 검증 (SDV-1~SDV-7)
  → LOCK 값 Part2 정본 일치 (SDV-4)
  → AI 의미 검증 (SSV-1~SSV-3)

산출물: sot2_conflict.json + sot2_crossref.json + sot2_lock.json + sot2_validate.json
판정: 
  CLEAN: CONFLICT 0건 + MISMATCH 0건
  WARN:  CONFLICT ≤3건 (MEDIUM 이하)
  BLOCK: CONFLICT 1건+ (CRITICAL) → SOT 2 수정 필요
```

### 파이프라인 C: SOT/SOT 2 → PART2 참조 유효성

**실행 시점**: PART2 구현 세션 시작 전

```
Step C-1: /sot-check method-c {STEP/Phase}
  → 해당 STEP/Phase의 "참조 SOT 문서"가 최신인지 확인
  → 방식 C 요약 �� Part2 정본 대조

Step C-2: /sot-conflict sot2-vs-part2
  → SOT 2 상세 내용이 PART2 구현 지시와 일치하는지
  → 예: SOT 2에서 필드가 추가되었는데 PART2에는 반영 안 된 경우

Step C-3: /completeness-map sot2
  → SOT 2 내용 중 PART2에 반영되지 않은 항목 탐지

산출물: method_c_check.json + sot2_vs_part2.json + completeness.md
판정: 미반영 항목 0건 → PASS / 1건 이상 → PART2 업데이트 또는 의도적 제외 확인
```

## 4.4 SOT 하네스 실행 타이밍

```
[SOT 문서 수정 시]
  → 파이프라인 A (SOT 내부 정합성) 자동 트리거

[SOT 2 상세화 작업 완료 시]  ← 현재 진행 중인 작업
  → 파이프라인 B (SOT↔SOT 2 교차 검증) 실행

[PART2 구현 세션 ��작 전]
  → 파이프라인 C (SOT→PART2 참조 유효성) 실행

[CLAUDE.md 보강 시]
  → 보강전략 8단계 검증 (기존 계획 §9)
  → + 파이프라인 A 결과를 CLAUDE.md에 반영
```

## 4.5 SOT 하네스 자동화 옵션

### 현재 (수동 실행)

각 파이프라인을 Claude Code에서 수동으로 `/sot-conflict`, `/sot-check` 등 실행.

### 향후 (Hook 자동화, 선택적)

```
# .claude/settings.json에 추가 가능 (향후)
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "condition": "filePath.includes('docs/sot/')",
        "command": "echo '⚠️ SOT 파일 수정됨 — /sot-conflict scan 실행 권장'"
      },
      {
        "matcher": "Write|Edit",
        "condition": "filePath.includes('docs/sot 2/')",
        "command": "echo '⚠️ SOT 2 파일 수��됨 — /sot-conflict sot2-vs-sot 실행 권장'"
      }
    ]
  }
}
```

> 현재 단계에서는 수동 실행으로 충분. 작업 흐름이 안정되면 Hook으로 자동화.

---

# 5. 전체 하네스 아키텍처 — 5계층 구조

## 5.1 하네스 계층도

이전 계획(§3)에서는 PART2 코드 하네스(린터/CI/테스트)만 다루었다. SOT/SOT 2 계층을 포함한 **전체 하네스 아키텍처**는 5계층이다:

```
┌─────────────────────────────────────────────────────────────────────┐
│ [L1] SOT 하네스 — 원본 정합성                                       │
│   SOT 68개 파일 간 모순 탐지                                        │
│   도구: /sot-conflict, /sot-check, /integrity                      │
│   판정: CONFLICT 0건 = PASS                                        │
├─────────────────────────────────────────────────────────────────────┤
│ [L2] SOT 2 ��네스 — 상세 일관성                                     │
│   SOT 2 (648개) ↔ SOT (68개) 교차 검증                             │
���   도구: /sot-conflict sot2-vs-sot, /sot2-cross-ref, /validate sot2 │
│   판정: MISMATCH 0건 = CLEAN                                       │
├───────────────────────────��─────────────────────────────────────────┤
│ [L3] CLAUDE.md 하네스 — AI 컨텍스트 정확��                          │
│   CLAUDE.md가 SOT/SOT 2를 정확히 반영하는지                         │
│   도구: 보강전략 V1.0 (8단계 검증 스킬)                              │
│   판정: GOLD/SILVER/BRONZE/REJECT                                   │
├─────��─────────────────���───────────────────────────────────���─────────┤
│ [L4] PART2 → 코드 하���스 — 구현 규칙 강제                           │
│   PART2 참조가 최신 SOT 기준인지 + 코드 린트/테스트                  │
│   도구: ruff + vamos_lint + pytest + CI                             │
│   판정: ruff 0 errors + pytest PASS + CI GREEN                     │
├────────────────────────���──────────────────────────────────��─────────┤
│ [L5] Eval 하네스 — 지속 품질 측정                                    │
│   생성된 코드/시스템의 실제 품질 평가                                 │
│   도���: ragas + deepeval + promptfoo + 멱등성 테스트                 │
���   판정: QoD ≥ 기준값 + 회귀 없음                                    │
└────────��────────────────────────────────────────────────────────────┘
```

## 5.2 계층 간 의존 관계

```
L1 (SOT 정합)
 ↓  L1 PASS여야 L2 결과가 의미 있음
L2 (SOT↔SOT 2 일관)
 ↓  L2 CLEAN이어야 CLAUDE.md 보강이 정확함
L3 (CLAUDE.md 정확)
 ↓  L3 SILVER+ 여야 AI가 올바른 맥락으로 코드 생성
L4 (코드 린트/테스트)
 ↓  L4 GREEN이어야 코드 품질 보장
L5 (Eval 품질)
     L5 QoD 기준 충족 → 배포 가능
```

**핵심 원칙**: 상위 계층이 실패하면 하위 계층 결과를 신뢰할 수 없다.
- L1 CONFLICT → CLAUDE.md 보강해봤자 틀린 정보 기반
- L2 MISMATCH → PART2가 SOT 2 최신 내용과 어긋남
- L3 REJECT → AI가 잘못된 맥락으로 코드 생성

## 5.3 계층별 실행 빈도

| 계층 | 실행 시점 | 빈도 |
|------|---------|------|
| L1 | SOT 파일 수정 시 | 낮음 (SOT는 안��적) |
| L2 | SOT 2 상세화 작업 완료 시 | **높음 (현재 진행 중)** |
| L3 | CLAUDE.md 보강 시 | 1회 (보강전략 적용 시) |
| L4 | 코드 생성 시마다 | **매우 높음 (매 커밋)** |
| L5 | V1 Phase 5 이후 | 주기적 (주 1회+) |

## 5.4 기존 실행 계획과의 통합

기존 5단계 계획에 SOT 하네스를 **선행 단계**로 추가:

```
[0단계] SOT 정합성 확인 (신규)        ← L1 + L2
  │  현재 SOT 2 작업 진행 중이므로 즉시 실행 가능
  │  기존 스킬 활용 — 새 도구 개발 불필요
  │
[1단계] Layer 0: PART2 기본 설정       ← L4 기반
  │
[2단계] Layer 1: VAMOS 고유 규칙       ← L4 확장
  │
[3단계] CLAUDE.md 보강                 ← L3
  │  L1+L2 결과를 반영하여 보강
  │
[4단계] V0 구현 재개                   ← L4 위에서 실행
  │  매 세션 시작 전 /sot-check method-c ��행
  │
[5단계] Eval + 모니터링               ← L5
```

## 5.5 SOT 2 작업 시 검증 워크플로우 (현재 적용 가능)

현재 SOT 2 상세화 작업을 진행 중이므로, **지금 바로** 적용할 수 있는 워크플로우:

```
SOT 2 도메인 상세화 작업 완료 (예: 6-3_Agent-Teams-PARL)
  │
  ├─ Step 1: /sot-conflict sot2-vs-sot
  │    → 이 도메인이 SOT 원본과 모순 없는지 확인
  │
  ├─ Step 2: /sot2-cross-ref 6-3
  │    → 이 도메인이 다른 SOT 2 도메인과 모순 없는지 확인
  │
  ├─ Step 3: /validate sot2 6-3_Agent-Teams-PARL
  │    → 구조 검증 (SDV-1~7) + LOCK 일치 (SDV-4)
  │
  └─ Step 4: 결과 확인
       → CLEAN: 다음 도메인으로 진행
       → MISMATCH: 수정 후 Step 1 재실행
```

> **이 워크플로우는 린터/CI 없이도 지금 바로 실행 가능합니다.**
> SOT 2 상세화 작업의 품질을 즉시 높이는 가장 빠른 하네스입니다.

---

# 6. 최종 실행 계획: 5단계

## 6.1 전체 순서도 (SOT 계층 포함)

```
현재 상태
 │  SOT(68) + SOT 2(648) 상세화 진행 중
 │  PART2 구현가이드 존재하나 실행 하네스 부재
 │  AI 작업 시 일관성 부족 체감
 │
 ▼
[0단계] SOT 정합성 확인 (신규)                     소요: 1~2시간    ← L1+L2
 │  /sot-conflict scan → SOT 68개 내부 모순 확인
 │  /sot-conflict sot2-vs-sot → SOT↔SOT 2 교차 검증
 │  /sot2-cross-ref all → SOT 2 내부 교차참조 검증
 │  = "원본 문서가 정확해야 이후 모든 작업이 의미 있음"
 │  ※ 기존 스킬 활용 — 새 도구 개발 불필요, 지금 바로 실행 가능
 │
 ▼
[1단계] Layer 0: PART2 기본 설정 파일 생성          소요: 30분       ← L4 기반
 │  pyproject.toml + ruff + pytest + CI yaml
 │  = "코드가 최소한의 규칙을 따르게 강제하는 기반"
 │
 ▼
[2단계] Layer 1: VAMOS 고유 규칙 린터 추가          소요: 2~3시간    ← L4 확장
 │  DEC-002 import 금지 + 네이밍 LOCK + R2 검사
 │  = "VAMOS 전용 규칙까지 코드 레벨에서 강제"
 │
 ▼
[3단계] CLAUDE.md 보강전략 V1.0 적용               소요: 반나절      ← L3
 │  697줄 → ~953줄, §21~§27 추가
 │  0단계 결과 반영 (SOT 불일치 해소 후 보강)
 │  = "AI가 VAMOS를 정확히 이해하는 컨텍스트 확보"
 │
 ▼
[4단계] V0 구현 재개 (PART2 순서대로)              소요: PART2 기준 1~2주  ← L4
 │  0~3단계 하네스 위에서 구현
 │  매 세션 시작 전: /sot-check method-c (SOT→PART2 참조 유효성)
 │  매 코드 생성마다: 린터+테스트 자동 검증
 │
 ▼
[5단계] Eval + 모니터링 (V1 Phase 5)              소요: V1 일정 내  ← L5
    기존 평가 도구 파이프라인 연결
    기본 메트릭 수집 + Alert 규칙
```

## 6.2 접근 방식: 계층형 (Layer 0 → 1 → 2)

**순수 PART2 중심도 아니고, 순수 VAMOS 전체 분석도 아닌, 계층형 접근을 채택한다.**

| Layer | 범위 | 시점 | 내용 |
|-------|------|------|------|
| **Layer 0** | PART2 기본 설정 | 즉시 (1단계) | ruff 13개 룰, pytest, mypy, CI yaml — 범용 Python 품질 |
| **Layer 1** | VAMOS 핵심 규칙 | V0 병행 (2단계) | DEC-002, 네이밍 LOCK, R2, R7 — VAMOS 고유 코드 규칙 |
| **Layer 2** | VAMOS 전체 규칙 | V1 진입 시 (3단계+) | 187개 모듈 명명, 15개 교차 용어, SOT 2 연동 |

**이유:**
- Layer 0만으로는 VAMOS 고유 규칙(네이밍, import 금지)을 잡지 못함
- Layer 2를 처음부터 하면 CLAUDE.md 보강이 선행 필요 + 과잉 설계 위험
- Layer 0 → 1 → 2 순서로 올라가면 가장 적은 노력으로 점진적 일관성 확보

---

# 7. 1단계 상세: Layer 0 — PART2 기본 설정 파일 생성

> **소요 시간**: 30분
> **근거**: PART2 구현가이드 V0-STEP-1 (line 194~244) + V0-STEP-6 (line 1375~1550)
> **전제**: PART2에 이미 정의된 설정을 그대로 실제 파일로 만드는 작업

## 7.1 산출물 목록

| # | 파일 | 내용 | PART2 근거 |
|---|------|------|-----------|
| 1 | `backend/pyproject.toml` | Poetry 의존성 + ruff + mypy 설정 | line 1490~1536 |
| 2 | `.github/workflows/quality-python.yml` | ruff lint + mypy CI | line 1410~1430 |
| 3 | `.github/workflows/test-python.yml` | pytest + coverage CI | line 1432~1450 |
| 4 | `backend/tests/__init__.py` | 테스트 패키지 초기화 | PART2 구조 |
| 5 | `backend/tests/conftest.py` | pytest fixture, async 지원, Ollama 스킵 | line 1541~1545 |

## 7.2 pyproject.toml 상세

PART2 line 1490~1536에서 직접 추출:

```toml
[tool.poetry]
name = "vamos-backend"
version = "0.1.0"
description = "VAMOS AI Backend"
python = "^3.11"

[tool.poetry.dependencies]
python = "^3.11"
pydantic = ">=2.0.0,<3.0"
langchain-core = ">=0.3.0,<1.0"         # DEC-002 Allowlist
langchain-community = ">=0.3.0,<1.0"    # DEC-002 Allowlist
langchain-openai = ">=0.2.0,<1.0"       # DEC-002 Allowlist
langgraph = ">=0.2.0,<1.0"              # LOCK: Agent Workflow
chromadb = ">=0.5.0,<1.0"               # V1 Vector DB
# ... (PART2 PHASE_B3 정본 기준 전체 의존성)

[tool.poetry.group.dev.dependencies]
pytest = ">=8.3.0,<9.0"
pytest-asyncio = ">=0.24.0,<1.0"
pytest-cov = ">=6.0.0,<7.0"
ruff = ">=0.8.0,<1.0"
mypy = ">=1.0"

[tool.ruff]
target-version = "py311"
line-length = 100                        # PHASE_B6 정본

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "S", "B", "A", "C4", "DTZ", "T20", "ICN"]

[tool.mypy]
python_version = "3.11"
strict = true
```

## 7.3 CI 워크플로우 상세

### quality-python.yml (PART2 line 1410~1430)

```yaml
name: Python Quality
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          cd backend
          pip install poetry
          poetry install
      - name: Ruff lint
        run: cd backend && poetry run ruff check .
      - name: Mypy type check
        run: cd backend && poetry run mypy .
```

### test-python.yml (PART2 line 1432~1450)

```yaml
name: Python Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          cd backend
          pip install poetry
          poetry install
      - name: Run pytest
        run: cd backend && poetry run pytest tests/ -v --tb=short --cov=. --cov-report=term-missing
```

## 7.4 conftest.py 상세

```python
"""VAMOS 테스트 공통 Fixture (PART2 line 1541~1545 기반)"""
import os
import pytest

# Ollama 의존 테스트 스킵 (M-10)
OLLAMA_AVAILABLE = bool(os.getenv("OLLAMA_HOST"))

@pytest.fixture
def skip_without_ollama():
    if not OLLAMA_AVAILABLE:
        pytest.skip("Ollama not available")
```

## 7.5 완료 기준

- [ ] `backend/pyproject.toml` 파일 생성됨
- [ ] `poetry install` 정상 실행됨
- [ ] `poetry run ruff check .` 실행 가능
- [ ] `poetry run pytest tests/` 실행 가능 (0 tests collected OK)
- [ ] `.github/workflows/` 두 파일 생성됨

---

# 8. 2단계 상세: Layer 1 — VAMOS 고유 규칙 린터 추가

> **소요 시간**: 2~3시간 (V0-STEP-2~3과 병행 가능)
> **근거**: CLAUDE.md §7 LOCK 결정사항 + PART2 §1.3 R1~R11

## 8.1 pyproject.toml 보강 — VAMOS 전용 ruff 규칙

Layer 0의 ruff 설정에 VAMOS 고유 규칙을 추가:

```toml
# === Layer 1 추가 ===

[tool.ruff.lint.flake8-tidy-imports.banned-api]
# DEC-002: langchain 본체 패키지 import 금지
"langchain".msg = "DEC-002: langchain 본체 import 금지. langchain-core/community/openai만 허용"
"langchain.chains".msg = "DEC-002: langchain.chains import 금지"
"langchain.agents".msg = "DEC-002: langchain.agents import 금지"

[tool.ruff.lint.per-file-ignores]
# 테스트 파일은 보안 린트 완화
"tests/**/*.py" = ["S101"]  # assert 사용 허용
```

## 8.2 VAMOS 커스텀 린터 — scripts/vamos_lint.py

ruff로 잡을 수 없는 VAMOS 고유 규칙을 검사하는 커스텀 스크립트:

```python
"""
VAMOS 커스텀 린터 (Layer 1)

PART2 R1~R11 + CLAUDE.md LOCK 결정사항 중 ruff로 검사 불가능한 규칙 검증.

검사 항목:
  VL-001: class Config: 사용 금지 (R2, Pydantic v2는 model_config 사용)
  VL-002: S-#(모듈ID) vs S#_(상태) 네이밍 혼동 검사
  VL-003: CORE→COND 역방향 import 금지 (R7)
  VL-004: LOCK/FREEZE 상수 재할당 검사 (R5)
  VL-005: 파일명 규칙 (events=lower.dot, failures=UPPER_SNAKE)
"""
```

### VL-001: class Config 금지 (R2)

```python
# Pydantic v2에서는 model_config = ConfigDict(...) 사용
# class Config: 는 v1 패턴이므로 금지

검사: "class Config:" 패턴이 Pydantic 모델 내부에 있으면 에러
예외: Pydantic과 무관한 설정 클래스는 허용
```

### VL-002: S-#/S#_ 네이밍 구분

```python
# CLAUDE.md §7.1: S-#=모듈 ID(하이픈), S#_=상태(언더스코어)
# 혼동 방지 검사

검사:
  - 변수명에 "S1_", "S2_" 등이 모듈 ID 맥락에서 사용되면 경고
  - "S-1", "S-2" 등이 상태 맥락에서 사용되면 경고
```

### VL-003: CORE→COND 역방향 import 금지 (R7)

```python
# orange_core/ (CORE) 모듈이 COND 모듈을 import하면 금지
# CORE→COND 단방향만 허용

검사: orange_core/ 파일에서 COND 모듈 import 탐지
```

### VL-004: LOCK/FREEZE 상수 재할당

```python
# LOCK 값은 런타임 변경 불가 (R5)
# config.v1.toml의 LOCK 주석이 달린 값을 코드에서 재할당하면 경고

검사: LOCK으로 표시된 config 키를 runtime에서 덮어쓰는 패턴 탐지
```

### VL-005: 파일명 규칙

```python
# CLAUDE.md §7.4 네이밍 LOCK
# event 이름: lower.dot (예: oc.intent.parsed)
# failure 코드: UPPER_SNAKE (예: INTENT_PARSE_FAILED)
# fallback: FB_UPPER_SNAKE (예: FB_INTENT_RETRY)

검사: events/ 디렉토리 내 파일명, failure/fallback 상수 네이밍
```

## 8.3 CI 통합

quality-python.yml에 vamos_lint 단계 추가:

```yaml
      - name: VAMOS custom lint
        run: cd backend && python ../scripts/vamos_lint.py .
```

## 8.4 완료 기준

- [ ] pyproject.toml에 VAMOS 전용 ruff banned-api 추가됨
- [ ] scripts/vamos_lint.py 생성 및 5개 규칙 (VL-001~005) 구현
- [ ] CI yaml에 vamos_lint 단계 추가됨
- [ ] 기존 코드에 대해 vamos_lint 실행 시 에러 0건 (또는 알려진 위반 목록화)

---

# 9. 3단계 상세: CLAUDE.md 보강전략 V1.0 적용

> **소요 시간**: 반나절
> **근거**: `D:\VAMOS\CLAUDE 보강전략 V1.0.md`
> **전제**: 1~2단계 완료 후 실행 (하네스 인프라 위에서 AI가 정확한 맥락으로 작업)

## 9.1 보강 요약

| 구분 | 현재 | 보강 후 |
|------|------|--------|
| 줄 수 | 697줄, 20개 섹션 | ~953줄, 27개 섹션 |
| SOT 2 참조 | 0% (648개 파일 무시) | 36개 도메인 라우팅 테이블 |
| 모듈 커버리지 | 81개만 (COND 106개 누락) | 187개 전체 |
| 파일 경로 | 파일명만 | 전체 경로 명시 |
| 교차 용어 | 없음 | 15개 동음이의어 주의사항 |
| 스킬 참조 | 없음 | 55개 스킬 + TOOL_GUIDE 경로 |

## 9.2 보강전략 V1.0 Phase A 실행 순서 (5 세션)

보강전략 V1.0 문서에 정의된 세션별 실행:

| 세션 | 작업 | 대상 섹션 |
|------|------|---------|
| A-1 | 기존 섹션 수정: 경로/줄 수/갱신일 | §2, §4, 헤더 |
| A-2 | 모듈 섹션 보강: EVX 테이블 + COND 106개 | §6 |
| A-3 | 경로 보강: 특화 시스템 + 참조 경로 | §17, §18 |
| A-4 | 신규 섹션 전반: SOT 2 라우팅 + COND 상세 + 교차 용어 | §21, §22, §23 |
| A-5 | 신규 섹션 후반: STEP7 매핑 + 의존성 + KG + .claude 참조 | §24~§27 |

## 9.3 보강 후 효과 (하네스 관점)

| 효과 | 설명 |
|------|------|
| AI 맥락 정확도 향상 | SOT 2 도메인 질문 시 정확한 파일 경로로 유도 |
| 동음이의어 혼동 방지 | 15개 교차 용어 명시 (QoD, Gate, Pipeline 등) |
| 모듈 인식 완전성 | 187개 전체 모듈을 AI가 인식 |
| 하네스 연결 | §27에서 55개 스킬 + Hook 경로 참조 → AI가 하네스 도구를 인식 |

## 9.4 보강 후 검증 (보강전략 Phase B)

8개 검증 스킬로 CLAUDE.md 정확성 확인:

```
/claude-md-sot-conflict     → SOT 간 모순 탐지
/claude-md-hallucination    → atomic claim 검증 (95%+ VERIFIED 목표)
/claude-md-fact-audit       → 3 Agent 토론 재검증
/claude-md-cross-examine    → 핵심 수치 근거 추적
/claude-md-symbolic         → 수학적 결정론 검증 (AI 0%)
/claude-md-consensus        → 50개 수치 3회 다수결
/claude-md-completeness     → SOT 대비 누락 탐지
/claude-md-final-review     → GOLD/SILVER/BRONZE/REJECT 판정
```

---

# 10. 4단계 상세: V0 구현 재개 — 하네스 위에서

> **소요 시간**: PART2 기준 1~2주
> **근거**: PART2 §2 V0 구현
> **전제**: 1~3단계 완료 (린터 + CLAUDE.md 보강 위에서 실행)

## 10.1 변경된 V0 워크플로우

### 이전 (하네스 없음)

```
V0-STEP-N AI 프롬프트 → Claude 코드 생성 → 눈으로 확인 → 다음 STEP
```

### 이후 (하네스 있음)

```
V0-STEP-N AI 프롬프트 → Claude 코드 생성
  → ruff check (Layer 0: 범용 Python 품질)
  → vamos_lint (Layer 1: VAMOS 고유 규칙)
  → pytest (최소 테스트)
  → 모두 PASS → 다음 STEP
  → FAIL → 위반 사항 수정 후 재실행
```

## 10.2 V0-STEP별 하네스 적용

| STEP | 기존 (PART2) | 하네스 추가 |
|------|-------------|-----------|
| STEP-1: 스캐폴딩 | monorepo 초기화 | **1단계에서 이미 절반 완료** (pyproject.toml, CI yaml) |
| STEP-2: 스키마 | 25개 Pydantic 모델 | ruff(DTZ) + vamos_lint(VL-001: class Config 금지) |
| STEP-3: config | config.v1.toml | vamos_lint(VL-004: LOCK 재할당 금지) |
| STEP-4: IPC 브릿지 | Rust↔Python JSON-RPC | pytest IPC 테스트 |
| STEP-5: 최소 파이프라인 | 5-Phase skeleton | pytest E2E 테스트 + vamos_lint(VL-003: 의존성 방향) |
| STEP-6: CI + 테스트 | GitHub Actions | **1~2단계에서 이미 완료** |

## 10.3 V0 완료 체크리스트 (PART2 + 하네스)

PART2 원본 13항목 + 하네스 3항목 추가:

```
PART2 원본:
- [ ] monorepo 구조 생성 완료
- [ ] 25개 Pydantic 스키마 정의 완료
- [ ] JSON-RPC 통신 동작 확인
- [ ] LangGraph 5-Phase 파이프라인 최소 동작
- [ ] 사용자 입력 → IntentFrame → Decision → Response 흐름 확인
- [ ] config.v1.toml 로드 확인
- [ ] JSONL 로깅 동작 확인
- [ ] pytest 실행 + 기본 통과
- [ ] EventTypeRegistry / FailureCodeRegistry / FallbackRegistry 정의 완료
- [ ] L0 Session Memory (SQLite) 기본 CRUD 동작
- [ ] Tauri IPC 브릿지 동작 확인
- [ ] 기본 E2E 테스트 (사용자 입력 → 응답) 통과
- [ ] V0 비용 = ₩0 (로컬 전용) 확인

하네스 추가:
- [ ] ruff check PASS (0 errors)
- [ ] vamos_lint PASS (VL-001~005, 0 errors)
- [ ] CI 워크플로우 (quality-python + test-python) 정상 실행
```

---

# 11. 5단계 상세: Eval + 모니터링

> **소요 시점**: V1 Phase 5 (통합 테스트 단계)
> **근거**: PART2 §3.5 V1 Phase 5 + 영상의 Evaluation/Agent Dog 개념

## 11.1 최소 Eval Pipeline 구축

기존 개별 스크립트를 하나의 실행 체인으로 연결:

```
/eval-run 실행
  ├── ragas_evaluator.py    → faithfulness, relevancy, precision, recall
  ├── deepeval_metrics.py   → HallucinationMetric, FaithfulnessMetric
  ├── promptfoo             → 10개 테스트 케이스
  └── minicheck_verifier.py → NLI 검증
      ↓
  결과 저장 → SQLite eval_results 테이블
      ↓
  기준선(baseline) 대비 회귀 감지
      ↓
  PASS / REGRESSION_DETECTED 판정
```

## 11.2 QoD 5요소 실측 코드

현재 가중치만 정의 → 각 요소의 실제 계산 함수를 RAGAS 메트릭과 매핑:

| QoD 요소 | 가중치 | RAGAS 메트릭 매핑 |
|---------|--------|-----------------|
| Accuracy | 0.30 | faithfulness |
| Relevance | 0.25 | answer_relevancy |
| Completeness | 0.20 | context_recall |
| Safety | 0.15 | (커스텀: Guardrails 통과율) |
| Efficiency | 0.10 | (응답시간 기반 점수) |

## 11.3 최소 모니터링 스택 (V1)

V1은 로컬 환경이므로 경량 모니터링:

| 항목 | V1 구현 | 도구 |
|------|--------|------|
| 메트릭 수집 | SQLite metrics 테이블 | 자체 구현 (JSONL → SQLite 집계) |
| 기본 Alert | 비용 80% 도달, Self-check FAIL 연속 3회 | I-20 Failure/Fallback Manager |
| Health Check | `/health` 엔드포인트 | JSON-RPC |
| 로그 조회 | JSONL 파일 기반 검색 | 자체 스크립트 |

V2에서 Langfuse/Phoenix Docker 서비스 + PostgreSQL 기반으로 확장.

## 11.4 멱등성 테스트 (V1 Phase 1 이후)

```python
def test_idempotency():
    """동일 입력 3회 실행 → 동일 결과 확인"""
    intent = create_test_intent("오늘 코스피 분석해줘")
    
    results = []
    for _ in range(3):
        result = pipeline.run(intent, seed=42)
        results.append(result)
    
    # Decision 구조 동일성 확인
    assert results[0].decision.conclusion == results[1].decision.conclusion == results[2].decision.conclusion
    
    # ResponseEnvelope 구조 동일성 확인
    assert results[0].answer.summary == results[1].answer.summary == results[2].answer.summary
```

## 11.5 역할별 Eval 프로필 (영상의 "조직 맞춤형 평가")

| RBAC 역할 | Self-check 임계값 | 허용 자율도 | Eval 성향 |
|----------|-----------------|-----------|----------|
| VIEWER (L0) | P0:70 (기본) | 읽기 전용 | 높은 정확도 요구 |
| OPERATOR (L1) | P0:70, P1:75 | 실행 가능 | 균형 |
| ADMIN (L2, P2) | P0:70, P1:75, P2:80 | 관리 가능 | 탐색적 허용 |
| OWNER (L3, P2) | 동일 | 최대 | 동일 (Non-goal은 절대 금지) |

---

# 12. 하네스 용어 → VAMOS 적용 매핑표

## 12.1 핵심 개념 매핑

| 영상 용어 | 영상 정의 | VAMOS 현재 구현체 | 하네스 구축 후 |
|----------|---------|-----------------|-------------|
| **하네스** | AI를 틀에 가두는 규칙 | Gate 5개 + LOCK 28개 (설계) | + ruff + vamos_lint + CI + pytest |
| **린터** | 코드 규칙 강제 | 네이밍 LOCK (문서만) | ruff 13룰 + vamos_lint VL-001~005 |
| **멱등성** | 반복해도 같은 결과 | Decision Lock (스키마만) | + idempotency test + seed 고정 |
| **CPS** | Context→Problem→Solution | 5-Phase Pipeline (설계) | + CPS 태그 로깅 |
| **DDD** | 도메인 주도 설계 | BLUE NODE 6개 도메인 | + VL-003 의존성 방향 검사 |
| **Evaluation** | AI 성능 평가 | ragas/deepeval (개별 스크립트) | + Eval Pipeline Orchestrator |
| **RAG** | 검색 후 답변 | I-2 + 6단계 RAG Pipeline (설계) | 동일 (V0에서 기본 구현) |
| **할루시네이션** | AI 거짓말 | EvidenceGate (설계) | + /claude-md-hallucination 스킬 |
| **Agent Dog** | 에이전트 모니터링 | langfuse/phoenix (스크립트) | + SQLite 메트릭 + Alert 규칙 |
| **AX** | AI 대전환 | V0→V1→V2→V3 로드맵 | 동일 (하네스가 전환 품질 보장) |

## 12.2 VAMOS 고유 하네스 요소 (영상에 없는 것)

| VAMOS 고유 | 설명 | 하네스 역할 |
|-----------|------|-----------|
| **5-Gate** (Policy/Approval/Cost/Evidence/SelfCheck) | 의사결정 검증 체계 | 코드 린터보다 상위 — 정책 린터 |
| **LOCK 28개 네임스페이스** | 변경 불가 결정사항 | 시스템 레벨 린터 (config frozen) |
| **7개 불변 구역** | safety, cost_ceiling 등 | 최상위 하네스 (ABSOLUTE) |
| **문서 위계 ABSOLUTE** | RULE > PLAN > DESIGN LOCK | 문서 하네스 (충돌 해소 규칙) |
| **8단계 검증 파이프라인** (보강전략) | CLAUDE.md 검증 | 메타 하네스 (하네스의 하네스) |
| **55개 .claude 스킬** | 검증/감사/추출 자동화 | 스킬 하네스 (Claude 작업 제어) |
| **deterministic_validator.py** | EA/CM JSON 검증 | 데이터 하네스 (산출물 품질) |

---

# 13. 위험 요소 및 대응

| # | 위험 | 심각도 | 대응 |
|---|------|--------|------|
| 1 | **SOT 내부 불일치가 이미 존재** (보강전략에서 7건 발견) | **HIGH** | 0단계에서 /sot-conflict scan으로 전수 확인 후 수정 |
| 2 | **SOT 2 상세화 중 SOT 원본과 어긋남** | **HIGH** | SOT 2 작업 완료 시마다 /sot-conflict sot2-vs-sot 실행 |
| 3 | **PART2 참조 SOT가 구버전 기준** | **MEDIUM** | V0 세션 시작 전 /sot-check method-c로 참조 유효성 확인 |
| 4 | Layer 1 커스텀 린터 오탐 (false positive) | MEDIUM | 초기에는 경고(warn) 모드로 실행, 안정화 후 에러(error) 전환 |
| 5 | CI가 너무 엄격해서 개발 속도 저하 | MEDIUM | V0에서는 ruff + pytest만 필수, vamos_lint는 경고만 |
| 6 | CLAUDE.md 보강 중 기존 내용 변질 | HIGH | 보강전략 RULE-A1: "기존 §1~§20 의미 변경 금지. 경로 추가, 수치 갱신, 형식 변환만" |
| 7 | 하네스 구축에 시간 과투자 | MEDIUM | Layer 0(30분) + Layer 1(2~3시간)으로 제한. Layer 2는 V1 진입 시 |
| 8 | PART2 설정과 VAMOS 규칙 충돌 | LOW | PART2가 기반, VAMOS 규칙은 레이어로 추가 (override 아님 augment) |

---

# 14. 성공 기준

## 14.1 단계별 성공 기준

| 단계 | 성공 기준 | 측정 방법 |
|------|---------|---------|
| **0단계** | **SOT 내부 CONFLICT 0건 + SOT↔SOT 2 MISMATCH 0건 (CRITICAL)** | `/sot-conflict scan` + `/sot-conflict sot2-vs-sot` |
| 1단계 | ruff + pytest + CI 실행 가능 | `poetry run ruff check .` PASS |
| 2단계 | VAMOS 고유 규칙 5개 검사 가능 | `python vamos_lint.py .` PASS |
| 3단계 | CLAUDE.md 187개 모듈 + 36개 도메인 인식 + L1/L2 결과 반영 | 보강전략 Phase B 검증 SILVER 이상 |
| 4단계 | V0 완료 체크리스트 16항목 + SOT→PART2 참조 유효성 | PART2 13항목 + 하네스 3항목 + `/sot-check method-c` |
| 5단계 | QoD ≥ 0.70 (V1 최소), Eval Pipeline 동작 | /eval-run 실행 + 결과 저장 |

## 14.2 최종 목표 (영상 기준)

```
하네스 구축 전:  "AI에게 시키면 매번 다른 결과"
하네스 구축 후:  "어떤 AI 모델에 시켜도 린터 통과 + 테스트 통과 + 동일 품질"

이것이 영상에서 말하는 "프롬프트 대신 하네스 깎기"의 VAMOS 버전이다.
```

---

> **매트릭스 매핑**: 본 계획서는 STRATEGY_08 매트릭스 **D1행 + B행(B1, B2a, B3, BF)** 에 해당한다.
> - D1: §4 SOT/SOT 2 하네스 계층 (L1+L2 — 원본 정합)
> - B1: §7 Layer 0 + Layer 1 (구축 환경 세팅)
> - B2a: §8 Layer 1 린터 + 멱등성 검증 (하네스 실행)
> - B3: §11 Eval Pipeline (산출물 품질 평가)
> - BF: §13 위험 대응 + §6 피드백 흐름 (구축 역류)
>
> **다음 단계**: 0단계(SOT 정합성 확인)부터 실행 시작
> **참조 문서**:
> - `D:\VAMOS\docs\sot\` — SOT 정본 68개 파일 (L1 하네스 대상)
> - `D:\VAMOS\docs\sot 2\` — SOT 2 상세 648개 파일, 36개 도메인 (L2 하네스 대상)
> - `D:\VAMOS\CLAUDE.md` — AI 컨텍스트 697줄 → 보강 후 ~953줄 (L3 하네스 대상)
> - `D:\VAMOS\CLAUDE 보강전략 V1.0.md` — CLAUDE.md 보강 + 8단계 검증 스킬
> - `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` — 구현 순서 + 린터/CI/테스트 설정 (L4 하네��� 근거)
> - `D:\VAMOS\.claude\skills\` — 기존 55개 스킬 (SOT 검증 스킬 포함)
> - `D:\VAMOS\.claude\skills\sot-conflict\` — SOT 간 모순 탐지
> - `D:\VAMOS\.claude\skills\sot-check\` — SOT 원본 직접 대조
> - `D:\VAMOS\.claude\skills\sot2-cross-ref\` — SOT 2 교차참조 검증
> - `D:\VAMOS\.claude\skills\validate\` — 2계층 결정론적 + AI 의미 검증
